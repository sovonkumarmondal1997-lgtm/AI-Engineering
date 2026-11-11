# M05 Practice Questions — Kubernetes Storage and Stateful Data Workloads

**Stage:** Stage 2E — Production DevOps & Platform Engineering  
**Module:** M05 — Kubernetes Storage and Stateful Data Workloads  
**Unit:** 9 — Practice questions  
**Target file:** `practice-questions.md`

> **Source and verification status:** The uploaded prompt `Pasted markdown(20261027-202150).md` supplies the complete assessment specification and explicit Unit 1–8 coverage list. The library copy `PROMPT-Kubernetes-Storage-and-Stateful-Data-Workloads.md` was found and its opening curriculum material was retrieved through file search. The exact `Roadmap_ptree.md` was not located in the available search results; this assessment therefore uses the exact M05 tree reproduced in the uploaded prompt rather than claiming direct inspection of the tree. Unit lesson files are available in the library by name, but their full contents were not independently cross-checked for this bank. Lesson-level coverage is therefore **not independently confirmed**. No commands, manifests, labs, or question outputs in this file were executed; all excerpts are illustrative.

**Safety rule:** For any storage incident, establish owner, references, backend identity, and data-safety/recovery status before destructive action. Unknown means stop, preserve evidence, and escalate—not delete.

## 9.0 How to use this question bank

- Attempt each question before reading its model answer. Answers are placed directly under prompts for standalone review; cover the answer block while self-testing.
- Levels progress from **L1 Beginner** through **L4 Expert**. Level is the primary expected reasoning depth, not a claim that all learners progress at the same pace.
- Each question has a unique ID, objective, time estimate, question type, model answer, common misconceptions, rubric, source note, and version note.
- For output interpretation, snippets are labelled **illustrative / expected output (not executed here)**. They demonstrate the evidence pattern to reason about; they are not recorded observations.
- For manifest review, distinguish YAML/API schema validity from driver capability, scheduling behavior, and application correctness. Several snippets intentionally contain defects and are not intended to apply.
- Treat `[VERIFY]` as an explicit check against the exact Kubernetes release, CSI driver/sidecars, operator, backend, filesystem, or policy engine in use.
- Recommended study loop: answer → score → identify the missed concept → revisit the named unit → repeat with a different scenario.
- Practical questions must fit a zero-budget local `kind`/WSL2 or native Linux setup (about 4 CPU cores, 8 GB RAM, 30 GB free disk, at most three kind workers). Do not run memory-heavy stacks simultaneously. Use fake credentials only.
- `kind` topology labels simulate scheduler constraints; they do not create real independent zones or production durability. A local-path-style provisioner must not be assumed to support CSI snapshots or expansion. CSI hostpath is a teaching/reference driver, not a production storage system; verify actual capabilities and install instructions.

## 9.1 Coverage map and assessment blueprint

| Unit | Main assessment themes | Required type minimum | Question IDs |
|---|---|---|---|

| 1 — Volumes, PersistentVolumes, PersistentVolumeClaims | Core concepts, MCQ, evidence interpretation, manifest review, incident response, design | 3 short answers, 3 MCQs, 2 outputs, 2 manifest reviews, 1 incident, 1 design | M05-U01-Q001–Q015 (12 questions; ID gaps are not used) |
| 2 — StorageClasses, Dynamic Provisioning, CSI Drivers | Core concepts, MCQ, evidence interpretation, manifest review, incident response, design | 3 short answers, 3 MCQs, 2 outputs, 2 manifest reviews, 1 incident, 1 design | M05-U02-Q001–Q015 (12 questions; ID gaps are not used) |
| 3 — Volume Snapshots, Cloning, Expansion | Core concepts, MCQ, evidence interpretation, manifest review, incident response, design | 3 short answers, 3 MCQs, 2 outputs, 2 manifest reviews, 1 incident, 1 design | M05-U03-Q001–Q015 (12 questions; ID gaps are not used) |
| 4 — StatefulSet Storage Patterns and Stable Identity | Core concepts, MCQ, evidence interpretation, manifest review, incident response, design | 3 short answers, 3 MCQs, 2 outputs, 2 manifest reviews, 1 incident, 1 design | M05-U04-Q001–Q015 (12 questions; ID gaps are not used) |
| 5 — Running Databases and Brokers with Operators | Core concepts, MCQ, evidence interpretation, manifest review, incident response, design | 3 short answers, 3 MCQs, 2 outputs, 2 manifest reviews, 1 incident, 1 design | M05-U05-Q001–Q015 (12 questions; ID gaps are not used) |
| 6 — Storage Performance: IOPS, Throughput, Latency | Core concepts, MCQ, evidence interpretation, manifest review, incident response, design | 3 short answers, 3 MCQs, 2 outputs, 2 manifest reviews, 1 incident, 1 design | M05-U06-Q001–Q015 (12 questions; ID gaps are not used) |
| 7 — Data Locality, Zonal Failure, Volume Affinity | Core concepts, MCQ, evidence interpretation, manifest review, incident response, design | 3 short answers, 3 MCQs, 2 outputs, 2 manifest reviews, 1 incident, 1 design | M05-U07-Q001–Q015 (12 questions; ID gaps are not used) |
| 8 — Storage Troubleshooting and Orphaned Volumes | Core concepts, MCQ, evidence interpretation, manifest review, incident response, design | 3 short answers, 3 MCQs, 2 outputs, 2 manifest reviews, 1 incident, 1 design | M05-U08-Q001–Q015 (12 questions; ID gaps are not used) |

**Cross-unit bank:** 38 distinct scenarios (M05-XINT-001 through M05-XINT-034) integrate at least two units each, with multi-unit integration in the strongest scenarios. The 38 cross-unit questions are necessary because the per-unit minimum yields 96 questions; 96 + 38 = 134 total.

**Type taxonomy:** conceptual short answer; multiple choice; output interpretation; manifest review; incident/troubleshooting; design; cross-unit integration scenario. The count ledger treats cross-unit scenarios as a separate type, not as a second count in a unit-specific category.

## 9.2 Scoring policy and safety-critical errors

Suggested scoring is defined per question. For a quick percentage, sum earned points and divide by the sum of maximum points. Use the result diagnostically rather than as a production authorization.

Safety-critical errors materially reduce the score:
- Deleting a PVC/PV/backend volume before ownership, references, recovery and approval are established.
- Removing finalizers as a first-line action.
- Force-detaching without checking old-node fencing, backend state, driver procedure and application consistency.
- Running `fsck` on a mounted filesystem.
- Treating snapshot readiness as a verified independent backup.
- Treating `kind` fake zones as real zonal resilience.
- Declaring WFFC Pending broken without checking for a consumer and scheduling events.
- Assuming CSI capabilities are uniform.
- Treating `kubectl top` as disk I/O telemetry.
- Treating Pod restart, StatefulSet identity, PDB or a single replica as a backup.

A correct “stop, preserve evidence, and escalate” response earns credit when the evidence is insufficient or the proposed mutation risks data loss.


## 9.3 Unit 1 — Volumes, PersistentVolumes, PersistentVolumeClaims

### Conceptual short answer

### M05-U01-Q001 — ephemeral and persistent storage

- **Unit/category:** Unit 1 / Conceptual short answer
- **Level:** L1 Beginner
- **Objective tested:** ephemeral and persistent storage
- **Estimated time:** 4–12 minutes
- **Question type:** Conceptual short answer
- **Question prompt:** Explain the lifecycle difference between container writable layers, Pod-scoped volumes, and persistent storage.
- **Model answer:** Container writable-layer changes are tied to the container instance; Pod volumes can outlive a container restart but are bounded by the Pod/volume type; a PV-backed claim can persist beyond Pod replacement. Verify the specific volume type and reclaim behavior before relying on persistence.
- **Common wrong answers/misconceptions:**
- Treating one Kubernetes object status as proof of end-to-end data health — object state covers only part of the lifecycle.
- Skipping the owner/data-safety check — destructive changes require confirmed ownership, references, and recoverability.
- Assuming identical behavior across all drivers and versions — verify implementation-specific support.
- **Scoring rubric:** 3 points: correct distinction (1), evidence/reasoning (1), safety/version caveat (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 1; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] where driver, filesystem, operator, or Kubernetes release affects the behavior.

### M05-U01-Q002 — PV/PVC binding

- **Unit/category:** Unit 1 / Conceptual short answer
- **Level:** L2 Intermediate
- **Objective tested:** PV/PVC binding
- **Estimated time:** 4–12 minutes
- **Question type:** Conceptual short answer
- **Question prompt:** A PVC requests 8Gi while a candidate PV advertises 4Gi. Explain whether the claim can bind and what else must match.
- **Model answer:** The 4Gi PV does not satisfy an 8Gi request. Binding also depends on access modes, volumeMode, StorageClass, selectors/pre-binding, and availability. Do not resize or replace a data volume without checking its current owner and contents.
- **Common wrong answers/misconceptions:**
- Treating one Kubernetes object status as proof of end-to-end data health — object state covers only part of the lifecycle.
- Skipping the owner/data-safety check — destructive changes require confirmed ownership, references, and recoverability.
- Assuming identical behavior across all drivers and versions — verify implementation-specific support.
- **Scoring rubric:** 3 points: correct distinction (1), evidence/reasoning (1), safety/version caveat (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 1; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] where driver, filesystem, operator, or Kubernetes release affects the behavior.

### M05-U01-Q003 — access modes

- **Unit/category:** Unit 1 / Conceptual short answer
- **Level:** L3 Advanced
- **Objective tested:** access modes
- **Estimated time:** 4–12 minutes
- **Question type:** Conceptual short answer
- **Question prompt:** Explain why ReadWriteOnce does not simply mean “one Pod only,” and why access mode is not a substitute for backend capability checks.
- **Model answer:** RWO describes read-write mounting by a single node under Kubernetes access-mode semantics; multiple Pods on that node may use it. Actual attachment and multi-node behavior depend on the volume plugin/backend. ReadWriteOncePod has stricter single-Pod semantics where supported; verify cluster and driver support.
- **Common wrong answers/misconceptions:**
- Treating one Kubernetes object status as proof of end-to-end data health — object state covers only part of the lifecycle.
- Skipping the owner/data-safety check — destructive changes require confirmed ownership, references, and recoverability.
- Assuming identical behavior across all drivers and versions — verify implementation-specific support.
- **Scoring rubric:** 3 points: correct distinction (1), evidence/reasoning (1), safety/version caveat (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 1; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] where driver, filesystem, operator, or Kubernetes release affects the behavior.

### Multiple choice

### M05-U01-Q004 — Apply a core concept and reject plausible unsafe interpretations.

- **Unit/category:** Unit 1 / Multiple choice
- **Level:** L1 Beginner
- **Objective tested:** Apply a core concept and reject plausible unsafe interpretations.
- **Estimated time:** 4–12 minutes
- **Question type:** Multiple choice
- **Question prompt:** A PVC requests 10Gi. Which PV is a viable candidate on capacity alone?
- **Options:**
  - **A.** A 5Gi PV
  - **B.** A 10Gi PV
  - **C.** A 2Gi PV
  - **D.** A PV with unknown capacity
- **Model answer:** **Correct option: B.** The 10Gi PV meets the requested capacity; other binding constraints still need checking.

- **A:** The 5Gi PV is undersized.
- **B (correct):** The 10Gi PV meets the requested capacity; other binding constraints still need checking.
- **C:** The 2Gi PV is undersized.
- **D:** Unknown capacity cannot establish a match.

- **Common wrong answers/misconceptions:**
- Choosing an option based on a status word without checking the described lifecycle.
- Assuming backend or application guarantees that the prompt does not establish.
- Taking a destructive action before confirming ownership and data safety.
- **Scoring rubric:** 1 point for the correct option; up to 2 additional points for explaining why it is correct and why each distractor fails.
- **Source/coverage note:** Parent M05 syllabus, Unit 1; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact driver/version behavior where noted.

### M05-U01-Q005 — Apply a core concept and reject plausible unsafe interpretations.

- **Unit/category:** Unit 1 / Multiple choice
- **Level:** L2 Intermediate
- **Objective tested:** Apply a core concept and reject plausible unsafe interpretations.
- **Estimated time:** 4–12 minutes
- **Question type:** Multiple choice
- **Question prompt:** Which statement about Retain is safest?
- **Options:**
  - **A.** It guarantees automatic data deletion
  - **B.** It preserves the resource for deliberate handling after claim release
  - **C.** It means the PV is immediately reusable by any claim
  - **D.** It guarantees an independent backup
- **Model answer:** **Correct option: B.** Retain commonly leaves the PV/backend resource for deliberate recovery or cleanup.

- **A:** Retain is not a deletion guarantee.
- **B (correct):** Retain commonly leaves the PV/backend resource for deliberate recovery or cleanup.
- **C:** A Released PV may retain claimRef and require a controlled recovery/rebinding procedure.
- **D:** Retention is not backup independence or restore validation.

- **Common wrong answers/misconceptions:**
- Choosing an option based on a status word without checking the described lifecycle.
- Assuming backend or application guarantees that the prompt does not establish.
- Taking a destructive action before confirming ownership and data safety.
- **Scoring rubric:** 1 point for the correct option; up to 2 additional points for explaining why it is correct and why each distractor fails.
- **Source/coverage note:** Parent M05 syllabus, Unit 1; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact driver/version behavior where noted.

### M05-U01-Q006 — Apply a core concept and reject plausible unsafe interpretations.

- **Unit/category:** Unit 1 / Multiple choice
- **Level:** L2 Intermediate
- **Objective tested:** Apply a core concept and reject plausible unsafe interpretations.
- **Estimated time:** 4–12 minutes
- **Question type:** Multiple choice
- **Question prompt:** What is the safest first response to a PVC stuck Terminating with pvc-protection?
- **Options:**
  - **A.** Patch away the finalizer immediately
  - **B.** Delete the node
  - **C.** Find Pods referencing the claim and inspect controller state
  - **D.** Format the volume
- **Model answer:** **Correct option: C.** Protection may be waiting for a Pod reference to clear; gather evidence first.

- **A:** Bypassing protection can lose tracking or delete a live claim.
- **B:** Node deletion does not diagnose claim references and may worsen impact.
- **C (correct):** Protection may be waiting for a Pod reference to clear; gather evidence first.
- **D:** Formatting is destructive and unrelated to first-line diagnosis.

- **Common wrong answers/misconceptions:**
- Choosing an option based on a status word without checking the described lifecycle.
- Assuming backend or application guarantees that the prompt does not establish.
- Taking a destructive action before confirming ownership and data safety.
- **Scoring rubric:** 1 point for the correct option; up to 2 additional points for explaining why it is correct and why each distractor fails.
- **Source/coverage note:** Parent M05 syllabus, Unit 1; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact driver/version behavior where noted.

### Output interpretation

### M05-U01-Q010 — Interpret object/event/telemetry evidence and identify safe next checks.

- **Unit/category:** Unit 1 / Output interpretation
- **Level:** L2 Intermediate
- **Objective tested:** Interpret object/event/telemetry evidence and identify safe next checks.
- **Estimated time:** 4–12 minutes
- **Question type:** Output interpretation
- **Question prompt:** PVC is Bound; Pod event excerpt says `FailedMount`; PV is still Bound.

What does the evidence support, what does it not prove, which read-only checks come next, and what is the safest next action?

Illustrative / expected output (not executed here):
```text
Type     Reason      Object
Warning  FailedMount Pod/app-0
Message: MountVolume.SetUp failed for volume data: permission denied
```
- **Model answer:** The claim/PV binding succeeded, but mount setup did not. Check Pod securityContext, file ownership/mode, mount options, node-plugin/kubelet logs, and driver semantics. This excerpt does not prove data corruption or that changing permissions recursively is safe.
- **Common wrong answers/misconceptions:**
- Treating the excerpt as proof of a single root cause without corroborating evidence.
- Deleting or patching storage objects before confirming ownership, references and data safety.
- Assuming driver/backend behavior is universal.
- **Scoring rubric:** 5 points: accurate interpretation (2), limitations/next checks (1), safe action (1), prevention or verification (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 1; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact event text/status semantics against the installed Kubernetes release and driver.

### M05-U01-Q011 — Interpret object/event/telemetry evidence and identify safe next checks.

- **Unit/category:** Unit 1 / Output interpretation
- **Level:** L3 Advanced
- **Objective tested:** Interpret object/event/telemetry evidence and identify safe next checks.
- **Estimated time:** 4–12 minutes
- **Question type:** Output interpretation
- **Question prompt:** A PV has phase Released and reclaimPolicy Retain.

What does the evidence support, what does it not prove, which read-only checks come next, and what is the safest next action?

Illustrative / expected output (not executed here):
```yaml
status:
  phase: Released
spec:
  persistentVolumeReclaimPolicy: Retain
  claimRef:
    namespace: old-app
    name: data-db-0
```
- **Model answer:** The prior claim was released and retention may preserve data. Inspect claim UID/owner, backend ID, snapshots/restore jobs and recovery records. Do not clear claimRef or delete the PV merely to make it reusable.
- **Common wrong answers/misconceptions:**
- Treating the excerpt as proof of a single root cause without corroborating evidence.
- Deleting or patching storage objects before confirming ownership, references and data safety.
- Assuming driver/backend behavior is universal.
- **Scoring rubric:** 5 points: accurate interpretation (2), limitations/next checks (1), safe action (1), prevention or verification (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 1; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact event text/status semantics against the installed Kubernetes release and driver.

### Manifest review

### M05-U01-Q012 — Review storage manifests for lifecycle, capability, security, or data-loss defects.

- **Unit/category:** Unit 1 / Manifest review
- **Level:** L3 Advanced
- **Objective tested:** Review storage manifests for lifecycle, capability, security, or data-loss defects.
- **Estimated time:** 4–12 minutes
- **Question type:** Manifest review
- **Question prompt:** Review the following design: A claim requests 20Gi against a 5Gi static PV; it uses `storageClassName: fast` while the PV has `storageClassName: `; workload expects RWX but PV is RWO.

Illustrative snippet (not validated against a live cluster):
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata: {name: data}
spec:
  accessModes: [ReadWriteMany]
  storageClassName: fast
  resources:
    requests: {storage: 20Gi}
---
apiVersion: v1
kind: PersistentVolume
metadata: {name: pv-small}
spec:
  capacity: {storage: 5Gi}
  accessModes: [ReadWriteOnce]
  storageClassName: ""
  persistentVolumeReclaimPolicy: Delete
```
Find at least three substantive defects or dangerous omissions, provide a corrected design/patch strategy, and distinguish schema validation from runtime capability checks.
- **Model answer:** Defects:
1. PV capacity is insufficient for the 20Gi request.
2. StorageClass mismatch prevents the intended binding (explicit empty class differs from `fast`).
3. RWO does not satisfy the requested RWX capability; backend support must be checked.

Safe correction: Provision/choose a compatible PV/class with sufficient capacity and supported access semantics, or redesign the workload. Validate binding and test a disposable mount before migration; do not delete an existing data volume to force a match.
- **Common wrong answers/misconceptions:**
- Fixing only YAML syntax while leaving lifecycle/data-safety defects.
- Assuming API acceptance proves driver/backend capability.
- Deleting existing storage before proving migration/restore and owner approval.
- **Scoring rubric:** 8 points: 1 per substantive defect up to 3; 2 for safe correction; 1 for data-loss/ownership analysis; 1 for schema-vs-runtime distinction; 1 for validation/verification plan.
- **Source/coverage note:** Parent M05 syllabus, Unit 1; snippets are assessment examples, not executed manifests.
- **Version note:** [VERIFY] validate fields, API versions, operator CRDs and driver capabilities against the installed versions.
- **Defects expected in a complete review:**
  1. PV capacity is insufficient for the 20Gi request.
  2. StorageClass mismatch prevents the intended binding (explicit empty class differs from `fast`).
  3. RWO does not satisfy the requested RWX capability; backend support must be checked.
- **Corrected design/patch strategy:** Provision/choose a compatible PV/class with sufficient capacity and supported access semantics, or redesign the workload. Validate binding and test a disposable mount before migration; do not delete an existing data volume to force a match.

### M05-U01-Q013 — Review storage manifests for lifecycle, capability, security, or data-loss defects.

- **Unit/category:** Unit 1 / Manifest review
- **Level:** L3 Advanced
- **Objective tested:** Review storage manifests for lifecycle, capability, security, or data-loss defects.
- **Estimated time:** 4–12 minutes
- **Question type:** Manifest review
- **Question prompt:** Review the following design: A Pod mounts `/data` using `subPath: customer-a`; the source path is assumed to exist; container runs as UID 10001 but no permissions/security context are reviewed; `emptyDir` is used for database data.

Illustrative snippet (not validated against a live cluster):
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata: {name: data}
spec:
  accessModes: [ReadWriteMany]
  storageClassName: fast
  resources:
    requests: {storage: 20Gi}
---
apiVersion: v1
kind: PersistentVolume
metadata: {name: pv-small}
spec:
  capacity: {storage: 5Gi}
  accessModes: [ReadWriteOnce]
  storageClassName: ""
  persistentVolumeReclaimPolicy: Delete
```
Find at least three substantive defects or dangerous omissions, provide a corrected design/patch strategy, and distinguish schema validation from runtime capability checks.
- **Model answer:** Defects:
1. The subPath source path/semantics must be checked; missing or unsafe path assumptions can cause mount problems.
2. Non-root access is not established; review ownership, mode, fsGroup behavior and driver limitations.
3. emptyDir is Pod-lifetime storage and is inappropriate as the only persistence layer for database data.

Safe correction: Use a suitable persistent claim, verify subPath behavior and directory ownership, and test non-root access. Keep backup/recovery evidence before migrating any existing database data.
- **Common wrong answers/misconceptions:**
- Fixing only YAML syntax while leaving lifecycle/data-safety defects.
- Assuming API acceptance proves driver/backend capability.
- Deleting existing storage before proving migration/restore and owner approval.
- **Scoring rubric:** 8 points: 1 per substantive defect up to 3; 2 for safe correction; 1 for data-loss/ownership analysis; 1 for schema-vs-runtime distinction; 1 for validation/verification plan.
- **Source/coverage note:** Parent M05 syllabus, Unit 1; snippets are assessment examples, not executed manifests.
- **Version note:** [VERIFY] validate fields, API versions, operator CRDs and driver capabilities against the installed versions.
- **Defects expected in a complete review:**
  1. The subPath source path/semantics must be checked; missing or unsafe path assumptions can cause mount problems.
  2. Non-root access is not established; review ownership, mode, fsGroup behavior and driver limitations.
  3. emptyDir is Pod-lifetime storage and is inappropriate as the only persistence layer for database data.
- **Corrected design/patch strategy:** Use a suitable persistent claim, verify subPath behavior and directory ownership, and test non-root access. Keep backup/recovery evidence before migrating any existing database data.

### Incident/troubleshooting scenario

### M05-U01-Q014 — Use evidence-led troubleshooting and data-safety gates for a realistic storage incident.

- **Unit/category:** Unit 1 / Incident/troubleshooting scenario
- **Level:** L3 Advanced
- **Objective tested:** Use evidence-led troubleshooting and data-safety gates for a realistic storage incident.
- **Estimated time:** 4–12 minutes
- **Question type:** Incident/troubleshooting scenario
- **Question prompt:** A database Pod is replaced after a node drain. Its PVC is Bound, but writes fail. Events show mount permission denied after a non-root image change.

Give a ranked hypothesis, the first read-only checks, ownership/data-safety decision, safe mitigation/recovery, post-fix verification, prevention, and conditions that require stop-work/escalation.
- **Model answer:** Sequence: preserve event/log evidence; verify workload and data owner; confirm backup/recovery status; inspect UID/GID/mode, runAsUser/fsGroup, subPath and driver semantics; check node/plugin logs; make the smallest reviewed permission/security-context correction; verify application reads/writes and data integrity. Do not recursively chown or delete the PVC as a first response. Prevention: test non-root images against the actual storage driver.
- **Common wrong answers/misconceptions:**
- Jumping to deletion/finalizer removal/force-detach before evidence and data-safety checks.
- Treating one status or event as a complete root-cause proof.
- Skipping application-level verification after Kubernetes status recovers.
- **Scoring rubric:** 8 points: impact/evidence (2), ranked hypotheses (1), data-safety gate (1), safe recovery (2), verification (1), prevention/escalation (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 1; scenario synthesized from the explicit unit objectives.
- **Version note:** [VERIFY] driver/operator/filesystem specifics and runbook steps before production action.

### Design question

### M05-U01-Q015 — Make a defensible design with explicit constraints, trade-offs, failure modes and validati

- **Unit/category:** Unit 1 / Design question
- **Level:** L4 Expert
- **Objective tested:** Make a defensible design with explicit constraints, trade-offs, failure modes and validation.
- **Estimated time:** 4–12 minutes
- **Question type:** Design question
- **Question prompt:** Design storage for a disposable cache, a developer workspace, and a production database. Explain volume types, reclaim policies, access semantics, security context, quota and backup boundary.

State assumptions, compare at least two options, identify failure modes, define security/data-safety controls, and specify validation evidence.
- **Model answer:** Separate ephemeral scratch from persistent claims; use class/reclaim policy according to data class; validate access modes and volumeMode; apply least-privilege non-root permissions; budget bytes/inodes and quota; keep independent tested backups for production data. State which items are lab-only and verify backend support.
- **Common wrong answers/misconceptions:**
- Optimizing only for availability or cost while ignoring data integrity/recovery.
- Treating Kubernetes object readiness as proof of application correctness.
- Claiming driver or topology capabilities without verifying the deployed implementation.
- **Scoring rubric:** 8 points: constraints/options (2), lifecycle/data safety (2), failure modes/recovery (2), validation and security/cost trade-offs (2). Safety-critical unsafe deletion/force-detach/fsck-on-mounted-volume caps score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, Unit 1; design is aligned to stated unit outcomes.
- **Version note:** [VERIFY] exact implementation/API/backend support before implementation.

## 9.4 Unit 2 — StorageClasses, Dynamic Provisioning, CSI Drivers

### Conceptual short answer

### M05-U02-Q001 — static vs dynamic provisioning

- **Unit/category:** Unit 2 / Conceptual short answer
- **Level:** L1 Beginner
- **Objective tested:** static vs dynamic provisioning
- **Estimated time:** 4–12 minutes
- **Question type:** Conceptual short answer
- **Question prompt:** Compare static and dynamic provisioning, including the role of the StorageClass and provisioner.
- **Model answer:** Static provisioning uses an administrator-created PV; dynamic provisioning asks a provisioner/driver to create storage for a claim using StorageClass policy. A class alone does not guarantee a healthy driver or backend capacity.
- **Common wrong answers/misconceptions:**
- Treating one Kubernetes object status as proof of end-to-end data health — object state covers only part of the lifecycle.
- Skipping the owner/data-safety check — destructive changes require confirmed ownership, references, and recoverability.
- Assuming identical behavior across all drivers and versions — verify implementation-specific support.
- **Scoring rubric:** 3 points: correct distinction (1), evidence/reasoning (1), safety/version caveat (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 2; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] where driver, filesystem, operator, or Kubernetes release affects the behavior.

### M05-U02-Q002 — Immediate vs WaitForFirstConsumer

- **Unit/category:** Unit 2 / Conceptual short answer
- **Level:** L2 Intermediate
- **Objective tested:** Immediate vs WaitForFirstConsumer
- **Estimated time:** 4–12 minutes
- **Question type:** Conceptual short answer
- **Question prompt:** A claim remains Pending with a WaitForFirstConsumer class and no consumer Pod. Is this enough evidence of failure? Explain.
- **Model answer:** No. WFFC delays binding/provisioning until a consumer Pod can inform scheduling/topology. Inspect consumer existence and scheduling events before diagnosing failure.
- **Common wrong answers/misconceptions:**
- Treating one Kubernetes object status as proof of end-to-end data health — object state covers only part of the lifecycle.
- Skipping the owner/data-safety check — destructive changes require confirmed ownership, references, and recoverability.
- Assuming identical behavior across all drivers and versions — verify implementation-specific support.
- **Scoring rubric:** 3 points: correct distinction (1), evidence/reasoning (1), safety/version caveat (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 2; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] where driver, filesystem, operator, or Kubernetes release affects the behavior.

### M05-U02-Q003 — CSI architecture

- **Unit/category:** Unit 2 / Conceptual short answer
- **Level:** L3 Advanced
- **Objective tested:** CSI architecture
- **Estimated time:** 4–12 minutes
- **Question type:** Conceptual short answer
- **Question prompt:** Separate the typical responsibilities of a CSI controller plugin and node plugin.
- **Model answer:** Controller-side components commonly handle provisioning and may coordinate attach/resize/snapshot operations; the node plugin handles node-side staging/publishing and related operations. Exact capabilities and sidecars depend on the driver and installation; verify the deployed architecture.
- **Common wrong answers/misconceptions:**
- Treating one Kubernetes object status as proof of end-to-end data health — object state covers only part of the lifecycle.
- Skipping the owner/data-safety check — destructive changes require confirmed ownership, references, and recoverability.
- Assuming identical behavior across all drivers and versions — verify implementation-specific support.
- **Scoring rubric:** 3 points: correct distinction (1), evidence/reasoning (1), safety/version caveat (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 2; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] where driver, filesystem, operator, or Kubernetes release affects the behavior.

### Multiple choice

### M05-U02-Q004 — Apply a core concept and reject plausible unsafe interpretations.

- **Unit/category:** Unit 2 / Multiple choice
- **Level:** L1 Beginner
- **Objective tested:** Apply a core concept and reject plausible unsafe interpretations.
- **Estimated time:** 4–12 minutes
- **Question type:** Multiple choice
- **Question prompt:** A WFFC claim is Pending and no Pod references it. Best interpretation?
- **Options:**
  - **A.** Definite driver failure
  - **B.** Expected deferred binding may be occurring
  - **C.** Backend disk is corrupt
  - **D.** PVC must be deleted
- **Model answer:** **Correct option: B.** WFFC can defer provisioning/binding until a consumer Pod is schedulable.

- **A:** No evidence proves a driver failure.
- **B (correct):** WFFC can defer provisioning/binding until a consumer Pod is schedulable.
- **C:** No evidence concerns filesystem integrity.
- **D:** Deleting the claim is unnecessary and potentially harmful.

- **Common wrong answers/misconceptions:**
- Choosing an option based on a status word without checking the described lifecycle.
- Assuming backend or application guarantees that the prompt does not establish.
- Taking a destructive action before confirming ownership and data safety.
- **Scoring rubric:** 1 point for the correct option; up to 2 additional points for explaining why it is correct and why each distractor fails.
- **Source/coverage note:** Parent M05 syllabus, Unit 2; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact driver/version behavior where noted.

### M05-U02-Q005 — Apply a core concept and reject plausible unsafe interpretations.

- **Unit/category:** Unit 2 / Multiple choice
- **Level:** L2 Intermediate
- **Objective tested:** Apply a core concept and reject plausible unsafe interpretations.
- **Estimated time:** 4–12 minutes
- **Question type:** Multiple choice
- **Question prompt:** Which component most directly performs node-side volume mount operations in a CSI deployment?
- **Options:**
  - **A.** The StorageClass object
  - **B.** The CSI node plugin with kubelet integration
  - **C.** The PVC object
  - **D.** The namespace quota
- **Model answer:** **Correct option: B.** The node plugin participates in node-side staging/publishing with kubelet.

- **A:** StorageClass is configuration, not an executing component.
- **B (correct):** The node plugin participates in node-side staging/publishing with kubelet.
- **C:** PVC is a request object.
- **D:** Quota policy does not mount volumes.

- **Common wrong answers/misconceptions:**
- Choosing an option based on a status word without checking the described lifecycle.
- Assuming backend or application guarantees that the prompt does not establish.
- Taking a destructive action before confirming ownership and data safety.
- **Scoring rubric:** 1 point for the correct option; up to 2 additional points for explaining why it is correct and why each distractor fails.
- **Source/coverage note:** Parent M05 syllabus, Unit 2; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact driver/version behavior where noted.

### M05-U02-Q006 — Apply a core concept and reject plausible unsafe interpretations.

- **Unit/category:** Unit 2 / Multiple choice
- **Level:** L2 Intermediate
- **Objective tested:** Apply a core concept and reject plausible unsafe interpretations.
- **Estimated time:** 4–12 minutes
- **Question type:** Multiple choice
- **Question prompt:** What should be verified before changing CSI sidecar versions?
- **Options:**
  - **A.** Only the Pod name
  - **B.** Compatibility among Kubernetes, driver, sidecars, and supported features
  - **C.** Whether the PVC name is short
  - **D.** That all drivers use identical capabilities
- **Model answer:** **Correct option: B.** Compatibility and driver release guidance govern supported combinations.

- **A:** Names do not establish compatibility.
- **B (correct):** Compatibility and driver release guidance govern supported combinations.
- **C:** PVC naming does not establish compatibility.
- **D:** CSI drivers differ in capabilities and deployment architecture.

- **Common wrong answers/misconceptions:**
- Choosing an option based on a status word without checking the described lifecycle.
- Assuming backend or application guarantees that the prompt does not establish.
- Taking a destructive action before confirming ownership and data safety.
- **Scoring rubric:** 1 point for the correct option; up to 2 additional points for explaining why it is correct and why each distractor fails.
- **Source/coverage note:** Parent M05 syllabus, Unit 2; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact driver/version behavior where noted.

### Output interpretation

### M05-U02-Q010 — Interpret object/event/telemetry evidence and identify safe next checks.

- **Unit/category:** Unit 2 / Output interpretation
- **Level:** L2 Intermediate
- **Objective tested:** Interpret object/event/telemetry evidence and identify safe next checks.
- **Estimated time:** 4–12 minutes
- **Question type:** Output interpretation
- **Question prompt:** A WFFC claim has no consumer Pod and remains Pending.

What does the evidence support, what does it not prove, which read-only checks come next, and what is the safest next action?

Illustrative / expected output (not executed here):
```text
NAME       PROVISIONER              VOLUMEBINDINGMODE
slow-local example.invalid/driver   WaitForFirstConsumer
```
- **Model answer:** Pending may be expected because binding waits for a schedulable consumer. Verify the actual StorageClass and consumer workload; the placeholder provisioner above is illustrative and not installable.
- **Common wrong answers/misconceptions:**
- Treating the excerpt as proof of a single root cause without corroborating evidence.
- Deleting or patching storage objects before confirming ownership, references and data safety.
- Assuming driver/backend behavior is universal.
- **Scoring rubric:** 5 points: accurate interpretation (2), limitations/next checks (1), safe action (1), prevention or verification (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 2; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact event text/status semantics against the installed Kubernetes release and driver.

### M05-U02-Q011 — Interpret object/event/telemetry evidence and identify safe next checks.

- **Unit/category:** Unit 2 / Output interpretation
- **Level:** L3 Advanced
- **Objective tested:** Interpret object/event/telemetry evidence and identify safe next checks.
- **Estimated time:** 4–12 minutes
- **Question type:** Output interpretation
- **Question prompt:** Provisioning events show repeated failures while controller Pods restart.

What does the evidence support, what does it not prove, which read-only checks come next, and what is the safest next action?

Illustrative / expected output (not executed here):
```text
Warning ProvisioningFailed persistentvolumeclaim/data
Message: failed to provision volume: controller operation failed
```
- **Model answer:** This supports investigating provisioner/controller health, but does not identify the root cause. Check actual class provisioner, controller readiness/logs, backend capacity/authentication, and recent changes.
- **Common wrong answers/misconceptions:**
- Treating the excerpt as proof of a single root cause without corroborating evidence.
- Deleting or patching storage objects before confirming ownership, references and data safety.
- Assuming driver/backend behavior is universal.
- **Scoring rubric:** 5 points: accurate interpretation (2), limitations/next checks (1), safe action (1), prevention or verification (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 2; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact event text/status semantics against the installed Kubernetes release and driver.

### Manifest review

### M05-U02-Q012 — Review storage manifests for lifecycle, capability, security, or data-loss defects.

- **Unit/category:** Unit 2 / Manifest review
- **Level:** L3 Advanced
- **Objective tested:** Review storage manifests for lifecycle, capability, security, or data-loss defects.
- **Estimated time:** 4–12 minutes
- **Question type:** Manifest review
- **Question prompt:** Review the following design: StorageClass names a placeholder provisioner `example.invalid/csi`; it sets `volumeBindingMode: Immediate` for a topology-constrained local workload; driver secrets are referenced without confirming namespace/key.

Illustrative snippet (not validated against a live cluster):
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata: {name: local-fast}
provisioner: example.invalid/csi
volumeBindingMode: Immediate
parameters:
  secretName: backend-secret
  secretNamespace: default
```
Find at least three substantive defects or dangerous omissions, provide a corrected design/patch strategy, and distinguish schema validation from runtime capability checks.
- **Model answer:** Defects:
1. The placeholder provisioner is not a real installable driver.
2. Immediate binding can make topology-constrained placement harder; assess WFFC and workload scheduling.
3. Secret references and least-privilege/namespace/key correctness are unverified.

Safe correction: Use the actually installed provisioner and official supported parameters; select binding mode based on topology needs; verify secret references without printing secret data. Validate driver compatibility before applying.
- **Common wrong answers/misconceptions:**
- Fixing only YAML syntax while leaving lifecycle/data-safety defects.
- Assuming API acceptance proves driver/backend capability.
- Deleting existing storage before proving migration/restore and owner approval.
- **Scoring rubric:** 8 points: 1 per substantive defect up to 3; 2 for safe correction; 1 for data-loss/ownership analysis; 1 for schema-vs-runtime distinction; 1 for validation/verification plan.
- **Source/coverage note:** Parent M05 syllabus, Unit 2; snippets are assessment examples, not executed manifests.
- **Version note:** [VERIFY] validate fields, API versions, operator CRDs and driver capabilities against the installed versions.
- **Defects expected in a complete review:**
  1. The placeholder provisioner is not a real installable driver.
  2. Immediate binding can make topology-constrained placement harder; assess WFFC and workload scheduling.
  3. Secret references and least-privilege/namespace/key correctness are unverified.
- **Corrected design/patch strategy:** Use the actually installed provisioner and official supported parameters; select binding mode based on topology needs; verify secret references without printing secret data. Validate driver compatibility before applying.

### M05-U02-Q013 — Review storage manifests for lifecycle, capability, security, or data-loss defects.

- **Unit/category:** Unit 2 / Manifest review
- **Level:** L3 Advanced
- **Objective tested:** Review storage manifests for lifecycle, capability, security, or data-loss defects.
- **Estimated time:** 4–12 minutes
- **Question type:** Manifest review
- **Question prompt:** Review the following design: A manifest assumes every CSI driver supports expansion and snapshots; no driver/version is recorded; class parameters are copied from an unrelated provider.

Illustrative snippet (not validated against a live cluster):
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata: {name: local-fast}
provisioner: example.invalid/csi
volumeBindingMode: Immediate
parameters:
  secretName: backend-secret
  secretNamespace: default
```
Find at least three substantive defects or dangerous omissions, provide a corrected design/patch strategy, and distinguish schema validation from runtime capability checks.
- **Model answer:** Defects:
1. CSI capabilities are not uniform.
2. Driver/Kubernetes/sidecar versions and compatibility are not pinned/recorded.
3. Backend-specific parameters are being reused without authoritative documentation.

Safe correction: Record exact versions, inspect official driver/sidecar compatibility and capability docs, and test provision/resize/snapshot in a disposable environment. Do not infer production support from API object acceptance.
- **Common wrong answers/misconceptions:**
- Fixing only YAML syntax while leaving lifecycle/data-safety defects.
- Assuming API acceptance proves driver/backend capability.
- Deleting existing storage before proving migration/restore and owner approval.
- **Scoring rubric:** 8 points: 1 per substantive defect up to 3; 2 for safe correction; 1 for data-loss/ownership analysis; 1 for schema-vs-runtime distinction; 1 for validation/verification plan.
- **Source/coverage note:** Parent M05 syllabus, Unit 2; snippets are assessment examples, not executed manifests.
- **Version note:** [VERIFY] validate fields, API versions, operator CRDs and driver capabilities against the installed versions.
- **Defects expected in a complete review:**
  1. CSI capabilities are not uniform.
  2. Driver/Kubernetes/sidecar versions and compatibility are not pinned/recorded.
  3. Backend-specific parameters are being reused without authoritative documentation.
- **Corrected design/patch strategy:** Record exact versions, inspect official driver/sidecar compatibility and capability docs, and test provision/resize/snapshot in a disposable environment. Do not infer production support from API object acceptance.

### Incident/troubleshooting scenario

### M05-U02-Q014 — Use evidence-led troubleshooting and data-safety gates for a realistic storage incident.

- **Unit/category:** Unit 2 / Incident/troubleshooting scenario
- **Level:** L3 Advanced
- **Objective tested:** Use evidence-led troubleshooting and data-safety gates for a realistic storage incident.
- **Estimated time:** 4–12 minutes
- **Question type:** Incident/troubleshooting scenario
- **Question prompt:** New claims are Pending after a CSI controller rollout. Existing Pods still have mounted volumes, but the driver deployment reports restarts.

Give a ranked hypothesis, the first read-only checks, ownership/data-safety decision, safe mitigation/recovery, post-fix verification, prevention, and conditions that require stop-work/escalation.
- **Model answer:** Establish driver and operation scope; inspect controller/sidecar readiness, rollout diff, PVC events and backend auth/capacity. Existing mounted I/O may continue while new operations fail, but this is driver/operation-dependent [VERIFY]. Restore the controller via its owner/runbook; test provisioning/attach/resize/snapshot separately and reconcile leftovers. Do not force-delete claims.
- **Common wrong answers/misconceptions:**
- Jumping to deletion/finalizer removal/force-detach before evidence and data-safety checks.
- Treating one status or event as a complete root-cause proof.
- Skipping application-level verification after Kubernetes status recovers.
- **Scoring rubric:** 8 points: impact/evidence (2), ranked hypotheses (1), data-safety gate (1), safe recovery (2), verification (1), prevention/escalation (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 2; scenario synthesized from the explicit unit objectives.
- **Version note:** [VERIFY] driver/operator/filesystem specifics and runbook steps before production action.

### Design question

### M05-U02-Q015 — Make a defensible design with explicit constraints, trade-offs, failure modes and validati

- **Unit/category:** Unit 2 / Design question
- **Level:** L4 Expert
- **Objective tested:** Make a defensible design with explicit constraints, trade-offs, failure modes and validation.
- **Estimated time:** 4–12 minutes
- **Question type:** Design question
- **Question prompt:** Design a StorageClass/CSI onboarding checklist for a topology-constrained workload, including binding mode, compatibility, secrets, capacity, observability and a safe failure test.

State assumptions, compare at least two options, identify failure modes, define security/data-safety controls, and specify validation evidence.
- **Model answer:** Record Kubernetes/driver/sidecar versions and compatibility; choose Immediate/WFFC based on topology; verify provisioner/class parameters and allowedTopologies; use least-privilege Secret references; test provision/attach/mount/resize/snapshot separately; monitor controller/node plugins and reconcile backend inventory. Keep a rollback and no-data-loss test.
- **Common wrong answers/misconceptions:**
- Optimizing only for availability or cost while ignoring data integrity/recovery.
- Treating Kubernetes object readiness as proof of application correctness.
- Claiming driver or topology capabilities without verifying the deployed implementation.
- **Scoring rubric:** 8 points: constraints/options (2), lifecycle/data safety (2), failure modes/recovery (2), validation and security/cost trade-offs (2). Safety-critical unsafe deletion/force-detach/fsck-on-mounted-volume caps score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, Unit 2; design is aligned to stated unit outcomes.
- **Version note:** [VERIFY] exact implementation/API/backend support before implementation.

## 9.5 Unit 3 — Volume Snapshots, Cloning, Expansion

### Conceptual short answer

### M05-U03-Q001 — snapshot API objects

- **Unit/category:** Unit 3 / Conceptual short answer
- **Level:** L1 Beginner
- **Objective tested:** snapshot API objects
- **Estimated time:** 4–12 minutes
- **Question type:** Conceptual short answer
- **Question prompt:** Describe the relationship among VolumeSnapshot, VolumeSnapshotContent, and VolumeSnapshotClass.
- **Model answer:** The namespaced VolumeSnapshot expresses a user's snapshot request; cluster-scoped VolumeSnapshotContent represents the provisioned snapshot; VolumeSnapshotClass defines driver/policy parameters. These APIs require compatible CRDs/controller/driver support.
- **Common wrong answers/misconceptions:**
- Treating one Kubernetes object status as proof of end-to-end data health — object state covers only part of the lifecycle.
- Skipping the owner/data-safety check — destructive changes require confirmed ownership, references, and recoverability.
- Assuming identical behavior across all drivers and versions — verify implementation-specific support.
- **Scoring rubric:** 3 points: correct distinction (1), evidence/reasoning (1), safety/version caveat (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 3; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] where driver, filesystem, operator, or Kubernetes release affects the behavior.

### M05-U03-Q002 — restore and clone

- **Unit/category:** Unit 3 / Conceptual short answer
- **Level:** L2 Intermediate
- **Objective tested:** restore and clone
- **Estimated time:** 4–12 minutes
- **Question type:** Conceptual short answer
- **Question prompt:** What does creating a PVC from a snapshot prove, and what must a restore test additionally establish?
- **Model answer:** It proves the API accepted a restore request only if it completes; it does not prove application consistency or recoverability. Verify the target mounts, application starts, records/checksums validate, and the recovery point meets requirements.
- **Common wrong answers/misconceptions:**
- Treating one Kubernetes object status as proof of end-to-end data health — object state covers only part of the lifecycle.
- Skipping the owner/data-safety check — destructive changes require confirmed ownership, references, and recoverability.
- Assuming identical behavior across all drivers and versions — verify implementation-specific support.
- **Scoring rubric:** 3 points: correct distinction (1), evidence/reasoning (1), safety/version caveat (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 3; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] where driver, filesystem, operator, or Kubernetes release affects the behavior.

### M05-U03-Q003 — expansion

- **Unit/category:** Unit 3 / Conceptual short answer
- **Level:** L3 Advanced
- **Objective tested:** expansion
- **Estimated time:** 4–12 minutes
- **Question type:** Conceptual short answer
- **Question prompt:** Explain why an increased PVC request may not immediately increase the filesystem size.
- **Model answer:** Backend/controller expansion and node/filesystem resize can be separate stages. Check StorageClass expansion policy, PVC conditions/events, CSI resizer/node logs, and filesystem size. Normal PVC expansion does not provide a shrink operation; migration may be required.
- **Common wrong answers/misconceptions:**
- Treating one Kubernetes object status as proof of end-to-end data health — object state covers only part of the lifecycle.
- Skipping the owner/data-safety check — destructive changes require confirmed ownership, references, and recoverability.
- Assuming identical behavior across all drivers and versions — verify implementation-specific support.
- **Scoring rubric:** 3 points: correct distinction (1), evidence/reasoning (1), safety/version caveat (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 3; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] where driver, filesystem, operator, or Kubernetes release affects the behavior.

### Multiple choice

### M05-U03-Q004 — Apply a core concept and reject plausible unsafe interpretations.

- **Unit/category:** Unit 3 / Multiple choice
- **Level:** L1 Beginner
- **Objective tested:** Apply a core concept and reject plausible unsafe interpretations.
- **Estimated time:** 4–12 minutes
- **Question type:** Multiple choice
- **Question prompt:** What does readyToUse on a VolumeSnapshot establish by itself?
- **Options:**
  - **A.** A successful application-level restore
  - **B.** A controller-reported readiness state, not a restore test
  - **C.** That the snapshot is in another account
  - **D.** That the database has no unflushed transactions
- **Model answer:** **Correct option: B.** Readiness is not equivalent to a verified restore or application consistency.

- **A:** Only restoring and checking data tests recoverability.
- **B (correct):** Readiness is not equivalent to a verified restore or application consistency.
- **C:** Cross-account independence is not implied.
- **D:** Crash/application consistency depends on the process and application.

- **Common wrong answers/misconceptions:**
- Choosing an option based on a status word without checking the described lifecycle.
- Assuming backend or application guarantees that the prompt does not establish.
- Taking a destructive action before confirming ownership and data safety.
- **Scoring rubric:** 1 point for the correct option; up to 2 additional points for explaining why it is correct and why each distractor fails.
- **Source/coverage note:** Parent M05 syllabus, Unit 3; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact driver/version behavior where noted.

### M05-U03-Q005 — Apply a core concept and reject plausible unsafe interpretations.

- **Unit/category:** Unit 3 / Multiple choice
- **Level:** L2 Intermediate
- **Objective tested:** Apply a core concept and reject plausible unsafe interpretations.
- **Estimated time:** 4–12 minutes
- **Question type:** Multiple choice
- **Question prompt:** Which resize sequence is the safest diagnosis?
- **Options:**
  - **A.** Immediately delete and recreate the PVC
  - **B.** Check allowVolumeExpansion, PVC conditions/events, CSI resizer and filesystem size
  - **C.** Run fsck on the mounted filesystem
  - **D.** Assume filesystem expansion always happens instantly
- **Model answer:** **Correct option: B.** Evidence identifies which expansion stage is pending or unsupported.

- **A:** Recreating can destroy or orphan data.
- **B (correct):** Evidence identifies which expansion stage is pending or unsupported.
- **C:** fsck is not an expansion diagnostic and must not run on a mounted filesystem.
- **D:** Controller and filesystem stages can be separate.

- **Common wrong answers/misconceptions:**
- Choosing an option based on a status word without checking the described lifecycle.
- Assuming backend or application guarantees that the prompt does not establish.
- Taking a destructive action before confirming ownership and data safety.
- **Scoring rubric:** 1 point for the correct option; up to 2 additional points for explaining why it is correct and why each distractor fails.
- **Source/coverage note:** Parent M05 syllabus, Unit 3; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact driver/version behavior where noted.

### M05-U03-Q006 — Apply a core concept and reject plausible unsafe interpretations.

- **Unit/category:** Unit 3 / Multiple choice
- **Level:** L2 Intermediate
- **Objective tested:** Apply a core concept and reject plausible unsafe interpretations.
- **Estimated time:** 4–12 minutes
- **Question type:** Multiple choice
- **Question prompt:** Which statement about normal PVC expansion is correct?
- **Options:**
  - **A.** It is a supported shrink operation too
  - **B.** Shrinking is not supported by the normal expansion flow
  - **C.** It always works for every driver
  - **D.** It proves a backup exists
- **Model answer:** **Correct option: B.** Normal PVC expansion does not provide a shrink operation.

- **A:** This reverses the normal behavior.
- **B (correct):** Normal PVC expansion does not provide a shrink operation.
- **C:** Support depends on StorageClass/driver/backend.
- **D:** Resize is not backup.

- **Common wrong answers/misconceptions:**
- Choosing an option based on a status word without checking the described lifecycle.
- Assuming backend or application guarantees that the prompt does not establish.
- Taking a destructive action before confirming ownership and data safety.
- **Scoring rubric:** 1 point for the correct option; up to 2 additional points for explaining why it is correct and why each distractor fails.
- **Source/coverage note:** Parent M05 syllabus, Unit 3; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact driver/version behavior where noted.

### Output interpretation

### M05-U03-Q010 — Interpret object/event/telemetry evidence and identify safe next checks.

- **Unit/category:** Unit 3 / Output interpretation
- **Level:** L2 Intermediate
- **Objective tested:** Interpret object/event/telemetry evidence and identify safe next checks.
- **Estimated time:** 4–12 minutes
- **Question type:** Output interpretation
- **Question prompt:** Snapshot is created but readyToUse is false and controller logs report unsupported capability.

What does the evidence support, what does it not prove, which read-only checks come next, and what is the safest next action?

Illustrative / expected output (not executed here):
```text
VolumeSnapshot/data-snap: readyToUse=false
Controller log: requested snapshot operation is unsupported
```
- **Model answer:** Snapshot workflow is incomplete and capability support is in question. Check CRDs, snapshot controller/class, CSI driver capability and compatibility. Do not treat the object as a backup or delete it if retention is unknown.
- **Common wrong answers/misconceptions:**
- Treating the excerpt as proof of a single root cause without corroborating evidence.
- Deleting or patching storage objects before confirming ownership, references and data safety.
- Assuming driver/backend behavior is universal.
- **Scoring rubric:** 5 points: accurate interpretation (2), limitations/next checks (1), safe action (1), prevention or verification (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 3; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact event text/status semantics against the installed Kubernetes release and driver.

### M05-U03-Q011 — Interpret object/event/telemetry evidence and identify safe next checks.

- **Unit/category:** Unit 3 / Output interpretation
- **Level:** L3 Advanced
- **Objective tested:** Interpret object/event/telemetry evidence and identify safe next checks.
- **Estimated time:** 4–12 minutes
- **Question type:** Output interpretation
- **Question prompt:** PVC request increased; PVC conditions include FileSystemResizePending.

What does the evidence support, what does it not prove, which read-only checks come next, and what is the safest next action?

Illustrative / expected output (not executed here):
```yaml
status:
  conditions:
  - type: FileSystemResizePending
    status: "True"
```
- **Model answer:** The node/filesystem resize stage may still be pending after a resize request. Inspect PVC events, CSI resizer/node logs and actual filesystem size; verify driver/filesystem support. Do not shrink/recreate the volume as a shortcut.
- **Common wrong answers/misconceptions:**
- Treating the excerpt as proof of a single root cause without corroborating evidence.
- Deleting or patching storage objects before confirming ownership, references and data safety.
- Assuming driver/backend behavior is universal.
- **Scoring rubric:** 5 points: accurate interpretation (2), limitations/next checks (1), safe action (1), prevention or verification (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 3; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact event text/status semantics against the installed Kubernetes release and driver.

### Manifest review

### M05-U03-Q012 — Review storage manifests for lifecycle, capability, security, or data-loss defects.

- **Unit/category:** Unit 3 / Manifest review
- **Level:** L3 Advanced
- **Objective tested:** Review storage manifests for lifecycle, capability, security, or data-loss defects.
- **Estimated time:** 4–12 minutes
- **Question type:** Manifest review
- **Question prompt:** Review the following design: A VolumeSnapshot is applied but the cluster has no verified snapshot CRDs/controller; deletionPolicy is assumed; restore claim uses an unverified source reference.

Illustrative snippet (not validated against a live cluster):
```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata: {name: db-snap, namespace: app}
spec:
  volumeSnapshotClassName: assumed-default
  source:
    persistentVolumeClaimName: db-data
# restore is assumed safe as soon as readyToUse is true
```
Find at least three substantive defects or dangerous omissions, provide a corrected design/patch strategy, and distinguish schema validation from runtime capability checks.
- **Model answer:** Defects:
1. Snapshot API/controller installation is not verified.
2. Deletion policy/retention behavior is assumed.
3. Restore dataSource kind/name/namespace compatibility is not checked.

Safe correction: Verify installed CRDs/controller/class and driver capability, document retention, and validate the exact API schema. Restore to a new disposable claim and check application data before relying on the snapshot.
- **Common wrong answers/misconceptions:**
- Fixing only YAML syntax while leaving lifecycle/data-safety defects.
- Assuming API acceptance proves driver/backend capability.
- Deleting existing storage before proving migration/restore and owner approval.
- **Scoring rubric:** 8 points: 1 per substantive defect up to 3; 2 for safe correction; 1 for data-loss/ownership analysis; 1 for schema-vs-runtime distinction; 1 for validation/verification plan.
- **Source/coverage note:** Parent M05 syllabus, Unit 3; snippets are assessment examples, not executed manifests.
- **Version note:** [VERIFY] validate fields, API versions, operator CRDs and driver capabilities against the installed versions.
- **Defects expected in a complete review:**
  1. Snapshot API/controller installation is not verified.
  2. Deletion policy/retention behavior is assumed.
  3. Restore dataSource kind/name/namespace compatibility is not checked.
- **Corrected design/patch strategy:** Verify installed CRDs/controller/class and driver capability, document retention, and validate the exact API schema. Restore to a new disposable claim and check application data before relying on the snapshot.

### M05-U03-Q013 — Review storage manifests for lifecycle, capability, security, or data-loss defects.

- **Unit/category:** Unit 3 / Manifest review
- **Level:** L3 Advanced
- **Objective tested:** Review storage manifests for lifecycle, capability, security, or data-loss defects.
- **Estimated time:** 4–12 minutes
- **Question type:** Manifest review
- **Question prompt:** Review the following design: A team expands a PVC, expects shrink to be supported later, and deletes the old volume immediately after the new claim binds.

Illustrative snippet (not validated against a live cluster):
```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata: {name: db-snap, namespace: app}
spec:
  volumeSnapshotClassName: assumed-default
  source:
    persistentVolumeClaimName: db-data
# restore is assumed safe as soon as readyToUse is true
```
Find at least three substantive defects or dangerous omissions, provide a corrected design/patch strategy, and distinguish schema validation from runtime capability checks.
- **Model answer:** Defects:
1. Normal PVC expansion does not provide shrink.
2. Binding the new claim does not prove data copied correctly.
3. Deleting the old volume before application-level validation/backup can cause data loss.

Safe correction: Plan migration/copy with checksums or application validation, verify backup and target size, cut over under a rollback plan, and retain the old source until approval and recovery criteria are met.
- **Common wrong answers/misconceptions:**
- Fixing only YAML syntax while leaving lifecycle/data-safety defects.
- Assuming API acceptance proves driver/backend capability.
- Deleting existing storage before proving migration/restore and owner approval.
- **Scoring rubric:** 8 points: 1 per substantive defect up to 3; 2 for safe correction; 1 for data-loss/ownership analysis; 1 for schema-vs-runtime distinction; 1 for validation/verification plan.
- **Source/coverage note:** Parent M05 syllabus, Unit 3; snippets are assessment examples, not executed manifests.
- **Version note:** [VERIFY] validate fields, API versions, operator CRDs and driver capabilities against the installed versions.
- **Defects expected in a complete review:**
  1. Normal PVC expansion does not provide shrink.
  2. Binding the new claim does not prove data copied correctly.
  3. Deleting the old volume before application-level validation/backup can cause data loss.
- **Corrected design/patch strategy:** Plan migration/copy with checksums or application validation, verify backup and target size, cut over under a rollback plan, and retain the old source until approval and recovery criteria are met.

### Incident/troubleshooting scenario

### M05-U03-Q014 — Use evidence-led troubleshooting and data-safety gates for a realistic storage incident.

- **Unit/category:** Unit 3 / Incident/troubleshooting scenario
- **Level:** L3 Advanced
- **Objective tested:** Use evidence-led troubleshooting and data-safety gates for a realistic storage incident.
- **Estimated time:** 4–12 minutes
- **Question type:** Incident/troubleshooting scenario
- **Question prompt:** A snapshot reports readyToUse, but the first restore attempt produces an application that starts with missing expected records.

Give a ranked hypothesis, the first read-only checks, ownership/data-safety decision, safe mitigation/recovery, post-fix verification, prevention, and conditions that require stop-work/escalation.
- **Model answer:** Treat snapshot readiness as insufficient. Preserve source and logs; check restore target, snapshot/content/class/driver, database consistency procedure, recovery point and app-level expected records/checksums. Restore again to a separate disposable target only under a reviewed plan; do not overwrite the source. Record measured RPO/RTO and fix backup validation.
- **Common wrong answers/misconceptions:**
- Jumping to deletion/finalizer removal/force-detach before evidence and data-safety checks.
- Treating one status or event as a complete root-cause proof.
- Skipping application-level verification after Kubernetes status recovers.
- **Scoring rubric:** 8 points: impact/evidence (2), ranked hypotheses (1), data-safety gate (1), safe recovery (2), verification (1), prevention/escalation (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 3; scenario synthesized from the explicit unit objectives.
- **Version note:** [VERIFY] driver/operator/filesystem specifics and runbook steps before production action.

### Design question

### M05-U03-Q015 — Make a defensible design with explicit constraints, trade-offs, failure modes and validati

- **Unit/category:** Unit 3 / Design question
- **Level:** L4 Expert
- **Objective tested:** Make a defensible design with explicit constraints, trade-offs, failure modes and validation.
- **Estimated time:** 4–12 minutes
- **Question type:** Design question
- **Question prompt:** Design a backup/restore validation plan for a PostgreSQL workload using snapshots where supported, with a separate recovery copy, consistency procedure, RPO/RTO and expansion strategy.

State assumptions, compare at least two options, identify failure modes, define security/data-safety controls, and specify validation evidence.
- **Model answer:** Document source data owner and consistency procedure; snapshot only with supported driver; create a separate target; validate database startup and representative records/checksums; test retention/deletion policy; measure recovery time and recovered data point; verify expansion support and never assume shrink. Snapshot alone is not an independent backup.
- **Common wrong answers/misconceptions:**
- Optimizing only for availability or cost while ignoring data integrity/recovery.
- Treating Kubernetes object readiness as proof of application correctness.
- Claiming driver or topology capabilities without verifying the deployed implementation.
- **Scoring rubric:** 8 points: constraints/options (2), lifecycle/data safety (2), failure modes/recovery (2), validation and security/cost trade-offs (2). Safety-critical unsafe deletion/force-detach/fsck-on-mounted-volume caps score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, Unit 3; design is aligned to stated unit outcomes.
- **Version note:** [VERIFY] exact implementation/API/backend support before implementation.

## 9.6 Unit 4 — StatefulSet Storage Patterns and Stable Identity

### Conceptual short answer

### M05-U04-Q001 — stable identity

- **Unit/category:** Unit 4 / Conceptual short answer
- **Level:** L1 Beginner
- **Objective tested:** stable identity
- **Estimated time:** 4–12 minutes
- **Question type:** Conceptual short answer
- **Question prompt:** What does StatefulSet stable identity provide, and what does it not provide?
- **Model answer:** It provides stable ordinal/network identity and claim naming patterns for replicas. It does not itself replicate data, guarantee durability, or make an application highly available.
- **Common wrong answers/misconceptions:**
- Treating one Kubernetes object status as proof of end-to-end data health — object state covers only part of the lifecycle.
- Skipping the owner/data-safety check — destructive changes require confirmed ownership, references, and recoverability.
- Assuming identical behavior across all drivers and versions — verify implementation-specific support.
- **Scoring rubric:** 3 points: correct distinction (1), evidence/reasoning (1), safety/version caveat (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 4; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] where driver, filesystem, operator, or Kubernetes release affects the behavior.

### M05-U04-Q002 — claim templates

- **Unit/category:** Unit 4 / Conceptual short answer
- **Level:** L2 Intermediate
- **Objective tested:** claim templates
- **Estimated time:** 4–12 minutes
- **Question type:** Conceptual short answer
- **Question prompt:** Explain the storage lifecycle of claims created from volumeClaimTemplates when a StatefulSet Pod is replaced.
- **Model answer:** The replacement Pod normally reuses the claim associated with its ordinal; the claim and data can outlive the Pod. Deletion/scale-down retention behavior depends on configuration/version and must be checked before lifecycle changes.
- **Common wrong answers/misconceptions:**
- Treating one Kubernetes object status as proof of end-to-end data health — object state covers only part of the lifecycle.
- Skipping the owner/data-safety check — destructive changes require confirmed ownership, references, and recoverability.
- Assuming identical behavior across all drivers and versions — verify implementation-specific support.
- **Scoring rubric:** 3 points: correct distinction (1), evidence/reasoning (1), safety/version caveat (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 4; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] where driver, filesystem, operator, or Kubernetes release affects the behavior.

### M05-U04-Q003 — rollout and quorum

- **Unit/category:** Unit 4 / Conceptual short answer
- **Level:** L3 Advanced
- **Objective tested:** rollout and quorum
- **Estimated time:** 4–12 minutes
- **Question type:** Conceptual short answer
- **Question prompt:** Why can a rolling update be unsafe for a stateful quorum-based service even when Pods eventually become Ready?
- **Model answer:** Readiness alone does not prove quorum, replication catch-up, or data consistency. Review update strategy/partition, PDB, replica health, disruption budget, and application/operator guidance before rollout.
- **Common wrong answers/misconceptions:**
- Treating one Kubernetes object status as proof of end-to-end data health — object state covers only part of the lifecycle.
- Skipping the owner/data-safety check — destructive changes require confirmed ownership, references, and recoverability.
- Assuming identical behavior across all drivers and versions — verify implementation-specific support.
- **Scoring rubric:** 3 points: correct distinction (1), evidence/reasoning (1), safety/version caveat (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 4; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] where driver, filesystem, operator, or Kubernetes release affects the behavior.

### Multiple choice

### M05-U04-Q004 — Apply a core concept and reject plausible unsafe interpretations.

- **Unit/category:** Unit 4 / Multiple choice
- **Level:** L1 Beginner
- **Objective tested:** Apply a core concept and reject plausible unsafe interpretations.
- **Estimated time:** 4–12 minutes
- **Question type:** Multiple choice
- **Question prompt:** A StatefulSet Pod is replaced. What most commonly preserves its per-ordinal data association?
- **Options:**
  - **A.** The Pod IP address
  - **B.** The ordinal-associated PVC created from volumeClaimTemplates
  - **C.** A Service selector alone
  - **D.** A PDB
- **Model answer:** **Correct option: B.** The claim naming/association provides the persistent storage link for the ordinal.

- **A:** Pod IP can change.
- **B (correct):** The claim naming/association provides the persistent storage link for the ordinal.
- **C:** A Service routes traffic but does not store data.
- **D:** PDB limits disruptions; it does not preserve data.

- **Common wrong answers/misconceptions:**
- Choosing an option based on a status word without checking the described lifecycle.
- Assuming backend or application guarantees that the prompt does not establish.
- Taking a destructive action before confirming ownership and data safety.
- **Scoring rubric:** 1 point for the correct option; up to 2 additional points for explaining why it is correct and why each distractor fails.
- **Source/coverage note:** Parent M05 syllabus, Unit 4; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact driver/version behavior where noted.

### M05-U04-Q005 — Apply a core concept and reject plausible unsafe interpretations.

- **Unit/category:** Unit 4 / Multiple choice
- **Level:** L2 Intermediate
- **Objective tested:** Apply a core concept and reject plausible unsafe interpretations.
- **Estimated time:** 4–12 minutes
- **Question type:** Multiple choice
- **Question prompt:** Which claim is safe to make about StatefulSet identity?
- **Options:**
  - **A.** Stable identity means data is replicated
  - **B.** Stable ordinal identity does not itself provide replication or durability
  - **C.** Every StatefulSet has automatic backups
  - **D.** PDB guarantees quorum
- **Model answer:** **Correct option: B.** Identity and persistence association are not replication or backup.

- **A:** Identity is not replication.
- **B (correct):** Identity and persistence association are not replication or backup.
- **C:** Backups require an explicit system and restore validation.
- **D:** PDB does not guarantee application quorum.

- **Common wrong answers/misconceptions:**
- Choosing an option based on a status word without checking the described lifecycle.
- Assuming backend or application guarantees that the prompt does not establish.
- Taking a destructive action before confirming ownership and data safety.
- **Scoring rubric:** 1 point for the correct option; up to 2 additional points for explaining why it is correct and why each distractor fails.
- **Source/coverage note:** Parent M05 syllabus, Unit 4; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact driver/version behavior where noted.

### M05-U04-Q006 — Apply a core concept and reject plausible unsafe interpretations.

- **Unit/category:** Unit 4 / Multiple choice
- **Level:** L2 Intermediate
- **Objective tested:** Apply a core concept and reject plausible unsafe interpretations.
- **Estimated time:** 4–12 minutes
- **Question type:** Multiple choice
- **Question prompt:** Before scaling a database StatefulSet down, what should be checked first?
- **Options:**
  - **A.** Only the desired replica count
  - **B.** Application/operator procedure, replica/quorum health, claim-retention behavior and recovery plan
  - **C.** Whether the Pod names are alphabetical
  - **D.** Whether the Service has a ClusterIP
- **Model answer:** **Correct option: B.** Scale-down can affect data-bearing members and claims; review application and retention semantics.

- **A:** Replica count alone is insufficient.
- **B (correct):** Scale-down can affect data-bearing members and claims; review application and retention semantics.
- **C:** Alphabetical names do not establish safe lifecycle.
- **D:** Service ClusterIP does not establish storage safety.

- **Common wrong answers/misconceptions:**
- Choosing an option based on a status word without checking the described lifecycle.
- Assuming backend or application guarantees that the prompt does not establish.
- Taking a destructive action before confirming ownership and data safety.
- **Scoring rubric:** 1 point for the correct option; up to 2 additional points for explaining why it is correct and why each distractor fails.
- **Source/coverage note:** Parent M05 syllabus, Unit 4; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact driver/version behavior where noted.

### Output interpretation

### M05-U04-Q010 — Interpret object/event/telemetry evidence and identify safe next checks.

- **Unit/category:** Unit 4 / Output interpretation
- **Level:** L2 Intermediate
- **Objective tested:** Interpret object/event/telemetry evidence and identify safe next checks.
- **Estimated time:** 4–12 minutes
- **Question type:** Output interpretation
- **Question prompt:** A replacement StatefulSet Pod uses the same ordinal claim name.

What does the evidence support, what does it not prove, which read-only checks come next, and what is the safest next action?

Illustrative / expected output (not executed here):
```text
NAME       STATUS   VOLUME
 data-db-0 Bound    pvc-abc
Pod/db-0   Pending  (event: volume node affinity conflict)
```
- **Model answer:** Stable ordinal-to-claim association may exist while scheduling still fails. Check PV affinity, node labels, Pod constraints and class topology; Bound does not prove mountability or application health.
- **Common wrong answers/misconceptions:**
- Treating the excerpt as proof of a single root cause without corroborating evidence.
- Deleting or patching storage objects before confirming ownership, references and data safety.
- Assuming driver/backend behavior is universal.
- **Scoring rubric:** 5 points: accurate interpretation (2), limitations/next checks (1), safe action (1), prevention or verification (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 4; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact event text/status semantics against the installed Kubernetes release and driver.

### M05-U04-Q011 — Interpret object/event/telemetry evidence and identify safe next checks.

- **Unit/category:** Unit 4 / Output interpretation
- **Level:** L3 Advanced
- **Objective tested:** Interpret object/event/telemetry evidence and identify safe next checks.
- **Estimated time:** 4–12 minutes
- **Question type:** Output interpretation
- **Question prompt:** A scale-down removed an ordinal but a PVC remains.

What does the evidence support, what does it not prove, which read-only checks come next, and what is the safest next action?

Illustrative / expected output (not executed here):
```text
StatefulSet replicas: 2
PVC data-db-2: Bound
```
- **Model answer:** A remaining claim may reflect retention behavior and may hold important data. Check StatefulSet retention policy/version, owner, operator and recovery requirements. Do not delete it solely because its ordinal is currently absent.
- **Common wrong answers/misconceptions:**
- Treating the excerpt as proof of a single root cause without corroborating evidence.
- Deleting or patching storage objects before confirming ownership, references and data safety.
- Assuming driver/backend behavior is universal.
- **Scoring rubric:** 5 points: accurate interpretation (2), limitations/next checks (1), safe action (1), prevention or verification (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 4; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact event text/status semantics against the installed Kubernetes release and driver.

### Manifest review

### M05-U04-Q012 — Review storage manifests for lifecycle, capability, security, or data-loss defects.

- **Unit/category:** Unit 4 / Manifest review
- **Level:** L3 Advanced
- **Objective tested:** Review storage manifests for lifecycle, capability, security, or data-loss defects.
- **Estimated time:** 4–12 minutes
- **Question type:** Manifest review
- **Question prompt:** Review the following design: StatefulSet claim template is edited assuming existing claims will be recreated automatically; scale-down deletes ordinal claims without retention review; rollout proceeds without replication/quorum checks.

Illustrative snippet (not validated against a live cluster):
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata: {name: db}
spec:
  replicas: 3
  selector: {matchLabels: {app: db}}
  serviceName: db
  template:
    metadata: {labels: {app: db}}
    spec:
      containers:
      - name: db
        image: postgres:latest
        volumeMounts: [{name: data, mountPath: /var/lib/postgresql/data}]
  volumeClaimTemplates: [] # existing claim migration assumed automatic
```
Find at least three substantive defects or dangerous omissions, provide a corrected design/patch strategy, and distinguish schema validation from runtime capability checks.
- **Model answer:** Defects:
1. Existing PVCs are not safely migrated merely by changing the template.
2. Claim deletion/retention behavior must be checked; data may be lost or retained unexpectedly.
3. Rollout lacks application-level quorum/replication and disruption review.

Safe correction: Review exact StatefulSet version/policy and operator procedure, snapshot/backup and validate restore, assess quorum and PDB/readiness, then perform a staged change with post-change data checks.
- **Common wrong answers/misconceptions:**
- Fixing only YAML syntax while leaving lifecycle/data-safety defects.
- Assuming API acceptance proves driver/backend capability.
- Deleting existing storage before proving migration/restore and owner approval.
- **Scoring rubric:** 8 points: 1 per substantive defect up to 3; 2 for safe correction; 1 for data-loss/ownership analysis; 1 for schema-vs-runtime distinction; 1 for validation/verification plan.
- **Source/coverage note:** Parent M05 syllabus, Unit 4; snippets are assessment examples, not executed manifests.
- **Version note:** [VERIFY] validate fields, API versions, operator CRDs and driver capabilities against the installed versions.
- **Defects expected in a complete review:**
  1. Existing PVCs are not safely migrated merely by changing the template.
  2. Claim deletion/retention behavior must be checked; data may be lost or retained unexpectedly.
  3. Rollout lacks application-level quorum/replication and disruption review.
- **Corrected design/patch strategy:** Review exact StatefulSet version/policy and operator procedure, snapshot/backup and validate restore, assess quorum and PDB/readiness, then perform a staged change with post-change data checks.

### M05-U04-Q013 — Review storage manifests for lifecycle, capability, security, or data-loss defects.

- **Unit/category:** Unit 4 / Manifest review
- **Level:** L3 Advanced
- **Objective tested:** Review storage manifests for lifecycle, capability, security, or data-loss defects.
- **Estimated time:** 4–12 minutes
- **Question type:** Manifest review
- **Question prompt:** Review the following design: A Pod uses a new ordinal but mounts a manually named shared claim; two replicas write concurrently without checking access mode/application semantics; a PDB is treated as a backup.

Illustrative snippet (not validated against a live cluster):
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata: {name: db}
spec:
  replicas: 3
  selector: {matchLabels: {app: db}}
  serviceName: db
  template:
    metadata: {labels: {app: db}}
    spec:
      containers:
      - name: db
        image: postgres:latest
        volumeMounts: [{name: data, mountPath: /var/lib/postgresql/data}]
  volumeClaimTemplates: [] # existing claim migration assumed automatic
```
Find at least three substantive defects or dangerous omissions, provide a corrected design/patch strategy, and distinguish schema validation from runtime capability checks.
- **Model answer:** Defects:
1. Claim-per-replica identity is bypassed or ambiguous.
2. Concurrent write semantics may be unsupported or unsafe for the backend/application.
3. A PDB controls disruption availability; it is not a backup or data replication mechanism.

Safe correction: Use a reviewed per-replica claim design or supported shared-storage/application protocol, validate access mode and consistency semantics, and establish independent backup/restore.
- **Common wrong answers/misconceptions:**
- Fixing only YAML syntax while leaving lifecycle/data-safety defects.
- Assuming API acceptance proves driver/backend capability.
- Deleting existing storage before proving migration/restore and owner approval.
- **Scoring rubric:** 8 points: 1 per substantive defect up to 3; 2 for safe correction; 1 for data-loss/ownership analysis; 1 for schema-vs-runtime distinction; 1 for validation/verification plan.
- **Source/coverage note:** Parent M05 syllabus, Unit 4; snippets are assessment examples, not executed manifests.
- **Version note:** [VERIFY] validate fields, API versions, operator CRDs and driver capabilities against the installed versions.
- **Defects expected in a complete review:**
  1. Claim-per-replica identity is bypassed or ambiguous.
  2. Concurrent write semantics may be unsupported or unsafe for the backend/application.
  3. A PDB controls disruption availability; it is not a backup or data replication mechanism.
- **Corrected design/patch strategy:** Use a reviewed per-replica claim design or supported shared-storage/application protocol, validate access mode and consistency semantics, and establish independent backup/restore.

### Incident/troubleshooting scenario

### M05-U04-Q014 — Use evidence-led troubleshooting and data-safety gates for a realistic storage incident.

- **Unit/category:** Unit 4 / Incident/troubleshooting scenario
- **Level:** L3 Advanced
- **Objective tested:** Use evidence-led troubleshooting and data-safety gates for a realistic storage incident.
- **Estimated time:** 4–12 minutes
- **Question type:** Incident/troubleshooting scenario
- **Question prompt:** After a StatefulSet scale-down and later scale-up, an ordinal Pod is blocked and an old claim remains.

Give a ranked hypothesis, the first read-only checks, ownership/data-safety decision, safe mitigation/recovery, post-fix verification, prevention, and conditions that require stop-work/escalation.
- **Model answer:** Inspect StatefulSet claim templates, ordinal claim names, retention policy/version, Pod events, PV affinity, operator status and owner. Confirm data identity before creating/rebinding a claim. Follow operator-supported recovery; verify database membership/data before scaling further. Do not delete the old claim because the ordinal is absent.
- **Common wrong answers/misconceptions:**
- Jumping to deletion/finalizer removal/force-detach before evidence and data-safety checks.
- Treating one status or event as a complete root-cause proof.
- Skipping application-level verification after Kubernetes status recovers.
- **Scoring rubric:** 8 points: impact/evidence (2), ranked hypotheses (1), data-safety gate (1), safe recovery (2), verification (1), prevention/escalation (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 4; scenario synthesized from the explicit unit objectives.
- **Version note:** [VERIFY] driver/operator/filesystem specifics and runbook steps before production action.

### Design question

### M05-U04-Q015 — Make a defensible design with explicit constraints, trade-offs, failure modes and validati

- **Unit/category:** Unit 4 / Design question
- **Level:** L4 Expert
- **Objective tested:** Make a defensible design with explicit constraints, trade-offs, failure modes and validation.
- **Estimated time:** 4–12 minutes
- **Question type:** Design question
- **Question prompt:** Design a three-replica StatefulSet lifecycle policy covering stable identity, per-replica claims, rollout, PDB/quorum, scale-down retention, backup and safe re-expansion.

State assumptions, compare at least two options, identify failure modes, define security/data-safety controls, and specify validation evidence.
- **Model answer:** Use volumeClaimTemplates and stable ordinal identity; confirm claim-retention behavior for installed version; assess readiness/replication/quorum before rollout or scale-down; set PDB consistent with availability needs; stage changes; verify each replica's data and backups. Stable identity is not replication.
- **Common wrong answers/misconceptions:**
- Optimizing only for availability or cost while ignoring data integrity/recovery.
- Treating Kubernetes object readiness as proof of application correctness.
- Claiming driver or topology capabilities without verifying the deployed implementation.
- **Scoring rubric:** 8 points: constraints/options (2), lifecycle/data safety (2), failure modes/recovery (2), validation and security/cost trade-offs (2). Safety-critical unsafe deletion/force-detach/fsck-on-mounted-volume caps score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, Unit 4; design is aligned to stated unit outcomes.
- **Version note:** [VERIFY] exact implementation/API/backend support before implementation.

## 9.7 Unit 5 — Running Databases and Brokers with Operators

### Conceptual short answer

### M05-U05-Q001 — operator reconciliation

- **Unit/category:** Unit 5 / Conceptual short answer
- **Level:** L1 Beginner
- **Objective tested:** operator reconciliation
- **Estimated time:** 4–12 minutes
- **Question type:** Conceptual short answer
- **Question prompt:** Explain how an operator differs from a one-time manifest applied to a database Pod.
- **Model answer:** An operator watches custom resources and reconciles desired state through controllers; its CRDs and behavior are version-specific. Editing generated resources directly may be reverted or conflict with reconciliation.
- **Common wrong answers/misconceptions:**
- Treating one Kubernetes object status as proof of end-to-end data health — object state covers only part of the lifecycle.
- Skipping the owner/data-safety check — destructive changes require confirmed ownership, references, and recoverability.
- Assuming identical behavior across all drivers and versions — verify implementation-specific support.
- **Scoring rubric:** 3 points: correct distinction (1), evidence/reasoning (1), safety/version caveat (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 5; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] where driver, filesystem, operator, or Kubernetes release affects the behavior.

### M05-U05-Q002 — database correctness

- **Unit/category:** Unit 5 / Conceptual short answer
- **Level:** L2 Intermediate
- **Objective tested:** database correctness
- **Estimated time:** 4–12 minutes
- **Question type:** Conceptual short answer
- **Question prompt:** Why are Kubernetes storage primitives insufficient to prove PostgreSQL data correctness?
- **Model answer:** PV/PVC state covers storage allocation/binding, not WAL recovery, replication, transaction consistency, backup validity, or application-level integrity. Use database/operator status, logs, backups and restore validation.
- **Common wrong answers/misconceptions:**
- Treating one Kubernetes object status as proof of end-to-end data health — object state covers only part of the lifecycle.
- Skipping the owner/data-safety check — destructive changes require confirmed ownership, references, and recoverability.
- Assuming identical behavior across all drivers and versions — verify implementation-specific support.
- **Scoring rubric:** 3 points: correct distinction (1), evidence/reasoning (1), safety/version caveat (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 5; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] where driver, filesystem, operator, or Kubernetes release affects the behavior.

### M05-U05-Q003 — broker operator scope

- **Unit/category:** Unit 5 / Conceptual short answer
- **Level:** L3 Advanced
- **Objective tested:** broker operator scope
- **Estimated time:** 4–12 minutes
- **Question type:** Conceptual short answer
- **Question prompt:** What is the correct assessment posture for a broker operator that the syllabus labels Awareness rather than mandatory hands-on?
- **Model answer:** Assess architecture, reconciliation, storage and operational trade-offs conceptually; do not require installation of a heavyweight broker stack unless the syllabus explicitly makes it optional. Keep lab resource constraints.
- **Common wrong answers/misconceptions:**
- Treating one Kubernetes object status as proof of end-to-end data health — object state covers only part of the lifecycle.
- Skipping the owner/data-safety check — destructive changes require confirmed ownership, references, and recoverability.
- Assuming identical behavior across all drivers and versions — verify implementation-specific support.
- **Scoring rubric:** 3 points: correct distinction (1), evidence/reasoning (1), safety/version caveat (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 5; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] where driver, filesystem, operator, or Kubernetes release affects the behavior.

### Multiple choice

### M05-U05-Q004 — Apply a core concept and reject plausible unsafe interpretations.

- **Unit/category:** Unit 5 / Multiple choice
- **Level:** L1 Beginner
- **Objective tested:** Apply a core concept and reject plausible unsafe interpretations.
- **Estimated time:** 4–12 minutes
- **Question type:** Multiple choice
- **Question prompt:** What is the primary role of a database operator?
- **Options:**
  - **A.** Replace the database's transaction engine
  - **B.** Reconcile a declared database state through controller logic
  - **C.** Guarantee that all PVCs are backed up
  - **D.** Make all custom resources version-independent
- **Model answer:** **Correct option: B.** Operators watch custom resources and reconcile desired state.

- **A:** The database engine remains responsible for transaction semantics.
- **B (correct):** Operators watch custom resources and reconcile desired state.
- **C:** Backup behavior must be explicitly configured and tested.
- **D:** CRD fields and behavior are version-specific.

- **Common wrong answers/misconceptions:**
- Choosing an option based on a status word without checking the described lifecycle.
- Assuming backend or application guarantees that the prompt does not establish.
- Taking a destructive action before confirming ownership and data safety.
- **Scoring rubric:** 1 point for the correct option; up to 2 additional points for explaining why it is correct and why each distractor fails.
- **Source/coverage note:** Parent M05 syllabus, Unit 5; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact driver/version behavior where noted.

### M05-U05-Q005 — Apply a core concept and reject plausible unsafe interpretations.

- **Unit/category:** Unit 5 / Multiple choice
- **Level:** L2 Intermediate
- **Objective tested:** Apply a core concept and reject plausible unsafe interpretations.
- **Estimated time:** 4–12 minutes
- **Question type:** Multiple choice
- **Question prompt:** Which evidence best validates a database restore?
- **Options:**
  - **A.** PVC is Bound only
  - **B.** Pod is Ready only
  - **C.** Restored database starts and application-level records/checksums and recovery point are validated
  - **D.** Snapshot object exists
- **Model answer:** **Correct option: C.** A restore test needs application/data verification, not just Kubernetes object status.

- **A:** Bound proves only binding.
- **B:** Ready is not proof of correct records or intended recovery point.
- **C (correct):** A restore test needs application/data verification, not just Kubernetes object status.
- **D:** Snapshot existence does not prove restore.

- **Common wrong answers/misconceptions:**
- Choosing an option based on a status word without checking the described lifecycle.
- Assuming backend or application guarantees that the prompt does not establish.
- Taking a destructive action before confirming ownership and data safety.
- **Scoring rubric:** 1 point for the correct option; up to 2 additional points for explaining why it is correct and why each distractor fails.
- **Source/coverage note:** Parent M05 syllabus, Unit 5; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact driver/version behavior where noted.

### M05-U05-Q006 — Apply a core concept and reject plausible unsafe interpretations.

- **Unit/category:** Unit 5 / Multiple choice
- **Level:** L2 Intermediate
- **Objective tested:** Apply a core concept and reject plausible unsafe interpretations.
- **Estimated time:** 4–12 minutes
- **Question type:** Multiple choice
- **Question prompt:** If Strimzi/Kafka is Awareness-only in the syllabus, what is appropriate?
- **Options:**
  - **A.** Require a full Kafka HA install in every laptop lab
  - **B.** Assess its architecture and trade-offs without making heavyweight installation mandatory
  - **C.** Invent a custom resource field to simplify the exercise
  - **D.** Assume a single broker is HA
- **Model answer:** **Correct option: B.** Assessment scope must follow the syllabus and laptop constraints.

- **A:** This violates scope and resource limits.
- **B (correct):** Assessment scope must follow the syllabus and laptop constraints.
- **C:** Invented fields are unsafe.
- **D:** A single broker is not a replicated HA deployment.

- **Common wrong answers/misconceptions:**
- Choosing an option based on a status word without checking the described lifecycle.
- Assuming backend or application guarantees that the prompt does not establish.
- Taking a destructive action before confirming ownership and data safety.
- **Scoring rubric:** 1 point for the correct option; up to 2 additional points for explaining why it is correct and why each distractor fails.
- **Source/coverage note:** Parent M05 syllabus, Unit 5; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact driver/version behavior where noted.

### Output interpretation

### M05-U05-Q010 — Interpret object/event/telemetry evidence and identify safe next checks.

- **Unit/category:** Unit 5 / Output interpretation
- **Level:** L2 Intermediate
- **Objective tested:** Interpret object/event/telemetry evidence and identify safe next checks.
- **Estimated time:** 4–12 minutes
- **Question type:** Output interpretation
- **Question prompt:** Operator custom resource is Ready but application-level restore validation has not been performed.

What does the evidence support, what does it not prove, which read-only checks come next, and what is the safest next action?

Illustrative / expected output (not executed here):
```text
CustomResource status: Ready
Restore test: NOT RUN
```
- **Model answer:** Ready is the operator's reported condition, not proof of backup correctness or restore success. Inspect operator status/logs, backup catalog and run an isolated restore with application-level checks.
- **Common wrong answers/misconceptions:**
- Treating the excerpt as proof of a single root cause without corroborating evidence.
- Deleting or patching storage objects before confirming ownership, references and data safety.
- Assuming driver/backend behavior is universal.
- **Scoring rubric:** 5 points: accurate interpretation (2), limitations/next checks (1), safe action (1), prevention or verification (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 5; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact event text/status semantics against the installed Kubernetes release and driver.

### M05-U05-Q011 — Interpret object/event/telemetry evidence and identify safe next checks.

- **Unit/category:** Unit 5 / Output interpretation
- **Level:** L3 Advanced
- **Objective tested:** Interpret object/event/telemetry evidence and identify safe next checks.
- **Estimated time:** 4–12 minutes
- **Question type:** Output interpretation
- **Question prompt:** A database Pod is Ready but replication lag/quorum evidence is absent.

What does the evidence support, what does it not prove, which read-only checks come next, and what is the safest next action?

Illustrative / expected output (not executed here):
```text
Pod/db-0 Ready: True
Replica health: unknown
Last restore verification: unknown
```
- **Model answer:** Pod readiness alone does not prove database quorum, replication freshness, or recoverability. Check database/operator status, replication/consistency indicators, backup evidence and documented failover policy.
- **Common wrong answers/misconceptions:**
- Treating the excerpt as proof of a single root cause without corroborating evidence.
- Deleting or patching storage objects before confirming ownership, references and data safety.
- Assuming driver/backend behavior is universal.
- **Scoring rubric:** 5 points: accurate interpretation (2), limitations/next checks (1), safe action (1), prevention or verification (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 5; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact event text/status semantics against the installed Kubernetes release and driver.

### Manifest review

### M05-U05-Q012 — Review storage manifests for lifecycle, capability, security, or data-loss defects.

- **Unit/category:** Unit 5 / Manifest review
- **Level:** L3 Advanced
- **Objective tested:** Review storage manifests for lifecycle, capability, security, or data-loss defects.
- **Estimated time:** 4–12 minutes
- **Question type:** Manifest review
- **Question prompt:** Review the following design: A PostgreSQL custom resource copies an unverified field from a blog; a single instance is labelled HA; backup success is inferred from a Ready status.

Illustrative snippet (not validated against a live cluster):
```yaml
apiVersion: database.example.invalid/v1
kind: DatabaseCluster
metadata: {name: pg}
spec:
  version: latest
  replicas: 1
  backup: {enabled: true}
# field names and backup semantics copied without checking operator docs
```
Find at least three substantive defects or dangerous omissions, provide a corrected design/patch strategy, and distinguish schema validation from runtime capability checks.
- **Model answer:** Defects:
1. Custom-resource fields are version-specific and must be checked in official CloudNativePG API docs.
2. A single instance does not establish HA/failover resilience.
3. Ready alone does not prove backup restore or data integrity.

Safe correction: Pin/verify operator version and CRD schema, design supported replica/failover topology, and execute a documented restore test with application-level verification. Do not invent fields.
- **Common wrong answers/misconceptions:**
- Fixing only YAML syntax while leaving lifecycle/data-safety defects.
- Assuming API acceptance proves driver/backend capability.
- Deleting existing storage before proving migration/restore and owner approval.
- **Scoring rubric:** 8 points: 1 per substantive defect up to 3; 2 for safe correction; 1 for data-loss/ownership analysis; 1 for schema-vs-runtime distinction; 1 for validation/verification plan.
- **Source/coverage note:** Parent M05 syllabus, Unit 5; snippets are assessment examples, not executed manifests.
- **Version note:** [VERIFY] validate fields, API versions, operator CRDs and driver capabilities against the installed versions.
- **Defects expected in a complete review:**
  1. Custom-resource fields are version-specific and must be checked in official CloudNativePG API docs.
  2. A single instance does not establish HA/failover resilience.
  3. Ready alone does not prove backup restore or data integrity.
- **Corrected design/patch strategy:** Pin/verify operator version and CRD schema, design supported replica/failover topology, and execute a documented restore test with application-level verification. Do not invent fields.

### M05-U05-Q013 — Review storage manifests for lifecycle, capability, security, or data-loss defects.

- **Unit/category:** Unit 5 / Manifest review
- **Level:** L3 Advanced
- **Objective tested:** Review storage manifests for lifecycle, capability, security, or data-loss defects.
- **Estimated time:** 4–12 minutes
- **Question type:** Manifest review
- **Question prompt:** Review the following design: A broker operator is required in every local lab despite a 4-core/8-GB budget; credentials are stored in plain text; operator-generated resources are manually patched.

Illustrative snippet (not validated against a live cluster):
```yaml
apiVersion: database.example.invalid/v1
kind: DatabaseCluster
metadata: {name: pg}
spec:
  version: latest
  replicas: 1
  backup: {enabled: true}
# field names and backup semantics copied without checking operator docs
```
Find at least three substantive defects or dangerous omissions, provide a corrected design/patch strategy, and distinguish schema validation from runtime capability checks.
- **Model answer:** Defects:
1. Heavyweight broker installation conflicts with stated resource constraints and Awareness scope.
2. Plain-text credentials violate secret hygiene.
3. Manual edits to reconciled resources may be reverted or conflict with the operator.

Safe correction: Keep broker operator Awareness-only unless explicitly optional; use fake credentials and supported Secret workflows; change desired custom resources or official configuration through the operator.
- **Common wrong answers/misconceptions:**
- Fixing only YAML syntax while leaving lifecycle/data-safety defects.
- Assuming API acceptance proves driver/backend capability.
- Deleting existing storage before proving migration/restore and owner approval.
- **Scoring rubric:** 8 points: 1 per substantive defect up to 3; 2 for safe correction; 1 for data-loss/ownership analysis; 1 for schema-vs-runtime distinction; 1 for validation/verification plan.
- **Source/coverage note:** Parent M05 syllabus, Unit 5; snippets are assessment examples, not executed manifests.
- **Version note:** [VERIFY] validate fields, API versions, operator CRDs and driver capabilities against the installed versions.
- **Defects expected in a complete review:**
  1. Heavyweight broker installation conflicts with stated resource constraints and Awareness scope.
  2. Plain-text credentials violate secret hygiene.
  3. Manual edits to reconciled resources may be reverted or conflict with the operator.
- **Corrected design/patch strategy:** Keep broker operator Awareness-only unless explicitly optional; use fake credentials and supported Secret workflows; change desired custom resources or official configuration through the operator.

### Incident/troubleshooting scenario

### M05-U05-Q014 — Use evidence-led troubleshooting and data-safety gates for a realistic storage incident.

- **Unit/category:** Unit 5 / Incident/troubleshooting scenario
- **Level:** L3 Advanced
- **Objective tested:** Use evidence-led troubleshooting and data-safety gates for a realistic storage incident.
- **Estimated time:** 4–12 minutes
- **Question type:** Incident/troubleshooting scenario
- **Question prompt:** A database operator reports Ready, but a restore drill has not been performed and a failover event occurred during node maintenance.

Give a ranked hypothesis, the first read-only checks, ownership/data-safety decision, safe mitigation/recovery, post-fix verification, prevention, and conditions that require stop-work/escalation.
- **Model answer:** Check operator CRD/version, status/events/logs, primary/replica health, replication lag, failover fencing, backups and restore evidence. Ready does not prove backup validity. Follow database-specific runbook and stop if consistency is unknown; verify records and recovery point after recovery. Do not assume one instance is HA.
- **Common wrong answers/misconceptions:**
- Jumping to deletion/finalizer removal/force-detach before evidence and data-safety checks.
- Treating one status or event as a complete root-cause proof.
- Skipping application-level verification after Kubernetes status recovers.
- **Scoring rubric:** 8 points: impact/evidence (2), ranked hypotheses (1), data-safety gate (1), safe recovery (2), verification (1), prevention/escalation (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 5; scenario synthesized from the explicit unit objectives.
- **Version note:** [VERIFY] driver/operator/filesystem specifics and runbook steps before production action.

### Design question

### M05-U05-Q015 — Make a defensible design with explicit constraints, trade-offs, failure modes and validati

- **Unit/category:** Unit 5 / Design question
- **Level:** L4 Expert
- **Objective tested:** Make a defensible design with explicit constraints, trade-offs, failure modes and validation.
- **Estimated time:** 4–12 minutes
- **Question type:** Design question
- **Question prompt:** Design a constrained local learning environment for PostgreSQL with CloudNativePG as the primary hands-on operator and broker operators Awareness-only unless optional. Include CRD/version verification, secrets, backup/restore, resource limits and runbooks.

State assumptions, compare at least two options, identify failure modes, define security/data-safety controls, and specify validation evidence.
- **Model answer:** Use official CloudNativePG documentation and verified API versions; pin images/versions per official instructions; use fake credentials and Secrets; avoid running all heavyweight stacks simultaneously; test operator status and database backup/restore; treat broker operators as Awareness-only unless optional lab is explicitly approved; document CPU/RAM/disk limits.
- **Common wrong answers/misconceptions:**
- Optimizing only for availability or cost while ignoring data integrity/recovery.
- Treating Kubernetes object readiness as proof of application correctness.
- Claiming driver or topology capabilities without verifying the deployed implementation.
- **Scoring rubric:** 8 points: constraints/options (2), lifecycle/data safety (2), failure modes/recovery (2), validation and security/cost trade-offs (2). Safety-critical unsafe deletion/force-detach/fsck-on-mounted-volume caps score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, Unit 5; design is aligned to stated unit outcomes.
- **Version note:** [VERIFY] exact implementation/API/backend support before implementation.

## 9.8 Unit 6 — Storage Performance: IOPS, Throughput, Latency

### Conceptual short answer

### M05-U06-Q001 — IOPS throughput latency

- **Unit/category:** Unit 6 / Conceptual short answer
- **Level:** L1 Beginner
- **Objective tested:** IOPS throughput latency
- **Estimated time:** 4–12 minutes
- **Question type:** Conceptual short answer
- **Question prompt:** Define IOPS, throughput, and latency, and explain why they are not interchangeable.
- **Model answer:** IOPS is operations per second; throughput is bytes per second; latency is time per operation, often analyzed at percentiles. Block size and workload mix affect relationships; one metric cannot substitute for the others.
- **Common wrong answers/misconceptions:**
- Treating one Kubernetes object status as proof of end-to-end data health — object state covers only part of the lifecycle.
- Skipping the owner/data-safety check — destructive changes require confirmed ownership, references, and recoverability.
- Assuming identical behavior across all drivers and versions — verify implementation-specific support.
- **Scoring rubric:** 3 points: correct distinction (1), evidence/reasoning (1), safety/version caveat (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 6; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] where driver, filesystem, operator, or Kubernetes release affects the behavior.

### M05-U06-Q002 — benchmark methodology

- **Unit/category:** Unit 6 / Conceptual short answer
- **Level:** L2 Intermediate
- **Objective tested:** benchmark methodology
- **Estimated time:** 4–12 minutes
- **Question type:** Conceptual short answer
- **Question prompt:** Why must a fio comparison control warm-up, steady state, workload profile, and repeated runs?
- **Model answer:** Cache, burst limits, noisy neighbors, queue depth, block size, and run-to-run variance can distort results. Compare equivalent profiles and report conditions rather than presenting one laptop run as a backend guarantee.
- **Common wrong answers/misconceptions:**
- Treating one Kubernetes object status as proof of end-to-end data health — object state covers only part of the lifecycle.
- Skipping the owner/data-safety check — destructive changes require confirmed ownership, references, and recoverability.
- Assuming identical behavior across all drivers and versions — verify implementation-specific support.
- **Scoring rubric:** 3 points: correct distinction (1), evidence/reasoning (1), safety/version caveat (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 6; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] where driver, filesystem, operator, or Kubernetes release affects the behavior.

### M05-U06-Q003 — tool limitations

- **Unit/category:** Unit 6 / Conceptual short answer
- **Level:** L3 Advanced
- **Objective tested:** tool limitations
- **Estimated time:** 4–12 minutes
- **Question type:** Conceptual short answer
- **Question prompt:** Why is kubectl top not a disk I/O measurement?
- **Model answer:** It primarily reports CPU/memory metrics from resource metrics APIs, not disk IOPS/latency. Use suitable OS/backend telemetry such as iostat/fio and correlate with application metrics; availability depends on environment.
- **Common wrong answers/misconceptions:**
- Treating one Kubernetes object status as proof of end-to-end data health — object state covers only part of the lifecycle.
- Skipping the owner/data-safety check — destructive changes require confirmed ownership, references, and recoverability.
- Assuming identical behavior across all drivers and versions — verify implementation-specific support.
- **Scoring rubric:** 3 points: correct distinction (1), evidence/reasoning (1), safety/version caveat (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 6; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] where driver, filesystem, operator, or Kubernetes release affects the behavior.

### Multiple choice

### M05-U06-Q004 — Apply a core concept and reject plausible unsafe interpretations.

- **Unit/category:** Unit 6 / Multiple choice
- **Level:** L1 Beginner
- **Objective tested:** Apply a core concept and reject plausible unsafe interpretations.
- **Estimated time:** 4–12 minutes
- **Question type:** Multiple choice
- **Question prompt:** A workload does 4 KiB random reads. Which measurement is most directly about operations per second?
- **Options:**
  - **A.** IOPS
  - **B.** Throughput in MiB/s only
  - **C.** CPU request
  - **D.** PVC access mode
- **Model answer:** **Correct option: A.** IOPS counts I/O operations per second.

- **A (correct):** IOPS counts I/O operations per second.
- **B:** Throughput is bytes/time, not operation count.
- **C:** CPU request is not storage performance.
- **D:** Access mode is not performance.

- **Common wrong answers/misconceptions:**
- Choosing an option based on a status word without checking the described lifecycle.
- Assuming backend or application guarantees that the prompt does not establish.
- Taking a destructive action before confirming ownership and data safety.
- **Scoring rubric:** 1 point for the correct option; up to 2 additional points for explaining why it is correct and why each distractor fails.
- **Source/coverage note:** Parent M05 syllabus, Unit 6; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact driver/version behavior where noted.

### M05-U06-Q005 — Apply a core concept and reject plausible unsafe interpretations.

- **Unit/category:** Unit 6 / Multiple choice
- **Level:** L2 Intermediate
- **Objective tested:** Apply a core concept and reject plausible unsafe interpretations.
- **Estimated time:** 4–12 minutes
- **Question type:** Multiple choice
- **Question prompt:** Why report latency percentiles in addition to averages?
- **Options:**
  - **A.** Percentiles reveal tail behavior that averages can hide
  - **B.** Percentiles guarantee causation
  - **C.** Averages are always invalid
  - **D.** Percentiles measure storage capacity
- **Model answer:** **Correct option: A.** Tail latency affects user experience and may be obscured by the mean.

- **A (correct):** Tail latency affects user experience and may be obscured by the mean.
- **B:** Percentiles describe distribution, not causation.
- **C:** Averages can be useful but insufficient alone.
- **D:** Latency distribution is not capacity.

- **Common wrong answers/misconceptions:**
- Choosing an option based on a status word without checking the described lifecycle.
- Assuming backend or application guarantees that the prompt does not establish.
- Taking a destructive action before confirming ownership and data safety.
- **Scoring rubric:** 1 point for the correct option; up to 2 additional points for explaining why it is correct and why each distractor fails.
- **Source/coverage note:** Parent M05 syllabus, Unit 6; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact driver/version behavior where noted.

### M05-U06-Q006 — Apply a core concept and reject plausible unsafe interpretations.

- **Unit/category:** Unit 6 / Multiple choice
- **Level:** L2 Intermediate
- **Objective tested:** Apply a core concept and reject plausible unsafe interpretations.
- **Estimated time:** 4–12 minutes
- **Question type:** Multiple choice
- **Question prompt:** Which tool is not a direct disk I/O metric source by itself?
- **Options:**
  - **A.** iostat
  - **B.** fio
  - **C.** kubectl top
  - **D.** Backend storage telemetry
- **Model answer:** **Correct option: C.** kubectl top primarily surfaces CPU/memory metrics, not disk IOPS/latency.

- **A:** iostat can report device I/O metrics where available.
- **B:** fio generates and measures workload profiles.
- **C (correct):** kubectl top primarily surfaces CPU/memory metrics, not disk IOPS/latency.
- **D:** Backend telemetry may report storage metrics.

- **Common wrong answers/misconceptions:**
- Choosing an option based on a status word without checking the described lifecycle.
- Assuming backend or application guarantees that the prompt does not establish.
- Taking a destructive action before confirming ownership and data safety.
- **Scoring rubric:** 1 point for the correct option; up to 2 additional points for explaining why it is correct and why each distractor fails.
- **Source/coverage note:** Parent M05 syllabus, Unit 6; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact driver/version behavior where noted.

### Output interpretation

### M05-U06-Q010 — Interpret object/event/telemetry evidence and identify safe next checks.

- **Unit/category:** Unit 6 / Output interpretation
- **Level:** L2 Intermediate
- **Objective tested:** Interpret object/event/telemetry evidence and identify safe next checks.
- **Estimated time:** 4–12 minutes
- **Question type:** Output interpretation
- **Question prompt:** fio reports high throughput but application latency is poor.

What does the evidence support, what does it not prove, which read-only checks come next, and what is the safest next action?

Illustrative / expected output (not executed here):
```text
fio: bw=180MiB/s, clat percentiles not included
Application p99 latency: elevated
```
- **Model answer:** Throughput alone cannot explain latency; profile, block size, queue depth, tail latency, cache, CPU throttling and application behavior matter. Rerun a comparable controlled workload and correlate OS/backend/application telemetry; no conclusion can be drawn from this excerpt's number alone.
- **Common wrong answers/misconceptions:**
- Treating the excerpt as proof of a single root cause without corroborating evidence.
- Deleting or patching storage objects before confirming ownership, references and data safety.
- Assuming driver/backend behavior is universal.
- **Scoring rubric:** 5 points: accurate interpretation (2), limitations/next checks (1), safe action (1), prevention or verification (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 6; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact event text/status semantics against the installed Kubernetes release and driver.

### M05-U06-Q011 — Interpret object/event/telemetry evidence and identify safe next checks.

- **Unit/category:** Unit 6 / Output interpretation
- **Level:** L3 Advanced
- **Objective tested:** Interpret object/event/telemetry evidence and identify safe next checks.
- **Estimated time:** 4–12 minutes
- **Question type:** Output interpretation
- **Question prompt:** Disk free bytes remain but writes fail.

What does the evidence support, what does it not prove, which read-only checks come next, and what is the safest next action?

Illustrative / expected output (not executed here):
```text
df -h /data: 30% used
df -i /data: 100% used
```
- **Model answer:** Inode exhaustion is a likely cause even though byte capacity remains. Confirm mount and filesystem, inspect small-file growth and retention, and use application-safe cleanup. Do not delete arbitrary files.
- **Common wrong answers/misconceptions:**
- Treating the excerpt as proof of a single root cause without corroborating evidence.
- Deleting or patching storage objects before confirming ownership, references and data safety.
- Assuming driver/backend behavior is universal.
- **Scoring rubric:** 5 points: accurate interpretation (2), limitations/next checks (1), safe action (1), prevention or verification (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 6; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact event text/status semantics against the installed Kubernetes release and driver.

### Manifest review

### M05-U06-Q012 — Review storage manifests for lifecycle, capability, security, or data-loss defects.

- **Unit/category:** Unit 6 / Manifest review
- **Level:** L3 Advanced
- **Objective tested:** Review storage manifests for lifecycle, capability, security, or data-loss defects.
- **Estimated time:** 4–12 minutes
- **Question type:** Manifest review
- **Question prompt:** Review the following design: A benchmark compares 4KiB random writes against 1MiB sequential reads and reports one throughput number; no warm-up or repeats are documented; CPU throttling is ignored.

Illustrative snippet (not validated against a live cluster):
```yaml
apiVersion: v1
kind: Pod
metadata: {name: fio-test}
spec:
  containers:
  - name: fio
    image: fio:latest
    command: ["fio", "--filename=/dev/unknown", "--rw=randwrite", "--bs=4k"]
# no size/runtime cap, target verification, warm-up, repeats or latency percentiles
```
Find at least three substantive defects or dangerous omissions, provide a corrected design/patch strategy, and distinguish schema validation from runtime capability checks.
- **Model answer:** Defects:
1. Workloads differ in block size and access pattern, so results are not comparable.
2. No warm-up/steady-state/repeated runs are documented.
3. CPU throttling and workload conditions can confound I/O interpretation.

Safe correction: Define equivalent fio profiles, record block size/read-write mix/queue depth/cache and run conditions, repeat runs, measure latency percentiles and correlate CPU/I/O telemetry. Do not generalize laptop numbers to cloud guarantees.
- **Common wrong answers/misconceptions:**
- Fixing only YAML syntax while leaving lifecycle/data-safety defects.
- Assuming API acceptance proves driver/backend capability.
- Deleting existing storage before proving migration/restore and owner approval.
- **Scoring rubric:** 8 points: 1 per substantive defect up to 3; 2 for safe correction; 1 for data-loss/ownership analysis; 1 for schema-vs-runtime distinction; 1 for validation/verification plan.
- **Source/coverage note:** Parent M05 syllabus, Unit 6; snippets are assessment examples, not executed manifests.
- **Version note:** [VERIFY] validate fields, API versions, operator CRDs and driver capabilities against the installed versions.
- **Defects expected in a complete review:**
  1. Workloads differ in block size and access pattern, so results are not comparable.
  2. No warm-up/steady-state/repeated runs are documented.
  3. CPU throttling and workload conditions can confound I/O interpretation.
- **Corrected design/patch strategy:** Define equivalent fio profiles, record block size/read-write mix/queue depth/cache and run conditions, repeat runs, measure latency percentiles and correlate CPU/I/O telemetry. Do not generalize laptop numbers to cloud guarantees.

### M05-U06-Q013 — Review storage manifests for lifecycle, capability, security, or data-loss defects.

- **Unit/category:** Unit 6 / Manifest review
- **Level:** L3 Advanced
- **Objective tested:** Review storage manifests for lifecycle, capability, security, or data-loss defects.
- **Estimated time:** 4–12 minutes
- **Question type:** Manifest review
- **Question prompt:** Review the following design: A run writes to an unknown mounted path; it assumes O_DIRECT always works; the output reports average latency only and no safety cap is set.

Illustrative snippet (not validated against a live cluster):
```yaml
apiVersion: v1
kind: Pod
metadata: {name: fio-test}
spec:
  containers:
  - name: fio
    image: fio:latest
    command: ["fio", "--filename=/dev/unknown", "--rw=randwrite", "--bs=4k"]
# no size/runtime cap, target verification, warm-up, repeats or latency percentiles
```
Find at least three substantive defects or dangerous omissions, provide a corrected design/patch strategy, and distinguish schema validation from runtime capability checks.
- **Model answer:** Defects:
1. Target path/device ownership and disposable status are not confirmed; writes can destroy data.
2. O_DIRECT support/semantics depend on platform/filesystem and tool options.
3. Average latency omits tail behavior; no workload/capacity safety limits are specified.

Safe correction: Use an explicitly disposable test file/volume, inspect fio help and filesystem support, set bounded size/runtime and verify target, report percentiles plus IOPS/throughput, and clean up only the test artifact.
- **Common wrong answers/misconceptions:**
- Fixing only YAML syntax while leaving lifecycle/data-safety defects.
- Assuming API acceptance proves driver/backend capability.
- Deleting existing storage before proving migration/restore and owner approval.
- **Scoring rubric:** 8 points: 1 per substantive defect up to 3; 2 for safe correction; 1 for data-loss/ownership analysis; 1 for schema-vs-runtime distinction; 1 for validation/verification plan.
- **Source/coverage note:** Parent M05 syllabus, Unit 6; snippets are assessment examples, not executed manifests.
- **Version note:** [VERIFY] validate fields, API versions, operator CRDs and driver capabilities against the installed versions.
- **Defects expected in a complete review:**
  1. Target path/device ownership and disposable status are not confirmed; writes can destroy data.
  2. O_DIRECT support/semantics depend on platform/filesystem and tool options.
  3. Average latency omits tail behavior; no workload/capacity safety limits are specified.
- **Corrected design/patch strategy:** Use an explicitly disposable test file/volume, inspect fio help and filesystem support, set bounded size/runtime and verify target, report percentiles plus IOPS/throughput, and clean up only the test artifact.

### Incident/troubleshooting scenario

### M05-U06-Q014 — Use evidence-led troubleshooting and data-safety gates for a realistic storage incident.

- **Unit/category:** Unit 6 / Incident/troubleshooting scenario
- **Level:** L3 Advanced
- **Objective tested:** Use evidence-led troubleshooting and data-safety gates for a realistic storage incident.
- **Estimated time:** 4–12 minutes
- **Question type:** Incident/troubleshooting scenario
- **Question prompt:** An application's p99 latency rises during a storage benchmark; fio throughput looks normal, and node CPU throttling increased.

Give a ranked hypothesis, the first read-only checks, ownership/data-safety decision, safe mitigation/recovery, post-fix verification, prevention, and conditions that require stop-work/escalation.
- **Model answer:** Control workload profile and compare repeated equivalent runs; inspect latency percentiles, block size/mix, queue depth, cache, iostat/backend telemetry, CPU throttling, I/O wait and application metrics. Throughput alone cannot explain tail latency. Reduce/stop unsafe benchmark load, preserve baseline and test separately; do not infer disk cause from CPU or vice versa.
- **Common wrong answers/misconceptions:**
- Jumping to deletion/finalizer removal/force-detach before evidence and data-safety checks.
- Treating one status or event as a complete root-cause proof.
- Skipping application-level verification after Kubernetes status recovers.
- **Scoring rubric:** 8 points: impact/evidence (2), ranked hypotheses (1), data-safety gate (1), safe recovery (2), verification (1), prevention/escalation (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 6; scenario synthesized from the explicit unit objectives.
- **Version note:** [VERIFY] driver/operator/filesystem specifics and runbook steps before production action.

### Design question

### M05-U06-Q015 — Make a defensible design with explicit constraints, trade-offs, failure modes and validati

- **Unit/category:** Unit 6 / Design question
- **Level:** L4 Expert
- **Objective tested:** Make a defensible design with explicit constraints, trade-offs, failure modes and validation.
- **Estimated time:** 4–12 minutes
- **Question type:** Design question
- **Question prompt:** Design a repeatable storage performance experiment that compares random 4KiB, sequential 1MiB, mixed 70/30 and fsync-heavy profiles without overstating laptop results.

State assumptions, compare at least two options, identify failure modes, define security/data-safety controls, and specify validation evidence.
- **Model answer:** Use isolated disposable target; specify profile/block size/read-write mix/queue depth/cache/direct-I/O semantics; bound runtime/size; warm up, reach steady state, repeat; report IOPS, throughput and latency percentiles; collect iostat/CPU throttling/I/O wait/backend metrics; disclose local-laptop limitations.
- **Common wrong answers/misconceptions:**
- Optimizing only for availability or cost while ignoring data integrity/recovery.
- Treating Kubernetes object readiness as proof of application correctness.
- Claiming driver or topology capabilities without verifying the deployed implementation.
- **Scoring rubric:** 8 points: constraints/options (2), lifecycle/data safety (2), failure modes/recovery (2), validation and security/cost trade-offs (2). Safety-critical unsafe deletion/force-detach/fsck-on-mounted-volume caps score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, Unit 6; design is aligned to stated unit outcomes.
- **Version note:** [VERIFY] exact implementation/API/backend support before implementation.

## 9.9 Unit 7 — Data Locality, Zonal Failure, Volume Affinity

### Conceptual short answer

### M05-U07-Q001 — topology and affinity

- **Unit/category:** Unit 7 / Conceptual short answer
- **Level:** L1 Beginner
- **Objective tested:** topology and affinity
- **Estimated time:** 4–12 minutes
- **Question type:** Conceptual short answer
- **Question prompt:** Explain the role of PV nodeAffinity and why removing it to schedule a Pod can be unsafe.
- **Model answer:** Affinity constrains placement to nodes compatible with the data's location. Removing it can misrepresent physical locality or attempt unsafe access; restore eligible capacity or use a supported recovery/replication plan.
- **Common wrong answers/misconceptions:**
- Treating one Kubernetes object status as proof of end-to-end data health — object state covers only part of the lifecycle.
- Skipping the owner/data-safety check — destructive changes require confirmed ownership, references, and recoverability.
- Assuming identical behavior across all drivers and versions — verify implementation-specific support.
- **Scoring rubric:** 3 points: correct distinction (1), evidence/reasoning (1), safety/version caveat (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 7; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] where driver, filesystem, operator, or Kubernetes release affects the behavior.

### M05-U07-Q002 — fake zones

- **Unit/category:** Unit 7 / Conceptual short answer
- **Level:** L2 Intermediate
- **Objective tested:** fake zones
- **Estimated time:** 4–12 minutes
- **Question type:** Conceptual short answer
- **Question prompt:** What can topology labels in kind teach, and what can they not demonstrate?
- **Model answer:** They can demonstrate scheduler constraint interactions. They do not create independent physical zones, network paths, disks, or real zone-failure resilience.
- **Common wrong answers/misconceptions:**
- Treating one Kubernetes object status as proof of end-to-end data health — object state covers only part of the lifecycle.
- Skipping the owner/data-safety check — destructive changes require confirmed ownership, references, and recoverability.
- Assuming identical behavior across all drivers and versions — verify implementation-specific support.
- **Scoring rubric:** 3 points: correct distinction (1), evidence/reasoning (1), safety/version caveat (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 7; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] where driver, filesystem, operator, or Kubernetes release affects the behavior.

### M05-U07-Q003 — replication and quorum

- **Unit/category:** Unit 7 / Conceptual short answer
- **Level:** L3 Advanced
- **Objective tested:** replication and quorum
- **Estimated time:** 4–12 minutes
- **Question type:** Conceptual short answer
- **Question prompt:** Explain why three replicas spread across zones do not guarantee a safe recovery plan by themselves.
- **Model answer:** Quorum depends on application protocol and failure model; synchronous/asynchronous replication trades latency against data-loss exposure. Verify replica health, fencing, topology, backups, and RPO/RTO.
- **Common wrong answers/misconceptions:**
- Treating one Kubernetes object status as proof of end-to-end data health — object state covers only part of the lifecycle.
- Skipping the owner/data-safety check — destructive changes require confirmed ownership, references, and recoverability.
- Assuming identical behavior across all drivers and versions — verify implementation-specific support.
- **Scoring rubric:** 3 points: correct distinction (1), evidence/reasoning (1), safety/version caveat (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 7; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] where driver, filesystem, operator, or Kubernetes release affects the behavior.

### Multiple choice

### M05-U07-Q004 — Apply a core concept and reject plausible unsafe interpretations.

- **Unit/category:** Unit 7 / Multiple choice
- **Level:** L1 Beginner
- **Objective tested:** Apply a core concept and reject plausible unsafe interpretations.
- **Estimated time:** 4–12 minutes
- **Question type:** Multiple choice
- **Question prompt:** A Pod has a volume node-affinity conflict. Safest first step?
- **Options:**
  - **A.** Remove PV nodeAffinity
  - **B.** Compare PV affinity, node labels, Pod constraints, StorageClass topology and events
  - **C.** Delete the PV
  - **D.** Assume fake kind zones are real
- **Model answer:** **Correct option: B.** The scheduler's constraints need evidence-based reconciliation.

- **A:** Removing affinity can misrepresent data locality.
- **B (correct):** The scheduler's constraints need evidence-based reconciliation.
- **C:** Deleting PV risks data loss and does not fix topology.
- **D:** kind labels simulate scheduling only.

- **Common wrong answers/misconceptions:**
- Choosing an option based on a status word without checking the described lifecycle.
- Assuming backend or application guarantees that the prompt does not establish.
- Taking a destructive action before confirming ownership and data safety.
- **Scoring rubric:** 1 point for the correct option; up to 2 additional points for explaining why it is correct and why each distractor fails.
- **Source/coverage note:** Parent M05 syllabus, Unit 7; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact driver/version behavior where noted.

### M05-U07-Q005 — Apply a core concept and reject plausible unsafe interpretations.

- **Unit/category:** Unit 7 / Multiple choice
- **Level:** L2 Intermediate
- **Objective tested:** Apply a core concept and reject plausible unsafe interpretations.
- **Estimated time:** 4–12 minutes
- **Question type:** Multiple choice
- **Question prompt:** What do fake zone labels in kind prove?
- **Options:**
  - **A.** Real independent-zone durability
  - **B.** Scheduler constraint behavior in a simulated topology
  - **C.** Provider-level failover time
  - **D.** Cross-zone replication consistency
- **Model answer:** **Correct option: B.** Labels can teach scheduling logic, not physical failure domains.

- **A:** No independent zones are created.
- **B (correct):** Labels can teach scheduling logic, not physical failure domains.
- **C:** No provider timing is measured.
- **D:** No real replication is created by labels.

- **Common wrong answers/misconceptions:**
- Choosing an option based on a status word without checking the described lifecycle.
- Assuming backend or application guarantees that the prompt does not establish.
- Taking a destructive action before confirming ownership and data safety.
- **Scoring rubric:** 1 point for the correct option; up to 2 additional points for explaining why it is correct and why each distractor fails.
- **Source/coverage note:** Parent M05 syllabus, Unit 7; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact driver/version behavior where noted.

### M05-U07-Q006 — Apply a core concept and reject plausible unsafe interpretations.

- **Unit/category:** Unit 7 / Multiple choice
- **Level:** L2 Intermediate
- **Objective tested:** Apply a core concept and reject plausible unsafe interpretations.
- **Estimated time:** 4–12 minutes
- **Question type:** Multiple choice
- **Question prompt:** What is required before force-detaching after node loss?
- **Options:**
  - **A.** A fixed universal timeout
  - **B.** Verify fencing/old-node state, backend attachment, driver procedure and application consistency
  - **C.** Delete the VolumeAttachment first
  - **D.** Assume asynchronous replication has zero data loss
- **Model answer:** **Correct option: B.** Force-detach risks concurrent writers or data inconsistency; follow the exact driver/provider runbook.

- **A:** No universal timeout is guaranteed.
- **B (correct):** Force-detach risks concurrent writers or data inconsistency; follow the exact driver/provider runbook.
- **C:** Manual deletion is not a universal safe detach.
- **D:** Asynchronous replication may lose acknowledged recent writes.

- **Common wrong answers/misconceptions:**
- Choosing an option based on a status word without checking the described lifecycle.
- Assuming backend or application guarantees that the prompt does not establish.
- Taking a destructive action before confirming ownership and data safety.
- **Scoring rubric:** 1 point for the correct option; up to 2 additional points for explaining why it is correct and why each distractor fails.
- **Source/coverage note:** Parent M05 syllabus, Unit 7; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact driver/version behavior where noted.

### Output interpretation

### M05-U07-Q010 — Interpret object/event/telemetry evidence and identify safe next checks.

- **Unit/category:** Unit 7 / Output interpretation
- **Level:** L2 Intermediate
- **Objective tested:** Interpret object/event/telemetry evidence and identify safe next checks.
- **Estimated time:** 4–12 minutes
- **Question type:** Output interpretation
- **Question prompt:** Pod is Pending with a volume node-affinity conflict.

What does the evidence support, what does it not prove, which read-only checks come next, and what is the safest next action?

Illustrative / expected output (not executed here):
```text
Warning FailedScheduling
0/3 nodes are available: volume node affinity conflict
```
- **Model answer:** Scheduling constraints are incompatible. Compare PV nodeAffinity, node labels, Pod constraints, allowedTopologies and binding mode. Do not remove affinity or claim fake zones are real infrastructure.
- **Common wrong answers/misconceptions:**
- Treating the excerpt as proof of a single root cause without corroborating evidence.
- Deleting or patching storage objects before confirming ownership, references and data safety.
- Assuming driver/backend behavior is universal.
- **Scoring rubric:** 5 points: accurate interpretation (2), limitations/next checks (1), safe action (1), prevention or verification (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 7; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact event text/status semantics against the installed Kubernetes release and driver.

### M05-U07-Q011 — Interpret object/event/telemetry evidence and identify safe next checks.

- **Unit/category:** Unit 7 / Output interpretation
- **Level:** L3 Advanced
- **Objective tested:** Interpret object/event/telemetry evidence and identify safe next checks.
- **Estimated time:** 4–12 minutes
- **Question type:** Output interpretation
- **Question prompt:** A kind cluster has nodes labelled zone-a and zone-b.

What does the evidence support, what does it not prove, which read-only checks come next, and what is the safest next action?

Illustrative / expected output (not executed here):
```text
NAME     topology.kubernetes.io/zone
worker   zone-a
worker2  zone-b
```
- **Model answer:** Labels can test scheduler rules only. They do not establish physical separation, independent failure domains, replicated storage, or real zonal recovery.
- **Common wrong answers/misconceptions:**
- Treating the excerpt as proof of a single root cause without corroborating evidence.
- Deleting or patching storage objects before confirming ownership, references and data safety.
- Assuming driver/backend behavior is universal.
- **Scoring rubric:** 5 points: accurate interpretation (2), limitations/next checks (1), safe action (1), prevention or verification (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 7; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact event text/status semantics against the installed Kubernetes release and driver.

### Manifest review

### M05-U07-Q012 — Review storage manifests for lifecycle, capability, security, or data-loss defects.

- **Unit/category:** Unit 7 / Manifest review
- **Level:** L3 Advanced
- **Objective tested:** Review storage manifests for lifecycle, capability, security, or data-loss defects.
- **Estimated time:** 4–12 minutes
- **Question type:** Manifest review
- **Question prompt:** Review the following design: A PV has nodeAffinity for worker-a; the workload has a required nodeSelector for worker-b; the proposed fix removes PV affinity.

Illustrative snippet (not validated against a live cluster):
```yaml
apiVersion: v1
kind: PersistentVolume
metadata: {name: data-pv}
spec:
  local: {path: /mnt/data}
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - {key: kubernetes.io/hostname, operator: In, values: [worker-a]}
# proposed fix: remove nodeAffinity to schedule on worker-b
```
Find at least three substantive defects or dangerous omissions, provide a corrected design/patch strategy, and distinguish schema validation from runtime capability checks.
- **Model answer:** Defects:
1. PV and Pod constraints conflict.
2. Removing affinity can misrepresent the physical data location.
3. The plan lacks verification of available compatible nodes and recovery/replica options.

Safe correction: Compare labels, PV affinity, topology and scheduling constraints; restore compatible capacity or use a supported replica/backup recovery. Do not rewrite locality to force scheduling.
- **Common wrong answers/misconceptions:**
- Fixing only YAML syntax while leaving lifecycle/data-safety defects.
- Assuming API acceptance proves driver/backend capability.
- Deleting existing storage before proving migration/restore and owner approval.
- **Scoring rubric:** 8 points: 1 per substantive defect up to 3; 2 for safe correction; 1 for data-loss/ownership analysis; 1 for schema-vs-runtime distinction; 1 for validation/verification plan.
- **Source/coverage note:** Parent M05 syllabus, Unit 7; snippets are assessment examples, not executed manifests.
- **Version note:** [VERIFY] validate fields, API versions, operator CRDs and driver capabilities against the installed versions.
- **Defects expected in a complete review:**
  1. PV and Pod constraints conflict.
  2. Removing affinity can misrepresent the physical data location.
  3. The plan lacks verification of available compatible nodes and recovery/replica options.
- **Corrected design/patch strategy:** Compare labels, PV affinity, topology and scheduling constraints; restore compatible capacity or use a supported replica/backup recovery. Do not rewrite locality to force scheduling.

### M05-U07-Q013 — Review storage manifests for lifecycle, capability, security, or data-loss defects.

- **Unit/category:** Unit 7 / Manifest review
- **Level:** L3 Advanced
- **Objective tested:** Review storage manifests for lifecycle, capability, security, or data-loss defects.
- **Estimated time:** 4–12 minutes
- **Question type:** Manifest review
- **Question prompt:** Review the following design: A design spreads Pods over fake kind zones and claims zone-level durability; one zonal disk backs all replicas; quorum and RPO are not documented.

Illustrative snippet (not validated against a live cluster):
```yaml
apiVersion: v1
kind: PersistentVolume
metadata: {name: data-pv}
spec:
  local: {path: /mnt/data}
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - {key: kubernetes.io/hostname, operator: In, values: [worker-a]}
# proposed fix: remove nodeAffinity to schedule on worker-b
```
Find at least three substantive defects or dangerous omissions, provide a corrected design/patch strategy, and distinguish schema validation from runtime capability checks.
- **Model answer:** Defects:
1. kind labels do not create independent zones.
2. A single zonal volume does not become replicated by spreading Pods.
3. Quorum, replication mode, backup and RPO/RTO are unspecified.

Safe correction: Label the lab as scheduler simulation only; design actual application replication and storage failure domains for production; document synchronous/asynchronous trade-offs and restore evidence.
- **Common wrong answers/misconceptions:**
- Fixing only YAML syntax while leaving lifecycle/data-safety defects.
- Assuming API acceptance proves driver/backend capability.
- Deleting existing storage before proving migration/restore and owner approval.
- **Scoring rubric:** 8 points: 1 per substantive defect up to 3; 2 for safe correction; 1 for data-loss/ownership analysis; 1 for schema-vs-runtime distinction; 1 for validation/verification plan.
- **Source/coverage note:** Parent M05 syllabus, Unit 7; snippets are assessment examples, not executed manifests.
- **Version note:** [VERIFY] validate fields, API versions, operator CRDs and driver capabilities against the installed versions.
- **Defects expected in a complete review:**
  1. kind labels do not create independent zones.
  2. A single zonal volume does not become replicated by spreading Pods.
  3. Quorum, replication mode, backup and RPO/RTO are unspecified.
- **Corrected design/patch strategy:** Label the lab as scheduler simulation only; design actual application replication and storage failure domains for production; document synchronous/asynchronous trade-offs and restore evidence.

### Incident/troubleshooting scenario

### M05-U07-Q014 — Use evidence-led troubleshooting and data-safety gates for a realistic storage incident.

- **Unit/category:** Unit 7 / Incident/troubleshooting scenario
- **Level:** L3 Advanced
- **Objective tested:** Use evidence-led troubleshooting and data-safety gates for a realistic storage incident.
- **Estimated time:** 4–12 minutes
- **Question type:** Incident/troubleshooting scenario
- **Question prompt:** After a node-pool replacement, a Pod cannot schedule because the PV node affinity names a hostname that no longer exists.

Give a ranked hypothesis, the first read-only checks, ownership/data-safety decision, safe mitigation/recovery, post-fix verification, prevention, and conditions that require stop-work/escalation.
- **Model answer:** Compare PV affinity, current node labels, Pod selectors/affinity, StorageClass topology and scheduler events. Verify whether data is local or zone-bound; restore compatible capacity or use a supported replica/backup recovery. Never remove affinity just to force scheduling. Confirm application data after recovery.
- **Common wrong answers/misconceptions:**
- Jumping to deletion/finalizer removal/force-detach before evidence and data-safety checks.
- Treating one status or event as a complete root-cause proof.
- Skipping application-level verification after Kubernetes status recovers.
- **Scoring rubric:** 8 points: impact/evidence (2), ranked hypotheses (1), data-safety gate (1), safe recovery (2), verification (1), prevention/escalation (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 7; scenario synthesized from the explicit unit objectives.
- **Version note:** [VERIFY] driver/operator/filesystem specifics and runbook steps before production action.

### Design question

### M05-U07-Q015 — Make a defensible design with explicit constraints, trade-offs, failure modes and validati

- **Unit/category:** Unit 7 / Design question
- **Level:** L4 Expert
- **Objective tested:** Make a defensible design with explicit constraints, trade-offs, failure modes and validation.
- **Estimated time:** 4–12 minutes
- **Question type:** Design question
- **Question prompt:** Design a stateful service across node/zone failure domains. Contrast local/zonal storage with replicated data, explain topology spread and quorum, and label what kind can and cannot validate.

State assumptions, compare at least two options, identify failure modes, define security/data-safety controls, and specify validation evidence.
- **Model answer:** Map PV affinity and actual failure domains; use WFFC/allowedTopologies where appropriate; distinguish Pod spread from data replication; reason about synchronous/asynchronous replication and 3-vs-5-member quorum under explicit failure assumptions; test recovery/backup and record RTO/RPO; kind zones only test scheduler constraints.
- **Common wrong answers/misconceptions:**
- Optimizing only for availability or cost while ignoring data integrity/recovery.
- Treating Kubernetes object readiness as proof of application correctness.
- Claiming driver or topology capabilities without verifying the deployed implementation.
- **Scoring rubric:** 8 points: constraints/options (2), lifecycle/data safety (2), failure modes/recovery (2), validation and security/cost trade-offs (2). Safety-critical unsafe deletion/force-detach/fsck-on-mounted-volume caps score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, Unit 7; design is aligned to stated unit outcomes.
- **Version note:** [VERIFY] exact implementation/API/backend support before implementation.

## 9.10 Unit 8 — Storage Troubleshooting and Orphaned Volumes

### Conceptual short answer

### M05-U08-Q001 — status diagnosis

- **Unit/category:** Unit 8 / Conceptual short answer
- **Level:** L1 Beginner
- **Objective tested:** status diagnosis
- **Estimated time:** 4–12 minutes
- **Question type:** Conceptual short answer
- **Question prompt:** Why is PV Released not proof that a backend disk is orphaned?
- **Model answer:** Retain may intentionally preserve a recovery asset; snapshots, restore jobs, operators, or backend ownership may still reference it. Reconcile owner, references, stable ID, retention policy, and data safety.
- **Common wrong answers/misconceptions:**
- Treating one Kubernetes object status as proof of end-to-end data health — object state covers only part of the lifecycle.
- Skipping the owner/data-safety check — destructive changes require confirmed ownership, references, and recoverability.
- Assuming identical behavior across all drivers and versions — verify implementation-specific support.
- **Scoring rubric:** 3 points: correct distinction (1), evidence/reasoning (1), safety/version caveat (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] where driver, filesystem, operator, or Kubernetes release affects the behavior.

### M05-U08-Q002 — finalizers

- **Unit/category:** Unit 8 / Conceptual short answer
- **Level:** L2 Intermediate
- **Objective tested:** finalizers
- **Estimated time:** 4–12 minutes
- **Question type:** Conceptual short answer
- **Question prompt:** Why is forcibly removing a PVC/PV finalizer a high-risk first response?
- **Model answer:** Finalizers coordinate protection or cleanup; bypassing them can remove Kubernetes tracking while backend cleanup/protection remains incomplete. Inspect references and restore the responsible controller or follow a reviewed recovery procedure.
- **Common wrong answers/misconceptions:**
- Treating one Kubernetes object status as proof of end-to-end data health — object state covers only part of the lifecycle.
- Skipping the owner/data-safety check — destructive changes require confirmed ownership, references, and recoverability.
- Assuming identical behavior across all drivers and versions — verify implementation-specific support.
- **Scoring rubric:** 3 points: correct distinction (1), evidence/reasoning (1), safety/version caveat (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] where driver, filesystem, operator, or Kubernetes release affects the behavior.

### M05-U08-Q003 — orphan definition

- **Unit/category:** Unit 8 / Conceptual short answer
- **Level:** L3 Advanced
- **Objective tested:** orphan definition
- **Estimated time:** 4–12 minutes
- **Question type:** Conceptual short answer
- **Question prompt:** Define a true orphan candidate and name the evidence required before deletion.
- **Model answer:** A candidate lacks an evident intended owner, but must be reconciled against Kubernetes objects, snapshots, attachments, operators, restore workflows, backend inventory, stable IDs and retention records. Unknown ownership means stop/quarantine, not delete.
- **Common wrong answers/misconceptions:**
- Treating one Kubernetes object status as proof of end-to-end data health — object state covers only part of the lifecycle.
- Skipping the owner/data-safety check — destructive changes require confirmed ownership, references, and recoverability.
- Assuming identical behavior across all drivers and versions — verify implementation-specific support.
- **Scoring rubric:** 3 points: correct distinction (1), evidence/reasoning (1), safety/version caveat (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] where driver, filesystem, operator, or Kubernetes release affects the behavior.

### Multiple choice

### M05-U08-Q004 — Apply a core concept and reject plausible unsafe interpretations.

- **Unit/category:** Unit 8 / Multiple choice
- **Level:** L1 Beginner
- **Objective tested:** Apply a core concept and reject plausible unsafe interpretations.
- **Estimated time:** 4–12 minutes
- **Question type:** Multiple choice
- **Question prompt:** A PV is Released with Retain. What should the operator do first?
- **Options:**
  - **A.** Delete it by age
  - **B.** Reconcile owner, claimRef, backend ID, snapshots/restore references and data-safety status
  - **C.** Patch all finalizers
  - **D.** Assume data is disposable
- **Model answer:** **Correct option: B.** Released/Retain may indicate intentionally preserved data; ownership and recoverability come first.

- **A:** Age is not proof of orphan status.
- **B (correct):** Released/Retain may indicate intentionally preserved data; ownership and recoverability come first.
- **C:** Finalizer removal is high risk.
- **D:** Disposability requires evidence/authorization.

- **Common wrong answers/misconceptions:**
- Choosing an option based on a status word without checking the described lifecycle.
- Assuming backend or application guarantees that the prompt does not establish.
- Taking a destructive action before confirming ownership and data safety.
- **Scoring rubric:** 1 point for the correct option; up to 2 additional points for explaining why it is correct and why each distractor fails.
- **Source/coverage note:** Parent M05 syllabus, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact driver/version behavior where noted.

### M05-U08-Q005 — Apply a core concept and reject plausible unsafe interpretations.

- **Unit/category:** Unit 8 / Multiple choice
- **Level:** L2 Intermediate
- **Objective tested:** Apply a core concept and reject plausible unsafe interpretations.
- **Estimated time:** 4–12 minutes
- **Question type:** Multiple choice
- **Question prompt:** What should a report-only orphan audit do when owner metadata is missing?
- **Options:**
  - **A.** Automatically delete the volume
  - **B.** Mark owner unknown and require investigation/quarantine
  - **C.** Guess the team from the PV name
  - **D.** Remove the backend disk
- **Model answer:** **Correct option: B.** Unknown ownership is uncertainty, not authorization to delete.

- **A:** Deletion without owner/recovery checks risks data loss.
- **B (correct):** Unknown ownership is uncertainty, not authorization to delete.
- **C:** Names are not authoritative ownership.
- **D:** Backend deletion is destructive.

- **Common wrong answers/misconceptions:**
- Choosing an option based on a status word without checking the described lifecycle.
- Assuming backend or application guarantees that the prompt does not establish.
- Taking a destructive action before confirming ownership and data safety.
- **Scoring rubric:** 1 point for the correct option; up to 2 additional points for explaining why it is correct and why each distractor fails.
- **Source/coverage note:** Parent M05 syllabus, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact driver/version behavior where noted.

### M05-U08-Q006 — Apply a core concept and reject plausible unsafe interpretations.

- **Unit/category:** Unit 8 / Multiple choice
- **Level:** L2 Intermediate
- **Objective tested:** Apply a core concept and reject plausible unsafe interpretations.
- **Estimated time:** 4–12 minutes
- **Question type:** Multiple choice
- **Question prompt:** Which is the safest filesystem repair rule?
- **Options:**
  - **A.** Run fsck on the mounted production filesystem
  - **B.** Run fsck only on an unmounted filesystem with a suitable backup/recovery plan
  - **C.** Remount read-write immediately after I/O errors
  - **D.** Delete kernel logs first
- **Model answer:** **Correct option: B.** Filesystem repair must follow a filesystem-specific procedure on an unmounted filesystem and with recovery protection.

- **A:** Mounted repair risks corruption.
- **B (correct):** Filesystem repair must follow a filesystem-specific procedure on an unmounted filesystem and with recovery protection.
- **C:** Blind remount can worsen damage.
- **D:** Logs are evidence to preserve.

- **Common wrong answers/misconceptions:**
- Choosing an option based on a status word without checking the described lifecycle.
- Assuming backend or application guarantees that the prompt does not establish.
- Taking a destructive action before confirming ownership and data safety.
- **Scoring rubric:** 1 point for the correct option; up to 2 additional points for explaining why it is correct and why each distractor fails.
- **Source/coverage note:** Parent M05 syllabus, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact driver/version behavior where noted.

### Output interpretation

### M05-U08-Q010 — Interpret object/event/telemetry evidence and identify safe next checks.

- **Unit/category:** Unit 8 / Output interpretation
- **Level:** L2 Intermediate
- **Objective tested:** Interpret object/event/telemetry evidence and identify safe next checks.
- **Estimated time:** 4–12 minutes
- **Question type:** Output interpretation
- **Question prompt:** PVC is Terminating and has pvc-protection while a Pod still references it.

What does the evidence support, what does it not prove, which read-only checks come next, and what is the safest next action?

Illustrative / expected output (not executed here):
```text
PVC data: Terminating
Finalizer: kubernetes.io/pvc-protection
Pod app-0 volume claimName: data
```
- **Model answer:** Protection may be working as intended. Inspect the owning workload and termination state; stop it through its controller/operator and let references clear. Do not patch the finalizer first.
- **Common wrong answers/misconceptions:**
- Treating the excerpt as proof of a single root cause without corroborating evidence.
- Deleting or patching storage objects before confirming ownership, references and data safety.
- Assuming driver/backend behavior is universal.
- **Scoring rubric:** 5 points: accurate interpretation (2), limitations/next checks (1), safe action (1), prevention or verification (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact event text/status semantics against the installed Kubernetes release and driver.

### M05-U08-Q011 — Interpret object/event/telemetry evidence and identify safe next checks.

- **Unit/category:** Unit 8 / Output interpretation
- **Level:** L3 Advanced
- **Objective tested:** Interpret object/event/telemetry evidence and identify safe next checks.
- **Estimated time:** 4–12 minutes
- **Question type:** Output interpretation
- **Question prompt:** PV phase Released; owner label UNKNOWN; backend inventory has not been checked.

What does the evidence support, what does it not prove, which read-only checks come next, and what is the safest next action?

Illustrative / expected output (not executed here):
```text
PV phase=Released reclaimPolicy=Retain owner=UNKNOWN backendLookup=NOT_RUN
```
- **Model answer:** This is an investigation/quarantine candidate, not a deletion decision. Identify owner, reconcile backend stable ID, snapshots/attachments/operators, and confirm tested recovery or disposability before approval.
- **Common wrong answers/misconceptions:**
- Treating the excerpt as proof of a single root cause without corroborating evidence.
- Deleting or patching storage objects before confirming ownership, references and data safety.
- Assuming driver/backend behavior is universal.
- **Scoring rubric:** 5 points: accurate interpretation (2), limitations/next checks (1), safe action (1), prevention or verification (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] exact event text/status semantics against the installed Kubernetes release and driver.

### Manifest review

### M05-U08-Q012 — Review storage manifests for lifecycle, capability, security, or data-loss defects.

- **Unit/category:** Unit 8 / Manifest review
- **Level:** L3 Advanced
- **Objective tested:** Review storage manifests for lifecycle, capability, security, or data-loss defects.
- **Estimated time:** 4–12 minutes
- **Question type:** Manifest review
- **Question prompt:** Review the following design: A cleanup job deletes all PVs older than 30 days if phase is Released; owner metadata is optional; it removes finalizers on timeout.

Illustrative snippet (not validated against a live cluster):
```yaml
apiVersion: batch/v1
kind: CronJob
metadata: {name: cleanup-old-pvs}
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: cleanup
            image: kubectl:latest
            command: ["sh", "-c", "delete every Released PV older than 30 days; remove finalizers on timeout"]
          restartPolicy: Never
```
Find at least three substantive defects or dangerous omissions, provide a corrected design/patch strategy, and distinguish schema validation from runtime capability checks.
- **Model answer:** Defects:
1. Age and Released phase do not prove orphan status or disposability.
2. Missing owner metadata should block deletion and trigger investigation.
3. Blind finalizer removal can bypass protection/cleanup and lose tracking.

Safe correction: Make the job report-only; reconcile stable IDs and all references; require owner, tested restore/disposable declaration, quarantine, wait/recheck, independent approval, and post-delete inventory.
- **Common wrong answers/misconceptions:**
- Fixing only YAML syntax while leaving lifecycle/data-safety defects.
- Assuming API acceptance proves driver/backend capability.
- Deleting existing storage before proving migration/restore and owner approval.
- **Scoring rubric:** 8 points: 1 per substantive defect up to 3; 2 for safe correction; 1 for data-loss/ownership analysis; 1 for schema-vs-runtime distinction; 1 for validation/verification plan.
- **Source/coverage note:** Parent M05 syllabus, Unit 8; snippets are assessment examples, not executed manifests.
- **Version note:** [VERIFY] validate fields, API versions, operator CRDs and driver capabilities against the installed versions.
- **Defects expected in a complete review:**
  1. Age and Released phase do not prove orphan status or disposability.
  2. Missing owner metadata should block deletion and trigger investigation.
  3. Blind finalizer removal can bypass protection/cleanup and lose tracking.
- **Corrected design/patch strategy:** Make the job report-only; reconcile stable IDs and all references; require owner, tested restore/disposable declaration, quarantine, wait/recheck, independent approval, and post-delete inventory.

### M05-U08-Q013 — Review storage manifests for lifecycle, capability, security, or data-loss defects.

- **Unit/category:** Unit 8 / Manifest review
- **Level:** L3 Advanced
- **Objective tested:** Review storage manifests for lifecycle, capability, security, or data-loss defects.
- **Estimated time:** 4–12 minutes
- **Question type:** Manifest review
- **Question prompt:** Review the following design: An operator sees a missing backend ID in a PV report and runs filesystem repair on the mounted path; no backup or incident record exists.

Illustrative snippet (not validated against a live cluster):
```yaml
apiVersion: batch/v1
kind: CronJob
metadata: {name: cleanup-old-pvs}
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: cleanup
            image: kubectl:latest
            command: ["sh", "-c", "delete every Released PV older than 30 days; remove finalizers on timeout"]
          restartPolicy: Never
```
Find at least three substantive defects or dangerous omissions, provide a corrected design/patch strategy, and distinguish schema validation from runtime capability checks.
- **Model answer:** Defects:
1. Missing ID is uncertainty, not proof of absence or orphan status.
2. Filesystem repair must not run on a mounted filesystem and needs a recovery plan.
3. No backup/data-safety assessment or evidence preservation was performed.

Safe correction: Stop mutations; preserve logs/metadata; identify backend/provisioner and owner; verify a restorable copy or escalate; use filesystem-specific procedure only on an unmounted target with recovery protection.
- **Common wrong answers/misconceptions:**
- Fixing only YAML syntax while leaving lifecycle/data-safety defects.
- Assuming API acceptance proves driver/backend capability.
- Deleting existing storage before proving migration/restore and owner approval.
- **Scoring rubric:** 8 points: 1 per substantive defect up to 3; 2 for safe correction; 1 for data-loss/ownership analysis; 1 for schema-vs-runtime distinction; 1 for validation/verification plan.
- **Source/coverage note:** Parent M05 syllabus, Unit 8; snippets are assessment examples, not executed manifests.
- **Version note:** [VERIFY] validate fields, API versions, operator CRDs and driver capabilities against the installed versions.
- **Defects expected in a complete review:**
  1. Missing ID is uncertainty, not proof of absence or orphan status.
  2. Filesystem repair must not run on a mounted filesystem and needs a recovery plan.
  3. No backup/data-safety assessment or evidence preservation was performed.
- **Corrected design/patch strategy:** Stop mutations; preserve logs/metadata; identify backend/provisioner and owner; verify a restorable copy or escalate; use filesystem-specific procedure only on an unmounted target with recovery protection.

### Incident/troubleshooting scenario

### M05-U08-Q014 — Use evidence-led troubleshooting and data-safety gates for a realistic storage incident.

- **Unit/category:** Unit 8 / Incident/troubleshooting scenario
- **Level:** L3 Advanced
- **Objective tested:** Use evidence-led troubleshooting and data-safety gates for a realistic storage incident.
- **Estimated time:** 4–12 minutes
- **Question type:** Incident/troubleshooting scenario
- **Question prompt:** A PV is Released with Retain, its owner label is missing, and a backend inventory query has not yet been run.

Give a ranked hypothesis, the first read-only checks, ownership/data-safety decision, safe mitigation/recovery, post-fix verification, prevention, and conditions that require stop-work/escalation.
- **Model answer:** Stop cleanup. Record PV UID, claimRef, reclaim policy, backend identifier and evidence; search Pods/PVCs/snapshots/restore jobs/attachments/operators and authoritative backend inventory. Confirm owner and a tested copy or explicit disposability; quarantine and wait/recheck; require approval for exact ID and verify after cleanup. Missing owner is not permission to delete.
- **Common wrong answers/misconceptions:**
- Jumping to deletion/finalizer removal/force-detach before evidence and data-safety checks.
- Treating one status or event as a complete root-cause proof.
- Skipping application-level verification after Kubernetes status recovers.
- **Scoring rubric:** 8 points: impact/evidence (2), ranked hypotheses (1), data-safety gate (1), safe recovery (2), verification (1), prevention/escalation (1).
- **Source/coverage note:** Parent M05 syllabus, Unit 8; scenario synthesized from the explicit unit objectives.
- **Version note:** [VERIFY] driver/operator/filesystem specifics and runbook steps before production action.

### Design question

### M05-U08-Q015 — Make a defensible design with explicit constraints, trade-offs, failure modes and validati

- **Unit/category:** Unit 8 / Design question
- **Level:** L4 Expert
- **Objective tested:** Make a defensible design with explicit constraints, trade-offs, failure modes and validation.
- **Estimated time:** 4–12 minutes
- **Question type:** Design question
- **Question prompt:** Design a report-only orphan management workflow from inventory through owner reconciliation, quarantine, recheck, approval and post-delete verification.

State assumptions, compare at least two options, identify failure modes, define security/data-safety controls, and specify validation evidence.
- **Model answer:** Collect Kubernetes and backend inventories by stable ID; resolve owners and all references; missing ownership blocks deletion; require tested restorable copy or formal disposable-data approval; quarantine with owner/deadline; wait/recheck; independent approval and exact target; verify backend and Kubernetes inventory/audit trail after deletion.
- **Common wrong answers/misconceptions:**
- Optimizing only for availability or cost while ignoring data integrity/recovery.
- Treating Kubernetes object readiness as proof of application correctness.
- Claiming driver or topology capabilities without verifying the deployed implementation.
- **Scoring rubric:** 8 points: constraints/options (2), lifecycle/data safety (2), failure modes/recovery (2), validation and security/cost trade-offs (2). Safety-critical unsafe deletion/force-detach/fsck-on-mounted-volume caps score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, Unit 8; design is aligned to stated unit outcomes.
- **Version note:** [VERIFY] exact implementation/API/backend support before implementation.

## 9.11 Cross-unit integration scenarios

These scenarios require interaction across units; a single-unit answer is insufficient because the operational decision depends on lifecycle, scheduling, application state, recovery, performance, or governance evidence in combination. Every scenario includes the relevant units and a scoring rubric.

### M05-XINT-001 — Integrate Unit 2, Unit 4, Unit 7: Binding mode, topology and StatefulSet scheduling.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L3 Advanced
- **Objective tested:** Integrate Unit 2, Unit 4, Unit 7: Binding mode, topology and StatefulSet scheduling.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 2, Unit 4, Unit 7
- **Question prompt:** **Integrated concepts:** Unit 2, Unit 4, Unit 7.

**Scenario:** A three-member StatefulSet uses a topology-constrained class with WFFC. Claims remain Pending; one node has the required labels but is tainted, and the Pod has no toleration.

**Task:** Explain the scheduler/binding interaction, checks and safe next step.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Inspect events, class binding mode/allowedTopologies, node labels/taints, Pod tolerations, PV affinity and resource constraints. WFFC waits for a schedulable consumer; fix the intended scheduling policy or eligible capacity, not PV affinity. Verify claim binding, placement and application data.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 2, Unit 4, Unit 7; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-002 — Integrate Unit 4, Unit 5, Unit 8: StatefulSet identity, operator reconciliation and retent

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L3 Advanced
- **Objective tested:** Integrate Unit 4, Unit 5, Unit 8: StatefulSet identity, operator reconciliation and retention.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 4, Unit 5, Unit 8
- **Question prompt:** **Integrated concepts:** Unit 4, Unit 5, Unit 8.

**Scenario:** After scale-down, an ordinal's PVC remains Bound and the operator has a restore workflow open. A cleanup report labels it old.

**Task:** Decide whether to delete, quarantine or recover, and justify.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Do not delete. Stable ordinal claims and operator workflows may preserve member data. Check operator status, claim-retention behavior, snapshots/restore jobs, owner and backend ID; quarantine only after recording owner and references. Follow operator recovery and verify membership/data.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 4, Unit 5, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-003 — Integrate Unit 3, Unit 5, Unit 8: Snapshot consistency, backup hierarchy and RPO/RTO.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L4 Expert
- **Objective tested:** Integrate Unit 3, Unit 5, Unit 8: Snapshot consistency, backup hierarchy and RPO/RTO.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 3, Unit 5, Unit 8
- **Question prompt:** **Integrated concepts:** Unit 3, Unit 5, Unit 8.

**Scenario:** A database snapshot reports readyToUse. The team has no independent backup and proposes marking the recovery objective met.

**Task:** Design the evidence needed to accept the recovery plan.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Readiness alone is insufficient. Confirm application-consistency procedure, retention, copy/failure-domain independence, restore to a separate target, database recovery point and record/checksum integrity. Measure restore time and data-loss window; document RPO/RTO results and gaps.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 3, Unit 5, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-004 — Integrate Unit 2, Unit 5, Unit 8: CSI controller outage and existing mounted workload.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L4 Expert
- **Objective tested:** Integrate Unit 2, Unit 5, Unit 8: CSI controller outage and existing mounted workload.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 2, Unit 5, Unit 8
- **Question prompt:** **Integrated concepts:** Unit 2, Unit 5, Unit 8.

**Scenario:** New PVC provisioning fails during a CSI controller outage; a database Pod with an existing mount remains Ready.

**Task:** Rank hypotheses and define safe investigation without assuming universal behavior.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Inspect controller/sidecar logs, PVC events, backend auth/capacity and rollout history. Existing mounted I/O may continue while new provisioning/attach/resize/snapshot operations fail, but behavior is driver/operation-specific [VERIFY]. Preserve data, restore controller via its owner runbook and test each operation separately.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 2, Unit 5, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-005 — Integrate Unit 1, Unit 8: Retain, deleted namespace and backend inventory.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L3 Advanced
- **Objective tested:** Integrate Unit 1, Unit 8: Retain, deleted namespace and backend inventory.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 1, Unit 8
- **Question prompt:** **Integrated concepts:** Unit 1, Unit 8.

**Scenario:** A namespace was deleted. A Retain PV remains Released and the backend still lists a disk with a matching handle.

**Task:** Provide a recovery-first sequence and explain when cleanup is allowed.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Match PV UID/claimRef and stable backend handle; find owner, snapshots, restore jobs and retention/backup records. Establish tested copy or explicit disposability, quarantine/wait/recheck, require exact-ID approval, then verify Kubernetes/backend inventory after any cleanup. Namespace deletion does not establish orphan status.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 1, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-006 — Integrate Unit 3, Unit 6, Unit 8: Expansion stuck, filesystem conditions and performance.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L3 Advanced
- **Objective tested:** Integrate Unit 3, Unit 6, Unit 8: Expansion stuck, filesystem conditions and performance.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 3, Unit 6, Unit 8
- **Question prompt:** **Integrated concepts:** Unit 3, Unit 6, Unit 8.

**Scenario:** PVC requested size increased, `FileSystemResizePending` remains, and the app reports slow writes.

**Task:** Separate capacity from performance and define checks.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Inspect class expansion policy, PVC conditions/events, CSI resizer/node logs and actual `df -h`/`df -i`; collect latency/throughput/queue and backend telemetry. Determine whether resize is incomplete, inode/byte capacity is exhausted, or I/O is saturated. Avoid recreation/shrink; follow driver procedure and verify app writes.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 3, Unit 6, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-007 — Integrate Unit 4, Unit 5, Unit 7, Unit 8: Multi-Attach, zone affinity and database failove

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L4 Expert
- **Objective tested:** Integrate Unit 4, Unit 5, Unit 7, Unit 8: Multi-Attach, zone affinity and database failover.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 4, Unit 5, Unit 7, Unit 8
- **Question prompt:** **Integrated concepts:** Unit 4, Unit 5, Unit 7, Unit 8.

**Scenario:** After a node failure, replacement database Pod reports Multi-Attach and its PV affinity points to the failed node's zone.

**Task:** Define the safe order of operations and stop conditions.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Establish old-node fencing and backend attachment state; inspect VolumeAttachment, driver logs, PV affinity, replica/quorum health and application consistency. Follow exact provider/driver detach/failover runbook; do not delete attachment or rewrite affinity blindly. If fencing or data role is unknown, stop/escalate; verify database data after recovery.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 4, Unit 5, Unit 7, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-008 — Integrate Unit 5, Unit 6, Unit 8: Disk full, WAL growth and latency.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L4 Expert
- **Objective tested:** Integrate Unit 5, Unit 6, Unit 8: Disk full, WAL growth and latency.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 5, Unit 6, Unit 8
- **Question prompt:** **Integrated concepts:** Unit 5, Unit 6, Unit 8.

**Scenario:** PostgreSQL writes fail; `df -h` is near full, WAL usage grows, and p99 latency has increased.

**Task:** Identify the evidence needed to distinguish cause and safe mitigation.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Check bytes and inodes, WAL/replication/archiving state, database logs, IOPS/latency/queue, backend capacity and recent workload changes. Do not delete WAL files manually. Use database-supported retention/archiving/capacity runbook, preserve consistency, verify writes/replication and monitor headroom.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 5, Unit 6, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-009 — Integrate Unit 1, Unit 4, Unit 5: fsGroup, non-root image and StatefulSet rollout.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L3 Advanced
- **Objective tested:** Integrate Unit 1, Unit 4, Unit 5: fsGroup, non-root image and StatefulSet rollout.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 1, Unit 4, Unit 5
- **Question prompt:** **Integrated concepts:** Unit 1, Unit 4, Unit 5.

**Scenario:** A new non-root database image fails to write after rollout; the old ordinal is healthy and the claim is reused.

**Task:** Design a rollback/diagnosis plan that avoids damaging existing data.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Pause rollout if safe; inspect UID/GID/mode, fsGroup/fsGroupChangePolicy, mount driver semantics and logs. Compare old/new image identity and test a disposable claim. Avoid recursive chown on production data; use supported permissions/security context and operator rollout procedure, then verify database recovery and records.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 1, Unit 4, Unit 5; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-010 — Integrate Unit 3, Unit 5: Snapshot restore and application integrity.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L3 Advanced
- **Objective tested:** Integrate Unit 3, Unit 5: Snapshot restore and application integrity.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 3, Unit 5
- **Question prompt:** **Integrated concepts:** Unit 3, Unit 5.

**Scenario:** A snapshot restore PVC becomes Bound and the Pod starts, but a business table's expected row count differs.

**Task:** What evidence determines whether restore succeeded?

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Kubernetes binding/startup are insufficient. Check snapshot source/time, database recovery logs, consistency procedure, transaction/WAL state, expected records/checksums and restore point. Preserve source snapshot, repeat restore only to a separate target under plan, and record RPO/RTO and root cause.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 3, Unit 5; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-011 — Integrate Unit 4, Unit 5, Unit 7: Local volume loss and replica quorum.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L4 Expert
- **Objective tested:** Integrate Unit 4, Unit 5, Unit 7: Local volume loss and replica quorum.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 4, Unit 5, Unit 7
- **Question prompt:** **Integrated concepts:** Unit 4, Unit 5, Unit 7.

**Scenario:** A node hosting one local PV is permanently lost; two database replicas remain on other nodes, but replica health is unknown.

**Task:** Decide how to recover and what local durability claim is valid.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Local PV data is tied to its node/path; kind does not create durable cloud storage. Inspect operator/database quorum, replica freshness, backups and PV affinity. Use application-supported failover/rebuild from a verified source, not a recreated empty claim. Verify membership and data, then redesign failure-domain/backup policy.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 4, Unit 5, Unit 7; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-012 — Integrate Unit 2, Unit 4, Unit 8: Orphan false positive: detached but owned.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L3 Advanced
- **Objective tested:** Integrate Unit 2, Unit 4, Unit 8: Orphan false positive: detached but owned.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 2, Unit 4, Unit 8
- **Question prompt:** **Integrated concepts:** Unit 2, Unit 4, Unit 8.

**Scenario:** An audit finds an unattached disk with no active Pod, but a Bound PV and a StatefulSet claim still reference it.

**Task:** Explain why detached is not orphan and the reconciliation required.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Attachment state is transient; PV/PVC and StatefulSet ownership remain. Reconcile stable backend ID, claimRef UID, operator/restore references and driver state. Report as owned/not orphan; do not delete. Alert on stale attachment only after driver/backend evidence.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 2, Unit 4, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-013 — Integrate Unit 1, Unit 8: Admission/RBAC deletion protection and break-glass.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L4 Expert
- **Objective tested:** Integrate Unit 1, Unit 8: Admission/RBAC deletion protection and break-glass.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 1, Unit 8
- **Question prompt:** **Integrated concepts:** Unit 1, Unit 8.

**Scenario:** Admission policy blocks deletion of a protected PVC during an urgent incident; the incident commander proposes granting cluster-admin to everyone.

**Task:** Design a safe exception workflow.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Keep least privilege; verify policy and owner, impact, backup/data status and references. Use a time-bound authorized break-glass identity with change/incident ID, independent reviewer, exact resource scope, audit trail and post-incident review. Do not bypass backend protections or broadly grant cluster-admin.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 1, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-014 — Integrate Unit 2, Unit 8: Failed provisioning and backend residue.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L3 Advanced
- **Objective tested:** Integrate Unit 2, Unit 8: Failed provisioning and backend residue.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 2, Unit 8
- **Question prompt:** **Integrated concepts:** Unit 2, Unit 8.

**Scenario:** Provisioning failed; Kubernetes has no bound PV, but backend inventory lists a recently created disk.

**Task:** Determine if the disk can be cleaned up.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Correlate provisioning operation/controller logs, stable backend ID, creation timestamp, retries and any PV/claim/snapshot references. Confirm no in-flight reconciliation or owner; quarantine and recheck after a defined period. Require disposable/restore safety and approved exact-ID deletion, then verify backend cleanup.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 2, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-015 — Integrate Unit 3, Unit 5, Unit 8: Operator restore and local test-driver limitations.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L4 Expert
- **Objective tested:** Integrate Unit 3, Unit 5, Unit 8: Operator restore and local test-driver limitations.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 3, Unit 5, Unit 8
- **Question prompt:** **Integrated concepts:** Unit 3, Unit 5, Unit 8.

**Scenario:** A CloudNativePG restore lab uses a local-path-style provisioner. The team assumes CSI snapshots and online expansion are available.

**Task:** Correct the plan and list verification gates.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Local-path-style provisioning does not imply CSI snapshot/expansion support. Check actual provisioner, CRDs/controllers, driver capabilities, operator version and documented restore procedure. Use supported database backup/restore where appropriate; test snapshot/resize only if installed capabilities support them. Keep the lab zero-budget and resource-bounded.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 3, Unit 5, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-016 — Integrate Unit 5, Unit 6: Storage SLO breach and CPU throttling vs I/O wait.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L3 Advanced
- **Objective tested:** Integrate Unit 5, Unit 6: Storage SLO breach and CPU throttling vs I/O wait.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 5, Unit 6
- **Question prompt:** **Integrated concepts:** Unit 5, Unit 6.

**Scenario:** Database p99 worsens during fio; iostat latency rises in one run, while CPU throttling also rises.

**Task:** Design an experiment to isolate contributors.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Stop or reduce competing load if customer impact exists. Compare repeated controlled fio profiles, workload size, block size, read/write mix, queue depth and latency percentiles; collect iostat, CPU throttling, I/O wait and application metrics. One run cannot prove causation; isolate variables and report laptop fidelity limits.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 5, Unit 6; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-017 — Integrate Unit 1, Unit 8: Released PV recovery and claimRef identity.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L4 Expert
- **Objective tested:** Integrate Unit 1, Unit 8: Released PV recovery and claimRef identity.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 1, Unit 8
- **Question prompt:** **Integrated concepts:** Unit 1, Unit 8.

**Scenario:** A Released PV has claimRef namespace/name but the current claim with that name has a different UID; backend handle still exists.

**Task:** Explain the risk and safe recovery sequence.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Names can be reused; compare claimRef UID, PV UID, backend stable ID and audit/owner records. Preserve PV YAML and data; confirm intended dataset and restore copy, test documented reclaim/rebind on disposable storage, then verify application data. Do not clear claimRef based on matching name alone.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 1, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-018 — Integrate Unit 1, Unit 2, Unit 3, Unit 4, Unit 5, Unit 6, Unit 7, Unit 8: Capstone archite

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L4 Expert
- **Objective tested:** Integrate Unit 1, Unit 2, Unit 3, Unit 4, Unit 5, Unit 6, Unit 7, Unit 8: Capstone architecture review.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 1, Unit 2, Unit 3, Unit 4, Unit 5, Unit 6, Unit 7, Unit 8
- **Question prompt:** **Integrated concepts:** Unit 1, Unit 2, Unit 3, Unit 4, Unit 5, Unit 6, Unit 7, Unit 8.

**Scenario:** Review a proposed stateful data platform using per-replica claims, a database operator, snapshots, performance tests and kind fake zones. The design claims production-grade zonal durability.

**Task:** Identify minimum evidence and corrections before approval.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Require actual storage/driver compatibility, per-replica identity, operator-supported database topology, tested backups/restores, performance methodology, topology/replication design and RPO/RTO evidence. Kind labels validate scheduler constraints only. Separate local learning fidelity from production guarantees; reject the durability claim until real failure domains and recovery are demonstrated.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 1, Unit 2, Unit 3, Unit 4, Unit 5, Unit 6, Unit 7, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-019 — Integrate Unit 1, Unit 8: Reclaim policy conflict between dev and production.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L3 Advanced
- **Objective tested:** Integrate Unit 1, Unit 8: Reclaim policy conflict between dev and production.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 1, Unit 8
- **Question prompt:** **Integrated concepts:** Unit 1, Unit 8.

**Scenario:** A shared StorageClass has Delete policy for all namespaces; a production team requires a retained recovery asset.

**Task:** Propose governance and migration without risking current data.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Inventory current claims/PVs/backend, classify data and owners, review class policy and driver behavior, then create a separately reviewed class/policy for future claims. Do not assume changing a class retroactively changes existing PV policy; verify actual PV fields and migration plan. Test backup/restore and document exceptions.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 1, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-020 — Integrate Unit 2, Unit 7: StorageClass topology and allowedTopologies.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L3 Advanced
- **Objective tested:** Integrate Unit 2, Unit 7: StorageClass topology and allowedTopologies.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 2, Unit 7
- **Question prompt:** **Integrated concepts:** Unit 2, Unit 7.

**Scenario:** A claim provisions in an unexpected location because the class topology and Pod scheduling constraints were not reviewed together.

**Task:** Explain diagnosis and preventive design.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Inspect class binding mode, allowedTopologies, node labels, Pod selectors/affinity/spread, PV affinity and events. Choose WFFC when consumer scheduling should inform provisioning if supported; validate actual driver behavior. Never infer real zone resilience from labels alone.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 2, Unit 7; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-021 — Integrate Unit 4, Unit 5, Unit 7: StatefulSet PDB versus storage recovery.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L3 Advanced
- **Objective tested:** Integrate Unit 4, Unit 5, Unit 7: StatefulSet PDB versus storage recovery.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 4, Unit 5, Unit 7
- **Question prompt:** **Integrated concepts:** Unit 4, Unit 5, Unit 7.

**Scenario:** A PDB prevents a voluntary disruption, but a zone-bound database volume is inaccessible after a zone loss.

**Task:** Explain what the PDB protects and what it does not.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** A PDB constrains certain voluntary disruptions; it does not replicate data, make a zonal disk accessible elsewhere, or replace recovery. Check operator/database quorum, replicas, PV topology and backup. Recover using supported replication/restore and test data consistency; design PDB with failure-domain plan.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 4, Unit 5, Unit 7; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-022 — Integrate Unit 1, Unit 4: SubPath and permissions during data migration.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L3 Advanced
- **Objective tested:** Integrate Unit 1, Unit 4: SubPath and permissions during data migration.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 1, Unit 4
- **Question prompt:** **Integrated concepts:** Unit 1, Unit 4.

**Scenario:** A migration Pod mounts a PVC through subPath and cannot see the expected files; it runs as non-root.

**Task:** Build a safe evidence-first diagnosis.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Inspect exact volumeMount/subPath, source path contents, ownership/mode, UID/GID/fsGroup behavior and driver/filesystem semantics. Verify source and target data before cutover; do not recursively change permissions or delete source. Test on a disposable copy and compare checksums/application reads.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 1, Unit 4; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-023 — Integrate Unit 3, Unit 8: Snapshot deletion policy and orphan snapshot content.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L4 Expert
- **Objective tested:** Integrate Unit 3, Unit 8: Snapshot deletion policy and orphan snapshot content.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 3, Unit 8
- **Question prompt:** **Integrated concepts:** Unit 3, Unit 8.

**Scenario:** VolumeSnapshot was deleted but VolumeSnapshotContent and backend snapshot remain with a Retain policy.

**Task:** Decide whether this is leakage, intentional retention, or unknown.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Check snapshot class deletion policy, content finalizers/status, backend ID, backup catalog, legal retention and restore dependencies. Missing user-facing object does not prove orphan. Assign owner, quarantine/recheck, verify a restorable independent copy or formal disposability, approve exact cleanup and reconcile inventories.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 3, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-024 — Integrate Unit 5, Unit 7: Quorum 3 vs 5 and synchronous/asynchronous replication.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L4 Expert
- **Objective tested:** Integrate Unit 5, Unit 7: Quorum 3 vs 5 and synchronous/asynchronous replication.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 5, Unit 7
- **Question prompt:** **Integrated concepts:** Unit 5, Unit 7.

**Scenario:** A design proposes three replicas across zones and says it can tolerate any two failures; replication is asynchronous.

**Task:** Correct the claim and identify trade-offs.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** A three-member majority typically requires two votes; two failed members leave no majority, and asynchronous replication can lose recent writes. Exact semantics depend on application protocol. Compare 3/5 members, failure assumptions, synchronous latency, async RPO, fencing and restore path; verify operator docs and test failure drills.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 5, Unit 7; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-025 — Integrate Unit 2, Unit 3, Unit 8: Controller outage, expansion and snapshot jobs.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L4 Expert
- **Objective tested:** Integrate Unit 2, Unit 3, Unit 8: Controller outage, expansion and snapshot jobs.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 2, Unit 3, Unit 8
- **Question prompt:** **Integrated concepts:** Unit 2, Unit 3, Unit 8.

**Scenario:** CSI controller/sidecars restart while resize and snapshot requests are pending; application Pods remain mounted.

**Task:** Prioritize checks and recovery without assuming operation outcomes.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Record PVC/snapshot conditions and events, controller/sidecar logs, driver version, backend state and node-plugin health. Existing mounts may continue, but pending operations can fail or retry in driver-specific ways [VERIFY]. Restore controller under runbook, avoid deleting requests blindly, verify resize/filesystem and restore-test snapshot.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 2, Unit 3, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-026 — Integrate Unit 1, Unit 2, Unit 6, Unit 8: Backend capacity vs PVC quota vs inode exhaustio

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L3 Advanced
- **Objective tested:** Integrate Unit 1, Unit 2, Unit 6, Unit 8: Backend capacity vs PVC quota vs inode exhaustion.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 1, Unit 2, Unit 6, Unit 8
- **Question prompt:** **Integrated concepts:** Unit 1, Unit 2, Unit 6, Unit 8.

**Scenario:** PVC is Bound, writes fail, namespace quota is near its limit, backend reports low capacity and filesystem inode use is 100%.

**Task:** Separate the overlapping constraints and choose safe mitigations.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Check namespace quota, requested/actual PV size, backend/thin capacity, `df -h`, `df -i`, deleted-open files and growth/retention. Multiple constraints can coexist. Use approved capacity/retention remediation; don't assume expanding a PVC fixes backend or inode exhaustion. Verify write recovery.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 1, Unit 2, Unit 6, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-027 — Integrate Unit 2, Unit 5, Unit 8: CSI Secret rotation and workload outage.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L4 Expert
- **Objective tested:** Integrate Unit 2, Unit 5, Unit 8: CSI Secret rotation and workload outage.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 2, Unit 5, Unit 8
- **Question prompt:** **Integrated concepts:** Unit 2, Unit 5, Unit 8.

**Scenario:** After secret rotation, new attaches fail but existing mounted database Pods remain Ready.

**Task:** Plan a least-privilege investigation and rollback.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Check secret reference names/namespaces without exposing values, rotation timeline, controller/node logs, backend auth/audit and driver procedure. Existing I/O vs new operations is driver-specific. Restore a valid credential through secret management, verify attach/mount and database health, and test future rotation; never paste secret data into logs.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 2, Unit 5, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-028 — Integrate Unit 1, Unit 6, Unit 7: Local NVMe vs network storage trade-offs.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L4 Expert
- **Objective tested:** Integrate Unit 1, Unit 6, Unit 7: Local NVMe vs network storage trade-offs.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 1, Unit 6, Unit 7
- **Question prompt:** **Integrated concepts:** Unit 1, Unit 6, Unit 7.

**Scenario:** A workload wants the lowest measured local latency but also claims node-loss durability and zone portability.

**Task:** Evaluate the conflict and propose an evidence-based design.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Local NVMe may offer different performance characteristics but ties data to node/failure domain unless application replication/backup exists; network storage has its own latency/throughput and failure characteristics. Measure workload-specific IOPS/latency, map failure domains, define replication and backup, and state costs/limits without invented benchmark numbers.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 1, Unit 6, Unit 7; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-029 — Integrate Unit 3, Unit 8: Backup retention, legal hold and orphan cleanup.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L4 Expert
- **Objective tested:** Integrate Unit 3, Unit 8: Backup retention, legal hold and orphan cleanup.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 3, Unit 8
- **Question prompt:** **Integrated concepts:** Unit 3, Unit 8.

**Scenario:** An old snapshot has no current workload reference but may be under a retention hold; a cleanup SLA is overdue.

**Task:** Define a safe governance response.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Check backup catalog, retention/legal hold, owner, restore dependency, backend stable ID and policy. Age is a review trigger, not deletion authority. Quarantine and escalate ownerless/held resources; obtain legal/data-owner approval, verify independent recovery copy and audit exact deletion only after hold is cleared.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 3, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-030 — Integrate Unit 4, Unit 5, Unit 7: PDB, rollout partition and database catch-up.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L4 Expert
- **Objective tested:** Integrate Unit 4, Unit 5, Unit 7: PDB, rollout partition and database catch-up.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 4, Unit 5, Unit 7
- **Question prompt:** **Integrated concepts:** Unit 4, Unit 5, Unit 7.

**Scenario:** A rolling update respects a PDB but restarts a replica before it has caught up; the cluster loses write quorum.

**Task:** Explain why Kubernetes-level protection was insufficient and design guardrails.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** PDB and readiness do not necessarily encode database replication freshness/quorum. Check operator-supported update strategy/partition, replica lag, quorum, failure-domain placement and app-level health gates. Pause rollout, follow database runbook, restore quorum safely, and add replication-aware preconditions/monitoring.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 4, Unit 5, Unit 7; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-031 — Integrate Unit 1, Unit 6: Performance benchmark on a memory-backed emptyDir.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L3 Advanced
- **Objective tested:** Integrate Unit 1, Unit 6: Performance benchmark on a memory-backed emptyDir.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 1, Unit 6
- **Question prompt:** **Integrated concepts:** Unit 1, Unit 6.

**Scenario:** A team benchmarks writes to memory-backed emptyDir and claims the PV backend meets the same latency target.

**Task:** Reject or qualify the inference.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Memory-backed emptyDir is memory/tmpfs-backed and has different resource accounting and persistence semantics from backend PV storage. Benchmark the actual target type with controlled profile, repeat runs, record cache and CPU effects, and report it as a different storage path. Do not infer PV performance or durability.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 1, Unit 6; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-032 — Integrate Unit 4, Unit 7: Topology spread ScheduleAnyway vs DoNotSchedule.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L3 Advanced
- **Objective tested:** Integrate Unit 4, Unit 7: Topology spread ScheduleAnyway vs DoNotSchedule.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 4, Unit 7
- **Question prompt:** **Integrated concepts:** Unit 4, Unit 7.

**Scenario:** A StatefulSet uses topology spread with ScheduleAnyway and the team expects strict replica separation.

**Task:** Explain the scheduling trade-off and storage interaction.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** ScheduleAnyway permits scheduling despite skew when constraints cannot be met; DoNotSchedule blocks placement when constraints fail. Check actual labels, eligible domains, PV affinity, Pod constraints, and application replica topology. Do not claim separation without inspecting placement; validate version/API and failure-domain mapping.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 4, Unit 7; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-033 — Integrate Unit 2, Unit 7, Unit 8: Stale attachment plus node is NotReady.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L4 Expert
- **Objective tested:** Integrate Unit 2, Unit 7, Unit 8: Stale attachment plus node is NotReady.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 2, Unit 7, Unit 8
- **Question prompt:** **Integrated concepts:** Unit 2, Unit 7, Unit 8.

**Scenario:** A VolumeAttachment references a NotReady node; the replacement Pod is blocked, and backend detach status is unknown.

**Task:** Write a safe escalation decision tree.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Preserve events/logs; verify node fencing/actual state, driver and backend attachment, PV affinity, and application role/consistency. Follow exact provider/driver runbook; no universal timeout or safe generic delete exists. Stop if old-node write possibility is unresolved; verify new mount and data after approved detach.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 2, Unit 7, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-034 — Integrate Unit 1, Unit 8: Owner metadata, TTL and audit report design.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L3 Advanced
- **Objective tested:** Integrate Unit 1, Unit 8: Owner metadata, TTL and audit report design.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 1, Unit 8
- **Question prompt:** **Integrated concepts:** Unit 1, Unit 8.

**Scenario:** Platform team wants to delete every PV lacking an owner label after 14 days.

**Task:** Design a safer control that reduces cost without data loss.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Missing owner should trigger report, quarantine and owner discovery, not deletion. Add required ownership metadata at creation, periodic stable-ID inventory joins, TTL as review signal, namespace retirement workflow, RBAC/admission controls, independent approval and audit trail. Require tested recovery/disposable declaration and post-delete reconciliation.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 1, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-035 — Integrate Unit 3, Unit 5, Unit 6: Database restore, WAL and recovery point.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L4 Expert
- **Objective tested:** Integrate Unit 3, Unit 5, Unit 6: Database restore, WAL and recovery point.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 3, Unit 5, Unit 6
- **Question prompt:** **Integrated concepts:** Unit 3, Unit 5, Unit 6.

**Scenario:** A restore completes quickly but is missing transactions acknowledged shortly before failure; benchmark showed high throughput.

**Task:** Diagnose the recovery-point gap and propose tests.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Throughput does not prove WAL/archive completeness or recovery point. Check backup type, WAL retention/archive status, consistency, snapshot timing and operator/database restore procedure. Compare restored transaction markers to expected recovery point; measure RPO and restore duration. Preserve source and revise backup validation/runbooks.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 3, Unit 5, Unit 6; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-036 — Integrate Unit 1, Unit 2: PVC selector, pre-binding and capacity governance.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L3 Advanced
- **Objective tested:** Integrate Unit 1, Unit 2: PVC selector, pre-binding and capacity governance.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 1, Unit 2
- **Question prompt:** **Integrated concepts:** Unit 1, Unit 2.

**Scenario:** A claim has a selector for `tier=gold`, requests 12Gi and class `gold`; an Available 20Gi PV has no matching label.

**Task:** Explain why it may not bind and safe fix.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Capacity alone is insufficient: selector, class, access mode and volumeMode must match; pre-binding has its own semantics. Inspect PV/PVC YAML and ownership. Add a reviewed label or create an intended matching PV only after checking backend data/ownership; do not re-label an owned volume to force binding.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 1, Unit 2; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-037 — Integrate Unit 2, Unit 6, Unit 7: Data-locality trade-off with regional/shared storage.

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L4 Expert
- **Objective tested:** Integrate Unit 2, Unit 6, Unit 7: Data-locality trade-off with regional/shared storage.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 2, Unit 6, Unit 7
- **Question prompt:** **Integrated concepts:** Unit 2, Unit 6, Unit 7.

**Scenario:** An architect compares a zonal block disk, a regional replicated disk and a shared filesystem but has only one laptop benchmark.

**Task:** Propose an honest decision method.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Compare documented failure domains, attachment/access semantics, latency/throughput profile, consistency, supported topology, cost and recovery behavior. A laptop benchmark cannot validate provider guarantees. Use official backend docs, workload-specific test plan and restore/failure drills; mark unknown provider behavior [VERIFY].
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 2, Unit 6, Unit 7; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

### M05-XINT-038 — Integrate Unit 1, Unit 2, Unit 3, Unit 4, Unit 5, Unit 6, Unit 7, Unit 8: End-to-end incid

- **Unit/category:** Cross-unit / Cross-unit integration scenario
- **Level:** L4 Expert
- **Objective tested:** Integrate Unit 1, Unit 2, Unit 3, Unit 4, Unit 5, Unit 6, Unit 7, Unit 8: End-to-end incident review and prevention.
- **Estimated time:** 4–12 minutes
- **Question type:** Cross-unit integration scenario
- **Units/concepts integrated:** Unit 1, Unit 2, Unit 3, Unit 4, Unit 5, Unit 6, Unit 7, Unit 8
- **Question prompt:** **Integrated concepts:** Unit 1, Unit 2, Unit 3, Unit 4, Unit 5, Unit 6, Unit 7, Unit 8.

**Scenario:** A namespace was deleted, a database failed to return, a retained PV and snapshot remain, and the team has only a successful Pod readiness event.

**Task:** Produce an incident handoff and prevention plan.

Explain why an isolated single-unit answer is insufficient and cite the evidence in this prompt.
- **Model answer:** Record timeline/impact, object UIDs/claimRefs/backend IDs, events/driver/operator logs, data-safety and last verified recovery point. Reconcile retained PV/snapshot/restore workflow and database consistency; do not delete or rebind blindly. Verify restore/application records, measure RTO/RPO, assign follow-ups for retirement workflow, inventory, backup drills and least-privilege deletion controls.
- **Common wrong answers/misconceptions:**
- Solving only the Kubernetes scheduling/object-status symptom without checking data integrity and application recovery.
- Assuming driver/backend/operator capabilities without checking the exact implementation.
- Taking destructive action before owner, references, recovery and approval are established.
- **Scoring rubric:** 8 points: integrated reasoning (2), evidence and uncertainty (2), safe decision/recovery (2), verification/prevention (2). Unsafe destructive advice caps the score at 2/8.
- **Source/coverage note:** Parent M05 syllabus, integrated units: Unit 1, Unit 2, Unit 3, Unit 4, Unit 5, Unit 6, Unit 7, Unit 8; lesson-level cross-check not independently confirmed.
- **Version note:** [VERIFY] any driver, operator, API-version, backend, filesystem or measured-performance behavior not established by the scenario.

## 9.12 Practical lab and capstone review questions

The following practical checks use the question bank above; they do not claim that any lab was executed. Run only on a disposable cluster and verify exact versions/capabilities.

### Practical review checklist

1. **Inventory without mutation:** capture `kubectl config current-context`, `kubectl get pv`, `kubectl get pvc -A`, `kubectl get storageclass`, `kubectl get volumeattachment`, and sorted events. Explain the scope of each object and redact sensitive identifiers before sharing.
2. **Binding and topology:** create a disposable claim and consumer only after confirming the provisioner/class actually exists. If using WFFC, explain what evidence would distinguish normal waiting from unschedulable consumer behavior.
3. **Snapshot/restore:** do not assume local-path supports snapshots. Verify CRDs, snapshot controller/class, CSI driver and sidecar compatibility first. If supported, restore to a separate claim and verify application-level data, not just `Bound`/`Ready`.
4. **StatefulSet lifecycle:** record ordinal/claim association and retention policy. Never delete a claim solely because an ordinal is absent.
5. **Performance:** run bounded tests against a disposable target only; document profile, warm-up, repetitions, latency percentiles, IOPS, throughput, CPU throttling, I/O wait and environment limitations.
6. **Orphan workflow:** run report-only inventory, resolve owner/backend ID, inspect references, quarantine and recheck. No automatic deletion is authorized by this checklist.
7. **Capstone review:** require storage/driver compatibility evidence, operator/database consistency, restore-tested backups, topology/failure-domain clarity, measured RPO/RTO, least privilege, and a post-incident/runbook plan.

### Practical question P-LAB-001 — Is the local environment sufficient?

- **Unit/category:** Practical lab / environment-fidelity review
- **Level:** L2 Intermediate
- **Objective tested:** Separate low-cost learning evidence from production storage guarantees.
- **Estimated time:** 8 minutes
- **Question type:** Practical reasoning
- **Question prompt:** You have 4 CPU cores, 8 GB RAM and 30 GB free disk on WSL2 Ubuntu. Propose a safe sequence for studying storage binding, StatefulSet claims, snapshots and database recovery without running every heavy component together.
- **Model answer:** Start with `kind` and one control plane/one worker; learn PV/PVC and scheduling first. Add a local database/operator only after checking resource requirements and official install/API versions. Snapshot/expansion exercises require a verified compatible driver and controller; do not assume local-path provides them. Stop competing heavy stacks, use fake credentials, record disk headroom, and label fake zones as scheduling simulation. Restore validation must check application data.
- **Common wrong answers/misconceptions:**
  - Running PostgreSQL HA, Kafka, MinIO, service mesh and observability simultaneously — conflicts with the stated laptop budget.
  - Assuming local-path has CSI snapshot/expansion support — capability must be verified.
  - Calling kind labels real zones — they do not create independent failure domains.
- **Scoring rubric:** 5 points: resource-aware sequencing (2), capability/version checks (1), safety/credentials (1), fidelity caveat (1).
- **Source/coverage note:** Uploaded assessment prompt, learner/resource constraints; parent syllabus opening material retrieved. Lesson-level coverage not independently confirmed.
- **Version note:** `[VERIFY]` exact kind, operator, CSI hostpath, CRD and sidecar versions before optional exercises.

### Practical question P-CAP-002 — Evidence required before capstone acceptance

- **Unit/category:** Capstone review / integrated acceptance
- **Level:** L4 Expert
- **Objective tested:** Validate an end-to-end stateful data platform using evidence rather than status-only claims.
- **Estimated time:** 12 minutes
- **Question type:** Design/review
- **Question prompt:** A capstone report says “all Pods Ready, snapshot readyToUse, and zones spread, therefore production-grade.” Identify the missing evidence and propose acceptance gates.
- **Model answer:** Require the actual storage driver/backend and supported capabilities; database/operator version and topology; verified backup/restore to a separate target; application-level records/checksums and recovery point; measured RTO/RPO; workload-representative performance measurements with percentiles and environment caveats; actual failure-domain mapping; quorum/replication evidence; least-privilege secrets/deletion controls; and reconciled PV/snapshot/backend inventory. Kind fake zones cannot establish real zonal resilience.
- **Common wrong answers/misconceptions:**
  - Pod readiness alone proves data integrity — it does not.
  - Snapshot readyToUse proves independent backup — it does not prove restore success or independence.
  - Spread labels prove zone durability — labels do not create real failure domains.
- **Scoring rubric:** 8 points: storage/driver evidence (1), application restore validation (2), RPO/RTO (1), topology/replication (1), performance method (1), security/governance (1), honest fidelity statement (1).
- **Source/coverage note:** Parent M05 syllabus objectives across Units 1–8 and capstone context from the uploaded prompt; capstone file itself was not inspected.
- **Version note:** `[VERIFY]` every operator/driver/backend capability and API before acceptance.

## 9.13 Answer-key navigation and remediation map

| If you missed… | Revisit these questions | Remediation target |
|---|---|---|
| Ephemeral vs persistent storage, binding, modes, permissions | M05-U01-Q001–Q015; M05-XINT-009, 022, 028 | Unit 1: lifecycle, access modes, security context and claim ownership |
| StorageClass, WFFC, CSI components and capability checks | M05-U02-Q001–Q015; M05-XINT-001, 004, 013, 019, 025, 030 | Unit 2: provisioning, controller/node roles, topology and credentials |
| Snapshot/restore/expansion and consistency | M05-U03-Q001–Q015; M05-XINT-003, 010, 014, 023, 024, 032 | Unit 3: snapshot API chain, restore validation, expansion stages and backup hierarchy |
| StatefulSet identity, retention, rollout and quorum | M05-U04-Q001–Q015; M05-XINT-002, 007, 009, 011, 021, 029, 031 | Unit 4: ordinal claims, lifecycle and safe updates |
| Operator reconciliation, database correctness and brokers | M05-U05-Q001–Q015; M05-XINT-002, 003, 007, 008, 010, 014, 024, 032 | Unit 5: operator/version semantics, database consistency and backup/restore |
| IOPS, throughput, latency, tools and benchmark validity | M05-U06-Q001–Q015; M05-XINT-006, 008, 015, 025, 026, 028, 032 | Unit 6: workload profiles, percentiles, cache and noisy-neighbor controls |
| Locality, zones, affinity, topology spread and quorum | M05-U07-Q001–Q015; M05-XINT-001, 007, 011, 016, 020, 021, 029, 030 | Unit 7: real vs simulated failure domains and recovery trade-offs |
| Troubleshooting, orphan discovery, finalizers and cleanup | M05-U08-Q001–Q015; M05-XINT-004–005, 012–014, 018, 023–024, 027, 031, 033–034 | Unit 8: evidence-first diagnosis, ownership reconciliation, quarantine and approved cleanup |
| Cross-unit reasoning / capstone | M05-XINT-001–038; P-CAP-002 | Integrate all Units 1–8 and document evidence, uncertainty, safety and recovery |

## 9.14 Coverage ledger and question count audit

### Count summary

- Unit-specific questions: **96** (12 per Unit 1–8).
- Cross-unit integration scenarios: **38**.
- Core bank total: **134** unique question IDs.
- Additional practical review prompts: 2 (`P-LAB-001`, `P-CAP-002`), listed separately and not required to reach the minimum.
- Minimum required: 130; reconciled total: **134 = 96 + 38**.
- IDs: unit IDs use unique unit namespaces; cross-unit IDs are sequential `M05-XINT-001`–`M05-XINT-038`. The unit question numbering is Q001–Q006 and Q010–Q015; Q007–Q009 are intentionally unused, so there are 12 questions per unit, not 15.
- No subparts are counted as separate questions.
- MCQs: 24, each with exactly four options and individually explained distractors.
- Manifest reviews: 16, each includes at least three defects/risks and a correction strategy.
- Output interpretations: 16, each uses illustrative, not-executed excerpts.
- Incident scenarios: 8, each includes evidence-led safe response and a rubric.
- Design questions: 8, each includes a rubric and trade-offs.

| Unit | Conceptual short answer | MCQ | Output interpretation | Manifest review | Incident | Design | Unit total |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 3 | 3 | 2 | 2 | 1 | 1 | 12 |
| 2 | 3 | 3 | 2 | 2 | 1 | 1 | 12 |
| 3 | 3 | 3 | 2 | 2 | 1 | 1 | 12 |
| 4 | 3 | 3 | 2 | 2 | 1 | 1 | 12 |
| 5 | 3 | 3 | 2 | 2 | 1 | 1 | 12 |
| 6 | 3 | 3 | 2 | 2 | 1 | 1 | 12 |
| 7 | 3 | 3 | 2 | 2 | 1 | 1 | 12 |
| 8 | 3 | 3 | 2 | 2 | 1 | 1 | 12 |
| **Global unit total** | **24** | **24** | **16** | **16** | **8** | **8** | **96** |

| Cross-unit integration | Count |
|---|---:|
| Unique cross-unit IDs | 38 |
| Total core bank | 134 |
| Minimum satisfied | YES, if IDs and categories above are retained |

### Traceability matrix

| Syllabus requirement | Question IDs | Unit/section | Evidence tested | Status | Gap/caveat |
|---|---|---|---|---|---|
| Ephemeral/container/Pod/persistent storage | M05-U01-Q001, Q012–Q015 | 9.3 | Lifecycle and manifest risks | PASS | Lesson-level check not done |
| Binding, capacity, access modes, volumeMode, selector/pre-binding | M05-U01-Q002–Q006, M05-XINT-033 | 9.3, 9.11 | Matching requirements and safe binding | PASS | Exact plugin semantics `[VERIFY]` |
| StorageClass, provisioning and reclaim policy | M05-U01-Q002–Q003, M05-U02-Q001–Q006, M05-XINT-019 | 9.3–9.5, 9.11 | Static/dynamic, Retain/Delete, class constraints | PASS | Deprecated Recycle not assessed beyond source note; `[VERIFY]` |
| Local volumes, hostPath, subPath/subPathExpr, emptyDir/memory accounting | M05-U01-Q001, Q012–Q013, M05-XINT-022, 028 | 9.3, 9.11 | Persistence and path/permission risks | PARTIAL | `subPathExpr` and memory-backed emptyDir accounting not separately deep-tested |
| fsGroup/runAsUser/non-root permissions | M05-U01-Q001, Q013–Q014, M05-XINT-009, 022 | 9.3, 9.11 | UID/GID/mode/driver caveats | PASS | Driver/version behavior `[VERIFY]` |
| PVC/PV protection/finalizers/Released recovery | M05-U01-Q006, M05-U08-Q001–Q003, Q010–Q015, M05-XINT-005, 017, 023, 033–034 | 9.3, 9.10, 9.11 | Protection, ownership, recovery and cleanup | PASS | Exact finalizer flow `[VERIFY]` |
| Quotas, capacity governance, encryption, etcd vs PV data | M05-U01-Q015, M05-U08-Q014, M05-XINT-026, 033 | 9.3, 9.10–9.11 | Quota/capacity and governance | PARTIAL | Encryption and etcd-vs-PV distinction are not independently deep-tested |
| CSI architecture, sidecars, secrets, compatibility and capabilities | M05-U02-Q001–Q006, Q010–Q015, M05-XINT-004, 013, 025, 027 | 9.4, 9.11 | Controller/node, class, auth and version checks | PASS | Exact driver matrix `[VERIFY]` |
| Immediate/WFFC, allowedTopologies, capacity awareness | M05-U02-Q005, Q010–Q015, M05-U07-Q010–Q015, M05-XINT-001, 019 | 9.4, 9.8, 9.11 | Scheduling and topology | PASS | Driver capacity feature `[VERIFY]` |
| Snapshot CRDs/content/class, readyToUse/deletion policy | M05-U03-Q001–Q006, Q010–Q015, M05-U08-Q014, M05-XINT-003, 010, 023 | 9.5, 9.10–9.11 | API chain, retention and readiness | PASS | Driver-specific behavior `[VERIFY]` |
| Clone, dataSource constraints, expansion stages and no shrink | M05-U03-Q001–Q006, Q012–Q015, M05-XINT-006, 014, 024 | 9.5, 9.11 | Restore/resize and migration safety | PASS | Exact API schema `[VERIFY]` |
| Crash/application consistency, PostgreSQL, backup hierarchy, RPO/RTO | M05-U03-Q001–Q003, M05-U05-Q001–Q015, M05-XINT-003, 010, 024, 032 | 9.5, 9.7, 9.11 | Restore tests and consistency | PASS | Operator/database procedure `[VERIFY]` |
| StatefulSet identity, claims, retention, rollout/PDB/quorum | M05-U04-Q001–Q015, M05-XINT-001–002, 009, 011, 021, 029, 031 | 9.6, 9.11 | Identity vs replication, rollout safety | PASS | Exact retention policy version `[VERIFY]` |
| CloudNativePG hands-on scope; brokers Awareness | M05-U05-Q001–Q015, M05-XINT-014, 027 | 9.7, 9.11 | Operator reconciliation, scope/resource limits | PASS | No live operator docs/runtime test |
| IOPS/throughput/latency, fio profiles and tools | M05-U06-Q001–Q015, M05-XINT-006, 008, 015, 026, 028, 032 | 9.8, 9.11 | Measurement and tool limits | PASS | Numeric performance results intentionally absent |
| Cache/O_DIRECT/fsync, noisy neighbours, CPU throttling, DiskPressure | M05-U06-Q001–Q015, M05-XINT-015, 026, 028 | 9.8, 9.11 | Benchmark design and confounders | PARTIAL | O_DIRECT/fsync profile details not separately tested in depth |
| Local vs network storage, topology, spread constraints, quorum | M05-U07-Q001–Q015, M05-XINT-001, 007, 011, 016, 020–021, 029–030 | 9.9, 9.11 | Affinity, simulated zones, replication trade-offs | PASS | Real cloud behavior `[VERIFY]` |
| Troubleshooting sequence, events, CSI logs, node diagnostics | M05-U08-Q001–Q015, M05-XINT-004, 006, 013, 025–027, 033–034 | 9.10, 9.11 | Read-only-first diagnosis | PASS | No live logs/commands |
| Orphan discovery, backend reconciliation, quarantine/approval | M05-U08-Q001–Q015, M05-XINT-005, 012–014, 023, 033–034 | 9.10–9.11 | Owner/reference/backend gate | PASS | Backend API-specific workflow `[VERIFY]` |
| kind/WSL2 budget, max three workers, no paid storage | P-LAB-001, P-CAP-002, M05-U07-Q005, M05-XINT-014, 018 | 9.12, 9.9, 9.11 | Resource-aware labs and fidelity caveats | PASS | Local machine not inspected |
| Source hygiene, no invented outputs, independent audit | All question IDs; 9.15–9.16 | Whole bank | Provenance, illustrative labels, gap disclosure | PASS | Lesson files not independently read in full |

## 9.15 Source and version verification notes

### Source hierarchy and availability

1. **Uploaded prompt:** `Pasted markdown(20261027-202150).md` — fully available in this turn and used for exact target, count distribution, schema, safety rules, section order, topic checklist and audit requirements.
2. **Parent M05 curriculum prompt:** `PROMPT-Kubernetes-Storage-and-Stateful-Data-Workloads.md` — found in the user's Library by content search; its opening material and unit ordering were retrieved. The full document was not inspected line-by-line during this task.
3. **Project tree:** exact file `Roadmap_ptree.md` was not found in the available search results. The M05 tree and file order reproduced in the uploaded prompt are used; no claim is made that the exact tree file was inspected.
4. **Unit lessons:** filenames are present in the Library, including Units 1–8, but their full contents were not independently inspected for this assessment. Lesson-level coverage remains not independently confirmed.
5. **Live official documentation:** no live version-specific documentation review or command execution was performed for this artifact. The register below names the appropriate authority and marks verification pending rather than claiming a live check.

### Compact source/claim register

| # | Claim/topic | Source authority | Verification status | Caveat |
|---:|---|---|---|---|
| 1 | PV/PVC binding, reclaim policy and protection | Kubernetes Persistent Volumes docs/API reference | Source/version verification pending | Reclaim and finalizer behavior can involve provisioner-specific cleanup |
| 2 | Access modes and volumeMode | Kubernetes PV/PVC API docs | Source/version verification pending | Access modes do not replace backend capability checks |
| 3 | ReadWriteOncePod | Kubernetes PV docs/API reference | `[VERIFY]` | Confirm release support and CSI compatibility |
| 4 | StorageClass and dynamic provisioning | Kubernetes StorageClass docs | Source/version verification pending | Provisioner and parameters are implementation-specific |
| 5 | Immediate vs WFFC | Kubernetes StorageClass docs | Source/version verification pending | Driver/scheduler/topology interactions vary |
| 6 | CSI controller/node plugin | CSI specification and official driver docs | Source/version verification pending | Exact operation placement differs by driver |
| 7 | CSI sidecar compatibility | Official CSI sidecar release/compatibility docs | `[VERIFY]` | Verify deployed versions together |
| 8 | Driver Secrets and least privilege | Kubernetes Secret docs and driver docs | Source/version verification pending | Do not expose secret values in evidence |
| 9 | VolumeSnapshot APIs/CRDs | Kubernetes Volume Snapshots docs | Source/version verification pending | Requires compatible CRDs/controller/driver support |
| 10 | Snapshot deletion policy | Kubernetes snapshot docs/API reference | `[VERIFY]` | Backend deletion/retention semantics must be checked |
| 11 | PVC dataSource/clone | Kubernetes API docs and driver docs | `[VERIFY]` | Supported source kinds/capabilities vary |
| 12 | Volume expansion and filesystem resize | Kubernetes PV/StorageClass docs and driver docs | `[VERIFY]` | Backend and node resize support differs |
| 13 | Crash vs application consistency | Database/operator backup documentation | `[VERIFY]` | Application quiescing/WAL semantics are workload-specific |
| 14 | StatefulSet identity and claim templates | Kubernetes StatefulSet docs | Source/version verification pending | Identity is not replication or backup |
| 15 | StatefulSet claim retention | Kubernetes StatefulSet docs | `[VERIFY]` | Version/policy-specific behavior |
| 16 | PDB and rollout interactions | Kubernetes disruption/StatefulSet docs | Source/version verification pending | PDB does not prove application quorum |
| 17 | CloudNativePG CRDs and restore | Official CloudNativePG docs | `[VERIFY]` | Exact API fields and restore procedure must match version |
| 18 | Strimzi/Kafka awareness | Official Strimzi docs | `[VERIFY]` | Awareness scope is curriculum-derived; no mandatory installation |
| 19 | fio profile semantics | Official fio documentation | Source/version verification pending | Exact flags/output schema should be checked before lab |
| 20 | iostat/iotop/pidstat | Official OS/tool documentation | Source/version verification pending | Tool availability and fields vary by platform |
| 21 | kubectl top scope | Kubernetes resource metrics docs | Source/version verification pending | Not a direct disk I/O telemetry source |
| 22 | CPU throttling/I/O wait interpretation | Linux kernel/OS and workload telemetry docs | `[VERIFY]` | Metrics must be correlated; neither alone proves root cause |
| 23 | PV nodeAffinity and topology | Kubernetes PV/scheduling docs | Source/version verification pending | Actual labels/failure domains must be verified |
| 24 | Topology spread constraints | Kubernetes Pod topology spread docs | `[VERIFY]` | API/version and eligible-domain behavior must be checked |
| 25 | kind multi-node and simulated zones | Official kind docs | Source/version verification pending | Labels do not create physical zone independence |
| 26 | Multi-Attach and VolumeAttachment | Kubernetes storage API and driver docs | `[VERIFY]` | No universal detach timeout or force-detach rule |
| 27 | PVC/PV orphan reconciliation | Kubernetes APIs plus actual backend inventory | `[VERIFY]` | Backend inventory is required; object status alone is insufficient |
| 28 | `fsGroup` and permission behavior | Kubernetes security context docs and driver docs | `[VERIFY]` | Driver/filesystem may handle ownership differently |
| 29 | Filesystem repair | Exact filesystem/kernel/vendor runbook | `[VERIFY]` | `fsck` only on an unmounted filesystem with a recovery plan |
| 30 | Admission/RBAC deletion controls | Kubernetes RBAC/admission docs and policy-engine docs | `[VERIFY]` | API versions and engine schemas differ |
| 31 | RTO/RPO | Organization service objectives and backup/DR runbooks | `[VERIFY]` | Targets require measured recovery evidence |
| 32 | Local-path snapshot/expansion support | Actual provisioner documentation | `[VERIFY]` | Do not infer CSI capabilities from local persistence |

## 9.16 Independent assessment audit

### 9.16.1 Count and uniqueness audit

| Check | Result | Evidence | Limitation |
|---|---|---|---|
| Total unique core questions ≥130 | PASS | Count ledger computes 134 IDs: 96 unit + 38 cross-unit | Additional two practical prompts are excluded from minimum |
| At least 12 per Unit 1–8 | PASS | Exactly 12 each | Unit ID gaps Q007–Q009 are intentionally unused |
| Per-unit category minima | PASS | Each unit has 3 short answer, 3 MCQ, 2 outputs, 2 manifest reviews, 1 incident, 1 design | Categories are explicit in metadata |
| Cross-unit count | PASS | M05-XINT-001–038 | Each lists two or more units |
| MCQs have four options | PASS | 24 MCQ objects each carry four options | Must preserve generated option blocks |
| Every MCQ distractor explained | PASS | Model answer explains each of A–D | Scoring explanation is qualitative |
| Manifest reviews have ≥3 defects | PASS | 16 manifest reviews have three explicit defect entries | Snippets are illustrative and not schema-validated |
| Incident/design rubric | PASS | Eight incidents and eight design questions each have explicit rubric | No operational execution |
| No double-counting | PASS | Ledger counts unit question objects once and cross-unit IDs separately | Practical prompts P-LAB-001/P-CAP-002 are outside core count |
| Sequential cross-unit IDs | PASS | M05-XINT-001–038 | Unit question IDs have intentional gaps |

### 9.16.2 Curriculum traceability audit

The traceability matrix maps each major Unit 1–8 requirement from the uploaded prompt to questions and evidence. **PASS** means the topic is substantively tested by this bank based on the prompt's syllabus checklist; it does not mean every unit lesson file was independently inspected. **PARTIAL** marks areas that appear only at introductory level and should be expanded if the actual parent syllabus requires deeper coverage. **VERIFY** marks implementation-sensitive claims.

Known partial areas: `subPathExpr` and memory-backed `emptyDir` accounting; encryption and etcd-snapshot-vs-PV distinction; detailed O_DIRECT/fsync profile flags. These are not hidden behind a PASS label.

### 9.16.3 Technical authenticity audit

- **Object scope and lifecycle:** question answers distinguish PVC, PV, StorageClass, VolumeAttachment and snapshot API scope at the conceptual level. Exact API fields are marked for verification where needed.
- **Manifest fields:** some snippets are deliberately defective; the Unit 2 provisioner and Unit 5 custom resource are explicit placeholders, not real installable manifests. They must not be applied.
- **Outputs/events:** all excerpts are labelled illustrative/not executed; no runtime success is claimed.
- **CSI/backend/operator behavior:** claims about mounted I/O during controller outages, snapshot support, resize, secrets, attachment and custom-resource fields are marked `[VERIFY]` where implementation-specific.
- **Data safety:** incident and cleanup answers require owner/reference/data-safety review before deletion; no question recommends blanket orphan deletion.
- **Snapshot/backup:** readiness is not treated as restore success; application-level validation and recovery point are required.
- **Performance:** no unsupported performance numbers are claimed; laptop results are not promoted to provider guarantees.
- **kind topology:** fake labels are consistently described as scheduler simulation, not real zones.
- **Version-specific behavior:** source register names authoritative docs but states that live verification is pending.

### 9.16.4 Editorial and learning-quality audit

- L1–L4 progression is used across the bank.
- Every core question has a unique ID, objective, time estimate, type, answer, misconceptions, rubric, source note and version note.
- MCQ distractors are individually explained; manifest reviews list defects and a safe correction strategy.
- Cross-unit prompts state integrated units and require evidence from the prompt.
- The remediation map points to the relevant unit and integration cases.
- The question count is not inflated by subparts or duplicate category counting.
- Remaining limitation: because lesson files were not inspected in full, lesson-specific terminology and exact syllabus detail are not independently confirmed. The bank is aligned to the explicit requirements in the uploaded assessment prompt and the retrieved parent curriculum opening.

### 9.16.5 Five operator misreadings the bank is designed to prevent

1. **“Bound means the database can safely write.”** Binding does not prove mount, permission, filesystem, capacity, or application correctness.
2. **“Released means orphan.”** Retain and other recovery workflows can intentionally preserve storage.
3. **“Snapshot ready means backup verified.”** Restore and application integrity tests are required.
4. **“Pod spreading means data durability across zones.”** Placement labels do not create replicated data or real failure domains.
5. **“A stale attachment/finalizer is safe to delete.”** Verify node fencing, backend state, references and exact driver procedure first.

### Remaining verification items

- Inspect the exact `Roadmap_ptree.md` or closest copy if available.
- Read the full parent syllabus and each Unit 1–8 lesson for line-by-line traceability.
- Verify current Kubernetes/CSI/operator/API versions and official source details.
- Validate intentionally defective YAML only as a review exercise; do not apply it.
- Run no live lab until the exact driver, class, snapshot controller, operator and backend capabilities are verified.
- Confirm the generated file's count/ID audit using a local script before repository adoption.

**Independent audit result:** structure/counts and coverage mapping are internally specified for 130 core questions. Source fidelity is limited by incomplete full-document retrieval of the parent syllabus, lack of direct `Roadmap_ptree.md` inspection, and no full lesson review. Runtime validation is not claimed.

## 9.17 Final output contract

This artifact contains only the M05 Unit 9 practice-question bank. It does not author the M05 syllabus, unit lessons, README, or capstone and does not modify repository files.

**Delivery status:** Markdown artifact generated; all question excerpts/manifests are illustrative and were not executed. The count and content audit should be rerun against the saved file before adopting it into the repository. Source/version verification remains pending for live Kubernetes, CSI, filesystem, operator and backend behavior.
