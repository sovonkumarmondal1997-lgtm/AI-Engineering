# M09 — Secrets and Identity Management: Practice Questions

> **Purpose.** An answer-inclusive, offline-capable assessment bank for M09 Units 1–8. It is designed for a data/AI engineer with prior Git, CI, container, Kubernetes/RBAC, TLS/network policy, Helm/GitOps, IaC, and platform-operations foundations.
>
> **Safety.** All examples are synthetic. Never paste a real secret into an exercise, issue, chat, or output. Do not test a suspected credential against a live third-party service. Cloud and managed-host behavior is awareness-only unless explicitly verified for the exact host/version. `[ILLUSTRATIVE]` means representative sample data; `[ASSUMPTION]` means a design assumption; `[SIMULATION]` means local/mock behavior; `[VERIFY]` means check current official docs before applying the claim to a real environment.

## How to use this question bank

1. Answer each question before reading its model answer. Answers are adjacent so this file works offline.
2. Treat command/config fragments as review examples, not copy/paste production configuration. Confirm exact schemas, flags, defaults, and version behavior against the installed release.
3. For incidents, use the ordered sequence **diagnose → blast-radius/revocation check → contain → scope → eradicate → recover → prevent**. If a credential may still be valid and compromise is credible, revoke/rotate before Git-history cleanup.
4. Use only throwaway values such as `FAKE_LAB_SECRET_DO_NOT_USE_7f31`; never use a real cloud account or live identity.
5. Give yourself partial credit only where your answer states assumptions, evidence, failure modes, and a safe verification plan. Alternative designs can earn full credit if they satisfy the stated constraints.
6. Record weak objectives, not just total scores. A high quiz score is not proof of production readiness; practical drills, code review, incident judgment, and supervised operational experience are also required.

## Coverage map and question-count ledger

Each unit contains 18 unique questions: Q01–Q03 short answer; Q04–Q06 MCQ; Q07–Q09 output interpretation; Q10–Q11 config review; Q12–Q13 incident/troubleshooting; Q14 design; Q15 hands-on; Q16 boundary test; Q17 evidence reasoning; Q18 operational trade-off. Cross-unit scenarios are independently numbered and each combines at least two units.

| Section | Required minimum | Planned/actual IDs |
|---|---:|---|
| Unit U01 — Secrets threat model and lifecycle | 18 | `M09-U01-Q01`–`M09-U01-Q18` |
| Unit U02 — HashiCorp Vault architecture and auth methods | 18 | `M09-U02-Q01`–`M09-U02-Q18` |
| Unit U03 — Dynamic secrets, leases, and rotation | 18 | `M09-U03-Q01`–`M09-U03-Q18` |
| Unit U04 — External Secrets Operator and cloud secret managers | 18 | `M09-U04-Q01`–`M09-U04-Q18` |
| Unit U05 — SOPS, Sealed Secrets, and encrypted secrets in Git | 18 | `M09-U05-Q01`–`M09-U05-Q18` |
| Unit U06 — Kubernetes Secret encryption and the CSI Secret Store | 18 | `M09-U06-Q01`–`M09-U06-Q18` |
| Unit U07 — Workload identity, IRSA, and federated credentials | 18 | `M09-U07-Q01`–`M09-U07-Q18` |
| Unit U08 — Secret leak detection and incident response | 18 | `M09-U08-Q01`–`M09-U08-Q18` |
| Cross-unit integration | 32 minimum; 38 included | `M09-XI-001`–`M09-XI-038` |
| **Total** | **176 minimum** | **182 unique questions: 8 × 18 + 38** |

**Count policy:** each numbered ID is one question. Subparts and MCQ distractors are not counted separately. The ledger is reconciled against the explicit ID ranges above and the 38 separately numbered integration scenarios below.

## Scoring and remediation policy

These are the **course assessment bands**, not a universal industry standard:

- **80% or higher:** proceed to the next unit or capstone activity.
- **60–79%:** remediate weak objectives and retry targeted questions.
- **Below 60%:** repeat the relevant unit's core learning material and retake a different question subset.

### Scoring by question type

- **Short answer:** factual correctness, reasoning, and security/operational implications.
- **MCQ:** correct choice plus understanding of all three distractors; partial credit is available only where the rubric says so.
- **Output/config interpretation:** evidence reading, diagnosis, consequence, and verification.
- **Config review:** defects identified, impact, corrected design, tests, and safety.
- **Incident:** triage, containment, blast-radius/revocation, scope, recovery, prevention, and evidence handling.
- **Design:** weighted trade-offs, failure modes, least privilege, operability, recovery, evidence, and accountable ownership.

### Per-unit score sheet

| Unit | Score | Weak objectives / lesson to revisit |
|---|---:|---|
| U01 — Secrets threat model and lifecycle | ____ / ____ | See `01-secrets-threat-model-and-lifecycle.md` |
| U02 — HashiCorp Vault architecture and auth methods | ____ / ____ | See `02-hashicorp-vault-architecture-and-auth-methods.md` |
| U03 — Dynamic secrets, leases, and rotation | ____ / ____ | See `03-dynamic-secrets-leases-and-rotation.md` |
| U04 — External Secrets Operator and cloud secret managers | ____ / ____ | See `04-external-secrets-operator-and-cloud-secret-managers.md` |
| U05 — SOPS, Sealed Secrets, and encrypted secrets in Git | ____ / ____ | See `05-sops-sealed-secrets-and-encrypted-secrets-in-git.md` |
| U06 — Kubernetes Secret encryption and the CSI Secret Store | ____ / ____ | See `06-kubernetes-secret-encryption-and-csi-secret-store.md` |
| U07 — Workload identity, IRSA, and federated credentials | ____ / ____ | See `07-workload-identity-irsa-and-federated-credentials.md` |
| U08 — Secret leak detection and incident response | ____ / ____ | See `08-secret-leak-detection-and-incident-response.md` |
| Cross-unit integration | ____ / ____ | Revisit all linked units; see scenario IDs |

### Remediation map

| Common error | Remediate in unit | Lesson file |
|---|---|---|
| Treating Base64 or encrypted Git as proof that a live credential is safe | U01, U05, U06, U08 | `01-secrets-threat-model-and-lifecycle.md`; `05-sops-sealed-secrets-and-encrypted-secrets-in-git.md`; `06-kubernetes-secret-encryption-and-csi-secret-store.md`; `08-secret-leak-detection-and-incident-response.md` |
| Confusing authentication failure with authorization denial | U02, U07 | `02-hashicorp-vault-architecture-and-auth-methods.md`; `07-workload-identity-irsa-and-federated-credentials.md` |
| Ignoring lease expiry, client pools, or job duration | U03, U04 | `03-dynamic-secrets-leases-and-rotation.md`; `04-external-secrets-operator-and-cloud-secret-managers.md` |
| Assuming provider rotation automatically reloads an application | U04, U06 | `04-external-secrets-operator-and-cloud-secret-managers.md`; `06-kubernetes-secret-encryption-and-csi-secret-store.md` |
| Treating history rewrite as containment | U01, U05, U08 | `01-secrets-threat-model-and-lifecycle.md`; `05-sops-sealed-secrets-and-encrypted-secrets-in-git.md`; `08-secret-leak-detection-and-incident-response.md` |
| Accepting JWT based only on successful signature verification | U02, U07 | `02-hashicorp-vault-architecture-and-auth-methods.md`; `07-workload-identity-irsa-and-federated-credentials.md` |
| Assuming a green scanner covers history, logs, images, and artifacts | U08 | `08-secret-leak-detection-and-incident-response.md` |
| Broad wildcard access or missing negative tests | U02, U04, U06, U07 | Relevant unit lesson listed above |

### Spaced repetition and retest

Retest weak questions after 1 day, 1 week, and 3–4 weeks. Use a different question subset and change at least one boundary condition (identity, audience, TTL, namespace, artifact surface, or outage). For incident questions, verbally state the first action and why. For designs, ask a peer to challenge failure modes and recovery.

### Design-review rubric (100 points)

- Correctness and scope fit: 20
- Least privilege and trust boundaries: 20
- Blast-radius control and revocation: 15
- Failure handling and recovery: 15
- Verification, negative tests, and evidence: 15
- Auditability, ownership, and operations: 10
- Assumptions/version caveats and communication: 5

A quiz score alone does not establish production readiness. Production readiness requires validated configurations, observable operations, recovery exercises, safe incident practice, and review by authorized owners.

## Unit 1 — Secrets threat model and lifecycle

### M09-U01-Q01 — short answer

- **Level:** L1
- **Type:** short answer
- **Objective tested:** classify credentials, private keys, session tokens, and sensitive connection strings separately from public configuration
- **Estimated time:** [ILLUSTRATIVE] 6 minutes
- **Question / context:** Explain **secret classification** for a small data/AI platform. State the key boundary, the principal failure mode, and one control that reduces risk. Use a synthetic service credential; assume no cloud account is available.
- **Expected answer / model solution:** A strong answer should classify credentials, private keys, session tokens, and sensitive connection strings separately from public configuration; identify the boundary where exposure or misuse can occur; state who can use the credential and for what; and pair prevention with detection/recovery. The practical check is to trace the relevant evidence and test the control in a disposable local environment. Do not infer that a secret is safe merely because it is not visible in the current source file.
- **Common wrong answers:** Saying only “put it in a secret manager” misses consumers, permissions, logs, copies, expiry, and recovery. Treating an absence of findings as proof of no exposure is also unsupported.
- **Scoring rubric:** 4 points: concept 1; boundary/threat 1; actionable control 1; verification/evidence 1. Partial credit for a defensible alternative with explicit assumptions.
- **Safety/version note:** None beyond the synthetic/offline assumptions stated in this question.

### M09-U01-Q02 — short answer

- **Level:** L1
- **Type:** short answer
- **Objective tested:** map creation, storage, distribution, use, rotation, revocation, archival, and destruction
- **Estimated time:** [ILLUSTRATIVE] 7 minutes
- **Question / context:** Explain **lifecycle controls** for a small data/AI platform. State the key boundary, the principal failure mode, and one control that reduces risk. Use a synthetic service credential; assume no cloud account is available.
- **Expected answer / model solution:** A strong answer should map creation, storage, distribution, use, rotation, revocation, archival, and destruction; identify the boundary where exposure or misuse can occur; state who can use the credential and for what; and pair prevention with detection/recovery. The practical check is to trace the relevant evidence and test the control in a disposable local environment. Do not infer that a secret is safe merely because it is not visible in the current source file.
- **Common wrong answers:** Saying only “put it in a secret manager” misses consumers, permissions, logs, copies, expiry, and recovery. Treating an absence of findings as proof of no exposure is also unsupported.
- **Scoring rubric:** 4 points: concept 1; boundary/threat 1; actionable control 1; verification/evidence 1. Partial credit for a defensible alternative with explicit assumptions.
- **Safety/version note:** None beyond the synthetic/offline assumptions stated in this question.

### M09-U01-Q03 — short answer

- **Level:** L1
- **Type:** short answer
- **Objective tested:** trace source → build → deploy → runtime → logs/artifacts, including notebooks, shell history, backups, and container layers
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Explain **exposure tracing** for a small data/AI platform. State the key boundary, the principal failure mode, and one control that reduces risk. Use a synthetic service credential; assume no cloud account is available.
- **Expected answer / model solution:** A strong answer should trace source → build → deploy → runtime → logs/artifacts, including notebooks, shell history, backups, and container layers; identify the boundary where exposure or misuse can occur; state who can use the credential and for what; and pair prevention with detection/recovery. The practical check is to trace the relevant evidence and test the control in a disposable local environment. Do not infer that a secret is safe merely because it is not visible in the current source file.
- **Common wrong answers:** Saying only “put it in a secret manager” misses consumers, permissions, logs, copies, expiry, and recovery. Treating an absence of findings as proof of no exposure is also unsupported.
- **Scoring rubric:** 4 points: concept 1; boundary/threat 1; actionable control 1; verification/evidence 1. Partial credit for a defensible alternative with explicit assumptions.
- **Safety/version note:** None beyond the synthetic/offline assumptions stated in this question.

### M09-U01-Q04 — MCQ

- **Level:** L1
- **Type:** MCQ
- **Objective tested:** record owner, issuer/source, consumers, scope, expiry/rotation, storage locations, audit source, and runbook
- **Estimated time:** [ILLUSTRATIVE] 4 minutes
- **Question / context:** Which response best addresses **inventory and ownership**? Choose one. [ILLUSTRATIVE] The environment is a disposable local lab and the credential is synthetic.

A. Map the complete inventory and ownership path, restrict access to the minimum consumer, and verify the boundary with a negative test.
B. Rely on a naming convention and assume any component with the same project label is trusted.
C. Delete the visible value immediately and skip revocation, dependency discovery, and audit review.
D. Accept the configuration because the happy path works; do not test forbidden access.
- **Expected answer / model solution:** **Correct: A.** It directly addresses inventory and ownership and includes a verifiable boundary rather than relying on naming or a single successful request. **B is wrong** because labels/names do not enforce authorization. **C is incomplete** because deleting a copy does not necessarily invalidate a live credential or scope other copies. **D is wrong** because positive tests do not establish least privilege; negative tests are required.
- **Common wrong answers:** Choosing B confuses convention with enforcement. Choosing C mistakes cleanup for containment. Choosing D proves only one permitted path and leaves unauthorized access untested.
- **Scoring rubric:** 4 points: correct option 1; explain A 1; explain why B/C/D fail 2. Partial credit for identifying the key boundary even with a wrong choice.
- **Safety/version note:** Any product-specific commands or fields are [VERIFY] for the exact version; this is a concept question, not proof of product behavior.

### M09-U01-Q05 — MCQ

- **Level:** L2
- **Type:** MCQ
- **Objective tested:** compare lifetime, blast radius, revocation, operational complexity, and dependency requirements
- **Estimated time:** [ILLUSTRATIVE] 4 minutes
- **Question / context:** Which response best addresses **static versus dynamic credentials**? Choose one. [ILLUSTRATIVE] The environment is a disposable local lab and the credential is synthetic.

A. Use a narrowly scoped identity/policy and inspect the relevant audit/operational evidence before concluding.
B. Rely on a naming convention and assume any component with the same project label is trusted.
C. Delete the visible value immediately and skip revocation, dependency discovery, and audit review.
D. Accept the configuration because the happy path works; do not test forbidden access.
- **Expected answer / model solution:** **Correct: A.** It directly addresses static versus dynamic credentials and includes a verifiable boundary rather than relying on naming or a single successful request. **B is wrong** because labels/names do not enforce authorization. **C is incomplete** because deleting a copy does not necessarily invalidate a live credential or scope other copies. **D is wrong** because positive tests do not establish least privilege; negative tests are required.
- **Common wrong answers:** Choosing B confuses convention with enforcement. Choosing C mistakes cleanup for containment. Choosing D proves only one permitted path and leaves unauthorized access untested.
- **Scoring rubric:** 4 points: correct option 1; explain A 1; explain why B/C/D fail 2. Partial credit for identifying the key boundary even with a wrong choice.
- **Safety/version note:** Any product-specific commands or fields are [VERIFY] for the exact version; this is a concept question, not proof of product behavior.

### M09-U01-Q06 — MCQ

- **Level:** L2
- **Type:** MCQ
- **Objective tested:** explain why Base64 is reversible encoding and not confidentiality protection
- **Estimated time:** [ILLUSTRATIVE] 4 minutes
- **Question / context:** Which response best addresses **encoding versus encryption**? Choose one. [ILLUSTRATIVE] The environment is a disposable local lab and the credential is synthetic.

A. Treat the observed representation as insufficient proof of confidentiality; validate the actual protection boundary and test access.
B. Rely on a naming convention and assume any component with the same project label is trusted.
C. Delete the visible value immediately and skip revocation, dependency discovery, and audit review.
D. Accept the configuration because the happy path works; do not test forbidden access.
- **Expected answer / model solution:** **Correct: A.** It directly addresses encoding versus encryption and includes a verifiable boundary rather than relying on naming or a single successful request. **B is wrong** because labels/names do not enforce authorization. **C is incomplete** because deleting a copy does not necessarily invalidate a live credential or scope other copies. **D is wrong** because positive tests do not establish least privilege; negative tests are required.
- **Common wrong answers:** Choosing B confuses convention with enforcement. Choosing C mistakes cleanup for containment. Choosing D proves only one permitted path and leaves unauthorized access untested.
- **Scoring rubric:** 4 points: correct option 1; explain A 1; explain why B/C/D fail 2. Partial credit for identifying the key boundary even with a wrong choice.
- **Safety/version note:** Any product-specific commands or fields are [VERIFY] for the exact version; this is a concept question, not proof of product behavior.

### M09-U01-Q07 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** identify actors, boundaries, abuse cases, allowed operations, and blast-radius controls
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Interpret this representative output and propose the next two verification steps:

```text
[ILLUSTRATIVE] inventory row: owner=unknown; source=CI variable; consumers=etl-worker, notebook-job; expiry=none; last_seen=build-log; audit_source=missing
```
Do not assume omitted fields are healthy.
- **Expected answer / model solution:** The inventory is incomplete and signals high uncertainty: owner, expiry, audit source, and lifecycle runbook are missing. Treat the build-log appearance as an exposure, identify the exact synthetic credential and privileges, notify the accountable incident owner, rotate/revoke if it could be live, then trace consumers and artifacts.
- **Common wrong answers:** Declaring success from one green field is insufficient. For identity, do not stop at signature validity; for freshness, do not equate source update with process adoption; for inventory, do not treat unknown ownership as a reason to delay escalation.
- **Scoring rubric:** 5 points: interpret evidence 2; identify missing evidence 1; safe next steps 1; verification criteria 1.
- **Safety/version note:** Output is synthetic and [ILLUSTRATIVE], not captured from a live product.

### M09-U01-Q08 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** prioritize by privilege, exposure, validity, reachability, duration, and business impact
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Interpret this representative output and propose the next two verification steps:

```text
[ILLUSTRATIVE] verifier result: signature=valid; issuer=expected; audience=unexpected-api; subject=repo:demo/project:ref:refs/heads/feature; exp=in-future; policy=role expects refs/heads/main
```
Do not assume omitted fields are healthy.
- **Expected answer / model solution:** The token should be rejected by the stated verifier/role constraints despite a valid signature: audience and subject/ref do not match. Signature validity alone does not prove intended audience or authorization. Check issuer, key/JWKS, time claims, audience, subject, then resulting policy separately.
- **Common wrong answers:** Declaring success from one green field is insufficient. For identity, do not stop at signature validity; for freshness, do not equate source update with process adoption; for inventory, do not treat unknown ownership as a reason to delay escalation.
- **Scoring rubric:** 5 points: interpret evidence 2; identify missing evidence 1; safe next steps 1; verification criteria 1.
- **Safety/version note:** Output is synthetic and [ILLUSTRATIVE], not captured from a live product.

### M09-U01-Q09 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** evaluate environment variables, mounted files, process access, logs, and crash dumps
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Interpret this representative output and propose the next two verification steps:

```text
[ILLUSTRATIVE] rollout evidence: provider_version=v8; mounted_file_version=v8; process_started_at=09:00; process_loaded_version=v7; env_source=process-start
```
Do not assume omitted fields are healthy.
- **Expected answer / model solution:** The source and mounted file are current but the process still uses a previously loaded value. Determine whether the app reads a file dynamically or loads a value at startup; trigger a controlled reload/restart only after a safe rollout plan, then verify the app actually adopted v8.
- **Common wrong answers:** Declaring success from one green field is insufficient. For identity, do not stop at signature validity; for freshness, do not equate source update with process adoption; for inventory, do not treat unknown ownership as a reason to delay escalation.
- **Scoring rubric:** 5 points: interpret evidence 2; identify missing evidence 1; safe next steps 1; verification criteria 1.
- **Safety/version note:** Output is synthetic and [ILLUSTRATIVE], not captured from a live product.

### M09-U01-Q10 — config review

- **Level:** L2
- **Type:** config review
- **Objective tested:** distinguish planned replacement from immediate invalidation after compromise
- **Estimated time:** [ILLUSTRATIVE] 12 minutes
- **Question / context:** Review the synthetic configuration for **rotation and revocation**. Find at least three defects, explain impact, provide exact conceptual fixes, and state a verification test.

```yaml
# [ILLUSTRATIVE] unsafe example
secret_value: "FAKE_DO_NOT_USE_7f31"
read_all_paths: true
audit_enabled: false
owner: ""
ttl: "never"
```
- **Expected answer / model solution:** Defects to identify: (1) the fake credential is embedded directly in configuration; replace it with a reference/injection from the approved secret source and ensure it never enters committed files or logs; (2) broad access (`read_all_paths` / wildcard allow) violates least privilege; narrow to the exact required path/actions; (3) audit disabled or failure ignored removes important evidence and can conceal outages; enable and monitor appropriate audit/reconciliation evidence; (4) missing owner or shared namespace boundary prevents accountability and can permit cross-tenant access; define owner and enforce scope; (5) unbounded/disabled TTL or refresh policy can leave stale credentials; set lifecycle behavior appropriate to workload and monitor expiry; (6) no forbidden-access test means the policy is unproven. Verification: positive test for the intended consumer, negative test for a neighboring identity/path, review emitted audit/conditions, and ensure the synthetic value is absent from repository history/artifacts.
- **Common wrong answers:** Only changing the fake value is not enough. Broad permissions cannot be justified by a successful happy path. Enabling a feature without testing its effective behavior is not verification. A TTL must be compatible with consumer refresh and job duration.
- **Scoring rubric:** 8 points: identify defects 3; impact/fix 3; positive and negative verification 2. Partial credit for equivalent safe corrections.
- **Safety/version note:** Illustrative pseudo-configuration, not a valid product schema. Any exact fields/commands are [VERIFY] for the named version.

### M09-U01-Q11 — config review

- **Level:** L2
- **Type:** config review
- **Objective tested:** handle tickets, chat, SaaS, and external support bundles without reproducing a secret
- **Estimated time:** [ILLUSTRATIVE] 12 minutes
- **Question / context:** Review the synthetic configuration for **third-party and collaboration surfaces**. Find at least three defects, explain impact, provide exact conceptual fixes, and state a verification test.

```yaml
# [ILLUSTRATIVE] unsafe example
allow:
  - "*"
refresh: "disabled"
on_failure: "ignore"
namespace_boundary: "shared"
test_forbidden_access: false
```
- **Expected answer / model solution:** Defects to identify: (1) the fake credential is embedded directly in configuration; replace it with a reference/injection from the approved secret source and ensure it never enters committed files or logs; (2) broad access (`read_all_paths` / wildcard allow) violates least privilege; narrow to the exact required path/actions; (3) audit disabled or failure ignored removes important evidence and can conceal outages; enable and monitor appropriate audit/reconciliation evidence; (4) missing owner or shared namespace boundary prevents accountability and can permit cross-tenant access; define owner and enforce scope; (5) unbounded/disabled TTL or refresh policy can leave stale credentials; set lifecycle behavior appropriate to workload and monitor expiry; (6) no forbidden-access test means the policy is unproven. Verification: positive test for the intended consumer, negative test for a neighboring identity/path, review emitted audit/conditions, and ensure the synthetic value is absent from repository history/artifacts.
- **Common wrong answers:** Only changing the fake value is not enough. Broad permissions cannot be justified by a successful happy path. Enabling a feature without testing its effective behavior is not verification. A TTL must be compatible with consumer refresh and job duration.
- **Scoring rubric:** 8 points: identify defects 3; impact/fix 3; positive and negative verification 2. Partial credit for equivalent safe corrections.
- **Safety/version note:** Illustrative pseudo-configuration, not a valid product schema. Any exact fields/commands are [VERIFY] for the named version.

### M09-U01-Q12 — incident/troubleshooting

- **Level:** L3
- **Type:** incident/troubleshooting
- **Objective tested:** assess old backups, registry layers, CI artifacts, and clones as residual exposure
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** Incident: an alert indicates a possible failure or exposure involving **backup and artifact retention**. The service is important but the evidence is incomplete; only synthetic logs are available in the exercise. Give an ordered response using diagnose → blast-radius/revocation check → contain → scope → eradicate → recover → prevent. Identify the first action and why.
- **Expected answer / model solution:** First preserve the alert/event identifiers and time window without copying the credential into chat or a ticket. Quickly determine credential type, privilege, validity, consumers, and whether safe immediate revocation/rotation is warranted; when compromise is credible and the credential may still be valid, invalidate/rotate before Git or artifact cleanup. Contain affected identities/paths, scope access using audit logs and deployment/artifact metadata, clean exposed copies as hygiene, restore with a known-good credential and controlled rollout, verify the old credential fails through an authorized test, then add missing inventory, detector, owner, and runbook controls. If evidence is insufficient, state uncertainty and escalate rather than inventing facts.
- **Common wrong answers:** Purging files first delays containment. Restarting everything without mapping dependencies may cause avoidable outage. Deleting evidence or pasting the secret into a ticket destroys safety and investigation quality.
- **Scoring rubric:** 8 points: first action/rationale 1; blast radius and revocation 2; scope/evidence 1; recovery/verification 2; prevention/ownership 1; safe uncertainty 1.
- **Safety/version note:** Synthetic incident only; do not validate a credential against a live third-party service.

### M09-U01-Q13 — incident/troubleshooting

- **Level:** L3
- **Type:** incident/troubleshooting
- **Objective tested:** map service accounts, CI jobs, workloads, and automation identities to credentials and permissions
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** Incident: an alert indicates a possible failure or exposure involving **non-human identities**. The service is important but the evidence is incomplete; only synthetic logs are available in the exercise. Give an ordered response using diagnose → blast-radius/revocation check → contain → scope → eradicate → recover → prevent. Identify the first action and why.
- **Expected answer / model solution:** First preserve the alert/event identifiers and time window without copying the credential into chat or a ticket. Quickly determine credential type, privilege, validity, consumers, and whether safe immediate revocation/rotation is warranted; when compromise is credible and the credential may still be valid, invalidate/rotate before Git or artifact cleanup. Contain affected identities/paths, scope access using audit logs and deployment/artifact metadata, clean exposed copies as hygiene, restore with a known-good credential and controlled rollout, verify the old credential fails through an authorized test, then add missing inventory, detector, owner, and runbook controls. If evidence is insufficient, state uncertainty and escalate rather than inventing facts.
- **Common wrong answers:** Purging files first delays containment. Restarting everything without mapping dependencies may cause avoidable outage. Deleting evidence or pasting the secret into a ticket destroys safety and investigation quality.
- **Scoring rubric:** 8 points: first action/rationale 1; blast radius and revocation 2; scope/evidence 1; recovery/verification 2; prevention/ownership 1; safe uncertainty 1.
- **Safety/version note:** Synthetic incident only; do not validate a credential against a live third-party service.

### M09-U01-Q14 — design

- **Level:** L4
- **Type:** design
- **Objective tested:** build a defensible inventory from manifests, audit records, deployment metadata, and owner interviews
- **Estimated time:** [ILLUSTRATIVE] 20 minutes
- **Question / context:** Design a small-platform control for **data-flow evidence**. Constraints: zero-budget laptop lab, no live cloud account, two workloads with different privilege levels, and a requirement to demonstrate both permitted and forbidden behavior. State assumptions and failure modes.
- **Expected answer / model solution:** Model answer: start from the data flow and classify the credential; assign an accountable owner and inventory fields; select a delivery/control pattern appropriate to the consumer and freshness requirements; restrict each workload to its minimum path/permission; define rotation/revocation and outage behavior; ensure logs and audit evidence do not reveal the secret; and implement a disposable synthetic positive test plus a negative cross-workload test. Document recovery, cleanup, and what the local simulation cannot prove about a managed provider. A different design earns full credit if it explicitly handles these constraints.
- **Common wrong answers:** A single global credential for both workloads ignores privilege separation. “Use a vault” without auth, policy, lifecycle, audit, and recovery detail is not a design. A local mock is not evidence of cloud-provider parity.
- **Scoring rubric:** 10 points: correctness 2; least privilege 2; lifecycle/recovery 2; failure handling 1; verification/evidence 2; ownership/assumptions 1.
- **Safety/version note:** Provider-specific details remain [VERIFY]; no cloud account is required.

### M09-U01-Q15 — hands-on

- **Level:** L2
- **Type:** hands-on
- **Objective tested:** review exceptions, expiry, compensating controls, and accountable approval
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** In a disposable repository/local lab, design a safe test for **classification exceptions** using only values such as `FAKE_LAB_SECRET_DO_NOT_USE_7f31`. State the setup, observation, cleanup, and success criteria. Do not run a scan against external systems.
- **Expected answer / model solution:** Create a disposable fixture with one synthetic secret-like value and one harmless negative control. Run the relevant local control using documentation for the installed version, capture only redacted findings/exit status, and test both detection and non-detection cases. Record tool/version, fixture hash, expected result, and cleanup. The success criterion is not just a green run: the positive fixture must be detected (where detection is intended), the negative fixture should not create an unjustified finding, and no real credential is contacted or exposed.
- **Common wrong answers:** Testing only a clean repository does not establish detection coverage. Printing full matched values can create another leak. Skipping the negative fixture hides false-positive risk.
- **Scoring rubric:** 6 points: safe setup 1; positive test 1; negative test 1; evidence 1; cleanup 1; version caveat 1.
- **Safety/version note:** Exact command syntax is [VERIFY] for the installed tool/version; lab is [SIMULATION].

### M09-U01-Q16 — boundary test

- **Level:** L3
- **Type:** boundary test
- **Objective tested:** choose preventive, detective, containment, and recovery controls at each lifecycle stage
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** Define a negative test for **secret handling controls**. The test must demonstrate that a deliberately unauthorized synthetic identity cannot access a resource outside its assigned scope. What must be held constant, and what result counts as failure?
- **Expected answer / model solution:** Use two synthetic identities and two isolated resources. Establish a positive control for the authorized identity, then attempt the forbidden operation with the unauthorized identity while keeping the target, action, and policy state explicit. Denial must be enforced by the system, not merely by hiding a UI or omitting a credential. Capture status/audit evidence without logging secret material. Any success by the unauthorized identity is a failure and requires investigation of inherited policy, wildcard paths, namespace scope, cached credentials, and alternate access paths.
- **Common wrong answers:** A missing credential is not always a valid authorization test because it may test authentication only. Testing only the authorized identity proves no isolation. A client-side block is not an enforcement boundary.
- **Scoring rubric:** 6 points: clear boundary 2; valid positive/negative controls 2; evidence and failure criterion 1; safe handling 1.
- **Safety/version note:** Use local/synthetic identities only; exact denial codes and event names are version-specific [VERIFY].

### M09-U01-Q17 — evidence reasoning

- **Level:** L3
- **Type:** evidence reasoning
- **Objective tested:** state which evidence would change a conclusion about validity, access, or exposure
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** You believe **evidence quality** is correctly controlled, but your only evidence is a successful happy-path test and a green dashboard. Name three additional pieces of evidence that would strengthen or overturn the conclusion.
- **Expected answer / model solution:** Useful evidence includes a negative test against an unauthorized identity; an audit trail for the exact principal, path, action, and time; versioned configuration/policy review; evidence that the runtime consumer adopted the intended value; and a documented recovery/rotation test. Evidence that would overturn the conclusion includes an inherited wildcard permission, a stale process value, missing audit coverage, an artifact copy, or a test fixture that never exercised the intended path. State the time window and blind spots.
- **Common wrong answers:** A green dashboard may cover only the scanner/controller's configured scope. A single success says nothing about forbidden access. Absence of logs is not proof that no access occurred.
- **Scoring rubric:** 6 points: three relevant evidence items 3; counterevidence 1; scope/limitations 1; clear verification plan 1.
- **Safety/version note:** All examples are synthetic; evidence completeness depends on configured product/version and retention [VERIFY].

### M09-U01-Q18 — operational trade-off

- **Level:** L4
- **Type:** operational trade-off
- **Objective tested:** balance short TTLs, availability, rotation automation, client refresh, and incident response
- **Estimated time:** [ILLUSTRATIVE] 12 minutes
- **Question / context:** Evaluate the trade-off in **operational trade-offs** for (A) a short-running stateless API and (B) a 90-minute ETL job. State which design decisions may differ and which security invariants must remain unchanged.
- **Expected answer / model solution:** The API may tolerate shorter-lived credentials and rapid replacement if it can reacquire and retry safely. The ETL job needs lease/TTL planning, renewal capability, checkpointing, idempotency, connection-pool refresh, and a controlled recovery path. In both cases, least privilege, owner/inventory, auditability, safe handling, and an explicit revocation plan remain invariants. Choose TTLs from measured job duration and renewal behavior, not a universal number; define failure thresholds and alert before expiry.
- **Common wrong answers:** One TTL for every workload ignores duration and recovery. Making the ETL credential effectively permanent to avoid outages trades away bounded exposure. Aggressive expiry without client refresh can create predictable outages.
- **Scoring rubric:** 8 points: compare workload needs 2; preserve security invariants 2; failure handling 2; evidence/monitoring 1; explicit assumptions 1.
- **Safety/version note:** TTL numbers are [ASSUMPTION] unless derived from measured workload and provider constraints.

## Unit 2 — HashiCorp Vault architecture and auth methods

### M09-U02-Q01 — short answer

- **Level:** L1
- **Type:** short answer
- **Objective tested:** trace a client request through authentication, identity/token, policy authorization, secret engine, and audit
- **Estimated time:** [ILLUSTRATIVE] 6 minutes
- **Question / context:** Explain **request/auth/policy/audit flow** for a small data/AI platform. State the key boundary, the principal failure mode, and one control that reduces risk. Use a synthetic service credential; assume no cloud account is available.
- **Expected answer / model solution:** A strong answer should trace a client request through authentication, identity/token, policy authorization, secret engine, and audit; identify the boundary where exposure or misuse can occur; state who can use the credential and for what; and pair prevention with detection/recovery. The practical check is to trace the relevant evidence and test the control in a disposable local environment. Do not infer that a secret is safe merely because it is not visible in the current source file.
- **Common wrong answers:** Saying only “put it in a secret manager” misses consumers, permissions, logs, copies, expiry, and recovery. Treating an absence of findings as proof of no exposure is also unsupported.
- **Scoring rubric:** 4 points: concept 1; boundary/threat 1; actionable control 1; verification/evidence 1. Partial credit for a defensible alternative with explicit assumptions.
- **Safety/version note:** None beyond the synthetic/offline assumptions stated in this question.

### M09-U02-Q02 — short answer

- **Level:** L1
- **Type:** short answer
- **Objective tested:** explain why local development mode is not a production deployment pattern
- **Estimated time:** [ILLUSTRATIVE] 7 minutes
- **Question / context:** Explain **development versus production mode** for a small data/AI platform. State the key boundary, the principal failure mode, and one control that reduces risk. Use a synthetic service credential; assume no cloud account is available.
- **Expected answer / model solution:** A strong answer should explain why local development mode is not a production deployment pattern; identify the boundary where exposure or misuse can occur; state who can use the credential and for what; and pair prevention with detection/recovery. The practical check is to trace the relevant evidence and test the control in a disposable local environment. Do not infer that a secret is safe merely because it is not visible in the current source file.
- **Common wrong answers:** Saying only “put it in a secret manager” misses consumers, permissions, logs, copies, expiry, and recovery. Treating an absence of findings as proof of no exposure is also unsupported.
- **Scoring rubric:** 4 points: concept 1; boundary/threat 1; actionable control 1; verification/evidence 1. Partial credit for a defensible alternative with explicit assumptions.
- **Safety/version note:** None beyond the synthetic/offline assumptions stated in this question.

### M09-U02-Q03 — short answer

- **Level:** L1
- **Type:** short answer
- **Objective tested:** separate initialization, unseal/recovery material custody, and availability planning
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Explain **initialization and seal custody** for a small data/AI platform. State the key boundary, the principal failure mode, and one control that reduces risk. Use a synthetic service credential; assume no cloud account is available.
- **Expected answer / model solution:** A strong answer should separate initialization, unseal/recovery material custody, and availability planning; identify the boundary where exposure or misuse can occur; state who can use the credential and for what; and pair prevention with detection/recovery. The practical check is to trace the relevant evidence and test the control in a disposable local environment. Do not infer that a secret is safe merely because it is not visible in the current source file.
- **Common wrong answers:** Saying only “put it in a secret manager” misses consumers, permissions, logs, copies, expiry, and recovery. Treating an absence of findings as proof of no exposure is also unsupported.
- **Scoring rubric:** 4 points: concept 1; boundary/threat 1; actionable control 1; verification/evidence 1. Partial credit for a defensible alternative with explicit assumptions.
- **Safety/version note:** None beyond the synthetic/offline assumptions stated in this question.

### M09-U02-Q04 — MCQ

- **Level:** L1
- **Type:** MCQ
- **Objective tested:** reduce root-token use, secure any break-glass path, and avoid routine application access
- **Estimated time:** [ILLUSTRATIVE] 4 minutes
- **Question / context:** Which response best addresses **root-token minimization**? Choose one. [ILLUSTRATIVE] The environment is a disposable local lab and the credential is synthetic.

A. Map the complete root-token minimization path, restrict access to the minimum consumer, and verify the boundary with a negative test.
B. Rely on a naming convention and assume any component with the same project label is trusted.
C. Delete the visible value immediately and skip revocation, dependency discovery, and audit review.
D. Accept the configuration because the happy path works; do not test forbidden access.
- **Expected answer / model solution:** **Correct: A.** It directly addresses root-token minimization and includes a verifiable boundary rather than relying on naming or a single successful request. **B is wrong** because labels/names do not enforce authorization. **C is incomplete** because deleting a copy does not necessarily invalidate a live credential or scope other copies. **D is wrong** because positive tests do not establish least privilege; negative tests are required.
- **Common wrong answers:** Choosing B confuses convention with enforcement. Choosing C mistakes cleanup for containment. Choosing D proves only one permitted path and leaves unauthorized access untested.
- **Scoring rubric:** 4 points: correct option 1; explain A 1; explain why B/C/D fail 2. Partial credit for identifying the key boundary even with a wrong choice.
- **Safety/version note:** Any product-specific commands or fields are [VERIFY] for the exact version; this is a concept question, not proof of product behavior.

### M09-U02-Q05 — MCQ

- **Level:** L2
- **Type:** MCQ
- **Objective tested:** distinguish invalid/missing identity from a valid identity denied by policy
- **Estimated time:** [ILLUSTRATIVE] 4 minutes
- **Question / context:** Which response best addresses **authn versus authz**? Choose one. [ILLUSTRATIVE] The environment is a disposable local lab and the credential is synthetic.

A. Use a narrowly scoped identity/policy and inspect the relevant audit/operational evidence before concluding.
B. Rely on a naming convention and assume any component with the same project label is trusted.
C. Delete the visible value immediately and skip revocation, dependency discovery, and audit review.
D. Accept the configuration because the happy path works; do not test forbidden access.
- **Expected answer / model solution:** **Correct: A.** It directly addresses authn versus authz and includes a verifiable boundary rather than relying on naming or a single successful request. **B is wrong** because labels/names do not enforce authorization. **C is incomplete** because deleting a copy does not necessarily invalidate a live credential or scope other copies. **D is wrong** because positive tests do not establish least privilege; negative tests are required.
- **Common wrong answers:** Choosing B confuses convention with enforcement. Choosing C mistakes cleanup for containment. Choosing D proves only one permitted path and leaves unauthorized access untested.
- **Scoring rubric:** 4 points: correct option 1; explain A 1; explain why B/C/D fail 2. Partial credit for identifying the key boundary even with a wrong choice.
- **Safety/version note:** Any product-specific commands or fields are [VERIFY] for the exact version; this is a concept question, not proof of product behavior.

### M09-U02-Q06 — MCQ

- **Level:** L2
- **Type:** MCQ
- **Objective tested:** reason about exact paths, capabilities, namespaces/mounts, and least privilege
- **Estimated time:** [ILLUSTRATIVE] 4 minutes
- **Question / context:** Which response best addresses **policy path/capability review**? Choose one. [ILLUSTRATIVE] The environment is a disposable local lab and the credential is synthetic.

A. Treat the observed representation as insufficient proof of confidentiality; validate the actual protection boundary and test access.
B. Rely on a naming convention and assume any component with the same project label is trusted.
C. Delete the visible value immediately and skip revocation, dependency discovery, and audit review.
D. Accept the configuration because the happy path works; do not test forbidden access.
- **Expected answer / model solution:** **Correct: A.** It directly addresses policy path/capability review and includes a verifiable boundary rather than relying on naming or a single successful request. **B is wrong** because labels/names do not enforce authorization. **C is incomplete** because deleting a copy does not necessarily invalidate a live credential or scope other copies. **D is wrong** because positive tests do not establish least privilege; negative tests are required.
- **Common wrong answers:** Choosing B confuses convention with enforcement. Choosing C mistakes cleanup for containment. Choosing D proves only one permitted path and leaves unauthorized access untested.
- **Scoring rubric:** 4 points: correct option 1; explain A 1; explain why B/C/D fail 2. Partial credit for identifying the key boundary even with a wrong choice.
- **Safety/version note:** Any product-specific commands or fields are [VERIFY] for the exact version; this is a concept question, not proof of product behavior.

### M09-U02-Q07 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** explain workload token validation/TokenReview concepts and trust-boundary requirements
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Interpret this representative output and propose the next two verification steps:

```text
[ILLUSTRATIVE] inventory row: owner=unknown; source=CI variable; consumers=etl-worker, notebook-job; expiry=none; last_seen=build-log; audit_source=missing
```
Do not assume omitted fields are healthy.
- **Expected answer / model solution:** The inventory is incomplete and signals high uncertainty: owner, expiry, audit source, and lifecycle runbook are missing. Treat the build-log appearance as an exposure, identify the exact synthetic credential and privileges, notify the accountable incident owner, rotate/revoke if it could be live, then trace consumers and artifacts.
- **Common wrong answers:** Declaring success from one green field is insufficient. For identity, do not stop at signature validity; for freshness, do not equate source update with process adoption; for inventory, do not treat unknown ownership as a reason to delay escalation.
- **Scoring rubric:** 5 points: interpret evidence 2; identify missing evidence 1; safe next steps 1; verification criteria 1.
- **Safety/version note:** Output is synthetic and [ILLUSTRATIVE], not captured from a live product.

### M09-U02-Q08 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** evaluate issuer, signature/key, audience, subject, time claims, and configured role constraints
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Interpret this representative output and propose the next two verification steps:

```text
[ILLUSTRATIVE] verifier result: signature=valid; issuer=expected; audience=unexpected-api; subject=repo:demo/project:ref:refs/heads/feature; exp=in-future; policy=role expects refs/heads/main
```
Do not assume omitted fields are healthy.
- **Expected answer / model solution:** The token should be rejected by the stated verifier/role constraints despite a valid signature: audience and subject/ref do not match. Signature validity alone does not prove intended audience or authorization. Check issuer, key/JWKS, time claims, audience, subject, then resulting policy separately.
- **Common wrong answers:** Declaring success from one green field is insufficient. For identity, do not stop at signature validity; for freshness, do not equate source update with process adoption; for inventory, do not treat unknown ownership as a reason to delay escalation.
- **Scoring rubric:** 5 points: interpret evidence 2; identify missing evidence 1; safe next steps 1; verification criteria 1.
- **Safety/version note:** Output is synthetic and [ILLUSTRATIVE], not captured from a live product.

### M09-U02-Q09 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** plan audit coverage, access restriction, retention, integrity, and sensitive-field handling
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Interpret this representative output and propose the next two verification steps:

```text
[ILLUSTRATIVE] rollout evidence: provider_version=v8; mounted_file_version=v8; process_started_at=09:00; process_loaded_version=v7; env_source=process-start
```
Do not assume omitted fields are healthy.
- **Expected answer / model solution:** The source and mounted file are current but the process still uses a previously loaded value. Determine whether the app reads a file dynamically or loads a value at startup; trigger a controlled reload/restart only after a safe rollout plan, then verify the app actually adopted v8.
- **Common wrong answers:** Declaring success from one green field is insufficient. For identity, do not stop at signature validity; for freshness, do not equate source update with process adoption; for inventory, do not treat unknown ownership as a reason to delay escalation.
- **Scoring rubric:** 5 points: interpret evidence 2; identify missing evidence 1; safe next steps 1; verification criteria 1.
- **Safety/version note:** Output is synthetic and [ILLUSTRATIVE], not captured from a live product.

### M09-U02-Q10 — config review

- **Level:** L2
- **Type:** config review
- **Objective tested:** relate auth method, entity/alias, token TTL, policy set, and revocation
- **Estimated time:** [ILLUSTRATIVE] 12 minutes
- **Question / context:** Review the synthetic configuration for **identity/entity/token lifecycle**. Find at least three defects, explain impact, provide exact conceptual fixes, and state a verification test.

```yaml
# [ILLUSTRATIVE] unsafe example
secret_value: "FAKE_DO_NOT_USE_7f31"
read_all_paths: true
audit_enabled: false
owner: ""
ttl: "never"
```
- **Expected answer / model solution:** Defects to identify: (1) the fake credential is embedded directly in configuration; replace it with a reference/injection from the approved secret source and ensure it never enters committed files or logs; (2) broad access (`read_all_paths` / wildcard allow) violates least privilege; narrow to the exact required path/actions; (3) audit disabled or failure ignored removes important evidence and can conceal outages; enable and monitor appropriate audit/reconciliation evidence; (4) missing owner or shared namespace boundary prevents accountability and can permit cross-tenant access; define owner and enforce scope; (5) unbounded/disabled TTL or refresh policy can leave stale credentials; set lifecycle behavior appropriate to workload and monitor expiry; (6) no forbidden-access test means the policy is unproven. Verification: positive test for the intended consumer, negative test for a neighboring identity/path, review emitted audit/conditions, and ensure the synthetic value is absent from repository history/artifacts.
- **Common wrong answers:** Only changing the fake value is not enough. Broad permissions cannot be justified by a successful happy path. Enabling a feature without testing its effective behavior is not verification. A TTL must be compatible with consumer refresh and job duration.
- **Scoring rubric:** 8 points: identify defects 3; impact/fix 3; positive and negative verification 2. Partial credit for equivalent safe corrections.
- **Safety/version note:** Illustrative pseudo-configuration, not a valid product schema. Any exact fields/commands are [VERIFY] for the named version.

### M09-U02-Q11 — config review

- **Level:** L2
- **Type:** config review
- **Objective tested:** assess availability, storage quorum, seal dependencies, and safe recovery procedures
- **Estimated time:** [ILLUSTRATIVE] 12 minutes
- **Question / context:** Review the synthetic configuration for **HA and operational failure**. Find at least three defects, explain impact, provide exact conceptual fixes, and state a verification test.

```yaml
# [ILLUSTRATIVE] unsafe example
allow:
  - "*"
refresh: "disabled"
on_failure: "ignore"
namespace_boundary: "shared"
test_forbidden_access: false
```
- **Expected answer / model solution:** Defects to identify: (1) the fake credential is embedded directly in configuration; replace it with a reference/injection from the approved secret source and ensure it never enters committed files or logs; (2) broad access (`read_all_paths` / wildcard allow) violates least privilege; narrow to the exact required path/actions; (3) audit disabled or failure ignored removes important evidence and can conceal outages; enable and monitor appropriate audit/reconciliation evidence; (4) missing owner or shared namespace boundary prevents accountability and can permit cross-tenant access; define owner and enforce scope; (5) unbounded/disabled TTL or refresh policy can leave stale credentials; set lifecycle behavior appropriate to workload and monitor expiry; (6) no forbidden-access test means the policy is unproven. Verification: positive test for the intended consumer, negative test for a neighboring identity/path, review emitted audit/conditions, and ensure the synthetic value is absent from repository history/artifacts.
- **Common wrong answers:** Only changing the fake value is not enough. Broad permissions cannot be justified by a successful happy path. Enabling a feature without testing its effective behavior is not verification. A TTL must be compatible with consumer refresh and job duration.
- **Scoring rubric:** 8 points: identify defects 3; impact/fix 3; positive and negative verification 2. Partial credit for equivalent safe corrections.
- **Safety/version note:** Illustrative pseudo-configuration, not a valid product schema. Any exact fields/commands are [VERIFY] for the named version.

### M09-U02-Q12 — incident/troubleshooting

- **Level:** L3
- **Type:** incident/troubleshooting
- **Objective tested:** prove allowed actions succeed and forbidden paths/actions fail
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** Incident: an alert indicates a possible failure or exposure involving **negative policy tests**. The service is important but the evidence is incomplete; only synthetic logs are available in the exercise. Give an ordered response using diagnose → blast-radius/revocation check → contain → scope → eradicate → recover → prevent. Identify the first action and why.
- **Expected answer / model solution:** First preserve the alert/event identifiers and time window without copying the credential into chat or a ticket. Quickly determine credential type, privilege, validity, consumers, and whether safe immediate revocation/rotation is warranted; when compromise is credible and the credential may still be valid, invalidate/rotate before Git or artifact cleanup. Contain affected identities/paths, scope access using audit logs and deployment/artifact metadata, clean exposed copies as hygiene, restore with a known-good credential and controlled rollout, verify the old credential fails through an authorized test, then add missing inventory, detector, owner, and runbook controls. If evidence is insufficient, state uncertainty and escalate rather than inventing facts.
- **Common wrong answers:** Purging files first delays containment. Restarting everything without mapping dependencies may cause avoidable outage. Deleting evidence or pasting the secret into a ticket destroys safety and investigation quality.
- **Scoring rubric:** 8 points: first action/rationale 1; blast radius and revocation 2; scope/evidence 1; recovery/verification 2; prevention/ownership 1; safe uncertainty 1.
- **Safety/version note:** Synthetic incident only; do not validate a credential against a live third-party service.

### M09-U02-Q13 — incident/troubleshooting

- **Level:** L3
- **Type:** incident/troubleshooting
- **Objective tested:** interpret representative synthetic request outcomes without treating logs as complete proof
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** Incident: an alert indicates a possible failure or exposure involving **audit interpretation**. The service is important but the evidence is incomplete; only synthetic logs are available in the exercise. Give an ordered response using diagnose → blast-radius/revocation check → contain → scope → eradicate → recover → prevent. Identify the first action and why.
- **Expected answer / model solution:** First preserve the alert/event identifiers and time window without copying the credential into chat or a ticket. Quickly determine credential type, privilege, validity, consumers, and whether safe immediate revocation/rotation is warranted; when compromise is credible and the credential may still be valid, invalidate/rotate before Git or artifact cleanup. Contain affected identities/paths, scope access using audit logs and deployment/artifact metadata, clean exposed copies as hygiene, restore with a known-good credential and controlled rollout, verify the old credential fails through an authorized test, then add missing inventory, detector, owner, and runbook controls. If evidence is insufficient, state uncertainty and escalate rather than inventing facts.
- **Common wrong answers:** Purging files first delays containment. Restarting everything without mapping dependencies may cause avoidable outage. Deleting evidence or pasting the secret into a ticket destroys safety and investigation quality.
- **Scoring rubric:** 8 points: first action/rationale 1; blast radius and revocation 2; scope/evidence 1; recovery/verification 2; prevention/ownership 1; safe uncertainty 1.
- **Safety/version note:** Synthetic incident only; do not validate a credential against a live third-party service.

### M09-U02-Q14 — design

- **Level:** L4
- **Type:** design
- **Objective tested:** separate endpoint/network, auth method, token, policy, and backend causes
- **Estimated time:** [ILLUSTRATIVE] 20 minutes
- **Question / context:** Design a small-platform control for **auth troubleshooting**. Constraints: zero-budget laptop lab, no live cloud account, two workloads with different privilege levels, and a requirement to demonstrate both permitted and forbidden behavior. State assumptions and failure modes.
- **Expected answer / model solution:** Model answer: start from the data flow and classify the credential; assign an accountable owner and inventory fields; select a delivery/control pattern appropriate to the consumer and freshness requirements; restrict each workload to its minimum path/permission; define rotation/revocation and outage behavior; ensure logs and audit evidence do not reveal the secret; and implement a disposable synthetic positive test plus a negative cross-workload test. Document recovery, cleanup, and what the local simulation cannot prove about a managed provider. A different design earns full credit if it explicitly handles these constraints.
- **Common wrong answers:** A single global credential for both workloads ignores privilege separation. “Use a vault” without auth, policy, lifecycle, audit, and recovery detail is not a design. A local mock is not evidence of cloud-provider parity.
- **Scoring rubric:** 10 points: correctness 2; least privilege 2; lifecycle/recovery 2; failure handling 1; verification/evidence 2; ownership/assumptions 1.
- **Safety/version note:** Provider-specific details remain [VERIFY]; no cloud account is required.

### M09-U02-Q15 — hands-on

- **Level:** L2
- **Type:** hands-on
- **Objective tested:** design documented, time-bounded, auditable emergency access
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** In a disposable repository/local lab, design a safe test for **recovery and break-glass** using only values such as `FAKE_LAB_SECRET_DO_NOT_USE_7f31`. State the setup, observation, cleanup, and success criteria. Do not run a scan against external systems.
- **Expected answer / model solution:** Create a disposable fixture with one synthetic secret-like value and one harmless negative control. Run the relevant local control using documentation for the installed version, capture only redacted findings/exit status, and test both detection and non-detection cases. Record tool/version, fixture hash, expected result, and cleanup. The success criterion is not just a green run: the positive fixture must be detected (where detection is intended), the negative fixture should not create an unjustified finding, and no real credential is contacted or exposed.
- **Common wrong answers:** Testing only a clean repository does not establish detection coverage. Printing full matched values can create another leak. Skipping the negative fixture hides false-positive risk.
- **Scoring rubric:** 6 points: safe setup 1; positive test 1; negative test 1; evidence 1; cleanup 1; version caveat 1.
- **Safety/version note:** Exact command syntax is [VERIFY] for the installed tool/version; lab is [SIMULATION].

### M09-U02-Q16 — boundary test

- **Level:** L3
- **Type:** boundary test
- **Objective tested:** treat Vault/OpenBao behavior and version-specific fields as [VERIFY] unless checked
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** Define a negative test for **compatibility boundaries**. The test must demonstrate that a deliberately unauthorized synthetic identity cannot access a resource outside its assigned scope. What must be held constant, and what result counts as failure?
- **Expected answer / model solution:** Use two synthetic identities and two isolated resources. Establish a positive control for the authorized identity, then attempt the forbidden operation with the unauthorized identity while keeping the target, action, and policy state explicit. Denial must be enforced by the system, not merely by hiding a UI or omitting a credential. Capture status/audit evidence without logging secret material. Any success by the unauthorized identity is a failure and requires investigation of inherited policy, wildcard paths, namespace scope, cached credentials, and alternate access paths.
- **Common wrong answers:** A missing credential is not always a valid authorization test because it may test authentication only. Testing only the authorized identity proves no isolation. A client-side block is not an enforcement boundary.
- **Scoring rubric:** 6 points: clear boundary 2; valid positive/negative controls 2; evidence and failure criterion 1; safe handling 1.
- **Safety/version note:** Use local/synthetic identities only; exact denial codes and event names are version-specific [VERIFY].

### M09-U02-Q17 — evidence reasoning

- **Level:** L3
- **Type:** evidence reasoning
- **Objective tested:** design narrow read paths without broad list/read access
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** You believe **least-privilege application policy** is correctly controlled, but your only evidence is a successful happy-path test and a green dashboard. Name three additional pieces of evidence that would strengthen or overturn the conclusion.
- **Expected answer / model solution:** Useful evidence includes a negative test against an unauthorized identity; an audit trail for the exact principal, path, action, and time; versioned configuration/policy review; evidence that the runtime consumer adopted the intended value; and a documented recovery/rotation test. Evidence that would overturn the conclusion includes an inherited wildcard permission, a stale process value, missing audit coverage, an artifact copy, or a test fixture that never exercised the intended path. State the time window and blind spots.
- **Common wrong answers:** A green dashboard may cover only the scanner/controller's configured scope. A single success says nothing about forbidden access. Absence of logs is not proof that no access occurred.
- **Scoring rubric:** 6 points: three relevant evidence items 3; counterevidence 1; scope/limitations 1; clear verification plan 1.
- **Safety/version note:** All examples are synthetic; evidence completeness depends on configured product/version and retention [VERIFY].

### M09-U02-Q18 — operational trade-off

- **Level:** L4
- **Type:** operational trade-off
- **Objective tested:** balance HA, key custody, audit completeness, admin overhead, and recovery time
- **Estimated time:** [ILLUSTRATIVE] 12 minutes
- **Question / context:** Evaluate the trade-off in **operational trade-offs** for (A) a short-running stateless API and (B) a 90-minute ETL job. State which design decisions may differ and which security invariants must remain unchanged.
- **Expected answer / model solution:** The API may tolerate shorter-lived credentials and rapid replacement if it can reacquire and retry safely. The ETL job needs lease/TTL planning, renewal capability, checkpointing, idempotency, connection-pool refresh, and a controlled recovery path. In both cases, least privilege, owner/inventory, auditability, safe handling, and an explicit revocation plan remain invariants. Choose TTLs from measured job duration and renewal behavior, not a universal number; define failure thresholds and alert before expiry.
- **Common wrong answers:** One TTL for every workload ignores duration and recovery. Making the ETL credential effectively permanent to avoid outages trades away bounded exposure. Aggressive expiry without client refresh can create predictable outages.
- **Scoring rubric:** 8 points: compare workload needs 2; preserve security invariants 2; failure handling 2; evidence/monitoring 1; explicit assumptions 1.
- **Safety/version note:** TTL numbers are [ASSUMPTION] unless derived from measured workload and provider constraints.

## Unit 3 — Dynamic secrets, leases, and rotation

### M09-U03-Q01 — short answer

- **Level:** L1
- **Type:** short answer
- **Objective tested:** compare issuance-time credentials with per-client dynamically generated credentials
- **Estimated time:** [ILLUSTRATIVE] 6 minutes
- **Question / context:** Explain **static versus dynamic credentials** for a small data/AI platform. State the key boundary, the principal failure mode, and one control that reduces risk. Use a synthetic service credential; assume no cloud account is available.
- **Expected answer / model solution:** A strong answer should compare issuance-time credentials with per-client dynamically generated credentials; identify the boundary where exposure or misuse can occur; state who can use the credential and for what; and pair prevention with detection/recovery. The practical check is to trace the relevant evidence and test the control in a disposable local environment. Do not infer that a secret is safe merely because it is not visible in the current source file.
- **Common wrong answers:** Saying only “put it in a secret manager” misses consumers, permissions, logs, copies, expiry, and recovery. Treating an absence of findings as proof of no exposure is also unsupported.
- **Scoring rubric:** 4 points: concept 1; boundary/threat 1; actionable control 1; verification/evidence 1. Partial credit for a defensible alternative with explicit assumptions.
- **Safety/version note:** None beyond the synthetic/offline assumptions stated in this question.

### M09-U03-Q02 — short answer

- **Level:** L1
- **Type:** short answer
- **Objective tested:** interpret lease ID, TTL, renewal, expiry, and revocation as distinct lifecycle events
- **Estimated time:** [ILLUSTRATIVE] 7 minutes
- **Question / context:** Explain **lease and TTL semantics** for a small data/AI platform. State the key boundary, the principal failure mode, and one control that reduces risk. Use a synthetic service credential; assume no cloud account is available.
- **Expected answer / model solution:** A strong answer should interpret lease ID, TTL, renewal, expiry, and revocation as distinct lifecycle events; identify the boundary where exposure or misuse can occur; state who can use the credential and for what; and pair prevention with detection/recovery. The practical check is to trace the relevant evidence and test the control in a disposable local environment. Do not infer that a secret is safe merely because it is not visible in the current source file.
- **Common wrong answers:** Saying only “put it in a secret manager” misses consumers, permissions, logs, copies, expiry, and recovery. Treating an absence of findings as proof of no exposure is also unsupported.
- **Scoring rubric:** 4 points: concept 1; boundary/threat 1; actionable control 1; verification/evidence 1. Partial credit for a defensible alternative with explicit assumptions.
- **Safety/version note:** None beyond the synthetic/offline assumptions stated in this question.

### M09-U03-Q03 — short answer

- **Level:** L1
- **Type:** short answer
- **Objective tested:** design database users with minimum schema/table privileges and bounded lifetime
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Explain **database role grants** for a small data/AI platform. State the key boundary, the principal failure mode, and one control that reduces risk. Use a synthetic service credential; assume no cloud account is available.
- **Expected answer / model solution:** A strong answer should design database users with minimum schema/table privileges and bounded lifetime; identify the boundary where exposure or misuse can occur; state who can use the credential and for what; and pair prevention with detection/recovery. The practical check is to trace the relevant evidence and test the control in a disposable local environment. Do not infer that a secret is safe merely because it is not visible in the current source file.
- **Common wrong answers:** Saying only “put it in a secret manager” misses consumers, permissions, logs, copies, expiry, and recovery. Treating an absence of findings as proof of no exposure is also unsupported.
- **Scoring rubric:** 4 points: concept 1; boundary/threat 1; actionable control 1; verification/evidence 1. Partial credit for a defensible alternative with explicit assumptions.
- **Safety/version note:** None beyond the synthetic/offline assumptions stated in this question.

### M09-U03-Q04 — MCQ

- **Level:** L1
- **Type:** MCQ
- **Objective tested:** coordinate credential refresh with connection pools, retries, and long-running jobs
- **Estimated time:** [ILLUSTRATIVE] 4 minutes
- **Question / context:** Which response best addresses **client refresh and pools**? Choose one. [ILLUSTRATIVE] The environment is a disposable local lab and the credential is synthetic.

A. Map the complete client refresh and pools path, restrict access to the minimum consumer, and verify the boundary with a negative test.
B. Rely on a naming convention and assume any component with the same project label is trusted.
C. Delete the visible value immediately and skip revocation, dependency discovery, and audit review.
D. Accept the configuration because the happy path works; do not test forbidden access.
- **Expected answer / model solution:** **Correct: A.** It directly addresses client refresh and pools and includes a verifiable boundary rather than relying on naming or a single successful request. **B is wrong** because labels/names do not enforce authorization. **C is incomplete** because deleting a copy does not necessarily invalidate a live credential or scope other copies. **D is wrong** because positive tests do not establish least privilege; negative tests are required.
- **Common wrong answers:** Choosing B confuses convention with enforcement. Choosing C mistakes cleanup for containment. Choosing D proves only one permitted path and leaves unauthorized access untested.
- **Scoring rubric:** 4 points: correct option 1; explain A 1; explain why B/C/D fail 2. Partial credit for identifying the key boundary even with a wrong choice.
- **Safety/version note:** Any product-specific commands or fields are [VERIFY] for the exact version; this is a concept question, not proof of product behavior.

### M09-U03-Q05 — MCQ

- **Level:** L2
- **Type:** MCQ
- **Objective tested:** decide between scheduled overlap and urgent invalidation after suspected compromise
- **Estimated time:** [ILLUSTRATIVE] 4 minutes
- **Question / context:** Which response best addresses **rotation versus revocation**? Choose one. [ILLUSTRATIVE] The environment is a disposable local lab and the credential is synthetic.

A. Use a narrowly scoped identity/policy and inspect the relevant audit/operational evidence before concluding.
B. Rely on a naming convention and assume any component with the same project label is trusted.
C. Delete the visible value immediately and skip revocation, dependency discovery, and audit review.
D. Accept the configuration because the happy path works; do not test forbidden access.
- **Expected answer / model solution:** **Correct: A.** It directly addresses rotation versus revocation and includes a verifiable boundary rather than relying on naming or a single successful request. **B is wrong** because labels/names do not enforce authorization. **C is incomplete** because deleting a copy does not necessarily invalidate a live credential or scope other copies. **D is wrong** because positive tests do not establish least privilege; negative tests are required.
- **Common wrong answers:** Choosing B confuses convention with enforcement. Choosing C mistakes cleanup for containment. Choosing D proves only one permitted path and leaves unauthorized access untested.
- **Scoring rubric:** 4 points: correct option 1; explain A 1; explain why B/C/D fail 2. Partial credit for identifying the key boundary even with a wrong choice.
- **Safety/version note:** Any product-specific commands or fields are [VERIFY] for the exact version; this is a concept question, not proof of product behavior.

### M09-U03-Q06 — MCQ

- **Level:** L2
- **Type:** MCQ
- **Objective tested:** explain controlled backend credential rotation and recovery implications
- **Estimated time:** [ILLUSTRATIVE] 4 minutes
- **Question / context:** Which response best addresses **root credential rotation**? Choose one. [ILLUSTRATIVE] The environment is a disposable local lab and the credential is synthetic.

A. Treat the observed representation as insufficient proof of confidentiality; validate the actual protection boundary and test access.
B. Rely on a naming convention and assume any component with the same project label is trusted.
C. Delete the visible value immediately and skip revocation, dependency discovery, and audit review.
D. Accept the configuration because the happy path works; do not test forbidden access.
- **Expected answer / model solution:** **Correct: A.** It directly addresses root credential rotation and includes a verifiable boundary rather than relying on naming or a single successful request. **B is wrong** because labels/names do not enforce authorization. **C is incomplete** because deleting a copy does not necessarily invalidate a live credential or scope other copies. **D is wrong** because positive tests do not establish least privilege; negative tests are required.
- **Common wrong answers:** Choosing B confuses convention with enforcement. Choosing C mistakes cleanup for containment. Choosing D proves only one permitted path and leaves unauthorized access untested.
- **Scoring rubric:** 4 points: correct option 1; explain A 1; explain why B/C/D fail 2. Partial credit for identifying the key boundary even with a wrong choice.
- **Safety/version note:** Any product-specific commands or fields are [VERIFY] for the exact version; this is a concept question, not proof of product behavior.

### M09-U03-Q07 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** distinguish token lifecycle concepts where taught and verify product/version semantics
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Interpret this representative output and propose the next two verification steps:

```text
[ILLUSTRATIVE] inventory row: owner=unknown; source=CI variable; consumers=etl-worker, notebook-job; expiry=none; last_seen=build-log; audit_source=missing
```
Do not assume omitted fields are healthy.
- **Expected answer / model solution:** The inventory is incomplete and signals high uncertainty: owner, expiry, audit source, and lifecycle runbook are missing. Treat the build-log appearance as an exposure, identify the exact synthetic credential and privileges, notify the accountable incident owner, rotate/revoke if it could be live, then trace consumers and artifacts.
- **Common wrong answers:** Declaring success from one green field is insufficient. For identity, do not stop at signature validity; for freshness, do not equate source update with process adoption; for inventory, do not treat unknown ownership as a reason to delay escalation.
- **Scoring rubric:** 5 points: interpret evidence 2; identify missing evidence 1; safe next steps 1; verification criteria 1.
- **Safety/version note:** Output is synthetic and [ILLUSTRATIVE], not captured from a live product.

### M09-U03-Q08 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** handle mid-job expiry with checkpoints, idempotency, bounded retries, and safe reacquisition
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Interpret this representative output and propose the next two verification steps:

```text
[ILLUSTRATIVE] verifier result: signature=valid; issuer=expected; audience=unexpected-api; subject=repo:demo/project:ref:refs/heads/feature; exp=in-future; policy=role expects refs/heads/main
```
Do not assume omitted fields are healthy.
- **Expected answer / model solution:** The token should be rejected by the stated verifier/role constraints despite a valid signature: audience and subject/ref do not match. Signature validity alone does not prove intended audience or authorization. Check issuer, key/JWKS, time claims, audience, subject, then resulting policy separately.
- **Common wrong answers:** Declaring success from one green field is insufficient. For identity, do not stop at signature validity; for freshness, do not equate source update with process adoption; for inventory, do not treat unknown ownership as a reason to delay escalation.
- **Scoring rubric:** 5 points: interpret evidence 2; identify missing evidence 1; safe next steps 1; verification criteria 1.
- **Safety/version note:** Output is synthetic and [ILLUSTRATIVE], not captured from a live product.

### M09-U03-Q09 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** plan dual-validity windows without leaving old credentials valid indefinitely
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Interpret this representative output and propose the next two verification steps:

```text
[ILLUSTRATIVE] rollout evidence: provider_version=v8; mounted_file_version=v8; process_started_at=09:00; process_loaded_version=v7; env_source=process-start
```
Do not assume omitted fields are healthy.
- **Expected answer / model solution:** The source and mounted file are current but the process still uses a previously loaded value. Determine whether the app reads a file dynamically or loads a value at startup; trigger a controlled reload/restart only after a safe rollout plan, then verify the app actually adopted v8.
- **Common wrong answers:** Declaring success from one green field is insufficient. For identity, do not stop at signature validity; for freshness, do not equate source update with process adoption; for inventory, do not treat unknown ownership as a reason to delay escalation.
- **Scoring rubric:** 5 points: interpret evidence 2; identify missing evidence 1; safe next steps 1; verification criteria 1.
- **Safety/version note:** Output is synthetic and [ILLUSTRATIVE], not captured from a live product.

### M09-U03-Q10 — config review

- **Level:** L2
- **Type:** config review
- **Objective tested:** prove old credentials fail safely without testing against a third-party service
- **Estimated time:** [ILLUSTRATIVE] 12 minutes
- **Question / context:** Review the synthetic configuration for **negative verification**. Find at least three defects, explain impact, provide exact conceptual fixes, and state a verification test.

```yaml
# [ILLUSTRATIVE] unsafe example
secret_value: "FAKE_DO_NOT_USE_7f31"
read_all_paths: true
audit_enabled: false
owner: ""
ttl: "never"
```
- **Expected answer / model solution:** Defects to identify: (1) the fake credential is embedded directly in configuration; replace it with a reference/injection from the approved secret source and ensure it never enters committed files or logs; (2) broad access (`read_all_paths` / wildcard allow) violates least privilege; narrow to the exact required path/actions; (3) audit disabled or failure ignored removes important evidence and can conceal outages; enable and monitor appropriate audit/reconciliation evidence; (4) missing owner or shared namespace boundary prevents accountability and can permit cross-tenant access; define owner and enforce scope; (5) unbounded/disabled TTL or refresh policy can leave stale credentials; set lifecycle behavior appropriate to workload and monitor expiry; (6) no forbidden-access test means the policy is unproven. Verification: positive test for the intended consumer, negative test for a neighboring identity/path, review emitted audit/conditions, and ensure the synthetic value is absent from repository history/artifacts.
- **Common wrong answers:** Only changing the fake value is not enough. Broad permissions cannot be justified by a successful happy path. Enabling a feature without testing its effective behavior is not verification. A TTL must be compatible with consumer refresh and job duration.
- **Scoring rubric:** 8 points: identify defects 3; impact/fix 3; positive and negative verification 2. Partial credit for equivalent safe corrections.
- **Safety/version note:** Illustrative pseudo-configuration, not a valid product schema. Any exact fields/commands are [VERIFY] for the named version.

### M09-U03-Q11 — config review

- **Level:** L2
- **Type:** config review
- **Objective tested:** identify consumers, pools, jobs, replicas, rollback paths, and secret owners before rotation
- **Estimated time:** [ILLUSTRATIVE] 12 minutes
- **Question / context:** Review the synthetic configuration for **dependency mapping**. Find at least three defects, explain impact, provide exact conceptual fixes, and state a verification test.

```yaml
# [ILLUSTRATIVE] unsafe example
allow:
  - "*"
refresh: "disabled"
on_failure: "ignore"
namespace_boundary: "shared"
test_forbidden_access: false
```
- **Expected answer / model solution:** Defects to identify: (1) the fake credential is embedded directly in configuration; replace it with a reference/injection from the approved secret source and ensure it never enters committed files or logs; (2) broad access (`read_all_paths` / wildcard allow) violates least privilege; narrow to the exact required path/actions; (3) audit disabled or failure ignored removes important evidence and can conceal outages; enable and monitor appropriate audit/reconciliation evidence; (4) missing owner or shared namespace boundary prevents accountability and can permit cross-tenant access; define owner and enforce scope; (5) unbounded/disabled TTL or refresh policy can leave stale credentials; set lifecycle behavior appropriate to workload and monitor expiry; (6) no forbidden-access test means the policy is unproven. Verification: positive test for the intended consumer, negative test for a neighboring identity/path, review emitted audit/conditions, and ensure the synthetic value is absent from repository history/artifacts.
- **Common wrong answers:** Only changing the fake value is not enough. Broad permissions cannot be justified by a successful happy path. Enabling a feature without testing its effective behavior is not verification. A TTL must be compatible with consumer refresh and job duration.
- **Scoring rubric:** 8 points: identify defects 3; impact/fix 3; positive and negative verification 2. Partial credit for equivalent safe corrections.
- **Safety/version note:** Illustrative pseudo-configuration, not a valid product schema. Any exact fields/commands are [VERIFY] for the named version.

### M09-U03-Q12 — incident/troubleshooting

- **Level:** L3
- **Type:** incident/troubleshooting
- **Objective tested:** predict effects of lease, prefix, token, and backend credential revocation
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** Incident: an alert indicates a possible failure or exposure involving **revocation blast radius**. The service is important but the evidence is incomplete; only synthetic logs are available in the exercise. Give an ordered response using diagnose → blast-radius/revocation check → contain → scope → eradicate → recover → prevent. Identify the first action and why.
- **Expected answer / model solution:** First preserve the alert/event identifiers and time window without copying the credential into chat or a ticket. Quickly determine credential type, privilege, validity, consumers, and whether safe immediate revocation/rotation is warranted; when compromise is credible and the credential may still be valid, invalidate/rotate before Git or artifact cleanup. Contain affected identities/paths, scope access using audit logs and deployment/artifact metadata, clean exposed copies as hygiene, restore with a known-good credential and controlled rollout, verify the old credential fails through an authorized test, then add missing inventory, detector, owner, and runbook controls. If evidence is insufficient, state uncertainty and escalate rather than inventing facts.
- **Common wrong answers:** Purging files first delays containment. Restarting everything without mapping dependencies may cause avoidable outage. Deleting evidence or pasting the secret into a ticket destroys safety and investigation quality.
- **Scoring rubric:** 8 points: first action/rationale 1; blast radius and revocation 2; scope/evidence 1; recovery/verification 2; prevention/ownership 1; safe uncertainty 1.
- **Safety/version note:** Synthetic incident only; do not validate a credential against a live third-party service.

### M09-U03-Q13 — incident/troubleshooting

- **Level:** L3
- **Type:** incident/troubleshooting
- **Objective tested:** measure renewal failures, lease age, expiry risk, auth errors, and rotation lag
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** Incident: an alert indicates a possible failure or exposure involving **monitoring and alerts**. The service is important but the evidence is incomplete; only synthetic logs are available in the exercise. Give an ordered response using diagnose → blast-radius/revocation check → contain → scope → eradicate → recover → prevent. Identify the first action and why.
- **Expected answer / model solution:** First preserve the alert/event identifiers and time window without copying the credential into chat or a ticket. Quickly determine credential type, privilege, validity, consumers, and whether safe immediate revocation/rotation is warranted; when compromise is credible and the credential may still be valid, invalidate/rotate before Git or artifact cleanup. Contain affected identities/paths, scope access using audit logs and deployment/artifact metadata, clean exposed copies as hygiene, restore with a known-good credential and controlled rollout, verify the old credential fails through an authorized test, then add missing inventory, detector, owner, and runbook controls. If evidence is insufficient, state uncertainty and escalate rather than inventing facts.
- **Common wrong answers:** Purging files first delays containment. Restarting everything without mapping dependencies may cause avoidable outage. Deleting evidence or pasting the secret into a ticket destroys safety and investigation quality.
- **Scoring rubric:** 8 points: first action/rationale 1; blast radius and revocation 2; scope/evidence 1; recovery/verification 2; prevention/ownership 1; safe uncertainty 1.
- **Safety/version note:** Synthetic incident only; do not validate a credential against a live third-party service.

### M09-U03-Q14 — design

- **Level:** L4
- **Type:** design
- **Objective tested:** respond to manager outage, client refresh failure, DB grant error, and expired credentials
- **Estimated time:** [ILLUSTRATIVE] 20 minutes
- **Question / context:** Design a small-platform control for **failure-mode runbooks**. Constraints: zero-budget laptop lab, no live cloud account, two workloads with different privilege levels, and a requirement to demonstrate both permitted and forbidden behavior. State assumptions and failure modes.
- **Expected answer / model solution:** Model answer: start from the data flow and classify the credential; assign an accountable owner and inventory fields; select a delivery/control pattern appropriate to the consumer and freshness requirements; restrict each workload to its minimum path/permission; define rotation/revocation and outage behavior; ensure logs and audit evidence do not reveal the secret; and implement a disposable synthetic positive test plus a negative cross-workload test. Document recovery, cleanup, and what the local simulation cannot prove about a managed provider. A different design earns full credit if it explicitly handles these constraints.
- **Common wrong answers:** A single global credential for both workloads ignores privilege separation. “Use a vault” without auth, policy, lifecycle, audit, and recovery detail is not a design. A local mock is not evidence of cloud-provider parity.
- **Scoring rubric:** 10 points: correctness 2; least privilege 2; lifecycle/recovery 2; failure handling 1; verification/evidence 2; ownership/assumptions 1.
- **Safety/version note:** Provider-specific details remain [VERIFY]; no cloud account is required.

### M09-U03-Q15 — hands-on

- **Level:** L2
- **Type:** hands-on
- **Objective tested:** manage rotation of a fixed database account without confusing it with per-lease dynamic users
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** In a disposable repository/local lab, design a safe test for **static role rotation** using only values such as `FAKE_LAB_SECRET_DO_NOT_USE_7f31`. State the setup, observation, cleanup, and success criteria. Do not run a scan against external systems.
- **Expected answer / model solution:** Create a disposable fixture with one synthetic secret-like value and one harmless negative control. Run the relevant local control using documentation for the installed version, capture only redacted findings/exit status, and test both detection and non-detection cases. Record tool/version, fixture hash, expected result, and cleanup. The success criterion is not just a green run: the positive fixture must be detected (where detection is intended), the negative fixture should not create an unjustified finding, and no real credential is contacted or exposed.
- **Common wrong answers:** Testing only a clean repository does not establish detection coverage. Printing full matched values can create another leak. Skipping the negative fixture hides false-positive risk.
- **Scoring rubric:** 6 points: safe setup 1; positive test 1; negative test 1; evidence 1; cleanup 1; version caveat 1.
- **Safety/version note:** Exact command syntax is [VERIFY] for the installed tool/version; lab is [SIMULATION].

### M09-U03-Q16 — boundary test

- **Level:** L3
- **Type:** boundary test
- **Objective tested:** distinguish encryption-key rotation from re-encryption/rewrap needs where taught
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** Define a negative test for **Transit and rewrap concepts**. The test must demonstrate that a deliberately unauthorized synthetic identity cannot access a resource outside its assigned scope. What must be held constant, and what result counts as failure?
- **Expected answer / model solution:** Use two synthetic identities and two isolated resources. Establish a positive control for the authorized identity, then attempt the forbidden operation with the unauthorized identity while keeping the target, action, and policy state explicit. Denial must be enforced by the system, not merely by hiding a UI or omitting a credential. Capture status/audit evidence without logging secret material. Any success by the unauthorized identity is a failure and requires investigation of inherited policy, wildcard paths, namespace scope, cached credentials, and alternate access paths.
- **Common wrong answers:** A missing credential is not always a valid authorization test because it may test authentication only. Testing only the authorized identity proves no isolation. A client-side block is not an enforcement boundary.
- **Scoring rubric:** 6 points: clear boundary 2; valid positive/negative controls 2; evidence and failure criterion 1; safe handling 1.
- **Safety/version note:** Use local/synthetic identities only; exact denial codes and event names are version-specific [VERIFY].

### M09-U03-Q17 — evidence reasoning

- **Level:** L3
- **Type:** evidence reasoning
- **Objective tested:** define when rollback is unsafe because old credentials have been revoked or suspected compromised
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** You believe **safe rollback** is correctly controlled, but your only evidence is a successful happy-path test and a green dashboard. Name three additional pieces of evidence that would strengthen or overturn the conclusion.
- **Expected answer / model solution:** Useful evidence includes a negative test against an unauthorized identity; an audit trail for the exact principal, path, action, and time; versioned configuration/policy review; evidence that the runtime consumer adopted the intended value; and a documented recovery/rotation test. Evidence that would overturn the conclusion includes an inherited wildcard permission, a stale process value, missing audit coverage, an artifact copy, or a test fixture that never exercised the intended path. State the time window and blind spots.
- **Common wrong answers:** A green dashboard may cover only the scanner/controller's configured scope. A single success says nothing about forbidden access. Absence of logs is not proof that no access occurred.
- **Scoring rubric:** 6 points: three relevant evidence items 3; counterevidence 1; scope/limitations 1; clear verification plan 1.
- **Safety/version note:** All examples are synthetic; evidence completeness depends on configured product/version and retention [VERIFY].

### M09-U03-Q18 — operational trade-off

- **Level:** L4
- **Type:** operational trade-off
- **Objective tested:** balance TTL, job duration, availability, renewal load, and privilege
- **Estimated time:** [ILLUSTRATIVE] 12 minutes
- **Question / context:** Evaluate the trade-off in **operational trade-offs** for (A) a short-running stateless API and (B) a 90-minute ETL job. State which design decisions may differ and which security invariants must remain unchanged.
- **Expected answer / model solution:** The API may tolerate shorter-lived credentials and rapid replacement if it can reacquire and retry safely. The ETL job needs lease/TTL planning, renewal capability, checkpointing, idempotency, connection-pool refresh, and a controlled recovery path. In both cases, least privilege, owner/inventory, auditability, safe handling, and an explicit revocation plan remain invariants. Choose TTLs from measured job duration and renewal behavior, not a universal number; define failure thresholds and alert before expiry.
- **Common wrong answers:** One TTL for every workload ignores duration and recovery. Making the ETL credential effectively permanent to avoid outages trades away bounded exposure. Aggressive expiry without client refresh can create predictable outages.
- **Scoring rubric:** 8 points: compare workload needs 2; preserve security invariants 2; failure handling 2; evidence/monitoring 1; explicit assumptions 1.
- **Safety/version note:** TTL numbers are [ASSUMPTION] unless derived from measured workload and provider constraints.

## Unit 4 — External Secrets Operator and cloud secret managers

### M09-U04-Q01 — short answer

- **Level:** L1
- **Type:** short answer
- **Objective tested:** trace provider value → controller reconciliation → Kubernetes target → application consumer
- **Estimated time:** [ILLUSTRATIVE] 6 minutes
- **Question / context:** Explain **reconciliation flow** for a small data/AI platform. State the key boundary, the principal failure mode, and one control that reduces risk. Use a synthetic service credential; assume no cloud account is available.
- **Expected answer / model solution:** A strong answer should trace provider value → controller reconciliation → Kubernetes target → application consumer; identify the boundary where exposure or misuse can occur; state who can use the credential and for what; and pair prevention with detection/recovery. The practical check is to trace the relevant evidence and test the control in a disposable local environment. Do not infer that a secret is safe merely because it is not visible in the current source file.
- **Common wrong answers:** Saying only “put it in a secret manager” misses consumers, permissions, logs, copies, expiry, and recovery. Treating an absence of findings as proof of no exposure is also unsupported.
- **Scoring rubric:** 4 points: concept 1; boundary/threat 1; actionable control 1; verification/evidence 1. Partial credit for a defensible alternative with explicit assumptions.
- **Safety/version note:** None beyond the synthetic/offline assumptions stated in this question.

### M09-U04-Q02 — short answer

- **Level:** L1
- **Type:** short answer
- **Objective tested:** compare namespaced SecretStore and cluster-scoped store boundaries; verify exact CRD/version
- **Estimated time:** [ILLUSTRATIVE] 7 minutes
- **Question / context:** Explain **store scope** for a small data/AI platform. State the key boundary, the principal failure mode, and one control that reduces risk. Use a synthetic service credential; assume no cloud account is available.
- **Expected answer / model solution:** A strong answer should compare namespaced SecretStore and cluster-scoped store boundaries; verify exact CRD/version; identify the boundary where exposure or misuse can occur; state who can use the credential and for what; and pair prevention with detection/recovery. The practical check is to trace the relevant evidence and test the control in a disposable local environment. Do not infer that a secret is safe merely because it is not visible in the current source file.
- **Common wrong answers:** Saying only “put it in a secret manager” misses consumers, permissions, logs, copies, expiry, and recovery. Treating an absence of findings as proof of no exposure is also unsupported.
- **Scoring rubric:** 4 points: concept 1; boundary/threat 1; actionable control 1; verification/evidence 1. Partial credit for a defensible alternative with explicit assumptions.
- **Safety/version note:** None beyond the synthetic/offline assumptions stated in this question.

### M09-U04-Q03 — short answer

- **Level:** L1
- **Type:** short answer
- **Objective tested:** use workload identity or narrowly scoped provider identity rather than broad static credentials
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Explain **provider authentication** for a small data/AI platform. State the key boundary, the principal failure mode, and one control that reduces risk. Use a synthetic service credential; assume no cloud account is available.
- **Expected answer / model solution:** A strong answer should use workload identity or narrowly scoped provider identity rather than broad static credentials; identify the boundary where exposure or misuse can occur; state who can use the credential and for what; and pair prevention with detection/recovery. The practical check is to trace the relevant evidence and test the control in a disposable local environment. Do not infer that a secret is safe merely because it is not visible in the current source file.
- **Common wrong answers:** Saying only “put it in a secret manager” misses consumers, permissions, logs, copies, expiry, and recovery. Treating an absence of findings as proof of no exposure is also unsupported.
- **Scoring rubric:** 4 points: concept 1; boundary/threat 1; actionable control 1; verification/evidence 1. Partial credit for a defensible alternative with explicit assumptions.
- **Safety/version note:** None beyond the synthetic/offline assumptions stated in this question.

### M09-U04-Q04 — MCQ

- **Level:** L1
- **Type:** MCQ
- **Objective tested:** verify remote object, property, version, target key, and namespace mapping
- **Estimated time:** [ILLUSTRATIVE] 4 minutes
- **Question / context:** Which response best addresses **remote key/property mapping**? Choose one. [ILLUSTRATIVE] The environment is a disposable local lab and the credential is synthetic.

A. Map the complete remote key/property mapping path, restrict access to the minimum consumer, and verify the boundary with a negative test.
B. Rely on a naming convention and assume any component with the same project label is trusted.
C. Delete the visible value immediately and skip revocation, dependency discovery, and audit review.
D. Accept the configuration because the happy path works; do not test forbidden access.
- **Expected answer / model solution:** **Correct: A.** It directly addresses remote key/property mapping and includes a verifiable boundary rather than relying on naming or a single successful request. **B is wrong** because labels/names do not enforce authorization. **C is incomplete** because deleting a copy does not necessarily invalidate a live credential or scope other copies. **D is wrong** because positive tests do not establish least privilege; negative tests are required.
- **Common wrong answers:** Choosing B confuses convention with enforcement. Choosing C mistakes cleanup for containment. Choosing D proves only one permitted path and leaves unauthorized access untested.
- **Scoring rubric:** 4 points: correct option 1; explain A 1; explain why B/C/D fail 2. Partial credit for identifying the key boundary even with a wrong choice.
- **Safety/version note:** Any product-specific commands or fields are [VERIFY] for the exact version; this is a concept question, not proof of product behavior.

### M09-U04-Q05 — MCQ

- **Level:** L2
- **Type:** MCQ
- **Objective tested:** reason about refresh interval, provider outage, status, and last-known value
- **Estimated time:** [ILLUSTRATIVE] 4 minutes
- **Question / context:** Which response best addresses **refresh and stale values**? Choose one. [ILLUSTRATIVE] The environment is a disposable local lab and the credential is synthetic.

A. Use a narrowly scoped identity/policy and inspect the relevant audit/operational evidence before concluding.
B. Rely on a naming convention and assume any component with the same project label is trusted.
C. Delete the visible value immediately and skip revocation, dependency discovery, and audit review.
D. Accept the configuration because the happy path works; do not test forbidden access.
- **Expected answer / model solution:** **Correct: A.** It directly addresses refresh and stale values and includes a verifiable boundary rather than relying on naming or a single successful request. **B is wrong** because labels/names do not enforce authorization. **C is incomplete** because deleting a copy does not necessarily invalidate a live credential or scope other copies. **D is wrong** because positive tests do not establish least privilege; negative tests are required.
- **Common wrong answers:** Choosing B confuses convention with enforcement. Choosing C mistakes cleanup for containment. Choosing D proves only one permitted path and leaves unauthorized access untested.
- **Scoring rubric:** 4 points: correct option 1; explain A 1; explain why B/C/D fail 2. Partial credit for identifying the key boundary even with a wrong choice.
- **Safety/version note:** Any product-specific commands or fields are [VERIFY] for the exact version; this is a concept question, not proof of product behavior.

### M09-U04-Q06 — MCQ

- **Level:** L2
- **Type:** MCQ
- **Objective tested:** distinguish mounted-file updates from environment variables fixed at process start
- **Estimated time:** [ILLUSTRATIVE] 4 minutes
- **Question / context:** Which response best addresses **application reload semantics**? Choose one. [ILLUSTRATIVE] The environment is a disposable local lab and the credential is synthetic.

A. Treat the observed representation as insufficient proof of confidentiality; validate the actual protection boundary and test access.
B. Rely on a naming convention and assume any component with the same project label is trusted.
C. Delete the visible value immediately and skip revocation, dependency discovery, and audit review.
D. Accept the configuration because the happy path works; do not test forbidden access.
- **Expected answer / model solution:** **Correct: A.** It directly addresses application reload semantics and includes a verifiable boundary rather than relying on naming or a single successful request. **B is wrong** because labels/names do not enforce authorization. **C is incomplete** because deleting a copy does not necessarily invalidate a live credential or scope other copies. **D is wrong** because positive tests do not establish least privilege; negative tests are required.
- **Common wrong answers:** Choosing B confuses convention with enforcement. Choosing C mistakes cleanup for containment. Choosing D proves only one permitted path and leaves unauthorized access untested.
- **Scoring rubric:** 4 points: correct option 1; explain A 1; explain why B/C/D fail 2. Partial credit for identifying the key boundary even with a wrong choice.
- **Safety/version note:** Any product-specific commands or fields are [VERIFY] for the exact version; this is a concept question, not proof of product behavior.

### M09-U04-Q07 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** identify mount patterns that may not reflect source-file replacement as expected; verify runtime behavior
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Interpret this representative output and propose the next two verification steps:

```text
[ILLUSTRATIVE] inventory row: owner=unknown; source=CI variable; consumers=etl-worker, notebook-job; expiry=none; last_seen=build-log; audit_source=missing
```
Do not assume omitted fields are healthy.
- **Expected answer / model solution:** The inventory is incomplete and signals high uncertainty: owner, expiry, audit source, and lifecycle runbook are missing. Treat the build-log appearance as an exposure, identify the exact synthetic credential and privileges, notify the accountable incident owner, rotate/revoke if it could be live, then trace consumers and artifacts.
- **Common wrong answers:** Declaring success from one green field is insufficient. For identity, do not stop at signature validity; for freshness, do not equate source update with process adoption; for inventory, do not treat unknown ownership as a reason to delay escalation.
- **Scoring rubric:** 5 points: interpret evidence 2; identify missing evidence 1; safe next steps 1; verification criteria 1.
- **Safety/version note:** Output is synthetic and [ILLUSTRATIVE], not captured from a live product.

### M09-U04-Q08 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** prevent cross-namespace and cross-tenant reads through store/provider IAM
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Interpret this representative output and propose the next two verification steps:

```text
[ILLUSTRATIVE] verifier result: signature=valid; issuer=expected; audience=unexpected-api; subject=repo:demo/project:ref:refs/heads/feature; exp=in-future; policy=role expects refs/heads/main
```
Do not assume omitted fields are healthy.
- **Expected answer / model solution:** The token should be rejected by the stated verifier/role constraints despite a valid signature: audience and subject/ref do not match. Signature validity alone does not prove intended audience or authorization. Check issuer, key/JWKS, time claims, audience, subject, then resulting policy separately.
- **Common wrong answers:** Declaring success from one green field is insufficient. For identity, do not stop at signature validity; for freshness, do not equate source update with process adoption; for inventory, do not treat unknown ownership as a reason to delay escalation.
- **Scoring rubric:** 5 points: interpret evidence 2; identify missing evidence 1; safe next steps 1; verification criteria 1.
- **Safety/version note:** Output is synthetic and [ILLUSTRATIVE], not captured from a live product.

### M09-U04-Q09 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** use conditions, controller logs, events, and provider audit data without assuming one version's event names
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Interpret this representative output and propose the next two verification steps:

```text
[ILLUSTRATIVE] rollout evidence: provider_version=v8; mounted_file_version=v8; process_started_at=09:00; process_loaded_version=v7; env_source=process-start
```
Do not assume omitted fields are healthy.
- **Expected answer / model solution:** The source and mounted file are current but the process still uses a previously loaded value. Determine whether the app reads a file dynamically or loads a value at startup; trigger a controlled reload/restart only after a safe rollout plan, then verify the app actually adopted v8.
- **Common wrong answers:** Declaring success from one green field is insufficient. For identity, do not stop at signature validity; for freshness, do not equate source update with process adoption; for inventory, do not treat unknown ownership as a reason to delay escalation.
- **Scoring rubric:** 5 points: interpret evidence 2; identify missing evidence 1; safe next steps 1; verification criteria 1.
- **Safety/version note:** Output is synthetic and [ILLUSTRATIVE], not captured from a live product.

### M09-U04-Q10 — config review

- **Level:** L2
- **Type:** config review
- **Objective tested:** design bounded retries, backoff, stale-value policy, and alerting
- **Estimated time:** [ILLUSTRATIVE] 12 minutes
- **Question / context:** Review the synthetic configuration for **rate limits and outages**. Find at least three defects, explain impact, provide exact conceptual fixes, and state a verification test.

```yaml
# [ILLUSTRATIVE] unsafe example
secret_value: "FAKE_DO_NOT_USE_7f31"
read_all_paths: true
audit_enabled: false
owner: ""
ttl: "never"
```
- **Expected answer / model solution:** Defects to identify: (1) the fake credential is embedded directly in configuration; replace it with a reference/injection from the approved secret source and ensure it never enters committed files or logs; (2) broad access (`read_all_paths` / wildcard allow) violates least privilege; narrow to the exact required path/actions; (3) audit disabled or failure ignored removes important evidence and can conceal outages; enable and monitor appropriate audit/reconciliation evidence; (4) missing owner or shared namespace boundary prevents accountability and can permit cross-tenant access; define owner and enforce scope; (5) unbounded/disabled TTL or refresh policy can leave stale credentials; set lifecycle behavior appropriate to workload and monitor expiry; (6) no forbidden-access test means the policy is unproven. Verification: positive test for the intended consumer, negative test for a neighboring identity/path, review emitted audit/conditions, and ensure the synthetic value is absent from repository history/artifacts.
- **Common wrong answers:** Only changing the fake value is not enough. Broad permissions cannot be justified by a successful happy path. Enabling a feature without testing its effective behavior is not verification. A TTL must be compatible with consumer refresh and job duration.
- **Scoring rubric:** 8 points: identify defects 3; impact/fix 3; positive and negative verification 2. Partial credit for equivalent safe corrections.
- **Safety/version note:** Illustrative pseudo-configuration, not a valid product schema. Any exact fields/commands are [VERIFY] for the named version.

### M09-U04-Q11 — config review

- **Level:** L2
- **Type:** config review
- **Objective tested:** compare managed provider control plane, access model, availability, audit, and portability
- **Estimated time:** [ILLUSTRATIVE] 12 minutes
- **Question / context:** Review the synthetic configuration for **cloud secret manager trade-offs**. Find at least three defects, explain impact, provide exact conceptual fixes, and state a verification test.

```yaml
# [ILLUSTRATIVE] unsafe example
allow:
  - "*"
refresh: "disabled"
on_failure: "ignore"
namespace_boundary: "shared"
test_forbidden_access: false
```
- **Expected answer / model solution:** Defects to identify: (1) the fake credential is embedded directly in configuration; replace it with a reference/injection from the approved secret source and ensure it never enters committed files or logs; (2) broad access (`read_all_paths` / wildcard allow) violates least privilege; narrow to the exact required path/actions; (3) audit disabled or failure ignored removes important evidence and can conceal outages; enable and monitor appropriate audit/reconciliation evidence; (4) missing owner or shared namespace boundary prevents accountability and can permit cross-tenant access; define owner and enforce scope; (5) unbounded/disabled TTL or refresh policy can leave stale credentials; set lifecycle behavior appropriate to workload and monitor expiry; (6) no forbidden-access test means the policy is unproven. Verification: positive test for the intended consumer, negative test for a neighboring identity/path, review emitted audit/conditions, and ensure the synthetic value is absent from repository history/artifacts.
- **Common wrong answers:** Only changing the fake value is not enough. Broad permissions cannot be justified by a successful happy path. Enabling a feature without testing its effective behavior is not verification. A TTL must be compatible with consumer refresh and job duration.
- **Scoring rubric:** 8 points: identify defects 3; impact/fix 3; positive and negative verification 2. Partial credit for equivalent safe corrections.
- **Safety/version note:** Illustrative pseudo-configuration, not a valid product schema. Any exact fields/commands are [VERIFY] for the named version.

### M09-U04-Q12 — incident/troubleshooting

- **Level:** L3
- **Type:** incident/troubleshooting
- **Objective tested:** choose object materialization versus file mount based on app interface and exposure needs
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** Incident: an alert indicates a possible failure or exposure involving **ESO versus CSI**. The service is important but the evidence is incomplete; only synthetic logs are available in the exercise. Give an ordered response using diagnose → blast-radius/revocation check → contain → scope → eradicate → recover → prevent. Identify the first action and why.
- **Expected answer / model solution:** First preserve the alert/event identifiers and time window without copying the credential into chat or a ticket. Quickly determine credential type, privilege, validity, consumers, and whether safe immediate revocation/rotation is warranted; when compromise is credible and the credential may still be valid, invalidate/rotate before Git or artifact cleanup. Contain affected identities/paths, scope access using audit logs and deployment/artifact metadata, clean exposed copies as hygiene, restore with a known-good credential and controlled rollout, verify the old credential fails through an authorized test, then add missing inventory, detector, owner, and runbook controls. If evidence is insufficient, state uncertainty and escalate rather than inventing facts.
- **Common wrong answers:** Purging files first delays containment. Restarting everything without mapping dependencies may cause avoidable outage. Deleting evidence or pasting the secret into a ticket destroys safety and investigation quality.
- **Scoring rubric:** 8 points: first action/rationale 1; blast radius and revocation 2; scope/evidence 1; recovery/verification 2; prevention/ownership 1; safe uncertainty 1.
- **Safety/version note:** Synthetic incident only; do not validate a credential against a live third-party service.

### M09-U04-Q13 — incident/troubleshooting

- **Level:** L3
- **Type:** incident/troubleshooting
- **Objective tested:** compare Kubernetes controller reconciliation with workload-local rendering/renewal patterns
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** Incident: an alert indicates a possible failure or exposure involving **ESO versus Vault Agent**. The service is important but the evidence is incomplete; only synthetic logs are available in the exercise. Give an ordered response using diagnose → blast-radius/revocation check → contain → scope → eradicate → recover → prevent. Identify the first action and why.
- **Expected answer / model solution:** First preserve the alert/event identifiers and time window without copying the credential into chat or a ticket. Quickly determine credential type, privilege, validity, consumers, and whether safe immediate revocation/rotation is warranted; when compromise is credible and the credential may still be valid, invalidate/rotate before Git or artifact cleanup. Contain affected identities/paths, scope access using audit logs and deployment/artifact metadata, clean exposed copies as hygiene, restore with a known-good credential and controlled rollout, verify the old credential fails through an authorized test, then add missing inventory, detector, owner, and runbook controls. If evidence is insufficient, state uncertainty and escalate rather than inventing facts.
- **Common wrong answers:** Purging files first delays containment. Restarting everything without mapping dependencies may cause avoidable outage. Deleting evidence or pasting the secret into a ticket destroys safety and investigation quality.
- **Scoring rubric:** 8 points: first action/rationale 1; blast radius and revocation 2; scope/evidence 1; recovery/verification 2; prevention/ownership 1; safe uncertainty 1.
- **Safety/version note:** Synthetic incident only; do not validate a credential against a live third-party service.

### M09-U04-Q14 — design

- **Level:** L4
- **Type:** design
- **Objective tested:** evaluate whether a Kubernetes Secret is created/synchronized and the resulting RBAC/etcd exposure
- **Estimated time:** [ILLUSTRATIVE] 20 minutes
- **Question / context:** Design a small-platform control for **Kubernetes target object**. Constraints: zero-budget laptop lab, no live cloud account, two workloads with different privilege levels, and a requirement to demonstrate both permitted and forbidden behavior. State assumptions and failure modes.
- **Expected answer / model solution:** Model answer: start from the data flow and classify the credential; assign an accountable owner and inventory fields; select a delivery/control pattern appropriate to the consumer and freshness requirements; restrict each workload to its minimum path/permission; define rotation/revocation and outage behavior; ensure logs and audit evidence do not reveal the secret; and implement a disposable synthetic positive test plus a negative cross-workload test. Document recovery, cleanup, and what the local simulation cannot prove about a managed provider. A different design earns full credit if it explicitly handles these constraints.
- **Common wrong answers:** A single global credential for both workloads ignores privilege separation. “Use a vault” without auth, policy, lifecycle, audit, and recovery detail is not a design. A local mock is not evidence of cloud-provider parity.
- **Scoring rubric:** 10 points: correctness 2; least privilege 2; lifecycle/recovery 2; failure handling 1; verification/evidence 2; ownership/assumptions 1.
- **Safety/version note:** Provider-specific details remain [VERIFY]; no cloud account is required.

### M09-U04-Q15 — hands-on

- **Level:** L2
- **Type:** hands-on
- **Objective tested:** define whether latest or pinned remote versions are consumed and how changes are deployed
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** In a disposable repository/local lab, design a safe test for **version pinning and rollout** using only values such as `FAKE_LAB_SECRET_DO_NOT_USE_7f31`. State the setup, observation, cleanup, and success criteria. Do not run a scan against external systems.
- **Expected answer / model solution:** Create a disposable fixture with one synthetic secret-like value and one harmless negative control. Run the relevant local control using documentation for the installed version, capture only redacted findings/exit status, and test both detection and non-detection cases. Record tool/version, fixture hash, expected result, and cleanup. The success criterion is not just a green run: the positive fixture must be detected (where detection is intended), the negative fixture should not create an unjustified finding, and no real credential is contacted or exposed.
- **Common wrong answers:** Testing only a clean repository does not establish detection coverage. Printing full matched values can create another leak. Skipping the negative fixture hides false-positive risk.
- **Scoring rubric:** 6 points: safe setup 1; positive test 1; negative test 1; evidence 1; cleanup 1; version caveat 1.
- **Safety/version note:** Exact command syntax is [VERIFY] for the installed tool/version; lab is [SIMULATION].

### M09-U04-Q16 — boundary test

- **Level:** L3
- **Type:** boundary test
- **Objective tested:** prove a workload cannot read a neighboring tenant's secret
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** Define a negative test for **negative tenant test**. The test must demonstrate that a deliberately unauthorized synthetic identity cannot access a resource outside its assigned scope. What must be held constant, and what result counts as failure?
- **Expected answer / model solution:** Use two synthetic identities and two isolated resources. Establish a positive control for the authorized identity, then attempt the forbidden operation with the unauthorized identity while keeping the target, action, and policy state explicit. Denial must be enforced by the system, not merely by hiding a UI or omitting a credential. Capture status/audit evidence without logging secret material. Any success by the unauthorized identity is a failure and requires investigation of inherited policy, wildcard paths, namespace scope, cached credentials, and alternate access paths.
- **Common wrong answers:** A missing credential is not always a valid authorization test because it may test authentication only. Testing only the authorized identity proves no isolation. A client-side block is not an enforcement boundary.
- **Scoring rubric:** 6 points: clear boundary 2; valid positive/negative controls 2; evidence and failure criterion 1; safe handling 1.
- **Safety/version note:** Use local/synthetic identities only; exact denial codes and event names are version-specific [VERIFY].

### M09-U04-Q17 — evidence reasoning

- **Level:** L3
- **Type:** evidence reasoning
- **Objective tested:** verify provider version, target resource update, mounted value metadata, and application behavior
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** You believe **evidence for freshness** is correctly controlled, but your only evidence is a successful happy-path test and a green dashboard. Name three additional pieces of evidence that would strengthen or overturn the conclusion.
- **Expected answer / model solution:** Useful evidence includes a negative test against an unauthorized identity; an audit trail for the exact principal, path, action, and time; versioned configuration/policy review; evidence that the runtime consumer adopted the intended value; and a documented recovery/rotation test. Evidence that would overturn the conclusion includes an inherited wildcard permission, a stale process value, missing audit coverage, an artifact copy, or a test fixture that never exercised the intended path. State the time window and blind spots.
- **Common wrong answers:** A green dashboard may cover only the scanner/controller's configured scope. A single success says nothing about forbidden access. Absence of logs is not proof that no access occurred.
- **Scoring rubric:** 6 points: three relevant evidence items 3; counterevidence 1; scope/limitations 1; clear verification plan 1.
- **Safety/version note:** All examples are synthetic; evidence completeness depends on configured product/version and retention [VERIFY].

### M09-U04-Q18 — operational trade-off

- **Level:** L4
- **Type:** operational trade-off
- **Objective tested:** balance simplicity, consistency delay, API cost/rate limits, failure modes, and operational ownership
- **Estimated time:** [ILLUSTRATIVE] 12 minutes
- **Question / context:** Evaluate the trade-off in **operational trade-offs** for (A) a short-running stateless API and (B) a 90-minute ETL job. State which design decisions may differ and which security invariants must remain unchanged.
- **Expected answer / model solution:** The API may tolerate shorter-lived credentials and rapid replacement if it can reacquire and retry safely. The ETL job needs lease/TTL planning, renewal capability, checkpointing, idempotency, connection-pool refresh, and a controlled recovery path. In both cases, least privilege, owner/inventory, auditability, safe handling, and an explicit revocation plan remain invariants. Choose TTLs from measured job duration and renewal behavior, not a universal number; define failure thresholds and alert before expiry.
- **Common wrong answers:** One TTL for every workload ignores duration and recovery. Making the ETL credential effectively permanent to avoid outages trades away bounded exposure. Aggressive expiry without client refresh can create predictable outages.
- **Scoring rubric:** 8 points: compare workload needs 2; preserve security invariants 2; failure handling 2; evidence/monitoring 1; explicit assumptions 1.
- **Safety/version note:** TTL numbers are [ASSUMPTION] unless derived from measured workload and provider constraints.

## Unit 5 — SOPS, Sealed Secrets, and encrypted secrets in Git

### M09-U05-Q01 — short answer

- **Level:** L1
- **Type:** short answer
- **Objective tested:** identify ciphertext, data-key protection, recipients, private-key locations, and recovery ownership
- **Estimated time:** [ILLUSTRATIVE] 6 minutes
- **Question / context:** Explain **encryption and key custody** for a small data/AI platform. State the key boundary, the principal failure mode, and one control that reduces risk. Use a synthetic service credential; assume no cloud account is available.
- **Expected answer / model solution:** A strong answer should identify ciphertext, data-key protection, recipients, private-key locations, and recovery ownership; identify the boundary where exposure or misuse can occur; state who can use the credential and for what; and pair prevention with detection/recovery. The practical check is to trace the relevant evidence and test the control in a disposable local environment. Do not infer that a secret is safe merely because it is not visible in the current source file.
- **Common wrong answers:** Saying only “put it in a secret manager” misses consumers, permissions, logs, copies, expiry, and recovery. Treating an absence of findings as proof of no exposure is also unsupported.
- **Scoring rubric:** 4 points: concept 1; boundary/threat 1; actionable control 1; verification/evidence 1. Partial credit for a defensible alternative with explicit assumptions.
- **Safety/version note:** None beyond the synthetic/offline assumptions stated in this question.

### M09-U05-Q02 — short answer

- **Level:** L1
- **Type:** short answer
- **Objective tested:** explain which file content is encrypted and where decryption occurs in a GitOps workflow
- **Estimated time:** [ILLUSTRATIVE] 7 minutes
- **Question / context:** Explain **SOPS trust boundary** for a small data/AI platform. State the key boundary, the principal failure mode, and one control that reduces risk. Use a synthetic service credential; assume no cloud account is available.
- **Expected answer / model solution:** A strong answer should explain which file content is encrypted and where decryption occurs in a GitOps workflow; identify the boundary where exposure or misuse can occur; state who can use the credential and for what; and pair prevention with detection/recovery. The practical check is to trace the relevant evidence and test the control in a disposable local environment. Do not infer that a secret is safe merely because it is not visible in the current source file.
- **Common wrong answers:** Saying only “put it in a secret manager” misses consumers, permissions, logs, copies, expiry, and recovery. Treating an absence of findings as proof of no exposure is also unsupported.
- **Scoring rubric:** 4 points: concept 1; boundary/threat 1; actionable control 1; verification/evidence 1. Partial credit for a defensible alternative with explicit assumptions.
- **Safety/version note:** None beyond the synthetic/offline assumptions stated in this question.

### M09-U05-Q03 — short answer

- **Level:** L1
- **Type:** short answer
- **Objective tested:** reason about controller/private-key custody and scope; verify controller/version semantics
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Explain **Sealed Secrets trust boundary** for a small data/AI platform. State the key boundary, the principal failure mode, and one control that reduces risk. Use a synthetic service credential; assume no cloud account is available.
- **Expected answer / model solution:** A strong answer should reason about controller/private-key custody and scope; verify controller/version semantics; identify the boundary where exposure or misuse can occur; state who can use the credential and for what; and pair prevention with detection/recovery. The practical check is to trace the relevant evidence and test the control in a disposable local environment. Do not infer that a secret is safe merely because it is not visible in the current source file.
- **Common wrong answers:** Saying only “put it in a secret manager” misses consumers, permissions, logs, copies, expiry, and recovery. Treating an absence of findings as proof of no exposure is also unsupported.
- **Scoring rubric:** 4 points: concept 1; boundary/threat 1; actionable control 1; verification/evidence 1. Partial credit for a defensible alternative with explicit assumptions.
- **Safety/version note:** None beyond the synthetic/offline assumptions stated in this question.

### M09-U05-Q04 — MCQ

- **Level:** L1
- **Type:** MCQ
- **Objective tested:** explain why encrypted-at-rest Git storage does not replace rotation of an exposed live credential
- **Estimated time:** [ILLUSTRATIVE] 4 minutes
- **Question / context:** Which response best addresses **live-secret leak response**? Choose one. [ILLUSTRATIVE] The environment is a disposable local lab and the credential is synthetic.

A. Map the complete live-secret leak response path, restrict access to the minimum consumer, and verify the boundary with a negative test.
B. Rely on a naming convention and assume any component with the same project label is trusted.
C. Delete the visible value immediately and skip revocation, dependency discovery, and audit review.
D. Accept the configuration because the happy path works; do not test forbidden access.
- **Expected answer / model solution:** **Correct: A.** It directly addresses live-secret leak response and includes a verifiable boundary rather than relying on naming or a single successful request. **B is wrong** because labels/names do not enforce authorization. **C is incomplete** because deleting a copy does not necessarily invalidate a live credential or scope other copies. **D is wrong** because positive tests do not establish least privilege; negative tests are required.
- **Common wrong answers:** Choosing B confuses convention with enforcement. Choosing C mistakes cleanup for containment. Choosing D proves only one permitted path and leaves unauthorized access untested.
- **Scoring rubric:** 4 points: correct option 1; explain A 1; explain why B/C/D fail 2. Partial credit for identifying the key boundary even with a wrong choice.
- **Safety/version note:** Any product-specific commands or fields are [VERIFY] for the exact version; this is a concept question, not proof of product behavior.

### M09-U05-Q05 — MCQ

- **Level:** L2
- **Type:** MCQ
- **Objective tested:** trace render output, diffs, Helm values, CI logs, controller memory, and runtime objects
- **Estimated time:** [ILLUSTRATIVE] 4 minutes
- **Question / context:** Which response best addresses **GitOps plaintext surfaces**? Choose one. [ILLUSTRATIVE] The environment is a disposable local lab and the credential is synthetic.

A. Use a narrowly scoped identity/policy and inspect the relevant audit/operational evidence before concluding.
B. Rely on a naming convention and assume any component with the same project label is trusted.
C. Delete the visible value immediately and skip revocation, dependency discovery, and audit review.
D. Accept the configuration because the happy path works; do not test forbidden access.
- **Expected answer / model solution:** **Correct: A.** It directly addresses GitOps plaintext surfaces and includes a verifiable boundary rather than relying on naming or a single successful request. **B is wrong** because labels/names do not enforce authorization. **C is incomplete** because deleting a copy does not necessarily invalidate a live credential or scope other copies. **D is wrong** because positive tests do not establish least privilege; negative tests are required.
- **Common wrong answers:** Choosing B confuses convention with enforcement. Choosing C mistakes cleanup for containment. Choosing D proves only one permitted path and leaves unauthorized access untested.
- **Scoring rubric:** 4 points: correct option 1; explain A 1; explain why B/C/D fail 2. Partial credit for identifying the key boundary even with a wrong choice.
- **Safety/version note:** Any product-specific commands or fields are [VERIFY] for the exact version; this is a concept question, not proof of product behavior.

### M09-U05-Q06 — MCQ

- **Level:** L2
- **Type:** MCQ
- **Objective tested:** plan adding new recipients, re-encryption, validation, and removal of retired access
- **Estimated time:** [ILLUSTRATIVE] 4 minutes
- **Question / context:** Which response best addresses **recipient/key rotation**? Choose one. [ILLUSTRATIVE] The environment is a disposable local lab and the credential is synthetic.

A. Treat the observed representation as insufficient proof of confidentiality; validate the actual protection boundary and test access.
B. Rely on a naming convention and assume any component with the same project label is trusted.
C. Delete the visible value immediately and skip revocation, dependency discovery, and audit review.
D. Accept the configuration because the happy path works; do not test forbidden access.
- **Expected answer / model solution:** **Correct: A.** It directly addresses recipient/key rotation and includes a verifiable boundary rather than relying on naming or a single successful request. **B is wrong** because labels/names do not enforce authorization. **C is incomplete** because deleting a copy does not necessarily invalidate a live credential or scope other copies. **D is wrong** because positive tests do not establish least privilege; negative tests are required.
- **Common wrong answers:** Choosing B confuses convention with enforcement. Choosing C mistakes cleanup for containment. Choosing D proves only one permitted path and leaves unauthorized access untested.
- **Scoring rubric:** 4 points: correct option 1; explain A 1; explain why B/C/D fail 2. Partial credit for identifying the key boundary even with a wrong choice.
- **Safety/version note:** Any product-specific commands or fields are [VERIFY] for the exact version; this is a concept question, not proof of product behavior.

### M09-U05-Q07 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** evaluate backup/custody and the risk of permanent inability to decrypt repository history
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Interpret this representative output and propose the next two verification steps:

```text
[ILLUSTRATIVE] inventory row: owner=unknown; source=CI variable; consumers=etl-worker, notebook-job; expiry=none; last_seen=build-log; audit_source=missing
```
Do not assume omitted fields are healthy.
- **Expected answer / model solution:** The inventory is incomplete and signals high uncertainty: owner, expiry, audit source, and lifecycle runbook are missing. Treat the build-log appearance as an exposure, identify the exact synthetic credential and privileges, notify the accountable incident owner, rotate/revoke if it could be live, then trace consumers and artifacts.
- **Common wrong answers:** Declaring success from one green field is insufficient. For identity, do not stop at signature validity; for freshness, do not equate source update with process adoption; for inventory, do not treat unknown ownership as a reason to delay escalation.
- **Scoring rubric:** 5 points: interpret evidence 2; identify missing evidence 1; safe next steps 1; verification criteria 1.
- **Safety/version note:** Output is synthetic and [ILLUSTRATIVE], not captured from a live product.

### M09-U05-Q08 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** revoke/replace affected credentials and encryption trust material; assess historical ciphertext
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Interpret this representative output and propose the next two verification steps:

```text
[ILLUSTRATIVE] verifier result: signature=valid; issuer=expected; audience=unexpected-api; subject=repo:demo/project:ref:refs/heads/feature; exp=in-future; policy=role expects refs/heads/main
```
Do not assume omitted fields are healthy.
- **Expected answer / model solution:** The token should be rejected by the stated verifier/role constraints despite a valid signature: audience and subject/ref do not match. Signature validity alone does not prove intended audience or authorization. Check issuer, key/JWKS, time claims, audience, subject, then resulting policy separately.
- **Common wrong answers:** Declaring success from one green field is insufficient. For identity, do not stop at signature validity; for freshness, do not equate source update with process adoption; for inventory, do not treat unknown ownership as a reason to delay escalation.
- **Scoring rubric:** 5 points: interpret evidence 2; identify missing evidence 1; safe next steps 1; verification criteria 1.
- **Safety/version note:** Output is synthetic and [ILLUSTRATIVE], not captured from a live product.

### M09-U05-Q09 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** compare strict namespace/name scope and organizational key boundaries where applicable
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Interpret this representative output and propose the next two verification steps:

```text
[ILLUSTRATIVE] rollout evidence: provider_version=v8; mounted_file_version=v8; process_started_at=09:00; process_loaded_version=v7; env_source=process-start
```
Do not assume omitted fields are healthy.
- **Expected answer / model solution:** The source and mounted file are current but the process still uses a previously loaded value. Determine whether the app reads a file dynamically or loads a value at startup; trigger a controlled reload/restart only after a safe rollout plan, then verify the app actually adopted v8.
- **Common wrong answers:** Declaring success from one green field is insufficient. For identity, do not stop at signature validity; for freshness, do not equate source update with process adoption; for inventory, do not treat unknown ownership as a reason to delay escalation.
- **Scoring rubric:** 5 points: interpret evidence 2; identify missing evidence 1; safe next steps 1; verification criteria 1.
- **Safety/version note:** Output is synthetic and [ILLUSTRATIVE], not captured from a live product.

### M09-U05-Q10 — config review

- **Level:** L2
- **Type:** config review
- **Objective tested:** inspect file matching, encrypted fields, recipient selection, and accidental plaintext exclusions
- **Estimated time:** [ILLUSTRATIVE] 12 minutes
- **Question / context:** Review the synthetic configuration for **SOPS configuration review**. Find at least three defects, explain impact, provide exact conceptual fixes, and state a verification test.

```yaml
# [ILLUSTRATIVE] unsafe example
secret_value: "FAKE_DO_NOT_USE_7f31"
read_all_paths: true
audit_enabled: false
owner: ""
ttl: "never"
```
- **Expected answer / model solution:** Defects to identify: (1) the fake credential is embedded directly in configuration; replace it with a reference/injection from the approved secret source and ensure it never enters committed files or logs; (2) broad access (`read_all_paths` / wildcard allow) violates least privilege; narrow to the exact required path/actions; (3) audit disabled or failure ignored removes important evidence and can conceal outages; enable and monitor appropriate audit/reconciliation evidence; (4) missing owner or shared namespace boundary prevents accountability and can permit cross-tenant access; define owner and enforce scope; (5) unbounded/disabled TTL or refresh policy can leave stale credentials; set lifecycle behavior appropriate to workload and monitor expiry; (6) no forbidden-access test means the policy is unproven. Verification: positive test for the intended consumer, negative test for a neighboring identity/path, review emitted audit/conditions, and ensure the synthetic value is absent from repository history/artifacts.
- **Common wrong answers:** Only changing the fake value is not enough. Broad permissions cannot be justified by a successful happy path. Enabling a feature without testing its effective behavior is not verification. A TTL must be compatible with consumer refresh and job duration.
- **Scoring rubric:** 8 points: identify defects 3; impact/fix 3; positive and negative verification 2. Partial credit for equivalent safe corrections.
- **Safety/version note:** Illustrative pseudo-configuration, not a valid product schema. Any exact fields/commands are [VERIFY] for the named version.

### M09-U05-Q11 — config review

- **Level:** L2
- **Type:** config review
- **Objective tested:** detect plaintext introduced after decryption or templating
- **Estimated time:** [ILLUSTRATIVE] 12 minutes
- **Question / context:** Review the synthetic configuration for **rendered manifest review**. Find at least three defects, explain impact, provide exact conceptual fixes, and state a verification test.

```yaml
# [ILLUSTRATIVE] unsafe example
allow:
  - "*"
refresh: "disabled"
on_failure: "ignore"
namespace_boundary: "shared"
test_forbidden_access: false
```
- **Expected answer / model solution:** Defects to identify: (1) the fake credential is embedded directly in configuration; replace it with a reference/injection from the approved secret source and ensure it never enters committed files or logs; (2) broad access (`read_all_paths` / wildcard allow) violates least privilege; narrow to the exact required path/actions; (3) audit disabled or failure ignored removes important evidence and can conceal outages; enable and monitor appropriate audit/reconciliation evidence; (4) missing owner or shared namespace boundary prevents accountability and can permit cross-tenant access; define owner and enforce scope; (5) unbounded/disabled TTL or refresh policy can leave stale credentials; set lifecycle behavior appropriate to workload and monitor expiry; (6) no forbidden-access test means the policy is unproven. Verification: positive test for the intended consumer, negative test for a neighboring identity/path, review emitted audit/conditions, and ensure the synthetic value is absent from repository history/artifacts.
- **Common wrong answers:** Only changing the fake value is not enough. Broad permissions cannot be justified by a successful happy path. Enabling a feature without testing its effective behavior is not verification. A TTL must be compatible with consumer refresh and job duration.
- **Scoring rubric:** 8 points: identify defects 3; impact/fix 3; positive and negative verification 2. Partial credit for equivalent safe corrections.
- **Safety/version note:** Illustrative pseudo-configuration, not a valid product schema. Any exact fields/commands are [VERIFY] for the named version.

### M09-U05-Q12 — incident/troubleshooting

- **Level:** L3
- **Type:** incident/troubleshooting
- **Objective tested:** distinguish history cleanup from credential invalidation and downstream clone handling
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** Incident: an alert indicates a possible failure or exposure involving **Git history hygiene**. The service is important but the evidence is incomplete; only synthetic logs are available in the exercise. Give an ordered response using diagnose → blast-radius/revocation check → contain → scope → eradicate → recover → prevent. Identify the first action and why.
- **Expected answer / model solution:** First preserve the alert/event identifiers and time window without copying the credential into chat or a ticket. Quickly determine credential type, privilege, validity, consumers, and whether safe immediate revocation/rotation is warranted; when compromise is credible and the credential may still be valid, invalidate/rotate before Git or artifact cleanup. Contain affected identities/paths, scope access using audit logs and deployment/artifact metadata, clean exposed copies as hygiene, restore with a known-good credential and controlled rollout, verify the old credential fails through an authorized test, then add missing inventory, detector, owner, and runbook controls. If evidence is insufficient, state uncertainty and escalate rather than inventing facts.
- **Common wrong answers:** Purging files first delays containment. Restarting everything without mapping dependencies may cause avoidable outage. Deleting evidence or pasting the secret into a ticket destroys safety and investigation quality.
- **Scoring rubric:** 8 points: first action/rationale 1; blast radius and revocation 2; scope/evidence 1; recovery/verification 2; prevention/ownership 1; safe uncertainty 1.
- **Safety/version note:** Synthetic incident only; do not validate a credential against a live third-party service.

### M09-U05-Q13 — incident/troubleshooting

- **Level:** L3
- **Type:** incident/troubleshooting
- **Objective tested:** limit which jobs/branches/environments can access decryption keys
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** Incident: an alert indicates a possible failure or exposure involving **CI decryption permissions**. The service is important but the evidence is incomplete; only synthetic logs are available in the exercise. Give an ordered response using diagnose → blast-radius/revocation check → contain → scope → eradicate → recover → prevent. Identify the first action and why.
- **Expected answer / model solution:** First preserve the alert/event identifiers and time window without copying the credential into chat or a ticket. Quickly determine credential type, privilege, validity, consumers, and whether safe immediate revocation/rotation is warranted; when compromise is credible and the credential may still be valid, invalidate/rotate before Git or artifact cleanup. Contain affected identities/paths, scope access using audit logs and deployment/artifact metadata, clean exposed copies as hygiene, restore with a known-good credential and controlled rollout, verify the old credential fails through an authorized test, then add missing inventory, detector, owner, and runbook controls. If evidence is insufficient, state uncertainty and escalate rather than inventing facts.
- **Common wrong answers:** Purging files first delays containment. Restarting everything without mapping dependencies may cause avoidable outage. Deleting evidence or pasting the secret into a ticket destroys safety and investigation quality.
- **Scoring rubric:** 8 points: first action/rationale 1; blast radius and revocation 2; scope/evidence 1; recovery/verification 2; prevention/ownership 1; safe uncertainty 1.
- **Safety/version note:** Synthetic incident only; do not validate a credential against a live third-party service.

### M09-U05-Q14 — design

- **Level:** L4
- **Type:** design
- **Objective tested:** choose encrypted Git, ESO, CSI, Vault Agent, dynamic credentials, or workload identity
- **Estimated time:** [ILLUSTRATIVE] 20 minutes
- **Question / context:** Design a small-platform control for **pattern selection**. Constraints: zero-budget laptop lab, no live cloud account, two workloads with different privilege levels, and a requirement to demonstrate both permitted and forbidden behavior. State assumptions and failure modes.
- **Expected answer / model solution:** Model answer: start from the data flow and classify the credential; assign an accountable owner and inventory fields; select a delivery/control pattern appropriate to the consumer and freshness requirements; restrict each workload to its minimum path/permission; define rotation/revocation and outage behavior; ensure logs and audit evidence do not reveal the secret; and implement a disposable synthetic positive test plus a negative cross-workload test. Document recovery, cleanup, and what the local simulation cannot prove about a managed provider. A different design earns full credit if it explicitly handles these constraints.
- **Common wrong answers:** A single global credential for both workloads ignores privilege separation. “Use a vault” without auth, policy, lifecycle, audit, and recovery detail is not a design. A local mock is not evidence of cloud-provider parity.
- **Scoring rubric:** 10 points: correctness 2; least privilege 2; lifecycle/recovery 2; failure handling 1; verification/evidence 2; ownership/assumptions 1.
- **Safety/version note:** Provider-specific details remain [VERIFY]; no cloud account is required.

### M09-U05-Q15 — hands-on

- **Level:** L2
- **Type:** hands-on
- **Objective tested:** verify unauthorized identities cannot decrypt protected content
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** In a disposable repository/local lab, design a safe test for **negative decryption tests** using only values such as `FAKE_LAB_SECRET_DO_NOT_USE_7f31`. State the setup, observation, cleanup, and success criteria. Do not run a scan against external systems.
- **Expected answer / model solution:** Create a disposable fixture with one synthetic secret-like value and one harmless negative control. Run the relevant local control using documentation for the installed version, capture only redacted findings/exit status, and test both detection and non-detection cases. Record tool/version, fixture hash, expected result, and cleanup. The success criterion is not just a green run: the positive fixture must be detected (where detection is intended), the negative fixture should not create an unjustified finding, and no real credential is contacted or exposed.
- **Common wrong answers:** Testing only a clean repository does not establish detection coverage. Printing full matched values can create another leak. Skipping the negative fixture hides false-positive risk.
- **Scoring rubric:** 6 points: safe setup 1; positive test 1; negative test 1; evidence 1; cleanup 1; version caveat 1.
- **Safety/version note:** Exact command syntax is [VERIFY] for the installed tool/version; lab is [SIMULATION].

### M09-U05-Q16 — boundary test

- **Level:** L3
- **Type:** boundary test
- **Objective tested:** test authorized recovery from backed-up key material in a disposable environment
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** Define a negative test for **recovery exercise**. The test must demonstrate that a deliberately unauthorized synthetic identity cannot access a resource outside its assigned scope. What must be held constant, and what result counts as failure?
- **Expected answer / model solution:** Use two synthetic identities and two isolated resources. Establish a positive control for the authorized identity, then attempt the forbidden operation with the unauthorized identity while keeping the target, action, and policy state explicit. Denial must be enforced by the system, not merely by hiding a UI or omitting a credential. Capture status/audit evidence without logging secret material. Any success by the unauthorized identity is a failure and requires investigation of inherited policy, wildcard paths, namespace scope, cached credentials, and alternate access paths.
- **Common wrong answers:** A missing credential is not always a valid authorization test because it may test authentication only. Testing only the authorized identity proves no isolation. A client-side block is not an enforcement boundary.
- **Scoring rubric:** 6 points: clear boundary 2; valid positive/negative controls 2; evidence and failure criterion 1; safe handling 1.
- **Safety/version note:** Use local/synthetic identities only; exact denial codes and event names are version-specific [VERIFY].

### M09-U05-Q17 — evidence reasoning

- **Level:** L3
- **Type:** evidence reasoning
- **Objective tested:** verify sensitive fields are encrypted while metadata and intended public values remain readable
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** You believe **evidence for encryption coverage** is correctly controlled, but your only evidence is a successful happy-path test and a green dashboard. Name three additional pieces of evidence that would strengthen or overturn the conclusion.
- **Expected answer / model solution:** Useful evidence includes a negative test against an unauthorized identity; an audit trail for the exact principal, path, action, and time; versioned configuration/policy review; evidence that the runtime consumer adopted the intended value; and a documented recovery/rotation test. Evidence that would overturn the conclusion includes an inherited wildcard permission, a stale process value, missing audit coverage, an artifact copy, or a test fixture that never exercised the intended path. State the time window and blind spots.
- **Common wrong answers:** A green dashboard may cover only the scanner/controller's configured scope. A single success says nothing about forbidden access. Absence of logs is not proof that no access occurred.
- **Scoring rubric:** 6 points: three relevant evidence items 3; counterevidence 1; scope/limitations 1; clear verification plan 1.
- **Safety/version note:** All examples are synthetic; evidence completeness depends on configured product/version and retention [VERIFY].

### M09-U05-Q18 — operational trade-off

- **Level:** L4
- **Type:** operational trade-off
- **Objective tested:** balance reviewability, controller dependence, key custody, recovery, and secret freshness
- **Estimated time:** [ILLUSTRATIVE] 12 minutes
- **Question / context:** Evaluate the trade-off in **operational trade-offs** for (A) a short-running stateless API and (B) a 90-minute ETL job. State which design decisions may differ and which security invariants must remain unchanged.
- **Expected answer / model solution:** The API may tolerate shorter-lived credentials and rapid replacement if it can reacquire and retry safely. The ETL job needs lease/TTL planning, renewal capability, checkpointing, idempotency, connection-pool refresh, and a controlled recovery path. In both cases, least privilege, owner/inventory, auditability, safe handling, and an explicit revocation plan remain invariants. Choose TTLs from measured job duration and renewal behavior, not a universal number; define failure thresholds and alert before expiry.
- **Common wrong answers:** One TTL for every workload ignores duration and recovery. Making the ETL credential effectively permanent to avoid outages trades away bounded exposure. Aggressive expiry without client refresh can create predictable outages.
- **Scoring rubric:** 8 points: compare workload needs 2; preserve security invariants 2; failure handling 2; evidence/monitoring 1; explicit assumptions 1.
- **Safety/version note:** TTL numbers are [ASSUMPTION] unless derived from measured workload and provider constraints.

## Unit 6 — Kubernetes Secret encryption and the CSI Secret Store

### M09-U06-Q01 — short answer

- **Level:** L1
- **Type:** short answer
- **Objective tested:** distinguish Kubernetes object access controls from value encoding
- **Estimated time:** [ILLUSTRATIVE] 6 minutes
- **Question / context:** Explain **Secret API and Base64** for a small data/AI platform. State the key boundary, the principal failure mode, and one control that reduces risk. Use a synthetic service credential; assume no cloud account is available.
- **Expected answer / model solution:** A strong answer should distinguish Kubernetes object access controls from value encoding; identify the boundary where exposure or misuse can occur; state who can use the credential and for what; and pair prevention with detection/recovery. The practical check is to trace the relevant evidence and test the control in a disposable local environment. Do not infer that a secret is safe merely because it is not visible in the current source file.
- **Common wrong answers:** Saying only “put it in a secret manager” misses consumers, permissions, logs, copies, expiry, and recovery. Treating an absence of findings as proof of no exposure is also unsupported.
- **Scoring rubric:** 4 points: concept 1; boundary/threat 1; actionable control 1; verification/evidence 1. Partial credit for a defensible alternative with explicit assumptions.
- **Safety/version note:** None beyond the synthetic/offline assumptions stated in this question.

### M09-U06-Q02 — short answer

- **Level:** L1
- **Type:** short answer
- **Objective tested:** explain encryption-at-rest boundary and why existing objects may need migration/rewrite
- **Estimated time:** [ILLUSTRATIVE] 7 minutes
- **Question / context:** Explain **API server and etcd encryption** for a small data/AI platform. State the key boundary, the principal failure mode, and one control that reduces risk. Use a synthetic service credential; assume no cloud account is available.
- **Expected answer / model solution:** A strong answer should explain encryption-at-rest boundary and why existing objects may need migration/rewrite; identify the boundary where exposure or misuse can occur; state who can use the credential and for what; and pair prevention with detection/recovery. The practical check is to trace the relevant evidence and test the control in a disposable local environment. Do not infer that a secret is safe merely because it is not visible in the current source file.
- **Common wrong answers:** Saying only “put it in a secret manager” misses consumers, permissions, logs, copies, expiry, and recovery. Treating an absence of findings as proof of no exposure is also unsupported.
- **Scoring rubric:** 4 points: concept 1; boundary/threat 1; actionable control 1; verification/evidence 1. Partial credit for a defensible alternative with explicit assumptions.
- **Safety/version note:** None beyond the synthetic/offline assumptions stated in this question.

### M09-U06-Q03 — short answer

- **Level:** L1
- **Type:** short answer
- **Objective tested:** plan encryption key access, rotation, retained old keys, recovery, and managed-cluster ownership
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Explain **key custody and rotation** for a small data/AI platform. State the key boundary, the principal failure mode, and one control that reduces risk. Use a synthetic service credential; assume no cloud account is available.
- **Expected answer / model solution:** A strong answer should plan encryption key access, rotation, retained old keys, recovery, and managed-cluster ownership; identify the boundary where exposure or misuse can occur; state who can use the credential and for what; and pair prevention with detection/recovery. The practical check is to trace the relevant evidence and test the control in a disposable local environment. Do not infer that a secret is safe merely because it is not visible in the current source file.
- **Common wrong answers:** Saying only “put it in a secret manager” misses consumers, permissions, logs, copies, expiry, and recovery. Treating an absence of findings as proof of no exposure is also unsupported.
- **Scoring rubric:** 4 points: concept 1; boundary/threat 1; actionable control 1; verification/evidence 1. Partial credit for a defensible alternative with explicit assumptions.
- **Safety/version note:** None beyond the synthetic/offline assumptions stated in this question.

### M09-U06-Q04 — MCQ

- **Level:** L1
- **Type:** MCQ
- **Objective tested:** restrict get/list/watch and use audit evidence to investigate reads
- **Estimated time:** [ILLUSTRATIVE] 4 minutes
- **Question / context:** Which response best addresses **RBAC and audit**? Choose one. [ILLUSTRATIVE] The environment is a disposable local lab and the credential is synthetic.

A. Map the complete RBAC and audit path, restrict access to the minimum consumer, and verify the boundary with a negative test.
B. Rely on a naming convention and assume any component with the same project label is trusted.
C. Delete the visible value immediately and skip revocation, dependency discovery, and audit review.
D. Accept the configuration because the happy path works; do not test forbidden access.
- **Expected answer / model solution:** **Correct: A.** It directly addresses RBAC and audit and includes a verifiable boundary rather than relying on naming or a single successful request. **B is wrong** because labels/names do not enforce authorization. **C is incomplete** because deleting a copy does not necessarily invalidate a live credential or scope other copies. **D is wrong** because positive tests do not establish least privilege; negative tests are required.
- **Common wrong answers:** Choosing B confuses convention with enforcement. Choosing C mistakes cleanup for containment. Choosing D proves only one permitted path and leaves unauthorized access untested.
- **Scoring rubric:** 4 points: correct option 1; explain A 1; explain why B/C/D fail 2. Partial credit for identifying the key boundary even with a wrong choice.
- **Safety/version note:** Any product-specific commands or fields are [VERIFY] for the exact version; this is a concept question, not proof of product behavior.

### M09-U06-Q05 — MCQ

- **Level:** L2
- **Type:** MCQ
- **Objective tested:** consider privileged workloads, node administrators, process inspection, and mounted files
- **Estimated time:** [ILLUSTRATIVE] 4 minutes
- **Question / context:** Which response best addresses **node/pod/process exposure**? Choose one. [ILLUSTRATIVE] The environment is a disposable local lab and the credential is synthetic.

A. Use a narrowly scoped identity/policy and inspect the relevant audit/operational evidence before concluding.
B. Rely on a naming convention and assume any component with the same project label is trusted.
C. Delete the visible value immediately and skip revocation, dependency discovery, and audit review.
D. Accept the configuration because the happy path works; do not test forbidden access.
- **Expected answer / model solution:** **Correct: A.** It directly addresses node/pod/process exposure and includes a verifiable boundary rather than relying on naming or a single successful request. **B is wrong** because labels/names do not enforce authorization. **C is incomplete** because deleting a copy does not necessarily invalidate a live credential or scope other copies. **D is wrong** because positive tests do not establish least privilege; negative tests are required.
- **Common wrong answers:** Choosing B confuses convention with enforcement. Choosing C mistakes cleanup for containment. Choosing D proves only one permitted path and leaves unauthorized access untested.
- **Scoring rubric:** 4 points: correct option 1; explain A 1; explain why B/C/D fail 2. Partial credit for identifying the key boundary even with a wrong choice.
- **Safety/version note:** Any product-specific commands or fields are [VERIFY] for the exact version; this is a concept question, not proof of product behavior.

### M09-U06-Q06 — MCQ

- **Level:** L2
- **Type:** MCQ
- **Objective tested:** trace workload mount request through CSI driver/provider to secret source
- **Estimated time:** [ILLUSTRATIVE] 4 minutes
- **Question / context:** Which response best addresses **CSI provider flow**? Choose one. [ILLUSTRATIVE] The environment is a disposable local lab and the credential is synthetic.

A. Treat the observed representation as insufficient proof of confidentiality; validate the actual protection boundary and test access.
B. Rely on a naming convention and assume any component with the same project label is trusted.
C. Delete the visible value immediately and skip revocation, dependency discovery, and audit review.
D. Accept the configuration because the happy path works; do not test forbidden access.
- **Expected answer / model solution:** **Correct: A.** It directly addresses CSI provider flow and includes a verifiable boundary rather than relying on naming or a single successful request. **B is wrong** because labels/names do not enforce authorization. **C is incomplete** because deleting a copy does not necessarily invalidate a live credential or scope other copies. **D is wrong** because positive tests do not establish least privilege; negative tests are required.
- **Common wrong answers:** Choosing B confuses convention with enforcement. Choosing C mistakes cleanup for containment. Choosing D proves only one permitted path and leaves unauthorized access untested.
- **Scoring rubric:** 4 points: correct option 1; explain A 1; explain why B/C/D fail 2. Partial credit for identifying the key boundary even with a wrong choice.
- **Safety/version note:** Any product-specific commands or fields are [VERIFY] for the exact version; this is a concept question, not proof of product behavior.

### M09-U06-Q07 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** interpret the resource as a provider/config binding while verifying exact schema/version
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Interpret this representative output and propose the next two verification steps:

```text
[ILLUSTRATIVE] inventory row: owner=unknown; source=CI variable; consumers=etl-worker, notebook-job; expiry=none; last_seen=build-log; audit_source=missing
```
Do not assume omitted fields are healthy.
- **Expected answer / model solution:** The inventory is incomplete and signals high uncertainty: owner, expiry, audit source, and lifecycle runbook are missing. Treat the build-log appearance as an exposure, identify the exact synthetic credential and privileges, notify the accountable incident owner, rotate/revoke if it could be live, then trace consumers and artifacts.
- **Common wrong answers:** Declaring success from one green field is insufficient. For identity, do not stop at signature validity; for freshness, do not equate source update with process adoption; for inventory, do not treat unknown ownership as a reason to delay escalation.
- **Scoring rubric:** 5 points: interpret evidence 2; identify missing evidence 1; safe next steps 1; verification criteria 1.
- **Safety/version note:** Output is synthetic and [ILLUSTRATIVE], not captured from a live product.

### M09-U06-Q08 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** evaluate optional synchronization and the additional object/RBAC/etcd exposure
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Interpret this representative output and propose the next two verification steps:

```text
[ILLUSTRATIVE] verifier result: signature=valid; issuer=expected; audience=unexpected-api; subject=repo:demo/project:ref:refs/heads/feature; exp=in-future; policy=role expects refs/heads/main
```
Do not assume omitted fields are healthy.
- **Expected answer / model solution:** The token should be rejected by the stated verifier/role constraints despite a valid signature: audience and subject/ref do not match. Signature validity alone does not prove intended audience or authorization. Check issuer, key/JWKS, time claims, audience, subject, then resulting policy separately.
- **Common wrong answers:** Declaring success from one green field is insufficient. For identity, do not stop at signature validity; for freshness, do not equate source update with process adoption; for inventory, do not treat unknown ownership as a reason to delay escalation.
- **Scoring rubric:** 5 points: interpret evidence 2; identify missing evidence 1; safe next steps 1; verification criteria 1.
- **Safety/version note:** Output is synthetic and [ILLUSTRATIVE], not captured from a live product.

### M09-U06-Q09 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** separate source rotation, mounted content update, and application reread
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Interpret this representative output and propose the next two verification steps:

```text
[ILLUSTRATIVE] rollout evidence: provider_version=v8; mounted_file_version=v8; process_started_at=09:00; process_loaded_version=v7; env_source=process-start
```
Do not assume omitted fields are healthy.
- **Expected answer / model solution:** The source and mounted file are current but the process still uses a previously loaded value. Determine whether the app reads a file dynamically or loads a value at startup; trigger a controlled reload/restart only after a safe rollout plan, then verify the app actually adopted v8.
- **Common wrong answers:** Declaring success from one green field is insufficient. For identity, do not stop at signature validity; for freshness, do not equate source update with process adoption; for inventory, do not treat unknown ownership as a reason to delay escalation.
- **Scoring rubric:** 5 points: interpret evidence 2; identify missing evidence 1; safe next steps 1; verification criteria 1.
- **Safety/version note:** Output is synthetic and [ILLUSTRATIVE], not captured from a live product.

### M09-U06-Q10 — config review

- **Level:** L2
- **Type:** config review
- **Objective tested:** recognize process-start environment values do not automatically update on source changes
- **Estimated time:** [ILLUSTRATIVE] 12 minutes
- **Question / context:** Review the synthetic configuration for **environment variable limitations**. Find at least three defects, explain impact, provide exact conceptual fixes, and state a verification test.

```yaml
# [ILLUSTRATIVE] unsafe example
secret_value: "FAKE_DO_NOT_USE_7f31"
read_all_paths: true
audit_enabled: false
owner: ""
ttl: "never"
```
- **Expected answer / model solution:** Defects to identify: (1) the fake credential is embedded directly in configuration; replace it with a reference/injection from the approved secret source and ensure it never enters committed files or logs; (2) broad access (`read_all_paths` / wildcard allow) violates least privilege; narrow to the exact required path/actions; (3) audit disabled or failure ignored removes important evidence and can conceal outages; enable and monitor appropriate audit/reconciliation evidence; (4) missing owner or shared namespace boundary prevents accountability and can permit cross-tenant access; define owner and enforce scope; (5) unbounded/disabled TTL or refresh policy can leave stale credentials; set lifecycle behavior appropriate to workload and monitor expiry; (6) no forbidden-access test means the policy is unproven. Verification: positive test for the intended consumer, negative test for a neighboring identity/path, review emitted audit/conditions, and ensure the synthetic value is absent from repository history/artifacts.
- **Common wrong answers:** Only changing the fake value is not enough. Broad permissions cannot be justified by a successful happy path. Enabling a feature without testing its effective behavior is not verification. A TTL must be compatible with consumer refresh and job duration.
- **Scoring rubric:** 8 points: identify defects 3; impact/fix 3; positive and negative verification 2. Partial credit for equivalent safe corrections.
- **Safety/version note:** Illustrative pseudo-configuration, not a valid product schema. Any exact fields/commands are [VERIFY] for the named version.

### M09-U06-Q11 — config review

- **Level:** L2
- **Type:** config review
- **Objective tested:** test the actual mount/update behavior in the named cluster/version
- **Estimated time:** [ILLUSTRATIVE] 12 minutes
- **Question / context:** Review the synthetic configuration for **subPath and file semantics**. Find at least three defects, explain impact, provide exact conceptual fixes, and state a verification test.

```yaml
# [ILLUSTRATIVE] unsafe example
allow:
  - "*"
refresh: "disabled"
on_failure: "ignore"
namespace_boundary: "shared"
test_forbidden_access: false
```
- **Expected answer / model solution:** Defects to identify: (1) the fake credential is embedded directly in configuration; replace it with a reference/injection from the approved secret source and ensure it never enters committed files or logs; (2) broad access (`read_all_paths` / wildcard allow) violates least privilege; narrow to the exact required path/actions; (3) audit disabled or failure ignored removes important evidence and can conceal outages; enable and monitor appropriate audit/reconciliation evidence; (4) missing owner or shared namespace boundary prevents accountability and can permit cross-tenant access; define owner and enforce scope; (5) unbounded/disabled TTL or refresh policy can leave stale credentials; set lifecycle behavior appropriate to workload and monitor expiry; (6) no forbidden-access test means the policy is unproven. Verification: positive test for the intended consumer, negative test for a neighboring identity/path, review emitted audit/conditions, and ensure the synthetic value is absent from repository history/artifacts.
- **Common wrong answers:** Only changing the fake value is not enough. Broad permissions cannot be justified by a successful happy path. Enabling a feature without testing its effective behavior is not verification. A TTL must be compatible with consumer refresh and job duration.
- **Scoring rubric:** 8 points: identify defects 3; impact/fix 3; positive and negative verification 2. Partial credit for equivalent safe corrections.
- **Safety/version note:** Illustrative pseudo-configuration, not a valid product schema. Any exact fields/commands are [VERIFY] for the named version.

### M09-U06-Q12 — incident/troubleshooting

- **Level:** L3
- **Type:** incident/troubleshooting
- **Objective tested:** explain why snapshots may retain plaintext if at-rest encryption was absent or misconfigured
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** Incident: an alert indicates a possible failure or exposure involving **etcd snapshot recovery**. The service is important but the evidence is incomplete; only synthetic logs are available in the exercise. Give an ordered response using diagnose → blast-radius/revocation check → contain → scope → eradicate → recover → prevent. Identify the first action and why.
- **Expected answer / model solution:** First preserve the alert/event identifiers and time window without copying the credential into chat or a ticket. Quickly determine credential type, privilege, validity, consumers, and whether safe immediate revocation/rotation is warranted; when compromise is credible and the credential may still be valid, invalidate/rotate before Git or artifact cleanup. Contain affected identities/paths, scope access using audit logs and deployment/artifact metadata, clean exposed copies as hygiene, restore with a known-good credential and controlled rollout, verify the old credential fails through an authorized test, then add missing inventory, detector, owner, and runbook controls. If evidence is insufficient, state uncertainty and escalate rather than inventing facts.
- **Common wrong answers:** Purging files first delays containment. Restarting everything without mapping dependencies may cause avoidable outage. Deleting evidence or pasting the secret into a ticket destroys safety and investigation quality.
- **Scoring rubric:** 8 points: first action/rationale 1; blast radius and revocation 2; scope/evidence 1; recovery/verification 2; prevention/ownership 1; safe uncertainty 1.
- **Safety/version note:** Synthetic incident only; do not validate a credential against a live third-party service.

### M09-U06-Q13 — incident/troubleshooting

- **Level:** L3
- **Type:** incident/troubleshooting
- **Objective tested:** separate provider-managed control-plane capabilities from customer-configurable settings
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** Incident: an alert indicates a possible failure or exposure involving **managed cluster differences**. The service is important but the evidence is incomplete; only synthetic logs are available in the exercise. Give an ordered response using diagnose → blast-radius/revocation check → contain → scope → eradicate → recover → prevent. Identify the first action and why.
- **Expected answer / model solution:** First preserve the alert/event identifiers and time window without copying the credential into chat or a ticket. Quickly determine credential type, privilege, validity, consumers, and whether safe immediate revocation/rotation is warranted; when compromise is credible and the credential may still be valid, invalidate/rotate before Git or artifact cleanup. Contain affected identities/paths, scope access using audit logs and deployment/artifact metadata, clean exposed copies as hygiene, restore with a known-good credential and controlled rollout, verify the old credential fails through an authorized test, then add missing inventory, detector, owner, and runbook controls. If evidence is insufficient, state uncertainty and escalate rather than inventing facts.
- **Common wrong answers:** Purging files first delays containment. Restarting everything without mapping dependencies may cause avoidable outage. Deleting evidence or pasting the secret into a ticket destroys safety and investigation quality.
- **Scoring rubric:** 8 points: first action/rationale 1; blast radius and revocation 2; scope/evidence 1; recovery/verification 2; prevention/ownership 1; safe uncertainty 1.
- **Safety/version note:** Synthetic incident only; do not validate a credential against a live third-party service.

### M09-U06-Q14 — design

- **Level:** L4
- **Type:** design
- **Objective tested:** reason about data keys, key-encryption keys, provider reachability, and outage modes
- **Estimated time:** [ILLUSTRATIVE] 20 minutes
- **Question / context:** Design a small-platform control for **KMS/envelope concepts**. Constraints: zero-budget laptop lab, no live cloud account, two workloads with different privilege levels, and a requirement to demonstrate both permitted and forbidden behavior. State assumptions and failure modes.
- **Expected answer / model solution:** Model answer: start from the data flow and classify the credential; assign an accountable owner and inventory fields; select a delivery/control pattern appropriate to the consumer and freshness requirements; restrict each workload to its minimum path/permission; define rotation/revocation and outage behavior; ensure logs and audit evidence do not reveal the secret; and implement a disposable synthetic positive test plus a negative cross-workload test. Document recovery, cleanup, and what the local simulation cannot prove about a managed provider. A different design earns full credit if it explicitly handles these constraints.
- **Common wrong answers:** A single global credential for both workloads ignores privilege separation. “Use a vault” without auth, policy, lifecycle, audit, and recovery detail is not a design. A local mock is not evidence of cloud-provider parity.
- **Scoring rubric:** 10 points: correctness 2; least privilege 2; lifecycle/recovery 2; failure handling 1; verification/evidence 2; ownership/assumptions 1.
- **Safety/version note:** Provider-specific details remain [VERIFY]; no cloud account is required.

### M09-U06-Q15 — hands-on

- **Level:** L2
- **Type:** hands-on
- **Objective tested:** prove an unauthorized service account cannot read a Secret or enumerate unrelated objects
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** In a disposable repository/local lab, design a safe test for **negative RBAC test** using only values such as `FAKE_LAB_SECRET_DO_NOT_USE_7f31`. State the setup, observation, cleanup, and success criteria. Do not run a scan against external systems.
- **Expected answer / model solution:** Create a disposable fixture with one synthetic secret-like value and one harmless negative control. Run the relevant local control using documentation for the installed version, capture only redacted findings/exit status, and test both detection and non-detection cases. Record tool/version, fixture hash, expected result, and cleanup. The success criterion is not just a green run: the positive fixture must be detected (where detection is intended), the negative fixture should not create an unjustified finding, and no real credential is contacted or exposed.
- **Common wrong answers:** Testing only a clean repository does not establish detection coverage. Printing full matched values can create another leak. Skipping the negative fixture hides false-positive risk.
- **Scoring rubric:** 6 points: safe setup 1; positive test 1; negative test 1; evidence 1; cleanup 1; version caveat 1.
- **Safety/version note:** Exact command syntax is [VERIFY] for the installed tool/version; lab is [SIMULATION].

### M09-U06-Q16 — boundary test

- **Level:** L3
- **Type:** boundary test
- **Objective tested:** verify encryption status using supported safe procedures rather than assuming config alone is enough
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** Define a negative test for **existing-object migration**. The test must demonstrate that a deliberately unauthorized synthetic identity cannot access a resource outside its assigned scope. What must be held constant, and what result counts as failure?
- **Expected answer / model solution:** Use two synthetic identities and two isolated resources. Establish a positive control for the authorized identity, then attempt the forbidden operation with the unauthorized identity while keeping the target, action, and policy state explicit. Denial must be enforced by the system, not merely by hiding a UI or omitting a credential. Capture status/audit evidence without logging secret material. Any success by the unauthorized identity is a failure and requires investigation of inherited policy, wildcard paths, namespace scope, cached credentials, and alternate access paths.
- **Common wrong answers:** A missing credential is not always a valid authorization test because it may test authentication only. Testing only the authorized identity proves no isolation. A client-side block is not an enforcement boundary.
- **Scoring rubric:** 6 points: clear boundary 2; valid positive/negative controls 2; evidence and failure criterion 1; safe handling 1.
- **Safety/version note:** Use local/synthetic identities only; exact denial codes and event names are version-specific [VERIFY].

### M09-U06-Q17 — evidence reasoning

- **Level:** L3
- **Type:** evidence reasoning
- **Objective tested:** evaluate whether backups and retained keys can restore data safely
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** You believe **recovery and key loss** is correctly controlled, but your only evidence is a successful happy-path test and a green dashboard. Name three additional pieces of evidence that would strengthen or overturn the conclusion.
- **Expected answer / model solution:** Useful evidence includes a negative test against an unauthorized identity; an audit trail for the exact principal, path, action, and time; versioned configuration/policy review; evidence that the runtime consumer adopted the intended value; and a documented recovery/rotation test. Evidence that would overturn the conclusion includes an inherited wildcard permission, a stale process value, missing audit coverage, an artifact copy, or a test fixture that never exercised the intended path. State the time window and blind spots.
- **Common wrong answers:** A green dashboard may cover only the scanner/controller's configured scope. A single success says nothing about forbidden access. Absence of logs is not proof that no access occurred.
- **Scoring rubric:** 6 points: three relevant evidence items 3; counterevidence 1; scope/limitations 1; clear verification plan 1.
- **Safety/version note:** All examples are synthetic; evidence completeness depends on configured product/version and retention [VERIFY].

### M09-U06-Q18 — operational trade-off

- **Level:** L4
- **Type:** operational trade-off
- **Objective tested:** balance API object integration, file mounts, key custody, portability, and application reload
- **Estimated time:** [ILLUSTRATIVE] 12 minutes
- **Question / context:** Evaluate the trade-off in **operational trade-offs** for (A) a short-running stateless API and (B) a 90-minute ETL job. State which design decisions may differ and which security invariants must remain unchanged.
- **Expected answer / model solution:** The API may tolerate shorter-lived credentials and rapid replacement if it can reacquire and retry safely. The ETL job needs lease/TTL planning, renewal capability, checkpointing, idempotency, connection-pool refresh, and a controlled recovery path. In both cases, least privilege, owner/inventory, auditability, safe handling, and an explicit revocation plan remain invariants. Choose TTLs from measured job duration and renewal behavior, not a universal number; define failure thresholds and alert before expiry.
- **Common wrong answers:** One TTL for every workload ignores duration and recovery. Making the ETL credential effectively permanent to avoid outages trades away bounded exposure. Aggressive expiry without client refresh can create predictable outages.
- **Scoring rubric:** 8 points: compare workload needs 2; preserve security invariants 2; failure handling 2; evidence/monitoring 1; explicit assumptions 1.
- **Safety/version note:** TTL numbers are [ASSUMPTION] unless derived from measured workload and provider constraints.

## Unit 7 — Workload identity, IRSA, and federated credentials

### M09-U07-Q01 — short answer

- **Level:** L1
- **Type:** short answer
- **Objective tested:** explain short-lived identity exchange and residual token/metadata risks
- **Estimated time:** [ILLUSTRATIVE] 6 minutes
- **Question / context:** Explain **workload identity versus static keys** for a small data/AI platform. State the key boundary, the principal failure mode, and one control that reduces risk. Use a synthetic service credential; assume no cloud account is available.
- **Expected answer / model solution:** A strong answer should explain short-lived identity exchange and residual token/metadata risks; identify the boundary where exposure or misuse can occur; state who can use the credential and for what; and pair prevention with detection/recovery. The practical check is to trace the relevant evidence and test the control in a disposable local environment. Do not infer that a secret is safe merely because it is not visible in the current source file.
- **Common wrong answers:** Saying only “put it in a secret manager” misses consumers, permissions, logs, copies, expiry, and recovery. Treating an absence of findings as proof of no exposure is also unsupported.
- **Scoring rubric:** 4 points: concept 1; boundary/threat 1; actionable control 1; verification/evidence 1. Partial credit for a defensible alternative with explicit assumptions.
- **Safety/version note:** None beyond the synthetic/offline assumptions stated in this question.

### M09-U07-Q02 — short answer

- **Level:** L1
- **Type:** short answer
- **Objective tested:** validate signature/key, issuer, audience, subject, not-before/expiry, and algorithm policy
- **Estimated time:** [ILLUSTRATIVE] 7 minutes
- **Question / context:** Explain **JWT validation** for a small data/AI platform. State the key boundary, the principal failure mode, and one control that reduces risk. Use a synthetic service credential; assume no cloud account is available.
- **Expected answer / model solution:** A strong answer should validate signature/key, issuer, audience, subject, not-before/expiry, and algorithm policy; identify the boundary where exposure or misuse can occur; state who can use the credential and for what; and pair prevention with detection/recovery. The practical check is to trace the relevant evidence and test the control in a disposable local environment. Do not infer that a secret is safe merely because it is not visible in the current source file.
- **Common wrong answers:** Saying only “put it in a secret manager” misses consumers, permissions, logs, copies, expiry, and recovery. Treating an absence of findings as proof of no exposure is also unsupported.
- **Scoring rubric:** 4 points: concept 1; boundary/threat 1; actionable control 1; verification/evidence 1. Partial credit for a defensible alternative with explicit assumptions.
- **Safety/version note:** None beyond the synthetic/offline assumptions stated in this question.

### M09-U07-Q03 — short answer

- **Level:** L1
- **Type:** short answer
- **Objective tested:** describe discovery metadata, signing keys, rotation, cache behavior, and safe failure
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Explain **OIDC discovery and JWKS** for a small data/AI platform. State the key boundary, the principal failure mode, and one control that reduces risk. Use a synthetic service credential; assume no cloud account is available.
- **Expected answer / model solution:** A strong answer should describe discovery metadata, signing keys, rotation, cache behavior, and safe failure; identify the boundary where exposure or misuse can occur; state who can use the credential and for what; and pair prevention with detection/recovery. The practical check is to trace the relevant evidence and test the control in a disposable local environment. Do not infer that a secret is safe merely because it is not visible in the current source file.
- **Common wrong answers:** Saying only “put it in a secret manager” misses consumers, permissions, logs, copies, expiry, and recovery. Treating an absence of findings as proof of no exposure is also unsupported.
- **Scoring rubric:** 4 points: concept 1; boundary/threat 1; actionable control 1; verification/evidence 1. Partial credit for a defensible alternative with explicit assumptions.
- **Safety/version note:** None beyond the synthetic/offline assumptions stated in this question.

### M09-U07-Q04 — MCQ

- **Level:** L1
- **Type:** MCQ
- **Objective tested:** separate accepted identity from permissions granted by the target service
- **Estimated time:** [ILLUSTRATIVE] 4 minutes
- **Question / context:** Which response best addresses **authentication versus authorization**? Choose one. [ILLUSTRATIVE] The environment is a disposable local lab and the credential is synthetic.

A. Map the complete authentication versus authorization path, restrict access to the minimum consumer, and verify the boundary with a negative test.
B. Rely on a naming convention and assume any component with the same project label is trusted.
C. Delete the visible value immediately and skip revocation, dependency discovery, and audit review.
D. Accept the configuration because the happy path works; do not test forbidden access.
- **Expected answer / model solution:** **Correct: A.** It directly addresses authentication versus authorization and includes a verifiable boundary rather than relying on naming or a single successful request. **B is wrong** because labels/names do not enforce authorization. **C is incomplete** because deleting a copy does not necessarily invalidate a live credential or scope other copies. **D is wrong** because positive tests do not establish least privilege; negative tests are required.
- **Common wrong answers:** Choosing B confuses convention with enforcement. Choosing C mistakes cleanup for containment. Choosing D proves only one permitted path and leaves unauthorized access untested.
- **Scoring rubric:** 4 points: correct option 1; explain A 1; explain why B/C/D fail 2. Partial credit for identifying the key boundary even with a wrong choice.
- **Safety/version note:** Any product-specific commands or fields are [VERIFY] for the exact version; this is a concept question, not proof of product behavior.

### M09-U07-Q05 — MCQ

- **Level:** L2
- **Type:** MCQ
- **Objective tested:** reason about audience, expiration, mounting, automount controls, and workload exposure
- **Estimated time:** [ILLUSTRATIVE] 4 minutes
- **Question / context:** Which response best addresses **projected ServiceAccount tokens**? Choose one. [ILLUSTRATIVE] The environment is a disposable local lab and the credential is synthetic.

A. Use a narrowly scoped identity/policy and inspect the relevant audit/operational evidence before concluding.
B. Rely on a naming convention and assume any component with the same project label is trusted.
C. Delete the visible value immediately and skip revocation, dependency discovery, and audit review.
D. Accept the configuration because the happy path works; do not test forbidden access.
- **Expected answer / model solution:** **Correct: A.** It directly addresses projected ServiceAccount tokens and includes a verifiable boundary rather than relying on naming or a single successful request. **B is wrong** because labels/names do not enforce authorization. **C is incomplete** because deleting a copy does not necessarily invalidate a live credential or scope other copies. **D is wrong** because positive tests do not establish least privilege; negative tests are required.
- **Common wrong answers:** Choosing B confuses convention with enforcement. Choosing C mistakes cleanup for containment. Choosing D proves only one permitted path and leaves unauthorized access untested.
- **Scoring rubric:** 4 points: correct option 1; explain A 1; explain why B/C/D fail 2. Partial credit for identifying the key boundary even with a wrong choice.
- **Safety/version note:** Any product-specific commands or fields are [VERIFY] for the exact version; this is a concept question, not proof of product behavior.

### M09-U07-Q06 — MCQ

- **Level:** L2
- **Type:** MCQ
- **Objective tested:** evaluate trust conditions and role permissions while marking host/version specifics [VERIFY]
- **Estimated time:** [ILLUSTRATIVE] 4 minutes
- **Question / context:** Which response best addresses **AWS IRSA awareness**? Choose one. [ILLUSTRATIVE] The environment is a disposable local lab and the credential is synthetic.

A. Treat the observed representation as insufficient proof of confidentiality; validate the actual protection boundary and test access.
B. Rely on a naming convention and assume any component with the same project label is trusted.
C. Delete the visible value immediately and skip revocation, dependency discovery, and audit review.
D. Accept the configuration because the happy path works; do not test forbidden access.
- **Expected answer / model solution:** **Correct: A.** It directly addresses AWS IRSA awareness and includes a verifiable boundary rather than relying on naming or a single successful request. **B is wrong** because labels/names do not enforce authorization. **C is incomplete** because deleting a copy does not necessarily invalidate a live credential or scope other copies. **D is wrong** because positive tests do not establish least privilege; negative tests are required.
- **Common wrong answers:** Choosing B confuses convention with enforcement. Choosing C mistakes cleanup for containment. Choosing D proves only one permitted path and leaves unauthorized access untested.
- **Scoring rubric:** 4 points: correct option 1; explain A 1; explain why B/C/D fail 2. Partial credit for identifying the key boundary even with a wrong choice.
- **Safety/version note:** Any product-specific commands or fields are [VERIFY] for the exact version; this is a concept question, not proof of product behavior.

### M09-U07-Q07 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** distinguish the pattern at awareness level and verify current host setup
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Interpret this representative output and propose the next two verification steps:

```text
[ILLUSTRATIVE] inventory row: owner=unknown; source=CI variable; consumers=etl-worker, notebook-job; expiry=none; last_seen=build-log; audit_source=missing
```
Do not assume omitted fields are healthy.
- **Expected answer / model solution:** The inventory is incomplete and signals high uncertainty: owner, expiry, audit source, and lifecycle runbook are missing. Treat the build-log appearance as an exposure, identify the exact synthetic credential and privileges, notify the accountable incident owner, rotate/revoke if it could be live, then trace consumers and artifacts.
- **Common wrong answers:** Declaring success from one green field is insufficient. For identity, do not stop at signature validity; for freshness, do not equate source update with process adoption; for inventory, do not treat unknown ownership as a reason to delay escalation.
- **Scoring rubric:** 5 points: interpret evidence 2; identify missing evidence 1; safe next steps 1; verification criteria 1.
- **Safety/version note:** Output is synthetic and [ILLUSTRATIVE], not captured from a live product.

### M09-U07-Q08 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** compare issuer/subject/audience trust and least-privilege permissions; host details [VERIFY]
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Interpret this representative output and propose the next two verification steps:

```text
[ILLUSTRATIVE] verifier result: signature=valid; issuer=expected; audience=unexpected-api; subject=repo:demo/project:ref:refs/heads/feature; exp=in-future; policy=role expects refs/heads/main
```
Do not assume omitted fields are healthy.
- **Expected answer / model solution:** The token should be rejected by the stated verifier/role constraints despite a valid signature: audience and subject/ref do not match. Signature validity alone does not prove intended audience or authorization. Check issuer, key/JWKS, time claims, audience, subject, then resulting policy separately.
- **Common wrong answers:** Declaring success from one green field is insufficient. For identity, do not stop at signature validity; for freshness, do not equate source update with process adoption; for inventory, do not treat unknown ownership as a reason to delay escalation.
- **Scoring rubric:** 5 points: interpret evidence 2; identify missing evidence 1; safe next steps 1; verification criteria 1.
- **Safety/version note:** Output is synthetic and [ILLUSTRATIVE], not captured from a live product.

### M09-U07-Q09 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** constrain repository, branch/ref, environment, workflow, and fork trust
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Interpret this representative output and propose the next two verification steps:

```text
[ILLUSTRATIVE] rollout evidence: provider_version=v8; mounted_file_version=v8; process_started_at=09:00; process_loaded_version=v7; env_source=process-start
```
Do not assume omitted fields are healthy.
- **Expected answer / model solution:** The source and mounted file are current but the process still uses a previously loaded value. Determine whether the app reads a file dynamically or loads a value at startup; trigger a controlled reload/restart only after a safe rollout plan, then verify the app actually adopted v8.
- **Common wrong answers:** Declaring success from one green field is insufficient. For identity, do not stop at signature validity; for freshness, do not equate source update with process adoption; for inventory, do not treat unknown ownership as a reason to delay escalation.
- **Scoring rubric:** 5 points: interpret evidence 2; identify missing evidence 1; safe next steps 1; verification criteria 1.
- **Safety/version note:** Output is synthetic and [ILLUSTRATIVE], not captured from a live product.

### M09-U07-Q10 — config review

- **Level:** L2
- **Type:** config review
- **Objective tested:** prove wrong subject/audience tokens are rejected
- **Estimated time:** [ILLUSTRATIVE] 12 minutes
- **Question / context:** Review the synthetic configuration for **subject and audience negative tests**. Find at least three defects, explain impact, provide exact conceptual fixes, and state a verification test.

```yaml
# [ILLUSTRATIVE] unsafe example
secret_value: "FAKE_DO_NOT_USE_7f31"
read_all_paths: true
audit_enabled: false
owner: ""
ttl: "never"
```
- **Expected answer / model solution:** Defects to identify: (1) the fake credential is embedded directly in configuration; replace it with a reference/injection from the approved secret source and ensure it never enters committed files or logs; (2) broad access (`read_all_paths` / wildcard allow) violates least privilege; narrow to the exact required path/actions; (3) audit disabled or failure ignored removes important evidence and can conceal outages; enable and monitor appropriate audit/reconciliation evidence; (4) missing owner or shared namespace boundary prevents accountability and can permit cross-tenant access; define owner and enforce scope; (5) unbounded/disabled TTL or refresh policy can leave stale credentials; set lifecycle behavior appropriate to workload and monitor expiry; (6) no forbidden-access test means the policy is unproven. Verification: positive test for the intended consumer, negative test for a neighboring identity/path, review emitted audit/conditions, and ensure the synthetic value is absent from repository history/artifacts.
- **Common wrong answers:** Only changing the fake value is not enough. Broad permissions cannot be justified by a successful happy path. Enabling a feature without testing its effective behavior is not verification. A TTL must be compatible with consumer refresh and job duration.
- **Scoring rubric:** 8 points: identify defects 3; impact/fix 3; positive and negative verification 2. Partial credit for equivalent safe corrections.
- **Safety/version note:** Illustrative pseudo-configuration, not a valid product schema. Any exact fields/commands are [VERIFY] for the named version.

### M09-U07-Q11 — config review

- **Level:** L2
- **Type:** config review
- **Objective tested:** diagnose unknown key IDs, cache staleness, issuer changes, and fail-closed behavior
- **Estimated time:** [ILLUSTRATIVE] 12 minutes
- **Question / context:** Review the synthetic configuration for **JWKS rotation failure**. Find at least three defects, explain impact, provide exact conceptual fixes, and state a verification test.

```yaml
# [ILLUSTRATIVE] unsafe example
allow:
  - "*"
refresh: "disabled"
on_failure: "ignore"
namespace_boundary: "shared"
test_forbidden_access: false
```
- **Expected answer / model solution:** Defects to identify: (1) the fake credential is embedded directly in configuration; replace it with a reference/injection from the approved secret source and ensure it never enters committed files or logs; (2) broad access (`read_all_paths` / wildcard allow) violates least privilege; narrow to the exact required path/actions; (3) audit disabled or failure ignored removes important evidence and can conceal outages; enable and monitor appropriate audit/reconciliation evidence; (4) missing owner or shared namespace boundary prevents accountability and can permit cross-tenant access; define owner and enforce scope; (5) unbounded/disabled TTL or refresh policy can leave stale credentials; set lifecycle behavior appropriate to workload and monitor expiry; (6) no forbidden-access test means the policy is unproven. Verification: positive test for the intended consumer, negative test for a neighboring identity/path, review emitted audit/conditions, and ensure the synthetic value is absent from repository history/artifacts.
- **Common wrong answers:** Only changing the fake value is not enough. Broad permissions cannot be justified by a successful happy path. Enabling a feature without testing its effective behavior is not verification. A TTL must be compatible with consumer refresh and job duration.
- **Scoring rubric:** 8 points: identify defects 3; impact/fix 3; positive and negative verification 2. Partial credit for equivalent safe corrections.
- **Safety/version note:** Illustrative pseudo-configuration, not a valid product schema. Any exact fields/commands are [VERIFY] for the named version.

### M09-U07-Q12 — incident/troubleshooting

- **Level:** L3
- **Type:** incident/troubleshooting
- **Objective tested:** map issuer/audience/subject claims to role constraints and resulting Vault policies
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** Incident: an alert indicates a possible failure or exposure involving **Vault JWT auth**. The service is important but the evidence is incomplete; only synthetic logs are available in the exercise. Give an ordered response using diagnose → blast-radius/revocation check → contain → scope → eradicate → recover → prevent. Identify the first action and why.
- **Expected answer / model solution:** First preserve the alert/event identifiers and time window without copying the credential into chat or a ticket. Quickly determine credential type, privilege, validity, consumers, and whether safe immediate revocation/rotation is warranted; when compromise is credible and the credential may still be valid, invalidate/rotate before Git or artifact cleanup. Contain affected identities/paths, scope access using audit logs and deployment/artifact metadata, clean exposed copies as hygiene, restore with a known-good credential and controlled rollout, verify the old credential fails through an authorized test, then add missing inventory, detector, owner, and runbook controls. If evidence is insufficient, state uncertainty and escalate rather than inventing facts.
- **Common wrong answers:** Purging files first delays containment. Restarting everything without mapping dependencies may cause avoidable outage. Deleting evidence or pasting the secret into a ticket destroys safety and investigation quality.
- **Scoring rubric:** 8 points: first action/rationale 1; blast radius and revocation 2; scope/evidence 1; recovery/verification 2; prevention/ownership 1; safe uncertainty 1.
- **Safety/version note:** Synthetic incident only; do not validate a credential against a live third-party service.

### M09-U07-Q13 — incident/troubleshooting

- **Level:** L3
- **Type:** incident/troubleshooting
- **Objective tested:** explain what synthetic JWT tests prove and what they cannot prove about cloud trust
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** Incident: an alert indicates a possible failure or exposure involving **local simulation fidelity**. The service is important but the evidence is incomplete; only synthetic logs are available in the exercise. Give an ordered response using diagnose → blast-radius/revocation check → contain → scope → eradicate → recover → prevent. Identify the first action and why.
- **Expected answer / model solution:** First preserve the alert/event identifiers and time window without copying the credential into chat or a ticket. Quickly determine credential type, privilege, validity, consumers, and whether safe immediate revocation/rotation is warranted; when compromise is credible and the credential may still be valid, invalidate/rotate before Git or artifact cleanup. Contain affected identities/paths, scope access using audit logs and deployment/artifact metadata, clean exposed copies as hygiene, restore with a known-good credential and controlled rollout, verify the old credential fails through an authorized test, then add missing inventory, detector, owner, and runbook controls. If evidence is insufficient, state uncertainty and escalate rather than inventing facts.
- **Common wrong answers:** Purging files first delays containment. Restarting everything without mapping dependencies may cause avoidable outage. Deleting evidence or pasting the secret into a ticket destroys safety and investigation quality.
- **Scoring rubric:** 8 points: first action/rationale 1; blast radius and revocation 2; scope/evidence 1; recovery/verification 2; prevention/ownership 1; safe uncertainty 1.
- **Safety/version note:** Synthetic incident only; do not validate a credential against a live third-party service.

### M09-U07-Q14 — design

- **Level:** L4
- **Type:** design
- **Objective tested:** trace workload identity → secret manager/Vault → short-lived credential
- **Estimated time:** [ILLUSTRATIVE] 20 minutes
- **Question / context:** Design a small-platform control for **identity-to-secret exchange**. Constraints: zero-budget laptop lab, no live cloud account, two workloads with different privilege levels, and a requirement to demonstrate both permitted and forbidden behavior. State assumptions and failure modes.
- **Expected answer / model solution:** Model answer: start from the data flow and classify the credential; assign an accountable owner and inventory fields; select a delivery/control pattern appropriate to the consumer and freshness requirements; restrict each workload to its minimum path/permission; define rotation/revocation and outage behavior; ensure logs and audit evidence do not reveal the secret; and implement a disposable synthetic positive test plus a negative cross-workload test. Document recovery, cleanup, and what the local simulation cannot prove about a managed provider. A different design earns full credit if it explicitly handles these constraints.
- **Common wrong answers:** A single global credential for both workloads ignores privilege separation. “Use a vault” without auth, policy, lifecycle, audit, and recovery detail is not a design. A local mock is not evidence of cloud-provider parity.
- **Scoring rubric:** 10 points: correctness 2; least privilege 2; lifecycle/recovery 2; failure handling 1; verification/evidence 2; ownership/assumptions 1.
- **Safety/version note:** Provider-specific details remain [VERIFY]; no cloud account is required.

### M09-U07-Q15 — hands-on

- **Level:** L2
- **Type:** hands-on
- **Objective tested:** remove static fallback after proving federated path works and usage has ceased
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** In a disposable repository/local lab, design a safe test for **static-key migration** using only values such as `FAKE_LAB_SECRET_DO_NOT_USE_7f31`. State the setup, observation, cleanup, and success criteria. Do not run a scan against external systems.
- **Expected answer / model solution:** Create a disposable fixture with one synthetic secret-like value and one harmless negative control. Run the relevant local control using documentation for the installed version, capture only redacted findings/exit status, and test both detection and non-detection cases. Record tool/version, fixture hash, expected result, and cleanup. The success criterion is not just a green run: the positive fixture must be detected (where detection is intended), the negative fixture should not create an unjustified finding, and no real credential is contacted or exposed.
- **Common wrong answers:** Testing only a clean repository does not establish detection coverage. Printing full matched values can create another leak. Skipping the negative fixture hides false-positive risk.
- **Scoring rubric:** 6 points: safe setup 1; positive test 1; negative test 1; evidence 1; cleanup 1; version caveat 1.
- **Safety/version note:** Exact command syntax is [VERIFY] for the installed tool/version; lab is [SIMULATION].

### M09-U07-Q16 — boundary test

- **Level:** L3
- **Type:** boundary test
- **Objective tested:** inspect synthetic claims without exposing bearer tokens or treating decode as verification
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** Define a negative test for **claim inspection safety**. The test must demonstrate that a deliberately unauthorized synthetic identity cannot access a resource outside its assigned scope. What must be held constant, and what result counts as failure?
- **Expected answer / model solution:** Use two synthetic identities and two isolated resources. Establish a positive control for the authorized identity, then attempt the forbidden operation with the unauthorized identity while keeping the target, action, and policy state explicit. Denial must be enforced by the system, not merely by hiding a UI or omitting a credential. Capture status/audit evidence without logging secret material. Any success by the unauthorized identity is a failure and requires investigation of inherited policy, wildcard paths, namespace scope, cached credentials, and alternate access paths.
- **Common wrong answers:** A missing credential is not always a valid authorization test because it may test authentication only. Testing only the authorized identity proves no isolation. A client-side block is not an enforcement boundary.
- **Scoring rubric:** 6 points: clear boundary 2; valid positive/negative controls 2; evidence and failure criterion 1; safe handling 1.
- **Safety/version note:** Use local/synthetic identities only; exact denial codes and event names are version-specific [VERIFY].

### M09-U07-Q17 — evidence reasoning

- **Level:** L3
- **Type:** evidence reasoning
- **Objective tested:** restrict who can assume which role and what the role can access
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** You believe **least-privilege trust policy** is correctly controlled, but your only evidence is a successful happy-path test and a green dashboard. Name three additional pieces of evidence that would strengthen or overturn the conclusion.
- **Expected answer / model solution:** Useful evidence includes a negative test against an unauthorized identity; an audit trail for the exact principal, path, action, and time; versioned configuration/policy review; evidence that the runtime consumer adopted the intended value; and a documented recovery/rotation test. Evidence that would overturn the conclusion includes an inherited wildcard permission, a stale process value, missing audit coverage, an artifact copy, or a test fixture that never exercised the intended path. State the time window and blind spots.
- **Common wrong answers:** A green dashboard may cover only the scanner/controller's configured scope. A single success says nothing about forbidden access. Absence of logs is not proof that no access occurred.
- **Scoring rubric:** 6 points: three relevant evidence items 3; counterevidence 1; scope/limitations 1; clear verification plan 1.
- **Safety/version note:** All examples are synthetic; evidence completeness depends on configured product/version and retention [VERIFY].

### M09-U07-Q18 — operational trade-off

- **Level:** L4
- **Type:** operational trade-off
- **Objective tested:** balance identity plumbing, provider coupling, rotation, audit, and outage behavior
- **Estimated time:** [ILLUSTRATIVE] 12 minutes
- **Question / context:** Evaluate the trade-off in **operational trade-offs** for (A) a short-running stateless API and (B) a 90-minute ETL job. State which design decisions may differ and which security invariants must remain unchanged.
- **Expected answer / model solution:** The API may tolerate shorter-lived credentials and rapid replacement if it can reacquire and retry safely. The ETL job needs lease/TTL planning, renewal capability, checkpointing, idempotency, connection-pool refresh, and a controlled recovery path. In both cases, least privilege, owner/inventory, auditability, safe handling, and an explicit revocation plan remain invariants. Choose TTLs from measured job duration and renewal behavior, not a universal number; define failure thresholds and alert before expiry.
- **Common wrong answers:** One TTL for every workload ignores duration and recovery. Making the ETL credential effectively permanent to avoid outages trades away bounded exposure. Aggressive expiry without client refresh can create predictable outages.
- **Scoring rubric:** 8 points: compare workload needs 2; preserve security invariants 2; failure handling 2; evidence/monitoring 1; explicit assumptions 1.
- **Safety/version note:** TTL numbers are [ASSUMPTION] unless derived from measured workload and provider constraints.

## Unit 8 — Secret leak detection and incident response

### M09-U08-Q01 — short answer

- **Level:** L1
- **Type:** short answer
- **Objective tested:** compare exact patterns, entropy heuristics, verified detectors, and coverage limits
- **Estimated time:** [ILLUSTRATIVE] 6 minutes
- **Question / context:** Explain **pattern and entropy detectors** for a small data/AI platform. State the key boundary, the principal failure mode, and one control that reduces risk. Use a synthetic service credential; assume no cloud account is available.
- **Expected answer / model solution:** A strong answer should compare exact patterns, entropy heuristics, verified detectors, and coverage limits; identify the boundary where exposure or misuse can occur; state who can use the credential and for what; and pair prevention with detection/recovery. The practical check is to trace the relevant evidence and test the control in a disposable local environment. Do not infer that a secret is safe merely because it is not visible in the current source file.
- **Common wrong answers:** Saying only “put it in a secret manager” misses consumers, permissions, logs, copies, expiry, and recovery. Treating an absence of findings as proof of no exposure is also unsupported.
- **Scoring rubric:** 4 points: concept 1; boundary/threat 1; actionable control 1; verification/evidence 1. Partial credit for a defensible alternative with explicit assumptions.
- **Safety/version note:** None beyond the synthetic/offline assumptions stated in this question.

### M09-U08-Q02 — short answer

- **Level:** L1
- **Type:** short answer
- **Objective tested:** scan working tree, Git history, deleted files, logs/artifacts, images/layers, manifests/IaC, and collaboration surfaces
- **Estimated time:** [ILLUSTRATIVE] 7 minutes
- **Question / context:** Explain **surface coverage** for a small data/AI platform. State the key boundary, the principal failure mode, and one control that reduces risk. Use a synthetic service credential; assume no cloud account is available.
- **Expected answer / model solution:** A strong answer should scan working tree, Git history, deleted files, logs/artifacts, images/layers, manifests/IaC, and collaboration surfaces; identify the boundary where exposure or misuse can occur; state who can use the credential and for what; and pair prevention with detection/recovery. The practical check is to trace the relevant evidence and test the control in a disposable local environment. Do not infer that a secret is safe merely because it is not visible in the current source file.
- **Common wrong answers:** Saying only “put it in a secret manager” misses consumers, permissions, logs, copies, expiry, and recovery. Treating an absence of findings as proof of no exposure is also unsupported.
- **Scoring rubric:** 4 points: concept 1; boundary/threat 1; actionable control 1; verification/evidence 1. Partial credit for a defensible alternative with explicit assumptions.
- **Safety/version note:** None beyond the synthetic/offline assumptions stated in this question.

### M09-U08-Q03 — short answer

- **Level:** L1
- **Type:** short answer
- **Objective tested:** design layered local and CI checks; mark exact commands/config [VERIFY] by version
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Explain **Gitleaks/Trivy/pre-commit** for a small data/AI platform. State the key boundary, the principal failure mode, and one control that reduces risk. Use a synthetic service credential; assume no cloud account is available.
- **Expected answer / model solution:** A strong answer should design layered local and CI checks; mark exact commands/config [VERIFY] by version; identify the boundary where exposure or misuse can occur; state who can use the credential and for what; and pair prevention with detection/recovery. The practical check is to trace the relevant evidence and test the control in a disposable local environment. Do not infer that a secret is safe merely because it is not visible in the current source file.
- **Common wrong answers:** Saying only “put it in a secret manager” misses consumers, permissions, logs, copies, expiry, and recovery. Treating an absence of findings as proof of no exposure is also unsupported.
- **Scoring rubric:** 4 points: concept 1; boundary/threat 1; actionable control 1; verification/evidence 1. Partial credit for a defensible alternative with explicit assumptions.
- **Safety/version note:** None beyond the synthetic/offline assumptions stated in this question.

### M09-U08-Q04 — MCQ

- **Level:** L1
- **Type:** MCQ
- **Objective tested:** avoid broad exclusions; test both positive and negative fixtures
- **Estimated time:** [ILLUSTRATIVE] 4 minutes
- **Question / context:** Which response best addresses **custom detectors and allowlists**? Choose one. [ILLUSTRATIVE] The environment is a disposable local lab and the credential is synthetic.

A. Map the complete custom detectors and allowlists path, restrict access to the minimum consumer, and verify the boundary with a negative test.
B. Rely on a naming convention and assume any component with the same project label is trusted.
C. Delete the visible value immediately and skip revocation, dependency discovery, and audit review.
D. Accept the configuration because the happy path works; do not test forbidden access.
- **Expected answer / model solution:** **Correct: A.** It directly addresses custom detectors and allowlists and includes a verifiable boundary rather than relying on naming or a single successful request. **B is wrong** because labels/names do not enforce authorization. **C is incomplete** because deleting a copy does not necessarily invalidate a live credential or scope other copies. **D is wrong** because positive tests do not establish least privilege; negative tests are required.
- **Common wrong answers:** Choosing B confuses convention with enforcement. Choosing C mistakes cleanup for containment. Choosing D proves only one permitted path and leaves unauthorized access untested.
- **Scoring rubric:** 4 points: correct option 1; explain A 1; explain why B/C/D fail 2. Partial credit for identifying the key boundary even with a wrong choice.
- **Safety/version note:** Any product-specific commands or fields are [VERIFY] for the exact version; this is a concept question, not proof of product behavior.

### M09-U08-Q05 — MCQ

- **Level:** L2
- **Type:** MCQ
- **Objective tested:** recognize URL encoding, splitting, transformations, and structured fields that bypass simple masks
- **Estimated time:** [ILLUSTRATIVE] 4 minutes
- **Question / context:** Which response best addresses **log redaction limits**? Choose one. [ILLUSTRATIVE] The environment is a disposable local lab and the credential is synthetic.

A. Use a narrowly scoped identity/policy and inspect the relevant audit/operational evidence before concluding.
B. Rely on a naming convention and assume any component with the same project label is trusted.
C. Delete the visible value immediately and skip revocation, dependency discovery, and audit review.
D. Accept the configuration because the happy path works; do not test forbidden access.
- **Expected answer / model solution:** **Correct: A.** It directly addresses log redaction limits and includes a verifiable boundary rather than relying on naming or a single successful request. **B is wrong** because labels/names do not enforce authorization. **C is incomplete** because deleting a copy does not necessarily invalidate a live credential or scope other copies. **D is wrong** because positive tests do not establish least privilege; negative tests are required.
- **Common wrong answers:** Choosing B confuses convention with enforcement. Choosing C mistakes cleanup for containment. Choosing D proves only one permitted path and leaves unauthorized access untested.
- **Scoring rubric:** 4 points: correct option 1; explain A 1; explain why B/C/D fail 2. Partial credit for identifying the key boundary even with a wrong choice.
- **Safety/version note:** Any product-specific commands or fields are [VERIFY] for the exact version; this is a concept question, not proof of product behavior.

### M09-U08-Q06 — MCQ

- **Level:** L2
- **Type:** MCQ
- **Objective tested:** triage and revoke/rotate before history cleanup when a credential may remain valid
- **Estimated time:** [ILLUSTRATIVE] 4 minutes
- **Question / context:** Which response best addresses **incident ordering**? Choose one. [ILLUSTRATIVE] The environment is a disposable local lab and the credential is synthetic.

A. Treat the observed representation as insufficient proof of confidentiality; validate the actual protection boundary and test access.
B. Rely on a naming convention and assume any component with the same project label is trusted.
C. Delete the visible value immediately and skip revocation, dependency discovery, and audit review.
D. Accept the configuration because the happy path works; do not test forbidden access.
- **Expected answer / model solution:** **Correct: A.** It directly addresses incident ordering and includes a verifiable boundary rather than relying on naming or a single successful request. **B is wrong** because labels/names do not enforce authorization. **C is incomplete** because deleting a copy does not necessarily invalidate a live credential or scope other copies. **D is wrong** because positive tests do not establish least privilege; negative tests are required.
- **Common wrong answers:** Choosing B confuses convention with enforcement. Choosing C mistakes cleanup for containment. Choosing D proves only one permitted path and leaves unauthorized access untested.
- **Scoring rubric:** 4 points: correct option 1; explain A 1; explain why B/C/D fail 2. Partial credit for identifying the key boundary even with a wrong choice.
- **Safety/version note:** Any product-specific commands or fields are [VERIFY] for the exact version; this is a concept question, not proof of product behavior.

### M09-U08-Q07 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** distinguish password, cloud key, dynamic lease, TLS, signing, and encryption key response
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Interpret this representative output and propose the next two verification steps:

```text
[ILLUSTRATIVE] inventory row: owner=unknown; source=CI variable; consumers=etl-worker, notebook-job; expiry=none; last_seen=build-log; audit_source=missing
```
Do not assume omitted fields are healthy.
- **Expected answer / model solution:** The inventory is incomplete and signals high uncertainty: owner, expiry, audit source, and lifecycle runbook are missing. Treat the build-log appearance as an exposure, identify the exact synthetic credential and privileges, notify the accountable incident owner, rotate/revoke if it could be live, then trace consumers and artifacts.
- **Common wrong answers:** Declaring success from one green field is insufficient. For identity, do not stop at signature validity; for freshness, do not equate source update with process adoption; for inventory, do not treat unknown ownership as a reason to delay escalation.
- **Scoring rubric:** 5 points: interpret evidence 2; identify missing evidence 1; safe next steps 1; verification criteria 1.
- **Safety/version note:** Output is synthetic and [ILLUSTRATIVE], not captured from a live product.

### M09-U08-Q08 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** treat rewrite as hygiene and assess forks, mirrors, clones, caches, and artifacts
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Interpret this representative output and propose the next two verification steps:

```text
[ILLUSTRATIVE] verifier result: signature=valid; issuer=expected; audience=unexpected-api; subject=repo:demo/project:ref:refs/heads/feature; exp=in-future; policy=role expects refs/heads/main
```
Do not assume omitted fields are healthy.
- **Expected answer / model solution:** The token should be rejected by the stated verifier/role constraints despite a valid signature: audience and subject/ref do not match. Signature validity alone does not prove intended audience or authorization. Check issuer, key/JWKS, time claims, audience, subject, then resulting policy separately.
- **Common wrong answers:** Declaring success from one green field is insufficient. For identity, do not stop at signature validity; for freshness, do not equate source update with process adoption; for inventory, do not treat unknown ownership as a reason to delay escalation.
- **Scoring rubric:** 5 points: interpret evidence 2; identify missing evidence 1; safe next steps 1; verification criteria 1.
- **Safety/version note:** Output is synthetic and [ILLUSTRATIVE], not captured from a live product.

### M09-U08-Q09 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** handle alert metadata securely and investigate unexpected use without disclosing token
- **Estimated time:** [ILLUSTRATIVE] 8 minutes
- **Question / context:** Interpret this representative output and propose the next two verification steps:

```text
[ILLUSTRATIVE] rollout evidence: provider_version=v8; mounted_file_version=v8; process_started_at=09:00; process_loaded_version=v7; env_source=process-start
```
Do not assume omitted fields are healthy.
- **Expected answer / model solution:** The source and mounted file are current but the process still uses a previously loaded value. Determine whether the app reads a file dynamically or loads a value at startup; trigger a controlled reload/restart only after a safe rollout plan, then verify the app actually adopted v8.
- **Common wrong answers:** Declaring success from one green field is insufficient. For identity, do not stop at signature validity; for freshness, do not equate source update with process adoption; for inventory, do not treat unknown ownership as a reason to delay escalation.
- **Scoring rubric:** 5 points: interpret evidence 2; identify missing evidence 1; safe next steps 1; verification criteria 1.
- **Safety/version note:** Output is synthetic and [ILLUSTRATIVE], not captured from a live product.

### M09-U08-Q10 — config review

- **Level:** L2
- **Type:** config review
- **Objective tested:** correlate secret-path reads, auth failures, identity, time, source, and downstream actions
- **Estimated time:** [ILLUSTRATIVE] 12 minutes
- **Question / context:** Review the synthetic configuration for **audit analytics**. Find at least three defects, explain impact, provide exact conceptual fixes, and state a verification test.

```yaml
# [ILLUSTRATIVE] unsafe example
secret_value: "FAKE_DO_NOT_USE_7f31"
read_all_paths: true
audit_enabled: false
owner: ""
ttl: "never"
```
- **Expected answer / model solution:** Defects to identify: (1) the fake credential is embedded directly in configuration; replace it with a reference/injection from the approved secret source and ensure it never enters committed files or logs; (2) broad access (`read_all_paths` / wildcard allow) violates least privilege; narrow to the exact required path/actions; (3) audit disabled or failure ignored removes important evidence and can conceal outages; enable and monitor appropriate audit/reconciliation evidence; (4) missing owner or shared namespace boundary prevents accountability and can permit cross-tenant access; define owner and enforce scope; (5) unbounded/disabled TTL or refresh policy can leave stale credentials; set lifecycle behavior appropriate to workload and monitor expiry; (6) no forbidden-access test means the policy is unproven. Verification: positive test for the intended consumer, negative test for a neighboring identity/path, review emitted audit/conditions, and ensure the synthetic value is absent from repository history/artifacts.
- **Common wrong answers:** Only changing the fake value is not enough. Broad permissions cannot be justified by a successful happy path. Enabling a feature without testing its effective behavior is not verification. A TTL must be compatible with consumer refresh and job duration.
- **Scoring rubric:** 8 points: identify defects 3; impact/fix 3; positive and negative verification 2. Partial credit for equivalent safe corrections.
- **Safety/version note:** Illustrative pseudo-configuration, not a valid product schema. Any exact fields/commands are [VERIFY] for the named version.

### M09-U08-Q11 — config review

- **Level:** L2
- **Type:** config review
- **Objective tested:** define measurable indicators and SLOs without hiding severity in averages
- **Estimated time:** [ILLUSTRATIVE] 12 minutes
- **Question / context:** Review the synthetic configuration for **time-to-detect and revoke**. Find at least three defects, explain impact, provide exact conceptual fixes, and state a verification test.

```yaml
# [ILLUSTRATIVE] unsafe example
allow:
  - "*"
refresh: "disabled"
on_failure: "ignore"
namespace_boundary: "shared"
test_forbidden_access: false
```
- **Expected answer / model solution:** Defects to identify: (1) the fake credential is embedded directly in configuration; replace it with a reference/injection from the approved secret source and ensure it never enters committed files or logs; (2) broad access (`read_all_paths` / wildcard allow) violates least privilege; narrow to the exact required path/actions; (3) audit disabled or failure ignored removes important evidence and can conceal outages; enable and monitor appropriate audit/reconciliation evidence; (4) missing owner or shared namespace boundary prevents accountability and can permit cross-tenant access; define owner and enforce scope; (5) unbounded/disabled TTL or refresh policy can leave stale credentials; set lifecycle behavior appropriate to workload and monitor expiry; (6) no forbidden-access test means the policy is unproven. Verification: positive test for the intended consumer, negative test for a neighboring identity/path, review emitted audit/conditions, and ensure the synthetic value is absent from repository history/artifacts.
- **Common wrong answers:** Only changing the fake value is not enough. Broad permissions cannot be justified by a successful happy path. Enabling a feature without testing its effective behavior is not verification. A TTL must be compatible with consumer refresh and job duration.
- **Scoring rubric:** 8 points: identify defects 3; impact/fix 3; positive and negative verification 2. Partial credit for equivalent safe corrections.
- **Safety/version note:** Illustrative pseudo-configuration, not a valid product schema. Any exact fields/commands are [VERIFY] for the named version.

### M09-U08-Q12 — incident/troubleshooting

- **Level:** L3
- **Type:** incident/troubleshooting
- **Objective tested:** use idempotency, rate limits, approval gates, and circuit breakers
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** Incident: an alert indicates a possible failure or exposure involving **automated response safeguards**. The service is important but the evidence is incomplete; only synthetic logs are available in the exercise. Give an ordered response using diagnose → blast-radius/revocation check → contain → scope → eradicate → recover → prevent. Identify the first action and why.
- **Expected answer / model solution:** First preserve the alert/event identifiers and time window without copying the credential into chat or a ticket. Quickly determine credential type, privilege, validity, consumers, and whether safe immediate revocation/rotation is warranted; when compromise is credible and the credential may still be valid, invalidate/rotate before Git or artifact cleanup. Contain affected identities/paths, scope access using audit logs and deployment/artifact metadata, clean exposed copies as hygiene, restore with a known-good credential and controlled rollout, verify the old credential fails through an authorized test, then add missing inventory, detector, owner, and runbook controls. If evidence is insufficient, state uncertainty and escalate rather than inventing facts.
- **Common wrong answers:** Purging files first delays containment. Restarting everything without mapping dependencies may cause avoidable outage. Deleting evidence or pasting the secret into a ticket destroys safety and investigation quality.
- **Scoring rubric:** 8 points: first action/rationale 1; blast radius and revocation 2; scope/evidence 1; recovery/verification 2; prevention/ownership 1; safe uncertainty 1.
- **Safety/version note:** Synthetic incident only; do not validate a credential against a live third-party service.

### M09-U08-Q13 — incident/troubleshooting

- **Level:** L3
- **Type:** incident/troubleshooting
- **Objective tested:** preserve timestamps, event IDs, hashes, access records, and chain-of-custody according to policy
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** Incident: an alert indicates a possible failure or exposure involving **evidence preservation**. The service is important but the evidence is incomplete; only synthetic logs are available in the exercise. Give an ordered response using diagnose → blast-radius/revocation check → contain → scope → eradicate → recover → prevent. Identify the first action and why.
- **Expected answer / model solution:** First preserve the alert/event identifiers and time window without copying the credential into chat or a ticket. Quickly determine credential type, privilege, validity, consumers, and whether safe immediate revocation/rotation is warranted; when compromise is credible and the credential may still be valid, invalidate/rotate before Git or artifact cleanup. Contain affected identities/paths, scope access using audit logs and deployment/artifact metadata, clean exposed copies as hygiene, restore with a known-good credential and controlled rollout, verify the old credential fails through an authorized test, then add missing inventory, detector, owner, and runbook controls. If evidence is insufficient, state uncertainty and escalate rather than inventing facts.
- **Common wrong answers:** Purging files first delays containment. Restarting everything without mapping dependencies may cause avoidable outage. Deleting evidence or pasting the secret into a ticket destroys safety and investigation quality.
- **Scoring rubric:** 8 points: first action/rationale 1; blast radius and revocation 2; scope/evidence 1; recovery/verification 2; prevention/ownership 1; safe uncertainty 1.
- **Safety/version note:** Synthetic incident only; do not validate a credential against a live third-party service.

### M09-U08-Q14 — design

- **Level:** L4
- **Type:** design
- **Objective tested:** validate detector coverage using synthetic fixtures and review exclusions
- **Estimated time:** [ILLUSTRATIVE] 20 minutes
- **Question / context:** Design a small-platform control for **false positives/negatives**. Constraints: zero-budget laptop lab, no live cloud account, two workloads with different privilege levels, and a requirement to demonstrate both permitted and forbidden behavior. State assumptions and failure modes.
- **Expected answer / model solution:** Model answer: start from the data flow and classify the credential; assign an accountable owner and inventory fields; select a delivery/control pattern appropriate to the consumer and freshness requirements; restrict each workload to its minimum path/permission; define rotation/revocation and outage behavior; ensure logs and audit evidence do not reveal the secret; and implement a disposable synthetic positive test plus a negative cross-workload test. Document recovery, cleanup, and what the local simulation cannot prove about a managed provider. A different design earns full credit if it explicitly handles these constraints.
- **Common wrong answers:** A single global credential for both workloads ignores privilege separation. “Use a vault” without auth, policy, lifecycle, audit, and recovery detail is not a design. A local mock is not evidence of cloud-provider parity.
- **Scoring rubric:** 10 points: correctness 2; least privilege 2; lifecycle/recovery 2; failure handling 1; verification/evidence 2; ownership/assumptions 1.
- **Safety/version note:** Provider-specific details remain [VERIFY]; no cloud account is required.

### M09-U08-Q15 — hands-on

- **Level:** L2
- **Type:** hands-on
- **Objective tested:** assess recoverable old layers, logs, caches, and registry retention
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** In a disposable repository/local lab, design a safe test for **CI artifact and image cleanup** using only values such as `FAKE_LAB_SECRET_DO_NOT_USE_7f31`. State the setup, observation, cleanup, and success criteria. Do not run a scan against external systems.
- **Expected answer / model solution:** Create a disposable fixture with one synthetic secret-like value and one harmless negative control. Run the relevant local control using documentation for the installed version, capture only redacted findings/exit status, and test both detection and non-detection cases. Record tool/version, fixture hash, expected result, and cleanup. The success criterion is not just a green run: the positive fixture must be detected (where detection is intended), the negative fixture should not create an unjustified finding, and no real credential is contacted or exposed.
- **Common wrong answers:** Testing only a clean repository does not establish detection coverage. Printing full matched values can create another leak. Skipping the negative fixture hides false-positive risk.
- **Scoring rubric:** 6 points: safe setup 1; positive test 1; negative test 1; evidence 1; cleanup 1; version caveat 1.
- **Safety/version note:** Exact command syntax is [VERIFY] for the installed tool/version; lab is [SIMULATION].

### M09-U08-Q16 — boundary test

- **Level:** L3
- **Type:** boundary test
- **Objective tested:** assign incident command and ownership when inventory is incomplete
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** Define a negative test for **credential owner escalation**. The test must demonstrate that a deliberately unauthorized synthetic identity cannot access a resource outside its assigned scope. What must be held constant, and what result counts as failure?
- **Expected answer / model solution:** Use two synthetic identities and two isolated resources. Establish a positive control for the authorized identity, then attempt the forbidden operation with the unauthorized identity while keeping the target, action, and policy state explicit. Denial must be enforced by the system, not merely by hiding a UI or omitting a credential. Capture status/audit evidence without logging secret material. Any success by the unauthorized identity is a failure and requires investigation of inherited policy, wildcard paths, namespace scope, cached credentials, and alternate access paths.
- **Common wrong answers:** A missing credential is not always a valid authorization test because it may test authentication only. Testing only the authorized identity proves no isolation. A client-side block is not an enforcement boundary.
- **Scoring rubric:** 6 points: clear boundary 2; valid positive/negative controls 2; evidence and failure criterion 1; safe handling 1.
- **Safety/version note:** Use local/synthetic identities only; exact denial codes and event names are version-specific [VERIFY].

### M09-U08-Q17 — evidence reasoning

- **Level:** L3
- **Type:** evidence reasoning
- **Objective tested:** prove old credential invalid through authorized local/provider evidence, not live third-party probing
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** You believe **safe verification** is correctly controlled, but your only evidence is a successful happy-path test and a green dashboard. Name three additional pieces of evidence that would strengthen or overturn the conclusion.
- **Expected answer / model solution:** Useful evidence includes a negative test against an unauthorized identity; an audit trail for the exact principal, path, action, and time; versioned configuration/policy review; evidence that the runtime consumer adopted the intended value; and a documented recovery/rotation test. Evidence that would overturn the conclusion includes an inherited wildcard permission, a stale process value, missing audit coverage, an artifact copy, or a test fixture that never exercised the intended path. State the time window and blind spots.
- **Common wrong answers:** A green dashboard may cover only the scanner/controller's configured scope. A single success says nothing about forbidden access. Absence of logs is not proof that no access occurred.
- **Scoring rubric:** 6 points: three relevant evidence items 3; counterevidence 1; scope/limitations 1; clear verification plan 1.
- **Safety/version note:** All examples are synthetic; evidence completeness depends on configured product/version and retention [VERIFY].

### M09-U08-Q18 — operational trade-off

- **Level:** L4
- **Type:** operational trade-off
- **Objective tested:** balance detection sensitivity, false-positive cost, response automation, and service continuity
- **Estimated time:** [ILLUSTRATIVE] 12 minutes
- **Question / context:** Evaluate the trade-off in **operational trade-offs** for (A) a short-running stateless API and (B) a 90-minute ETL job. State which design decisions may differ and which security invariants must remain unchanged.
- **Expected answer / model solution:** The API may tolerate shorter-lived credentials and rapid replacement if it can reacquire and retry safely. The ETL job needs lease/TTL planning, renewal capability, checkpointing, idempotency, connection-pool refresh, and a controlled recovery path. In both cases, least privilege, owner/inventory, auditability, safe handling, and an explicit revocation plan remain invariants. Choose TTLs from measured job duration and renewal behavior, not a universal number; define failure thresholds and alert before expiry.
- **Common wrong answers:** One TTL for every workload ignores duration and recovery. Making the ETL credential effectively permanent to avoid outages trades away bounded exposure. Aggressive expiry without client refresh can create predictable outages.
- **Scoring rubric:** 8 points: compare workload needs 2; preserve security invariants 2; failure handling 2; evidence/monitoring 1; explicit assumptions 1.
- **Safety/version note:** TTL numbers are [ASSUMPTION] unless derived from measured workload and provider constraints.

## Cross-unit integration scenarios

### M09-XI-001 — design

- **Level:** L4
- **Type:** design
- **Objective tested:** Integrate U01/U04/U05/U06/U07: Secret-delivery pattern for a Kubernetes workload
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** **Units:** U01/U04/U05/U06/U07. **Scenario:** A small data platform has a stateless API and a long-running ETL job. One needs a static third-party API token; the other needs database credentials that can be short-lived. Local kind is available; cloud accounts are not. This is a multi-stage scenario: state the order of operations, decision points, trade-offs, and verification criteria.
- **Expected answer / model solution:** Choose per-consumer patterns rather than one universal mechanism. For the static external API token, ESO or CSI may fit depending on whether the app consumes a Kubernetes object or file; protect any resulting Secret with RBAC and at-rest encryption, and verify reload behavior. For the ETL database, prefer workload identity to obtain dynamic credentials if supported; design renewal, checkpointing, and pool refresh. SOPS/Sealed Secrets can protect Git-stored encrypted data but do not make the runtime value non-sensitive. Test positive and negative access locally; mark provider parity [VERIFY].
- **Common wrong answers:** Use one shared long-lived key for every workload; it broadens blast radius. Claim a local kind test proves managed-cloud IAM behavior; it does not.
- **Scoring rubric:** 10 points: workload-specific fit 3; least privilege 2; lifecycle/reload 2; negative tests 2; caveats 1.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-002 — incident/troubleshooting

- **Level:** L4
- **Type:** incident/troubleshooting
- **Objective tested:** Integrate U01/U05/U08: Password committed to Git and Helm values
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** **Units:** U01/U05/U08. **Scenario:** A synthetic database password appears in a public repository and a Helm values file. The service may still accept it. The repository is mirrored and CI artifacts are retained. This is a multi-stage scenario: state the order of operations, decision points, trade-offs, and verification criteria.
- **Expected answer / model solution:** First assess validity/privilege and rotate or revoke promptly if the credential may be live. Preserve incident timestamps and evidence, identify all consumers and Helm releases, issue a replacement through the approved source, roll out safely, and verify the old credential fails. Then remove plaintext from current files, inspect logs/artifacts/images and mirrors, rewrite history only as hygiene, notify owners of clones/forks, and add scanning plus safe templating tests.
- **Common wrong answers:** Purge Git history first and rotate later; delete only the current values file; paste the password into a ticket for coordination.
- **Scoring rubric:** 10 points: immediate action 2; dependency map 2; rotate/deploy/verify 2; hygiene/residual copies 2; prevention 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-003 — incident/troubleshooting

- **Level:** L4
- **Type:** incident/troubleshooting
- **Objective tested:** Integrate U02/U03/U07: Dynamic database credential expires during ETL
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** **Units:** U02/U03/U07. **Scenario:** A 90-minute ETL job receives a synthetic dynamic DB credential with a 30-minute TTL. At minute 31, new database connections fail while existing connections behave differently. Logs are illustrative. This is a multi-stage scenario: state the order of operations, decision points, trade-offs, and verification criteria.
- **Expected answer / model solution:** Check lease metadata, renewal outcome, DB role/credential status, and pool behavior. Do not assume an existing connection proves new connections will work. Stop unsafe retries; checkpoint the job and use idempotent recovery. Reacquire/renew through the authorized identity path, refresh the pool, and resume from checkpoint. Reassess TTL/renewal against measured duration; verify old credential rejection in an isolated test.
- **Common wrong answers:** Increase TTL indefinitely; retry every second; restart the entire ETL without checking idempotency.
- **Scoring rubric:** 10 points: distinguish lease and pool 2; safe containment/checkpoint 2; reacquire/refresh 2; old-credential test 2; prevention/monitoring 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-004 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** Integrate U03/U04/U06: ESO rotates source but environment variable stays old
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** **Units:** U03/U04/U06. **Scenario:** Provider value changes from synthetic version v7 to v8. ESO reconciliation and the Kubernetes Secret show v8, but a running process reports it loaded v7 at startup. Give a safe, evidence-led response and name the verification criteria.
- **Expected answer / model solution:** Separate provider update, target-object update, and application adoption. Verify reconciliation status/version, target object metadata without printing the value, and process reload semantics. Environment variables are generally fixed for an already-running process; roll out a controlled restart or change to a supported file/reload pattern. Confirm new process behavior and old credential invalidation, while maintaining rollback constraints.
- **Common wrong answers:** Assume ESO is broken because the process is old; restart all workloads immediately without rollout safety; assume environment variables mutate live.
- **Scoring rubric:** 8 points: trace stages 2; explain process semantics 2; safe reload plan 2; verify adopted version 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-005 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** Integrate U04/U06: CSI-mounted secret updates but application does not reload
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** **Units:** U04/U06. **Scenario:** A synthetic file-mounted secret changes at the mount path, but the application continues using the old credential in memory. Cluster/version and driver behavior are not specified. Give a safe, evidence-led response and name the verification criteria.
- **Expected answer / model solution:** Verify source version and mount content using a safe metadata/hash check, then inspect application reload behavior and mount semantics for the actual driver/version [VERIFY]. Trigger the documented reload/restart path with readiness and rollback controls. Test whether a file watcher or re-open-on-use is supported; do not assume updates propagate to process memory. Verify new authentication and old credential failure in a local test.
- **Common wrong answers:** Declare rotation complete because the file changed; print the secret in logs; assume all CSI providers have identical refresh behavior.
- **Scoring rubric:** 8 points: separate mount from process 2; verify driver/version 2; controlled reload 2; end-to-end test 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-006 — output interpretation

- **Level:** L4
- **Type:** output interpretation
- **Objective tested:** Integrate U01/U06: Secret appears in etcd snapshot
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** **Units:** U01/U06. **Scenario:** A Kubernetes Secret value is Base64-encoded in an API object and can be recovered from an old etcd snapshot. The cluster type/version and encryption configuration are unknown. This is a multi-stage scenario: state the order of operations, decision points, trade-offs, and verification criteria.
- **Expected answer / model solution:** Base64 is encoding, not encryption. Determine whether API-server encryption-at-rest was configured, whether the object was rewritten after configuration, snapshot access controls, and backup retention. Treat recoverable snapshots as an exposure surface; rotate the live credential if compromise is credible, restrict snapshot access, preserve evidence, and follow a tested key/backup recovery plan. Confirm cluster-specific managed control-plane responsibilities [VERIFY].
- **Common wrong answers:** Claim Base64 is encryption; enable encryption now and assume historical snapshots changed; delete the snapshot without evidence or retention review.
- **Scoring rubric:** 8 points: encoding distinction 2; live containment 2; snapshot/key analysis 2; recovery and host caveat 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-007 — output interpretation

- **Level:** L3
- **Type:** output interpretation
- **Objective tested:** Integrate U02/U07: JWT has wrong audience or subject
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** **Units:** U02/U07. **Scenario:** Verifier rules are explicit: issuer must equal `https://issuer.example.invalid`; signature must validate under the configured trusted key; audience must equal `vault-lab`; subject must equal `system:serviceaccount:etl:runner`; `exp` must be future and `nbf` must be past. Synthetic token has correct issuer/signature/time but audience `other-api` and subject `system:serviceaccount:dev:runner`. Give a safe, evidence-led response and name the verification criteria.
- **Expected answer / model solution:** Reject the token because audience and subject mismatch. Signature validity and issuer match are necessary but not sufficient. After authentication/role constraints, separately evaluate authorization policies for the resulting identity. Record a redacted failure reason and test wrong-audience and wrong-subject tokens explicitly.
- **Common wrong answers:** Accept because the signature is valid; call it authorization-only without checking configured role validation; decode claims and treat decoding as verification.
- **Scoring rubric:** 8 points: identify both decisive mismatches 3; authn/authz distinction 2; negative tests 2; safe evidence 1.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-008 — output interpretation

- **Level:** L3
- **Type:** output interpretation
- **Objective tested:** Integrate U05/U07/U08: CI OIDC trust permits fork or branch
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** **Units:** U05/U07/U08. **Scenario:** A CI trust rule matches repository name only, with no branch/ref or fork boundary. A pull request from a fork can run a job that requests a token. No live cloud account is available. Give a safe, evidence-led response and name the verification criteria.
- **Expected answer / model solution:** Tighten the trust conditions to the intended issuer, audience, repository, protected ref/environment, and workflow context supported by the host. Explicitly deny fork and untrusted branch cases. Test synthetic claims for main, feature, fork, and environment mismatch. Restrict permissions and secrets for untrusted workflows. Host-specific claim names/semantics are [VERIFY].
- **Common wrong answers:** Trust repository name alone; assume a fork cannot run CI; test only the main-branch success case.
- **Scoring rubric:** 8 points: identify trust gap 2; narrow conditions 2; negative test matrix 2; host/version caveat 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-009 — incident/troubleshooting

- **Level:** L4
- **Type:** incident/troubleshooting
- **Objective tested:** Integrate U01/U07/U08: Leaked cloud-style key in public repository
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** **Units:** U01/U07/U08. **Scenario:** A synthetic cloud-style access key is detected in a public repository. The owner and privilege are not yet known; audit records are available for the last 48 hours. This is a multi-stage scenario: state the order of operations, decision points, trade-offs, and verification criteria.
- **Expected answer / model solution:** First use the authorized issuer/control plane to disable/rotate the key when credible exposure is indicated; do not test it against external services. Identify owner, permissions, consumers, and last-use events; scope the 48-hour window and any earlier retention. Review downstream activity, deploy replacement through workload identity or secret manager, verify old key rejection through authorized evidence, then remove copies/history and add controls.
- **Common wrong answers:** Ask a learner to try the key against the cloud API; clean Git before invalidation; assume no abuse because there are no logs.
- **Scoring rubric:** 8 points: immediate containment 2; privilege/owner scope 2; audit/recovery 2; hygiene/prevention 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-010 — output interpretation

- **Level:** L3
- **Type:** output interpretation
- **Objective tested:** Integrate U01/U05/U08: History rewrite but clone/fork remains
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** **Units:** U01/U05/U08. **Scenario:** Repository history was rewritten after a synthetic secret leak. A developer reports an old clone and a mirror still contain the commit. The credential's validity is unknown. Give a safe, evidence-led response and name the verification criteria.
- **Expected answer / model solution:** Treat history rewriting as hygiene, not remediation. Determine validity and rotate/revoke first if still usable; identify clones, forks, mirrors, caches, artifacts, and recipients; restrict access or coordinate re-cloning according to policy. Preserve evidence and verify old credential failure independently of repository cleanup.
- **Common wrong answers:** Declare incident closed because the branch no longer contains the commit; demand every clone be proven clean before rotating.
- **Scoring rubric:** 8 points: distinguish hygiene/remediation 2; invalidate 2; residual-copy scope 2; verification 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-011 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** Integrate U01/U08: Scanner misses Base64-encoded value
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** **Units:** U01/U08. **Scenario:** A synthetic secret detector catches the raw string but misses its Base64 representation. The pipeline reports green. No evidence says encoded variants are in scope. Give a safe, evidence-led response and name the verification criteria.
- **Expected answer / model solution:** Document detector coverage and test synthetic raw, encoded, URL-encoded, and split fixtures. Add supported decoding/normalization or additional controls where appropriate, while controlling false positives. Scan history, logs, artifacts, and images separately. Do not claim complete coverage from one scanner; use least privilege, short lifetimes, redaction, and response readiness as compensating controls.
- **Common wrong answers:** Assume entropy detection catches every encoding; disable the detector because one variant was missed; label all encoded text as a secret without validation.
- **Scoring rubric:** 8 points: coverage gap 2; fixture-based tests 2; layered controls 2; assurance wording 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-012 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** Integrate U01/U08: Broad allowlist suppresses test and production paths
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** **Units:** U01/U08. **Scenario:** A detector allowlist excludes `**/fixtures/**`, but a production manifest is accidentally placed under that path. A synthetic credential is not reported. Give a safe, evidence-led response and name the verification criteria.
- **Expected answer / model solution:** Narrow exclusions to exact known fixture files and document why each is safe. Add a regression fixture proving a production-like path is scanned and a known false-positive fixture is ignored. Review allowlist changes and monitor suppressed findings. A path name is not a trust boundary.
- **Common wrong answers:** Keep the broad exclusion because the directory name says fixtures; remove all allowlists and accept unreviewed noise; claim the scanner is effective without a test.
- **Scoring rubric:** 8 points: identify scope defect 2; narrow allowlist 2; positive/negative regression 2; review/monitoring 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-013 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** Integrate U01/U08: Pre-commit hook bypassed
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** **Units:** U01/U08. **Scenario:** A developer commits a synthetic secret using a bypass flag or an environment without the hook. Local controls are not mandatory and CI does not scan. Give a safe, evidence-led response and name the verification criteria.
- **Expected answer / model solution:** Treat pre-commit as an early feedback layer, not the sole enforcement point. Add repository CI scanning and, where available, server-side/push protection; scan current tree and history as appropriate; protect CI configuration and exceptions; use safe synthetic test fixtures. If the credential might be real, follow incident response and invalidate it before cleanup.
- **Common wrong answers:** Rely on developer discipline; block all commits without providing a safe workflow; assume local hook coverage equals server enforcement.
- **Scoring rubric:** 8 points: defense in depth 3; scope/CI backstop 2; safe incident path 2; usability 1.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-014 — output interpretation

- **Level:** L3
- **Type:** output interpretation
- **Objective tested:** Integrate U01/U08: Secret in old container layer
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** **Units:** U01/U08. **Scenario:** The current image filesystem has no secret, but an earlier build layer added and later deleted a synthetic credential. Registry retention includes the old digest. Give a safe, evidence-led response and name the verification criteria.
- **Expected answer / model solution:** Inspect image layers and build/cache artifacts using local tooling and fake values. Treat deleted-in-later-layer data as potentially recoverable. Rotate/revoke if the value may be live, identify tags/digests and deployment consumers, rebuild from a clean context, remove exposed images/caches according to retention policy, and verify the new image history and registry state.
- **Common wrong answers:** Trust the final filesystem only; delete the tag but ignore immutable digest; rebuild without invalidating the credential.
- **Scoring rubric:** 8 points: layer persistence 2; containment 2; rebuild/registry scope 2; verification 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-015 — output interpretation

- **Level:** L4
- **Type:** output interpretation
- **Objective tested:** Integrate U01/U08: CI artifact contains recoverable redacted data
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** **Units:** U01/U08. **Scenario:** A CI artifact masks the middle of a token but retains prefix/suffix and a reversible encoded field. It is downloadable by a wider group than the source repository. This is a multi-stage scenario: state the order of operations, decision points, trade-offs, and verification criteria.
- **Expected answer / model solution:** Restrict artifact access and preserve metadata/evidence; determine whether the residual data is usable or reconstructable without publishing it. Rotate/revoke if credible exposure, identify downloads/retention, remove or expire affected artifacts under policy, and test redaction with encoded/split fixtures. Redaction is not prevention; avoid placing secret values in artifacts at all.
- **Common wrong answers:** Assume masking means safe; paste the unmasked token into the incident channel; delete all evidence without recording artifact IDs/time.
- **Scoring rubric:** 8 points: contain/access scope 2; credential decision 2; artifact cleanup 2; prevention/test 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-016 — incident/troubleshooting

- **Level:** L3
- **Type:** incident/troubleshooting
- **Objective tested:** Integrate U01/U08: Canary token triggered from unexpected build
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** **Units:** U01/U08. **Scenario:** A synthetic canary/honeytoken alert names an artifact digest and timestamp. The token value itself is not shown. A recent build accessed the artifact from an unfamiliar job. Give a safe, evidence-led response and name the verification criteria.
- **Expected answer / model solution:** Do not disclose or re-use the canary. Preserve event ID, digest, time, principal, source, and artifact provenance. Compare expected build graph and access logs, isolate the suspicious job/identity if justified, check whether token was copied into a test fixture or public output, and escalate according to incident policy. Rotate any real credentials implicated by the investigation, not the canary as if it were a production credential.
- **Common wrong answers:** Print the canary value to search for it; dismiss the alert as a false positive before checking provenance; automatically disable all production identities without a blast-radius review.
- **Scoring rubric:** 8 points: safe evidence 2; provenance/scope 2; proportionate containment 2; prevention 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-017 — incident/troubleshooting

- **Level:** L4
- **Type:** incident/troubleshooting
- **Objective tested:** Integrate U01/U03/U08: TLS private key leaked across services
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** **Units:** U01/U03/U08. **Scenario:** A synthetic TLS private key used by several services is found in an image layer. Certificate issuer, SANs, and service inventory are available; exact production steps are out of scope. This is a multi-stage scenario: state the order of operations, decision points, trade-offs, and verification criteria.
- **Expected answer / model solution:** Assess affected certificates, SANs, services, trust chain, and exposure window. Revoke/replace certificates and keys through authorized PKI procedures, prioritize externally exposed/high-risk endpoints, roll out replacements with overlap only where safe, monitor handshake errors, and verify each service presents the new certificate. Clean images/artifacts/history after containment and document dependent rollout.
- **Common wrong answers:** Rotate only the first service; remove the key from Git and assume the certificate is invalid; reuse the same private key in a new certificate without threat review.
- **Scoring rubric:** 8 points: scope dependencies 2; key/certificate containment 2; rollout/verification 2; hygiene/monitoring 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-018 — incident/troubleshooting

- **Level:** L4
- **Type:** incident/troubleshooting
- **Objective tested:** Integrate U01/U05/U08: Signing key used for artifact signing leaked
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** **Units:** U01/U05/U08. **Scenario:** A synthetic signing key was used to sign internal artifacts. The team cannot yet determine whether unauthorized signatures were produced. This is a multi-stage scenario: state the order of operations, decision points, trade-offs, and verification criteria.
- **Expected answer / model solution:** Treat this as a trust incident, not merely a password rotation. Preserve signing logs and artifact provenance; disable/revoke the affected key/certificate or trust binding according to the signing system; identify artifacts signed during the exposure window; establish a trusted replacement, re-sign or rebuild affected artifacts as appropriate, and publish/communicate trust changes. Verify consumers reject signatures from the compromised identity where supported.
- **Common wrong answers:** Only encrypt the old key file; assume signatures remain trustworthy because the artifacts were built internally; rotate without assessing trust consumers.
- **Scoring rubric:** 10 points: preserve evidence 2; revoke trust 2; artifact scope 2; replacement/re-sign 2; verifier test 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-019 — incident/troubleshooting

- **Level:** L4
- **Type:** incident/troubleshooting
- **Objective tested:** Integrate U01/U05/U06: Encryption key suspected compromised
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** **Units:** U01/U05/U06. **Scenario:** A key-encryption key may have been exposed. The platform uses envelope encryption, but it is unknown which data keys were wrapped by it and whether plaintext data keys were exposed. This is a multi-stage scenario: state the order of operations, decision points, trade-offs, and verification criteria.
- **Expected answer / model solution:** Separate compromise of the key-encryption key from exposure of plaintext data keys or encrypted data. Preserve evidence, identify key versions and dependent ciphertext/data-key wrapping, restrict/disable key use according to the approved incident plan, and assess whether rewrapping, data re-encryption, or credential rotation is required. Test restore/decrypt with retained authorized keys. Exact provider behavior is [VERIFY].
- **Common wrong answers:** Assume rotating the KEK automatically rewrites all ciphertext; delete all old keys before recovery is tested; assume ciphertext alone proves there was no data exposure.
- **Scoring rubric:** 10 points: distinguish key layers 3; scope affected data 2; safe containment/recovery 2; verify decrypt/rewrap 2; caveat 1.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-020 — incident/troubleshooting

- **Level:** L3
- **Type:** incident/troubleshooting
- **Objective tested:** Integrate U02/U03/U08: Dynamic secret leak detected
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** **Units:** U02/U03/U08. **Scenario:** A synthetic dynamic DB username/password and lease identifier are found in a CI log. The lease may still be active and the job identity is known. Give a safe, evidence-led response and name the verification criteria.
- **Expected answer / model solution:** Use the authorized secret manager/database control path to revoke the lease or disable the credential promptly, then confirm the database rejects new use in a local/authorized verification path. Preserve audit window, identify lease consumer and downstream logs/artifacts, assess whether the issuing role/root credential or broader policy is implicated, and fix logging plus scanner coverage. Do not expose the password in incident tickets.
- **Common wrong answers:** Delete the log first; assume TTL expiration is soon enough; revoke every lease globally without assessing blast radius unless the incident warrants it.
- **Scoring rubric:** 8 points: lease-first containment 2; audit/scope 2; old credential verification 2; prevention 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-021 — output interpretation

- **Level:** L3
- **Type:** output interpretation
- **Objective tested:** Integrate U02/U03/U08: Vault audit shows unusual reads and auth failures
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** **Units:** U02/U03/U08. **Scenario:** Synthetic audit events show an unexpected identity reading a secret path followed by repeated authentication failures. Fields are illustrative and may not match every version. Give a safe, evidence-led response and name the verification criteria.
- **Expected answer / model solution:** Correlate timestamp, entity/alias, auth method, token/accessor metadata, path, source, result, and adjacent events. Verify audit coverage and time synchronization. Revoke/contain the suspicious identity or credential based on confidence and impact; inspect policy changes and downstream database/cloud activity; avoid logging secret values. Test legitimate access and forbidden paths after remediation.
- **Common wrong answers:** Treat every auth failure as proof of compromise; ignore successful reads because they are few; copy full request payloads into chat.
- **Scoring rubric:** 8 points: correlate evidence 2; proportionate containment 2; scope downstream activity 2; safe verification/prevention 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-022 — incident/troubleshooting

- **Level:** L4
- **Type:** incident/troubleshooting
- **Objective tested:** Integrate U02/U06/U07: Unexpected ServiceAccount read a Secret
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** **Units:** U02/U06/U07. **Scenario:** Kubernetes audit evidence indicates ServiceAccount `batch/worker` read a Secret in namespace `payments`, although its intended scope is `batch` only. The exact cluster audit policy is unknown. This is a multi-stage scenario: state the order of operations, decision points, trade-offs, and verification criteria.
- **Expected answer / model solution:** Preserve audit metadata and identify the API verb, object, user, namespace, source, and time window. Check RoleBindings/ClusterRoleBindings, projected token exposure, impersonation, controller permissions, and namespace-scoped policies. Contain the identity if unauthorized access is credible, rotate affected secret(s), and add a negative RBAC test. Verify audit policy coverage for the cluster version.
- **Common wrong answers:** Assume namespace names isolate access automatically; delete the ServiceAccount before collecting evidence; rotate every cluster secret without scoping.
- **Scoring rubric:** 8 points: evidence 2; permission-path analysis 2; containment/rotation 2; negative test 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-023 — incident/troubleshooting

- **Level:** L4
- **Type:** incident/troubleshooting
- **Objective tested:** Integrate U01/U03/U04: Unknown dependencies before rotation
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** **Units:** U01/U03/U04. **Scenario:** A service owner requests urgent rotation, but inventory is missing and multiple ETL jobs may share the credential. The credential is not confirmed compromised but is high privilege. This is a multi-stage scenario: state the order of operations, decision points, trade-offs, and verification criteria.
- **Expected answer / model solution:** Immediately establish an incident/rotation owner and map consumers from manifests, secret references, audit, deployment metadata, and service-owner interviews. If compromise is credible, containment takes priority and controlled outage may be necessary; otherwise plan overlap where safe, canary rollout, pool refresh, rollback limits, and a time-bounded removal of the old credential. Verify every consumer and old-credential rejection.
- **Common wrong answers:** Delay forever until inventory is perfect; rotate silently at the issuer and assume consumers update; leave both credentials valid indefinitely.
- **Scoring rubric:** 8 points: owner/evidence 2; urgency decision 2; rollout/rollback 2; completion verification 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-024 — incident/troubleshooting

- **Level:** L4
- **Type:** incident/troubleshooting
- **Objective tested:** Integrate U02/U03/U04: Secret manager unavailable during response
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** **Units:** U02/U03/U04. **Scenario:** The approved secret manager is unavailable during a suspected credential leak. No local copy of the secret is allowed; break-glass access is documented but requires an authorized approver. This is a multi-stage scenario: state the order of operations, decision points, trade-offs, and verification criteria.
- **Expected answer / model solution:** Use the incident process and approved break-glass route; do not bypass custody controls or paste secrets into chat. Determine whether the issuer offers an independent emergency disable path, preserve evidence, restrict affected workload access/network paths if safe, escalate to the service owner/provider support through approved channels, and restore access from documented recovery material. After service returns, rotate/revoke, reconcile state, and test recovery.
- **Common wrong answers:** Store a temporary plaintext copy in a shared file; disable unrelated services without impact assessment; assume the manager outage means the credential is invalid.
- **Scoring rubric:** 8 points: safe containment 2; approved escalation/recovery 2; evidence 1; post-recovery rotation/reconciliation 2; prevention 1.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-025 — output interpretation

- **Level:** L4
- **Type:** output interpretation
- **Objective tested:** Integrate U02/U03/U08: High-privilege alert reaches automation
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** **Units:** U02/U03/U08. **Scenario:** An automated responder receives an alert about a suspected organization-wide admin credential. The alert source has a 3% known false-positive rate and the responder can revoke credentials. This is a multi-stage scenario: state the order of operations, decision points, trade-offs, and verification criteria.
- **Expected answer / model solution:** Use automation for evidence capture, enrichment, deduplication, and reversible low-risk containment. Require human approval or a pre-authorized incident policy for high-impact revocation unless a defined emergency threshold is met. Use idempotency keys, blast-radius estimates, rate limits, and a circuit breaker; record the decision and verify both security and service health.
- **Common wrong answers:** Always revoke everything immediately regardless of confidence; never automate any response; retry indefinitely until the provider accepts the request.
- **Scoring rubric:** 8 points: risk-based gate 2; safe automation boundaries 2; idempotency/rate controls 2; verification/audit 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-026 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** Integrate U08/U02: Detector duplicates events and retry storm
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** **Units:** U08/U02. **Scenario:** A synthetic scanner emits the same finding on every retry, creating duplicate tickets and repeated rotation requests. Some rotation actions are not idempotent. Give a safe, evidence-led response and name the verification criteria.
- **Expected answer / model solution:** Use a stable fingerprint based on detector, repository/object, secret type, and location while avoiding storing the secret value. Make response state transitions idempotent; use bounded retries, exponential backoff, rate limits, and a circuit breaker. Separate detection event from remediation action; require approval for broad revocation and record completion evidence.
- **Common wrong answers:** Use the secret itself as the ticket deduplication key; retry every second; make every finding automatically trigger a new rotation.
- **Scoring rubric:** 8 points: safe fingerprint 2; idempotency 2; bounded retry/circuit breaker 2; approval/audit 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-027 — design

- **Level:** L4
- **Type:** design
- **Objective tested:** Integrate U01/U08: Organization-wide coverage and SLOs
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** **Units:** U01/U08. **Scenario:** A platform team wants a measurable secret detection program across source, Git history, CI logs/artifacts, container images, IaC/manifests, and collaboration systems. Coverage is currently unknown. Give a safe, evidence-led response and name the verification criteria.
- **Expected answer / model solution:** Create an inventory of repositories, build systems, registries, artifact stores, and log surfaces; assign owners and scan cadence; use synthetic canaries/fixtures to prove each surface is covered; track detector false positives and exceptions. Define time-to-detect and time-to-revoke by severity, with explicit start/stop events and reporting of missing telemetry. Avoid claiming full coverage where systems cannot be scanned.
- **Common wrong answers:** Use one scanner's green status as the organization-wide SLO; measure only number of findings; ignore unscannable SaaS surfaces.
- **Scoring rubric:** 8 points: surface inventory 2; coverage tests 2; meaningful SLOs 2; gaps/ownership 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-028 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** Integrate U01/U08: URL-encoded or split fragments in logs
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** **Units:** U01/U08. **Scenario:** An application logs a URL-encoded token fragment in one line and the remainder in a second line. Basic exact-string redaction does not match either line independently. Give a safe, evidence-led response and name the verification criteria.
- **Expected answer / model solution:** Avoid logging credentials at source; redact structured sensitive fields before serialization; test URL-encoded, Base64, split, nested, and partial fixtures. Restrict log access and retention; if a live credential may be recoverable, rotate/revoke and scope log exports/downstream indexes. Redaction is defense in depth, not permission to log secrets.
- **Common wrong answers:** Assume exact-string masking catches transformations; increase log retention for easier debugging; paste reconstructed token into a ticket.
- **Scoring rubric:** 8 points: prevention vs redaction 2; fixture coverage 2; containment/rotation 2; access/retention 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-029 — output interpretation

- **Level:** L2
- **Type:** output interpretation
- **Objective tested:** Integrate U01/U08: Developer wants to paste secret into ticket
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** **Units:** U01/U08. **Scenario:** A developer proposes posting the synthetic-looking but unverified token in a broad incident ticket to speed debugging. Give a safe, evidence-led response and name the verification criteria.
- **Expected answer / model solution:** Do not paste it. Share a secret-free identifier, source location, timestamp, redacted fingerprint, owner, and approved secret-manager reference. Treat the value as potentially live until classified; use the approved incident channel and access controls. If already posted, restrict access, preserve metadata, assess audience/retention, and rotate if exposure is credible.
- **Common wrong answers:** Post it temporarily then delete; assume private ticket permissions are sufficient; put it in an attachment instead of the body.
- **Scoring rubric:** 6 points: no disclosure 2; safe metadata 2; response if already exposed 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-030 — incident/troubleshooting

- **Level:** L4
- **Type:** incident/troubleshooting
- **Objective tested:** Integrate U01/U08: Unknown service owner
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** **Units:** U01/U08. **Scenario:** A high-privilege credential appears in an artifact. Inventory owner is blank, audit retention is limited, and the on-call team cannot identify a consumer immediately. This is a multi-stage scenario: state the order of operations, decision points, trade-offs, and verification criteria.
- **Expected answer / model solution:** Assign an incident commander and service-owner escalation path; determine issuer and privileges from the secret manager/IAM inventory and audit metadata, not from the secret value. If credible exposure exists, disable/rotate through the authorized owner path while assessing service impact. Preserve evidence, identify consumers from deployment references, and make owner/runbook fields mandatory going forward.
- **Common wrong answers:** Wait for the owner to appear before containing; broadcast the credential to find the owner; assume no owner means no consumers.
- **Scoring rubric:** 8 points: accountable escalation 2; safe identification 2; containment decision 2; governance fix 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-031 — design

- **Level:** L3
- **Type:** design
- **Objective tested:** Integrate U01/U07: Static credential and workload identity coexist
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** **Units:** U01/U07. **Scenario:** A workload has both a synthetic static cloud key and a configured federated identity. Logs show recent static-key use but not its exact source. Give a safe, evidence-led response and name the verification criteria.
- **Expected answer / model solution:** Prove the federated path works with issuer/signature/audience/subject checks and least-privilege authorization; enumerate static key consumers and usage; deploy identity-based access, monitor for static-key use, then disable/revoke the key after a controlled cutover. Search source, CI variables, images, backups, and runtime references; verify old key rejection through authorized control-plane evidence.
- **Common wrong answers:** Delete the key file while leaving the issuer key active; remove fallback before proving federation works; trust zero log events without checking audit coverage.
- **Scoring rubric:** 8 points: federation validation 2; usage inventory 2; staged removal 2; negative verification 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-032 — output interpretation

- **Level:** L3
- **Type:** output interpretation
- **Objective tested:** Integrate U01/U05/U06/U08: Stale secret remains in backup or registry
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** **Units:** U01/U05/U06/U08. **Scenario:** Source cleanup is complete, but a retained backup and image digest may contain an old synthetic credential. The credential has been rotated but retention requirements apply. Give a safe, evidence-led response and name the verification criteria.
- **Expected answer / model solution:** Confirm the old credential is invalid; identify backup/image copies, access controls, retention/deletion constraints, and restore paths. Remove or quarantine copies where policy permits, ensure future restores cannot reintroduce the old credential, and test restore hygiene. Document residual risk if deletion is not possible. Rotation does not erase old copies, but invalidation reduces their utility.
- **Common wrong answers:** Assume cleanup of source removed all copies; violate retention policy by deleting evidence without approval; declare all risk gone without checking restore paths.
- **Scoring rubric:** 8 points: invalidation 2; residual-copy inventory 2; restore controls 2; residual-risk record 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-033 — output interpretation

- **Level:** L3
- **Type:** output interpretation
- **Objective tested:** Integrate U03/U04/U05: GitOps continually reintroduces old value
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** **Units:** U03/U04/U05. **Scenario:** A secret is rotated at the provider, but a GitOps controller repeatedly restores the old value from an encrypted manifest or rendered Helm values. Give a safe, evidence-led response and name the verification criteria.
- **Expected answer / model solution:** Identify the authoritative source of desired state and trace whether the old value comes from SOPS/Sealed Secrets, Helm values, an ExternalSecret target, or a stale controller cache. Update the source of truth and encryption/reference configuration, then reconcile in a controlled way. Ensure old credential is invalid, inspect rendered manifests/logs for plaintext, and verify the controller no longer restores it.
- **Common wrong answers:** Repeatedly patch the live Kubernetes Secret; disable GitOps indefinitely; assume ciphertext means the old live credential cannot be used.
- **Scoring rubric:** 8 points: source-of-truth trace 2; live containment 2; controlled reconcile 2; verification 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-034 — incident/troubleshooting

- **Level:** L3
- **Type:** incident/troubleshooting
- **Objective tested:** Integrate U03/U04/U06: Issuer rotation succeeds but pools use old sessions
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** **Units:** U03/U04/U06. **Scenario:** The issuer has replaced a synthetic database password. Existing pooled connections remain open, while new connections fail intermittently because replicas refresh at different times. Give a safe, evidence-led response and name the verification criteria.
- **Expected answer / model solution:** Distinguish authentication for new connections from established sessions. Map replicas/pools, refresh logic, rollout waves, grace overlap, and retry behavior. Ensure old credential invalidation is deliberate and compatible with incident risk; refresh/recycle pools safely, monitor connection errors, and verify each replica uses the new credential. If compromise is suspected, prioritize containment over a long overlap.
- **Common wrong answers:** Assume successful issuer rotation updates existing sessions; terminate all connections without workload impact analysis; retain the old credential forever as fallback.
- **Scoring rubric:** 8 points: session/pool distinction 2; dependency/rollout plan 2; verification per replica 2; security trade-off 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-035 — output interpretation

- **Level:** L3
- **Type:** output interpretation
- **Objective tested:** Integrate U01/U08: Green scanner but untested surfaces
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** **Units:** U01/U08. **Scenario:** CI reports zero findings, but no test fixtures exercise Git history, logs, images, or artifacts. The team claims comprehensive coverage. Give a safe, evidence-led response and name the verification criteria.
- **Expected answer / model solution:** Reject the broad assurance claim. Build synthetic positive fixtures for each promised surface and negative fixtures for false-positive behavior; verify scanner scope/config/version and failure policy; record unscannable surfaces and compensating controls. A green run proves only that configured checks found no issue in their tested scope.
- **Common wrong answers:** Treat zero findings as zero risk; test only working-tree files; count installed scanners instead of coverage.
- **Scoring rubric:** 8 points: scope critique 2; surface fixture plan 3; version/config evidence 1; honest reporting 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-036 — incident/troubleshooting

- **Level:** L3
- **Type:** incident/troubleshooting
- **Objective tested:** Integrate U02/U04/U06/U07: Cross-tenant secret access attempt
- **Estimated time:** [ILLUSTRATIVE] 10 minutes
- **Question / context:** **Units:** U02/U04/U06/U07. **Scenario:** Tenant A workload tries to access Tenant B's synthetic secret through a shared store or role. The request is denied once, but inherited cluster permissions are not reviewed. Give a safe, evidence-led response and name the verification criteria.
- **Expected answer / model solution:** Preserve identity, path, namespace, role/store mapping, and denial evidence. Review provider IAM, Vault policies, Kubernetes RBAC, cluster-scoped stores, service-account bindings, and controller permissions. Add a negative test for Tenant A against Tenant B and a positive test for Tenant A's own resource; inspect audit evidence and ensure the denial is enforced at the source boundary where possible.
- **Common wrong answers:** Treat one denial as proof of isolation; grant cluster-wide access to simplify debugging; test only the controller identity, not workload identity.
- **Scoring rubric:** 8 points: layered boundary review 3; positive/negative test 2; audit/blast-radius 2; ownership 1.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-037 — incident/troubleshooting

- **Level:** L4
- **Type:** incident/troubleshooting
- **Objective tested:** Integrate U01/U05/U08: Encrypted Git file but decryption key compromised
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** **Units:** U01/U05/U08. **Scenario:** A private decryption key used for encrypted Git files may have been exposed. The repository contains old ciphertext and some decrypted CI artifacts. This is a multi-stage scenario: state the order of operations, decision points, trade-offs, and verification criteria.
- **Expected answer / model solution:** Assess which identities and ciphertext are in scope, preserve evidence, restrict/revoke compromised decryption access, and rotate any live credentials that the key could reveal. Determine whether old ciphertext can be decrypted by the exposed key, inspect CI artifacts and repository copies, re-encrypt with new trusted recipients/keys, and test recovery from authorized backup. History cleanup is secondary to credential invalidation.
- **Common wrong answers:** Assume encrypted files remain safe after key compromise; rotate only the file-encryption key but not exposed live credentials; purge Git first.
- **Scoring rubric:** 10 points: key/ciphertext scope 2; live credential rotation 2; key custody/re-encryption 2; artifacts/history 2; recovery test 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

### M09-XI-038 — incident/troubleshooting

- **Level:** L4
- **Type:** incident/troubleshooting
- **Objective tested:** Integrate U01/U02/U08: Incident lacks timestamps, inventory, audit retention, owner
- **Estimated time:** [ILLUSTRATIVE] 15 minutes
- **Question / context:** **Units:** U01/U02/U08. **Scenario:** A production incident has only a vague alert, no owner field, inconsistent timestamps, and a short audit-retention window. A high-privilege credential may be involved. This is a multi-stage scenario: state the order of operations, decision points, trade-offs, and verification criteria.
- **Expected answer / model solution:** Start incident command and preserve all remaining evidence with source/time-zone/clock notes. Establish a bounded timeline from CI, identity, API, deployment, and registry metadata; identify credential issuer and consumers; make a risk-based revocation decision; document unknowns explicitly. Then implement inventory ownership, synchronized timestamps, audit retention, escalation/runbooks, and periodic game days. Do not invent a complete timeline from missing data.
- **Common wrong answers:** Delay containment until all evidence is perfect; claim absence of logs proves no access; alter logs to normalize timestamps without preserving originals.
- **Scoring rubric:** 10 points: preserve evidence 2; timeline/scope 2; containment decision 2; explicit uncertainty 2; governance prevention 2.
- **Safety/version note:** Synthetic/offline scenario. Exact cloud-host, controller, command, and version behavior is [VERIFY] unless stated otherwise.

## Twelve design-review whiteboard prompts

### WB-01 — Choosing a secrets architecture for a data/AI platform

- **Context and constraints:** Two workloads need an external API token and dynamic database credentials; zero-budget local learning first, production later.
- **Approach A:** Approach A: ESO/CSI for static external values plus workload identity for dynamic issuance. Approach B: Vault Agent/Vault dynamic secrets for both if operational ownership supports it.
- **Approach B:** Compare at least one credible alternative against the stated constraints; see the trade-off analysis below.
- **Key trade-offs:** Compare consumer interface, credential lifetime, audit, blast radius, reload, availability, operator burden, and local-vs-production fidelity. Keep the two workload needs distinct.
- **Answer outline:** State assumptions, trace the identity/secret flow, identify enforcement boundaries, describe failure and recovery, and include positive/negative verification plus ownership.
- **Scoring rubric (10 points):** requirements and correctness 2; least privilege/trust boundaries 2; failure/rotation/recovery 2; verification/evidence 2; trade-offs/ownership/caveats 2.

### WB-02 — ESO versus CSI versus Vault Agent

- **Context and constraints:** The app can read a file but does not need a Kubernetes Secret object; a second legacy app expects an environment variable.
- **Approach A:** ESO creates/reconciles a Kubernetes object; CSI mounts provider values as files; Vault Agent can render/renew Vault-issued values close to the workload.
- **Approach B:** Compare at least one credible alternative against the stated constraints; see the trade-off analysis below.
- **Key trade-offs:** Compare etcd/RBAC exposure, reload behavior, provider integration, renewal, namespace boundaries, observability, and operational complexity. Exact behavior is version/driver dependent [VERIFY].
- **Answer outline:** State assumptions, trace the identity/secret flow, identify enforcement boundaries, describe failure and recovery, and include positive/negative verification plus ownership.
- **Scoring rubric (10 points):** requirements and correctness 2; least privilege/trust boundaries 2; failure/rotation/recovery 2; verification/evidence 2; trade-offs/ownership/caveats 2.

### WB-03 — Vault availability, initialization/unseal, recovery, and audit

- **Context and constraints:** A small platform needs a production-oriented design and a documented break-glass path.
- **Approach A:** Approach A: managed Vault service where available. Approach B: self-managed HA with carefully controlled storage, seal/recovery dependencies, and operations.
- **Approach B:** Compare at least one credible alternative against the stated constraints; see the trade-off analysis below.
- **Key trade-offs:** Discuss availability, custody, root-token minimization, quorum/restore, audit-device failure, access to audit logs, and tested recovery. Do not treat dev mode as production.
- **Answer outline:** State assumptions, trace the identity/secret flow, identify enforcement boundaries, describe failure and recovery, and include positive/negative verification plus ownership.
- **Scoring rubric (10 points):** requirements and correctness 2; least privilege/trust boundaries 2; failure/rotation/recovery 2; verification/evidence 2; trade-offs/ownership/caveats 2.

### WB-04 — TTL and rotation for long-running ETL

- **Context and constraints:** A job runs 90 minutes, writes checkpoints, and uses a pooled DB client; credential renewal can fail.
- **Approach A:** Approach A: renewable dynamic credential plus client/pool refresh. Approach B: bounded overlapping static-role rotation with explicit rollout, if dynamic issuance is unavailable.
- **Approach B:** Compare at least one credible alternative against the stated constraints; see the trade-off analysis below.
- **Key trade-offs:** Compare TTL to measured duration, renewal margin, pool behavior, checkpoint/idempotency, outage tolerance, and old credential invalidation.
- **Answer outline:** State assumptions, trace the identity/secret flow, identify enforcement boundaries, describe failure and recovery, and include positive/negative verification plus ownership.
- **Scoring rubric (10 points):** requirements and correctness 2; least privilege/trust boundaries 2; failure/rotation/recovery 2; verification/evidence 2; trade-offs/ownership/caveats 2.

### WB-05 — Trust-policy design for Kubernetes workloads and CI OIDC

- **Context and constraints:** Only a protected main-branch workflow and one Kubernetes ServiceAccount should receive a role.
- **Approach A:** Approach A: workload federation with issuer/audience/subject conditions. Approach B: short-lived brokered identity via Vault or provider-specific workload identity.
- **Approach B:** Compare at least one credible alternative against the stated constraints; see the trade-off analysis below.
- **Key trade-offs:** Constrain issuer, signature/key, audience, subject/ref/environment, time claims, and resulting authorization. Host claim names and federation details [VERIFY].
- **Answer outline:** State assumptions, trace the identity/secret flow, identify enforcement boundaries, describe failure and recovery, and include positive/negative verification plus ownership.
- **Scoring rubric (10 points):** requirements and correctness 2; least privilege/trust boundaries 2; failure/rotation/recovery 2; verification/evidence 2; trade-offs/ownership/caveats 2.

### WB-06 — Kubernetes encryption-at-rest and key custody

- **Context and constraints:** A cluster stores Secret objects and etcd snapshots are backed up. Control-plane ownership differs between local and managed environments.
- **Approach A:** Approach A: API-server encryption-at-rest with controlled key custody. Approach B: managed KMS integration where supported.
- **Approach B:** Compare at least one credible alternative against the stated constraints; see the trade-off analysis below.
- **Key trade-offs:** Compare API/RBAC access, encryption provider boundary, existing-object migration, key rotation, snapshots, recovery, and managed-provider responsibilities.
- **Answer outline:** State assumptions, trace the identity/secret flow, identify enforcement boundaries, describe failure and recovery, and include positive/negative verification plus ownership.
- **Scoring rubric (10 points):** requirements and correctness 2; least privilege/trust boundaries 2; failure/rotation/recovery 2; verification/evidence 2; trade-offs/ownership/caveats 2.

### WB-07 — GitOps secret handling with SOPS/Sealed Secrets and manager references

- **Context and constraints:** The team wants reviewable Git history but must avoid plaintext values and keep recovery possible.
- **Approach A:** Approach A: encrypted files with controlled decryption key custody. Approach B: Git stores only references while ESO/CSI/Vault retrieves runtime values.
- **Approach B:** Compare at least one credible alternative against the stated constraints; see the trade-off analysis below.
- **Key trade-offs:** Compare CI decryption permissions, plaintext render/diff/log risk, key loss/compromise, scope, rotation, and app freshness.
- **Answer outline:** State assumptions, trace the identity/secret flow, identify enforcement boundaries, describe failure and recovery, and include positive/negative verification plus ownership.
- **Scoring rubric (10 points):** requirements and correctness 2; least privilege/trust boundaries 2; failure/rotation/recovery 2; verification/evidence 2; trade-offs/ownership/caveats 2.

### WB-08 — Leak-detection and incident-response program

- **Context and constraints:** The organization has several repositories, image registries, CI systems, and log platforms; coverage is unmeasured.
- **Approach A:** Approach A: local hooks plus CI/server-side checks and scheduled historical/artifact scans. Approach B: centralized scanning with surface-specific connectors and incident automation.
- **Approach B:** Compare at least one credible alternative against the stated constraints; see the trade-off analysis below.
- **Key trade-offs:** Compare coverage, false positives, latency, exception governance, access to findings, SLOs, and safe automation.
- **Answer outline:** State assumptions, trace the identity/secret flow, identify enforcement boundaries, describe failure and recovery, and include positive/negative verification plus ownership.
- **Scoring rubric (10 points):** requirements and correctness 2; least privilege/trust boundaries 2; failure/rotation/recovery 2; verification/evidence 2; trade-offs/ownership/caveats 2.

### WB-09 — Roadmap for eliminating static credentials and measuring progress

- **Context and constraints:** Hundreds of workloads have static keys; some providers support federation, others do not.
- **Approach A:** Approach A: prioritize high-privilege/high-exposure workloads and migrate to workload identity. Approach B: use short-lived brokered credentials as an interim control.
- **Approach B:** Compare at least one credible alternative against the stated constraints; see the trade-off analysis below.
- **Key trade-offs:** Compare migration risk, dependency mapping, fallback, provider capability, ownership, and evidence that static usage has ceased.
- **Answer outline:** State assumptions, trace the identity/secret flow, identify enforcement boundaries, describe failure and recovery, and include positive/negative verification plus ownership.
- **Scoring rubric (10 points):** requirements and correctness 2; least privilege/trust boundaries 2; failure/rotation/recovery 2; verification/evidence 2; trade-offs/ownership/caveats 2.

### WB-10 — Break-glass access and emergency revocation/rotation

- **Context and constraints:** The secret manager may be unavailable during an incident; emergency admin access can affect many services.
- **Approach A:** Approach A: pre-authorized emergency disable path with multi-party approval. Approach B: documented offline recovery material with controlled custody and audit.
- **Approach B:** Compare at least one credible alternative against the stated constraints; see the trade-off analysis below.
- **Key trade-offs:** Compare response speed, misuse risk, availability, custody, audit, recovery, and blast radius. Define thresholds where human approval is required.
- **Answer outline:** State assumptions, trace the identity/secret flow, identify enforcement boundaries, describe failure and recovery, and include positive/negative verification plus ownership.
- **Scoring rubric (10 points):** requirements and correctness 2; least privilege/trust boundaries 2; failure/rotation/recovery 2; verification/evidence 2; trade-offs/ownership/caveats 2.

### WB-11 — Multi-tenant secret isolation and negative-test strategy

- **Context and constraints:** Tenants share cluster controllers but must not read one another's secrets.
- **Approach A:** Approach A: namespace-scoped stores/roles and provider IAM boundaries. Approach B: separate control-plane identities or clusters for higher isolation needs.
- **Approach B:** Compare at least one credible alternative against the stated constraints; see the trade-off analysis below.
- **Key trade-offs:** Compare blast radius, shared controller privilege, cluster-scoped resources, tenant onboarding, audit, and testability.
- **Answer outline:** State assumptions, trace the identity/secret flow, identify enforcement boundaries, describe failure and recovery, and include positive/negative verification plus ownership.
- **Scoring rubric (10 points):** requirements and correctness 2; least privilege/trust boundaries 2; failure/rotation/recovery 2; verification/evidence 2; trade-offs/ownership/caveats 2.

### WB-12 — Vault versus cloud secret manager under zero-budget learning and production constraints

- **Context and constraints:** The learner can run a local disposable lab but production may use a managed cloud provider later.
- **Approach A:** Approach A: local Vault-compatible lab to learn auth, policy, leases, audit, and recovery. Approach B: provider-native secret manager/workload identity in production when organization support and requirements fit.
- **Approach B:** Compare at least one credible alternative against the stated constraints; see the trade-off analysis below.
- **Key trade-offs:** Compare zero-cost learning, operational ownership, integration, availability, portability, audit, dynamic secrets, and provider lock-in. Do not infer local parity with cloud behavior.
- **Answer outline:** State assumptions, trace the identity/secret flow, identify enforcement boundaries, describe failure and recovery, and include positive/negative verification plus ownership.
- **Scoring rubric (10 points):** requirements and correctness 2; least privilege/trust boundaries 2; failure/rotation/recovery 2; verification/evidence 2; trade-offs/ownership/caveats 2.

## Final answer-key index and remediation map

Answers are adjacent to each question to keep this file self-contained. Use the stable ID prefix to locate remediation:

- `M09-U01-Q01`–`M09-U01-Q18`: **Secrets threat model and lifecycle**; revisit `01-secrets-threat-model-and-lifecycle.md`.
- `M09-U02-Q01`–`M09-U02-Q18`: **HashiCorp Vault architecture and auth methods**; revisit `02-hashicorp-vault-architecture-and-auth-methods.md`.
- `M09-U03-Q01`–`M09-U03-Q18`: **Dynamic secrets, leases, and rotation**; revisit `03-dynamic-secrets-leases-and-rotation.md`.
- `M09-U04-Q01`–`M09-U04-Q18`: **External Secrets Operator and cloud secret managers**; revisit `04-external-secrets-operator-and-cloud-secret-managers.md`.
- `M09-U05-Q01`–`M09-U05-Q18`: **SOPS, Sealed Secrets, and encrypted secrets in Git**; revisit `05-sops-sealed-secrets-and-encrypted-secrets-in-git.md`.
- `M09-U06-Q01`–`M09-U06-Q18`: **Kubernetes Secret encryption and the CSI Secret Store**; revisit `06-kubernetes-secret-encryption-and-csi-secret-store.md`.
- `M09-U07-Q01`–`M09-U07-Q18`: **Workload identity, IRSA, and federated credentials**; revisit `07-workload-identity-irsa-and-federated-credentials.md`.
- `M09-U08-Q01`–`M09-U08-Q18`: **Secret leak detection and incident response**; revisit `08-secret-leak-detection-and-incident-response.md`.
- `M09-XI-001`–`M09-XI-038`: cross-unit reasoning; follow each scenario's unit list and remediate the corresponding lesson files.

**Retest rule:** do not memorize model answers. Re-answer with a changed boundary condition and produce evidence for the positive and negative test. For an incident, name the first action and justify it. For rotation, include dependency discovery and safe verification that the old credential no longer works.

## References, version notes, and claim register

Official documentation starting points (consult the exact version/host in use; URL paths and behavior may change). These are reference entry points, not claims that a live environment was inspected:

- HashiCorp Vault documentation: https://developer.hashicorp.com/vault/docs
- Kubernetes documentation: https://kubernetes.io/docs/concepts/configuration/secret/ ; https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/ ; https://kubernetes.io/docs/reference/access-authn-authz/rbac/ ; https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/
- External Secrets Operator documentation: https://external-secrets.io/latest/
- Secrets Store CSI Driver documentation: https://secrets-store-csi-driver.sigs.k8s.io/
- Mozilla SOPS repository/docs: https://github.com/getsops/sops
- Bitnami Sealed Secrets repository/docs: https://github.com/bitnami-labs/sealed-secrets
- AWS EKS IAM roles for service accounts: https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html
- Google Cloud Workload Identity Federation: https://cloud.google.com/iam/docs/workload-identity-federation
- Microsoft Entra workload identity federation: https://learn.microsoft.com/en-us/entra/workload-id/workload-identity-federation
- Gitleaks documentation: https://github.com/gitleaks/gitleaks
- Trivy secret scanning: https://trivy.dev/latest/docs/scanner/secret/
- pre-commit documentation: https://pre-commit.com/
- TruffleHog documentation: https://github.com/trufflesecurity/trufflehog
- detect-secrets documentation: https://github.com/Yelp/detect-secrets
- Git documentation: https://git-scm.com/docs
- git-filter-repo documentation: https://github.com/newren/git-filter-repo

**Version note:** This bank intentionally avoids treating any one CRD schema, CLI flag, cloud trust claim, event name, encryption provider configuration, or managed-service default as universal. Marked `[VERIFY]` claims must be checked against the installed release and target host before real use. URLs are official project/vendor entry points; their current content and version applicability should be rechecked at use time.

### Claim register

Status meanings: **[ILLUSTRATIVE]** synthetic examples; **[ASSUMPTION]** scenario premise; **[SIMULATION]** local/mock behavior; **[VERIFY]** product/host/version detail requiring current verification. No entry below implies a live lab was run.

| ID | Claim | Relevant unit/question IDs | Product/version/host scope | Source | Status | Next verification action |
|---|---|---|---|---|---|---|
| C01 | Base64 is reversible encoding, not confidentiality protection | U01-Q06; U06-Q01; XI-006 | General/Kubernetes Secret representation | Kubernetes Secrets docs | Verified concept | Check current Kubernetes docs and cluster config |
| C02 | Secret lifecycle includes rotation and revocation as distinct operations | U01-Q02; U03-Q05; U08-Q06 | General | Vault docs; course syllabus | Verified concept | Map to the actual issuer's supported operations |
| C03 | A deleted file may remain in Git history or artifacts | U01-Q03; U05-Q12; U08-Q02; XI-010 | Git/CI/registry | Git docs; scanner docs | Verified concept | Inspect only disposable repo and artifact scopes |
| C04 | A successful happy path does not prove least privilege | U02-Q12; U06-Q15; U07-Q17 | General access control | Kubernetes RBAC/Vault policy docs | Verified concept | Run explicit negative tests |
| C05 | Vault dev mode is for development, not production security | U02-Q02 | Vault release-specific behavior | Vault docs | [VERIFY] | Review current Vault dev-mode documentation |
| C06 | Vault policy path/capability behavior is version/config dependent | U02-Q06; U02-Q12 | Vault exact version/mount | Vault docs | [VERIFY] | Test policy with allowed and forbidden paths |
| C07 | Vault Kubernetes auth details depend on setup and version | U02-Q07; XI-021 | Vault/Kubernetes | Vault docs; Kubernetes docs | [VERIFY] | Verify TokenReview, audience, and auth config |
| C08 | Vault audit events may contain sensitive metadata and require access controls | U02-Q09; XI-021 | Vault configured audit devices | Vault docs | [VERIFY] | Review current audit-device behavior and redaction |
| C09 | Dynamic credential TTL must fit workload refresh behavior | U03-Q02; U03-Q08; XI-003 | Vault/DB/client | Vault lease docs | [ASSUMPTION] | Measure job duration and renewal margin |
| C10 | Lease revocation may affect dependent sessions or new connections differently | U03-Q05; U03-Q12; XI-003 | DB backend/client pool | Vault and DB docs | [VERIFY] | Test isolated backend and pool semantics |
| C11 | Database dynamic role SQL grants are backend-specific | U03-Q03 | Database/Vault DB engine | Vault DB secrets engine docs | [VERIFY] | Review exact DB plugin and role config |
| C12 | ESO reconciliation schemas and status fields vary by release | U04-Q01; U04-Q09 | ESO installed CRD version | ESO docs | [VERIFY] | Inspect installed CRDs and matching release docs |
| C13 | SecretStore and ClusterSecretStore scope differ by resource design | U04-Q02; XI-036 | ESO CRD version | ESO docs | [VERIFY] | Review namespace/cluster scope and provider auth |
| C14 | Provider value update does not guarantee process reload | U04-Q06; U06-Q09; XI-004 | Application runtime | ESO/CSI and app docs | Verified concept | Test process adoption end-to-end |
| C15 | CSI refresh semantics depend on driver/provider/configuration | U04-Q12; U06-Q06; XI-005 | CSI driver/provider version | CSI Driver docs | [VERIFY] | Check rotation feature and mount behavior |
| C16 | SOPS decryption requires access to configured recipient/key material | U05-Q01; U05-Q13 | SOPS version/config | SOPS docs | [VERIFY] | Review exact config and recipient setup |
| C17 | Sealed Secrets scope/controller key behavior is release/config dependent | U05-Q03; U05-Q09 | Sealed Secrets version/scope | Sealed Secrets docs | [VERIFY] | Check scope mode and controller key custody |
| C18 | Encrypted Git does not invalidate a leaked live credential | U05-Q04; XI-037 | General | Course security principle | Verified concept | Rotate credential and test old-value rejection |
| C19 | Rendered manifests or CI logs may expose plaintext after decryption | U05-Q05; XI-002 | GitOps/CI toolchain | SOPS/GitOps docs | Verified concept | Inspect disposable pipeline output and artifact retention |
| C20 | Kubernetes encryption-at-rest configuration differs by cluster/version | U06-Q02; U06-Q13; XI-006 | Kubernetes distribution/version | Kubernetes docs | [VERIFY] | Check control-plane configuration with cluster owner |
| C21 | Enabling encryption config may not by itself prove old objects are rewritten | U06-Q16; XI-006 | Kubernetes/version/provider | Kubernetes encryption docs | [VERIFY] | Follow version-specific migration/rewrite procedure |
| C22 | etcd snapshots can retain previously persisted secret data | U06-Q12; XI-006 | Backup and cluster configuration | Kubernetes/etcd docs | [VERIFY] | Review snapshot access and encryption history |
| C23 | SecretProviderClass schema is driver/provider version dependent | U06-Q07 | CSI driver/provider version | CSI Driver docs | [VERIFY] | Validate installed CRD and provider documentation |
| C24 | Projected ServiceAccount token properties depend on cluster/configuration | U07-Q05 | Kubernetes version | Kubernetes ServiceAccount docs | [VERIFY] | Inspect token projection and audience configuration |
| C25 | JWT acceptance requires signature, issuer, audience, subject, and time checks as configured | U07-Q02; XI-007 | Verifier policy | JWT/OIDC/Vault docs | Verified concept | Test each claim mismatch independently |
| C26 | Decoded JWT claims are not proof of signature validity | U07-Q16 | JWT verifier | JWT/OIDC docs | Verified concept | Use a real verifier in a local synthetic test |
| C27 | JWKS rotation/cache behavior depends on verifier implementation | U07-Q03; U07-Q11 | OIDC provider/verifier | Provider and library docs | [VERIFY] | Test unknown-kid and key-rollover behavior |
| C28 | AWS IRSA trust configuration is host-specific | U07-Q06 | AWS EKS/cluster version | AWS EKS docs | [VERIFY] | Check current EKS guide and trust policy |
| C29 | EKS Pod Identity differs from IRSA; do not assume identical setup | U07-Q07 | AWS EKS current service | AWS EKS docs | [VERIFY] | Review current service documentation |
| C30 | GCP and Azure federation claim mapping is provider-specific | U07-Q08 | GCP/Azure host configuration | Google/Microsoft docs | [VERIFY] | Verify issuer, subject, audience, and attribute mapping |
| C31 | Local JWT/STS-like simulation cannot prove cloud parity | U07-Q13; XI-007 | Local lab | Course limitation | [SIMULATION] | Record exactly what was simulated |
| C32 | Scanner coverage depends on configured paths, history, and artifact surfaces | U08-Q02; U08-Q17; XI-035 | Gitleaks/Trivy/version | Official scanner docs | [VERIFY] | Run synthetic fixture matrix across each promised surface |
| C33 | Gitleaks and Trivy command/config behavior is version-dependent | U08-Q03; U08-Q15 | Installed scanner version | Official tool docs | [VERIFY] | Check installed release docs before use |
| C34 | Pre-commit is a local control and can be bypassed | U08-Q03; XI-013 | Developer workflow | pre-commit docs | Verified concept | Confirm CI/server-side backstops |
| C35 | History rewriting is hygiene, not credential invalidation | U08-Q06; XI-009; XI-010 | Git and replicas | Git docs | Verified concept | Verify old credential invalidation separately |
| C36 | Redaction can miss encoded or split fragments | U08-Q05; XI-028 | Logging pipeline | Application/logging design | Verified concept | Test synthetic encoded/split fixtures |
| C37 | Automated response needs idempotency, rate limits, and human gates | U08-Q12; XI-025; XI-026 | Response orchestration | Course operational design | [ASSUMPTION] | Exercise duplicate/retry and high-impact approval paths |
| C38 | TTD/TTR SLO definitions require explicit event boundaries | U08-Q11; XI-027 | Organization program | Course measurement design | [ASSUMPTION] | Agree start/stop timestamps and severity tiers |
| C39 | All sample credentials/logs/configs are synthetic | All units; all XI | This document | Author-created examples | [ILLUSTRATIVE] | Keep fake-value patterns and inspect before reuse |
| C40 | Incident chronology and log timestamps may be incomplete or skewed | U08-Q13; XI-038 | Local/production observability | Course incident premise | [ASSUMPTION] | Record source clock/time zone and uncertainty |

## Ten-pass authenticity and completeness audit

1. **Source alignment:** the bank follows the supplied M09 Unit 1–8 ordering and topic scope. Questions are mapped by unit IDs and cross-unit scenario labels. The syllabus source itself should be treated as authoritative; where a specific lesson detail is not present in the accessible source, the bank uses explicit assumptions and verification notes rather than asserting product defaults.
2. **Coverage:** all eight units appear in syllabus order; the required topic families are represented across questions and scenarios.
3. **Count integrity:** 18 questions per unit × 8 = 144; 38 distinct cross-unit scenarios; **182 total unique questions**. IDs are stable and ranges are enumerated in the ledger.
4. **Answer completeness:** each numbered question includes level, type, objective, illustrative time, context, model answer, common wrong answers, rubric, and safety/version note.
5. **MCQ quality:** each unit has exactly three MCQs (24 total); each has four options and explanations for the correct choice and every distractor.
6. **Technical authenticity:** volatile CLI flags, CRD fields, provider claims, managed-cluster defaults, event names, and version-specific behavior are marked `[VERIFY]` in the question bank/claim register. The linked URLs are official documentation entry points; their current page contents were not independently revalidated in this artifact-generation pass.
7. **Security safety:** sample credentials and outputs are synthetic. No question instructs learners to validate credentials against a live third-party service. Incident answers prioritize revocation/rotation before history cleanup when the credential may still be valid.
8. **Assessment balance:** L1–L4 questions cover fundamentals, implementation, troubleshooting, and design/program management. The unit pattern includes short answer, MCQ, output interpretation, config review, incidents, design, hands-on, boundary tests, evidence reasoning, and trade-offs.
9. **References and traceability:** official project/vendor documentation entry points and a 40-entry claim register are included. A reference link is not a claim that the page was freshly opened or that the tool was executed.
10. **Structural and immutability audit:** required top-level sections and exactly 12 whiteboard prompts are present in this generated standalone file. No repository files were modified. No live labs, credential scans, cloud API calls, production changes, or runtime product tests were performed.

## Sign-off and known limitations

- **Artifact:** `practice-questions.md` (standalone Markdown file).
- **Question count:** 182 unique questions — Unit 1: 18; Unit 2: 18; Unit 3: 18; Unit 4: 18; Unit 5: 18; Unit 6: 18; Unit 7: 18; Unit 8: 18; cross-unit: 38.
- **Whiteboard prompts:** exactly 12.
- **Claim register:** 40 entries.
- **Roadmap tree access:** the exact `Roadmap_ptree.md` was **not independently inspected** during this artifact generation. The supplied prompt's stated M09 layout and scope were used. No claim is made that the artifact was installed into or committed to a repository.
- **Repository mutation:** no repository file was modified; only this standalone artifact was created.
- **Verification limits:** no live labs or runtime tests were run. Official URLs are listed as documentation entry points, but their current content was not freshly verified in this pass. Claims marked `[VERIFY]` must be checked against the exact product version and host before real use.
