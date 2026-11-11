# Security and Release Rubric --- M17 Unit 4

> **Target file:** `security-and-release-rubric.md`\
> **Module:** M17 --- Production DevOps Integrated Capstone\
> **Unit:** 4 --- Security and release rubric\
> **Estimated time:** 18--24 hours for study, implementation, evidence
> capture, and review. This is a planning estimate, not a completion
> guarantee.\
> **Prerequisites:** Stage 2E M01--M16 outcomes. Highest relevance: M01
> images/registry; M02 CI/CD; M04 networking/TLS; M06 packaging; M08
> GitOps/progressive delivery; M09 secrets/identity; M10
> SRE/incident/SLO/ORR; M11 observability; M12 security/supply chain;
> M13 backup/DR/chaos.\
> **Core tools:** Git, GitHub Actions, kind, kubectl, Helm or Kustomize,
> Argo CD, local registry, Prometheus/Grafana, backup/verification
> tooling.\
> **Awareness/optional tools:** cosign, one policy engine (Kyverno or
> Gatekeeper), Argo Rollouts, Syft or another SBOM generator, Gitleaks
> or another secret scanner, Chaos Mesh/Litmus.\
> **Last reviewed:** 2026-11-04.\
> **Tool baseline assumed:** no exact tool versions are asserted. Record
> installed versions in the learner's `versions.txt`; verify all
> version-sensitive flags, action pins, APIs, policy syntax, and
> registry/runtime adapters against official documentation before use.\
> **Stack profile:** Cap-Core by default; Cap+Security and Cap+Chaos are
> optional extensions.\
> **Footprint:** measure yours. The planning envelope is approximately 4
> CPU / 8 GB RAM / 30 GB disk, not a promise that all components fit
> simultaneously.\
> **Scope:** lab-scale security and release assessment. A passing result
> is not certification of production security, regulatory compliance, or
> enterprise threat resistance.

------------------------------------------------------------------------

## Unit 4 --- Security and release rubric

### M17 contract and unit boundary

M17 integrates, demonstrates, reviews, and assesses M01--M16. Unit 4
assesses the security and release properties of the end-to-end delivery
path. It does not re-teach the earlier modules and does not replace Unit
1's requirements, Unit 2's readiness checklist, Unit 3's
incident/recovery rubric, Unit 5's cost/reliability rubric, or Unit 6's
platform/delivery rubric.

**M17 stage exit criteria --- verbatim**

> deploy a service through the full tested pipeline; reconcile desired
> state from Git; apply identity and security controls; demonstrate
> metrics/logs/alerts; execute a failure, rollback, backup restore, and
> teardown; map every acceptance criterion to evidence.

**M17 evidence artifact set --- verbatim**

> capstone repository, architecture diagram, runbooks, CI/GitOps
> evidence, incident report, restore evidence, signed-off checklist.

**M17 pass rule --- verbatim**

> every criterion is demonstrated, evidence is committed or safely
> retained, and the lab is reproducible from its README/runbook.

Unit 4 contributes evidence to this contract; it cannot independently
certify the entire M17 capstone.

### Source hierarchy and M01--M16 handoffs

Use this authority order: (1) governing M17 syllabus prompt, (2)
supplied repository tree, (3) Unit 1 requirements/evidence contract, (4)
M01--M16 handoffs, and (5) official primary documentation for
version-sensitive technical details. Do not silently reconcile
conflicting documents.

  ---------------------------------------------------------------------
  Module                             Handoff consumed by Unit 4
  ---------------------------------- ----------------------------------
  M01                                Image construction, registry,
                                     image identity, digest and
                                     retention

  M02                                CI/CD workflow, test stages,
                                     quality gates, build identity and
                                     pipeline permissions

  M03                                Operational procedures and safe
                                     diagnostics

  M04                                Network boundaries, ingress, DNS
                                     and TLS

  M05                                Stateful workload and storage
                                     context; security must preserve
                                     data integrity

  M06                                Helm or Kustomize packaging and
                                     rendered-manifest review

  M07                                Declarative infrastructure and
                                     controlled change

  M08                                GitOps desired state, Argo CD
                                     reconciliation, promotion and
                                     rollback

  M09                                Secrets, identity, RBAC and least
                                     privilege

  M10                                SRE, incident response, SLOs,
                                     error budgets, postmortems and ORR

  M11                                Metrics, logs, dashboards and
                                     alert evidence

  M12                                Security controls,
                                     dependency/supply-chain concepts,
                                     scanning and provenance awareness

  M13                                Backup, disaster recovery and safe
                                     fault injection

  M14                                Multi-cluster concepts; awareness
                                     only in the local core profile

  M15                                Capacity and FinOps; security
                                     evidence must not create
                                     uncontrolled cost

  M16                                Platform conventions and golden
                                     paths; optional reuse only.
                                     Backstage and Crossplane are not
                                     required.
  ---------------------------------------------------------------------

**Stack discipline**

-   **Cap-Core:** kind + Argo CD + minimal Prometheus/Grafana + local
    registry + backup tooling. Demonstrate digest-based artifact
    identity even when signing is not enabled.
-   **Cap+Security:** Cap-Core plus one policy engine and cosign where
    feasible. Do not run two policy engines or multiple GitOps
    controllers at once.
-   **Cap+Chaos:** Cap-Core plus one chaos tool or scripted benign fault
    injection, not both by default.
-   Start with Cap-Core. Measure host/container CPU, memory and disk
    before bootstrap and during the lab. Stop optional components when
    not needed. Do not invent resource-footprint values.
-   WSL2 and native Linux can differ in networking, filesystem
    performance, permissions, cgroups and container-runtime behavior.
    Record the actual host environment.
-   No paid service, cloud account, GPU, public endpoint or real
    production credential is required. Optional cloud use requires
    separate approval and the M17 cost-safety gate; budgets are alerts,
    not caps.

**Local-lab fidelity boundary:** a laptop `kind` cluster demonstrates
mechanics, repeatability and evidence discipline at lab scale. It does
not prove real multi-region behavior, real cloud limits, production
traffic capacity, enterprise identity federation, regulatory compliance,
production security, or managed-cloud controls.

### Unit 1 requirement and acceptance interfaces

Unit 1 is canonical for requirement IDs, acceptance-criterion IDs,
status semantics and the evidence-index schema. Unit 4 does not create
new `REQ-*` or `AC-*` identifiers.

  ----------------------------------------------------------------------
  Unit 1 ID              Canonical meaning      Unit 4 relationship
  ---------------------- ---------------------- ------------------------
  `REQ-001`              Build, test, publish   Pipeline/security-gate
                         and deploy through the evidence
                         documented CI pipeline 

  `REQ-002`              Record immutable       Artifact identity and
                         image/model artifact   promotion verifier
                         identity by            
                         digest/hash            

  `REQ-003`              Build, test and        Required-check and gate
                         security gates run     evidence
                         before promotion       

  `REQ-004`--`REQ-005`   Git desired state;     GitOps release-path
                         Argo CD                evidence
                         reconciliation/drift   

  `REQ-006`              Workload/operator      RBAC and
                         identities use least   workload-identity
                         privilege              evidence

  `REQ-007`              CI credentials are     CI permissions and
                         scoped; secrets are    secret-handling evidence
                         not hard-coded         

  `REQ-008`              No plaintext secrets   Secret scan and
                         in Git, images or logs planted-canary negative
                                                test

  `REQ-009`              Workloads use non-root Runtime-hardening
                         and restrictive        evidence
                         settings where         
                         compatible             

  `REQ-010`              Network access is      Network-policy and
                         limited to declared    connectivity evidence
                         dependencies           

  `REQ-021`              Clean clone bootstraps Reproducibility of the
                         and verifies the       security/release checks
                         selected local profile 

  `REQ-022`--`REQ-027`   Traceability,          Evidence integrity and
                         provenance, checksums, checker evidence
                         validators and         
                         planted-defect tests   

  `REQ-030`              Tool versions          Digest identity and
                         recorded; deployment   version record
                         promotes digests, not  
                         mutable tags           

  `REQ-031`              Preflight/context      Safety boundary for lab
                         guard refuses          verification
                         unexpected context     

  `REQ-032`              Risks, assumptions,    Risk acceptance and
                         non-goals, ADRs,       scope decisions
                         milestones and cloud   
                         gate recorded          
  ----------------------------------------------------------------------

  ----------------------------------------------------------------------
  Unit 1 AC             Canonical scope          Unit 4 use
  --------------------- ------------------------ -----------------------
  `AC-001`              CI delivery              CI security and
                        (`REQ-001`--`REQ-003`)   release-gate evidence

  `AC-002`              GitOps reconciliation    Desired-state and
                        (`REQ-004`--`REQ-005`)   release promotion
                                                 evidence

  `AC-003`              Identity/RBAC            Least-privilege and
                        (`REQ-006`, `REQ-009`)   workload-hardening
                                                 evidence

  `AC-004`              Secret hygiene           Secret-scan and
                        (`REQ-007`--`REQ-008`)   planted-canary evidence

  `AC-006`              Incident investigation   Cross-reference only;
                        (`REQ-015`)              Unit 3 owns incident
                                                 scoring

  `AC-007`              Rollback (`REQ-016`)     Release rollback
                                                 evidence; coordinate
                                                 with Unit 3/6

  `AC-010`              ML artifact identity     Model/image digest
                        (`REQ-002`, `REQ-030`)   binding

  `AC-012`              Fresh clone/traceability Reproducible security
                        (`REQ-021`--`REQ-031`)   checks and evidence
  ----------------------------------------------------------------------

**Cross-document discrepancy to preserve:** the supplied Unit 3 document
contains an older conflicting Unit 1 crosswalk in which `REQ-008` is
described as controlled failure, `REQ-009` as rollback, and subsequent
IDs are shifted. The completed Unit 1 register is authoritative:
`REQ-008` is plaintext-secret prevention; `REQ-015` is controlled
failure investigation; `REQ-016` is Git-controlled rollback; `REQ-017`
is backup/restore; `REQ-018` is restore integrity and measured RPO/RTO.
Unit 4 uses the Unit 1 meanings and does not edit Unit 3.

**Scoring-convention note:** Unit 3 and Unit 6 use a 0--3 criterion
rating scale; Unit 5 uses a different percentage mapping for its four
learning levels. Unit 4 uses an explicit 0--3 criterion rating scale and
reports its score as a Unit 4 result only. Do not aggregate percentage
scores across units until the M17 owner defines one shared scoring
convention.

------------------------------------------------------------------------

### 4.0 Why this matters in production

Security is a property of the entire delivery path, not a scanner
installed in CI or a policy file committed to Git. A release can pass a
build, produce a green scan badge and still be unsafe if the scan was
not a required check, the findings were ignored, the signer identity was
wrong, the SBOM described another artifact, or the deployed workload
used a different digest.

Release integrity is also a reliability control. During an incident,
responders need to know which source revision, build, image, model
artifact and configuration are running. Without that chain, a rollback
can restore the wrong image, an incident timeline can point to the wrong
change, and a security investigation cannot bound the affected
deployment.

This rubric assesses five connected domains:

1.  **Identity:** who or what can read, change, build, publish, promote
    or run the service.
2.  **Secrets:** whether credentials are kept out of source, images,
    logs and evidence, and whether exposure can be contained.
3.  **Supply chain:** whether dependencies, build inputs, SBOM,
    provenance and artifact identity are reviewable.
4.  **Runtime hardening:** whether workloads run with appropriately
    restricted identity, privilege, filesystem and network access.
5.  **Release integrity:** whether the artifact tested is the artifact
    promoted and deployed, and whether the release can be verified and
    rolled back.

The central test is not "does a security control exist?" It is "does the
control apply to this release, does it enforce the intended behavior,
can a safe negative test demonstrate that it rejects the unsafe case,
and is the evidence bound to the exact commit/artifact/deployment under
review?"

### 4.1 Learning objectives (6--10, tagged L1--L4)

1.  **\[L1\]** Distinguish security intent, implementation, enforcement,
    test execution, evidence and risk acceptance.
2.  **\[L1\]** Explain the release lifecycle and identify evidence
    required at every transition from commit to rollback.
3.  **\[L2\]** Implement secret hygiene, least-privilege identity,
    runtime hardening and pipeline permissions with positive and
    negative tests.
4.  **\[L2\]** Produce an SBOM and bind it to the exact built artifact
    digest; explain the limits of an SBOM.
5.  **\[L2\]** Compare registry, GitOps desired-state and
    running-workload digests, failing closed on missing, tag-only,
    malformed or mismatched values.
6.  **\[L3\]** Design risk-based controls and vulnerability triage using
    exploitability/reachability reasoning, compensating controls, owners
    and expiry.
7.  **\[L3\]** Evaluate fail-open/fail-closed choices, policy rollout,
    developer friction and local-lab fidelity.
8.  **\[L4\]** Review a synthetic flawed release, independently
    challenge evidence, calibrate scores and issue a defensible go/no-go
    recommendation with conditions.
9.  **\[L4\]** Lead a defensive supply-chain incident drill: contain,
    revoke/rotate, rebuild from a trusted source, re-verify and
    communicate.

### 4.2 Concept map and vocabulary

#### Release path and trust boundaries

``` mermaid
flowchart LR
  DEV["Developer workstation"] --> SRC["Source Git / reviewed commit"]
  SRC --> CI["CI identity: build, test, scan"]
  CI --> SBOM["SBOM + test/scan evidence"]
  CI --> REG["Registry: immutable digest"]
  CI -. "optional signature / attestation" .-> TRUST["Trusted signer / policy"]
  REG --> PROMO["Promotion record by digest"]
  TRUST -. "verify identity + subject" .-> PROMO
  PROMO --> GITOPS["GitOps repository / reviewed desired state"]
  GITOPS --> ARGO["Argo CD reconciliation"]
  ARGO --> K8S["kind lab cluster"]
  K8S --> RUN["Running workload image digest"]
  RUN --> VERIFY["Registry = GitOps = runtime verifier"]
  VERIFY --> REVIEW["Human release decision / rollback readiness"]
  CI --> EVIDENCE["Redacted evidence index"]
  K8S --> EVIDENCE
  REVIEW --> EVIDENCE
```

The workstation, source-control platform, CI runner, registry, GitOps
repository, cluster, workload and evidence store are separate trust
boundaries. A credential valid in one boundary must not automatically
grant authority in another. The source repository and GitOps repository
may be separate; record their distinct commit identities.

#### Vocabulary

  -----------------------------------------------------------------------------
  Term                     Meaning                 What to verify
  ------------------------ ----------------------- ----------------------------
  Source revision          Immutable identifier    Commit SHA and repository
                           for the source state    identity
                           used by a build         

  Build identity           CI run/workflow         Run ID, workflow revision,
                           identity and inputs     builder identity, timestamps
                           that produced an        
                           artifact                

  Image tag                Human-readable registry Never use as the sole
                           pointer that may be     release identity
                           mutable                 

  Artifact digest          Content-addressed       Exact digest in registry,
                           identifier for artifact GitOps and runtime
                           bytes                   

  SBOM                     Inventory of components SBOM subject matches the
                           in an artifact          artifact digest

  Provenance/attestation   Claims about            Trusted issuer, signer
                           how/where/by whom an    identity, subject digest and
                           artifact was built      policy

  Signature                Cryptographic binding   Expected signer/issuer is
                           to a subject under a    trusted for this
                           signer identity         repository/workflow

  Least privilege          Minimum permissions     Effective permissions and
                           required for a defined  denied-action tests
                           task                    

  Workload identity        Identity assigned to a  Service account, token
                           running                 audience/lifetime where
                           service/workload        applicable, RBAC

  RBAC                     Role-based              Actual
                           authorization rules     verbs/resources/namespaces
                                                   and harmless negative checks

  Secret scanning          Detection of likely     Scanner ran on relevant
                           credential material in  commit/build context; canary
                           configured scope        is detected

  Protected branch/release Controls on who can     Required checks,
  path                     merge/promote           reviewer/approval record and
                                                   branch policy evidence

  Admission policy         Cluster-side rule       A forbidden test object is
                           evaluated when an       denied or visibly flagged
                           object is admitted      

  Vulnerability triage     Risk decision based on  Finding identity, affected
                           severity, reachability, digest, disposition, owner
                           exploitability and      and expiry
                           context                 

  Immutable promotion      Moving the same         Digest equality; no rebuild
                           artifact identity       between stages
                           through environments    

  Fail closed              Uncertainty or failed   Negative test blocks release
                           control prevents the    or returns explicit blocker
                           protected action        

  Risk acceptance          Time-bounded decision   Owner, approver, rationale,
                           to tolerate a scoped    compensating control and
                           residual risk           expiry

  Release record           Auditable record of     Source SHA, build/run,
                           what was approved and   digest, GitOps revision,
                           deployed                reviewer and time

  Rollback                 Return to a prior       Reverted Git state,
                           known-good              reconciled revision, runtime
                           release/configuration   digest and smoke check
  -----------------------------------------------------------------------------

**Digest is identity, not trust.** A digest proves that two references
identify the same content under the hash algorithm. It does not prove
that the content is benign, that its source was trusted, that its build
was reproducible, that the signer was authorized, or that the
dependencies are safe.

**SBOM is inventory, not certification.** It helps identify components
and support vulnerability response. It is only relevant if it describes
the artifact under review. It does not prove the artifact is
vulnerability-free, complete, or correctly built.

**A valid signature is not sufficient by itself.** The reviewer must
verify the expected signer identity, issuer/trust root, subject digest
and policy context. A cryptographically valid signature from an
unexpected identity is not an authorized release.

#### Worked synthetic release example

**\[ILLUSTRATIVE --- fake values only; not an executed release\]**

  ----------------------------------------------------------------------------------------------------------------------------------
  Stage      Synthetic record                                                                                         Evidence
                                                                                                                      relationship
  ---------- -------------------------------------------------------------------------------------------------------- --------------
  Source     Commit `7f3a9c2e1d4b6a8f0c2e4d6b8a1f3c5e7d9b0a2c`                                                        Source
                                                                                                                      repository +
                                                                                                                      branch +
                                                                                                                      commit

  CI         Run `m17-ci-1842`                                                                                        Workflow
                                                                                                                      revision,
                                                                                                                      tests, scan,
                                                                                                                      builder
                                                                                                                      identity

  Artifact   `registry.local/m17/inference@sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`   Registry
                                                                                                                      digest

  SBOM       `sbom-inference.cdx.json` with subject digest above                                                      SBOM subject
                                                                                                                      and file
                                                                                                                      checksum

  GitOps     Desired image uses the same `@sha256:...` reference                                                      GitOps commit
                                                                                                                      and Argo
                                                                                                                      source
                                                                                                                      revision

  Runtime    Running workload reports the same normalized image digest                                                Read-only
                                                                                                                      cluster
                                                                                                                      evidence

  Review     All required checks and gates have evidence                                                              Reviewer, UTC
                                                                                                                      timestamp,
                                                                                                                      decision and
                                                                                                                      residual risks
  ----------------------------------------------------------------------------------------------------------------------------------

The values are deliberately synthetic. The example shows identity
linkage, not a real registry, build, signature or deployment.

#### Looks safe but is not proven

-   **"The scan passed."** The scan may have run against another commit
    or image, may not be a required check, or may have findings
    suppressed without an owner/expiry.
-   **"The signature verified."** The signature may belong to an
    unexpected signer or may refer to a different subject digest.
-   **"The SBOM exists."** It may describe a prior image, a source
    directory rather than the built artifact, or a different digest from
    the deployed workload.
-   **"The policy file is in Git."** The admission controller may not be
    installed, may be in audit mode, or may not evaluate the
    namespace/workload.
-   **"The workload is non-root."** A single setting does not prove
    minimal capabilities, safe filesystem permissions, secret handling
    or network isolation.

### 4.3 Level 1 --- Beginner

The learner first learns to read the release path as a chain of claims.
Each transition must have a record:

  -----------------------------------------------------------------------
  Transition              Claim                   Minimum evidence
  ----------------------- ----------------------- -----------------------
  Commit → build          This source revision    Repository, commit SHA,
                          was built               CI run identity

  Build → test            The produced candidate  Test result tied to run
                          was tested              and commit

  Test → scan             Security checks         Scanner/tool version,
                          evaluated the candidate scope, timestamp,
                                                  result

  Scan → sign/attest      The candidate was       Subject digest, signer
                          signed/attested if this identity, issuer/trust
                          profile enables it      policy, verification
                                                  result

  Publish                 The candidate exists in Repository and
                          the registry            immutable digest

  Promote                 The same artifact was   Promotion/change record
                          selected for the next   and digest
                          environment             

  Deploy via GitOps       Desired state           GitOps commit, Argo
                          references the approved source revision and
                          artifact                image digest

  Verify                  Running workload uses   Read-only runtime
                          the expected artifact   image/digest evidence
                                                  and smoke check

  Rollback                A prior known-good      Revert commit,
                          release was restored    reconciled revision,
                                                  runtime digest and
                                                  post-rollback
                                                  verification
  -----------------------------------------------------------------------

In Cap-Core, if signing is not enabled, record the explicit alternative:
build once, capture the registry digest, promote that digest through
GitOps, and compare the registry/GitOps/runtime values. This establishes
identity consistency only. It does not establish trusted builder
identity, signed provenance or supply-chain authorization.

A learner at L1 can explain why `:latest` is not stable identity,
identify the trust boundaries, distinguish a policy file from an
enforced control, and name the evidence required. L1 is a learning
outcome, not proof of a working security control.

### 4.4 Level 2 --- Intermediate

The learner implements the controls and collects repeatable evidence.

**Secret hygiene**

-   Keep credentials out of source, build context, image layers,
    environment dumps, logs, screenshots and evidence artifacts.
-   Use secret references or an approved local secret mechanism; never
    commit a real credential.
-   Run a scanner on the relevant repository/commit and, where
    applicable, build context.
-   Use a planted synthetic canary in a temporary directory to prove the
    scanner/gate is wired correctly.
-   Record scanner version, scope, run identity, exit status and
    redacted result. Review suppressions; broad allowlists can hide real
    exposure.
-   Define revoke/rotate steps for any real credential that is
    accidentally exposed. Never copy the credential into the incident
    record.

**Identity and least privilege**

-   Separate human, CI, GitOps-controller and workload identities.
-   Limit CI token permissions to the required operations. A workflow
    that only checks out and tests source should not receive registry
    write or deployment permissions.
-   Prefer short-lived identity federation where the provider supports
    it. If the local lab uses a static test credential, keep it
    disposable, narrowly scoped and outside source control.
-   Use dedicated service accounts and namespace-scoped RBAC where
    possible.
-   Verify both allowed and denied actions. A role name or manifest is
    not proof of effective permissions.

**Image and runtime hardening**

-   Use a minimal, maintained base image and pin the base by digest
    where the build system supports it. Record exceptions and update
    policy.
-   Run as non-root where compatible; avoid privileged mode and
    unnecessary Linux capabilities.
-   Use read-only root filesystem and an appropriate seccomp profile
    where supported by the workload/runtime.
-   Do not assume one `securityContext` field makes a container secure.
    Review mounts, writable paths, capabilities, service-account token
    mounting, host namespaces and network reachability.
-   Scan the exact built image; record scope, tool/database timestamp if
    available, and triage.

**Dependencies and SBOM**

-   Use lockfiles and hashes where the package ecosystem supports them.
-   Generate an SBOM for the exact built artifact, not an unrelated
    source snapshot.
-   Record SBOM checksum, image digest, build/run identity and tool
    version.
-   Compare the SBOM subject to the registry/deployed digest before
    relying on it.
-   Review dependency update cadence, transitive dependencies, source
    trust and build reproducibility.

**Pipeline and source-control security**

-   Make tests and security checks required checks for the protected
    release path.
-   Pin third-party actions to reviewed immutable commit SHAs where
    applicable; verify each pin against the upstream repository and
    update intentionally.
-   Declare minimal workflow permissions. Avoid `write-all`.
-   Do not pass protected secrets to untrusted pull-request code. Use a
    separate unprivileged validation path for forked/untrusted
    contributions.
-   Protect release branches and record approval/change history.
-   Detect skipped tests, ignored failures, `continue-on-error` misuse
    and conditions that allow promotion after a failed gate.

**Runtime/network controls**

-   Apply Kubernetes Pod Security Standards and security contexts
    appropriate to the workload.
-   Use NetworkPolicy to express required communication paths where the
    selected CNI enforces it. Verify actual CNI support; a manifest
    alone does not prove enforcement.
-   If using an admission policy engine, select one engine only and test
    both allowed and denied fixtures.
-   Keep optional policy engine/signature installation in Cap+Security;
    the core track must still prove digest identity.

**Release process**

-   Promote the same digest; do not rebuild per environment.
-   Update GitOps through a reviewed change.
-   Verify Argo CD source revision, health and reconciliation.
-   Compare registry digest, GitOps desired digest and running workload
    digest.
-   Keep a release record and prove rollback using the Git-controlled
    path. Coordinate rollback with Unit 3 and Unit 6; do not assume code
    rollback reverses data/schema changes.

### 4.5 Level 3 --- Advanced

#### Threat model → control → test → evidence → residual risk

For each service profile, identify:

1.  **Assets:** source code, image, model artifact, database data,
    credentials, CI secrets, GitOps state and release evidence.
2.  **Trust boundaries:** workstation, source-control platform, CI
    runner, registry, GitOps repository/controller, cluster, workload,
    telemetry and backup/evidence destination.
3.  **Actors:** developer, reviewer, CI identity, registry identity,
    GitOps controller, workload service account, operator and reviewer.
4.  **Entry points:** pull requests, dependency updates, build inputs,
    image publication, GitOps changes, admission requests, secret
    references and operator actions.
5.  **Failure/attack paths:** leaked test credential, mutable-tag
    change, untrusted dependency, compromised build output, unexpected
    signer, broad CI token, privilege escalation path or stale GitOps
    reference.
6.  **Controls:** narrow identity, protected change path, digest
    pinning, scanning, SBOM, optional signature/provenance, runtime
    policy and evidence validation.
7.  **Tests:** positive and negative cases, including deliberate but
    safe planted defects.
8.  **Residual risk:** what remains unproven, who owns it, compensating
    control, review trigger and expiry.

Do not turn this model into exploitation instructions. The objective is
defensive reasoning and test design.

#### Risk-based profile weighting

The base rubric weights remain fixed at 100. Do not redistribute weights
after seeing results. The table below changes reviewer emphasis and the
evidence sample selected, not the denominator.

  -----------------------------------------------------------------------
  Profile                 Higher-risk areas to    Conditional
                          inspect closely         considerations
  ----------------------- ----------------------- -----------------------
  Data service            Database credentials,   Database operator and
  (PostgreSQL)            storage access, backup  storage implementation
                          identity, network       vary; record actual
                          paths, data integrity   components
                          and restore             
                          compatibility           

  Scheduled               Service identity,       Job may not expose an
  pipeline/CronJob        secret access,          HTTP endpoint; do not
                          dependency inputs,      mark service-only
                          writable output paths,  checks as required
                          idempotent reruns and   
                          data-output integrity   

  ML inference service    Model source trust,     Model registry/format
                          model hash/digest,      and runtime differ; do
                          model/code pairing,     not assume a specific
                          runtime identity,       platform
                          artifact loading path   
                          and rollback of both    
                          code and model          

  Integrated capstone     Entire commit-to-deploy Requires cross-unit
                          chain, separation of    evidence but does not
                          duties, traceability    duplicate Unit 2/3/5/6
                          and consistent evidence scoring
                          across all workloads    
  -----------------------------------------------------------------------

#### Vulnerability triage and accepted risk

A scanner severity is an input, not the final decision. Record:

-   finding identifier exactly as emitted by the learner's scanner;
-   component/package and version;
-   affected artifact digest and scan scope;
-   scanner version and database/update timestamp if available;
-   severity as reported, plus exploitability and reachability
    reasoning;
-   whether the vulnerable component is present, loaded, reachable and
    exposed in this workload;
-   available fix/upgrade and compatibility risks;
-   compensating controls;
-   owner, approver, rationale, creation date, expiry and review
    trigger.

Use synthetic findings or results from the learner's own scan. Do not
invent CVE IDs, vulnerability details or scanner output. An accepted
risk without expiry is not accepted for this rubric; it is an unresolved
finding. An expired acceptance fails the relevant gate. Severity alone
does not justify ignoring a finding; "not reachable" requires evidence
and a reviewable rationale.

#### Enforcement versus documentation

  -----------------------------------------------------------------------
  State                   Example                 Rubric interpretation
  ----------------------- ----------------------- -----------------------
  Intent only             README says "all        No demonstrated control
                          workloads run non-root" 

  Configured              Manifest contains       Configuration evidence
                          `runAsNonRoot: true`    only

  Enforced                Admission/policy layer  Enforcement evidence
                          rejects a prohibited    
                          workload                

  Tested                  A safe prohibited       Positive/negative test
                          fixture is rejected and evidence
                          an allowed fixture      
                          succeeds                

  Bound to release        Test record identifies  Strong evidence for the
                          the same policy         current release
                          revision, workload and  
                          release                 
  -----------------------------------------------------------------------

A policy in audit mode can be useful during rollout, but it is not
equivalent to enforcement. State the mode and scope. Do not call it a
blocking gate until a denied fixture proves the gate blocks the request.

#### Fail closed versus fail open

Choose behavior by threat, blast radius and operational dependency:

-   A missing digest, digest mismatch, unexpected signer or missing
    required release approval should block promotion.
-   A required test or scanner failure should block promotion unless a
    pre-approved, time-bounded exception process explicitly covers the
    case.
-   If an optional signing service is unavailable in Cap-Core, the
    release must not pretend signature verification occurred; use the
    declared digest-only path and state its limits.
-   If a mandatory scanner service is unavailable, either stop promotion
    or use a formally approved alternative with equivalent scope and
    recorded residual risk. Do not silently skip the check.
-   A runtime policy engine outage may have different behavior depending
    on admission mode and workload criticality; document the selected
    fail behavior and test it in the lab.
-   Avoid universal claims that every component must always fail closed.
    The decision must be explicit, owned and tested.

#### Evidence freshness and anti-gaming

Bind evidence to commit SHA, build/run identity, artifact digest, GitOps
revision, deployment identity, timestamps and target environment where
possible. Refresh evidence after a relevant source, dependency,
workflow, policy, image, configuration or deployment change. A
screenshot without provenance is supporting context, not sufficient
proof.

Use reviewer-selected inputs and planted defects: synthetic secret,
`:latest`, wrong signer identity, broad RBAC, privileged pod, SBOM
subject mismatch, ignored finding, skipped check and digest mismatch. A
learner who knows the exact test fixture should still be required to
show that the gate rejects the defect class, not merely one hard-coded
string.

#### Four worked review examples

1.  **Scanner findings ignored:** the workflow contains a scan step and
    is green, but a synthetic high-risk finding is suppressed without
    rationale/expiry. The scan's existence is not enough; the criterion
    is capped or failed until triage and gate behavior are evidenced.
2.  **Signature verifies under wrong identity:** cryptographic
    verification succeeds, but the signer is not the approved
    workflow/repository identity. Treat as an integrity failure; do not
    promote.
3.  **Broad CI token:** a read-only test job has write permissions or
    access to deployment secrets. Reduce permissions, split
    jobs/identities and run an unauthorized-action check.
4.  **SBOM digest mismatch:** an SBOM exists but its subject digest
    differs from the image in GitOps/runtime. The SBOM cannot support
    claims about that deployed artifact; regenerate or correctly bind
    it.

### 4.6 Level 4 --- Expert

#### Release/security review procedure

1.  Confirm declared profile, service scope, owner, source repository,
    GitOps repository, commit SHA, CI run/build identity, registry
    repository, artifact digest, GitOps revision, deployed workload and
    rubric version.
2.  Inspect the trust-boundary diagram and credential/data flows.
3.  Verify required checks are configured and that the relevant
    tests/scans actually executed for the release under review.
4.  Confirm scan scope and artifact identity; inspect findings,
    suppressions, disposition, compensating controls and expiry.
5.  Confirm the SBOM subject is the exact artifact digest; review
    dependency lock/hash evidence where supported.
6.  If signing is enabled, verify the expected signer identity,
    issuer/trust policy, subject digest and provenance policy. A valid
    signature from an unexpected identity is a failure.
7.  Inspect human, CI, GitOps and workload permissions; run safe
    negative authorization checks.
8.  Inspect runtime hardening and network/admission enforcement; test
    allowed and denied fixtures.
9.  Independently compare registry digest, GitOps desired digest and
    running workload digest.
10. Review approval/change record, release notes, promotion history,
    post-deploy health and rollback proof.
11. Record blockers, residual risks, waivers, N-A decisions, owners, due
    dates and review triggers.
12. Decide `GO`, `GO_WITH_CONDITIONS` or `NO_GO` for the declared lab
    exercise. This is a human course decision, not a production
    certification.

#### Synthetic flawed submission --- learner copy

**\[SYNTHETIC SCENARIO\]** A team submits a release package for
`inference-api`. All names, values and defects below are fictional. The
learner should score the submission before reading the answer key.

  ---------------------------------------------------------------------------
                \# Submitted claim/evidence                Planted defect
  ---------------- --------------------------------------- ------------------
                 1 Secret scanner config exists in Git     No release
                                                           workflow invokes
                                                           it

                 2 Secret-scan job is green                Synthetic canary
                                                           in a disposable
                                                           fixture is not
                                                           detected

                 3 CI workflow uses broad write            Test-only job can
                   permissions                             publish or change
                                                           release state

                 4 Workload manifest has no privilege      Container runs as
                   restrictions                            root or requests
                                                           privileged mode
                                                           without
                                                           justification

                 5 Deployment image is                     Mutable tag is
                   `registry.local/inference-api:latest`   used as release
                                                           identity

                 6 Scanner report is attached              Serious synthetic
                                                           finding is
                                                           suppressed without
                                                           triage or expiry

                 7 SBOM file exists                        SBOM subject is a
                                                           different digest

                 8 Signature verification output is green  Signer identity is
                                                           not the expected
                                                           trusted identity

                 9 GitOps manifest uses digest A           Registry/runtime
                                                           evidence reports
                                                           digest B

                10 Rollback runbook is complete            No rollback
                                                           execution or
                                                           runtime
                                                           verification
                                                           exists

                11 Workflow uses a third-party action by   Declared policy
                   mutable tag                             requires immutable
                                                           pinning

                12 Pull-request workflow has access to     Untrusted code can
                   protected secrets                       execute in a
                                                           secret-bearing job

                13 NetworkPolicy/admission YAML exists     Enforcement is
                                                           disabled, out of
                                                           scope or not
                                                           tested

                14 Release marked approved                 No auditable
                                                           reviewer/change
                                                           record exists
  ---------------------------------------------------------------------------

#### Separated answer key

  ---------------------------------------------------------------------------------------------------------
    \# Risk                      Evidence needed to  Likely      Blocker?            Expected reviewer
                                 resolve             criterion                       decision
                                                     impact                          
  ---- ------------------------- ------------------- ----------- ------------------- ----------------------
     1 Secret control is not on  Workflow run and    SR-01,      Yes if required     No-Go until wired and
       the release path          required-check      SR-06       secret gate is      tested
                                 configuration                   absent              

     2 Scanner false-negative or Planted-canary test SR-01       Yes                 No-Go; fix
       misconfiguration          output showing                                      scanner/config
                                 detection and                                       
                                 blocked gate                                        

     3 CI identity blast radius  Effective           SR-02,      Yes if release path No-Go or isolate
       is excessive              permissions review  SR-06       can be altered by   before release
                                 and harmless                    an unnecessary      
                                 denied-action test              identity            

     4 Runtime privilege risk    Pod spec/runtime    SR-03,      Yes for unexplained No-Go until
                                 evidence and denied SR-08       privileged workload justified/restricted
                                 privileged fixture                                  

     5 Artifact identity can     Immutable digest in SR-05,      Yes                 No-Go
       change without review     registry, GitOps    SR-09                           
                                 and runtime                                         

     6 Known risk is             Finding record,     SR-07       Yes when policy     No-Go until
       unowned/unbounded         reachability                    says critical       disposition
                                 analysis, approver,             finding blocks;     
                                 compensating                    otherwise major     
                                 control and expiry              with explicit       
                                                                 approval            

     7 SBOM does not describe    SBOM subject and    SR-04       Major; gate if SBOM Do not claim SBOM
       deployed artifact         artifact digest                 is a required       coverage
                                 comparison                      release control     

     8 Untrusted signer could    Expected            SR-05       Yes when signature  No-Go
       authorize artifact        identity/trust                  is                  
                                 policy and                      selected/required   
                                 verification record                                 

     9 Registry/GitOps/runtime   Three-way verifier  SR-05,      Yes                 No-Go
       mismatch                  output and release  SR-09                           
                                 identity trace                                      

    10 Recovery path is unproven Rehearsed rollback  SR-09; Unit Yes for required    No-Go
                                 evidence and        3/6         M17 rollback        
                                 post-rollback       interface                       
                                 digest/smoke check                                  

    11 Action reference can move Reviewed full SHA   SR-06       Major or blocker by Fix before protected
                                 pin and update                  declared release    promotion
                                 record                          policy              

    12 Protected credential may  Workflow            SR-02,      Yes                 No-Go; rotate any
       be exposed to untrusted   event/permission    SR-06                           exposed credential
       code                      review and negative                                 
                                 test                                                

    13 Policy intent is not      Admission/network   SR-08       Gate if required by No credit for
       enforcement               negative test and               profile; otherwise  configuration alone
                                 policy mode/scope               not demonstrated    

    14 Approval is unauditable   Reviewer, role,     SR-09       Yes for protected   No-Go
                                 timestamp, scope,               release             
                                 decision, rationale                                 
                                 and change record                                   
  ---------------------------------------------------------------------------------------------------------

#### Calibration exercise

Two reviewers score the same synthetic evidence independently. The table
is illustrative, not a benchmark.

  ---------------------------------------------------------------------
  Criterion              Reviewer A        Reviewer B Evidence-based
                                                      resolution
  --------------- ----------------- ----------------- -----------------
  SR-01 Secrets                   2                 3 Canary test is
                                                      not shown on the
                                                      release workflow;
                                                      settle at 1 or 2
                                                      only if the
                                                      baseline evidence
                                                      is complete. Do
                                                      not award 3.

  SR-05 Artifact                  1                 2 Runtime digest
  integrity                                           differs from
                                                      GitOps; this is a
                                                      gate failure
                                                      regardless of
                                                      score.

  SR-07                           2                 2 Both agree the
  Vulnerability                                       finding has no
  triage                                              expiry; mark the
                                                      acceptance
                                                      invalid.

  SR-09 Release                   1                 2 Rollback was
  process                                             documented but
                                                      not executed; no
                                                      competent rating
                                                      for rollback
                                                      proof.
  ---------------------------------------------------------------------

Calibration procedure:

1.  Preserve each reviewer's original rating and evidence references.
2.  Identify the exact descriptor that caused disagreement.
3.  Re-read the artifact/run record, not just the submission narrative.
4.  Resolve against the observable descriptor; seniority does not decide
    the score.
5.  Record the final rating, reason, and any rubric wording that allowed
    ambiguity.
6.  If reasonable reviewers still disagree, revise the descriptor and
    re-score affected submissions. Do not average opinions to hide a
    gate failure.

#### Defensive supply-chain incident drill

**Scenario:** a synthetic test credential used by a local CI job is
reported as exposed in a test log, or a registry/GitOps/runtime digest
mismatch is detected. The exercise uses only the learner's own local lab
and synthetic data.

**Required actions**

1.  Stop the affected promotion path. Do not delete or overwrite
    evidence.
2.  Record the affected source commit, CI run, build identity, artifact
    digest, GitOps revision and known deployments.
3.  Preserve redacted workflow output, audit records and timestamps.
    Never print/copy the secret.
4.  Revoke/rotate the disposable test credential using the provider's
    documented mechanism; if no credential was actually used, record the
    tabletop decision.
5.  Identify which artifacts and environments may be affected. Mark
    uncertain scope explicitly.
6.  Rebuild from a trusted source revision after remediation.
7.  Re-run tests and scans; regenerate the SBOM for the new digest.
8.  Verify signature/provenance if enabled; otherwise perform the
    declared digest-only checks and state the trust limitation.
9.  Promote through GitOps, compare registry/GitOps/runtime digests, and
    perform a benign smoke test.
10. Communicate status, remaining uncertainty, owner and next review
    date.
11. Complete a blameless incident record and prevention actions.

**Timeline template**

  -------------------------------------------------------------------------------------------------
  Time (UTC)      Event/action            Evidence ID  Actor/role   Interpretation/uncertainty
  --------------- ----------------------- ------------ ------------ -------------------------------
  `<timestamp>`   Detection/report        `<EVD-ID>`   `<role>`     What is known vs assumed
                  received                                          

  `<timestamp>`   Promotion stopped       `<EVD-ID>`   `<role>`     Confirm no further promotion

  `<timestamp>`   Scope established       `<EVD-ID>`   `<role>`     Commit/run/digest/deployments

  `<timestamp>`   Credential              `<EVD-ID>`   `<role>`     No secret value in evidence
                  revoked/rotated or                                
                  tabletop decision                                 
                  recorded                                          

  `<timestamp>`   Trusted rebuild and     `<EVD-ID>`   `<role>`     New digest and checks
                  verification                                      

  `<timestamp>`   GitOps redeploy and     `<EVD-ID>`   `<role>`     Runtime identity
                  smoke verification                                

  `<timestamp>`   Communication/closure   `<EVD-ID>`   `<role>`     Residual risk and owner
                  decision                                          
  -------------------------------------------------------------------------------------------------

**Abort criteria:** wrong Kubernetes context/namespace; any real
credential or production data appears; target ownership is unclear; a
state-changing command would affect a non-lab resource; no
rollback/cleanup path exists; resource use destabilizes the host. Stop
and mark `NOT_DEMONSTRATED` rather than improvising.

**Scoring:** full credit requires containment evidence, scope record,
credential handling without secret disclosure, trusted rebuild,
test/scan evidence, artifact identity verification, GitOps
reconciliation, communication and prevention actions. A tabletop can
demonstrate reasoning but must not be represented as a live credential
revocation or deployment.

### 4.7 SRE lens

Security and reliability intersect in the release path:

-   A wrong or untraceable artifact invalidates rollback assumptions and
    makes incident reconstruction harder.
-   Define user-facing SLI/SLO and post-deploy health checks for the
    service. The security rubric does not prescribe universal SLO
    targets or alert thresholds.
-   Monitor for suspicious artifact identity changes, unexpected
    workload identity, secret-scan findings, failed policy checks and
    release-gate bypasses.
-   Correlate CI run, commit, artifact digest, GitOps revision,
    Kubernetes workload and telemetry by identity/time.
-   Decide what happens when scanners, registries, signature services or
    policy controllers are unavailable. A required control must not be
    silently skipped.
-   Rollback code and model artifact together where relevant. Do not
    assume rollback reverses irreversible schema/data changes.
-   Integrate with M10/M13 incident and recovery practice: timeline,
    impact, evidence preservation, owner, actions, review dates and
    no-blame analysis.

**Runbook minimum:** trigger; impact; prerequisites; safe diagnostics;
target context/namespace; containment; credential revoke/rotation;
trusted rebuild; verification; rollback/recovery; communication;
evidence capture; escalation.

**Illustrative digest-mismatch runbook**

1.  Trigger: registry, GitOps and runtime digest values do not match.
2.  Impact: pause promotion; do not assume which value is correct.
3.  Prerequisites: identify the lab profile, namespace, owner, source
    SHA and last approved release record.
4.  Diagnostics: use read-only registry metadata, GitOps revision and
    explicitly context-scoped workload inspection.
5.  Decision: preserve all three values; identify whether the mismatch
    is stale evidence, an unreviewed GitOps change or a different
    running image.
6.  Recovery: restore the approved GitOps revision or rebuild/re-promote
    from the trusted source; do not mutate the cluster imperatively as a
    shortcut.
7.  Verification: re-run the three-way digest verifier and benign smoke
    check.
8.  Evidence: timestamped values, run ID, GitOps commit, reviewer and
    result.

### 4.8 Security lens

  --------------------------------------------------------------------------------------------------------
  Boundary                 Threat/failure      Control              Positive         Negative test
                                                                    evidence         
  ------------------------ ------------------- -------------------- ---------------- ---------------------
  Developer                Secret accidentally Secret hygiene,      Scan result and  Synthetic canary is
  workstation/source       committed           local scanning,      clean commit     detected
                                               redaction                             

  Source control           Unreviewed/unsafe   Protected branch,    Branch/ruleset   Missing
                           change              required checks,     evidence and PR  check/approval blocks
                                               reviewer             record           merge/promotion

  CI runner                Broad token or      Minimal permissions, Workflow         Untrusted PR receives
                           untrusted PR access separated jobs,      permissions and  no protected secret
                                               short-lived identity run identity     
                                               where supported                       

  Dependency/build inputs  Untrusted or        Lockfiles/hashes,    Lockfile and     Changed/unlocked
                           drifting dependency review, reproducible build metadata   dependency is flagged
                                               build inputs                          

  Registry                 Mutable or          Access control,      Registry digest  Tag-only/mismatched
                           unauthorized        digest identity,     and publication  digest is rejected
                           artifact            retention            identity         

  GitOps controller        Unauthorized        Scoped               GitOps commit,   Unapproved revision
                           desired-state       repository/project   Argo source      is blocked/flagged
                           change              permissions and      revision         
                                               review                                

  Cluster/admission        Privileged or       PSS/security context Effective policy Privileged fixture is
                           unsafe workload     and one optional     mode and denied  denied/flagged
                                               admission engine     fixture          

  Workload/network         Excess permissions  Dedicated service    Role rules,      Harmless unauthorized
                           or lateral          account, RBAC,       identity,        action/connectivity
                           reachability        NetworkPolicy        allowed-path     is denied
                                                                    tests            

  Observability/evidence   Secret leakage or   Redaction,           Redaction review Synthetic secret
                           tampered evidence   checksums, access    and evidence     marker in evidence is
                                               control, timestamps  index            rejected

  Backup/evidence          Credential/data     Separate identity,   Access record    Unauthorized
  destination              exposure            least privilege,     and redacted     read/write is denied
                                               retention            inventory        where testable
  --------------------------------------------------------------------------------------------------------

**Defensive-only boundary:** no real-target scanning, exploitation,
persistence, evasion, credential theft, malicious dependency injection
or unauthorized access. All negative tests use synthetic fixtures,
harmless authorization queries, policy simulation or the learner's
isolated lab.

### 4.9 Full security and release rubric

#### Performance levels and scoring convention

The learning pathway is L1 Beginner, L2 Intermediate, L3 Advanced and L4
Expert. For criterion scoring, use the same four labels with explicit
evidence anchors:

-   **L1 --- Beginner / Not demonstrated (rating 0):** identifies the
    control and evidence, but the implementation is absent, unsafe or
    unsupported by evidence.
-   **L2 --- Intermediate / Emerging (rating 1):** partial
    implementation exists; evidence is incomplete, manual, stale or
    lacks a required negative test.
-   **L3 --- Advanced / Competent (rating 2):** control is implemented,
    applicable tests pass, required negative tests fail safely, and
    evidence is current and bound to the release.
-   **L4 --- Expert / Strong (rating 3):** independent review confirms
    scope, enforcement, negative-test coverage, freshness, residual-risk
    handling and reproducibility across the declared profile.

For criterion weight (W) and rating (r `\in`{=tex}{0,1,2,3}):

\[ `\text{points}`{=tex} = `\operatorname{round}`{=tex}`\left`{=tex}(W
`\times`{=tex}`\frac{r}{3}`{=tex}, 2`\right`{=tex}) \]

Round each criterion to two decimal places using the scoring script's
standard rounding policy; total the rounded criterion values. The
weights remain fixed at 100. N-A receives zero points and does not
reduce or redistribute the denominator. It is allowed only for a
profile-conditional criterion, with rationale and reviewer approval.

**\[ASSUMPTION --- course threshold, not an industry standard\]** A
numeric Unit 4 score of 70/100 is the minimum score for a
`READY_FOR_HUMAN_REVIEW` recommendation. This threshold never overrides
non-waivable gates, missing mandatory evidence, or the M17 pass rule.
All mandatory criteria must be at least L3/Competent for the unit to be
considered demonstrated.

#### Rubric summary

  --------------------------------------------------------------------------------
  ID          Criterion           Weight Critical   Primary evidence
                                         gate       
  ----------- ---------------- --------- ---------- ------------------------------
  SR-01       Secrets hygiene         12 Yes        Secret scan, synthetic-canary
              and exposure                          negative test,
              response                              rotation/revocation procedure

  SR-02       Identity and            12 Yes        CI permissions, workload
              least privilege                       identity/RBAC audit,
                                                    denied-action test

  SR-03       Image and               10 Yes        Image metadata/scan,
              runtime                               non-root/security context,
              hardening                             privileged-fixture denial

  SR-04       Dependency              10 No         Lockfiles/hashes, SBOM, SBOM
              control and SBOM                      subject digest comparison
              binding                               

  SR-05       Artifact                14 Yes        Registry/GitOps/runtime digest
              integrity and                         match; signature/trust record
              provenance                            if selected

  SR-06       Pipeline and            12 Yes        Required checks, action pins,
              source-control                        permissions, protected path,
              security                              PR isolation

  SR-07       Vulnerability           10 No         Finding register, reachability
              triage and                            rationale,
              accepted risk                         expiry/approver/compensating
                                                    control

  SR-08       Runtime, network        10 Yes        PSS/security context, network
              and admission                         tests, policy enforcement
              controls                              evidence

  SR-09       Release process,        10 Yes        Promotion/change record,
              approval and                          post-deploy check, executed
              rollback                              rollback evidence

  **Total**                      **100**            
  --------------------------------------------------------------------------------

#### Observable performance descriptors

  ---------------------------------------------------------------------------------------------------------------------------------------------------
  Criterion          Weight L1 --- Beginner / Not    L2 --- Intermediate / Emerging L3 --- Advanced / Competent L4 --- Expert / Strong
                            demonstrated                                                                        
  ---------------- -------- ------------------------ ------------------------------ --------------------------- -------------------------------------
  **SR-01 Secrets        12 Can identify secret      Scanner/config exists and      Scanner runs on the release Reviewer-selected canary variants are
  hygiene**                 locations but has no     baseline run is recorded;      path; synthetic canary is   detected; suppression review is
                            complete scan scope or   canary test, image/log review  detected and blocks;        controlled; evidence proves no secret
                            exposure procedure.      or revocation procedure is     source/image/log/evidence   value was emitted; exposure scope and
                                                     incomplete.                    checks and redaction are    credential lifecycle are
                                                                                    evidenced; revoke/rotate    independently challenged.
                                                                                    procedure is rehearsed or   
                                                                                    safely table-topped.        

  **SR-02 Identity       12 Identities/permissions   Roles/service accounts are     Human, CI, GitOps and       Reviewer challenges effective
  and least                 are undocumented or      declared, but effective        workload identities are     permissions and trust boundaries,
  privilege**               broad.                   permissions, CI token scope or separated as applicable;    checks namespace/audience/lifetime
                                                     denied-action evidence is      RBAC is audited;            where relevant, and proves
                                                     incomplete.                    short-lived identity is     unnecessary privilege cannot be
                                                                                    used where supported;       exercised.
                                                                                    harmless unauthorized       
                                                                                    action is denied.           

  **SR-03                10 Image/runtime settings   Minimal/pinned base and        Exact image is scanned and  Reviewer-selected workload/config
  Image/runtime             are unreviewed;          security context are partially triaged; base pinning is    variants prove enforcement;
  hardening**               root/privileged behavior configured; scan/negative-test recorded where supported;   exceptions have
                            is unexplained.          evidence incomplete.           workload runs non-root with owner/rationale/expiry; limitations
                                                                                    least capabilities and      of the runtime/CNI are explicit.
                                                                                    appropriate                 
                                                                                    filesystem/security         
                                                                                    settings; privileged        
                                                                                    fixture is denied/flagged.  

  **SR-04                10 Dependencies are not     Lockfiles or SBOM exist, but   Dependencies are reviewed   Reviewer independently regenerates or
  Dependency                traceable; no            hashes, tool/run metadata or   and locked/hashed where     spot-checks SBOM identity, tests
  control and SBOM          artifact-bound SBOM.     subject digest linkage is      supported; SBOM is          dependency drift and explains
  binding**                                          incomplete.                    generated for the built     completeness/coverage limits.
                                                                                    artifact; subject digest    
                                                                                    matches the promoted        
                                                                                    artifact; mismatch test     
                                                                                    fails.                      

  **SR-05 Artifact       14 Release uses mutable tag Registry digest exists but     Registry, GitOps and        Independent verifier catches
  integrity and             or artifact identity is  GitOps/runtime comparison or   running digests match;      missing/tag-only/malformed/mismatch
  provenance**              missing.                 promotion record is            promotion uses immutable    cases; reviewer traces
                                                     incomplete; optional signing   digest; if signing is       source/build/artifact/deployment
                                                     status unclear.                enabled, expected           identities and challenges signer
                                                                                    identity/issuer/subject     trust, not just cryptographic
                                                                                    policy verifies; Cap-Core   validity.
                                                                                    documents digest-only       
                                                                                    limitations.                

  **SR-06 Pipeline       12 Checks are               Some required checks and       Required checks gate        Reviewer plants
  and                       optional/skippable;      minimal permissions exist, but promotion; actions are      skipped-check/permission/PR defects
  source-control            workflow permissions and action pinning, branch         pinned to reviewed          and proves they are blocked; change
  security**                PR secret handling are   protection or untrusted-PR     immutable SHAs where        control and action-pin update process
                            unsafe or unknown.       separation is incomplete.      applicable; permissions are are repeatable.
                                                                                    minimal; protected          
                                                                                    branches/release path and   
                                                                                    PR secret isolation are     
                                                                                    evidenced.                  

  **SR-07                10 Scan output is treated   Findings are listed, but       Findings are tied to the    Reviewer challenges suppression and
  Vulnerability             as a green/red badge;    reachability/exploitability,   artifact digest and scan    stale database context, tests expiry
  triage and                findings lack            affected digest, owner,        context; severity and       behavior, and rejects unsupported
  accepted risk**           disposition.             compensating control or expiry reachability are reasoned;  "not reachable" claims.
                                                     is incomplete.                 accepted risk has owner,    
                                                                                    approver, scope, rationale, 
                                                                                    compensating control and    
                                                                                    expiry.                     

  **SR-08 Runtime,       10 Policy exists only as    PSS/security context or        Runtime restrictions are    Reviewer-selected allowed/denied
  network and               prose/config; effective  NetworkPolicy is configured,   inspected; network paths    fixtures verify enforcement and blast
  admission                 enforcement is unknown.  but CNI/policy mode or denied  are declared and tested     radius; exceptions and failure
  controls**                                         fixture is not demonstrated.   where supported; one        behavior are versioned and
                                                                                    optional admission engine   independently reviewed.
                                                                                    denies a prohibited fixture 
                                                                                    or the limitation is        
                                                                                    documented with approved    
                                                                                    N-A.                        

  **SR-09 Release        10 No traceable             Release record exists but      Change/approval record ties Reviewer replays the release
  process,                  approval/promotion or    post-deploy verification,      source SHA, build/run,      evidence, challenges data/schema
  approval and              rollback evidence.       approval provenance or         digest and GitOps revision; compatibility, verifies abort
  rollback**                                         executed rollback is           post-deploy health is       criteria and independently validates
                                                     incomplete.                    checked; Git-controlled     rollback/re-promotion.
                                                                                    rollback is executed and    
                                                                                    runtime identity verified.  
  ---------------------------------------------------------------------------------------------------------------------------------------------------

#### Criterion verification contracts

  ---------------------------------------------------------------------------------------------------------------------------------
  ID      Verification method    Required evidence                 Negative test / fail condition          Profile applicability
  ------- ---------------------- --------------------------------- --------------------------------------- ------------------------
  SR-01   Secret scanner on      Scanner config/version/scope/run, Synthetic canary not detected or gate   Required all profiles
          source/build context;  redacted result, canary result,   remains green                           
          image/log/evidence     exposure runbook                                                          
          review; canary fixture                                                                           

  SR-02   RBAC audit; workflow   Role/RoleBinding/ServiceAccount   Unnecessary action is allowed or CI     Required all profiles
          permission review;     review, workflow permissions,     receives broader permissions than       
          harmless `auth can-i`  identity notes                    declared                                
          queries                                                                                          

  SR-03   Image inspection/scan; Base image identity, image        Privileged/root fixture not             Required all profiles;
          workload spec/runtime  digest, scan/triage, pod security flagged/denied under declared policy    exceptions need
          inspection; admission  settings                                                                  rationale
          test where selected                                                                              

  SR-04   Lockfile/hash review;  Lockfiles, SBOM, checksum,        SBOM subject differs from               Required where
          SBOM generation;       build/run and subject digest      promoted/runtime digest                 dependencies/artifacts
          subject digest                                                                                   exist; ML model
          comparison                                                                                       inventory may need
                                                                                                           separate format

  SR-05   Three-way digest       Registry digest, GitOps           Missing/tag-only/malformed/mismatched   Required all profiles;
          verifier; optional     commit/image, runtime digest,     digest; wrong signer identity           signature only if
          signature/provenance   promotion record; trust policy if                                         Cap+Security selected
          verifier               enabled                                                                   

  SR-06   Workflow/static policy Workflow revision, run ID, branch Skipped/ignored required check, broad   Required all profiles
          review; required-check rules, action pin list,           permissions, protected secret exposed   
          evidence; PR           permission record                 to untrusted PR                         
          event/permission                                                                                 
          review                                                                                           

  SR-07   Finding triage review  Finding ID, affected digest,      Expired or ownerless accepted risk;     Required when findings
          and expiry validation  scanner context, reachability     finding silently suppressed             exist; no invented CVEs
                                 rationale, owner/approver/expiry                                          

  SR-08   PSS/security context   Policy version/mode/scope, CNI    Prohibited workload or unauthorized     Required controls where
          inspection;            support, allowed/denied fixture   path succeeds where control is declared supported; capability
          NetworkPolicy test;    outputs                           enforced                                gaps must be explicitly
          optional admission                                                                               N-A approved
          engine test                                                                                      

  SR-09   Release record, GitOps Approval, source SHA, run/build,  Missing approval, tag-only release,     Required all profiles
          history, post-deploy   digest, GitOps revision, rollback untested/failed rollback                
          smoke check and Git    SHA/runtime digest                                                        
          rollback                                                                                         
  ---------------------------------------------------------------------------------------------------------------------------------

#### Non-waivable release gates

A numeric score cannot average away these failures:

1.  **G-01 --- Secret exposure:** a real credential/private key or
    sensitive production data is found in source, image, log or
    evidence. Stop; revoke/rotate; assess scope; preserve redacted
    evidence. This cannot be waived.
2.  **G-02 --- Artifact identity mismatch:** registry, GitOps desired
    state and running workload do not identify the same artifact, or
    identity is missing/tag-only. Stop promotion/release until resolved.
3.  **G-03 --- Required checks bypassed:** a required test/security gate
    failed, was skipped or was ignored and the artifact was still
    promoted. Stop release.
4.  **G-04 --- Untrusted PR receives protected secrets:** any protected
    credential is exposed to untrusted pull-request code. Stop,
    revoke/rotate and remediate workflow boundaries.
5.  **G-05 --- Unexplained privileged runtime:** a workload is
    privileged or has unjustified broad capabilities/permissions and the
    declared policy does not permit it.
6.  **G-06 --- Evidence fabrication/tampering:** fabricated, doctored or
    knowingly misbound evidence. Integrity failure; score is not
    meaningful until reviewed.
7.  **G-07 --- Required rollback not demonstrated:** M17 requires
    rollback execution and verification. A runbook alone is not proof.
    Coordinate with Unit 3 and Unit 6.

A missing signature is not automatically a gate failure in Cap-Core
because signing is optional/Awareness in the governing scope. If
Cap+Security selects signature verification as a required control, then
missing/invalid signature or wrong signer identity blocks that selected
profile.

#### Scoring example

**Representative example --- your output will differ.** The numbers are
synthetic.

  Criterion      Weight   Rating Calculation        Points
  ----------- --------- -------- ------------- -----------
  SR-01              12        3 12 × 3/3            12.00
  SR-02              12        2 12 × 2/3             8.00
  SR-03              10        2 10 × 2/3             6.67
  SR-04              10        2 10 × 2/3             6.67
  SR-05              14        1 14 × 1/3             4.67
  SR-06              12        2 12 × 2/3             8.00
  SR-07              10        2 10 × 2/3             6.67
  SR-08              10        2 10 × 2/3             6.67
  SR-09              10        1 10 × 1/3             3.33
  **Total**     **100**                          **62.68**

The result is below the assumed 70-point threshold. In addition, SR-05
is only emerging and the release/rollback evidence is incomplete. If
G-02 or G-07 is actually failed, the result is `BLOCKED` regardless of
the numeric score.

### 4.10 Automated scoring and release-evidence verification

The following code is educational implementation content for the
learner's separate capstone implementation repository. It does not
create additional learning-roadmap files. All examples are unexecuted in
this document; verify dependency versions and run the tests in the
learner's isolated repository.

#### 4.10.1 Machine-readable rubric YAML

``` yaml
# File: security/rubric.yaml
schema_version: "1"
unit: "M17-U4"
title: "Security and release rubric"
scoring:
  scale_min: 0
  scale_max: 3
  formula: "round(weight * rating / 3, 2)"
  rounding: "two decimal places per criterion; sum rounded criterion points"
  weights_total: 100
  assumed_numeric_threshold: 70
  threshold_label: "[ASSUMPTION — course threshold, not industry standard]"
  na_policy: "zero points; no denominator redistribution; reviewer approval required"
profiles:
  - data_service
  - scheduled_pipeline
  - ml_inference
  - integrated_capstone
criteria:
  - id: SR-01
    name: "Secrets hygiene and exposure response"
    weight: 12
    critical_gate: true
    non_waivable: true
    human_review_required: true
    applicability:
      data_service: required
      scheduled_pipeline: required
      ml_inference: required
      integrated_capstone: required
    evidence:
      - secret_scan
      - synthetic_canary_negative_test
      - redaction_review
      - exposure_response_runbook
    verification: "Secret scanner on relevant source/build scope; inspect images/logs/evidence; verify canary failure."
    negative_test: "NT-01 synthetic canary is detected and the gate blocks."
    levels:
      L1: "No complete scan scope or exposure procedure."
      L2: "Baseline scan exists; canary/gate or response evidence incomplete."
      L3: "Release-path scan, canary block, redaction and response procedure evidenced."
      L4: "Reviewer-selected canaries and suppression review independently verified."
  - id: SR-02
    name: "Identity and least privilege"
    weight: 12
    critical_gate: true
    non_waivable: true
    human_review_required: true
    applicability:
      data_service: required
      scheduled_pipeline: required
      ml_inference: required
      integrated_capstone: required
    evidence:
      - ci_permissions
      - workload_identity
      - rbac_audit
      - denied_action_test
    verification: "Review effective CI/workload permissions and run harmless authorization queries."
    negative_test: "NT-06 unnecessary action is denied."
    levels:
      L1: "Identities and permissions are undocumented or broad."
      L2: "Roles exist but effective permissions or denied-action evidence is incomplete."
      L3: "Identities are separated, least privilege is evidenced and denied action is proven."
      L4: "Reviewer independently challenges identity scope, trust boundaries and privilege."
  - id: SR-03
    name: "Image and runtime hardening"
    weight: 10
    critical_gate: true
    non_waivable: true
    human_review_required: true
    applicability:
      data_service: required
      scheduled_pipeline: required
      ml_inference: required
      integrated_capstone: required
    evidence:
      - image_digest
      - base_image_policy
      - image_scan
      - runtime_security_context
      - privileged_fixture_test
    verification: "Inspect exact image and workload security settings; review scan/triage and denied fixture."
    negative_test: "NT-05 privileged workload is denied or flagged."
    levels:
      L1: "Image/runtime settings are unreviewed."
      L2: "Some hardening is configured but scan or negative-test evidence is incomplete."
      L3: "Exact image is scanned and runtime restrictions are tested."
      L4: "Reviewer-selected variants verify enforcement and exception handling."
  - id: SR-04
    name: "Dependency control and SBOM binding"
    weight: 10
    critical_gate: false
    non_waivable: false
    human_review_required: true
    applicability:
      data_service: required
      scheduled_pipeline: required
      ml_inference: required
      integrated_capstone: required
    evidence:
      - dependency_lockfiles
      - dependency_hashes
      - sbom
      - sbom_subject_digest
      - sbom_mismatch_test
    verification: "Review lockfiles/hashes and compare SBOM subject to the built artifact digest."
    negative_test: "NT-08 SBOM subject mismatch is rejected."
    levels:
      L1: "Dependencies are not traceable."
      L2: "Lockfile or SBOM exists but binding is incomplete."
      L3: "SBOM subject matches the exact promoted artifact and mismatch test fails."
      L4: "Reviewer independently spot-checks generation, identity and coverage limits."
  - id: SR-05
    name: "Artifact integrity and provenance"
    weight: 14
    critical_gate: true
    non_waivable: true
    human_review_required: true
    applicability:
      data_service: required
      scheduled_pipeline: required
      ml_inference: required
      integrated_capstone: required
    evidence:
      - registry_digest
      - gitops_digest
      - runtime_digest
      - promotion_record
      - signature_verification_if_selected
    verification: "Three-way exact digest comparison; verify expected signer identity if Cap+Security selects signing."
    negative_test: "NT-02 tag-only, NT-03 signature/trust mismatch, NT-09 digest mismatch."
    levels:
      L1: "Release identity is missing or mutable-tag based."
      L2: "Registry digest exists but promotion/runtime comparison is incomplete."
      L3: "Registry, GitOps and runtime digest match; optional trust policy is correctly verified."
      L4: "Independent verifier catches missing, malformed, tag-only and mismatched values."
  - id: SR-06
    name: "Pipeline and source-control security"
    weight: 12
    critical_gate: true
    non_waivable: true
    human_review_required: true
    applicability:
      data_service: required
      scheduled_pipeline: required
      ml_inference: required
      integrated_capstone: required
    evidence:
      - required_checks
      - workflow_permissions
      - action_pin_inventory
      - branch_protection
      - pull_request_secret_isolation
    verification: "Review workflow conditions, permissions, immutable action pins and protected release path."
    negative_test: "NT-07 broad permissions, NT-11 unpinned action and NT-12 untrusted PR secret exposure are flagged."
    levels:
      L1: "Checks are optional/skippable or permissions are unknown."
      L2: "Some controls exist but branch/PR/action-pin evidence is incomplete."
      L3: "Required checks gate promotion; permissions and PR secret boundaries are evidenced."
      L4: "Reviewer-planted workflow defects are detected and change control is repeatable."
  - id: SR-07
    name: "Vulnerability triage and accepted risk"
    weight: 10
    critical_gate: false
    non_waivable: false
    human_review_required: true
    applicability:
      data_service: required
      scheduled_pipeline: required
      ml_inference: required
      integrated_capstone: required
    evidence:
      - scanner_findings
      - finding_triage
      - risk_acceptance
      - expiry_validation
    verification: "Review finding scope, affected digest, reachability, owner, approver, compensating control and expiry."
    negative_test: "NT-10 ignored/expired finding fails the declared gate."
    levels:
      L1: "Findings are treated as a badge with no disposition."
      L2: "Findings are listed but context/owner/expiry is incomplete."
      L3: "Findings are tied to digest and accepted risk is time-bounded."
      L4: "Reviewer challenges suppressions, expiry and reachability claims."
  - id: SR-08
    name: "Runtime, network and admission controls"
    weight: 10
    critical_gate: true
    non_waivable: true
    human_review_required: true
    applicability:
      data_service: required
      scheduled_pipeline: required
      ml_inference: required
      integrated_capstone: required
    evidence:
      - pod_security_settings
      - network_policy
      - cni_enforcement_note
      - admission_policy_if_selected
      - allowed_denied_fixtures
    verification: "Inspect PSS/security context and test allowed/denied network/admission behavior where supported."
    negative_test: "NT-05 privileged fixture and NT-15 unauthorized network path are denied where declared enforced."
    levels:
      L1: "Policy intent/configuration exists without enforcement evidence."
      L2: "Some restrictions exist but CNI/mode/negative test is incomplete."
      L3: "Applicable restrictions are enforced and safe negative tests are evidenced."
      L4: "Reviewer-selected fixtures verify scope, exceptions and failure behavior."
  - id: SR-09
    name: "Release process, approval and rollback"
    weight: 10
    critical_gate: true
    non_waivable: true
    human_review_required: true
    applicability:
      data_service: required
      scheduled_pipeline: required
      ml_inference: required
      integrated_capstone: required
    evidence:
      - release_record
      - promotion_approval
      - post_deploy_verification
      - rollback_execution
      - rollback_runtime_digest
    verification: "Trace approval/source/build/digest/GitOps and verify a Git-controlled rollback."
    negative_test: "NT-13 missing approval and NT-14 missing/failed rollback evidence block."
    levels:
      L1: "No traceable approval/promotion or rollback evidence."
      L2: "Release record exists but execution/verification is incomplete."
      L3: "Approval, promotion, health check and rollback are evidenced."
      L4: "Reviewer independently replays identity and rollback evidence."
```

#### 4.10.2 Submission format

This is an illustrative learner submission. Evidence paths are examples
and must be replaced with actual repository-local files or approved
retained references.

``` json
{
  "schema_version": "1",
  "profile": "integrated_capstone",
  "scope": "synthetic local kind lab",
  "commit_sha": "REPLACE_WITH_ACTUAL_COMMIT_SHA",
  "artifact_digest": "sha256:REPLACE_WITH_ACTUAL_64_HEX_DIGEST",
  "items": [
    {
      "id": "SR-01",
      "status": "PASS",
      "rating": 2,
      "evidence_refs": ["E-SR01-SCAN", "E-SR01-CANARY"],
      "attestation": {
        "reviewer": "REPLACE_WITH_REVIEWER",
        "role": "REPLACE_WITH_REVIEWER_ROLE",
        "timestamp_utc": "REPLACE_WITH_ACTUAL_TIMESTAMP",
        "decision": "PASS",
        "rationale": "Reviewed the actual scan and canary evidence."
      },
      "na_reason": null,
      "waiver": null
    }
  ],
  "evidence": [
    {
      "evidence_id": "E-SR01-SCAN",
      "requirement_id": "REQ-008",
      "path": "evidence/security/secret-scan.txt",
      "evidence_type": "automated_test",
      "timestamp_utc": "REPLACE_WITH_ACTUAL_TIMESTAMP",
      "source_commit": "REPLACE_WITH_ACTUAL_COMMIT_SHA",
      "artifact_digest": "sha256:REPLACE_WITH_ACTUAL_64_HEX_DIGEST",
      "checksum": "sha256:REPLACE_WITH_ACTUAL_FILE_CHECKSUM",
      "verification_method": "scanner run tied to release workflow",
      "result": "PASS",
      "owner": "REPLACE_WITH_OWNER"
    }
  ],
  "attestations": [],
  "risk_acceptances": []
}
```

#### 4.10.3 Scoring script

**Dependency:** PyYAML is an external dependency; Python's standard
library does not parse YAML. Install and pin a reviewed version in the
learner's environment, then verify the installed version before running.
The exact supported version is `[VERIFY]`; do not assume an unverified
version.

``` python
# File: security/score_rubric.py
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import yaml  # External dependency: PyYAML; verify and pin locally.

STATUSES = {"PASS", "FAIL", "NOT_DEMONSTRATED", "NOT_APPLICABLE", "WAIVED"}
PROFILES = {"data_service", "scheduled_pipeline", "ml_inference", "integrated_capstone"}
SHA_RE = re.compile(r"^[0-9a-fA-F]{40,64}$")

def parse_time(value):
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            return None
        return dt.astimezone(timezone.utc)
    except ValueError:
        return None

def points(weight, rating):
    value = Decimal(str(weight)) * Decimal(str(rating)) / Decimal("3")
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def load_yaml(path):
    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)

def evaluate(rubric, submission, root):
    errors, blockers, findings = [], [], []
    criteria = rubric.get("criteria") if isinstance(rubric, dict) else None
    items = submission.get("items") if isinstance(submission, dict) else None
    if not isinstance(criteria, list) or not isinstance(items, list):
        return {"result": "INCOMPLETE", "errors": ["rubric.criteria and submission.items must be lists"]}

    if submission.get("profile") not in PROFILES:
        errors.append("unsupported or missing submission profile")

    by_criterion = {}
    weight_total = 0
    for row in criteria:
        if not isinstance(row, dict) or not row.get("id"):
            errors.append("invalid criterion record")
            continue
        cid = row["id"]
        if cid in by_criterion:
            errors.append(f"duplicate rubric criterion: {cid}")
        by_criterion[cid] = row
        weight = row.get("weight")
        if isinstance(weight, bool) or not isinstance(weight, int) or weight <= 0:
            errors.append(f"{cid}: weight must be a positive integer")
        else:
            weight_total += weight
    if weight_total != 100:
        errors.append(f"rubric weights total {weight_total}, expected 100")

    evidence_rows = submission.get("evidence", [])
    if not isinstance(evidence_rows, list):
        errors.append("evidence must be a list")
        evidence_rows = []
    evidence_by_id = {}
    for ev in evidence_rows:
        if not isinstance(ev, dict) or not ev.get("evidence_id"):
            errors.append("invalid evidence record")
            continue
        eid = ev["evidence_id"]
        if eid in evidence_by_id:
            errors.append(f"duplicate evidence ID: {eid}")
        evidence_by_id[eid] = ev

    submission_by_id = {}
    for item in items:
        if not isinstance(item, dict) or not item.get("id"):
            errors.append("invalid submission item")
            continue
        cid = item["id"]
        if cid in submission_by_id:
            errors.append(f"duplicate submission item: {cid}")
        submission_by_id[cid] = item

    for cid in by_criterion.keys() - submission_by_id.keys():
        errors.append(f"{cid}: missing submission item")
    for cid in submission_by_id.keys() - by_criterion.keys():
        errors.append(f"{cid}: unknown criterion")

    total = Decimal("0.00")
    status_counts = {s: 0 for s in STATUSES}
    gate_results = []
    for cid, criterion in by_criterion.items():
        item = submission_by_id.get(cid)
        if item is None:
            continue
        status = item.get("status")
        rating = item.get("rating")
        if status not in STATUSES:
            errors.append(f"{cid}: invalid status {status!r}")
            continue
        status_counts[status] += 1

        if status == "NOT_APPLICABLE":
            reason = item.get("na_reason")
            applicability = criterion.get("applicability", {}).get(submission.get("profile"))
            att = item.get("na_attestation")
            if not isinstance(reason, str) or not reason.strip():
                errors.append(f"{cid}: N-A requires a reason")
            if applicability not in {"conditional", "na_allowed"}:
                errors.append(f"{cid}: N-A is not permitted for selected profile")
            if not isinstance(att, dict) or not att.get("reviewer") or not parse_time(att.get("timestamp_utc")) or not att.get("rationale"):
                errors.append(f"{cid}: N-A requires reviewer attestation")
            if criterion.get("critical_gate") or criterion.get("non_waivable"):
                blockers.append(f"{cid}: critical/non-waivable criterion cannot be N-A")
            continue

        if status == "WAIVED":
            waiver = item.get("waiver")
            valid = (
                isinstance(waiver, dict)
                and all(waiver.get(k) for k in ("owner", "approver", "rationale", "compensating_control"))
                and parse_time(waiver.get("created_at"))
                and parse_time(waiver.get("expires_at"))
            )
            if not valid:
                errors.append(f"{cid}: waiver metadata incomplete")
                blockers.append(f"{cid}: invalid waiver")
            elif parse_time(waiver["expires_at"]) <= datetime.now(timezone.utc):
                blockers.append(f"{cid}: waiver expired")
            if criterion.get("critical_gate") or criterion.get("non_waivable"):
                blockers.append(f"{cid}: critical/non-waivable criterion cannot be waived")
            continue

        refs = item.get("evidence_refs", [])
        if not isinstance(refs, list):
            errors.append(f"{cid}: evidence_refs must be a list")
            refs = []
        resolved = []
        for ref in refs:
            ev = evidence_by_id.get(ref)
            if ev is None:
                errors.append(f"{cid}: unknown evidence reference {ref}")
                continue
            resolved.append(ev)
            raw_path = ev.get("path")
            if raw_path:
                candidate = (root / raw_path).resolve()
                if root.resolve() not in candidate.parents and candidate != root.resolve():
                    errors.append(f"{cid}: evidence path escapes repository: {raw_path}")
                elif not candidate.is_file():
                    errors.append(f"{cid}: evidence file missing: {raw_path}")
                else:
                    checksum = ev.get("checksum")
                    if checksum:
                        import hashlib
                        actual = hashlib.sha256(candidate.read_bytes()).hexdigest()
                        expected = str(checksum).removeprefix("sha256:")
                        if actual.lower() != expected.lower():
                            errors.append(f"{cid}: evidence checksum mismatch: {raw_path}")

        if status == "PASS" and not resolved:
            blockers.append(f"{cid}: PASS without evidence")
        if status in {"FAIL", "NOT_DEMONSTRATED"}:
            rating = 0
        if isinstance(rating, bool) or not isinstance(rating, int) or rating not in {0, 1, 2, 3}:
            errors.append(f"{cid}: rating must be integer 0..3")
            rating = 0
        if status == "PASS" and rating == 0:
            errors.append(f"{cid}: PASS cannot have rating 0")
        if status == "FAIL" and criterion.get("critical_gate"):
            blockers.append(f"{cid}: critical gate failed")
        if criterion.get("critical_gate") and (status != "PASS" or rating < 2):
            blockers.append(f"{cid}: critical gate requires a demonstrated competent rating (2 or 3)")

        if criterion.get("automation") == "manual" or criterion.get("human_review_required"):
            att = item.get("attestation")
            if status == "PASS" and (
                not isinstance(att, dict)
                or not att.get("reviewer")
                or not att.get("role")
                or not parse_time(att.get("timestamp_utc"))
                or not att.get("decision") == "PASS"
                or not att.get("rationale")
            ):
                blockers.append(f"{cid}: manual pass lacks reviewer attestation")

        total += points(criterion["weight"], rating)

    for cid, item in submission_by_id.items():
        if item.get("status") == "PASS" and not item.get("evidence_refs"):
            findings.append(f"{cid}: claimed Pass has no evidence references")

    if errors or blockers:
        result = "BLOCKED"
    elif any(status_counts[s] for s in ("NOT_DEMONSTRATED", "FAIL", "NOT_APPLICABLE", "WAIVED")):
        result = "INCOMPLETE"
    else:
        threshold = Decimal(str(rubric.get("scoring", {}).get("assumed_numeric_threshold", 70)))
        result = "READY_FOR_HUMAN_REVIEW" if total >= threshold else "INCOMPLETE"

    return {
        "result": result,
        "score": str(total),
        "weight_total": weight_total,
        "status_counts": status_counts,
        "blockers": blockers,
        "errors": errors,
        "findings": findings,
        "notice": "This validator checks structure and selected evidence properties. It does not prove evidence truthfulness, control effectiveness, or production readiness."
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rubric", default="security/rubric.yaml")
    parser.add_argument("--submission", default="security/submission.json")
    parser.add_argument("--root", default=".")
    parser.add_argument("--report", default="evidence/security/unit4-score.json")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    try:
        rubric = load_yaml(args.rubric)
        submission = json.loads(Path(args.submission).read_text(encoding="utf-8"))
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"INPUT_ERROR: {exc}", file=sys.stderr)
        return 2

    report = evaluate(rubric, submission, root)
    report["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
    report["profile"] = submission.get("profile")
    report["scope"] = submission.get("scope")
    report["commit_sha"] = submission.get("commit_sha")
    report["artifact_digest"] = submission.get("artifact_digest")
    output = Path(args.report)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Result: {report['result']}; score: {report.get('score', 'unavailable')}/100")
    for row in report.get("blockers", []):
        print(f"BLOCKER: {row}")
    return 0 if report["result"] == "READY_FOR_HUMAN_REVIEW" else 1

if __name__ == "__main__":
    raise SystemExit(main())
```

**Important limitations:** this teaching runner checks a subset of
schema, paths and checksums. It does not parse arbitrary workflow
semantics, validate registry authenticity, prove reviewer identity,
determine exploitability, prove a signature trust policy, or inspect
whether a human attestation is genuine. The runner's
`READY_FOR_HUMAN_REVIEW` is not a `GO` decision. Review its path
handling, symlink/race behavior, timestamps, schema and PyYAML version
before use.

#### 4.10.4 Release-evidence verifier --- registry = GitOps = runtime

This verifier accepts three explicit values. It intentionally does not
guess registry or Argo CD API fields. Extract values through
version-verified adapters and pass the normalized values as arguments. A
digest-only match proves identity consistency, not trust or safety.

``` python
# File: security/verify_release_identity.py
from __future__ import annotations

import argparse
import json
import re
import sys

DIGEST_RE = re.compile(r"^sha256:([0-9a-f]{64})$")

def normalize_digest(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("digest is missing")
    value = value.strip()
    if "@" in value:
        _, value = value.rsplit("@", 1)
    if ":" in value and not value.startswith("sha256:"):
        raise ValueError("tag or ambiguous reference is not an accepted digest")
    match = DIGEST_RE.fullmatch(value)
    if not match:
        raise ValueError("malformed or unsupported digest; expected sha256:<64 lowercase hex>")
    return "sha256:" + match.group(1)

def verify(registry, gitops, running):
    raw = {"registry": registry, "gitops": gitops, "running": running}
    normalized = {}
    errors = []
    for key, value in raw.items():
        try:
            normalized[key] = normalize_digest(value)
        except ValueError as exc:
            errors.append(f"{key}: {exc}")
    if errors:
        return {"result": "BLOCKED", "values": raw, "normalized": normalized, "errors": errors}
    distinct = set(normalized.values())
    if len(distinct) != 1:
        mismatches = []
        pairs = (("registry", "gitops"), ("registry", "running"), ("gitops", "running"))
        for left, right in pairs:
            if normalized[left] != normalized[right]:
                mismatches.append(f"{left} != {right}")
        return {"result": "BLOCKED", "values": raw, "normalized": normalized, "errors": mismatches}
    return {
        "result": "MATCH",
        "values": raw,
        "normalized": normalized,
        "errors": [],
        "notice": "Digest equality proves content identity consistency only; it does not prove trust, safety, signature validity or vulnerability status."
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--gitops", required=True)
    parser.add_argument("--running", required=True)
    parser.add_argument("--commit", default=None)
    parser.add_argument("--deployment", default=None)
    args = parser.parse_args()
    result = verify(args.registry, args.gitops, args.running)
    result["commit"] = args.commit
    result["deployment"] = args.deployment
    print(json.dumps(result, indent=2))
    return 0 if result["result"] == "MATCH" else 1

if __name__ == "__main__":
    raise SystemExit(main())
```

Example invocation (synthetic values only):

``` bash
python security/verify_release_identity.py \
  --registry 'sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' \
  --gitops 'registry.local/m17/inference@sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' \
  --running 'sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' \
  --commit 'REPLACE_WITH_COMMIT_SHA' \
  --deployment 'kind-m17-lab/m17-app/inference'
```

**Representative example --- your output will differ.** A successful
result contains `MATCH` and three normalized identical digest values.
Interpretation: the three supplied identity values agree. It does not
prove the image is trusted, signed, scanned, non-malicious or
production-safe. A tag-only, missing, malformed or unequal value returns
`BLOCKED`.

#### 4.10.5 Release verifier tests

``` python
# File: security/test_verify_release_identity.py
import unittest
from verify_release_identity import verify

GOOD = "sha256:" + ("a" * 64)
OTHER = "sha256:" + ("b" * 64)

class VerifyReleaseIdentityTests(unittest.TestCase):
    def test_matching_values_pass(self):
        self.assertEqual(verify(GOOD, GOOD, GOOD)["result"], "MATCH")

    def test_registry_missing_blocks(self):
        self.assertEqual(verify("", GOOD, GOOD)["result"], "BLOCKED")

    def test_tag_only_blocks(self):
        self.assertEqual(verify("registry.local/app:latest", GOOD, GOOD)["result"], "BLOCKED")

    def test_malformed_digest_blocks(self):
        self.assertEqual(verify("sha256:abc", GOOD, GOOD)["result"], "BLOCKED")

    def test_registry_gitops_mismatch_blocks(self):
        self.assertEqual(verify(GOOD, OTHER, GOOD)["result"], "BLOCKED")

    def test_registry_runtime_mismatch_blocks(self):
        self.assertEqual(verify(GOOD, GOOD, OTHER)["result"], "BLOCKED")

    def test_gitops_runtime_mismatch_blocks(self):
        self.assertEqual(verify(GOOD, OTHER, OTHER.replace("b", "c"))["result"], "BLOCKED")

if __name__ == "__main__":
    unittest.main()
```

These are test definitions, not execution results. The learner must run
them in the implementation repository and retain the actual test output.

#### 4.10.6 RBAC audit --- read-only and lab-scoped

The script below checks a small declared permission set using
`kubectl auth can-i`. It does not create roles or exercise a real
privileged action. Confirm the selected service-account name and
namespace before running. Every Kubernetes command explicitly selects
`kind-m17-lab`.

``` bash
#!/usr/bin/env bash
# File: security/audit-rbac.sh
set -euo pipefail

CONTEXT="kind-m17-lab"
NAMESPACE="m17-app"
SERVICE_ACCOUNT="inference"

kubectl --context kind-m17-lab cluster-info >/dev/null
kubectl --context kind-m17-lab get namespace "${NAMESPACE}" >/dev/null

AS_ID="system:serviceaccount:${NAMESPACE}:${SERVICE_ACCOUNT}"

check() {
  local verb="$1"
  local resource="$2"
  local expected="$3"
  local actual
  actual="$(kubectl auth can-i "${verb}" "${resource}" \
    --as="${AS_ID}" --namespace="${NAMESPACE}" --context kind-m17-lab)"
  printf '%s %s expected=%s actual=%s\n' "${verb}" "${resource}" "${expected}" "${actual}"
  test "${actual}" = "${expected}"
}

# Example least-privilege contract; adapt to the actual workload.
check get configmaps yes
check list pods no
check get secrets no
check create pods/exec no
```

The expected values are a teaching contract, not a claim about the
learner's current cluster. `kubectl auth can-i` checks authorization for
the selected identity and request; it does not prove the workload
actually uses that identity, validate every admission/network control,
or test runtime behavior. Impersonation may require operator
permissions; if unavailable, record the limitation and use a safe policy
fixture rather than granting broad privileges.

**Representative example --- your output will differ.** The script
prints each requested verb/resource and expected/actual authorization
result. A successful check means only that the API authorization query
returned the expected answer for that identity/context; it does not
prove the workload's full effective security posture.

#### 4.10.7 Secret-scan configuration and synthetic canary

Use a real scanner and verify its current configuration/CLI syntax. The
following Gitleaks-style TOML rule is an illustrative custom detector;
confirm the supported schema and command for the installed version
before running (`[VERSION-SENSITIVE]`).

``` toml
# File: security/gitleaks.toml
title = "M17 synthetic secret canary test"

[[rules]]
id = "m17-synthetic-canary"
description = "Synthetic marker used only to verify scanner wiring"
regex = '''M17_TEST_SECRET_DO_NOT_USE_[A-Z0-9]{16}'''
keywords = ["M17_TEST_SECRET_DO_NOT_USE_"]
```

Create the fixture only in a temporary directory and never use a real
token:

``` bash
tmpdir="$(mktemp -d)"
trap 'rm -rf "${tmpdir}"' EXIT
printf '%s\n' 'M17_TEST_SECRET_DO_NOT_USE_0123456789ABCDEF' > "${tmpdir}/canary.txt"

# [VERIFY] Confirm the installed Gitleaks version and exact `dir` command flags.
gitleaks version
gitleaks dir --config security/gitleaks.toml --redact "${tmpdir}"
```

Expected behavior: the scanner detects the synthetic marker and returns
its documented finding/exit behavior. The learner's test harness must
assert that the scan is not interpreted as clean. Do not paste raw
secret-like output into committed evidence; record only redacted finding
metadata and exit status. Remove the temporary directory and verify it
is gone. A scanner may miss formats it does not recognize and may
produce false positives; a clean scan is not proof that no secrets
exist.

#### 4.10.8 SBOM and dependency control

A representative Syft-style command is shown only as a version-sensitive
example. Confirm the installed tool version and output syntax. Generate
the SBOM from the exact immutable image reference:

``` bash
# [VERIFY] Confirm Syft syntax/version and supported output format.
syft version
syft 'registry.local/m17/inference@sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' \
  -o cyclonedx-json=security/sbom-inference.cdx.json
```

Record the generated SBOM file checksum, subject image digest, source
commit, build/run ID, generator version and timestamp. If the generator
does not encode the subject digest in the format used, maintain an
explicit sidecar record linking the SBOM checksum to the artifact digest
and build identity. The release verifier must reject a sidecar whose
subject differs from the deployed artifact. Lockfiles/hashes are
ecosystem-dependent; mark unsupported ecosystems and document the
verification method rather than inventing a universal command.

#### 4.10.9 Representative protected CI workflow

This workflow illustrates the control boundary; it is not a complete
provider-independent pipeline. Replace the action placeholders with
reviewed full commit SHAs, verify syntax against current GitHub Actions
documentation, and test the event/permission behavior in a disposable
repository. The placeholders are intentionally not runnable.

``` yaml
# File: .github/workflows/security-release.yml
name: security-release

on:
  pull_request:
  push:
    branches: ["main"]

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@REPLACE_WITH_REVIEWED_FULL_COMMIT_SHA
      - name: Unit tests
        run: python -m unittest discover -s tests -v
      - name: Secret scan
        run: |
          echo "Replace with verified scanner install and invocation"
          exit 1

  publish:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    needs: [validate]
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@REPLACE_WITH_REVIEWED_FULL_COMMIT_SHA
      - name: Build and publish
        run: |
          echo "Use a reviewed builder and capture the immutable registry digest"
          exit 1
```

The deliberate `exit 1` placeholders prevent accidental execution before
the learner supplies verified tooling. The example demonstrates that
pull-request validation has read-only permissions and that publication
is a separate protected push job. A production workflow also needs a
verified builder, registry authentication, digest capture, required
branch checks, provenance policy and release record. Do not pass
protected secrets to untrusted pull-request code.

### 4.11 Negative-test suite and hands-on labs

#### Negative-test catalogue

These are test designs, not test results. Each must be run only with
synthetic fixtures or the learner's own isolated lab.

  ----------------------------------------------------------------------------------------------
  ID      Setup/fixture         Expected result           Evidence artifact   Why it matters
  ------- --------------------- ------------------------- ------------------- ------------------
  NT-01   Place the synthetic   Scanner detects it; gate  Redacted finding,   Proves
          canary in a temporary blocks                    exit status, run    scanner/gate
          test directory                                  identity            wiring

  NT-02   Replace immutable     Verifier rejects/flags    Verifier JSON       Prevents mutable
          reference with        tag-only identity                             promotion identity
          `:latest`                                                           

  NT-03   Cap+Security: use an  Required signature policy Trust-policy        Distinguishes
          unsigned artifact or  rejects/flags; Cap-Core   verification record profile
          wrong expected signer records signature as not                      requirement from
          fixture               selected                                      optional tool

  NT-04   Configure a           Verification fails        Policy fixture and  Cryptographic
          cryptographically     expected-identity check   verifier result     validity is not
          valid signature under                                               authorization
          an unexpected                                                       
          identity in a                                                       
          synthetic policy                                                    
          fixture                                                             

  NT-05   Submit a privileged   Admission policy/PSS      Denial/flag record  Proves runtime
          workload fixture      flags or denies it under  and policy mode     control is active
                                declared enforcement                          

  NT-06   Query an unnecessary  Authorization query       RBAC audit output   Proves
          workload permission   returns `no`                                  least-privilege
                                                                              boundary

  NT-07   Give a test-only CI   Conformance               Workflow review and Limits CI blast
          job broad write       check/reviewer flags the  test result         radius
          permissions           excess                                        

  NT-08   Make SBOM subject     SBOM binding check        Subject comparison  Prevents unrelated
          digest differ from    blocks/flags              report              inventory being
          artifact digest                                                     presented as
                                                                              evidence

  NT-09   Make registry, GitOps Three-way verifier        Verifier JSON with  Detects release
          and running digest    returns `BLOCKED`         mismatch reason     identity drift
          differ pairwise                                                     

  NT-10   Leave a synthetic     Gate fails/flags expired  Finding register    Prevents
          finding ignored or    risk                      and expiry test     silent/unbounded
          let accepted-risk                                                   vulnerability
          expiry pass                                                         acceptance

  NT-11   Replace a reviewed    Workflow policy flags the Action pin          Protects workflow
          immutable action SHA  action                    inventory and       supply chain
          with a mutable tag                              conformance result  

  NT-12   Use an untrusted      Test proves protected     Workflow            Prevents secret
          pull-request event in secrets are not available event/permissions   exposure to
          a secret-bearing job                            review              untrusted code
          fixture                                                             

  NT-13   Remove required       Release gate blocks/flags Release record      Makes promotion
          release               missing approval          validation          auditable
          approval/change                                                     
          record                                                              

  NT-14   Remove rollback       Release remains           Rollback record and Runbook-only
          execution evidence or blocked/incomplete        digest verification rollback is not
          use a wrong rollback                                                proof
          digest                                                              

  NT-15   Where CNI/policy      Connection is denied;     Before/after        Demonstrates
          support is verified,  allowed path still        connectivity test   segmentation
          attempt an undeclared succeeds                                      enforcement
          benign connectivity                                                 
          path                                                                

  NT-16   Skip or mark a        Required-check/pipeline   Workflow run and    Prevents green
          required test         conformance fails         planted-defect      status from hiding
          `continue-on-error`                             report              skipped controls
          and attempt promotion                                               
  ----------------------------------------------------------------------------------------------

**Positive cases:** a known digest match; a known allowed RBAC request;
an allowed workload fixture; a valid SBOM subject match; a required test
that runs and passes; a valid approval record. A negative suite without
positive cases can create a policy that rejects everything.

#### LAB-SR-01 --- Trace a release by immutable identity

-   **Goal:** Trace a synthetic source SHA through CI, registry, GitOps
    and running workload.
-   **Prerequisites:** Cap-Core, separate source/GitOps identities,
    read-only access to local registry and `kind` lab.
-   **Steps:**
    1.  Record the selected profile, source repository and GitOps
        repository.
    2.  Build a toy service using the learner's existing M01/M02
        pipeline.
    3.  Capture source SHA, CI run/build identity and registry digest.
    4.  Update the GitOps manifest to the exact digest through a
        reviewed commit.
    5.  Inspect Argo CD source revision and workload image reference.
    6.  Extract the running image identity using a version-verified
        adapter; every Kubernetes command must use
        `--context kind-m17-lab`.
    7.  Run the three-way verifier and retain the report.
-   **Expected evidence:** source SHA, run ID, registry digest, GitOps
    commit/digest, runtime digest, verifier JSON and timestamps.
-   **Cleanup:** revert the test GitOps commit or leave the declared
    stable revision; remove only learner-created disposable resources
    using the guarded teardown process.
-   **Stretch:** repeat for the toy ML model hash and prove code/model
    pairing.
-   **Common failure modes:** tag-only image; rebuilding for the second
    environment; stale runtime output; confusing GitOps commit with
    source commit; adapter extracts a tag rather than a digest.
-   **Acceptance:** all three digest identities match; no claim is made
    that the digest proves trust.

#### LAB-SR-02 --- Secret hygiene and least privilege

-   **Goal:** Prove a synthetic secret canary is detected and
    unnecessary permissions are denied.
-   **Prerequisites:** scanner configured with synthetic custom rule;
    disposable temp directory; dedicated test service account.
-   **Steps:**
    1.  Run a baseline scan on the relevant source scope.
    2.  Create the synthetic canary fixture in a temporary directory.
    3.  Run the scanner; assert that the finding causes a non-clean
        result.
    4.  Remove the fixture and verify cleanup; do not commit the canary.
    5.  Review workflow permissions and workload service-account
        bindings.
    6.  Run the read-only RBAC audit script. Confirm every command uses
        `--context kind-m17-lab`.
    7.  Record an exposure-response procedure for a hypothetical real
        credential without creating one.
-   **Expected evidence:** baseline scan, canary negative-test result,
    redacted scanner metadata, workflow permission review, RBAC report
    and response runbook.
-   **Cleanup:** remove temp files, verify no canary remains, delete
    only lab-created test bindings if any.
-   **Stretch:** reviewer chooses a second synthetic pattern and checks
    suppression handling.
-   **Common failure modes:** scanner command not actually run; canary
    regex not configured; output leaks the fixture; broad allowlist;
    audit checks the wrong service account.
-   **Acceptance:** canary is detected and blocked; expected
    unauthorized action returns `no`; no secret value is committed.

#### LAB-SR-03 --- Supply-chain evidence and vulnerability triage

-   **Goal:** Generate an SBOM for the exact built artifact and make a
    defensible synthetic finding decision.
-   **Prerequisites:** local image registry, exact artifact digest,
    lockfiles where supported, SBOM tool installed and version recorded.
-   **Steps:**
    1.  Build once and capture the immutable digest.
    2.  Generate an SBOM from that digest using a verified tool command.
    3.  Record SBOM checksum, subject digest, generator version, source
        SHA and CI run.
    4.  Review scanner findings from the learner's own scan or a clearly
        labelled synthetic finding record.
    5.  Record severity, reachability/exploitability reasoning, affected
        digest, owner, compensating control, approver and expiry.
    6.  Change the subject digest in a disposable test fixture and
        verify the mismatch is rejected.
-   **Expected evidence:** SBOM, checksum, subject binding, finding
    register, expiry test and mismatch result.
-   **Cleanup:** remove only disposable fixtures; retain redacted
    evidence according to the learner's retention policy.
-   **Stretch:** regenerate the SBOM after a dependency update and
    compare the resulting component inventory.
-   **Common failure modes:** SBOM generated from source instead of
    image; subject digest missing; invented CVE; finding disposition has
    no owner/expiry.
-   **Acceptance:** SBOM subject matches the built artifact; mismatch
    fixture fails; no invented vulnerability data is presented as real.

#### LAB-SR-04 --- Negative release tests and gate review

-   **Goal:** Exercise at least five negative tests and show that the
    release path fails safely.
-   **Prerequisites:** isolated lab; verified context guard;
    policy/scan/verifier fixtures; rollback plan.
-   **Steps:**
    1.  Confirm context and namespace ownership before any cluster
        operation.
    2.  Run the tag-only digest test.
    3.  Run the synthetic canary test.
    4.  Run the SBOM subject mismatch test.
    5.  Run the RBAC denied-action query.
    6.  If Cap+Security is selected, run the wrong-signer identity
        fixture and privileged admission fixture.
    7.  Record which tests are automated and which require reviewer
        judgment.
-   **Expected evidence:** at least five test records with setup,
    expected result, actual result, timestamp and cleanup.
-   **Cleanup:** restore baseline policy/configuration and remove
    disposable fixtures; confirm no unintended workload remains.
-   **Stretch:** add an untrusted-PR secret-isolation test in a
    disposable repository.
-   **Common failure modes:** running against the wrong context; tests
    that only print warnings but return success; negative fixture not
    reaching the gate; no positive test.
-   **Acceptance:** unsafe cases are blocked or explicitly flagged under
    the selected profile; no live attack is performed.

#### LAB-SR-05 --- Expert release review and supply-chain incident tabletop

-   **Goal:** Review a synthetic flawed release, issue go/no-go, then
    complete a defensive incident tabletop.
-   **Prerequisites:** completed evidence package from Labs 1--4;
    synthetic flawed-submission table; reviewer scoring sheet.
-   **Steps:**
    1.  Review the synthetic submission without reading the answer key.
    2.  Score all nine criteria independently and list blockers.
    3.  Compare with a second reviewer or facilitator anchor; resolve
        differences by evidence.
    4.  Decide `GO`, `GO_WITH_CONDITIONS` or `NO_GO` for the lab
        exercise.
    5.  Run the supply-chain incident tabletop: stop promotion,
        establish scope, preserve redacted evidence, revoke/rotate a
        hypothetical synthetic credential, rebuild from trusted source,
        re-run checks, verify digest and communicate.
    6.  Record residual risks, owners, due dates and follow-up review.
-   **Expected evidence:** independent score sheets, discrepancy
    resolution, decision record, timeline,
    containment/rebuild/verification plan and postmortem actions.
-   **Cleanup:** no production resource is touched; close tabletop
    artifacts and ensure no synthetic canary remains in committed files.
-   **Stretch:** conduct a blinded review with one defect omitted from
    the initial summary; reviewer must discover it from evidence.
-   **Common failure modes:** reviewer accepts narrative, averages away
    a blocker, mistakes a valid signature for trusted identity, or
    treats tabletop actions as executed operations.
-   **Acceptance:** decision is defensible, blockers remain visible, and
    tabletop status is not misrepresented as live execution.

### 4.12 Evidence artifacts

#### Unit 4 evidence package

  -----------------------------------------------------------------------
  Artifact               Minimum content               Commit or retain?
  ---------------------- ----------------------------- ------------------
  Rubric                 YAML schema version,          Commit
  definition/version     criterion IDs, weights and    
                         policy                        

  Threat                 Assets, actors, boundaries,   Commit after
  model/trust-boundary   control ownership             review
  diagram                                              

  Source/build identity  Source SHA, workflow/run ID,  Commit
                         builder identity              non-sensitive
                                                       metadata

  Required-check         Workflow revision, required   Commit redacted
  evidence               jobs, test/scan result and    summary; retain
                         exit status                   provider record
                                                       reference

  Secret-scan evidence   Scanner/version/scope/time,   Commit redacted
                         redacted finding summary,     output only
                         canary result                 

  RBAC audit             Service account, namespace,   Commit redacted
                         permission matrix,            report
                         denied-action result          

  Image/runtime evidence Image digest, base-image      Commit
                         policy, non-root/security     
                         settings, scan context        

  Dependency/SBOM        SBOM, checksum, subject       Commit or safely
  evidence               digest, generator version     retain large SBOM
                                                       with stable
                                                       reference

  Vulnerability triage   Finding IDs from actual scan  Commit
                         or synthetic labels,          
                         reachability, owner, expiry   

  Signature/provenance   Expected identity,            Commit redacted
  evidence               issuer/trust policy, subject  metadata
                         digest and verification       
                         record if enabled             

  Digest verification    Registry/GitOps/runtime       Commit
                         values, commit/deployment     
                         context and result            

  Release/change record  Reviewer, approval, source    Commit
                         SHA, run, digest, GitOps      
                         revision, notes               

  Rollback evidence      Prior/target SHA, digest,     Commit redacted
                         Argo revision, runtime        evidence
                         verification                  

  Negative-test evidence Test ID, fixture description, Commit
                         expected/actual result, exit  
                         status                        

  Reviewer record        Scores, blockers, residual    Commit
                         risks, decision, owners and   
                         dates                         

  Not-demonstrated       Gaps, reason, next action,    Commit
  register               owner and due date            
  -----------------------------------------------------------------------

#### Evidence-index alignment

Unit 1 defines `evidence/index.yaml` with root keys `schema_version` and
`evidence`. Each record uses singular `requirement_id`, not
`requirement_ids`, and includes fields such as `evidence_id`, `path` or
retained reference, `evidence_type`, `timestamp_utc`, source
commit/run/digest, checksum where appropriate, `verification_method`,
`result` and `owner`.

**\[ALIGN WITH `capstone-requirements.md`\]** A Unit 4 traceability row
may reference more than one Unit 1 requirement, but the Unit 1 evidence
record remains one `requirement_id` per record. Create separate
records/rows when one artifact supports multiple requirements. Do not
change Unit 1's schema.

Suggested learner-side evidence paths (not new learning-roadmap files):

``` text
evidence/
└── security/
    ├── threat-model.md
    ├── rubric-submission.json
    ├── score-report.json
    ├── secret-scan/
    ├── rbac/
    ├── image-runtime/
    ├── sbom/
    ├── artifact-identity/
    ├── release/
    ├── negative-tests/
    ├── incident-tabletop/
    └── reviewer-signoff.md
```

**Commit:** non-sensitive, redacted text records, rubric definitions,
policy fixtures, checksums and reproducible test summaries.

**Safely retain:** large scan/SBOM artifacts, CI-provider run records,
registry metadata exports or evidence that must remain in a restricted
system. Use a stable locator, access owner, retention period and
checksum where supported.

**Never commit:** secrets, tokens, private keys, credential-bearing
kubeconfigs, production/customer data, account IDs, unredacted logs, or
sensitive environment dumps. Redact before evidence capture where
possible. A checksum proves byte identity, not truthfulness.

#### Traceability matrix

  -------------------------------------------------------------------------
  Unit 4 criterion    Unit 1 REQ    Unit 1 AC IDs Control/test/evidence
                      IDs                         relationship
  ------------------- ------------- ------------- -------------------------
  SR-01 Secrets       REQ-007,      AC-004        Secret scan + synthetic
                      REQ-008                     canary + redacted
                                                  evidence

  SR-02 Identity      REQ-006,      AC-003,       CI/workload identity +
                      REQ-007       AC-004        RBAC + denied action

  SR-03 Runtime       REQ-009       AC-003        Non-root/security
                                                  context + prohibited
                                                  fixture

  SR-04               REQ-001,      AC-001,       Build identity + SBOM
  SBOM/dependencies   REQ-002,      AC-010        subject digest
                      REQ-030                     

  SR-05 Artifact      REQ-002,      AC-001,       Registry/GitOps/runtime
  integrity           REQ-030       AC-010        digest verifier

  SR-06 Pipeline      REQ-001,      AC-001,       Required checks +
  security            REQ-003,      AC-004        permissions + PR boundary
                      REQ-007                     

  SR-07 Vulnerability REQ-003,      AC-001        Finding triage and
  triage              REQ-032                     time-bounded acceptance

  SR-08               REQ-009,      AC-003        Runtime restriction and
  Runtime/network     REQ-010                     network/admission tests

  SR-09               REQ-001,      AC-001,       Approval, digest
  Release/rollback    REQ-002,      AC-007,       promotion, rollback
                      REQ-003,      AC-010        verification
                      REQ-016,                    
                      REQ-030                     
  -------------------------------------------------------------------------

These are supporting links to Unit 1 requirements, not new requirements.
Unit 3 owns incident/recovery scoring; Unit 5 owns cost/reliability
scoring; Unit 6 owns platform/delivery scoring. Unit 4 owns the
security/release criteria above.

### 4.13 Common review-board questions

**1. How do you prove the artifact tested is the artifact deployed?**

I require a trace from source commit to CI run/build identity, registry
digest, GitOps commit and running workload identity. The
release-evidence verifier compares the normalized registry,
desired-state and runtime digests and fails on missing, malformed,
tag-only or mismatched values. The evidence must include timestamps and
the relevant repository/run/deployment context. This proves identity
consistency for the declared lab scope. It does not prove the artifact
is benign, signed by a trusted builder, or free of vulnerabilities.

**2. What does a valid signature prove, and what does it not prove?**

A valid signature proves that the signed subject is cryptographically
bound to a signing identity under the verification mechanism used. It
does not prove that the signer is authorized for this
repository/workflow, that the build inputs are safe, that the artifact
is vulnerability-free, or that the SBOM matches. I verify the expected
signer identity, issuer/trust root, subject digest and provenance
policy. In Cap-Core, if signing is not selected, I use digest equality
and clearly state that this is a weaker identity-consistency control,
not provenance verification.

**3. How do you decide whether a scanner finding blocks release or can
be accepted temporarily?**

I review the affected component and artifact digest, scanner
scope/database context, severity, exploitability, reachability,
exposure, available fix, compatibility risk and compensating controls. A
temporary acceptance needs an owner, approver, scope, rationale,
creation date, expiry, review trigger and evidence. Expired or ownerless
acceptance is not valid. Critical gates and mandatory requirements
cannot be waived by a numeric score. I never invent CVE data; I use
findings from the learner's scan or labelled synthetic examples.

**4. What evidence proves least privilege and runtime controls are
enforced rather than merely documented?**

I inspect effective CI permissions, service accounts, Role/RoleBinding
rules, workload security context, admission/network policy mode and
scope. Then I run safe negative tests: query an unnecessary
authorization, submit a prohibited fixture to the selected admission
layer, and test an undeclared network path where the CNI supports
enforcement. A policy file or role name alone is not proof. The evidence
must identify the namespace, identity, policy revision, timestamp and
expected/actual result.

**5. What does this local capstone prove, and what must be validated
separately before real production use?**

It proves that the learner can build a bounded, repeatable release path,
maintain artifact identity, apply and test selected security controls,
preserve evidence and defend a review decision in the declared local
lab. It does not prove enterprise IAM, production traffic behavior,
cloud control-plane security, multi-region resilience, regulatory
compliance, real threat resistance or production incident readiness.
Before production, the organization must validate its actual identity
federation, runner/registry trust, policy enforcement, threat model,
data classification, monitoring, recovery, compliance obligations,
operational ownership and change governance.

### 4.14 Sources and verification notes

#### Primary design sources inspected

1.  `PROMPT-Production-DevOps-Integrated-Capstone.md` --- governing M17
    scope, Unit 4 requirements, tool profiles, cost safety, evidence
    standard and fidelity boundary.
2.  `Roadmap_ptree.md` (timestamped supplied equivalent) --- Stage 2E
    and M17 folder structure.
3.  `capstone-requirements.md` --- canonical REQ-001...REQ-032 register,
    AC-001...AC-012 definitions, evidence-index schema and pass rule.
4.  `production-readiness-checklist.md` --- Unit 2 readiness items,
    gates, N-A/waiver/freshness discipline and Unit 1 crosswalk.
5.  `incident-and-recovery-rubric.md` --- Unit 3
    incident/rollback/restore evidence and the conflicting REQ crosswalk
    noted above.
6.  `cost-and-reliability-rubric.md` --- Unit 5 SLO/cost/reliability
    ownership and scoring convention.
7.  `platform-and-delivery-rubric.md` --- Unit 6
    delivery/digest/GitOps/rollback ownership and canonical Unit 1
    crosswalk.
8.  The newly supplied Unit 4 generation prompt
    `Pasted markdown(20261104-074012).md`.

The Unit 2 prompt `Pasted markdown(20261104-072228).md` was also
reviewed as the prior adjacent-unit generation specification. Unit 4
follows its source discipline and M17 contract but does not duplicate
its readiness checklist.

#### Technical verification notes

No live tool execution or external version verification is claimed in
this authoring document. The following require learner verification
against the installed tool baseline:

-   GitHub Actions full immutable action commit SHAs, branch/ruleset
    settings, event permissions and runner behavior.
-   `kubectl`/kind context and namespace names, CNI NetworkPolicy
    enforcement, PSS/admission behavior and API compatibility.
-   Argo CD image/source revision fields and runtime image-digest
    extraction adapter.
-   Registry digest metadata and the normalization used by the local
    registry/runtime.
-   Gitleaks configuration schema and CLI syntax; the synthetic canary
    rule is marked version-sensitive.
-   Syft SBOM output syntax and whether the selected SBOM format records
    the artifact subject in the expected field.
-   PyYAML version, parsing behavior and dependency pin.
-   Cosign identity/issuer verification flags and trust policy, if
    Cap+Security is selected.
-   Exact Helm/Kustomize rendering and policy-engine syntax for the
    selected versions.

Official primary references for learner verification:

-   Kubernetes security contexts:
    https://kubernetes.io/docs/tasks/configure-pod-container/security-context/
-   Kubernetes Pod Security Standards:
    https://kubernetes.io/docs/concepts/security/pod-security-standards/
-   Kubernetes NetworkPolicy:
    https://kubernetes.io/docs/concepts/services-networking/network-policies/
-   Kubernetes RBAC:
    https://kubernetes.io/docs/reference/access-authn-authz/rbac/
-   GitHub Actions workflow permissions:
    https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions
-   GitHub Actions secure use:
    https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions
-   Argo CD documentation: https://argo-cd.readthedocs.io/
-   Sigstore Cosign documentation: https://docs.sigstore.dev/cosign/
-   Gitleaks documentation: https://github.com/gitleaks/gitleaks
-   Syft documentation: https://github.com/anchore/syft

These links are verification starting points, not claims that a specific
version or flag was checked during authoring.

### 4.15 Final self-review and sign-off

#### Self-check questions

**Q1 --- Digest versus tag (L1).** A deployment manifest references
`inference-api:latest`, and the registry currently resolves that tag to
digest A. Is the release identity adequately recorded?

-   **Answer:** No. The tag is mutable and does not pin the content
    selected for deployment. Record the immutable digest and compare
    registry, GitOps and runtime identities.
-   **Why the tempting answer fails:** "The registry resolves it today"
    is a time-dependent observation. A later push can move the tag
    without changing the manifest.

**Q2 --- Scan ran but findings were ignored (L2/L3).** CI shows a
successful scanner job, but a finding is suppressed with no owner or
expiry. Can the criterion pass?

-   **Answer:** No. A scanner execution without triage/gate behavior is
    not effective control evidence. Record the affected digest,
    reachability/exploitability reasoning, disposition, compensating
    control, owner, approver and expiry.
-   **Why the tempting answer fails:** Green status may only mean the
    scanner process completed, not that the risk was resolved or
    accepted.

**Q3 --- Signature identity (L3).** A signature is cryptographically
valid, but the signer identity is not the expected repository/workflow
identity. Is the artifact trusted?

-   **Answer:** No. Verification must enforce the expected
    signer/issuer, subject digest and trust policy.
-   **Why the tempting answer fails:** Cryptographic validity answers
    "was this subject signed by this key/identity?" It does not answer
    "is this identity authorized to release this artifact?"

**Q4 --- SBOM mismatch (L2).** An SBOM exists, but its subject digest
differs from the running image digest. What should the reviewer
conclude?

-   **Answer:** The SBOM does not establish dependency inventory for the
    running artifact. Regenerate or correctly bind it to the exact
    digest.
-   **Why the tempting answer fails:** File existence and plausible
    package names do not prove subject identity.

**Q5 --- Planted secret (L2).** The baseline scan is clean, but a
synthetic canary is not detected. Is secret hygiene demonstrated?

-   **Answer:** No. The negative test shows that the scanner/gate may
    not cover the intended scope or pattern. Fix the configuration and
    rerun.
-   **Why the tempting answer fails:** A clean baseline can mean the
    repository had no detected pattern; it does not prove the scanner
    would detect a known test marker.

**Q6 --- Broad CI token (L3).** A unit-test job has registry write and
deployment permissions "for convenience." What is the correct response?

-   **Answer:** Reduce the permissions and separate
    build/test/publish/deploy identities or jobs. Prove the unnecessary
    action is denied.
-   **Why the tempting answer fails:** Convenience does not justify
    expanding the blast radius of untrusted code or a compromised test
    dependency.

**Q7 --- Documented policy but no enforcement (L3).** A NetworkPolicy
and admission policy are committed, but the cluster runs without the
relevant enforcement capability. What rating is justified?

-   **Answer:** At most partial/emerging; enforcement is not
    demonstrated. Verify CNI and policy-engine mode/scope, run a
    negative fixture, or record an approved profile-specific N-A where
    genuinely unsupported.
-   **Why the tempting answer fails:** Desired configuration is not
    proof that a controller enforces it.

**Q8 --- High score with a blocker (L4).** A submission scores 91/100
but registry, GitOps and runtime digests differ. Can it be approved?

-   **Answer:** No. G-02 blocks release independently of the numeric
    score.
-   **Why the tempting answer fails:** A weighted average can hide a
    critical failure; the rubric explicitly prevents that.

**Q9 --- Local lab fidelity (L4).** A learner demonstrates a signed
image, least-privilege RBAC and a successful rollback in kind. Can they
claim production security certification?

-   **Answer:** No. The result proves bounded local mechanics and
    evidence discipline. Enterprise identity, real production threat
    resistance, compliance, traffic, cloud failure domains and
    organizational operations require separate validation.
-   **Why the tempting answer fails:** A realistic lab is still not the
    production environment or a formal assurance process.

#### Final reviewer sign-off template

``` text
M17 Unit 4 — Security and release review

Profile:
Service/workload:
Source repository and commit SHA:
CI run/build identity:
Registry artifact digest:
GitOps repository/revision:
Running workload digest:
Rubric version:
Reviewer / role:
Review timestamp (UTC):
Score / 100:
Critical gates: PASS / FAIL / NOT DEMONSTRATED
Non-waivable blockers:
Waivers (ID, owner, approver, expiry):
N-A items and rationale:
Residual risks:
Not demonstrated:
Required actions / owners / due dates:
Decision: GO / GO_WITH_CONDITIONS / NO_GO
Decision scope and limitations:
Next review date:
Reviewer signature/attestation reference:
```

A sign-off is valid only for the declared profile, artifact,
configuration and review time. A later change to source, dependency,
workflow, policy, image, model, GitOps revision or deployment may
invalidate evidence and require re-review.

#### \#### Authoring audit

  -----------------------------------------------------------------------------------
  Check                   Result                  Evidence/notes
  ----------------------- ----------------------- -----------------------------------
  Correct target and Unit PASS                    One standalone document:
  4 scope                                         `security-and-release-rubric.md`;
                                                  Unit 4 only

  Required headings       PASS                    All required headings present in
  4.0--4.15 in order                              the specified order

  M17 stage exit,         PASS                    Reproduced verbatim in the M17
  evidence set and pass                           contract
  rule                                            

  M01--M16 handoffs and   PASS                    Governing M17 prompt and supplied
  stack profiles                                  tree used

  Unit 1 REQ/AC/evidence  PASS                    Canonical Unit 1 IDs and singular
  contract                                        `requirement_id` schema used

  Cross-document          PASS                    Unit 3 shifted REQ crosswalk is
  discrepancy handling                            explicitly identified and not
                                                  propagated

  Four-level teaching     PASS                    L1--L4 progression included;
  model                                           criterion rating formula stated

  Rubric criteria and     PASS                    Nine criteria; weights sum to
  weights                                         exactly 100

  Non-waivable gates and  PASS                    Gate behavior independent of score;
  N-A/waiver policy                               N-A policy and expiry rules stated

  Rubric YAML parsing     PASS                    PyYAML parsed all nine criteria;
                                                  total weight = 100; all nine
                                                  require human review

  Scoring runner          PASS --- isolated       All-pass submission returned
                          synthetic scenarios     `READY_FOR_HUMAN_REVIEW` at 100.00;
                                                  critical-gate rating 1 returned
                                                  `BLOCKED`; missing evidence file
                                                  returned `BLOCKED`

  Three-way digest        PASS --- 7 isolated     Match, missing value, tag-only,
  verifier                unit tests              malformed digest and all three
                                                  pairwise mismatch cases

  Embedded static syntax  PASS                    14 code blocks checked; Python AST,
                                                  YAML, JSON, TOML and `bash -n`
                                                  checks reported no syntax errors

  RBAC audit, secret-scan PARTIAL                 Included; not executed against a
  config, SBOM step                               live lab/toolchain; exact local
                                                  versions/flags require verification

  Negative-test coverage  PASS --- design         Sixteen test designs list setup,
                          coverage                expected result and evidence; only
                                                  the digest-verifier unit tests were
                                                  executed

  Five progressive        PASS --- authored       LAB-SR-01 through LAB-SR-05 include
  hands-on labs                                   goal, prerequisites, steps,
                                                  evidence, cleanup, stretch and
                                                  failure modes; labs not executed

  Self-check questions    PASS                    Nine questions with answer keys and
                                                  explanations

  Review-board questions  PASS                    Exactly five questions with senior
                                                  model answers

  Live runtime execution  PARTIAL                 Isolated Python verifier/scorer
                                                  tests executed; no live CI,
                                                  scanner, registry, Kubernetes,
                                                  signature, SBOM generation or
                                                  deployment/rollback drill

  External version/syntax NOT VERIFIED            Version-sensitive items are listed
  verification                                    for learner verification

  Repository write        NOT VERIFIED            Standalone artifact created in the
  verification                                    session; no repository files were
                                                  edited
  -----------------------------------------------------------------------------------

**Human sign-off remains required.** This authoring audit is not a
security assessment, release approval, runtime test report or production
certification.
