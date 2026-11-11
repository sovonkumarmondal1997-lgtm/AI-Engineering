# M03 --- Production Kubernetes Operations: Practice Questions

## Document metadata

-   **Target:**
    `Stage 2E — Production DevOps & Platform Engineering/03-Production-Kubernetes-Operations/practice-questions.md`
-   **Environment:** zero-budget WSL2/Linux laptop; kind is a local
    simulation, not proof of managed-cluster behavior.
-   **Evidence status:** authored scenarios/output are illustrative; no
    cluster/lab commands were executed. Version-sensitive details are
    marked `[VERIFY]`.
-   **Sources read:** uploaded practice prompt,
    `PROMPT-Production-Kubernetes-Operations(3).md`, available
    roadmap-tree variant, and all 11 available lesson files
    (topic/heading scope inspected). Exact canonical `Roadmap_ptree.md`,
    syllabus output file, M03 README and repository checkout/diff were
    unavailable.

## How to use this question bank

Answer before reading the model answer. Separate observations from
hypotheses. For MCQs, explain every distractor. For manifest reviews,
identify independent defects, impact, correction, and verification. For
incidents, include a low-risk test, scoped mitigation, stop/rollback
condition, and prevention. `[VERIFY]` means verify exact
Kubernetes/etcd/kubectl/distribution/provider versions before
operational use.

## Coverage map and question-count ledger

  --------------------------------------------------------------------------------------------
  Unit/section            Required   Actual count Question types  Level        Source status
                           minimum                present         coverage     
  ----------------- -------------- -------------- --------------- ------------ ---------------
  Unit 1:                       12             13 3 SA, 3 MCQ, 2  L1--L4       Lesson file
  Production                                      OUT, 2 MAN, 1                available;
  cluster                                         INC, 1 DES + 1               topic scope
  architecture and                                extra                        inspected
  control plane                                                                

  Unit 2:                       12             13 3 SA, 3 MCQ, 2  L1--L4       Lesson file
  Namespaces,                                     OUT, 2 MAN, 1                available;
  resource quotas,                                INC, 1 DES + 1               topic scope
  and limit ranges                                extra                        inspected

  Unit 3: Probes,               12             13 3 SA, 3 MCQ, 2  L1--L4       Lesson file
  health checks,                                  OUT, 2 MAN, 1                available;
  and workload                                    INC, 1 DES + 1               topic scope
  recovery                                        extra                        inspected

  Unit 4:                       12             13 3 SA, 3 MCQ, 2  L1--L4       Lesson file
  Deployments,                                    OUT, 2 MAN, 1                available;
  StatefulSets,                                   INC, 1 DES + 1               topic scope
  Jobs, and                                       extra                        inspected
  CronJobs                                                                     

  Unit 5: Pod                   12             13 3 SA, 3 MCQ, 2  L1--L4       Lesson file
  disruption                                      OUT, 2 MAN, 1                available;
  budgets and                                     INC, 1 DES + 1               topic scope
  graceful shutdown                               extra                        inspected

  Unit 6:                       12             12 3 SA, 3 MCQ, 2  L1--L4       Lesson file
  Horizontal and                                  OUT, 2 MAN, 1                available;
  vertical                                        INC, 1 DES                   topic scope
  autoscaling                                                                  inspected

  Unit 7: Node                  12             12 3 SA, 3 MCQ, 2  L1--L4       Lesson file
  pools, taints,                                  OUT, 2 MAN, 1                available;
  affinity, and                                   INC, 1 DES                   topic scope
  workload                                                                     inspected
  placement                                                                    

  Unit 8: Cluster               12             12 3 SA, 3 MCQ, 2  L1--L4       Lesson file
  upgrades and                                    OUT, 2 MAN, 1                available;
  version                                         INC, 1 DES                   topic scope
  compatibility                                                                inspected

  Unit 9:                       12             12 3 SA, 3 MCQ, 2  L1--L4       Lesson file
  Kubernetes RBAC                                 OUT, 2 MAN, 1                available;
  and Pod Security                                INC, 1 DES                   topic scope
  Standards                                                                    inspected

  Unit 10: etcd                 12             12 3 SA, 3 MCQ, 2  L1--L4       Lesson file
  health, backup,                                 OUT, 2 MAN, 1                available;
  and control-plane                               INC, 1 DES                   topic scope
  troubleshooting                                                              inspected

  Unit 11:                      12             12 3 SA, 3 MCQ, 2  L1--L4       Lesson file
  Production                                      OUT, 2 MAN, 1                available;
  cluster                                         INC, 1 DES                   topic scope
  troubleshooting                                                              inspected

  Cross-unit                    25             28 Mixed incident, L2--L4       Syllabus topics
  integration                                     output,                      cross-checked
                                                  manifest,                    against lessons
                                                  design and                   
                                                  recovery                     

  **Total scored           **160**        **165** **Full per-unit **L1--L4**   **Unique IDs
  questions**                                     mix plus                     recounted
                                                  integration**                below**

  Whiteboard            10 exactly             10 Design review   L3--L4       Prompt scope
  prompts                                                                      
  (additional)                                                                 
  --------------------------------------------------------------------------------------------

-   Units 1--11: 132 required base questions plus five extra questions
    in Units 1--5 = 137; 28 cross-unit questions = 165 total. The ten
    whiteboard prompts are additional, not counted as scored questions.

## Scoring and remediation policy

-   **80% or higher:** proceed, retaining any safety-critical
    remediation items. **60--79%:** remediate weak objectives and retry
    a different subset. **Below 60%:** revisit core lesson material and
    retake a different subset.
-   Short answer: facts, mechanism, operational implication. MCQ:
    correct selection and reasoning. Output: evidence, uncertainty and
    next diagnostic. Manifest: defects, corrections, verification and
    safety. Incident: evidence, differential, mitigation, stop
    condition, verification and prevention. Design: use the explicit
    rubric.
-   Never treat a score alone as production readiness. Unsafe
    destructive action or unsupported certainty should receive no credit
    even if the proposed end state sounds plausible.

### Remediation map

  ------------------------------------------------------------------------------------------------------------------
  Common mistake          Revisit                 Lesson file
  ----------------------- ----------------------- ------------------------------------------------------------------
  Misunderstanding:       Unit 1                  `01-production-cluster-architecture-and-control-plane.md`
  declarative state and                           
  reconciliation                                  

  Misunderstanding:       Unit 2                  `02-namespaces-resource-quotas-and-limit-ranges.md`
  ResourceQuota versus                            
  LimitRange                                      

  Misunderstanding:       Unit 3                  `03-probes-health-checks-and-workload-recovery.md`
  readiness versus                                
  liveness versus startup                         

  Misunderstanding:       Unit 4                  `04-deployments-statefulsets-jobs-and-cronjobs-in-production.md`
  rollback does not                               
  reverse external side                           
  effects                                         

  Misunderstanding:       Unit 5                  `05-pod-disruption-budgets-and-graceful-shutdown.md`
  SIGTERM, draining and                           
  in-flight work                                  

  Misunderstanding: HPA   Unit 6                  `06-horizontal-and-vertical-autoscaling.md`
  versus VPA versus node                          
  autoscaling                                     

  Misunderstanding:       Unit 7                  `07-node-pools-taints-affinity-and-workload-placement.md`
  taints/tolerations do                           
  not guarantee placement                         

  Misunderstanding:       Unit 8                  `08-cluster-upgrades-and-version-compatibility.md`
  in-place versus                                 
  rotation versus                                 
  blue/green                                      

  Misunderstanding:       Unit 9                  `09-kubernetes-rbac-and-pod-security-standards.md`
  authentication versus                           
  authorization versus                            
  admission                                       

  Misunderstanding:       Unit 10                 `10-etcd-health-backup-and-control-plane-troubleshooting.md`
  snapshot integrity                              
  versus recoverability                           

  Misunderstanding:       Unit 11                 `11-production-cluster-troubleshooting.md`
  privacy-safe diagnostic                         
  bundles                                         
  ------------------------------------------------------------------------------------------------------------------

## Unit 1 --- Production cluster architecture and control plane

### U01-SA-01 --- Unit 1 --- Production cluster architecture and control plane

-   **Unit/category:** Unit 1 --- Production cluster architecture and
    control plane
-   **Level:** L1
-   **Objective tested:** Explain the mechanism and operational
    consequence of control plane versus data plane.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Control plane versus data plane. Explain the
    mechanism, the trade-off, and one failure mode.
-   **Model answer:** Explain control plane versus data plane by
    defining the mechanism, identifying the responsible Kubernetes
    layer/resource, and stating one production implication. Validate
    with the relevant object status/events rather than assuming the
    declared configuration proves runtime behavior.
-   **Common wrong answers/misconceptions:** Common misconceptions: etcd
    is state store, not process launcher; kind node count does not prove
    production HA. These fail because they collapse distinct mechanisms
    or claim guarantees beyond the resource/component boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:**
    01-production-cluster-architecture-and-control-plane.md --- control
    plane versus data plane
-   **Version note:** Not version-sensitive

### U01-SA-02 --- Unit 1 --- Production cluster architecture and control plane

-   **Unit/category:** Unit 1 --- Production cluster architecture and
    control plane
-   **Level:** L2
-   **Objective tested:** Explain the mechanism and operational
    consequence of declarative state and reconciliation.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Declarative state and reconciliation. Explain
    the mechanism, the trade-off, and one failure mode.
-   **Model answer:** The distinction is operational: declarative state
    and reconciliation. Inspect the relevant API object, its
    conditions/events and the component that owns the decision. A
    configuration setting is not a substitute for evidence that the
    intended behavior occurred.
-   **Common wrong answers/misconceptions:** Common misconceptions: kind
    node count does not prove production HA; API server, scheduler,
    controllers, kubelet/runtime, networking/storage. These fail because
    they collapse distinct mechanisms or claim guarantees beyond the
    resource/component boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:**
    01-production-cluster-architecture-and-control-plane.md ---
    declarative state and reconciliation
-   **Version note:** Not version-sensitive

### U01-SA-03 --- Unit 1 --- Production cluster architecture and control plane

-   **Unit/category:** Unit 1 --- Production cluster architecture and
    control plane
-   **Level:** L3
-   **Objective tested:** Explain the mechanism and operational
    consequence of failure domains and kind limitations.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Failure domains and kind limitations. Explain
    the mechanism, the trade-off, and one failure mode.
-   **Model answer:** Use a failure model first: failure domains and
    kind limitations. State what the mechanism guarantees, what it does
    not guarantee, and which evidence would falsify your initial
    hypothesis. Record a measurable verification signal and rollback
    boundary.
-   **Common wrong answers/misconceptions:** Common misconceptions: API
    server, scheduler, controllers, kubelet/runtime, networking/storage;
    etcd is state store, not process launcher. These fail because they
    collapse distinct mechanisms or claim guarantees beyond the
    resource/component boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:**
    01-production-cluster-architecture-and-control-plane.md --- failure
    domains and kind limitations
-   **Version note:** Not version-sensitive

### U01-MCQ-01 --- Unit 1 --- Production cluster architecture and control plane

-   **Unit/category:** Unit 1 --- Production cluster architecture and
    control plane
-   **Level:** L1
-   **Objective tested:** Choose an evidence-based operational response
    to scheduler placement.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which response best addresses scheduler
    placement? Options: A. Make the broadest change immediately.; B.
    Inspect the owning resource status/events and confirm scope before
    changing state.; C. Delete the namespace.; D. Assume the symptom
    uniquely proves one root cause.
-   **Model answer:** A is incorrect (Make the broadest change
    immediately.): a broad immediate change skips diagnosis and may
    enlarge blast radius.; B is best (Inspect the owning resource
    status/events and confirm scope before changing state.): Evidence
    from the owning resource and event stream narrows the differential
    while preserving state.; C is incorrect (Delete the namespace.):
    deleting the namespace is destructive and unrelated to an
    evidence-first diagnosis.; D is incorrect (Assume the symptom
    uniquely proves one root cause.): a symptom rarely proves one unique
    root cause without corroborating evidence..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    B is the only best answer.
-   **Source/coverage note:**
    01-production-cluster-architecture-and-control-plane.md --- control
    plane versus data plane
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U01-MCQ-02 --- Unit 1 --- Production cluster architecture and control plane

-   **Unit/category:** Unit 1 --- Production cluster architecture and
    control plane
-   **Level:** L2
-   **Objective tested:** Choose an evidence-based operational response
    to etcd state storage.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which statement about declarative state and
    reconciliation is most accurate? Options: A. API server, scheduler,
    controllers, kubelet/runtime, networking/storage; B. etcd is state
    store, not process launcher; C. kind node count does not prove
    production HA; D. The mechanism guarantees every dependent
    application outcome.
-   **Model answer:** A is incorrect (API server, scheduler,
    controllers, kubelet/runtime, networking/storage): this statement
    does not correctly express the lesson's mechanism or guarantee; it
    conflates a distinct control or overstates what the component
    ensures.; B is best (etcd is state store, not process launcher): The
    correct distinction is the boundary described in the lesson;
    application-level correctness still requires independent
    verification.; C is incorrect (kind node count does not prove
    production HA): this statement does not correctly express the
    lesson's mechanism or guarantee; it conflates a distinct control or
    overstates what the component ensures.; D is incorrect (The
    mechanism guarantees every dependent application outcome.): this
    statement does not correctly express the lesson's mechanism or
    guarantee; it conflates a distinct control or overstates what the
    component ensures..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    B is the only best answer.
-   **Source/coverage note:**
    01-production-cluster-architecture-and-control-plane.md ---
    declarative state and reconciliation
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U01-MCQ-03 --- Unit 1 --- Production cluster architecture and control plane

-   **Unit/category:** Unit 1 --- Production cluster architecture and
    control plane
-   **Level:** L3
-   **Objective tested:** Choose an evidence-based operational response
    to API accepted but workload not converging.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which evidence is strongest before changing
    policy for API accepted but workload not converging? Options: A. A
    single screenshot without timestamp.; B. Only the desired-state
    manifest.; C. Correlated status, events, recent changes,
    capacity/dependency evidence and an explicit SLO impact.; D. A guess
    based on a similar incident.
-   **Model answer:** A is incorrect (A single screenshot without
    timestamp.): a screenshot alone lacks the correlated status, event
    and timeline evidence needed for diagnosis.; B is incorrect (Only
    the desired-state manifest.): desired state alone does not prove
    observed runtime behavior or root cause.; C is best (Correlated
    status, events, recent changes, capacity/dependency evidence and an
    explicit SLO impact.): Correlated evidence supports a differential
    and helps select a scoped reversible mitigation.; D is incorrect (A
    guess based on a similar incident.): guessing from a similar
    incident is not evidence for this cluster..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    C is the only best answer.
-   **Source/coverage note:**
    01-production-cluster-architecture-and-control-plane.md --- failure
    domains and kind limitations
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U01-OUT-01 --- Unit 1 --- Production cluster architecture and control plane

-   **Unit/category:** Unit 1 --- Production cluster architecture and
    control plane
-   **Level:** L2
-   **Objective tested:** Interpret a symptom without overstating what
    it proves about control plane versus data plane.
-   **Estimated time:** 7 minutes
-   **Question type:** Output interpretation
-   **Question prompt:** **Illustrative output --- not observed
    execution.** Scenario: scheduler placement. Assume a current
    namespace/context is confirmed. The only evidence available is this
    symptom; no additional root-cause evidence has been supplied. State
    what can be concluded and what to inspect next.
-   **Model answer:** The observation supports investigation of
    scheduler placement, but does not uniquely establish root cause.
    Inspect the relevant object status/conditions, timestamped events,
    recent changes and the adjacent layer: kind node count does not
    prove production HA. If the next evidence remains ambiguous, keep
    competing hypotheses open and perform a low-risk read-only test
    before mutation.
-   **Common wrong answers/misconceptions:** Wrong answer 1: state a
    definitive root cause from a symptom alone. Wrong answer 2: perform
    a destructive change before collecting object/event evidence.
-   **Scoring rubric:** 4 points: observed fact 1; bounded inference 1;
    next evidence 1; safe action 1.
-   **Source/coverage note:**
    01-production-cluster-architecture-and-control-plane.md ---
    scheduler placement
-   **Version note:** \[VERIFY\] all sample output is illustrative and
    command fields vary by version.

### U01-OUT-02 --- Unit 1 --- Production cluster architecture and control plane

-   **Unit/category:** Unit 1 --- Production cluster architecture and
    control plane
-   **Level:** L3
-   **Objective tested:** Interpret a symptom without overstating what
    it proves about declarative state and reconciliation.
-   **Estimated time:** 7 minutes
-   **Question type:** Output interpretation
-   **Question prompt:** **Illustrative output --- not observed
    execution.** Scenario: etcd state storage. Assume a current
    namespace/context is confirmed. The only evidence available is this
    symptom; no additional root-cause evidence has been supplied. State
    what can be concluded and what to inspect next.
-   **Model answer:** The observation supports investigation of etcd
    state storage, but does not uniquely establish root cause. Inspect
    the relevant object status/conditions, timestamped events, recent
    changes and the adjacent layer: API server, scheduler, controllers,
    kubelet/runtime, networking/storage. If the next evidence remains
    ambiguous, keep competing hypotheses open and perform a low-risk
    read-only test before mutation.
-   **Common wrong answers/misconceptions:** Wrong answer 1: state a
    definitive root cause from a symptom alone. Wrong answer 2: perform
    a destructive change before collecting object/event evidence.
-   **Scoring rubric:** 4 points: observed fact 1; bounded inference 1;
    next evidence 1; safe action 1.
-   **Source/coverage note:**
    01-production-cluster-architecture-and-control-plane.md --- etcd
    state storage
-   **Version note:** \[VERIFY\] all sample output is illustrative and
    command fields vary by version.

### U01-MAN-01 --- Unit 1 --- Production cluster architecture and control plane

-   **Unit/category:** Unit 1 --- Production cluster architecture and
    control plane

-   **Level:** L2

-   **Objective tested:** Find at least three independent defects in a
    production cluster architecture and control plane configuration.

-   **Estimated time:** 10 minutes

-   **Question type:** Manifest review

-   **Question prompt:** Review this **intentionally defective training
    fixture** and identify at least three independent defects/risks.
    Give a correction plan and verification evidence. Do not apply it
    as-is.

    ``` yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata: {name: scorer, namespace: scoring}
    spec:
      replicas: 3
      selector: {matchLabels: {app: scorer}}
      template:
        metadata: {labels: {app: worker}}
        spec:
          containers:
          - name: scorer
            image: scorer:latest
    ```

-   **Model answer:** Defects: selector `app: scorer` does not match Pod
    label `app: worker`; mutable `latest` image tag is not reproducible;
    requests/limits and health contract are absent for a production API.
    Align the labels, pin a release or digest, add measured resources
    and appropriate startup/readiness/liveness contracts. Verify with
    server-side dry-run, rollout status, Pod events and a request-level
    smoke test.

-   **Common wrong answers/misconceptions:** Wrong answer 1: treat a
    YAML parse as proof of semantic correctness. Wrong answer 2: remove
    all controls to make the workload proceed. Wrong answer 3: give a
    correction without verification.

-   **Scoring rubric:** 6 points: three independent defects 3; precise
    fixes 1; verification 1; safety/rollback 1.

-   **Source/coverage note:**
    01-production-cluster-architecture-and-control-plane.md --- failure
    domains and kind limitations

-   **Version note:** \[VERIFY\] intentionally defective excerpt;
    validate API fields and defaults against target version.

### U01-MAN-02 --- Unit 1 --- Production cluster architecture and control plane

-   **Unit/category:** Unit 1 --- Production cluster architecture and
    control plane

-   **Level:** L3

-   **Objective tested:** Find at least three independent defects in a
    production cluster architecture and control plane configuration.

-   **Estimated time:** 10 minutes

-   **Question type:** Manifest review

-   **Question prompt:** Review this **intentionally defective training
    fixture** and identify at least three independent defects/risks.
    Give a correction plan and verification evidence. Do not apply it
    as-is.

    ``` yaml
    apiVersion: v1
    kind: Pod
    metadata: {name: diagnostic, namespace: production}
    spec:
      containers:
      - name: shell
        image: busybox:latest
        command: ["sh", "-c", "sleep 3600"]
        securityContext: {privileged: true}
      serviceAccountName: default
    ```

-   **Model answer:** Risks: privileged container grants unnecessary
    host-level capabilities; mutable image tag undermines
    reproducibility; default ServiceAccount may expose unintended API
    permissions; no resource bounds. Use a pinned trusted image,
    non-root/restricted securityContext, dedicated least-privilege
    identity or no token automount where appropriate, and resource
    requests/limits. Verify RBAC with `kubectl auth can-i` and policy
    admission in staging.

-   **Common wrong answers/misconceptions:** Wrong answer 1: treat a
    YAML parse as proof of semantic correctness. Wrong answer 2: remove
    all controls to make the workload proceed. Wrong answer 3: give a
    correction without verification.

-   **Scoring rubric:** 6 points: three independent defects 3; precise
    fixes 1; verification 1; safety/rollback 1.

-   **Source/coverage note:**
    01-production-cluster-architecture-and-control-plane.md --- control
    plane versus data plane

-   **Version note:** \[VERIFY\] intentionally defective excerpt;
    validate API fields and defaults against target version.

### U01-INC-01 --- Unit 1 --- Production cluster architecture and control plane

-   **Unit/category:** Unit 1 --- Production cluster architecture and
    control plane
-   **Level:** L3
-   **Objective tested:** Use evidence-first troubleshooting for
    deployment does not converge.
-   **Estimated time:** 15 minutes
-   **Question type:** Incident/troubleshooting
-   **Question prompt:** deployment does not converge. Describe scope
    and timeline, evidence to collect, competing hypotheses, a low-risk
    first test, scoped mitigation, verification, rollback/stop
    condition, and prevention.
-   **Model answer:** Confirm context, namespace, affected SLO and
    change window; capture object conditions/events/logs and recent
    changes. Investigate scheduler placement and compare at least two
    plausible causes. Prefer read-only evidence first; apply only a
    scoped, reversible mitigation approved for the environment. Verify
    service-level behavior and object convergence, define a stop
    condition, and record the outcome/runbook follow-up.
-   **Common wrong answers/misconceptions:** Wrong answer 1: treat
    symptom as root cause. Wrong answer 2: make a cluster-wide change
    without blast-radius analysis. Wrong answer 3: declare recovery
    without SLO/object verification.
-   **Scoring rubric:** 8 points: scope/timeline 1; evidence 2;
    differential 1; low-risk test 1; scoped mitigation/stop 1;
    verification 1; prevention/handoff 1.
-   **Source/coverage note:**
    01-production-cluster-architecture-and-control-plane.md ---
    deployment does not converge
-   **Version note:** \[VERIFY\] any destructive/provider-specific
    recovery action against exact release runbook.

### U01-DES-01 --- Unit 1 --- Production cluster architecture and control plane

-   **Unit/category:** Unit 1 --- Production cluster architecture and
    control plane
-   **Level:** L4
-   **Objective tested:** Design a production-ready approach for design
    a laptop lab with explicit trade-offs.
-   **Estimated time:** 18 minutes
-   **Question type:** Design
-   **Question prompt:** design a laptop lab. State constraints, compare
    at least two approaches, explain failure modes/cost/operability, and
    give a verification plan.
-   **Model answer:** Define the SLO, failure domains, data/security
    constraints and operating ownership. Approach A optimizes
    simplicity/cost but accepts tighter shared blast radius; approach B
    adds isolation or redundancy at higher capacity/operational cost.
    Select based on measured demand and explicit failure model. Include
    monitoring, rollback/stop criteria, staging rehearsal and a
    post-change verification signal.
-   **Common wrong answers/misconceptions:** Wrong answer 1: choose the
    most complex option without a risk case. Wrong answer 2: optimize
    cost without addressing failure domains. Wrong answer 3: rely on
    component presence rather than tested recovery.
-   **Scoring rubric:** 10 points: constraints/SLO 2; mechanism
    correctness 2; alternatives/trade-offs 2; failure handling 2;
    observability/verification 2.
-   **Source/coverage note:**
    01-production-cluster-architecture-and-control-plane.md ---
    expert/design topics
-   **Version note:** \[VERIFY\] implementation syntax and
    managed-provider behavior.

### U01-EXT-01 --- Unit 1 --- Production cluster architecture and control plane

-   **Unit/category:** Unit 1 --- Production cluster architecture and
    control plane
-   **Level:** L3
-   **Objective tested:** Evaluate a change proposal for control plane
    versus data plane using production evidence.
-   **Estimated time:** 8 minutes
-   **Question type:** Short answer / operational decision
-   **Question prompt:** An engineer proposes changing control plane
    versus data plane after one incident observation. What measurements
    and guardrails should be required before approving the change?
-   **Model answer:** Require timestamped baseline and post-change
    metrics, affected SLOs, a bounded hypothesis, a reversible change
    plan, a stop/rollback threshold and a verification owner. Test
    representative load/failure conditions in staging where possible;
    document residual risk.
-   **Common wrong answers/misconceptions:** Wrong answer 1: act on one
    sample. Wrong answer 2: approve a permanent policy change without
    owner or review date.
-   **Scoring rubric:** 5 points: measurement 2; safety/rollback 1;
    verification 1; governance 1.
-   **Source/coverage note:**
    01-production-cluster-architecture-and-control-plane.md --- control
    plane versus data plane
-   **Version note:** \[VERIFY\] exact policy behavior before rollout.

## Unit 2 --- Namespaces, resource quotas, and limit ranges

### U02-SA-01 --- Unit 2 --- Namespaces, resource quotas, and limit ranges

-   **Unit/category:** Unit 2 --- Namespaces, resource quotas, and limit
    ranges
-   **Level:** L1
-   **Objective tested:** Explain the mechanism and operational
    consequence of namespace scope versus security isolation.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Namespace scope versus security isolation.
    Explain the mechanism, the trade-off, and one failure mode.
-   **Model answer:** Explain namespace scope versus security isolation
    by defining the mechanism, identifying the responsible Kubernetes
    layer/resource, and stating one production implication. Validate
    with the relevant object status/events rather than assuming the
    declared configuration proves runtime behavior.
-   **Common wrong answers/misconceptions:** Common misconceptions: CPU
    limits can throttle while memory-limit breach can OOM; namespace
    quota is not node capacity. These fail because they collapse
    distinct mechanisms or claim guarantees beyond the
    resource/component boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:**
    02-namespaces-resource-quotas-and-limit-ranges.md --- namespace
    scope versus security isolation
-   **Version note:** Not version-sensitive

### U02-SA-02 --- Unit 2 --- Namespaces, resource quotas, and limit ranges

-   **Unit/category:** Unit 2 --- Namespaces, resource quotas, and limit
    ranges
-   **Level:** L2
-   **Objective tested:** Explain the mechanism and operational
    consequence of requests and limits for CPU versus memory.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Requests and limits for cpu versus memory.
    Explain the mechanism, the trade-off, and one failure mode.
-   **Model answer:** The distinction is operational: requests and
    limits for CPU versus memory. Inspect the relevant API object, its
    conditions/events and the component that owns the decision. A
    configuration setting is not a substitute for evidence that the
    intended behavior occurred.
-   **Common wrong answers/misconceptions:** Common misconceptions:
    namespace quota is not node capacity; requests inform scheduling.
    These fail because they collapse distinct mechanisms or claim
    guarantees beyond the resource/component boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:**
    02-namespaces-resource-quotas-and-limit-ranges.md --- requests and
    limits for CPU versus memory
-   **Version note:** Not version-sensitive

### U02-SA-03 --- Unit 2 --- Namespaces, resource quotas, and limit ranges

-   **Unit/category:** Unit 2 --- Namespaces, resource quotas, and limit
    ranges
-   **Level:** L3
-   **Objective tested:** Explain the mechanism and operational
    consequence of ResourceQuota versus LimitRange.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Resourcequota versus limitrange. Explain the
    mechanism, the trade-off, and one failure mode.
-   **Model answer:** Use a failure model first: ResourceQuota versus
    LimitRange. State what the mechanism guarantees, what it does not
    guarantee, and which evidence would falsify your initial hypothesis.
    Record a measurable verification signal and rollback boundary.
-   **Common wrong answers/misconceptions:** Common misconceptions:
    requests inform scheduling; CPU limits can throttle while
    memory-limit breach can OOM. These fail because they collapse
    distinct mechanisms or claim guarantees beyond the
    resource/component boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:**
    02-namespaces-resource-quotas-and-limit-ranges.md --- ResourceQuota
    versus LimitRange
-   **Version note:** Not version-sensitive

### U02-MCQ-01 --- Unit 2 --- Namespaces, resource quotas, and limit ranges

-   **Unit/category:** Unit 2 --- Namespaces, resource quotas, and limit
    ranges
-   **Level:** L1
-   **Objective tested:** Choose an evidence-based operational response
    to quota denial during surge.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which response best addresses quota denial
    during surge? Options: A. Make the broadest change immediately.; B.
    Inspect the owning resource status/events and confirm scope before
    changing state.; C. Delete the namespace.; D. Assume the symptom
    uniquely proves one root cause.
-   **Model answer:** A is incorrect (Make the broadest change
    immediately.): a broad immediate change skips diagnosis and may
    enlarge blast radius.; B is best (Inspect the owning resource
    status/events and confirm scope before changing state.): Evidence
    from the owning resource and event stream narrows the differential
    while preserving state.; C is incorrect (Delete the namespace.):
    deleting the namespace is destructive and unrelated to an
    evidence-first diagnosis.; D is incorrect (Assume the symptom
    uniquely proves one root cause.): a symptom rarely proves one unique
    root cause without corroborating evidence..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    B is the only best answer.
-   **Source/coverage note:**
    02-namespaces-resource-quotas-and-limit-ranges.md --- namespace
    scope versus security isolation
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U02-MCQ-02 --- Unit 2 --- Namespaces, resource quotas, and limit ranges

-   **Unit/category:** Unit 2 --- Namespaces, resource quotas, and limit
    ranges
-   **Level:** L2
-   **Objective tested:** Choose an evidence-based operational response
    to LimitRange minimum request rejection.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which statement about requests and limits for
    CPU versus memory is most accurate? Options: A. requests inform
    scheduling; B. CPU limits can throttle while memory-limit breach can
    OOM; C. namespace quota is not node capacity; D. The mechanism
    guarantees every dependent application outcome.
-   **Model answer:** A is incorrect (requests inform scheduling): this
    statement does not correctly express the lesson's mechanism or
    guarantee; it conflates a distinct control or overstates what the
    component ensures.; B is best (CPU limits can throttle while
    memory-limit breach can OOM): The correct distinction is the
    boundary described in the lesson; application-level correctness
    still requires independent verification.; C is incorrect (namespace
    quota is not node capacity): this statement does not correctly
    express the lesson's mechanism or guarantee; it conflates a distinct
    control or overstates what the component ensures.; D is incorrect
    (The mechanism guarantees every dependent application outcome.):
    this statement does not correctly express the lesson's mechanism or
    guarantee; it conflates a distinct control or overstates what the
    component ensures..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    B is the only best answer.
-   **Source/coverage note:**
    02-namespaces-resource-quotas-and-limit-ranges.md --- requests and
    limits for CPU versus memory
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U02-MCQ-03 --- Unit 2 --- Namespaces, resource quotas, and limit ranges

-   **Unit/category:** Unit 2 --- Namespaces, resource quotas, and limit
    ranges
-   **Level:** L3
-   **Objective tested:** Choose an evidence-based operational response
    to capacity fairness across teams.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which evidence is strongest before changing
    policy for capacity fairness across teams? Options: A. A single
    screenshot without timestamp.; B. Only the desired-state
    manifest.; C. Correlated status, events, recent changes,
    capacity/dependency evidence and an explicit SLO impact.; D. A guess
    based on a similar incident.
-   **Model answer:** A is incorrect (A single screenshot without
    timestamp.): a screenshot alone lacks the correlated status, event
    and timeline evidence needed for diagnosis.; B is incorrect (Only
    the desired-state manifest.): desired state alone does not prove
    observed runtime behavior or root cause.; C is best (Correlated
    status, events, recent changes, capacity/dependency evidence and an
    explicit SLO impact.): Correlated evidence supports a differential
    and helps select a scoped reversible mitigation.; D is incorrect (A
    guess based on a similar incident.): guessing from a similar
    incident is not evidence for this cluster..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    C is the only best answer.
-   **Source/coverage note:**
    02-namespaces-resource-quotas-and-limit-ranges.md --- ResourceQuota
    versus LimitRange
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U02-OUT-01 --- Unit 2 --- Namespaces, resource quotas, and limit ranges

-   **Unit/category:** Unit 2 --- Namespaces, resource quotas, and limit
    ranges
-   **Level:** L2
-   **Objective tested:** Interpret a symptom without overstating what
    it proves about namespace scope versus security isolation.
-   **Estimated time:** 7 minutes
-   **Question type:** Output interpretation
-   **Question prompt:** **Illustrative output --- not observed
    execution.** Scenario: quota denial during surge. Assume a current
    namespace/context is confirmed. The only evidence available is this
    symptom; no additional root-cause evidence has been supplied. State
    what can be concluded and what to inspect next.
-   **Model answer:** The observation supports investigation of quota
    denial during surge, but does not uniquely establish root cause.
    Inspect the relevant object status/conditions, timestamped events,
    recent changes and the adjacent layer: requests inform scheduling.
    If the next evidence remains ambiguous, keep competing hypotheses
    open and perform a low-risk read-only test before mutation.
-   **Common wrong answers/misconceptions:** Wrong answer 1: state a
    definitive root cause from a symptom alone. Wrong answer 2: perform
    a destructive change before collecting object/event evidence.
-   **Scoring rubric:** 4 points: observed fact 1; bounded inference 1;
    next evidence 1; safe action 1.
-   **Source/coverage note:**
    02-namespaces-resource-quotas-and-limit-ranges.md --- quota denial
    during surge
-   **Version note:** \[VERIFY\] all sample output is illustrative and
    command fields vary by version.

### U02-OUT-02 --- Unit 2 --- Namespaces, resource quotas, and limit ranges

-   **Unit/category:** Unit 2 --- Namespaces, resource quotas, and limit
    ranges
-   **Level:** L3
-   **Objective tested:** Interpret a symptom without overstating what
    it proves about requests and limits for CPU versus memory.
-   **Estimated time:** 7 minutes
-   **Question type:** Output interpretation
-   **Question prompt:** **Illustrative output --- not observed
    execution.** Scenario: LimitRange minimum request rejection. Assume
    a current namespace/context is confirmed. The only evidence
    available is this symptom; no additional root-cause evidence has
    been supplied. State what can be concluded and what to inspect next.
-   **Model answer:** The observation supports investigation of
    LimitRange minimum request rejection, but does not uniquely
    establish root cause. Inspect the relevant object status/conditions,
    timestamped events, recent changes and the adjacent layer: CPU
    limits can throttle while memory-limit breach can OOM. If the next
    evidence remains ambiguous, keep competing hypotheses open and
    perform a low-risk read-only test before mutation.
-   **Common wrong answers/misconceptions:** Wrong answer 1: state a
    definitive root cause from a symptom alone. Wrong answer 2: perform
    a destructive change before collecting object/event evidence.
-   **Scoring rubric:** 4 points: observed fact 1; bounded inference 1;
    next evidence 1; safe action 1.
-   **Source/coverage note:**
    02-namespaces-resource-quotas-and-limit-ranges.md --- LimitRange
    minimum request rejection
-   **Version note:** \[VERIFY\] all sample output is illustrative and
    command fields vary by version.

### U02-MAN-01 --- Unit 2 --- Namespaces, resource quotas, and limit ranges

-   **Unit/category:** Unit 2 --- Namespaces, resource quotas, and limit
    ranges

-   **Level:** L2

-   **Objective tested:** Find at least three independent defects in a
    namespaces, resource quotas, and limit ranges configuration.

-   **Estimated time:** 10 minutes

-   **Question type:** Manifest review

-   **Question prompt:** Review this **intentionally defective training
    fixture** and identify at least three independent defects/risks.
    Give a correction plan and verification evidence. Do not apply it
    as-is.

    ``` yaml
    apiVersion: v1
    kind: Pod
    metadata: {name: etl, namespace: etl}
    spec:
      containers:
      - name: job
        image: etl:latest
        resources:
          requests: {cpu: "0", memory: 64Mi}
          limits: {cpu: "4", memory: 64Mi}
    ```

-   **Model answer:** Risks: zero CPU request is misleading and may fail
    validation/policy; memory request equals a low limit and may OOM a
    real ETL workload; large CPU limit can cause quota
    pressure/throttling; image tag is mutable. Set measured positive
    requests, choose justified limits, pin image, and check
    ResourceQuota/LimitRange plus peak memory. Verify admission and run
    under representative input.

-   **Common wrong answers/misconceptions:** Wrong answer 1: treat a
    YAML parse as proof of semantic correctness. Wrong answer 2: remove
    all controls to make the workload proceed. Wrong answer 3: give a
    correction without verification.

-   **Scoring rubric:** 6 points: three independent defects 3; precise
    fixes 1; verification 1; safety/rollback 1.

-   **Source/coverage note:**
    02-namespaces-resource-quotas-and-limit-ranges.md --- ResourceQuota
    versus LimitRange

-   **Version note:** \[VERIFY\] intentionally defective excerpt;
    validate API fields and defaults against target version.

### U02-MAN-02 --- Unit 2 --- Namespaces, resource quotas, and limit ranges

-   **Unit/category:** Unit 2 --- Namespaces, resource quotas, and limit
    ranges

-   **Level:** L3

-   **Objective tested:** Find at least three independent defects in a
    namespaces, resource quotas, and limit ranges configuration.

-   **Estimated time:** 10 minutes

-   **Question type:** Manifest review

-   **Question prompt:** Review this **intentionally defective training
    fixture** and identify at least three independent defects/risks.
    Give a correction plan and verification evidence. Do not apply it
    as-is.

    ``` yaml
    apiVersion: v1
    kind: ResourceQuota
    metadata: {name: budget, namespace: etl}
    spec:
      hard:
        requests.cpu: "2"
        requests.memory: 2Gi
    ---
    apiVersion: v1
    kind: Pod
    metadata: {name: worker, namespace: etl}
    spec:
      containers:
      - name: worker
        image: worker:v1
    ```

-   **Model answer:** Risks: quota covers requests but workload omits
    explicit requests; no LimitRange defaults/bounds are shown;
    object-count or storage constraints may be absent; no evidence the
    budget matches measured batch needs. Define explicit resource
    requests and suitable limits, add an appropriate LimitRange if
    policy requires defaults, size quota against usage/headroom and
    inspect admission errors. Test a representative Pod and rollout.

-   **Common wrong answers/misconceptions:** Wrong answer 1: treat a
    YAML parse as proof of semantic correctness. Wrong answer 2: remove
    all controls to make the workload proceed. Wrong answer 3: give a
    correction without verification.

-   **Scoring rubric:** 6 points: three independent defects 3; precise
    fixes 1; verification 1; safety/rollback 1.

-   **Source/coverage note:**
    02-namespaces-resource-quotas-and-limit-ranges.md --- namespace
    scope versus security isolation

-   **Version note:** \[VERIFY\] intentionally defective excerpt;
    validate API fields and defaults against target version.

### U02-INC-01 --- Unit 2 --- Namespaces, resource quotas, and limit ranges

-   **Unit/category:** Unit 2 --- Namespaces, resource quotas, and limit
    ranges
-   **Level:** L3
-   **Objective tested:** Use evidence-first troubleshooting for quota
    blocks model API rollout.
-   **Estimated time:** 15 minutes
-   **Question type:** Incident/troubleshooting
-   **Question prompt:** quota blocks model API rollout. Describe scope
    and timeline, evidence to collect, competing hypotheses, a low-risk
    first test, scoped mitigation, verification, rollback/stop
    condition, and prevention.
-   **Model answer:** Confirm context, namespace, affected SLO and
    change window; capture object conditions/events/logs and recent
    changes. Investigate quota denial during surge and compare at least
    two plausible causes. Prefer read-only evidence first; apply only a
    scoped, reversible mitigation approved for the environment. Verify
    service-level behavior and object convergence, define a stop
    condition, and record the outcome/runbook follow-up.
-   **Common wrong answers/misconceptions:** Wrong answer 1: treat
    symptom as root cause. Wrong answer 2: make a cluster-wide change
    without blast-radius analysis. Wrong answer 3: declare recovery
    without SLO/object verification.
-   **Scoring rubric:** 8 points: scope/timeline 1; evidence 2;
    differential 1; low-risk test 1; scoped mitigation/stop 1;
    verification 1; prevention/handoff 1.
-   **Source/coverage note:**
    02-namespaces-resource-quotas-and-limit-ranges.md --- quota blocks
    model API rollout
-   **Version note:** \[VERIFY\] any destructive/provider-specific
    recovery action against exact release runbook.

### U02-DES-01 --- Unit 2 --- Namespaces, resource quotas, and limit ranges

-   **Unit/category:** Unit 2 --- Namespaces, resource quotas, and limit
    ranges
-   **Level:** L4
-   **Objective tested:** Design a production-ready approach for design
    multi-team resource governance with explicit trade-offs.
-   **Estimated time:** 18 minutes
-   **Question type:** Design
-   **Question prompt:** design multi-team resource governance. State
    constraints, compare at least two approaches, explain failure
    modes/cost/operability, and give a verification plan.
-   **Model answer:** Define the SLO, failure domains, data/security
    constraints and operating ownership. Approach A optimizes
    simplicity/cost but accepts tighter shared blast radius; approach B
    adds isolation or redundancy at higher capacity/operational cost.
    Select based on measured demand and explicit failure model. Include
    monitoring, rollback/stop criteria, staging rehearsal and a
    post-change verification signal.
-   **Common wrong answers/misconceptions:** Wrong answer 1: choose the
    most complex option without a risk case. Wrong answer 2: optimize
    cost without addressing failure domains. Wrong answer 3: rely on
    component presence rather than tested recovery.
-   **Scoring rubric:** 10 points: constraints/SLO 2; mechanism
    correctness 2; alternatives/trade-offs 2; failure handling 2;
    observability/verification 2.
-   **Source/coverage note:**
    02-namespaces-resource-quotas-and-limit-ranges.md --- expert/design
    topics
-   **Version note:** \[VERIFY\] implementation syntax and
    managed-provider behavior.

### U02-EXT-01 --- Unit 2 --- Namespaces, resource quotas, and limit ranges

-   **Unit/category:** Unit 2 --- Namespaces, resource quotas, and limit
    ranges
-   **Level:** L3
-   **Objective tested:** Evaluate a change proposal for namespace scope
    versus security isolation using production evidence.
-   **Estimated time:** 8 minutes
-   **Question type:** Short answer / operational decision
-   **Question prompt:** An engineer proposes changing namespace scope
    versus security isolation after one incident observation. What
    measurements and guardrails should be required before approving the
    change?
-   **Model answer:** Require timestamped baseline and post-change
    metrics, affected SLOs, a bounded hypothesis, a reversible change
    plan, a stop/rollback threshold and a verification owner. Test
    representative load/failure conditions in staging where possible;
    document residual risk.
-   **Common wrong answers/misconceptions:** Wrong answer 1: act on one
    sample. Wrong answer 2: approve a permanent policy change without
    owner or review date.
-   **Scoring rubric:** 5 points: measurement 2; safety/rollback 1;
    verification 1; governance 1.
-   **Source/coverage note:**
    02-namespaces-resource-quotas-and-limit-ranges.md --- namespace
    scope versus security isolation
-   **Version note:** \[VERIFY\] exact policy behavior before rollout.

## Unit 3 --- Probes, health checks, and workload recovery

### U03-SA-01 --- Unit 3 --- Probes, health checks, and workload recovery

-   **Unit/category:** Unit 3 --- Probes, health checks, and workload
    recovery
-   **Level:** L1
-   **Objective tested:** Explain the mechanism and operational
    consequence of readiness versus liveness versus startup.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Readiness versus liveness versus startup.
    Explain the mechanism, the trade-off, and one failure mode.
-   **Model answer:** Explain readiness versus liveness versus startup
    by defining the mechanism, identifying the responsible Kubernetes
    layer/resource, and stating one production implication. Validate
    with the relevant object status/events rather than assuming the
    declared configuration proves runtime behavior.
-   **Common wrong answers/misconceptions:** Common misconceptions:
    liveness may restart container; startup probe protects
    initialization window. These fail because they collapse distinct
    mechanisms or claim guarantees beyond the resource/component
    boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:**
    03-probes-health-checks-and-workload-recovery.md --- readiness
    versus liveness versus startup
-   **Version note:** Not version-sensitive

### U03-SA-02 --- Unit 3 --- Probes, health checks, and workload recovery

-   **Unit/category:** Unit 3 --- Probes, health checks, and workload
    recovery
-   **Level:** L2
-   **Objective tested:** Explain the mechanism and operational
    consequence of probe timing and false positives.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Probe timing and false positives. Explain the
    mechanism, the trade-off, and one failure mode.
-   **Model answer:** The distinction is operational: probe timing and
    false positives. Inspect the relevant API object, its
    conditions/events and the component that owns the decision. A
    configuration setting is not a substitute for evidence that the
    intended behavior occurred.
-   **Common wrong answers/misconceptions:** Common misconceptions:
    startup probe protects initialization window; readiness gates
    traffic. These fail because they collapse distinct mechanisms or
    claim guarantees beyond the resource/component boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:**
    03-probes-health-checks-and-workload-recovery.md --- probe timing
    and false positives
-   **Version note:** Not version-sensitive

### U03-SA-03 --- Unit 3 --- Probes, health checks, and workload recovery

-   **Unit/category:** Unit 3 --- Probes, health checks, and workload
    recovery
-   **Level:** L3
-   **Objective tested:** Explain the mechanism and operational
    consequence of dependency-aware health contracts.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Dependency-aware health contracts. Explain the
    mechanism, the trade-off, and one failure mode.
-   **Model answer:** Use a failure model first: dependency-aware health
    contracts. State what the mechanism guarantees, what it does not
    guarantee, and which evidence would falsify your initial hypothesis.
    Record a measurable verification signal and rollback boundary.
-   **Common wrong answers/misconceptions:** Common misconceptions:
    readiness gates traffic; liveness may restart container. These fail
    because they collapse distinct mechanisms or claim guarantees beyond
    the resource/component boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:**
    03-probes-health-checks-and-workload-recovery.md ---
    dependency-aware health contracts
-   **Version note:** Not version-sensitive

### U03-MCQ-01 --- Unit 3 --- Probes, health checks, and workload recovery

-   **Unit/category:** Unit 3 --- Probes, health checks, and workload
    recovery
-   **Level:** L1
-   **Objective tested:** Choose an evidence-based operational response
    to 503 liveness failures and restarts.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which response best addresses 503 liveness
    failures and restarts? Options: A. Make the broadest change
    immediately.; B. Inspect the owning resource status/events and
    confirm scope before changing state.; C. Delete the namespace.; D.
    Assume the symptom uniquely proves one root cause.
-   **Model answer:** A is incorrect (Make the broadest change
    immediately.): a broad immediate change skips diagnosis and may
    enlarge blast radius.; B is best (Inspect the owning resource
    status/events and confirm scope before changing state.): Evidence
    from the owning resource and event stream narrows the differential
    while preserving state.; C is incorrect (Delete the namespace.):
    deleting the namespace is destructive and unrelated to an
    evidence-first diagnosis.; D is incorrect (Assume the symptom
    uniquely proves one root cause.): a symptom rarely proves one unique
    root cause without corroborating evidence..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    B is the only best answer.
-   **Source/coverage note:**
    03-probes-health-checks-and-workload-recovery.md --- readiness
    versus liveness versus startup
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U03-MCQ-02 --- Unit 3 --- Probes, health checks, and workload recovery

-   **Unit/category:** Unit 3 --- Probes, health checks, and workload
    recovery
-   **Level:** L2
-   **Objective tested:** Choose an evidence-based operational response
    to Running but not Ready.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which statement about probe timing and false
    positives is most accurate? Options: A. readiness gates traffic; B.
    liveness may restart container; C. startup probe protects
    initialization window; D. The mechanism guarantees every dependent
    application outcome.
-   **Model answer:** A is incorrect (readiness gates traffic): this
    statement does not correctly express the lesson's mechanism or
    guarantee; it conflates a distinct control or overstates what the
    component ensures.; B is best (liveness may restart container): The
    correct distinction is the boundary described in the lesson;
    application-level correctness still requires independent
    verification.; C is incorrect (startup probe protects initialization
    window): this statement does not correctly express the lesson's
    mechanism or guarantee; it conflates a distinct control or
    overstates what the component ensures.; D is incorrect (The
    mechanism guarantees every dependent application outcome.): this
    statement does not correctly express the lesson's mechanism or
    guarantee; it conflates a distinct control or overstates what the
    component ensures..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    B is the only best answer.
-   **Source/coverage note:**
    03-probes-health-checks-and-workload-recovery.md --- probe timing
    and false positives
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U03-MCQ-03 --- Unit 3 --- Probes, health checks, and workload recovery

-   **Unit/category:** Unit 3 --- Probes, health checks, and workload
    recovery
-   **Level:** L3
-   **Objective tested:** Choose an evidence-based operational response
    to slow model initialization.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which evidence is strongest before changing
    policy for slow model initialization? Options: A. A single
    screenshot without timestamp.; B. Only the desired-state
    manifest.; C. Correlated status, events, recent changes,
    capacity/dependency evidence and an explicit SLO impact.; D. A guess
    based on a similar incident.
-   **Model answer:** A is incorrect (A single screenshot without
    timestamp.): a screenshot alone lacks the correlated status, event
    and timeline evidence needed for diagnosis.; B is incorrect (Only
    the desired-state manifest.): desired state alone does not prove
    observed runtime behavior or root cause.; C is best (Correlated
    status, events, recent changes, capacity/dependency evidence and an
    explicit SLO impact.): Correlated evidence supports a differential
    and helps select a scoped reversible mitigation.; D is incorrect (A
    guess based on a similar incident.): guessing from a similar
    incident is not evidence for this cluster..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    C is the only best answer.
-   **Source/coverage note:**
    03-probes-health-checks-and-workload-recovery.md ---
    dependency-aware health contracts
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U03-OUT-01 --- Unit 3 --- Probes, health checks, and workload recovery

-   **Unit/category:** Unit 3 --- Probes, health checks, and workload
    recovery
-   **Level:** L2
-   **Objective tested:** Interpret a symptom without overstating what
    it proves about readiness versus liveness versus startup.
-   **Estimated time:** 7 minutes
-   **Question type:** Output interpretation
-   **Question prompt:** **Illustrative output --- not observed
    execution.** Scenario: 503 liveness failures and restarts. Assume a
    current namespace/context is confirmed. The only evidence available
    is this symptom; no additional root-cause evidence has been
    supplied. State what can be concluded and what to inspect next.
-   **Model answer:** The observation supports investigation of 503
    liveness failures and restarts, but does not uniquely establish root
    cause. Inspect the relevant object status/conditions, timestamped
    events, recent changes and the adjacent layer: liveness may restart
    container. If the next evidence remains ambiguous, keep competing
    hypotheses open and perform a low-risk read-only test before
    mutation.
-   **Common wrong answers/misconceptions:** Wrong answer 1: state a
    definitive root cause from a symptom alone. Wrong answer 2: perform
    a destructive change before collecting object/event evidence.
-   **Scoring rubric:** 4 points: observed fact 1; bounded inference 1;
    next evidence 1; safe action 1.
-   **Source/coverage note:**
    03-probes-health-checks-and-workload-recovery.md --- 503 liveness
    failures and restarts
-   **Version note:** \[VERIFY\] all sample output is illustrative and
    command fields vary by version.

### U03-OUT-02 --- Unit 3 --- Probes, health checks, and workload recovery

-   **Unit/category:** Unit 3 --- Probes, health checks, and workload
    recovery
-   **Level:** L3
-   **Objective tested:** Interpret a symptom without overstating what
    it proves about probe timing and false positives.
-   **Estimated time:** 7 minutes
-   **Question type:** Output interpretation
-   **Question prompt:** **Illustrative output --- not observed
    execution.** Scenario: Running but not Ready. Assume a current
    namespace/context is confirmed. The only evidence available is this
    symptom; no additional root-cause evidence has been supplied. State
    what can be concluded and what to inspect next.
-   **Model answer:** The observation supports investigation of Running
    but not Ready, but does not uniquely establish root cause. Inspect
    the relevant object status/conditions, timestamped events, recent
    changes and the adjacent layer: startup probe protects
    initialization window. If the next evidence remains ambiguous, keep
    competing hypotheses open and perform a low-risk read-only test
    before mutation.
-   **Common wrong answers/misconceptions:** Wrong answer 1: state a
    definitive root cause from a symptom alone. Wrong answer 2: perform
    a destructive change before collecting object/event evidence.
-   **Scoring rubric:** 4 points: observed fact 1; bounded inference 1;
    next evidence 1; safe action 1.
-   **Source/coverage note:**
    03-probes-health-checks-and-workload-recovery.md --- Running but not
    Ready
-   **Version note:** \[VERIFY\] all sample output is illustrative and
    command fields vary by version.

### U03-MAN-01 --- Unit 3 --- Probes, health checks, and workload recovery

-   **Unit/category:** Unit 3 --- Probes, health checks, and workload
    recovery

-   **Level:** L2

-   **Objective tested:** Find at least three independent defects in a
    probes, health checks, and workload recovery configuration.

-   **Estimated time:** 10 minutes

-   **Question type:** Manifest review

-   **Question prompt:** Review this **intentionally defective training
    fixture** and identify at least three independent defects/risks.
    Give a correction plan and verification evidence. Do not apply it
    as-is.

    ``` yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata: {name: scorer}
    spec:
      replicas: 3
      selector: {matchLabels: {app: scorer}}
      template:
        metadata: {labels: {app: scorer}}
        spec:
          containers:
          - name: api
            image: scorer:v1
            livenessProbe:
              httpGet: {path: /health, port: 8080}
              periodSeconds: 5
              timeoutSeconds: 1
              failureThreshold: 1
    ```

-   **Model answer:** Risks: one short timeout/failure can restart the
    container; endpoint is unspecified and may deeply check remote
    dependencies; no readiness probe prevents explicit traffic gating;
    no startup protection for slow initialization. Separate local
    liveness from serving readiness, add startup protection if cold
    start warrants it, and tune timing from measured latency/jitter.
    Test dependency outage and cold start before rollout.

-   **Common wrong answers/misconceptions:** Wrong answer 1: treat a
    YAML parse as proof of semantic correctness. Wrong answer 2: remove
    all controls to make the workload proceed. Wrong answer 3: give a
    correction without verification.

-   **Scoring rubric:** 6 points: three independent defects 3; precise
    fixes 1; verification 1; safety/rollback 1.

-   **Source/coverage note:**
    03-probes-health-checks-and-workload-recovery.md ---
    dependency-aware health contracts

-   **Version note:** \[VERIFY\] intentionally defective excerpt;
    validate API fields and defaults against target version.

### U03-MAN-02 --- Unit 3 --- Probes, health checks, and workload recovery

-   **Unit/category:** Unit 3 --- Probes, health checks, and workload
    recovery

-   **Level:** L3

-   **Objective tested:** Find at least three independent defects in a
    probes, health checks, and workload recovery configuration.

-   **Estimated time:** 10 minutes

-   **Question type:** Manifest review

-   **Question prompt:** Review this **intentionally defective training
    fixture** and identify at least three independent defects/risks.
    Give a correction plan and verification evidence. Do not apply it
    as-is.

    ``` yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata: {name: model-api}
    spec:
      replicas: 2
      selector: {matchLabels: {app: model-api}}
      template:
        metadata: {labels: {app: model-api}}
        spec:
          containers:
          - name: api
            image: model-api:v2
            readinessProbe:
              httpGet: {path: /ready, port: 8000}
              initialDelaySeconds: 0
            livenessProbe:
              httpGet: {path: /ready, port: 8000}
              initialDelaySeconds: 5
    ```

-   **Model answer:** Risks: readiness and liveness share a
    startup-dependent endpoint; liveness may restart
    healthy-but-initializing process; no startup probe/timing budget for
    slow model load; no timeout/threshold values are explicitly
    reviewed. Use distinct contracts, startup protection if justified,
    readiness false until safe to serve, and liveness for local
    unrecoverable failure. Validate cold-start and dependency-failure
    behavior.

-   **Common wrong answers/misconceptions:** Wrong answer 1: treat a
    YAML parse as proof of semantic correctness. Wrong answer 2: remove
    all controls to make the workload proceed. Wrong answer 3: give a
    correction without verification.

-   **Scoring rubric:** 6 points: three independent defects 3; precise
    fixes 1; verification 1; safety/rollback 1.

-   **Source/coverage note:**
    03-probes-health-checks-and-workload-recovery.md --- readiness
    versus liveness versus startup

-   **Version note:** \[VERIFY\] intentionally defective excerpt;
    validate API fields and defaults against target version.

### U03-INC-01 --- Unit 3 --- Probes, health checks, and workload recovery

-   **Unit/category:** Unit 3 --- Probes, health checks, and workload
    recovery
-   **Level:** L3
-   **Objective tested:** Use evidence-first troubleshooting for
    feature-store outage triggers restarts.
-   **Estimated time:** 15 minutes
-   **Question type:** Incident/troubleshooting
-   **Question prompt:** feature-store outage triggers restarts.
    Describe scope and timeline, evidence to collect, competing
    hypotheses, a low-risk first test, scoped mitigation, verification,
    rollback/stop condition, and prevention.
-   **Model answer:** Confirm context, namespace, affected SLO and
    change window; capture object conditions/events/logs and recent
    changes. Investigate 503 liveness failures and restarts and compare
    at least two plausible causes. Prefer read-only evidence first;
    apply only a scoped, reversible mitigation approved for the
    environment. Verify service-level behavior and object convergence,
    define a stop condition, and record the outcome/runbook follow-up.
-   **Common wrong answers/misconceptions:** Wrong answer 1: treat
    symptom as root cause. Wrong answer 2: make a cluster-wide change
    without blast-radius analysis. Wrong answer 3: declare recovery
    without SLO/object verification.
-   **Scoring rubric:** 8 points: scope/timeline 1; evidence 2;
    differential 1; low-risk test 1; scoped mitigation/stop 1;
    verification 1; prevention/handoff 1.
-   **Source/coverage note:**
    03-probes-health-checks-and-workload-recovery.md --- feature-store
    outage triggers restarts
-   **Version note:** \[VERIFY\] any destructive/provider-specific
    recovery action against exact release runbook.

### U03-DES-01 --- Unit 3 --- Probes, health checks, and workload recovery

-   **Unit/category:** Unit 3 --- Probes, health checks, and workload
    recovery
-   **Level:** L4
-   **Objective tested:** Design a production-ready approach for design
    health contracts with explicit trade-offs.
-   **Estimated time:** 18 minutes
-   **Question type:** Design
-   **Question prompt:** design health contracts. State constraints,
    compare at least two approaches, explain failure
    modes/cost/operability, and give a verification plan.
-   **Model answer:** Define the SLO, failure domains, data/security
    constraints and operating ownership. Approach A optimizes
    simplicity/cost but accepts tighter shared blast radius; approach B
    adds isolation or redundancy at higher capacity/operational cost.
    Select based on measured demand and explicit failure model. Include
    monitoring, rollback/stop criteria, staging rehearsal and a
    post-change verification signal.
-   **Common wrong answers/misconceptions:** Wrong answer 1: choose the
    most complex option without a risk case. Wrong answer 2: optimize
    cost without addressing failure domains. Wrong answer 3: rely on
    component presence rather than tested recovery.
-   **Scoring rubric:** 10 points: constraints/SLO 2; mechanism
    correctness 2; alternatives/trade-offs 2; failure handling 2;
    observability/verification 2.
-   **Source/coverage note:**
    03-probes-health-checks-and-workload-recovery.md --- expert/design
    topics
-   **Version note:** \[VERIFY\] implementation syntax and
    managed-provider behavior.

### U03-EXT-01 --- Unit 3 --- Probes, health checks, and workload recovery

-   **Unit/category:** Unit 3 --- Probes, health checks, and workload
    recovery
-   **Level:** L3
-   **Objective tested:** Evaluate a change proposal for readiness
    versus liveness versus startup using production evidence.
-   **Estimated time:** 8 minutes
-   **Question type:** Short answer / operational decision
-   **Question prompt:** An engineer proposes changing readiness versus
    liveness versus startup after one incident observation. What
    measurements and guardrails should be required before approving the
    change?
-   **Model answer:** Require timestamped baseline and post-change
    metrics, affected SLOs, a bounded hypothesis, a reversible change
    plan, a stop/rollback threshold and a verification owner. Test
    representative load/failure conditions in staging where possible;
    document residual risk.
-   **Common wrong answers/misconceptions:** Wrong answer 1: act on one
    sample. Wrong answer 2: approve a permanent policy change without
    owner or review date.
-   **Scoring rubric:** 5 points: measurement 2; safety/rollback 1;
    verification 1; governance 1.
-   **Source/coverage note:**
    03-probes-health-checks-and-workload-recovery.md --- readiness
    versus liveness versus startup
-   **Version note:** \[VERIFY\] exact policy behavior before rollout.

## Unit 4 --- Deployments, StatefulSets, Jobs, and CronJobs

### U04-SA-01 --- Unit 4 --- Deployments, StatefulSets, Jobs, and CronJobs

-   **Unit/category:** Unit 4 --- Deployments, StatefulSets, Jobs, and
    CronJobs
-   **Level:** L1
-   **Objective tested:** Explain the mechanism and operational
    consequence of choose controller by workload semantics.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Choose controller by workload semantics.
    Explain the mechanism, the trade-off, and one failure mode.
-   **Model answer:** Explain choose controller by workload semantics by
    defining the mechanism, identifying the responsible Kubernetes
    layer/resource, and stating one production implication. Validate
    with the relevant object status/events rather than assuming the
    declared configuration proves runtime behavior.
-   **Common wrong answers/misconceptions:** Common misconceptions:
    StatefulSet gives stable identity/storage association; Job/CronJob
    success does not mean exactly-once side effects. These fail because
    they collapse distinct mechanisms or claim guarantees beyond the
    resource/component boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:**
    04-deployments-statefulsets-jobs-and-cronjobs-in-production.md ---
    choose controller by workload semantics
-   **Version note:** Not version-sensitive

### U04-SA-02 --- Unit 4 --- Deployments, StatefulSets, Jobs, and CronJobs

-   **Unit/category:** Unit 4 --- Deployments, StatefulSets, Jobs, and
    CronJobs
-   **Level:** L2
-   **Objective tested:** Explain the mechanism and operational
    consequence of rollback does not reverse external side effects.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Rollback does not reverse external side
    effects. Explain the mechanism, the trade-off, and one failure mode.
-   **Model answer:** The distinction is operational: rollback does not
    reverse external side effects. Inspect the relevant API object, its
    conditions/events and the component that owns the decision. A
    configuration setting is not a substitute for evidence that the
    intended behavior occurred.
-   **Common wrong answers/misconceptions:** Common misconceptions:
    Job/CronJob success does not mean exactly-once side effects;
    Deployment for interchangeable replicas. These fail because they
    collapse distinct mechanisms or claim guarantees beyond the
    resource/component boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:**
    04-deployments-statefulsets-jobs-and-cronjobs-in-production.md ---
    rollback does not reverse external side effects
-   **Version note:** Not version-sensitive

### U04-SA-03 --- Unit 4 --- Deployments, StatefulSets, Jobs, and CronJobs

-   **Unit/category:** Unit 4 --- Deployments, StatefulSets, Jobs, and
    CronJobs
-   **Level:** L3
-   **Objective tested:** Explain the mechanism and operational
    consequence of retries, concurrency, and idempotency.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Retries, concurrency, and idempotency. Explain
    the mechanism, the trade-off, and one failure mode.
-   **Model answer:** Use a failure model first: retries, concurrency,
    and idempotency. State what the mechanism guarantees, what it does
    not guarantee, and which evidence would falsify your initial
    hypothesis. Record a measurable verification signal and rollback
    boundary.
-   **Common wrong answers/misconceptions:** Common misconceptions:
    Deployment for interchangeable replicas; StatefulSet gives stable
    identity/storage association. These fail because they collapse
    distinct mechanisms or claim guarantees beyond the
    resource/component boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:**
    04-deployments-statefulsets-jobs-and-cronjobs-in-production.md ---
    retries, concurrency, and idempotency
-   **Version note:** Not version-sensitive

### U04-MCQ-01 --- Unit 4 --- Deployments, StatefulSets, Jobs, and CronJobs

-   **Unit/category:** Unit 4 --- Deployments, StatefulSets, Jobs, and
    CronJobs
-   **Level:** L1
-   **Objective tested:** Choose an evidence-based operational response
    to rollout timeout.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which response best addresses rollout timeout?
    Options: A. Make the broadest change immediately.; B. Inspect the
    owning resource status/events and confirm scope before changing
    state.; C. Delete the namespace.; D. Assume the symptom uniquely
    proves one root cause.
-   **Model answer:** A is incorrect (Make the broadest change
    immediately.): a broad immediate change skips diagnosis and may
    enlarge blast radius.; B is best (Inspect the owning resource
    status/events and confirm scope before changing state.): Evidence
    from the owning resource and event stream narrows the differential
    while preserving state.; C is incorrect (Delete the namespace.):
    deleting the namespace is destructive and unrelated to an
    evidence-first diagnosis.; D is incorrect (Assume the symptom
    uniquely proves one root cause.): a symptom rarely proves one unique
    root cause without corroborating evidence..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    B is the only best answer.
-   **Source/coverage note:**
    04-deployments-statefulsets-jobs-and-cronjobs-in-production.md ---
    choose controller by workload semantics
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U04-MCQ-02 --- Unit 4 --- Deployments, StatefulSets, Jobs, and CronJobs

-   **Unit/category:** Unit 4 --- Deployments, StatefulSets, Jobs, and
    CronJobs
-   **Level:** L2
-   **Objective tested:** Choose an evidence-based operational response
    to overlapping scheduled Jobs.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which statement about rollback does not reverse
    external side effects is most accurate? Options: A. Deployment for
    interchangeable replicas; B. StatefulSet gives stable
    identity/storage association; C. Job/CronJob success does not mean
    exactly-once side effects; D. The mechanism guarantees every
    dependent application outcome.
-   **Model answer:** A is incorrect (Deployment for interchangeable
    replicas): this statement does not correctly express the lesson's
    mechanism or guarantee; it conflates a distinct control or
    overstates what the component ensures.; B is best (StatefulSet gives
    stable identity/storage association): The correct distinction is the
    boundary described in the lesson; application-level correctness
    still requires independent verification.; C is incorrect
    (Job/CronJob success does not mean exactly-once side effects): this
    statement does not correctly express the lesson's mechanism or
    guarantee; it conflates a distinct control or overstates what the
    component ensures.; D is incorrect (The mechanism guarantees every
    dependent application outcome.): this statement does not correctly
    express the lesson's mechanism or guarantee; it conflates a distinct
    control or overstates what the component ensures..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    B is the only best answer.
-   **Source/coverage note:**
    04-deployments-statefulsets-jobs-and-cronjobs-in-production.md ---
    rollback does not reverse external side effects
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U04-MCQ-03 --- Unit 4 --- Deployments, StatefulSets, Jobs, and CronJobs

-   **Unit/category:** Unit 4 --- Deployments, StatefulSets, Jobs, and
    CronJobs
-   **Level:** L3
-   **Objective tested:** Choose an evidence-based operational response
    to StatefulSet stable identity and storage.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which evidence is strongest before changing
    policy for StatefulSet stable identity and storage? Options: A. A
    single screenshot without timestamp.; B. Only the desired-state
    manifest.; C. Correlated status, events, recent changes,
    capacity/dependency evidence and an explicit SLO impact.; D. A guess
    based on a similar incident.
-   **Model answer:** A is incorrect (A single screenshot without
    timestamp.): a screenshot alone lacks the correlated status, event
    and timeline evidence needed for diagnosis.; B is incorrect (Only
    the desired-state manifest.): desired state alone does not prove
    observed runtime behavior or root cause.; C is best (Correlated
    status, events, recent changes, capacity/dependency evidence and an
    explicit SLO impact.): Correlated evidence supports a differential
    and helps select a scoped reversible mitigation.; D is incorrect (A
    guess based on a similar incident.): guessing from a similar
    incident is not evidence for this cluster..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    C is the only best answer.
-   **Source/coverage note:**
    04-deployments-statefulsets-jobs-and-cronjobs-in-production.md ---
    retries, concurrency, and idempotency
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U04-OUT-01 --- Unit 4 --- Deployments, StatefulSets, Jobs, and CronJobs

-   **Unit/category:** Unit 4 --- Deployments, StatefulSets, Jobs, and
    CronJobs
-   **Level:** L2
-   **Objective tested:** Interpret a symptom without overstating what
    it proves about choose controller by workload semantics.
-   **Estimated time:** 7 minutes
-   **Question type:** Output interpretation
-   **Question prompt:** **Illustrative output --- not observed
    execution.** Scenario: rollout timeout. Assume a current
    namespace/context is confirmed. The only evidence available is this
    symptom; no additional root-cause evidence has been supplied. State
    what can be concluded and what to inspect next.
-   **Model answer:** The observation supports investigation of rollout
    timeout, but does not uniquely establish root cause. Inspect the
    relevant object status/conditions, timestamped events, recent
    changes and the adjacent layer: Job/CronJob success does not mean
    exactly-once side effects. If the next evidence remains ambiguous,
    keep competing hypotheses open and perform a low-risk read-only test
    before mutation.
-   **Common wrong answers/misconceptions:** Wrong answer 1: state a
    definitive root cause from a symptom alone. Wrong answer 2: perform
    a destructive change before collecting object/event evidence.
-   **Scoring rubric:** 4 points: observed fact 1; bounded inference 1;
    next evidence 1; safe action 1.
-   **Source/coverage note:**
    04-deployments-statefulsets-jobs-and-cronjobs-in-production.md ---
    rollout timeout
-   **Version note:** \[VERIFY\] all sample output is illustrative and
    command fields vary by version.

### U04-OUT-02 --- Unit 4 --- Deployments, StatefulSets, Jobs, and CronJobs

-   **Unit/category:** Unit 4 --- Deployments, StatefulSets, Jobs, and
    CronJobs
-   **Level:** L3
-   **Objective tested:** Interpret a symptom without overstating what
    it proves about rollback does not reverse external side effects.
-   **Estimated time:** 7 minutes
-   **Question type:** Output interpretation
-   **Question prompt:** **Illustrative output --- not observed
    execution.** Scenario: overlapping scheduled Jobs. Assume a current
    namespace/context is confirmed. The only evidence available is this
    symptom; no additional root-cause evidence has been supplied. State
    what can be concluded and what to inspect next.
-   **Model answer:** The observation supports investigation of
    overlapping scheduled Jobs, but does not uniquely establish root
    cause. Inspect the relevant object status/conditions, timestamped
    events, recent changes and the adjacent layer: Deployment for
    interchangeable replicas. If the next evidence remains ambiguous,
    keep competing hypotheses open and perform a low-risk read-only test
    before mutation.
-   **Common wrong answers/misconceptions:** Wrong answer 1: state a
    definitive root cause from a symptom alone. Wrong answer 2: perform
    a destructive change before collecting object/event evidence.
-   **Scoring rubric:** 4 points: observed fact 1; bounded inference 1;
    next evidence 1; safe action 1.
-   **Source/coverage note:**
    04-deployments-statefulsets-jobs-and-cronjobs-in-production.md ---
    overlapping scheduled Jobs
-   **Version note:** \[VERIFY\] all sample output is illustrative and
    command fields vary by version.

### U04-MAN-01 --- Unit 4 --- Deployments, StatefulSets, Jobs, and CronJobs

-   **Unit/category:** Unit 4 --- Deployments, StatefulSets, Jobs, and
    CronJobs

-   **Level:** L2

-   **Objective tested:** Find at least three independent defects in a
    deployments, statefulsets, jobs, and cronjobs configuration.

-   **Estimated time:** 10 minutes

-   **Question type:** Manifest review

-   **Question prompt:** Review this **intentionally defective training
    fixture** and identify at least three independent defects/risks.
    Give a correction plan and verification evidence. Do not apply it
    as-is.

    ``` yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata: {name: scorer}
    spec:
      replicas: 3
      selector: {matchLabels: {app: scorer}}
      strategy:
        rollingUpdate: {maxSurge: 1, maxUnavailable: 100%}
      template:
        metadata: {labels: {app: model}}
        spec:
          containers:
          - name: scorer
            image: scorer:latest
    ```

-   **Model answer:** Risks: selector/template labels mismatch; 100%
    maxUnavailable can take all replicas out during rollout; mutable
    image tag makes rollback/reproduction uncertain; no resource/probe
    contract. Match labels, pin image, choose surge/unavailable values
    against SLO and quota headroom, add health/resource settings, and
    verify rollout plus serving traffic.

-   **Common wrong answers/misconceptions:** Wrong answer 1: treat a
    YAML parse as proof of semantic correctness. Wrong answer 2: remove
    all controls to make the workload proceed. Wrong answer 3: give a
    correction without verification.

-   **Scoring rubric:** 6 points: three independent defects 3; precise
    fixes 1; verification 1; safety/rollback 1.

-   **Source/coverage note:**
    04-deployments-statefulsets-jobs-and-cronjobs-in-production.md ---
    retries, concurrency, and idempotency

-   **Version note:** \[VERIFY\] intentionally defective excerpt;
    validate API fields and defaults against target version.

### U04-MAN-02 --- Unit 4 --- Deployments, StatefulSets, Jobs, and CronJobs

-   **Unit/category:** Unit 4 --- Deployments, StatefulSets, Jobs, and
    CronJobs

-   **Level:** L3

-   **Objective tested:** Find at least three independent defects in a
    deployments, statefulsets, jobs, and cronjobs configuration.

-   **Estimated time:** 10 minutes

-   **Question type:** Manifest review

-   **Question prompt:** Review this **intentionally defective training
    fixture** and identify at least three independent defects/risks.
    Give a correction plan and verification evidence. Do not apply it
    as-is.

    ``` yaml
    apiVersion: batch/v1
    kind: CronJob
    metadata: {name: nightly-reconcile, namespace: data}
    spec:
      schedule: "*/5 * * * *"
      concurrencyPolicy: Allow
      jobTemplate:
        spec:
          template:
            spec:
              restartPolicy: Never
              containers:
              - name: reconcile
                image: reconcile:latest
    ```

-   **Model answer:** Risks: frequent schedule plus `Allow` permits
    overlap; work is not described as idempotent/checkpointed; mutable
    image tag harms repeatability; retries/deadline/history/alerts are
    not bounded or documented. Choose concurrency policy from semantics,
    implement idempotency, bound retries/deadlines, pin image and
    monitor outcomes. Test overlapping and missed-schedule scenarios.

-   **Common wrong answers/misconceptions:** Wrong answer 1: treat a
    YAML parse as proof of semantic correctness. Wrong answer 2: remove
    all controls to make the workload proceed. Wrong answer 3: give a
    correction without verification.

-   **Scoring rubric:** 6 points: three independent defects 3; precise
    fixes 1; verification 1; safety/rollback 1.

-   **Source/coverage note:**
    04-deployments-statefulsets-jobs-and-cronjobs-in-production.md ---
    choose controller by workload semantics

-   **Version note:** \[VERIFY\] intentionally defective excerpt;
    validate API fields and defaults against target version.

### U04-INC-01 --- Unit 4 --- Deployments, StatefulSets, Jobs, and CronJobs

-   **Unit/category:** Unit 4 --- Deployments, StatefulSets, Jobs, and
    CronJobs
-   **Level:** L3
-   **Objective tested:** Use evidence-first troubleshooting for schema
    migration makes rollback unsafe.
-   **Estimated time:** 15 minutes
-   **Question type:** Incident/troubleshooting
-   **Question prompt:** schema migration makes rollback unsafe.
    Describe scope and timeline, evidence to collect, competing
    hypotheses, a low-risk first test, scoped mitigation, verification,
    rollback/stop condition, and prevention.
-   **Model answer:** Confirm context, namespace, affected SLO and
    change window; capture object conditions/events/logs and recent
    changes. Investigate rollout timeout and compare at least two
    plausible causes. Prefer read-only evidence first; apply only a
    scoped, reversible mitigation approved for the environment. Verify
    service-level behavior and object convergence, define a stop
    condition, and record the outcome/runbook follow-up.
-   **Common wrong answers/misconceptions:** Wrong answer 1: treat
    symptom as root cause. Wrong answer 2: make a cluster-wide change
    without blast-radius analysis. Wrong answer 3: declare recovery
    without SLO/object verification.
-   **Scoring rubric:** 8 points: scope/timeline 1; evidence 2;
    differential 1; low-risk test 1; scoped mitigation/stop 1;
    verification 1; prevention/handoff 1.
-   **Source/coverage note:**
    04-deployments-statefulsets-jobs-and-cronjobs-in-production.md ---
    schema migration makes rollback unsafe
-   **Version note:** \[VERIFY\] any destructive/provider-specific
    recovery action against exact release runbook.

### U04-DES-01 --- Unit 4 --- Deployments, StatefulSets, Jobs, and CronJobs

-   **Unit/category:** Unit 4 --- Deployments, StatefulSets, Jobs, and
    CronJobs
-   **Level:** L4
-   **Objective tested:** Design a production-ready approach for design
    controllers for API, queue, ETL and nightly job with explicit
    trade-offs.
-   **Estimated time:** 18 minutes
-   **Question type:** Design
-   **Question prompt:** design controllers for API, queue, ETL and
    nightly job. State constraints, compare at least two approaches,
    explain failure modes/cost/operability, and give a verification
    plan.
-   **Model answer:** Define the SLO, failure domains, data/security
    constraints and operating ownership. Approach A optimizes
    simplicity/cost but accepts tighter shared blast radius; approach B
    adds isolation or redundancy at higher capacity/operational cost.
    Select based on measured demand and explicit failure model. Include
    monitoring, rollback/stop criteria, staging rehearsal and a
    post-change verification signal.
-   **Common wrong answers/misconceptions:** Wrong answer 1: choose the
    most complex option without a risk case. Wrong answer 2: optimize
    cost without addressing failure domains. Wrong answer 3: rely on
    component presence rather than tested recovery.
-   **Scoring rubric:** 10 points: constraints/SLO 2; mechanism
    correctness 2; alternatives/trade-offs 2; failure handling 2;
    observability/verification 2.
-   **Source/coverage note:**
    04-deployments-statefulsets-jobs-and-cronjobs-in-production.md ---
    expert/design topics
-   **Version note:** \[VERIFY\] implementation syntax and
    managed-provider behavior.

### U04-EXT-01 --- Unit 4 --- Deployments, StatefulSets, Jobs, and CronJobs

-   **Unit/category:** Unit 4 --- Deployments, StatefulSets, Jobs, and
    CronJobs
-   **Level:** L3
-   **Objective tested:** Evaluate a change proposal for choose
    controller by workload semantics using production evidence.
-   **Estimated time:** 8 minutes
-   **Question type:** Short answer / operational decision
-   **Question prompt:** An engineer proposes changing choose controller
    by workload semantics after one incident observation. What
    measurements and guardrails should be required before approving the
    change?
-   **Model answer:** Require timestamped baseline and post-change
    metrics, affected SLOs, a bounded hypothesis, a reversible change
    plan, a stop/rollback threshold and a verification owner. Test
    representative load/failure conditions in staging where possible;
    document residual risk.
-   **Common wrong answers/misconceptions:** Wrong answer 1: act on one
    sample. Wrong answer 2: approve a permanent policy change without
    owner or review date.
-   **Scoring rubric:** 5 points: measurement 2; safety/rollback 1;
    verification 1; governance 1.
-   **Source/coverage note:**
    04-deployments-statefulsets-jobs-and-cronjobs-in-production.md ---
    choose controller by workload semantics
-   **Version note:** \[VERIFY\] exact policy behavior before rollout.

## Unit 5 --- Pod disruption budgets and graceful shutdown

### U05-SA-01 --- Unit 5 --- Pod disruption budgets and graceful shutdown

-   **Unit/category:** Unit 5 --- Pod disruption budgets and graceful
    shutdown
-   **Level:** L1
-   **Objective tested:** Explain the mechanism and operational
    consequence of voluntary versus involuntary disruption.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Voluntary versus involuntary disruption.
    Explain the mechanism, the trade-off, and one failure mode.
-   **Model answer:** Explain voluntary versus involuntary disruption by
    defining the mechanism, identifying the responsible Kubernetes
    layer/resource, and stating one production implication. Validate
    with the relevant object status/events rather than assuming the
    declared configuration proves runtime behavior.
-   **Common wrong answers/misconceptions:** Common misconceptions: PDB
    cannot prevent all failures; shutdown must bound and checkpoint
    work. These fail because they collapse distinct mechanisms or claim
    guarantees beyond the resource/component boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:**
    05-pod-disruption-budgets-and-graceful-shutdown.md --- voluntary
    versus involuntary disruption
-   **Version note:** Not version-sensitive

### U05-SA-02 --- Unit 5 --- Pod disruption budgets and graceful shutdown

-   **Unit/category:** Unit 5 --- Pod disruption budgets and graceful
    shutdown
-   **Level:** L2
-   **Objective tested:** Explain the mechanism and operational
    consequence of PDB boundary and blocked drain.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Pdb boundary and blocked drain. Explain the
    mechanism, the trade-off, and one failure mode.
-   **Model answer:** The distinction is operational: PDB boundary and
    blocked drain. Inspect the relevant API object, its
    conditions/events and the component that owns the decision. A
    configuration setting is not a substitute for evidence that the
    intended behavior occurred.
-   **Common wrong answers/misconceptions:** Common misconceptions:
    shutdown must bound and checkpoint work; PDB constrains voluntary
    eviction. These fail because they collapse distinct mechanisms or
    claim guarantees beyond the resource/component boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:**
    05-pod-disruption-budgets-and-graceful-shutdown.md --- PDB boundary
    and blocked drain
-   **Version note:** Not version-sensitive

### U05-SA-03 --- Unit 5 --- Pod disruption budgets and graceful shutdown

-   **Unit/category:** Unit 5 --- Pod disruption budgets and graceful
    shutdown
-   **Level:** L3
-   **Objective tested:** Explain the mechanism and operational
    consequence of SIGTERM, draining and in-flight work.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Sigterm, draining and in-flight work. Explain
    the mechanism, the trade-off, and one failure mode.
-   **Model answer:** Use a failure model first: SIGTERM, draining and
    in-flight work. State what the mechanism guarantees, what it does
    not guarantee, and which evidence would falsify your initial
    hypothesis. Record a measurable verification signal and rollback
    boundary.
-   **Common wrong answers/misconceptions:** Common misconceptions: PDB
    constrains voluntary eviction; PDB cannot prevent all failures.
    These fail because they collapse distinct mechanisms or claim
    guarantees beyond the resource/component boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:**
    05-pod-disruption-budgets-and-graceful-shutdown.md --- SIGTERM,
    draining and in-flight work
-   **Version note:** Not version-sensitive

### U05-MCQ-01 --- Unit 5 --- Pod disruption budgets and graceful shutdown

-   **Unit/category:** Unit 5 --- Pod disruption budgets and graceful
    shutdown
-   **Level:** L1
-   **Objective tested:** Choose an evidence-based operational response
    to ALLOWED DISRUPTIONS zero.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which response best addresses ALLOWED
    DISRUPTIONS zero? Options: A. Make the broadest change
    immediately.; B. Inspect the owning resource status/events and
    confirm scope before changing state.; C. Delete the namespace.; D.
    Assume the symptom uniquely proves one root cause.
-   **Model answer:** A is incorrect (Make the broadest change
    immediately.): a broad immediate change skips diagnosis and may
    enlarge blast radius.; B is best (Inspect the owning resource
    status/events and confirm scope before changing state.): Evidence
    from the owning resource and event stream narrows the differential
    while preserving state.; C is incorrect (Delete the namespace.):
    deleting the namespace is destructive and unrelated to an
    evidence-first diagnosis.; D is incorrect (Assume the symptom
    uniquely proves one root cause.): a symptom rarely proves one unique
    root cause without corroborating evidence..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    B is the only best answer.
-   **Source/coverage note:**
    05-pod-disruption-budgets-and-graceful-shutdown.md --- voluntary
    versus involuntary disruption
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U05-MCQ-02 --- Unit 5 --- Pod disruption budgets and graceful shutdown

-   **Unit/category:** Unit 5 --- Pod disruption budgets and graceful
    shutdown
-   **Level:** L2
-   **Objective tested:** Choose an evidence-based operational response
    to termination grace expires before work finishes.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which statement about PDB boundary and blocked
    drain is most accurate? Options: A. PDB constrains voluntary
    eviction; B. PDB cannot prevent all failures; C. shutdown must bound
    and checkpoint work; D. The mechanism guarantees every dependent
    application outcome.
-   **Model answer:** A is incorrect (PDB constrains voluntary
    eviction): this statement does not correctly express the lesson's
    mechanism or guarantee; it conflates a distinct control or
    overstates what the component ensures.; B is best (PDB cannot
    prevent all failures): The correct distinction is the boundary
    described in the lesson; application-level correctness still
    requires independent verification.; C is incorrect (shutdown must
    bound and checkpoint work): this statement does not correctly
    express the lesson's mechanism or guarantee; it conflates a distinct
    control or overstates what the component ensures.; D is incorrect
    (The mechanism guarantees every dependent application outcome.):
    this statement does not correctly express the lesson's mechanism or
    guarantee; it conflates a distinct control or overstates what the
    component ensures..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    B is the only best answer.
-   **Source/coverage note:**
    05-pod-disruption-budgets-and-graceful-shutdown.md --- PDB boundary
    and blocked drain
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U05-MCQ-03 --- Unit 5 --- Pod disruption budgets and graceful shutdown

-   **Unit/category:** Unit 5 --- Pod disruption budgets and graceful
    shutdown
-   **Level:** L3
-   **Objective tested:** Choose an evidence-based operational response
    to weekly drain with unhealthy replica.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which evidence is strongest before changing
    policy for weekly drain with unhealthy replica? Options: A. A single
    screenshot without timestamp.; B. Only the desired-state
    manifest.; C. Correlated status, events, recent changes,
    capacity/dependency evidence and an explicit SLO impact.; D. A guess
    based on a similar incident.
-   **Model answer:** A is incorrect (A single screenshot without
    timestamp.): a screenshot alone lacks the correlated status, event
    and timeline evidence needed for diagnosis.; B is incorrect (Only
    the desired-state manifest.): desired state alone does not prove
    observed runtime behavior or root cause.; C is best (Correlated
    status, events, recent changes, capacity/dependency evidence and an
    explicit SLO impact.): Correlated evidence supports a differential
    and helps select a scoped reversible mitigation.; D is incorrect (A
    guess based on a similar incident.): guessing from a similar
    incident is not evidence for this cluster..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    C is the only best answer.
-   **Source/coverage note:**
    05-pod-disruption-budgets-and-graceful-shutdown.md --- SIGTERM,
    draining and in-flight work
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U05-OUT-01 --- Unit 5 --- Pod disruption budgets and graceful shutdown

-   **Unit/category:** Unit 5 --- Pod disruption budgets and graceful
    shutdown
-   **Level:** L2
-   **Objective tested:** Interpret a symptom without overstating what
    it proves about voluntary versus involuntary disruption.
-   **Estimated time:** 7 minutes
-   **Question type:** Output interpretation
-   **Question prompt:** **Illustrative output --- not observed
    execution.** Scenario: ALLOWED DISRUPTIONS zero. Assume a current
    namespace/context is confirmed. The only evidence available is this
    symptom; no additional root-cause evidence has been supplied. State
    what can be concluded and what to inspect next.
-   **Model answer:** The observation supports investigation of ALLOWED
    DISRUPTIONS zero, but does not uniquely establish root cause.
    Inspect the relevant object status/conditions, timestamped events,
    recent changes and the adjacent layer: PDB constrains voluntary
    eviction. If the next evidence remains ambiguous, keep competing
    hypotheses open and perform a low-risk read-only test before
    mutation.
-   **Common wrong answers/misconceptions:** Wrong answer 1: state a
    definitive root cause from a symptom alone. Wrong answer 2: perform
    a destructive change before collecting object/event evidence.
-   **Scoring rubric:** 4 points: observed fact 1; bounded inference 1;
    next evidence 1; safe action 1.
-   **Source/coverage note:**
    05-pod-disruption-budgets-and-graceful-shutdown.md --- ALLOWED
    DISRUPTIONS zero
-   **Version note:** \[VERIFY\] all sample output is illustrative and
    command fields vary by version.

### U05-OUT-02 --- Unit 5 --- Pod disruption budgets and graceful shutdown

-   **Unit/category:** Unit 5 --- Pod disruption budgets and graceful
    shutdown
-   **Level:** L3
-   **Objective tested:** Interpret a symptom without overstating what
    it proves about PDB boundary and blocked drain.
-   **Estimated time:** 7 minutes
-   **Question type:** Output interpretation
-   **Question prompt:** **Illustrative output --- not observed
    execution.** Scenario: termination grace expires before work
    finishes. Assume a current namespace/context is confirmed. The only
    evidence available is this symptom; no additional root-cause
    evidence has been supplied. State what can be concluded and what to
    inspect next.
-   **Model answer:** The observation supports investigation of
    termination grace expires before work finishes, but does not
    uniquely establish root cause. Inspect the relevant object
    status/conditions, timestamped events, recent changes and the
    adjacent layer: PDB cannot prevent all failures. If the next
    evidence remains ambiguous, keep competing hypotheses open and
    perform a low-risk read-only test before mutation.
-   **Common wrong answers/misconceptions:** Wrong answer 1: state a
    definitive root cause from a symptom alone. Wrong answer 2: perform
    a destructive change before collecting object/event evidence.
-   **Scoring rubric:** 4 points: observed fact 1; bounded inference 1;
    next evidence 1; safe action 1.
-   **Source/coverage note:**
    05-pod-disruption-budgets-and-graceful-shutdown.md --- termination
    grace expires before work finishes
-   **Version note:** \[VERIFY\] all sample output is illustrative and
    command fields vary by version.

### U05-MAN-01 --- Unit 5 --- Pod disruption budgets and graceful shutdown

-   **Unit/category:** Unit 5 --- Pod disruption budgets and graceful
    shutdown

-   **Level:** L2

-   **Objective tested:** Find at least three independent defects in a
    pod disruption budgets and graceful shutdown configuration.

-   **Estimated time:** 10 minutes

-   **Question type:** Manifest review

-   **Question prompt:** Review this **intentionally defective training
    fixture** and identify at least three independent defects/risks.
    Give a correction plan and verification evidence. Do not apply it
    as-is.

    ``` yaml
    apiVersion: policy/v1
    kind: PodDisruptionBudget
    metadata: {name: scorer-pdb, namespace: scoring}
    spec:
      minAvailable: "100%"
      selector: {matchLabels: {app: scorer}}
    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata: {name: scorer, namespace: scoring}
    spec:
      replicas: 3
      selector: {matchLabels: {app: model}}
      template:
        metadata: {labels: {app: model}}
        spec: {containers: [{name: api, image: scorer:v1}]}
    ```

-   **Model answer:** Risks: PDB selector `app: scorer` matches no
    Deployment Pods labeled `app: model`; a 100% minAvailable policy can
    block all voluntary disruption if corrected; the workload lacks an
    explicit graceful-shutdown/readiness plan. Align selectors, select a
    budget consistent with SLO and replicas, ensure spare capacity and
    test drain behavior. Verify PDB status and actual selected Pods.

-   **Common wrong answers/misconceptions:** Wrong answer 1: treat a
    YAML parse as proof of semantic correctness. Wrong answer 2: remove
    all controls to make the workload proceed. Wrong answer 3: give a
    correction without verification.

-   **Scoring rubric:** 6 points: three independent defects 3; precise
    fixes 1; verification 1; safety/rollback 1.

-   **Source/coverage note:**
    05-pod-disruption-budgets-and-graceful-shutdown.md --- SIGTERM,
    draining and in-flight work

-   **Version note:** \[VERIFY\] intentionally defective excerpt;
    validate API fields and defaults against target version.

### U05-MAN-02 --- Unit 5 --- Pod disruption budgets and graceful shutdown

-   **Unit/category:** Unit 5 --- Pod disruption budgets and graceful
    shutdown

-   **Level:** L3

-   **Objective tested:** Find at least three independent defects in a
    pod disruption budgets and graceful shutdown configuration.

-   **Estimated time:** 10 minutes

-   **Question type:** Manifest review

-   **Question prompt:** Review this **intentionally defective training
    fixture** and identify at least three independent defects/risks.
    Give a correction plan and verification evidence. Do not apply it
    as-is.

    ``` yaml
    apiVersion: v1
    kind: Pod
    metadata: {name: consumer, namespace: queue}
    spec:
      terminationGracePeriodSeconds: 10
      containers:
      - name: worker
        image: consumer:v1
        lifecycle:
          preStop:
            exec: {command: ["sh", "-c", "sleep 15"]}
    ```

-   **Model answer:** Risks: preStop sleep exceeds the 10-second
    termination grace budget; no application SIGTERM handling or
    stop-intake/checkpoint/release behavior is described; a worker may
    be killed mid-message. Implement bounded shutdown and
    idempotent/released work, set grace from measured shutdown latency,
    avoid redundant sleep, and test drain with in-flight messages.
    Verify message correctness and termination duration.

-   **Common wrong answers/misconceptions:** Wrong answer 1: treat a
    YAML parse as proof of semantic correctness. Wrong answer 2: remove
    all controls to make the workload proceed. Wrong answer 3: give a
    correction without verification.

-   **Scoring rubric:** 6 points: three independent defects 3; precise
    fixes 1; verification 1; safety/rollback 1.

-   **Source/coverage note:**
    05-pod-disruption-budgets-and-graceful-shutdown.md --- voluntary
    versus involuntary disruption

-   **Version note:** \[VERIFY\] intentionally defective excerpt;
    validate API fields and defaults against target version.

### U05-INC-01 --- Unit 5 --- Pod disruption budgets and graceful shutdown

-   **Unit/category:** Unit 5 --- Pod disruption budgets and graceful
    shutdown
-   **Level:** L3
-   **Objective tested:** Use evidence-first troubleshooting for drain
    blocked while one replica unhealthy.
-   **Estimated time:** 15 minutes
-   **Question type:** Incident/troubleshooting
-   **Question prompt:** drain blocked while one replica unhealthy.
    Describe scope and timeline, evidence to collect, competing
    hypotheses, a low-risk first test, scoped mitigation, verification,
    rollback/stop condition, and prevention.
-   **Model answer:** Confirm context, namespace, affected SLO and
    change window; capture object conditions/events/logs and recent
    changes. Investigate ALLOWED DISRUPTIONS zero and compare at least
    two plausible causes. Prefer read-only evidence first; apply only a
    scoped, reversible mitigation approved for the environment. Verify
    service-level behavior and object convergence, define a stop
    condition, and record the outcome/runbook follow-up.
-   **Common wrong answers/misconceptions:** Wrong answer 1: treat
    symptom as root cause. Wrong answer 2: make a cluster-wide change
    without blast-radius analysis. Wrong answer 3: declare recovery
    without SLO/object verification.
-   **Scoring rubric:** 8 points: scope/timeline 1; evidence 2;
    differential 1; low-risk test 1; scoped mitigation/stop 1;
    verification 1; prevention/handoff 1.
-   **Source/coverage note:**
    05-pod-disruption-budgets-and-graceful-shutdown.md --- drain blocked
    while one replica unhealthy
-   **Version note:** \[VERIFY\] any destructive/provider-specific
    recovery action against exact release runbook.

### U05-DES-01 --- Unit 5 --- Pod disruption budgets and graceful shutdown

-   **Unit/category:** Unit 5 --- Pod disruption budgets and graceful
    shutdown
-   **Level:** L4
-   **Objective tested:** Design a production-ready approach for design
    maintenance policy across failure domains with explicit trade-offs.
-   **Estimated time:** 18 minutes
-   **Question type:** Design
-   **Question prompt:** design maintenance policy across failure
    domains. State constraints, compare at least two approaches, explain
    failure modes/cost/operability, and give a verification plan.
-   **Model answer:** Define the SLO, failure domains, data/security
    constraints and operating ownership. Approach A optimizes
    simplicity/cost but accepts tighter shared blast radius; approach B
    adds isolation or redundancy at higher capacity/operational cost.
    Select based on measured demand and explicit failure model. Include
    monitoring, rollback/stop criteria, staging rehearsal and a
    post-change verification signal.
-   **Common wrong answers/misconceptions:** Wrong answer 1: choose the
    most complex option without a risk case. Wrong answer 2: optimize
    cost without addressing failure domains. Wrong answer 3: rely on
    component presence rather than tested recovery.
-   **Scoring rubric:** 10 points: constraints/SLO 2; mechanism
    correctness 2; alternatives/trade-offs 2; failure handling 2;
    observability/verification 2.
-   **Source/coverage note:**
    05-pod-disruption-budgets-and-graceful-shutdown.md --- expert/design
    topics
-   **Version note:** \[VERIFY\] implementation syntax and
    managed-provider behavior.

### U05-EXT-01 --- Unit 5 --- Pod disruption budgets and graceful shutdown

-   **Unit/category:** Unit 5 --- Pod disruption budgets and graceful
    shutdown
-   **Level:** L3
-   **Objective tested:** Evaluate a change proposal for voluntary
    versus involuntary disruption using production evidence.
-   **Estimated time:** 8 minutes
-   **Question type:** Short answer / operational decision
-   **Question prompt:** An engineer proposes changing voluntary versus
    involuntary disruption after one incident observation. What
    measurements and guardrails should be required before approving the
    change?
-   **Model answer:** Require timestamped baseline and post-change
    metrics, affected SLOs, a bounded hypothesis, a reversible change
    plan, a stop/rollback threshold and a verification owner. Test
    representative load/failure conditions in staging where possible;
    document residual risk.
-   **Common wrong answers/misconceptions:** Wrong answer 1: act on one
    sample. Wrong answer 2: approve a permanent policy change without
    owner or review date.
-   **Scoring rubric:** 5 points: measurement 2; safety/rollback 1;
    verification 1; governance 1.
-   **Source/coverage note:**
    05-pod-disruption-budgets-and-graceful-shutdown.md --- voluntary
    versus involuntary disruption
-   **Version note:** \[VERIFY\] exact policy behavior before rollout.

## Unit 6 --- Horizontal and vertical autoscaling

### U06-SA-01 --- Unit 6 --- Horizontal and vertical autoscaling

-   **Unit/category:** Unit 6 --- Horizontal and vertical autoscaling
-   **Level:** L1
-   **Objective tested:** Explain the mechanism and operational
    consequence of HPA versus VPA versus node autoscaling.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Hpa versus vpa versus node autoscaling. Explain
    the mechanism, the trade-off, and one failure mode.
-   **Model answer:** Explain HPA versus VPA versus node autoscaling by
    defining the mechanism, identifying the responsible Kubernetes
    layer/resource, and stating one production implication. Validate
    with the relevant object status/events rather than assuming the
    declared configuration proves runtime behavior.
-   **Common wrong answers/misconceptions:** Common misconceptions: node
    autoscaling adds capacity; metrics quality and startup delay affect
    scaling. These fail because they collapse distinct mechanisms or
    claim guarantees beyond the resource/component boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:** 06-horizontal-and-vertical-autoscaling.md
    --- HPA versus VPA versus node autoscaling
-   **Version note:** Not version-sensitive

### U06-SA-02 --- Unit 6 --- Horizontal and vertical autoscaling

-   **Unit/category:** Unit 6 --- Horizontal and vertical autoscaling
-   **Level:** L2
-   **Objective tested:** Explain the mechanism and operational
    consequence of metrics and requests for utilization.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Metrics and requests for utilization. Explain
    the mechanism, the trade-off, and one failure mode.
-   **Model answer:** The distinction is operational: metrics and
    requests for utilization. Inspect the relevant API object, its
    conditions/events and the component that owns the decision. A
    configuration setting is not a substitute for evidence that the
    intended behavior occurred.
-   **Common wrong answers/misconceptions:** Common misconceptions:
    metrics quality and startup delay affect scaling; HPA changes
    replica count. These fail because they collapse distinct mechanisms
    or claim guarantees beyond the resource/component boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:** 06-horizontal-and-vertical-autoscaling.md
    --- metrics and requests for utilization
-   **Version note:** Not version-sensitive

### U06-SA-03 --- Unit 6 --- Horizontal and vertical autoscaling

-   **Unit/category:** Unit 6 --- Horizontal and vertical autoscaling
-   **Level:** L3
-   **Objective tested:** Explain the mechanism and operational
    consequence of thrashing, lag and stabilization.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Thrashing, lag and stabilization. Explain the
    mechanism, the trade-off, and one failure mode.
-   **Model answer:** Use a failure model first: thrashing, lag and
    stabilization. State what the mechanism guarantees, what it does not
    guarantee, and which evidence would falsify your initial hypothesis.
    Record a measurable verification signal and rollback boundary.
-   **Common wrong answers/misconceptions:** Common misconceptions: HPA
    changes replica count; node autoscaling adds capacity. These fail
    because they collapse distinct mechanisms or claim guarantees beyond
    the resource/component boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:** 06-horizontal-and-vertical-autoscaling.md
    --- thrashing, lag and stabilization
-   **Version note:** Not version-sensitive

### U06-MCQ-01 --- Unit 6 --- Horizontal and vertical autoscaling

-   **Unit/category:** Unit 6 --- Horizontal and vertical autoscaling
-   **Level:** L1
-   **Objective tested:** Choose an evidence-based operational response
    to HPA utilization unknown.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which response best addresses HPA utilization
    unknown? Options: A. Make the broadest change immediately.; B.
    Inspect the owning resource status/events and confirm scope before
    changing state.; C. Delete the namespace.; D. Assume the symptom
    uniquely proves one root cause.
-   **Model answer:** A is incorrect (Make the broadest change
    immediately.): a broad immediate change skips diagnosis and may
    enlarge blast radius.; B is best (Inspect the owning resource
    status/events and confirm scope before changing state.): Evidence
    from the owning resource and event stream narrows the differential
    while preserving state.; C is incorrect (Delete the namespace.):
    deleting the namespace is destructive and unrelated to an
    evidence-first diagnosis.; D is incorrect (Assume the symptom
    uniquely proves one root cause.): a symptom rarely proves one unique
    root cause without corroborating evidence..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    B is the only best answer.
-   **Source/coverage note:** 06-horizontal-and-vertical-autoscaling.md
    --- HPA versus VPA versus node autoscaling
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U06-MCQ-02 --- Unit 6 --- Horizontal and vertical autoscaling

-   **Unit/category:** Unit 6 --- Horizontal and vertical autoscaling
-   **Level:** L2
-   **Objective tested:** Choose an evidence-based operational response
    to replicas oscillate while startup takes 90 seconds.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which statement about metrics and requests for
    utilization is most accurate? Options: A. HPA changes replica
    count; B. node autoscaling adds capacity; C. metrics quality and
    startup delay affect scaling; D. The mechanism guarantees every
    dependent application outcome.
-   **Model answer:** A is incorrect (HPA changes replica count): this
    statement does not correctly express the lesson's mechanism or
    guarantee; it conflates a distinct control or overstates what the
    component ensures.; B is best (node autoscaling adds capacity): The
    correct distinction is the boundary described in the lesson;
    application-level correctness still requires independent
    verification.; C is incorrect (metrics quality and startup delay
    affect scaling): this statement does not correctly express the
    lesson's mechanism or guarantee; it conflates a distinct control or
    overstates what the component ensures.; D is incorrect (The
    mechanism guarantees every dependent application outcome.): this
    statement does not correctly express the lesson's mechanism or
    guarantee; it conflates a distinct control or overstates what the
    component ensures..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    B is the only best answer.
-   **Source/coverage note:** 06-horizontal-and-vertical-autoscaling.md
    --- metrics and requests for utilization
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U06-MCQ-03 --- Unit 6 --- Horizontal and vertical autoscaling

-   **Unit/category:** Unit 6 --- Horizontal and vertical autoscaling
-   **Level:** L3
-   **Objective tested:** Choose an evidence-based operational response
    to queue lag high while CPU low.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which evidence is strongest before changing
    policy for queue lag high while CPU low? Options: A. A single
    screenshot without timestamp.; B. Only the desired-state
    manifest.; C. Correlated status, events, recent changes,
    capacity/dependency evidence and an explicit SLO impact.; D. A guess
    based on a similar incident.
-   **Model answer:** A is incorrect (A single screenshot without
    timestamp.): a screenshot alone lacks the correlated status, event
    and timeline evidence needed for diagnosis.; B is incorrect (Only
    the desired-state manifest.): desired state alone does not prove
    observed runtime behavior or root cause.; C is best (Correlated
    status, events, recent changes, capacity/dependency evidence and an
    explicit SLO impact.): Correlated evidence supports a differential
    and helps select a scoped reversible mitigation.; D is incorrect (A
    guess based on a similar incident.): guessing from a similar
    incident is not evidence for this cluster..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    C is the only best answer.
-   **Source/coverage note:** 06-horizontal-and-vertical-autoscaling.md
    --- thrashing, lag and stabilization
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U06-OUT-01 --- Unit 6 --- Horizontal and vertical autoscaling

-   **Unit/category:** Unit 6 --- Horizontal and vertical autoscaling
-   **Level:** L2
-   **Objective tested:** Interpret a symptom without overstating what
    it proves about HPA versus VPA versus node autoscaling.
-   **Estimated time:** 7 minutes
-   **Question type:** Output interpretation
-   **Question prompt:** **Illustrative output --- not observed
    execution.** Scenario: HPA utilization unknown. Assume a current
    namespace/context is confirmed. The only evidence available is this
    symptom; no additional root-cause evidence has been supplied. State
    what can be concluded and what to inspect next.
-   **Model answer:** The observation supports investigation of HPA
    utilization unknown, but does not uniquely establish root cause.
    Inspect the relevant object status/conditions, timestamped events,
    recent changes and the adjacent layer: node autoscaling adds
    capacity. If the next evidence remains ambiguous, keep competing
    hypotheses open and perform a low-risk read-only test before
    mutation.
-   **Common wrong answers/misconceptions:** Wrong answer 1: state a
    definitive root cause from a symptom alone. Wrong answer 2: perform
    a destructive change before collecting object/event evidence.
-   **Scoring rubric:** 4 points: observed fact 1; bounded inference 1;
    next evidence 1; safe action 1.
-   **Source/coverage note:** 06-horizontal-and-vertical-autoscaling.md
    --- HPA utilization unknown
-   **Version note:** \[VERIFY\] all sample output is illustrative and
    command fields vary by version.

### U06-OUT-02 --- Unit 6 --- Horizontal and vertical autoscaling

-   **Unit/category:** Unit 6 --- Horizontal and vertical autoscaling
-   **Level:** L3
-   **Objective tested:** Interpret a symptom without overstating what
    it proves about metrics and requests for utilization.
-   **Estimated time:** 7 minutes
-   **Question type:** Output interpretation
-   **Question prompt:** **Illustrative output --- not observed
    execution.** Scenario: replicas oscillate while startup takes 90
    seconds. Assume a current namespace/context is confirmed. The only
    evidence available is this symptom; no additional root-cause
    evidence has been supplied. State what can be concluded and what to
    inspect next.
-   **Model answer:** The observation supports investigation of replicas
    oscillate while startup takes 90 seconds, but does not uniquely
    establish root cause. Inspect the relevant object status/conditions,
    timestamped events, recent changes and the adjacent layer: metrics
    quality and startup delay affect scaling. If the next evidence
    remains ambiguous, keep competing hypotheses open and perform a
    low-risk read-only test before mutation.
-   **Common wrong answers/misconceptions:** Wrong answer 1: state a
    definitive root cause from a symptom alone. Wrong answer 2: perform
    a destructive change before collecting object/event evidence.
-   **Scoring rubric:** 4 points: observed fact 1; bounded inference 1;
    next evidence 1; safe action 1.
-   **Source/coverage note:** 06-horizontal-and-vertical-autoscaling.md
    --- replicas oscillate while startup takes 90 seconds
-   **Version note:** \[VERIFY\] all sample output is illustrative and
    command fields vary by version.

### U06-MAN-01 --- Unit 6 --- Horizontal and vertical autoscaling

-   **Unit/category:** Unit 6 --- Horizontal and vertical autoscaling

-   **Level:** L2

-   **Objective tested:** Find at least three independent defects in a
    horizontal and vertical autoscaling configuration.

-   **Estimated time:** 10 minutes

-   **Question type:** Manifest review

-   **Question prompt:** Review this **intentionally defective training
    fixture** and identify at least three independent defects/risks.
    Give a correction plan and verification evidence. Do not apply it
    as-is.

    ``` yaml
    apiVersion: autoscaling/v2
    kind: HorizontalPodAutoscaler
    metadata: {name: scorer, namespace: scoring}
    spec:
      scaleTargetRef: {apiVersion: apps/v1, kind: Deployment, name: scorer}
      minReplicas: 1
      maxReplicas: 100
      metrics:
      - type: Resource
        resource:
          name: cpu
          target: {type: Utilization, averageUtilization: 70}
    ```

-   **Model answer:** Risks: CPU utilization may be unavailable or
    misleading without CPU requests; min/max range is very broad without
    capacity/SLO justification; metrics availability and scaling
    behavior/stabilization are not reviewed. Set measured requests,
    confirm metrics API/HPA conditions, bound max replicas to downstream
    and cluster capacity, and test burst/scale-down behavior. `[VERIFY]`
    autoscaling/v2 fields and installed metrics components for the
    target release.

-   **Common wrong answers/misconceptions:** Wrong answer 1: treat a
    YAML parse as proof of semantic correctness. Wrong answer 2: remove
    all controls to make the workload proceed. Wrong answer 3: give a
    correction without verification.

-   **Scoring rubric:** 6 points: three independent defects 3; precise
    fixes 1; verification 1; safety/rollback 1.

-   **Source/coverage note:** 06-horizontal-and-vertical-autoscaling.md
    --- thrashing, lag and stabilization

-   **Version note:** \[VERIFY\] intentionally defective excerpt;
    validate API fields and defaults against target version.

### U06-MAN-02 --- Unit 6 --- Horizontal and vertical autoscaling

-   **Unit/category:** Unit 6 --- Horizontal and vertical autoscaling

-   **Level:** L3

-   **Objective tested:** Find at least three independent defects in a
    horizontal and vertical autoscaling configuration.

-   **Estimated time:** 10 minutes

-   **Question type:** Manifest review

-   **Question prompt:** Review this **intentionally defective training
    fixture** and identify at least three independent defects/risks.
    Give a correction plan and verification evidence. Do not apply it
    as-is.

    ``` yaml
    apiVersion: autoscaling.k8s.io/v1
    kind: VerticalPodAutoscaler
    metadata: {name: scorer, namespace: scoring}
    spec:
      targetRef: {apiVersion: apps/v1, kind: Deployment, name: scorer}
      updatePolicy: {updateMode: Auto}
    ```

-   **Model answer:** Risks: VPA API is an optional add-on/CRD and may
    not exist; Auto updates can change/evict Pods depending on
    implementation and version; simultaneous CPU-utilization HPA can
    create feedback as requests change; no disruption/capacity plan.
    Verify VPA install/version and supported HPA combination, consider
    recommendation-only mode, define PDB/headroom and test in staging.
    `[VERIFY]` exact API and update semantics.

-   **Common wrong answers/misconceptions:** Wrong answer 1: treat a
    YAML parse as proof of semantic correctness. Wrong answer 2: remove
    all controls to make the workload proceed. Wrong answer 3: give a
    correction without verification.

-   **Scoring rubric:** 6 points: three independent defects 3; precise
    fixes 1; verification 1; safety/rollback 1.

-   **Source/coverage note:** 06-horizontal-and-vertical-autoscaling.md
    --- HPA versus VPA versus node autoscaling

-   **Version note:** \[VERIFY\] intentionally defective excerpt;
    validate API fields and defaults against target version.

### U06-INC-01 --- Unit 6 --- Horizontal and vertical autoscaling

-   **Unit/category:** Unit 6 --- Horizontal and vertical autoscaling
-   **Level:** L3
-   **Objective tested:** Use evidence-first troubleshooting for
    scale-out Pods remain Pending.
-   **Estimated time:** 15 minutes
-   **Question type:** Incident/troubleshooting
-   **Question prompt:** scale-out Pods remain Pending. Describe scope
    and timeline, evidence to collect, competing hypotheses, a low-risk
    first test, scoped mitigation, verification, rollback/stop
    condition, and prevention.
-   **Model answer:** Confirm context, namespace, affected SLO and
    change window; capture object conditions/events/logs and recent
    changes. Investigate HPA utilization unknown and compare at least
    two plausible causes. Prefer read-only evidence first; apply only a
    scoped, reversible mitigation approved for the environment. Verify
    service-level behavior and object convergence, define a stop
    condition, and record the outcome/runbook follow-up.
-   **Common wrong answers/misconceptions:** Wrong answer 1: treat
    symptom as root cause. Wrong answer 2: make a cluster-wide change
    without blast-radius analysis. Wrong answer 3: declare recovery
    without SLO/object verification.
-   **Scoring rubric:** 8 points: scope/timeline 1; evidence 2;
    differential 1; low-risk test 1; scoped mitigation/stop 1;
    verification 1; prevention/handoff 1.
-   **Source/coverage note:** 06-horizontal-and-vertical-autoscaling.md
    --- scale-out Pods remain Pending
-   **Version note:** \[VERIFY\] any destructive/provider-specific
    recovery action against exact release runbook.

### U06-DES-01 --- Unit 6 --- Horizontal and vertical autoscaling

-   **Unit/category:** Unit 6 --- Horizontal and vertical autoscaling
-   **Level:** L4
-   **Objective tested:** Design a production-ready approach for choose
    API and queue scaling signals with explicit trade-offs.
-   **Estimated time:** 18 minutes
-   **Question type:** Design
-   **Question prompt:** choose API and queue scaling signals. State
    constraints, compare at least two approaches, explain failure
    modes/cost/operability, and give a verification plan.
-   **Model answer:** Define the SLO, failure domains, data/security
    constraints and operating ownership. Approach A optimizes
    simplicity/cost but accepts tighter shared blast radius; approach B
    adds isolation or redundancy at higher capacity/operational cost.
    Select based on measured demand and explicit failure model. Include
    monitoring, rollback/stop criteria, staging rehearsal and a
    post-change verification signal.
-   **Common wrong answers/misconceptions:** Wrong answer 1: choose the
    most complex option without a risk case. Wrong answer 2: optimize
    cost without addressing failure domains. Wrong answer 3: rely on
    component presence rather than tested recovery.
-   **Scoring rubric:** 10 points: constraints/SLO 2; mechanism
    correctness 2; alternatives/trade-offs 2; failure handling 2;
    observability/verification 2.
-   **Source/coverage note:** 06-horizontal-and-vertical-autoscaling.md
    --- expert/design topics
-   **Version note:** \[VERIFY\] implementation syntax and
    managed-provider behavior.

## Unit 7 --- Node pools, taints, affinity, and workload placement

### U07-SA-01 --- Unit 7 --- Node pools, taints, affinity, and workload placement

-   **Unit/category:** Unit 7 --- Node pools, taints, affinity, and
    workload placement
-   **Level:** L1
-   **Objective tested:** Explain the mechanism and operational
    consequence of nodeSelector versus affinity.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Nodeselector versus affinity. Explain the
    mechanism, the trade-off, and one failure mode.
-   **Model answer:** Explain nodeSelector versus affinity by defining
    the mechanism, identifying the responsible Kubernetes
    layer/resource, and stating one production implication. Validate
    with the relevant object status/events rather than assuming the
    declared configuration proves runtime behavior.
-   **Common wrong answers/misconceptions:** Common misconceptions:
    toleration permits but does not attract; placement policy cannot
    create capacity. These fail because they collapse distinct
    mechanisms or claim guarantees beyond the resource/component
    boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:**
    07-node-pools-taints-affinity-and-workload-placement.md ---
    nodeSelector versus affinity
-   **Version note:** Not version-sensitive

### U07-SA-02 --- Unit 7 --- Node pools, taints, affinity, and workload placement

-   **Unit/category:** Unit 7 --- Node pools, taints, affinity, and
    workload placement
-   **Level:** L2
-   **Objective tested:** Explain the mechanism and operational
    consequence of taints/tolerations do not guarantee placement.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Taints/tolerations do not guarantee placement.
    Explain the mechanism, the trade-off, and one failure mode.
-   **Model answer:** The distinction is operational: taints/tolerations
    do not guarantee placement. Inspect the relevant API object, its
    conditions/events and the component that owns the decision. A
    configuration setting is not a substitute for evidence that the
    intended behavior occurred.
-   **Common wrong answers/misconceptions:** Common misconceptions:
    placement policy cannot create capacity; required affinity is hard
    constraint. These fail because they collapse distinct mechanisms or
    claim guarantees beyond the resource/component boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:**
    07-node-pools-taints-affinity-and-workload-placement.md ---
    taints/tolerations do not guarantee placement
-   **Version note:** Not version-sensitive

### U07-SA-03 --- Unit 7 --- Node pools, taints, affinity, and workload placement

-   **Unit/category:** Unit 7 --- Node pools, taints, affinity, and
    workload placement
-   **Level:** L3
-   **Objective tested:** Explain the mechanism and operational
    consequence of topology spread and failure domains.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Topology spread and failure domains. Explain
    the mechanism, the trade-off, and one failure mode.
-   **Model answer:** Use a failure model first: topology spread and
    failure domains. State what the mechanism guarantees, what it does
    not guarantee, and which evidence would falsify your initial
    hypothesis. Record a measurable verification signal and rollback
    boundary.
-   **Common wrong answers/misconceptions:** Common misconceptions:
    required affinity is hard constraint; toleration permits but does
    not attract. These fail because they collapse distinct mechanisms or
    claim guarantees beyond the resource/component boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:**
    07-node-pools-taints-affinity-and-workload-placement.md --- topology
    spread and failure domains
-   **Version note:** Not version-sensitive

### U07-MCQ-01 --- Unit 7 --- Node pools, taints, affinity, and workload placement

-   **Unit/category:** Unit 7 --- Node pools, taints, affinity, and
    workload placement
-   **Level:** L1
-   **Objective tested:** Choose an evidence-based operational response
    to FailedScheduling due to taint/affinity.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which response best addresses FailedScheduling
    due to taint/affinity? Options: A. Make the broadest change
    immediately.; B. Inspect the owning resource status/events and
    confirm scope before changing state.; C. Delete the namespace.; D.
    Assume the symptom uniquely proves one root cause.
-   **Model answer:** A is incorrect (Make the broadest change
    immediately.): a broad immediate change skips diagnosis and may
    enlarge blast radius.; B is best (Inspect the owning resource
    status/events and confirm scope before changing state.): Evidence
    from the owning resource and event stream narrows the differential
    while preserving state.; C is incorrect (Delete the namespace.):
    deleting the namespace is destructive and unrelated to an
    evidence-first diagnosis.; D is incorrect (Assume the symptom
    uniquely proves one root cause.): a symptom rarely proves one unique
    root cause without corroborating evidence..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    B is the only best answer.
-   **Source/coverage note:**
    07-node-pools-taints-affinity-and-workload-placement.md ---
    nodeSelector versus affinity
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U07-MCQ-02 --- Unit 7 --- Node pools, taints, affinity, and workload placement

-   **Unit/category:** Unit 7 --- Node pools, taints, affinity, and
    workload placement
-   **Level:** L2
-   **Objective tested:** Choose an evidence-based operational response
    to all replicas on one node.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which statement about taints/tolerations do not
    guarantee placement is most accurate? Options: A. required affinity
    is hard constraint; B. toleration permits but does not attract; C.
    placement policy cannot create capacity; D. The mechanism guarantees
    every dependent application outcome.
-   **Model answer:** A is incorrect (required affinity is hard
    constraint): this statement does not correctly express the lesson's
    mechanism or guarantee; it conflates a distinct control or
    overstates what the component ensures.; B is best (toleration
    permits but does not attract): The correct distinction is the
    boundary described in the lesson; application-level correctness
    still requires independent verification.; C is incorrect (placement
    policy cannot create capacity): this statement does not correctly
    express the lesson's mechanism or guarantee; it conflates a distinct
    control or overstates what the component ensures.; D is incorrect
    (The mechanism guarantees every dependent application outcome.):
    this statement does not correctly express the lesson's mechanism or
    guarantee; it conflates a distinct control or overstates what the
    component ensures..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    B is the only best answer.
-   **Source/coverage note:**
    07-node-pools-taints-affinity-and-workload-placement.md ---
    taints/tolerations do not guarantee placement
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U07-MCQ-03 --- Unit 7 --- Node pools, taints, affinity, and workload placement

-   **Unit/category:** Unit 7 --- Node pools, taints, affinity, and
    workload placement
-   **Level:** L3
-   **Objective tested:** Choose an evidence-based operational response
    to GPU workload remains Pending.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which evidence is strongest before changing
    policy for GPU workload remains Pending? Options: A. A single
    screenshot without timestamp.; B. Only the desired-state
    manifest.; C. Correlated status, events, recent changes,
    capacity/dependency evidence and an explicit SLO impact.; D. A guess
    based on a similar incident.
-   **Model answer:** A is incorrect (A single screenshot without
    timestamp.): a screenshot alone lacks the correlated status, event
    and timeline evidence needed for diagnosis.; B is incorrect (Only
    the desired-state manifest.): desired state alone does not prove
    observed runtime behavior or root cause.; C is best (Correlated
    status, events, recent changes, capacity/dependency evidence and an
    explicit SLO impact.): Correlated evidence supports a differential
    and helps select a scoped reversible mitigation.; D is incorrect (A
    guess based on a similar incident.): guessing from a similar
    incident is not evidence for this cluster..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    C is the only best answer.
-   **Source/coverage note:**
    07-node-pools-taints-affinity-and-workload-placement.md --- topology
    spread and failure domains
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U07-OUT-01 --- Unit 7 --- Node pools, taints, affinity, and workload placement

-   **Unit/category:** Unit 7 --- Node pools, taints, affinity, and
    workload placement
-   **Level:** L2
-   **Objective tested:** Interpret a symptom without overstating what
    it proves about nodeSelector versus affinity.
-   **Estimated time:** 7 minutes
-   **Question type:** Output interpretation
-   **Question prompt:** **Illustrative output --- not observed
    execution.** Scenario: FailedScheduling due to taint/affinity.
    Assume a current namespace/context is confirmed. The only evidence
    available is this symptom; no additional root-cause evidence has
    been supplied. State what can be concluded and what to inspect next.
-   **Model answer:** The observation supports investigation of
    FailedScheduling due to taint/affinity, but does not uniquely
    establish root cause. Inspect the relevant object status/conditions,
    timestamped events, recent changes and the adjacent layer: placement
    policy cannot create capacity. If the next evidence remains
    ambiguous, keep competing hypotheses open and perform a low-risk
    read-only test before mutation.
-   **Common wrong answers/misconceptions:** Wrong answer 1: state a
    definitive root cause from a symptom alone. Wrong answer 2: perform
    a destructive change before collecting object/event evidence.
-   **Scoring rubric:** 4 points: observed fact 1; bounded inference 1;
    next evidence 1; safe action 1.
-   **Source/coverage note:**
    07-node-pools-taints-affinity-and-workload-placement.md ---
    FailedScheduling due to taint/affinity
-   **Version note:** \[VERIFY\] all sample output is illustrative and
    command fields vary by version.

### U07-OUT-02 --- Unit 7 --- Node pools, taints, affinity, and workload placement

-   **Unit/category:** Unit 7 --- Node pools, taints, affinity, and
    workload placement
-   **Level:** L3
-   **Objective tested:** Interpret a symptom without overstating what
    it proves about taints/tolerations do not guarantee placement.
-   **Estimated time:** 7 minutes
-   **Question type:** Output interpretation
-   **Question prompt:** **Illustrative output --- not observed
    execution.** Scenario: all replicas on one node. Assume a current
    namespace/context is confirmed. The only evidence available is this
    symptom; no additional root-cause evidence has been supplied. State
    what can be concluded and what to inspect next.
-   **Model answer:** The observation supports investigation of all
    replicas on one node, but does not uniquely establish root cause.
    Inspect the relevant object status/conditions, timestamped events,
    recent changes and the adjacent layer: required affinity is hard
    constraint. If the next evidence remains ambiguous, keep competing
    hypotheses open and perform a low-risk read-only test before
    mutation.
-   **Common wrong answers/misconceptions:** Wrong answer 1: state a
    definitive root cause from a symptom alone. Wrong answer 2: perform
    a destructive change before collecting object/event evidence.
-   **Scoring rubric:** 4 points: observed fact 1; bounded inference 1;
    next evidence 1; safe action 1.
-   **Source/coverage note:**
    07-node-pools-taints-affinity-and-workload-placement.md --- all
    replicas on one node
-   **Version note:** \[VERIFY\] all sample output is illustrative and
    command fields vary by version.

### U07-MAN-01 --- Unit 7 --- Node pools, taints, affinity, and workload placement

-   **Unit/category:** Unit 7 --- Node pools, taints, affinity, and
    workload placement

-   **Level:** L2

-   **Objective tested:** Find at least three independent defects in a
    node pools, taints, affinity, and workload placement configuration.

-   **Estimated time:** 10 minutes

-   **Question type:** Manifest review

-   **Question prompt:** Review this **intentionally defective training
    fixture** and identify at least three independent defects/risks.
    Give a correction plan and verification evidence. Do not apply it
    as-is.

    ``` yaml
    apiVersion: batch/v1
    kind: Job
    metadata: {name: gpu-batch, namespace: ml}
    spec:
      template:
        spec:
          nodeSelector: {accelerator: nvidia}
          tolerations:
          - {key: dedicated, operator: Equal, value: gpu, effect: NoSchedule}
          restartPolicy: Never
          containers:
          - name: task
            image: gpu-task:v1
    ```

-   **Model answer:** Risks: selector label may not exist on eligible
    nodes; toleration does not attract the Pod or allocate a GPU;
    container does not request the GPU resource; capacity/quota/storage
    constraints are not checked. Verify labels and taints, request the
    appropriate extended resource, inspect events and node allocatable,
    then test placement. GPU device plugin/driver support is
    environment-specific.

-   **Common wrong answers/misconceptions:** Wrong answer 1: treat a
    YAML parse as proof of semantic correctness. Wrong answer 2: remove
    all controls to make the workload proceed. Wrong answer 3: give a
    correction without verification.

-   **Scoring rubric:** 6 points: three independent defects 3; precise
    fixes 1; verification 1; safety/rollback 1.

-   **Source/coverage note:**
    07-node-pools-taints-affinity-and-workload-placement.md --- topology
    spread and failure domains

-   **Version note:** \[VERIFY\] intentionally defective excerpt;
    validate API fields and defaults against target version.

### U07-MAN-02 --- Unit 7 --- Node pools, taints, affinity, and workload placement

-   **Unit/category:** Unit 7 --- Node pools, taints, affinity, and
    workload placement

-   **Level:** L3

-   **Objective tested:** Find at least three independent defects in a
    node pools, taints, affinity, and workload placement configuration.

-   **Estimated time:** 10 minutes

-   **Question type:** Manifest review

-   **Question prompt:** Review this **intentionally defective training
    fixture** and identify at least three independent defects/risks.
    Give a correction plan and verification evidence. Do not apply it
    as-is.

    ``` yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata: {name: api}
    spec:
      replicas: 3
      selector: {matchLabels: {app: api}}
      template:
        metadata: {labels: {app: api}}
        spec:
          affinity:
            nodeAffinity:
              requiredDuringSchedulingIgnoredDuringExecution:
                nodeSelectorTerms:
                - matchExpressions: [{key: pool, operator: In, values: [low-latency]}]
            podAntiAffinity:
              requiredDuringSchedulingIgnoredDuringExecution:
              - labelSelector: {matchLabels: {app: api}}
                topologyKey: kubernetes.io/hostname
          containers: [{name: api, image: api:v1}]
    ```

-   **Model answer:** Risks: hard node affinity narrows eligible nodes;
    required anti-affinity demands separate hosts but only one matching
    node may exist; no requests/readiness or failure-domain fallback is
    shown. Add eligible capacity or deliberately soften placement with
    documented SLO trade-off, set measured resources and health checks,
    and verify distribution after rollout.

-   **Common wrong answers/misconceptions:** Wrong answer 1: treat a
    YAML parse as proof of semantic correctness. Wrong answer 2: remove
    all controls to make the workload proceed. Wrong answer 3: give a
    correction without verification.

-   **Scoring rubric:** 6 points: three independent defects 3; precise
    fixes 1; verification 1; safety/rollback 1.

-   **Source/coverage note:**
    07-node-pools-taints-affinity-and-workload-placement.md ---
    nodeSelector versus affinity

-   **Version note:** \[VERIFY\] intentionally defective excerpt;
    validate API fields and defaults against target version.

### U07-INC-01 --- Unit 7 --- Node pools, taints, affinity, and workload placement

-   **Unit/category:** Unit 7 --- Node pools, taints, affinity, and
    workload placement
-   **Level:** L3
-   **Objective tested:** Use evidence-first troubleshooting for node
    pool rotation leaves Pods Pending.
-   **Estimated time:** 15 minutes
-   **Question type:** Incident/troubleshooting
-   **Question prompt:** node pool rotation leaves Pods Pending.
    Describe scope and timeline, evidence to collect, competing
    hypotheses, a low-risk first test, scoped mitigation, verification,
    rollback/stop condition, and prevention.
-   **Model answer:** Confirm context, namespace, affected SLO and
    change window; capture object conditions/events/logs and recent
    changes. Investigate FailedScheduling due to taint/affinity and
    compare at least two plausible causes. Prefer read-only evidence
    first; apply only a scoped, reversible mitigation approved for the
    environment. Verify service-level behavior and object convergence,
    define a stop condition, and record the outcome/runbook follow-up.
-   **Common wrong answers/misconceptions:** Wrong answer 1: treat
    symptom as root cause. Wrong answer 2: make a cluster-wide change
    without blast-radius analysis. Wrong answer 3: declare recovery
    without SLO/object verification.
-   **Scoring rubric:** 8 points: scope/timeline 1; evidence 2;
    differential 1; low-risk test 1; scoped mitigation/stop 1;
    verification 1; prevention/handoff 1.
-   **Source/coverage note:**
    07-node-pools-taints-affinity-and-workload-placement.md --- node
    pool rotation leaves Pods Pending
-   **Version note:** \[VERIFY\] any destructive/provider-specific
    recovery action against exact release runbook.

### U07-DES-01 --- Unit 7 --- Node pools, taints, affinity, and workload placement

-   **Unit/category:** Unit 7 --- Node pools, taints, affinity, and
    workload placement
-   **Level:** L4
-   **Objective tested:** Design a production-ready approach for design
    placement for API, GPU and ETL with explicit trade-offs.
-   **Estimated time:** 18 minutes
-   **Question type:** Design
-   **Question prompt:** design placement for API, GPU and ETL. State
    constraints, compare at least two approaches, explain failure
    modes/cost/operability, and give a verification plan.
-   **Model answer:** Define the SLO, failure domains, data/security
    constraints and operating ownership. Approach A optimizes
    simplicity/cost but accepts tighter shared blast radius; approach B
    adds isolation or redundancy at higher capacity/operational cost.
    Select based on measured demand and explicit failure model. Include
    monitoring, rollback/stop criteria, staging rehearsal and a
    post-change verification signal.
-   **Common wrong answers/misconceptions:** Wrong answer 1: choose the
    most complex option without a risk case. Wrong answer 2: optimize
    cost without addressing failure domains. Wrong answer 3: rely on
    component presence rather than tested recovery.
-   **Scoring rubric:** 10 points: constraints/SLO 2; mechanism
    correctness 2; alternatives/trade-offs 2; failure handling 2;
    observability/verification 2.
-   **Source/coverage note:**
    07-node-pools-taints-affinity-and-workload-placement.md ---
    expert/design topics
-   **Version note:** \[VERIFY\] implementation syntax and
    managed-provider behavior.

## Unit 8 --- Cluster upgrades and version compatibility

### U08-SA-01 --- Unit 8 --- Cluster upgrades and version compatibility

-   **Unit/category:** Unit 8 --- Cluster upgrades and version
    compatibility
-   **Level:** L1
-   **Objective tested:** Explain the mechanism and operational
    consequence of compatibility is a dependency graph.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Compatibility is a dependency graph. Explain
    the mechanism, the trade-off, and one failure mode.
-   **Model answer:** Explain compatibility is a dependency graph by
    defining the mechanism, identifying the responsible Kubernetes
    layer/resource, and stating one production implication. Validate
    with the relevant object status/events rather than assuming the
    declared configuration proves runtime behavior.
-   **Common wrong answers/misconceptions:** Common misconceptions:
    static scanning misses some live usage; rollback may be unsafe after
    state/API changes. These fail because they collapse distinct
    mechanisms or claim guarantees beyond the resource/component
    boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:**
    08-cluster-upgrades-and-version-compatibility.md --- compatibility
    is a dependency graph
-   **Version note:** Not version-sensitive

### U08-SA-02 --- Unit 8 --- Cluster upgrades and version compatibility

-   **Unit/category:** Unit 8 --- Cluster upgrades and version
    compatibility
-   **Level:** L2
-   **Objective tested:** Explain the mechanism and operational
    consequence of deprecation versus removal.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Deprecation versus removal. Explain the
    mechanism, the trade-off, and one failure mode.
-   **Model answer:** The distinction is operational: deprecation versus
    removal. Inspect the relevant API object, its conditions/events and
    the component that owns the decision. A configuration setting is not
    a substitute for evidence that the intended behavior occurred.
-   **Common wrong answers/misconceptions:** Common misconceptions:
    rollback may be unsafe after state/API changes; check actual
    version-skew matrix. These fail because they collapse distinct
    mechanisms or claim guarantees beyond the resource/component
    boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:**
    08-cluster-upgrades-and-version-compatibility.md --- deprecation
    versus removal
-   **Version note:** Not version-sensitive

### U08-SA-03 --- Unit 8 --- Cluster upgrades and version compatibility

-   **Unit/category:** Unit 8 --- Cluster upgrades and version
    compatibility
-   **Level:** L3
-   **Objective tested:** Explain the mechanism and operational
    consequence of in-place versus rotation versus blue/green.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** In-place versus rotation versus blue/green.
    Explain the mechanism, the trade-off, and one failure mode.
-   **Model answer:** Use a failure model first: in-place versus
    rotation versus blue/green. State what the mechanism guarantees,
    what it does not guarantee, and which evidence would falsify your
    initial hypothesis. Record a measurable verification signal and
    rollback boundary.
-   **Common wrong answers/misconceptions:** Common misconceptions:
    check actual version-skew matrix; static scanning misses some live
    usage. These fail because they collapse distinct mechanisms or claim
    guarantees beyond the resource/component boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:**
    08-cluster-upgrades-and-version-compatibility.md --- in-place versus
    rotation versus blue/green
-   **Version note:** Not version-sensitive

### U08-MCQ-01 --- Unit 8 --- Cluster upgrades and version compatibility

-   **Unit/category:** Unit 8 --- Cluster upgrades and version
    compatibility
-   **Level:** L1
-   **Objective tested:** Choose an evidence-based operational response
    to scanner finds removed API.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which response best addresses scanner finds
    removed API? Options: A. Make the broadest change immediately.; B.
    Inspect the owning resource status/events and confirm scope before
    changing state.; C. Delete the namespace.; D. Assume the symptom
    uniquely proves one root cause.
-   **Model answer:** A is incorrect (Make the broadest change
    immediately.): a broad immediate change skips diagnosis and may
    enlarge blast radius.; B is best (Inspect the owning resource
    status/events and confirm scope before changing state.): Evidence
    from the owning resource and event stream narrows the differential
    while preserving state.; C is incorrect (Delete the namespace.):
    deleting the namespace is destructive and unrelated to an
    evidence-first diagnosis.; D is incorrect (Assume the symptom
    uniquely proves one root cause.): a symptom rarely proves one unique
    root cause without corroborating evidence..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    B is the only best answer.
-   **Source/coverage note:**
    08-cluster-upgrades-and-version-compatibility.md --- compatibility
    is a dependency graph
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U08-MCQ-02 --- Unit 8 --- Cluster upgrades and version compatibility

-   **Unit/category:** Unit 8 --- Cluster upgrades and version
    compatibility
-   **Level:** L2
-   **Objective tested:** Choose an evidence-based operational response
    to webhook times out after upgrade.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which statement about deprecation versus
    removal is most accurate? Options: A. check actual version-skew
    matrix; B. static scanning misses some live usage; C. rollback may
    be unsafe after state/API changes; D. The mechanism guarantees every
    dependent application outcome.
-   **Model answer:** A is incorrect (check actual version-skew matrix):
    this statement does not correctly express the lesson's mechanism or
    guarantee; it conflates a distinct control or overstates what the
    component ensures.; B is best (static scanning misses some live
    usage): The correct distinction is the boundary described in the
    lesson; application-level correctness still requires independent
    verification.; C is incorrect (rollback may be unsafe after
    state/API changes): this statement does not correctly express the
    lesson's mechanism or guarantee; it conflates a distinct control or
    overstates what the component ensures.; D is incorrect (The
    mechanism guarantees every dependent application outcome.): this
    statement does not correctly express the lesson's mechanism or
    guarantee; it conflates a distinct control or overstates what the
    component ensures..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    B is the only best answer.
-   **Source/coverage note:**
    08-cluster-upgrades-and-version-compatibility.md --- deprecation
    versus removal
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U08-MCQ-03 --- Unit 8 --- Cluster upgrades and version compatibility

-   **Unit/category:** Unit 8 --- Cluster upgrades and version
    compatibility
-   **Level:** L3
-   **Objective tested:** Choose an evidence-based operational response
    to CSI mount failure after node upgrade.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which evidence is strongest before changing
    policy for CSI mount failure after node upgrade? Options: A. A
    single screenshot without timestamp.; B. Only the desired-state
    manifest.; C. Correlated status, events, recent changes,
    capacity/dependency evidence and an explicit SLO impact.; D. A guess
    based on a similar incident.
-   **Model answer:** A is incorrect (A single screenshot without
    timestamp.): a screenshot alone lacks the correlated status, event
    and timeline evidence needed for diagnosis.; B is incorrect (Only
    the desired-state manifest.): desired state alone does not prove
    observed runtime behavior or root cause.; C is best (Correlated
    status, events, recent changes, capacity/dependency evidence and an
    explicit SLO impact.): Correlated evidence supports a differential
    and helps select a scoped reversible mitigation.; D is incorrect (A
    guess based on a similar incident.): guessing from a similar
    incident is not evidence for this cluster..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    C is the only best answer.
-   **Source/coverage note:**
    08-cluster-upgrades-and-version-compatibility.md --- in-place versus
    rotation versus blue/green
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U08-OUT-01 --- Unit 8 --- Cluster upgrades and version compatibility

-   **Unit/category:** Unit 8 --- Cluster upgrades and version
    compatibility
-   **Level:** L2
-   **Objective tested:** Interpret a symptom without overstating what
    it proves about compatibility is a dependency graph.
-   **Estimated time:** 7 minutes
-   **Question type:** Output interpretation
-   **Question prompt:** **Illustrative output --- not observed
    execution.** Scenario: scanner finds removed API. Assume a current
    namespace/context is confirmed. The only evidence available is this
    symptom; no additional root-cause evidence has been supplied. State
    what can be concluded and what to inspect next.
-   **Model answer:** The observation supports investigation of scanner
    finds removed API, but does not uniquely establish root cause.
    Inspect the relevant object status/conditions, timestamped events,
    recent changes and the adjacent layer: check actual version-skew
    matrix. If the next evidence remains ambiguous, keep competing
    hypotheses open and perform a low-risk read-only test before
    mutation.
-   **Common wrong answers/misconceptions:** Wrong answer 1: state a
    definitive root cause from a symptom alone. Wrong answer 2: perform
    a destructive change before collecting object/event evidence.
-   **Scoring rubric:** 4 points: observed fact 1; bounded inference 1;
    next evidence 1; safe action 1.
-   **Source/coverage note:**
    08-cluster-upgrades-and-version-compatibility.md --- scanner finds
    removed API
-   **Version note:** \[VERIFY\] all sample output is illustrative and
    command fields vary by version.

### U08-OUT-02 --- Unit 8 --- Cluster upgrades and version compatibility

-   **Unit/category:** Unit 8 --- Cluster upgrades and version
    compatibility
-   **Level:** L3
-   **Objective tested:** Interpret a symptom without overstating what
    it proves about deprecation versus removal.
-   **Estimated time:** 7 minutes
-   **Question type:** Output interpretation
-   **Question prompt:** **Illustrative output --- not observed
    execution.** Scenario: webhook times out after upgrade. Assume a
    current namespace/context is confirmed. The only evidence available
    is this symptom; no additional root-cause evidence has been
    supplied. State what can be concluded and what to inspect next.
-   **Model answer:** The observation supports investigation of webhook
    times out after upgrade, but does not uniquely establish root cause.
    Inspect the relevant object status/conditions, timestamped events,
    recent changes and the adjacent layer: static scanning misses some
    live usage. If the next evidence remains ambiguous, keep competing
    hypotheses open and perform a low-risk read-only test before
    mutation.
-   **Common wrong answers/misconceptions:** Wrong answer 1: state a
    definitive root cause from a symptom alone. Wrong answer 2: perform
    a destructive change before collecting object/event evidence.
-   **Scoring rubric:** 4 points: observed fact 1; bounded inference 1;
    next evidence 1; safe action 1.
-   **Source/coverage note:**
    08-cluster-upgrades-and-version-compatibility.md --- webhook times
    out after upgrade
-   **Version note:** \[VERIFY\] all sample output is illustrative and
    command fields vary by version.

### U08-MAN-01 --- Unit 8 --- Cluster upgrades and version compatibility

-   **Unit/category:** Unit 8 --- Cluster upgrades and version
    compatibility

-   **Level:** L2

-   **Objective tested:** Find at least three independent defects in a
    cluster upgrades and version compatibility configuration.

-   **Estimated time:** 10 minutes

-   **Question type:** Manifest review

-   **Question prompt:** Review this **intentionally defective training
    fixture** and identify at least three independent defects/risks.
    Give a correction plan and verification evidence. Do not apply it
    as-is.

    ``` yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata: {name: gateway}
    spec:
      replicas: 3
      selector: {matchLabels: {app: gateway}}
      template:
        metadata: {labels: {app: gateway}}
        spec:
          containers: [{name: gateway, image: gateway:v1}]
    # Upgrade plan: upgrade control plane only; skip CNI, CSI, ingress, CRDs and webhooks.
    ```

-   **Model answer:** Risks: no version-skew/upgrade-order check;
    CNI/CSI/ingress compatibility is unreviewed; CRD/operator/webhook
    readiness and rollback behavior are missing; workload/PDB/backup
    gates absent. Build a compatibility inventory from authoritative
    target-version docs, stage rings, test API deprecations and add-ons,
    define health gates and stop/rollback criteria. Do not treat
    successful API upgrade as end-to-end validation.

-   **Common wrong answers/misconceptions:** Wrong answer 1: treat a
    YAML parse as proof of semantic correctness. Wrong answer 2: remove
    all controls to make the workload proceed. Wrong answer 3: give a
    correction without verification.

-   **Scoring rubric:** 6 points: three independent defects 3; precise
    fixes 1; verification 1; safety/rollback 1.

-   **Source/coverage note:**
    08-cluster-upgrades-and-version-compatibility.md --- in-place versus
    rotation versus blue/green

-   **Version note:** \[VERIFY\] intentionally defective excerpt;
    validate API fields and defaults against target version.

### U08-MAN-02 --- Unit 8 --- Cluster upgrades and version compatibility

-   **Unit/category:** Unit 8 --- Cluster upgrades and version
    compatibility

-   **Level:** L3

-   **Objective tested:** Find at least three independent defects in a
    cluster upgrades and version compatibility configuration.

-   **Estimated time:** 10 minutes

-   **Question type:** Manifest review

-   **Question prompt:** Review this **intentionally defective training
    fixture** and identify at least three independent defects/risks.
    Give a correction plan and verification evidence. Do not apply it
    as-is.

    ``` yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata: {name: scorer}
    spec:
      replicas: 2
      selector: {matchLabels: {app: scorer}}
      template:
        metadata: {labels: {app: scorer}}
        spec:
          containers:
          - name: scorer
            image: scorer:v2
            # migration plan only changes apiVersion; removed fields/defaults not reviewed
    ```

-   **Model answer:** Risks: target API may not serve old fields;
    changed defaults can alter behavior; no server-side validation or
    release-note review; no compatibility/data rollback plan. Verify
    target schema and semantics, update removed fields, compare
    effective defaults, test in target-version staging, and validate
    workload/data behavior. API version conversion alone is not proof of
    semantic equivalence.

-   **Common wrong answers/misconceptions:** Wrong answer 1: treat a
    YAML parse as proof of semantic correctness. Wrong answer 2: remove
    all controls to make the workload proceed. Wrong answer 3: give a
    correction without verification.

-   **Scoring rubric:** 6 points: three independent defects 3; precise
    fixes 1; verification 1; safety/rollback 1.

-   **Source/coverage note:**
    08-cluster-upgrades-and-version-compatibility.md --- compatibility
    is a dependency graph

-   **Version note:** \[VERIFY\] intentionally defective excerpt;
    validate API fields and defaults against target version.

### U08-INC-01 --- Unit 8 --- Cluster upgrades and version compatibility

-   **Unit/category:** Unit 8 --- Cluster upgrades and version
    compatibility
-   **Level:** L3
-   **Objective tested:** Use evidence-first troubleshooting for upgrade
    causes intermittent API and volume failures.
-   **Estimated time:** 15 minutes
-   **Question type:** Incident/troubleshooting
-   **Question prompt:** upgrade causes intermittent API and volume
    failures. Describe scope and timeline, evidence to collect,
    competing hypotheses, a low-risk first test, scoped mitigation,
    verification, rollback/stop condition, and prevention.
-   **Model answer:** Confirm context, namespace, affected SLO and
    change window; capture object conditions/events/logs and recent
    changes. Investigate scanner finds removed API and compare at least
    two plausible causes. Prefer read-only evidence first; apply only a
    scoped, reversible mitigation approved for the environment. Verify
    service-level behavior and object convergence, define a stop
    condition, and record the outcome/runbook follow-up.
-   **Common wrong answers/misconceptions:** Wrong answer 1: treat
    symptom as root cause. Wrong answer 2: make a cluster-wide change
    without blast-radius analysis. Wrong answer 3: declare recovery
    without SLO/object verification.
-   **Scoring rubric:** 8 points: scope/timeline 1; evidence 2;
    differential 1; low-risk test 1; scoped mitigation/stop 1;
    verification 1; prevention/handoff 1.
-   **Source/coverage note:**
    08-cluster-upgrades-and-version-compatibility.md --- upgrade causes
    intermittent API and volume failures
-   **Version note:** \[VERIFY\] any destructive/provider-specific
    recovery action against exact release runbook.

### U08-DES-01 --- Unit 8 --- Cluster upgrades and version compatibility

-   **Unit/category:** Unit 8 --- Cluster upgrades and version
    compatibility
-   **Level:** L4
-   **Objective tested:** Design a production-ready approach for design
    fleet upgrade gates with explicit trade-offs.
-   **Estimated time:** 18 minutes
-   **Question type:** Design
-   **Question prompt:** design fleet upgrade gates. State constraints,
    compare at least two approaches, explain failure
    modes/cost/operability, and give a verification plan.
-   **Model answer:** Define the SLO, failure domains, data/security
    constraints and operating ownership. Approach A optimizes
    simplicity/cost but accepts tighter shared blast radius; approach B
    adds isolation or redundancy at higher capacity/operational cost.
    Select based on measured demand and explicit failure model. Include
    monitoring, rollback/stop criteria, staging rehearsal and a
    post-change verification signal.
-   **Common wrong answers/misconceptions:** Wrong answer 1: choose the
    most complex option without a risk case. Wrong answer 2: optimize
    cost without addressing failure domains. Wrong answer 3: rely on
    component presence rather than tested recovery.
-   **Scoring rubric:** 10 points: constraints/SLO 2; mechanism
    correctness 2; alternatives/trade-offs 2; failure handling 2;
    observability/verification 2.
-   **Source/coverage note:**
    08-cluster-upgrades-and-version-compatibility.md --- expert/design
    topics
-   **Version note:** \[VERIFY\] implementation syntax and
    managed-provider behavior.

## Unit 9 --- Kubernetes RBAC and Pod Security Standards

### U09-SA-01 --- Unit 9 --- Kubernetes RBAC and Pod Security Standards

-   **Unit/category:** Unit 9 --- Kubernetes RBAC and Pod Security
    Standards
-   **Level:** L1
-   **Objective tested:** Explain the mechanism and operational
    consequence of authentication versus authorization versus admission.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Authentication versus authorization versus
    admission. Explain the mechanism, the trade-off, and one failure
    mode.
-   **Model answer:** Explain authentication versus authorization versus
    admission by defining the mechanism, identifying the responsible
    Kubernetes layer/resource, and stating one production implication.
    Validate with the relevant object status/events rather than assuming
    the declared configuration proves runtime behavior.
-   **Common wrong answers/misconceptions:** Common misconceptions:
    admission can reject otherwise authorized request; least privilege
    requires explicit scope and verbs. These fail because they collapse
    distinct mechanisms or claim guarantees beyond the
    resource/component boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:**
    09-kubernetes-rbac-and-pod-security-standards.md --- authentication
    versus authorization versus admission
-   **Version note:** Not version-sensitive

### U09-SA-02 --- Unit 9 --- Kubernetes RBAC and Pod Security Standards

-   **Unit/category:** Unit 9 --- Kubernetes RBAC and Pod Security
    Standards
-   **Level:** L2
-   **Objective tested:** Explain the mechanism and operational
    consequence of Role/RoleBinding scope and least privilege.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Role/rolebinding scope and least privilege.
    Explain the mechanism, the trade-off, and one failure mode.
-   **Model answer:** The distinction is operational: Role/RoleBinding
    scope and least privilege. Inspect the relevant API object, its
    conditions/events and the component that owns the decision. A
    configuration setting is not a substitute for evidence that the
    intended behavior occurred.
-   **Common wrong answers/misconceptions:** Common misconceptions:
    least privilege requires explicit scope and verbs; RBAC controls API
    authorization. These fail because they collapse distinct mechanisms
    or claim guarantees beyond the resource/component boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:**
    09-kubernetes-rbac-and-pod-security-standards.md ---
    Role/RoleBinding scope and least privilege
-   **Version note:** Not version-sensitive

### U09-SA-03 --- Unit 9 --- Kubernetes RBAC and Pod Security Standards

-   **Unit/category:** Unit 9 --- Kubernetes RBAC and Pod Security
    Standards
-   **Level:** L3
-   **Objective tested:** Explain the mechanism and operational
    consequence of Pod Security Standards staged rollout.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Pod security standards staged rollout. Explain
    the mechanism, the trade-off, and one failure mode.
-   **Model answer:** Use a failure model first: Pod Security Standards
    staged rollout. State what the mechanism guarantees, what it does
    not guarantee, and which evidence would falsify your initial
    hypothesis. Record a measurable verification signal and rollback
    boundary.
-   **Common wrong answers/misconceptions:** Common misconceptions: RBAC
    controls API authorization; admission can reject otherwise
    authorized request. These fail because they collapse distinct
    mechanisms or claim guarantees beyond the resource/component
    boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:**
    09-kubernetes-rbac-and-pod-security-standards.md --- Pod Security
    Standards staged rollout
-   **Version note:** Not version-sensitive

### U09-MCQ-01 --- Unit 9 --- Kubernetes RBAC and Pod Security Standards

-   **Unit/category:** Unit 9 --- Kubernetes RBAC and Pod Security
    Standards
-   **Level:** L1
-   **Objective tested:** Choose an evidence-based operational response
    to Forbidden for get pods.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which response best addresses Forbidden for get
    pods? Options: A. Make the broadest change immediately.; B. Inspect
    the owning resource status/events and confirm scope before changing
    state.; C. Delete the namespace.; D. Assume the symptom uniquely
    proves one root cause.
-   **Model answer:** A is incorrect (Make the broadest change
    immediately.): a broad immediate change skips diagnosis and may
    enlarge blast radius.; B is best (Inspect the owning resource
    status/events and confirm scope before changing state.): Evidence
    from the owning resource and event stream narrows the differential
    while preserving state.; C is incorrect (Delete the namespace.):
    deleting the namespace is destructive and unrelated to an
    evidence-first diagnosis.; D is incorrect (Assume the symptom
    uniquely proves one root cause.): a symptom rarely proves one unique
    root cause without corroborating evidence..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    B is the only best answer.
-   **Source/coverage note:**
    09-kubernetes-rbac-and-pod-security-standards.md --- authentication
    versus authorization versus admission
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U09-MCQ-02 --- Unit 9 --- Kubernetes RBAC and Pod Security Standards

-   **Unit/category:** Unit 9 --- Kubernetes RBAC and Pod Security
    Standards
-   **Level:** L2
-   **Objective tested:** Choose an evidence-based operational response
    to PSA rejects privileged Pod though can-i says yes.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which statement about Role/RoleBinding scope
    and least privilege is most accurate? Options: A. RBAC controls API
    authorization; B. admission can reject otherwise authorized
    request; C. least privilege requires explicit scope and verbs; D.
    The mechanism guarantees every dependent application outcome.
-   **Model answer:** A is incorrect (RBAC controls API authorization):
    this statement does not correctly express the lesson's mechanism or
    guarantee; it conflates a distinct control or overstates what the
    component ensures.; B is best (admission can reject otherwise
    authorized request): The correct distinction is the boundary
    described in the lesson; application-level correctness still
    requires independent verification.; C is incorrect (least privilege
    requires explicit scope and verbs): this statement does not
    correctly express the lesson's mechanism or guarantee; it conflates
    a distinct control or overstates what the component ensures.; D is
    incorrect (The mechanism guarantees every dependent application
    outcome.): this statement does not correctly express the lesson's
    mechanism or guarantee; it conflates a distinct control or
    overstates what the component ensures..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    B is the only best answer.
-   **Source/coverage note:**
    09-kubernetes-rbac-and-pod-security-standards.md ---
    Role/RoleBinding scope and least privilege
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U09-MCQ-03 --- Unit 9 --- Kubernetes RBAC and Pod Security Standards

-   **Unit/category:** Unit 9 --- Kubernetes RBAC and Pod Security
    Standards
-   **Level:** L3
-   **Objective tested:** Choose an evidence-based operational response
    to overprivileged ServiceAccount.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which evidence is strongest before changing
    policy for overprivileged ServiceAccount? Options: A. A single
    screenshot without timestamp.; B. Only the desired-state
    manifest.; C. Correlated status, events, recent changes,
    capacity/dependency evidence and an explicit SLO impact.; D. A guess
    based on a similar incident.
-   **Model answer:** A is incorrect (A single screenshot without
    timestamp.): a screenshot alone lacks the correlated status, event
    and timeline evidence needed for diagnosis.; B is incorrect (Only
    the desired-state manifest.): desired state alone does not prove
    observed runtime behavior or root cause.; C is best (Correlated
    status, events, recent changes, capacity/dependency evidence and an
    explicit SLO impact.): Correlated evidence supports a differential
    and helps select a scoped reversible mitigation.; D is incorrect (A
    guess based on a similar incident.): guessing from a similar
    incident is not evidence for this cluster..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    C is the only best answer.
-   **Source/coverage note:**
    09-kubernetes-rbac-and-pod-security-standards.md --- Pod Security
    Standards staged rollout
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U09-OUT-01 --- Unit 9 --- Kubernetes RBAC and Pod Security Standards

-   **Unit/category:** Unit 9 --- Kubernetes RBAC and Pod Security
    Standards
-   **Level:** L2
-   **Objective tested:** Interpret a symptom without overstating what
    it proves about authentication versus authorization versus
    admission.
-   **Estimated time:** 7 minutes
-   **Question type:** Output interpretation
-   **Question prompt:** **Illustrative output --- not observed
    execution.** Scenario: Forbidden for get pods. Assume a current
    namespace/context is confirmed. The only evidence available is this
    symptom; no additional root-cause evidence has been supplied. State
    what can be concluded and what to inspect next.
-   **Model answer:** The observation supports investigation of
    Forbidden for get pods, but does not uniquely establish root cause.
    Inspect the relevant object status/conditions, timestamped events,
    recent changes and the adjacent layer: admission can reject
    otherwise authorized request. If the next evidence remains
    ambiguous, keep competing hypotheses open and perform a low-risk
    read-only test before mutation.
-   **Common wrong answers/misconceptions:** Wrong answer 1: state a
    definitive root cause from a symptom alone. Wrong answer 2: perform
    a destructive change before collecting object/event evidence.
-   **Scoring rubric:** 4 points: observed fact 1; bounded inference 1;
    next evidence 1; safe action 1.
-   **Source/coverage note:**
    09-kubernetes-rbac-and-pod-security-standards.md --- Forbidden for
    get pods
-   **Version note:** \[VERIFY\] all sample output is illustrative and
    command fields vary by version.

### U09-OUT-02 --- Unit 9 --- Kubernetes RBAC and Pod Security Standards

-   **Unit/category:** Unit 9 --- Kubernetes RBAC and Pod Security
    Standards
-   **Level:** L3
-   **Objective tested:** Interpret a symptom without overstating what
    it proves about Role/RoleBinding scope and least privilege.
-   **Estimated time:** 7 minutes
-   **Question type:** Output interpretation
-   **Question prompt:** **Illustrative output --- not observed
    execution.** Scenario: PSA rejects privileged Pod though can-i says
    yes. Assume a current namespace/context is confirmed. The only
    evidence available is this symptom; no additional root-cause
    evidence has been supplied. State what can be concluded and what to
    inspect next.
-   **Model answer:** The observation supports investigation of PSA
    rejects privileged Pod though can-i says yes, but does not uniquely
    establish root cause. Inspect the relevant object status/conditions,
    timestamped events, recent changes and the adjacent layer: least
    privilege requires explicit scope and verbs. If the next evidence
    remains ambiguous, keep competing hypotheses open and perform a
    low-risk read-only test before mutation.
-   **Common wrong answers/misconceptions:** Wrong answer 1: state a
    definitive root cause from a symptom alone. Wrong answer 2: perform
    a destructive change before collecting object/event evidence.
-   **Scoring rubric:** 4 points: observed fact 1; bounded inference 1;
    next evidence 1; safe action 1.
-   **Source/coverage note:**
    09-kubernetes-rbac-and-pod-security-standards.md --- PSA rejects
    privileged Pod though can-i says yes
-   **Version note:** \[VERIFY\] all sample output is illustrative and
    command fields vary by version.

### U09-MAN-01 --- Unit 9 --- Kubernetes RBAC and Pod Security Standards

-   **Unit/category:** Unit 9 --- Kubernetes RBAC and Pod Security
    Standards

-   **Level:** L2

-   **Objective tested:** Find at least three independent defects in a
    kubernetes rbac and pod security standards configuration.

-   **Estimated time:** 10 minutes

-   **Question type:** Manifest review

-   **Question prompt:** Review this **intentionally defective training
    fixture** and identify at least three independent defects/risks.
    Give a correction plan and verification evidence. Do not apply it
    as-is.

    ``` yaml
    apiVersion: rbac.authorization.k8s.io/v1
    kind: ClusterRoleBinding
    metadata: {name: consumer-admin}
    subjects:
    - kind: ServiceAccount
      name: consumer
      namespace: queue
    roleRef:
      apiGroup: rbac.authorization.k8s.io
      kind: ClusterRole
      name: cluster-admin
    ```

-   **Model answer:** Risks: cluster-admin is excessive for a queue
    consumer; cluster-wide binding expands blast radius; token
    exposure/automount and access recertification are unaddressed.
    Replace with explicit least-privilege namespace-scoped
    Role/RoleBinding, disable token automount if not needed, audit
    effective permissions and test required operations. Verify
    `kubectl auth can-i` under the workload identity.

-   **Common wrong answers/misconceptions:** Wrong answer 1: treat a
    YAML parse as proof of semantic correctness. Wrong answer 2: remove
    all controls to make the workload proceed. Wrong answer 3: give a
    correction without verification.

-   **Scoring rubric:** 6 points: three independent defects 3; precise
    fixes 1; verification 1; safety/rollback 1.

-   **Source/coverage note:**
    09-kubernetes-rbac-and-pod-security-standards.md --- Pod Security
    Standards staged rollout

-   **Version note:** \[VERIFY\] intentionally defective excerpt;
    validate API fields and defaults against target version.

### U09-MAN-02 --- Unit 9 --- Kubernetes RBAC and Pod Security Standards

-   **Unit/category:** Unit 9 --- Kubernetes RBAC and Pod Security
    Standards

-   **Level:** L3

-   **Objective tested:** Find at least three independent defects in a
    kubernetes rbac and pod security standards configuration.

-   **Estimated time:** 10 minutes

-   **Question type:** Manifest review

-   **Question prompt:** Review this **intentionally defective training
    fixture** and identify at least three independent defects/risks.
    Give a correction plan and verification evidence. Do not apply it
    as-is.

    ``` yaml
    apiVersion: v1
    kind: Namespace
    metadata:
      name: production
      labels:
        pod-security.kubernetes.io/enforce: restricted:latest
    # Apply this label to every namespace immediately, with no audit or inventory.
    ```

-   **Model answer:** Risks: label version `latest` is
    version-sensitive; immediate enforce can block existing
    workloads/rollouts; no audit inventory, remediation path, exception
    expiry or rollback plan. Pin the intended policy version, audit/warn
    first, remediate securityContext/capabilities/volume needs, then
    stage enforcement and monitor denials. `[VERIFY]` exact label syntax
    and policy version.

-   **Common wrong answers/misconceptions:** Wrong answer 1: treat a
    YAML parse as proof of semantic correctness. Wrong answer 2: remove
    all controls to make the workload proceed. Wrong answer 3: give a
    correction without verification.

-   **Scoring rubric:** 6 points: three independent defects 3; precise
    fixes 1; verification 1; safety/rollback 1.

-   **Source/coverage note:**
    09-kubernetes-rbac-and-pod-security-standards.md --- authentication
    versus authorization versus admission

-   **Version note:** \[VERIFY\] intentionally defective excerpt;
    validate API fields and defaults against target version.

### U09-INC-01 --- Unit 9 --- Kubernetes RBAC and Pod Security Standards

-   **Unit/category:** Unit 9 --- Kubernetes RBAC and Pod Security
    Standards
-   **Level:** L3
-   **Objective tested:** Use evidence-first troubleshooting for
    consumer denied access and role is overbroad.
-   **Estimated time:** 15 minutes
-   **Question type:** Incident/troubleshooting
-   **Question prompt:** consumer denied access and role is overbroad.
    Describe scope and timeline, evidence to collect, competing
    hypotheses, a low-risk first test, scoped mitigation, verification,
    rollback/stop condition, and prevention.
-   **Model answer:** Confirm context, namespace, affected SLO and
    change window; capture object conditions/events/logs and recent
    changes. Investigate Forbidden for get pods and compare at least two
    plausible causes. Prefer read-only evidence first; apply only a
    scoped, reversible mitigation approved for the environment. Verify
    service-level behavior and object convergence, define a stop
    condition, and record the outcome/runbook follow-up.
-   **Common wrong answers/misconceptions:** Wrong answer 1: treat
    symptom as root cause. Wrong answer 2: make a cluster-wide change
    without blast-radius analysis. Wrong answer 3: declare recovery
    without SLO/object verification.
-   **Scoring rubric:** 8 points: scope/timeline 1; evidence 2;
    differential 1; low-risk test 1; scoped mitigation/stop 1;
    verification 1; prevention/handoff 1.
-   **Source/coverage note:**
    09-kubernetes-rbac-and-pod-security-standards.md --- consumer denied
    access and role is overbroad
-   **Version note:** \[VERIFY\] any destructive/provider-specific
    recovery action against exact release runbook.

### U09-DES-01 --- Unit 9 --- Kubernetes RBAC and Pod Security Standards

-   **Unit/category:** Unit 9 --- Kubernetes RBAC and Pod Security
    Standards
-   **Level:** L4
-   **Objective tested:** Design a production-ready approach for design
    RBAC and PSA rollout with explicit trade-offs.
-   **Estimated time:** 18 minutes
-   **Question type:** Design
-   **Question prompt:** design RBAC and PSA rollout. State constraints,
    compare at least two approaches, explain failure
    modes/cost/operability, and give a verification plan.
-   **Model answer:** Define the SLO, failure domains, data/security
    constraints and operating ownership. Approach A optimizes
    simplicity/cost but accepts tighter shared blast radius; approach B
    adds isolation or redundancy at higher capacity/operational cost.
    Select based on measured demand and explicit failure model. Include
    monitoring, rollback/stop criteria, staging rehearsal and a
    post-change verification signal.
-   **Common wrong answers/misconceptions:** Wrong answer 1: choose the
    most complex option without a risk case. Wrong answer 2: optimize
    cost without addressing failure domains. Wrong answer 3: rely on
    component presence rather than tested recovery.
-   **Scoring rubric:** 10 points: constraints/SLO 2; mechanism
    correctness 2; alternatives/trade-offs 2; failure handling 2;
    observability/verification 2.
-   **Source/coverage note:**
    09-kubernetes-rbac-and-pod-security-standards.md --- expert/design
    topics
-   **Version note:** \[VERIFY\] implementation syntax and
    managed-provider behavior.

## Unit 10 --- etcd health, backup, and control-plane troubleshooting

### U10-SA-01 --- Unit 10 --- etcd health, backup, and control-plane troubleshooting

-   **Unit/category:** Unit 10 --- etcd health, backup, and
    control-plane troubleshooting
-   **Level:** L1
-   **Objective tested:** Explain the mechanism and operational
    consequence of Raft quorum and member failures.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Raft quorum and member failures. Explain the
    mechanism, the trade-off, and one failure mode.
-   **Model answer:** Explain Raft quorum and member failures by
    defining the mechanism, identifying the responsible Kubernetes
    layer/resource, and stating one production implication. Validate
    with the relevant object status/events rather than assuming the
    declared configuration proves runtime behavior.
-   **Common wrong answers/misconceptions:** Common misconceptions: etcd
    snapshot does not include PV bytes automatically; restore tooling is
    release/environment sensitive. These fail because they collapse
    distinct mechanisms or claim guarantees beyond the
    resource/component boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:**
    10-etcd-health-backup-and-control-plane-troubleshooting.md --- Raft
    quorum and member failures
-   **Version note:** Not version-sensitive

### U10-SA-02 --- Unit 10 --- etcd health, backup, and control-plane troubleshooting

-   **Unit/category:** Unit 10 --- etcd health, backup, and
    control-plane troubleshooting
-   **Level:** L2
-   **Objective tested:** Explain the mechanism and operational
    consequence of snapshot integrity versus recoverability.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Snapshot integrity versus recoverability.
    Explain the mechanism, the trade-off, and one failure mode.
-   **Model answer:** The distinction is operational: snapshot integrity
    versus recoverability. Inspect the relevant API object, its
    conditions/events and the component that owns the decision. A
    configuration setting is not a substitute for evidence that the
    intended behavior occurred.
-   **Common wrong answers/misconceptions:** Common misconceptions:
    restore tooling is release/environment sensitive; three-member
    quorum requires two. These fail because they collapse distinct
    mechanisms or claim guarantees beyond the resource/component
    boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:**
    10-etcd-health-backup-and-control-plane-troubleshooting.md ---
    snapshot integrity versus recoverability
-   **Version note:** Not version-sensitive

### U10-SA-03 --- Unit 10 --- etcd health, backup, and control-plane troubleshooting

-   **Unit/category:** Unit 10 --- etcd health, backup, and
    control-plane troubleshooting
-   **Level:** L3
-   **Objective tested:** Explain the mechanism and operational
    consequence of restore compatibility, PV scope, RPO/RTO.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Restore compatibility, pv scope, rpo/rto.
    Explain the mechanism, the trade-off, and one failure mode.
-   **Model answer:** Use a failure model first: restore compatibility,
    PV scope, RPO/RTO. State what the mechanism guarantees, what it does
    not guarantee, and which evidence would falsify your initial
    hypothesis. Record a measurable verification signal and rollback
    boundary.
-   **Common wrong answers/misconceptions:** Common misconceptions:
    three-member quorum requires two; etcd snapshot does not include PV
    bytes automatically. These fail because they collapse distinct
    mechanisms or claim guarantees beyond the resource/component
    boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:**
    10-etcd-health-backup-and-control-plane-troubleshooting.md ---
    restore compatibility, PV scope, RPO/RTO
-   **Version note:** Not version-sensitive

### U10-MCQ-01 --- Unit 10 --- etcd health, backup, and control-plane troubleshooting

-   **Unit/category:** Unit 10 --- etcd health, backup, and
    control-plane troubleshooting
-   **Level:** L1
-   **Objective tested:** Choose an evidence-based operational response
    to one etcd endpoint unreachable.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which response best addresses one etcd endpoint
    unreachable? Options: A. Make the broadest change immediately.; B.
    Inspect the owning resource status/events and confirm scope before
    changing state.; C. Delete the namespace.; D. Assume the symptom
    uniquely proves one root cause.
-   **Model answer:** A is incorrect (Make the broadest change
    immediately.): a broad immediate change skips diagnosis and may
    enlarge blast radius.; B is best (Inspect the owning resource
    status/events and confirm scope before changing state.): Evidence
    from the owning resource and event stream narrows the differential
    while preserving state.; C is incorrect (Delete the namespace.):
    deleting the namespace is destructive and unrelated to an
    evidence-first diagnosis.; D is incorrect (Assume the symptom
    uniquely proves one root cause.): a symptom rarely proves one unique
    root cause without corroborating evidence..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    B is the only best answer.
-   **Source/coverage note:**
    10-etcd-health-backup-and-control-plane-troubleshooting.md --- Raft
    quorum and member failures
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U10-MCQ-02 --- Unit 10 --- etcd health, backup, and control-plane troubleshooting

-   **Unit/category:** Unit 10 --- etcd health, backup, and
    control-plane troubleshooting
-   **Level:** L2
-   **Objective tested:** Choose an evidence-based operational response
    to snapshot only on same host and no restore drill.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which statement about snapshot integrity versus
    recoverability is most accurate? Options: A. three-member quorum
    requires two; B. etcd snapshot does not include PV bytes
    automatically; C. restore tooling is release/environment
    sensitive; D. The mechanism guarantees every dependent application
    outcome.
-   **Model answer:** A is incorrect (three-member quorum requires two):
    this statement does not correctly express the lesson's mechanism or
    guarantee; it conflates a distinct control or overstates what the
    component ensures.; B is best (etcd snapshot does not include PV
    bytes automatically): The correct distinction is the boundary
    described in the lesson; application-level correctness still
    requires independent verification.; C is incorrect (restore tooling
    is release/environment sensitive): this statement does not correctly
    express the lesson's mechanism or guarantee; it conflates a distinct
    control or overstates what the component ensures.; D is incorrect
    (The mechanism guarantees every dependent application outcome.):
    this statement does not correctly express the lesson's mechanism or
    guarantee; it conflates a distinct control or overstates what the
    component ensures..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    B is the only best answer.
-   **Source/coverage note:**
    10-etcd-health-backup-and-control-plane-troubleshooting.md ---
    snapshot integrity versus recoverability
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U10-MCQ-03 --- Unit 10 --- etcd health, backup, and control-plane troubleshooting

-   **Unit/category:** Unit 10 --- etcd health, backup, and
    control-plane troubleshooting
-   **Level:** L3
-   **Objective tested:** Choose an evidence-based operational response
    to API intermittent with etcd latency/disk alarms.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which evidence is strongest before changing
    policy for API intermittent with etcd latency/disk alarms?
    Options: A. A single screenshot without timestamp.; B. Only the
    desired-state manifest.; C. Correlated status, events, recent
    changes, capacity/dependency evidence and an explicit SLO
    impact.; D. A guess based on a similar incident.
-   **Model answer:** A is incorrect (A single screenshot without
    timestamp.): a screenshot alone lacks the correlated status, event
    and timeline evidence needed for diagnosis.; B is incorrect (Only
    the desired-state manifest.): desired state alone does not prove
    observed runtime behavior or root cause.; C is best (Correlated
    status, events, recent changes, capacity/dependency evidence and an
    explicit SLO impact.): Correlated evidence supports a differential
    and helps select a scoped reversible mitigation.; D is incorrect (A
    guess based on a similar incident.): guessing from a similar
    incident is not evidence for this cluster..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    C is the only best answer.
-   **Source/coverage note:**
    10-etcd-health-backup-and-control-plane-troubleshooting.md ---
    restore compatibility, PV scope, RPO/RTO
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U10-OUT-01 --- Unit 10 --- etcd health, backup, and control-plane troubleshooting

-   **Unit/category:** Unit 10 --- etcd health, backup, and
    control-plane troubleshooting
-   **Level:** L2
-   **Objective tested:** Interpret a symptom without overstating what
    it proves about Raft quorum and member failures.
-   **Estimated time:** 7 minutes
-   **Question type:** Output interpretation
-   **Question prompt:** **Illustrative output --- not observed
    execution.** Scenario: one etcd endpoint unreachable. Assume a
    current namespace/context is confirmed. The only evidence available
    is this symptom; no additional root-cause evidence has been
    supplied. State what can be concluded and what to inspect next.
-   **Model answer:** The observation supports investigation of one etcd
    endpoint unreachable, but does not uniquely establish root cause.
    Inspect the relevant object status/conditions, timestamped events,
    recent changes and the adjacent layer: restore tooling is
    release/environment sensitive. If the next evidence remains
    ambiguous, keep competing hypotheses open and perform a low-risk
    read-only test before mutation.
-   **Common wrong answers/misconceptions:** Wrong answer 1: state a
    definitive root cause from a symptom alone. Wrong answer 2: perform
    a destructive change before collecting object/event evidence.
-   **Scoring rubric:** 4 points: observed fact 1; bounded inference 1;
    next evidence 1; safe action 1.
-   **Source/coverage note:**
    10-etcd-health-backup-and-control-plane-troubleshooting.md --- one
    etcd endpoint unreachable
-   **Version note:** \[VERIFY\] all sample output is illustrative and
    command fields vary by version.

### U10-OUT-02 --- Unit 10 --- etcd health, backup, and control-plane troubleshooting

-   **Unit/category:** Unit 10 --- etcd health, backup, and
    control-plane troubleshooting
-   **Level:** L3
-   **Objective tested:** Interpret a symptom without overstating what
    it proves about snapshot integrity versus recoverability.
-   **Estimated time:** 7 minutes
-   **Question type:** Output interpretation
-   **Question prompt:** **Illustrative output --- not observed
    execution.** Scenario: snapshot only on same host and no restore
    drill. Assume a current namespace/context is confirmed. The only
    evidence available is this symptom; no additional root-cause
    evidence has been supplied. State what can be concluded and what to
    inspect next.
-   **Model answer:** The observation supports investigation of snapshot
    only on same host and no restore drill, but does not uniquely
    establish root cause. Inspect the relevant object status/conditions,
    timestamped events, recent changes and the adjacent layer:
    three-member quorum requires two. If the next evidence remains
    ambiguous, keep competing hypotheses open and perform a low-risk
    read-only test before mutation.
-   **Common wrong answers/misconceptions:** Wrong answer 1: state a
    definitive root cause from a symptom alone. Wrong answer 2: perform
    a destructive change before collecting object/event evidence.
-   **Scoring rubric:** 4 points: observed fact 1; bounded inference 1;
    next evidence 1; safe action 1.
-   **Source/coverage note:**
    10-etcd-health-backup-and-control-plane-troubleshooting.md ---
    snapshot only on same host and no restore drill
-   **Version note:** \[VERIFY\] all sample output is illustrative and
    command fields vary by version.

### U10-MAN-01 --- Unit 10 --- etcd health, backup, and control-plane troubleshooting

-   **Unit/category:** Unit 10 --- etcd health, backup, and
    control-plane troubleshooting

-   **Level:** L2

-   **Objective tested:** Find at least three independent defects in a
    etcd health, backup, and control-plane troubleshooting
    configuration.

-   **Estimated time:** 10 minutes

-   **Question type:** Manifest review

-   **Question prompt:** Review this **intentionally defective training
    fixture** and identify at least three independent defects/risks.
    Give a correction plan and verification evidence. Do not apply it
    as-is.

    ``` yaml
    # Backup runbook excerpt
    ETCDCTL_API=3 etcdctl snapshot save /tmp/etcd.db
    ls -l /tmp/etcd.db
    cat /tmp/backup.log >> /shared/team.log
    # success if file exists
    ```

-   **Model answer:** Risks: `/tmp` on the same host is not
    durable/off-node; file existence does not verify snapshot
    status/integrity; cluster state may be sensitive and shared logs can
    leak operational details; TLS/version/retention/restore drill are
    absent. Use a protected approved destination, verify compatible
    tool/TLS and snapshot metadata, create an off-node protected copy,
    and test isolated restore with measured RPO/RTO. Do not log
    credentials.

-   **Common wrong answers/misconceptions:** Wrong answer 1: treat a
    YAML parse as proof of semantic correctness. Wrong answer 2: remove
    all controls to make the workload proceed. Wrong answer 3: give a
    correction without verification.

-   **Scoring rubric:** 6 points: three independent defects 3; precise
    fixes 1; verification 1; safety/rollback 1.

-   **Source/coverage note:**
    10-etcd-health-backup-and-control-plane-troubleshooting.md ---
    restore compatibility, PV scope, RPO/RTO

-   **Version note:** \[VERIFY\] intentionally defective excerpt;
    validate API fields and defaults against target version.

### U10-MAN-02 --- Unit 10 --- etcd health, backup, and control-plane troubleshooting

-   **Unit/category:** Unit 10 --- etcd health, backup, and
    control-plane troubleshooting

-   **Level:** L3

-   **Objective tested:** Find at least three independent defects in a
    etcd health, backup, and control-plane troubleshooting
    configuration.

-   **Estimated time:** 10 minutes

-   **Question type:** Manifest review

-   **Question prompt:** Review this **intentionally defective training
    fixture** and identify at least three independent defects/risks.
    Give a correction plan and verification evidence. Do not apply it
    as-is.

    ``` yaml
    # Restore runbook excerpt
    etcdutl snapshot restore /var/lib/etcd/snapshot.db --data-dir /var/lib/etcd
    # run while existing API server and etcd are active
    # version compatibility and target identity not checked
    ```

-   **Model answer:** Risks: target data directory may be live and
    overwritten/corrupted; exact tool/version compatibility is not
    verified; target cluster identity/consistency and backup integrity
    are not checked; no approval, isolation or stop condition. Rehearse
    in isolation, follow exact release-specific procedure, verify backup
    and target paths, stop relevant components under approved
    maintenance, and require explicit recovery authorization. `[VERIFY]`
    exact syntax and tool availability.

-   **Common wrong answers/misconceptions:** Wrong answer 1: treat a
    YAML parse as proof of semantic correctness. Wrong answer 2: remove
    all controls to make the workload proceed. Wrong answer 3: give a
    correction without verification.

-   **Scoring rubric:** 6 points: three independent defects 3; precise
    fixes 1; verification 1; safety/rollback 1.

-   **Source/coverage note:**
    10-etcd-health-backup-and-control-plane-troubleshooting.md --- Raft
    quorum and member failures

-   **Version note:** \[VERIFY\] intentionally defective excerpt;
    validate API fields and defaults against target version.

### U10-INC-01 --- Unit 10 --- etcd health, backup, and control-plane troubleshooting

-   **Unit/category:** Unit 10 --- etcd health, backup, and
    control-plane troubleshooting
-   **Level:** L3
-   **Objective tested:** Use evidence-first troubleshooting for control
    plane unavailable with disk alarms.
-   **Estimated time:** 15 minutes
-   **Question type:** Incident/troubleshooting
-   **Question prompt:** control plane unavailable with disk alarms.
    Describe scope and timeline, evidence to collect, competing
    hypotheses, a low-risk first test, scoped mitigation, verification,
    rollback/stop condition, and prevention.
-   **Model answer:** Confirm context, namespace, affected SLO and
    change window; capture object conditions/events/logs and recent
    changes. Investigate one etcd endpoint unreachable and compare at
    least two plausible causes. Prefer read-only evidence first; apply
    only a scoped, reversible mitigation approved for the environment.
    Verify service-level behavior and object convergence, define a stop
    condition, and record the outcome/runbook follow-up.
-   **Common wrong answers/misconceptions:** Wrong answer 1: treat
    symptom as root cause. Wrong answer 2: make a cluster-wide change
    without blast-radius analysis. Wrong answer 3: declare recovery
    without SLO/object verification.
-   **Scoring rubric:** 8 points: scope/timeline 1; evidence 2;
    differential 1; low-risk test 1; scoped mitigation/stop 1;
    verification 1; prevention/handoff 1.
-   **Source/coverage note:**
    10-etcd-health-backup-and-control-plane-troubleshooting.md ---
    control plane unavailable with disk alarms
-   **Version note:** \[VERIFY\] any destructive/provider-specific
    recovery action against exact release runbook.

### U10-DES-01 --- Unit 10 --- etcd health, backup, and control-plane troubleshooting

-   **Unit/category:** Unit 10 --- etcd health, backup, and
    control-plane troubleshooting
-   **Level:** L4
-   **Objective tested:** Design a production-ready approach for design
    etcd plus application-data recovery with explicit trade-offs.
-   **Estimated time:** 18 minutes
-   **Question type:** Design
-   **Question prompt:** design etcd plus application-data recovery.
    State constraints, compare at least two approaches, explain failure
    modes/cost/operability, and give a verification plan.
-   **Model answer:** Define the SLO, failure domains, data/security
    constraints and operating ownership. Approach A optimizes
    simplicity/cost but accepts tighter shared blast radius; approach B
    adds isolation or redundancy at higher capacity/operational cost.
    Select based on measured demand and explicit failure model. Include
    monitoring, rollback/stop criteria, staging rehearsal and a
    post-change verification signal.
-   **Common wrong answers/misconceptions:** Wrong answer 1: choose the
    most complex option without a risk case. Wrong answer 2: optimize
    cost without addressing failure domains. Wrong answer 3: rely on
    component presence rather than tested recovery.
-   **Scoring rubric:** 10 points: constraints/SLO 2; mechanism
    correctness 2; alternatives/trade-offs 2; failure handling 2;
    observability/verification 2.
-   **Source/coverage note:**
    10-etcd-health-backup-and-control-plane-troubleshooting.md ---
    expert/design topics
-   **Version note:** \[VERIFY\] implementation syntax and
    managed-provider behavior.

## Unit 11 --- Production cluster troubleshooting

### U11-SA-01 --- Unit 11 --- Production cluster troubleshooting

-   **Unit/category:** Unit 11 --- Production cluster troubleshooting
-   **Level:** L1
-   **Objective tested:** Explain the mechanism and operational
    consequence of observe hypothesize test fix verify document.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Observe hypothesize test fix verify document.
    Explain the mechanism, the trade-off, and one failure mode.
-   **Model answer:** Explain observe hypothesize test fix verify
    document by defining the mechanism, identifying the responsible
    Kubernetes layer/resource, and stating one production implication.
    Validate with the relevant object status/events rather than assuming
    the declared configuration proves runtime behavior.
-   **Common wrong answers/misconceptions:** Common misconceptions:
    Running does not mean Ready; logs/events may contain sensitive
    content. These fail because they collapse distinct mechanisms or
    claim guarantees beyond the resource/component boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:** 11-production-cluster-troubleshooting.md
    --- observe hypothesize test fix verify document
-   **Version note:** Not version-sensitive

### U11-SA-02 --- Unit 11 --- Production cluster troubleshooting

-   **Unit/category:** Unit 11 --- Production cluster troubleshooting
-   **Level:** L2
-   **Objective tested:** Explain the mechanism and operational
    consequence of Pod phase versus container reason.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Pod phase versus container reason. Explain the
    mechanism, the trade-off, and one failure mode.
-   **Model answer:** The distinction is operational: Pod phase versus
    container reason. Inspect the relevant API object, its
    conditions/events and the component that owns the decision. A
    configuration setting is not a substitute for evidence that the
    intended behavior occurred.
-   **Common wrong answers/misconceptions:** Common misconceptions:
    logs/events may contain sensitive content; events and previous logs
    are evidence. These fail because they collapse distinct mechanisms
    or claim guarantees beyond the resource/component boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:** 11-production-cluster-troubleshooting.md
    --- Pod phase versus container reason
-   **Version note:** Not version-sensitive

### U11-SA-03 --- Unit 11 --- Production cluster troubleshooting

-   **Unit/category:** Unit 11 --- Production cluster troubleshooting
-   **Level:** L3
-   **Objective tested:** Explain the mechanism and operational
    consequence of privacy-safe diagnostic bundles.
-   **Estimated time:** 5 minutes
-   **Question type:** Short answer
-   **Question prompt:** Privacy-safe diagnostic bundles. Explain the
    mechanism, the trade-off, and one failure mode.
-   **Model answer:** Use a failure model first: privacy-safe diagnostic
    bundles. State what the mechanism guarantees, what it does not
    guarantee, and which evidence would falsify your initial hypothesis.
    Record a measurable verification signal and rollback boundary.
-   **Common wrong answers/misconceptions:** Common misconceptions:
    events and previous logs are evidence; Running does not mean Ready.
    These fail because they collapse distinct mechanisms or claim
    guarantees beyond the resource/component boundary.
-   **Scoring rubric:** 3 points: correct concept 1; mechanism 1;
    operational implication/safety boundary 1.
-   **Source/coverage note:** 11-production-cluster-troubleshooting.md
    --- privacy-safe diagnostic bundles
-   **Version note:** Not version-sensitive

### U11-MCQ-01 --- Unit 11 --- Production cluster troubleshooting

-   **Unit/category:** Unit 11 --- Production cluster troubleshooting
-   **Level:** L1
-   **Objective tested:** Choose an evidence-based operational response
    to ImagePullBackOff with manifest unknown.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which response best addresses ImagePullBackOff
    with manifest unknown? Options: A. Make the broadest change
    immediately.; B. Inspect the owning resource status/events and
    confirm scope before changing state.; C. Delete the namespace.; D.
    Assume the symptom uniquely proves one root cause.
-   **Model answer:** A is incorrect (Make the broadest change
    immediately.): a broad immediate change skips diagnosis and may
    enlarge blast radius.; B is best (Inspect the owning resource
    status/events and confirm scope before changing state.): Evidence
    from the owning resource and event stream narrows the differential
    while preserving state.; C is incorrect (Delete the namespace.):
    deleting the namespace is destructive and unrelated to an
    evidence-first diagnosis.; D is incorrect (Assume the symptom
    uniquely proves one root cause.): a symptom rarely proves one unique
    root cause without corroborating evidence..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    B is the only best answer.
-   **Source/coverage note:** 11-production-cluster-troubleshooting.md
    --- observe hypothesize test fix verify document
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U11-MCQ-02 --- Unit 11 --- Production cluster troubleshooting

-   **Unit/category:** Unit 11 --- Production cluster troubleshooting
-   **Level:** L2
-   **Objective tested:** Choose an evidence-based operational response
    to Service has no endpoints despite Running Pods.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which statement about Pod phase versus
    container reason is most accurate? Options: A. events and previous
    logs are evidence; B. Running does not mean Ready; C. logs/events
    may contain sensitive content; D. The mechanism guarantees every
    dependent application outcome.
-   **Model answer:** A is incorrect (events and previous logs are
    evidence): this statement does not correctly express the lesson's
    mechanism or guarantee; it conflates a distinct control or
    overstates what the component ensures.; B is best (Running does not
    mean Ready): The correct distinction is the boundary described in
    the lesson; application-level correctness still requires independent
    verification.; C is incorrect (logs/events may contain sensitive
    content): this statement does not correctly express the lesson's
    mechanism or guarantee; it conflates a distinct control or
    overstates what the component ensures.; D is incorrect (The
    mechanism guarantees every dependent application outcome.): this
    statement does not correctly express the lesson's mechanism or
    guarantee; it conflates a distinct control or overstates what the
    component ensures..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    B is the only best answer.
-   **Source/coverage note:** 11-production-cluster-troubleshooting.md
    --- Pod phase versus container reason
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U11-MCQ-03 --- Unit 11 --- Production cluster troubleshooting

-   **Unit/category:** Unit 11 --- Production cluster troubleshooting
-   **Level:** L3
-   **Objective tested:** Choose an evidence-based operational response
    to API unavailable but processes still running.
-   **Estimated time:** 3 minutes
-   **Question type:** Multiple choice --- one best answer
-   **Question prompt:** Which evidence is strongest before changing
    policy for API unavailable but processes still running? Options: A.
    A single screenshot without timestamp.; B. Only the desired-state
    manifest.; C. Correlated status, events, recent changes,
    capacity/dependency evidence and an explicit SLO impact.; D. A guess
    based on a similar incident.
-   **Model answer:** A is incorrect (A single screenshot without
    timestamp.): a screenshot alone lacks the correlated status, event
    and timeline evidence needed for diagnosis.; B is incorrect (Only
    the desired-state manifest.): desired state alone does not prove
    observed runtime behavior or root cause.; C is best (Correlated
    status, events, recent changes, capacity/dependency evidence and an
    explicit SLO impact.): Correlated evidence supports a differential
    and helps select a scoped reversible mitigation.; D is incorrect (A
    guess based on a similar incident.): guessing from a similar
    incident is not evidence for this cluster..
-   **Common wrong answers/misconceptions:** Plausible errors: select an
    action from the wrong layer, or assume a single signal proves root
    cause. The model answer explains each distractor individually.
-   **Scoring rubric:** 2 points: correct option 1; correct reasoning 1.
    C is the only best answer.
-   **Source/coverage note:** 11-production-cluster-troubleshooting.md
    --- privacy-safe diagnostic bundles
-   **Version note:** \[VERIFY\] if applied to a version-specific field
    or command; otherwise concept-level.

### U11-OUT-01 --- Unit 11 --- Production cluster troubleshooting

-   **Unit/category:** Unit 11 --- Production cluster troubleshooting
-   **Level:** L2
-   **Objective tested:** Interpret a symptom without overstating what
    it proves about observe hypothesize test fix verify document.
-   **Estimated time:** 7 minutes
-   **Question type:** Output interpretation
-   **Question prompt:** **Illustrative output --- not observed
    execution.** Scenario: ImagePullBackOff with manifest unknown.
    Assume a current namespace/context is confirmed. The only evidence
    available is this symptom; no additional root-cause evidence has
    been supplied. State what can be concluded and what to inspect next.
-   **Model answer:** The observation supports investigation of
    ImagePullBackOff with manifest unknown, but does not uniquely
    establish root cause. Inspect the relevant object status/conditions,
    timestamped events, recent changes and the adjacent layer: events
    and previous logs are evidence. If the next evidence remains
    ambiguous, keep competing hypotheses open and perform a low-risk
    read-only test before mutation.
-   **Common wrong answers/misconceptions:** Wrong answer 1: state a
    definitive root cause from a symptom alone. Wrong answer 2: perform
    a destructive change before collecting object/event evidence.
-   **Scoring rubric:** 4 points: observed fact 1; bounded inference 1;
    next evidence 1; safe action 1.
-   **Source/coverage note:** 11-production-cluster-troubleshooting.md
    --- ImagePullBackOff with manifest unknown
-   **Version note:** \[VERIFY\] all sample output is illustrative and
    command fields vary by version.

### U11-OUT-02 --- Unit 11 --- Production cluster troubleshooting

-   **Unit/category:** Unit 11 --- Production cluster troubleshooting
-   **Level:** L3
-   **Objective tested:** Interpret a symptom without overstating what
    it proves about Pod phase versus container reason.
-   **Estimated time:** 7 minutes
-   **Question type:** Output interpretation
-   **Question prompt:** **Illustrative output --- not observed
    execution.** Scenario: Service has no endpoints despite Running
    Pods. Assume a current namespace/context is confirmed. The only
    evidence available is this symptom; no additional root-cause
    evidence has been supplied. State what can be concluded and what to
    inspect next.
-   **Model answer:** The observation supports investigation of Service
    has no endpoints despite Running Pods, but does not uniquely
    establish root cause. Inspect the relevant object status/conditions,
    timestamped events, recent changes and the adjacent layer: Running
    does not mean Ready. If the next evidence remains ambiguous, keep
    competing hypotheses open and perform a low-risk read-only test
    before mutation.
-   **Common wrong answers/misconceptions:** Wrong answer 1: state a
    definitive root cause from a symptom alone. Wrong answer 2: perform
    a destructive change before collecting object/event evidence.
-   **Scoring rubric:** 4 points: observed fact 1; bounded inference 1;
    next evidence 1; safe action 1.
-   **Source/coverage note:** 11-production-cluster-troubleshooting.md
    --- Service has no endpoints despite Running Pods
-   **Version note:** \[VERIFY\] all sample output is illustrative and
    command fields vary by version.

### U11-MAN-01 --- Unit 11 --- Production cluster troubleshooting

-   **Unit/category:** Unit 11 --- Production cluster troubleshooting

-   **Level:** L2

-   **Objective tested:** Find at least three independent defects in a
    production cluster troubleshooting configuration.

-   **Estimated time:** 10 minutes

-   **Question type:** Manifest review

-   **Question prompt:** Review this **intentionally defective training
    fixture** and identify at least three independent defects/risks.
    Give a correction plan and verification evidence. Do not apply it
    as-is.

    ``` yaml
    #!/bin/sh
    kubectl get secrets -A -o yaml > /tmp/diag.txt
    chmod 644 /tmp/diag.txt
    curl -F file=@/tmp/diag.txt https://support.example/upload
    ```

-   **Model answer:** Risks: retrieves Secret values; output is
    world-readable; automatic upload exposes credentials/customer data;
    context/scope, redaction, approval and retention are absent. Collect
    only necessary non-secret metadata/status/events, use restrictive
    permissions, redact and manually review, secure the destination, and
    require explicit approval. Base64-encoded Secret data is not safe to
    publish.

-   **Common wrong answers/misconceptions:** Wrong answer 1: treat a
    YAML parse as proof of semantic correctness. Wrong answer 2: remove
    all controls to make the workload proceed. Wrong answer 3: give a
    correction without verification.

-   **Scoring rubric:** 6 points: three independent defects 3; precise
    fixes 1; verification 1; safety/rollback 1.

-   **Source/coverage note:** 11-production-cluster-troubleshooting.md
    --- privacy-safe diagnostic bundles

-   **Version note:** \[VERIFY\] intentionally defective excerpt;
    validate API fields and defaults against target version.

### U11-MAN-02 --- Unit 11 --- Production cluster troubleshooting

-   **Unit/category:** Unit 11 --- Production cluster troubleshooting

-   **Level:** L3

-   **Objective tested:** Find at least three independent defects in a
    production cluster troubleshooting configuration.

-   **Estimated time:** 10 minutes

-   **Question type:** Manifest review

-   **Question prompt:** Review this **intentionally defective training
    fixture** and identify at least three independent defects/risks.
    Give a correction plan and verification evidence. Do not apply it
    as-is.

    ``` yaml
    #!/bin/sh
    kubectl delete pods -n production -l app=scorer
    # run automatically whenever any readiness check fails
    # no context check, evidence capture, rate limit or approval
    ```

-   **Model answer:** Risks: readiness failure does not prove restart is
    correct; broad selector can remove all replicas simultaneously; no
    context/namespace confirmation; no evidence, rate limit, approval or
    stop condition. Make automation read-only by default, capture
    events/logs/previous logs, require explicit target confirmation and
    scoped action, and verify SLO recovery with a rollback plan.

-   **Common wrong answers/misconceptions:** Wrong answer 1: treat a
    YAML parse as proof of semantic correctness. Wrong answer 2: remove
    all controls to make the workload proceed. Wrong answer 3: give a
    correction without verification.

-   **Scoring rubric:** 6 points: three independent defects 3; precise
    fixes 1; verification 1; safety/rollback 1.

-   **Source/coverage note:** 11-production-cluster-troubleshooting.md
    --- observe hypothesize test fix verify document

-   **Version note:** \[VERIFY\] intentionally defective excerpt;
    validate API fields and defaults against target version.

### U11-INC-01 --- Unit 11 --- Production cluster troubleshooting

-   **Unit/category:** Unit 11 --- Production cluster troubleshooting
-   **Level:** L3
-   **Objective tested:** Use evidence-first troubleshooting for 5xx,
    queue lag and node pressure.
-   **Estimated time:** 15 minutes
-   **Question type:** Incident/troubleshooting
-   **Question prompt:** 5xx, queue lag and node pressure. Describe
    scope and timeline, evidence to collect, competing hypotheses, a
    low-risk first test, scoped mitigation, verification, rollback/stop
    condition, and prevention.
-   **Model answer:** Confirm context, namespace, affected SLO and
    change window; capture object conditions/events/logs and recent
    changes. Investigate ImagePullBackOff with manifest unknown and
    compare at least two plausible causes. Prefer read-only evidence
    first; apply only a scoped, reversible mitigation approved for the
    environment. Verify service-level behavior and object convergence,
    define a stop condition, and record the outcome/runbook follow-up.
-   **Common wrong answers/misconceptions:** Wrong answer 1: treat
    symptom as root cause. Wrong answer 2: make a cluster-wide change
    without blast-radius analysis. Wrong answer 3: declare recovery
    without SLO/object verification.
-   **Scoring rubric:** 8 points: scope/timeline 1; evidence 2;
    differential 1; low-risk test 1; scoped mitigation/stop 1;
    verification 1; prevention/handoff 1.
-   **Source/coverage note:** 11-production-cluster-troubleshooting.md
    --- 5xx, queue lag and node pressure
-   **Version note:** \[VERIFY\] any destructive/provider-specific
    recovery action against exact release runbook.

### U11-DES-01 --- Unit 11 --- Production cluster troubleshooting

-   **Unit/category:** Unit 11 --- Production cluster troubleshooting
-   **Level:** L4
-   **Objective tested:** Design a production-ready approach for design
    on-call diagnostic workflow with explicit trade-offs.
-   **Estimated time:** 18 minutes
-   **Question type:** Design
-   **Question prompt:** design on-call diagnostic workflow. State
    constraints, compare at least two approaches, explain failure
    modes/cost/operability, and give a verification plan.
-   **Model answer:** Define the SLO, failure domains, data/security
    constraints and operating ownership. Approach A optimizes
    simplicity/cost but accepts tighter shared blast radius; approach B
    adds isolation or redundancy at higher capacity/operational cost.
    Select based on measured demand and explicit failure model. Include
    monitoring, rollback/stop criteria, staging rehearsal and a
    post-change verification signal.
-   **Common wrong answers/misconceptions:** Wrong answer 1: choose the
    most complex option without a risk case. Wrong answer 2: optimize
    cost without addressing failure domains. Wrong answer 3: rely on
    component presence rather than tested recovery.
-   **Scoring rubric:** 10 points: constraints/SLO 2; mechanism
    correctness 2; alternatives/trade-offs 2; failure handling 2;
    observability/verification 2.
-   **Source/coverage note:** 11-production-cluster-troubleshooting.md
    --- expert/design topics
-   **Version note:** \[VERIFY\] implementation syntax and
    managed-provider behavior.

### XINT-01 --- Cross-unit integration

-   **Unit/category:** Cross-unit integration
-   **Level:** L2
-   **Objective tested:** Integrate Units 2, 6, 7, 11 to diagnose a
    multi-layer production incident.
-   **Estimated time:** 12 minutes
-   **Question type:** Cross-unit incident/design decision
-   **Question prompt:** HPA raises replicas, but new Pods are Pending
    and quota denials rise. Separate scaling demand, scheduler
    constraints and namespace policy. **Units/concepts integrated:**
    Units 2, 6, 7, 11. Explain why an isolated single-unit explanation
    is insufficient.
-   **Model answer:** HPA metrics/conditions show demand; Pod events
    show placement failure; quota usage and rejected requests show
    namespace cap. Treat each layer independently, change only the
    constraint supported by evidence, and verify ready capacity and SLO.
-   **Common wrong answers/misconceptions:** Wrong answer 1: apply only
    one concept and ignore interacting constraints. Wrong answer 2: make
    a global/destructive change before evidence. Wrong answer 3: skip
    verification or data-safety checks.
-   **Scoring rubric:** 6 points: evidence across layers 2; correct
    interaction model 1; safe mitigation 1; verification 1;
    prevention/stop condition 1.
-   **Source/coverage note:** Syllabus-derived; lesson scope
    cross-checked: Units 2, 6, 7, 11.
-   **Version note:** \[VERIFY\] version/provider-specific commands and
    recovery details.

### XINT-02 --- Cross-unit integration

-   **Unit/category:** Cross-unit integration
-   **Level:** L2
-   **Objective tested:** Integrate Units 3, 4, 5, 7 to diagnose a
    multi-layer production incident.
-   **Estimated time:** 12 minutes
-   **Question type:** Cross-unit incident/design decision
-   **Question prompt:** A node drain blocks on a PDB while rollout
    readiness is degraded. Decide whether to continue maintenance.
    **Units/concepts integrated:** Units 3, 4, 5, 7. Explain why an
    isolated single-unit explanation is insufficient.
-   **Model answer:** Pause drain; inspect PDB, probes, rollout
    strategy, topology and replacement capacity. Restore healthy
    capacity or reschedule maintenance; only change policy after
    explicit availability review. Verify each batch.
-   **Common wrong answers/misconceptions:** Wrong answer 1: apply only
    one concept and ignore interacting constraints. Wrong answer 2: make
    a global/destructive change before evidence. Wrong answer 3: skip
    verification or data-safety checks.
-   **Scoring rubric:** 6 points: evidence across layers 2; correct
    interaction model 1; safe mitigation 1; verification 1;
    prevention/stop condition 1.
-   **Source/coverage note:** Syllabus-derived; lesson scope
    cross-checked: Units 3, 4, 5, 7.
-   **Version note:** \[VERIFY\] version/provider-specific commands and
    recovery details.

### XINT-03 --- Cross-unit integration

-   **Unit/category:** Cross-unit integration
-   **Level:** L2
-   **Objective tested:** Integrate Units 4, 6, 11 to diagnose a
    multi-layer production incident.
-   **Estimated time:** 12 minutes
-   **Question type:** Cross-unit incident/design decision
-   **Question prompt:** CronJob overlaps with retrying ETL and
    duplicate partitions appear while queue lag rises. What controls are
    missing? **Units/concepts integrated:** Units 4, 6, 11. Explain why
    an isolated single-unit explanation is insufficient.
-   **Model answer:** Inspect Job history, schedule/concurrency,
    idempotency/checkpoints, queue age and consumer throughput. Bound
    overlap/retries and implement durable idempotency; verify partition
    uniqueness and backlog recovery.
-   **Common wrong answers/misconceptions:** Wrong answer 1: apply only
    one concept and ignore interacting constraints. Wrong answer 2: make
    a global/destructive change before evidence. Wrong answer 3: skip
    verification or data-safety checks.
-   **Scoring rubric:** 6 points: evidence across layers 2; correct
    interaction model 1; safe mitigation 1; verification 1;
    prevention/stop condition 1.
-   **Source/coverage note:** Syllabus-derived; lesson scope
    cross-checked: Units 4, 6, 11.
-   **Version note:** \[VERIFY\] version/provider-specific commands and
    recovery details.

### XINT-04 --- Cross-unit integration

-   **Unit/category:** Cross-unit integration
-   **Level:** L2
-   **Objective tested:** Integrate Units 8, 9, 11 to diagnose a
    multi-layer production incident.
-   **Estimated time:** 12 minutes
-   **Question type:** Cross-unit incident/design decision
-   **Question prompt:** Admission rejects a Pod after upgrade although
    RBAC allows create. Diagnose without weakening controls globally.
    **Units/concepts integrated:** Units 8, 9, 11. Explain why an
    isolated single-unit explanation is insufficient.
-   **Model answer:** Capture exact denial, identity/context, PSA
    namespace labels/version, securityContext and upgrade timeline. Fix
    manifest or use approved scoped exception; verify admission and
    runtime behavior.
-   **Common wrong answers/misconceptions:** Wrong answer 1: apply only
    one concept and ignore interacting constraints. Wrong answer 2: make
    a global/destructive change before evidence. Wrong answer 3: skip
    verification or data-safety checks.
-   **Scoring rubric:** 6 points: evidence across layers 2; correct
    interaction model 1; safe mitigation 1; verification 1;
    prevention/stop condition 1.
-   **Source/coverage note:** Syllabus-derived; lesson scope
    cross-checked: Units 8, 9, 11.
-   **Version note:** \[VERIFY\] version/provider-specific commands and
    recovery details.

### XINT-05 --- Cross-unit integration

-   **Unit/category:** Cross-unit integration
-   **Level:** L3
-   **Objective tested:** Integrate Units 1, 3, 9, 10, 11 to diagnose a
    multi-layer production incident.
-   **Estimated time:** 18 minutes
-   **Question type:** Cross-unit incident/design decision
-   **Question prompt:** API errors coincide with etcd latency, probe
    failures and webhook timeouts. Build a differential and containment
    plan. **Units/concepts integrated:** Units 1, 3, 9, 10, 11. Explain
    why an isolated single-unit explanation is insufficient.
-   **Model answer:** Correlate timestamps across API, etcd, webhook
    endpoints/certificates, probe logs and dependencies. Do not assume
    one cause; use authorized/provider evidence, scoped mitigation and
    post-recovery API/readiness/admission checks.
-   **Common wrong answers/misconceptions:** Wrong answer 1: apply only
    one concept and ignore interacting constraints. Wrong answer 2: make
    a global/destructive change before evidence. Wrong answer 3: skip
    verification or data-safety checks.
-   **Scoring rubric:** 6 points: evidence across layers 2; correct
    interaction model 1; safe mitigation 1; verification 1;
    prevention/stop condition 1.
-   **Source/coverage note:** Syllabus-derived; lesson scope
    cross-checked: Units 1, 3, 9, 10, 11.
-   **Version note:** \[VERIFY\] version/provider-specific commands and
    recovery details.

### XINT-06 --- Cross-unit integration

-   **Unit/category:** Cross-unit integration
-   **Level:** L3
-   **Objective tested:** Integrate Units 4, 5, 7, 8 to diagnose a
    multi-layer production incident.
-   **Estimated time:** 18 minutes
-   **Question type:** Cross-unit incident/design decision
-   **Question prompt:** Upgrade is planned while a stateful replica is
    unhealthy and PDB allows no disruption. Go or no-go?
    **Units/concepts integrated:** Units 4, 5, 7, 8. Explain why an
    isolated single-unit explanation is insufficient.
-   **Model answer:** No-go until state/storage health, PDB, topology,
    capacity, compatibility and restore evidence are understood. Canary
    only after readiness and stop gates pass.
-   **Common wrong answers/misconceptions:** Wrong answer 1: apply only
    one concept and ignore interacting constraints. Wrong answer 2: make
    a global/destructive change before evidence. Wrong answer 3: skip
    verification or data-safety checks.
-   **Scoring rubric:** 6 points: evidence across layers 2; correct
    interaction model 1; safe mitigation 1; verification 1;
    prevention/stop condition 1.
-   **Source/coverage note:** Syllabus-derived; lesson scope
    cross-checked: Units 4, 5, 7, 8.
-   **Version note:** \[VERIFY\] version/provider-specific commands and
    recovery details.

### XINT-07 --- Cross-unit integration

-   **Unit/category:** Cross-unit integration
-   **Level:** L3
-   **Objective tested:** Integrate Units 4, 8, 10 to diagnose a
    multi-layer production incident.
-   **Estimated time:** 18 minutes
-   **Question type:** Cross-unit incident/design decision
-   **Question prompt:** Recent etcd snapshot exists, but PV data is not
    backed up and no restore test has run. Does a 30-minute RTO have
    evidence? **Units/concepts integrated:** Units 4, 8, 10. Explain why
    an isolated single-unit explanation is insufficient.
-   **Model answer:** No. etcd snapshot is not PV backup and no timed
    drill proves tooling, consistency or RTO. Add protected off-node
    copies, separate application-data recovery and a version-compatible
    timed restore rehearsal.
-   **Common wrong answers/misconceptions:** Wrong answer 1: apply only
    one concept and ignore interacting constraints. Wrong answer 2: make
    a global/destructive change before evidence. Wrong answer 3: skip
    verification or data-safety checks.
-   **Scoring rubric:** 6 points: evidence across layers 2; correct
    interaction model 1; safe mitigation 1; verification 1;
    prevention/stop condition 1.
-   **Source/coverage note:** Syllabus-derived; lesson scope
    cross-checked: Units 4, 8, 10.
-   **Version note:** \[VERIFY\] version/provider-specific commands and
    recovery details.

### XINT-08 --- Cross-unit integration

-   **Unit/category:** Cross-unit integration
-   **Level:** L3
-   **Objective tested:** Integrate Units 3, 4, 11 to diagnose a
    multi-layer production incident.
-   **Estimated time:** 18 minutes
-   **Question type:** Cross-unit incident/design decision
-   **Question prompt:** Service has no endpoints; Pods are Running but
    not Ready after a model rollout. What sequence avoids blaming DNS
    prematurely? **Units/concepts integrated:** Units 3, 4, 11. Explain
    why an isolated single-unit explanation is insufficient.
-   **Model answer:** Inspect rollout/image version, readiness
    events/logs, Pod labels/Service selector, EndpointSlice, then
    request path/DNS. Distinguish startup, selector and network failure;
    rollback only after data compatibility review.
-   **Common wrong answers/misconceptions:** Wrong answer 1: apply only
    one concept and ignore interacting constraints. Wrong answer 2: make
    a global/destructive change before evidence. Wrong answer 3: skip
    verification or data-safety checks.
-   **Scoring rubric:** 6 points: evidence across layers 2; correct
    interaction model 1; safe mitigation 1; verification 1;
    prevention/stop condition 1.
-   **Source/coverage note:** Syllabus-derived; lesson scope
    cross-checked: Units 3, 4, 11.
-   **Version note:** \[VERIFY\] version/provider-specific commands and
    recovery details.

### XINT-09 --- Cross-unit integration

-   **Unit/category:** Cross-unit integration
-   **Level:** L3
-   **Objective tested:** Integrate Units 2, 3, 6, 11 to diagnose a
    multi-layer production incident.
-   **Estimated time:** 18 minutes
-   **Question type:** Cross-unit incident/design decision
-   **Question prompt:** HPA and VPA both change behavior; replicas
    oscillate and OOMs rise. Stabilize safely. **Units/concepts
    integrated:** Units 2, 3, 6, 11. Explain why an isolated single-unit
    explanation is insufficient.
-   **Model answer:** Correlate metrics, VPA mode, request changes, OOM
    events and startup. Verify supported combination; consider
    recommendation-only VPA or better signal/stabilization. Make one
    controlled change and measure SLO/resource outcomes.
-   **Common wrong answers/misconceptions:** Wrong answer 1: apply only
    one concept and ignore interacting constraints. Wrong answer 2: make
    a global/destructive change before evidence. Wrong answer 3: skip
    verification or data-safety checks.
-   **Scoring rubric:** 6 points: evidence across layers 2; correct
    interaction model 1; safe mitigation 1; verification 1;
    prevention/stop condition 1.
-   **Source/coverage note:** Syllabus-derived; lesson scope
    cross-checked: Units 2, 3, 6, 11.
-   **Version note:** \[VERIFY\] version/provider-specific commands and
    recovery details.

### XINT-10 --- Cross-unit integration

-   **Unit/category:** Cross-unit integration
-   **Level:** L3
-   **Objective tested:** Integrate Units 7, 9, 11 to diagnose a
    multi-layer production incident.
-   **Estimated time:** 18 minutes
-   **Question type:** Cross-unit incident/design decision
-   **Question prompt:** Queue consumer has an overprivileged long-lived
    token and runs on a shared pool. Design containment.
    **Units/concepts integrated:** Units 7, 9, 11. Explain why an
    isolated single-unit explanation is insufficient.
-   **Model answer:** Preserve audit evidence, rotate/revoke through
    approved procedures, narrow ServiceAccount permissions/token
    exposure, consider placement isolation, then verify access/function.
    Taints are not authorization controls.
-   **Common wrong answers/misconceptions:** Wrong answer 1: apply only
    one concept and ignore interacting constraints. Wrong answer 2: make
    a global/destructive change before evidence. Wrong answer 3: skip
    verification or data-safety checks.
-   **Scoring rubric:** 6 points: evidence across layers 2; correct
    interaction model 1; safe mitigation 1; verification 1;
    prevention/stop condition 1.
-   **Source/coverage note:** Syllabus-derived; lesson scope
    cross-checked: Units 7, 9, 11.
-   **Version note:** \[VERIFY\] version/provider-specific commands and
    recovery details.

### XINT-11 --- Cross-unit integration

-   **Unit/category:** Cross-unit integration
-   **Level:** L3
-   **Objective tested:** Integrate Units 1, 4, 11 to diagnose a
    multi-layer production incident.
-   **Estimated time:** 18 minutes
-   **Question type:** Cross-unit incident/design decision
-   **Question prompt:** CronJob misses schedules during API outage and
    later multiple Jobs appear. What before cleanup? **Units/concepts
    integrated:** Units 1, 4, 11. Explain why an isolated single-unit
    explanation is insufficient.
-   **Model answer:** Inspect controller/event timeline,
    deadlines/concurrency, Job history and external side effects.
    Reconcile durable checkpoints before deleting anything; verify
    idempotency and adjust bounded schedule policy.
-   **Common wrong answers/misconceptions:** Wrong answer 1: apply only
    one concept and ignore interacting constraints. Wrong answer 2: make
    a global/destructive change before evidence. Wrong answer 3: skip
    verification or data-safety checks.
-   **Scoring rubric:** 6 points: evidence across layers 2; correct
    interaction model 1; safe mitigation 1; verification 1;
    prevention/stop condition 1.
-   **Source/coverage note:** Syllabus-derived; lesson scope
    cross-checked: Units 1, 4, 11.
-   **Version note:** \[VERIFY\] version/provider-specific commands and
    recovery details.

### XINT-12 --- Cross-unit integration

-   **Unit/category:** Cross-unit integration
-   **Level:** L3
-   **Objective tested:** Integrate Units 2, 7, 8, 11 to diagnose a
    multi-layer production incident.
-   **Estimated time:** 18 minutes
-   **Question type:** Cross-unit incident/design decision
-   **Question prompt:** GPU Pod remains Pending after node-pool
    rotation despite affinity and toleration. Find the mismatch.
    **Units/concepts integrated:** Units 2, 7, 8, 11. Explain why an
    isolated single-unit explanation is insufficient.
-   **Model answer:** Check scheduler events, actual labels/taints, GPU
    resource capacity, allocatable, quota and add-on compatibility.
    Toleration does not attract the Pod or supply GPU; correct pool
    metadata/capacity and verify placement.
-   **Common wrong answers/misconceptions:** Wrong answer 1: apply only
    one concept and ignore interacting constraints. Wrong answer 2: make
    a global/destructive change before evidence. Wrong answer 3: skip
    verification or data-safety checks.
-   **Scoring rubric:** 6 points: evidence across layers 2; correct
    interaction model 1; safe mitigation 1; verification 1;
    prevention/stop condition 1.
-   **Source/coverage note:** Syllabus-derived; lesson scope
    cross-checked: Units 2, 7, 8, 11.
-   **Version note:** \[VERIFY\] version/provider-specific commands and
    recovery details.

### XINT-13 --- Cross-unit integration

-   **Unit/category:** Cross-unit integration
-   **Level:** L3
-   **Objective tested:** Integrate Units 3, 4, 5, 9 to diagnose a
    multi-layer production incident.
-   **Estimated time:** 18 minutes
-   **Question type:** Cross-unit incident/design decision
-   **Question prompt:** Security admission blocks rollout while PDB and
    rollout strategy limit replacement capacity. Safe sequence?
    **Units/concepts integrated:** Units 3, 4, 5, 9. Explain why an
    isolated single-unit explanation is insufficient.
-   **Model answer:** Inspect denial, policy labels, Pod security
    settings, readiness, PDB and surge capacity. Remediate manifest and
    test staged policy enforcement; do not weaken PDB/security globally
    as a shortcut.
-   **Common wrong answers/misconceptions:** Wrong answer 1: apply only
    one concept and ignore interacting constraints. Wrong answer 2: make
    a global/destructive change before evidence. Wrong answer 3: skip
    verification or data-safety checks.
-   **Scoring rubric:** 6 points: evidence across layers 2; correct
    interaction model 1; safe mitigation 1; verification 1;
    prevention/stop condition 1.
-   **Source/coverage note:** Syllabus-derived; lesson scope
    cross-checked: Units 3, 4, 5, 9.
-   **Version note:** \[VERIFY\] version/provider-specific commands and
    recovery details.

### XINT-14 --- Cross-unit integration

-   **Unit/category:** Cross-unit integration
-   **Level:** L3
-   **Objective tested:** Integrate Units 4, 8, 10 to diagnose a
    multi-layer production incident.
-   **Estimated time:** 18 minutes
-   **Question type:** Cross-unit incident/design decision
-   **Question prompt:** Restore rehearsal brings control plane back but
    StatefulSet has stale app state. What did test reveal?
    **Units/concepts integrated:** Units 4, 8, 10. Explain why an
    isolated single-unit explanation is insufficient.
-   **Model answer:** Cluster-state recovery and application-data
    recovery are distinct. Inspect PV consistency, snapshot timestamps,
    schema/queue checkpoints and reconciliation; coordinate backups and
    retest RPO/RTO.
-   **Common wrong answers/misconceptions:** Wrong answer 1: apply only
    one concept and ignore interacting constraints. Wrong answer 2: make
    a global/destructive change before evidence. Wrong answer 3: skip
    verification or data-safety checks.
-   **Scoring rubric:** 6 points: evidence across layers 2; correct
    interaction model 1; safe mitigation 1; verification 1;
    prevention/stop condition 1.
-   **Source/coverage note:** Syllabus-derived; lesson scope
    cross-checked: Units 4, 8, 10.
-   **Version note:** \[VERIFY\] version/provider-specific commands and
    recovery details.

### XINT-15 --- Cross-unit integration

-   **Unit/category:** Cross-unit integration
-   **Level:** L3
-   **Objective tested:** Integrate Units 1, 8, 9, 11 to diagnose a
    multi-layer production incident.
-   **Estimated time:** 18 minutes
-   **Question type:** Cross-unit incident/design decision
-   **Question prompt:** After upgrade, webhook times out and new Pods
    fail admission while old Pods serve. What safeguards?
    **Units/concepts integrated:** Units 1, 8, 9, 11. Explain why an
    isolated single-unit explanation is insufficient.
-   **Model answer:** Freeze rollout; inspect webhook endpoints,
    certificates, API config, compatibility and failure policy. Protect
    existing workload, apply approved fix/rollback with security review,
    then verify new admission and SLO.
-   **Common wrong answers/misconceptions:** Wrong answer 1: apply only
    one concept and ignore interacting constraints. Wrong answer 2: make
    a global/destructive change before evidence. Wrong answer 3: skip
    verification or data-safety checks.
-   **Scoring rubric:** 6 points: evidence across layers 2; correct
    interaction model 1; safe mitigation 1; verification 1;
    prevention/stop condition 1.
-   **Source/coverage note:** Syllabus-derived; lesson scope
    cross-checked: Units 1, 8, 9, 11.
-   **Version note:** \[VERIFY\] version/provider-specific commands and
    recovery details.

### XINT-16 --- Cross-unit integration

-   **Unit/category:** Cross-unit integration
-   **Level:** L3
-   **Objective tested:** Integrate Units 2, 3, 6, 7, 11 to diagnose a
    multi-layer production incident.
-   **Estimated time:** 18 minutes
-   **Question type:** Cross-unit incident/design decision
-   **Question prompt:** Node memory pressure, OOMKilled containers, HPA
    scale-out and Pending replacements occur together. Explain
    mechanisms. **Units/concepts integrated:** Units 2, 3, 6, 7, 11.
    Explain why an isolated single-unit explanation is insufficient.
-   **Model answer:** Memory limits can cause OOM; node pressure can
    cause eviction; HPA adds Pod demand but not nodes. Inspect events,
    requests/limits, allocatable, quota and placement; mitigate
    load/capacity and verify SLO.
-   **Common wrong answers/misconceptions:** Wrong answer 1: apply only
    one concept and ignore interacting constraints. Wrong answer 2: make
    a global/destructive change before evidence. Wrong answer 3: skip
    verification or data-safety checks.
-   **Scoring rubric:** 6 points: evidence across layers 2; correct
    interaction model 1; safe mitigation 1; verification 1;
    prevention/stop condition 1.
-   **Source/coverage note:** Syllabus-derived; lesson scope
    cross-checked: Units 2, 3, 6, 7, 11.
-   **Version note:** \[VERIFY\] version/provider-specific commands and
    recovery details.

### XINT-17 --- Cross-unit integration

-   **Unit/category:** Cross-unit integration
-   **Level:** L3
-   **Objective tested:** Integrate Units 2, 5, 6, 7 to diagnose a
    multi-layer production incident.
-   **Estimated time:** 18 minutes
-   **Question type:** Cross-unit incident/design decision
-   **Question prompt:** Quota raised for rollout causes ETL to starve
    API. How should governance change? **Units/concepts integrated:**
    Units 2, 5, 6, 7. Explain why an isolated single-unit explanation is
    insufficient.
-   **Model answer:** Review percentiles, requests/limits, quota,
    priority, pool capacity and SLO. Create fair budgets/headroom/surge
    assumptions and validate under burst and maintenance; quota alone is
    not isolation.
-   **Common wrong answers/misconceptions:** Wrong answer 1: apply only
    one concept and ignore interacting constraints. Wrong answer 2: make
    a global/destructive change before evidence. Wrong answer 3: skip
    verification or data-safety checks.
-   **Scoring rubric:** 6 points: evidence across layers 2; correct
    interaction model 1; safe mitigation 1; verification 1;
    prevention/stop condition 1.
-   **Source/coverage note:** Syllabus-derived; lesson scope
    cross-checked: Units 2, 5, 6, 7.
-   **Version note:** \[VERIFY\] version/provider-specific commands and
    recovery details.

### XINT-18 --- Cross-unit integration

-   **Unit/category:** Cross-unit integration
-   **Level:** L3
-   **Objective tested:** Integrate Units 3, 6, 11 to diagnose a
    multi-layer production incident.
-   **Estimated time:** 18 minutes
-   **Question type:** Cross-unit incident/design decision
-   **Question prompt:** Liveness restarts all API replicas during
    feature-store slowdown while HPA sees CPU spikes. Response?
    **Units/concepts integrated:** Units 3, 6, 11. Explain why an
    isolated single-unit explanation is insufficient.
-   **Model answer:** Correlate dependency latency, probe failures,
    restart rate and HPA metrics. Separate local liveness from serving
    readiness; protect traffic and stabilize scaling after accounting
    for metric lag. Verify ready capacity and latency.
-   **Common wrong answers/misconceptions:** Wrong answer 1: apply only
    one concept and ignore interacting constraints. Wrong answer 2: make
    a global/destructive change before evidence. Wrong answer 3: skip
    verification or data-safety checks.
-   **Scoring rubric:** 6 points: evidence across layers 2; correct
    interaction model 1; safe mitigation 1; verification 1;
    prevention/stop condition 1.
-   **Source/coverage note:** Syllabus-derived; lesson scope
    cross-checked: Units 3, 6, 11.
-   **Version note:** \[VERIFY\] version/provider-specific commands and
    recovery details.

### XINT-19 --- Cross-unit integration

-   **Unit/category:** Cross-unit integration
-   **Level:** L3
-   **Objective tested:** Integrate Units 1, 8, 10, 11 to diagnose a
    multi-layer production incident.
-   **Estimated time:** 18 minutes
-   **Question type:** Cross-unit incident/design decision
-   **Question prompt:** Managed cluster API is unavailable but worker
    workloads still serve. What can be inferred and who owns recovery?
    **Units/concepts integrated:** Units 1, 8, 10, 11. Explain why an
    isolated single-unit explanation is insufficient.
-   **Model answer:** Existing containers may continue while
    API/reconciliation is impaired; this proves neither etcd health nor
    full recovery. Use provider status/approved telemetry, avoid
    self-managed etcd commands, and verify API/controllers after
    restoration.
-   **Common wrong answers/misconceptions:** Wrong answer 1: apply only
    one concept and ignore interacting constraints. Wrong answer 2: make
    a global/destructive change before evidence. Wrong answer 3: skip
    verification or data-safety checks.
-   **Scoring rubric:** 6 points: evidence across layers 2; correct
    interaction model 1; safe mitigation 1; verification 1;
    prevention/stop condition 1.
-   **Source/coverage note:** Syllabus-derived; lesson scope
    cross-checked: Units 1, 8, 10, 11.
-   **Version note:** \[VERIFY\] version/provider-specific commands and
    recovery details.

### XINT-20 --- Cross-unit integration

-   **Unit/category:** Cross-unit integration
-   **Level:** L3
-   **Objective tested:** Integrate Units 1, 7, 8 to diagnose a
    multi-layer production incident.
-   **Estimated time:** 18 minutes
-   **Question type:** Cross-unit incident/design decision
-   **Question prompt:** kind CI passes but production CSI and node-pool
    behavior fails. What test gap exists? **Units/concepts integrated:**
    Units 1, 7, 8. Explain why an isolated single-unit explanation is
    insufficient.
-   **Model answer:** kind tests selected local behaviors, not every
    provider control plane, CSI/CNI or cloud failure domain. Add
    target-version compatibility, staging integration and provider
    preflight; retain kind for fast feedback but do not claim parity.
-   **Common wrong answers/misconceptions:** Wrong answer 1: apply only
    one concept and ignore interacting constraints. Wrong answer 2: make
    a global/destructive change before evidence. Wrong answer 3: skip
    verification or data-safety checks.
-   **Scoring rubric:** 6 points: evidence across layers 2; correct
    interaction model 1; safe mitigation 1; verification 1;
    prevention/stop condition 1.
-   **Source/coverage note:** Syllabus-derived; lesson scope
    cross-checked: Units 1, 7, 8.
-   **Version note:** \[VERIFY\] version/provider-specific commands and
    recovery details.

### XINT-21 --- Cross-unit integration

-   **Unit/category:** Cross-unit integration
-   **Level:** L3
-   **Objective tested:** Integrate Units 9, 11 to diagnose a
    multi-layer production incident.
-   **Estimated time:** 18 minutes
-   **Question type:** Cross-unit incident/design decision
-   **Question prompt:** Diagnostic bundle during RBAC incident may
    include sensitive annotations in descriptions. How handle evidence?
    **Units/concepts integrated:** Units 9, 11. Explain why an isolated
    single-unit explanation is insufficient.
-   **Model answer:** Minimize data, avoid Secret values, restrict
    permissions/destination, inspect and redact manually, set retention,
    and preserve audit evidence. Automated redaction is imperfect.
-   **Common wrong answers/misconceptions:** Wrong answer 1: apply only
    one concept and ignore interacting constraints. Wrong answer 2: make
    a global/destructive change before evidence. Wrong answer 3: skip
    verification or data-safety checks.
-   **Scoring rubric:** 6 points: evidence across layers 2; correct
    interaction model 1; safe mitigation 1; verification 1;
    prevention/stop condition 1.
-   **Source/coverage note:** Syllabus-derived; lesson scope
    cross-checked: Units 9, 11.
-   **Version note:** \[VERIFY\] version/provider-specific commands and
    recovery details.

### XINT-22 --- Cross-unit integration

-   **Unit/category:** Cross-unit integration
-   **Level:** L3
-   **Objective tested:** Integrate Units 5, 7 to diagnose a multi-layer
    production incident.
-   **Estimated time:** 18 minutes
-   **Question type:** Cross-unit incident/design decision
-   **Question prompt:** PDB permits one disruption but topology leaves
    no eligible replacement. Why is PDB insufficient? **Units/concepts
    integrated:** Units 5, 7. Explain why an isolated single-unit
    explanation is insufficient.
-   **Model answer:** PDB governs voluntary disruption budget, not
    scheduler feasibility. Check constraints, labels/taints, requests
    and domain capacity; provision eligible replacement capacity and
    rehearse drain.
-   **Common wrong answers/misconceptions:** Wrong answer 1: apply only
    one concept and ignore interacting constraints. Wrong answer 2: make
    a global/destructive change before evidence. Wrong answer 3: skip
    verification or data-safety checks.
-   **Scoring rubric:** 6 points: evidence across layers 2; correct
    interaction model 1; safe mitigation 1; verification 1;
    prevention/stop condition 1.
-   **Source/coverage note:** Syllabus-derived; lesson scope
    cross-checked: Units 5, 7.
-   **Version note:** \[VERIFY\] version/provider-specific commands and
    recovery details.

### XINT-23 --- Cross-unit integration

-   **Unit/category:** Cross-unit integration
-   **Level:** L3
-   **Objective tested:** Integrate Units 2, 4, 5, 9 to diagnose a
    multi-layer production incident.
-   **Estimated time:** 18 minutes
-   **Question type:** Cross-unit incident/design decision
-   **Question prompt:** Rollout blocked by quota and new security
    policy; old image is vulnerable. What decision record is needed?
    **Units/concepts integrated:** Units 2, 4, 5, 9. Explain why an
    isolated single-unit explanation is insufficient.
-   **Model answer:** Record vulnerability severity, denial, SLO/old
    capacity, quota headroom, compliant remediation, scoped exception
    owner/expiry and rollback. Prefer compliant fix and approved
    capacity; verify patched version and close exception.
-   **Common wrong answers/misconceptions:** Wrong answer 1: apply only
    one concept and ignore interacting constraints. Wrong answer 2: make
    a global/destructive change before evidence. Wrong answer 3: skip
    verification or data-safety checks.
-   **Scoring rubric:** 6 points: evidence across layers 2; correct
    interaction model 1; safe mitigation 1; verification 1;
    prevention/stop condition 1.
-   **Source/coverage note:** Syllabus-derived; lesson scope
    cross-checked: Units 2, 4, 5, 9.
-   **Version note:** \[VERIFY\] version/provider-specific commands and
    recovery details.

### XINT-24 --- Cross-unit integration

-   **Unit/category:** Cross-unit integration
-   **Level:** L4
-   **Objective tested:** Integrate Units 4, 5, 7, 10, 11 to diagnose a
    multi-layer production incident.
-   **Estimated time:** 18 minutes
-   **Question type:** Cross-unit incident/design decision
-   **Question prompt:** Node failure leaves StatefulSet Pods Pending
    while API serves with lower cache hit rate. Recover without risking
    persistent data. **Units/concepts integrated:** Units 4, 5, 7,
    10, 11. Explain why an isolated single-unit explanation is
    insufficient.
-   **Model answer:** Inspect node/PVC events, StatefulSet identity,
    storage topology, replication and backups before force detach.
    Follow CSI/provider procedure, protect data, restore service and
    verify durable state.
-   **Common wrong answers/misconceptions:** Wrong answer 1: apply only
    one concept and ignore interacting constraints. Wrong answer 2: make
    a global/destructive change before evidence. Wrong answer 3: skip
    verification or data-safety checks.
-   **Scoring rubric:** 6 points: evidence across layers 2; correct
    interaction model 1; safe mitigation 1; verification 1;
    prevention/stop condition 1.
-   **Source/coverage note:** Syllabus-derived; lesson scope
    cross-checked: Units 4, 5, 7, 10, 11.
-   **Version note:** \[VERIFY\] version/provider-specific commands and
    recovery details.

### XINT-25 --- Cross-unit integration

-   **Unit/category:** Cross-unit integration
-   **Level:** L4
-   **Objective tested:** Integrate Units 3, 4, 8 to diagnose a
    multi-layer production incident.
-   **Estimated time:** 18 minutes
-   **Question type:** Cross-unit incident/design decision
-   **Question prompt:** Upgrade changes probe field/behavior and cold
    model servers restart. What compare? **Units/concepts integrated:**
    Units 3, 4, 8. Explain why an isolated single-unit explanation is
    insufficient.
-   **Model answer:** Compare release notes/schema, startup
    distribution, probe timing/events and workload/add-on changes.
    Freeze rollout, make compatible correction or approved rollback, and
    test cold starts.
-   **Common wrong answers/misconceptions:** Wrong answer 1: apply only
    one concept and ignore interacting constraints. Wrong answer 2: make
    a global/destructive change before evidence. Wrong answer 3: skip
    verification or data-safety checks.
-   **Scoring rubric:** 6 points: evidence across layers 2; correct
    interaction model 1; safe mitigation 1; verification 1;
    prevention/stop condition 1.
-   **Source/coverage note:** Syllabus-derived; lesson scope
    cross-checked: Units 3, 4, 8.
-   **Version note:** \[VERIFY\] version/provider-specific commands and
    recovery details.

### XINT-26 --- Cross-unit integration

-   **Unit/category:** Cross-unit integration
-   **Level:** L4
-   **Objective tested:** Integrate Units 2, 6, 7, 11 to diagnose a
    multi-layer production incident.
-   **Estimated time:** 18 minutes
-   **Question type:** Cross-unit incident/design decision
-   **Question prompt:** Nightly ETL CPU use throttles API; HPA adds
    replicas that stay Pending. Design mitigation. **Units/concepts
    integrated:** Units 2, 6, 7, 11. Explain why an isolated single-unit
    explanation is insufficient.
-   **Model answer:** Measure throttling, requests/limits, queue/latency
    and allocatable; use fair quotas, concurrency limits and justified
    dedicated pools; verify HPA signal. Shape batch load or add capacity
    while protecting data correctness.
-   **Common wrong answers/misconceptions:** Wrong answer 1: apply only
    one concept and ignore interacting constraints. Wrong answer 2: make
    a global/destructive change before evidence. Wrong answer 3: skip
    verification or data-safety checks.
-   **Scoring rubric:** 6 points: evidence across layers 2; correct
    interaction model 1; safe mitigation 1; verification 1;
    prevention/stop condition 1.
-   **Source/coverage note:** Syllabus-derived; lesson scope
    cross-checked: Units 2, 6, 7, 11.
-   **Version note:** \[VERIFY\] version/provider-specific commands and
    recovery details.

### XINT-27 --- Cross-unit integration

-   **Unit/category:** Cross-unit integration
-   **Level:** L4
-   **Objective tested:** Integrate Units 1, 5, 8, 10, 11 to diagnose a
    multi-layer production incident.
-   **Estimated time:** 18 minutes
-   **Question type:** Cross-unit incident/design decision
-   **Question prompt:** Self-managed control plane loses etcd quorum
    during maintenance. What must the incident commander avoid and
    require? **Units/concepts integrated:** Units 1, 5, 8, 10, 11.
    Explain why an isolated single-unit explanation is insufficient.
-   **Model answer:** Avoid improvised member removal/restore. Confirm
    topology/version, member health, backup integrity and data-loss
    risk; follow approved release-specific recovery with isolated target
    and stop conditions; verify API and data.
-   **Common wrong answers/misconceptions:** Wrong answer 1: apply only
    one concept and ignore interacting constraints. Wrong answer 2: make
    a global/destructive change before evidence. Wrong answer 3: skip
    verification or data-safety checks.
-   **Scoring rubric:** 6 points: evidence across layers 2; correct
    interaction model 1; safe mitigation 1; verification 1;
    prevention/stop condition 1.
-   **Source/coverage note:** Syllabus-derived; lesson scope
    cross-checked: Units 1, 5, 8, 10, 11.
-   **Version note:** \[VERIFY\] version/provider-specific commands and
    recovery details.

### XINT-28 --- Cross-unit integration

-   **Unit/category:** Cross-unit integration
-   **Level:** L4
-   **Objective tested:** Integrate Units 1, 3, 5, 6, 7, 10 to diagnose
    a multi-layer production incident.
-   **Estimated time:** 18 minutes
-   **Question type:** Cross-unit incident/design decision
-   **Question prompt:** Team claims 99.99% availability from three
    replicas, PDB, HPA and snapshots. Evaluate evidence.
    **Units/concepts integrated:** Units 1, 3, 5, 6, 7, 10. Explain why
    an isolated single-unit explanation is insufficient.
-   **Model answer:** Components do not prove SLO. Require
    failure-domain placement, probe correctness, capacity, dependency
    resilience, drain/scaling tests, restore drills and measured
    error-budget data; validate through game days.
-   **Common wrong answers/misconceptions:** Wrong answer 1: apply only
    one concept and ignore interacting constraints. Wrong answer 2: make
    a global/destructive change before evidence. Wrong answer 3: skip
    verification or data-safety checks.
-   **Scoring rubric:** 6 points: evidence across layers 2; correct
    interaction model 1; safe mitigation 1; verification 1;
    prevention/stop condition 1.
-   **Source/coverage note:** Syllabus-derived; lesson scope
    cross-checked: Units 1, 3, 5, 6, 7, 10.
-   **Version note:** \[VERIFY\] version/provider-specific commands and
    recovery details.

## Ten design-review whiteboard prompts

### WB-01 --- Single large cluster versus multiple smaller clusters

-   **Context and constraints:** Several teams differ in data
    sensitivity, SLO and cost; SRE staff is limited.
-   **Plausible approaches:** A: one cluster with
    namespaces/quota/RBAC/policy. B: clusters split by trust boundary,
    region or workload class.
-   **Key trade-offs:** A lowers baseline duplication but increases
    shared blast radius; B improves isolation and upgrade autonomy but
    increases cost and fleet complexity.
-   **Answer outline:** Define threat model, SLOs, network/storage
    boundaries, control-plane ownership, upgrade policy and DR. Choose
    boundaries by risk evidence.
-   **Scoring rubric:** 10 points: constraints 2; isolation 2;
    cost/operations 2; upgrade/DR 2; decision evidence 2.

### WB-02 --- HA control-plane sizing and failure domains

-   **Context and constraints:** Critical self-managed control plane
    must tolerate one member or host failure.
-   **Plausible approaches:** A: three etcd/control-plane members spread
    across independent domains. B: managed control plane with provider
    commitments and customer-owned worker/add-on resilience.
-   **Key trade-offs:** A gives control but requires quorum, patching,
    certificates and restore operations; B shifts ownership and
    visibility. Node count alone does not prove independent domains.
-   **Answer outline:** State failure model, quorum, placement, network,
    backups, monitoring, ownership and timed recovery exercise.
-   **Scoring rubric:** 10 points: quorum 2; domains 2; ownership 2;
    backup/restore 2; verification 2.

### WB-03 --- PDB policy for fleet maintenance

-   **Context and constraints:** API and queue consumers rotate nodes
    weekly while processing in-flight work.
-   **Plausible approaches:** A: per-service PDB, staged drain and
    headroom. B: node-pool rotation/blue-green capacity.
-   **Key trade-offs:** PDB only constrains voluntary evictions; strict
    budgets block maintenance and loose budgets risk SLO. Shutdown and
    scheduler feasibility matter.
-   **Answer outline:** Model healthy replicas, topology, shutdown
    latency, surge, queue checkpoint behavior, stop thresholds; rehearse
    drain.
-   **Scoring rubric:** 10 points: semantics 2; capacity 2; shutdown 2;
    staged maintenance 2; escalation 2.

### WB-04 --- Cluster upgrade strategy and compatibility gates

-   **Context and constraints:** Many clusters have mixed versions,
    CRDs, CNI/CSI and webhooks.
-   **Plausible approaches:** A: in-place upgrades in canary rings. B:
    node-pool rotation or blue/green cluster migration.
-   **Key trade-offs:** In-place needs less temporary capacity but
    limits rollback; rotation/blue-green adds isolation at cost of
    migration complexity.
-   **Answer outline:** Inventory compatibility, deprecations, workload
    health, add-ons, backups and rollback limits. Gate rings on SLO and
    stop criteria.
-   **Scoring rubric:** 10 points: inventory 2; trade-offs 2; gates 2;
    recovery limits 2; governance 2.

### WB-05 --- Autoscaling signal selection and avoiding HPA thrashing

-   **Context and constraints:** API is latency-bound, consumer
    queue-bound, cold model startup 90 seconds.
-   **Plausible approaches:** A: CPU HPA with stabilization. B: API
    concurrency/latency and queue age/depth signals with bounded rates.
-   **Key trade-offs:** CPU is simple but may lag; custom signals need
    reliable metrics. Fast scaling can overload downstream; slow scaling
    hurts latency.
-   **Answer outline:** Specify signal, metric delay, headroom, min/max,
    startup, VPA interaction and downstream protection; test
    burst/recovery.
-   **Scoring rubric:** 10 points: signal fit 2; lag/startup 2; feedback
    controls 2; downstream protection 2; test/cost 2.

### WB-06 --- Resource requests/limits and multi-team fairness

-   **Context and constraints:** API, GPU inference and ETL share bursty
    capacity.
-   **Plausible approaches:** A: shared pool with
    quota/LimitRange/PriorityClass. B: dedicated pools for specialized
    workloads.
-   **Key trade-offs:** Shared improves utilization but risks noisy
    neighbors; dedicated pools improve predictability but fragment
    capacity and cost more.
-   **Answer outline:** Use percentiles, allocatable, surge headroom and
    quota-denial trends; define exception/review cadence.
-   **Scoring rubric:** 10 points: semantics 2; measurement 2; fairness
    2; isolation 2; monitoring 2.

### WB-07 --- Least-privilege RBAC and Pod Security rollout

-   **Context and constraints:** New restricted policy may reject legacy
    workloads.
-   **Plausible approaches:** A: namespace-scoped RBAC and staged PSA
    audit/warn/enforce. B: GitOps identities and policy-as-code with
    expiring exceptions.
-   **Key trade-offs:** Immediate enforcement is consistent but risks
    outages; staged rollout needs deadlines to avoid permanent
    exceptions.
-   **Answer outline:** Map personas/verbs/resources, audit
    bindings/tokens, inventory securityContext, stage policy, monitor
    denials and test rollback.
-   **Scoring rubric:** 10 points: identity 2; least privilege 2; staged
    policy 2; exception governance 2; audit 2.

### WB-08 --- etcd backup/restore with RPO/RTO

-   **Context and constraints:** Self-managed control plane targets RPO
    15 min and RTO 60 min; application data is on PVs.
-   **Plausible approaches:** A: frequent etcd snapshots plus off-site
    copies and drills. B: managed control plane plus provider recovery
    commitments and separate application-data backup.
-   **Key trade-offs:** Snapshots do not automatically include PV bytes;
    restore tooling/version and stale state matter. Faster recovery
    costs storage and test effort.
-   **Answer outline:** Define cadence, off-node security, PV
    consistency, exact version, restore sequence, measured objectives
    and owners.
-   **Scoring rubric:** 10 points: scope 2; cadence 2; separate data 2;
    security 1; timed drill 3.

### WB-09 --- Troubleshooting automation and privacy-safe bundles

-   **Context and constraints:** On-call needs fast multi-tenant
    diagnostics without exposing credentials/customer data.
-   **Plausible approaches:** A: read-only allowlist with
    redaction/manual review. B: controlled diagnostic service with
    scoped identity, audit, retention and approval.
-   **Key trade-offs:** Automation speeds triage but can amplify
    exposure or mutate production; heuristic redaction is imperfect.
    Need API-unavailable path.
-   **Answer outline:** Define context checks, data minimization,
    permissions, destination, retention, audit and manual review. Test
    both paths.
-   **Scoring rubric:** 10 points: scope 2; privacy 3; access/audit 2;
    fallback 1; retention/test 2.

### WB-10 --- Resilient data/ML pipeline across API, queue, stateful dependency, ETL Job and CronJob

-   **Context and constraints:** Platform serves scoring, consumes
    events, uses a feature store, backfills and nightly reconciles.
-   **Plausible approaches:** A: one cluster with policy, pools and
    workload contracts. B: separate stateful/batch from
    latency-sensitive serving.
-   **Key trade-offs:** Shared reduces duplicated cost but couples noisy
    neighbors and maintenance; separation improves blast radius but adds
    network/data/governance cost.
-   **Answer outline:** Map SLOs, idempotency, probes, scaling, resource
    budgets, PDB/shutdown, RBAC/PSA, backup/restore and ownership.
-   **Scoring rubric:** 10 points: semantics 2; SLO/capacity 2; data
    correctness 2; security 2; operations/cost 2.

## Final answer key index and remediation map

Model answers appear immediately after each prompt; no separate answer
file is required. Use the question ID to log weak objectives and retry
with a different example.

### Question ID reconciliation

-   Generated scored IDs: **165**; unique IDs: **165**; duplicates:
    **0**.
-   Cross-unit IDs: **28**; whiteboard prompts: **10**.
-   Per-unit base mix: 3 SA, 3 MCQ, 2 OUT, 2 MAN, 1 INC, 1 DES; Units
    1--5 each add one EXT item.

## Sources, version notes, and claim register

### Official documentation entry points

-   Architecture: https://kubernetes.io/docs/concepts/architecture/
-   Deployments:
    https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
-   StatefulSets:
    https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/
-   Jobs/CronJobs:
    https://kubernetes.io/docs/concepts/workloads/controllers/job/
-   Resources:
    https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
-   ResourceQuota:
    https://kubernetes.io/docs/concepts/policy/resource-quotas/
-   LimitRange: https://kubernetes.io/docs/concepts/policy/limit-range/
-   Probes:
    https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/
-   PDB: https://kubernetes.io/docs/tasks/run-application/configure-pdb/
-   HPA:
    https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/
-   Scheduling:
    https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/
-   Taints/tolerations:
    https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/
-   Version skew: https://kubernetes.io/releases/version-skew-policy/
-   Deprecation guide:
    https://kubernetes.io/docs/reference/using-api/deprecation-guide/
-   RBAC: https://kubernetes.io/docs/reference/access-authn-authz/rbac/
-   Pod Security Standards:
    https://kubernetes.io/docs/concepts/security/pod-security-standards/
-   Pod Security Admission:
    https://kubernetes.io/docs/concepts/security/pod-security-admission/
-   etcd recovery: https://etcd.io/docs/v3.5/op-guide/recovery/
-   kind: https://kind.sigs.k8s.io/docs/user/quick-start/
-   Pod debugging:
    https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/
-   Service debugging:
    https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/
-   DNS debugging:
    https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/

**Verification boundary:** these are official documentation entry
points, not a claim that every page was live-opened during this pass. No
labs, manifests, cluster commands, etcd restore, or provider API were
executed. All sample output is illustrative.

### Claim register

  --------------------------------------------------------------------------------------------------------------------------------------------
  ID         Claim tested or used                     Source-derived   Authoritative     Version-sensitive?   Lesson/question   Verification
                                                      or inference     source                                 IDs               status
  ---------- ---------------------------------------- ---------------- ----------------- -------------------- ----------------- --------------
  C01        API server/etcd responsibilities         Source-derived   Architecture docs \[VERIFY\] for       U01-SA-01;        Lesson scope
                                                      or inference as                    version/provider     U10-SA-01         checked;
                                                      indicated by                       specifics                              external page
                                                      lesson                                                                    not
                                                                                                                                live-opened

  C02        Scheduler/kubelet/runtime roles          Source-derived   Architecture docs \[VERIFY\] for       U01-MCQ-01;       Lesson scope
                                                      or inference as                    version/provider     U11-SA-02         checked;
                                                      indicated by                       specifics                              external page
                                                      lesson                                                                    not
                                                                                                                                live-opened

  C03        Namespace is not complete isolation      Source-derived   Namespace/RBAC    \[VERIFY\] for       U02-SA-01;        Lesson scope
                                                      or inference as  docs              version/provider     U09-DES-01        checked;
                                                      indicated by                       specifics                              external page
                                                      lesson                                                                    not
                                                                                                                                live-opened

  C04        Requests affect scheduling; CPU/memory   Source-derived   Resource docs     \[VERIFY\] for       U02-SA-02;        Lesson scope
             differ                                   or inference as                    version/provider     XINT-16           checked;
                                                      indicated by                       specifics                              external page
                                                      lesson                                                                    not
                                                                                                                                live-opened

  C05        Quota caps aggregate namespace           Source-derived   ResourceQuota     \[VERIFY\] for       U02-OUT-01;       Lesson scope
             consumption                              or inference as  docs              version/provider     XINT-01           checked;
                                                      indicated by                       specifics                              external page
                                                      lesson                                                                    not
                                                                                                                                live-opened

  C06        LimitRange can default/constrain         Source-derived   LimitRange docs   \[VERIFY\] for       U02-OUT-02;       Lesson scope
             resources                                or inference as                    version/provider     U02-MAN-02        checked;
                                                      indicated by                       specifics                              external page
                                                      lesson                                                                    not
                                                                                                                                live-opened

  C07        Readiness/liveness/startup semantics     Source-derived   Probe docs        \[VERIFY\] for       U03-SA-01;        Lesson scope
                                                      or inference as                    version/provider     U03-MCQ-02        checked;
                                                      indicated by                       specifics                              external page
                                                      lesson                                                                    not
                                                                                                                                live-opened

  C08        Deep liveness can cause restart storms   Source-derived   Probe docs        \[VERIFY\] for       U03-SA-02;        Lesson scope
                                                      or inference as                    version/provider     XINT-18           checked;
                                                      indicated by                       specifics                              external page
                                                      lesson                                                                    not
                                                                                                                                live-opened

  C09        Rollback does not reverse external side  Source-derived   Deployment docs   \[VERIFY\] for       U04-SA-02;        Lesson scope
             effects                                  or inference as                    version/provider     XINT-27           checked;
                                                      indicated by                       specifics                              external page
                                                      lesson                                                                    not
                                                                                                                                live-opened

  C10        Jobs do not guarantee exactly-once side  Source-derived   Job docs          \[VERIFY\] for       U04-SA-03;        Lesson scope
             effects                                  or inference as                    version/provider     XINT-03           checked;
                                                      indicated by                       specifics                              external page
                                                      lesson                                                                    not
                                                                                                                                live-opened

  C11        PDB constrains voluntary eviction        Source-derived   PDB docs          \[VERIFY\] for       U05-SA-01;        Lesson scope
                                                      or inference as                    version/provider     XINT-21           checked;
                                                      indicated by                       specifics                              external page
                                                      lesson                                                                    not
                                                                                                                                live-opened

  C12        Graceful shutdown requires application   Source-derived   Pod lifecycle     \[VERIFY\] for       U05-SA-02;        Lesson scope
             cooperation                              or inference as  docs              version/provider     XINT-27           checked;
                                                      indicated by                       specifics                              external page
                                                      lesson                                                                    not
                                                                                                                                live-opened

  C13        HPA scales replicas; node scaler adds    Source-derived   HPA/provider docs \[VERIFY\] for       U06-SA-01;        Lesson scope
             capacity                                 or inference as                    version/provider     XINT-01           checked;
                                                      indicated by                       specifics                              external page
                                                      lesson                                                                    not
                                                                                                                                live-opened

  C14        Resource HPA needs usable                Source-derived   HPA docs          \[VERIFY\] for       U06-MCQ-02;       Lesson scope
             metrics/requests                         or inference as                    version/provider     U06-OUT-01        checked;
                                                      indicated by                       specifics                              external page
                                                      lesson                                                                    not
                                                                                                                                live-opened

  C15        Toleration does not guarantee placement  Source-derived   Scheduling docs   \[VERIFY\] for       U07-MCQ-01;       Lesson scope
                                                      or inference as                    version/provider     U07-MAN-01        checked;
                                                      indicated by                       specifics                              external page
                                                      lesson                                                                    not
                                                                                                                                live-opened

  C16        Affinity/topology can make nodes         Source-derived   Scheduling docs   \[VERIFY\] for       U07-OUT-01;       Lesson scope
             ineligible                               or inference as                    version/provider     XINT-12           checked;
                                                      indicated by                       specifics                              external page
                                                      lesson                                                                    not
                                                                                                                                live-opened

  C17        Compatibility includes                   Source-derived   Version skew docs \[VERIFY\] for       U08-SA-01;        Lesson scope
             add-ons/CRDs/webhooks                    or inference as                    version/provider     XINT-20           checked;
                                                      indicated by                       specifics                              external page
                                                      lesson                                                                    not
                                                                                                                                live-opened

  C18        Static scanner may miss live API use     Source-derived   Deprecation guide \[VERIFY\] for       U08-OUT-01        Lesson scope
                                                      or inference as                    version/provider                       checked;
                                                      indicated by                       specifics                              external page
                                                      lesson                                                                    not
                                                                                                                                live-opened

  C19        Authentication/authorization/admission   Source-derived   Auth docs         \[VERIFY\] for       U09-SA-01;        Lesson scope
             differ                                   or inference as                    version/provider     XINT-04           checked;
                                                      indicated by                       specifics                              external page
                                                      lesson                                                                    not
                                                                                                                                live-opened

  C20        RBAC least privilege and PSA policy      Source-derived   RBAC/PSA docs     \[VERIFY\] for       U09-MAN-02;       Lesson scope
             rollout                                  or inference as                    version/provider     XINT-13           checked;
                                                      indicated by                       specifics                              external page
                                                      lesson                                                                    not
                                                                                                                                live-opened

  C21        etcd quorum requires majority            Source-derived   etcd docs         \[VERIFY\] for       U10-SA-01;        Lesson scope
                                                      or inference as                    version/provider     U10-MCQ-01        checked;
                                                      indicated by                       specifics                              external page
                                                      lesson                                                                    not
                                                                                                                                live-opened

  C22        etcd snapshot excludes arbitrary PV      Source-derived   etcd/storage docs \[VERIFY\] for       U10-SA-02;        Lesson scope
             bytes                                    or inference as                    version/provider     XINT-07           checked;
                                                      indicated by                       specifics                              external page
                                                      lesson                                                                    not
                                                                                                                                live-opened

  C23        Pod phase differs from container reason  Source-derived   Pod lifecycle     \[VERIFY\] for       U11-SA-02;        Lesson scope
                                                      or inference as  docs              version/provider     U11-OUT-02        checked;
                                                      indicated by                       specifics                              external page
                                                      lesson                                                                    not
                                                                                                                                live-opened

  C24        Service endpoints depend on              Source-derived   Service debug     \[VERIFY\] for       U11-MCQ-03;       Lesson scope
             selectors/readiness                      or inference as  docs              version/provider     U11-OUT-02        checked;
                                                      indicated by                       specifics                              external page
                                                      lesson                                                                    not
                                                                                                                                live-opened

  C25        Logs/events may contain sensitive data   Source-derived   Security          \[VERIFY\] for       U11-SA-03;        Lesson scope
                                                      or inference as  principle/debug   version/provider     XINT-22           checked;
                                                      indicated by     docs              specifics                              external page
                                                      lesson                                                                    not
                                                                                                                                live-opened

  C26        kind is not production equivalence       Source-derived   kind docs         \[VERIFY\] for       U01-DES-01;       Lesson scope
                                                      or inference as                    version/provider     XINT-19           checked;
                                                      indicated by                       specifics                              external page
                                                      lesson                                                                    not
                                                                                                                                live-opened
  --------------------------------------------------------------------------------------------------------------------------------------------

## Ten-pass authenticity and completeness audit

  ----------------------------------------------------------------------------------------
  Check                  Status (PASS /    Evidence          Fix or limitation
                         NEEDS ATTENTION /                   
                         NOT VERIFIED)                       
  ---------------------- ----------------- ----------------- -----------------------------
  1\. Repository         NEEDS ATTENTION   Roadmap variant   Canonical
  fidelity                                 lists expected    Roadmap_ptree.md/repository
                                           M03 folder and    checkout unavailable;
                                           unit order.       standalone target path used;
                                                             diff cannot be inspected.

  2\. Syllabus fidelity  PASS              Uploaded prompt   Detailed source notes map to
                                           scope and all 11  lesson filenames and
                                           lesson files      concepts.
                                           inspected for     
                                           topic/heading     
                                           scope.            

  3\. Count and          PASS              165 unique IDs,   Whiteboards are additional to
  distribution                             12+ per unit, 28  scored total.
                                           cross-unit, 10    
                                           whiteboards.      

  4\. Question schema    PASS              Every scored      Human review of free-text
                                           question emitted  quality remains advisable.
                                           with required     
                                           metadata/answer   
                                           fields.           

  5\. Per-unit type mix  PASS              3 SA, 3 MCQ, 2    Units 1--5 have one
                                           OUT, 2 MAN, 1     additional item.
                                           INC, 1 DES per    
                                           unit.             

  6\. Technical          NEEDS ATTENTION   Grounded in       No live docs or cluster
  authenticity                             lessons and       execution; version-sensitive
                                           official doc      details marked \[VERIFY\].
                                           entry points      
                                           listed.           

  7\. Answer key quality PASS              Every question    Expert review recommended
                                           has model answer, before formal grading.
                                           misconceptions    
                                           and rubric; MCQs  
                                           have A--D and     
                                           distractor        
                                           analysis.         

  8\. Cross-unit and     PASS              28 cross-unit     L4 depth is authored judgment
  level coverage                           prompts list      and merits human review.
                                           integrated units; 
                                           L1--L4 included.  

  9\. Sources and claim  NEEDS ATTENTION   26 claim register URLs not all opened live;
  hygiene                                  rows and official inclusion is not live
                                           doc URLs          verification.
                                           included.         

  10\.                   NEEDS ATTENTION   ID/count audit    No repository diff; cannot
  Editorial/repository                     generated; file   certify repository mutation
  safety                                   written in new    boundaries.
                                           standalone target 
                                           path.             
  ----------------------------------------------------------------------------------------

## Sign-off and known limitations

-   **Sources actually read:** uploaded practice prompt;
    `PROMPT-Production-Kubernetes-Operations(3).md`; available
    roadmap-tree variant; all 11 lesson files were present and their
    headings/topic scope inspected. The exact canonical
    `Roadmap_ptree.md`, syllabus output, M03 README and project README
    were not separately available for full tree verification.
-   **Questions checked against lessons?** Yes, at topic/heading and
    targeted section level; no claim that every paragraph or lab was
    executed.
-   **Repository diff inspected?** No repository checkout was available.
    The file is in a standalone mirrored target folder; no claim is made
    about an actual repository diff.
-   **Unresolved \[VERIFY\]:** Kubernetes/kubectl output/flags and field
    defaults; etcd/etcdutl restore compatibility; PSA label versions;
    HPA/VPA and optional metrics; CNI/CSI/ingress/webhook/provider
    behavior; kind image capabilities; destructive recovery commands.
    Verify exact versions before use.
-   **Execution:** no cluster/lab/manifest
    apply/snapshot/restore/provider API was run. All outputs/incidents
    are illustrative. Manifest excerpts are defective training fixtures
    and must not be applied as-is.
-   **Privacy:** logs/events/annotations may contain sensitive data even
    when Secret objects are excluded; manual review and retention
    controls are required.

**Sign-off:** Ready for guided practice and instructor review; not
verified as a production runbook.
