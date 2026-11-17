# M14 Capstone --- Two-Region Failover for a Data Platform

> **Target:** `Projects/01-two-region-failover-for-a-data-platform.md`\
> **Stage:** Stage 2E --- Production DevOps & Platform Engineering\
> **Module:** M14 --- Multi-Cluster and Multi-Region Operations, Unit 10
> capstone\
> **Status:** **SPECIFICATION DRAFT --- RUNTIME NOT EXECUTED**\
> **Audience:** Data/AI engineers who completed M01--M13 and have
> operated a single-cluster platform\
> **Estimated effort:** 45--75 hours `[ILLUSTRATIVE]`\
> **Budget:** zero-budget local simulation; no cloud accounts, paid
> services, public DNS changes, production data, or production
> credentials\
> **Tool baseline:** actual versions not inventoried; version-sensitive
> details are `[VERIFY]`\
> **Last authored:** 2026-10-29

> **Mandatory fidelity statement:** **Two `kind` clusters on one laptop
> are not two geographic regions.** They share hardware and may share
> network, power, storage, and host failure domains. A local simulation
> can test workflows, guards, decisions, and measurement methods; it
> cannot prove independent regional resilience, real WAN replication
> behavior, real provider DNS/global-routing behavior, or production
> failover performance. The roadmap treats true global traffic
> management as **not feasible free**; this capstone simulates endpoint
> switching locally.

## Summary

The learner designs and later implements a reviewable two-cluster
operating model with explicit context safety, a validated fleet
registry, staged GitOps, active-active stateless inference, a
single-writer data tier with a replica or deterministic simulation,
object/model artifact integrity gates, local traffic switching,
per-cluster observability, conformance/quarantine, measured failover and
fail-back, and a game-master incident simulation.

This is a **project specification with inline proposed artifacts**, not
a report of a completed repository implementation. Paths below are
proposed paths inside a future capstone workspace. Only this Markdown
specification is created by this task.

## Table of contents

1.  [Scenario and boundaries](#1-scenario-and-boundaries)
2.  [Prerequisites and completion
    contract](#2-prerequisites-and-completion-contract)
3.  [Architecture and failure
    boundaries](#3-architecture-and-failure-boundaries)
4.  [ADR-001: topology choice](#4-adr-001-topology-choice)
5.  [Proposed repository layout](#5-proposed-repository-layout)
6.  [Profiles, resource budget, and
    sequencing](#6-profiles-resource-budget-and-sequencing)
7.  [Preflight and hard gates](#7-preflight-and-hard-gates)
8.  [Fleet, registry, CIDRs, and
    lifecycle](#8-fleet-registry-cidrs-and-lifecycle)
9.  [GitOps, rings, and integrity
    gates](#9-gitops-rings-and-integrity-gates)
10. [Connectivity, TLS, and
    isolation](#10-connectivity-tls-and-isolation)
11. [Local traffic simulation](#11-local-traffic-simulation)
12. [Regional serving and capacity](#12-regional-serving-and-capacity)
13. [Data replication and
    consistency](#13-data-replication-and-consistency)
14. [Observability and policy
    governance](#14-observability-and-policy-governance)
15. [Game-master simulation](#15-game-master-simulation)
16. [Bounded resilience experiments](#16-bounded-resilience-experiments)
17. [Evidence and measurements](#17-evidence-and-measurements)
18. [Runbooks, fail-back, and
    postmortem](#18-runbooks-fail-back-and-postmortem)
19. [Safety harness and
    `make verify-all`](#19-safety-harness-and-make-verify-all)
20. [Sequencing and cleanup](#20-sequencing-and-cleanup)
21. [Acceptance matrix](#21-acceptance-matrix)
22. [Risk register and
    troubleshooting](#22-risk-register-and-troubleshooting)
23. [Not simulated and fidelity
    limits](#23-not-simulated-and-fidelity-limits)
24. [Glossary](#24-glossary)
25. [Claim and Uncertainty Register](#25-claim-and-uncertainty-register)
26. [Roadmap Alignment and Authenticity
    Audit](#26-roadmap-alignment-and-authenticity-audit)

------------------------------------------------------------------------

## 1. Scenario and boundaries

The starting data/ML platform runs in one Kubernetes cluster. Problems
include a large blast radius; engineers using whichever `kubectl`
context is active; no validated fleet inventory; single-cluster GitOps;
untested replication; no tested global entry point; untimed DNS
failover; an overprivileged shared kubeconfig; and dashboards that
average away regional failures.

The running example includes: - stateless inference API (active-active
candidate); - PostgreSQL system of record (single writer, cross-cluster
replica or simulator); - object storage for datasets/model artifacts; -
model registry and alias gated by artifact completeness/hash; -
ETL/streaming jobs with region-pinned or mirrored ownership; - GitOps
repository, per-cluster identity/secrets, local and central telemetry,
and a common security/policy baseline.

M14 owns steady-state fleet and multi-region operations. Reuse rather
than re-teach: - M03: cluster architecture and version skew. - M04:
CNI/CIDR, Services/DNS, Gateway/LB, TLS and mesh fundamentals. - M05:
stateful workloads/operators. - M07: IaC and provider composition. -
M08: GitOps, controller hardening, digest promotion and drift. - M09:
secrets/identity. - M10: SLOs and incident practice. - M11:
observability. - M12: supply-chain security/admission. - M13:
backup/restore, recovery markers and DR drills. Do not re-teach M13
mechanics; reference M13 Units 1, 6 and 7. - M15--M17 are forward
references only for FinOps, platform golden paths and later integration.

### Completion contract

The learner must prove target guards work, ring 0 halts on a planted bad
change, quarantine excludes non-conformant/unreachable clusters, write
routing waits for data promotion and fencing, failover and fail-back are
evidenced, and cleanup is independently verified. A local pass is not
production certification.

## 2. Prerequisites and completion contract

Prerequisites: Linux/WSL2 shell, Git, Docker, `kubectl`, kind, basic
YAML, Kubernetes Services, NetworkPolicy, GitOps, health checks,
SQL/PostgreSQL, Prometheus and incident runbooks.

Safety rules: 1. Use disposable lab data only. 2. Only
`stage2e-east-lab` and `stage2e-west-lab` are allowed targets. 3. Every
mutation names its target explicitly; never infer from current context.
4. Fail closed on unknown identity, missing evidence or stale status. 5.
Every fault has a bounded lease, watchdog, manual abort and automatic
abort. 6. Keep secrets out of manifests, logs and evidence. 7. Preserve
evidence before cleanup when safe; cleanup failure is a failed run. 8.
Do not enable authoritative writes until the old writer is fenced or
proven unable to accept conflicting writes. 9. Mark examples
`[ILLUSTRATIVE]`, generated incident data `[SYNTHETIC]`, actual captured
results `[MEASURED]`, and unresolved version details `[VERIFY]`.

## 3. Architecture and failure boundaries

``` text
                    reviewed Git / desired state
                              |
                       GitOps hub (lab)
                       /             \
                 ring 0/canary      ring 1
                     |                |
       +------------------------+ +------------------------+
       | stage2e-east-lab       | | stage2e-west-lab       |
       | inference API          | | inference API          |
       | local alerts/metrics   | | local alerts/metrics   |
       | PostgreSQL writer*     | | replica/simulator*     |
       | policy/conformance     | | policy/conformance     |
       +------------------------+ +------------------------+
                   \                /
                    local DNS-like/proxy switch
                              |
                        client harness
```

`*` Real PostgreSQL replication is profile-dependent. If it cannot be
safely operated, use the deterministic write-ledger simulator and label
it `[SIMULATED]`. Do not claim database replication was tested when only
the simulator ran.

  -----------------------------------------------------------------------
  Boundary                Failure                 Required behavior
  ----------------------- ----------------------- -----------------------
  Cluster                 wrong context, API      stop mutation;
                          unreachable, CIDR       unknown/unreachable is
                          overlap                 not healthy

  GitOps hub              unavailable or          pause promotion; local
                          compromised             workloads may continue;
                                                  no blind reapply

  Network/discovery       stale endpoint, DNS     bounded
                          forwarding, TLS         retries/timeouts; owner
                          mismatch                and fallback documented

  Data                    lag, stale replica,     one write authority;
                          divergent writes        block unsafe promotion;
                                                  reconcile

  Traffic                 false-positive health,  measure client-observed
                          client cache tail       success; TTL is not
                                                  total recovery

  Policy                  version skew, stale     quarantine/UNKNOWN; no
                          report, bypass          promotion

  Telemetry               hub down, label         local alerting,
                          collision, cardinality  absent-cluster
                          surge                   detection, bounded cost

  Host                    memory/disk exhaustion  abort, preserve safe
                                                  evidence, verify
                                                  cleanup
  -----------------------------------------------------------------------

**Fidelity reminder:** the diagram represents logical roles, not
independent regions.

## 4. ADR-001: topology choice

**Status:** `[ASSUMPTION]` proposed for the lab; review before
implementation.

**Decision:** use two small kind clusters with exact names and distinct
pod/service CIDRs. Use one GitOps hub for the exercise, retain local
alerts, keep the data tier single-writer, and use a local DNS-like state
machine plus a proxy variant.

Scores below are `[ILLUSTRATIVE]`, 1 (poor) to 5 (strong), not measured
values.

  -----------------------------------------------------------------------------
  Criterion                 Weight    One cluster Two local kind   Real regions
                                                        clusters 
  ----------------- -------------- -------------- -------------- --------------
  Blast-radius                 20%              2              4              5
  learning                                                       

  Zero-budget                  20%              5              5              1
  feasibility                                                    

  Reproducibility              15%              5              4              3

  Real                         20%              1              1              5
  region-failure                                                 
  fidelity                                                       

  Fleet/GitOps                 15%              1              4              5
  learning                                                       

  Operational                  10%              5              3              1
  simplicity                                                     

  **Weighted score        **100%**       **3.05**       **3.45**       **3.60**
  / 5**                                                          
  -----------------------------------------------------------------------------

Real regions are outside budget; two local clusters are selected for
learning, not production assurance. Costs include extra networking,
identity, telemetry and on-call complexity. Alternatives: single
cluster; managed multi-region services; optional Cluster API with Docker
provider only if versions/resources are verified; optional mesh; true
GSLB (not feasible free). Review when requirements, budget, platform or
provider change.

## 5. Proposed repository layout

These are proposed implementation paths, not files created by this task.

``` text
project-root/
├── fleet/{registry,cidr-plan,inventory,lifecycle}/
├── gitops/{hub,applicationsets,rings,platform-bundle,apps}/
├── connectivity/{exposure,dns,trust}/
├── traffic/{dns-server,gslb-controller,client-harness,proxy-variant}/
├── data/{replication,canary,verification,model-gating}/
├── observability/{per-cluster,aggregation,slos,alerts,dashboards}/
├── governance/{policies,conformance,rbac,credential-inventory}/
├── chaos/  drills/  evidence/  runbooks/  sim/  docs/  scripts/
├── Makefile
└── versions.txt
```

  -----------------------------------------------------------------------
  Path                                Purpose
  ----------------------------------- -----------------------------------
  `fleet/registry`                    non-secret identity, ownership,
                                      tier, lifecycle

  `fleet/cidr-plan`                   network plan and overlap tests

  `fleet/inventory`                   actual contexts, versions and
                                      support checks

  `fleet/lifecycle`                   guarded create/replace/decommission

  `gitops/hub`                        one selected controller and scoped
                                      identities

  `gitops/applicationsets`            selector and exact fan-out preview

  `gitops/rings`                      ring membership, health gate, halt,
                                      rollback, quarantine

  `connectivity`                      endpoint, TLS/trust and
                                      allowed-path definitions

  `traffic`                           local resolver, controller state
                                      machine, client log and proxy

  `data`                              replication, canary, write ledger,
                                      hash/divergence gates

  `observability`                     per-cluster scrape, SLOs, alerts
                                      and dashboards

  `governance`                        one policy engine, conformance,
                                      RBAC and metadata-only inventory

  `chaos`, `drills`, `sim`            bounded faults, game-master phases,
                                      deterministic tests

  `evidence`, `runbooks`, `docs`      audit bundle, operational
                                      procedures and ADRs

  `scripts`, `Makefile`,              guards, validators, test
  `versions.txt`                      orchestration and actual tool
                                      versions
  -----------------------------------------------------------------------

`Projects/README.md` is a companion index/grading/resource plan and is
not generated or rewritten here.

## 6. Profiles, resource budget, and sequencing

The following are proposed profiles, not upstream product tiers.

  -----------------------------------------------------------------------
  Profile                 Components              Stop list
  ----------------------- ----------------------- -----------------------
  **Fleet-Core**          two kind clusters,      no optional controllers
                          context guard,          or full telemetry
                          registry/CIDR           
                          validation, tiny        
                          inference service,      
                          deterministic           
                          traffic/write ledger,   
                          evidence                

  **Fleet+GitOps**        Core plus one GitOps    stop data stack and
                          controller and local    full telemetry first
                          Git server              

  **Fleet+Data**          Core plus PostgreSQL    stop GitOps hub and
                          replica or write-ledger full telemetry
                          simulator, object-store 
                          simulation, DNS/proxy   

  **Minimal               minimal metrics, local  avoid full tracing/log
  Observability**         alert check and         stack
                          conformance scanner     

  **Full (optional)**     cross-cluster tracing   fall back immediately
                          or mesh only if         on pressure
                          headroom allows         
  -----------------------------------------------------------------------

Footprint numbers must be measured; do not promise all components fit
within 8 GB. Before each profile record CPU, memory, disk, ports, Docker
status, available time and cleanup window. If pressure is high, use
Core/synthetic mode.

Sequencing: (1) preflight; (2) cluster config, registry, CIDR and
context guard; (3) sample service; (4) traffic harness; (5) data
role/write ledger; (6) GitOps rings; (7) minimal
observability/conformance; (8) synthetic game-master; (9) one bounded
experiment at a time; (10) failover/reconciliation/fail-back; (11)
evidence/postmortem; (12) teardown. Each phase stops until the prior
gate has fresh evidence.

## 7. Preflight and hard gates

Record OS/runtime, tool versions, CPU/memory/disk, Docker health, ports,
contexts, CIDRs, profile, time available and abort owner.

  -----------------------------------------------------------------------------
  Gate                    Test                      No-go condition
  ----------------------- ------------------------- ---------------------------
  G1                      enumerate contexts, exact unknown/ambiguous/non-lab
                          allow-list                target

  G2                      registry required fields  missing owner, CIDR,
                                                    lifecycle or identity

  G3                      pairwise CIDR + host      unintended overlap
                          route check               

  G4                      wrong-target negative     any mutation proceeds
                          test                      

  G5                      cleanup plan reviewed     unknown cleanup scope

  G6                      resource headroom         host pressure or no cleanup
                          measured                  window

  G7                      versions/docs checked or  mutation-critical
                          component simulated       compatibility unknown

  G8                      write-authority/fencing   writes possible while
                          gate defined              authority is unknown
  -----------------------------------------------------------------------------

Read-only preflight commands (not executed here):

``` bash
uname -a
docker version
kind version
kubectl version --client
docker info
df -h
free -h
nproc
kubectl config get-contexts -o name
```

## 8. Fleet, registry, CIDRs, and lifecycle

### 8.1 Registry

`fleet/registry/clusters.yaml`

``` yaml
schemaVersion: 1
clusters:
  - name: stage2e-east-lab
    id: east-lab
    environment: lab
    regionLabel: east
    tier: canary
    owner: platform-lab
    kubernetesVersion: "[RECORD_ACTUAL_VERSION]"
    podCIDR: 10.240.0.0/16
    serviceCIDR: 10.96.0.0/16
    credentialType: local-kubeconfig-reference
    lifecycleState: planned
    context: kind-stage2e-east-lab
  - name: stage2e-west-lab
    id: west-lab
    environment: lab
    regionLabel: west
    tier: standard
    owner: platform-lab
    kubernetesVersion: "[RECORD_ACTUAL_VERSION]"
    podCIDR: 10.241.0.0/16
    serviceCIDR: 10.97.0.0/16
    credentialType: local-kubeconfig-reference
    lifecycleState: planned
    context: kind-stage2e-west-lab
```

These CIDRs are proposed values, not proof of compatibility with local
Docker/VPN routes. Validate pod, service and host ranges before
creation. kind fields such as `networking.podSubnet` and `serviceSubnet`
are `[VERIFY]` for the selected kind version. Demonstrate default
overlap using a controlled fixture, not by assuming every kind setup is
identical.

`fleet/cidr-plan/overlap-fixture.json` `[SYNTHETIC]`

``` json
{"networks":[{"name":"east-pods","cidr":"10.20.0.0/16"},{"name":"west-pods","cidr":"10.20.0.0/16"}],"expected":"FAIL_OVERLAP"}
```

Acceptance: overlapping fixture fails; chosen plan passes; actual config
and host routes are recorded.

### 8.2 Context guard reference

`scripts/kctl` --- minimal teaching wrapper, not production-grade safety
boundary:

``` python
#!/usr/bin/env python3
import argparse, subprocess, sys

ALLOWED = {
    "stage2e-east-lab": "kind-stage2e-east-lab",
    "stage2e-west-lab": "kind-stage2e-west-lab",
}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--target", required=True, choices=sorted(ALLOWED))
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("args", nargs=argparse.REMAINDER)
    a = p.parse_args()
    if a.args and a.args[0] == "--":
        a.args = a.args[1:]
    if not a.args:
        p.error("kubectl arguments required")
    if any(x == "--context" or x.startswith("--context=") for x in a.args):
        print("REFUSE: --target is the only target selector", file=sys.stderr)
        return 22
    context = ALLOWED[a.target]
    try:
        known = subprocess.run(
            ["kubectl", "config", "get-contexts", "-o", "name"],
            check=True, capture_output=True, text=True, timeout=10
        ).stdout.splitlines()
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"REFUSE: cannot enumerate contexts: {e}", file=sys.stderr)
        return 20
    if context not in known:
        print(f"REFUSE: expected context missing: {context}", file=sys.stderr)
        return 21
    cmd = ["kubectl", "--context", context, *a.args]
    if a.dry_run:
        print("DRY-RUN:", " ".join(cmd))
        return 0
    try:
        return subprocess.run(cmd, timeout=60).returncode
    except subprocess.TimeoutExpired:
        return 124

if __name__ == "__main__":
    raise SystemExit(main())
```

This wrapper only makes target selection explicit. Before any high-risk
use, add trusted cluster-marker verification, mutation-verb/resource
allow-lists, namespace restrictions, audit logs, per-command timeouts
and safe deletion policy. Never treat this example alone as a production
security boundary.

### 8.3 Registry validator contract

`scripts/validate_registry.py` must parse CIDRs using a standard
IP-network library, reject invalid or duplicate cluster identities,
require the two exact names and all required fields, compare every
pod/service range for overlap, and compare registry values with actual
cluster configs and host routes. Pin YAML dependencies and record
versions. Expected behavior: overlap fixture exits non-zero; valid plan
passes. No test was executed during authoring.

### 8.4 Inventory and lifecycle

`fleet/inventory/report-template.md`

  --------------------------------------------------------------------------------------------------------------
  Cluster              Context    Kubernetes   Support      Owner          Lifecycle   Conformance   Timestamp
                                  version      check                                                 
  -------------------- ---------- ------------ ------------ -------------- ----------- ------------- -----------
  `stage2e-east-lab`   `[OPEN]`   `[RECORD]`   `[VERIFY]`   platform-lab   planned     UNKNOWN       blank

  `stage2e-west-lab`   `[OPEN]`   `[RECORD]`   `[VERIFY]`   platform-lab   planned     UNKNOWN       blank
  --------------------------------------------------------------------------------------------------------------

Lifecycle state machine:
`planned → validated → creating → ready → draining → replacing/decommissioning → deleted → verified`.
Unknown transitions fail closed. Use kind-config-as-code for the
zero-budget path. Cluster API with Docker provider (CAPD) is
Awareness/optional; use only if provider compatibility, resource
headroom and WSL2/Linux behavior are verified.

Blue/green sequence: snapshot registry; verify
target/version/CIDR/capacity; create replacement; apply baseline/policy;
verify workload/telemetry; compare config; move a small ring after
gates; keep old cluster until data ownership, telemetry, credentials,
GitOps registrations and routes are checked; decommission with dry-run
inventory; verify no workloads, registrations, credentials, data owners,
telemetry targets or leftover resources.

Management-plane loss drill: simulate hub unavailability; verify
workloads and local alerts; pause changes; recover hub from reviewed
configuration; enumerate actual clusters; compare revision, policy and
quarantine; reconcile one cluster at a time; resume only after fresh
evidence.

Negative tests: wrong context, missing target, unregistered cluster,
CIDR overlap, unsafe deletion, stale version inventory and hub
unavailable. Expected result is fail-closed/non-zero or UNKNOWN, never
silent pass.

## 9. GitOps, rings, and integrity gates

Use one controller only for the required path: Argo CD with
ApplicationSet cluster generators is the intended example. Do not run
Argo CD and Flux together. Exact ApplicationSet fields, labels, pruning,
API schemas and version compatibility are `[VERIFY]`.

`gitops/rings/rings.yaml`

``` yaml
rings:
  - name: ring-0
    members: [stage2e-east-lab]
    purpose: canary
    promotionRequires:
      - fresh-per-cluster-health
      - regional-slo-pass
      - conformance-pass
      - policy-version-compatible
      - rollback-revision-known
  - name: ring-1
    members: [stage2e-west-lab]
    purpose: next-wave
    promotionRequires:
      - ring-0-approved
      - fresh-per-cluster-health
      - regional-slo-pass
      - conformance-pass
```

Before sync, produce an impact report with revision/digest, exact target
cluster/context set, labels, ring, quarantine status, evidence
freshness, dependency order, changed/pruned/deleted resources and
rollback revision. A selector is not a substitute for reviewing resolved
targets.

`gitops/platform-bundle/order.yaml`

``` yaml
components:
  - name: namespaces-and-labels
    dependsOn: []
  - name: CRDs-and-controllers
    dependsOn: [namespaces-and-labels]
  - name: policy-engine
    dependsOn: [CRDs-and-controllers]
  - name: policy-baseline
    dependsOn: [policy-engine]
  - name: observability-prerequisites
    dependsOn: [namespaces-and-labels]
  - name: regional-services
    dependsOn: [policy-baseline, observability-prerequisites]
  - name: data-role-and-canary
    dependsOn: [regional-services]
```

CRDs/controllers must be ready before dependent custom resources. Map
this contract to the selected controller's supported mechanism after
verification.

ApplicationSet intent (not validated for apply):

``` yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: regional-inference
spec:
  generators:
    - clusters:
        selector:
          matchLabels:
            environment: lab
            platform-ready: "true"
  template:
    metadata:
      name: 'inference-{{name}}'
    spec:
      project: default
      source:
        repoURL: "[LOCAL_GIT_REPOSITORY_URL]"
        targetRevision: "[REVIEWED_COMMIT_OR_DIGEST]"
        path: "gitops/apps/inference/overlays/{{name}}"
      destination:
        server: '{{server}}'
        namespace: inference
```

Do not apply unchanged. Validate API fields, project restrictions,
repository, target selection and prune/delete semantics for the actual
Argo CD version. Cluster labels must be set by a trusted registration
workflow.

Gate contract: halt on FAIL, UNKNOWN, UNREACHABLE, stale evidence or
ambiguous target. Sync success is not application health. Plant a bad
image/config fixture in ring 0; acceptance is that the gate catches it
and ring 1 does not advance. Rollback only to a known-good revision
after checking data/schema compatibility, then verify health per
cluster.

Deletion guard refuses unknown target, broad target set, deletion of a
namespace with data owner/tenant, removal of sole control plane without
recovery plan, or prune without a fresh impact report.

Hub-down/rebuild: preserve last trusted revision; pause rollout; inspect
local workload/alerts; restore hub from reviewed config; rotate
credentials if compromise suspected; compare both clusters' revisions,
policies and quarantine; reconcile one cluster at a time.

Admission integrity: use M12's verified equivalent or a selected
signature-verification mechanism. Exact APIs/CRDs are `[VERIFY]`.
Negative test uses a disposable unsigned/wrong-digest fixture; admission
must deny it, and a central desired-state change alone must not bypass
the gate. If resource limits require simulation, label `[SIMULATED]`; do
not claim cryptographic enforcement.

## 10. Connectivity, TLS, and isolation

`connectivity/exposure/endpoints.yaml`

``` yaml
endpoints:
  - id: east-inference
    cluster: stage2e-east-lab
    region: east
    baseURL: "[OBSERVED_LOCAL_EAST_ENDPOINT]"
    readinessPath: /ready
    owner: inference-platform
  - id: west-inference
    cluster: stage2e-west-lab
    region: west
    baseURL: "[OBSERVED_LOCAL_WEST_ENDPOINT]"
    readinessPath: /ready
    owner: inference-platform
```

Use explicit connection/request timeouts, bounded retries with backoff,
circuit breaker/bulkhead, trace/correlation ID and idempotency keys. Do
not blindly retry non-idempotent writes.

Start with default-deny NetworkPolicy and allow only documented flows.
Exact enforcement depends on CNI `[VERIFY]`. Positive tests: approved
client reaches inference, approved health probe reaches readiness,
metrics scrape reaches only intended target. Negative tests: unapproved
namespace cannot reach inference; unrelated workload cannot reach
database; east-to-west call is denied unless in dependency allow-list.
Record caller, target, port, policy, result and timestamp.

Use a local lab CA only if existing M04 tooling is available. Never
store private keys in the repository/evidence. Verify SAN, issuer,
expiry, peer identity and trust bundle. If mTLS is too heavy, use
deterministic trust-state simulation and label it. Rotation sequence:
capture known-good fingerprint/request; stage trust overlap if
supported; rotate one endpoint; verify; rotate the second; remove old
trust only after both pass; abort/restore known-good bundle if error
threshold is breached.

If one cluster/shared host is the only DNS forwarder, its failure may
make another cluster appear unreachable. Document each dependency's
caller, target, owner, timeout, fallback and failure behavior.
Compromised-cluster isolation: stop rollout eligibility and routing
weight, preserve evidence, isolate only after the target guard and lease
pass, then verify the other cluster's health, data authority and alert
path.

## 11. Local traffic simulation

Use a deterministic DNS-like resolver, health checker, GSLB-like state
machine and client harness; compare with a proxy-based upstream switch.
This is not real GSLB.

``` text
PREFLIGHT -> BASELINE -> DEGRADED_SIGNAL -> DECISION_PENDING
  -> alternate eligible?
  -> data authority confirmed?
  -> gradual traffic shift -> client verification -> stabilization
  -> failover recorded -> fail-back precheck -> reconciliation/fencing
  -> gradual return -> postcheck -> CLOSED
```

If the alternate is unhealthy or data authority is unknown, fail
static/manual and keep writes blocked. Health-check threshold/hysteresis
avoids switching on a single transient probe.

Observed recovery includes detection, decision, propagation, client
cache/connection tail and warm-up. These components can overlap;
calculate elapsed time from an event timeline instead of assuming the
sum is exact. TTL is not a hard bound on client recovery.

`traffic/measurement-template.csv`

``` csv
run_id,profile,variant,client_behavior,ttl_seconds,probe_interval_seconds,threshold,detect_time_utc,decision_time_utc,alternate_first_success_utc,consistent_success_utc,p50_ms,p95_ms,p99_ms,assumptions,result,caveats
```

`[ILLUSTRATIVE]` sequential timing example: detection 18 s + decision 7
s + propagation/cache 35 s + client retry/connection tail 22 s + warm-up
13 s = 95 s. Not measured, not an SLA. Test transient probe failure,
sustained failure, both endpoints unhealthy, stale client cache, invalid
TLS and healthy endpoint with unknown data authority.

## 12. Regional serving and capacity

### Active-active inference

Both clusters serve a stateless API; each response must include
`cluster`, `region`, `model_alias` and `request_id`. The end-to-end
client test must prove requests reach both cluster identities. Expected
schema only, not captured output:

``` json
{"service":"inference-api","region":"east","cluster":"stage2e-east-lab","model_alias":"stable","request_id":"generated"}
```

### N+1 arithmetic

\[ `\text{surviving safe capacity}`{=tex}
`\geq `{=tex}`\text{total peak demand after evacuation}`{=tex} \]

`[ILLUSTRATIVE]`: east 600 requests/s, west 400 requests/s, west safe
capacity 700 requests/s. East loss creates 1,000 requests/s demand;
utilization is (1000/700 `\approx 142.9`{=tex}%). Full evacuation is
unsafe. Add capacity, shed noncritical load, partially shift or declare
controlled brownout. Measure CPU, memory, model load, downstream limits,
queues and telemetry; local laptop tests do not prove production
capacity.

### Read-local/write-primary and tenant home region

Reads can be local only within the data class's staleness tolerance.
Writes go only to the verified primary. Read-your-writes may require
session routing, version tokens or waiting for freshness. Unknown
authority means reject/queue writes safely.

`data/verification/tenant-home-region.csv`

``` csv
tenant_id,home_region,write_owner,migration_state,verification_evidence
tenant-demo-01,east,east,stable,[OPEN]
tenant-demo-02,west,west,stable,[OPEN]
```

Migration:
`stable → planned → writes-paused-or-fenced → data-copied → parity-verified → routing-updated → canary-verified → stable`.
Abort on missing owner, incomplete copy, conflicting authority or failed
parity.

Multi-writer toy `[SYNTHETIC]`: east has balance 110/version 8; west has
105/version 8; both derived from version 7. Preserve both and apply
explicit ownership/version/merge policy; do not choose by wall-clock
timestamp alone. Financial data should not casually use last-write-wins.

Readiness requires fresh cluster/endpoint, workload/model hash,
capacity, data role/lag/canary, valid credentials/trust, conformance
PASS, local alerts, dependency health, rollback and evidence path.

## 13. Data replication and consistency

### Consistency matrix

`data/consistency-matrix.csv`

``` csv
data_class,source_of_truth,write_pattern,staleness_tolerance,loss_tolerance,failover_action,verification_evidence
system_of_record,east-primary,single-writer,none-for-authoritative-write,declared-RPO-only,verify-promotion-and-fence,write-ledger-and-replica-canary
session_cache,regional-cache,local-write,seconds,loss-tolerant,rebuild-or-expire,cache-rebuild-check
model_artifact,immutable-artifact-store,content-addressed,none-before-promotion,no-silent-corruption,replicate-and-hash-check,sha256-manifest
model_alias,registry-control-plane,guarded-single-owner,none-for-release-pointer,low-with-audit,freeze-alias-until-artifact-ready,alias-history-and-hash
feature_store,declared-per-dataset,per-dataset,explicit-per-feature,explicit-per-feature,stale-read-policy,lag-and-version-canary
ETL-checkpoint,job-owner,region-pinned-or-explicitly-mirrored,job-specific,job-specific,replay-idempotently,checkpoint-and-replay-log
audit-log,append-only-source,ordered-append,policy-defined,very-low,verify-completeness-and-order,sequence-gap-report
tenant-config,declared-owner,home-region-write,explicit-bounded-window,declared,freeze-and-reconcile,version/parity-report
metrics,regional-telemetry,append/aggregate,windowed,loss-tolerant-within-budget,continue-local-collection,local-buffer-and-central-ingest
billing-ledger,authoritative-ledger,single-writer-or-governed,none-for-authoritative-write,explicitly-bounded,manual-guarded-promotion,ledger-reconciliation
```

Synchronous replication waits for remote acknowledgement under the
selected guarantee but increases latency and can reduce write
availability during partition. Asynchronous replication lowers write
latency but permits lag and possible acknowledged-write loss on
promotion. Choose per data class; a deterministic simulator is
acceptable only when labelled `[SIMULATED]`.

### PostgreSQL path and lag

Intended real path: PostgreSQL primary in east and standby in west.
Exact settings, images, queries, slot/WAL behavior and compatibility are
`[VERIFY]` against the selected PostgreSQL release. Record
primary/standby identity, timeline, lag distribution, canary sequence,
acknowledgement ledger, WAL/slot retention and disk headroom.

Measure lag from a monotonic canary sequence and sampling interval;
timestamps require clock uncertainty. p99.9 lag is a risk signal, not an
exact count of lost writes. Pause/throttle backfill when the declared
lag threshold is breached or measurement is UNKNOWN. Resume only after
fresh stable evidence.

Bounded partition/pause: use deterministic simulation by default; real
pause only in an isolated disposable lab with short lease and tested
abort. Acceptance: lag alert fires, fault expires/aborts, replication
resumes, sequence gaps/parity are checked and one writer remains
authoritative.

WAL/replication slots: a stalled consumer may prevent WAL cleanup and
grow disk. Monitor slot state, retained bytes, lag and filesystem
headroom. Never drop a slot as generic cleanup without understanding
consequences.

`data/verification/write-ledger.csv` `[SYNTHETIC]`

``` csv
seq,write_id,primary_acknowledged,visible_on_promoted_standby
1001,w-1001,true,true
1002,w-1002,true,true
1003,w-1003,true,false
1004,w-1004,true,false
1005,w-1005,false,false
```

In this synthetic ledger, 1003 and 1004 are two acknowledged writes
missing after promotion. 1005 was not acknowledged and is not counted.
This does not represent an actual promotion. Reconcile the ledger and
recovered data before final classification.

Reconciliation: freeze competing writes; preserve both histories;
compare sequence IDs, idempotency keys, versions and hashes; classify
missing acknowledged writes, unacknowledged operations, duplicates and
conflicts; apply domain policy; verify invariants; resume only after
authority/consistency gates pass.

### Object store, model alias and schema

Replicate a harmless object and deletion marker; check hash, metadata
and delete propagation. **Replication is not backup** because
deletion/corruption can replicate; M13 owns immutable backup and restore
verification.

`data/model-gating/promotion-contract.yaml`

``` yaml
modelAlias: stable
promotionRequires:
  - artifactPresentInTarget
  - expectedHashMatchesObservedHash
  - manifestComplete
  - modelVersionCompatible
  - targetPolicyConformant
  - targetHealthFresh
  - ownerApprovalRecorded
onFailure:
  - blockAliasPromotion
  - preserveEvidence
  - keepPreviousAlias
```

Hash command/tool is `[VERIFY]`. Wrong hash, incomplete artifact or
non-conformant target blocks alias promotion. Divergence detector
distinguishes missing, stale and unequal data. Use expand/contract
schema evolution: add backward-compatible schema, deploy compatible
readers/writers, backfill with lag monitoring, verify both regions,
switch under a gate, contract only when every consumer is verified.

## 14. Observability and policy governance

Per-cluster Prometheus identity must include unique `cluster` and
`region` labels. Verify the selected scrape/export config; duplicate
labels can merge failure domains.

Global event-weighted success ratio:

\[
`\text{global ratio}`{=tex}=`\frac{\sum_i \text{good events}_i}{\sum_i \text{eligible events}_i}`{=tex}
\]

`[ILLUSTRATIVE]`: east 99,900/100,000; west 600/1,000. Global =
100,500/101,000 ≈ 99.505%, while west is only 60%. Keep regional
guardrails and worst-cluster panels.

`observability/slos/region-success-ratio.rules.yaml` `[INTENT EXAMPLE]`

``` yaml
groups:
  - name: regional-slo
    rules:
      - alert: RegionalSuccessRatioBelowObjective
        expr: |
          sum by (cluster, region) (rate(http_requests_total{status=~"2.."}[5m]))
          /
          sum by (cluster, region) (rate(http_requests_total[5m]))
          < 0.99
        for: 5m
        labels:
          severity: page
```

Metric labels, zero denominator and absent-series behavior must be
verified. Test healthy regions, one bad region hidden by global
aggregation, missing cluster series, stale heartbeat, zero denominator
and recovery with `promtool`; do not claim tests passed without output.
`amtool` route tests are `[VERIFY]`.

`governance/conformance/required-dimensions.yaml`

``` yaml
dimensions:
  - cluster-version-support
  - required-baseline-components
  - cluster-and-region-labels
  - pod-security-standard-labels
  - default-deny-network-policy
  - admission-policy-presence-and-mode
  - unexpected-cluster-admin-bindings
  - image-signature-policy
  - audit-logging
  - encryption-at-rest-evidence-where-inspectable
statusSemantics:
  PASS: fresh evidence meets requirement
  FAIL: fresh evidence proves violation
  UNKNOWN: missing, stale, unsupported or ambiguous
  UNREACHABLE: cluster could not be queried
rolloutEligibility:
  requireAllCriticalDimensionsPass: true
  unknownIsGreen: false
  unreachableIsGreen: false
```

An uninspectable check is UNKNOWN, not PASS. Plant missing policy or
unexpected cluster-admin binding; scanner must return FAIL and ring
advancer must skip that cluster. Recheck eligibility immediately before
promotion to avoid time-of-check/time-of-use races.

Choose one policy engine---Kyverno or ValidatingAdmissionPolicy
(VAP)---after verifying support for the selected Kubernetes release. Do
not mix both in the required path. Roll out audit → warn → enforce by
rings. Before enforcement verify compatibility, report freshness, denial
rate, exception owner/scope/expiry, rollback, observed per-cluster mode
and independent bypass alert. Version-skew UNKNOWN blocks enforcement.

Credential inventory is metadata only: identifier, owner role, scope,
type, review/expiry and rotation status. Never print tokens, kubeconfigs
or private keys. Hub compromise tabletop: stop fan-out, preserve audit,
scope reachable clusters, rotate/revoke through approved process,
independently inspect both clusters and restore trusted state only after
verification.

Measure series count, sample rate, bytes, queue depth and disk impact if
running telemetry. Otherwise use synthetic calculations labelled
`[ILLUSTRATIVE]`. Avoid request/user IDs and raw URLs as metric labels;
no fabricated prices.

## 15. Game-master simulation

### State machine and harness contract

``` text
CREATED -> PREFLIGHT -> BASELINE -> PHASE_1_BAD_RING
 -> PHASE_2_LAG -> PHASE_3_EAST_LOSS -> PHASE_4_INJECT
 -> FAILBACK_RECONCILIATION -> EVIDENCE_REVIEW -> CLOSED
Any state -> ABORT_REQUESTED -> CLEANUP -> CLOSED or CLEANUP_FAILED
```

`sim/harness-contract.yaml`

``` yaml
mode: synthetic-by-default
networkCalls: disabled-by-default
shellFromScenarioData: forbidden
allowedClusters: [stage2e-east-lab, stage2e-west-lab]
requireBeforeEveryAction: [explicitTarget, allowList, allowedTransition, validFaultLease, validDeadline]
abortTriggers: [manualAbort, wrongTarget, deadlineExceeded, criticalSLOBreach, memoryOrDiskThreshold, unexpectedState, cleanupFailure]
exitNonzeroOn: [cleanupFailure, verificationFailure]
replaySeedRange: "0..9999"
recordActualChosenDelays: true
```

The manifest contains run ID, variant, seed, mode, allowed clusters,
deadline, phase triggers, observations, hidden cause IDs, fault leases,
abort criteria and evidence IDs. Do not parse scenario values into shell
commands. Hidden causes may be withheld, but safety warnings and stop
conditions must never be hidden. Required tests: wrong target, missing
allow-list, expired inject, abort trigger, unexpected transition,
cleanup failure, same-seed replay and variant distinction.

### Learner-facing Variant A

**A1 --- bad fleet change.** A ring-0 change is synced; east's regional
success falls; west is not yet targeted. Halt promotion, preserve
revision/target report, determine affected cluster, rollback only if
compatible, verify each cluster.

Hints: (1) inspect ring/revision/regional SLO; (2) compare sync status
to runtime health; (3) halt, preserve evidence, rollback safely and
verify per cluster.

**A2 --- lag during backfill.** Lag rises and canary trails while
maintenance approaches. Inspect lag distribution, canary, write ledger,
backfill rate and WAL/disk. Pause/throttle if objective breached; do not
infer exact lost writes from p99.9 alone.

Hints: (1) inspect lag and canary; (2) correlate backfill, retained WAL
and freshness; (3) pause load and require fresh stable evidence.

**A3 --- east "region" loss.** Endpoint unavailable; central telemetry
delayed; west capacity and old-writer state uncertain. Assign roles,
communicate uncertainty, verify data/capacity/authority, promote only
through approved process, fence old writer before writes, shift
gradually, measure client tail and quantify loss only from supplied
ledger, then hand off IC.

Hints: (1) inspect local health/data role/capacity; (2) endpoint
reachability is not write authority; (3) keep writes blocked until
promotion/fencing proof.

**A4 --- inject.** Facilitator selects missing lab trust material,
unmirrored model artifact, stale cache tail, expired lab credential or
reseed requirement. Identify failed gate, repair via approved path,
verify fresh evidence, preserve blocked action.

Hints: (1) inspect readiness/conformance; (2) compare
hash/trust/credential/cache/lag evidence; (3) stop, repair, rerun gate.

**Fail-back:** east returns. Verify version, policy, credentials, data
divergence, capacity and ownership. Reconcile with one writer, shift
gradually and verify client/SLO/lag.

### Learner-facing Variant B

Different symptom order and causes: west conformance is stale and policy
capability unknown; model alias points to artifact with wrong hash; east
health probe intermittently reports success; later stale client cache
continues sending to east after endpoint loss. Reconstruct timeline,
quarantine west, block alias promotion, distinguish false-positive
probes from actual endpoint loss, keep writes blocked until
authority/fencing and capacity pass, then perform gated failover and
fail-back.

Hints: (1) compare report freshness, artifact manifest/hash, probes and
client logs; (2) test independent health signals; (3) quarantine/block,
preserve evidence, verify authority and shift gradually.

### Facilitator answer key --- Variant A

**Hidden causes:** bad revision passes sync but fails regional SLO;
backfill causes lag/RPO risk; east endpoint loss leaves writer status
uncertain; synthetic ledger contains two acknowledged writes absent from
promoted standby.

**Expected decisions:** stop ring progression; preserve
target/revision/SLO; rollback only after compatibility check; pause
backfill and inspect lag/canary/WAL/disk; keep writes blocked until west
freshness/capacity and old-writer fencing are proven; shift gradually;
quantify only acknowledged writes missing in ledger; reconcile before
fail-back.

**Acceptable alternatives:** wait for fresh evidence; remain read-only;
use deterministic simulator if real replication is infeasible; choose a
reviewed forward fix if rollback is unsafe.

**Traps:** promote solely because east is down; treat sync as health;
route writes before fencing; infer exact loss from lag percentile; fail
back when endpoint returns; accept stale conformance; clean up before
evidence.

**Evidence:** run ID/seed, state transitions, target set, revision, SLO,
lag/canary, write ledger, fencing, capacity, client records, traffic
shifts, reconciliation, cleanup and postmortem.

### Facilitator answer key --- Variant B

**Hidden causes:** stale west conformance means UNKNOWN; model artifact
hash mismatch; east probe has false-positive success; client cache
extends observed failures after endpoint loss.

**Expected decisions:** quarantine west pending fresh report and
compatible policy; block model alias until hash/manifest passes; use
probe history and independent signals; measure client tail separately
from DNS/controller; keep writes blocked until
authority/fencing/capacity pass; fail back only after reconciliation and
fresh readiness.

**Traps:** stale report treated green; filename treated as hash proof;
one successful probe treated as regional health; TTL treated as upper
bound; routing treated as promotion.

### Scoring

Score 0--4 each: decision under uncertainty; data-loss reasoning;
blast-radius discipline; fencing/promotion/write order; communication/IC
handoff; per-cluster/client verification; RTA/RPA/client-tail evidence;
inject response; fail-back/reconciliation; evidence/cleanup. 0
absent/unsafe; 1 major gaps; 2 partial; 3 sound with minor omissions; 4
correct, evidenced and bounded. Suggested thresholds `[ASSUMPTION]`:
below 24/40 remediate; 24--31 replay weak phases; 32--36 strong lab
performance; 37--40 evidence review complete. A score alone does not
establish production readiness.

## 16. Bounded resilience experiments

All experiments are lab-only and default to deterministic simulation.
Real fault mechanisms require preflight, explicit target identity,
bounded lease, tested abort and cleanup. One fault at a time.

  --------------------------------------------------------------------------------------------------
  ID             Hypothesis/profile     Fault and bound    Abort / dry-run         Evidence /
                                                                                   acceptance
  -------------- ---------------------- ------------------ ----------------------- -----------------
  E1             client retries remain  synthetic          abort on                request timeline,
  latency/loss   bounded; Core          delay/loss ≤30 s   deadline/SLO/host       retry count,
                                        `[ILLUSTRATIVE]`   pressure; dry-run event timeout behavior
                                                           only                    

  E2 endpoint    switch only after      mark one endpoint  lease restores map;     client endpoint
  failure        health gate; Core      down ≤30 s         abort if both unhealthy log and state
                                                                                   transitions

  E3 resolver    DNS dependency is      fail local         restore on expiry;      resolver/client
  failure        visible; Fleet+Data    resolver state ≤20 dry-run state only      tail and alert
                                        s                                          

  E4 replication lag alert blocks       pause synthetic    abort on                lag/canary, write
  pause          maintenance;           replication ≤30 s  disk/memory/authority   ledger,
                 simulator/data profile                    ambiguity               resume/parity

  E5 capacity    evacuation blocked if  bounded synthetic  abort on declared       capacity formula
  stress         capacity insufficient; load               resource/error          and
                 Core                                      threshold               brownout/shift
                                                                                   decision

  E6 hub outage  local workload/alerts  mark hub           watchdog restores;      local signals,
                 persist;               unavailable ≤60 s  manual abort            hub state,
                 GitOps/simulation                                                 pause/reconcile
                                                                                   evidence

  E7 trust       invalid trust is       invalid trust      abort if recovery fails fingerprint
  failure        detected and           fixture                                    metadata, denied
                 reversible; simulation                                            then valid
                                                                                   request

  E8 cardinality series gate catches    add synthetic      stop at local resource  series/bytes
  regression     growth; minimal        high-cardinality   threshold               delta and
                 telemetry/simulation   dimension                                  rollback
  --------------------------------------------------------------------------------------------------

`chaos/lease-contract.yaml`

``` yaml
mode: synthetic-by-default
maxFaultSeconds: 60
require: [explicitTarget, exactAllowList, preflightPass, baselineEvidence, cleanupRecorded]
abortOn: [manualAbort, deadlineExceeded, leaseExpired, wrongTarget, criticalSLOBreach, memoryOrDiskThreshold, unexpectedState, cleanupFailure]
onAbort: [stopTransitions, restoreKnownGoodState, verifyFaultInactive, preserveEvidence, nonzeroIfCleanupUnverified]
```

A `finally` block alone does not guarantee cleanup after host
termination; if an independent watchdog is unavailable, use synthetic
mode. Negative test: substitute a production-like context in the
fixture; guard rejects before fault begins, logs `ABORT_WRONG_TARGET`,
performs no mutation and returns non-zero.

## 17. Evidence and measurements

### Evidence bundle

``` text
evidence/<run-id>/
├── run.json
├── versions.txt
├── registry-redacted.yaml
├── preflight.txt
├── guard-tests.txt
├── target-impact-report.json
├── event-timeline.csv
├── rollout-and-ring-state.json
├── per-cluster-slo/
├── global-slo/
├── replication-lag.csv
├── write-ledger-redacted.csv
├── client-requests.csv
├── capacity-worksheet.csv
├── conformance-reports/
├── policy-rollout/
├── experiment-results/
├── cleanup-verification.txt
├── postmortem.md
└── manifest.sha256
```

Do not include kubeconfigs, tokens, private keys, passwords or sensitive
data. Record run ID, timestamps, scenario/seed, source revision, actual
tool versions, cluster metadata, profile, target set, timeline,
per-cluster/global SLO, lag, write loss, client requests, capacity,
conformance, policy, abort/cleanup and postmortem. Hash utility/version
is `[VERIFY]`; hash equality proves byte equality relative to the
manifest, not truth or completeness.

### Measurement definitions

-   **RTA:** `[ASSUMPTION]` elapsed time from declared service-affecting
    trigger to consistent client success and incident-owner declaration
    that the stated service objective is restored. Record first
    alternate success separately.
-   **RPA:** `[ASSUMPTION]` recovered data point from the highest
    contiguous acknowledged write/canary sequence present after
    promotion/reconciliation compared with the pre-failure ledger.
    Report sequence gap and clock uncertainty; this is actual achieved
    result, not target RPO.
-   **Client tail:** time until clients consistently succeed against
    alternate endpoint, with population, sampling window, failed
    requests, caching and connection reuse stated.
-   **Acknowledged-write loss:** acknowledged-before-failure operations
    absent after recovery, verified against the ledger and recovered
    data; classify missing, replayable, duplicate and unresolved
    separately.

`evidence/measurement-template.csv`

``` csv
run_id,scenario,profile,objective_RTA_seconds,objective_RPO_seconds,trigger_utc,first_alternate_success_utc,consistent_success_utc,RTA_actual_seconds,RPA_sequence_gap,lag_p50_ms,lag_p95_ms,lag_p99_ms,lag_p999_ms,acknowledged_writes_missing,client_p50_ms,client_p95_ms,client_p99_ms,assumptions,evidence_paths,limitations
```

`[SYNTHETIC]` example: trigger 12:00:00; first alternate success
12:00:42; sustained success 12:01:10. If stabilization criteria are met
then RTA actual under this definition is 70 s. First alternate success
is a separate milestone. If two acknowledged writes are missing in the
synthetic ledger, report "2 potentially lost; reconciliation pending."
None of these are measured results.

Evidence checks: matching run IDs; explicit time zone; source/cluster
identity; actual or `[VERIFY]` versions; separate synthetic vs measured
data; per-cluster and global SLO; ring halt/rollback; data
role/fencing/reconciliation; cleanup verification; valid manifest; no
secrets.

## 18. Runbooks, fail-back, and postmortem

Every runbook states trigger/severity, role/channel placeholders, safe
first action, target identity, go/no-go, bounded commands/actions,
per-cluster and client verification, evidence, rollback/abort, cleanup
and prevention.

### Wrong context

Trigger: target mismatch or unknown context. Stop mutation, preserve
command/audit output, enumerate contexts, compare registry and trusted
cluster marker, inspect changed resources read-only, notify owner, and
only restore after impact is known. Verify negative test returns
non-zero and no unapproved target was touched.

### Bad ring rollout

Trigger: SLO breach, health failure, conformance FAIL/UNKNOWN, stale
evidence or target mismatch. Halt promotion; preserve revision/impact
report; rollback only if schema/data compatibility is confirmed; verify
per-cluster health and ensure ring 1 did not advance.

### Hub down/rebuild

Pause fan-out, preserve last trusted revision, use local telemetry,
restore from reviewed config, rotate credentials if compromise
suspected, enumerate both clusters, compare revisions/policy/quarantine,
reconcile one cluster at a time. Unknown hub trust means changes remain
frozen.

### Endpoint/TLS/trust failure

Pause rotation/fan-out. Capture caller, target, DNS, certificate
metadata, authorization and policy. Distinguish DNS, route, SAN/expiry,
trust, authorization and app errors. Restore known-good trust only
through approved path; verify positive and negative connectivity tests.

### DNS/client failover

Preserve probe/client timeline. Verify alternate endpoint and data
authority. If both endpoints are unhealthy or authority unknown, fail
static/manual and keep writes blocked. Shift gradually only after gates;
record first and sustained client success.

### Replication lag/RPO excursion

Pause backfill/maintenance. Inspect lag distribution, canary, slot/WAL,
disk and write ledger. Resume only after fresh stabilization window and
parity. Unknown lag is not a pass.

### East loss / promotion / fencing

Assign roles and communicate uncertainty. Keep writes blocked. Verify
west data freshness/capacity and old east writer fencing; promote
through verified lab process; fence old writer before enabling writes;
shift traffic gradually; verify data role, client success, regional SLO
and local alerts. If fencing cannot be proven, remain
read-only/unavailable for writes.

### Fail-back/reconciliation

Keep current writer authority. Verify returning region
version/policy/credentials/data/capacity, reconcile divergence, verify
artifact hash and schema, ensure no competing writer, then shift small
traffic share and observe. Abort on stale telemetry, unresolved
divergence, unknown capacity or fencing uncertainty.

### Quarantine / compromised hub / cleanup failure

Quarantine any critical FAIL, stale report or unreachable cluster;
require fresh PASS. For suspected hub compromise, stop fan-out, preserve
audit, scope access, rotate/revoke through approved process,
independently inspect both clusters and restore trusted state only after
verification. For abort, stop transitions, expire faults, verify
inactive, preserve evidence and return non-zero if cleanup cannot be
verified.

### Blameless postmortem template

`evidence/postmortem-template.md`

``` markdown
# Postmortem — [RUN_ID]
## Summary
- Scenario/variant; synthetic or measured:
- Service/cluster scope; user impact:
- Start/end; declared objectives and thresholds:
## Timeline
| Time UTC | Event | Cluster | Evidence ID | Confidence/uncertainty |
|---|---|---|---|---|
## Measurements
- RTA objective / actual / definition:
- RPA objective / actual / sequence gap:
- Client-tail sampling window and p50/p95/p99:
- Lag distribution and canary:
- Acknowledged writes missing/replayed/duplicate/unresolved:
- Capacity and cleanup result:
## Decisions and uncertainty
- Decision owner; alternatives; why safe; what was unknown:
## What went well / poorly / was lucky
## Contributing conditions (no individual blame)
## Detection and verification gaps
## Action items
| Action | Owner role | Due date | Control hierarchy | Verification/retest | Status |
|---|---|---|---|---|---|
## Required retests
1. Ring halt/rollback after gate change.
2. Fencing/write-routing order and fail-back reconciliation.
## Risk/objective updates and readiness decision
```

`[ILLUSTRATIVE]` example: ring-0 bad revision is synced but regional SLO
gate halts before ring 1. Contributing condition: sync status was
over-weighted. Retest both SLO-blocks-promotion and rollback-health
checks. No real incident is claimed.

## 19. Safety harness and `make verify-all`

`Makefile` contract (supporting scripts must be implemented separately;
not created by this document):

``` makefile
.PHONY: preflight validate-registry test guard-negative evidence-check cleanup-check verify-all
preflight:
    python scripts/preflight.py
validate-registry:
    python scripts/validate_registry.py fleet/registry/clusters.yaml
test:
    python -m unittest discover -s sim/tests -v
guard-negative:
    python -m unittest sim.tests.test_guards -v
evidence-check:
    python scripts/verify_evidence.py evidence
cleanup-check:
    python scripts/verify_cleanup.py --targets stage2e-east-lab,stage2e-west-lab
verify-all: preflight validate-registry test guard-negative evidence-check cleanup-check
    python scripts/assert_no_unapproved_targets.py --allowed stage2e-east-lab,stage2e-west-lab
```

Representative pure allow-list tests, not proof of kubectl safety:

``` python
import unittest
ALLOWED = {"stage2e-east-lab", "stage2e-west-lab"}
def validate_target(target):
    if not target or target not in ALLOWED:
        raise ValueError("explicit allow-listed target required")
    return target
class GuardTests(unittest.TestCase):
    def test_allowed(self):
        self.assertEqual(validate_target("stage2e-east-lab"), "stage2e-east-lab")
    def test_missing(self):
        with self.assertRaises(ValueError): validate_target("")
    def test_non_lab(self):
        with self.assertRaises(ValueError): validate_target("production")
    def test_unknown(self):
        with self.assertRaises(ValueError): validate_target("stage2e-north-lab")
```

`verify-all` must refuse non-lab/unknown/ambiguous/missing targets;
validate registry/CIDR; run available schema/lint/unit/integration
tests; test ring/quarantine/abort/cleanup; verify evidence and hashes;
assert no unapproved targets; exit non-zero on any failure. Exact
versions are `[VERIFY]`.

Expected output is illustrative only:

``` text
[ILLUSTRATIVE] preflight: PASS
[ILLUSTRATIVE] registry/CIDR: PASS
[ILLUSTRATIVE] guard tests: PASS
[ILLUSTRATIVE] wrong-target integration test: blocked as expected
[ILLUSTRATIVE] ring/quarantine/abort tests: PASS
[ILLUSTRATIVE] evidence manifest: PASS
[ILLUSTRATIVE] cleanup verification: PASS
[ILLUSTRATIVE] verify-all: PASS
```

**Actual status: NOT RUN.** Never copy illustrative output into
evidence.

## 20. Sequencing and cleanup

  ------------------------------------------------------------------------------------------------
  Phase                      Profile                        Time Risk          Go/no-go evidence
                                                `[ILLUSTRATIVE]`               
  -------------------------- ---------------- ------------------ ------------- -------------------
  Preflight                  Core                         1--2 h READ-ONLY     versions, headroom,
                                                                               ports, targets

  Cluster/registry           Core                         3--5 h FLEET-WIDE    CIDR, registry,
                                                                               guard tests

  Lifecycle                  Core                         3--4 h FAULT         dry-run, version
                                                                               and cleanup checks

  GitOps rings               Fleet+GitOps                 4--7 h FLEET-WIDE    fan-out, ring-0
                                                                               halt, rollback

  Connectivity               Core                         3--5 h FAULT         allowed/denied path
                                                                               and trust evidence

  Traffic                    Fleet+Data/sim               3--5 h FAILOVER      event timeline and
                                                                               client tail

  Data                       Fleet+Data/sim               5--8 h FAILOVER      lag, authority,
                                                                               write ledger,
                                                                               reconciliation

  Observability/governance   minimal                      4--7 h FLEET-WIDE    SLO,
                                                                               absent-cluster,
                                                                               quarantine

  Game master/experiments    Core/sim                    6--10 h FAULT         replay, abort and
                                                                               cleanup evidence

  Fail-back/evidence         Core                         4--7 h FAILOVER      parity, manifest,
                                                                               postmortem

  Teardown                   all used                     2--4 h FLEET-WIDE    complete
                             profiles                                          leftover-resource
                                                                               verification
  ------------------------------------------------------------------------------------------------

Before each lab: choose one profile, check target allow-list, resources
and ports, confirm lease/abort, capture baseline/run ID, record cleanup,
and verify no production target or credential. After each lab: stop
fault, preserve evidence, remove only owned resources, check
clusters/namespaces/GitOps registrations/replication
slots/DNS/proxy/processes/temporary rules/lab keys/volumes, verify both
cluster states and host recovery, hash evidence and mark unknown
leftovers OPEN. Teardown is not complete until independently verified.

## 21. Acceptance matrix

Statuses describe this **specification**, not runtime execution.
`PARTIAL` means implementation/testing remains. `OPEN` means an
unresolved item is visible.

  -----------------------------------------------------------------------------------------------------------
                 \# Requirement                             Status        Evidence      Verification method /
                                                                                        limitation
  ----------------- --------------------------------------- ------------- ------------- ---------------------
                  1 exact lab names and explicit context    PARTIAL       §§1, 8, 19    context inventory and
                    safety                                                              wrong-target
                                                                                        integration; not run

                  2 registry schema/validation              PARTIAL       §8            validator and
                                                                                        required fields;
                                                                                        dependencies not
                                                                                        pinned

                  3 CIDR overlap demonstrated/fixed         PARTIAL       §8.1          fixture fails and
                                                                                        chosen ranges pass;
                                                                                        actual routes unknown

                  4 context guard and wrong-target tests    PARTIAL       §§8.2, 19     unit/integration
                                                                                        tests; wrapper
                                                                                        requires hardening

                  5 version/support inventory               OPEN          §8.4          record actual
                                                                                        versions and current
                                                                                        authoritative support

                  6 lifecycle/blue-green/decommission       PARTIAL       §8.4          lifecycle drill and
                                                                                        leftover verifier not
                                                                                        run

                  7 GitOps hub/least-privilege credentials  PARTIAL       §9            review RBAC;
                                                                                        controller not
                                                                                        installed

                  8 ApplicationSet fan-out/impact report    PARTIAL       §9            validate API/selector
                                                                                        on selected release

                  9 ring gates, bad change, halt and        PARTIAL       §9            plant ring-0 failure;
                    rollback                                                            not run

                 10 deletion-cascade guard                  PARTIAL       §9            unknown target/prune
                                                                                        negative tests

                 11 hub-down/rebuild                        PARTIAL       §§8--9        local workload/alert
                                                                                        and rebuild evidence

                 12 admission integrity/signature and       PARTIAL       §9            verifier/API
                    bypass test                                                         `[VERIFY]`

                 13 endpoint/TLS/resilience/NetworkPolicy   PARTIAL       §10           positive and negative
                    tests                                                               request tests

                 14 DNS coupling and trust rotation         PARTIAL       §10           before/after trust
                                                                                        evidence

                 15 local traffic and client-tail           PARTIAL       §11, §17      blank worksheet; no
                    measurement                                                         measurement

                 16 writes blocked until promotion/fencing  PARTIAL       §§11, 18      gate
                                                                                        implementation/test
                                                                                        required

                 17 active-active stateless serving         PARTIAL       §12           per-region response
                                                                                        test not run

                 18 N+1 capacity arithmetic/evacuation      PARTIAL       §12           example illustrative;
                                                                                        capacity not measured

                 19 tenant                                  PARTIAL       §12           fixture and
                    home-region/migration/multi-writer toy                              state-gate tests

                 20 lag distribution and p99.9/RPO          PARTIAL       §13           PostgreSQL
                    reasoning                                                           queries/settings
                                                                                        `[VERIFY]`

                 21 partition/lag experiment and abort      PARTIAL       §§13, 16      synthetic default; no
                                                                                        fault run

                 22 acknowledged-write loss/reconciliation  PARTIAL       §13           synthetic ledger only

                 23 object replication/delete and           PARTIAL       §13           object store not
                    not-a-backup                                                        started

                 24 model alias/hash gate                   PARTIAL       §13           contract specified;
                                                                                        not executed

                 25 divergence and schema migration         PARTIAL       §13           tests not run

                 26 consistency matrix                      PASS          §13           learner must tailor
                                                            (specified)                 data classes

                 27 per-cluster Prometheus identity         PARTIAL       §14           Prometheus not
                                                                                        configured

                 28 worst-cluster/regional/global SLO and   PARTIAL       §14           syntax/version
                    promtool                                                            `[VERIFY]`

                 29 local/global alerts, absent cluster,    PARTIAL       §14           tool availability
                    amtool                                                              `[VERIFY]`

                 30 hub-down observability                  PARTIAL       §14           simulation or lab
                                                                                        drill

                 31 conformance FAIL vs UNKNOWN/UNREACHABLE PARTIAL       §14           scanner not
                                                                                        implemented here

                 32 quarantine integrated with ring         PARTIAL       §14           test exclusion before
                    advancer                                                            promotion

                 33 policy rings/version skew/bypass alert  PARTIAL       §14           one engine selected
                                                                                        after verification

                 34 RBAC-as-code and metadata-only          PARTIAL       §14           no secrets included
                    inventory                                                           

                 35 hub-compromise tabletop                 PARTIAL       §14, §18      tabletop not run

                 36 at least six bounded experiments with   PARTIAL       §16           contract specified;
                    auto-abort                                                          watchdog not
                                                                                        implemented

                 37 A/B scenarios, separated keys, hints,   PASS          §15           harness/replay not
                    scoring                                 (specified)                 run

                 38 failover/fail-back RTA/RPA/client-tail  PARTIAL       §§11, 17--18  no actual
                                                                                        measurements

                 39 `make verify-all` fails closed          PARTIAL       §19           supporting scripts
                                                                                        not included as files

                 40 evidence bundle and manifest/hash       PARTIAL       §17           no run bundle
                                                                                        generated

                 41 blameless postmortem and retested fixes PARTIAL       §18           template/synthetic
                                                                                        example only

                 42 cleanup verification                    PARTIAL       §20           no cleanup executed

                 43 fidelity caveats/not-simulated list     PASS          §§1, 3, 23    local clusters cannot
                                                            (specified)                 prove region
                                                                                        independence

                 44 no fabricated execution/results         PASS          §§17, 19,     official docs not
                                                            (document     25--26        checked live
                                                            review)                     
  -----------------------------------------------------------------------------------------------------------

## 22. Risk register and troubleshooting

  -----------------------------------------------------------------------
  Risk                    Prevention/detection    Response
  ----------------------- ----------------------- -----------------------
  Wrong-context mutation  explicit target,        stop, preserve
                          identity marker,        evidence, inspect
                          negative tests          read-only

  CIDR overlap            pairwise validator +    stop provisioning;
                          host route check        replan

  Hub compromise/fan-out  least privilege, rings, halt fan-out, scope,
                          independent audit       rotate, inspect

  Stale conformance       freshness and UNKNOWN   quarantine and refresh
  appears green           semantics               

  DNS/client tail         client harness and tail keep safe path; revise
  underestimated          distribution            objective

  Split-brain writes      single-writer, fencing, block writes
                          write gate              

  Lag/WAL growth          lag, slot and disk      pause load and verify
                          monitoring              recovery

  Host resource           sequenced profiles and  auto-abort and stop
  exhaustion              thresholds              optional stack

  Secret in evidence      metadata-only inventory quarantine bundle,
                          and redaction           rotate affected
                                                  credential

  Cleanup leaves fault    lease/watchdog +        block next run
  active                  independent             
                          verification            

  Policy false            audit/warn, rings,      halt enforcement and
  deny/bypass             rollback, bypass alert  inspect

  Global SLO hides region regional guardrails and respond to regional
                          worst-cluster panel     symptom
  -----------------------------------------------------------------------

Troubleshooting: missing context → stop, never switch to current
context; CIDR failure → inspect all ranges and host/VPN/Docker routes;
unexpected fan-out → stop sync and save resolved target report;
sync-success/app-failure → inspect runtime/SLO/policy per cluster;
endpoint resolves/TLS fails → inspect SAN/expiry/trust/identity; green
global/bad region → inspect regional numerator/denominator and absent
series; high/stale lag → pause backfill; unknown writer → remain
read-only; model hash mismatch → block alias; cleanup failure → no next
run.

## 23. Not simulated and fidelity limits

Two local kind clusters cannot prove independent geographic regions/AZs,
real WAN latency/partition, provider routing convergence, public DNS
cache behavior, global proxy availability, production-scale/GPU
capacity, real cloud replication durability, immutable backup,
enterprise identity/key management, legal residency compliance,
production RTA/RPA objectives, real prices or SLAs. Local tests can
prove only the exact guard, state-machine, gate, evidence and cleanup
behavior actually exercised. A deterministic simulator does not prove
PostgreSQL or object-store semantics.

## 24. Glossary

-   **ADR:** Architecture Decision Record.
-   **ApplicationSet:** Argo CD resource that generates Applications;
    fields are version-dependent.
-   **Blast radius:** scope of impact from a failure/change.
-   **CA/mTLS:** Certificate Authority / mutual TLS.
-   **CIDR:** Classless Inter-Domain Routing range.
-   **Fencing:** prevents an old/competing writer retaining authority.
-   **GSLB:** Global Server Load Balancing; only a local analogue is
    simulated here.
-   **GitOps:** reconcile version-controlled desired state with observed
    state.
-   **IC/JIT:** Incident Commander / Just-In-Time privilege.
-   **N+1:** capacity to tolerate loss of one defined failure domain.
-   **RPA/RTA:** recovery-point/time actual/achieved measures as defined
    by the assumptions in this project.
-   **RPO:** Recovery Point Objective.
-   **SLO/SLI:** Service-Level Objective / Indicator.
-   **UNKNOWN/UNREACHABLE:** not proof of health; never silently PASS.
-   **WAL:** Write-Ahead Log.

## 25. Claim and Uncertainty Register

No live official documentation was consulted. These URLs are
verification entry points, not sources claimed to have been reviewed.

  ----------------------------------------------------------------------------------------------------------------------------------------------
  ID          Claim / uncertainty       Canonical entry point                      Status             Consequence            Human verification
  ----------- ------------------------- ------------------------------------------ ------------------ ---------------------- -------------------
  C-01        kind networking           https://kind.sigs.k8s.io/                  `[VERIFY]`         creation/overlap risk  inspect selected
              fields/CIDR behavior                                                                                           release and actual
                                                                                                                             config

  C-02        Kubernetes support window https://kubernetes.io/docs/                `[VERIFY]`         unsupported            record version and
                                                                                                      APIs/version           current support
                                                                                                                             policy

  C-03        Cluster API/CAPD          https://cluster-api.sigs.k8s.io/           `[VERIFY]`         resource/provider      verify matrix;
              compatibility                                                                           failure                otherwise use
                                                                                                                             config-as-code
                                                                                                                             fallback

  C-04        Argo CD                   https://argo-cd.readthedocs.io/            `[VERIFY]`         wrong fan-out/deletion validate exact
              ApplicationSet/prune                                                                                           release and target
              behavior                                                                                                       resolution

  C-05        admission                 https://kubernetes.io/docs/                `[VERIFY]`         integrity gate may not verify selected M12
              signature-verifier APIs                                                                 hold                   equivalent and
                                                                                                                             negative test

  C-06        NetworkPolicy enforcement https://kubernetes.io/docs/                `[VERIFY]`         policy may not be      identify CNI and
                                                                                                      enforced               run
                                                                                                                             positive/negative
                                                                                                                             tests

  C-07        PostgreSQL                https://www.postgresql.org/docs/           `[VERIFY]`         unsafe promotion/RPO   verify selected
              replication/lag/WAL                                                                                            version and query
                                                                                                                             output

  C-08        Prometheus                https://prometheus.io/docs/                `[VERIFY]`         alert errors/false     validate with
              rules/labels/promtool                                                                   green                  installed version

  C-09        Grafana provisioning      https://grafana.com/docs/grafana/latest/   `[VERIFY]`         dashboard              verify selected
                                                                                                      identity/data-source   release
                                                                                                      issues                 

  C-10        OpenTelemetry components  https://opentelemetry.io/docs/             `[VERIFY]`         missing/correlated     optional; verify
                                                                                                      traces                 before enabling

  C-11        Docker/kind/WSL2 resource https://kind.sigs.k8s.io/                  `[VERIFY]`         profile may exceed     measure actual
              behavior                                                                                host                   machine

  C-12        DNS/proxy behavior        https://coredns.io/                        `[VERIFY]`         cache/propagation      use deterministic
                                                                                                      assumptions wrong      model or verify
                                                                                                                             implementation

  C-13        policy engine and version https://kyverno.io/docs/                   `[VERIFY]`         false pass/deny        choose one engine
              skew                                                                                                           and test
                                                                                                                             compatibility

  C-14        SHA-256 utility           OS docs not reviewed                       `[VERIFY]`         manifest verification  record tool/version
              availability                                                                            failure                and test known
                                                                                                                             fixture

  C-15        example                   invented examples                          `[ILLUSTRATIVE]`   mistaken for real      measure actual
              scores/timings/capacity                                                                 result                 environment

  C-16        exact RTA/RPA source      source glossary not fully verified         `[ASSUMPTION]`     metrics may differ     confirm M13/M14
              definitions                                                                             from roadmap           glossary

  C-17        exact `Roadmap_ptree.md`  not available under exact name             `[OPEN]`           path mismatch possible inspect exact
                                                                                                                             source before
                                                                                                                             commit

  C-18        sibling lesson interface  not checked line-by-line in this pass      `[OPEN]`           detail may conflict    cross-check all
              alignment                                                                               with final lesson      Unit 1--8 contracts
  ----------------------------------------------------------------------------------------------------------------------------------------------

## 26. Roadmap Alignment and Authenticity Audit

**Scope:** this document is grounded in the supplied capstone prompt and
readable M14 roadmap excerpt. The exact file `Roadmap_ptree.md` was not
available under that filename. The primary M14 prompt was read for
context; final sibling lesson files were not independently verified
line-by-line. The exact target path comes from the supplied prompt. No
other repository file is generated or modified.

  -----------------------------------------------------------------------------------------------------------------------
  Requirement                            Status         Evidence       Verification method       Notes / limitation
  -------------------------------------- -------------- -------------- ------------------------- ------------------------
  Exact target path/basename             PASS           Metadata       compare supplied contract one standalone artifact

  Exact two lab names and scenario       PASS           §§1--3         static review             labels are not real
                                                                                                 regions

  M14 Units 1--8 and handoffs            PASS           §§1, 8--14     crosswalk to prompt       sibling lessons not
                                                                                                 fully audited

  `Projects/README.md` not duplicated    PASS           §§1, 5         output inventory          not created

  Repository layout and purpose          PASS           §5             compare required tree     proposed, not created

  ADR and scored alternatives            PASS           §4             static review             scores illustrative

  Profiles/resource plan/sequencing      PASS           §§6, 20        gate review               footprint not measured

  Preflight and stop/go gates            PASS           §7             static review             host preflight not run

  Registry/CIDR/context guard            PARTIAL        §8             validator and             wrapper needs hardening;
                                                                       wrong-target tests        not run

  Lifecycle/version/decommission         PARTIAL        §8             disposable lifecycle      no cluster operations
                                                                       drill                     

  GitOps hub/rings/fan-out/rollback      PARTIAL        §9             selected-controller       manifests not applied
                                                                       validation                

  Admission integrity and bypass test    PARTIAL        §9             disposable negative test  API/verifier `[VERIFY]`

  Connectivity/TLS/NetworkPolicy         PARTIAL        §10            allowed/denied request    CNI/cert stack not
                                                                       tests                     selected

  Traffic simulation and client-tail     PARTIAL        §11            client event timeline     no measurements

  Active-active/N+1/tenant locality      PARTIAL        §12            endpoint and capacity     capacity example
                                                                       tests                     illustrative

  Replication/RPO/write loss/reconcile   PARTIAL        §13            selected-version drill or DB not run
                                                                       simulator                 

  Object/hash/schema/divergence          PARTIAL        §13            integrity and migration   not run
                                                                       tests                     

  Observability/SLO/alerts/conformance   PARTIAL        §14            promtool/amtool/scanner   versions not checked
                                                                       tests                     

  Quarantine/policy/RBAC/hub tabletop    PARTIAL        §14            negative tests/tabletop   not run

  Variants A/B, keys, hints, scoring     PASS           §15            scenario review and       harness not implemented
                                         (specified)                   replay test plan          

  Six+ bounded experiments/auto-abort    PARTIAL        §16            run each with             watchdog not implemented
                                                                       lease/cleanup             

  Evidence/RTA/RPA/client-tail/hash      PARTIAL        §17            populate and validate run no run evidence
                                                                       bundle                    

  Runbooks/fail-back/postmortem          PASS           §18            tabletop/retest           template + synthetic
                                         (specified)                                             example

  `make verify-all` fail-closed contract PARTIAL        §19            run unit/integration      support scripts not
                                                                       tests                     included

  Cleanup verification                   PARTIAL        §20            teardown and inventory    not executed

  44 acceptance rows                     PASS           §21            count rows                runtime statuses remain
                                         (specified)                                             partial/open

  Limits and risk register               PASS           §§22--23       static review             no production assurance

  Claim/uncertainty register             PASS           §25            status review             live docs not consulted

  Exact `Roadmap_ptree.md` verified      BLOCKED        C-17           inspect exact named file  unavailable under exact
                                                                                                 name

  Runtime tests/cluster operations       BLOCKED        §§19, 26       run in isolated lab       none executed
  executed                                                                                       

  Current official API docs reviewed     BLOCKED        §25            record                    URLs are entry points
  live                                                                 source/version/date       only

  No fabricated measurements/execution   PASS (document §§17, 19,      review labels and status  examples labelled
  claims                                 review)        25--26                                   illustrative/synthetic
  -----------------------------------------------------------------------------------------------------------------------

**Final status: SPECIFICATION DRAFT --- RUNTIME NOT EXECUTED.** This
document defines architecture, implementation contracts, representative
artifacts, safety gates, game-master scenarios, evidence, runbooks and
acceptance criteria. It does not claim the proposed code is a complete
integrated repository, that all supporting files exist, that manifests
are deployable without version review, or that any cluster/failover/test
was run. Resolve `[OPEN]` items, verify version-sensitive behavior,
compare sibling contracts, implement supporting files, and run
`make verify-all` in an isolated environment before treating the project
as validated.
