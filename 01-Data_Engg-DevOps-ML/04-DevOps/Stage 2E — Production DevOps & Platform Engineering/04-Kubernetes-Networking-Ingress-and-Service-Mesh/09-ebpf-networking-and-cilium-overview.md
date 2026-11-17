# eBPF networking and Cilium overview

## 9.0 Metadata, prerequisites and learning outcomes

**Stage:** Stage 2E — Production DevOps & Platform Engineering  
**Module:** M04 — Kubernetes Networking, Ingress and Service Mesh  
**Unit:** 9 — eBPF networking and Cilium overview  
**Target file:** `09-ebpf-networking-and-cilium-overview.md`  
**Estimated time:** 5–8 hours for the reading and read-only path; 3–5 additional hours if the Cilium-as-CNI lab is supported and performed  
**Prerequisites:** Linux/TCP/IP basics, Kubernetes Pods/Services, CNI concepts from Unit 1, Kubernetes NetworkPolicy from Unit 5, and basic cluster operations from M03  
**Core tools:** `kubectl`, `kind`, Docker, Cilium CLI, Helm (installation route dependent), and optionally Hubble  
**Awareness:** BPF maps and programs, kube-proxy replacement, WireGuard/IPsec, Cilium Gateway API, Tetragon, Falco, Pixie, Prometheus and Grafana  
**Documentation checked:** 2026-10-28 for the official Cilium pages listed in Section 9.14. The stable documentation results consulted identify Cilium 1.20.4; the `latest` pages may describe a development release and are not a reproducible version pin.  
**Runtime status:** Reasoned review only; commands and labs were not executed in this environment.

### Source availability and limitations

Available source files inspected: `Roadmap(5).md`, `PROMPT-Kubernetes-Networking-Ingress-and-Service-Mesh(9).md`, Units 1, 5, 7 and 8, and the uploaded Unit 9 prompt. The roadmap lists Unit 9 between Unit 8 and Unit 10. The available M04 syllabus copy treats Cilium/Hubble as implementation-specific awareness for earlier NetworkPolicy work and reserves this unit for a deeper eBPF/Cilium overview. The Unit 7/8 lessons use `ml-platform` and the model/feature service example; this unit reuses that terminology.

The exact `M04-Kubernetes-Networking-Ingress-and-Service-Mesh-Copy-Paste-Prompt-Pack.md`, Unit 10 lesson, and `Projects/README.md` / `Projects/01-secure-ingress-and-mtls-for-data-and-ml-apis.md` were not present as separate files in the inspected workspace. The available syllabus and uploaded Unit 9 prompt specify the section structure used here. No missing source has been represented as inspected.

**Important decision:** The primary hands-on route is a fresh, disposable `kind` cluster with Cilium as its CNI, but only if the learner's OS/kernel/runtime and chosen version meet the official prerequisites. The fallback is a read-only interpretation exercise. Do not migrate a shared cluster or replace a valuable cluster's CNI to complete this lesson.

### Learning outcomes

By the end, the learner should be able to:

1. Explain eBPF programs, kernel hooks, maps, the verifier and their safety limits.
2. Distinguish eBPF, CNI, datapath, control plane, user-space agent and Hubble.
3. Explain where Cilium can enforce policy and observe flows, without assuming all traffic bypasses iptables or conntrack.
4. Identify the operational consequences of replacing the default CNI in a new cluster.
5. Read a Cilium/Hubble flow record and separate observed facts from hypotheses.
6. Review native Kubernetes NetworkPolicy and Cilium-specific L3/L4/L7 and DNS/FQDN policy.
7. Explain the difference between network-layer encryption, TLS/mTLS identity and application authorization.
8. Choose between Cilium, Calico and a managed/default CNI using explicit operational criteria.
9. Follow a safe troubleshooting and migration runbook with read-only evidence first.
10. Design a reproducible performance test without inventing a benchmark or assuming eBPF is always faster.

## 9.1 Why this topic matters in production

Kubernetes networking failures often cross several layers: a Pod may be healthy but unreachable, a policy may deny DNS, a datapath upgrade may change traffic handling, or a flow record may show a drop without explaining the application-level cause. eBPF gives systems such as Cilium a way to attach verified programs to supported kernel paths for networking, security and observability, while Cilium combines that kernel datapath with Kubernetes-aware agents and policy APIs. This can simplify some packet-processing and visibility tasks, but it also adds kernel dependencies, privileged components, upgrade coupling and a new set of operational failure modes. The right engineering question is not “Is eBPF faster?” but “Does this specific datapath and policy design meet our security, reliability, performance and support requirements, demonstrated by repeatable evidence?”

## 9.2 Mental model and architecture

### From application request to kernel datapath

Consider `model-api` calling `feature-service` in namespace `ml-platform`.

```text
FastAPI model-api Pod
  |
  | connect() / send()
  v
Pod network namespace and attached datapath hooks
  |
  | eBPF program may classify, redirect, account for, or enforce policy
  v
Host networking / tunnel or native-routing path
  |
  | optional node-to-node encapsulation/encryption, depending on config
  v
Destination node / destination Pod datapath
  |
  | policy decision and service handling according to selected mode
  v
feature-service Pod
  |
  v
Redis / Postgres dependency as separately permitted by policy
```

This is a conceptual map, not a universal packet trace. The exact hook, service load-balancing path, tunnel/native-routing behavior, conntrack interaction and iptables involvement depend on Cilium version and configuration, kernel capabilities, traffic type, and optional kube-proxy replacement. Packet capture on the Pod, kind node container, WSL2 host and Windows host may show different interfaces and address translations.

### Cilium components and responsibilities

| Component | Responsibility | Operational caveat |
|---|---|---|
| Cilium agent | Runs on cluster nodes and configures/observes node-local networking, endpoint state and policy enforcement | Agent readiness is not the same as end-to-end application health |
| Cilium operator | Handles cluster-level coordination tasks assigned to the operator in the selected release, including relevant identity/IPAM responsibilities depending on mode | Exact responsibilities and deployment shape are release/configuration dependent |
| eBPF datapath | Kernel programs and maps used for supported packet handling, policy and telemetry paths | Maps/programs are kernel resources; debugging requires datapath-specific evidence |
| Kubernetes CNI integration | Connects Cilium to Pod network setup and endpoint lifecycle | Replacing a CNI is a cluster-level change, not an ordinary application rollout |
| Cilium identity/policy | Associates endpoint labels with security identities and evaluates configured policy | Identity allocation and policy synchronization can fail independently of app health |
| Hubble | Observability for network flows using Cilium's flow visibility facilities | A flow record does not prove application correctness, full payload contents, or that every packet was observed |
| Hubble Relay/UI (optional) | Aggregates/serves flow data and may provide a UI depending on installation | Adds resources and another component to operate; not required for the low-resource core lab |

### Control plane versus datapath

The **control plane** is responsible for distributing configuration and coordinating desired state. The **datapath** is the actual traffic-processing path. A control-plane API may accept a policy while an agent has not yet converged, or an agent can be unhealthy while some previously installed datapath state still affects traffic. Diagnose desired state, agent status, endpoint identity/policy state and observed flows separately.

Cilium is a Kubernetes CNI and networking/security platform, not just a command-line tool. Installing it as the CNI changes how the cluster connects Pods and may change service handling if optional kube-proxy replacement is configured. Cilium does not automatically replace application TLS, application authorization, every service-mesh capability, or a full metrics/logs/traces platform.

### What eBPF contributes

eBPF (extended Berkeley Packet Filter) allows a privileged loader to load programs into supported Linux kernel execution points. A program can inspect a bounded context and make a decision or update a map. Networking products use suitable hooks to classify packets, enforce policy, redirect traffic, maintain counters or emit events. The kernel verifier checks program properties such as safe memory access and bounded execution according to verifier rules; it does not prove that the program's policy is logically correct, that a privileged deployment is secure, or that the host cannot be misconfigured.

```text
Kubernetes object / operator config
              |
              v
      Cilium user-space agent
              |
       compiles/configures
              v
  eBPF program + BPF maps in kernel
              |
              v
   supported networking hook/path
              |
       packet verdict/action
              |
              v
   counters/events -> Hubble/telemetry
```

A **hook** is a supported place where a program can run. A **map** is a kernel data structure used to store/share state between programs or user space and kernel. The **verifier** checks program safety constraints before load. A **datapath** is the mechanism that processes traffic. A **CNI** is the plugin interface used to configure Pod networking; it is not synonymous with eBPF.

### eBPF, iptables and conntrack: no universal bypass claim

Cilium can implement selected service and policy paths with eBPF, and some configurations reduce or replace parts of traditional kube-proxy/iptables processing. Other features and paths may still use netfilter/iptables, conntrack, sockets, routing, tunneling or proxy redirection. Cilium's system-requirements documentation explicitly describes kernel/netfilter requirements for certain modes and L7 redirection, illustrating why “Cilium bypasses iptables” is too broad. Confirm the active datapath configuration and relevant flow path before drawing conclusions.

## 9.3 Core concepts and terminology

| Term | Definition | Common misconception |
|---|---|---|
| eBPF | Kernel facility for loading programs at supported hooks, subject to verifier and privilege constraints | Any eBPF program is automatically safe or correct |
| Verifier | Kernel component that checks allowed program behavior before load | It validates the security policy's business intent |
| BPF map | Kernel data structure for sharing state/counters/configuration with eBPF programs and user space | Every map has unlimited capacity |
| CNI | Container Network Interface used to configure Pod networking | CNI and service mesh are the same layer |
| Datapath | Actual path and mechanisms that process packets | The datapath is the same thing as the operator/control plane |
| Cilium agent | Node-level Cilium component that configures and monitors networking | One healthy agent proves every endpoint works |
| Security identity | Identity associated with an endpoint based on relevant labels/state | A Pod IP alone is a stable security principal |
| `CiliumNetworkPolicy` (CNP) | Cilium-specific namespaced policy API with capabilities beyond native Kubernetes NetworkPolicy | It is a portable Kubernetes API supported identically by all CNIs |
| `CiliumClusterwideNetworkPolicy` (CCNP) | Cilium-specific cluster-wide policy resource | Its scope is limited to one namespace |
| Hubble flow | An observation about a network flow as surfaced by Hubble | It always contains the full application payload |
| Verdict | A reported flow/policy outcome such as forwarded or dropped, as exposed by the selected tooling | A drop record always identifies the root cause without context |
| FQDN policy | Policy that can associate permitted destinations with DNS-derived names under documented Cilium behavior | It is a universal, perfect domain firewall for every protocol and resolver path |
| kube-proxy replacement | An optional design in which Cilium takes over supported Kubernetes service load-balancing functionality | It is automatically enabled or suitable for every cluster |
| WireGuard/IPsec | Network-layer encryption mechanisms supported in particular Cilium configurations | They provide application-level workload authorization or HTTP identity |
| L7 policy | Policy based on supported application-protocol attributes such as HTTP fields where proxy/redirection requirements are met | Every packet is automatically visible at L7 |
| Hubble Relay | Component that aggregates/serves Hubble flow data in supported deployments | It is required for every basic Cilium flow inspection |

### L3, L4 and L7 policy

- **L3:** addresses or endpoint identities, such as which Pods/namespaces can communicate.
- **L4:** transport protocol and port, such as TCP/8081.
- **L7:** supported application-protocol attributes, for example HTTP methods/paths, when the policy and proxy/redirection prerequisites are satisfied.

Native Kubernetes `NetworkPolicy` primarily expresses Pod/namespace/IP peers and ports/protocols. Cilium's policy CRDs can add Cilium-specific identity, L7 and DNS/FQDN capabilities. Exact schema and policy composition must be checked against the installed Cilium release. Do not assume policy order or allow/deny interaction rules from another firewall product.

### Hubble flow interpretation — worked example 1

The following record is **illustrative—not captured from a live cluster**:

```text
2026-10-28T10:15:00Z flow:
  source: namespace=ml-platform, pod=model-api-abc
  destination: namespace=ml-platform, pod=feature-service-def, port=8081/TCP
  verdict: DROPPED
  direction: EGRESS
  reason: policy-denied
```

Line-by-line interpretation:

- `source` identifies the endpoint as represented by the flow source; verify labels and identity in the cluster rather than trusting a display name alone.
- `destination` shows the destination endpoint/port associated with the observed flow. Confirm the Service's current EndpointSlices and the actual selected Pod.
- `verdict: DROPPED` means this event reports a drop. It does not, by itself, prove which policy object is wrong or whether the application's intended request should be allowed.
- `direction: EGRESS` is the reported direction relative to the endpoint/flow event. Direction labels can be tool/version/context-sensitive; correlate with the exact command and source endpoint.
- `reason: policy-denied` is an illustrative reason string only. Do not expect that exact field/value from every Cilium version or output format.

Operator next steps: confirm the source and destination Pod labels, list applicable NetworkPolicy/CNP/CCNP resources, inspect Cilium agent/endpoint status, check Hubble for both directions, and run one bounded request from a known test Pod. A policy drop can coexist with an application bug; the flow record is one piece of evidence.

### What Hubble can and cannot prove

Hubble can help show flow direction, endpoint context, verdicts/drops, DNS-related observations and L7 events when the relevant features and telemetry are enabled. It can help answer “what traffic was observed and what verdict did the datapath report?” It cannot automatically prove that all traffic was captured, that an HTTP request had the intended business effect, that no bypass path exists, or that an observed DNS name is the only way to reach a remote service. Absence of a flow can mean no traffic, missing visibility, wrong scope, dropped telemetry, or an unsupported path. Verify the version's CLI syntax and configured visibility before interpreting silence.

### Kernel and platform requirements

The official Cilium 1.20.4 system requirements page lists Linux kernel 5.10 or later as the general recommendation, with certain supported distributions having documented equivalent exceptions, and lists specific kernel configuration options and feature-specific requirements. That is not a blanket statement that every Cilium feature works on every kernel at that version. Cilium feature requirements vary by mode and release.

On WSL2, `uname -r` reports the Linux kernel used by the WSL distribution, but Docker may run through a different daemon/runtime context and kind nodes are containers using the host kernel. Confirm the actual runtime and kernel constraints for the intended deployment. A successful local installation does not guarantee a production node image has the same BPF features, netfilter modules, cgroup configuration or support contract.

## 9.4 Guided walkthrough with worked examples

### Example A — Least-privilege model API to feature service

Assume the `ml-platform` namespace has `model-api` Pods labelled `app: model-api` and `feature-service` Pods labelled `app: feature-service`. The feature service listens on TCP/8081. A policy selecting the model API and allowing egress only to the feature service is a useful starting concept, but remember that destination ingress policy, source egress policy, DNS, and cross-namespace database access may all be separate concerns.

The following Cilium policy is a **schema-gated template** based on the Cilium `CiliumNetworkPolicy` API group/version shown in official Cilium policy examples. Verify the installed CRD and every field with the selected release before applying. It is deliberately scoped to one source workload and one destination port; it does not create the Services or ensure the destination is healthy.

```yaml
# File: manifests/unit-09/model-api-to-feature-service.template.yaml
# [VERIFY] Check installed CiliumNetworkPolicy CRD schema and Cilium release first.
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: model-api-to-feature-service
  namespace: ml-platform
spec:
  endpointSelector:
    matchLabels:
      app: model-api
  egress:
    - toEndpoints:
        - matchLabels:
            k8s:io.kubernetes.pod.namespace: ml-platform
            app: feature-service
      toPorts:
        - ports:
            - port: "8081"
              protocol: TCP
```

Interpretation:

- `apiVersion` and `kind` select the Cilium-specific API; `cilium.io/v2` must be served by the installed CRD.
- `metadata.namespace` scopes this namespaced CNP to `ml-platform`.
- `endpointSelector` selects source endpoints labelled `app: model-api`.
- `egress` describes outgoing permissions for those selected endpoints under the applicable policy semantics.
- `toEndpoints` selects destination endpoints by Kubernetes namespace label and application label; verify actual labels.
- `toPorts` limits the allowed destination port/protocol to TCP/8081.
- This policy does **not** automatically allow DNS, Postgres, Redis, telemetry, ingress, or any other dependency. Under an egress-isolated policy model, required flows must be added intentionally.

Before applying, record current policies and test baseline connectivity. Validate the CRD exists with `kubectl get crd ciliumnetworkpolicies.cilium.io`; inspect the live schema using `kubectl explain ciliumnetworkpolicy.spec --api-version=cilium.io/v2` only after the CRD is installed. A server-side dry-run validates against the live API server, but cannot prove the expected packet behavior. Do not apply this template to a cluster that is not confirmed disposable.

### Example B — DNS/FQDN-aware egress to a controlled test destination

Cilium documents DNS-based policies using `toFQDNs` and DNS proxy rules. FQDN policy has important dependencies: the relevant DNS queries must be observed by the configured policy path, the destination must resolve as expected, and the feature must be supported by the installed release/configuration. It is not a universal domain firewall and should not be used to permit arbitrary internet access by assumption.

The following is a **review-only template**. It uses the reserved `.test` domain for a controlled lab name and does not instruct the learner to contact a public endpoint. The name must be served by a local test DNS setup or local mock; if that is not available, do not apply it as an active experiment.

```yaml
# File: manifests/unit-09/etl-fqdn-egress.template.yaml
# [VERIFY] Confirm Cilium DNS proxy/FQDN policy support and CRD schema for selected release.
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: etl-worker-controlled-fqdn
  namespace: ml-platform
spec:
  endpointSelector:
    matchLabels:
      app: etl-worker
  egress:
    - toEndpoints:
        - matchLabels:
            k8s:io.kubernetes.pod.namespace: kube-system
            k8s:k8s-app: kube-dns
      toPorts:
        - ports:
            - port: "53"
              protocol: ANY
          rules:
            dns:
              - matchName: "api.mock.test"
    - toFQDNs:
        - matchName: "api.mock.test"
      toPorts:
        - ports:
            - port: "8080"
              protocol: TCP
```

**Preconditions to verify before applying:**

1. The installed Cilium release supports the shown FQDN/DNS policy schema.
2. The cluster's DNS Pods actually match the selectors; labels differ by distribution.
3. The test name resolves through the cluster's configured DNS path to a controlled local destination.
4. The local mock service is not publicly exposed and contains no real credentials/data.
5. The ETL worker is expected to call only this destination for this experiment.
6. Existing egress policy is captured and a rollback procedure is ready.

**Expected policy intent:** allow the selected ETL workload to query the cluster DNS path for the test name and reach a matching destination on TCP/8080, subject to the release's documented FQDN policy semantics. This does not prove all external egress is denied, does not cover every alternate resolver/protocol path, and does not create the DNS record or mock server. The `protocol: ANY` and DNS rule structure are version/schema-sensitive; if the installed CRD rejects them, stop and consult the exact official schema instead of guessing a replacement.

### Example C — Cluster-wide policy and blast radius

`CiliumClusterwideNetworkPolicy` is a Cilium-specific cluster-scoped resource. It can affect endpoints across namespaces, so a selector or rule mistake can create a large blast radius. Start with namespaced policy unless a cluster-wide control is genuinely required, and require a review, a representative test, an explicit owner, and a rollback plan for every CCNP change.

```yaml
# File: manifests/unit-09/clusterwide-policy-review-only.yaml
# REVIEW ONLY — do not apply as part of this lesson.
# [VERIFY] Confirm the current CiliumClusterwideNetworkPolicy schema and selector semantics.
apiVersion: cilium.io/v2
kind: CiliumClusterwideNetworkPolicy
metadata:
  name: example-clusterwide-policy-review-only
spec:
  endpointSelector:
    matchLabels:
      security.example.com/managed: "true"
  description: "Illustrative selector for review; no ingress/egress rules are specified."
```

This intentionally incomplete policy-shaped example is for schema/selector review only and is not an operational policy. Do not apply it as a “test.” The key learning is to identify the scope and verify the selectors across all namespaces. For an actual CCNP, use the selected release's official examples and include fully reviewed ingress/egress semantics, a change owner, pre/post tests, and rollback.

### kube-proxy replacement is an option, not a default assumption

Cilium can provide Kubernetes service load-balancing through eBPF in supported configurations, potentially replacing kube-proxy. The choice depends on the Cilium release, kernel/platform, routing mode, cluster bootstrapping and required features. Do not infer that it is enabled merely because Cilium is installed. Check the active Cilium configuration and official kube-proxy replacement guide. A service-path issue should be debugged against the actual configuration, not against the architecture you expected to install.

### Transparent encryption versus mTLS

Cilium documents network-layer transparent encryption options including WireGuard and IPsec for supported traffic paths. Encryption can protect packets between nodes/endpoints under the selected mode, but it is not equivalent to TLS/mTLS:
- WireGuard/IPsec protect network traffic at a lower layer and do not provide HTTP-level application authorization.
- TLS/mTLS can authenticate a server and, with mTLS, a client/workload at the TLS endpoint.
- Mesh identity/policy and application authorization answer different questions from network reachability.
- NetworkPolicy remains a separate access-control layer.
- Not every path is necessarily encrypted in every mode. Cilium's docs describe exceptions and mode-dependent behavior, so verify which source/destination pairs and node paths are protected.

Do not enable encryption in this introductory lab. Treat it as an architecture review unless a separate, verified exercise has the required kernel support and test plan.

## 9.5 Hands-on lab: setup, execution and evidence

### Lab safety contract

- Use a newly created, disposable `kind` cluster named `m04-cilium-lab`; never replace the CNI in a shared or valuable cluster.
- Confirm the actual OS, kernel, Docker/runtime, kind, Kubernetes version and resource availability.
- The laptop baseline is approximately 4 CPU cores, 8 GB RAM and 30 GB disk. These are planning assumptions, not a guarantee that every optional component fits.
- Do not run Cilium, a service mesh, Cilium/Hubble extras and a full Prometheus/Grafana stack together on this budget.
- No paid cloud, public endpoint, production secret, real user data, external scanning or uncontrolled traffic.
- Every mutating sequence must check the expected context and explicitly confirm the cluster is disposable.
- Commands below were authored but not executed. Version placeholders must be replaced only after checking official compatibility.

### Path A — Install Cilium as the CNI only if verified

**Goal:** create a new cluster with the default CNI disabled, install a selected compatible Cilium release, verify status/connectivity, and optionally inspect a local flow/policy.  
**Time:** 2–4 hours, depending on installation and image downloads.  
**Resource plan:** one small kind cluster, Cilium agent/operator, a tiny sample workload and only the minimum visibility features needed.  
**Preconditions:** official Cilium kind procedure and system requirements reviewed; the kernel/runtime supports the selected feature set; no overlapping Pod/Service subnet; enough disk and memory; all tools installed from their official sources.

#### Step 1 — Read-only preflight

```bash
# File: commands/unit-09-preflight.sh
set -euo pipefail

printf '%s\n' 'OS:'
uname -a
printf '%s\n' 'Kernel:'
uname -r
printf '%s\n' 'Architecture:'
uname -m

for cmd in docker kind kubectl helm; do
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    printf 'Missing required command: %s\n' "${cmd}" >&2
    exit 10
  fi
done

docker version
kind version
kubectl version --client
helm version
printf '%s\n' 'Current context (do not mutate any cluster yet):'
kubectl config current-context || true
printf '%s\n' 'Existing kind clusters:'
kind get clusters
```

Interpretation: the output records tool/runtime versions and current context. It does not prove kernel feature availability, Cilium compatibility, or sufficient resources. On WSL2, confirm which Docker daemon is actually serving kind. If the environment is unclear or incompatible, use Path B and leave the cluster untouched.

#### Step 2 — Verify official compatibility and choose a version

Consult:
- Cilium's **Installation Using Kind** page for the chosen stable release.
- Cilium **System Requirements** and feature-specific kernel requirements.
- The selected Cilium release's Kubernetes compatibility information.
- The matching Cilium CLI installation instructions and release notes.
- Official kind configuration docs.

Do not use a floating `latest` version for a reproducible lab. The documentation consulted included Cilium 1.20.4 stable pages; this is not a claim that 1.20.4 is the right version for every Kubernetes version or remains the preferred release at execution time. Set `<CILIUM_VERSION>` only after compatibility is confirmed. If no compatible combination can be established, stop and use Path B.

#### Step 3 — Create a new cluster with default CNI disabled

The official Cilium kind guide uses a kind configuration with `networking.disableDefaultCNI: true`. The cluster's Pods may remain NotReady until Cilium is installed; that is expected for this setup.

```yaml
# File: manifests/unit-09/kind-cilium-config.yaml
# [VERIFY] Confirm against official kind documentation and selected Cilium release.
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: m04-cilium-lab
nodes:
  - role: control-plane
  - role: worker
networking:
  disableDefaultCNI: true
```

**⚠ DESTRUCTIVE / CLUSTER CREATION:** Creating this named cluster is a mutation and downloads/creates local containers. First confirm that no existing cluster uses this name and that this is an isolated lab.

```bash
# File: commands/create-cilium-kind-lab.sh
set -euo pipefail

CLUSTER_NAME="m04-cilium-lab"
if kind get clusters | grep -Fxq "${CLUSTER_NAME}"; then
  echo "Refusing: kind cluster ${CLUSTER_NAME} already exists; inspect it manually." >&2
  exit 20
fi

echo "About to create a NEW disposable cluster: ${CLUSTER_NAME}"
read -r -p 'Type CREATE-DISPOSABLE-CILIUM-LAB to continue: ' CONFIRM
if [[ "${CONFIRM}" != "CREATE-DISPOSABLE-CILIUM-LAB" ]]; then
  echo "Cancelled." >&2
  exit 21
fi

kind create cluster --name "${CLUSTER_NAME}" --config manifests/unit-09/kind-cilium-config.yaml
EXPECTED_CONTEXT="kind-${CLUSTER_NAME}"
ACTUAL_CONTEXT="$(kubectl config current-context)"
if [[ "${ACTUAL_CONTEXT}" != "${EXPECTED_CONTEXT}" ]]; then
  echo "Context mismatch: expected ${EXPECTED_CONTEXT}, got ${ACTUAL_CONTEXT}" >&2
  exit 22
fi
kubectl --context "${EXPECTED_CONTEXT}" cluster-info
kubectl --context "${EXPECTED_CONTEXT}" get nodes
```

The context check prevents the following commands from silently proceeding under a different context, but it cannot prove the cluster contains no valuable workloads. Inspect before continuing.

#### Step 4 — Install the matching Cilium release

**[VERIFY]** The official kind guide documents using the Cilium CLI to install Cilium into the new cluster and waiting for status/connectivity checks. Verify exact Cilium CLI version compatibility and install syntax for the chosen release. Do not copy a command from a development (`latest`) page into a pinned stable environment without review.

After the CLI is installed from the official instructions, the documented command family includes `cilium install --version <version>`. Verify flags with `cilium install --help` for the installed CLI. Run only when the current context is exactly `kind-m04-cilium-lab` and the cluster was created by the guarded Step 3.

```bash
# File: commands/install-cilium-lab.sh
set -euo pipefail
EXPECTED_CONTEXT="kind-m04-cilium-lab"
ACTUAL_CONTEXT="$(kubectl config current-context)"
if [[ "${ACTUAL_CONTEXT}" != "${EXPECTED_CONTEXT}" ]]; then
  printf 'Refusing install: expected %s, got %s\n' "${EXPECTED_CONTEXT}" "${ACTUAL_CONTEXT}" >&2
  exit 30
fi
if [[ "${CONFIRM_DISPOSABLE_CLUSTER:-}" != "yes" ]]; then
  echo "Set CONFIRM_DISPOSABLE_CLUSTER=yes only after confirming this is the disposable lab." >&2
  exit 31
fi
: "${CILIUM_VERSION:?Set CILIUM_VERSION only after checking official compatibility}"
if ! command -v cilium >/dev/null 2>&1; then
  echo "Cilium CLI missing; install using official instructions first." >&2
  exit 32
fi
cilium version
cilium install --version "${CILIUM_VERSION}"
cilium status --wait
```

The exact status flags must be confirmed with the installed CLI help and the selected official release. If the CLI rejects a flag or reports incompatibility, stop and consult that release's docs. Do not “fix” installation by disabling security controls or deleting cluster CRDs.

#### Step 5 — Connectivity and flow visibility

The Cilium CLI provides a documented connectivity-test workflow for supported releases. Confirm exact command and options with `cilium connectivity test --help` and the selected release guide before execution. The test creates workloads and network traffic, so run it only in the disposable cluster and capture the version and start/end time.

Hubble is optional. Enable it only if supported by the chosen Cilium release and the laptop can afford the extra components. Verify `cilium hubble --help`, the official Hubble installation page and the required relay/UI configuration. Use `hubble observe --help` before selecting namespace/direction/verdict filters. Similarly, confirm the exact current syntax for `cilium monitor` and `cilium bpf` from the installed CLI/agent documentation; command names and subcommands are version-sensitive.

Do not assume that installing Cilium automatically installs Hubble Relay or a UI. If Hubble is not installed, the core lab can still demonstrate CNI setup and connectivity testing without flow UI.

#### Step 6 — Policy experiment

Deploy or reuse a minimal local sample with `model-api`, `feature-service`, and a test client in `ml-platform`. Before any policy apply:
1. confirm context and disposable-cluster confirmation;
2. verify the CiliumNetworkPolicy CRD and schema;
3. record baseline connectivity and existing policies;
4. apply a narrowly scoped policy from Section 9.4 only after adapting selectors/ports to the actual sample;
5. test an allowed model-api → feature-service request and a disallowed test-client → feature-service request if the test setup and policy intent support that distinction;
6. collect policy resource, endpoint labels, Hubble/CLI evidence if enabled, and app response;
7. restore baseline policy and verify expected connectivity.

Do not use a broad cluster-wide policy for this introductory test. If the policy does not behave as expected, remove only the exact test resource after checking the current context and confirming the saved baseline.

#### Step 7 — Cleanup

**⚠ DESTRUCTIVE:** deleting the named kind cluster removes all Pods, Services, policy resources and local cluster state inside it. Do not run this against any cluster other than the explicitly named disposable cluster.

```bash
# File: commands/delete-cilium-kind-lab.sh
set -euo pipefail
EXPECTED_CONTEXT="kind-m04-cilium-lab"
ACTUAL_CONTEXT="$(kubectl config current-context)"
if [[ "${ACTUAL_CONTEXT}" != "${EXPECTED_CONTEXT}" ]]; then
  printf 'Refusing deletion: expected %s, got %s\n' "${EXPECTED_CONTEXT}" "${ACTUAL_CONTEXT}" >&2
  exit 40
fi
if [[ "${CONFIRM_DISPOSABLE_CLUSTER:-}" != "yes" ]]; then
  echo "Set CONFIRM_DISPOSABLE_CLUSTER=yes only after verifying this cluster is disposable." >&2
  exit 41
fi
kind get clusters | grep -Fxq "m04-cilium-lab" || {
  echo "Named kind cluster not found; nothing to delete." >&2
  exit 42
}
echo "⚠ DESTRUCTIVE: this removes the entire m04-cilium-lab cluster."
read -r -p 'Type DELETE-M04-CILIUM-LAB to continue: ' CONFIRM
if [[ "${CONFIRM}" != "DELETE-M04-CILIUM-LAB" ]]; then
  echo "Cancelled." >&2
  exit 43
fi
kind delete cluster --name m04-cilium-lab
if kind get clusters | grep -Fxq "m04-cilium-lab"; then
  echo "Cluster still appears in kind cluster list." >&2
  exit 44
fi
echo "Cluster deletion verified from kind cluster list."
```

After cleanup, confirm the cluster no longer appears in `kind get clusters`; also verify no lab containers remain from that cluster. Do not manually delete Cilium CRDs from another cluster as a cleanup shortcut.

### Path B — Cilium cannot safely be installed: read-only evidence analysis

Use this path if the kernel/runtime is incompatible, resource limits are tight, versions cannot be pinned, or the learner does not want to create a new cluster. It makes **no live Cilium behavior reproduced locally** claim.

The following samples are **illustrative—not captured from a live cluster**.

**Illustrative status summary:**

```text
Cilium: OK
Operator: OK
Hubble: disabled
KubeProxyReplacement: partial
```

Interpretation: treat each line as a fictional summary field. In a real environment, confirm exact output fields with the installed CLI version. “OK” would indicate a reported component status, not that every flow works. “Hubble: disabled” means this fictional sample does not provide Hubble evidence. “KubeProxyReplacement: partial” is a placeholder, not a universal Cilium status string.

**Illustrative Hubble-style flow:**

```text
FORWARDED  ml-platform/model-api -> ml-platform/feature-service:8081 TCP
DROPPED    ml-platform/etl-worker -> mock-external:8080 TCP  (policy denied)
```

- The first line suggests an observed flow reported as forwarded to the feature service. Confirm labels, port, and whether a response was observed.
- The second line suggests an observed drop associated with a policy decision. It does not establish that the FQDN policy is correct or that DNS resolution succeeded.
- Neither line proves application-level success, correct business output, or complete observation of all traffic.
- The displayed syntax is illustrative; do not expect this exact format from `hubble observe`.

**Read-only review exercise:**

1. Identify source, destination, protocol/port, verdict and the likely policy direction.
2. List at least three competing explanations for a missing expected flow: no request was sent, the wrong namespace/filter was used, or telemetry was not enabled/available.
3. Inspect the policy template from Section 9.4 and mark every field that requires installed-CRD verification.
4. Explain what additional live evidence would be needed: actual Cilium status, endpoint labels/identity, policy resource and status, DNS resolution path, Hubble/agent logs, and a controlled request.
5. State the boundary: this is a guided analysis of sample output, not a Cilium install or enforcement test.

## 9.6 Validation, expected results and interpretation

### Validation ladder

Use evidence in increasing order of operational cost:

1. **Static review:** manifest path, namespace, selectors, port/protocol and API group/version.
2. **Schema validation:** CRD exists; use `kubectl explain` and server-side dry-run where applicable.
3. **Control-plane state:** selected CLI status, agent/operator health, CRD resources.
4. **Endpoint state:** Pod readiness, labels, identities and endpoints.
5. **Flow evidence:** Hubble or documented agent/CLI evidence, when available.
6. **Application evidence:** bounded request succeeds/fails as intended and app logs correlate.
7. **Recovery evidence:** remove test policy/fault, repeat request, verify baseline.

A policy object existing is not proof of enforcement. A Hubble flow is not proof that the application returned a valid prediction. A successful HTTP request is not proof that all disallowed paths are blocked.

### Expected outcomes (not live results)

| Check | Expected behavior | What it establishes | What it does not establish |
|---|---|---|---|
| New cluster starts with default CNI disabled | Nodes may remain NotReady before Cilium is installed | Cluster creation followed the documented CNI bootstrap pattern | Cilium is installed or compatible |
| Cilium status/readiness | Selected release reports components healthy | Some control-plane/agent health checks pass | Every service path or policy works |
| Connectivity test | Documented test workloads complete their test cases | Tested paths behave as the test asserts | Production scale or all app paths are healthy |
| Allowed model-api → feature-service | Request succeeds with expected response | The tested path is allowed and app responded | No other caller can reach feature-service |
| Denied test-client → feature-service | Request is denied under the intended test policy | The tested disallowed path is blocked, if denial is attributed correctly | Every bypass path is blocked |
| Hubble shows forwarded flow | A flow event was observed and reported as forwarded | Flow telemetry saw that event/verdict | Business transaction succeeded |
| Hubble shows drop | A flow event was reported as dropped | The event is evidence of a drop at the observed point | Root cause without policy/context inspection |
| Post-cleanup request | Known-good request works and test resources are absent | Lab rollback was effective for checked resources | No unrelated residue exists outside inspected scope |

### Blank lab worksheet

| Field | Learner's measured value |
|---|---|
| Date/time and operator |  |
| OS / WSL2 or native Linux |  |
| Kernel version and relevant support evidence |  |
| Docker/runtime and kind version |  |
| Kubernetes server version |  |
| Cilium CLI version |  |
| Cilium agent/operator version |  |
| CNI mode / kube-proxy replacement configuration |  |
| Hubble enabled? Relay/UI installed? |  |
| Namespace and workload labels |  |
| Baseline allowed request result |  |
| Baseline denied request result |  |
| Policy resource/API version |  |
| Hubble/CLI evidence file and redactions |  |
| Post-policy allowed result |  |
| Post-policy denied result |  |
| Cleanup and post-cleanup verification |  |
| Unresolved `[VERIFY]` items |  |

## 9.7 Security, reliability and failure modes

### Operational failure modes

| Failure mode | Possible symptom | Evidence to collect first | Safe response |
|---|---|---|---|
| Cilium agent crash/restarts | Node-local connectivity/policy symptoms | Pod status/events, agent logs, node conditions, version/config | Scope affected nodes; follow official recovery guidance; avoid restarting every node |
| Operator unavailable | Some cluster-level coordination or identity/IPAM operations fail | Operator status/logs, related resource conditions, agent state | Restore the operator according to release docs; verify scope and resource pressure |
| Identity allocation/exhaustion | New endpoints lack expected identity or policy state | Endpoint/identity status and allocation metrics/logs, label churn | Check documented allocation mode/capacity; reduce churn and escalate before broad restarts |
| Policy-map/resource limits | Drops or failure to install/update policy | Agent logs, policy/endpoint status, kernel/resource evidence | Reduce policy complexity safely, check documented limits, preserve evidence |
| Stale/unexpected policy | Allowed path denied or prohibited path allowed | All matching native/Cilium policies, labels, selector overlap, current resource state | Narrow change, run positive/negative tests, restore known-good policy |
| Control-plane/datapath divergence | API object exists but behavior disagrees | Desired policy, agent convergence/status, flow evidence, endpoint identity | Wait/diagnose documented reconciliation; do not assume apply success means datapath convergence |
| DNS/FQDN policy failure | Name resolves but destination blocked, or expected name is absent | DNS query path, policy, resolved IP, observed flow, DNS proxy support | Verify supported resolver/policy path; test with controlled mock; do not open all egress |
| Upgrade incompatibility | Nodes/policies behave differently after update | Versions, release notes, kernel, config, CRDs and agent logs | Stop rollout, compare supported skew, use documented rollback/upgrade plan |
| Privileged-agent compromise/misuse | Potential broad node/network impact | RBAC, image provenance, admission/audit logs, unexpected agent changes | Isolate through approved incident process; preserve evidence; escalate to security/platform owners |
| Performance regression | Throughput/latency/drops change | Same workload/config, kernel/CPU, policy, packet size, repeated trials | Reproduce controlled baseline; do not declare a winner from one run |

### Privileged-component threat model

Cilium agents run with elevated privileges needed to manage networking and kernel datapath state. Treat the agent image, its configuration, operator permissions and upgrade process as part of the cluster's trusted computing base. Controls include:
- pin approved images and versions; verify provenance/digests according to M12 supply-chain controls;
- restrict who can modify Cilium resources, Helm values and node-level configuration;
- review cluster-scoped policy changes and changes to service load balancing;
- use audit logs and change records;
- separate read-only diagnostics from write privileges;
- test upgrades and rollbacks in disposable/representative clusters;
- reduce blast radius with namespace-scoped policies and staged rollout when possible.

The kernel verifier constrains what an eBPF program can do, but it does not remove the risks of a privileged agent, malicious or incorrect configuration, kernel vulnerabilities, or a logically overbroad policy.

### Encryption is not identity authorization

Cilium WireGuard/IPsec can protect traffic on supported network paths. They do not automatically provide workload-level mTLS semantics or application permissions. If a feature service requires mutual workload authentication, use the appropriate mesh/application identity controls (Unit 7/8) and separately maintain network reachability policy. Do not remove NetworkPolicy because traffic is encrypted.

### Adjacent tools: different jobs

- **Falco:** runtime security detection based on supported system/event signals; not a replacement for Cilium's CNI or policy datapath.
- **Tetragon:** eBPF-based security observability and enforcement focused on process/kernel-level events and policies; not interchangeable with network flow visibility.
- **Pixie:** observability tooling aimed at application/network telemetry collection in supported environments; not a general-purpose CNI replacement.
- **Hubble:** Cilium network-flow observability tied to Cilium's datapath and enabled telemetry.

These tools overlap in some visibility scenarios but have different data sources, policies, operational overhead and threat models. M11 covers the wider observability platform; M12 covers supply-chain/security tooling.

## 9.8 Observability and performance methodology

### Choose the right evidence source

| Question | Preferred evidence | Limitation |
|---|---|---|
| Did Kubernetes create the Pod/Service/EndpointSlice? | `kubectl get/describe`, events and endpoint resources | Does not prove packets reached the app |
| Is Cilium installed/healthy? | Version-matched Cilium CLI status and agent/operator logs | Does not prove all datapath paths work |
| Was a flow forwarded or dropped? | Hubble or version-matched Cilium flow diagnostics | Visibility depends on feature/configuration and event scope |
| Did the application succeed? | HTTP/gRPC response, application logs, business-level checks | Does not alone prove which policy/path permitted it |
| Did a kernel/datapath change alter behavior? | Kernel/config versions, Cilium diagnostics, controlled packet capture and repeated tests | Captures can observe different network namespaces and may miss offloaded/short-lived events |
| Is the issue a performance regression? | Repeated controlled baseline comparison, latency distributions, throughput, CPU/memory and drops | Local lab results do not predict production fleet performance |

### Reproducible performance experiment

Do not run a performance benchmark until basic correctness is established. A useful experiment asks a narrow question, such as: “Under this workload and policy, does the chosen Cilium configuration change request latency or CPU relative to the documented baseline?” It does not begin with an assumption that eBPF is faster.

Record the following before each run:

- kernel version/configuration and OS/runtime;
- Kubernetes, kind, Cilium CLI/agent/operator and relevant CRD versions;
- CNI/routing/tunnel mode and kube-proxy replacement setting;
- workload image/version, request payload size, concurrency and request rate;
- policy shape: no policy, simple L3/L4, and L7/FQDN only if safely supported;
- CPU/memory limits, node count, resource pressure and background load;
- warm-up period, measured duration, trial number and test tool version;
- request rate/throughput, p50/p95/p99 latency where sample size supports it, errors/drops and CPU/memory;
- exact commands, timestamps, configuration and any changes between trials.

Run multiple trials with the same workload and keep baseline and candidate conditions as alike as possible. Avoid changing the CNI and workload at the same time. Report distributions and variance, not just one average. If packet sizes, connection reuse, DNS caching, policy complexity or CPU throttling differ, identify them as confounders.

| Trial | Configuration | Warm-up | Duration | Request size / concurrency | Throughput | p50 / p95 / p99 | Errors/drops | CPU / memory | Notes |
|---|---|---|---|---|---|---|---|---|---|
| Baseline 1 |  |  |  |  |  |  |  |  |  |
| Baseline 2 |  |  |  |  |  |  |  |  |  |
| Cilium 1 |  |  |  |  |  |  |  |  |  |
| Cilium 2 |  |  |  |  |  |  |  |  |  |

No benchmark results are provided here because no experiment was run. A local `kind` test cannot reproduce production NICs, multi-AZ traffic, real node density, hardware offloads, cloud load balancers or fleet-scale policy churn.

### Metrics and dashboards awareness

Cilium/Hubble can integrate with metrics and dashboards in supported deployments, and Prometheus/Grafana may be used to display selected signals. Exact metric names, labels, default enablement and dashboards are release/configuration-sensitive: verify the selected release's official metrics documentation and current scrape configuration. Do not install a full monitoring stack for this unit's core lab. M11 owns platform-wide metrics, logs, traces, alerting and dashboard design.

## 9.9 Troubleshooting decision tree

Start every incident by defining scope: one Pod, one node, one namespace, all endpoints, or cluster-wide. Gather read-only evidence before changing policy, restarting components or deleting resources.

### Decision tree: symptom to safe next action

```text
Traffic failure or unexpected behavior
  |
  +-- Is the Kubernetes object/endpoint present and ready?
  |      |
  |      +-- No -> inspect events, selectors, readiness and EndpointSlices
  |      |
  |      +-- Yes
  |           |
  |           +-- Is Cilium agent healthy on relevant nodes?
  |           |      |
  |           |      +-- No -> scope nodes; inspect agent logs/events/version
  |           |      |
  |           |      +-- Yes
  |           |           |
  |           |           +-- Does flow evidence show a drop?
  |           |           |      |
  |           |           |      +-- Yes -> inspect policy, identity, direction and port
  |           |           |      |
  |           |           |      +-- No/unknown -> verify telemetry scope; inspect routing/DNS/app
  |           |           |
  |           |           +-- Did the problem begin after an upgrade/config change?
  |           |                  |
  |           |                  +-- Yes -> compare versions/config/CRDs and stop rollout
  |           |                  +-- No -> test one bounded path and compare baseline
  |           |
  |           +-- Is application-level request valid and successful?
  |                  |
  |                  +-- No -> inspect app/dependency; network evidence is not the whole story
  |                  +-- Yes -> preserve evidence and continue scoped validation
```

### Symptom-specific procedures

| Symptom | Read-only evidence first | Likely causes to test | Safe mitigation / stop condition |
|---|---|---|---|
| Pods not Ready after CNI installation | Node status, Pod events, Cilium agent/operator status, selected release docs | CNI bootstrap incomplete, image pull issue, incompatible kernel/config, subnet conflict | Stop further mutation; verify version and prerequisites. Do not install a second CNI over it |
| `cilium status` unhealthy/not ready | CLI/server version, agent/operator Pods/events/logs, node health | Version mismatch, agent crash, control-plane/API issue, unsupported config | Follow matching release troubleshooting; preserve logs; escalate before restarting all agents |
| Pod-to-Pod or Pod-to-Service fails | Endpoints/EndpointSlices, labels, service port/targetPort, route/config, flow evidence | Selector mismatch, policy, service datapath/config, routing/tunnel or app listener | Test one source/destination/port; don't flush rules or disable all policy |
| Traffic denied unexpectedly | Applicable Kubernetes NP/CNP/CCNP, endpoint labels/identity, Hubble event | Wrong selector, missing DNS/egress path, policy scope, stale convergence | Restore only a reviewed prior policy in disposable test; retain narrow controls |
| Hubble shows drops or no expected flows | Hubble status/filters, source/destination scope, agent status, actual request | Policy drop, wrong namespace/filter, missing visibility, no request, telemetry unavailable | Verify the observation path before inferring root cause |
| DNS/FQDN policy blocks destination | Pod resolver config, DNS flow/query, policy schema, resolved address, destination flow | DNS not observed, selector mismatch, name mismatch, alternate resolver, unsupported policy path | Stop external traffic; reproduce with a controlled local DNS/mock; don't allow all egress |
| Agent unavailable/restarting | Node and Pod events, previous logs, resource pressure, versions | Crash, image/runtime problem, kernel feature/config mismatch, memory pressure | Scope affected node(s); follow release runbook; escalate if multiple nodes affected |
| Identity allocation/map limits suspected | Agent/operator logs, identity/endpoint status, policy complexity and documented limits | Label churn, allocation mode, map/resource pressure | Confirm supported limit and evidence; do not invent capacity or clear maps blindly |
| Upgrade changed behavior | Before/after version/config/CRD diff, release notes, policy and flow evidence | Compatibility/skew, changed defaults/API, datapath/config change | Stop rollout; use documented rollback path; do not downgrade blindly across state/schema changes |
| Performance differs from baseline | Kernel/config capture, workload parity, repeated trials, latency/drop/CPU evidence | Different test conditions, policy complexity, CPU throttling, path/config changes | Repeat controlled trials; no performance claim from a single run |

### Incident runbook: alert → triage → mitigation → validation → escalation

1. **Alert and scope:** record time, symptom, affected namespace/nodes/endpoints, and recent changes. Establish whether the issue is localized or cluster-wide.
2. **Collect evidence:** capture Cilium/CLI versions, status, agent/operator events and logs, relevant policy objects, endpoint labels, Kubernetes Service/EndpointSlice state, and Hubble flow evidence if available. Redact secrets and sensitive payloads.
3. **Form hypotheses:** list at least two plausible causes and the evidence that would distinguish them. Avoid “restart everything” as a diagnosis.
4. **Mitigate safely:** stop a rollout or test load; restore a previously reviewed policy/configuration only after checking the current context; do not disable all policy or delete CRDs.
5. **Validate:** run a bounded allowed request and a negative test; confirm the policy result, application response and telemetry.
6. **Escalate:** involve the platform/networking owner when agent/control-plane failures affect multiple nodes, an upgrade threatens cluster connectivity, identity/policy state cannot converge, or safe rollback is unclear.
7. **Follow up:** preserve a sanitized timeline and add a regression test/change guard.

## 9.10 Production operations and runbooks

### CNI adoption/migration strategy

Changing the CNI is a cluster-level risk. Depending on the source CNI, managed Kubernetes restrictions and the destination configuration, safe migration may require a vendor-supported procedure or cluster recreation. Do not treat “install Cilium” as a universal in-place replacement recipe.

1. **Inventory:** current CNI/version, Kubernetes distribution, kernel/OS support, kube-proxy mode, IPAM, Pod/service CIDRs, NetworkPolicy resources, ingress/load-balancer paths, node pool shapes and observability dependencies.
2. **Compatibility:** verify the exact Cilium release against Kubernetes, kernel, distribution and runtime; review kube-proxy replacement, encryption, L7/FQDN, IPAM and routing prerequisites separately.
3. **Policy inventory:** export and review native NetworkPolicy and vendor-specific policies; identify allow/deny semantics, selectors, DNS and egress dependencies.
4. **Plan the target:** use a fresh representative cluster first. Pin images/charts/CLI, capture values/configuration and document support boundaries.
5. **Test representative paths:** model API → feature service, feature service → Redis/Postgres, ETL → controlled mock, DNS, ingress and metrics scraping. Include both allowed and denied tests.
6. **Canary and observe:** use a representative non-production cluster or vendor-supported node/cluster migration method. Define success/stop criteria and owners before the change.
7. **Rollback:** write the rollback path before migration. CNI rollback may require recreating the cluster or restoring a supported configuration, not simply uninstalling a chart.
8. **Execute with change control:** scheduled window, backup/restore plan, escalation contacts, versioned manifests, monitoring and explicit abort criteria.
9. **Validate and close:** check node readiness, Pod networking, Services, DNS, policy, ingress, observability and app SLIs. Record the final version/config and remaining risks.

**Stop conditions:** compatibility not proven; IPAM/CIDR conflict; required policy feature unavailable; no supported rollback; node/Pod readiness remains unhealthy; representative allowed/denied tests fail; or observability needed to assess impact is unavailable.

### Version and upgrade governance

Maintain a compatibility matrix covering Kubernetes, Cilium agent/operator/CLI, kernel, relevant CRD schemas and optional features. Pin versions and chart/image digests according to organizational policy. Read release notes for removed/deprecated APIs, defaults, datapath changes and upgrade order. Test upgrades in a disposable cluster with policy and service-path tests before production. Do not combine a CNI migration, kernel upgrade, kube-proxy replacement change and broad policy rollout into one unobservable change.

### Runbook: agent unavailable or policy divergence

- Verify context, node and namespace scope.
- Inspect agent/operator status and recent events/logs using commands documented for the selected version.
- Compare desired policy/CRD state with endpoint labels and available flow evidence.
- Check node/kernel/runtime changes and resource pressure.
- Preserve sanitized diagnostic output before remediation.
- Follow official release guidance to restore a component or roll back a change; do not manually delete BPF maps, CRDs, or node networking state unless a documented procedure explicitly requires it.
- Validate one known-good request, one intended-deny request and DNS/telemetry paths.
- Escalate if several nodes are affected or rollback could isolate the cluster from its API server.

### Governance checklist

- [ ] Approved Cilium release, images/digests and upgrade owner.
- [ ] Kubernetes/kernel/platform compatibility evidence.
- [ ] Least-privilege RBAC for policy/config changes and read-only diagnostics.
- [ ] Review and approval for all cluster-wide policies.
- [ ] CNI migration/rollback runbook and change window.
- [ ] Audit logs for policy and configuration changes.
- [ ] Known-good test matrix and evidence retention/redaction procedure.
- [ ] Capacity plan for agents, maps, flow telemetry and optional Relay/UI.
- [ ] Defined escalation path for cluster-wide networking failures.

## 9.11 Design choices, trade-offs and alternatives

### Cilium vs Calico vs managed/default CNI

There is no universal winner. Choose against actual requirements and operating capacity.

| Criterion | Cilium | Calico | Managed/default CNI |
|---|---|---|---|
| Core approach | eBPF-based datapath and Kubernetes-aware networking/policy in supported configurations | Networking/policy platform with implementation options that vary by edition/configuration | Provider/distribution-integrated networking and support model |
| L3/L4 policy | Native Kubernetes policy plus Cilium-specific policy features | Native Kubernetes policy plus Calico-specific policy features depending on product/config | Native policy support varies by provider implementation |
| L7/FQDN visibility/control | Supported capabilities exist with specific proxy/kernel/config prerequisites; verify exact release | Features depend on Calico product/edition/configuration; verify current support | Often limited or provided through separate service products |
| Flow visibility | Hubble is integrated with Cilium datapath in supported setups | Calico flow visibility depends on product/configuration | Provider tooling varies |
| Kernel/platform dependency | Significant; feature-specific kernel requirements | Depends on selected datapath/features | Provider controls much of the supported node platform |
| Operational complexity | Datapath, identities, BPF maps, CRDs and optional features add learning/upgrade work | Depends on mode, product and policy/telemetry requirements | Lower direct CNI ownership, but provider constraints and reduced control may apply |
| Migration/support | Must follow Cilium-supported migration/cluster setup | Must follow Calico-supported migration/cluster setup | Managed-provider-supported procedures are authoritative |
| Portability | Cilium-specific CRDs and datapath config create some ecosystem coupling | Calico-specific CRDs/features create some ecosystem coupling | Provider-specific APIs and limits can create dependency |
| Best fit when | Team needs its supported policy/visibility/datapath capabilities and can operate them | Team's requirements match supported Calico capabilities and support model | Team prioritizes provider integration and a smaller self-managed networking surface |
| Cost model | Engineering time, node resources, support and optional telemetry components | Engineering time, node resources and edition/support costs | Provider charges/support costs plus feature limits |

Evaluate policy features, kernel/platform support, visibility, support model, operational capacity, portability and total cost. Do not decide from marketing claims or a single local benchmark.

### Capability awareness: Gateway API, service mesh, bandwidth and egress

Cilium has documentation for Gateway API/ingress integration, and it has capabilities adjacent to service mesh, bandwidth management and egress gateway. These features vary by release, configuration and maturity. This unit does not use them as its main lab.

- **Gateway API/ingress:** verify exact supported Gateway API versions, controller status and route features. Unit 3 owns ingress/Gateway API fundamentals.
- **Sidecarless/service-mesh capabilities:** Cilium's network datapath and optional L7 proxy capabilities are not automatically equivalent to Linkerd or Istio identity, retry, traffic shifting and authorization features. Unit 7/8 own service mesh behavior.
- **Bandwidth management:** kernel support and configuration are prerequisites; verify the feature and its impact on scheduling/queuing before enabling.
- **Egress gateway:** routing egress through selected nodes is not the same as guaranteeing all outbound traffic is allowed or encrypted. Verify exact mode, identity and failure behavior.
- **Prometheus/Grafana:** awareness only here; M11 owns metric pipelines, dashboards, alert rules and SLO implementation.

### When to use Cilium-specific policy

Use native Kubernetes NetworkPolicy where its portable L3/L4 model satisfies the requirement and portability is important. Use Cilium-specific policy only when the additional feature is needed, verified, supportable and tested. Document the vendor-specific dependency, the API version and rollback. Avoid gratuitous use of CCNP when a namespaced policy is sufficient.

## 9.12 Exercises and knowledge checks

### Exercises

1. Draw the request path from `model-api` to `feature-service`. Mark where the Kubernetes API, Cilium agent, eBPF datapath, NetworkPolicy and Hubble fit. Explain which parts are control plane versus data plane.
2. Review the model-api-to-feature-service CNP template. List its preconditions, the labels it depends on, and the flows it does not permit.
3. Review the FQDN policy template and identify the DNS proxy, local DNS record, destination mock, CRD schema and rollback requirements.
4. Interpret the illustrative Hubble drop from Section 9.3. List three hypotheses and the next evidence that would distinguish them.
5. Design a migration checklist for a team using a different CNI. State what could force cluster recreation and which conditions would stop the change.
6. Create a performance experiment worksheet with at least two baseline and two candidate trials. Do not fill values until tests are actually run.
7. Compare Cilium, Calico and managed/default CNI for a hypothetical team with limited on-call capacity but a requirement for DNS/FQDN-aware egress. Identify the evidence required before choosing.

### Knowledge-check questions and answer key

**1. Does the eBPF verifier prove a program is secure and correct?**  
**Answer:** No. It checks kernel-enforced program constraints before loading. It does not prove that the policy intent is correct, that configuration is least-privilege, or that a privileged agent is safe. **Tempting wrong answer:** “Verified means no security risk.”

**2. Is eBPF always faster than iptables?**  
**Answer:** No. Performance depends on workload, kernel, datapath mode, policy complexity, hardware, connection behavior and measurement method. **Tempting wrong answer:** “Newer kernel mechanism means lower latency in every case.”

**3. Does Cilium universally bypass iptables and conntrack?**  
**Answer:** No. Some paths/features use eBPF; other paths and features may use netfilter/iptables, conntrack or proxy redirection. Verify the actual configuration and path. **Tempting wrong answer:** “Installing Cilium removes every iptables rule.”

**4. What is the difference between CNI and service mesh?**  
**Answer:** CNI configures Pod networking; a service mesh adds workload-to-workload traffic features such as identity, policy/telemetry and, depending on implementation, retries or routing. They overlap in some policy/visibility concerns but are not interchangeable. **Tempting wrong answer:** “Cilium makes Linkerd/Istio unnecessary.”

**5. What can a Hubble `DROPPED` event prove?**  
**Answer:** It is evidence that an observed flow event was reported as dropped at the recorded point. It does not alone prove the full root cause or application-level impact. **Tempting wrong answer:** “The event always names the exact faulty policy.”

**6. Why must Cilium-as-CNI use a fresh disposable cluster for this lab?**  
**Answer:** CNI installation changes cluster networking and can affect every Pod. A fresh cluster avoids disrupting a shared/valuable environment and makes cleanup bounded. **Tempting wrong answer:** “Installing another CNI over the current one is a reversible package change.”

**7. What is the difference between native NetworkPolicy and CiliumNetworkPolicy?**  
**Answer:** Native NetworkPolicy is a Kubernetes API primarily for L3/L4 reachability. CNP is Cilium-specific and can provide additional capabilities such as identity-aware selectors and supported L7/FQDN policy. **Tempting wrong answer:** “Every CNI interprets CNP identically.”

**8. Does an FQDN policy perfectly restrict every way a workload can reach a domain?**  
**Answer:** No. Behavior depends on observed DNS queries, resolver path, policy implementation, protocols, address resolution and version-specific limitations. **Tempting wrong answer:** “A domain string guarantees all network paths to that domain are controlled.”

**9. Is WireGuard/IPsec encryption equivalent to mTLS?**  
**Answer:** No. Network-layer encryption protects supported traffic paths; mTLS authenticates peers at TLS endpoints. Neither alone replaces application authorization. **Tempting wrong answer:** “Encrypted packets mean the application caller is authorized.”

**10. Why is a CCNP more dangerous to roll out than a namespaced CNP?**  
**Answer:** Its scope can span namespaces and workloads across the cluster. Selector mistakes have a larger blast radius. **Tempting wrong answer:** “A cluster-wide resource is only a template until it is used by a Pod.”

**11. What should you do when `cilium status` is healthy but a request fails?**  
**Answer:** Check endpoints, labels, policy, identity, route/port, DNS, flow evidence and application logs. Status is a component health signal, not an end-to-end test. **Tempting wrong answer:** “Restart Cilium on every node.”

**12. How should you claim a performance improvement?**  
**Answer:** Compare repeatable, like-for-like runs with fixed workload, versions, packet size, concurrency, warm-up and resource conditions. Report percentiles, throughput, errors/drops and confounders. **Tempting wrong answer:** “One successful local run proves Cilium is faster in production.”

## 9.13 Summary and readiness gate

### Summary

eBPF provides a programmable kernel facility, with the verifier enforcing safety constraints on loaded programs. Cilium uses eBPF in its networking datapath and combines it with Kubernetes integration, identities, policy and optional Hubble flow visibility. These capabilities can improve the available policy/observability model for the right environment, but they introduce kernel/platform dependencies, privileged components, version coupling and operational complexity. Cilium-specific policy is not portable Kubernetes NetworkPolicy, network-layer encryption is not mTLS, and a Hubble flow is not an application-level success signal. The adoption decision must be based on documented support, a safe migration path, repeatable tests and operational ownership—not on a blanket performance claim.

### Measurable readiness gate

The learner is ready to move on when they can complete all of the following without guessing:

- [ ] Explain hook, program, map, verifier, CNI, datapath, agent, operator and Hubble in their own words.
- [ ] Explain at least two reasons a verified eBPF program/deployment can still be unsafe or incorrect.
- [ ] Trace one model-api → feature-service request and distinguish control-plane from datapath components.
- [ ] Identify the exact Cilium/Kubernetes/kernel compatibility evidence required for a lab.
- [ ] Interpret a forwarded and a dropped illustrative Hubble event without claiming more than the record proves.
- [ ] Review a CNP template and identify selectors, port, API/CRD prerequisite, allowed flow and missing dependencies.
- [ ] Explain the risks and limitations of DNS/FQDN-aware egress policy.
- [ ] Distinguish Cilium WireGuard/IPsec from TLS/mTLS and application authorization.
- [ ] Explain why CNI migration requires a rollback plan and may require cluster recreation.
- [ ] Produce a blank performance test plan with no fabricated values.
- [ ] Complete Path A safely **or** complete Path B and explicitly state that no live Cilium behavior was reproduced.
- [ ] Preserve sanitized evidence and verify cleanup of all lab resources.

A failed item means the learner should revisit that concept or repeat the relevant read-only exercise. Do not mark the lab complete solely because installation commands returned success.

## 9.14 References, source/claim register and audit

### Consulted official sources

1. **Cilium, “Installation Using Kind” (stable documentation identifying Cilium 1.20.4).** https://docs.cilium.io/en/stable/installation/kind/  
   Consulted for the kind-specific setup pattern, disabling default CNI and the general installation/validation workflow.
2. **Cilium, “System Requirements” (Cilium 1.20.4 documentation).** https://docs.cilium.io/en/stable/operations/system_requirements/  
   Consulted for general kernel requirements and feature-specific kernel/configuration dependencies.
3. **Cilium, “Overview of Network Policy” (Cilium 1.20.x stable documentation).** https://docs.cilium.io/en/stable/security/policy/  
   Consulted for supported policy resource families, including Kubernetes NetworkPolicy, CiliumNetworkPolicy and CiliumClusterwideNetworkPolicy.
4. **Cilium, “Locking Down External Access with DNS-Based Policies” (development/latest documentation).** https://docs.cilium.io/en/latest/security/dns/  
   Consulted for the documented `toFQDNs`/DNS policy concepts and example structure. Because this page is under `latest`, verify against the selected stable release before use.
5. **Cilium, “WireGuard Transparent Encryption” (development/latest documentation).** https://docs.cilium.io/en/latest/security/network/encryption-wireguard/  
   Consulted for conceptual behavior, configuration dependencies and limitations. Exact syntax must be checked against the selected stable release.
6. **Cilium, “Transparent Encryption” (development/latest documentation).** https://docs.cilium.io/en/latest/security/network/encryption/  
   Consulted for encryption modes and limitations; release/maturity status must be verified.
7. **Cilium Hubble documentation.** https://docs.cilium.io/en/stable/observability/hubble/  
   Consulted as the official entry point for Hubble flow visibility; exact CLI/output must be verified against the selected release.
8. **Available repository files:** `Roadmap(5).md`, `PROMPT-Kubernetes-Networking-Ingress-and-Service-Mesh(9).md`, Unit 1, Unit 5, Unit 7 and Unit 8. Consulted for roadmap order, M04 boundaries, `ml-platform` vocabulary, and service-mesh/network-policy distinctions.
9. **Uploaded Unit 9 prompt.** Used as the controlling requirement list for this lesson.

### Official references to verify before a real lab

- Cilium release notes and Kubernetes compatibility for the selected Cilium/CLI/Kubernetes combination.
- Exact current Cilium CLI installation and `cilium install`, `cilium status`, connectivity-test and Hubble command syntax.
- Official kind configuration schema for the selected kind version and node image.
- Exact CRD schema for `CiliumNetworkPolicy` and `CiliumClusterwideNetworkPolicy` in the selected release.
- Cilium's current identity, agent/operator architecture and kube-proxy replacement guide.
- Current Hubble flow field/CLI syntax, Hubble Relay/UI prerequisites and metrics configuration.
- Current DNS/FQDN policy requirements, DNS proxy behavior, selector labels and limits.
- Current WireGuard/IPsec feature maturity, kernel requirements and which traffic paths are encrypted.
- Cilium Gateway API/ingress, sidecarless service-mesh, bandwidth-manager and egress-gateway feature status.
- Kubernetes documentation for NetworkPolicy semantics, CNI integration, Services and EndpointSlices.
- Linux kernel documentation for eBPF programs, maps, verifier and supported hooks.
- Official Calico documentation and the learner's managed/default CNI support matrix before making a platform choice.
- The missing Unit 10 and project files if exact cross-module/capstone compatibility needs to be checked.

### Claim register

| Claim/topic | Source URL or file | Source type | Version/date checked | Confidence/status | Notes |
|---|---|---|---|---|---|
| Cilium kind installation uses kind config with default CNI disabled | Cilium Installation Using Kind | Official Cilium documentation | Stable page identifying 1.20.4; accessed 2026-10-28 | High — consulted | Exact CLI/version pair still needs selection |
| General Cilium kernel requirement and feature-specific dependencies | Cilium System Requirements | Official Cilium documentation | 1.20.4 page; accessed 2026-10-28 | High — consulted | Do not treat as universal support for all features |
| Cilium supports Kubernetes NetworkPolicy, CNP and CCNP resource families | Cilium Overview of Network Policy | Official Cilium documentation | Stable 1.20.x page; accessed 2026-10-28 | High — consulted | Policy semantics/schema must match installed CRDs |
| DNS/FQDN policy uses documented Cilium-specific constructs | Cilium DNS policy docs | Official, `latest` development documentation | Accessed 2026-10-28 | High for concept; `[VERIFY]` syntax | Check stable release schema and resolver path |
| WireGuard can encrypt supported Cilium-managed traffic paths | Cilium WireGuard docs | Official, `latest` development documentation | Accessed 2026-10-28 | High for concept; `[VERSION-SENSITIVE]` | Path coverage and requirements vary by configuration |
| Hubble provides network flow visibility for supported Cilium deployments | Cilium Hubble docs | Official Cilium documentation | Entry page accessed 2026-10-28 | High — concept | Exact fields/commands not runtime-verified |
| eBPF verifier does not prove policy intent or whole deployment security | Linux/eBPF engineering explanation | General technical reasoning | Not a runtime test | High — reasoned | Verifier enforces program constraints, not business correctness |
| Cilium is not universally faster | Measurement discipline and systems reasoning | General engineering principle | No benchmark performed | High — reasoned | Performance depends on actual path/workload/configuration |
| CNI migration is cluster-level risk and may require recreation/vendor procedure | M04 syllabus, Cilium installation guidance | Repository source + operational inference | Accessed 2026-10-28 | High — guidance | Exact migration depends on source CNI/distribution |
| CNP and FQDN templates in this lesson are schema-gated | Lesson authoring status | Authoring limitation | Not applied or validated | High — explicit limitation | Must inspect live CRDs and perform dry-run before use |
| Cilium status/flow samples are illustrative | Lesson text | Authored example | No live output captured | High — explicit limitation | Not a claim about literal CLI formatting |
| Performance results | No source/result | Not applicable | Not run | Not claimed | Worksheet intentionally blank |
| Unit 9 aligns with Unit 10/capstone | Roadmap order and available sibling lessons | Partial repository evidence | Unit 10/project files unavailable separately | Partial — source limitation | Confirm when those files are available |

### Ten-pass quality audit

This is an internal authoring audit, not independent external validation.

| Pass | Result | Checks performed | Defects/corrections | Unresolved risks |
|---|---|---|---|---|
| 1. Roadmap fidelity | PASS WITH LIMITATIONS | Compared available roadmap, syllabus and uploaded Unit 9 prompt | Kept Unit 9 scope and M04 cross-module boundaries | Exact prompt pack and project files unavailable separately |
| 2. Structure | PASS | Verified headings 9.0–9.14 and Appendices A–E in requested order | Included substantive content in all sections | Appendix titles follow uploaded Unit 9 prompt because prompt pack appendix titles were unavailable |
| 3. Technical correctness | PASS WITH LIMITATIONS | Reviewed eBPF/verifier/maps, CNI/datapath, policy, Hubble and encryption distinctions | Avoided universal iptables bypass, speed or mTLS-equivalence claims | Exact release behavior depends on installed version/configuration |
| 4. Version integrity | PASS WITH LIMITATIONS | Consulted official stable Cilium 1.20.4 docs and explicitly tagged `latest` docs | Used `<CILIUM_VERSION>` and schema/CLI verification gates | No full compatibility matrix or live CRD schema check performed |
| 5. Safety | PASS WITH LIMITATIONS | Added disposable cluster, context/confirmation guards and destructive cleanup warnings | Primary lab creates a new named cluster; fallback is read-only | Scripts not executed; human must verify the cluster/runtime before running |
| 6. Evidence honesty | PASS | Reviewed for fabricated outputs, benchmarks and execution claims | All sample outputs labelled illustrative; no measured values supplied | Human-run results remain to be collected |
| 7. Reproducibility | PASS WITH LIMITATIONS | Included preflight, version choice, install workflow, tests, evidence and cleanup | Exact version-dependent flags are gated by installed help/docs | CLI/version compatibility must be confirmed before lab |
| 8. Pedagogy | PASS | Beginner-to-advanced explanation, diagrams, worked policy/Hubble examples, answer key | Added explicit interpretation and limits | Learner must adapt sample selectors/ports to actual app |
| 9. Cross-module consistency | PASS WITH LIMITATIONS | Checked available Unit 1/5/7/8 and roadmap boundaries | Reused `ml-platform`, model-api and feature-service vocabulary; avoided duplicating mesh lessons | Unit 10 and project files were not available separately |
| 10. Markdown/completeness/adversarial review | PASS WITH LIMITATIONS | Reviewed headings, tables, code fences, placeholders, blast radius and unsupported-feature claims | CCNP example marked review-only; FQDN policy explicitly version-gated | Automated lint, cluster schema validation and runtime tests not performed |

### Runtime execution status

**Reasoned review only; commands and labs were not executed in this environment.** Official Cilium documentation pages were accessed for the sources listed above. The full compatibility matrix was not audited, manifests were not checked against a live API server, and no Cilium cluster, Hubble flow, policy enforcement test or performance benchmark was run.

## Appendix A — Command and manifest reference

| Command/configuration | Purpose | Safe use / evidence | Version and risk caveat |
|---|---|---|---|
| `uname -a` / `uname -r` | Inspect kernel | Record kernel and OS context | WSL2/Docker/kind share or abstract kernel context; confirm actual node/runtime |
| `kind get clusters` | List local kind clusters | Read-only inventory before create/delete | Does not show non-kind clusters |
| `kubectl config current-context` | Check active Kubernetes context | Must match intended named lab context before mutation | Context name alone does not prove cluster is disposable |
| `kubectl --context <CTX> get nodes` | Inspect node state | Check readiness before/after CNI install | Nodes may be NotReady while default CNI is disabled and Cilium not yet installed |
| `cilium version` | Record CLI/server version | Capture versions before changes | Requires Cilium CLI; exact output varies |
| `cilium install --version <CILIUM_VERSION>` | Install selected Cilium release | Only on fresh disposable cluster, after official compatibility check and CLI help review | Version/flags must match selected release |
| `cilium status --wait` | Wait for installation status | Use only after verifying flag with installed CLI help | Status is not an end-to-end app test |
| `cilium connectivity test` | Run documented connectivity test | Disposable cluster only; capture exact command/version/results | Can create test workloads/traffic; verify flags and release support |
| `hubble observe --help` | Inspect Hubble CLI options | Read-only help | Requires compatible Hubble tooling |
| `cilium monitor` / agent monitor command | Inspect datapath events | Verify exact CLI/agent command for selected release first | Command placement/options are version-sensitive |
| `cilium bpf` | Inspect BPF state where supported | Verify subcommand and required permissions first | Output and subcommands differ; do not modify maps casually |
| `kubectl get crd ciliumnetworkpolicies.cilium.io` | Check CNP CRD exists | Read-only schema prerequisite | Does not prove every desired field is served |
| `kubectl explain ciliumnetworkpolicy.spec --api-version=cilium.io/v2` | Inspect live schema | Only after CRD installed; exact resource name/version may vary | Use installed API schema, not memory |
| `kubectl apply --dry-run=server -f <FILE>` | Validate against live API/admission | Use after review and only against the intended lab context | Requires CRD; does not prove runtime enforcement |
| `CiliumNetworkPolicy` | Namespaced Cilium policy | Test one intended allow and deny path | Cilium-specific API; verify schema |
| `CiliumClusterwideNetworkPolicy` | Cluster-wide Cilium policy | Review-only in this unit; require broad-scope approval | High blast radius; never use as casual lab shortcut |
| `cilium hubble enable` | Enable Hubble where supported | Only after verifying current CLI help, resources and laptop budget | Not assumed available or installed automatically |
| `kind delete cluster --name m04-cilium-lab` | Remove the lab cluster | **⚠ DESTRUCTIVE**; use guard and explicit confirmation | Deletes all resources in that named kind cluster |
| Delete Cilium CRDs manually | Remove API types | Not recommended as generic cleanup | Can disrupt any cluster workloads using those resources; follow official uninstall only |

## Appendix B — Troubleshooting matrix

| Symptom | First evidence | Hypotheses | Safe action | Verify/rollback/escalate |
|---|---|---|---|---|
| Pods NotReady after CNI setup | Node conditions, Pod events, Cilium status | CNI not installed/converged, incompatible config, image pull or subnet issue | Stop; check selected release's installation steps | Continue only when readiness and documented checks pass |
| Cilium status unhealthy | Agent/operator logs/events, versions | Agent crash, unsupported kernel/config, control-plane issue | Preserve evidence; follow version-matched runbook | Escalate if multiple nodes or API reachability affected |
| Pod-to-Pod fails | Endpoints, labels, policy, flow evidence | Selector mismatch, policy denial, routing/datapath issue | Test one path and compare source/destination policies | Restore last known-good test policy if confirmed; do not flush networking |
| Service traffic fails | Service/EndpointSlice, service mode/config | Wrong port, missing endpoints, kube-proxy replacement config | Verify actual mode and service path | Validate with bounded request and status evidence |
| Unexpected policy drop | Matching native NP/CNP/CCNP, labels, flow event | Missing egress/DNS rule, wrong selector or policy scope | Change only a reviewed rule | Positive/negative test and record rollback |
| No Hubble flow | Hubble status, filters, request evidence | No request, wrong filter, telemetry unavailable | Verify telemetry scope and send a bounded test | Do not infer allow/deny from silence |
| FQDN policy failure | DNS query/path, resolved IP, policy schema | DNS not observed, selector mismatch, name mismatch, unsupported behavior | Use a controlled local DNS/mock | Keep external traffic disabled until verified |
| Agent repeatedly restarts | Events, previous logs, resource pressure | Image/kernel/config incompatibility, resource exhaustion | Scope node and capture logs | Follow official release guidance; escalate before broad restart |
| Suspected identity/map exhaustion | Agent/operator logs and documented metrics | Label churn, capacity/config issue | Verify exact limit and allocation mode | No blind map clearing; escalate with evidence |
| Upgrade regression | Version/config/CRD diff and release notes | API/default/datapath changes or unsupported skew | Stop rollout and follow tested rollback | Confirm representative flows before proceeding |
| Performance regression | Kernel/config, workload parity, repeated trials | Different test load, CPU pressure, policy overhead, changed path | Repeat controlled baseline | No claim without repeated measurements |

## Appendix C — Lab evidence and results worksheet

Keep this evidence outside the repository unless a separate task authorizes creating evidence files. Do not store private keys, credentials, Kubernetes Secrets, raw sensitive payloads or unredacted packet captures.

Suggested evidence bundle:
- `versions.txt` — OS/kernel, Docker/runtime, kind, Kubernetes, Cilium CLI/agent/operator and CRD versions.
- `preflight.txt` — context, named lab cluster, node readiness and resource checks.
- `configuration/` — sanitized kind config, selected Cilium config/Helm values, policy manifest and schema verification notes.
- `status-before-after.txt` — selected status and component readiness evidence.
- `connectivity-results.txt` — exact test command, version, timestamp, exit status and output.
- `policy-tests.csv` — source/destination, intended allow/deny, actual result, request ID and interpretation.
- `hubble-samples.txt` — redacted flow evidence and explanation of its limits, if Hubble was enabled.
- `performance.csv` — blank until real trials are performed; include trial, warm-up, duration, packet size, concurrency, throughput, p50/p95/p99, errors/drops, CPU/memory and notes.
- `cleanup-proof.txt` — final request, resource inventory and cluster deletion check if Path A was used.
- `unresolved-verification.md` — version-specific questions and owners.

| Evidence item | Captured? | Path (if any) | Redaction reviewed? | Notes |
|---|---|---|---|---|
| Versions and environment |  |  |  |  |
| Disposable cluster/context proof |  |  |  |  |
| Cilium status/agent readiness |  |  |  |  |
| CNP/CRD schema verification |  |  |  |  |
| Connectivity test |  |  |  |  |
| Allowed flow test |  |  |  |  |
| Denied flow test |  |  |  |  |
| Hubble/monitor evidence |  |  |  |  |
| Performance trials |  |  |  |  |
| Cleanup/post-cleanup validation |  |  |  |  |

## Appendix D — Glossary

- **BPF map:** Kernel-managed data structure used to share state, counters or configuration with eBPF programs and user space.
- **Cilium agent:** Node-level Cilium component responsible for local networking/policy datapath coordination and observation.
- **Cilium operator:** Component responsible for cluster-level tasks assigned to it by the selected Cilium release/configuration.
- **CiliumNetworkPolicy (CNP):** Namespaced Cilium-specific policy API.
- **CiliumClusterwideNetworkPolicy (CCNP):** Cilium-specific cluster-scoped policy API with broad potential impact.
- **CNI:** Container Network Interface, used by Kubernetes/runtime integration to configure Pod networking.
- **Control plane:** Components that manage desired state and distribute configuration.
- **Datapath:** Actual packet-processing path through kernel/networking mechanisms.
- **eBPF:** Extended Berkeley Packet Filter, a Linux kernel facility for running programs at supported hooks under verifier and privilege constraints.
- **FQDN:** Fully qualified domain name; Cilium DNS/FQDN policy behavior depends on supported DNS observation and configuration.
- **Hubble:** Cilium network-flow observability system.
- **Hook:** Supported kernel execution point at which an eBPF program may run.
- **Identity:** Security identity associated with an endpoint based on configured metadata/labels; not merely its current IP address.
- **kube-proxy replacement:** Optional service load-balancing architecture in which Cilium handles supported Kubernetes service functionality.
- **L3/L4/L7:** Network, transport and application-protocol layers used to describe policy granularity.
- **NetworkPolicy:** Kubernetes API for controlling selected Pod ingress/egress reachability when enforced by a supporting network implementation.
- **Operator:** User-space controller that performs cluster-level coordination tasks.
- **Verifier:** Kernel facility that checks eBPF program constraints before loading.
- **WireGuard/IPsec:** Network-layer encryption mechanisms supported in particular Cilium configurations; not substitutes for application authorization or mTLS.

## Appendix E — Author verification and completion checklist

- [ ] Exact target filename is `09-ebpf-networking-and-cilium-overview.md`.
- [ ] Only the target lesson file was created; no sibling lesson, roadmap, prompt pack or repository file was modified.
- [ ] Exact headings 9.0–9.14 and Appendices A–E appear in order.
- [ ] The available roadmap and M04 syllabus scope are represented; missing prompt pack, Unit 10 and project files are disclosed.
- [ ] Cilium/Kubernetes/kernel/CLI compatibility checked against the selected release before any lab mutation.
- [ ] `kind` config and `disableDefaultCNI` behavior checked against official documentation.
- [ ] Every Cilium-specific manifest validated against the installed CRD schema before apply.
- [ ] All context and disposable-cluster guards reviewed before mutating commands.
- [ ] No shared/production cluster, public endpoint, paid service or real secret used.
- [ ] Cilium status and connectivity test evidence captured if Path A was run.
- [ ] Hubble output clearly labelled actual or illustrative, with evidence limitations explained.
- [ ] Allowed and denied policy paths tested with actual outcomes if Path A was run.
- [ ] No fabricated performance result or universal performance claim appears.
- [ ] Cleanup and post-cleanup verification completed if Path A was run.
- [ ] Remaining `[VERIFY]` items assigned to an owner before production use.

**Reviewer:** ______________________________  
**Date:** ______________________________  
**Environment / OS / kernel:** ______________________________  
**Kubernetes / Cilium / CLI versions:** ______________________________  
**Path performed:** Path A / Path B / Neither  
**Actual lab result:** ______________________________  
**Outstanding verification items:** ______________________________  
**Human sign-off:** ______________________________

**Status:** `DRAFT-AUDITED`  
**Runtime statement:** Reasoned review only; commands and labs were not executed in this environment.
