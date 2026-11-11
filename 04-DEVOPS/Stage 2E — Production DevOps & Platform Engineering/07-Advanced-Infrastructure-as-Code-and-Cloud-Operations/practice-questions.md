**Sources actually inspected:** uploaded `Pasted markdown(20261028-061918).md`; relevant retrieved sections of `PROMPT-Advanced-Infrastructure-as-Code-and-Cloud-Operations.md` (Unit 13 requirements and Unit 14 capstone). The roadmap tree and individual lesson/capstone files were not independently available.

# Stage 2E — Advanced Infrastructure as Code and Cloud Operations
## Practice Questions, Answer Keys, and Design Review

**Source inspection note:** I inspected the uploaded assessment-generation prompt and searched the Library for `PROMPT-Advanced-Infrastructure-as-Code-and-Cloud-Operations.md`; the authoritative prompt’s Unit 13 requirements and Unit 14 capstone scenario/deliverables were available. The actual `Roadmap_ptree.md`, repository checkout, individual Unit 1–12 lesson files, and capstone project file were not independently available for inspection in this session. Accordingly, this assessment is grounded in the uploaded prompt’s explicit unit coverage map and retrieved syllabus/capstone sections, not a claim that each lesson file was read. Where a detail is version-sensitive it is marked. `[ASSUMPTION]` denotes a teaching scenario synthesized from the stated syllabus.

> **Safety:** All outputs are synthetic and all execution practice is intended for disposable local labs or LocalStack by default. Do not run destructive examples against production. Verify installed tool/provider versions and official documentation before using version-sensitive syntax.

## How to use this assessment

Attempt each question before reading the model answer. Preserve evidence for code reviews: target identity, backend, plan/output, policy results, relevant logs, and a short decision record. Questions have stable IDs. The 144 unit questions plus 30 cross-unit scenarios total **174 explicitly identified questions**; ten whiteboard prompts and the capstone checkpoint are additional assessment components, not counted toward 174.

## Coverage matrix

| Unit | Source-derived syllabus coverage | Required IDs |
|---|---|---|
| Unit 1 — 1 | state maps resource addresses to remote objects; backend stores state; locking serializes supported operations; backups and recovery must preserve a known-good copy; state can contain secrets; manual state surgery is exceptional. | U01-SA-01…U01-DES-01 (12) |
| Unit 2 — 2 | modules encapsulate reusable resource patterns behind typed inputs and outputs; examples and validation clarify contracts; environments reuse pinned versions while keeping identities, backends, and environment-specific values separate. | U02-SA-01…U02-DES-01 (12) |
| Unit 3 — 3 | migration changes state location/address or adopts existing objects; backup and ownership mapping precede changes; drift compares declared configuration with observed objects; avoid dual management. | U03-SA-01…U03-DES-01 (12) |
| Unit 4 — 4 | plans are proposed changes; create/update/delete/replace and unknown values require context; saved plans and artifacts are sensitive; approval binds to reviewed evidence; rollback is not always a simple inverse apply. | U04-SA-01…U04-DES-01 (12) |
| Unit 5 — 5 | separate account/project/subscription, identity, backend and configuration where appropriate; workspaces alone are not a security boundary; CI identity and endpoint/profile must be asserted. | U05-SA-01…U05-DES-01 (12) |
| Unit 6 — 6 | policy evaluates selected configuration/plan evidence; policy tests and explicit deny rules provide pre-apply guardrails; exemptions need owner, scope, expiry and evidence; policy is not IAM or runtime compliance. | U06-SA-01…U06-DES-01 (12) |
| Unit 7 — 7 | quotas and service limits differ by service/account/region and can be adjustable or hard; preflight must account for existing usage, concurrent changes and recovery headroom; never assume fixed values. | U07-SA-01…U07-DES-01 (12) |
| Unit 8 — 8 | decommission requires ownership/inventory, retention and dependency checks, reviewed destroy plan, dry-run discovery, deletion caps, approvals, and evidence; prevent recurring leaks with TTL/tagging and accountable ownership. | U08-SA-01…U08-DES-01 (12) |
| Unit 9 — 9 | tool choice weighs workflow, state/plan semantics, language, reuse, ecosystem, migration and governance; similar concepts do not guarantee interchangeable syntax, state, providers or operational behavior. | U09-SA-01…U09-DES-01 (12) |
| Unit 10 — 10 | inventory selects targets; playbooks should converge idempotently; use modules and handlers; command/shell need change guards; secrets need Vault/no_log with limits; preserve host-key verification, least privilege and rolling controls. | U10-SA-01…U10-DES-01 (12) |
| Unit 11 — 11 | use a testing pyramid: formatting/static validation, native tests, policy/plan assertions, mocks where supported, emulator tests with fidelity limits, integration/Terratest, post-apply checks; cleanup is a risk-bearing operation. | U11-SA-01…U11-DES-01 (12) |
| Unit 12 — 12 | controllers reconcile desired state; CRDs, ProviderConfig, XRDs, Compositions, XRs/claims define APIs; conditions are evidence not guarantees; deletion/ownership/credentials/RBAC/provider upgrades need careful boundaries. | U12-SA-01…U12-DES-01 (12) |

## Unit-by-unit assessment

### Unit 1 — 1

**Scope and objectives:** state maps resource addresses to remote objects; backend stores state; locking serializes supported operations; backups and recovery must preserve a known-good copy; state can contain secrets; manual state surgery is exceptional.

### U01-SA-01 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L1  
**Objective tested:** Explain state file, remote backend, lock contention, backup/versioning, recovery runbook, least-privilege backend access.  
**Estimated time:** 4 minutes  
**Question:** Explain the core purpose and one important limitation of state file.

**Model answer:** The state is the ownership and mapping record, not a complete backup of the infrastructure or proof that runtime resources are healthy. Verify backend/workspace/identity, stop concurrent writers, preserve copies, and recover through the documented version-specific runbook.

**Rationale:** A common error is to treat the mechanism as a guarantee of runtime health or safety; it only addresses the stated scope.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U01-SA-02 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L2  
**Objective tested:** Explain state file, remote backend, lock contention, backup/versioning, recovery runbook, least-privilege backend access.  
**Estimated time:** 6 minutes  
**Question:** Identify the minimum evidence you would collect before a high-risk change involving state file, remote backend, lock contention, backup/versioning, recovery runbook, least-privilege backend access.

**Model answer:** Collect the declared configuration, target environment and effective identity, relevant state/backend context, proposed change or status output, applicable policy/test results, ownership/dependency evidence, and a recovery/rollback assessment. The state is the ownership and mapping record, not a complete backup of the infrastructure or proof that runtime resources are healthy. Verify backend/workspace/identity, stop concurrent writers, preserve copies, and recover through the documented version-specific runbook.

**Rationale:** The evidence ties the intended change to the correct target and makes impact and recovery reviewable.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U01-SA-03 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L3  
**Objective tested:** Explain state file, remote backend, lock contention, backup/versioning, recovery runbook, least-privilege backend access.  
**Estimated time:** 7 minutes  
**Question:** Describe one failure mode and one preventive control for state file, remote backend, lock contention, backup/versioning, recovery runbook, least-privilege backend access.

**Model answer:** Failure mode: local state checked into Git; force-unlock without proving stale lock; edit state JSON by hand; restore a backup without checking lineage/serial and resulting plan. Prevention: explicit target and ownership checks, least privilege, reviewable evidence, bounded change scope, and a tested recovery path appropriate to the tool.

**Rationale:** Prevention should interrupt the failure before mutation and provide observable evidence that the guardrail works.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U01-MCQ-01 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L1  
**Objective tested:** Choose a safe and technically accurate response for 1.  
**Estimated time:** 3 minutes  
**Question:** What is the safest first response to a suspected state corruption event?

A. Run state-changing commands until the error disappears
B. Stop concurrent writers and preserve state/backend evidence
C. Delete the lock record immediately
D. Recreate all resources manually

**Model answer:** **B.** Stop concurrent writers and preserve state/backend evidence

**Rationale:** Stopping writes and preserving evidence prevents compounding damage and enables controlled recovery.

**Common wrong answers / distractor analysis:** **A:** A can worsen divergence **B:** Correct choice. **C:** C may remove a valid lock **D:** D risks duplication and data loss.

### U01-MCQ-02 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L2  
**Objective tested:** Choose a safe and technically accurate response for 1.  
**Estimated time:** 3 minutes  
**Question:** What does remote state locking primarily provide when supported by the backend?

A. Encryption of every secret in all artifacts
B. Serialization of conflicting state operations
C. Proof that resources are healthy
D. A replacement for IAM

**Model answer:** **B.** Serialization of conflicting state operations

**Rationale:** Locking coordinates concurrent operations against the same state.

**Common wrong answers / distractor analysis:** **A:** A is a separate security property **B:** Correct choice. **C:** C confuses state coordination with runtime health **D:** D is false because access control remains necessary.

### U01-MCQ-03 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L3  
**Objective tested:** Choose a safe and technically accurate response for 1.  
**Estimated time:** 3 minutes  
**Question:** A state backup is available. What must happen before restoration?

A. Restore immediately without comparing context
B. Verify backend/workspace, preserve current copy, and follow the recovery runbook
C. Commit the backup to Git for audit
D. Unlock every backend lock

**Model answer:** **B.** Verify backend/workspace, preserve current copy, and follow the recovery runbook

**Rationale:** Recovery requires correct target and evidence preservation before changing authoritative state.

**Common wrong answers / distractor analysis:** **A:** A can restore the wrong environment **B:** Correct choice. **C:** C may expose secrets **D:** D is unrelated and unsafe.

### U01-OUT-01 — Output interpretation — initial signal

**Unit / topic:** Output interpretation — initial signal  
**Level:** L2  
**Objective tested:** Interpret an 1 signal without overclaiming.  
**Estimated time:** 7 minutes  
**Question:** [ILLUSTRATIVE] A tool run reports: `target=backend=state-prod; lock=held by another operation`. No additional context is provided.

Read the synthetic output. What can you infer, what remains unknown, and what is the safest next action?

**Model answer:** The output is a signal, not enough to authorize a change. Confirm the effective target and identity, collect surrounding logs/state/plan or conditions, determine whether any mutation partially succeeded, and assess affected resources and rollback before acting. Specifically for this unit: The state is the ownership and mapping record, not a complete backup of the infrastructure or proof that runtime resources are healthy. Verify backend/workspace/identity, stop concurrent writers, preserve copies, and recover through the documented version-specific runbook.

**Rationale:** The output identifies a risk or failure category but lacks enough context to prove full scope, root cause, or safe recovery.

**Common wrong answers:** Assuming success from a single status field; retrying immediately; taking a destructive action before target and partial-success checks.

**Safety/version note:** [ILLUSTRATIVE] Synthetic output; not executed.

### U01-OUT-02 — Output interpretation — incomplete green gate

**Unit / topic:** Output interpretation — incomplete green gate  
**Level:** L3  
**Objective tested:** Identify missing evidence for 1.  
**Estimated time:** 8 minutes  
**Question:** [ILLUSTRATIVE] A reviewer receives a green CI summary: `validate=PASS policy=PASS plan=PASS`. The artifact has no recorded target account/project, backend identifier, effective identity, or post-apply verification. The diff includes a change related to state file.

Should the reviewer approve, reject, or request more information? Explain what is and is not proven.

**Model answer:** **Needs-info / hold.** Green checks only prove the recorded checks passed against their actual inputs. Require target/backend/identity evidence, the complete reviewed diff and relevant state, plus unit-specific evidence: The state is the ownership and mapping record, not a complete backup of the infrastructure or proof that runtime resources are healthy. Verify backend/workspace/identity, stop concurrent writers, preserve copies, and recover through the documented version-specific runbook.

**Rationale:** A green summary is not a substitute for artifact identity, target proof, scope review, or runtime/post-change verification.

**Common wrong answers:** Approve because all statuses are green; reject without examining evidence when a hold can safely resolve uncertainty; assume the plan proves runtime behavior.

**Safety/version note:** [ILLUSTRATIVE] Synthetic output; not executed.

### U01-REV-01 — Code/config review

**Unit / topic:** Code/config review  
**Level:** L3  
**Objective tested:** Find at least three defects in a 1 workflow and propose safer corrections.  
**Estimated time:** 10 minutes  
**Question:** Review this intentionally flawed snippet. Identify at least three substantive defects, their likely impact, and a corrected pattern. Do not execute it.

```text
# Illustrative state/backend workflow (intentionally flawed)
terraform { backend "local" {} }
# state file copied into repository
# CI permits parallel apply jobs
# lock error handler always removes the lock
```

**Model answer:**
1. **Defect and correction:** Local-only backend is not a suitable shared CI state design; select a supported remote backend and document locking/versioning.
2. **Defect and correction:** State is committed/copied into repository; remove it from source control, restrict access and rotate any exposed secrets.
3. **Defect and correction:** Parallel writers plus blind lock removal can corrupt state; serialize operations and prove a lock is stale before supported recovery.

**Rationale:** The snippet lacks layered controls for state file, remote backend, lock contention, backup/versioning, recovery runbook, least-privilege backend access; a safe correction verifies target and ownership, narrows permissions and change scope, preserves evidence, and includes a tested recovery path.

**Common wrong answers:** Fixing only syntax; treating a comment as an enforced control; assuming a green command means the operation is safe; overlooking secret exposure or cleanup.

**Safety/version note:** `[ILLUSTRATIVE]` Review exercise only; not executed. Confirm syntax and behavior for the installed versions before adapting any pattern.

### U01-REV-02 — Code/config review

**Unit / topic:** Code/config review  
**Level:** L4  
**Objective tested:** Find at least three defects in a 1 workflow and propose safer corrections.  
**Estimated time:** 12 minutes  
**Question:** Review this intentionally flawed snippet. Identify at least three substantive defects, their likely impact, and a corrected pattern. Do not execute it.

```text
# Illustrative state/backend workflow (intentionally flawed)
terraform { backend "local" {} }
# state file copied into repository
# CI permits parallel apply jobs
# lock error handler always removes the lock
```

**Model answer:**
1. **Defect and correction:** Parallel writers plus blind lock removal can corrupt state; serialize operations and prove a lock is stale before supported recovery.
2. **Defect and correction:** State is committed/copied into repository; remove it from source control, restrict access and rotate any exposed secrets.
3. **Defect and correction:** Local-only backend is not a suitable shared CI state design; select a supported remote backend and document locking/versioning.

**Rationale:** The snippet lacks layered controls for state file, remote backend, lock contention, backup/versioning, recovery runbook, least-privilege backend access; a safe correction verifies target and ownership, narrows permissions and change scope, preserves evidence, and includes a tested recovery path.

**Common wrong answers:** Fixing only syntax; treating a comment as an enforced control; assuming a green command means the operation is safe; overlooking secret exposure or cleanup.

**Safety/version note:** `[ILLUSTRATIVE]` Review exercise only; not executed. Confirm syntax and behavior for the installed versions before adapting any pattern.

### U01-INC-01 — Incident and troubleshooting

**Unit / topic:** Incident and troubleshooting  
**Level:** L4  
**Objective tested:** Respond to a unit-specific infrastructure failure with containment, blast-radius analysis, recovery and prevention.  
**Estimated time:** 15 minutes  
**Question:** Symptom: a deployment involving state file fails part-way through. Operators disagree whether to retry or roll back. Give a structured response: symptom/evidence → diagnosis → blast-radius and rollback check → immediate fix → prevention/regression test.

**Model answer:** 1. **Contain:** pause further writes/deployments and avoid broad retries. 2. **Evidence:** capture timestamps, exact error, target identity, backend/state or controller status, plan/change record and logs with secrets redacted. 3. **Diagnose:** distinguish configuration error, authorization, provider/API failure, concurrency, partial apply and external drift. 4. **Blast radius:** enumerate changed, replaced, deleted and possibly created resources; identify stateful/data dependencies and other environments. 5. **Rollback/recovery:** verify the correct target, preserve current state/evidence, choose a tested recovery or forward-fix path; do not assume inverse apply is safe. 6. **Fix and verify:** make the smallest reviewed correction and run appropriate post-change checks. 7. **Prevent:** add a regression/negative test, target assertion, alert/runbook or policy as appropriate. Unit-specific concerns: The state is the ownership and mapping record, not a complete backup of the infrastructure or proof that runtime resources are healthy. Verify backend/workspace/identity, stop concurrent writers, preserve copies, and recover through the documented version-specific runbook.

**Rationale:** The sequence prevents a second failure while preserving enough evidence to distinguish root cause from symptoms. Recovery choice depends on partial success, data semantics and tool version.

**Common wrong answers:** Blind retry; destroy/recreate before inventory; restore state without target verification; declare recovery from command exit code alone; omit a regression test.

### U01-DES-01 — Design question with scoring rubric

**Unit / topic:** Design question with scoring rubric  
**Level:** L4  
**Objective tested:** Design an operationally safe 1 approach with explicit trade-offs and evidence.  
**Estimated time:** 20 minutes  
**Question:** Design a solution for state file, remote backend, lock contention, backup/versioning, recovery runbook, least-privilege backend access. State assumptions, define boundaries and ownership, describe normal workflow and failure handling, identify security controls, and explain what evidence demonstrates success. Keep implementation local/LocalStack by default.

**Model answer:** A strong design names the authoritative owner and target; separates environments and credentials where appropriate; documents inputs, versions and limits; uses least privilege, reviewable plans/policy/tests and bounded operations; preserves recovery evidence; and defines post-change verification, alerting, rollback criteria and an exit path. Specifically: The state is the ownership and mapping record, not a complete backup of the infrastructure or proof that runtime resources are healthy. Verify backend/workspace/identity, stop concurrent writers, preserve copies, and recover through the documented version-specific runbook.

**Rationale:** Production quality depends on explicit ownership, fail-safe behavior, verifiable evidence and operational recovery—not merely a successful happy path.

**Common wrong answers:** “Use best practices” without naming controls; assume the tool guarantees safety; omit a failure path; mix dev/prod ownership; provide no evidence or measurable acceptance criteria.

**Scoring rubric (20 points):**
- Correct architecture and ownership boundary — 4
- Target, identity, state and blast-radius controls — 4
- Security/policy/testing controls — 4
- Failure handling, rollback/recovery and verification — 4
- Trade-offs, evidence, version assumptions and exit path — 4

**Safety/version note:** Verify version-sensitive syntax and provider-specific semantics before implementation.


### Unit 2 — 2

**Scope and objectives:** modules encapsulate reusable resource patterns behind typed inputs and outputs; examples and validation clarify contracts; environments reuse pinned versions while keeping identities, backends, and environment-specific values separate.

### U02-SA-01 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L1  
**Objective tested:** Explain module boundaries, input/output contracts, variable validation, semantic versioning, provider ownership, consumer compatibility.  
**Estimated time:** 4 minutes  
**Question:** Explain the core purpose and one important limitation of module boundaries.

**Model answer:** A module is a versioned interface. Review inputs/outputs, defaults, validation, provider assumptions, examples, changelog, and consumer tests before upgrading. Reuse should not collapse environment security boundaries.

**Rationale:** A common error is to treat the mechanism as a guarantee of runtime health or safety; it only addresses the stated scope.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U02-SA-02 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L2  
**Objective tested:** Explain module boundaries, input/output contracts, variable validation, semantic versioning, provider ownership, consumer compatibility.  
**Estimated time:** 6 minutes  
**Question:** Identify the minimum evidence you would collect before a high-risk change involving module boundaries, input/output contracts, variable validation, semantic versioning, provider ownership, consumer compatibility.

**Model answer:** Collect the declared configuration, target environment and effective identity, relevant state/backend context, proposed change or status output, applicable policy/test results, ownership/dependency evidence, and a recovery/rollback assessment. A module is a versioned interface. Review inputs/outputs, defaults, validation, provider assumptions, examples, changelog, and consumer tests before upgrading. Reuse should not collapse environment security boundaries.

**Rationale:** The evidence ties the intended change to the correct target and makes impact and recovery reviewable.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U02-SA-03 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L3  
**Objective tested:** Explain module boundaries, input/output contracts, variable validation, semantic versioning, provider ownership, consumer compatibility.  
**Estimated time:** 7 minutes  
**Question:** Describe one failure mode and one preventive control for module boundaries, input/output contracts, variable validation, semantic versioning, provider ownership, consumer compatibility.

**Model answer:** Failure mode: copy/paste entire environments; breaking output rename without migration; provider credentials embedded in a child module; unpinned moving source. Prevention: explicit target and ownership checks, least privilege, reviewable evidence, bounded change scope, and a tested recovery path appropriate to the tool.

**Rationale:** Prevention should interrupt the failure before mutation and provide observable evidence that the guardrail works.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U02-MCQ-01 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L1  
**Objective tested:** Choose a safe and technically accurate response for 2.  
**Estimated time:** 3 minutes  
**Question:** Which is the strongest module contract?

A. Unvalidated variables and undocumented defaults
B. Typed inputs, validation, stable outputs, examples, and versioned changes
C. A child module that silently configures all credentials
D. One copied module per environment with no tests

**Model answer:** **B.** Typed inputs, validation, stable outputs, examples, and versioned changes

**Rationale:** A module should provide an explicit and testable consumer contract.

**Common wrong answers / distractor analysis:** **A:** A leaves invalid configurations **B:** Correct choice. **C:** C obscures identity boundaries **D:** D duplicates fixes and drifts.

### U02-MCQ-02 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L2  
**Objective tested:** Choose a safe and technically accurate response for 2.  
**Estimated time:** 3 minutes  
**Question:** A new module version renames an output consumed by three environments. Best next step?

A. Publish without notice
B. Assess compatibility, add migration guidance/tests, and version the breaking change
C. Change production first to discover failures
D. Assume outputs are private implementation details

**Model answer:** **B.** Assess compatibility, add migration guidance/tests, and version the breaking change

**Rationale:** Outputs are part of the consumer-facing contract.

**Common wrong answers / distractor analysis:** **A:** A breaks consumers **B:** Correct choice. **C:** C reverses safe rollout **D:** D ignores module interface semantics.

### U02-MCQ-03 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L3  
**Objective tested:** Choose a safe and technically accurate response for 2.  
**Estimated time:** 3 minutes  
**Question:** Why pin module versions in environment configurations?

A. To guarantee zero runtime defects
B. To make the reviewed dependency version reproducible
C. To avoid all testing
D. To share state across environments

**Model answer:** **B.** To make the reviewed dependency version reproducible

**Rationale:** Pinning improves reproducibility and controlled upgrades, but does not guarantee correctness.

**Common wrong answers / distractor analysis:** **A:** A overstates the guarantee **B:** Correct choice. **C:** C is the opposite of good practice **D:** D conflates code reuse with state isolation.

### U02-OUT-01 — Output interpretation — initial signal

**Unit / topic:** Output interpretation — initial signal  
**Level:** L2  
**Objective tested:** Interpret an 2 signal without overclaiming.  
**Estimated time:** 7 minutes  
**Question:** [ILLUSTRATIVE] A tool run reports: `target=module version changed; one consumer output is missing`. No additional context is provided.

Read the synthetic output. What can you infer, what remains unknown, and what is the safest next action?

**Model answer:** The output is a signal, not enough to authorize a change. Confirm the effective target and identity, collect surrounding logs/state/plan or conditions, determine whether any mutation partially succeeded, and assess affected resources and rollback before acting. Specifically for this unit: A module is a versioned interface. Review inputs/outputs, defaults, validation, provider assumptions, examples, changelog, and consumer tests before upgrading. Reuse should not collapse environment security boundaries.

**Rationale:** The output identifies a risk or failure category but lacks enough context to prove full scope, root cause, or safe recovery.

**Common wrong answers:** Assuming success from a single status field; retrying immediately; taking a destructive action before target and partial-success checks.

**Safety/version note:** [ILLUSTRATIVE] Synthetic output; not executed.

### U02-OUT-02 — Output interpretation — incomplete green gate

**Unit / topic:** Output interpretation — incomplete green gate  
**Level:** L3  
**Objective tested:** Identify missing evidence for 2.  
**Estimated time:** 8 minutes  
**Question:** [ILLUSTRATIVE] A reviewer receives a green CI summary: `validate=PASS policy=PASS plan=PASS`. The artifact has no recorded target account/project, backend identifier, effective identity, or post-apply verification. The diff includes a change related to module boundaries.

Should the reviewer approve, reject, or request more information? Explain what is and is not proven.

**Model answer:** **Needs-info / hold.** Green checks only prove the recorded checks passed against their actual inputs. Require target/backend/identity evidence, the complete reviewed diff and relevant state, plus unit-specific evidence: A module is a versioned interface. Review inputs/outputs, defaults, validation, provider assumptions, examples, changelog, and consumer tests before upgrading. Reuse should not collapse environment security boundaries.

**Rationale:** A green summary is not a substitute for artifact identity, target proof, scope review, or runtime/post-change verification.

**Common wrong answers:** Approve because all statuses are green; reject without examining evidence when a hold can safely resolve uncertainty; assume the plan proves runtime behavior.

**Safety/version note:** [ILLUSTRATIVE] Synthetic output; not executed.

### U02-REV-01 — Code/config review

**Unit / topic:** Code/config review  
**Level:** L3  
**Objective tested:** Find at least three defects in a 2 workflow and propose safer corrections.  
**Estimated time:** 10 minutes  
**Question:** Review this intentionally flawed snippet. Identify at least three substantive defects, their likely impact, and a corrected pattern. Do not execute it.

```text
# Illustrative module consumer (intentionally flawed)
module "platform" {
  source = "../modules/platform"
  environment = "prod"
  admin_role_arn = var.shared_admin_role
}
# source is unpinned; required inputs have no validation
# child module silently configures provider credentials
```

**Model answer:**
1. **Defect and correction:** Relative unpinned source may not be reproducible; version/pin module source according to repository policy.
2. **Defect and correction:** Environment string is hard-coded and may be passed incorrectly; use validated typed input and explicit environment configuration.
3. **Defect and correction:** Shared admin role/provider credentials violate least privilege and hide provider boundary; keep provider configuration/identity at intended root boundary.

**Rationale:** The snippet lacks layered controls for module boundaries, input/output contracts, variable validation, semantic versioning, provider ownership, consumer compatibility; a safe correction verifies target and ownership, narrows permissions and change scope, preserves evidence, and includes a tested recovery path.

**Common wrong answers:** Fixing only syntax; treating a comment as an enforced control; assuming a green command means the operation is safe; overlooking secret exposure or cleanup.

**Safety/version note:** `[ILLUSTRATIVE]` Review exercise only; not executed. Confirm syntax and behavior for the installed versions before adapting any pattern.

### U02-REV-02 — Code/config review

**Unit / topic:** Code/config review  
**Level:** L4  
**Objective tested:** Find at least three defects in a 2 workflow and propose safer corrections.  
**Estimated time:** 12 minutes  
**Question:** Review this intentionally flawed snippet. Identify at least three substantive defects, their likely impact, and a corrected pattern. Do not execute it.

```text
# Illustrative module consumer (intentionally flawed)
module "platform" {
  source = "../modules/platform"
  environment = "prod"
  admin_role_arn = var.shared_admin_role
}
# source is unpinned; required inputs have no validation
# child module silently configures provider credentials
```

**Model answer:**
1. **Defect and correction:** Shared admin role/provider credentials violate least privilege and hide provider boundary; keep provider configuration/identity at intended root boundary.
2. **Defect and correction:** Environment string is hard-coded and may be passed incorrectly; use validated typed input and explicit environment configuration.
3. **Defect and correction:** Relative unpinned source may not be reproducible; version/pin module source according to repository policy.

**Rationale:** The snippet lacks layered controls for module boundaries, input/output contracts, variable validation, semantic versioning, provider ownership, consumer compatibility; a safe correction verifies target and ownership, narrows permissions and change scope, preserves evidence, and includes a tested recovery path.

**Common wrong answers:** Fixing only syntax; treating a comment as an enforced control; assuming a green command means the operation is safe; overlooking secret exposure or cleanup.

**Safety/version note:** `[ILLUSTRATIVE]` Review exercise only; not executed. Confirm syntax and behavior for the installed versions before adapting any pattern.

### U02-INC-01 — Incident and troubleshooting

**Unit / topic:** Incident and troubleshooting  
**Level:** L4  
**Objective tested:** Respond to a unit-specific infrastructure failure with containment, blast-radius analysis, recovery and prevention.  
**Estimated time:** 15 minutes  
**Question:** Symptom: a deployment involving module boundaries fails part-way through. Operators disagree whether to retry or roll back. Give a structured response: symptom/evidence → diagnosis → blast-radius and rollback check → immediate fix → prevention/regression test.

**Model answer:** 1. **Contain:** pause further writes/deployments and avoid broad retries. 2. **Evidence:** capture timestamps, exact error, target identity, backend/state or controller status, plan/change record and logs with secrets redacted. 3. **Diagnose:** distinguish configuration error, authorization, provider/API failure, concurrency, partial apply and external drift. 4. **Blast radius:** enumerate changed, replaced, deleted and possibly created resources; identify stateful/data dependencies and other environments. 5. **Rollback/recovery:** verify the correct target, preserve current state/evidence, choose a tested recovery or forward-fix path; do not assume inverse apply is safe. 6. **Fix and verify:** make the smallest reviewed correction and run appropriate post-change checks. 7. **Prevent:** add a regression/negative test, target assertion, alert/runbook or policy as appropriate. Unit-specific concerns: A module is a versioned interface. Review inputs/outputs, defaults, validation, provider assumptions, examples, changelog, and consumer tests before upgrading. Reuse should not collapse environment security boundaries.

**Rationale:** The sequence prevents a second failure while preserving enough evidence to distinguish root cause from symptoms. Recovery choice depends on partial success, data semantics and tool version.

**Common wrong answers:** Blind retry; destroy/recreate before inventory; restore state without target verification; declare recovery from command exit code alone; omit a regression test.

### U02-DES-01 — Design question with scoring rubric

**Unit / topic:** Design question with scoring rubric  
**Level:** L4  
**Objective tested:** Design an operationally safe 2 approach with explicit trade-offs and evidence.  
**Estimated time:** 20 minutes  
**Question:** Design a solution for module boundaries, input/output contracts, variable validation, semantic versioning, provider ownership, consumer compatibility. State assumptions, define boundaries and ownership, describe normal workflow and failure handling, identify security controls, and explain what evidence demonstrates success. Keep implementation local/LocalStack by default.

**Model answer:** A strong design names the authoritative owner and target; separates environments and credentials where appropriate; documents inputs, versions and limits; uses least privilege, reviewable plans/policy/tests and bounded operations; preserves recovery evidence; and defines post-change verification, alerting, rollback criteria and an exit path. Specifically: A module is a versioned interface. Review inputs/outputs, defaults, validation, provider assumptions, examples, changelog, and consumer tests before upgrading. Reuse should not collapse environment security boundaries.

**Rationale:** Production quality depends on explicit ownership, fail-safe behavior, verifiable evidence and operational recovery—not merely a successful happy path.

**Common wrong answers:** “Use best practices” without naming controls; assume the tool guarantees safety; omit a failure path; mix dev/prod ownership; provide no evidence or measurable acceptance criteria.

**Scoring rubric (20 points):**
- Correct architecture and ownership boundary — 4
- Target, identity, state and blast-radius controls — 4
- Security/policy/testing controls — 4
- Failure handling, rollback/recovery and verification — 4
- Trade-offs, evidence, version assumptions and exit path — 4

**Safety/version note:** Verify version-sensitive syntax and provider-specific semantics before implementation.


### Unit 3 — 3

**Scope and objectives:** migration changes state location/address or adopts existing objects; backup and ownership mapping precede changes; drift compares declared configuration with observed objects; avoid dual management.

### U03-SA-01 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L1  
**Objective tested:** Explain import/adoption, state moves, refresh/plan interpretation, drift limitations, backup, ownership exclusivity.  
**Estimated time:** 4 minutes  
**Question:** Explain the core purpose and one important limitation of import/adoption.

**Model answer:** Before importing or moving, prove exactly which state owns the object and back up the source and destination state. A plan is evidence about the provider-visible subset, not proof of complete runtime correctness.

**Rationale:** A common error is to treat the mechanism as a guarantee of runtime health or safety; it only addresses the stated scope.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U03-SA-02 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L2  
**Objective tested:** Explain import/adoption, state moves, refresh/plan interpretation, drift limitations, backup, ownership exclusivity.  
**Estimated time:** 6 minutes  
**Question:** Identify the minimum evidence you would collect before a high-risk change involving import/adoption, state moves, refresh/plan interpretation, drift limitations, backup, ownership exclusivity.

**Model answer:** Collect the declared configuration, target environment and effective identity, relevant state/backend context, proposed change or status output, applicable policy/test results, ownership/dependency evidence, and a recovery/rollback assessment. Before importing or moving, prove exactly which state owns the object and back up the source and destination state. A plan is evidence about the provider-visible subset, not proof of complete runtime correctness.

**Rationale:** The evidence ties the intended change to the correct target and makes impact and recovery reviewable.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U03-SA-03 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L3  
**Objective tested:** Explain import/adoption, state moves, refresh/plan interpretation, drift limitations, backup, ownership exclusivity.  
**Estimated time:** 7 minutes  
**Question:** Describe one failure mode and one preventive control for import/adoption, state moves, refresh/plan interpretation, drift limitations, backup, ownership exclusivity.

**Model answer:** Failure mode: importing the same object into two states; assuming import writes desired configuration; treating no diff as proof of no drift; migrating without backup. Prevention: explicit target and ownership checks, least privilege, reviewable evidence, bounded change scope, and a tested recovery path appropriate to the tool.

**Rationale:** Prevention should interrupt the failure before mutation and provide observable evidence that the guardrail works.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U03-MCQ-01 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L1  
**Objective tested:** Choose a safe and technically accurate response for 3.  
**Estimated time:** 3 minutes  
**Question:** Before importing an existing object, the key question is:

A. Can the import command run quickly?
B. Which state will own it, and is it already managed elsewhere?
C. Can the state file be deleted afterward?
D. Can drift checks be disabled permanently?

**Model answer:** **B.** Which state will own it, and is it already managed elsewhere?

**Rationale:** Ownership must be explicit to prevent duplicate state ownership and competing changes.

**Common wrong answers / distractor analysis:** **A:** A ignores risk **B:** Correct choice. **C:** C destroys recovery options **D:** D removes a useful signal.

### U03-MCQ-02 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L2  
**Objective tested:** Choose a safe and technically accurate response for 3.  
**Estimated time:** 3 minutes  
**Question:** A plan shows no changes. What can you conclude?

A. No infrastructure drift exists anywhere
B. The evaluated configuration/state/provider view proposes no changes at this time
C. The runtime service is healthy
D. No secret exists in state

**Model answer:** **B.** The evaluated configuration/state/provider view proposes no changes at this time

**Rationale:** A plan is scoped by configuration, state, provider visibility and timing.

**Common wrong answers / distractor analysis:** **A:** A overgeneralizes scope **B:** Correct choice. **C:** C requires runtime checks **D:** D is false because state may contain secrets.

### U03-MCQ-03 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L3  
**Objective tested:** Choose a safe and technically accurate response for 3.  
**Estimated time:** 3 minutes  
**Question:** A resource is moved between module addresses. Safest approach?

A. Back up state, use the source-supported address-move workflow, then inspect plan
B. Delete and recreate the resource by default
C. Import it into a second state as a precaution
D. Edit state JSON without a recovery copy

**Model answer:** **A.** Back up state, use the source-supported address-move workflow, then inspect plan

**Rationale:** A controlled move preserves ownership mapping and provides reviewable evidence.

**Common wrong answers / distractor analysis:** **A:** Correct choice. **B:** B may be disruptive **C:** C creates dual management **D:** D is fragile and difficult to recover.

### U03-OUT-01 — Output interpretation — initial signal

**Unit / topic:** Output interpretation — initial signal  
**Level:** L2  
**Objective tested:** Interpret an 3 signal without overclaiming.  
**Estimated time:** 7 minutes  
**Question:** [ILLUSTRATIVE] A tool run reports: `target=plan contains an address change and one delete`. No additional context is provided.

Read the synthetic output. What can you infer, what remains unknown, and what is the safest next action?

**Model answer:** The output is a signal, not enough to authorize a change. Confirm the effective target and identity, collect surrounding logs/state/plan or conditions, determine whether any mutation partially succeeded, and assess affected resources and rollback before acting. Specifically for this unit: Before importing or moving, prove exactly which state owns the object and back up the source and destination state. A plan is evidence about the provider-visible subset, not proof of complete runtime correctness.

**Rationale:** The output identifies a risk or failure category but lacks enough context to prove full scope, root cause, or safe recovery.

**Common wrong answers:** Assuming success from a single status field; retrying immediately; taking a destructive action before target and partial-success checks.

**Safety/version note:** [ILLUSTRATIVE] Synthetic output; not executed.

### U03-OUT-02 — Output interpretation — incomplete green gate

**Unit / topic:** Output interpretation — incomplete green gate  
**Level:** L3  
**Objective tested:** Identify missing evidence for 3.  
**Estimated time:** 8 minutes  
**Question:** [ILLUSTRATIVE] A reviewer receives a green CI summary: `validate=PASS policy=PASS plan=PASS`. The artifact has no recorded target account/project, backend identifier, effective identity, or post-apply verification. The diff includes a change related to import/adoption.

Should the reviewer approve, reject, or request more information? Explain what is and is not proven.

**Model answer:** **Needs-info / hold.** Green checks only prove the recorded checks passed against their actual inputs. Require target/backend/identity evidence, the complete reviewed diff and relevant state, plus unit-specific evidence: Before importing or moving, prove exactly which state owns the object and back up the source and destination state. A plan is evidence about the provider-visible subset, not proof of complete runtime correctness.

**Rationale:** A green summary is not a substitute for artifact identity, target proof, scope review, or runtime/post-change verification.

**Common wrong answers:** Approve because all statuses are green; reject without examining evidence when a hold can safely resolve uncertainty; assume the plan proves runtime behavior.

**Safety/version note:** [ILLUSTRATIVE] Synthetic output; not executed.

### U03-REV-01 — Code/config review

**Unit / topic:** Code/config review  
**Level:** L3  
**Objective tested:** Find at least three defects in a 3 workflow and propose safer corrections.  
**Estimated time:** 10 minutes  
**Question:** Review this intentionally flawed snippet. Identify at least three substantive defects, their likely impact, and a corrected pattern. Do not execute it.

```text
# Illustrative adoption workflow (intentionally flawed)
# import object into new state without inventory
# no backup is captured
# existing state keeps managing the same object
# plan is skipped after import
```

**Model answer:**
1. **Defect and correction:** No ownership inventory can cause duplicate management; map exact object/address and current state first.
2. **Defect and correction:** No backup removes recovery path; capture and verify state copies before migration.
3. **Defect and correction:** Two states manage one object and plan is skipped; establish single ownership, inspect plan and test recovery before proceeding.

**Rationale:** The snippet lacks layered controls for import/adoption, state moves, refresh/plan interpretation, drift limitations, backup, ownership exclusivity; a safe correction verifies target and ownership, narrows permissions and change scope, preserves evidence, and includes a tested recovery path.

**Common wrong answers:** Fixing only syntax; treating a comment as an enforced control; assuming a green command means the operation is safe; overlooking secret exposure or cleanup.

**Safety/version note:** `[ILLUSTRATIVE]` Review exercise only; not executed. Confirm syntax and behavior for the installed versions before adapting any pattern.

### U03-REV-02 — Code/config review

**Unit / topic:** Code/config review  
**Level:** L4  
**Objective tested:** Find at least three defects in a 3 workflow and propose safer corrections.  
**Estimated time:** 12 minutes  
**Question:** Review this intentionally flawed snippet. Identify at least three substantive defects, their likely impact, and a corrected pattern. Do not execute it.

```text
# Illustrative adoption workflow (intentionally flawed)
# import object into new state without inventory
# no backup is captured
# existing state keeps managing the same object
# plan is skipped after import
```

**Model answer:**
1. **Defect and correction:** Two states manage one object and plan is skipped; establish single ownership, inspect plan and test recovery before proceeding.
2. **Defect and correction:** No backup removes recovery path; capture and verify state copies before migration.
3. **Defect and correction:** No ownership inventory can cause duplicate management; map exact object/address and current state first.

**Rationale:** The snippet lacks layered controls for import/adoption, state moves, refresh/plan interpretation, drift limitations, backup, ownership exclusivity; a safe correction verifies target and ownership, narrows permissions and change scope, preserves evidence, and includes a tested recovery path.

**Common wrong answers:** Fixing only syntax; treating a comment as an enforced control; assuming a green command means the operation is safe; overlooking secret exposure or cleanup.

**Safety/version note:** `[ILLUSTRATIVE]` Review exercise only; not executed. Confirm syntax and behavior for the installed versions before adapting any pattern.

### U03-INC-01 — Incident and troubleshooting

**Unit / topic:** Incident and troubleshooting  
**Level:** L4  
**Objective tested:** Respond to a unit-specific infrastructure failure with containment, blast-radius analysis, recovery and prevention.  
**Estimated time:** 15 minutes  
**Question:** Symptom: a deployment involving import/adoption fails part-way through. Operators disagree whether to retry or roll back. Give a structured response: symptom/evidence → diagnosis → blast-radius and rollback check → immediate fix → prevention/regression test.

**Model answer:** 1. **Contain:** pause further writes/deployments and avoid broad retries. 2. **Evidence:** capture timestamps, exact error, target identity, backend/state or controller status, plan/change record and logs with secrets redacted. 3. **Diagnose:** distinguish configuration error, authorization, provider/API failure, concurrency, partial apply and external drift. 4. **Blast radius:** enumerate changed, replaced, deleted and possibly created resources; identify stateful/data dependencies and other environments. 5. **Rollback/recovery:** verify the correct target, preserve current state/evidence, choose a tested recovery or forward-fix path; do not assume inverse apply is safe. 6. **Fix and verify:** make the smallest reviewed correction and run appropriate post-change checks. 7. **Prevent:** add a regression/negative test, target assertion, alert/runbook or policy as appropriate. Unit-specific concerns: Before importing or moving, prove exactly which state owns the object and back up the source and destination state. A plan is evidence about the provider-visible subset, not proof of complete runtime correctness.

**Rationale:** The sequence prevents a second failure while preserving enough evidence to distinguish root cause from symptoms. Recovery choice depends on partial success, data semantics and tool version.

**Common wrong answers:** Blind retry; destroy/recreate before inventory; restore state without target verification; declare recovery from command exit code alone; omit a regression test.

### U03-DES-01 — Design question with scoring rubric

**Unit / topic:** Design question with scoring rubric  
**Level:** L4  
**Objective tested:** Design an operationally safe 3 approach with explicit trade-offs and evidence.  
**Estimated time:** 20 minutes  
**Question:** Design a solution for import/adoption, state moves, refresh/plan interpretation, drift limitations, backup, ownership exclusivity. State assumptions, define boundaries and ownership, describe normal workflow and failure handling, identify security controls, and explain what evidence demonstrates success. Keep implementation local/LocalStack by default.

**Model answer:** A strong design names the authoritative owner and target; separates environments and credentials where appropriate; documents inputs, versions and limits; uses least privilege, reviewable plans/policy/tests and bounded operations; preserves recovery evidence; and defines post-change verification, alerting, rollback criteria and an exit path. Specifically: Before importing or moving, prove exactly which state owns the object and back up the source and destination state. A plan is evidence about the provider-visible subset, not proof of complete runtime correctness.

**Rationale:** Production quality depends on explicit ownership, fail-safe behavior, verifiable evidence and operational recovery—not merely a successful happy path.

**Common wrong answers:** “Use best practices” without naming controls; assume the tool guarantees safety; omit a failure path; mix dev/prod ownership; provide no evidence or measurable acceptance criteria.

**Scoring rubric (20 points):**
- Correct architecture and ownership boundary — 4
- Target, identity, state and blast-radius controls — 4
- Security/policy/testing controls — 4
- Failure handling, rollback/recovery and verification — 4
- Trade-offs, evidence, version assumptions and exit path — 4

**Safety/version note:** Verify version-sensitive syntax and provider-specific semantics before implementation.


### Unit 4 — 4

**Scope and objectives:** plans are proposed changes; create/update/delete/replace and unknown values require context; saved plans and artifacts are sensitive; approval binds to reviewed evidence; rollback is not always a simple inverse apply.

### U04-SA-01 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L1  
**Objective tested:** Explain plan review, replacements, unknowns, blast radius, saved plan integrity, approval, post-apply checks.  
**Estimated time:** 4 minutes  
**Question:** Explain the core purpose and one important limitation of plan review.

**Model answer:** Classify approve/reject/needs-info. Confirm target, identity, backend, resource actions, unknowns, policy results, stateful dependencies, rollback and post-apply verification. A plan is not a guarantee.

**Rationale:** A common error is to treat the mechanism as a guarantee of runtime health or safety; it only addresses the stated scope.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U04-SA-02 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L2  
**Objective tested:** Explain plan review, replacements, unknowns, blast radius, saved plan integrity, approval, post-apply checks.  
**Estimated time:** 6 minutes  
**Question:** Identify the minimum evidence you would collect before a high-risk change involving plan review, replacements, unknowns, blast radius, saved plan integrity, approval, post-apply checks.

**Model answer:** Collect the declared configuration, target environment and effective identity, relevant state/backend context, proposed change or status output, applicable policy/test results, ownership/dependency evidence, and a recovery/rollback assessment. Classify approve/reject/needs-info. Confirm target, identity, backend, resource actions, unknowns, policy results, stateful dependencies, rollback and post-apply verification. A plan is not a guarantee.

**Rationale:** The evidence ties the intended change to the correct target and makes impact and recovery reviewable.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U04-SA-03 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L3  
**Objective tested:** Explain plan review, replacements, unknowns, blast radius, saved plan integrity, approval, post-apply checks.  
**Estimated time:** 7 minutes  
**Question:** Describe one failure mode and one preventive control for plan review, replacements, unknowns, blast radius, saved plan integrity, approval, post-apply checks.

**Model answer:** Failure mode: approve due only to successful exit code; apply a regenerated/unreviewed plan; assume replacement is harmless; publish plan artifacts. Prevention: explicit target and ownership checks, least privilege, reviewable evidence, bounded change scope, and a tested recovery path appropriate to the tool.

**Rationale:** Prevention should interrupt the failure before mutation and provide observable evidence that the guardrail works.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U04-MCQ-01 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L1  
**Objective tested:** Choose a safe and technically accurate response for 4.  
**Estimated time:** 3 minutes  
**Question:** A plan includes an unexpected replacement of a stateful resource. Decision?

A. Approve because replacement is a normal action
B. Reject or hold pending cause, data/availability impact, and recovery evidence
C. Apply and inspect later
D. Ignore because unknown values are harmless

**Model answer:** **B.** Reject or hold pending cause, data/availability impact, and recovery evidence

**Rationale:** Unexpected replacement is a high-risk change needing explanation and explicit safeguards.

**Common wrong answers / distractor analysis:** **A:** This option ignores the required safety boundary and is not supported by the evidence. **B:** Correct choice. **C:** This option ignores the required safety boundary and is not supported by the evidence. **D:** This option ignores the required safety boundary and is not supported by the evidence.

### U04-MCQ-02 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L2  
**Objective tested:** Choose a safe and technically accurate response for 4.  
**Estimated time:** 3 minutes  
**Question:** Which statement about a saved plan is correct?

A. It is safe to publish because it is read-only
B. It can contain sensitive information and should be protected and tied to review
C. It proves runtime behavior
D. It can be regenerated after approval without re-review

**Model answer:** **B.** It can contain sensitive information and should be protected and tied to review

**Rationale:** Saved plans and derived JSON can reveal sensitive values and represent a specific proposal.

**Common wrong answers / distractor analysis:** **A:** A ignores exposure **B:** Correct choice. **C:** C overstates plan guarantees **D:** D breaks approval-to-artifact integrity.

### U04-MCQ-03 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L3  
**Objective tested:** Choose a safe and technically accurate response for 4.  
**Estimated time:** 3 minutes  
**Question:** A CI plan passed but target identity is not recorded. What is the best decision?

A. Approve because the job passed
B. Needs-info: prove account/project, identity, backend, and environment before approval
C. Run destroy to verify identity
D. Treat workspace name as sufficient proof

**Model answer:** **B.** Needs-info: prove account/project, identity, backend, and environment before approval

**Rationale:** Target verification is a prerequisite for safe change.

**Common wrong answers / distractor analysis:** **A:** A relies on process success alone **B:** Correct choice. **C:** C is destructive **D:** D treats a weak selector as a security boundary.

### U04-OUT-01 — Output interpretation — initial signal

**Unit / topic:** Output interpretation — initial signal  
**Level:** L2  
**Objective tested:** Interpret an 4 signal without overclaiming.  
**Estimated time:** 7 minutes  
**Question:** [ILLUSTRATIVE] A tool run reports: `target=2 to add, 1 to destroy; replacement marked for a stateful object`. No additional context is provided.

Read the synthetic output. What can you infer, what remains unknown, and what is the safest next action?

**Model answer:** The output is a signal, not enough to authorize a change. Confirm the effective target and identity, collect surrounding logs/state/plan or conditions, determine whether any mutation partially succeeded, and assess affected resources and rollback before acting. Specifically for this unit: Classify approve/reject/needs-info. Confirm target, identity, backend, resource actions, unknowns, policy results, stateful dependencies, rollback and post-apply verification. A plan is not a guarantee.

**Rationale:** The output identifies a risk or failure category but lacks enough context to prove full scope, root cause, or safe recovery.

**Common wrong answers:** Assuming success from a single status field; retrying immediately; taking a destructive action before target and partial-success checks.

**Safety/version note:** [ILLUSTRATIVE] Synthetic output; not executed.

### U04-OUT-02 — Output interpretation — incomplete green gate

**Unit / topic:** Output interpretation — incomplete green gate  
**Level:** L3  
**Objective tested:** Identify missing evidence for 4.  
**Estimated time:** 8 minutes  
**Question:** [ILLUSTRATIVE] A reviewer receives a green CI summary: `validate=PASS policy=PASS plan=PASS`. The artifact has no recorded target account/project, backend identifier, effective identity, or post-apply verification. The diff includes a change related to plan review.

Should the reviewer approve, reject, or request more information? Explain what is and is not proven.

**Model answer:** **Needs-info / hold.** Green checks only prove the recorded checks passed against their actual inputs. Require target/backend/identity evidence, the complete reviewed diff and relevant state, plus unit-specific evidence: Classify approve/reject/needs-info. Confirm target, identity, backend, resource actions, unknowns, policy results, stateful dependencies, rollback and post-apply verification. A plan is not a guarantee.

**Rationale:** A green summary is not a substitute for artifact identity, target proof, scope review, or runtime/post-change verification.

**Common wrong answers:** Approve because all statuses are green; reject without examining evidence when a hold can safely resolve uncertainty; assume the plan proves runtime behavior.

**Safety/version note:** [ILLUSTRATIVE] Synthetic output; not executed.

### U04-REV-01 — Code/config review

**Unit / topic:** Code/config review  
**Level:** L3  
**Objective tested:** Find at least three defects in a 4 workflow and propose safer corrections.  
**Estimated time:** 10 minutes  
**Question:** Review this intentionally flawed snippet. Identify at least three substantive defects, their likely impact, and a corrected pattern. Do not execute it.

```text
# Illustrative change gate (intentionally flawed)
if plan_command_succeeded; then
  terraform apply -auto-approve
fi
# target identity is not asserted
# reviewed saved plan is not the applied artifact
# destroy/replace actions are not analyzed
```

**Model answer:**
1. **Defect and correction:** Plan success alone is not approval; review actions, unknowns and policy results.
2. **Defect and correction:** Applying a newly generated/unreviewed plan breaks reviewed-artifact binding; apply the exact approved saved plan where supported.
3. **Defect and correction:** No target identity assertion creates cross-environment blast radius; fail closed on account/backend/profile mismatch.

**Rationale:** The snippet lacks layered controls for plan review, replacements, unknowns, blast radius, saved plan integrity, approval, post-apply checks; a safe correction verifies target and ownership, narrows permissions and change scope, preserves evidence, and includes a tested recovery path.

**Common wrong answers:** Fixing only syntax; treating a comment as an enforced control; assuming a green command means the operation is safe; overlooking secret exposure or cleanup.

**Safety/version note:** `[ILLUSTRATIVE]` Review exercise only; not executed. Confirm syntax and behavior for the installed versions before adapting any pattern.

### U04-REV-02 — Code/config review

**Unit / topic:** Code/config review  
**Level:** L4  
**Objective tested:** Find at least three defects in a 4 workflow and propose safer corrections.  
**Estimated time:** 12 minutes  
**Question:** Review this intentionally flawed snippet. Identify at least three substantive defects, their likely impact, and a corrected pattern. Do not execute it.

```text
# Illustrative change gate (intentionally flawed)
if plan_command_succeeded; then
  terraform apply -auto-approve
fi
# target identity is not asserted
# reviewed saved plan is not the applied artifact
# destroy/replace actions are not analyzed
```

**Model answer:**
1. **Defect and correction:** No target identity assertion creates cross-environment blast radius; fail closed on account/backend/profile mismatch.
2. **Defect and correction:** Applying a newly generated/unreviewed plan breaks reviewed-artifact binding; apply the exact approved saved plan where supported.
3. **Defect and correction:** Plan success alone is not approval; review actions, unknowns and policy results.

**Rationale:** The snippet lacks layered controls for plan review, replacements, unknowns, blast radius, saved plan integrity, approval, post-apply checks; a safe correction verifies target and ownership, narrows permissions and change scope, preserves evidence, and includes a tested recovery path.

**Common wrong answers:** Fixing only syntax; treating a comment as an enforced control; assuming a green command means the operation is safe; overlooking secret exposure or cleanup.

**Safety/version note:** `[ILLUSTRATIVE]` Review exercise only; not executed. Confirm syntax and behavior for the installed versions before adapting any pattern.

### U04-INC-01 — Incident and troubleshooting

**Unit / topic:** Incident and troubleshooting  
**Level:** L4  
**Objective tested:** Respond to a unit-specific infrastructure failure with containment, blast-radius analysis, recovery and prevention.  
**Estimated time:** 15 minutes  
**Question:** Symptom: a deployment involving plan review fails part-way through. Operators disagree whether to retry or roll back. Give a structured response: symptom/evidence → diagnosis → blast-radius and rollback check → immediate fix → prevention/regression test.

**Model answer:** 1. **Contain:** pause further writes/deployments and avoid broad retries. 2. **Evidence:** capture timestamps, exact error, target identity, backend/state or controller status, plan/change record and logs with secrets redacted. 3. **Diagnose:** distinguish configuration error, authorization, provider/API failure, concurrency, partial apply and external drift. 4. **Blast radius:** enumerate changed, replaced, deleted and possibly created resources; identify stateful/data dependencies and other environments. 5. **Rollback/recovery:** verify the correct target, preserve current state/evidence, choose a tested recovery or forward-fix path; do not assume inverse apply is safe. 6. **Fix and verify:** make the smallest reviewed correction and run appropriate post-change checks. 7. **Prevent:** add a regression/negative test, target assertion, alert/runbook or policy as appropriate. Unit-specific concerns: Classify approve/reject/needs-info. Confirm target, identity, backend, resource actions, unknowns, policy results, stateful dependencies, rollback and post-apply verification. A plan is not a guarantee.

**Rationale:** The sequence prevents a second failure while preserving enough evidence to distinguish root cause from symptoms. Recovery choice depends on partial success, data semantics and tool version.

**Common wrong answers:** Blind retry; destroy/recreate before inventory; restore state without target verification; declare recovery from command exit code alone; omit a regression test.

### U04-DES-01 — Design question with scoring rubric

**Unit / topic:** Design question with scoring rubric  
**Level:** L4  
**Objective tested:** Design an operationally safe 4 approach with explicit trade-offs and evidence.  
**Estimated time:** 20 minutes  
**Question:** Design a solution for plan review, replacements, unknowns, blast radius, saved plan integrity, approval, post-apply checks. State assumptions, define boundaries and ownership, describe normal workflow and failure handling, identify security controls, and explain what evidence demonstrates success. Keep implementation local/LocalStack by default.

**Model answer:** A strong design names the authoritative owner and target; separates environments and credentials where appropriate; documents inputs, versions and limits; uses least privilege, reviewable plans/policy/tests and bounded operations; preserves recovery evidence; and defines post-change verification, alerting, rollback criteria and an exit path. Specifically: Classify approve/reject/needs-info. Confirm target, identity, backend, resource actions, unknowns, policy results, stateful dependencies, rollback and post-apply verification. A plan is not a guarantee.

**Rationale:** Production quality depends on explicit ownership, fail-safe behavior, verifiable evidence and operational recovery—not merely a successful happy path.

**Common wrong answers:** “Use best practices” without naming controls; assume the tool guarantees safety; omit a failure path; mix dev/prod ownership; provide no evidence or measurable acceptance criteria.

**Scoring rubric (20 points):**
- Correct architecture and ownership boundary — 4
- Target, identity, state and blast-radius controls — 4
- Security/policy/testing controls — 4
- Failure handling, rollback/recovery and verification — 4
- Trade-offs, evidence, version assumptions and exit path — 4

**Safety/version note:** Verify version-sensitive syntax and provider-specific semantics before implementation.


### Unit 5 — 5

**Scope and objectives:** separate account/project/subscription, identity, backend and configuration where appropriate; workspaces alone are not a security boundary; CI identity and endpoint/profile must be asserted.

### U05-SA-01 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L1  
**Objective tested:** Explain account/project/subscription isolation, CI identity, profiles, backend separation, workspace limits, boundary tests.  
**Estimated time:** 4 minutes  
**Question:** Explain the core purpose and one important limitation of account/project/subscription isolation.

**Model answer:** The authoritative boundary depends on the threat: cloud IAM/organization controls constrain API actions, backend permissions constrain state, and CI approvals constrain workflow initiation. Layer them and verify effective identity and target.

**Rationale:** A common error is to treat the mechanism as a guarantee of runtime health or safety; it only addresses the stated scope.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U05-SA-02 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L2  
**Objective tested:** Explain account/project/subscription isolation, CI identity, profiles, backend separation, workspace limits, boundary tests.  
**Estimated time:** 6 minutes  
**Question:** Identify the minimum evidence you would collect before a high-risk change involving account/project/subscription isolation, CI identity, profiles, backend separation, workspace limits, boundary tests.

**Model answer:** Collect the declared configuration, target environment and effective identity, relevant state/backend context, proposed change or status output, applicable policy/test results, ownership/dependency evidence, and a recovery/rollback assessment. The authoritative boundary depends on the threat: cloud IAM/organization controls constrain API actions, backend permissions constrain state, and CI approvals constrain workflow initiation. Layer them and verify effective identity and target.

**Rationale:** The evidence ties the intended change to the correct target and makes impact and recovery reviewable.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U05-SA-03 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L3  
**Objective tested:** Explain account/project/subscription isolation, CI identity, profiles, backend separation, workspace limits, boundary tests.  
**Estimated time:** 7 minutes  
**Question:** Describe one failure mode and one preventive control for account/project/subscription isolation, CI identity, profiles, backend separation, workspace limits, boundary tests.

**Model answer:** Failure mode: same broad role for dev and prod; workspace-only security; credentials from ambient profile; account mismatch not checked. Prevention: explicit target and ownership checks, least privilege, reviewable evidence, bounded change scope, and a tested recovery path appropriate to the tool.

**Rationale:** Prevention should interrupt the failure before mutation and provide observable evidence that the guardrail works.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U05-MCQ-01 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L1  
**Objective tested:** Choose a safe and technically accurate response for 5.  
**Estimated time:** 3 minutes  
**Question:** Which is not a reliable security boundary by itself?

A. Separate cloud account/project with distinct IAM
B. Organization-level deny boundary where available
C. Terraform workspace name alone
D. Restricted backend access

**Model answer:** **C.** Terraform workspace name alone

**Rationale:** Workspace selection does not by itself isolate credentials or cloud permissions.

**Common wrong answers / distractor analysis:** **A:** This option ignores the required safety boundary and is not supported by the evidence. **B:** This option ignores the required safety boundary and is not supported by the evidence. **C:** Correct choice. **D:** This option ignores the required safety boundary and is not supported by the evidence.

### U05-MCQ-02 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L2  
**Objective tested:** Choose a safe and technically accurate response for 5.  
**Estimated time:** 3 minutes  
**Question:** CI unexpectedly selects a production profile during a dev job. Safest response?

A. Continue if code directory says dev
B. Fail closed, record effective identity and target, and fix environment assertions
C. Use a broader role to bypass the error
D. Rename the workspace only

**Model answer:** **B.** Fail closed, record effective identity and target, and fix environment assertions

**Rationale:** Fail-closed target assertions prevent cross-environment operations.

**Common wrong answers / distractor analysis:** **A:** A trusts path alone **B:** Correct choice. **C:** C expands blast radius **D:** D is not authoritative identity isolation.

### U05-MCQ-03 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L3  
**Objective tested:** Choose a safe and technically accurate response for 5.  
**Estimated time:** 3 minutes  
**Question:** Which control most directly constrains API actions by a cloud identity?

A. A plan JSON policy alone
B. Cloud IAM and any applicable organization-level boundary
C. A local README
D. State file naming convention

**Model answer:** **B.** Cloud IAM and any applicable organization-level boundary

**Rationale:** Cloud-side identity and organization controls govern API authorization; other controls are defense in depth.

**Common wrong answers / distractor analysis:** **A:** This option ignores the required safety boundary and is not supported by the evidence. **B:** Correct choice. **C:** This option ignores the required safety boundary and is not supported by the evidence. **D:** This option ignores the required safety boundary and is not supported by the evidence.

### U05-OUT-01 — Output interpretation — initial signal

**Unit / topic:** Output interpretation — initial signal  
**Level:** L2  
**Objective tested:** Interpret an 5 signal without overclaiming.  
**Estimated time:** 7 minutes  
**Question:** [ILLUSTRATIVE] A tool run reports: `target=effective account differs from expected environment`. No additional context is provided.

Read the synthetic output. What can you infer, what remains unknown, and what is the safest next action?

**Model answer:** The output is a signal, not enough to authorize a change. Confirm the effective target and identity, collect surrounding logs/state/plan or conditions, determine whether any mutation partially succeeded, and assess affected resources and rollback before acting. Specifically for this unit: The authoritative boundary depends on the threat: cloud IAM/organization controls constrain API actions, backend permissions constrain state, and CI approvals constrain workflow initiation. Layer them and verify effective identity and target.

**Rationale:** The output identifies a risk or failure category but lacks enough context to prove full scope, root cause, or safe recovery.

**Common wrong answers:** Assuming success from a single status field; retrying immediately; taking a destructive action before target and partial-success checks.

**Safety/version note:** [ILLUSTRATIVE] Synthetic output; not executed.

### U05-OUT-02 — Output interpretation — incomplete green gate

**Unit / topic:** Output interpretation — incomplete green gate  
**Level:** L3  
**Objective tested:** Identify missing evidence for 5.  
**Estimated time:** 8 minutes  
**Question:** [ILLUSTRATIVE] A reviewer receives a green CI summary: `validate=PASS policy=PASS plan=PASS`. The artifact has no recorded target account/project, backend identifier, effective identity, or post-apply verification. The diff includes a change related to account/project/subscription isolation.

Should the reviewer approve, reject, or request more information? Explain what is and is not proven.

**Model answer:** **Needs-info / hold.** Green checks only prove the recorded checks passed against their actual inputs. Require target/backend/identity evidence, the complete reviewed diff and relevant state, plus unit-specific evidence: The authoritative boundary depends on the threat: cloud IAM/organization controls constrain API actions, backend permissions constrain state, and CI approvals constrain workflow initiation. Layer them and verify effective identity and target.

**Rationale:** A green summary is not a substitute for artifact identity, target proof, scope review, or runtime/post-change verification.

**Common wrong answers:** Approve because all statuses are green; reject without examining evidence when a hold can safely resolve uncertainty; assume the plan proves runtime behavior.

**Safety/version note:** [ILLUSTRATIVE] Synthetic output; not executed.

### U05-REV-01 — Code/config review

**Unit / topic:** Code/config review  
**Level:** L3  
**Objective tested:** Find at least three defects in a 5 workflow and propose safer corrections.  
**Estimated time:** 10 minutes  
**Question:** Review this intentionally flawed snippet. Identify at least three substantive defects, their likely impact, and a corrected pattern. Do not execute it.

```text
# Illustrative environment selection (intentionally flawed)
ENV=dev
CLOUD_PROFILE=prod-admin
terraform apply -auto-approve
# workspace name is the only environment check
# backend is shared across dev and prod
```

**Model answer:**
1. **Defect and correction:** Environment variable contradicts prod profile; assert effective identity rather than trusting label.
2. **Defect and correction:** Auto-approved apply bypasses human risk gate; use environment-appropriate approval and reviewed artifact.
3. **Defect and correction:** Workspace/shared backend alone is not a security boundary; separate backend/identity and cloud-side permissions.

**Rationale:** The snippet lacks layered controls for account/project/subscription isolation, CI identity, profiles, backend separation, workspace limits, boundary tests; a safe correction verifies target and ownership, narrows permissions and change scope, preserves evidence, and includes a tested recovery path.

**Common wrong answers:** Fixing only syntax; treating a comment as an enforced control; assuming a green command means the operation is safe; overlooking secret exposure or cleanup.

**Safety/version note:** `[ILLUSTRATIVE]` Review exercise only; not executed. Confirm syntax and behavior for the installed versions before adapting any pattern.

### U05-REV-02 — Code/config review

**Unit / topic:** Code/config review  
**Level:** L4  
**Objective tested:** Find at least three defects in a 5 workflow and propose safer corrections.  
**Estimated time:** 12 minutes  
**Question:** Review this intentionally flawed snippet. Identify at least three substantive defects, their likely impact, and a corrected pattern. Do not execute it.

```text
# Illustrative environment selection (intentionally flawed)
ENV=dev
CLOUD_PROFILE=prod-admin
terraform apply -auto-approve
# workspace name is the only environment check
# backend is shared across dev and prod
```

**Model answer:**
1. **Defect and correction:** Workspace/shared backend alone is not a security boundary; separate backend/identity and cloud-side permissions.
2. **Defect and correction:** Auto-approved apply bypasses human risk gate; use environment-appropriate approval and reviewed artifact.
3. **Defect and correction:** Environment variable contradicts prod profile; assert effective identity rather than trusting label.

**Rationale:** The snippet lacks layered controls for account/project/subscription isolation, CI identity, profiles, backend separation, workspace limits, boundary tests; a safe correction verifies target and ownership, narrows permissions and change scope, preserves evidence, and includes a tested recovery path.

**Common wrong answers:** Fixing only syntax; treating a comment as an enforced control; assuming a green command means the operation is safe; overlooking secret exposure or cleanup.

**Safety/version note:** `[ILLUSTRATIVE]` Review exercise only; not executed. Confirm syntax and behavior for the installed versions before adapting any pattern.

### U05-INC-01 — Incident and troubleshooting

**Unit / topic:** Incident and troubleshooting  
**Level:** L4  
**Objective tested:** Respond to a unit-specific infrastructure failure with containment, blast-radius analysis, recovery and prevention.  
**Estimated time:** 15 minutes  
**Question:** Symptom: a deployment involving account/project/subscription isolation fails part-way through. Operators disagree whether to retry or roll back. Give a structured response: symptom/evidence → diagnosis → blast-radius and rollback check → immediate fix → prevention/regression test.

**Model answer:** 1. **Contain:** pause further writes/deployments and avoid broad retries. 2. **Evidence:** capture timestamps, exact error, target identity, backend/state or controller status, plan/change record and logs with secrets redacted. 3. **Diagnose:** distinguish configuration error, authorization, provider/API failure, concurrency, partial apply and external drift. 4. **Blast radius:** enumerate changed, replaced, deleted and possibly created resources; identify stateful/data dependencies and other environments. 5. **Rollback/recovery:** verify the correct target, preserve current state/evidence, choose a tested recovery or forward-fix path; do not assume inverse apply is safe. 6. **Fix and verify:** make the smallest reviewed correction and run appropriate post-change checks. 7. **Prevent:** add a regression/negative test, target assertion, alert/runbook or policy as appropriate. Unit-specific concerns: The authoritative boundary depends on the threat: cloud IAM/organization controls constrain API actions, backend permissions constrain state, and CI approvals constrain workflow initiation. Layer them and verify effective identity and target.

**Rationale:** The sequence prevents a second failure while preserving enough evidence to distinguish root cause from symptoms. Recovery choice depends on partial success, data semantics and tool version.

**Common wrong answers:** Blind retry; destroy/recreate before inventory; restore state without target verification; declare recovery from command exit code alone; omit a regression test.

### U05-DES-01 — Design question with scoring rubric

**Unit / topic:** Design question with scoring rubric  
**Level:** L4  
**Objective tested:** Design an operationally safe 5 approach with explicit trade-offs and evidence.  
**Estimated time:** 20 minutes  
**Question:** Design a solution for account/project/subscription isolation, CI identity, profiles, backend separation, workspace limits, boundary tests. State assumptions, define boundaries and ownership, describe normal workflow and failure handling, identify security controls, and explain what evidence demonstrates success. Keep implementation local/LocalStack by default.

**Model answer:** A strong design names the authoritative owner and target; separates environments and credentials where appropriate; documents inputs, versions and limits; uses least privilege, reviewable plans/policy/tests and bounded operations; preserves recovery evidence; and defines post-change verification, alerting, rollback criteria and an exit path. Specifically: The authoritative boundary depends on the threat: cloud IAM/organization controls constrain API actions, backend permissions constrain state, and CI approvals constrain workflow initiation. Layer them and verify effective identity and target.

**Rationale:** Production quality depends on explicit ownership, fail-safe behavior, verifiable evidence and operational recovery—not merely a successful happy path.

**Common wrong answers:** “Use best practices” without naming controls; assume the tool guarantees safety; omit a failure path; mix dev/prod ownership; provide no evidence or measurable acceptance criteria.

**Scoring rubric (20 points):**
- Correct architecture and ownership boundary — 4
- Target, identity, state and blast-radius controls — 4
- Security/policy/testing controls — 4
- Failure handling, rollback/recovery and verification — 4
- Trade-offs, evidence, version assumptions and exit path — 4

**Safety/version note:** Verify version-sensitive syntax and provider-specific semantics before implementation.


### Unit 6 — 6

**Scope and objectives:** policy evaluates selected configuration/plan evidence; policy tests and explicit deny rules provide pre-apply guardrails; exemptions need owner, scope, expiry and evidence; policy is not IAM or runtime compliance.

### U06-SA-01 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L1  
**Objective tested:** Explain plan JSON, policy layers, deny/allow, tests, exemptions, failure modes, OPA/Rego/Conftest version checks.  
**Estimated time:** 4 minutes  
**Question:** Explain the core purpose and one important limitation of plan JSON.

**Model answer:** A passing policy means only that the evaluated inputs passed the rules actually run. It cannot replace provider IAM, organization boundaries, runtime monitoring, or proof that the plan artifact is the one applied.

**Rationale:** A common error is to treat the mechanism as a guarantee of runtime health or safety; it only addresses the stated scope.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U06-SA-02 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L2  
**Objective tested:** Explain plan JSON, policy layers, deny/allow, tests, exemptions, failure modes, OPA/Rego/Conftest version checks.  
**Estimated time:** 6 minutes  
**Question:** Identify the minimum evidence you would collect before a high-risk change involving plan JSON, policy layers, deny/allow, tests, exemptions, failure modes, OPA/Rego/Conftest version checks.

**Model answer:** Collect the declared configuration, target environment and effective identity, relevant state/backend context, proposed change or status output, applicable policy/test results, ownership/dependency evidence, and a recovery/rollback assessment. A passing policy means only that the evaluated inputs passed the rules actually run. It cannot replace provider IAM, organization boundaries, runtime monitoring, or proof that the plan artifact is the one applied.

**Rationale:** The evidence ties the intended change to the correct target and makes impact and recovery reviewable.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U06-SA-03 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L3  
**Objective tested:** Explain plan JSON, policy layers, deny/allow, tests, exemptions, failure modes, OPA/Rego/Conftest version checks.  
**Estimated time:** 7 minutes  
**Question:** Describe one failure mode and one preventive control for plan JSON, policy layers, deny/allow, tests, exemptions, failure modes, OPA/Rego/Conftest version checks.

**Model answer:** Failure mode: policy runs on source only while plan differs; fail-open on evaluator error; permanent undocumented exemption; confusing policy pass with cloud enforcement. Prevention: explicit target and ownership checks, least privilege, reviewable evidence, bounded change scope, and a tested recovery path appropriate to the tool.

**Rationale:** Prevention should interrupt the failure before mutation and provide observable evidence that the guardrail works.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U06-MCQ-01 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L1  
**Objective tested:** Choose a safe and technically accurate response for 6.  
**Estimated time:** 3 minutes  
**Question:** Policy returns pass on a plan. What does that establish?

A. The live cloud is fully compliant
B. The evaluated input passed the rules that ran
C. The provider identity cannot exceed IAM permissions
D. No later drift can occur

**Model answer:** **B.** The evaluated input passed the rules that ran

**Rationale:** Policy scope is limited to inputs, rules, and evaluation context.

**Common wrong answers / distractor analysis:** **A:** This option ignores the required safety boundary and is not supported by the evidence. **B:** Correct choice. **C:** This option ignores the required safety boundary and is not supported by the evidence. **D:** This option ignores the required safety boundary and is not supported by the evidence.

### U06-MCQ-02 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L2  
**Objective tested:** Choose a safe and technically accurate response for 6.  
**Estimated time:** 3 minutes  
**Question:** What is a safe exemption pattern?

A. Permanent wildcard exception with no owner
B. Narrow scope, reason, accountable owner, expiry/review, and evidence
C. Skip policy for production
D. Silently change the rule when it blocks a deployment

**Model answer:** **B.** Narrow scope, reason, accountable owner, expiry/review, and evidence

**Rationale:** Governed exceptions are explicit, bounded and reviewable.

**Common wrong answers / distractor analysis:** **A:** A has no lifecycle **B:** Correct choice. **C:** C removes controls at highest risk **D:** D destroys auditability.

### U06-MCQ-03 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L3  
**Objective tested:** Choose a safe and technically accurate response for 6.  
**Estimated time:** 3 minutes  
**Question:** Policy engine errors during a required gate. Best default?

A. Treat error as pass
B. Fail closed or stop for explicit controlled adjudication
C. Delete the policy file
D. Apply and check next week

**Model answer:** **B.** Fail closed or stop for explicit controlled adjudication

**Rationale:** A required control should not silently permit changes when evaluation is unavailable.

**Common wrong answers / distractor analysis:** **A:** A is fail-open **B:** Correct choice. **C:** C bypasses governance **D:** D defers risk until after mutation.

### U06-OUT-01 — Output interpretation — initial signal

**Unit / topic:** Output interpretation — initial signal  
**Level:** L2  
**Objective tested:** Interpret an 6 signal without overclaiming.  
**Estimated time:** 7 minutes  
**Question:** [ILLUSTRATIVE] A tool run reports: `target=policy evaluator returned an error`. No additional context is provided.

Read the synthetic output. What can you infer, what remains unknown, and what is the safest next action?

**Model answer:** The output is a signal, not enough to authorize a change. Confirm the effective target and identity, collect surrounding logs/state/plan or conditions, determine whether any mutation partially succeeded, and assess affected resources and rollback before acting. Specifically for this unit: A passing policy means only that the evaluated inputs passed the rules actually run. It cannot replace provider IAM, organization boundaries, runtime monitoring, or proof that the plan artifact is the one applied.

**Rationale:** The output identifies a risk or failure category but lacks enough context to prove full scope, root cause, or safe recovery.

**Common wrong answers:** Assuming success from a single status field; retrying immediately; taking a destructive action before target and partial-success checks.

**Safety/version note:** [ILLUSTRATIVE] Synthetic output; not executed.

### U06-OUT-02 — Output interpretation — incomplete green gate

**Unit / topic:** Output interpretation — incomplete green gate  
**Level:** L3  
**Objective tested:** Identify missing evidence for 6.  
**Estimated time:** 8 minutes  
**Question:** [ILLUSTRATIVE] A reviewer receives a green CI summary: `validate=PASS policy=PASS plan=PASS`. The artifact has no recorded target account/project, backend identifier, effective identity, or post-apply verification. The diff includes a change related to plan JSON.

Should the reviewer approve, reject, or request more information? Explain what is and is not proven.

**Model answer:** **Needs-info / hold.** Green checks only prove the recorded checks passed against their actual inputs. Require target/backend/identity evidence, the complete reviewed diff and relevant state, plus unit-specific evidence: A passing policy means only that the evaluated inputs passed the rules actually run. It cannot replace provider IAM, organization boundaries, runtime monitoring, or proof that the plan artifact is the one applied.

**Rationale:** A green summary is not a substitute for artifact identity, target proof, scope review, or runtime/post-change verification.

**Common wrong answers:** Approve because all statuses are green; reject without examining evidence when a hold can safely resolve uncertainty; assume the plan proves runtime behavior.

**Safety/version note:** [ILLUSTRATIVE] Synthetic output; not executed.

### U06-REV-01 — Code/config review

**Unit / topic:** Code/config review  
**Level:** L3  
**Objective tested:** Find at least three defects in a 6 workflow and propose safer corrections.  
**Estimated time:** 10 minutes  
**Question:** Review this intentionally flawed snippet. Identify at least three substantive defects, their likely impact, and a corrected pattern. Do not execute it.

```text
# Illustrative policy gate (intentionally flawed)
policy-evaluate plan.json || echo "policy unavailable; continuing"
# source-only policy result is treated as runtime proof
# exemptions have no owner or expiry
# plan artifact identity is not checked
```

**Model answer:**
1. **Defect and correction:** Evaluator failure is fail-open; stop required gate or explicit controlled adjudication.
2. **Defect and correction:** Policy pass is misrepresented as runtime proof; use IAM and post-apply monitoring/verification as separate controls.
3. **Defect and correction:** Unbounded exemptions are ungoverned; require narrow scope, owner, expiry and review evidence.

**Rationale:** The snippet lacks layered controls for plan JSON, policy layers, deny/allow, tests, exemptions, failure modes, OPA/Rego/Conftest version checks; a safe correction verifies target and ownership, narrows permissions and change scope, preserves evidence, and includes a tested recovery path.

**Common wrong answers:** Fixing only syntax; treating a comment as an enforced control; assuming a green command means the operation is safe; overlooking secret exposure or cleanup.

**Safety/version note:** `[ILLUSTRATIVE]` Review exercise only; not executed. Confirm syntax and behavior for the installed versions before adapting any pattern.

### U06-REV-02 — Code/config review

**Unit / topic:** Code/config review  
**Level:** L4  
**Objective tested:** Find at least three defects in a 6 workflow and propose safer corrections.  
**Estimated time:** 12 minutes  
**Question:** Review this intentionally flawed snippet. Identify at least three substantive defects, their likely impact, and a corrected pattern. Do not execute it.

```text
# Illustrative policy gate (intentionally flawed)
policy-evaluate plan.json || echo "policy unavailable; continuing"
# source-only policy result is treated as runtime proof
# exemptions have no owner or expiry
# plan artifact identity is not checked
```

**Model answer:**
1. **Defect and correction:** Unbounded exemptions are ungoverned; require narrow scope, owner, expiry and review evidence.
2. **Defect and correction:** Policy pass is misrepresented as runtime proof; use IAM and post-apply monitoring/verification as separate controls.
3. **Defect and correction:** Evaluator failure is fail-open; stop required gate or explicit controlled adjudication.

**Rationale:** The snippet lacks layered controls for plan JSON, policy layers, deny/allow, tests, exemptions, failure modes, OPA/Rego/Conftest version checks; a safe correction verifies target and ownership, narrows permissions and change scope, preserves evidence, and includes a tested recovery path.

**Common wrong answers:** Fixing only syntax; treating a comment as an enforced control; assuming a green command means the operation is safe; overlooking secret exposure or cleanup.

**Safety/version note:** `[ILLUSTRATIVE]` Review exercise only; not executed. Confirm syntax and behavior for the installed versions before adapting any pattern.

### U06-INC-01 — Incident and troubleshooting

**Unit / topic:** Incident and troubleshooting  
**Level:** L4  
**Objective tested:** Respond to a unit-specific infrastructure failure with containment, blast-radius analysis, recovery and prevention.  
**Estimated time:** 15 minutes  
**Question:** Symptom: a deployment involving plan JSON fails part-way through. Operators disagree whether to retry or roll back. Give a structured response: symptom/evidence → diagnosis → blast-radius and rollback check → immediate fix → prevention/regression test.

**Model answer:** 1. **Contain:** pause further writes/deployments and avoid broad retries. 2. **Evidence:** capture timestamps, exact error, target identity, backend/state or controller status, plan/change record and logs with secrets redacted. 3. **Diagnose:** distinguish configuration error, authorization, provider/API failure, concurrency, partial apply and external drift. 4. **Blast radius:** enumerate changed, replaced, deleted and possibly created resources; identify stateful/data dependencies and other environments. 5. **Rollback/recovery:** verify the correct target, preserve current state/evidence, choose a tested recovery or forward-fix path; do not assume inverse apply is safe. 6. **Fix and verify:** make the smallest reviewed correction and run appropriate post-change checks. 7. **Prevent:** add a regression/negative test, target assertion, alert/runbook or policy as appropriate. Unit-specific concerns: A passing policy means only that the evaluated inputs passed the rules actually run. It cannot replace provider IAM, organization boundaries, runtime monitoring, or proof that the plan artifact is the one applied.

**Rationale:** The sequence prevents a second failure while preserving enough evidence to distinguish root cause from symptoms. Recovery choice depends on partial success, data semantics and tool version.

**Common wrong answers:** Blind retry; destroy/recreate before inventory; restore state without target verification; declare recovery from command exit code alone; omit a regression test.

### U06-DES-01 — Design question with scoring rubric

**Unit / topic:** Design question with scoring rubric  
**Level:** L4  
**Objective tested:** Design an operationally safe 6 approach with explicit trade-offs and evidence.  
**Estimated time:** 20 minutes  
**Question:** Design a solution for plan JSON, policy layers, deny/allow, tests, exemptions, failure modes, OPA/Rego/Conftest version checks. State assumptions, define boundaries and ownership, describe normal workflow and failure handling, identify security controls, and explain what evidence demonstrates success. Keep implementation local/LocalStack by default.

**Model answer:** A strong design names the authoritative owner and target; separates environments and credentials where appropriate; documents inputs, versions and limits; uses least privilege, reviewable plans/policy/tests and bounded operations; preserves recovery evidence; and defines post-change verification, alerting, rollback criteria and an exit path. Specifically: A passing policy means only that the evaluated inputs passed the rules actually run. It cannot replace provider IAM, organization boundaries, runtime monitoring, or proof that the plan artifact is the one applied.

**Rationale:** Production quality depends on explicit ownership, fail-safe behavior, verifiable evidence and operational recovery—not merely a successful happy path.

**Common wrong answers:** “Use best practices” without naming controls; assume the tool guarantees safety; omit a failure path; mix dev/prod ownership; provide no evidence or measurable acceptance criteria.

**Scoring rubric (20 points):**
- Correct architecture and ownership boundary — 4
- Target, identity, state and blast-radius controls — 4
- Security/policy/testing controls — 4
- Failure handling, rollback/recovery and verification — 4
- Trade-offs, evidence, version assumptions and exit path — 4

**Safety/version note:** Verify version-sensitive syntax and provider-specific semantics before implementation.


### Unit 7 — 7

**Scope and objectives:** quotas and service limits differ by service/account/region and can be adjustable or hard; preflight must account for existing usage, concurrent changes and recovery headroom; never assume fixed values.

### U07-SA-01 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L1  
**Objective tested:** Explain quota versus limit, capacity/headroom, preflight, concurrency, provider errors, escalation, DR/launch planning.  
**Estimated time:** 4 minutes  
**Question:** Explain the core purpose and one important limitation of quota versus limit.

**Model answer:** Treat quota checks as time-bounded estimates: account for current usage, parallel deployments, regional/service scope, and DR/rollback capacity. Capture actual service error and escalate with evidence.

**Rationale:** A common error is to treat the mechanism as a guarantee of runtime health or safety; it only addresses the stated scope.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U07-SA-02 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L2  
**Objective tested:** Explain quota versus limit, capacity/headroom, preflight, concurrency, provider errors, escalation, DR/launch planning.  
**Estimated time:** 6 minutes  
**Question:** Identify the minimum evidence you would collect before a high-risk change involving quota versus limit, capacity/headroom, preflight, concurrency, provider errors, escalation, DR/launch planning.

**Model answer:** Collect the declared configuration, target environment and effective identity, relevant state/backend context, proposed change or status output, applicable policy/test results, ownership/dependency evidence, and a recovery/rollback assessment. Treat quota checks as time-bounded estimates: account for current usage, parallel deployments, regional/service scope, and DR/rollback capacity. Capture actual service error and escalate with evidence.

**Rationale:** The evidence ties the intended change to the correct target and makes impact and recovery reviewable.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U07-SA-03 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L3  
**Objective tested:** Explain quota versus limit, capacity/headroom, preflight, concurrency, provider errors, escalation, DR/launch planning.  
**Estimated time:** 7 minutes  
**Question:** Describe one failure mode and one preventive control for quota versus limit, capacity/headroom, preflight, concurrency, provider errors, escalation, DR/launch planning.

**Model answer:** Failure mode: invented quota values; preflight only counts planned resources; retry storm after quota error; consuming all headroom. Prevention: explicit target and ownership checks, least privilege, reviewable evidence, bounded change scope, and a tested recovery path appropriate to the tool.

**Rationale:** Prevention should interrupt the failure before mutation and provide observable evidence that the guardrail works.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U07-MCQ-01 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L1  
**Objective tested:** Choose a safe and technically accurate response for 7.  
**Estimated time:** 3 minutes  
**Question:** A quota preflight says capacity is available. What uncertainty remains?

A. None; preflight guarantees capacity
B. Concurrent deployments and intervening usage can consume headroom
C. Quota is identical in every region
D. Quota errors always retry successfully

**Model answer:** **B.** Concurrent deployments and intervening usage can consume headroom

**Rationale:** Preflight is a time-bounded estimate and must consider concurrency and scope.

**Common wrong answers / distractor analysis:** **A:** A overstates certainty **B:** Correct choice. **C:** C invents universal behavior **D:** D encourages unsafe retries.

### U07-MCQ-02 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L2  
**Objective tested:** Choose a safe and technically accurate response for 7.  
**Estimated time:** 3 minutes  
**Question:** A quota error occurs during a launch. Best response?

A. Retry at high concurrency
B. Capture exact service/account/region error, pause affected rollout, assess partial changes and escalate with evidence
C. Delete unrelated resources immediately
D. Assume the service is down globally

**Model answer:** **B.** Capture exact service/account/region error, pause affected rollout, assess partial changes and escalate with evidence

**Rationale:** Containment and precise error evidence avoid worsening the failure.

**Common wrong answers / distractor analysis:** **A:** A can amplify throttling **B:** Correct choice. **C:** C has no ownership basis **D:** D overgeneralizes.

### U07-MCQ-03 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L3  
**Objective tested:** Choose a safe and technically accurate response for 7.  
**Estimated time:** 3 minutes  
**Question:** Which is important for disaster-recovery quota planning?

A. Use all available capacity in normal operation
B. Reserve documented headroom for recovery and rollback demand
C. Use a guessed fixed quota number
D. Ignore region and service scope

**Model answer:** **B.** Reserve documented headroom for recovery and rollback demand

**Rationale:** DR and rollback can require additional capacity at the moment normal capacity is constrained.

**Common wrong answers / distractor analysis:** **A:** A leaves no headroom **B:** Correct choice. **C:** C fabricates values **D:** D ignores how limits are scoped.

### U07-OUT-01 — Output interpretation — initial signal

**Unit / topic:** Output interpretation — initial signal  
**Level:** L2  
**Objective tested:** Interpret an 7 signal without overclaiming.  
**Estimated time:** 7 minutes  
**Question:** [ILLUSTRATIVE] A tool run reports: `target=service API returned quota exceeded`. No additional context is provided.

Read the synthetic output. What can you infer, what remains unknown, and what is the safest next action?

**Model answer:** The output is a signal, not enough to authorize a change. Confirm the effective target and identity, collect surrounding logs/state/plan or conditions, determine whether any mutation partially succeeded, and assess affected resources and rollback before acting. Specifically for this unit: Treat quota checks as time-bounded estimates: account for current usage, parallel deployments, regional/service scope, and DR/rollback capacity. Capture actual service error and escalate with evidence.

**Rationale:** The output identifies a risk or failure category but lacks enough context to prove full scope, root cause, or safe recovery.

**Common wrong answers:** Assuming success from a single status field; retrying immediately; taking a destructive action before target and partial-success checks.

**Safety/version note:** [ILLUSTRATIVE] Synthetic output; not executed.

### U07-OUT-02 — Output interpretation — incomplete green gate

**Unit / topic:** Output interpretation — incomplete green gate  
**Level:** L3  
**Objective tested:** Identify missing evidence for 7.  
**Estimated time:** 8 minutes  
**Question:** [ILLUSTRATIVE] A reviewer receives a green CI summary: `validate=PASS policy=PASS plan=PASS`. The artifact has no recorded target account/project, backend identifier, effective identity, or post-apply verification. The diff includes a change related to quota versus limit.

Should the reviewer approve, reject, or request more information? Explain what is and is not proven.

**Model answer:** **Needs-info / hold.** Green checks only prove the recorded checks passed against their actual inputs. Require target/backend/identity evidence, the complete reviewed diff and relevant state, plus unit-specific evidence: Treat quota checks as time-bounded estimates: account for current usage, parallel deployments, regional/service scope, and DR/rollback capacity. Capture actual service error and escalate with evidence.

**Rationale:** A green summary is not a substitute for artifact identity, target proof, scope review, or runtime/post-change verification.

**Common wrong answers:** Approve because all statuses are green; reject without examining evidence when a hold can safely resolve uncertainty; assume the plan proves runtime behavior.

**Safety/version note:** [ILLUSTRATIVE] Synthetic output; not executed.

### U07-REV-01 — Code/config review

**Unit / topic:** Code/config review  
**Level:** L3  
**Objective tested:** Find at least three defects in a 7 workflow and propose safer corrections.  
**Estimated time:** 10 minutes  
**Question:** Review this intentionally flawed snippet. Identify at least three substantive defects, their likely impact, and a corrected pattern. Do not execute it.

```text
# Illustrative quota preflight (intentionally flawed)
if planned_count < 1000; then deploy; fi
# number is an invented universal quota
# existing usage and region are ignored
# concurrent deployments and DR headroom are ignored
```

**Model answer:**
1. **Defect and correction:** Hard-coded universal quota is fabricated and likely wrong; query/document actual service/account/region limit.
2. **Defect and correction:** Planned count ignores existing usage; calculate headroom from current usage and planned deltas.
3. **Defect and correction:** Concurrency and DR/rollback needs are ignored; reserve headroom and serialize or coordinate launches.

**Rationale:** The snippet lacks layered controls for quota versus limit, capacity/headroom, preflight, concurrency, provider errors, escalation, DR/launch planning; a safe correction verifies target and ownership, narrows permissions and change scope, preserves evidence, and includes a tested recovery path.

**Common wrong answers:** Fixing only syntax; treating a comment as an enforced control; assuming a green command means the operation is safe; overlooking secret exposure or cleanup.

**Safety/version note:** `[ILLUSTRATIVE]` Review exercise only; not executed. Confirm syntax and behavior for the installed versions before adapting any pattern.

### U07-REV-02 — Code/config review

**Unit / topic:** Code/config review  
**Level:** L4  
**Objective tested:** Find at least three defects in a 7 workflow and propose safer corrections.  
**Estimated time:** 12 minutes  
**Question:** Review this intentionally flawed snippet. Identify at least three substantive defects, their likely impact, and a corrected pattern. Do not execute it.

```text
# Illustrative quota preflight (intentionally flawed)
if planned_count < 1000; then deploy; fi
# number is an invented universal quota
# existing usage and region are ignored
# concurrent deployments and DR headroom are ignored
```

**Model answer:**
1. **Defect and correction:** Concurrency and DR/rollback needs are ignored; reserve headroom and serialize or coordinate launches.
2. **Defect and correction:** Planned count ignores existing usage; calculate headroom from current usage and planned deltas.
3. **Defect and correction:** Hard-coded universal quota is fabricated and likely wrong; query/document actual service/account/region limit.

**Rationale:** The snippet lacks layered controls for quota versus limit, capacity/headroom, preflight, concurrency, provider errors, escalation, DR/launch planning; a safe correction verifies target and ownership, narrows permissions and change scope, preserves evidence, and includes a tested recovery path.

**Common wrong answers:** Fixing only syntax; treating a comment as an enforced control; assuming a green command means the operation is safe; overlooking secret exposure or cleanup.

**Safety/version note:** `[ILLUSTRATIVE]` Review exercise only; not executed. Confirm syntax and behavior for the installed versions before adapting any pattern.

### U07-INC-01 — Incident and troubleshooting

**Unit / topic:** Incident and troubleshooting  
**Level:** L4  
**Objective tested:** Respond to a unit-specific infrastructure failure with containment, blast-radius analysis, recovery and prevention.  
**Estimated time:** 15 minutes  
**Question:** Symptom: a deployment involving quota versus limit fails part-way through. Operators disagree whether to retry or roll back. Give a structured response: symptom/evidence → diagnosis → blast-radius and rollback check → immediate fix → prevention/regression test.

**Model answer:** 1. **Contain:** pause further writes/deployments and avoid broad retries. 2. **Evidence:** capture timestamps, exact error, target identity, backend/state or controller status, plan/change record and logs with secrets redacted. 3. **Diagnose:** distinguish configuration error, authorization, provider/API failure, concurrency, partial apply and external drift. 4. **Blast radius:** enumerate changed, replaced, deleted and possibly created resources; identify stateful/data dependencies and other environments. 5. **Rollback/recovery:** verify the correct target, preserve current state/evidence, choose a tested recovery or forward-fix path; do not assume inverse apply is safe. 6. **Fix and verify:** make the smallest reviewed correction and run appropriate post-change checks. 7. **Prevent:** add a regression/negative test, target assertion, alert/runbook or policy as appropriate. Unit-specific concerns: Treat quota checks as time-bounded estimates: account for current usage, parallel deployments, regional/service scope, and DR/rollback capacity. Capture actual service error and escalate with evidence.

**Rationale:** The sequence prevents a second failure while preserving enough evidence to distinguish root cause from symptoms. Recovery choice depends on partial success, data semantics and tool version.

**Common wrong answers:** Blind retry; destroy/recreate before inventory; restore state without target verification; declare recovery from command exit code alone; omit a regression test.

### U07-DES-01 — Design question with scoring rubric

**Unit / topic:** Design question with scoring rubric  
**Level:** L4  
**Objective tested:** Design an operationally safe 7 approach with explicit trade-offs and evidence.  
**Estimated time:** 20 minutes  
**Question:** Design a solution for quota versus limit, capacity/headroom, preflight, concurrency, provider errors, escalation, DR/launch planning. State assumptions, define boundaries and ownership, describe normal workflow and failure handling, identify security controls, and explain what evidence demonstrates success. Keep implementation local/LocalStack by default.

**Model answer:** A strong design names the authoritative owner and target; separates environments and credentials where appropriate; documents inputs, versions and limits; uses least privilege, reviewable plans/policy/tests and bounded operations; preserves recovery evidence; and defines post-change verification, alerting, rollback criteria and an exit path. Specifically: Treat quota checks as time-bounded estimates: account for current usage, parallel deployments, regional/service scope, and DR/rollback capacity. Capture actual service error and escalate with evidence.

**Rationale:** Production quality depends on explicit ownership, fail-safe behavior, verifiable evidence and operational recovery—not merely a successful happy path.

**Common wrong answers:** “Use best practices” without naming controls; assume the tool guarantees safety; omit a failure path; mix dev/prod ownership; provide no evidence or measurable acceptance criteria.

**Scoring rubric (20 points):**
- Correct architecture and ownership boundary — 4
- Target, identity, state and blast-radius controls — 4
- Security/policy/testing controls — 4
- Failure handling, rollback/recovery and verification — 4
- Trade-offs, evidence, version assumptions and exit path — 4

**Safety/version note:** Verify version-sensitive syntax and provider-specific semantics before implementation.


### Unit 8 — 8

**Scope and objectives:** decommission requires ownership/inventory, retention and dependency checks, reviewed destroy plan, dry-run discovery, deletion caps, approvals, and evidence; prevent recurring leaks with TTL/tagging and accountable ownership.

### U08-SA-01 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L1  
**Objective tested:** Explain inventory, orphan discovery, retention, dependency order, cleanup dry-runs, deletion caps, approval, audit evidence.  
**Estimated time:** 4 minutes  
**Question:** Explain the core purpose and one important limitation of inventory.

**Model answer:** Do not delete based on age or a “temporary” tag alone. Verify owner, environment, dependencies, data-retention/legal holds, and plan; use a bounded batch and record before/after evidence.

**Rationale:** A common error is to treat the mechanism as a guarantee of runtime health or safety; it only addresses the stated scope.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U08-SA-02 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L2  
**Objective tested:** Explain inventory, orphan discovery, retention, dependency order, cleanup dry-runs, deletion caps, approval, audit evidence.  
**Estimated time:** 6 minutes  
**Question:** Identify the minimum evidence you would collect before a high-risk change involving inventory, orphan discovery, retention, dependency order, cleanup dry-runs, deletion caps, approval, audit evidence.

**Model answer:** Collect the declared configuration, target environment and effective identity, relevant state/backend context, proposed change or status output, applicable policy/test results, ownership/dependency evidence, and a recovery/rollback assessment. Do not delete based on age or a “temporary” tag alone. Verify owner, environment, dependencies, data-retention/legal holds, and plan; use a bounded batch and record before/after evidence.

**Rationale:** The evidence ties the intended change to the correct target and makes impact and recovery reviewable.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U08-SA-03 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L3  
**Objective tested:** Explain inventory, orphan discovery, retention, dependency order, cleanup dry-runs, deletion caps, approval, audit evidence.  
**Estimated time:** 7 minutes  
**Question:** Describe one failure mode and one preventive control for inventory, orphan discovery, retention, dependency order, cleanup dry-runs, deletion caps, approval, audit evidence.

**Model answer:** Failure mode: bulk delete on tag only; destroy before checking data retention; no deletion cap; assume untracked means unused. Prevention: explicit target and ownership checks, least privilege, reviewable evidence, bounded change scope, and a tested recovery path appropriate to the tool.

**Rationale:** Prevention should interrupt the failure before mutation and provide observable evidence that the guardrail works.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U08-MCQ-01 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L1  
**Objective tested:** Choose a safe and technically accurate response for 8.  
**Estimated time:** 3 minutes  
**Question:** A resource is tagged temporary and has no recent activity. Can the janitor delete it?

A. Yes, age and tag prove it is orphaned
B. No; verify owner, environment, dependencies, retention, and approval first
C. Yes, if deletion is scripted
D. Only if no cost is recorded

**Model answer:** **B.** No; verify owner, environment, dependencies, retention, and approval first

**Rationale:** Tags and age are discovery signals, not sufficient authorization to delete.

**Common wrong answers / distractor analysis:** **A:** This option ignores the required safety boundary and is not supported by the evidence. **B:** Correct choice. **C:** This option ignores the required safety boundary and is not supported by the evidence. **D:** This option ignores the required safety boundary and is not supported by the evidence.

### U08-MCQ-02 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L2  
**Objective tested:** Choose a safe and technically accurate response for 8.  
**Estimated time:** 3 minutes  
**Question:** What should a cleanup dry-run produce?

A. Only a delete command
B. A candidate inventory with ownership/evidence, intended actions, exclusions, and reviewable blast radius
C. A guarantee that deletion cannot fail
D. A replacement for post-delete verification

**Model answer:** **B.** A candidate inventory with ownership/evidence, intended actions, exclusions, and reviewable blast radius

**Rationale:** Dry-run evidence must make scope and rationale reviewable.

**Common wrong answers / distractor analysis:** **A:** A lacks context **B:** Correct choice. **C:** C overpromises **D:** D omits verification.

### U08-MCQ-03 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L3  
**Objective tested:** Choose a safe and technically accurate response for 8.  
**Estimated time:** 3 minutes  
**Question:** What reduces recurring orphan creation?

A. Rely on quarterly manual memory
B. Ownership/TTL tags, inventory, bounded janitors, alerts and accountable cleanup workflow
C. Delete all untagged resources immediately
D. Disable resource creation

**Model answer:** **B.** Ownership/TTL tags, inventory, bounded janitors, alerts and accountable cleanup workflow

**Rationale:** Prevention combines lifecycle metadata, discovery and governed action.

**Common wrong answers / distractor analysis:** **A:** A is unreliable **B:** Correct choice. **C:** C may delete legitimate resources **D:** D is not a proportionate governance model.

### U08-OUT-01 — Output interpretation — initial signal

**Unit / topic:** Output interpretation — initial signal  
**Level:** L2  
**Objective tested:** Interpret an 8 signal without overclaiming.  
**Estimated time:** 7 minutes  
**Question:** [ILLUSTRATIVE] A tool run reports: `target=cleanup candidate has no owner tag`. No additional context is provided.

Read the synthetic output. What can you infer, what remains unknown, and what is the safest next action?

**Model answer:** The output is a signal, not enough to authorize a change. Confirm the effective target and identity, collect surrounding logs/state/plan or conditions, determine whether any mutation partially succeeded, and assess affected resources and rollback before acting. Specifically for this unit: Do not delete based on age or a “temporary” tag alone. Verify owner, environment, dependencies, data-retention/legal holds, and plan; use a bounded batch and record before/after evidence.

**Rationale:** The output identifies a risk or failure category but lacks enough context to prove full scope, root cause, or safe recovery.

**Common wrong answers:** Assuming success from a single status field; retrying immediately; taking a destructive action before target and partial-success checks.

**Safety/version note:** [ILLUSTRATIVE] Synthetic output; not executed.

### U08-OUT-02 — Output interpretation — incomplete green gate

**Unit / topic:** Output interpretation — incomplete green gate  
**Level:** L3  
**Objective tested:** Identify missing evidence for 8.  
**Estimated time:** 8 minutes  
**Question:** [ILLUSTRATIVE] A reviewer receives a green CI summary: `validate=PASS policy=PASS plan=PASS`. The artifact has no recorded target account/project, backend identifier, effective identity, or post-apply verification. The diff includes a change related to inventory.

Should the reviewer approve, reject, or request more information? Explain what is and is not proven.

**Model answer:** **Needs-info / hold.** Green checks only prove the recorded checks passed against their actual inputs. Require target/backend/identity evidence, the complete reviewed diff and relevant state, plus unit-specific evidence: Do not delete based on age or a “temporary” tag alone. Verify owner, environment, dependencies, data-retention/legal holds, and plan; use a bounded batch and record before/after evidence.

**Rationale:** A green summary is not a substitute for artifact identity, target proof, scope review, or runtime/post-change verification.

**Common wrong answers:** Approve because all statuses are green; reject without examining evidence when a hold can safely resolve uncertainty; assume the plan proves runtime behavior.

**Safety/version note:** [ILLUSTRATIVE] Synthetic output; not executed.

### U08-REV-01 — Code/config review

**Unit / topic:** Code/config review  
**Level:** L3  
**Objective tested:** Find at least three defects in a 8 workflow and propose safer corrections.  
**Estimated time:** 10 minutes  
**Question:** Review this intentionally flawed snippet. Identify at least three substantive defects, their likely impact, and a corrected pattern. Do not execute it.

```text
# Illustrative cleanup job (intentionally flawed)
for resource in $(list-resources --tag temporary); do delete "$resource"; done
# no owner/retention/dependency check
# no dry-run or approval
# no batch cap or before/after evidence
```

**Model answer:**
1. **Defect and correction:** Tag-only deletion ignores owner, dependency and retention; verify inventory and legal/data requirements.
2. **Defect and correction:** No dry-run/approval allows unintended destructive changes; create candidate report and review.
3. **Defect and correction:** No cap/evidence increases blast radius and impairs audit; bounded batches with stop conditions and before/after records.

**Rationale:** The snippet lacks layered controls for inventory, orphan discovery, retention, dependency order, cleanup dry-runs, deletion caps, approval, audit evidence; a safe correction verifies target and ownership, narrows permissions and change scope, preserves evidence, and includes a tested recovery path.

**Common wrong answers:** Fixing only syntax; treating a comment as an enforced control; assuming a green command means the operation is safe; overlooking secret exposure or cleanup.

**Safety/version note:** `[ILLUSTRATIVE]` Review exercise only; not executed. Confirm syntax and behavior for the installed versions before adapting any pattern.

### U08-REV-02 — Code/config review

**Unit / topic:** Code/config review  
**Level:** L4  
**Objective tested:** Find at least three defects in a 8 workflow and propose safer corrections.  
**Estimated time:** 12 minutes  
**Question:** Review this intentionally flawed snippet. Identify at least three substantive defects, their likely impact, and a corrected pattern. Do not execute it.

```text
# Illustrative cleanup job (intentionally flawed)
for resource in $(list-resources --tag temporary); do delete "$resource"; done
# no owner/retention/dependency check
# no dry-run or approval
# no batch cap or before/after evidence
```

**Model answer:**
1. **Defect and correction:** No cap/evidence increases blast radius and impairs audit; bounded batches with stop conditions and before/after records.
2. **Defect and correction:** No dry-run/approval allows unintended destructive changes; create candidate report and review.
3. **Defect and correction:** Tag-only deletion ignores owner, dependency and retention; verify inventory and legal/data requirements.

**Rationale:** The snippet lacks layered controls for inventory, orphan discovery, retention, dependency order, cleanup dry-runs, deletion caps, approval, audit evidence; a safe correction verifies target and ownership, narrows permissions and change scope, preserves evidence, and includes a tested recovery path.

**Common wrong answers:** Fixing only syntax; treating a comment as an enforced control; assuming a green command means the operation is safe; overlooking secret exposure or cleanup.

**Safety/version note:** `[ILLUSTRATIVE]` Review exercise only; not executed. Confirm syntax and behavior for the installed versions before adapting any pattern.

### U08-INC-01 — Incident and troubleshooting

**Unit / topic:** Incident and troubleshooting  
**Level:** L4  
**Objective tested:** Respond to a unit-specific infrastructure failure with containment, blast-radius analysis, recovery and prevention.  
**Estimated time:** 15 minutes  
**Question:** Symptom: a deployment involving inventory fails part-way through. Operators disagree whether to retry or roll back. Give a structured response: symptom/evidence → diagnosis → blast-radius and rollback check → immediate fix → prevention/regression test.

**Model answer:** 1. **Contain:** pause further writes/deployments and avoid broad retries. 2. **Evidence:** capture timestamps, exact error, target identity, backend/state or controller status, plan/change record and logs with secrets redacted. 3. **Diagnose:** distinguish configuration error, authorization, provider/API failure, concurrency, partial apply and external drift. 4. **Blast radius:** enumerate changed, replaced, deleted and possibly created resources; identify stateful/data dependencies and other environments. 5. **Rollback/recovery:** verify the correct target, preserve current state/evidence, choose a tested recovery or forward-fix path; do not assume inverse apply is safe. 6. **Fix and verify:** make the smallest reviewed correction and run appropriate post-change checks. 7. **Prevent:** add a regression/negative test, target assertion, alert/runbook or policy as appropriate. Unit-specific concerns: Do not delete based on age or a “temporary” tag alone. Verify owner, environment, dependencies, data-retention/legal holds, and plan; use a bounded batch and record before/after evidence.

**Rationale:** The sequence prevents a second failure while preserving enough evidence to distinguish root cause from symptoms. Recovery choice depends on partial success, data semantics and tool version.

**Common wrong answers:** Blind retry; destroy/recreate before inventory; restore state without target verification; declare recovery from command exit code alone; omit a regression test.

### U08-DES-01 — Design question with scoring rubric

**Unit / topic:** Design question with scoring rubric  
**Level:** L4  
**Objective tested:** Design an operationally safe 8 approach with explicit trade-offs and evidence.  
**Estimated time:** 20 minutes  
**Question:** Design a solution for inventory, orphan discovery, retention, dependency order, cleanup dry-runs, deletion caps, approval, audit evidence. State assumptions, define boundaries and ownership, describe normal workflow and failure handling, identify security controls, and explain what evidence demonstrates success. Keep implementation local/LocalStack by default.

**Model answer:** A strong design names the authoritative owner and target; separates environments and credentials where appropriate; documents inputs, versions and limits; uses least privilege, reviewable plans/policy/tests and bounded operations; preserves recovery evidence; and defines post-change verification, alerting, rollback criteria and an exit path. Specifically: Do not delete based on age or a “temporary” tag alone. Verify owner, environment, dependencies, data-retention/legal holds, and plan; use a bounded batch and record before/after evidence.

**Rationale:** Production quality depends on explicit ownership, fail-safe behavior, verifiable evidence and operational recovery—not merely a successful happy path.

**Common wrong answers:** “Use best practices” without naming controls; assume the tool guarantees safety; omit a failure path; mix dev/prod ownership; provide no evidence or measurable acceptance criteria.

**Scoring rubric (20 points):**
- Correct architecture and ownership boundary — 4
- Target, identity, state and blast-radius controls — 4
- Security/policy/testing controls — 4
- Failure handling, rollback/recovery and verification — 4
- Trade-offs, evidence, version assumptions and exit path — 4

**Safety/version note:** Verify version-sensitive syntax and provider-specific semantics before implementation.


### Unit 9 — 9

**Scope and objectives:** tool choice weighs workflow, state/plan semantics, language, reuse, ecosystem, migration and governance; similar concepts do not guarantee interchangeable syntax, state, providers or operational behavior.

### U09-SA-01 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L1  
**Objective tested:** Explain tool comparison, reuse, migration costs, state semantics, version verification, team skills, ecosystem governance.  
**Estimated time:** 4 minutes  
**Question:** Explain the core purpose and one important limitation of tool comparison.

**Model answer:** Choose against requirements and migration cost, not syntax preference alone. Inventory state, providers, policy/test pipeline, team skills and exit path; verify each tool/version’s semantics before conversion.

**Rationale:** A common error is to treat the mechanism as a guarantee of runtime health or safety; it only addresses the stated scope.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U09-SA-02 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L2  
**Objective tested:** Explain tool comparison, reuse, migration costs, state semantics, version verification, team skills, ecosystem governance.  
**Estimated time:** 6 minutes  
**Question:** Identify the minimum evidence you would collect before a high-risk change involving tool comparison, reuse, migration costs, state semantics, version verification, team skills, ecosystem governance.

**Model answer:** Collect the declared configuration, target environment and effective identity, relevant state/backend context, proposed change or status output, applicable policy/test results, ownership/dependency evidence, and a recovery/rollback assessment. Choose against requirements and migration cost, not syntax preference alone. Inventory state, providers, policy/test pipeline, team skills and exit path; verify each tool/version’s semantics before conversion.

**Rationale:** The evidence ties the intended change to the correct target and makes impact and recovery reviewable.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U09-SA-03 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L3  
**Objective tested:** Explain tool comparison, reuse, migration costs, state semantics, version verification, team skills, ecosystem governance.  
**Estimated time:** 7 minutes  
**Question:** Describe one failure mode and one preventive control for tool comparison, reuse, migration costs, state semantics, version verification, team skills, ecosystem governance.

**Model answer:** Failure mode: assuming drop-in compatibility; migrating without state inventory; selecting solely by language; mixing ownership without explicit boundary. Prevention: explicit target and ownership checks, least privilege, reviewable evidence, bounded change scope, and a tested recovery path appropriate to the tool.

**Rationale:** Prevention should interrupt the failure before mutation and provide observable evidence that the guardrail works.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U09-MCQ-01 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L1  
**Objective tested:** Choose a safe and technically accurate response for 9.  
**Estimated time:** 3 minutes  
**Question:** What is the safest tool migration assumption?

A. State and syntax are interchangeable
B. Semantics, state formats, providers and workflows must be inventoried and verified
C. Only the HCL files matter
D. A new tool removes the need for tests

**Model answer:** **B.** Semantics, state formats, providers and workflows must be inventoried and verified

**Rationale:** Tool changes are operational migrations with compatibility and exit costs.

**Common wrong answers / distractor analysis:** **A:** This option ignores the required safety boundary and is not supported by the evidence. **B:** Correct choice. **C:** This option ignores the required safety boundary and is not supported by the evidence. **D:** This option ignores the required safety boundary and is not supported by the evidence.

### U09-MCQ-02 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L2  
**Objective tested:** Choose a safe and technically accurate response for 9.  
**Estimated time:** 3 minutes  
**Question:** How should Terraform/OpenTofu/Pulumi be compared?

A. Choose the newest tool automatically
B. Compare requirements, state/workflow, language, ecosystem, skills, governance and migration costs
C. Pick the shortest syntax only
D. Use all three to manage the same object

**Model answer:** **B.** Compare requirements, state/workflow, language, ecosystem, skills, governance and migration costs

**Rationale:** Selection is a multi-dimensional platform decision.

**Common wrong answers / distractor analysis:** **A:** A is arbitrary **B:** Correct choice. **C:** C optimizes one factor **D:** D creates ownership conflicts unless carefully partitioned.

### U09-MCQ-03 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L3  
**Objective tested:** Choose a safe and technically accurate response for 9.  
**Estimated time:** 3 minutes  
**Question:** A team wants to reuse existing Terraform state in another tool. Best response?

A. Convert directly in production
B. Build a migration inventory, test a disposable copy, verify supported paths and recovery/rollback
C. Delete old state after file conversion
D. Assume provider resources map identically

**Model answer:** **B.** Build a migration inventory, test a disposable copy, verify supported paths and recovery/rollback

**Rationale:** State migration needs a tested and reversible plan.

**Common wrong answers / distractor analysis:** **A:** A is unsafe **B:** Correct choice. **C:** C destroys recovery **D:** D assumes compatibility without evidence.

### U09-OUT-01 — Output interpretation — initial signal

**Unit / topic:** Output interpretation — initial signal  
**Level:** L2  
**Objective tested:** Interpret an 9 signal without overclaiming.  
**Estimated time:** 7 minutes  
**Question:** [ILLUSTRATIVE] A tool run reports: `target=new tool reports unsupported state feature`. No additional context is provided.

Read the synthetic output. What can you infer, what remains unknown, and what is the safest next action?

**Model answer:** The output is a signal, not enough to authorize a change. Confirm the effective target and identity, collect surrounding logs/state/plan or conditions, determine whether any mutation partially succeeded, and assess affected resources and rollback before acting. Specifically for this unit: Choose against requirements and migration cost, not syntax preference alone. Inventory state, providers, policy/test pipeline, team skills and exit path; verify each tool/version’s semantics before conversion.

**Rationale:** The output identifies a risk or failure category but lacks enough context to prove full scope, root cause, or safe recovery.

**Common wrong answers:** Assuming success from a single status field; retrying immediately; taking a destructive action before target and partial-success checks.

**Safety/version note:** [ILLUSTRATIVE] Synthetic output; not executed.

### U09-OUT-02 — Output interpretation — incomplete green gate

**Unit / topic:** Output interpretation — incomplete green gate  
**Level:** L3  
**Objective tested:** Identify missing evidence for 9.  
**Estimated time:** 8 minutes  
**Question:** [ILLUSTRATIVE] A reviewer receives a green CI summary: `validate=PASS policy=PASS plan=PASS`. The artifact has no recorded target account/project, backend identifier, effective identity, or post-apply verification. The diff includes a change related to tool comparison.

Should the reviewer approve, reject, or request more information? Explain what is and is not proven.

**Model answer:** **Needs-info / hold.** Green checks only prove the recorded checks passed against their actual inputs. Require target/backend/identity evidence, the complete reviewed diff and relevant state, plus unit-specific evidence: Choose against requirements and migration cost, not syntax preference alone. Inventory state, providers, policy/test pipeline, team skills and exit path; verify each tool/version’s semantics before conversion.

**Rationale:** A green summary is not a substitute for artifact identity, target proof, scope review, or runtime/post-change verification.

**Common wrong answers:** Approve because all statuses are green; reject without examining evidence when a hold can safely resolve uncertainty; assume the plan proves runtime behavior.

**Safety/version note:** [ILLUSTRATIVE] Synthetic output; not executed.

### U09-REV-01 — Code/config review

**Unit / topic:** Code/config review  
**Level:** L3  
**Objective tested:** Find at least three defects in a 9 workflow and propose safer corrections.  
**Estimated time:** 10 minutes  
**Question:** Review this intentionally flawed snippet. Identify at least three substantive defects, their likely impact, and a corrected pattern. Do not execute it.

```text
# Illustrative tool migration (intentionally flawed)
convert-state --source terraform --target other-tool
apply
# no tool/provider version inventory
# no disposable rehearsal or backup
# old tool continues managing the same objects
```

**Model answer:**
1. **Defect and correction:** Conversion syntax/semantics are not universal; verify supported version-specific migration path.
2. **Defect and correction:** No backup/rehearsal makes migration irreversible; test disposable copy and recovery.
3. **Defect and correction:** Dual ownership risks conflicting updates; define cutover and disable old owner only after verified transfer.

**Rationale:** The snippet lacks layered controls for tool comparison, reuse, migration costs, state semantics, version verification, team skills, ecosystem governance; a safe correction verifies target and ownership, narrows permissions and change scope, preserves evidence, and includes a tested recovery path.

**Common wrong answers:** Fixing only syntax; treating a comment as an enforced control; assuming a green command means the operation is safe; overlooking secret exposure or cleanup.

**Safety/version note:** `[ILLUSTRATIVE]` Review exercise only; not executed. Confirm syntax and behavior for the installed versions before adapting any pattern.

### U09-REV-02 — Code/config review

**Unit / topic:** Code/config review  
**Level:** L4  
**Objective tested:** Find at least three defects in a 9 workflow and propose safer corrections.  
**Estimated time:** 12 minutes  
**Question:** Review this intentionally flawed snippet. Identify at least three substantive defects, their likely impact, and a corrected pattern. Do not execute it.

```text
# Illustrative tool migration (intentionally flawed)
convert-state --source terraform --target other-tool
apply
# no tool/provider version inventory
# no disposable rehearsal or backup
# old tool continues managing the same objects
```

**Model answer:**
1. **Defect and correction:** Dual ownership risks conflicting updates; define cutover and disable old owner only after verified transfer.
2. **Defect and correction:** No backup/rehearsal makes migration irreversible; test disposable copy and recovery.
3. **Defect and correction:** Conversion syntax/semantics are not universal; verify supported version-specific migration path.

**Rationale:** The snippet lacks layered controls for tool comparison, reuse, migration costs, state semantics, version verification, team skills, ecosystem governance; a safe correction verifies target and ownership, narrows permissions and change scope, preserves evidence, and includes a tested recovery path.

**Common wrong answers:** Fixing only syntax; treating a comment as an enforced control; assuming a green command means the operation is safe; overlooking secret exposure or cleanup.

**Safety/version note:** `[ILLUSTRATIVE]` Review exercise only; not executed. Confirm syntax and behavior for the installed versions before adapting any pattern.

### U09-INC-01 — Incident and troubleshooting

**Unit / topic:** Incident and troubleshooting  
**Level:** L4  
**Objective tested:** Respond to a unit-specific infrastructure failure with containment, blast-radius analysis, recovery and prevention.  
**Estimated time:** 15 minutes  
**Question:** Symptom: a deployment involving tool comparison fails part-way through. Operators disagree whether to retry or roll back. Give a structured response: symptom/evidence → diagnosis → blast-radius and rollback check → immediate fix → prevention/regression test.

**Model answer:** 1. **Contain:** pause further writes/deployments and avoid broad retries. 2. **Evidence:** capture timestamps, exact error, target identity, backend/state or controller status, plan/change record and logs with secrets redacted. 3. **Diagnose:** distinguish configuration error, authorization, provider/API failure, concurrency, partial apply and external drift. 4. **Blast radius:** enumerate changed, replaced, deleted and possibly created resources; identify stateful/data dependencies and other environments. 5. **Rollback/recovery:** verify the correct target, preserve current state/evidence, choose a tested recovery or forward-fix path; do not assume inverse apply is safe. 6. **Fix and verify:** make the smallest reviewed correction and run appropriate post-change checks. 7. **Prevent:** add a regression/negative test, target assertion, alert/runbook or policy as appropriate. Unit-specific concerns: Choose against requirements and migration cost, not syntax preference alone. Inventory state, providers, policy/test pipeline, team skills and exit path; verify each tool/version’s semantics before conversion.

**Rationale:** The sequence prevents a second failure while preserving enough evidence to distinguish root cause from symptoms. Recovery choice depends on partial success, data semantics and tool version.

**Common wrong answers:** Blind retry; destroy/recreate before inventory; restore state without target verification; declare recovery from command exit code alone; omit a regression test.

### U09-DES-01 — Design question with scoring rubric

**Unit / topic:** Design question with scoring rubric  
**Level:** L4  
**Objective tested:** Design an operationally safe 9 approach with explicit trade-offs and evidence.  
**Estimated time:** 20 minutes  
**Question:** Design a solution for tool comparison, reuse, migration costs, state semantics, version verification, team skills, ecosystem governance. State assumptions, define boundaries and ownership, describe normal workflow and failure handling, identify security controls, and explain what evidence demonstrates success. Keep implementation local/LocalStack by default.

**Model answer:** A strong design names the authoritative owner and target; separates environments and credentials where appropriate; documents inputs, versions and limits; uses least privilege, reviewable plans/policy/tests and bounded operations; preserves recovery evidence; and defines post-change verification, alerting, rollback criteria and an exit path. Specifically: Choose against requirements and migration cost, not syntax preference alone. Inventory state, providers, policy/test pipeline, team skills and exit path; verify each tool/version’s semantics before conversion.

**Rationale:** Production quality depends on explicit ownership, fail-safe behavior, verifiable evidence and operational recovery—not merely a successful happy path.

**Common wrong answers:** “Use best practices” without naming controls; assume the tool guarantees safety; omit a failure path; mix dev/prod ownership; provide no evidence or measurable acceptance criteria.

**Scoring rubric (20 points):**
- Correct architecture and ownership boundary — 4
- Target, identity, state and blast-radius controls — 4
- Security/policy/testing controls — 4
- Failure handling, rollback/recovery and verification — 4
- Trade-offs, evidence, version assumptions and exit path — 4

**Safety/version note:** Verify version-sensitive syntax and provider-specific semantics before implementation.


### Unit 10 — 10

**Scope and objectives:** inventory selects targets; playbooks should converge idempotently; use modules and handlers; command/shell need change guards; secrets need Vault/no_log with limits; preserve host-key verification, least privilege and rolling controls.

### U10-SA-01 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L1  
**Objective tested:** Explain inventory, idempotency, modules/roles, handlers, command vs shell, changed_when/creates, precedence, Vault/no_log, become, host keys, serial/check-mode limits.  
**Estimated time:** 4 minutes  
**Question:** Explain the core purpose and one important limitation of inventory.

**Model answer:** Verify inventory, target count, privilege escalation, secret handling, and rollout controls before execution. Check mode is not proof that every module predicts changes accurately. Prefer modules and bounded serial batches.

**Rationale:** A common error is to treat the mechanism as a guarantee of runtime health or safety; it only addresses the stated scope.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U10-SA-02 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L2  
**Objective tested:** Explain inventory, idempotency, modules/roles, handlers, command vs shell, changed_when/creates, precedence, Vault/no_log, become, host keys, serial/check-mode limits.  
**Estimated time:** 6 minutes  
**Question:** Identify the minimum evidence you would collect before a high-risk change involving inventory, idempotency, modules/roles, handlers, command vs shell, changed_when/creates, precedence, Vault/no_log, become, host keys, serial/check-mode limits.

**Model answer:** Collect the declared configuration, target environment and effective identity, relevant state/backend context, proposed change or status output, applicable policy/test results, ownership/dependency evidence, and a recovery/rollback assessment. Verify inventory, target count, privilege escalation, secret handling, and rollout controls before execution. Check mode is not proof that every module predicts changes accurately. Prefer modules and bounded serial batches.

**Rationale:** The evidence ties the intended change to the correct target and makes impact and recovery reviewable.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U10-SA-03 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L3  
**Objective tested:** Explain inventory, idempotency, modules/roles, handlers, command vs shell, changed_when/creates, precedence, Vault/no_log, become, host keys, serial/check-mode limits.  
**Estimated time:** 7 minutes  
**Question:** Describe one failure mode and one preventive control for inventory, idempotency, modules/roles, handlers, command vs shell, changed_when/creates, precedence, Vault/no_log, become, host keys, serial/check-mode limits.

**Model answer:** Failure mode: disable host-key checking; broad sudo; secrets printed in output; non-idempotent shell; assume check mode is authoritative. Prevention: explicit target and ownership checks, least privilege, reviewable evidence, bounded change scope, and a tested recovery path appropriate to the tool.

**Rationale:** Prevention should interrupt the failure before mutation and provide observable evidence that the guardrail works.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U10-MCQ-01 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L1  
**Objective tested:** Choose a safe and technically accurate response for 10.  
**Estimated time:** 3 minutes  
**Question:** Why prefer an Ansible module over an unguarded shell command when available?

A. Modules always succeed
B. Modules usually expose desired-state semantics and improve idempotency/reporting
C. Shell cannot run commands
D. Modules remove need to verify targets

**Model answer:** **B.** Modules usually expose desired-state semantics and improve idempotency/reporting

**Rationale:** Modules often provide better convergence and change reporting, though module behavior still must be checked.

**Common wrong answers / distractor analysis:** **A:** A overstates reliability **B:** Correct choice. **C:** C is false **D:** D ignores inventory and target risk.

### U10-MCQ-02 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L2  
**Objective tested:** Choose a safe and technically accurate response for 10.  
**Estimated time:** 3 minutes  
**Question:** What does `no_log` do and not do?

A. Guarantees no secret exists anywhere
B. Suppresses selected task output but does not erase secrets from inputs, controller memory, other logs or external systems
C. Encrypts inventory
D. Rotates a leaked credential

**Model answer:** **B.** Suppresses selected task output but does not erase secrets from inputs, controller memory, other logs or external systems

**Rationale:** Output suppression is limited; secret lifecycle and access control remain necessary.

**Common wrong answers / distractor analysis:** **A:** A overstates scope **B:** Correct choice. **C:** C is unrelated **D:** D is a separate incident-response action.

### U10-MCQ-03 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L3  
**Objective tested:** Choose a safe and technically accurate response for 10.  
**Estimated time:** 3 minutes  
**Question:** Before a rolling production configuration change, what matters most?

A. Disable host key checking to reduce failures
B. Verify inventory/host identity, privilege scope, batch size, health checks and rollback
C. Use `--limit all` without inspection
D. Assume check mode exactly predicts all changes

**Model answer:** **B.** Verify inventory/host identity, privilege scope, batch size, health checks and rollback

**Rationale:** Target validation and bounded rollout protect against broad unintended change.

**Common wrong answers / distractor analysis:** **A:** A weakens authenticity **B:** Correct choice. **C:** C expands blast radius **D:** D overstates check-mode fidelity.

### U10-OUT-01 — Output interpretation — initial signal

**Unit / topic:** Output interpretation — initial signal  
**Level:** L2  
**Objective tested:** Interpret an 10 signal without overclaiming.  
**Estimated time:** 7 minutes  
**Question:** [ILLUSTRATIVE] A tool run reports: `target=Ansible recap: changed=18 failed=0 unreachable=0`. No additional context is provided.

Read the synthetic output. What can you infer, what remains unknown, and what is the safest next action?

**Model answer:** The output is a signal, not enough to authorize a change. Confirm the effective target and identity, collect surrounding logs/state/plan or conditions, determine whether any mutation partially succeeded, and assess affected resources and rollback before acting. Specifically for this unit: Verify inventory, target count, privilege escalation, secret handling, and rollout controls before execution. Check mode is not proof that every module predicts changes accurately. Prefer modules and bounded serial batches.

**Rationale:** The output identifies a risk or failure category but lacks enough context to prove full scope, root cause, or safe recovery.

**Common wrong answers:** Assuming success from a single status field; retrying immediately; taking a destructive action before target and partial-success checks.

**Safety/version note:** [ILLUSTRATIVE] Synthetic output; not executed.

### U10-OUT-02 — Output interpretation — incomplete green gate

**Unit / topic:** Output interpretation — incomplete green gate  
**Level:** L3  
**Objective tested:** Identify missing evidence for 10.  
**Estimated time:** 8 minutes  
**Question:** [ILLUSTRATIVE] A reviewer receives a green CI summary: `validate=PASS policy=PASS plan=PASS`. The artifact has no recorded target account/project, backend identifier, effective identity, or post-apply verification. The diff includes a change related to inventory.

Should the reviewer approve, reject, or request more information? Explain what is and is not proven.

**Model answer:** **Needs-info / hold.** Green checks only prove the recorded checks passed against their actual inputs. Require target/backend/identity evidence, the complete reviewed diff and relevant state, plus unit-specific evidence: Verify inventory, target count, privilege escalation, secret handling, and rollout controls before execution. Check mode is not proof that every module predicts changes accurately. Prefer modules and bounded serial batches.

**Rationale:** A green summary is not a substitute for artifact identity, target proof, scope review, or runtime/post-change verification.

**Common wrong answers:** Approve because all statuses are green; reject without examining evidence when a hold can safely resolve uncertainty; assume the plan proves runtime behavior.

**Safety/version note:** [ILLUSTRATIVE] Synthetic output; not executed.

### U10-REV-01 — Code/config review

**Unit / topic:** Code/config review  
**Level:** L3  
**Objective tested:** Find at least three defects in a 10 workflow and propose safer corrections.  
**Estimated time:** 10 minutes  
**Question:** Review this intentionally flawed snippet. Identify at least three substantive defects, their likely impact, and a corrected pattern. Do not execute it.

```text
# Illustrative Ansible play (intentionally flawed)
- hosts: all
  become: true
  tasks:
    - shell: "rotate_secret {{ secret_value }}"
    - debug: var=secret_value
# host-key checking disabled in ansible.cfg
# no serial or health gate
```

**Model answer:**
1. **Defect and correction:** Shell command may be non-idempotent and secret interpolation can leak; prefer appropriate module/guarded task and secret-safe handling.
2. **Defect and correction:** Debug prints secret; remove and rotate if exposed, restrict logs/artifacts, use `no_log` where appropriate with known limits.
3. **Defect and correction:** Host-key checking disabled weakens server authenticity; retain verification and use bounded `serial` plus health/rollback gates.

**Rationale:** The snippet lacks layered controls for inventory, idempotency, modules/roles, handlers, command vs shell, changed_when/creates, precedence, Vault/no_log, become, host keys, serial/check-mode limits; a safe correction verifies target and ownership, narrows permissions and change scope, preserves evidence, and includes a tested recovery path.

**Common wrong answers:** Fixing only syntax; treating a comment as an enforced control; assuming a green command means the operation is safe; overlooking secret exposure or cleanup.

**Safety/version note:** `[ILLUSTRATIVE]` Review exercise only; not executed. Confirm syntax and behavior for the installed versions before adapting any pattern.

### U10-REV-02 — Code/config review

**Unit / topic:** Code/config review  
**Level:** L4  
**Objective tested:** Find at least three defects in a 10 workflow and propose safer corrections.  
**Estimated time:** 12 minutes  
**Question:** Review this intentionally flawed snippet. Identify at least three substantive defects, their likely impact, and a corrected pattern. Do not execute it.

```text
# Illustrative Ansible play (intentionally flawed)
- hosts: all
  become: true
  tasks:
    - shell: "rotate_secret {{ secret_value }}"
    - debug: var=secret_value
# host-key checking disabled in ansible.cfg
# no serial or health gate
```

**Model answer:**
1. **Defect and correction:** Host-key checking disabled weakens server authenticity; retain verification and use bounded `serial` plus health/rollback gates.
2. **Defect and correction:** Debug prints secret; remove and rotate if exposed, restrict logs/artifacts, use `no_log` where appropriate with known limits.
3. **Defect and correction:** Shell command may be non-idempotent and secret interpolation can leak; prefer appropriate module/guarded task and secret-safe handling.

**Rationale:** The snippet lacks layered controls for inventory, idempotency, modules/roles, handlers, command vs shell, changed_when/creates, precedence, Vault/no_log, become, host keys, serial/check-mode limits; a safe correction verifies target and ownership, narrows permissions and change scope, preserves evidence, and includes a tested recovery path.

**Common wrong answers:** Fixing only syntax; treating a comment as an enforced control; assuming a green command means the operation is safe; overlooking secret exposure or cleanup.

**Safety/version note:** `[ILLUSTRATIVE]` Review exercise only; not executed. Confirm syntax and behavior for the installed versions before adapting any pattern.

### U10-INC-01 — Incident and troubleshooting

**Unit / topic:** Incident and troubleshooting  
**Level:** L4  
**Objective tested:** Respond to a unit-specific infrastructure failure with containment, blast-radius analysis, recovery and prevention.  
**Estimated time:** 15 minutes  
**Question:** Symptom: a deployment involving inventory fails part-way through. Operators disagree whether to retry or roll back. Give a structured response: symptom/evidence → diagnosis → blast-radius and rollback check → immediate fix → prevention/regression test.

**Model answer:** 1. **Contain:** pause further writes/deployments and avoid broad retries. 2. **Evidence:** capture timestamps, exact error, target identity, backend/state or controller status, plan/change record and logs with secrets redacted. 3. **Diagnose:** distinguish configuration error, authorization, provider/API failure, concurrency, partial apply and external drift. 4. **Blast radius:** enumerate changed, replaced, deleted and possibly created resources; identify stateful/data dependencies and other environments. 5. **Rollback/recovery:** verify the correct target, preserve current state/evidence, choose a tested recovery or forward-fix path; do not assume inverse apply is safe. 6. **Fix and verify:** make the smallest reviewed correction and run appropriate post-change checks. 7. **Prevent:** add a regression/negative test, target assertion, alert/runbook or policy as appropriate. Unit-specific concerns: Verify inventory, target count, privilege escalation, secret handling, and rollout controls before execution. Check mode is not proof that every module predicts changes accurately. Prefer modules and bounded serial batches.

**Rationale:** The sequence prevents a second failure while preserving enough evidence to distinguish root cause from symptoms. Recovery choice depends on partial success, data semantics and tool version.

**Common wrong answers:** Blind retry; destroy/recreate before inventory; restore state without target verification; declare recovery from command exit code alone; omit a regression test.

### U10-DES-01 — Design question with scoring rubric

**Unit / topic:** Design question with scoring rubric  
**Level:** L4  
**Objective tested:** Design an operationally safe 10 approach with explicit trade-offs and evidence.  
**Estimated time:** 20 minutes  
**Question:** Design a solution for inventory, idempotency, modules/roles, handlers, command vs shell, changed_when/creates, precedence, Vault/no_log, become, host keys, serial/check-mode limits. State assumptions, define boundaries and ownership, describe normal workflow and failure handling, identify security controls, and explain what evidence demonstrates success. Keep implementation local/LocalStack by default.

**Model answer:** A strong design names the authoritative owner and target; separates environments and credentials where appropriate; documents inputs, versions and limits; uses least privilege, reviewable plans/policy/tests and bounded operations; preserves recovery evidence; and defines post-change verification, alerting, rollback criteria and an exit path. Specifically: Verify inventory, target count, privilege escalation, secret handling, and rollout controls before execution. Check mode is not proof that every module predicts changes accurately. Prefer modules and bounded serial batches.

**Rationale:** Production quality depends on explicit ownership, fail-safe behavior, verifiable evidence and operational recovery—not merely a successful happy path.

**Common wrong answers:** “Use best practices” without naming controls; assume the tool guarantees safety; omit a failure path; mix dev/prod ownership; provide no evidence or measurable acceptance criteria.

**Scoring rubric (20 points):**
- Correct architecture and ownership boundary — 4
- Target, identity, state and blast-radius controls — 4
- Security/policy/testing controls — 4
- Failure handling, rollback/recovery and verification — 4
- Trade-offs, evidence, version assumptions and exit path — 4

**Safety/version note:** Verify version-sensitive syntax and provider-specific semantics before implementation.


### Unit 11 — 11

**Scope and objectives:** use a testing pyramid: formatting/static validation, native tests, policy/plan assertions, mocks where supported, emulator tests with fidelity limits, integration/Terratest, post-apply checks; cleanup is a risk-bearing operation.

### U11-SA-01 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L1  
**Objective tested:** Explain native tests, positive/negative/idempotency tests, plan JSON, mocks [VERIFY], LocalStack fidelity, Go/Terratest, retries/timeouts, contract/upgrade/drift tests, janitors.  
**Estimated time:** 4 minutes  
**Question:** Explain the core purpose and one important limitation of native tests.

**Model answer:** Match test type to the claim: static checks do not prove cloud behavior; emulator success does not prove real IAM/quota parity; integration tests require isolated targets, bounded retries, and reliable cleanup.

**Rationale:** A common error is to treat the mechanism as a guarantee of runtime health or safety; it only addresses the stated scope.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U11-SA-02 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L2  
**Objective tested:** Explain native tests, positive/negative/idempotency tests, plan JSON, mocks [VERIFY], LocalStack fidelity, Go/Terratest, retries/timeouts, contract/upgrade/drift tests, janitors.  
**Estimated time:** 6 minutes  
**Question:** Identify the minimum evidence you would collect before a high-risk change involving native tests, positive/negative/idempotency tests, plan JSON, mocks [VERIFY], LocalStack fidelity, Go/Terratest, retries/timeouts, contract/upgrade/drift tests, janitors.

**Model answer:** Collect the declared configuration, target environment and effective identity, relevant state/backend context, proposed change or status output, applicable policy/test results, ownership/dependency evidence, and a recovery/rollback assessment. Match test type to the claim: static checks do not prove cloud behavior; emulator success does not prove real IAM/quota parity; integration tests require isolated targets, bounded retries, and reliable cleanup.

**Rationale:** The evidence ties the intended change to the correct target and makes impact and recovery reviewable.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U11-SA-03 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L3  
**Objective tested:** Explain native tests, positive/negative/idempotency tests, plan JSON, mocks [VERIFY], LocalStack fidelity, Go/Terratest, retries/timeouts, contract/upgrade/drift tests, janitors.  
**Estimated time:** 7 minutes  
**Question:** Describe one failure mode and one preventive control for native tests, positive/negative/idempotency tests, plan JSON, mocks [VERIFY], LocalStack fidelity, Go/Terratest, retries/timeouts, contract/upgrade/drift tests, janitors.

**Model answer:** Failure mode: only happy-path tests; claim LocalStack proves all cloud behavior; unbounded retry; cleanup runs against wrong target. Prevention: explicit target and ownership checks, least privilege, reviewable evidence, bounded change scope, and a tested recovery path appropriate to the tool.

**Rationale:** Prevention should interrupt the failure before mutation and provide observable evidence that the guardrail works.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U11-MCQ-01 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L1  
**Objective tested:** Choose a safe and technically accurate response for 11.  
**Estimated time:** 3 minutes  
**Question:** What does a passing LocalStack test prove?

A. All real-cloud IAM and quota behavior
B. Only behavior covered by that test against the emulator and its supported fidelity
C. No need for integration testing
D. The production account is configured correctly

**Model answer:** **B.** Only behavior covered by that test against the emulator and its supported fidelity

**Rationale:** Emulator fidelity is bounded and must be documented.

**Common wrong answers / distractor analysis:** **A:** A overclaims parity **B:** Correct choice. **C:** C confuses test layers **D:** D is outside the test target.

### U11-MCQ-02 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L2  
**Objective tested:** Choose a safe and technically accurate response for 11.  
**Estimated time:** 3 minutes  
**Question:** Why test negative cases?

A. To make CI slower
B. To verify invalid or unsafe configurations are rejected
C. To avoid reviewing plans
D. To guarantee zero defects

**Model answer:** **B.** To verify invalid or unsafe configurations are rejected

**Rationale:** Negative tests prove guardrails reject known bad inputs.

**Common wrong answers / distractor analysis:** **A:** A is not the purpose **B:** Correct choice. **C:** C removes a separate control **D:** D overpromises.

### U11-MCQ-03 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L3  
**Objective tested:** Choose a safe and technically accurate response for 11.  
**Estimated time:** 3 minutes  
**Question:** A Terratest test times out and cleanup also fails. Best response?

A. Ignore leftover resources
B. Capture logs/state/target, stop unsafe retries, inventory leftovers and clean only verified test-owned resources
C. Run janitor against the whole account
D. Increase retries without limit

**Model answer:** **B.** Capture logs/state/target, stop unsafe retries, inventory leftovers and clean only verified test-owned resources

**Rationale:** A test failure can leave resources behind; recovery must be scoped and evidenced.

**Common wrong answers / distractor analysis:** **A:** A leaves leaks **B:** Correct choice. **C:** C has dangerous blast radius **D:** D may amplify failures.

### U11-OUT-01 — Output interpretation — initial signal

**Unit / topic:** Output interpretation — initial signal  
**Level:** L2  
**Objective tested:** Interpret an 11 signal without overclaiming.  
**Estimated time:** 7 minutes  
**Question:** [ILLUSTRATIVE] A tool run reports: `target=integration test timed out; cleanup status unknown`. No additional context is provided.

Read the synthetic output. What can you infer, what remains unknown, and what is the safest next action?

**Model answer:** The output is a signal, not enough to authorize a change. Confirm the effective target and identity, collect surrounding logs/state/plan or conditions, determine whether any mutation partially succeeded, and assess affected resources and rollback before acting. Specifically for this unit: Match test type to the claim: static checks do not prove cloud behavior; emulator success does not prove real IAM/quota parity; integration tests require isolated targets, bounded retries, and reliable cleanup.

**Rationale:** The output identifies a risk or failure category but lacks enough context to prove full scope, root cause, or safe recovery.

**Common wrong answers:** Assuming success from a single status field; retrying immediately; taking a destructive action before target and partial-success checks.

**Safety/version note:** [ILLUSTRATIVE] Synthetic output; not executed.

### U11-OUT-02 — Output interpretation — incomplete green gate

**Unit / topic:** Output interpretation — incomplete green gate  
**Level:** L3  
**Objective tested:** Identify missing evidence for 11.  
**Estimated time:** 8 minutes  
**Question:** [ILLUSTRATIVE] A reviewer receives a green CI summary: `validate=PASS policy=PASS plan=PASS`. The artifact has no recorded target account/project, backend identifier, effective identity, or post-apply verification. The diff includes a change related to native tests.

Should the reviewer approve, reject, or request more information? Explain what is and is not proven.

**Model answer:** **Needs-info / hold.** Green checks only prove the recorded checks passed against their actual inputs. Require target/backend/identity evidence, the complete reviewed diff and relevant state, plus unit-specific evidence: Match test type to the claim: static checks do not prove cloud behavior; emulator success does not prove real IAM/quota parity; integration tests require isolated targets, bounded retries, and reliable cleanup.

**Rationale:** A green summary is not a substitute for artifact identity, target proof, scope review, or runtime/post-change verification.

**Common wrong answers:** Approve because all statuses are green; reject without examining evidence when a hold can safely resolve uncertainty; assume the plan proves runtime behavior.

**Safety/version note:** [ILLUSTRATIVE] Synthetic output; not executed.

### U11-REV-01 — Code/config review

**Unit / topic:** Code/config review  
**Level:** L3  
**Objective tested:** Find at least three defects in a 11 workflow and propose safer corrections.  
**Estimated time:** 10 minutes  
**Question:** Review this intentionally flawed snippet. Identify at least three substantive defects, their likely impact, and a corrected pattern. Do not execute it.

```text
# Illustrative integration test (intentionally flawed)
func TestPlatform(t *testing.T) {
  terraform.InitAndApply(t, options)
  assertExpected(t)
  // no guaranteed cleanup or bounded timeout
}
# shared target account used by parallel tests
# LocalStack pass is described as proof of real-cloud IAM/quota behavior
```

**Model answer:**
1. **Defect and correction:** Cleanup is not guaranteed if assertion fails; use robust teardown and independently verify leftovers.
2. **Defect and correction:** Shared target plus parallel tests risks cross-test interference; isolate state/accounts/namespaces and bound concurrency.
3. **Defect and correction:** Emulator fidelity overclaimed; document gaps and test cloud-only semantics separately where justified.

**Rationale:** The snippet lacks layered controls for native tests, positive/negative/idempotency tests, plan JSON, mocks [VERIFY], LocalStack fidelity, Go/Terratest, retries/timeouts, contract/upgrade/drift tests, janitors; a safe correction verifies target and ownership, narrows permissions and change scope, preserves evidence, and includes a tested recovery path.

**Common wrong answers:** Fixing only syntax; treating a comment as an enforced control; assuming a green command means the operation is safe; overlooking secret exposure or cleanup.

**Safety/version note:** `[ILLUSTRATIVE]` Review exercise only; not executed. Confirm syntax and behavior for the installed versions before adapting any pattern.

### U11-REV-02 — Code/config review

**Unit / topic:** Code/config review  
**Level:** L4  
**Objective tested:** Find at least three defects in a 11 workflow and propose safer corrections.  
**Estimated time:** 12 minutes  
**Question:** Review this intentionally flawed snippet. Identify at least three substantive defects, their likely impact, and a corrected pattern. Do not execute it.

```text
# Illustrative integration test (intentionally flawed)
func TestPlatform(t *testing.T) {
  terraform.InitAndApply(t, options)
  assertExpected(t)
  // no guaranteed cleanup or bounded timeout
}
# shared target account used by parallel tests
# LocalStack pass is described as proof of real-cloud IAM/quota behavior
```

**Model answer:**
1. **Defect and correction:** Emulator fidelity overclaimed; document gaps and test cloud-only semantics separately where justified.
2. **Defect and correction:** Shared target plus parallel tests risks cross-test interference; isolate state/accounts/namespaces and bound concurrency.
3. **Defect and correction:** Cleanup is not guaranteed if assertion fails; use robust teardown and independently verify leftovers.

**Rationale:** The snippet lacks layered controls for native tests, positive/negative/idempotency tests, plan JSON, mocks [VERIFY], LocalStack fidelity, Go/Terratest, retries/timeouts, contract/upgrade/drift tests, janitors; a safe correction verifies target and ownership, narrows permissions and change scope, preserves evidence, and includes a tested recovery path.

**Common wrong answers:** Fixing only syntax; treating a comment as an enforced control; assuming a green command means the operation is safe; overlooking secret exposure or cleanup.

**Safety/version note:** `[ILLUSTRATIVE]` Review exercise only; not executed. Confirm syntax and behavior for the installed versions before adapting any pattern.

### U11-INC-01 — Incident and troubleshooting

**Unit / topic:** Incident and troubleshooting  
**Level:** L4  
**Objective tested:** Respond to a unit-specific infrastructure failure with containment, blast-radius analysis, recovery and prevention.  
**Estimated time:** 15 minutes  
**Question:** Symptom: a deployment involving native tests fails part-way through. Operators disagree whether to retry or roll back. Give a structured response: symptom/evidence → diagnosis → blast-radius and rollback check → immediate fix → prevention/regression test.

**Model answer:** 1. **Contain:** pause further writes/deployments and avoid broad retries. 2. **Evidence:** capture timestamps, exact error, target identity, backend/state or controller status, plan/change record and logs with secrets redacted. 3. **Diagnose:** distinguish configuration error, authorization, provider/API failure, concurrency, partial apply and external drift. 4. **Blast radius:** enumerate changed, replaced, deleted and possibly created resources; identify stateful/data dependencies and other environments. 5. **Rollback/recovery:** verify the correct target, preserve current state/evidence, choose a tested recovery or forward-fix path; do not assume inverse apply is safe. 6. **Fix and verify:** make the smallest reviewed correction and run appropriate post-change checks. 7. **Prevent:** add a regression/negative test, target assertion, alert/runbook or policy as appropriate. Unit-specific concerns: Match test type to the claim: static checks do not prove cloud behavior; emulator success does not prove real IAM/quota parity; integration tests require isolated targets, bounded retries, and reliable cleanup.

**Rationale:** The sequence prevents a second failure while preserving enough evidence to distinguish root cause from symptoms. Recovery choice depends on partial success, data semantics and tool version.

**Common wrong answers:** Blind retry; destroy/recreate before inventory; restore state without target verification; declare recovery from command exit code alone; omit a regression test.

### U11-DES-01 — Design question with scoring rubric

**Unit / topic:** Design question with scoring rubric  
**Level:** L4  
**Objective tested:** Design an operationally safe 11 approach with explicit trade-offs and evidence.  
**Estimated time:** 20 minutes  
**Question:** Design a solution for native tests, positive/negative/idempotency tests, plan JSON, mocks [VERIFY], LocalStack fidelity, Go/Terratest, retries/timeouts, contract/upgrade/drift tests, janitors. State assumptions, define boundaries and ownership, describe normal workflow and failure handling, identify security controls, and explain what evidence demonstrates success. Keep implementation local/LocalStack by default.

**Model answer:** A strong design names the authoritative owner and target; separates environments and credentials where appropriate; documents inputs, versions and limits; uses least privilege, reviewable plans/policy/tests and bounded operations; preserves recovery evidence; and defines post-change verification, alerting, rollback criteria and an exit path. Specifically: Match test type to the claim: static checks do not prove cloud behavior; emulator success does not prove real IAM/quota parity; integration tests require isolated targets, bounded retries, and reliable cleanup.

**Rationale:** Production quality depends on explicit ownership, fail-safe behavior, verifiable evidence and operational recovery—not merely a successful happy path.

**Common wrong answers:** “Use best practices” without naming controls; assume the tool guarantees safety; omit a failure path; mix dev/prod ownership; provide no evidence or measurable acceptance criteria.

**Scoring rubric (20 points):**
- Correct architecture and ownership boundary — 4
- Target, identity, state and blast-radius controls — 4
- Security/policy/testing controls — 4
- Failure handling, rollback/recovery and verification — 4
- Trade-offs, evidence, version assumptions and exit path — 4

**Safety/version note:** Verify version-sensitive syntax and provider-specific semantics before implementation.


### Unit 12 — 12

**Scope and objectives:** controllers reconcile desired state; CRDs, ProviderConfig, XRDs, Compositions, XRs/claims define APIs; conditions are evidence not guarantees; deletion/ownership/credentials/RBAC/provider upgrades need careful boundaries.

### U12-SA-01 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L1  
**Objective tested:** Explain reconcile loop, managed resources, ProviderConfig, XRD/Composition/XR/claim, conditions, external-name, Delete/Orphan, managementPolicies [VERIFY], GitOps, quotas/rate limits, backup/restore, adoption/exit.  
**Estimated time:** 4 minutes  
**Question:** Explain the core purpose and one important limitation of reconcile loop.

**Model answer:** Verify API group/version and provider package schema. Establish one owner per object; inspect conditions/events and external identity; model deletion semantics and recovery before changing claims or compositions.

**Rationale:** A common error is to treat the mechanism as a guarantee of runtime health or safety; it only addresses the stated scope.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U12-SA-02 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L2  
**Objective tested:** Explain reconcile loop, managed resources, ProviderConfig, XRD/Composition/XR/claim, conditions, external-name, Delete/Orphan, managementPolicies [VERIFY], GitOps, quotas/rate limits, backup/restore, adoption/exit.  
**Estimated time:** 6 minutes  
**Question:** Identify the minimum evidence you would collect before a high-risk change involving reconcile loop, managed resources, ProviderConfig, XRD/Composition/XR/claim, conditions, external-name, Delete/Orphan, managementPolicies [VERIFY], GitOps, quotas/rate limits, backup/restore, adoption/exit.

**Model answer:** Collect the declared configuration, target environment and effective identity, relevant state/backend context, proposed change or status output, applicable policy/test results, ownership/dependency evidence, and a recovery/rollback assessment. Verify API group/version and provider package schema. Establish one owner per object; inspect conditions/events and external identity; model deletion semantics and recovery before changing claims or compositions.

**Rationale:** The evidence ties the intended change to the correct target and makes impact and recovery reviewable.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U12-SA-03 — Conceptual short answer

**Unit / topic:** Conceptual short answer  
**Level:** L3  
**Objective tested:** Explain reconcile loop, managed resources, ProviderConfig, XRD/Composition/XR/claim, conditions, external-name, Delete/Orphan, managementPolicies [VERIFY], GitOps, quotas/rate limits, backup/restore, adoption/exit.  
**Estimated time:** 7 minutes  
**Question:** Describe one failure mode and one preventive control for reconcile loop, managed resources, ProviderConfig, XRD/Composition/XR/claim, conditions, external-name, Delete/Orphan, managementPolicies [VERIFY], GitOps, quotas/rate limits, backup/restore, adoption/exit.

**Model answer:** Failure mode: assuming claim deletion always or never deletes infrastructure; dual Terraform/Crossplane management; broad provider credentials; interpreting Ready as full application correctness. Prevention: explicit target and ownership checks, least privilege, reviewable evidence, bounded change scope, and a tested recovery path appropriate to the tool.

**Rationale:** Prevention should interrupt the failure before mutation and provide observable evidence that the guardrail works.

**Common wrong answers:** “Just run the command” ignores target, ownership and rollback; “the tool guarantees it” overstates the mechanism.

### U12-MCQ-01 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L1  
**Objective tested:** Choose a safe and technically accurate response for 12.  
**Estimated time:** 3 minutes  
**Question:** What does a controller reconciliation loop do?

A. Runs once and exits permanently
B. Repeatedly compares observed state with declared desired state and attempts convergence
C. Guarantees application-level correctness
D. Replaces Kubernetes RBAC

**Model answer:** **B.** Repeatedly compares observed state with declared desired state and attempts convergence

**Rationale:** Reconciliation is continuous control-loop behavior.

**Common wrong answers / distractor analysis:** **A:** A misunderstands controllers **B:** Correct choice. **C:** C overstates scope **D:** D confuses reconciliation with authorization.

### U12-MCQ-02 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L2  
**Objective tested:** Choose a safe and technically accurate response for 12.  
**Estimated time:** 3 minutes  
**Question:** A Crossplane claim is deleted. What is the safe assumption?

A. Underlying resources always persist
B. Underlying resources always delete
C. Deletion outcome depends on composition, ownership and configured/version-specific deletion semantics; inspect before acting
D. Kubernetes namespace is the only control

**Model answer:** **C.** Deletion outcome depends on composition, ownership and configured/version-specific deletion semantics; inspect before acting

**Rationale:** Deletion semantics are configuration and version dependent and must be verified.

**Common wrong answers / distractor analysis:** **A:** This option ignores the required safety boundary and is not supported by the evidence. **B:** This option ignores the required safety boundary and is not supported by the evidence. **C:** Correct choice. **D:** This option ignores the required safety boundary and is not supported by the evidence.

### U12-MCQ-03 — Multiple choice

**Unit / topic:** Multiple choice  
**Level:** L3  
**Objective tested:** Choose a safe and technically accurate response for 12.  
**Estimated time:** 3 minutes  
**Question:** A managed resource is Ready. What else may still need checking?

A. Nothing
B. Conditions/events, external identity, provider permissions, dependent service health and desired outcome
C. Only its YAML indentation
D. Whether Terraform also manages it

**Model answer:** **B.** Conditions/events, external identity, provider permissions, dependent service health and desired outcome

**Rationale:** A condition is useful evidence but not complete end-to-end proof.

**Common wrong answers / distractor analysis:** **A:** A overstates readiness **B:** Correct choice. **C:** C is insufficient **D:** D highlights a hazard but is not the full verification set.

### U12-OUT-01 — Output interpretation — initial signal

**Unit / topic:** Output interpretation — initial signal  
**Level:** L2  
**Objective tested:** Interpret an 12 signal without overclaiming.  
**Estimated time:** 7 minutes  
**Question:** [ILLUSTRATIVE] A tool run reports: `target=managed resource condition Ready=False; provider reports authorization error`. No additional context is provided.

Read the synthetic output. What can you infer, what remains unknown, and what is the safest next action?

**Model answer:** The output is a signal, not enough to authorize a change. Confirm the effective target and identity, collect surrounding logs/state/plan or conditions, determine whether any mutation partially succeeded, and assess affected resources and rollback before acting. Specifically for this unit: Verify API group/version and provider package schema. Establish one owner per object; inspect conditions/events and external identity; model deletion semantics and recovery before changing claims or compositions.

**Rationale:** The output identifies a risk or failure category but lacks enough context to prove full scope, root cause, or safe recovery.

**Common wrong answers:** Assuming success from a single status field; retrying immediately; taking a destructive action before target and partial-success checks.

**Safety/version note:** [ILLUSTRATIVE] Synthetic output; not executed.

### U12-OUT-02 — Output interpretation — incomplete green gate

**Unit / topic:** Output interpretation — incomplete green gate  
**Level:** L3  
**Objective tested:** Identify missing evidence for 12.  
**Estimated time:** 8 minutes  
**Question:** [ILLUSTRATIVE] A reviewer receives a green CI summary: `validate=PASS policy=PASS plan=PASS`. The artifact has no recorded target account/project, backend identifier, effective identity, or post-apply verification. The diff includes a change related to reconcile loop.

Should the reviewer approve, reject, or request more information? Explain what is and is not proven.

**Model answer:** **Needs-info / hold.** Green checks only prove the recorded checks passed against their actual inputs. Require target/backend/identity evidence, the complete reviewed diff and relevant state, plus unit-specific evidence: Verify API group/version and provider package schema. Establish one owner per object; inspect conditions/events and external identity; model deletion semantics and recovery before changing claims or compositions.

**Rationale:** A green summary is not a substitute for artifact identity, target proof, scope review, or runtime/post-change verification.

**Common wrong answers:** Approve because all statuses are green; reject without examining evidence when a hold can safely resolve uncertainty; assume the plan proves runtime behavior.

**Safety/version note:** [ILLUSTRATIVE] Synthetic output; not executed.

### U12-REV-01 — Code/config review

**Unit / topic:** Code/config review  
**Level:** L3  
**Objective tested:** Find at least three defects in a 12 workflow and propose safer corrections.  
**Estimated time:** 10 minutes  
**Question:** Review this intentionally flawed snippet. Identify at least three substantive defects, their likely impact, and a corrected pattern. Do not execute it.

```text
# Illustrative Crossplane setup (intentionally flawed)
# provider uses broad long-lived credentials
# Terraform and Crossplane both own the same external object
# claim deletion semantics are assumed without checking policy/version
# Ready condition is treated as application health
```

**Model answer:**
1. **Defect and correction:** Broad long-lived credentials exceed least privilege; use scoped identity and secret rotation/storage controls.
2. **Defect and correction:** Dual management creates ownership conflict; assign one authoritative controller per external object.
3. **Defect and correction:** Deletion semantics/version and Ready scope are assumed; inspect API/schema/conditions/events and verify application outcome.

**Rationale:** The snippet lacks layered controls for reconcile loop, managed resources, ProviderConfig, XRD/Composition/XR/claim, conditions, external-name, Delete/Orphan, managementPolicies [VERIFY], GitOps, quotas/rate limits, backup/restore, adoption/exit; a safe correction verifies target and ownership, narrows permissions and change scope, preserves evidence, and includes a tested recovery path.

**Common wrong answers:** Fixing only syntax; treating a comment as an enforced control; assuming a green command means the operation is safe; overlooking secret exposure or cleanup.

**Safety/version note:** `[ILLUSTRATIVE]` Review exercise only; not executed. Confirm syntax and behavior for the installed versions before adapting any pattern.

### U12-REV-02 — Code/config review

**Unit / topic:** Code/config review  
**Level:** L4  
**Objective tested:** Find at least three defects in a 12 workflow and propose safer corrections.  
**Estimated time:** 12 minutes  
**Question:** Review this intentionally flawed snippet. Identify at least three substantive defects, their likely impact, and a corrected pattern. Do not execute it.

```text
# Illustrative Crossplane setup (intentionally flawed)
# provider uses broad long-lived credentials
# Terraform and Crossplane both own the same external object
# claim deletion semantics are assumed without checking policy/version
# Ready condition is treated as application health
```

**Model answer:**
1. **Defect and correction:** Deletion semantics/version and Ready scope are assumed; inspect API/schema/conditions/events and verify application outcome.
2. **Defect and correction:** Dual management creates ownership conflict; assign one authoritative controller per external object.
3. **Defect and correction:** Broad long-lived credentials exceed least privilege; use scoped identity and secret rotation/storage controls.

**Rationale:** The snippet lacks layered controls for reconcile loop, managed resources, ProviderConfig, XRD/Composition/XR/claim, conditions, external-name, Delete/Orphan, managementPolicies [VERIFY], GitOps, quotas/rate limits, backup/restore, adoption/exit; a safe correction verifies target and ownership, narrows permissions and change scope, preserves evidence, and includes a tested recovery path.

**Common wrong answers:** Fixing only syntax; treating a comment as an enforced control; assuming a green command means the operation is safe; overlooking secret exposure or cleanup.

**Safety/version note:** `[ILLUSTRATIVE]` Review exercise only; not executed. Confirm syntax and behavior for the installed versions before adapting any pattern.

### U12-INC-01 — Incident and troubleshooting

**Unit / topic:** Incident and troubleshooting  
**Level:** L4  
**Objective tested:** Respond to a unit-specific infrastructure failure with containment, blast-radius analysis, recovery and prevention.  
**Estimated time:** 15 minutes  
**Question:** Symptom: a deployment involving reconcile loop fails part-way through. Operators disagree whether to retry or roll back. Give a structured response: symptom/evidence → diagnosis → blast-radius and rollback check → immediate fix → prevention/regression test.

**Model answer:** 1. **Contain:** pause further writes/deployments and avoid broad retries. 2. **Evidence:** capture timestamps, exact error, target identity, backend/state or controller status, plan/change record and logs with secrets redacted. 3. **Diagnose:** distinguish configuration error, authorization, provider/API failure, concurrency, partial apply and external drift. 4. **Blast radius:** enumerate changed, replaced, deleted and possibly created resources; identify stateful/data dependencies and other environments. 5. **Rollback/recovery:** verify the correct target, preserve current state/evidence, choose a tested recovery or forward-fix path; do not assume inverse apply is safe. 6. **Fix and verify:** make the smallest reviewed correction and run appropriate post-change checks. 7. **Prevent:** add a regression/negative test, target assertion, alert/runbook or policy as appropriate. Unit-specific concerns: Verify API group/version and provider package schema. Establish one owner per object; inspect conditions/events and external identity; model deletion semantics and recovery before changing claims or compositions.

**Rationale:** The sequence prevents a second failure while preserving enough evidence to distinguish root cause from symptoms. Recovery choice depends on partial success, data semantics and tool version.

**Common wrong answers:** Blind retry; destroy/recreate before inventory; restore state without target verification; declare recovery from command exit code alone; omit a regression test.

### U12-DES-01 — Design question with scoring rubric

**Unit / topic:** Design question with scoring rubric  
**Level:** L4  
**Objective tested:** Design an operationally safe 12 approach with explicit trade-offs and evidence.  
**Estimated time:** 20 minutes  
**Question:** Design a solution for reconcile loop, managed resources, ProviderConfig, XRD/Composition/XR/claim, conditions, external-name, Delete/Orphan, managementPolicies [VERIFY], GitOps, quotas/rate limits, backup/restore, adoption/exit. State assumptions, define boundaries and ownership, describe normal workflow and failure handling, identify security controls, and explain what evidence demonstrates success. Keep implementation local/LocalStack by default.

**Model answer:** A strong design names the authoritative owner and target; separates environments and credentials where appropriate; documents inputs, versions and limits; uses least privilege, reviewable plans/policy/tests and bounded operations; preserves recovery evidence; and defines post-change verification, alerting, rollback criteria and an exit path. Specifically: Verify API group/version and provider package schema. Establish one owner per object; inspect conditions/events and external identity; model deletion semantics and recovery before changing claims or compositions.

**Rationale:** Production quality depends on explicit ownership, fail-safe behavior, verifiable evidence and operational recovery—not merely a successful happy path.

**Common wrong answers:** “Use best practices” without naming controls; assume the tool guarantees safety; omit a failure path; mix dev/prod ownership; provide no evidence or measurable acceptance criteria.

**Scoring rubric (20 points):**
- Correct architecture and ownership boundary — 4
- Target, identity, state and blast-radius controls — 4
- Security/policy/testing controls — 4
- Failure handling, rollback/recovery and verification — 4
- Trade-offs, evidence, version assumptions and exit path — 4

**Safety/version note:** Verify version-sensitive syntax and provider-specific semantics before implementation.


## Cross-unit integration scenarios

Each scenario integrates at least two units. The answers are model responses, not a claim that any commands were executed.
### X-001 — State backend + plan review

**Unit / topic:** State backend + plan review  
**Level:** L3  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 10 minutes  
**Question:** A reviewed plan is based on a backend that may be shared by dev and prod. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Needs-info/hold. Verify backend identity, workspace, effective cloud identity and environment assertions; stop concurrent writers; inspect plan actions and state backup/recovery. Separate state/permissions where required and re-plan only after the correct target is established.

**Rationale:** The plan is only meaningful for the state and target it evaluated.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

### X-002 — Module upgrade + consumer contracts

**Unit / topic:** Module upgrade + consumer contracts  
**Level:** L3  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 10 minutes  
**Question:** A pinned module upgrade changes an output used by staging and prod. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Test compatibility in a disposable environment; inspect changelog and typed input/output contract; add consumer/contract tests; version the breaking change and roll environments through approvals. Do not upgrade prod first.

**Rationale:** Module reuse depends on stable interfaces and staged evidence.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

### X-003 — Import + drift + ownership

**Unit / topic:** Import + drift + ownership  
**Level:** L3  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 10 minutes  
**Question:** An existing storage object is imported while the old state still declares it. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Pause apply; map object ID/address and both states; back up both; choose one owner; perform version-supported import/move workflow and inspect resulting plan.

**Rationale:** Dual management can cause competing updates or deletion.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

### X-004 — Plan analyzer + human approval

**Unit / topic:** Plan analyzer + human approval  
**Level:** L3  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 10 minutes  
**Question:** A plan analyzer flags replacement but CI says all checks passed. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Hold approval. Inspect exact actions, stateful dependencies, unknowns, policy result, target identity, analyzer test coverage and human-approved artifact. Decide approve/reject/needs-info based on evidence.

**Rationale:** Automated risk scoring supports but does not replace accountable review.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

### X-005 — Account boundary + CI identity

**Unit / topic:** Account boundary + CI identity  
**Level:** L3  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 10 minutes  
**Question:** A dev pipeline inherits a prod credential from the runner. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Fail closed; record effective identity without exposing secrets; rotate/revoke if exposed; separate workload identities and add account/project assertions, least privilege and negative tests.

**Rationale:** Directory labels and workspaces do not override cloud authorization.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

### X-006 — Policy JSON + provider IAM

**Unit / topic:** Policy JSON + provider IAM  
**Level:** L3  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 10 minutes  
**Question:** A public-access policy passes because the plan JSON lacks the relevant attribute. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Check schema/unknowns and whether the policy input covers the setting; reject/needs-info until the rule is tested against a crafted failing plan. Enforce cloud-side IAM/organization controls and post-apply checks as defense in depth.

**Rationale:** A policy cannot enforce a property absent from its evaluated input.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

### X-007 — Quota + recovery headroom

**Unit / topic:** Quota + recovery headroom  
**Level:** L3  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 10 minutes  
**Question:** A launch uses nearly all regional capacity and a rollback would require replacement capacity. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Pause rollout; check actual quota scope and usage; estimate remaining capacity for normal operation, recovery and DR; capture provider error and escalate. Stage deployment or request quota increase based on evidence.

**Rationale:** Quota planning must include concurrent demand and recovery capacity.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

### X-008 — Decommission + retention

**Unit / topic:** Decommission + retention  
**Level:** L3  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 10 minutes  
**Question:** An old data bucket is tagged temporary but may contain retained datasets. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Do not delete. Identify owner/data classification, retention/legal hold, dependencies and backup; produce dry-run inventory and plan, approval, bounded deletion and evidence; verify lifecycle prevention.

**Rationale:** Cost and age do not override retention and ownership.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

### X-009 — Terraform/OpenTofu/Pulumi decision

**Unit / topic:** Terraform/OpenTofu/Pulumi decision  
**Level:** L3  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 10 minutes  
**Question:** The team proposes replacing its tool because syntax looks similar. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Compare state/provider semantics, workflows, policy/tests, language/team skills, migration tooling and exit cost. Inventory ownership; rehearse on disposable copy; verify version support; cut over one boundary at a time.

**Rationale:** Conceptual similarity does not guarantee state or provider interchangeability.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

### X-010 — Ansible convergence + immutable image

**Unit / topic:** Ansible convergence + immutable image  
**Level:** L3  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 10 minutes  
**Question:** A playbook repairs drift every night but the same host drifts again. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Determine whether configuration belongs in an immutable image, Ansible convergence, or a Kubernetes controller. Use idempotent modules, identify competing writers, add drift evidence and limit rollout; do not mask symptoms with repeated shell commands.

**Rationale:** Choose one authoritative mechanism for each configuration surface.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

### X-011 — Testing pyramid + LocalStack

**Unit / topic:** Testing pyramid + LocalStack  
**Level:** L3  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 10 minutes  
**Question:** LocalStack passes but the real cloud denies an IAM action. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Treat the emulator result as bounded evidence. Inspect actual identity/policy and cloud error; add an integration or contract test for the cloud-only semantic and maintain a fidelity table. Keep destructive testing isolated.

**Rationale:** Emulator parity is not universal.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

### X-012 — Crossplane + Terraform ownership

**Unit / topic:** Crossplane + Terraform ownership  
**Level:** L3  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 10 minutes  
**Question:** A Terraform plan proposes deletion of an object also reconciled by Crossplane. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Stop both writers; identify authoritative owner, state address and external identity; preserve state; transfer ownership deliberately and test in lab. Do not apply either controller until ownership is singular.

**Rationale:** Dual management can create a reconciliation fight or destructive drift.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

### X-013 — Provider failure during apply + state recovery

**Unit / topic:** Provider failure during apply + state recovery  
**Level:** L3  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 10 minutes  
**Question:** An apply times out after creating some resources; state is uncertain. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Do not blindly retry. Preserve logs and state copy, confirm target, inspect provider/API and actual objects, determine partial success, then run supported refresh/plan/recovery procedure. Verify no duplicates or orphaned resources.

**Rationale:** A client timeout does not prove the server made no change.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

### X-014 — Secret in state + plan artifact + logs

**Unit / topic:** Secret in state + plan artifact + logs  
**Level:** L3  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 10 minutes  
**Question:** A credential appears in a CI artifact and task output. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Restrict/remove artifact access, preserve incident evidence securely, rotate/revoke credential, inspect state/plan/log/cache retention and downstream copies, then add redaction, access controls and secret-scanning tests. `sensitive`/`no_log` do not erase persisted values.

**Rationale:** Exposure response must address all persistence surfaces.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

### X-015 — Wrong account/profile in CI

**Unit / topic:** Wrong account/profile in CI  
**Level:** L4  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 10 minutes  
**Question:** The pipeline applies successfully but to the wrong account. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Treat as an incident: stop further changes, identify every resource touched and whether data/security exposure occurred, preserve logs and plan, notify owner, assess safe compensation/recovery, add fail-closed identity assertions and negative tests.

**Rationale:** Successful execution is not correct execution.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

### X-016 — Policy passes, runtime fails

**Unit / topic:** Policy passes, runtime fails  
**Level:** L3  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 10 minutes  
**Question:** Policy and plan pass but a deployed service is unreachable. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Check policy scope, network/dependency assumptions, provider result and post-apply health. Use runtime smoke/health checks and rollback criteria; extend test coverage for the missing behavior.

**Rationale:** Pre-apply policy does not prove service health.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

### X-017 — Manual drift after apply

**Unit / topic:** Manual drift after apply  
**Level:** L3  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 10 minutes  
**Question:** A console change is discovered during the next plan. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Record who/what/why, compare observed change to desired configuration, assess security and blast radius, then either codify the intended change or revert under approval. Test drift detection and restrict unauthorized manual mutation.

**Rationale:** Do not blindly overwrite potentially intentional or security-relevant changes.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

### X-018 — Quota exhaustion during deployment

**Unit / topic:** Quota exhaustion during deployment  
**Level:** L3  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 10 minutes  
**Question:** Some resources exist but later ones failed due to quota. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Pause new waves, inventory partial resources and state, identify service/region quota and remaining headroom, then decide staged retry, cleanup of verified test-owned resources, or escalation. Add quota preflight and concurrency controls.

**Rationale:** Partial apply plus retries can create duplicate or orphaned resources.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

### X-019 — Cleanup janitor hits protected resource

**Unit / topic:** Cleanup janitor hits protected resource  
**Level:** L3  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 10 minutes  
**Question:** A scheduled cleanup proposes deleting an untagged shared resource. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Stop job and quarantine candidate; verify owner, dependencies, retention and environment; review dry-run evidence and deletion cap; repair metadata/inventory and add protected-resource exclusions and test fixtures.

**Rationale:** Missing tags are not proof of orphan status.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

### X-020 — Stateful module replacement

**Unit / topic:** Stateful module replacement  
**Level:** L3  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 15 minutes  
**Question:** An upgrade plan replaces a persistent storage resource. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Reject/hold until replacement reason, data migration, backup/restore test, downtime, dependencies and recovery are understood. Test in isolated env and update module compatibility policy.

**Rationale:** A valid plan can still be unacceptable operationally.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

### X-021 — Ansible become + privilege

**Unit / topic:** Ansible become + privilege  
**Level:** L3  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 15 minutes  
**Question:** A playbook uses `become: true` for every host and task. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Narrow privilege to tasks that require it, scope inventory and host group, verify host identity, use least-privilege sudo and secret-safe output, and test with a bounded rollout.

**Rationale:** Convenience does not justify blanket privilege escalation.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

### X-022 — SSH host-key verification disabled

**Unit / topic:** SSH host-key verification disabled  
**Level:** L3  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 15 minutes  
**Question:** A deployment succeeds after disabling host-key checks to fix a connection error. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Restore host-key verification; establish trusted host keys and diagnose mismatch; consider credential exposure and investigate logs. Add CI/lint guard to reject disabling authenticity checks.

**Rationale:** Disabling verification hides a security boundary rather than fixing trust.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

### X-023 — Crossplane provider upgrade

**Unit / topic:** Crossplane provider upgrade  
**Level:** L3  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 15 minutes  
**Question:** A provider package upgrade causes reconciliation failures. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Hold further rollout, inspect package/schema/version notes and managed-resource conditions/events, compare rendered/composed resources, preserve cluster/etcd and external-state recovery data, test rollback compatibility, and upgrade in stages.

**Rationale:** Controller API/schema changes can alter reconciliation and require explicit verification.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

### X-024 — Crossplane claim deletion

**Unit / topic:** Crossplane claim deletion  
**Level:** L3  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 15 minutes  
**Question:** A team deletes a claim to clean a namespace. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Before deletion inspect XR/claim linkage, composition and configured deletion behavior (`Delete`/`Orphan` and management policies are version-sensitive). Confirm external object inventory and recovery; run only a disposable lab demonstration until semantics are verified.

**Rationale:** Claim deletion is not universally equivalent to external deletion or retention.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

### X-025 — Management cluster loss

**Unit / topic:** Management cluster loss  
**Level:** L3  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 15 minutes  
**Question:** Crossplane management cluster is lost while cloud resources remain. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Recover cluster/control-plane backups and provider credentials from secure backup, restore CRDs/compositions/provider configuration at verified versions, inspect external identities and reconcile cautiously. Prevent dual ownership and test restore drills.

**Rationale:** The control plane and external resources have different recovery lifecycles.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

### X-026 — Reconcile storm + API rate limit

**Unit / topic:** Reconcile storm + API rate limit  
**Level:** L3  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 15 minutes  
**Question:** Many Crossplane resources retry against a throttled provider API. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Reduce rollout/concurrency, inspect conditions/events and provider errors, avoid uncontrolled retries, prioritize critical resources, and review controller/provider backoff and API limits for installed versions. Add load tests and alerting.

**Rationale:** Retrying harder can amplify throttling.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

### X-027 — CI matrix too slow/flaky

**Unit / topic:** CI matrix too slow/flaky  
**Level:** L3  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 15 minutes  
**Question:** Every matrix job provisions the full integration stack and runs cleanup. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Move cheap static/native tests earlier; isolate and cap integration concurrency; use bounded timeouts/retries, reliable teardown and artifact capture; retain representative end-to-end tests. Never share state between parallel jobs.

**Rationale:** More integration tests are not automatically better if they interfere or leak.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

### X-028 — LocalStack parity gap

**Unit / topic:** LocalStack parity gap  
**Level:** L3  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 15 minutes  
**Question:** An emulator passes but production quota and IAM behavior differ. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Document exact fidelity limits, inspect real-cloud error and identity, add narrowly scoped cloud integration checks only where authorized, and avoid claiming emulator evidence proves unsupported semantics.

**Rationale:** Test claims must match the test environment.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

### X-029 — Retention + decommission evidence

**Unit / topic:** Retention + decommission evidence  
**Level:** L3  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 15 minutes  
**Question:** A project is retired but an audit requires evidence and retained data. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Inventory resources and data; identify retention/legal holds, dependencies, owner approvals and export/backup integrity; run reviewed bounded deletion only for eligible resources; preserve before/after records and verify retained data access.

**Rationale:** Decommissioning is a governed lifecycle, not a bulk destroy.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

### X-030 — Capstone: multi-environment data platform

**Unit / topic:** Capstone: multi-environment data platform  
**Level:** L4  
**Objective tested:** Integrate multiple units to make a safe decision with evidence.  
**Estimated time:** 15 minutes  
**Question:** The data/ML platform has local state, shared dev/prod config, public storage exposure, quota exhaustion, costly orphans and a wrong-target destroy. Explain the decision, evidence needed, blast radius, rollback/recovery, and prevention.

**Model answer:** Design distinct dev/staging/prod configurations and backend/identity boundaries; guarded bootstrap; reusable pinned modules; policy and risk analyzer; reviewed-plan approval; tests and fidelity table; drift checks; quota preflight/headroom; secret handling; state recovery/lock runbook; decommission dry-run, retention, deletion caps and audit evidence. Validate each deliverable with commands/inspection in local/LocalStack by default and record known limitations.

**Rationale:** The scenario is intentionally cross-cutting: safety depends on architecture, policy, tests, identity, state and operations working together.

**Common wrong answers:** Act before verifying target/ownership; treat a passing tool or status as a guarantee; skip evidence and rollback analysis; broaden permissions; retry or delete blindly.

**Safety/version note:** `[ASSUMPTION]` Scenario is synthetic. Verify version-specific syntax and provider behavior before any lab adaptation.

## Scoring rubric and learning decision

Score the **174 explicitly identified questions**; whiteboard prompts and capstone checkpoint are scored separately. Record both aggregate and per-unit scores. Suggested maximums are normalized per question so every question has equal weight unless a facilitator publishes a different weighting before the attempt.

- **MCQ:** 1 point for the best answer; 0 otherwise. To earn full credit in review discussion, the learner should explain all three distractors; the facilitator may record rationale quality separately but should not silently alter the published score.
- **Short answer:** 0–3 points: 1 for correct concept, 1 for relevant limitation/failure mode, 1 for evidence/control.
- **Output interpretation:** 0–4 points: identify signal, state what is unknown, name evidence/target checks, choose safe next action.
- **Code/config review:** 0–6 points: up to 1 point per each of three or more meaningful defects, and up to 3 for impact and safe correction. No credit for invented defects or fixes that create a new unsafe condition.
- **Incident:** 0–8 points: containment/evidence, diagnosis, blast-radius, rollback/recovery, fix/verification, prevention/regression test.
- **Design:** 0–20 points using the rubric attached to each design question. Normalize each item to a percentage before aggregating, or use a declared weighted scheme consistently.

**Decision thresholds (required):**
- **80% or higher:** proceed.
- **60–79%:** remediate weak units and repeat those questions.
- **Below 60%:** repeat the relevant lessons and retake the assessment.

**[ASSESSMENT RECOMMENDATION] Safety-critical override:** Regardless of aggregate score, remediation is mandatory after a material error involving wrong target/account/backend, secret exposure, unsafe destruction/deletion, or dual management of the same external object. Require a correct explanation and successful local negative-test demonstration before sign-off.

A high aggregate score must not conceal a low score on Units 1, 4, 5, 6, 8, 10 or 12. Report each unit’s normalized score, error types and remediation evidence.

## Ten design-review whiteboard prompts
### DR-01 — State layout and splitting strategy

**Scenario and constraints:** A platform has dev, staging and prod components with different change cadence and sensitivity. Keep the exercise local or diagram-only; no production mutations.

**Required deliverable:** Draw state ownership and dependency diagram; include backend, lock, backup and recovery boundaries.

**Model-answer outline:** State blast radius, least-privilege access, dependency trade-offs, migration plan, recovery drill and how to prevent two states owning one object.

**Common failure modes:** One state per everything without considering dependencies; split by arbitrary folders; no restore rehearsal.

**Evaluation rubric (10 points):**
- Correct architecture and ownership — 2
- Security and environment boundaries — 2
- Failure, rollback/recovery and blast-radius reasoning — 2
- Testable evidence and acceptance criteria — 2
- Trade-offs, limitations and exit path — 2

**Additional evidence/source verification required:** Installed backend/tool locking and versioning behavior; actual team access and recovery objectives.

### DR-02 — Workspace vs directory vs account/project isolation

**Scenario and constraints:** Teams suggest using workspaces alone to prevent prod access from dev. Keep the exercise local or diagram-only; no production mutations.

**Required deliverable:** Comparison table across selection, IAM identity, state access, blast radius, operator error and operational overhead.

**Model-answer outline:** Explain workspace convenience versus independent backend/account identity boundaries; choose controls per threat and verify target in CI.

**Common failure modes:** Treat workspace name as authorization; assume separate folders alone constrain cloud API.

**Evaluation rubric (10 points):**
- Correct architecture and ownership — 2
- Security and environment boundaries — 2
- Failure, rollback/recovery and blast-radius reasoning — 2
- Testable evidence and acceptance criteria — 2
- Trade-offs, limitations and exit path — 2

**Additional evidence/source verification required:** Cloud organization/account model, IAM capabilities and backend access model.

### DR-03 — Module versioning and consumer compatibility

**Scenario and constraints:** A module change fixes security defaults but changes an output. Keep the exercise local or diagram-only; no production mutations.

**Required deliverable:** Versioning and rollout diagram with consumer contract tests and changelog.

**Model-answer outline:** Define SemVer policy, compatibility window, pinned versions, staged rollout, deprecation and emergency patch process.

**Common failure modes:** Floating source references; breaking changes without migration; upgrade all environments at once.

**Evaluation rubric (10 points):**
- Correct architecture and ownership — 2
- Security and environment boundaries — 2
- Failure, rollback/recovery and blast-radius reasoning — 2
- Testable evidence and acceptance criteria — 2
- Trade-offs, limitations and exit path — 2

**Additional evidence/source verification required:** Installed IaC version, module source behavior and consumer dependency graph.

### DR-04 — Policy-layer design and exception governance

**Scenario and constraints:** Policy, IAM and CI approval all appear to enforce the same public-access rule. Keep the exercise local or diagram-only; no production mutations.

**Required deliverable:** Control matrix showing prevention/detection layer, input, authority, bypass and evidence.

**Model-answer outline:** Use policy-as-code for pre-apply checks, cloud IAM/org controls for API authorization, pipeline approvals for process, runtime detection for drift; govern narrow expiring exceptions.

**Common failure modes:** Assume policy pass equals compliance; fail-open; permanent wildcard exception.

**Evaluation rubric (10 points):**
- Correct architecture and ownership — 2
- Security and environment boundaries — 2
- Failure, rollback/recovery and blast-radius reasoning — 2
- Testable evidence and acceptance criteria — 2
- Trade-offs, limitations and exit path — 2

**Additional evidence/source verification required:** Policy engine/version, plan JSON schema, actual cloud organization controls.

### DR-05 — Quota governance and DR headroom

**Scenario and constraints:** A launch and a disaster-recovery test could compete for regional capacity. Keep the exercise local or diagram-only; no production mutations.

**Required deliverable:** Capacity table by service/region: current usage, planned delta, concurrency, recovery reserve and escalation owner.

**Model-answer outline:** Use sourced current quota evidence, time-bound preflight, rollout concurrency and explicit recovery headroom; never hard-code unverified universal limits.

**Common failure modes:** Plan count only; assume quota is global; consume all capacity.

**Evaluation rubric (10 points):**
- Correct architecture and ownership — 2
- Security and environment boundaries — 2
- Failure, rollback/recovery and blast-radius reasoning — 2
- Testable evidence and acceptance criteria — 2
- Trade-offs, limitations and exit path — 2

**Additional evidence/source verification required:** Actual quota/usage APIs, account and region scope, service-specific limit semantics.

### DR-06 — Decommission governance and orphan cleanup

**Scenario and constraints:** A janitor finds hundreds of old resources, some untagged. Keep the exercise local or diagram-only; no production mutations.

**Required deliverable:** State diagram from discovery to candidate report, owner review, retention check, approval, bounded deletion and evidence.

**Model-answer outline:** Inventory and ownership proof, retention/legal hold, dependencies, dry-run, deletion cap, protected exclusions and post-delete verification.

**Common failure modes:** Delete by age/tag alone; no approval or audit evidence.

**Evaluation rubric (10 points):**
- Correct architecture and ownership — 2
- Security and environment boundaries — 2
- Failure, rollback/recovery and blast-radius reasoning — 2
- Testable evidence and acceptance criteria — 2
- Trade-offs, limitations and exit path — 2

**Additional evidence/source verification required:** Resource inventory, ownership metadata, retention policy and deletion semantics.

### DR-07 — Terraform vs OpenTofu vs Pulumi

**Scenario and constraints:** The organization wants a tool change to improve developer experience. Keep the exercise local or diagram-only; no production mutations.

**Required deliverable:** Decision matrix and migration/exit plan.

**Model-answer outline:** Compare state and provider semantics, language, policy/testing ecosystem, team skills, governance, support and migration cost; rehearse with disposable state.

**Common failure modes:** Assume drop-in compatibility; ignore state and ownership.

**Evaluation rubric (10 points):**
- Correct architecture and ownership — 2
- Security and environment boundaries — 2
- Failure, rollback/recovery and blast-radius reasoning — 2
- Testable evidence and acceptance criteria — 2
- Trade-offs, limitations and exit path — 2

**Additional evidence/source verification required:** Specific installed versions, provider support, supported state migration path.

### DR-08 — Ansible vs immutable images

**Scenario and constraints:** Hosts are repeatedly modified after deployment and drift reappears. Keep the exercise local or diagram-only; no production mutations.

**Required deliverable:** Decision tree assigning each configuration surface to image build, Ansible convergence or controller.

**Model-answer outline:** Choose based on lifecycle, mutable state, rollout, drift and recovery; keep idempotent playbooks and bounded `serial` when Ansible is appropriate.

**Common failure modes:** Disable host verification; broad sudo; make multiple controllers fight over same setting.

**Evaluation rubric (10 points):**
- Correct architecture and ownership — 2
- Security and environment boundaries — 2
- Failure, rollback/recovery and blast-radius reasoning — 2
- Testable evidence and acceptance criteria — 2
- Trade-offs, limitations and exit path — 2

**Additional evidence/source verification required:** Ansible/module check-mode behavior, image pipeline and workload architecture.

### DR-09 — Crossplane adoption and ownership boundaries

**Scenario and constraints:** A team wants Crossplane for a resource Terraform already manages. Keep the exercise local or diagram-only; no production mutations.

**Required deliverable:** Ownership map for external resource, state, XR/claim, provider identity, deletion semantics and exit path.

**Model-answer outline:** Use one authoritative owner; plan adoption/import or cutover; verify CRDs/provider schema, RBAC, credentials, Delete/Orphan behavior, backup and rate limits.

**Common failure modes:** Dual management; assume claim deletion behavior; overbroad provider credentials.

**Evaluation rubric (10 points):**
- Correct architecture and ownership — 2
- Security and environment boundaries — 2
- Failure, rollback/recovery and blast-radius reasoning — 2
- Testable evidence and acceptance criteria — 2
- Trade-offs, limitations and exit path — 2

**Additional evidence/source verification required:** Crossplane/provider package versions, API groups, composition mechanism, management policies and backup procedures.

### DR-10 — Change-approval design

**Scenario and constraints:** An automated plan risk analyzer flags replacements but teams complain approvals are slow. Keep the exercise local or diagram-only; no production mutations.

**Required deliverable:** Pipeline sequence from validate/policy/plan/risk analysis to approval, exact artifact application and post-apply checks.

**Model-answer outline:** Define risk thresholds, human accountability, evidence retention, artifact integrity, exception process, concurrency and rollback criteria; test analyzer on crafted plans.

**Common failure modes:** Auto-approve every low score; apply regenerated plan; treat risk score as proof.

**Evaluation rubric (10 points):**
- Correct architecture and ownership — 2
- Security and environment boundaries — 2
- Failure, rollback/recovery and blast-radius reasoning — 2
- Testable evidence and acceptance criteria — 2
- Trade-offs, limitations and exit path — 2

**Additional evidence/source verification required:** CI platform approval and artifact controls, IaC plan semantics and analyzer test corpus.

## Capstone readiness checkpoint — Governed Multi-Environment Data Platform Infrastructure

**Source basis:** The syllabus prompt’s Unit 14 capstone section describes a data/ML team with laptop-built infrastructure, local state, shared dev/prod configuration, a publicly exposed bucket, quota exhaustion, long-lived temporary resources, and a destroy targeting the wrong environment. The checkpoint below maps to deliverables explicitly visible in the retrieved capstone source; it does not claim to inspect a separate project specification file.

| Checkpoint | Evidence to submit | Acceptance question |
|---|---|---|
| Multi-environment layout and state | `live/{dev,staging,prod}/...`, per-environment backend configuration, bootstrap guard, versions inventory | Can a wrong environment/profile/endpoint fail closed? Is state separated and access-controlled? |
| State recovery and locking | Recovery drill evidence, backup/versioning notes, lock recovery runbook | Can the learner restore a known-good state version and show a clean reviewed plan? Are lock semantics documented for the installed version? |
| Reusable modules and upgrade safety | Storage module, queue/topic or equivalent, environment module, typed/validated inputs, changelog and pinned versions | Do modules include security defaults and contract tests? Is a breaking upgrade tested before production rollout? |
| Safe plans and approval | CI workflow or local runner, risk analyzer, crafted plans, saved-plan artifact controls | Does the workflow analyze and approve the same artifact it applies, then verify the result? |
| Policy and boundaries | Policy tests, boundary assertions, simulated-vs-real fidelity table, ADR | Are public access and environment boundaries checked? Does the learner distinguish policy from cloud IAM? |
| Drift and test strategy | Drift evidence, native/static/plan tests, integration tests where appropriate | Are drift and negative cases tested without overstating LocalStack fidelity? |
| Quota preflight | Current scoped quota evidence or clearly labelled local simulation, headroom calculation, escalation runbook | Does it account for existing use, concurrency and DR/rollback capacity without inventing values? |
| Secrets and identity | Secret-handling review, least-privilege identity configuration, exposure response plan | Are secrets absent from Git and access-controlled in state/plan/logs/artifacts? Is rotation covered after exposure? |
| Decommission and orphan cleanup | Candidate inventory, dry-run, retention/owner review, deletion caps, evidence | Is deletion authorized by ownership and retention evidence rather than age/tag alone? |
| Recovery and audit trail | Before/after evidence, runbooks, target identity and decision records | Can a reviewer reconstruct what changed, where, why and how recovery was assessed? |
| Optional Crossplane track | Only if included: provider/XRD/Composition evidence, deletion-semantics lab, decision memo | Are API/provider versions verified, ownership singular, credentials scoped, and restore/exit path documented? |

**Capstone readiness decision:** proceed only when every required deliverable in the authoritative capstone spec has inspectable evidence and all safety-critical negative tests pass. Do not infer acceptance from a README, a green CI badge, or a successful LocalStack run alone. The full source capstone spec should be checked for any additional numbered deliverables beyond those visible in the retrieved excerpt.

## Coverage and count audit

The audit counts question IDs, not subparts, options, rubric bullets or whiteboard prompts. Unit sections contain the required 3 short answers, 3 MCQs, 2 output interpretations, 2 code reviews, 1 incident and 1 design question each.

| Section | Required count | Actual count | IDs covered | Result |
|---|---:|---:|---|---|
| Unit 1 | 12 | 12 | U01-SA-01–03; U01-MCQ-01–03; U01-OUT-01–02; U01-REV-01–02; U01-INC-01; U01-DES-01 | PASS |
| Unit 2 | 12 | 12 | U02-SA-01–03; U02-MCQ-01–03; U02-OUT-01–02; U02-REV-01–02; U02-INC-01; U02-DES-01 | PASS |
| Unit 3 | 12 | 12 | U03-SA-01–03; U03-MCQ-01–03; U03-OUT-01–02; U03-REV-01–02; U03-INC-01; U03-DES-01 | PASS |
| Unit 4 | 12 | 12 | U04-SA-01–03; U04-MCQ-01–03; U04-OUT-01–02; U04-REV-01–02; U04-INC-01; U04-DES-01 | PASS |
| Unit 5 | 12 | 12 | U05-SA-01–03; U05-MCQ-01–03; U05-OUT-01–02; U05-REV-01–02; U05-INC-01; U05-DES-01 | PASS |
| Unit 6 | 12 | 12 | U06-SA-01–03; U06-MCQ-01–03; U06-OUT-01–02; U06-REV-01–02; U06-INC-01; U06-DES-01 | PASS |
| Unit 7 | 12 | 12 | U07-SA-01–03; U07-MCQ-01–03; U07-OUT-01–02; U07-REV-01–02; U07-INC-01; U07-DES-01 | PASS |
| Unit 8 | 12 | 12 | U08-SA-01–03; U08-MCQ-01–03; U08-OUT-01–02; U08-REV-01–02; U08-INC-01; U08-DES-01 | PASS |
| Unit 9 | 12 | 12 | U09-SA-01–03; U09-MCQ-01–03; U09-OUT-01–02; U09-REV-01–02; U09-INC-01; U09-DES-01 | PASS |
| Unit 10 | 12 | 12 | U10-SA-01–03; U10-MCQ-01–03; U10-OUT-01–02; U10-REV-01–02; U10-INC-01; U10-DES-01 | PASS |
| Unit 11 | 12 | 12 | U11-SA-01–03; U11-MCQ-01–03; U11-OUT-01–02; U11-REV-01–02; U11-INC-01; U11-DES-01 | PASS |
| Unit 12 | 12 | 12 | U12-SA-01–03; U12-MCQ-01–03; U12-OUT-01–02; U12-REV-01–02; U12-INC-01; U12-DES-01 | PASS |
| Cross-unit scenarios | 30 | 30 | X-001–X-030 | PASS |
| Whiteboard design-review prompts | exactly 10 (separate) | 10 | DR-01–DR-10 | PASS |
| **Total explicitly identified questions** | **≥170** | **174** | **144 unit + 30 cross-unit** | **PASS** |

## Ten-pass authenticity audit

| Pass | Result (PASS/FIXED/OPEN) | Defects found | Fixes applied | Residual risk |
|---|---|---|---|---|
| 1 — Count and distribution | PASS | Risk of under-counting subparts or omitting a unit category | Counted explicit IDs by required type: 12 per unit and 30 cross-unit | Counts are mechanically checkable; substantive coverage still requires reviewer judgment |
| 2 — Source fidelity | OPEN | Actual repository tree, all individual lesson files, and standalone capstone project file were not available for independent inspection | Grounded scope in uploaded prompt’s unit checklist and retrieved authoritative syllabus/capstone sections; limitation disclosed | Must compare against actual lesson files and full capstone before treating as final repository acceptance |
| 3 — Technical accuracy | FIXED | Version-sensitive syntax and provider semantics could be mistaken for universal behavior | Used illustrative outputs; added `[VERIFY]`/`[VERSION-SENSITIVE]` notes where appropriate; avoided asserting specific quotas or tool versions | No end-to-end tool execution or external provider validation performed |
| 4 — Answer-key completeness | PASS | MCQ distractors, code review fixes and design rubrics are common omission points | Every MCQ has four options and per-option analysis; each review question lists at least three defects/corrections; each design rubric totals 20 | A technical reviewer should validate nuance against exact lesson examples |
| 5 — Safety and security | FIXED | Potential for blind retries, target mismatch, secret exposure, or destructive cleanup to be normalized | Answers require target/identity checks, containment, evidence, rollback assessment, least privilege, retention and bounded deletion | Operational approval policies vary by organization; production actions remain out of scope |
| 6 — Version/source authenticity | OPEN | Exact installed tool/provider versions are unknown; actual lesson citations and schemas unavailable | Marked version-sensitive behavior and avoided fabricated versions, quotas, prices and command outputs | Must verify installed Terraform/OpenTofu, Ansible, Terratest and Crossplane/provider documentation before lab use |
| 7 — Pedagogical progression | PASS | Advanced topics could be presented without a foundation | Each unit progresses from L1/L2 concepts to L3 output/review and L4 incident/design | Facilitator may need to adjust timing for learner experience |
| 8 — Cross-unit consistency | PASS | State, policy, account boundaries, tests, cleanup and controller ownership can be contradictory if treated in isolation | Repeated consistent principles: one owner per external object, exact target identity, policy is not IAM, emulator fidelity is bounded | Exact implementation semantics remain version/provider dependent |
| 9 — Adversarial review | FIXED | A learner could infer that green checks, `sensitive`, `no_log`, `Ready`, or a dry-run proves complete safety | Added explicit limitations and incident responses for state/plan/log persistence, conditions, deletion and policy coverage | Must still review against the organization’s secret handling and incident policies |
| 10 — Final file/scope audit | OPEN | Repository-wide status/diff and target repository path could not be inspected; only standalone output could be written in this session | Created only `/mnt/data/practice-questions.md` as a standalone artifact; performed mechanical ID/type/code-fence checks after generation | **Repository-wide change scope could not be independently verified; this authoring instruction requires modification of only the target file.** The repository target was not written because repository editing was unavailable. |

## Source and verification notes

- **Inspected:** uploaded prompt `Pasted markdown(20261028-061918).md`; Library source `PROMPT-Advanced-Infrastructure-as-Code-and-Cloud-Operations.md` (including retrieved Unit 13 requirements and Unit 14 capstone section).
- **Not independently inspected:** actual `Roadmap_ptree.md`, individual Unit 1–12 lesson files, `Projects/README.md`, and `Projects/01-governed-multi-environment-data-platform-infrastructure.md`.
- **Not executed:** no Terraform/OpenTofu, Ansible, Terratest, LocalStack, kind, Kubernetes, Crossplane, or cloud command was run for this assessment. All sample outputs are illustrative.
- **Repository status:** repository-wide change scope could not be independently verified; this authoring instruction requires modification of only the target file. This artifact was written to `/mnt/data/practice-questions.md`, not into the repository folder.

## Final learner checklist

Before marking the module complete, verify that you can consistently: (1) prove target identity and backend before state-changing work; (2) distinguish plan/policy/test evidence from runtime guarantees; (3) find secret persistence surfaces and rotate after exposure; (4) establish one owner for each external object; (5) evaluate destructive actions against retention, dependencies and recovery; (6) account for quota, concurrency and recovery headroom; (7) explain emulator and version limitations; (8) preserve evidence and execute a tested recovery runbook; and (9) show negative tests that fail closed on the safety-critical cases.
