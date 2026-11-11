# Practice Questions — Container Image Engineering and Registry Hygiene

**Purpose and audience.** This is the M01 question bank for Stage 2E — Production DevOps & Platform Engineering. It assesses a data/AI engineer who knows Git, Linux shell, Python and basic containers but has not operated production container platforms. Prerequisites are Docker basics and the eight M01 lessons. Save this standalone artifact as `Stage 2E — Production DevOps & Platform Engineering/01-Container-Image-Engineering-and-Registry-Hygiene/practice-questions.md`; the repository destination was not mounted, so no repository file was edited.

## How to use this bank

1. Complete a closed-book pass and record confidence before reading answers.
2. Review with the relevant lesson and official documentation; record the source used.
3. Run only safe local experiments in a disposable WSL2 Ubuntu/native Linux environment within approximately 4 CPU cores, 8 GB RAM and 30 GB disk.
4. Retest misses after 2–3 days and one week. Preserve a per-module score.
5. Never treat a high aggregate score as a substitute for a critical security gate.

## Levels and evidence

- **L1 Beginner:** define terms and explain core concepts.
- **L2 Intermediate:** apply patterns and interpret simple evidence.
- **L3 Advanced:** compare options, test hypotheses and measure trade-offs.
- **L4 Expert:** troubleshoot failures, define controls and reason about blast radius and recovery.

Record `ID | answer | confidence | evidence/source | score | retest date`. Times are illustrative estimates, not measured.

## Assessment rules and thresholds

Award points for reasoning and evidence, not keywords alone. Partial credit is allowed. MCQs are single-answer, four-option questions; each distractor explanation is included. Configuration reviews require at least three meaningful defects, their impact and corrections. Incident answers must distinguish confirmed facts from hypotheses and include symptom, scope, tests, mitigation, root cause, prevention and follow-up evidence. Design rubrics accept multiple valid choices when assumptions and trade-offs are explicit.

- **80% or above:** proceed if every module gate is met.
- **60–79%:** remediate weak objectives and retest.
- **Below 60%:** repeat the relevant material.
- **Critical gate:** unsafe advice such as disabling TLS, embedding secrets, trusting mutable tags, granting registry admin to workloads, or using privileged containers without justification fails the relevant gate regardless of aggregate score.

## Table of contents

- [Modules 1–8](#module-1--multi-stage-builds-and-layer-optimization)
- [Cross-module integration](#cross-module-integration)
- [Six whiteboard/design-review prompts](#six-whiteboarddesign-review-prompts)
- [Answer-key index](#answer-key-navigation-and-question-index)
- [Coverage matrices](#module-coverage-matrix)
- [Remediation map](#scoring-and-remediation-map)
- [Appendices A–E](#appendix-a--claim-and-source-register)



## Module 1 — Multi-stage builds and layer optimization

**Coverage tally:** 4 short answer; 3 MCQ; 3 command/output interpretation; 2 Dockerfile/config review; 2 incident/troubleshooting. Modules 3–8 add one design question each. Levels L1–L4 are represented.

### M01-Q001 — build context and .dockerignore

- **ID:** `M01-Q001`
- **Module / topic:** M01 — build context and .dockerignore
- **Level:** L1 Beginner
- **Objective tested:** Explain and apply build context and .dockerignore in the context of multi-stage builds and layer optimization.
- **Estimated time:** 7 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** Define and distinguish build context and .dockerignore.
- **Model answer:** Explain the core terms, what each identifies or controls, and one operational consequence. Do not infer that one control guarantees security or reproducibility.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M01-Q002 — instruction ordering and cache invalidation

- **ID:** `M01-Q002`
- **Module / topic:** M01 — instruction ordering and cache invalidation
- **Level:** L1 Beginner
- **Objective tested:** Explain and apply instruction ordering and cache invalidation in the context of multi-stage builds and layer optimization.
- **Estimated time:** 9 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** Explain how instruction ordering and cache invalidation affects a real data-service image.
- **Model answer:** Describe the mechanism, identify the inputs or runtime conditions involved, and explain how you would verify the behavior from build/runtime evidence.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M01-Q003 — builder/runtime separation

- **ID:** `M01-Q003`
- **Module / topic:** M01 — builder/runtime separation
- **Level:** L2 Intermediate
- **Objective tested:** Explain and apply builder/runtime separation in the context of multi-stage builds and layer optimization.
- **Estimated time:** 11 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** Apply builder/runtime separation to a Python FastAPI or batch ETL container.
- **Model answer:** State the design choice, the relevant compatibility/security/reliability trade-off, and a test in the final image. A builder-stage success alone does not prove runtime success.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M01-Q004 — BuildKit secrets and cache mounts

- **ID:** `M01-Q004`
- **Module / topic:** M01 — BuildKit secrets and cache mounts
- **Level:** L3 Advanced
- **Objective tested:** Explain and apply BuildKit secrets and cache mounts in the context of multi-stage builds and layer optimization.
- **Estimated time:** 13 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** At L3, evaluate BuildKit secrets and cache mounts under a production constraint.
- **Model answer:** Compare at least two options, name the assumptions and failure modes, and choose based on evidence. Record version-sensitive behavior for official-document verification.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M01-Q005 — MCQ: build context and .dockerignore

- **ID:** `M01-Q005`
- **Module / topic:** M01 — MCQ: build context and .dockerignore
- **Level:** L1 Beginner
- **Objective tested:** Choose the defensible answer about build context and .dockerignore.
- **Estimated time:** 5 minutes `[ILLUSTRATIVE]`
- **Question type:** MCQ
- **Question prompt:** Which is the most defensible approach to build context and .dockerignore?

A. Choose a documented approach, verify it against the actual build/runtime context, and retain evidence.
B. A. Assume the default is secure.
C. B. Disable the control if it causes friction.
D. C. Treat a successful build as proof of production safety.
- **Model answer:** Choose a documented approach, verify it against the actual build/runtime context, and retain evidence.
- **Common wrong answers / failure modes:** Correct answer (A): Choose a documented approach, verify it against the actual build/runtime context, and retain evidence.

Distractors:
- A. Assume the default is secure. — Defaults can vary and may not meet the workload's needs.
- B. Disable the control if it causes friction. — This removes protection without diagnosing the failure.
- C. Treat a successful build as proof of production safety. — Build success does not prove runtime compatibility or security.
- **Scoring guidance:** 4 points: 1 for the correct option, 1 for rationale, and 2 for explaining distractors; for strict MCQ scoring, the selected answer earns 1 point.
- **Source/verification note:** Official documentation named in Appendix A; do not infer current defaults without checking the installed version.


### M01-Q006 — MCQ: instruction ordering and cache invalidation

- **ID:** `M01-Q006`
- **Module / topic:** M01 — MCQ: instruction ordering and cache invalidation
- **Level:** L2 Intermediate
- **Objective tested:** Choose the defensible answer about instruction ordering and cache invalidation.
- **Estimated time:** 5 minutes `[ILLUSTRATIVE]`
- **Question type:** MCQ
- **Question prompt:** A data-service container fails after a change to instruction ordering and cache invalidation. What should be done first?

A. A. Rebuild repeatedly without recording inputs.
B. Collect the exact error, identify the affected digest/platform/configuration, and run a discriminating test.
C. B. Grant broad privileges immediately.
D. C. Roll forward to a mutable tag without checking identity.
- **Model answer:** Collect the exact error, identify the affected digest/platform/configuration, and run a discriminating test.
- **Common wrong answers / failure modes:** Correct answer (B): Collect the exact error, identify the affected digest/platform/configuration, and run a discriminating test.

Distractors:
- A. Rebuild repeatedly without recording inputs. — This creates little diagnostic evidence.
- B. Grant broad privileges immediately. — The symptom may be unrelated and the change increases blast radius.
- C. Roll forward to a mutable tag without checking identity. — The artifact may differ from the tested release.
- **Scoring guidance:** 4 points: 1 for the correct option, 1 for rationale, and 2 for explaining distractors; for strict MCQ scoring, the selected answer earns 1 point.
- **Source/verification note:** Official documentation named in Appendix A; do not infer current defaults without checking the installed version.


### M01-Q007 — MCQ: builder/runtime separation

- **ID:** `M01-Q007`
- **Module / topic:** M01 — MCQ: builder/runtime separation
- **Level:** L3 Advanced
- **Objective tested:** Choose the defensible answer about builder/runtime separation.
- **Estimated time:** 5 minutes `[ILLUSTRATIVE]`
- **Question type:** MCQ
- **Question prompt:** Which statement about builder/runtime separation is correct?

A. A. It proves the image is vulnerability-free.
B. B. It makes all builds byte-identical.
C. A control or artifact provides bounded evidence; its scope and limitations must be stated explicitly.
D. C. It replaces rollback and monitoring.
- **Model answer:** A control or artifact provides bounded evidence; its scope and limitations must be stated explicitly.
- **Common wrong answers / failure modes:** Correct answer (C): A control or artifact provides bounded evidence; its scope and limitations must be stated explicitly.

Distractors:
- A. It proves the image is vulnerability-free. — No single control proves absence of all vulnerabilities.
- B. It makes all builds byte-identical. — Reproducibility depends on all material inputs and tooling.
- C. It replaces rollback and monitoring. — Operational controls remain necessary.
- **Scoring guidance:** 4 points: 1 for the correct option, 1 for rationale, and 2 for explaining distractors; for strict MCQ scoring, the selected answer earns 1 point.
- **Source/verification note:** Official documentation named in Appendix A; do not infer current defaults without checking the installed version.


### M01-Q008 — Evidence interpretation: image-size measurement

- **ID:** `M01-Q008`
- **Module / topic:** M01 — Evidence interpretation: image-size measurement
- **Level:** L2 Intermediate
- **Objective tested:** Interpret command or log evidence about image-size measurement without inventing hidden environmental facts.
- **Estimated time:** 7 minutes `[ILLUSTRATIVE]`
- **Question type:** command/output interpretation
- **Question prompt:** A build log for a Python API changes after a source-only edit while the dependency layer reruns. Interpret this evidence in relation to image-size measurement.

Representative evidence is `[ILLUSTRATIVE]`; no command was executed for this question.
- **Model answer:** The log proves the step reran in this build, not why. Inspect instruction ordering, exact inputs, build args and cache import/export. Move stable dependency manifests before frequently changing source where appropriate, then compare logs.
- **Common wrong answers / failure modes:** Assuming illustrative output was executed; treating one symptom as conclusive root cause; changing security controls before collecting evidence.
- **Scoring guidance:** 5 points: 2 for interpretation, 1 for limits of evidence, 1 for safe test, 1 for mitigation or verification.
- **Source/verification note:** Output is illustrative. Consult official CLI/runtime documentation for current flags and defaults.


### M01-Q009 — Evidence interpretation: FastAPI dependencies

- **ID:** `M01-Q009`
- **Module / topic:** M01 — Evidence interpretation: FastAPI dependencies
- **Level:** L3 Advanced
- **Objective tested:** Interpret command or log evidence about FastAPI dependencies without inventing hidden environmental facts.
- **Estimated time:** 9 minutes `[ILLUSTRATIVE]`
- **Question type:** command/output interpretation
- **Question prompt:** [ILLUSTRATIVE] Runtime logs show a failure involving FastAPI dependencies. State what the evidence proves, what it does not prove, and the next safe diagnostic step.

Representative evidence is `[ILLUSTRATIVE]`; no command was executed for this question.
- **Model answer:** The log proves a symptom, not a unique root cause. Check the exact error, image digest, platform, effective runtime config, filesystem/identity and dependency evidence. Apply a reversible mitigation and retest the final image.
- **Common wrong answers / failure modes:** Assuming illustrative output was executed; treating one symptom as conclusive root cause; changing security controls before collecting evidence.
- **Scoring guidance:** 5 points: 2 for interpretation, 1 for limits of evidence, 1 for safe test, 1 for mitigation or verification.
- **Source/verification note:** Output is illustrative. Consult official CLI/runtime documentation for current flags and defaults.


### M01-Q010 — Evidence interpretation: Go linking

- **ID:** `M01-Q010`
- **Module / topic:** M01 — Evidence interpretation: Go linking
- **Level:** L4 Expert
- **Objective tested:** Interpret command or log evidence about Go linking without inventing hidden environmental facts.
- **Estimated time:** 11 minutes `[ILLUSTRATIVE]`
- **Question type:** command/output interpretation
- **Question prompt:** A release check reports a different image digest after a configuration change related to Go linking. What does that prove and what should be compared?

Representative evidence is `[ILLUSTRATIVE]`; no command was executed for this question.
- **Model answer:** The digest difference means the image content identity differs; it does not by itself prove tampering or identify the cause. Compare base digest, resolved dependencies, platform, image config, layer contents, timestamps and provenance; promote only validated content.
- **Common wrong answers / failure modes:** Assuming illustrative output was executed; treating one symptom as conclusive root cause; changing security controls before collecting evidence.
- **Scoring guidance:** 5 points: 2 for interpretation, 1 for limits of evidence, 1 for safe test, 1 for mitigation or verification.
- **Source/verification note:** Output is illustrative. Consult official CLI/runtime documentation for current flags and defaults.


### M01-Q011 — Configuration review 1

- **ID:** `M01-Q011`
- **Module / topic:** M01 — Configuration review 1
- **Level:** L2 Intermediate
- **Objective tested:** Find at least three meaningful defects affecting build context and .dockerignore and propose safe corrections.
- **Estimated time:** 12 minutes `[ILLUSTRATIVE]`
- **Question type:** Dockerfile/config review
- **Question prompt:** Review this design: broad `COPY . .`; mutable base tag; dependency installation after copying all source; a secret supplied using `ARG`; no final-image smoke test. Context: build context and .dockerignore and instruction ordering and cache invalidation.
- **Model answer:** Defects and fixes: (1) broad context copy may include credentials, `.git`, datasets or virtual environments; add `.dockerignore` and selective COPY. (2) mutable base reference weakens input identity; document/pin the chosen base policy. (3) copy dependency manifests before source to improve cache reuse. (4) ARG is not a secret-delivery mechanism; use a supported BuildKit secret mount and verify no logs/layers leak it. (5) add final-image startup/import/health smoke tests.
- **Common wrong answers / failure modes:** Treating formatting as a security defect; recommending disabled TLS, embedded secrets, privileged execution or broad host mounts; fixing symptoms without validation.
- **Scoring guidance:** 8 points: 2 per substantive defect including impact and correction, plus 2 for prioritization and validation. Partial credit for another safe fix.
- **Source/verification note:** [VERIFY AGAINST FINAL UNIT FILE]. Consult Dockerfile, BuildKit, OCI, registry and runtime documentation as relevant.


### M01-Q012 — Configuration review 2

- **ID:** `M01-Q012`
- **Module / topic:** M01 — Configuration review 2
- **Level:** L4 Expert
- **Objective tested:** Find at least three meaningful defects affecting instruction ordering and cache invalidation and propose safe corrections.
- **Estimated time:** 12 minutes `[ILLUSTRATIVE]`
- **Question type:** Dockerfile/config review
- **Question prompt:** Review this release/runtime configuration: image deployed by mutable tag only; no recorded digest; broad registry permissions; no rollback inventory; no evidence from the actual target platform. Context: builder/runtime separation and BuildKit secrets and cache mounts.
- **Model answer:** Defects and fixes: (1) mutable tag is not stable release identity; record and deploy approved digest. (2) broad registry permissions increase blast radius; separate pull, push and delete/admin identities. (3) no rollback inventory; retain prior approved digests. (4) no target-platform validation; test each supported architecture. (5) no evidence trail; record source/build metadata, test results and promotion approval.
- **Common wrong answers / failure modes:** Treating formatting as a security defect; recommending disabled TLS, embedded secrets, privileged execution or broad host mounts; fixing symptoms without validation.
- **Scoring guidance:** 8 points: 2 per substantive defect including impact and correction, plus 2 for prioritization and validation. Partial credit for another safe fix.
- **Source/verification note:** [VERIFY AGAINST FINAL UNIT FILE]. Consult Dockerfile, BuildKit, OCI, registry and runtime documentation as relevant.


### M01-Q013 — Incident: builder/runtime separation

- **ID:** `M01-Q013`
- **Module / topic:** M01 — Incident: builder/runtime separation
- **Level:** L3 Advanced
- **Objective tested:** Diagnose an operational failure involving builder/runtime separation and provide safe recovery.
- **Estimated time:** 15 minutes `[ILLUSTRATIVE]`
- **Question type:** incident/troubleshooting
- **Question prompt:** Incident: a production data-service rollout fails after a change involving build context and .dockerignore. Give symptom, scope, hypotheses, discriminating tests, mitigation, root cause, prevention and follow-up evidence.
- **Model answer:** First establish affected release digests, platforms, nodes and time window. Treat causes as hypotheses until logs/tests discriminate them. Preserve healthy workloads and rollback to a known approved digest if impact warrants. Fix the demonstrated cause, add a regression test, and record post-change health and ownership.
- **Common wrong answers / failure modes:** Jumping to root cause; no impact scope; unsafe cleanup; broad privilege; missing rollback or follow-up evidence.
- **Scoring guidance:** 10 points: symptom/scope 2; hypotheses/tests 2; mitigation 2; root cause/prevention 2; follow-up evidence/owner 2.
- **Source/verification note:** Illustrative scenario. Verify implementation-specific operations in the current official runbook.


### M01-Q014 — Incident: BuildKit secrets and cache mounts

- **ID:** `M01-Q014`
- **Module / topic:** M01 — Incident: BuildKit secrets and cache mounts
- **Level:** L4 Expert
- **Objective tested:** Diagnose an operational failure involving BuildKit secrets and cache mounts and provide safe recovery.
- **Estimated time:** 15 minutes `[ILLUSTRATIVE]`
- **Question type:** incident/troubleshooting
- **Question prompt:** Incident: the team proposes a broad cleanup/security bypass to resolve an issue involving BuildKit secrets and cache mounts. As incident lead, define a safer response and recovery plan.
- **Model answer:** Do not perform broad deletion or disable protections without evidence. Scope the impact, preserve artifacts/logs, inspect the actual failure and current policy, choose a reversible mitigation, and document approval. Verify recovery with pull/startup/health tests and add a runbook or guardrail.
- **Common wrong answers / failure modes:** Jumping to root cause; no impact scope; unsafe cleanup; broad privilege; missing rollback or follow-up evidence.
- **Scoring guidance:** 10 points: symptom/scope 2; hypotheses/tests 2; mitigation 2; root cause/prevention 2; follow-up evidence/owner 2.
- **Source/verification note:** Illustrative scenario. Verify implementation-specific operations in the current official runbook.



**Module tally:** 14 questions. IDs `M01-Q001` through `M01-Q014`.


## Module 2 — Minimal and distroless base images

**Coverage tally:** 4 short answer; 3 MCQ; 3 command/output interpretation; 2 Dockerfile/config review; 2 incident/troubleshooting. Modules 3–8 add one design question each. Levels L1–L4 are represented.

### M02-Q001 — full/slim/minimal/distroless trade-offs

- **ID:** `M02-Q001`
- **Module / topic:** M02 — full/slim/minimal/distroless trade-offs
- **Level:** L1 Beginner
- **Objective tested:** Explain and apply full/slim/minimal/distroless trade-offs in the context of minimal and distroless base images.
- **Estimated time:** 7 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** Define and distinguish full/slim/minimal/distroless trade-offs.
- **Model answer:** Explain the core terms, what each identifies or controls, and one operational consequence. Do not infer that one control guarantees security or reproducibility.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M02-Q002 — glibc versus musl

- **ID:** `M02-Q002`
- **Module / topic:** M02 — glibc versus musl
- **Level:** L1 Beginner
- **Objective tested:** Explain and apply glibc versus musl in the context of minimal and distroless base images.
- **Estimated time:** 9 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** Explain how glibc versus musl affects a real data-service image.
- **Model answer:** Describe the mechanism, identify the inputs or runtime conditions involved, and explain how you would verify the behavior from build/runtime evidence.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M02-Q003 — Python native wheels

- **ID:** `M02-Q003`
- **Module / topic:** M02 — Python native wheels
- **Level:** L2 Intermediate
- **Objective tested:** Explain and apply Python native wheels in the context of minimal and distroless base images.
- **Estimated time:** 11 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** Apply Python native wheels to a Python FastAPI or batch ETL container.
- **Model answer:** State the design choice, the relevant compatibility/security/reliability trade-off, and a test in the final image. A builder-stage success alone does not prove runtime success.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M02-Q004 — CA certificates

- **ID:** `M02-Q004`
- **Module / topic:** M02 — CA certificates
- **Level:** L3 Advanced
- **Objective tested:** Explain and apply CA certificates in the context of minimal and distroless base images.
- **Estimated time:** 13 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** At L3, evaluate CA certificates under a production constraint.
- **Model answer:** Compare at least two options, name the assumptions and failure modes, and choose based on evidence. Record version-sensitive behavior for official-document verification.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M02-Q005 — MCQ: full/slim/minimal/distroless trade-offs

- **ID:** `M02-Q005`
- **Module / topic:** M02 — MCQ: full/slim/minimal/distroless trade-offs
- **Level:** L1 Beginner
- **Objective tested:** Choose the defensible answer about full/slim/minimal/distroless trade-offs.
- **Estimated time:** 5 minutes `[ILLUSTRATIVE]`
- **Question type:** MCQ
- **Question prompt:** Which is the most defensible approach to full/slim/minimal/distroless trade-offs?

A. Choose a documented approach, verify it against the actual build/runtime context, and retain evidence.
B. A. Assume the default is secure.
C. B. Disable the control if it causes friction.
D. C. Treat a successful build as proof of production safety.
- **Model answer:** Choose a documented approach, verify it against the actual build/runtime context, and retain evidence.
- **Common wrong answers / failure modes:** Correct answer (A): Choose a documented approach, verify it against the actual build/runtime context, and retain evidence.

Distractors:
- A. Assume the default is secure. — Defaults can vary and may not meet the workload's needs.
- B. Disable the control if it causes friction. — This removes protection without diagnosing the failure.
- C. Treat a successful build as proof of production safety. — Build success does not prove runtime compatibility or security.
- **Scoring guidance:** 4 points: 1 for the correct option, 1 for rationale, and 2 for explaining distractors; for strict MCQ scoring, the selected answer earns 1 point.
- **Source/verification note:** Official documentation named in Appendix A; do not infer current defaults without checking the installed version.


### M02-Q006 — MCQ: glibc versus musl

- **ID:** `M02-Q006`
- **Module / topic:** M02 — MCQ: glibc versus musl
- **Level:** L2 Intermediate
- **Objective tested:** Choose the defensible answer about glibc versus musl.
- **Estimated time:** 5 minutes `[ILLUSTRATIVE]`
- **Question type:** MCQ
- **Question prompt:** A data-service container fails after a change to glibc versus musl. What should be done first?

A. A. Rebuild repeatedly without recording inputs.
B. Collect the exact error, identify the affected digest/platform/configuration, and run a discriminating test.
C. B. Grant broad privileges immediately.
D. C. Roll forward to a mutable tag without checking identity.
- **Model answer:** Collect the exact error, identify the affected digest/platform/configuration, and run a discriminating test.
- **Common wrong answers / failure modes:** Correct answer (B): Collect the exact error, identify the affected digest/platform/configuration, and run a discriminating test.

Distractors:
- A. Rebuild repeatedly without recording inputs. — This creates little diagnostic evidence.
- B. Grant broad privileges immediately. — The symptom may be unrelated and the change increases blast radius.
- C. Roll forward to a mutable tag without checking identity. — The artifact may differ from the tested release.
- **Scoring guidance:** 4 points: 1 for the correct option, 1 for rationale, and 2 for explaining distractors; for strict MCQ scoring, the selected answer earns 1 point.
- **Source/verification note:** Official documentation named in Appendix A; do not infer current defaults without checking the installed version.


### M02-Q007 — MCQ: Python native wheels

- **ID:** `M02-Q007`
- **Module / topic:** M02 — MCQ: Python native wheels
- **Level:** L3 Advanced
- **Objective tested:** Choose the defensible answer about Python native wheels.
- **Estimated time:** 5 minutes `[ILLUSTRATIVE]`
- **Question type:** MCQ
- **Question prompt:** Which statement about Python native wheels is correct?

A. A. It proves the image is vulnerability-free.
B. B. It makes all builds byte-identical.
C. A control or artifact provides bounded evidence; its scope and limitations must be stated explicitly.
D. C. It replaces rollback and monitoring.
- **Model answer:** A control or artifact provides bounded evidence; its scope and limitations must be stated explicitly.
- **Common wrong answers / failure modes:** Correct answer (C): A control or artifact provides bounded evidence; its scope and limitations must be stated explicitly.

Distractors:
- A. It proves the image is vulnerability-free. — No single control proves absence of all vulnerabilities.
- B. It makes all builds byte-identical. — Reproducibility depends on all material inputs and tooling.
- C. It replaces rollback and monitoring. — Operational controls remain necessary.
- **Scoring guidance:** 4 points: 1 for the correct option, 1 for rationale, and 2 for explaining distractors; for strict MCQ scoring, the selected answer earns 1 point.
- **Source/verification note:** Official documentation named in Appendix A; do not infer current defaults without checking the installed version.


### M02-Q008 — Evidence interpretation: timezone and locale data

- **ID:** `M02-Q008`
- **Module / topic:** M02 — Evidence interpretation: timezone and locale data
- **Level:** L2 Intermediate
- **Objective tested:** Interpret command or log evidence about timezone and locale data without inventing hidden environmental facts.
- **Estimated time:** 7 minutes `[ILLUSTRATIVE]`
- **Question type:** command/output interpretation
- **Question prompt:** A build log for a Python API changes after a source-only edit while the dependency layer reruns. Interpret this evidence in relation to timezone and locale data.

Representative evidence is `[ILLUSTRATIVE]`; no command was executed for this question.
- **Model answer:** The log proves the step reran in this build, not why. Inspect instruction ordering, exact inputs, build args and cache import/export. Move stable dependency manifests before frequently changing source where appropriate, then compare logs.
- **Common wrong answers / failure modes:** Assuming illustrative output was executed; treating one symptom as conclusive root cause; changing security controls before collecting evidence.
- **Scoring guidance:** 5 points: 2 for interpretation, 1 for limits of evidence, 1 for safe test, 1 for mitigation or verification.
- **Source/verification note:** Output is illustrative. Consult official CLI/runtime documentation for current flags and defaults.


### M02-Q009 — Evidence interpretation: numeric user metadata

- **ID:** `M02-Q009`
- **Module / topic:** M02 — Evidence interpretation: numeric user metadata
- **Level:** L3 Advanced
- **Objective tested:** Interpret command or log evidence about numeric user metadata without inventing hidden environmental facts.
- **Estimated time:** 9 minutes `[ILLUSTRATIVE]`
- **Question type:** command/output interpretation
- **Question prompt:** [ILLUSTRATIVE] Runtime logs show a failure involving numeric user metadata. State what the evidence proves, what it does not prove, and the next safe diagnostic step.

Representative evidence is `[ILLUSTRATIVE]`; no command was executed for this question.
- **Model answer:** The log proves a symptom, not a unique root cause. Check the exact error, image digest, platform, effective runtime config, filesystem/identity and dependency evidence. Apply a reversible mitigation and retest the final image.
- **Common wrong answers / failure modes:** Assuming illustrative output was executed; treating one symptom as conclusive root cause; changing security controls before collecting evidence.
- **Scoring guidance:** 5 points: 2 for interpretation, 1 for limits of evidence, 1 for safe test, 1 for mitigation or verification.
- **Source/verification note:** Output is illustrative. Consult official CLI/runtime documentation for current flags and defaults.


### M02-Q010 — Evidence interpretation: runtime dependency closure

- **ID:** `M02-Q010`
- **Module / topic:** M02 — Evidence interpretation: runtime dependency closure
- **Level:** L4 Expert
- **Objective tested:** Interpret command or log evidence about runtime dependency closure without inventing hidden environmental facts.
- **Estimated time:** 11 minutes `[ILLUSTRATIVE]`
- **Question type:** command/output interpretation
- **Question prompt:** A release check reports a different image digest after a configuration change related to runtime dependency closure. What does that prove and what should be compared?

Representative evidence is `[ILLUSTRATIVE]`; no command was executed for this question.
- **Model answer:** The digest difference means the image content identity differs; it does not by itself prove tampering or identify the cause. Compare base digest, resolved dependencies, platform, image config, layer contents, timestamps and provenance; promote only validated content.
- **Common wrong answers / failure modes:** Assuming illustrative output was executed; treating one symptom as conclusive root cause; changing security controls before collecting evidence.
- **Scoring guidance:** 5 points: 2 for interpretation, 1 for limits of evidence, 1 for safe test, 1 for mitigation or verification.
- **Source/verification note:** Output is illustrative. Consult official CLI/runtime documentation for current flags and defaults.


### M02-Q011 — Configuration review 1

- **ID:** `M02-Q011`
- **Module / topic:** M02 — Configuration review 1
- **Level:** L2 Intermediate
- **Objective tested:** Find at least three meaningful defects affecting full/slim/minimal/distroless trade-offs and propose safe corrections.
- **Estimated time:** 12 minutes `[ILLUSTRATIVE]`
- **Question type:** Dockerfile/config review
- **Question prompt:** Review this design: broad `COPY . .`; mutable base tag; dependency installation after copying all source; a secret supplied using `ARG`; no final-image smoke test. Context: full/slim/minimal/distroless trade-offs and glibc versus musl.
- **Model answer:** Defects and fixes: (1) broad context copy may include credentials, `.git`, datasets or virtual environments; add `.dockerignore` and selective COPY. (2) mutable base reference weakens input identity; document/pin the chosen base policy. (3) copy dependency manifests before source to improve cache reuse. (4) ARG is not a secret-delivery mechanism; use a supported BuildKit secret mount and verify no logs/layers leak it. (5) add final-image startup/import/health smoke tests.
- **Common wrong answers / failure modes:** Treating formatting as a security defect; recommending disabled TLS, embedded secrets, privileged execution or broad host mounts; fixing symptoms without validation.
- **Scoring guidance:** 8 points: 2 per substantive defect including impact and correction, plus 2 for prioritization and validation. Partial credit for another safe fix.
- **Source/verification note:** [VERIFY AGAINST FINAL UNIT FILE]. Consult Dockerfile, BuildKit, OCI, registry and runtime documentation as relevant.


### M02-Q012 — Configuration review 2

- **ID:** `M02-Q012`
- **Module / topic:** M02 — Configuration review 2
- **Level:** L4 Expert
- **Objective tested:** Find at least three meaningful defects affecting glibc versus musl and propose safe corrections.
- **Estimated time:** 12 minutes `[ILLUSTRATIVE]`
- **Question type:** Dockerfile/config review
- **Question prompt:** Review this release/runtime configuration: image deployed by mutable tag only; no recorded digest; broad registry permissions; no rollback inventory; no evidence from the actual target platform. Context: Python native wheels and CA certificates.
- **Model answer:** Defects and fixes: (1) mutable tag is not stable release identity; record and deploy approved digest. (2) broad registry permissions increase blast radius; separate pull, push and delete/admin identities. (3) no rollback inventory; retain prior approved digests. (4) no target-platform validation; test each supported architecture. (5) no evidence trail; record source/build metadata, test results and promotion approval.
- **Common wrong answers / failure modes:** Treating formatting as a security defect; recommending disabled TLS, embedded secrets, privileged execution or broad host mounts; fixing symptoms without validation.
- **Scoring guidance:** 8 points: 2 per substantive defect including impact and correction, plus 2 for prioritization and validation. Partial credit for another safe fix.
- **Source/verification note:** [VERIFY AGAINST FINAL UNIT FILE]. Consult Dockerfile, BuildKit, OCI, registry and runtime documentation as relevant.


### M02-Q013 — Incident: Python native wheels

- **ID:** `M02-Q013`
- **Module / topic:** M02 — Incident: Python native wheels
- **Level:** L3 Advanced
- **Objective tested:** Diagnose an operational failure involving Python native wheels and provide safe recovery.
- **Estimated time:** 15 minutes `[ILLUSTRATIVE]`
- **Question type:** incident/troubleshooting
- **Question prompt:** Incident: a production data-service rollout fails after a change involving full/slim/minimal/distroless trade-offs. Give symptom, scope, hypotheses, discriminating tests, mitigation, root cause, prevention and follow-up evidence.
- **Model answer:** First establish affected release digests, platforms, nodes and time window. Treat causes as hypotheses until logs/tests discriminate them. Preserve healthy workloads and rollback to a known approved digest if impact warrants. Fix the demonstrated cause, add a regression test, and record post-change health and ownership.
- **Common wrong answers / failure modes:** Jumping to root cause; no impact scope; unsafe cleanup; broad privilege; missing rollback or follow-up evidence.
- **Scoring guidance:** 10 points: symptom/scope 2; hypotheses/tests 2; mitigation 2; root cause/prevention 2; follow-up evidence/owner 2.
- **Source/verification note:** Illustrative scenario. Verify implementation-specific operations in the current official runbook.


### M02-Q014 — Incident: CA certificates

- **ID:** `M02-Q014`
- **Module / topic:** M02 — Incident: CA certificates
- **Level:** L4 Expert
- **Objective tested:** Diagnose an operational failure involving CA certificates and provide safe recovery.
- **Estimated time:** 15 minutes `[ILLUSTRATIVE]`
- **Question type:** incident/troubleshooting
- **Question prompt:** Incident: the team proposes a broad cleanup/security bypass to resolve an issue involving CA certificates. As incident lead, define a safer response and recovery plan.
- **Model answer:** Do not perform broad deletion or disable protections without evidence. Scope the impact, preserve artifacts/logs, inspect the actual failure and current policy, choose a reversible mitigation, and document approval. Verify recovery with pull/startup/health tests and add a runbook or guardrail.
- **Common wrong answers / failure modes:** Jumping to root cause; no impact scope; unsafe cleanup; broad privilege; missing rollback or follow-up evidence.
- **Scoring guidance:** 10 points: symptom/scope 2; hypotheses/tests 2; mitigation 2; root cause/prevention 2; follow-up evidence/owner 2.
- **Source/verification note:** Illustrative scenario. Verify implementation-specific operations in the current official runbook.



**Module tally:** 14 questions. IDs `M02-Q001` through `M02-Q014`.


## Module 3 — Reproducible and deterministic image builds

**Coverage tally:** 4 short answer; 3 MCQ; 3 command/output interpretation; 2 Dockerfile/config review; 2 incident/troubleshooting. Modules 3–8 add one design question each. Levels L1–L4 are represented.

### M03-Q001 — mutable tags versus digests

- **ID:** `M03-Q001`
- **Module / topic:** M03 — mutable tags versus digests
- **Level:** L1 Beginner
- **Objective tested:** Explain and apply mutable tags versus digests in the context of reproducible and deterministic image builds.
- **Estimated time:** 7 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** Define and distinguish mutable tags versus digests.
- **Model answer:** Explain the core terms, what each identifies or controls, and one operational consequence. Do not infer that one control guarantees security or reproducibility.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M03-Q002 — base image pinning

- **ID:** `M03-Q002`
- **Module / topic:** M03 — base image pinning
- **Level:** L1 Beginner
- **Objective tested:** Explain and apply base image pinning in the context of reproducible and deterministic image builds.
- **Estimated time:** 9 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** Explain how base image pinning affects a real data-service image.
- **Model answer:** Describe the mechanism, identify the inputs or runtime conditions involved, and explain how you would verify the behavior from build/runtime evidence.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M03-Q003 — lockfiles and hashes

- **ID:** `M03-Q003`
- **Module / topic:** M03 — lockfiles and hashes
- **Level:** L2 Intermediate
- **Objective tested:** Explain and apply lockfiles and hashes in the context of reproducible and deterministic image builds.
- **Estimated time:** 11 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** Apply lockfiles and hashes to a Python FastAPI or batch ETL container.
- **Model answer:** State the design choice, the relevant compatibility/security/reliability trade-off, and a test in the final image. A builder-stage success alone does not prove runtime success.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M03-Q004 — package repository snapshots

- **ID:** `M03-Q004`
- **Module / topic:** M03 — package repository snapshots
- **Level:** L3 Advanced
- **Objective tested:** Explain and apply package repository snapshots in the context of reproducible and deterministic image builds.
- **Estimated time:** 13 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** At L3, evaluate package repository snapshots under a production constraint.
- **Model answer:** Compare at least two options, name the assumptions and failure modes, and choose based on evidence. Record version-sensitive behavior for official-document verification.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M03-Q005 — MCQ: mutable tags versus digests

- **ID:** `M03-Q005`
- **Module / topic:** M03 — MCQ: mutable tags versus digests
- **Level:** L1 Beginner
- **Objective tested:** Choose the defensible answer about mutable tags versus digests.
- **Estimated time:** 5 minutes `[ILLUSTRATIVE]`
- **Question type:** MCQ
- **Question prompt:** Which is the most defensible approach to mutable tags versus digests?

A. Choose a documented approach, verify it against the actual build/runtime context, and retain evidence.
B. A. Assume the default is secure.
C. B. Disable the control if it causes friction.
D. C. Treat a successful build as proof of production safety.
- **Model answer:** Choose a documented approach, verify it against the actual build/runtime context, and retain evidence.
- **Common wrong answers / failure modes:** Correct answer (A): Choose a documented approach, verify it against the actual build/runtime context, and retain evidence.

Distractors:
- A. Assume the default is secure. — Defaults can vary and may not meet the workload's needs.
- B. Disable the control if it causes friction. — This removes protection without diagnosing the failure.
- C. Treat a successful build as proof of production safety. — Build success does not prove runtime compatibility or security.
- **Scoring guidance:** 4 points: 1 for the correct option, 1 for rationale, and 2 for explaining distractors; for strict MCQ scoring, the selected answer earns 1 point.
- **Source/verification note:** Official documentation named in Appendix A; do not infer current defaults without checking the installed version.


### M03-Q006 — MCQ: base image pinning

- **ID:** `M03-Q006`
- **Module / topic:** M03 — MCQ: base image pinning
- **Level:** L2 Intermediate
- **Objective tested:** Choose the defensible answer about base image pinning.
- **Estimated time:** 5 minutes `[ILLUSTRATIVE]`
- **Question type:** MCQ
- **Question prompt:** A data-service container fails after a change to base image pinning. What should be done first?

A. A. Rebuild repeatedly without recording inputs.
B. Collect the exact error, identify the affected digest/platform/configuration, and run a discriminating test.
C. B. Grant broad privileges immediately.
D. C. Roll forward to a mutable tag without checking identity.
- **Model answer:** Collect the exact error, identify the affected digest/platform/configuration, and run a discriminating test.
- **Common wrong answers / failure modes:** Correct answer (B): Collect the exact error, identify the affected digest/platform/configuration, and run a discriminating test.

Distractors:
- A. Rebuild repeatedly without recording inputs. — This creates little diagnostic evidence.
- B. Grant broad privileges immediately. — The symptom may be unrelated and the change increases blast radius.
- C. Roll forward to a mutable tag without checking identity. — The artifact may differ from the tested release.
- **Scoring guidance:** 4 points: 1 for the correct option, 1 for rationale, and 2 for explaining distractors; for strict MCQ scoring, the selected answer earns 1 point.
- **Source/verification note:** Official documentation named in Appendix A; do not infer current defaults without checking the installed version.


### M03-Q007 — MCQ: lockfiles and hashes

- **ID:** `M03-Q007`
- **Module / topic:** M03 — MCQ: lockfiles and hashes
- **Level:** L3 Advanced
- **Objective tested:** Choose the defensible answer about lockfiles and hashes.
- **Estimated time:** 5 minutes `[ILLUSTRATIVE]`
- **Question type:** MCQ
- **Question prompt:** Which statement about lockfiles and hashes is correct?

A. A. It proves the image is vulnerability-free.
B. B. It makes all builds byte-identical.
C. A control or artifact provides bounded evidence; its scope and limitations must be stated explicitly.
D. C. It replaces rollback and monitoring.
- **Model answer:** A control or artifact provides bounded evidence; its scope and limitations must be stated explicitly.
- **Common wrong answers / failure modes:** Correct answer (C): A control or artifact provides bounded evidence; its scope and limitations must be stated explicitly.

Distractors:
- A. It proves the image is vulnerability-free. — No single control proves absence of all vulnerabilities.
- B. It makes all builds byte-identical. — Reproducibility depends on all material inputs and tooling.
- C. It replaces rollback and monitoring. — Operational controls remain necessary.
- **Scoring guidance:** 4 points: 1 for the correct option, 1 for rationale, and 2 for explaining distractors; for strict MCQ scoring, the selected answer earns 1 point.
- **Source/verification note:** Official documentation named in Appendix A; do not infer current defaults without checking the installed version.


### M03-Q008 — Evidence interpretation: timestamps and SOURCE_DATE_EPOCH

- **ID:** `M03-Q008`
- **Module / topic:** M03 — Evidence interpretation: timestamps and SOURCE_DATE_EPOCH
- **Level:** L2 Intermediate
- **Objective tested:** Interpret command or log evidence about timestamps and SOURCE_DATE_EPOCH without inventing hidden environmental facts.
- **Estimated time:** 7 minutes `[ILLUSTRATIVE]`
- **Question type:** command/output interpretation
- **Question prompt:** A build log for a Python API changes after a source-only edit while the dependency layer reruns. Interpret this evidence in relation to timestamps and SOURCE_DATE_EPOCH.

Representative evidence is `[ILLUSTRATIVE]`; no command was executed for this question.
- **Model answer:** The log proves the step reran in this build, not why. Inspect instruction ordering, exact inputs, build args and cache import/export. Move stable dependency manifests before frequently changing source where appropriate, then compare logs.
- **Common wrong answers / failure modes:** Assuming illustrative output was executed; treating one symptom as conclusive root cause; changing security controls before collecting evidence.
- **Scoring guidance:** 5 points: 2 for interpretation, 1 for limits of evidence, 1 for safe test, 1 for mitigation or verification.
- **Source/verification note:** Output is illustrative. Consult official CLI/runtime documentation for current flags and defaults.


### M03-Q009 — Evidence interpretation: artifact versus image reproducibility

- **ID:** `M03-Q009`
- **Module / topic:** M03 — Evidence interpretation: artifact versus image reproducibility
- **Level:** L3 Advanced
- **Objective tested:** Interpret command or log evidence about artifact versus image reproducibility without inventing hidden environmental facts.
- **Estimated time:** 9 minutes `[ILLUSTRATIVE]`
- **Question type:** command/output interpretation
- **Question prompt:** [ILLUSTRATIVE] Runtime logs show a failure involving artifact versus image reproducibility. State what the evidence proves, what it does not prove, and the next safe diagnostic step.

Representative evidence is `[ILLUSTRATIVE]`; no command was executed for this question.
- **Model answer:** The log proves a symptom, not a unique root cause. Check the exact error, image digest, platform, effective runtime config, filesystem/identity and dependency evidence. Apply a reversible mitigation and retest the final image.
- **Common wrong answers / failure modes:** Assuming illustrative output was executed; treating one symptom as conclusive root cause; changing security controls before collecting evidence.
- **Scoring guidance:** 5 points: 2 for interpretation, 1 for limits of evidence, 1 for safe test, 1 for mitigation or verification.
- **Source/verification note:** Output is illustrative. Consult official CLI/runtime documentation for current flags and defaults.


### M03-Q010 — Evidence interpretation: hermetic/offline builds

- **ID:** `M03-Q010`
- **Module / topic:** M03 — Evidence interpretation: hermetic/offline builds
- **Level:** L4 Expert
- **Objective tested:** Interpret command or log evidence about hermetic/offline builds without inventing hidden environmental facts.
- **Estimated time:** 11 minutes `[ILLUSTRATIVE]`
- **Question type:** command/output interpretation
- **Question prompt:** A release check reports a different image digest after a configuration change related to hermetic/offline builds. What does that prove and what should be compared?

Representative evidence is `[ILLUSTRATIVE]`; no command was executed for this question.
- **Model answer:** The digest difference means the image content identity differs; it does not by itself prove tampering or identify the cause. Compare base digest, resolved dependencies, platform, image config, layer contents, timestamps and provenance; promote only validated content.
- **Common wrong answers / failure modes:** Assuming illustrative output was executed; treating one symptom as conclusive root cause; changing security controls before collecting evidence.
- **Scoring guidance:** 5 points: 2 for interpretation, 1 for limits of evidence, 1 for safe test, 1 for mitigation or verification.
- **Source/verification note:** Output is illustrative. Consult official CLI/runtime documentation for current flags and defaults.


### M03-Q011 — Configuration review 1

- **ID:** `M03-Q011`
- **Module / topic:** M03 — Configuration review 1
- **Level:** L2 Intermediate
- **Objective tested:** Find at least three meaningful defects affecting mutable tags versus digests and propose safe corrections.
- **Estimated time:** 12 minutes `[ILLUSTRATIVE]`
- **Question type:** Dockerfile/config review
- **Question prompt:** Review this design: broad `COPY . .`; mutable base tag; dependency installation after copying all source; a secret supplied using `ARG`; no final-image smoke test. Context: mutable tags versus digests and base image pinning.
- **Model answer:** Defects and fixes: (1) broad context copy may include credentials, `.git`, datasets or virtual environments; add `.dockerignore` and selective COPY. (2) mutable base reference weakens input identity; document/pin the chosen base policy. (3) copy dependency manifests before source to improve cache reuse. (4) ARG is not a secret-delivery mechanism; use a supported BuildKit secret mount and verify no logs/layers leak it. (5) add final-image startup/import/health smoke tests.
- **Common wrong answers / failure modes:** Treating formatting as a security defect; recommending disabled TLS, embedded secrets, privileged execution or broad host mounts; fixing symptoms without validation.
- **Scoring guidance:** 8 points: 2 per substantive defect including impact and correction, plus 2 for prioritization and validation. Partial credit for another safe fix.
- **Source/verification note:** [VERIFY AGAINST FINAL UNIT FILE]. Consult Dockerfile, BuildKit, OCI, registry and runtime documentation as relevant.


### M03-Q012 — Configuration review 2

- **ID:** `M03-Q012`
- **Module / topic:** M03 — Configuration review 2
- **Level:** L4 Expert
- **Objective tested:** Find at least three meaningful defects affecting base image pinning and propose safe corrections.
- **Estimated time:** 12 minutes `[ILLUSTRATIVE]`
- **Question type:** Dockerfile/config review
- **Question prompt:** Review this release/runtime configuration: image deployed by mutable tag only; no recorded digest; broad registry permissions; no rollback inventory; no evidence from the actual target platform. Context: lockfiles and hashes and package repository snapshots.
- **Model answer:** Defects and fixes: (1) mutable tag is not stable release identity; record and deploy approved digest. (2) broad registry permissions increase blast radius; separate pull, push and delete/admin identities. (3) no rollback inventory; retain prior approved digests. (4) no target-platform validation; test each supported architecture. (5) no evidence trail; record source/build metadata, test results and promotion approval.
- **Common wrong answers / failure modes:** Treating formatting as a security defect; recommending disabled TLS, embedded secrets, privileged execution or broad host mounts; fixing symptoms without validation.
- **Scoring guidance:** 8 points: 2 per substantive defect including impact and correction, plus 2 for prioritization and validation. Partial credit for another safe fix.
- **Source/verification note:** [VERIFY AGAINST FINAL UNIT FILE]. Consult Dockerfile, BuildKit, OCI, registry and runtime documentation as relevant.


### M03-Q013 — Incident: lockfiles and hashes

- **ID:** `M03-Q013`
- **Module / topic:** M03 — Incident: lockfiles and hashes
- **Level:** L3 Advanced
- **Objective tested:** Diagnose an operational failure involving lockfiles and hashes and provide safe recovery.
- **Estimated time:** 15 minutes `[ILLUSTRATIVE]`
- **Question type:** incident/troubleshooting
- **Question prompt:** Incident: a production data-service rollout fails after a change involving mutable tags versus digests. Give symptom, scope, hypotheses, discriminating tests, mitigation, root cause, prevention and follow-up evidence.
- **Model answer:** First establish affected release digests, platforms, nodes and time window. Treat causes as hypotheses until logs/tests discriminate them. Preserve healthy workloads and rollback to a known approved digest if impact warrants. Fix the demonstrated cause, add a regression test, and record post-change health and ownership.
- **Common wrong answers / failure modes:** Jumping to root cause; no impact scope; unsafe cleanup; broad privilege; missing rollback or follow-up evidence.
- **Scoring guidance:** 10 points: symptom/scope 2; hypotheses/tests 2; mitigation 2; root cause/prevention 2; follow-up evidence/owner 2.
- **Source/verification note:** Illustrative scenario. Verify implementation-specific operations in the current official runbook.


### M03-Q014 — Incident: package repository snapshots

- **ID:** `M03-Q014`
- **Module / topic:** M03 — Incident: package repository snapshots
- **Level:** L4 Expert
- **Objective tested:** Diagnose an operational failure involving package repository snapshots and provide safe recovery.
- **Estimated time:** 15 minutes `[ILLUSTRATIVE]`
- **Question type:** incident/troubleshooting
- **Question prompt:** Incident: the team proposes a broad cleanup/security bypass to resolve an issue involving package repository snapshots. As incident lead, define a safer response and recovery plan.
- **Model answer:** Do not perform broad deletion or disable protections without evidence. Scope the impact, preserve artifacts/logs, inspect the actual failure and current policy, choose a reversible mitigation, and document approval. Verify recovery with pull/startup/health tests and add a runbook or guardrail.
- **Common wrong answers / failure modes:** Jumping to root cause; no impact scope; unsafe cleanup; broad privilege; missing rollback or follow-up evidence.
- **Scoring guidance:** 10 points: symptom/scope 2; hypotheses/tests 2; mitigation 2; root cause/prevention 2; follow-up evidence/owner 2.
- **Source/verification note:** Illustrative scenario. Verify implementation-specific operations in the current official runbook.


### M03-Q015 — Whiteboard design review

- **ID:** `M03-Q015`
- **Module / topic:** M03 — Whiteboard design review
- **Level:** L4 Expert
- **Objective tested:** Design and defend a production approach to reproducible and deterministic image builds.
- **Estimated time:** 25 minutes `[ILLUSTRATIVE]`
- **Question type:** design
- **Question prompt:** Design a repeatable build workflow for a Python/pyarrow batch job. State pinned inputs, dependency hash policy, timestamp caveats, output equality criterion and reviewer evidence. Defend the criterion against a weaker alternative.
- **Model answer:** A strong answer states assumptions, provides a traceable design, names failure modes, defines acceptance evidence and defends the trade-off. Multiple architectures can earn full credit if constraints are explicit.
- **Common wrong answers / failure modes:** Selecting a tool without assumptions; claiming one universally correct answer; ignoring recovery, trust boundaries or measurable acceptance criteria.
- **Scoring guidance:** 10 points: base/tool/platform identity 2; lockfile/hash and repository strategy 2; timestamp caveats 2; repeat-build evidence 2; artifact versus image identity distinction 2.
- **Source/verification note:** [VERIFY AGAINST FINAL UNIT FILE]. Version-sensitive implementation claims require current official documentation.



**Module tally:** 15 questions. IDs `M03-Q001` through `M03-Q015`.


## Module 4 — Build caching, BuildKit, and build performance

**Coverage tally:** 4 short answer; 3 MCQ; 3 command/output interpretation; 2 Dockerfile/config review; 2 incident/troubleshooting. Modules 3–8 add one design question each. Levels L1–L4 are represented.

### M04-Q001 — cache invalidation

- **ID:** `M04-Q001`
- **Module / topic:** M04 — cache invalidation
- **Level:** L1 Beginner
- **Objective tested:** Explain and apply cache invalidation in the context of build caching, buildkit, and build performance.
- **Estimated time:** 7 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** Define and distinguish cache invalidation.
- **Model answer:** Explain the core terms, what each identifies or controls, and one operational consequence. Do not infer that one control guarantees security or reproducibility.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M04-Q002 — dependency-first copy patterns

- **ID:** `M04-Q002`
- **Module / topic:** M04 — dependency-first copy patterns
- **Level:** L1 Beginner
- **Objective tested:** Explain and apply dependency-first copy patterns in the context of build caching, buildkit, and build performance.
- **Estimated time:** 9 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** Explain how dependency-first copy patterns affects a real data-service image.
- **Model answer:** Describe the mechanism, identify the inputs or runtime conditions involved, and explain how you would verify the behavior from build/runtime evidence.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M04-Q003 — BuildKit/buildx

- **ID:** `M04-Q003`
- **Module / topic:** M04 — BuildKit/buildx
- **Level:** L2 Intermediate
- **Objective tested:** Explain and apply BuildKit/buildx in the context of build caching, buildkit, and build performance.
- **Estimated time:** 11 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** Apply BuildKit/buildx to a Python FastAPI or batch ETL container.
- **Model answer:** State the design choice, the relevant compatibility/security/reliability trade-off, and a test in the final image. A builder-stage success alone does not prove runtime success.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M04-Q004 — cache mounts

- **ID:** `M04-Q004`
- **Module / topic:** M04 — cache mounts
- **Level:** L3 Advanced
- **Objective tested:** Explain and apply cache mounts in the context of build caching, buildkit, and build performance.
- **Estimated time:** 13 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** At L3, evaluate cache mounts under a production constraint.
- **Model answer:** Compare at least two options, name the assumptions and failure modes, and choose based on evidence. Record version-sensitive behavior for official-document verification.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M04-Q005 — MCQ: cache invalidation

- **ID:** `M04-Q005`
- **Module / topic:** M04 — MCQ: cache invalidation
- **Level:** L1 Beginner
- **Objective tested:** Choose the defensible answer about cache invalidation.
- **Estimated time:** 5 minutes `[ILLUSTRATIVE]`
- **Question type:** MCQ
- **Question prompt:** Which is the most defensible approach to cache invalidation?

A. Choose a documented approach, verify it against the actual build/runtime context, and retain evidence.
B. A. Assume the default is secure.
C. B. Disable the control if it causes friction.
D. C. Treat a successful build as proof of production safety.
- **Model answer:** Choose a documented approach, verify it against the actual build/runtime context, and retain evidence.
- **Common wrong answers / failure modes:** Correct answer (A): Choose a documented approach, verify it against the actual build/runtime context, and retain evidence.

Distractors:
- A. Assume the default is secure. — Defaults can vary and may not meet the workload's needs.
- B. Disable the control if it causes friction. — This removes protection without diagnosing the failure.
- C. Treat a successful build as proof of production safety. — Build success does not prove runtime compatibility or security.
- **Scoring guidance:** 4 points: 1 for the correct option, 1 for rationale, and 2 for explaining distractors; for strict MCQ scoring, the selected answer earns 1 point.
- **Source/verification note:** Official documentation named in Appendix A; do not infer current defaults without checking the installed version.


### M04-Q006 — MCQ: dependency-first copy patterns

- **ID:** `M04-Q006`
- **Module / topic:** M04 — MCQ: dependency-first copy patterns
- **Level:** L2 Intermediate
- **Objective tested:** Choose the defensible answer about dependency-first copy patterns.
- **Estimated time:** 5 minutes `[ILLUSTRATIVE]`
- **Question type:** MCQ
- **Question prompt:** A data-service container fails after a change to dependency-first copy patterns. What should be done first?

A. A. Rebuild repeatedly without recording inputs.
B. Collect the exact error, identify the affected digest/platform/configuration, and run a discriminating test.
C. B. Grant broad privileges immediately.
D. C. Roll forward to a mutable tag without checking identity.
- **Model answer:** Collect the exact error, identify the affected digest/platform/configuration, and run a discriminating test.
- **Common wrong answers / failure modes:** Correct answer (B): Collect the exact error, identify the affected digest/platform/configuration, and run a discriminating test.

Distractors:
- A. Rebuild repeatedly without recording inputs. — This creates little diagnostic evidence.
- B. Grant broad privileges immediately. — The symptom may be unrelated and the change increases blast radius.
- C. Roll forward to a mutable tag without checking identity. — The artifact may differ from the tested release.
- **Scoring guidance:** 4 points: 1 for the correct option, 1 for rationale, and 2 for explaining distractors; for strict MCQ scoring, the selected answer earns 1 point.
- **Source/verification note:** Official documentation named in Appendix A; do not infer current defaults without checking the installed version.


### M04-Q007 — MCQ: BuildKit/buildx

- **ID:** `M04-Q007`
- **Module / topic:** M04 — MCQ: BuildKit/buildx
- **Level:** L3 Advanced
- **Objective tested:** Choose the defensible answer about BuildKit/buildx.
- **Estimated time:** 5 minutes `[ILLUSTRATIVE]`
- **Question type:** MCQ
- **Question prompt:** Which statement about BuildKit/buildx is correct?

A. A. It proves the image is vulnerability-free.
B. B. It makes all builds byte-identical.
C. A control or artifact provides bounded evidence; its scope and limitations must be stated explicitly.
D. C. It replaces rollback and monitoring.
- **Model answer:** A control or artifact provides bounded evidence; its scope and limitations must be stated explicitly.
- **Common wrong answers / failure modes:** Correct answer (C): A control or artifact provides bounded evidence; its scope and limitations must be stated explicitly.

Distractors:
- A. It proves the image is vulnerability-free. — No single control proves absence of all vulnerabilities.
- B. It makes all builds byte-identical. — Reproducibility depends on all material inputs and tooling.
- C. It replaces rollback and monitoring. — Operational controls remain necessary.
- **Scoring guidance:** 4 points: 1 for the correct option, 1 for rationale, and 2 for explaining distractors; for strict MCQ scoring, the selected answer earns 1 point.
- **Source/verification note:** Official documentation named in Appendix A; do not infer current defaults without checking the installed version.


### M04-Q008 — Evidence interpretation: local/inline/registry/CI caches

- **ID:** `M04-Q008`
- **Module / topic:** M04 — Evidence interpretation: local/inline/registry/CI caches
- **Level:** L2 Intermediate
- **Objective tested:** Interpret command or log evidence about local/inline/registry/CI caches without inventing hidden environmental facts.
- **Estimated time:** 7 minutes `[ILLUSTRATIVE]`
- **Question type:** command/output interpretation
- **Question prompt:** A build log for a Python API changes after a source-only edit while the dependency layer reruns. Interpret this evidence in relation to local/inline/registry/CI caches.

Representative evidence is `[ILLUSTRATIVE]`; no command was executed for this question.
- **Model answer:** The log proves the step reran in this build, not why. Inspect instruction ordering, exact inputs, build args and cache import/export. Move stable dependency manifests before frequently changing source where appropriate, then compare logs.
- **Common wrong answers / failure modes:** Assuming illustrative output was executed; treating one symptom as conclusive root cause; changing security controls before collecting evidence.
- **Scoring guidance:** 5 points: 2 for interpretation, 1 for limits of evidence, 1 for safe test, 1 for mitigation or verification.
- **Source/verification note:** Output is illustrative. Consult official CLI/runtime documentation for current flags and defaults.


### M04-Q009 — Evidence interpretation: cache trust boundaries

- **ID:** `M04-Q009`
- **Module / topic:** M04 — Evidence interpretation: cache trust boundaries
- **Level:** L3 Advanced
- **Objective tested:** Interpret command or log evidence about cache trust boundaries without inventing hidden environmental facts.
- **Estimated time:** 9 minutes `[ILLUSTRATIVE]`
- **Question type:** command/output interpretation
- **Question prompt:** [ILLUSTRATIVE] Runtime logs show a failure involving cache trust boundaries. State what the evidence proves, what it does not prove, and the next safe diagnostic step.

Representative evidence is `[ILLUSTRATIVE]`; no command was executed for this question.
- **Model answer:** The log proves a symptom, not a unique root cause. Check the exact error, image digest, platform, effective runtime config, filesystem/identity and dependency evidence. Apply a reversible mitigation and retest the final image.
- **Common wrong answers / failure modes:** Assuming illustrative output was executed; treating one symptom as conclusive root cause; changing security controls before collecting evidence.
- **Scoring guidance:** 5 points: 2 for interpretation, 1 for limits of evidence, 1 for safe test, 1 for mitigation or verification.
- **Source/verification note:** Output is illustrative. Consult official CLI/runtime documentation for current flags and defaults.


### M04-Q010 — Evidence interpretation: cold/warm/partial measurements

- **ID:** `M04-Q010`
- **Module / topic:** M04 — Evidence interpretation: cold/warm/partial measurements
- **Level:** L4 Expert
- **Objective tested:** Interpret command or log evidence about cold/warm/partial measurements without inventing hidden environmental facts.
- **Estimated time:** 11 minutes `[ILLUSTRATIVE]`
- **Question type:** command/output interpretation
- **Question prompt:** A release check reports a different image digest after a configuration change related to cold/warm/partial measurements. What does that prove and what should be compared?

Representative evidence is `[ILLUSTRATIVE]`; no command was executed for this question.
- **Model answer:** The digest difference means the image content identity differs; it does not by itself prove tampering or identify the cause. Compare base digest, resolved dependencies, platform, image config, layer contents, timestamps and provenance; promote only validated content.
- **Common wrong answers / failure modes:** Assuming illustrative output was executed; treating one symptom as conclusive root cause; changing security controls before collecting evidence.
- **Scoring guidance:** 5 points: 2 for interpretation, 1 for limits of evidence, 1 for safe test, 1 for mitigation or verification.
- **Source/verification note:** Output is illustrative. Consult official CLI/runtime documentation for current flags and defaults.


### M04-Q011 — Configuration review 1

- **ID:** `M04-Q011`
- **Module / topic:** M04 — Configuration review 1
- **Level:** L2 Intermediate
- **Objective tested:** Find at least three meaningful defects affecting cache invalidation and propose safe corrections.
- **Estimated time:** 12 minutes `[ILLUSTRATIVE]`
- **Question type:** Dockerfile/config review
- **Question prompt:** Review this design: broad `COPY . .`; mutable base tag; dependency installation after copying all source; a secret supplied using `ARG`; no final-image smoke test. Context: cache invalidation and dependency-first copy patterns.
- **Model answer:** Defects and fixes: (1) broad context copy may include credentials, `.git`, datasets or virtual environments; add `.dockerignore` and selective COPY. (2) mutable base reference weakens input identity; document/pin the chosen base policy. (3) copy dependency manifests before source to improve cache reuse. (4) ARG is not a secret-delivery mechanism; use a supported BuildKit secret mount and verify no logs/layers leak it. (5) add final-image startup/import/health smoke tests.
- **Common wrong answers / failure modes:** Treating formatting as a security defect; recommending disabled TLS, embedded secrets, privileged execution or broad host mounts; fixing symptoms without validation.
- **Scoring guidance:** 8 points: 2 per substantive defect including impact and correction, plus 2 for prioritization and validation. Partial credit for another safe fix.
- **Source/verification note:** [VERIFY AGAINST FINAL UNIT FILE]. Consult Dockerfile, BuildKit, OCI, registry and runtime documentation as relevant.


### M04-Q012 — Configuration review 2

- **ID:** `M04-Q012`
- **Module / topic:** M04 — Configuration review 2
- **Level:** L4 Expert
- **Objective tested:** Find at least three meaningful defects affecting dependency-first copy patterns and propose safe corrections.
- **Estimated time:** 12 minutes `[ILLUSTRATIVE]`
- **Question type:** Dockerfile/config review
- **Question prompt:** Review this release/runtime configuration: image deployed by mutable tag only; no recorded digest; broad registry permissions; no rollback inventory; no evidence from the actual target platform. Context: BuildKit/buildx and cache mounts.
- **Model answer:** Defects and fixes: (1) mutable tag is not stable release identity; record and deploy approved digest. (2) broad registry permissions increase blast radius; separate pull, push and delete/admin identities. (3) no rollback inventory; retain prior approved digests. (4) no target-platform validation; test each supported architecture. (5) no evidence trail; record source/build metadata, test results and promotion approval.
- **Common wrong answers / failure modes:** Treating formatting as a security defect; recommending disabled TLS, embedded secrets, privileged execution or broad host mounts; fixing symptoms without validation.
- **Scoring guidance:** 8 points: 2 per substantive defect including impact and correction, plus 2 for prioritization and validation. Partial credit for another safe fix.
- **Source/verification note:** [VERIFY AGAINST FINAL UNIT FILE]. Consult Dockerfile, BuildKit, OCI, registry and runtime documentation as relevant.


### M04-Q013 — Incident: BuildKit/buildx

- **ID:** `M04-Q013`
- **Module / topic:** M04 — Incident: BuildKit/buildx
- **Level:** L3 Advanced
- **Objective tested:** Diagnose an operational failure involving BuildKit/buildx and provide safe recovery.
- **Estimated time:** 15 minutes `[ILLUSTRATIVE]`
- **Question type:** incident/troubleshooting
- **Question prompt:** Incident: a production data-service rollout fails after a change involving cache invalidation. Give symptom, scope, hypotheses, discriminating tests, mitigation, root cause, prevention and follow-up evidence.
- **Model answer:** First establish affected release digests, platforms, nodes and time window. Treat causes as hypotheses until logs/tests discriminate them. Preserve healthy workloads and rollback to a known approved digest if impact warrants. Fix the demonstrated cause, add a regression test, and record post-change health and ownership.
- **Common wrong answers / failure modes:** Jumping to root cause; no impact scope; unsafe cleanup; broad privilege; missing rollback or follow-up evidence.
- **Scoring guidance:** 10 points: symptom/scope 2; hypotheses/tests 2; mitigation 2; root cause/prevention 2; follow-up evidence/owner 2.
- **Source/verification note:** Illustrative scenario. Verify implementation-specific operations in the current official runbook.


### M04-Q014 — Incident: cache mounts

- **ID:** `M04-Q014`
- **Module / topic:** M04 — Incident: cache mounts
- **Level:** L4 Expert
- **Objective tested:** Diagnose an operational failure involving cache mounts and provide safe recovery.
- **Estimated time:** 15 minutes `[ILLUSTRATIVE]`
- **Question type:** incident/troubleshooting
- **Question prompt:** Incident: the team proposes a broad cleanup/security bypass to resolve an issue involving cache mounts. As incident lead, define a safer response and recovery plan.
- **Model answer:** Do not perform broad deletion or disable protections without evidence. Scope the impact, preserve artifacts/logs, inspect the actual failure and current policy, choose a reversible mitigation, and document approval. Verify recovery with pull/startup/health tests and add a runbook or guardrail.
- **Common wrong answers / failure modes:** Jumping to root cause; no impact scope; unsafe cleanup; broad privilege; missing rollback or follow-up evidence.
- **Scoring guidance:** 10 points: symptom/scope 2; hypotheses/tests 2; mitigation 2; root cause/prevention 2; follow-up evidence/owner 2.
- **Source/verification note:** Illustrative scenario. Verify implementation-specific operations in the current official runbook.


### M04-Q015 — Whiteboard design review

- **ID:** `M04-Q015`
- **Module / topic:** M04 — Whiteboard design review
- **Level:** L4 Expert
- **Objective tested:** Design and defend a production approach to build caching, buildkit, and build performance.
- **Estimated time:** 25 minutes `[ILLUSTRATIVE]`
- **Question type:** design
- **Question prompt:** Design a cache strategy for FastAPI and PySpark images across laptops and CI. Cover cache backend, trust boundaries, cold/warm/partial metrics and failure behavior. Defend the strategy against a plausible alternative.
- **Model answer:** A strong answer states assumptions, provides a traceable design, names failure modes, defines acceptance evidence and defends the trade-off. Multiple architectures can earn full credit if constraints are explicit.
- **Common wrong answers / failure modes:** Selecting a tool without assumptions; claiming one universally correct answer; ignoring recovery, trust boundaries or measurable acceptance criteria.
- **Scoring guidance:** 10 points: layer/cache-mount distinction 2; backend fit/access 2; benchmark plan 2; poisoning/trust mitigation 2; reasoned alternative and fallback 2.
- **Source/verification note:** [VERIFY AGAINST FINAL UNIT FILE]. Version-sensitive implementation claims require current official documentation.



**Module tally:** 15 questions. IDs `M04-Q001` through `M04-Q015`.


## Module 5 — Image tagging, versioning, and immutability

**Coverage tally:** 4 short answer; 3 MCQ; 3 command/output interpretation; 2 Dockerfile/config review; 2 incident/troubleshooting. Modules 3–8 add one design question each. Levels L1–L4 are represented.

### M05-Q001 — mutable tags versus digests

- **ID:** `M05-Q001`
- **Module / topic:** M05 — mutable tags versus digests
- **Level:** L1 Beginner
- **Objective tested:** Explain and apply mutable tags versus digests in the context of image tagging, versioning, and immutability.
- **Estimated time:** 7 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** Define and distinguish mutable tags versus digests.
- **Model answer:** Explain the core terms, what each identifies or controls, and one operational consequence. Do not infer that one control guarantees security or reproducibility.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M05-Q002 — SemVer and Git SHA

- **ID:** `M05-Q002`
- **Module / topic:** M05 — SemVer and Git SHA
- **Level:** L1 Beginner
- **Objective tested:** Explain and apply SemVer and Git SHA in the context of image tagging, versioning, and immutability.
- **Estimated time:** 9 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** Explain how SemVer and Git SHA affects a real data-service image.
- **Model answer:** Describe the mechanism, identify the inputs or runtime conditions involved, and explain how you would verify the behavior from build/runtime evidence.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M05-Q003 — build metadata

- **ID:** `M05-Q003`
- **Module / topic:** M05 — build metadata
- **Level:** L2 Intermediate
- **Objective tested:** Explain and apply build metadata in the context of image tagging, versioning, and immutability.
- **Estimated time:** 11 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** Apply build metadata to a Python FastAPI or batch ETL container.
- **Model answer:** State the design choice, the relevant compatibility/security/reliability trade-off, and a test in the final image. A builder-stage success alone does not prove runtime success.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M05-Q004 — OCI labels

- **ID:** `M05-Q004`
- **Module / topic:** M05 — OCI labels
- **Level:** L3 Advanced
- **Objective tested:** Explain and apply OCI labels in the context of image tagging, versioning, and immutability.
- **Estimated time:** 13 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** At L3, evaluate OCI labels under a production constraint.
- **Model answer:** Compare at least two options, name the assumptions and failure modes, and choose based on evidence. Record version-sensitive behavior for official-document verification.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M05-Q005 — MCQ: mutable tags versus digests

- **ID:** `M05-Q005`
- **Module / topic:** M05 — MCQ: mutable tags versus digests
- **Level:** L1 Beginner
- **Objective tested:** Choose the defensible answer about mutable tags versus digests.
- **Estimated time:** 5 minutes `[ILLUSTRATIVE]`
- **Question type:** MCQ
- **Question prompt:** Which is the most defensible approach to mutable tags versus digests?

A. Choose a documented approach, verify it against the actual build/runtime context, and retain evidence.
B. A. Assume the default is secure.
C. B. Disable the control if it causes friction.
D. C. Treat a successful build as proof of production safety.
- **Model answer:** Choose a documented approach, verify it against the actual build/runtime context, and retain evidence.
- **Common wrong answers / failure modes:** Correct answer (A): Choose a documented approach, verify it against the actual build/runtime context, and retain evidence.

Distractors:
- A. Assume the default is secure. — Defaults can vary and may not meet the workload's needs.
- B. Disable the control if it causes friction. — This removes protection without diagnosing the failure.
- C. Treat a successful build as proof of production safety. — Build success does not prove runtime compatibility or security.
- **Scoring guidance:** 4 points: 1 for the correct option, 1 for rationale, and 2 for explaining distractors; for strict MCQ scoring, the selected answer earns 1 point.
- **Source/verification note:** Official documentation named in Appendix A; do not infer current defaults without checking the installed version.


### M05-Q006 — MCQ: SemVer and Git SHA

- **ID:** `M05-Q006`
- **Module / topic:** M05 — MCQ: SemVer and Git SHA
- **Level:** L2 Intermediate
- **Objective tested:** Choose the defensible answer about SemVer and Git SHA.
- **Estimated time:** 5 minutes `[ILLUSTRATIVE]`
- **Question type:** MCQ
- **Question prompt:** A data-service container fails after a change to SemVer and Git SHA. What should be done first?

A. A. Rebuild repeatedly without recording inputs.
B. Collect the exact error, identify the affected digest/platform/configuration, and run a discriminating test.
C. B. Grant broad privileges immediately.
D. C. Roll forward to a mutable tag without checking identity.
- **Model answer:** Collect the exact error, identify the affected digest/platform/configuration, and run a discriminating test.
- **Common wrong answers / failure modes:** Correct answer (B): Collect the exact error, identify the affected digest/platform/configuration, and run a discriminating test.

Distractors:
- A. Rebuild repeatedly without recording inputs. — This creates little diagnostic evidence.
- B. Grant broad privileges immediately. — The symptom may be unrelated and the change increases blast radius.
- C. Roll forward to a mutable tag without checking identity. — The artifact may differ from the tested release.
- **Scoring guidance:** 4 points: 1 for the correct option, 1 for rationale, and 2 for explaining distractors; for strict MCQ scoring, the selected answer earns 1 point.
- **Source/verification note:** Official documentation named in Appendix A; do not infer current defaults without checking the installed version.


### M05-Q007 — MCQ: build metadata

- **ID:** `M05-Q007`
- **Module / topic:** M05 — MCQ: build metadata
- **Level:** L3 Advanced
- **Objective tested:** Choose the defensible answer about build metadata.
- **Estimated time:** 5 minutes `[ILLUSTRATIVE]`
- **Question type:** MCQ
- **Question prompt:** Which statement about build metadata is correct?

A. A. It proves the image is vulnerability-free.
B. B. It makes all builds byte-identical.
C. A control or artifact provides bounded evidence; its scope and limitations must be stated explicitly.
D. C. It replaces rollback and monitoring.
- **Model answer:** A control or artifact provides bounded evidence; its scope and limitations must be stated explicitly.
- **Common wrong answers / failure modes:** Correct answer (C): A control or artifact provides bounded evidence; its scope and limitations must be stated explicitly.

Distractors:
- A. It proves the image is vulnerability-free. — No single control proves absence of all vulnerabilities.
- B. It makes all builds byte-identical. — Reproducibility depends on all material inputs and tooling.
- C. It replaces rollback and monitoring. — Operational controls remain necessary.
- **Scoring guidance:** 4 points: 1 for the correct option, 1 for rationale, and 2 for explaining distractors; for strict MCQ scoring, the selected answer earns 1 point.
- **Source/verification note:** Official documentation named in Appendix A; do not infer current defaults without checking the installed version.


### M05-Q008 — Evidence interpretation: multi-platform image index

- **ID:** `M05-Q008`
- **Module / topic:** M05 — Evidence interpretation: multi-platform image index
- **Level:** L2 Intermediate
- **Objective tested:** Interpret command or log evidence about multi-platform image index without inventing hidden environmental facts.
- **Estimated time:** 7 minutes `[ILLUSTRATIVE]`
- **Question type:** command/output interpretation
- **Question prompt:** A build log for a Python API changes after a source-only edit while the dependency layer reruns. Interpret this evidence in relation to multi-platform image index.

Representative evidence is `[ILLUSTRATIVE]`; no command was executed for this question.
- **Model answer:** The log proves the step reran in this build, not why. Inspect instruction ordering, exact inputs, build args and cache import/export. Move stable dependency manifests before frequently changing source where appropriate, then compare logs.
- **Common wrong answers / failure modes:** Assuming illustrative output was executed; treating one symptom as conclusive root cause; changing security controls before collecting evidence.
- **Scoring guidance:** 5 points: 2 for interpretation, 1 for limits of evidence, 1 for safe test, 1 for mitigation or verification.
- **Source/verification note:** Output is illustrative. Consult official CLI/runtime documentation for current flags and defaults.


### M05-Q009 — Evidence interpretation: digest-based promotion

- **ID:** `M05-Q009`
- **Module / topic:** M05 — Evidence interpretation: digest-based promotion
- **Level:** L3 Advanced
- **Objective tested:** Interpret command or log evidence about digest-based promotion without inventing hidden environmental facts.
- **Estimated time:** 9 minutes `[ILLUSTRATIVE]`
- **Question type:** command/output interpretation
- **Question prompt:** [ILLUSTRATIVE] Runtime logs show a failure involving digest-based promotion. State what the evidence proves, what it does not prove, and the next safe diagnostic step.

Representative evidence is `[ILLUSTRATIVE]`; no command was executed for this question.
- **Model answer:** The log proves a symptom, not a unique root cause. Check the exact error, image digest, platform, effective runtime config, filesystem/identity and dependency evidence. Apply a reversible mitigation and retest the final image.
- **Common wrong answers / failure modes:** Assuming illustrative output was executed; treating one symptom as conclusive root cause; changing security controls before collecting evidence.
- **Scoring guidance:** 5 points: 2 for interpretation, 1 for limits of evidence, 1 for safe test, 1 for mitigation or verification.
- **Source/verification note:** Output is illustrative. Consult official CLI/runtime documentation for current flags and defaults.


### M05-Q010 — Evidence interpretation: rollback identity

- **ID:** `M05-Q010`
- **Module / topic:** M05 — Evidence interpretation: rollback identity
- **Level:** L4 Expert
- **Objective tested:** Interpret command or log evidence about rollback identity without inventing hidden environmental facts.
- **Estimated time:** 11 minutes `[ILLUSTRATIVE]`
- **Question type:** command/output interpretation
- **Question prompt:** A release check reports a different image digest after a configuration change related to rollback identity. What does that prove and what should be compared?

Representative evidence is `[ILLUSTRATIVE]`; no command was executed for this question.
- **Model answer:** The digest difference means the image content identity differs; it does not by itself prove tampering or identify the cause. Compare base digest, resolved dependencies, platform, image config, layer contents, timestamps and provenance; promote only validated content.
- **Common wrong answers / failure modes:** Assuming illustrative output was executed; treating one symptom as conclusive root cause; changing security controls before collecting evidence.
- **Scoring guidance:** 5 points: 2 for interpretation, 1 for limits of evidence, 1 for safe test, 1 for mitigation or verification.
- **Source/verification note:** Output is illustrative. Consult official CLI/runtime documentation for current flags and defaults.


### M05-Q011 — Configuration review 1

- **ID:** `M05-Q011`
- **Module / topic:** M05 — Configuration review 1
- **Level:** L2 Intermediate
- **Objective tested:** Find at least three meaningful defects affecting mutable tags versus digests and propose safe corrections.
- **Estimated time:** 12 minutes `[ILLUSTRATIVE]`
- **Question type:** Dockerfile/config review
- **Question prompt:** Review this design: broad `COPY . .`; mutable base tag; dependency installation after copying all source; a secret supplied using `ARG`; no final-image smoke test. Context: mutable tags versus digests and SemVer and Git SHA.
- **Model answer:** Defects and fixes: (1) broad context copy may include credentials, `.git`, datasets or virtual environments; add `.dockerignore` and selective COPY. (2) mutable base reference weakens input identity; document/pin the chosen base policy. (3) copy dependency manifests before source to improve cache reuse. (4) ARG is not a secret-delivery mechanism; use a supported BuildKit secret mount and verify no logs/layers leak it. (5) add final-image startup/import/health smoke tests.
- **Common wrong answers / failure modes:** Treating formatting as a security defect; recommending disabled TLS, embedded secrets, privileged execution or broad host mounts; fixing symptoms without validation.
- **Scoring guidance:** 8 points: 2 per substantive defect including impact and correction, plus 2 for prioritization and validation. Partial credit for another safe fix.
- **Source/verification note:** [VERIFY AGAINST FINAL UNIT FILE]. Consult Dockerfile, BuildKit, OCI, registry and runtime documentation as relevant.


### M05-Q012 — Configuration review 2

- **ID:** `M05-Q012`
- **Module / topic:** M05 — Configuration review 2
- **Level:** L4 Expert
- **Objective tested:** Find at least three meaningful defects affecting SemVer and Git SHA and propose safe corrections.
- **Estimated time:** 12 minutes `[ILLUSTRATIVE]`
- **Question type:** Dockerfile/config review
- **Question prompt:** Review this release/runtime configuration: image deployed by mutable tag only; no recorded digest; broad registry permissions; no rollback inventory; no evidence from the actual target platform. Context: build metadata and OCI labels.
- **Model answer:** Defects and fixes: (1) mutable tag is not stable release identity; record and deploy approved digest. (2) broad registry permissions increase blast radius; separate pull, push and delete/admin identities. (3) no rollback inventory; retain prior approved digests. (4) no target-platform validation; test each supported architecture. (5) no evidence trail; record source/build metadata, test results and promotion approval.
- **Common wrong answers / failure modes:** Treating formatting as a security defect; recommending disabled TLS, embedded secrets, privileged execution or broad host mounts; fixing symptoms without validation.
- **Scoring guidance:** 8 points: 2 per substantive defect including impact and correction, plus 2 for prioritization and validation. Partial credit for another safe fix.
- **Source/verification note:** [VERIFY AGAINST FINAL UNIT FILE]. Consult Dockerfile, BuildKit, OCI, registry and runtime documentation as relevant.


### M05-Q013 — Incident: build metadata

- **ID:** `M05-Q013`
- **Module / topic:** M05 — Incident: build metadata
- **Level:** L3 Advanced
- **Objective tested:** Diagnose an operational failure involving build metadata and provide safe recovery.
- **Estimated time:** 15 minutes `[ILLUSTRATIVE]`
- **Question type:** incident/troubleshooting
- **Question prompt:** Incident: a production data-service rollout fails after a change involving mutable tags versus digests. Give symptom, scope, hypotheses, discriminating tests, mitigation, root cause, prevention and follow-up evidence.
- **Model answer:** First establish affected release digests, platforms, nodes and time window. Treat causes as hypotheses until logs/tests discriminate them. Preserve healthy workloads and rollback to a known approved digest if impact warrants. Fix the demonstrated cause, add a regression test, and record post-change health and ownership.
- **Common wrong answers / failure modes:** Jumping to root cause; no impact scope; unsafe cleanup; broad privilege; missing rollback or follow-up evidence.
- **Scoring guidance:** 10 points: symptom/scope 2; hypotheses/tests 2; mitigation 2; root cause/prevention 2; follow-up evidence/owner 2.
- **Source/verification note:** Illustrative scenario. Verify implementation-specific operations in the current official runbook.


### M05-Q014 — Incident: OCI labels

- **ID:** `M05-Q014`
- **Module / topic:** M05 — Incident: OCI labels
- **Level:** L4 Expert
- **Objective tested:** Diagnose an operational failure involving OCI labels and provide safe recovery.
- **Estimated time:** 15 minutes `[ILLUSTRATIVE]`
- **Question type:** incident/troubleshooting
- **Question prompt:** Incident: the team proposes a broad cleanup/security bypass to resolve an issue involving OCI labels. As incident lead, define a safer response and recovery plan.
- **Model answer:** Do not perform broad deletion or disable protections without evidence. Scope the impact, preserve artifacts/logs, inspect the actual failure and current policy, choose a reversible mitigation, and document approval. Verify recovery with pull/startup/health tests and add a runbook or guardrail.
- **Common wrong answers / failure modes:** Jumping to root cause; no impact scope; unsafe cleanup; broad privilege; missing rollback or follow-up evidence.
- **Scoring guidance:** 10 points: symptom/scope 2; hypotheses/tests 2; mitigation 2; root cause/prevention 2; follow-up evidence/owner 2.
- **Source/verification note:** Illustrative scenario. Verify implementation-specific operations in the current official runbook.


### M05-Q015 — Whiteboard design review

- **ID:** `M05-Q015`
- **Module / topic:** M05 — Whiteboard design review
- **Level:** L4 Expert
- **Objective tested:** Design and defend a production approach to image tagging, versioning, and immutability.
- **Estimated time:** 25 minutes `[ILLUSTRATIVE]`
- **Question type:** design
- **Question prompt:** Design release identity and promotion across dev, staging and production. Include tags, digests, source metadata, multi-platform behavior, rollback and drift detection. Defend digest promotion against rebuild-per-environment.
- **Model answer:** A strong answer states assumptions, provides a traceable design, names failure modes, defines acceptance evidence and defends the trade-off. Multiple architectures can earn full credit if constraints are explicit.
- **Common wrong answers / failure modes:** Selecting a tool without assumptions; claiming one universally correct answer; ignoring recovery, trust boundaries or measurable acceptance criteria.
- **Scoring guidance:** 10 points: tag/digest/source distinction 2; immutable promotion 2; metadata/evidence 2; platform identity/testing 2; rollback/drift and alternative defense 2.
- **Source/verification note:** [VERIFY AGAINST FINAL UNIT FILE]. Version-sensitive implementation claims require current official documentation.



**Module tally:** 15 questions. IDs `M05-Q001` through `M05-Q015`.


## Module 6 — Container registries, mirrors, and pull-through caches

**Coverage tally:** 4 short answer; 3 MCQ; 3 command/output interpretation; 2 Dockerfile/config review; 2 incident/troubleshooting. Modules 3–8 add one design question each. Levels L1–L4 are represented.

### M06-Q001 — OCI Distribution concepts

- **ID:** `M06-Q001`
- **Module / topic:** M06 — OCI Distribution concepts
- **Level:** L1 Beginner
- **Objective tested:** Explain and apply OCI Distribution concepts in the context of container registries, mirrors, and pull-through caches.
- **Estimated time:** 7 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** Define and distinguish OCI Distribution concepts.
- **Model answer:** Explain the core terms, what each identifies or controls, and one operational consequence. Do not infer that one control guarantees security or reproducibility.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M06-Q002 — local Distribution registry

- **ID:** `M06-Q002`
- **Module / topic:** M06 — local Distribution registry
- **Level:** L1 Beginner
- **Objective tested:** Explain and apply local Distribution registry in the context of container registries, mirrors, and pull-through caches.
- **Estimated time:** 9 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** Explain how local Distribution registry affects a real data-service image.
- **Model answer:** Describe the mechanism, identify the inputs or runtime conditions involved, and explain how you would verify the behavior from build/runtime evidence.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M06-Q003 — authentication versus TLS

- **ID:** `M06-Q003`
- **Module / topic:** M06 — authentication versus TLS
- **Level:** L2 Intermediate
- **Objective tested:** Explain and apply authentication versus TLS in the context of container registries, mirrors, and pull-through caches.
- **Estimated time:** 11 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** Apply authentication versus TLS to a Python FastAPI or batch ETL container.
- **Model answer:** State the design choice, the relevant compatibility/security/reliability trade-off, and a test in the final image. A builder-stage success alone does not prove runtime success.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M06-Q004 — registry mirrors

- **ID:** `M06-Q004`
- **Module / topic:** M06 — registry mirrors
- **Level:** L3 Advanced
- **Objective tested:** Explain and apply registry mirrors in the context of container registries, mirrors, and pull-through caches.
- **Estimated time:** 13 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** At L3, evaluate registry mirrors under a production constraint.
- **Model answer:** Compare at least two options, name the assumptions and failure modes, and choose based on evidence. Record version-sensitive behavior for official-document verification.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M06-Q005 — MCQ: OCI Distribution concepts

- **ID:** `M06-Q005`
- **Module / topic:** M06 — MCQ: OCI Distribution concepts
- **Level:** L1 Beginner
- **Objective tested:** Choose the defensible answer about OCI Distribution concepts.
- **Estimated time:** 5 minutes `[ILLUSTRATIVE]`
- **Question type:** MCQ
- **Question prompt:** Which is the most defensible approach to OCI Distribution concepts?

A. Choose a documented approach, verify it against the actual build/runtime context, and retain evidence.
B. A. Assume the default is secure.
C. B. Disable the control if it causes friction.
D. C. Treat a successful build as proof of production safety.
- **Model answer:** Choose a documented approach, verify it against the actual build/runtime context, and retain evidence.
- **Common wrong answers / failure modes:** Correct answer (A): Choose a documented approach, verify it against the actual build/runtime context, and retain evidence.

Distractors:
- A. Assume the default is secure. — Defaults can vary and may not meet the workload's needs.
- B. Disable the control if it causes friction. — This removes protection without diagnosing the failure.
- C. Treat a successful build as proof of production safety. — Build success does not prove runtime compatibility or security.
- **Scoring guidance:** 4 points: 1 for the correct option, 1 for rationale, and 2 for explaining distractors; for strict MCQ scoring, the selected answer earns 1 point.
- **Source/verification note:** Official documentation named in Appendix A; do not infer current defaults without checking the installed version.


### M06-Q006 — MCQ: local Distribution registry

- **ID:** `M06-Q006`
- **Module / topic:** M06 — MCQ: local Distribution registry
- **Level:** L2 Intermediate
- **Objective tested:** Choose the defensible answer about local Distribution registry.
- **Estimated time:** 5 minutes `[ILLUSTRATIVE]`
- **Question type:** MCQ
- **Question prompt:** A data-service container fails after a change to local Distribution registry. What should be done first?

A. A. Rebuild repeatedly without recording inputs.
B. Collect the exact error, identify the affected digest/platform/configuration, and run a discriminating test.
C. B. Grant broad privileges immediately.
D. C. Roll forward to a mutable tag without checking identity.
- **Model answer:** Collect the exact error, identify the affected digest/platform/configuration, and run a discriminating test.
- **Common wrong answers / failure modes:** Correct answer (B): Collect the exact error, identify the affected digest/platform/configuration, and run a discriminating test.

Distractors:
- A. Rebuild repeatedly without recording inputs. — This creates little diagnostic evidence.
- B. Grant broad privileges immediately. — The symptom may be unrelated and the change increases blast radius.
- C. Roll forward to a mutable tag without checking identity. — The artifact may differ from the tested release.
- **Scoring guidance:** 4 points: 1 for the correct option, 1 for rationale, and 2 for explaining distractors; for strict MCQ scoring, the selected answer earns 1 point.
- **Source/verification note:** Official documentation named in Appendix A; do not infer current defaults without checking the installed version.


### M06-Q007 — MCQ: authentication versus TLS

- **ID:** `M06-Q007`
- **Module / topic:** M06 — MCQ: authentication versus TLS
- **Level:** L3 Advanced
- **Objective tested:** Choose the defensible answer about authentication versus TLS.
- **Estimated time:** 5 minutes `[ILLUSTRATIVE]`
- **Question type:** MCQ
- **Question prompt:** Which statement about authentication versus TLS is correct?

A. A. It proves the image is vulnerability-free.
B. B. It makes all builds byte-identical.
C. A control or artifact provides bounded evidence; its scope and limitations must be stated explicitly.
D. C. It replaces rollback and monitoring.
- **Model answer:** A control or artifact provides bounded evidence; its scope and limitations must be stated explicitly.
- **Common wrong answers / failure modes:** Correct answer (C): A control or artifact provides bounded evidence; its scope and limitations must be stated explicitly.

Distractors:
- A. It proves the image is vulnerability-free. — No single control proves absence of all vulnerabilities.
- B. It makes all builds byte-identical. — Reproducibility depends on all material inputs and tooling.
- C. It replaces rollback and monitoring. — Operational controls remain necessary.
- **Scoring guidance:** 4 points: 1 for the correct option, 1 for rationale, and 2 for explaining distractors; for strict MCQ scoring, the selected answer earns 1 point.
- **Source/verification note:** Official documentation named in Appendix A; do not infer current defaults without checking the installed version.


### M06-Q008 — Evidence interpretation: pull-through cache hit/miss

- **ID:** `M06-Q008`
- **Module / topic:** M06 — Evidence interpretation: pull-through cache hit/miss
- **Level:** L2 Intermediate
- **Objective tested:** Interpret command or log evidence about pull-through cache hit/miss without inventing hidden environmental facts.
- **Estimated time:** 7 minutes `[ILLUSTRATIVE]`
- **Question type:** command/output interpretation
- **Question prompt:** A build log for a Python API changes after a source-only edit while the dependency layer reruns. Interpret this evidence in relation to pull-through cache hit/miss.

Representative evidence is `[ILLUSTRATIVE]`; no command was executed for this question.
- **Model answer:** The log proves the step reran in this build, not why. Inspect instruction ordering, exact inputs, build args and cache import/export. Move stable dependency manifests before frequently changing source where appropriate, then compare logs.
- **Common wrong answers / failure modes:** Assuming illustrative output was executed; treating one symptom as conclusive root cause; changing security controls before collecting evidence.
- **Scoring guidance:** 5 points: 2 for interpretation, 1 for limits of evidence, 1 for safe test, 1 for mitigation or verification.
- **Source/verification note:** Output is illustrative. Consult official CLI/runtime documentation for current flags and defaults.


### M06-Q009 — Evidence interpretation: Docker versus containerd config

- **ID:** `M06-Q009`
- **Module / topic:** M06 — Evidence interpretation: Docker versus containerd config
- **Level:** L3 Advanced
- **Objective tested:** Interpret command or log evidence about Docker versus containerd config without inventing hidden environmental facts.
- **Estimated time:** 9 minutes `[ILLUSTRATIVE]`
- **Question type:** command/output interpretation
- **Question prompt:** [ILLUSTRATIVE] Runtime logs show a failure involving Docker versus containerd config. State what the evidence proves, what it does not prove, and the next safe diagnostic step.

Representative evidence is `[ILLUSTRATIVE]`; no command was executed for this question.
- **Model answer:** The log proves a symptom, not a unique root cause. Check the exact error, image digest, platform, effective runtime config, filesystem/identity and dependency evidence. Apply a reversible mitigation and retest the final image.
- **Common wrong answers / failure modes:** Assuming illustrative output was executed; treating one symptom as conclusive root cause; changing security controls before collecting evidence.
- **Scoring guidance:** 5 points: 2 for interpretation, 1 for limits of evidence, 1 for safe test, 1 for mitigation or verification.
- **Source/verification note:** Output is illustrative. Consult official CLI/runtime documentation for current flags and defaults.


### M06-Q010 — Evidence interpretation: hosted registry comparison

- **ID:** `M06-Q010`
- **Module / topic:** M06 — Evidence interpretation: hosted registry comparison
- **Level:** L4 Expert
- **Objective tested:** Interpret command or log evidence about hosted registry comparison without inventing hidden environmental facts.
- **Estimated time:** 11 minutes `[ILLUSTRATIVE]`
- **Question type:** command/output interpretation
- **Question prompt:** A release check reports a different image digest after a configuration change related to hosted registry comparison. What does that prove and what should be compared?

Representative evidence is `[ILLUSTRATIVE]`; no command was executed for this question.
- **Model answer:** The digest difference means the image content identity differs; it does not by itself prove tampering or identify the cause. Compare base digest, resolved dependencies, platform, image config, layer contents, timestamps and provenance; promote only validated content.
- **Common wrong answers / failure modes:** Assuming illustrative output was executed; treating one symptom as conclusive root cause; changing security controls before collecting evidence.
- **Scoring guidance:** 5 points: 2 for interpretation, 1 for limits of evidence, 1 for safe test, 1 for mitigation or verification.
- **Source/verification note:** Output is illustrative. Consult official CLI/runtime documentation for current flags and defaults.


### M06-Q011 — Configuration review 1

- **ID:** `M06-Q011`
- **Module / topic:** M06 — Configuration review 1
- **Level:** L2 Intermediate
- **Objective tested:** Find at least three meaningful defects affecting OCI Distribution concepts and propose safe corrections.
- **Estimated time:** 12 minutes `[ILLUSTRATIVE]`
- **Question type:** Dockerfile/config review
- **Question prompt:** Review this design: broad `COPY . .`; mutable base tag; dependency installation after copying all source; a secret supplied using `ARG`; no final-image smoke test. Context: OCI Distribution concepts and local Distribution registry.
- **Model answer:** Defects and fixes: (1) broad context copy may include credentials, `.git`, datasets or virtual environments; add `.dockerignore` and selective COPY. (2) mutable base reference weakens input identity; document/pin the chosen base policy. (3) copy dependency manifests before source to improve cache reuse. (4) ARG is not a secret-delivery mechanism; use a supported BuildKit secret mount and verify no logs/layers leak it. (5) add final-image startup/import/health smoke tests.
- **Common wrong answers / failure modes:** Treating formatting as a security defect; recommending disabled TLS, embedded secrets, privileged execution or broad host mounts; fixing symptoms without validation.
- **Scoring guidance:** 8 points: 2 per substantive defect including impact and correction, plus 2 for prioritization and validation. Partial credit for another safe fix.
- **Source/verification note:** [VERIFY AGAINST FINAL UNIT FILE]. Consult Dockerfile, BuildKit, OCI, registry and runtime documentation as relevant.


### M06-Q012 — Configuration review 2

- **ID:** `M06-Q012`
- **Module / topic:** M06 — Configuration review 2
- **Level:** L4 Expert
- **Objective tested:** Find at least three meaningful defects affecting local Distribution registry and propose safe corrections.
- **Estimated time:** 12 minutes `[ILLUSTRATIVE]`
- **Question type:** Dockerfile/config review
- **Question prompt:** Review this release/runtime configuration: image deployed by mutable tag only; no recorded digest; broad registry permissions; no rollback inventory; no evidence from the actual target platform. Context: authentication versus TLS and registry mirrors.
- **Model answer:** Defects and fixes: (1) mutable tag is not stable release identity; record and deploy approved digest. (2) broad registry permissions increase blast radius; separate pull, push and delete/admin identities. (3) no rollback inventory; retain prior approved digests. (4) no target-platform validation; test each supported architecture. (5) no evidence trail; record source/build metadata, test results and promotion approval.
- **Common wrong answers / failure modes:** Treating formatting as a security defect; recommending disabled TLS, embedded secrets, privileged execution or broad host mounts; fixing symptoms without validation.
- **Scoring guidance:** 8 points: 2 per substantive defect including impact and correction, plus 2 for prioritization and validation. Partial credit for another safe fix.
- **Source/verification note:** [VERIFY AGAINST FINAL UNIT FILE]. Consult Dockerfile, BuildKit, OCI, registry and runtime documentation as relevant.


### M06-Q013 — Incident: authentication versus TLS

- **ID:** `M06-Q013`
- **Module / topic:** M06 — Incident: authentication versus TLS
- **Level:** L3 Advanced
- **Objective tested:** Diagnose an operational failure involving authentication versus TLS and provide safe recovery.
- **Estimated time:** 15 minutes `[ILLUSTRATIVE]`
- **Question type:** incident/troubleshooting
- **Question prompt:** Incident: a production data-service rollout fails after a change involving OCI Distribution concepts. Give symptom, scope, hypotheses, discriminating tests, mitigation, root cause, prevention and follow-up evidence.
- **Model answer:** First establish affected release digests, platforms, nodes and time window. Treat causes as hypotheses until logs/tests discriminate them. Preserve healthy workloads and rollback to a known approved digest if impact warrants. Fix the demonstrated cause, add a regression test, and record post-change health and ownership.
- **Common wrong answers / failure modes:** Jumping to root cause; no impact scope; unsafe cleanup; broad privilege; missing rollback or follow-up evidence.
- **Scoring guidance:** 10 points: symptom/scope 2; hypotheses/tests 2; mitigation 2; root cause/prevention 2; follow-up evidence/owner 2.
- **Source/verification note:** Illustrative scenario. Verify implementation-specific operations in the current official runbook.


### M06-Q014 — Incident: registry mirrors

- **ID:** `M06-Q014`
- **Module / topic:** M06 — Incident: registry mirrors
- **Level:** L4 Expert
- **Objective tested:** Diagnose an operational failure involving registry mirrors and provide safe recovery.
- **Estimated time:** 15 minutes `[ILLUSTRATIVE]`
- **Question type:** incident/troubleshooting
- **Question prompt:** Incident: the team proposes a broad cleanup/security bypass to resolve an issue involving registry mirrors. As incident lead, define a safer response and recovery plan.
- **Model answer:** Do not perform broad deletion or disable protections without evidence. Scope the impact, preserve artifacts/logs, inspect the actual failure and current policy, choose a reversible mitigation, and document approval. Verify recovery with pull/startup/health tests and add a runbook or guardrail.
- **Common wrong answers / failure modes:** Jumping to root cause; no impact scope; unsafe cleanup; broad privilege; missing rollback or follow-up evidence.
- **Scoring guidance:** 10 points: symptom/scope 2; hypotheses/tests 2; mitigation 2; root cause/prevention 2; follow-up evidence/owner 2.
- **Source/verification note:** Illustrative scenario. Verify implementation-specific operations in the current official runbook.


### M06-Q015 — Whiteboard design review

- **ID:** `M06-Q015`
- **Module / topic:** M06 — Whiteboard design review
- **Level:** L4 Expert
- **Objective tested:** Design and defend a production approach to container registries, mirrors, and pull-through caches.
- **Estimated time:** 25 minutes `[ILLUSTRATIVE]`
- **Question type:** design
- **Question prompt:** Design a zero-budget local and CI registry strategy with a local Distribution registry and optional pull-through cache. Include TLS/auth, capacity, miss/outage behavior and recovery; compare with a durable private registry.
- **Model answer:** A strong answer states assumptions, provides a traceable design, names failure modes, defines acceptance evidence and defends the trade-off. Multiple architectures can earn full credit if constraints are explicit.
- **Common wrong answers / failure modes:** Selecting a tool without assumptions; claiming one universally correct answer; ignoring recovery, trust boundaries or measurable acceptance criteria.
- **Scoring guidance:** 10 points: registry/cache distinction 2; auth/TLS/client config 2; outage/capacity 2; safe local design/limits 2; justified alternative trade-off 2.
- **Source/verification note:** [VERIFY AGAINST FINAL UNIT FILE]. Version-sensitive implementation claims require current official documentation.



**Module tally:** 15 questions. IDs `M06-Q001` through `M06-Q015`.


## Module 7 — Registry retention, garbage collection, and access control

**Coverage tally:** 4 short answer; 3 MCQ; 3 command/output interpretation; 2 Dockerfile/config review; 2 incident/troubleshooting. Modules 3–8 add one design question each. Levels L1–L4 are represented.

### M07-Q001 — retention policy

- **ID:** `M07-Q001`
- **Module / topic:** M07 — retention policy
- **Level:** L1 Beginner
- **Objective tested:** Explain and apply retention policy in the context of registry retention, garbage collection, and access control.
- **Estimated time:** 7 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** Define and distinguish retention policy.
- **Model answer:** Explain the core terms, what each identifies or controls, and one operational consequence. Do not infer that one control guarantees security or reproducibility.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M07-Q002 — tag deletion versus blob reachability

- **ID:** `M07-Q002`
- **Module / topic:** M07 — tag deletion versus blob reachability
- **Level:** L1 Beginner
- **Objective tested:** Explain and apply tag deletion versus blob reachability in the context of registry retention, garbage collection, and access control.
- **Estimated time:** 9 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** Explain how tag deletion versus blob reachability affects a real data-service image.
- **Model answer:** Describe the mechanism, identify the inputs or runtime conditions involved, and explain how you would verify the behavior from build/runtime evidence.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M07-Q003 — garbage-collection sequencing

- **ID:** `M07-Q003`
- **Module / topic:** M07 — garbage-collection sequencing
- **Level:** L2 Intermediate
- **Objective tested:** Explain and apply garbage-collection sequencing in the context of registry retention, garbage collection, and access control.
- **Estimated time:** 11 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** Apply garbage-collection sequencing to a Python FastAPI or batch ETL container.
- **Model answer:** State the design choice, the relevant compatibility/security/reliability trade-off, and a test in the final image. A builder-stage success alone does not prove runtime success.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M07-Q004 — in-use digest protection

- **ID:** `M07-Q004`
- **Module / topic:** M07 — in-use digest protection
- **Level:** L3 Advanced
- **Objective tested:** Explain and apply in-use digest protection in the context of registry retention, garbage collection, and access control.
- **Estimated time:** 13 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** At L3, evaluate in-use digest protection under a production constraint.
- **Model answer:** Compare at least two options, name the assumptions and failure modes, and choose based on evidence. Record version-sensitive behavior for official-document verification.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M07-Q005 — MCQ: retention policy

- **ID:** `M07-Q005`
- **Module / topic:** M07 — MCQ: retention policy
- **Level:** L1 Beginner
- **Objective tested:** Choose the defensible answer about retention policy.
- **Estimated time:** 5 minutes `[ILLUSTRATIVE]`
- **Question type:** MCQ
- **Question prompt:** Which is the most defensible approach to retention policy?

A. Choose a documented approach, verify it against the actual build/runtime context, and retain evidence.
B. A. Assume the default is secure.
C. B. Disable the control if it causes friction.
D. C. Treat a successful build as proof of production safety.
- **Model answer:** Choose a documented approach, verify it against the actual build/runtime context, and retain evidence.
- **Common wrong answers / failure modes:** Correct answer (A): Choose a documented approach, verify it against the actual build/runtime context, and retain evidence.

Distractors:
- A. Assume the default is secure. — Defaults can vary and may not meet the workload's needs.
- B. Disable the control if it causes friction. — This removes protection without diagnosing the failure.
- C. Treat a successful build as proof of production safety. — Build success does not prove runtime compatibility or security.
- **Scoring guidance:** 4 points: 1 for the correct option, 1 for rationale, and 2 for explaining distractors; for strict MCQ scoring, the selected answer earns 1 point.
- **Source/verification note:** Official documentation named in Appendix A; do not infer current defaults without checking the installed version.


### M07-Q006 — MCQ: tag deletion versus blob reachability

- **ID:** `M07-Q006`
- **Module / topic:** M07 — MCQ: tag deletion versus blob reachability
- **Level:** L2 Intermediate
- **Objective tested:** Choose the defensible answer about tag deletion versus blob reachability.
- **Estimated time:** 5 minutes `[ILLUSTRATIVE]`
- **Question type:** MCQ
- **Question prompt:** A data-service container fails after a change to tag deletion versus blob reachability. What should be done first?

A. A. Rebuild repeatedly without recording inputs.
B. Collect the exact error, identify the affected digest/platform/configuration, and run a discriminating test.
C. B. Grant broad privileges immediately.
D. C. Roll forward to a mutable tag without checking identity.
- **Model answer:** Collect the exact error, identify the affected digest/platform/configuration, and run a discriminating test.
- **Common wrong answers / failure modes:** Correct answer (B): Collect the exact error, identify the affected digest/platform/configuration, and run a discriminating test.

Distractors:
- A. Rebuild repeatedly without recording inputs. — This creates little diagnostic evidence.
- B. Grant broad privileges immediately. — The symptom may be unrelated and the change increases blast radius.
- C. Roll forward to a mutable tag without checking identity. — The artifact may differ from the tested release.
- **Scoring guidance:** 4 points: 1 for the correct option, 1 for rationale, and 2 for explaining distractors; for strict MCQ scoring, the selected answer earns 1 point.
- **Source/verification note:** Official documentation named in Appendix A; do not infer current defaults without checking the installed version.


### M07-Q007 — MCQ: garbage-collection sequencing

- **ID:** `M07-Q007`
- **Module / topic:** M07 — MCQ: garbage-collection sequencing
- **Level:** L3 Advanced
- **Objective tested:** Choose the defensible answer about garbage-collection sequencing.
- **Estimated time:** 5 minutes `[ILLUSTRATIVE]`
- **Question type:** MCQ
- **Question prompt:** Which statement about garbage-collection sequencing is correct?

A. A. It proves the image is vulnerability-free.
B. B. It makes all builds byte-identical.
C. A control or artifact provides bounded evidence; its scope and limitations must be stated explicitly.
D. C. It replaces rollback and monitoring.
- **Model answer:** A control or artifact provides bounded evidence; its scope and limitations must be stated explicitly.
- **Common wrong answers / failure modes:** Correct answer (C): A control or artifact provides bounded evidence; its scope and limitations must be stated explicitly.

Distractors:
- A. It proves the image is vulnerability-free. — No single control proves absence of all vulnerabilities.
- B. It makes all builds byte-identical. — Reproducibility depends on all material inputs and tooling.
- C. It replaces rollback and monitoring. — Operational controls remain necessary.
- **Scoring guidance:** 4 points: 1 for the correct option, 1 for rationale, and 2 for explaining distractors; for strict MCQ scoring, the selected answer earns 1 point.
- **Source/verification note:** Official documentation named in Appendix A; do not infer current defaults without checking the installed version.


### M07-Q008 — Evidence interpretation: dry-run plans

- **ID:** `M07-Q008`
- **Module / topic:** M07 — Evidence interpretation: dry-run plans
- **Level:** L2 Intermediate
- **Objective tested:** Interpret command or log evidence about dry-run plans without inventing hidden environmental facts.
- **Estimated time:** 7 minutes `[ILLUSTRATIVE]`
- **Question type:** command/output interpretation
- **Question prompt:** A build log for a Python API changes after a source-only edit while the dependency layer reruns. Interpret this evidence in relation to dry-run plans.

Representative evidence is `[ILLUSTRATIVE]`; no command was executed for this question.
- **Model answer:** The log proves the step reran in this build, not why. Inspect instruction ordering, exact inputs, build args and cache import/export. Move stable dependency manifests before frequently changing source where appropriate, then compare logs.
- **Common wrong answers / failure modes:** Assuming illustrative output was executed; treating one symptom as conclusive root cause; changing security controls before collecting evidence.
- **Scoring guidance:** 5 points: 2 for interpretation, 1 for limits of evidence, 1 for safe test, 1 for mitigation or verification.
- **Source/verification note:** Output is illustrative. Consult official CLI/runtime documentation for current flags and defaults.


### M07-Q009 — Evidence interpretation: least privilege

- **ID:** `M07-Q009`
- **Module / topic:** M07 — Evidence interpretation: least privilege
- **Level:** L3 Advanced
- **Objective tested:** Interpret command or log evidence about least privilege without inventing hidden environmental facts.
- **Estimated time:** 9 minutes `[ILLUSTRATIVE]`
- **Question type:** command/output interpretation
- **Question prompt:** [ILLUSTRATIVE] Runtime logs show a failure involving least privilege. State what the evidence proves, what it does not prove, and the next safe diagnostic step.

Representative evidence is `[ILLUSTRATIVE]`; no command was executed for this question.
- **Model answer:** The log proves a symptom, not a unique root cause. Check the exact error, image digest, platform, effective runtime config, filesystem/identity and dependency evidence. Apply a reversible mitigation and retest the final image.
- **Common wrong answers / failure modes:** Assuming illustrative output was executed; treating one symptom as conclusive root cause; changing security controls before collecting evidence.
- **Scoring guidance:** 5 points: 2 for interpretation, 1 for limits of evidence, 1 for safe test, 1 for mitigation or verification.
- **Source/verification note:** Output is illustrative. Consult official CLI/runtime documentation for current flags and defaults.


### M07-Q010 — Evidence interpretation: push/pull/delete separation

- **ID:** `M07-Q010`
- **Module / topic:** M07 — Evidence interpretation: push/pull/delete separation
- **Level:** L4 Expert
- **Objective tested:** Interpret command or log evidence about push/pull/delete separation without inventing hidden environmental facts.
- **Estimated time:** 11 minutes `[ILLUSTRATIVE]`
- **Question type:** command/output interpretation
- **Question prompt:** A release check reports a different image digest after a configuration change related to push/pull/delete separation. What does that prove and what should be compared?

Representative evidence is `[ILLUSTRATIVE]`; no command was executed for this question.
- **Model answer:** The digest difference means the image content identity differs; it does not by itself prove tampering or identify the cause. Compare base digest, resolved dependencies, platform, image config, layer contents, timestamps and provenance; promote only validated content.
- **Common wrong answers / failure modes:** Assuming illustrative output was executed; treating one symptom as conclusive root cause; changing security controls before collecting evidence.
- **Scoring guidance:** 5 points: 2 for interpretation, 1 for limits of evidence, 1 for safe test, 1 for mitigation or verification.
- **Source/verification note:** Output is illustrative. Consult official CLI/runtime documentation for current flags and defaults.


### M07-Q011 — Configuration review 1

- **ID:** `M07-Q011`
- **Module / topic:** M07 — Configuration review 1
- **Level:** L2 Intermediate
- **Objective tested:** Find at least three meaningful defects affecting retention policy and propose safe corrections.
- **Estimated time:** 12 minutes `[ILLUSTRATIVE]`
- **Question type:** Dockerfile/config review
- **Question prompt:** Review this design: broad `COPY . .`; mutable base tag; dependency installation after copying all source; a secret supplied using `ARG`; no final-image smoke test. Context: retention policy and tag deletion versus blob reachability.
- **Model answer:** Defects and fixes: (1) broad context copy may include credentials, `.git`, datasets or virtual environments; add `.dockerignore` and selective COPY. (2) mutable base reference weakens input identity; document/pin the chosen base policy. (3) copy dependency manifests before source to improve cache reuse. (4) ARG is not a secret-delivery mechanism; use a supported BuildKit secret mount and verify no logs/layers leak it. (5) add final-image startup/import/health smoke tests.
- **Common wrong answers / failure modes:** Treating formatting as a security defect; recommending disabled TLS, embedded secrets, privileged execution or broad host mounts; fixing symptoms without validation.
- **Scoring guidance:** 8 points: 2 per substantive defect including impact and correction, plus 2 for prioritization and validation. Partial credit for another safe fix.
- **Source/verification note:** [VERIFY AGAINST FINAL UNIT FILE]. Consult Dockerfile, BuildKit, OCI, registry and runtime documentation as relevant.


### M07-Q012 — Configuration review 2

- **ID:** `M07-Q012`
- **Module / topic:** M07 — Configuration review 2
- **Level:** L4 Expert
- **Objective tested:** Find at least three meaningful defects affecting tag deletion versus blob reachability and propose safe corrections.
- **Estimated time:** 12 minutes `[ILLUSTRATIVE]`
- **Question type:** Dockerfile/config review
- **Question prompt:** Review this release/runtime configuration: image deployed by mutable tag only; no recorded digest; broad registry permissions; no rollback inventory; no evidence from the actual target platform. Context: garbage-collection sequencing and in-use digest protection.
- **Model answer:** Defects and fixes: (1) mutable tag is not stable release identity; record and deploy approved digest. (2) broad registry permissions increase blast radius; separate pull, push and delete/admin identities. (3) no rollback inventory; retain prior approved digests. (4) no target-platform validation; test each supported architecture. (5) no evidence trail; record source/build metadata, test results and promotion approval.
- **Common wrong answers / failure modes:** Treating formatting as a security defect; recommending disabled TLS, embedded secrets, privileged execution or broad host mounts; fixing symptoms without validation.
- **Scoring guidance:** 8 points: 2 per substantive defect including impact and correction, plus 2 for prioritization and validation. Partial credit for another safe fix.
- **Source/verification note:** [VERIFY AGAINST FINAL UNIT FILE]. Consult Dockerfile, BuildKit, OCI, registry and runtime documentation as relevant.


### M07-Q013 — Incident: garbage-collection sequencing

- **ID:** `M07-Q013`
- **Module / topic:** M07 — Incident: garbage-collection sequencing
- **Level:** L3 Advanced
- **Objective tested:** Diagnose an operational failure involving garbage-collection sequencing and provide safe recovery.
- **Estimated time:** 15 minutes `[ILLUSTRATIVE]`
- **Question type:** incident/troubleshooting
- **Question prompt:** Incident: a production data-service rollout fails after a change involving retention policy. Give symptom, scope, hypotheses, discriminating tests, mitigation, root cause, prevention and follow-up evidence.
- **Model answer:** First establish affected release digests, platforms, nodes and time window. Treat causes as hypotheses until logs/tests discriminate them. Preserve healthy workloads and rollback to a known approved digest if impact warrants. Fix the demonstrated cause, add a regression test, and record post-change health and ownership.
- **Common wrong answers / failure modes:** Jumping to root cause; no impact scope; unsafe cleanup; broad privilege; missing rollback or follow-up evidence.
- **Scoring guidance:** 10 points: symptom/scope 2; hypotheses/tests 2; mitigation 2; root cause/prevention 2; follow-up evidence/owner 2.
- **Source/verification note:** Illustrative scenario. Verify implementation-specific operations in the current official runbook.


### M07-Q014 — Incident: in-use digest protection

- **ID:** `M07-Q014`
- **Module / topic:** M07 — Incident: in-use digest protection
- **Level:** L4 Expert
- **Objective tested:** Diagnose an operational failure involving in-use digest protection and provide safe recovery.
- **Estimated time:** 15 minutes `[ILLUSTRATIVE]`
- **Question type:** incident/troubleshooting
- **Question prompt:** Incident: the team proposes a broad cleanup/security bypass to resolve an issue involving in-use digest protection. As incident lead, define a safer response and recovery plan.
- **Model answer:** Do not perform broad deletion or disable protections without evidence. Scope the impact, preserve artifacts/logs, inspect the actual failure and current policy, choose a reversible mitigation, and document approval. Verify recovery with pull/startup/health tests and add a runbook or guardrail.
- **Common wrong answers / failure modes:** Jumping to root cause; no impact scope; unsafe cleanup; broad privilege; missing rollback or follow-up evidence.
- **Scoring guidance:** 10 points: symptom/scope 2; hypotheses/tests 2; mitigation 2; root cause/prevention 2; follow-up evidence/owner 2.
- **Source/verification note:** Illustrative scenario. Verify implementation-specific operations in the current official runbook.


### M07-Q015 — Whiteboard design review

- **ID:** `M07-Q015`
- **Module / topic:** M07 — Whiteboard design review
- **Level:** L4 Expert
- **Objective tested:** Design and defend a production approach to registry retention, garbage collection, and access control.
- **Estimated time:** 25 minutes `[ILLUSTRATIVE]`
- **Question type:** design
- **Question prompt:** Design retention, quarantine and garbage collection for inference API and PySpark images. Include digest inventory, identities, audit, dry-run, restore evidence and retention-window trade-off.
- **Model answer:** A strong answer states assumptions, provides a traceable design, names failure modes, defines acceptance evidence and defends the trade-off. Multiple architectures can earn full credit if constraints are explicit.
- **Common wrong answers / failure modes:** Selecting a tool without assumptions; claiming one universally correct answer; ignoring recovery, trust boundaries or measurable acceptance criteria.
- **Scoring guidance:** 10 points: digest inventory 2; least privilege 2; safe GC sequence 2; quarantine/audit 2; restore/rollback evidence and justified retention 2.
- **Source/verification note:** [VERIFY AGAINST FINAL UNIT FILE]. Version-sensitive implementation claims require current official documentation.



**Module tally:** 15 questions. IDs `M07-Q001` through `M07-Q015`.


## Module 8 — Non-root containers and runtime defaults

**Coverage tally:** 4 short answer; 3 MCQ; 3 command/output interpretation; 2 Dockerfile/config review; 2 incident/troubleshooting. Modules 3–8 add one design question each. Levels L1–L4 are represented.

### M08-Q001 — UID/GID and root-in-container risk

- **ID:** `M08-Q001`
- **Module / topic:** M08 — UID/GID and root-in-container risk
- **Level:** L1 Beginner
- **Objective tested:** Explain and apply UID/GID and root-in-container risk in the context of non-root containers and runtime defaults.
- **Estimated time:** 7 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** Define and distinguish UID/GID and root-in-container risk.
- **Model answer:** Explain the core terms, what each identifies or controls, and one operational consequence. Do not infer that one control guarantees security or reproducibility.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M08-Q002 — numeric USER

- **ID:** `M08-Q002`
- **Module / topic:** M08 — numeric USER
- **Level:** L1 Beginner
- **Objective tested:** Explain and apply numeric USER in the context of non-root containers and runtime defaults.
- **Estimated time:** 9 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** Explain how numeric USER affects a real data-service image.
- **Model answer:** Describe the mechanism, identify the inputs or runtime conditions involved, and explain how you would verify the behavior from build/runtime evidence.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M08-Q003 — COPY --chown

- **ID:** `M08-Q003`
- **Module / topic:** M08 — COPY --chown
- **Level:** L2 Intermediate
- **Objective tested:** Explain and apply COPY --chown in the context of non-root containers and runtime defaults.
- **Estimated time:** 11 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** Apply COPY --chown to a Python FastAPI or batch ETL container.
- **Model answer:** State the design choice, the relevant compatibility/security/reliability trade-off, and a test in the final image. A builder-stage success alone does not prove runtime success.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M08-Q004 — read-only root filesystem

- **ID:** `M08-Q004`
- **Module / topic:** M08 — read-only root filesystem
- **Level:** L3 Advanced
- **Objective tested:** Explain and apply read-only root filesystem in the context of non-root containers and runtime defaults.
- **Estimated time:** 13 minutes `[ILLUSTRATIVE]`
- **Question type:** short answer
- **Question prompt:** At L3, evaluate read-only root filesystem under a production constraint.
- **Model answer:** Compare at least two options, name the assumptions and failure modes, and choose based on evidence. Record version-sensitive behavior for official-document verification.
- **Common wrong answers / failure modes:** Confusing adjacent concepts; asserting a universal rule without assumptions; omitting evidence or limitations.
- **Scoring guidance:** 4 points: 2 for the core concept, 1 for operational consequence, 1 for a limitation or verification step.
- **Source/verification note:** Syllabus objective; check the relevant official Docker, BuildKit, OCI, registry or runtime documentation. `[VERIFY]` where implementation-specific.


### M08-Q005 — MCQ: UID/GID and root-in-container risk

- **ID:** `M08-Q005`
- **Module / topic:** M08 — MCQ: UID/GID and root-in-container risk
- **Level:** L1 Beginner
- **Objective tested:** Choose the defensible answer about UID/GID and root-in-container risk.
- **Estimated time:** 5 minutes `[ILLUSTRATIVE]`
- **Question type:** MCQ
- **Question prompt:** Which is the most defensible approach to UID/GID and root-in-container risk?

A. Choose a documented approach, verify it against the actual build/runtime context, and retain evidence.
B. A. Assume the default is secure.
C. B. Disable the control if it causes friction.
D. C. Treat a successful build as proof of production safety.
- **Model answer:** Choose a documented approach, verify it against the actual build/runtime context, and retain evidence.
- **Common wrong answers / failure modes:** Correct answer (A): Choose a documented approach, verify it against the actual build/runtime context, and retain evidence.

Distractors:
- A. Assume the default is secure. — Defaults can vary and may not meet the workload's needs.
- B. Disable the control if it causes friction. — This removes protection without diagnosing the failure.
- C. Treat a successful build as proof of production safety. — Build success does not prove runtime compatibility or security.
- **Scoring guidance:** 4 points: 1 for the correct option, 1 for rationale, and 2 for explaining distractors; for strict MCQ scoring, the selected answer earns 1 point.
- **Source/verification note:** Official documentation named in Appendix A; do not infer current defaults without checking the installed version.


### M08-Q006 — MCQ: numeric USER

- **ID:** `M08-Q006`
- **Module / topic:** M08 — MCQ: numeric USER
- **Level:** L2 Intermediate
- **Objective tested:** Choose the defensible answer about numeric USER.
- **Estimated time:** 5 minutes `[ILLUSTRATIVE]`
- **Question type:** MCQ
- **Question prompt:** A data-service container fails after a change to numeric USER. What should be done first?

A. A. Rebuild repeatedly without recording inputs.
B. Collect the exact error, identify the affected digest/platform/configuration, and run a discriminating test.
C. B. Grant broad privileges immediately.
D. C. Roll forward to a mutable tag without checking identity.
- **Model answer:** Collect the exact error, identify the affected digest/platform/configuration, and run a discriminating test.
- **Common wrong answers / failure modes:** Correct answer (B): Collect the exact error, identify the affected digest/platform/configuration, and run a discriminating test.

Distractors:
- A. Rebuild repeatedly without recording inputs. — This creates little diagnostic evidence.
- B. Grant broad privileges immediately. — The symptom may be unrelated and the change increases blast radius.
- C. Roll forward to a mutable tag without checking identity. — The artifact may differ from the tested release.
- **Scoring guidance:** 4 points: 1 for the correct option, 1 for rationale, and 2 for explaining distractors; for strict MCQ scoring, the selected answer earns 1 point.
- **Source/verification note:** Official documentation named in Appendix A; do not infer current defaults without checking the installed version.


### M08-Q007 — MCQ: COPY --chown

- **ID:** `M08-Q007`
- **Module / topic:** M08 — MCQ: COPY --chown
- **Level:** L3 Advanced
- **Objective tested:** Choose the defensible answer about COPY --chown.
- **Estimated time:** 5 minutes `[ILLUSTRATIVE]`
- **Question type:** MCQ
- **Question prompt:** Which statement about COPY --chown is correct?

A. A. It proves the image is vulnerability-free.
B. B. It makes all builds byte-identical.
C. A control or artifact provides bounded evidence; its scope and limitations must be stated explicitly.
D. C. It replaces rollback and monitoring.
- **Model answer:** A control or artifact provides bounded evidence; its scope and limitations must be stated explicitly.
- **Common wrong answers / failure modes:** Correct answer (C): A control or artifact provides bounded evidence; its scope and limitations must be stated explicitly.

Distractors:
- A. It proves the image is vulnerability-free. — No single control proves absence of all vulnerabilities.
- B. It makes all builds byte-identical. — Reproducibility depends on all material inputs and tooling.
- C. It replaces rollback and monitoring. — Operational controls remain necessary.
- **Scoring guidance:** 4 points: 1 for the correct option, 1 for rationale, and 2 for explaining distractors; for strict MCQ scoring, the selected answer earns 1 point.
- **Source/verification note:** Official documentation named in Appendix A; do not infer current defaults without checking the installed version.


### M08-Q008 — Evidence interpretation: writable paths and tmpfs

- **ID:** `M08-Q008`
- **Module / topic:** M08 — Evidence interpretation: writable paths and tmpfs
- **Level:** L2 Intermediate
- **Objective tested:** Interpret command or log evidence about writable paths and tmpfs without inventing hidden environmental facts.
- **Estimated time:** 7 minutes `[ILLUSTRATIVE]`
- **Question type:** command/output interpretation
- **Question prompt:** A build log for a Python API changes after a source-only edit while the dependency layer reruns. Interpret this evidence in relation to writable paths and tmpfs.

Representative evidence is `[ILLUSTRATIVE]`; no command was executed for this question.
- **Model answer:** The log proves the step reran in this build, not why. Inspect instruction ordering, exact inputs, build args and cache import/export. Move stable dependency manifests before frequently changing source where appropriate, then compare logs.
- **Common wrong answers / failure modes:** Assuming illustrative output was executed; treating one symptom as conclusive root cause; changing security controls before collecting evidence.
- **Scoring guidance:** 5 points: 2 for interpretation, 1 for limits of evidence, 1 for safe test, 1 for mitigation or verification.
- **Source/verification note:** Output is illustrative. Consult official CLI/runtime documentation for current flags and defaults.


### M08-Q009 — Evidence interpretation: capabilities and no-new-privileges

- **ID:** `M08-Q009`
- **Module / topic:** M08 — Evidence interpretation: capabilities and no-new-privileges
- **Level:** L3 Advanced
- **Objective tested:** Interpret command or log evidence about capabilities and no-new-privileges without inventing hidden environmental facts.
- **Estimated time:** 9 minutes `[ILLUSTRATIVE]`
- **Question type:** command/output interpretation
- **Question prompt:** [ILLUSTRATIVE] Runtime logs show a failure involving capabilities and no-new-privileges. State what the evidence proves, what it does not prove, and the next safe diagnostic step.

Representative evidence is `[ILLUSTRATIVE]`; no command was executed for this question.
- **Model answer:** The log proves a symptom, not a unique root cause. Check the exact error, image digest, platform, effective runtime config, filesystem/identity and dependency evidence. Apply a reversible mitigation and retest the final image.
- **Common wrong answers / failure modes:** Assuming illustrative output was executed; treating one symptom as conclusive root cause; changing security controls before collecting evidence.
- **Scoring guidance:** 5 points: 2 for interpretation, 1 for limits of evidence, 1 for safe test, 1 for mitigation or verification.
- **Source/verification note:** Output is illustrative. Consult official CLI/runtime documentation for current flags and defaults.


### M08-Q010 — Evidence interpretation: seccomp/AppArmor concepts

- **ID:** `M08-Q010`
- **Module / topic:** M08 — Evidence interpretation: seccomp/AppArmor concepts
- **Level:** L4 Expert
- **Objective tested:** Interpret command or log evidence about seccomp/AppArmor concepts without inventing hidden environmental facts.
- **Estimated time:** 11 minutes `[ILLUSTRATIVE]`
- **Question type:** command/output interpretation
- **Question prompt:** A release check reports a different image digest after a configuration change related to seccomp/AppArmor concepts. What does that prove and what should be compared?

Representative evidence is `[ILLUSTRATIVE]`; no command was executed for this question.
- **Model answer:** The digest difference means the image content identity differs; it does not by itself prove tampering or identify the cause. Compare base digest, resolved dependencies, platform, image config, layer contents, timestamps and provenance; promote only validated content.
- **Common wrong answers / failure modes:** Assuming illustrative output was executed; treating one symptom as conclusive root cause; changing security controls before collecting evidence.
- **Scoring guidance:** 5 points: 2 for interpretation, 1 for limits of evidence, 1 for safe test, 1 for mitigation or verification.
- **Source/verification note:** Output is illustrative. Consult official CLI/runtime documentation for current flags and defaults.


### M08-Q011 — Configuration review 1

- **ID:** `M08-Q011`
- **Module / topic:** M08 — Configuration review 1
- **Level:** L2 Intermediate
- **Objective tested:** Find at least three meaningful defects affecting UID/GID and root-in-container risk and propose safe corrections.
- **Estimated time:** 12 minutes `[ILLUSTRATIVE]`
- **Question type:** Dockerfile/config review
- **Question prompt:** Review this design: broad `COPY . .`; mutable base tag; dependency installation after copying all source; a secret supplied using `ARG`; no final-image smoke test. Context: UID/GID and root-in-container risk and numeric USER.
- **Model answer:** Defects and fixes: (1) broad context copy may include credentials, `.git`, datasets or virtual environments; add `.dockerignore` and selective COPY. (2) mutable base reference weakens input identity; document/pin the chosen base policy. (3) copy dependency manifests before source to improve cache reuse. (4) ARG is not a secret-delivery mechanism; use a supported BuildKit secret mount and verify no logs/layers leak it. (5) add final-image startup/import/health smoke tests.
- **Common wrong answers / failure modes:** Treating formatting as a security defect; recommending disabled TLS, embedded secrets, privileged execution or broad host mounts; fixing symptoms without validation.
- **Scoring guidance:** 8 points: 2 per substantive defect including impact and correction, plus 2 for prioritization and validation. Partial credit for another safe fix.
- **Source/verification note:** [VERIFY AGAINST FINAL UNIT FILE]. Consult Dockerfile, BuildKit, OCI, registry and runtime documentation as relevant.


### M08-Q012 — Configuration review 2

- **ID:** `M08-Q012`
- **Module / topic:** M08 — Configuration review 2
- **Level:** L4 Expert
- **Objective tested:** Find at least three meaningful defects affecting numeric USER and propose safe corrections.
- **Estimated time:** 12 minutes `[ILLUSTRATIVE]`
- **Question type:** Dockerfile/config review
- **Question prompt:** Review this release/runtime configuration: image deployed by mutable tag only; no recorded digest; broad registry permissions; no rollback inventory; no evidence from the actual target platform. Context: COPY --chown and read-only root filesystem.
- **Model answer:** Defects and fixes: (1) mutable tag is not stable release identity; record and deploy approved digest. (2) broad registry permissions increase blast radius; separate pull, push and delete/admin identities. (3) no rollback inventory; retain prior approved digests. (4) no target-platform validation; test each supported architecture. (5) no evidence trail; record source/build metadata, test results and promotion approval.
- **Common wrong answers / failure modes:** Treating formatting as a security defect; recommending disabled TLS, embedded secrets, privileged execution or broad host mounts; fixing symptoms without validation.
- **Scoring guidance:** 8 points: 2 per substantive defect including impact and correction, plus 2 for prioritization and validation. Partial credit for another safe fix.
- **Source/verification note:** [VERIFY AGAINST FINAL UNIT FILE]. Consult Dockerfile, BuildKit, OCI, registry and runtime documentation as relevant.


### M08-Q013 — Incident: COPY --chown

- **ID:** `M08-Q013`
- **Module / topic:** M08 — Incident: COPY --chown
- **Level:** L3 Advanced
- **Objective tested:** Diagnose an operational failure involving COPY --chown and provide safe recovery.
- **Estimated time:** 15 minutes `[ILLUSTRATIVE]`
- **Question type:** incident/troubleshooting
- **Question prompt:** Incident: a production data-service rollout fails after a change involving UID/GID and root-in-container risk. Give symptom, scope, hypotheses, discriminating tests, mitigation, root cause, prevention and follow-up evidence.
- **Model answer:** First establish affected release digests, platforms, nodes and time window. Treat causes as hypotheses until logs/tests discriminate them. Preserve healthy workloads and rollback to a known approved digest if impact warrants. Fix the demonstrated cause, add a regression test, and record post-change health and ownership.
- **Common wrong answers / failure modes:** Jumping to root cause; no impact scope; unsafe cleanup; broad privilege; missing rollback or follow-up evidence.
- **Scoring guidance:** 10 points: symptom/scope 2; hypotheses/tests 2; mitigation 2; root cause/prevention 2; follow-up evidence/owner 2.
- **Source/verification note:** Illustrative scenario. Verify implementation-specific operations in the current official runbook.


### M08-Q014 — Incident: read-only root filesystem

- **ID:** `M08-Q014`
- **Module / topic:** M08 — Incident: read-only root filesystem
- **Level:** L4 Expert
- **Objective tested:** Diagnose an operational failure involving read-only root filesystem and provide safe recovery.
- **Estimated time:** 15 minutes `[ILLUSTRATIVE]`
- **Question type:** incident/troubleshooting
- **Question prompt:** Incident: the team proposes a broad cleanup/security bypass to resolve an issue involving read-only root filesystem. As incident lead, define a safer response and recovery plan.
- **Model answer:** Do not perform broad deletion or disable protections without evidence. Scope the impact, preserve artifacts/logs, inspect the actual failure and current policy, choose a reversible mitigation, and document approval. Verify recovery with pull/startup/health tests and add a runbook or guardrail.
- **Common wrong answers / failure modes:** Jumping to root cause; no impact scope; unsafe cleanup; broad privilege; missing rollback or follow-up evidence.
- **Scoring guidance:** 10 points: symptom/scope 2; hypotheses/tests 2; mitigation 2; root cause/prevention 2; follow-up evidence/owner 2.
- **Source/verification note:** Illustrative scenario. Verify implementation-specific operations in the current official runbook.


### M08-Q015 — Whiteboard design review

- **ID:** `M08-Q015`
- **Module / topic:** M08 — Whiteboard design review
- **Level:** L4 Expert
- **Objective tested:** Design and defend a production approach to non-root containers and runtime defaults.
- **Estimated time:** 25 minutes `[ILLUSTRATIVE]`
- **Question type:** design
- **Question prompt:** Design hardening for a FastAPI inference container that loads a model, writes scratch files, exposes health endpoints and must shut down gracefully. Defend read-only root plus targeted writable mounts against a writable root.
- **Model answer:** A strong answer states assumptions, provides a traceable design, names failure modes, defines acceptance evidence and defends the trade-off. Multiple architectures can earn full credit if constraints are explicit.
- **Common wrong answers / failure modes:** Selecting a tool without assumptions; claiming one universally correct answer; ignoring recovery, trust boundaries or measurable acceptance criteria.
- **Scoring guidance:** 10 points: numeric identity/ownership 2; writable-path inventory 2; capability/no-new-privileges/seccomp awareness 2; limits/probes/PID 1 2; policy tests and trade-off defense 2.
- **Source/verification note:** [VERIFY AGAINST FINAL UNIT FILE]. Version-sensitive implementation claims require current official documentation.



**Module tally:** 15 questions. IDs `M08-Q001` through `M08-Q015`.


## Cross-module integration

These 15 scenarios combine the eight modules and do not add a ninth module. They are L4 and require evidence-based production judgment.

### XMOD-Q001 — Multi-stage + distroless + non-root

- **ID:** `XMOD-Q001`
- **Module / topic:** XMOD — Multi-stage + distroless + non-root
- **Level:** L4 Expert
- **Objective tested:** Integrate multiple M01 modules to make a safe production decision for multi-stage + distroless + non-root.
- **Estimated time:** 18 minutes `[ILLUSTRATIVE]`
- **Question type:** cross-module integration
- **Question prompt:** FastAPI fails to load a model after moving to distroless and UID 10001. Diagnose evidence, mitigation and prevention.
- **Model answer:** Compare builder/runtime ABI, copied artifacts, ownership, certificates and writable paths. Roll back to approved digest if needed; copy only runtime dependencies, set ownership, mount only required writable paths, and test startup under the effective UID.
- **Common wrong answers / failure modes:** Trusting tags, cache, or scanner presence as proof; broad privilege or unsafe deletion; failure to preserve rollback options.
- **Scoring guidance:** 5 points: scope/evidence 1; hypotheses or correct distinction 1; mitigation 1; prevention 1; follow-up evidence 1.
- **Source/verification note:** Illustrative integration scenario. Verify current implementation-specific behavior against official documentation.


### XMOD-Q002 — Reproducibility + cache + digest promotion

- **ID:** `XMOD-Q002`
- **Module / topic:** XMOD — Reproducibility + cache + digest promotion
- **Level:** L4 Expert
- **Objective tested:** Integrate multiple M01 modules to make a safe production decision for reproducibility + cache + digest promotion.
- **Estimated time:** 18 minutes `[ILLUSTRATIVE]`
- **Question type:** cross-module integration
- **Question prompt:** A warm CI build using remote cache differs from a local rebuild at the same Git SHA. Define the release gate.
- **Model answer:** Compare base digest, lockfiles/hashes, package sources, platform, timestamps, builder, cache inputs and image config/layers. Rebuild in trusted context and promote only validated digest; cache is not provenance.
- **Common wrong answers / failure modes:** Trusting tags, cache, or scanner presence as proof; broad privilege or unsafe deletion; failure to preserve rollback options.
- **Scoring guidance:** 5 points: scope/evidence 1; hypotheses or correct distinction 1; mitigation 1; prevention 1; follow-up evidence 1.
- **Source/verification note:** Illustrative integration scenario. Verify current implementation-specific behavior against official documentation.


### XMOD-Q003 — Mutable tag + mirror outage + rollback

- **ID:** `XMOD-Q003`
- **Module / topic:** XMOD — Mutable tag + mirror outage + rollback
- **Level:** L4 Expert
- **Objective tested:** Integrate multiple M01 modules to make a safe production decision for mutable tag + mirror outage + rollback.
- **Estimated time:** 18 minutes `[ILLUSTRATIVE]`
- **Question type:** cross-module integration
- **Question prompt:** A tag moves during upstream outage; existing nodes run but cold nodes cannot pull. Contain and recover.
- **Model answer:** Inventory imageIDs/digests, freeze tag movement, preserve healthy workloads, retrieve approved content from trusted cache/replica by digest, restore upstream and validate. Add digest-based rollout and drift checks.
- **Common wrong answers / failure modes:** Trusting tags, cache, or scanner presence as proof; broad privilege or unsafe deletion; failure to preserve rollback options.
- **Scoring guidance:** 5 points: scope/evidence 1; hypotheses or correct distinction 1; mitigation 1; prevention 1; follow-up evidence 1.
- **Source/verification note:** Illustrative integration scenario. Verify current implementation-specific behavior against official documentation.


### XMOD-Q004 — SBOM + quarantine + retention

- **ID:** `XMOD-Q004`
- **Module / topic:** XMOD — SBOM + quarantine + retention
- **Level:** L4 Expert
- **Objective tested:** Integrate multiple M01 modules to make a safe production decision for sbom + quarantine + retention.
- **Estimated time:** 18 minutes `[ILLUSTRATIVE]`
- **Question type:** cross-module integration
- **Question prompt:** A scan finds a critical package in a production-tagged image while cleanup is scheduled. Coordinate controls.
- **Model answer:** Quarantine the digest, block promotion, triage context and owner, preserve evidence, pause deletion of potentially relevant artifacts, remediate and rescan. A scan is evidence, not a complete safety verdict.
- **Common wrong answers / failure modes:** Trusting tags, cache, or scanner presence as proof; broad privilege or unsafe deletion; failure to preserve rollback options.
- **Scoring guidance:** 5 points: scope/evidence 1; hypotheses or correct distinction 1; mitigation 1; prevention 1; follow-up evidence 1.
- **Source/verification note:** Illustrative integration scenario. Verify current implementation-specific behavior against official documentation.


### XMOD-Q005 — Read-only root + scratch + limits

- **ID:** `XMOD-Q005`
- **Module / topic:** XMOD — Read-only root + scratch + limits
- **Level:** L4 Expert
- **Objective tested:** Integrate multiple M01 modules to make a safe production decision for read-only root + scratch + limits.
- **Estimated time:** 18 minutes `[ILLUSTRATIVE]`
- **Question type:** cross-module integration
- **Question prompt:** A PySpark worker fails on read-only root and then OOMs after scratch is moved to tmpfs.
- **Model answer:** Inventory write paths; distinguish scratch from durable output; inspect memory and ephemeral-storage pressure. Use bounded temporary storage and durable output storage, set appropriate limits and test representative load.
- **Common wrong answers / failure modes:** Trusting tags, cache, or scanner presence as proof; broad privilege or unsafe deletion; failure to preserve rollback options.
- **Scoring guidance:** 5 points: scope/evidence 1; hypotheses or correct distinction 1; mitigation 1; prevention 1; follow-up evidence 1.
- **Source/verification note:** Illustrative integration scenario. Verify current implementation-specific behavior against official documentation.


### XMOD-Q006 — GC + in-use inventory + restore

- **ID:** `XMOD-Q006`
- **Module / topic:** XMOD — GC + in-use inventory + restore
- **Level:** L4 Expert
- **Objective tested:** Integrate multiple M01 modules to make a safe production decision for gc + in-use inventory + restore.
- **Estimated time:** 18 minutes `[ILLUSTRATIVE]`
- **Question type:** cross-module integration
- **Question prompt:** Registry is full and an old digest has no tag but appears in rollback records. What preflight is required?
- **Model answer:** Resolve deployment/rollback records to digests, enumerate references, verify backups and implementation-specific GC semantics, review a dry-run, control writes as documented and verify critical pulls afterward.
- **Common wrong answers / failure modes:** Trusting tags, cache, or scanner presence as proof; broad privilege or unsafe deletion; failure to preserve rollback options.
- **Scoring guidance:** 5 points: scope/evidence 1; hypotheses or correct distinction 1; mitigation 1; prevention 1; follow-up evidence 1.
- **Source/verification note:** Illustrative integration scenario. Verify current implementation-specific behavior against official documentation.


### XMOD-Q007 — Multi-platform index + ABI

- **ID:** `XMOD-Q007`
- **Module / topic:** XMOD — Multi-platform index + ABI
- **Level:** L4 Expert
- **Objective tested:** Integrate multiple M01 modules to make a safe production decision for multi-platform index + abi.
- **Estimated time:** 18 minutes `[ILLUSTRATIVE]`
- **Question type:** cross-module integration
- **Question prompt:** AMD64 passes, ARM64 fails a native import, but the top-level index digest is stable. Explain.
- **Model answer:** Index digest identifies an index, not successful child behavior. Inspect child digest/platform and ABI; test each supported architecture and record per-platform evidence. Roll back or constrain support until fixed.
- **Common wrong answers / failure modes:** Trusting tags, cache, or scanner presence as proof; broad privilege or unsafe deletion; failure to preserve rollback options.
- **Scoring guidance:** 5 points: scope/evidence 1; hypotheses or correct distinction 1; mitigation 1; prevention 1; follow-up evidence 1.
- **Source/verification note:** Illustrative integration scenario. Verify current implementation-specific behavior against official documentation.


### XMOD-Q008 — Cache poisoning + SBOM + access

- **ID:** `XMOD-Q008`
- **Module / topic:** XMOD — Cache poisoning + SBOM + access
- **Level:** L4 Expert
- **Objective tested:** Integrate multiple M01 modules to make a safe production decision for cache poisoning + sbom + access.
- **Estimated time:** 18 minutes `[ILLUSTRATIVE]`
- **Question type:** cross-module integration
- **Question prompt:** An untrusted branch can write a cache used by release builds; resulting image has an SBOM. Is it trustworthy?
- **Model answer:** Not on that evidence alone. Separate cache trust domains, restrict writers, rebuild/validate in trusted release context, verify provenance/signature per policy, and treat SBOM as component inventory rather than proof of origin.
- **Common wrong answers / failure modes:** Trusting tags, cache, or scanner presence as proof; broad privilege or unsafe deletion; failure to preserve rollback options.
- **Scoring guidance:** 5 points: scope/evidence 1; hypotheses or correct distinction 1; mitigation 1; prevention 1; follow-up evidence 1.
- **Source/verification note:** Illustrative integration scenario. Verify current implementation-specific behavior against official documentation.


### XMOD-Q009 — Build SLO + cold/warm measurement

- **ID:** `XMOD-Q009`
- **Module / topic:** XMOD — Build SLO + cold/warm measurement
- **Level:** L4 Expert
- **Objective tested:** Integrate multiple M01 modules to make a safe production decision for build slo + cold/warm measurement.
- **Estimated time:** 18 minutes `[ILLUSTRATIVE]`
- **Question type:** cross-module integration
- **Question prompt:** A team claims a build SLO based only on warm local timings while CI runners share disk and CPU.
- **Model answer:** Define workload and SLO; measure cold/warm/partial cases repeatedly on representative runners; record cache state, architecture, network and pressure; track percentiles, failures and capacity without inventing measurements.
- **Common wrong answers / failure modes:** Trusting tags, cache, or scanner presence as proof; broad privilege or unsafe deletion; failure to preserve rollback options.
- **Scoring guidance:** 5 points: scope/evidence 1; hypotheses or correct distinction 1; mitigation 1; prevention 1; follow-up evidence 1.
- **Source/verification note:** Illustrative integration scenario. Verify current implementation-specific behavior against official documentation.


### XMOD-Q010 — Tag movement + pull failure + fleet recovery

- **ID:** `XMOD-Q010`
- **Module / topic:** XMOD — Tag movement + pull failure + fleet recovery
- **Level:** L4 Expert
- **Objective tested:** Integrate multiple M01 modules to make a safe production decision for tag movement + pull failure + fleet recovery.
- **Estimated time:** 18 minutes `[ILLUSTRATIVE]`
- **Question type:** cross-module integration
- **Question prompt:** During rollout, a mutable tag moves, some nodes fail pulls and running nodes show different imageIDs.
- **Model answer:** Freeze promotion, collect imageIDs, tag resolution, pull errors and release records. Preserve healthy fleet, roll back/forward only to approved digests, restore registry access and add digest pinning and drift alerts.
- **Common wrong answers / failure modes:** Trusting tags, cache, or scanner presence as proof; broad privilege or unsafe deletion; failure to preserve rollback options.
- **Scoring guidance:** 5 points: scope/evidence 1; hypotheses or correct distinction 1; mitigation 1; prevention 1; follow-up evidence 1.
- **Source/verification note:** Illustrative integration scenario. Verify current implementation-specific behavior against official documentation.


### XMOD-Q011 — Build secrets + lockfiles + cache

- **ID:** `XMOD-Q011`
- **Module / topic:** XMOD — Build secrets + lockfiles + cache
- **Level:** L4 Expert
- **Objective tested:** Integrate multiple M01 modules to make a safe production decision for build secrets + lockfiles + cache.
- **Estimated time:** 18 minutes `[ILLUSTRATIVE]`
- **Question type:** cross-module integration
- **Question prompt:** A package token is supplied as ARG and dependency resolution changes between builds. Fix both without losing cache efficiency.
- **Model answer:** Use supported BuildKit secret mount, ensure installer does not log/copy token, pin dependencies and hashes, control repository inputs, copy lockfile before source and verify secrets are absent from layers/metadata.
- **Common wrong answers / failure modes:** Trusting tags, cache, or scanner presence as proof; broad privilege or unsafe deletion; failure to preserve rollback options.
- **Scoring guidance:** 5 points: scope/evidence 1; hypotheses or correct distinction 1; mitigation 1; prevention 1; follow-up evidence 1.
- **Source/verification note:** Illustrative integration scenario. Verify current implementation-specific behavior against official documentation.


### XMOD-Q012 — Minimal image + scanner + TLS

- **ID:** `XMOD-Q012`
- **Module / topic:** XMOD — Minimal image + scanner + TLS
- **Level:** L4 Expert
- **Objective tested:** Integrate multiple M01 modules to make a safe production decision for minimal image + scanner + tls.
- **Estimated time:** 18 minutes `[ILLUSTRATIVE]`
- **Question type:** cross-module integration
- **Question prompt:** A minimal image has zero scan findings but TLS and timezone operations fail.
- **Model answer:** Zero findings means none were detected within scan scope/database, not that the image is safe or compatible. Add required CA/timezone data, test final-image TLS/time behavior and record scan scope.
- **Common wrong answers / failure modes:** Trusting tags, cache, or scanner presence as proof; broad privilege or unsafe deletion; failure to preserve rollback options.
- **Scoring guidance:** 5 points: scope/evidence 1; hypotheses or correct distinction 1; mitigation 1; prevention 1; follow-up evidence 1.
- **Source/verification note:** Illustrative integration scenario. Verify current implementation-specific behavior against official documentation.


### XMOD-Q013 — Cache outage + capacity

- **ID:** `XMOD-Q013`
- **Module / topic:** XMOD — Cache outage + capacity
- **Level:** L4 Expert
- **Objective tested:** Integrate multiple M01 modules to make a safe production decision for cache outage + capacity.
- **Estimated time:** 18 minutes `[ILLUSTRATIVE]`
- **Question type:** cross-module integration
- **Question prompt:** A pull-through cache fills disk and cold nodes fail on cache misses.
- **Model answer:** Scope by hit/miss and disk pressure; avoid unreviewed deletion. Use approved alternate registry or safely add capacity; protect required digests; define eviction, monitoring and cold-start drills.
- **Common wrong answers / failure modes:** Trusting tags, cache, or scanner presence as proof; broad privilege or unsafe deletion; failure to preserve rollback options.
- **Scoring guidance:** 5 points: scope/evidence 1; hypotheses or correct distinction 1; mitigation 1; prevention 1; follow-up evidence 1.
- **Source/verification note:** Illustrative integration scenario. Verify current implementation-specific behavior against official documentation.


### XMOD-Q014 — Rootless + limits + filesystem

- **ID:** `XMOD-Q014`
- **Module / topic:** XMOD — Rootless + limits + filesystem
- **Level:** L4 Expert
- **Objective tested:** Integrate multiple M01 modules to make a safe production decision for rootless + limits + filesystem.
- **Estimated time:** 18 minutes `[ILLUSTRATIVE]`
- **Question type:** cross-module integration
- **Question prompt:** Team says rootless Docker means a Python worker needs no limits or filesystem restrictions.
- **Model answer:** Rootless engine and non-root process are different controls. Apply resource limits, least privilege, filesystem/write-path controls and runtime policy appropriate to the threat model; test load and exhaustion behavior.
- **Common wrong answers / failure modes:** Trusting tags, cache, or scanner presence as proof; broad privilege or unsafe deletion; failure to preserve rollback options.
- **Scoring guidance:** 5 points: scope/evidence 1; hypotheses or correct distinction 1; mitigation 1; prevention 1; follow-up evidence 1.
- **Source/verification note:** Illustrative integration scenario. Verify current implementation-specific behavior against official documentation.


### XMOD-Q015 — Quarantine + deletion incident

- **ID:** `XMOD-Q015`
- **Module / topic:** XMOD — Quarantine + deletion incident
- **Level:** L4 Expert
- **Objective tested:** Integrate multiple M01 modules to make a safe production decision for quarantine + deletion incident.
- **Estimated time:** 18 minutes `[ILLUSTRATIVE]`
- **Question type:** cross-module integration
- **Question prompt:** A suspected compromised digest is quarantined, but retention would delete it before investigation closes.
- **Model answer:** Block promotion/use while preserving evidence with restricted access and a documented hold. Record digest/provenance, assign incident owner, restrict deletion, then dispose only after documented clearance.
- **Common wrong answers / failure modes:** Trusting tags, cache, or scanner presence as proof; broad privilege or unsafe deletion; failure to preserve rollback options.
- **Scoring guidance:** 5 points: scope/evidence 1; hypotheses or correct distinction 1; mitigation 1; prevention 1; follow-up evidence 1.
- **Source/verification note:** Illustrative integration scenario. Verify current implementation-specific behavior against official documentation.



## Six whiteboard/design-review prompts

These are the additional module design questions already counted as M03-Q015 through M08-Q015; they are not counted twice. They cover reproducibility, caching, release/registry strategy and runtime hardening. At least four require defending a decision against a plausible alternative. See each module question for full prompt and rubric.

- `M03-Q015` — Reproducible and deterministic image builds

- `M04-Q015` — Build caching, BuildKit, and build performance

- `M05-Q015` — Image tagging, versioning, and immutability

- `M06-Q015` — Container registries, mirrors, and pull-through caches

- `M07-Q015` — Registry retention, garbage collection, and access control

- `M08-Q015` — Non-root containers and runtime defaults


## Answer-key navigation and question index

Each question contains its model answer and scoring guidance inline.

| ID | Module | Level | Type | Topic |
|---|---|---|---|---|

| `M01-Q001` | 1 | L1 Beginner | short answer | build context and .dockerignore |

| `M01-Q002` | 1 | L1 Beginner | short answer | instruction ordering and cache invalidation |

| `M01-Q003` | 1 | L2 Intermediate | short answer | builder/runtime separation |

| `M01-Q004` | 1 | L3 Advanced | short answer | BuildKit secrets and cache mounts |

| `M01-Q005` | 1 | L1 Beginner | MCQ | MCQ: build context and .dockerignore |

| `M01-Q006` | 1 | L2 Intermediate | MCQ | MCQ: instruction ordering and cache invalidation |

| `M01-Q007` | 1 | L3 Advanced | MCQ | MCQ: builder/runtime separation |

| `M01-Q008` | 1 | L2 Intermediate | command/output interpretation | Evidence interpretation: image-size measurement |

| `M01-Q009` | 1 | L3 Advanced | command/output interpretation | Evidence interpretation: FastAPI dependencies |

| `M01-Q010` | 1 | L4 Expert | command/output interpretation | Evidence interpretation: Go linking |

| `M01-Q011` | 1 | L2 Intermediate | Dockerfile/config review | Configuration review 1 |

| `M01-Q012` | 1 | L4 Expert | Dockerfile/config review | Configuration review 2 |

| `M01-Q013` | 1 | L3 Advanced | incident/troubleshooting | Incident: builder/runtime separation |

| `M01-Q014` | 1 | L4 Expert | incident/troubleshooting | Incident: BuildKit secrets and cache mounts |

| `M02-Q001` | 2 | L1 Beginner | short answer | full/slim/minimal/distroless trade-offs |

| `M02-Q002` | 2 | L1 Beginner | short answer | glibc versus musl |

| `M02-Q003` | 2 | L2 Intermediate | short answer | Python native wheels |

| `M02-Q004` | 2 | L3 Advanced | short answer | CA certificates |

| `M02-Q005` | 2 | L1 Beginner | MCQ | MCQ: full/slim/minimal/distroless trade-offs |

| `M02-Q006` | 2 | L2 Intermediate | MCQ | MCQ: glibc versus musl |

| `M02-Q007` | 2 | L3 Advanced | MCQ | MCQ: Python native wheels |

| `M02-Q008` | 2 | L2 Intermediate | command/output interpretation | Evidence interpretation: timezone and locale data |

| `M02-Q009` | 2 | L3 Advanced | command/output interpretation | Evidence interpretation: numeric user metadata |

| `M02-Q010` | 2 | L4 Expert | command/output interpretation | Evidence interpretation: runtime dependency closure |

| `M02-Q011` | 2 | L2 Intermediate | Dockerfile/config review | Configuration review 1 |

| `M02-Q012` | 2 | L4 Expert | Dockerfile/config review | Configuration review 2 |

| `M02-Q013` | 2 | L3 Advanced | incident/troubleshooting | Incident: Python native wheels |

| `M02-Q014` | 2 | L4 Expert | incident/troubleshooting | Incident: CA certificates |

| `M03-Q001` | 3 | L1 Beginner | short answer | mutable tags versus digests |

| `M03-Q002` | 3 | L1 Beginner | short answer | base image pinning |

| `M03-Q003` | 3 | L2 Intermediate | short answer | lockfiles and hashes |

| `M03-Q004` | 3 | L3 Advanced | short answer | package repository snapshots |

| `M03-Q005` | 3 | L1 Beginner | MCQ | MCQ: mutable tags versus digests |

| `M03-Q006` | 3 | L2 Intermediate | MCQ | MCQ: base image pinning |

| `M03-Q007` | 3 | L3 Advanced | MCQ | MCQ: lockfiles and hashes |

| `M03-Q008` | 3 | L2 Intermediate | command/output interpretation | Evidence interpretation: timestamps and SOURCE_DATE_EPOCH |

| `M03-Q009` | 3 | L3 Advanced | command/output interpretation | Evidence interpretation: artifact versus image reproducibility |

| `M03-Q010` | 3 | L4 Expert | command/output interpretation | Evidence interpretation: hermetic/offline builds |

| `M03-Q011` | 3 | L2 Intermediate | Dockerfile/config review | Configuration review 1 |

| `M03-Q012` | 3 | L4 Expert | Dockerfile/config review | Configuration review 2 |

| `M03-Q013` | 3 | L3 Advanced | incident/troubleshooting | Incident: lockfiles and hashes |

| `M03-Q014` | 3 | L4 Expert | incident/troubleshooting | Incident: package repository snapshots |

| `M03-Q015` | 3 | L4 Expert | design | Whiteboard design review |

| `M04-Q001` | 4 | L1 Beginner | short answer | cache invalidation |

| `M04-Q002` | 4 | L1 Beginner | short answer | dependency-first copy patterns |

| `M04-Q003` | 4 | L2 Intermediate | short answer | BuildKit/buildx |

| `M04-Q004` | 4 | L3 Advanced | short answer | cache mounts |

| `M04-Q005` | 4 | L1 Beginner | MCQ | MCQ: cache invalidation |

| `M04-Q006` | 4 | L2 Intermediate | MCQ | MCQ: dependency-first copy patterns |

| `M04-Q007` | 4 | L3 Advanced | MCQ | MCQ: BuildKit/buildx |

| `M04-Q008` | 4 | L2 Intermediate | command/output interpretation | Evidence interpretation: local/inline/registry/CI caches |

| `M04-Q009` | 4 | L3 Advanced | command/output interpretation | Evidence interpretation: cache trust boundaries |

| `M04-Q010` | 4 | L4 Expert | command/output interpretation | Evidence interpretation: cold/warm/partial measurements |

| `M04-Q011` | 4 | L2 Intermediate | Dockerfile/config review | Configuration review 1 |

| `M04-Q012` | 4 | L4 Expert | Dockerfile/config review | Configuration review 2 |

| `M04-Q013` | 4 | L3 Advanced | incident/troubleshooting | Incident: BuildKit/buildx |

| `M04-Q014` | 4 | L4 Expert | incident/troubleshooting | Incident: cache mounts |

| `M04-Q015` | 4 | L4 Expert | design | Whiteboard design review |

| `M05-Q001` | 5 | L1 Beginner | short answer | mutable tags versus digests |

| `M05-Q002` | 5 | L1 Beginner | short answer | SemVer and Git SHA |

| `M05-Q003` | 5 | L2 Intermediate | short answer | build metadata |

| `M05-Q004` | 5 | L3 Advanced | short answer | OCI labels |

| `M05-Q005` | 5 | L1 Beginner | MCQ | MCQ: mutable tags versus digests |

| `M05-Q006` | 5 | L2 Intermediate | MCQ | MCQ: SemVer and Git SHA |

| `M05-Q007` | 5 | L3 Advanced | MCQ | MCQ: build metadata |

| `M05-Q008` | 5 | L2 Intermediate | command/output interpretation | Evidence interpretation: multi-platform image index |

| `M05-Q009` | 5 | L3 Advanced | command/output interpretation | Evidence interpretation: digest-based promotion |

| `M05-Q010` | 5 | L4 Expert | command/output interpretation | Evidence interpretation: rollback identity |

| `M05-Q011` | 5 | L2 Intermediate | Dockerfile/config review | Configuration review 1 |

| `M05-Q012` | 5 | L4 Expert | Dockerfile/config review | Configuration review 2 |

| `M05-Q013` | 5 | L3 Advanced | incident/troubleshooting | Incident: build metadata |

| `M05-Q014` | 5 | L4 Expert | incident/troubleshooting | Incident: OCI labels |

| `M05-Q015` | 5 | L4 Expert | design | Whiteboard design review |

| `M06-Q001` | 6 | L1 Beginner | short answer | OCI Distribution concepts |

| `M06-Q002` | 6 | L1 Beginner | short answer | local Distribution registry |

| `M06-Q003` | 6 | L2 Intermediate | short answer | authentication versus TLS |

| `M06-Q004` | 6 | L3 Advanced | short answer | registry mirrors |

| `M06-Q005` | 6 | L1 Beginner | MCQ | MCQ: OCI Distribution concepts |

| `M06-Q006` | 6 | L2 Intermediate | MCQ | MCQ: local Distribution registry |

| `M06-Q007` | 6 | L3 Advanced | MCQ | MCQ: authentication versus TLS |

| `M06-Q008` | 6 | L2 Intermediate | command/output interpretation | Evidence interpretation: pull-through cache hit/miss |

| `M06-Q009` | 6 | L3 Advanced | command/output interpretation | Evidence interpretation: Docker versus containerd config |

| `M06-Q010` | 6 | L4 Expert | command/output interpretation | Evidence interpretation: hosted registry comparison |

| `M06-Q011` | 6 | L2 Intermediate | Dockerfile/config review | Configuration review 1 |

| `M06-Q012` | 6 | L4 Expert | Dockerfile/config review | Configuration review 2 |

| `M06-Q013` | 6 | L3 Advanced | incident/troubleshooting | Incident: authentication versus TLS |

| `M06-Q014` | 6 | L4 Expert | incident/troubleshooting | Incident: registry mirrors |

| `M06-Q015` | 6 | L4 Expert | design | Whiteboard design review |

| `M07-Q001` | 7 | L1 Beginner | short answer | retention policy |

| `M07-Q002` | 7 | L1 Beginner | short answer | tag deletion versus blob reachability |

| `M07-Q003` | 7 | L2 Intermediate | short answer | garbage-collection sequencing |

| `M07-Q004` | 7 | L3 Advanced | short answer | in-use digest protection |

| `M07-Q005` | 7 | L1 Beginner | MCQ | MCQ: retention policy |

| `M07-Q006` | 7 | L2 Intermediate | MCQ | MCQ: tag deletion versus blob reachability |

| `M07-Q007` | 7 | L3 Advanced | MCQ | MCQ: garbage-collection sequencing |

| `M07-Q008` | 7 | L2 Intermediate | command/output interpretation | Evidence interpretation: dry-run plans |

| `M07-Q009` | 7 | L3 Advanced | command/output interpretation | Evidence interpretation: least privilege |

| `M07-Q010` | 7 | L4 Expert | command/output interpretation | Evidence interpretation: push/pull/delete separation |

| `M07-Q011` | 7 | L2 Intermediate | Dockerfile/config review | Configuration review 1 |

| `M07-Q012` | 7 | L4 Expert | Dockerfile/config review | Configuration review 2 |

| `M07-Q013` | 7 | L3 Advanced | incident/troubleshooting | Incident: garbage-collection sequencing |

| `M07-Q014` | 7 | L4 Expert | incident/troubleshooting | Incident: in-use digest protection |

| `M07-Q015` | 7 | L4 Expert | design | Whiteboard design review |

| `M08-Q001` | 8 | L1 Beginner | short answer | UID/GID and root-in-container risk |

| `M08-Q002` | 8 | L1 Beginner | short answer | numeric USER |

| `M08-Q003` | 8 | L2 Intermediate | short answer | COPY --chown |

| `M08-Q004` | 8 | L3 Advanced | short answer | read-only root filesystem |

| `M08-Q005` | 8 | L1 Beginner | MCQ | MCQ: UID/GID and root-in-container risk |

| `M08-Q006` | 8 | L2 Intermediate | MCQ | MCQ: numeric USER |

| `M08-Q007` | 8 | L3 Advanced | MCQ | MCQ: COPY --chown |

| `M08-Q008` | 8 | L2 Intermediate | command/output interpretation | Evidence interpretation: writable paths and tmpfs |

| `M08-Q009` | 8 | L3 Advanced | command/output interpretation | Evidence interpretation: capabilities and no-new-privileges |

| `M08-Q010` | 8 | L4 Expert | command/output interpretation | Evidence interpretation: seccomp/AppArmor concepts |

| `M08-Q011` | 8 | L2 Intermediate | Dockerfile/config review | Configuration review 1 |

| `M08-Q012` | 8 | L4 Expert | Dockerfile/config review | Configuration review 2 |

| `M08-Q013` | 8 | L3 Advanced | incident/troubleshooting | Incident: COPY --chown |

| `M08-Q014` | 8 | L4 Expert | incident/troubleshooting | Incident: read-only root filesystem |

| `M08-Q015` | 8 | L4 Expert | design | Whiteboard design review |

| `XMOD-Q001` | XMOD | L4 Expert | cross-module integration | Multi-stage + distroless + non-root |

| `XMOD-Q002` | XMOD | L4 Expert | cross-module integration | Reproducibility + cache + digest promotion |

| `XMOD-Q003` | XMOD | L4 Expert | cross-module integration | Mutable tag + mirror outage + rollback |

| `XMOD-Q004` | XMOD | L4 Expert | cross-module integration | SBOM + quarantine + retention |

| `XMOD-Q005` | XMOD | L4 Expert | cross-module integration | Read-only root + scratch + limits |

| `XMOD-Q006` | XMOD | L4 Expert | cross-module integration | GC + in-use inventory + restore |

| `XMOD-Q007` | XMOD | L4 Expert | cross-module integration | Multi-platform index + ABI |

| `XMOD-Q008` | XMOD | L4 Expert | cross-module integration | Cache poisoning + SBOM + access |

| `XMOD-Q009` | XMOD | L4 Expert | cross-module integration | Build SLO + cold/warm measurement |

| `XMOD-Q010` | XMOD | L4 Expert | cross-module integration | Tag movement + pull failure + fleet recovery |

| `XMOD-Q011` | XMOD | L4 Expert | cross-module integration | Build secrets + lockfiles + cache |

| `XMOD-Q012` | XMOD | L4 Expert | cross-module integration | Minimal image + scanner + TLS |

| `XMOD-Q013` | XMOD | L4 Expert | cross-module integration | Cache outage + capacity |

| `XMOD-Q014` | XMOD | L4 Expert | cross-module integration | Rootless + limits + filesystem |

| `XMOD-Q015` | XMOD | L4 Expert | cross-module integration | Quarantine + deletion incident |


## Module coverage matrix

| Module | Required type | Required count | Actual count | Levels covered | Status |
|---|---|---:|---:|---|---|

| M01 — Multi-stage builds and layer optimization | short answer | 4 | 4 | L1–L4 | COVERED |

| M01 — Multi-stage builds and layer optimization | MCQ | 3 | 3 | L1–L4 | COVERED |

| M01 — Multi-stage builds and layer optimization | command/output interpretation | 3 | 3 | L1–L4 | COVERED |

| M01 — Multi-stage builds and layer optimization | Dockerfile/config review | 2 | 2 | L1–L4 | COVERED |

| M01 — Multi-stage builds and layer optimization | incident/troubleshooting | 2 | 2 | L1–L4 | COVERED |

| M02 — Minimal and distroless base images | short answer | 4 | 4 | L1–L4 | COVERED |

| M02 — Minimal and distroless base images | MCQ | 3 | 3 | L1–L4 | COVERED |

| M02 — Minimal and distroless base images | command/output interpretation | 3 | 3 | L1–L4 | COVERED |

| M02 — Minimal and distroless base images | Dockerfile/config review | 2 | 2 | L1–L4 | COVERED |

| M02 — Minimal and distroless base images | incident/troubleshooting | 2 | 2 | L1–L4 | COVERED |

| M03 — Reproducible and deterministic image builds | short answer | 4 | 4 | L1–L4 | COVERED |

| M03 — Reproducible and deterministic image builds | MCQ | 3 | 3 | L1–L4 | COVERED |

| M03 — Reproducible and deterministic image builds | command/output interpretation | 3 | 3 | L1–L4 | COVERED |

| M03 — Reproducible and deterministic image builds | Dockerfile/config review | 2 | 2 | L1–L4 | COVERED |

| M03 — Reproducible and deterministic image builds | incident/troubleshooting | 2 | 2 | L1–L4 | COVERED |

| M03 — Reproducible and deterministic image builds | additional design | 1 | 1 | L4 Expert | COVERED |

| M04 — Build caching, BuildKit, and build performance | short answer | 4 | 4 | L1–L4 | COVERED |

| M04 — Build caching, BuildKit, and build performance | MCQ | 3 | 3 | L1–L4 | COVERED |

| M04 — Build caching, BuildKit, and build performance | command/output interpretation | 3 | 3 | L1–L4 | COVERED |

| M04 — Build caching, BuildKit, and build performance | Dockerfile/config review | 2 | 2 | L1–L4 | COVERED |

| M04 — Build caching, BuildKit, and build performance | incident/troubleshooting | 2 | 2 | L1–L4 | COVERED |

| M04 — Build caching, BuildKit, and build performance | additional design | 1 | 1 | L4 Expert | COVERED |

| M05 — Image tagging, versioning, and immutability | short answer | 4 | 4 | L1–L4 | COVERED |

| M05 — Image tagging, versioning, and immutability | MCQ | 3 | 3 | L1–L4 | COVERED |

| M05 — Image tagging, versioning, and immutability | command/output interpretation | 3 | 3 | L1–L4 | COVERED |

| M05 — Image tagging, versioning, and immutability | Dockerfile/config review | 2 | 2 | L1–L4 | COVERED |

| M05 — Image tagging, versioning, and immutability | incident/troubleshooting | 2 | 2 | L1–L4 | COVERED |

| M05 — Image tagging, versioning, and immutability | additional design | 1 | 1 | L4 Expert | COVERED |

| M06 — Container registries, mirrors, and pull-through caches | short answer | 4 | 4 | L1–L4 | COVERED |

| M06 — Container registries, mirrors, and pull-through caches | MCQ | 3 | 3 | L1–L4 | COVERED |

| M06 — Container registries, mirrors, and pull-through caches | command/output interpretation | 3 | 3 | L1–L4 | COVERED |

| M06 — Container registries, mirrors, and pull-through caches | Dockerfile/config review | 2 | 2 | L1–L4 | COVERED |

| M06 — Container registries, mirrors, and pull-through caches | incident/troubleshooting | 2 | 2 | L1–L4 | COVERED |

| M06 — Container registries, mirrors, and pull-through caches | additional design | 1 | 1 | L4 Expert | COVERED |

| M07 — Registry retention, garbage collection, and access control | short answer | 4 | 4 | L1–L4 | COVERED |

| M07 — Registry retention, garbage collection, and access control | MCQ | 3 | 3 | L1–L4 | COVERED |

| M07 — Registry retention, garbage collection, and access control | command/output interpretation | 3 | 3 | L1–L4 | COVERED |

| M07 — Registry retention, garbage collection, and access control | Dockerfile/config review | 2 | 2 | L1–L4 | COVERED |

| M07 — Registry retention, garbage collection, and access control | incident/troubleshooting | 2 | 2 | L1–L4 | COVERED |

| M07 — Registry retention, garbage collection, and access control | additional design | 1 | 1 | L4 Expert | COVERED |

| M08 — Non-root containers and runtime defaults | short answer | 4 | 4 | L1–L4 | COVERED |

| M08 — Non-root containers and runtime defaults | MCQ | 3 | 3 | L1–L4 | COVERED |

| M08 — Non-root containers and runtime defaults | command/output interpretation | 3 | 3 | L1–L4 | COVERED |

| M08 — Non-root containers and runtime defaults | Dockerfile/config review | 2 | 2 | L1–L4 | COVERED |

| M08 — Non-root containers and runtime defaults | incident/troubleshooting | 2 | 2 | L1–L4 | COVERED |

| M08 — Non-root containers and runtime defaults | additional design | 1 | 1 | L4 Expert | COVERED |

| Cross-module | integration | 15 | 15 | L4 Expert | COVERED |


**Count:** 112 core questions + 6 additional module design questions + 15 cross-module questions = **133 total**. Six whiteboard prompts refer to the six counted design questions.


## Syllabus objective coverage matrix

| Objective/topic | Question IDs |
|---|---|

| M01: build context and .dockerignore | `M01-Q001`–`M01-Q014` |

| M01: instruction ordering and cache invalidation | `M01-Q001`–`M01-Q014` |

| M01: builder/runtime separation | `M01-Q001`–`M01-Q014` |

| M01: BuildKit secrets and cache mounts | `M01-Q001`–`M01-Q014` |

| M01: image-size measurement | `M01-Q001`–`M01-Q014` |

| M01: FastAPI dependencies | `M01-Q001`–`M01-Q014` |

| M01: Go linking | `M01-Q001`–`M01-Q014` |

| M01: Java runtime dependencies | `M01-Q001`–`M01-Q014` |

| M01: pandas/pyarrow shared libraries | `M01-Q001`–`M01-Q014` |

| M01: Airflow worker image design | `M01-Q001`–`M01-Q014` |

| M02: full/slim/minimal/distroless trade-offs | `M02-Q001`–`M02-Q014` |

| M02: glibc versus musl | `M02-Q001`–`M02-Q014` |

| M02: Python native wheels | `M02-Q001`–`M02-Q014` |

| M02: CA certificates | `M02-Q001`–`M02-Q014` |

| M02: timezone and locale data | `M02-Q001`–`M02-Q014` |

| M02: numeric user metadata | `M02-Q001`–`M02-Q014` |

| M02: runtime dependency closure | `M02-Q001`–`M02-Q014` |

| M02: scanner coverage limits | `M02-Q001`–`M02-Q014` |

| M02: debuggability | `M02-Q001`–`M02-Q014` |

| M02: evidence-based base selection | `M02-Q001`–`M02-Q014` |

| M03: mutable tags versus digests | `M03-Q001`–`M03-Q015` |

| M03: base image pinning | `M03-Q001`–`M03-Q015` |

| M03: lockfiles and hashes | `M03-Q001`–`M03-Q015` |

| M03: package repository snapshots | `M03-Q001`–`M03-Q015` |

| M03: timestamps and SOURCE_DATE_EPOCH | `M03-Q001`–`M03-Q015` |

| M03: artifact versus image reproducibility | `M03-Q001`–`M03-Q015` |

| M03: hermetic/offline builds | `M03-Q001`–`M03-Q015` |

| M03: SBOM and provenance | `M03-Q001`–`M03-Q015` |

| M03: repeat-build comparison | `M03-Q001`–`M03-Q015` |

| M03: platform-specific outputs | `M03-Q001`–`M03-Q015` |

| M04: cache invalidation | `M04-Q001`–`M04-Q015` |

| M04: dependency-first copy patterns | `M04-Q001`–`M04-Q015` |

| M04: BuildKit/buildx | `M04-Q001`–`M04-Q015` |

| M04: cache mounts | `M04-Q001`–`M04-Q015` |

| M04: local/inline/registry/CI caches | `M04-Q001`–`M04-Q015` |

| M04: cache trust boundaries | `M04-Q001`–`M04-Q015` |

| M04: cold/warm/partial measurements | `M04-Q001`–`M04-Q015` |

| M04: remote builds | `M04-Q001`–`M04-Q015` |

| M04: QEMU versus native builds | `M04-Q001`–`M04-Q015` |

| M04: benchmark design | `M04-Q001`–`M04-Q015` |

| M05: mutable tags versus digests | `M05-Q001`–`M05-Q015` |

| M05: SemVer and Git SHA | `M05-Q001`–`M05-Q015` |

| M05: build metadata | `M05-Q001`–`M05-Q015` |

| M05: OCI labels | `M05-Q001`–`M05-Q015` |

| M05: multi-platform image index | `M05-Q001`–`M05-Q015` |

| M05: digest-based promotion | `M05-Q001`–`M05-Q015` |

| M05: rollback identity | `M05-Q001`–`M05-Q015` |

| M05: drift detection | `M05-Q001`–`M05-Q015` |

| M05: SBOM/provenance/signature relationships | `M05-Q001`–`M05-Q015` |

| M05: release metadata | `M05-Q001`–`M05-Q015` |

| M06: OCI Distribution concepts | `M06-Q001`–`M06-Q015` |

| M06: local Distribution registry | `M06-Q001`–`M06-Q015` |

| M06: authentication versus TLS | `M06-Q001`–`M06-Q015` |

| M06: registry mirrors | `M06-Q001`–`M06-Q015` |

| M06: pull-through cache hit/miss | `M06-Q001`–`M06-Q015` |

| M06: Docker versus containerd config | `M06-Q001`–`M06-Q015` |

| M06: hosted registry comparison | `M06-Q001`–`M06-Q015` |

| M06: capacity and HA | `M06-Q001`–`M06-Q015` |

| M06: outage behavior | `M06-Q001`–`M06-Q015` |

| M06: recovery runbooks | `M06-Q001`–`M06-Q015` |

| M07: retention policy | `M07-Q001`–`M07-Q015` |

| M07: tag deletion versus blob reachability | `M07-Q001`–`M07-Q015` |

| M07: garbage-collection sequencing | `M07-Q001`–`M07-Q015` |

| M07: in-use digest protection | `M07-Q001`–`M07-Q015` |

| M07: dry-run plans | `M07-Q001`–`M07-Q015` |

| M07: least privilege | `M07-Q001`–`M07-Q015` |

| M07: push/pull/delete separation | `M07-Q001`–`M07-Q015` |

| M07: robot/service accounts | `M07-Q001`–`M07-Q015` |

| M07: audit logs and quarantine | `M07-Q001`–`M07-Q015` |

| M07: deletion recovery | `M07-Q001`–`M07-Q015` |

| M08: UID/GID and root-in-container risk | `M08-Q001`–`M08-Q015` |

| M08: numeric USER | `M08-Q001`–`M08-Q015` |

| M08: COPY --chown | `M08-Q001`–`M08-Q015` |

| M08: read-only root filesystem | `M08-Q001`–`M08-Q015` |

| M08: writable paths and tmpfs | `M08-Q001`–`M08-Q015` |

| M08: capabilities and no-new-privileges | `M08-Q001`–`M08-Q015` |

| M08: seccomp/AppArmor concepts | `M08-Q001`–`M08-Q015` |

| M08: health checks and PID 1 | `M08-Q001`–`M08-Q015` |

| M08: rootless threat model | `M08-Q001`–`M08-Q015` |

| M08: runtime hardening conformance tests | `M08-Q001`–`M08-Q015` |

| Cross-unit release, security, performance, outage and recovery | `XMOD-Q001`–`XMOD-Q015` |


## Scoring and remediation map

| Weak area | Lesson file | Targeted retest | Evidence to collect |
|---|---|---|---|

| Multi-stage builds and layer optimization | `01-multi-stage-builds-and-layer-optimization.md` | M01-Q001–M01-Q014 plus related XMOD | Capture local evidence, document assumptions, and demonstrate a safe verification/rollback step. |

| Minimal and distroless base images | `02-minimal-and-distroless-base-images.md` | M02-Q001–M02-Q014 plus related XMOD | Capture local evidence, document assumptions, and demonstrate a safe verification/rollback step. |

| Reproducible and deterministic image builds | `03-reproducible-and-deterministic-image-builds.md` | M03-Q001–M03-Q015 plus related XMOD | Capture local evidence, document assumptions, and demonstrate a safe verification/rollback step. |

| Build caching, BuildKit, and build performance | `04-build-caching-buildkit-and-build-performance.md` | M04-Q001–M04-Q015 plus related XMOD | Capture local evidence, document assumptions, and demonstrate a safe verification/rollback step. |

| Image tagging, versioning, and immutability | `05-image-tagging-versioning-and-immutability.md` | M05-Q001–M05-Q015 plus related XMOD | Capture local evidence, document assumptions, and demonstrate a safe verification/rollback step. |

| Container registries, mirrors, and pull-through caches | `06-container-registries-mirrors-and-pull-through-caches.md` | M06-Q001–M06-Q015 plus related XMOD | Capture local evidence, document assumptions, and demonstrate a safe verification/rollback step. |

| Registry retention, garbage collection, and access control | `07-registry-retention-garbage-collection-and-access-control.md` | M07-Q001–M07-Q015 plus related XMOD | Capture local evidence, document assumptions, and demonstrate a safe verification/rollback step. |

| Non-root containers and runtime defaults | `08-non-root-containers-and-runtime-defaults.md` | M08-Q001–M08-Q015 plus related XMOD | Capture local evidence, document assumptions, and demonstrate a safe verification/rollback step. |


Remediate critical security misconceptions first, then repeat the module set, then retake related integration questions. Exact lesson section anchors must be checked against the final repository.


## Appendix A — Claim and Source Register

| ID | Question ID(s) | Claim/topic | Official source document + section/title | Confidence | Tag |
|---|---|---|---|---|---|

| SRC-01 | Relevant module set; see objective matrix | Build context and `.dockerignore` | Dockerfile reference — build context and `.dockerignore` | Medium | none |

| SRC-02 | Relevant module set; see objective matrix | Instruction cache behavior | Docker build documentation — cache invalidation | Medium | [VERIFY] |

| SRC-03 | Relevant module set; see objective matrix | Multi-stage builds | Dockerfile reference — multi-stage builds | Medium | none |

| SRC-04 | Relevant module set; see objective matrix | BuildKit secrets | Docker Build documentation — build secrets | Medium | none |

| SRC-05 | Relevant module set; see objective matrix | Cache mounts | Docker Build documentation — cache mounts | Medium | [VERIFY] |

| SRC-06 | Relevant module set; see objective matrix | Image inspect | Docker CLI reference — `docker image inspect` | Medium | none |

| SRC-07 | Relevant module set; see objective matrix | Digest pinning | OCI image-spec — descriptors and digests | Medium | none |

| SRC-08 | Relevant module set; see objective matrix | glibc/musl compatibility | Python packaging documentation — platform compatibility; base-image vendor documentation | Medium | [VERIFY] |

| SRC-09 | Relevant module set; see objective matrix | CA trust | Base-image/vendor documentation — CA certificates | Medium | [VERIFY] |

| SRC-10 | Relevant module set; see objective matrix | Distroless contents | Distroless project documentation — image contents and debugging | Medium | none |

| SRC-11 | Relevant module set; see objective matrix | SBOM generation | Syft documentation — SBOM generation and formats | Medium | none |

| SRC-12 | Relevant module set; see objective matrix | Vulnerability scanning | Trivy documentation — scanning and vulnerability database | Medium | none |

| SRC-13 | Relevant module set; see objective matrix | Reproducible timestamps | Reproducible Builds documentation — `SOURCE_DATE_EPOCH` | Medium | none |

| SRC-14 | Relevant module set; see objective matrix | Python package hashes | Python packaging/pip documentation — hash-checking mode | Medium | none |

| SRC-15 | Relevant module set; see objective matrix | Registry configuration | CNCF Distribution documentation — configuration and storage | Medium | [VERIFY] |

| SRC-16 | Relevant module set; see objective matrix | Distribution API | OCI Distribution Specification — API endpoints and content | Medium | none |

| SRC-17 | Relevant module set; see objective matrix | Tag and digest | OCI image-spec — descriptors and digests | Medium | none |

| SRC-18 | Relevant module set; see objective matrix | Image index | OCI image-spec — image index | Medium | none |

| SRC-19 | Relevant module set; see objective matrix | Multi-platform builds | Docker Buildx documentation — multi-platform builds | Medium | none |

| SRC-20 | Relevant module set; see objective matrix | QEMU emulation | Docker documentation — multi-platform builds and emulation | Medium | [VERIFY] |

| SRC-21 | Relevant module set; see objective matrix | Cache backends | Docker Buildx documentation — cache backends | Medium | [VERIFY] |

| SRC-22 | Relevant module set; see objective matrix | Remote cache trust | BuildKit documentation — cache import/export | Medium | [VERIFY] |

| SRC-23 | Relevant module set; see objective matrix | Registry TLS | Docker Engine documentation — registry certificates and security | Medium | [VERIFY] |

| SRC-24 | Relevant module set; see objective matrix | Registry authentication | CNCF Distribution documentation — authentication | Medium | [VERIFY] |

| SRC-25 | Relevant module set; see objective matrix | containerd registry config | containerd documentation — registry hosts configuration | Medium | [VERIFY] |

| SRC-26 | Relevant module set; see objective matrix | Pull-through cache | CNCF Distribution documentation — pull-through cache | Medium | [VERIFY] |

| SRC-27 | Relevant module set; see objective matrix | Garbage collection | CNCF Distribution documentation — garbage collection | Medium | [VERIFY] |

| SRC-28 | Relevant module set; see objective matrix | Repository permissions | Registry product documentation — repository permissions and robot accounts | Medium | none |

| SRC-29 | Relevant module set; see objective matrix | Retention | Registry product documentation — retention and cleanup | Medium | [VERIFY] |

| SRC-30 | Relevant module set; see objective matrix | Non-root identity | Dockerfile reference — `USER`; Docker Engine security documentation | Medium | none |

| SRC-31 | Relevant module set; see objective matrix | COPY ownership | Dockerfile reference — `COPY --chown` | Medium | none |

| SRC-32 | Relevant module set; see objective matrix | Read-only filesystem | Docker run reference — read-only filesystem options | Medium | none |

| SRC-33 | Relevant module set; see objective matrix | Linux capabilities | Linux capabilities man page; Docker run security options | Medium | none |

| SRC-34 | Relevant module set; see objective matrix | No-new-privileges | Docker run security options — `no-new-privileges` | Medium | none |

| SRC-35 | Relevant module set; see objective matrix | Seccomp | Docker Engine security — seccomp | Medium | [VERIFY] |

| SRC-36 | Relevant module set; see objective matrix | AppArmor | Docker Engine security — AppArmor | Medium | [VERIFY] |

| SRC-37 | Relevant module set; see objective matrix | PID 1 and signals | Docker run documentation — init, stop signal and exec form | Medium | none |

| SRC-38 | Relevant module set; see objective matrix | Rootless mode | Docker Engine documentation — rootless mode | Medium | [VERIFY] |

| SRC-39 | Relevant module set; see objective matrix | Kubernetes security context | Kubernetes documentation — security context | Medium | [VERIFY] |

| SRC-40 | Relevant module set; see objective matrix | Resource limits | Docker run reference — CPU, memory and PID limits | Medium | [VERIFY] |

| SRC-41 | Relevant module set; see objective matrix | Container security guidance | NIST SP 800-190 — Application Container Security Guide | Medium | none |

| SRC-42 | Relevant module set; see objective matrix | Benchmark guidance | CIS Docker Benchmark — container and daemon recommendations | Medium | none |

| SRC-43 | Relevant module set; see objective matrix | Build provenance | SLSA specification — provenance | Medium | none |


## Appendix B — Audit Report

| Pass | Result (PASS/FIXED/OPEN) | Defects found | Fixes applied | Residual risk |
|---|---|---|---|---|
| 1 — Source and scope fidelity | FIXED | Repository tree was available; destination tree is not mounted. | Kept the eight specified modules in order and used the supplied syllabus as coverage contract. | Exact repository destination must be verified before copying. |
| 2 — Count and distribution | PASS | Counts can drift after manual edits. | Generated 112 core, 6 design and 15 integration questions. | Re-run ID/type validation after edits. |
| 3 — Metadata completeness | FIXED | Types need different scoring and answer structures. | Every question has metadata; MCQs include three distractors with explanations. | Human editorial check remains necessary. |
| 4 — Technical correctness | OPEN | Runtime and tool behavior can be version-sensitive. | Named official sources and marked verification needs. | No live documentation review or command execution performed. |
| 5 — Security and SRE review | FIXED | Risks include mutable tags, cache trust, broad privileges and unsafe deletion. | Answers emphasize least privilege, evidence, digest identity and reversible mitigation. | Local policy and registry-specific behavior need review. |
| 6 — Pedagogy and fairness | FIXED | Some wording may not exactly match final lesson sections. | L1–L4 progression, practical scenarios, partial credit and alternative-valid design rubrics included. | Times are illustrative. |
| 7 — Answer-key consistency | OPEN | Automated generation cannot replace independent review. | Answers align with question intent and rubrics are explicit. | Independent human answer-key audit remains open. |
| 8 — Coverage and traceability | FIXED | Objective-to-question mapping is broad by module rather than exact lesson heading. | Every listed topic maps to its module set; integration topics map to XMOD IDs. | Verify exact final lesson headings. |
| 9 — Adversarial staff review | FIXED | Likely objections: tag/digest confusion, cache as provenance, scan as proof, distroless as secure by definition, rootless as universal defense, GC semantics, one-platform testing and unmeasured benchmarks. | Those objections are covered in questions and answers. | Implementation-specific claims need current source review. |
| 10 — Integrity and usability | FIXED | Long files can accumulate duplicate IDs and stale matrices. | Added stable IDs, index, matrices and appendices. | Run fresh parser after any edit. |

## Appendix C — Human Verification Checklist

### Docker / BuildKit
- [ ] **Check:** `COPY --chown`, secret mounts, cache mounts, build context and cache behavior against installed versions.
  - **Official source:** Dockerfile reference and BuildKit documentation.
  - **Safe local check:** `docker version`; `docker buildx version`; inspect a harmless local build log.
  - **Evidence to close:** versioned notes and saved local output.

### OCI / Distribution
- [ ] **Check:** tag deletion, blob reachability, GC sequence and pull-through cache behavior.
  - **Official source:** OCI Image Specification, OCI Distribution Specification and CNCF Distribution docs.
  - **Safe local check:** use only a disposable local registry and test repository; do not run deletion/GC against production.
  - **Evidence to close:** configuration, preflight inventory, documented sequence and post-operation pull test.

### Trivy / Syft
- [ ] **Check:** scanner database state, SBOM format and coverage limitations.
  - **Official source:** Trivy and Syft official documentation.
  - **Safe local check:** run only if installed; capture version and database metadata.
  - **Evidence to close:** sanitized output plus explicit scope and limitations.

### Registry products
- [ ] **Check:** current pricing, quotas, retention, immutability, service-account and audit features for Docker Hub, GHCR, ECR, GCR/Artifact Registry, ACR and Harbor.
  - **Official source:** each product's current official docs/pricing pages.
  - **Safe local check:** no paid account required; mark changing values `[VERIFY]`.
  - **Evidence to close:** dated comparison with plan/region and official references.

### containerd / Kubernetes
- [ ] **Check:** actual node pull client and supported registry/security-context fields.
  - **Official source:** containerd documentation and Kubernetes security-context documentation.
  - **Safe local check:** inspect local runtime/cluster version; do not assume Docker daemon configuration applies.
  - **Evidence to close:** versioned configuration and a nonproduction pull/security-context test.

### Other sources
- [ ] **Check:** exact NIST SP 800-190, CIS Docker Benchmark and SLSA wording before citing recommendations.
  - **Official source:** official NIST, CIS and SLSA publications.
  - **Safe local check:** consult exact version and section title; do not infer section numbers.
  - **Evidence to close:** document version/date and section title.

## Appendix D — Known Limitations and Assumptions

- The supplied prompt and a Roadmap project-tree file were found in the user's Library. The tree establishes the Stage 2E module path and target filename.
- Lesson files were found in the Library for several units, but a full line-by-line comparison of all eight lessons was not completed. Align terminology and exact lesson headings before using this as a formal exam.
- The repository working tree and destination directory were not mounted. This is a standalone artifact; no repository file was changed.
- External documentation was not consulted live. Appendix A names official sources to verify; prices, quotas, flags, defaults and product behavior may change.
- No Docker commands, scanner runs, registry operations or labs were executed. Scenario values and time estimates are illustrative; no benchmark is claimed as measured.
- Exact behavior depends on Docker/BuildKit/buildx, registry implementation, operating system, architecture, scanner database and runtime versions.

## Appendix E — Sign-off


`Content status: DRAFT-AUDITED | Audit date: 2026-10-24 | Auditor role: AI self-audit (requires human verification) | Total questions: 133 | Unverified items: 51`


An AI self-audit does not replace human review, running the labs, or verifying version-sensitive claims against current official documentation.
