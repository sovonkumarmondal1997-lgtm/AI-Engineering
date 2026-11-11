# Unit 1 --- Threat modelling for data and ML platforms

**Target file:** `01-threat-modelling-for-data-and-ml-platforms.md` \|
**Estimated time:** 12--16 hours \| **Prerequisites:** Stages 0--2D and
Stage 2E M01--M11\
**Core tools:** Markdown, Mermaid/ASCII DFDs, YAML, Python standard
library \| **Awareness:** MITRE ATT&CK, Microsoft Kubernetes threat
matrix, CIS Benchmarks, NIST SP 800-190, OWASP, CNCF Cloud Native
Security Whitepaper, LINDDUN, PASTA/OCTAVE/ATASM \| **Last reviewed:**
2026-10-29; reverify before production use \| **Tool/spec baseline:**
Python 3.11+ for examples; framework/spec versions `[VERIFY]` \|
**Footprint:** text-only core under 100 MB; measure yours \|
**Internet:** not needed for core labs; online references are for
current verification. Offline fallback: this lesson's synthetic
fixtures.

> **Defensive-only:** use synthetic data and a local workspace you own.
> Do not test third-party systems or use real credentials/data. Any
> unsafe-deserialization demonstration must be a benign marker-file test
> in a disposable, isolated directory; never load an untrusted model in
> a service.

## 1.0 Why this matters in production

A scanner may report many findings in a large Python image while the
most consequential risk is a CI identity that can push arbitrary images
to a registry which GitOps automatically deploys. A model-serving pod
with broad object-store access can turn a modest application weakness
into exposure of training data or model weights. Threat modelling makes
these paths explicit before selecting controls, so effort follows
plausible impact and trust assumptions rather than raw finding counts.
It comes first in M12 because scanning, SBOMs, signatures, provenance,
build isolation, identity, hardening, admission, auditing, and runtime
detection should each address a defined threat and have a test that
verifies the control.

## 1.1 Learning objectives

1.  Explain assets, actors, threats, vulnerabilities, risk, controls,
    and residual risk. `[L1]`
2.  Draw a DFD with external entities, processes, data stores, flows,
    and trust boundaries. `[L1]`
3.  Apply relevant STRIDE categories to DFD elements and flows. `[L1]`
4.  Enumerate platform threats with preconditions, assets, impact,
    owner, mitigation, and evidence. `[L2]`
5.  Rate likelihood and impact using explicit qualitative criteria and
    document uncertainty. `[L2]`
6.  Map threats to preventive, detective, corrective controls and
    negative tests. `[L2]`
7.  Validate a versioned threat-model fixture and generate a
    threat→control→test matrix. `[L2/L4]`
8.  Analyze software supply-chain, data, privacy, and ML attack paths,
    including unsafe model deserialization. `[L3]`
9.  Defend mitigation choices using risk reduction, effort, usability,
    and residual risk. `[L3]`
10. Design an operating model for ownership, reviews, acceptance,
    metrics, and incident-driven updates. `[L4]`

## 1.2 Concept map and vocabulary

  -----------------------------------------------------------------------
  Term                    Precise definition      Common misconception
  ----------------------- ----------------------- -----------------------
  Threat modelling        Structured analysis of  A one-time form or
                          what can go wrong, why, scanner report
                          and how to              
                          reduce/manage risk      

  Asset                   Valuable data,          Only servers are assets
                          identity, model,        
                          service, evidence, or   
                          delivery capability     

  Actor                   Person, service,        Every actor is an
                          organization, or        external attacker
                          process capable of      
                          causing an event        

  Threat                  Plausible harmful       Same as a vulnerability
                          scenario involving an   
                          actor/event and an      
                          asset                   

  Vulnerability           Weakness in design,     Automatically high risk
                          code, configuration,    
                          process, or assumption  

  Risk                    Contextual judgment of  A score is a precise
                          likelihood and impact,  probability
                          including uncertainty   

  Likelihood              Qualitative             "High" means a known
                          plausibility under      percentage
                          stated conditions       

  Impact                  Consequence to          Only downtime counts
                          confidentiality,        
                          integrity,              
                          availability, privacy,  
                          safety, or operations   

  Attack surface          Interfaces, inputs,     Only public ports
                          identities,             
                          dependencies, and trust 
                          boundaries reachable by 
                          threats                 

  Trust boundary          Point where identity,   Only a network
                          ownership, privilege,   perimeter
                          or assumptions change   

  Control                 Measure intended to     A documented control
                          prevent, detect, or     necessarily works
                          correct a threat        

  Residual risk           Risk remaining after    Controls reduce risk to
                          controls                zero

  Risk acceptance         Time-bounded decision   Verbal "fine for now"
                          by an authorized owner  is sufficient
                          to retain known risk    

  Abuse/misuse case       Scenario in which a     Only malicious users
                          feature is used to      matter
                          violate intended rules  
                          or cause harm           

  DFD                     Diagram of entities,    A diagram proves
                          processes, stores,      security
                          flows, and boundaries   

  Attack tree             Decomposition of an     It requires exploit
                          unwanted goal into      instructions
                          AND/OR paths            

  STRIDE                  Spoofing, Tampering,    Every category applies
                          Repudiation,            everywhere
                          Information Disclosure, 
                          Denial of Service,      
                          Elevation of Privilege  

  CIA                     Confidentiality,        CIA fully covers
                          Integrity, Availability privacy

  Privacy                 Appropriate collection, Encryption alone solves
                          use, disclosure,        privacy
                          inference, retention,   
                          and handling of         
                          personal information    

  Security debt           Unresolved weaknesses,  Undated backlog items
                          exceptions, or untested are harmless
                          assumptions increasing  
                          future risk/cost        

  SBOM                    Inventory of software   A certificate that
                          components in a defined software is safe
                          artifact                

  Signature               Cryptographic claim     Proof that the artifact
                          tied to an artifact     is benign
                          digest and a trust      
                          configuration           

  Provenance              Claims about source,    True merely because a
                          builder, inputs, and    document exists
                          production process      
  -----------------------------------------------------------------------

### The four questions

Use this practical sequence: **What are we working on? What can go
wrong? What are we going to do about it? Did we do a good enough job?**
Exact wording and attribution to the Threat Modeling Manifesto and/or
Adam Shostack must be checked against the current primary source before
formal quotation: `[VERIFY]`.

### Vulnerability, threat, and risk

-   **Weakness:** CI has a long-lived registry credential.
-   **Threat scenario:** compromised CI or a leaked credential is used
    to publish an unapproved image.
-   **Risk:** if promotion accepts mutable tags and the pod can read
    sensitive data, unauthorized code may run with data access.
-   **Control hypothesis:** scoped short-lived identity, digest
    promotion, and admission verification interrupt parts of the path.
-   **Test:** submit a benign disallowed artifact fixture in the local
    lab and verify rejection.

Use qualitative categories, not fake precision. A matrix is a
prioritization aid, not a calibrated probability.

### CIA, privacy, and sensitivity

-   **Confidentiality:** only authorized identities read data,
    credentials, weights, logs, and artifacts.
-   **Integrity:** code, data, models, configurations, and evidence are
    not altered unnoticed or accepted without authorization.
-   **Availability:** systems remain usable within acceptable
    objectives.
-   **Privacy:** personal data is used, inferred, shared, and retained
    appropriately.
-   **Sensitivity:** classify data by the harm that exposure or
    alteration could cause.

### End-to-end diagram

``` mermaid
flowchart LR
  Dev[Developer laptop] -->|reviewed source| Git[(Git)]
  Git --> CI[CI runner/build]
  Dep[Dependencies + base image] --> CI
  CI -->|image + evidence| Art[Artifact]
  Art --> Reg[(Registry)]
  Reg --> GitOps[GitOps controller]
  GitOps --> API[Kubernetes API]
  API --> Pods[Inference / ETL / notebook pods]
  Pods --> Obj[(Model + dataset store)]
  Pods --> DB[(Feature store / database)]
  Sec[(Secrets backend / workload identity)] --> Pods
  Pods --> Obs[(Logs / metrics / audit)]
  Scan[Scan + SBOM] -. inventory / known issues .-> Art
  Sign[Sign + provenance] -. identity / build claims .-> Art
  Admit[Admission policy] -. accept or reject .-> API
  Detect[Runtime detection] -. behavior signals .-> Pods
```

-   **Scanning** reports known issues visible to the scanner/database
    snapshot; it cannot prove safety.
-   **SBOM** inventories components; it may be incomplete and does not
    establish trust.
-   **Signing** verifies a signer's claim for an artifact digest under a
    trust setup; it does not prove the signer/build was uncompromised.
-   **Provenance** records build claims; its value depends on producer
    integrity and policy verification.
-   **Admission** rejects objects that violate configured policy; it
    cannot protect bypass paths or post-admission behavior.
-   **Runtime detection** observes selected behavior; it can miss events
    and does not prevent every compromise.

DFD notation: an **external entity** is outside the boundary; a
**process** transforms/routes data; a **data store** persists state; a
**flow** is a directional transfer; a **trust boundary** marks changed
identity, privilege, ownership, or assumptions. Name each flow, identify
data sensitivity and identity, and ask who can initiate it, what
authenticates it, what authorization applies, and what evidence remains.

## 1.3 Level 1 --- Beginner

### Assets and actors

  -----------------------------------------------------------------------
  Asset                  Example harm           Review question
  ---------------------- ---------------------- -------------------------
  Developer              Source or credentials  Are credentials scoped
  identity/laptop        exposed                and workstation risks
                                                considered?

  Git and approvals      Unauthorized           Who can merge and bypass
                         source/manifests       review?

  CI runner/cache        Build tampering or     Can untrusted jobs access
                         token exposure         release permissions?

  Dependencies/base      Malicious code enters  Are source and versions
  image                  build                  controlled?

  Image/model artifact   Tampering or unsafe    Is digest, origin, and
                         content                approval verified?

  Registry               Unauthorized push or   Who can
                         tag mutation           publish/promote/delete?

  Kubernetes             Privilege escalation   Are RBAC and workload
  API/nodes/pods         or lateral movement    privileges narrow?

  Training/inference     Exposure, poisoning,   Who can read/write, and
  data                   or integrity loss      is lineage retained?

  Model weights/metadata Theft, backdoor,       Is origin trusted and
                         unsafe deserialization format appropriate?

  Feature store/database Unauthorized           Are grants per workload?
                         reads/writes           

  Secrets                Credential misuse      Are identities
  backend/workload                              short-lived and scoped?
  identity                                      

  Observability          Secret leakage or      Are logs minimized,
                         evidence tampering     redacted, and protected?

  Notebook platform      Unreviewed code with   Are notebook identity and
                         broad access           egress constrained?
  -----------------------------------------------------------------------

Actors include external attackers, malicious/compromised dependency
maintainers, compromised CI, malicious insiders, careless developers,
compromised third-party services, curious tenants, and compromised
workloads. Define each actor's actual capability; do not grant them
omnipotence by assumption.

Trust boundaries include laptop→Git, Git→CI, CI→registry,
registry→GitOps, GitOps→Kubernetes API, pod→identity provider,
inference→model/data store, notebook→shared data, and
workload→observability. The attack surface includes APIs, dependency
resolution, build scripts, registry write permissions, GitOps
reconciliation, Kubernetes admission, service accounts, notebook
kernels, model importers, data queries, logs, and operational
procedures.

### STRIDE

  -----------------------------------------------------------------------
  Category                Meaning                 Example
  ----------------------- ----------------------- -----------------------
  Spoofing                Impersonating identity  Workload claims an
                                                  identity it should not
                                                  have

  Tampering               Unauthorized            Model artifact or
                          modification            manifest changes

  Repudiation             Cannot establish who    Promotion lacks
                          did what                actor/digest audit
                                                  evidence

  Information disclosure  Unauthorized exposure   Logs include sensitive
                                                  request fields

  Denial of service       Loss/degradation of     Expensive requests
                          availability            exhaust inference
                                                  capacity

  Elevation of privilege  Gaining excess          Pod can create
                          authority               privileged workloads
  -----------------------------------------------------------------------

STRIDE is a prompt, not an algorithm. Apply categories that fit and
explain why a category matters or does not.

### Guided lab: first DFD

**Footprint:** negligible; text-only. **Internet:** no. **Offline:** all
content below. **WSL2/native Linux:** both work; no cluster needed.
**Scope:** synthetic architecture only.

``` bash
mkdir -p threat-model-lab/models threat-model-lab/evidence
cd threat-model-lab
```

Save as `models/first-dfd.mmd`:

``` mermaid
flowchart LR
  Dev[Developer] -->|commit| Git[(Git)]
  Git --> CI[CI runner]
  CI -->|digest| Reg[(Registry)]
  Reg --> GitOps[GitOps]
  GitOps --> API[Kubernetes API]
  API --> Pod[Inference pod]
  Pod --> Store[(Model object store)]
  Pod --> DB[(Feature database)]
  Pod --> Obs[(Observability)]
  Secrets[(Secrets backend)] --> Pod
```

Review: are flows directional/named; are stores and privileged systems
visible; does each flow have an identity and authorization story; where
does sensitive data cross; what happens if a component is compromised?

**Evidence:** `models/first-dfd.mmd` plus short review notes. Rendering
is optional. **What happened?** An implicit architecture became
reviewable; the diagram is not proof that controls exist.

  -----------------------------------------------------------------------
  Mistake                 Symptom                 Fix
  ----------------------- ----------------------- -----------------------
  Boxes without arrows    No visible trust        Add directional named
                          crossing                flows

  CI omitted              Supply chain begins     Include source, build,
                          mysteriously at image   inputs, registry,
                                                  deploy

  Pod treated as one box  Identity/data           Separate workload,
                          boundaries hidden       identity, stores

  Logs ignored            Sensitive data and      Model log
                          audit integrity omitted read/write/delete paths

  Only happy path shown   Manual/break-glass      Add actual bypass paths
                          bypass absent           
  -----------------------------------------------------------------------

Cleanup: inspect the current directory before deleting; then remove only
the disposable workspace.

## 1.4 Level 2 --- Intermediate

### Full element and flow inventory

  ------------------------------------------------------------------------
  ID              Element                 Type            Main assets /
                                                          trust concern
  --------------- ----------------------- --------------- ----------------
  E01             Developer laptop        Entity          Source changes,
                                                          credentials

  E02             Git repository          Store           Source,
                                                          manifests,
                                                          approvals

  E03             CI runner/build system  Process         Build inputs,
                                                          tokens, logs

  E04             Dependency/base-image   Entity          Packages, base
                  sources                                 layers

  E05             Image/artifact + build  Artifact        Code, SBOM,
                  evidence                                provenance

  E06             Local registry          Store           Image blobs,
                                                          tags, manifests

  E07             GitOps controller       Process         Desired state,
                                                          reconciliation
                                                          identity

  E08             Kubernetes API server   Control plane   Cluster state
                                                          and admission
                                                          decisions

  E09             Cluster nodes           Runtime         Runtime and node
                                                          credentials

  E10             Workload pods           Runtime         Application,
                                                          identity,
                                                          mounted data

  E11             FastAPI inference       Process/API     Requests and
                  endpoint                                predictions

  E12             ETL/training pipeline   Process         Data transforms
                                                          and training
                                                          jobs

  E13             Model/dataset object    Store           Weights,
                  store                                   datasets,
                                                          lineage

  E14             Feature store/database  Store           Features,
                                                          labels, records

  E15             Secrets                 Service/store   Secret material
                  backend/workload                        and identity
                  identity                                claims

  E16             Observability stack     Store/service   Logs, metrics,
                                                          audit evidence

  E17             Notebook platform       Process         Interactive
                                                          code,
                                                          credentials,
                                                          data access
  ------------------------------------------------------------------------

  ------------------------------------------------------------------------------
  Flow            From → to             Data / identity      Main question
  --------------- --------------------- -------------------- -------------------
  F01             E01→E02               Commit/review        Can unauthorized
                                        metadata             changes merge?

  F02             E02→E03               Source/workflow      Can untrusted jobs
                                        context              access privileged
                                                             permissions?

  F03             E03↔E04               Package/base-image   Are inputs
                                        retrieval            controlled?

  F04             E03→E05               Image/build evidence Can output be tied
                                                             to inputs?

  F05             E05↔E06               Push/pull by digest  Who can publish or
                                                             mutate?

  F06             E06→E07               Promoted digest      Can mutable tags or
                                                             unapproved
                                                             artifacts be
                                                             selected?

  F07             E07→E08               Desired manifests    Is controller
                                                             privilege
                                                             constrained?

  F08             E08→E09/E10           Workload             Are admission and
                                        spec/runtime         runtime controls
                                                             applied?

  F09             E11→E13               Model/data reads     Is workload access
                                                             least-privileged?

  F10             E11→E14               Feature queries      Can one workload
                                                             access another
                                                             tenant?

  F11             E12→E13/E14           Training             Is lineage/write
                                        outputs/features     access auditable?

  F12             E10→E15               Identity/secret      Are trust and scope
                                        access               narrow?

  F13             E10/E11/E12/E17→E16   Logs/metrics/audit   Are secrets
                                                             redacted and logs
                                                             protected?

  F14             E17→E13/E14           Notebook             Is notebook access
                                        reads/writes         narrower than broad
                                                             store access?

  F15             Clients↔E11           Requests/responses   Are auth, limits,
                                                             and privacy
                                                             defined?
  ------------------------------------------------------------------------------

### STRIDE threat register

  ------------------------------------------------------------------------------------------------------------
  ID        Element/flow; STRIDE     Scenario and         Impact                       Control/test
                                     precondition                                      
  --------- ------------------------ -------------------- ---------------------------- -----------------------
  T01       E01/E02 F01; Tampering,  Source merges        Unauthorized code built      Protected review;
            Repudiation              without attributable                              unapproved-change test
                                     review                                            

  T02       E02/E03 F02; Elevation   Untrusted CI job     Unauthorized publication     Isolated jobs;
                                     accesses release                                  permission-denial test
                                     permissions                                       

  T03       E03/E04 F03; Tampering   Unintended           Runtime compromise           Controlled sources,
                                     dependency enters                                 SBOM/scan; inventory
                                     build                                             comparison

  T04       E03/E05 F04;             Artifact cannot be   Unaccountable artifact       Provenance
            Repudiation/Tampering    tied to approved     promotion                    verification;
                                     inputs                                            missing-evidence
                                                                                       rejection

  T05       E05/E06 F05;             Unauthorized         Unapproved image available   Scoped registry
            Spoofing/Tampering       registry publisher                                identity; denied-push
                                                                                       test

  T06       E06/E07/E08 F06--F07;    Mutable tag or       Unapproved code runs         Digest and artifact
            Tampering                unapproved digest                                 policy;
                                     promoted                                          disallowed-artifact
                                                                                       test

  T07       E07/E08 F07; Elevation   GitOps identity      Cross-namespace/privileged   Narrow RBAC;
                                     changes unrelated    changes                      unauthorized-resource
                                     resources                                         test

  T08       E08/E10 F08; Elevation   Pod requests unsafe  Node/neighbor risk           Admission/PSS;
                                     privilege/host                                    invalid-manifest test
                                     access                                            

  T09       E10/E11/E13/E14          Inference identity   Dataset/PII exposure         Scoped grants;
            F09--F10; Disclosure     reads unrelated data                              cross-scope denial

  T10       E12/E13/E14 F11;         Data/labels altered  Model integrity harm         Write controls,
            Tampering                without lineage                                   lineage;
                                                                                       unauthorized-write test

  T11       E10/E15 F12;             Workload identity    Secret/downstream access     Narrow trust/roles;
            Spoofing/Elevation       trust too broad                                   unauthorized identity
                                                                                       denied

  T12       E10/E16 F13; Disclosure  Logs contain secrets Credential leak/lost         Redaction and separate
                                     or are deletable by  evidence                     roles; synthetic marker
                                     workload                                          test

  T13       E17/E13/E14 F14;         Notebook accesses    Exposure or poisoning        Per-notebook identity;
            Disclosure/Tampering     shared data too                                   cross-scope denial
                                     broadly                                           

  T14       E11/F15; DoS             Expensive/repeated   Inference outage             Auth, limits, timeouts;
                                     requests exhaust                                  bounded load test
                                     capacity                                          

  T15       E11/E13 F09;             Untrusted pickle     Code execution in loader     Reject untrusted
            Tampering/Elevation      loaded by privileged context                      pickle; intake test
                                     process                                           

  T16       E16/F13;                 Audit events lack    Weak investigation/privacy   Structured minimal
            Repudiation/Disclosure   actor/digest or      harm                         logs; audit/redaction
                                     expose payloads                                   test
  ------------------------------------------------------------------------------------------------------------

### Qualitative risk criteria

**Likelihood:** Low = requires uncommon conditions and controls appear
effective; Medium = plausible through realistic access or a known
weakness; High = reachable through ordinary exposure, broad permissions,
or absent/failed controls; Unknown = evidence insufficient and requires
investigation.

**Impact:** Low = limited recoverable effect on non-sensitive assets;
Medium = material degradation or limited exposure/integrity loss; High =
sensitive data/model exposure, unauthorized production code,
cross-tenant access, or sustained outage; Critical = severe broad harm
as defined by the organization.

  ---------------------------------------------------------------------
  Likelihood    Low           Medium        High          Critical
   Impact                                                 
  ------------- ------------- ------------- ------------- -------------
  Low           Low           Low/Medium    Medium        High

  Medium        Low/Medium    Medium        High          High

  High          Medium        High          High          Highest

  Unknown       Investigate   Investigate   Investigate   Investigate
                                            urgently      urgently
  ---------------------------------------------------------------------

Adjust for sensitivity, reach, dependencies, and uncertainty. Document
why a rating was selected and what evidence could change it. This is not
a probability model.

  -----------------------------------------------------------------------------
  Threat         L            I            Uncertainty   Priority / action
  -------------- ------------ ------------ ------------- ----------------------
  T05            Medium       High         Medium        High; test denied push
  unauthorized                                           
  registry push                                          

  T09 broad data Medium       Critical     High          Highest/investigate;
  identity                                               inventory actual
                                                         grants

  T12 sensitive  Medium       High         Medium        High; synthetic marker
  logs                                                   redaction test

  T14 inference  Medium       Medium       Medium        Medium; test
  exhaustion                                             quotas/timeouts
  -----------------------------------------------------------------------------

DREAD's current status and the exact claim that it is "discouraged" must
be verified: `[VERIFY]`. The practical concern with multi-factor numeric
schemes is false precision when subjective inputs are inconsistent. This
lesson uses explicit qualitative criteria, rationale, uncertainty, and
ownership instead of pretending ordinal scores are probabilities.

### Controls and M12 handoff

  ----------------------------------------------------------------------------------------------------------
  Threat group     Prevent                 Detect                   Correct          Residual risk
  ---------------- ----------------------- ------------------------ ---------------- -----------------------
  Source/CI        Protected reviews,      Audit/workflow checks    Revoke           Compromised
  T01--T02         least-privilege jobs,                            credentials,     reviewer/build service
                   isolated runners                                 revert/rebuild   

  Build/artifact   Controlled inputs,      Scan, SBOM review,       Quarantine,      Unknown malicious
  T03--T06         digest promotion,       registry audit           rebuild, roll    behavior/trusted signer
                   verified                                         back             compromise
                   signatures/provenance                                             

  Cluster T07--T08 RBAC, PSS, admission    Kubernetes audit/policy  Revoke roles,    Admin/node compromise
                                           reports                  isolate workload 

  Data/identity    Per-workload grants,    Data access audit        Revoke access,   Legitimate
  T09--T13         scoped identity, egress                          rotate exposed   abuse/unlogged paths
                   controls                                         credentials      

  Inference T14    Auth, quotas, timeouts  Rate/latency/error       Limit or disable Distributed
                                           telemetry                endpoint         demand/model-specific
                                                                                     abuse

  Model import T15 Reject untrusted        Artifact-origin/intake   Quarantine and   Parser
                   pickle; isolate intake  audit                    replace          bugs/trusted-source
                                                                                     compromise

  Observability    Minimize/redact logs,   Synthetic marker scan,   Restrict access  Unknown sensitive
  T12/T16          separate roles          audit review             and rotate       formats
                                                                    exposed secrets  
  ----------------------------------------------------------------------------------------------------------

M01 already introduced hardening, digest pinning, Trivy/Syft basics, and
cosign awareness; M12 deepens triage, SBOM lifecycle, signing policy,
and provenance. M02 covered CI/CD, runner security, permissions, SHA
pinning, and OIDC concepts; Unit 5 applies isolation and ephemeral
identity. M03 RBAC/PSS are reused by Units 7--8. M04
NetworkPolicy/mTLS/egress are referenced, not retaught. M06 chart
verification and manifest checks are reused. M08 promotion by digest and
GitOps evidence chains are reused; admission-time verification is
deferred to M12. M09 owns identity/federation/secrets mechanics; Unit 1
models attack paths and validation without re-teaching them. M10
incident/postmortem practice and M11 telemetry pipelines are reused.

### Filled risk register

The following entries are illustrative risk-register rows for the
running example. Ratings are qualitative, and owners are roles to be
replaced with accountable people in a real environment.

  -----------------------------------------------------------------------------------------------------------------------------------------------------------
  Risk ID Threat         Likelihood   Impact     Priority   Existing/proposed   Negative test / evidence               Owner           Residual risk
                                                            control                                                                    
  ------- -------------- ------------ ---------- ---------- ------------------- -------------------------------------- --------------- ----------------------
  R01     T01 unreviewed Medium       High       High       Protected review    Unapproved synthetic change rejected;  Source owner    Trusted reviewer or
          source reaches                                    and attributable    `evidence/source-review.txt`                           SCM compromise
          release                                           approvals                                                                  

  R02     T02 untrusted  Medium       High       High       Separate untrusted  Verify no release secret/publish       CI owner        Runner/control-plane
          CI job                                            jobs and release    permission;                                            compromise
          accesses                                          identity            `evidence/ci-permissions.txt`                          
          release                                                                                                                      
          permissions                                                                                                                  

  R03     T03 unintended Medium       High       High       Controlled          Compare fixture inventory;             Build owner     Novel malicious
          dependency                                        dependency sources, `evidence/dependency-inventory.txt`                    dependency may evade
          enters build                                      inventory and                                                              detection
                                                            triage                                                                     

  R04     T05            Medium       High       High       Scoped publisher    Unauthorized local push denied;        Registry owner  Registry administrator
          unauthorized                                      identity and digest `evidence/registry-denial.txt`                         compromise
          registry                                          promotion                                                                  
          publication                                                                                                                  

  R05     T06 unapproved Medium       High       High       Verify digest,      Missing-evidence fixture rejected;     Release owner   Trusted signer/build
          artifact is                                       signature and       `evidence/artifact-verification.txt`                   compromise
          promoted                                          provenance policy                                                          

  R06     T09 inference  Medium       Critical   Highest    Per-workload        Cross-scope synthetic read denied;     Data owner      Privileged
          identity reads                                    identity and        `evidence/data-access-denial.txt`                      administrator or data
          unrelated data                                    least-privilege                                                            service compromise
                                                            data grants                                                                

  R07     T12 sensitive  Medium       High       High       Minimize/redact     Synthetic marker absent/redacted;      Observability   Unknown sensitive
          values leak                                       fields and separate `evidence/redaction.txt`               owner           formats or alternate
          into logs                                         log privileges                                                             log paths

  R08     T14 inference  Medium       Medium     Medium     Authentication,     Requests over configured limit         Inference owner Distributed load or
          resource                                          bounded input,      throttled;                                             model-specific
          exhaustion                                        quotas and timeouts `evidence/inference-limit.txt`                         expensive inputs

  R09     T15 untrusted  Medium       Critical   Highest    Reject untrusted    Untrusted fixture rejected before      ML platform     Parser flaws or
          pickle                                            pickle; isolate     serving; `evidence/model-intake.txt`   owner           compromised trusted
          executes in                                       artifact intake                                                            source
          loader                                                                                                                       

  R10     T13 notebook   Medium       High       High       Separate notebook   Cross-scope read denied;               Notebook owner  User may misuse
          identity                                          identities, narrow  `evidence/data-access-denial.txt`                      legitimately granted
          accesses                                          grants, egress                                                             data
          shared data                                       policy                                                                     
  -----------------------------------------------------------------------------------------------------------------------------------------------------------

A real register also needs a creation date, due date, status, decision
history, and a review date. Do not treat the illustrative rows as
evidence that controls have been implemented.

### Risk acceptance template

``` yaml
acceptance_id: RA-EXAMPLE-001
threat_id: T14
decision: accepted_temporarily
rationale: "Illustrative local-lab example only"
residual_likelihood: medium
residual_impact: medium
compensating_controls:
  - "Endpoint disabled outside local lab"
  - "Synthetic requests only"
owner_role: "Service owner"
approver_role: "Authorized risk owner"
approved_at: "YYYY-MM-DD"
expires_at: "YYYY-MM-DD"
review_trigger:
  - "Before external exposure"
  - "After related incident or architecture change"
closure_evidence: "Passing rate-limit and timeout test"
```

No verbal or indefinite acceptance. Record the threat, remaining risk,
rationale, compensating controls, accountable owner, authorized
approver, expiry, review trigger, and closure evidence.

### Canonical threat-model artifact

A full model should be versioned in Git and contain scope,
architecture/DFD reference, assumptions, elements, flows, threats,
controls, tests, owners, statuses, evidence paths, review metadata, and
accepted residual risks. Example schema:

``` yaml
schema_version: "1.0"
model:
  id: "TM-DATA-ML-LOCAL"
  title: "Local data and ML delivery platform"
  owner: "Platform security owner"
  reviewer: "Data/ML platform reviewer"
  created: "2026-10-29"
  last_reviewed: "2026-10-29"
  review_due: "2027-01-29"
  status: "draft"
  scope:
    included: ["source-to-runtime delivery", "inference/ETL", "model/data stores", "identity", "notebooks", "observability"]
    excluded: ["cloud-provider internals", "GPU driver implementation", "compliance determination"]
  assumptions:
    - id: A01
      statement: "All lab identities and data are synthetic."
      validation: "Review fixture directory before each run."
      owner: "Learner"
    - id: A02
      statement: "GitOps deploys only the reviewed desired state."
      validation: "Compare reviewed and running digest."
      owner: "Platform owner"
elements:
  - {id: E01, name: "Developer laptop", type: "external_entity"}
  - {id: E02, name: "Git", type: "data_store"}
  - {id: E03, name: "CI runner", type: "process"}
  - {id: E04, name: "Dependency/base-image sources", type: "external_entity"}
  - {id: E05, name: "Container artifact", type: "artifact"}
  - {id: E06, name: "Registry", type: "data_store"}
  - {id: E07, name: "GitOps controller", type: "process"}
  - {id: E08, name: "Kubernetes API server", type: "process"}
  - {id: E09, name: "Cluster nodes", type: "process"}
  - {id: E10, name: "Workload pods", type: "process"}
  - {id: E11, name: "FastAPI inference", type: "process"}
  - {id: E12, name: "ETL/training pipeline", type: "process"}
  - {id: E13, name: "Model/dataset object store", type: "data_store"}
  - {id: E14, name: "Feature database", type: "data_store"}
  - {id: E15, name: "Secrets/workload identity", type: "service"}
  - {id: E16, name: "Observability", type: "data_store"}
  - {id: E17, name: "Notebook platform", type: "process"}
flows:
  - {id: F01, from: E01, to: E02, data: "Commit/review metadata", identity: "Developer"}
  - {id: F02, from: E02, to: E03, data: "Reviewed source", identity: "CI job"}
  - {id: F03, from: E03, to: E04, data: "Dependency retrieval", identity: "Build job"}
  - {id: F04, from: E03, to: E05, data: "Image/build evidence", identity: "Builder"}
  - {id: F05, from: E05, to: E06, data: "Artifact push by digest", identity: "Publisher"}
  - {id: F06, from: E06, to: E07, data: "Promoted digest", identity: "GitOps reader"}
  - {id: F07, from: E07, to: E08, data: "Deployment manifests", identity: "GitOps identity"}
  - {id: F08, from: E08, to: E09, data: "Scheduled workload", identity: "Control plane"}
  - {id: F09, from: E11, to: E13, data: "Model/data read", identity: "Inference identity"}
  - {id: F10, from: E11, to: E14, data: "Feature query", identity: "Inference identity"}
  - {id: F11, from: E12, to: E13, data: "Training outputs", identity: "Training identity"}
  - {id: F12, from: E10, to: E15, data: "Identity/secret access", identity: "Workload"}
  - {id: F13, from: E10, to: E16, data: "Logs/metrics/audit", identity: "Telemetry identity"}
  - {id: F14, from: E17, to: E13, data: "Notebook model/data access", identity: "Notebook identity"}
controls:
  - {id: C01, name: "Protected source review", owner: "Source owner", test_id: TEST-T01, evidence_path: "evidence/source-review.txt", monitoring: "Review audit", mitigates: [T01]}
  - {id: C02, name: "Separate untrusted CI permissions", owner: "CI owner", test_id: TEST-T02, evidence_path: "evidence/ci-permissions.txt", monitoring: "Workflow audit", mitigates: [T02]}
  - {id: C03, name: "Dependency inventory and triage", owner: "Build owner", test_id: TEST-T03, evidence_path: "evidence/dependency-inventory.txt", monitoring: "SBOM/scan freshness", mitigates: [T03, T10]}
  - {id: C04, name: "Digest/provenance verification", owner: "Release owner", test_id: TEST-T04, evidence_path: "evidence/artifact-verification.txt", monitoring: "Verification failures", mitigates: [T04, T06]}
  - {id: C05, name: "Scoped registry publishing", owner: "Registry owner", test_id: TEST-T05, evidence_path: "evidence/registry-denial.txt", monitoring: "Registry write audit", mitigates: [T05]}
  - {id: C06, name: "Narrow cluster permissions", owner: "Cluster owner", test_id: TEST-T07, evidence_path: "evidence/rbac-tests.txt", monitoring: "Kubernetes audit", mitigates: [T07, T08]}
  - {id: C07, name: "Scoped workload/data identity", owner: "Data owner", test_id: TEST-T09, evidence_path: "evidence/data-access-denial.txt", monitoring: "Data access audit", mitigates: [T09, T11, T13]}
  - {id: C08, name: "Protected/redacted logs", owner: "Observability owner", test_id: TEST-T12, evidence_path: "evidence/redaction.txt", monitoring: "Redaction checks", mitigates: [T12, T16]}
  - {id: C09, name: "Safe model intake", owner: "ML platform owner", test_id: TEST-T15, evidence_path: "evidence/model-intake.txt", monitoring: "Artifact origin review", mitigates: [T15]}
  - {id: C10, name: "Inference limits", owner: "Inference owner", test_id: TEST-T14, evidence_path: "evidence/inference-limit.txt", monitoring: "Rate/latency metrics", mitigates: [T14]}
tests:
  - {id: TEST-T01, threat_id: T01, method: "Unapproved synthetic change", expected: "Review gate rejects it"}
  - {id: TEST-T02, threat_id: T02, method: "Inspect untrusted job permissions", expected: "No release secret or publish permission"}
  - {id: TEST-T03, threat_id: T03, method: "Compare local dependency fixture inventory", expected: "Inventory retained; gaps flagged"}
  - {id: TEST-T04, threat_id: T04, method: "Use artifact fixture without provenance", expected: "Policy rejects or flags missing evidence"}
  - {id: TEST-T05, threat_id: T05, method: "Attempt unauthorized local registry push", expected: "Push denied"}
  - {id: TEST-T07, threat_id: T07, method: "Use test identity on unrelated namespace", expected: "Authorization denied"}
  - {id: TEST-T09, threat_id: T09, method: "Request unrelated synthetic dataset", expected: "Access denied and audited"}
  - {id: TEST-T12, threat_id: T12, method: "Log a synthetic secret marker", expected: "Marker redacted or absent"}
  - {id: TEST-T14, threat_id: T14, method: "Send bounded requests above configured limit", expected: "Throttled/rejected"}
  - {id: TEST-T15, threat_id: T15, method: "Submit untrusted model fixture to intake", expected: "Rejected before serving process"}
threats:
  - {id: T01, scenario: "Unreviewed source reaches release", owner: "Source owner", element_ids: [E01, E02], flow_ids: [F01], stride: [Tampering, Repudiation], likelihood: medium, impact_level: high, priority: high, mitigation_ids: [C01], status: mitigating, evidence: [TEST-T01]}
  - {id: T02, scenario: "Untrusted CI job has release permissions", owner: "CI owner", element_ids: [E02, E03], flow_ids: [F02], stride: [Elevation of Privilege], likelihood: medium, impact_level: high, priority: high, mitigation_ids: [C02], status: mitigating, evidence: [TEST-T02]}
  - {id: T03, scenario: "Unintended dependency enters build", owner: "Build owner", element_ids: [E03, E04], flow_ids: [F03], stride: [Tampering], likelihood: medium, impact_level: high, priority: high, mitigation_ids: [C03], status: mitigating, evidence: [TEST-T03]}
  - {id: T04, scenario: "Artifact origin cannot be established", owner: "Release owner", element_ids: [E03, E05], flow_ids: [F04], stride: [Repudiation, Tampering], likelihood: medium, impact_level: high, priority: high, mitigation_ids: [C04], status: mitigating, evidence: [TEST-T04]}
  - {id: T05, scenario: "Unauthorized registry publication", owner: "Registry owner", element_ids: [E05, E06], flow_ids: [F05], stride: [Spoofing, Tampering], likelihood: medium, impact_level: high, priority: high, mitigation_ids: [C05], status: mitigating, evidence: [TEST-T05]}
  - {id: T06, scenario: "Unapproved artifact promoted", owner: "Release owner", element_ids: [E06, E07, E08], flow_ids: [F06, F07], stride: [Tampering], likelihood: medium, impact_level: high, priority: high, mitigation_ids: [C04], status: mitigating, evidence: [TEST-T04]}
  - {id: T07, scenario: "GitOps identity alters unrelated resources", owner: "Cluster owner", element_ids: [E07, E08], flow_ids: [F07], stride: [Elevation of Privilege], likelihood: medium, impact_level: high, priority: high, mitigation_ids: [C06], status: mitigating, evidence: [TEST-T07]}
  - {id: T08, scenario: "Workload requests unsafe privileges", owner: "Cluster owner", element_ids: [E08, E10], flow_ids: [F08], stride: [Elevation of Privilege], likelihood: medium, impact_level: high, priority: high, mitigation_ids: [C06], status: mitigating, evidence: [TEST-T07]}
  - {id: T09, scenario: "Inference identity reads unrelated data", owner: "Data owner", element_ids: [E10, E11, E13, E14], flow_ids: [F09, F10], stride: [Information Disclosure], likelihood: medium, impact_level: critical, priority: highest, mitigation_ids: [C07], status: mitigating, evidence: [TEST-T09]}
  - {id: T10, scenario: "Training or feature data altered without lineage", owner: "Data owner", element_ids: [E12, E13, E14], flow_ids: [F11], stride: [Tampering], likelihood: medium, impact_level: high, priority: high, mitigation_ids: [C03], status: mitigating, evidence: [TEST-T03]}
  - {id: T11, scenario: "Workload identity trust too broad", owner: "Identity owner", element_ids: [E10, E15], flow_ids: [F12], stride: [Spoofing, Elevation of Privilege], likelihood: medium, impact_level: high, priority: high, mitigation_ids: [C07], status: mitigating, evidence: [TEST-T09]}
  - {id: T12, scenario: "Sensitive data leaks through logs", owner: "Observability owner", element_ids: [E10, E16], flow_ids: [F13], stride: [Information Disclosure], likelihood: medium, impact_level: high, priority: high, mitigation_ids: [C08], status: mitigating, evidence: [TEST-T12]}
  - {id: T13, scenario: "Notebook accesses shared data too broadly", owner: "Notebook owner", element_ids: [E17, E13, E14], flow_ids: [F14], stride: [Information Disclosure, Tampering], likelihood: medium, impact_level: high, priority: high, mitigation_ids: [C07], status: mitigating, evidence: [TEST-T09]}
  - {id: T14, scenario: "Inference resource exhaustion", owner: "Inference owner", element_ids: [E11], flow_ids: [F15], stride: [Denial of Service], likelihood: medium, impact_level: medium, priority: medium, mitigation_ids: [C10], status: mitigating, evidence: [TEST-T14]}
  - {id: T15, scenario: "Untrusted pickle executes during model import", owner: "ML platform owner", element_ids: [E11, E13], flow_ids: [F09], stride: [Tampering, Elevation of Privilege], likelihood: medium, impact_level: critical, priority: highest, mitigation_ids: [C09], status: mitigating, evidence: [TEST-T15]}
  - {id: T16, scenario: "Audit evidence is missing or sensitive", owner: "Observability owner", element_ids: [E16], flow_ids: [F13], stride: [Repudiation, Information Disclosure], likelihood: medium, impact_level: high, priority: high, mitigation_ids: [C08], status: mitigating, evidence: [TEST-T12]}
```

The YAML is a human-readable model example; verify syntax with a YAML
parser before use. The dependency-free validator below deliberately
consumes a normalized JSON fixture, not YAML.

### Attack tree A --- run attacker-controlled code in inference pod

``` text
ROOT OR: attacker-controlled code runs in inference pod
  A AND: malicious code enters an accepted image
    OR: compromised source / unreviewed merge / unintended dependency
    AND: release controls accept artifact
      missing provenance verification + broad registry/promote permissions
  B AND: untrusted model file is executed by loader
    artifact intake accepts file + privileged process deserializes pickle
  C AND: deployment constraints are bypassed
    alternate deployment path + insufficient workload restrictions
```

**High-leverage cut points:** isolate untrusted CI, scope release
identity, verify digest/signature/provenance, enforce admission, deny
unsafe privileges, and reject untrusted pickle. Each interrupts a
different branch.

### Attack tree B --- exfiltrate training dataset

``` text
ROOT OR: unauthorized party obtains training dataset
  A AND: obtain identity + identity has broad dataset grants
  B AND: influence deployed workload + policy accepts it + workload can reach store
  C OR: broad notebook export / sensitive logs / over-sharing to third party
  D OR: backup or artifact copy has weaker access controls
```

Cut points include per-workload data grants, restricted egress/export,
minimal logs, independent backup controls, lineage, and audit. Alternate
copies and legitimate-but-abusive access remain residual risks.

### Frameworks, abuse cases, and method choice

Use frameworks as vocabularies, not substitutes for system-specific
reasoning. Current names/status/versions must be verified: MITRE ATT&CK
for Containers/Cloud `[VERIFY]`; Microsoft Kubernetes threat matrix
`[VERIFY]`; CIS Kubernetes Benchmark and applicability to kind
`[VERIFY]`; NIST SP 800-190, *Application Container Security Guide*;
OWASP Top 10, Kubernetes Top Ten, CI/CD Security Risks, and Top 10 for
LLM Applications `[VERIFY]`; CNCF Cloud Native Security Whitepaper
`[VERIFY]`; SLSA specification/threat model `[VERIFY]`; MITRE ATLAS
`[VERIFY]`; LINDDUN `[VERIFY]`.

  -----------------------------------------------------------------------
  Method                  Effort / fit            Limitation
  ----------------------- ----------------------- -----------------------
  STRIDE                  DFD-based engineering   Does not rank risk or
                          review; moderate effort prove coverage alone

  Attack trees            Goal-oriented paths and Can omit operational
                          cut points              context

  PASTA                   More structured,        Can be heavy for small
                          risk-centric; details   changes
                          `[VERIFY]`              

  OCTAVE                  Organizational          May not supply
                          asset/risk focus;       implementation tests
                          details `[VERIFY]`      alone

  ATASM                   Current name/details    Verify method and fit
                          `[VERIFY]`              before adopting
  -----------------------------------------------------------------------

Abuse/misuse examples: inference clients send expensive requests;
notebooks use shared credentials to read unrelated data; training
pipelines consume altered labels without lineage; model import loads an
untrusted pickle. Model changes when new dependencies/model sources,
data classes, identities, trust boundaries, notebooks, incidents, or
near misses occur. Keep reviews collaborative and time-boxed; output a
prioritized backlog, not just a diagram.

## 1.5 Level 3 --- Advanced

### Supply-chain stage-by-stage analysis

  -----------------------------------------------------------------------------------------------------------
  Stage               Asset and scenario        Trust        Controls / evidence            Residual risk
                                                assumption                                  
  ------------------- ------------------------- ------------ ------------------------------ -----------------
  Source              Compromised               Reviews      Protected review; approval     Trusted reviewer
                      maintainer/account or     identify     audit                          compromise
                      unreviewed merge          harmful                                     
                                                changes                                     

  Build               Compromised runner,       Builder and  Unit 5 isolation; permissions  Build service
                      poisoned cache, malicious job          test                           compromise
                      build script              isolation                                   
                                                are sound                                   

  Inputs              Dependency                Package      Units 2--3 scanning/SBOM;      Novel malicious
                      confusion/typosquatting   source and   inventory review               package
                      or compromised base image identity are                                
                                                controlled                                  

  Artifact/registry   Tampering, mutable tag,   Digest and   Units 4/6; unauthorized push   Trusted
                      stolen push identity      publisher    and digest tests               signer/registry
                                                are verified                                admin compromise

  Deploy              Pipeline bypass, manual   All deploy   Units 8/11 admission/policy;   Cluster-admin
                      kubectl, overprivileged   paths are    rejection test                 bypass
                      GitOps                    governed                                    

  Runtime             Escape attempt, lateral   Pod          Units 6/7/12                   Node/kernel
                      movement, credential      boundaries   identity/hardening/detection   compromise
                      misuse, data access       and data                                    
                                                grants hold                                 

  Model artifact      Unsafe format, poisoned   Source and   Intake review, provenance,     Model behavior
                      data, backdoor, unknown   lineage      safe format decision           and parser risk
                      origin                    evidence are                                
                                                credible                                    
  -----------------------------------------------------------------------------------------------------------

Do not reproduce SLSA threat categories A--I from memory. Verify the
current authoritative threat-model specification first; until then use
general classes above, not official category labels.

ML/data risks include training-data poisoning, model backdoors, unsafe
pickle deserialization, model theft/extraction, membership
inference/privacy leakage, adversarial inputs, prompt injection and data
exfiltration for LLM endpoints, compromised notebooks, poisoned feature
stores, unsafe model hubs, GPU/driver supply chain (Awareness),
over-broad data access, shared service accounts, credentials in
notebooks/DAGs, encryption gaps, backup exposure, and data-residency
concerns (Awareness; no legal advice). LINDDUN is Awareness-level;
verify current source details.

A chain such as
`leaked CI token → unauthorized image push → GitOps deployment → workload identity → sensitive store`
depends on multiple assumptions. Interrupt it at token scope/lifetime,
registry write permissions, digest promotion, signature/provenance
verification, admission, workload identity scope, data authorization,
and audit. Document each assumption and a test that challenges it.

### Threat prioritization and defended exercise

Group threats by shared prerequisite, identify high-leverage controls,
estimate cost/operational burden, define a negative test, assign an
owner, and reassess residual risk. Keep a security-debt register with
ID, priority, due date, owner, dependencies, compensating controls,
acceptance expiry, and closure evidence.

**Exercise:** A pilot has (a) many low/medium image findings with no
known reachable path, (b) a shared inference identity that can read
every training dataset, and (c) missing model provenance. Choose three
actions, justify order, and define one negative test for each. A strong
answer prioritizes actual data-access blast radius and artifact
acceptance risk based on deployment context, while triaging scanner
findings by reachability, exploitability, and impact---not by count
alone.

### Safe model-deserialization workshop

Python pickle is not a safe interchange format for untrusted data;
deserialization may invoke behavior in the loader process. Do not
download or load a public-hub model. If demonstrating the risk, author
and inspect a benign local-only marker test, run it in a disposable
directory without credentials, network, or sensitive files, verify only
the intended marker is created, and delete the workspace. This is not a
reusable exploit.

### Optional bounded marker demonstration

Only perform this exercise in a fresh disposable directory with no
network, credentials, or sensitive files. Read the code before running
it. It creates a marker file in the current directory; it does not
contact a network or read secrets. Do not use this pattern with real or
third-party model files.

Create `pickle_marker_demo.py`:

``` python
import pickle
from pathlib import Path

MARKER = Path("DISPOSABLE_LAB_MARKER.txt")

class MarkerOnly:
    def __reduce__(self):
        # The only intended side effect is writing a harmless marker locally.
        return (Path.write_text, (MARKER, "marker created by disposable lab demo"))

# Create the fixture locally, then load it in the same disposable directory.
fixture = Path("marker-only-fixture.pkl")
fixture.write_bytes(pickle.dumps(MarkerOnly()))
print("Created local fixture:", fixture)

loaded = pickle.loads(fixture.read_bytes())  # Deliberately unsafe for untrusted input.
print("Marker exists:", MARKER.exists())
print("Marker content:", MARKER.read_text(encoding="utf-8") if MARKER.exists() else "MISSING")
```

Run only in the disposable directory:

``` bash
python pickle_marker_demo.py
```

Expected illustrative evidence: `Marker exists: True` and the marker
content states that it was created by the lab demo. This output is
illustrative, not authoring-time execution evidence. The key observation
is that unpickling can invoke the callable represented by the serialized
object; this is why an untrusted pickle can execute code in the loader's
process context. The demonstration is a safety-bounded proof of the
risk, not a reusable exploit. Immediately remove the disposable
directory after inspecting the marker.

Mitigations: reject untrusted pickle; verify source/digest and
provenance; separate intake from serving; validate in a low-privilege
isolated process; prefer a more constrained format such as safetensors
or ONNX when appropriate and after checking current capabilities; retain
lineage/evaluation/approval evidence; test that the service rejects
untrusted artifacts. No format eliminates parser bugs or malicious model
behavior.

### Validation chain

For every high-risk threat, record **threat → control → test → expected
evidence → monitoring/owner**. Example: T09 → C07 scoped identity →
TEST-T09 synthetic cross-scope read → `evidence/data-access-denial.txt`
→ data-access audit and named data owner. A safe purple-team-style
exercise uses deliberately invalid manifests/identity fixtures in the
learner's own disposable lab; it is not the full M12 capstone.

## 1.6 Level 4 --- Expert

### Reusable patterns

  -----------------------------------------------------------------------
  Pattern                 Typical boundary        Questions
  ----------------------- ----------------------- -----------------------
  API service             Client, service         Can input exhaust
                          identity, backing       capacity or disclose
                          stores, telemetry       data?

  Batch/ETL               Scheduler, worker,      Can input be
                          source/sink, job        substituted? Are
                          identity                retries and lineage
                                                  controlled?

  Model serving           Image, model artifact,  Is origin verified and
                          inference, feature      deserialization safe?
                          store                   

  Notebook platform       User session, kernel,   Are credentials/data
                          shared storage, egress  isolated by user?

  CI fleet                Source, job, runner,    Can untrusted jobs
                          cache, secrets,         cross permission
                          registry                boundaries?

  GitOps controller       Desired-state repo,     Can it alter unrelated
                          controller identity,    namespaces or bypass
                          cluster API             review?
  -----------------------------------------------------------------------

### Threat-model-as-code

Keep Markdown/YAML in Git. A production pipeline should validate
syntax/schema, unique IDs, references, named owners, review dates,
mitigation or accepted risk for every threat, test/evidence for every
control, and generated traceability. Human review is still needed for
semantic completeness. Optional `pytm`/Threagile syntax and maintenance
status are `[VERIFY]`.

Create `validate_model.py`:

``` python
import json, sys
from pathlib import Path

TOP = {"schema_version", "model", "elements", "flows", "controls", "tests", "threats"}

def validate(d):
    errors = []
    missing = TOP - set(d)
    if missing:
        return [f"missing top-level keys: {', '.join(sorted(missing))}"]
    for key in ("id", "title", "owner", "last_reviewed", "review_due", "scope", "assumptions"):
        if not d["model"].get(key):
            errors.append(f"model missing required field: {key}")
    elems = {x.get("id") for x in d["elements"]}
    controls = {x.get("id") for x in d["controls"]}
    tests = {x.get("id") for x in d["tests"]}
    threats = {x.get("id") for x in d["threats"]}
    for t in d["threats"]:
        tid = t.get("id", "?")
        if not t.get("owner"): errors.append(f"{tid}: missing owner")
        if not t.get("scenario"): errors.append(f"{tid}: missing scenario")
        if not t.get("mitigation_ids") and t.get("status") != "accepted":
            errors.append(f"{tid}: no mitigation or documented acceptance")
        for c in t.get("mitigation_ids", []):
            if c not in controls: errors.append(f"{tid}: unknown control {c}")
        for e in t.get("element_ids", []):
            if e not in elems: errors.append(f"{tid}: unknown element {e}")
    for c in d["controls"]:
        cid = c.get("id", "?")
        if not c.get("owner"): errors.append(f"{cid}: missing owner")
        if not c.get("test_id") or c.get("test_id") not in tests:
            errors.append(f"{cid}: missing/unknown test_id")
        if not c.get("evidence_path"): errors.append(f"{cid}: missing evidence_path")
    for t in d["tests"]:
        if t.get("threat_id") not in threats: errors.append(f"{t.get('id')}: unknown threat")
        if not t.get("method") or not t.get("expected"): errors.append(f"{t.get('id')}: method/expected required")
    for f in d["flows"]:
        if f.get("from") not in elems or f.get("to") not in elems:
            errors.append(f"{f.get('id')}: unknown flow endpoint")
    return errors

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python validate_model.py model.json")
    try:
        model = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"cannot read valid JSON: {exc}")
    problems = validate(model)
    if problems:
        print("INVALID")
        print("\n".join("- " + p for p in problems))
        raise SystemExit(1)
    print("STRUCTURALLY VALID (not a security assurance)")
```

The validator deliberately consumes normalized JSON fixtures using only
the standard library. It does not parse the YAML example. This is a
teaching implementation and does not prove model completeness.

Create `tests/valid-model.json`:

``` json
{
  "schema_version":"1.0",
  "model":{"id":"TM-TEST","title":"Synthetic model","owner":"Learner","last_reviewed":"2026-10-29","review_due":"2027-01-29","scope":{"included":["synthetic API"]},"assumptions":[{"id":"A01","statement":"Synthetic data only"}]},
  "elements":[{"id":"E01","name":"API","type":"process"}],
  "flows":[{"id":"F01","from":"E01","to":"E01","data":"synthetic request"}],
  "controls":[{"id":"C01","name":"Bounded input","owner":"API owner","test_id":"TEST-01","evidence_path":"evidence/test.txt","mitigates":["T01"]}],
  "tests":[{"id":"TEST-01","threat_id":"T01","method":"Send oversized synthetic input","expected":"Request rejected"}],
  "threats":[{"id":"T01","scenario":"Oversized request exhausts service","owner":"API owner","element_ids":["E01"],"mitigation_ids":["C01"],"status":"mitigating"}]
}
```

Create `tests/invalid-model.json` as a copy but remove T01's `owner` and
set `mitigation_ids` to `[]`. Create `tests/test_validator.py`:

``` python
import json, unittest
from pathlib import Path
from validate_model import validate

ROOT = Path(__file__).resolve().parents[1]
def load(name):
    return json.loads((ROOT / "tests" / name).read_text(encoding="utf-8"))

class Tests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(validate(load("valid-model.json")), [])
    def test_invalid_owner_and_mitigation(self):
        errors = validate(load("invalid-model.json"))
        self.assertTrue(any("missing owner" in e for e in errors))
        self.assertTrue(any("no mitigation" in e for e in errors))
    def test_unknown_endpoint(self):
        d = load("valid-model.json")
        d["flows"][0]["to"] = "E-NOPE"
        self.assertTrue(any("unknown flow endpoint" in e for e in validate(d)))

if __name__ == "__main__":
    unittest.main()
```

Create `traceability.py`:

``` python
import json, sys
from pathlib import Path

def generate(d):
    controls = {c["id"]: c for c in d["controls"]}
    tests = {t["id"]: t for t in d["tests"]}
    rows = [
        "| Threat | Control | Test | Owner | Evidence | Monitoring |",
        "|---|---|---|---|---|---|"
    ]
    for threat in sorted(d["threats"], key=lambda x: x["id"]):
        for cid in threat.get("mitigation_ids", []):
            c = controls.get(cid)
            if c is None:
                raise ValueError(f"{threat['id']}: unknown control {cid}")
            test = tests.get(c.get("test_id"))
            if test is None:
                raise ValueError(f"{cid}: missing test {c.get('test_id')}")
            rows.append(f"| {threat['id']} | {cid} — {c['name']} | {test['id']} — {test['method']} | {c['owner']} | {c['evidence_path']} | {c.get('monitoring', 'NOT DEFINED')} |")
    return "\n".join(rows) + "\n"

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: python traceability.py model.json output.md")
    d = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    Path(sys.argv[2]).write_text(generate(d), encoding="utf-8")
    print("wrote", sys.argv[2])
```

Create `tests/test_traceability.py`:

``` python
import json, unittest
from pathlib import Path
from traceability import generate
ROOT = Path(__file__).resolve().parents[1]

class TraceabilityTests(unittest.TestCase):
    def test_links(self):
        d = json.loads((ROOT / "tests/valid-model.json").read_text(encoding="utf-8"))
        out = generate(d)
        for value in ("T01", "C01", "TEST-01", "API owner", "evidence/test.txt"):
            self.assertIn(value, out)
    def test_unknown_control_fails_closed(self):
        d = json.loads((ROOT / "tests/valid-model.json").read_text(encoding="utf-8"))
        d["threats"][0]["mitigation_ids"] = ["C-NOT-FOUND"]
        with self.assertRaises(ValueError): generate(d)

if __name__ == "__main__":
    unittest.main()
```

Run from the lab workspace:

``` bash
python --version
python validate_model.py tests/valid-model.json
python validate_model.py tests/invalid-model.json
python -m unittest discover -s tests -v
python traceability.py tests/valid-model.json evidence/traceability.md
```

Illustrative output, not executed during authoring:

``` text
STRUCTURALLY VALID (not a security assurance)
INVALID
- T01: missing owner
- T01: no mitigation or documented acceptance
```

The invalid fixture should exit non-zero. A passing structural test does
not show that the architecture is complete or that controls work. The
model IDs must match across threats, controls, tests, risk register, and
generated output.

### Flawed model exercise

``` yaml
model:
  title: "ML service"
  owner: "Team"
  review_due: "never"
threats:
  - id: T-1
    scenario: "Data might leak"
    likelihood: medium
    impact: medium
    mitigation: "Use security"
  - id: T-2
    scenario: "CI could be compromised"
    likelihood: medium
    impact: medium
    mitigation: "Trust CI"
```

Find eight defects. **Answer key:** no schema/model ID; no
scope/DFD/assumptions; "Team" is not accountable; review date never
expires; vague threat scenario; no actors/preconditions/assets/flows;
unsupported ratings; non-actionable controls; no control
type/test/evidence; no residual risk/acceptance; CI architecture absent;
no stable references; no ML-specific import/data/notebook threats.

### Metrics and program operations

  ------------------------------------------------------------------------------
  Metric             Definition                               Gaming risk /
                                                              caveat
  ------------------ ---------------------------------------- ------------------
  High-risk threats  High/critical threats with current       Test quality may
  with tested        passing negative test ÷ all              be weak
  controls           high/critical threats                    

  Model freshness    Models reviewed within interval ÷ active Date-only review
                     models                                   is not meaningful

  Overdue review     Models past review date ÷ models in      Do not extend
  rate               scope                                    dates without
                                                              review

  Residual high-risk Open/accepted high risks at a point in   Examine age,
  count              time                                     owners, and scope

  Time to mitigate   Elapsed time from confirmed issue to     Report aged tail
                     verified closure                         and reopened
                                                              issues

  Traceability       High-priority threats linked to          Link presence is
  completeness       control/test/owner/evidence/monitoring ÷ not quality
                     high-priority threats                    

  Design-origin      Findings found during design ÷ all       More can mean
  findings           categorized findings                     better early
                                                              detection

  Evidence freshness Required tests with current evidence ÷   Green status can
                     required tests                           mask wrong-path
                                                              tests
  ------------------------------------------------------------------------------

Ownership: service owner owns context/remediation; security champion
facilitates; platform/security reviewer challenges assumptions;
authorized risk approver accepts residual risk; incident/postmortem
owner ensures lessons are reflected. Review on a cadence and when
dependencies, models, data classes, identities, trust boundaries,
deployment paths, or incidents change. Exceptions need rationale,
compensating controls, approver, expiry, and revalidation. Do not reward
shrinking scope or downgrading severity.

### Failure scenarios

  --------------------------------------------------------------------------------
  Symptom      Hypothesis      Test                Root cause      Correction /
                                                                   prevention
  ------------ --------------- ------------------- --------------- ---------------
  Notebook     Change trigger  Compare inventory   Model treated   Add notebook
  platform     missing         to DFD/identity     as static       flows; require
  absent from                  list                                review on new
  model                                                            execution
                                                                   surfaces

  Every threat Rating anchors  Re-rate sample      No calibration  Define anchors,
  is medium    vague           against explicit                    rationale,
                               criteria                            escalation

  CI omitted   Model starts at Trace               Incomplete      Add runner,
               registry        source-to-runtime   scope           inputs, tokens,
                                                                   registry

  Risk         No owner/expiry Audit risk register No formal       Require
  accepted                                         workflow        approver and
  verbally                                                         expiry in
                                                                   validation

  Public       Source          Inspect intake and  Unsafe          Reject
  pickle       popularity      reject fixture      serialization   untrusted
  loaded in    mistaken for                        and missing     pickle, isolate
  production   trust                               provenance      intake, verify
                                                                   origin

  Controls     Documentation   Run approved        No evidence     Add
  never tested treated as      negative test       owner/cadence   traceability,
               enforcement                                         tests,
                                                                   monitoring
  --------------------------------------------------------------------------------

Models are incomplete, assumption-dependent, and can become stale.
Structural validation cannot prove semantic completeness. A passing
negative test only proves the tested path behaved as expected under that
configuration.

## 1.7 SRE lens

Track SLIs with defined denominators: high-risk threats with tested
controls / all high-risk threats; models reviewed on time / all active
models; high-priority threats with complete traceability / all
high-priority threats; elapsed time to verified mitigation; residual
high-risk count by age/owner; and material changes with a linked review
/ all identified material changes. Metrics can be gamed by shrinking
scope, lowering severity, marking untested controls implemented, or
updating dates without review; sample underlying evidence.

  -----------------------------------------------------------------------
  Failure                 Blast radius            Recovery
  ----------------------- ----------------------- -----------------------
  Stale model             New data path/identity  Compare model to
                          not assessed            deployed inventory;
                                                  reopen review

  Missing review process  Changes bypass analysis Audit material changes
                                                  and incident follow-up

  Broken validator        Invalid model passes or Test validator with
                          valid model fails       known fixtures; review
                                                  schema

  Evidence pipeline       Control claims cannot   Mark evidence
  unavailable             be substantiated        unknown/stale, preserve
                                                  last known record

  Evidence                False assurance         Protect source, compare
  forged/incomplete                               independent telemetry

  Incomplete inventory    Metrics look healthy    Independent
                          while assets are        architecture and
                          omitted                 identity review
  -----------------------------------------------------------------------

Fail-closed policy should be risk-based: a high-risk release should not
claim assurance if required evidence is absent, while a low-risk
documentation issue need not block every development change. A missing
model is not proof of an insecure system, but it is a loss of assurance.

**Runbook --- critical attack path:** Trigger on a newly plausible path
to sensitive data or unauthorized artifact promotion. (1) Triage
affected assets, identities, release path, and evidence. (2) Contain by
restricting a role, pausing promotion, quarantining a digest, disabling
risky import, or isolating a workload. (3) Validate only in the owned
lab or through approved defensive checks. (4) Assign owner/due date and
test mitigation. (5) Update model/residual risk and M10 postmortem
actions. (6) Add relevant telemetry through M11. Preserve evidence; do
not place secrets in tickets.

**Cost/capacity:** core labs need only text and Python. If using
Linux/WSL2, measure rather than assume:

``` bash
du -sh .
free -h
df -h .
ps -eo pid,comm,%cpu,%mem --sort=-%mem | head
```

WSL2 and native Linux resource reporting differ. At scale, cost is
reviewer time, test maintenance, evidence retention, integration, and
exception handling; optimize for risk reduction and maintainability.

## 1.8 Security lens

  ---------------------------------------------------------------------------------------------------------------------------
  Threat          Preventive                 Detective              Corrective           Negative test /    Residual risk /
                                                                                         evidence           owner
  --------------- -------------------------- ---------------------- -------------------- ------------------ -----------------
  Stale/omitted   Change-triggered review    Compare model with     Update model and     Add synthetic      Unknown services;
  architecture                               manifests/identities   reassess             component; verify  service owner
                                                                                         review is required 

  Control exists  Enforced policy/config     Periodic negative      Fix drift            Submit disallowed  Break-glass
  only in docs                               tests and audit                             manifest; retain   bypass; cluster
                                                                                         denial             owner

  Syntax-only     Schema/reference checks    Test validator and     Repair               Remove             Semantic gaps;
  validator       plus review                fixtures               model/validator      owner/reference;   model maintainer
                                                                                         expect failure     

  Unowned risk    Required                   Acceptance audit       Escalate or revoke   Acceptance without Poor approval
  acceptance      owner/approver/expiry                                                  expiry fails       context; risk
                                                                                         review             owner

  Incomplete      Asset checklist            Compare service/data   Add missing elements Inventory diff     Discovery gaps;
  inventory                                  inventory                                                      platform owner

  Scanner misses  Separate model intake      Intake/provenance      Quarantine/replace   Submit untrusted   Parser/behavior
  model file      policy                     audit                                       fixture            risks; ML owner

  Compromised     Isolation, scoped          Identity and           Revoke identity,     Unauthorized       Trusted
  CI/signing      identity, policy           verification audit     quarantine, rebuild  signer fixture     control-plane
  trust                                                                                  rejected           compromise

  Missing data    Model identity and data    Access audit/grant     Revoke excessive     Cross-scope read   Privileged admin
  boundary        flow                       review                 grants               denied             access

  Sensitive logs  Minimize/redact/restrict   Synthetic marker       Restrict, rotate     Marker             Unrecognized data
                                             checks                 exposed credentials  absent/redacted    formats
  ---------------------------------------------------------------------------------------------------------------------------

Frameworks are completeness aids, not substitutes for reasoning: verify
current matrix/list names and versions for MITRE ATT&CK
Containers/Cloud, Microsoft Kubernetes threat matrix, CIS Kubernetes
Benchmark (including kind applicability), OWASP lists, CNCF Cloud Native
Security Whitepaper, SLSA, MITRE ATLAS, and LINDDUN. NIST SP 800-190 is
an application container security guide. Do not claim regulatory
compliance.

## 1.9 Production checklist

-   [ ] Scope, exclusions, assumptions, owner, review date, and DFD are
    recorded.
-   [ ] Developer, Git, CI, dependencies/base image, artifact, registry,
    GitOps, API server, nodes, pods, inference, ETL, object store,
    feature store, identity/secrets, notebooks, and observability are
    included.
-   [ ] Flows have direction, data class, identity, and trust
    boundaries.
-   [ ] Assets/actors and CIA/privacy properties are documented.
-   [ ] STRIDE coverage has rationale; risk definitions and uncertainty
    are explicit.
-   [ ] Threats include scenario, preconditions, impact, owner, status,
    controls, and evidence.
-   [ ] Source/build/input/artifact/registry/deploy/runtime threats are
    covered.
-   [ ] ML/data threats include poisoning, backdoors, unsafe pickle,
    privacy/model theft, notebooks, feature store, model hubs, and
    relevant LLM/GPU awareness.
-   [ ] Controls map to prevention, detection, correction, and negative
    tests.
-   [ ] Risk acceptance has rationale, owner, approver, compensating
    controls, expiry, and review trigger.
-   [ ] High-risk threats link to test, expected evidence, monitoring,
    and owner.
-   [ ] Validator and traceability tests include positive and negative
    fixtures.
-   [ ] No credentials, private keys, real sensitive data, or
    third-party model files are committed.
-   [ ] Incidents/near misses trigger model review.

## 1.10 Hands-on lab set

  --------------------------------------------------------------------------------------------------------------------------------
  Lab ID   Goal           Steps                     Expected evidence                    Cleanup            Stretch
  -------- -------------- ------------------------- ------------------------------------ ------------------ ----------------------
  LAB-01   DFD            Create                    Diagram and review notes             Remove disposable  Separate
                          `models/first-dfd.mmd`;                                        workspace only     supply-chain/data
                          label flows/boundaries                                         after path check   views

  LAB-02   Threat         Use T01--T16; rate        Model and risk register with 8+      Retain synthetic   Add threat and defend
           register       likelihood/impact; assign entries                              evidence or remove rating
                          owners/tests                                                   workspace          

  LAB-03   Validator      Create JSON               Valid fixture passes; invalid        Remove generated   Add
                          fixtures/script/tests;    fixture fails                        outputs after      unique-ID/acceptance
                          run commands                                                   review             checks

  LAB-04   Traceability   Generate matrix and run   Matrix links                         Remove output if   Fail closed on every
                          tests                     threat/control/test/owner/evidence   not retained       unresolved link

  LAB-05   Model intake   Review policy and reject  Intake decision/test record          Delete disposable  Add provenance/format
                          untrusted fixture before                                       marker/workspace   allowlist
                          serving                                                                           
  --------------------------------------------------------------------------------------------------------------------------------

All labs are idempotent with fresh fixtures, text/Python only,
negligible footprint, and no internet requirement. Offline fallback is
the included synthetic content. WSL2/native Linux both support core
labs; no cluster or kernel instrumentation is required. If performing a
marker demonstration, use a disposable isolated directory without
credentials/network/sensitive files. **Defensive-only:** test only your
own local fixtures.

## 1.11 Self-check questions

1.  **Why model before selecting tools?** To prioritize controls against
    real paths; scanner output is incomplete/contextual.
2.  **Vulnerability vs threat vs risk?** Weakness vs harmful scenario vs
    contextual likelihood/impact judgment.
3.  **Does a signature prove safety?** No; it verifies a claim about a
    digest under a trust configuration.
4.  **Why include CI/GitOps?** They turn source/artifacts into running
    workloads and hold powerful identities.
5.  **Is "medium" a probability?** No; it is qualitative and needs
    explicit criteria.
6.  **What does acceptance require?** Rationale, residual risk,
    compensating controls, owner, approver, expiry, review trigger.
7.  **What does an SBOM prove?** Component inventory within its
    coverage, not safety.
8.  **Why is pickle unsafe for untrusted files?** Deserialization can
    invoke behavior in the loader process.
9.  **What does a passing validator prove?** Only that tested structural
    rules passed for that fixture.
10. **How handle unknown likelihood?** Record uncertainty and
    investigate; do not silently rate it low.

Wrong answers are tempting because tool presence, signature, categories,
and green tests look like stronger assurance than they actually provide.

## 1.12 Evidence artifacts

Save `models/first-dfd.mmd`, `models/threat-model.yaml`, a risk register
with at least eight entries, risk-acceptance template,
`validate_model.py`, `tests/valid-model.json`,
`tests/invalid-model.json`, `tests/test_validator.py`,
`traceability.py`, `tests/test_traceability.py`, generated
`evidence/traceability.md`, validator/test output labelled as actual or
illustrative, flawed-model review, model-intake review, completed
checklist, and assumptions/residual-risk notes. Include Python version
and rerun/cleanup instructions. Never commit credentials, private keys,
real third-party model files, or sensitive logs.

## 1.13 Common interview and design-review questions

1.  **How prioritize scanner findings?** Use reachability, exploit
    preconditions, asset sensitivity, privilege, attack-path leverage,
    controls, and uncertainty; scanner severity is one input.
2.  **SBOM vs scan vs signature vs provenance?** Inventory vs
    known-issue lookup vs signer/digest claim vs build claims; none
    alone proves safety.
3.  **How threat-model model import?** Include origin, format, loader
    privileges, data/model lineage, serving identity, and intake
    evidence; reject untrusted pickle and isolate validation.
4.  **What makes a production-grade model?** Scope, assumptions,
    prioritized threats, owners, tests/evidence, residual risk/expiry,
    review triggers, and reconciliation with deployed architecture.
5.  **How validate admission safely?** Disposable environment, valid and
    violating fixtures, audit/warn first, expected event and denial,
    bypass review, staged enforcement/rollback.

## 1.14 Sources and verification notes

Consult primary sources: Threat Modeling Manifesto; Adam Shostack,
*Threat Modeling: Designing for Security*; MITRE ATT&CK for
Containers/Cloud; Microsoft Kubernetes threat matrix; CIS Kubernetes
Benchmark; NIST SP 800-190; OWASP Top 10, Kubernetes Top Ten, CI/CD
Security Risks, and Top 10 for LLM Applications; CNCF Cloud Native
Security Whitepaper; SLSA specification/threat model; MITRE ATLAS;
LINDDUN; Python docs for `pickle`, `json`, `unittest`, and `pathlib`;
official safetensors/ONNX documentation. Exact current names, versions,
sections, and status are `[VERIFY]` unless checked directly.

-   **General concepts used:** CIA, STRIDE category names, DFD
    elements/flows/boundaries, qualitative risk reasoning, and the
    distinction between scan/SBOM/signature/provenance/admission/runtime
    detection.
-   **\[VERIFY\]:** exact attribution of four questions; current DREAD
    status; SLSA A--I categories; current
    MITRE/Microsoft/OWASP/CNCF/ATLAS/LINDDUN names and versions; kind
    benchmark applicability; optional tool syntax/maintenance;
    model-format claims.
-   **Code execution:** scripts and tests were not executed during
    authoring; expected outputs are illustrative. Run all examples in a
    disposable environment before relying on them.
-   **No compliance claim:** this lesson is not legal advice and does
    not establish SOC 2, ISO 27001, PCI, HIPAA, FedRAMP, or other
    compliance.

## Author's Verification and Completeness Audit

  -----------------------------------------------------------------------
  Requirement             Status                  Evidence / limitation
  ----------------------- ----------------------- -----------------------
  Required Unit 1 title   PASS                    Top of document
  and metadata                                    

  Production rationale    PASS                    §§1.0--1.1
  and L1--L4 objectives                           

  Glossary, four          VERIFY                  §1.2; attribution and
  questions, CIA/privacy,                         current references need
  control diagram                                 verification

  Beginner concepts and   PASS                    §1.3
  guided DFD lab                                  

  Required platform       PASS                    §1.4
  elements, flows, STRIDE                         
  threats                                         

  Qualitative risk, DREAD VERIFY                  §1.4; DREAD current
  caution, control                                status not
  mapping                                         independently verified

  Risk acceptance and     PASS                    §1.4
  structured YAML                                 
  artifact                                        

  Two attack trees        PASS                    §1.4

  Pattern/anti-pattern,   PASS                    §§1.4, 1.6
  positive/negative                               
  validation                                      

  Supply-chain and        PASS                    §§1.4--1.5
  ML/data-specific                                
  threats                                         

  SLSA A--I not           VERIFY                  §1.5; omitted until
  fabricated                                      authoritative
                                                  verification

  Expert validator,       PASS                    §1.6; code not executed
  traceability generator,                         
  tests                                           

  Program metrics,        PASS                    §1.6
  ownership, failure                              
  scenarios                                       

  SRE lens, runbook, cost PASS                    §1.7
  notes                                           

  Security lens and       PASS                    §1.8
  bypasses                                        

  Checklist, 3--5 labs,   PASS                    §§1.9--1.13
  questions, evidence,                            
  interviews                                      

  Sources and             VERIFY                  §1.14
  verification notes                              

  Actual code/test        GAP                     Not executed during
  execution                                       authoring; run commands
                                                  and retain evidence

  Repository mutation     PASS for this chat      This is a standalone
                                                  artifact; no repository
                                                  files were modified by
                                                  this chat
  -----------------------------------------------------------------------

**Remaining verification:** check exact attribution of the four
questions; current SLSA category labels; current framework
names/versions; DREAD source status; model-format recommendations and
optional tool details. The YAML example should be parsed by a verified
YAML parser before operational use. The validator consumes JSON fixtures
by design and does not prove semantic completeness. No other repository
file was modified by this chat.
