# Multi-Cluster GitOps and Config Propagation

> Module: M14 | Stage: 2E — Production DevOps & Platform Engineering | Unit: 3

This unit teaches how one reviewed desired state is propagated safely to a fleet of Kubernetes clusters. It assumes completion of M08 GitOps, M09 identity/secrets, M10 SRE, M11 observability, M12 supply-chain security/admission, and M13 backup/DR. The main lab uses one Argo CD hub on `stage2e-east-lab`, registering `stage2e-west-lab`. Flux is comparison-only or must be tested in a separate environment. These two local kind clusters are not two real regions and cannot prove regional resilience.

## Module metadata

| Field | Value |
|---|---|
| Target filename | `03-multi-cluster-gitops-and-config-propagation.md` |
| Prerequisites | Stages 0–2D and Stage 2E M01–M13; especially M08–M13 |
| Estimated study time | 24–36 hours, including lab execution and evidence review |
| Review date | 2026-10-29; supplied prompt/roadmap reviewed and selected official docs consulted |
| Tool baseline | Pin Kubernetes/kind, Argo CD, ApplicationSet, CLI, Kustomize, and policy-engine versions before execution; version-sensitive syntax is `[VERIFY]` unless explicitly source-checked |
| Core tools | kind, kubectl contexts, Git, Argo CD, YAML tooling, Python 3 standard library |
| Awareness tools | Flux, Rancher Fleet, Karmada, Open Cluster Management, cloud fleet products |
| Profiles | `Fleet-Core`: two clusters/contexts/guards. `Fleet+GitOps`: adds one Argo CD hub and a tiny app. `Fleet+Data`: reserved for later units and not required here |
| Clusters touched | Only `stage2e-east-lab` and `stage2e-west-lab` in runnable instructions |
| Destructive labs | LAB-05 deletion behavior and LAB-06 hub stop/rebuild; disposable resources only, with preflight, preview, abort criteria and cleanup |
| Execution status | No cluster or Kubernetes manifest was applied. After drafting, the embedded offline Python test snippets were extracted to a temporary workspace and 12 tests passed; this does not validate live controller behavior or manifest schemas. |

## Table of contents

1. Handoff from M08 and why fleet GitOps is different
2. Learning objectives
3. Prerequisites, lab environment, and safety contract
4. Concept map and vocabulary
5. Level 1 — Beginner: fleet GitOps foundations
6. Level 2 — Intermediate: fan-out and controlled rollout
7. Level 3 — Advanced: production fleet GitOps
8. Level 4 — Expert: fleet operations under failure
9. SRE lens
10. Security lens
11. Production-readiness checklist
12. Hands-on lab set
13. Self-check questions
14. Evidence artifacts and suggested lab repository layout
15. Senior interview and design-review questions
16. What this unit teaches vs. what other modules own
17. Sources and verification notes
Appendix A — Complete lab files
Appendix B — Ordered execution, rollback, and cleanup
Appendix C — Requirement traceability audit
Appendix D — Claim Register and unresolved verification
Appendix E — Truthful execution statement

## 1. Handoff from M08 and why fleet GitOps is different

*M08 taught GitOps for one cluster — controllers, Applications/Kustomizations, repository layouts, environment promotion by digest, drift handling, secrets-by-reference, and evidence — and explicitly deferred multi-cluster delivery to this module ("agent per cluster vs hub — Awareness, forward ref M14"). This unit teaches **how one Git source of truth is propagated safely to many clusters**: hub-and-spoke vs per-cluster agents, cluster registration and credentials, ApplicationSet-style fan-out, ring/wave rollouts across clusters, per-cluster configuration, and the failure semantics of the management plane — without re-teaching M08's single-cluster mechanics.*

One merge can now affect multiple clusters, namespaces, teams and dependencies. The core problem is not just applying the same YAML everywhere; it is proving *which* targets are eligible, *what* version they receive, *in what order*, *which health evidence* allows promotion, and *how propagation halts* when a target is unhealthy or unknown. The running example is a stateless inference API deployed to two logical lab clusters. Cross-cluster networking, DNS failover, regional data replication and fleet dashboards belong to later M14 units.

## 2. Learning objectives

- **L1:** explain hub/push and agent/pull; identify credential location, network direction and management-plane failure behavior; distinguish source acceptance, sync, health and convergence.
- **L2:** operate one Argo CD hub on east, register west with constrained permissions, target only approved lab clusters, and verify each target independently.
- **L2:** apply per-cluster overlays and a shared baseline; implement ring rollout with health gates and automatic halt; demonstrate a bad canary that does not advance to ring 1.
- **L2/L3:** create a fan-out impact report; test ApplicationSet deletion risk; audit least privilege and admission enforcement; prevent CRD/operator skew with capability metadata.
- **L3:** design repository governance, deterministic configuration inheritance, tenancy boundaries, conformance quarantine, drift checks and staged promotion.
- **L4:** define fleet GitOps SLIs/SLOs, use incident runbooks, onboard/offboard clusters safely, separate author/approver/promoter, and write an evidence-based hub/agent ADR.

Completion is evidence-based. An authored script is not a passed test; an Application marked `Synced` is not proof that the service works; a lab result is not production assurance.

## 3. Prerequisites, lab environment, and safety contract

### 3.1 Resource-aware profiles

Do not run every platform component at once on an 8 GB laptop. Measure your own machine; these profiles are sequencing guidance, not guaranteed resource estimates.

| Profile | Start | Stop | Purpose |
|---|---|---|---|
| `Fleet-Core` | two small kind clusters, contexts, guard scripts | unrelated workloads | context safety, offline selector/impact tests |
| `Fleet+GitOps` | `Fleet-Core` plus one Argo CD hub on east, local Git source if needed, tiny app | unrelated Git server/app after evidence capture | primary labs |
| `Fleet+Data` | not needed here | keep stopped | reserved for later M14 traffic/data labs |

Two clusters plus Argo CD, observability, a replicated database and cross-cluster networking can exceed the budget. This unit needs only the minimum GitOps profile. Never run Argo CD and Flux against the same resources in the same lab environment.

### 3.2 Preflight and context guard

```bash
kubectl config get-contexts
kubectl --context stage2e-east-lab cluster-info
kubectl --context stage2e-west-lab cluster-info
kubectl --context stage2e-east-lab get nodes -o wide
kubectl --context stage2e-west-lab get nodes -o wide
```

If a context is missing, resolves to an unexpected cluster, or could be production, stop. Never repair an ambiguous context by guessing or copy a production kubeconfig into the lab.

```bash
#!/usr/bin/env bash
# scripts/kubectl-lab.sh — guard only; still review every mutation.
set -euo pipefail
if [[ $# -lt 2 || "$1" != "--context" ]]; then
  echo 'usage: kubectl-lab.sh --context stage2e-east-lab|stage2e-west-lab <kubectl args...>' >&2
  exit 64
fi
ctx="$2"; shift 2
case "$ctx" in stage2e-east-lab|stage2e-west-lab) ;; *) echo "refusing non-lab context: $ctx" >&2; exit 65 ;; esac
printf 'TARGET CONTEXT: %s\nCOMMAND: kubectl --context %q' "$ctx" "$ctx" >&2
printf ' %q' "$@" >&2; printf '\n' >&2
exec kubectl --context "$ctx" "$@"
```

This wrapper is not a safety guarantee: it cannot verify that kubeconfig maps a context to the expected cluster. Confirm identity separately.

### 3.3 Safety contract

1. Use only `stage2e-east-lab` and `stage2e-west-lab` for runnable cluster operations.
2. Name `--context` explicitly, print the target before a mutation, and verify it afterward.
3. Destructive tests are disposable-lab-only; require preflight, preview/dry-run where supported, typed confirmation, abort criteria and post-check.
4. Never use production credentials or commit tokens, kubeconfigs, passwords, private keys or rendered Secret values.
5. Never run an unguarded broad delete, prune or ApplicationSet change against unknown infrastructure.
6. Use one GitOps controller in the main environment: Argo CD. Flux is guided analysis or a separate environment.
7. Reuse the M12 policy engine; do not install multiple policy engines for this unit.
8. Missing/stale capability data, unknown targets or an unexpectedly broad selector means fail closed.
9. Outputs in this file are illustrative/synthetic unless explicitly identified as captured. None is captured from a real run.
10. Two kind clusters share host, kernel, power, storage and often networking; they do not prove independent regions or provider control-plane resilience.

## 4. Concept map and vocabulary

```text
                 reviewed commit / immutable image digest
                                  |
                                  v
                           Git source of truth
                                  |
                    +-------------+-------------+
                    |                           |
              hub/push model              agent/pull model
           Argo CD hub on east             controller per cluster
                    |                           |
             target credentials            each agent reads Git
              /             \              /              \
             v               v            v                v
        east API          west API      east API          west API
             |               |            |                |
         workloads        workloads    workloads        workloads
```

- **Desired state:** reviewed manifests/configuration intended to be true.
- **Reconciliation:** repeated comparison and correction of observed state against desired state.
- **Registration:** destination/auth metadata known to the hub; not proof of a successful sync.
- **Application:** Argo CD resource describing a source and destination.
- **ApplicationSet:** generator/template controller that creates and updates Applications; not itself a rollout guarantee.
- **Fan-out:** one change generates work for several clusters/Applications.
- **Overlay:** controlled environment/region/cluster-specific configuration.
- **Ring/wave:** ordered cluster cohort; ring 0 is the smallest canary cohort.
- **Drift:** observed state differs from desired state.
- **Sync:** controller's assessment/action to align resources with desired state.
- **Health:** controller or application assessment; it may not prove business correctness.
- **Convergence:** every eligible target has the desired revision and passed the required health gates.
- **Blast radius:** scope of impact from one credential, change or controller action.
- **Management plane:** GitOps controllers, source, identity, policy and fleet status.
- **Data plane:** running workloads and user traffic.

The state ladder is: `commit merged → controller observed source → target generated → sync attempted → resources synced → health gate passed → service test passed → all eligible clusters converged`. These are distinct states.

## 5. Level 1 — Beginner: fleet GitOps foundations

### 5.1 The multi-cluster delivery problem

Fleet delivery must handle a shared baseline plus controlled differences, ordering and compatibility, drift repair, staged promotion, bounded blast radius, and visibility when a cluster is unreachable. Before merge, answer: which exact clusters are eligible; which immutable artifact is promoted; what dependencies must be ready; what evidence advances the next ring; what halts a rollout; and what remains observable if the hub fails?

### 5.2 Hub/push vs agent/pull

| Dimension | Hub/push | Agent/pull |
|---|---|---|
| Credentials | Hub holds target credentials; compromise can span spokes according to permissions | Each cluster holds source access/local reconciliation identity; shared Git governance can still fan out bad changes |
| Network | Hub must reach each target API endpoint | Each agent needs source reachability; routine inbound hub-to-cluster API access is not needed for the basic pull path |
| Controller down | Workloads usually keep running; central reconciliation, rollout gates and visibility degrade | One agent failure can be local; other agents can continue if source/network remain available |
| Visibility | Convenient central view, but stale targets can look deceptively healthy without freshness alerts | Local autonomy; fleet aggregation is separate work |
| Bootstrap/ops | One hub plus target registration and credential setup | Controllers/bootstrap/upgrades per cluster |
| Cost/load | Central controller/repo-server and target API connections; possible concentration point | More controller overhead distributed across clusters |
| Tenancy | Requires strong AppProject, source, destination, RBAC and generator boundaries | Local ownership may help; shared source and organization governance still matter |
| Recovery | Rebuild hub, re-register, re-adopt without prune | Rebuild/re-adopt each local agent; repeated operations |
| Good fit | Centrally governed fleet with reliable hub-to-target reachability | Edge/isolated networks, local autonomy, stronger local ownership |

A hybrid is possible: agents reconcile locally and a read-only central view aggregates status. The observation hub must truly lack write credentials. Choose based on network, credential blast radius, ownership, visibility and recovery—not fashion.

### 5.3 Cluster registration and credentials

Registration binds a stable cluster name, API endpoint, authentication configuration and optionally labels/project metadata. Argo CD supports CLI and declarative registration workflows. Exact behavior of `argocd cluster add`, target ServiceAccount permissions, token lifecycle and Secret shape depends on the chosen version/configuration and must be checked before execution `[VERIFY]`.

Argo CD's declarative setup documents cluster Secrets labelled `argocd.argoproj.io/secret-type: cluster`, with fields such as `name` and `server`. Never commit credential data. Prefer the approved M09 secret/identity process; rotate/revoke credentials and retain a break-glass path independent of the hub. Use short-lived credentials where the selected auth integration supports them, and verify renewal behavior `[VERIFY]`.

Distinguish `destination.name` (registered identifier) from `destination.server` (API endpoint). An Application destination should use one, not both. Labels on registered cluster metadata become a targeting API: a label mistake can become a fleet-wide routing mistake.

A `cluster-admin` identity on every spoke makes hub compromise a fleet-wide administrative incident. The required negative test is that the west hub identity cannot list/get Secrets cluster-wide and cannot write to forbidden namespaces. Verify `kubectl auth can-i` identity/impersonation flags against the installed Kubernetes version; a check run as the learner's admin identity does not prove the hub identity is constrained.

### 5.4 Fleet repository structure

Illustrative layout only; not a claim about the learner's existing repository:

```text
gitops/
├── clusters/
│   ├── stage2e-east-lab/{kustomization.yaml,applicationset.yaml}
│   └── stage2e-west-lab/kustomization.yaml
├── fleet/{cluster-registry.json,rings.json,capability-matrix.json}
├── platform/{namespaces,quotas-network-policy,policy,observability,baseline}/
└── apps/sample-api/
    ├── base/{deployment.yaml,service.yaml,kustomization.yaml}
    └── overlays/{east,west}/
```

`clusters/<cluster>/` is a small entry point; `platform/` holds shared baseline components; `apps/<app>/base` holds common intent; overlays hold minimal justified differences; `fleet/` stores non-secret inventory, ring membership and capabilities. Directory-per-cluster is explicit but can duplicate content. Generated targets reduce copy/paste but raise selector and preview risk.

Use branch protection, repository ownership/review rules and signed commits/tags where supported. Promote immutable image digests; retain commit, digest, approval, target set, ring and health evidence. Every cluster-specific override needs an owner, reason, review/expiry date and test. A recommended precedence convention is `global defaults → environment/region → cluster → ring override`; it is not an Argo CD intrinsic. Test rendered results rather than relying on filenames to imply precedence.

### 5.5 Desired state, sync state, health and convergence

A merge may not yet be observed by the controller; an ApplicationSet may generate east but not west; west may be unreachable; a Deployment may be synced but unhealthy; pods may be healthy while the service is broken. For each cluster record desired commit/digest, generated Application/destination, sync revision/result, health/reason, independent `kubectl --context` state, service smoke-test result, and any exclusion/unreachable reason. Never hide an unreachable cluster from the denominator without explicit reason and timestamp.

### 5.6 What happens when the hub is down

A hub outage does not automatically stop already-running workloads. It degrades reconciliation, rollout coordination and central visibility; drift may remain unrepaired and new desired state may remain unapplied. Exact behavior depends on installed components/configuration. Recover the management plane and verify it does not prune or replace existing resources. The lab hub is intentionally on east to make the dependency visible; production may host management services separately or use agents.

### 5.7 Common beginner mistakes

- Treating registration as proof of health/convergence.
- Using broad or empty selectors.
- Confusing ApplicationSet generation with rollout ordering.
- Equating `Synced` with service correctness.
- Granting cluster-admin for convenience.
- Removing a label without previewing generated Application deletion.
- Calling two local kind clusters “two regions.”
- Running two GitOps controllers against the same resources.
- Promoting mutable tags or claiming synthetic output is measured.

## 6. Level 2 — Intermediate: fan-out and controlled rollout

### 6.1 Argo CD hub-on-east architecture

Install one Argo CD instance on `stage2e-east-lab`, register `stage2e-west-lab`, and deploy one tiny app to both. West's target identity is constrained; east-local administrative permissions are separate. Use an isolated Git source. Preview actual generated targets before enabling sync. The local cluster may not have the same cluster Secret metadata as remote clusters; selector/local-cluster behavior is version-sensitive `[VERIFY]`.

```text
Git commit → Argo CD/ApplicationSet on east
                    ├─ ring 0: stage2e-east-lab
                    └─ ring 1: stage2e-west-lab (only after gate/approval)
```

### 6.2 ApplicationSet fan-out

An ApplicationSet generator produces parameters and a template renders Applications. Cluster generators use registered cluster metadata; list generators represent explicit sets; Git-directory generators derive targets from repository directories; matrix generators combine outputs. More flexibility means more ways to widen the target set accidentally.

Safe workflow: **preview target set → compare allow-list → review diff → sync approved ring → independently verify targets**. ApplicationSet is not inherently ordered. Current Argo CD documentation describes Progressive Syncs/RollingSync as beta since v3.3.0; verify availability, feature flags and behavior for the installed version. If not verified, use the deterministic script-level gate in Appendix A and label it external orchestration, not native Argo CD behavior.

### 6.3 Labels, selectors, destinations and target safety

Labels must represent eligibility, not merely description. Require lab identity, environment, ring, compatibility and conformance; missing values fail closed. Example offline registry:

```json
{
  "allowed_clusters": ["stage2e-east-lab", "stage2e-west-lab"],
  "clusters": [
    {"name":"stage2e-east-lab","server":"https://east.invalid","env":"lab","region":"east","ring":"canary","tier":"0","conformant":true,"capabilities":["apps-v1"],"namespace_allowlist":["sample-api"]},
    {"name":"stage2e-west-lab","server":"https://west.invalid","env":"lab","region":"west","ring":"stable","tier":"1","conformant":true,"capabilities":["apps-v1"],"namespace_allowlist":["sample-api"]}
  ]
}
```

`.invalid` endpoints are placeholders. The offline registry is not a substitute for inspecting actual Argo CD cluster entries and generated Applications. Appendix A's analyzer fails on empty selectors, missing required labels, unknown clusters, namespace expansion and deletion risk, but it does not emulate the controller.

### 6.4 Per-cluster overlays and inheritance

Kustomize overlays or Helm values express small, justified differences while reusing a base. Example:

```yaml
# apps/sample-api/overlays/east/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: sample-api
resources:
  - ../../base
patches:
  - path: replica-patch.yaml
```

```yaml
# apps/sample-api/overlays/east/replica-patch.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sample-api
spec:
  replicas: 1
```

Use the same immutable image digest across overlays unless an approved promotion explicitly changes it. Lint override sprawl, track owners/expiry, and produce a cluster diff from the shared baseline. Secrets are referenced through M09's approach; never put Secret values in overlays.

### 6.5 Platform baseline and dependency ordering

Baseline components may include namespaces, quotas, NetworkPolicies, admission policy, observability agents, certificate automation, operators and application prerequisites. CNI/CSI, bootstrap add-ons, CRDs and some operators may belong to Unit 2's cluster lifecycle process. Do not blindly reinstall a CNI through GitOps.

Recommended order, adapted to the platform: (1) cluster identity/API reachability; (2) bootstrap components and compatible CRDs; (3) namespaces/quotas/network policy; (4) policy baseline; (5) observability and deployment markers; (6) operator readiness; (7) application; (8) independent health and smoke test. Use observable readiness gates, not sleeps alone. M12 owns policy detail; M11 owns fleet aggregation.

### 6.6 Ring rollout, health gates and automatic halt

```text
Target impact report / allow-list
       | fail → STOP
       v
Ring 0: stage2e-east-lab
       | sync + health + smoke test fails → HALT / pin or revert / notify
       v pass
Manual promotion approval
       v
Ring 1: stage2e-west-lab → independent sync + health + smoke test
```

Fleet rings decide which clusters receive a revision; within-cluster canaries gradually expose traffic/replicas inside one cluster. Both layers may be needed. A gate should combine sync success, Application health and application-level smoke checks. Plant a bad readiness setting only in the disposable sample app; prove ring 1's revision remains unchanged, revert/pin the known-good version, recheck ring 0 and require explicit promotion approval. The Appendix A gate is a simulation, not native Argo CD behavior. Verify native RollingSync constraints (including automated-sync behavior) before using it in production.

### 6.7 Fan-out impact report and CI gate

Before sync, report clusters, namespaces, Applications and important resource kinds affected. Compare before/after target sets and fail if a target is outside the allow-list, selector labels are missing/empty, a forbidden tier/namespace is hit, the target set expands, deletion risk appears, or capability/conformance metadata is missing/stale. Appendix A gives deterministic JSON analysis and a human summary; add pinned Kustomize/Helm rendering and actual ApplicationSet target inspection in a real pipeline. Do not claim the offline analyzer fully renders Argo CD.

### 6.8 ApplicationSet deletion-cascade hazard and guard

ApplicationSet, generated Application and child-resource deletion are related but distinct. Official Argo CD docs explain that generated Applications have owner references and may carry the Argo CD resource finalizer; preservation settings affect whether child resources remain when Applications are deleted. Exact behavior depends on version, finalizers, sync policy and deletion path.

- `preserveResourcesOnDeletion: true` is not a universal “never delete” switch.
- `applicationsSync` governs ApplicationSet controller create/update/delete behavior; exact values/semantics are version-sensitive `[VERIFY]`.
- AppProject source/destination/kind restrictions limit deployment scope but do not replace target-set review.
- Orphaning an ApplicationSet does not automatically remove the Application's own resource finalizer.
- Removing a cluster label may remove generated Applications and can cause child-resource deletion depending on configuration.

On disposable resources only: capture generated Applications, preview the changed target list, inspect owner references/finalizers, verify current-version semantics, test a controlled label/generator change only when its effect is understood, then restore the reviewed config and verify cleanup. If semantics are unclear, stop at dry-run and mark the lab partial.

### 6.9 Hub-down and hub-rebuild

**Hub-down:** capture app state on both clusters; stop only the named disposable Argo CD controller component on east after inspecting owner/labels; verify running workloads continue; introduce harmless drift in the sample namespace and verify it is not reconciled while the controller is unavailable; record loss of central visibility; restore the hub and verify reconciliation.

**Hub-rebuild:** record source, pinned versions, config, cluster names/servers and non-secret registration metadata; rebuild from declared source; restore credentials through the approved secret process; re-register west; inspect ownership/tracking/finalizers; re-adopt without prune; verify sync, health and smoke tests independently on each target. Do not enable pruning until a reviewed no-prune adoption test passes.

### 6.10 Credential blast radius and admission verification

| Capability for west hub identity | Expected result |
|---|---|
| Required sample app resource operations in `sample-api` | Allow only needed verbs/kinds |
| Cluster-wide list/get Secrets | **Deny** |
| Writes to forbidden namespaces | **Deny** |
| Arbitrary cluster-scoped resource creation | Deny unless explicitly justified |
| Modify RBAC/admission policy | Deny for normal app deploy identity |

Use `kubectl auth can-i` with explicit `--context stage2e-west-lab` and an identity proven to match the hub credential. Verify identity/impersonation flags for the installed version. An admin-context check proves nothing about the hub identity. Reuse M12's policy engine so west rejects an unsigned/unapproved image even if the hub requests it. The policy syntax and signature verification semantics are `[VERIFY]` until matched to the chosen engine/version. Do not install multiple policy engines; keep the test in a disposable namespace and never expose secret values.

### 6.11 CRD/operator version skew

A CRD defines an API type; an operator/controller reconciles it. If a target does not serve the required API version, applying a custom resource can fail. Capability labels should include served APIs, operator/CRD versions, Kubernetes version, policy baseline and conformance. Missing/stale capability data is unknown, not compatible. Use a fixture or disposable cluster to prove a cluster lacking `example.io/v2` is excluded. Upgrade in the operator-supported order, wait for CRD/controller readiness, then apply dependent custom resources; the exact sequence is operator-specific `[VERIFY]`.

### 6.12 Fleet convergence measurement

Define merge-to-all-eligible-clusters-converged time as the interval from merge timestamp to the point every eligible cluster has reached the target revision and passed health gates. Record merge time/commit, controller observation, sync completion per cluster, health-gate completion, smoke-test completion, final convergence time, ring approvals, and excluded/unreachable targets with reason and owner. Do not calculate p50/p95 from one or two observations. Laptop timings are local simulation values, not production estimates.

### 6.13 Hub vs agent ADR

**ADR-001 — lab decision; production decision open.** Context: two logical clusters, zero-budget laptop, central review desired. Options: (A) Argo CD hub; (B) agent per cluster; (C) local agents plus read-only status hub. Select A for this unit only because it meets the learning objective and uses one controller. Trade-off: central status/controller simplicity versus credential concentration, east dependency and hub-to-west API reachability. Production evidence required: actual permissions, network path, outage tests, source outage, resource use, tenancy, recovery time and ownership. Any unmeasured overhead/scale claim is `[ASSUMPTION]`. Revisit if cluster count, isolation, network or ownership changes.

### 6.14 Optional Flux comparison

Use guided analysis or a separate disposable environment; do not run Flux with Argo CD against the same resources. Compare bootstrap, credentials, reconciliation, repo layout, visibility, outage behavior and overhead. Flux's official installation docs describe bootstrap as installing controllers and configuring Git sync; use current CLI/docs and verify supported versions/commands `[VERIFY]`.

## 7. Level 3 — Advanced: production fleet GitOps

### 7.1 Hub and agent security models

For a hub, keep a credential inventory (target, purpose, scope, owner, rotation date and revocation procedure), monitor hub actions/denials, and rehearse a compromise tabletop. Know which clusters the hub can reach, which actions the stolen identity can take, how promotion is frozen, how credentials are revoked independently, and how trusted state is re-adopted. For agents, bootstrap each cluster declaratively and keep credentials local; agents reduce central write credentials but do not eliminate source-governance risk because a bad Git change can still be pulled everywhere. Use source restrictions, branch protection, signed commits/tags where enforced, per-cluster policy and monitoring. An observation-only hub should have no write credentials. Workload identity/trust bindings belong to M09/M07. CAPI `ClusterResourceSet` and post-provision hook behavior are `[VERIFY]`, not assumed universal practice.

### 7.2 Repository governance and inheritance

Use repository boundaries matching ownership/trust. Protect `CODEOWNERS` or equivalent rules for fleet registry, selectors, policy baseline and rings. Separate author, approver and promoter for high-impact changes. Promote immutable image digests; retain commit/build provenance, approval, target report and per-ring health evidence. Use deterministic inheritance: global baseline → environment/region → cluster exception → temporary ring override. CI should reject unknown override keys, unexplained drift and expired exceptions. Break-glass changes must be audited and reconciled to Git.

### 7.3 Capability-aware targeting and CRD sequencing

Capabilities should be versioned and refreshed from evidence: Kubernetes version, served API versions, CRD/operator version, policy baseline, storage/network capabilities and conformance. A stale label can make a selector assert false compatibility. If a cluster is unreachable or metadata is unknown, quarantine it from promotion. Prefer documented capability tests and operator-supported compatibility ranges over naive string comparison. Install/upgrade CRDs and controllers in the supported sequence, wait for readiness, then apply custom resources. Test positive, negative, missing-label and stale-label cases.

### 7.4 Multi-tenancy and AppProject/ApplicationSet boundaries

AppProjects restrict source repositories, destinations, namespaces and resource kinds, but are not the entire tenancy model. ApplicationSet authoring and generator inputs are privileged: a broad generator may create Applications for unintended destinations. Protect source paths, cluster labels, project definitions and repository credentials. Audit a tenant-created ApplicationSet by rendering targets, checking source/destination/project restrictions, inspecting generated Applications, and only then enabling sync. Verify directory/cluster generator behavior for the installed version `[VERIFY]`. Use separate instances or per-cluster GitOps where shared-hub boundaries cannot meet ownership requirements.

### 7.5 Two layers of progressive delivery

| Layer | Controls | Evidence | Use when |
|---|---|---|---|
| Within-cluster rollout | replicas/traffic inside one cluster | rollout health, metrics, errors, smoke test | workload change needs gradual traffic exposure |
| Fleet rings | which clusters receive a revision and in what order | per-cluster sync, health, compatibility and approval | shared change has multi-cluster blast radius |

A low-risk config change may need a small ring and short gate; policy, operator or ingress changes may require both layers and longer observation. Do not skip a fleet ring because an app has an internal canary: they cover different failure domains.

### 7.6 Drift, conformance, unreachable clusters and quarantine

Track drift age, last successful sync, credential expiry, API reachability, policy revision and conformance freshness. Alert when a cluster silently stops syncing; distinguish failed from unknown/unreachable. Never quietly remove an unreachable cluster from the denominator. Quarantine it from promotion until independently checked. Conformance should include policy baseline, required API capabilities, identity/RBAC and application readiness. Compare hub status with independent target checks. During a drift storm, freeze propagation, find the common cause and avoid broad corrective syncs until targets are known.

### 7.7 Fleet CI and ring simulation

CI should validate YAML/schema, render Kustomize/Helm with pinned versions, validate ApplicationSet selector intent, run offline target tests, flag deletion risk, require image digests, and test the ring harness. Ephemeral kind can provide controller integration coverage, but offline tests should remain useful without a live cluster. A simulator is not a substitute for actual controller semantics; production use needs a version-pinned integration test proving generated targets, deletion behavior and halt behavior.

### 7.8 Scale, reliability and cost

Measure controller/repo-server CPU and memory, Git fetch frequency, repo size, target API latency, reconcile queue delay, retries and provider rate limits. Argo CD sharding/replicas, repo-server capacity, reconciliation intervals, webhooks and connection settings are deployment/version-dependent `[VERIFY]`. Do not quote universal cluster-count thresholds. Track convergence time, ring success, sync failure, drift age, unreachable duration, halt time and clusters affected per change. Detailed cost modeling is deferred to M15; qualitatively, hubs centralize controller capacity while agents multiply local overhead.

### 7.9 Alternatives and scope

| Option | Framing | Consideration |
|---|---|---|
| Argo CD hub | central GitOps configuration propagation | central status, concentrated credentials/network dependency |
| Flux per cluster | local pull/reconciliation | local autonomy; fleet aggregation is separate |
| Rancher Fleet | GitOps fleet management | compare current targeting/governance docs `[VERIFY]` |
| Karmada | multi-cluster application management, propagation/placement capabilities | broader than simple config sync; verify current features `[VERIFY]` |
| Open Cluster Management (OCM) | fleet governance/multi-cluster management | verify project status and policy/placement scope `[VERIFY]` |
| Cloud fleet products | provider-specific inventory/policy/network/workload features | may require paid services; awareness only here |
| KubeFed | historical federation effort | current status/suitability `[VERIFY]` |

Configuration propagation is not workload placement/scheduling. Do not introduce a fleet platform unless its extra capabilities solve a demonstrated need.

## 8. Level 4 — Expert: fleet operations under failure

### 8.1 Fleet GitOps SLIs/SLOs

Candidate service-level indicators (SLIs): merge-to-converged time, p95 convergence (only with enough real observations), ring success/failure rate, per-cluster drift age, sync failure rate, unreachable/stale duration, time to halt a bad rollout, hub recovery time and maximum clusters affected by one change. Choose objectives from service criticality, customer impact, baseline observations and error budgets; do not invent universal targets. State sample size, percentile method and how unknown clusters count. A single laptop run cannot establish a production p95.

### 8.2 Runbooks

Each incident begins by freezing further harm, determining exact affected targets, preserving evidence and communicating an owner/status. Verify each cluster independently after mitigation.

**Hub outage:** freeze promotion; confirm outage independently; inspect hub pods/events, Git and target reachability, last sync per cluster; recover declared installation; verify generated Applications, sync, health and smoke checks. Prevent with pinned versions, tested rebuild, separated failure domain and alerts.

**Target unreachable:** quarantine it and mark unknown; do not promote around the missing target; inspect API/network errors, credential age and last sync; repair connectivity/credential under change control; verify context, sync, health and capability freshness. Alert on stale sync.

**Expired credential:** freeze target eligibility; identify credential source without printing token; rotate/reissue and revoke old credential; test positive and negative RBAC; re-register only after review; monitor expiry.

**Bad change reached ring 1:** freeze propagation; enumerate actual revisions by cluster; pin/revert by ring to known-good digest; verify service state per cluster; notify incident owner; repair missing gate and test before re-promotion.

**ApplicationSet deletion cascade:** stop changes to ApplicationSet/labels; inspect generated Applications, owner references, finalizers, events and target set; do not strip finalizers blindly; restore reviewed config only after impact review; restore named resources as appropriate; add deletion-diff CI and regression test.

**CRD/operator mismatch:** halt targets missing capability; record served API/operator versions; stop retries; follow vendor/project upgrade order on canary; verify CRD establishment/controller health/resource reconciliation before promotion; add capability and skew tests.

**Drift storm:** freeze high-fan-out changes; compare drift by revision/cluster/kind/time; determine whether source, another controller or API failure caused it; avoid broad parallel sync; correct a bounded target set; add queue/drift monitoring.

**Git provider outage:** pause promotion; identify cached revision and controller behavior; preserve last known-good digest; restore source via approved procedure; verify source revision and convergence; monitor provider and test source recovery.

**Hub compromise:** freeze rollout; inventory reachable clusters, credentials and actions; revoke/rotate credentials through an independent path; preserve audit logs; rely on target policy/RBAC to limit actions; rebuild from trusted pinned source and re-adopt without prune; review source protection and blast radius.

**Emergency CVE patch:** identify artifact/capability requirements; author pins patch, independent approver reviews, promoter controls rings; run impact/security checks; expedite but retain canary and health gate; if break-glass bypass is unavoidable, record incident-command approval and reconcile to Git; review the exception afterward.

### 8.3 Hub failover and recovery

Reuse M13 recovery discipline rather than re-teaching backup/restore. Keep source, pinned controller versions, config, non-secret registration metadata and recovery steps outside the hub failure domain. Reissue credentials through approved secret management, not logs. A rebuilt hub must not prune live resources during re-adoption: inspect tracking, ownership, destinations and finalizers; keep pruning disabled until a no-prune adoption test passes. Rehearse at a defined cadence and record recovery time, drift and per-cluster verification.

### 8.4 Cluster onboarding/offboarding

Onboarding sequence: `registry entry → cluster created (Unit 2) → least-privilege credentials → registered → baseline applied → conformance verified → assigned to ring`. Check identity/API server, capabilities, namespaces/policy, admission, observability, labels, owner, rollback and a test sync.

Offboarding sequence:
1. Remove from future promotion rings.
2. Plan workload drain/migration and inspect stateful dependencies.
3. Verify current state, dependencies and owner approval.
4. Review impact before deregistering.
5. Revoke credentials independently.
6. Remove ApplicationSet membership/labels only after previewing generated Application deletions.
7. Remove managed resources only under reviewed policy.
8. Remove DNS/monitoring entries (Units 4, 5 and 8).
9. Audit orphaned credentials, Applications and registry records.
10. Verify no unintended resources/credentials remain.

Deregistering a cluster is not the same as deleting workloads. Label removal can trigger Application deletion and, depending on settings, child-resource deletion.

### 8.5 Emergency changes, break-glass and reconciliation

Separate author, approver and promoter. Use a pre-verified rollback, known-good digest, explicit target set and real health gate. Signatures help only where the toolchain enforces them; they do not replace authorization. Break-glass changes require who/what/why/where/when, evidence, target-side policy and prompt reconciliation to Git. Temporary exceptions need an owner and expiry.

### 8.6 Ten hypothetical incident analyses

These are design scenarios, not claims about real incidents. For each, preserve the stated sequence: symptom → hypotheses → safe evidence → root cause → immediate mitigation → durable prevention → residual risk.

1. **ApplicationSet change prunes Applications.** Symptom: generated apps disappear. Hypotheses: selector/generator/template change or finalizer policy. Evidence: before/after target diff, events, owner references, finalizers, Git/audit logs. Cause: no deletion-aware review. Mitigate: freeze; restore reviewed config only after preview; do not blindly strip finalizers. Prevent with impact CI, allow-list and disposable regression. Residual: privileged controller can still delete resources.
2. **Ingress annotation reaches every cluster.** Symptom: multi-cluster traffic fails. Hypotheses: broad selector, no ring gate, weak smoke test. Evidence: revision by cluster, ingress events, target list, smoke checks. Cause: fleet change treated like one-cluster change. Mitigate: freeze, revert by ring, verify each endpoint. Prevent with canary ring and traffic-specific health check. Residual: shared dependencies can still fail.
3. **Hub credential leak with cluster-admin.** Symptom: privileged changes across clusters. Hypotheses: token/log leak, compromised hub, overbroad identity. Evidence: audit logs and sanitized secret access history. Cause: fleet-wide admin credential. Mitigate: freeze, revoke via independent path, assess audit logs. Prevent with least privilege, rotation, secret scanning and reviews. Residual: repository authority can still distribute harmful desired state.
4. **Hub is hosted on failed production cluster.** Symptom: workload cluster and fleet management fail together. Evidence: placement/dependencies and independent target state. Cause: shared failure domain. Mitigate: recover hub in independent environment. Prevent with external recovery artifacts, tested rebuild or agent model. Residual: identity/source can remain common dependencies.
5. **Cluster stops syncing after token expiry.** Symptom: stale config while dashboard appears green. Evidence: last sync, credential metadata, local state, eligibility set. Cause: no stale-sync alert or denominator check. Mitigate: quarantine as unknown and renew safely. Prevent with freshness SLI and credential inventory. Residual: divergence can occur between checks.
6. **CRD v2 reaches v1-only cluster.** Symptom: custom resource fails. Evidence: served API versions, operator version, generated targets. Cause: stale/missing capability metadata. Mitigate: halt, pin compatible revision, upgrade canary in supported order. Prevent with fail-closed selector and skew fixtures. Residual: API presence alone does not prove behavioral compatibility.
7. **Emergency patch skips rings and breaks tier-0.** Evidence: approvals, promotion logs, revision per cluster. Cause: emergency path lacks guardrails. Mitigate: freeze, revert, verify critical services and communicate. Prevent with audited emergency flow and role separation. Residual: exceptional bypass may sometimes be necessary but must be documented.
8. **Tenant ApplicationSet targets another team's namespace.** Evidence: generated Application, AppProject, source revision and audit log. Cause: broad destination/project and shared generator rights. Mitigate: stop generator after preserving evidence; inspect before cleanup. Prevent with project isolation, protected paths and tenant tests. Residual: administrators remain privileged.
9. **Conformance green because unreachable clusters were skipped.** Evidence: inventory, observation time, excluded targets and raw probes. Cause: unknown treated as compliant. Mitigate: mark unknown and block promotion. Prevent with explicit denominator/freshness SLO. Residual: monitoring can fail together.
10. **Policy version mismatch silently weakens rule.** Evidence: policy-engine versions, admission test, status/schema. Cause: assumed portability across versions. Mitigate: halt incompatible clusters and restore supported policy. Prevent with capability labels, negative tests and version matrix. Residual: policy semantics change; regression tests remain necessary.

### 8.7 Scale and governance operating model

Name owners for registry, credentials, ApplicationSets, baseline policy, ring promotion, hub recovery and incident communications. Define who can freeze/unfreeze promotion. Treat selector and capability changes as privileged control-plane code. Retain evidence long enough to investigate delayed failures; governance should scale with criticality and fan-out.

## 9. SRE lens

Treat fleet GitOps as a delivery service. Track merge-to-converged time, sync failure, drift age, unreachable duration, ring health, bad-change halt time and clusters affected per change. State denominator and unknown handling. A ring gate is valuable only if the canary is representative, health signal meaningful, halt hard and revert tested. Combine controller status with workload readiness and application checks. Rehearse runbooks on disposable clusters.

## 10. Security lens

- Minimize hub credentials and constrain namespaces/resource kinds.
- Treat registry labels, ApplicationSet sources and ring config as privileged inputs.
- Enforce target-side admission as an independent trust boundary.
- Keep credentials out of Git, logs, artifacts and screenshots.
- Separate app deploy rights from RBAC, policy, CRD and cluster-scoped changes.
- Protect branches/promotion records and use signatures where enforced.
- Make stale/unknown/unreachable targets ineligible for high-risk promotion.
- Audit rotation/revocation, not only initial registration.
- Do not treat a selector, AppProject or preservation field as a universal safety guarantee.

## 11. Production-readiness checklist

- [ ] Both contexts and cluster identities verified; only named lab targets used.
- [ ] Argo CD/ApplicationSet versions pinned.
- [ ] Actual generated target set matches reviewed allow-list.
- [ ] Credential scopes documented; no secrets in Git.
- [ ] West identity denied cluster-wide Secret reads and forbidden writes.
- [ ] AppProject source/destination/resource restrictions tested.
- [ ] Admission policy rejects the unapproved-image negative test.
- [ ] Overlays deterministic and rendered with pinned tooling.
- [ ] Capability metadata fresh; unknown fails closed.
- [ ] Baseline dependencies and readiness gates documented.
- [ ] Ring-0 failure prevents ring-1 advancement in the chosen orchestration layer.
- [ ] Impact report detects target expansion, missing labels, namespace expansion and deletion risk.
- [ ] Deletion semantics verified on disposable resources against installed version.
- [ ] Hub-down/rebuild distinguishes workload continuity from reconciliation/visibility.
- [ ] Re-adoption proven without prune.
- [ ] Convergence includes per-cluster timestamps and explicit exclusions.
- [ ] Runbooks cover the ten incident classes and have owners.
- [ ] Evidence has no credentials and labels synthetic output.
- [ ] Human reviewer reran integration checks with installed versions.

## 12. Hands-on lab set

Every lab must capture evidence and verify each target independently. Estimates are approximate; measure your machine. Expected output is synthetic unless you capture actual output.

### M14-U3-LAB-01 — Argo CD hub on east; register west
- **Objective:** install one hub, register west with least privilege, deploy a tiny app to both.
- **Profile/footprint:** `Fleet+GitOps`; two small clusters plus one controller; measure RAM/CPU/disk.
- **Prerequisites:** verified contexts, isolated Git source, pinned versions, no production credentials.
- **Clusters:** east for hub, west for remote registration; both for app checks.
- **Start/stop:** start `Fleet-Core`, then Argo CD only on east; stop unrelated services.
- **Steps:** preflight; install version-matched Argo CD in `argocd` on east; create scoped west identity/RBAC; register west using verified CLI/declarative workflow; inspect non-secret name/server/labels; preview target list; deploy; independently verify both.
- **Evidence/matrix:** versions, sanitized registration metadata, RBAC matrix, Application destinations, Deployment/Pod state, sync/health/smoke result for east and west.
- **Cleanup:** remove only named sample app; retain hub for later labs; do not blindly remove CRDs.
- **Destructive/abort:** mutating install; abort on unexpected context, broad permissions, unknown version or unexpected target.
- **Stretch:** rotate west credential and verify recovery.
- **Fidelity:** local clusters are not independent regions.

### M14-U3-LAB-02 — ApplicationSet cluster-generator fan-out
- **Objective:** target only intended lab clusters and use overlays.
- **Profile:** `Fleet+GitOps`; existing hub.
- **Prerequisites:** LAB-01, labels and schema recorded.
- **Clusters:** east/west.
- **Start/stop:** hub running; no data stack.
- **Steps:** inspect actual cluster labels; add only reviewed lab labels; apply the illustrative ApplicationSet only after verifying its schema/source/project/deletion fields; inspect generated Application name/destination/path; sync; independently check workloads; test missing-label/unknown-cluster fixtures.
- **Evidence/matrix:** target set, generated specs, overlay render, both cluster states; ensure local default cluster not accidentally selected.
- **Cleanup:** inspect preservation/deletion behavior before removing ApplicationSet; delete only named lab resources.
- **Destructive/abort:** moderate due to cascade risk; abort on any unexpected Application or ambiguous destination.
- **Stretch:** capability selector.
- **Fidelity:** offline analyzer is not the controller.

### M14-U3-LAB-03 — Ring rollout with health gates
- **Objective:** a failed ring 0 cannot advance ring 1.
- **Profile:** `Fleet+GitOps` plus offline harness.
- **Prerequisites:** LAB-02, known-good revision.
- **Clusters:** east first, west only after approval.
- **Steps:** configure rings; run positive test; plant a lab-only readiness failure; assert ring-0 halt and unchanged ring-1 revision; revert/pin; verify east health; require explicit approval; verify west after promotion.
- **Evidence/matrix:** gate JSON, revision by cluster, health/smoke result, approval; assert failure → `NOT_ADVANCED` for ring 1.
- **Cleanup:** revert bad change and verify both targets.
- **Destructive/abort:** disposable workload only; abort if failed gate advances.
- **Stretch:** test native RollingSync on verified version.
- **Fidelity:** simulator is not native Argo CD behavior.

### M14-U3-LAB-04 — Fan-out impact report and CI gate
- **Objective:** reject expansion, forbidden namespace and deletion risk before sync.
- **Profile:** `Fleet-Core` offline; `Fleet+GitOps` for comparison.
- **Prerequisites:** Python 3 and Appendix A fixtures.
- **Clusters:** none for offline tests; read-only status checks for integration comparison.
- **Steps:** run analyzer on good fixture; run broad selector, missing label, unknown cluster, namespace expansion and deletion-risk cases; assert non-zero exit; compare actual generated Applications with offline output.
- **Evidence/matrix:** JSON report, human summary, test log, actual-vs-intended targets; every target must be approved.
- **Cleanup:** sanitize/remove internal inventory outputs.
- **Destructive/abort:** offline none; abort if forbidden targets pass.
- **Stretch:** CI integration.
- **Fidelity:** not a full YAML/Helm/Argo CD renderer.

### M14-U3-LAB-05 — ApplicationSet deletion-cascade guard
- **Objective:** observe generator/label change effects and verify preservation boundary.
- **Profile:** `Fleet+GitOps`, disposable sample namespace.
- **Prerequisites:** LAB-02, exact version/docs checked, known-good manifests.
- **Clusters:** only east/west lab targets.
- **Steps:** capture target Applications; inspect sync policy, preservation setting, owner refs/finalizers; preview a selector change; list deletions; verify exact semantics; execute only if target set is lab-only and effects understood; verify resource fate; restore config; run offline negative test; verify cleanup.
- **Evidence/matrix:** before/after targets, metadata, events, policy values, cleanup check.
- **Cleanup:** restore known-good config and delete only reviewed lab resources.
- **Destructive/abort:** high; stop at dry-run if semantics unclear or target set includes anything else.
- **Stretch:** separate fresh namespace test of non-cascading delete.
- **Fidelity:** no live deletion was executed during authoring.

### M14-U3-LAB-06 — Hub-down and hub-rebuild
- **Objective:** prove workloads can continue while reconciliation/visibility degrades; rebuild without prune.
- **Profile:** `Fleet+GitOps`.
- **Prerequisites:** LAB-01/02, pinned source and versions, baseline evidence.
- **Clusters:** stop only named controller components on east; check workloads on both.
- **Steps:** record workloads; stop only disposable controller after inspecting labels/owner; verify workloads remain; create harmless drift; verify it is not reconciled; record visibility loss; restore hub; verify reconciliation; rehearse rebuild/re-registration with pruning disabled; check each cluster.
- **Evidence/matrix:** before/during/after workloads, events, drift, recovery time, adoption state.
- **Cleanup:** restore replica count and desired app state.
- **Destructive/abort:** moderate; abort if controller resource cannot be identified or rebuild might prune.
- **Stretch:** repeated local recovery timing.
- **Fidelity:** does not model provider/regional failure.

### M14-U3-LAB-07 — Credential blast radius and admission enforcement
- **Objective:** prove west identity cannot read Secrets cluster-wide/write forbidden namespaces; policy rejects unapproved image.
- **Profile:** `Fleet+GitOps`, reuse one M12 policy engine.
- **Prerequisites:** identity mapped to hub credential; RBAC/policy syntax verified.
- **Clusters:** west, plus east hub status.
- **Steps:** run positive/negative `auth can-i`; verify Secret read and forbidden write denials; deploy approved image; attempt unapproved image in disposable namespace; capture admission denial; rotate/revoke test identity.
- **Evidence/matrix:** sanitized identity checks, policy version, denial event, rotation record without secret value.
- **Cleanup:** remove named test workload and revoke temporary identity if no longer needed.
- **Destructive/abort:** moderate; abort if identity cannot be identified or policy syntax is unverified.
- **Stretch:** older policy version fixture.
- **Fidelity:** admission syntax remains `[VERIFY]` until selected engine/version checked.

### M14-U3-LAB-08 — CRD/operator version-skew prevention
- **Objective:** exclude incompatible clusters and fail closed on missing/stale capability data.
- **Profile:** `Fleet-Core` plus fixtures; disposable cluster optional.
- **Prerequisites:** capability matrix and operator documentation; no production CRs.
- **Clusters:** none for fixture mode.
- **Steps:** require `example.io/v2`; fixture compatible/incompatible clusters; test selector; test missing/stale metadata; document operator-supported upgrade sequence; only then consider disposable integration.
- **Evidence/matrix:** capability matrix, selector tests and compatibility notes; unsupported cluster never receives the CR.
- **Cleanup:** remove only lab fixtures; inspect dependencies before CRD removal.
- **Destructive/abort:** offline none; live CRD change high-risk and must abort if dependencies unknown.
- **Stretch:** authenticated capability discovery.
- **Fidelity:** fixtures do not prove real operator compatibility.

### M14-U3-LAB-09 — Fleet convergence measurement and hub-vs-agent ADR
- **Objective:** measure per-cluster milestones and decide architecture with evidence.
- **Profile:** `Fleet+GitOps`.
- **Prerequisites:** successful deployment and timestamp template.
- **Clusters:** read-only checks east/west.
- **Steps:** record merge/commit, controller observation, sync, health, smoke test, final all-eligible convergence; list exclusions/reasons; write ADR comparing credentials, network, outage, visibility, overhead, tenancy and recovery; label hypothetical data `[ASSUMPTION]`.
- **Evidence/matrix:** CSV/JSON timestamps, target table, ADR, sample size; no guessed timestamps or silent exclusions.
- **Cleanup:** sanitize URLs; no resource cleanup.
- **Destructive/abort:** none; abort if missing timestamps are guessed.
- **Stretch:** repeat runs for valid percentiles.
- **Fidelity:** laptop timing is not production performance.

### M14-U3-LAB-10 — Optional Flux comparison
- **Objective:** compare per-cluster pull without overlapping Argo CD ownership.
- **Profile:** guided analysis by default; separate disposable environment if hands-on.
- **Prerequisites:** current Flux docs/CLI verified.
- **Clusters:** none in guided mode; separate disposable cluster if hands-on.
- **Steps:** compare bootstrap, credentials, reconciliation, repo layout, visibility, outage behavior, tenancy and upgrades; mark source-verified versus `[VERIFY]`.
- **Evidence/matrix:** comparison table and ADR delta; no secret values; no shared resource ownership.
- **Cleanup:** inspect dependencies before removing controllers/CRDs in the separate environment.
- **Destructive/abort:** guided low-risk; abort if environment overlaps Argo CD lab.
- **Stretch:** isolated bootstrap and source outage test.
- **Fidelity:** guided analysis is not execution.

## 13. Self-check questions

1. **Why isn't registration convergence?** It proves destination/auth metadata, not successful sync, health or service behavior.
2. **Hub trade-off?** Central visibility/controller simplicity versus concentrated credentials and network/control dependency.
3. **Does agent/pull remove governance risk?** No; bad Git can fan out to all agents.
4. **Why isn't ApplicationSet a rollout controller?** It generates Applications; safe ordering and health gates need separate verified behavior.
5. **What if ring 0 fails?** Freeze, preserve evidence, revert/pin, and prove ring 1 did not advance.
6. **Why isn't preservation a universal delete lock?** It covers a specific child-resource deletion path; policies/finalizers/version matter.
7. **Why an allow-list in addition to labels?** Labels can be stale or broadened; allow-list catches target expansion.
8. **What does `Synced` not prove?** Business correctness or endpoint health.
9. **Why deny cluster-wide Secret reads?** It reduces credential exposure and hub-compromise impact.
10. **What if capability metadata is stale?** Fail closed and quarantine until refreshed.
11. **Why not blindly manage CNI via app GitOps?** It may be a bootstrap dependency; reinstall can destabilize networking.
12. **Fleet ring vs workload canary?** Which clusters receive revision vs how traffic/replicas change inside one cluster.
13. **Do two kind clusters prove regional failover?** No; shared host failure domain and no real global routing.
14. **When is p95 meaningful?** With enough real observations, stated method and explicit exclusions.
15. **First action for bad fleet change?** Freeze propagation, identify targets, revert/pin by ring, communicate and verify.
16. **Deregister vs delete workloads?** Target registration removal is separate from resource deletion behavior.
17. **Why target-side admission?** It prevents the hub being the only trust anchor.
18. **Why isn't the impact script a full renderer?** It analyzes fixtures, not all Argo CD/Kustomize/Helm/live behavior.
19. **Why separate author/approver/promoter?** Reduce unchecked single-identity power over high-impact changes.
20. **What evidence should remain?** Commit/digest, target diff, approvals, per-cluster sync/health, smoke tests, exclusions and rollback result.

## 14. Evidence artifacts and suggested lab repository layout

```text
m14-u3-evidence/
├── versions.txt
├── preflight/{contexts.txt,cluster-identity.txt}
├── target-analysis/{before.json,after.json,summary.txt}
├── rollout/{ring-gate.json,per-cluster-status.csv,approval-record.md}
├── security/{sanitized-permission-matrix.md,auth-can-i-results.txt,admission-denial.txt}
├── recovery/{hub-down-timeline.csv,rebuild-checklist.md}
├── adr/ADR-001-hub-vs-agent.md
└── final-audit.md
```

Sanitize sensitive identifiers; never include credential values. Capture tool versions/timestamps; distinguish raw output from interpretation and synthetic from captured evidence.

## 15. Senior interview and design-review questions

1. **How choose hub vs agents for disconnected clusters?** Evaluate network direction, autonomy, credential blast radius, visibility and ownership; prove governance/aggregation.
2. **How prevent one ApplicationSet merge from reaching all clusters?** Allow-list, reviewed selectors, target diff, rings, role separation and deletion-aware tests.
3. **Define fleet convergence.** Every eligible target has the intended revision and passes sync, health and required service checks; unknowns remain visible.
4. **Re-adopt after hub rebuild?** Pinned config, reviewed credentials, inspect tracking/finalizers, disable pruning until ownership is proven, verify each target.
5. **Respond to leaked hub token?** Freeze, inventory, revoke via independent path, review logs, rebuild trusted state and verify clusters.
6. **Protect tenant from malicious ApplicationSet?** Source/destination/kind restrictions, protected generator path, selector constraints, admission and potentially separate instances.
7. **Handle CRD skew?** Fresh capabilities, fail-closed unknowns, supported upgrade order and canary evidence.
8. **Measure convergence SLO?** Timestamp merge, observation, sync, health and service tests; define denominator and sample size.
9. **When native RollingSync?** Only when installed version supports required behavior and limitations fit; verify health/auto-sync/approval requirements.
10. **Why can green dashboards mislead?** Stale data, omitted unreachable targets, shallow health checks or policy version mismatch.
11. **Propagation vs placement?** Propagation applies config to selected clusters; placement chooses where workloads run.
12. **Speed emergency patch safely?** Pinned artifact, separate roles, target report, expedited canary/gates, recorded exception and review.
13. **When split a hub?** Measured saturation, unacceptable credential blast radius, trust boundaries, network constraints or recovery coupling.
14. **What does safe offboarding prevent?** Accidental Application deletion, orphaned credentials/resources, stale traffic references and hidden dependencies.
15. **How test future cluster selectors?** Positive, missing label, unexpected cluster, stale capability, forbidden tier and empty selector fixtures plus controller integration tests.

## 16. What this unit teaches vs. what other modules own

| Module | Boundary |
|---|---|
| M08 — GitOps | Reuses single-cluster controllers, Applications/Kustomizations, repo layout, digest promotion, drift, secret references, evidence and within-cluster progressive delivery; no full re-teaching. |
| M02/M03 and Unit 2 | Cluster creation/lifecycle and Cluster API; this unit starts with a ready cluster. |
| M04 — Networking | Reuses single-cluster networking; Unit 4 owns cross-cluster connectivity/discovery. |
| M07 — IaC | Infrastructure and identity binding as code are prerequisites. |
| M09 — Identity/secrets | Reuses workload identity, trust, secret references and rotation. |
| M10 — SRE | Reuses error budgets, incident roles, freeze/rollback and change control. |
| M11 — Observability | Uses per-cluster status/markers; Unit 8 owns fleet aggregation/dashboard. |
| M12 — Supply chain/admission | Reuses signature verification and policy enforcement. |
| M13 — Backup/DR | Reuses hub rebuild/re-adoption; detailed backup/restore remains M13. |
| M15 — Capacity/FinOps | Detailed cost modeling deferred; only qualitative drivers here. |
| M16 — Platform Engineering | Cluster vending/golden paths are forward references. |
| M17 — Integrated capstone | This unit provides fleet GitOps building blocks, not the entire capstone. |
| M14 Units 4–8 | Own networking, global traffic, regional patterns, replication/consistency and fleet observability/governance. |

## 17. Sources and verification notes

Official pages consulted on 2026-10-29:

1. Argo CD, **Declarative Setup** — https://argo-cd.readthedocs.io/en/latest/operator-manual/declarative-setup/
2. Argo CD, **Cluster Generator** — https://argo-cd.readthedocs.io/en/latest/operator-manual/applicationset/Generators-Cluster/
3. Argo CD, **ApplicationSet Specification Reference** — https://argo-cd.readthedocs.io/en/latest/operator-manual/applicationset/applicationset-specification/
4. Argo CD, **Application Pruning & Resource Deletion** — https://argo-cd.readthedocs.io/en/latest/operator-manual/applicationset/Application-Deletion/
5. Argo CD, **Controlling Resource Modification** — https://argo-cd.readthedocs.io/en/latest/operator-manual/applicationset/Controlling-Resource-Modification/
6. Argo CD, **Progressive Syncs** — https://argo-cd.readthedocs.io/en/latest/operator-manual/applicationset/Progressive-Syncs/
7. Argo CD, **Sync Phases and Waves** — https://argo-cd.readthedocs.io/en/latest/user-guide/sync-waves/
8. Flux, **Installation** — https://fluxcd.io/flux/installation/

These official docs were consulted but every field/flag was not validated against a pinned release. `/latest/` pages may move. Before execution, pin versions and use matching docs.

Unresolved `[VERIFY]`: exact `argocd cluster add` behavior/permissions/token renewal; cluster Secret auth schema; ApplicationSet template/generator/missing-key/local-cluster semantics; `applicationsSync`, preservation/finalizer deletion paths; RollingSync feature flags/maturity; AppProject/RBAC boundaries; Kubernetes `auth can-i` identity flags; selected M12 admission policy syntax; operator-specific CRD upgrade order; current status of Fleet/Karmada/OCM/KubeFed/cloud products; kind CIDR fields and actual machine footprint.

## Appendix A — Complete lab files

These examples are complete for offline analysis, but live manifests require version pinning and review. Scripts do not call Kubernetes or emulate Argo CD. `.invalid` endpoints and the image digest placeholder are intentionally non-deployable.

### A.1 `fixtures/registry.json`

```json
{
  "allowed_clusters": ["stage2e-east-lab", "stage2e-west-lab"],
  "clusters": [
    {"name":"stage2e-east-lab","server":"https://east.invalid","env":"lab","region":"east","ring":"canary","tier":"0","conformant":true,"capabilities":["apps-v1","policy-v1"],"namespace_allowlist":["sample-api"]},
    {"name":"stage2e-west-lab","server":"https://west.invalid","env":"lab","region":"west","ring":"stable","tier":"1","conformant":true,"capabilities":["apps-v1","policy-v1"],"namespace_allowlist":["sample-api"]}
  ]
}
```

### A.2 `fixtures/change-good.json`

```json
{"change_id":"demo-001","selector":{"env":"lab"},"approved_clusters":["stage2e-east-lab","stage2e-west-lab"],"namespace":"sample-api","application":"sample-api","resources":["Deployment","Service","ConfigMap"],"deletions":[],"required_capabilities":["apps-v1"],"forbidden_tiers":["0-critical","prod-critical"]}
```

### A.3 `fixtures/change-broad-selector.json`

```json
{"change_id":"negative-broad-selector","selector":{},"approved_clusters":["stage2e-east-lab","stage2e-west-lab"],"namespace":"sample-api","application":"sample-api","resources":["Deployment"],"deletions":[],"required_capabilities":[],"forbidden_tiers":["0-critical","prod-critical"]}
```

### A.4 `fixtures/change-namespace-expansion.json`

```json
{"change_id":"negative-namespace-expansion","selector":{"env":"lab"},"approved_clusters":["stage2e-east-lab","stage2e-west-lab"],"namespace":"kube-system","application":"sample-api","resources":["DaemonSet"],"deletions":[],"required_capabilities":[],"forbidden_tiers":["0-critical","prod-critical"]}
```

### A.5 `fixtures/change-deletion-risk.json`

```json
{"change_id":"negative-deletion-risk","selector":{"env":"lab"},"approved_clusters":["stage2e-east-lab","stage2e-west-lab"],"namespace":"sample-api","application":"sample-api","resources":["Deployment"],"deletions":["Application/sample-api-stage2e-west-lab"],"required_capabilities":["apps-v1"],"forbidden_tiers":["0-critical","prod-critical"]}
```

### A.6 `scripts/fleet_impact.py`

```python
#!/usr/bin/env python3
"""Offline target/impact analyzer. Not an Argo CD/Kustomize renderer."""
import argparse, json, sys
from pathlib import Path
REQUIRED_LABELS = {"env"}

def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def analyze(registry, change):
    errors, warnings, targets = [], [], []
    allowed = set(registry.get("allowed_clusters", []))
    clusters = registry.get("clusters", [])
    names = [c.get("name") for c in clusters]
    if None in names or len(set(names)) != len(names):
        errors.append("duplicate or missing cluster names in registry")
    selector = change.get("selector")
    if not isinstance(selector, dict) or not selector:
        errors.append("empty or invalid selector: fail closed")
        selector = {}
    missing_labels = REQUIRED_LABELS - set(selector)
    if missing_labels:
        errors.append("selector missing required labels: " + ", ".join(sorted(missing_labels)))
    for c in clusters:
        name = c.get("name")
        if not name or not all(c.get(k) == v for k, v in selector.items()):
            continue
        if name not in allowed:
            errors.append(f"selector matched unapproved cluster: {name}"); continue
        if not c.get("conformant", False):
            errors.append(f"cluster is not conformant: {name}"); continue
        if not c.get("capabilities"):
            errors.append(f"missing capability metadata: {name}"); continue
        missing = set(change.get("required_capabilities", [])) - set(c["capabilities"])
        if missing:
            warnings.append(f"excluded incompatible cluster {name}; missing {sorted(missing)}"); continue
        if c.get("tier") in set(change.get("forbidden_tiers", [])):
            errors.append(f"forbidden tier targeted: {name}"); continue
        ns = change.get("namespace")
        if ns not in set(c.get("namespace_allowlist", [])):
            errors.append(f"namespace not allowed on {name}: {ns}"); continue
        targets.append({"cluster":name,"server":c.get("server"),"ring":c.get("ring"),"namespace":ns,
                        "application":change.get("application"),"resources":sorted(set(change.get("resources", [])))})
    requested = set(change.get("approved_clusters", []))
    unknown = requested - allowed
    if unknown: errors.append(f"approved_clusters contains unknown cluster(s): {sorted(unknown)}")
    target_names = {t["cluster"] for t in targets}
    if target_names - requested: errors.append(f"target expansion beyond approved_clusters: {sorted(target_names-requested)}")
    if requested - target_names: warnings.append(f"approved cluster(s) not selected/eligible: {sorted(requested-target_names)}")
    deletions = change.get("deletions", [])
    if deletions:
        warnings.append("deletion risk: " + ", ".join(deletions))
        errors.append("deletion requires separate reviewed approval")
    if not targets: errors.append("no eligible targets; fail closed")
    return {"change_id":change.get("change_id","unknown"),"targets":sorted(targets,key=lambda t:(t["ring"] or "",t["cluster"])),
            "target_count":len(targets),"errors":errors,"warnings":warnings,
            "decision":"REJECT" if errors else "REVIEW_REQUIRED" if warnings else "PASS_OFFLINE_ANALYSIS_ONLY",
            "limitations":["Does not render Kubernetes YAML, Kustomize, Helm or ApplicationSet templates.",
                           "Does not query live Argo CD/Kubernetes state.","Does not prove authorization, health or deletion semantics."]}

def main():
    p=argparse.ArgumentParser(); p.add_argument("--registry",required=True); p.add_argument("--change",required=True); p.add_argument("--json-out"); a=p.parse_args()
    try: r=analyze(load(a.registry),load(a.change))
    except (OSError,json.JSONDecodeError,TypeError) as e:
        print(f"input error: {e}",file=sys.stderr); return 2
    rendered=json.dumps(r,indent=2,sort_keys=True)
    if a.json_out: Path(a.json_out).write_text(rendered+"\n",encoding="utf-8")
    print(f"Change: {r['change_id']} | Decision: {r['decision']} | Targets: {r['target_count']}")
    for t in r["targets"]: print(f" - {t['cluster']} ring={t['ring']} namespace={t['namespace']} app={t['application']} resources={','.join(t['resources'])}")
    for w in r["warnings"]: print("WARNING: "+w)
    for e in r["errors"]: print("ERROR: "+e,file=sys.stderr)
    if a.json_out: print("JSON written to "+a.json_out)
    return 1 if r["errors"] else 0
if __name__ == "__main__": raise SystemExit(main())
```

### A.7 `tests/test_fleet_impact.py`

```python
import importlib.util, json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("fleet_impact",ROOT/"scripts/fleet_impact.py")
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
registry=json.loads((ROOT/"fixtures/registry.json").read_text())
def change(n): return json.loads((ROOT/f"fixtures/{n}").read_text())
class ImpactTests(unittest.TestCase):
    def test_expected_targets(self):
        r=mod.analyze(registry,change("change-good.json")); self.assertEqual({t["cluster"] for t in r["targets"]},{"stage2e-east-lab","stage2e-west-lab"}); self.assertFalse(r["errors"])
    def test_empty_selector(self): self.assertTrue(mod.analyze(registry,change("change-broad-selector.json"))["errors"])
    def test_namespace_expansion(self): self.assertTrue(any("namespace not allowed" in e for e in mod.analyze(registry,change("change-namespace-expansion.json"))["errors"]))
    def test_deletion_risk(self): self.assertTrue(any("deletion" in e for e in mod.analyze(registry,change("change-deletion-risk.json"))["errors"]))
    def test_unknown_cluster(self):
        c=change("change-good.json"); c["approved_clusters"].append("stage2e-north-lab")
        self.assertTrue(any("unknown cluster" in e for e in mod.analyze(registry,c)["errors"]))
    def test_missing_required_label(self):
        c=change("change-good.json"); c["selector"]={"region":"east"}
        self.assertTrue(any("missing required labels" in e for e in mod.analyze(registry,c)["errors"]))
    def test_missing_capabilities(self):
        r=json.loads(json.dumps(registry)); r["clusters"][1]["capabilities"]=[]
        self.assertTrue(any("missing capability metadata" in e for e in mod.analyze(r,change("change-good.json"))["errors"]))
    def test_unapproved_matching_cluster(self):
        r=json.loads(json.dumps(registry)); r["clusters"].append({"name":"stage2e-north-lab","server":"https://north.invalid","env":"lab","ring":"stable","tier":"1","conformant":True,"capabilities":["apps-v1"],"namespace_allowlist":["sample-api"]})
        c=change("change-good.json")
        self.assertTrue(any("unapproved cluster" in e for e in mod.analyze(r,c)["errors"]))
if __name__=="__main__": unittest.main()
```

### A.8 `fixtures/rings.json`

```json
{"rings":[{"name":"ring-0","clusters":["stage2e-east-lab"],"requires_approval":false},{"name":"ring-1","clusters":["stage2e-west-lab"],"requires_approval":true}],"required_gates":["sync_ok","health_ok","smoke_ok"],"policy":"stop on first failed gate; no later ring advances"}
```

### A.9 `scripts/ring_gate.py`

```python
#!/usr/bin/env python3
"""Deterministic ring gate simulator; does not control Argo CD."""
import argparse,json,sys
from pathlib import Path

def evaluate(rings,results,approved=False):
    output=[]; halted=False
    for ring in rings["rings"]:
        name=ring["name"]
        if halted:
            output.append({"ring":name,"decision":"NOT_ADVANCED","reason":"prior ring failed or awaits approval"}); continue
        if ring.get("requires_approval") and not approved:
            output.append({"ring":name,"decision":"WAITING_APPROVAL","reason":"explicit approval required"}); halted=True; continue
        states=[results.get(c,{}) for c in ring["clusters"]]
        failed=[c for c,s in zip(ring["clusters"],states) if not all(s.get(g) is True for g in rings["required_gates"])]
        if failed: output.append({"ring":name,"decision":"HALT","failed_clusters":failed}); halted=True
        else: output.append({"ring":name,"decision":"PASS","clusters":ring["clusters"]})
    return {"simulated":True,"rings":output,"halted":halted,"note":"simulation only; no controller/API/workload changed"}

def main():
    p=argparse.ArgumentParser(); p.add_argument("--rings",required=True); p.add_argument("--results",required=True); p.add_argument("--approve-ring-1",action="store_true"); p.add_argument("--out"); a=p.parse_args()
    try: r=evaluate(json.loads(Path(a.rings).read_text()),json.loads(Path(a.results).read_text()),a.approve_ring_1)
    except Exception as e: print(f"input error: {e}",file=sys.stderr); return 2
    s=json.dumps(r,indent=2); print(s)
    if a.out: Path(a.out).write_text(s+"\n")
    return 0
if __name__=="__main__": raise SystemExit(main())
```

### A.10 `tests/test_ring_gate.py`

```python
import importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("ring_gate",ROOT/"scripts/ring_gate.py")
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
rings=json.loads((ROOT/"fixtures/rings.json").read_text())
GOOD={"stage2e-east-lab":{"sync_ok":True,"health_ok":True,"smoke_ok":True},"stage2e-west-lab":{"sync_ok":True,"health_ok":True,"smoke_ok":True}}
class RingGateTests(unittest.TestCase):
    def test_bad_canary_halts_ring1(self):
        bad=json.loads(json.dumps(GOOD)); bad["stage2e-east-lab"]["health_ok"]=False
        out=mod.evaluate(rings,bad,True); self.assertEqual(out["rings"][0]["decision"],"HALT"); self.assertEqual(out["rings"][1]["decision"],"NOT_ADVANCED")
    def test_approval_required(self):
        out=mod.evaluate(rings,GOOD,False); self.assertEqual(out["rings"][0]["decision"],"PASS"); self.assertEqual(out["rings"][1]["decision"],"WAITING_APPROVAL")
    def test_approved_success_advances(self): self.assertEqual(mod.evaluate(rings,GOOD,True)["rings"][1]["decision"],"PASS")
    def test_missing_gate_fails_closed(self):
        out=mod.evaluate(rings,{"stage2e-east-lab":{"sync_ok":True}},True); self.assertEqual(out["rings"][0]["decision"],"HALT"); self.assertEqual(out["rings"][1]["decision"],"NOT_ADVANCED")
if __name__=="__main__": unittest.main()
```

### A.11 Sample app manifests

```yaml
# apps/sample-api/base/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: sample-api
  labels:
    app.kubernetes.io/part-of: m14-u3-lab
```

```yaml
# apps/sample-api/base/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sample-api
  namespace: sample-api
spec:
  replicas: 1
  selector:
    matchLabels: {app.kubernetes.io/name: sample-api}
  template:
    metadata:
      labels: {app.kubernetes.io/name: sample-api}
    spec:
      containers:
        - name: app
          image: registry.example.invalid/m14/sample-api@sha256:REPLACE_WITH_REAL_DIGEST
          ports: [{name: http, containerPort: 8080}]
          readinessProbe:
            httpGet: {path: /healthz, port: http}
            initialDelaySeconds: 2
            periodSeconds: 5
          resources:
            requests: {cpu: 25m, memory: 32Mi}
            limits: {cpu: 200m, memory: 128Mi}
```

```yaml
# apps/sample-api/base/service.yaml
apiVersion: v1
kind: Service
metadata: {name: sample-api, namespace: sample-api}
spec:
  selector: {app.kubernetes.io/name: sample-api}
  ports: [{name: http, port: 80, targetPort: http}]
```

```yaml
# apps/sample-api/base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources: [namespace.yaml, deployment.yaml, service.yaml]
```

```yaml
# apps/sample-api/overlays/east/kustomization.yaml (west uses same structure)
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources: [../../base]
patches:
  - path: replica-patch.yaml
```

```yaml
# apps/sample-api/overlays/east/replica-patch.yaml (west equivalent)
apiVersion: apps/v1
kind: Deployment
metadata: {name: sample-api, namespace: sample-api}
spec: {replicas: 1}
```

The image digest and repository are placeholders and are not deployable. Replace only with an image you control and have verified. Do not claim a successful deploy using the placeholder.

### A.12 Illustrative ApplicationSet (version-sensitive; do not apply without review)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata: {name: m14-u3-sample-api, namespace: argocd}
spec:
  generators:
    - clusters:
        selector:
          matchLabels:
            env: lab
            m14-u3-approved: "true"
  template:
    metadata:
      name: '{{name}}-sample-api'
      labels:
        app.kubernetes.io/part-of: m14-u3-lab
        fleet-ring: '{{metadata.labels.ring}}'
    spec:
      project: m14-u3-lab
      source:
        repoURL: https://git.example.invalid/platform/gitops.git
        targetRevision: REPLACE_WITH_REVIEWED_COMMIT
        path: apps/sample-api/overlays/{{metadata.labels.region}}
      destination:
        name: '{{name}}'
        namespace: sample-api
      syncPolicy:
        syncOptions: [CreateNamespace=true]
  syncPolicy:
    preserveResourcesOnDeletion: true
    applicationsSync: create-update
```

Before applying, verify the installed ApplicationSet CRD schema, template mode, selector/label data, destination semantics, AppProject, repo path and deletion behavior. `applicationsSync` values/semantics are `[VERIFY]`; preservation is not a universal delete lock. The AppProject must exist and restrict source/destination/kinds. This ApplicationSet does not implement ring advancement.

### A.13 Illustrative AppProject (version-sensitive)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata: {name: m14-u3-lab, namespace: argocd}
spec:
  description: Disposable M14 Unit 3 lab only
  sourceRepos: [https://git.example.invalid/platform/gitops.git]
  destinations:
    - {name: stage2e-east-lab, namespace: sample-api}
    - {name: stage2e-west-lab, namespace: sample-api}
  clusterResourceWhitelist: []
  namespaceResourceWhitelist:
    - {group: "", kind: Namespace}
    - {group: "", kind: Service}
    - {group: apps, kind: Deployment}
```

Verify destination matching and schema against the installed version. This is not a production-complete project; do not grant cluster-scoped permissions just to make a sample sync.

### A.14 RBAC intent example (not a universal registration manifest)

```yaml
apiVersion: v1
kind: ServiceAccount
metadata: {name: argocd-west-sample-deployer, namespace: sample-api}
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata: {name: sample-api-deployer, namespace: sample-api}
rules:
  - apiGroups: [""]
    resources: [services, configmaps]
    verbs: [get, list, watch, create, update, patch, delete]
  - apiGroups: [apps]
    resources: [deployments]
    verbs: [get, list, watch, create, update, patch, delete]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata: {name: sample-api-deployer, namespace: sample-api}
subjects:
  - kind: ServiceAccount
    name: argocd-west-sample-deployer
    namespace: sample-api
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: sample-api-deployer
```

This deliberately grants no Secret access, namespace creation, or cluster-scoped rights. Create the namespace through a separately reviewed bootstrap path. Actual Argo CD identity mapping and credential issuance must be verified; a ServiceAccount alone is not a complete token lifecycle, and do not assume a long-lived token Secret is automatically created in every Kubernetes version.

### A.15 Evidence template

```markdown
# M14-U3 Rollout Evidence
- Date/time and timezone:
- Operator and tool versions:
- Source commit / image digest:
- Approved target allow-list / actual generated targets:
- Ring plan and approver:
- Ring 0 sync / health / smoke result:
- Halt decision and reason:
- Ring 1 approval and result:
- Per-cluster revision, sync, health and smoke test:
- Excluded/unreachable targets and reason:
- Cleanup independently verified:
- Synthetic versus captured evidence:
- Open risks / [VERIFY] items:
```

## Appendix B — Ordered execution, rollback and cleanup

### B.1 Safe order

1. Read the module and matching-version official docs.
2. Pin versions and record them in `versions.txt`.
3. Verify contexts and cluster identity.
4. Start `Fleet-Core`; run offline tests first.
5. Install one Argo CD hub on east using version-matched instructions.
6. Register west with reviewed least-privilege credentials.
7. Preview target set; apply AppProject/ApplicationSet only after review.
8. Verify each target independently.
9. Run ring/impact tests offline, then bounded integration tests.
10. Run deletion and hub-rebuild drills only after prerequisites and abort checks.
11. Capture and sanitize evidence.
12. Clean up named resources; verify no stray/sensitive artifacts remain.

### B.2 Rollback

Freeze promotion first. Identify exact revision and affected clusters. Pin/revert to known-good immutable digest by ring. Verify ring 0 before advancing later rings. Keep pruning disabled during rebuild/re-adoption until ownership is proven. Verify every target with explicit context and independent application checks. Preserve events, revisions, impact reports and approvals.

### B.3 Cleanup

List exact named resources and owners before deletion. Inspect ApplicationSet owner references, Application finalizers, AppProject dependencies and shared CRDs/operators. Delete only sample resources created for the lab, after understanding cascade behavior. Do not automatically remove shared CRDs or the entire `argocd` namespace. Revoke temporary credentials through the approved process; verify revocation. Re-run context preflight and check both clusters for unexpected sample resources.

### B.4 Abort conditions

Abort before mutation if a context is unexpected, the target list includes an unknown cluster, credentials exceed intended scope, version-sensitive fields are unchecked, deletion effect is unclear, CRD dependencies are unknown, or a required negative test unexpectedly succeeds. An abort is correct when safety cannot be proven.

## Appendix C — Requirement traceability audit

`PASS` means the teaching requirement is represented, not that a live lab passed. `PARTIAL` means integration/version checks remain; `OPEN` means live verification is still required.

| Requirement | Location | Status |
|---|---|---|
| Verbatim M08 handoff; L1–L4 | §§1–2, §§5–8 | PASS |
| Hub/agent comparison and diagrams | §§4, 5.2, 6.1 | PASS |
| Registration and credential flow | §§5.3, 6.1, LAB-01 | PARTIAL — exact CLI/auth `[VERIFY]` |
| Repository structure and inheritance | §§5.4, 6.4, 7.2 | PASS |
| ApplicationSet generator, selectors, templates | §§6.2–6.3, A.12 | PARTIAL — schema/version `[VERIFY]` |
| Deletion/preserve/sync semantics | §6.8, A.12, LAB-05 | PARTIAL — installed-version behavior |
| Overlays and baseline ordering | §§6.4–6.5, A.11 | PASS as examples; render not run |
| Ring rollout, health gate, auto-halt | §6.6, A.8–A.10, LAB-03 | PASS as simulator; native integration OPEN |
| Fan-out impact report/CI gate | §6.7, A.1–A.7, LAB-04 | PASS offline; not full renderer |
| Hub-down/rebuild without prune | §6.9, §8.3, LAB-06, Appendix B | PARTIAL — not executed |
| Secret-read/forbidden-write negative test | §§5.3, 6.10, LAB-07, A.14 | PARTIAL — live RBAC OPEN |
| Admission unapproved-image test | §6.10, LAB-07 | OPEN — policy syntax `[VERIFY]` |
| CRD skew/capability labels | §§6.11, 7.3, LAB-08 | PASS fixture plan; live test OPEN |
| Convergence measurement and ADR | §§6.12–6.13, LAB-09, A.15 | PASS method/template; no measurements claimed |
| Flux comparison | §6.14, LAB-10 | PASS guided; hands-on optional |
| L3 tenancy/progressive/drift/scale/alternatives | §§7.1–7.9 | PASS with caveats |
| L4 SLOs/runbooks/onboarding/offboarding/emergency | §§8.1–8.7 | PASS |
| Ten hypothetical incidents | §8.6 | PASS |
| Ten complete lab specifications | §12 | PASS as plans; not executed |
| SRE/security/readiness/questions/evidence/interview | §§9–15 | PASS |
| Cross-module boundaries | §16 | PASS |
| Sources, claim register and execution statement | §17, Appendices D–E | PASS with open verification |
| Complete offline fixtures/scripts/tests/manifests | Appendix A | PASS as authored; not executed |
| Ordered rollback/cleanup/abort | Appendix B | PASS as procedure; not executed |

## Appendix D — Claim Register and unresolved verification

| Claim | Source/status | Sensitivity | Required verification | Risk if wrong |
|---|---|---|---|---|
| Cluster credentials use labelled cluster Secrets in declarative Argo CD setup | Official Declarative Setup page reviewed 2026-10-29 | Medium/high | Match installed version/auth provider | Registration failure or credential exposure |
| Cluster generator exposes cluster name/server/labels and selectors | Official Cluster Generator page reviewed 2026-10-29 | High | Test actual metadata/template mode | Unintended fan-out |
| ApplicationSet deletion may delete generated Apps/children depending on settings | Official deletion/modification docs reviewed 2026-10-29 | High | Disposable test with exact version | Workload deletion/orphaning |
| `applicationsSync` and preservation fields | Official ApplicationSet spec reviewed 2026-10-29 | High | Validate CRD schema and behavior | False safety assumption |
| RollingSync beta status and behavior | Official Progressive Syncs page reviewed 2026-10-29 | High | Confirm version/flags/constraints | Ring gate not enforced |
| Sync waves order resources within one Application | Official Sync Waves page reviewed 2026-10-29 | Medium | Validate health and resource semantics | Dependency ordering failure |
| Flux bootstrap installs controllers and configures Git sync | Official Flux Installation page reviewed 2026-10-29 | Medium/high | Use current CLI/docs in separate env | Wrong bootstrap/overlapping ownership |
| West identity denies cluster-wide Secret reads | Design intent only; not tested | High | Live `auth can-i` tests and audit | Secret exposure/privilege escalation |
| Admission rejects unapproved image | Design intent only; engine not selected | High | M12 engine/version negative test | Untrusted image deployment |
| CRD/operator upgrade order | Operator unspecified | High | Operator-specific guide and disposable test | API failure/controller outage |
| kind cluster isolation/footprint | Not measured | Medium | Check CIDRs/config and measure machine | False regional assurance/resource exhaustion |
| Fleet/Karmada/OCM/KubeFed/cloud feature status | Awareness only | High | Check current official project status before recommendation | Stale architecture choice |
| Impact analyzer equals actual Argo CD target set | Explicitly not claimed | N/A | Compare generated Applications live | False-negative target expansion |
| Ring harness proves native Argo CD behavior | Explicitly not claimed | N/A | Version-pinned integration test | False confidence in rollout halt |

## Appendix E — Truthful execution statement

- **Source-reviewed:** supplied Unit 3 prompt and roadmap were inspected for target path, curriculum, required labs, safety rules and neighboring module boundaries.
- **Official sources consulted:** Argo CD Declarative Setup, Cluster Generator, ApplicationSet Specification, Application Deletion, Controlling Resource Modification, Progressive Syncs, Sync Phases/Waves, and Flux Installation (links in §17); review date 2026-10-29.
- **Commands/configurations/tests executed:** the two embedded offline Python test suites were extracted to `/tmp/m14-u3-module-audit` and run with `python -m unittest discover`; 12 tests passed. No kind/Kubernetes cluster, Argo CD, Flux, policy engine or workload was run, and no Kubernetes manifest was applied.
- **Static checks:** structure, requirement coverage, named cluster consistency, safety boundaries and offline examples were reviewed. The offline Python tests were executed, but no formal YAML/schema validation or controller integration test was run.
- **Synthetic examples:** no real command output or performance measurement is claimed. `.invalid` endpoints and image digest are placeholders.
- **Remaining uncertainty:** all `[VERIFY]` items in §17 and Appendix D remain open until checked against exact installed versions and executed in a disposable lab.
- **Human validation:** this audit does not replace an operator running the labs, reviewing each mutation, inspecting generated targets and verifying no unintended resources/secrets remain.
