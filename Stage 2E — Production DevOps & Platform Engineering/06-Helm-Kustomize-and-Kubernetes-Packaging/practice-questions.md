# M06 Practice Questions — Helm, Kustomize, and Kubernetes Packaging

**Stage:** Stage 2E — Production DevOps & Platform Engineering  
**Module:** M06 — `06-Helm-Kustomize-and-Kubernetes-Packaging`  
**Purpose:** standalone question bank for Units 1–8, from L1 fundamentals to L4 production judgment.

## Table of contents

- [How to use the question bank](#how-to-use-the-question-bank)
- [Source alignment and assumptions](#source-alignment-and-assumptions)
- [Difficulty levels](#difficulty-levels)
- [Scoring and remediation policy](#scoring-and-remediation-policy)
- [Unit 1 — Kubernetes manifest management and the templating problem](#unit-1--kubernetes-manifest-management-and-the-templating-problem)
- [Unit 2 — Helm charts, values, and templates](#unit-2--helm-charts-values-and-templates)
- [Unit 3 — Helm hooks, dependencies, and subcharts](#unit-3--helm-hooks-dependencies-and-subcharts)
- [Unit 4 — Helm chart testing, linting, and versioning](#unit-4--helm-chart-testing-linting-and-versioning)
- [Unit 5 — Kustomize bases, overlays, and patches](#unit-5--kustomize-bases-overlays-and-patches)
- [Unit 6 — Choosing Helm vs Kustomize, and combining them](#unit-6--choosing-helm-vs-kustomize-and-combining-them)
- [Unit 7 — Chart repositories, OCI registries, and signing](#unit-7--chart-repositories-oci-registries-and-signing)
- [Unit 8 — Operators, CRDs, and custom controllers overview](#unit-8--operators-crds-and-custom-controllers-overview)
- [Cross-unit integration questions](#cross-unit-integration-questions)
- [Design-review / whiteboard prompts](#design-review--whiteboard-prompts)
- [Final scorecard and remediation plan](#final-scorecard-and-remediation-plan)
- [Coverage matrix against the syllabus](#coverage-matrix-against-the-syllabus)
- [Version-sensitive answer notes and references](#version-sensitive-answer-notes-and-references)

## How to use the question bank

Answer each question before reading its model answer. Treat `[ILLUSTRATIVE]` output as constructed teaching material, not captured execution evidence. For review questions, enumerate each defect, its consequence, and a correction. Use disposable environments for install/upgrade exercises; never run destructive CRD operations against production.

## Source alignment and assumptions

The uploaded prompt provides the authoritative Unit 1–8 scope and target filenames. The completed chapter files, `PROMPT — Generate SYLLABUS-Helm-Kustomize-and-Kubernetes-Packaging.md`, and `Roadmap_ptree.md` were not independently available for inspection during this generation. This bank therefore aligns to the unit map included in the prompt and does not claim chapter-by-chapter cross-checking. Helm, Kustomize, Kubernetes API, OCI, Cosign, CRD conversion/CEL, and controller-library behavior may be version-sensitive; verify against the installed versions. No commands, clusters, signatures, or releases were executed.

## Difficulty levels

- **L1:** beginner concepts and simple interpretation.
- **L2:** rendering/configuration and routine debugging.
- **L3:** lifecycle, compatibility, and supply-chain analysis.
- **L4:** production incident response, blast-radius control, and migration design.

## Scoring and remediation policy

Score points earned divided by points available, not raw number correct. Short answer and MCQ: 4 points; output interpretation: 6; configuration review: 8; incident and design: 10. Cross-unit questions state weights. Each whiteboard prompt is worth 10. **80%+**: proceed and revisit errors; **60–79%**: remediate weak objectives, redo missed questions, and retest; **below 60%**: repeat the relevant unit and retake its questions. Any safety-critical miss involving signature verification, CRD deletion, finalizers, excessive RBAC, or rollback requires remediation regardless of score. A high score alone does not prove production readiness.

## Unit 1 — Kubernetes manifest management and the templating problem

### M06-U1-Q01 — Conceptual short answer

**ID:** `M06-U1-Q01`  
**Category:** Conceptual short answer  
**Difficulty:** L1  
**Objective:** manifest duplication and declarative state  
**Estimated time:** 4 minutes  
**Points:** 4

**Question**

Why do copied environment manifests drift?

**Model answer**

Identify the shared cause, state the relevant lifecycle boundary, and recommend a proportionate control that preserves intentional environment differences.

**Rationale**

The expected response connects the concept to its operational consequence and a practical control.

**Common wrong answers / failure modes**

Common errors include relying on naming conventions alone, assuming a render proves deployment health, or adding complexity without a demonstrated requirement.

**Scoring guidance**

Award 1 point for the core concept, 1 for causal reasoning, 1 for operational impact, and 1 for a safe corrective action.

### M06-U1-Q02 — Conceptual short answer

**ID:** `M06-U1-Q02`  
**Category:** Conceptual short answer  
**Difficulty:** L2  
**Objective:** manifest duplication and declarative state  
**Estimated time:** 4 minutes  
**Points:** 4

**Question**

What does declarative desired state mean?

**Model answer**

Trace the input through the relevant tool stage, distinguish what the evidence proves from what remains unknown, and validate the resulting resource or artifact.

**Rationale**

The expected response connects the concept to its operational consequence and a practical control.

**Common wrong answers / failure modes**

Common errors include relying on naming conventions alone, assuming a render proves deployment health, or adding complexity without a demonstrated requirement.

**Scoring guidance**

Award 1 point for the core concept, 1 for causal reasoning, 1 for operational impact, and 1 for a safe corrective action.

### M06-U1-Q03 — Conceptual short answer

**ID:** `M06-U1-Q03`  
**Category:** Conceptual short answer  
**Difficulty:** L2  
**Objective:** manifest duplication and declarative state  
**Estimated time:** 4 minutes  
**Points:** 4

**Question**

How should shared and environment-specific configuration be separated?

**Model answer**

Prefer explicit ownership, repeatable inputs, documented compatibility, and tests that exercise the final output rather than assuming tool defaults.

**Rationale**

The expected response connects the concept to its operational consequence and a practical control.

**Common wrong answers / failure modes**

Common errors include relying on naming conventions alone, assuming a render proves deployment health, or adding complexity without a demonstrated requirement.

**Scoring guidance**

Award 1 point for the core concept, 1 for causal reasoning, 1 for operational impact, and 1 for a safe corrective action.

### M06-U1-Q04 — Multiple choice

**ID:** `M06-U1-Q04`  
**Category:** Multiple choice  
**Difficulty:** L1  
**Objective:** manifest duplication and declarative state  
**Estimated time:** 3 minutes  
**Points:** 4

**Question**

Which statement is correct?

A. Copying files prevents drift by itself.
B. A shared source with explicit differences reduces unintended drift.
C. Rendering proves runtime health.
D. An operator is always required.

**Model answer**

**Correct answer: B.** Incorrect: this leaves the underlying lifecycle or drift problem unresolved.

**Rationale**

The best answer preserves the distinction between source, rendered artifact, lifecycle operation, and runtime evidence.

**Common wrong answers / failure modes**

- **A:** Correct: this approach binds the decision to reviewable evidence and repeatable policy.
- **B:** This is the best option under the stated constraints.
- **C:** Incorrect: this confuses one validation layer with end-to-end correctness.
- **D:** Incorrect: this skips evidence gathering and can increase blast radius.

**Scoring guidance**

4 points for the correct option and a concise reason; 0–2 partial credit may be used for a correct choice with incomplete rationale.

### M06-U1-Q05 — Multiple choice

**ID:** `M06-U1-Q05`  
**Category:** Multiple choice  
**Difficulty:** L2  
**Objective:** manifest duplication and declarative state  
**Estimated time:** 3 minutes  
**Points:** 4

**Question**

What is the safest first step?

A. Delete all resources.
B. Retry immediately.
C. Ignore the failure if YAML parses.
D. Collect relevant inputs, output, ownership, and lifecycle evidence before changing state.

**Model answer**

**Correct answer: D.** Incorrect: this skips evidence gathering and can increase blast radius.

**Rationale**

The best answer preserves the distinction between source, rendered artifact, lifecycle operation, and runtime evidence.

**Common wrong answers / failure modes**

- **A:** Correct: this approach binds the decision to reviewable evidence and repeatable policy.
- **B:** Incorrect: this leaves the underlying lifecycle or drift problem unresolved.
- **C:** Incorrect: this confuses one validation layer with end-to-end correctness.
- **D:** This is the best option under the stated constraints.

**Scoring guidance**

4 points for the correct option and a concise reason; 0–2 partial credit may be used for a correct choice with incomplete rationale.

### M06-U1-Q06 — Multiple choice

**ID:** `M06-U1-Q06`  
**Category:** Multiple choice  
**Difficulty:** L3  
**Objective:** manifest duplication and declarative state  
**Estimated time:** 3 minutes  
**Points:** 4

**Question**

Which release control is strongest?

A. Validate the exact artifact and rendered output against documented policy.
B. Trust the filename alone.
C. Skip compatibility tests.
D. Treat signatures as proof of safety.

**Model answer**

**Correct answer: A.** Correct: this approach binds the decision to reviewable evidence and repeatable policy.

**Rationale**

The best answer preserves the distinction between source, rendered artifact, lifecycle operation, and runtime evidence.

**Common wrong answers / failure modes**

- **A:** This is the best option under the stated constraints.
- **B:** Incorrect: this leaves the underlying lifecycle or drift problem unresolved.
- **C:** Incorrect: this confuses one validation layer with end-to-end correctness.
- **D:** Incorrect: this skips evidence gathering and can increase blast radius.

**Scoring guidance**

4 points for the correct option and a concise reason; 0–2 partial credit may be used for a correct choice with incomplete rationale.

### M06-U1-Q07 — Output interpretation

**ID:** `M06-U1-Q07`  
**Category:** Output interpretation  
**Difficulty:** L2  
**Objective:** manifest duplication and declarative state  
**Estimated time:** 6 minutes  
**Points:** 6

**Question**

Three environments copy a Deployment; a security fix reached only dev. Recommend a source strategy.

```text
[ILLUSTRATIVE]
Input under review: Three environments copy a Deployment; a security fix reached only dev. Recommend a source strategy.
Evidence: the tool reports successful rendering, but no API-server validation or apply result is provided.
```

**Model answer**

Interpret only what the supplied evidence establishes. Inspect exact source, effective values/overlay, tool version, target identity, and final rendered output; then run the next validation layer appropriate to the workflow. Do not claim that rendering proves API acceptance or runtime health. If behavior is version-sensitive, reproduce with the installed tool and record the version.

**Rationale**

The reasoning chain should proceed from evidence to hypothesis, then a bounded validation step; it should not invent command results.

**Common wrong answers / failure modes**

Tempting error: treating a successful render/build as proof that resources were accepted or are healthy. Another error is to patch live state before locating the source of divergence.

**Scoring guidance**

Award 2 points for interpretation, 2 for evidence-based reasoning, and 2 for safe next steps and explicit uncertainty.

### M06-U1-Q08 — Output interpretation

**ID:** `M06-U1-Q08`  
**Category:** Output interpretation  
**Difficulty:** L3  
**Objective:** manifest duplication and declarative state  
**Estimated time:** 6 minutes  
**Points:** 6

**Question**

A render command succeeds but no apply or health check follows. What is proven?

```text
[ILLUSTRATIVE]
Input under review: A render command succeeds but no apply or health check follows. What is proven?
Evidence: the final rendered resource differs from the expected environment state; source and intermediate outputs are available for comparison.
```

**Model answer**

Compare the expected and actual final resource, locate the first stage where they diverge, and correct the source of the mismatch. Validate the final output and check live state only through the approved lifecycle owner.

**Rationale**

The reasoning chain should proceed from evidence to hypothesis, then a bounded validation step; it should not invent command results.

**Common wrong answers / failure modes**

Tempting error: treating a successful render/build as proof that resources were accepted or are healthy. Another error is to patch live state before locating the source of divergence.

**Scoring guidance**

Award 2 points for interpretation, 2 for evidence-based reasoning, and 2 for safe next steps and explicit uncertainty.

### M06-U1-Q09 — Configuration review

**ID:** `M06-U1-Q09`  
**Category:** Configuration review  
**Difficulty:** L3  
**Objective:** manifest duplication and declarative state  
**Estimated time:** 8 minutes  
**Points:** 8

**Question**

Choose between plain YAML, Helm, and Kustomize for three mostly identical environments.

```yaml
# Kubernetes manifest management and the templating problem
apiVersion: apps/v1
kind: Deployment
metadata: { name: sample }
spec:
  replicas: 2
  selector: { matchLabels: { app: sample } }
  template:
    metadata: { labels: { app: different } }
    spec:
      containers:
      - name: app
        image: example.invalid/app:latest
        securityContext: { privileged: true }
# Additional issue: the release input/dependency is not pinned or schema-validated.
```

**Model answer**

Intended defects: (1) selector `app: sample` does not match Pod label `app: different`; (2) mutable `latest` weakens release identity; (3) privileged container is unjustified and expands blast radius; (4) dependency/source is not pinned; (5) no schema/rendered-output test is shown. Correct labels, use an approved immutable reference, apply least privilege, pin the source/dependency, and add validation.

**Rationale**

A good review enumerates independent defects and connects each to impact and correction.

**Common wrong answers / failure modes**

Common failure: reporting only the syntax/target issue while missing selector, security, immutability, or validation defects.

**Scoring guidance**

Up to 2 points for each distinct defect with its consequence and correction; maximum 8.

### M06-U1-Q10 — Configuration review

**ID:** `M06-U1-Q10`  
**Category:** Configuration review  
**Difficulty:** L3  
**Objective:** manifest duplication and declarative state  
**Estimated time:** 8 minutes  
**Points:** 8

**Question**

A team changes selector labels per environment. Explain the compatibility risk.

```yaml
# Kubernetes manifest management and the templating problem
source: ./vendor-or-base
patchTarget: name-that-does-not-exist
patchPath: /spec/replicaCount
image: example.invalid/app:latest
# Additional issue: no final rendered-output test; production override can remove a required security setting.
```

**Model answer**

Intended defects: (1) target name does not match the actual resource; (2) `/spec/replicaCount` is not the Deployment replicas path (`/spec/replicas`); (3) mutable image reference; (4) production overlay can erase a required security invariant; (5) no final-render test. Fix target/path, use an approved image identity, preserve security baseline, and test the complete build. Multiple targeted corrections may be valid.

**Rationale**

A good review enumerates independent defects and connects each to impact and correction.

**Common wrong answers / failure modes**

Common failure: reporting only the syntax/target issue while missing selector, security, immutability, or validation defects.

**Scoring guidance**

Up to 2 points for each distinct defect with its consequence and correction; maximum 8.

### M06-U1-Q11 — Incident / troubleshooting

**ID:** `M06-U1-Q11`  
**Category:** Incident / troubleshooting  
**Difficulty:** L4  
**Objective:** manifest duplication and declarative state  
**Estimated time:** 12 minutes  
**Points:** 10

**Question**

A patch fixes the image but prod still lacks a readiness probe. Give an evidence-led response.

**Model answer**

Symptom → evidence → diagnosis → containment/fix → prevention: first collect the exact source, rendered artifact, tool/version inputs, live status/events/logs relevant to this unit, and prior known-good revision. Rank hypotheses from evidence. Pause risky promotion, contain with the approved owner-specific procedure, repair the source, and verify recovery. Add a regression gate and document remaining uncertainty.

**Rationale**

Incident response must preserve evidence and reduce blast radius before making a potentially destructive change.

**Common wrong answers / failure modes**

Failures include blind retries, deleting resources before inventory, assuming rollback reverses data/CRD changes, or declaring success without verification.

**Scoring guidance**

2 points each for evidence, diagnosis, containment, recovery verification, and prevention/uncertainty.

### M06-U1-Q12 — Design question

**ID:** `M06-U1-Q12`  
**Category:** Design question  
**Difficulty:** L3  
**Objective:** manifest duplication and declarative state  
**Estimated time:** 15 minutes  
**Points:** 10

**Question**

Design delivery for dev/staging/prod with only hostname and replica differences.

**Model answer**

A strong answer states assumptions, alternatives, chosen approach, lifecycle owner, compatibility constraints, validation evidence, rollback/exit plan, and operational cost. Accept alternatives if the trade-offs are explicit.

**Rationale**

The objective is reasoned judgment under constraints, not a memorized tool definition.

**Common wrong answers / failure modes**

Common failures: no decision criteria, no owner, no validation, no migration/rollback path, or assuming the simplest demo is production-ready.

**Scoring guidance**

Use the unit's 10-point rubric: 2 points each for constraints/tool fit, ownership, compatibility/security, validation evidence, and rollback/operability.

## Unit 2 — Helm charts, values, and templates

### M06-U2-Q01 — Conceptual short answer

**ID:** `M06-U2-Q01`  
**Category:** Conceptual short answer  
**Difficulty:** L1  
**Objective:** chart values and rendering  
**Estimated time:** 4 minutes  
**Points:** 4

**Question**

What constitutes a chart's consumer-facing API?

**Model answer**

Identify the shared cause, state the relevant lifecycle boundary, and recommend a proportionate control that preserves intentional environment differences.

**Rationale**

The expected response connects the concept to its operational consequence and a practical control.

**Common wrong answers / failure modes**

Common errors include relying on naming conventions alone, assuming a render proves deployment health, or adding complexity without a demonstrated requirement.

**Scoring guidance**

Award 1 point for the core concept, 1 for causal reasoning, 1 for operational impact, and 1 for a safe corrective action.

### M06-U2-Q02 — Conceptual short answer

**ID:** `M06-U2-Q02`  
**Category:** Conceptual short answer  
**Difficulty:** L2  
**Objective:** chart values and rendering  
**Estimated time:** 4 minutes  
**Points:** 4

**Question**

How do chart version and appVersion differ?

**Model answer**

Trace the input through the relevant tool stage, distinguish what the evidence proves from what remains unknown, and validate the resulting resource or artifact.

**Rationale**

The expected response connects the concept to its operational consequence and a practical control.

**Common wrong answers / failure modes**

Common errors include relying on naming conventions alone, assuming a render proves deployment health, or adding complexity without a demonstrated requirement.

**Scoring guidance**

Award 1 point for the core concept, 1 for causal reasoning, 1 for operational impact, and 1 for a safe corrective action.

### M06-U2-Q03 — Conceptual short answer

**ID:** `M06-U2-Q03`  
**Category:** Conceptual short answer  
**Difficulty:** L2  
**Objective:** chart values and rendering  
**Estimated time:** 4 minutes  
**Points:** 4

**Question**

Why is rendering not equivalent to upgrading a release?

**Model answer**

Prefer explicit ownership, repeatable inputs, documented compatibility, and tests that exercise the final output rather than assuming tool defaults.

**Rationale**

The expected response connects the concept to its operational consequence and a practical control.

**Common wrong answers / failure modes**

Common errors include relying on naming conventions alone, assuming a render proves deployment health, or adding complexity without a demonstrated requirement.

**Scoring guidance**

Award 1 point for the core concept, 1 for causal reasoning, 1 for operational impact, and 1 for a safe corrective action.

### M06-U2-Q04 — Multiple choice

**ID:** `M06-U2-Q04`  
**Category:** Multiple choice  
**Difficulty:** L1  
**Objective:** chart values and rendering  
**Estimated time:** 3 minutes  
**Points:** 4

**Question**

Which statement is correct?

A. Copying files prevents drift by itself.
B. A shared source with explicit differences reduces unintended drift.
C. Rendering proves runtime health.
D. An operator is always required.

**Model answer**

**Correct answer: B.** Incorrect: this leaves the underlying lifecycle or drift problem unresolved.

**Rationale**

The best answer preserves the distinction between source, rendered artifact, lifecycle operation, and runtime evidence.

**Common wrong answers / failure modes**

- **A:** Correct: this approach binds the decision to reviewable evidence and repeatable policy.
- **B:** This is the best option under the stated constraints.
- **C:** Incorrect: this confuses one validation layer with end-to-end correctness.
- **D:** Incorrect: this skips evidence gathering and can increase blast radius.

**Scoring guidance**

4 points for the correct option and a concise reason; 0–2 partial credit may be used for a correct choice with incomplete rationale.

### M06-U2-Q05 — Multiple choice

**ID:** `M06-U2-Q05`  
**Category:** Multiple choice  
**Difficulty:** L2  
**Objective:** chart values and rendering  
**Estimated time:** 3 minutes  
**Points:** 4

**Question**

What is the safest first step?

A. Delete all resources.
B. Retry immediately.
C. Ignore the failure if YAML parses.
D. Collect relevant inputs, output, ownership, and lifecycle evidence before changing state.

**Model answer**

**Correct answer: D.** Incorrect: this skips evidence gathering and can increase blast radius.

**Rationale**

The best answer preserves the distinction between source, rendered artifact, lifecycle operation, and runtime evidence.

**Common wrong answers / failure modes**

- **A:** Correct: this approach binds the decision to reviewable evidence and repeatable policy.
- **B:** Incorrect: this leaves the underlying lifecycle or drift problem unresolved.
- **C:** Incorrect: this confuses one validation layer with end-to-end correctness.
- **D:** This is the best option under the stated constraints.

**Scoring guidance**

4 points for the correct option and a concise reason; 0–2 partial credit may be used for a correct choice with incomplete rationale.

### M06-U2-Q06 — Multiple choice

**ID:** `M06-U2-Q06`  
**Category:** Multiple choice  
**Difficulty:** L3  
**Objective:** chart values and rendering  
**Estimated time:** 3 minutes  
**Points:** 4

**Question**

Which release control is strongest?

A. Validate the exact artifact and rendered output against documented policy.
B. Trust the filename alone.
C. Skip compatibility tests.
D. Treat signatures as proof of safety.

**Model answer**

**Correct answer: A.** Correct: this approach binds the decision to reviewable evidence and repeatable policy.

**Rationale**

The best answer preserves the distinction between source, rendered artifact, lifecycle operation, and runtime evidence.

**Common wrong answers / failure modes**

- **A:** This is the best option under the stated constraints.
- **B:** Incorrect: this leaves the underlying lifecycle or drift problem unresolved.
- **C:** Incorrect: this confuses one validation layer with end-to-end correctness.
- **D:** Incorrect: this skips evidence gathering and can increase blast radius.

**Scoring guidance**

4 points for the correct option and a concise reason; 0–2 partial credit may be used for a correct choice with incomplete rationale.

### M06-U2-Q07 — Output interpretation

**ID:** `M06-U2-Q07`  
**Category:** Output interpretation  
**Difficulty:** L2  
**Objective:** chart values and rendering  
**Estimated time:** 6 minutes  
**Points:** 6

**Question**

A values key exists but the template reads a different path. Diagnose.

```text
[ILLUSTRATIVE]
Input under review: A values key exists but the template reads a different path. Diagnose.
Evidence: the tool reports successful rendering, but no API-server validation or apply result is provided.
```

**Model answer**

Interpret only what the supplied evidence establishes. Inspect exact source, effective values/overlay, tool version, target identity, and final rendered output; then run the next validation layer appropriate to the workflow. Do not claim that rendering proves API acceptance or runtime health. If behavior is version-sensitive, reproduce with the installed tool and record the version.

**Rationale**

The reasoning chain should proceed from evidence to hypothesis, then a bounded validation step; it should not invent command results.

**Common wrong answers / failure modes**

Tempting error: treating a successful render/build as proof that resources were accepted or are healthy. Another error is to patch live state before locating the source of divergence.

**Scoring guidance**

Award 2 points for interpretation, 2 for evidence-based reasoning, and 2 for safe next steps and explicit uncertainty.

### M06-U2-Q08 — Output interpretation

**ID:** `M06-U2-Q08`  
**Category:** Output interpretation  
**Difficulty:** L3  
**Objective:** chart values and rendering  
**Estimated time:** 6 minutes  
**Points:** 6

**Question**

A template renders an empty image reference. What evidence do you inspect first?

```text
[ILLUSTRATIVE]
Input under review: A template renders an empty image reference. What evidence do you inspect first?
Evidence: the final rendered resource differs from the expected environment state; source and intermediate outputs are available for comparison.
```

**Model answer**

Compare the expected and actual final resource, locate the first stage where they diverge, and correct the source of the mismatch. Validate the final output and check live state only through the approved lifecycle owner.

**Rationale**

The reasoning chain should proceed from evidence to hypothesis, then a bounded validation step; it should not invent command results.

**Common wrong answers / failure modes**

Tempting error: treating a successful render/build as proof that resources were accepted or are healthy. Another error is to patch live state before locating the source of divergence.

**Scoring guidance**

Award 2 points for interpretation, 2 for evidence-based reasoning, and 2 for safe next steps and explicit uncertainty.

### M06-U2-Q09 — Configuration review

**ID:** `M06-U2-Q09`  
**Category:** Configuration review  
**Difficulty:** L3  
**Objective:** chart values and rendering  
**Estimated time:** 8 minutes  
**Points:** 8

**Question**

Review a chart with mismatched value names and a mutable image tag.

```yaml
# Helm charts, values, and templates
apiVersion: apps/v1
kind: Deployment
metadata: { name: sample }
spec:
  replicas: 2
  selector: { matchLabels: { app: sample } }
  template:
    metadata: { labels: { app: different } }
    spec:
      containers:
      - name: app
        image: example.invalid/app:latest
        securityContext: { privileged: true }
# Additional issue: the release input/dependency is not pinned or schema-validated.
```

**Model answer**

Intended defects: (1) selector `app: sample` does not match Pod label `app: different`; (2) mutable `latest` weakens release identity; (3) privileged container is unjustified and expands blast radius; (4) dependency/source is not pinned; (5) no schema/rendered-output test is shown. Correct labels, use an approved immutable reference, apply least privilege, pin the source/dependency, and add validation.

**Rationale**

A good review enumerates independent defects and connects each to impact and correction.

**Common wrong answers / failure modes**

Common failure: reporting only the syntax/target issue while missing selector, security, immutability, or validation defects.

**Scoring guidance**

Up to 2 points for each distinct defect with its consequence and correction; maximum 8.

### M06-U2-Q10 — Configuration review

**ID:** `M06-U2-Q10`  
**Category:** Configuration review  
**Difficulty:** L3  
**Objective:** chart values and rendering  
**Estimated time:** 8 minutes  
**Points:** 8

**Question**

Review a chart with missing defaults, weak typing, and an undocumented required key.

```yaml
# Helm charts, values, and templates
source: ./vendor-or-base
patchTarget: name-that-does-not-exist
patchPath: /spec/replicaCount
image: example.invalid/app:latest
# Additional issue: no final rendered-output test; production override can remove a required security setting.
```

**Model answer**

Intended defects: (1) target name does not match the actual resource; (2) `/spec/replicaCount` is not the Deployment replicas path (`/spec/replicas`); (3) mutable image reference; (4) production overlay can erase a required security invariant; (5) no final-render test. Fix target/path, use an approved image identity, preserve security baseline, and test the complete build. Multiple targeted corrections may be valid.

**Rationale**

A good review enumerates independent defects and connects each to impact and correction.

**Common wrong answers / failure modes**

Common failure: reporting only the syntax/target issue while missing selector, security, immutability, or validation defects.

**Scoring guidance**

Up to 2 points for each distinct defect with its consequence and correction; maximum 8.

### M06-U2-Q11 — Incident / troubleshooting

**ID:** `M06-U2-Q11`  
**Category:** Incident / troubleshooting  
**Difficulty:** L4  
**Objective:** chart values and rendering  
**Estimated time:** 12 minutes  
**Points:** 10

**Question**

A Helm upgrade succeeds but the new ReplicaSet is unavailable. Respond safely.

**Model answer**

Symptom → evidence → diagnosis → containment/fix → prevention: first collect the exact source, rendered artifact, tool/version inputs, live status/events/logs relevant to this unit, and prior known-good revision. Rank hypotheses from evidence. Pause risky promotion, contain with the approved owner-specific procedure, repair the source, and verify recovery. Add a regression gate and document remaining uncertainty.

**Rationale**

Incident response must preserve evidence and reduce blast radius before making a potentially destructive change.

**Common wrong answers / failure modes**

Failures include blind retries, deleting resources before inventory, assuming rollback reverses data/CRD changes, or declaring success without verification.

**Scoring guidance**

2 points each for evidence, diagnosis, containment, recovery verification, and prevention/uncertainty.

### M06-U2-Q12 — Design question

**ID:** `M06-U2-Q12`  
**Category:** Design question  
**Difficulty:** L3  
**Objective:** chart values and rendering  
**Estimated time:** 15 minutes  
**Points:** 10

**Question**

Design a stable values API for a shared internal chart.

**Model answer**

A strong answer states assumptions, alternatives, chosen approach, lifecycle owner, compatibility constraints, validation evidence, rollback/exit plan, and operational cost. Accept alternatives if the trade-offs are explicit.

**Rationale**

The objective is reasoned judgment under constraints, not a memorized tool definition.

**Common wrong answers / failure modes**

Common failures: no decision criteria, no owner, no validation, no migration/rollback path, or assuming the simplest demo is production-ready.

**Scoring guidance**

Use the unit's 10-point rubric: 2 points each for constraints/tool fit, ownership, compatibility/security, validation evidence, and rollback/operability.

## Unit 3 — Helm hooks, dependencies, and subcharts

### M06-U3-Q01 — Conceptual short answer

**ID:** `M06-U3-Q01`  
**Category:** Conceptual short answer  
**Difficulty:** L1  
**Objective:** hooks and dependencies  
**Estimated time:** 4 minutes  
**Points:** 4

**Question**

Why are hooks not ordinary release resources?

**Model answer**

Identify the shared cause, state the relevant lifecycle boundary, and recommend a proportionate control that preserves intentional environment differences.

**Rationale**

The expected response connects the concept to its operational consequence and a practical control.

**Common wrong answers / failure modes**

Common errors include relying on naming conventions alone, assuming a render proves deployment health, or adding complexity without a demonstrated requirement.

**Scoring guidance**

Award 1 point for the core concept, 1 for causal reasoning, 1 for operational impact, and 1 for a safe corrective action.

### M06-U3-Q02 — Conceptual short answer

**ID:** `M06-U3-Q02`  
**Category:** Conceptual short answer  
**Difficulty:** L2  
**Objective:** hooks and dependencies  
**Estimated time:** 4 minutes  
**Points:** 4

**Question**

Why should chart dependencies be pinned?

**Model answer**

Trace the input through the relevant tool stage, distinguish what the evidence proves from what remains unknown, and validate the resulting resource or artifact.

**Rationale**

The expected response connects the concept to its operational consequence and a practical control.

**Common wrong answers / failure modes**

Common errors include relying on naming conventions alone, assuming a render proves deployment health, or adding complexity without a demonstrated requirement.

**Scoring guidance**

Award 1 point for the core concept, 1 for causal reasoning, 1 for operational impact, and 1 for a safe corrective action.

### M06-U3-Q03 — Conceptual short answer

**ID:** `M06-U3-Q03`  
**Category:** Conceptual short answer  
**Difficulty:** L2  
**Objective:** hooks and dependencies  
**Estimated time:** 4 minutes  
**Points:** 4

**Question**

What should be reviewed in a third-party chart?

**Model answer**

Prefer explicit ownership, repeatable inputs, documented compatibility, and tests that exercise the final output rather than assuming tool defaults.

**Rationale**

The expected response connects the concept to its operational consequence and a practical control.

**Common wrong answers / failure modes**

Common errors include relying on naming conventions alone, assuming a render proves deployment health, or adding complexity without a demonstrated requirement.

**Scoring guidance**

Award 1 point for the core concept, 1 for causal reasoning, 1 for operational impact, and 1 for a safe corrective action.

### M06-U3-Q04 — Multiple choice

**ID:** `M06-U3-Q04`  
**Category:** Multiple choice  
**Difficulty:** L1  
**Objective:** hooks and dependencies  
**Estimated time:** 3 minutes  
**Points:** 4

**Question**

Which statement is correct?

A. Copying files prevents drift by itself.
B. A shared source with explicit differences reduces unintended drift.
C. Rendering proves runtime health.
D. An operator is always required.

**Model answer**

**Correct answer: B.** Incorrect: this leaves the underlying lifecycle or drift problem unresolved.

**Rationale**

The best answer preserves the distinction between source, rendered artifact, lifecycle operation, and runtime evidence.

**Common wrong answers / failure modes**

- **A:** Correct: this approach binds the decision to reviewable evidence and repeatable policy.
- **B:** This is the best option under the stated constraints.
- **C:** Incorrect: this confuses one validation layer with end-to-end correctness.
- **D:** Incorrect: this skips evidence gathering and can increase blast radius.

**Scoring guidance**

4 points for the correct option and a concise reason; 0–2 partial credit may be used for a correct choice with incomplete rationale.

### M06-U3-Q05 — Multiple choice

**ID:** `M06-U3-Q05`  
**Category:** Multiple choice  
**Difficulty:** L2  
**Objective:** hooks and dependencies  
**Estimated time:** 3 minutes  
**Points:** 4

**Question**

What is the safest first step?

A. Delete all resources.
B. Retry immediately.
C. Ignore the failure if YAML parses.
D. Collect relevant inputs, output, ownership, and lifecycle evidence before changing state.

**Model answer**

**Correct answer: D.** Incorrect: this skips evidence gathering and can increase blast radius.

**Rationale**

The best answer preserves the distinction between source, rendered artifact, lifecycle operation, and runtime evidence.

**Common wrong answers / failure modes**

- **A:** Correct: this approach binds the decision to reviewable evidence and repeatable policy.
- **B:** Incorrect: this leaves the underlying lifecycle or drift problem unresolved.
- **C:** Incorrect: this confuses one validation layer with end-to-end correctness.
- **D:** This is the best option under the stated constraints.

**Scoring guidance**

4 points for the correct option and a concise reason; 0–2 partial credit may be used for a correct choice with incomplete rationale.

### M06-U3-Q06 — Multiple choice

**ID:** `M06-U3-Q06`  
**Category:** Multiple choice  
**Difficulty:** L3  
**Objective:** hooks and dependencies  
**Estimated time:** 3 minutes  
**Points:** 4

**Question**

Which release control is strongest?

A. Validate the exact artifact and rendered output against documented policy.
B. Trust the filename alone.
C. Skip compatibility tests.
D. Treat signatures as proof of safety.

**Model answer**

**Correct answer: A.** Correct: this approach binds the decision to reviewable evidence and repeatable policy.

**Rationale**

The best answer preserves the distinction between source, rendered artifact, lifecycle operation, and runtime evidence.

**Common wrong answers / failure modes**

- **A:** This is the best option under the stated constraints.
- **B:** Incorrect: this leaves the underlying lifecycle or drift problem unresolved.
- **C:** Incorrect: this confuses one validation layer with end-to-end correctness.
- **D:** Incorrect: this skips evidence gathering and can increase blast radius.

**Scoring guidance**

4 points for the correct option and a concise reason; 0–2 partial credit may be used for a correct choice with incomplete rationale.

### M06-U3-Q07 — Output interpretation

**ID:** `M06-U3-Q07`  
**Category:** Output interpretation  
**Difficulty:** L2  
**Objective:** hooks and dependencies  
**Estimated time:** 6 minutes  
**Points:** 6

**Question**

A pre-upgrade migration hook fails halfway. What should happen before retry?

```text
[ILLUSTRATIVE]
Input under review: A pre-upgrade migration hook fails halfway. What should happen before retry?
Evidence: the tool reports successful rendering, but no API-server validation or apply result is provided.
```

**Model answer**

Interpret only what the supplied evidence establishes. Inspect exact source, effective values/overlay, tool version, target identity, and final rendered output; then run the next validation layer appropriate to the workflow. Do not claim that rendering proves API acceptance or runtime health. If behavior is version-sensitive, reproduce with the installed tool and record the version.

**Rationale**

The reasoning chain should proceed from evidence to hypothesis, then a bounded validation step; it should not invent command results.

**Common wrong answers / failure modes**

Tempting error: treating a successful render/build as proof that resources were accepted or are healthy. Another error is to patch live state before locating the source of divergence.

**Scoring guidance**

Award 2 points for interpretation, 2 for evidence-based reasoning, and 2 for safe next steps and explicit uncertainty.

### M06-U3-Q08 — Output interpretation

**ID:** `M06-U3-Q08`  
**Category:** Output interpretation  
**Difficulty:** L3  
**Objective:** hooks and dependencies  
**Estimated time:** 6 minutes  
**Points:** 6

**Question**

A dependency update introduces cluster-wide RBAC. Which controls should catch it?

```text
[ILLUSTRATIVE]
Input under review: A dependency update introduces cluster-wide RBAC. Which controls should catch it?
Evidence: the final rendered resource differs from the expected environment state; source and intermediate outputs are available for comparison.
```

**Model answer**

Compare the expected and actual final resource, locate the first stage where they diverge, and correct the source of the mismatch. Validate the final output and check live state only through the approved lifecycle owner.

**Rationale**

The reasoning chain should proceed from evidence to hypothesis, then a bounded validation step; it should not invent command results.

**Common wrong answers / failure modes**

Tempting error: treating a successful render/build as proof that resources were accepted or are healthy. Another error is to patch live state before locating the source of divergence.

**Scoring guidance**

Award 2 points for interpretation, 2 for evidence-based reasoning, and 2 for safe next steps and explicit uncertainty.

### M06-U3-Q09 — Configuration review

**ID:** `M06-U3-Q09`  
**Category:** Configuration review  
**Difficulty:** L3  
**Objective:** hooks and dependencies  
**Estimated time:** 8 minutes  
**Points:** 8

**Question**

Review a wildcard dependency and a non-idempotent hook Job.

```yaml
# Helm hooks, dependencies, and subcharts
apiVersion: apps/v1
kind: Deployment
metadata: { name: sample }
spec:
  replicas: 2
  selector: { matchLabels: { app: sample } }
  template:
    metadata: { labels: { app: different } }
    spec:
      containers:
      - name: app
        image: example.invalid/app:latest
        securityContext: { privileged: true }
# Additional issue: the release input/dependency is not pinned or schema-validated.
```

**Model answer**

Intended defects: (1) selector `app: sample` does not match Pod label `app: different`; (2) mutable `latest` weakens release identity; (3) privileged container is unjustified and expands blast radius; (4) dependency/source is not pinned; (5) no schema/rendered-output test is shown. Correct labels, use an approved immutable reference, apply least privilege, pin the source/dependency, and add validation.

**Rationale**

A good review enumerates independent defects and connects each to impact and correction.

**Common wrong answers / failure modes**

Common failure: reporting only the syntax/target issue while missing selector, security, immutability, or validation defects.

**Scoring guidance**

Up to 2 points for each distinct defect with its consequence and correction; maximum 8.

### M06-U3-Q10 — Configuration review

**ID:** `M06-U3-Q10`  
**Category:** Configuration review  
**Difficulty:** L3  
**Objective:** hooks and dependencies  
**Estimated time:** 8 minutes  
**Points:** 8

**Question**

Review a subchart condition that conflicts with parent-chart assumptions.

```yaml
# Helm hooks, dependencies, and subcharts
source: ./vendor-or-base
patchTarget: name-that-does-not-exist
patchPath: /spec/replicaCount
image: example.invalid/app:latest
# Additional issue: no final rendered-output test; production override can remove a required security setting.
```

**Model answer**

Intended defects: (1) target name does not match the actual resource; (2) `/spec/replicaCount` is not the Deployment replicas path (`/spec/replicas`); (3) mutable image reference; (4) production overlay can erase a required security invariant; (5) no final-render test. Fix target/path, use an approved image identity, preserve security baseline, and test the complete build. Multiple targeted corrections may be valid.

**Rationale**

A good review enumerates independent defects and connects each to impact and correction.

**Common wrong answers / failure modes**

Common failure: reporting only the syntax/target issue while missing selector, security, immutability, or validation defects.

**Scoring guidance**

Up to 2 points for each distinct defect with its consequence and correction; maximum 8.

### M06-U3-Q11 — Incident / troubleshooting

**ID:** `M06-U3-Q11`  
**Category:** Incident / troubleshooting  
**Difficulty:** L4  
**Objective:** hooks and dependencies  
**Estimated time:** 12 minutes  
**Points:** 10

**Question**

A migration hook fails and retry could repeat side effects. Respond.

**Model answer**

Symptom → evidence → diagnosis → containment/fix → prevention: first collect the exact source, rendered artifact, tool/version inputs, live status/events/logs relevant to this unit, and prior known-good revision. Rank hypotheses from evidence. Pause risky promotion, contain with the approved owner-specific procedure, repair the source, and verify recovery. Add a regression gate and document remaining uncertainty.

**Rationale**

Incident response must preserve evidence and reduce blast radius before making a potentially destructive change.

**Common wrong answers / failure modes**

Failures include blind retries, deleting resources before inventory, assuming rollback reverses data/CRD changes, or declaring success without verification.

**Scoring guidance**

2 points each for evidence, diagnosis, containment, recovery verification, and prevention/uncertainty.

### M06-U3-Q12 — Design question

**ID:** `M06-U3-Q12`  
**Category:** Design question  
**Difficulty:** L3  
**Objective:** hooks and dependencies  
**Estimated time:** 15 minutes  
**Points:** 10

**Question**

Choose between a Helm hook, separate migration Job, and application-managed migration.

**Model answer**

A strong answer states assumptions, alternatives, chosen approach, lifecycle owner, compatibility constraints, validation evidence, rollback/exit plan, and operational cost. Accept alternatives if the trade-offs are explicit.

**Rationale**

The objective is reasoned judgment under constraints, not a memorized tool definition.

**Common wrong answers / failure modes**

Common failures: no decision criteria, no owner, no validation, no migration/rollback path, or assuming the simplest demo is production-ready.

**Scoring guidance**

Use the unit's 10-point rubric: 2 points each for constraints/tool fit, ownership, compatibility/security, validation evidence, and rollback/operability.

## Unit 4 — Helm chart testing, linting, and versioning

### M06-U4-Q01 — Conceptual short answer

**ID:** `M06-U4-Q01`  
**Category:** Conceptual short answer  
**Difficulty:** L1  
**Objective:** testing and SemVer  
**Estimated time:** 4 minutes  
**Points:** 4

**Question**

Why is helm lint insufficient as a release gate?

**Model answer**

Identify the shared cause, state the relevant lifecycle boundary, and recommend a proportionate control that preserves intentional environment differences.

**Rationale**

The expected response connects the concept to its operational consequence and a practical control.

**Common wrong answers / failure modes**

Common errors include relying on naming conventions alone, assuming a render proves deployment health, or adding complexity without a demonstrated requirement.

**Scoring guidance**

Award 1 point for the core concept, 1 for causal reasoning, 1 for operational impact, and 1 for a safe corrective action.

### M06-U4-Q02 — Conceptual short answer

**ID:** `M06-U4-Q02`  
**Category:** Conceptual short answer  
**Difficulty:** L2  
**Objective:** testing and SemVer  
**Estimated time:** 4 minutes  
**Points:** 4

**Question**

How does chart SemVer differ from application SemVer?

**Model answer**

Trace the input through the relevant tool stage, distinguish what the evidence proves from what remains unknown, and validate the resulting resource or artifact.

**Rationale**

The expected response connects the concept to its operational consequence and a practical control.

**Common wrong answers / failure modes**

Common errors include relying on naming conventions alone, assuming a render proves deployment health, or adding complexity without a demonstrated requirement.

**Scoring guidance**

Award 1 point for the core concept, 1 for causal reasoning, 1 for operational impact, and 1 for a safe corrective action.

### M06-U4-Q03 — Conceptual short answer

**ID:** `M06-U4-Q03`  
**Category:** Conceptual short answer  
**Difficulty:** L2  
**Objective:** testing and SemVer  
**Estimated time:** 4 minutes  
**Points:** 4

**Question**

What should a rendered diff review include?

**Model answer**

Prefer explicit ownership, repeatable inputs, documented compatibility, and tests that exercise the final output rather than assuming tool defaults.

**Rationale**

The expected response connects the concept to its operational consequence and a practical control.

**Common wrong answers / failure modes**

Common errors include relying on naming conventions alone, assuming a render proves deployment health, or adding complexity without a demonstrated requirement.

**Scoring guidance**

Award 1 point for the core concept, 1 for causal reasoning, 1 for operational impact, and 1 for a safe corrective action.

### M06-U4-Q04 — Multiple choice

**ID:** `M06-U4-Q04`  
**Category:** Multiple choice  
**Difficulty:** L1  
**Objective:** testing and SemVer  
**Estimated time:** 3 minutes  
**Points:** 4

**Question**

Which statement is correct?

A. Copying files prevents drift by itself.
B. A shared source with explicit differences reduces unintended drift.
C. Rendering proves runtime health.
D. An operator is always required.

**Model answer**

**Correct answer: B.** Incorrect: this leaves the underlying lifecycle or drift problem unresolved.

**Rationale**

The best answer preserves the distinction between source, rendered artifact, lifecycle operation, and runtime evidence.

**Common wrong answers / failure modes**

- **A:** Correct: this approach binds the decision to reviewable evidence and repeatable policy.
- **B:** This is the best option under the stated constraints.
- **C:** Incorrect: this confuses one validation layer with end-to-end correctness.
- **D:** Incorrect: this skips evidence gathering and can increase blast radius.

**Scoring guidance**

4 points for the correct option and a concise reason; 0–2 partial credit may be used for a correct choice with incomplete rationale.

### M06-U4-Q05 — Multiple choice

**ID:** `M06-U4-Q05`  
**Category:** Multiple choice  
**Difficulty:** L2  
**Objective:** testing and SemVer  
**Estimated time:** 3 minutes  
**Points:** 4

**Question**

What is the safest first step?

A. Delete all resources.
B. Retry immediately.
C. Ignore the failure if YAML parses.
D. Collect relevant inputs, output, ownership, and lifecycle evidence before changing state.

**Model answer**

**Correct answer: D.** Incorrect: this skips evidence gathering and can increase blast radius.

**Rationale**

The best answer preserves the distinction between source, rendered artifact, lifecycle operation, and runtime evidence.

**Common wrong answers / failure modes**

- **A:** Correct: this approach binds the decision to reviewable evidence and repeatable policy.
- **B:** Incorrect: this leaves the underlying lifecycle or drift problem unresolved.
- **C:** Incorrect: this confuses one validation layer with end-to-end correctness.
- **D:** This is the best option under the stated constraints.

**Scoring guidance**

4 points for the correct option and a concise reason; 0–2 partial credit may be used for a correct choice with incomplete rationale.

### M06-U4-Q06 — Multiple choice

**ID:** `M06-U4-Q06`  
**Category:** Multiple choice  
**Difficulty:** L3  
**Objective:** testing and SemVer  
**Estimated time:** 3 minutes  
**Points:** 4

**Question**

Which release control is strongest?

A. Validate the exact artifact and rendered output against documented policy.
B. Trust the filename alone.
C. Skip compatibility tests.
D. Treat signatures as proof of safety.

**Model answer**

**Correct answer: A.** Correct: this approach binds the decision to reviewable evidence and repeatable policy.

**Rationale**

The best answer preserves the distinction between source, rendered artifact, lifecycle operation, and runtime evidence.

**Common wrong answers / failure modes**

- **A:** This is the best option under the stated constraints.
- **B:** Incorrect: this leaves the underlying lifecycle or drift problem unresolved.
- **C:** Incorrect: this confuses one validation layer with end-to-end correctness.
- **D:** Incorrect: this skips evidence gathering and can increase blast radius.

**Scoring guidance**

4 points for the correct option and a concise reason; 0–2 partial credit may be used for a correct choice with incomplete rationale.

### M06-U4-Q07 — Output interpretation

**ID:** `M06-U4-Q07`  
**Category:** Output interpretation  
**Difficulty:** L2  
**Objective:** testing and SemVer  
**Estimated time:** 6 minutes  
**Points:** 6

**Question**

Classify a backward-compatible optional value addition.

```text
[ILLUSTRATIVE]
Input under review: Classify a backward-compatible optional value addition.
Evidence: the tool reports successful rendering, but no API-server validation or apply result is provided.
```

**Model answer**

Interpret only what the supplied evidence establishes. Inspect exact source, effective values/overlay, tool version, target identity, and final rendered output; then run the next validation layer appropriate to the workflow. Do not claim that rendering proves API acceptance or runtime health. If behavior is version-sensitive, reproduce with the installed tool and record the version.

**Rationale**

The reasoning chain should proceed from evidence to hypothesis, then a bounded validation step; it should not invent command results.

**Common wrong answers / failure modes**

Tempting error: treating a successful render/build as proof that resources were accepted or are healthy. Another error is to patch live state before locating the source of divergence.

**Scoring guidance**

Award 2 points for interpretation, 2 for evidence-based reasoning, and 2 for safe next steps and explicit uncertainty.

### M06-U4-Q08 — Output interpretation

**ID:** `M06-U4-Q08`  
**Category:** Output interpretation  
**Difficulty:** L3  
**Objective:** testing and SemVer  
**Estimated time:** 6 minutes  
**Points:** 6

**Question**

A chart changes a resource name and creates a second resource. How should this be classified?

```text
[ILLUSTRATIVE]
Input under review: A chart changes a resource name and creates a second resource. How should this be classified?
Evidence: the final rendered resource differs from the expected environment state; source and intermediate outputs are available for comparison.
```

**Model answer**

Compare the expected and actual final resource, locate the first stage where they diverge, and correct the source of the mismatch. Validate the final output and check live state only through the approved lifecycle owner.

**Rationale**

The reasoning chain should proceed from evidence to hypothesis, then a bounded validation step; it should not invent command results.

**Common wrong answers / failure modes**

Tempting error: treating a successful render/build as proof that resources were accepted or are healthy. Another error is to patch live state before locating the source of divergence.

**Scoring guidance**

Award 2 points for interpretation, 2 for evidence-based reasoning, and 2 for safe next steps and explicit uncertainty.

### M06-U4-Q09 — Configuration review

**ID:** `M06-U4-Q09`  
**Category:** Configuration review  
**Difficulty:** L3  
**Objective:** testing and SemVer  
**Estimated time:** 8 minutes  
**Points:** 8

**Question**

Review CI that lints and packages but does not render or test upgrades.

```yaml
# Helm chart testing, linting, and versioning
apiVersion: apps/v1
kind: Deployment
metadata: { name: sample }
spec:
  replicas: 2
  selector: { matchLabels: { app: sample } }
  template:
    metadata: { labels: { app: different } }
    spec:
      containers:
      - name: app
        image: example.invalid/app:latest
        securityContext: { privileged: true }
# Additional issue: the release input/dependency is not pinned or schema-validated.
```

**Model answer**

Intended defects: (1) selector `app: sample` does not match Pod label `app: different`; (2) mutable `latest` weakens release identity; (3) privileged container is unjustified and expands blast radius; (4) dependency/source is not pinned; (5) no schema/rendered-output test is shown. Correct labels, use an approved immutable reference, apply least privilege, pin the source/dependency, and add validation.

**Rationale**

A good review enumerates independent defects and connects each to impact and correction.

**Common wrong answers / failure modes**

Common failure: reporting only the syntax/target issue while missing selector, security, immutability, or validation defects.

**Scoring guidance**

Up to 2 points for each distinct defect with its consequence and correction; maximum 8.

### M06-U4-Q10 — Configuration review

**ID:** `M06-U4-Q10`  
**Category:** Configuration review  
**Difficulty:** L3  
**Objective:** testing and SemVer  
**Estimated time:** 8 minutes  
**Points:** 8

**Question**

Review a schema whose type conflicts with the template and a breaking key rename.

```yaml
# Helm chart testing, linting, and versioning
source: ./vendor-or-base
patchTarget: name-that-does-not-exist
patchPath: /spec/replicaCount
image: example.invalid/app:latest
# Additional issue: no final rendered-output test; production override can remove a required security setting.
```

**Model answer**

Intended defects: (1) target name does not match the actual resource; (2) `/spec/replicaCount` is not the Deployment replicas path (`/spec/replicas`); (3) mutable image reference; (4) production overlay can erase a required security invariant; (5) no final-render test. Fix target/path, use an approved image identity, preserve security baseline, and test the complete build. Multiple targeted corrections may be valid.

**Rationale**

A good review enumerates independent defects and connects each to impact and correction.

**Common wrong answers / failure modes**

Common failure: reporting only the syntax/target issue while missing selector, security, immutability, or validation defects.

**Scoring guidance**

Up to 2 points for each distinct defect with its consequence and correction; maximum 8.

### M06-U4-Q11 — Incident / troubleshooting

**ID:** `M06-U4-Q11`  
**Category:** Incident / troubleshooting  
**Difficulty:** L4  
**Objective:** testing and SemVer  
**Estimated time:** 12 minutes  
**Points:** 10

**Question**

A Service selector no longer matches Pod labels after upgrade. Respond.

**Model answer**

Symptom → evidence → diagnosis → containment/fix → prevention: first collect the exact source, rendered artifact, tool/version inputs, live status/events/logs relevant to this unit, and prior known-good revision. Rank hypotheses from evidence. Pause risky promotion, contain with the approved owner-specific procedure, repair the source, and verify recovery. Add a regression gate and document remaining uncertainty.

**Rationale**

Incident response must preserve evidence and reduce blast radius before making a potentially destructive change.

**Common wrong answers / failure modes**

Failures include blind retries, deleting resources before inventory, assuming rollback reverses data/CRD changes, or declaring success without verification.

**Scoring guidance**

2 points each for evidence, diagnosis, containment, recovery verification, and prevention/uncertainty.

### M06-U4-Q12 — Design question

**ID:** `M06-U4-Q12`  
**Category:** Design question  
**Difficulty:** L3  
**Objective:** testing and SemVer  
**Estimated time:** 15 minutes  
**Points:** 10

**Question**

Design CI gates for a shared chart with many consumers.

**Model answer**

A strong answer states assumptions, alternatives, chosen approach, lifecycle owner, compatibility constraints, validation evidence, rollback/exit plan, and operational cost. Accept alternatives if the trade-offs are explicit.

**Rationale**

The objective is reasoned judgment under constraints, not a memorized tool definition.

**Common wrong answers / failure modes**

Common failures: no decision criteria, no owner, no validation, no migration/rollback path, or assuming the simplest demo is production-ready.

**Scoring guidance**

Use the unit's 10-point rubric: 2 points each for constraints/tool fit, ownership, compatibility/security, validation evidence, and rollback/operability.

## Unit 5 — Kustomize bases, overlays, and patches

### M06-U5-Q01 — Conceptual short answer

**ID:** `M06-U5-Q01`  
**Category:** Conceptual short answer  
**Difficulty:** L1  
**Objective:** overlays and patch targets  
**Estimated time:** 4 minutes  
**Points:** 4

**Question**

What belongs in a base versus an overlay?

**Model answer**

Identify the shared cause, state the relevant lifecycle boundary, and recommend a proportionate control that preserves intentional environment differences.

**Rationale**

The expected response connects the concept to its operational consequence and a practical control.

**Common wrong answers / failure modes**

Common errors include relying on naming conventions alone, assuming a render proves deployment health, or adding complexity without a demonstrated requirement.

**Scoring guidance**

Award 1 point for the core concept, 1 for causal reasoning, 1 for operational impact, and 1 for a safe corrective action.

### M06-U5-Q02 — Conceptual short answer

**ID:** `M06-U5-Q02`  
**Category:** Conceptual short answer  
**Difficulty:** L2  
**Objective:** overlays and patch targets  
**Estimated time:** 4 minutes  
**Points:** 4

**Question**

When might JSON 6902 patches be useful?

**Model answer**

Trace the input through the relevant tool stage, distinguish what the evidence proves from what remains unknown, and validate the resulting resource or artifact.

**Rationale**

The expected response connects the concept to its operational consequence and a practical control.

**Common wrong answers / failure modes**

Common errors include relying on naming conventions alone, assuming a render proves deployment health, or adding complexity without a demonstrated requirement.

**Scoring guidance**

Award 1 point for the core concept, 1 for causal reasoning, 1 for operational impact, and 1 for a safe corrective action.

### M06-U5-Q03 — Conceptual short answer

**ID:** `M06-U5-Q03`  
**Category:** Conceptual short answer  
**Difficulty:** L2  
**Objective:** overlays and patch targets  
**Estimated time:** 4 minutes  
**Points:** 4

**Question**

Why do generated ConfigMap names sometimes include hashes?

**Model answer**

Prefer explicit ownership, repeatable inputs, documented compatibility, and tests that exercise the final output rather than assuming tool defaults.

**Rationale**

The expected response connects the concept to its operational consequence and a practical control.

**Common wrong answers / failure modes**

Common errors include relying on naming conventions alone, assuming a render proves deployment health, or adding complexity without a demonstrated requirement.

**Scoring guidance**

Award 1 point for the core concept, 1 for causal reasoning, 1 for operational impact, and 1 for a safe corrective action.

### M06-U5-Q04 — Multiple choice

**ID:** `M06-U5-Q04`  
**Category:** Multiple choice  
**Difficulty:** L1  
**Objective:** overlays and patch targets  
**Estimated time:** 3 minutes  
**Points:** 4

**Question**

Which statement is correct?

A. Copying files prevents drift by itself.
B. A shared source with explicit differences reduces unintended drift.
C. Rendering proves runtime health.
D. An operator is always required.

**Model answer**

**Correct answer: B.** Incorrect: this leaves the underlying lifecycle or drift problem unresolved.

**Rationale**

The best answer preserves the distinction between source, rendered artifact, lifecycle operation, and runtime evidence.

**Common wrong answers / failure modes**

- **A:** Correct: this approach binds the decision to reviewable evidence and repeatable policy.
- **B:** This is the best option under the stated constraints.
- **C:** Incorrect: this confuses one validation layer with end-to-end correctness.
- **D:** Incorrect: this skips evidence gathering and can increase blast radius.

**Scoring guidance**

4 points for the correct option and a concise reason; 0–2 partial credit may be used for a correct choice with incomplete rationale.

### M06-U5-Q05 — Multiple choice

**ID:** `M06-U5-Q05`  
**Category:** Multiple choice  
**Difficulty:** L2  
**Objective:** overlays and patch targets  
**Estimated time:** 3 minutes  
**Points:** 4

**Question**

What is the safest first step?

A. Delete all resources.
B. Retry immediately.
C. Ignore the failure if YAML parses.
D. Collect relevant inputs, output, ownership, and lifecycle evidence before changing state.

**Model answer**

**Correct answer: D.** Incorrect: this skips evidence gathering and can increase blast radius.

**Rationale**

The best answer preserves the distinction between source, rendered artifact, lifecycle operation, and runtime evidence.

**Common wrong answers / failure modes**

- **A:** Correct: this approach binds the decision to reviewable evidence and repeatable policy.
- **B:** Incorrect: this leaves the underlying lifecycle or drift problem unresolved.
- **C:** Incorrect: this confuses one validation layer with end-to-end correctness.
- **D:** This is the best option under the stated constraints.

**Scoring guidance**

4 points for the correct option and a concise reason; 0–2 partial credit may be used for a correct choice with incomplete rationale.

### M06-U5-Q06 — Multiple choice

**ID:** `M06-U5-Q06`  
**Category:** Multiple choice  
**Difficulty:** L3  
**Objective:** overlays and patch targets  
**Estimated time:** 3 minutes  
**Points:** 4

**Question**

Which release control is strongest?

A. Validate the exact artifact and rendered output against documented policy.
B. Trust the filename alone.
C. Skip compatibility tests.
D. Treat signatures as proof of safety.

**Model answer**

**Correct answer: A.** Correct: this approach binds the decision to reviewable evidence and repeatable policy.

**Rationale**

The best answer preserves the distinction between source, rendered artifact, lifecycle operation, and runtime evidence.

**Common wrong answers / failure modes**

- **A:** This is the best option under the stated constraints.
- **B:** Incorrect: this leaves the underlying lifecycle or drift problem unresolved.
- **C:** Incorrect: this confuses one validation layer with end-to-end correctness.
- **D:** Incorrect: this skips evidence gathering and can increase blast radius.

**Scoring guidance**

4 points for the correct option and a concise reason; 0–2 partial credit may be used for a correct choice with incomplete rationale.

### M06-U5-Q07 — Output interpretation

**ID:** `M06-U5-Q07`  
**Category:** Output interpretation  
**Difficulty:** L2  
**Objective:** overlays and patch targets  
**Estimated time:** 6 minutes  
**Points:** 6

**Question**

A patch targets a resource name that differs from the base. Diagnose.

```text
[ILLUSTRATIVE]
Input under review: A patch targets a resource name that differs from the base. Diagnose.
Evidence: the tool reports successful rendering, but no API-server validation or apply result is provided.
```

**Model answer**

Interpret only what the supplied evidence establishes. Inspect exact source, effective values/overlay, tool version, target identity, and final rendered output; then run the next validation layer appropriate to the workflow. Do not claim that rendering proves API acceptance or runtime health. If behavior is version-sensitive, reproduce with the installed tool and record the version.

**Rationale**

The reasoning chain should proceed from evidence to hypothesis, then a bounded validation step; it should not invent command results.

**Common wrong answers / failure modes**

Tempting error: treating a successful render/build as proof that resources were accepted or are healthy. Another error is to patch live state before locating the source of divergence.

**Scoring guidance**

Award 2 points for interpretation, 2 for evidence-based reasoning, and 2 for safe next steps and explicit uncertainty.

### M06-U5-Q08 — Output interpretation

**ID:** `M06-U5-Q08`  
**Category:** Output interpretation  
**Difficulty:** L3  
**Objective:** overlays and patch targets  
**Estimated time:** 6 minutes  
**Points:** 6

**Question**

A generated ConfigMap hash changes but the workload references an old literal name. Explain.

```text
[ILLUSTRATIVE]
Input under review: A generated ConfigMap hash changes but the workload references an old literal name. Explain.
Evidence: the final rendered resource differs from the expected environment state; source and intermediate outputs are available for comparison.
```

**Model answer**

Compare the expected and actual final resource, locate the first stage where they diverge, and correct the source of the mismatch. Validate the final output and check live state only through the approved lifecycle owner.

**Rationale**

The reasoning chain should proceed from evidence to hypothesis, then a bounded validation step; it should not invent command results.

**Common wrong answers / failure modes**

Tempting error: treating a successful render/build as proof that resources were accepted or are healthy. Another error is to patch live state before locating the source of divergence.

**Scoring guidance**

Award 2 points for interpretation, 2 for evidence-based reasoning, and 2 for safe next steps and explicit uncertainty.

### M06-U5-Q09 — Configuration review

**ID:** `M06-U5-Q09`  
**Category:** Configuration review  
**Difficulty:** L3  
**Objective:** overlays and patch targets  
**Estimated time:** 8 minutes  
**Points:** 8

**Question**

Review a patch with a wrong target, wrong path, and mutable image tag.

```yaml
# Kustomize bases, overlays, and patches
apiVersion: apps/v1
kind: Deployment
metadata: { name: sample }
spec:
  replicas: 2
  selector: { matchLabels: { app: sample } }
  template:
    metadata: { labels: { app: different } }
    spec:
      containers:
      - name: app
        image: example.invalid/app:latest
        securityContext: { privileged: true }
# Additional issue: the release input/dependency is not pinned or schema-validated.
```

**Model answer**

Intended defects: (1) selector `app: sample` does not match Pod label `app: different`; (2) mutable `latest` weakens release identity; (3) privileged container is unjustified and expands blast radius; (4) dependency/source is not pinned; (5) no schema/rendered-output test is shown. Correct labels, use an approved immutable reference, apply least privilege, pin the source/dependency, and add validation.

**Rationale**

A good review enumerates independent defects and connects each to impact and correction.

**Common wrong answers / failure modes**

Common failure: reporting only the syntax/target issue while missing selector, security, immutability, or validation defects.

**Scoring guidance**

Up to 2 points for each distinct defect with its consequence and correction; maximum 8.

### M06-U5-Q10 — Configuration review

**ID:** `M06-U5-Q10`  
**Category:** Configuration review  
**Difficulty:** L3  
**Objective:** overlays and patch targets  
**Estimated time:** 8 minutes  
**Points:** 8

**Question**

Review an overlay that may remove a required security context and duplicates a resource.

```yaml
# Kustomize bases, overlays, and patches
source: ./vendor-or-base
patchTarget: name-that-does-not-exist
patchPath: /spec/replicaCount
image: example.invalid/app:latest
# Additional issue: no final rendered-output test; production override can remove a required security setting.
```

**Model answer**

Intended defects: (1) target name does not match the actual resource; (2) `/spec/replicaCount` is not the Deployment replicas path (`/spec/replicas`); (3) mutable image reference; (4) production overlay can erase a required security invariant; (5) no final-render test. Fix target/path, use an approved image identity, preserve security baseline, and test the complete build. Multiple targeted corrections may be valid.

**Rationale**

A good review enumerates independent defects and connects each to impact and correction.

**Common wrong answers / failure modes**

Common failure: reporting only the syntax/target issue while missing selector, security, immutability, or validation defects.

**Scoring guidance**

Up to 2 points for each distinct defect with its consequence and correction; maximum 8.

### M06-U5-Q11 — Incident / troubleshooting

**ID:** `M06-U5-Q11`  
**Category:** Incident / troubleshooting  
**Difficulty:** L4  
**Objective:** overlays and patch targets  
**Estimated time:** 12 minutes  
**Points:** 10

**Question**

Production overlay promotes the wrong image and drops a security setting. Respond.

**Model answer**

Symptom → evidence → diagnosis → containment/fix → prevention: first collect the exact source, rendered artifact, tool/version inputs, live status/events/logs relevant to this unit, and prior known-good revision. Rank hypotheses from evidence. Pause risky promotion, contain with the approved owner-specific procedure, repair the source, and verify recovery. Add a regression gate and document remaining uncertainty.

**Rationale**

Incident response must preserve evidence and reduce blast radius before making a potentially destructive change.

**Common wrong answers / failure modes**

Failures include blind retries, deleting resources before inventory, assuming rollback reverses data/CRD changes, or declaring success without verification.

**Scoring guidance**

2 points each for evidence, diagnosis, containment, recovery verification, and prevention/uncertainty.

### M06-U5-Q12 — Design question

**ID:** `M06-U5-Q12`  
**Category:** Design question  
**Difficulty:** L3  
**Objective:** overlays and patch targets  
**Estimated time:** 15 minutes  
**Points:** 10

**Question**

Design overlays for image, replicas, hostname, and resource-request differences.

**Model answer**

A strong answer states assumptions, alternatives, chosen approach, lifecycle owner, compatibility constraints, validation evidence, rollback/exit plan, and operational cost. Accept alternatives if the trade-offs are explicit.

**Rationale**

The objective is reasoned judgment under constraints, not a memorized tool definition.

**Common wrong answers / failure modes**

Common failures: no decision criteria, no owner, no validation, no migration/rollback path, or assuming the simplest demo is production-ready.

**Scoring guidance**

Use the unit's 10-point rubric: 2 points each for constraints/tool fit, ownership, compatibility/security, validation evidence, and rollback/operability.

## Unit 6 — Choosing Helm vs Kustomize, and combining them

### M06-U6-Q01 — Conceptual short answer

**ID:** `M06-U6-Q01`  
**Category:** Conceptual short answer  
**Difficulty:** L1  
**Objective:** composition and lifecycle ownership  
**Estimated time:** 4 minutes  
**Points:** 4

**Question**

Why can combining Helm and Kustomize increase operational risk?

**Model answer**

Identify the shared cause, state the relevant lifecycle boundary, and recommend a proportionate control that preserves intentional environment differences.

**Rationale**

The expected response connects the concept to its operational consequence and a practical control.

**Common wrong answers / failure modes**

Common errors include relying on naming conventions alone, assuming a render proves deployment health, or adding complexity without a demonstrated requirement.

**Scoring guidance**

Award 1 point for the core concept, 1 for causal reasoning, 1 for operational impact, and 1 for a safe corrective action.

### M06-U6-Q02 — Conceptual short answer

**ID:** `M06-U6-Q02`  
**Category:** Conceptual short answer  
**Difficulty:** L2  
**Objective:** composition and lifecycle ownership  
**Estimated time:** 4 minutes  
**Points:** 4

**Question**

What does lifecycle ownership mean in a render-then-patch pipeline?

**Model answer**

Trace the input through the relevant tool stage, distinguish what the evidence proves from what remains unknown, and validate the resulting resource or artifact.

**Rationale**

The expected response connects the concept to its operational consequence and a practical control.

**Common wrong answers / failure modes**

Common errors include relying on naming conventions alone, assuming a render proves deployment health, or adding complexity without a demonstrated requirement.

**Scoring guidance**

Award 1 point for the core concept, 1 for causal reasoning, 1 for operational impact, and 1 for a safe corrective action.

### M06-U6-Q03 — Conceptual short answer

**ID:** `M06-U6-Q03`  
**Category:** Conceptual short answer  
**Difficulty:** L2  
**Objective:** composition and lifecycle ownership  
**Estimated time:** 4 minutes  
**Points:** 4

**Question**

How can double-templating be prevented?

**Model answer**

Prefer explicit ownership, repeatable inputs, documented compatibility, and tests that exercise the final output rather than assuming tool defaults.

**Rationale**

The expected response connects the concept to its operational consequence and a practical control.

**Common wrong answers / failure modes**

Common errors include relying on naming conventions alone, assuming a render proves deployment health, or adding complexity without a demonstrated requirement.

**Scoring guidance**

Award 1 point for the core concept, 1 for causal reasoning, 1 for operational impact, and 1 for a safe corrective action.

### M06-U6-Q04 — Multiple choice

**ID:** `M06-U6-Q04`  
**Category:** Multiple choice  
**Difficulty:** L1  
**Objective:** composition and lifecycle ownership  
**Estimated time:** 3 minutes  
**Points:** 4

**Question**

Which statement is correct?

A. Copying files prevents drift by itself.
B. A shared source with explicit differences reduces unintended drift.
C. Rendering proves runtime health.
D. An operator is always required.

**Model answer**

**Correct answer: B.** Incorrect: this leaves the underlying lifecycle or drift problem unresolved.

**Rationale**

The best answer preserves the distinction between source, rendered artifact, lifecycle operation, and runtime evidence.

**Common wrong answers / failure modes**

- **A:** Correct: this approach binds the decision to reviewable evidence and repeatable policy.
- **B:** This is the best option under the stated constraints.
- **C:** Incorrect: this confuses one validation layer with end-to-end correctness.
- **D:** Incorrect: this skips evidence gathering and can increase blast radius.

**Scoring guidance**

4 points for the correct option and a concise reason; 0–2 partial credit may be used for a correct choice with incomplete rationale.

### M06-U6-Q05 — Multiple choice

**ID:** `M06-U6-Q05`  
**Category:** Multiple choice  
**Difficulty:** L2  
**Objective:** composition and lifecycle ownership  
**Estimated time:** 3 minutes  
**Points:** 4

**Question**

What is the safest first step?

A. Delete all resources.
B. Retry immediately.
C. Ignore the failure if YAML parses.
D. Collect relevant inputs, output, ownership, and lifecycle evidence before changing state.

**Model answer**

**Correct answer: D.** Incorrect: this skips evidence gathering and can increase blast radius.

**Rationale**

The best answer preserves the distinction between source, rendered artifact, lifecycle operation, and runtime evidence.

**Common wrong answers / failure modes**

- **A:** Correct: this approach binds the decision to reviewable evidence and repeatable policy.
- **B:** Incorrect: this leaves the underlying lifecycle or drift problem unresolved.
- **C:** Incorrect: this confuses one validation layer with end-to-end correctness.
- **D:** This is the best option under the stated constraints.

**Scoring guidance**

4 points for the correct option and a concise reason; 0–2 partial credit may be used for a correct choice with incomplete rationale.

### M06-U6-Q06 — Multiple choice

**ID:** `M06-U6-Q06`  
**Category:** Multiple choice  
**Difficulty:** L3  
**Objective:** composition and lifecycle ownership  
**Estimated time:** 3 minutes  
**Points:** 4

**Question**

Which release control is strongest?

A. Validate the exact artifact and rendered output against documented policy.
B. Trust the filename alone.
C. Skip compatibility tests.
D. Treat signatures as proof of safety.

**Model answer**

**Correct answer: A.** Correct: this approach binds the decision to reviewable evidence and repeatable policy.

**Rationale**

The best answer preserves the distinction between source, rendered artifact, lifecycle operation, and runtime evidence.

**Common wrong answers / failure modes**

- **A:** This is the best option under the stated constraints.
- **B:** Incorrect: this leaves the underlying lifecycle or drift problem unresolved.
- **C:** Incorrect: this confuses one validation layer with end-to-end correctness.
- **D:** Incorrect: this skips evidence gathering and can increase blast radius.

**Scoring guidance**

4 points for the correct option and a concise reason; 0–2 partial credit may be used for a correct choice with incomplete rationale.

### M06-U6-Q07 — Output interpretation

**ID:** `M06-U6-Q07`  
**Category:** Output interpretation  
**Difficulty:** L2  
**Objective:** composition and lifecycle ownership  
**Estimated time:** 6 minutes  
**Points:** 6

**Question**

A vendor chart supports most required settings but needs one unsupported field. Choose a pattern.

```text
[ILLUSTRATIVE]
Input under review: A vendor chart supports most required settings but needs one unsupported field. Choose a pattern.
Evidence: the tool reports successful rendering, but no API-server validation or apply result is provided.
```

**Model answer**

Interpret only what the supplied evidence establishes. Inspect exact source, effective values/overlay, tool version, target identity, and final rendered output; then run the next validation layer appropriate to the workflow. Do not claim that rendering proves API acceptance or runtime health. If behavior is version-sensitive, reproduce with the installed tool and record the version.

**Rationale**

The reasoning chain should proceed from evidence to hypothesis, then a bounded validation step; it should not invent command results.

**Common wrong answers / failure modes**

Tempting error: treating a successful render/build as proof that resources were accepted or are healthy. Another error is to patch live state before locating the source of divergence.

**Scoring guidance**

Award 2 points for interpretation, 2 for evidence-based reasoning, and 2 for safe next steps and explicit uncertainty.

### M06-U6-Q08 — Output interpretation

**ID:** `M06-U6-Q08`  
**Category:** Output interpretation  
**Difficulty:** L3  
**Objective:** composition and lifecycle ownership  
**Estimated time:** 6 minutes  
**Points:** 6

**Question**

Does helm template output automatically create Helm release history? Explain.

```text
[ILLUSTRATIVE]
Input under review: Does helm template output automatically create Helm release history? Explain.
Evidence: the final rendered resource differs from the expected environment state; source and intermediate outputs are available for comparison.
```

**Model answer**

Compare the expected and actual final resource, locate the first stage where they diverge, and correct the source of the mismatch. Validate the final output and check live state only through the approved lifecycle owner.

**Rationale**

The reasoning chain should proceed from evidence to hypothesis, then a bounded validation step; it should not invent command results.

**Common wrong answers / failure modes**

Tempting error: treating a successful render/build as proof that resources were accepted or are healthy. Another error is to patch live state before locating the source of divergence.

**Scoring guidance**

Award 2 points for interpretation, 2 for evidence-based reasoning, and 2 for safe next steps and explicit uncertainty.

### M06-U6-Q09 — Configuration review

**ID:** `M06-U6-Q09`  
**Category:** Configuration review  
**Difficulty:** L3  
**Objective:** composition and lifecycle ownership  
**Estimated time:** 8 minutes  
**Points:** 8

**Question**

Review a pipeline that directly applies rendered output and then runs helm upgrade.

```yaml
# Choosing Helm vs Kustomize, and combining them
apiVersion: apps/v1
kind: Deployment
metadata: { name: sample }
spec:
  replicas: 2
  selector: { matchLabels: { app: sample } }
  template:
    metadata: { labels: { app: different } }
    spec:
      containers:
      - name: app
        image: example.invalid/app:latest
        securityContext: { privileged: true }
# Additional issue: the release input/dependency is not pinned or schema-validated.
```

**Model answer**

Intended defects: (1) selector `app: sample` does not match Pod label `app: different`; (2) mutable `latest` weakens release identity; (3) privileged container is unjustified and expands blast radius; (4) dependency/source is not pinned; (5) no schema/rendered-output test is shown. Correct labels, use an approved immutable reference, apply least privilege, pin the source/dependency, and add validation.

**Rationale**

A good review enumerates independent defects and connects each to impact and correction.

**Common wrong answers / failure modes**

Common failure: reporting only the syntax/target issue while missing selector, security, immutability, or validation defects.

**Scoring guidance**

Up to 2 points for each distinct defect with its consequence and correction; maximum 8.

### M06-U6-Q10 — Configuration review

**ID:** `M06-U6-Q10`  
**Category:** Configuration review  
**Difficulty:** L3  
**Objective:** composition and lifecycle ownership  
**Estimated time:** 8 minutes  
**Points:** 8

**Question**

Review an unpinned wrapper chart with a broad post-renderer and selector mutation.

```yaml
# Choosing Helm vs Kustomize, and combining them
source: ./vendor-or-base
patchTarget: name-that-does-not-exist
patchPath: /spec/replicaCount
image: example.invalid/app:latest
# Additional issue: no final rendered-output test; production override can remove a required security setting.
```

**Model answer**

Intended defects: (1) target name does not match the actual resource; (2) `/spec/replicaCount` is not the Deployment replicas path (`/spec/replicas`); (3) mutable image reference; (4) production overlay can erase a required security invariant; (5) no final-render test. Fix target/path, use an approved image identity, preserve security baseline, and test the complete build. Multiple targeted corrections may be valid.

**Rationale**

A good review enumerates independent defects and connects each to impact and correction.

**Common wrong answers / failure modes**

Common failure: reporting only the syntax/target issue while missing selector, security, immutability, or validation defects.

**Scoring guidance**

Up to 2 points for each distinct defect with its consequence and correction; maximum 8.

### M06-U6-Q11 — Incident / troubleshooting

**ID:** `M06-U6-Q11`  
**Category:** Incident / troubleshooting  
**Difficulty:** L4  
**Objective:** composition and lifecycle ownership  
**Estimated time:** 12 minutes  
**Points:** 10

**Question**

Two deployment paths modify the same resources and production drifts. Respond.

**Model answer**

Symptom → evidence → diagnosis → containment/fix → prevention: first collect the exact source, rendered artifact, tool/version inputs, live status/events/logs relevant to this unit, and prior known-good revision. Rank hypotheses from evidence. Pause risky promotion, contain with the approved owner-specific procedure, repair the source, and verify recovery. Add a regression gate and document remaining uncertainty.

**Rationale**

Incident response must preserve evidence and reduce blast radius before making a potentially destructive change.

**Common wrong answers / failure modes**

Failures include blind retries, deleting resources before inventory, assuming rollback reverses data/CRD changes, or declaring success without verification.

**Scoring guidance**

2 points each for evidence, diagnosis, containment, recovery verification, and prevention/uncertainty.

### M06-U6-Q12 — Design question

**ID:** `M06-U6-Q12`  
**Category:** Design question  
**Difficulty:** L3  
**Objective:** composition and lifecycle ownership  
**Estimated time:** 15 minutes  
**Points:** 10

**Question**

Choose a composition pattern for a vendor chart with one unsupported field.

**Model answer**

A strong answer states assumptions, alternatives, chosen approach, lifecycle owner, compatibility constraints, validation evidence, rollback/exit plan, and operational cost. Accept alternatives if the trade-offs are explicit.

**Rationale**

The objective is reasoned judgment under constraints, not a memorized tool definition.

**Common wrong answers / failure modes**

Common failures: no decision criteria, no owner, no validation, no migration/rollback path, or assuming the simplest demo is production-ready.

**Scoring guidance**

Use the unit's 10-point rubric: 2 points each for constraints/tool fit, ownership, compatibility/security, validation evidence, and rollback/operability.

## Unit 7 — Chart repositories, OCI registries, and signing

### M06-U7-Q01 — Conceptual short answer

**ID:** `M06-U7-Q01`  
**Category:** Conceptual short answer  
**Difficulty:** L1  
**Objective:** artifact identity and trust  
**Estimated time:** 4 minutes  
**Points:** 4

**Question**

How do chart version and artifact digest differ?

**Model answer**

Identify the shared cause, state the relevant lifecycle boundary, and recommend a proportionate control that preserves intentional environment differences.

**Rationale**

The expected response connects the concept to its operational consequence and a practical control.

**Common wrong answers / failure modes**

Common errors include relying on naming conventions alone, assuming a render proves deployment health, or adding complexity without a demonstrated requirement.

**Scoring guidance**

Award 1 point for the core concept, 1 for causal reasoning, 1 for operational impact, and 1 for a safe corrective action.

### M06-U7-Q02 — Conceptual short answer

**ID:** `M06-U7-Q02`  
**Category:** Conceptual short answer  
**Difficulty:** L2  
**Objective:** artifact identity and trust  
**Estimated time:** 4 minutes  
**Points:** 4

**Question**

What does a valid signature establish and not establish?

**Model answer**

Trace the input through the relevant tool stage, distinguish what the evidence proves from what remains unknown, and validate the resulting resource or artifact.

**Rationale**

The expected response connects the concept to its operational consequence and a practical control.

**Common wrong answers / failure modes**

Common errors include relying on naming conventions alone, assuming a render proves deployment health, or adding complexity without a demonstrated requirement.

**Scoring guidance**

Award 1 point for the core concept, 1 for causal reasoning, 1 for operational impact, and 1 for a safe corrective action.

### M06-U7-Q03 — Conceptual short answer

**ID:** `M06-U7-Q03`  
**Category:** Conceptual short answer  
**Difficulty:** L2  
**Objective:** artifact identity and trust  
**Estimated time:** 4 minutes  
**Points:** 4

**Question**

Why must verification happen before installation?

**Model answer**

Prefer explicit ownership, repeatable inputs, documented compatibility, and tests that exercise the final output rather than assuming tool defaults.

**Rationale**

The expected response connects the concept to its operational consequence and a practical control.

**Common wrong answers / failure modes**

Common errors include relying on naming conventions alone, assuming a render proves deployment health, or adding complexity without a demonstrated requirement.

**Scoring guidance**

Award 1 point for the core concept, 1 for causal reasoning, 1 for operational impact, and 1 for a safe corrective action.

### M06-U7-Q04 — Multiple choice

**ID:** `M06-U7-Q04`  
**Category:** Multiple choice  
**Difficulty:** L1  
**Objective:** artifact identity and trust  
**Estimated time:** 3 minutes  
**Points:** 4

**Question**

Which statement is correct?

A. Copying files prevents drift by itself.
B. A shared source with explicit differences reduces unintended drift.
C. Rendering proves runtime health.
D. An operator is always required.

**Model answer**

**Correct answer: B.** Incorrect: this leaves the underlying lifecycle or drift problem unresolved.

**Rationale**

The best answer preserves the distinction between source, rendered artifact, lifecycle operation, and runtime evidence.

**Common wrong answers / failure modes**

- **A:** Correct: this approach binds the decision to reviewable evidence and repeatable policy.
- **B:** This is the best option under the stated constraints.
- **C:** Incorrect: this confuses one validation layer with end-to-end correctness.
- **D:** Incorrect: this skips evidence gathering and can increase blast radius.

**Scoring guidance**

4 points for the correct option and a concise reason; 0–2 partial credit may be used for a correct choice with incomplete rationale.

### M06-U7-Q05 — Multiple choice

**ID:** `M06-U7-Q05`  
**Category:** Multiple choice  
**Difficulty:** L2  
**Objective:** artifact identity and trust  
**Estimated time:** 3 minutes  
**Points:** 4

**Question**

What is the safest first step?

A. Delete all resources.
B. Retry immediately.
C. Ignore the failure if YAML parses.
D. Collect relevant inputs, output, ownership, and lifecycle evidence before changing state.

**Model answer**

**Correct answer: D.** Incorrect: this skips evidence gathering and can increase blast radius.

**Rationale**

The best answer preserves the distinction between source, rendered artifact, lifecycle operation, and runtime evidence.

**Common wrong answers / failure modes**

- **A:** Correct: this approach binds the decision to reviewable evidence and repeatable policy.
- **B:** Incorrect: this leaves the underlying lifecycle or drift problem unresolved.
- **C:** Incorrect: this confuses one validation layer with end-to-end correctness.
- **D:** This is the best option under the stated constraints.

**Scoring guidance**

4 points for the correct option and a concise reason; 0–2 partial credit may be used for a correct choice with incomplete rationale.

### M06-U7-Q06 — Multiple choice

**ID:** `M06-U7-Q06`  
**Category:** Multiple choice  
**Difficulty:** L3  
**Objective:** artifact identity and trust  
**Estimated time:** 3 minutes  
**Points:** 4

**Question**

Which release control is strongest?

A. Validate the exact artifact and rendered output against documented policy.
B. Trust the filename alone.
C. Skip compatibility tests.
D. Treat signatures as proof of safety.

**Model answer**

**Correct answer: A.** Correct: this approach binds the decision to reviewable evidence and repeatable policy.

**Rationale**

The best answer preserves the distinction between source, rendered artifact, lifecycle operation, and runtime evidence.

**Common wrong answers / failure modes**

- **A:** This is the best option under the stated constraints.
- **B:** Incorrect: this leaves the underlying lifecycle or drift problem unresolved.
- **C:** Incorrect: this confuses one validation layer with end-to-end correctness.
- **D:** Incorrect: this skips evidence gathering and can increase blast radius.

**Scoring guidance**

4 points for the correct option and a concise reason; 0–2 partial credit may be used for a correct choice with incomplete rationale.

### M06-U7-Q07 — Output interpretation

**ID:** `M06-U7-Q07`  
**Category:** Output interpretation  
**Difficulty:** L2  
**Objective:** artifact identity and trust  
**Estimated time:** 6 minutes  
**Points:** 6

**Question**

A mirror returns the expected version but a different digest. Respond.

```text
[ILLUSTRATIVE]
Input under review: A mirror returns the expected version but a different digest. Respond.
Evidence: the tool reports successful rendering, but no API-server validation or apply result is provided.
```

**Model answer**

Interpret only what the supplied evidence establishes. Inspect exact source, effective values/overlay, tool version, target identity, and final rendered output; then run the next validation layer appropriate to the workflow. Do not claim that rendering proves API acceptance or runtime health. If behavior is version-sensitive, reproduce with the installed tool and record the version.

**Rationale**

The reasoning chain should proceed from evidence to hypothesis, then a bounded validation step; it should not invent command results.

**Common wrong answers / failure modes**

Tempting error: treating a successful render/build as proof that resources were accepted or are healthy. Another error is to patch live state before locating the source of divergence.

**Scoring guidance**

Award 2 points for interpretation, 2 for evidence-based reasoning, and 2 for safe next steps and explicit uncertainty.

### M06-U7-Q08 — Output interpretation

**ID:** `M06-U7-Q08`  
**Category:** Output interpretation  
**Difficulty:** L3  
**Objective:** artifact identity and trust  
**Estimated time:** 6 minutes  
**Points:** 6

**Question**

A signing key may be compromised. What is the first response sequence?

```text
[ILLUSTRATIVE]
Input under review: A signing key may be compromised. What is the first response sequence?
Evidence: the final rendered resource differs from the expected environment state; source and intermediate outputs are available for comparison.
```

**Model answer**

Compare the expected and actual final resource, locate the first stage where they diverge, and correct the source of the mismatch. Validate the final output and check live state only through the approved lifecycle owner.

**Rationale**

The reasoning chain should proceed from evidence to hypothesis, then a bounded validation step; it should not invent command results.

**Common wrong answers / failure modes**

Tempting error: treating a successful render/build as proof that resources were accepted or are healthy. Another error is to patch live state before locating the source of divergence.

**Scoring guidance**

Award 2 points for interpretation, 2 for evidence-based reasoning, and 2 for safe next steps and explicit uncertainty.

### M06-U7-Q09 — Configuration review

**ID:** `M06-U7-Q09`  
**Category:** Configuration review  
**Difficulty:** L3  
**Objective:** artifact identity and trust  
**Estimated time:** 8 minutes  
**Points:** 8

**Question**

Review a pipeline that installs before verifying and verifies a different local file.

```yaml
# Chart repositories, OCI registries, and signing
apiVersion: apps/v1
kind: Deployment
metadata: { name: sample }
spec:
  replicas: 2
  selector: { matchLabels: { app: sample } }
  template:
    metadata: { labels: { app: different } }
    spec:
      containers:
      - name: app
        image: example.invalid/app:latest
        securityContext: { privileged: true }
# Additional issue: the release input/dependency is not pinned or schema-validated.
```

**Model answer**

Intended defects: (1) selector `app: sample` does not match Pod label `app: different`; (2) mutable `latest` weakens release identity; (3) privileged container is unjustified and expands blast radius; (4) dependency/source is not pinned; (5) no schema/rendered-output test is shown. Correct labels, use an approved immutable reference, apply least privilege, pin the source/dependency, and add validation.

**Rationale**

A good review enumerates independent defects and connects each to impact and correction.

**Common wrong answers / failure modes**

Common failure: reporting only the syntax/target issue while missing selector, security, immutability, or validation defects.

**Scoring guidance**

Up to 2 points for each distinct defect with its consequence and correction; maximum 8.

### M06-U7-Q10 — Configuration review

**ID:** `M06-U7-Q10`  
**Category:** Configuration review  
**Difficulty:** L3  
**Objective:** artifact identity and trust  
**Estimated time:** 8 minutes  
**Points:** 8

**Question**

Review a mirror policy based only on filenames and a key copied to all runners.

```yaml
# Chart repositories, OCI registries, and signing
source: ./vendor-or-base
patchTarget: name-that-does-not-exist
patchPath: /spec/replicaCount
image: example.invalid/app:latest
# Additional issue: no final rendered-output test; production override can remove a required security setting.
```

**Model answer**

Intended defects: (1) target name does not match the actual resource; (2) `/spec/replicaCount` is not the Deployment replicas path (`/spec/replicas`); (3) mutable image reference; (4) production overlay can erase a required security invariant; (5) no final-render test. Fix target/path, use an approved image identity, preserve security baseline, and test the complete build. Multiple targeted corrections may be valid.

**Rationale**

A good review enumerates independent defects and connects each to impact and correction.

**Common wrong answers / failure modes**

Common failure: reporting only the syntax/target issue while missing selector, security, immutability, or validation defects.

**Scoring guidance**

Up to 2 points for each distinct defect with its consequence and correction; maximum 8.

### M06-U7-Q11 — Incident / troubleshooting

**ID:** `M06-U7-Q11`  
**Category:** Incident / troubleshooting  
**Difficulty:** L4  
**Objective:** artifact identity and trust  
**Estimated time:** 12 minutes  
**Points:** 10

**Question**

An approved chart digest differs from the mirrored artifact and key exposure is suspected. Respond.

**Model answer**

Symptom → evidence → diagnosis → containment/fix → prevention: first collect the exact source, rendered artifact, tool/version inputs, live status/events/logs relevant to this unit, and prior known-good revision. Rank hypotheses from evidence. Pause risky promotion, contain with the approved owner-specific procedure, repair the source, and verify recovery. Add a regression gate and document remaining uncertainty.

**Rationale**

Incident response must preserve evidence and reduce blast radius before making a potentially destructive change.

**Common wrong answers / failure modes**

Failures include blind retries, deleting resources before inventory, assuming rollback reverses data/CRD changes, or declaring success without verification.

**Scoring guidance**

2 points each for evidence, diagnosis, containment, recovery verification, and prevention/uncertainty.

### M06-U7-Q12 — Design question

**ID:** `M06-U7-Q12`  
**Category:** Design question  
**Difficulty:** L4  
**Objective:** artifact identity and trust  
**Estimated time:** 15 minutes  
**Points:** 10

**Question**

Design a low-cost signing and verification policy for local-to-production releases.

**Model answer**

A strong answer states assumptions, alternatives, chosen approach, lifecycle owner, compatibility constraints, validation evidence, rollback/exit plan, and operational cost. Accept alternatives if the trade-offs are explicit.

**Rationale**

The objective is reasoned judgment under constraints, not a memorized tool definition.

**Common wrong answers / failure modes**

Common failures: no decision criteria, no owner, no validation, no migration/rollback path, or assuming the simplest demo is production-ready.

**Scoring guidance**

Use the unit's 10-point rubric: 2 points each for constraints/tool fit, ownership, compatibility/security, validation evidence, and rollback/operability.

## Unit 8 — Operators, CRDs, and custom controllers overview

### M06-U8-Q01 — Conceptual short answer

**ID:** `M06-U8-Q01`  
**Category:** Conceptual short answer  
**Difficulty:** L1  
**Objective:** CRD/controller lifecycle  
**Estimated time:** 4 minutes  
**Points:** 4

**Question**

Distinguish CRD, custom resource, and controller.

**Model answer**

Identify the shared cause, state the relevant lifecycle boundary, and recommend a proportionate control that preserves intentional environment differences.

**Rationale**

The expected response connects the concept to its operational consequence and a practical control.

**Common wrong answers / failure modes**

Common errors include relying on naming conventions alone, assuming a render proves deployment health, or adding complexity without a demonstrated requirement.

**Scoring guidance**

Award 1 point for the core concept, 1 for causal reasoning, 1 for operational impact, and 1 for a safe corrective action.

### M06-U8-Q02 — Conceptual short answer

**ID:** `M06-U8-Q02`  
**Category:** Conceptual short answer  
**Difficulty:** L2  
**Objective:** CRD/controller lifecycle  
**Estimated time:** 4 minutes  
**Points:** 4

**Question**

Why must reconciliation be idempotent and use bounded backoff?

**Model answer**

Trace the input through the relevant tool stage, distinguish what the evidence proves from what remains unknown, and validate the resulting resource or artifact.

**Rationale**

The expected response connects the concept to its operational consequence and a practical control.

**Common wrong answers / failure modes**

Common errors include relying on naming conventions alone, assuming a render proves deployment health, or adding complexity without a demonstrated requirement.

**Scoring guidance**

Award 1 point for the core concept, 1 for causal reasoning, 1 for operational impact, and 1 for a safe corrective action.

### M06-U8-Q03 — Conceptual short answer

**ID:** `M06-U8-Q03`  
**Category:** Conceptual short answer  
**Difficulty:** L2  
**Objective:** CRD/controller lifecycle  
**Estimated time:** 4 minutes  
**Points:** 4

**Question**

Distinguish owner references from finalizers.

**Model answer**

Prefer explicit ownership, repeatable inputs, documented compatibility, and tests that exercise the final output rather than assuming tool defaults.

**Rationale**

The expected response connects the concept to its operational consequence and a practical control.

**Common wrong answers / failure modes**

Common errors include relying on naming conventions alone, assuming a render proves deployment health, or adding complexity without a demonstrated requirement.

**Scoring guidance**

Award 1 point for the core concept, 1 for causal reasoning, 1 for operational impact, and 1 for a safe corrective action.

### M06-U8-Q04 — Multiple choice

**ID:** `M06-U8-Q04`  
**Category:** Multiple choice  
**Difficulty:** L1  
**Objective:** CRD/controller lifecycle  
**Estimated time:** 3 minutes  
**Points:** 4

**Question**

Which statement is correct?

A. Copying files prevents drift by itself.
B. A shared source with explicit differences reduces unintended drift.
C. Rendering proves runtime health.
D. An operator is always required.

**Model answer**

**Correct answer: B.** Incorrect: this leaves the underlying lifecycle or drift problem unresolved.

**Rationale**

The best answer preserves the distinction between source, rendered artifact, lifecycle operation, and runtime evidence.

**Common wrong answers / failure modes**

- **A:** Correct: this approach binds the decision to reviewable evidence and repeatable policy.
- **B:** This is the best option under the stated constraints.
- **C:** Incorrect: this confuses one validation layer with end-to-end correctness.
- **D:** Incorrect: this skips evidence gathering and can increase blast radius.

**Scoring guidance**

4 points for the correct option and a concise reason; 0–2 partial credit may be used for a correct choice with incomplete rationale.

### M06-U8-Q05 — Multiple choice

**ID:** `M06-U8-Q05`  
**Category:** Multiple choice  
**Difficulty:** L2  
**Objective:** CRD/controller lifecycle  
**Estimated time:** 3 minutes  
**Points:** 4

**Question**

What is the safest first step?

A. Delete all resources.
B. Retry immediately.
C. Ignore the failure if YAML parses.
D. Collect relevant inputs, output, ownership, and lifecycle evidence before changing state.

**Model answer**

**Correct answer: D.** Incorrect: this skips evidence gathering and can increase blast radius.

**Rationale**

The best answer preserves the distinction between source, rendered artifact, lifecycle operation, and runtime evidence.

**Common wrong answers / failure modes**

- **A:** Correct: this approach binds the decision to reviewable evidence and repeatable policy.
- **B:** Incorrect: this leaves the underlying lifecycle or drift problem unresolved.
- **C:** Incorrect: this confuses one validation layer with end-to-end correctness.
- **D:** This is the best option under the stated constraints.

**Scoring guidance**

4 points for the correct option and a concise reason; 0–2 partial credit may be used for a correct choice with incomplete rationale.

### M06-U8-Q06 — Multiple choice

**ID:** `M06-U8-Q06`  
**Category:** Multiple choice  
**Difficulty:** L3  
**Objective:** CRD/controller lifecycle  
**Estimated time:** 3 minutes  
**Points:** 4

**Question**

Which release control is strongest?

A. Validate the exact artifact and rendered output against documented policy.
B. Trust the filename alone.
C. Skip compatibility tests.
D. Treat signatures as proof of safety.

**Model answer**

**Correct answer: A.** Correct: this approach binds the decision to reviewable evidence and repeatable policy.

**Rationale**

The best answer preserves the distinction between source, rendered artifact, lifecycle operation, and runtime evidence.

**Common wrong answers / failure modes**

- **A:** This is the best option under the stated constraints.
- **B:** Incorrect: this leaves the underlying lifecycle or drift problem unresolved.
- **C:** Incorrect: this confuses one validation layer with end-to-end correctness.
- **D:** Incorrect: this skips evidence gathering and can increase blast radius.

**Scoring guidance**

4 points for the correct option and a concise reason; 0–2 partial credit may be used for a correct choice with incomplete rationale.

### M06-U8-Q07 — Output interpretation

**ID:** `M06-U8-Q07`  
**Category:** Output interpretation  
**Difficulty:** L2  
**Objective:** CRD/controller lifecycle  
**Estimated time:** 6 minutes  
**Points:** 6

**Question**

A CR is accepted but no child resource appears. What evidence separates schema from controller health?

```text
[ILLUSTRATIVE]
Input under review: A CR is accepted but no child resource appears. What evidence separates schema from controller health?
Evidence: the tool reports successful rendering, but no API-server validation or apply result is provided.
```

**Model answer**

Interpret only what the supplied evidence establishes. Inspect exact source, effective values/overlay, tool version, target identity, and final rendered output; then run the next validation layer appropriate to the workflow. Do not claim that rendering proves API acceptance or runtime health. If behavior is version-sensitive, reproduce with the installed tool and record the version.

**Rationale**

The reasoning chain should proceed from evidence to hypothesis, then a bounded validation step; it should not invent command results.

**Common wrong answers / failure modes**

Tempting error: treating a successful render/build as proof that resources were accepted or are healthy. Another error is to patch live state before locating the source of divergence.

**Scoring guidance**

Award 2 points for interpretation, 2 for evidence-based reasoning, and 2 for safe next steps and explicit uncertainty.

### M06-U8-Q08 — Output interpretation

**ID:** `M06-U8-Q08`  
**Category:** Output interpretation  
**Difficulty:** L3  
**Objective:** CRD/controller lifecycle  
**Estimated time:** 6 minutes  
**Points:** 6

**Question**

A namespace is terminating with a custom-resource finalizer. What should be checked first?

```text
[ILLUSTRATIVE]
Input under review: A namespace is terminating with a custom-resource finalizer. What should be checked first?
Evidence: the final rendered resource differs from the expected environment state; source and intermediate outputs are available for comparison.
```

**Model answer**

Compare the expected and actual final resource, locate the first stage where they diverge, and correct the source of the mismatch. Validate the final output and check live state only through the approved lifecycle owner.

**Rationale**

The reasoning chain should proceed from evidence to hypothesis, then a bounded validation step; it should not invent command results.

**Common wrong answers / failure modes**

Tempting error: treating a successful render/build as proof that resources were accepted or are healthy. Another error is to patch live state before locating the source of divergence.

**Scoring guidance**

Award 2 points for interpretation, 2 for evidence-based reasoning, and 2 for safe next steps and explicit uncertainty.

### M06-U8-Q09 — Configuration review

**ID:** `M06-U8-Q09`  
**Category:** Configuration review  
**Difficulty:** L3  
**Objective:** CRD/controller lifecycle  
**Estimated time:** 8 minutes  
**Points:** 8

**Question**

Review a controller that creates duplicate Jobs, marks Ready prematurely, and has cluster-admin RBAC.

```yaml
# Operators, CRDs, and custom controllers overview
apiVersion: apps/v1
kind: Deployment
metadata: { name: sample }
spec:
  replicas: 2
  selector: { matchLabels: { app: sample } }
  template:
    metadata: { labels: { app: different } }
    spec:
      containers:
      - name: app
        image: example.invalid/app:latest
        securityContext: { privileged: true }
# Additional issue: the release input/dependency is not pinned or schema-validated.
```

**Model answer**

Intended defects: (1) selector `app: sample` does not match Pod label `app: different`; (2) mutable `latest` weakens release identity; (3) privileged container is unjustified and expands blast radius; (4) dependency/source is not pinned; (5) no schema/rendered-output test is shown. Correct labels, use an approved immutable reference, apply least privilege, pin the source/dependency, and add validation.

**Rationale**

A good review enumerates independent defects and connects each to impact and correction.

**Common wrong answers / failure modes**

Common failure: reporting only the syntax/target issue while missing selector, security, immutability, or validation defects.

**Scoring guidance**

Up to 2 points for each distinct defect with its consequence and correction; maximum 8.

### M06-U8-Q10 — Configuration review

**ID:** `M06-U8-Q10`  
**Category:** Configuration review  
**Difficulty:** L3  
**Objective:** CRD/controller lifecycle  
**Estimated time:** 8 minutes  
**Points:** 8

**Question**

Review a CRD deletion upgrade plan with no inventory and a broken webhook.

```yaml
# Operators, CRDs, and custom controllers overview
source: ./vendor-or-base
patchTarget: name-that-does-not-exist
patchPath: /spec/replicaCount
image: example.invalid/app:latest
# Additional issue: no final rendered-output test; production override can remove a required security setting.
```

**Model answer**

Intended defects: (1) target name does not match the actual resource; (2) `/spec/replicaCount` is not the Deployment replicas path (`/spec/replicas`); (3) mutable image reference; (4) production overlay can erase a required security invariant; (5) no final-render test. Fix target/path, use an approved image identity, preserve security baseline, and test the complete build. Multiple targeted corrections may be valid.

**Rationale**

A good review enumerates independent defects and connects each to impact and correction.

**Common wrong answers / failure modes**

Common failure: reporting only the syntax/target issue while missing selector, security, immutability, or validation defects.

**Scoring guidance**

Up to 2 points for each distinct defect with its consequence and correction; maximum 8.

### M06-U8-Q11 — Incident / troubleshooting

**ID:** `M06-U8-Q11`  
**Category:** Incident / troubleshooting  
**Difficulty:** L4  
**Objective:** CRD/controller lifecycle  
**Estimated time:** 12 minutes  
**Points:** 10

**Question**

A webhook outage blocks Pod creation while a CRD schema upgrade rejects old objects. Respond.

**Model answer**

Symptom → evidence → diagnosis → containment/fix → prevention: first collect the exact source, rendered artifact, tool/version inputs, live status/events/logs relevant to this unit, and prior known-good revision. Rank hypotheses from evidence. Pause risky promotion, contain with the approved owner-specific procedure, repair the source, and verify recovery. Add a regression gate and document remaining uncertainty.

**Rationale**

Incident response must preserve evidence and reduce blast radius before making a potentially destructive change.

**Common wrong answers / failure modes**

Failures include blind retries, deleting resources before inventory, assuming rollback reverses data/CRD changes, or declaring success without verification.

**Scoring guidance**

2 points each for evidence, diagnosis, containment, recovery verification, and prevention/uncertainty.

### M06-U8-Q12 — Design question

**ID:** `M06-U8-Q12`  
**Category:** Design question  
**Difficulty:** L4  
**Objective:** CRD/controller lifecycle  
**Estimated time:** 15 minutes  
**Points:** 10

**Question**

Decide whether recurring pipeline operations justify a custom operator.

**Model answer**

A strong answer states assumptions, alternatives, chosen approach, lifecycle owner, compatibility constraints, validation evidence, rollback/exit plan, and operational cost. Accept alternatives if the trade-offs are explicit.

**Rationale**

The objective is reasoned judgment under constraints, not a memorized tool definition.

**Common wrong answers / failure modes**

Common failures: no decision criteria, no owner, no validation, no migration/rollback path, or assuming the simplest demo is production-ready.

**Scoring guidance**

Use the unit's 10-point rubric: 2 points each for constraints/tool fit, ownership, compatibility/security, validation evidence, and rollback/operability.

## Cross-unit integration questions

Exactly 44 questions follow; each connects at least two M06 units.

### M06-X-Q001 — Cross-unit — Packaging and rendered-manifest reasoning

**ID:** `M06-X-Q001`  
**Category:** Cross-unit — Packaging and rendered-manifest reasoning  
**Difficulty:** L2  
**Objective:** Integrate U1/U2/U5: packaging and rendered-manifest reasoning  
**Estimated time:** 6 minutes  
**Points:** 5

**Question**

Three environments duplicate a Deployment; only replicas differ. Choose a tool and gates.

**Model answer**

Use plain manifests only if duplication stays trivial; otherwise a Kustomize base/overlay or Helm values API may fit. Render/build each environment, validate output, review diffs, and verify rollout separately.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 5 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q002 — Cross-unit — Packaging and rendered-manifest reasoning

**ID:** `M06-X-Q002`  
**Category:** Cross-unit — Packaging and rendered-manifest reasoning  
**Difficulty:** L2  
**Objective:** Integrate U1/U2/U5: packaging and rendered-manifest reasoning  
**Estimated time:** 6 minutes  
**Points:** 5

**Question**

Predict final replicas when Helm renders 2 and a later matching Kustomize replica transformer sets 4.

**Model answer**

In a render-then-transform pipeline the final output should show 4 if the transformer targets the intended Deployment. Confirm stage order, target identity, and installed version.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 5 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q003 — Cross-unit — Packaging and rendered-manifest reasoning

**ID:** `M06-X-Q003`  
**Category:** Cross-unit — Packaging and rendered-manifest reasoning  
**Difficulty:** L2  
**Objective:** Integrate U1/U2/U5: packaging and rendered-manifest reasoning  
**Estimated time:** 10 minutes  
**Points:** 6

**Question**

A chart exposes `environment` but hardcodes hostnames and images. Review its API.

**Model answer**

Expose only supported, documented fields that consumers need; align templates, schema, defaults, and tests. Do not make every template detail configurable.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 6 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q004 — Cross-unit — Packaging and rendered-manifest reasoning

**ID:** `M06-X-Q004`  
**Category:** Cross-unit — Packaging and rendered-manifest reasoning  
**Difficulty:** L2  
**Objective:** Integrate U1/U2/U5: packaging and rendered-manifest reasoning  
**Estimated time:** 6 minutes  
**Points:** 5

**Question**

Selector labels differ between staging and production although only image should change.

**Model answer**

Preserve selector identity and matching Pod labels. Treat selector changes as compatibility risks and assert invariants in rendered-output tests.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 5 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q005 — Cross-unit — Packaging and rendered-manifest reasoning

**ID:** `M06-X-Q005`  
**Category:** Cross-unit — Packaging and rendered-manifest reasoning  
**Difficulty:** L2  
**Objective:** Integrate U1/U2/U5: packaging and rendered-manifest reasoning  
**Estimated time:** 6 minutes  
**Points:** 5

**Question**

A successful render is reported as proof of production deployment.

**Model answer**

Rendering proves output generation only. Add manifest/API validation, explicit apply/upgrade evidence, rollout readiness, and smoke checks.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 5 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q006 — Cross-unit — Packaging and rendered-manifest reasoning

**ID:** `M06-X-Q006`  
**Category:** Cross-unit — Packaging and rendered-manifest reasoning  
**Difficulty:** L2  
**Objective:** Integrate U1/U2/U5: packaging and rendered-manifest reasoning  
**Estimated time:** 10 minutes  
**Points:** 6

**Question**

A Service selector matches no Pod labels. Debug efficiently.

**Model answer**

Compare final rendered Service selectors and Pod template labels, inspect transformations and effective values, then inspect live endpoints after the approved apply path.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 6 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q007 — Cross-unit — Helm chart interface and lifecycle

**ID:** `M06-X-Q007`  
**Category:** Cross-unit — Helm chart interface and lifecycle  
**Difficulty:** L2  
**Objective:** Integrate U2/U3/U4: helm chart interface and lifecycle  
**Estimated time:** 6 minutes  
**Points:** 5

**Question**

An optional backward-compatible values field is added.

**Model answer**

Usually a minor chart release if it adds functionality without breaking consumers; version the chart artifact and document the interface.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 5 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q008 — Cross-unit — Helm chart interface and lifecycle

**ID:** `M06-X-Q008`  
**Category:** Cross-unit — Helm chart interface and lifecycle  
**Difficulty:** L2  
**Objective:** Integrate U2/U3/U4: helm chart interface and lifecycle  
**Estimated time:** 6 minutes  
**Points:** 5

**Question**

An upgrade uses `--reuse-values` and a new security default seems absent.

**Model answer**

[VERSION-SENSITIVE] Inspect effective values and rendered output with the target Helm version; do not assume new defaults merge as expected with stored values.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 5 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q009 — Cross-unit — Helm chart interface and lifecycle

**ID:** `M06-X-Q009`  
**Category:** Cross-unit — Helm chart interface and lifecycle  
**Difficulty:** L2  
**Objective:** Integrate U2/U3/U4: helm chart interface and lifecycle  
**Estimated time:** 10 minutes  
**Points:** 6

**Question**

A pre-upgrade migration hook failed halfway.

**Model answer**

Collect logs, release status, hook annotations, and external migration state. Do not retry until repeatability/partial side effects are understood.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 6 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q010 — Cross-unit — Helm chart interface and lifecycle

**ID:** `M06-X-Q010`  
**Category:** Cross-unit — Helm chart interface and lifecycle  
**Difficulty:** L2  
**Objective:** Integrate U2/U3/U4: helm chart interface and lifecycle  
**Estimated time:** 6 minutes  
**Points:** 5

**Question**

A wildcard subchart dependency changes RBAC unexpectedly.

**Model answer**

Pin the dependency, inspect the resolved package and rendered RBAC, then test the exact dependency graph before promotion.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 5 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q011 — Cross-unit — Helm chart interface and lifecycle

**ID:** `M06-X-Q011`  
**Category:** Cross-unit — Helm chart interface and lifecycle  
**Difficulty:** L2  
**Objective:** Integrate U2/U3/U4: helm chart interface and lifecycle  
**Estimated time:** 6 minutes  
**Points:** 5

**Question**

A required values key is renamed.

**Model answer**

Treat as breaking unless staged compatibility/deprecation retains the old key; publish migration notes and consumer rollout plan.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 5 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q012 — Cross-unit — Helm chart interface and lifecycle

**ID:** `M06-X-Q012`  
**Category:** Cross-unit — Helm chart interface and lifecycle  
**Difficulty:** L2  
**Objective:** Integrate U2/U3/U4: helm chart interface and lifecycle  
**Estimated time:** 10 minutes  
**Points:** 6

**Question**

A hook Job lacks cleanup and failure policy.

**Model answer**

Review lifecycle semantics, idempotency, timeout, retry and cleanup behavior; test failed install/upgrade cases with the installed Helm version.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 6 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q013 — Cross-unit — Kustomize and composition

**ID:** `M06-X-Q013`  
**Category:** Cross-unit — Kustomize and composition  
**Difficulty:** L3  
**Objective:** Integrate U5/U6: kustomize and composition  
**Estimated time:** 6 minutes  
**Points:** 5

**Question**

Overlays repeat whole Deployments to change image and replicas.

**Model answer**

Use a shared base and narrow patches/transformers; preserve selectors/security invariants and test each final build.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 5 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q014 — Cross-unit — Kustomize and composition

**ID:** `M06-X-Q014`  
**Category:** Cross-unit — Kustomize and composition  
**Difficulty:** L3  
**Objective:** Integrate U5/U6: kustomize and composition  
**Estimated time:** 6 minutes  
**Points:** 5

**Question**

A JSON Patch uses `/spec/replicaCount`.

**Model answer**

Inspect the actual resource schema; Deployment uses `spec.replicas`. Confirm operation and target match.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 5 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q015 — Cross-unit — Kustomize and composition

**ID:** `M06-X-Q015`  
**Category:** Cross-unit — Kustomize and composition  
**Difficulty:** L3  
**Objective:** Integrate U5/U6: kustomize and composition  
**Estimated time:** 10 minutes  
**Points:** 6

**Question**

Generated ConfigMap hash changes but a workload has a literal old name.

**Model answer**

Ensure generator references are transformed in the same build and inspect the full output; avoid hardcoded generated names.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 6 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q016 — Cross-unit — Kustomize and composition

**ID:** `M06-X-Q016`  
**Category:** Cross-unit — Kustomize and composition  
**Difficulty:** L3  
**Objective:** Integrate U5/U6: kustomize and composition  
**Estimated time:** 6 minutes  
**Points:** 5

**Question**

A production overlay changes immutable selector labels.

**Model answer**

Keep identity stable; if identity migration is necessary, plan a separate resource and traffic transition instead of casual mutation.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 5 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q017 — Cross-unit — Kustomize and composition

**ID:** `M06-X-Q017`  
**Category:** Cross-unit — Kustomize and composition  
**Difficulty:** L3  
**Objective:** Integrate U5/U6: kustomize and composition  
**Estimated time:** 6 minutes  
**Points:** 5

**Question**

Compare render-then-patch, Kustomize Helm integration, and Helm post-renderer.

**Model answer**

Render-then-patch gives final artifacts but changes lifecycle ownership; Kustomize Helm integration is version/setup-sensitive; post-renderer keeps Helm lifecycle but adds executable trust and testing requirements.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 5 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q018 — Cross-unit — Kustomize and composition

**ID:** `M06-X-Q018`  
**Category:** Cross-unit — Kustomize and composition  
**Difficulty:** L3  
**Objective:** Integrate U5/U6: kustomize and composition  
**Estimated time:** 10 minutes  
**Points:** 6

**Question**

Helm syntax remains literal after a Kustomize stage.

**Model answer**

Assign each field to one template engine, inspect intermediate outputs, and assert no unresolved tokens remain unless intentionally literal.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 6 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q019 — Cross-unit — Artifact distribution and trust

**ID:** `M06-X-Q019`  
**Category:** Cross-unit — Artifact distribution and trust  
**Difficulty:** L3  
**Objective:** Integrate U4/U7: artifact distribution and trust  
**Estimated time:** 6 minutes  
**Points:** 5

**Question**

A chart is packaged and pushed to OCI. What identity should be recorded?

**Model answer**

Record chart/version, digest, source commit, tool inputs, signature/provenance and registry destination; verify the exact pulled artifact before installation.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 5 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q020 — Cross-unit — Artifact distribution and trust

**ID:** `M06-X-Q020`  
**Category:** Cross-unit — Artifact distribution and trust  
**Difficulty:** L3  
**Objective:** Integrate U4/U7: artifact distribution and trust  
**Estimated time:** 6 minutes  
**Points:** 5

**Question**

Same version label, different artifact digest.

**Model answer**

Stop promotion, quarantine and compare bytes, build logs, and mirror/registry audit data. Approve only the exact reviewed digest.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 5 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q021 — Cross-unit — Artifact distribution and trust

**ID:** `M06-X-Q021`  
**Category:** Cross-unit — Artifact distribution and trust  
**Difficulty:** L3  
**Objective:** Integrate U4/U7: artifact distribution and trust  
**Estimated time:** 10 minutes  
**Points:** 6

**Question**

A valid signature accompanies cluster-admin RBAC.

**Model answer**

Do not infer safety. Verify trusted signer and exact artifact, then independently review rendered RBAC, source, configuration, and policy.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 6 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q022 — Cross-unit — Artifact distribution and trust

**ID:** `M06-X-Q022`  
**Category:** Cross-unit — Artifact distribution and trust  
**Difficulty:** L3  
**Objective:** Integrate U4/U7: artifact distribution and trust  
**Estimated time:** 6 minutes  
**Points:** 5

**Question**

Verification runs after installation.

**Model answer**

Move verification before consumption and bind it to the exact artifact/digest and expected signer identity. Retain logs and release evidence.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 5 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q023 — Cross-unit — Artifact distribution and trust

**ID:** `M06-X-Q023`  
**Category:** Cross-unit — Artifact distribution and trust  
**Difficulty:** L3  
**Objective:** Integrate U4/U7: artifact distribution and trust  
**Estimated time:** 6 minutes  
**Points:** 5

**Question**

A mirror serves an older artifact under a familiar version.

**Model answer**

Compare approved digest and audit sync history; stop promotion and refresh only from a trusted source after verification.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 5 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q024 — Cross-unit — Artifact distribution and trust

**ID:** `M06-X-Q024`  
**Category:** Cross-unit — Artifact distribution and trust  
**Difficulty:** L3  
**Objective:** Integrate U4/U7: artifact distribution and trust  
**Estimated time:** 10 minutes  
**Points:** 6

**Question**

A signing key may be compromised.

**Model answer**

Freeze signing/promotions, preserve evidence, determine exposure scope, rotate/revoke trust according to policy, rebuild and re-sign verified artifacts, and notify stakeholders.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 6 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q025 — Cross-unit — CRDs and operators

**ID:** `M06-X-Q025`  
**Category:** Cross-unit — CRDs and operators  
**Difficulty:** L3  
**Objective:** Integrate U3/U8: crds and operators  
**Estimated time:** 6 minutes  
**Points:** 5

**Question**

A CRD is accepted but no child resource appears.

**Model answer**

Inspect controller health/logs, watch scope, RBAC, queue errors, events and status. CRD acceptance proves schema validation, not reconciliation.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 5 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q026 — Cross-unit — CRDs and operators

**ID:** `M06-X-Q026`  
**Category:** Cross-unit — CRDs and operators  
**Difficulty:** L3  
**Objective:** Integrate U3/U8: crds and operators  
**Estimated time:** 6 minutes  
**Points:** 5

**Question**

An operator tightens schema and existing CRs fail.

**Model answer**

Stop rollout, inventory and back up CRs, compare schema/versions/conversion, test compatibility and rollback limits, and stage a safe migration.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 5 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q027 — Cross-unit — CRDs and operators

**ID:** `M06-X-Q027`  
**Category:** Cross-unit — CRDs and operators  
**Difficulty:** L3  
**Objective:** Integrate U3/U8: crds and operators  
**Estimated time:** 10 minutes  
**Points:** 6

**Question**

Helm chart upgrade does not update an existing CRD as expected.

**Model answer**

Inspect the chart's CRD lifecycle and installed Helm version; follow documented CRD migration rather than assuming ordinary release rollback reverses it.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 6 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q028 — Cross-unit — CRDs and operators

**ID:** `M06-X-Q028`  
**Category:** Cross-unit — CRDs and operators  
**Difficulty:** L3  
**Objective:** Integrate U3/U8: crds and operators  
**Estimated time:** 6 minutes  
**Points:** 5

**Question**

A webhook outage blocks Pod creation.

**Model answer**

Collect admission errors, service/endpoints/certificates and failure policy; contain using approved scoped mitigation and restore webhook health. Avoid deleting CRDs or disabling admission globally by default.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 5 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q029 — Cross-unit — CRDs and operators

**ID:** `M06-X-Q029`  
**Category:** Cross-unit — CRDs and operators  
**Difficulty:** L3  
**Objective:** Integrate U3/U8: crds and operators  
**Estimated time:** 6 minutes  
**Points:** 5

**Question**

An owner reference exists but an external resource remains.

**Model answer**

Owner references support Kubernetes garbage collection; external cleanup may require controller logic/finalizers. Inspect the supported cleanup workflow.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 5 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q030 — Cross-unit — CRDs and operators

**ID:** `M06-X-Q030`  
**Category:** Cross-unit — CRDs and operators  
**Difficulty:** L3  
**Objective:** Integrate U3/U8: crds and operators  
**Estimated time:** 10 minutes  
**Points:** 6

**Question**

A controller hot-loops against the API server.

**Model answer**

Inspect repeated writes, reconcile errors, queue/backoff and request rate; fix idempotency and bounded exponential backoff, and verify API pressure falls.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 6 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q031 — Cross-unit — Production incidents

**ID:** `M06-X-Q031`  
**Category:** Cross-unit — Production incidents  
**Difficulty:** L4  
**Objective:** Integrate U2/U4/U6: production incidents  
**Estimated time:** 6 minutes  
**Points:** 5

**Question**

Production differs from staging from the same Git commit.

**Model answer**

Compare tool versions, chart/dependency digest, values/overlays, rendered output, image digest, approvals and live drift; stop promotion until first divergence is found.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 5 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q032 — Cross-unit — Production incidents

**ID:** `M06-X-Q032`  
**Category:** Cross-unit — Production incidents  
**Difficulty:** L4  
**Objective:** Integrate U2/U4/U6: production incidents  
**Estimated time:** 6 minutes  
**Points:** 5

**Question**

A chart changes a Service name and leaves two Services.

**Model answer**

Inspect old/new resource identity, endpoints, history and consumers. Halt promotion and plan traffic migration or tested rollback; do not delete either blindly.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 5 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q033 — Cross-unit — Production incidents

**ID:** `M06-X-Q033`  
**Category:** Cross-unit — Production incidents  
**Difficulty:** L4  
**Objective:** Integrate U2/U4/U6: production incidents  
**Estimated time:** 10 minutes  
**Points:** 6

**Question**

A patch removes a security setting in production.

**Model answer**

Capture exact overlay and rendered output, halt promotion, restore through the owner workflow, and add policy assertions plus a regression test.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 6 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q034 — Cross-unit — Production incidents

**ID:** `M06-X-Q034`  
**Category:** Cross-unit — Production incidents  
**Difficulty:** L4  
**Objective:** Integrate U2/U4/U6: production incidents  
**Estimated time:** 6 minutes  
**Points:** 5

**Question**

A mirror artifact was overwritten after approval.

**Model answer**

Preserve approved and retrieved digests, bytes, registry audit logs and deployments; quarantine source, restore trusted content, and investigate access controls.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 5 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q035 — Cross-unit — Production incidents

**ID:** `M06-X-Q035`  
**Category:** Cross-unit — Production incidents  
**Difficulty:** L4  
**Objective:** Integrate U2/U4/U6: production incidents  
**Estimated time:** 6 minutes  
**Points:** 5

**Question**

A CRD schema blocks updates to existing resources.

**Model answer**

Stop rollout, inventory/back up objects, determine schema versus conversion/controller failure, test a compatible migration, and document rollback limitations; never delete the CRD as a shortcut.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 5 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q036 — Cross-unit — Production incidents

**ID:** `M06-X-Q036`  
**Category:** Cross-unit — Production incidents  
**Difficulty:** L4  
**Objective:** Integrate U2/U4/U6: production incidents  
**Estimated time:** 10 minutes  
**Points:** 6

**Question**

A namespace is stuck terminating with a finalizer and controller hot loop.

**Model answer**

Inspect finalizer purpose, controller logs/RBAC, external cleanup and API errors. Restore controller/cleanup, rate-limit loops, and consider manual finalizer removal only as approved last resort.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 6 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q037 — Cross-unit — Architecture and platform design

**ID:** `M06-X-Q037`  
**Category:** Cross-unit — Architecture and platform design  
**Difficulty:** L4  
**Objective:** Integrate U1/U6/U7/U8: architecture and platform design  
**Estimated time:** 6 minutes  
**Points:** 5

**Question**

Design a reusable chart for 30 teams.

**Model answer**

Define a small documented values API, safe defaults, schema, deprecation windows, SemVer, representative tests, and staged consumer migration.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 5 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q038 — Cross-unit — Architecture and platform design

**ID:** `M06-X-Q038`  
**Category:** Cross-unit — Architecture and platform design  
**Difficulty:** L4  
**Objective:** Integrate U1/U6/U7/U8: architecture and platform design  
**Estimated time:** 6 minutes  
**Points:** 5

**Question**

Design a golden path with exceptions.

**Model answer**

Provide supported chart/overlay patterns, pinned tools, validation/evidence and ownership; require time-bounded risk-approved exceptions with tests and review/expiry.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 5 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q039 — Cross-unit — Architecture and platform design

**ID:** `M06-X-Q039`  
**Category:** Cross-unit — Architecture and platform design  
**Difficulty:** L4  
**Objective:** Integrate U1/U6/U7/U8: architecture and platform design  
**Estimated time:** 10 minutes  
**Points:** 6

**Question**

Wrap a vendor chart without making upgrades difficult.

**Model answer**

Pin upstream version/digest, expose narrow values, keep patches small, test rendered diffs/RBAC/hooks/CRDs, track upstream changes and retain an exit path.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 6 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q040 — Cross-unit — Architecture and platform design

**ID:** `M06-X-Q040`  
**Category:** Cross-unit — Architecture and platform design  
**Difficulty:** L4  
**Objective:** Integrate U1/U6/U7/U8: architecture and platform design  
**Estimated time:** 6 minutes  
**Points:** 5

**Question**

Specify a signed release policy.

**Model answer**

Build from reviewed source, pin dependencies, test output, sign exact artifact, publish digest/provenance, verify signer and digest before install, protect keys and plan compromise response.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 5 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q041 — Cross-unit — Architecture and platform design

**ID:** `M06-X-Q041`  
**Category:** Cross-unit — Architecture and platform design  
**Difficulty:** L4  
**Objective:** Integrate U1/U6/U7/U8: architecture and platform design  
**Estimated time:** 6 minutes  
**Points:** 5

**Question**

Decide whether to build an operator.

**Model answer**

Prefer existing operators or declarative packaging unless recurring domain-specific reconciliation justifies a controller; account for API evolution, retries, finalizers, RBAC, webhooks and on-call cost.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 5 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q042 — Cross-unit — Architecture and platform design

**ID:** `M06-X-Q042`  
**Category:** Cross-unit — Architecture and platform design  
**Difficulty:** L4  
**Objective:** Integrate U1/U6/U7/U8: architecture and platform design  
**Estimated time:** 10 minutes  
**Points:** 6

**Question**

Design staged rollout/rollback for image and configuration changes.

**Model answer**

Promote immutable digests, test compatibility, stage rollout, collect readiness/smoke evidence, retain previous artifact/config and state rollback limits for migrations/hooks/CRDs.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 6 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q043 — Cross-unit — Architecture and platform design

**ID:** `M06-X-Q043`  
**Category:** Cross-unit — Architecture and platform design  
**Difficulty:** L4  
**Objective:** Integrate U1/U6/U7/U8: architecture and platform design  
**Estimated time:** 6 minutes  
**Points:** 5

**Question**

GitOps wants rendered evidence and controller-owned reconciliation.

**Model answer**

Document render location/version parity, source of truth, diff evidence, drift detection and lifecycle owner; avoid competing direct-apply paths.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 5 for correct decision, supporting evidence, safe next step, and explicit trade-off.

### M06-X-Q044 — Cross-unit — Architecture and platform design

**ID:** `M06-X-Q044`  
**Category:** Cross-unit — Architecture and platform design  
**Difficulty:** L4  
**Objective:** Integrate U1/U6/U7/U8: architecture and platform design  
**Estimated time:** 10 minutes  
**Points:** 8

**Question**

Design the M06 capstone for a scoring API, ETL CronJob, and DataPipeline CR.

**Model answer**

Specify packaging boundaries, chart/overlay tests, artifact trust, staged promotion, CRD/controller/RBAC ownership, backup and rollback limits, and acceptance evidence.

**Rationale**

The answer should connect the named M06 layers and make assumptions and verification steps explicit.

**Common wrong answers / failure modes**

Common failures: treating version labels as immutable identity, confusing rendering with deployment, changing state before gathering evidence, or omitting rollback/ownership.

**Scoring guidance**

Score up to 8 for correct decision, supporting evidence, safe next step, and explicit trade-off.

## Design-review / whiteboard prompts

These eight prompts are additional to the 140 numbered core questions. Each is scored out of 10.

### DR-01 — Stable values API for 30 teams

**Scenario and constraints**

Design defaults, required values, schema, deprecation, SemVer, and migration.

**Expected artifacts / diagrams**

Values tree/schema, compatibility table, migration plan, test gates.

**Evaluation rubric (10 points)**

2 points each: interface/defaults; schema; compatibility; SemVer/release notes; staged migration/tests.

**Model answer outline**

Use a small documented API, safe defaults, typed schema, deprecation window, impact-based SemVer, consumer tests and migration notes.

**Common design failure modes**

Over-configurability, silent defaults, immediate key removal, no schema.

**Acceptable alternatives**

Nested or flatter layouts are acceptable if stable and documented.

### DR-02 — Helm, Kustomize, or both

**Scenario and constraints**

Choose for third-party dependencies and environment differences; address ownership, diffs, drift, rollback, and workflow.

**Expected artifacts / diagrams**

Decision matrix, lifecycle diagram, rendered artifact flow, rollback sequence.

**Evaluation rubric (10 points)**

2 points each: tool fit; ownership; reproducible diffs; drift/rollback; workflow/exceptions.

**Model answer outline**

Use Helm where chart values/dependencies help, Kustomize for structural overlays, or combine only with explicit stage order and ownership. Pin tools and inspect final output.

**Common design failure modes**

Ambiguous owner, competing apply paths, no exit path.

**Acceptable alternatives**

Any approach is acceptable with clear constraints and lifecycle.

### DR-03 — Vendor chart adoption

**Scenario and constraints**

Pin version, review rendered resources, choose patching strategy, manage supply-chain risk and upstream upgrades.

**Expected artifacts / diagrams**

Dependency inventory, RBAC review, patch register, upgrade/rollback plan.

**Evaluation rubric (10 points)**

2 points each: provenance/pinning; resource review; narrow patches; compatibility tests; exit path.

**Model answer outline**

Pin chart/digest, review values/schema, RBAC, hooks, CRDs and images; use supported values first; keep patches narrow; test upgrades and track upstream.

**Common design failure modes**

Wildcard versions, blanket patches, trust signature as proof of safety.

**Acceptable alternatives**

A maintained fork is acceptable if ownership/upstream merge is funded.

### DR-04 — CRD lifecycle for Helm operator

**Scenario and constraints**

Address installation, upgrade, deletion, backup, versioning, conversion and rollback limitations.

**Expected artifacts / diagrams**

CRD state diagram, inventory/backup runbook, migration matrix.

**Evaluation rubric (10 points)**

2 points each: lifecycle semantics; version/conversion; backup; rollback limits; tests/approval.

**Model answer outline**

Manage CRDs deliberately, inventory/back up CRs, stage compatible schema/controller migration, test conversion, and document rollback limits. CRD deletion deletes custom resources.

**Common design failure modes**

Assuming chart rollback reverses CRDs; deleting CRD to force replacement.

**Acceptable alternatives**

A separately managed CRD release can be appropriate.

### DR-05 — Signing and verification policy

**Scenario and constraints**

Address trust roots, rotation, digest pinning, CI permissions, mirrors and limits of signatures.

**Expected artifacts / diagrams**

Trust-boundary diagram, verification gate, compromise runbook.

**Evaluation rubric (10 points)**

2 points each: artifact identity; signer trust; key custody; mirror/CI controls; incident response.

**Model answer outline**

Sign the exact tested artifact with protected key material; record digest/provenance; verify signer and digest before install; rotate keys and respond to compromise. Continue safety review.

**Common design failure modes**

Signing different bytes, key on all runners, verify after install, equate signature with safety.

**Acceptable alternatives**

Keyless signing is acceptable with explicit identity policy.

### DR-06 — Prevent breaking chart/subchart changes

**Scenario and constraints**

Address pinning, tests, schema, SemVer, release notes and consumer migration.

**Expected artifacts / diagrams**

Dependency graph, compatibility matrix, CI map, migration schedule.

**Evaluation rubric (10 points)**

2 points each: pinned graph; tests/schema; compatibility; SemVer; migration.

**Model answer outline**

Pin dependencies, test values and upgrades, validate schema/rendered output, deprecate before removal, document impact and stage consumer migration.

**Common design failure modes**

Testing only parent, wildcard dependencies, wrong SemVer, no consumer inventory.

**Acceptable alternatives**

Coordinated major release is acceptable with a tested migration window.

### DR-07 — Operator or simpler packaging

**Scenario and constraints**

Decide whether recurring data-pipeline operations justify an operator; compare existing operators, Helm/Kustomize, Crossplane and policy.

**Expected artifacts / diagrams**

Decision tree, ownership matrix, failure model, maintenance estimate.

**Evaluation rubric (10 points)**

2 points each: requirements fit; alternatives; reconciliation need; safety burden; exit criteria.

**Model answer outline**

Prefer an existing operator or declarative packaging unless recurring domain logic needs reconciliation. Include API evolution, idempotency, retries, finalizers, RBAC, webhooks and support.

**Common design failure modes**

Building an operator for one-time install; ignoring hot loops/webhooks.

**Acceptable alternatives**

Crossplane or policy-based alternatives can fit if lifecycle ownership is clear.

### DR-08 — Promotion dev/staging/prod

**Scenario and constraints**

Address immutable image digests, environment config, approvals, evidence, drift, rollback and secrets.

**Expected artifacts / diagrams**

Promotion flow, artifact manifest, approval gates, drift/rollback procedure.

**Evaluation rubric (10 points)**

2 points each: identity; config separation; evidence/approval; drift/secrets; rollback.

**Model answer outline**

Promote the same chart/image digests, supply reviewed environment config, render and compare, verify before install, record approvals, detect drift and keep secrets out of ordinary manifests.

**Common design failure modes**

Rebuild each environment without identity controls; secret values in Git; assuming migrations roll back.

**Acceptable alternatives**

CI-rendered or controller-rendered evidence is acceptable if inputs and ownership align.

## Final scorecard and remediation plan

| Assessment area | Available points | Earned | Percentage | Weak objectives/evidence | Next action |
|---|---:|---:|---:|---|---|
| Unit 1 — Kubernetes manifest management and the templating problem | ____ | ____ | ____% | ____ | Revisit `01-kubernetes-manifest-management-and-the-templating-problem.md` and redo missed IDs |
| Unit 2 — Helm charts, values, and templates | ____ | ____ | ____% | ____ | Revisit `02-helm-charts-values-and-templates.md` and redo missed IDs |
| Unit 3 — Helm hooks, dependencies, and subcharts | ____ | ____ | ____% | ____ | Revisit `03-helm-hooks-dependencies-and-subcharts.md` and redo missed IDs |
| Unit 4 — Helm chart testing, linting, and versioning | ____ | ____ | ____% | ____ | Revisit `04-helm-chart-testing-linting-and-versioning.md` and redo missed IDs |
| Unit 5 — Kustomize bases, overlays, and patches | ____ | ____ | ____% | ____ | Revisit `05-kustomize-bases-overlays-and-patches.md` and redo missed IDs |
| Unit 6 — Choosing Helm vs Kustomize, and combining them | ____ | ____ | ____% | ____ | Revisit `06-choosing-helm-vs-kustomize-and-combining-them.md` and redo missed IDs |
| Unit 7 — Chart repositories, OCI registries, and signing | ____ | ____ | ____% | ____ | Revisit `07-chart-repositories-oci-registries-and-signing.md` and redo missed IDs |
| Unit 8 — Operators, CRDs, and custom controllers overview | ____ | ____ | ____% | ____ | Revisit `08-operators-crds-and-custom-controllers-overview.md` and redo missed IDs |
| Cross-unit integration | ____ | ____ | ____% | ____ | Retest linked units |
| Whiteboard prompts | 80 | ____ | ____% | ____ | Rewrite using rubric and peer review |
| **Overall weighted score** | ____ | ____ | ____% | ____ | Apply thresholds above |

## Coverage matrix against the syllabus

| Roadmap objective | Unit questions | Cross-unit IDs | Difficulty levels | Formats | Status | Notes/verification |
|---|---|---|---|---|---|---|
| Plain YAML duplication, declarative state, configuration boundaries | U1 Q01–Q12 | Q001–Q006 | L1–L4 | short, MCQ, output, review, incident, design | Covered | Source map from supplied prompt. |
| Helm charts, values, templates, rendering and release lifecycle | U2 Q01–Q12 | Q001–Q012,Q031–Q032,Q037 | L1–L4 | all unit formats | Covered | Render with installed Helm. |
| Hooks, dependencies, subcharts | U3 Q01–Q12 | Q009–Q012,Q039 | L1–L4 | all unit formats | Covered | Verify lifecycle semantics. |
| Linting, schema/render validation, tests, SemVer, CI | U4 Q01–Q12 | Q007,Q011,Q020,Q022,Q032,Q040,Q042 | L1–L4 | all unit formats | Covered | Actual CI/plugin syntax is version-sensitive. |
| Kustomize bases, overlays, patches, generators, components | U5 Q01–Q12 | Q002–Q006,Q013–Q018,Q033 | L1–L4 | all unit formats | Covered | Build with installed Kustomize. |
| Helm vs Kustomize, composition patterns, ownership, drift, ADR | U6 Q01–Q12 | Q017–Q018,Q031–Q033,Q038–Q039,Q043–Q044 | L1–L4 | all unit formats | Covered | Integration setup needs local verification. |
| HTTP repositories, OCI, package/version/digest | U7 Q01–Q12 | Q019–Q024,Q034 | L1–L4 | all unit formats | Covered | Registry behavior varies. |
| Signing, verification, key management, mirroring, incident response | U7 Q01–Q12 | Q019–Q024,Q034,Q040 | L2–L4 | MCQ, output, review, incident, design | Covered | Signature is not proof of safety. |
| CRD schema, served/storage versions and conversion | U8 Q01–Q12 | Q025–Q027,Q035 | L1–L4 | all unit formats | Covered | Validate against target Kubernetes version. |
| Reconciliation, idempotency, queues and backoff | U8 Q01–Q12 | Q025,Q030,Q036,Q041 | L2–L4 | review, incident, design, integration | Covered | No controller execution is claimed. |
| Finalizers, owner refs, webhooks, Helm CRD lifecycle | U8 Q01–Q12 | Q027–Q029,Q036 | L2–L4 | MCQ, output, review, incident, design | Covered | Manual finalizer removal is not default. |
| Operator inspection, RBAC, multi-tenancy, due diligence | U8 Q01–Q12 | Q028–Q030,Q036,Q041,Q044 | L2–L4 | review, incident, design | Covered | Inspect actual pinned vendor artifact. |
| Five CRD/operator incident classes | U8 Q11; Q026–Q030,Q035–Q036 | Q026–Q030,Q035–Q036 | L3–L4 | incident, output, design | Covered | CRD deletion deletes its custom resources. |
| Production trade-offs and capstone | U1–U8 Q12; DR-01–DR-08 | Q037–Q044 | L3–L4 | design/whiteboard | Covered | Use disposable lab and documented acceptance gates. |

## Version-sensitive answer notes and references

- **Helm:** consult official documentation for values merging, hooks, dependencies, OCI, provenance, CRDs, post-renderers, and tests; reproduce using the installed version.
- **Kustomize:** verify patch targeting, generator references, components, remote bases, and Helm integration using the installed version and exact build target.
- **Kubernetes:** validate against the target API version. CRD schema, CEL, pruning/defaulting, conversion, served/storage versions, webhook behavior, and printer-column JSONPath can be version-sensitive.
- **Controllers/operators:** verify queue/backoff, cache, leader election, status, finalizers, owner references, and webhook semantics against the exact framework and operator release.
- **Supply chain:** verify the exact artifact digest and trusted signer identity before installation. A signature supports integrity and trust under policy; it does not prove the artifact is benign or correctly configured.
- All outputs marked `[ILLUSTRATIVE]` are constructed examples, not executed command results. Record tool versions, inputs, commands, and observed output in lab evidence when verifying behavior.

---

## Final audit record

- Expected unit IDs: 96 (`M06-U1-Q01` through `M06-U8-Q12`), 12 per unit.
- Expected cross-unit IDs: 44 (`M06-X-Q001` through `M06-X-Q044`).
- Expected design-review prompts: 8 (`DR-01` through `DR-08`), additional to core questions.
- No live command, cluster test, signature, or release execution is claimed.
