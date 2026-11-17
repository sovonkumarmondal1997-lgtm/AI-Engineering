# Network troubleshooting: DNS, latency and packet loss

**Stage:** Stage 2E — Production DevOps & Platform Engineering  
**Module:** M04 — Kubernetes Networking, Ingress and Service Mesh  
**Unit:** 10  
**Audience:** Learners who know Linux, TCP/IP, DNS, HTTP/TLS and basic Kubernetes objects but are new to production network troubleshooting  
**Estimated study time:** 8–12 hours, including the gauntlet  
**Budget:** Local laptop, approximately 4 CPU, 8 GB RAM and 30 GB disk; no paid cloud or public endpoint  
**Status:** `DRAFT-AUDITED` — commands, manifests and labs were not executed in this environment.

> **Evidence rule:** This lesson distinguishes documented facts, reasoned hypotheses, expected observations, illustrative output and actual observations. All sample output in this document is illustrative unless explicitly stated otherwise. No live cluster, packet capture, fault injection or benchmark was run while authoring this lesson.

## 10.0 Metadata, prerequisites and learning outcomes

### Source availability and limitations

Inspected files available in the working folder:

- `Roadmap(5).md`, including the M04 tree and unit order.
- `PROMPT-Kubernetes-Networking-Ingress-and-Service-Mesh(9).md`, the available syllabus prompt variant.
- Units 1–9 sibling lessons, including Units 2 (Services/DNS), 3 (Ingress/Gateway API), 5 (NetworkPolicy), 6 (TLS/cert-manager), 7–8 (service mesh/mTLS), and 9 (eBPF/Cilium).
- The uploaded Unit 10 generation prompt.

The roadmap places Unit 10 after eBPF/Cilium and before the M04 project/README/practice material. The sibling lessons use `ml-platform`, `model-api`, `feature-service`, DNS, policy and mesh concepts; this lesson reuses that context and refers back to the earlier units instead of re-teaching them in full.

The exact `M04-Kubernetes-Networking-Ingress-and-Service-Mesh-Copy-Paste-Prompt-Pack.md`, the M04 `Projects/README.md`, and `Projects/01-secure-ingress-and-mtls-for-data-and-ml-apis.md` were not available as separate files in the inspected workspace. The uploaded Unit 10 prompt and available syllabus control the lesson scope. No unavailable file is represented as inspected.

Official Kubernetes DNS/service debugging, kind networking, and curl documentation were consulted on 2026-10-28. Linux utility behavior and availability vary by distribution and image; specific kernel counters, `conntrack`, `tc netem`, debug ephemeral containers, ingress/Gateway APIs and mesh diagnostics remain conditional and are marked `[VERIFY]` where applicable.

### Learning outcomes

By the end of this unit, you should be able to:

1. Follow a repeatable, evidence-first troubleshooting sequence instead of running random commands or restarting components prematurely.
2. Identify which layer and network hop is most likely responsible for a symptom.
3. Diagnose Pod-to-Service failures using Service ports, selectors, EndpointSlices, readiness, DNS, policy, datapath and application evidence.
4. Investigate DNS failures involving query names, search domains, `ndots`, CoreDNS, upstream resolvers, caching and DNS egress policy.
5. Separate DNS, TCP connection, TLS handshake, time-to-first-byte and total request time.
6. Interpret HTTP 502/503/504/499 carefully and identify which hop actually emitted the status.
7. Use `curl`, `dig`, `nslookup`, `nc`, `ss`, `ip`, `traceroute`/`mtr`, `tcpdump`, `nstat`, `conntrack` and `tc` when available and appropriate.
8. Use a safe, read-only `netcheck` report script with explicit context and namespace guards.
9. Perform a local `kind` baseline test and troubleshoot controlled, reversible faults.
10. Preserve evidence, communicate impact, mitigate safely, verify recovery and produce a blameless postmortem.

### Shared running example

The platform contains:

- a FastAPI `model-api` that serves prediction requests;
- an internal `feature-service`;
- Postgres and Redis dependencies;
- an ETL worker that calls approved external APIs;
- a metrics endpoint;
- an ingress/Gateway and TLS termination path;
- an optional Linkerd or Istio mesh, selected in earlier units;
- optional Cilium/Hubble visibility only if Cilium is actually installed.

A prediction request may traverse:

```text
Client
  -> ingress / Gateway / local port mapping
  -> Service virtual IP and selected EndpointSlice endpoint
  -> optional mesh proxy / mTLS policy
  -> model-api Pod
  -> feature-service Service / Pod
  -> Redis or Postgres
  -> response back through the request path
```

A single request can fail at multiple layers. A DNS failure may look like an application timeout; a connection timeout may be caused by policy, an absent endpoint, routing or a full connection-tracking table; a 504 may be emitted by an ingress proxy while the application is still processing. The job is to locate the failing hop with evidence.

## 10.1 Why this topic matters in production

A network symptom is not a root cause. “The API is slow” could mean DNS takes 800 ms, TCP SYNs are retransmitted, TLS negotiation stalls, a proxy retries a downstream call, the backend is CPU-throttled, or the service has no ready endpoints. Restarting CoreDNS, flushing conntrack or deleting a Pod before identifying the failing layer can erase evidence and make a localized problem worse.

Production troubleshooting therefore needs three disciplines:

1. **Path reasoning:** trace the request from the client to the actual responder and back.
2. **Evidence correlation:** align timestamps, request IDs, source/destination, namespace, node, deployment revision and telemetry from each hop.
3. **Controlled change:** test one hypothesis, apply the smallest safe mitigation, verify recovery and record what would prevent recurrence.

The same discipline applies to batch ETL and model inference. A retry may mask packet loss while amplifying load. A DNS lookup delay may multiply across several dependencies. A long-lived gRPC stream may behave differently from a short HTTP request. A mesh can add useful identity and telemetry but also introduce another timeout, proxy or authorization boundary.

## 10.2 Mental model and architecture

### The practical network stack

OSI is a useful vocabulary, not a promise that every failure maps neatly to one layer.

| Layer/view | Questions | Useful evidence | Common trap |
|---|---|---|---|
| Application | Did the request reach the intended handler? Was the response valid? | App logs, request IDs, status and dependency timing | Assuming a TCP connect proves app success |
| HTTP/gRPC | Which hop emitted the status? Was the path/method correct? | `curl -v`, response headers, proxy/app logs, traces | Treating 502/503/504 as unique root-cause codes |
| TLS | Did SNI, trust chain, certificate validity and protocol negotiation succeed? | `curl -v`, `openssl s_client` if available, certificate inspection | Assuming a TCP connection proves TLS success |
| TCP/UDP | Did the handshake complete? Are there resets/retransmissions? | `ss -ti`, `nc`, `tcpdump`, socket errors | Treating ICMP behavior as a TCP verdict |
| IP/routing | Does the route exist? Is traffic asymmetric or fragmented? | `ip route`, `ip -s link`, `traceroute`/`mtr`, packet capture | Assuming traceroute displays every router |
| Kubernetes service routing | Does the Service select ready endpoints? Is the port mapping correct? | Service, EndpointSlice, Pod readiness, kube-proxy/CNI evidence | Blaming DNS when the Service has no endpoints |
| Policy/mesh | Is the flow allowed? Is mTLS/authorization consistent? | NetworkPolicy/CNP, mesh policy/status, Hubble if present | Disabling all policy as a “test” |
| Node/kernel/runtime | Are there drops, conntrack pressure, resource exhaustion or MTU issues? | Interface counters, `nstat`, `conntrack -S`, node logs/metrics | Tuning sysctls without evidence |
| External/local boundary | Is traffic traversing host ports, Docker, WSL2 NAT, firewall or load balancer? | Host route/firewall, kind port mapping, LB/controller status | Assuming `localhost` means the same endpoint everywhere |

### Request-path evidence map

```text
Workstation / client
  | DNS lookup timing
  | TCP connect timing
  | TLS handshake timing
  | first-byte and total timing
  v
Local host / WSL2 / Docker / kind port mapping
  | firewall, NAT, host port, node container
  v
Ingress / Gateway / NodePort (only if installed)
  | controller class, route acceptance, TLS/SNI, backend protocol
  v
Service
  | port -> targetPort, selector, EndpointSlices
  v
Pod / optional mesh proxy
  | readiness, listener, policy, mTLS, retries/timeouts
  v
Application -> dependency -> response
```

At every hop ask: “What would I expect to observe if this hop were healthy?” Then compare it with the failing request and a known-good request. A missing observation can mean no traffic occurred, the tool observed the wrong interface, the event was filtered, or the telemetry system was unavailable. Absence of evidence is not automatically evidence of a drop.

### Symptom, cause, contributing factor and detection gap

- **Symptom:** the user-facing observation, such as a 504 or a failed DNS lookup.
- **Root cause:** the condition that directly produced the failure, established by evidence.
- **Contributing factor:** something that increased impact, such as aggressive retries or a missing readiness gate.
- **Detection gap:** why monitoring or alerts did not identify the issue early enough.
- **Mitigation:** a change that restores service or reduces impact; it may not remove the root cause.
- **Prevention:** a change that reduces recurrence probability or shortens detection/recovery time.

Do not write “DNS caused an outage” merely because a request failed to resolve. Record the exact query, resolver, response, timestamps and affected path.

## 10.3 Core concepts and terminology

### Service, selector, ports and EndpointSlice

A Kubernetes Service gives a stable virtual endpoint for a set of Pods or another destination type. For a typical selector-based Service:

- `port` is the port clients use on the Service.
- `targetPort` is the destination port on selected endpoints.
- the selector matches Pod labels;
- EndpointSlices represent the Service's backend endpoints and readiness/conditions;
- readiness affects whether an endpoint is eligible for normal Service traffic, subject to the implementation and configuration.

A Service object can exist while having no usable endpoints. A DNS A/AAAA response for the Service IP can therefore coexist with failed application connections. Check the Service and EndpointSlices before blaming DNS.

### DNS resolution and `ndots`

Inside a Pod, `/etc/resolv.conf` commonly contains a cluster DNS server, search suffixes and `options ndots:5`, though actual values vary. Search behavior depends on the resolver implementation and query name. With `ndots:5`, a name with fewer than five dots may be tried with search suffixes before or in addition to an absolute lookup depending on resolver behavior. A short name can trigger several DNS queries. Exact ordering, parallelism, caching and retry behavior vary by libc/runtime and tool; observe the actual resolver path rather than assuming a fixed query count.

For example, from namespace `ml-platform`, a short query `feature-service` may be expanded using namespace and cluster suffixes. An explicit FQDN with a trailing dot is commonly used to request an absolute name, but validate client-library behavior in the actual application. A lookup from the workstation does not test the Pod's resolver, search path or DNS egress policy.

### Latency vocabulary

- **DNS time:** time spent resolving the requested name, when measured separately.
- **Connect time:** elapsed time to establish the TCP connection.
- **TLS time:** elapsed time for TLS negotiation, including relevant handshake steps.
- **TTFB / start-transfer time:** time until the first response byte; it includes earlier phases and server/proxy processing.
- **Total time:** time until the response completes.
- **p50 / p95 / p99:** latency percentiles; p95 means 95% of observations are at or below that value for the defined sample/window.
- **Variance:** the spread of observations; a stable median can conceal a long tail.
- **Retransmission:** TCP retransmits data when acknowledgement/transport behavior indicates loss or delay; retransmission evidence needs correlation with the path and load.
- **MTU:** maximum packet payload size supported at a link layer; headers and encapsulation reduce the available inner-packet size.
- **PMTUD:** Path MTU Discovery, a process by which endpoints discover path constraints; blocked control messages or tunnel overhead can create black-hole symptoms.
- **SNAT:** source network address translation, often used to make outbound traffic appear from a node or gateway address.
- **Conntrack:** kernel connection-tracking state used by networking/NAT/firewall paths; implementation and visibility depend on kernel/netfilter configuration.
- **SYN backlog:** pending connection-handshake state at a listening socket; pressure may appear as connection failures or retransmissions.
- **TIME_WAIT:** TCP state used after connection close to help prevent delayed segments from corrupting later connections; many entries are not automatically a fault.
- **Ephemeral ports:** temporary local ports used for outgoing connections; exhaustion can limit new connections under certain patterns.
- **Connection pooling/keep-alive:** reuse of connections to reduce setup cost; it changes the timing interpretation and can mask intermittent connection setup failures.

### Tool selection and execution location

| Tool | Run from | Use | Limitations/security |
|---|---|---|---|
| `ping` | Workstation, diagnostic Pod or node where available | Reachability/latency of ICMP echo | ICMP may be blocked/rate-limited; failure does not prove TCP is unreachable |
| `curl -v`, `curl -w` | Workstation or approved diagnostic Pod | HTTP/TLS and timing decomposition | `curl` may not exist in minimal images; verbose output can include sensitive headers |
| `dig`, `nslookup` | Workstation or Pod with the relevant resolver | DNS query and response | Different tools/libraries may follow different search/retry behavior |
| `nc` | Workstation/Pod | Bounded TCP connection check | Syntax varies by implementation; success proves only a connection, not protocol correctness |
| `ss` | Same network namespace as socket; node if authorized | Socket states and TCP details | Minimal images may lack it; output depends on kernel/tool version |
| `ip`, `ip -s link`, `ip route` | Linux host or authorized node/debug environment | Interfaces, counters and routes | Pod, node, WSL2 and Windows see different network namespaces |
| `traceroute`, `mtr` | Workstation or approved diagnostic Pod | Path clues and loss/latency patterns | Intermediate hops may filter probes or reply asymmetrically |
| `tcpdump` | Correct Pod/node/host namespace, with permission | Packet metadata and protocol exchanges | Capture can be sensitive; offload, namespace and capture point affect visibility |
| `kubectl debug` / ephemeral container | Cluster API with required RBAC and supported version/runtime | Debug a target Pod/node with approved image | Admission/security policy, runtime and version can block it; may alter Pod spec |
| netshoot-style image | Dedicated diagnostic Pod in approved namespace | Toolbox containing common network utilities | Review image provenance, tag/digest, privileges and cleanup |
| `nstat` | Linux node/host with tool available | Kernel network statistics | Counters may be global or namespace-dependent and cumulative |
| `conntrack -S` | Authorized Linux node/host with conntrack tools | Connection-tracking counters | Availability and meaning depend on `nf_conntrack`/netfilter/kernel; `[VERIFY]` |
| `tc netem` | Exact Linux network namespace/interface with sufficient privilege | Controlled delay/loss/reordering lab | Mutates traffic; wrong interface can affect unrelated workloads; syntax/support `[VERIFY]` |

## 10.4 Guided walkthrough with worked examples

### Worked example 1 — A 504 with slow first byte

Suppose a client reports HTTP 504 and a high total duration. The code alone does not tell you whether the ingress, mesh proxy, application gateway or upstream dependency emitted it.

Use a bounded, non-mutating request to the intended local/test URL:

```bash
# Location: workstation, or approved diagnostic Pod.
# Classification: READ-ONLY request; do not target a public/third-party system.
curl --connect-timeout 3 --max-time 15 -sS -o /dev/null \
  -w 'http_code=%{http_code}\nremote_ip=%{remote_ip}\nnamelookup=%{time_namelookup}\nconnect=%{time_connect}\ntls=%{time_appconnect}\npretransfer=%{time_pretransfer}\nttfb=%{time_starttransfer}\ntotal=%{time_total}\n' \
  'http://127.0.0.1:18080/'
```

Interpretation:

- `http_code` is the status observed by this curl client, not proof of which component generated it.
- `remote_ip` is the remote peer seen by curl, which may be a local port-forward or proxy.
- `namelookup` measures name resolution for this request; for a numeric loopback URL it will usually be near zero and tells you nothing about in-cluster DNS.
- `connect` is the time from start until TCP connection establishment.
- `tls` is the time until TLS handshake completion; for plain HTTP this is generally zero.
- `pretransfer` is the time until the transfer is ready to begin and includes preceding connection/TLS work.
- `ttfb` is the time until the first byte of response; it includes preceding phases and waiting for the responder.
- `total` is the overall time to complete the response.

This command has no guaranteed literal output in this lesson. Repeat the measurement and correlate it with ingress, mesh, app and dependency logs. A low `connect` with high TTFB points away from a slow TCP handshake but does not uniquely identify the application as the cause. A high `namelookup` in a real hostname test suggests inspecting the actual resolver; a numeric URL bypasses that test.

For a hostname under your control, compare a normal request with a controlled `--resolve` mapping only when you understand the effect on SNI/Host and the destination. Do not use `-k` as a default workaround: it disables certificate verification and can conceal a real TLS trust failure.

### Worked example 2 — Service resolves but connection fails

Assume `model-api` cannot connect to `feature-service.ml-platform.svc.cluster.local:8081`.

**Step 1: verify the request target and context.**

```bash
# Location: workstation. Classification: READ-ONLY.
kubectl config current-context
kubectl get namespace ml-platform
kubectl -n ml-platform get svc feature-service -o wide
kubectl -n ml-platform describe svc feature-service
kubectl -n ml-platform get endpointslice \
  -l kubernetes.io/service-name=feature-service -o wide
```

If the Service name is wrong or the namespace does not exist, stop and correct the target. Do not proceed with a guessed context.

**Step 2: compare Service port and endpoint port.**

Inspect `port`, `targetPort`, selector labels and EndpointSlice ports. If the Service forwards to 8081 but the application listens on 8080, DNS can resolve correctly while TCP fails or is reset. A named `targetPort` must match the named container port where used.

**Step 3: inspect selected Pods and listener.**

```bash
# Location: workstation via Kubernetes API; READ-ONLY.
kubectl -n ml-platform get pods --show-labels -o wide
kubectl -n ml-platform get pods -l app=feature-service
kubectl -n ml-platform describe pod <FEATURE_POD>
```

If an approved shell/tool is already available in the target Pod:

```bash
# Location: target Pod; READ-ONLY.
kubectl -n ml-platform exec <FEATURE_POD> -- sh -c 'ss -lnt 2>/dev/null || true'
```

This is only useful if `sh`/`ss` exist; a minimal container may not contain either. Do not change the app image merely to get a diagnostic tool. Use an approved ephemeral/debug container when supported, or inspect app startup logs and deployment configuration.

**Step 4: test the same path from a known-good source.**

Run one bounded request from a Pod in the correct namespace if possible, then compare a request from another namespace or a known-good Pod. Record source Pod, destination, timestamp and request ID. If one path works and another fails, compare labels/policy, node placement, mesh identity and source-specific routes.

**Step 5: inspect policy and datapath evidence.**

Review Kubernetes NetworkPolicy and any installed Cilium/mesh policies. If Cilium/Hubble is actually present, use the version-matched flow tool; otherwise do not invent Hubble output. A policy object existing does not prove enforcement, and a flow drop does not by itself identify the intended policy change.

### Worked example 3 — DNS search-path amplification

A worker makes many short-name lookups and occasionally experiences slow startup. The first question is not “Is CoreDNS broken?” but “Which names does the client actually query, against which resolver, and how many attempts happen before the application proceeds?”

```bash
# Location: target Pod or approved diagnostic Pod; READ-ONLY.
cat /etc/resolv.conf
getent hosts feature-service 2>/dev/null || true
nslookup feature-service 2>/dev/null || true
dig feature-service 2>/dev/null || true
```

Only run commands that exist in the image. `getent`, `nslookup` and `dig` may use different libraries and search behavior; they are not guaranteed to produce identical query sequences. The `resolv.conf` file shows configured nameservers, search domains and options, not necessarily every request made by the application.

Compare:
- the short name from the same namespace;
- `feature-service.ml-platform`;
- the cluster FQDN used by your cluster;
- an absolute FQDN with a trailing dot when appropriate;
- DNS query logs/metrics if already available.

Do not edit cluster-wide CoreDNS settings to solve one Pod's query behavior without evidence. Search suffixes, `ndots`, retries and application resolver behavior must be considered together.

### HTTP status codes: identify the responder

| Status | Common meaning at the emitting HTTP hop | What it does **not** prove |
|---|---|---|
| 502 Bad Gateway | A gateway/proxy reports an invalid or failed upstream interaction according to its implementation | It does not uniquely prove a crashed Pod or a bad `targetPort` |
| 503 Service Unavailable | A responder reports it cannot serve the request; may reflect no healthy backends, overload or application logic | It does not uniquely prove zero EndpointSlice endpoints |
| 504 Gateway Timeout | A gateway/proxy timed out waiting for an upstream operation | It does not prove the upstream is down; it may be slow or the timeout budget may be inconsistent |
| 499 | Commonly used by NGINX to log a client-closed request; not a standard response status defined for general HTTP semantics | It is not a universal status emitted to clients or a universal root cause |

Identify the responder using response headers, access logs, request IDs, trace spans, connection timing and the exact path. Headers can be rewritten or removed, so correlate multiple sources. Some codes are implementation-specific and version-sensitive.

## 10.5 Hands-on lab: setup, execution and evidence

### Safety and fidelity contract

- Use a new, learner-owned `kind` cluster named `m04-netdiag-lab`, with a dedicated namespace `netdiag`.
- The examples use a simple HTTP echo service to establish a known-good Service path. They do not install a mesh, Cilium, ingress controller, Gateway API controller, full observability stack or cloud load balancer.
- Do not use a shared or production context. Do not expose a public endpoint.
- All sample manifests are for training. For production, pin images by approved digest and verify image provenance.
- Commands below were authored but not executed. Check installed versions and adjust only after reviewing official documentation.
- `kind` is a local Kubernetes-in-containers environment, not a faithful multi-AZ cluster or cloud load-balancer test. On WSL2/Docker, localhost, host networking and node-container networking differ.

### Step 1 — Read-only preflight

```bash
# File: scripts/unit-10-preflight.sh
# Location: workstation. Classification: READ-ONLY.
set -euo pipefail

for cmd in docker kind kubectl; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    printf 'Missing required command: %s\n' "$cmd" >&2
    exit 10
  fi
done

uname -a
uname -r
docker version
kind version
kubectl version --client
printf 'Current context: '
kubectl config current-context || true
printf 'kind clusters:\n'
kind get clusters
```

Interpret the output as environment inventory. It does not prove the API server is reachable, that the intended cluster is disposable, or that a given CNI enforces NetworkPolicy.

### Step 2 — Create the disposable cluster

Save this as `manifests/unit-10/kind-config.yaml`:

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: m04-netdiag-lab
nodes:
  - role: control-plane
```

The configuration uses kind's documented `v1alpha4` config API and a single control-plane node. A one-node lab is sufficient for Service/selector/DNS basics but cannot demonstrate realistic cross-node paths. See the official kind configuration and quick-start pages in Section 10.14.

```bash
# Location: workstation. Classification: MUTATING.
set -euo pipefail
CLUSTER='m04-netdiag-lab'

if kind get clusters | grep -Fxq "$CLUSTER"; then
  echo "Refusing: cluster already exists; inspect it manually." >&2
  exit 20
fi
read -r -p 'Type CREATE-DISPOSABLE-NETDIAG to create a new lab cluster: ' confirm
if [[ "$confirm" != 'CREATE-DISPOSABLE-NETDIAG' ]]; then
  echo 'Cancelled.'
  exit 21
fi

kind create cluster --name "$CLUSTER" --config manifests/unit-10/kind-config.yaml
expected="kind-$CLUSTER"
actual="$(kubectl config current-context)"
if [[ "$actual" != "$expected" ]]; then
  printf 'Context mismatch: expected %s, got %s\n' "$expected" "$actual" >&2
  exit 22
fi
kubectl --context "$expected" cluster-info
kubectl --context "$expected" get nodes
```

Stop if the context is not `kind-m04-netdiag-lab`, the API server is not reachable, or cluster ownership is uncertain.

### Step 3 — Create namespace, Deployment and Service

Save as `manifests/unit-10/baseline.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: netdiag
  labels:
    purpose: m04-unit-10-lab
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: echo
  namespace: netdiag
spec:
  replicas: 1
  selector:
    matchLabels:
      app: echo
  template:
    metadata:
      labels:
        app: echo
    spec:
      containers:
        - name: echo
          image: hashicorp/http-echo:0.2.3
          args: ["-text=netdiag-ok"]
          ports:
            - name: http
              containerPort: 5678
          readinessProbe:
            tcpSocket:
              port: http
            initialDelaySeconds: 2
            periodSeconds: 5
          resources:
            requests:
              cpu: 10m
              memory: 16Mi
            limits:
              cpu: 100m
              memory: 64Mi
---
apiVersion: v1
kind: Service
metadata:
  name: echo
  namespace: netdiag
spec:
  selector:
    app: echo
  ports:
    - name: http
      port: 80
      targetPort: 5678
  type: ClusterIP
```

The readiness probe is a TCP socket check, not an HTTP semantic health check. The sample image tag is for a training example, not a production image-pinning recommendation. Verify registry availability and organizational image policy before running.

**MUTATING command — apply only to the guarded lab context:**

```bash
# Location: workstation via Kubernetes API. Classification: MUTATING.
set -euo pipefail
expected='kind-m04-netdiag-lab'
actual="$(kubectl config current-context)"
if [[ "$actual" != "$expected" ]]; then
  printf 'Refusing apply: expected %s, got %s\n' "$expected" "$actual" >&2
  exit 30
fi
read -r -p 'Type APPLY-NETDIAG-LAB to apply the sample namespace/workload: ' confirm
if [[ "$confirm" != 'APPLY-NETDIAG-LAB' ]]; then
  echo 'Cancelled.'
  exit 31
fi
kubectl --context "$expected" apply -f manifests/unit-10/baseline.yaml
kubectl --context "$expected" -n netdiag rollout status deployment/echo --timeout=120s
kubectl --context "$expected" -n netdiag get svc,endpointslice,pods -o wide
```

### Step 4 — Establish a known-good request

```bash
# Location: workstation. Classification: MUTATING local process + READ-ONLY request.
# The port-forward opens a local listener only while the command is running.
kubectl --context kind-m04-netdiag-lab -n netdiag \
  port-forward svc/echo 18080:80
```

In a second workstation terminal:

```bash
# Location: workstation. Classification: READ-ONLY HTTP request.
curl --connect-timeout 3 --max-time 10 -sS \
  -w '\nhttp_code=%{http_code} connect=%{time_connect} ttfb=%{time_starttransfer} total=%{time_total}\n' \
  http://127.0.0.1:18080/
```

Expected observation: the request should return the configured echo text and a successful HTTP status if the image starts, the Service and endpoints are correct, and the port-forward is active. This is an expectation, not an observed result. The port-forward path does not test an ingress controller, cloud load balancer, external DNS, or the normal client-to-Service datapath in all respects.

### Step 5 — Use `netcheck` (read-only by default)

Save as `scripts/netcheck.sh`:

```bash
#!/usr/bin/env bash
# netcheck.sh — bounded, read-only Kubernetes networking evidence report.
# Location: workstation with kubectl configured.
# Does not create resources, dump Secrets, or send traffic to public endpoints.
set -euo pipefail

usage() {
  cat >&2 <<'USAGE'
Usage:
  netcheck.sh EXPECTED_CONTEXT NAMESPACE SERVICE [POD_FOR_OPTIONAL_IN_POD_CHECK]

Example:
  ./scripts/netcheck.sh kind-m04-netdiag-lab netdiag echo echo-<pod-suffix>

The expected context must match exactly. Use only a cluster you are authorized
to inspect. The optional Pod check runs only if a Pod name is supplied; it
attempts safe metadata/DNS checks and gracefully reports missing tools.
USAGE
}

if [[ "$#" -lt 3 || "$#" -gt 4 ]]; then
  usage
  exit 2
fi

EXPECTED_CONTEXT="$1"
NAMESPACE="$2"
SERVICE="$3"
POD="${4:-}"

for value in "$EXPECTED_CONTEXT" "$NAMESPACE" "$SERVICE"; do
  if [[ -z "$value" ]]; then
    echo "ERROR: required arguments cannot be empty." >&2
    exit 2
  fi
done

if ! command -v kubectl >/dev/null 2>&1; then
  echo "ERROR: kubectl is required." >&2
  exit 10
fi

ACTUAL_CONTEXT="$(kubectl config current-context 2>/dev/null || true)"
if [[ -z "$ACTUAL_CONTEXT" || "$ACTUAL_CONTEXT" != "$EXPECTED_CONTEXT" ]]; then
  printf 'ERROR: context guard failed; expected=%s actual=%s\n' \
    "$EXPECTED_CONTEXT" "${ACTUAL_CONTEXT:-<unknown>}" >&2
  exit 3
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
REPORT="netcheck-${STAMP}.txt"
umask 077
: > "$REPORT"

section() {
  printf '\n===== %s =====\n' "$1" | tee -a "$REPORT"
}
run_readonly() {
  local label="$1"
  shift
  section "$label"
  if timeout 10s "$@" 2>&1 | tee -a "$REPORT"; then
    printf 'STATUS=OK label=%s\n' "$label" | tee -a "$REPORT"
    return 0
  else
    local rc="${PIPESTATUS[0]:-1}"
    printf 'STATUS=ERROR label=%s exit=%s\n' "$label" "$rc" | tee -a "$REPORT"
    return 1
  fi
}

printf 'NETCHECK REPORT\nUTC=%s\nEXPECTED_CONTEXT=%s\nNAMESPACE=%s\nSERVICE=%s\n' \
  "$STAMP" "$EXPECTED_CONTEXT" "$NAMESPACE" "$SERVICE" | tee -a "$REPORT"
printf 'Classification: READ-ONLY; no objects are created or changed.\n' | tee -a "$REPORT"

FAILURES=0
run_readonly 'cluster-info' kubectl --context "$EXPECTED_CONTEXT" cluster-info || FAILURES=$((FAILURES + 1))
run_readonly 'namespace' kubectl --context "$EXPECTED_CONTEXT" get namespace "$NAMESPACE" -o name || FAILURES=$((FAILURES + 1))
run_readonly 'service' kubectl --context "$EXPECTED_CONTEXT" -n "$NAMESPACE" get service "$SERVICE" -o yaml || FAILURES=$((FAILURES + 1))
run_readonly 'endpointslices' kubectl --context "$EXPECTED_CONTEXT" -n "$NAMESPACE" \
  get endpointslices -l "kubernetes.io/service-name=$SERVICE" -o wide || FAILURES=$((FAILURES + 1))
run_readonly 'pods-readiness-summary' kubectl --context "$EXPECTED_CONTEXT" -n "$NAMESPACE" \
  get pods -o 'custom-columns=NAME:.metadata.name,READY:.status.containerStatuses[*].ready,PHASE:.status.phase,NODE:.spec.nodeName' || FAILURES=$((FAILURES + 1))
run_readonly 'recent-events' kubectl --context "$EXPECTED_CONTEXT" -n "$NAMESPACE" \
  get events --sort-by=.lastTimestamp || FAILURES=$((FAILURES + 1))

if [[ -n "$POD" ]]; then
  section 'optional-pod-metadata'
  if timeout 10s kubectl --context "$EXPECTED_CONTEXT" -n "$NAMESPACE" \
      get pod "$POD" -o 'custom-columns=NAME:.metadata.name,PHASE:.status.phase,IP:.status.podIP,NODE:.spec.nodeName' \
      2>&1 | tee -a "$REPORT"; then
    echo 'STATUS=OK label=optional-pod-metadata' | tee -a "$REPORT"
  else
    echo 'STATUS=ERROR label=optional-pod-metadata; Pod may be absent or access denied' | tee -a "$REPORT"
    FAILURES=$((FAILURES + 1))
  fi

  section 'optional-in-pod-dns'
  echo 'The following check is best-effort and requires sh plus nslookup in the target image.' | tee -a "$REPORT"
  if timeout 10s kubectl --context "$EXPECTED_CONTEXT" -n "$NAMESPACE" exec "$POD" -- \
      sh -c 'if command -v nslookup >/dev/null 2>&1; then nslookup kubernetes.default.svc; else echo "OPTIONAL_TOOL_MISSING: nslookup"; exit 42; fi' \
      2>&1 | tee -a "$REPORT"; then
    echo 'STATUS=OK label=optional-in-pod-dns' | tee -a "$REPORT"
  else
    echo 'STATUS=LIMITED label=optional-in-pod-dns; inspect output, Pod tools, RBAC and DNS policy' | tee -a "$REPORT"
  fi
fi

section 'summary'
printf 'FAILURE_COUNT=%s\nREPORT=%s\n' "$FAILURES" "$REPORT" | tee -a "$REPORT"
if [[ "$FAILURES" -eq 0 ]]; then
  echo 'NETCHECK_STATUS=COMPLETE_WITHOUT_API_CHECK_ERRORS' | tee -a "$REPORT"
  exit 0
fi
echo 'NETCHECK_STATUS=COMPLETED_WITH_CHECK_ERRORS; inspect each section' | tee -a "$REPORT"
exit 4
```

**Safety notes for `netcheck`:**

- It is read-only by design and checks the exact current context before querying resources.
- Exit code `0` means the scripted API checks completed without reported errors; it does not prove end-to-end networking.
- Exit code `2` means invalid arguments; `3` means context guard failure; `10` means `kubectl` is missing; `4` means one or more checks reported an error.
- `timeout` is a GNU/coreutils utility and may not be present on every workstation; `[VERIFY]` availability. If absent, install an approved equivalent or remove the timeout wrapper only after review.
- The script does not print Secrets, arbitrary Pod environment variables, or packet payloads. The report may still contain internal names/IPs, so protect and redact it before sharing.
- `kubectl exec` is optional and requires RBAC plus an existing Pod. It does not create a debug Pod. The DNS command may be unavailable in a minimal image.
- Run `chmod 700 scripts/netcheck.sh` and execute it from a protected working directory. The script itself was not executed during authoring.

### Step 6 — Cleanup

**DESTRUCTIVE:** delete only the dedicated namespace and/or explicitly named disposable kind cluster after checking context. Do not delete broad namespaces or CRDs.

```bash
# Location: workstation. Classification: DESTRUCTIVE.
set -euo pipefail
expected='kind-m04-netdiag-lab'
actual="$(kubectl config current-context)"
if [[ "$actual" != "$expected" ]]; then
  printf 'Refusing cleanup: expected %s, got %s\n' "$expected" "$actual" >&2
  exit 40
fi
read -r -p 'Type DELETE-NETDIAG-NAMESPACE to remove only namespace netdiag: ' confirm
if [[ "$confirm" != 'DELETE-NETDIAG-NAMESPACE' ]]; then
  echo 'Cancelled.'
  exit 41
fi
kubectl --context "$expected" delete namespace netdiag --wait=true
kubectl --context "$expected" get namespace netdiag
```

The final `get` should report that the namespace is absent; if it still exists, inspect deletion status rather than repeatedly issuing delete commands. If you want to remove the whole lab, confirm the exact kind cluster name and use the kind cluster deletion command only after explicit confirmation. Deleting the cluster removes all its resources.

## 10.6 Validation, expected results and interpretation

### Evidence ladder

1. **Target identity:** correct context, namespace, Service and intended destination.
2. **Kubernetes object state:** Service ports/selectors, EndpointSlices, Pod readiness and events.
3. **Name resolution:** actual Pod resolver configuration, query name/type, answer/rcode and resolver.
4. **Transport:** TCP connection, socket state, reset/timeout, retransmissions and interface counters.
5. **TLS:** SNI, certificate validity/chain/trust, ALPN and mTLS identity/policy when relevant.
6. **HTTP/application:** response code, headers, request ID, application logs and dependency timings.
7. **Policy/routing:** NetworkPolicy/CNI/mesh policy, route, node datapath and ingress/service implementation.
8. **Recovery:** same request succeeds after the smallest safe fix, negative test remains blocked if intended, and telemetry reflects recovery.

### Expected observations, not guaranteed output

| Check | Expected observation | What it establishes | What it does not establish |
|---|---|---|---|
| Service exists | API returns Service details | Name and spec are present | Backend endpoints exist |
| EndpointSlice has ready endpoints | One or more backend addresses/conditions are listed | Kubernetes has endpoint records for the Service | The process is listening or application is healthy |
| DNS query succeeds | Resolver returns an address or valid record | The tested name/query/resolver path worked at that time | TCP or HTTP connectivity works |
| TCP connect succeeds | Connection to the tested IP/port is established | A listener/path accepted the connection | TLS, HTTP, auth or business operation succeeds |
| TLS handshake succeeds | Client completes trust/protocol negotiation | Tested TLS endpoint accepted the handshake | mTLS authorization to a downstream service works |
| `curl` succeeds | Client received the expected response | One tested end-to-end path worked | All clients, replicas or payload sizes work |
| `ss -ti` shows retransmissions | TCP reports retransmission-related details if supported | A socket has transport-level evidence worth correlating | The root cause is necessarily physical packet loss |
| `ip -s link` shows drops | Interface counters report drops | Some packets were dropped at that interface/counter | All drops relate to this incident |
| `tcpdump` sees SYN but no SYN-ACK | Capture point observed an unanswered handshake attempt | Useful evidence for a path/listener/filter hypothesis | The destination never received it unless capture points prove that |
| Hubble reports a drop | Cilium flow visibility reports a drop if enabled | Evidence at the observed Cilium path | Hubble exists in every cluster or captures every flow |

### Reading a symptom without overclaiming

A TCP connect timeout differs from a connection reset. A timeout may indicate dropped packets, an unreachable path, no response, or a filtered return path. A reset suggests a TCP RST was received or generated along the path, but the responsible hop still needs identification. A TLS certificate error occurs after TCP connectivity and points to a different phase. A slow TTFB after fast DNS/connect may point to server/proxy processing or an upstream dependency, but timing alone does not establish which component is slow.

### DNS evidence checklist

- Record the exact queried name and record type.
- Capture which resolver is queried and whether the name is short, partially qualified or absolute.
- Inspect Pod `/etc/resolv.conf` and search/`ndots` options.
- Check CoreDNS Pod health, Service and EndpointSlices.
- Correlate query logs/metrics if already enabled; do not casually edit CoreDNS just to turn on logging in a shared cluster.
- Review DNS egress policy over UDP and TCP 53 as applicable to the implementation and workload.
- Check cache TTL, negative caching, retries and upstream forwarding.
- Compare the same query from a known-good Pod and the failing Pod.
- Verify whether the application uses the OS resolver, a language-specific DNS client, a sidecar or a custom resolver.

## 10.7 Security, reliability and failure modes

### Diagnostic access is privileged access

Debugging often tempts engineers to create a privileged Pod, use host networking, install arbitrary packages or disable NetworkPolicy. These actions can expand the incident blast radius and bypass the very controls being diagnosed.

Use this order:

1. Existing application metrics/logs and Kubernetes object inspection.
2. Approved diagnostic Pod in a dedicated namespace, with minimal permissions and a known image.
3. Ephemeral container or node debug workflow only if supported, approved and required.
4. Host-level capture or privileged inspection only under a time-bounded incident procedure with explicit approval.

`kubectl debug` support depends on Kubernetes version, target type, container runtime and RBAC/admission configuration. A debug image may not inherit the target container's network namespace in the way you expect unless the chosen mode supports it. Review the official docs and cluster policy first. Never use privileged host access as a casual workaround.

### Packet captures are sensitive

A packet capture can contain internal IPs, DNS names, TLS metadata, tokens in unencrypted protocols, cookies or payload data. Encrypted TLS application payload is not ordinarily readable as plaintext in a standard packet capture, but metadata can still be sensitive. TLS 1.3 and encrypted-client-hello capabilities can reduce what is visible to a passive observer. Use short captures, narrow filters, restrictive file permissions, approved storage and retention limits. Do not upload raw production pcaps to a ticket or chat without review and redaction.

Example safe capture patterns (only with authorized access and correct interface):

```bash
# Location: authorized Linux node/host or diagnostic namespace.
# Classification: READ-ONLY capture, but creates a sensitive local file.
# [VERIFY] tcpdump availability, interface name, privileges and platform syntax.
umask 077
timeout 15s tcpdump -ni <INTERFACE> -c 200 \
  'udp port 53 or tcp port 53' -w dns-small-capture.pcap
```

```bash
# TCP handshake to one known test host and port.
# Location: authorized capture point. READ-ONLY capture; sensitive artifact.
timeout 15s tcpdump -ni <INTERFACE> -c 200 \
  'host <TEST_IP> and tcp port <TEST_PORT> and (tcp[tcpflags] & (tcp-syn|tcp-ack|tcp-rst) != 0)' \
  -w tcp-handshake.pcap
```

```bash
# TLS handshake metadata for one test destination; not plaintext application data.
# Location: authorized capture point. READ-ONLY capture; sensitive artifact.
timeout 15s tcpdump -ni <INTERFACE> -c 200 \
  'host <TEST_IP> and tcp port 443' -w tls-metadata.pcap
```

`<INTERFACE>`, `<TEST_IP>` and `<TEST_PORT>` are placeholders. Verify the BPF filter syntax for the installed tcpdump/libpcap version. The TCP bit filter may not be portable to every build; if unsupported, use a simpler host/port filter and inspect packets offline with approved tools. `-c` and `timeout` bound capture duration/packet count, but not every environment guarantees a strict file-size bound. Confirm file size and remove artifacts according to policy. Do not capture on `any` without understanding duplicate/encapsulation visibility.

### `ping`, `traceroute` and `mtr` limitations

- ICMP echo can be blocked, rate-limited or deprioritized. A failed `ping` does not prove a TCP service is unreachable.
- `traceroute` may use UDP, ICMP or TCP depending on implementation/options. Intermediate routers may not reply, and asymmetric routing can make the displayed path incomplete.
- `mtr` samples path behavior over time but is not a definitive loss measurement for the application path. Loss at an intermediate hop that does not continue to later hops can indicate rate-limited ICMP responses rather than forwarded traffic loss.
- Always pair path tools with a test of the actual destination protocol and port.

### `ss`, retransmissions and interface counters

Use `ss -ti` for supported TCP socket details, for example:

```bash
# Location: Linux host or same network namespace as the socket.
# Classification: READ-ONLY. Requires ss/iproute2 and suitable permissions.
ss -ti dst <TEST_IP>
ss -tan state syn-sent
ss -tan state time-wait
```

The exact fields vary by kernel and iproute2 version. Retransmission-related counters on a socket can indicate trouble on the connection but need time correlation with packet captures and application logs. Large `TIME_WAIT` counts can be normal for high connection churn. Investigate whether connection pooling/keep-alive is appropriate before changing kernel settings.

```bash
# Location: Linux host/node; READ-ONLY.
ip -s link
ip route
nstat -az
```

`ip -s link` shows per-interface counters exposed by the kernel. `nstat` displays network statistics available to that build/kernel; counters may be cumulative and may not be isolated to one Pod. Record a before/after interval rather than attributing a lifetime counter to a single incident.

### Conntrack and SNAT

Conntrack pressure can contribute to dropped new connections or NAT failures, but the symptoms depend on the datapath and platform. `conntrack -S` may expose counters if the conntrack userspace tool and relevant kernel interfaces are available. `nf_conntrack` modules, sysctls, namespaces and counter meanings vary; mark them `[VERIFY]` and inspect the platform's official kernel/distribution documentation.

```bash
# Location: authorized Linux node/host; READ-ONLY.
# [VERIFY] conntrack package, kernel/netfilter support and privileges.
conntrack -S
```

Do not intentionally exhaust conntrack or change `nf_conntrack_max` as a lab. Instead inspect documented metrics, compare current usage with supported capacity and use a simulated/output-analysis exercise. Do not flush the conntrack table as a first-line fix; that can disrupt many active connections.

### MTU and PMTUD

MTU-related failures can be selective: small requests succeed while large payloads or TLS handshakes stall. Tunnels and overlays add headers and reduce the effective inner MTU. PMTUD depends on network feedback; blocked ICMP “fragmentation needed” or Packet Too Big messages can create a black hole. Check interface MTUs, tunnel configuration and packet evidence at relevant hops. Do not randomly lower MTU across nodes.

### `tc netem` is optional controlled fault injection

`tc netem` can emulate delay, loss, duplication or reordering on a Linux interface. It is not part of the required core lab. The wrong interface or namespace can impair the host or unrelated workloads. Exact syntax and privileges are platform-sensitive `[VERIFY]`.

If performing an optional experiment, use only a disposable Linux namespace or a dedicated kind node with a documented procedure. Inspect the current qdisc before mutation, apply a small impairment to the exact target interface, run a bounded local test, and restore the original qdisc exactly. If the original qdisc state cannot be captured and restored, do not run the experiment; use the analysis-only worksheet instead. No `tc netem` command is required to pass this unit.

### Timeout ladders, retries and long-lived connections

A request can have timeouts at the client, ingress, mesh, application and downstream dependency. The values need a coherent budget. If a client deadline is 10 seconds, the ingress waits 30 seconds, and the application retries a downstream call three times with its own 8-second timeout, the user may disconnect while work continues. This can create wasted compute and retry amplification.

Design the timeout ladder from the outer request budget inward:
- client total deadline;
- ingress/Gateway upstream timeout;
- mesh route/request timeout and retry budget;
- application request deadline;
- downstream database/feature-service timeout;
- cleanup/cancellation behavior.

Do not assume every component's timeout has the same semantics. Some apply to idle time, some to connect time, some to total request time, and some to each retry. gRPC streams and server-sent events need separate idle/maximum-duration considerations. Unit 8 covers retries and circuit breaking in depth.

## 10.8 Observability and performance methodology

### Metrics, logs, traces and flow evidence

| Signal | Best for | Cannot prove alone |
|---|---|---|
| Metrics | Rates, error percentages, saturation, latency distributions, DNS query rates, connection counts | Why one request failed without correlated detail |
| Logs | Event details, status, errors, configuration transitions | Complete request path if logs are missing or uncorrelated |
| Traces | Parent/child timing across ingress, app and dependency | Packets were delivered or every span was sampled |
| Packet capture | Actual packets at one capture point, handshake/retransmission clues | Full path behavior from one interface; TLS plaintext |
| Hubble (only if Cilium exists) | Observed flow context/verdicts in supported paths | All flows were observed or application logic succeeded |
| Kubernetes events/status | Scheduling, readiness, controller and resource changes | End-to-end application reachability |
| Synthetic probes | User-like test path and recurring availability/latency | All clients, regions, payloads or backends behave identically |

Correlate by UTC timestamp, request ID/trace ID, source/destination, namespace, Pod revision and endpoint. Clock skew between nodes and systems can make event ordering misleading; use synchronized clocks and record timestamp precision.

### Synthetic probes and health checks

- A **synthetic probe** exercises a defined path at a controlled interval and records latency/error.
- A **readiness probe** controls whether a Pod should receive normal Service traffic.
- A **liveness probe** asks whether the container should be restarted under the configured failure policy.
- A **startup probe** can delay liveness/readiness evaluation while an application starts.

A readiness check should verify the conditions required to serve traffic, not necessarily every downstream dependency if that would create cascading endpoint removal. A liveness probe should not restart a process merely because a remote dependency is temporarily slow. M03 covers probe design and workload recovery; here, use probes as evidence rather than treating every failed probe as proof of a network problem.

A DNS canary should query a representative internal name using the resolver path relevant to the application and alert on failure/latency. It should not generate unbounded query volume or depend solely on a public endpoint.

### Performance diagnosis method

1. Define the symptom and SLI: e.g., p95 request latency or DNS resolution error rate.
2. Capture baseline under representative, bounded load.
3. Segment time into DNS, connect, TLS, TTFB, app and dependency phases where telemetry supports it.
4. Compare a known-good path with the failing path using the same payload and concurrency.
5. Repeat measurements; record p50/p95/p99, sample count, variance, warm-up and duration.
6. Inspect errors/drops, CPU throttling, memory pressure, connection pool saturation and backend latency.
7. Change one variable at a time and repeat.
8. State limitations and confounders.

A single slow request is a clue, not a latency distribution. Percentiles require enough samples and a clearly defined aggregation window. Do not compare p95 from different time windows, request types or sample sizes without qualification.

### Evidence-to-action mapping

| Observation | Next discriminating test |
|---|---|
| DNS slow, connect fast after resolution | Compare actual query path, search expansion, CoreDNS/upstream timings and cache behavior |
| DNS succeeds, TCP connect times out | Test destination port, endpoints, policy, route and SYN/SYN-ACK visibility |
| TCP connects, TLS fails | Inspect SNI, certificate chain/expiry, ALPN, trust bundle and mTLS policy |
| Connect/TLS fast, TTFB high | Correlate ingress/mesh/app/dependency spans and logs |
| Small request works, large payload stalls | Compare MTU/PMTUD, proxy buffering/limits, body size and capture evidence |
| Same Service works from one Pod but not another | Compare namespace, labels, policy, mesh identity, node placement and resolver config |
| Only external path fails | Inspect ingress/Gateway, LB/NodePort, firewall, host mappings, SNI and externalTrafficPolicy |
| Latency increases with concurrency | Inspect queues, CPU throttling, connection pool, retry amplification, downstream saturation and drops |

## 10.9 Troubleshooting decision tree

### Decision tree A — Pod to Service failure

```text
Pod cannot reach Service
  |
  +-- 1. Correct context, namespace, Service name and port?
  |       +-- No -> correct target; do not mutate yet
  |       +-- Yes
  |
  +-- 2. Service port/targetPort and selector correct?
  |       +-- No -> compare manifest with live Service/Pod labels
  |       +-- Yes
  |
  +-- 3. EndpointSlice has ready endpoint(s)?
  |       +-- No -> inspect selectors, readiness, rollout and Pod state
  |       +-- Yes
  |
  +-- 4. Process listens on targetPort?
  |       +-- No/unknown -> inspect app startup/listener evidence
  |       +-- Yes
  |
  +-- 5. Does DNS resolve from the source Pod?
  |       +-- No -> inspect resolv.conf, CoreDNS, Service and DNS policy
  |       +-- Yes
  |
  +-- 6. Does TCP connect work to Service IP and endpoint IP?
  |       +-- Service IP fails, endpoint IP works -> service datapath/config hypothesis
  |       +-- Both fail -> policy, routing, listener, MTU or node path
  |       +-- TCP works -> TLS/mesh/auth/application layer
  |
  +-- 7. Compare same path from a known-good Pod and inspect logs/traces
```

Evidence order matters. DNS can resolve a Service IP even when the Service has no ready endpoints. A direct Pod-IP test may bypass the Service load-balancing path and is diagnostic only, not a production workaround.

### Decision tree B — Internal success, external failure

```text
Internal Service request succeeds; external URL fails
  |
  +-- Is an ingress/Gateway controller actually installed?
  |      +-- No -> external path is not configured; do not assume Ingress is implemented
  |      +-- Yes
  |
  +-- Is the IngressClass/GatewayClass/controller association correct?
  +-- Is the route accepted/programmed according to this controller's status model?
  +-- Does backend Service have ready EndpointSlice endpoints?
  +-- Is backend protocol/port correct?
  +-- Is LB/NodePort/externalTrafficPolicy path configured for this environment?
  +-- Does host/port mapping reach the intended kind node?
  +-- Does TLS SNI select the expected certificate/route?
  +-- Which hop emits the observed 502/503/504?
```

In kind, an ingress controller or Gateway implementation must be installed separately. `extraPortMappings` map host ports to kind node container ports; they are not equivalent to a cloud load balancer. On WSL2/Docker, test the Windows host, WSL distribution, kind node container and Pod as separate boundaries. Keep any port mapping bound to loopback for a local-only lab.

### Decision tree C — DNS error

```text
Name lookup fails or is slow
  |
  +-- Exact query name/type and resolver known?
  |      +-- No -> record Pod /etc/resolv.conf and reproduce same query
  |      +-- Yes
  |
  +-- Is name correct for the Service namespace/FQDN?
  +-- Does resolver return NXDOMAIN, SERVFAIL, timeout, or an address?
  +-- Is cluster DNS Service present with ready EndpointSlices?
  +-- Are CoreDNS Pods healthy and receiving the query?
  +-- Is upstream forwarding healthy for external names?
  +-- Does egress policy permit DNS over required transport?
  +-- Are search suffixes/ndots causing excess queries?
  +-- Are caching/TTL/negative caching or custom resolver paths relevant?
```

Interpret DNS outcomes carefully: NXDOMAIN is a negative answer for the queried name; SERVFAIL indicates the server could not complete the query; timeout means no response arrived within the client wait, which could reflect packet loss, filtering, server load or a return-path issue. Confirm exact response semantics from the tool output and resolver implementation.

### Decision tree D — Reset, timeout, packet loss or path-specific failure

1. Determine whether failure occurs during DNS, TCP connect, TLS handshake, first byte or response body.
2. Record whether the symptom is timeout, reset, refusal, certificate error, HTTP error or application error.
3. Compare small versus large payloads, short versus long-lived connections, and same-node versus cross-node path if safely available.
4. Check listener, EndpointSlices, readiness, policy and recent rollout.
5. Inspect socket state/retransmissions and interface counters where permitted.
6. Check MTU/PMTUD, SNAT/conntrack, ephemeral ports and SYN backlog only with evidence.
7. Correlate CPU throttling, memory pressure, mesh retries, connection pool and downstream latency.
8. Stop and escalate if diagnosis requires broad node changes, privileged access or risky host-level fault injection.

### Symptom table: top three causes and first useful command

| Symptom | Top three plausible causes | First useful command |
|---|---|---|
| Service DNS resolves but request fails | Wrong targetPort/listener; no ready endpoints; policy/datapath block | `kubectl -n <NAMESPACE> get svc,endpointslice,pods -o wide` |
| `curl` says connection refused | No listener; wrong targetPort; active reject/reset by a hop | `kubectl -n <NAMESPACE> describe svc <SERVICE>` |
| `curl` times out | Dropped/filtered path; no response from backend; MTU/conntrack/overload | `curl -v --connect-timeout 3 --max-time 10 <LOCAL_TEST_URL>` |
| DNS `NXDOMAIN` | Wrong name/namespace; missing Service/record; negative cache | `kubectl -n <NAMESPACE> get svc <SERVICE>` plus exact query |
| DNS timeout | CoreDNS unavailable/overloaded; DNS egress blocked; path/return packet loss | `kubectl -n kube-system get pods,svc,endpointslice` |
| 502 | Upstream connect/protocol failure; no usable backend; proxy configuration | Inspect response headers and the emitting proxy's access/error log |
| 503 | No healthy backend; overload; app intentionally unavailable | `kubectl -n <NAMESPACE> get endpointslice,pods` |
| 504 | Upstream too slow; inconsistent timeout ladder; dependency delay | Compare curl timing with ingress/mesh/app/dependency logs |
| Large request stalls | MTU/PMTUD; proxy body/buffering limit; backend processing | Compare small/large requests and inspect phase timings |
| Intermittent resets | Pod rollout/termination; connection reuse/backend churn; policy/firewall/device reset | `kubectl -n <NAMESPACE> get pods -o wide` and correlated logs |
| Only one source Pod fails | Different labels/policy/identity; node path; resolver config | Compare source Pod labels, node and `/etc/resolv.conf` |
| High p99 with normal p50 | Queueing; retries; one slow dependency/endpoint | Correlate request traces and endpoint-level latency |

## 10.10 Production operations and runbooks

### Standard troubleshooting runbook

1. **Impact:** record start time, detection source, affected users/services, request rate and severity.
2. **Scope:** identify cluster/context, namespace, node, workload revision, source/destination, protocol/port and affected paths.
3. **Known-good comparison:** find a path that works with the same request shape; record what differs.
4. **Evidence:** gather timestamps, request IDs, status headers, Service/EndpointSlice, Pod readiness, events, logs, traces, resolver config and network evidence appropriate to the hypothesis.
5. **Hypotheses:** rank likely causes by evidence and state a test that would falsify each.
6. **Action classification:** label every command read-only, mutating or destructive; obtain approval before mutation.
7. **Mitigation:** apply the smallest reversible change; preserve the prior state and define a rollback condition.
8. **Verification:** rerun a bounded positive test and relevant negative/security test; confirm latency/error recovery over a defined window.
9. **Communication:** send concise updates with impact, current hypothesis, evidence, mitigation and next update time.
10. **Prevention:** create a postmortem with root cause, contributing factors, detection gaps, owners and due dates.

### Incident record template

```text
Incident ID:
Severity / incident commander:
Start time UTC / detection time UTC:
Affected users, services and regions:
Current context / cluster / namespace:
Known-good path:
Failing path:
Recent changes (deployment, policy, DNS, cert, node, CNI, mesh):
Observed symptom and exact error/status:
Request IDs / trace IDs:
Evidence files and timestamps:
Hypotheses ranked by evidence:
Commands run (location + READ-ONLY/MUTATING/DESTRUCTIVE):
Mitigation and approval:
Rollback condition and owner:
Verification results (positive + negative tests):
Communication timeline:
Root cause:
Contributing factors:
Detection gaps:
Prevention actions / owner / due date:
```

### Illustrative-only incident narrative: DNS policy regression

**This is a fictional training example, not a real incident or measured result.**

- 09:00 UTC: a policy change is deployed to an ETL namespace. ETL workers begin timing out before external API requests.
- 09:04 UTC: application logs show name-resolution timeout errors; no external API response is recorded.
- 09:07 UTC: the team confirms the workload is Ready and its local health endpoint responds. This rules out neither DNS nor outbound egress.
- 09:10 UTC: `resolv.conf` shows the expected cluster resolver. The DNS Service and EndpointSlices are present.
- 09:14 UTC: policy review shows the new egress policy allows the application destination but omitted the required DNS path. A controlled DNS query from the ETL Pod fails while the same query from a known-good diagnostic Pod succeeds.
- 09:18 UTC: the approved rollback restores the previous policy. The team tests the DNS name, performs one bounded request to the controlled endpoint and verifies the application logs show successful resolution.
- 09:30 UTC: the team keeps the service under observation and records the missing DNS dependency in the policy test matrix.

**Reasoning:** the evidence ties symptom onset to a policy change, demonstrates a source-specific DNS failure, and confirms recovery after rollback. The conclusion would be weaker if the only evidence were “ETL started working after a restart.” Prevention actions include explicit DNS tests in policy CI, a reviewed egress dependency inventory and an alert for resolver failures. Do not copy this narrative into a real postmortem without replacing every fictional fact with evidence.

### Postmortem template

```text
Title:
Date / duration:
Summary:
Customer and internal impact:
Detection and response:
Timeline (UTC):
What went well:
What made response harder:
Root cause (evidence-backed):
Contributing factors:
Why existing safeguards did not prevent/detect it:
Corrective actions (owner, due date, success criterion):
Preventive tests/alerts/runbooks:
Residual risks:
Follow-up review date:
```

Avoid blame-oriented statements such as “operator forgot DNS.” Prefer system-focused findings: “The policy validation workflow did not test DNS from the selected workload, so a required dependency was omitted without detection.”

## 10.11 Design choices, trade-offs and alternatives

### Which diagnostic location should you use?

- **Workstation:** useful for local port mapping, client timing, local resolver and host firewall. It does not automatically reproduce a Pod's resolver or network namespace.
- **Application Pod:** best for the actual runtime's resolver, DNS libraries, connection pools and source-specific policy; may lack tools.
- **Dedicated diagnostic Pod:** useful for a controlled toolbox, but its labels, identity, namespace and node may differ from the failing workload. A successful probe does not prove the application Pod path works.
- **Ephemeral debug container:** useful when permitted and supported; can share aspects of a target Pod's namespaces depending on mode. It changes the Pod's debug state and requires RBAC/admission approval.
- **Node:** useful for interface, route, kernel and host datapath evidence; requires elevated access and carries greater risk.
- **External client:** useful for ingress/TLS/LB behavior, but should be an approved controlled endpoint. No public/third-party probing is required by this lesson.

### Choosing tools by hypothesis

| Hypothesis | Minimum useful evidence | Escalate to |
|---|---|---|
| Wrong Service configuration | Service spec, labels, EndpointSlice | Pod listener, datapath/policy |
| DNS name/search issue | Pod resolver config and exact query | CoreDNS/upstream logs and DNS packet capture |
| TCP path problem | Bounded `nc`/curl connect test, endpoint state | `ss`, `tcpdump`, route/interface counters |
| TLS problem | `curl -v`, cert chain/SNI inspection | ingress/mesh TLS logs, packet metadata |
| Packet loss/MTU | Repeated request timing, socket counters, MTU config | bounded packet captures and controlled test |
| Conntrack/SNAT pressure | platform metrics and documented counters | authorized node-level conntrack evidence |
| Application/dependency delay | traces, app/dependency logs and phase timing | profiling/load test under approved scope |

### `kind` fidelity limits

- The default kind network plugin may not enforce Kubernetes NetworkPolicy; policy exercises must first verify that the selected CNI enforces it.
- A LoadBalancer Service does not automatically provide a cloud load balancer. Local helpers may be required and are out of scope for the core lab.
- `extraPortMappings` forward ports between host and kind node containers; they are not equivalent to cloud ingress.
- A one-node lab cannot model real multi-node or multi-zone paths.
- WSL2/Docker adds NAT and distinct host/network namespaces. `localhost` from Windows, WSL2, kind node and Pod are different contexts.
- CoreDNS, ingress/Gateway controllers, mesh proxies, Cilium/Hubble, `conntrack`, `tc` and node debug access are not assumed installed.

### Choosing a safe fault-injection method

Prefer a reversible Kubernetes object change in the disposable namespace, such as a wrong Service port or selector, because the effect is bounded and visible. Use policy denial only if the installed CNI actually enforces NetworkPolicy. Use illustrative analysis for ingress/Gateway/mTLS features that are not installed. Avoid host-level `tc netem`, conntrack exhaustion, DNS loop injection or broad node mutation in this constrained lab.

## 10.12 Exercises and knowledge checks

### Troubleshooting gauntlet: learner-facing challenges

**Instructions:** Attempt each challenge before opening the answer key below. Use only `kind` cluster `m04-netdiag-lab` and namespace `netdiag` for mutating exercises. If the required controller, CNI feature or tooling is not installed, use the stated analysis-only route; do not install a large stack just to complete a challenge.

For each scenario, submit:
1. symptom and impact;
2. current context, namespace and path;
3. at least three pieces of evidence;
4. hypotheses ranked by evidence;
5. smallest safe fix;
6. a positive recovery test and a relevant negative test;
7. prevention/control;
8. cleanup/restoration proof.

**Scoring rubric per scenario (10 points):** scope/context (1), evidence before mutation (2), plausible ranked hypotheses (2), smallest safe fix (2), verification and cleanup (2), honest fidelity/limitations (1). A correct guess without evidence earns limited credit.

#### Challenge G01 — Wrong Service `targetPort`

- **Initial symptom:** Service exists and a Pod appears Ready, but a request to the Service fails.
- **Hint 1:** Compare the Service port and `targetPort`.
- **Hint 2:** Compare that port with the actual process listener/container port.
- **Hint 3:** Check EndpointSlice port information before inspecting packet captures.
- **Diagnostic commands:** `kubectl -n netdiag get svc echo -o yaml`; `kubectl -n netdiag get endpointslice -l kubernetes.io/service-name=echo -o yaml`; inspect the Deployment.
- **Evidence required:** before/after Service port mapping, endpoint ports, bounded request result.
- **Fidelity:** simulated local reproduction, if the learner changes only the disposable lab Service.

#### Challenge G02 — Service selector mismatch

- **Initial symptom:** Service exists, but no backend is selected.
- **Hint 1:** Compare `spec.selector` with Pod labels.
- **Hint 2:** Do not confuse a Deployment selector with the Service selector.
- **Hint 3:** EndpointSlice evidence should show whether endpoints are selected.
- **Diagnostic commands:** `kubectl -n netdiag get svc echo -o yaml`; `kubectl -n netdiag get pods --show-labels`; inspect EndpointSlices.
- **Evidence required:** selector/label diff and request outcome.
- **Fidelity:** simulated local reproduction.

#### Challenge G03 — Missing or unready EndpointSlice endpoints

- **Initial symptom:** Requests fail intermittently or no backend appears eligible.
- **Hint 1:** Inspect Pod readiness and rollout state.
- **Hint 2:** Check EndpointSlice addresses and conditions.
- **Hint 3:** A running container is not always a ready Service endpoint.
- **Diagnostic commands:** `kubectl -n netdiag get pods -o wide`; `kubectl -n netdiag describe pod <POD>`; inspect EndpointSlices/events.
- **Evidence required:** readiness state, events, endpoint conditions and bounded request.
- **Fidelity:** simulated local reproduction; scale or readiness mutation only in the lab.

#### Challenge G04 — Default-deny policy forgot DNS egress

- **Initial symptom:** name-based access fails after an egress policy change; direct access may behave differently.
- **Hint 1:** Inspect all applicable NetworkPolicy resources.
- **Hint 2:** Confirm the CNI actually enforces NetworkPolicy before interpreting the result.
- **Hint 3:** Test the cluster DNS name from the affected workload and inspect UDP/TCP 53 rules.
- **Diagnostic commands:** `kubectl -n netdiag get networkpolicy`; inspect Pod `/etc/resolv.conf`; query a local Service name.
- **Evidence required:** CNI identity/enforcement evidence, policy manifest and DNS test.
- **Fidelity:** simulated local reproduction only if enforcement is verified; otherwise read-only analysis. Do not install a new CNI just for this challenge.

#### Challenge G05 — `ndots` / search-domain query amplification

- **Initial symptom:** DNS query volume or lookup latency appears unexpectedly high.
- **Hint 1:** Read `/etc/resolv.conf` from the affected Pod.
- **Hint 2:** Compare short name, namespace-qualified name and absolute FQDN.
- **Hint 3:** Different resolver implementations can issue different sequences; observe rather than assume a fixed count.
- **Diagnostic commands:** `cat /etc/resolv.conf`; available `dig`, `nslookup` or `getent`; CoreDNS telemetry if already enabled.
- **Evidence required:** query names/results/timing, resolver implementation, search suffixes and options.
- **Fidelity:** read-only analysis or simulated local comparison.

#### Challenge G06 — MTU mismatch / large-payload stall

- **Initial symptom:** small requests work but a large request stalls or times out.
- **Hint 1:** Compare request sizes and whether the failure starts after TLS/connect.
- **Hint 2:** Inspect interface/tunnel MTUs and PMTUD-related evidence.
- **Hint 3:** Do not change host MTU or run `tc` on an unknown interface.
- **Diagnostic commands:** `ip link`; `ip -s link`; bounded curl comparisons; packet-capture review if authorized.
- **Evidence required:** payload-size comparison, MTU path, capture location and limitations.
- **Fidelity:** read-only analysis by default. Optional `tc` experiment only with verified namespace/interface, saved qdisc state and exact cleanup `[VERIFY]`.

#### Challenge G07 — Wrong `IngressClass` or controller mismatch

- **Initial symptom:** internal Service works, but local external/ingress request fails or reaches the wrong controller.
- **Hint 1:** Confirm an ingress controller exists.
- **Hint 2:** Inspect IngressClass and the resource's class reference.
- **Hint 3:** Check controller events/logs and the actual host/port mapping.
- **Diagnostic commands:** `kubectl get ingressclass`; `kubectl -n <NAMESPACE> get ingress -o yaml`; controller Pod/events only if present.
- **Evidence required:** controller presence, class name, route/backend state and local request path.
- **Fidelity:** read-only analysis unless a controller is already installed; no controller installation required.

#### Challenge G08 — Unaccepted `HTTPRoute`

- **Initial symptom:** a Gateway API route exists but traffic does not reach the backend.
- **Hint 1:** Check whether Gateway API CRDs and a compatible controller exist.
- **Hint 2:** Inspect `parentRefs`, listener/route attachment and status conditions.
- **Hint 3:** Do not assume status condition names or acceptance behavior without the installed controller's docs.
- **Diagnostic commands:** `kubectl get crd | grep -i gateway`; inspect Gateway/HTTPRoute only if CRDs exist; controller docs/logs.
- **Evidence required:** CRD/controller versions, route status, parent/listener and backend endpoints.
- **Fidelity:** read-only analysis with illustrative status if Gateway API/controller is absent.

#### Challenge G09 — TLS expiry, SNI or certificate-chain mismatch

- **Initial symptom:** TCP connects but TLS verification fails or the wrong certificate is presented.
- **Hint 1:** Compare hostname/SNI with the certificate SAN and served route.
- **Hint 2:** Inspect validity dates and the complete chain.
- **Hint 3:** Identify whether TLS terminates at ingress, mesh or application.
- **Diagnostic commands:** `curl -v` to the local-only endpoint; approved certificate inspection; `openssl s_client` only if installed.
- **Evidence required:** exact hostname, certificate subject/SAN/validity, chain/trust result and termination point.
- **Fidelity:** local-only reproduction if a local TLS endpoint already exists; otherwise read-only analysis.

#### Challenge G10 — Strict mTLS versus plaintext client mismatch

- **Initial symptom:** one workload can connect while another receives a reset/authorization failure after mesh policy change.
- **Hint 1:** Determine whether the selected mesh is installed and the workload is enrolled.
- **Hint 2:** Inspect identity/policy status and proxy logs, not just the app container.
- **Hint 3:** A TCP connect is not proof of mTLS authentication or authorization.
- **Diagnostic commands:** version-matched Linkerd/Istio status/policy commands only if that mesh exists; app/proxy logs.
- **Evidence required:** mesh/version, workload identity, policy state and controlled request result.
- **Fidelity:** read-only analysis unless the mesh was already selected and installed. Do not install a mesh solely for this challenge.

#### Challenge G11 — `externalTrafficPolicy` source-IP / traffic surprise

- **Initial symptom:** source IP differs from expectation or traffic reaches only some nodes/endpoints.
- **Hint 1:** Identify Service type, traffic policy and actual traffic entry point.
- **Hint 2:** Check whether this is kind, a local helper, NodePort or a real provider load balancer.
- **Hint 3:** Understand the platform's source NAT and health-check behavior before drawing conclusions.
- **Diagnostic commands:** `kubectl -n <NAMESPACE> get svc <SERVICE> -o yaml`; node/LB status if available.
- **Evidence required:** service spec, client path, observed source address and environment limitations.
- **Fidelity:** read-only analysis in the baseline lab; no cloud load balancer required.

#### Challenge G12 — CoreDNS loop or upstream-resolution failure

- **Initial symptom:** internal names resolve but external names time out or fail, or both fail after resolver changes.
- **Hint 1:** Check CoreDNS Pod health, Service and EndpointSlices.
- **Hint 2:** Inspect CoreDNS logs and forwarding config only with appropriate authorization.
- **Hint 3:** Host `systemd-resolved` stub resolvers can be relevant to forwarding loops in some environments.
- **Diagnostic commands:** `kubectl -n kube-system get pods,svc,endpointslice`; CoreDNS logs; inspect ConfigMap read-only.
- **Evidence required:** affected query names, response/error, DNS endpoints, logs and upstream path.
- **Fidelity:** read-only analysis. Do not deliberately introduce a loop in a shared or default cluster.

#### Challenge G13 — Suspected conntrack pressure

- **Initial symptom:** new connections fail intermittently while existing connections may survive.
- **Hint 1:** Check whether the problem is new connections, DNS, NAT or a single destination.
- **Hint 2:** Use platform metrics and counters if available; record a before/after interval.
- **Hint 3:** Never exhaust host resources to “prove” the hypothesis.
- **Diagnostic commands:** approved node metrics; `nstat`; `conntrack -S` only if installed and permitted `[VERIFY]`.
- **Evidence required:** kernel/tool availability, time-correlated counters, connection failure pattern and resource context.
- **Fidelity:** read-only analysis; no resource exhaustion.

#### Challenge G14 — Timeout-ladder mismatch

- **Initial symptom:** client sees timeout/499 while ingress or app continues work; some requests return 504.
- **Hint 1:** Separate connect, TLS, TTFB and total time.
- **Hint 2:** Compare client, ingress, mesh, app and downstream timeout/retry settings.
- **Hint 3:** A timeout at one hop may not cancel work at another hop.
- **Diagnostic commands:** structured `curl -w`; correlated logs/traces; inspect config only for installed components.
- **Evidence required:** timeout values/semantics, request timeline and identified status-code emitter.
- **Fidelity:** read-only analysis or local configuration review.

#### Challenge G15 — DNS succeeds but only one source Pod fails

- **Initial symptom:** a feature call works from one Pod but fails from another.
- **Hint 1:** Compare namespace, labels, node, readiness and mesh enrollment.
- **Hint 2:** Inspect policy selectors and DNS configuration from both source Pods.
- **Hint 3:** Compare direct endpoint and Service paths without treating direct Pod-IP success as a fix.
- **Diagnostic commands:** `kubectl get pods --show-labels -o wide`; applicable policies; source Pod resolver config; bounded request.
- **Evidence required:** source comparison table, policies, node placement, exact errors and request IDs.
- **Fidelity:** read-only analysis or simulated local reproduction.

### Gauntlet answer key — do not read until you attempt the challenges

**G01 — Wrong targetPort.** Hidden cause: Service points to a port where the process is not listening. Compare Service `targetPort`, EndpointSlice port and actual listener. Smallest fix: correct the Service port mapping in the lab manifest and apply only to the lab. Prevention: service contract tests and deployment/port consistency checks. Cleanup: restore the baseline manifest and verify the request.

**G02 — Selector mismatch.** Hidden cause: Service selector does not match Pod labels. Evidence: selector/label comparison and empty or unexpected EndpointSlices. Fix the selector or labels in the disposable lab, not both arbitrarily. Prevention: manifest validation and tests that assert endpoints exist after deployment.

**G03 — Missing/unready endpoints.** Hidden cause: readiness failure or no replicas/selected endpoints. Evidence: Pod readiness, events, EndpointSlice conditions, rollout status. Fix the readiness/app problem or restore a known-good replica count. Do not weaken readiness merely to force traffic. Verify endpoint eligibility and request success.

**G04 — DNS egress omitted.** Hidden cause: enforced egress isolation permits the application destination but blocks DNS. First verify that the installed CNI enforces NetworkPolicy. If not, mark the result analysis-only. Add the narrow DNS rule appropriate to the cluster's DNS labels and UDP/TCP requirements only after schema/implementation review. Verify DNS and the allowed/denied application paths. Never remove all policy as a shortcut.

**G05 — Search amplification.** Hidden cause: short names with the configured search list/`ndots` generate multiple candidate queries and retries. Exact behavior depends on resolver library. Compare actual query sequence and latency using the same client. Prefer correct namespace-qualified or absolute names where appropriate, but do not blindly change `ndots` cluster-wide. Prevention: DNS query telemetry and workload-specific tests.

**G06 — MTU/PMTUD.** Hidden cause in the exercise: path MTU or blocked PMTUD feedback causes larger packets to stall. The evidence must show size-specific failure and relevant MTU/path behavior; without it, this remains a hypothesis. Use analysis-only by default. Do not run `tc` unless the namespace/interface and rollback are verified. Prevention: documented overlay MTU and packet-size tests.

**G07 — IngressClass mismatch.** Hidden cause: the Ingress resource references a class not watched by the installed controller, or no controller exists. Verify controller presence and class/status/logs. Correct the class only after checking controller configuration. If no controller exists, the correct diagnosis is “external route not installed,” not “network is broken.”

**G08 — HTTPRoute unaccepted.** Hidden cause: missing/incorrect parent attachment, listener/hostname mismatch, unsupported API/controller, or backend reference issue. Inspect installed CRDs and the actual controller's status semantics. Fix the specific route/parent mismatch. If Gateway API is absent, use the illustrative analysis path and do not apply the custom resource.

**G09 — TLS/SNI.** Hidden cause: client hostname/SNI mismatch, expired/wrong SAN certificate, incomplete chain or wrong termination point. Confirm certificate and hostname with the same local endpoint and client trust. Fix the certificate/route/chain; do not use `curl -k` as a production fix. Prevention: certificate-expiry monitoring and automated renewal tests.

**G10 — mTLS mismatch.** Hidden cause: one client lacks mesh enrollment/identity or violates strict peer/authorization policy. Inspect mesh state and proxy logs. Fix enrollment or narrowly correct policy only if intended. Do not switch strict mTLS off globally. If the mesh is absent, report the exercise as analysis-only.

**G11 — externalTrafficPolicy.** Hidden cause: observed source IP and endpoint distribution depend on `externalTrafficPolicy`, node routing, source NAT, load-balancer health checks and the environment. `kind` alone does not reproduce a cloud provider's behavior. Inspect Service configuration and actual path; explain limits rather than claiming a cloud result.

**G12 — CoreDNS/upstream.** Hidden cause: forwarding configuration/upstream resolver path fails or loops, or DNS endpoints are unavailable. Distinguish internal and external query results; inspect CoreDNS logs/config read-only. Do not edit CoreDNS or introduce a loop in a shared cluster. Recovery must be verified with the exact previously failing query.

**G13 — Conntrack pressure.** Hidden cause: analysis assumes pressure but must be confirmed from counters/metrics and time-correlated connection failures. Do not exhaust resources or tune sysctls blindly. If counters are unavailable, state that the evidence is insufficient and escalate to the platform owner.

**G14 — Timeout mismatch.** Hidden cause: the client deadline expires before upstream processing completes, or a proxy timeout/retry budget differs from application/downstream limits. Compare each timeout's semantics and the timeline. Fix by establishing a coherent request budget and cancellation behavior. Verify response latency and that unnecessary downstream work stops.

**G15 — Source-specific failure.** Hidden cause: source Pods differ in namespace/labels/policy/identity/node/resolver configuration. Compare those dimensions systematically. Fix only the identified selector, policy or configuration difference. Do not conclude that the destination Service is globally broken if a known-good source succeeds.

### Additional knowledge checks

1. **Why does a Service DNS answer not prove a backend exists?**  
   Because DNS can return the Service virtual IP even if the Service has no ready EndpointSlice endpoints. Inspect the Service and endpoints.

2. **Does ICMP ping failure prove a TCP service is unreachable?**  
   No. ICMP may be filtered or rate-limited. Test the actual destination protocol/port and correlate with logs.

3. **What does high `time_starttransfer` with low `time_connect` suggest?**  
   The TCP connection was relatively quick but the first response byte was delayed. Investigate proxy/app/dependency processing; timing alone does not identify the component.

4. **What does a 504 prove?**  
   Only that the client observed a 504 from some responding hop. Identify the emitter and upstream timeout evidence before claiming a root cause.

5. **Why can `ndots:5` matter?**  
   Search-list behavior can cause several candidate DNS queries for short names. Exact amplification depends on resolver behavior, cache and retries.

6. **What can `tcpdump` prove?**  
   It can show packets visible at one capture point. It cannot prove the entire path from one location, and ordinary TLS captures do not expose encrypted application payload.

7. **Why can a diagnostic Pod succeed while the application Pod fails?**  
   The Pods may have different namespaces, labels, NetworkPolicy selection, mesh identity, node placement, DNS configuration or routes.

8. **When should you use `conntrack -S`?**  
   Only when the tool/kernel support and access are confirmed and the hypothesis concerns connection-tracking pressure. It is not a generic first command for all timeouts.

9. **Why should `tc netem` be optional?**  
   It mutates traffic on a specific interface and can affect unrelated workloads if mis-scoped. Use a disposable namespace/interface with saved state and exact cleanup, or use analysis-only exercises.

10. **What makes a good incident mitigation?**  
    It is small, reversible, approved, tied to evidence and followed by positive/negative verification. It does not merely hide the symptom or erase diagnostic state.

## 10.13 Summary and readiness gate

### Summary

Troubleshooting begins with the exact symptom and request path, not with a favorite command. Identify the responding hop, compare known-good and failing paths, and gather timestamped evidence across Kubernetes objects, DNS, TCP, TLS, HTTP, policy and application telemetry. A Service can exist without endpoints; DNS success does not prove connectivity; TCP success does not prove TLS or application success; and a 502/503/504 does not uniquely identify a root cause. Packet captures, socket counters, conntrack and fault injection can be valuable but require correct scope, permissions and interpretation. Prefer safe, reversible local faults and read-only evidence, then verify recovery and record prevention.

### Readiness gate

You are ready to move on when you can:

- [ ] Explain the sequence: symptom → layer → hop → evidence → hypothesis → smallest fix → verification → prevention.
- [ ] Use Service, selector, EndpointSlice and Pod readiness evidence to diagnose a Service failure.
- [ ] Run a controlled DNS comparison from the actual Pod resolver path and explain `search`/`ndots`.
- [ ] Separate DNS, connect, TLS, TTFB and total time using curl timing fields.
- [ ] Explain why ICMP, traceroute, packet captures and Hubble have visibility limits.
- [ ] Identify the actual HTTP status-code emitter from correlated evidence.
- [ ] Explain MTU/PMTUD, retransmissions, conntrack/SNAT and timeout-ladder hypotheses without unsafe tuning.
- [ ] Run or safely review the `netcheck` script and interpret its exit codes/limitations.
- [ ] Complete at least 12 gauntlet scenarios with evidence, safe fix, verification and cleanup; analysis-only is acceptable where a feature is absent.
- [ ] Write an incident record and postmortem separating root cause, contributing factors and detection gaps.
- [ ] State which tests were actually run versus expected or illustrative.

## 10.14 References, source/claim register and audit

### Official references consulted

1. Kubernetes, **Debugging DNS Resolution** — https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/  
   Consulted 2026-10-28 for Pod resolver configuration, CoreDNS checks, DNS Service/EndpointSlice checks and common resolver caveats.
2. Kubernetes, **Debugging Services** — https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/  
   Consulted 2026-10-28 for Service, endpoint and DNS troubleshooting concepts including `ndots`.
3. kind, **Configuration** — https://kind.sigs.k8s.io/docs/user/configuration/  
   Consulted 2026-10-28 for kind networking and port-mapping behavior and the limits of local port forwarding.
4. kind, **Quick Start** — https://kind.sigs.k8s.io/docs/user/quick-start/  
   Consulted 2026-10-28 for creating clusters using a configuration file.
5. curl, **`--write-out` / write-out variables** — https://curl.se/docs/manpage.html#-w  
   Official reference for timing variables. Verify the installed curl version and supported variables before using a script across heterogeneous systems.
6. Kubernetes, **Debugging running Pods / `kubectl debug`** — https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/  
   Verify current runtime/version/RBAC and ephemeral-container behavior before use.
7. Kubernetes, **Network Policies** — https://kubernetes.io/docs/concepts/services-networking/network-policies/  
   Use to verify native policy semantics and the requirement for a policy-enforcing network implementation.
8. Kubernetes, **DNS for Services and Pods** — https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/  
   Use for name formats, namespace scope and cluster DNS behavior.
9. Linux/iproute2/tcpdump/conntrack references: tool availability and kernel behavior are distribution-specific. Consult the local man pages and official kernel/distribution documentation for the exact installed versions before privileged diagnostics or mutation.
10. Available local sources: `Roadmap(5).md`, `PROMPT-Kubernetes-Networking-Ingress-and-Service-Mesh(9).md`, Units 1–9, and the uploaded Unit 10 prompt. These shaped unit order, `ml-platform` vocabulary, safe local lab assumptions and boundaries with networking, policy, TLS, mesh and Cilium units.

### Claim register

| Claim/topic | Source URL or file | Source type | Version/date checked | Confidence/status | Notes |
|---|---|---|---|---|---|
| Pod DNS diagnosis should inspect resolver config, CoreDNS Pods, Service and EndpointSlices | Kubernetes DNS debugging | Official docs | Accessed 2026-10-28 | High — consulted | Actual labels and configuration can vary by cluster |
| Service reachability requires examining Service spec and backend endpoints | Kubernetes Debugging Services | Official docs | Accessed 2026-10-28 | High — consulted | CNI/datapath-specific behavior still requires local evidence |
| kind supports configurable networking and extra port mappings | kind Configuration | Official docs | Accessed 2026-10-28 | High — consulted | Not equivalent to a cloud load balancer |
| curl exposes timing variables through write-out | curl man page | Official docs | Accessed 2026-10-28 | High — consulted | Verify installed curl version and semantics |
| `ndots`/search behavior can affect query volume | Kubernetes DNS docs and resolver concepts | Official docs + reasoned explanation | Accessed 2026-10-28 | High with implementation caveat | Exact query order/count depends on resolver, client, cache and retries |
| `ping` failure does not prove TCP failure | TCP/IP operational reasoning | Reasoned interpretation | Not a live test | High | ICMP can be filtered/rate-limited |
| 502/503/504 do not uniquely prove a root cause | HTTP/proxy operational reasoning | Reasoned interpretation | Not a live test | High | Identify actual emitter and implementation |
| `499` commonly appears in NGINX logs for client-closed requests | NGINX-specific behavior | Implementation-specific knowledge | `[VERSION-SENSITIVE]` | High with caveat | Not a universal standard client response |
| `ss -ti`, `nstat`, `conntrack -S`, `tc netem` availability and output | Local Linux tools/man pages | Platform-specific | `[VERIFY]` at execution time | Conditional | Kernel, distribution, package, namespace and privileges vary |
| Baseline `kind` app/service will work | Lesson manifest | Expected behavior | Not run | Expected, not observed | Verify image pull, port-forward and local runtime |
| netcheck script exit codes and report content | Lesson script | Authored artifact | Not executed | Review only | Test in a disposable cluster before relying on it operationally |
| Gauntlet scenarios | Lesson design | Mix of local simulation and analysis | Not run | Defined fidelity per scenario | No shared/production fault injection |
| Performance numbers | None | Not applicable | Not measured | Not claimed | No fabricated benchmark values |
| Exact M04 prompt pack/project alignment | Not available separately | Source limitation | Not checked | Unresolved | Available syllabus and uploaded prompt used as controlling source |

### Ten-pass quality audit

| Pass | Status | What was checked | Remaining limitation |
|---|---|---|---|
| 1. Roadmap fidelity | PASS WITH LIMITATIONS | M04 tree, available syllabus and uploaded Unit 10 prompt | Exact copy-paste prompt pack and project files unavailable separately |
| 2. Structure | PASS | Sections 10.0–10.14 and Appendices A–E in order | Appendix titles follow the uploaded prompt |
| 3. Technical accuracy | PASS WITH LIMITATIONS | DNS, Services, EndpointSlices, curl timing, TCP/TLS, HTTP status interpretation and tool boundaries | Platform-specific kernel counters and controller statuses need local verification |
| 4. Version discipline | PASS WITH LIMITATIONS | Version-sensitive tools/CRDs/controllers marked conditional or `[VERIFY]` | No single installed Kubernetes/Linux/curl/controller version selected |
| 5. Safety | PASS WITH LIMITATIONS | Context guards, local-only scope, no public probing, bounded captures, destructive cleanup warnings | Scripts/lab not executed |
| 6. Reproducibility | PASS WITH LIMITATIONS | Baseline kind config, app/Service, request test, netcheck script, evidence and cleanup | Local image/runtime compatibility must be checked by learner |
| 7. Evidence honesty | PASS | Sample outputs are not claimed as observed; no benchmark or fault-injection results claimed | Actual evidence must be captured during learner execution |
| 8. Pedagogy | PASS | Worked examples, decision trees, tool table, 15 gauntlet scenarios, graduated hints and separated answer key | Some scenarios are analysis-only by design |
| 9. Cross-module consistency | PASS WITH LIMITATIONS | Boundaries with Units 1–9 and M03/M11/M08 are stated | Project/capstone files unavailable separately |
| 10. Markdown/script/completeness | PASS WITH LIMITATIONS | Code fences, headings, placeholders, script guards, exit codes, no Secret dumps and cleanup logic reviewed manually | Automated shell lint and live execution not performed |

### Exact execution status

**Reasoned review only; commands, scripts and labs were not executed in this environment.** Official Kubernetes, kind and curl documentation pages were consulted as listed above. The `netcheck` script has not been shell-linted or tested against a live cluster. No packet capture, `tc netem` impairment, conntrack pressure test, policy fault, TLS fault or performance benchmark was performed.

## Appendix A — Command and manifest reference

| Command | Location | Classification | Purpose / caveat |
|---|---|---|---|
| `kubectl config current-context` | Workstation | READ-ONLY | Verify target before any mutation |
| `kubectl get svc,endpointslice,pods -o wide` | Workstation/API | READ-ONLY | Compare Service, endpoints and Pods; add explicit namespace |
| `kubectl describe svc <SERVICE>` | Workstation/API | READ-ONLY | Inspect ports, selector and events |
| `kubectl get pods --show-labels` | Workstation/API | READ-ONLY | Compare labels and selectors |
| `kubectl get events --sort-by=.lastTimestamp` | Workstation/API | READ-ONLY | Review recent resource events |
| `kubectl exec <POD> -- cat /etc/resolv.conf` | Pod | READ-ONLY | Inspect resolver config if `cat` exists |
| `dig <NAME>` / `nslookup <NAME>` | Pod/workstation | READ-ONLY query | Test actual resolver; tool behavior differs |
| `curl -v <URL>` | Workstation/Pod | READ-ONLY request | Verbose HTTP/TLS diagnostics; protect headers |
| `curl -w '<FIELDS>'` | Workstation/Pod | READ-ONLY request | Timing decomposition; version-check variables |
| `nc -vz -w 3 <HOST> <PORT>` | Workstation/Pod | READ-ONLY connect | Syntax varies by netcat implementation |
| `ss -ti dst <IP>` | Linux socket namespace | READ-ONLY | TCP state/detail if supported |
| `ip -s link` / `ip route` | Linux host/node | READ-ONLY | Interface counters and routes |
| `traceroute <HOST>` / `mtr <HOST>` | Workstation/Pod | READ-ONLY probes | Probes may be filtered; do not infer app path alone |
| `tcpdump -ni <IFACE> -c <N> '<FILTER>'` | Authorized host/node | READ-ONLY capture, sensitive file | Narrow filter, short duration, restrictive permissions |
| `nstat -az` | Linux host/node | READ-ONLY | Kernel network counters; may be cumulative |
| `conntrack -S` | Authorized Linux host/node | READ-ONLY, `[VERIFY]` | Requires tools/kernel support; do not flush state |
| `tc qdisc show dev <IFACE>` | Exact Linux namespace/interface | READ-ONLY, `[VERIFY]` | Inspect current qdisc before any netem lab |
| `tc qdisc add ... netem ...` | Exact disposable interface | MUTATING, optional, `[VERIFY]` | Not required; only with saved state and exact cleanup |
| `kubectl debug` | Cluster API | MUTATING debug operation | Requires version/RBAC/admission/runtime support |
| `kubectl apply -f manifests/unit-10/baseline.yaml` | Workstation/API | MUTATING | Only guarded disposable cluster |
| `kubectl port-forward svc/echo 18080:80` | Workstation/API | Local listener process | Test local Service path; not ingress/LB equivalence |
| `kubectl delete namespace netdiag` | Workstation/API | DESTRUCTIVE | Only after context check and confirmation |
| `kind delete cluster --name m04-netdiag-lab` | Workstation | DESTRUCTIVE | Removes all resources in that local cluster |

## Appendix B — Troubleshooting matrix

| Symptom | First checks | Next evidence | Safe mitigation |
|---|---|---|---|
| Service resolves but fails | Service ports/selectors, EndpointSlices | Listener, policy, routing, flow evidence | Correct only confirmed Service/endpoint/policy mismatch |
| DNS timeout | Pod resolver, CoreDNS Service/Pods/endpoints | DNS logs/upstream path/policy | Restore narrow DNS path; avoid broad egress |
| NXDOMAIN | Exact query and namespace | Service existence/FQDN/negative cache | Correct name or record, then verify |
| Connection refused | Listener, targetPort, endpoint | RST/source evidence | Fix listener/port or backend health |
| Connection timeout | Destination, endpoints, policy | `ss`, `tcpdump`, route/counters | Scope path; do not flush rules |
| TLS failure | SNI, SAN, expiry, chain, trust | Termination point and proxy logs | Correct certificate/route/trust; do not default to `-k` |
| 502 | Identify emitter and upstream | Controller/mesh/app logs | Correct confirmed backend/protocol/config issue |
| 503 | Endpoint health, overload | App and proxy logs/metrics | Restore capacity or correct readiness/policy |
| 504 | Phase timings and timeout ladder | Traces and dependency timings | Align deadlines and fix slow dependency |
| Large payload stalls | Payload size, MTU, PMTUD | interface/tunnel config, packet evidence | Correct supported MTU/path issue with review |
| Intermittent resets | Rollouts, keep-alive, backend churn | socket and proxy logs | Fix lifecycle/pool/policy issue with bounded test |
| One Pod fails | labels, node, policy, resolver | source-to-source comparison | Fix identified difference only |
| External-only failure | controller/class/route, host mapping, TLS | LB/NodePort/firewall and logs | Correct external path; preserve loopback-only lab |
| Suspected conntrack pressure | platform metrics and counters | approved node-level evidence | escalate; never force exhaustion as a test |
| p99 latency rise | repeated timings, traces, saturation | per-endpoint/dependency distribution | mitigate queue/retry/dependency bottleneck and verify |

## Appendix C — Lab evidence and results worksheet

| Evidence | Value / artifact path | Captured at UTC | Interpretation / limitations |
|---|---|---|---|
| OS, kernel, Docker/runtime, kind, Kubernetes versions |  |  |  |
| Current context and cluster identity |  |  |  |
| Namespace and baseline workload readiness |  |  |  |
| Service spec/port/targetPort/selector |  |  |  |
| EndpointSlice addresses/conditions/ports |  |  |  |
| Baseline request status/connect/TTFB/total |  |  |  |
| `netcheck` exit code and report |  |  |  |
| DNS resolver config and exact query |  |  |  |
| Policy enforcement/CNI evidence if used |  |  |  |
| TLS certificate/SNI evidence if used |  |  |  |
| Packet capture details and retention approval |  |  |  |
| Scenario ID/fidelity label |  |  |  |
| Before/after state and rollback proof |  |  |  |
| Cleanup verification |  |  |  |
| Unresolved hypotheses |  |  |  |

**Evidence handling:** keep reports and captures private by default. Review and redact internal names, IPs, headers, cookies, tokens, payloads and any credentials before sharing. Never capture Kubernetes Secret values or arbitrary environment variables as a shortcut.

## Appendix D — Glossary

- **ALPN:** TLS extension used to negotiate an application protocol such as HTTP/2.
- **CNI:** Container Network Interface, the integration used to configure Pod networking.
- **CoreDNS:** Common Kubernetes cluster DNS implementation.
- **Conntrack:** Kernel connection-tracking state used by some firewall/NAT/networking paths.
- **DNS negative caching:** Temporarily caching negative DNS responses such as nonexistence, according to resolver/server behavior.
- **EndpointSlice:** Kubernetes resource representing endpoints for a Service.
- **Ephemeral port:** Temporary local port used for outgoing connections.
- **FQDN:** Fully qualified domain name.
- **IngressClass:** Kubernetes resource that identifies an ingress controller class where the API/controller uses it.
- **mTLS:** Mutual TLS, where both sides authenticate using certificates according to the configured trust/policy.
- **MTU:** Maximum transmission unit at a network interface/path.
- **`ndots`:** Resolver option controlling how many dots a name must contain before it is initially treated as absolute under relevant resolver behavior.
- **NetworkPolicy:** Kubernetes API for selected Pod ingress/egress controls when enforced by the CNI.
- **PMTUD:** Path MTU Discovery.
- **p50/p95/p99:** Latency percentiles for a defined sample/window.
- **SNI:** TLS Server Name Indication, used to indicate the intended server name during handshake when visible.
- **SNAT:** Source Network Address Translation.
- **SYN backlog:** Pending TCP connection handshake state at a listener.
- **TTFB:** Time to first byte.
- **`TIME_WAIT`:** TCP state after connection close; counts need context.
- **`tc netem`:** Linux traffic-control facility for emulating network conditions.
- **Endpoint readiness:** Conditions used by Kubernetes networking to represent endpoint availability; inspect actual EndpointSlice status.
- **Timeout ladder:** Coordinated timeout/deadline budget across client, ingress, mesh, application and downstream dependencies.

## Appendix E — Author verification and completion checklist

- [ ] Exact target filename: `10-network-troubleshooting-dns-latency-and-packet-loss.md`.
- [ ] Sections 10.0–10.14 and Appendices A–E are present in order.
- [ ] Source availability note discloses the missing exact prompt pack/project files.
- [ ] Every command has an execution location and safety classification.
- [ ] The baseline lab checks the context and uses only the named disposable kind cluster.
- [ ] The `netcheck` script uses `set -euo pipefail`, quoted variables, required arguments, context guard, timestamped report, bounded commands where available, meaningful exit codes and no Secret dumps.
- [ ] At least 12 gauntlet challenges include hints, evidence, safe fix, prevention, cleanup and fidelity label.
- [ ] The answer key is separated after all learner-facing challenges.
- [ ] NetworkPolicy challenge is conditional on verified CNI enforcement.
- [ ] Gateway API, TLS, mesh, Hubble, conntrack and `tc` exercises are conditional or analysis-only if dependencies are absent.
- [ ] No public probing, host-wide fault injection or actual resource exhaustion is required.
- [ ] No fabricated outputs, benchmark numbers or lab results appear.
- [ ] Source/claim register and ten-pass audit are present.
- [ ] Actual learner-run evidence and unresolved verification items are recorded before production use.

**Reviewer:** ______________________________  
**Date:** ______________________________  
**Kubernetes / kind / OS / kernel versions:** ______________________________  
**Path performed:** baseline / selected live scenarios / analysis-only  
**Commands/scripts actually executed:** ______________________________  
**Evidence reviewed:** ______________________________  
**Outstanding verification items:** ______________________________  
**Human sign-off:** ______________________________
