# Cross-Cluster Service Discovery and Traffic Routing

> **Module:** M14 — Multi-Cluster-and-Multi-Region-Operations  
> **Stage:** Stage 2E — Production DevOps & Platform Engineering  
> **Target filename:** `04-cross-cluster-service-discovery-and-traffic-routing.md`  
> **Prerequisites:** M04 single-cluster networking; M09 identity and secrets; M10 SRE reliability patterns; M11 observability; M12 security and supply-chain controls; M13 fault injection and disaster-recovery fundamentals; M14 Units 1–3.  
> **Estimated time:** 18–30 hours for reading and guided labs; optional mesh/interconnect work is additional.  
> **Lab environment:** WSL2 Ubuntu or native Linux, Docker, kubectl, kind, and two single-node clusters named `stage2e-east-lab` and `stage2e-west-lab`. Target baseline is approximately 4 CPU cores, 8 GB RAM, and 30 GB free disk; measure your own footprint.  
> **Assumed baseline:** Kubernetes APIs and common tools; versions of kind, Kubernetes, Gateway API, cert-manager, CoreDNS, and optional networking products are environment-dependent and must be checked. `[VERIFY]` means verify the exact syntax, compatibility, and behavior against the installed version and current official documentation.  
> **Last reviewed:** 2026-10-29 for this authored document; no claim of live official-document verification is made here.  
> **Scope:** The default hands-on path is a small, private-by-default cross-cluster call through an explicitly exposed endpoint, with TLS, a local Service abstraction, and bounded client resilience.  
> **Lab safety:** Never use production kubeconfigs, tokens, private keys, or credentials. Every cluster operation must name `--context stage2e-east-lab` or `--context stage2e-west-lab`. These names are logical labels, not real regions.

## Table of contents

- [1. Purpose, Scope, and Learning Outcomes](#1-purpose-scope-and-learning-outcomes)
- [2. Mental Model: What Changes at the Cluster Boundary?](#2-mental-model-what-changes-at-the-cluster-boundary)
- [3. Level 1 — Foundations and Architecture Vocabulary](#3-level-1--foundations-and-architecture-vocabulary)
- [4. Level 2 — Build a Minimal Cross-Cluster Call](#4-level-2--build-a-minimal-cross-cluster-call)
- [5. Level 3 — Architecture Selection and Traffic Policy](#5-level-3--architecture-selection-and-traffic-policy)
- [6. Level 4 — Production Operations, Security, and Reliability](#6-level-4--production-operations-security-and-reliability)
- [7. Hands-On Labs](#7-hands-on-labs)
- [8. Incident Analysis: Diagnose, Fix, Prevent](#8-incident-analysis-diagnose-fix-prevent)
- [9. Architecture Decision Record Exercise](#9-architecture-decision-record-exercise)
- [10. Verification, Evidence, and Cleanup](#10-verification-evidence-and-cleanup)
- [11. Knowledge Check and Self-Assessment](#11-knowledge-check-and-self-assessment)
- [12. References and Version-Sensitive Verification](#12-references-and-version-sensitive-verification)
- [13. Final Roadmap Alignment Audit](#13-final-roadmap-alignment-audit)

> M04 taught single-cluster networking: the Kubernetes networking model and CIDR planning (including the cost of overlapping ranges and future peering), Services/kube-proxy/CoreDNS, Gateway/Ingress, load balancers (MetalLB locally), NetworkPolicy, cert-manager, service-mesh fundamentals and mTLS, and a Cilium/Cluster Mesh overview as Awareness. This unit applies that knowledge **across clusters**: how services in one cluster find and call services in another, the available architectures and their trade-offs, trust and identity across clusters, failure semantics, and security — without re-teaching single-cluster networking.

This unit focuses on what changes when a service call crosses an independent cluster boundary. It does not re-teach the M04 networking model, deliver a full global DNS/global load-balancing design (M14 Unit 5), define complete active-active/active-passive regional architecture (Unit 6), teach data consistency in depth (Unit 7), or duplicate GitOps propagation (Unit 3). The lab hostname is local to the exercise; it is not a global routing service.

## 1. Purpose, Scope, and Learning Outcomes

Cross-cluster communication is a deliberate dependency, not a free extension of a cluster-local Service. The caller needs a discovery mechanism, a reachable path, compatible protocol and endpoint behavior, authenticated identity, authorization, timeouts, telemetry, and a safe response to partial failure.

By the end, you should be able to:

1. Explain why cross-cluster calls introduce latency, transfer cost, security exposure, and failure-domain coupling.
2. Explain why ordinary Kubernetes Services and `svc.ns.svc.cluster.local` names are cluster-scoped.
3. Compare external endpoints, manually managed Service/EndpointSlice patterns, Multi-Cluster Services (MCS), network interconnects, multi-cluster meshes, application-level routing, and asynchronous alternatives.
4. Build and validate a small lab-safe call using TLS, a local Service abstraction, bounded retries, a circuit-breaker-like fail-fast mechanism, and local-first fallback where safe.
5. Demonstrate private exposure controls, network allow-listing, authentication, authorization, and identity validation.
6. Explain DNS forwarding failure coupling and endpoint freshness.
7. Explain `ServiceExport`, `ServiceImport`, and `clusterset.local` concepts, and why a teaching endpoint mirror is not a conformant MCS implementation.
8. Choose an architecture based on latency, trust, scale, failure isolation, cost, and operational maturity.
9. Diagnose remote cluster, gateway, DNS, certificate, endpoint, packet-loss, and partial-failure scenarios without causing retry storms.
10. Rotate a lab trust bundle with an overlap window and explain one-sided rotation failure.
11. Compare declared and observed cross-cluster dependencies and isolate a compromised cluster.
12. Define SLOs and telemetry for requests, endpoint-sync lag, gateways, certificates, and transfer volume.
13. Produce an ADR and identify what a laptop lab cannot prove.

**Default design rule:** **Keep request paths cluster-local by default. Make cross-cluster calls explicit, bounded, observable, and fallback-able.**

## 2. Mental Model: What Changes at the Cluster Boundary?

A cross-cluster call has at least five independent questions:

1. **Discovery:** How does the caller learn a usable hostname or endpoint?
2. **Connectivity:** Is there a network path from source to destination?
3. **Identity:** Who is calling, and who is serving?
4. **Authorization:** Is that identity permitted to perform this operation?
5. **Traffic policy:** What happens under latency, endpoint churn, partial failure, and recovery?

A successful DNS lookup proves only that a resolver returned an answer. It does not prove route reachability, TLS validity, authorization, or application health. A reachable TCP port proves neither application readiness nor correct identity.

```text
East cluster                                      West cluster
+------------------------------+                  +------------------------------+
| caller / feature consumer    |                  | feature-service              |
|        |                     |                  | readiness + application auth |
|        v                     |                  |          ^                   |
| local Service abstraction    |                  |          |                   |
|        |                     |                  | east-west / ingress gateway  |
+--------|---------------------+                  +----------|-------------------+
         | DNS + TLS hostname validation                     |
         +--------------- explicit network path ------------+
                     identity + authorization
```

### 2.1 Kubernetes behavior at a glance

- A normal `ClusterIP` Service provides a stable virtual address inside the cluster's service network.
- CoreDNS ordinarily answers for that cluster's Kubernetes service names. The common `service.namespace.svc.cluster.local` form is not a global namespace shared by independent clusters.
- A headless Service returns endpoint addresses according to its DNS behavior; it does not create cross-cluster routing.
- EndpointSlices represent backend endpoints for a Service within the API and controller model that owns them. A hand-written or mirrored EndpointSlice does not automatically acquire the lifecycle guarantees of a real cross-cluster controller.
- `ExternalName` creates a DNS alias-like Service abstraction; it does not proxy packets, validate TLS identity, or guarantee that the target is reachable.
- NetworkPolicy enforcement depends on a supporting network implementation and its policy semantics. A policy object alone is not proof that traffic is blocked.
- The MCS API defines cross-cluster service concepts; an implementation must provide the corresponding controllers, discovery, connectivity assumptions, and lifecycle behavior. API concepts and implementations must not be conflated. `[VERIFY]`

### 2.2 Six architecture families

#### A. Exposed external endpoint

```text
East caller -> local Service/HTTP client -> private DNS hostname
            -> controlled ingress/east-west gateway -> West Service
```

The remote service has an explicitly exposed endpoint, ideally private to the lab or internal network. The caller uses a stable hostname and TLS. Exposure is a controlled path, not a claim that the service should be public. A `NodePort`, `LoadBalancer`, or gateway path depends on host networking and the selected lab implementation; test reachability before building DNS or TLS around it.

#### B. Manual Service / EndpointSlice wiring

```text
East client -> East Service -> manually declared endpoint(s) -> West endpoint
                                     ^
                           operator-maintained mapping
```

This can create a stable local abstraction, but endpoint lifecycle is now a responsibility: address changes, readiness, termination, ports, address families, and stale entries must be managed. A manually authored EndpointSlice is not a production controller.

#### C. Multi-Cluster Services (MCS) API

```text
West Service -> ServiceExport
      | controller/implementation-specific export and discovery
East consumer -> ServiceImport -> clusterset.local discovery -> implementation path
```

`ServiceExport`, `ServiceImport`, and `clusterset.local` are MCS concepts. The exact APIs, installation requirements, DNS semantics, endpoint propagation, and failure behavior depend on the implementation and version. `[VERIFY]` Never infer that applying an export object alone establishes a network path.

#### D. Network interconnect

```text
East workload -> East route/gateway -> encrypted interconnect/tunnel
                                      -> West route/gateway -> West workload
```

Examples to compare include Submariner, Cilium Cluster Mesh, and Liqo. Connectivity, routing, service discovery, identity, and authorization remain distinct concerns. A tunnel does not automatically provide a service catalog, application authentication, or correct policy. Compatibility, CNI constraints, and kind/WSL2 support must be checked before installation. `[VERIFY]`

#### E. Multi-cluster service mesh

```text
East workload -> local sidecar/ambient dataplane -> east-west gateway
              -> trust and service discovery -> West dataplane -> service
```

Istio primary-remote/multi-primary and Linkerd multicluster/service mirroring are awareness-level options here. Consider trust anchors, gateway placement, service mirroring, control-plane topology, identity, upgrade order, and operational burden. Exact topology and commands are version-sensitive. `[VERIFY]`

#### F. Application-level routing and asynchronous integration

```text
Synchronous: client/BFF -> policy-aware endpoint selection -> remote API
Asynchronous: producer -> queue/stream -> local consumer/replica
```

An API gateway or backend-for-frontend can apply tenant/home-cluster rules explicitly. Queues, streams, local replicas, caches, and replication can remove a synchronous dependency, but introduce freshness, ordering, duplication, consistency, and write-authority questions. See Unit 7 for the deeper replication/consistency treatment.

### 2.3 Control plane versus data plane

- **Control plane:** publishes endpoint metadata, trust bundles, routing rules, service exports/imports, or mesh configuration.
- **Data plane:** carries actual requests and responses.
- A healthy control plane does not guarantee a working data path.
- A data path may continue for a while after a control-plane outage using cached configuration, but endpoint changes and revocations may not propagate. The exact behavior is implementation-specific. `[VERIFY]`

### 2.4 Architecture trade-off matrix

| Family | Discovery | Connectivity / path | Identity and authorization | Failure/fallback | Burden / coupling | Laptop feasibility |
|---|---|---|---|---|---|---|
| Exposed private endpoint | Stable hostname/DNS | Explicit gateway, ingress, or host path | TLS plus application identity/authorization | Client timeouts and fallback; endpoint can be unavailable | Low–medium; depends on endpoint implementation | Best default if host reachability is proven |
| Manual Service/EndpointSlice | Manually maintained mapping | Must separately provide routing | Not supplied by endpoint object | Stale endpoint unless actively reconciled | Medium; lifecycle ownership is easy to miss | Good as a bounded toy |
| MCS API | `ServiceExport`/`ServiceImport` concepts | Implementation-specific | Depends on implementation and workload security | Controller and endpoint propagation behavior varies | Medium–high; implementation coupling | Guided analysis unless preflight confirms support |
| Interconnect | May be separate from routing/discovery | Tunnel/routed network | Separate identity/policy layer still required | Partition, routing, or tunnel failures | High; CNI/network dependency | Optional only after feasibility check |
| Multi-cluster mesh | Mesh service registry/mirroring | East-west gateways and dataplane | Mesh identity/mTLS plus authorization policy | Retry/outlier behavior is implementation-specific | High; mesh version and topology coupling | Guided analysis by default |
| App-level routing | Client/BFF/catalog | Explicit endpoints and routing policy | Application/workload identity | Application-controlled fallback | Medium; code and policy ownership | Feasible |
| Async / local replica | Queue, stream, or replicated data | Broker/replication path rather than synchronous RPC | Producer/consumer identity and data policy | Decouples request availability, but freshness/lag matter | Medium–high; consistency/operations | Design exercise; lightweight local toy possible |

**Important:** the comparison does not imply every family provides all five layers. Always select discovery, connectivity, identity, authorization, and traffic policy deliberately.

## 3. Level 1 — Foundations and Architecture Vocabulary

### 3.1 Why cross-cluster calls exist

Common reasons include a shared read-only feature service, migration from one cluster to another, data locality, failover, and a service mesh spanning clusters. Each adds a dependency edge.

Costs and risks include:

- additional network round trips and tail latency;
- transfer/egress charges in real environments;
- a new path to secure and observe;
- dependence on the remote cluster, gateway, resolver, trust chain, and endpoint controller;
- more complex incident diagnosis;
- risk that “independent” clusters are not operationally independent because one synchronously calls the other.

Avoid a synchronous cross-cluster request when a local cache/replica or asynchronous event can meet the freshness and correctness contract. Do not replicate sensitive data without checking residency, privacy, retention, and access policy. Do not fall back to stale data without exposing staleness to the caller.

### 3.2 Discovery is not reachability

| Signal | What it proves | What it does not prove |
|---|---|---|
| DNS answer | Resolver returned an answer | Route, TLS, authorization, application health |
| TCP connect | A listener accepted a connection | Correct service, identity, operation success |
| TLS handshake | The peer satisfied the configured certificate checks | Caller is authorized for a business operation |
| HTTP 200 on `/healthz` | That endpoint returned success | All dependencies or business requests are healthy |
| Kubernetes object is `Ready` | The relevant readiness condition passed | Cross-cluster request path works end to end |
| Synthetic request succeeds | One request path worked at that time | All tenants, regions, failure modes, or capacity limits work |

### 3.3 Core vocabulary

- **Endpoint freshness:** how recently the advertised endpoint set was reconciled with actual service state.
- **Endpoint drain:** stop routing new requests to an endpoint while allowing in-flight requests to finish within a bounded grace period.
- **Gray failure:** a path works intermittently or slowly rather than being cleanly up/down.
- **Trust bundle:** certificates or trust anchors accepted to validate peers.
- **Trust domain:** a namespace of workload identities; cross-domain trust must be explicit.
- **Local-first:** use an eligible local dependency first, and use remote capacity only when policy allows.
- **Retry budget:** a bound on additional load generated by retries.
- **Kill switch:** a controlled way to revoke route/identity/policy so a compromised or unsafe cluster cannot call across the boundary.
- **Dependency edge:** a declared or observed relationship from a caller/service to a remote service.
- **Home cluster:** the cluster designated as authoritative for a tenant or service; routing away from it requires an explicit consistency/ownership contract.

### 3.4 Common beginner mistakes

1. Assuming `svc.cluster.local` resolves across clusters.
2. Treating DNS as a proxy or health check.
3. Exposing an internal endpoint publicly just to make a lab work.
4. Using source IP as the only identity.
5. Retrying all failures indefinitely.
6. Retrying non-idempotent writes without an idempotency/correctness design.
7. Sharing a root CA without understanding its compromise blast radius.
8. Treating an EndpointSlice as a self-maintaining service registry.
9. Installing a mesh before writing down the actual requirements.
10. Describing two kind clusters on one laptop as two regions.

## 4. Level 2 — Build a Minimal Cross-Cluster Call

### 4.1 Default lab architecture and honest limitations

Use two local kind clusters, with a sample HTTP feature service in west and an east-side client that calls a stable remote hostname. The recommended path is a private host-reachable endpoint plus TLS and an east-side local Service abstraction. A host port-forward can validate application/TLS behavior, but it is not a persistent production routing architecture. A NodePort or gateway route is suitable only if preflight confirms host reachability in the selected Docker/WSL2 setup.

```text
Host workstation
  |-- kind cluster stage2e-east-lab
  |      |-- caller -> local Service -> client policy
  |
  |-- kind cluster stage2e-west-lab
         |-- feature-service -> private lab endpoint
                    ^
        host/Docker networking path (verify locally)
```

**Fidelity boundary:** two kind clusters share one host, kernel, power, storage, and often the same Docker networking domain. Pod and Service networks are not automatically joined. This lab does not prove WAN routing, real regional isolation, managed load-balancer behavior, or multi-region resilience.

### 4.2 Preflight and resource profile

Run on the host:

```bash
docker version
kind version
kubectl version --client
free -h
df -h .
docker ps --format 'table {{.Names}}\t{{.Status}}'
kubectl config get-contexts
```

Confirm both contexts exist and map to the intended clusters:

```bash
kubectl --context stage2e-east-lab cluster-info
kubectl --context stage2e-west-lab cluster-info
kubectl --context stage2e-east-lab get nodes -o wide
kubectl --context stage2e-west-lab get nodes -o wide
```

Stop if either context maps to a non-disposable cluster. Do not paste credentials into the lesson, shell history, or evidence. If the machine is near the memory/disk limit, run one lab at a time, omit optional meshes, and delete only lab namespaces/resources after checking their contents.

### 4.3 Choose one endpoint path, do not combine alternatives blindly

**Default:** a host-reachable endpoint chosen after testing. For the lightest initial connectivity test, a temporary port-forward can verify the service process and HTTP response. It does not create a stable cross-cluster network path and should not be presented as production connectivity.

**Optional:** NodePort, Ingress/Gateway, or MetalLB. Choose one implementation that is actually installed and reachable from the caller. Host routing, source-IP preservation, and Docker/WSL2 port exposure vary; mark those details `[VERIFY]`. Do not copy commands from multiple options into a single sequence.

### 4.4 Minimal sample service

The following manifest is a lightweight HTTP fixture. It uses an illustrative image tag; pin and verify an approved image before use in a real environment. It intentionally has no secrets.

Save as `feature-service.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: cross-cluster-lab
  labels:
    app.kubernetes.io/part-of: cross-cluster-lab
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: feature-service
  namespace: cross-cluster-lab
spec:
  replicas: 1
  selector:
    matchLabels:
      app: feature-service
  template:
    metadata:
      labels:
        app: feature-service
    spec:
      containers:
        - name: app
          image: hashicorp/http-echo:1.0.0
          args:
            - "-text=served-by-west"
            - "-listen=:8080"
          ports:
            - name: http
              containerPort: 8080
          readinessProbe:
            tcpSocket:
              port: http
            initialDelaySeconds: 2
            periodSeconds: 5
          resources:
            requests:
              cpu: 25m
              memory: 32Mi
            limits:
              cpu: 200m
              memory: 96Mi
---
apiVersion: v1
kind: Service
metadata:
  name: feature-service
  namespace: cross-cluster-lab
spec:
  selector:
    app: feature-service
  ports:
    - name: http
      port: 8080
      targetPort: http
```

Apply only to west after reading the manifest:

```bash
kubectl --context stage2e-west-lab apply -f feature-service.yaml
kubectl --context stage2e-west-lab -n cross-cluster-lab rollout status deployment/feature-service
kubectl --context stage2e-west-lab -n cross-cluster-lab get svc,endpointslices,pods -o wide
```

This service is HTTP-only inside west. It is not yet the TLS endpoint. For a secure cross-cluster call, terminate TLS at a selected gateway/endpoint with a certificate whose SAN matches the stable hostname; the caller must validate both hostname and trust chain. Do not disable certificate validation to “make the lab pass.”

### 4.5 TLS and hostname plan

Choose one TLS termination point and document it. The certificate SAN should include `features.west.lab.internal` if that is the hostname the client uses. Keep the private key in a Kubernetes Secret or approved secret mechanism; never commit it to Git or copy it into evidence.

A lab CA can be created using OpenSSL on the host. These commands create local test material only; protect the output directory and remove it at cleanup. The exact openssl options should be checked against the installed version.

```bash
umask 077
mkdir -p ./lab-pki
cd ./lab-pki
openssl genrsa -out lab-root-ca.key 3072
openssl req -x509 -new -key lab-root-ca.key -sha256 -days 30 \
  -subj "/CN=Cross Cluster Lab Root CA" -out lab-root-ca.crt
openssl genrsa -out features-west.key 2048
openssl req -new -key features-west.key \
  -subj "/CN=features.west.lab.internal" -out features-west.csr
cat > features-west.ext <<'EOF'
subjectAltName=DNS:features.west.lab.internal
extendedKeyUsage=serverAuth
keyUsage=digitalSignature,keyEncipherment
EOF
openssl x509 -req -in features-west.csr -CA lab-root-ca.crt \
  -CAkey lab-root-ca.key -CAcreateserial -out features-west.crt \
  -days 14 -sha256 -extfile features-west.ext
openssl verify -CAfile lab-root-ca.crt features-west.crt
```

This is a teaching certificate flow, not a full certificate-management design. In a cert-manager-based lab, verify the installed issuer and trust-distribution model before applying resources. A CA issuer does not by itself distribute trust to clients. Do not expose or commit `lab-root-ca.key` or `features-west.key`.

For the selected gateway, create a TLS Secret only in the intended lab namespace and context, using the generated cert and key. The exact gateway/Ingress manifest depends on the selected controller and is `[VERIFY]`; do not mix controller-specific annotations or APIs. Verify the endpoint from the host before proceeding:

```bash
curl --fail --show-error --cacert ./lab-pki/lab-root-ca.crt \
  --resolve features.west.lab.internal:443:127.0.0.1 \
  https://features.west.lab.internal/
```

The address above is only correct if the selected gateway/port is deliberately bound to host loopback. Replace it only after verifying the actual lab endpoint. Do not make it listen on a public interface by default.

### 4.6 Local Service abstraction in east

The simplest safe abstraction is an east-side client configuration that uses a stable endpoint hostname rather than embedding a remote pod IP. If the service needs to look like a local Kubernetes Service, an `ExternalName` can alias a DNS name, but it does not proxy traffic and may not suit all protocols or TLS hostname expectations.

Illustrative object:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: feature-service-remote
  namespace: cross-cluster-lab
spec:
  type: ExternalName
  externalName: features.west.lab.internal
```

Apply in east only after the hostname resolves from east and the client’s TLS/SNI behavior is understood:

```bash
kubectl --context stage2e-east-lab apply -f feature-service-remote.yaml
kubectl --context stage2e-east-lab -n cross-cluster-lab get service feature-service-remote -o yaml
```

`ExternalName` is DNS indirection, not a proxy. Some client libraries may construct a TLS hostname or HTTP Host header from the alias, not the target name. Validate actual client behavior; if it cannot preserve the intended hostname, use a local proxy/gateway abstraction with explicit upstream TLS configuration instead. Do not add a manually managed EndpointSlice to this example without redesigning the endpoint lifecycle.

### 4.7 Client resilience: bounded, explicit, and operation-aware

A client policy should specify:

- connect timeout;
- total request deadline;
- maximum attempts;
- exponential backoff with jitter;
- retry budget;
- which status/errors are retryable;
- idempotency semantics;
- circuit breaker or equivalent fail-fast state;
- concurrency/bulkhead limit;
- local-first fallback and whether stale data is acceptable.

Representative policy (not a controller-specific configuration):

```yaml
remote_call_policy:
  connect_timeout_ms: 150
  request_deadline_ms: 500
  max_attempts: 2
  backoff:
    base_ms: 40
    max_ms: 120
    jitter: full
  retry_budget:
    max_retry_fraction: 0.10
    window_seconds: 10
  circuit_breaker:
    failure_threshold: 5
    open_seconds: 15
    half_open_probe_limit: 1
  fallback:
    mode: local-first
    allowed_operations:
      - read_feature_snapshot
    stale_data_max_age_seconds: 60
```

These values are `[ASSUMPTION]` examples for reasoning, not recommended universal thresholds. The client must enforce them in code or a selected proxy/library; a YAML document alone does not enforce policy. Do not retry non-idempotent writes without an idempotency key or a defined reconciliation model.

**Retry amplification example:** if each attempt is retried twice by three independent layers, a single logical request can generate up to \(3^3=27\) downstream attempts, depending on exact retry semantics. Avoid client retries + gateway retries + mesh retries without an end-to-end retry budget.

### 4.8 Local-first fallback

The local fallback is appropriate only when the local copy can answer correctly. For a read-only feature snapshot, the caller might use a local cache and return its age in the response. For an authoritative write, account mutation, or request requiring remote-only data, fallback may be unsafe and should fail explicitly.

A useful response includes `served-by-cluster`, `fallback-used`, `dependency-age`, and trace context. These fields are illustrative; avoid high-cardinality metric labels such as raw user IDs.

### 4.9 DNS forwarding and its failure coupling

Each cluster has its own DNS configuration. A stub-domain/forwarding arrangement can direct a chosen suffix to another resolver, but exact CoreDNS Corefile syntax, plugin order, cache behavior, and timeout semantics are `[VERIFY]` against the installed CoreDNS version. Do not paste an unverified Corefile into a live cluster.

Before enabling forwarding, define:
- which suffix is forwarded;
- destination resolver and network path;
- timeout/retry/cache behavior;
- access controls;
- how to disable the forward;
- what the application does when lookup fails.

Controlled test plan:

1. From east, resolve the selected remote hostname and record latency/result.
2. Make a real HTTPS request and verify TLS and application response.
3. In a disposable test only, block or stop the chosen forwarding dependency.
4. Repeat lookup and request tests, recording resolver errors and client deadlines.
5. Restore forwarding, wait for relevant caches/TTL behavior, and re-test.
6. Compare with a stable direct endpoint plus application fallback.

DNS is not a traffic proxy or a health check. A low TTL does not guarantee every client stops using an old address immediately; client caches, resolver caches, connection pools, and application behavior also matter.

### 4.10 MCS-style endpoint-mirroring teaching toy

A tiny script that copies endpoint data from west to east can demonstrate freshness hazards, but it is **a teaching toy — not a conformant MCS implementation**. It does not provide a durable controller loop, watches, leader election, conflict handling, full readiness/termination semantics, multi-address-family support, security, or complete deletion guarantees.

Toy algorithm:

```text
every interval:
  read west Service + EndpointSlices using west context
  validate expected service identity, port, address family, and readiness
  compare observation timestamp / generation with last accepted state
  if observation is missing or too old:
      mark remote endpoint unavailable; do not preserve stale endpoint as healthy
  else:
      publish a lab-only endpoint record in east
  on west Service deletion:
      mark record unavailable and remove only the owned lab record
```

Do not run this pseudocode as a controller. A real implementation must handle RBAC, API watch reconnects, resource ownership, endpoint readiness and termination, port mapping, address-family compatibility, stale data, deletion, race conditions, retries, observability, and security. MCS semantics and the selected implementation/version must be verified. `[VERIFY]`

A stale-endpoint demonstration can be done safely with a fixture: set the endpoint observation timestamp to an old synthetic time and assert that the consumer marks the remote dependency unavailable. This proves the test logic only, not a live controller's behavior.

## 5. Level 3 — Architecture Selection and Traffic Policy

### 5.1 Decision framework

Choose the architecture from requirements, not popularity. Answer these questions in order:

1. **Can the request be served locally?** If yes, prefer a local copy/cache/replica when freshness and data policy allow.
2. **Must the call be synchronous?** If no, consider queues, streams, or asynchronous replication.
3. **What is the end-to-end latency budget?** Include DNS, connection establishment, TLS, gateway hops, application time, retries, and tail latency.
4. **What is the trust boundary?** Define caller identity, server identity, authorization, trust anchors, and revocation.
5. **How many clusters and how much endpoint churn?** Manual mappings become harder to own as targets and changes grow.
6. **What connectivity is actually available?** An MCS object or mesh does not create routes if the network path is absent.
7. **What failure behavior is required?** Decide whether to fail fast, serve stale/local data, or queue work.
8. **What can the team operate?** Include upgrades, on-call maturity, compatibility testing, and exit strategy.
9. **What does cross-cluster traffic cost?** Estimate bytes and request rates; do not invent cloud egress prices.
10. **What is unproven?** Record lab-only evidence and target-environment tests still required.

### 5.2 Required comparison for design reviews

| Option | Best fit | Main risks | Operational decision |
|---|---|---|---|
| Private exposed endpoint | Small number of explicit service dependencies | Endpoint exposure, DNS/TLS mismatch, manual endpoint operations | Good first step when route and trust are well controlled |
| MCS API implementation | Standardized service export/import across supported clusters | Implementation/version coupling; discovery does not equal connectivity | Adopt only after confirming implementation guarantees and compatibility |
| Submariner | Cross-cluster connectivity where its supported topology fits | CNI/routing constraints, tunnel and broker operations, version skew | Validate current supported topology and diagnostics `[VERIFY]` |
| Cilium Cluster Mesh | Clusters using a compatible Cilium networking setup and required capabilities | CNI coupling, identity/policy interaction, upgrade coordination | Do not retrofit casually; verify exact Cilium/Kubernetes versions `[VERIFY]` |
| Istio multi-cluster | Mesh-level identity, traffic policy, and telemetry requirements justify complexity | Gateway/control-plane/trust complexity; retries can amplify failures | Awareness/comparison depth in this unit; verify topology/version `[VERIFY]` |
| Linkerd multicluster | Mesh identity and service mirroring requirements fit its supported design | Mirroring semantics, gateways, identity and version skew | Verify current prerequisites and commands `[VERIFY]` |
| Application-level routing | Tenant/home-cluster policy and explicit fallbacks matter | Routing logic can become duplicated or inconsistent | Define a single policy owner and test routing decisions |
| Async messaging/local replica | A synchronous remote dependency is too fragile or latency-sensitive | Freshness, consistency, duplicate processing, write authority | Use when product semantics tolerate asynchronous behavior |

Submariner, Cilium Cluster Mesh, Linkerd, Istio, Gateway API, and MCS capabilities change over time. This lesson does not assert their current product status or exact supported version matrix. Verify the official documentation for the chosen release.

### 5.3 Traffic policies

- **Locality-aware routing:** prefer local capacity; use remote only when the remote service is authorized, healthy enough, and within the latency/cost policy.
- **Failover priority:** define ordered eligible endpoints and the conditions for failover. Mesh outlier detection, retry, and ejection behavior is implementation-specific `[VERIFY]`.
- **Weighted migration:** move a small, measured share of eligible traffic to the new cluster, observe health, then increase only after an explicit gate. Use a verified Gateway API or mesh feature; do not assume all implementations support weighted cross-cluster routes.
- **Tenant/home-cluster routing:** derive the destination from an authenticated tenant identity or trusted routing policy, not an arbitrary user-controlled header. Log and test misrouting.
- **Sticky sessions:** session affinity can pin traffic to a failed cluster. Decide whether session state is portable or whether re-authentication/recovery is expected.
- **Ingress vs east-west gateway:** ingress handles an entry path into a cluster; east-west gateways are a controlled cross-cluster path in some mesh/interconnect designs. Neither automatically grants application authorization.
- **Endpoint drain:** stop new requests, allow bounded in-flight completion, then remove the endpoint. Long-lived streams and connection pools need separate handling.
- **Avoid double failover:** client fallback + gateway retries + mesh retries can create loops and amplify load. Assign a retry owner and end-to-end budget.

### 5.4 Worked example A — shared read-only feature service

**Assumptions:** feature values are read-only, a local snapshot can be at most 60 seconds stale, and caller identity is authenticated. These are illustrative assumptions, not measured facts.

**Request flow:** east checks local snapshot; if it is within the age bound, it responds locally. If not, it makes one bounded remote request over TLS. On failure, it may return an explicitly marked stale snapshot if still within the policy; otherwise it returns a controlled error.

**Selected pattern:** local-first application routing plus a private remote endpoint. This is lighter than a full mesh for one dependency.

**Security:** hostname validation, trusted CA, workload/application identity, authorization by operation, rate limits, and audit logs.

**Telemetry:** source/destination cluster, request outcome, latency histogram, fallback rate, snapshot age, and dependency error class.

**Rejected alternative:** synchronous-only remote RPC because it would make east availability depend on west for every request.

### 5.5 Worked example B — migrate a service from west to east

**Assumptions:** both versions can serve the same API contract during migration; data ownership is explicit.

1. Deploy and verify the east version without routing user traffic.
2. Run synthetic tests against east directly.
3. Route a small approved share to east using one verified traffic-shifting mechanism.
4. Compare error rate, p95/p99 latency, saturation, and business correctness by destination.
5. Increase traffic only after a review gate.
6. Roll back routing to west if the gate fails; do not assume rollback also reverses data writes.
7. Remove west only after traffic, dependency, and data ownership checks pass.

**Rejected alternative:** change all clients at once, because the blast radius and diagnosis ambiguity are larger.

### 5.6 Worked example C — tenant/home-cluster service

**Assumptions:** each tenant has an authoritative home cluster and a request must not silently cross into another tenant's data plane.

Routing should derive the home cluster from trusted server-side tenant metadata. If the home cluster is unavailable, fail explicitly or queue an operation if product semantics permit. Do not automatically send a write to a different cluster unless data ownership and idempotency are designed for it.

**Rejected alternative:** choose the destination from an untrusted `X-Region` header, because a client could steer requests across isolation boundaries.

### 5.7 Failure semantics and performance

| Failure | User-visible symptom | Safe first response | Do not do |
|---|---|---|---|
| Remote cluster unavailable | Connect timeout/refusal | Fail fast after deadline; use approved local fallback | Retry indefinitely |
| East-west gateway unavailable | Many services fail through one path | Confirm gateway/path, halt rollout, preserve local paths | Change unrelated DNS blindly |
| Interconnect partition | Some endpoints work, others fail | Treat as gray/partitioned; bound concurrency and retry | Assume hard-down detection is immediate |
| Packet loss/high latency | p99 rises; intermittent timeouts | Inspect source/destination path and queueing; reduce load | Increase retries without a budget |
| Remote DNS failure | Lookup errors/timeouts | Separate resolver failure from route failure; use approved fallback | Treat DNS as a health proxy |
| Stale endpoint | Requests hit drained/deleted backend | Mark endpoint set stale/unavailable; refresh/reconcile | Keep advertising stale endpoint as healthy |
| Expired/mismatched certificate | TLS handshake fails | Verify hostname, validity, trust chain, and rotation state | Disable TLS verification |
| One-sided trust rotation | Only one direction or cluster pair fails | Restore overlap and verify both sides | Replace trust roots simultaneously without overlap |
| Retry storm | Remote recovery is overloaded | Stop extra retries, reduce concurrency, apply backpressure | Add another retry layer |
| Ambiguous timeout | Caller does not know if write committed | Use idempotency/status reconciliation | Blindly replay non-idempotent write |
| Endpoint drain | Long requests fail at termination | Allow bounded grace; test streams/connections | Remove endpoint before observing in-flight behavior |
| High transfer volume | Unexpected cost and saturation | Attribute bytes by service/pair; batch/cache where valid | Guess egress price or ignore volume |
| Chatty dependency | Many remote calls per user request | Reduce round trips, batch, localize data | Add a mesh and assume latency disappears |

Use M10's timeout, backpressure, load-shedding, retry-budget, and circuit-breaker principles. No single mechanism guarantees resilience.

## 6. Level 4 — Production Operations, Security, and Reliability

### 6.1 SLOs and capacity

Define SLOs from a service's user impact and measured baseline. Numeric thresholds below are examples to customize, not universal targets.

| SLI | Example definition | Break down by |
|---|---|---|
| Cross-cluster request success | Successful eligible requests / total eligible requests | source cluster, destination, service, route |
| Tail latency | p95/p99 end-to-end request duration | source/destination pair, operation |
| Endpoint freshness | age since last successful endpoint observation/reconciliation | service, source cluster, destination |
| Gateway/interconnect health | availability, saturation, connection errors, queueing | gateway, path, cluster pair |
| DNS | lookup success and latency | resolver, suffix, cluster |
| Certificate health | expiry horizon, trust-bundle convergence, handshake failures | certificate identity, cluster pair |
| Dependency governance | unapproved observed edges | caller, callee, environment |
| Transfer budget | bytes by service and cluster pair | service, route, data class |

Separate user-facing SLIs from internal metrics. A global average can hide a failing cluster pair. Measure connection and stream limits, concurrency, gateway headroom, backpressure, and retry traffic. Do not present laptop measurements as production capacity estimates.

### 6.2 Observability

Capture request count, error count, latency histograms, retries, fallback, and circuit-breaker state. Propagate trace context across the boundary and correlate logs using request/trace IDs. Include source and destination cluster attribution, service, route, status class, and a controlled region-like label. Avoid high-cardinality labels such as user IDs, arbitrary URLs, or request IDs in metrics.

Useful alerts include:
- new cross-cluster dependency edge not in the declared allow-list;
- remote request success/latency SLO burn;
- endpoint observation age above its chosen threshold;
- DNS lookup failure or latency increase;
- gateway/interconnect saturation;
- certificate nearing expiry or trust-bundle mismatch;
- unexpected cross-cluster bytes;
- local fallback rate or stale-read age above policy.

M11 owns general observability foundations; M14 Unit 8 owns broader fleet aggregation and governance. This unit focuses on source/destination attribution and path evidence.

### 6.3 Security and zero trust

- Keep east-west exposure private by default; use a controlled gateway where appropriate.
- Apply network restrictions at both ends when supported. A flat route between all pod CIDRs is not a default recommendation.
- Separate authentication (who is the caller?) from authorization (may this caller perform this action?).
- Treat ServiceAccount token audiences, issuers, and trust bindings as cluster-specific until verified. Reuse M09's identity/secret-management patterns.
- Use mTLS or equivalent peer authentication when the chosen architecture supports it, but do not assume mTLS alone authorizes a business action.
- Prefer narrow trust relationships. A shared root CA increases the blast radius if its private key is compromised.
- Plan overlap-based rotation, revocation, expiry monitoring, and recovery.
- Use short-lived credentials and keep keys out of Git, logs, and evidence artifacts.
- Source IP allow-listing can be a defense-in-depth network control, but it is not workload identity and not application authorization.
- Apply rate limits, request-size limits, audit logs, and negative tests.
- For compromise, revoke identity and credentials, block the path, confirm that policy denies the cluster even if its IP remains permitted, then restore only after validation.

### 6.4 Trust-bundle rotation

A safe general pattern is:
1. inventory all peers and trust consumers;
2. publish the new trust anchor alongside the old anchor where the system supports overlap;
3. verify both sides trust the overlap bundle;
4. rotate serving certificates and identities in a controlled order;
5. observe successful handshakes from both directions;
6. remove the old anchor only after confirming no legitimate peer still depends on it;
7. retain a rollback plan and evidence.

Exact sequence depends on CA and mesh implementation `[VERIFY]`. The one-sided failure exercise should use only lab certificates and a disposable path. Do not leave the clusters in a mixed or partially trusted state.

### 6.5 Operational complexity and upgrades

- Record the compatibility matrix for Kubernetes, CNI, mesh/interconnect, Gateway API, cert-manager, and MCS implementation.
- Upgrade a canary cluster first, test cross-cluster requests, then proceed under an explicit gate.
- Use ephemeral two-cluster CI for manifest, compatibility, and failure tests where practical.
- Track endpoint propagation, certificate convergence, and trust status.
- Define service owner, caller owner, data owner, SLO owner, and incident escalation for every dependency.
- Require N/N-1 API compatibility for staggered rollouts when relevant.
- Keep rollback and exit plans for project-specific networking and mesh features.
- Commands such as `subctl diagnose`, `cilium clustermesh status`, or `istioctl` multi-cluster checks are version/context-sensitive `[VERIFY]`; confirm official syntax before running.

### 6.6 “Replicate, don't call” as a heuristic

`[ASSUMPTION]` **Replicate, don't call** is a useful design heuristic when data can safely be made available near the consumer. It is not a universal law. Evaluate freshness, consistency, privacy, residency, retention, write authority, and stale-read behavior. A local replica can improve availability but create stale or conflicting data; a synchronous call may be required for authoritative decisions.

Cross-links:
- M14 Unit 5: user-facing global entry, global load balancing, and DNS failover.
- M14 Unit 6: active-active/active-passive and home-region patterns.
- M14 Unit 7: replication and consistency.
- M14 Unit 8: fleet observability and policy governance.
- M15: cross-cluster egress/transfer cost.
- M16: service ownership/catalog and dependency contracts.
- M13: fault injection and disaster-recovery concepts.

### 6.7 L4 failure drills

| Drill | Hypothesis | Preconditions | Evidence | Recovery |
|---|---|---|---|---|
| Kill/block east-west gateway | Local requests continue; remote calls fail within deadline | disposable lab route only | request latency/errors, fallback, gateway logs | restore gateway/path; verify TLS and request success |
| Slow/partition interconnect | bounded client behavior prevents retry storm | verified fault-injection method; otherwise deterministic app fault | expected vs observed timing, retries, concurrency | remove fault; verify baseline |
| DNS forward failure | lookup failure is distinct from application health | isolated resolver config with backup | lookup errors, cache timing, client result | restore config; test positive resolution |
| Stale endpoint | stale record is detected or request fails visibly | toy fixture or disposable endpoint | endpoint age, request failure, alert | reconcile endpoint; confirm fresh observation |
| Expired certificate | TLS fails closed | lab-only certificate | TLS error, expiry, alert | rotate certificate and verify hostname/trust |
| One-sided trust rotation | cross-cluster handshake fails in affected direction | lab-only CA and rollback bundle | handshake errors by direction | restore overlap, converge both sides |
| Compromised-cluster isolation | removed identity/path prevents cross-cluster calls | explicit kill-switch plan | denied network request and denied identity | restore only after incident gate and evidence review |

If `tc` or Chaos Mesh is considered, verify it works in the actual WSL2/kind environment and inspect the exact target first `[VERIFY]`. Otherwise use a deterministic application or gateway fault. Never run an unverified fault command on the host or production network.

## 7. Hands-On Labs

**Shared rules for all labs:** contexts are explicit; cluster names are exactly `stage2e-east-lab` and `stage2e-west-lab`; expected output is representative, not observed; save evidence under a local path such as `evidence/lab-01/`; never save secrets. Every lab must be run against disposable resources only. Stop if context identity, endpoint exposure, or cleanup scope is unclear.

### Lab 1 — Cross-cluster call through an exposed endpoint

- **Level/time:** L2; 2–4 hours.
- **Objective:** serve `feature-service` in west, expose it through one private lab-safe path with TLS, resolve a stable hostname, call it from east through a local abstraction, and prove the serving cluster.
- **Prerequisites:** two contexts verified; non-overlapping cluster CIDR plan reviewed; route feasibility tested; local CA material generated; one endpoint approach chosen.
- **Topology:** east caller → local abstraction/client → TLS hostname → selected private endpoint → west service.
- **Steps:**
  1. Apply the sample `feature-service.yaml` to west and wait for rollout.
  2. Verify service/pods and the selected endpoint from the host before configuring east.
  3. Configure exactly one endpoint path (gateway/Ingress, NodePort, or a temporary port-forward for a limited proof). Do not treat port-forward as production networking.
  4. Install the server certificate with SAN matching `features.west.lab.internal` using the selected TLS termination mechanism.
  5. Verify hostname and CA from the host with `curl --cacert`; never use `-k`.
  6. Configure the east caller to use the stable hostname and local Service abstraction.
  7. Add a client deadline, maximum attempts, backoff/jitter, retry budget, fail-fast behavior, and local-first fallback for the read-only operation.
  8. Add `served-by-cluster` and fallback metadata to the response or trace.
  9. Stop the west app or block only the lab path, then verify the local snapshot path continues serving. Restore and verify again.
- **Positive tests:** expected hostname resolves; TLS hostname/trust checks pass; response identifies west; east local fallback works during remote loss.
- **Negative tests:** wrong CA fails; wrong hostname fails; west unavailable does not create unbounded retries; stale fallback beyond allowed age is rejected.
- **Representative evidence:** sanitized curl response, TLS verification output, client retry/fallback counters, context identity, endpoint path diagram.
- **Common mistakes:** assuming `ExternalName` proxies; certificate SAN mismatch; public binding; unbounded retries; treating port-forward as stable routing.
- **Cleanup:** remove only named lab resources with explicit context; delete local test keys securely after retaining no sensitive material.
- **Pass criteria:** successful verified TLS call and correct fallback semantics; no disabled certificate verification.
- **Fidelity limit:** does not prove WAN routing, regional independence, or production gateway capacity.

### Lab 2 — NetworkPolicy and ingress allow-listing

- **Level/time:** L2; 1–3 hours.
- **Objective:** demonstrate permitted and denied paths at network and application layers.
- **Prerequisites:** selected endpoint path works; confirm the CNI actually enforces NetworkPolicy.
- **Steps:**
  1. Record the CNI and current policy state in both contexts.
  2. Create a narrowly scoped policy in west for the actual pod-to-pod path if the lab network architecture supports it. If traffic reaches a gateway from outside the cluster, enforce the corresponding gateway ingress control rather than assuming pod NetworkPolicy covers it.
  3. Permit only the intended lab caller/path.
  4. Test from the permitted caller.
  5. Test from an unauthorized pod/path.
  6. Send a request without required application authentication and verify the application rejects it.
  7. Remove/restore only the lab policy and verify expected behavior.
- **Positive/negative tests:** allowed network path succeeds; unauthorized path is denied; unauthenticated application request is rejected; source IP alone does not bypass application authorization.
- **Evidence:** policy manifests, CNI identity/version, allow/deny outputs, application auth response.
- **Common mistakes:** assuming every CNI enforces policy; confusing gateway source IP with caller identity; using an overly broad selector.
- **Cleanup:** delete the named lab policy and test pods only after confirming exact context and namespace.
- **Pass criteria:** both network and application controls are demonstrated or a limitation is explicitly recorded.
- **`[VERIFY]`:** kind networking and source-IP preservation can vary by route/controller.

### Lab 3 — Cross-cluster DNS forwarding and failure coupling

- **Level/time:** L2; 2–3 hours.
- **Objective:** demonstrate remote-name resolution and what fails when the forwarding dependency fails.
- **Prerequisites:** stable endpoint and TLS request already work independently of DNS; use a disposable DNS configuration.
- **Steps:**
  1. Select a unique lab suffix and a resolver path. Record the current CoreDNS configuration before changes.
  2. Verify official CoreDNS syntax for the installed version. `[VERIFY]`
  3. Configure a stub/forwarding rule only in the disposable east cluster.
  4. Test lookup and an HTTPS request; capture resolver latency and request outcome.
  5. Disable or block only the lab forwarding path.
  6. Repeat lookup/request and record errors, timeout, and cache effects.
  7. Restore the original configuration and verify the name and TLS request recover.
- **Positive/negative tests:** remote name resolves before fault; lookup fails or degrades after fault; application does not retry without bound; direct approved fallback behaves as designed.
- **Evidence:** before/after CoreDNS config diff, `nslookup`/`dig` output, request trace, timestamps.
- **Common mistakes:** assuming DNS is a proxy; assuming TTL forces all clients to discard cached addresses; changing the default resolver without a rollback.
- **Cleanup:** restore saved CoreDNS configuration, verify pods are healthy, remove temporary records.
- **Pass criteria:** failure coupling and recovery are evidenced without leaving DNS altered.
- **Fallback:** guided analysis if the lab cannot safely configure a stub domain.

### Lab 4 — MCS-style endpoint-mirroring toy

- **Level/time:** L2; 2–4 hours.
- **Objective:** model endpoint freshness and stale endpoint failure without claiming MCS conformance.
- **Prerequisites:** understand Service and EndpointSlice ownership; use fixtures or disposable namespaces.
- **Toy input fixture:**

```json
{
  "service": "feature-service",
  "source_cluster": "stage2e-west-lab",
  "observed_at": "2026-10-29T10:00:00Z",
  "max_age_seconds": 30,
  "endpoints": [
    {"address": "192.0.2.10", "port": 8080, "ready": true}
  ]
}
```

The address is documentation-only TEST-NET space and must not be used as a live endpoint.

- **Steps:** implement a small offline validator that checks service identity, timestamp age, readiness, port, and address family; mark expired observations unavailable; test deletion and termination as explicit fixture states. If a live EndpointSlice is mirrored, use a disposable namespace, narrow RBAC, ownership labels, and verified API semantics.
- **Positive tests:** fresh ready endpoint is accepted; valid port/address-family fixture passes.
- **Negative tests:** stale timestamp rejected; unready/deleted endpoint rejected; unsupported address family rejected; wrong service identity rejected.
- **Evidence:** fixture inputs, test output, limitations list.
- **Common mistakes:** calling the toy a controller; assuming an endpoint object updates itself; retaining stale endpoints as healthy.
- **Cleanup:** remove only owned lab record/resource; verify no unexpected EndpointSlices remain.
- **Pass criteria:** freshness tests pass and all production gaps are listed.
- **Fidelity limit:** does not prove MCS behavior, watch correctness, or controller safety.

### Lab 5 — Failure drills: remote loss, latency/loss, certificate expiry, gateway block

- **Level/time:** L2/L4; 2–5 hours.
- **Objective:** run feasible faults one at a time and prove bounded retries/local continuity.
- **Prerequisites:** working request path, telemetry, and rollback command for each fault.
- **Steps:** record baseline; choose one fault; write expected behavior and abort condition; inject deterministic application/gateway failure or a preflight-verified network fault; observe requests; stop the fault; verify recovery; only then proceed to the next fault.
- **Fault cases:** remote app unavailable; latency/packet loss using `tc`/Chaos only after `[VERIFY]`; expired lab certificate; gateway path blocked.
- **Positive/negative tests:** local-first route continues where valid; retry count remains bounded; TLS fails closed for expired cert; gateway block denies remote path.
- **Evidence:** expected-vs-observed table, traces, retry counts, fault start/stop times.
- **Common mistakes:** combining faults, injecting on the host instead of a disposable path, skipping post-recovery checks.
- **Cleanup:** remove injected fault, restore certificate/path, verify both clusters and local paths.
- **Pass criteria:** each fault has a distinct diagnosis and verified recovery.
- **Fallback:** deterministic app-level error injection if kind cannot reproduce network faults faithfully.

### Lab 6 — Cross-cluster trust rotation

- **Level/time:** L3/L4; 2–4 hours.
- **Objective:** rotate lab trust with overlap and demonstrate one-sided failure.
- **Prerequisites:** working TLS request and local-only CA/key material.
- **Steps:** inventory trust consumers; create a second lab CA; publish overlap trust on both sides using the chosen implementation; rotate server certificate; verify both directions; remove old trust only after all peers are verified; in a separate controlled round, omit new trust on one side and observe handshake failure; restore overlap and recover.
- **Positive tests:** both peers trust the new cert during overlap; post-rotation request succeeds.
- **Negative tests:** one-sided trust causes expected TLS failure; wrong/expired cert fails closed.
- **Evidence:** certificate fingerprints/expiry (not private keys), trust-bundle versions, handshake result by direction.
- **Common mistakes:** rotating both sides at once; exposing private keys; removing old trust too early.
- **Cleanup:** restore known-good lab trust, remove test keys, verify all handshakes.
- **Pass criteria:** overlap and one-sided failure are explained with evidence.
- **`[VERIFY]`:** exact trust-distribution procedure depends on selected gateway/mesh.

### Lab 7 — Cross-cluster dependency audit

- **Level/time:** L3; 2–3 hours.
- **Objective:** compare declared dependencies with observed request edges.
- **Declared allow-list example:**

```yaml
declared_edges:
  - source_cluster: stage2e-east-lab
    source_service: feature-consumer
    destination_cluster: stage2e-west-lab
    destination_service: feature-service
    purpose: read-only-feature-lookup
```

- **Steps:** gather declared edges from service metadata/ADR; collect observed edges from gateway logs, traces, or flow evidence available in the lab; normalize source/destination/service; compare; emit an alert/report for an undeclared edge. If telemetry is synthetic, label it.
- **Positive tests:** declared edge is recognized; no unexpected edge produces clean report.
- **Negative tests:** new destination, unknown source, or missing declaration raises a report.
- **Evidence:** allow-list, sanitized sample observations, diff report, test output.
- **Common mistakes:** assuming absence of telemetry means absence of dependency; including high-cardinality identifiers; confusing DNS queries with successful application calls.
- **Cleanup:** remove temporary test records and telemetry fixtures.
- **Pass criteria:** unapproved edge is detected and the limitation of observation coverage is documented.

### Lab 8 — Architecture selection across six scenarios

- **Level/time:** L3; 2 hours.
- **Objective:** select patterns from requirements and defend rejected options.
- **Scenario set:**
  1. One read-only feature API, strict latency budget, local snapshot possible.
  2. A service migration needs a staged traffic shift and rollback.
  3. A tenant must remain in its home cluster; cross-tenant fallback is forbidden.
  4. Many clusters need supported service export/import and a standard implementation.
  5. A compatible CNI environment requires routed cross-cluster connectivity.
  6. A workflow can tolerate minutes of freshness delay and should survive remote API outages.
- **Steps:** score each scenario on sync/async, latency, identity, cluster count, endpoint churn, ops maturity, cost, and failure isolation; record an ADR; identify one rejected alternative.
- **Model answer:** (1) local cache plus bounded private endpoint; (2) staged app/Gateway/mesh traffic shift after feature verification; (3) app-level home-cluster routing and explicit fail-closed behavior; (4) MCS implementation after compatibility verification; (5) compare Submariner/Cilium Cluster Mesh against network requirements; (6) async queue/replication. These are conditional examples, not universal answers.
- **Evidence:** completed scorecard and ADR.
- **Pass criteria:** choices cite requirements and limitations rather than popularity.

### Lab 9 — Optional deep dive: choose one only after preflight

Choose **exactly one**: Linkerd multicluster/service mirroring, Cilium Cluster Mesh, or Submariner. Do not install multiple systems together.

- **Level/time:** advanced; time depends on chosen system and compatibility.
- **Prerequisites:** official current compatibility docs reviewed; free disk/RAM measured; rollback plan written; existing cluster state backed up or disposable.
- **Preflight:** confirm Kubernetes/kind versions, CNI requirements, kernel/network requirements, installation footprint, DNS assumptions, trust model, and supported operating mode. `[VERIFY]`
- **Steps:** follow the selected project's official guide for the pinned release; do not improvise flags; validate connectivity, discovery, identity, and authorization separately; capture diagnostics; uninstall only using the version-matched documented procedure.
- **Evidence:** exact versions, compatibility references, preflight decision, test output, cleanup evidence.
- **Stop criteria:** unsupported WSL2/kind topology, resource pressure, ambiguous destructive action, or inability to revert.
- **Fallback:** guided architecture review of official documentation. This can establish conceptual understanding, not live compatibility.
- **Pass criteria:** one option evaluated with explicit prerequisites and no unsupported product-status claims.

### Lab 10 — Isolate a compromised cluster

- **Level/time:** L4; 2–4 hours.
- **Objective:** simulate compromise in one lab cluster and prove the cluster loses both network path and authorized identity.
- **Prerequisites:** known-good baseline, local-only credentials, kill-switch plan, service owner identified.
- **Steps:** define the selected cluster as suspected compromised; freeze cross-cluster changes; remove/deny its gateway route or network policy; revoke/disable its lab identity or trust binding using the selected system's verified process; test calls in both directions; verify the unaffected cluster's local path; restore only after validation and evidence capture.
- **Positive tests:** unaffected local path remains available; restored legitimate identity succeeds only after approval.
- **Negative tests:** compromised cluster cannot call across the boundary even if source IP remains allow-listed; stale credentials cannot reauthorize it.
- **Evidence:** incident timeline, before/after authorization tests, network policy/gateway state, trust version.
- **Common mistakes:** relying on IP alone; restoring before credential revocation; revoking trust without knowing collateral impact.
- **Cleanup:** restore known-good lab identity/path, verify expected allow/deny behavior, remove temporary rules and credentials.
- **Pass criteria:** network and identity controls independently enforce isolation and recovery is gated.

## 8. Incident Analysis: Diagnose, Fix, Prevent

The following incidents are hypothetical teaching scenarios. Timelines, impact descriptions, and command outputs are synthetic unless an operator captures real evidence. Use the diagnostic approach, not the fictional numbers, as the reusable lesson.

### Incident 1 — Remote dependency defeats regional independence

- **Symptoms / misleading signal:** cluster B's local API is Ready, but requests fail when cluster A's feature service is down. Local health checks appear green.
- **Synthetic timeline:** T+0 A becomes unavailable; T+1 B's request latency rises; T+3 B's worker pool saturates; T+5 alerts show B errors despite local pods Ready.
- **Impact/blast radius:** services in B that synchronously call A are affected; local-only routes may remain healthy.
- **Hypotheses:** remote DNS failure, route loss, A outage, dependency timeout too long, retry amplification.
- **Safe tests:** compare local endpoint success with remote dependency success; inspect traces by source/destination; run a bounded request to A; check DNS and TLS independently.
- **Root cause:** architecture encoded a synchronous dependency without local fallback or explicit availability contract.
- **Immediate mitigation:** shed optional remote calls; fail fast; use a safe local snapshot if freshness policy permits.
- **Durable fix:** dependency inventory, local cache/replica or async design, bounded deadlines, per-edge SLO.
- **Prevention/alerting:** alert on new edges and remote dependency latency; test remote loss.
- **What would have prevented it?** A dependency review that treated cross-cluster calls as coupling.
- **Lesson:** local pod readiness is not end-to-end service availability.

### Incident 2 — Retry storm during partial recovery

- **Symptoms:** west begins recovering, but request volume and p99 increase; every layer reports retries.
- **Timeline:** synthetic T+0 west returns intermittently; T+1 client retries; T+2 gateway retries; T+3 downstream load rises above recovery capacity.
- **Impact:** recovery takes longer; unrelated calls share exhausted connections or worker pools.
- **Hypotheses:** retry multipliers, no jitter, excessive concurrency, health check mismatch.
- **Safe tests:** inspect attempts per logical request; compare configured client/gateway/mesh retries; use a controlled failure fixture.
- **Root cause:** retries were configured independently with no global budget.
- **Immediate mitigation:** disable one retry layer or lower attempts; cap concurrency; shed load.
- **Durable fix:** assign a retry owner, propagate deadlines, use jitter and retry budgets, apply bulkheads.
- **Prevention:** alert on retry ratio and downstream attempt amplification; rehearse recovery.
- **What would have prevented it?** End-to-end retry budget and a tested failure timeline.
- **Lesson:** retries consume the capacity needed to recover.

### Incident 3 — One-sided mTLS CA/trust rotation

- **Symptoms:** some cross-cluster calls fail TLS while local calls succeed; failures differ by direction.
- **Timeline:** synthetic T+0 new CA is installed on east only; T+1 west presents a certificate east accepts but west-side callers reject; T+2 cross-cluster error rate rises.
- **Impact:** affected peer paths fail closed.
- **Hypotheses:** hostname/SAN mismatch, expiry, trust bundle not converged, wrong certificate served.
- **Safe tests:** inspect certificate chain/fingerprint/expiry; test both directions; compare trust-bundle versions; do not log private keys.
- **Root cause:** rotation lacked an overlap window and per-peer verification gate.
- **Immediate mitigation:** restore known-good overlap trust or roll back the lab certificate.
- **Durable fix:** inventory consumers, overlap old/new trust, rotate serving certs, verify both directions, remove old trust last.
- **Prevention:** trust-convergence metric and expiry alert.
- **What would have prevented it?** A staged trust rotation runbook.
- **Lesson:** a successful local TLS check does not prove cross-cluster trust.

### Incident 4 — Interconnect gray failure

- **Symptoms:** no hard-down alert, but p99 doubles and some requests time out.
- **Timeline:** synthetic T+0 packet loss begins; T+1 health checks still pass; T+2 queueing and tail latency rise; T+4 clients retry.
- **Impact:** intermittent errors and reduced capacity.
- **Hypotheses:** loss/latency, gateway saturation, DNS delays, endpoint churn, application slowdown.
- **Safe tests:** compare request traces, retransmit/connection metrics where available, gateway saturation, and local-only latency.
- **Root cause:** monitoring tracked availability but not tail latency and path quality.
- **Immediate mitigation:** reduce concurrency, bound retries, route local where valid.
- **Durable fix:** pair-level latency SLO, saturation and packet-loss telemetry, tested fail-fast behavior.
- **Prevention:** gray-failure drills and alerting on latency/error-budget burn.
- **What would have prevented it?** Observability by source/destination pair.
- **Lesson:** “reachable” does not mean “healthy enough.”

### Incident 5 — Stale imported endpoint

- **Symptoms:** discovery succeeds but requests hit a drained or deleted backend.
- **Timeline:** synthetic T+0 backend is removed; T+1 mirror remains stale; T+2 requests fail despite DNS and Service object appearing present.
- **Impact:** callers experience intermittent connection errors or stale routing.
- **Hypotheses:** endpoint controller lag, stale mirror, readiness/termination race, cache retention.
- **Safe tests:** compare source Service/EndpointSlices with imported/mirrored records and timestamps; verify endpoint readiness and port.
- **Root cause:** endpoint lifecycle was manually mirrored without freshness/deletion semantics.
- **Immediate mitigation:** mark the remote endpoint unavailable and remove only the stale lab record after ownership check.
- **Durable fix:** use a supported implementation or a controller with freshness, ownership, and deletion guarantees.
- **Prevention:** endpoint age metric and stale endpoint alert.
- **What would have prevented it?** Explicit lifecycle ownership.
- **Lesson:** discovery data has a freshness contract.

### Incident 6 — Publicly exposed east-west gateway

- **Symptoms:** unexpected traffic reaches an internal service; network allow-list exists but does not authenticate callers.
- **Timeline:** synthetic T+0 gateway binds publicly; T+1 scan or unexpected request appears; T+2 logs show requests without valid service identity.
- **Impact:** expanded attack surface and possible data exposure.
- **Hypotheses:** wrong bind address, public LoadBalancer, permissive route, missing auth policy.
- **Safe tests:** inspect gateway Service/address, cloud exposure only in a real reviewed environment, route policy, auth logs, and intended callers.
- **Root cause:** internal service exposure was treated as trusted based on network location.
- **Immediate mitigation:** close public route, restrict network path, require authenticated identity.
- **Durable fix:** private-by-default exposure, authorization, request limits, audit.
- **Prevention:** deployment policy and exposure scans.
- **What would have prevented it?** A reviewed trust boundary and negative auth test.
- **Lesson:** internal routing is not identity.

### Incident 7 — Undeclared dependency discovered during failover

- **Symptoms:** failover succeeds at the traffic layer but requests still fail because an undocumented service calls the original cluster.
- **Timeline:** synthetic T+0 failover begins; T+1 unexpected edge appears in traces; T+2 hidden dependency becomes unavailable.
- **Impact:** partial outage with confusing ownership.
- **Hypotheses:** hard-coded hostname, untracked callback, background worker, stale client config.
- **Safe tests:** inspect traces/gateway logs/flow data, search config for destination hostname, compare observed edges to allow-list.
- **Root cause:** no dependency inventory and no alert for new edges.
- **Immediate mitigation:** restore the dependency if safe; freeze further routing changes; notify owner.
- **Durable fix:** declare service dependencies and update failover tests.
- **Prevention:** automated declared-vs-observed comparison.
- **What would have prevented it?** Dependency contract and ownership.
- **Lesson:** a failover plan is only as complete as its dependency graph.

### Incident 8 — Overlapping pod CIDRs discovered during interconnect setup

- **Symptoms:** routes collide or one cluster's addresses are ambiguous after connecting clusters.
- **Timeline:** synthetic T+0 interconnect configuration begins; T+1 overlap is discovered; T+2 teams attempt ad hoc route overrides.
- **Impact:** unreliable or misrouted traffic; risk of broad outage.
- **Hypotheses:** overlapping pod/service ranges, incorrect route export, host/Docker subnet conflict.
- **Safe tests:** collect actual pod/service CIDRs from both lab contexts and Docker networks; compare before changing routes.
- **Root cause:** topology planning omitted cross-cluster address allocation.
- **Immediate mitigation:** stop interconnect changes; restore previous routes; do not paper over with unreviewed static routes.
- **Durable fix:** re-plan non-overlapping ranges or use a supported translation design only if explicitly justified.
- **Prevention:** CIDR registry and preflight validation.
- **What would have prevented it?** Unit 1 topology review before enabling connectivity.
- **Lesson:** address planning is an architectural prerequisite, not an afterthought.

## 9. Architecture Decision Record Exercise

### 9.1 Fill-in-ready ADR template

```markdown
# ADR: <cross-cluster service pattern>

- Status: Proposed | Accepted | Superseded
- Date:
- Owners: service, platform, security, operations
- Context/problem:
- Functional requirements:
- Non-functional requirements:
- Request-path latency budget:
- Expected request rate and transfer volume:
- Options considered:
- Decision and rationale:
- Discovery and routing model:
- Connectivity/CNI/mesh assumptions:
- Identity, mTLS, trust domains, authorization:
- Timeouts, retries, circuit breaker, fallback:
- DNS and endpoint freshness assumptions:
- Observability, SLOs, alerts:
- Failure modes and blast radius:
- Cost and operational burden:
- Upgrade/version-skew plan:
- Rollback and migration plan:
- Validation evidence:
- Rejected alternatives:
- Open [VERIFY] items:
- What the laptop lab does not prove:
```

### 9.2 Worked example: read-only feature service

- **Status:** Proposed.
- **Date:** 2026-10-29.
- **Owners:** feature-service owner, platform networking, security, on-call.
- **Context:** east consumers sometimes need a feature value served by west. `[ASSUMPTION]` The response can use a local snapshot up to 60 seconds old; all authoritative writes remain local.
- **Requirements:** hostname-verified TLS, authenticated callers, bounded remote deadline, local-first fallback, request attribution, no public exposure.
- **Latency budget:** `[ASSUMPTION]` remote request deadline of 500 ms for the lab design; validate from production measurements before adopting.
- **Traffic volume:** unknown until measured; collect requests/bytes by service pair before production rollout.
- **Options:** private endpoint; manual EndpointSlice; MCS; mesh; application-level routing; asynchronous replication.
- **Decision:** use a private, explicit endpoint and application-level local-first behavior initially. A full mesh or MCS implementation is not justified for one dependency unless future scale, identity, or policy requirements change.
- **Discovery/routing:** stable hostname `features.west.lab.internal`; east uses a local abstraction or client config that preserves the correct TLS hostname.
- **Connectivity:** one verified private gateway/host route; no assumption that pod CIDRs are connected.
- **Identity/security:** server certificate SAN matches hostname; caller authenticates using the selected app identity mechanism; authorization enforced at service/gateway; source IP is not identity.
- **Resilience:** one bounded retry at most for eligible idempotent reads; jitter, deadline, retry budget, and fail-fast state; local snapshot fallback with age metadata.
- **DNS/freshness:** local DNS forwarding is optional; if used, resolver failure is monitored. Endpoint freshness is measured at the selected endpoint/gateway/controller.
- **SLO/alerts:** request success and p95/p99 by pair; fallback rate; DNS failure; certificate expiry; unexpected dependency edge; transfer volume.
- **Failure/blast radius:** remote endpoint outage should affect only requests that cannot use a valid local snapshot.
- **Cost/operations:** local endpoint and app policy are lower complexity; real egress cost is not known until measured.
- **Upgrade/rollback:** test certificate, gateway, and client changes in the lab; route rollback must not assume it reverses data changes.
- **Validation evidence:** lab TLS positive/negative tests, bounded retry test, local fallback test, dependency audit.
- **Rejected alternatives:** synchronous-only RPC (couples availability); manual endpoint mirror as production control (stale lifecycle risk); mesh by default (higher operational burden for one edge).
- **Open `[VERIFY]`:** exact gateway API/controller, cert-manager trust distribution, installed Kubernetes versions, production identity mechanism, and actual endpoint path.
- **Lab limitation:** two kind clusters on one laptop do not prove WAN behavior, regional isolation, production SLOs, real egress cost, or provider load-balancer behavior.

## 10. Verification, Evidence, and Cleanup

### 10.1 Test matrix

| Test | Command/method | Expected representative result | Evidence | Does not prove |
|---|---|---|---|---|
| Discovery works | `getent hosts features.west.lab.internal` from the chosen caller environment | hostname resolves to intended lab endpoint | resolver output/time | route/TLS/auth success |
| Discovery fails safely | isolate lab forwarding dependency | lookup error/timeout is bounded | resolver logs and timing | production resolver behavior |
| Connectivity works | bounded HTTPS request from east | response received | trace and response headers | all paths/loads work |
| Connectivity fails | stop lab endpoint or block path | deadline expires; local path may continue | error class, retry count | real WAN partition behavior |
| TLS hostname/trust passes | `curl --cacert <lab-ca> https://features.west.lab.internal` | verified TLS | sanitized TLS output | application authorization |
| TLS failure | wrong CA or hostname in lab | verification fails | error and cert fingerprint | all client implementations behave identically |
| Authorization allows intended caller | authenticated request | allowed operation | audit event and response | all identities/policies |
| Authorization rejects unintended caller | omit/alter lab identity | denial | denial log | production IdP behavior |
| Endpoint fresh | compare source endpoint with mirror/controller observation | timestamps and endpoint set agree | endpoint snapshot | full MCS conformance |
| Stale endpoint detected | use expired fixture | marked unavailable | test output | live controller correctness |
| Local-first survives remote loss | inject remote app fault | valid local read returns with fallback marker | trace and age | correctness of all fallback data |
| Retry bounded | inspect attempts under fault | attempts stay within policy | client counters | fleet-wide retry budget |
| New dependency detected | add synthetic undeclared edge | report flags edge | diff report | unobserved traffic is absent |
| Kill switch works | remove route/identity in lab | cross-cluster call denied | before/after request and policy evidence | compromise containment in production |
| Recovery works | restore known-good route/trust | call succeeds after validation | timeline, cert version, request | long-term stability |

Every command that reads or mutates cluster state must include an explicit context. Commands run inside a pod should state which cluster/namespace the pod belongs to.

### 10.2 Evidence directory

Suggested local structure (create it as part of the exercise; it is not created by this lesson):

```text
evidence/
  lab-01/
    topology.md
    versions.txt
    tls-positive.txt
    tls-negative.txt
    request-trace.txt
    fallback-test.txt
  lab-02/
    policy.yaml
    allow-deny-results.txt
  lab-03/
    coredns-before.yaml
    coredns-after.yaml
    dns-timings.txt
  lab-04/
    fixtures/
    toy-tests.txt
    limitations.md
  lab-05/
    expected-vs-observed.md
    fault-timeline.md
  lab-06/
    cert-fingerprints.txt
    trust-convergence.md
  lab-07/
    declared-edges.yaml
    observed-edges-sanitized.json
    dependency-diff.md
  lab-08/
    scorecard.md
    adr.md
  lab-09/
    preflight.md
    version-matrix.md
    decision.md
  lab-10/
    incident-timeline.md
    kill-switch-results.md
```

Do not save private keys, tokens, full kubeconfigs, raw secrets, or sensitive request payloads. Keep evidence minimal and sanitized.

### 10.3 Cleanup checklist

1. Confirm both contexts still point to the named lab clusters.
2. List lab namespaces/resources before deletion.
3. Remove temporary DNS forwarding and restore saved CoreDNS configuration.
4. Remove only the lab TLS Secret/gateway/NetworkPolicy objects created for this lesson.
5. Remove the endpoint-mirroring toy records and verify no unexpected EndpointSlices remain.
6. Remove fault injection and verify normal request success.
7. Restore a known-good trust bundle and verify the request in both directions where applicable.
8. Delete only `cross-cluster-lab` resources in the intended contexts after inspecting their contents.
9. Remove local private keys and temporary credentials; retain only non-sensitive fingerprints and evidence.
10. If an optional mesh/interconnect was installed, use the official cleanup procedure for the exact pinned version and inspect dependent resources before uninstalling.

Representative scoped cleanup, only after inspection:

```bash
kubectl --context stage2e-east-lab -n cross-cluster-lab get all,configmap,secret,networkpolicy
kubectl --context stage2e-west-lab -n cross-cluster-lab get all,configmap,secret,networkpolicy
# After confirming these are disposable lesson resources:
kubectl --context stage2e-east-lab delete namespace cross-cluster-lab
kubectl --context stage2e-west-lab delete namespace cross-cluster-lab
```

The namespace deletion is destructive within that namespace. Do not run it if the namespace contains anything beyond this lab. Namespace deletion can remove resources not shown by `get all`; inspect all relevant namespaced resource types first. Never run a broad unscoped delete.

## 11. Knowledge Check and Self-Assessment

### Beginner

**1. Why does `feature-service.cross-cluster-lab.svc.cluster.local` not automatically resolve to west from east?**  
**Answer:** Ordinary Kubernetes Service DNS is cluster-scoped. Independent clusters have separate API and DNS/control-plane domains unless an explicit cross-cluster discovery mechanism is configured.  
**Tempting wrong answer:** “Because DNS is broken.” The name may resolve correctly in east to an east-side Service; it does not imply a global registry.

**2. What does a successful DNS lookup prove?**  
**Answer:** Only that a resolver returned an answer. It does not prove connectivity, TLS validity, authorization, or application health.  
**Tempting wrong answer:** “The service is healthy.” DNS is not a health check.

**3. What is the difference between discovery and connectivity?**  
**Answer:** Discovery tells the caller where to try; connectivity is the network path that carries the request. They can fail independently.

**4. Does an `ExternalName` Service proxy the HTTP request?**  
**Answer:** No. It provides DNS alias behavior; it does not proxy traffic or guarantee TLS hostname correctness.

**5. Why is source IP not sufficient identity?**  
**Answer:** IPs can be shared, translated, reassigned, or represent gateways rather than workloads. Use authenticated identity and authorization, with network controls as defense in depth.

**6. Why are two kind clusters not two regions?**  
**Answer:** They share a host and many failure domains; the lab cannot demonstrate WAN or independent regional failure behavior.

### Intermediate

**7. When is a manual EndpointSlice mirror risky?**  
**Answer:** When no controller owns endpoint readiness, updates, termination, address family, ports, stale detection, and deletion. A stale endpoint can remain discoverable after its backend disappears.

**8. What is the difference between MCS concepts and an implementation?**  
**Answer:** `ServiceExport`, `ServiceImport`, and `clusterset.local` are API concepts; an implementation supplies controllers and behavior, and may have specific connectivity requirements. Verify exact semantics for the selected version.

**9. What must a TLS client validate?**  
**Answer:** It should validate the certificate chain against intended trust anchors and validate the peer name/SAN against the hostname used. TLS success still does not prove business authorization.

**10. Why are unbounded retries dangerous?**  
**Answer:** They increase load during an outage and can delay recovery. Retries must be bounded by attempts, deadlines, jitter, and a budget.

**11. Should a remote read always fall back to local data?**  
**Answer:** No. Fallback is valid only if local data is correct enough for the operation and its staleness is visible. Authoritative writes or security-sensitive decisions may need to fail closed.

**12. What is the risk of DNS forwarding?**  
**Answer:** It introduces a dependency on the remote resolver/path. If that path fails, lookups may fail or stall; caches and client connection pools can affect recovery.

**13. Why is a low DNS TTL not a guarantee of immediate endpoint change?**  
**Answer:** Clients and intermediate resolvers may cache, applications may pin addresses, and established connections can outlive DNS records.

### Advanced

**14. A request times out after a non-idempotent write. Should the client retry?**  
**Answer:** Not blindly. The write may have committed even if the response was lost. Use idempotency keys or a status/reconciliation mechanism.

**15. What is the difference between a circuit breaker and a timeout?**  
**Answer:** A timeout bounds one operation's wait. A circuit breaker suppresses repeated attempts after a failure threshold and may permit limited probes during half-open state. Neither replaces concurrency limits or a retry budget.

**16. How can multiple retry layers amplify load?**  
**Answer:** Independent attempts multiply. If three layers each allow three total attempts, a logical request can cause up to \(3^3=27\) downstream attempts under some retry semantics. Configure one primary retry owner and a shared deadline/budget.

**17. What is a gray failure?**  
**Answer:** Partial or degraded operation—such as packet loss or high latency—where the path is not completely down. Availability-only probes can miss it.

**18. Why does one-sided CA rotation fail?**  
**Answer:** One peer may trust the new certificate while the other does not, causing direction-specific handshake failures. Use a verified overlap window and confirm both sides before removing old trust.

**19. How should a new observed dependency edge be handled?**  
**Answer:** Compare it with the declared allow-list, identify the owner and business purpose, and either approve/update the contract or investigate/block it. Absence from telemetry is not proof of absence.

**20. Why can a gateway allow-list still be insufficient?**  
**Answer:** The allowed source IP may be a shared node or gateway. It does not prove the calling workload identity or authorize its requested operation.

### Operations and calculations

**21. A request deadline is 500 ms. The client spends 100 ms connecting, 250 ms on attempt one, and then plans a 250 ms retry. Is the plan valid?**  
**Answer:** No; it already exceeds the 500 ms deadline before accounting for backoff and overhead. A retry must fit within the remaining end-to-end budget.

**22. An endpoint observation is 95 seconds old and the policy maximum is 30 seconds. Is it eligible?**  
**Answer:** No. It should be marked stale/unavailable or refreshed before routing. Do not silently treat it as healthy.

**23. Why can global average latency hide a failure?**  
**Answer:** A high-volume healthy cluster pair can dominate the aggregate and conceal a failing low-volume pair. Break down by source/destination, service, and route.

**24. What should happen when the home cluster for a tenant is unavailable?**  
**Answer:** Follow the tenant's explicit policy: fail closed, queue an eligible operation, or use a safe replica. Do not route to another tenant's or cluster's data authority without a correctness contract.

**25. What should an ADR record beyond the selected tool?**  
**Answer:** Requirements, latency budget, request volume, trust/authorization, discovery and connectivity assumptions, fallback, failure modes, SLOs, costs, upgrades, rollback, validation evidence, rejected options, unresolved verification, and lab limitations.

**26. What evidence is needed before declaring a cross-cluster path production-ready?**  
**Answer:** Version compatibility, positive/negative tests, identity and authorization tests, fault drills, measured SLOs, capacity and cost observations, dependency inventory, rollback/recovery evidence, and threat-model review in the target environment.

## 12. References and Version-Sensitive Verification

**Source-verification statement:** this document was authored without a live official-document verification pass. Therefore, version-sensitive behavior is intentionally marked `[VERIFY]`; no current compatibility, maturity, or product-status claim is asserted as live-checked. Before execution, consult official documentation for the exact installed release and record URLs/version numbers in the lab evidence.

Primary documentation to consult:

1. Kubernetes Services — `https://kubernetes.io/docs/concepts/services-networking/service/`
2. Kubernetes DNS for Services and Pods — `https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/`
3. Kubernetes EndpointSlices — `https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/`
4. Kubernetes NetworkPolicy — `https://kubernetes.io/docs/concepts/services-networking/network-policies/`
5. Kubernetes ServiceAccounts and workload credentials — `https://kubernetes.io/docs/concepts/security/service-accounts/`
6. CoreDNS official documentation — `https://coredns.io/manual/toc/`
7. Gateway API documentation — `https://gateway-api.sigs.k8s.io/`
8. cert-manager documentation — `https://cert-manager.io/docs/`
9. Multi-Cluster Services API project/specification documentation — verify the current official repository and the chosen implementation/version `[VERIFY]`.
10. Submariner official documentation — verify current installation, supported topology, and diagnostic commands `[VERIFY]`.
11. Cilium Cluster Mesh documentation — verify Cilium/Kubernetes compatibility and current setup commands `[VERIFY]`.
12. Linkerd multicluster documentation — verify current service-mirroring model and prerequisites `[VERIFY]`.
13. Istio multi-cluster documentation — verify primary-remote/multi-primary topology, gateways, trust, and version compatibility `[VERIFY]`.
14. SPIFFE/SPIRE documentation if workload identity/trust domains are selected — `[VERIFY]`.
15. kind documentation for networking and port mapping — verify behavior for the installed version and host OS `[VERIFY]`.
16. WSL2 networking documentation and `tc`/Chaos Mesh compatibility — `[VERIFY]` before fault injection.

### Open verification items

- The selected Gateway API/Ingress controller, API version, TLS Secret wiring, and host-reachability route.
- CoreDNS forwarding syntax and cache/timeout behavior for the installed version.
- Exact MCS API version and behavior of the implementation selected.
- Current supported versions and operating models for Submariner, Cilium Cluster Mesh, Linkerd multicluster, and Istio multi-cluster.
- NetworkPolicy enforcement and source-IP behavior in the actual kind/CNI/WSL2 setup.
- cert-manager trust distribution and rotation workflow.
- Any optional fault-injection or mesh command and its cleanup procedure.

## 13. Final Roadmap Alignment Audit

Status reflects the contents of this lesson, not proof that a live cluster passed the labs.

### Pass A — Source and scope

| Requirement | Status | Location / action |
|---|---|---|
| Correct target filename and M14/Stage 2E location | PASS | Metadata |
| Verbatim M04 handoff | PASS | Immediately after metadata |
| Requirements based on supplied Unit 4 prompt; uncertainty visible | PASS | Sections 1–13; source statement in Section 12 |
| Scoped to Unit 4, not a replacement for Units 5–8 | PASS | Section 1 and cross-links in Section 6 |
| Source gaps not silently invented | PASS | `[VERIFY]` notes and Section 12 |

### Pass B — Topic coverage

| Requirement | Status | Location / action |
|---|---|---|
| L1 architecture taxonomy and cluster-scoped DNS | PASS | Sections 2–3 |
| L2 exposed endpoint, TLS, local abstraction, client resilience, DNS, MCS toy | PARTIAL | Section 4 supplies coherent design and test sequence, but gateway-specific full manifests and an executable endpoint-mirroring controller are intentionally not claimed; complete only after selecting and verifying the lab route |
| L3 decision framework, routing policy, failure semantics, cost | PASS | Section 5 |
| L4 SLOs, observability, zero-trust, upgrades, runbooks, dependency governance, isolation | PASS | Section 6 |
| All ten labs | PASS | Section 7 |
| All eight incident scenarios | PASS | Section 8 |
| ADR template and worked example | PASS | Section 9 |
| Verification matrix, cleanup, 20+ answered questions | PASS | Sections 10–11 |

### Pass C — Technical authenticity

| Requirement | Status | Location / action |
|---|---|---|
| Kubernetes API/DNS scope appropriately qualified | PASS | Sections 2–4 |
| MCS concept distinguished from implementation | PASS | Sections 2.2, 4.10, 5.2 |
| Product status/prerequisites not invented | PASS | Sections 5.2 and 12; live compatibility review remains OPEN |
| CoreDNS/Gateway API/NetworkPolicy/EndpointSlice/certificate specifics verified or marked | PARTIAL | Version-sensitive items are marked `[VERIFY]`; exact live syntax remains OPEN |
| Commands use explicit contexts or are clearly host-local | PASS | Sections 4, 7, 10; endpoint-specific commands remain conditional on chosen route |
| Labs include tests, evidence, cleanup, pass criteria | PASS | Section 7 |
| Outputs/timings identified as representative/synthetic | PASS | Sections 7–8 and 12 |
| Retry/fallback does not prescribe unbounded retry or unsafe write replay | PASS | Sections 4–6 and 11 |
| Lab fidelity limitations explicit | PASS | Sections 2, 4, 7, 9, and trust statement below |
| No unsupported performance/product-status claims as fact | PASS | Sections 5, 6, 12 |

### Pass D — Consistency and pedagogy

| Requirement | Status | Location / action |
|---|---|---|
| Hostnames, contexts, ports, certificate concepts consistent at design level | PARTIAL | The selected endpoint/gateway is intentionally environment-dependent; final manifest-level consistency must be checked after choosing the route |
| Commands are scoped and cleanup is narrow | PASS | Sections 4, 7, 10 |
| Local-first and remote-failure expectations coherent | PASS | Sections 4–6 and Labs 1/5 |
| Progression from concepts to implementation to design to operations | PASS | Sections 3–6 |
| Handoff avoids re-teaching M04 | PASS | Section 1 |
| Cross-module boundaries respected | PASS | Sections 1 and 6.6 |
| Complete lesson, not an outline | PASS | Sections 1–13 |

### Trust statement

An AI self-audit does not replace a human running each configuration, policy, certificate rotation, fault injection, and recovery procedure with the installed versions. All sample outputs and timings are representative/synthetic unless actually captured from a run. Tool behavior, flags, API fields, project status, and supported versions must be checked against current official documentation. Two `kind` clusters on one laptop do not demonstrate multi-region resilience or real WAN behavior. No cross-cluster design should be considered production-ready until it has been exercised, measured, threat-modelled, and reviewed in the target environment.

### Execution statement

- **Source review:** the supplied Unit 4 authoring prompt was used as the controlling requirement.
- **Live official-source verification:** not performed for this authored lesson.
- **Cluster commands executed:** none.
- **Kubernetes manifests applied:** none.
- **Integration tests / certificate rotations / fault drills executed:** none.
- **Static review:** structure, safety boundaries, required lab/scenario coverage, and version-sensitive uncertainty were reviewed in the authored text.
- **Open work:** choose and verify a concrete gateway/endpoint path; pin exact versions; validate every API field/command; implement any optional MCS/mesh lab only after preflight; run positive/negative tests and record actual evidence.
- **Human validation required:** execute the lesson on the installed versions and review it for the target production environment before adoption.
