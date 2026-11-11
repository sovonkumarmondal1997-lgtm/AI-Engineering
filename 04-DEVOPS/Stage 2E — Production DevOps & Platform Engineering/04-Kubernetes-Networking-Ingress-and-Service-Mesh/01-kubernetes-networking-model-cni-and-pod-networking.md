# Kubernetes Networking Model, CNI, and Pod Networking

> Unit 1 of Stage 2E — Production DevOps & Platform Engineering, Module M04

**Abstract:** This unit develops a packet-first mental model of Kubernetes pod networking, the Container Network Interface (CNI), address allocation, routes, MTU, and operational failure diagnosis. Labs use a disposable local `kind` cluster. Version-sensitive installation instructions are deliberately gated by official-documentation checks rather than guessed.

**Module:** M04 · **Stage:** 2E · **Unit:** 1  
**Estimated study time:** 12–18 hours, including labs and review  
**Last reviewed:** 2026-10-28  
**Kubernetes/tool baseline assumed:** Linux or WSL2 Ubuntu, Docker, `kind`, `kubectl`, `iproute2`; exact versions must be recorded before running labs. CNI installation compatibility is `[VERIFY]` against the selected release's official documentation.

> **Important verification notice:** This document is written from established knowledge of the documentation; verify against current official docs before executing version-sensitive installation steps. No live cluster was run as part of authoring this document. Commands and outputs marked as examples are illustrative, not observed results.

## Table of contents

- [1.0 Why this matters in production](#10-why-this-matters-in-production)
- [1.1 Learning objectives](#11-learning-objectives)
- [1.2 Concept map and vocabulary](#12-concept-map-and-vocabulary)
- [1.3 Level 1 — Beginner](#13-level-1--beginner)
- [1.4 Level 2 — Intermediate](#14-level-2--intermediate)
- [1.5 Level 3 — Advanced](#15-level-3--advanced)
- [1.6 Level 4 — Expert](#16-level-4--expert)
- [1.7 SRE lens](#17-sre-lens)
- [1.8 Security lens](#18-security-lens)
- [1.9 Production checklist](#19-production-checklist)
- [1.10 Hands-on lab set](#110-hands-on-lab-set)
- [1.11 Self-check questions](#111-self-check-questions)
- [1.12 Evidence artifacts](#112-evidence-artifacts)
- [1.13 Common interview and design-review questions](#113-common-interview-and-design-review-questions)
- [1.14 Sources and verification notes](#114-sources-and-verification-notes)
- [Appendix A — Claim Register](#appendix-a--claim-register)
- [Appendix B — Unit Audit Report](#appendix-b--unit-audit-report)
- [Appendix C — Human Verification Checklist](#appendix-c--human-verification-checklist)
- [Appendix D — Known Limitations and Assumptions](#appendix-d--known-limitations-and-assumptions)
- [Appendix E — CNI Architecture Decision Record Template](#appendix-e--cni-architecture-decision-record-template)

## Unit 1 — Kubernetes networking model, CNI, and pod networking

**Target file:** `01-kubernetes-networking-model-cni-and-pod-networking.md` | **Estimated time:** 12–18 hours | **Prerequisites:** Stages 0–2D; M01 container images; M02 CI/CD; M03 Kubernetes operations; working Linux and TCP/IP basics.  
**Core tools:** `kubectl`, Docker, `kind`, `iproute2`, `ss`, `tcpdump` if available, shell. | **Awareness:** BGP, VXLAN/Geneve/IP-in-IP, Cilium, Calico, Flannel, kindnet, Multus, WireGuard/IPsec. | **Last reviewed:** 2026-10-28 | **Kubernetes/tool baseline assumed:** Record exact versions locally; all compatibility and install claims are `[VERIFY]`.

### 1.0 Why this matters in production

When a FastAPI model-scoring pod cannot reach a feature-service, the application error may be only the final symptom. The root cause could be a missing route, a depleted IP pool, a failed CNI agent, an MTU mismatch, or a policy that is not actually enforced. Incorrect CIDR planning can also make future VPN, VPC peering, or multi-cluster connectivity difficult or impossible without renumbering. Networking changes have a large blast radius because a CNI failure can affect new pod sandboxes across a node or cluster. This unit teaches you to prove the packet path with evidence before changing configuration.

### 1.1 Learning objectives

By completion, the learner can:

1. **[L1]** Explain the four Kubernetes networking requirements and distinguish pod, node, Service, and pod-CIDR addresses.
2. **[L1]** Explain a network namespace, interface, veth pair, bridge, route, and encapsulation.
3. **[L1]** Describe the CNI contract and the runtime's role in invoking network setup/teardown.
4. **[L2]** Inspect node and pod networking using `kubectl`, `docker exec`, and `iproute2`.
5. **[L2]** Trace same-node and cross-node traffic and identify what is observed versus inferred.
6. **[L2]** Compare overlay, routed, and cloud-native network designs.
7. **[L3]** Diagnose IP exhaustion and likely MTU/PMTUD faults with a hypothesis-driven process.
8. **[L3]** Evaluate a CNI using security, policy, IPAM, observability, compatibility, and operational burden.
9. **[L4]** Plan a safe CNI upgrade/migration with validation gates and rollback constraints.
10. **[L4]** Produce a CNI Architecture Decision Record (ADR) supported by evidence and explicit open questions.

### 1.2 Concept map and vocabulary

| Term | Precise definition | Common misconception |
|---|---|---|
| Network namespace | Linux kernel isolation context for network interfaces, routes, sockets, and related state. | It is not a VM or a separate kernel. |
| Interface | A network endpoint visible to a network namespace, such as `eth0` or a host-side virtual interface. | An interface name alone does not reveal the entire packet path. |
| veth pair | Two linked virtual Ethernet interfaces; a frame transmitted on one side is received by the peer. | A veth pair does not itself provide cross-node routing. |
| Bridge | A Layer-2 forwarding device connecting interfaces. | Not every CNI uses a Linux bridge as its primary datapath. |
| Route | A routing-table rule selecting a next hop or interface for a destination prefix. | A route does not guarantee that firewalls, policy, or the remote path permit traffic. |
| Pod IP | An address assigned to a pod's network namespace by the network implementation/IPAM. | It is not the node IP and is not normally the Service ClusterIP. |
| Node IP | An address used by a Kubernetes node for node-level communication. A node may have several. | It is not necessarily the address a remote client sees. |
| Pod CIDR | A prefix associated with a node or cluster for pod address allocation/routing, depending on the implementation and configuration. | It is not the same as the list of addresses currently assigned to pods. |
| IPAM | IP Address Management: allocation, tracking, and release of addresses or prefixes. | Kubernetes does not impose one universal IPAM implementation. |
| CNI | Container Network Interface specification and plugin contract used by runtimes to configure container networking. | CNI is not one specific network product. |
| MTU | Maximum size of a packet/frame payload accepted at a particular network layer/interface, subject to the layer's definition. | One MTU value is not automatically valid end-to-end. |
| PMTUD | Path MTU Discovery: mechanisms by which endpoints infer the maximum packet size across a path. | Blocking required ICMP feedback can cause hard-to-explain large-packet failures. |
| NetworkPolicy enforcement | Actual datapath behavior implementing Kubernetes NetworkPolicy rules. | Creating a NetworkPolicy object does not prove that the installed CNI enforces it. |

#### The four networking requirements

Kubernetes describes a model in which: (1) pods can communicate with other pods without network address translation (NAT) in the normal cluster model; (2) nodes can communicate with pods; (3) a pod can discover its own IP as the address other peers use to reach it; and (4) containers within one pod share the pod network namespace and IP address. Kubernetes does not prescribe one universal packet-forwarding implementation. A CNI and the cluster's network design implement the model.

#### Address types

- **Pod IP:** assigned to the pod network namespace. The application usually binds to this namespace's interfaces.
- **Node IP:** belongs to the node's network environment. In `kind`, a node is a container, so its IP is not necessarily the laptop's IP.
- **Service ClusterIP:** a virtual service address handled by the Kubernetes Service datapath. It is not normally configured as an interface address inside a pod. Full Service translation is covered in [Unit 2](02-services-kube-proxy-and-cluster-dns.md).
- **External address:** an address used outside the cluster; its assignment and path depend on the host, local Docker network, external load balancer, routing, and NAT.
- **Pod CIDR:** an allocation/routing prefix, not an individual pod address.

#### Same-node packet path (conceptual; implementation-dependent)

```text
Source container socket
  -> source pod network namespace (pod IP:source-port)
  -> pod-side interface (often eth0)
  -> veth peer in node network namespace
  -> bridge / host routing / CNI datapath
  -> policy enforcement point, if implemented by the CNI
  -> destination pod's host-side veth
  -> destination pod namespace
  -> destination socket

NAT: not inherently required for ordinary pod-to-pod traffic; may exist for other traffic
or implementation-specific cases. Confirm with routes/rules/capture, not assumption.
```

#### Cross-node packet path (conceptual; inspect the actual CNI)

```text
Pod A namespace
  -> pod interface and host-side peer on Node A
  -> CNI routing/datapath and policy on Node A
  -> [overlay: encapsulate inner pod packet in an outer node-to-node packet]
     OR [routed: forward toward route for destination pod CIDR]
  -> Docker/kind node network (plus possible WSL2/host NAT boundaries)
  -> Node B receives outer packet or routed packet
  -> [overlay: decapsulate, if used]
  -> CNI datapath/policy on Node B
  -> destination pod interface
  -> Pod B namespace

NAT/encapsulation points depend on CNI mode and destination. A packet capture at one point
cannot prove what happens at every other point.
```

#### CNI lifecycle and files

The Container Network Interface (CNI) is a specification/contract for configuring container networking. In Kubernetes, the container runtime mediates sandbox networking and invokes CNI plugins according to the runtime and CNI integration in use; do not simplify this to “the kubelet directly runs every CNI binary.” Operations commonly include `ADD` to configure a sandbox and `DEL` to clean up, with other operations and lifecycle details depending on the specification/runtime version.

- `/etc/cni/net.d`: commonly holds CNI network configuration files on a node.
- `/opt/cni/bin`: commonly holds CNI plugin executables on a node.
- Exact paths, invocation details, config selection, and runtime behavior are `[VERSION-SENSITIVE]`; verify against the runtime and CNI documentation for the installed baseline.
- A successful CNI operation is not a guarantee that every route, policy, DNS query, Service translation, or external network hop is healthy.

### 1.3 Level 1 — Beginner

#### First-principles explanation

A pod is not a VM. Containers in a pod share a network namespace, so they share the pod IP and port space; two containers in the same pod cannot independently listen on the same address/port combination. A network namespace holds network state. A veth pair provides a virtual cable between the pod namespace and the node namespace. The CNI configures the relevant interfaces and addressing, and the implementation ensures traffic can reach the destination through local forwarding, routes, an overlay, or a combination.

Kubernetes objects describe desired state; Linux networking state and CNI agents implement packet forwarding. `kubectl get pods` tells you the assigned pod IP and placement, but not by itself whether the path works.

#### Guided lab: inspect an existing local kind cluster

First inspect, do not mutate:

```bash
# Read-only inventory
kubectl config current-context
kubectl get nodes -o wide
kubectl get pods -A -o wide
kind get clusters
docker ps --format 'table {{.Names}}\t{{.Status}}'
```

**Example — yours will differ:** current context may be `kind-networking-lab`; node and pod names, IPs, and statuses vary. Interpret the output by recording (a) which node hosts each pod, (b) pod IP versus node IP, and (c) whether all relevant pods are Ready.

Discover the node container names rather than assuming them:

```bash
docker ps --format '{{.Names}}'
# Replace <node-container> only after inspecting the output.
docker exec <node-container> ip addr
docker exec <node-container> ip link
docker exec <node-container> ip route
docker exec <node-container> ss -lntup
```

**Example — yours will differ:** `ip addr` lists interfaces and addresses; `ip route` shows connected prefixes and selected next hops. Interface names such as `eth0`, `cni0`, or `vxlan.calico` are not universal. If a command is absent in the node image, record that limitation; do not install tools into a valuable node to force the example.

Check the pod view:

```bash
kubectl get pods -A -o wide
kubectl get nodes -o wide
kubectl get node <node-name> -o jsonpath='{.spec.podCIDR}{"\n"}'
```

**Example — yours will differ:** `.spec.podCIDR` may be empty or not tell the whole allocation story for a particular CNI/configuration. Compare Kubernetes fields with node-local routes and CNI IPAM evidence.

#### What just happened?

`kubectl get pods -o wide` shows Kubernetes' recorded pod IP and node placement. `docker exec` enters the network namespace of a `kind` node container to inspect its own interfaces/routes. These are two different views. A pod's `eth0` is inside the pod namespace; its veth peer is visible from the host/node namespace, but it may not have an obvious pod name. `ip netns list` may show nothing because container runtimes do not have to register every network namespace under the conventional `/var/run/netns` names. Where permitted, process namespace handles and `nsenter` can help, but do not assume host PID visibility or privileges in WSL2.

#### Common beginner mistakes → symptom → fix

- Confusing pod IP with node IP → packet path analysis points at the wrong interface → record pod IP, node placement, and node IP separately.
- Assuming a NetworkPolicy is enforced because it exists → traffic still passes → verify the CNI's documented enforcement capability and test a controlled allow/deny case.
- Assuming `localhost` means the same thing everywhere → connection refused → identify whether the command runs on Windows, WSL2, a node container, or inside a pod.
- Assuming `ip netns list` enumerates all container namespaces → empty output → use runtime/node inspection methods appropriate to the environment.
- Treating a single capture as the whole path → incorrect root cause → capture at multiple relevant points and state what each observation proves.

### 1.4 Level 2 — Intermediate

#### Runnable topology and safety guard

The following creates a disposable cluster using kind's default CNI. It is useful for learning node/pod inspection, but **does not satisfy the policy-capable CNI lab by itself**. Do not install a second CNI on top of an existing one. For the policy-capable CNI branch, follow the official CNI's current kind-specific guide and the verification gates below.

```yaml
# File: lab/kind-config.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: networking-lab
nodes:
  - role: control-plane
  - role: worker
  - role: worker
```

`kind.x-k8s.io/v1alpha4` is kind's configuration API in commonly used releases, but confirm against the installed kind documentation. For reproducibility, pin a Kubernetes node image tag supported by your selected kind release after checking the kind release matrix; this document does not guess a current tag.

```bash
# File: lab/create-default-kind.sh
#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME="networking-lab"
EXPECTED_CONTEXT="kind-${CLUSTER_NAME}"

for cmd in docker kind kubectl; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "Missing command: $cmd" >&2; exit 2; }
done

docker info >/dev/null
kind get clusters
CURRENT_CONTEXT="$(kubectl config current-context 2>/dev/null || true)"

if kind get clusters | grep -Fxq "$CLUSTER_NAME"; then
  echo "Refusing to overwrite existing cluster '$CLUSTER_NAME'." >&2
  exit 3
fi
if [[ -n "$CURRENT_CONTEXT" && "$CURRENT_CONTEXT" != "$EXPECTED_CONTEXT" ]]; then
  echo "Current context is '$CURRENT_CONTEXT'. Inspect it before creating or mutating clusters." >&2
  echo "Expected context for subsequent lab operations: '$EXPECTED_CONTEXT'." >&2
  exit 4
fi

kind create cluster --config lab/kind-config.yaml
kubectl --context "$EXPECTED_CONTEXT" get nodes -o wide
```

**Example — yours will differ:** nodes should eventually become `Ready` when the default kind networking is functioning. If creation fails, inspect Docker resources and kind logs before retrying. This script refuses to overwrite a same-named cluster; it does not delete or replace an existing one.

> **WSL2 caveat:** Docker Desktop/WSL2 introduces additional network and NAT boundaries. `localhost` in a pod, a kind node container, WSL2, and Windows can refer to different network namespaces. This lab has no real multi-AZ topology and cannot prove cloud load-balancer, VPC, or production routing behavior.

#### Trace same-node and cross-node flows

Deploy a tiny HTTP server and client. Image tags must be pinned to an approved, reviewed version before use; replace the illustrative placeholder only after confirming the image exists and supports the requested command.

```yaml
# File: lab/traffic-test.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: netlab
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: netlab
  namespace: netlab
automountServiceAccountToken: false
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: echo
  namespace: netlab
spec:
  replicas: 2
  selector:
    matchLabels:
      app: echo
  template:
    metadata:
      labels:
        app: echo
    spec:
      serviceAccountName: netlab
      containers:
        - name: echo
          image: hashicorp/http-echo:<PINNED_VERSION>
          args: ["-listen=:8080", "-text=network-lab"]
          ports:
            - name: http
              containerPort: 8080
          resources:
            requests:
              cpu: 10m
              memory: 16Mi
            limits:
              cpu: 100m
              memory: 64Mi
          securityContext:
            runAsNonRoot: true
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop: ["ALL"]
          readinessProbe:
            tcpSocket:
              port: http
            periodSeconds: 5
          livenessProbe:
            tcpSocket:
              port: http
            periodSeconds: 10
---
apiVersion: v1
kind: Pod
metadata:
  name: client
  namespace: netlab
  labels:
    app: client
spec:
  serviceAccountName: netlab
  automountServiceAccountToken: false
  containers:
    - name: client
      image: curlimages/curl:<PINNED_VERSION>
      command: ["sh", "-c", "sleep 36000"]
      resources:
        requests:
          cpu: 10m
          memory: 16Mi
        limits:
          cpu: 100m
          memory: 64Mi
      securityContext:
        runAsNonRoot: true
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop: ["ALL"]
```

Before applying, replace `<PINNED_VERSION>` with verified immutable tags/digests. A literal placeholder is not runnable. Validate then apply only after checking the context:

```bash
kubectl config current-context
kubectl --context kind-networking-lab apply --dry-run=server -f lab/traffic-test.yaml
kubectl --context kind-networking-lab apply -f lab/traffic-test.yaml
kubectl --context kind-networking-lab -n netlab get pods -o wide
kubectl --context kind-networking-lab -n netlab get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.nodeName}{"\t"}{.status.podIP}{"\n"}{end}'
```

**Example — yours will differ:** two `echo` replicas may land on the same or different nodes; Kubernetes scheduling is not a guarantee of distribution. Confirm actual placement before labeling a request “same-node” or “cross-node.” If you need deterministic placement, use node selectors/affinity based on the discovered node labels and validate the resulting placement; avoid assuming node names.

For an observed pod IP, issue a direct request from the client. If the client image does not contain the desired utility, use a reviewed diagnostic image with a pinned digest, or run a command supported by the selected image.

```bash
kubectl --context kind-networking-lab -n netlab exec client -- \
  curl --connect-timeout 3 http://<ECHO_POD_IP>:8080/
```

**Example — yours will differ:** a successful response containing `network-lab` proves this request reached the selected pod at that time; it does not prove every cross-node path, policy rule, or failure case.

To inspect node networking:

```bash
for node in $(kind get nodes --name networking-lab); do
  echo "===== $node ====="
  docker exec "$node" ip addr
  docker exec "$node" ip route
done
```

**Example — yours will differ:** routes and interfaces vary with CNI and kind versions. Save output with node names. Use `tcpdump` only for your lab's traffic; captures can contain sensitive payloads. A capture on the node's Docker-facing interface may show outer encapsulated traffic but not the original inner packet, depending on the CNI and capture point.

#### Network model comparison

| Model | Packet path | Encapsulation | Dependencies | MTU implications | Strengths | Limitations / common failures |
|---|---|---|---|---|---|---|
| Overlay | Pod packet is carried inside a node-to-node packet. | Often VXLAN, Geneve, or IP-in-IP, depending on CNI/mode. | Overlay interfaces, underlay reachability, tunnel config. | Outer headers reduce usable inner MTU. | Can connect pod ranges without native underlay routes for each pod. | MTU mismatch, blocked tunnel protocol/port, tunnel/route failure. |
| Routed | Node routes traffic toward destination pod prefix or next hop. | None required by the routing model itself. | Correct host routes or routing protocol, forwarding, firewall rules. | Often avoids tunnel overhead, but physical/virtual path MTU still matters. | Transparent packet path; potentially efficient. | Missing/incorrect route propagation, route scale, overlapping prefixes. |
| Cloud-native | Pod addresses or node interfaces integrate with cloud network constructs. | Depends on implementation; not inherently an overlay. | Cloud IP allocation, VPC routes, security controls, quotas. | Depends on cloud path and encapsulation details. | Native integration and cloud routing semantics. | Address quota exhaustion, route/security-group mismatch, provider-specific limits. |

#### CNI comparison: selection depth

| CNI | Appropriate learning focus | NetworkPolicy | Observability / encryption | Operational note |
|---|---|---|---|---|
| kindnet | Default local kind networking behavior and lab limitations. | Do not assume Kubernetes NetworkPolicy enforcement; verify the installed kind setup. | Basic inspection through node state and logs. | Convenient for basic labs; not a production CNI recommendation by itself. |
| Calico | Policy, routing/overlay choices, IPAM, and operational model. | Supports policy capabilities in documented configurations; verify mode/version. | Product capabilities vary by configuration and release. | Evaluate installation path, dataplane mode, and upgrade compatibility. |
| Cilium | eBPF-based datapath concepts, policy, visibility, and optional advanced features. | Supports policy; exact behavior depends on configuration/version. | Hubble and encryption options depend on enabled components and compatibility. | Check kernel, kind workflow, and resource needs before selecting it for an 8 GB laptop. |
| Flannel | Overlay networking concepts and simple pod connectivity. | Do not assume native NetworkPolicy enforcement from Flannel alone; combinations vary. | Observability and security features depend on companion components. | Useful for topology learning; validate policy requirements separately. |

All current release, compatibility, maintenance, kernel, installation, encryption, and feature claims are `[VERIFY]`. Do not install multiple CNIs into one cluster to compare them.

### 1.5 Level 3 — Advanced

#### CNI selection trade-offs

| Option | Benefit | Cost | Risk | Choose when |
|---|---|---|---|---|
| Minimal/default cluster CNI | Less operational complexity for basic clusters. | May lack required policy or visibility features. | Security assumptions may be false. | Workload requirements are modest and limitations are documented. |
| Policy-focused CNI | Enforces L3/L4 segmentation when correctly configured. | Policy testing and troubleshooting burden. | Mislabeling or policy mistakes can interrupt traffic. | Segmentation is a production requirement. |
| eBPF-capable CNI | Can integrate routing, policy, and visibility in a kernel datapath. | Kernel compatibility and deeper operational skills. | Upgrade/feature interactions can be complex. | Team can support its kernel, rollout, and troubleshooting model. |
| Cloud-integrated networking | Native address/routing integration. | Provider quotas, costs, and platform-specific operations. | Cloud network changes can affect many workloads. | Cluster is intentionally tied to a cloud network design. |

Do not select on benchmark claims alone. Measure representative traffic, payload sizes, concurrency, CPU/memory, packet drops, and tail latency on a controlled baseline. Laptop results teach methodology; they are not production capacity predictions.

#### IPAM and capacity

IPAM may allocate per-node pod CIDR blocks and then allocate pod addresses from those blocks, or use an underlying network's address allocation model. Exact behavior is CNI-specific. Capacity planning should consider:

- expected maximum pods per node and rollout surge;
- addresses available per allocated prefix;
- reserved addresses and implementation overhead;
- node scale-out and replacement behavior;
- cluster Pod CIDR and Service CIDR;
- VPN, corporate, VPC, peering, and future cluster ranges;
- provider-specific address quotas if applicable.

A pod stuck in `ContainerCreating` with `FailedCreatePodSandBox` may indicate an IPAM failure, but this is a hypothesis, not a diagnosis. Check events, CNI agent logs, IPAM state, node readiness, and recent changes. Avoid quoting a universal pod limit; limits vary by distribution, CNI, node size, cloud configuration, and kubelet settings.

#### MTU and PMTUD

Encapsulation adds headers to an outer packet. If the underlay MTU is \(M\) and encapsulation overhead is \(H\), a first approximation for the maximum inner packet is \(M-H\), but the exact overhead depends on the encapsulation, address family, options, and path. Treat this as an estimate, then measure.

A classic symptom is that small requests succeed but large payloads or long-lived streams stall. Possible causes include MTU mismatch, blocked ICMP needed for PMTUD, a tunnel path issue, or application timeouts. On Linux, `ping -M do -s <payload>` can help test IPv4 path sizes where supported; payload semantics and flags differ by platform/address family. Do not treat ping alone as proof of the application's path. Use controlled captures and application-level tests.

#### Encryption and authorization are different controls

WireGuard and IPsec are examples of mechanisms used to encrypt node-to-node traffic in supported configurations. Encryption protects data in transit; it does not itself decide which workload is authorized to connect. NetworkPolicy enforcement is a separate control. Product support, kernel requirements, key management, and installation steps are `[VERIFY]`.

#### CNI versus kube-proxy

The CNI configures pod networking and the datapath needed for pod connectivity; the Service datapath (commonly kube-proxy or a CNI-provided alternative) implements virtual Service behavior. The boundary is implementation-dependent, especially in eBPF-based setups. A direct pod-IP request isolates more of the pod-routing path than a Service-IP request, but it is still not a complete diagnosis. Full Service, EndpointSlice, kube-proxy, and DNS analysis belongs in [Unit 2](02-services-kube-proxy-and-cluster-dns.md).

### 1.6 Level 4 — Expert

#### Failure decision tree: `ContainerCreating` / sandbox errors

```text
Pod stuck in ContainerCreating?
  |
  +-- kubectl describe pod -> inspect Events and exact FailedCreatePodSandBox message
  |
  +-- Node Ready?
  |     +-- No -> inspect node conditions, system pods, kubelet/runtime and CNI readiness
  |
  +-- CNI agent healthy on the target node?
  |     +-- No -> inspect agent logs, recent rollout, node/kernel compatibility
  |
  +-- CNI config and binaries present/valid?
  |     +-- No -> compare /etc/cni/net.d and /opt/cni/bin with the approved release
  |
  +-- IPAM allocation succeeds and pool has capacity?
  |     +-- No -> inspect allocation state, per-node/cluster capacity, recent pod churn
  |
  +-- Pod IP assigned but traffic fails?
        +-- inspect routes, interfaces, policy enforcement, MTU and capture points
        +-- separate direct pod-IP failure from Service/DNS failure
```

Read-only first:

```bash
kubectl --context kind-networking-lab -n netlab describe pod <pod-name>
kubectl --context kind-networking-lab get nodes
kubectl --context kind-networking-lab get pods -A -o wide
kubectl --context kind-networking-lab get events -A --sort-by=.lastTimestamp
```

**Example — yours will differ:** the event message may identify a CNI `ADD` failure, IP allocation problem, missing binary/configuration, or a different failure. Follow the exact message and gather evidence before changing anything.

For a CNI-specific agent, discover the namespace, pod names, and labels first; then read logs for the relevant node. Do not copy a guessed selector or namespace from a different release. On a self-managed Linux node, runtime/kubelet logs may be available through systemd; in kind, logs and node containers differ. Use the current runtime's official diagnostic guidance.

#### Failure scenarios and controls

| Symptom | Hypothesis | Test/evidence | Fix and prevention |
|---|---|---|---|
| New pods fail sandbox setup | CNI agent/config/runtime issue | Pod events, node readiness, agent logs, config/binary inventory | Restore compatible config/artifacts; pin and stage upgrades. |
| Some pod IPs cannot be allocated | IPAM exhaustion or allocation leak | Allocation state, per-node CIDR, pod churn, CNI logs | Reclaim safely, expand/replan ranges, alert on remaining capacity. |
| Cross-node only fails | Missing route, tunnel failure, firewall, or MTU | Compare source/destination routes and captures on both nodes | Repair route/tunnel/firewall; validate bidirectional traffic. |
| Small requests work, large ones stall | MTU/PMTUD issue | Controlled size sweep, capture ICMP/fragment behavior | Align MTUs and allow required PMTUD signals; retest realistic payloads. |
| Policy object exists but traffic passes | CNI doesn't enforce it or selector mismatch | Confirm CNI capability; test a policy matrix | Install/configure a policy-enforcing implementation and test deny/allow. |
| Existing traffic works but new pods fail after agent crash | Existing datapath state survives while setup/update fails | Compare old and newly created pods; agent/runtime events | Restore agent; avoid assuming existing flows prove control-plane health. |
| CIDR overlap causes asymmetric reachability | Competing routes select different destinations | Compare route tables and address plans | Renumber before peering; document reserved ranges and ownership. |
| CNI upgrade leaves nodes NotReady | Compatibility or rollout/order failure | Node conditions, agent rollout, release notes, runtime/kernel matrix | Stop rollout, follow documented recovery plan; don't improvise a second CNI. |

#### CNI migration strategy

1. Inventory current CNI, version, datapath mode, IPAM, policy objects, kernel/runtime, node images, and all dependencies.
2. Read official upgrade and migration docs for the exact current-to-target path; confirm whether in-place replacement is supported.
3. Reproduce in a disposable cluster with representative workloads and failure tests.
4. Define preflight checks, maintenance window, canary/staged rollout, health gates, abort criteria, and owner.
5. Back up cluster configuration and CNI state according to vendor guidance; understand what is and is not restorable.
6. Validate pod creation, same-node and cross-node traffic, policy, DNS/Service path, MTU, and node recovery.
7. Roll out gradually and watch errors/latency; halt on predefined thresholds.
8. Execute rollback only by the documented supported procedure. Rollback may not be a simple inverse if CRDs, IPAM state, routes, or datapath configuration changed.
9. Record lessons, versions, evidence, and a runbook update.

### 1.7 SRE lens

Useful indicators include pod sandbox setup failure rate, node readiness, CNI agent health, IPAM pool utilization, packet drops, cross-node request success, and latency by path. Define an SLI with an explicit denominator—for example, successful test requests divided by total synthetic requests over a window. Do not invent a universal SLO; derive it from the platform's user-facing reliability objectives.

**Runbook snippet**

- **Alert:** sandbox failures or cross-node probe failures increase.
- **Triage:** identify affected nodes and workloads; inspect events, CNI agent status, recent changes, pod IP/CIDR, and direct pod-IP path.
- **Mitigate:** stop a rollout; avoid deleting CNI components blindly. Use the approved rollback or node-isolation procedure.
- **Follow-up:** preserve sanitized evidence, find the initiating change, add a regression test, and update capacity/compatibility checks.

**Blast radius:** a per-pod policy issue may be narrow; broken node networking or IPAM can affect every new pod on a node; a bad cluster-wide CNI rollout can affect the whole cluster. CNI capacity planning should include operational time, address-space cost, and the human cost of supporting complex datapaths.

### 1.8 Security lens

Threats include lateral movement between workloads, traffic interception on untrusted paths, unauthorized egress, spoofing, accidental exposure caused by `hostNetwork`, and false confidence from unenforced policy objects. CNI agents often require elevated privileges to configure kernel networking; verify the vendor's permissions, image provenance, release signatures/checksums, and upgrade path.

| Control | Verification |
|---|---|
| NetworkPolicy is actually enforced | Read the selected CNI's official support docs, then run a controlled source/destination/port allow-deny matrix. |
| Least-privilege workload defaults | Inspect workload security contexts, ServiceAccount token mounting, and RBAC. |
| CNI artifacts are trusted | Verify official registry/release source, digest/signature guidance, and pinned version. |
| Host networking is exceptional | Search manifests for `hostNetwork: true`; review each use for port collisions and isolation. |
| Captures do not leak data | Capture only lab traffic, summarize/redact evidence, and delete raw PCAPs after analysis. |
| CIDRs do not overlap | Compare pod/service ranges against corporate VPN, VPC, and future-cluster allocations. |

This unit does not implement full zero-trust segmentation, TLS/mTLS, ingress protection, or egress controls. Those are covered in sibling units.

### 1.9 Production checklist

- [ ] Current CNI, version, datapath mode, IPAM, runtime, kernel, and node image are recorded.
- [ ] Pod CIDR, Service CIDR, node ranges, VPN/VPC ranges, and future-cluster ranges are documented and non-overlapping.
- [ ] Same-node and cross-node flows have been tested with the actual CNI configuration.
- [ ] NetworkPolicy enforcement is proven by a controlled test, not inferred from API objects.
- [ ] MTU and PMTUD behavior are tested with realistic payload sizes.
- [ ] IPAM utilization and sandbox failures have alerting/triage procedures.
- [ ] CNI upgrades are pinned, reviewed, staged, and have a documented recovery plan.
- [ ] Existing datapath behavior and new-pod behavior are both considered during CNI-agent failure.
- [ ] Host-network workloads are reviewed and justified.
- [ ] Local-lab limitations are not used as proof of cloud or multi-AZ behavior.

### 1.10 Hands-on lab set

All labs are local-only and should fit within the approximate 4 CPU / 8 GB RAM / 30 GB disk budget if run one at a time. Measure actual Docker/container memory before adding a more feature-rich CNI. Avoid running a service mesh, full observability stack, and multiple CNI stacks simultaneously.

#### Lab 1 — Inspect pod and node network state

**Goal:** distinguish pod IP, node IP, interfaces, and routes.  
**Steps:** use the read-only commands in Unit 1.3; save node/pod output and node `ip addr`/`ip route`.  
**Expected evidence:** mapping of each pod to node and pod IP, plus route snapshots.  
**Cleanup:** no mutation required.  
**Stretch:** use `ss` to identify listening sockets in a diagnostic pod.  
**kind caveat:** a kind node is a container, not a physical or cloud VM.

#### Lab 2 — Same-node and cross-node pod traffic

**Goal:** prove placement and request success.  
**Steps:** deploy the test workloads in Unit 1.4 with pinned images; verify actual placement; call the destination pod IP directly. Capture only lab traffic if `tcpdump` is available and permitted.  
**Expected evidence:** source/destination pod IP, source/destination node, successful request output, and capture-point notes.  
**Cleanup:** `kubectl --context kind-networking-lab delete namespace netlab` after confirming the context.  
**Stretch:** compare the direct pod-IP path with a Service path after studying Unit 2.  
**kind caveat:** Docker networking and WSL2 can alter the observed outer path.

#### Lab 3 — Policy-capable CNI installation (required verification-gated lab)

**Goal:** create a disposable multi-node kind cluster with one CNI that officially documents policy enforcement and a compatible kind installation workflow.  
**Resource estimate:** measure before install; if the documented CNI plus Kubernetes exceeds the laptop budget, use the concept-only fallback and do not claim enforcement.  
**Preflight:** record `kind version`, `kubectl version --client`, `docker version`, kernel (`uname -r` in WSL2/Linux), free disk, and available memory. Confirm cluster name `networking-policy-lab` is unused and inspect `kubectl config current-context`.  
**Install procedure:** choose Cilium or Calico only after consulting its current official kind installation guide and compatibility matrix. Record the exact documentation URL, release version, node image, kernel requirements, install command, and rollback/recreate steps in `environment-and-versions.md`. The exact commands are `[VERIFY: current official CNI kind guide]`; they are intentionally not guessed here. Do not install two CNIs in the same cluster.

A common kind workflow can involve disabling the default CNI at cluster creation, but whether `disableDefaultCNI: true` and the selected CNI's install order are supported must be confirmed for the exact kind/CNI release. If official instructions do not support the host/kernel combination, delete only the disposable cluster and use the fallback: continue with default-kind routing inspection, document that NetworkPolicy enforcement was not tested, and do not present policy as enforced.

**Observe pre-CNI state:** only do this if the verified install workflow explicitly requires a cluster without the default CNI. Expect nodes to remain `NotReady` until a working CNI is installed; this must be a temporary, isolated state. Save `kubectl get nodes` and events.  
**After install:** wait with a bounded timeout for nodes to become `Ready`; inspect system pods and events. If readiness does not converge, stop and follow the CNI's official troubleshooting path rather than adding a second CNI.  
**Traffic test:** deploy minimal non-root test workloads with pinned images, resource requests/limits, explicit ServiceAccount, and readiness checks. Confirm actual node placement, run same-node and cross-node requests, inspect node routes/interfaces, and record per-node pod CIDR evidence. Test a policy only if the selected CNI documents enforcement and the controlled deny/allow test behaves as expected.  
**Cleanup — ⚠ DESTRUCTIVE:** first run `kubectl config current-context` and `kind get clusters`. Confirm the exact target is `networking-policy-lab`; then delete that named disposable cluster using kind's documented delete command. Verify it no longer appears in `kind get clusters`. Do not delete CRDs from a shared cluster; CRD deletion may remove dependent custom resources.  
**Expected evidence:** pre/post readiness, CNI agent health, routes/interfaces, pod placements/IPs, same/cross-node request results, policy test result or explicit “not tested,” and cleanup report.  
**kind caveat:** local kind traffic does not establish cloud network, multi-AZ, production throughput, or managed-load-balancer behavior.

#### Lab 4 — MTU hypothesis test

**Goal:** understand why large payloads may fail while small payloads work.  
**Steps:** first identify the path and interface MTUs; use a controlled lab destination. If supported, test progressively larger payloads with Linux `ping -M do -s <payload> <destination>` and correlate with packet captures. Do not run tests against third-party systems.  
**Expected evidence:** tested sizes, command/platform, observed responses, MTU at capture points, and caveats.  
**Cleanup:** no persistent changes; delete raw captures.  
**Stretch:** compare pod-to-pod and node-to-node paths.  
**kind caveat:** WSL2 and Docker add boundaries and may change the path.

#### Lab 5 — Controlled workload-level failure and diagnosis

**Goal:** practice hypothesis-driven triage without damaging CNI state.  
**Steps:** use an intentionally wrong test destination IP or stop the test server; record symptom, hypothesis, test, evidence, fix, and prevention. Do **not** alter the only active cluster's CNI config or routes.  
**Expected evidence:** one incident note showing why the initial hypothesis was accepted/rejected.  
**Cleanup:** restore the destination/server and remove test resources.  
**Stretch:** distinguish connection refused, timeout, and no-route symptoms.  
**kind caveat:** failure is deliberately at the workload/test level, not a simulation of every CNI failure.

### 1.11 Self-check questions

1. **Why can two containers in one pod use `localhost` to communicate?**  
   **Answer:** They share the pod network namespace and IP/port space. **Tempting wrong answer:** they share a filesystem or VM; those are separate concepts.

2. **What does a veth pair do?**  
   **Answer:** It links two virtual Ethernet interfaces across namespaces. **Tempting wrong answer:** it routes between nodes; routing is a separate function.

3. **Is a Service ClusterIP normally configured on a pod's `eth0`?**  
   **Answer:** No; it is a virtual Service address implemented by the Service datapath. **Tempting wrong answer:** all Kubernetes IPs are interface addresses.

4. **Who invokes CNI plugins in the Kubernetes sandbox lifecycle?**  
   **Answer:** The runtime mediates sandbox networking and invokes plugins according to its CNI integration; exact details depend on versions. **Tempting wrong answer:** the kubelet directly invokes every plugin in all implementations.

5. **Why is `kubectl get pods -o wide` insufficient to prove connectivity?**  
   **Answer:** It shows assigned IP and placement, not route, policy, firewall, MTU, or socket health. **Tempting wrong answer:** a pod IP implies a working datapath.

6. **What extra issue can an overlay introduce?**  
   **Answer:** Encapsulation overhead reduces effective inner MTU and requires the outer path to carry tunnel traffic. **Tempting wrong answer:** encapsulation only changes performance, never packet size.

7. **Why might small requests work but large ones stall?**  
   **Answer:** MTU/PMTUD or fragmentation/ICMP handling may fail. **Tempting wrong answer:** the application must be slow.

8. **Does a NetworkPolicy object prove the traffic is blocked?**  
   **Answer:** No; the CNI must enforce it and selectors/ports must match. **Tempting wrong answer:** API acceptance means datapath enforcement.

9. **What is the difference between a pod CIDR and pod IP?**  
   **Answer:** A CIDR is a prefix for allocation/routing; a pod IP is one address assigned to a pod. **Tempting wrong answer:** they are interchangeable labels.

10. **What should you check first for `FailedCreatePodSandBox`?**  
    **Answer:** Exact pod events, node readiness, and CNI/runtime errors; then agent/config/IPAM evidence. **Tempting wrong answer:** delete the pod repeatedly without inspecting the cause.

11. **Can a CNI-agent crash immediately break every existing connection?**  
    **Answer:** Not universally; existing datapath state may continue while new sandbox setup or updates fail. Behavior depends on implementation and failure mode. **Tempting wrong answer:** every CNI behaves identically.

12. **Why reserve non-overlapping CIDRs early?**  
    **Answer:** Overlap can make routing, VPN/peering, and multi-cluster connectivity ambiguous. **Tempting wrong answer:** NAT will always solve overlapping networks.

13. **What does a successful direct pod-IP request prove?**  
    **Answer:** That one path/request worked at that time. It does not prove Service, DNS, policy coverage, or every node path. **Tempting wrong answer:** one success certifies the cluster network.

14. **Why is CNI migration high risk?**  
    **Answer:** It changes routes, interfaces, IPAM, policy, and node readiness across workloads; rollback may not be a simple inverse. **Tempting wrong answer:** a CNI is just a replaceable daemon.

15. **What must be recorded before a CNI choice?**  
    **Answer:** Workload needs, policy/IPAM/topology requirements, kernel/runtime compatibility, evidence, operational skills, risks, and rollback plan. **Tempting wrong answer:** choose based on popularity alone.

### 1.12 Evidence artifacts

Save the following under a local lab evidence directory; sanitize hostnames/IPs if sharing publicly.

- `environment-and-versions.md` — OS/WSL2 or native Linux, Docker, kind, Kubernetes node image, CNI and version, kernel, official links checked.
- `kind-config.yaml` — exact disposable-cluster configuration.
- `nodes-and-pods.txt` — sanitized `kubectl get nodes/pods -o wide` output.
- `pod-cidr-and-routes.md` — per-node pod CIDR fields, node-local routes, interfaces, and interpretation.
- `same-node-flow.md` and `cross-node-flow.md` — source/destination IPs, node placement, command, output, route evidence, capture point and limitations.
- `cni-comparison.md` — topology, policy, IPAM, observability, encryption, compatibility, operational burden.
- `cni-adr.md` — completed decision record with alternatives and rollback.
- `lab-verification-and-cleanup.md` — validation, known failures, cleanup confirmation, and open items.
- `known-limitations.md` — kind/WSL2 limitations and unverified assumptions.

Do not retain raw packet captures containing secrets or payloads. Save sanitized summaries and delete raw captures after analysis.

### 1.13 Common interview and design-review questions

1. **Walk through a same-node and cross-node pod packet.**  
   **Model answer:** Start at the source socket and pod namespace, follow the pod interface and host-side veth, inspect the CNI's local forwarding/routing, identify policy points, then explain the actual cross-node path as observed—tunnel encapsulation or routed forwarding—and the destination-side delivery. Separate captured facts from inferred steps and do not assume NAT or a specific interface name.

2. **A pod is stuck in `ContainerCreating` with `FailedCreatePodSandBox`. How do you respond?**  
   **Model answer:** Read the exact event, check node readiness, CNI agent health/logs, runtime signals, CNI config/binaries, IPAM state/capacity, and recent changes. Establish whether the failure is node-specific or cluster-wide. Do not repeatedly delete pods or install a second CNI without evidence.

3. **Small API calls work but large model payloads time out. What do you investigate?**  
   **Model answer:** Compare path/interface MTUs, encapsulation overhead, PMTUD/ICMP behavior, captures at relevant points, and application/LB timeouts. Use controlled size tests. Check IPAM separately if the symptom is intermittent pod creation rather than size-dependent traffic.

4. **How do you choose and migrate a CNI?**  
   **Model answer:** Map workload requirements to policy, IPAM, topology, observability, encryption, kernel/runtime compatibility, support, and on-call capability. Benchmark methodically, test a disposable cluster, pin versions, stage rollout, define gates and abort criteria, and use the vendor-supported recovery plan. Do not assume rollback is a simple inverse.

5. **A NetworkPolicy exists but traffic is still allowed. Is kube-proxy broken?**  
   **Model answer:** Not necessarily. First verify that the CNI actually enforces NetworkPolicy and that the policy selectors/ports match. CNI pod networking and Service translation are distinct responsibilities, although some CNIs implement a Service datapath. Test direct pod IP and Service IP separately; defer detailed Service/kube-proxy analysis to Unit 2.

### 1.14 Sources and verification notes

This document does not claim that current web documentation was consulted during authoring. Verify these official sources before executing version-sensitive steps:

- Kubernetes documentation: **Cluster Networking**, **Nodes**, **Pods**, and **Network Policies** — verify current sections and semantics.
- CNI project: **CNI Specification** — verify version and runtime/plugin lifecycle details.
- kind documentation: **Configuration**, **Known Issues**, and **Networking** — verify the installed kind version and node image compatibility.
- Selected CNI official documentation: installation on kind, architecture/datapath, IPAM, NetworkPolicy, MTU, kernel prerequisites, upgrades, and recovery.
- Linux `iproute2` manual pages: `ip-link(8)`, `ip-address(8)`, `ip-route(8)`, `ip-netns(8)`, `nsenter(1)`, and `tcpdump(8)` where applicable.
- Container runtime documentation for the runtime actually used by the cluster.

Use canonical URLs from the official project domains when checking current material. Record the exact version and section consulted in `environment-and-versions.md`. All current release tags, installation commands, kernel prerequisites, policy behavior, dual-stack support, and maintenance status remain `[VERIFY]` until confirmed.

---

## Appendix A — Claim Register

| ID | Section | Claim | Source (official document + section/title) | Confidence | Tag / verification action |
|---|---|---|---|---|---|
| A01 | 1.2 | Kubernetes networking model includes pod-to-pod connectivity without NAT in the normal model. | Kubernetes docs, Cluster Networking | High | Verify current wording and exceptions. |
| A02 | 1.2 | Containers in a pod share the pod network namespace. | Kubernetes docs, Pods / Networking | High | Verify current documentation. |
| A03 | 1.2 | Kubernetes does not mandate one universal packet-forwarding implementation. | Kubernetes docs, Cluster Networking | High | Verify current wording. |
| A04 | 1.2 | CNI is a specification/contract for container networking plugins. | CNI Specification | High | Verify spec version used by runtime. |
| A05 | 1.2 | Runtime integration mediates CNI invocation for sandbox networking. | Kubernetes CRI/runtime docs; CNI Specification | Medium | `[VERIFY]` exact runtime lifecycle for installed versions. |
| A06 | 1.2 | `/etc/cni/net.d` commonly stores CNI config. | CNI project docs and distribution docs | Medium | `[VERIFY]` actual node filesystem. |
| A07 | 1.2 | `/opt/cni/bin` commonly stores plugin binaries. | CNI project docs and distribution docs | Medium | `[VERIFY]` actual node filesystem. |
| A08 | 1.2 | A CNI success does not prove every network path is healthy. | Inference from component boundaries | High | Test end-to-end separately. |
| A09 | 1.2 | Service ClusterIP is not normally a pod interface address. | Kubernetes docs, Services | High | Full details deferred to Unit 2. |
| A10 | 1.3 | `ip route` exposes routing-table entries in the current namespace. | `ip-route(8)` | High | Check command availability. |
| A11 | 1.3 | `ip netns list` may not enumerate all runtime-created namespaces. | `ip-netns(8)` and runtime implementation behavior | Medium | Verify namespace registration in the host environment. |
| A12 | 1.4 | kind nodes run as containers. | kind docs, Design / Quick Start | High | Verify kind version. |
| A13 | 1.4 | kind/WSL2 adds network boundaries not equivalent to cloud networking. | kind networking docs; WSL2 docs | High | Record host setup-specific topology. |
| A14 | 1.4 | Interface names vary by CNI and configuration. | Linux/CNI implementation behavior | High | Inspect rather than assume. |
| A15 | 1.4 | Overlay encapsulation can reduce effective inner MTU. | Selected CNI docs; tunnel protocol docs | High | Verify actual encapsulation and overhead. |
| A16 | 1.4 | Routed models need correct routes to destination pod prefixes. | Linux routing docs; CNI architecture docs | High | Inspect routes in lab. |
| A17 | 1.4 | Cloud-native address allocation and quotas are provider-specific. | Official cloud networking docs | High | Verify for chosen provider if applicable. |
| A18 | 1.4 | NetworkPolicy enforcement depends on the CNI implementation/configuration. | Kubernetes docs, Network Policies | High | Verify and test chosen CNI. |
| A19 | 1.5 | IPAM behavior differs by CNI. | Selected CNI IPAM docs | High | Record chosen implementation details. |
| A20 | 1.5 | There is no universal pod limit for all Kubernetes clusters. | Kubernetes node/kubelet docs and CNI/provider docs | High | Determine limit for actual distribution/config. |
| A21 | 1.5 | `ping -M do -s` can support IPv4 MTU diagnosis on Linux where available. | `ping(8)` / iputils docs | Medium | `[VERIFY]` platform and flags. |
| A22 | 1.5 | PMTUD can be impaired when needed ICMP feedback is blocked. | IP protocol standards and Linux/network docs | High | Test exact path and address family. |
| A23 | 1.5 | Encryption in transit and authorization are distinct controls. | WireGuard/IPsec docs; Kubernetes NetworkPolicy docs | High | Verify CNI feature integration. |
| A24 | 1.5 | CNI and Service datapath responsibilities are conceptually distinct. | Kubernetes Services docs; CNI docs | High | Verify eBPF/kube-proxy replacement mode. |
| A25 | 1.6 | CNI agent failure may affect new pod setup differently from existing datapath flows. | CNI vendor failure/operations docs | Medium | `[VERIFY]` behavior for exact CNI/datapath. |
| A26 | 1.6 | CNI migration rollback may not be a simple inverse. | CNI vendor upgrade/migration docs | Medium | Verify exact migration path and state handling. |
| A27 | 1.7 | Sandbox failures, node readiness, IPAM and CNI health are useful operational signals. | Kubernetes node/events docs; CNI operations docs | High | Define local SLI and alert thresholds. |
| A28 | 1.8 | CNI agents may require elevated privileges to configure networking. | Selected CNI installation/security docs | High | Inspect exact RBAC/capabilities. |
| A29 | 1.8 | `hostNetwork` reduces network namespace isolation and can create port conflicts. | Kubernetes Pod API docs | High | Review each workload exception. |
| A30 | 1.10 | `disableDefaultCNI: true` is not assumed universally valid for every lab workflow. | kind config docs and selected CNI kind guide | High | `[VERIFY]` exact supported workflow before use. |
| A31 | 1.10 | A no-CNI cluster may remain NotReady until networking is installed. | Kubernetes node networking docs; selected CNI guide | High | Verify exact conditions and expected events. |
| A32 | 1.10 | `kubectl apply --dry-run=server` cannot prove datapath connectivity. | Kubernetes API dry-run semantics; networking separation | High | Perform live lab tests separately. |
| A33 | 1.10 | Raw packet captures may contain sensitive payloads. | General packet-capture security practice | High | Sanitize summaries and delete PCAPs. |
| A34 | 1.14 | Current installation commands and feature status are version-sensitive. | Official kind/CNI docs | High | Verify at execution time. |
| A35 | Appendix D | Local kind tests cannot establish production multi-AZ behavior. | kind topology and cloud architecture distinction | High | Record as a limitation. |

## Appendix B — Unit Audit Report

| Pass | Result (PASS/FIXED/OPEN) | Defects found | Fixes applied | Residual risk |
|---|---|---|---|---|
| 1 — Completeness | FIXED | This file covers required teaching areas and five labs, but the policy-capable CNI installation is verification-gated rather than a copy/paste install. | Added explicit official-doc selection workflow, fallback, packet paths, failure tree, questions, evidence, and appendices. | Exact live install commands remain OPEN until the learner selects a CNI/version and verifies official compatibility. |
| 2 — Technical accuracy | PASS | Implementation-specific packet paths could be overgeneralized. | Labeled diagrams conceptual and required observed routes/captures for actual path. | Exact datapath behavior must be confirmed for chosen CNI. |
| 3 — Manifest and command validity | OPEN | Image tags are placeholders and kind image pinning is not filled with a guessed version. | Clearly marked placeholders; provided dry-run and context checks. | Replace placeholders with verified pinned images and validate on target versions. |
| 4 — Official-source grounding | OPEN | No live documentation consultation was performed in this authoring step. | Stated this limitation and supplied official document titles to consult. | Human must verify canonical URLs, versions, API fields, and install steps. |
| 5 — Lab reproducibility | OPEN | Exact policy-capable CNI install commands are deliberately not guessed. | Added preflight, decision gate, pre/post readiness, traffic evidence, troubleshooting, cleanup, and fallback. | Cannot claim the policy-capable lab is copy/paste-complete until a supported CNI/version is selected and checked. |
| 6 — Safety and resource realism | PASS | CNI install and cluster deletion are high-impact operations. | Restricted them to disposable named clusters; included context guards and explicit destructive warning. | Host resource use varies; measure before installation. |
| 7 — Pedagogy and consistency | PASS | Some details depend on implementation. | Defined terms, used one data/ML running example, and separated facts from verification requirements. | Learner must avoid treating conceptual diagrams as observed evidence. |
| 8 — Independent production review | FIXED | Senior review objections: guessed versions, assumed interface names, policy false confidence, unsafe CNI replacement, universal MTU overhead, wrong runtime ownership, overclaiming test results, and WSL2 equivalence. | Each objection is explicitly qualified or covered by a verification gate. | Exact CNI, runtime, kernel, and host environment remain OPEN until inspected. |

## Appendix C — Human Verification Checklist

| Area | What to check | Official documentation location | Verification command or test | Status |
|---|---|---|---|---|
| Kubernetes/kind baseline | Supported Kubernetes node image and kind version | kind releases, configuration docs | `kind version; kubectl version --client` | OPEN |
| CNI install and compatibility | Supported kind workflow, version matrix, kernel requirements | Selected CNI official installation docs | Follow the exact documented preflight and health check | OPEN |
| Runtime/CNI lifecycle | Runtime's CNI invocation and config selection | Runtime docs + CNI spec | Inspect runtime docs and node config paths | OPEN |
| Routes and packet capture | Interfaces, routes, and capture point are correctly interpreted | Linux `iproute2`, `tcpdump` docs; CNI architecture docs | `docker exec <node> ip addr; docker exec <node> ip route` | OPEN |
| MTU/PMTUD | Actual interface MTUs, encapsulation, ICMP handling | Selected CNI MTU docs; Linux `ping(8)` | Controlled lab-only packet-size tests | OPEN |
| IPAM/CIDRs | Cluster/pod/Service ranges do not overlap; pool capacity is sufficient | Kubernetes networking docs + CNI IPAM docs | Compare node pod CIDRs, CNI allocation state, VPN/VPC plan | OPEN |
| NetworkPolicy | CNI supports and enforces the tested policy | Kubernetes NetworkPolicy docs + CNI policy docs | Controlled source/destination/port deny/allow matrix | OPEN |
| IPv4/IPv6/dual-stack | Exact Kubernetes, kind, and CNI support | Kubernetes dual-stack docs + CNI docs | Verify documented prerequisites; run dedicated test only if supported | OPEN |
| WSL2/native Linux | Kernel features, Docker network, localhost and capture differences | Microsoft WSL docs; Docker docs; kind docs | Record `uname -r`, Docker network and context details | OPEN |
| Cleanup | Disposable cluster and test resources removed | kind docs | `kind get clusters; kubectl config get-contexts` | OPEN |

## Appendix D — Known Limitations and Assumptions

- Exact Kubernetes, kind, Docker/runtime, and CNI versions are not asserted. Record them before the lab.
- No live cluster was created, and no command output or packet capture is represented as observed evidence.
- The default-kind lab is suitable for basic topology inspection but does not establish NetworkPolicy enforcement.
- The policy-capable CNI lab is gated on selecting a current officially documented kind-compatible workflow. If that workflow is not compatible with the host/kernel/resource budget, use the stated concept-only fallback and clearly mark policy enforcement as untested.
- `kind` nodes are containers. There is no real multi-AZ network, managed cloud load balancer, provider IP quota, or production underlay.
- WSL2 and Docker Desktop may add NAT boundaries and can affect `localhost`, DNS, kernel feature availability, and packet capture.
- CNI-specific interface names, routes, IPAM, tunnel type, MTU, encryption, NetworkPolicy behavior, and failure semantics are implementation/configuration-dependent.
- `hostNetwork`, IPv6/dual-stack, CNI migration, and cluster-wide configuration changes require version-specific validation.
- Full Service/kube-proxy/CoreDNS behavior is deferred to Unit 2; full NetworkPolicy design is deferred to Unit 5; ingress/mesh/load-balancing and observability are deferred to their sibling units.
- Multus is awareness only. Multi-cluster implementation is deferred to M14.
- Local laptop performance is not a production benchmark. Measure with controlled workloads and disclose confounders.

## Appendix E — CNI Architecture Decision Record Template

```markdown
# CNI Architecture Decision Record

- Status: Proposed / Accepted / Rejected / Superseded
- Date:
- Owner:
- Reviewers:
- Review date:

## Context and constraints
- Cluster environments:
- Kubernetes/runtime/kernel baseline:
- Workload types and traffic patterns:
- Resource and support constraints:
- Security/compliance requirements:

## Workload requirements
- Pod-to-pod topology:
- NetworkPolicy requirements:
- IPAM/addressing requirements:
- Observability requirements:
- Encryption requirements:
- IPv4/IPv6 requirements:
- Cloud/platform integration:

## Candidate options
1.
2.
3.

## Evaluation criteria
| Criterion | Weight or rationale | Evidence for each candidate |
|---|---|---|
| Policy enforcement | | |
| Datapath/performance methodology | | |
| IPAM and address scale | | |
| Observability/debuggability | | |
| Encryption | | |
| Kernel/runtime compatibility | | |
| Upgrade/support model | | |
| Operational/on-call burden | | |
| Cost | | |

## Evidence collected
- Official documentation and versions:
- Lab results:
- Failure tests:
- Compatibility checks:
- Open questions:

## Decision and rationale

## Alternatives rejected
- Option:
- Reason:

## Security, reliability, performance, and cost trade-offs

## Compatibility and upgrade plan
- Pinned versions:
- Staging/canary:
- Validation gates:
- Abort criteria:

## Rollback and recovery
- Preconditions:
- Exact supported recovery steps:
- Data/IPAM/CRD state risks:
- Recovery owner:

## Success criteria
- Connectivity:
- Policy:
- MTU:
- IPAM:
- Observability:
- Upgrade/rollback:

## Open verification items

## Approval and next review
```
