## Unit 6 — Workload identity and credential rotation (security architecture view)

**Target file:** `06-workload-identity-and-credential-rotation.md` | **Estimated time:** 18–26 hours | **Prerequisites:** M01–M11, especially M03 RBAC/ServiceAccounts, M04 NetworkPolicy/TLS, M06 operator/chart review, M08 GitOps/drift, M09 identity/secrets/rotation mechanisms, M10 incident response, M11 observability, and M12 Units 4–5  
**Core tools:** Python 3 standard library, `kubectl`, `kind`, Git, local JSON/YAML fixtures, shell utilities | **Awareness:** Vault audit, cloud workload identity and metadata protections, rbac-tool/kubectl-who-can/KubiScan classes, audit2rbac-like analysis, Kyverno/OPA, Falco, SPIFFE/SPIRE, Prometheus/Grafana/Loki/Alertmanager  
**Last reviewed:** 2026-10-29 | **Tool/spec baseline assumed:** Kubernetes ServiceAccount, RBAC, audit, admission, and NetworkPolicy concepts; exact Kubernetes/kind/CNI versions must be recorded from the learner’s environment `[VERIFY]`. Provider-specific identity claim names and metadata behavior are not universal.  
**Footprint:** one small `kind` cluster at a time, synthetic fixtures, and a small data/ML workload. Keep approximately 30 GB free before pulling images; actual use varies. Tear down clusters between live labs.  
**Needs internet at lab time:** internet may be needed to install `kind`/`kubectl` and pull node images. Labs have offline fixture paths after setup. No paid platform, cloud account, production Vault, or live cloud metadata service is required.

> **Safety boundary:** use only a disposable local cluster and synthetic identities. Never print, store, commit, or paste a real bearer token. The compromised-token drill uses synthetic audit events and fake Secret markers unless a separately isolated local token is intentionally created and its authority is verified to be limited to the disposable cluster. Do not target third-party systems or real metadata endpoints.

### 6.0 Why this matters in production

Identity is a security boundary, not just a way to connect services. A workload may be reachable only from a private network and still be dangerous if its ServiceAccount can read every Secret, its cloud identity can access production object storage, or a shared credential appears in a notebook, CI log, or image layer. Network location helps, but identity, authorization, and audit determine which principal may perform which action and provide evidence when it does.

For data and ML platforms, identity misuse can cross boundaries: a model-serving Pod may read database credentials; a notebook may reuse a shared object-store key; an ETL controller may create privileged Pods; a CI identity may alter a release; an operator may have cluster-wide authority; or a compromised node may expose credentials available to Pods scheduled there. Each path depends on actual permissions, credential type, token audience/lifetime, namespace, admission controls, CNI behavior, and resource scope.

This unit treats workload identity and credential rotation as **security controls to audit, test, and operate**. M09 owns implementation mechanisms for secret backends, federation, token issuance, and rotation workflows. Here the learner inventories identities, identifies risky grants, traces attack paths, tests policy previews, measures rotation readiness, detects abuse, and rehearses containment.

A short-lived credential limits the time in which it may be replayed; it does not prevent compromised code from using it while valid. Rotation also fails as a control if consumers do not reload credentials, old credentials remain accepted, the new credential is not verified, or emergency revocation has never been rehearsed.

### 6.1 Learning objectives

1. **[L1]** Explain why identity, authorization, and audit—not network location alone—form a primary cloud-native security perimeter.
2. **[L1]** Inventory human, CI, Kubernetes, service-to-service, workload-to-cloud, controller/operator, and node/kubelet identities; classify static, short-lived, dynamic, and federated credentials.
3. **[L2]** Run the audit tool against Kubernetes JSON snapshots or normalized fixtures and detect high-risk RBAC, ServiceAccount, token, subject, and environment-reuse patterns.
4. **[L2]** Explain prerequisites for `kubectl auth can-i --list --as=...`, distinguishing a local fixture from an API-server authorization decision.
5. **[L2]** Build/test an identity graph that finds the shortest path from a compromised Pod to a fake sensitive Secret/data store and recommends cut edges.
6. **[L2]** Apply identity hygiene: dedicated ServiceAccounts, disabled token automount where not required, scoped RBAC, no unnecessary long-lived token Secrets, and environment separation.
7. **[L3]** Complete a defended architecture review covering principals, issuer/subject/audience trust, blast radius, credential storage, rotation, audit, monitoring, break-glass, ownership, exceptions, and residual risk.
8. **[L3]** Test admission-policy previews and trust-policy linting with positive/negative fixtures without duplicating full policy authoring in Units 8 and 11.
9. **[L3]** Demonstrate time-bound JIT access records with idempotent expiry cleanup and audit evidence without assuming RoleBindings have built-in TTL.
10. **[L3]** Design risk-based rotation for registry credentials, signing keys, database credentials, TLS certificates, CI trust, and relevant KMS/data keys; measure time-to-rotate.
11. **[L4]** Produce posture reports, access-review recommendations, and synthetic identity-abuse detections; reason about precision, recall, and missing telemetry.
12. **[L4]** Respond to compromised ServiceAccount, CI, human, or controller identity using containment, scoping, revocation/rotation, recovery, verification, and postmortem steps.

### 6.2 Concept map and vocabulary

#### Identity types and credential classes

| Identity | Example | Security question |
|---|---|---|
| Human | Engineer using Kubernetes/Vault | Is access attributable, reviewed, and time-bound where possible? |
| CI | Release workflow identity | Can an untrusted branch request it or publish/deploy with it? |
| Kubernetes ServiceAccount | `serving/ml-api` | What Kubernetes API actions can its Pods perform? |
| Workload-to-service | Pod identity for object store/database | Which external resource, audience, and scope are authorized? |
| Service-to-service | mTLS/SPIFFE-style identity | Is the peer authenticated and authorized for this operation? |
| Controller/operator | Operator ServiceAccount | Can it create Pods, read Secrets, or modify RBAC outside its purpose? |
| Node/kubelet | Node API identity | What is exposed if the node is compromised? |
| Break-glass | Emergency operator identity | Is use rare, time-limited, attributable, and audited? |

- **Static long-lived:** fixed API key/password/indefinite token. Requires secure storage, inventory, rotation, and leak response.
- **Short-lived:** credential with bounded expiry. Reduces replay window but does not prevent misuse while valid.
- **Dynamic:** credential created for a consumer/session, often with lease/revocation. Mechanisms are M09.
- **Federated:** one identity system accepts a constrained assertion from another. Issuer, subject, audience, trust policy, and target authorization must align; claim names are provider-specific `[VERIFY]`.

| Term | Definition |
|---|---|
| Principal | Entity requesting an action: user, ServiceAccount, CI job, workload. |
| Subject / issuer / audience | Identity represented by a credential / system issuing assertion / intended recipient of token. Exact semantics depend on provider. |
| ServiceAccount | Kubernetes API object representing workload identity. |
| Role / ClusterRole | RBAC permissions scoped to a namespace / cluster-wide or reusable. |
| RoleBinding / ClusterRoleBinding | Associates subjects with a role. A RoleBinding referencing a ClusterRole still grants only in its namespace. |
| Projected token | Token provided through a projected volume, often with expiry/audience; verify version behavior `[VERIFY]`. |
| RBAC / IAM | Kubernetes role-based authorization / external Identity and Access Management. |
| Workload identity / federation | Identity for running application/job / trust across identity systems. |
| Rotation / revocation | Replace credential and retire old material / make credential or trust path no longer accepted. Effect varies by token/verifier. |
| Identity graph / attack path | Graph of principals, bindings, permissions, secrets, and trust / sequence of relationships to a protected asset. |
| Confused deputy / SSRF | Privileged service induced to use its authority for an untrusted caller / attacker-influenced server request to unintended internal endpoint. |
| Honeytoken | Synthetic credential/resource whose unexpected use should alert. |
| Break-glass / JIT | Exceptional emergency access / access granted for a bounded time and reason. |
| Rotation readiness / blast radius | Ability to replace, reload, verify, retire, and recover / systems/data affected by compromised identity. |

#### Identity/data-flow diagram

```text
[Pod: ml-api] --runs as--> [ServiceAccount: serving/ml-api]
                                  |
                                  v
                         [RoleBinding in serving]
                                  |
                                  v
                         [Role: read-config]
                                  |
                                  v
                    [ConfigMap: serving/runtime-config]

Dangerous path to prevent:
[Compromised Pod] -> [shared/broad SA] -> [wildcard or secrets-read grant]
                  -> [production DB credential] -> [database/data exposure]
```

Trust boundaries include the Pod process, token mount, API server authentication/authorization, external federation, target-resource IAM, controller/operator actions, consumer reload, and audit collection. A private network is not an identity control.

#### Attack-path patterns and caveats

- **Stolen ServiceAccount token → API:** depends on token acceptance, audience/expiry, and actual authorization.
- **Broad RBAC:** wildcard or broad Secret reads can widen impact; actual consequences depend on bindings, namespaces, resources, and admission.
- **`create pods` / `pods/exec`:** may enable running/interacting with code in a chosen context; escalation is not automatic.
- **`serviceaccounts/token`:** can allow requesting tokens subject to API and policy behavior; audit caller, target SA, audience, and use.
- **`impersonate`, `bind`, `escalate`:** high-risk verbs whose effect depends on resource and authorization checks.
- **SSRF → metadata:** an application fetching user-controlled URLs may reach internal endpoints if network and metadata protections permit. No real metadata endpoint is called in this unit.
- **Confused deputy/shared identity:** a controller or shared dev/prod identity can expand blast radius and reduce audit attribution.
- **Node compromise:** may expose data/credentials available to workloads on that node; node controls reduce but do not eliminate risk.

### 6.3 Level 1 — Beginner

#### Identity is a perimeter

A private IP does not answer who is making a request. A workload can be compromised inside a trusted subnet. Ask: which principal is this, who issued the identity, which audience is intended, what operation is authorized, what is the smallest scope, and where is the action audited?

For example, `serving/ml-api` may need to read one ConfigMap but not Kubernetes Secrets. If its Pod does not call the Kubernetes API at runtime, it generally should not receive a mounted API token. If it does need the API, use a dedicated ServiceAccount and narrow permissions.

#### Identity inventory starter

| Field | Synthetic example | Why it matters |
|---|---|---|
| Identity ID | `k8s:serving/ml-api` | Stable inventory key |
| Type/owner | ServiceAccount / `model-platform` | Control and remediation |
| Environment | `dev` | Detects dev/prod reuse |
| Consumers | `ml-api` Deployment | Reveals scope |
| Credential type | Projected SA token | Lifecycle/expiry behavior |
| Permissions | `get configmaps` in `serving` | Actual authority |
| External trust | None | Avoids assumed cloud access |
| Rotation/revocation | Token lifecycle and consumer restart if required | Operational readiness |
| Audit source | Kubernetes API audit | Detects use |
| Review date | ISO date | Age and review cadence |

#### Illustrative manifest

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ml-api
  namespace: serving
automountServiceAccountToken: false
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-api
  namespace: serving
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ml-api
  template:
    metadata:
      labels:
        app: ml-api
    spec:
      serviceAccountName: ml-api
      automountServiceAccountToken: false
      containers:
        - name: api
          image: python:3.12-slim
          command: ["python", "-c", "import time; time.sleep(3600)"]
          securityContext:
            allowPrivilegeEscalation: false
            runAsNonRoot: true
            runAsUser: 10001
            capabilities:
              drop: ["ALL"]
```

This is a learning manifest, not a production image. Pin a reviewed image digest in a real release. If the app needs the API, do not blindly disable its token and break service; document the API calls and test the required projected-token/audience behavior `[VERIFY]`.

**What happened?** A token mount can grant a process access to the API as its ServiceAccount. Disabling automount is useful only if the app does not need that identity. Common mistakes: assuming private IP means trusted; assuming short-lived means safe; treating missing activity as proof an identity is stale; assuming deleting an SA instantly revokes every token.

**Positive test:** audit fixture reports no unnecessary token mount when automount is false.  
**Negative test:** set automount true and training metadata says API access is not required; the audit must flag it.

### 6.4 Level 2 — Intermediate

#### Safe audit procedure

Record actual environment:

```bash
date -u
kubectl version --client
kubectl config current-context
kubectl get nodes -o wide
kind version   # optional
python3 --version
```

Check that the current context is disposable before applying/deleting resources. Collect separate snapshots only if authorized:

```bash
kubectl get serviceaccounts -A -o json > serviceaccounts.json
kubectl get pods -A -o json > pods.json
kubectl get roles -A -o json > roles.json
kubectl get rolebindings -A -o json > rolebindings.json
kubectl get clusterroles -o json > clusterroles.json
kubectl get clusterrolebindings -o json > clusterrolebindings.json
kubectl get secrets -A -o json > secrets.json
```

These are separate JSON documents; normalize them into one `items` array before running the included audit. Do not save raw Secret snapshots: they contain secret material. If you need to detect token Secret *types*, pipe the Secret JSON through a redactor and save metadata/type only; never archive the raw response.

`normalize_snapshots.py` (accepts Kubernetes List JSON files and removes `data`/`stringData` from Secret objects before output):

```python
import json,sys
from pathlib import Path
items=[]
for filename in sys.argv[1:]:
    data=json.loads(Path(filename).read_text(encoding="utf-8"))
    if not isinstance(data,dict) or not isinstance(data.get("items"),list):
        raise SystemExit(f"DENY: {filename} is not a Kubernetes List JSON document")
    for obj in data["items"]:
        clean=dict(obj)
        if clean.get("kind")=="Secret":
            clean.pop("data",None); clean.pop("stringData",None)
        items.append(clean)
print(json.dumps({"items":items},indent=2))
```

Example: `python3 normalize_snapshots.py serviceaccounts.json pods.json roles.json rolebindings.json clusterroles.json clusterrolebindings.json secrets.json > snapshot-redacted.json`. Review the redacted output before storing it. This helper expects each input to be a JSON object with an `items` array; it does not fetch cluster data or verify snapshot completeness.

`kubectl auth can-i --list --as=system:serviceaccount:serving:ml-api -n serving` requires the caller to have impersonation authorization. A denial may mean the caller cannot impersonate, not that the target has no permissions. Fixture audit does not need cluster-admin, but is not a complete Kubernetes authorization engine.

#### Identity hygiene and rotation

- Disable `automountServiceAccountToken` when API access is unnecessary; verify Pod/SA precedence for the cluster version.
- Use dedicated ServiceAccounts; scope Role/RoleBinding and avoid wildcards.
- Review `secrets` read, `pods/exec`, `create pods`, `serviceaccounts/token`, `impersonate`, `bind`, and `escalate`.
- Avoid legacy long-lived ServiceAccount token Secrets; behavior evolved across Kubernetes versions `[VERIFY]`.
- Review operator/chart RBAC before install and upgrade.
- Separate dev/test/staging/prod identities and trust policies.
- Give every identity an owner, purpose, scope, audit source, rotation/revocation procedure, and review date.
- Use observed API usage to inform least privilege, not as proof every unobserved permission is unnecessary.

Rotation stages: inventory owner/consumers; obtain replacement; update/reload consumers; verify new credential; stop accepting old material where supported; verify old credential rejection; record timestamps, failure, rollback, and residual risk. Scheduled rotation and emergency revocation are different. Choose cadence based on impact, exposure, lifetime, consumer complexity, and revocation capability; no universal number applies. `[ASSUMPTION]` Set locally approved drill targets rather than presenting them as industry standards.

Detection signals include privileged RBAC changes, unexpected token requests, Secret reads by unusual workloads, `pods/exec` into sensitive Pods, impersonation, unexpected external identity use, honeytoken access, and attempts to reach an API/metadata endpoint that a workload should not need. Audit availability depends on control-plane configuration; use synthetic JSONL when live audit is unavailable.

### 6.5 Level 3 — Advanced

#### Architecture review checklist

For each workload, document: (1) principals; (2) issuer/subject/audience/environment trust boundaries; (3) exact permissions, wildcards, Secret reads, exec, token creation and RBAC escalation; (4) credential storage/mount/log exposure, expiry, reload, rotation and revocation; (5) blast radius; (6) monitoring and audit coverage; (7) break-glass/JIT; (8) owner/review date/failure mode/rollback; (9) policy preview/negative-test matrix; and (10) evidence, exceptions and residual risk.

**Synthetic completed review — model API:** `serving/ml-api` does not need Kubernetes API access; token automount disabled; no RoleBinding expected; a hypothetical ClusterRoleBinding granting broad Secret read to all ServiceAccounts is removed; ETL receives a separate identity scoped to its required resources. Positive test: API starts without token. Negative test: wildcard/Secret-read policy fixture is rejected. Residual risk: compromised app code can still use network access and any external credential legitimately granted.

#### Identity graph and cut edges

Model nodes such as Pod, ServiceAccount, RoleBinding, Role, permission, Secret, and asset. Edges represent configured/observed relationships, not mere co-location.

```text
pod:etl-worker -> sa:pipeline/etl-worker -> binding:all-workloads
 -> role:read-secrets -> permission:get-secrets
 -> secret:data-prod/db-credentials -> asset:production-db
```

The included graph analyzer computes shortest paths in this input graph and lists cut-edge candidates: narrow/remove a binding, split a shared identity, remove an unnecessary permission, or block access to the sensitive Secret. A candidate is not an automatic production change. Validate with owners and alternative paths; the graph is not a full Kubernetes authorization evaluator.

#### Admission/policy preview and trust-policy linting

Full production policy authoring is deferred to Units 8 and 11. Preview these rules in audit/warn mode first: non-allow-listed cluster-admin bindings; wildcard RBAC; broad Secret read; `pods/exec`; `serviceaccounts/token`; `impersonate`/`bind`/`escalate`; disallowed default SA; unnecessary automount; legacy token Secret; unauthorized ClusterRoleBinding creation; trust policies missing/wildcarding `sub` or `aud`. Use positive, negative, malformed, and allow-list fixtures before enforce mode. Provider-specific claim names are `[VERIFY]`; the fixture linter is not a parser for every cloud policy language. Integrate a provider-specific adapter into M02 CI and the policy review/admission pipeline only after fixture tests cover the exact provider claim names and expected allow/deny outcomes.

#### Metadata/SSRF, nodes, operators and ML data plane

If an app fetches user-controlled URLs, SSRF may reach internal endpoints. Use destination allow-lists, redirect controls, egress restrictions, metadata protections, and avoid broad workload credentials. AWS IMDSv2 is a provider-specific example; verify official documentation and hop-limit behavior `[VERIFY]`. Never call a real metadata endpoint in this lab.

NetworkPolicy can restrict Pod traffic only if the installed CNI enforces it. A `kind` policy object existing does not prove packet filtering. Node authorization and NodeRestriction are separate controls; verify the actual control-plane configuration `[VERIFY]`. Node controls do not neutralize a compromised host.

Review operators/charts before install: list every role/binding/subject, ask why each resource/verb is needed, identify Secret/exec/Pod/RBAC permissions and cross-namespace reach, assign an owner, and review upgrades. For ML systems prefer per-user notebook identities, short-lived scoped object-store/database credentials, separate training/registry/inference identities, no long-lived keys in notebooks/DAGs/images, and egress to approved data/model endpoints only.

#### JIT and break-glass

RoleBinding does not universally provide a built-in TTL. A teaching script can maintain an expiry ledger and reconcile expired grants, but the cleanup mechanism itself must be reliable. Production JIT should use an approved broker/controller, independently audit grant/revoke, and alert on cleanup failure. Break-glass must be separate, time-limited, attributable, monitored, tested, and never routine.

### 6.6 Level 4 — Expert

#### Continuous posture program

Every finding needs severity, identity/object, owner, age, remediation status, exception/expiry, evidence, and review date. Schedule audits, compare snapshots, export metrics, alert on new critical grants, and track whether remediation reduces risk.

| Metric | Definition and source | Caveat |
|---|---|---|
| Cluster-admin count | Non-allow-listed bindings to cluster-admin; RBAC audit | Allow-list must be narrow and reviewed |
| Wildcard grants | Roles/ClusterRoles with wildcard groups/resources/verbs | Count is not effective reachability |
| Default-SA usage | Workloads using default SA where policy requires dedicated identity / workloads in scope | Requires policy/owner context |
| Unnecessary token mounts | Enabled mounts with no declared API need / workloads in scope | “No need” must be validated |
| Static credential indicators | Static credential records / all inventory records | Never scrape secret values |
| Stale SAs/missing subjects | Inventory age + binding subjects absent from snapshot | Missing events may mean missing telemetry |
| Trust-policy pass rate | Policies passing provider-specific lint / policies in scope | Adapter coverage is version-dependent |
| Rotation readiness | Credential types with tested replacement/reload/revoke / types in scope | Documentation alone is not a drill |
| Time-to-rotate/revoke/contain | Defined start event to verified completion event | Define endpoints consistently |
| Detection precision/recall | True positives / reviewed alerts; detected true positives / known test events | Requires adjudicated labels and test coverage |
| Access review completion | Reviews completed / reviews due | Completion is not quality |
| Expired exceptions | Exceptions past expiry / active exceptions | Continuously check owner and expiry |

Do not invent universal target values. Thresholds are `[ASSUMPTION]` until owners approve them.

#### Detection and incident playbooks

Test detections for ClusterRoleBinding changes, powerful role grants, token-minting anomalies, Secret-read spikes, impersonation, `pods/exec`, unexpected workload identity use, operator actions, honeytoken access, and rotation failures. Kubernetes audit events use the `audit.k8s.io` API group, but actual fields/availability depend on configured audit policy and control plane `[VERIFY]`. Falco-style rules are concepts here; full rule authoring belongs to Unit 12.

For a compromised ServiceAccount/token: declare incident; preserve relevant audit/resource evidence; identify token type/audience/expiry/verifier; scope grants and target assets; contain workload and remove inappropriate bindings; rotate external credentials; verify denial where supported; restore from reviewed configuration; test legitimate access; add regression test and postmortem. For CI identity: freeze promotion, disable trust, scope artifacts, isolate runner, rotate affected credentials, rebuild trusted. For human identity: revoke sessions/credentials, inspect admin changes and impersonation. For operator identity: contain reconciliation, inspect generated resources/RBAC, restore reviewed manifests, rotate and verify.

**Synthetic incident analyses (not real incidents):** (1) CI SA had cluster-wide Secret read and a compromised Pod read DB credentials; remove grant, rotate DB credential, test cross-namespace denial. (2) every Pod auto-mounted a broad token; disable where unnecessary and test API-required workload. (3) operator had cluster-admin; narrow RBAC and test chart upgrades. (4) break-glass used routinely and unaudited; separate routine access and alert on every emergency use. (5) rotation runbook untested; run four-type drill and measure time. (6) many unused bindings; staged owner-reviewed removal with rollback. (7) notebooks shared one long-lived cloud key; revoke, split identities, and test cross-user isolation. For each record residual risk and regression test.

Multi-tenant governance requires per-team/environment identities, central minimum policy, clear exception boundaries, Git-reviewed RBAC/trust policy, drift detection, owner/expiry metadata, and a controlled emergency policy rollback. Identity controls cannot stop code from using its legitimate permissions; combine with egress restrictions, runtime detection, admission, and workload hardening.

#### 6.6.6 Cross-module handoff

> M09 owns the mechanisms: secrets backends, dynamic secrets, workload identity federation (issuer/JWKS/claims/audience), trust-policy design, rotation engineering, and the leak-response runbook. This unit does **not** re-teach those. It treats workload identity and credential rotation **as security controls in the platform's threat model**: attack paths through identities, detection of abuse, enforcement through admission/policy, rotation as incident response, and security audits of identity configurations.

| Module | Reused knowledge | What Unit 6 adds | What remains deferred |
|---|---|---|---|
| M03 | RBAC, ServiceAccounts, Pod Security Standards | Audits authorization risk and attack paths | RBAC fundamentals |
| M04 | NetworkPolicy, mTLS, TLS certificates | Restricts identity exposure and measures certificate rotation | Network/TLS fundamentals |
| M06 Unit 8 | Operator/chart RBAC review | Least-privilege recommendations and upgrade review | Full packaging workflow |
| M08 Unit 6 | Identity-as-code and drift | Posture evidence, owners, exception expiry | GitOps implementation |
| M09 Unit 1 | Credential inventory/classes | Risk and owner audit | Credential taxonomy |
| M09 Unit 2 | Vault audit/break-glass | Detection and emergency-access review | Vault implementation |
| M09 Unit 3 | Dynamic DB credentials | Rotation readiness/consumer verification | Dynamic-secret mechanism |
| M09 Unit 6 | Projected tokens/legacy token Secrets | Token-mount/lifecycle audit | Token implementation |
| M09 Unit 7 | Issuer/JWKS/claims/audience/Vault JWT auth | Trust-policy audit and attack-path reasoning | Federation mechanism tutorial |
| M09 Unit 8 | Leak response/revoke-first | Identity incident drill | General leak-response workflow |
| M09 Unit 10 | Static-credential metric | Posture metric and ownership | Base metric definition |
| M12 Unit 4 | Signing key rotation/verification | Rotation readiness and trust-boundary review | Signing implementation |
| M12 Unit 5 | CI identity/build isolation | CI identity compromise response | Build isolation |
| M12 Unit 7 | Runtime/container hardening | Identity blast-radius handoff | Runtime hardening |
| M12 Units 8 and 11 | Admission/policy engines | Requirements and preview | Full policy authoring/rollout |
| M12 Unit 12 | Falco/runtime detection | Identity abuse and honeytoken linkage | Full Falco rules |
| M10 | Incident command/postmortems | Credential-specific containment/timing | General incident process |
| M11 | Metrics/logs/alerts | Identity posture metrics and event integration | Observability setup |
| M14/M16 | Multi-cluster governance | Identity ownership/exception boundaries | Full multi-cluster implementation |

### 6.7 SRE lens

| Failure mode | Default decision | Mitigation |
|---|---|---|
| Issuer/federation unavailable | Fail closed for new privileged actions; explicitly define existing-session behavior | Bounded retry and pre-approved audited fallback; avoid casual permanent backup token |
| Token expires mid-operation | Refresh only through supported mechanism | Verify audience/clock/refresh behavior; never log token |
| Rotation breaks consumer | Do not restore known-exposed credential without approval | Reload/restart consumer; verify new credential; overlap only if supported |
| Audit pipeline unavailable | Mark visibility degraded; pause high-risk promotion if policy requires | Bounded protected spool, alert on gap, replay and verify |
| Emergency revocation breaks service | Containment first; restore with new narrow credential | Identify consumer, issue replacement, verify least privilege |
| JIT cleanup fails | Alert and retry idempotently | Reconcile live binding; escalate if privilege remains |
| CNI does not enforce NetworkPolicy | Do not claim isolation | Supported CNI or fixture fallback; record gap |
| Operator identity compromised | Contain controller authority safely | Preserve logs, narrow RBAC, inspect resources, rotate, restore reviewed state |

SLIs: audit coverage/freshness; failed auth; rotation success; time-to-rotate/revoke/contain; policy violation rate; stale grants; access review completion; detection precision/recall; exceptions past expiry. Every metric needs denominator, source, owner, window and limitation.

**Trigger → triage → mitigation → follow-up:** suspicious grant/Secret read/token request/honeytoken → validate identity, time, resource, scope and telemetry → freeze risky actions, isolate workload, narrow/revoke identity, rotate downstream secrets → restore reviewed state, verify denial and service, regression test, measure time, postmortem. Audit volume/retention has a cost; missing events are a risk, not proof of no activity.

### 6.8 Security lens

| Threat | Control and negative test | Residual risk |
|---|---|---|
| Stolen Pod token | Least privilege, audience/lifetime, no unnecessary mount; prohibited action denied | Valid token can be abused within its granted scope |
| Broad RBAC | Audit + policy preview; wildcard/Secret-read fixture flagged | Static checker may miss indirect authority |
| Cross-environment reuse | Separate identities/trust; same synthetic identity ID across dev/prod flagged | External inventory may be incomplete |
| Credential in notebook/image | Secret scanning/build controls; fake marker test fails gate | Transformed/encoded secrets may evade detection |
| SSRF/metadata | Egress and metadata protections; fixture blocked-destination case | Alternate node/network path may bypass Pod policy |
| Compromised operator | Narrow RBAC and API monitoring; cluster-admin fixture flagged | Controller can misuse legitimately granted access |
| Rotation ineffective | Consumer reload + old-credential rejection test | Backend may not support immediate revocation |
| Audit gaps | Coverage/freshness metrics; missing event reports unknown | Upstream event loss |
| JIT privilege persists | Expiry reconciler and cleanup-failure alert | Reconciler itself can fail |
| Node compromise | Node authorization/NodeRestriction and workload isolation | Host may expose mounted data/credentials |

### 6.9 Production checklist

- [ ] Every human, CI, Kubernetes, workload, service-to-service, operator/controller, and node identity has owner and purpose.
- [ ] Credential classes and consumers inventoried without secret values.
- [ ] Trust policies constrain issuer/subject/audience/environment/target scope as supported.
- [ ] Dedicated ServiceAccounts used where practical; default-SA use reviewed.
- [ ] Unnecessary token automount disabled and tested; legacy long-lived token Secrets reviewed.
- [ ] RBAC audit covers cluster-admin, wildcards, Secret read, `pods/exec`, token creation, `impersonate`, `bind`, and `escalate`.
- [ ] Missing subjects, stale inventory, and cross-environment reuse reviewed.
- [ ] `kubectl auth can-i --as` interpreted only with impersonation permission.
- [ ] Operator/chart RBAC reviewed before install and upgrade.
- [ ] Node authorization/NodeRestriction verified where applicable.
- [ ] API/metadata access and NetworkPolicy enforcement measured for actual CNI.
- [ ] Notebook/DAG/image/model artifacts contain no shared long-lived credentials.
- [ ] Rotation inventory includes registry, signing, DB, TLS, CI trust and relevant data/KMS keys.
- [ ] At least four credential types have a successful rotation drill and consumer verification.
- [ ] Emergency revocation and scheduled rotation have separate runbooks.
- [ ] Break-glass/JIT access is separate, monitored, time-bound and rehearsed.
- [ ] Audit coverage, retention, redaction and freshness reviewed.
- [ ] Identity detections have positive/negative tests.
- [ ] Access reviews treat unobserved use cautiously.
- [ ] Exceptions have owner, reason, expiry, controls and revisit trigger.
- [ ] Posture metrics include owner/remediation, not only totals.
- [ ] Compromised identity tabletop measured time-to-contain and produced a postmortem.

### 6.10 Hands-on lab set

All ten labs are defensive and zero-budget. Use Python fixtures as the baseline; `kind` is optional where live behavior adds value. Record actual versions. Never save production Secret data. On WSL2, verify runtime integration, RAM/disk, and `kubectl config current-context`; native Linux may differ in cgroups, filesystem, and networking. If a CNI/audit feature is unavailable, use the fixture and document exactly what it proves.

#### Lab 1 — Kubernetes identity audit with planted defects

**Level/time:** L2–L4, 2–3 h. **Footprint/internet:** Python standard library, offline. **Prerequisites:** Python 3. **Objectives:** audit ServiceAccounts, Pods, roles, bindings, token Secrets, missing subjects, stale inventory and cross-environment reuse.

Tree: `lab-01/{identity_audit.py,test_identity_audit.py,fixtures/clean.json,fixtures/defects.json,evidence/}`.

The audit script accepts a single JSON object with an `items` array of Kubernetes-like objects. Optional `training.example/last-used-at`, `training.example/environment`, `training.example/identity-id`, and `training.example/api-access-required` annotations are training metadata, not Kubernetes API fields. It never reads/prints Secret data.

`identity_audit.py`:

```python
#!/usr/bin/env python3
import argparse, json, sys
from datetime import date
from pathlib import Path

ALLOW_CLUSTER_ADMIN_BINDINGS = {"platform-break-glass-binding"}
STALE_DAYS = 180  # [ASSUMPTION] local training policy

def ann(obj, key, default=None):
    return (obj.get("metadata") or {}).get("annotations", {}).get(key, default)

def objname(obj):
    m = obj.get("metadata") or {}
    return f"{m.get('namespace')}/{m.get('name','<unnamed>')}" if m.get("namespace") else m.get("name","<unnamed>")

def finding(rule, severity, obj, evidence, limitation, remediation):
    return {"finding_id":rule,"severity":severity,"kind":obj.get("kind","Unknown"),
            "object":objname(obj),"evidence":evidence,"limitation":limitation,"remediation":remediation}

def valid_items(data):
    if not isinstance(data,dict) or not isinstance(data.get("items"),list):
        raise ValueError("expected JSON object with items array")
    for x in data["items"]:
        if not isinstance(x,dict) or not isinstance(x.get("kind"),str) or not isinstance(x.get("metadata",{}),dict):
            raise ValueError("each item must have kind and object metadata")
    return data["items"]

def audit(items, today=None):
    today = today or date.today()
    out = []
    sas = [x for x in items if x["kind"]=="ServiceAccount"]
    pods = [x for x in items if x["kind"]=="Pod"]
    roles = [x for x in items if x["kind"] in {"Role","ClusterRole"}]
    bindings = [x for x in items if x["kind"] in {"RoleBinding","ClusterRoleBinding"}]
    secrets = [x for x in items if x["kind"]=="Secret"]
    known = {((x.get("metadata") or {}).get("namespace","default"),(x.get("metadata") or {}).get("name")) for x in sas}

    for b in bindings:
        meta=b.get("metadata") or {}; ref=b.get("roleRef") or {}
        if ref.get("name")=="cluster-admin" and meta.get("name") not in ALLOW_CLUSTER_ADMIN_BINDINGS:
            out.append(finding("ID001","critical",b,"Non-allow-listed cluster-admin binding.",
                "Static config does not prove effective authorization.","Remove/narrow; use a reviewed, time-bound exception."))
        for sub in b.get("subjects") or []:
            if sub.get("kind")=="ServiceAccount":
                ns=sub.get("namespace") or meta.get("namespace") or "default"
                if (ns,sub.get("name")) not in known:
                    out.append(finding("ID010","high",b,f"Missing subject ServiceAccount {ns}/{sub.get('name')}.",
                        "Snapshot may be incomplete or captured during recreation.","Verify inventory then repair/remove stale binding."))

    for role in roles:
        for rule in role.get("rules") or []:
            groups=rule.get("apiGroups") or []; resources=rule.get("resources") or []; verbs=rule.get("verbs") or []
            if any("*" in a for a in (groups,resources,verbs)):
                out.append(finding("ID002","high",role,f"Wildcard in groups={groups}, resources={resources}, verbs={verbs}.",
                    "Wildcards may be intentional; impact depends on bindings.","Use explicit minimum rules or documented exception."))
            if "secrets" in resources and any(v in verbs for v in ("get","list","watch","*")):
                out.append(finding("ID003","critical" if role["kind"]=="ClusterRole" else "high",role,
                    f"Secret read/list/watch verbs={verbs}.","Rules alone do not show bound subjects or actual Secret values.",
                    "Narrow namespace/resources; avoid broad list/watch; separate identity."))
            if "pods/exec" in resources and any(v in verbs for v in ("create","get","*")):
                out.append(finding("ID004","high",role,f"pods/exec verbs={verbs}.",
                    "Sensitive Pod reachability needs separate review.","Remove if unnecessary; narrow and audit if required."))
            if "serviceaccounts/token" in resources and any(v in verbs for v in ("create","*")):
                out.append(finding("ID005","high",role,"Can create ServiceAccount tokens.",
                    "Target and audience behavior require context.","Constrain target SA/audience/purpose and audit use."))
            if any(v in verbs for v in ("impersonate","bind","escalate")):
                out.append(finding("ID006","critical",role,f"Dangerous RBAC verb in {verbs}.",
                    "Impact depends on resource, resourceNames and API checks.","Remove or tightly scope with owner and regression tests."))

    for pod in pods:
        meta=pod.get("metadata") or {}; spec=pod.get("spec") or {}; ns=meta.get("namespace","default")
        sa=spec.get("serviceAccountName") or "default"
        if sa=="default":
            out.append(finding("ID007","medium",pod,"Pod uses default ServiceAccount.",
                "Some use may be intentional; inspect policy and owner.","Use dedicated SA or document exception."))
        saobj=next((x for x in sas if (x.get("metadata") or {}).get("name")==sa and
                    (x.get("metadata") or {}).get("namespace","default")==ns),{})
        mount=spec.get("automountServiceAccountToken",saobj.get("automountServiceAccountToken",True))
        need=ann(pod,"training.example/api-access-required",ann(saobj,"training.example/api-access-required","unknown"))
        if mount is True and need in {"false","unknown"}:
            out.append(finding("ID008","medium" if need=="false" else "low",pod,
                f"Token automount enabled; API need={need}.","Training metadata is not native API evidence.",
                "Validate API need with owner; disable if unnecessary and test workload."))

    for sec in secrets:
        if sec.get("type")=="kubernetes.io/service-account-token":
            out.append(finding("ID009","high",sec,"Legacy-style ServiceAccount token Secret type.",
                "Token lifecycle varies by Kubernetes version; Secret data was not read.",
                "Prefer supported projected/TokenRequest flow; verify whether still accepted."))

    envs={}
    for sa in sas:
        last=ann(sa,"training.example/last-used-at")
        if last:
            try:
                age=(today-date.fromisoformat(last)).days
                if age>STALE_DAYS:
                    out.append(finding("ID011","low",sa,f"Inventory last-used date is {age} days old.",
                        "Absence of observed use does not prove unused; telemetry may be incomplete.",
                        "Review owner and audit coverage; stage removal with rollback."))
            except ValueError:
                out.append(finding("ID012","low",sa,f"Malformed training last-used date {last!r}.",
                    "Not a Kubernetes-native last-use field.","Correct inventory; do not infer staleness."))
        ident=ann(sa,"training.example/identity-id"); env=ann(sa,"training.example/environment")
        if ident and env: envs.setdefault(ident,set()).add(env)
    for sa in sas:
        ident=ann(sa,"training.example/identity-id")
        if ident and len(envs.get(ident,set()))>1:
            out.append(finding("ID013","high",sa,f"Synthetic identity {ident!r} reused across {sorted(envs[ident])}.",
                "Only reuse represented in supplied inventory is detectable.",
                "Separate identities/trust policies or document narrow exception."))
    return sorted(out,key=lambda x:(x["finding_id"],x["kind"],x["object"],x["evidence"]))

def load_snapshot(path):
    return valid_items(json.loads(Path(path).read_text(encoding="utf-8")))

def report(findings):
    lines=[f"IDENTITY AUDIT: {len(findings)} finding(s)",""]
    for f in findings:
        lines += [f"[{f['severity'].upper()}] {f['finding_id']} {f['kind']} {f['object']}",
                  f" Evidence: {f['evidence']}",f" Limitation: {f['limitation']}",
                  f" Remediation: {f['remediation']}",""]
    return "\n".join(lines).rstrip()+"\n"

def main():
    p=argparse.ArgumentParser(); p.add_argument("input_json")
    p.add_argument("--json-out",required=True); p.add_argument("--report-out",required=True); a=p.parse_args()
    try:
        items=load_snapshot(a.input_json)
        findings=audit(items)
        Path(a.json_out).write_text(json.dumps(findings,indent=2)+"\n",encoding="utf-8")
        Path(a.report_out).write_text(report(findings),encoding="utf-8")
        print(f"findings={len(findings)}")
        return 1 if findings else 0
    except (OSError,UnicodeError,json.JSONDecodeError,ValueError) as e:
        print(f"ERROR: {type(e).__name__}: invalid input/output",file=sys.stderr); return 2

if __name__=="__main__": raise SystemExit(main())
```

`test_identity_audit.py`:

```python
import unittest, json
from datetime import date
from identity_audit import audit, valid_items

def o(kind,name,namespace=None,**kw):
    m={"name":name}
    if namespace: m["namespace"]=namespace
    return {"apiVersion":"v1","kind":kind,"metadata":m,**kw}

class Tests(unittest.TestCase):
    def test_clean(self):
        items=[o("ServiceAccount","api","serving",automountServiceAccountToken=False),
               o("Pod","api-0","serving",spec={"serviceAccountName":"api","automountServiceAccountToken":False}),
               o("Role","config","serving",rules=[{"apiGroups":[""],"resources":["configmaps"],"verbs":["get"]}]),
               o("RoleBinding","config","serving",roleRef={"kind":"Role","name":"config"},
                 subjects=[{"kind":"ServiceAccount","name":"api","namespace":"serving"}])]
        self.assertEqual(audit(items,today=date(2026,10,29)),[])
    def test_cluster_admin(self):
        self.assertIn("ID001",{x["finding_id"] for x in audit([o("ClusterRoleBinding","bad",roleRef={"name":"cluster-admin"})])})
    def test_allowlist(self):
        self.assertNotIn("ID001",{x["finding_id"] for x in audit([o("ClusterRoleBinding","platform-break-glass-binding",roleRef={"name":"cluster-admin"})])})
    def test_wildcard_and_secret(self):
        r=o("ClusterRole","bad",rules=[{"apiGroups":["*"],"resources":["secrets"],"verbs":["get","*"]}])
        ids={x["finding_id"] for x in audit([r])}; self.assertTrue({"ID002","ID003"}<=ids)
    def test_exec_token_and_dangerous_verbs(self):
        r=o("Role","bad","n",rules=[{"apiGroups":[""],"resources":["pods/exec","serviceaccounts/token","users"],"verbs":["create","impersonate","escalate"]}])
        ids={x["finding_id"] for x in audit([r])}; self.assertTrue({"ID004","ID005","ID006"}<=ids)
    def test_default_and_automount(self):
        p=o("Pod","p","n",spec={"serviceAccountName":"default"})
        ids={x["finding_id"] for x in audit([p])}; self.assertTrue({"ID007","ID008"}<=ids)
    def test_legacy_token(self):
        self.assertIn("ID009",{x["finding_id"] for x in audit([o("Secret","token","n",type="kubernetes.io/service-account-token")])})
    def test_missing_subject(self):
        b=o("RoleBinding","stale","n",subjects=[{"kind":"ServiceAccount","name":"gone","namespace":"n"}])
        self.assertIn("ID010",{x["finding_id"] for x in audit([b])})
    def test_stale_and_bad_date(self):
        a=o("ServiceAccount","old","n",metadata={"name":"old","namespace":"n","annotations":{"training.example/last-used-at":"2020-01-01"}})
        b=o("ServiceAccount","bad","n",metadata={"name":"bad","namespace":"n","annotations":{"training.example/last-used-at":"nope"}})
        ids={x["finding_id"] for x in audit([a,b],today=date(2026,10,29))}; self.assertTrue({"ID011","ID012"}<=ids)
    def test_cross_environment(self):
        a=o("ServiceAccount","a","dev",metadata={"name":"a","namespace":"dev","annotations":{"training.example/identity-id":"shared","training.example/environment":"dev"}})
        b=o("ServiceAccount","b","prod",metadata={"name":"b","namespace":"prod","annotations":{"training.example/identity-id":"shared","training.example/environment":"prod"}})
        self.assertIn("ID013",{x["finding_id"] for x in audit([a,b])})
    def test_malformed_json(self):
        import tempfile
        from pathlib import Path
        from identity_audit import load_snapshot
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"bad.json"; f.write_text("{",encoding="utf-8")
            with self.assertRaises(json.JSONDecodeError): load_snapshot(f)
    def test_unknown_kind_ignored(self): self.assertEqual(audit([o("Widget","x")]),[])
    def test_missing_nullable_fields(self): self.assertEqual(audit([{"kind":"Role","metadata":{"name":"empty"}}]),[])
    def test_bad_schema(self):
        with self.assertRaises(ValueError): valid_items({"items":{}})
    def test_malformed_date_does_not_crash(self):
        x=o("ServiceAccount","x","n",metadata={"name":"x","namespace":"n","annotations":{"training.example/last-used-at":"?"}})
        self.assertIn("ID012",{f["finding_id"] for f in audit([x])})

if __name__=="__main__": unittest.main()
```

Create `clean.json` with one dedicated SA, a Pod with automount false, a Role granting `get configmaps`, and a binding to that existing SA. Create `defects.json` with at least 15 planted patterns: cluster-admin binding, wildcard role, broad Secret read, `pods/exec`, token creation, `impersonate`, default-SA Pod, unnecessary automount, legacy token Secret, missing SA subject, stale date, malformed date, cross-environment reuse, undocumented token need, and an allow-listed emergency binding. No Secret data values are needed.

Run `python3 -m unittest -v test_identity_audit.py`, then invoke the script on both fixtures. Exit codes: 0 no findings; 1 policy findings; 2 input/tool error. **Positive:** clean fixture exits 0. **Negative:** defect fixture exits 1 and reports the planted rules. What it proves: deterministic detection on this schema. It does not compute all effective Kubernetes permissions or infer undocumented graph edges. False positives: intentional grants, incomplete snapshots, stale inventory. False negatives: indirect permissions, omitted resources, unsupported shapes. Cleanup: retain sanitized reports only. Evidence: reports, tests, versions, limitations.

#### Lab 2 — Identity graph and attack-path analyzer

**Level/time:** L2–L3, 1–2 h. **Footprint:** Python standard library, offline. Tree: `lab-02/{graph.json,identity_graph.py,test_identity_graph.py,evidence/}`.

`identity_graph.py`:

```python
import json
from collections import deque
from pathlib import Path

def shortest_path(graph,start,target):
    nodes={n["id"] for n in graph.get("nodes",[]) if isinstance(n,dict) and "id" in n}
    if start not in nodes or target not in nodes: return None
    adj={n:[] for n in nodes}
    for e in graph.get("edges",[]):
        if isinstance(e,dict) and e.get("from") in nodes and e.get("to") in nodes:
            adj[e["from"]].append((e["to"],e.get("kind","unknown")))
    q=deque([(start,[start],[])]); seen={start}
    while q:
        node,path,kinds=q.popleft()
        if node==target: return {"nodes":path,"edge_kinds":kinds}
        for nxt,kind in sorted(adj[node]):
            if nxt not in seen: seen.add(nxt); q.append((nxt,path+[nxt],kinds+[kind]))
    return None

def cuts(path):
    if not path: return []
    return [{"from":a,"to":b,"kind":k,"recommendation":"Review/narrow this edge; verify owner and alternate paths."}
            for a,b,k in zip(path["nodes"],path["nodes"][1:],path["edge_kinds"])]

def load(path):
    g=json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(g,dict) or not isinstance(g.get("nodes"),list) or not isinstance(g.get("edges"),list):
        raise ValueError("expected graph object with nodes/edges arrays")
    return g

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser(); p.add_argument("graph_json"); p.add_argument("--start",default="pod:etl-worker")
    p.add_argument("--target",default="asset:production-db"); p.add_argument("--out",required=True); a=p.parse_args()
    g=load(a.graph_json); path=shortest_path(g,a.start,a.target)
    Path(a.out).write_text(json.dumps({"path":path,"cut_edge_candidates":cuts(path)},indent=2)+"\n")
    print("reachable" if path else "unreachable")
```

`graph.json` should include nodes `pod:etl-worker`, `sa:pipeline/etl-worker`, `binding:all-workloads`, `role:read-secrets`, `permission:get-secrets`, `secret:data-prod/db-credentials`, `asset:production-db` and edges in that order. Use only fake names and no secret values.

`test_identity_graph.py`:

```python
import unittest
from identity_graph import shortest_path,cuts
class Tests(unittest.TestCase):
    def setUp(self):
        self.g={"nodes":[{"id":"pod"},{"id":"sa"},{"id":"secret"},{"id":"db"}],
                "edges":[{"from":"pod","to":"sa","kind":"runs-as"},{"from":"sa","to":"secret","kind":"can-read"},{"from":"secret","to":"db","kind":"contains"}]}
    def test_reachable(self): self.assertEqual(shortest_path(self.g,"pod","db")["nodes"],["pod","sa","secret","db"])
    def test_unreachable(self): self.assertIsNone(shortest_path(self.g,"pod","missing"))
    def test_missing_edge_ignored(self):
        self.assertIsNone(shortest_path({"nodes":[{"id":"a"},{"id":"b"}],"edges":[{"from":"a","to":"missing"}]},"a","b"))
    def test_cut_candidates(self): self.assertEqual(len(cuts(shortest_path(self.g,"pod","db"))),3)
    def test_no_path_no_cuts(self): self.assertEqual(cuts(None),[])
if __name__=="__main__": unittest.main()
```

Run `python3 -m unittest -v test_identity_graph.py`. Positive: path to fake asset found. Negative: remove `sa -> secret`; target becomes unreachable. Cut edges are recommendations, not automatic changes. Limitations: input graph may omit grants, namespaces, admission, or external IAM; shortest path is not proof of exploitability. Cleanup temporary reports; retain synthetic path/tests.

#### Lab 3 — Admission/policy enforcement preview

**Level/time:** L2–L3, 1–2 h. **Footprint:** Python standard library; optional Kyverno/OPA is awareness `[VERIFY]`. Tree: `lab-03/{policy_preview.py,test_policy_preview.py,fixtures/,evidence/}`.

`policy_preview.py`:

```python
def evaluate(obj,policy):
    out=[]; kind=obj.get("kind"); name=(obj.get("metadata") or {}).get("name","<unnamed>")
    if kind in {"Role","ClusterRole"}:
        for r in obj.get("rules") or []:
            if any("*" in (r.get(k) or []) for k in ("apiGroups","resources","verbs")):
                out.append(("wildcard-rbac",name))
            if "secrets" in (r.get("resources") or []) and any(v in (r.get("verbs") or []) for v in ("get","list","watch","*")):
                out.append(("secret-read",name))
    if kind in {"RoleBinding","ClusterRoleBinding"} and (obj.get("roleRef") or {}).get("name")=="cluster-admin":
        if name not in set(policy.get("cluster_admin_allowlist",[])): out.append(("cluster-admin",name))
    if kind=="Pod":
        s=obj.get("spec") or {}
        if policy.get("deny_default_sa") and (s.get("serviceAccountName") or "default")=="default": out.append(("default-sa",name))
        if policy.get("deny_automount") and s.get("automountServiceAccountToken") is True: out.append(("automount",name))
    if kind=="Secret" and obj.get("type")=="kubernetes.io/service-account-token": out.append(("legacy-token",name))
    return out

def decision(findings,mode):
    return "DENY" if mode=="enforce" and findings else "ALLOW_WITH_FINDINGS" if findings else "ALLOW"
```

`test_policy_preview.py`:

```python
import unittest
from policy_preview import evaluate,decision
P={"mode":"audit","deny_default_sa":True,"deny_automount":True,"cluster_admin_allowlist":[]}
class Tests(unittest.TestCase):
    def test_clean_pod(self): self.assertEqual(evaluate({"kind":"Pod","metadata":{"name":"ok"},"spec":{"serviceAccountName":"api","automountServiceAccountToken":False}},P),[])
    def test_wildcard(self): self.assertIn(("wildcard-rbac","bad"),evaluate({"kind":"ClusterRole","metadata":{"name":"bad"},"rules":[{"apiGroups":["*"],"resources":["*"],"verbs":["*"]}]},P))
    def test_audit_warns_not_blocks(self): self.assertEqual(decision([("bad","x")],"audit"),"ALLOW_WITH_FINDINGS")
    def test_enforce_denies(self): self.assertEqual(decision([("bad","x")],"enforce"),"DENY")
    def test_allowlist(self):
        x={"kind":"ClusterRoleBinding","metadata":{"name":"platform-break-glass-binding"},"roleRef":{"name":"cluster-admin"}}
        self.assertEqual(evaluate(x,dict(P,cluster_admin_allowlist=["platform-break-glass-binding"])),[])
if __name__=="__main__": unittest.main()
```

Positive: clean fixture passes. Negative: wildcard and non-allow-listed cluster-admin are flagged; enforce decision denies. Interpretation: this is a policy-intent preview, not a live admission request. Start audit/warn, review false positives, then Units 8/11 own production engine authoring. Cleanup fixtures. Evidence: tests, policy corpus, exceptions/owners, limitations.

#### Lab 4 — Compromised-token drill

**Level/time:** L2–L4, 1–2 h. **Footprint:** synthetic JSONL offline; kind optional. Tree: `lab-04/{events.jsonl,detect_identity_events.py,test_detect_identity_events.py,runbook.md,evidence/}`.

Synthetic event fixtures (not guaranteed exact output of any cluster version):

```json
{"ts":"2026-10-29T10:00:00Z","event":"secret_read","user":"system:serviceaccount:serving:ml-api","namespace":"data-prod","resource":"secrets","name":"FAKE_DB_MARKER","allowed":true}
{"ts":"2026-10-29T10:01:00Z","event":"token_request","user":"system:serviceaccount:serving:ml-api","namespace":"serving","audience":"unexpected-fixture-audience","allowed":true}
{"ts":"2026-10-29T10:02:00Z","event":"rbac_change","user":"synthetic-admin","resource":"clusterrolebindings","name":"unexpected-binding","allowed":true}
```

`detect_identity_events.py`:

```python
def detect(e):
    out=[]
    if e.get("event")=="secret_read" and e.get("namespace")=="data-prod": out.append("sensitive_secret_read")
    if e.get("event")=="token_request" and e.get("audience")=="unexpected-fixture-audience": out.append("unexpected_token_audience")
    if e.get("event")=="rbac_change" and e.get("resource")=="clusterrolebindings": out.append("privileged_binding_change")
    return out
```

`test_detect_identity_events.py`:

```python
import unittest
from detect_identity_events import detect
class Tests(unittest.TestCase):
    def test_sensitive_read(self): self.assertIn("sensitive_secret_read",detect({"event":"secret_read","namespace":"data-prod"}))
    def test_unexpected_audience(self): self.assertIn("unexpected_token_audience",detect({"event":"token_request","audience":"unexpected-fixture-audience"}))
    def test_benign_event(self): self.assertEqual(detect({"event":"health_check"}),[])
if __name__=="__main__": unittest.main()
```

Run `python3 -m unittest -v test_detect_identity_events.py`. Runbook: freeze risky changes; identify identity/token type/audience; preserve logs; inspect grants; contain Pod/remove inappropriate binding; rotate exposed external credential; verify denial where backend semantics support it; restore reviewed config; test legitimate access; add regression test/postmortem. Positive: sensitive read alerts. Negative: benign health check does not. Limitations: fixture detection does not prove live audit coverage. Never print real tokens. Cleanup lab resources; evidence is synthetic alert, timeline, containment and gap note.

#### Lab 5 — Rotation drill set and readiness inventory

**Level/time:** L2–L4, 2–3 h. **Footprint:** synthetic files offline. **Objective:** measure four credential types: registry credential, signing key (Unit 4), dynamic DB credential/role (M09), TLS certificate (M04).

Tree: `lab-05/{credentials.json,rotation_drill.py,test_rotation_drill.py,runbook.md,evidence/}`. Each inventory row must include credential ID (non-secret), owner, consumers, scope, storage, issuer/authority, expiry, rotation procedure, reload/restart needs, verification, rollback, last drill, measured time, and residual risk.

`rotation_drill.py`:

```python
import json,sys
from pathlib import Path
REQUIRED={"id","type","owner","consumers","scope","storage","issuer_authority","expiry","reload","verification","rollback","residual_risk"}
def validate(items):
    errors=[]
    for i,x in enumerate(items):
        missing=sorted(REQUIRED-set(x))
        if missing: errors.append(f"row {i}: missing {','.join(missing)}")
        if not x.get("owner") or not x.get("consumers"): errors.append(f"row {i}: owner and consumers required")
    return errors
if __name__=="__main__":
    items=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")); errors=validate(items)
    if errors: print("DENY: "+"; ".join(errors)); raise SystemExit(1)
    print(f"INVENTORY_PASS: {len(items)} credential records; no secret values required")
    for x in items: print(f"READY_FOR_DRILL id={x['id']} type={x['type']} owner={x['owner']}")
```

`test_rotation_drill.py`:

```python
import unittest
from rotation_drill import validate
GOOD={"id":"x","type":"registry credential","owner":"team","consumers":["app"],"scope":"lab","storage":"fixture","issuer_authority":"lab","expiry":"2026-11-30","reload":"restart","verification":"new accepted/old rejected","rollback":"restore reviewed fixture","residual_risk":"fixture only"}
class Tests(unittest.TestCase):
    def test_complete(self): self.assertEqual(validate([GOOD]),[])
    def test_missing_owner(self): self.assertTrue(validate([dict(GOOD,owner="")]))
    def test_missing_consumer(self): self.assertTrue(validate([dict(GOOD,consumers=[])]))
if __name__=="__main__": unittest.main()
```

Run the tests and script. For each of four types, record UTC start/end, new-credential success, old-credential rejection where supported, consumer reload/restart, rollback and failure. `time_to_rotate_seconds = verified_new_use - drill_start`. A new credential working while old material remains accepted is not a complete revocation test. Positive: complete inventory passes. Negative: missing owner/consumer fails. These fixtures do not prove Vault/registry/CA revocation behavior. Cleanup synthetic keys/certs and never retain real key material. Evidence: inventory, four timings, verification outputs, residual risks.


#### Lab 6 — Identity posture metrics and dashboard

**Level/time:** L3–L4, 1–2 h. **Footprint/internet:** Python standard library, offline. **Objective:** export counts/trends with ownership and missing-data status; connect to M11 or use an offline report.

Tree: `lab-06/{posture.json,posture_metrics.py,test_posture_metrics.py,evidence/}`.

`posture_metrics.py`:

```python
import json,sys
from pathlib import Path
FIELDS=["cluster_admin_bindings","wildcard_grants","default_sa_workloads","token_automount_enabled",
        "static_credential_indicators","stale_serviceaccounts","missing_binding_subjects","trust_policy_findings"]
def summarize(s):
    missing=[k for k in FIELDS if k not in s]
    if missing: return {"status":"INCOMPLETE","missing":missing,"metrics":{}}
    for k in FIELDS:
        if not isinstance(s[k],int) or s[k]<0: return {"status":"INVALID","field":k,"metrics":{}}
    return {"status":"OK","metrics":{k:s[k] for k in FIELDS},
            "total_findings":sum(s[k] for k in FIELDS),
            "note":"Counts can overlap; total_findings is not a unique-risk count."}
if __name__=="__main__":
    r=summarize(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")))
    Path(sys.argv[2]).write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8")
    print(r["status"]); raise SystemExit(0 if r["status"]=="OK" else 1)
```

`test_posture_metrics.py`:

```python
import unittest
from posture_metrics import summarize
GOOD={"cluster_admin_bindings":0,"wildcard_grants":1,"default_sa_workloads":2,"token_automount_enabled":3,
      "static_credential_indicators":2,"stale_serviceaccounts":1,"missing_binding_subjects":0,"trust_policy_findings":1}
class Tests(unittest.TestCase):
    def test_counts(self):
        r=summarize(GOOD); self.assertEqual(r["status"],"OK"); self.assertEqual(r["total_findings"],10)
    def test_missing_is_not_zero(self):
        x=dict(GOOD); x.pop("stale_serviceaccounts"); self.assertEqual(summarize(x)["status"],"INCOMPLETE")
    def test_negative_invalid(self): self.assertEqual(summarize(dict(GOOD,wildcard_grants=-1))["status"],"INVALID")
if __name__=="__main__": unittest.main()
```

Run `python3 -m unittest -v test_posture_metrics.py`. Add `collected_at_utc`, owner, source and observation window to your snapshot. M11 path: export bounded-label gauges and alert on locally approved thresholds or stale collection; never use identity/Secret names as unbounded Prometheus labels. Thresholds are `[ASSUMPTION]` until approved.

**Positive:** complete non-negative snapshot reports expected counts. **Negative:** missing/negative values report `INCOMPLETE`/`INVALID`, not zero. Counts can overlap. Cleanup synthetic data. Evidence: snapshot, summary, trend, owner/source/window, M11 integration or offline fallback.

#### Lab 7 — JIT access with auto-expiry and audit

**Level/time:** L3–L4, 1–2 h. **Footprint:** Python standard library; offline. **Objective:** record requester, reason, scope, deadline; test idempotent grant and expiry cleanup.

Tree: `lab-07/{jit_access.py,test_jit_access.py,ledger.json,evidence/}`. The core implementation is a **ledger simulation**. It does not create a live RoleBinding. Kubernetes RoleBinding TTL is not assumed to exist; a production broker/controller must apply and remove the actual grant and alert on cleanup failure.

`jit_access.py`:

```python
from datetime import timedelta
from pathlib import Path
import json

def grant(ledger, requester, reason, namespace, serviceaccount, role, now, ttl_minutes):
    if not requester.strip() or not reason.strip(): raise ValueError("requester and reason required")
    if not 1 <= ttl_minutes <= 60: raise ValueError("TTL must be 1..60 minutes in this lab")
    if not all(x and x.replace("-","").replace("_","").isalnum() for x in (namespace,serviceaccount,role)):
        raise ValueError("names must be simple lab identifiers")
    key=f"{namespace}:{serviceaccount}:{role}"
    for r in ledger:
        if r["key"]==key and r["status"]=="active": return ledger,r
    r={"key":key,"requester":requester,"reason":reason,"namespace":namespace,
       "serviceaccount":serviceaccount,"role":role,"created_at":now.isoformat(),
       "expires_at":(now+timedelta(minutes=ttl_minutes)).isoformat(),"status":"active",
       "audit":["grant-record-created"]}
    return ledger+[r],r

def reconcile(ledger, now):
    events=[]
    for r in ledger:
        if r["status"]=="active" and r["expires_at"] <= now.isoformat():
            r["status"]="expired"; r["audit"].append("expiry-reconciled")
            events.append({"event":"jit_expired","key":r["key"],"at":now.isoformat()})
    return ledger,events

if __name__=="__main__":
    import argparse
    from datetime import datetime,timezone
    p=argparse.ArgumentParser(); p.add_argument("ledger"); p.add_argument("--grant",action="store_true")
    p.add_argument("--reconcile",action="store_true"); p.add_argument("--requester",default="")
    p.add_argument("--reason",default=""); p.add_argument("--namespace",default="jit-lab")
    p.add_argument("--serviceaccount",default="reviewer"); p.add_argument("--role",default="read-config")
    p.add_argument("--ttl-minutes",type=int,default=5); a=p.parse_args(); f=Path(a.ledger)
    ledger=json.loads(f.read_text()) if f.exists() else []; now=datetime.now(timezone.utc)
    if a.grant: ledger,r=grant(ledger,a.requester,a.reason,a.namespace,a.serviceaccount,a.role,now,a.ttl_minutes); print(json.dumps(r,indent=2))
    if a.reconcile: ledger,events=reconcile(ledger,now); print(json.dumps({"events":events},indent=2))
    f.write_text(json.dumps(ledger,indent=2)+"\n")
```

`test_jit_access.py`:

```python
import unittest
from datetime import datetime,timezone,timedelta
from jit_access import grant,reconcile
NOW=datetime(2026,10,29,10,0,tzinfo=timezone.utc)
class Tests(unittest.TestCase):
    def test_grant_audits_requester_reason_deadline(self):
        l,r=grant([],"reviewer","synthetic review","jit-lab","reviewer","read-config",NOW,5)
        self.assertEqual(r["status"],"active"); self.assertEqual(r["reason"],"synthetic review"); self.assertIn("expires_at",r)
    def test_missing_reason(self):
        with self.assertRaises(ValueError): grant([],"reviewer","","jit-lab","reviewer","read-config",NOW,5)
    def test_repeat_does_not_extend(self):
        l,a=grant([],"reviewer","review","jit-lab","reviewer","read-config",NOW,5)
        l,b=grant(l,"reviewer","again","jit-lab","reviewer","read-config",NOW+timedelta(minutes=1),5)
        self.assertEqual(a["expires_at"],b["expires_at"]); self.assertEqual(len(l),1)
    def test_expiry(self):
        l,_=grant([],"reviewer","review","jit-lab","reviewer","read-config",NOW,5)
        l,e=reconcile(l,NOW+timedelta(minutes=6)); self.assertEqual(l[0]["status"],"expired"); self.assertEqual(e[0]["event"],"jit_expired")
    def test_not_expired(self):
        l,_=grant([],"reviewer","review","jit-lab","reviewer","read-config",NOW,5)
        l,e=reconcile(l,NOW+timedelta(minutes=2)); self.assertEqual(l[0]["status"],"active"); self.assertEqual(e,[])
if __name__=="__main__": unittest.main()
```

Run tests; simulate `python3 jit_access.py ledger.json --grant --requester reviewer --reason "synthetic review" --ttl-minutes 1`, wait at least one minute, then run `--reconcile`. **Positive:** record is active before expiry. **Negative:** missing reason fails; expired grant transitions and emits audit event; repeated grant does not extend expiry. If you implement live kind extension, verify context, apply a namespace-scoped Role/RoleBinding, reconcile actual deletion, and never grant cluster-admin.

For an optional live kind demonstration, apply this minimal base manifest first. It grants only `get` on ConfigMaps in `jit-lab`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: jit-lab
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: reviewer
  namespace: jit-lab
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: read-config
  namespace: jit-lab
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    verbs: ["get"]
```

**Optional live extension:** this script only accepts a `kind-*` current context and fixed namespace/ServiceAccount/Role names. It never reads or prints a token. The user running it must already be authorized to manage RoleBindings and impersonate the test ServiceAccount. Do not use it against a shared cluster.

`jit_kind.py`:

```python
import json, subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

NS, SA, ROLE, BINDING = "jit-lab", "reviewer", "read-config", "jit-reviewer-read-config"

def kubectl(args, input_text=None):
    return subprocess.run(["kubectl", *args], input=input_text, text=True,
                          capture_output=True, check=False)

def require_kind_context():
    r=kubectl(["config","current-context"])
    if r.returncode or not r.stdout.strip().startswith("kind-"):
        raise RuntimeError("DENY: current context must start with kind-")
    for args in (["get","namespace",NS],["get","serviceaccount",SA,"-n",NS],["get","role",ROLE,"-n",NS]):
        r=kubectl(args)
        if r.returncode: raise RuntimeError("DENY: expected lab namespace, ServiceAccount, or Role missing")

def manifest():
    return f"""apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: {BINDING}
  namespace: {NS}
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: {ROLE}
subjects:
- kind: ServiceAccount
  name: {SA}
  namespace: {NS}
"""

def grant_live(ledger, requester, reason, ttl_minutes=5):
    if not requester.strip() or not reason.strip(): raise ValueError("requester/reason required")
    if not 1 <= ttl_minutes <= 30: raise ValueError("TTL must be 1..30 minutes")
    require_kind_context()
    active=next((x for x in ledger if x["binding"]==BINDING and x["status"]=="active"),None)
    if active: return ledger, active
    r=kubectl(["apply","-f","-"], manifest())
    if r.returncode: raise RuntimeError("RoleBinding apply failed; inspect sanitized kubectl error")
    # Requires caller's impersonation permission; no bearer token is printed.
    check=kubectl(["auth","can-i","get","configmaps",f"--as=system:serviceaccount:{NS}:{SA}","-n",NS])
    if check.returncode or check.stdout.strip()!="yes":
        kubectl(["delete","rolebinding",BINDING,"-n",NS,"--ignore-not-found=true"])
        raise RuntimeError("DENY: permission verification failed; temporary binding removed")
    now=datetime.now(timezone.utc)
    record={"binding":BINDING,"namespace":NS,"serviceaccount":SA,"role":ROLE,
            "requester":requester,"reason":reason,"created_at":now.isoformat(),
            "expires_at":(now+timedelta(minutes=ttl_minutes)).isoformat(),
            "status":"active","audit":["rolebinding-created","can-i-get-configmaps=yes"]}
    return ledger+[record],record

def reconcile_live(ledger, now=None):
    now=now or datetime.now(timezone.utc); events=[]
    require_kind_context()
    for r in ledger:
        expiry=datetime.fromisoformat(r["expires_at"])
        if r["status"]=="active" and expiry<=now:
            result=kubectl(["delete","rolebinding",r["binding"],"-n",r["namespace"],"--ignore-not-found=true"])
            if result.returncode:
                events.append({"event":"jit_cleanup_failed","binding":r["binding"],"at":now.isoformat()})
                continue
            r["status"]="expired"; r.setdefault("audit",[]).append("rolebinding-deleted")
            events.append({"event":"jit_expired","binding":r["binding"],"at":now.isoformat()})
    return ledger,events

def main():
    import argparse
    p=argparse.ArgumentParser(); p.add_argument("ledger"); p.add_argument("--grant",action="store_true")
    p.add_argument("--reconcile",action="store_true"); p.add_argument("--requester",default="")
    p.add_argument("--reason",default=""); p.add_argument("--ttl-minutes",type=int,default=5); a=p.parse_args()
    f=Path(a.ledger); ledger=json.loads(f.read_text()) if f.exists() else []
    if a.grant: ledger,r=grant_live(ledger,a.requester,a.reason,a.ttl_minutes); print(json.dumps(r,indent=2))
    if a.reconcile: ledger,events=reconcile_live(ledger); print(json.dumps({"events":events},indent=2))
    f.write_text(json.dumps(ledger,indent=2)+"\n")
if __name__=="__main__": main()
```

The `--reconcile` command must be scheduled/run again after the deadline; this small script is not a continuously running controller. If it is not run, the binding remains. In production, use a managed JIT/access broker or resilient controller with durable state, retries, alerting, and independent reconciliation. Test the failure case in the local lab, not by leaving real privileged access active.

`test_jit_kind.py` tests the live extension's safety guard and cleanup-failure behavior without contacting a cluster:

```python
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from datetime import datetime,timezone,timedelta
import jit_kind

class LiveJITTests(unittest.TestCase):
    def test_manifest_is_narrow(self):
        m=jit_kind.manifest()
        self.assertIn("namespace: jit-lab",m)
        self.assertIn("name: read-config",m)
        self.assertNotIn("cluster-admin",m)
    def test_cleanup_failure_keeps_record_active(self):
        now=datetime(2026,10,29,10,0,tzinfo=timezone.utc)
        ledger=[{"binding":"jit-reviewer-read-config","namespace":"jit-lab",
                 "expires_at":(now-timedelta(minutes=1)).isoformat(),"status":"active"}]
        with patch("jit_kind.require_kind_context"), patch("jit_kind.kubectl",return_value=SimpleNamespace(returncode=1)):
            ledger,events=jit_kind.reconcile_live(ledger,now)
        self.assertEqual(ledger[0]["status"],"active")
        self.assertEqual(events[0]["event"],"jit_cleanup_failed")
    def test_wrong_context_rejected(self):
        with patch("jit_kind.kubectl",return_value=SimpleNamespace(returncode=0,stdout="docker-desktop\\n")):
            with self.assertRaises(RuntimeError): jit_kind.require_kind_context()
if __name__=="__main__": unittest.main()
```

Run `python3 -m unittest -v test_jit_kind.py`. These tests exercise mocked control flow only; they do not prove a live cluster's RBAC or cleanup behavior.

 Cleanup ledger and lab binding. Evidence: before/after ledger, tests, expiry event, explicit simulation/live distinction.

#### Lab 8 — Metadata/API-server access restriction

**Level/time:** L2–L3, 1–2 h. **Footprint:** optional kind; fixture fallback offline. Do not call real metadata endpoints.

Tree: `lab-08/{no-api-workload.yaml,network-policy.yaml,check_policy.py,evidence/}`.

`no-api-workload.yaml` (illustrative):

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: identity-no-api
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app
  namespace: identity-no-api
automountServiceAccountToken: false
---
apiVersion: v1
kind: Pod
metadata:
  name: app
  namespace: identity-no-api
  labels:
    app: no-api
spec:
  serviceAccountName: app
  automountServiceAccountToken: false
  containers:
    - name: app
      image: busybox:1.36
      command: ["sh", "-c", "sleep 3600"]
```

`network-policy.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-egress
  namespace: identity-no-api
spec:
  podSelector: {}
  policyTypes: ["Egress"]
  egress: []
```

This intentionally blocks all egress and may block DNS/application dependencies; it is not a production allow-list. API-server paths in kind may involve host/node addresses that differ by CNI. NetworkPolicy works only with a network plugin that enforces it `[VERIFY]`.

`check_policy.py`:

```python
def evaluate(policy, labels):
    spec=policy.get("spec",{}); selector=spec.get("podSelector",{}).get("matchLabels",{})
    if not all(labels.get(k)==v for k,v in selector.items()): return "NOT_SELECTED"
    if "Egress" not in spec.get("policyTypes",[]): return "NO_EGRESS_POLICY"
    if not spec.get("egress"): return "DENY_EGRESS_BY_POLICY_INTENT"
    return "REVIEW_ALLOW_RULES"
if __name__=="__main__":
    p={"spec":{"podSelector":{"matchLabels":{"app":"no-api"}},"policyTypes":["Egress"],"egress":[]}}
    print(evaluate(p,{"app":"no-api"}))
```

**Live test:** only in disposable kind, apply manifests, inspect `kubectl get networkpolicy -n identity-no-api -o yaml`, and test harmless connectivity to `kubernetes.default.svc:443`. Use a separate positive-control workload/namespace whose owner documents API need. Do not print tokens. If policy has no effect, verify CNI support and report `NOT VERIFIED`; do not infer enforcement from resource existence.

**Positive:** fixture selects intended Pod and returns deny-egress intent. **Negative:** change Pod label or add allow rule and confirm expected result changes. Live network denial counts only if CNI path was verified. **Proves:** fixture intent or tested route only. **Does not prove:** every egress path or cloud metadata defense. Cleanup namespace/cluster. Evidence: manifest, CNI/version, connectivity result, limitations.

#### Lab 9 — Audit-log access review

**Level/time:** L3–L4, 1–2 h. **Footprint:** Python standard library, offline. **Objective:** infer observed permissions, propose reductions, and produce ≥5 review findings with owner, confidence, reviewer, and review date.

Tree: `lab-09/{audit.jsonl,access_review.py,test_access_review.py,evidence/}`. `audit.jsonl` contains synthetic events, e.g.:

```json
{"ts":"2026-10-01T10:00:00Z","identity":"sa:serving/ml-api","action":"get","resource":"configmaps","namespace":"serving"}
{"ts":"2026-10-02T10:00:00Z","identity":"sa:pipeline/etl","action":"get","resource":"secrets","namespace":"pipeline"}
{"ts":"2026-10-03T10:00:00Z","identity":"sa:ops/operator","action":"list","resource":"pods","namespace":"default"}
{"ts":"2026-10-04T10:00:00Z","identity":"ci:release","action":"create","resource":"deployments","namespace":"staging"}
{"ts":"2026-10-05T10:00:00Z","identity":"human:reviewer","action":"get","resource":"configmaps","namespace":"serving"}
```

`access_review.py`:

```python
from collections import defaultdict
def build_review(events,grants,window,reviewer,review_date):
    observed=defaultdict(set)
    for e in events: observed[e.get("identity")].add((e.get("action"),e.get("resource"),e.get("namespace")))
    out=[]
    for g in grants:
        ident=g["identity"]; match=(g["verb"],g["resource"],g["namespace"]) in observed.get(ident,set())
        out.append({"identity":ident,"current_grant":f"{g['verb']} {g['resource']} in {g['namespace']}",
          "observed_use_window":window,"observed_match":match,
          "proposed_grant":"retain pending owner review" if match else "candidate for reduction; not-observed does not mean not-needed",
          "confidence":"medium" if match else "low","risk":"validate least privilege and data sensitivity",
          "reviewer":reviewer,"owner":g.get("owner","UNASSIGNED"),"review_date":review_date})
    return out
```

`test_access_review.py`:

```python
import unittest
from access_review import build_review
class Tests(unittest.TestCase):
    def test_observed_not_auto_removed(self):
        r=build_review([{"identity":"sa:x","action":"get","resource":"configmaps","namespace":"n"}],
          [{"identity":"sa:x","verb":"get","resource":"configmaps","namespace":"n","owner":"team"}],"window","reviewer","2026-10-29")
        self.assertIn("retain",r[0]["proposed_grant"])
    def test_unobserved_low_confidence(self):
        r=build_review([], [{"identity":"sa:x","verb":"list","resource":"pods","namespace":"n","owner":"team"}],"window","reviewer","2026-10-29")
        self.assertEqual(r[0]["confidence"],"low"); self.assertIn("not-observed does not mean not-needed",r[0]["proposed_grant"])
    def test_missing_owner_visible(self):
        r=build_review([], [{"identity":"sa:x","verb":"get","resource":"secrets","namespace":"n"}],"window","reviewer","2026-10-29")
        self.assertEqual(r[0]["owner"],"UNASSIGNED")
if __name__=="__main__": unittest.main()
```

Positive: observed permission remains pending owner review. Negative: unobserved permission is low-confidence candidate, never automatic deletion. Generate ≥5 rows and include current grant, observed window, proposed grant, confidence, risk, reviewer, owner, review date. Absence of events is not proof of no need; logs can be incomplete. Cleanup synthetic logs; evidence report, tests, owner decisions.

#### Lab 10 — Operator RBAC review

**Level/time:** L2–L3, 1–2 h. **Footprint:** offline. Do not install production operator. Tree: `lab-10/{operator-fixture.yaml,review.md,evidence/}`.

Synthetic intentionally over-privileged fixture:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: sample-operator
  namespace: operators
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: sample-operator
rules:
  - apiGroups: ["*"]
    resources: ["*"]
    verbs: ["*"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: sample-operator
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: sample-operator
subjects:
  - kind: ServiceAccount
    name: sample-operator
    namespace: operators
```

`review.md` should identify: wildcard cluster-wide permissions; potential Secret access; potential Pod/exec and RBAC-related authority depending on rules; cross-namespace reach; missing documented need for each verb. Recommend explicit API groups/resources/verbs, namespace-scoped Role where possible, separation of read/write authority, owner approval, and upgrade diff review. Do not assume the operator actually uses every permission in the wildcard rule.

**Positive:** reviewed narrow fixture has no wildcard finding in Lab 1 audit. **Negative:** synthetic fixture triggers wildcard/high-blast-radius findings. **Proves:** static permission breadth. **Does not prove:** runtime use or the minimum permissions required by operator code. Cleanup temporary fixture. Evidence: findings, owner decision, least-privilege proposal, upgrade-review plan.

#### Lab completion rubric

| Lab | Pass criteria | Evidence | Limit |
|---|---|---|---|
| 1 | Clean passes; ≥10 defects detected; parser error distinct | JSON/report/tests | Heuristic, not full RBAC engine |
| 2 | Reachable/unreachable path and cut candidates tested | Graph/output/tests | Input completeness |
| 3 | Clean allowed, risky fixture flagged, audit/enforce decision tested | Fixtures/tests | Not live admission |
| 4 | Synthetic sensitive event alerts; containment documented | Alerts/timeline/runbook | Not live audit proof |
| 5 | Four types inventoried/timed; reload/old-credential test | Inventory/timings | Local not production SLO |
| 6 | Correct counts and missing-data status | Snapshot/report/tests | Counts can overlap |
| 7 | Request/reason/deadline and expiry tested | Ledger/tests | Ledger simulation |
| 8 | Policy intent tested; CNI measured or unverified | Manifest/result | Resource alone is not enforcement |
| 9 | ≥5 review findings; unobserved use not auto-deleted | Report/tests | Observation window can miss rare paths |
| 10 | Excessive RBAC identified and least-privilege proposal defended | Manifest/review | Static permissions only |


#### Lab 1 fixture corpus (complete minimal example)

`fixtures/clean.json`:

```json
{
  "items": [
    {"apiVersion":"v1","kind":"ServiceAccount","metadata":{"name":"ml-api","namespace":"serving"},"automountServiceAccountToken":false},
    {"apiVersion":"v1","kind":"Pod","metadata":{"name":"ml-api-0","namespace":"serving","annotations":{"training.example/api-access-required":"false"}},"spec":{"serviceAccountName":"ml-api","automountServiceAccountToken":false}},
    {"apiVersion":"rbac.authorization.k8s.io/v1","kind":"Role","metadata":{"name":"read-config","namespace":"serving"},"rules":[{"apiGroups":[""],"resources":["configmaps"],"verbs":["get"]}]},
    {"apiVersion":"rbac.authorization.k8s.io/v1","kind":"RoleBinding","metadata":{"name":"read-config","namespace":"serving"},"roleRef":{"kind":"Role","name":"read-config"},"subjects":[{"kind":"ServiceAccount","name":"ml-api","namespace":"serving"}]}
  ]
}
```

`fixtures/defects.json` (15+ planted conditions; synthetic metadata only):

```json
{
  "items": [
    {"apiVersion":"v1","kind":"ServiceAccount","metadata":{"name":"etl","namespace":"pipeline","annotations":{"training.example/identity-id":"shared-data","training.example/environment":"dev","training.example/last-used-at":"2020-01-01"}}},
    {"apiVersion":"v1","kind":"ServiceAccount","metadata":{"name":"etl-prod","namespace":"pipeline-prod","annotations":{"training.example/identity-id":"shared-data","training.example/environment":"prod"}}},
    {"apiVersion":"v1","kind":"ServiceAccount","metadata":{"name":"bad-date","namespace":"lab","annotations":{"training.example/last-used-at":"not-a-date"}}},
    {"apiVersion":"v1","kind":"Pod","metadata":{"name":"default-pod","namespace":"lab","annotations":{"training.example/api-access-required":"false"}},"spec":{"serviceAccountName":"default","automountServiceAccountToken":true}},
    {"apiVersion":"v1","kind":"Secret","metadata":{"name":"old-token","namespace":"lab"},"type":"kubernetes.io/service-account-token"},
    {"apiVersion":"rbac.authorization.k8s.io/v1","kind":"ClusterRole","metadata":{"name":"wildcard"},"rules":[{"apiGroups":["*"],"resources":["*"],"verbs":["*"]}]},
    {"apiVersion":"rbac.authorization.k8s.io/v1","kind":"ClusterRole","metadata":{"name":"secret-reader"},"rules":[{"apiGroups":[""],"resources":["secrets"],"verbs":["get","list","watch"]}]},
    {"apiVersion":"rbac.authorization.k8s.io/v1","kind":"Role","metadata":{"name":"exec"},"rules":[{"apiGroups":[""],"resources":["pods/exec"],"verbs":["create"]}]},
    {"apiVersion":"rbac.authorization.k8s.io/v1","kind":"Role","metadata":{"name":"mint-token"},"rules":[{"apiGroups":[""],"resources":["serviceaccounts/token"],"verbs":["create"]}]},
    {"apiVersion":"rbac.authorization.k8s.io/v1","kind":"ClusterRole","metadata":{"name":"impersonate"},"rules":[{"apiGroups":[""],"resources":["users"],"verbs":["impersonate"]}]},
    {"apiVersion":"rbac.authorization.k8s.io/v1","kind":"ClusterRole","metadata":{"name":"escalate"},"rules":[{"apiGroups":["rbac.authorization.k8s.io"],"resources":["clusterroles"],"verbs":["bind","escalate"]}]},
    {"apiVersion":"rbac.authorization.k8s.io/v1","kind":"ClusterRoleBinding","metadata":{"name":"bad-admin"},"roleRef":{"kind":"ClusterRole","name":"cluster-admin"},"subjects":[]},
    {"apiVersion":"rbac.authorization.k8s.io/v1","kind":"ClusterRoleBinding","metadata":{"name":"platform-break-glass-binding"},"roleRef":{"kind":"ClusterRole","name":"cluster-admin"},"subjects":[]},
    {"apiVersion":"rbac.authorization.k8s.io/v1","kind":"RoleBinding","metadata":{"name":"missing-subject","namespace":"lab"},"roleRef":{"kind":"Role","name":"read-config"},"subjects":[{"kind":"ServiceAccount","name":"deleted","namespace":"lab"}]},
    {"apiVersion":"v1","kind":"ServiceAccount","metadata":{"name":"unknown-need","namespace":"lab"},"automountServiceAccountToken":true},
    {"apiVersion":"v1","kind":"Pod","metadata":{"name":"unknown-need-pod","namespace":"lab"},"spec":{"serviceAccountName":"unknown-need"}}
  ]
}
```

Run the audit against both. Because the allow-listed `platform-break-glass-binding` still has a cluster-admin role, separately review it as a privileged exception with owner/expiry; the script's allow-list suppresses ID001 only, not all risk. The script currently reports missing subjects only on bindings and checks `automount` on Pods, so the final SA-only row is a review fixture but does not necessarily generate an automount finding without a Pod referencing it. Record such limitations rather than claiming every line must trigger a finding.

#### Lab 3 addendum — trust-policy linter fixtures

Use a normalized, provider-neutral fixture schema rather than guessing a cloud policy language. `trust_lint.py`:

```python
def lint(policy):
    findings=[]
    conditions=policy.get("conditions") or {}
    for claim in ("sub","aud"):
        value=conditions.get(claim)
        if value is None or value=="":
            findings.append(f"missing_{claim}")
        elif value=="*" or value==["*"] or (isinstance(value,str) and "*" in value):
            findings.append(f"wildcard_{claim}")
    return findings

if __name__=="__main__":
    import json,sys
    from pathlib import Path
    p=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    findings=lint(p)
    print(json.dumps({"findings":findings,"decision":"DENY" if findings else "ALLOW"},indent=2))
    raise SystemExit(1 if findings else 0)
```

`test_trust_lint.py`:

```python
import unittest
from trust_lint import lint
class Tests(unittest.TestCase):
    def test_narrow_policy(self): self.assertEqual(lint({"conditions":{"sub":"repo:team/app:ref:main","aud":"registry-push"}}),[])
    def test_missing_sub(self): self.assertIn("missing_sub",lint({"conditions":{"aud":"registry-push"}}))
    def test_missing_aud(self): self.assertIn("missing_aud",lint({"conditions":{"sub":"repo:team/app"}}))
    def test_wildcard_subject(self): self.assertIn("wildcard_sub",lint({"conditions":{"sub":"*","aud":"registry-push"}}))
    def test_wildcard_audience(self): self.assertIn("wildcard_aud",lint({"conditions":{"sub":"repo:team/app","aud":"*"}}))
if __name__=="__main__": unittest.main()
```

Positive: narrow fixture is accepted. Negative: missing/wildcard `sub` or `aud` is rejected. Provider claim names and policy semantics are `[VERIFY]`; a provider adapter must map the real policy format to this normalized schema, use official docs, and test both allowed and denied tokens without logging token contents. The fixture linter does not verify token signatures or real federation.


#### Troubleshooting and failure analysis

| Symptom | Likely cause | Diagnostic | Safe fix | Regression test |
|---|---|---|---|---|
| Pod cannot access API after automount disabled | Workload genuinely needs API or token source changed | Review documented API calls and projected token config; never print token | Dedicated SA and narrow grant, or keep token disabled if unnecessary | Positive API-required test; negative unrelated-resource access |
| Pod can access API despite expected NetworkPolicy | CNI does not enforce policy or route differs | Verify CNI/version and test exact route/port | Supported CNI enforcement; document residual paths | Repeat connectivity test from selected and positive-control Pods |
| `kubectl auth can-i --as` fails | Caller lacks impersonation permission or identity syntax is wrong | Inspect error and caller authorization | Request approved least privilege or use fixture audit | Confirm impersonation succeeds only for authorized caller |
| Audit flags intentional privileged binding | Allow-list absent or exception too broad | Verify owner, purpose, expiry, scope | Narrow named exception and review date | Allowed binding is excepted; similar unknown binding is flagged |
| Audit misses inherited/indirect permission | Snapshot incomplete or checker is heuristic | Compare all bindings and external IAM/trust paths | Extend adapter/graph and use provider-side effective authorization checks | Add regression fixture for missed path |
| Projected token expires or has unexpected audience | Consumer refresh/audience mismatch | Verify source and expected audience with approved diagnostics | Align audience and supported refresh behavior | Intended audience succeeds; wrong audience fails |
| Trust linter assumes wrong claim | Provider/version mismatch | Compare policy with official provider documentation | Provider-specific adapter and versioned fixtures | Wrong/missing `sub` and `aud` fail |
| Rotation breaks consumer | App does not reload credential/certificate | Inspect consumer reload behavior and drill timeline | Add reload/restart orchestration; overlap only if supported | Rotate in disposable service and verify recovery |
| Old credential remains valid | Old material not revoked or verifier caches it | Test old synthetic credential against intended verifier | Disable old trust path and verify backend semantics | Old credential rejected where supported |
| Revocation not immediate | Token type, expiry, cache, issuer, verifier | Identify credential class and validation path | Contain access, rotate downstream credentials, document expiry window | Test actual validator; do not claim immediate revocation without proof |
| JIT binding not cleaned up | Reconciler/ledger failure | Compare ledger and live binding/audit | Idempotent cleanup, retry and owner alert | Inject cleanup failure in fixture and verify alert/retry |
| Audit logs missing/delayed/sensitive | Audit policy/backend/retention issue or unsafe logging | Compare known test events with sink; search only fake markers | Restore collection, redact; rotate if real secret exposed | Event-count and redaction test |
| Operator chart requests excessive RBAC | Defaults too broad or API needs undocumented | Render pinned chart and inspect RBAC objects | Narrow roles, ask owner/vendor, test reconciliation | Upgrade diff plus audit regression test |
| Access review suggests unused permission removal | Observation window missed rare use | Check coverage, release/DR paths, owner | Low-confidence staged removal and rollback | Test rare/DR workflow before removing |
| Honeytoken false positive/no alert | Expected fixture activity or event routing gap | Inspect source event and rule logic | Scope honeytoken and verify routing | Positive and negative event fixture tests |
| WSL2/kind/CNI lacks feature | Runtime/kernel/network plugin difference | Record versions and inspect official support | Supported local setup or offline fixture fallback | Rerun same test after environment change |

Prioritize evidence preservation, containment, least-risk repair, and regression tests. Do not permanently disable a security control as the normal repair.

### 6.11 Self-check questions

1. Why is a private network insufficient as a security perimeter?
2. Distinguish ServiceAccount, Role, and RoleBinding.
3. Why can `kubectl auth can-i --as=...` fail even when the target has permissions?
4. Why is broad `get/list/watch secrets` risky?
5. Does a short-lived projected token prevent abuse by compromised application code?
6. Why is “not observed in logs” not proof that a permission is unnecessary?
7. What does the identity graph prove—and not prove?
8. Why verify both new-credential success and old-credential rejection?
9. Why test NetworkPolicy against the actual CNI?
10. What differs between a JIT ledger expiry and a live RoleBinding being removed?

#### Answer key and tempting wrong answers

1. **Identity + authorization + audit are required.** Internal workloads can be compromised. *Tempting wrong answer:* private IPs are trusted; network location does not identify the caller or constrain permissions.
2. **ServiceAccount is a principal, Role defines permissions, RoleBinding associates subjects with a role.** *Tempting wrong answer:* the binding contains the permission rules.
3. **The caller needs impersonation authorization.** A denial may be about the caller, not the target. *Tempting wrong answer:* the target has no permissions.
4. **Broad Secret access widens credential exposure.** *Tempting wrong answer:* base64 means encrypted; it does not.
5. **No.** It narrows the replay window but valid permissions can still be abused. *Tempting wrong answer:* expiry neutralizes code execution.
6. **Logs may be incomplete and rare paths may be absent.** *Tempting wrong answer:* no event means no use.
7. **It finds paths in the modeled graph.** It cannot prove graph completeness or full Kubernetes authorization. *Tempting wrong answer:* a shortest path proves exploitability.
8. **Rotation is incomplete if consumers fail or old material remains accepted.** *Tempting wrong answer:* changing a file is enough.
9. **NetworkPolicy depends on CNI enforcement.** *Tempting wrong answer:* creating the object blocks packets automatically.
10. **The ledger is a simulation; a live binding must be removed by a real reconciler.** *Tempting wrong answer:* RoleBindings expire automatically.

### 6.12 Evidence artifacts

Create the following inside the learner's lab workspace only; this module does not create sidecar files.

```text
evidence/unit-06/
├── versions.txt
├── architecture-review.md
├── identity-inventory.csv
├── lab-01/{clean-report.json,defect-report.json,tests.txt}
├── lab-02/{attack-path.json,tests.txt}
├── lab-03/{policy-preview-tests.txt,trust-lint-tests.txt}
├── lab-04/{synthetic-alerts.txt,timeline.csv,containment-notes.md}
├── lab-05/{rotation-inventory.json,rotation-timings.csv,verification-results.md}
├── lab-06/{posture-snapshot.json,posture-report.json,trend.csv}
├── lab-07/{jit-ledger-before.json,jit-ledger-after.json,tests.txt}
├── lab-08/{network-policy.yaml,enforcement-result.md}
├── lab-09/{access-review.json,review-decisions.md}
└── lab-10/{operator-rbac-review.md,least-privilege-proposal.yaml}
```

#### Synthetic identity graph result

```json
{
  "status": "SYNTHETIC_EXAMPLE_NOT_EXECUTED",
  "start": "pod:etl-worker",
  "target": "asset:production-db",
  "path": ["pod:etl-worker","sa:pipeline/etl-worker","binding:all-workloads","role:read-secrets","permission:get-secrets","secret:data-prod/db-credentials","asset:production-db"],
  "cut_edge_candidates": ["narrow/remove broad binding","split shared identity","remove unnecessary Secret permission","restrict access to sensitive Secret"]
}
```

This is an illustrative result, not a run output. Your graph script emits the concrete candidate edge list; validate candidates with owners and alternative paths.

#### Decision record template

```markdown
# Identity Architecture Decision Record
- Decision ID / date (UTC):
- Owner / approver / status:
- Workload and business purpose:
- Assets and data sensitivity:
- Principals and credential types:
- Trust boundaries (issuer / subject / audience / environment):
- Current permissions and effective-scope evidence:
- Attack paths considered:
- Options and trade-offs:
- Decision and rationale:
- Positive / negative tests:
- Rotation/revocation readiness:
- Monitoring and audit coverage:
- Break-glass/JIT:
- Exceptions (owner, reason, expiry, compensating control):
- Residual risk:
- Review date / revisit trigger:
```

#### Tool inventory template

```text
date_utc=<actual UTC timestamp>
os=<actual OS/release>
kernel=<actual kernel>
python=<actual python3 --version>
kubectl_client=<actual version or not-installed>
kubernetes_server=<actual version or not-used>
kind=<actual version or not-installed>
cni=<actual plugin/configuration or unknown>
audit_log_source=<actual source or synthetic-fixture-only>
identity_audit_tests=<pass/fail/not-run>
graph_tests=<pass/fail/not-run>
jit_tests=<pass/fail/not-run>
```

Never include token bytes, Secret data, private keys, live identity-provider payloads, or production identifiers.

### 6.13 Common interview and design-review questions

1. **Why is identity a primary security perimeter?** Network boundaries constrain reachability, but compromised workloads can run inside them. Identity/authorization scope actions and audit attributes activity; legitimate permissions can still be abused.
2. **How review a ServiceAccount that reads Secrets cluster-wide?** Enumerate bindings/rules, scope and target resources, validate need with owners, narrow grant, rotate potentially exposed credentials, test cross-namespace denial, and alert on unusual Secret reads.
3. **Does deleting/recreating a ServiceAccount revoke a stolen token?** Not universally or instantly. Token type, expiry, issuer, verifier, cache, and cluster behavior matter. Contain, identify token type, rotate downstream credentials, and verify denial before claiming revocation.
4. **How derive least-privilege RBAC from audit logs?** Treat observed actions as evidence, validate with owners/tests, and remove grants incrementally. Absence of events may reflect missing coverage or rare paths.
5. **What makes rotation production-ready?** Inventory owner/consumers, replacement/reload, new-credential positive test, old-credential rejection where supported, emergency revoke, rollback, monitoring, and a measured drill.
6. **What if a workload needs no Kubernetes API access?** Disable automount, test application behavior, restrict egress where feasible, and validate CNI enforcement; do not confuse no token mount with all API paths blocked.
7. **How manage an operator with cluster-admin?** Review rendered permissions, narrow groups/resources/verbs and namespaces, test upgrades, monitor API actions, and track an owner/expiry for any exception.
8. **What must JIT access guarantee?** Requester, reason, scope, deadline, approval, audit, idempotent expiry, cleanup-failure alert, and proof of removal. Do not assume built-in RoleBinding TTL.
9. **How tune identity-abuse detection?** Define event coverage, positive/negative fixtures, adjudicate alerts, track precision/recall and gaps, and route to owners. Do not suppress a noisy high-risk rule without risk review.
10. **What distinguishes a local audit from a production posture program?** Local code validates a bounded schema/test corpus; production also needs complete inventories, provider-specific semantics, effective authorization, owners, access reviews, exceptions, telemetry, and drills on actual versions.

### 6.14 Sources and verification notes

Primary documentation consulted:

1. **Kubernetes — Service Accounts.** Kubernetes project. https://kubernetes.io/docs/concepts/security/service-accounts/ — ServiceAccount assignment, token automounting, projected/TokenRequest tokens, and long-lived token Secret cautions. Verify behavior for the actual server version.
2. **Kubernetes — RBAC Authorization.** Kubernetes project. https://kubernetes.io/docs/reference/access-authn-authz/rbac/ — Role/ClusterRole, bindings, and authorization semantics.
3. **Kubernetes — Auditing.** Kubernetes project. https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/ — `audit.k8s.io` event model and log/webhook backend concepts; availability depends on control-plane configuration.
4. **Kubernetes — Network Policies.** Kubernetes project. https://kubernetes.io/docs/concepts/services-networking/network-policies/ — a network plugin must enforce NetworkPolicy.
5. **Kubernetes — Using Node Authorization.** Kubernetes project. https://kubernetes.io/docs/reference/access-authn-authz/node/ — node authorization and NodeRestriction; verify exact configuration.
6. **Kubernetes — Admission Controllers.** Kubernetes project. https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/ — admission concepts and NodeRestriction references.
7. **HashiCorp Vault — JWT/OIDC auth and audit devices.** HashiCorp. https://developer.hashicorp.com/vault/docs/auth/jwt and https://developer.hashicorp.com/vault/docs/audit — awareness/handoff only; no live Vault required.
8. **AWS — Configure the instance metadata service.** AWS. https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html — provider-specific metadata awareness; do not generalize to other clouds.
9. **Cilium — Network policy.** Cilium project. https://docs.cilium.io/en/stable/security/policy/ — optional local CNI awareness; verify installed CNI/version.
10. **Course handoffs:** M03 RBAC/ServiceAccounts/PSS; M04 NetworkPolicy/mTLS/TLS; M06 Unit 8 operator/chart RBAC; M08 Unit 6 identity-as-code/drift; M09 Units 1, 2, 3, 6, 7, 8, 10; M10 incident command; M11 observability; M12 Units 4, 5, 7, 8, 11, 12; M14/M16 multi-cluster governance.

#### Version verification procedure

```bash
kubectl version --client
kubectl version -o yaml
kubectl config current-context
kubectl get nodes -o wide
kubectl get networkpolicy -A
```

If a command fails due to missing permission/tool, record that rather than inferring a feature is absent. Check official documentation for the actual server version and CNI. For NodeRestriction, verify control-plane plugin configuration through the supported administrative path. For audit events, verify policy/backend/retention/coverage. For cloud claims/metadata, check the actual provider's docs. Never retrieve, decode, or print a live bearer token to verify behavior.

### Author’s Verification and Completeness Audit

Status meanings: `PASS` means concrete content and supporting code/fixture/test exist; `PARTIAL` means simulation or live environment validation remains; `VERIFY` means a current environment-specific detail is unresolved. Content PASS does not mean a live production control was executed.

| Requirement | Evidence location | Validation performed | Status | Limitation / follow-up |
|---|---|---|---|---|
| 1. Correct title/Unit 6/filename | Title and metadata | Compared with prompt | PASS | Exact filename is correct. |
| 2. Verbatim handoff | §6.14 | Compared to required text | PASS | Exact wording included. |
| 3. M09 reused without re-teaching | §§6.0, 6.4, 6.14 | Scope review | PASS | Mechanism implementation remains M09. |
| 4. L1 identity perimeter/types/classes/attack paths | §§6.0–6.3 | Content cross-check | PASS | Specific behavior remains version-sensitive. |
| 5. L2 audit and dangerous grants/mounts | Lab 1 | Script/tests/fixture corpus included | PARTIAL | Execute all tests locally; not a full RBAC engine. |
| 6. Hygiene/rotation/abuse detection | §§6.4, Labs 4–5 | Content and code review | PARTIAL | Live revocation/rotation not run. |
| 7. Architecture review and identity graph | §6.5, Lab 2 | Checklist and analyzer included | PASS/PARTIAL | Graph depends on input completeness. |
| 8. Shortest path/cut-edge recommendations/tests | Lab 2 | Code and tests included | PARTIAL | Must execute tests before use. |
| 9. Policy preview/Unit 8/11 boundary | Lab 3 | Positive/negative tests included | PASS/PARTIAL | Not live admission engine. |
| 10. Trust-policy lint `sub`/`aud` | Lab 3 addendum | Linter and tests included | PASS/PARTIAL | Provider-specific adapter remains `[VERIFY]`. |
| 11. Metadata/SSRF/API restriction/CNI | §§6.5, Lab 8 | Official docs checked, fallback described | PARTIAL | Actual CNI enforcement must be measured. |
| 12. Node identity/NodeRestriction/operator review | §6.5, Lab 10 | Official docs and synthetic fixture | PARTIAL | Control-plane configuration/real chart unverified. |
| 13. ML data-plane identity/egress | §6.5 | Content review | PASS | External IAM not configured locally. |
| 14. Rotation readiness/SLO/role change/departure/emergency | §§6.4, 6.6, Lab 5 | Four types and timing plan included | PARTIAL | Actual timings require learner execution. |
| 15. JIT expiry/audit/tests | Lab 7 | Ledger and tests included | PARTIAL | Ledger simulation, not live RoleBinding. |
| 16. L4 posture/access review/detection/incidents/governance | §6.6 | Content cross-check | PASS/PARTIAL | No live multi-tenant environment. |
| 17. All ten labs complete | §6.10 Labs 1–10 | Ten lab sections and rubrics present | PASS/PARTIAL | Live cluster features optional/unverified. |
| 18. Audit script ≥10 defects/tests/reports | Lab 1 | Clean fixture produced 0 findings; defect fixture produced 16 findings across IDs ID001–ID013; audit tests passed in the 49-test suite | PASS/PARTIAL | Heuristic checker; run on sanitized learner snapshots and review its limits. |
| 19. Four credential types rotation | Lab 5 | Registry/signing/DB/TLS types included | PASS/PARTIAL | Actual time measurements not produced here. |
| 20. Posture metrics/M11 fallback | Lab 6 | Script, tests, bounded metric guidance | PASS/PARTIAL | M11 integration not run. |
| 21. Access review/operator review | Labs 9–10 | Report/test and synthetic manifest | PASS/PARTIAL | Live chart rendering optional. |
| 22. SRE/security/checklist/troubleshooting | §§6.7–6.9 and troubleshooting table under §6.10 | Content included | PASS | Live failure behavior remains environment-dependent. |
| 23. Self-check answer key and five senior questions | §§6.11, 6.13 | 10 self-check and 10 interview questions | PASS | None. |
| 24. Evidence/rubric/review/decision record | §6.12 and lab rubrics | Proposed evidence tree/templates | PASS/PARTIAL | Evidence files are not created separately. |
| 25. Zero-budget/WSL2/native/offline/cleanup | Metadata, §6.10 | Constraints included | PASS/PARTIAL | Actual laptop/tool availability must be measured. |
| 26. All cross-module handoffs | §6.14 | Four-column table and statement included | PASS | None. |
| 27. Official sources or `[VERIFY]` | §6.14 | Official Kubernetes/Vault/AWS/Cilium URLs included | PASS/PARTIAL | Check current docs for actual versions. |
| 28. No fabricated versions/claims/incidents/output | Throughout | Static review | PASS | Samples labeled synthetic/illustrative. |
| 29. No real credentials/tokens/external targets | All labs | Safety review | PASS | Maintain the same safety boundary. |
| 30. Markdown/code integrity | Whole file | 49 unit tests passed; 22 extracted Python snippets syntax-compiled; required headings/order, ten labs, exact handoff, and even fence count checked | PASS/PARTIAL | Live Kubernetes/CNI/provider integration remains unexecuted. |
| 31. Only target file created | Delivery | Target path absent before creation | PASS | No sidecar files intended. |

#### Completion verdict

The final local validation executed **49 Python unit tests with zero failures or errors** across the audit checker, graph analyzer, policy preview, synthetic event detector, rotation inventory, posture metrics, JIT ledger and mocked live-JIT guard, access review, and trust-policy linter. The clean audit fixture returned zero findings; the planted-defect fixture returned 16 findings across all 13 implemented finding IDs. All 22 extracted Python snippets syntax-compiled, and the required section order, ten labs, exact handoff statement, and Markdown fence balance were checked. These tests validate local code and synthetic inputs, not a live Kubernetes cluster.

Remaining `[VERIFY]` items are actual Kubernetes/kind/CNI versions, NetworkPolicy enforcement, projected-token and revocation semantics, control-plane audit coverage, provider-specific `sub`/`aud` claims and metadata protections, and live JIT binding cleanup. Local fixtures prove logic over the modeled schema, not production identity-provider or cluster behavior.
