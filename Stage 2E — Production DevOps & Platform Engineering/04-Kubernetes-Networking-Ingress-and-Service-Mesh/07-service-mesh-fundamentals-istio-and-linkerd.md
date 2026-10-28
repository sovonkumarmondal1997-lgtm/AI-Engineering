# Service mesh fundamentals: Istio and Linkerd

## Unit 7 — Service mesh fundamentals: Istio and Linkerd

**Target file:** `07-service-mesh-fundamentals-istio-and-linkerd.md` | **Estimated time:** 6–10 hours, including local experiments | **Prerequisites:** M01–M03 and M04 Units 1–6; basic Kubernetes networking, Services, TLS, probes, RBAC, and NetworkPolicy  
**Core tools:** Kubernetes, `kind`, `kubectl`, Docker, one mesh CLI | **Awareness:** Istio, Linkerd, Gateway API/GAMMA, SPIFFE, multi-cluster mesh | **Last reviewed:** 2026-10-28 (authoring date, not the date of a full compatibility audit) | **Kubernetes/tool baseline assumed:** a recent `kind`-supported Kubernetes release; exact Kubernetes, mesh, CLI, and CRD versions must be selected from the chosen project's current compatibility documentation.

> **Status: DRAFT-AUDITED.** Official Linkerd, Istio, and Gateway API pages were consulted for selected architecture and installation concepts. The exact installation release, supported Kubernetes matrix, and local lab were not executed or fully validated. All unverified release-specific instructions remain marked. This is not a production-ready change plan until the human verification checklist is complete.

**Module-wide hands-on choice — [ASSUMPTION]: Linkerd, sidecar mode.** The available M04 source specifies one mesh but does not record a previous final choice. Linkerd is selected as the single hands-on mesh for Unit 7, the planned Unit 8 lab, and the M04 capstone because it gives this learning sequence a single, focused proxy/control-plane path to operate before adding detailed policy and traffic-management concepts. This is a pedagogical choice, **not** a claim that Linkerd has lower memory use or better performance. No resource-footprint measurements were made. Istio remains the documented comparison. Before committing to the choice, verify the current Linkerd/Kubernetes compatibility matrix and run the measurement method in Lab 2. If later evidence causes a change, update Unit 8 and the capstone together; do not silently switch meshes between units.

### 7.0 Why this matters in production

A service mesh can centralize workload identity, encrypted service-to-service transport, and traffic telemetry, but it also inserts components into application request paths and Pod lifecycles. A failed injection webhook can prevent new Pods from starting; a proxy or trust configuration change can break calls between otherwise healthy services; and proxy CPU or memory pressure can increase tail latency. A control-plane outage may affect configuration and identity operations differently from already-established traffic, so “the mesh is down” is not a sufficiently precise incident diagnosis. This unit teaches how to reason about those boundaries, onboard one low-risk workload, measure the observed overhead, and decide from evidence whether a mesh is justified.

### 7.1 Learning objectives

1. **[L1]** Explain what a service mesh can and cannot provide, including control-plane/data-plane separation and request-path interception.
2. **[L1]** Trace a request from the model API to the internal feature service and identify where identity, encryption, policy, and telemetry are applied.
3. **[L2]** Install and verify one selected mesh using the current official instructions and a guarded throwaway `kind` context.
4. **[L2]** Enroll a single sample workload and prove actual proxy/data-plane enrollment rather than relying on a namespace label alone.
5. **[L3]** Compare Istio and Linkerd architecture, operating model, routing/policy model, Gateway API relationship, and upgrade risks without inventing performance claims.
6. **[L3]** Design a repeatable baseline-versus-meshed experiment reporting median and p95 latency, CPU, memory, errors, and test conditions.
7. **[L4]** Diagnose an injection, proxy lifecycle, control-plane, identity, or NetworkPolicy failure with bounded tests and reversible mitigations.
8. **[L4]** Produce a ring-based adoption decision and an exit plan supported by measured evidence and explicit ownership.

### 7.2 Concept map and vocabulary

### Request path: what handles the packet?

[ASSUMPTION] To align with the more detailed network-policy example in M04 Unit 5, this lesson uses namespace `ml-platform`, `model-api` on TCP/8080, `feature-service` on TCP/8081, `postgres` on TCP/5432, and `redis` on TCP/6379. Unit 6 uses `ml-demo` in its illustrative certificate exercise; treat that as a separate lab namespace, not a claim that all M04 manifests share one namespace. Confirm the repository's final shared contract before combining manifests.

```text
model-api Pod                                         feature-service Pod
+---------------------------+                         +---------------------------+
| FastAPI application       |                         | Feature application       |
|       |                   |                         |       ^                   |
|       v                   |                         |       |                   |
| Linkerd proxy (sidecar)   |==== network path =====>| Linkerd proxy (sidecar)   |
+---------------------------+                         +---------------------------+
              |                         |
              |                         +-- NetworkPolicy/CNI enforcement point(s)
              |
              +-- workload identity and encrypted mesh hop only if
                  both endpoints and policy/config are correctly meshed

Control plane distributes configuration/identity material; it is not normally
a per-request application hop. Telemetry is emitted by proxies and applications.
```

The drawing is a logical path, not a packet capture. Actual interception uses implementation-specific networking rules and may include init containers, proxy listeners, redirection, and node-level networking. A NetworkPolicy-capable CNI enforces network reachability separately from mesh policy. It can block the proxy's traffic to the control plane, DNS, telemetry components, or peer workload. Do not assume every packet traverses the same path for every protocol, host-network Pod, probe, or unmeshed workload.

### Control plane versus data plane

```text
                 Operator / Git / CLI
                         |
                         v
             +--------------------------+
             | Mesh control plane       |
             | desired config, identity |
             | discovery, validation    |
             +--------------------------+
                 | configuration / identity
                 | distribution
       +---------+--------------------------+
       v                                    v
+---------------------+             +---------------------+
| Source workload     |             | Destination workload |
| app + proxy         |<-- traffic ->| proxy + app          |
+---------------------+             +---------------------+
       | telemetry                         | telemetry
       +------------------+----------------+
                          v
               Metrics/logging/tracing
          (selected add-on or existing platform)
```

The control plane manages and distributes state. The data plane handles application traffic. This distinction matters during incidents: an unavailable control plane may prevent new configuration from propagating while existing proxies continue using cached state, but traffic continuity is not guaranteed in every failure. Identity certificate expiry, proxy restarts, stale endpoints, data-plane failure, or a policy change can alter the result. Test the selected mesh/version instead of relying on a universal promise.

### Glossary

| Term | Precise definition | Common misconception |
|---|---|---|
| Service mesh | A platform layer for service-to-service communication features such as workload identity, transport security, traffic policy, and telemetry. | It automatically makes every workload secure or reliable. |
| Control plane | Components that configure, discover, or provision identity for the data plane. | Every application request passes through the control plane. |
| Data plane | Components that intercept, proxy, or otherwise mediate workload traffic. | Data-plane health is guaranteed by control-plane health. |
| Sidecar | A proxy container deployed alongside an application container in a Pod. | A namespace label proves every running Pod has a sidecar. |
| Ambient/sidecarless | A family of designs that move some traffic processing to node-level or shared components and may use optional L7 proxies. | It is feature-identical to sidecar mode in every release. |
| Proxy | A component that mediates traffic between a workload and another endpoint. | A proxy automatically enforces every desired policy. |
| Workload identity | An identity assigned to a workload for authentication and policy decisions. | Network IP address is a durable workload identity. |
| Injection | A process, often an admission webhook or manifest transform, that adds proxy-related Pod configuration. | Injection label means injection succeeded. |
| mTLS | Mutual TLS, where both peers authenticate certificates during a TLS connection. | mTLS alone defines what an authenticated peer may do. |
| NetworkPolicy | Kubernetes API policy for selecting Pods and restricting network flows, implemented by a policy-capable network plugin. | A mesh replaces the CNI or NetworkPolicy. |
| Mesh ingress | An ingress path managed through mesh-aware gateway/proxy components. | It is synonymous with every standalone Ingress controller. |
| Gateway API | Kubernetes APIs for role-oriented traffic routing; support varies by implementation and feature. | All implementations support the same routes and policies. |
| GAMMA | Gateway API for Mesh Management and Administration, extending Gateway API concepts to east-west/service-mesh use cases. | GAMMA means every mesh resource is portable today. |
| Control-plane availability | Ability of management components to respond and distribute valid state. | Existing traffic always continues, or always stops, when it is unavailable. |
| Exit strategy | A tested process to remove mesh participation and restore a known-good traffic path. | Uninstalling a chart alone removes every injected proxy and policy. |

### “Do we need a mesh?” decision tree

```text
Do multiple services need consistent transport identity, security, or telemetry?
  |
  +-- No --> Use native Kubernetes networking and application-level controls.
  |
  +-- Yes --> Can supported libraries/platform features meet requirements
              with lower operational complexity?
                |
                +-- Yes --> Compare library/platform approach against mesh cost.
                |
                +-- No --> Can the team own control plane, proxies, upgrades,
                            identity, observability, and incident response?
                              |
                              +-- No --> Reduce scope or defer adoption.
                              |
                              +-- Yes --> Pilot one low-risk service, measure,
                                          then expand by rollout rings.
```

### Sidecar and ambient/sidecarless models

| Model | Conceptual data path | Potential benefit | Operational caveat |
|---|---|---|---|
| Sidecar | Proxy container alongside each participating Pod's application container | Per-workload proxy behavior and a familiar deployment boundary | Additional per-Pod resource use, injection and shutdown concerns |
| Ambient / sidecarless | Selected traffic is mediated by node-level components; optional L7 waypoint-like proxies may handle richer policy/routing | Can avoid a per-Pod sidecar for some traffic paths | Different interception, policy, observability, upgrade and feature constraints |

Istio documents sidecar and ambient modes; exact maturity and capabilities are release-sensitive. Linkerd's standard data plane uses a per-workload proxy model; do not imply that Istio ambient architecture is interchangeable with Linkerd. The core lab in this lesson is **Linkerd sidecar mode only**. No ambient mode or second mesh is installed.

### 7.3 Level 1 — Beginner: Foundations

### What a mesh helps with

A mesh can provide a consistent mechanism for workload-to-workload identity, encrypted transport, service-level telemetry, and centrally managed communication behavior. Depending on the implementation and enabled features, it may also support traffic shifting, retries/timeouts, or policy enforcement. The operational value is consistency across services: a team does not need to reimplement every transport concern in each client library.

The mesh does not repair incorrect business logic, slow SQL queries, exhausted database connections, unsafe retry behavior, missing authorization in the application, or unmeshed traffic paths. It does not guarantee end-to-end encryption past the proxy's termination point. It also does not replace Kubernetes NetworkPolicy, RBAC, Pod Security Standards, application SLOs, or incident ownership. A mesh may make a bad retry policy easier to apply consistently, which can amplify an outage if the policy is wrong.

### Alternatives and trade-offs

| Approach | Good fit | Main cost or limitation |
|---|---|---|
| No mesh + native Kubernetes networking | Small systems with simple trust boundaries | Cross-service features may be implemented inconsistently |
| Application/library-level controls | Teams own client code and can standardize libraries | Language/framework differences and upgrade drift |
| Ingress/Gateway only | Need mainly north-south entry controls | Does not by itself standardize east-west traffic |
| CNI / NetworkPolicy | Network reachability and segmentation | Not a universal substitute for workload identity or HTTP-level policy |
| Service mesh | Many services need shared identity, transport security, telemetry, or traffic controls | Control-plane, proxy, compatibility, resource, and debugging overhead |

### Guided read-only walkthrough

Start with the state of the workload and namespace, before installing a mesh:

```bash
# File: commands/inspect-mesh-baseline.sh
set -euo pipefail
EXPECTED_CONTEXT="kind-m04-mesh-lab"
ACTUAL_CONTEXT="$(kubectl config current-context)"
if [[ "${ACTUAL_CONTEXT}" != "${EXPECTED_CONTEXT}" ]]; then
  printf 'Refusing to inspect wrong context: expected %s, got %s\n' \
    "${EXPECTED_CONTEXT}" "${ACTUAL_CONTEXT}" >&2
  exit 20
fi
kubectl --context "${EXPECTED_CONTEXT}" get nodes -o wide
kubectl --context "${EXPECTED_CONTEXT}" get ns
kubectl --context "${EXPECTED_CONTEXT}" -n ml-platform get deploy,pod,svc
kubectl --context "${EXPECTED_CONTEXT}" -n ml-platform get events \
  --sort-by=.metadata.creationTimestamp
```

Expected output is **[ILLUSTRATIVE]**: Kubernetes returns node, namespace, deployment, Pod, Service, and event information; actual names and readiness depend on the learner's cluster. This establishes a baseline but does not show the packet path or prove the CNI enforces NetworkPolicy. If the namespace or app is absent, deploy the agreed sample application first or adapt the lesson to the existing M04 sample—do not assume the above resources exist.

### Request-path reasoning

For `model-api` calling `feature-service`, identify each stage:

1. The application resolves the Service DNS name and opens a connection to the service port.
2. If the source workload is meshed, its proxy may intercept the connection and apply supported data-plane behavior.
3. Kubernetes networking and any CNI-enforced NetworkPolicy determine whether packets can reach the destination path.
4. If the destination workload is meshed, its proxy receives traffic and mediates the connection to the application container.
5. The application processes the request and responds through the reverse path.
6. Proxy telemetry can report traffic observed by the proxy, but does not replace application logs, business metrics, or tracing.

Exact port redirection, probe handling, and protocol detection are implementation- and version-dependent. Do not diagnose an application issue solely from a mesh dashboard.

### 7.4 Level 2 — Intermediate: Working Practice

### Selected mesh and installation gate

**Selected for the hands-on lab:** Linkerd sidecar mode. The source syllabus explicitly calls for one hands-on mesh and a measured comparison rather than a guessed resource ranking. The available files did not contain a prior final choice or the Unit 8/capstone source prompts, so this is an explicit module-wide assumption to carry forward.

The official Linkerd documentation consulted for this lesson describes a CLI-based path that installs CRDs before the control plane, validates the cluster with `linkerd check --pre`, and verifies the installation with `linkerd check`. It also documents the Gateway API CRDs as a prerequisite for some Linkerd features. **[VERIFY]** The selected release's supported Kubernetes matrix, current CLI acquisition instructions, Gateway API release, and exact install route must be checked immediately before execution. For production, the official installation documentation describes Helm as a repeatable installation option; M06 owns deeper Helm instruction.

Use the official Linkerd Getting Started and Installing Linkerd pages listed in Section 7.14. Choose a stable/vendor-supported distribution appropriate to the learner's needs rather than blindly copying an edge release. The current page content can change. Do not use an invented version number or assume a version remains compatible with the cluster.

### Guard the throwaway cluster

The cluster is named `m04-mesh-lab`; the expected context is commonly `kind-m04-mesh-lab`. Verify the actual context produced by the installed `kind` version. Never rely on a context name alone if it could point to a different cluster.

```bash
# File: commands/guard-mesh-lab.sh
set -euo pipefail
EXPECTED_CONTEXT="kind-m04-mesh-lab"
ACTUAL_CONTEXT="$(kubectl config current-context)"
if [[ "${ACTUAL_CONTEXT}" != "${EXPECTED_CONTEXT}" ]]; then
  printf 'Refusing mutation: expected %s, got %s\n' \
    "${EXPECTED_CONTEXT}" "${ACTUAL_CONTEXT}" >&2
  exit 20
fi
kubectl --context "${EXPECTED_CONTEXT}" cluster-info
kubectl --context "${EXPECTED_CONTEXT}" get nodes
```

Before creating a cluster, check available RAM, CPU, disk, Docker status, `kind version`, `kubectl version`, and `kind get clusters`. Do not reuse a cluster containing valuable work. A cluster creation command may be run only after that check. Resource footprint in this lesson is a planning constraint, not a measured claim.

### Installation procedure (version-gated)

1. Read the official Linkerd install instructions and supported Kubernetes version table.
2. Install the CLI using the currently documented official method, then confirm `linkerd version`.
3. Run `linkerd check --pre` against the guarded context and resolve reported prerequisites before installation.
4. Check whether the Gateway API CRDs required by the selected Linkerd features are present and compatible. Install them only through the current official procedure if missing; avoid replacing CRDs owned by another project without checking compatibility.
5. Review the rendered manifests and exact target context. Apply the official documented CRD installation stage, then the control-plane stage. The current official docs show a CLI route using `linkerd install --crds` followed by `linkerd install`; verify exact commands and supported release before use.
6. Wait for documented readiness conditions and run `linkerd check`. Capture versions and status.
7. Do not install Linkerd Viz in the core measurement lab initially. It adds telemetry components that can confound resource measurements. Add a minimal extension only if it is needed and the remaining resource budget permits it.

**[VERIFY]** This lesson intentionally does not pin the CLI installation shell command, a Linkerd release, Gateway API CRD version, or image digest. Retrieve them from the official documentation at execution time. Avoid piping a remote script directly into a privileged shell without inspecting its provenance and behavior.

### Enroll only the sample namespace

A Linkerd injection label or annotation is a request for injection, not proof that a running Pod has the proxy. A namespace label typically affects Pods created afterward; existing Pods generally need to be recreated through a controlled rollout to receive injected containers. Exact annotation precedence and injection behavior must be verified for the chosen release.

```bash
# File: commands/enroll-sample-namespace.sh
set -euo pipefail
EXPECTED_CONTEXT="kind-m04-mesh-lab"
test "$(kubectl config current-context)" = "${EXPECTED_CONTEXT}" || {
  echo "Wrong context; refusing" >&2; exit 20;
}
# Inspect first; this label mutation is limited to the throwaway sample namespace.
kubectl --context "${EXPECTED_CONTEXT}" get namespace ml-platform --show-labels
# [VERIFY] Confirm the current Linkerd injection label and policy with official docs.
# The common Linkerd annotation is linkerd.io/inject=enabled; confirm for the chosen release.
kubectl --context "${EXPECTED_CONTEXT}" label namespace ml-platform \
  linkerd.io/inject=enabled --overwrite
```

The `--overwrite` option intentionally changes an existing label, so inspect current state first. After applying the verified label, recreate only the sample deployment using a reviewed rollout/restart process. Do not restart the whole cluster or unrelated namespaces.

Verify actual enrollment using all of the following, as applicable to the release:

- Inspect the Pod specification and list container names.
- Inspect the Pod description and events for injection errors.
- Run the documented Linkerd proxy check against the namespace/workload.
- Confirm the application request still succeeds.
- Inspect control-plane and proxy health.
- Compare Pod template and live Pod state; do not treat the namespace label as sufficient evidence.

A proxy sidecar is normally visible as an additional container in the Pod. The exact container name and health command should be verified from current Linkerd documentation. **[VERIFY]** Do not copy Istio's `istio-proxy` container name or Istio-specific commands into a Linkerd lab.

### Operational pitfalls during onboarding

- **Startup and readiness:** a proxy may affect how the application starts, becomes reachable, or responds to probes. Validate the selected version's probe behavior; do not assume all probes are rewritten or bypassed the same way.
- **Jobs/CronJobs:** a sidecar lifecycle can complicate completion if the proxy does not exit or shutdown behavior differs. Test batch workloads separately before broad enrollment.
- **Shutdown/drain:** termination grace periods and connection draining affect in-flight requests. Verify behavior with the selected proxy and workload.
- **Resources:** proxy CPU/memory requests and limits count against Pod scheduling and node capacity. Measure rather than copy a guessed universal value.
- **Injection webhook:** webhook failure or an invalid injection configuration may delay or reject Pod creation depending on admission settings. Check events and webhook health.
- **NetworkPolicy:** policy must allow the actual traffic to peers and the control plane, DNS, and any telemetry services. A mesh does not make blocked network flows magically pass. A NetworkPolicy may also interfere with probes or control-plane communication depending on CNI and topology.
- **Protocol handling:** gRPC, streaming, and non-HTTP protocols need specific validation. Unit 8 covers detailed retry/timeout and traffic-policy behavior.

### Pattern catalogue and anti-patterns

| Pattern | Why it is safer |
|---|---|
| Enroll one non-critical workload first | Limits blast radius and exposes startup/probe problems early |
| Record baseline before installing the mesh | Makes overhead comparison interpretable |
| Use official compatibility checks before installation | Reduces risk from unsupported Kubernetes/CRD combinations |
| Verify actual proxy presence and request flow | Distinguishes intent from runtime state |
| Change one variable per test | Helps isolate CNI, mesh, application, and resource causes |
| Keep a tested no-mesh path and rollback gate | Makes exit possible under incident pressure |

| Anti-pattern | Risk | Better approach |
|---|---|---|
| Mesh every namespace on day one | Broad outage from webhook, identity, or policy errors | Ring-based enrollment with explicit exit criteria |
| Choose based on marketing or claimed memory numbers | Decision unsupported by local workload evidence | Measure same workload under controlled conditions |
| Treat mTLS as authorization | Authenticated but unauthorized workloads may still access services | Define identity-to-action policy separately in Unit 8 |
| Install dashboards before baseline | Add-on resource use contaminates the comparison | Measure core mesh first, then add only needed telemetry |
| Disable NetworkPolicy to “make mesh work” | Removes independent segmentation controls | Identify exact blocked flow and add a narrowly scoped rule |
| Remove mesh by deleting CRDs | May delete custom resources and leave residual state | Follow official uninstall and verify resource ownership |
| Assume a label proves enrollment | Workload may still run without proxy | Inspect live Pod, proxy health, and request path |

### 7.5 Level 3 — Advanced: Production Engineering

### Istio and Linkerd comparison

This is an architectural comparison, not a ranking. Exact features, resource requirements, supported versions, and release policies change. Verify the current official docs before making a production decision.

| Dimension | Istio | Linkerd |
|---|---|---|
| Architecture/control plane | `istiod` provides discovery, configuration distribution, and identity/certificate functions for supported deployment modes | Control-plane components manage service discovery, identity, policy/configuration, and proxy support; exact component details depend on release |
| Common data plane | Envoy sidecars in sidecar mode; ambient mode uses node-level `ztunnel` for L4 and optional waypoint proxies for L7 features | Linkerd's workload proxy architecture; official docs describe its Rust-based micro-proxy |
| Identity and mTLS | Built-in workload identity and mTLS capabilities; detailed configuration belongs to Unit 8 | Workload identity and mTLS capabilities; detailed policy/configuration belongs to Unit 8 |
| Authorization/policy | Istio-specific resources include `PeerAuthentication` and `AuthorizationPolicy`; API schemas must match installed CRDs | Linkerd policy APIs and supported resources are release-sensitive; verify current policy docs |
| Traffic management | `VirtualService`, `DestinationRule`, and related resources in applicable Istio configurations | Routing can use Linkerd-specific APIs and/or Gateway API features depending on release; verify `ServiceProfile` status before relying on it |
| Gateway API / GAMMA | Support depends on version, component, and feature; do not infer full parity | Support depends on current release and Gateway API resources installed |
| Telemetry | Proxy telemetry and optional add-ons; choose components carefully for small clusters | Core data plane plus optional extensions such as viz; extensions add resources |
| Installation/upgrade | Multiple install profiles and modes increase flexibility but require mode/version discipline | CLI and Helm installation paths are documented; production install approach depends on distribution and operational standards |
| Resource measurement | Measure control-plane plus per-Pod proxy or ambient components separately | Measure control-plane plus per-workload proxy and any extensions separately |
| Kubernetes compatibility | Current support matrix `[VERIFY]` | Current support matrix `[VERIFY]` |
| Learning/debugging surface | Broad feature set, multiple modes and APIs can increase decision space | Focused proxy/control-plane model, but still requires release-specific API and policy knowledge |
| Ecosystem/governance/licensing | Verify current governance, license and support model from authoritative sources; no legal conclusion here | Verify current governance, license and support model from authoritative sources; no legal conclusion here |
| Sidecar/sidecarless | Sidecar and ambient modes documented; maturity and feature differences remain version-sensitive | Do not assume Istio ambient parity; verify Linkerd's current supported architecture |
| Multi-cluster | Capabilities exist with topology-specific configuration; M14 owns the deeper design | Multi-cluster capabilities exist but require release-specific setup; M14 owns the deeper design |
| Lock-in/exit | Custom CRDs and policy can create configuration coupling | Custom policy/routing APIs and operational knowledge can create coupling |
| Decision evidence | Local workload test, compatibility review, failure rehearsal, ownership fit | Same measurement and governance criteria |

### Istio concepts to recognize

- **`istiod`:** Istio's control-plane component for discovery/configuration and identity functions. Exact responsibilities and deployment shape depend on the selected release and mode.
- **Envoy:** proxy used by Istio's conventional sidecar data plane and relevant gateway/waypoint paths.
- **Sidecar mode:** an Envoy proxy is injected alongside each participating Pod.
- **Ambient mode:** uses node-level `ztunnel` for L4 traffic mediation and optional waypoint proxies for L7 features. Do not treat it as an installation flag to toggle casually on an existing cluster; migration order and feature gaps are version-sensitive.
- **`VirtualService` and `DestinationRule`:** Istio routing/traffic-management APIs in supported configurations.
- **`Gateway`:** Istio's own gateway resource is distinct from the Kubernetes Gateway API `Gateway` kind; names alone do not make them interchangeable.
- **`PeerAuthentication` and `AuthorizationPolicy`:** security/policy resources whose exact fields and semantics must be checked against installed CRDs. Unit 8 owns detailed enforcement.

### Linkerd concepts to recognize

- **Control plane:** validates and distributes configuration and supports workload identity/proxy operations.
- **Proxy:** Linkerd's data-plane proxy; official documentation describes it as a Rust-based micro-proxy. Verify the current architecture documentation before making implementation-specific assumptions.
- **`ServiceProfile`:** historically used for service-level routing/telemetry features; exact current status and supported behavior are **[VERIFY]**. Do not make it the foundation of a new lab without checking the selected release.
- **Gateway API and policy CRDs:** some Linkerd features rely on Gateway API CRDs, but the exact resource support, channel, and version are release-sensitive.
- **`linkerd check`:** official diagnostic CLI used to validate parts of the installation. It is not a substitute for a request-path test or application health check.

### Gateway API and GAMMA

Gateway API is a role-oriented Kubernetes API family for expressing traffic routing. The GAMMA initiative defines how Gateway API resources can be used for service-mesh/east-west routing while preserving the project's role-oriented model. The official Gateway API mesh overview states that GAMMA mesh support has been in the Standard Channel since Gateway API v1.1.0; implementation support still varies and must be checked for the chosen mesh and resource. Do not infer that every Gateway API implementation supports the same resources, policies, or conformance level.

A standalone ingress controller generally manages north-south traffic entering the cluster. A mesh-aware gateway may share mesh identity and policy semantics, but it is not automatically the same controller or data plane. Unit 3 covers external ingress/Gateway routing; Unit 8 covers detailed mesh traffic policy.

### Reproducible footprint and latency measurement

Do not choose a mesh based on a claimed generic RAM figure. Measure the selected candidate on the actual laptop and sample workload.

1. Record OS, WSL2/native Linux, Docker version, `kind`, Kubernetes server version, mesh CLI/release, node count, CPU/memory limits, and disk free space.
2. Establish a baseline with the sample app **before** installing the mesh. Use the same request endpoint, payload, concurrency, duration, warm-up, and request generator for the meshed test.
3. Choose a bounded test, for example 5 warm-up requests followed by 100 measured sequential requests **[ILLUSTRATIVE]**. Increase only if the laptop remains responsive. A low-rate sequential test does not measure high-concurrency throughput.
4. Record per-request latency and calculate median and p95 from raw observations using a documented tool or a small script that has been locally validated. Do not infer p95 from an average.
5. Record CPU/memory for app Pods, proxy containers, control-plane Pods, and nodes separately. `kubectl top` requires a functioning metrics source such as Metrics Server; if unavailable, install nothing automatically—either verify a minimal source, use a documented local container/runtime measurement, or mark that measurement unavailable.
6. Repeat runs under comparable conditions. Record request count, errors, restarts, CPU throttling, test duration, warm-up, and whether the machine was under other load.
7. Report absolute values and deltas, not an unsupported “winner.” WSL2 scheduling, Docker Desktop, background processes, cache effects, and laptop thermal/power behavior can dominate small differences.

| Metric | Baseline | Meshed | Delta | Method | Run count | Caveats |
|---|---|---|---|---|---|---|
| Median latency |  |  |  |  |  |  |
| p95 latency |  |  |  |  |  |  |
| Request success / error count |  |  |  |  |  |  |
| App CPU / memory |  |  |  |  |  |  |
| Proxy CPU / memory | N/A |  |  |  |  |  |
| Control-plane CPU / memory | N/A |  |  |  |  |  |
| Restarts / throttling |  |  |  |  |  |  |
| Total test duration |  |  |  |  |  |  |

A small `kind` test cannot establish production performance, multi-AZ behavior, cloud load-balancer behavior, or fleet-scale control-plane capacity. It can expose local regressions and teach the learner how to measure consistently.

### Control-plane outage semantics

| Component/state | Existing traffic may do | New configuration / identity operations may do | What to verify | Caveat |
|---|---|---|---|---|
| Control plane unavailable; proxies healthy with cached state | May continue under current proxy state | Changes may not propagate; new identity material may be delayed | Bounded request probes, proxy logs/status, control-plane health | Not a universal guarantee |
| Proxy restarted while control plane unavailable | May fail to reconnect or initialize fully | New config/identity may be unavailable | Restart count, Pod events, proxy readiness | Depends on cached state and startup requirements |
| Identity issuer/certificate expires | Existing sessions may continue temporarily; new handshakes can fail | Renewal or new identity distribution may fail | Certificate/identity status and handshake errors | Depends on certificate lifetime and implementation |
| Control plane pushes invalid configuration | Some proxies may reject config or show degraded state | Desired behavior may not take effect | Config status, proxy logs, control-plane events | Details differ by implementation |
| Admission/injection webhook unavailable | Existing Pods may continue | New Pod admission may fail or proceed without injection depending on configuration | Events, webhook configuration and endpoints | Fail-open/fail-closed semantics must be checked |

### Decision record: mesh or no mesh

Use this template after Lab 2. Do not prefill a winner.

```markdown
# File: evidence/unit-07/mesh-decision-record.md

## Context
Services, traffic patterns, trust boundaries, team capabilities:

## Options
- No mesh + application/platform controls
- Linkerd (hands-on candidate)
- Istio (comparison candidate)

## Constraints
Laptop budget, Kubernetes compatibility, identity requirements, SLOs, operations ownership:

## Evidence
Baseline and meshed median/p95, CPU/memory, errors, restarts, test conditions:

## Decision
[Leave blank until measurement and review]

## Rejected alternatives and reasons
[Use evidence, not unsupported footprint claims]

## Risks and mitigations
[Control plane, proxy, identity, upgrades, NetworkPolicy, exit]

## Owner / review date / revisit trigger
[Fill in]

## Exit criteria
[Observable conditions that justify rollback or removal]
```

### 7.6 Level 4 — Expert: Operating at Scale and Under Failure

### Ring-based adoption and rollback

| Ring | Entry criteria | Exit criteria | Blast radius | Rollback gate |
|---|---|---|---|---|
| 0: lab/dev | Compatibility checked; baseline captured; owner assigned | Proxy enrollment and requests succeed; overhead recorded | Throwaway cluster | Recreate unmeshed workload and verify requests |
| 1: one low-risk service | Tested policy/config; dashboards/runbook available | Stable request success/latency, no unexplained restarts, identity valid | Single service | Stop expansion; restore last known-good workload template |
| 2: one namespace/team | Team trained; NetworkPolicy and probe paths reviewed | SLOs and error budget remain healthy; jobs and dependencies validated | Namespace/team | Remove enrollment in controlled rollout; validate direct path |
| 3: broader fleet | Upgrade/rotation rehearsal, ownership and compatibility matrix | Fleet inventory and renewal/upgrade signals healthy | Many services | Roll back by ring; preserve known-good control-plane and policy state |

Set quantitative entry/exit thresholds from each service's SLO and baseline; do not invent a universal latency percentage. M10 owns SLO/error-budget design, and M08 owns automated progressive delivery/GitOps analysis.

### Incident scenarios: symptom → hypotheses → tests → mitigation → prevention

| Scenario | Symptom / hypotheses | Evidence and test | Safe mitigation | Prevention |
|---|---|---|---|---|
| Injection webhook unavailable | New Pods remain pending or admission errors appear | Pod events; webhook Service/endpoints; control-plane logs; admission config | Restore webhook/control-plane health; pause rollout | Monitor admission failures; test webhook upgrade and rollback |
| Upgrade breaks proxy compatibility | Requests fail after a mixed-version rollout | Control-plane/proxy versions, proxy logs, request probes, release notes | Halt expansion and follow documented rollback/upgrade order | Compatibility matrix and throwaway rehearsal |
| Identity issuer/trust expires | Peer handshakes fail despite healthy Pods | Identity/certificate status, proxy logs, handshake errors, clocks | Restore issuer/trust using approved procedure; verify both endpoints | Expiry monitoring and rotation game day |
| Control plane unavailable or invalid config | New config fails to propagate or proxy reports rejection | Control-plane readiness/logs and data-plane status | Restore control plane or revert invalid config | Staged config rollout, validation and HA review |
| Proxy CPU/memory pressure | Tail latency increases, throttling or restarts rise | Container resource metrics, restarts, node pressure, comparable baseline | Reduce rollout scope; adjust reviewed resource policy or workload concurrency | Measure per-Pod overhead and capacity headroom |
| NetworkPolicy blocks mesh path | Direct path and meshed path differ; proxy cannot reach control plane/peer | Policy selectors, CNI events/flows if available, DNS/control-plane connectivity | Add narrowly scoped verified allow rule or correct labels/ports | Policy tests include proxy/control-plane/DNS paths |
| Job/CronJob fails to complete | Work finished but Pod remains running or batch timeout occurs | Pod containers/status, termination events, proxy lifecycle docs | Use supported mesh-aware Job handling or opt out only under reviewed policy | Dedicated batch-workload test before enrollment |
| Mesh removal leaves residual state | Pods still injected, admission config persists, traffic breaks | Namespace labels, webhook config, control-plane resources, live Pod specs | Follow official uninstall and recreate workloads as needed | Documented exit checklist and ownership inventory |

### Control-plane HA, version skew and configuration storms

High availability is more than running multiple replicas: dependencies, certificates, webhook availability, scheduling, resource limits, upgrade order, and recovery procedures matter. A control-plane outage can have a small immediate data-plane impact and still create a latent risk if configuration or identity cannot renew. Monitor both present request health and the ability to safely change state.

Version skew between control plane, proxies, CLI, CRDs, and Kubernetes APIs can create subtle failures. Use the selected release's official upgrade guide to establish supported skew and order. Avoid mixing commands from `latest`, edge, stable, and vendor-supported distributions. Roll out upgrades in a throwaway cluster, then a low-risk ring, with a defined rollback trigger.

Configuration push storms can occur when broad changes trigger many proxies to receive new state. Validate changes, scope them narrowly, observe propagation and proxy resource use, and avoid changing many namespaces at once. A policy that is syntactically valid can still cause a traffic outage; validate behavior with bounded tests.

### Ownership model

| Responsibility | Primary owner | Evidence / control |
|---|---|---|
| Mesh control plane and upgrades | Platform team | Compatibility matrix, release notes, health checks, rollback runbook |
| Application enrollment and readiness | Service owner with platform support | Proxy presence, health probes, startup/shutdown tests |
| Identity and trust lifecycle | Platform/security owner | Expiry signals, rotation procedure, trust inventory |
| Authorization policy | Security/platform plus service owner | Reviewed policy, positive and negative tests |
| NetworkPolicy/CNI | Platform/network owner | Flow matrix, policy test, CNI enforcement evidence |
| Telemetry and SLOs | Service owner / observability team | Request-level SLOs, proxy and app signals, alert tests |
| Incident response | On-call owner | Runbook, escalation path, post-incident actions |
| Exit and decommission | Platform + service owner | No-mesh traffic test, label/webhook cleanup, resource inventory |

### Exit strategy (throwaway cluster only)

**⚠ DESTRUCTIVE — mesh removal can interrupt traffic and delete owned resources. Never test removal in production as part of this lesson.**

1. Capture current namespaces, workload templates, labels, webhook state, custom resources, and request success.
2. Identify every namespace and workload enrolled in the mesh. Confirm ownership of all resources to be removed.
3. Use the selected Linkerd release's official uninstall instructions; do not invent a generic uninstall command or delete CRDs blindly.
4. Remove the enrollment label/configuration through a guarded mutation, then recreate only the sample workload so the new Pods are not injected.
5. Verify live Pod container lists and run the same request test without the proxy.
6. Verify webhook configuration, control-plane resources, extensions, CRDs and custom resources according to official uninstall guidance. Do not delete a shared CRD if other resources depend on it.
7. Confirm no port-forward or local process remains and record post-cleanup cluster state.

An uninstall that removes the control plane while application Pods still depend on injected proxies may leave confusing residual behavior. Confirm actual state, not just command exit status.

### 7.7 SRE lens

Relevant service-level indicators include request success, latency (especially p95/p99), proxy and control-plane availability, configuration propagation, identity/certificate expiry, proxy restart rate, CPU/memory pressure, and telemetry gaps. Metric names and labels are implementation/version-specific; verify them before writing alert rules. Mesh telemetry is a useful transport view, not a replacement for application-level business outcomes, distributed traces, or service ownership.

### Alert → triage → mitigation → follow-up

- **Alert:** request errors/latency rise, proxy restarts increase, control plane is unhealthy, or identity renewal is nearing its recovery deadline.
- **Triage:** determine whether the fault is application, proxy, control plane, identity, NetworkPolicy, DNS, or dependency related. Compare unmeshed and meshed paths only in a safe test environment.
- **Mitigation:** stop expanding the rollout; restore the last known-good configuration; remove enrollment from a single low-risk workload only if that is a documented and tested rollback path.
- **Follow-up:** preserve sanitized events/logs, identify the first failing component, add a test or alert, update the compatibility matrix, and run a controlled rehearsal.

The blast radius depends on the change: an application annotation may affect one deployment, a namespace label may affect all recreated Pods in that namespace, a webhook failure can affect new Pod creation across its scope, and a control-plane or trust change can affect many services. Resource/cost review should include proxy overhead per Pod, control-plane replicas, telemetry add-ons, test environments, and on-call/debugging time.

### 7.8 Security lens

| Threat | Control | Verification method | What remains unaddressed |
|---|---|---|---|
| Workload impersonation / identity mismatch | Correct identity issuance, trust configuration, and enrollment | Inspect identity status and test a permitted peer connection | Compromised workload can still misuse its own identity |
| mTLS mistaken for authorization | Explicit identity-to-action policy in Unit 8 and application authorization | Negative tests for an unauthorized identity | Policy mistakes and application-level authorization gaps remain |
| Unintended plaintext / incomplete enrollment | Inventory mesh participation and test real request paths | Inspect live Pods and use documented TLS/identity diagnostics | Unmeshed or bypass paths may exist outside the test scope |
| Overly broad authorization | Narrow policy scope and reviewed defaults | Positive and negative policy tests | Admin privileges and policy engine defects remain |
| Compromised control plane/webhook | Least privilege, supply-chain controls, audit, version pinning | Review RBAC, images, admission config, logs | Cluster administrator compromise remains high impact |
| Expired identity/trust | Expiry monitoring and rehearsed rotation | Check certificate validity/status and handshake tests | Monitoring can miss alternate endpoints or stale telemetry |
| Sidecar bypass / non-meshed Job | Enrollment inventory and workload-class tests | Compare Pod specs, Job behavior and traffic path | Host-network/special workloads need separate review |
| NetworkPolicy blocks control/data plane | Explicit policy matrix and CNI validation | Inspect selectors/ports and test allowed paths | CNI-specific behavior may differ from a `kind` lab |
| Sensitive telemetry or mirrored data | Minimize payload collection, access-control telemetry, redact secrets | Inspect telemetry configuration and access logs | Metadata may still be sensitive; data retention remains a concern |
| Excessive proxy/control-plane privileges or supply-chain risk | Review RBAC, image source, provenance, admission and upgrade process | Compare installed manifests with official release artifacts | A trusted upstream can still have vulnerabilities |

A service mesh is one control layer, not “zero trust” by itself. NetworkPolicy constrains reachability; mesh identity/policy can constrain workload communication; application authorization decides whether a request may perform a business action. Use them as complementary controls.

### 7.9 Production checklist

- [ ] **Compatibility:** record Kubernetes, mesh CLI/control-plane, proxy, and CRD versions; compare them with official support documentation.
- [ ] **Install source:** use the selected distribution's official instructions; review rendered manifests and supply-chain provenance.
- [ ] **Control plane:** verify health, readiness, webhook availability, and recovery procedures.
- [ ] **Enrollment:** inspect live Pods and prove proxy presence; do not rely on labels alone.
- [ ] **Request path:** test the sample API and internal feature call under the intended mesh configuration.
- [ ] **Resources:** record baseline and meshed CPU/memory, restarts, throttling, median/p95 latency and error count.
- [ ] **Startup/probes/Jobs:** test readiness, termination, gRPC/streaming, and batch completion where used.
- [ ] **NetworkPolicy:** confirm DNS, peer, control-plane, telemetry, and probe paths are explicitly understood.
- [ ] **Identity lifecycle:** document trust issuer, expiry monitoring, rotation ownership, and failure recovery.
- [ ] **Telemetry:** identify verified signals and limitations; do not deploy a full stack solely for this lesson.
- [ ] **Upgrade/rollback:** rehearse upgrade in a throwaway cluster and define supported version skew.
- [ ] **Ownership:** assign control plane, app enrollment, policy, identity, observability, and incident owners.
- [ ] **Runbooks:** test webhook, proxy, control-plane, identity, and NetworkPolicy failure paths.
- [ ] **Exit:** document official uninstall, residual-state checks, workload recreation, and no-mesh verification.
- [ ] **Evidence:** retain sanitized version list, status/events, measurement data, decision record, and cleanup proof.

### 7.10 Hands-on lab set

| Lab | Goal | Evidence | Cleanup | Stretch |
|---|---|---|---|---|
| 1 — Decision and trace | Draw a no-mesh and mesh path; identify control/data plane and decide what needs protection | Annotated path and blank ADR | No cluster mutation required | Map a gRPC/streaming path |
| 2 — Mandatory install/measure | Install Linkerd, enroll one sample, prove proxy presence, compare baseline/meshed measurements | Versions, Pod proof, request logs, measurement table, decision memo | Remove enrollment, uninstall via official route, verify clean cluster | Add only a minimal verified telemetry extension after baseline |
| 3 — Incremental onboarding pitfall | Investigate one bounded injection/probe/NetworkPolicy issue and restore the sample | Events, before/after state, root-cause notes | Restore workload and policy state | Test a Job/CronJob separately |
| 4 — Control-plane failure rehearsal (optional) | Observe bounded behavior during a short control-plane interruption if safe | Request results, control-plane/proxy state, recovery evidence | Restore control plane and verify requests | Repeat after checking release-specific guidance |
| 5 — Exit verification (optional) | Remove mesh participation in a throwaway cluster | No-mesh request test and resource inventory | Follow official uninstall and verify residual state | Compare resource state before/after removal |

### Lab 1 — Service mesh decision and architecture trace

**Goal:** create an accurate logical request trace and record whether the use case warrants a mesh. **Estimate:** 30–45 minutes; no cluster changes and negligible additional resource use. **Prerequisites:** M04 Units 1–6 and the running example.

1. Draw `model-api` → `feature-service` including source proxy, CNI/NetworkPolicy enforcement, destination proxy, and application. Label control-plane communication separately from application traffic.
2. Draw the no-mesh path and mark which requirements would otherwise be implemented in application libraries or platform components.
3. Identify which properties need evidence: workload identity, transport encryption, policy, telemetry, retries, and latency.
4. Complete the ADR template in Section 7.5 with unknowns explicitly marked. Do not claim a packet capture or live measurement from a diagram.
5. **Expected result [ILLUSTRATIVE]:** a logical diagram and a decision record listing requirements, alternatives, risks, owners, and measurements still needed.
6. Evidence proves that the learner can reason about architecture; it does not prove any live traffic follows the drawing.

**Cleanup / repeatability:** no cluster changes; remove only local scratch files if desired. Re-run by drawing the path for another service. No post-cleanup cluster verification is needed because this lab is read-only.

### Lab 2 — Mandatory: install and measure Linkerd on kind

**Goal:** install one compatible Linkerd release in a disposable cluster, mesh only a sample workload, measure baseline versus meshed behavior, and remove the mesh cleanly. **Estimate:** 2–4 hours depending on image downloads and compatibility issues. **Planning footprint:** the mesh and sample app share the 4-CPU/8-GB/30-GB laptop budget; no fixed memory or CPU figure is asserted. Stop other heavy labs and do not run Cilium/Hubble or a full observability stack simultaneously.

**Prerequisites:** Docker, `kind`, `kubectl`, Linkerd CLI from its official current installation instructions, OpenSSL if inspecting identity material, and a sample `model-api` / `feature-service` app with a bounded health or request endpoint. Confirm the app exists or deploy the already-reviewed M04 sample; this lesson does not fabricate a full application manifest.

**Step 1 — Inspect machine and cluster.** Record OS/WSL2 details, CPU/RAM/disk availability, Docker status, `kind version`, `kubectl version`, and current context. Use `kind get clusters` before creating anything. If using WSL2, ensure Docker and the CLI/kubeconfig are reachable from the same environment. Do not assume Windows `localhost`, WSL2 `localhost`, kind node IP, and Pod IP are interchangeable.

**Step 2 — Create/reuse the throwaway cluster.** Check that `m04-mesh-lab` is not already a valuable cluster. Create it only if absent and the laptop has sufficient resources. Verify that the actual context is `kind-m04-mesh-lab` or update the guard to the exact observed context. Before every mutation, run the guard from Section 7.4 and inspect cluster identity. If a previous mesh, Cilium/Hubble lab, or full observability stack is running, remove it using its official procedure first and verify cleanup.

**Step 3 — Check official compatibility and install.** Read the current Linkerd installation and supported Kubernetes version pages. Install the CLI from the documented official source, run `linkerd version`, and execute `linkerd check --pre`. Resolve all failed prechecks before applying manifests. Confirm whether Gateway API CRDs are present and which release Linkerd requires. Review the rendered installation resources, then install CRDs first and the control plane second using the official syntax for the selected version. The consulted official guide documents `linkerd install --crds | kubectl apply -f -` followed by `linkerd install | kubectl apply -f -`; verify this remains correct for the exact release/distribution. Run `linkerd check` after installation. **Do not install viz initially.**

**Step 4 — Capture baseline.** Confirm the app and Service are ready. Use the same local client, endpoint, request payload, concurrency, and duration planned for the meshed test. A small bounded test such as 5 warm-up requests followed by 100 sequential measured requests is **[ILLUSTRATIVE]**; adjust to avoid saturating the laptop. Record individual latencies, success/errors, total requests and duration. Capture Pod/node CPU and memory with a documented method. `kubectl top` only works when a metrics source is available; if it is not, record “unavailable” or use a documented local container/runtime measurement instead of assuming it works. Do not add a large metrics stack just to fill one table.

**Step 5 — Enroll one namespace.** Inspect the existing namespace labels and Pod template. Verify current Linkerd injection annotation/label semantics. The commonly documented namespace label is `linkerd.io/inject=enabled`, but check the selected release before applying it. Guard the mutation. Recreate only the sample deployment through a reviewed rollout so new Pods can receive injection. Check events and the live Pod's container list. Run the version-appropriate Linkerd proxy check and confirm the request still succeeds. A namespace label alone is not proof.

**Step 6 — Measure meshed state.** Repeat exactly the baseline workload and sampling method. Capture application container resources, proxy resources, control-plane resources, restarts/throttling, latency distribution, errors, and run conditions. If metrics are unavailable, record that fact rather than inventing values. Repeat runs if the machine remains responsive. Do not declare the mesh faster or slower from a single noisy run.

| Metric | Baseline | Meshed | Delta | Method | Run count | Caveats |
|---|---|---|---|---|---|---|
| Median latency |  |  |  |  |  |  |
| p95 latency |  |  |  |  |  |  |
| Success / errors |  |  |  |  |  |  |
| App CPU / memory |  |  |  |  |  |  |
| Proxy CPU / memory | N/A |  |  |  |  |  |
| Control-plane CPU / memory | N/A |  |  |  |  |  |
| Restarts / throttling |  |  |  |  |  |  |
| Test duration / request count |  |  |  |  |  |  |

**Step 7 — Optional bounded control-plane test.** Do this only if the selected Linkerd version's official docs describe a safe test and the cluster is disposable. Do not delete CRDs, identity resources, or the whole control plane as a shortcut. If no safe reversible interruption procedure is verified, record the experiment as proposed and do not run it. If performed, use a brief, bounded interruption, continuous low-rate requests, and immediate recovery; capture proxy status, request results, and control-plane recovery. Do not generalize this result to all failure modes.

**Step 8 — Fill decision memo.** Compare no-mesh and Linkerd using only actual results. Istio remains a documented alternative, not a second installed system. Do not prefill a winner or use fabricated RAM/latency numbers. If the test was too noisy, say so and propose a better run.

**Cleanup and post-cleanup verification.** **⚠ DESTRUCTIVE:** removing a mesh can disrupt traffic. First guard the context and confirm the cluster is throwaway. Remove the namespace enrollment label/configuration and recreate the sample workload as needed; prove it no longer has the proxy. Then follow the selected release's official Linkerd uninstall procedure. Do not delete CRDs unless the official procedure and resource ownership show it is safe; CRDs may have dependent custom resources. Verify that sample requests work without mesh enrollment, control-plane resources are removed as expected, no port-forward remains, and no other workload was affected. If the cluster was created solely for this lab, delete only the exact named cluster after final context and ownership checks. Remove temporary evidence secrets or generated credentials; retain only sanitized evidence. The entire lab is repeatable from a clean throwaway cluster. **This lesson does not claim the lab was executed.**

### Lab 3 — Incremental onboarding and operational pitfall

**Goal:** observe a bounded failure related to injection, readiness, or NetworkPolicy and restore service. **Estimate:** 45–90 minutes; use the existing throwaway cluster only after Lab 2's baseline and evidence are saved. **Prerequisites:** sample app healthy with Linkerd enrolled and the context guard passing.

1. Capture Pod descriptions, container lists, request success and current namespace labels.
2. Choose exactly one issue: (a) remove the injection label and recreate a single sample Pod, (b) inspect a known readiness/probe issue without changing production-like shared settings, or (c) use a pre-reviewed throwaway NetworkPolicy that blocks one known required flow. Do not inject multiple failures at once.
3. Before mutation, guard context, record the exact resource and save its original configuration. Bound the test to the sample namespace.
4. Observe Pod events, proxy status, application readiness, and request outcome. Do not assume every failure is caused by the mesh; check Service endpoints and application logs.
5. Restore the original label/policy/configuration and recreate only the affected sample workload if needed.
6. **Expected output [ILLUSTRATIVE]:** the selected change produces a specific, bounded discrepancy (such as no proxy in a newly created Pod or a blocked flow), and restoration returns the sample to its baseline.
7. Evidence proves only this specific test and configuration; it does not prove all probes or NetworkPolicy behavior is identical across CNIs and mesh releases.

**Cleanup:** verify the original namespace label and policy are restored, all sample Pods are healthy, requests succeed, and no temporary resources remain. Repeat by restoring baseline first and changing one variable.

### Lab 4 — Optional control-plane failure or upgrade rehearsal

**Goal:** understand the selected mesh's failure semantics without unbounded disruption. **Estimate:** 45–120 minutes; resource footprint similar to Lab 2. **Prerequisites:** clean throwaway cluster, documented release-specific procedure, continuous low-rate request test, and a clear recovery path.

1. Consult official Linkerd docs for the relevant component, upgrade order, and failure behavior. If no safe procedure can be verified, do not interrupt the control plane.
2. Record healthy control-plane/proxy state and a short baseline request test.
3. Perform only a reversible, bounded action documented for the selected release. Do not delete CRDs, identity roots, or admission configuration as a test.
4. Observe existing requests, new Pod creation, proxy/control-plane status, and recovery. Record what was and was not tested.
5. Restore the component immediately and verify normal requests and readiness.

**Expected result [ILLUSTRATIVE]:** behavior is observed rather than assumed; it may differ by component, cached state, certificate lifetime, and proxy restart. This lesson does not claim this experiment ran. Cleanup means returning all components to ready state and verifying no temporary scale changes or test resources remain.

### Lab 5 — Optional mesh removal and exit verification

**Goal:** prove the sample can operate without mesh participation. **Estimate:** 45–90 minutes; throwaway cluster only.

1. Capture a healthy meshed request and inventory namespace labels, injected Pod containers, webhooks, control-plane resources and CRDs.
2. Guard context and follow the current official Linkerd uninstall procedure. Remove enrollment from the sample and recreate it.
3. Verify no proxy is present in the new Pod, the sample request succeeds, and no unrelated namespace changed.
4. Inspect residual resources according to the official cleanup guide. Do not blanket-delete CRDs; determine whether any other resource depends on them.
5. Save sanitized before/after evidence.

**Expected output [ILLUSTRATIVE]:** a healthy sample workload runs without the mesh proxy and only intended resources are removed. If that is not true, stop and repair the throwaway cluster rather than claiming success. Cleanup includes removal of the exact lab cluster if lab-owned and verification of no remaining port-forward or temporary material.

### 7.11 Self-check questions

1. **What does a service mesh provide, and what does it not provide?**  
   **Answer:** It can standardize workload communication features such as identity, transport security, traffic behavior, and telemetry. It does not automatically supply correct application authorization, fix bad code, or replace NetworkPolicy. **Tempting wrong answer:** “Installing the mesh makes all services zero trust.” Installation alone proves neither enrollment nor policy correctness.

2. **What is the control plane versus data plane?**  
   **Answer:** The control plane configures and supports data-plane components; the data plane mediates application traffic. **Tempting wrong answer:** “Every request passes through the control plane.” That confuses management with traffic forwarding.

3. **Is ambient/sidecarless behavior interchangeable with sidecar mode?**  
   **Answer:** No. Interception, L4/L7 handling, policy attachment, telemetry, and migration behavior vary. **Tempting wrong answer:** “Sidecarless is just sidecar mode without the container.” The data path and supported features can differ materially.

4. **Why is an injection label insufficient proof?**  
   **Answer:** The label is configuration intent; existing Pods may not be recreated, webhook injection can fail, and live Pod state may differ. Inspect actual containers, events, proxy health, and request flow. **Tempting wrong answer:** “Label present means every Pod is meshed.”

5. **Why does NetworkPolicy still matter?**  
   **Answer:** It provides network reachability controls through the CNI, separate from mesh identity and L7 policy. It can block control-plane, DNS, telemetry, or peer traffic. **Tempting wrong answer:** “The mesh encrypts traffic, so network policy is redundant.”

6. **What happens when the control plane is unavailable?**  
   **Answer:** Existing proxies may continue with cached state, but new configuration or identity operations may fail; restarts and certificate expiry can change behavior. Verify the selected implementation. **Tempting wrong answer:** “Traffic always continues” or “traffic always stops.”

7. **How do you measure overhead without inventing a benchmark?**  
   **Answer:** Keep workload, concurrency, warm-up, duration and resource limits comparable; repeat runs; report median/p95, CPU/memory, errors and caveats. **Tempting wrong answer:** “One average latency result proves the mesh cost.”

8. **Does mTLS replace authorization?**  
   **Answer:** No. mTLS can authenticate workload identities and protect transport; policy and application logic decide what those identities may do. **Tempting wrong answer:** “A trusted workload may call every service operation.”

9. **How should a proxy or injection failure be handled?**  
   **Answer:** Determine whether it affects existing traffic, new Pod admission, or only one workload; inspect events and health, pause rollout, restore the last known-good state, and verify requests. **Tempting wrong answer:** “Delete the mesh and its CRDs immediately.” That may increase blast radius or delete dependent resources.

10. **Why is mesh removal a high-risk change?**  
    **Answer:** Running Pods, labels, webhooks, identity, policies, and control-plane resources may be coupled. Use official cleanup, recreate workloads as needed, test the no-mesh path, and inspect residual resources. **Tempting wrong answer:** “Uninstalling the package guarantees all proxies disappear.”

### 7.12 Evidence artifacts

Save evidence locally under `evidence/unit-07/`; this is a suggested evidence location and not permission to create repository files other than the lesson. Keep it outside version control or exclude it using the learner's own repository policy.

- `versions.txt` — OS/WSL2 details, Docker, `kind`, Kubernetes server, Linkerd CLI/control plane, and relevant CRD versions.
- `cluster-context.txt` — context name and sanitized cluster identity confirmation.
- `baseline-pods.txt` / `meshed-pods.txt` — Pod readiness and container names without secrets.
- `control-plane-check.txt` / `proxy-check.txt` — sanitized output from version-appropriate health commands.
- `baseline-requests.csv` / `meshed-requests.csv` — timestamp, duration, success/error; no sensitive payloads.
- `resource-samples.csv` — CPU/memory source, sampling interval, Pod/container, and caveats.
- `measurement-summary.md` — median/p95, run count, test conditions, errors, restarts and throttling.
- `events-and-diagnostics.txt` — sanitized events and relevant log excerpts.
- `mesh-decision-record.md` — alternatives, constraints, measured evidence, decision, risks and owner.
- `cleanup-proof.txt` — no-mesh request test, proxy absence, resource inventory, and cluster cleanup status.
- `unresolved-verification.md` — release/API/compatibility items that remain open.

Do not save private keys, tokens, raw Secret YAML, full request bodies, or sensitive telemetry. A screenshot of a dashboard is not sufficient evidence of proxy enrollment or end-to-end encryption. Evidence should be reproducible and tied to a specific version and request path.

### 7.13 Common interview and design-review questions

1. **When is a service mesh justified over libraries or no mesh?**  
   **Model answer:** It is justified when multiple services need shared identity, transport security, policy, or telemetry that is difficult to implement consistently in applications. The team must be able to operate proxies, control plane, upgrades, trust lifecycle, and incident response. Compare with libraries and native Kubernetes features, then pilot one low-risk service and measure overhead and operational value. Evidence includes baseline/meshed tests, a compatibility review, and clear ownership. A small service count and simple requirements may not justify the added failure modes.

2. **How do you compare Istio and Linkerd under a strict laptop budget?**  
   **Model answer:** Select one for the hands-on lab, install it alone, and measure the same workload under identical conditions. Record control-plane and per-workload proxy resources separately, median/p95 latency, errors, restarts and test conditions. Compare official feature/support matrices and operational complexity for the real requirements. Do not install both simultaneously or infer a resource winner from general claims. The local result is a learning measurement, not a production benchmark.

3. **What happens to data-plane traffic if the control plane fails?**  
   **Model answer:** Existing proxies may continue with cached configuration, but new config distribution, identity operations, restarts, or certificate renewal may be impaired. Behavior depends on the mesh, failure component, cached state, proxy lifecycle and identity validity. Test a bounded scenario in a disposable cluster and record existing request behavior, new Pod creation, proxy health and recovery. Avoid universal guarantees.

4. **How do proxies, NetworkPolicy and application authorization interact?**  
   **Model answer:** The proxy mediates selected traffic and may apply identity or traffic policy; NetworkPolicy/CNI controls network reachability; the application authorizes business actions. All three layers must align. A NetworkPolicy can block the proxy's required control-plane or peer path; mTLS can authenticate a caller without granting a business operation. Use positive and negative tests at each layer.

5. **How would you roll out, upgrade and remove a mesh with bounded blast radius?**  
   **Model answer:** Start in a throwaway cluster, validate compatibility, measure baseline, then onboard dev/test, one low-risk service, one namespace and broader fleet with entry/exit gates. Maintain a version matrix, upgrade rehearsal, rollback criteria, named owners and identity lifecycle monitoring. For removal, use official cleanup, remove enrollment, recreate workloads as required, verify no proxy and successful direct requests, inspect webhooks/CRDs/custom resources, and never delete shared CRDs blindly.

### 7.14 Sources and verification notes

### Consulted sources

- **Linkerd, “Getting Started.”** Consulted for the CLI/control-plane sequence, pre-install validation, CRD prerequisites, injection concept, proxy check, and optional Viz extension. Current page content may use an edge release; do not copy its example version as a stable recommendation.
- **Linkerd, “Installing Linkerd.”** Consulted for CLI versus Helm installation paths, Gateway API prerequisites, pre-install checks, and `linkerd check`.
- **Linkerd, “Troubleshooting.”** Consulted for the purpose and examples of `linkerd check` and control-plane resource diagnostics.
- **Linkerd, “Adding your services to Linkerd.”** Consulted for the namespace injection annotation concept.
- **Istio, “Deployment” and “Architecture.”** Consulted for `istiod`, Envoy, deployment considerations, and identity/configuration responsibilities.
- **Istio, “Sidecar or ambient?” and ambient architecture pages.** Consulted for the conceptual distinction between per-Pod sidecars and ambient data-plane components.
- **Gateway API, “The GAMMA Initiative” and “Gateway API for Service Mesh.”** Consulted for the GAMMA scope and the relationship between Gateway API and east-west routing.
- **Available M04 master syllabus prompt and Roadmap copy (`Roadmap(5).md`).** Consulted for Unit 7 requirements, unit order, one-mesh constraint, resource-budget expectations, and cross-unit boundaries.
- **Available M04 Unit 5 and Unit 6 lessons.** Consulted for the sample namespace/service naming used in this lesson and the prior TLS/NetworkPolicy context.
- **Uploaded Unit 7 prompt.** Used as the controlling structure and safety specification.

### Official references requiring verification before execution

- Linkerd current stable/vendor-supported release, supported Kubernetes versions, CLI installation instructions, required Gateway API CRDs, exact install/uninstall commands, and supported proxy/control-plane skew.
- Linkerd current policy and routing resource availability, `ServiceProfile` status, injection semantics, probe behavior, Job/CronJob lifecycle, metrics and proxy check syntax.
- Istio current CRD schemas and supported version matrix for `VirtualService`, `DestinationRule`, `Gateway`, `PeerAuthentication`, `AuthorizationPolicy`, sidecar mode and ambient mode.
- Gateway API current release and conformance matrix for the selected mesh; GAMMA support does not imply every implementation supports every feature.
- Kubernetes documentation for admission webhook failure policy, Pod lifecycle, probes, resource metrics, NetworkPolicy, and CRD deletion impact.
- SPIFFE specifications for workload identity concepts.
- Google SRE Book/Workbook for rollout, change management, SLOs and incident response.
- Official project governance, license, and support statements; no legal or maintenance conclusion is made here.

### Unresolved verification items

1. Exact Linkerd release and compatibility with the learner's Kubernetes/`kind` version.
2. Official CLI install command and distribution choice for the learner's environment.
3. Gateway API CRD version and whether the selected Linkerd features require installation or a particular channel.
4. Current injection annotation/label semantics and proxy-check commands for the selected release.
5. Current resource names, CRD fields, and supported routing/policy features for Linkerd and Istio.
6. Whether the sample app and its Service/port contract are present in the actual repository; this lesson assumes the Unit 5-style `ml-platform` contract for its request trace.
7. Availability of a metrics source for `kubectl top`; no resource measurement has been performed.
8. Safe, release-specific control-plane interruption and uninstall procedure for the chosen distribution.
9. Actual footprint, latency, error rate, control-plane failure behavior, and cleanup outcomes; all learner result tables remain blank.

### Runtime execution status

**Reasoned review only; commands and labs were not executed in this environment.** Selected official documentation pages were consulted, but there was no live Kubernetes cluster validation and no full audit of every current version-specific API or installation instruction. The self-audit below is not an independent external audit.

## Appendix A — Command and manifest reference

| Command / configuration | Purpose | Safe use / expected evidence | Version/implementation caveat |
|---|---|---|---|
| `kubectl config current-context` | Identify current cluster context | Must equal the explicit throwaway context before mutation | Context name alone does not prove cluster ownership |
| `kind get clusters` | Inspect local kind clusters | Confirm exact lab cluster exists before create/delete | Local tool/runtime state |
| `kubectl get pods -n ml-platform -o wide` | Inspect workload state | Pod readiness, node placement, Pod IP | Namespace may differ in the actual shared contract |
| `linkerd version` | Inspect CLI and server version | CLI version and control-plane availability | Exact output varies by release |
| `linkerd check --pre` | Pre-install validation | List of checks and failures | Confirm command against selected release |
| `linkerd install --crds` | Render/apply CRDs through official installation workflow | Review output and apply only after context guard | Official current docs show this pattern; verify release/distribution |
| `linkerd install` | Render/apply control-plane resources | Inspect generated manifest and control-plane readiness | Verify exact flags and release; not a production install standard by itself |
| `linkerd check` | Verify installation health | Check results for control plane and configured components | Does not prove application request success |
| `kubectl describe pod <pod> -n <namespace>` | Inspect containers, events and readiness | Proxy presence and admission/startup evidence | Pod name and namespace must be discovered |
| `kubectl get events -n <namespace> --sort-by=.metadata.creationTimestamp` | Review recent failures | Admission, scheduling, readiness events | Events are not a complete audit log |
| `kubectl top pods -n <namespace>` | Sample CPU/memory | Per-Pod resource snapshot if metrics source exists | Requires metrics API/source; otherwise unavailable |
| `kubectl label namespace ml-platform linkerd.io/inject=enabled` | Request Linkerd injection | Inspect label before and after | Verify current label semantics; mutating operation needs context guard |
| `kubectl get crd` | Inventory CRDs | Identify mesh/Gateway API CRDs | Do not delete shared CRDs blindly |
| Official uninstall procedure | Remove mesh | Verify proxy-free Pods and expected resources absent | Must match selected release/distribution; high-risk in shared clusters |

## Appendix B — Troubleshooting decision trees

### B1. Workload expected to be meshed has no proxy

- **Symptom:** namespace label is present, but the Pod has only application containers.
- **Hypotheses:** Pod predates enrollment; annotation/label is wrong; injection webhook is unhealthy; workload opt-out or policy applies; admission failed.
- **First evidence:** guarded `kubectl describe pod`, live Pod container list, namespace labels, Pod events, and current-version mesh injection diagnostics.
- **Interpretation:** label expresses intent; live Pod spec is the evidence of actual injection.
- **Safe mitigation:** fix the verified label/annotation or webhook issue, then recreate only the sample workload in the throwaway cluster.
- **Prevention:** post-deploy assertion checks container/proxy health and a request test.

### B2. Pod creation blocked by injection/admission

- **Symptom:** new Pods fail admission, remain pending, or emit webhook errors.
- **Hypotheses:** webhook endpoints unavailable, incompatible control plane, invalid configuration, certificate/trust problem, or admission timeout.
- **First evidence:** Pod events, webhook configuration/endpoints, control-plane readiness/logs, and selected mesh's documented diagnostics.
- **Interpretation:** separate admission failure from scheduler or application readiness failure.
- **Safe mitigation:** pause rollout and restore webhook/control-plane health using official guidance; avoid changing fail-open/fail-closed policy blindly.
- **Prevention:** test webhook upgrades, readiness, certificates and rollback in a disposable cluster.

### B3. Meshed request fails while direct Pod/Service request works

- **Symptom:** a request fails only after mesh enrollment.
- **Hypotheses:** proxy protocol handling, identity/policy, interception, DNS, NetworkPolicy, port mismatch, or proxy-to-app reachability.
- **First evidence:** compare Pod/Service endpoints, proxy health/logs, app logs, DNS, NetworkPolicy selectors/ports, and request result from the same client.
- **Interpretation:** a direct request may bypass the proxy and is not equivalent to the intended production path.
- **Safe mitigation:** isolate one flow and repair the documented cause; do not disable all policies or TLS as a shortcut.
- **Prevention:** maintain meshed positive/negative request tests and protocol-specific tests for gRPC/streaming.

### B4. Latency/CPU/memory regresses after enrollment

- **Symptom:** p95/p99 latency rises, throttling/restarts appear, or node pressure increases.
- **Hypotheses:** proxy resource overhead, CPU contention, different request workload, cold caches, added connection behavior, telemetry add-on cost, or application variance.
- **First evidence:** raw request timings, test conditions, per-container resource samples, restarts, throttling and node pressure.
- **Interpretation:** one average or one run cannot isolate causality.
- **Safe mitigation:** pause rollout; repeat comparable bounded tests; reduce scope and adjust reviewed resource settings only after identifying the bottleneck.
- **Prevention:** repeat runs, report median/p95 and errors, and keep control-plane and proxy resource measurements separate.

### B5. Existing traffic works but new configuration does not apply

- **Symptom:** current requests succeed but new policy/routing/configuration is absent or rejected.
- **Hypotheses:** control plane unavailable, config invalid, proxy disconnected, unsupported version/CRD, or propagation delay.
- **First evidence:** control-plane readiness/logs, proxy status, resource conditions/events, installed CRDs and release compatibility.
- **Interpretation:** cached data-plane state may remain while new desired state cannot propagate.
- **Safe mitigation:** restore control-plane health or revert the invalid change using the supported procedure.
- **Prevention:** validate manifests and configuration, stage changes, and alert on control-plane health/config rejection.

### B6. NetworkPolicy blocks proxy/control-plane/telemetry traffic

- **Symptom:** service calls or proxy checks fail after policy changes; DNS or metrics may disappear.
- **Hypotheses:** selectors/labels do not match, wrong port/protocol, egress/ingress isolation missing a required flow, or CNI-specific behavior.
- **First evidence:** NetworkPolicy manifests, live Pod labels, Service/endpoints, DNS tests, control-plane reachability, and CNI-supported flow evidence.
- **Interpretation:** mesh enrollment does not override CNI enforcement.
- **Safe mitigation:** add a narrowly scoped verified rule for the required flow in the throwaway cluster and rerun positive/negative tests.
- **Prevention:** include proxy, DNS, control-plane, telemetry, probe, and workload paths in the policy matrix.

### B7. Identity/certificate/issuer issue disrupts mesh communication

- **Symptom:** handshake or identity validation failures while Pods and Services are otherwise ready.
- **Hypotheses:** certificate expiry, trust mismatch, clock skew, issuer/control-plane issue, or identity policy mismatch.
- **First evidence:** current mesh identity diagnostics, proxy logs, certificate validity/status where exposed, control-plane readiness, and clock checks.
- **Interpretation:** transport failure and authorization denial can have similar application symptoms; classify the layer.
- **Safe mitigation:** follow the selected mesh's documented identity recovery/rotation procedure; do not copy Unit 6 cert-manager steps blindly into a mesh-managed identity system.
- **Prevention:** expiry/rotation monitoring, trust inventory, and a tested recovery runbook.

### B8. Mesh removal leaves residual configuration or breaks traffic

- **Symptom:** Pods still contain proxies, admission remains active, or requests fail after uninstall.
- **Hypotheses:** old Pods were not recreated, namespace labels remain, webhooks/CRDs/custom resources are still present, or uninstall order was wrong.
- **First evidence:** live Pod containers, namespace labels, webhook configuration, mesh resources, request tests and official uninstall documentation.
- **Interpretation:** deleting the control plane is not proof that every workload returned to the no-mesh state.
- **Safe mitigation:** restore the known-good sample path, remove enrollment per official instructions, recreate affected sample Pods and verify requests.
- **Prevention:** maintain a mesh inventory and a rehearsed exit checklist; never blanket-delete CRDs.

## Appendix C — Claim register

Confidence indicates confidence in the general claim as written, not verification of a particular learner environment. A `VERIFY` tag means current-version or runtime confirmation remains outstanding.

| ID | Section | Claim | Source and section | Confidence | Status tag | Verification needed |
|---|---|---|---|---|---|---|
| C01 | 7.2–7.3 | A mesh separates management/control functions from traffic-handling/data-plane functions | Linkerd Getting Started; Istio Architecture | High | Consulted | Confirm selected release component layout |
| C02 | 7.2 | Sidecar mode places a proxy alongside a workload Pod; Istio ambient uses node-level components and optional L7 proxies | Istio Sidecar or ambient?; Ambient architecture | High | Consulted, version-sensitive | Confirm selected Istio release/mode support |
| C03 | 7.2 | NetworkPolicy and mesh policy are distinct control layers | M04 syllabus; Kubernetes NetworkPolicy docs | High | General concept | Verify CNI enforcement in the actual cluster |
| C04 | 7.4 | Linkerd official docs describe `linkerd check --pre`, CRD-first installation, control-plane installation, and `linkerd check` | Linkerd Installing Linkerd | High | Consulted, version-sensitive | Reconfirm syntax for chosen release/distribution |
| C05 | 7.4 | Linkerd uses namespace/workload injection configuration and live Pod verification is necessary | Linkerd Adding your services | High | Consulted, version-sensitive | Confirm current label/annotation semantics |
| C06 | 7.5 | Istio uses `istiod` and Envoy for common sidecar data-plane deployments | Istio Architecture | High | Consulted | Confirm exact deployment mode |
| C07 | 7.5 | Linkerd proxy is described in official docs as a Rust-based micro-proxy | Linkerd architecture docs | Medium | VERIFY | Reconfirm wording against current official architecture page |
| C08 | 7.5 | Linkerd `ServiceProfile` status and routing support can change across releases | Linkerd routing/API docs | High | VERIFY | Inspect current API and migration docs |
| C09 | 7.5 | Gateway API/GAMMA addresses service-mesh/east-west routing and implementation support varies | Gateway API GAMMA / mesh overview | High | Consulted | Check chosen mesh conformance/resource support |
| C10 | 7.5 | GAMMA mesh support is in the Gateway API Standard Channel since v1.1.0 | Gateway API mesh overview | High | Consulted | Check current spec/channel and implementation support before use |
| C11 | 7.4/7.10 | Exact Kubernetes/mesh compatibility must be checked before installation | Official Linkerd supported Kubernetes versions and install docs | High | VERIFY | Select actual release pair |
| C12 | 7.4/7.10 | `kubectl top` depends on an available metrics source | Kubernetes resource metrics docs | High | VERIFY environment | Confirm Metrics API before measurement |
| C13 | 7.6 | Control-plane failure can affect configuration/identity operations differently from existing traffic | Mesh architecture and operational inference | High | VERIFY by implementation | Run only documented bounded experiment |
| C14 | 7.6 | Mesh removal may require workload recreation and cleanup of labels/webhooks/resources | Official uninstall guidance; Kubernetes Pod/admission behavior | High | VERSION-SENSITIVE | Follow selected release's uninstall instructions |
| C15 | 7.6 | CRD deletion can remove dependent custom resources | Kubernetes CRD documentation | High | General Kubernetes behavior | Inspect ownership/dependencies before cleanup |
| C16 | 7.5/7.10 | Performance must be measured under comparable conditions; no generic overhead number is asserted | Engineering methodology | High | Measurement plan only | Collect learner measurements |
| C17 | 7.8 | mTLS authenticates peers/ protects transport but does not define all application authorization | TLS/security architecture | High | General concept | Test policy and application behavior |
| C18 | 7.14 | Official documentation was consulted for selected architecture/install concepts | Sources listed in 7.14 | High | Consulted | Other version-sensitive pages still require review |
| C19 | 7.2 | The chosen `ml-platform` namespace/ports align with the available Unit 5 lesson, while Unit 6 has a separate illustrative namespace | M04 Unit 5 and Unit 6 files | High | ASSUMPTION / cross-file note | Confirm final repository contract before combining manifests |
| C20 | All | No live cluster lab or resource benchmark was executed during authoring | Runtime status | High | Runtime limitation | Human executes labs and records evidence |

## Appendix D — Ten-pass audit and correction log

This is an internal self-audit, not an independent external review.

| Pass | Result | Checks performed | Defects found / corrections made | Unresolved risks |
|---|---|---|---|---|
| 1. Completeness | PASS WITH LIMITATIONS | Exact title, sections 7.0–7.14, Appendices A–E, five labs, measurement lab and required diagrams/tables | Added decision tree, request/control-plane diagrams, comparison tables and troubleshooting trees | Unit 8/capstone source prompts were not available to inspect; module-wide choice recorded as an assumption |
| 2. Technical correctness | PASS WITH LIMITATIONS | Separated control plane/data plane, mesh/NetworkPolicy/authorization, and injection intent/live enrollment | Avoided universal traffic-continuity or performance claims | Failure behavior depends on selected release and was not runtime-tested |
| 3. Command/manifest validity | PASS WITH LIMITATIONS | Guard scripts, common Linkerd CLI patterns, context assertions and safe mutation order reviewed | Used explicit verification gates for release-sensitive installation and label behavior | Commands were not executed against a cluster |
| 4. Currency | PASS WITH LIMITATIONS | Consulted current official architecture/install pages for selected concepts; version-specific items tagged | No fixed release numbers, resource claims, or guessed current `ServiceProfile` API asserted | Compatibility matrix and exact install route need human confirmation |
| 5. Security | PASS WITH LIMITATIONS | No public endpoint/production secret, bounded failure tests, RBAC/identity/NetworkPolicy and CRD risks covered | Added warnings for destructive cleanup and proxy bypass | Actual cluster policy and admission behavior unknown |
| 6. Fabrication scan | PASS WITH LIMITATIONS | Checked release numbers, benchmarks, metrics, governance/licensing, expected outputs and execution claims | Kept measurement tables blank and outputs illustrative; no legal conclusion made | Some general architecture statements need release-specific recheck |
| 7. Executability | PASS WITH LIMITATIONS | Added context guards, ordered install/measure/cleanup, resource-budget guidance and alternative when metrics unavailable | Avoided inventing a universal uninstall command or control-plane failure test | Full lab feasibility depends on laptop and current release; no execution occurred |
| 8. Pedagogy | PASS | Beginner-to-expert sequence, glossary, diagrams, tables, guided commands, self-check answers | Added explicit alternatives and common misconceptions | Learner must adapt to existing app resources |
| 9. Cross-file consistency | PASS WITH LIMITATIONS | Checked M04 roadmap sequence, Unit 5 labels/ports and Unit 6 namespace distinction | Chose Linkerd as explicit assumption for Unit 8/capstone; adopted Unit 5-style `ml-platform` example for this lesson | Need to carry Linkerd choice into Unit 8 and capstone; their source prompts were not available |
| 10. Adversarial review | PASS WITH LIMITATIONS | Looked for misleading traffic guarantees, unsupported overhead claims, residual configuration, unsafe CRD deletion and scope creep | Kept control-plane test optional and reversible; no CRD deletion as routine cleanup | Human must verify commands, resource ownership and post-cleanup state |

## Appendix E — Human verification checklist and sign-off

Before using this lesson as an executable lab:

- [ ] Confirm exact destination path: `Stage 2E — Production DevOps & Platform Engineering/04-Kubernetes-Networking-Ingress-and-Service-Mesh/07-service-mesh-fundamentals-istio-and-linkerd.md`.
- [ ] Confirm the master M04 roadmap, Unit 8 prompt, capstone and any prompt pack do not already specify a different mesh. If they do, reconcile Unit 7, Unit 8 and capstone together.
- [ ] Verify the selected Linkerd release, Kubernetes/`kind` compatibility, official CLI install method, Gateway API CRD requirements, and install/uninstall procedure.
- [ ] Verify all CLI syntax, injection labels, proxy container/health checks, policy resources, and version-skew requirements against the selected release.
- [ ] Confirm the sample application and `ml-platform` namespace/service/port contract before applying any configuration.
- [ ] Confirm CPU/RAM/disk availability and remove other heavy lab components before starting the mesh lab.
- [ ] Capture baseline measurements before installation and repeat comparable measurements after enrollment; keep the decision memo blank until actual evidence exists.
- [ ] Prove proxy enrollment from live Pod state and verify the real request path.
- [ ] Run only bounded failure tests in the throwaway cluster; restore healthy state and verify requests.
- [ ] Follow official cleanup; verify workloads are no longer injected, no unexpected resources remain, and no shared CRDs were deleted.
- [ ] Ensure evidence contains no credentials, private keys, raw Secret YAML, or sensitive request payloads.
- [ ] Confirm no unrelated repository file was modified.

**Sign-off**

- Reviewer: ______________________________
- Date: __________________________________
- Environment / OS / WSL2 details: ______________________________
- Kubernetes / kind / mesh CLI / control-plane versions: ______________________________
- Result: ______________________________
- Outstanding verification items: ______________________________
- Human review completed: Yes / No

**Content status:** `DRAFT-AUDITED`  
**Chosen hands-on mesh:** Linkerd sidecar mode `[ASSUMPTION — carry into Unit 8 and capstone unless evidence-backed review changes all three]`  
**Audit type:** AI self-audit; not an independent external audit  
**Runtime status:** Reasoned review only; commands and labs were not executed in this environment.
