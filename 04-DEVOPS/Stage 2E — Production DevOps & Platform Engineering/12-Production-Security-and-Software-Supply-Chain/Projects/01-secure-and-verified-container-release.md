# Secure and Verified Container Release

> **A threat-model-driven, zero-budget capstone for a local data/ML
> delivery platform.**

  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Metadata                            Value
  ----------------------------------- -------------------------------------------------------------------------------------------------------------------------------------------------------------
  Stage                               Stage 2E --- Production DevOps & Platform Engineering

  Module                              M12 --- Production Security & Software Supply Chain

  Project                             Unit 14: Secure and Verified Container Release

  Intended destination                `Stage 2E — Production DevOps & Platform Engineering/12-Production-Security-and-Software-Supply-Chain/Projects/01-secure-and-verified-container-release.md`

  Estimated duration                  24--40 focused hours \[ILLUSTRATIVE\]; record actual time rather than treating this as a benchmark

  Lab budget                          Free/open-source tooling; approximately 4 CPU cores, 8 GB RAM, 30 GB disk

  Primary platform                    WSL2 Ubuntu; native Linux or a Linux VM is preferred for kernel-level runtime instrumentation

  Status                              DRAFT-AUDITED; human execution and version verification required

  Tool/specification baseline         Tool versions are not predeclared. Capture actual versions in `versions.txt`; see the verification register

  Safety                              Defensive-only; learner-owned disposable local lab; synthetic findings and dummy identities only
  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## Abstract

This workbook assembles the M12 learning units into a repeatable
release-control system for three harmless sample workloads: an inference
API, an ETL/batch job, and a notebook-style image. It guides the learner
from a threat model through hardened builds, risk-based vulnerability
triage, SBOM generation, isolated CI trust paths, signing and
provenance, admission policy, runtime controls, detection, remediation,
evidence, and incident response. The capstone is accepted only when
controls have positive and negative tests, saved evidence, ownership,
and explicit residual risk. A local lab can demonstrate mechanics and
policy logic; it cannot by itself prove production security, a hosted
trusted-builder guarantee, complete inventory, full kernel-level
detection, or regulatory compliance.

> **Evidence labels used throughout**
>
> -   **Executed evidence:** captured from a command actually run in the
>     learner's lab.
> -   **Representative expected result:** illustrative; it is not
>     claimed to have been observed.
> -   **\[SYNTHETIC\]:** invented training fixture, never a real
>     advisory or incident.
> -   **\[ASSUMPTION\]:** environmental premise awaiting confirmation.
> -   **\[ILLUSTRATIVE\]:** suggested value that must be chosen and
>     measured locally.
> -   **\[VERIFY\]:** version-sensitive detail that must be checked
>     against the selected version's official documentation.
> -   **NOT RUN / INCONCLUSIVE:** neither status is a pass.

## Table of contents

-   [1. Purpose, outcomes, and scope](#1-purpose-outcomes-and-scope)
-   [2. Scenario and architecture](#2-scenario-and-architecture)
-   [3. Threat model and control
    traceability](#3-threat-model-and-control-traceability)
-   [4. Prerequisites, resources, and
    feasibility](#4-prerequisites-resources-and-feasibility)
-   [5. Repository layout and evidence
    inventory](#5-repository-layout-and-evidence-inventory)
-   [6. Phase 0 --- Safe bootstrap and
    preflight](#6-phase-0--safe-bootstrap-and-preflight)
-   [7. Phase 1 --- Three hardened sample
    workloads](#7-phase-1--three-hardened-sample-workloads)
-   [8. Phase 2 --- Scan, triage, VEX, and
    exceptions](#8-phase-2--scan-triage-vex-and-exceptions)
-   [9. Phase 3 --- SBOM and component
    inventory](#9-phase-3--sbom-and-component-inventory)
-   [10. Phase 4 --- Separate untrusted and trusted build
    paths](#10-phase-4--separate-untrusted-and-trusted-build-paths)
-   [11. Phase 5 --- Signing, attestations, and
    provenance](#11-phase-5--signing-attestations-and-provenance)
-   [12. Phase 6 --- Admission and deployment
    enforcement](#12-phase-6--admission-and-deployment-enforcement)
-   [13. Phase 7 --- Runtime hardening and network
    boundaries](#13-phase-7--runtime-hardening-and-network-boundaries)
-   [14. Phase 8 --- Runtime detection and audit
    correlation](#14-phase-8--runtime-detection-and-audit-correlation)
-   [15. Phase 9 --- Findings, exceptions, and evidence
    lifecycle](#15-phase-9--findings-exceptions-and-evidence-lifecycle)
-   [16. Phase 10 --- Benign adversary-emulation
    suite](#16-phase-10--benign-adversary-emulation-suite)
-   [17. Incident exercise and blameless
    postmortem](#17-incident-exercise-and-blameless-postmortem)
-   [18. Make interface and
    guardrails](#18-make-interface-and-guardrails)
-   [19. Handoff documentation
    templates](#19-handoff-documentation-templates)
-   [20. Scoring and acceptance
    checklist](#20-scoring-and-acceptance-checklist)
-   [21. Troubleshooting](#21-troubleshooting)
-   [22. Cleanup and residual risk](#22-cleanup-and-residual-risk)
-   [23. Roadmap traceability matrix](#23-roadmap-traceability-matrix)
-   [24. References and verification
    register](#24-references-and-verification-register)
-   [25. Final independent audit
    report](#25-final-independent-audit-report)

------------------------------------------------------------------------

## 1. Purpose, outcomes, and scope

### 1.1 The engineering problem

A green build means only that the checks configured in that build
passed. It does not establish that the source was reviewed, the builder
was trustworthy, the image is the one tested, the artifact contains a
complete component inventory, the signer is authorized, admission
checked the intended identity, or the running workload has the intended
runtime controls.

This capstone connects those claims into an evidence chain:

1.  A documented threat model identifies the risks that matter.
2.  Source and dependencies are built through a defined path.
3.  The actual artifact is scanned and inventoried.
4.  The image is identified by digest, not just by a mutable tag.
5.  A trusted path signs the digest and attaches evidence.
6.  Verification checks signer trust, subject digest, provenance claims,
    and required attestations.
7.  Admission rejects invalid or unsafe workload declarations.
8.  Runtime restrictions reduce blast radius.
9.  Runtime and Kubernetes audit evidence support detection and
    response.
10. Findings, exceptions, incidents, and acceptance evidence have owners
    and lifecycle states.

### 1.2 Learning outcomes

At completion, the learner should be able to:

-   Explain the threat model and map each important threat to a control,
    positive test, negative test, evidence, owner, and residual risk.
-   Build three small images with distinct trust boundaries and hardened
    defaults.
-   Pin artifact identity by digest and document what is and is not
    reproducible.
-   Produce repeatable Trivy reports and triage synthetic findings using
    context rather than raw counts.
-   Generate SPDX and CycloneDX SBOMs for actual images, validate
    structure, associate each inventory with a digest, and query a
    synthetic advisory.
-   Separate untrusted validation from trusted release operations and
    test that the former cannot sign or promote.
-   Sign image digests with a disposable key, verify the intended public
    key, and reject wrong-key or wrong-digest cases.
-   Generate and verify a provenance statement using the chosen, checked
    predicate schema.
-   Test Kubernetes admission policy against valid, invalid, and
    bypass-shaped fixtures.
-   Apply non-root, read-only filesystem, capability, seccomp,
    token-mount, resource, and network restrictions.
-   Test runtime detection where supported and use clearly labeled
    fixtures where live Falco instrumentation is not available.
-   Run a benign incident drill, preserve evidence, contain, recover,
    and write a blameless postmortem.
-   State limitations without treating a laptop demonstration as a
    production guarantee.

### 1.3 In scope

-   Local sample applications and a local registry or local image store.
-   Trivy scanning, Syft SBOM generation, cosign key-based signing, and
    a SLSA-style provenance statement.
-   CI trust separation design and a local trust-boundary simulation.
-   Kubernetes manifests and policy examples for VAP, Kyverno, and
    Gatekeeper, exercised in sequence or as fixture tests.
-   Falco feasibility preflight, custom-rule catalog, fixture tests, and
    optional live runtime detection.
-   Risk register, exception lifecycle, evidence index, benign test
    scorecard, incident exercise, and cleanup verification.

### 1.4 Out of scope

-   Production credentials, customer data, real model weights, or real
    training data.
-   Testing third-party infrastructure or scanning targets without
    authorization.
-   Container escapes, exploitation payloads, malware, credential theft,
    or real exfiltration.
-   Paid SaaS security platforms, managed cloud services, HSM/KMS, or
    hosted SLSA L3 builders as pass prerequisites.
-   Claiming compliance certification or a SLSA level without satisfying
    the applicable requirements.
-   Replacing the full teaching content owned by M01--M12 or
    reimplementing M13--M16.

### 1.5 Ownership boundaries

  ------------------------------------------------------------------------
  Module                   Existing ownership      This capstone consumes
  ------------------------ ----------------------- -----------------------
  M01 --- Container image  Image construction,     Hardened image
  engineering and registry registry hygiene, base  patterns, digest
  hygiene                  images                  references, basic
                                                   Trivy/Syft familiarity

  M02 --- CI/CD pipeline   Pipeline fundamentals   Trust separation,
  engineering                                      permissions, release
                                                   gates

  M03/M04 --- Kubernetes   Cluster operations,     Deployment baseline and
  operations, networking   RBAC, PSS,              tests
  and security             NetworkPolicy           

  M06 ---                  Packaging and release   Rendered manifests or
  Helm/Kustomize/release   mechanics               packaging only where
  engineering                                      useful

  M07 --- IaC              Infrastructure          No cloud infrastructure
                           provisioning            required; reuse
                                                   patterns if present

  M08 --- GitOps           Declarative promotion   Promotion evidence; no
                           and reconciliation      routine manual
                                                   production `kubectl`
                                                   bypass

  M09 --- Secrets and      Workload identity,      Reuse concepts; do not
  identity                 short-lived identity,   re-teach the full
                           rotation                module

  M10 --- SRE and incident Incident roles and      Incident exercise and
  management               postmortems             handoff

  M11 --- Observability    Logs, metrics,          Optional local alert
                           dashboards, alerting    path and evidence
                                                   discipline

  M12 Units 1--12          Security controls and   Integrated end-to-end
                           detection               verification

  M13--M16                 Disaster recovery,      Forward handoffs only
                           multi-cluster           
                           operations, cost,       
                           golden paths            
  ------------------------------------------------------------------------

## 2. Scenario and architecture

### 2.1 Scenario

A data/ML team releases three workload types:

1.  **Inference API:** serves a harmless JSON response representing a
    model prediction.
2.  **ETL job:** reads a small local fixture and emits a summary; it
    does not connect to real data stores.
3.  **Notebook-style image:** represents a controlled development
    environment. It is not a production service and must not inherit
    production credentials, service accounts, network reach, or signing
    privileges.

The unsafe baseline uses mutable public tags, long-lived registry
passwords, inconsistent scanning, unsigned images, broad deployment
rights, root workloads, unnecessary service-account tokens, unrestricted
egress, and no reliable source-to-artifact record. A synthetic advisory
arrives and the team cannot identify affected deployed digests.

### 2.2 Target architecture

``` mermaid
flowchart LR
  Dev[Developer / reviewed source] --> PR[Untrusted validation path]
  PR -->|tests only; no signing rights| Report[Validation reports]
  Dev --> Review[Protected review / release authorization]
  Review --> Trusted[Trusted release path]
  Trusted --> Build[Isolated builder]
  Build --> Image[OCI image by digest]
  Build --> SBOM[SBOM + scan + test evidence]
  Build --> Prov[Provenance statement]
  Trusted --> Sign[Lab signing key / restricted signer]
  Image --> Sign
  Sign --> Registry[Local registry or local artifact store]
  SBOM --> Registry
  Prov --> Registry
  Registry --> Verify[Promotion verification]
  Verify --> GitOps[Reviewed deployment manifest]
  GitOps --> Admission[Kubernetes admission policy]
  Admission --> Runtime[Hardened workload]
  Runtime --> Detect[Falco / audit / fixture detections]
  Detect --> Incident[Incident workflow + evidence index]
  SBOM --> Inventory[Digest-indexed inventory]
  Inventory --> Incident
```

**Trust boundaries:** developer workstation; untrusted contribution
runner; protected source/release authorization; trusted builder/signing
path; artifact registry; deployment controller; Kubernetes
API/admission; workload runtime; evidence store. A boundary is
meaningful only if permissions, credentials, execution context, and
network reach differ across it.

### 2.3 Design principle: artifact identity is the join key

Use the immutable image digest to join build evidence, scan results,
SBOM, signature, provenance, admission decision, and running workload. A
tag such as `latest` is a mutable pointer. It can be useful as a
convenience label but is not a sufficient release identity.

Record at least: - repository and immutable source revision; - image
name and full digest; - builder identity/path; - scanner version and
database freshness state; - SBOM format and generator version; -
signature identity or public-key fingerprint; - provenance
predicate/schema version; - policy revision and decision; - deployment
namespace/workload and observed image digest; - evidence timestamp and
result status.

### 2.4 Success criteria

The capstone passes only when each required control has: 1. a declared
threat and control owner; 2. a positive test proving a valid release
remains usable; 3. a negative test proving a prohibited condition is
rejected or detected; 4. saved evidence with artifact digest and
tool/version context; 5. a result status (`PASS`, `FAIL`, `NOT RUN`, or
`INCONCLUSIVE`); 6. documented limitations and residual risk.

A configuration file existing on disk is not proof of enforcement. A
test that was skipped is not a pass. A scanner report with zero findings
is not proof that an artifact is safe.

## 3. Threat model and control traceability

### 3.1 Data-flow elements and trust boundaries

  ---------------------------------------------------------------------------------
  ID                Element / store /    Data handled        Trust boundary and
                    actor                                    primary concern
  ----------------- -------------------- ------------------- ----------------------
  E01               Developer            Source, local       Local compromise or
                    workstation          configuration       accidental secret
                                                             inclusion

  E02               Source repository    Code, lockfiles,    Unauthorized change or
                                         Dockerfiles, policy poisoned dependency

  E03               Untrusted PR runner  Unreviewed code and Must not access
                                         build context       release credentials or
                                                             signing capability

  E04               Protected release    Approved ref and    Bypass or mistaken
                    authorization        review decision     approval

  E05               Trusted builder      Build inputs, build Builder compromise,
                                         outputs             mutable tools,
                                                             cross-job
                                                             contamination

  E06               Dependency/package   Packages and        Dependency confusion,
                    sources              metadata            substitution,
                                                             unavailable metadata

  E07               Image registry       OCI manifests,      Mutable tag, artifact
                                         layers, signatures  substitution,
                                                             unauthorized overwrite

  E08               Scanner and          Image/filesystem,   Stale DB, false
                    vulnerability DB     advisory data       positives/negatives,
                                                             incomplete coverage

  E09               SBOM/inventory store Component metadata  Missing packages,
                                         and digests         stale inventory,
                                                             incorrect artifact
                                                             association

  E10               Signer/provenance    Digest, identity,   Key misuse, forged
                    generator            build claims        claims, wrong subject
                                                             digest

  E11               Promotion verifier   Signatures,         Overbroad trust rule
                                         attestations,       or failure to validate
                                         policy              claims

  E12               GitOps/deployment    Desired manifests   Manual bypass, stale
                    source               and digest          manifest, unauthorized
                                                             promotion

  E13               Kubernetes           Workload            Admission bypass,
                    API/admission        specifications      policy engine outage
                                                             or misconfiguration

  E14               Inference workload   Request data, model Unsafe model
                                         artifact            deserialization,
                                                             excessive privilege,
                                                             egress

  E15               ETL workload         Data fixture,       Data leakage,
                                         output              overbroad store
                                                             access, dependency
                                                             risk

  E16               Notebook workload    User code, analysis Interactive execution
                                         files               and data exposure;
                                                             separate trust tier

  E17               Model/data store     Model file,         Integrity,
                                         metadata,           confidentiality,
                                         training-data       provenance and access
                                         fixture             control

  E18               Runtime sensor/audit Process events, API Missing telemetry or
                    source               audit records       sensor tampering

  E19               Evidence/incident    Reports, logs,      Sensitive evidence
                    store                decision records    leakage, incomplete
                                                             chain of custody

  E20               Incident             Findings,           Delayed response,
                    responder/release    decisions, recovery unclear ownership,
                    owner                actions             premature closure
  ---------------------------------------------------------------------------------

### 3.2 STRIDE analysis

STRIDE categories are Spoofing, Tampering, Repudiation, Information
disclosure, Denial of service, and Elevation of privilege. They are a
brainstorming framework, not a probability model.

  ----------------------------------------------------------------------------
  Element / flow    Relevant STRIDE   Example risk      Main control and
                                                        evidence
  ----------------- ----------------- ----------------- ----------------------
  E01 → E02 source  Spoofing,         Unauthorized      Protected refs, review
  push              Tampering         commit or author  records, immutable
                                      identity assumed  commit ID
                                      from display name 

  E02 → E03         Tampering, EoP    Untrusted         No release
  untrusted runner                    workflow obtains  secret/permission in
                                      signing rights    PR path; negative
                                                        workflow audit

  E06 → E05         Tampering, DoS    Poisoned or       Lockfiles/hashes,
  dependency                          unavailable       controlled sources,
  resolution                          package           scan and dependency
                                                        review

  E05 → E07 image   Tampering,        Builder emits     Digest, signed
  publication       Repudiation       artifact without  provenance, protected
                                      traceable source  builder path

  E08 scan result → Repudiation, DoS  Stale DB falsely  Freshness check and
  release gate                        treated as        explicit offline
                                      current           status

  E09 SBOM →        Tampering,        SBOM associated   Digest binding,
  inventory         Information       with wrong digest validation, minimal
                    disclosure        or leaks          metadata
                                      sensitive paths   

  E10 signer → E11  Spoofing,         Wrong key or      Pinned trust
  verifier          Tampering         identity accepted key/identity,
                                                        wrong-key negative
                                                        test

  E11 → E13         EoP, DoS          Broad bypass      Scoped policy, bypass
  admission                           label or webhook  tests, failure-mode
                                      failure permits   plan
                                      unsafe pod        

  E12 → E13         Tampering,        Mutable tag       Digest-only release
  deployment        Repudiation       changes after     manifest and observed
                                      review            digest check

  E13 → E14/E15/E16 EoP, DoS          Privileged/root   Pod security baseline,
  runtime                             workload or token admission denials
                                      mount             

  E14 → E17 model   Information       Model substituted Model hash/identity
  store             disclosure,       or loaded from    check, access scope
                    Tampering         untrusted source  

  E15 → E17 data    Information       Batch job reads   Workload identity and
  store             disclosure        data beyond its   egress/authorization
                                      need              boundaries

  E16 → E17         Information       Interactive code  Separate namespace, no
                    disclosure, EoP   accesses          production identity,
                                      production data   egress restrictions
                                      or secrets        

  E18 → E19         Repudiation, DoS  Sensor stops but  Sensor
  telemetry                           no alerts arrive  heartbeat/health
                                                        check, fixture and
                                                        outage drill

  E20 incident      Repudiation, DoS  Evidence          Evidence preservation,
  handling                            destroyed or      incident log, assigned
                                      containment       roles
                                      delayed           
  ----------------------------------------------------------------------------

### 3.3 Qualitative risk criteria

Use qualitative categories; do not invent numerical probabilities.

-   **Likelihood --- Low:** requires multiple independent failures and
    is not exposed through routine paths; **Medium:** plausible under
    normal development or operational conditions; **High:** readily
    reachable, common misconfiguration, or exposed to untrusted input.
-   **Impact --- Low:** limited local disruption without sensitive data
    or release impact; **Medium:** workload interruption or bounded data
    exposure; **High:** release integrity, sensitive data/model
    exposure, or broad service impact; **Critical:** credible
    cross-boundary compromise or high-consequence
    data/model/control-plane impact.
-   **Priority:** combine likelihood, impact, exposure, exploitability
    evidence, fix availability, asset criticality, and compensating
    controls. This is a decision aid, not a mathematically calibrated
    score.

### 3.4 Risk register starter

Save as `threat-model/risk-register.csv`. The records below are
\[ILLUSTRATIVE\] and must be reviewed by a named owner.

``` csv
risk_id,threat,likelihood,impact,priority,owner,mitigation,positive_test,negative_test,evidence,decision,review_date,residual_risk
R-001,Untrusted PR reaches signer,High,High,Immediate,Release owner,Separate workflow permissions and isolated runner,Trusted ref can sign,PR path cannot sign,ci/tests/ plus evidence/signatures/,Mitigate,YYYY-MM-DD,Hosted provider isolation remains unproven locally
R-002,Mutable image tag promoted,Medium,High,High,Platform owner,Require digest in release manifest,Approved digest accepted,Tag-only manifest denied,evidence/admission/,Mitigate,YYYY-MM-DD,Registry overwrite controls require external review
R-003,Incomplete component inventory,Medium,High,High,Security owner,SBOM quality checks and known fixture query,Known package found,Unknown/missing subject rejected,evidence/sbom/,Mitigate,YYYY-MM-DD,Static/vendored/model content may remain invisible
R-004,Notebook accesses production data,Medium,Critical,High,Data owner,Separate identity/namespace and default-deny egress,Notebook runs without production credentials,Token/egress policy violation denied,evidence/admission/,Mitigate,YYYY-MM-DD,Human data-access mistakes remain possible
R-005,Runtime sensor silently stops,Medium,High,High,SRE owner,Heartbeat and sensor-health drill,Heartbeat is fresh,Stopped stream is flagged,evidence/runtime/,Mitigate,YYYY-MM-DD,Fixture path does not prove kernel sensor health
R-006,Synthetic advisory affects deployed digest,Medium,High,High,Release owner,Digest-indexed SBOM inventory and rescan workflow,Known unaffected image excluded,Known affected image listed,evidence/incident/,Mitigate,YYYY-MM-DD,Real advisory feed freshness is separate
R-007,Signing key compromise,Low,Critical,High,Security owner,Lab key isolation,Valid key verifies intended artifact,Wrong key rejected,evidence/signatures/,Mitigate,YYYY-MM-DD,Local key custody is not HSM/KMS protection
```

### 3.5 Attack trees (defensive planning only)

These are goal trees for controls and tabletop discussion, not
operational attack instructions.

**A. Goal: attacker-controlled code runs in the production inference
pod**

``` mermaid
flowchart TD
  A[Goal: unreviewed code executes in inference pod] --> B[Compromise source/review path]
  A --> C[Influence trusted build]
  A --> D[Substitute or misidentify artifact]
  A --> E[Bypass admission or deployment controls]
  B --> B1[Unprotected release ref]
  C --> C1[Untrusted job shares trusted cache or credential]
  D --> D1[Mutable tag or digest mismatch]
  E --> E1[Broad manual deployment privilege]
  E --> E2[Policy only checks one container list]
  B1 --> K[Controls: protected refs, provenance, digest, admission, RBAC]
  C1 --> K
  D1 --> K
  E1 --> K
  E2 --> K
```

**B. Goal: training data is exposed**

``` mermaid
flowchart TD
  A[Goal: training data exposed] --> B[Obtain workload execution]
  A --> C[Obtain excessive identity]
  A --> D[Reach data/model store]
  A --> E[Move data across boundary]
  B --> B1[Notebook compromise or unsafe model loading]
  C --> C1[Unnecessary service-account token or broad workload identity]
  D --> D1[Unrestricted egress or overbroad store authorization]
  E --> E1[Unmonitored outbound flow]
  B1 --> K[Controls: trust-tier separation, no token by default, least privilege, default-deny egress, audit/detection]
  C1 --> K
  D1 --> K
  E1 --> K
```

### 3.6 ML/data-specific threat notes

-   **Unsafe model deserialization:** some serialization formats can
    invoke code during loading. Treat model artifacts as executable
    inputs unless the format and loader provide a verified safer
    contract. Do not load untrusted pickle-like artifacts in a
    privileged production process.
-   **Compromised model artifact:** a software SBOM does not prove model
    integrity. Record model hash, origin, version, and approval
    separately; verify the hash at load or staging time where feasible.
-   **Training-data exposure:** control data access independently from
    image identity; do not embed datasets or credentials in image
    layers.
-   **Notebook compromise:** notebook-style images allow interactive
    execution and should be a separate trust tier, namespace, identity,
    and egress policy.
-   **Poisoned dependency:** lockfiles and hashes improve repeatability
    but do not prove a dependency is benign.
-   **Compromised CI:** separate untrusted validation from trusted
    release, protect caches, minimize permissions, and have a kill
    switch.
-   **Overbroad workload identity:** a pod identity should be narrowly
    scoped to the data/model objects and actions it needs.
-   **Model/data exfiltration:** enforce store authorization and network
    paths; monitor expected egress and unusual transfer patterns. This
    lab uses synthetic data only.

### 3.7 Threat-to-control traceability schema

Every row in `threat-model/threats.yaml` should have `id`,
`description`, `likelihood`, `impact`, `owner`, `controls`,
`positive_test`, `negative_test`, `evidence`, `residual_risk`, and
`status`. The starter validator in Phase 0 rejects missing fields and
expired/malformed exceptions. Add an owner and review date for any
accepted risk.

### 3.8 Risk acceptance policy

Risk acceptance is not a way to skip a test silently. An exception must
include: - unique ID and exact scope; - threat/control affected; - named
accountable owner; - rationale and evidence considered; - compensating
controls; - expiry and review date in ISO `YYYY-MM-DD`; - exit condition
and a remediation ticket/reference; - approver role separate from the
requester for high-impact exceptions \[ASSUMPTION: local lab simulates
this separation\].

Expired or ownerless exceptions fail `make evidence-check`. An accepted
risk still appears in metrics and the final residual-risk summary.

## 4. Prerequisites, resources, and feasibility

### 4.1 Preflight prerequisites

Required for the core path: - Git, Python 3, Make, a container
engine/build capability, Trivy, Syft, cosign, `jq`, and a text editor. -
A local Kubernetes cluster such as `kind` for
deployment/admission/runtime-manifest tests. - `kubectl`; policy engine
CLIs or cluster installation methods only for the selected engine
exercise. - Internet access for initial image/package pulls and
vulnerability database updates, unless cached artifacts/fixtures are
used.

Optional: - Local OCI registry, Helm/Kustomize if already part of the
learner's M06/M08 workflow, Prometheus/Loki/Grafana/Alertmanager, Falco
with a supported kernel/driver, and a format validator for
SPDX/CycloneDX.

**\[VERIFY\]** Install versions from official documentation and capture
them. Do not copy arbitrary install scripts into a privileged shell
without reviewing the script and source. Prefer package-manager or
signed-release installation methods supported by the upstream project.

### 4.2 Laptop budget and execution sequence

  ------------------------------------------------------------------------
  Component               Resource pressure       Budget decision
  ----------------------- ----------------------- ------------------------
  Three sample builds     Low--medium; image      Build and inspect one at
                          layers consume disk     a time; prune only
                                                  project-owned images

  Vulnerability DB        Network and disk;       Update once, record
                          database may be large   freshness, avoid
                                                  repeated updates during
                                                  same comparison

  Local registry          Disk proportional to    Use local registry only
                          image layers and        if it adds value;
                          attestations            otherwise use local
                                                  image references and
                                                  fixtures

  `kind` cluster          Medium; control plane   One cluster at a time
                          plus workloads          

  Kyverno                 Medium; admission       Exercise after VAP, then
                          webhooks and policy     remove and verify
                          resources               cleanup before
                                                  Gatekeeper

  Gatekeeper              Medium;                 Never install with
                          controller/webhook      Kyverno in the same
                          resources               cluster

  Falco                   Variable; kernel/driver Run feasibility
                          and event overhead      preflight first; use
                                                  fixture/rule-authoring
                                                  path if unsupported

  Observability stack     High relative to 8 GB   Optional; prefer JSON
                          RAM                     fixtures and a small
                                                  collector path for the
                                                  core capstone

  Total disk              Variable                Reserve 30 GB; measure
                                                  with `df -h` and
                                                  container-engine disk
                                                  inspection
  ------------------------------------------------------------------------

All resource estimates are \[ILLUSTRATIVE\]. Measure before and after
each phase; do not treat these as benchmarks.

### 4.3 Feasibility decision tree

``` mermaid
flowchart TD
  A[Start: measure CPU/RAM/disk] --> B{Can build and scan locally?}
  B -- No --> B1[Use prebuilt local fixture metadata; mark build/scan NOT RUN]
  B -- Yes --> C{Can run kind?}
  C -- No --> C1[Run manifest/policy unit tests offline; admission integration OPEN]
  C -- Yes --> D[Run VAP baseline]
  D --> E[Remove VAP test objects and validate cleanup]
  E --> F[Install Kyverno and test]
  F --> G[Remove Kyverno and verify no webhook remains]
  G --> H[Install Gatekeeper and test separately]
  H --> I{Falco kernel/driver supported?}
  I -- Yes --> J[Run bounded benign detection tests]
  I -- No --> K[Use rules and synthetic fixtures; live runtime detection NOT RUN]
```

### 4.4 Duration plan

  Workstream                                   Suggested effort \[ILLUSTRATIVE\]
  ------------------------------------------ -----------------------------------
  Preflight and threat model                                              2--4 h
  Sample apps/images                                                      3--5 h
  Scanning, triage, SBOM                                                  3--5 h
  CI trust separation, signing, provenance                                4--7 h
  Admission and runtime baseline                                          4--7 h
  Detection, audit, incident drill                                        4--7 h
  Evidence, cleanup, independent review                                   2--5 h

### 4.5 Offline fixture mode

Offline mode can test: - validator behavior; - policy logic against
fixture manifests; - scoring of synthetic findings; - SBOM query logic
against saved SBOM fixtures; - incident workflow and evidence index; -
rule metadata and fixture correlation.

Offline mode does **not** prove: - vulnerability database freshness or
current advisory coverage; - registry authentication or actual signature
storage behavior; - a real build's provenance integrity; - live
admission API compatibility; - kernel event capture or Falco driver
health; - external CI provider OIDC claims or runner isolation.

Record every fixture-only test as `NOT RUN` for the live behavior and
`PASS` only for the fixture logic itself.

## 5. Repository layout and evidence inventory

Create this project beneath `M12/Projects/`; the target repository is
not modified by this workbook itself. The paths below are a proposed
project layout, not a claim that the files already exist.

``` text
secure-and-verified-container-release/
├── README.md
├── Makefile
├── versions.txt
├── .gitignore
├── app/
│   ├── inference-api/
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   ├── requirements.lock.txt
│   │   └── Dockerfile
│   ├── etl-job/
│   │   ├── job.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── notebook/
│       ├── notebook_stub.py
│       └── Dockerfile
├── ci/
│   ├── untrusted/README.md
│   ├── trusted-release/README.md
│   ├── policy/release-policy.yaml
│   └── tests/test_workflow_boundaries.py
├── builder/
│   ├── build-definition/README.md
│   ├── tool-verification/versions.sh
│   └── provenance/README.md
├── policy/
│   ├── kyverno/
│   ├── gatekeeper/
│   ├── vap/
│   ├── rego/
│   └── tests/
├── detection/
│   ├── falco/
│   ├── audit/
│   ├── alert-rules/
│   └── fixtures/
├── threat-model/
│   ├── data-flow.md
│   ├── threats.yaml
│   ├── risk-register.csv
│   └── validate.py
├── audit/
│   ├── findings/
│   ├── exceptions/
│   ├── evidence-index.md
│   └── reports/
├── runbooks/
├── sim/
│   ├── benign/
│   ├── fixtures/
│   └── scorecard/
├── evidence/
│   ├── scans/
│   ├── sbom/
│   ├── signatures/
│   ├── provenance/
│   ├── admission/
│   ├── runtime/
│   └── incident/
└── docs/
    ├── architecture.md
    ├── trust-model.md
    ├── rollout-and-rollback.md
    └── limitations.md
```

### 5.1 Artifact states

-   **Learner-created:** source code, Dockerfiles, threat model, policy,
    scripts, runbooks, and documentation.
-   **Provided inline here:** sample app files, representative
    Dockerfiles, validator, fixture findings, test inventory, and
    templates.
-   **Generated during execution:** built image digests, scan reports,
    SBOMs, signatures, attestations, provenance, policy test output, and
    tool-version inventory.
-   **Only present after a real run:** command logs, actual scanner
    reports, live admission denials, observed runtime alerts, and
    measured timing.

### 5.2 Evidence naming convention

Use a stable, timestamped pattern such as:

`evidence/<category>/<UTC-YYYYMMDDTHHMMSSZ>_<test-id>_<short-digest-or-fixture>.<ext>`

Examples are naming examples, not existing evidence: -
`evidence/scans/20261029T120000Z_SCAN-API_sha256-<digest>.json` -
`evidence/admission/20261029T120000Z-ADV-05-invalid-image.yaml.log` -
`evidence/runtime/20261029T120000Z-DET-04-fixture.json`

Do not put secrets, tokens, private keys, customer data, or full
sensitive command environments in evidence. Keep local evidence private
and retain only as long as needed for the learning review; delete
disposable credentials and keys at cleanup. Preserve the evidence needed
for the final review until the reviewer signs off.

### 5.3 `.gitignore` starter

``` gitignore
# Secrets and disposable signing material
*.key
*.pem
*.token
.env
.env.*
!*.env.example
cosign.key
cosign.pub
# Local evidence may contain internal paths and operational details
evidence/
# Local clusters, registries and caches
.cache/
.tmp/
*.log
# Python
__pycache__/
*.py[cod]
.venv/
```

If the public key must be included in a teaching evidence bundle, copy
it explicitly to `evidence/signatures/` after review; never commit the
private key. Adapt ignore rules if evidence is intentionally tracked in
a controlled training repository.

## 6. Phase 0 --- Safe bootstrap and preflight

### Why this phase exists

A secure workflow that runs against the wrong cluster is itself a risk.
The first gate must establish the actual environment, tool versions,
available resources, and lab context before building or applying policy.

### Threats and controls

-   **Threat:** destructive command reaches a non-lab cluster.
    -   **Control:** require explicit expected context and a unique
        namespace prefix; refuse when context differs.
-   **Threat:** unsupported platform is mistaken for a failed control.
    -   **Control:** classify capability as supported, unsupported, or
        not checked; use fixture mode honestly.
-   **Threat:** secrets are accidentally committed or printed.
    -   **Control:** dummy-only credentials, `.gitignore`, redacted
        logs, no secret values in command-line arguments.

### Files to create

-   `versions.txt`
-   `.gitignore`
-   `threat-model/data-flow.md`
-   `threat-model/threats.yaml`
-   `threat-model/validate.py`
-   `docs/limitations.md`

### `versions.txt` starter

``` text
# Fill only from actual command output. Never copy example versions as if observed.
capture_date_utc=
os_release=
kernel_release=
container_engine_version=
buildkit_version=
kubectl_version=
kubernetes_server_version=
kind_version=
trivy_version=
trivy_db_updated_at=
syft_version=
cosign_version=
python_version=
jq_version=
falco_version_or_NOT_INSTALLED=
policy_engine_and_version_or_NOT_INSTALLED=
network_policy_enforcement=
falco_driver_or_fixture_mode=
```

### Preflight commands

Run commands individually and save actual output. A command not
available on the platform is a recorded prerequisite failure, not a
reason to fabricate a value.

``` bash
date -u +%Y-%m-%dT%H:%M:%SZ
uname -a
cat /etc/os-release
nproc
free -h
df -h .
git --version
python3 --version
make --version
docker version
kubectl version --client
kind version
trivy --version
syft version
cosign version
jq --version
```

Some commands will be absent until tools are installed. Mark them
`NOT INSTALLED` in the version inventory rather than running an
unreviewed install script.

### Threat validator starter

The script below validates a compact JSON representation of the risk
register and exception list. It is a complete runnable Python
standard-library validator; it deliberately does not parse arbitrary
YAML, so use JSON for machine-validated input or add a pinned YAML
parser as a documented dependency.

Save as `threat-model/validate.py`:

``` python
#!/usr/bin/env python3
"""Validate required threat/control fields and exception expiry without third-party packages."""
from __future__ import annotations
import json
import re
import sys
from datetime import date
from pathlib import Path

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
THREAT_FIELDS = {
    "id", "description", "likelihood", "impact", "owner", "controls",
    "positive_test", "negative_test", "evidence", "residual_risk", "status"
}
EXCEPTION_FIELDS = {
    "id", "scope", "owner", "rationale", "compensating_controls",
    "expiry", "review_date", "exit_condition"
}
ALLOWED_LIKELIHOOD = {"Low", "Medium", "High"}
ALLOWED_IMPACT = {"Low", "Medium", "High", "Critical"}

def valid_date(value: object) -> bool:
    if not isinstance(value, str) or not DATE_RE.fullmatch(value):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False

def nonempty(value: object) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value) and all(nonempty(x) for x in value)
    return value is not None

def validate(document: dict) -> list[str]:
    errors: list[str] = []
    threats = document.get("threats")
    exceptions = document.get("exceptions", [])
    if not isinstance(threats, list) or not threats:
        errors.append("'threats' must be a non-empty list")
        threats = []
    ids: set[str] = set()
    for index, item in enumerate(threats):
        prefix = f"threats[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        missing = sorted(THREAT_FIELDS - item.keys())
        if missing:
            errors.append(f"{prefix} missing fields: {', '.join(missing)}")
        for field in THREAT_FIELDS:
            if field in item and not nonempty(item[field]):
                errors.append(f"{prefix}.{field} must not be empty")
        tid = item.get("id")
        if isinstance(tid, str):
            if tid in ids:
                errors.append(f"duplicate threat id: {tid}")
            ids.add(tid)
        if item.get("likelihood") not in ALLOWED_LIKELIHOOD:
            errors.append(f"{prefix}.likelihood must be one of {sorted(ALLOWED_LIKELIHOOD)}")
        if item.get("impact") not in ALLOWED_IMPACT:
            errors.append(f"{prefix}.impact must be one of {sorted(ALLOWED_IMPACT)}")
        if isinstance(item.get("controls"), list) and not item["controls"]:
            errors.append(f"{prefix}.controls must include at least one mitigation or an explicit accepted-risk control")
    if not isinstance(exceptions, list):
        errors.append("'exceptions' must be a list")
        exceptions = []
    for index, item in enumerate(exceptions):
        prefix = f"exceptions[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        missing = sorted(EXCEPTION_FIELDS - item.keys())
        if missing:
            errors.append(f"{prefix} missing fields: {', '.join(missing)}")
        for field in EXCEPTION_FIELDS:
            if field in item and not nonempty(item[field]):
                errors.append(f"{prefix}.{field} must not be empty")
        for field in ("expiry", "review_date"):
            value = item.get(field)
            if not valid_date(value):
                errors.append(f"{prefix}.{field} must be a valid YYYY-MM-DD date")
            elif field == "expiry" and date.fromisoformat(value) < date.today():
                errors.append(f"{prefix} exception {item.get('id', index)} is expired")
    return errors

def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 threat-model/validate.py threat-model/register.json", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read valid JSON: {exc}", file=sys.stderr)
        return 2
    errors = validate(document)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: required threat and exception fields are present")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

Save a valid starter as `threat-model/register.json`:

``` json
{
  "threats": [
    {
      "id": "T-PR-001",
      "description": "Untrusted contribution reaches release signing capability",
      "likelihood": "High",
      "impact": "Critical",
      "owner": "release-owner",
      "controls": ["Separate untrusted and trusted jobs", "Protected release ref"],
      "positive_test": "Trusted protected-ref fixture is accepted",
      "negative_test": "Untrusted-ref fixture cannot invoke signing",
      "evidence": "evidence/ci/",
      "residual_risk": "Hosted runner isolation is not proved by local simulation",
      "status": "OPEN"
    }
  ],
  "exceptions": []
}
```

### Positive test

``` bash
python3 threat-model/validate.py threat-model/register.json
```

**Representative expected result:** exit code `0` and a `PASS` message.

### Negative test

Make a temporary copy, remove `owner`, and confirm the validator exits
nonzero. Also add an expired exception and a malformed date. Keep these
as fixtures under `sim/fixtures/`; do not corrupt the canonical
register.

### Evidence

-   `evidence/preflight/host-inventory.txt`
-   `evidence/preflight/tool-versions.txt`
-   `evidence/preflight/threat-register-validation.log`
-   `evidence/preflight/validator-negative-tests.log`

### Cleanup

No cluster or registry should be created in this phase. Remove any
temporary test copies. Keep only the evidence necessary for review.

### Acceptance criteria

-   Actual platform and tool versions are recorded or marked absent.
-   Resource availability is measured.
-   The current Kubernetes context is recorded before cluster
    operations.
-   Threat validator positive and negative tests are run.
-   No secret is printed or committed.

### What this proves / does not prove

It proves the local preflight and validator logic ran as recorded. It
does not prove the local host is uncompromised, every tool is authentic,
or an external CI runner has equivalent properties.

## 7. Phase 1 --- Three hardened sample workloads

### Why this phase exists

The workload types have different trust and execution needs. The
inference API should expose a narrow request interface; the ETL job
should run to completion with no network access unless explicitly
needed; the notebook image is interactive and should be isolated rather
than granted production identity.

### Design choices

-   Use a small Python standard-library HTTP server for the API so the
    starter does not need third-party runtime packages.
-   Use a small standard-library ETL script reading a bundled synthetic
    CSV.
-   Use a notebook-style stub rather than launching a full Jupyter stack
    by default. A full notebook stack is \[OPTIONAL\] because it
    increases resource use and requires a separate
    network/authentication design.
-   Use multi-stage builds where they provide a concrete benefit; do not
    claim every tiny application benefits from one.
-   Prefer a maintained minimal base image and digest pinning. Exact
    image digests are platform/architecture-specific and must be
    selected and verified by the learner. Use `BASE_IMAGE` as an
    explicit build argument only if the build workflow supplies a
    verified digest-pinned reference.
-   No secrets in Docker build arguments, environment variables, labels,
    layers, or source.

### 7.1 Inference API

Create `app/inference-api/app.py`:

``` python
#!/usr/bin/env python3
"""Harmless inference-shaped API; returns a deterministic demo result."""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8080"))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/healthz":
            body = {"status": "ok"}
            self.send_response(200)
        elif self.path == "/predict?value=1":
            body = {"prediction": 1, "model": "synthetic-demo-v1"}
            self.send_response(200)
        else:
            body = {"error": "not found", "path": self.path}
            self.send_response(404)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode("utf-8"))

    def log_message(self, fmt, *args):
        # Keep request logging simple; do not log secrets or request bodies.
        print("request", self.command, self.path, self.client_address[0])

if __name__ == "__main__":
    HTTPServer((HOST, PORT), Handler).serve_forever()
```

Create `app/inference-api/requirements.txt` containing a comment only:

``` text
# This sample uses only the Python standard library.
```

Create `app/inference-api/Dockerfile`:

``` dockerfile
# [VERIFY] Replace this example placeholder with a maintained, verified,
# digest-pinned Python base image for the target architecture.
ARG BASE_IMAGE=python:3.12-slim
FROM ${BASE_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app
COPY --chown=10001:10001 app/inference-api/app.py /app/app.py

USER 10001:10001
EXPOSE 8080
# Health is checked by the orchestrator; do not assume Docker HEALTHCHECK is used.
CMD ["python", "-I", "/app/app.py"]
```

The `BASE_IMAGE` default is intentionally **not** a digest pin. For an
accepted build, override it with a verified digest reference, for
example `python:<selected-tag>@sha256:<verified-digest>`; the
placeholder is not a usable digest. Capture the resolved digest and
platform in the build evidence. The exact Python version is a
compatibility choice, not a permanent recommendation.

### 7.2 ETL job

Create `app/etl-job/job.py`:

``` python
#!/usr/bin/env python3
"""Summarize a synthetic CSV; no external data store is contacted."""
import csv
import json
import sys
from pathlib import Path

def main() -> int:
    source = Path(sys.argv[1] if len(sys.argv) > 1 else "/data/sample.csv")
    total = 0
    count = 0
    with source.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            total += int(row["value"])
            count += 1
    print(json.dumps({
        "input": source.name,
        "rows": count,
        "sum": total,
        "dataset": "synthetic-training-fixture"
    }, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

Create `app/etl-job/sample.csv`:

``` csv
record_id,value
sample-001,2
sample-002,3
sample-003,5
```

Create `app/etl-job/requirements.txt`:

``` text
# Standard-library only; no third-party dependencies.
```

Create `app/etl-job/Dockerfile`:

``` dockerfile
# [VERIFY] Replace with a maintained digest-pinned base image for the target platform.
ARG BASE_IMAGE=python:3.12-slim
FROM ${BASE_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY --chown=10002:10002 app/etl-job/job.py /app/job.py
COPY --chown=10002:10002 app/etl-job/sample.csv /data/sample.csv
USER 10002:10002
ENTRYPOINT ["python", "-I", "/app/job.py"]
CMD ["/data/sample.csv"]
```

### 7.3 Notebook-style image

Create `app/notebook/notebook_stub.py`:

``` python
#!/usr/bin/env python3
"""Controlled notebook-style image stub; intentionally has no server or credentials."""
from pathlib import Path
import json

workspace = Path("/workspace")
workspace.mkdir(parents=True, exist_ok=True)
marker = workspace / "lab-ready.txt"
marker.write_text("synthetic notebook workspace ready\n", encoding="utf-8")
print(json.dumps({
    "mode": "controlled-analysis-stub",
    "workspace": str(workspace),
    "production_credentials": False
}, sort_keys=True))
```

Create `app/notebook/Dockerfile`:

``` dockerfile
# [VERIFY] Replace with a maintained digest-pinned Python base image.
ARG BASE_IMAGE=python:3.12-slim
FROM ${BASE_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /workspace
COPY --chown=10003:10003 app/notebook/notebook_stub.py /app/notebook_stub.py
USER 10003:10003
ENTRYPOINT ["python", "-I", "/app/notebook_stub.py"]
```

This stub is not a full notebook service. A real Jupyter image needs
authentication, TLS/proxy, user isolation, persistence, extension
governance, and network access decisions. Do not expose a notebook
service publicly for this exercise.

### 7.4 Build-context hygiene

Create a root `.dockerignore`:

``` dockerignore
.git
.git/**
.env
.env.*
*.key
*.pem
*.token
**/__pycache__
**/.pytest_cache
.venv
evidence
audit
```

Use separate build contexts (`app/inference-api`, `app/etl-job`,
`app/notebook`) or a reviewed root context with explicit `COPY` paths.
Do not copy the whole repository into the image. Never pass a secret via
`ARG` or bake credentials into files. Build secrets, if ever needed in a
later extension, must use the builder's documented secret mount
mechanism and be verified against the selected BuildKit version
\[VERIFY\].

### 7.5 Naive baseline and hardened comparison

For a safe comparison, build a **fixture-only naive Dockerfile** that
deliberately uses a mutable tag and root user but does not include
secrets or unsafe payloads. Name it `sim/benign/naive.Dockerfile` and do
not deploy it:

``` dockerfile
# [SYNTHETIC TRAINING BASELINE — DO NOT DEPLOY]
FROM python:3.12-slim
WORKDIR /app
COPY app.py /app/app.py
CMD ["python", "/app/app.py"]
```

Compare baseline and hardened image metadata, user, filesystem behavior,
package inventory, digest, and policy decisions. A smaller image may
still be vulnerable; a distroless image may reduce available utilities
while also making debugging harder. Minimality is one control, not a
security verdict.

### 7.6 Build and inspect

First verify selected base-image digests from the registry/tool output.
Then build each workload with a digest-pinned `BASE_IMAGE`. Example
shape (replace the variable with an actual verified reference):

``` bash
export VERIFIED_PYTHON_BASE='python:3.12-slim@sha256:<verified-digest>'
docker build --build-arg BASE_IMAGE="$VERIFIED_PYTHON_BASE" \
  -f app/inference-api/Dockerfile -t localhost/secure-release/inference-api:lab .
```

**\[VERIFY\]** Build context and Dockerfile path behavior depend on how
the command is invoked. Prefer a repository-root context only if the
`COPY` paths are correct; otherwise use a dedicated context and adjust
`COPY` accordingly. Do not leave the literal `<verified-digest>` in an
executable command.

Inspect actual image metadata with the engine's documented inspection
command. Record user, entrypoint, environment, layers, and digest. Run
as the non-root user and test read-only root filesystem compatibility at
runtime. The Dockerfile alone cannot enforce all Kubernetes runtime
settings.

### 7.7 Reproducibility check

Build twice from the same source revision, base digest, platform,
builder version, dependency inputs, and build arguments. Compare image
digests. If digests differ, record the difference and investigate
timestamps, nondeterministic build steps, metadata, architecture, or
dependency resolution. Do not normalize away meaningful differences
merely to claim reproducibility.

### Positive tests

-   API `/healthz` returns a JSON success response.
-   ETL job returns the expected row count and sum for the synthetic
    fixture.
-   Notebook stub writes only within its designated workspace.
-   Runtime user is non-root.
-   The workload runs under a read-only root filesystem with explicit
    writable temp/workspace paths where needed.

### Negative tests

-   An unpinned base image is rejected by the build-policy test.
-   A fixture Dockerfile running as root is rejected by the image
    baseline test.
-   A secret-pattern file placed in a temporary build context is
    excluded by `.dockerignore` and absent from image layers. Use only a
    dummy marker; do not use a real credential.
-   A write to a read-only root path fails while an approved writable
    path works.

### Evidence

Save build logs, image digests, base image digests, runtime UID
inspection, read-only filesystem test, and reproducibility comparison
under `evidence/build/`. Record `NOT RUN` where the platform cannot
perform a test.

### Cleanup

Remove temporary baseline images and dummy marker files. Do not run
global prune commands unless you have reviewed exactly what would be
removed; use project-specific tags and inspect resources first.

### Acceptance criteria

All three workload definitions are complete and harmless; base images
are selected and pinned by digest for accepted builds; no real secret
enters context/layers; all three workloads have distinct runtime
identities; the notebook is explicitly treated as a separate trust tier.

### What this proves / does not prove

This proves selected build and runtime properties for the tested
artifact and platform. It does not prove all dependencies are safe, all
builds are hermetic, all architectures behave identically, or a model
file is trustworthy.

## 8. Phase 2 --- Scan, triage, VEX, and exceptions

### Why this phase exists

Vulnerability counts are not risk scores. A fixable critical flaw
reachable by an exposed inference API may outrank many low-impact
findings in an unused build-only dependency. Conversely, "unreachable"
is a claim requiring evidence and may change after a feature or
configuration change.

### Scanner workflow

Use Trivy as the core scanner for image, filesystem/dependency, and
configuration scanning. The exact commands, formats, exit codes, ignore
syntax, VEX support, and database metadata behavior are
version-sensitive: **\[VERIFY\]** against the installed Trivy version's
official CLI reference before treating any command as a gate.

Capture: - Trivy version; - database timestamp/freshness state; - image
digest; - scan target and settings; - machine-readable report; -
human-readable report; - exit code; - offline/online state; - exceptions
and rationale.

**Representative command shapes --- verify flags and formats first:**

``` bash
trivy image --format json --output evidence/scans/inference-image.json "$IMAGE_BY_DIGEST"
trivy image --format table "$IMAGE_BY_DIGEST" > evidence/scans/inference-image.txt
trivy fs --format json --output evidence/scans/source-fs.json .
trivy config --format json --output evidence/scans/config.json .
```

Do not assume every subcommand supports identical flags. Run the
installed command's `--help` and compare it to official documentation.
If the version does not support a requested output, record the mismatch
and use a supported format. Do not silently swap in a different scanner.

### 8.1 Scan consistency

Scan all three image types using the same documented Trivy version and
the same database snapshot where feasible. If the database updates
between scans, capture each timestamp and do not compare the raw counts
as if the scans were contemporaneous. Pin the tested image by digest.
Repeat scans of deployed digests on a schedule chosen by the learner;
record the cadence as a policy decision, not an industry statistic.

### 8.2 Triage dimensions

  -----------------------------------------------------------------------
  Dimension               Question                Evidence to inspect
  ----------------------- ----------------------- -----------------------
  Asset criticality       What workload and data  Service tier, data
                          does this affect?       classification,
                                                  business owner

  Exposure                Is the workload         Service, ingress,
                          internet-facing,        network policy
                          internal, scheduled, or 
                          developer-only?         

  Exploitability          Is the vulnerable path  Call path,
                          reachable in this       configuration, feature
                          build/runtime?          usage; state
                                                  uncertainty

  Fix availability        Is there a patched      Vendor advisory,
                          version or maintained   package changelog,
                          base?                   current scanner
                                                  metadata

  Package type            OS package, language    SBOM and package
                          dependency,             metadata
                          vendored/static code,   
                          tool-only dependency?   

  Distro backport         Could the distribution  Distribution advisory
                          have patched without    and package release
                          changing upstream       notes
                          version?                

  Compensating control    Does a control reduce   Tested control, scope,
                          likelihood or impact?   failure mode

  Decision                Fix, mitigate, accept   Named owner, due date,
                          temporarily, or         evidence, expiry
                          establish not-affected? 

  Recheck                 How will closure be     Rescan of the released
                          verified?               digest and policy
                                                  result
  -----------------------------------------------------------------------

Do not label a finding "false positive" merely because the package
version looks old. Distribution backports and version semantics require
package-specific evidence. Do not claim "unreachable" without a
defensible call-path/configuration analysis. Scanner blind spots include
undiscovered static/vendored code, unsupported ecosystems, dynamically
downloaded files, model contents, and stale advisory data.

### 8.3 Synthetic triage fixture set

All records below are **\[SYNTHETIC\]** training data; the identifiers
are not CVEs and must never be presented as real vulnerabilities.

  -----------------------------------------------------------------------
  ID                Fixture           Context           Expected decision
                                                        exercise
  ----------------- ----------------- ----------------- -----------------
  SYN-001           Critical, fix     Inference API     Prioritize
                    available         exposed;          immediate
                                      vulnerable        remediation and
                                      component used on block release
                                      request path      pending
                                                        fix/approved
                                                        mitigation

  SYN-002           Critical, no fix  ETL runtime       Mitigate
                                      dependency;       exposure, assign
                                      exposure limited  owner, expiry,
                                      but impact high   and vendor
                                                        monitoring

  SYN-003           High, build-only  Compiler/tool     Confirm final
                                      present only in   image excludes
                                      build stage       it; still assess
                                                        builder risk

  SYN-004           High, allegedly   Runtime package   Do not accept
                    unused            with no           "unused" until
                                      reachability      evidence is
                                      evidence          attached

  SYN-005           Old upstream      OS package        Verify distro
                    version, distro   patched by        advisory; do not
                    backport          distribution      infer
                                                        vulnerability
                                                        from version
                                                        string alone

  SYN-006           KEV-listed        Synthetic         Use a clearly
                    scenario          substitute for a  labeled synthetic
                                      real current KEV  record unless
                                      case              current CISA KEV
                                                        data is actually
                                                        retrieved and
                                                        cited

  SYN-007           Medium with       Egress restricted Document control
                    compensating      and process not   scope and failure
                    control           exposed           mode; do not
                                                        automatically
                                                        downgrade

  SYN-008           End-of-life base  No longer         Replace base even
                                      maintained        if current
                                                        scanner shows few
                                                        findings

  SYN-009           False-positive    Scanner           Investigate
                    uncertainty       identifies        package identity;
                                      component         keep open until
                                      ambiguously       evidence

  SYN-010           False-negative    Static vendored   Add source/build
                    uncertainty       library absent    inspection;
                                      from SBOM         scanner silence
                                                        is not absence
                                                        proof

  SYN-011           High, exposed     Request parsing   Fix promptly;
                    endpoint          path              test regression

  SYN-012           Medium,           Developer image   Separate trust
                    notebook-only     with interactive  tier and shorten
                                      access            exception
                                                        duration

  SYN-013           Low, old tool     Build-only CLI    Consider builder
                                      not in final      integrity and
                                      image             update lifecycle

  SYN-014           Critical,         Model artifact is Do not load
                    vulnerable model  untrusted         untrusted
                    loader                              artifact;
                                                        validate format
                                                        and provenance

  SYN-015           High, model hash  Model file        Quarantine
                    mismatch          differs from      artifact and
                                      approved hash     investigate
                                                        provenance

  SYN-016           High, mutable tag Tag resolves to   Pin and verify
                                      different digest  digest;
                                      on later pull     invalidate stale
                                                        evidence

  SYN-017           High, stale       Scanner DB older  Mark scan stale
                    database          than local        and prevent it
                                      freshness policy  from being
                                                        accepted as
                                                        current

  SYN-018           Medium, package   Component has     Record
                    hash absent       incomplete        uncertainty and
                                      metadata          seek
                                                        authoritative
                                                        package metadata

  SYN-019           High, dependency  Similar package   Verify
                    confusion         name from         registry/source
                                      unexpected source and lockfile
                                                        origin

  SYN-020           High, no fix and  Service exposed,  Contain exposure
                    broad reach       package cannot be and track
                                      patched           explicit risk
                                                        acceptance

  SYN-021           Medium,           Parent package    Update dependency
                    transitive        pulls component   chain and rerun
                    dependency                          tests

  SYN-022           High, CI-only     Dummy secret      Verify it is
                    secret scanner    marker in test    synthetic and
                    finding           fixture           ensure no real
                                                        secret exists in
                                                        repository

  SYN-023           Medium,           Present only in   Document
                    vulnerable test   validation stage  build/test
                    tool                                environment risk
                                                        separately from
                                                        runtime risk

  SYN-024           High, uncertain   Scanner and       Keep inconclusive
                    distro mapping    vendor advisory   pending vendor
                                      disagree          evidence

  SYN-025           Critical, signed  Valid signature,  Reject on risk
                    but vulnerable    unacceptable scan policy; signature
                                      result            proves key-bound
                                                        integrity, not
                                                        safety
  -----------------------------------------------------------------------

### 8.4 Risk-based triage record schema

Each real or synthetic finding record should include: `finding_id`,
`artifact_digest`, `source`, `component`, `advisory_ref`, `severity`,
`exposure`, `reachability_evidence_or_uncertainty`,
`exploitability_context`, `fix_available`, `asset_criticality`,
`compensating_controls`, `decision`, `owner`, `due_date`, `rationale`,
`evidence_links`, `state`, and `last_verified`.

Use `SYN-001` style IDs for invented training findings. Never fabricate
a real CVE number.

### 8.5 VEX and "not affected" claims

Choose one VEX format explicitly and validate against its current
specification before use. **\[VERIFY\]** The current VEX format schema,
status values, required fields, and Trivy consumption support must be
checked against official sources for the selected version. Do not mix
CycloneDX VEX and OpenVEX fields in one document without explaining the
distinction.

A "not affected" decision must include: - the exact product/component
and artifact identity; - a recognized status value in the selected
format; - a justification grounded in code/configuration/build
evidence; - evidence location and reviewer; - scope and review date; -
conditions that would invalidate the decision.

Negative test: a VEX record with no justification or no affected
component identity must be rejected by the local validator. Never
suppress findings solely to make a dashboard green.

### 8.6 Expiring suppressions and database freshness

Every suppression/ignore requires owner, rationale, scope, created date,
expiry date, and exit condition. Validate dates and fail when expired.
The scanner's own ignore mechanism may vary; keep the independent
exception registry authoritative and test the scanner configuration
separately.

**\[VERIFY\]** Confirm the installed Trivy version's database metadata
and offline options. If the database is unavailable or stale, label the
scan as stale/offline and do not pass a "current vulnerability status"
gate. A cached report is useful for deterministic triage exercises but
does not demonstrate current advisory coverage.

### 8.7 Scheduled rescan design

For each deployed digest: 1. Retrieve the exact digest, not a mutable
tag. 2. Scan with a recorded DB freshness state. 3. Compare findings to
the previous report. 4. Open or update finding records with owners and
due dates. 5. Re-evaluate risk based on exposure and fix availability.
6. Trigger release replacement/containment when policy requires. 7. Save
reports and close only after rescanning the remediated digest.

### 8.8 Synthetic advisory "are we affected?" drill

Use `SYN-ADVISORY-2026-001` as a **synthetic internal training ID**, not
a CVE. Create a fixture component name/version in a test SBOM, query the
digest-indexed inventory, and prove: - a known affected fixture image is
returned; - a known unaffected fixture image is not returned; -
unknown/malformed SBOM data produces `INCONCLUSIVE`, not a false "not
affected" answer.

Optional KEV/EPSS enrichment must record source URL, retrieval time,
parsing version, identifier match confidence, and the fact that KEV/EPSS
is context---not a fully automated risk decision. If current data is not
fetched, use the synthetic substitute only.

### Positive test

-   All three images are scanned under the same recorded settings and
    database state, or any difference is explained.
-   Machine-readable and human-readable reports are saved.
-   A known synthetic component is found in the expected SBOM fixture.
-   A justified VEX fixture passes.

### Negative test

-   A stale database cannot satisfy a current-scan gate.
-   An unjustified "not affected" fixture fails.
-   An expired ignore fails.
-   A synthetic critical/fixable exposed finding blocks release under
    the chosen policy.

### Cleanup, acceptance, limitations

Keep synthetic fixture IDs clearly separated from live reports. Do not
suppress findings in real artifacts to mimic the fixture result.
Acceptance requires triage decisions with owners, due dates, evidence,
and explicit uncertainty. Scanning does not prove exploitability,
absence of vulnerabilities, runtime reachability, or complete inventory.

## 9. Phase 3 --- SBOM and component inventory

### Why this phase exists

A Software Bill of Materials (SBOM) is a machine-readable inventory of
components associated with an artifact. It supports investigation and
change analysis, but it is not a complete representation of source
behavior, all static code, model semantics, or training data.

### Generate actual-artifact SBOMs

Use Syft as the core generator. Generate both SPDX and CycloneDX outputs
for each actual image digest. **\[VERIFY\]** Confirm the installed Syft
CLI syntax, supported output identifiers, schema versions, and validator
compatibility against the official documentation for the selected
release.

Representative command shapes:

``` bash
syft "$IMAGE_BY_DIGEST" -o spdx-json=evidence/sbom/inference.spdx.json
syft "$IMAGE_BY_DIGEST" -o cyclonedx-json=evidence/sbom/inference.cdx.json
```

These output-selector forms are version-sensitive; verify with
`syft --help` before use. If unsupported, use the documented syntax for
the installed version and record the change.

### 9.1 Subject association

For each SBOM, save a manifest containing: - image repository and
digest; - platform/architecture; - Syft version; - format and schema
version; - creation timestamp; - source commit; - output checksum; -
validation result; - known limitations.

The SBOM must describe the actual built artifact, not merely the source
tree. Build-time source SBOMs may be useful as a separate inventory, but
they must not be mislabeled as image SBOMs.

### 9.2 SBOM quality checks

Check: - subject/artifact identity and digest association; - non-empty
component list where components are expected; - generator and creation
metadata; - duplicate or unknown component handling; - package URLs and
hashes where applicable; - relationships when the chosen format exposes
them; - schema validity using an appropriate validator if feasible; -
whether the inventory differs unexpectedly between releases.

Syntax validity is not completeness. A schema-valid SBOM can still omit
vendored or statically linked components. A model binary may appear as a
file but its semantic contents and training lineage are not fully
described by a software SBOM.

### 9.3 Digest-indexed inventory and query

Create `evidence/sbom/inventory.json` with entries shaped like:

``` json
{
  "schema_version": "local-inventory-v1",
  "generated_at": "FILL_FROM_REAL_RUN",
  "images": [
    {
      "name": "localhost/secure-release/inference-api",
      "digest": "sha256:REPLACE_WITH_ACTUAL_DIGEST",
      "spdx_path": "evidence/sbom/inference.spdx.json",
      "cyclonedx_path": "evidence/sbom/inference.cdx.json",
      "scan_path": "evidence/scans/inference-image.json",
      "status": "NOT RUN"
    }
  ]
}
```

The digest is intentionally a placeholder, not an image identity. Never
accept this inventory as complete until every real entry is populated
from observed build output.

A simple query script should: 1. read the inventory; 2. parse each
supported SBOM format using a format-specific adapter; 3. search package
name/version or package URL; 4. return image name, digest, SBOM path,
and confidence/limitations; 5. fail closed to `INCONCLUSIVE` on parse
errors or unknown formats.

Do not write one generic parser that assumes SPDX and CycloneDX share
the same field names.

### 9.4 Release-to-release diff

Compare component identity and version, not just line-oriented JSON.
Normalize only irrelevant ordering/formatting differences. Report
additions, removals, version changes, unknown identifiers, and
schema/generator changes. A change in generator version can change
inventory output even when the image has not changed; preserve raw SBOMs
for audit.

### 9.5 ML artifact inventory

Maintain a separate optional `evidence/sbom/model-inventory.json`:

``` json
{
  "schema_version": "local-model-inventory-v1",
  "models": [
    {
      "model_id": "synthetic-demo-model",
      "version": "v1",
      "sha256": "REPLACE_WITH_HASH_OF_SYNTHETIC_FIXTURE",
      "origin": "local training fixture",
      "approval": "NOT RUN",
      "loader_format": "plain-text-demo",
      "data_lineage_reference": "synthetic-only",
      "notes": "This record does not prove model safety or data provenance."
    }
  ]
}
```

Use a harmless text fixture for this capstone. Do not load untrusted
pickle or arbitrary model binaries as part of the normal acceptance
path. If a separate unsafe-deserialization risk demonstration is
performed, isolate it in a disposable environment and use a benign
marker-only fixture; do not use real data or credentials.

### Positive and negative tests

-   Positive: query the known synthetic component and return the
    expected image digest.
-   Negative: query a known absent component and return "not found in
    complete tested inventory" only when the inventory's completeness
    assumptions are satisfied; otherwise return `INCONCLUSIVE`.
-   Negative: a mismatched image digest in the SBOM manifest fails.
-   Negative: malformed SBOM or unknown schema fails validation.

### Evidence and acceptance

Save raw SPDX/CycloneDX outputs, validation results, inventory index,
query results, diff report, and limitations. Acceptance requires both
formats for each actual image, subject-digest association,
positive/negative queries, and an explicit inventory blind-spot
statement.

## 10. Phase 4 --- Separate untrusted and trusted build paths

### Why this phase exists

A pull request from an untrusted contributor may execute arbitrary
build/test code. If that code shares a registry password, signing key,
privileged Docker socket, trusted cache, or release permissions, the
pipeline boundary is only cosmetic.

### Trust-path design

``` mermaid
flowchart TD
  A[PR / fork / untrusted contribution] --> U[Untrusted validation runner]
  U --> UT[Lint, unit tests, fixture policy tests]
  U -. no signing key, no release token, no trusted cache .-> Stop[End]
  B[Protected ref + required review] --> T[Trusted release runner]
  T --> VerifySource[Verify source/ref and tools]
  VerifySource --> Build[Build isolated artifact]
  Build --> Scan[Scan + SBOM + tests]
  Scan --> Sign[Sign digest + attest evidence]
  Sign --> Promote[Promote only after verification]
  Promote --> GitOps[Reviewed GitOps change]
```

### 10.1 Capability table

  -------------------------------------------------------------------------
  Capability              Untrusted validation     Trusted release
  ----------------------- ------------------------ ------------------------
  Read source             Yes, subject to          Yes
                          repository visibility    

  Run lint/unit tests     Yes                      Yes

  Use public package      Controlled/allowlisted   Controlled/allowlisted
  sources                                          

  Access release signing  **No**                   Only the isolated
  key                                              signing step

  Write release registry  **No**                   Narrow repository/scope

  Reuse trusted cache     **No**                   Only documented trusted
                                                   cache

  Change protected        No                       Through reviewed release
  release ref                                      process

  Deploy to cluster       No                       Through GitOps/promotion
                                                   process

  Access production       No                       Not needed for local
  secrets                                          capstone

  Use Docker              No by default            Only if justified and
  socket/privileged                                isolated; prefer
  builder                                          rootless supported build
  -------------------------------------------------------------------------

### 10.2 CI configuration rules

-   Use ephemeral or short-lived runners where feasible.
-   Do not expose the host Docker socket to untrusted jobs.
-   Keep caches separate across untrusted and trusted trust domains.
-   Pin CI actions/plugins by immutable commit or digest where the
    provider supports it.
-   Minimize workflow permissions and job-level credentials.
-   Protect release branches/tags and require review/environment
    approval.
-   Restrict egress where feasible and document package endpoints.
-   Verify tool downloads/checksums/signatures using the official
    release procedure.
-   Do not assume a local CI simulation proves hosted provider
    isolation.

**\[VERIFY\]** OIDC claim names, workflow permission syntax, runner
isolation guarantees, and action pinning behavior are provider- and
version-specific. Check official documentation for the chosen provider
before enabling a real trusted release path.

### 10.3 CI audit script requirements

Create `ci/tests/test_workflow_boundaries.py` or a provider-specific
audit script that flags: - untrusted workflows with write-all
permissions; - secret references in pull-request/fork jobs; - mutable
action/plugin references; - privileged build configuration or Docker
socket mounts; - trusted/untrusted cache namespace overlap; -
signing/promotion steps reachable from unprotected refs; - release job
without an explicit protected-ref condition.

Static checks are heuristics. A script that does not find a pattern does
not prove the workflow is safe. Add positive and negative workflow
fixtures and review the actual provider's effective permissions.

### 10.3a Complete local trust-boundary fixture test

Save as `ci/tests/test_workflow_boundaries.py`. This deliberately
validates a small, provider-neutral JSON fixture model; it is **not** a
parser or proof of any hosted CI provider's effective permissions.

``` python
#!/usr/bin/env python3
"""Provider-neutral negative tests for a simplified release trust model."""
from dataclasses import dataclass

@dataclass
class Job:
    name: str
    ref_class: str
    can_sign: bool = False
    can_promote: bool = False
    has_release_secret: bool = False
    cache_domain: str = "untrusted"

def violations(job: Job) -> list[str]:
    problems = []
    if job.ref_class != "protected" and job.can_sign:
        problems.append("untrusted ref has signing capability")
    if job.ref_class != "protected" and job.can_promote:
        problems.append("untrusted ref has promotion capability")
    if job.ref_class != "protected" and job.has_release_secret:
        problems.append("untrusted ref receives release secret")
    if job.ref_class != "protected" and job.cache_domain == "trusted":
        problems.append("untrusted ref can write/use trusted cache")
    if job.ref_class == "protected" and job.can_sign and not job.can_promote:
        # Signing without an authorized promotion step is allowed only if the
        # design explicitly documents this split; this fixture assumes coupling.
        problems.append("signing capability is not tied to authorized release flow")
    return problems

def expect_rejected(name: str, job: Job) -> None:
    found = violations(job)
    if not found:
        raise AssertionError(f"{name}: expected policy rejection, got allow")
    print(f"PASS negative {name}: {', '.join(found)}")

def main() -> int:
    valid = Job("trusted-release", "protected", True, True, False, "trusted")
    if violations(valid):
        raise AssertionError(f"positive trusted release rejected: {violations(valid)}")
    print("PASS positive trusted release fixture")
    expect_rejected("PR-signing", Job("pr", "untrusted", True, False, False, "untrusted"))
    expect_rejected("PR-promotion", Job("pr", "untrusted", False, True, False, "untrusted"))
    expect_rejected("PR-secret", Job("pr", "untrusted", False, False, True, "untrusted"))
    expect_rejected("cache-crossing", Job("pr", "untrusted", False, False, False, "trusted"))
    safe_pr = Job("pr-safe", "untrusted", False, False, False, "untrusted")
    if violations(safe_pr):
        raise AssertionError(f"safe untrusted validation rejected: {violations(safe_pr)}")
    print("PASS positive untrusted validation has no release capabilities")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

Run `python3 ci/tests/test_workflow_boundaries.py`. Save actual output
under `evidence/ci/`. The test checks a simplified capability model, not
the workflow file's real semantics; a provider-specific static checker
and provider run are still required.

### 10.4 Required benign negative tests

1.  Untrusted ref attempts to invoke the signing step: deny.
2.  A harmless marker artifact is written to an untrusted cache: trusted
    release must not consume it.
3.  A dummy secret file is seeded in a controlled test context:
    untrusted job must not be able to read it.
4.  A job attempts to reach a non-allowlisted endpoint: local
    policy/fixture must reject or record the attempt; do not probe
    third-party systems.
5.  Release from an unprotected ref: deny.
6.  A valid protected-ref fixture with all required review metadata:
    allow.

Use fixture logic if no hosted CI is available. Label provider-specific
enforcement as `OPEN` until tested in that provider.

### 10.5 CI compromise kill-switch drill

-   Stop promotion and disable the release job using the provider's
    documented mechanism.
-   Preserve run logs, source revision, artifact digests, cache
    identifiers, and policy decisions.
-   Revoke/rotate disposable lab credentials or keys if they may have
    been exposed.
-   Mark affected artifacts quarantined and prevent new deployment.
-   Rebuild from a reviewed source revision on a clean trusted path.
-   Verify signatures/provenance and deployment digest before
    re-enabling promotion.
-   Record approvals and recovery evidence.

Do not include real credential theft or actual secret exfiltration in
the drill.

### Acceptance and limits

Acceptance requires separate documented trust paths, no long-lived
registry password in workflow, tests for the five negative cases, and
explicit limits of local simulation. It does not prove a real hosted
runner's isolation or a cloud identity provider's claims.

## 11. Phase 5 --- Signing, attestations, and provenance

### Why this phase exists

A signature establishes that a particular key or signing identity signed
a particular artifact identity. It does not establish that the image is
free of vulnerabilities, that the build was authorized, or that the
claims inside an attestation are true. Those require separate policy
checks and trust in the signer/builder.

### 11.1 Lab-only key management

Use cosign key-based signing with a disposable lab key. **\[VERIFY\]**
Confirm the selected cosign release's key-generation, signing,
verification, and attestation syntax from official documentation.

Typical command shape:

``` bash
cosign generate-key-pair
```

This may prompt for a password and create a private key and public key
in the current directory, depending on the selected version. Follow the
official version's exact behavior. Keep the private key outside Git,
images, logs, and shared evidence. Use a local lab-only password; do not
paste it into the document or shell history. For automation, use an
approved secret input mechanism rather than command-line literals.

### 11.2 Sign the immutable digest

Use the full image reference with `@sha256:<actual-digest>`. Do not sign
a mutable tag as the sole identity.

``` bash
cosign sign --key cosign.key "$IMAGE_BY_DIGEST"
cosign verify --key cosign.pub "$IMAGE_BY_DIGEST"
```

These are representative commands; confirm flags and registry behavior
for the installed version. Save the actual digest and verification
output. If the local registry cannot store signatures/attestations,
document the limitation and use a local fixture only for the affected
portion.

### 11.3 Negative signature tests

-   Unsigned digest: verification must fail.
-   Wrong public key: verification must fail.
-   Tag moved to a different digest: verification of the original digest
    remains about the original object; deployment policy must reject
    tag-only references.
-   Tampered artifact/statement: digest or signature verification must
    fail.
-   Correctly signed but vulnerable image: signature verification may
    pass, but risk policy must reject the release. This is an essential
    demonstration that "signed" does not mean "safe."

### 11.4 Attestation types

Generate separate attestations for: - SBOM; - scan summary; - test
report; - provenance.

Each statement must identify the subject digest. Attestations should be
generated only from the trusted release path. The content must be
derived from actual tool outputs; do not sign a manually invented
"clean" report as if it were measured.

**\[VERIFY\]** Confirm cosign's current attestation command syntax and
the exact predicate types/formats accepted by the installed version.
Keep command lines and generated statement examples separate. Any sample
statement in this document is illustrative, not captured output.

### 11.5 SLSA-style provenance

Use the in-toto Statement envelope and a verified SLSA provenance
predicate/schema. The current SLSA Build Provenance specification uses
the predicate type URI `https://slsa.dev/provenance/v1`; confirm the
schema and current requirement track before relying on it. The official
specification describes provenance as verifiable information about how
an artifact was produced. See the references section.

The policy should consume only fields it validates: - subject artifact
digest; - builder identity; - source repository and immutable
ref/revision; - build type; - relevant external parameters; - resolved
dependencies where the selected schema supports them.

A provenance file merely existing is not authenticity. Verify the
attestation signature and validate the subject digest and required
claims against trusted values. Do not accept arbitrary annotations or
broad regular expressions as proof of trusted origin.

### 11.6 Representative provenance envelope

**\[SYNTHETIC --- REPRESENTATIVE; not generated by a real build\]**

``` json
{
  "_type": "https://in-toto.io/Statement/v1",
  "subject": [
    {
      "name": "localhost/secure-release/inference-api",
      "digest": {
        "sha256": "REPLACE_WITH_ACTUAL_IMAGE_DIGEST_HEX"
      }
    }
  ],
  "predicateType": "https://slsa.dev/provenance/v1",
  "predicate": {
    "buildDefinition": {
      "buildType": "REPLACE_WITH_VERIFIED_BUILD_TYPE_URI",
      "externalParameters": {
        "sourceRepository": "REPLACE_WITH_ACTUAL_REPOSITORY",
        "sourceRef": "REPLACE_WITH_IMMUTABLE_COMMIT"
      },
      "resolvedDependencies": []
    },
    "runDetails": {
      "builder": {
        "id": "REPLACE_WITH_TRUSTED_BUILDER_ID"
      },
      "metadata": {
        "invocationId": "REPLACE_WITH_ACTUAL_RUN_ID"
      }
    }
  }
}
```

This is a schema-oriented teaching shape, not a claim that the object is
fully valid under every current schema revision. Validate it with the
selected official schema/validator and use the exact field semantics
required by that schema. Do not leave placeholder strings in an accepted
attestation.

### 11.7 Verification policy

The local policy should pin: - trusted public key or tightly scoped
signer identity; - artifact digest; - expected source repository and
immutable revision; - expected builder identity; - required predicate
types and subject digest; - required scan/test conditions; - policy
revision and exception state.

A signature alone does not prove build isolation. A valid provenance
statement signed by an untrusted signer is not trusted provenance. A
trusted signer can still sign an unsafe image if the release gate is
defective.

### 11.8 Key rotation and compromise

1.  Pause release signing and promotion.
2.  Preserve key fingerprint, recent artifact digests, and signing
    evidence.
3.  Generate a new disposable lab key and update the explicit trust
    configuration.
4.  Verify that new releases are accepted with the new key.
5.  Verify that a new policy rejects an artifact signed only by the
    retired key, unless a documented migration window intentionally
    allows it.
6.  Re-sign only through a trusted rebuild/reverification process; do
    not silently relabel old artifacts.
7.  Remove the old private key and record destruction/rotation evidence.
8.  Review artifacts signed during the suspected compromise window.

For real production, key custody, revocation, KMS/HSM integration,
access audit, and signer identity are separate architectural concerns
and remain outside this local capstone.

### 11.9 SLSA gap analysis

  ---------------------------------------------------------------------------
  Requirement area  Local evidence        Gap/limitation    Next action
  ----------------- --------------------- ----------------- -----------------
  Artifact subject  Actual digest         Only covers       Bind every
  digest            recorded and checked  tested artifact   release output

  Builder identity  Local builder         Local identifier  Use a documented
                    label/configuration   is not a hosted   trusted builder
                                          trusted-builder   and verify its
                                          guarantee         identity

  Source identity   Commit/ref recorded   Record may be     Bind source
                                          manually asserted identity from
                                                            trusted CI
                                                            context

  Build isolation   Local separate-path   Does not prove    Review provider
                    simulation            multi-tenant      architecture and
                                          isolation         audit evidence

  Provenance        Key-based signature   Key custody is    Use protected
  authenticity      verified locally      local             signing identity
                                                            and managed
                                                            controls in
                                                            production

  Hermeticity       Dependency inputs     Network/build     Improve input
                    documented            environment may   pinning and
                                          remain mutable    restrict network

  SLSA level        No level claimed      Full              Evaluate the
                                          track-specific    current official
                                          requirements not  requirements
                                          independently     against evidence
                                          satisfied         
  ---------------------------------------------------------------------------

Do not claim a SLSA level based on this table alone.

### Acceptance and limits

Acceptance requires digest signing, verification, negative tests,
subject-bound attestations, provenance schema validation,
wrong-key/forged-provenance rejection, and a written trust model. It
does not prove that the build was benign, that the builder is production
trusted, or that the SBOM is complete.

## 12. Phase 6 --- Admission and deployment enforcement

### Why this phase exists

CI is not the only path to a cluster. Admission control evaluates API
requests at deployment time and can reject manifests that bypassed or
drifted from the release process. Admission policy must be staged
carefully: an incorrect enforcement rule can block legitimate rollouts.

### 12.1 Policy decision table

  --------------------------------------------------------------------------------
  Requirement       Desired decision      Positive case       Negative case
  ----------------- --------------------- ------------------- --------------------
  Approved registry Only configured       Approved registry   Unapproved registry
                    local/release         digest              denied
                    registry                                  

  Digest pinning    Require immutable     `name@sha256:...`   Tag-only reference
                    digest reference                          denied

  Signature trust   Require pinned        Correctly signed    Unsigned/wrong
                    trusted key/identity  digest              signer denied

  Attestations      Require expected      Required verified   Missing/mismatched
                    predicates/subject    evidence            subject denied

  Privilege         `privileged: false`   Restricted          Privileged fixture
                    or omitted; reject    container           denied
                    true                                      

  Identity          Non-root UID and no   Explicit non-root   Root/token mount
                    unnecessary token     workload            denied

  Filesystem        Read-only root where  Read-only manifest  Writable root
                    compatible                                rejected when policy
                                                              requires

  Capabilities      Drop all; add only    Drop-all manifest   Unapproved
                    reviewed exceptions                       capability denied

  Init containers   Same image/runtime    Safe init image     Unsafe init image
                    rules as regular                          denied
                    containers                                

  Ephemeral         Cover if allowed by   Approved debug      Unapproved debug
  containers        environment/policy    process             path denied or
                                                              explicitly marked
                                                              OPEN

  Exception         Narrow, owned,        Valid exception     Expired/ownerless
                    expiring                                  exception denied
  --------------------------------------------------------------------------------

### 12.2 Engine strategy

1.  **VAP baseline:** use Kubernetes ValidatingAdmissionPolicy (VAP)
    where the selected cluster supports it. Kubernetes documentation
    identifies VAP as stable since Kubernetes v1.30; verify your server
    version and API before use.
2.  **Kyverno authoring:** exercise in a disposable cluster after VAP
    work.
3.  **Gatekeeper authoring:** exercise in a separate disposable cluster
    after Kyverno is removed and cleanup verified.
4.  Never install Kyverno and Gatekeeper together in this constrained
    capstone.

The capstone should compare the engine implementations but must not
claim all three were live-tested if one was fixture-only.

### 12.3 Representative VAP baseline

The following is a **policy shape**, not a complete
signature/attestation verifier. Native VAP CEL checks can enforce
manifest fields; image signature and provenance verification usually
require an external verifier or a policy engine integration that
supports those checks. **Do not claim VAP alone verifies cosign
signatures unless a concrete supported integration is implemented and
tested.**

**\[VERIFY\]** Validate API versions, expression syntax, matching rules,
and `validationActions` against the selected Kubernetes server version.
Apply to a disposable namespace first.

``` yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicy
metadata:
  name: secure-release-baseline
spec:
  failurePolicy: Fail
  matchConstraints:
    resourceRules:
      - apiGroups: ["apps"]
        apiVersions: ["v1"]
        operations: ["CREATE", "UPDATE"]
        resources: ["deployments"]
  validations:
    - expression: "object.spec.template.spec.containers.all(c, c.image.matches('^localhost/secure-release/[^@]+@sha256:[a-f0-9]{64}$'))"
      message: "Containers must use an approved repository and immutable SHA-256 digest."
    - expression: "object.spec.template.spec.containers.all(c, has(c.securityContext) && has(c.securityContext.runAsNonRoot) && c.securityContext.runAsNonRoot)"
      message: "All application containers must explicitly run as non-root."
    - expression: "object.spec.template.spec.containers.all(c, has(c.securityContext) && has(c.securityContext.allowPrivilegeEscalation) && !c.securityContext.allowPrivilegeEscalation)"
      message: "Privilege escalation must be disabled."
    - expression: "!has(object.spec.template.spec.hostNetwork) || !object.spec.template.spec.hostNetwork"
      message: "Host networking is not allowed."
---
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicyBinding
metadata:
  name: secure-release-baseline
spec:
  policyName: secure-release-baseline
  validationActions: [Deny]
  matchResources:
    namespaceSelector:
      matchLabels:
        secure-release-lab: "true"
```

**Important review items:** this sample intentionally shows only a
baseline for Deployment regular containers. Before calling it complete,
add equivalent checks for init containers, relevant workload kinds,
pod-level token mounting, capabilities, read-only filesystem, and
supported update paths; test every path. CEL expression type checking
may reject expressions depending on the server version and available CEL
functions. Do not apply until `kubectl` server-side validation and
fixture tests succeed. The `localhost` registry pattern is lab-specific
and must be changed only through reviewed policy edits.

### 12.4 Kyverno and Gatekeeper

Provide separate policy directories and tests. For Kyverno, test image
digest, registry, signature identity/key, and attestations only with the
current verified `verifyImages` API supported by the installed version.
For Gatekeeper, test declarative manifest constraints with a
ConstraintTemplate and Constraint. **\[VERIFY\]** Check current policy
API versions, image-verification support, Rego/CEL integration, and test
commands in official docs. Do not copy old versioned examples without
verifying compatibility.

At minimum, policy tests must cover: - valid release; - unsigned
image; - wrong signer/key; - missing attestation; - subject digest
mismatch; - tag-only image; - unapproved registry; - privileged/root
configuration; - service-account token mounting; - unsafe init
container; - broad opt-out label; - exception expiry.

### 12.4a Policy-engine comparison matrix

  ---------------------------------------------------------------------------------------------
  Engine            Intended role in this capstone        What to             Important gap
                                                          implement/test      
  ----------------- ------------------------------------- ------------------- -----------------
  Kubernetes VAP    Native CEL manifest baseline          Digest/registry     Does not by
                                                          shape and selected  itself fetch and
                                                          pod security        verify cosign
                                                          fields;             signatures or
                                                          create/update       SLSA attestations
                                                          behavior;           
                                                          valid/invalid       
                                                          fixtures            

  Kyverno           Policy authoring and, if verified for Registry/digest     Exact API fields
                    the chosen release, image             policy,             and behavior vary
                    signature/attestation verification    `verifyImages`      by release; use
                                                          trust identity,     official docs
                                                          required            matching
                                                          attestation,        installed version
                                                          exception expiry,   
                                                          positive/negative   
                                                          manifests           

  OPA Gatekeeper    ConstraintTemplate/Constraint-based   Non-root,           Cryptographic
                    manifest validation                   privileged, token,  artifact
                                                          registry/digest     verification is
                                                          patterns and bypass not automatically
                                                          cases               provided by a
                                                                              basic manifest
                                                                              constraint

  Fixture-only      Offline logic checks when             Valid and invalid   Does not prove
  adapter           cluster/engine unavailable            YAML/JSON fixtures; API-server
                                                          stable test IDs and admission,
                                                          expected decisions  webhook health,
                                                                              or
                                                                              engine-specific
                                                                              semantics
  ---------------------------------------------------------------------------------------------

Record `LIVE`, `FIXTURE ONLY`, or `NOT RUN` per engine. Never mark the
matrix complete based on the presence of YAML alone.

### 12.5 Bypass analysis

Check: - regular containers **and** init containers; - all workload
kinds permitted in the target namespace; - update operations as well as
create; - ephemeral containers and debug permissions where available; -
registry patterns anchored to the full expected path; - opt-out labels
that are not freely settable by workload authors; - policy-engine RBAC,
webhook reachability, and failure behavior; - GitOps reconciliation and
RBAC so ad hoc manual `kubectl` is not the normal production path.

### 12.6 Staged rollout and rollback

1.  **Audit:** observe policy decisions without blocking, where
    supported.
2.  **Warn:** surface violations to owners and correct manifests.
3.  **Enforce:** apply to a narrow lab namespace only after
    positive/negative tests pass.
4.  **Rollback:** remove the binding or switch the policy to the
    pre-reviewed non-blocking state using the documented engine
    mechanism; verify cluster health.
5.  **Kill switch:** release owner can stop promotion; cluster admin can
    disable only the lab policy after recording the reason and time.

`failurePolicy: Fail` is fail-closed for matching evaluation errors but
may reduce availability if the policy path is unhealthy. `Ignore` trades
enforcement strength for availability. Choose deliberately and document
the threat/availability trade-off. Do not enable enforcement globally on
a production cluster as part of this exercise.

### 12.7 Exception-as-code

Each exception must include owner, reason, exact namespace/workload or
policy scope, expiry, compensating control, approver, and exit
condition. Test expired exceptions. Check whether exception
labels/annotations can be set by the same principal being constrained;
if so, the exception design may be bypassable.

### 12.8 Cleanup proof

After each engine exercise: - remove lab policy bindings, policies,
webhooks, constraints, and controller installation; - inspect the API
for remaining objects; - confirm no blocking webhook or policy
remains; - save the cleanup output; - only then start the next policy
engine.

### Acceptance and limits

Acceptance requires a valid manifest to pass and prohibited fixtures to
be rejected, plus an engine comparison matrix and cleanup proof. A
fixture-only policy test does not prove live admission. VAP baseline
field checks do not prove image authenticity unless a separately
implemented trusted verifier is actually invoked.

## 13. Phase 7 --- Runtime hardening and network boundaries

### Why this phase exists

Supply-chain controls reduce the chance of deploying an unsafe artifact.
Runtime hardening limits the consequences if an application or
dependency is compromised. It does not replace identity authorization,
data access controls, or detection.

### 13.1 Deployment baseline

Apply these settings where compatible: - explicit non-root UID/GID; -
`allowPrivilegeEscalation: false`; - read-only root filesystem; - drop
all Linux capabilities, adding only a reviewed capability if strictly
required; - seccomp profile such as `RuntimeDefault` when supported; -
CPU/memory requests and limits selected for the actual workload; -
liveness/readiness/startup probes appropriate to the application; -
explicit service account; - `automountServiceAccountToken: false` unless
Kubernetes API access is required; - no host PID/network/IPC or hostPath
by default; - no privileged containers; - resource quotas and namespace
separation; - explicit writable paths using `emptyDir` or a dedicated
volume; - restrictive egress and ingress.

**\[VERIFY\]** Kubernetes field support and Pod Security Standards
behavior depend on the server version and runtime. Confirm with the
official docs for the selected cluster.

### 13.2 Representative deployment fragment

``` yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: inference-api
  namespace: secure-release-lab
  labels:
    app.kubernetes.io/name: inference-api
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: inference-api
  template:
    metadata:
      labels:
        app.kubernetes.io/name: inference-api
    spec:
      serviceAccountName: inference-api
      automountServiceAccountToken: false
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
        runAsGroup: 10001
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: api
          image: localhost/secure-release/inference-api@sha256:REPLACE_WITH_ACTUAL_DIGEST
          ports:
            - name: http
              containerPort: 8080
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop: ["ALL"]
          resources:
            requests:
              cpu: "50m"
              memory: "64Mi"
            limits:
              cpu: "500m"
              memory: "256Mi"
          readinessProbe:
            httpGet:
              path: /healthz
              port: http
            initialDelaySeconds: 2
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /healthz
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
```

Replace the digest placeholder with the actual digest before use. The
resource values are \[ILLUSTRATIVE\] starting points only; measure and
tune. Do not apply a manifest with placeholder digest.

### 13.3 NetworkPolicy

A default-deny policy is useful only if the cluster's CNI enforces
NetworkPolicy. Verify enforcement with a benign connectivity test; a
policy object existing is not proof. Start with default-deny
ingress/egress, then allow only required traffic such as DNS and the
API's known ingress source. DNS details and namespace selectors depend
on the cluster setup.

**\[VERIFY\]** NetworkPolicy semantics and CNI support must be tested on
the actual `kind`/local cluster version and network plugin. If
enforcement is unavailable, record network controls as `OPEN` and use a
separate supported lab/fixture test.

### 13.4 Workload trust tiers

  -----------------------------------------------------------------------------
  Workload         Identity       Data access     Network        Runtime
  ---------------- -------------- --------------- -------------- --------------
  Inference API    Dedicated      Only approved   Narrow         Non-root,
                   service        model/version   ingress;       read-only
                   account; token                 minimal egress root, probes
                   off unless                                    
                   needed                                        

  ETL job          Dedicated job  Synthetic       No egress      Non-root, no
                   identity       input/output    unless         token by
                                  only in lab     explicitly     default
                                                  required       

  Notebook-style   Separate       No production   No broad       Interactive
  image            namespace and  data in         egress;        trust tier, no
                   identity       capstone        controlled     release
                                                  access only    credentials
  -----------------------------------------------------------------------------

### 13.5 Benign compromise-response drill

Use only a disposable lab workload and a dummy identity: 1. Record
workload namespace/name, image digest, labels, owner, and recent
release. 2. Preserve pod description, events, relevant logs, and
audit/runtime alert evidence. 3. Apply a lab quarantine policy/label or
NetworkPolicy to isolate the workload. Verify the actual CNI enforces
it. 4. Rotate/revoke only dummy lab credentials if the scenario requires
it. 5. Replace the workload from a verified digest and known-good
deployment manifest. 6. Confirm readiness, intended network behavior,
and absence of the original suspect digest. 7. Record recovery evidence
and remaining uncertainty.

Do not delete the pod or its evidence before capture unless containment
requires it to stop immediate harm; if termination is necessary, record
why and preserve available evidence first.

### Acceptance and limits

Acceptance requires positive workload startup, negative policy denials,
token-mount verification, read-only filesystem test, non-root runtime
identity, and network connectivity tests. If NetworkPolicy enforcement
is not demonstrated, the egress-control acceptance remains `OPEN`. These
controls reduce blast radius but do not prove application-level
authorization or prevent all data leakage.

## 14. Phase 8 --- Runtime detection and audit correlation

### Why this phase exists

Prevention can fail, and a quiet alert stream can mean either no
suspicious activity or a broken sensor. Runtime detection and Kubernetes
audit evidence provide additional signals but must be correlated to
artifact identity and sensor health.

### 14.1 Falco feasibility preflight

Before installing or starting Falco, record: - OS and kernel version; -
whether running under WSL2, native Linux, or VM; - container runtime; -
kernel headers/BTF/driver support as required by the selected Falco
version; - chosen driver/source and installation method; - resource
budget; - whether the event stream can be tested with a benign rule.

**\[VERIFY\]** Driver options, kernel/BTF support, rule fields, plugins,
outputs, metrics, and replay support are release-sensitive. Consult the
official Falco documentation for the installed version. Do not attempt
to bypass kernel protections or use unsupported driver hacks.

Decision: - If live Falco is supported, run a bounded local lab and save
actual events. - If unsupported, use rule-authoring, syntax validation,
and synthetic fixture correlation. Mark live kernel detection `NOT RUN`;
do not claim the rules detected anything live.

### 14.2 Custom rule catalog

Create at least ten rules or a justified smaller runnable subset plus
fixtures for all ten. The intent catalog below is version-neutral; map
each intent to the exact field/operator syntax supported by the chosen
Falco release and validate it before running.

  ---------------------------------------------------------------------------
  ID                Detection intent      Benign test       Negative test /
                                                            tuning
  ----------------- --------------------- ----------------- -----------------
  FAL-01            Shell/process starts  Run an approved   Normal approved
                    in a production-like  shell marker      process should
                    container             command in        not alert
                                          disposable lab    
                                          only              

  FAL-02            Unexpected write to   Write a harmless  Write to approved
                    protected path        marker in a       temp path should
                                          lab-only          not alert
                                          protected-path    
                                          fixture           

  FAL-03            Package manager/tool  Execute a benign  Normal app
                    execution at runtime  version/help      startup should
                                          command in a      not alert
                                          disposable image  
                                          with tool present 

  FAL-04            Sensitive token path  Fixture event     Expected no-token
                    access                records attempted workload emits no
                                          access to a dummy such event
                                          token path; do    
                                          not read real     
                                          tokens            

  FAL-05            Unexpected outbound   Local-only        Approved local
                    connection            connection to a   health traffic
                                          listener inside   should not alert
                                          the same lab      
                                          network           

  FAL-06            Unexpected binary     Execute a         Approved
                    execution             harmless known    entrypoint should
                                          test binary in    not alert
                                          the disposable    
                                          lab               

  FAL-07            Privileged/identity   Synthetic         Safe pod create
                    configuration change  Kubernetes audit  should not alert
                                          event shows       
                                          privileged pod    
                                          request           

  FAL-08            Admission denial /    Synthetic or live Valid release
                    bypass attempt        audit record for  should not be
                                          denied manifest   classified as
                                                            bypass

  FAL-09            Sensor process        Stop/restart only Expected
                    restart or            lab sensor under  heartbeat remains
                    unavailable stream    supervision       fresh when sensor
                                                            healthy

  FAL-10            Unexpected            Marker event      Known baseline
                    write/process after   correlated to new event should not
                    release change        digest            trigger
                                                            high-severity
                                                            alert
  ---------------------------------------------------------------------------

Rule metadata should include a stable rule ID, description, priority,
tags, threat-model reference, runbook path, test fixture, owner, tuning
notes, and exception expiry if applicable. Do not copy a rule from a
different Falco version without verifying its fields and macro
dependencies.

### 14.3 Six default-rule observations

If live Falco is available, collect at least six benign default-rule
observations from the selected distribution's shipped rule set. Record
the exact rule names and configuration that were actually observed; do
not invent rule names in advance. If live Falco is unavailable, use six
fixture events and mark live default-rule observations `NOT RUN`.

### 14.4 Fixture schema

Use JSON Lines in `detection/fixtures/events.jsonl`. Example:

``` json
{"event_id":"FIX-001","status":"SYNTHETIC","sensor_mode":"fixture","timestamp":"FILL_AT_RUN","rule_id":"FAL-01","workload":"inference-api","image_digest":"sha256:REPLACE_WITH_ACTUAL_OR_FIXTURE_DIGEST","namespace":"secure-release-lab","summary":"Benign marker process event","expected":"DETECT"}
{"event_id":"FIX-002","status":"SYNTHETIC","sensor_mode":"fixture","timestamp":"FILL_AT_RUN","rule_id":"FAL-05","workload":"etl-job","image_digest":"sha256:REPLACE_WITH_ACTUAL_OR_FIXTURE_DIGEST","namespace":"secure-release-lab","summary":"Approved local health connection","expected":"NO_ALERT"}
```

These records are fixtures. Replace timestamps and digests only when
actual values exist. Keep a `fixture` label through downstream
dashboards so synthetic events cannot be confused with production
telemetry.

### 14.5 Correlation fields

Correlate alert with: - event timestamp and sensor identity/health; -
namespace, pod/workload, container; - actual image digest and deployment
revision; - SBOM inventory reference and scan status; -
signature/provenance verification decision; - owner/on-call route; -
recent release or policy change; - incident ID and runbook.

### 14.6 Optional observability path

If the laptop can support it, use a local path such as JSON →
collector/Falcosidekick → Loki → Grafana → Alertmanager → M10 incident
workflow. Exact component versions, endpoints, metric names, and
LogQL/PromQL syntax must be verified against the installed release. Do
not install a full stack if it risks exhausting the laptop. Fixture
parsing and a local JSON summary are acceptable for the core capstone
but do not demonstrate the live stack.

### 14.7 Sensor health and tampering drill

Define a heartbeat or health check supported by the selected
sensor/exporter. Test: - healthy sensor produces a fresh heartbeat; -
stale/missing heartbeat creates a health alert or explicit
`INCONCLUSIVE`; - empty alert stream with stale heartbeat is not treated
as "no threat"; - benign sensor restart is recorded; - after restart,
event generation and delivery are verified.

Do not assume a specific metric exists until checked in official docs.
If no native health metric is available, build a documented external
process/heartbeat check and label it as such.

### 14.8 Runtime triage runbook

1.  Validate the alert and its source; check sensor health.
2.  Identify workload and exact digest.
3.  Correlate scan, SBOM, provenance, deployment owner, and recent
    release.
4.  Scope affected pods/namespaces and preserve logs/events/audit
    evidence.
5.  Contain using a reviewed lab quarantine procedure.
6.  Rotate dummy credentials if relevant.
7.  Replace the workload from a verified digest and reviewed manifest.
8.  Confirm recovery and monitor.
9.  Record detection/containment times only if measured.
10. Tune the rule with owner and expiry; never silently suppress it.

### Acceptance and limits

Acceptance requires rule metadata validation, fixture positive/negative
tests for all ten intents, sensor-health logic, and a scorecard. Live
detection is accepted only if a supported sensor actually produced the
evidence. Fixture success is not live kernel detection.

## 15. Phase 9 --- Findings, exceptions, and evidence lifecycle

### Why this phase exists

Security findings become operational work only when they have owners,
decisions, due dates, and closure evidence. A merged patch is not proof
that the deployed digest is fixed.

### 15.1 Finding lifecycle

`new → triaged → assigned → remediating / mitigated / accepted / not-affected → re-scanned/re-verified → closed`

A finding cannot move directly to `closed` merely because a PR merged.
Re-scan the released digest and verify the relevant policy again.

### 15.2 Normalized finding schema

``` json
{
  "finding_id": "SYN-001",
  "artifact_digest": "sha256:REPLACE_WITH_ACTUAL_OR_FIXTURE_DIGEST",
  "source": "Trivy-or-fixture",
  "component": "synthetic-component",
  "advisory_reference": "SYN-ADVISORY-2026-001",
  "severity": "Critical",
  "exposure": "internet-facing inference API (scenario)",
  "reachability": "evidence attached or explicitly unknown",
  "fixability": "fix available",
  "asset_criticality": "High",
  "owner": "named-owner",
  "due_date": "YYYY-MM-DD",
  "decision": "remediate",
  "evidence_links": ["evidence/scans/"],
  "state": "triaged",
  "last_verified": "NOT RUN"
}
```

The synthetic advisory ID is not a real CVE. Populate actual fields only
from observed evidence.

### 15.3 Illustrative remediation SLAs

These are **\[ILLUSTRATIVE\] policy examples**, not universal industry
requirements: - Critical and exposed with a fix: immediate triage,
release block, remediation owner assigned the same working day. - High
and exposed: expedited triage and a short, explicit due date selected by
the service owner. - No-fix critical/high: documented mitigation,
exposure reduction, exception expiry, and scheduled re-evaluation. - Low
or build-only: prioritize based on actual risk and builder exposure, not
solely severity.

Choose actual targets based on asset criticality, risk appetite,
operational capacity, and legal/customer obligations. Record them in
policy and review them periodically.

### 15.4 Exception validation

An exception registry entry must contain owner, rationale, exact scope,
compensating controls, expiry, review date, and exit condition. The
validator must reject: - missing owner; - missing rationale; - malformed
or impossible date; - expired exception; - broad wildcard scope without
justification; - no exit condition; - an exception that has no linked
threat/control.

### 15.5 Metrics that drive action

Track: - scan freshness and DB state; - running-digest coverage by
workload; - findings by exposure, fixability, severity, and age; - time
to remediate (only from recorded timestamps); - exceptions by age and
owner; - signature/attestation verification failures; - policy denials
and false-positive review; - detection coverage against threat model; -
sensor heartbeat freshness and event delivery; - percentage of accepted
criteria with executed evidence.

Do not use "zero findings" as the only success metric. It can mean
incomplete inventory, stale databases, suppressions, or broken scanning.

### 15.6 Evidence index

Create `audit/evidence-index.md` with one row per acceptance criterion:

  -----------------------------------------------------------------------------------------------------------------
  Criterion   Command/test       Result   Timestamp   Tool/version   Artifact   Evidence   Limitations    Owner
  ID                                      UTC                        digest     path                      
  ----------- ------------------ -------- ----------- -------------- ---------- ---------- -------------- ---------
  PRE-01      `make preflight`   NOT RUN                                                   Fill after     learner
                                                                                           execution      

  IMG-01      image              NOT RUN                                                   Build platform learner
              build/inspection                                                             matters        

  SCAN-01     Trivy scans        NOT RUN                                                   DB freshness   learner
                                                                                           must be        
                                                                                           recorded       

  SBOM-01     SPDX/CycloneDX     NOT RUN                                                   Completeness   learner
              generation                                                                   limitations    

  SIG-01      cosign verify      NOT RUN                                                   Local key      learner
                                                                                           trust only     

  ADM-01      admission tests    NOT RUN                                                   Live cluster   learner
                                                                                           required       

  DET-01      Falco/fixture      NOT RUN                                                   Clearly label  learner
              tests                                                                        fixture vs     
                                                                                           live           

  IR-01       incident drill     NOT RUN                                                   Times must be  learner
                                                                                           measured       
  -----------------------------------------------------------------------------------------------------------------

### Acceptance and limits

Acceptance requires finding lifecycle, expiring exception checks,
evidence index, and risk-based metrics. A complete evidence index
documents what is known; it does not independently validate the truth of
every underlying claim.

## 16. Phase 10 --- Benign adversary-emulation suite

### 16.1 Rules of engagement

-   Run only against this learner-owned disposable lab or fixture files.
-   Use synthetic IDs and dummy values.
-   No exploit payloads, malware, real credentials, third-party
    scanning, or destructive cluster operations.
-   Tests should prove a defensive control blocks, detects, or
    explicitly fails closed.
-   Each result is `PASS`, `FAIL`, `NOT RUN`, or `INCONCLUSIVE`.
-   `NOT RUN` is never counted as a pass.
-   Record detection/blocking time only if measured with actual
    timestamps.

### 16.2 Test inventory

  -----------------------------------------------------------------------------------------------------------------------------------------------------------------
  ID          Threat/control       Benign setup and exact test                           Expected outcome   Evidence                            Cleanup /
                                                                                                                                                limitation
  ----------- -------------------- ----------------------------------------------------- ------------------ ----------------------------------- -------------------
  ADV-01      Untrusted ref        Run local workflow-policy test with                   Denied; no signing `evidence/ci/ADV-01.log`            Remove fixture
              attempts release     `ref_type=untrusted`;                                 capability                                             output; local
              promotion            `python3 ci/tests/test_workflow_boundaries.py`                                                               simulation does not
                                   \[script to create\]                                                                                         prove provider
                                                                                                                                                isolation

  ADV-02      Mutable image        Submit fixture manifest with `image: ...:latest` to   Denied             `evidence/admission/ADV-02.log`     No cluster mutation
              reference            manifest policy test                                                                                         required in fixture
                                                                                                                                                mode

  ADV-03      Unsigned image       Run                                                   Nonzero            `evidence/signatures/ADV-03.log`    Do not treat
                                   `cosign verify --key cosign.pub "$UNSIGNED_DIGEST"`   verification                                           command output as
                                   using a real disposable local artifact                result                                                 observed until run

  ADV-04      Wrong signing key    Verify signed digest using a separately generated     Rejected           `evidence/signatures/ADV-04.log`    Delete temporary
                                   wrong public key                                                                                             wrong private key
                                                                                                                                                after evidence
                                                                                                                                                review

  ADV-05      Missing/mismatched   Policy fixture has no required predicate or wrong     Denied             `evidence/provenance/ADV-05.json`   Fixture result does
              attestation          subject digest                                                                                               not prove registry
                                                                                                                                                integration

  ADV-06      Wrong provenance     Mutate fixture source ref/builder ID and verify       Denied             `evidence/provenance/ADV-06.json`   Do not sign false
              source/builder       policy                                                                                                       claims as actual
                                                                                                                                                provenance

  ADV-07      Synthetic            Feed `SYN-001` into risk gate                         Release blocked or `evidence/scans/ADV-07.json`        Synthetic only
              critical/fixable                                                           explicit approved                                      
              finding                                                                    mitigation                                             
                                                                                         required                                               

  ADV-08      Stale vulnerability  Mark scan metadata stale in test fixture              Gate fails as      `evidence/scans/ADV-08.json`        Must separately
              DB                                                                         current scan                                           test actual DB
                                                                                                                                                freshness in live
                                                                                                                                                mode

  ADV-09      Unjustified VEX      Fixture VEX lacks justification/evidence              Validator rejects  `evidence/scans/ADV-09.json`        VEX schema support
              suppression                                                                                                                       version-sensitive

  ADV-10      InitContainer bypass Manifest has unsafe init container and safe app       Denied             `evidence/admission/ADV-10.log`     Cover live engine
                                   container                                                                                                    only if run

  ADV-11      Privileged/root      Manifest requests privileged mode or root UID         Denied             `evidence/admission/ADV-11.log`     Never run a
              configuration                                                                                                                     privileged workload

  ADV-12      Unneeded             Manifest enables automount without approved need      Denied             `evidence/admission/ADV-12.log`     Validate exceptions
              service-account                                                                                                                   separately
              token                                                                                                                             

  ADV-13      Unexpected egress    Attempt a local-only connection that policy should    Blocked if CNI     `evidence/runtime/ADV-13.log`       Never contact a
                                   block                                                 enforcement is                                         third-party
                                                                                         live; otherwise                                        endpoint
                                                                                         fixture `NOT RUN`                                      
                                                                                         for network                                            

  ADV-14      Marker-based         Emit benign marker event or fixture record            Detection or       `evidence/runtime/ADV-14.json`      No persistence;
              unexpected                                                                 fixture                                                delete marker after
              write/process                                                              correlation                                            evidence
                                                                                         succeeds                                               

  ADV-15      Runtime sensor       Mark sensor heartbeat stale or stop only disposable   Health check       `evidence/runtime/ADV-15.json`      Fixture mode does
              unavailable          lab sensor                                            alerts or returns                                      not prove live
                                                                                         explicit                                               sensor health
                                                                                         inconclusive; not                                      
                                                                                         "no threat"                                            

  ADV-16      Expired exception    Add expired date to test-only exception fixture       Validator fails    `evidence/audit/ADV-16.log`         Do not expire the
                                                                                                                                                canonical accepted
                                                                                                                                                exception unless
                                                                                                                                                intended

  ADV-17      Unapproved registry  Fixture uses unapproved registry                      Policy denies      `evidence/admission/ADV-17.log`     Fixture or live
                                                                                                                                                admission must be
                                                                                                                                                distinguished

  ADV-18      Tampered             Change a copy of a signed statement or test digest    Signature/digest   `evidence/signatures/ADV-18.log`    Never mutate a
              artifact/statement   fixture                                               verification fails                                     production artifact

  ADV-19      Broad opt-out label  Add an untrusted `skip-policy=true` label             Denied or label    `evidence/admission/ADV-19.log`     Policy authorship
                                                                                         ignored                                                and RBAC review
                                                                                                                                                required

  ADV-20      Positive control     Valid digest, trusted signature, required evidence,   Accepted           `evidence/admission/ADV-20.log`     Must be run after
                                   non-root manifest                                                                                            negative cases;
                                                                                                                                                valid release must
                                                                                                                                                remain possible
  -----------------------------------------------------------------------------------------------------------------------------------------------------------------

### 16.3 Scorecard

Create `sim/scorecard/results.csv`:

``` csv
test_id,control,mode,result,observed_at_utc,block_or_detect_time_seconds,evidence,limitation,owner
ADV-01,untrusted-release-boundary,fixture,NOT RUN,,,evidence/ci/ADV-01.log,Local simulation only,learner
ADV-02,digest-pinning,fixture,NOT RUN,,,evidence/admission/ADV-02.log,Live admission not implied,learner
ADV-03,signature-verification,live,NOT RUN,,,evidence/signatures/ADV-03.log,Requires actual signed and unsigned local artifacts,learner
ADV-20,positive-release-control,fixture,NOT RUN,,,evidence/admission/ADV-20.log,Live admission not implied,learner
```

Add a row for every test. Allowed result values are exactly `PASS`,
`FAIL`, `NOT RUN`, and `INCONCLUSIVE`. Add a validator that rejects
unknown result values and any attempt to summarize `NOT RUN` as pass.
Leave times blank unless measured.

### 16.3a Complete scorecard validator

Save as `sim/scorecard/validate_scorecard.py`. It checks that all 20
required test IDs are present and that statuses are valid; it does not
convert a skipped test into a pass.

``` python
#!/usr/bin/env python3
import csv
import sys
from pathlib import Path

REQUIRED = {f"ADV-{i:02d}" for i in range(1, 21)}
ALLOWED = {"PASS", "FAIL", "NOT RUN", "INCONCLUSIVE"}

def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "sim/scorecard/results.csv")
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
    except OSError as exc:
        print(f"FAIL: cannot read scorecard: {exc}")
        return 2
    errors = []
    seen = set()
    for row in rows:
        test_id = row.get("test_id", "")
        status = row.get("result", "")
        if test_id in seen:
            errors.append(f"duplicate test_id {test_id}")
        seen.add(test_id)
        if status not in ALLOWED:
            errors.append(f"{test_id}: invalid result {status!r}")
        if status == "PASS" and not row.get("evidence", "").strip():
            errors.append(f"{test_id}: PASS requires evidence path")
        if status == "PASS" and not row.get("observed_at_utc", "").strip():
            errors.append(f"{test_id}: PASS requires observed timestamp")
    missing = sorted(REQUIRED - seen)
    extra = sorted(seen - REQUIRED)
    if missing:
        errors.append("missing required tests: " + ", ".join(missing))
    if extra:
        errors.append("unexpected test IDs: " + ", ".join(extra))
    if errors:
        for error in errors:
            print("FAIL:", error)
        return 1
    counts = {status: sum(1 for row in rows if row["result"] == status) for status in sorted(ALLOWED)}
    print("Scorecard structurally valid; statuses are not independently verified.")
    print("Counts:", counts)
    if counts["FAIL"] or counts["NOT RUN"] or counts["INCONCLUSIVE"]:
        print("Overall status: OPEN (not all tests passed)")
        return 1
    print("Overall status: all listed tests PASS; human evidence review still required")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

Run `python3 sim/scorecard/validate_scorecard.py`. A structurally
complete starter scorecard should return nonzero while tests remain
`NOT RUN`. A structurally valid CSV is not proof the underlying evidence
is truthful; review evidence paths and timestamps.

### 16.4 Positive control requirements

At least one valid image must pass build, scan-policy, SBOM, signature,
provenance, manifest, and admission checks. If a required live subsystem
is unavailable, mark that portion `NOT RUN` and the end-to-end chain
`INCONCLUSIVE` or `OPEN`, not passed.

### Acceptance

All 20 tests have stable IDs, preconditions, expected outcomes, evidence
paths, and cleanup. The learner must fill observed results only after
running them. A test catalog alone is not evidence of detection or
blocking.

## 17. Incident exercise and blameless postmortem

### 17.1 Scenario A --- synthetic advisory or provenance discrepancy

**\[SYNTHETIC\]** An internal synthetic advisory `SYN-ADVISORY-2026-001`
may affect a component included in one released image, or the provenance
statement's source revision does not match the approved release record.
The team cannot immediately determine whether the running inference
service is affected.

#### Declaration criteria

Declare a lab incident when one or more of these conditions occur: - a
synthetic critical/fixable finding maps to a running digest; - signature
or provenance verification disagrees with release metadata; - inventory
cannot determine affected workloads within the agreed decision window; -
an artifact appears to have been promoted from an untrusted path.

Roles: - Incident lead: coordinates decisions and timeline. - Release
owner: stops promotion and identifies releases. - Security investigator:
validates finding/signature/provenance. - Platform/SRE responder: scopes
workloads and containment. - Communications owner: maintains a concise
status log. - Note taker: captures timestamps, commands, and evidence
paths.

One learner may fill multiple roles in the local exercise, but document
that the role separation is simulated.

#### First actions

1.  Pause promotion using the lab kill switch.
2.  Preserve the release commit, image digest, signature verification
    output, provenance statement, scan report, SBOM, manifest, admission
    decision, and relevant logs.
3.  Do not delete evidence or rebuild over the original artifact.
4.  Query the digest-indexed SBOM inventory to identify affected image
    digests.
5.  Map those digests to running workloads using observed cluster state,
    not mutable tags.
6.  Determine whether the evidence is authentic and current; if not,
    mark the conclusion `INCONCLUSIVE`.
7.  Choose containment proportionate to the risk: quarantine the
    affected lab workload, block new deployment, or roll back to a
    verified known-good digest.
8.  Rotate only dummy lab identities if they may be compromised.
9.  Verify recovery and record the decision.

#### Affected-image query

The query must return image digest, component/version, SBOM path, scan
state, and deployed workload references. If SBOMs are missing or
malformed, the result must be `INCONCLUSIVE`, not "not affected." Do not
fabricate affected-image output; capture the actual query result.

#### Decision log template

  ------------------------------------------------------------------------------
  UTC time    Actor/role   Decision/action   Evidence    Rationale   Follow-up
                                             path                    owner
  ----------- ------------ ----------------- ----------- ----------- -----------
                           Promotion paused                          

                           Affected digest                           
                           identified /                              
                           inconclusive                              

                           Containment                               
                           selected                                  

                           Credential                                
                           rotation decision                         

                           Recovery verified                         
                           / open                                    
  ------------------------------------------------------------------------------

### 17.2 Scenario B --- missing sensor or policy engine

A deployment appears to have no runtime alerts, but the sensor heartbeat
is stale or a policy webhook is unreachable. The responder must
distinguish: - **No alert observed with healthy telemetry**; - **Sensor
unhealthy / event stream stopped**; - **Policy evaluation not reached or
inconclusive**; - **Policy denied the request**.

Do not interpret absence of alerts as absence of risk. Pause promotion
if the control is a required release gate and its health cannot be
established. Preserve controller/webhook status, API events, sensor
heartbeat, and timestamps before restarting or deleting components.

### 17.3 Timeline fields

Record actual times only:

``` text
Incident ID:
Scenario:
Declared at UTC:
Promotion stopped at UTC:
Evidence preserved at UTC:
Affected digests identified at UTC:
Containment started/completed UTC:
Credential rotation decision and UTC:
Known-good replacement deployed UTC:
Recovery verified at UTC:
Incident closed or remains open:
Detection latency (measured only):
Containment duration (measured only):
```

### 17.4 Blameless postmortem template

-   **Summary:** what happened, written without assigning personal
    blame.
-   **Impact:** affected synthetic workload, data/model assets, release
    path, duration if measured.
-   **Detection:** what signal triggered response; what was missing.
-   **Timeline:** timestamped actions and evidence.
-   **Contributing conditions:** design gaps, unclear ownership, stale
    evidence, inadequate tests, or failure modes.
-   **What worked:** controls that reduced uncertainty or impact.
-   **What failed:** controls bypassed, unavailable, misconfigured, or
    untested.
-   **Why the system allowed this:** focus on process and technical
    conditions.
-   **Corrective actions:** action, owner, due date, success metric,
    regression test.
-   **Threat-model update:** new or changed threat/control.
-   **Evidence retention:** what was kept, where, and for how long.
-   **Communication:** audience, status, unresolved questions.
-   **Follow-up review:** verify remediation and close only with
    evidence.

### Acceptance and limits

The incident drill passes only if evidence is preserved, promotion stops
when warranted, affected digests are identified or explicitly
inconclusive, containment/recovery decisions are documented, and the
postmortem includes owners and regression tests. Do not invent
time-to-detect or time-to-contain.

## 18. Make interface and guardrails

### 18.1 Command interface

The final project should provide these targets only after implementing
them. The following Makefile is a safe starter for local validation and
inventory; cluster-changing targets deliberately refuse until the
learner adds a verified context guard and a reviewed implementation.

Create `Makefile`:

``` makefile
SHELL := /bin/sh
PYTHON ?= python3
PROJECT_NAME := secure-and-verified-container-release

.PHONY: help preflight validate-threats validate-scorecard evidence-check \
        policy-test detection-test adversary-tests verify-all cleanup

help:
    @printf '%s\n' \
      'preflight          Show local tool/context/resource inventory' \
      'validate-threats   Validate threat and exception register JSON' \
      'policy-test       Run local fixture policy tests (after implementation)' \
      'detection-test    Run local detection fixture tests (after implementation)' \
      'adversary-tests   Run bounded benign test suite (after implementation)' \
      'evidence-check    Check evidence index and scorecard states' \
      'verify-all        Aggregate required checks; skipped tests are not passes' \
      'cleanup           Refuse destructive work until expected lab context is configured'

preflight:
    @date -u +%Y-%m-%dT%H:%M:%SZ
    @uname -a
    @python3 --version
    @command -v docker >/dev/null 2>&1 && docker version || echo 'docker: NOT INSTALLED'
    @command -v kubectl >/dev/null 2>&1 && kubectl config current-context || echo 'kubectl: NOT INSTALLED'
    @command -v trivy >/dev/null 2>&1 && trivy --version || echo 'trivy: NOT INSTALLED'
    @command -v syft >/dev/null 2>&1 && syft version || echo 'syft: NOT INSTALLED'
    @command -v cosign >/dev/null 2>&1 && cosign version || echo 'cosign: NOT INSTALLED'
    @df -h .

validate-threats:
    $(PYTHON) threat-model/validate.py threat-model/register.json

policy-test:
    @echo 'OPEN: implement and run the selected VAP/Kyverno/Gatekeeper fixture suite'
    @exit 2

detection-test:
    @echo 'OPEN: implement and run detection fixture validation'
    @exit 2

adversary-tests:
    @echo 'OPEN: run all ADV-01 through ADV-20; NOT RUN is not a pass'
    @exit 2

evidence-check:
    @echo 'OPEN: implement scorecard/evidence-index validation before capstone sign-off'
    @exit 2

verify-all: validate-threats policy-test detection-test adversary-tests evidence-check
    @echo 'PASS: all defined checks completed'

cleanup:
    @echo 'REFUSED: configure EXPECTED_LAB_CONTEXT and implement reviewed, scoped cleanup first'
    @exit 2
```

The `OPEN` targets intentionally fail rather than pretending required
tests exist. Before final acceptance, replace each placeholder target
with a real implementation and test it. Do not change a placeholder to
exit zero merely to make CI green.

### 18.2 Context guard requirements

Before any destructive or enforcement operation: 1. Print current
Kubernetes context and cluster. 2. Require explicit
`EXPECTED_LAB_CONTEXT` and verify exact equality. 3. Require a unique
lab namespace label and confirm the target namespace belongs to the
project. 4. Refuse unknown, missing, or production-like contexts. 5. Use
namespace-scoped operations where possible. 6. Print the planned
resources before applying or deleting. 7. Require an explicit human
confirmation for teardown if resources are not uniquely labeled. 8.
Never delete user data or shared resources.

A guardrail test should use a deliberately wrong context string and
verify that the operation refuses **before** invoking any destructive
command. Do not test this by running a destructive command.

### 18.3 Idempotence and exit behavior

-   Re-running preflight should be safe.
-   Build targets should use explicit tags and contexts.
-   `verify-all` must return nonzero if a required check fails, is
    skipped, or is uninterpretable.
-   If a platform-limited check is permitted as `NOT RUN`, the summary
    must keep it visible and the overall live end-to-end status cannot
    be reported as a complete pass.
-   Cleanup must verify removal of namespaces, lab registry data where
    applicable, temporary keys, dummy credentials, webhook/policy
    objects, and temporary files.
-   Do not use `docker system prune`, `kubectl delete all`, or broad
    cluster cleanup as a default.

### Acceptance

All advertised Make targets must exist and have defined behavior. The
initial starter intentionally marks incomplete targets `OPEN`; the
project is not complete until implemented or explicitly scoped as a
non-live fixture path with corresponding acceptance gaps.

## 19. Handoff documentation templates

These are complete content templates to copy into the corresponding
files and fill with actual values. They are not proof that the documents
already exist.

### 19.1 `README.md`

``` markdown
# Secure and Verified Container Release

## Purpose
Demonstrate a threat-model-driven secure release for the inference API, ETL job,
and controlled notebook-style image using a local, zero-budget lab.

## Prerequisites
List actual OS/kernel, container engine, Kubernetes version, tools, disk/RAM,
network access, and optional Falco/policy-engine requirements. See versions.txt.

## Architecture
Developer source -> untrusted validation -> protected trusted build -> scan/SBOM
-> signing/provenance -> verification -> reviewed deployment -> admission
-> hardened runtime -> detection and incident workflow.

## Quick start
1. Read docs/limitations.md and threat-model/data-flow.md.
2. Run `make preflight`; save actual output.
3. Fill versions.txt from observed tool output.
4. Run threat-model validator and its negative fixtures.
5. Build and inspect each image using verified digest-pinned base images.
6. Scan and generate SPDX/CycloneDX SBOMs.
7. Sign the actual image digest with a disposable lab key.
8. Verify signatures/provenance and test negative cases.
9. Test VAP, then Kyverno, then Gatekeeper in separate cleanup-verified phases.
10. Run runtime hardening and supported detection tests.
11. Complete the scorecard, incident exercise, and final audit.
12. Run reviewed cleanup and verify removal.

## Safety
Only use synthetic data and dummy credentials. Never run against a non-lab cluster.
Never treat NOT RUN as PASS. Do not test third-party systems.

## Evidence
Every acceptance criterion has an evidence-index row with timestamp, tool version,
artifact digest, result, and limitations. Redact secrets and private keys.

## Acceptance
All required positive and negative tests have observed results or are explicitly
NOT RUN/INCONCLUSIVE. Live gaps remain open; the lab is not a production certification.

## Cleanup
Use the verified context guard and remove only uniquely labeled lab resources.
Delete temporary private keys and dummy credentials after evidence review.
```

### 19.2 `docs/architecture.md`

``` markdown
# Architecture

## Components
- Source repository and protected release revision
- Untrusted validation path
- Trusted builder and release authorization
- Registry/artifact store
- Trivy scanner and vulnerability database
- Syft SBOM generator
- Cosign signer and verifier
- Provenance/attestation generator and verifier
- GitOps deployment source
- Kubernetes API and admission policy
- Runtime workloads and NetworkPolicy
- Falco/audit evidence and incident workflow

## Trust boundaries
Document which identities, credentials, caches, networks, and permissions cross
each boundary. A diagram alone is not proof of enforcement.

## Data flows
Use threat-model/data-flow.md and include actual local registry/cluster details.

## Failure modes
Record registry unavailable, stale scanner DB, signer unavailable, invalid
attestation, admission webhook failure, network policy not enforced, and sensor
heartbeat missing. State whether each fails closed, fails open, or becomes
INCONCLUSIVE under the tested configuration.
```

### 19.3 `docs/trust-model.md`

``` markdown
# Trust model

## Artifact identity
The full image digest is the release identity. Tags are not sufficient.

## Signer
Record public-key fingerprint or tightly scoped identity, how it is protected,
who may use it, rotation procedure, and revocation/retirement behavior.

## Builder
Record the actual builder ID, source revision, build definition, external
parameters, and isolation assumptions. A locally named builder is not automatically
a trusted hosted builder.

## Attestations
List required predicate types and schemas, subject-digest checks, verifier
version, and policy revision. Explain what each predicate proves and does not prove.

## Trust decisions
Pin trust roots and identities. Do not use broad regular expressions or
untrusted image annotations as the only trust condition.

## Known gaps
State local key custody, provider OIDC, transparency-log, hermeticity, and
reproducibility limitations.
```

### 19.4 `docs/rollout-and-rollback.md`

``` markdown
# Rollout and rollback

1. Test policies against valid and invalid fixtures.
2. Run audit-only mode where supported.
3. Resolve false positives and document exceptions with expiry.
4. Enforce in the disposable lab namespace.
5. Monitor denials, webhook health, and legitimate deployment success.
6. Stop promotion if verification is unhealthy or an artifact is suspect.
7. Roll back to a known-good digest through the reviewed deployment path.
8. Preserve evidence and verify the running digest after recovery.

Rollback triggers include incorrect broad denial, policy engine outage, signature
verification failure, unexpected artifact digest, and suspected signer compromise.
Document exact commands only after verifying them for the selected engine/version.
```

### 19.5 `docs/limitations.md`

``` markdown
# Limitations

- Laptop-local build and policy tests do not prove production isolation.
- Local key-based cosign signing does not prove keyless identity or public
  transparency-log guarantees.
- A signature proves a key-bound statement, not that the artifact is safe.
- SBOM completeness is limited by scanner ecosystem support, static/vendored
  code, dynamically downloaded files, and model/data content.
- Trivy results depend on version, database freshness, package mapping, and
  detection coverage.
- VEX and policy-engine APIs are version-sensitive.
- VAP baseline checks do not themselves validate signatures/provenance unless
  a separate supported verifier is integrated and tested.
- NetworkPolicy is not proven without a CNI enforcement test.
- Falco live detection is NOT RUN if kernel/driver support is unavailable.
- Fixture-based policy/detection tests do not prove live integration.
- No SLSA level or regulatory compliance is claimed.
- All measurements and test outcomes must come from actual execution.
```

### 19.6 Runbook index

Create the following runbooks under `runbooks/`: -
`critical-scan-finding.md` - `signature-or-provenance-failure.md` -
`admission-denial.md` - `runtime-alert.md` -
`sensor-health-failure.md` - `suspected-ci-compromise.md`

Each runbook must include trigger, severity/incident declaration, first
actions, evidence to preserve, safe containment, rollback/recovery,
verification, communications, escalation, cleanup, and "do not"
warnings. Use M10's incident roles and M11's telemetry conventions
instead of inventing a separate incident-management system.

### 19.7 `audit/evidence-index.md` final fields

For every criterion record: - criterion/test ID; - command or test
artifact; - `PASS` / `FAIL` / `NOT RUN` / `INCONCLUSIVE`; - UTC
timestamp; - OS/kernel and relevant tool version; - artifact digest or
fixture ID; - evidence path/checksum; - owner; - limitations and next
action.

### 19.8 Cleanup and secret-removal policy

-   Keep private keys outside the repository and image contexts.
-   Use only dummy throwaway credentials; rotate them if a test might
    expose them.
-   Delete disposable private keys, temporary wrong-key fixtures, dummy
    token files, and test markers after evidence review.
-   Remove lab namespace resources, registry data owned by the project,
    admission bindings/policies, webhooks/controllers, temporary
    volumes, and local clusters only after confirming ownership.
-   Verify no blocking webhook or policy remains.
-   Do not remove shared clusters, shared registries, or user data.
-   Record cleanup evidence and any remaining resource as `OPEN`, with
    owner and next action.

## 20. Scoring and acceptance checklist

### 20.1 Scoring model

Score only tested outcomes. Suggested weighting is \[ILLUSTRATIVE\] and
should be adjusted by the reviewer.

  ------------------------------------------------------------------------
  Area                                        Weight Evidence expected
  --------------------- ---------------------------- ---------------------
  Threat model and                               10% STRIDE, risk
  traceability                                       register, attack
                                                     trees, validator

  Hardened images and                            10% Actual digests,
  build repeatability                                runtime
                                                     UID/filesystem tests

  Scan and triage                                10% Three reports, DB
                                                     freshness, 25
                                                     synthetic cases,
                                                     exceptions/VEX

  SBOM and inventory                             10% SPDX/CycloneDX per
                                                     image, quality
                                                     checks, query/diff

  CI isolation                                   10% Trust diagram,
                                                     capability matrix,
                                                     negative tests

  Signing and                                    10% Actual digest
  provenance                                         verification,
                                                     wrong-key and
                                                     forged-provenance
                                                     tests

  Admission                                      10% Valid/invalid
                                                     manifests, engine
                                                     matrix, cleanup proof

  Runtime                                         8% Runtime checks and
  hardening/network                                  CNI enforcement
                                                     evidence or OPEN gap

  Detection and audit                             8% Ten-rule catalog,
                                                     fixtures/live
                                                     evidence, health
                                                     drill

  Incident, evidence,                             8% Incident log,
  cleanup                                            postmortem, evidence
                                                     index, teardown
                                                     verification

  Independent audit                               6% Corrected findings,
                                                     remaining OPEN items,
                                                     traceability matrix
  ------------------------------------------------------------------------

A score cannot override a critical failure. Any test proving that an
untrusted path can sign/promote, a wrong signer is accepted, or an
unsafe workload bypasses enforced policy should block acceptance until
fixed or explicitly accepted as a lab-only gap by the reviewer. Do not
assign points for unexecuted tests.

### 20.2 Final acceptance checklist

-   [ ] Threat model includes at least 10 meaningful data-flow elements
    and trust boundaries.
-   [ ] STRIDE analysis, qualitative likelihood/impact criteria, two
    attack trees, and risk register exist.
-   [ ] ML/data-specific threats are included.
-   [ ] Risk acceptance records have owner, rationale, compensating
    controls, expiry/review, and exit condition.
-   [ ] Validator negative tests reject missing fields, missing
    mitigations, missing owners, controls without tests, malformed
    dates, and expired exceptions.
-   [ ] Three harmless workload images are built from verified
    digest-pinned bases.
-   [ ] Build context contains no real secrets; image runtime user and
    filesystem behavior are tested.
-   [ ] Build-twice comparison records actual digests and
    nondeterminism.
-   [ ] All three images have comparable Trivy reports and recorded DB
    freshness.
-   [ ] At least 25 synthetic findings are triaged with evidence and
    owners.
-   [ ] VEX format is explicitly named and schema/status support
    verified; unjustified not-affected case rejected.
-   [ ] Expiring ignores and stale DB tests work.
-   [ ] SPDX and CycloneDX SBOMs are generated for actual image digests.
-   [ ] SBOM quality, inventory query, release diff, and known-absent
    query are tested.
-   [ ] Model artifact identity is separate from software SBOM.
-   [ ] Untrusted and trusted CI paths are documented and negative tests
    are present.
-   [ ] No long-lived registry password is used in workflow;
    provider-specific claims are verified or OPEN.
-   [ ] Image digest is signed and verified with a lab-only key.
-   [ ] Wrong key, unsigned image, mismatch, missing attestation, and
    forged provenance are rejected.
-   [ ] A correctly signed but vulnerable image is rejected by risk
    policy.
-   [ ] Provenance schema and subject digest are validated; no
    unsupported SLSA level is claimed.
-   [ ] VAP baseline is tested; Kyverno and Gatekeeper are exercised
    separately or clearly marked fixture-only.
-   [ ] Admission tests include init-container bypass, registry, digest,
    signer/attestation, privileged/root, and exceptions.
-   [ ] Cleanup confirms no blocking webhook/policy remains.
-   [ ] Runtime hardening is tested; NetworkPolicy is claimed only if
    CNI enforcement is demonstrated.
-   [ ] Falco feasibility is documented; ten rule intents have
    positive/negative fixtures.
-   [ ] Sensor health distinguishes no alerts from no telemetry.
-   [ ] Finding lifecycle, exception validation, evidence index, and
    action-oriented metrics exist.
-   [ ] All 20 benign adversary tests have results; NOT RUN is not PASS.
-   [ ] Incident exercise preserves evidence, scopes digests, records
    decisions, and includes a blameless postmortem.
-   [ ] Make targets advertised as complete actually run; incomplete
    targets fail closed.
-   [ ] Context guard is tested with wrong expected context before any
    destructive operation.
-   [ ] Handoff docs and six runbooks are complete.
-   [ ] Versions are actual observations or clearly marked absent.
-   [ ] Final audit and verification register list every unresolved
    item.
-   [ ] Cleanup removes only project-owned resources and temporary
    secrets.

## 21. Troubleshooting

  --------------------------------------------------------------------------
  Symptom                 Likely cause               Safe next step
  ----------------------- -------------------------- -----------------------
  Build fails fetching    Network, registry access,  Check the exact
  base image              architecture mismatch,     reference and registry
                          invalid digest             metadata; use a
                                                     verified cached image
                                                     if available and mark
                                                     network test
                                                     limitations

  Digest differs between  Different base             Compare build inputs
  builds                  digest/platform/tool       and metadata; record
                          version, timestamps,       the mismatch rather
                          nondeterministic output    than claiming
                                                     reproducibility

  Trivy reports differ    Database updated or        Record database
  between images scanned  settings differ            timestamp/settings;
  minutes apart                                      repeat under one
                                                     controlled snapshot

  Trivy database          Offline network or cache   Use fixture mode for
  unavailable             issue                      triage; mark current
                                                     vulnerability coverage
                                                     NOT RUN

  "No vulnerabilities"    Unsupported package,       Inspect build/source
  but inventory seems     static/vendored component, inputs and record
  incomplete              missing metadata           uncertainty

  SBOM parser rejects     Schema/format version      Check Syft and
  output                  mismatch or unsupported    validator versions; use
                          selector                   supported format and
                                                     record it

  Signature verification  Wrong digest/key, registry Verify actual digest
  fails                   artifact lookup, key path  and public key; consult
                          or version syntax          selected cosign docs;
                                                     preserve output

  Signature passes but    Signature policy is being  Add independent
  release should fail     confused with              scan/provenance
                          vulnerability/provenance   conditions; test
                          policy                     signed-vulnerable
                                                     fixture

  Provenance exists but   Policy does not            Validate predicate
  verifier accepts wrong  consume/pin the source     schema and explicitly
  source                  claim                      compare expected
                                                     source/ref/builder

  VAP policy fails to     Kubernetes version/API     Check server version
  install                 unsupported or CEL         and API schema;
                          expression type error      validate in disposable
                                                     cluster before
                                                     enforcing

  Admission blocks all    Policy too broad or        Stop promotion, switch
  deployments             selector wrong             to reviewed audit
                                                     mode/disable binding in
                                                     lab, inspect match
                                                     scope and positive
                                                     fixture

  Kyverno/Gatekeeper      Prior controller/webhook   Stop; inventory
  overlap                 cleanup incomplete         webhooks and policy
                                                     objects, remove
                                                     previous engine and
                                                     verify before
                                                     proceeding

  NetworkPolicy object    CNI does not enforce       Test from a benign pod
  exists but traffic      policy or selectors are    to a local listener;
  still flows             wrong                      mark OPEN if
                                                     enforcement cannot be
                                                     proved

  Falco cannot start      Unsupported kernel/driver, Do not bypass host
                          permissions, incompatible  protections; use
                          runtime                    rule/fixture mode or
                                                     native Linux/VM

  No Falco alerts         No matching event, wrong   Check sensor
                          rules, or dead sensor      health/heartbeat and a
                                                     known benign trigger
                                                     before concluding no
                                                     suspicious activity

  CI test passes locally  Local simulation lacks     Keep provider-specific
  but provider behavior   provider semantics         gate OPEN until tested
  differs                                            with least-privilege
                                                     disposable workflow

  `make verify-all` says  Placeholder targets or     Make each target return
  success despite skipped shell pipeline hides       nonzero on missing
  checks                  failure                    implementation;
                                                     aggregate status
                                                     explicitly

  Cleanup refuses         Expected context missing   Verify exact context
                          or mismatch                and resource ownership;
                                                     do not bypass the guard

  Evidence contains       Overly broad               Restrict access, redact
  secrets                 logs/environment capture   carefully, rotate dummy
                                                     credential, and
                                                     document the incident;
                                                     do not upload real
                                                     secrets
  --------------------------------------------------------------------------

## 22. Cleanup and residual risk

### 22.1 Cleanup sequence

1.  Stop promotion and ensure no policy enforcement remains necessary
    for a running lab.
2.  Preserve final reports, test scorecard, artifact digests, and
    incident evidence.
3.  Confirm current Kubernetes context equals the explicit lab context.
4.  List project namespace, labels, workloads, policies, webhooks, and
    controller resources before deleting.
5.  Delete only resources uniquely labeled for this project.
6.  Verify no Kyverno or Gatekeeper webhook/controller remains from its
    exercise; verify no blocking VAP binding remains.
7.  Verify lab NetworkPolicies and namespaces are removed.
8.  Remove project-owned local registry data and tagged images only
    after checking references.
9.  Delete disposable private keys, wrong-key fixtures, dummy
    credentials, and marker files.
10. Remove temporary files and logs containing sensitive local paths if
    no longer needed.
11. Re-run preflight/listing checks and save cleanup evidence.
12. Record any remaining resource as `OPEN`, with owner and next action.

Do not use a broad delete/prune operation as the default. Do not delete
shared resources or user data. If cleanup cannot be verified, the
project remains open.

### 22.2 Residual-risk register

At minimum, carry forward: - local runner/build isolation does not equal
a trusted hosted builder; - lab key custody is not HSM/KMS protection; -
public Sigstore keyless/transparency behavior is not demonstrated by
key-based local signing; - scanner and SBOM coverage is imperfect and
depends on tool/database/schema versions; - VEX interpretation and
exception processes require governance; - VAP baseline checks do not
automatically verify signatures/attestations; - policy engine APIs and
webhook failure behavior are version-sensitive; - NetworkPolicy
enforcement depends on CNI support; - Falco live detection may be
unavailable under WSL2; - fixtures do not prove live telemetry, alert
routing, or measured time-to-detect; - the sample model inventory does
not prove model safety or training-data lineage; - no regulatory
compliance or SLSA level is claimed.

### 22.3 Handoffs

-   **M13 --- Disaster recovery:** extend artifact/evidence retention
    and restore tests only in that module.
-   **M14 --- Multi-cluster operations:** extend policy, identity, and
    digest verification across clusters only in that module.
-   **M15 --- Cost engineering:** measure scanning/build/telemetry
    resource costs and optimize without weakening required controls.
-   **M16 --- Golden paths:** package verified defaults into reusable
    templates and platform guardrails.

## 23. Roadmap traceability matrix

Status values: `PASS` only after evidence is executed and reviewed;
`PARTIAL` when some evidence exists but a required dimension remains;
`OPEN` when live behavior or implementation remains unverified;
`NOT APPLICABLE` only when a requirement genuinely does not apply. The
initial status below is conservative because this workbook itself has
not run the learner's lab.

  -----------------------------------------------------------------------------------------------------------------------
  M12 unit /  Requirement             Project         Positive evidence    Negative test              Initial status/gap
  earlier                             phase/file                                                      
  module                                                                                              
  ----------- ----------------------- --------------- -------------------- -------------------------- -------------------
  M01         Hardened image and      Phase 1;        Image digest, UID,   Root/unpinned baseline     OPEN --- learner
              registry hygiene        Dockerfiles     filesystem tests     denied                     build required

  M02         CI/CD security trust    Phase 4; `ci/`  Protected release    Untrusted promotion        OPEN --- provider
              separation                              fixture              attempt                    semantics untested

  M03         Cluster operations and  Phase 6--7;     Valid workload       Unsafe workload denied     OPEN --- live
              RBAC                    `policy/`       admitted                                        cluster required

  M04         Network and Kubernetes  Phase 7;        Allowed traffic      Prohibited local traffic   OPEN --- CNI
              security                NetworkPolicy   works                blocked                    enforcement must be
                                                                                                      proven

  M06         Release packaging       Phase 6;        Reviewed digest      Tag-only manifest denied   PARTIAL --- use
                                      manifests       manifest                                        packaging only if
                                                                                                      needed

  M07         IaC                     Feasibility and Local setup          Wrong-context refusal      NOT APPLICABLE to
                                      bootstrap       documented                                      cloud provisioning;
                                                                                                      local guard OPEN

  M08         GitOps                  Phases 4, 6, 17 Reviewed promotion   Manual bypass fixture      OPEN --- actual
                                                      evidence             denied                     GitOps integration
                                                                                                      optional

  M09         Identity/secrets        Phases 4, 5, 7, Short-lived/dummy    PR cannot read dummy       OPEN --- no real
                                      17              identity design      secret                     provider
                                                                                                      integration

  M10         Incident response       Phase 17        Timeline and         Sensor/policy failure      OPEN --- exercise
                                                      postmortem           scenario                   not run

  M11         Observability           Phase 14--15    Alert/health         Stale heartbeat not        OPEN --- full stack
                                                      evidence             treated as healthy         optional

  M12 U1      Threat model            Phase 3         STRIDE, risks,       Missing owner/mitigation   OPEN --- learner
                                                      validator            rejected                   review required

  M12 U2      Scan/triage             Phase 8         Three actual reports Stale DB/finding gate      OPEN --- Trivy run
                                                                                                      required

  M12 U3      SBOM/provenance         Phase 9         SPDX + CycloneDX per Mismatch/malformed         OPEN --- Syft run
              inventory                               digest               inventory rejected         required

  M12 U4      Signing/verification    Phase 11        Actual digest        Wrong key/unsigned digest  OPEN --- cosign run
                                                      verifies             rejected                   required

  M12 U5      Build                   Phase 10        Trust path and       Untrusted job cannot sign  PARTIAL --- local
              isolation/short-lived                   capability table                                simulation only
              CI                                                                                      

  M12 U6      Workload                Phases 10--13,  Dummy identity and   Token mount or             OPEN --- no cloud
              identity/rotation       17              rotation procedure   unauthorized identity      identity required
                                                                           rejected                   

  M12 U7      Runtime hardening       Phase 13        Non-root/read-only   Privileged/root fixture    OPEN --- cluster
                                                      tests                denied                     required

  M12 U8      Admission policy        Phase 12        Valid manifest       Unsigned/tag-only/unsafe   OPEN ---
                                                      admitted             manifest denied            VAP/policy-engine
                                                                                                      test required

  M12 U9      Auditing/remediation    Phase 15        Finding lifecycle    Expired exception fails    PARTIAL ---
                                                      and evidence index                              validator
                                                                                                      extensions may be
                                                                                                      needed

  M12 U10     SLSA/provenance         Phase 11        Schema-validated     Wrong source/builder       OPEN --- official
                                                      subject-bound        fixture rejected           schema validation
                                                      statement                                       required

  M12 U11     Kyverno/Gatekeeper      Phase 12        Separate engine test Bypass fixture denied      OPEN --- no
                                                      reports                                         simultaneous
                                                                                                      install

  M12 U12     Falco runtime detection Phase 14        Live event or        Sensor failure/stale       OPEN --- platform
                                                      labeled fixture      heartbeat                  feasibility pending

  M12 U14     Integrated capstone     All phases      Evidence index and   20 benign tests            OPEN --- execution
                                                      scorecard                                       pending

  M13         Disaster recovery       Handoff only    N/A                  N/A                        NOT APPLICABLE to
                                                                                                      this capstone

  M14         Multi-cluster           Handoff only    N/A                  N/A                        NOT APPLICABLE to
              operations                                                                              this capstone

  M15         Cost engineering        Handoff only    N/A                  N/A                        NOT APPLICABLE to
                                                                                                      this capstone

  M16         Golden paths            Handoff only    N/A                  N/A                        NOT APPLICABLE to
                                                                                                      this capstone
  -----------------------------------------------------------------------------------------------------------------------

### Traceability review rule

Before final sign-off, inspect every requirement in the acceptance
checklist and ensure the matrix points to an actual file/test/evidence
row. Any criterion without a positive and negative test is `OPEN`. Do
not change statuses from `OPEN` merely because the document describes
how to test them.

## 24. References and verification register

### 24.1 Official references

The following official references were consulted for selected
version-sensitive claims. The retrieved pages can change; capture the
exact version/date used in the learner's verification register.

1.  **Kubernetes --- Validating Admission Policy.** Documents VAP as a
    declarative, in-process alternative to validating admission webhooks
    and states it has been stable since Kubernetes v1.30. This does not
    guarantee the learner's cluster supports the same API; inspect the
    actual server version and API.
    <https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/>
2.  **Kubernetes --- ValidatingAdmissionPolicy v1 API reference.** Use
    for field-level/API review and CEL validation semantics.
    <https://kubernetes.io/docs/reference/kubernetes-api/admissionregistration/validating-admission-policy-v1/>
3.  **Sigstore --- Cosign quickstart.** Documents signing and verifying
    artifacts and images, and introduces keyless identity and
    attestations. This workbook's core path uses a lab-only key; public
    keyless flows are optional.
    <https://docs.sigstore.dev/quickstart/quickstart-cosign/>
4.  **Sigstore --- Verifying signatures.** Reference for image
    verification and attestation verification command behavior. Verify
    against the installed release.
    <https://docs.sigstore.dev/cosign/verifying/verify/>
5.  **SLSA --- Build Provenance specification.** Describes the
    `https://slsa.dev/provenance/v1` predicate type and the purpose of
    provenance. The current track/level requirements must be checked
    separately before making a level claim.
    <https://github.com/slsa-framework/slsa/blob/main/spec/build-provenance.md>
6.  **OPA Gatekeeper --- Constraint Templates.** Reference for
    Gatekeeper's ConstraintTemplate model and current schema
    considerations. Verify the selected Gatekeeper release and policy
    API.
    <https://open-policy-agent.github.io/gatekeeper/website/docs/constrainttemplates/>
7.  **Kyverno --- Verify Images Rules.** Image signature and attestation
    policy API changes across releases; use documentation for the
    installed version, not a stale versioned page.
    <https://kyverno.io/docs/policy-types/cluster-policy/verify-images/>

**Verification limitation:** this reference list does not substitute for
checking current Trivy, Syft, SPDX, CycloneDX, VEX, Docker/BuildKit,
CI-provider OIDC, Falco, Prometheus, Loki, or Alertmanager syntax
against the exact installed versions. Those items remain in the register
below.

### 24.2 Verification register

  ---------------------------------------------------------------------------------------------------------------------------
  Claim/item                      Official source  Version/date                        Result         Owner / next action
                                  or check                                                            
  ------------------------------- ---------------- ----------------------------------- -------------- -----------------------
  Docker/BuildKit build behavior, Docker docs and  Record actual version/date          `[VERIFY]` for Learner: verify
  digest-pinned bases, build      selected engine                                      chosen flags   commands before build
  secrets                         `--help`                                                            

  Trivy image/fs/config commands, Official Trivy   Record actual version and DB        `[VERIFY]`     Learner: capture output
  JSON format, exit codes         CLI docs +       timestamp                                          and verify DB freshness
                                  installed                                                           
                                  `trivy --help`                                                      

  Trivy ignore/VEX support and    Official Trivy   Record version/date                 `[VERIFY]`     Learner: test
  offline behavior                docs for                                                            positive/negative
                                  selected release                                                    fixtures

  Syft SPDX/CycloneDX selectors   Official Syft    Record version/date                 `[VERIFY]`     Learner: validate all
  and schema versions             docs and                                                            six image/format
                                  generated output                                                    combinations

  SPDX/CycloneDX schema           Official format  Record schema/tool version          `[VERIFY]`     Learner: record schema
  validation                      specifications                                                      validation
                                  and validator                                                       
                                  docs                                                                

  VEX format/status values        Selected         Record format/version               `[VERIFY]`     Learner: reject
                                  official VEX                                                        unjustified
                                  specification                                                       not-affected record

  Cosign key generation, sign,    Official         Record version/date                 Partial        Learner: run actual
  verify, attest                  Sigstore docs                                        reference      key/sign/negative tests
                                  and installed                                        check; exact   
                                  CLI help                                             syntax         
                                                                                       `[VERIFY]`     

  SLSA provenance                 Official SLSA    Current predicate                   Reference      Learner: validate
  schema/predicate                provenance       `https://slsa.dev/provenance/v1`;   consulted;     statement with schema
                                  specification    exact revision to record            full schema    
                                  and schema                                           test           
                                                                                       `[VERIFY]`     

  CI OIDC claims, permissions,    Official chosen  Provider/version/date               `[VERIFY]`     Learner: do not enable
  runner isolation, immutable     CI provider docs                                                    release workflow until
  action refs                                                                                         checked

  Kubernetes API/security         Official docs    Record server version/date          Partial VAP    Learner: server-side
  fields/PSS/audit fields         for selected                                         reference      validation and live
                                  cluster version                                      checked; rest  tests
                                                                                       `[VERIFY]`     

  VAP fields and CEL functions    Official         VAP stable since v1.30 per docs;    Reference      Learner: validate in
                                  Kubernetes VAP   actual cluster still to check       checked;       disposable cluster
                                  docs                                                 sample         
                                                                                       expressions    
                                                                                       need live      
                                                                                       validation     

  Kyverno verifyImages API        Official Kyverno Record version/date                 `[VERIFY]`     Learner: verify
                                  docs for exact                                                      signature/attestation
                                  release                                                             support

  Gatekeeper                      Official         Record version/date                 Reference      Learner: separate
  ConstraintTemplate/Constraint   Gatekeeper docs                                      consulted;     cluster test
  APIs                            for exact                                            selected API   
                                  release                                              `[VERIFY]`     

  Falco drivers, BTF/kernel, rule Official Falco   Record version/date                 `[VERIFY]`     Learner: preflight;
  fields and metrics              docs for                                                            fixture fallback if
                                  selected release                                                    unsupported

  Prometheus/Alertmanager/LogQL   Official         Record versions/date                `[VERIFY]`     Learner: optional stack
  syntax and metric names         component docs                                                      validation
                                  and local config                                                    

  SLSA level claim                Exact official   No level claimed in this workbook   NOT CLAIMED    Do not claim level
                                  track/version                                                       until every applicable
                                  requirements                                                        requirement is
                                  plus evidence                                                       evidenced
                                  mapping                                                             

  Production security/compliance  Independent      Not assessed                        NOT CLAIMED    Human security review
                                  production                                                          required
                                  review and                                                          
                                  applicable                                                          
                                  obligations                                                         
  ---------------------------------------------------------------------------------------------------------------------------

### 24.3 Human verification checklist

Before relying on any version-sensitive command or policy: 1. Confirm
the tool and server versions from actual command output. 2. Open the
official documentation matching those versions. 3. Verify every flag,
output format, API version, field, schema, and status value. 4. Run
syntax validation in a disposable directory/cluster. 5. Test a positive
and negative case. 6. Save actual output with timestamp and version. 7.
Mark unresolved behaviors `[VERIFY]` and the corresponding criterion
`OPEN`. 8. Review whether a change in tool version invalidates prior
evidence.

## 25. Final independent audit report

### 25.1 Audit summary

**Status: PASS WITH OPEN ITEMS.**

This document provides a comprehensive guided implementation plan,
representative starter artifacts, positive/negative test design,
evidence conventions, traceability, and an explicit version-verification
process. It has not been executed against the learner's host, container
engine, registry, Kubernetes cluster, CI provider, or Falco sensor. The
local capstone cannot be considered accepted until the human execution
checklist and all required evidence are completed.

### 25.2 Findings table

  ------------------------------------------------------------------------------------------------------------------------------
  ID          Severity    Finding                 Source/requirement     Correction made                 Residual risk
  ----------- ----------- ----------------------- ---------------------- ------------------------------- -----------------------
  AUD-01      High        Full roadmap tree file  Source authority       Explicitly records source       Confirm exact
                          was not available as a  protocol               limitation and keeps M12        `Roadmap_ptree.md`
                          distinct source during                         ownership boundaries from the   placement before
                          this authoring pass;                           supplied capstone prompt        repository merge
                          repository placement is                                                        
                          based on the supplied                                                          
                          prompt and available                                                           
                          M12 syllabus prompt                                                            
                          context                                                                        

  AUD-02      High        Local environment/tool  Evidence honesty and   `versions.txt` requires actual  Human must capture
                          versions are not        tool verification      observed values; no invented    versions and verify
                          available from the                             versions are supplied           syntax
                          prompt alone                                                                   

  AUD-03      High        Dockerfile base image   Hardened build         Explicitly requires learner to  Build remains OPEN
                          placeholders are not    requirement            select/verify digest-pinned     until actual digests
                          immutable digests                              bases and prohibits accepting   are recorded
                                                                         placeholders                    

  AUD-04      High        VAP baseline cannot     Admission enforcement  States the limitation and       Signature/attestation
                          verify                  requirement            requires a separate supported   admission remains OPEN
                          signatures/provenance                          verifier for authenticity       until integrated/tested
                          by itself                                      claims                          

  AUD-05      High        VAP sample does not     Bypass-resistance      Calls out init containers,      Full live policy
                          fully cover all         requirement            workload kinds, updates,        coverage remains OPEN
                          workload kinds and                             ephemeral containers, and       
                          container lists                                policy bypass tests             

  AUD-06      High        Policy-engine API and   Technical accuracy     Marks selected details          Must verify selected
                          Falco rule syntax are   requirement            `[VERIFY]`, links official      versions and tests
                          version-sensitive                              sources, and requires           
                                                                         live/fixture distinction        

  AUD-07      Medium      Full hosted CI/OIDC     CI isolation           Separates local logic tests     Real provider review
                          behavior cannot be      requirement            from provider-specific proof    remains necessary
                          proven by local                                and marks provider gate OPEN    
                          simulation                                                                     

  AUD-08      Medium      SBOM and scanner        Inventory/scanning     Adds explicit limitations for   Residual inventory
                          results can be          requirements           static/vendored/model/dynamic   uncertainty remains
                          incomplete                                     content and stale DB            

  AUD-09      Medium      Live Falco may be       Runtime detection      Adds feasibility preflight and  Live detection remains
                          unavailable on WSL2     requirement            fixture fallback without        NOT RUN if unsupported
                                                                         claiming live detection         

  AUD-10      Medium      Makefile includes       Guardrail/verify-all   Targets fail nonzero rather     Capstone is not
                          intentionally           requirement            than falsely passing;           complete until targets
                          incomplete targets in                          acceptance requires replacing   are implemented
                          the starter                                    them with real checks           

  AUD-11      Medium      Exact                   SBOM/VEX requirements  Requires explicit               Human must complete
                          SPDX/CycloneDX/VEX                             format/version and schema       schema validation
                          schema validation                              validation; marks unresolved    
                          depends on chosen                              syntax `[VERIFY]`               
                          versions                                                                       

  AUD-12      Medium      Full observability      Laptop feasibility     Makes the stack optional and    Fixture path does not
                          stack may exceed the                           supports fixture-based core     prove alert routing
                          resource budget                                tests                           
  ------------------------------------------------------------------------------------------------------------------------------

### 25.3 Roadmap traceability status

-   M01: `OPEN` --- actual image build and registry behavior not
    executed.
-   M02: `PARTIAL` --- trust-boundary design included; hosted provider
    enforcement not tested.
-   M03/M04: `OPEN` --- live Kubernetes and CNI enforcement not tested.
-   M06: `PARTIAL` --- digest-based manifest flow included; packaging
    integration optional.
-   M07: `NOT APPLICABLE` to cloud provisioning; local guardrails remain
    `OPEN`.
-   M08: `OPEN` --- GitOps integration not run.
-   M09: `PARTIAL` --- identity and rotation boundaries included; no
    real provider integration.
-   M10: `OPEN` --- incident exercise not run.
-   M11: `OPEN` --- optional telemetry stack not run.
-   M12 U1--U12: `PARTIAL/OPEN` --- requirements mapped to phases, but
    learner execution and selected-version verification remain
    outstanding.
-   M12 U14: `OPEN` --- capstone evidence has not been collected.
-   M13--M16: `NOT APPLICABLE` to implementation scope; forward handoffs
    only.

### 25.4 Test status counts

The document defines 20 adversary-emulation tests (ADV-01 through
ADV-20). **Observed result counts at document generation:** `PASS = 0`,
`FAIL = 0`, `NOT RUN = 20`, `INCONCLUSIVE = 0`. These are status
assignments in the unexecuted starter scorecard, not observed test
outcomes. The learner must update each row only after running the
corresponding test. Other phase tests are also not executed.

### 25.5 `[VERIFY]` inventory count

`[VERIFY]` is intentionally used in this document for version-sensitive
tool/API/schema details. The authoritative count must be generated after
saving the final file using the command below; do not manually estimate
it:

``` bash
grep -o '\[VERIFY\]' 01-secure-and-verified-container-release.md | wc -l
```

Record that observed count and the verification-register owner/action in
the final evidence index.

### 25.6 Human execution checklist

-   [ ] Confirm the exact roadmap tree and destination path.
-   [ ] Install tools only from official sources and capture observed
    versions.
-   [ ] Measure available RAM, CPU, disk, and network access.
-   [ ] Run preflight and threat-validator positive/negative tests.
-   [ ] Select maintained digest-pinned base images and record their
    actual digests.
-   [ ] Build all three sample images and test non-root/read-only
    filesystem behavior.
-   [ ] Run reproducibility comparison twice under documented
    conditions.
-   [ ] Run Trivy on all three actual image digests with recorded DB
    freshness.
-   [ ] Complete triage of all 25 synthetic findings and the advisory
    drill.
-   [ ] Verify VEX format/status/schema and negative unjustified
    suppression.
-   [ ] Generate SPDX and CycloneDX SBOMs for all three actual images.
-   [ ] Validate SBOMs and run positive/negative component inventory
    queries.
-   [ ] Test CI trust-boundary fixtures; verify provider-specific
    configuration before any real release use.
-   [ ] Generate a lab-only cosign key, sign actual digest, and run
    unsigned/wrong-key/tampered negative tests.
-   [ ] Generate and schema-validate subject-bound
    attestations/provenance.
-   [ ] Run wrong source/builder/subject provenance tests.
-   [ ] Test VAP in a disposable cluster and document its limitations.
-   [ ] Remove VAP test objects; test Kyverno in a separate phase;
    remove and verify cleanup.
-   [ ] Test Gatekeeper in a separate phase; verify cleanup and no
    blocking webhook remains.
-   [ ] Test runtime hardening, token mounting, privilege, and CNI
    NetworkPolicy enforcement.
-   [ ] Run Falco preflight; test live only if supported, otherwise mark
    live checks NOT RUN.
-   [ ] Validate ten detection intents and sensor-health fixtures.
-   [ ] Run all 20 adversary tests and positive control.
-   [ ] Run incident exercise and write postmortem from actual
    timestamps.
-   [ ] Implement all advertised Make targets; ensure `verify-all` fails
    for required skipped/failed/inconclusive tests.
-   [ ] Test wrong-context refusal without running destructive
    operations.
-   [ ] Complete evidence index, residual-risk register, handoff docs,
    and six runbooks.
-   [ ] Execute cleanup with verified context and confirm no lab
    policy/webhook/key/credential remains.
-   [ ] Review final acceptance checklist with a human reviewer.

### 25.7 Final sign-off

``` text
Content status: DRAFT-AUDITED
Audit date: 2026-10-29
Auditor: AI self-audit; human execution review required
[VERIFY] count: obtain from the saved file using the command above
Adversary tests: PASS 0 | FAIL 0 | NOT RUN 20 | INCONCLUSIVE 0 (starter status; not executed)
Production security certification: NOT CLAIMED
Regulatory compliance certification: NOT CLAIMED
SLSA level: NOT CLAIMED
Final capstone acceptance: OPEN pending human execution and evidence review
```

This project does not certify production security or regulatory
compliance. It is a defensive teaching lab. Any result not backed by
actual execution and review must remain `NOT RUN`, `INCONCLUSIVE`, or
`OPEN`.
