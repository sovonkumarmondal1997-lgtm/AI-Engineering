# PROMPT — Generate `SYLLABUS-Kubernetes-Networking-Ingress-and-Service-Mesh.md`

> Paste everything between `=== BEGIN PROMPT ===` and `=== END PROMPT ===` into a capable, long-context LLM. The output is very large, so the prompt uses a multi-part Delivery Protocol (Section 14).

=== BEGIN PROMPT ===

# 1. ROLE

You are a **Senior DevOps Engineer and SRE with 15 years of production experience** running Kubernetes networking for data and ML platforms. You have debugged conntrack exhaustion, CoreDNS meltdowns, expired-certificate outages, mesh upgrades that broke mTLS, and "the network policy that blocked DNS" at 2 a.m. You teach with **evidence over opinion, packet-level reasoning, safe defaults, and every claim verifiable.**

You are also a careful technical author. You never invent a manifest field, an annotation, a CRD version, a flag, a default, or a version number. When unsure, you say so and mark it `[VERIFY]`.

# 2. TASK

Produce **one complete learning syllabus with full teaching content** for the folder:

`Stage 2E — Production DevOps & Platform Engineering / 04-Kubernetes-Networking-Ingress-and-Service-Mesh/` (module code **M04**)

Output file name: **`SYLLABUS-Kubernetes-Networking-Ingress-and-Service-Mesh.md`**

It must teach, **one after another, from beginner to advanced**, these 13 units in this exact order:

| # | Unit | Target file |
|---|---|---|
| 0 | Folder orientation | `README.md` |
| 1 | Kubernetes networking model, CNI, pod networking | `01-kubernetes-networking-model-cni-and-pod-networking.md` |
| 2 | Services, kube-proxy, cluster DNS | `02-services-kube-proxy-and-cluster-dns.md` |
| 3 | Ingress controllers and Gateway API | `03-ingress-controllers-and-gateway-api.md` |
| 4 | Load balancers and external traffic management | `04-load-balancers-and-external-traffic-management.md` |
| 5 | Network policies and zero-trust segmentation | `05-network-policies-and-zero-trust-segmentation.md` |
| 6 | TLS termination and certificate lifecycle with cert-manager | `06-tls-termination-and-certificate-lifecycle-with-cert-manager.md` |
| 7 | Service mesh fundamentals: Istio and Linkerd | `07-service-mesh-fundamentals-istio-and-linkerd.md` |
| 8 | mTLS, traffic shifting, retries, circuit breaking | `08-mtls-traffic-shifting-retries-and-circuit-breaking.md` |
| 9 | eBPF networking and Cilium overview | `09-ebpf-networking-and-cilium-overview.md` |
| 10 | Network troubleshooting: DNS, latency, packet loss | `10-network-troubleshooting-dns-latency-and-packet-loss.md` |
| 11 | Practice questions | `practice-questions.md` |
| 12 | Capstone project | `Projects/README.md` + `Projects/01-secure-ingress-and-mtls-for-data-and-ml-apis.md` |

Do **not** add, merge, skip, or reorder units. This is the **teaching content itself**, not an outline.

# 3. LEARNER AND CONTEXT

- **Learner:** a data/AI engineer who completed Stages 0–2D and Stage 2E modules M01 (images), M02 (CI/CD), and M03 (production Kubernetes operations). They know Linux basics, TCP/IP/DNS/HTTP/TLS at a working level (per the stage prerequisites), and can operate Pods, Deployments, Services at a basic level. They have **not** operated cluster networking in production.
- **Stage constraint — zero budget.** All hands-on work runs on a laptop (WSL2 Ubuntu primary, native Linux secondary; ~4 CPU, 8 GB RAM, 30 GB disk). No managed cloud clusters, no cloud load balancers, no paid services, no real public domain required.
- **Primary lab platform: `kind`.** Important fidelity limits to address explicitly and honestly (verify each `[VERIFY]`): kind's default CNI does not enforce NetworkPolicy; `LoadBalancer` Services need a local helper (MetalLB or `cloud-provider-kind`) and are not equivalent to cloud load balancers; host-port mappings via `extraPortMappings` are not a cloud ingress path; there is no real multi-AZ network; WSL2/Docker networking adds an extra NAT layer; `localhost` means different things inside a pod, a kind node container, WSL2, and Windows.
- **Tooling-map alignment and scope decisions** (state these to the learner in the README):
  - **Core (hands-on):** a CNI plugin (a policy-enforcing one for labs), Kubernetes Service + CoreDNS, an Ingress controller.
  - **Taught at working depth because this folder has dedicated modules, though the stage tooling map lists them as Awareness:** Gateway API, cert-manager, one service mesh (choose **Linkerd or Istio as the single hands-on mesh** based on the 8 GB budget and justify the choice with a resource-footprint comparison method, not a claimed number; the other is a documented comparison, with an optional lab only if resources allow `[VERIFY]` footprint), Cilium (hands-on only if used as the lab CNI; otherwise overview plus an optional lab).
  - **Awareness only:** Calico internals, Flannel, Antrea, Contour, Traefik, HAProxy Ingress, Envoy Gateway, Kong, NGINX Gateway Fabric, Consul, Kuma, Open Service Mesh, Cilium Cluster Mesh, cloud-native load balancers (AWS/GCP/Azure), BGP/MetalLB L3 mode, Multus, service-mesh ambient/sidecarless internals beyond concept, Hubble depth.
- **Ingress ecosystem caution:** the maintenance status of specific ingress controllers (including the widely used community NGINX-based one) has changed over time. Do **not** assume any controller is current or recommended; teach how to **evaluate maintenance status** and mark every named controller's status `[VERIFY]`. Teach Ingress API and Gateway API side by side, and explain the migration path.
- **Domain flavor:** a data/ML platform exposing: a FastAPI model-scoring API, an internal feature-service, a Postgres/Redis dependency, an ETL worker that calls external APIs, and a metrics endpoint. Realistic needs: public-ish API ingress with TLS, internal-only services, egress control for the ETL worker, canary rollout of a new model version, gRPC and long-lived streaming connections, large request payloads and timeouts.
- **Cross-module links:** M01 (non-root, images), M02 (CI/CD deploy), M03 (Services/probes/PDB/RBAC/PSS, troubleshooting method), M05 (storage), M06 (Helm/Kustomize — install via manifests or `kubectl` here; flag where Helm is the vendor-supported route), M08 (progressive delivery/GitOps — traffic shifting here is by hand/mesh config; automated analysis is M08), M09 (secrets/identity, workload identity), M10 (SLOs), M11 (observability: metrics/traces/logs for mesh and ingress), M12 (supply chain/security), M14 (multi-cluster networking), M15 (egress/LB cost). State clearly what is **taught here vs. deferred**.

# 4. TEACHING MODEL — THE FOUR LEVELS (UNITS 1–10)

| Level | Name | Learner outcome |
|---|---|---|
| **L1** | Beginner — Foundations | Explains the concept, runs and reads basic commands/manifests, and can trace a packet conceptually. |
| **L2** | Intermediate — Working Practice | Configures it correctly for a real data/ML service and avoids common mistakes. |
| **L3** | Advanced — Production Engineering | Designs, secures, measures, and defends choices under constraints (availability, latency, security, cost). |
| **L4** | Expert — Operating at Scale and Under Failure | Diagnoses failures at packet/protocol level, writes policy and automation, plans safe change for a fleet. |

# 5. MANDATORY STRUCTURE FOR EACH UNIT 1–10

Use this exact skeleton, same headings, same order, in every unit. If a section is genuinely not applicable, write one sentence explaining why.

```
## Unit N — <Title>
**Target file:** <filename>  |  **Estimated time:** <hours>  |  **Prerequisites:** <list>
**Core tools:** …  |  **Awareness:** …  |  **Last reviewed:** <date>  |  **Kubernetes/tool baseline assumed:** <ranges, [VERIFY]>

### N.0 Why this matters in production
(3–6 sentences; a concrete outage, security incident, or cost this prevents. No hype.)

### N.1 Learning objectives
(6–10 measurable outcomes, action verbs, each tagged L1–L4.)

### N.2 Concept map and vocabulary
(Glossary table: term | precise definition | common misconception. At least one packet-path or control-flow diagram — mermaid or ASCII — showing source, hops, NAT/encapsulation points, and where policy/TLS is applied.)

### N.3 Level 1 — Beginner
- First-principles explanation (what happens to a packet/request, hop by hop, and which component owns each hop)
- Guided lab: exact manifests/commands, expected output, how to read it
- "What just happened?" walkthrough (trace with the actual IPs, ports, rules, and objects involved)
- Common beginner mistakes → symptom → fix

### N.4 Level 2 — Intermediate
- Complete, runnable manifests for the data/ML platform running example
- Pattern catalogue: pattern | when to use | when NOT to use
- Anti-pattern catalogue: bad config → why it hurts in production → corrected version
- Lab with observable before/after behavior

### N.5 Level 3 — Advanced
- Design decisions with a trade-off table (option | benefit | cost | risk | choose when)
- Reliability, performance, and security techniques
- Measurement/verification method (what to observe, which command/tool, how to avoid fooling yourself)
- Lab requiring a defended decision, not a copied manifest

### N.6 Level 4 — Expert
- Failure scenarios (symptom → hypothesis → test → root cause → fix → prevention)
- Policy-as-code and automation (validation scripts, policy tests, CI checks of manifests)
- Fleet/organizational concerns: standards, ownership, change management, review checklists
- Edge cases and platform differences (kind vs production, WSL2, managed vs self-managed, IPv6/dual-stack awareness)

### N.7 SRE lens
- SLIs/SLOs relevant here (e.g., request success rate, p95/p99 latency, DNS error rate, certificate days-to-expiry, config-propagation time)
- Failure modes and blast radius
- Runbook snippet: alert → triage → mitigation → follow-up
- Cost and capacity notes

### N.8 Security lens
- Threats addressed (e.g., lateral movement, spoofing, sniffing, exposed services, expired/rogue certificates, SSRF-to-metadata, data exfiltration) and what is NOT addressed
- Controls and how to verify each with a concrete test

### N.9 Production checklist
(Checkbox list; every item verifiable by command or test.)

### N.10 Hands-on lab set
(3–5 labs: ID | goal | steps | expected evidence | cleanup | stretch. Idempotent, safe to re-run, within the local resource baseline, each labeled with the **kind-simulation caveat** where relevant.)

### N.11 Self-check questions
(6–10 questions with concise answer keys and a note on why wrong options are tempting.)

### N.12 Evidence artifacts
(Exactly what files/captures/outputs the learner saves to prove completion.)

### N.13 Common interview and design-review questions
(5 questions with senior-level model answers.)

### N.14 Sources and verification notes
(Official docs consulted by name and section; [VERIFY] items; version-sensitive claims.)
```

# 6. MODULE-SPECIFIC CONTENT REQUIREMENTS

Minimum topics. Add depth, never remove.

## Unit 1 — Kubernetes networking model, CNI, pod networking
- **L1:** the four Kubernetes networking requirements (pod-to-pod without NAT, node-to-pod, pod's own IP view, containers in a pod share the network namespace); network namespaces, veth pairs, bridges, routes; pod IP vs node IP vs Service IP; `ip addr`, `ip route`, `ip netns`/`nsenter`, `ss`, `kubectl get pods -o wide`; what a CNI plugin is and when the kubelet/runtime calls it (ADD/DEL, config in `/etc/cni/net.d`, binaries in `/opt/cni/bin`).
- **L2:** trace a pod-to-pod packet on the same node and across nodes in kind (inspect node container routes/interfaces with `docker exec`); pod CIDR allocation per node; overlay (VXLAN/Geneve/IP-in-IP) vs routed (BGP/host routes) vs cloud-native (VPC/ENI) networking — comparison table; MTU and encapsulation overhead; CNI choice (kindnet default, Calico, Cilium, Flannel — comparison with Awareness boundaries); cluster/service/pod CIDR planning and the cost of getting it wrong; hostNetwork and its implications; IPv4/IPv6/dual-stack basics `[VERIFY]` support.
- **L3:** CNI selection criteria (policy support, performance, observability, encryption, ecosystem, operational burden); IPAM models and exhaustion; MTU mismatch diagnosis (large-packet black holes; `ping -M do -s`, PMTUD); node-to-node encryption options (WireGuard/IPsec — concept, via CNI `[VERIFY]`); multi-network (Multus) as Awareness; CNI installation/upgrade risk and ordering (nodes `NotReady` without CNI); CNI failure semantics (what keeps working when the CNI agent crashes); kube-proxy vs CNI responsibility boundary (deferred detail to Unit 2).
- **L4:** CIDR planning for fleets and future peering (forward ref M14); CNI migration strategy (and why it is high risk); capacity/limits (pods per node, IPs per node, conntrack table sizing); diagnosing IP exhaustion and stuck `ContainerCreating` from CNI errors (`failed to set up sandbox`); CNI observability; ADR template for CNI choice.
- **Must include:** a lab that creates a multi-node kind cluster with a **policy-capable CNI installed by documented kind-compatible steps** (`disableDefaultCNI: true` config `[VERIFY]`), shows the node `NotReady` before CNI install and `Ready` after, then traces same-node and cross-node pod traffic with `tcpdump`/`ip route` evidence and finds the pod CIDR per node.

## Unit 2 — Services, kube-proxy, cluster DNS
- **L1:** why Services exist (pod IPs are ephemeral); ClusterIP, NodePort, LoadBalancer (concept), ExternalName, headless; selectors, Endpoints/EndpointSlices; `kubectl get svc,endpointslices`; port vs targetPort vs nodePort; DNS names (`svc.namespace.svc.cluster.local`), search domains and `ndots`.
- **L2:** kube-proxy modes (iptables, IPVS, nftables `[VERIFY]` availability) and what each programs; inspect rules (`iptables-save`/`nft list`/`ipvsadm` inside a kind node); session affinity; `externalTrafficPolicy` and `internalTrafficPolicy` basics; named ports; CoreDNS architecture (Corefile, `kubernetes` plugin, `forward`, `cache`, `loop`, `ready`, `health`), `dnsPolicy` and `dnsConfig`; headless Services for StatefulSets (link M03/M05); pod DNS records.
- **L3:** **the `ndots:5` problem** and its latency/QPS cost for external names; trailing-dot FQDNs, `dnsConfig` tuning; NodeLocal DNSCache (concept + optional lab `[VERIFY]`); CoreDNS scaling and autoscaling (cluster-proportional-autoscaler concept), conntrack and UDP DNS races (known kernel behavior — `[VERIFY]` framing); EndpointSlice scaling and propagation delay; readiness and endpoint removal vs connection draining (link M03 Unit 5); topology-aware routing `[VERSION-SENSITIVE]`; kube-proxy-less operation via eBPF (forward ref Unit 9); IPVS vs iptables scale trade-offs; Service-without-selector with manual EndpointSlices.
- **L4:** conntrack exhaustion diagnosis and sizing; DNS-failure incident analysis (CoreDNS crashloop, upstream timeout, loop detection, NXDOMAIN storms); Service CIDR exhaustion; blast radius of CoreDNS config changes; custom DNS stubs and split-horizon; DNS SLO and synthetic probes; policy-as-code to require sane `dnsConfig` for heavy-egress workloads.
- **Must include:** a lab that inspects kube-proxy rules for a Service (mapping ClusterIP → endpoints in the rule set), demonstrates endpoint changes live, measures DNS query counts for an external name with and without `ndots` tuning (using `tcpdump` or CoreDNS metrics/logging `[VERIFY]`), and breaks and repairs CoreDNS in the throwaway cluster.

## Unit 3 — Ingress controllers and Gateway API
- **L1:** north–south vs east–west traffic; L4 vs L7; reverse proxy concept; Ingress resource vs Ingress controller (an Ingress object does nothing without a controller); `IngressClass`; host/path routing; `pathType` (Exact/Prefix/ImplementationSpecific).
- **L2:** install one maintained, kind-compatible ingress controller via its official instructions (`extraPortMappings`, node labels `ingress-ready` pattern `[VERIFY]`); route to the API and feature-service; default backend; annotations are controller-specific and non-portable (explain portability risk); timeouts, body-size limits, websocket/gRPC support; rewrites and their risks; **Gateway API**: `GatewayClass`, `Gateway`, `HTTPRoute`, roles (infra provider / cluster operator / app developer), `ReferenceGrant`, cross-namespace attachment, status conditions `[VERIFY]` current API versions and channel (standard vs experimental) and which resources are GA; install of Gateway API CRDs and a conformant implementation for the lab.
- **L3:** Ingress vs Gateway API trade-off table and migration approach (including tools that convert Ingress to Gateway — Awareness `[VERIFY]`); controller selection framework (maintenance status, conformance, features, performance, operability, security record, licensing); multi-tenant ingress (shared vs per-team vs per-environment gateways); header/query matching, weighted routing (`backendRefs` weights), redirects/rewrites in Gateway API; rate limiting and WAF as controller/extension features (Awareness, controller-specific `[VERIFY]`); real client IP preservation (`X-Forwarded-For`, PROXY protocol, `externalTrafficPolicy: Local` — link Unit 4); ingress HA and PDBs (link M03); connection idle timeouts alignment across LB → ingress → app; HTTP/2/gRPC and streaming specifics (e.g., large model responses, SSE) and timeouts.
- **L4:** admission validation of Ingress/Gateway objects (snippet-annotation risks — explain the class of risk defensively; policy to restrict); controller upgrade strategy and config reload behavior; 502/503/504 triage by hop; capacity and tuning; ingress observability (access logs, metrics; forward ref M11); standardized golden-path route templates (forward ref M16); incident: "an annotation injected by one tenant broke ingress for everyone" and "controller reached end of maintenance" → migration plan.
- **Must include:** a lab that serves the same routes through (a) an Ingress and (b) a Gateway API `HTTPRoute`, with side-by-side manifests, a weighted 90/10 split to two versions of the API, and a deliberately misconfigured route decoded via status conditions/events/logs.

## Unit 4 — Load balancers and external traffic management
- **L1:** what a load balancer does (L4 vs L7); Service `type: LoadBalancer` and what actually provisions the LB; NodePort path; why `<pending>` happens off-cloud; algorithms (round robin, least-connections, hashing) conceptually.
- **L2:** provide LoadBalancer IPs locally with MetalLB in L2 mode or `cloud-provider-kind` (choose one, justify, `[VERIFY]` install steps and Docker network ranges on WSL2/Linux); IP address pool configuration; `externalTrafficPolicy: Cluster` vs `Local` (source IP preservation vs hop/imbalance trade-off); health checks from LBs to nodes (`healthCheckNodePort`); external-dns as Awareness; DNS for external names; egress basics (SNAT, node IP as source).
- **L3:** external traffic architecture patterns (cloud LB → NodePort → pod; LB → ingress → services; direct-to-pod/NEG-style `[Awareness]`); LB idle timeouts vs keep-alives vs app timeouts — the **timeout ladder** design rule; connection draining during deploys and node drains (link M03 Unit 5); source-IP preservation and PROXY protocol; TCP vs HTTP health checks; UDP/gRPC/TLS passthrough handling; global vs regional LB and DNS-based traffic management (Awareness; forward ref M14); egress control: egress gateways, fixed egress IPs, NAT-gateway costs (Awareness; forward ref M15); capacity: ephemeral-port/SNAT exhaustion and conntrack.
- **L4:** multi-LB blast radius and IP exhaustion; DDoS and rate-limit layering (Awareness); failover design and testing; upgrade without dropping connections; LB metrics/SLOs; incident analysis: "502s only during deploys" (timeout/drain mismatch), "client IPs all show the node IP," "LB health check marked all nodes unhealthy."
- **Must include:** a lab with a MetalLB-or-equivalent LoadBalancer Service, a demonstration of source-IP behavior under both `externalTrafficPolicy` modes with captured evidence, and a rolling-deploy test measuring dropped requests before and after fixing readiness/drain settings. State plainly that real cloud LB behavior will differ.

## Unit 5 — Network policies and zero-trust segmentation
- **L1:** default is allow-all; what NetworkPolicy is (an API object enforced by the CNI — **creating a policy with a non-enforcing CNI does nothing**); pod selectors, namespace selectors, `ingress`/`egress`, `policyTypes`; additive semantics (no deny rules; allow-lists only); verify with test pods (`curl`/`nc`).
- **L2:** default-deny ingress and egress per namespace; **allow DNS egress** (the classic mistake) with correct selectors and ports (UDP/TCP 53); allow ingress-controller → app; app → database; namespace isolation; `ipBlock` (and its limits/NAT caveats); port ranges (`endPort` `[VERIFY]`); label hygiene as the policy foundation; testing policies with a repeatable matrix script (source × destination × port → expected allow/deny).
- **L3:** zero-trust principles (never trust the network; identity-based access; least privilege; assume breach) and what NetworkPolicy does and does not give (L3/L4 only, IP/label based, no authentication, no L7, no FQDN rules in vanilla API); admin/baseline policies and `AdminNetworkPolicy`/`BaselineAdminNetworkPolicy` `[VERSION-SENSITIVE]` status; CNI-specific extended policies (CiliumNetworkPolicy with L7/FQDN rules; Calico GlobalNetworkPolicy — Awareness with one worked example `[VERIFY]` syntax); egress control for the ETL worker (allow specific external CIDRs; FQDN policy via CNI extension; egress gateway); controlling access to the cloud metadata endpoint and the API server (concept); policy rollout strategy (observe → audit → enforce; flow logs via Hubble/Calico — Awareness); interplay with mesh authorization policy (Unit 8).
- **L4:** policy-as-code: generated default-deny via namespace vending, CI tests with a policy simulator or live matrix on ephemeral kind, drift detection; policy visualization/analysis tools (Awareness `[VERIFY]`); scaling policy management across teams; failure scenarios: policy blocks probes? (explain kubelet-to-pod probe traffic handling per CNI `[VERIFY]`), blocks DNS, blocks webhook callbacks from the API server (link M03 webhooks), blocks metrics scraping; incident: "default-deny shipped at 5 p.m. and the API lost its database"; emergency policy rollback.
- **Must include:** a lab that first proves the default CNI (or a non-enforcing config) ignores a policy if applicable, then (on the policy-enforcing CNI) builds a full segmentation for ingress → api → db plus restricted egress for the ETL worker, validates with an automated allow/deny matrix script, and deliberately omits DNS egress to show and diagnose the failure.

## Unit 6 — TLS termination and certificate lifecycle with cert-manager
- **L1:** TLS handshake essentials, certificates, chains, CAs, SANs, expiry, private keys; where TLS is terminated (edge, ingress, pod, mesh); HTTP→HTTPS redirect; HSTS concept; `openssl s_client`, `openssl x509 -text`, `curl -v --cacert`.
- **L2:** manual TLS Secret (`kubernetes.io/tls`) on an Ingress/Gateway listener using a local CA (`mkcert` or `openssl`) — lab-only trust; install cert-manager via official manifests `[VERIFY]` version/CRD notes; `Issuer`/`ClusterIssuer` (SelfSigned, CA), `Certificate`, `CertificateRequest`, `Order`/`Challenge` (ACME concept); the CA-issuer bootstrap pattern (self-signed root → CA issuer → leaf certs); ingress-shim annotations vs explicit `Certificate`; renewal behavior (`duration`, `renewBefore`), secret rotation and how workloads pick it up.
- **L3:** ACME and Let's Encrypt (HTTP-01 vs DNS-01; wildcard needs DNS-01; rate limits `[VERIFY]` — **Awareness only; no public domain or internet-exposed endpoint is required for the lab**; use a local CA and, optionally, a local ACME test server such as Pebble `[VERIFY]` as a stretch); trust distribution (`trust-manager` Awareness); private PKI design (offline root, intermediate, short-lived leaves); key algorithms and sizes, `rotationPolicy`; certificate observability: cert-manager metrics, `certmanager_certificate_expiration_timestamp_seconds` `[VERIFY]` name, alerting at N days; secret handling (RBAC on secrets; etcd encryption at rest concept; forward ref M09); external issuers (Vault, cloud CAs — Awareness); mTLS-capable cert use (client auth EKU) conceptually; TLS 1.2/1.3 policy and cipher choices (Awareness: follow current guidance `[VERIFY]` Mozilla/NIST); OCSP stapling and revocation realities (Awareness).
- **L4:** the **expired-certificate outage** pattern and a prevention program (inventory, monitoring, auto-renewal testing, game days); renewal failure analysis (`kubectl describe certificate/certificaterequest/order/challenge`, controller logs); CA rotation without downtime; cert-manager upgrade and CRD management risks; multi-cluster/multi-tenant issuer design (forward ref M14); compliance evidence; incident: "wildcard cert private key exposed" → revoke/rotate/reissue/audit; incident: "ClusterIssuer deleted and renewals silently stopped."
- **Must include:** a lab issuing a cert from a local CA through cert-manager for the API ingress, verifying the chain with `openssl`/`curl`, forcing early renewal (e.g., short `duration`/`renewBefore` in a lab-only issuer `[VERIFY]` minimum allowed values) and proving the new cert is served without downtime, then deleting the issuer to see and fix the failure. All crypto material is lab-only and labelled so.

## Unit 7 — Service mesh fundamentals: Istio and Linkerd
- **L1:** the problems a mesh addresses (uniform mTLS, retries/timeouts, traffic shaping, golden-signal telemetry, authz) and the problems it **adds** (complexity, latency, resource cost, debugging surface); data plane vs control plane; sidecar model vs sidecarless/ambient (concept, `[VERSION-SENSITIVE]` maturity); "do you need a mesh?" decision framework (alternatives: library-level, ingress-only, CNI-level mTLS/policy).
- **L2:** install the chosen hands-on mesh with its official CLI/manifests on the kind cluster `[VERIFY]` current install path and compatibility with the Kubernetes version; namespace injection/annotation; verify the data plane is meshed; mesh dashboards/telemetry basics (Linkerd viz or Istio add-ons — keep footprint small `[VERIFY]`); onboarding a service incrementally; the sidecar's effect on startup order, probes, Job completion, and resource requests (known operational pitfalls); mesh and NetworkPolicy interplay.
- **L3:** architecture details for **both** meshes (Istio: istiod, Envoy, CRDs `VirtualService`/`DestinationRule`/`Gateway`/`PeerAuthentication`/`AuthorizationPolicy`, sidecar vs ambient; Linkerd: control plane, Rust micro-proxy, `ServiceProfile`/Gateway API-based routing `[VERIFY]` current model, policy CRDs) in a comparison table (security model, features, resource footprint method, operational complexity, ecosystem, license/governance `[VERIFY]`, upgrade model); Gateway API's role in meshes (GAMMA initiative `[VERIFY]`); mesh ingress vs standalone ingress; control-plane HA and failure semantics (what happens to traffic when the control plane is down — verify in lab); proxy resource sizing, concurrency, and tail-latency overhead measurement method; upgrade strategies (canary control plane / revisions); multi-cluster mesh as Awareness (forward ref M14).
- **L4:** mesh adoption/migration program (ring-based onboarding, opt-out escape hatches); mesh failure modes (certificate/identity-issuer expiry, injection webhook failure blocking pod creation — link M03, version skew between control and data plane, config push storms, proxy memory growth); governance (who owns mesh config; policy review); cost/benefit review and **exit strategy** (how to remove a mesh safely); incident: "mesh upgrade broke mTLS between old and new proxies" and "trust anchor expired."
- **Must include:** a lab that installs the chosen mesh, meshes the sample apps, proves the proxies are injected, measures baseline vs meshed latency/CPU/memory using a documented method (N runs, median/p95, noise warnings), and then removes the mesh cleanly. A written decision memo comparing Istio and Linkerd for the learner's own measurements.

## Unit 8 — mTLS, traffic shifting, retries, circuit breaking
- **L1:** TLS vs mutual TLS; workload identity (SPIFFE concept); certificate issuance by the mesh CA; permissive vs strict modes; why retries/timeouts/circuit breakers exist (partial failure, cascading failure, retry storms).
- **L2:** enable and **verify mTLS** (check identity and encryption via mesh CLI tooling and packet capture showing ciphertext `[VERIFY]` method); strict-mode rollout in stages (permissive → strict) per namespace; authorization policies (allow by identity/namespace/path/method) layered on a default-deny; timeouts and retries configuration in the chosen mesh; **weighted traffic shifting** (e.g., 90/10, 50/50 model-version canary) with real measurement of split accuracy; header-based routing for testers.
- **L3:** retry-safety rules (idempotency, retry budgets, `retryOn` conditions, per-try timeout < overall timeout, jitter/backoff), **retry amplification** across call depth (show the arithmetic), hedging (Awareness); circuit breaking and outlier detection (connection-pool limits, consecutive-error ejection) with Istio `DestinationRule` fields and Linkerd's equivalents/limitations `[VERIFY]`, and how they differ from app-level breakers; load-balancing algorithms in the mesh (EWMA vs round-robin vs least-request); fault injection (delay/abort) for resilience testing; traffic mirroring/shadowing for a new model version (data privacy caveats for mirrored production data); rate limiting (local vs global — Awareness); egress control through the mesh (`ServiceEntry`/egress policy `[VERIFY]`); gRPC and long-lived streams and how retries/timeouts behave; interaction of mesh policy with app-level TLS and with Kubernetes NetworkPolicy (defense in depth: both).
- **L4:** progressive-delivery boundaries (manual shifting here vs automated analysis in M08 — Argo Rollouts/Flagger as forward-ref Awareness); designing resilience policy as code with defaults, and testing it in CI on ephemeral kind (fault-injection tests that assert behavior); mTLS troubleshooting (identity mismatch, expired issuer, clock skew, plaintext-to-strict failures, non-meshed clients such as Jobs/CronJobs and kubelet probes); SLO-aware policy (error-budget burn → freeze shifts, forward ref M10); incident analysis: "retry storm took down the feature-service," "strict mTLS enabled and the metrics scraper broke," "canary weight didn't match intent."
- **Must include:** a lab covering (1) staged strict-mTLS rollout with proof of encryption and a blocked plaintext client, (2) a 90/10 canary with measured actual split across ≥ 1,000 requests, (3) fault injection plus retry/timeout tuning that demonstrates retry amplification and its fix, (4) a circuit-breaking/outlier-ejection demonstration, with metrics evidence for each.

## Unit 9 — eBPF networking and Cilium overview
- **L1:** what eBPF is (sandboxed programs in the kernel, verifier, hooks, maps) in plain terms; why it matters for networking (bypass iptables/conntrack paths, observability, policy); limits and kernel-version/feature requirements `[VERIFY]` (and WSL2 kernel support caveats); eBPF is not a "faster iptables" in every case.
- **L2:** Cilium architecture (agent, operator, datapath, identity-based policy, Hubble `[VERIFY]` components), install on kind as the lab CNI with documented kind-specific steps `[VERIFY]` (or an overview-level walkthrough if the learner kept another CNI); `cilium status`/`connectivity test` `[VERIFY]` commands; identity-based vs IP-based policy; kube-proxy replacement concept and prerequisites; Hubble flows for visibility (`hubble observe`).
- **L3:** CiliumNetworkPolicy (L3/L4/L7, FQDN/DNS-aware egress policy) with worked examples `[VERIFY]` syntax; `CiliumClusterwideNetworkPolicy`; transparent encryption (WireGuard/IPsec) `[VERIFY]`; Gateway API and ingress support in Cilium (Awareness); service mesh features without sidecars (Awareness, maturity `[VERSION-SENSITIVE]`); bandwidth management/egress gateway (Awareness); performance claims — **teach how to test, never quote**; observability integration with Prometheus/Grafana (forward ref M11); trade-offs: kernel dependency, debugging complexity (BPF maps), upgrade risk, ecosystem lock-in.
- **L4:** adoption/migration strategy from another CNI (risk and staged approach; Awareness); eBPF security/observability tools beyond networking (Falco/Tetragon/Pixie — Awareness, forward ref M12/M11); diagnosing datapath issues (`cilium monitor`, `cilium bpf` tooling `[VERIFY]`, drop reasons in Hubble); operational runbook (agent crash, identity exhaustion, policy-map limits); governance of privileged agents (they run with high privilege — threat-model it); decision framework "Cilium vs Calico vs managed-default CNI" for an organization.
- **Must include:** an overview-level or optional hands-on lab (if Cilium is the lab CNI, observe live flows with Hubble and apply an L7/FQDN policy; if not, a guided read-only analysis of provided captured Hubble/Cilium output); explicit statement of what was and was not reproduced locally.

## Unit 10 — Network troubleshooting: DNS, latency, packet loss
- **L1:** the systematic method (define the symptom → locate the layer → isolate the hop → test → fix → verify); the OSI/TCP-IP layered checklist applied to Kubernetes; basic tools (`ping`, `curl -v`, `dig`/`nslookup`, `nc`, `ss`, `ip`, `traceroute`/`mtr`, `tcpdump`); ephemeral debug containers (`kubectl debug`) and a netshoot-style toolbox image (and its security implications — use only in lab/with approval).
- **L2:** the decision tree: Pod cannot reach Service (selector/endpoints/port/targetPort/DNS/policy/CNI/kube-proxy); Service works in-cluster but not from outside (ingress/LB/NodePort/firewall); DNS failures (CoreDNS health, upstream, `ndots`, policy); intermittent connection resets; "works from one pod, fails from another" (policy, node, MTU); reading `describe svc/ingress/endpointslice`, CoreDNS logs, ingress access/error logs; HTTP status triage 502/503/504/499 by hop.
- **L3:** latency analysis (DNS lookup time vs connect vs TLS vs TTFB — `curl -w` timing format; conntrack and SNAT effects; CPU throttling-induced latency link M03; mesh proxy overhead; cross-zone latency awareness); packet-loss diagnosis (`mtr`, retransmits via `ss -ti`/`nstat`, interface drops via `ip -s link`, MTU/PMTUD blackholes, conntrack table full — `conntrack -S`, `nf_conntrack` limits `[VERIFY]`); `tcpdump` capture-and-read technique (filters, from a debug container or node, saving pcap, reading in Wireshark/tshark — Awareness for the GUI); TLS failure diagnosis (`openssl s_client`, SNI mistakes, chain issues, expiry, mTLS identity errors); controlled fault injection with `tc netem` for delay/loss in lab `[VERIFY]` availability in kind nodes; load-induced issues (SYN backlog, ephemeral-port exhaustion, TIME_WAIT).
- **L4:** correlating metrics/logs/traces across ingress → mesh → app; flow-log-based forensics (Hubble — Awareness); building diagnostic automation (a `netcheck` script/Job producing a report; synthetic probes; DNS canaries); runbooks per failure class; network incident post-mortem template; "debugging when the debugger is blocked" (policy or PSS prevents debug pods; privileged access procedures and audit); chaos drills (drop DNS, inject latency, kill CNI agent) with expected vs observed tables; pattern table (symptom → top-3 causes → first command).
- **Must include:** a **networking troubleshooting gauntlet** of at least **12 provided broken scenarios** applied to a kind cluster (e.g., wrong `targetPort`, selector mismatch, missing endpoints, default-deny without DNS egress, `ndots` storm, MTU mismatch simulated via `tc`/interface MTU `[VERIFY]` feasibility, Ingress with wrong `IngressClass`, HTTPRoute not accepted, expired/mismatched cert, strict mTLS vs plaintext client, `externalTrafficPolicy` source-IP surprise, CoreDNS loop/upstream failure, conntrack-pressure simulation `[VERIFY]` safe approximation, timeout-ladder mismatch). Each has hidden cause, hints at three levels, diagnosis rubric, fix, and prevention policy; answers in clearly separated answer-key sections.

# 7. PRACTICE QUESTIONS (Unit 11)

At least **150 questions**: ≥ 12 per Units 1–10 plus ~25 cross-unit integration scenarios. Per unit:
- 3 × conceptual short-answer
- 3 × multiple choice (4 options; explain every distractor)
- 2 × output interpretation (given `kubectl`/`ip`/`iptables`/`dig`/`curl -v`/`tcpdump`/mesh output, what is wrong?)
- 2 × manifest review (find ≥ 3 defects, fix them)
- 1 × incident/troubleshooting scenario (symptom → diagnose → fix → prevent)
- 1 × design question with a rubric

Each question: ID, level (L1–L4), objective tested, time estimate, **model answer**, **common wrong answers**. Include packet-walk questions ("trace a request from a laptop to a pod and list every NAT/encryption/policy point"). Include a scoring rubric (≥ 80% proceed; 60–79% remediate; < 60% repeat) and 10 "design-review" whiteboard prompts requiring written trade-off reasoning (e.g., mesh vs no mesh, Ingress vs Gateway API, where to terminate TLS, CNI selection, egress control design, timeout ladder, retry policy for a deep call graph). Test only taught content.

# 8. CAPSTONE PROJECT (Unit 12)

**Project:** *Secure Ingress and mTLS for Data and ML APIs.*

Deliver `Projects/README.md` (index, grading, evidence submission) and the full spec.

**Scenario:** A data platform exposes a model-scoring API, a feature service, and a metrics endpoint. Today: everything is `LoadBalancer`/NodePort exposed, plain HTTP, no NetworkPolicy, certificates are copy-pasted and one expired last quarter, a canary was done by editing replicas, retries doubled load during an incident, DNS is slow for external calls, and nobody can explain how a request travels. The learner builds the secure, observable, locally verifiable traffic architecture.

**Required deliverables (each with acceptance criteria verifiable by command or inspection):**
1. kind cluster config with policy-enforcing CNI, bootstrap script with context safety checks, and `versions.txt`.
2. Local LoadBalancer provider (MetalLB or equivalent) and a single ingress path via Gateway API (primary) with an Ingress equivalent kept for comparison.
3. TLS via cert-manager with a local CA: ingress termination for the API; renewal tested; expiry alert rule written (Prometheus rule file validated syntactically; backend optional).
4. Namespace segmentation: default-deny ingress/egress, explicit allows (ingress → api → feature-service → db; DNS; metrics scraper), restricted ETL egress; an automated **allow/deny matrix test** that exits non-zero on drift.
5. Service mesh (chosen mesh) with staged strict mTLS and identity-based authorization policies; proof of encryption and a blocked non-meshed/unauthorized client.
6. Traffic management: weighted canary for a model-version change with measured split; timeouts, bounded retries with budget, circuit breaking/outlier detection; a fault-injection test demonstrating no retry amplification.
7. DNS hygiene: `ndots`/`dnsConfig` tuning for the ETL worker with measured query reduction; CoreDNS health checks.
8. Timeout-ladder design document and tests (client → ingress → mesh → app consistent; streaming endpoint covered).
9. A `netcheck` diagnostic script/Job and ≥ 6 incident drills (DNS failure, policy block, cert expiry, mTLS mismatch, LB source-IP, MTU/latency fault) with expected vs observed results.
10. `Makefile` targets: `up`, `deploy`, `verify`, `matrix-test`, `cert-test`, `canary-test`, `chaos`, `down`; `make verify` produces a pass/fail report with evidence.
11. Documentation: end-to-end **packet/request path diagram** (client → LB → gateway → mesh proxy → pod, annotated with NAT, TLS, policy points), ≥ 5 ADRs (CNI, Gateway API vs Ingress, mesh choice, TLS/PKI design, egress approach), runbooks for 5 incident types (expired cert, DNS outage, 502/503 during deploy, default-deny outage, mesh control-plane failure), and a production-readiness review using the Unit 1–10 checklists.
12. A before/after results table (p50/p95 latency with/without mesh, DNS queries per external call, canary split error, time-to-detect expiry, requests dropped during deploy, blocked lateral-movement tests) filled from the learner's **own** measurements. Provide the template; never fabricate results.

**Include:** 6–7 milestones with time estimates; a 100-point rubric (Poor/Adequate/Strong/Exemplary descriptors); stretch goals (Cilium L7/FQDN policy, Pebble ACME, Istio-vs-Linkerd comparison, external-dns simulation); common failure points; self-review checklist; exact evidence folder structure; a resource-budget plan for running everything within 4 CPU / 8 GB (state what to disable or sequence).

**Provide complete, runnable starter code and manifests:** small realistic FastAPI API and feature service, ETL worker, all YAML, scripts, Makefile, matrix-test and verification scripts. No `TODO: implement` in required deliverables. All credentials, keys, and certificates are lab-only fakes generated locally and labelled as such.

# 9. README ORIENTATION (Unit 0)

Include: purpose and audience; Gate In prerequisites (including M01–M03 outcomes consumed here and the stage networking prerequisites); module dependency graph and why order matters (CNI → Services/DNS → Ingress/LB → Policy → TLS → Mesh → mTLS/traffic → eBPF → troubleshooting); 6-week and 10-week pacing plans; tool matrix (Core / working-depth / Awareness, matching Section 3) with install-verification commands; lab environment checklist (Docker resources, kind version, kubectl skew, ports used, disk, WSL2 networking notes); **resource-budget guide** (what can run together in 8 GB; sequence mesh and CNI labs); **kind-vs-production fidelity table** (real / simulated / not reproducible: CNI enforcement, LB, ingress path, zones, MTU, cloud LB health checks, NAT/egress IPs, public ACME); glossary; module-to-exit-criteria mapping; evidence rules; how to use practice questions and the project; table linking M04 to M01–M03, M05, M06, M08–M12, M14–M16; a **safety section** on context hygiene, throwaway clusters, using packet capture only on lab traffic, using `tcpdump`/debug images only on clusters you own, and never scanning or probing networks you do not own.

# 10. CODE AND COMMAND RULES (NON-NEGOTIABLE)

1. Every code block names its language and, for files, a first-line path comment (e.g., `# File: manifests/gateway/httproute.yaml`).
2. Every command is paired with **representative expected output**, labelled "example — yours will differ" (IPs, ports, hashes, timings will vary), plus a short interpretation.
3. **Only real syntax.** Use apiVersions, kinds, fields, annotations, CRDs, flags, metric names, and CLI subcommands you are confident exist. Anything that varies by Kubernetes version, CNI, controller, mesh, or feature gate is tagged `[VERIFY: what/where]` or `[VERSION-SENSITIVE]`. State the apiVersion for every manifest (`networking.k8s.io/v1`, `gateway.networking.k8s.io/v1`, `cert-manager.io/v1`, `security.istio.io/v1`, `networking.istio.io/v1`, `policy.linkerd.io/…`, `cilium.io/v2`…), and mark the ones you are not certain of. Never guess. When showing install steps for controllers/CNI/mesh/cert-manager/MetalLB, **point to the official install documentation and the version-compatibility matrix** and use `<VERSION>` placeholders instead of invented version numbers.
4. **Context safety:** every lab begins with a context check (`kubectl config current-context` asserted against the expected `kind-<name>`); destructive or cluster-wide commands are labelled `⚠ DESTRUCTIVE` with the target named and a read-only or dry-run (`--dry-run=server`, `kubectl diff`) alternative first. CNI replacement and mesh removal are labelled high-risk and only run on throwaway clusters.
5. **Manifests follow the standards taught** in M01/M03: pinned images (digest with tag comment), resource requests/limits, probes, non-root `securityContext`, explicit ServiceAccount, labels (policy depends on them) — unless a deliberate anti-pattern labelled `# ANTI-PATTERN — DO NOT COPY` with defect list and fix beside it.
6. **No real secrets, keys, or public-internet exposure.** All TLS material is generated locally and labelled lab-only; never instruct opening ports to the internet, using a real domain, or using a real Let's Encrypt account. Public ACME is Awareness only. Use obviously fake credentials (`example-password-do-not-use`).
7. **Defensive security only:** lateral-movement and exfiltration scenarios exist to *verify that controls block them* on the learner's own cluster; no scanning tools aimed at external hosts, no exploit code, no evasion techniques. Packet captures only on lab traffic; remind the learner that captures can contain secrets and must be deleted.
8. **Scripts:** `set -euo pipefail`, quoted variables, explicit exit codes, context assertion, `--dry-run` where mutating, idempotent where possible; the matrix-test and verify scripts exit non-zero on failure. Python: typed where practical, minimal dependencies, with tests.
9. **Resource realism:** every lab states its approximate CPU/RAM/disk footprint and fits within 4 CPU / 8 GB; never run mesh, Cilium/Hubble, and a full observability stack simultaneously; tell the learner when to delete clusters. State measurement caveats for any latency comparison on a laptop (noisy; use relative comparisons and repeated runs).
10. **Every lab ends with cleanup** (delete namespaces/clusters, remove CRDs installed for the lab if appropriate, remove kubeconfig contexts, stop port-forwards, delete pcap files) and a verification that nothing stray remains. Warn that removing CRDs deletes dependent resources.
11. **Every performance claim** (latency overhead, throughput, footprint, speedups) is tied to a measurement command or labelled "typical range — measure yours". Never quote mesh/CNI/eBPF benchmark numbers as fact.
12. Call out WSL2 vs native Linux differences (nested NAT, `localhost` semantics, Docker network ranges for MetalLB pools, kernel/eBPF support, DNS resolver behavior) wherever they alter outcomes.
13. Validate every manifest mentally against server-side dry-run semantics: selectors match labels, ports/names align (`port`/`targetPort`/`containerPort`/named ports), namespaces are consistent, `parentRefs`/`backendRefs`/`ReferenceGrant`s resolve, `IngressClass`/`GatewayClass` names match the installed controller, and cross-file references resolve.

# 11. PEDAGOGY RULES

- **Packets before YAML:** for every feature, first show the hop-by-hop path and where decisions (NAT, routing, policy, TLS, retries) occur; then show the configuration that controls it.
- **One running example** (data/ML platform) evolving through the folder: pod network → reachable by name → exposed → segmented → encrypted → meshed → resilient → observable → diagnosable.
- **Show failure on purpose:** every unit has at least one lab where the learner breaks the network and diagnoses it with evidence (captures, rule dumps, events, logs).
- **Diagrams** for pod networking (veth/bridge/overlay), Service translation (ClusterIP DNAT), DNS resolution with `ndots`, Ingress/Gateway role model, LB→node→pod paths with source-IP effects, NetworkPolicy evaluation, TLS termination points, cert-manager object flow, mesh control/data plane, mTLS handshake with identities, retry amplification, the timeout ladder, and the eBPF hook points.
- Plain, precise English; no filler or marketing; define acronyms at first use; consistent terms (*pod IP, ClusterIP, endpoint, ingress, gateway, listener, route, policy, identity, proxy, hop*).
- Honest trade-offs; avoid "always/never" without reasons and exceptions; be vendor-neutral and fair between Istio and Linkerd, and between Cilium and other CNIs.

# 12. AUTHENTICITY, AUDIT, AND VERIFICATION PROTOCOL (MANDATORY)

**All learning content must be audited and verified before final submission.** You act as author first, then as an independent auditor of your own work, and you include the audit evidence in the deliverable.

## 12.1 Authoring-time rules
- Base technical claims on **official documentation and specifications**: Kubernetes docs (Services, Networking, DNS for Services and Pods, NetworkPolicy, Ingress, Gateway API concept pages, kube-proxy reference), Gateway API specification and conformance docs, CNI specification, CoreDNS documentation, cert-manager docs, the chosen controller's docs, MetalLB docs, Istio docs, Linkerd docs, Cilium docs, Calico docs (Awareness), RFCs (e.g., TCP/TLS/HTTP/DNS RFCs by number and title where certain), SPIFFE specification, the Linux kernel/`iproute2`/`iptables`/`nftables` docs, CIS Kubernetes Benchmark, NSA/CISA Kubernetes Hardening Guidance, Mozilla/NIST TLS guidance, Google SRE Book/Workbook. Cite by **document name and section/title**, not invented URLs; give a URL only if certain it is canonical, else mark `[VERIFY]`.
- **Do not fabricate:** versions, support/maintenance status of any project, API versions or fields, annotations, CRDs, metric names, flags, default values, quotas, rate limits, benchmark numbers, CVE IDs, RFC numbers you are unsure of, quotes, or tool behaviors. Derive numbers from stated commands or label `[ILLUSTRATIVE]`.
- Mark uncertainty with `[VERIFY]`, `[ILLUSTRATIVE]`, `[VERSION-SENSITIVE]`, or `[ASSUMPTION]`.
- Keep a running **Claim Register** for every non-trivial factual claim.

## 12.2 Mandatory multi-pass self-audit (before delivering each part)

| Pass | Name | What you check | Fail condition |
|---|---|---|---|
| 1 | **Completeness** | All 13 units, all Section 5 sections, all Section 6 topics, L1–L4, all "Must include" labs. | Any gap. |
| 2 | **Technical accuracy** | Every apiVersion/kind/field/annotation/flag/command is real and correctly used; packet paths and NAT/encapsulation descriptions are correct; mentally execute each lab. | Invented or misused syntax/behavior. |
| 3 | **Executability** | YAML valid and internally consistent (labels, selectors, ports, names, `parentRefs`, `IngressClass`); scripts pass ShellCheck in principle; labs have steps, evidence, cleanup; manifests pass server-side dry-run once CRDs exist. | Broken or ambiguous step. |
| 4 | **Currency** | Version- and maintenance-sensitive items tagged; no deprecated/removed API taught as current (e.g., `networking.k8s.io/v1beta1` Ingress, `extensions/v1beta1`, Endpoints-only reasoning where EndpointSlices apply, Gateway API `v1alpha2/v1beta1` where `v1` exists, Istio/Linkerd legacy CRDs, kube-proxy-only assumptions, cert-manager `v1alpha*`); no controller presented as "the standard" without a `[VERIFY]` maintenance check. | Stale or untagged claim. |
| 5 | **Security correctness** | No insecure practice shown as good; no overclaims (NetworkPolicy ≠ authentication or L7 control; mTLS ≠ authorization; a mesh ≠ zero trust by itself; TLS termination at ingress ≠ end-to-end encryption; cert-manager issuing ≠ trust; private key in a Secret ≠ protected without RBAC/encryption; `--insecure` flags are lab-only); no unsafe public exposure. | Overclaim or unlabeled insecure example. |
| 6 | **Fabrication scan** | Hunt for invented numbers, versions, CRD fields, annotations, metric names, outputs shown as measured, benchmark claims, citations. | Any unsupported specific. |
| 7 | **Pedagogical consistency** | True beginner→advanced ramp; no concept used before introduced (e.g., no mesh policy before NetworkPolicy and TLS basics); consistent terms; running example evolves coherently. | Undisclosed forward dependency; drift. |
| 8 | **Cross-consistency** | Questions test only taught content; capstone deliverables map to units; checklists match lessons; README matches content; the kind-fidelity table matches every lab caveat; the single-mesh decision is applied consistently across Units 7, 8, and the capstone. | Orphan item; contradiction. |
| 9 | **Adversarial review** | As a skeptical staff SRE and a security reviewer: list the 10 most likely objections ("what would break, mislead, or weaken security in a real production cluster?") and resolve each. | Unresolved objection. |
| 10 | **Lab safety & feasibility** | Labs run on kind within 4 CPU / 8 GB / 30 GB, are idempotent and context-guarded, never expose anything publicly or probe third-party networks, avoid paid resources, handle CNI/mesh high-risk steps on throwaway clusters, and clean up. | Hidden cost, resource blowout, wrong-cluster risk, public exposure, leftover state. |

## 12.3 Audit artifacts inside the syllabus (final appendices)

**Appendix A — Claim Register:** `ID | Unit | Claim | Source (document + section) | Confidence (High/Med/Low) | Tag`. ≥ **90 entries**, covering every version-sensitive, maintenance-status, and security-relevant claim.

**Appendix B — Audit Report:** `Pass | Result (PASS/FIXED/OPEN) | Defects found | Fixes applied | Residual risk` for passes 1–10. Be candid; report real defects.

**Appendix C — Human Verification Checklist:** every `[VERIFY]` / `[VERSION-SENSITIVE]` item grouped by component (CNI/kind config, kube-proxy/Services/EndpointSlices, CoreDNS, Ingress controller, Gateway API CRDs/versions, MetalLB/cloud-provider-kind, NetworkPolicy/Admin policies, cert-manager, Istio, Linkerd, Cilium/Hubble, tcpdump/tc/conntrack tooling), each with *what to check*, *where (official doc name)*, *how to test with one command*. Closable by a reviewer in under 6 hours.

**Appendix D — Known Limitations and Assumptions:** what is out of scope (cloud LB specifics, BGP, multi-cluster networking, full observability stack, Helm packaging), assumed Kubernetes/tool versions, kind fidelity limits, WSL2 caveats, anything unverified.

**Appendix E — Sign-off block:** `Content status: DRAFT-AUDITED | Audit date | Auditor: AI self-audit (requires human verification) | Unverified items count`. State plainly that AI self-audit does not replace a human running the labs on a real kind cluster.

## 12.4 Trust rules
- If a pass finds a defect you cannot confidently fix, leave it visible as `OPEN` in Appendix B and list it in Appendix C. Never hide uncertainty.
- Never claim a command or manifest "was run/tested" unless it actually was. Use "expected output (representative)".
- Never claim verification against live documentation unless you consulted it; otherwise say "written from knowledge of the documentation; verify against current docs".

# 13. OUTPUT FORMAT

- **One Markdown document:** `SYLLABUS-Kubernetes-Networking-Ingress-and-Service-Mesh.md`.
- Begin with: title, abstract paragraph, metadata block (`Module: M04`, `Stage: 2E`, `Estimated total time`, `Last reviewed`, `Assumed tool baseline`), and a **linked table of contents** to all units and appendices.
- Then Units 0–12 in order, then Appendices A–E.
- Headings: `#` title, `##` units, `###`/`####` below; tables for comparisons; fenced code with language tags; mermaid for diagrams.
- Cross-link units with relative links to sibling target files.
- **Depth target:** Units 1–10 each ≥ 2,500 words of teaching text excluding code and manifests; ≥ 150 practice questions; capstone with complete code. **Do not compress to fit**—use the Delivery Protocol.
- No placeholder text, no "etc." in required lists, no "exercise left to the reader" for required deliverables.

# 14. DELIVERY PROTOCOL

Deliver in **numbered parts**; wait for the user to type `continue` between parts.

| Part | Content |
|---|---|
| 1 | Title, abstract, metadata, TOC, Unit 0, Unit 1 |
| 2 | Units 2, 3 |
| 3 | Units 4, 5 |
| 4 | Units 6, 7 |
| 5 | Units 8, 9 |
| 6 | Unit 10 |
| 7 | Unit 11 (practice questions) |
| 8 | Unit 12 (capstone, full code) |
| 9 | Appendices A–E, including the cross-part audit |

Rules:
- End each part with: `PART n/9 COMPLETE — units delivered: …; open [VERIFY] items so far: <count>; next: Part n+1`.
- Run the per-unit audit (passes 1–10, scoped) **before** printing each part; maintain the Claim Register throughout.
- Part 9 runs the cross-part audit (passes 7, 8, 9 especially) and lists every correction to earlier parts as `CORRECTION: Part n, Unit x, section y — old → new`.
- Never summarize a unit to save space. If nearing the length limit, stop at a clean section boundary, print `TRUNCATED AT: <unit/section>`, and resume exactly there on `continue`.
- After Part 9 print: "Concatenate Parts 1–9 in order into `SYLLABUS-Kubernetes-Networking-Ingress-and-Service-Mesh.md` and apply all listed corrections."

# 15. DEFINITION OF DONE

- [ ] All 13 units present in order; Units 1–10 each have L1–L4 and sections N.0–N.14.
- [ ] Every Section 6 topic taught at its stated level, with every kind-simulation limit stated honestly.
- [ ] Exactly one hands-on service mesh chosen and justified; the other compared; the decision applied consistently.
- [ ] ≥ 150 practice questions with model answers and distractor analysis, including packet-walk questions.
- [ ] Capstone has complete runnable code, acceptance criteria, rubric, matrix test, `make verify`, and a blank measurement template.
- [ ] Every lab has context guard, steps, expected evidence, cleanup; all fit the local baseline; none touch the public internet or third-party hosts.
- [ ] No fabricated versions, fields, annotations, metric names, maintenance claims, numbers, or citations; every uncertainty tagged.
- [ ] Appendices A–E present; Claim Register ≥ 90; passes 1–10 reported candidly.
- [ ] Running example evolves coherently across all units.
- [ ] Forward references (M01–M03, M05, M06, M08–M12, M14–M16) explicit and not half-taught.
- [ ] A human can close every open item in under 6 hours using Appendix C.

# 16. START

Confirm in **one line** that you understand the task, then immediately begin **Part 1/9**. Do not ask clarifying questions; record an `[ASSUMPTION]` where information is missing and proceed.

=== END PROMPT ===

---

## Notes for the human operator (not part of the prompt)

1. Use one long conversation across all 9 parts so the Claim Register and running example stay consistent.
2. AI self-audit is not independent. Run the labs on a real kind cluster and close every `[VERIFY]` item against current official docs.
3. Highest fabrication risk, check first:
   - Maintenance status of each ingress controller. The prompt forbids assuming any controller is current.
   - Gateway API versions and which resources are GA.
   - kind steps for a custom CNI (`disableDefaultCNI`), MetalLB and `cloud-provider-kind`.
   - Istio and Linkerd CRD names and API versions, since both have changed over time.
   - cert-manager metric names and minimum `duration` / `renewBefore` values.
   - Cilium and Hubble CLI commands.
   - `AdminNetworkPolicy` maturity.
4. Scope decisions I made, which you can change:
   - The tooling map lists Gateway API, cert-manager and service mesh as Awareness, but this folder has dedicated modules for them. The prompt teaches them at working depth.
   - Exactly one mesh is hands-on, chosen for the 8 GB budget. The other is a comparison. Running Istio, Cilium with Hubble and an observability stack at once will not fit in 8 GB.
   - Public ACME and Let's Encrypt are Awareness only. Labs use a local CA, so no real domain or internet exposure is needed.
5. Network labs involve packet capture and fault injection. The prompt limits them to the learner's own lab cluster and traffic, and has the learner delete pcaps afterward.
6. Several labs, such as the CNI swap and mesh removal, are high-risk. They are labelled as such and meant only for throwaway clusters.
