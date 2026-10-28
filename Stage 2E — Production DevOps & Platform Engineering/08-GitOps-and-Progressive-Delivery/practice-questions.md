# M08 Practice Questions — GitOps and Progressive Delivery

> **Assessment status:** source-aligned practice bank for M08 Units 1–13. All command output and fictional service data in this file are `SIMULATED / REPRESENTATIVE` unless a question explicitly says otherwise. Flawed examples are labelled `INTENTIONALLY FLAWED`. This is an instructional assessment, not a compliance certification.

## Purpose, scope, prerequisites, and how to use this bank

This bank assesses the 13-unit M08 curriculum from beginner foundations (L1) through production engineering and advanced operational judgment (L4). It is answer-rich by design: attempt each prompt before opening its answer. Use a disposable environment only; do not run snippets against production. The primary examples use the fictional `orders-api` service, synthetic commit IDs, and placeholder artifact digests.

**Prerequisites:** Git, shell and YAML/JSON reading, basic Kubernetes workloads and Services, CI/CD vocabulary, and the M08 unit lessons. You can answer the evidence and design questions without a live cluster. Product-specific CLI/CRD behavior marked `[VERIFY]` must be checked against the installed version.

**Source fidelity:** The supplied roadmap snapshot is `Roadmap(9).md`, not a file literally named `Roadmap_ptree.md`; the inspected snapshot lists the requested `08-GitOps-and-Progressive-Delivery/` directory and the capstone path. The uploaded prompt notes that an older tree may use `03-GitOps-and-Progressive-Delivery/`; that older name was not present in the inspected snapshot. The syllabus prompt is the curriculum authority. Unit 1 and Unit 2 lesson files are available in the workspace but currently sit outside the target directory; their intended relative paths are confirmed by the roadmap tree. The capstone project path is listed in the tree but its project file was not available in the inspected target folder. No lesson completion or lab execution is assumed.

## Curriculum map: Units 1–13

| Unit | Title | Main outcome |
|---|---|---|
| 1 | GitOps principles and desired-state reconciliation | Distinguish desired state from live state and explain a reconciliation loop. [Lesson](<01-gitops-principles-and-desired-state-reconciliation.md>) |
| 2 | Argo CD: applications, projects, and sync policies | Trace an application from source revision through render, diff, sync, and live state. [Lesson](<02-argo-cd-applications-projects-and-sync-policies.md>) |
| 3 | Flux controllers and Kustomize/Helm reconciliation | Identify Flux source, Kustomize, Helm, and notification-controller responsibilities. [Lesson](<03-flux-controllers-and-kustomize-helm-reconciliation.md>) |
| 4 | Repository layout and multi-environment promotion | Compare repository and environment promotion patterns. [Lesson](<04-repository-layout-and-multi-environment-promotion.md>) |
| 5 | Configuration and secret reference management | Distinguish configuration values from secret material and secret references. [Lesson](<05-configuration-and-secret-reference-management.md>) |
| 6 | Deployment drift detection and reconciliation | Distinguish unauthorized drift from expected mutation/defaulting. [Lesson](<06-deployment-drift-detection-and-reconciliation.md>) |
| 7 | Progressive delivery: canary and blue-green releases | Choose delivery strategies based on traffic, state, and recovery constraints. [Lesson](<07-progressive-delivery-with-canary-and-blue-green-releases.md>) |
| 8 | Argo Rollouts, Flagger, and traffic-based analysis | Distinguish rollout-controller roles from Kubernetes Deployment mechanics. [Lesson](<08-argo-rollouts-flagger-and-traffic-based-analysis.md>) |
| 9 | Release health analysis and automated abort | Evaluate rollout health using infrastructure and business SLIs. [Lesson](<09-release-health-analysis-and-automated-abort.md>) |
| 10 | Feature flags and dark launches | Separate deployment state from feature exposure. [Lesson](<10-feature-flags-and-dark-launches.md>) |
| 11 | Database and data-platform migration safety | Sequence schema and application changes for compatibility. [Lesson](<11-database-and-data-platform-migration-safety.md>) |
| 12 | Backward-compatible pipeline and API releases | Classify backward/forward/breaking and semantic changes. [Lesson](<12-backward-compatible-pipeline-and-api-releases.md>) |
| 13 | Release evidence and audit trails | Distinguish audit trail, release evidence, observability, provenance, and attestation. [Lesson](<13-release-evidence-and-audit-trails.md>) |

## Assessment rules, IDs, levels, and scoring

Each unit has exactly 12 core questions in the required mix: 3 conceptual, 3 MCQs, 2 output interpretation, 2 configuration/manifest reviews, 1 incident, and 1 design. Cross-unit scenarios use `XINT-01` onward; additional whiteboard prompts use `DESIGN-01` onward. Every question has a model answer, reasoning, common mistakes, caveat, and scoring criteria. MCQs explain all four options. Each manifest review contains at least three distinct defects and a corrected direction/snippet.

**Levels:** L1 foundations; L2 practical implementation; L3 production engineering; L4 advanced operational judgment.

**Scoring thresholds (syllabus):** **80% or higher:** proceed to the next stage/capstone checkpoint. **60%–79%:** remediate weak objectives and retest those topics. **Below 60%:** repeat the relevant unit review and practical exercises before retesting. A **critical-safety override** applies regardless of aggregate score if a learner repeatedly recommends leaking secrets, skipping backup/compatibility checks for destructive migrations, treating missing metrics as healthy, using mutable tags as artifact proof, or making production changes without blast-radius/rollback analysis. This is an instructional rubric, not a formal certification.

# Unit 1 — GitOps principles and desired-state reconciliation (12 questions)

### U01-Q01 — Explain the core model for declarative state, pull-based reconciliation, drift, and trust bound

- **Unit / topic:** GitOps principles and desired-state reconciliation
- **Level:** L1
- **Question type:** conceptual
- **Objective tested:** distinguish desired state from live state and explain a reconciliation loop
- **Estimated time:** 6 minutes

**Question / scenario**

Explain the core model for declarative state, pull-based reconciliation, drift, and trust boundaries. In your answer, distinguish the desired configuration, the controller or process that acts on it, and the evidence that shows whether the intended outcome actually occurred.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Git is the reviewed source of desired state; a controller repeatedly observes desired and actual state and attempts convergence. Convergence is not proof of application correctness.

**Reasoning**

Desired state, observed live state, and reconciliation outcome are separate facts. Compare the declared revision and policy with live resources, then verify the service outcome; no single controller status proves the whole system correct.

**Common wrong answers**

- **Assume convergence is guaranteed** A controller can be unavailable, unauthorized, or blocked; verify its observed revision and live state.
- **Treat live state as the source of truth** Live state may contain drift or an emergency change that still needs classification and reconciliation.

**Operational caveat**

Controller defaults and reconciliation semantics differ. Verify the installed policy and test sync/prune behavior in a disposable environment.

**Scoring rubric**

Full credit (3 points): states the core mechanism accurately (1), distinguishes what the evidence does and does not prove (1), and identifies a safe next check or operational implication (1).

</details>

---

### U01-Q02 — Predict self-heal behavior when auto-sync is disabled

- **Unit / topic:** — GitOps principles and desired-state reconciliation
- **Level:** — L2
- **Question type:** — conceptual
- **Objective tested:** — predict and verify predict self-heal behavior when auto-sync is disabled
- **Estimated time:** — 7 minutes

**Question / scenario**

Predict controller behavior when Git declares three replicas but the live Deployment has five. The controller reports drift; self-heal is enabled but automated sync is disabled. What can you conclude now, and what changes after an authorized sync?

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Git is the declared intent and the five-replica Deployment is the observed state. Drift is detected, but with automated sync disabled the controller may not apply the correction until a sync is initiated. After an authorized sync, the live replica count should converge toward three, assuming no competing writer or admission mutation. Confirm the controller’s actual policy/version and inspect the diff before acting.

**Reasoning**

Predict reconciliation from explicit policy; distinguish detection from remediation and state what remains uncertain.

**Common wrong answers**

- **Assume convergence is guaranteed** — A controller can be unavailable, unauthorized, or blocked; verify its observed revision and live state.
- **Treat live state as the source of truth** — Live state may contain drift or an emergency change that still needs classification and reconciliation.

**Operational caveat**

Self-heal/auto-sync semantics differ by controller and configuration. Verify the installed policy, prune behavior, and live diff; preserve incident evidence before overwriting unexpected changes.

**Scoring rubric**

Full credit (3 points): states the correct operational conclusion (1), cites the evidence/policy that supports it (1), and names a safe next check plus a remaining uncertainty (1).

</details>

---

### U01-Q03 — Recover safely after controller unavailability

- **Unit / topic:** — GitOps principles and desired-state reconciliation
- **Level:** — L3
- **Question type:** — conceptual
- **Objective tested:** — diagnose and recover safely from recover safely after controller unavailability
- **Estimated time:** — 8 minutes

**Question / scenario**

The Git repository changes while the GitOps controller is unavailable. Explain what is known, what is not yet known, and the safest recovery sequence once the controller returns.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Only the reviewed desired-state change is known from Git. Until reconciliation resumes and runtime is inspected, do not claim the cluster has converged. Record the commit and approval, inspect the controller’s source revision and health, compare rendered desired state with live resources, assess blast radius, then sync through the approved path and verify workload plus business health.

**Reasoning**

Separate desired state, controller observation, applied state, and application outcome. A successful Git commit is not proof that the cluster received or successfully ran the change.

**Common wrong answers**

- **Assume convergence is guaranteed** — A controller can be unavailable, unauthorized, or blocked; verify its observed revision and live state.
- **Treat live state as the source of truth** — Live state may contain drift or an emergency change that still needs classification and reconciliation.

**Operational caveat**

Controller outages can leave stale or partially applied state. Confirm the last observed revision and live resources, and avoid destructive pruning until ownership and recovery are understood.

**Scoring rubric**

Full credit (4 points): identifies the relevant state/evidence (1), orders diagnosis before mutation (1), checks blast radius and rollback/data compatibility (1), and defines verification/prevention (1).

</details>

---

### U01-Q04 — A controller repeatedly restores a Git-declared replica count after a manual edit. Which explan

- **Unit / topic:** GitOps principles and desired-state reconciliation
- **Level:** L1
- **Question type:** MCQ
- **Objective tested:** distinguish desired state from live state and explain a reconciliation loop
- **Estimated time:** 3 minutes

**Question / scenario**

A controller repeatedly restores a Git-declared replica count after a manual edit. Which explanation is best?

A. The API server always rejects manual edits to Deployments
B. The reconciliation controller is converging live state toward its declared desired state
C. The image digest is invalid by definition
D. Git automatically changes the live cluster without a controller

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**B**. The reconciliation controller is converging live state toward its declared desired state

**Reasoning**

- **A. Incorrect.** The option proposes “The API server always rejects manual edits to Deployments”; it makes a universal guarantee that the evidence does not support; controller and provider behavior depends on explicit policy, version, and observed state.
- **B. Correct.** Reconciliation explains the observed correction; API admission is not the only reason a manual edit can disappear.
- **C. Incorrect.** The option proposes “The image digest is invalid by definition”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.
- **D. Incorrect.** The option proposes “Git automatically changes the live cluster without a controller”; Git records intent and review context but does not by itself prove what the cluster ran or that every required approval/promotion record exists.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses assume convergence is guaranteed with verified state, or skips the required safety check: A controller can be unavailable, unauthorized, or blocked; verify its observed revision and live state.

**Operational caveat**

Controller defaults and reconciliation semantics differ. Verify the installed policy and test sync/prune behavior in a disposable environment.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U01-Q05 — Which statement best describes the CI/GitOps boundary?

- **Unit / topic:** GitOps principles and desired-state reconciliation
- **Level:** L2
- **Question type:** MCQ
- **Objective tested:** compare pull-based GitOps with push-based deployment and identify credential/blast-radius differences
- **Estimated time:** 3 minutes

**Question / scenario**

Which statement best describes the CI/GitOps boundary?

A. CI should always hold cluster-admin credentials
B. CI can build, test, sign and propose a digest update; the in-cluster controller deploys reviewed desired state
C. The GitOps controller must rebuild application source
D. A successful sync proves business correctness

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**B**. CI can build, test, sign and propose a digest update; the in-cluster controller deploys reviewed desired state

**Reasoning**

- **A. Incorrect.** The option proposes “CI should always hold cluster-admin credentials”; it makes a universal guarantee that the evidence does not support; controller and provider behavior depends on explicit policy, version, and observed state.
- **B. Correct.** Separating artifact production from deployment can reduce CI credential exposure; runtime correctness still needs independent checks.
- **C. Incorrect.** The option proposes “The GitOps controller must rebuild application source”; Git records intent and review context but does not by itself prove what the cluster ran or that every required approval/promotion record exists.
- **D. Incorrect.** The option proposes “A successful sync proves business correctness”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses assume convergence is guaranteed with verified state, or skips the required safety check: A controller can be unavailable, unauthorized, or blocked; verify its observed revision and live state.

**Operational caveat**

Controller defaults and reconciliation semantics differ. Verify the installed policy and test sync/prune behavior in a disposable environment.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U01-Q06 — Git declares resource X absent, and the live resource exists. Which outcome is justified?

- **Unit / topic:** GitOps principles and desired-state reconciliation
- **Level:** L3
- **Question type:** MCQ
- **Objective tested:** predict controller behavior from Git, live state, and explicit sync/prune/self-heal policy
- **Estimated time:** 3 minutes

**Question / scenario**

Git declares resource X absent, and the live resource exists. Which outcome is justified?

A. It is always deleted immediately
B. It is never deleted by any GitOps controller
C. Outcome depends on explicit pruning/deletion policy and controller semantics
D. The controller must convert it to a Secret

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**C**. Outcome depends on explicit pruning/deletion policy and controller semantics

**Reasoning**

- **A. Incorrect.** The option proposes “It is always deleted immediately”; it makes a universal guarantee that the evidence does not support; controller and provider behavior depends on explicit policy, version, and observed state.
- **B. Incorrect.** The option proposes “It is never deleted by any GitOps controller”; it makes a universal guarantee that the evidence does not support; controller and provider behavior depends on explicit policy, version, and observed state.
- **C. Correct.** Deletion semantics are policy- and controller-dependent; verify the installed version and resource ownership before enabling prune.
- **D. Incorrect.** The option proposes “The controller must convert it to a Secret”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses assume convergence is guaranteed with verified state, or skips the required safety check: A controller can be unavailable, unauthorized, or blocked; verify its observed revision and live state.

**Operational caveat**

Controller defaults and reconciliation semantics differ. Verify the installed policy and test sync/prune behavior in a disposable environment.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U01-Q07 — Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for GitOps principles and desi

- **Unit / topic:** GitOps principles and desired-state reconciliation
- **Level:** L2
- **Question type:** output interpretation
- **Objective tested:** distinguish desired state from live state and explain a reconciliation loop
- **Estimated time:** 7 minutes

**Question / scenario**

Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for GitOps principles and desired-state reconciliation:

```text
SIMULATED / REPRESENTATIVE
Git desired image: registry.example.invalid/orders-api@sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
Live image:        registry.example.invalid/orders-api@sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
Controller:        healthy; auto-sync enabled; self-heal enabled; prune disabled
Observed status:   OutOfSync → Synced after reconciliation
```

Predict the controller outcome from the explicit Git/live state and the stated auto-sync, self-heal, and prune policies. State whether digest B is restored to A, whether unrelated absent resources are pruned, what remains unknown, and which business-level check is still needed. Cite the exact fields/lines above.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Git declares digest A while live state shows digest B. Because self-heal and auto-sync are enabled, the controller is expected to attempt to restore A; `prune disabled` means this excerpt does not justify deleting unrelated resources. The transition `OutOfSync → Synced` is consistent with reconciliation, but the business error rate remains elevated, so do not conclude the service is healthy. Preserve the patch/actor/event evidence, check whether A is the approved release, and investigate the business regression before any further promotion.

**Reasoning**

Output interpretation must separate observations from inference. A status or event can be stale, partial, or scoped to a single resource; the next check should target the earliest missing/failed link and preserve the current evidence.

**Common wrong answers**

- **Assume the best because one field is green.** That ignores contradictory fields and coverage gaps.
- **Mutate immediately.** Diagnose source, identity, scope, and rollback safety first unless containment urgency requires a minimal authorized action.

**Operational caveat**

All output is simulated; it is not claimed to come from a live cluster. Exact CLI output and controller status wording are `[VERIFY]` for the installed version.

**Scoring rubric**

Full credit: cite two specific fields, identify one unknown, choose a safe next action, and explain promotion/rollback constraints (4 points).

</details>

---

### U01-Q08 — Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for GitOps principles and desi

- **Unit / topic:** GitOps principles and desired-state reconciliation
- **Level:** L3
- **Question type:** output interpretation
- **Objective tested:** compare pull-based GitOps with push-based deployment and identify credential/blast-radius differences
- **Estimated time:** 8 minutes

**Question / scenario**

Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for GitOps principles and desired-state reconciliation:

```text
SIMULATED / REPRESENTATIVE
09:00Z commit config-repo@cafe123 updates orders-api digest A
09:02Z controller applies digest A
09:08Z operator patches live Deployment to digest B
09:10Z controller detects drift and restores digest A
09:11Z application health reports Healthy; business error rate remains elevated
```

State what is established, what remains unknown, the safest next diagnostic step, and whether you would promote, reconcile, pause, abort, or gather more evidence. Justify the decision using specific fields/lines above.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The timeline shows the operator changed the live image at 09:08Z and the controller restored digest A at 09:10Z. At 09:11Z resource health is Healthy while the business error rate is still elevated. This proves the control plane converged, not that the hotfix was unnecessary or the application is correct. Correlate the incident, image digests, request-level/business metrics, and the authorization record; if the hotfix is warranted, reconcile it through the approved emergency Git path.

**Reasoning**

Output interpretation must separate observations from inference. A status or event can be stale, partial, or scoped to a single resource; the next check should target the earliest missing/failed link and preserve the current evidence.

**Common wrong answers**

- **Assume the best because one field is green.** That ignores contradictory fields and coverage gaps.
- **Mutate immediately.** Diagnose source, identity, scope, and rollback safety first unless containment urgency requires a minimal authorized action.

**Operational caveat**

All output is simulated; it is not claimed to come from a live cluster. Exact CLI output and controller status wording are `[VERIFY]` for the installed version.

**Scoring rubric**

Full credit: cite two specific fields, identify one unknown, choose a safe next action, and explain promotion/rollback constraints (4 points).

</details>

---

### U01-Q09 — Review this `INTENTIONALLY FLAWED` example for GitOps principles and desired-state reconciliati

- **Unit / topic:** GitOps principles and desired-state reconciliation
- **Level:** L3
- **Question type:** configuration/manifest review
- **Objective tested:** distinguish desired state from live state and explain a reconciliation loop
- **Estimated time:** 10 minutes

**Question / scenario**

Review this `INTENTIONALLY FLAWED` example for GitOps principles and desired-state reconciliation. Identify at least three distinct defects, explain their operational impact, and propose a corrected version or exact correction.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: orders-api
spec:
  replicas: 3
  selector:
    matchLabels: {app: orders-api}
  template:
    metadata:
      labels: {app: wrong-label}
    spec:
      containers:
      - name: api
        image: registry.example.invalid/orders-api:latest
```

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The defects are:

1. The pod-template label is `wrong-label` while the Deployment selector expects `app=orders-api`, so the Deployment cannot manage matching Pods correctly.
2. The image uses mutable `:latest`, so the manifest does not pin tested artifact bytes.
3. There is no explicit provenance/release metadata or statement of how the digest was verified.

**Corrected direction/snippet:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: orders-api
  labels:
    app.kubernetes.io/name: orders-api
spec:
  replicas: 3
  selector:
    matchLabels: {app: orders-api}
  template:
    metadata:
      labels: {app: orders-api}
    spec:
      containers:
      - name: api
        image: registry.example.invalid/orders-api@sha256:REPLACE_WITH_REAL_DIGEST
```

The correction is an instructional pattern; confirm product-specific schema and provider support before applying it.

**Reasoning**

The defects are not merely style issues: they can make resources fail to select, weaken access boundaries, make the artifact mutable, trigger unintended deletion, leak sensitive data, or convert missing evidence into an unsafe action. Corrections must be tested in a disposable environment.

**Common wrong answers**

- **Fix only syntax.** A valid manifest can still be insecure or semantically unsafe.
- **Assume an illustrative snippet is a complete deployable CRD.** Required fields and semantics depend on the installed API/version.

**Operational caveat**

The original is intentionally flawed and must not be applied. Corrected snippets may be bounded examples rather than complete production configuration; `[VERIFY]` any controller-specific fields.

**Scoring rubric**

Full credit: at least three distinct defects (3 points), impact for each (3), corrected snippet/direction (2), version/safety caveat (2).

</details>

---

### U01-Q10 — Review this `INTENTIONALLY FLAWED` example for GitOps principles and desired-state reconciliati

- **Unit / topic:** GitOps principles and desired-state reconciliation
- **Level:** L3
- **Question type:** configuration/manifest review
- **Objective tested:** compare pull-based GitOps with push-based deployment and identify credential/blast-radius differences
- **Estimated time:** 10 minutes

**Question / scenario**

Review this `INTENTIONALLY FLAWED` example for GitOps principles and desired-state reconciliation. Identify at least three distinct defects, explain their operational impact, and propose a corrected version or exact correction.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-settings
data:
  desired-replicas: "3"
  production-password: "DO_NOT_USE_REAL_SECRET"
  deployment-mode: manual-hotfix-only
```

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The defects are:

1. The ConfigMap contains a password-like secret value, which should not be stored in plaintext configuration.
2. The `manual-hotfix-only` mode contradicts a reviewed desired-state workflow and invites out-of-band changes.
3. The snippet has no owner/context or validation policy for the setting; use a controlled configuration value and a secret reference.

**Corrected direction/snippet:**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-settings
data:
  desired-replicas: "3"
  deployment-mode: git-reviewed
# Store secret material in an approved secret manager; commit references, not values.
```

The correction is an instructional pattern; confirm product-specific schema and provider support before applying it.

**Reasoning**

The defects are not merely style issues: they can make resources fail to select, weaken access boundaries, make the artifact mutable, trigger unintended deletion, leak sensitive data, or convert missing evidence into an unsafe action. Corrections must be tested in a disposable environment.

**Common wrong answers**

- **Fix only syntax.** A valid manifest can still be insecure or semantically unsafe.
- **Assume an illustrative snippet is a complete deployable CRD.** Required fields and semantics depend on the installed API/version.

**Operational caveat**

The original is intentionally flawed and must not be applied. Corrected snippets may be bounded examples rather than complete production configuration; `[VERIFY]` any controller-specific fields.

**Scoring rubric**

Full credit: at least three distinct defects (3 points), impact for each (3), corrected snippet/direction (2), version/safety caveat (2).

</details>

---

### U01-Q11 — Incident: An operator manually changes the `orders-api` Deployment image in production while Gi

- **Unit / topic:** GitOps principles and desired-state reconciliation
- **Level:** L4
- **Question type:** incident/troubleshooting
- **Objective tested:** predict controller behavior from Git, live state, and explicit sync/prune/self-heal policy
- **Estimated time:** 15 minutes

**Question / scenario**

Incident: An operator manually changes the `orders-api` Deployment image in production while Git still declares the prior digest. The controller is configured to self-heal. The change disappears during the next reconciliation.

Provide symptom → diagnosis → evidence to preserve → blast-radius and rollback-safety check → containment/recovery → prevention. Identify one residual uncertainty that must not be presented as fact.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**Symptom:** An operator manually changes the `orders-api` Deployment image in production while Git still declares the prior digest. The controller is configured to self-heal. The change disappears during the next reconciliation.

**Diagnosis:** Git is the reviewed source of desired state; a controller repeatedly observes desired and actual state and attempts convergence. Convergence is not proof of application correctness.

**Evidence:** collect the relevant Git revision/PR, controller conditions/events, live resource state, runtime/metric samples, timestamps, and actor/approval data as applicable.

**Blast radius and rollback:** identify affected environments/replicas/consumers, determine whether state/data/external side effects changed, and test whether the prior version can safely read current state. Do not assume an image rollback reverses data.

**Containment/recovery:** use the smallest authorized reversible action; pause promotion or isolate the affected path if warranted; preserve a before/after record; reconcile the intended fix into the declared source; verify customer-facing behavior.

**Prevention:** A manual hotfix can be overwritten when the controller restores declared state. Preserve incident evidence, decide whether the change is justified, reconcile the fix into Git, and verify convergence.

**Residual uncertainty:** any missing history, unknown consumer behavior, unparseable runtime identity, or absent metric sample remains UNKNOWN until corroborated.

**Reasoning**

The incident response separates preserving evidence from containment, makes recovery contingent on state compatibility, and verifies both control-plane convergence and application-level outcome.

**Common wrong answers**

- **Immediately force-sync/redeploy without preserving evidence.** This can erase the live state that explains the incident.
- **Assume rollback is safe because the previous artifact exists.** Data, schema, event, or external side effects may be incompatible.

**Operational caveat**

Escalate to the incident commander/security owner when compromise or regulated data is plausible. Use only approved break-glass authority and an explicit reconciliation/review path.

**Scoring rubric**

10 points: diagnosis 2; evidence 2; blast radius/rollback 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### U01-Q12 — Design reviewed desired-state delivery and recovery

- **Unit / topic:** — GitOps principles and desired-state reconciliation
- **Level:** — L4
- **Question type:** — design
- **Objective tested:** — design a safe, auditable workflow for gitops principles and desired-state reconciliation
- **Estimated time:** — 20 minutes

**Question / scenario**

Design a GitOps operating model for a production service that supports reviewed changes, controlled reconciliation, emergency fixes, and proof of runtime health.

**Deliverables expected:** a component/workflow diagram, ownership and evidence table, failure modes, rollback/recovery path, and a short decision record. State assumptions and include at least two viable alternatives.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Use a protected configuration repository as desired-state authority; require reviewed changes and narrowly scoped controller identity; pin artifact digests; define explicit sync/self-heal/prune policies by environment; document break-glass approval, evidence capture, expiry, and reconciliation back into Git. Monitor controller convergence separately from application SLIs and retain change/runtime correlation evidence.

**Reasoning**

GitOps controls desired-state delivery, not all runtime correctness. A strong design links authorization, immutable artifact identity, controller action, live state, and business verification.

**Common wrong answers**

- **Assume convergence is guaranteed** — A controller can be unavailable, unauthorized, or blocked; verify its observed revision and live state.
- **Treat live state as the source of truth** — Live state may contain drift or an emergency change that still needs classification and reconciliation.

**Operational caveat**

Policy choices are illustrative. Verify controller-specific behavior and test recovery/pruning in a disposable environment before production rollout.

**Scoring rubric**

10 points: safety/correctness 2; evidence and verification 2; alternatives and trade-offs 2; failure/recovery plan 2; ownership, clarity, and unresolved uncertainty 2.

</details>

---

# Unit 2 — Argo CD: applications, projects, and sync policies (12 questions)

### U02-Q01 — Explain the core model for Application source/destination, sync versus health, projects, and de

- **Unit / topic:** Argo CD: applications, projects, and sync policies
- **Level:** L1
- **Question type:** conceptual
- **Objective tested:** trace an Application from source revision through render, diff, sync, and live state
- **Estimated time:** 6 minutes

**Question / scenario**

Explain the core model for Application source/destination, sync versus health, projects, and deletion semantics. In your answer, distinguish the desired configuration, the controller or process that acts on it, and the evidence that shows whether the intended outcome actually occurred.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

An Argo CD Application identifies a source and destination; rendered desired manifests are compared with cluster state. Sync status and health status answer different questions.

**Reasoning**

Argo CD sync status describes desired/live comparison, while health, project boundaries, operation history, and application telemetry describe different aspects. Diagnose the specific resource and policy before retrying or changing sync behavior.

**Common wrong answers**

- **Treat `Synced` as healthy** Sync and health are distinct; inspect degraded resources and application telemetry.
- **Enable prune or retry sync as a first diagnostic** This can delete resources or repeat a failure without identifying the cause.

**Operational caveat**

AppProject, sync, hooks/waves, history, and finalizer behavior are version-sensitive. Check the installed Argo CD documentation and current RBAC.

**Scoring rubric**

Full credit (3 points): states the core mechanism accurately (1), distinguishes what the evidence does and does not prove (1), and identifies a safe next check or operational implication (1).

</details>

---

### U02-Q02 — Interpret Synced and Degraded together

- **Unit / topic:** — Argo CD: applications, projects, and sync policies
- **Level:** — L2
- **Question type:** — conceptual
- **Objective tested:** — predict and verify interpret synced and degraded together
- **Estimated time:** — 7 minutes

**Question / scenario**

An Argo CD Application reports `Synced` and `Degraded`. Explain why these statuses can coexist and list the next checks before deciding to retry sync or roll back.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

`Synced` indicates the compared desired and live configuration is aligned; `Degraded` indicates a health problem in one or more resources. Inspect the degraded resource, Kubernetes events, rollout/replica readiness, application telemetry, and operation history. Do not retry sync blindly: first distinguish a manifest/configuration problem from a runtime or dependency failure.

**Reasoning**

Sync status and health status answer different questions. The resource conditions and runtime evidence—not the word `Synced` alone—determine the next safe action.

**Common wrong answers**

- **Treat `Synced` as healthy** — Sync and health are distinct; inspect degraded resources and application telemetry.
- **Enable prune or retry sync as a first diagnostic** — This can delete resources or repeat a failure without identifying the cause.

**Operational caveat**

Exact status details and CLI output vary by Argo CD version. Verify `argocd app get`/history behavior for the installed release and inspect live Kubernetes resources.

**Scoring rubric**

Full credit (3 points): states the correct operational conclusion (1), cites the evidence/policy that supports it (1), and names a safe next check plus a remaining uncertainty (1).

</details>

---

### U02-Q03 — Review production project and prune boundaries

- **Unit / topic:** — Argo CD: applications, projects, and sync policies
- **Level:** — L3
- **Question type:** — conceptual
- **Objective tested:** — diagnose and recover safely from review production project and prune boundaries
- **Estimated time:** — 8 minutes

**Question / scenario**

A production Application targets the correct cluster but uses a broad project and has automated sync plus prune. What policy and evidence checks should precede any change to that configuration?

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Confirm source repository/revision, destination namespace/cluster, AppProject source/destination/resource restrictions, sync policy, prune impact, and operator permissions. Inventory resources that would be deleted, validate the intended project and target in a disposable environment, obtain the required review, and preserve current Application/operation state before changing policy.

**Reasoning**

Application source, destination, project restrictions, sync policy, and resource health are separate control points; changing several at once can obscure the cause of a failure.

**Common wrong answers**

- **Treat `Synced` as healthy** — Sync and health are distinct; inspect degraded resources and application telemetry.
- **Enable prune or retry sync as a first diagnostic** — This can delete resources or repeat a failure without identifying the cause.

**Operational caveat**

AppProject and sync-policy details are version-sensitive. Check installed documentation and current RBAC; do not rely on unverified defaults.

**Scoring rubric**

Full credit (4 points): identifies the relevant state/evidence (1), orders diagnosis before mutation (1), checks blast radius and rollback/data compatibility (1), and defines verification/prevention (1).

</details>

---

### U02-Q04 — An Application reports `Synced` and `Degraded`. What is the safest interpretation?

- **Unit / topic:** Argo CD: applications, projects, and sync policies
- **Level:** L1
- **Question type:** MCQ
- **Objective tested:** trace an Application from source revision through render, diff, sync, and live state
- **Estimated time:** 3 minutes

**Question / scenario**

An Application reports `Synced` and `Degraded`. What is the safest interpretation?

A. Git and live manifests compare as synchronized, but at least one health check indicates a problem
B. The application is guaranteed to serve correct responses
C. The controller is unable to read Git, so status is meaningless
D. The cluster has no live resources

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**A**. Git and live manifests compare as synchronized, but at least one health check indicates a problem

**Reasoning**

- **A. Correct.** Sync is desired/live comparison; health evaluates resource readiness/health. Neither alone proves business correctness.
- **B. Incorrect.** The option proposes “The application is guaranteed to serve correct responses”; it makes a universal guarantee that the evidence does not support; controller and provider behavior depends on explicit policy, version, and observed state.
- **C. Incorrect.** The option proposes “The controller is unable to read Git, so status is meaningless”; Git records intent and review context but does not by itself prove what the cluster ran or that every required approval/promotion record exists.
- **D. Incorrect.** The option proposes “The cluster has no live resources”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses treat `synced` as healthy with verified state, or skips the required safety check: Sync and health are distinct; inspect degraded resources and application telemetry.

**Operational caveat**

AppProject, sync, hooks/waves, history, and finalizer behavior are version-sensitive. Check the installed Argo CD documentation and current RBAC.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U02-Q05 — What is the primary purpose of an AppProject?

- **Unit / topic:** Argo CD: applications, projects, and sync policies
- **Level:** L2
- **Question type:** MCQ
- **Objective tested:** distinguish sync status from health and business correctness
- **Estimated time:** 3 minutes

**Question / scenario**

What is the primary purpose of an AppProject?

A. Build container images
B. Constrain which sources, destinations, and resource kinds applications may use, plus related access boundaries
C. Replace Kubernetes RBAC in every case
D. Guarantee zero downtime

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**B**. Constrain which sources, destinations, and resource kinds applications may use, plus related access boundaries

**Reasoning**

- **A. Incorrect.** The option proposes “Build container images”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.
- **B. Correct.** Projects add Argo CD policy boundaries; Kubernetes RBAC and controller permissions remain important.
- **C. Incorrect.** The option proposes “Replace Kubernetes RBAC in every case”; it makes a universal guarantee that the evidence does not support; controller and provider behavior depends on explicit policy, version, and observed state.
- **D. Incorrect.** The option proposes “Guarantee zero downtime”; it makes a universal guarantee that the evidence does not support; controller and provider behavior depends on explicit policy, version, and observed state.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses treat `synced` as healthy with verified state, or skips the required safety check: Sync and health are distinct; inspect degraded resources and application telemetry.

**Operational caveat**

AppProject, sync, hooks/waves, history, and finalizer behavior are version-sensitive. Check the installed Argo CD documentation and current RBAC.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U02-Q06 — What should be checked before enabling automated prune in production?

- **Unit / topic:** Argo CD: applications, projects, and sync policies
- **Level:** L3
- **Question type:** MCQ
- **Objective tested:** evaluate AppProject boundaries, sync policies, and deletion/prune risk
- **Estimated time:** 3 minutes

**Question / scenario**

What should be checked before enabling automated prune in production?

A. Whether the YAML file is short
B. Deletion ownership, resource inventory, recovery/backup plan, and a disposable validation of prune behavior
C. Only the app version string
D. Whether all events are green

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**B**. Deletion ownership, resource inventory, recovery/backup plan, and a disposable validation of prune behavior

**Reasoning**

- **A. Incorrect.** The option proposes “Whether the YAML file is short”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.
- **B. Correct.** Prune can delete resources removed from desired state; assess impact and recovery before enabling it.
- **C. Incorrect.** The option proposes “Only the app version string”; it narrows the decision to one signal and omits the other required checks, such as ownership, runtime state, telemetry quality, or recovery safety.
- **D. Incorrect.** The option proposes “Whether all events are green”; structural shape alone cannot establish semantic compatibility across real producers and consumers.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses treat `synced` as healthy with verified state, or skips the required safety check: Sync and health are distinct; inspect degraded resources and application telemetry.

**Operational caveat**

AppProject, sync, hooks/waves, history, and finalizer behavior are version-sensitive. Check the installed Argo CD documentation and current RBAC.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U02-Q07 — Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Argo CD: applications, pro

- **Unit / topic:** Argo CD: applications, projects, and sync policies
- **Level:** L2
- **Question type:** output interpretation
- **Objective tested:** trace an Application from source revision through render, diff, sync, and live state
- **Estimated time:** 7 minutes

**Question / scenario**

Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Argo CD: applications, projects, and sync policies:

```text
SIMULATED / REPRESENTATIVE
NAME          SYNC STATUS   HEALTH STATUS
orders-api    Synced        Degraded
Last operation: Sync failed on Deployment/orders-api readiness check
Desired revision: cafe123
Live replicas: 1 desired / 0 available
```

State what is established, what remains unknown, the safest next diagnostic step, and whether you would promote, reconcile, pause, abort, or gather more evidence. Justify the decision using specific fields/lines above.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

`Synced` and `Degraded` are not contradictory: desired/live configuration can be synchronized while a Deployment has zero available replicas. The output explicitly says `1 desired / 0 available` and a readiness-check failure. Do not close the incident; inspect pod events/logs, readiness probes, image pull status, and application dependencies, then verify both resource health and business checks.

**Reasoning**

Output interpretation must separate observations from inference. A status or event can be stale, partial, or scoped to a single resource; the next check should target the earliest missing/failed link and preserve the current evidence.

**Common wrong answers**

- **Assume the best because one field is green.** That ignores contradictory fields and coverage gaps.
- **Mutate immediately.** Diagnose source, identity, scope, and rollback safety first unless containment urgency requires a minimal authorized action.

**Operational caveat**

All output is simulated; it is not claimed to come from a live cluster. Exact CLI output and controller status wording are `[VERIFY]` for the installed version.

**Scoring rubric**

Full credit: cite two specific fields, identify one unknown, choose a safe next action, and explain promotion/rollback constraints (4 points).

</details>

---

### U02-Q08 — Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Argo CD: applications, pro

- **Unit / topic:** Argo CD: applications, projects, and sync policies
- **Level:** L3
- **Question type:** output interpretation
- **Objective tested:** distinguish sync status from health and business correctness
- **Estimated time:** 8 minutes

**Question / scenario**

Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Argo CD: applications, projects, and sync policies:

```text
SIMULATED / REPRESENTATIVE
Application source revision: cafe123
Destination namespace: orders-prod
Project: default
Sync policy: automated
Prune: enabled
Self-heal: enabled
Resource diff: one live ConfigMap absent from desired manifests
```

State what is established, what remains unknown, the safest next diagnostic step, and whether you would promote, reconcile, pause, abort, or gather more evidence. Justify the decision using specific fields/lines above.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The Application targets `orders-prod` but uses project `default`, automated sync, prune, and self-heal. The output also says a live ConfigMap is absent from desired manifests. Before reconciling/deleting it, establish ownership and whether it contains state needed by the service. Restrict the AppProject and source/destination scope; test prune semantics in a disposable namespace and preserve the diff and operation history.

**Reasoning**

Output interpretation must separate observations from inference. A status or event can be stale, partial, or scoped to a single resource; the next check should target the earliest missing/failed link and preserve the current evidence.

**Common wrong answers**

- **Assume the best because one field is green.** That ignores contradictory fields and coverage gaps.
- **Mutate immediately.** Diagnose source, identity, scope, and rollback safety first unless containment urgency requires a minimal authorized action.

**Operational caveat**

All output is simulated; it is not claimed to come from a live cluster. Exact CLI output and controller status wording are `[VERIFY]` for the installed version.

**Scoring rubric**

Full credit: cite two specific fields, identify one unknown, choose a safe next action, and explain promotion/rollback constraints (4 points).

</details>

---

### U02-Q09 — Review this `INTENTIONALLY FLAWED` example for Argo CD: applications, projects, and sync polici

- **Unit / topic:** Argo CD: applications, projects, and sync policies
- **Level:** L3
- **Question type:** configuration/manifest review
- **Objective tested:** trace an Application from source revision through render, diff, sync, and live state
- **Estimated time:** 10 minutes

**Question / scenario**

Review this `INTENTIONALLY FLAWED` example for Argo CD: applications, projects, and sync policies. Identify at least three distinct defects, explain their operational impact, and propose a corrected version or exact correction.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata: {name: orders-api, namespace: argocd}
spec:
  project: default
  source:
    repoURL: https://git.example.invalid/platform.git
    path: prod/orders-api
    targetRevision: main
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The defects are:

1. The Application uses the broad `default` AppProject rather than a restricted production project.
2. The destination is `default`, not the intended `orders-prod` namespace.
3. Automated prune and self-heal are enabled without demonstrating deletion/rollback safeguards.

**Corrected direction/snippet:**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata: {name: orders-api, namespace: argocd}
spec:
  project: orders-prod-restricted
  source:
    repoURL: https://git.example.invalid/platform.git
    path: prod/orders-api
    targetRevision: main
  destination:
    server: https://kubernetes.default.svc
    namespace: orders-prod
  # Add automated sync/prune/self-heal only after deletion and recovery policy review.
```

The correction is an instructional pattern; confirm product-specific schema and provider support before applying it.

**Reasoning**

The defects are not merely style issues: they can make resources fail to select, weaken access boundaries, make the artifact mutable, trigger unintended deletion, leak sensitive data, or convert missing evidence into an unsafe action. Corrections must be tested in a disposable environment.

**Common wrong answers**

- **Fix only syntax.** A valid manifest can still be insecure or semantically unsafe.
- **Assume an illustrative snippet is a complete deployable CRD.** Required fields and semantics depend on the installed API/version.

**Operational caveat**

The original is intentionally flawed and must not be applied. Corrected snippets may be bounded examples rather than complete production configuration; `[VERIFY]` any controller-specific fields.

**Scoring rubric**

Full credit: at least three distinct defects (3 points), impact for each (3), corrected snippet/direction (2), version/safety caveat (2).

</details>

---

### U02-Q10 — Review this `INTENTIONALLY FLAWED` example for Argo CD: applications, projects, and sync polici

- **Unit / topic:** Argo CD: applications, projects, and sync policies
- **Level:** L3
- **Question type:** configuration/manifest review
- **Objective tested:** distinguish sync status from health and business correctness
- **Estimated time:** 10 minutes

**Question / scenario**

Review this `INTENTIONALLY FLAWED` example for Argo CD: applications, projects, and sync policies. Identify at least three distinct defects, explain their operational impact, and propose a corrected version or exact correction.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata: {name: orders-prod, namespace: argocd}
spec:
  sourceRepos: ["*"]
  destinations:
  - namespace: "*"
    server: "*"
  clusterResourceWhitelist:
  - group: "*"
    kind: "*"
```

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The defects are:

1. `sourceRepos: ["*"]` permits any source repository.
2. The destination wildcard permits any namespace/cluster destination.
3. The cluster-resource whitelist allows every group and kind, defeating least-privilege boundaries.

**Corrected direction/snippet:**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata: {name: orders-prod-restricted, namespace: argocd}
spec:
  sourceRepos:
  - https://git.example.invalid/platform.git
  destinations:
  - namespace: orders-prod
    server: https://kubernetes.default.svc
  clusterResourceWhitelist: []
# Add only resource kinds that the workload demonstrably requires; validate schema for installed version.
```

The correction is an instructional pattern; confirm product-specific schema and provider support before applying it.

**Reasoning**

The defects are not merely style issues: they can make resources fail to select, weaken access boundaries, make the artifact mutable, trigger unintended deletion, leak sensitive data, or convert missing evidence into an unsafe action. Corrections must be tested in a disposable environment.

**Common wrong answers**

- **Fix only syntax.** A valid manifest can still be insecure or semantically unsafe.
- **Assume an illustrative snippet is a complete deployable CRD.** Required fields and semantics depend on the installed API/version.

**Operational caveat**

The original is intentionally flawed and must not be applied. Corrected snippets may be bounded examples rather than complete production configuration; `[VERIFY]` any controller-specific fields.

**Scoring rubric**

Full credit: at least three distinct defects (3 points), impact for each (3), corrected snippet/direction (2), version/safety caveat (2).

</details>

---

### U02-Q11 — Incident: An Application is `Synced` but its Deployment is `Degraded`. A teammate interprets Sy

- **Unit / topic:** Argo CD: applications, projects, and sync policies
- **Level:** L4
- **Question type:** incident/troubleshooting
- **Objective tested:** evaluate AppProject boundaries, sync policies, and deletion/prune risk
- **Estimated time:** 15 minutes

**Question / scenario**

Incident: An Application is `Synced` but its Deployment is `Degraded`. A teammate interprets Synced as proof the service is healthy and closes the incident.

Provide symptom → diagnosis → evidence to preserve → blast-radius and rollback-safety check → containment/recovery → prevention. Identify one residual uncertainty that must not be presented as fact.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**Symptom:** An Application is `Synced` but its Deployment is `Degraded`. A teammate interprets Synced as proof the service is healthy and closes the incident.

**Diagnosis:** An Argo CD Application identifies a source and destination; rendered desired manifests are compared with cluster state. Sync status and health status answer different questions.

**Evidence:** collect the relevant Git revision/PR, controller conditions/events, live resource state, runtime/metric samples, timestamps, and actor/approval data as applicable.

**Blast radius and rollback:** identify affected environments/replicas/consumers, determine whether state/data/external side effects changed, and test whether the prior version can safely read current state. Do not assume an image rollback reverses data.

**Containment/recovery:** use the smallest authorized reversible action; pause promotion or isolate the affected path if warranted; preserve a before/after record; reconcile the intended fix into the declared source; verify customer-facing behavior.

**Prevention:** AppProjects and RBAC constrain sources, destinations, resource kinds, and user actions; overly broad permissions turn a deployment system into a privilege-escalation path.

**Residual uncertainty:** any missing history, unknown consumer behavior, unparseable runtime identity, or absent metric sample remains UNKNOWN until corroborated.

**Reasoning**

The incident response separates preserving evidence from containment, makes recovery contingent on state compatibility, and verifies both control-plane convergence and application-level outcome.

**Common wrong answers**

- **Immediately force-sync/redeploy without preserving evidence.** This can erase the live state that explains the incident.
- **Assume rollback is safe because the previous artifact exists.** Data, schema, event, or external side effects may be incompatible.

**Operational caveat**

Escalate to the incident commander/security owner when compromise or regulated data is plausible. Use only approved break-glass authority and an explicit reconciliation/review path.

**Scoring rubric**

10 points: diagnosis 2; evidence 2; blast radius/rollback 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### U02-Q12 — Design production Application boundaries and sync policy

- **Unit / topic:** — Argo CD: applications, projects, and sync policies
- **Level:** — L4
- **Question type:** — design
- **Objective tested:** — design a safe, auditable workflow for argo cd: applications, projects, and sync policies
- **Estimated time:** — 20 minutes

**Question / scenario**

Design an Argo CD production Application model with environment boundaries, controlled sync/prune, auditable promotion, and safe diagnosis of degraded resources.

**Deliverables expected:** a component/workflow diagram, ownership and evidence table, failure modes, rollback/recovery path, and a short decision record. State assumptions and include at least two viable alternatives.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Use an explicitly scoped AppProject, least-privilege source/destination permissions, reviewed environment-specific configuration, and immutable image digests. Choose manual or automated sync deliberately; make prune behavior explicit and test it; retain operation/history evidence externally where required. Separate sync status from health, and define runbooks for degraded resources, failed operations, and rollback compatibility.

**Reasoning**

An Application is one link in the delivery chain. Safe operation requires source trust, project boundaries, controlled sync, runtime health checks, and evidence retention.

**Common wrong answers**

- **Treat `Synced` as healthy** — Sync and health are distinct; inspect degraded resources and application telemetry.
- **Enable prune or retry sync as a first diagnostic** — This can delete resources or repeat a failure without identifying the cause.

**Operational caveat**

Verify exact fields, finalizer behavior, hooks/waves, and CLI output against the installed Argo CD version.

**Scoring rubric**

10 points: safety/correctness 2; evidence and verification 2; alternatives and trade-offs 2; failure/recovery plan 2; ownership, clarity, and unresolved uncertainty 2.

</details>

---

# Unit 3 — Flux controllers and Kustomize/Helm reconciliation (12 questions)

### U03-Q01 — Explain the core model for source artifacts, Kustomization/HelmRelease, conditions, dependencie

- **Unit / topic:** Flux controllers and Kustomize/Helm reconciliation
- **Level:** L1
- **Question type:** conceptual
- **Objective tested:** identify Flux source, Kustomize, Helm, and notification controller responsibilities
- **Estimated time:** 6 minutes

**Question / scenario**

Explain the core model for source artifacts, Kustomization/HelmRelease, conditions, dependencies, notifications. In your answer, distinguish the desired configuration, the controller or process that acts on it, and the evidence that shows whether the intended outcome actually occurred.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Flux is a set of Kubernetes controllers: source artifacts are fetched, then Kustomize or Helm controllers reconcile workloads. A healthy source does not prove the application is healthy.

**Reasoning**

Flux source acquisition, Kustomize/Helm reconciliation, controller conditions, Kubernetes runtime health, and notifications are distinct links. Correlate source revision through applied resources and retain transient events if they matter for later review.

**Common wrong answers**

- **Treat source readiness as proof of deployment** A source revision can be fetched without every downstream resource successfully applying it.
- **Assume notifications are durable history** Events can be transient; export required evidence and verify actual resources.

**Operational caveat**

Flux CRDs, controller conditions, notification providers, and dependency semantics vary by version. Check installed schemas and do not expose secrets in events.

**Scoring rubric**

Full credit (3 points): states the core mechanism accurately (1), distinguishes what the evidence does and does not prove (1), and identifies a safe next check or operational implication (1).

</details>

---

### U03-Q02 — Diagnose stale Flux revision after source failure

- **Unit / topic:** — Flux controllers and Kustomize/Helm reconciliation
- **Level:** — L2
- **Question type:** — conceptual
- **Objective tested:** — predict and verify diagnose stale flux revision after source failure
- **Estimated time:** — 7 minutes

**Question / scenario**

A Flux source is not Ready, while a downstream Kustomization still shows an older applied revision. What can you conclude and how should you investigate?

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The source failure means the newest desired revision has not been reliably made available to downstream reconciliation. The older applied revision is evidence of prior state, not proof the newest commit is deployed. Inspect source-controller conditions/events, authentication/network errors, observed revision, downstream Kustomization/HelmRelease status, and live workloads; restore source readiness before claiming convergence.

**Reasoning**

Flux separates source acquisition from Kustomize/Helm reconciliation. A downstream resource may remain at an older revision while its source is failing.

**Common wrong answers**

- **Treat source readiness as proof of deployment** — A source revision can be fetched without every downstream resource successfully applying it.
- **Assume notifications are durable history** — Events can be transient; export required evidence and verify actual resources.

**Operational caveat**

Flux conditions, CLI output, and dependency semantics vary by version. Check the installed controller versions and official docs.

**Scoring rubric**

Full credit (3 points): states the correct operational conclusion (1), cites the evidence/policy that supports it (1), and names a safe next check plus a remaining uncertainty (1).

</details>

---

### U03-Q03 — Investigate successful reconciliation with unhealthy runtime

- **Unit / topic:** — Flux controllers and Kustomize/Helm reconciliation
- **Level:** — L3
- **Question type:** — conceptual
- **Objective tested:** — diagnose and recover safely from investigate successful reconciliation with unhealthy runtime
- **Estimated time:** — 8 minutes

**Question / scenario**

A Helm release reconciles successfully, but the application is unhealthy and notification events are not retained. Explain the investigation and evidence plan.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Correlate the HelmRelease and source revision with rendered values, Kubernetes workload status, pod events/logs, and application SLIs. Export relevant notifications/events to durable storage with timestamps and release identifiers, redacting secrets. Treat successful reconciliation as evidence of controller action, not proof of business correctness.

**Reasoning**

Source readiness, reconciliation success, workload health, and business outcomes are different stages. Transient events need external retention when they are needed for later investigation.

**Common wrong answers**

- **Treat source readiness as proof of deployment** — A source revision can be fetched without every downstream resource successfully applying it.
- **Assume notifications are durable history** — Events can be transient; export required evidence and verify actual resources.

**Operational caveat**

Check the installed Flux/Helm controller APIs and notification provider configuration. Redact payloads and avoid exposing secret values in logs.

**Scoring rubric**

Full credit (4 points): identifies the relevant state/evidence (1), orders diagnosis before mutation (1), checks blast radius and rollback/data compatibility (1), and defines verification/prevention (1).

</details>

---

### U03-Q04 — Which component role is most accurate?

- **Unit / topic:** Flux controllers and Kustomize/Helm reconciliation
- **Level:** L1
- **Question type:** MCQ
- **Objective tested:** identify Flux source, Kustomize, Helm, and notification controller responsibilities
- **Estimated time:** 3 minutes

**Question / scenario**

Which component role is most accurate?

A. source-controller obtains source artifacts; kustomize-controller applies Kustomize-built state
B. helm-controller stores Kubernetes audit logs forever
C. notification-controller is the sole workload reconciler
D. source-controller routes user HTTP traffic

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**A**. source-controller obtains source artifacts; kustomize-controller applies Kustomize-built state

**Reasoning**

- **A. Correct.** Flux controllers have distinct responsibilities; verify installed optional controllers and versions.
- **B. Incorrect.** The option proposes “helm-controller stores Kubernetes audit logs forever”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.
- **C. Incorrect.** The option proposes “notification-controller is the sole workload reconciler”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.
- **D. Incorrect.** The option proposes “source-controller routes user HTTP traffic”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses treat source readiness as proof of deployment with verified state, or skips the required safety check: A source revision can be fetched without every downstream resource successfully applying it.

**Operational caveat**

Flux CRDs, controller conditions, notification providers, and dependency semantics vary by version. Check installed schemas and do not expose secrets in events.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U03-Q05 — A Flux Kustomization is not Ready because its GitRepository has no artifact. What should be che

- **Unit / topic:** Flux controllers and Kustomize/Helm reconciliation
- **Level:** L2
- **Question type:** MCQ
- **Objective tested:** diagnose source/reconciliation readiness from conditions and events
- **Estimated time:** 3 minutes

**Question / scenario**

A Flux Kustomization is not Ready because its GitRepository has no artifact. What should be checked first?

A. Change the Service selector
B. Source URL, credentials, ref, source-controller conditions and logs
C. Delete all Deployments
D. Increase canary traffic

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**B**. Source URL, credentials, ref, source-controller conditions and logs

**Reasoning**

- **A. Incorrect.** The option proposes “Change the Service selector”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.
- **B. Correct.** Downstream reconciliation depends on a ready source artifact; debug the first failing link.
- **C. Incorrect.** The option proposes “Delete all Deployments”; it proposes an unsafe shortcut without first establishing authorization, impact, evidence preservation, and a recovery path.
- **D. Incorrect.** The option proposes “Increase canary traffic”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses treat source readiness as proof of deployment with verified state, or skips the required safety check: A source revision can be fetched without every downstream resource successfully applying it.

**Operational caveat**

Flux CRDs, controller conditions, notification providers, and dependency semantics vary by version. Check installed schemas and do not expose secrets in events.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U03-Q06 — Why export Flux notifications/events to durable storage?

- **Unit / topic:** Flux controllers and Kustomize/Helm reconciliation
- **Level:** L3
- **Question type:** MCQ
- **Objective tested:** design safe pruning, dependency, and event-retention behavior
- **Estimated time:** 3 minutes

**Question / scenario**

Why export Flux notifications/events to durable storage?

A. Events are guaranteed to be retained indefinitely
B. Export creates a correlated record that can outlive transient Kubernetes events/controller history
C. Notifications replace runtime metrics
D. It prevents all Git outages

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**B**. Export creates a correlated record that can outlive transient Kubernetes events/controller history

**Reasoning**

- **A. Incorrect.** The option proposes “Events are guaranteed to be retained indefinitely”; it makes a universal guarantee that the evidence does not support; controller and provider behavior depends on explicit policy, version, and observed state.
- **B. Correct.** Retention and delivery semantics depend on configuration; export is not automatically immutable or complete.
- **C. Incorrect.** The option proposes “Notifications replace runtime metrics”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.
- **D. Incorrect.** The option proposes “It prevents all Git outages”; a mutable tag can point to different bytes over time and therefore does not prove the exact artifact that was tested or ran.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses treat source readiness as proof of deployment with verified state, or skips the required safety check: A source revision can be fetched without every downstream resource successfully applying it.

**Operational caveat**

Flux CRDs, controller conditions, notification providers, and dependency semantics vary by version. Check installed schemas and do not expose secrets in events.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U03-Q07 — Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Flux controllers and Kusto

- **Unit / topic:** Flux controllers and Kustomize/Helm reconciliation
- **Level:** L2
- **Question type:** output interpretation
- **Objective tested:** identify Flux source, Kustomize, Helm, and notification controller responsibilities
- **Estimated time:** 7 minutes

**Question / scenario**

Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Flux controllers and Kustomize/Helm reconciliation:

```text
SIMULATED / REPRESENTATIVE
NAME           REVISION       READY  MESSAGE
orders-source  (none)         False  failed to fetch artifact: authentication failed
orders-app     (unknown)      False  dependency/source artifact not ready
```

State what is established, what remains unknown, the safest next diagnostic step, and whether you would promote, reconcile, pause, abort, or gather more evidence. Justify the decision using specific fields/lines above.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The first failed link is the source: `orders-source` has no revision and `Ready=False` because authentication failed. The downstream app is not ready because its source artifact is unavailable. Fix the repository credential/URL/ref using a least-privilege identity and inspect source-controller conditions/logs before changing workload manifests; then confirm the artifact revision and downstream reconciliation.

**Reasoning**

Output interpretation must separate observations from inference. A status or event can be stale, partial, or scoped to a single resource; the next check should target the earliest missing/failed link and preserve the current evidence.

**Common wrong answers**

- **Assume the best because one field is green.** That ignores contradictory fields and coverage gaps.
- **Mutate immediately.** Diagnose source, identity, scope, and rollback safety first unless containment urgency requires a minimal authorized action.

**Operational caveat**

All output is simulated; it is not claimed to come from a live cluster. Exact CLI output and controller status wording are `[VERIFY]` for the installed version.

**Scoring rubric**

Full credit: cite two specific fields, identify one unknown, choose a safe next action, and explain promotion/rollback constraints (4 points).

</details>

---

### U03-Q08 — Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Flux controllers and Kusto

- **Unit / topic:** Flux controllers and Kustomize/Helm reconciliation
- **Level:** L3
- **Question type:** output interpretation
- **Objective tested:** diagnose source/reconciliation readiness from conditions and events
- **Estimated time:** 8 minutes

**Question / scenario**

Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Flux controllers and Kustomize/Helm reconciliation:

```text
SIMULATED / REPRESENTATIVE
source-controller: GitRepository orders-config Ready=False
reason: AuthenticationFailed
kustomize-controller: Kustomization orders-app Ready=False
lastAppliedRevision: (not recorded)
notification-controller: no durable event archive configured
```

State what is established, what remains unknown, the safest next diagnostic step, and whether you would promote, reconcile, pause, abort, or gather more evidence. Justify the decision using specific fields/lines above.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The GitRepository is `Ready=False` with `AuthenticationFailed`, `lastAppliedRevision` is absent, and no durable notification archive is configured. This indicates both a source access failure and a retention gap. Restore source access securely, verify the fetched revision and applied revision, and export correlated events before they expire; do not infer what was deployed from the current Git branch alone.

**Reasoning**

Output interpretation must separate observations from inference. A status or event can be stale, partial, or scoped to a single resource; the next check should target the earliest missing/failed link and preserve the current evidence.

**Common wrong answers**

- **Assume the best because one field is green.** That ignores contradictory fields and coverage gaps.
- **Mutate immediately.** Diagnose source, identity, scope, and rollback safety first unless containment urgency requires a minimal authorized action.

**Operational caveat**

All output is simulated; it is not claimed to come from a live cluster. Exact CLI output and controller status wording are `[VERIFY]` for the installed version.

**Scoring rubric**

Full credit: cite two specific fields, identify one unknown, choose a safe next action, and explain promotion/rollback constraints (4 points).

</details>

---

### U03-Q09 — Review this `INTENTIONALLY FLAWED` example for Flux controllers and Kustomize/Helm reconciliati

- **Unit / topic:** Flux controllers and Kustomize/Helm reconciliation
- **Level:** L3
- **Question type:** configuration/manifest review
- **Objective tested:** identify Flux source, Kustomize, Helm, and notification controller responsibilities
- **Estimated time:** 10 minutes

**Question / scenario**

Review this `INTENTIONALLY FLAWED` example for Flux controllers and Kustomize/Helm reconciliation. Identify at least three distinct defects, explain their operational impact, and propose a corrected version or exact correction.

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata: {name: orders-config, namespace: flux-system}
spec:
  interval: 1m
  url: https://git.example.invalid/platform.git
  ref:
    branch: main
  secretRef:
    name: shared-admin-token
```

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The defects are:

1. A shared admin credential is referenced instead of a dedicated read-only repository identity.
2. The snippet does not show a pinned/controlled trust and branch policy for the source revision.
3. Credential scope and rotation/ownership are not documented; source access failures need safe handling.

**Corrected direction/snippet:**

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata: {name: orders-config, namespace: flux-system}
spec:
  interval: 1m
  url: https://git.example.invalid/platform.git
  ref:
    branch: main
  # Reference a dedicated least-privilege read-only credential Secret created securely; do not reuse admin credentials.
```

The correction is an instructional pattern; confirm product-specific schema and provider support before applying it.

**Reasoning**

The defects are not merely style issues: they can make resources fail to select, weaken access boundaries, make the artifact mutable, trigger unintended deletion, leak sensitive data, or convert missing evidence into an unsafe action. Corrections must be tested in a disposable environment.

**Common wrong answers**

- **Fix only syntax.** A valid manifest can still be insecure or semantically unsafe.
- **Assume an illustrative snippet is a complete deployable CRD.** Required fields and semantics depend on the installed API/version.

**Operational caveat**

The original is intentionally flawed and must not be applied. Corrected snippets may be bounded examples rather than complete production configuration; `[VERIFY]` any controller-specific fields.

**Scoring rubric**

Full credit: at least three distinct defects (3 points), impact for each (3), corrected snippet/direction (2), version/safety caveat (2).

</details>

---

### U03-Q10 — Review this `INTENTIONALLY FLAWED` example for Flux controllers and Kustomize/Helm reconciliati

- **Unit / topic:** Flux controllers and Kustomize/Helm reconciliation
- **Level:** L3
- **Question type:** configuration/manifest review
- **Objective tested:** diagnose source/reconciliation readiness from conditions and events
- **Estimated time:** 10 minutes

**Question / scenario**

Review this `INTENTIONALLY FLAWED` example for Flux controllers and Kustomize/Helm reconciliation. Identify at least three distinct defects, explain their operational impact, and propose a corrected version or exact correction.

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata: {name: orders-app, namespace: flux-system}
spec:
  interval: 1m
  path: ./clusters/prod/orders-api
  sourceRef: {kind: GitRepository, name: orders-config}
  prune: true
  targetNamespace: default
```

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The defects are:

1. Pruning is enabled without a demonstrated ownership/deletion drill.
2. The target namespace is `default` instead of the production namespace.
3. The API version and field support must be checked against installed Flux CRDs; the example has no dependency/health verification strategy.

**Corrected direction/snippet:**

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata: {name: orders-app, namespace: flux-system}
spec:
  interval: 1m
  path: ./clusters/prod/orders-api
  sourceRef: {kind: GitRepository, name: orders-config}
  prune: false # Enable only after ownership/deletion tests and recovery design.
  targetNamespace: orders-prod
# Confirm apiVersion and fields against installed Flux CRDs before applying.
```

The correction is an instructional pattern; confirm product-specific schema and provider support before applying it.

**Reasoning**

The defects are not merely style issues: they can make resources fail to select, weaken access boundaries, make the artifact mutable, trigger unintended deletion, leak sensitive data, or convert missing evidence into an unsafe action. Corrections must be tested in a disposable environment.

**Common wrong answers**

- **Fix only syntax.** A valid manifest can still be insecure or semantically unsafe.
- **Assume an illustrative snippet is a complete deployable CRD.** Required fields and semantics depend on the installed API/version.

**Operational caveat**

The original is intentionally flawed and must not be applied. Corrected snippets may be bounded examples rather than complete production configuration; `[VERIFY]` any controller-specific fields.

**Scoring rubric**

Full credit: at least three distinct defects (3 points), impact for each (3), corrected snippet/direction (2), version/safety caveat (2).

</details>

---

### U03-Q11 — Incident: A Flux Kustomization is Ready=False because the referenced source has not produced a 

- **Unit / topic:** Flux controllers and Kustomize/Helm reconciliation
- **Level:** L4
- **Question type:** incident/troubleshooting
- **Objective tested:** design safe pruning, dependency, and event-retention behavior
- **Estimated time:** 15 minutes

**Question / scenario**

Incident: A Flux Kustomization is Ready=False because the referenced source has not produced a ready artifact; the team keeps editing Deployment manifests without fixing the source failure.

Provide symptom → diagnosis → evidence to preserve → blast-radius and rollback-safety check → containment/recovery → prevention. Identify one residual uncertainty that must not be presented as fact.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**Symptom:** A Flux Kustomization is Ready=False because the referenced source has not produced a ready artifact; the team keeps editing Deployment manifests without fixing the source failure.

**Diagnosis:** Flux is a set of Kubernetes controllers: source artifacts are fetched, then Kustomize or Helm controllers reconcile workloads. A healthy source does not prove the application is healthy.

**Evidence:** collect the relevant Git revision/PR, controller conditions/events, live resource state, runtime/metric samples, timestamps, and actor/approval data as applicable.

**Blast radius and rollback:** identify affected environments/replicas/consumers, determine whether state/data/external side effects changed, and test whether the prior version can safely read current state. Do not assume an image rollback reverses data.

**Containment/recovery:** use the smallest authorized reversible action; pause promotion or isolate the affected path if warranted; preserve a before/after record; reconcile the intended fix into the declared source; verify customer-facing behavior.

**Prevention:** Events and notifications are operationally useful but transient. Durable audit requirements need export, correlation identifiers, redaction, and retention.

**Residual uncertainty:** any missing history, unknown consumer behavior, unparseable runtime identity, or absent metric sample remains UNKNOWN until corroborated.

**Reasoning**

The incident response separates preserving evidence from containment, makes recovery contingent on state compatibility, and verifies both control-plane convergence and application-level outcome.

**Common wrong answers**

- **Immediately force-sync/redeploy without preserving evidence.** This can erase the live state that explains the incident.
- **Assume rollback is safe because the previous artifact exists.** Data, schema, event, or external side effects may be incompatible.

**Operational caveat**

Escalate to the incident commander/security owner when compromise or regulated data is plausible. Use only approved break-glass authority and an explicit reconciliation/review path.

**Scoring rubric**

10 points: diagnosis 2; evidence 2; blast radius/rollback 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### U03-Q12 — Design Flux reconciliation and durable event evidence

- **Unit / topic:** — Flux controllers and Kustomize/Helm reconciliation
- **Level:** — L4
- **Question type:** — design
- **Objective tested:** — design a safe, auditable workflow for flux controllers and kustomize/helm reconciliation
- **Estimated time:** — 20 minutes

**Question / scenario**

Design a Flux-based delivery path for a service using Kustomize overlays and a Helm release, including source failure handling and durable event evidence.

**Deliverables expected:** a component/workflow diagram, ownership and evidence table, failure modes, rollback/recovery path, and a short decision record. State assumptions and include at least two viable alternatives.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Separate source, Kustomize, Helm, and notification responsibilities; pin or review source revisions; use environment overlays with explicit ownership; define reconciliation readiness gates and dependency handling only where supported. Export controller events/notifications with stable release correlation IDs, retention and redaction, and verify actual workloads and business metrics after reconciliation.

**Reasoning**

Composable controllers improve separation of concerns but also create multiple states to correlate. The design must show which revision was fetched, rendered, applied, and verified.

**Common wrong answers**

- **Treat source readiness as proof of deployment** — A source revision can be fetched without every downstream resource successfully applying it.
- **Assume notifications are durable history** — Events can be transient; export required evidence and verify actual resources.

**Operational caveat**

Verify CRD schemas, controller versions, notification integrations, and exact CLI output before applying examples.

**Scoring rubric**

10 points: safety/correctness 2; evidence and verification 2; alternatives and trade-offs 2; failure/recovery plan 2; ownership, clarity, and unresolved uncertainty 2.

</details>

---

# Unit 4 — Repository layout and multi-environment promotion (12 questions)

### U04-Q01 — Explain the core model for app/config repos, overlays, promotion, immutable artifacts, review o

- **Unit / topic:** Repository layout and multi-environment promotion
- **Level:** L1
- **Question type:** conceptual
- **Objective tested:** compare repository and environment promotion patterns
- **Estimated time:** 6 minutes

**Question / scenario**

Explain the core model for app/config repos, overlays, promotion, immutable artifacts, review ownership. In your answer, distinguish the desired configuration, the controller or process that acts on it, and the evidence that shows whether the intended outcome actually occurred.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Repository strategy is a trade-off among ownership, autonomy, visibility, and operational complexity. No single-repo or multi-repo pattern is universally best.

**Reasoning**

Promotion must preserve artifact identity while changing environment-specific intent through a reviewable path. The source commit, build, digest, config commit, approvals, and runtime observation prove different parts of the release.

**Common wrong answers**

- **Rebuild separately for production** A rebuild may produce different artifact bytes and weaken promotion traceability.
- **Treat a branch or directory name as an approval** Authorization depends on configured protections, review evidence, and ownership.

**Operational caveat**

Repository topology and approval rules are organizational choices. Verify actual branch/path protections and retain the exact config commit used for promotion.

**Scoring rubric**

Full credit (3 points): states the core mechanism accurately (1), distinguishes what the evidence does and does not prove (1), and identifies a safe next check or operational implication (1).

</details>

---

### U04-Q02 — Promote the same tested artifact

- **Unit / topic:** — Repository layout and multi-environment promotion
- **Level:** — L2
- **Question type:** — conceptual
- **Objective tested:** — predict and verify promote the same tested artifact
- **Estimated time:** — 7 minutes

**Question / scenario**

A release passed tests in staging. Production promotion would either update the image digest or rebuild the source commit. Which approach better preserves artifact identity, and what records should accompany promotion?

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Promote the same tested artifact by changing the production configuration reference to the verified immutable digest. Rebuilding can produce different bytes even from the same source commit. Record source commit, CI/build ID, digest, staging evidence, reviewed production config commit, approver/change ID, and post-promotion verification.

**Reasoning**

Promotion should advance an already-tested artifact through environments while keeping environment-specific configuration reviewable and the artifact identity stable.

**Common wrong answers**

- **Rebuild separately for production** — A rebuild may produce different artifact bytes and weaken promotion traceability.
- **Treat a branch or directory name as an approval** — Authorization depends on configured protections, review evidence, and ownership.

**Operational caveat**

Repository strategy is a trade-off, not a universal rule. Verify branch protections, path ownership, and CI provenance for the chosen repository model.

**Scoring rubric**

Full credit (3 points): states the correct operational conclusion (1), cites the evidence/policy that supports it (1), and names a safe next check plus a remaining uncertainty (1).

</details>

---

### U04-Q03 — Promote an application hotfix through the config repository

- **Unit / topic:** — Repository layout and multi-environment promotion
- **Level:** — L3
- **Question type:** — conceptual
- **Objective tested:** — diagnose and recover safely from promote an application hotfix through the config repository
- **Estimated time:** — 8 minutes

**Question / scenario**

Your team has separate application and configuration repositories. A hotfix lands in the application repo, but production still references the old digest. Describe the safe promotion sequence and evidence needed.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Build/test/scan the hotfix, publish the artifact, record its immutable digest and build provenance, then update the production config repository through the reviewed promotion path. Verify the exact digest in Git and the runtime after reconciliation; link the application commit, build, configuration commit, approver, and deployment record.

**Reasoning**

The application repository records source changes; the configuration repository records deployment intent. A change in one does not prove the other was promoted.

**Common wrong answers**

- **Rebuild separately for production** — A rebuild may produce different artifact bytes and weaken promotion traceability.
- **Treat a branch or directory name as an approval** — Authorization depends on configured protections, review evidence, and ownership.

**Operational caveat**

Promotion gates and approvals are organizational policy. Ensure the source and config repository trust boundaries are independently protected.

**Scoring rubric**

Full credit (4 points): identifies the relevant state/evidence (1), orders diagnosis before mutation (1), checks blast radius and rollback/data compatibility (1), and defines verification/prevention (1).

</details>

---

### U04-Q04 — What best proves staging and production received the same application artifact?

- **Unit / topic:** Repository layout and multi-environment promotion
- **Level:** L1
- **Question type:** MCQ
- **Objective tested:** compare repository and environment promotion patterns
- **Estimated time:** 3 minutes

**Question / scenario**

What best proves staging and production received the same application artifact?

A. Same human-readable tag only
B. Same source commit only, regardless of build inputs
C. Same verified artifact digest referenced by both environment configurations
D. Same deployment timestamp

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**C**. Same verified artifact digest referenced by both environment configurations

**Reasoning**

- **A. Incorrect.** The option proposes “Same human-readable tag only”; a mutable tag can point to different bytes over time and therefore does not prove the exact artifact that was tested or ran.
- **B. Incorrect.** The option proposes “Same source commit only, regardless of build inputs”; Git records intent and review context but does not by itself prove what the cluster ran or that every required approval/promotion record exists.
- **C. Correct.** A digest identifies artifact content; the commit alone may not capture all build inputs or guarantee a reproducible build.
- **D. Incorrect.** The option proposes “Same deployment timestamp”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses rebuild separately for production with verified state, or skips the required safety check: A rebuild may produce different artifact bytes and weaken promotion traceability.

**Operational caveat**

Repository topology and approval rules are organizational choices. Verify actual branch/path protections and retain the exact config commit used for promotion.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U04-Q05 — Which is a valid reason to split app and config repositories?

- **Unit / topic:** Repository layout and multi-environment promotion
- **Level:** L2
- **Question type:** MCQ
- **Objective tested:** promote the same immutable artifact through environments with reviewable changes
- **Estimated time:** 3 minutes

**Question / scenario**

Which is a valid reason to split app and config repositories?

A. It guarantees no drift
B. It can separate application code ownership from deployment authority and release configuration
C. It eliminates the need for reviews
D. It makes tags immutable

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**B**. It can separate application code ownership from deployment authority and release configuration

**Reasoning**

- **A. Incorrect.** The option proposes “It guarantees no drift”; it makes a universal guarantee that the evidence does not support; controller and provider behavior depends on explicit policy, version, and observed state.
- **B. Correct.** Repository boundaries are an organizational/security trade-off, not a guarantee.
- **C. Incorrect.** The option proposes “It eliminates the need for reviews”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.
- **D. Incorrect.** The option proposes “It makes tags immutable”; a mutable tag can point to different bytes over time and therefore does not prove the exact artifact that was tested or ran.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses rebuild separately for production with verified state, or skips the required safety check: A rebuild may produce different artifact bytes and weaken promotion traceability.

**Operational caveat**

Repository topology and approval rules are organizational choices. Verify actual branch/path protections and retain the exact config commit used for promotion.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U04-Q06 — A production overlay changed without an owner review. What is the primary concern?

- **Unit / topic:** Repository layout and multi-environment promotion
- **Level:** L3
- **Question type:** MCQ
- **Objective tested:** evaluate path ownership, drift, and rollback implications
- **Estimated time:** 3 minutes

**Question / scenario**

A production overlay changed without an owner review. What is the primary concern?

A. The YAML indentation is always invalid
B. Production promotion may bypass the intended change-control and ownership boundary
C. Git cannot track directory changes
D. It proves the container image was compromised

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**B**. Production promotion may bypass the intended change-control and ownership boundary

**Reasoning**

- **A. Incorrect.** The option proposes “The YAML indentation is always invalid”; it makes a universal guarantee that the evidence does not support; controller and provider behavior depends on explicit policy, version, and observed state.
- **B. Correct.** First preserve PR/commit and policy evidence, then enforce the repository's actual review rules.
- **C. Incorrect.** The option proposes “Git cannot track directory changes”; Git records intent and review context but does not by itself prove what the cluster ran or that every required approval/promotion record exists.
- **D. Incorrect.** The option proposes “It proves the container image was compromised”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses rebuild separately for production with verified state, or skips the required safety check: A rebuild may produce different artifact bytes and weaken promotion traceability.

**Operational caveat**

Repository topology and approval rules are organizational choices. Verify actual branch/path protections and retain the exact config commit used for promotion.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U04-Q07 — Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Repository layout and mult

- **Unit / topic:** Repository layout and multi-environment promotion
- **Level:** L2
- **Question type:** output interpretation
- **Objective tested:** compare repository and environment promotion patterns
- **Estimated time:** 7 minutes

**Question / scenario**

Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Repository layout and multi-environment promotion:

```text
SIMULATED / REPRESENTATIVE
DEV:     commit cafe123, image digest sha256:aaaa...
STAGE:   commit cafe123, image digest sha256:aaaa..., tests PASS
PROD:    commit cafe123, image digest sha256:bbbb..., tests UNKNOWN
Release question: did production receive the artifact validated in staging? No.
```

State what is established, what remains unknown, the safest next diagnostic step, and whether you would promote, reconcile, pause, abort, or gather more evidence. Justify the decision using specific fields/lines above.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Dev and stage both use digest `aaaa...`, but production uses `bbbb...` and its tests are UNKNOWN. Therefore production has not been shown to run the exact artifact tested in staging. Block promotion or investigate the provenance mapping; update production to the validated digest via reviewed configuration change and verify the live runtime identity.

**Reasoning**

Output interpretation must separate observations from inference. A status or event can be stale, partial, or scoped to a single resource; the next check should target the earliest missing/failed link and preserve the current evidence.

**Common wrong answers**

- **Assume the best because one field is green.** That ignores contradictory fields and coverage gaps.
- **Mutate immediately.** Diagnose source, identity, scope, and rollback safety first unless containment urgency requires a minimal authorized action.

**Operational caveat**

All output is simulated; it is not claimed to come from a live cluster. Exact CLI output and controller status wording are `[VERIFY]` for the installed version.

**Scoring rubric**

Full credit: cite two specific fields, identify one unknown, choose a safe next action, and explain promotion/rollback constraints (4 points).

</details>

---

### U04-Q08 — Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Repository layout and mult

- **Unit / topic:** Repository layout and multi-environment promotion
- **Level:** L3
- **Question type:** output interpretation
- **Objective tested:** promote the same immutable artifact through environments with reviewable changes
- **Estimated time:** 8 minutes

**Question / scenario**

Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Repository layout and multi-environment promotion:

```text
SIMULATED / REPRESENTATIVE
PR #482 changes environments/prod/orders-api/image to tag v2.4.0
No required owner review recorded
The tag was rebuilt after staging
Config commit: 9f00abc
```

State what is established, what remains unknown, the safest next diagnostic step, and whether you would promote, reconcile, pause, abort, or gather more evidence. Justify the decision using specific fields/lines above.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

PR #482 uses a mutable tag, lacks required owner review, and the tag was rebuilt after staging. The config commit identifies the config change but not necessarily the bytes deployed. Find the build-to-digest mapping, validate approvals, then promote the immutable digest that passed stage tests; if the original digest cannot be recovered, report the artifact identity as UNKNOWN.

**Reasoning**

Output interpretation must separate observations from inference. A status or event can be stale, partial, or scoped to a single resource; the next check should target the earliest missing/failed link and preserve the current evidence.

**Common wrong answers**

- **Assume the best because one field is green.** That ignores contradictory fields and coverage gaps.
- **Mutate immediately.** Diagnose source, identity, scope, and rollback safety first unless containment urgency requires a minimal authorized action.

**Operational caveat**

All output is simulated; it is not claimed to come from a live cluster. Exact CLI output and controller status wording are `[VERIFY]` for the installed version.

**Scoring rubric**

Full credit: cite two specific fields, identify one unknown, choose a safe next action, and explain promotion/rollback constraints (4 points).

</details>

---

### U04-Q09 — Review this `INTENTIONALLY FLAWED` example for Repository layout and multi-environment promotio

- **Unit / topic:** Repository layout and multi-environment promotion
- **Level:** L3
- **Question type:** configuration/manifest review
- **Objective tested:** compare repository and environment promotion patterns
- **Estimated time:** 10 minutes

**Question / scenario**

Review this `INTENTIONALLY FLAWED` example for Repository layout and multi-environment promotion. Identify at least three distinct defects, explain their operational impact, and propose a corrected version or exact correction.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: {name: orders-api}
spec:
  selector: {matchLabels: {app: orders-api}}
  template:
    metadata: {labels: {app: orders-api}}
    spec:
      containers:
      - name: api
        image: registry.example.invalid/orders-api:v2.4.0
```

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The defects are:

1. A mutable version tag is used instead of the exact digest tested in staging.
2. No release evidence or promotion link records which artifact passed stage tests.
3. The deployment example omits production ownership/review metadata and assumes the tag is stable.

**Corrected direction/snippet:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: {name: orders-api}
spec:
  selector: {matchLabels: {app: orders-api}}
  template:
    metadata: {labels: {app: orders-api}}
    spec:
      containers:
      - name: api
        image: registry.example.invalid/orders-api@sha256:REPLACE_WITH_REAL_DIGEST
# Record the digest tested in staging and promote the same digest after production approvals.
```

The correction is an instructional pattern; confirm product-specific schema and provider support before applying it.

**Reasoning**

The defects are not merely style issues: they can make resources fail to select, weaken access boundaries, make the artifact mutable, trigger unintended deletion, leak sensitive data, or convert missing evidence into an unsafe action. Corrections must be tested in a disposable environment.

**Common wrong answers**

- **Fix only syntax.** A valid manifest can still be insecure or semantically unsafe.
- **Assume an illustrative snippet is a complete deployable CRD.** Required fields and semantics depend on the installed API/version.

**Operational caveat**

The original is intentionally flawed and must not be applied. Corrected snippets may be bounded examples rather than complete production configuration; `[VERIFY]` any controller-specific fields.

**Scoring rubric**

Full credit: at least three distinct defects (3 points), impact for each (3), corrected snippet/direction (2), version/safety caveat (2).

</details>

---

### U04-Q10 — Review this `INTENTIONALLY FLAWED` example for Repository layout and multi-environment promotio

- **Unit / topic:** Repository layout and multi-environment promotion
- **Level:** L3
- **Question type:** configuration/manifest review
- **Objective tested:** promote the same immutable artifact through environments with reviewable changes
- **Estimated time:** 10 minutes

**Question / scenario**

Review this `INTENTIONALLY FLAWED` example for Repository layout and multi-environment promotion. Identify at least three distinct defects, explain their operational impact, and propose a corrected version or exact correction.

```yaml
# environments/prod/orders-api/kustomization.yaml
resources:
- ../../base
images:
- name: registry.example.invalid/orders-api
  newTag: latest
# All environment overlays are writable by every developer; no path owners.
```

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The defects are:

1. The `latest` tag is mutable and makes environment identity ambiguous.
2. The snippet gives no protected-path/required-review control.
3. The shared base/overlay promotion does not record the tested artifact digest or an approval/change ID.

**Corrected direction/snippet:**

```yaml
# environments/prod/orders-api/kustomization.yaml
resources:
- ../../base
images:
- name: registry.example.invalid/orders-api
  digest: sha256:REPLACE_WITH_REAL_DIGEST
# Configure protected production paths and required owners/reviews in the Git provider.
```

The correction is an instructional pattern; confirm product-specific schema and provider support before applying it.

**Reasoning**

The defects are not merely style issues: they can make resources fail to select, weaken access boundaries, make the artifact mutable, trigger unintended deletion, leak sensitive data, or convert missing evidence into an unsafe action. Corrections must be tested in a disposable environment.

**Common wrong answers**

- **Fix only syntax.** A valid manifest can still be insecure or semantically unsafe.
- **Assume an illustrative snippet is a complete deployable CRD.** Required fields and semantics depend on the installed API/version.

**Operational caveat**

The original is intentionally flawed and must not be applied. Corrected snippets may be bounded examples rather than complete production configuration; `[VERIFY]` any controller-specific fields.

**Scoring rubric**

Full credit: at least three distinct defects (3 points), impact for each (3), corrected snippet/direction (2), version/safety caveat (2).

</details>

---

### U04-Q11 — Incident: Staging passed digest D, but the production pipeline rebuilds source and deploys dige

- **Unit / topic:** Repository layout and multi-environment promotion
- **Level:** L4
- **Question type:** incident/troubleshooting
- **Objective tested:** evaluate path ownership, drift, and rollback implications
- **Estimated time:** 15 minutes

**Question / scenario**

Incident: Staging passed digest D, but the production pipeline rebuilds source and deploys digest E from the same commit. A defect appears only in production.

Provide symptom → diagnosis → evidence to preserve → blast-radius and rollback-safety check → containment/recovery → prevention. Identify one residual uncertainty that must not be presented as fact.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**Symptom:** Staging passed digest D, but the production pipeline rebuilds source and deploys digest E from the same commit. A defect appears only in production.

**Diagnosis:** Repository strategy is a trade-off among ownership, autonomy, visibility, and operational complexity. No single-repo or multi-repo pattern is universally best.

**Evidence:** collect the relevant Git revision/PR, controller conditions/events, live resource state, runtime/metric samples, timestamps, and actor/approval data as applicable.

**Blast radius and rollback:** identify affected environments/replicas/consumers, determine whether state/data/external side effects changed, and test whether the prior version can safely read current state. Do not assume an image rollback reverses data.

**Containment/recovery:** use the smallest authorized reversible action; pause promotion or isolate the affected path if warranted; preserve a before/after record; reconcile the intended fix into the declared source; verify customer-facing behavior.

**Prevention:** Branch, tag, and directory promotion models can work if authority and merge rules are explicit; uncontrolled environment branches create drift and ambiguous truth.

**Residual uncertainty:** any missing history, unknown consumer behavior, unparseable runtime identity, or absent metric sample remains UNKNOWN until corroborated.

**Reasoning**

The incident response separates preserving evidence from containment, makes recovery contingent on state compatibility, and verifies both control-plane convergence and application-level outcome.

**Common wrong answers**

- **Immediately force-sync/redeploy without preserving evidence.** This can erase the live state that explains the incident.
- **Assume rollback is safe because the previous artifact exists.** Data, schema, event, or external side effects may be incompatible.

**Operational caveat**

Escalate to the incident commander/security owner when compromise or regulated data is plausible. Use only approved break-glass authority and an explicit reconciliation/review path.

**Scoring rubric**

10 points: diagnosis 2; evidence 2; blast radius/rollback 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### U04-Q12 — Design traceable multi-environment promotion

- **Unit / topic:** — Repository layout and multi-environment promotion
- **Level:** — L4
- **Question type:** — design
- **Objective tested:** — design a safe, auditable workflow for repository layout and multi-environment promotion
- **Estimated time:** — 20 minutes

**Question / scenario**

Design a repository and promotion strategy for dev, staging, and production that balances review overhead, environment drift, ownership, and rollback.

**Deliverables expected:** a component/workflow diagram, ownership and evidence table, failure modes, rollback/recovery path, and a short decision record. State assumptions and include at least two viable alternatives.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Compare a single repository with environment overlays against separate application/config repositories or controlled environment branches. Whichever model is chosen, enforce protected paths, explicit owners, reviewed promotion commits, immutable artifact digests, and traceable rollback commits. Define how config-only changes, emergency fixes, and environment-specific secrets are handled.

**Reasoning**

No repository topology is universally best. The key properties are traceable authority, minimal accidental coupling, consistent artifact identity, and an operationally clear promotion/rollback path.

**Common wrong answers**

- **Rebuild separately for production** — A rebuild may produce different artifact bytes and weaken promotion traceability.
- **Treat a branch or directory name as an approval** — Authorization depends on configured protections, review evidence, and ownership.

**Operational caveat**

Repository design should reflect team size, release cadence, and governance. Confirm the actual tree and branch protections rather than assuming them.

**Scoring rubric**

10 points: safety/correctness 2; evidence and verification 2; alternatives and trade-offs 2; failure/recovery plan 2; ownership, clarity, and unresolved uncertainty 2.

</details>

---

# Unit 5 — Configuration and secret reference management (12 questions)

### U05-Q01 — Explain the core model for configuration/secret separation, least privilege, rotation, leak res

- **Unit / topic:** Configuration and secret reference management
- **Level:** L1
- **Question type:** conceptual
- **Objective tested:** distinguish configuration values from secret material and secret references
- **Estimated time:** 6 minutes

**Question / scenario**

Explain the core model for configuration/secret separation, least privilege, rotation, leak response. In your answer, distinguish the desired configuration, the controller or process that acts on it, and the evidence that shows whether the intended outcome actually occurred.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Non-sensitive configuration can live in Git; secret material should be held by an approved secret-management system or a reviewed encrypted workflow. A reference is not itself proof that the target secret exists or is authorized.

**Reasoning**

Secret management is a lifecycle control: storage, read/decrypt permissions, delivery, rotation, revocation, logging, history, and backup copies all matter. A manifest change alone cannot establish that an exposed credential is no longer usable.

**Common wrong answers**

- **Delete the secret line and stop** Copies may remain in history, logs, caches, artifacts, or backups; rotate/revoke the credential.
- **Put a replacement secret in ordinary YAML** Secret material should be delivered through a controlled secret mechanism with least privilege.

**Operational caveat**

Secret-provider refresh, mount, encryption, and revocation behavior depend on tooling. Use placeholders only and test rotation/rollback with disposable credentials.

**Scoring rubric**

Full credit (3 points): states the core mechanism accurately (1), distinguishes what the evidence does and does not prove (1), and identifies a safe next check or operational implication (1).

</details>

---

### U05-Q02 — Respond to a plaintext secret committed to Git

- **Unit / topic:** — Configuration and secret reference management
- **Level:** — L2
- **Question type:** — conceptual
- **Objective tested:** — predict and verify respond to a plaintext secret committed to git
- **Estimated time:** — 7 minutes

**Question / scenario**

A developer removes a plaintext password from the latest YAML commit after it was pushed to Git. Is the secret exposure resolved? State the immediate response and longer-term cleanup.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

No. The credential may remain in Git history, clones, caches, CI logs, artifacts, or backups. Revoke or rotate it first, assess access and use, remove the secret from current configuration, replace it with a controlled secret reference, and perform history cleanup only under an approved plan. Verify consumers and audit access to the old credential.

**Reasoning**

Removing a value from the current file does not invalidate copies or undo credential exposure. Containment and rotation are distinct from repository hygiene.

**Common wrong answers**

- **Delete the secret line and stop** — Copies may remain in history, logs, caches, artifacts, or backups; rotate/revoke the credential.
- **Put a replacement secret in ordinary YAML** — Secret material should be delivered through a controlled secret mechanism with least privilege.

**Operational caveat**

Secret-provider APIs and encryption patterns depend on the installed tooling. Use unmistakable placeholders and verify rotation behavior and audit logging.

**Scoring rubric**

Full credit (3 points): states the correct operational conclusion (1), cites the evidence/policy that supports it (1), and names a safe next check plus a remaining uncertainty (1).

</details>

---

### U05-Q03 — Rotate a credential while old and new replicas overlap

- **Unit / topic:** — Configuration and secret reference management
- **Level:** — L3
- **Question type:** — conceptual
- **Objective tested:** — diagnose and recover safely from rotate a credential while old and new replicas overlap
- **Estimated time:** — 8 minutes

**Question / scenario**

A secret must rotate during a progressive rollout, and old and new replicas overlap. What compatibility and access checks determine a safe sequence?

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Determine whether consumers can accept both old and new credentials during overlap, how revocation propagates, and whether restart/reload is required. Introduce the new credential with least privilege, verify consumers, roll replicas gradually, confirm no remaining use of the old value, then revoke it and retain redacted rotation evidence.

**Reasoning**

Rotation is a distributed transition: the producer, secret store, workloads, and rollback path must agree on the overlap window.

**Common wrong answers**

- **Delete the secret line and stop** — Copies may remain in history, logs, caches, artifacts, or backups; rotate/revoke the credential.
- **Put a replacement secret in ordinary YAML** — Secret material should be delivered through a controlled secret mechanism with least privilege.

**Operational caveat**

Provider-specific refresh intervals and mount semantics must be verified. Test the rotation path in a disposable environment and define a rollback/expiry plan.

**Scoring rubric**

Full credit (4 points): identifies the relevant state/evidence (1), orders diagnosis before mutation (1), checks blast radius and rollback/data compatibility (1), and defines verification/prevention (1).

</details>

---

### U05-Q04 — A token was committed and then deleted in a later commit. What must happen first?

- **Unit / topic:** Configuration and secret reference management
- **Level:** L1
- **Question type:** MCQ
- **Objective tested:** distinguish configuration values from secret material and secret references
- **Estimated time:** 3 minutes

**Question / scenario**

A token was committed and then deleted in a later commit. What must happen first?

A. Assume deletion revoked the token
B. Revoke/rotate the exposed credential and investigate where it propagated
C. Only squash the branch
D. Disable all logging permanently

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**B**. Revoke/rotate the exposed credential and investigate where it propagated

**Reasoning**

- **A. Incorrect.** The option proposes “Assume deletion revoked the token”; it proposes an unsafe shortcut without first establishing authorization, impact, evidence preservation, and a recovery path.
- **B. Correct.** Git history and other copies may retain the secret; credential revocation is the urgent control.
- **C. Incorrect.** The option proposes “Only squash the branch”; it narrows the decision to one signal and omits the other required checks, such as ownership, runtime state, telemetry quality, or recovery safety.
- **D. Incorrect.** The option proposes “Disable all logging permanently”; it proposes an unsafe shortcut without first establishing authorization, impact, evidence preservation, and a recovery path.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses delete the secret line and stop with verified state, or skips the required safety check: Copies may remain in history, logs, caches, artifacts, or backups; rotate/revoke the credential.

**Operational caveat**

Secret-provider refresh, mount, encryption, and revocation behavior depend on tooling. Use placeholders only and test rotation/rollback with disposable credentials.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U05-Q05 — What is the main benefit of a secret reference?

- **Unit / topic:** Configuration and secret reference management
- **Level:** L2
- **Question type:** MCQ
- **Objective tested:** evaluate least privilege, rotation, and leak-response procedures
- **Estimated time:** 3 minutes

**Question / scenario**

What is the main benefit of a secret reference?

A. It makes secret values public but encoded
B. It separates workload configuration from secret material and enables controlled retrieval/rotation
C. It guarantees every pod has permission
D. It eliminates the need for access logs

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**B**. It separates workload configuration from secret material and enables controlled retrieval/rotation

**Reasoning**

- **A. Incorrect.** The option proposes “It makes secret values public but encoded”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.
- **B. Correct.** References support separation but authorization, availability, and rotation still need verification.
- **C. Incorrect.** The option proposes “It guarantees every pod has permission”; it makes a universal guarantee that the evidence does not support; controller and provider behavior depends on explicit policy, version, and observed state.
- **D. Incorrect.** The option proposes “It eliminates the need for access logs”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses delete the secret line and stop with verified state, or skips the required safety check: Copies may remain in history, logs, caches, artifacts, or backups; rotate/revoke the credential.

**Operational caveat**

Secret-provider refresh, mount, encryption, and revocation behavior depend on tooling. Use placeholders only and test rotation/rollback with disposable credentials.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U05-Q06 — During rotation, what is the safest approach for a service that cannot switch all replicas inst

- **Unit / topic:** Configuration and secret reference management
- **Level:** L3
- **Question type:** MCQ
- **Objective tested:** detect secret exposure in manifests and Git history
- **Estimated time:** 3 minutes

**Question / scenario**

During rotation, what is the safest approach for a service that cannot switch all replicas instantly?

A. Revoke old credentials before distributing new credentials in every case
B. Use a controlled overlap if the secret system and threat policy allow it, verify all consumers, then revoke old material
C. Put both values in Git
D. Disable readiness checks

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**B**. Use a controlled overlap if the secret system and threat policy allow it, verify all consumers, then revoke old material

**Reasoning**

- **A. Incorrect.** The option proposes “Revoke old credentials before distributing new credentials in every case”; it makes a universal guarantee that the evidence does not support; controller and provider behavior depends on explicit policy, version, and observed state.
- **B. Correct.** The exact overlap policy depends on credential risk and provider capabilities; prove consumer migration before revocation.
- **C. Incorrect.** The option proposes “Put both values in Git”; it proposes an unsafe shortcut without first establishing authorization, impact, evidence preservation, and a recovery path.
- **D. Incorrect.** The option proposes “Disable readiness checks”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses delete the secret line and stop with verified state, or skips the required safety check: Copies may remain in history, logs, caches, artifacts, or backups; rotate/revoke the credential.

**Operational caveat**

Secret-provider refresh, mount, encryption, and revocation behavior depend on tooling. Use placeholders only and test rotation/rollback with disposable credentials.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U05-Q07 — Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Configuration and secret r

- **Unit / topic:** Configuration and secret reference management
- **Level:** L2
- **Question type:** output interpretation
- **Objective tested:** distinguish configuration values from secret material and secret references
- **Estimated time:** 7 minutes

**Question / scenario**

Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Configuration and secret reference management:

```text
SIMULATED / REPRESENTATIVE
Current manifest: secretRef.name=orders-api-token
Git history scan: commit 7aa001 contains a plaintext token-like value
Token status: still active
Registry/build logs: not yet checked
```

State what is established, what remains unknown, the safest next diagnostic step, and whether you would promote, reconcile, pause, abort, or gather more evidence. Justify the decision using specific fields/lines above.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The current manifest uses a secret reference, but the history scan found a token-like value in commit `7aa001` and the token is still active. The exposure is not remediated by deleting the current value. Revoke/rotate first, investigate Git history, CI logs, images, caches and backups, and record the incident. Only then perform approved history cleanup and verify consumers use the new credential.

**Reasoning**

Output interpretation must separate observations from inference. A status or event can be stale, partial, or scoped to a single resource; the next check should target the earliest missing/failed link and preserve the current evidence.

**Common wrong answers**

- **Assume the best because one field is green.** That ignores contradictory fields and coverage gaps.
- **Mutate immediately.** Diagnose source, identity, scope, and rollback safety first unless containment urgency requires a minimal authorized action.

**Operational caveat**

All output is simulated; it is not claimed to come from a live cluster. Exact CLI output and controller status wording are `[VERIFY]` for the installed version.

**Scoring rubric**

Full credit: cite two specific fields, identify one unknown, choose a safe next action, and explain promotion/rollback constraints (4 points).

</details>

---

### U05-Q08 — Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Configuration and secret r

- **Unit / topic:** Configuration and secret reference management
- **Level:** L3
- **Question type:** output interpretation
- **Objective tested:** evaluate least privilege, rotation, and leak-response procedures
- **Estimated time:** 8 minutes

**Question / scenario**

Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Configuration and secret reference management:

```text
SIMULATED / REPRESENTATIVE
Rotation timeline:
10:00 new secret version created
10:02 60% pods restarted
10:04 old token revoked
10:05 remaining 40% pods report authentication failures
```

State what is established, what remains unknown, the safest next diagnostic step, and whether you would promote, reconcile, pause, abort, or gather more evidence. Justify the decision using specific fields/lines above.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Only 60% of pods restarted before the old token was revoked; the remaining 40% now fail authentication. The rotation sequence created an availability gap. Restore service through the approved credential recovery path, verify every replica/consumer, and design a bounded overlap or coordinated reload plan if policy permits. Do not put credentials into Git to simplify rotation.

**Reasoning**

Output interpretation must separate observations from inference. A status or event can be stale, partial, or scoped to a single resource; the next check should target the earliest missing/failed link and preserve the current evidence.

**Common wrong answers**

- **Assume the best because one field is green.** That ignores contradictory fields and coverage gaps.
- **Mutate immediately.** Diagnose source, identity, scope, and rollback safety first unless containment urgency requires a minimal authorized action.

**Operational caveat**

All output is simulated; it is not claimed to come from a live cluster. Exact CLI output and controller status wording are `[VERIFY]` for the installed version.

**Scoring rubric**

Full credit: cite two specific fields, identify one unknown, choose a safe next action, and explain promotion/rollback constraints (4 points).

</details>

---

### U05-Q09 — Review this `INTENTIONALLY FLAWED` example for Configuration and secret reference management. I

- **Unit / topic:** Configuration and secret reference management
- **Level:** L3
- **Question type:** configuration/manifest review
- **Objective tested:** distinguish configuration values from secret material and secret references
- **Estimated time:** 10 minutes

**Question / scenario**

Review this `INTENTIONALLY FLAWED` example for Configuration and secret reference management. Identify at least three distinct defects, explain their operational impact, and propose a corrected version or exact correction.

```yaml
apiVersion: v1
kind: Secret
metadata: {name: orders-api-token, namespace: orders-prod}
type: Opaque
stringData:
  token: "EXAMPLE-BUT-DO-NOT-USE-A-REAL-TOKEN"
```

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The defects are:

1. Secret material is placed directly in a Kubernetes Secret manifest in Git; base64/`stringData` is not a secret-management boundary.
2. There is no evidence that the value is externally provisioned, encrypted in repository storage, or access-restricted.
3. The example has no rotation/incident process and may preserve the secret in Git history.

**Corrected direction/snippet:**

```yaml
# Store only a reference in workload configuration.
# The Secret object itself must be populated by an approved secret controller/workflow.
apiVersion: apps/v1
kind: Deployment
metadata: {name: orders-api}
spec:
  selector: {matchLabels: {app: orders-api}}
  template:
    metadata: {labels: {app: orders-api}}
    spec:
      containers:
      - name: api
        image: registry.example.invalid/orders-api@sha256:REPLACE_WITH_REAL_DIGEST
        env:
        - name: API_TOKEN
          valueFrom:
            secretKeyRef: {name: orders-api-token, key: token}
```

The correction is an instructional pattern; confirm product-specific schema and provider support before applying it.

**Reasoning**

The defects are not merely style issues: they can make resources fail to select, weaken access boundaries, make the artifact mutable, trigger unintended deletion, leak sensitive data, or convert missing evidence into an unsafe action. Corrections must be tested in a disposable environment.

**Common wrong answers**

- **Fix only syntax.** A valid manifest can still be insecure or semantically unsafe.
- **Assume an illustrative snippet is a complete deployable CRD.** Required fields and semantics depend on the installed API/version.

**Operational caveat**

The original is intentionally flawed and must not be applied. Corrected snippets may be bounded examples rather than complete production configuration; `[VERIFY]` any controller-specific fields.

**Scoring rubric**

Full credit: at least three distinct defects (3 points), impact for each (3), corrected snippet/direction (2), version/safety caveat (2).

</details>

---

### U05-Q10 — Review this `INTENTIONALLY FLAWED` example for Configuration and secret reference management. I

- **Unit / topic:** Configuration and secret reference management
- **Level:** L3
- **Question type:** configuration/manifest review
- **Objective tested:** evaluate least privilege, rotation, and leak-response procedures
- **Estimated time:** 10 minutes

**Question / scenario**

Review this `INTENTIONALLY FLAWED` example for Configuration and secret reference management. Identify at least three distinct defects, explain their operational impact, and propose a corrected version or exact correction.

```yaml
apiVersion: v1
kind: ConfigMap
metadata: {name: app-config}
data:
  API_TOKEN: "DO_NOT_USE_REAL_SECRET"
  LOG_LEVEL: debug
  allow-untrusted-tls: "true"
```

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The defects are:

1. A token is stored in a ConfigMap, which is intended for non-confidential configuration.
2. `allow-untrusted-tls: true` weakens transport authentication.
3. Debug-level logging is an unsafe production default unless explicitly justified and bounded.

**Corrected direction/snippet:**

```yaml
apiVersion: v1
kind: ConfigMap
metadata: {name: app-config}
data:
  LOG_LEVEL: info
  allow-untrusted-tls: "false"
# API_TOKEN belongs in a secret manager/reference, not ConfigMap data. Validate TLS behavior before promotion.
```

The correction is an instructional pattern; confirm product-specific schema and provider support before applying it.

**Reasoning**

The defects are not merely style issues: they can make resources fail to select, weaken access boundaries, make the artifact mutable, trigger unintended deletion, leak sensitive data, or convert missing evidence into an unsafe action. Corrections must be tested in a disposable environment.

**Common wrong answers**

- **Fix only syntax.** A valid manifest can still be insecure or semantically unsafe.
- **Assume an illustrative snippet is a complete deployable CRD.** Required fields and semantics depend on the installed API/version.

**Operational caveat**

The original is intentionally flawed and must not be applied. Corrected snippets may be bounded examples rather than complete production configuration; `[VERIFY]` any controller-specific fields.

**Scoring rubric**

Full credit: at least three distinct defects (3 points), impact for each (3), corrected snippet/direction (2), version/safety caveat (2).

</details>

---

### U05-Q11 — Incident: A developer removes a plaintext API token from the current YAML but does not revoke i

- **Unit / topic:** Configuration and secret reference management
- **Level:** L4
- **Question type:** incident/troubleshooting
- **Objective tested:** detect secret exposure in manifests and Git history
- **Estimated time:** 15 minutes

**Question / scenario**

Incident: A developer removes a plaintext API token from the current YAML but does not revoke it; a prior commit still contains the value.

Provide symptom → diagnosis → evidence to preserve → blast-radius and rollback-safety check → containment/recovery → prevention. Identify one residual uncertainty that must not be presented as fact.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**Symptom:** A developer removes a plaintext API token from the current YAML but does not revoke it; a prior commit still contains the value.

**Diagnosis:** Non-sensitive configuration can live in Git; secret material should be held by an approved secret-management system or a reviewed encrypted workflow. A reference is not itself proof that the target secret exists or is authorized.

**Evidence:** collect the relevant Git revision/PR, controller conditions/events, live resource state, runtime/metric samples, timestamps, and actor/approval data as applicable.

**Blast radius and rollback:** identify affected environments/replicas/consumers, determine whether state/data/external side effects changed, and test whether the prior version can safely read current state. Do not assume an image rollback reverses data.

**Containment/recovery:** use the smallest authorized reversible action; pause promotion or isolate the affected path if warranted; preserve a before/after record; reconcile the intended fix into the declared source; verify customer-facing behavior.

**Prevention:** Deleting a leaked secret from the latest commit does not invalidate copies in Git history, caches, logs, images, or backups. Revoke/rotate first, then clean history under an approved plan.

**Residual uncertainty:** any missing history, unknown consumer behavior, unparseable runtime identity, or absent metric sample remains UNKNOWN until corroborated.

**Reasoning**

The incident response separates preserving evidence from containment, makes recovery contingent on state compatibility, and verifies both control-plane convergence and application-level outcome.

**Common wrong answers**

- **Immediately force-sync/redeploy without preserving evidence.** This can erase the live state that explains the incident.
- **Assume rollback is safe because the previous artifact exists.** Data, schema, event, or external side effects may be incompatible.

**Operational caveat**

Escalate to the incident commander/security owner when compromise or regulated data is plausible. Use only approved break-glass authority and an explicit reconciliation/review path.

**Scoring rubric**

10 points: diagnosis 2; evidence 2; blast radius/rollback 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### U05-Q12 — Design secret-reference and rotation governance

- **Unit / topic:** — Configuration and secret reference management
- **Level:** — L4
- **Question type:** — design
- **Objective tested:** — design a safe, auditable workflow for configuration and secret reference management
- **Estimated time:** — 20 minutes

**Question / scenario**

Design secret-reference management for a Kubernetes service with rotation, least privilege, leak response, and GitOps review requirements.

**Deliverables expected:** a component/workflow diagram, ownership and evidence table, failure modes, rollback/recovery path, and a short decision record. State assumptions and include at least two viable alternatives.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Keep secret material out of ordinary Git manifests and evidence bundles; store references in desired state and use a controlled secret system or an explicitly supported encrypted-data pattern. Scope read/decrypt permissions, define rotation overlap and revocation, audit access, redact logs, and document leak response plus repository-history cleanup.

**Reasoning**

Secret security depends on the full lifecycle—creation, storage, access, delivery, rotation, logging, backup, and revocation—not just encryption at rest.

**Common wrong answers**

- **Delete the secret line and stop** — Copies may remain in history, logs, caches, artifacts, or backups; rotate/revoke the credential.
- **Put a replacement secret in ordinary YAML** — Secret material should be delivered through a controlled secret mechanism with least privilege.

**Operational caveat**

Exact external-secret and encryption-controller features are version/tool-specific. Verify implementation and never put real credentials in this assessment.

**Scoring rubric**

10 points: safety/correctness 2; evidence and verification 2; alternatives and trade-offs 2; failure/recovery plan 2; ownership, clarity, and unresolved uncertainty 2.

</details>

---

# Unit 6 — Deployment drift detection and reconciliation (12 questions)

### U06-Q01 — Explain the core model for drift classification, safe reconcile, break-glass, field ownership. 

- **Unit / topic:** Deployment drift detection and reconciliation
- **Level:** L1
- **Question type:** conceptual
- **Objective tested:** distinguish unauthorized drift from expected mutation/defaulting
- **Estimated time:** 6 minutes

**Question / scenario**

Explain the core model for drift classification, safe reconcile, break-glass, field ownership. In your answer, distinguish the desired configuration, the controller or process that acts on it, and the evidence that shows whether the intended outcome actually occurred.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Drift is a difference between declared and observed state, but not every diff is malicious or actionable: defaults, admission mutation, operators, and controllers may legitimately alter fields.

**Reasoning**

A live diff is a signal to classify, not an automatic instruction to overwrite. Correlate Git, audit identity/time, admission/defaulting, field ownership, and incident context before choosing reconcile, accept, or escalate.

**Common wrong answers**

- **Reconcile every difference immediately** A diff may be expected mutation or an active emergency change; classify and preserve evidence first.
- **Ignore every unexplained difference** That hides unauthorized changes and creates unbounded drift.

**Operational caveat**

Admission mutation, managed fields, audit logs, and ignore-difference mechanisms vary by Kubernetes/controller version. Verify the cause before changing reconciliation policy.

**Scoring rubric**

Full credit (3 points): states the core mechanism accurately (1), distinguishes what the evidence does and does not prove (1), and identifies a safe next check or operational implication (1).

</details>

---

### U06-Q02 — Classify admission mutation versus unauthorized drift

- **Unit / topic:** — Deployment drift detection and reconciliation
- **Level:** — L2
- **Question type:** — conceptual
- **Objective tested:** — predict and verify classify admission mutation versus unauthorized drift
- **Estimated time:** — 7 minutes

**Question / scenario**

A live field differs from Git, but the difference may be an admission-controller default or mutation. How do you distinguish expected mutation from unauthorized drift before reconciling?

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Capture the diff and timestamp, identify the field owner and admission/defaulting behavior, compare the rendered manifest and live object, inspect audit events and recent changes, then classify the difference. Reconcile accidental drift; document and explicitly model accepted mutation; escalate unexplained or security-sensitive changes. Do not blindly overwrite evidence.

**Reasoning**

Drift is a discrepancy, not automatically an unauthorized action. Classification prevents both destructive remediation and permanent acceptance of malicious changes.

**Common wrong answers**

- **Reconcile every difference immediately** — A diff may be expected mutation or an active emergency change; classify and preserve evidence first.
- **Ignore every unexplained difference** — That hides unauthorized changes and creates unbounded drift.

**Operational caveat**

Managed fields and admission behavior vary by API/version. Confirm the source of mutation and preserve audit evidence before remediation.

**Scoring rubric**

Full credit (3 points): states the correct operational conclusion (1), cites the evidence/policy that supports it (1), and names a safe next check plus a remaining uncertainty (1).

</details>

---

### U06-Q03 — Respond to a break-glass change that was reverted

- **Unit / topic:** — Deployment drift detection and reconciliation
- **Level:** — L3
- **Question type:** — conceptual
- **Objective tested:** — diagnose and recover safely from respond to a break-glass change that was reverted
- **Estimated time:** — 8 minutes

**Question / scenario**

During an incident, an operator makes a break-glass change that the controller later reverts. Describe the safe process for deciding whether to preserve, roll back, or reconcile that change.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Record actor, time, reason, resource diff, incident ID, and observed impact. Decide with the incident owner whether the hotfix is still needed; assess compatibility and blast radius; then either restore the prior desired state or create a reviewed Git change representing the accepted fix. Verify convergence and close the exception with an owner and expiry.

**Reasoning**

Break-glass is an exception with an evidence and reconciliation obligation, not a permanent alternative source of truth.

**Common wrong answers**

- **Reconcile every difference immediately** — A diff may be expected mutation or an active emergency change; classify and preserve evidence first.
- **Ignore every unexplained difference** — That hides unauthorized changes and creates unbounded drift.

**Operational caveat**

Exact drift-ignore rules and reconciliation policies are controller-specific. Verify before changing them, and test remediation on disposable resources.

**Scoring rubric**

Full credit (4 points): identifies the relevant state/evidence (1), orders diagnosis before mutation (1), checks blast radius and rollback/data compatibility (1), and defines verification/prevention (1).

</details>

---

### U06-Q04 — A diff shows an injected sidecar annotation added by an admission webhook. What is the best nex

- **Unit / topic:** Deployment drift detection and reconciliation
- **Level:** L1
- **Question type:** MCQ
- **Objective tested:** distinguish unauthorized drift from expected mutation/defaulting
- **Estimated time:** 3 minutes

**Question / scenario**

A diff shows an injected sidecar annotation added by an admission webhook. What is the best next step?

A. Immediately delete the annotation from production
B. Classify field ownership and expected mutation before deciding whether it is actionable drift
C. Disable admission permanently
D. Assume the whole cluster is compromised

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**B**. Classify field ownership and expected mutation before deciding whether it is actionable drift

**Reasoning**

- **A. Incorrect.** The option proposes “Immediately delete the annotation from production”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.
- **B. Correct.** A raw diff is not enough to classify drift; determine source, ownership, and intended policy.
- **C. Incorrect.** The option proposes “Disable admission permanently”; it proposes an unsafe shortcut without first establishing authorization, impact, evidence preservation, and a recovery path.
- **D. Incorrect.** The option proposes “Assume the whole cluster is compromised”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses reconcile every difference immediately with verified state, or skips the required safety check: A diff may be expected mutation or an active emergency change; classify and preserve evidence first.

**Operational caveat**

Admission mutation, managed fields, audit logs, and ignore-difference mechanisms vary by Kubernetes/controller version. Verify the cause before changing reconciliation policy.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U06-Q05 — During a security incident, an unexplained image change appears in live state. What should happ

- **Unit / topic:** Deployment drift detection and reconciliation
- **Level:** L2
- **Question type:** MCQ
- **Objective tested:** apply detect-classify-decide-reconcile workflow safely
- **Estimated time:** 3 minutes

**Question / scenario**

During a security incident, an unexplained image change appears in live state. What should happen before self-heal overwrites it?

A. Preserve relevant evidence and assess impact, then reconcile according to incident procedure
B. Delete all pod logs
C. Assume it was a harmless admission default
D. Force-push Git history

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**A**. Preserve relevant evidence and assess impact, then reconcile according to incident procedure

**Reasoning**

- **A. Correct.** Reconciliation can erase the live manifestation; preserve evidence without delaying necessary containment.
- **B. Incorrect.** The option proposes “Delete all pod logs”; it proposes an unsafe shortcut without first establishing authorization, impact, evidence preservation, and a recovery path.
- **C. Incorrect.** The option proposes “Assume it was a harmless admission default”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.
- **D. Incorrect.** The option proposes “Force-push Git history”; it proposes an unsafe shortcut without first establishing authorization, impact, evidence preservation, and a recovery path.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses reconcile every difference immediately with verified state, or skips the required safety check: A diff may be expected mutation or an active emergency change; classify and preserve evidence first.

**Operational caveat**

Admission mutation, managed fields, audit logs, and ignore-difference mechanisms vary by Kubernetes/controller version. Verify the cause before changing reconciliation policy.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U06-Q06 — What completes a break-glass change?

- **Unit / topic:** Deployment drift detection and reconciliation
- **Level:** L3
- **Question type:** MCQ
- **Objective tested:** preserve emergency changes and reconcile them back into desired state
- **Estimated time:** 3 minutes

**Question / scenario**

What completes a break-glass change?

A. A successful kubectl command only
B. A permanent exception to GitOps
C. An authorized, bounded change plus evidence, post-hoc review, and reconciliation into Git
D. A screenshot alone

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**C**. An authorized, bounded change plus evidence, post-hoc review, and reconciliation into Git

**Reasoning**

- **A. Incorrect.** The option proposes “A successful kubectl command only”; it narrows the decision to one signal and omits the other required checks, such as ownership, runtime state, telemetry quality, or recovery safety.
- **B. Incorrect.** The option proposes “A permanent exception to GitOps”; Git records intent and review context but does not by itself prove what the cluster ran or that every required approval/promotion record exists.
- **C. Correct.** The emergency path should be time-bounded and auditable, with desired state restored to a coherent source of truth.
- **D. Incorrect.** The option proposes “A screenshot alone”; it is not an independently correlated record of the required actor, artifact, approval, or runtime event.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses reconcile every difference immediately with verified state, or skips the required safety check: A diff may be expected mutation or an active emergency change; classify and preserve evidence first.

**Operational caveat**

Admission mutation, managed fields, audit logs, and ignore-difference mechanisms vary by Kubernetes/controller version. Verify the cause before changing reconciliation policy.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U06-Q07 — Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Deployment drift detection

- **Unit / topic:** Deployment drift detection and reconciliation
- **Level:** L2
- **Question type:** output interpretation
- **Objective tested:** distinguish unauthorized drift from expected mutation/defaulting
- **Estimated time:** 7 minutes

**Question / scenario**

Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Deployment drift detection and reconciliation:

```text
SIMULATED / REPRESENTATIVE
Desired replicas: 4
Live replicas: 6
Desired annotation: team=orders
Live annotation: team=orders, admission.example/sidecar-injected=true
Desired resources.requests.cpu: 250m
Live resources.requests.cpu: 500m
```

State what is established, what remains unknown, the safest next diagnostic step, and whether you would promote, reconcile, pause, abort, or gather more evidence. Justify the decision using specific fields/lines above.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The three differences have different owners: the injected sidecar annotation is expected admission mutation; replicas differ while an HPA is active, so field ownership needs confirmation; image digest A versus B is unexplained and should be preserved/investigated. Do not treat all diffs as malicious or globally ignore them. Inspect audit actor, managed fields, admission config, HPA status, and runtime image identity.

**Reasoning**

Output interpretation must separate observations from inference. A status or event can be stale, partial, or scoped to a single resource; the next check should target the earliest missing/failed link and preserve the current evidence.

**Common wrong answers**

- **Assume the best because one field is green.** That ignores contradictory fields and coverage gaps.
- **Mutate immediately.** Diagnose source, identity, scope, and rollback safety first unless containment urgency requires a minimal authorized action.

**Operational caveat**

All output is simulated; it is not claimed to come from a live cluster. Exact CLI output and controller status wording are `[VERIFY]` for the installed version.

**Scoring rubric**

Full credit: cite two specific fields, identify one unknown, choose a safe next action, and explain promotion/rollback constraints (4 points).

</details>

---

### U06-Q08 — Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Deployment drift detection

- **Unit / topic:** Deployment drift detection and reconciliation
- **Level:** L3
- **Question type:** output interpretation
- **Objective tested:** apply detect-classify-decide-reconcile workflow safely
- **Estimated time:** 8 minutes

**Question / scenario**

Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Deployment drift detection and reconciliation:

```text
SIMULATED / REPRESENTATIVE
Drift scan: 3 differences
1. sidecar injection annotation: owned by admission webhook (expected)
2. replicas: 4 desired / 6 live (HPA active; owner needs confirmation)
3. image digest: desired A / live B (unexplained; preserve evidence and investigate)
```

State what is established, what remains unknown, the safest next diagnostic step, and whether you would promote, reconcile, pause, abort, or gather more evidence. Justify the decision using specific fields/lines above.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The image digest mismatch is the highest-priority unexplained change; the replica count may be HPA-owned and the sidecar annotation is expected mutation. Capture current object and audit records, assess impact and incident scope, then decide whether to reconcile. This output illustrates why drift needs classification before remediation rather than a blanket `kubectl apply`.

**Reasoning**

Output interpretation must separate observations from inference. A status or event can be stale, partial, or scoped to a single resource; the next check should target the earliest missing/failed link and preserve the current evidence.

**Common wrong answers**

- **Assume the best because one field is green.** That ignores contradictory fields and coverage gaps.
- **Mutate immediately.** Diagnose source, identity, scope, and rollback safety first unless containment urgency requires a minimal authorized action.

**Operational caveat**

All output is simulated; it is not claimed to come from a live cluster. Exact CLI output and controller status wording are `[VERIFY]` for the installed version.

**Scoring rubric**

Full credit: cite two specific fields, identify one unknown, choose a safe next action, and explain promotion/rollback constraints (4 points).

</details>

---

### U06-Q09 — Review this `INTENTIONALLY FLAWED` example for Deployment drift detection and reconciliation. I

- **Unit / topic:** Deployment drift detection and reconciliation
- **Level:** L3
- **Question type:** configuration/manifest review
- **Objective tested:** distinguish unauthorized drift from expected mutation/defaulting
- **Estimated time:** 10 minutes

**Question / scenario**

Review this `INTENTIONALLY FLAWED` example for Deployment drift detection and reconciliation. Identify at least three distinct defects, explain their operational impact, and propose a corrected version or exact correction.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: {name: orders-api}
spec:
  replicas: 4
  selector: {matchLabels: {app: orders-api}}
  template:
    metadata: {labels: {app: orders-api}}
    spec:
      containers:
      - name: api
        image: registry.example.invalid/orders-api:latest
```

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The defects are:

1. The Deployment uses a mutable `latest` tag, obscuring the source of image drift.
2. `replicas: 4` may conflict with an HPA that owns scaling.
3. The example does not classify or preserve unexplained live drift before reconciliation.

**Corrected direction/snippet:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: {name: orders-api}
spec:
  # If HPA owns scale, avoid competing desired replicas or define a supported field-ownership strategy.
  selector: {matchLabels: {app: orders-api}}
  template:
    metadata: {labels: {app: orders-api}}
    spec:
      containers:
      - name: api
        image: registry.example.invalid/orders-api@sha256:REPLACE_WITH_REAL_DIGEST
# Confirm exact controller ownership and diff behavior before changing ignore rules.
```

The correction is an instructional pattern; confirm product-specific schema and provider support before applying it.

**Reasoning**

The defects are not merely style issues: they can make resources fail to select, weaken access boundaries, make the artifact mutable, trigger unintended deletion, leak sensitive data, or convert missing evidence into an unsafe action. Corrections must be tested in a disposable environment.

**Common wrong answers**

- **Fix only syntax.** A valid manifest can still be insecure or semantically unsafe.
- **Assume an illustrative snippet is a complete deployable CRD.** Required fields and semantics depend on the installed API/version.

**Operational caveat**

The original is intentionally flawed and must not be applied. Corrected snippets may be bounded examples rather than complete production configuration; `[VERIFY]` any controller-specific fields.

**Scoring rubric**

Full credit: at least three distinct defects (3 points), impact for each (3), corrected snippet/direction (2), version/safety caveat (2).

</details>

---

### U06-Q10 — Review this `INTENTIONALLY FLAWED` example for Deployment drift detection and reconciliation. I

- **Unit / topic:** Deployment drift detection and reconciliation
- **Level:** L3
- **Question type:** configuration/manifest review
- **Objective tested:** apply detect-classify-decide-reconcile workflow safely
- **Estimated time:** 10 minutes

**Question / scenario**

Review this `INTENTIONALLY FLAWED` example for Deployment drift detection and reconciliation. Identify at least three distinct defects, explain their operational impact, and propose a corrected version or exact correction.

```text
# Emergency procedure
1. kubectl edit deployment orders-api
2. Ignore GitOps alerts
3. Close incident when pods are Ready
4. Never record the patch in Git to avoid review delays
```

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The defects are:

1. The procedure starts with a live edit without confirming authority, context, scope, or recovery.
2. It explicitly discards evidence and ignores GitOps/controller alerts.
3. It forbids reconciliation into Git and has no owner, expiry, post-hoc review, or runtime verification.

**Corrected direction/snippet:**

```text
# Emergency procedure (illustrative)
1. Confirm context, incident authority, scope, and rollback path.
2. Capture current object, actor/time, diff, events, and relevant logs securely.
3. Apply the smallest authorized change and observe customer impact.
4. Open an emergency change record with owner and expiry.
5. Reconcile the intended state into a reviewed Git change; verify controller convergence.
6. Complete post-hoc review under the organization's defined policy window.
```

The correction is an instructional pattern; confirm product-specific schema and provider support before applying it.

**Reasoning**

The defects are not merely style issues: they can make resources fail to select, weaken access boundaries, make the artifact mutable, trigger unintended deletion, leak sensitive data, or convert missing evidence into an unsafe action. Corrections must be tested in a disposable environment.

**Common wrong answers**

- **Fix only syntax.** A valid manifest can still be insecure or semantically unsafe.
- **Assume an illustrative snippet is a complete deployable CRD.** Required fields and semantics depend on the installed API/version.

**Operational caveat**

The original is intentionally flawed and must not be applied. Corrected snippets may be bounded examples rather than complete production configuration; `[VERIFY]` any controller-specific fields.

**Scoring rubric**

Full credit: at least three distinct defects (3 points), impact for each (3), corrected snippet/direction (2), version/safety caveat (2).

</details>

---

### U06-Q11 — Incident: A manual resource limit change is detected during an incident. Self-heal would restor

- **Unit / topic:** Deployment drift detection and reconciliation
- **Level:** L4
- **Question type:** incident/troubleshooting
- **Objective tested:** preserve emergency changes and reconcile them back into desired state
- **Estimated time:** 15 minutes

**Question / scenario**

Incident: A manual resource limit change is detected during an incident. Self-heal would restore the old limit, but the current value may be preventing an outage.

Provide symptom → diagnosis → evidence to preserve → blast-radius and rollback-safety check → containment/recovery → prevention. Identify one residual uncertainty that must not be presented as fact.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**Symptom:** A manual resource limit change is detected during an incident. Self-heal would restore the old limit, but the current value may be preventing an outage.

**Diagnosis:** Drift is a difference between declared and observed state, but not every diff is malicious or actionable: defaults, admission mutation, operators, and controllers may legitimately alter fields.

**Evidence:** collect the relevant Git revision/PR, controller conditions/events, live resource state, runtime/metric samples, timestamps, and actor/approval data as applicable.

**Blast radius and rollback:** identify affected environments/replicas/consumers, determine whether state/data/external side effects changed, and test whether the prior version can safely read current state. Do not assume an image rollback reverses data.

**Containment/recovery:** use the smallest authorized reversible action; pause promotion or isolate the affected path if warranted; preserve a before/after record; reconcile the intended fix into the declared source; verify customer-facing behavior.

**Prevention:** Break-glass is an exception path, not an alternate permanent operating model. Record actor, time, reason, scope, expiry, approval, and the corresponding Git reconciliation.

**Residual uncertainty:** any missing history, unknown consumer behavior, unparseable runtime identity, or absent metric sample remains UNKNOWN until corroborated.

**Reasoning**

The incident response separates preserving evidence from containment, makes recovery contingent on state compatibility, and verifies both control-plane convergence and application-level outcome.

**Common wrong answers**

- **Immediately force-sync/redeploy without preserving evidence.** This can erase the live state that explains the incident.
- **Assume rollback is safe because the previous artifact exists.** Data, schema, event, or external side effects may be incompatible.

**Operational caveat**

Escalate to the incident commander/security owner when compromise or regulated data is plausible. Use only approved break-glass authority and an explicit reconciliation/review path.

**Scoring rubric**

10 points: diagnosis 2; evidence 2; blast radius/rollback 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### U06-Q12 — Design drift classification and break-glass governance

- **Unit / topic:** — Deployment drift detection and reconciliation
- **Level:** — L4
- **Question type:** — design
- **Objective tested:** — design a safe, auditable workflow for deployment drift detection and reconciliation
- **Estimated time:** — 20 minutes

**Question / scenario**

Design a drift-governance workflow that detects, classifies, records, and resolves both accidental and emergency live changes.

**Deliverables expected:** a component/workflow diagram, ownership and evidence table, failure modes, rollback/recovery path, and a short decision record. State assumptions and include at least two viable alternatives.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Implement detect → classify → decide → reconcile/accept/record. Correlate Git desired state, live diff, Kubernetes audit actor/time, admission mutations, controller events, and incident records. Define severity-based response, break-glass authorization, exception owner/expiry, and how accepted changes are represented in Git or policy. Measure repeat drift and verify remediation.

**Reasoning**

Detection and remediation are separate decisions. A safe workflow preserves evidence, identifies ownership, and only then chooses a reversible correction.

**Common wrong answers**

- **Reconcile every difference immediately** — A diff may be expected mutation or an active emergency change; classify and preserve evidence first.
- **Ignore every unexplained difference** — That hides unauthorized changes and creates unbounded drift.

**Operational caveat**

Use explicit field ownership and controller-specific ignore mechanisms only after verification; never assume all live differences have the same cause.

**Scoring rubric**

10 points: safety/correctness 2; evidence and verification 2; alternatives and trade-offs 2; failure/recovery plan 2; ownership, clarity, and unresolved uncertainty 2.

</details>

---

# Unit 7 — Progressive delivery: canary and blue-green releases (12 questions)

### U07-Q01 — Explain the core model for rolling/canary/blue-green, traffic, blast radius, state compatibilit

- **Unit / topic:** Progressive delivery: canary and blue-green releases
- **Level:** L1
- **Question type:** conceptual
- **Objective tested:** choose delivery strategies based on traffic, state, and recovery constraints
- **Estimated time:** 6 minutes

**Question / scenario**

Explain the core model for rolling/canary/blue-green, traffic, blast radius, state compatibility. In your answer, distinguish the desired configuration, the controller or process that acts on it, and the evidence that shows whether the intended outcome actually occurred.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Rolling updates replace replicas incrementally; canary exposes a subset of traffic or users; blue-green runs two environments and switches traffic; dark launch exercises code without exposing results to users.

**Reasoning**

Replica count and traffic exposure are different measurements. Release decisions must use measured exposure and health over an adequate window, and rollback requires compatibility checks for data and side effects.

**Common wrong answers**

- **Use replica percentage as traffic percentage** Routing, session affinity, and request distribution can make exposure very different.
- **Rollback only based on CPU or pod readiness** Business SLIs and data/state compatibility also determine release safety.

**Operational caveat**

Traffic routing depends on the service mesh, ingress, or rollout provider. Confirm measured traffic exposure and state compatibility before promotion or rollback.

**Scoring rubric**

Full credit (3 points): states the core mechanism accurately (1), distinguishes what the evidence does and does not prove (1), and identifies a safe next check or operational implication (1).

</details>

---

### U07-Q02 — Measure canary traffic rather than replica share

- **Unit / topic:** — Progressive delivery: canary and blue-green releases
- **Level:** — L2
- **Question type:** — conceptual
- **Objective tested:** — predict and verify measure canary traffic rather than replica share
- **Estimated time:** — 7 minutes

**Question / scenario**

A Deployment has three replicas and one is running the new version. Can the team claim that 33% of user traffic reaches the canary? What evidence would establish exposure?

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

No. Replica fraction does not establish request traffic fraction. Traffic may be uneven due to routing, session affinity, connection reuse, endpoint selection, or workload distribution. Verify the traffic router/service configuration and measure requests by stable/canary version over a defined window with enough samples.

**Reasoning**

Canary exposure is a traffic/user measurement, not merely a pod count. A strategy must control and observe actual exposure.

**Common wrong answers**

- **Use replica percentage as traffic percentage** — Routing, session affinity, and request distribution can make exposure very different.
- **Rollback only based on CPU or pod readiness** — Business SLIs and data/state compatibility also determine release safety.

**Operational caveat**

Exact traffic routing depends on ingress/service-mesh/provider setup. Verify installed configuration and metrics labels before making exposure claims.

**Scoring rubric**

Full credit (3 points): states the correct operational conclusion (1), cites the evidence/policy that supports it (1), and names a safe next check plus a remaining uncertainty (1).

</details>

---

### U07-Q03 — Decide on a canary with business regression after migration

- **Unit / topic:** — Progressive delivery: canary and blue-green releases
- **Level:** — L3
- **Question type:** — conceptual
- **Objective tested:** — diagnose and recover safely from decide on a canary with business regression after migration
- **Estimated time:** — 8 minutes

**Question / scenario**

A canary is healthy on CPU but has a rising business error rate and a database migration has already run. What should govern promotion or rollback?

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Pause or abort further exposure according to the pre-agreed guardrail, preserve metrics and rollout evidence, and assess customer impact. Before rollback, verify whether the old version can read the migrated schema and whether writes or side effects are reversible. If not, roll forward with a compatible fix or use a tested recovery plan rather than assuming an image rollback is safe.

**Reasoning**

Progressive delivery decisions require both infrastructure and business SLIs, plus state compatibility. A healthy resource is not equivalent to a healthy release.

**Common wrong answers**

- **Use replica percentage as traffic percentage** — Routing, session affinity, and request distribution can make exposure very different.
- **Rollback only based on CPU or pod readiness** — Business SLIs and data/state compatibility also determine release safety.

**Operational caveat**

Traffic-routing behavior and analysis integration are version-sensitive. Confirm the actual exposure and migration state before acting.

**Scoring rubric**

Full credit (4 points): identifies the relevant state/evidence (1), orders diagnosis before mutation (1), checks blast radius and rollback/data compatibility (1), and defines verification/prevention (1).

</details>

---

### U07-Q04 — A canary has one of three replicas but receives 0.2% of requests. What does replica count prove

- **Unit / topic:** Progressive delivery: canary and blue-green releases
- **Level:** L1
- **Question type:** MCQ
- **Objective tested:** choose delivery strategies based on traffic, state, and recovery constraints
- **Estimated time:** 3 minutes

**Question / scenario**

A canary has one of three replicas but receives 0.2% of requests. What does replica count prove?

A. That exactly one-third of traffic reached canary
B. Only that one of three replicas is assigned to the canary workload; traffic share must be measured separately
C. That the release is safe
D. That the router is misconfigured in every case

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**B**. Only that one of three replicas is assigned to the canary workload; traffic share must be measured separately

**Reasoning**

- **A. Incorrect.** The option proposes “That exactly one-third of traffic reached canary”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.
- **B. Correct.** Replica fraction and traffic fraction are different quantities.
- **C. Incorrect.** The option proposes “That the release is safe”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.
- **D. Incorrect.** The option proposes “That the router is misconfigured in every case”; it makes a universal guarantee that the evidence does not support; controller and provider behavior depends on explicit policy, version, and observed state.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses use replica percentage as traffic percentage with verified state, or skips the required safety check: Routing, session affinity, and request distribution can make exposure very different.

**Operational caveat**

Traffic routing depends on the service mesh, ingress, or rollout provider. Confirm measured traffic exposure and state compatibility before promotion or rollback.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U07-Q05 — Which signal should dominate if CPU is normal but checkout failures rise materially?

- **Unit / topic:** Progressive delivery: canary and blue-green releases
- **Level:** L2
- **Question type:** MCQ
- **Objective tested:** distinguish replica fraction from measured traffic fraction
- **Estimated time:** 3 minutes

**Question / scenario**

Which signal should dominate if CPU is normal but checkout failures rise materially?

A. CPU alone
B. Business-level failure signal, with the rollout policy evaluating severity and data quality
C. The container tag
D. Replica count

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**B**. Business-level failure signal, with the rollout policy evaluating severity and data quality

**Reasoning**

- **A. Incorrect.** The option proposes “CPU alone”; CPU alone does not establish customer-facing correctness; the stated business SLI and sample quality must be evaluated too.
- **B. Correct.** Infrastructure health is necessary but insufficient when business outcomes regress.
- **C. Incorrect.** The option proposes “The container tag”; a mutable tag can point to different bytes over time and therefore does not prove the exact artifact that was tested or ran.
- **D. Incorrect.** The option proposes “Replica count”; declared replica topology or an image reference does not by itself establish measured traffic distribution, runtime identity, or application health.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses use replica percentage as traffic percentage with verified state, or skips the required safety check: Routing, session affinity, and request distribution can make exposure very different.

**Operational caveat**

Traffic routing depends on the service mesh, ingress, or rollout provider. Confirm measured traffic exposure and state compatibility before promotion or rollback.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U07-Q06 — When is rollback unsafe even if the old image is available?

- **Unit / topic:** Progressive delivery: canary and blue-green releases
- **Level:** L3
- **Question type:** MCQ
- **Objective tested:** evaluate rollback feasibility when code and state evolve
- **Estimated time:** 3 minutes

**Question / scenario**

When is rollback unsafe even if the old image is available?

A. Whenever a canary was used
B. When new writes, schema, or external side effects are incompatible with the old version and no safe recovery exists
C. Only when pods use more than 1 CPU
D. Never; image rollback reverses all effects

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**B**. When new writes, schema, or external side effects are incompatible with the old version and no safe recovery exists

**Reasoning**

- **A. Incorrect.** The option proposes “Whenever a canary was used”; it makes a universal guarantee that the evidence does not support; controller and provider behavior depends on explicit policy, version, and observed state.
- **B. Correct.** Code rollback does not reverse data or external side effects; assess compatibility and roll-forward alternatives.
- **C. Incorrect.** The option proposes “Only when pods use more than 1 CPU”; CPU alone does not establish customer-facing correctness; the stated business SLI and sample quality must be evaluated too.
- **D. Incorrect.** The option proposes “Never; image rollback reverses all effects”; it makes a universal guarantee that the evidence does not support; controller and provider behavior depends on explicit policy, version, and observed state.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses use replica percentage as traffic percentage with verified state, or skips the required safety check: Routing, session affinity, and request distribution can make exposure very different.

**Operational caveat**

Traffic routing depends on the service mesh, ingress, or rollout provider. Confirm measured traffic exposure and state compatibility before promotion or rollback.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U07-Q07 — Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Progressive delivery: cana

- **Unit / topic:** Progressive delivery: canary and blue-green releases
- **Level:** L2
- **Question type:** output interpretation
- **Objective tested:** choose delivery strategies based on traffic, state, and recovery constraints
- **Estimated time:** 7 minutes

**Question / scenario**

Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Progressive delivery: canary and blue-green releases:

```text
SIMULATED / REPRESENTATIVE
Stable replicas: 3; canary replicas: 1
Observed request share over 10 min: stable 99.8%, canary 0.2%
Canary requests: 17
Canary 5xx: 0
Conclusion: sample is too small to establish safety.
```

State what is established, what remains unknown, the safest next diagnostic step, and whether you would promote, reconcile, pause, abort, or gather more evidence. Justify the decision using specific fields/lines above.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

One of four replicas is in the canary workload, but measured canary traffic is only 0.2% and only 17 requests were observed. Zero 5xx responses at that volume is insufficient evidence. Verify the traffic router/service configuration and sample coverage, then extend observation or use an approved validation strategy; do not claim a one-third traffic canary.

**Reasoning**

Output interpretation must separate observations from inference. A status or event can be stale, partial, or scoped to a single resource; the next check should target the earliest missing/failed link and preserve the current evidence.

**Common wrong answers**

- **Assume the best because one field is green.** That ignores contradictory fields and coverage gaps.
- **Mutate immediately.** Diagnose source, identity, scope, and rollback safety first unless containment urgency requires a minimal authorized action.

**Operational caveat**

All output is simulated; it is not claimed to come from a live cluster. Exact CLI output and controller status wording are `[VERIFY]` for the installed version.

**Scoring rubric**

Full credit: cite two specific fields, identify one unknown, choose a safe next action, and explain promotion/rollback constraints (4 points).

</details>

---

### U07-Q08 — Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Progressive delivery: cana

- **Unit / topic:** Progressive delivery: canary and blue-green releases
- **Level:** L3
- **Question type:** output interpretation
- **Objective tested:** distinguish replica fraction from measured traffic fraction
- **Estimated time:** 8 minutes

**Question / scenario**

Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Progressive delivery: canary and blue-green releases:

```text
SIMULATED / REPRESENTATIVE
Rollout: 20% traffic → 50% → 100%
At 50%: p95 latency stable 180 ms, canary 410 ms
Business checkout failure rate: baseline 0.4%, canary 2.8%
CPU: within limit
Analysis window: 5 minutes, 12 requests total
```

State what is established, what remains unknown, the safest next diagnostic step, and whether you would promote, reconcile, pause, abort, or gather more evidence. Justify the decision using specific fields/lines above.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

At 50% traffic the canary p95 latency is 410 ms versus 180 ms stable, and checkout failure rate is 2.8% versus 0.4% baseline. CPU being within limit does not outweigh the business regression. The 12-request sample is below a credible minimum; pause/abort per policy, validate telemetry freshness and sample count, and check state compatibility before rollback.

**Reasoning**

Output interpretation must separate observations from inference. A status or event can be stale, partial, or scoped to a single resource; the next check should target the earliest missing/failed link and preserve the current evidence.

**Common wrong answers**

- **Assume the best because one field is green.** That ignores contradictory fields and coverage gaps.
- **Mutate immediately.** Diagnose source, identity, scope, and rollback safety first unless containment urgency requires a minimal authorized action.

**Operational caveat**

All output is simulated; it is not claimed to come from a live cluster. Exact CLI output and controller status wording are `[VERIFY]` for the installed version.

**Scoring rubric**

Full credit: cite two specific fields, identify one unknown, choose a safe next action, and explain promotion/rollback constraints (4 points).

</details>

---

### U07-Q09 — Review this `INTENTIONALLY FLAWED` example for Progressive delivery: canary and blue-green rele

- **Unit / topic:** Progressive delivery: canary and blue-green releases
- **Level:** L3
- **Question type:** configuration/manifest review
- **Objective tested:** choose delivery strategies based on traffic, state, and recovery constraints
- **Estimated time:** 10 minutes

**Question / scenario**

Review this `INTENTIONALLY FLAWED` example for Progressive delivery: canary and blue-green releases. Identify at least three distinct defects, explain their operational impact, and propose a corrected version or exact correction.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: {name: orders-api}
spec:
  replicas: 1
  selector: {matchLabels: {app: orders-api}}
  template:
    metadata: {labels: {app: orders-api, track: canary}}
    spec:
      containers:
      - name: api
        image: registry.example.invalid/orders-api:v-next
```

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The defects are:

1. The image uses a mutable tag rather than a pinned candidate digest.
2. A canary label alone does not define traffic routing or a measured traffic split.
3. There is no staged health gate or minimum-sample requirement before promotion.

**Corrected direction/snippet:**

```yaml
# Deployment labels alone do not create a traffic percentage.
# Define the controller/traffic-provider integration and explicit weight steps for the selected platform.
# Pin the candidate artifact by digest and require sufficient request/sample volume before promotion.
apiVersion: apps/v1
kind: Deployment
metadata: {name: orders-api-canary}
spec:
  selector: {matchLabels: {app: orders-api, track: canary}}
  template:
    metadata: {labels: {app: orders-api, track: canary}}
    spec:
      containers:
      - name: api
        image: registry.example.invalid/orders-api@sha256:REPLACE_WITH_REAL_DIGEST
```

The correction is an instructional pattern; confirm product-specific schema and provider support before applying it.

**Reasoning**

The defects are not merely style issues: they can make resources fail to select, weaken access boundaries, make the artifact mutable, trigger unintended deletion, leak sensitive data, or convert missing evidence into an unsafe action. Corrections must be tested in a disposable environment.

**Common wrong answers**

- **Fix only syntax.** A valid manifest can still be insecure or semantically unsafe.
- **Assume an illustrative snippet is a complete deployable CRD.** Required fields and semantics depend on the installed API/version.

**Operational caveat**

The original is intentionally flawed and must not be applied. Corrected snippets may be bounded examples rather than complete production configuration; `[VERIFY]` any controller-specific fields.

**Scoring rubric**

Full credit: at least three distinct defects (3 points), impact for each (3), corrected snippet/direction (2), version/safety caveat (2).

</details>

---

### U07-Q10 — Review this `INTENTIONALLY FLAWED` example for Progressive delivery: canary and blue-green rele

- **Unit / topic:** Progressive delivery: canary and blue-green releases
- **Level:** L3
- **Question type:** configuration/manifest review
- **Objective tested:** distinguish replica fraction from measured traffic fraction
- **Estimated time:** 10 minutes

**Question / scenario**

Review this `INTENTIONALLY FLAWED` example for Progressive delivery: canary and blue-green releases. Identify at least three distinct defects, explain their operational impact, and propose a corrected version or exact correction.

```yaml
# rollout policy (illustrative, not a controller CRD)
strategy: canary
steps:
- setWeight: 50
- pause: 1s
analysis:
  metric: cpu_percent
  threshold: 95
  onEmpty: pass
rollback: always-safe
```

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The defects are:

1. The policy is explicitly not a controller schema but could be mistaken for deployable configuration.
2. A one-second pause is not a justified observation window for the workload.
3. Empty metrics pass and rollback is declared always safe, ignoring data/state compatibility.

**Corrected direction/snippet:**

```yaml
# rollout policy intent (translate to the installed controller/provider schema)
strategy: canary
steps:
- setWeight: 5
- observe: business error rate, latency, saturation and minimum sample count
- increase gradually only when data is fresh and sufficient
analysis_on_missing_data: inconclusive_or_abort_per_policy
rollback: verify state/data compatibility before restoring old code
```

The correction is an instructional pattern; confirm product-specific schema and provider support before applying it.

**Reasoning**

The defects are not merely style issues: they can make resources fail to select, weaken access boundaries, make the artifact mutable, trigger unintended deletion, leak sensitive data, or convert missing evidence into an unsafe action. Corrections must be tested in a disposable environment.

**Common wrong answers**

- **Fix only syntax.** A valid manifest can still be insecure or semantically unsafe.
- **Assume an illustrative snippet is a complete deployable CRD.** Required fields and semantics depend on the installed API/version.

**Operational caveat**

The original is intentionally flawed and must not be applied. Corrected snippets may be bounded examples rather than complete production configuration; `[VERIFY]` any controller-specific fields.

**Scoring rubric**

Full credit: at least three distinct defects (3 points), impact for each (3), corrected snippet/direction (2), version/safety caveat (2).

</details>

---

### U07-Q11 — Incident: A one-of-three replica canary looks healthy by CPU, but the traffic router still send

- **Unit / topic:** Progressive delivery: canary and blue-green releases
- **Level:** L4
- **Question type:** incident/troubleshooting
- **Objective tested:** evaluate rollback feasibility when code and state evolve
- **Estimated time:** 15 minutes

**Question / scenario**

Incident: A one-of-three replica canary looks healthy by CPU, but the traffic router still sends nearly all requests to the stable service.

Provide symptom → diagnosis → evidence to preserve → blast-radius and rollback-safety check → containment/recovery → prevention. Identify one residual uncertainty that must not be presented as fact.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**Symptom:** A one-of-three replica canary looks healthy by CPU, but the traffic router still sends nearly all requests to the stable service.

**Diagnosis:** Rolling updates replace replicas incrementally; canary exposes a subset of traffic or users; blue-green runs two environments and switches traffic; dark launch exercises code without exposing results to users.

**Evidence:** collect the relevant Git revision/PR, controller conditions/events, live resource state, runtime/metric samples, timestamps, and actor/approval data as applicable.

**Blast radius and rollback:** identify affected environments/replicas/consumers, determine whether state/data/external side effects changed, and test whether the prior version can safely read current state. Do not assume an image rollback reverses data.

**Containment/recovery:** use the smallest authorized reversible action; pause promotion or isolate the affected path if warranted; preserve a before/after record; reconcile the intended fix into the declared source; verify customer-facing behavior.

**Prevention:** Rollback safety depends on database/event/data compatibility and side effects, not only whether an old image remains available. Define health gates, observation windows, capacity, and abort criteria before rollout.

**Residual uncertainty:** any missing history, unknown consumer behavior, unparseable runtime identity, or absent metric sample remains UNKNOWN until corroborated.

**Reasoning**

The incident response separates preserving evidence from containment, makes recovery contingent on state compatibility, and verifies both control-plane convergence and application-level outcome.

**Common wrong answers**

- **Immediately force-sync/redeploy without preserving evidence.** This can erase the live state that explains the incident.
- **Assume rollback is safe because the previous artifact exists.** Data, schema, event, or external side effects may be incompatible.

**Operational caveat**

Escalate to the incident commander/security owner when compromise or regulated data is plausible. Use only approved break-glass authority and an explicit reconciliation/review path.

**Scoring rubric**

10 points: diagnosis 2; evidence 2; blast radius/rollback 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### U07-Q12 — Design progressive delivery with rollback constraints

- **Unit / topic:** — Progressive delivery: canary and blue-green releases
- **Level:** — L4
- **Question type:** — design
- **Objective tested:** — design a safe, auditable workflow for progressive delivery: canary and blue-green releases
- **Estimated time:** — 20 minutes

**Question / scenario**

Design progressive delivery for a stateful production service, including canary exposure, health gates, and rollback constraints.

**Deliverables expected:** a component/workflow diagram, ownership and evidence table, failure modes, rollback/recovery path, and a short decision record. State assumptions and include at least two viable alternatives.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Use a staged rollout with explicit stable/canary routing, a measured traffic split, minimum sample counts, business and infrastructure SLIs, and pause/abort criteria. Define capacity limits and a rollback decision that checks schema, persisted data, and side effects. Capture rollout status, metric window, decision, and post-recovery verification.

**Reasoning**

Canary safety depends on actual exposure and the ability to recover state, not on replica percentages alone.

**Common wrong answers**

- **Use replica percentage as traffic percentage** — Routing, session affinity, and request distribution can make exposure very different.
- **Rollback only based on CPU or pod readiness** — Business SLIs and data/state compatibility also determine release safety.

**Operational caveat**

Traffic-routing and rollout-controller behavior depend on installed integrations. Verify provider configuration and test rollback with production-like state.

**Scoring rubric**

10 points: safety/correctness 2; evidence and verification 2; alternatives and trade-offs 2; failure/recovery plan 2; ownership, clarity, and unresolved uncertainty 2.

</details>

---

# Unit 8 — Argo Rollouts, Flagger, and traffic-based analysis (12 questions)

### U08-Q01 — Explain the core model for rollout controllers, analysis results, traffic providers, promotion/

- **Unit / topic:** Argo Rollouts, Flagger, and traffic-based analysis
- **Level:** L1
- **Question type:** conceptual
- **Objective tested:** distinguish rollout-controller roles from Kubernetes Deployment mechanics
- **Estimated time:** 6 minutes

**Question / scenario**

Explain the core model for rollout controllers, analysis results, traffic providers, promotion/abort. In your answer, distinguish the desired configuration, the controller or process that acts on it, and the evidence that shows whether the intended outcome actually occurred.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Argo Rollouts and Flagger coordinate progressive delivery with Kubernetes resources and supported traffic/metrics integrations. Their APIs and provider capabilities are version-dependent.

**Reasoning**

A rollout controller's step/status is not the same as traffic routing or valid analysis. Verify provider configuration, stable/canary exposure, measurement freshness, sample size, and installed CRD behavior.

**Common wrong answers**

- **Treat a completed rollout step as proof of traffic exposure** Routing and actual request counters must corroborate the intended split.
- **Treat missing analysis as a pass** Absent samples cannot establish health; use the configured inconclusive/fail-safe path.

**Operational caveat**

Argo Rollouts/Flagger CRDs and provider integrations are version-sensitive. Verify exact schemas and missing-data policy against the installed release.

**Scoring rubric**

Full credit (3 points): states the core mechanism accurately (1), distinguishes what the evidence does and does not prove (1), and identifies a safe next check or operational implication (1).

</details>

---

### U08-Q02 — Handle an AnalysisRun with no samples

- **Unit / topic:** — Argo Rollouts, Flagger, and traffic-based analysis
- **Level:** — L2
- **Question type:** — conceptual
- **Objective tested:** — predict and verify handle an analysisrun with no samples
- **Estimated time:** — 7 minutes

**Question / scenario**

An AnalysisRun has no samples for the observation window. Should the rollout pass, fail, or remain inconclusive? Define the safe default and next checks.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Missing samples are not evidence of health. Under a fail-closed release policy, the rollout should remain inconclusive or abort/pause according to the explicitly configured policy, rather than silently pass. Check query correctness, provider availability, labels, time window, traffic volume, and sample freshness before retrying.

**Reasoning**

Analysis quality is part of the decision. A threshold cannot be evaluated if the measurement is absent or invalid.

**Common wrong answers**

- **Treat a completed rollout step as proof of traffic exposure** — Routing and actual request counters must corroborate the intended split.
- **Treat missing analysis as a pass** — Absent samples cannot establish health; use the configured inconclusive/fail-safe path.

**Operational caveat**

Exact AnalysisTemplate/AnalysisRun schemas and inconclusive policies vary by version/provider. Verify CRDs and installed documentation.

**Scoring rubric**

Full credit (3 points): states the correct operational conclusion (1), cites the evidence/policy that supports it (1), and names a safe next check plus a remaining uncertainty (1).

</details>

---

### U08-Q03 — Verify traffic routing before promotion

- **Unit / topic:** — Argo Rollouts, Flagger, and traffic-based analysis
- **Level:** — L3
- **Question type:** — conceptual
- **Objective tested:** — diagnose and recover safely from verify traffic routing before promotion
- **Estimated time:** — 8 minutes

**Question / scenario**

A rollout controller reports that a canary step completed, but observed traffic remains on the stable service. How should the team verify routing and avoid a false promotion?

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Compare rollout step/status with the traffic provider configuration, stable/canary service selectors, ingress/service-mesh routes, and request counters labelled by version. Confirm enough requests reached the canary during the observation window; if exposure is unproven, do not treat analysis as representative. Pause promotion and fix routing in a reviewed change.

**Reasoning**

Controller progression and actual traffic exposure are separate facts. A completed step does not by itself prove the intended percentage of requests reached the new version.

**Common wrong answers**

- **Treat a completed rollout step as proof of traffic exposure** — Routing and actual request counters must corroborate the intended split.
- **Treat missing analysis as a pass** — Absent samples cannot establish health; use the configured inconclusive/fail-safe path.

**Operational caveat**

Exact routing integrations and CRD fields are version-specific. Validate the provider integration against the installed release.

**Scoring rubric**

Full credit (4 points): identifies the relevant state/evidence (1), orders diagnosis before mutation (1), checks blast radius and rollback/data compatibility (1), and defines verification/prevention (1).

</details>

---

### U08-Q04 — An AnalysisRun has 12 samples but policy requires at least 100. What is the correct conclusion?

- **Unit / topic:** Argo Rollouts, Flagger, and traffic-based analysis
- **Level:** L1
- **Question type:** MCQ
- **Objective tested:** distinguish rollout-controller roles from Kubernetes Deployment mechanics
- **Estimated time:** 3 minutes

**Question / scenario**

An AnalysisRun has 12 samples but policy requires at least 100. What is the correct conclusion?

A. Pass because the measured ratio is high
B. Fail automatically in every controller implementation
C. Insufficient evidence; pause/abort/inconclusive per explicit policy
D. Ignore sample count if CPU is low

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**C**. Insufficient evidence; pause/abort/inconclusive per explicit policy

**Reasoning**

- **A. Incorrect.** The option proposes “Pass because the measured ratio is high”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.
- **B. Incorrect.** The option proposes “Fail automatically in every controller implementation”; it makes a universal guarantee that the evidence does not support; controller and provider behavior depends on explicit policy, version, and observed state.
- **C. Correct.** A favorable ratio from too few samples is not strong evidence; exact controller result mapping is version/policy dependent.
- **D. Incorrect.** The option proposes “Ignore sample count if CPU is low”; CPU alone does not establish customer-facing correctness; the stated business SLI and sample quality must be evaluated too.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses treat a completed rollout step as proof of traffic exposure with verified state, or skips the required safety check: Routing and actual request counters must corroborate the intended split.

**Operational caveat**

Argo Rollouts/Flagger CRDs and provider integrations are version-sensitive. Verify exact schemas and missing-data policy against the installed release.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U08-Q05 — What must be verified when configuring a traffic-based rollout?

- **Unit / topic:** Argo Rollouts, Flagger, and traffic-based analysis
- **Level:** L2
- **Question type:** MCQ
- **Objective tested:** interpret analysis and rollout states without assuming missing data is healthy
- **Estimated time:** 3 minutes

**Question / scenario**

What must be verified when configuring a traffic-based rollout?

A. Only the Deployment replica count
B. The installed CRD schema, controller version, traffic-provider integration, services/routes, and actual traffic distribution
C. Only the image tag
D. That every metric query returns a number

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**B**. The installed CRD schema, controller version, traffic-provider integration, services/routes, and actual traffic distribution

**Reasoning**

- **A. Incorrect.** The option proposes “Only the Deployment replica count”; it narrows the decision to one signal and omits the other required checks, such as ownership, runtime state, telemetry quality, or recovery safety.
- **B. Correct.** The rollout controller and traffic provider must work together; exact fields are version-sensitive.
- **C. Incorrect.** The option proposes “Only the image tag”; a mutable tag can point to different bytes over time and therefore does not prove the exact artifact that was tested or ran.
- **D. Incorrect.** The option proposes “That every metric query returns a number”; it makes a universal guarantee that the evidence does not support; controller and provider behavior depends on explicit policy, version, and observed state.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses treat a completed rollout step as proof of traffic exposure with verified state, or skips the required safety check: Routing and actual request counters must corroborate the intended split.

**Operational caveat**

Argo Rollouts/Flagger CRDs and provider integrations are version-sensitive. Verify exact schemas and missing-data policy against the installed release.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U08-Q06 — Why is manual promotion after empty metrics dangerous?

- **Unit / topic:** Argo Rollouts, Flagger, and traffic-based analysis
- **Level:** L3
- **Question type:** MCQ
- **Objective tested:** identify version-sensitive CRDs and traffic-provider dependencies
- **Estimated time:** 3 minutes

**Question / scenario**

Why is manual promotion after empty metrics dangerous?

A. Empty metrics always mean 0% errors
B. It converts missing evidence into a release decision without demonstrating health
C. It prevents controller events
D. It makes the image digest mutable

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**B**. It converts missing evidence into a release decision without demonstrating health

**Reasoning**

- **A. Incorrect.** The option proposes “Empty metrics always mean 0% errors”; it makes a universal guarantee that the evidence does not support; controller and provider behavior depends on explicit policy, version, and observed state.
- **B. Correct.** Preserve the inconclusive state and repair telemetry or use an explicitly approved degraded-mode policy.
- **C. Incorrect.** The option proposes “It prevents controller events”; structural shape alone cannot establish semantic compatibility across real producers and consumers.
- **D. Incorrect.** The option proposes “It makes the image digest mutable”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses treat a completed rollout step as proof of traffic exposure with verified state, or skips the required safety check: Routing and actual request counters must corroborate the intended split.

**Operational caveat**

Argo Rollouts/Flagger CRDs and provider integrations are version-sensitive. Verify exact schemas and missing-data policy against the installed release.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U08-Q07 — Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Argo Rollouts, Flagger, an

- **Unit / topic:** Argo Rollouts, Flagger, and traffic-based analysis
- **Level:** L2
- **Question type:** output interpretation
- **Objective tested:** distinguish rollout-controller roles from Kubernetes Deployment mechanics
- **Estimated time:** 7 minutes

**Question / scenario**

Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Argo Rollouts, Flagger, and traffic-based analysis:

```text
SIMULATED / REPRESENTATIVE
Rollout: orders-api
Phase: Paused
Analysis result: inconclusive / no datapoints in 5m window
Traffic provider: configured
Observed candidate requests: 0
Promotion decision: not yet justified
```

State what is established, what remains unknown, the safest next diagnostic step, and whether you would promote, reconcile, pause, abort, or gather more evidence. Justify the decision using specific fields/lines above.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The rollout is paused, has no datapoints in the five-minute window, and observed candidate requests are zero. No health conclusion is supported. Keep it paused/inconclusive or abort according to the documented policy; repair traffic/metrics collection and confirm the selected provider integration before promotion.

**Reasoning**

Output interpretation must separate observations from inference. A status or event can be stale, partial, or scoped to a single resource; the next check should target the earliest missing/failed link and preserve the current evidence.

**Common wrong answers**

- **Assume the best because one field is green.** That ignores contradictory fields and coverage gaps.
- **Mutate immediately.** Diagnose source, identity, scope, and rollback safety first unless containment urgency requires a minimal authorized action.

**Operational caveat**

All output is simulated; it is not claimed to come from a live cluster. Exact CLI output and controller status wording are `[VERIFY]` for the installed version.

**Scoring rubric**

Full credit: cite two specific fields, identify one unknown, choose a safe next action, and explain promotion/rollback constraints (4 points).

</details>

---

### U08-Q08 — Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Argo Rollouts, Flagger, an

- **Unit / topic:** Argo Rollouts, Flagger, and traffic-based analysis
- **Level:** L3
- **Question type:** output interpretation
- **Objective tested:** interpret analysis and rollout states without assuming missing data is healthy
- **Estimated time:** 8 minutes

**Question / scenario**

Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Argo Rollouts, Flagger, and traffic-based analysis:

```text
SIMULATED / REPRESENTATIVE
AnalysisRun orders-api-42: Failed
metric: request_success_ratio
query window: 5m; expected samples: >= 100
observed samples: 12
observed ratio: 0.995
provider response: partial data / stale timestamp
```

State what is established, what remains unknown, the safest next diagnostic step, and whether you would promote, reconcile, pause, abort, or gather more evidence. Justify the decision using specific fields/lines above.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The AnalysisRun has 12 samples when policy expects at least 100, and the provider reports partial/stale data. The ratio 0.995 cannot override sample/freshness requirements. Treat the result as insufficient evidence, inspect query/provider timestamps and routing, and follow the predeclared pause/abort policy rather than manually promoting.

**Reasoning**

Output interpretation must separate observations from inference. A status or event can be stale, partial, or scoped to a single resource; the next check should target the earliest missing/failed link and preserve the current evidence.

**Common wrong answers**

- **Assume the best because one field is green.** That ignores contradictory fields and coverage gaps.
- **Mutate immediately.** Diagnose source, identity, scope, and rollback safety first unless containment urgency requires a minimal authorized action.

**Operational caveat**

All output is simulated; it is not claimed to come from a live cluster. Exact CLI output and controller status wording are `[VERIFY]` for the installed version.

**Scoring rubric**

Full credit: cite two specific fields, identify one unknown, choose a safe next action, and explain promotion/rollback constraints (4 points).

</details>

---

### U08-Q09 — Review this `INTENTIONALLY FLAWED` example for Argo Rollouts, Flagger, and traffic-based analys

- **Unit / topic:** Argo Rollouts, Flagger, and traffic-based analysis
- **Level:** L3
- **Question type:** configuration/manifest review
- **Objective tested:** distinguish rollout-controller roles from Kubernetes Deployment mechanics
- **Estimated time:** 10 minutes

**Question / scenario**

Review this `INTENTIONALLY FLAWED` example for Argo Rollouts, Flagger, and traffic-based analysis. Identify at least three distinct defects, explain their operational impact, and propose a corrected version or exact correction.

```yaml
# INTENTIONALLY FLAWED: illustrative only, not a complete Rollout CRD
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata: {name: orders-api}
spec:
  replicas: 3
  selector: {matchLabels: {app: orders-api}}
  template:
    metadata: {labels: {app: orders-api}}
    spec:
      containers:
      - name: api
        image: registry.example.invalid/orders-api:latest
  strategy:
    canary:
      steps:
      - setWeight: 50
```

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The defects are:

1. The image uses `latest`, so the candidate artifact is not immutable.
2. Only one 50% step is shown, with no progressive observation/analysis gates.
3. The snippet does not define or verify traffic-provider routing/services and is not a complete Rollout manifest.

**Corrected direction/snippet:**

```yaml
# Correct the defects in intent; validate exact Rollout schema and traffic-provider fields for the installed version.
# 1) Pin candidate image by digest.
# 2) Provide a complete selector/template label match.
# 3) Add explicit staged weights, pause/analysis gates, and stable/canary routing supported by the selected provider.
# 4) Treat missing/stale/low-volume metrics as inconclusive or abort according to documented policy.
```

The correction is an instructional pattern; confirm product-specific schema and provider support before applying it.

**Reasoning**

The defects are not merely style issues: they can make resources fail to select, weaken access boundaries, make the artifact mutable, trigger unintended deletion, leak sensitive data, or convert missing evidence into an unsafe action. Corrections must be tested in a disposable environment.

**Common wrong answers**

- **Fix only syntax.** A valid manifest can still be insecure or semantically unsafe.
- **Assume an illustrative snippet is a complete deployable CRD.** Required fields and semantics depend on the installed API/version.

**Operational caveat**

The original is intentionally flawed and must not be applied. Corrected snippets may be bounded examples rather than complete production configuration; `[VERIFY]` any controller-specific fields.

**Scoring rubric**

Full credit: at least three distinct defects (3 points), impact for each (3), corrected snippet/direction (2), version/safety caveat (2).

</details>

---

### U08-Q10 — Review this `INTENTIONALLY FLAWED` example for Argo Rollouts, Flagger, and traffic-based analys

- **Unit / topic:** Argo Rollouts, Flagger, and traffic-based analysis
- **Level:** L3
- **Question type:** configuration/manifest review
- **Objective tested:** interpret analysis and rollout states without assuming missing data is healthy
- **Estimated time:** 10 minutes

**Question / scenario**

Review this `INTENTIONALLY FLAWED` example for Argo Rollouts, Flagger, and traffic-based analysis. Identify at least three distinct defects, explain their operational impact, and propose a corrected version or exact correction.

```text
# INTENTIONALLY FLAWED analysis policy pseudocode
if metric_query returns empty:
    result = Successful
if sample_count < minimum:
    result = Successful
if error_rate > threshold:
    result = Successful
# promote after one measurement regardless of timestamp
```

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The defects are:

1. Empty metric results are treated as successful.
2. Insufficient sample count is treated as successful.
3. Threshold breach is incorrectly treated as successful and timestamps/freshness are ignored.

**Corrected direction/snippet:**

```text
# Corrected decision policy pseudocode
if query_error or data_missing or data_stale or sample_count < minimum:
    result = Inconclusive  # or Abort/Pause as explicit policy dictates
elif error_rate > threshold:
    result = Failed
else:
    result = Successful
# Evaluate over defined windows; never treat absence as a healthy measurement.
```

The correction is an instructional pattern; confirm product-specific schema and provider support before applying it.

**Reasoning**

The defects are not merely style issues: they can make resources fail to select, weaken access boundaries, make the artifact mutable, trigger unintended deletion, leak sensitive data, or convert missing evidence into an unsafe action. Corrections must be tested in a disposable environment.

**Common wrong answers**

- **Fix only syntax.** A valid manifest can still be insecure or semantically unsafe.
- **Assume an illustrative snippet is a complete deployable CRD.** Required fields and semantics depend on the installed API/version.

**Operational caveat**

The original is intentionally flawed and must not be applied. Corrected snippets may be bounded examples rather than complete production configuration; `[VERIFY]` any controller-specific fields.

**Scoring rubric**

Full credit: at least three distinct defects (3 points), impact for each (3), corrected snippet/direction (2), version/safety caveat (2).

</details>

---

### U08-Q11 — Incident: A rollout remains paused because the metric provider returns no samples. An operator 

- **Unit / topic:** Argo Rollouts, Flagger, and traffic-based analysis
- **Level:** L4
- **Question type:** incident/troubleshooting
- **Objective tested:** identify version-sensitive CRDs and traffic-provider dependencies
- **Estimated time:** 15 minutes

**Question / scenario**

Incident: A rollout remains paused because the metric provider returns no samples. An operator manually promotes it to clear the queue.

Provide symptom → diagnosis → evidence to preserve → blast-radius and rollback-safety check → containment/recovery → prevention. Identify one residual uncertainty that must not be presented as fact.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**Symptom:** A rollout remains paused because the metric provider returns no samples. An operator manually promotes it to clear the queue.

**Diagnosis:** Argo Rollouts and Flagger coordinate progressive delivery with Kubernetes resources and supported traffic/metrics integrations. Their APIs and provider capabilities are version-dependent.

**Evidence:** collect the relevant Git revision/PR, controller conditions/events, live resource state, runtime/metric samples, timestamps, and actor/approval data as applicable.

**Blast radius and rollback:** identify affected environments/replicas/consumers, determine whether state/data/external side effects changed, and test whether the prior version can safely read current state. Do not assume an image rollback reverses data.

**Containment/recovery:** use the smallest authorized reversible action; pause promotion or isolate the affected path if warranted; preserve a before/after record; reconcile the intended fix into the declared source; verify customer-facing behavior.

**Prevention:** A replica-based canary is not automatically a traffic-based canary. Validate stable/canary services, routing configuration, and the installed provider integration.

**Residual uncertainty:** any missing history, unknown consumer behavior, unparseable runtime identity, or absent metric sample remains UNKNOWN until corroborated.

**Reasoning**

The incident response separates preserving evidence from containment, makes recovery contingent on state compatibility, and verifies both control-plane convergence and application-level outcome.

**Common wrong answers**

- **Immediately force-sync/redeploy without preserving evidence.** This can erase the live state that explains the incident.
- **Assume rollback is safe because the previous artifact exists.** Data, schema, event, or external side effects may be incompatible.

**Operational caveat**

Escalate to the incident commander/security owner when compromise or regulated data is plausible. Use only approved break-glass authority and an explicit reconciliation/review path.

**Scoring rubric**

10 points: diagnosis 2; evidence 2; blast radius/rollback 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### U08-Q12 — Design safe rollout analysis and traffic verification

- **Unit / topic:** — Argo Rollouts, Flagger, and traffic-based analysis
- **Level:** — L4
- **Question type:** — design
- **Objective tested:** — design a safe, auditable workflow for argo rollouts, flagger, and traffic-based analysis
- **Estimated time:** — 20 minutes

**Question / scenario**

Design a rollout-analysis workflow that proves traffic exposure, handles missing/stale measurements, and records promotion/abort decisions.

**Deliverables expected:** a component/workflow diagram, ownership and evidence table, failure modes, rollback/recovery path, and a short decision record. State assumptions and include at least two viable alternatives.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Correlate rollout steps with stable/canary routing configuration and request counters; validate metric labels, freshness, sample count, and query health; define pass/fail/inconclusive outcomes; pause or abort on missing data according to explicit policy. Preserve AnalysisRun/notification evidence and verify the application after promotion or abort.

**Reasoning**

A controller status is only one signal. The design must prove that the measured traffic corresponds to the version and window under evaluation.

**Common wrong answers**

- **Treat a completed rollout step as proof of traffic exposure** — Routing and actual request counters must corroborate the intended split.
- **Treat missing analysis as a pass** — Absent samples cannot establish health; use the configured inconclusive/fail-safe path.

**Operational caveat**

Verify CRD schemas, provider integrations, and analysis semantics against the installed versions.

**Scoring rubric**

10 points: safety/correctness 2; evidence and verification 2; alternatives and trade-offs 2; failure/recovery plan 2; ownership, clarity, and unresolved uncertainty 2.

</details>

---

# Unit 9 — Release health analysis and automated abort (12 questions)

### U09-Q01 — Explain the core model for SLIs, golden signals, PromQL, sample quality, pause/abort decisions.

- **Unit / topic:** Release health analysis and automated abort
- **Level:** L1
- **Question type:** conceptual
- **Objective tested:** evaluate rollout health using infrastructure and business SLIs
- **Estimated time:** 6 minutes

**Question / scenario**

Explain the core model for SLIs, golden signals, PromQL, sample quality, pause/abort decisions. In your answer, distinguish the desired configuration, the controller or process that acts on it, and the evidence that shows whether the intended outcome actually occurred.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

A health gate should specify metric semantics, labels, units, time window, baseline, minimum sample count, and missing-data behavior. Empty data is not equivalent to zero errors.

**Reasoning**

A health gate must validate the measurement before evaluating its value. Empty, stale, gappy, mislabelled, or low-volume telemetry is inconclusive unless an explicit, tested policy says otherwise.

**Common wrong answers**

- **Convert an empty metric series to zero failures** No observations mean the error rate is unknown, not healthy.
- **Use a threshold without checking labels, units, or sample count** A wrong query can produce a false green even when the threshold is reasonable.

**Operational caveat**

PromQL expressions, labels, scrape delay, and alert windows depend on the telemetry stack. Test empty/stale/missing-series behavior before automating decisions.

**Scoring rubric**

Full credit (3 points): states the core mechanism accurately (1), distinguishes what the evidence does and does not prove (1), and identifies a safe next check or operational implication (1).

</details>

---

### U09-Q02 — Classify empty canary metrics safely

- **Unit / topic:** — Release health analysis and automated abort
- **Level:** — L2
- **Question type:** — conceptual
- **Objective tested:** — predict and verify classify empty canary metrics safely
- **Estimated time:** — 7 minutes

**Question / scenario**

A release-health query returns an empty error-rate series for the canary, while stable has 120 requests and the canary has zero. What is the correct decision and why?

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The canary result is inconclusive because there are no canary samples; an empty series cannot prove a zero error rate. Hold or abort promotion according to the defined safety policy, check query labels and traffic routing, and gather sufficient observations before evaluating a threshold.

**Reasoning**

An analysis result is meaningful only when data quality, sample count, units, freshness, and window are valid.

**Common wrong answers**

- **Convert an empty metric series to zero failures** — No observations mean the error rate is unknown, not healthy.
- **Use a threshold without checking labels, units, or sample count** — A wrong query can produce a false green even when the threshold is reasonable.

**Operational caveat**

PromQL behavior depends on query shape and labels. Validate the expression against actual time series and test missing-data handling.

**Scoring rubric**

Full credit (3 points): states the correct operational conclusion (1), cites the evidence/policy that supports it (1), and names a safe next check plus a remaining uncertainty (1).

</details>

---

### U09-Q03 — Design a fail-closed release-health gate

- **Unit / topic:** — Release health analysis and automated abort
- **Level:** — L3
- **Question type:** — conceptual
- **Objective tested:** — diagnose and recover safely from design a fail-closed release-health gate
- **Estimated time:** — 8 minutes

**Question / scenario**

Design a release-health gate when telemetry may be stale or missing and a false green is more dangerous than a delayed release.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Define explicit pass/fail/inconclusive states, freshness and minimum-sample thresholds, a bounded observation window, error-rate/latency/business SLI guardrails, and operator escalation. Missing data or query errors should block promotion or trigger a safe pause/abort; record the query, labels, units, window, sample count, and decision reason.

**Reasoning**

Health gates must reason about measurement validity as well as measured values. A missing metric is a loss of evidence, not a positive signal.

**Common wrong answers**

- **Convert an empty metric series to zero failures** — No observations mean the error rate is unknown, not healthy.
- **Use a threshold without checking labels, units, or sample count** — A wrong query can produce a false green even when the threshold is reasonable.

**Operational caveat**

Thresholds are service-specific and illustrative. Validate metric semantics, alert delays, and rollback safety with production-like tests.

**Scoring rubric**

Full credit (4 points): identifies the relevant state/evidence (1), orders diagnosis before mutation (1), checks blast radius and rollback/data compatibility (1), and defines verification/prevention (1).

</details>

---

### U09-Q04 — A query succeeds but returns no series because the service label changed. What should the gate 

- **Unit / topic:** Release health analysis and automated abort
- **Level:** L1
- **Question type:** MCQ
- **Objective tested:** evaluate rollout health using infrastructure and business SLIs
- **Estimated time:** 3 minutes

**Question / scenario**

A query succeeds but returns no series because the service label changed. What should the gate do?

A. Pass as zero errors
B. Mark the release healthy because query transport succeeded
C. Report UNKNOWN/INCONCLUSIVE or abort per policy and repair the query/coverage
D. Disable all metrics

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**C**. Report UNKNOWN/INCONCLUSIVE or abort per policy and repair the query/coverage

**Reasoning**

- **A. Incorrect.** The option proposes “Pass as zero errors”; missing or empty telemetry is not evidence of zero failures; the operator must validate freshness, labels, coverage, and minimum samples and keep the result UNKNOWN/INCONCLUSIVE until then.
- **B. Incorrect.** The option proposes “Mark the release healthy because query transport succeeded”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.
- **C. Correct.** Query execution success is not data completeness; an empty vector can be a label or telemetry failure.
- **D. Incorrect.** The option proposes “Disable all metrics”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses convert an empty metric series to zero failures with verified state, or skips the required safety check: No observations mean the error rate is unknown, not healthy.

**Operational caveat**

PromQL expressions, labels, scrape delay, and alert windows depend on the telemetry stack. Test empty/stale/missing-series behavior before automating decisions.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U09-Q05 — A canary breaches the business failure threshold with sufficient samples while CPU remains low.

- **Unit / topic:** Release health analysis and automated abort
- **Level:** L2
- **Question type:** MCQ
- **Objective tested:** classify analysis as pass, fail, or inconclusive with missing/stale/low-volume data
- **Estimated time:** 3 minutes

**Question / scenario**

A canary breaches the business failure threshold with sufficient samples while CPU remains low. What is the best decision?

A. Promote because CPU is healthy
B. Follow the predeclared business SLI gate and pause/abort as designed
C. Change the threshold after seeing the result
D. Ignore canary metrics until 100% rollout

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**B**. Follow the predeclared business SLI gate and pause/abort as designed

**Reasoning**

- **A. Incorrect.** The option proposes “Promote because CPU is healthy”; CPU alone does not establish customer-facing correctness; the stated business SLI and sample quality must be evaluated too.
- **B. Correct.** Use the metric tied to customer outcome and avoid post-hoc threshold changes.
- **C. Incorrect.** The option proposes “Change the threshold after seeing the result”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.
- **D. Incorrect.** The option proposes “Ignore canary metrics until 100% rollout”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses convert an empty metric series to zero failures with verified state, or skips the required safety check: No observations mean the error rate is unknown, not healthy.

**Operational caveat**

PromQL expressions, labels, scrape delay, and alert windows depend on the telemetry stack. Test empty/stale/missing-series behavior before automating decisions.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U09-Q06 — Why specify a minimum sample count?

- **Unit / topic:** Release health analysis and automated abort
- **Level:** L3
- **Question type:** MCQ
- **Objective tested:** design thresholds and windows that limit false positives and false negatives
- **Estimated time:** 3 minutes

**Question / scenario**

Why specify a minimum sample count?

A. To make a metric dashboard look complex
B. To avoid decisions from statistically weak or low-volume observations
C. To guarantee the metric has no bias
D. To replace time windows

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**B**. To avoid decisions from statistically weak or low-volume observations

**Reasoning**

- **A. Incorrect.** The option proposes “To make a metric dashboard look complex”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.
- **B. Correct.** Minimum counts reduce uncertainty but do not by themselves guarantee statistical validity.
- **C. Incorrect.** The option proposes “To guarantee the metric has no bias”; it makes a universal guarantee that the evidence does not support; controller and provider behavior depends on explicit policy, version, and observed state.
- **D. Incorrect.** The option proposes “To replace time windows”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses convert an empty metric series to zero failures with verified state, or skips the required safety check: No observations mean the error rate is unknown, not healthy.

**Operational caveat**

PromQL expressions, labels, scrape delay, and alert windows depend on the telemetry stack. Test empty/stale/missing-series behavior before automating decisions.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U09-Q07 — Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Release health analysis an

- **Unit / topic:** Release health analysis and automated abort
- **Level:** L2
- **Question type:** output interpretation
- **Objective tested:** evaluate rollout health using infrastructure and business SLIs
- **Estimated time:** 7 minutes

**Question / scenario**

Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Release health analysis and automated abort:

```text
SIMULATED / REPRESENTATIVE
Query window: 5m
Metric: http_requests_total{service="orders-api", status="500"}
Expected traffic: ~2,000 requests
Returned series: empty
Query status: success
Correct classification: UNKNOWN/INCONCLUSIVE until query and coverage are validated
```

State what is established, what remains unknown, the safest next diagnostic step, and whether you would promote, reconcile, pause, abort, or gather more evidence. Justify the decision using specific fields/lines above.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The query completed but returned an empty series despite expected traffic around 2,000 requests. That is not evidence of zero 500s; it may indicate wrong labels, absent instrumentation, scrape gaps, or query semantics. Mark the analysis UNKNOWN/INCONCLUSIVE, validate raw metric labels and denominator, and only rerun once data coverage is demonstrated.

**Reasoning**

Output interpretation must separate observations from inference. A status or event can be stale, partial, or scoped to a single resource; the next check should target the earliest missing/failed link and preserve the current evidence.

**Common wrong answers**

- **Assume the best because one field is green.** That ignores contradictory fields and coverage gaps.
- **Mutate immediately.** Diagnose source, identity, scope, and rollback safety first unless containment urgency requires a minimal authorized action.

**Operational caveat**

All output is simulated; it is not claimed to come from a live cluster. Exact CLI output and controller status wording are `[VERIFY]` for the installed version.

**Scoring rubric**

Full credit: cite two specific fields, identify one unknown, choose a safe next action, and explain promotion/rollback constraints (4 points).

</details>

---

### U09-Q08 — Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Release health analysis an

- **Unit / topic:** Release health analysis and automated abort
- **Level:** L3
- **Question type:** output interpretation
- **Objective tested:** classify analysis as pass, fail, or inconclusive with missing/stale/low-volume data
- **Estimated time:** 8 minutes

**Question / scenario**

Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Release health analysis and automated abort:

```text
SIMULATED / REPRESENTATIVE
Baseline checkout failure rate: 0.4% (10m, 8,200 requests)
Canary checkout failure rate: 2.7% (10m, 740 requests)
Canary p95 latency: 520 ms; baseline p95: 210 ms
CPU: 38%
Configured abort threshold: failure rate > 1% with >= 200 requests
```

State what is established, what remains unknown, the safest next diagnostic step, and whether you would promote, reconcile, pause, abort, or gather more evidence. Justify the decision using specific fields/lines above.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Canary checkout failure rate is 2.7%, above the 1% threshold, with 740 requests exceeding the 200-request minimum; p95 latency is also materially worse than baseline. CPU at 38% does not negate the business SLI breach. Pause/abort per policy, verify the query and timestamps, and assess rollback safety against data/schema changes.

**Reasoning**

Output interpretation must separate observations from inference. A status or event can be stale, partial, or scoped to a single resource; the next check should target the earliest missing/failed link and preserve the current evidence.

**Common wrong answers**

- **Assume the best because one field is green.** That ignores contradictory fields and coverage gaps.
- **Mutate immediately.** Diagnose source, identity, scope, and rollback safety first unless containment urgency requires a minimal authorized action.

**Operational caveat**

All output is simulated; it is not claimed to come from a live cluster. Exact CLI output and controller status wording are `[VERIFY]` for the installed version.

**Scoring rubric**

Full credit: cite two specific fields, identify one unknown, choose a safe next action, and explain promotion/rollback constraints (4 points).

</details>

---

### U09-Q09 — Review this `INTENTIONALLY FLAWED` example for Release health analysis and automated abort. Ide

- **Unit / topic:** Release health analysis and automated abort
- **Level:** L3
- **Question type:** configuration/manifest review
- **Objective tested:** evaluate rollout health using infrastructure and business SLIs
- **Estimated time:** 10 minutes

**Question / scenario**

Review this `INTENTIONALLY FLAWED` example for Release health analysis and automated abort. Identify at least three distinct defects, explain their operational impact, and propose a corrected version or exact correction.

```yaml
# INTENTIONALLY FLAWED pseudo-policy; not PromQL or a controller CRD
metric: http_errors
window: 5
threshold: 0.01
empty_result: 0
minimum_samples: 0
action: promote
```

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The defects are:

1. The window `5` has no unit and is not a complete query window.
2. The metric is not defined with service/route labels or a denominator, so the population and ratio are unclear.
3. An empty result maps to zero and the sample minimum is zero, so missing data can pass.

**Corrected direction/snippet:**

```yaml
# Explicit analysis contract (translate to installed metrics/controller syntax)
metric: orders_checkout_failure_ratio
window: 10m
threshold: 0.01
minimum_samples: 200
require_fresh_samples: true
empty_or_query_error: inconclusive_or_abort
action_on_breach: pause_or_abort_per_release_policy
# Specify units, labels, baseline comparison and query owner.
```

The correction is an instructional pattern; confirm product-specific schema and provider support before applying it.

**Reasoning**

The defects are not merely style issues: they can make resources fail to select, weaken access boundaries, make the artifact mutable, trigger unintended deletion, leak sensitive data, or convert missing evidence into an unsafe action. Corrections must be tested in a disposable environment.

**Common wrong answers**

- **Fix only syntax.** A valid manifest can still be insecure or semantically unsafe.
- **Assume an illustrative snippet is a complete deployable CRD.** Required fields and semantics depend on the installed API/version.

**Operational caveat**

The original is intentionally flawed and must not be applied. Corrected snippets may be bounded examples rather than complete production configuration; `[VERIFY]` any controller-specific fields.

**Scoring rubric**

Full credit: at least three distinct defects (3 points), impact for each (3), corrected snippet/direction (2), version/safety caveat (2).

</details>

---

### U09-Q10 — Review this `INTENTIONALLY FLAWED` example for Release health analysis and automated abort. Ide

- **Unit / topic:** Release health analysis and automated abort
- **Level:** L3
- **Question type:** configuration/manifest review
- **Objective tested:** classify analysis as pass, fail, or inconclusive with missing/stale/low-volume data
- **Estimated time:** 10 minutes

**Question / scenario**

Review this `INTENTIONALLY FLAWED` example for Release health analysis and automated abort. Identify at least three distinct defects, explain their operational impact, and propose a corrected version or exact correction.

```promql
# INTENTIONALLY FLAWED PromQL-like snippet
sum(rate(http_requests_total{status="500"}[5]))
# compares all services and traffic to a hard-coded 0.01 without request denominator
```

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The defects are:

1. The range selector `[5]` is missing an explicit duration unit such as `5m`.
2. The query aggregates all services rather than scoping to `orders-api`.
3. The expression returns an error count rate, not an error ratio; it lacks a request-rate denominator and sample gate.

**Corrected direction/snippet:**

```promql
# Illustrative PromQL pattern; verify metric labels and scrape interval in the actual system
sum(rate(http_requests_total{service="orders-api",status="500"}[5m]))
/
sum(rate(http_requests_total{service="orders-api"}[5m]))
# Define a minimum traffic/sample gate separately; validate units and labels before promotion.
```

The correction is an instructional pattern; confirm product-specific schema and provider support before applying it.

**Reasoning**

The defects are not merely style issues: they can make resources fail to select, weaken access boundaries, make the artifact mutable, trigger unintended deletion, leak sensitive data, or convert missing evidence into an unsafe action. Corrections must be tested in a disposable environment.

**Common wrong answers**

- **Fix only syntax.** A valid manifest can still be insecure or semantically unsafe.
- **Assume an illustrative snippet is a complete deployable CRD.** Required fields and semantics depend on the installed API/version.

**Operational caveat**

The original is intentionally flawed and must not be applied. Corrected snippets may be bounded examples rather than complete production configuration; `[VERIFY]` any controller-specific fields.

**Scoring rubric**

Full credit: at least three distinct defects (3 points), impact for each (3), corrected snippet/direction (2), version/safety caveat (2).

</details>

---

### U09-Q11 — Incident: The analysis query uses a label that no longer exists and returns an empty vector; th

- **Unit / topic:** Release health analysis and automated abort
- **Level:** L4
- **Question type:** incident/troubleshooting
- **Objective tested:** design thresholds and windows that limit false positives and false negatives
- **Estimated time:** 15 minutes

**Question / scenario**

Incident: The analysis query uses a label that no longer exists and returns an empty vector; the pipeline interprets empty as zero errors.

Provide symptom → diagnosis → evidence to preserve → blast-radius and rollback-safety check → containment/recovery → prevention. Identify one residual uncertainty that must not be presented as fact.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**Symptom:** The analysis query uses a label that no longer exists and returns an empty vector; the pipeline interprets empty as zero errors.

**Diagnosis:** A health gate should specify metric semantics, labels, units, time window, baseline, minimum sample count, and missing-data behavior. Empty data is not equivalent to zero errors.

**Evidence:** collect the relevant Git revision/PR, controller conditions/events, live resource state, runtime/metric samples, timestamps, and actor/approval data as applicable.

**Blast radius and rollback:** identify affected environments/replicas/consumers, determine whether state/data/external side effects changed, and test whether the prior version can safely read current state. Do not assume an image rollback reverses data.

**Containment/recovery:** use the smallest authorized reversible action; pause promotion or isolate the affected path if warranted; preserve a before/after record; reconcile the intended fix into the declared source; verify customer-facing behavior.

**Prevention:** Automated abort should have explicit guardrails, a bounded observation window, human override rules, and a rollback-safety check for stateful changes.

**Residual uncertainty:** any missing history, unknown consumer behavior, unparseable runtime identity, or absent metric sample remains UNKNOWN until corroborated.

**Reasoning**

The incident response separates preserving evidence from containment, makes recovery contingent on state compatibility, and verifies both control-plane convergence and application-level outcome.

**Common wrong answers**

- **Immediately force-sync/redeploy without preserving evidence.** This can erase the live state that explains the incident.
- **Assume rollback is safe because the previous artifact exists.** Data, schema, event, or external side effects may be incompatible.

**Operational caveat**

Escalate to the incident commander/security owner when compromise or regulated data is plausible. Use only approved break-glass authority and an explicit reconciliation/review path.

**Scoring rubric**

10 points: diagnosis 2; evidence 2; blast radius/rollback 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### U09-Q12 — Design release-health policy for missing telemetry

- **Unit / topic:** — Release health analysis and automated abort
- **Level:** — L4
- **Question type:** — design
- **Objective tested:** — design a safe, auditable workflow for release health analysis and automated abort
- **Estimated time:** — 20 minutes

**Question / scenario**

Design a release-health gate when telemetry may be stale or missing and a false green is more dangerous than a delayed release.

**Deliverables expected:** a component/workflow diagram, ownership and evidence table, failure modes, rollback/recovery path, and a short decision record. State assumptions and include at least two viable alternatives.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Define explicit pass/fail/inconclusive states, freshness and minimum-sample thresholds, a bounded observation window, error-rate/latency/business SLI guardrails, and operator escalation. Missing data or query errors should block promotion or trigger a safe pause/abort; record the query, labels, units, window, sample count, and decision reason.

**Reasoning**

Health gates must reason about measurement validity as well as measured values. A missing metric is a loss of evidence, not a positive signal.

**Common wrong answers**

- **Convert an empty metric series to zero failures** — No observations mean the error rate is unknown, not healthy.
- **Use a threshold without checking labels, units, or sample count** — A wrong query can produce a false green even when the threshold is reasonable.

**Operational caveat**

Thresholds are service-specific and illustrative. Validate metric semantics, alert delays, and rollback safety with production-like tests.

**Scoring rubric**

10 points: safety/correctness 2; evidence and verification 2; alternatives and trade-offs 2; failure/recovery plan 2; ownership, clarity, and unresolved uncertainty 2.

</details>

---

# Unit 10 — Feature flags and dark launches (12 questions)

### U10-Q01 — Explain the core model for deploy versus release, targeting, kill switches, ownership, expiry. 

- **Unit / topic:** Feature flags and dark launches
- **Level:** L1
- **Question type:** conceptual
- **Objective tested:** separate deployment state from feature exposure
- **Estimated time:** 6 minutes

**Question / scenario**

Explain the core model for deploy versus release, targeting, kill switches, ownership, expiry. In your answer, distinguish the desired configuration, the controller or process that acts on it, and the evidence that shows whether the intended outcome actually occurred.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Deployment ships code; a feature flag controls exposure. A dark launch can execute a path without exposing its result to users, but it still consumes resources and may touch state.

**Reasoning**

A feature flag controls exposure, not the compatibility of deployed code, schemas, external side effects, or flag-service failure behavior. Design ownership, safe defaults, telemetry, expiry, and recovery as part of the release.

**Common wrong answers**

- **Assume disabling a flag restores the old system** A flag does not undo schema changes or external side effects.
- **Leave flags without owner or expiry** Unowned flags create ambiguous behavior and permanent test-state complexity.

**Operational caveat**

Flag SDK defaults, targeting, and outage behavior are provider-specific. Verify safe defaults and privacy controls for the installed implementation.

**Scoring rubric**

Full credit (3 points): states the core mechanism accurately (1), distinguishes what the evidence does and does not prove (1), and identifies a safe next check or operational implication (1).

</details>

---

### U10-Q02 — Assess flag-off versus schema compatibility

- **Unit / topic:** — Feature flags and dark launches
- **Level:** — L2
- **Question type:** — conceptual
- **Objective tested:** — predict and verify assess flag-off versus schema compatibility
- **Estimated time:** — 7 minutes

**Question / scenario**

A feature flag is off, but the new deployment requires a database column that the old application version does not know about. Is rollback safe?

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Not necessarily. A flag controls exposure of a code path; it does not restore schema compatibility or undo writes made by the new version. Check expand–migrate–contract sequencing, whether old code can tolerate the new schema/data, flag default behavior, and external side effects before rolling back.

**Reasoning**

Deployment state, feature exposure, and data/schema state are separate. Turning a feature off cannot repair an incompatible binary or migration.

**Common wrong answers**

- **Assume disabling a flag restores the old system** — A flag does not undo schema changes or external side effects.
- **Leave flags without owner or expiry** — Unowned flags create ambiguous behavior and permanent test-state complexity.

**Operational caveat**

Flag-provider outage defaults and SDK behavior are implementation-specific. Verify fail-open/fail-closed behavior and test the fallback path.

**Scoring rubric**

Full credit (3 points): states the correct operational conclusion (1), cites the evidence/policy that supports it (1), and names a safe next check plus a remaining uncertainty (1).

</details>

---

### U10-Q03 — Handle a flag-service outage during release

- **Unit / topic:** — Feature flags and dark launches
- **Level:** — L3
- **Question type:** — conceptual
- **Objective tested:** — diagnose and recover safely from handle a flag-service outage during release
- **Estimated time:** — 8 minutes

**Question / scenario**

A feature-flag service becomes unavailable during a progressive rollout. What should the operator verify before changing exposure or rolling back?

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Check the SDK's configured fallback/default behavior, cache/last-known state, targeting rules, and telemetry showing which code path users actually receive. Avoid assuming the flag is off. Pause exposure if safe, inspect application errors and compatibility, and use the documented provider-specific recovery path; record the decision and verify behavior after service recovery.

**Reasoning**

Flag-service availability affects exposure only according to the SDK and application fallback design. The deployed binary and data state still need independent compatibility checks.

**Common wrong answers**

- **Assume disabling a flag restores the old system** — A flag does not undo schema changes or external side effects.
- **Leave flags without owner or expiry** — Unowned flags create ambiguous behavior and permanent test-state complexity.

**Operational caveat**

Flag-provider outage semantics vary by SDK/version and configuration. Verify fallback behavior in tests before production.

**Scoring rubric**

Full credit (4 points): identifies the relevant state/evidence (1), orders diagnosis before mutation (1), checks blast radius and rollback/data compatibility (1), and defines verification/prevention (1).

</details>

---

### U10-Q04 — What does disabling a feature flag guarantee?

- **Unit / topic:** Feature flags and dark launches
- **Level:** L1
- **Question type:** MCQ
- **Objective tested:** separate deployment state from feature exposure
- **Estimated time:** 3 minutes

**Question / scenario**

What does disabling a feature flag guarantee?

A. It rolls back the deployed binary and all data writes
B. It stops the feature path from being exposed only to the extent the application/provider semantics implement that flag; it does not reverse schema changes
C. It makes a deployment digest immutable
D. It restores all old database state

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**B**. It stops the feature path from being exposed only to the extent the application/provider semantics implement that flag; it does not reverse schema changes

**Reasoning**

- **A. Incorrect.** The option proposes “It rolls back the deployed binary and all data writes”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.
- **B. Correct.** Flags control behavior/exposure, not deployment rollback or data reversibility.
- **C. Incorrect.** The option proposes “It makes a deployment digest immutable”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.
- **D. Incorrect.** The option proposes “It restores all old database state”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses assume disabling a flag restores the old system with verified state, or skips the required safety check: A flag does not undo schema changes or external side effects.

**Operational caveat**

Flag SDK defaults, targeting, and outage behavior are provider-specific. Verify safe defaults and privacy controls for the installed implementation.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U10-Q05 — Which flag should be removed first in governance cleanup?

- **Unit / topic:** Feature flags and dark launches
- **Level:** L2
- **Question type:** MCQ
- **Objective tested:** design a flag lifecycle with owner, expiry, telemetry, and safe defaults
- **Estimated time:** 3 minutes

**Question / scenario**

Which flag should be removed first in governance cleanup?

A. Any flag with no owner and no expiry after assessing dependencies and behavior
B. Every kill switch regardless of risk
C. Only flags that have never been evaluated
D. Flags that are part of security controls without review

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**A**. Any flag with no owner and no expiry after assessing dependencies and behavior

**Reasoning**

- **A. Correct.** Unowned/expired flags should be inventoried and safely removed; security-critical kill switches need deliberate ownership.
- **B. Incorrect.** The option proposes “Every kill switch regardless of risk”; it makes a universal guarantee that the evidence does not support; controller and provider behavior depends on explicit policy, version, and observed state.
- **C. Incorrect.** The option proposes “Only flags that have never been evaluated”; it makes a universal guarantee that the evidence does not support; controller and provider behavior depends on explicit policy, version, and observed state.
- **D. Incorrect.** The option proposes “Flags that are part of security controls without review”; it proposes an unsafe shortcut without first establishing authorization, impact, evidence preservation, and a recovery path.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses assume disabling a flag restores the old system with verified state, or skips the required safety check: A flag does not undo schema changes or external side effects.

**Operational caveat**

Flag SDK defaults, targeting, and outage behavior are provider-specific. Verify safe defaults and privacy controls for the installed implementation.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U10-Q06 — Why avoid sensitive user attributes in flag targeting?

- **Unit / topic:** Feature flags and dark launches
- **Level:** L3
- **Question type:** MCQ
- **Objective tested:** reason about flag-service failure and compatibility limits
- **Estimated time:** 3 minutes

**Question / scenario**

Why avoid sensitive user attributes in flag targeting?

A. They always cause a syntax error
B. They increase privacy exposure and can leak into logs, analytics, or provider systems
C. They prevent gradual rollout
D. They make flags expire automatically

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**B**. They increase privacy exposure and can leak into logs, analytics, or provider systems

**Reasoning**

- **A. Incorrect.** The option proposes “They always cause a syntax error”; it makes a universal guarantee that the evidence does not support; controller and provider behavior depends on explicit policy, version, and observed state.
- **B. Correct.** Use minimized, approved attributes and restrict access/retention.
- **C. Incorrect.** The option proposes “They prevent gradual rollout”; structural shape alone cannot establish semantic compatibility across real producers and consumers.
- **D. Incorrect.** The option proposes “They make flags expire automatically”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses assume disabling a flag restores the old system with verified state, or skips the required safety check: A flag does not undo schema changes or external side effects.

**Operational caveat**

Flag SDK defaults, targeting, and outage behavior are provider-specific. Verify safe defaults and privacy controls for the installed implementation.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U10-Q07 — Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Feature flags and dark lau

- **Unit / topic:** Feature flags and dark launches
- **Level:** L2
- **Question type:** output interpretation
- **Objective tested:** separate deployment state from feature exposure
- **Estimated time:** 7 minutes

**Question / scenario**

Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Feature flags and dark launches:

```text
SIMULATED / REPRESENTATIVE
Flag: new-checkout-flow
Enabled for production: false
Flag owner: none
Expiry: none
New deployment startup: requires column checkout_mode
Database migration: not yet applied
Conclusion: flag-off does not establish deployment compatibility.
```

State what is established, what remains unknown, the safest next diagnostic step, and whether you would promote, reconcile, pause, abort, or gather more evidence. Justify the decision using specific fields/lines above.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The flag is off, but the new binary requires `checkout_mode` before the migration exists. That is a deployment/schema compatibility defect independent of user exposure. Stop promotion, make startup/read behavior compatible or apply a staged migration safely, and only then decide whether to expose the feature. Assign an owner and expiry before launch.

**Reasoning**

Output interpretation must separate observations from inference. A status or event can be stale, partial, or scoped to a single resource; the next check should target the earliest missing/failed link and preserve the current evidence.

**Common wrong answers**

- **Assume the best because one field is green.** That ignores contradictory fields and coverage gaps.
- **Mutate immediately.** Diagnose source, identity, scope, and rollback safety first unless containment urgency requires a minimal authorized action.

**Operational caveat**

All output is simulated; it is not claimed to come from a live cluster. Exact CLI output and controller status wording are `[VERIFY]` for the installed version.

**Scoring rubric**

Full credit: cite two specific fields, identify one unknown, choose a safe next action, and explain promotion/rollback constraints (4 points).

</details>

---

### U10-Q08 — Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Feature flags and dark lau

- **Unit / topic:** Feature flags and dark launches
- **Level:** L3
- **Question type:** output interpretation
- **Objective tested:** design a flag lifecycle with owner, expiry, telemetry, and safe defaults
- **Estimated time:** 8 minutes

**Question / scenario**

Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Feature flags and dark launches:

```text
SIMULATED / REPRESENTATIVE
Flag provider timeout: 30s
Configured default: enabled
Targeting rule includes email address
Flag evaluation error rate: 18%
Customer reports: inconsistent checkout behavior across replicas
```

State what is established, what remains unknown, the safest next diagnostic step, and whether you would promote, reconcile, pause, abort, or gather more evidence. Justify the decision using specific fields/lines above.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The provider times out, the configured default is enabled, evaluation errors reach 18%, and targeting uses email. This risks inconsistent exposure and unnecessary personal-data handling. Apply the documented safe default/kill behavior, pause rollout if needed, inspect SDK/provider semantics, minimize targeting attributes, and verify business outcomes across replicas.

**Reasoning**

Output interpretation must separate observations from inference. A status or event can be stale, partial, or scoped to a single resource; the next check should target the earliest missing/failed link and preserve the current evidence.

**Common wrong answers**

- **Assume the best because one field is green.** That ignores contradictory fields and coverage gaps.
- **Mutate immediately.** Diagnose source, identity, scope, and rollback safety first unless containment urgency requires a minimal authorized action.

**Operational caveat**

All output is simulated; it is not claimed to come from a live cluster. Exact CLI output and controller status wording are `[VERIFY]` for the installed version.

**Scoring rubric**

Full credit: cite two specific fields, identify one unknown, choose a safe next action, and explain promotion/rollback constraints (4 points).

</details>

---

### U10-Q09 — Review this `INTENTIONALLY FLAWED` example for Feature flags and dark launches. Identify at lea

- **Unit / topic:** Feature flags and dark launches
- **Level:** L3
- **Question type:** configuration/manifest review
- **Objective tested:** separate deployment state from feature exposure
- **Estimated time:** 10 minutes

**Question / scenario**

Review this `INTENTIONALLY FLAWED` example for Feature flags and dark launches. Identify at least three distinct defects, explain their operational impact, and propose a corrected version or exact correction.

```yaml
flags:
  new-checkout-flow:
    enabled: true
    targeting: {email: "customer@example.invalid"}
    owner: ""
    expires: never
    default_on_error: true
```

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The defects are:

1. Targeting uses a personal email attribute without a stated privacy/minimization justification.
2. The flag has no owner.
3. The flag never expires and provider errors default to enabled, which may be unsafe.

**Corrected direction/snippet:**

```yaml
flags:
  new-checkout-flow:
    enabled: false # choose a safe default consistent with product and compatibility policy
    targeting: {cohort: "internal-test"} # use approved, minimized attributes
    owner: payments-platform
    expires: "2026-11-30"
    default_on_error: false
    telemetry: flag_evaluation_errors, exposure, business_outcome
# Validate exact provider schema and privacy rules for the selected flag platform.
```

The correction is an instructional pattern; confirm product-specific schema and provider support before applying it.

**Reasoning**

The defects are not merely style issues: they can make resources fail to select, weaken access boundaries, make the artifact mutable, trigger unintended deletion, leak sensitive data, or convert missing evidence into an unsafe action. Corrections must be tested in a disposable environment.

**Common wrong answers**

- **Fix only syntax.** A valid manifest can still be insecure or semantically unsafe.
- **Assume an illustrative snippet is a complete deployable CRD.** Required fields and semantics depend on the installed API/version.

**Operational caveat**

The original is intentionally flawed and must not be applied. Corrected snippets may be bounded examples rather than complete production configuration; `[VERIFY]` any controller-specific fields.

**Scoring rubric**

Full credit: at least three distinct defects (3 points), impact for each (3), corrected snippet/direction (2), version/safety caveat (2).

</details>

---

### U10-Q10 — Review this `INTENTIONALLY FLAWED` example for Feature flags and dark launches. Identify at lea

- **Unit / topic:** Feature flags and dark launches
- **Level:** L3
- **Question type:** configuration/manifest review
- **Objective tested:** design a flag lifecycle with owner, expiry, telemetry, and safe defaults
- **Estimated time:** 10 minutes

**Question / scenario**

Review this `INTENTIONALLY FLAWED` example for Feature flags and dark launches. Identify at least three distinct defects, explain their operational impact, and propose a corrected version or exact correction.

```text
# release checklist
- deploy new binary
- enable flag for all users
- if error rate rises, disable flag and assume rollback is complete
- keep flag permanently for future reuse
```

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The defects are:

1. The rollout exposes to all users before staged observation.
2. It assumes disabling a flag completes binary/data rollback.
3. It keeps the flag permanently without owner, expiry, telemetry, or removal criteria.

**Corrected direction/snippet:**

```text
# release checklist
- deploy code that remains compatible with current schema when flag is off
- verify default and provider-outage behavior
- expose to a small cohort with business telemetry
- disable exposure if needed, then separately evaluate binary/schema rollback safety
- assign owner, expiry, and removal PR; delete stale flag after safe convergence
```

The correction is an instructional pattern; confirm product-specific schema and provider support before applying it.

**Reasoning**

The defects are not merely style issues: they can make resources fail to select, weaken access boundaries, make the artifact mutable, trigger unintended deletion, leak sensitive data, or convert missing evidence into an unsafe action. Corrections must be tested in a disposable environment.

**Common wrong answers**

- **Fix only syntax.** A valid manifest can still be insecure or semantically unsafe.
- **Assume an illustrative snippet is a complete deployable CRD.** Required fields and semantics depend on the installed API/version.

**Operational caveat**

The original is intentionally flawed and must not be applied. Corrected snippets may be bounded examples rather than complete production configuration; `[VERIFY]` any controller-specific fields.

**Scoring rubric**

Full credit: at least three distinct defects (3 points), impact for each (3), corrected snippet/direction (2), version/safety caveat (2).

</details>

---

### U10-Q11 — Incident: The feature flag is disabled, but the new binary requires a newly added database colu

- **Unit / topic:** Feature flags and dark launches
- **Level:** L4
- **Question type:** incident/troubleshooting
- **Objective tested:** reason about flag-service failure and compatibility limits
- **Estimated time:** 15 minutes

**Question / scenario**

Incident: The feature flag is disabled, but the new binary requires a newly added database column at startup. Rolling back the binary now fails.

Provide symptom → diagnosis → evidence to preserve → blast-radius and rollback-safety check → containment/recovery → prevention. Identify one residual uncertainty that must not be presented as fact.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**Symptom:** The feature flag is disabled, but the new binary requires a newly added database column at startup. Rolling back the binary now fails.

**Diagnosis:** Deployment ships code; a feature flag controls exposure. A dark launch can execute a path without exposing its result to users, but it still consumes resources and may touch state.

**Evidence:** collect the relevant Git revision/PR, controller conditions/events, live resource state, runtime/metric samples, timestamps, and actor/approval data as applicable.

**Blast radius and rollback:** identify affected environments/replicas/consumers, determine whether state/data/external side effects changed, and test whether the prior version can safely read current state. Do not assume an image rollback reverses data.

**Containment/recovery:** use the smallest authorized reversible action; pause promotion or isolate the affected path if warranted; preserve a before/after record; reconcile the intended fix into the declared source; verify customer-facing behavior.

**Prevention:** Disabling a flag does not make an incompatible deployment or database schema backward-compatible. Flag-service outage behavior must be designed and tested.

**Residual uncertainty:** any missing history, unknown consumer behavior, unparseable runtime identity, or absent metric sample remains UNKNOWN until corroborated.

**Reasoning**

The incident response separates preserving evidence from containment, makes recovery contingent on state compatibility, and verifies both control-plane convergence and application-level outcome.

**Common wrong answers**

- **Immediately force-sync/redeploy without preserving evidence.** This can erase the live state that explains the incident.
- **Assume rollback is safe because the previous artifact exists.** Data, schema, event, or external side effects may be incompatible.

**Operational caveat**

Escalate to the incident commander/security owner when compromise or regulated data is plausible. Use only approved break-glass authority and an explicit reconciliation/review path.

**Scoring rubric**

10 points: diagnosis 2; evidence 2; blast radius/rollback 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### U10-Q12 — Design a governed feature-flag lifecycle

- **Unit / topic:** — Feature flags and dark launches
- **Level:** — L4
- **Question type:** — design
- **Objective tested:** — design a safe, auditable workflow for feature flags and dark launches
- **Estimated time:** — 20 minutes

**Question / scenario**

Design a governed feature-flag lifecycle covering ownership, targeting, safe defaults, telemetry, expiry, outage behavior, and cleanup.

**Deliverables expected:** a component/workflow diagram, ownership and evidence table, failure modes, rollback/recovery path, and a short decision record. State assumptions and include at least two viable alternatives.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Define flag type and purpose, owner, creation/change review, safe default, targeting limits, privacy constraints, telemetry, expiry date, removal criteria, and emergency kill-switch behavior. Test provider outage and stale-cache behavior, and coordinate flag state with deployment/schema compatibility and rollback.

**Reasoning**

Flags decouple deployment from exposure, but create operational state that must be owned and observed. They do not replace backward-compatible deployment design.

**Common wrong answers**

- **Assume disabling a flag restores the old system** — A flag does not undo schema changes or external side effects.
- **Leave flags without owner or expiry** — Unowned flags create ambiguous behavior and permanent test-state complexity.

**Operational caveat**

Exact SDK and provider outage behavior must be verified for the chosen implementation.

**Scoring rubric**

10 points: safety/correctness 2; evidence and verification 2; alternatives and trade-offs 2; failure/recovery plan 2; ownership, clarity, and unresolved uncertainty 2.

</details>

---

# Unit 11 — Database and data-platform migration safety (12 questions)

### U11-Q01 — Explain the core model for expand-migrate-contract, idempotency, backups, rollback/roll-forward

- **Unit / topic:** Database and data-platform migration safety
- **Level:** L1
- **Question type:** conceptual
- **Objective tested:** sequence schema and application changes for compatibility
- **Estimated time:** 6 minutes

**Question / scenario**

Explain the core model for expand-migrate-contract, idempotency, backups, rollback/roll-forward. In your answer, distinguish the desired configuration, the controller or process that acts on it, and the evidence that shows whether the intended outcome actually occurred.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Expand–migrate–contract separates additive schema changes, data migration and dual-compatible application versions, and later removal of obsolete schema.

**Reasoning**

Migration correctness depends on compatibility across overlapping versions, lock/backfill behavior, idempotency, validation, and recovery objectives. A completed Job or reversible script is not proof that data can safely return to the prior version.

**Common wrong answers**

- **Assume a down migration makes rollback safe** New writes or destructive transformations may not be reversible.
- **Run a backfill again without checking idempotency** Retries can duplicate or corrupt data when progress and keys are not designed safely.

**Operational caveat**

DDL locking, transaction semantics, backfill performance, and schema evolution depend on the database/lakehouse engine. Test with representative data and a verified restore path.

**Scoring rubric**

Full credit (3 points): states the core mechanism accurately (1), distinguishes what the evidence does and does not prove (1), and identifies a safe next check or operational implication (1).

</details>

---

### U11-Q02 — Sequence a required-column migration safely

- **Unit / topic:** — Database and data-platform migration safety
- **Level:** — L2
- **Question type:** — conceptual
- **Objective tested:** — predict and verify sequence a required-column migration safely
- **Estimated time:** — 7 minutes

**Question / scenario**

A migration adds a NOT NULL column while old application replicas are still writing rows without that field. Identify the compatibility failure and a safer migration sequence.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The migration can fail on existing rows or reject old writers unless a safe default/backfill and compatibility sequence is designed. Prefer expand–migrate–contract: add a nullable or otherwise backward-compatible field, deploy code that can read/write both forms, backfill idempotently, validate completeness, switch behavior, and only later enforce NOT NULL/remove old fields after old writers are gone.

**Reasoning**

Schema changes must coexist with overlapping application versions during progressive rollout and rollback. Ordering is a compatibility property, not merely a deployment-order preference.

**Common wrong answers**

- **Assume a down migration makes rollback safe** — New writes or destructive transformations may not be reversible.
- **Run a backfill again without checking idempotency** — Retries can duplicate or corrupt data when progress and keys are not designed safely.

**Operational caveat**

Database locking, DDL semantics, and lakehouse schema evolution depend on engine/format. Verify with production-like volume and a recovery plan.

**Scoring rubric**

Full credit (3 points): states the correct operational conclusion (1), cites the evidence/policy that supports it (1), and names a safe next check plus a remaining uncertainty (1).

</details>

---

### U11-Q03 — Validate migration output before switching traffic

- **Unit / topic:** — Database and data-platform migration safety
- **Level:** — L3
- **Question type:** — conceptual
- **Objective tested:** — diagnose and recover safely from validate migration output before switching traffic
- **Estimated time:** — 8 minutes

**Question / scenario**

A migration Job reports `Complete`, but downstream row counts and aggregates disagree with the pre-migration baseline. What should happen before traffic is switched?

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Treat Job completion as execution evidence, not correctness proof. Stop the switch, preserve logs/checkpoints, compare source and target counts/checksums/business aggregates, inspect duplicates/nulls/schema changes, and determine whether the backfill is resumable/idempotent. Restore from a tested backup or roll forward only under the approved recovery plan.

**Reasoning**

Data validation is an independent gate. A completed process can produce semantically incorrect data.

**Common wrong answers**

- **Assume a down migration makes rollback safe** — New writes or destructive transformations may not be reversible.
- **Run a backfill again without checking idempotency** — Retries can duplicate or corrupt data when progress and keys are not designed safely.

**Operational caveat**

Counts alone may miss semantic corruption. Use domain-appropriate invariants and verify backup/PITR capability before destructive changes.

**Scoring rubric**

Full credit (4 points): identifies the relevant state/evidence (1), orders diagnosis before mutation (1), checks blast radius and rollback/data compatibility (1), and defines verification/prevention (1).

</details>

---

### U11-Q04 — When should a destructive contract migration occur?

- **Unit / topic:** Database and data-platform migration safety
- **Level:** L1
- **Question type:** MCQ
- **Objective tested:** sequence schema and application changes for compatibility
- **Estimated time:** 3 minutes

**Question / scenario**

When should a destructive contract migration occur?

A. Immediately after the first new pod is Ready
B. After old consumers and rollback paths no longer require the old schema, with validated backup/recovery and explicit approval
C. Before the expand phase
D. Whenever a Job exits zero

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**B**. After old consumers and rollback paths no longer require the old schema, with validated backup/recovery and explicit approval

**Reasoning**

- **A. Incorrect.** The option proposes “Immediately after the first new pod is Ready”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.
- **B. Correct.** Contract is delayed until compatibility and recovery conditions are met.
- **C. Incorrect.** The option proposes “Before the expand phase”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.
- **D. Incorrect.** The option proposes “Whenever a Job exits zero”; it makes a universal guarantee that the evidence does not support; controller and provider behavior depends on explicit policy, version, and observed state.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses assume a down migration makes rollback safe with verified state, or skips the required safety check: New writes or destructive transformations may not be reversible.

**Operational caveat**

DDL locking, transaction semantics, backfill performance, and schema evolution depend on the database/lakehouse engine. Test with representative data and a verified restore path.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U11-Q05 — A backfill is retried and duplicates records. What control was missing?

- **Unit / topic:** Database and data-platform migration safety
- **Level:** L2
- **Question type:** MCQ
- **Objective tested:** assess lock/backfill/idempotency and recovery constraints
- **Estimated time:** 3 minutes

**Question / scenario**

A backfill is retried and duplicates records. What control was missing?

A. A larger image tag
B. Idempotency/checkpointing and uniqueness/validation semantics
C. A feature flag name
D. A controller dashboard

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**B**. Idempotency/checkpointing and uniqueness/validation semantics

**Reasoning**

- **A. Incorrect.** The option proposes “A larger image tag”; a mutable tag can point to different bytes over time and therefore does not prove the exact artifact that was tested or ran.
- **B. Correct.** Retries are normal in distributed operations; migration logic must safely resume.
- **C. Incorrect.** The option proposes “A feature flag name”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.
- **D. Incorrect.** The option proposes “A controller dashboard”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses assume a down migration makes rollback safe with verified state, or skips the required safety check: New writes or destructive transformations may not be reversible.

**Operational caveat**

DDL locking, transaction semantics, backfill performance, and schema evolution depend on the database/lakehouse engine. Test with representative data and a verified restore path.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U11-Q06 — Why may roll-forward be safer than rollback?

- **Unit / topic:** Database and data-platform migration safety
- **Level:** L3
- **Question type:** MCQ
- **Objective tested:** choose rollback versus roll-forward based on data compatibility
- **Estimated time:** 3 minutes

**Question / scenario**

Why may roll-forward be safer than rollback?

A. Rollback is always forbidden
B. New writes or schema changes may be unreadable by the old version, while a forward fix preserves valid state
C. The Git tag cannot be changed
D. Roll-forward needs no validation

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**B**. New writes or schema changes may be unreadable by the old version, while a forward fix preserves valid state

**Reasoning**

- **A. Incorrect.** The option proposes “Rollback is always forbidden”; it makes a universal guarantee that the evidence does not support; controller and provider behavior depends on explicit policy, version, and observed state.
- **B. Correct.** Choose recovery based on state compatibility, tested fixes, and customer/data risk.
- **C. Incorrect.** The option proposes “The Git tag cannot be changed”; a mutable tag can point to different bytes over time and therefore does not prove the exact artifact that was tested or ran.
- **D. Incorrect.** The option proposes “Roll-forward needs no validation”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses assume a down migration makes rollback safe with verified state, or skips the required safety check: New writes or destructive transformations may not be reversible.

**Operational caveat**

DDL locking, transaction semantics, backfill performance, and schema evolution depend on the database/lakehouse engine. Test with representative data and a verified restore path.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U11-Q07 — Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Database and data-platform

- **Unit / topic:** Database and data-platform migration safety
- **Level:** L2
- **Question type:** output interpretation
- **Objective tested:** sequence schema and application changes for compatibility
- **Estimated time:** 7 minutes

**Question / scenario**

Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Database and data-platform migration safety:

```text
SIMULATED / REPRESENTATIVE
Migration 014: add delivery_mode NOT NULL DEFAULT 'express'
Backfill: 82% complete
Old application replicas: 2
New application replicas: 3
Old reader errors: unknown-field delivery_mode
Rollback requested: old version cannot read new records
```

State what is established, what remains unknown, the safest next diagnostic step, and whether you would promote, reconcile, pause, abort, or gather more evidence. Justify the decision using specific fields/lines above.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Migration 014 adds a non-null field while old application replicas remain; the old reader reports `unknown-field`, and rollback is unsafe because it cannot read new records. Stop further incompatible writes and assess affected data. Prefer a tested forward-compatible fix unless a validated restore path meets RPO/RTO; do not blindly redeploy the old version.

**Reasoning**

Output interpretation must separate observations from inference. A status or event can be stale, partial, or scoped to a single resource; the next check should target the earliest missing/failed link and preserve the current evidence.

**Common wrong answers**

- **Assume the best because one field is green.** That ignores contradictory fields and coverage gaps.
- **Mutate immediately.** Diagnose source, identity, scope, and rollback safety first unless containment urgency requires a minimal authorized action.

**Operational caveat**

All output is simulated; it is not claimed to come from a live cluster. Exact CLI output and controller status wording are `[VERIFY]` for the installed version.

**Scoring rubric**

Full credit: cite two specific fields, identify one unknown, choose a safe next action, and explain promotion/rollback constraints (4 points).

</details>

---

### U11-Q08 — Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Database and data-platform

- **Unit / topic:** Database and data-platform migration safety
- **Level:** L3
- **Question type:** output interpretation
- **Objective tested:** assess lock/backfill/idempotency and recovery constraints
- **Estimated time:** 8 minutes

**Question / scenario**

Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Database and data-platform migration safety:

```text
SIMULATED / REPRESENTATIVE
Backfill run 1: processed 100,000 rows
Job restarted after timeout
Backfill run 2: processed 100,000 rows
Rows changed: 200,000
Expected unique rows: 100,000
Idempotency check: FAIL
```

State what is established, what remains unknown, the safest next diagnostic step, and whether you would promote, reconcile, pause, abort, or gather more evidence. Justify the decision using specific fields/lines above.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The same 100,000 rows were processed twice, producing 200,000 changes against 100,000 expected unique rows. The backfill is not idempotent or checkpoint-safe. Pause it, quantify duplicates, preserve logs/checkpoints, repair data under backup/approval, then implement idempotent batches and uniqueness/validation tests before resuming.

**Reasoning**

Output interpretation must separate observations from inference. A status or event can be stale, partial, or scoped to a single resource; the next check should target the earliest missing/failed link and preserve the current evidence.

**Common wrong answers**

- **Assume the best because one field is green.** That ignores contradictory fields and coverage gaps.
- **Mutate immediately.** Diagnose source, identity, scope, and rollback safety first unless containment urgency requires a minimal authorized action.

**Operational caveat**

All output is simulated; it is not claimed to come from a live cluster. Exact CLI output and controller status wording are `[VERIFY]` for the installed version.

**Scoring rubric**

Full credit: cite two specific fields, identify one unknown, choose a safe next action, and explain promotion/rollback constraints (4 points).

</details>

---

### U11-Q09 — Review this `INTENTIONALLY FLAWED` example for Database and data-platform migration safety. Ide

- **Unit / topic:** Database and data-platform migration safety
- **Level:** L3
- **Question type:** configuration/manifest review
- **Objective tested:** sequence schema and application changes for compatibility
- **Estimated time:** 10 minutes

**Question / scenario**

Review this `INTENTIONALLY FLAWED` example for Database and data-platform migration safety. Identify at least three distinct defects, explain their operational impact, and propose a corrected version or exact correction.

```yaml
apiVersion: batch/v1
kind: Job
metadata: {name: orders-backfill}
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: migrate
        image: registry.example.invalid/migrator:latest
        command: ["/bin/sh", "-c", "run-migration --unbounded"]
```

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The defects are:

1. The migration image uses mutable `latest`.
2. The command is an unbounded one-shot update without batch limits/checkpoints/idempotency.
3. The Job has no explicit retry/backoff or migration identity/validation; execution success would not prove data correctness.

**Corrected direction/snippet:**

```yaml
# Illustrative job intent; implement bounded, checkpointed, idempotent migration in application code.
apiVersion: batch/v1
kind: Job
metadata: {name: orders-backfill}
spec:
  backoffLimit: 2
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: migrate
        image: registry.example.invalid/migrator@sha256:REPLACE_WITH_REAL_DIGEST
        args: ["--migration-id=014", "--batch-size=500", "--resume-from-checkpoint"]
# Validate backup/restore, locking, permissions, and compatibility before production execution.
```

The correction is an instructional pattern; confirm product-specific schema and provider support before applying it.

**Reasoning**

The defects are not merely style issues: they can make resources fail to select, weaken access boundaries, make the artifact mutable, trigger unintended deletion, leak sensitive data, or convert missing evidence into an unsafe action. Corrections must be tested in a disposable environment.

**Common wrong answers**

- **Fix only syntax.** A valid manifest can still be insecure or semantically unsafe.
- **Assume an illustrative snippet is a complete deployable CRD.** Required fields and semantics depend on the installed API/version.

**Operational caveat**

The original is intentionally flawed and must not be applied. Corrected snippets may be bounded examples rather than complete production configuration; `[VERIFY]` any controller-specific fields.

**Scoring rubric**

Full credit: at least three distinct defects (3 points), impact for each (3), corrected snippet/direction (2), version/safety caveat (2).

</details>

---

### U11-Q10 — Review this `INTENTIONALLY FLAWED` example for Database and data-platform migration safety. Ide

- **Unit / topic:** Database and data-platform migration safety
- **Level:** L3
- **Question type:** configuration/manifest review
- **Objective tested:** assess lock/backfill/idempotency and recovery constraints
- **Estimated time:** 10 minutes

**Question / scenario**

Review this `INTENTIONALLY FLAWED` example for Database and data-platform migration safety. Identify at least three distinct defects, explain their operational impact, and propose a corrected version or exact correction.

```yaml
-- INTENTIONALLY FLAWED migration example
ALTER TABLE orders DROP COLUMN legacy_status;
-- no backup reference
-- no compatibility window
-- rollback assumes the old column can be recreated with its values
```

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The defects are:

1. The migration drops a column before a compatibility window.
2. No backup/PITR reference or tested restore path is recorded.
3. The assumed rollback cannot recreate dropped values, so the operation is not reversibly safe.

**Corrected direction/snippet:**

```yaml
-- Safer staged intent; exact SQL depends on the database engine
-- 1. Add the replacement field without removing legacy_status.
-- 2. Deploy code that can read/write both forms.
-- 3. Backfill in bounded idempotent batches and validate counts/checksums.
-- 4. Switch reads/writes, observe, and retain recovery window.
-- 5. Drop legacy_status only after consumers and rollback window are proven clear.
-- Record backup/PITR point and tested restore procedure before destructive contract phase.
```

The correction is an instructional pattern; confirm product-specific schema and provider support before applying it.

**Reasoning**

The defects are not merely style issues: they can make resources fail to select, weaken access boundaries, make the artifact mutable, trigger unintended deletion, leak sensitive data, or convert missing evidence into an unsafe action. Corrections must be tested in a disposable environment.

**Common wrong answers**

- **Fix only syntax.** A valid manifest can still be insecure or semantically unsafe.
- **Assume an illustrative snippet is a complete deployable CRD.** Required fields and semantics depend on the installed API/version.

**Operational caveat**

The original is intentionally flawed and must not be applied. Corrected snippets may be bounded examples rather than complete production configuration; `[VERIFY]` any controller-specific fields.

**Scoring rubric**

Full credit: at least three distinct defects (3 points), impact for each (3), corrected snippet/direction (2), version/safety caveat (2).

</details>

---

### U11-Q11 — Incident: A new application writes a non-null `delivery_mode` field. The previous version does 

- **Unit / topic:** Database and data-platform migration safety
- **Level:** L4
- **Question type:** incident/troubleshooting
- **Objective tested:** choose rollback versus roll-forward based on data compatibility
- **Estimated time:** 15 minutes

**Question / scenario**

Incident: A new application writes a non-null `delivery_mode` field. The previous version does not know that field and fails on records written by the new version.

Provide symptom → diagnosis → evidence to preserve → blast-radius and rollback-safety check → containment/recovery → prevention. Identify one residual uncertainty that must not be presented as fact.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**Symptom:** A new application writes a non-null `delivery_mode` field. The previous version does not know that field and fails on records written by the new version.

**Diagnosis:** Expand–migrate–contract separates additive schema changes, data migration and dual-compatible application versions, and later removal of obsolete schema.

**Evidence:** collect the relevant Git revision/PR, controller conditions/events, live resource state, runtime/metric samples, timestamps, and actor/approval data as applicable.

**Blast radius and rollback:** identify affected environments/replicas/consumers, determine whether state/data/external side effects changed, and test whether the prior version can safely read current state. Do not assume an image rollback reverses data.

**Containment/recovery:** use the smallest authorized reversible action; pause promotion or isolate the affected path if warranted; preserve a before/after record; reconcile the intended fix into the declared source; verify customer-facing behavior.

**Prevention:** Backfills should be resumable and idempotent, bounded, observable, and tested against production-like volume; a Kubernetes Job being complete does not prove data correctness.

**Residual uncertainty:** any missing history, unknown consumer behavior, unparseable runtime identity, or absent metric sample remains UNKNOWN until corroborated.

**Reasoning**

The incident response separates preserving evidence from containment, makes recovery contingent on state compatibility, and verifies both control-plane convergence and application-level outcome.

**Common wrong answers**

- **Immediately force-sync/redeploy without preserving evidence.** This can erase the live state that explains the incident.
- **Assume rollback is safe because the previous artifact exists.** Data, schema, event, or external side effects may be incompatible.

**Operational caveat**

Escalate to the incident commander/security owner when compromise or regulated data is plausible. Use only approved break-glass authority and an explicit reconciliation/review path.

**Scoring rubric**

10 points: diagnosis 2; evidence 2; blast radius/rollback 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### U11-Q12 — Design a recoverable zero-downtime migration

- **Unit / topic:** — Database and data-platform migration safety
- **Level:** — L4
- **Question type:** — design
- **Objective tested:** — design a safe, auditable workflow for database and data-platform migration safety
- **Estimated time:** — 20 minutes

**Question / scenario**

Design a zero-downtime schema migration with old/new application overlap, resumable backfill, verification, and a safe recovery path.

**Deliverables expected:** a component/workflow diagram, ownership and evidence table, failure modes, rollback/recovery path, and a short decision record. State assumptions and include at least two viable alternatives.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Use expand–migrate–contract: add backward-compatible schema, deploy tolerant readers/writers, backfill in bounded idempotent batches with checkpoints, compare counts and domain invariants, shift reads/writes, then contract only after old versions and consumers are retired. Capture backup/snapshot, RPO/RTO, migration ID, validation output, and a roll-forward/restore decision.

**Reasoning**

Migration safety depends on application overlap, write semantics, locking, data validation, and recovery—not just whether a migration script has a down method.

**Common wrong answers**

- **Assume a down migration makes rollback safe** — New writes or destructive transformations may not be reversible.
- **Run a backfill again without checking idempotency** — Retries can duplicate or corrupt data when progress and keys are not designed safely.

**Operational caveat**

Exact locking and transaction behavior depend on the database/lakehouse engine and volume. Rehearse the plan on representative data.

**Scoring rubric**

10 points: safety/correctness 2; evidence and verification 2; alternatives and trade-offs 2; failure/recovery plan 2; ownership, clarity, and unresolved uncertainty 2.

</details>

---

# Unit 12 — Backward-compatible pipeline and API releases (12 questions)

### U12-Q01 — Explain the core model for producer/consumer compatibility, contracts, deprecation, N-1. In you

- **Unit / topic:** Backward-compatible pipeline and API releases
- **Level:** L1
- **Question type:** conceptual
- **Objective tested:** classify backward/forward/breaking and semantic changes
- **Estimated time:** 6 minutes

**Question / scenario**

Explain the core model for producer/consumer compatibility, contracts, deprecation, N-1. In your answer, distinguish the desired configuration, the controller or process that acts on it, and the evidence that shows whether the intended outcome actually occurred.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Schema validity is not semantic compatibility. An unchanged field type can change meaning, units, nullability, ordering, or default behavior and still break consumers.

**Reasoning**

Compatibility includes semantics and the producer/consumer combinations that coexist during rollout and rollback. Schema checks must be complemented by contract tests, replay/shadow comparison, deprecation telemetry, and N-1 reasoning.

**Common wrong answers**

- **Rely only on schema validation** Syntactically valid payloads can change meaning, units, defaults, or consumer assumptions.
- **Switch all consumers without N-1 tests** Overlapping versions and persisted events require explicit compatibility evidence.

**Operational caveat**

Protocol compatibility differs across REST/JSON, Protobuf/gRPC, events, and data formats. Verify actual consumer behavior with contract/replay tests rather than assuming schema checks are sufficient.

**Scoring rubric**

Full credit (3 points): states the core mechanism accurately (1), distinguishes what the evidence does and does not prove (1), and identifies a safe next check or operational implication (1).

</details>

---

### U12-Q02 — Assess semantic compatibility of an event change

- **Unit / topic:** — Backward-compatible pipeline and API releases
- **Level:** — L2
- **Question type:** — conceptual
- **Objective tested:** — predict and verify assess semantic compatibility of an event change
- **Estimated time:** — 7 minutes

**Question / scenario**

A producer adds an optional JSON field, but a consumer changes its interpretation of an existing field without changing the schema. Is this backward-compatible?

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

No guarantee. Syntactic schema compatibility does not establish semantic compatibility. Consumers may rely on units, ordering, null/default behavior, enum meanings, or invariants that changed. Review the contract, test old/new producer-consumer combinations, replay representative events, and monitor consumer outcomes before promotion.

**Reasoning**

Compatibility includes meaning and behavior, not just field presence. N-1 support must account for overlapping versions and persisted messages/data.

**Common wrong answers**

- **Rely only on schema validation** — Syntactically valid payloads can change meaning, units, defaults, or consumer assumptions.
- **Switch all consumers without N-1 tests** — Overlapping versions and persisted events require explicit compatibility evidence.

**Operational caveat**

Contract semantics depend on consumer behavior and protocol. Verify with contract/replay tests and document version/deprecation policy.

**Scoring rubric**

Full credit (3 points): states the correct operational conclusion (1), cites the evidence/policy that supports it (1), and names a safe next check plus a remaining uncertainty (1).

</details>

---

### U12-Q03 — Protect old consumers during producer rollout

- **Unit / topic:** — Backward-compatible pipeline and API releases
- **Level:** — L3
- **Question type:** — conceptual
- **Objective tested:** — diagnose and recover safely from protect old consumers during producer rollout
- **Estimated time:** — 8 minutes

**Question / scenario**

A new producer version is live, but a long-lived consumer still expects the old event semantics. How should promotion and rollback be handled?

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Pause further rollout and identify affected consumers and persisted events. Prefer a backward-compatible producer change or a versioned event contract with tolerant readers; use replay/shadow diff and consumer-driven tests. Before rollback, check whether the old consumer can read events already written by the new producer; if not, roll forward or transform data under a tested plan.

**Reasoning**

Producer/consumer overlap and persisted data make rollback a contract problem. Restoring code cannot undo messages already emitted.

**Common wrong answers**

- **Rely only on schema validation** — Syntactically valid payloads can change meaning, units, defaults, or consumer assumptions.
- **Switch all consumers without N-1 tests** — Overlapping versions and persisted events require explicit compatibility evidence.

**Operational caveat**

Protocol-specific rules for Protobuf, gRPC, event schemas, and API gateways must be verified against the chosen tooling.

**Scoring rubric**

Full credit (4 points): identifies the relevant state/evidence (1), orders diagnosis before mutation (1), checks blast radius and rollback/data compatibility (1), and defines verification/prevention (1).

</details>

---

### U12-Q04 — A JSON schema check passes after changing the meaning of `amount` from cents to dollars. What d

- **Unit / topic:** Backward-compatible pipeline and API releases
- **Level:** L1
- **Question type:** MCQ
- **Objective tested:** classify backward/forward/breaking and semantic changes
- **Estimated time:** 3 minutes

**Question / scenario**

A JSON schema check passes after changing the meaning of `amount` from cents to dollars. What does the result prove?

A. Full semantic compatibility
B. Only that the structural rules checked by that schema passed; semantic behavior still requires contract/replay tests
C. That all consumers were tested
D. That rollback is safe

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**B**. Only that the structural rules checked by that schema passed; semantic behavior still requires contract/replay tests

**Reasoning**

- **A. Incorrect.** The option proposes “Full semantic compatibility”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.
- **B. Correct.** Structural schemas cannot necessarily detect unit changes or business-semantic changes.
- **C. Incorrect.** The option proposes “That all consumers were tested”; structural shape alone cannot establish semantic compatibility across real producers and consumers.
- **D. Incorrect.** The option proposes “That rollback is safe”; the availability of an old binary does not reverse writes or prove compatibility with current schema, events, or state.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses rely only on schema validation with verified state, or skips the required safety check: Syntactically valid payloads can change meaning, units, defaults, or consumer assumptions.

**Operational caveat**

Protocol compatibility differs across REST/JSON, Protobuf/gRPC, events, and data formats. Verify actual consumer behavior with contract/replay tests rather than assuming schema checks are sufficient.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U12-Q05 — What is a safer way to add a request field while old clients still exist?

- **Unit / topic:** Backward-compatible pipeline and API releases
- **Level:** L2
- **Question type:** MCQ
- **Objective tested:** design additive evolution and consumer contract checks
- **Estimated time:** 3 minutes

**Question / scenario**

What is a safer way to add a request field while old clients still exist?

A. Make the field required immediately
B. Add it as optional with a documented default/behavior, measure consumers, then deprecate old forms deliberately
C. Rename all fields at once
D. Skip contract tests because OpenAPI exists

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**B**. Add it as optional with a documented default/behavior, measure consumers, then deprecate old forms deliberately

**Reasoning**

- **A. Incorrect.** The option proposes “Make the field required immediately”; structural shape alone cannot establish semantic compatibility across real producers and consumers.
- **B. Correct.** Compatibility depends on client populations and semantics; stage changes and observe usage.
- **C. Incorrect.** The option proposes “Rename all fields at once”; structural shape alone cannot establish semantic compatibility across real producers and consumers.
- **D. Incorrect.** The option proposes “Skip contract tests because OpenAPI exists”; it proposes an unsafe shortcut without first establishing authorization, impact, evidence preservation, and a recovery path.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses rely only on schema validation with verified state, or skips the required safety check: Syntactically valid payloads can change meaning, units, defaults, or consumer assumptions.

**Operational caveat**

Protocol compatibility differs across REST/JSON, Protobuf/gRPC, events, and data formats. Verify actual consumer behavior with contract/replay tests rather than assuming schema checks are sufficient.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U12-Q06 — What should be checked before rolling back a producer?

- **Unit / topic:** Backward-compatible pipeline and API releases
- **Level:** L3
- **Question type:** MCQ
- **Objective tested:** assess N-1 and rollback compatibility across APIs, events, data and model interfaces
- **Estimated time:** 3 minutes

**Question / scenario**

What should be checked before rolling back a producer?

A. Only whether the old image still exists
B. Whether new events/data written by the current version remain readable/processable by the old version
C. Only API latency
D. Whether the PR title is conventional

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**B**. Whether new events/data written by the current version remain readable/processable by the old version

**Reasoning**

- **A. Incorrect.** The option proposes “Only whether the old image still exists”; the availability of an old binary does not reverse writes or prove compatibility with current schema, events, or state.
- **B. Correct.** Rollback can fail at the data boundary even when the binary can be redeployed.
- **C. Incorrect.** The option proposes “Only API latency”; it narrows the decision to one signal and omits the other required checks, such as ownership, runtime state, telemetry quality, or recovery safety.
- **D. Incorrect.** The option proposes “Whether the PR title is conventional”; Git records intent and review context but does not by itself prove what the cluster ran or that every required approval/promotion record exists.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses rely only on schema validation with verified state, or skips the required safety check: Syntactically valid payloads can change meaning, units, defaults, or consumer assumptions.

**Operational caveat**

Protocol compatibility differs across REST/JSON, Protobuf/gRPC, events, and data formats. Verify actual consumer behavior with contract/replay tests rather than assuming schema checks are sufficient.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U12-Q07 — Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Backward-compatible pipeli

- **Unit / topic:** Backward-compatible pipeline and API releases
- **Level:** L2
- **Question type:** output interpretation
- **Objective tested:** classify backward/forward/breaking and semantic changes
- **Estimated time:** 7 minutes

**Question / scenario**

Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Backward-compatible pipeline and API releases:

```text
SIMULATED / REPRESENTATIVE
Contract check: PASS (field `amount` remains integer)
Semantic replay: FAIL
Old sample: amount=1250 means 12.50 USD cents-based representation
New sample: amount=1250 means 1,250 USD
Downstream total: 100x larger than expected
```

State what is established, what remains unknown, the safest next diagnostic step, and whether you would promote, reconcile, pause, abort, or gather more evidence. Justify the decision using specific fields/lines above.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The structural contract passes because `amount` remains an integer, but replay fails because its unit changed and the downstream total is 100× expected. This is a semantic breaking change. Restore the documented old meaning or introduce a new explicitly named/versioned field with dual-read/write and consumer replay; schema validation alone is insufficient.

**Reasoning**

Output interpretation must separate observations from inference. A status or event can be stale, partial, or scoped to a single resource; the next check should target the earliest missing/failed link and preserve the current evidence.

**Common wrong answers**

- **Assume the best because one field is green.** That ignores contradictory fields and coverage gaps.
- **Mutate immediately.** Diagnose source, identity, scope, and rollback safety first unless containment urgency requires a minimal authorized action.

**Operational caveat**

All output is simulated; it is not claimed to come from a live cluster. Exact CLI output and controller status wording are `[VERIFY]` for the installed version.

**Scoring rubric**

Full credit: cite two specific fields, identify one unknown, choose a safe next action, and explain promotion/rollback constraints (4 points).

</details>

---

### U12-Q08 — Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Backward-compatible pipeli

- **Unit / topic:** Backward-compatible pipeline and API releases
- **Level:** L3
- **Question type:** output interpretation
- **Objective tested:** design additive evolution and consumer contract checks
- **Estimated time:** 8 minutes

**Question / scenario**

Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Backward-compatible pipeline and API releases:

```text
SIMULATED / REPRESENTATIVE
Consumer A deployed v2.4 (tolerates optional field region)
Consumer B deployed v2.3 (rejects unknown enum value `EXPRESS_PLUS`)
Producer v2.5 emits EXPRESS_PLUS to 30% of events
Schema registry structural check: PASS
Consumer contract: FAIL
```

State what is established, what remains unknown, the safest next diagnostic step, and whether you would promote, reconcile, pause, abort, or gather more evidence. Justify the decision using specific fields/lines above.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Consumer B rejects `EXPRESS_PLUS` while producer v2.5 emits it to 30% of events. The structural registry check passes, but consumer compatibility fails. Stop/limit emission, coordinate consumer support or version the event, replay representative data, and promote only when actual consumer contracts pass.

**Reasoning**

Output interpretation must separate observations from inference. A status or event can be stale, partial, or scoped to a single resource; the next check should target the earliest missing/failed link and preserve the current evidence.

**Common wrong answers**

- **Assume the best because one field is green.** That ignores contradictory fields and coverage gaps.
- **Mutate immediately.** Diagnose source, identity, scope, and rollback safety first unless containment urgency requires a minimal authorized action.

**Operational caveat**

All output is simulated; it is not claimed to come from a live cluster. Exact CLI output and controller status wording are `[VERIFY]` for the installed version.

**Scoring rubric**

Full credit: cite two specific fields, identify one unknown, choose a safe next action, and explain promotion/rollback constraints (4 points).

</details>

---

### U12-Q09 — Review this `INTENTIONALLY FLAWED` example for Backward-compatible pipeline and API releases. I

- **Unit / topic:** Backward-compatible pipeline and API releases
- **Level:** L3
- **Question type:** configuration/manifest review
- **Objective tested:** classify backward/forward/breaking and semantic changes
- **Estimated time:** 10 minutes

**Question / scenario**

Review this `INTENTIONALLY FLAWED` example for Backward-compatible pipeline and API releases. Identify at least three distinct defects, explain their operational impact, and propose a corrected version or exact correction.

```yaml
openapi: 3.1.0
info: {title: Orders API, version: "2.0"}
paths:
  /orders:
    post:
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [customer_id, delivery_mode]
              properties:
                customer_id: {type: string}
                delivery_mode: {type: string, enum: [STANDARD, EXPRESS]}
                amount: {type: integer, description: "Amount"}
```

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The defects are:

1. `delivery_mode` is newly required, breaking older clients that do not send it.
2. The enum has no compatibility plan for consumers that reject unknown values.
3. The `amount` field has ambiguous units and no stable semantic contract.

**Corrected direction/snippet:**

```yaml
openapi: 3.1.0
info: {title: Orders API, version: "2.0"}
paths:
  /orders:
    post:
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [customer_id]
              properties:
                customer_id: {type: string}
                delivery_mode: {type: string, enum: [STANDARD, EXPRESS]}
                amount_minor: {type: integer, description: "Amount in minor currency units (for example, cents); do not reinterpret existing amount silently."}
# Keep old field/semantics during a compatibility window and deprecate only after consumer evidence.
```

The correction is an instructional pattern; confirm product-specific schema and provider support before applying it.

**Reasoning**

The defects are not merely style issues: they can make resources fail to select, weaken access boundaries, make the artifact mutable, trigger unintended deletion, leak sensitive data, or convert missing evidence into an unsafe action. Corrections must be tested in a disposable environment.

**Common wrong answers**

- **Fix only syntax.** A valid manifest can still be insecure or semantically unsafe.
- **Assume an illustrative snippet is a complete deployable CRD.** Required fields and semantics depend on the installed API/version.

**Operational caveat**

The original is intentionally flawed and must not be applied. Corrected snippets may be bounded examples rather than complete production configuration; `[VERIFY]` any controller-specific fields.

**Scoring rubric**

Full credit: at least three distinct defects (3 points), impact for each (3), corrected snippet/direction (2), version/safety caveat (2).

</details>

---

### U12-Q10 — Review this `INTENTIONALLY FLAWED` example for Backward-compatible pipeline and API releases. I

- **Unit / topic:** Backward-compatible pipeline and API releases
- **Level:** L3
- **Question type:** configuration/manifest review
- **Objective tested:** design additive evolution and consumer contract checks
- **Estimated time:** 10 minutes

**Question / scenario**

Review this `INTENTIONALLY FLAWED` example for Backward-compatible pipeline and API releases. Identify at least three distinct defects, explain their operational impact, and propose a corrected version or exact correction.

**INTENTIONALLY FLAWED conceptual JSON:**

```json
{
  "event": "OrderCreated",
  "version": 2,
  "required": ["order_id", "amount"],
  "properties": {"order_id": "string", "amount": "number"},
  "compatibility": "breaking changes allowed without replay"
}
```

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The defects are:

1. The event requires `amount_minor` in v2 without showing a migration for existing consumers.
2. The property types are descriptive strings, not a valid formal schema for most schema systems.
3. The declared policy explicitly permits breaking changes without replay/consumer verification.

**Corrected direction/snippet:**

```json

{
  "event": "OrderCreated",
  "version": 2,
  "required": ["order_id", "amount_minor"],
  "properties": {"order_id": "string", "amount_minor": "integer with documented minor-unit semantics"},
  "migration": "dual-read/dual-write or versioned event with replay/consumer tests"
}
```

Preserve old semantics until all consumers and replay windows are accounted for; validate with the actual schema format/registry.

The correction is an instructional pattern; confirm product-specific schema and provider support before applying it.

**Reasoning**

The defects are not merely style issues: they can make resources fail to select, weaken access boundaries, make the artifact mutable, trigger unintended deletion, leak sensitive data, or convert missing evidence into an unsafe action. Corrections must be tested in a disposable environment.

**Common wrong answers**

- **Fix only syntax.** A valid manifest can still be insecure or semantically unsafe.
- **Assume an illustrative snippet is a complete deployable CRD.** Required fields and semantics depend on the installed API/version.

**Operational caveat**

The original is intentionally flawed and must not be applied. Corrected snippets may be bounded examples rather than complete production configuration; `[VERIFY]` any controller-specific fields.

**Scoring rubric**

Full credit: at least three distinct defects (3 points), impact for each (3), corrected snippet/direction (2), version/safety caveat (2).

</details>

---

### U12-Q11 — Incident: A producer keeps a numeric `amount` field but changes its unit from cents to dollars.

- **Unit / topic:** Backward-compatible pipeline and API releases
- **Level:** L4
- **Question type:** incident/troubleshooting
- **Objective tested:** assess N-1 and rollback compatibility across APIs, events, data and model interfaces
- **Estimated time:** 15 minutes

**Question / scenario**

Incident: A producer keeps a numeric `amount` field but changes its unit from cents to dollars. JSON schema validation still passes while downstream aggregates are wrong.

Provide symptom → diagnosis → evidence to preserve → blast-radius and rollback-safety check → containment/recovery → prevention. Identify one residual uncertainty that must not be presented as fact.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**Symptom:** A producer keeps a numeric `amount` field but changes its unit from cents to dollars. JSON schema validation still passes while downstream aggregates are wrong.

**Diagnosis:** Schema validity is not semantic compatibility. An unchanged field type can change meaning, units, nullability, ordering, or default behavior and still break consumers.

**Evidence:** collect the relevant Git revision/PR, controller conditions/events, live resource state, runtime/metric samples, timestamps, and actor/approval data as applicable.

**Blast radius and rollback:** identify affected environments/replicas/consumers, determine whether state/data/external side effects changed, and test whether the prior version can safely read current state. Do not assume an image rollback reverses data.

**Containment/recovery:** use the smallest authorized reversible action; pause promotion or isolate the affected path if warranted; preserve a before/after record; reconcile the intended fix into the declared source; verify customer-facing behavior.

**Prevention:** N-1 means the new system must coexist with the previous version during rollout/rollback. Producers, consumers, data writers/readers, and model preprocessing contracts must be considered together.

**Residual uncertainty:** any missing history, unknown consumer behavior, unparseable runtime identity, or absent metric sample remains UNKNOWN until corroborated.

**Reasoning**

The incident response separates preserving evidence from containment, makes recovery contingent on state compatibility, and verifies both control-plane convergence and application-level outcome.

**Common wrong answers**

- **Immediately force-sync/redeploy without preserving evidence.** This can erase the live state that explains the incident.
- **Assume rollback is safe because the previous artifact exists.** Data, schema, event, or external side effects may be incompatible.

**Operational caveat**

Escalate to the incident commander/security owner when compromise or regulated data is plausible. Use only approved break-glass authority and an explicit reconciliation/review path.

**Scoring rubric**

10 points: diagnosis 2; evidence 2; blast radius/rollback 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### U12-Q12 — Design backward-compatible producer/consumer evolution

- **Unit / topic:** — Backward-compatible pipeline and API releases
- **Level:** — L4
- **Question type:** — design
- **Objective tested:** — design a safe, auditable workflow for backward-compatible pipeline and api releases
- **Estimated time:** — 20 minutes

**Question / scenario**

Design a backward-compatible producer/consumer release process with contract tests, deprecation, N-1 support, and rollback evidence.

**Deliverables expected:** a component/workflow diagram, ownership and evidence table, failure modes, rollback/recovery path, and a short decision record. State assumptions and include at least two viable alternatives.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Publish and test an explicit contract; preserve additive compatible changes and tolerant readers; run old/new producer-consumer combinations and replay representative persisted events. Use consumer telemetry and a documented deprecation window, pin artifacts, and check whether the old version can read data/messages written by the new version before rollback.

**Reasoning**

Compatibility includes semantics and persisted state, not just schema shape. N-1 support requires safe overlap and an evidence-backed deprecation process.

**Common wrong answers**

- **Rely only on schema validation** — Syntactically valid payloads can change meaning, units, defaults, or consumer assumptions.
- **Switch all consumers without N-1 tests** — Overlapping versions and persisted events require explicit compatibility evidence.

**Operational caveat**

Exact compatibility guarantees depend on protocol and consumers. Verify using contract/replay tests and documented version/deprecation policy.

**Scoring rubric**

10 points: safety/correctness 2; evidence and verification 2; alternatives and trade-offs 2; failure/recovery plan 2; ownership, clarity, and unresolved uncertainty 2.

</details>

---

# Unit 13 — Release evidence and audit trails (12 questions)

### U13-Q01 — Explain the core model for provenance, release manifests, controller/runtime evidence, integrit

- **Unit / topic:** Release evidence and audit trails
- **Level:** L1
- **Question type:** conceptual
- **Objective tested:** distinguish audit trail, release evidence, observability, provenance, and attestation
- **Estimated time:** 6 minutes

**Question / scenario**

Explain the core model for provenance, release manifests, controller/runtime evidence, integrity and audit readiness. In your answer, distinguish the desired configuration, the controller or process that acts on it, and the evidence that shows whether the intended outcome actually occurred.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

A digest identifies artifact content; a signature/attestation makes claims only under a sound trust policy. A local hash proves byte equality relative to the hash, not who created the bytes.

**Reasoning**

Release evidence is a chain of linked claims, not a pile of files. Hashes, signatures, approvals, controller events, runtime observations, and post-deploy checks establish different facts and must be correlated by stable identifiers.

**Common wrong answers**

- **Infer the deployed artifact from a tag or green status** A tag can move and a controller status does not identify runtime bytes by itself.
- **Treat a detached SBOM/signature as proof of the live image** Evidence must link the SBOM/attestation subject to the observed runtime digest.

**Operational caveat**

Runtime imageID formats, controller history retention, Kubernetes audit policy, and WORM/object-lock semantics vary. Verify the installed platform and preserve missing evidence as UNKNOWN/INCOMPLETE.

**Scoring rubric**

Full credit (3 points): states the core mechanism accurately (1), distinguishes what the evidence does and does not prove (1), and identifies a safe next check or operational implication (1).

</details>

---

### U13-Q02 — Determine what a healthy controller status actually proves

- **Unit / topic:** — Release evidence and audit trails
- **Level:** — L2
- **Question type:** — conceptual
- **Objective tested:** — predict and verify determine what a healthy controller status actually proves
- **Estimated time:** — 7 minutes

**Question / scenario**

A release is marked healthy in the GitOps controller, but the team cannot link the running workload to the CI artifact digest or its SBOM. What can be claimed, and what evidence is missing?

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

You can claim only that the available controller status indicates its specific reconciliation/health conditions at the observed time. You cannot prove the exact artifact or its supply-chain linkage. Collect source commit/PR approvals, CI/build ID, artifact digest, SBOM subject, signature/attestation verification, config commit, controller sync/rollout records, runtime image identity, and post-deploy verification. Mark the chain INCOMPLETE until correlation is established.

**Reasoning**

Evidence must connect each release stage with stable identifiers. A healthy status or a detached SBOM cannot prove which bytes ran.

**Common wrong answers**

- **Infer the deployed artifact from a tag or green status** — A tag can move and a controller status does not identify runtime bytes by itself.
- **Treat a detached SBOM/signature as proof of the live image** — Evidence must link the SBOM/attestation subject to the observed runtime digest.

**Operational caveat**

Runtime imageID formats and controller-history retention vary. Verify parser assumptions and export transient evidence durably.

**Scoring rubric**

Full credit (3 points): states the correct operational conclusion (1), cites the evidence/policy that supports it (1), and names a safe next check plus a remaining uncertainty (1).

</details>

---

### U13-Q03 — Reconstruct a release after controller history expires

- **Unit / topic:** — Release evidence and audit trails
- **Level:** — L3
- **Question type:** — conceptual
- **Objective tested:** — diagnose and recover safely from reconstruct a release after controller history expires
- **Estimated time:** — 8 minutes

**Question / scenario**

The controller's historical events have expired and the team must answer who approved, promoted, and ran a release last quarter. How should the investigation proceed?

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Preserve remaining Git/PR, CI, registry, ticket, audit-log, rollout, and runtime records; correlate by release ID, digest, commit, environment, and timestamps. Clearly separate verified facts from inference and report the missing controller interval as INCOMPLETE. Do not claim a person or digest without supporting identity and runtime evidence; improve future retention/export after the investigation.

**Reasoning**

Different sources prove different claims: Git review proves an approval record, CI artifacts support build/test claims, and runtime observations support what was running. Missing records cannot be recreated reliably from memory.

**Common wrong answers**

- **Infer the deployed artifact from a tag or green status** — A tag can move and a controller status does not identify runtime bytes by itself.
- **Treat a detached SBOM/signature as proof of the live image** — Evidence must link the SBOM/attestation subject to the observed runtime digest.

**Operational caveat**

Retention and audit-log availability differ between managed and self-managed platforms. Record source coverage and gaps explicitly.

**Scoring rubric**

Full credit (4 points): identifies the relevant state/evidence (1), orders diagnosis before mutation (1), checks blast radius and rollback/data compatibility (1), and defines verification/prevention (1).

</details>

---

### U13-Q04 — What does a SHA-256 hash of a release manifest prove by itself?

- **Unit / topic:** Release evidence and audit trails
- **Level:** L1
- **Question type:** MCQ
- **Objective tested:** distinguish audit trail, release evidence, observability, provenance, and attestation
- **Estimated time:** 3 minutes

**Question / scenario**

What does a SHA-256 hash of a release manifest prove by itself?

A. Who approved the release
B. That the bytes match the calculated digest, assuming the digest is trusted
C. That the image ran in production
D. That the organization is compliant

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**B**. That the bytes match the calculated digest, assuming the digest is trusted

**Reasoning**

- **A. Incorrect.** The option proposes “Who approved the release”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.
- **B. Correct.** A hash is an integrity comparison; it does not establish origin or authorization without a trusted anchor.
- **C. Incorrect.** The option proposes “That the image ran in production”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.
- **D. Incorrect.** The option proposes “That the organization is compliant”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses infer the deployed artifact from a tag or green status with verified state, or skips the required safety check: A tag can move and a controller status does not identify runtime bytes by itself.

**Operational caveat**

Runtime imageID formats, controller history retention, Kubernetes audit policy, and WORM/object-lock semantics vary. Verify the installed platform and preserve missing evidence as UNKNOWN/INCOMPLETE.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U13-Q05 — The controller history has expired and no durable export exists. What should the audit query re

- **Unit / topic:** Release evidence and audit trails
- **Level:** L2
- **Question type:** MCQ
- **Objective tested:** correlate source/build/artifact/config/controller/rollout/runtime records
- **Estimated time:** 3 minutes

**Question / scenario**

The controller history has expired and no durable export exists. What should the audit query return?

A. Infer the release from the current Git tag
B. PASS because the controller is healthy now
C. INCOMPLETE/UNKNOWN for claims requiring the missing historical record, with gaps identified
D. Assume no deployment occurred

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**C**. INCOMPLETE/UNKNOWN for claims requiring the missing historical record, with gaps identified

**Reasoning**

- **A. Incorrect.** The option proposes “Infer the release from the current Git tag”; a mutable tag can point to different bytes over time and therefore does not prove the exact artifact that was tested or ran.
- **B. Incorrect.** The option proposes “PASS because the controller is healthy now”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.
- **C. Correct.** Current state cannot reconstruct every historical action; missing evidence must be reported honestly.
- **D. Incorrect.** The option proposes “Assume no deployment occurred”; it does not satisfy the evidence or safety condition in the question; the operator must use the stated policy and corroborating observations rather than this shortcut.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses infer the deployed artifact from a tag or green status with verified state, or skips the required safety check: A tag can move and a controller status does not identify runtime bytes by itself.

**Operational caveat**

Runtime imageID formats, controller history retention, Kubernetes audit policy, and WORM/object-lock semantics vary. Verify the installed platform and preserve missing evidence as UNKNOWN/INCOMPLETE.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U13-Q06 — Which link most directly proves what artifact was observed at runtime?

- **Unit / topic:** Release evidence and audit trails
- **Level:** L3
- **Question type:** MCQ
- **Objective tested:** report missing evidence as unknown or incomplete rather than inferred pass
- **Estimated time:** 3 minutes

**Question / scenario**

Which link most directly proves what artifact was observed at runtime?

A. PR title alone
B. A mutable tag in the release note
C. A verified observation of the running workload/runtime image identity correlated to the release and environment
D. A green dashboard screenshot only

Choose one best answer.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**C**. A verified observation of the running workload/runtime image identity correlated to the release and environment

**Reasoning**

- **A. Incorrect.** The option proposes “PR title alone”; Git records intent and review context but does not by itself prove what the cluster ran or that every required approval/promotion record exists.
- **B. Incorrect.** The option proposes “A mutable tag in the release note”; a mutable tag can point to different bytes over time and therefore does not prove the exact artifact that was tested or ran.
- **C. Correct.** Runtime observation needs collection time, scope, parser/runtime caveats, and correlation to the intended release.
- **D. Incorrect.** The option proposes “A green dashboard screenshot only”; it narrows the decision to one signal and omits the other required checks, such as ownership, runtime state, telemetry quality, or recovery safety.

Next, verify the relevant live status, policy, and telemetry rather than relying on an assumed default.

**Common wrong answers**

Choosing a distractor often confuses infer the deployed artifact from a tag or green status with verified state, or skips the required safety check: A tag can move and a controller status does not identify runtime bytes by itself.

**Operational caveat**

Runtime imageID formats, controller history retention, Kubernetes audit policy, and WORM/object-lock semantics vary. Verify the installed platform and preserve missing evidence as UNKNOWN/INCOMPLETE.

**Scoring rubric**

1 point for the best answer; 1 point for explaining why at least one tempting distractor is wrong; 1 point for naming the next verification step.

</details>

---

### U13-Q07 — Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Release evidence and audit

- **Unit / topic:** Release evidence and audit trails
- **Level:** L2
- **Question type:** output interpretation
- **Objective tested:** distinguish audit trail, release evidence, observability, provenance, and attestation
- **Estimated time:** 7 minutes

**Question / scenario**

Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Release evidence and audit trails:

```text
SIMULATED / REPRESENTATIVE
Manifest digest: sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
Runtime imageID: containerd://sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
Runtime format parser: unsupported
Observed replicas: 2/3
Conclusion: INCOMPLETE; do not silently claim MATCH or MISMATCH without runtime-specific verification.
```

State what is established, what remains unknown, the safest next diagnostic step, and whether you would promote, reconcile, pause, abort, or gather more evidence. Justify the decision using specific fields/lines above.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The declared manifest digest is A, but the runtime imageID string shows B and the parser is unsupported; only 2 of 3 replicas are observed. The correct status is INCOMPLETE, not a confident MATCH or MISMATCH. Collect all replicas, init containers and sidecars; verify runtime-specific imageID semantics and compare to the declared digest using a tested parser.

**Reasoning**

Output interpretation must separate observations from inference. A status or event can be stale, partial, or scoped to a single resource; the next check should target the earliest missing/failed link and preserve the current evidence.

**Common wrong answers**

- **Assume the best because one field is green.** That ignores contradictory fields and coverage gaps.
- **Mutate immediately.** Diagnose source, identity, scope, and rollback safety first unless containment urgency requires a minimal authorized action.

**Operational caveat**

All output is simulated; it is not claimed to come from a live cluster. Exact CLI output and controller status wording are `[VERIFY]` for the installed version.

**Scoring rubric**

Full credit: cite two specific fields, identify one unknown, choose a safe next action, and explain promotion/rollback constraints (4 points).

</details>

---

### U13-Q08 — Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Release evidence and audit

- **Unit / topic:** Release evidence and audit trails
- **Level:** L3
- **Question type:** output interpretation
- **Objective tested:** correlate source/build/artifact/config/controller/rollout/runtime records
- **Estimated time:** 8 minutes

**Question / scenario**

Read this complete `SIMULATED / REPRESENTATIVE` evidence excerpt for Release evidence and audit trails:

```text
SIMULATED / REPRESENTATIVE
release_id: orders-api-prod-2026-10-28.1
source_commit: cafe123
ci_run: build-981
image_digest: sha256:aaaa...
sbom_ref: sbom-981.json
controller_sync: missing
rollout_result: missing
post_deploy_check: PASS
Evidence coverage: incomplete chain
```

State what is established, what remains unknown, the safest next diagnostic step, and whether you would promote, reconcile, pause, abort, or gather more evidence. Justify the decision using specific fields/lines above.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The manifest links source commit, CI run, image digest and SBOM, but controller sync and rollout evidence are missing. A post-deploy check alone cannot establish the entire chain. Search durable event exports, Argo/Flux operation records, rollout analysis, Kubernetes audit logs and runtime observations; if the missing links cannot be recovered, state which claims remain incomplete and fix retention/export.

**Reasoning**

Output interpretation must separate observations from inference. A status or event can be stale, partial, or scoped to a single resource; the next check should target the earliest missing/failed link and preserve the current evidence.

**Common wrong answers**

- **Assume the best because one field is green.** That ignores contradictory fields and coverage gaps.
- **Mutate immediately.** Diagnose source, identity, scope, and rollback safety first unless containment urgency requires a minimal authorized action.

**Operational caveat**

All output is simulated; it is not claimed to come from a live cluster. Exact CLI output and controller status wording are `[VERIFY]` for the installed version.

**Scoring rubric**

Full credit: cite two specific fields, identify one unknown, choose a safe next action, and explain promotion/rollback constraints (4 points).

</details>

---

### U13-Q09 — Review this `INTENTIONALLY FLAWED` example for Release evidence and audit trails. Identify at l

- **Unit / topic:** Release evidence and audit trails
- **Level:** L3
- **Question type:** configuration/manifest review
- **Objective tested:** distinguish audit trail, release evidence, observability, provenance, and attestation
- **Estimated time:** 10 minutes

**Question / scenario**

Review this `INTENTIONALLY FLAWED` example for Release evidence and audit trails. Identify at least three distinct defects, explain their operational impact, and propose a corrected version or exact correction.

```json
{
  "release_id": "orders-api-prod-2026-10-28.1",
  "environment": "production",
  "image": "registry.example.invalid/orders-api:latest",
  "approved": true,
  "secret_token": "DO_NOT_USE_REAL_SECRET",
  "evidence": []
}
```

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The defects are:

1. A mutable `latest` tag is used instead of an artifact digest.
2. The `approved` boolean has no approver identity or source approval evidence reference.
3. The manifest embeds a secret-like field and has no linked evidence bundle.

**Corrected direction/snippet:**

```json
{
  "release_id": "orders-api-prod-2026-10-28.1",
  "service": "orders-api",
  "environment": "production",
  "source_commit": "REPLACE_WITH_FULL_COMMIT_SHA",
  "build_id": "REPLACE_WITH_CI_RUN_ID",
  "artifact_digest": "sha256:REPLACE_WITH_REAL_DIGEST",
  "approval_evidence_ref": "REPLACE_WITH_REVIEW_RECORD_URI",
  "controller_sync_evidence_ref": "REPLACE_WITH_DURABLE_EXPORT_URI",
  "rollout_outcome": "UNKNOWN",
  "post_deploy_verification": "INCOMPLETE",
  "evidence_bundle_ref": "REPLACE_WITH_BUNDLE_URI"
}
```

Never include secrets; define required/optional fields and provenance in local policy.

The correction is an instructional pattern; confirm product-specific schema and provider support before applying it.

**Reasoning**

The defects are not merely style issues: they can make resources fail to select, weaken access boundaries, make the artifact mutable, trigger unintended deletion, leak sensitive data, or convert missing evidence into an unsafe action. Corrections must be tested in a disposable environment.

**Common wrong answers**

- **Fix only syntax.** A valid manifest can still be insecure or semantically unsafe.
- **Assume an illustrative snippet is a complete deployable CRD.** Required fields and semantics depend on the installed API/version.

**Operational caveat**

The original is intentionally flawed and must not be applied. Corrected snippets may be bounded examples rather than complete production configuration; `[VERIFY]` any controller-specific fields.

**Scoring rubric**

Full credit: at least three distinct defects (3 points), impact for each (3), corrected snippet/direction (2), version/safety caveat (2).

</details>

---

### U13-Q10 — Review this `INTENTIONALLY FLAWED` example for Release evidence and audit trails. Identify at l

- **Unit / topic:** Release evidence and audit trails
- **Level:** L3
- **Question type:** configuration/manifest review
- **Objective tested:** correlate source/build/artifact/config/controller/rollout/runtime records
- **Estimated time:** 10 minutes

**Question / scenario**

Review this `INTENTIONALLY FLAWED` example for Release evidence and audit trails. Identify at least three distinct defects, explain their operational impact, and propose a corrected version or exact correction.

```text
# INTENTIONALLY FLAWED integrity plan
- Put bundle in a writable shared folder
- Save a SHA-256 next to each file
- Allow the same user to edit both evidence and checksums
- Call the folder immutable
- Delete old controller events after export without verifying the export
```

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

The defects are:

1. A writable folder is called immutable even though the same actor can edit evidence and checksums.
2. Adjacent hashes are not independently anchored or signed, so an attacker can rewrite both.
3. Old controller events are deleted without validating durable export completeness or redaction.

**Corrected direction/snippet:**

```text
# Safer evidence integrity plan
- Hash each artifact and create a manifest/index linking release ID and digest.
- Restrict writer and reader roles; separate approval/promotion duties where policy requires.
- Export events before expiry and validate count, IDs, timestamps, and redaction.
- Use retention/object-lock/WORM controls only after verifying mode, administrative bypass, and recovery implications.
- Anchor bundle hash/signature in an independently protected system; a writable folder is not immutable.
```

The correction is an instructional pattern; confirm product-specific schema and provider support before applying it.

**Reasoning**

The defects are not merely style issues: they can make resources fail to select, weaken access boundaries, make the artifact mutable, trigger unintended deletion, leak sensitive data, or convert missing evidence into an unsafe action. Corrections must be tested in a disposable environment.

**Common wrong answers**

- **Fix only syntax.** A valid manifest can still be insecure or semantically unsafe.
- **Assume an illustrative snippet is a complete deployable CRD.** Required fields and semantics depend on the installed API/version.

**Operational caveat**

The original is intentionally flawed and must not be applied. Corrected snippets may be bounded examples rather than complete production configuration; `[VERIFY]` any controller-specific fields.

**Scoring rubric**

Full credit: at least three distinct defects (3 points), impact for each (3), corrected snippet/direction (2), version/safety caveat (2).

</details>

---

### U13-Q11 — Incident: CI has an SBOM and signature for image A, but the production Deployment references a 

- **Unit / topic:** Release evidence and audit trails
- **Level:** L4
- **Question type:** incident/troubleshooting
- **Objective tested:** report missing evidence as unknown or incomplete rather than inferred pass
- **Estimated time:** 15 minutes

**Question / scenario**

Incident: CI has an SBOM and signature for image A, but the production Deployment references a mutable tag that now resolves to image B.

Provide symptom → diagnosis → evidence to preserve → blast-radius and rollback-safety check → containment/recovery → prevention. Identify one residual uncertainty that must not be presented as fact.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**Symptom:** CI has an SBOM and signature for image A, but the production Deployment references a mutable tag that now resolves to image B.

**Diagnosis:** A digest identifies artifact content; a signature/attestation makes claims only under a sound trust policy. A local hash proves byte equality relative to the hash, not who created the bytes.

**Evidence:** collect the relevant Git revision/PR, controller conditions/events, live resource state, runtime/metric samples, timestamps, and actor/approval data as applicable.

**Blast radius and rollback:** identify affected environments/replicas/consumers, determine whether state/data/external side effects changed, and test whether the prior version can safely read current state. Do not assume an image rollback reverses data.

**Containment/recovery:** use the smallest authorized reversible action; pause promotion or isolate the affected path if warranted; preserve a before/after record; reconcile the intended fix into the declared source; verify customer-facing behavior.

**Prevention:** Evidence supports specific claims, not blanket compliance. Missing, stale, or unlinked evidence must remain UNKNOWN/INCOMPLETE until independently verified.

**Residual uncertainty:** any missing history, unknown consumer behavior, unparseable runtime identity, or absent metric sample remains UNKNOWN until corroborated.

**Reasoning**

The incident response separates preserving evidence from containment, makes recovery contingent on state compatibility, and verifies both control-plane convergence and application-level outcome.

**Common wrong answers**

- **Immediately force-sync/redeploy without preserving evidence.** This can erase the live state that explains the incident.
- **Assume rollback is safe because the previous artifact exists.** Data, schema, event, or external side effects may be incompatible.

**Operational caveat**

Escalate to the incident commander/security owner when compromise or regulated data is plausible. Use only approved break-glass authority and an explicit reconciliation/review path.

**Scoring rubric**

10 points: diagnosis 2; evidence 2; blast radius/rollback 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### U13-Q12 — Design a durable release-evidence pipeline

- **Unit / topic:** — Release evidence and audit trails
- **Level:** — L4
- **Question type:** — design
- **Objective tested:** — design a safe, auditable workflow for release evidence and audit trails
- **Estimated time:** — 20 minutes

**Question / scenario**

Design a durable release-evidence pipeline that links source, approval, build, artifact, GitOps promotion, rollout, runtime observation, and post-deploy verification.

**Deliverables expected:** a component/workflow diagram, ownership and evidence table, failure modes, rollback/recovery path, and a short decision record. State assumptions and include at least two viable alternatives.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Define required evidence per stage and stable correlation keys (release ID, source commit, build ID, artifact digest, config commit, environment, timestamps). Assemble a manifest and indexed bundle; hash files and verify them; export transient controller/audit events; restrict access and redact secrets; retain evidence under an owned policy. Use signatures/attestations and independently protected anchors where stronger integrity is required, and report missing data as UNKNOWN/INCOMPLETE.

**Reasoning**

A release bundle is useful only if claims are linked to sources and the trust model is explicit. Hashes establish byte equality, signatures depend on key trust, and local files are not immutable.

**Common wrong answers**

- **Infer the deployed artifact from a tag or green status** — A tag can move and a controller status does not identify runtime bytes by itself.
- **Treat a detached SBOM/signature as proof of the live image** — Evidence must link the SBOM/attestation subject to the observed runtime digest.

**Operational caveat**

Version-specific controller verification, WORM/object-lock semantics, and runtime imageID parsing require authoritative verification. This is evidence engineering, not a compliance certification.

**Scoring rubric**

10 points: safety/correctness 2; evidence and verification 2; alternatives and trade-offs 2; failure/recovery plan 2; ownership, clarity, and unresolved uncertainty 2.

</details>

---

### Unit 13 lab-to-question coverage map

The seven hands-on labs from Unit 13 are represented as assessment targets; this bank does not claim the learner executed them.

| Unit 13 lab | Assessment questions | What a strong answer demonstrates |
|---|---|---|
| 1. Release manifest and evidence bundle | U13-Q09, U13-Q10, XINT-22, XINT-23, XINT-34 | Required fields, digest linkage, evidence completeness, checksums, and honest UNKNOWN/INCOMPLETE handling. |
| 2. Tamper-evidence demonstration | U13-Q09, U13-Q10, XINT-41 | Hash/signature distinction, modified-record detection, and independently protected chain-head anchoring. |
| 3. Runtime image versus Git desired state | U13-Q07, XINT-21, XINT-44 | All replicas/containers, runtime-format caveats, and MATCH/MISMATCH/UNKNOWN/INCOMPLETE outcomes. |
| 4. Controller-event JSONL export | U13-Q08, XINT-22, XINT-42 | Correlation fields, durable export, duplicate/out-of-order handling, timestamps, redaction, and retention. |
| 5. Segregation-of-duties check | XINT-24, XINT-35 | Author/reviewer/approver/promoter separation and distinction between simulated policy and provider-enforced rules. |
| 6. Audit query against the evidence store | U13-Q08, XINT-22, XINT-23, XINT-35 | Answering who deployed/approved, tests/scans, environments, and time interval without inferring missing facts. |
| 7. Incident timeline builder | U13-Q08, XINT-01, XINT-22, XINT-25, XINT-42 | Stable event IDs, explicit time zones, deduplication, causal uncertainty, rollback and post-incident verification. |


# Cross-unit integration scenarios (45 questions)

Each scenario requires reasoning across multiple units. Treat all output as simulated. Use the same disciplined sequence: preserve relevant evidence, establish identity/scope, assess customer/data blast radius, determine compatibility and recovery options, apply a minimal authorized fix, verify outcome, and prevent recurrence.

### XINT-01 — **Scenario:** A GitOps controller silently reverts an emergency hotfix.

- **Unit / topic:** Cross-unit integration: Units 1, 6, 13
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 1, 6, 13.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** A GitOps controller silently reverts an emergency hotfix.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 1, 6, 13.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Capture live diff, actor/time, events and incident ID before overwriting. Decide whether the hotfix is valid, then reconcile it through an emergency reviewed Git change; verify runtime/business health and close the exception with an owner/expiry.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Desired state, observed live state, and reconciliation outcome are separate facts. Compare the declared revision and policy with live resources, then verify the service outcome; no single controller status proves the whole system correct. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Do not disable reconciliation indefinitely or reapply the patch without recording it. Residual uncertainty remains if the original runtime state was not captured.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-02 — **Scenario:** A production promotion references a mutable image tag rather than a digest.

- **Unit / topic:** Cross-unit integration: Units 4, 7, 12, 13
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 4, 7, 12, 13.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** A production promotion references a mutable image tag rather than a digest.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 4, 7, 12, 13.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Resolve the exact artifact digest from trusted build/registry evidence, compare it to staging-tested digest, then update the production configuration through review. If the tag moved and no digest mapping survives, report artifact identity as UNKNOWN.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Promotion must preserve artifact identity while changing environment-specific intent through a reviewable path. The source commit, build, digest, config commit, approvals, and runtime observation prove different parts of the release. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

A tag string and source commit do not prove deployed bytes. Roll back only after confirming state compatibility.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-03 — **Scenario:** A canary has one of three replicas but no measured traffic split.

- **Unit / topic:** Cross-unit integration: Units 7, 8, 9
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 7, 8, 9.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** A canary has one of three replicas but no measured traffic split.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 7, 8, 9.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Inspect service selectors, route weights, provider status and request counts. Treat replica fraction as workload topology, not traffic percentage; configure and measure a supported traffic split before interpreting canary health.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Replica count and traffic exposure are different measurements. Release decisions must use measured exposure and health over an adequate window, and rollback requires compatibility checks for data and side effects. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Do not promote on a handful of requests or assume 1/3 replicas means 33% traffic.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-04 — **Scenario:** A low-traffic canary has too few samples for a reliable decision.

- **Unit / topic:** Cross-unit integration: Units 7, 8, 9
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 7, 8, 9.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** A low-traffic canary has too few samples for a reliable decision.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 7, 8, 9.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Use a minimum-sample and observation-window policy. Keep the result inconclusive, extend the window, use safe synthetic/load validation if appropriate, or require a human decision with documented uncertainty.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Replica count and traffic exposure are different measurements. Release decisions must use measured exposure and health over an adequate window, and rollback requires compatibility checks for data and side effects. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Do not lower thresholds after seeing results or treat zero observed failures as proof of safety.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-05 — **Scenario:** Analysis returns empty/gappy metrics; policy must not silently pass.

- **Unit / topic:** Cross-unit integration: Units 8, 9, 13
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 8, 9, 13.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** Analysis returns empty/gappy metrics; policy must not silently pass.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 8, 9, 13.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Check query syntax/labels, scrape health, timestamps, traffic volume, and provider errors. Return UNKNOWN/INCONCLUSIVE or pause/abort per policy; repair the data source and rerun with a defined window.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

A rollout controller's step/status is not the same as traffic routing or valid analysis. Verify provider configuration, stable/canary exposure, measurement freshness, sample size, and installed CRD behavior. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Empty vectors can indicate a broken query or telemetry gap, not zero errors.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-06 — **Scenario:** A schema migration adds a required column while old consumers still run.

- **Unit / topic:** Cross-unit integration: Units 7, 11, 12
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 7, 11, 12.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** A schema migration adds a required column while old consumers still run.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 7, 11, 12.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Pause contract/removal phase. Use an additive nullable/defaulted expand step, deploy compatible readers/writers, backfill and validate, then enforce requiredness only after old consumers are retired.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Replica count and traffic exposure are different measurements. Release decisions must use measured exposure and health over an adequate window, and rollback requires compatibility checks for data and side effects. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Do not assume old consumers tolerate the new schema; validate actual clients and database engine behavior.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-07 — **Scenario:** Rollback is requested after a destructive or non-backward-compatible migration.

- **Unit / topic:** Cross-unit integration: Units 7, 11, 12
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 7, 11, 12.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** Rollback is requested after a destructive or non-backward-compatible migration.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 7, 11, 12.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Freeze further rollout, assess backups/PITR, migration logs, write compatibility and RPO/RTO. Prefer a tested roll-forward if old code cannot read current state; restore only under approved recovery plan.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Replica count and traffic exposure are different measurements. Release decisions must use measured exposure and health over an adequate window, and rollback requires compatibility checks for data and side effects. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Reinstalling old code does not reverse dropped data or incompatible writes.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-08 — **Scenario:** A new event field breaks a consumer because of semantic rather than syntactic cha

- **Unit / topic:** Cross-unit integration: Units 9, 11, 12
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 9, 11, 12.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** A new event field breaks a consumer because of semantic rather than syntactic change.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 9, 11, 12.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Replay representative events against all consumers; compare semantics, units, defaults, enum values and null handling. Version or dual-write where necessary and promote only after consumer contracts pass.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

A health gate must validate the measurement before evaluating its value. Empty, stale, gappy, mislabelled, or low-volume telemetry is inconclusive unless an explicit, tested policy says otherwise. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

A schema registry structural pass does not prove semantic compatibility.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-09 — **Scenario:** A feature flag is disabled but the deployment is incompatible with the old databa

- **Unit / topic:** Cross-unit integration: Units 10, 11, 12
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 10, 11, 12.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** A feature flag is disabled but the deployment is incompatible with the old database schema.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 10, 11, 12.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Treat flag exposure and binary compatibility separately. Check startup/read paths, migrations and writes; restore compatibility via a safe forward fix or approved state recovery.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

A feature flag controls exposure, not the compatibility of deployed code, schemas, external side effects, or flag-service failure behavior. Design ownership, safe defaults, telemetry, expiry, and recovery as part of the release. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Flag-off does not undo schema/data changes or guarantee old code can run.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-10 — **Scenario:** A flag service is unavailable during a release.

- **Unit / topic:** Cross-unit integration: Units 7, 9, 10
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 7, 9, 10.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** A flag service is unavailable during a release.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 7, 9, 10.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Check the designed local/default behavior, evaluation errors, targeting privacy, and business impact. Pause exposure or choose a documented safe default; test provider recovery and flag-state consistency.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Replica count and traffic exposure are different measurements. Release decisions must use measured exposure and health over an adequate window, and rollback requires compatibility checks for data and side effects. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Do not assume every SDK fails closed/open the same way; verify the chosen SDK and configuration.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-11 — **Scenario:** An Argo CD application is OutOfSync after a manual change; decide whether to reco

- **Unit / topic:** Cross-unit integration: Units 2, 6, 13
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 2, 6, 13.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** An Argo CD application is OutOfSync after a manual change; decide whether to reconcile or preserve evidence first.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 2, 6, 13.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Inspect change actor, diff, timestamp, events, incident context and resource ownership. If unexpected or incident-related, preserve evidence first; then reconcile or incorporate the authorized fix into Git.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Argo CD sync status describes desired/live comparison, while health, project boundaries, operation history, and application telemetry describe different aspects. Diagnose the specific resource and policy before retrying or changing sync behavior. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

OutOfSync alone does not tell whether the live change is malicious, intentional, or a benign mutation.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-12 — **Scenario:** Flux source revision and deployed revision disagree.

- **Unit / topic:** Cross-unit integration: Units 3, 4, 6, 13
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 3, 4, 6, 13.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** Flux source revision and deployed revision disagree.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 3, 4, 6, 13.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Inspect source artifact revision, Kustomization/HelmRelease conditions, last-applied revision, paths and reconciliation errors. Determine whether a stale artifact or wrong target explains the gap; fix source/auth/path and verify convergence.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Flux source acquisition, Kustomize/Helm reconciliation, controller conditions, Kubernetes runtime health, and notifications are distinct links. Correlate source revision through applied resources and retain transient events if they matter for later review. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Do not assume source-controller readiness means downstream resources have reconciled.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-13 — **Scenario:** Secret rotation occurs during a progressive rollout.

- **Unit / topic:** Cross-unit integration: Units 5, 7, 8, 10
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 5, 7, 8, 10.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** Secret rotation occurs during a progressive rollout.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 5, 7, 8, 10.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Verify new credential distribution, replica reload semantics, provider versions and auth success before revoking old credential, subject to threat policy. Monitor both stable/canary and keep a bounded overlap only if approved.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Secret management is a lifecycle control: storage, read/decrypt permissions, delivery, rotation, revocation, logging, history, and backup copies all matter. A manifest change alone cannot establish that an exposed credential is no longer usable. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Do not put values in Git or assume restart behavior; assess leaked-credential risk before overlap.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-14 — **Scenario:** A GitOps repository is unavailable during an incident.

- **Unit / topic:** Cross-unit integration: Units 1, 4, 6, 13
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 1, 4, 6, 13.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** A GitOps repository is unavailable during an incident.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 1, 4, 6, 13.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Protect running workloads, use the documented break-glass path only if necessary, preserve exact live state and actor/time, restore repository access, then reconcile every out-of-band change into reviewed Git.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Desired state, observed live state, and reconciliation outcome are separate facts. Compare the declared revision and policy with live resources, then verify the service outcome; no single controller status proves the whole system correct. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Controller outage generally blocks new reconciliation but does not automatically stop already-running workloads; confirm actual failure scope.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-15 — **Scenario:** A controller is healthy but the application fails business-level checks.

- **Unit / topic:** Cross-unit integration: Units 2, 7, 9, 10
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 2, 7, 9, 10.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** A controller is healthy but the application fails business-level checks.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 2, 7, 9, 10.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Separate sync/health from service SLIs and business metrics. Pause rollout or disable exposure per policy; inspect dependencies, logs, and versioned contract behavior.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Argo CD sync status describes desired/live comparison, while health, project boundaries, operation history, and application telemetry describe different aspects. Diagnose the specific resource and policy before retrying or changing sync behavior. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Do not equate controller readiness with correct transactions or model outputs.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-16 — **Scenario:** A rollout aborts, but the previous version cannot read newly written data.

- **Unit / topic:** Cross-unit integration: Units 7, 8, 11, 12
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 7, 8, 11, 12.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** A rollout aborts, but the previous version cannot read newly written data.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 7, 8, 11, 12.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Do not blindly restore the old binary. Stop further incompatible writes, assess data transformations and compatibility, then choose a tested roll-forward or restore plan with explicit RPO/RTO.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Replica count and traffic exposure are different measurements. Release decisions must use measured exposure and health over an adequate window, and rollback requires compatibility checks for data and side effects. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

The rollout controller can switch traffic but cannot reverse incompatible data writes by itself.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-17 — **Scenario:** A database backfill is retried and duplicates data because it is not idempotent.

- **Unit / topic:** Cross-unit integration: Units 6, 11, 12
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 6, 11, 12.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** A database backfill is retried and duplicates data because it is not idempotent.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 6, 11, 12.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Stop or rate-limit the job, quantify duplicate impact, preserve checkpoint/log evidence, repair with a validated deduplication plan, and make batches idempotent with checkpoints/unique keys.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

A live diff is a signal to classify, not an automatic instruction to overwrite. Correlate Git, audit identity/time, admission/defaulting, field ownership, and incident context before choosing reconcile, accept, or escalate. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Do not rerun blindly or delete suspected duplicates without backup and ownership approval.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-18 — **Scenario:** A side-by-side pipeline produces different aggregates; design validation before s

- **Unit / topic:** Cross-unit integration: Units 4, 9, 11, 12
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 4, 9, 11, 12.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** A side-by-side pipeline produces different aggregates; design validation before switch-over.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 4, 9, 11, 12.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Keep old output authoritative while comparing deterministic samples, row counts, key coverage, nulls, distribution, lineage and business tolerances. Investigate differences and only switch after sign-off.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Promotion must preserve artifact identity while changing environment-specific intent through a reviewable path. The source commit, build, digest, config commit, approvals, and runtime observation prove different parts of the release. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

A successful job status proves execution, not equivalence or data correctness.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-19 — **Scenario:** An API deprecation date arrives but a long-lived partner client is still active.

- **Unit / topic:** Cross-unit integration: Units 4, 9, 12, 13
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 4, 9, 12, 13.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** An API deprecation date arrives but a long-lived partner client is still active.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 4, 9, 12, 13.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Use access telemetry and partner inventory to identify usage; follow documented exception/escalation policy, contact owner, and delay removal if risk requires. Record extension and expiry.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Promotion must preserve artifact identity while changing environment-specific intent through a reviewable path. The source commit, build, digest, config commit, approvals, and runtime observation prove different parts of the release. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

A calendar date does not prove consumers migrated; do not remove silently without usage evidence and contract policy.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-20 — **Scenario:** A feature flag has no owner or expiry and creates release ambiguity.

- **Unit / topic:** Cross-unit integration: Units 4, 10, 13
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 4, 10, 13.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** A feature flag has no owner or expiry and creates release ambiguity.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 4, 10, 13.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Inventory the flag, identify dependencies and targeting, assign a named team owner, set expiry/removal criteria, add exposure telemetry, then remove through a reviewed change after safe verification.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Promotion must preserve artifact identity while changing environment-specific intent through a reviewable path. The source commit, build, digest, config commit, approvals, and runtime observation prove different parts of the release. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Do not delete a flag blindly if it gates a kill switch or safety-critical behavior.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-21 — **Scenario:** Desired image digest differs from runtime imageID.

- **Unit / topic:** Cross-unit integration: Units 2, 6, 7, 13
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 2, 6, 7, 13.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** Desired image digest differs from runtime imageID.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 2, 6, 7, 13.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Collect all pod/container/init-container identities and rollout overlap; inspect pod spec, ReplicaSets, node runtime format, pull events and rollout state. Report MISMATCH only when identities can be reliably compared; otherwise UNKNOWN/INCOMPLETE.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Argo CD sync status describes desired/live comparison, while health, project boundaries, operation history, and application telemetry describe different aspects. Diagnose the specific resource and policy before retrying or changing sync behavior. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Do not parse every runtime imageID with one universal regex or ignore sidecars/old replicas.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-22 — **Scenario:** Controller history expired and the release evidence bundle is incomplete.

- **Unit / topic:** Cross-unit integration: Units 2, 3, 8, 13
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 2, 3, 8, 13.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** Controller history expired and the release evidence bundle is incomplete.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 2, 3, 8, 13.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Query CI, Git PR, registry, audit logs, durable event exports, rollout records and runtime snapshots using release ID/digest/time. Mark unsupported claims incomplete and repair retention/export controls.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Argo CD sync status describes desired/live comparison, while health, project boundaries, operation history, and application telemetry describe different aspects. Diagnose the specific resource and policy before retrying or changing sync behavior. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Do not reconstruct approval or exact runtime identity from memory or a mutable tag.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-23 — **Scenario:** CI signature/SBOM exists but cannot be linked to the live digest.

- **Unit / topic:** Cross-unit integration: Units 4, 12, 13
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 4, 12, 13.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** CI signature/SBOM exists but cannot be linked to the live digest.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 4, 12, 13.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Verify signature/attestation subject digest, SBOM subject and build provenance, then compare to the actual runtime artifact identity. If linkage is missing, treat supply-chain claim as unproven and investigate.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Promotion must preserve artifact identity while changing environment-specific intent through a reviewable path. The source commit, build, digest, config commit, approvals, and runtime observation prove different parts of the release. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

An SBOM for a similar version or source commit is not evidence for different bytes.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-24 — **Scenario:** An approver authored the change and the same identity performed promotion.

- **Unit / topic:** Cross-unit integration: Units 2, 4, 13
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 2, 4, 13.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** An approver authored the change and the same identity performed promotion.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 2, 4, 13.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Check the actual branch rules, required owner review, approval records and promotion actor. Apply policy-defined separation of duties; use an independent reviewer/promoter for high-risk changes and report exceptions.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Argo CD sync status describes desired/live comparison, while health, project boundaries, operation history, and application telemetry describe different aspects. Diagnose the specific resource and policy before retrying or changing sync behavior. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

A simulated policy file does not prove provider enforcement; verify actual configuration and audit logs.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-25 — **Scenario:** A force-push removed expected Git review history.

- **Unit / topic:** Cross-unit integration: Units 1, 4, 13
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 1, 4, 13.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** A force-push removed expected Git review history.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 1, 4, 13.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Preserve reflogs/remote audit logs/PR records where available, compare signed tags and protected-branch events, and determine what can be independently corroborated. Restore protection and restrict force-push.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Desired state, observed live state, and reconciliation outcome are separate facts. Compare the declared revision and policy with live resources, then verify the service outcome; no single controller status proves the whole system correct. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Do not claim a complete audit trail if independent records are absent.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-26 — **Scenario:** A break-glass cluster write was never reconciled into Git.

- **Unit / topic:** Cross-unit integration: Units 1, 6, 13
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 1, 6, 13.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** A break-glass cluster write was never reconciled into Git.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 1, 6, 13.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Capture live state and identity, classify ongoing impact, open emergency change with owner/expiry, reconcile approved state to Git and verify the controller no longer fights it.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Desired state, observed live state, and reconciliation outcome are separate facts. Compare the declared revision and policy with live resources, then verify the service outcome; no single controller status proves the whole system correct. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Do not leave a permanent ignore rule or treat the manual state as the new source without review.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-27 — **Scenario:** A migration Job ran before application compatibility was established.

- **Unit / topic:** Cross-unit integration: Units 2, 7, 11
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 2, 7, 11.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** A migration Job ran before application compatibility was established.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 2, 7, 11.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Inspect migration ID, logs, database schema/data and app versions; stop later stages, assess whether old readers still work, and use a tested recovery/forward-fix plan. Add explicit dependency/readiness gates and idempotent migration semantics.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Argo CD sync status describes desired/live comparison, while health, project boundaries, operation history, and application telemetry describe different aspects. Diagnose the specific resource and policy before retrying or changing sync behavior. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Sync waves/hooks or Job ordering do not make a migration transactional or backward-compatible.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-28 — **Scenario:** A canary appears healthy on CPU but violates business metrics.

- **Unit / topic:** Cross-unit integration: Units 7, 8, 9
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 7, 8, 9.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** A canary appears healthy on CPU but violates business metrics.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 7, 8, 9.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Pause/abort according to the business SLI gate; verify metric labels, sample count and data freshness, then inspect logs/traces and compare cohorts.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Replica count and traffic exposure are different measurements. Release decisions must use measured exposure and health over an adequate window, and rollback requires compatibility checks for data and side effects. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Low CPU is not a substitute for successful checkout, prediction quality, or data correctness.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-29 — **Scenario:** A blue-green switch is requested while session/state compatibility is unknown.

- **Unit / topic:** Cross-unit integration: Units 7, 10, 11, 12
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 7, 10, 11, 12.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** A blue-green switch is requested while session/state compatibility is unknown.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 7, 10, 11, 12.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Do not switch until session affinity/state ownership, shared schema, cache formats, and side effects are understood. Test old/new coexistence, drain behavior, and rollback; otherwise use a safer staged migration.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Replica count and traffic exposure are different measurements. Release decisions must use measured exposure and health over an adequate window, and rollback requires compatibility checks for data and side effects. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Blue-green reduces traffic-switch complexity but does not isolate shared state automatically.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-30 — **Scenario:** A release-health query uses the wrong label or unit and gives a false green.

- **Unit / topic:** Cross-unit integration: Units 8, 9, 13
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 8, 9, 13.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** A release-health query uses the wrong label or unit and gives a false green.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 8, 9, 13.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Validate metric semantics, labels, units, query window, expected traffic and sample counts against raw telemetry. Add query tests and known-good/bad fixtures; classify empty or impossible values as incomplete.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

A rollout controller's step/status is not the same as traffic routing or valid analysis. Verify provider configuration, stable/canary exposure, measurement freshness, sample size, and installed CRD behavior. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

A syntactically valid query may still measure the wrong population or unit.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-31 — **Scenario:** A rollout analysis is based on stale telemetry.

- **Unit / topic:** Cross-unit integration: Units 8, 9
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 8, 9.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** A rollout analysis is based on stale telemetry.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 8, 9.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Check event/sample timestamps, scrape delays, query range, provider health and data lag. Pause the decision until fresh samples arrive or follow a documented fail-safe policy.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

A rollout controller's step/status is not the same as traffic routing or valid analysis. Verify provider configuration, stable/canary exposure, measurement freshness, sample size, and installed CRD behavior. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

A successful query response does not guarantee the data is current.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-32 — **Scenario:** Drift is caused by admission mutation/defaulting rather than an unauthorized huma

- **Unit / topic:** Cross-unit integration: Units 1, 6, 13
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 1, 6, 13.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** Drift is caused by admission mutation/defaulting rather than an unauthorized human edit.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 1, 6, 13.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Compare audit actor, admission configuration, managed fields/ownership and pre/post admission object when available. Classify expected mutation and narrowly document ignore/ownership policy.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Desired state, observed live state, and reconciliation outcome are separate facts. Compare the declared revision and policy with live resources, then verify the service outcome; no single controller status proves the whole system correct. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Do not globally ignore diffs or assume every live-only field is harmless.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-33 — **Scenario:** A GitOps controller loses credentials or repository access during recovery.

- **Unit / topic:** Cross-unit integration: Units 1, 3, 5, 13
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 1, 3, 5, 13.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** A GitOps controller loses credentials or repository access during recovery.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 1, 3, 5, 13.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Check source authentication status, secret reference, rotation and least privilege; restore access through approved secret delivery, then verify fetched revision and downstream reconciliation.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Desired state, observed live state, and reconciliation outcome are separate facts. Compare the declared revision and policy with live resources, then verify the service outcome; no single controller status proves the whole system correct. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Do not paste tokens into logs or broaden to admin credentials as a shortcut.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-34 — **Scenario:** Post-deploy verification is missing despite successful sync.

- **Unit / topic:** Cross-unit integration: Units 2, 7, 9, 13
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 2, 7, 9, 13.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** Post-deploy verification is missing despite successful sync.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 2, 7, 9, 13.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Keep the release state as incomplete until runtime and business checks are captured. Run health/readiness, smoke, SLI and artifact identity checks; link outputs to release ID.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Argo CD sync status describes desired/live comparison, while health, project boundaries, operation history, and application telemetry describe different aspects. Diagnose the specific resource and policy before retrying or changing sync behavior. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

A successful sync proves a control-plane operation, not the complete post-deploy outcome.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-35 — **Scenario:** An audit query cannot determine who approved a production release.

- **Unit / topic:** Cross-unit integration: Units 2, 4, 13
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 2, 4, 13.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** An audit query cannot determine who approved a production release.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 2, 4, 13.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Search PR approvals, branch protection/audit logs, ticket records and identity provider events using the commit/release ID. If unavailable, report approver UNKNOWN and repair durable approval evidence.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Argo CD sync status describes desired/live comparison, while health, project boundaries, operation history, and application telemetry describe different aspects. Diagnose the specific resource and policy before retrying or changing sync behavior. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Do not infer approval from the author, commit signature, or current branch rules alone.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-36 — **Scenario:** A data/model release has no model version or training-data snapshot hash.

- **Unit / topic:** Cross-unit integration: Units 9, 11, 12, 13
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 9, 11, 12, 13.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** A data/model release has no model version or training-data snapshot hash.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 9, 11, 12, 13.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Freeze promotion until artifact identity, model version, training-data snapshot/hash, preprocessing/feature contract and evaluation metrics are linked. Preserve reproducibility metadata and owner approval.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

A health gate must validate the measurement before evaluating its value. Empty, stale, gappy, mislabelled, or low-volume telemetry is inconclusive unless an explicit, tested policy says otherwise. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

A container digest alone may not identify model weights/data embedded or fetched at runtime.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-37 — **Scenario:** A new version writes data the old version cannot read (N-1 compatibility).

- **Unit / topic:** Cross-unit integration: Units 7, 11, 12
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 7, 11, 12.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** A new version writes data the old version cannot read (N-1 compatibility).

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 7, 11, 12.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Stop incompatible writes or traffic growth; determine whether old consumers can be made tolerant, and prefer a safe forward fix if rollback is incompatible. Add producer/consumer contract tests and staged expand–migrate–contract.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Replica count and traffic exposure are different measurements. Release decisions must use measured exposure and health over an adequate window, and rollback requires compatibility checks for data and side effects. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

A rollout abort does not restore data to an old-compatible form.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-38 — **Scenario:** An emergency release has an exception but no expiry or owner.

- **Unit / topic:** Cross-unit integration: Units 1, 4, 6, 13
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 1, 4, 6, 13.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** An emergency release has an exception but no expiry or owner.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 1, 4, 6, 13.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Assign accountable owner, reason, scope, expiry and post-hoc review deadline; track the exception in a durable system and automatically alert on expiry.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Desired state, observed live state, and reconciliation outcome are separate facts. Compare the declared revision and policy with live resources, then verify the service outcome; no single controller status proves the whole system correct. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

An unbounded exception becomes permanent undocumented policy.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-39 — **Scenario:** A production rollback restores code but not a compatible feature-flag state.

- **Unit / topic:** Cross-unit integration: Units 7, 10, 11, 12
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 7, 10, 11, 12.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** A production rollback restores code but not a compatible feature-flag state.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 7, 10, 11, 12.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Correlate code version, flag state, schema and writes. Restore a compatible flag configuration through the approved flag control path, verify behavior and preserve timeline.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Replica count and traffic exposure are different measurements. Release decisions must use measured exposure and health over an adequate window, and rollback requires compatibility checks for data and side effects. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Code rollback and flag rollback are separate operations; neither reverses data automatically.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-40 — **Scenario:** A release bundle contains secrets or sensitive request payloads.

- **Unit / topic:** Cross-unit integration: Units 5, 13
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 5, 13.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** A release bundle contains secrets or sensitive request payloads.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 5, 13.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Restrict access, stop further propagation, rotate exposed credentials if applicable, purge/retain copies according to incident/legal policy, and rebuild a redacted evidence bundle with provenance.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Secret management is a lifecycle control: storage, read/decrypt permissions, delivery, rotation, revocation, logging, history, and backup copies all matter. A manifest change alone cannot establish that an exposed credential is no longer usable. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Do not blindly delete evidence if preservation obligations apply; involve security/privacy owners.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-41 — **Scenario:** A local evidence store is described as immutable despite being freely editable.

- **Unit / topic:** Cross-unit integration: Units 1, 13
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 1, 13.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** A local evidence store is described as immutable despite being freely editable.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 1, 13.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Correct the claim: local hashes detect changes only relative to trusted hash values. Use restricted access, independent anchor/signature and approved WORM/object-lock retention if needed; test administrative bypass.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Desired state, observed live state, and reconciliation outcome are separate facts. Compare the declared revision and policy with live resources, then verify the service outcome; no single controller status proves the whole system correct. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

A directory and adjacent checksum file are not immutable if the same actor can rewrite both.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-42 — **Scenario:** A controller event exporter receives duplicate or out-of-order events.

- **Unit / topic:** Cross-unit integration: Units 3, 8, 13
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 3, 8, 13.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** A controller event exporter receives duplicate or out-of-order events.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 3, 8, 13.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Assign stable event IDs, deduplicate idempotently, preserve original timestamps plus ingestion time, and build timelines using event time with uncertainty notes. Monitor dropped/duplicate counts.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Flux source acquisition, Kustomize/Helm reconciliation, controller conditions, Kubernetes runtime health, and notifications are distinct links. Correlate source revision through applied resources and retain transient events if they matter for later review. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Arrival order does not prove causal order; timestamps may be skewed.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-43 — **Scenario:** CI artifact retention deletes evidence before the investigation window.

- **Unit / topic:** Cross-unit integration: Units 4, 12, 13
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 4, 12, 13.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** CI artifact retention deletes evidence before the investigation window.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 4, 12, 13.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Set retention by risk and required investigation/recovery window; archive compact metadata longer than bulky artifacts where policy permits, verify retrieval and ownership, and alert before expiry.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Promotion must preserve artifact identity while changing environment-specific intent through a reviewable path. The source commit, build, digest, config commit, approvals, and runtime observation prove different parts of the release. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Retention cannot be fixed retroactively if the artifact is already gone; report gaps.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-44 — **Scenario:** An application is Healthy but has not been proven to run the expected artifact.

- **Unit / topic:** Cross-unit integration: Units 2, 7, 9, 13
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 2, 7, 9, 13.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** An application is Healthy but has not been proven to run the expected artifact.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 2, 7, 9, 13.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

Inspect live pod template, ReplicaSets, runtime image IDs, init containers and rollout overlap; correlate digest to CI and release bundle. Keep identity UNKNOWN if runtime format cannot be verified.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Argo CD sync status describes desired/live comparison, while health, project boundaries, operation history, and application telemetry describe different aspects. Diagnose the specific resource and policy before retrying or changing sync behavior. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Health status and artifact identity are separate evidence dimensions.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

### XINT-45 — **Scenario:** Choose mandatory evidence for a small local project versus a high-risk production

- **Unit / topic:** Cross-unit integration: Units 1, 4, 9, 13
- **Level:** L3/L4
- **Question type:** integration
- **Objective tested:** Integrate the controls and failure modes from Units 1, 4, 9, 13.
- **Estimated time:** 15 minutes

**Question / scenario**

**Scenario:** Choose mandatory evidence for a small local project versus a high-risk production service.

Provide diagnosis, the evidence to collect, immediate containment, blast-radius and rollback-safety analysis, prevention, and the remaining uncertainty.

**Multi-unit mapping:** Units 1, 4, 9, 13.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

For a local project, require source commit, reproducible test result, artifact digest, configuration revision, basic runtime check and cleanup. For high-risk production add independent approval, signed provenance, SBOM/scans, durable controller/audit exports, SoD, retention, access review and recovery evidence.

**Containment and verification:** pause the affected promotion/operation when safe, preserve current evidence, assess affected users/data/replicas/consumers, and choose rollback only after compatibility is established. Verify both the control-plane state and the customer/business outcome after recovery.

**Reasoning**

Desired state, observed live state, and reconciliation outcome are separate facts. Compare the declared revision and policy with live resources, then verify the service outcome; no single controller status proves the whole system correct. Correlate the relevant unit-specific evidence and distinguish verified facts from inference.

**Common wrong answers**

- **Treat one green signal as sufficient.** It leaves other control planes unverified.
- **Rollback immediately without state analysis.** That can worsen data loss or compatibility failure.
- **Fill evidence gaps from memory.** Record UNKNOWN/INCOMPLETE and state what source would resolve it.

**Operational caveat**

Scale controls to risk, but do not claim low-risk means no evidence or that a local bundle is immutable.

**Scoring rubric**

10 points: diagnosis 2; evidence/correlation 2; blast-radius and rollback safety 2; containment/recovery verification 2; prevention and uncertainty 2.

</details>

---

# Design-review / whiteboard prompts (12 additional questions)

These are additional design prompts, not counted among the integration scenarios. A strong response may select different viable options if assumptions, risks, and recovery are explicit.

### DESIGN-01 — **Scenario and constraints:** A team of six owns 40 services across two clusters; they need Git

- **Unit / topic:** Cross-unit design review
- **Level:** L4
- **Question type:** design-review
- **Objective tested:** Design and defend a safe operating model for: Argo CD versus Flux operating model.
- **Estimated time:** 25 minutes

**Question / scenario**

**Scenario and constraints:** A team of six owns 40 services across two clusters; they need Git-driven reconciliation, audit exports, and low operational overhead. Compare Argo CD and Flux.

**Deliverables expected:** Deliver a component diagram, ownership matrix, rollout workflow, failure modes, and decision record.

Design the system and state assumptions. Include at least two viable alternatives and justify the recommendation.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**Model design:** Option A: Argo CD offers an Application-centric UI/history model that can help teams inspect sync state; verify exact features/version. Option B: Flux provides a composable controller toolkit and source/Kustomize/Helm reconciliation. Compare existing skills, UI needs, tenancy, event retention, multi-cluster operations, and upgrades.

**Trade-off analysis:** Risk: controller privilege and source credentials; complexity: component and CRD count; cost: operator time; recovery: Git/backup/bootstrap; ownership: platform team versus service teams. No universal winner.

**Acceptable alternatives:** a lower-cost/local-first implementation can be reasonable for a small non-production project if it explicitly documents what it cannot prove. A more automated and independently retained architecture is appropriate when risk, scale, auditability, and recovery requirements justify its operational cost.

**Reasoning**

A good design does not maximize automation in isolation. It makes trust boundaries, ownership, failure modes, evidence completeness, recovery, and version assumptions explicit.

**Common wrong answers**

- **One tool solves the whole problem.** Each tool provides only a portion of the control/evidence chain.
- **No failure mode or rollback design.** Happy-path architecture is not operationally complete.
- **No ownership or expiry.** Exceptions and flags become permanent ambiguity.

**Operational caveat**

The model is illustrative. Verify current product support, schemas, retention semantics, provider integration, and policy requirements before implementation.

**Scoring rubric**

10 points: safety/correctness 2; evidence and verification 2; alternatives/trade-offs 2; operations/recovery 2; clarity and ownership 2.

</details>

---

### DESIGN-02 — **Scenario and constraints:** Three environments must promote the exact tested artifact with se

- **Unit / topic:** Cross-unit design review
- **Level:** L4
- **Question type:** design-review
- **Objective tested:** Design and defend a safe operating model for: Repository layout and environment promotion.
- **Estimated time:** 25 minutes

**Question / scenario**

**Scenario and constraints:** Three environments must promote the exact tested artifact with separate production owners.

**Deliverables expected:** Draw repository tree, PR paths, branch protection, artifact flow, rollback/revert process, and ownership rules.

Design the system and state assumptions. Include at least two viable alternatives and justify the recommendation.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**Model design:** Option A: one config repo with environment directories supports visible promotion diffs. Option B: separate environment repos offer stronger access boundaries but require explicit cross-repo promotion automation. Promote digest D, not a rebuild or mutable tag.

**Trade-off analysis:** Assess merge conflicts, reviewer ownership, blast radius, drift risk, audit correlation, and disaster recovery.

**Acceptable alternatives:** a lower-cost/local-first implementation can be reasonable for a small non-production project if it explicitly documents what it cannot prove. A more automated and independently retained architecture is appropriate when risk, scale, auditability, and recovery requirements justify its operational cost.

**Reasoning**

A good design does not maximize automation in isolation. It makes trust boundaries, ownership, failure modes, evidence completeness, recovery, and version assumptions explicit.

**Common wrong answers**

- **One tool solves the whole problem.** Each tool provides only a portion of the control/evidence chain.
- **No failure mode or rollback design.** Happy-path architecture is not operationally complete.
- **No ownership or expiry.** Exceptions and flags become permanent ambiguity.

**Operational caveat**

The model is illustrative. Verify current product support, schemas, retention semantics, provider integration, and policy requirements before implementation.

**Scoring rubric**

10 points: safety/correctness 2; evidence and verification 2; alternatives/trade-offs 2; operations/recovery 2; clarity and ownership 2.

</details>

---

### DESIGN-03 — **Scenario and constraints:** A service uses three credentials and cannot restart every replica

- **Unit / topic:** Cross-unit design review
- **Level:** L4
- **Question type:** design-review
- **Objective tested:** Design and defend a safe operating model for: Secret-reference strategy and rotation/leak response.
- **Estimated time:** 25 minutes

**Question / scenario**

**Scenario and constraints:** A service uses three credentials and cannot restart every replica at once.

**Deliverables expected:** Provide secret flow diagram, access matrix, rotation sequence, leak runbook, and validation checks.

Design the system and state assumptions. Include at least two viable alternatives and justify the recommendation.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**Model design:** Option A: external secret manager plus workload references; Option B: encrypted Git-managed secret workflow where approved. Rotate new value, distribute/verify consumers, revoke old value per threat policy, and scan history/logs.

**Trade-off analysis:** Compare cost, provider dependency, key-loss risk, latency, RBAC, audit, and emergency revocation. Never commit plaintext.

**Acceptable alternatives:** a lower-cost/local-first implementation can be reasonable for a small non-production project if it explicitly documents what it cannot prove. A more automated and independently retained architecture is appropriate when risk, scale, auditability, and recovery requirements justify its operational cost.

**Reasoning**

A good design does not maximize automation in isolation. It makes trust boundaries, ownership, failure modes, evidence completeness, recovery, and version assumptions explicit.

**Common wrong answers**

- **One tool solves the whole problem.** Each tool provides only a portion of the control/evidence chain.
- **No failure mode or rollback design.** Happy-path architecture is not operationally complete.
- **No ownership or expiry.** Exceptions and flags become permanent ambiguity.

**Operational caveat**

The model is illustrative. Verify current product support, schemas, retention semantics, provider integration, and policy requirements before implementation.

**Scoring rubric**

10 points: safety/correctness 2; evidence and verification 2; alternatives/trade-offs 2; operations/recovery 2; clarity and ownership 2.

</details>

---

### DESIGN-04 — **Scenario and constraints:** Development can tolerate frequent resets; production contains sta

- **Unit / topic:** Cross-unit design review
- **Level:** L4
- **Question type:** design-review
- **Objective tested:** Design and defend a safe operating model for: Auto-sync, self-heal, and prune by environment.
- **Estimated time:** 25 minutes

**Question / scenario**

**Scenario and constraints:** Development can tolerate frequent resets; production contains stateful resources and shared dependencies.

**Deliverables expected:** Create a policy table per environment and a prune/restore drill.

Design the system and state assumptions. Include at least two viable alternatives and justify the recommendation.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**Model design:** Option A: auto-sync/self-heal in dev, controlled production sync with review. Option B: automated production sync with strict protection, narrow scope, deletion safeguards and tested recovery. Prune should be separately justified for stateful/critical resources.

**Trade-off analysis:** Score blast radius, drift window, operator load, accidental deletion, and recovery time; validate actual controller behavior.

**Acceptable alternatives:** a lower-cost/local-first implementation can be reasonable for a small non-production project if it explicitly documents what it cannot prove. A more automated and independently retained architecture is appropriate when risk, scale, auditability, and recovery requirements justify its operational cost.

**Reasoning**

A good design does not maximize automation in isolation. It makes trust boundaries, ownership, failure modes, evidence completeness, recovery, and version assumptions explicit.

**Common wrong answers**

- **One tool solves the whole problem.** Each tool provides only a portion of the control/evidence chain.
- **No failure mode or rollback design.** Happy-path architecture is not operationally complete.
- **No ownership or expiry.** Exceptions and flags become permanent ambiguity.

**Operational caveat**

The model is illustrative. Verify current product support, schemas, retention semantics, provider integration, and policy requirements before implementation.

**Scoring rubric**

10 points: safety/correctness 2; evidence and verification 2; alternatives/trade-offs 2; operations/recovery 2; clarity and ownership 2.

</details>

---

### DESIGN-05 — **Scenario and constraints:** An incident needs an urgent live change while the GitOps controll

- **Unit / topic:** Cross-unit design review
- **Level:** L4
- **Question type:** design-review
- **Objective tested:** Design and defend a safe operating model for: Drift governance and safe break-glass.
- **Estimated time:** 25 minutes

**Question / scenario**

**Scenario and constraints:** An incident needs an urgent live change while the GitOps controller remains active.

**Deliverables expected:** Write an incident runbook, evidence checklist, exception schema, and post-hoc review flow.

Design the system and state assumptions. Include at least two viable alternatives and justify the recommendation.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**Model design:** Option A: patch live state with approved break-glass and reconcile immediately into a reviewed commit. Option B: change Git and expedite sync if the control plane is healthy. Choose based on urgency and blast radius.

**Trade-off analysis:** Must capture actor/time, diff, incident ID, owner/expiry, customer impact, and verification. Avoid permanent ignore rules.

**Acceptable alternatives:** a lower-cost/local-first implementation can be reasonable for a small non-production project if it explicitly documents what it cannot prove. A more automated and independently retained architecture is appropriate when risk, scale, auditability, and recovery requirements justify its operational cost.

**Reasoning**

A good design does not maximize automation in isolation. It makes trust boundaries, ownership, failure modes, evidence completeness, recovery, and version assumptions explicit.

**Common wrong answers**

- **One tool solves the whole problem.** Each tool provides only a portion of the control/evidence chain.
- **No failure mode or rollback design.** Happy-path architecture is not operationally complete.
- **No ownership or expiry.** Exceptions and flags become permanent ambiguity.

**Operational caveat**

The model is illustrative. Verify current product support, schemas, retention semantics, provider integration, and policy requirements before implementation.

**Scoring rubric**

10 points: safety/correctness 2; evidence and verification 2; alternatives/trade-offs 2; operations/recovery 2; clarity and ownership 2.

</details>

---

### DESIGN-06 — **Scenario and constraints:** A payment workflow gets only 30 requests per minute and rare but 

- **Unit / topic:** Cross-unit design review
- **Level:** L4
- **Question type:** design-review
- **Objective tested:** Design and defend a safe operating model for: Canary for a low-traffic service with business SLIs.
- **Estimated time:** 25 minutes

**Question / scenario**

**Scenario and constraints:** A payment workflow gets only 30 requests per minute and rare but high-impact failures.

**Deliverables expected:** Define traffic split, minimum sample policy, observation duration, synthetic tests, business SLI, abort and human override.

Design the system and state assumptions. Include at least two viable alternatives and justify the recommendation.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**Model design:** Option A: longer low-percentage canary with strict minimum samples. Option B: pre-production load/replay plus small production cohort and explicit inconclusive state. Do not pretend low volume provides statistical confidence.

**Trade-off analysis:** Balance exposure, time-to-decision, false negatives, cost, and customer risk.

**Acceptable alternatives:** a lower-cost/local-first implementation can be reasonable for a small non-production project if it explicitly documents what it cannot prove. A more automated and independently retained architecture is appropriate when risk, scale, auditability, and recovery requirements justify its operational cost.

**Reasoning**

A good design does not maximize automation in isolation. It makes trust boundaries, ownership, failure modes, evidence completeness, recovery, and version assumptions explicit.

**Common wrong answers**

- **One tool solves the whole problem.** Each tool provides only a portion of the control/evidence chain.
- **No failure mode or rollback design.** Happy-path architecture is not operationally complete.
- **No ownership or expiry.** Exceptions and flags become permanent ambiguity.

**Operational caveat**

The model is illustrative. Verify current product support, schemas, retention semantics, provider integration, and policy requirements before implementation.

**Scoring rubric**

10 points: safety/correctness 2; evidence and verification 2; alternatives/trade-offs 2; operations/recovery 2; clarity and ownership 2.

</details>

---

### DESIGN-07 — **Scenario and constraints:** Metric provider can be delayed or return empty series during depl

- **Unit / topic:** Cross-unit design review
- **Level:** L4
- **Question type:** design-review
- **Objective tested:** Design and defend a safe operating model for: Automated abort policy for missing metrics.
- **Estimated time:** 25 minutes

**Question / scenario**

**Scenario and constraints:** Metric provider can be delayed or return empty series during deploys.

**Deliverables expected:** Provide a decision table for pass/fail/inconclusive, query tests, alerting, and manual override.

Design the system and state assumptions. Include at least two viable alternatives and justify the recommendation.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**Model design:** Option A: fail closed by pausing/aborting on missing data; safer but may block releases during telemetry incidents. Option B: controlled degraded mode with independent checks and explicit risk approval. Never map empty to healthy by default.

**Trade-off analysis:** Consider data freshness, sample count, query errors, SLO severity, on-call burden, and auditability.

**Acceptable alternatives:** a lower-cost/local-first implementation can be reasonable for a small non-production project if it explicitly documents what it cannot prove. A more automated and independently retained architecture is appropriate when risk, scale, auditability, and recovery requirements justify its operational cost.

**Reasoning**

A good design does not maximize automation in isolation. It makes trust boundaries, ownership, failure modes, evidence completeness, recovery, and version assumptions explicit.

**Common wrong answers**

- **One tool solves the whole problem.** Each tool provides only a portion of the control/evidence chain.
- **No failure mode or rollback design.** Happy-path architecture is not operationally complete.
- **No ownership or expiry.** Exceptions and flags become permanent ambiguity.

**Operational caveat**

The model is illustrative. Verify current product support, schemas, retention semantics, provider integration, and policy requirements before implementation.

**Scoring rubric**

10 points: safety/correctness 2; evidence and verification 2; alternatives/trade-offs 2; operations/recovery 2; clarity and ownership 2.

</details>

---

### DESIGN-08 — **Scenario and constraints:** Several teams have hundreds of flags, including kill switches and

- **Unit / topic:** Cross-unit design review
- **Level:** L4
- **Question type:** design-review
- **Objective tested:** Design and defend a safe operating model for: Feature-flag lifecycle governance.
- **Estimated time:** 25 minutes

**Question / scenario**

**Scenario and constraints:** Several teams have hundreds of flags, including kill switches and experiments.

**Deliverables expected:** Design a registry schema, ownership workflow, expiry reports, safe defaults, privacy policy, and removal PR.

Design the system and state assumptions. Include at least two viable alternatives and justify the recommendation.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**Model design:** Option A: centralized flag platform and automated expiry enforcement. Option B: repository-owned declarations plus a lightweight inventory/report. Preserve special handling for kill switches and safety flags.

**Trade-off analysis:** Trade off centralized control, provider dependency, developer friction, privacy, and flag-state observability.

**Acceptable alternatives:** a lower-cost/local-first implementation can be reasonable for a small non-production project if it explicitly documents what it cannot prove. A more automated and independently retained architecture is appropriate when risk, scale, auditability, and recovery requirements justify its operational cost.

**Reasoning**

A good design does not maximize automation in isolation. It makes trust boundaries, ownership, failure modes, evidence completeness, recovery, and version assumptions explicit.

**Common wrong answers**

- **One tool solves the whole problem.** Each tool provides only a portion of the control/evidence chain.
- **No failure mode or rollback design.** Happy-path architecture is not operationally complete.
- **No ownership or expiry.** Exceptions and flags become permanent ambiguity.

**Operational caveat**

The model is illustrative. Verify current product support, schemas, retention semantics, provider integration, and policy requirements before implementation.

**Scoring rubric**

10 points: safety/correctness 2; evidence and verification 2; alternatives/trade-offs 2; operations/recovery 2; clarity and ownership 2.

</details>

---

### DESIGN-09 — **Scenario and constraints:** A service has old and new pods concurrently and a large table nee

- **Unit / topic:** Cross-unit design review
- **Level:** L4
- **Question type:** design-review
- **Objective tested:** Design and defend a safe operating model for: Zero-downtime database migration and recovery.
- **Estimated time:** 25 minutes

**Question / scenario**

**Scenario and constraints:** A service has old and new pods concurrently and a large table needing backfill.

**Deliverables expected:** Provide expand–migrate–contract timeline, migration Job semantics, backup/PITR, checksums, pause/resume, and rollback decision tree.

Design the system and state assumptions. Include at least two viable alternatives and justify the recommendation.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**Model design:** Option A: additive schema + dual-compatible app + idempotent batches + delayed contract. Option B: versioned tables/side-by-side migration where engine and workload justify it. Include restore test and roll-forward option.

**Trade-off analysis:** Evaluate lock duration, write amplification, RPO/RTO, storage, consistency, and old-reader compatibility.

**Acceptable alternatives:** a lower-cost/local-first implementation can be reasonable for a small non-production project if it explicitly documents what it cannot prove. A more automated and independently retained architecture is appropriate when risk, scale, auditability, and recovery requirements justify its operational cost.

**Reasoning**

A good design does not maximize automation in isolation. It makes trust boundaries, ownership, failure modes, evidence completeness, recovery, and version assumptions explicit.

**Common wrong answers**

- **One tool solves the whole problem.** Each tool provides only a portion of the control/evidence chain.
- **No failure mode or rollback design.** Happy-path architecture is not operationally complete.
- **No ownership or expiry.** Exceptions and flags become permanent ambiguity.

**Operational caveat**

The model is illustrative. Verify current product support, schemas, retention semantics, provider integration, and policy requirements before implementation.

**Scoring rubric**

10 points: safety/correctness 2; evidence and verification 2; alternatives/trade-offs 2; operations/recovery 2; clarity and ownership 2.

</details>

---

### DESIGN-10 — **Scenario and constraints:** Three consumers release at different cadences; one is a partner w

- **Unit / topic:** Cross-unit design review
- **Level:** L4
- **Question type:** design-review
- **Objective tested:** Design and defend a safe operating model for: API/event/data compatibility policy.
- **Estimated time:** 25 minutes

**Question / scenario**

**Scenario and constraints:** Three consumers release at different cadences; one is a partner with a long support window.

**Deliverables expected:** Define compatibility matrix, schema/semantic contract tests, deprecation headers/telemetry, sunset policy, and N-1 rules.

Design the system and state assumptions. Include at least two viable alternatives and justify the recommendation.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**Model design:** Option A: additive evolution and optional fields with consumer inventory. Option B: explicit versioned contracts with dual-publish/adapter period. Use replay tests for semantics and units.

**Trade-off analysis:** Compare duplicated maintenance, migration time, consumer coordination, data retention, and rollback.

**Acceptable alternatives:** a lower-cost/local-first implementation can be reasonable for a small non-production project if it explicitly documents what it cannot prove. A more automated and independently retained architecture is appropriate when risk, scale, auditability, and recovery requirements justify its operational cost.

**Reasoning**

A good design does not maximize automation in isolation. It makes trust boundaries, ownership, failure modes, evidence completeness, recovery, and version assumptions explicit.

**Common wrong answers**

- **One tool solves the whole problem.** Each tool provides only a portion of the control/evidence chain.
- **No failure mode or rollback design.** Happy-path architecture is not operationally complete.
- **No ownership or expiry.** Exceptions and flags become permanent ambiguity.

**Operational caveat**

The model is illustrative. Verify current product support, schemas, retention semantics, provider integration, and policy requirements before implementation.

**Scoring rubric**

10 points: safety/correctness 2; evidence and verification 2; alternatives/trade-offs 2; operations/recovery 2; clarity and ownership 2.

</details>

---

### DESIGN-11 — **Scenario and constraints:** A high-risk production service must reconstruct who approved, bui

- **Unit / topic:** Cross-unit design review
- **Level:** L4
- **Question type:** design-review
- **Objective tested:** Design and defend a safe operating model for: Release audit-readiness architecture.
- **Estimated time:** 25 minutes

**Question / scenario**

**Scenario and constraints:** A high-risk production service must reconstruct who approved, built, promoted and ran each artifact for a defined retention period.

**Deliverables expected:** Draw evidence pipeline, manifest schema, correlation IDs, access roles, retention tiers, integrity anchors, and audit queries.

Design the system and state assumptions. Include at least two viable alternatives and justify the recommendation.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**Model design:** Option A: durable object store with restricted writers, hashes/signatures, lifecycle policies and independent anchor. Option B: OCI-attached attestations plus an event store and query index. Keep controller events, SBOM, scan, approval, runtime and post-deploy checks linked.

**Trade-off analysis:** Versioning alone is not immutability; evaluate administrator bypass, compromised CI/signing key, retrieval latency, cost, privacy, and missing data.

**Acceptable alternatives:** a lower-cost/local-first implementation can be reasonable for a small non-production project if it explicitly documents what it cannot prove. A more automated and independently retained architecture is appropriate when risk, scale, auditability, and recovery requirements justify its operational cost.

**Reasoning**

A good design does not maximize automation in isolation. It makes trust boundaries, ownership, failure modes, evidence completeness, recovery, and version assumptions explicit.

**Common wrong answers**

- **One tool solves the whole problem.** Each tool provides only a portion of the control/evidence chain.
- **No failure mode or rollback design.** Happy-path architecture is not operationally complete.
- **No ownership or expiry.** Exceptions and flags become permanent ambiguity.

**Operational caveat**

The model is illustrative. Verify current product support, schemas, retention semantics, provider integration, and policy requirements before implementation.

**Scoring rubric**

10 points: safety/correctness 2; evidence and verification 2; alternatives/trade-offs 2; operations/recovery 2; clarity and ownership 2.

</details>

---

### DESIGN-12 — **Scenario and constraints:** The cluster continues serving traffic but repository access and c

- **Unit / topic:** Cross-unit design review
- **Level:** L4
- **Question type:** design-review
- **Objective tested:** Design and defend a safe operating model for: GitOps control-plane outage and recovery.
- **Estimated time:** 25 minutes

**Question / scenario**

**Scenario and constraints:** The cluster continues serving traffic but repository access and controller reconciliation fail during an incident.

**Deliverables expected:** Provide RACI, bootstrap sequence, source credential recovery, repository mirror/backups, drift inventory, and reconciliation checklist.

Design the system and state assumptions. Include at least two viable alternatives and justify the recommendation.

<details><summary>Reveal model answer, reasoning, and scoring</summary>

**Model answer**

**Model design:** Option A: restore repo/network/credentials and let controller converge. Option B: use approved break-glass for urgent containment, capture state and later reconcile. Bootstrap the controller from a trusted IaC/backup path.

**Trade-off analysis:** Avoid unsafe broad credentials, accidental prune after recovery, and blind mass sync. Verify workloads, source revision, and data backups.

**Acceptable alternatives:** a lower-cost/local-first implementation can be reasonable for a small non-production project if it explicitly documents what it cannot prove. A more automated and independently retained architecture is appropriate when risk, scale, auditability, and recovery requirements justify its operational cost.

**Reasoning**

A good design does not maximize automation in isolation. It makes trust boundaries, ownership, failure modes, evidence completeness, recovery, and version assumptions explicit.

**Common wrong answers**

- **One tool solves the whole problem.** Each tool provides only a portion of the control/evidence chain.
- **No failure mode or rollback design.** Happy-path architecture is not operationally complete.
- **No ownership or expiry.** Exceptions and flags become permanent ambiguity.

**Operational caveat**

The model is illustrative. Verify current product support, schemas, retention semantics, provider integration, and policy requirements before implementation.

**Scoring rubric**

10 points: safety/correctness 2; evidence and verification 2; alternatives/trade-offs 2; operations/recovery 2; clarity and ownership 2.

</details>

---

# Final scoring and remediation plan

## Per-unit score sheet

Record the number correct and percent for each unit. For each unit, use 12 core questions; assign partial credit only according to the rubric included with the question. Integration and design-review prompts should be scored separately.

| Unit | Core IDs | Score / 12 | % | Weak objective(s) | Remediation |
|---|---|---:|---:|---|---|
| 1 — GitOps principles and desired-state reconciliation | U01-Q01–Q12 |  |  |  | Revisit [Unit 1 lesson](<01-gitops-principles-and-desired-state-reconciliation.md>) and repeat the relevant lab/check. |
| 2 — Argo CD: applications, projects, and sync policies | U02-Q01–Q12 |  |  |  | Revisit [Unit 2 lesson](<02-argo-cd-applications-projects-and-sync-policies.md>) and repeat the relevant lab/check. |
| 3 — Flux controllers and Kustomize/Helm reconciliation | U03-Q01–Q12 |  |  |  | Revisit [Unit 3 lesson](<03-flux-controllers-and-kustomize-helm-reconciliation.md>) and repeat the relevant lab/check. |
| 4 — Repository layout and multi-environment promotion | U04-Q01–Q12 |  |  |  | Revisit [Unit 4 lesson](<04-repository-layout-and-multi-environment-promotion.md>) and repeat the relevant lab/check. |
| 5 — Configuration and secret reference management | U05-Q01–Q12 |  |  |  | Revisit [Unit 5 lesson](<05-configuration-and-secret-reference-management.md>) and repeat the relevant lab/check. |
| 6 — Deployment drift detection and reconciliation | U06-Q01–Q12 |  |  |  | Revisit [Unit 6 lesson](<06-deployment-drift-detection-and-reconciliation.md>) and repeat the relevant lab/check. |
| 7 — Progressive delivery: canary and blue-green releases | U07-Q01–Q12 |  |  |  | Revisit [Unit 7 lesson](<07-progressive-delivery-with-canary-and-blue-green-releases.md>) and repeat the relevant lab/check. |
| 8 — Argo Rollouts, Flagger, and traffic-based analysis | U08-Q01–Q12 |  |  |  | Revisit [Unit 8 lesson](<08-argo-rollouts-flagger-and-traffic-based-analysis.md>) and repeat the relevant lab/check. |
| 9 — Release health analysis and automated abort | U09-Q01–Q12 |  |  |  | Revisit [Unit 9 lesson](<09-release-health-analysis-and-automated-abort.md>) and repeat the relevant lab/check. |
| 10 — Feature flags and dark launches | U10-Q01–Q12 |  |  |  | Revisit [Unit 10 lesson](<10-feature-flags-and-dark-launches.md>) and repeat the relevant lab/check. |
| 11 — Database and data-platform migration safety | U11-Q01–Q12 |  |  |  | Revisit [Unit 11 lesson](<11-database-and-data-platform-migration-safety.md>) and repeat the relevant lab/check. |
| 12 — Backward-compatible pipeline and API releases | U12-Q01–Q12 |  |  |  | Revisit [Unit 12 lesson](<12-backward-compatible-pipeline-and-api-releases.md>) and repeat the relevant lab/check. |
| 13 — Release evidence and audit trails | U13-Q01–Q12 |  |  |  | Revisit [Unit 13 lesson](<13-release-evidence-and-audit-trails.md>) and repeat the relevant lab/check. |

**Objective-to-question mapping:** each unit’s Q01–Q03 test its listed objectives in order; Q04–Q06 test the unit’s three MCQ objectives; Q07–Q08 test output interpretation; Q09–Q10 test manifest/config review; Q11 tests incident reasoning; Q12 tests design. Cross-unit mapping is explicit in each XINT prompt; DESIGN prompts map to the topics in their headings.

### Weak-area diagnosis

- **Concept gap:** terminology is confused or a status is overclaimed. Re-read the relevant L1 concept map and explain the mechanism without tools.
- **Command/output gap:** the answer ignores fields, labels, timestamps, conditions, or sample coverage. Re-run the relevant local lab and annotate the output line by line.
- **Safety/rollback gap:** the answer mutates first, skips evidence preservation, or assumes code rollback reverses data. Rework the incident question with a blast-radius and compatibility checklist.
- **Design/trade-off gap:** the answer names a tool but omits ownership, failure modes, cost, recovery, or alternatives. Re-answer the unit design question using a diagram and scoring rubric.

### Capstone readiness gate

Proceed only when you can: (1) explain desired-state reconciliation and predict drift behavior; (2) select a delivery strategy based on measured traffic and business SLIs; (3) evaluate rollback compatibility across code, flags, schema, events, and data; (4) design a fail-closed/UNKNOWN analysis policy for missing or stale metrics; and (5) reconstruct a release from source commit through runtime evidence without inferring missing links. A critical-safety failure overrides the aggregate score.

# Coverage and authenticity audit matrix

| Audit requirement | Expected | Actual | Status | Notes |
|---|---|---|---|---|
| Unit core counts | 12 each for Units 1–13 | 12 × 13 = 156 | PASS | Programmatic ID count confirms exactly 12 per unit. |
| Cross-unit scenario uniqueness | At least 35 unique | 45 unique XINT IDs | PASS | IDs are unique and each scenario has an explicit multi-unit mapping. |
| Design prompt uniqueness | 12 additional unique prompts | 12 unique DESIGN IDs | PASS | Separate from the integration scenario IDs. |
| Cross-unit scenarios | At least 35 unique | 45 drafted | PASS | IDs XINT-01 onward; each has multi-unit mapping. |
| Design prompts | 12 additional | 12 drafted | PASS | IDs DESIGN-01 onward. |
| Total unique IDs | At least 203 | 213 unique IDs | PASS | 156 core + 45 integration + 12 design-review prompts. |
| Answer metadata | Every question includes answer/reasoning/wrong answers/caveat/rubric | 213 of 213 contain all fields | PASS | Confirmed by structural scan. |
| MCQ option explanations | Four options, each explained | 39 MCQs × 4 options; each option has an explanation | PASS | Option-count scan passed; explanations are conceptual, not provider-version claims. |
| Manifest-review defects | At least three distinct defects each | 26 reviews; 3 enumerated defects per review | PASS | Defects enumerated by unit; human review still advised before operational reuse. |
| Incident safety | Blast radius and rollback safety | Included in 13 unit incidents and integration scenarios | PASS | Review scenario-specific compatibility before using as a runbook. |
| Unit 13 incident/lab coverage | Seven incidents and seven labs represented | Included in U13 and cross-unit evidence questions | PASS | Questions assess concepts; they do not claim learner ran labs. |
| Scoring and safety override | Exact thresholds and override | Included above | PASS | Instructional, not certification. |
| Source and link fidelity | Confirmed tree paths only | Roadmap(9).md lists the requested `08-` path; Unit 1/2 files are physically outside target folder and capstone file was not found in target folder | PARTIAL | The uploaded prompt mentions an older `03-` path as a possible discrepancy; the inspected snapshot uses `08-`. No unrelated files were changed. |
| Live product/version behavior | No unsupported defaults or live-test claims | No live Kubernetes/GitOps/controller integrations executed | NOT VERIFIED | Verify exact CLI/CRD behavior against installed versions and official documentation before using examples operationally. |

# Version-sensitive `[VERIFY]` register and references

| Item | Why version-sensitive | Official source to check | Verification status |
|---|---|---|---|
| OpenGitOps principles | Current wording and principle page may evolve | https://opengitops.dev/ | Not independently re-verified during question-bank generation; check current text. |
| Argo CD Application, AppProject, sync and history | CRD fields, CLI output, sync options, tracking and deletion semantics vary by release | https://argo-cd.readthedocs.io/ | Conceptual questions avoid relying on unverified defaults; check installed version. |
| Flux source/Kustomize/Helm controllers and notifications | API versions, fields, status conditions, notification behavior and source verification can vary | https://fluxcd.io/flux/ | Verify installed Flux and CRD versions. |
| Argo Rollouts and AnalysisRun | CRD schema, analysis result states, traffic-provider integrations and CLI output vary | https://argo-rollouts.readthedocs.io/ | Use installed CRD schema and provider documentation. |
| Flagger | Provider-specific traffic analysis and metrics templates vary | https://docs.flagger.app/ | Verify selected release/provider. |
| Kubernetes workload inspection, RBAC, auditing | API versions, audit policy and managed-service retention/configuration differ | https://kubernetes.io/docs/ | Verify cluster version and managed-service controls. |
| Prometheus and PromQL | Metric names, labels, units, query functions and scrape intervals are installation-specific | https://prometheus.io/docs/prometheus/latest/querying/basics/ | All metric examples are illustrative; test against actual telemetry. |
| Git commit/tag signature verification | GPG/SSH setup and trust policy differ; verification does not itself prove review approval | https://git-scm.com/docs/git-verify-commit | Verify local Git version and trust configuration. |
| OCI image digests and labels | Registry/runtime identity strings and metadata availability differ | https://github.com/opencontainers/image-spec | Compare runtime-specific identity carefully; no universal imageID parser assumed. |
| SLSA/in-toto/Sigstore, SBOM | Attestation predicates, trust roots, keyless identity, formats and commands evolve | https://slsa.dev/ ; https://in-toto.io/ ; https://docs.sigstore.dev/ ; https://spdx.dev/ ; https://cyclonedx.org/ | Conceptual coverage; verify current command syntax and trust policy. |
| Database engine migration behavior | DDL locks, transaction semantics, default behavior and PITR differ by engine/version | Official documentation for the chosen database engine | No engine-specific destructive SQL is prescribed as a universal command. |

## Final self-audit checklist

- [x] Programmatic count: 156 unit-core questions (exactly 12 each), 45 XINT scenarios, 12 DESIGN prompts, 213 unique IDs total.
- [x] Unit 1–13 curriculum topics are represented in unit-specific core questions.
- [x] Each unit is designed for the required 3 conceptual + 3 MCQ + 2 output + 2 flawed-manifest + 1 incident + 1 design mix.
- [x] 45 cross-unit scenarios cover the required themes, each with an explicit multi-unit mapping.
- [x] 12 additional design-review prompts include deliverables, alternatives, trade-offs, and a 10-point rubric.
- [x] Answers are collapsible so learners can self-test.
- [x] Simulated output and intentionally flawed snippets are labelled.
- [x] Scoring thresholds and critical-safety override are stated.
- [x] Version-sensitive behavior is marked for verification rather than asserted as a universal default.
- [ ] Human review of every technical snippet and relative link remains necessary; this document does not claim live controller validation.
