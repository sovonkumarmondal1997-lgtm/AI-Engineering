# M04 Practice Questions — Kubernetes Networking, Ingress, and Service Mesh

## Purpose, audience, and how to use this bank

This bank assesses the M04 sequence from Unit 0 orientation through Units 1–10 and capstone integration. Attempt each question before consulting the answer key. For scenarios, write the symptom, evidence, ranked hypotheses, discriminating test, smallest safe fix, verification and prevention. For version-sensitive topics, answer with the verification method if the installed version is unknown.

**Audience:** Learners who have completed Stages 0–2D and M01–M03, know Linux/TCP/IP/DNS/HTTP/TLS and basic Kubernetes objects, and are beginning production networking operations. This bank supplements the lessons and labs; it does not replace them.

- **L1:** Beginner — Foundations.
- **L2:** Intermediate — Working Practice.
- **L3:** Advanced — Production Engineering.
- **L4:** Expert — Operating at Scale and Under Failure.

All hands-on work must stay in a learner-owned disposable local cluster. Never probe third-party networks or production clusters. Label version-dependent behavior `[VERIFY]`; distinguish authored expectations from actual observations. For mutating work, confirm context and target before acting, use the smallest scope, and clean up.

## Source Coverage and Limitations

**Inspected:** `Roadmap(5).md` (M04 tree and unit order); `PROMPT-Kubernetes-Networking-Ingress-and-Service-Mesh(9).md` (available syllabus-generation prompt and module-specific requirements); sibling lessons `01-kubernetes-networking-model-cni-and-pod-networking.md` through `10-network-troubleshooting-dns-latency-and-packet-loss.md`; and the uploaded practice-question generation prompt. The available Unit 7 lesson selects Linkerd sidecar mode for hands-on work, with Istio as comparison/awareness; this bank preserves that assumption.

**Unavailable as separate files in the inspected workspace:** the exact M04 copy-paste prompt pack named by the uploaded prompt, `Projects/README.md`, and `Projects/01-secure-ingress-and-mtls-for-data-and-ml-apis.md`. The roadmap tree lists the capstone files, but their detailed content was not available for inspection. Therefore capstone questions assess only integration themes stated in the uploaded prompt and available syllabus; exact project-specific acceptance criteria remain `[OPEN — SOURCE GAP]`. No lab or command was executed while generating this bank. No live documentation lookup is claimed here.

**Source-derived vs inference:** unit names/order, four-level teaching framework, local-lab constraints, selected Linkerd assumption and listed technical coverage come from inspected sources. Question formats, scoring, scenario rubrics and some capstone integration prompts are assessment-design inferences, labelled where they depend on unavailable project detail. No source conflict was silently resolved.

## Exam blueprint and coverage map

| Unit/topic | Question IDs | L1/L2/L3/L4 coverage | Formats represented | Source basis |
|---|---:|---|---|---|
| Unit 1 — Kubernetes networking model, CNI and Pod networking | Q001–Q016 (16) | L1: 4, L2: 5, L3: 5, L4: 2 | Short answer, MCQ, Packet-path tracing, Find the defect, Select all, Scenario, Compare/design, Design review, True/false, Output interpretation | Roadmap + syllabus + lesson |
| Unit 2 — Services, kube-proxy and cluster DNS | Q017–Q034 (18) | L1: 3, L2: 8, L3: 5, L4: 2 | Short answer, YAML interpretation, Scenario, Find the defect, SRE design, Design review | Roadmap + syllabus + lesson |
| Unit 3 — Ingress controllers and Gateway API | Q035–Q052 (18) | L1: 3, L2: 8, L3: 5, L4: 2 | Short answer, Scenario, Find the defect, Design review, Practical, Security review, SRE design | Roadmap + syllabus + lesson |
| Unit 4 — Load balancers and external traffic management | Q053–Q066 (14) | L1: 2, L2: 5, L3: 5, L4: 2 | Short answer, Compare/design, Scenario, True/false, Design review, SRE design, Find the defect | Roadmap + syllabus + lesson |
| Unit 5 — Network policies and zero-trust segmentation | Q067–Q082 (16) | L1: 3, L2: 6, L3: 5, L4: 2 | Short answer, Find the defect, Scenario, Design review, Security review, Compare/design, SRE design | Roadmap + syllabus + lesson |
| Unit 6 — TLS termination and certificate lifecycle | Q083–Q098 (16) | L1: 3, L2: 6, L3: 5, L4: 2 | Short answer, Compare/design, Find the defect, Practical, Scenario, Security review, SRE design, Design review | Roadmap + syllabus + lesson |
| Unit 7 — Service mesh fundamentals: Istio and Linkerd | Q099–Q112 (14) | L1: 2, L2: 5, L3: 5, L4: 2 | Short answer, Design review, Scenario, Find the defect, SRE design | Roadmap + syllabus + lesson |
| Unit 8 — mTLS, traffic shifting, retries and circuit breaking | Q113–Q130 (18) | L1: 3, L2: 8, L3: 5, L4: 2 | Short answer, Scenario, Practical, Find the defect, Design review, Security review | Roadmap + syllabus + lesson |
| Unit 9 — eBPF networking and Cilium overview | Q131–Q142 (12) | L1: 1, L2: 5, L3: 5, L4: 1 | Short answer, Design review, Scenario, Security review, SRE design | Roadmap + syllabus + lesson |
| Unit 10 — Network troubleshooting: DNS, latency and packet loss | Q143–Q164 (22) | L1: 5, L2: 8, L3: 7, L4: 2 | Short answer, Scenario, Packet capture, Security review, SRE design, Practical | Roadmap + syllabus + lesson |
| Cross-unit architecture and capstone | Q165–Q184 (20) | L1: 3, L2: 8, L3: 7, L4: 2 | Architecture review, Scenario, Practical, Design review, SRE design, Security review, Short answer, Source reasoning | Syllabus integration themes; detailed capstone source unavailable |

**Bank totals:** 184 questions; 43 scenario-tagged; 153 packet/request-path-tagged; 22 defect-finding-tagged. The tags may overlap. Counts are computed from the authored records below.

## How to score yourself

Score 100 points across four dimensions: **knowledge recall 20**, **applied reasoning 25**, **troubleshooting evidence 30**, and **safety/version judgment 25**. Use the question bank as a practice set; normalize the raw question score to 100 only after grading against the model answers.

| Dimension | Points | Full-credit standard |
|---|---:|---|
| Knowledge recall | 20 | Correct concepts, terminology and Kubernetes object boundaries; no unsupported universal claims |
| Applied reasoning | 25 | Correct request path, dependencies, trade-offs and expected observations |
| Troubleshooting evidence | 30 | Evidence-first sequence, discriminating test, interpretation, verification and prevention |
| Safety/version judgment | 25 | Correct context guard, local-only scope, least privilege, rollback, source/version verification and honest uncertainty |

**Performance bands:** 90–100 Exemplary; 80–89 Strong; 70–79 Adequate but revisit weak units; below 70 Remediate before claiming operational readiness. A severe safety error (e.g., mutation against an unknown/production context, disabling all policy, or leaking secrets) should trigger remediation regardless of total score. For `[VERIFY]` items, award full credit for naming the official source/version/schema to inspect and a safe validation method; do not penalize learners for refusing to guess.

## Question Bank

### Unit 1 — Kubernetes networking model, CNI and Pod networking

**Q001** — **[L1]** **Format:** Short answer · **Topic:** network model, packet/request path

State the four core Kubernetes networking requirements commonly used as a conceptual baseline. Why are they not a complete design specification?

**Q002** — **[L1]** **Format:** MCQ · **Topic:** IP identity

MCQ: Which address identifies a Kubernetes node rather than a workload endpoint? A) Pod IP B) node IP C) ClusterIP D) headless Service DNS name

**Q003** — **[L2]** **Format:** Short answer · **Topic:** network namespaces, packet/request path

Explain why containers in one Pod can ordinarily communicate over localhost while containers in different Pods cannot assume the same localhost.

**Q004** — **[L2]** **Format:** Packet-path tracing · **Topic:** cross-node path, scenario, packet/request path

Trace a request from Pod A on node 1 to Pod B on node 2. Name the evidence needed before claiming an overlay tunnel is involved.

**Q005** — **[L2]** **Format:** Find the defect · **Topic:** CNI implementation, packet/request path, defect-finding

Find the defect: a team assumes every CNI uses the same bridge and veth topology and writes a runbook that inspects only `cni0`. What is wrong with the runbook?

**Q006** — **[L3]** **Format:** Short answer · **Topic:** CNI versus Service datapath, packet/request path

What responsibilities does the CNI generally address, and why should it not be treated as synonymous with kube-proxy?

**Q007** — **[L3]** **Format:** Select all · **Topic:** CNI selection

Select all that apply: Which items should a CNI decision record compare? A) policy enforcement B) observability C) encryption options D) operational skill/upgrade risk E) only the logo

**Q008** — **[L3]** **Format:** Scenario · **Topic:** CNI failure, scenario, packet/request path, defect-finding

A Pod remains in `ContainerCreating` and events mention network setup. Give an evidence-first triage sequence.

**Q009** — **[L4]** **Format:** Short answer · **Topic:** MTU and PMTUD, packet/request path

Why can overlay encapsulation affect MTU and large-packet behavior?

**Q010** — **[L1]** **Format:** Compare/design · **Topic:** network architecture, packet/request path

Explain one practical difference among overlay, routed and cloud-native Pod networking.

**Q011** — **[L2]** **Format:** Design review · **Topic:** IPAM/CIDR, scenario

A cluster is close to Pod CIDR exhaustion. What should be assessed before changing CIDRs?

**Q012** — **[L2]** **Format:** True/false · **Topic:** hostNetwork

True/false with justification: `hostNetwork: true` is a universal fix for Pod networking failures.

**Q013** — **[L3]** **Format:** Packet-path tracing · **Topic:** address identity, scenario, packet/request path

What evidence distinguishes a Pod IP, node IP and Service IP during a packet-path investigation?

**Q014** — **[L3]** **Format:** Scenario · **Topic:** CNI migration, scenario, packet/request path

Name four CNI migration risks and a safe rollout principle.

**Q015** — **[L4]** **Format:** Design review · **Topic:** ADR

What should a CNI ADR contain besides the chosen plugin name?

**Q016** — **[L1]** **Format:** Output interpretation · **Topic:** veth and routes, packet/request path, defect-finding

A learner sees `ip link` output with veth-like interfaces. What can and cannot be concluded?

### Unit 2 — Services, kube-proxy and cluster DNS

**Q017** — **[L2]** **Format:** Short answer · **Topic:** Service types, packet/request path

Distinguish ClusterIP, NodePort, LoadBalancer, ExternalName and headless Services.

**Q018** — **[L2]** **Format:** YAML interpretation · **Topic:** port mapping, packet/request path, defect-finding

A Service has `port: 80` and `targetPort: 8081`. Which port does the client use and which port is the backend expected to accept?

**Q019** — **[L2]** **Format:** Short answer · **Topic:** EndpointSlice, packet/request path

What is an EndpointSlice, and why is checking only the Service object insufficient?

**Q020** — **[L3]** **Format:** Scenario · **Topic:** Service diagnosis, scenario, packet/request path, defect-finding

A Service resolves to a ClusterIP but requests time out. List the first four checks in order.

**Q021** — **[L3]** **Format:** Short answer · **Topic:** kube-proxy, packet/request path

Explain the kube-proxy responsibility and one reason the assumption “every cluster uses iptables kube-proxy” is unsafe.

**Q022** — **[L3]** **Format:** Short answer · **Topic:** CoreDNS, packet/request path

What is the purpose of CoreDNS in a typical Kubernetes cluster, and what evidence is needed before declaring it the root cause?

**Q023** — **[L4]** **Format:** Short answer · **Topic:** ndots, packet/request path

Explain how search domains and `ndots:5` can increase DNS query volume for a short or partially qualified name.

**Q024** — **[L1]** **Format:** Short answer · **Topic:** FQDN, packet/request path

What is the purpose of a trailing dot on an FQDN, and what caveat should an application engineer remember?

**Q025** — **[L2]** **Format:** Find the defect · **Topic:** resolver mismatch, packet/request path, defect-finding

Find the defect in this reasoning: “The Pod's `nslookup` succeeds, therefore the application’s DNS path is healthy.”

**Q026** — **[L2]** **Format:** Short answer · **Topic:** NodeLocal DNSCache, packet/request path

What is NodeLocal DNSCache intended to improve, and what must be verified before depending on it?

**Q027** — **[L3]** **Format:** Scenario · **Topic:** DNS policy, scenario, packet/request path

Why can DNS over TCP matter even when most DNS queries use UDP?

**Q028** — **[L3]** **Format:** Scenario · **Topic:** LoadBalancer pending, scenario, defect-finding

A `LoadBalancer` Service shows `<pending>` for EXTERNAL-IP. What is the right interpretation?

**Q029** — **[L4]** **Format:** Short answer · **Topic:** headless Service, packet/request path

What is a headless Service useful for, and how does its DNS behavior differ from a normal ClusterIP Service?

**Q030** — **[L1]** **Format:** Scenario · **Topic:** rollout endpoints, scenario, packet/request path

Describe how EndpointSlice propagation and connection draining can produce different observations during rollout.

**Q031** — **[L1]** **Format:** Scenario · **Topic:** conntrack, scenario, packet/request path

What are safe first steps for suspected conntrack pressure affecting Service or DNS traffic?

**Q032** — **[L2]** **Format:** SRE design · **Topic:** DNS SLO, packet/request path

Design a DNS SLO and a synthetic probe for `feature-service`.

**Q033** — **[L2]** **Format:** Design review · **Topic:** selectorless Service, packet/request path

What are the limits of manually managed EndpointSlices or a selectorless Service?

**Q034** — **[L2]** **Format:** Short answer · **Topic:** DNS errors, packet/request path

A DNS lookup returns SERVFAIL. What does that suggest, and what does it not prove?

### Unit 3 — Ingress controllers and Gateway API

**Q035** — **[L2]** **Format:** Short answer · **Topic:** Ingress object/controller, packet/request path

Distinguish an Ingress API object from an Ingress controller.

**Q036** — **[L2]** **Format:** Short answer · **Topic:** traffic direction, packet/request path

Explain north–south versus east–west traffic and L4 versus L7 routing.

**Q037** — **[L2]** **Format:** Scenario · **Topic:** IngressClass, scenario, packet/request path, defect-finding

What is the role of IngressClass, and how can a wrong class appear operationally?

**Q038** — **[L3]** **Format:** Find the defect · **Topic:** desired vs observed, packet/request path, defect-finding

Find the defect: a team applies an Ingress manifest and immediately declares the endpoint production-ready because `kubectl apply` succeeded.

**Q039** — **[L3]** **Format:** Short answer · **Topic:** Gateway API, packet/request path

Name the main Gateway API resource roles: GatewayClass, Gateway and HTTPRoute.

**Q040** — **[L3]** **Format:** Short answer · **Topic:** ReferenceGrant

When may ReferenceGrant matter?

**Q041** — **[L4]** **Format:** Scenario · **Topic:** HTTPRoute status, scenario, packet/request path, defect-finding

What evidence should be collected when an HTTPRoute is not accepted or programmed?

**Q042** — **[L1]** **Format:** Design review · **Topic:** Ingress vs Gateway API, packet/request path

Compare Ingress and Gateway API as design choices without declaring one universally superior.

**Q043** — **[L2]** **Format:** Short answer · **Topic:** annotations

Why are controller-specific annotations a portability and security risk?

**Q044** — **[L2]** **Format:** Scenario · **Topic:** HTTP status, scenario, packet/request path

A route returns 502, 503 or 504. How do you identify the actual failure rather than infer from the code alone?

**Q045** — **[L3]** **Format:** Design review · **Topic:** streaming, packet/request path

What should be considered when routing gRPC, HTTP/2, SSE or long-lived streams through a proxy?

**Q046** — **[L3]** **Format:** Practical · **Topic:** weighted routing, packet/request path

Explain a safe 90/10 weighted canary test and why configured weights are not proof of observed proportions.

**Q047** — **[L4]** **Format:** Scenario · **Topic:** route debugging, scenario, packet/request path, defect-finding

How should an invalid route be debugged?

**Q048** — **[L1]** **Format:** Design review · **Topic:** controller selection

What factors belong in an ingress-controller selection review?

**Q049** — **[L1]** **Format:** Short answer · **Topic:** client IP, packet/request path

How can client IP preservation be lost or misinterpreted?

**Q050** — **[L2]** **Format:** Security review · **Topic:** multi-tenancy

What should a multi-tenant Gateway design prevent?

**Q051** — **[L2]** **Format:** SRE design · **Topic:** HA/PDB, packet/request path

Why should controller HA and PodDisruptionBudget be reviewed together?

**Q052** — **[L2]** **Format:** Design review · **Topic:** migration, packet/request path

Name a safe migration sequence from an existing Ingress to Gateway API.

### Unit 4 — Load balancers and external traffic management

**Q053** — **[L2]** **Format:** Short answer · **Topic:** LoadBalancer, packet/request path

Why can a LoadBalancer Service remain pending in a local kind cluster?

**Q054** — **[L2]** **Format:** Short answer · **Topic:** L4/L7, packet/request path

Compare L4 and L7 load balancing with one suitable use case each.

**Q055** — **[L2]** **Format:** Compare/design · **Topic:** externalTrafficPolicy, packet/request path

Compare `externalTrafficPolicy: Cluster` and `Local` at a high level.

**Q056** — **[L3]** **Format:** Scenario · **Topic:** node path, scenario, packet/request path, defect-finding

A service is reachable on one node but not another. What should be checked before changing the Service?

**Q057** — **[L3]** **Format:** Short answer · **Topic:** health checks, packet/request path

Explain why `EXTERNAL-IP` is not a sufficient health signal for a load balancer.

**Q058** — **[L3]** **Format:** Scenario · **Topic:** draining, scenario, packet/request path

What is connection draining and why does it matter during rollout/node drain?

**Q059** — **[L4]** **Format:** Short answer · **Topic:** timeout ladder, packet/request path

Describe a timeout ladder across external LB, ingress, mesh and app.

**Q060** — **[L1]** **Format:** Scenario · **Topic:** egress NAT, scenario, packet/request path

How can egress SNAT and ephemeral-port limits affect ETL workers?

**Q061** — **[L2]** **Format:** True/false · **Topic:** kind fidelity

A learner proposes a local LoadBalancer helper and claims it proves cloud failover. What is missing?

**Q062** — **[L2]** **Format:** Short answer · **Topic:** health checks, packet/request path

What is the difference between TCP and HTTP health checks?

**Q063** — **[L3]** **Format:** Short answer · **Topic:** TLS boundary, packet/request path

Why should TLS passthrough be distinguished from TLS termination and re-encryption?

**Q064** — **[L3]** **Format:** Design review · **Topic:** global traffic, packet/request path

How should global/regional traffic management be treated in a zero-budget local curriculum?

**Q065** — **[L4]** **Format:** SRE design · **Topic:** algorithms

What evidence is needed before claiming a load-balancer algorithm is best?

**Q066** — **[L1]** **Format:** Find the defect · **Topic:** forwarded headers, packet/request path, defect-finding

Find the defect: the team trusts arbitrary `X-Forwarded-For` from every client for audit and authorization.

### Unit 5 — Network policies and zero-trust segmentation

**Q067** — **[L2]** **Format:** Short answer · **Topic:** policy boundary, packet/request path

What does Kubernetes NetworkPolicy control, and what does it not provide by itself?

**Q068** — **[L2]** **Format:** Short answer · **Topic:** additive policy, packet/request path

Explain additive policy semantics for a Pod that is isolated for ingress.

**Q069** — **[L2]** **Format:** Find the defect · **Topic:** selector mismatch, packet/request path, defect-finding

Find the selector defect: policy selects `app: model-api`, but actual Pods use `app.kubernetes.io/name: model-api`.

**Q070** — **[L3]** **Format:** Scenario · **Topic:** DNS egress, scenario, packet/request path

Why is DNS egress commonly forgotten in default-deny egress policy?

**Q071** — **[L3]** **Format:** Short answer · **Topic:** CNI enforcement, packet/request path

What prerequisite must be met before treating a NetworkPolicy lab result as proof of enforcement?

**Q072** — **[L3]** **Format:** Design review · **Topic:** least privilege, packet/request path

Design minimum connectivity for model-api → feature-service and model-api → Postgres/Redis.

**Q073** — **[L4]** **Format:** Short answer · **Topic:** namespace selector

Why is “allow all traffic from namespace X” often broader than intended?

**Q074** — **[L1]** **Format:** Design review · **Topic:** egress control, packet/request path

How should egress to external APIs be controlled for the ETL worker?

**Q075** — **[L2]** **Format:** Security review · **Topic:** SSRF, packet/request path

What is the defensive relationship between NetworkPolicy and SSRF/metadata risks?

**Q076** — **[L2]** **Format:** Scenario · **Topic:** policy rollout, scenario, packet/request path

Describe an observe → audit → enforce rollout for policy.

**Q077** — **[L3]** **Format:** Short answer · **Topic:** desired vs observed, packet/request path

What is the difference between a policy object and an enforced network control?

**Q078** — **[L3]** **Format:** Compare/design · **Topic:** policy and mesh, packet/request path

How should Kubernetes NetworkPolicy and mesh authorization be layered?

**Q079** — **[L4]** **Format:** Scenario · **Topic:** safe operations, scenario

What is the risk of disabling all NetworkPolicies during troubleshooting?

**Q080** — **[L1]** **Format:** SRE design · **Topic:** policy testing, packet/request path

Which tests should policy CI include for a model-serving platform?

**Q081** — **[L1]** **Format:** Short answer · **Topic:** L7/FQDN policy, packet/request path

Explain the limit of vanilla NetworkPolicy for L7 HTTP paths and FQDNs.

**Q082** — **[L2]** **Format:** Scenario · **Topic:** policy diagnosis, scenario, packet/request path, defect-finding

A DNS policy test fails only when the application Pod is selected by a default-deny rule. What evidence would distinguish selector mistake from missing DNS allowance?

### Unit 6 — TLS termination and certificate lifecycle

**Q083** — **[L2]** **Format:** Short answer · **Topic:** certificate meaning, packet/request path

What does a server certificate establish, and what does it not establish by itself?

**Q084** — **[L2]** **Format:** Short answer · **Topic:** SAN, packet/request path

Explain SAN/hostname verification and why checking only the certificate Common Name is insufficient as a modern habit.

**Q085** — **[L2]** **Format:** Short answer · **Topic:** SNI, packet/request path

What is SNI and why can a correct certificate appear wrong when testing an endpoint by IP?

**Q086** — **[L3]** **Format:** Compare/design · **Topic:** termination modes, packet/request path

Compare TLS passthrough, termination and re-encryption at ingress.

**Q087** — **[L3]** **Format:** Find the defect · **Topic:** TLS validation, packet/request path, defect-finding

Find the defect: `curl -k` succeeds, so the team declares certificate configuration correct.

**Q088** — **[L3]** **Format:** Short answer · **Topic:** cert-manager, packet/request path

Describe the cert-manager reconciliation flow at a conceptual level.

**Q089** — **[L4]** **Format:** Practical · **Topic:** local CA, packet/request path

What is the safe approach to local certificate practice under the zero-budget constraint?

**Q090** — **[L1]** **Format:** Scenario · **Topic:** renewal diagnosis, scenario, packet/request path, defect-finding

A certificate is not renewing. What evidence should be checked before deleting Certificate resources?

**Q091** — **[L2]** **Format:** Security review · **Topic:** private keys

How should private keys and TLS Secrets be protected?

**Q092** — **[L2]** **Format:** Short answer · **Topic:** certificate chain, packet/request path

Explain certificate chain validation and a common intermediate-chain failure.

**Q093** — **[L3]** **Format:** Scenario · **Topic:** client divergence, scenario, packet/request path

A TLS endpoint works from one client but not another. Give a discriminating investigation.

**Q094** — **[L3]** **Format:** SRE design · **Topic:** expiry monitoring, packet/request path

What should an expiry alert monitor beyond the certificate's notAfter date?

**Q095** — **[L4]** **Format:** Short answer · **Topic:** security properties, packet/request path

What is the difference between encryption, authentication and authorization in an mTLS path?

**Q096** — **[L1]** **Format:** Short answer · **Topic:** ALPN, packet/request path

What does ALPN contribute to TLS troubleshooting?

**Q097** — **[L1]** **Format:** Design review · **Topic:** backend encryption, packet/request path

Why should ingress-to-backend encryption be explicitly documented?

**Q098** — **[L2]** **Format:** Practical · **Topic:** TLS acceptance, packet/request path

What evidence validates a local TLS acceptance test?

### Unit 7 — Service mesh fundamentals: Istio and Linkerd

**Q099** — **[L2]** **Format:** Short answer · **Topic:** control/data plane, packet/request path

Distinguish service-mesh control plane and data plane.

**Q100** — **[L2]** **Format:** Short answer · **Topic:** sidecar, packet/request path

What is the main traffic-path implication of sidecar mode?

**Q101** — **[L2]** **Format:** Design review · **Topic:** mesh comparison, packet/request path

Compare Istio and Linkerd fairly for a constrained 4-CPU/8-GB lab.

**Q102** — **[L3]** **Format:** Short answer · **Topic:** selected mesh

Which mesh is the chosen hands-on mesh in this roadmap context, and how should the other be treated?

**Q103** — **[L3]** **Format:** Scenario · **Topic:** injection, scenario, packet/request path, defect-finding

A namespace has a mesh-injection label but a Pod has no proxy. What do you inspect?

**Q104** — **[L3]** **Format:** Short answer · **Topic:** mesh/policy, packet/request path

Name four ways a mesh can interact with NetworkPolicy.

**Q105** — **[L4]** **Format:** Design review · **Topic:** upgrade

What should a mesh upgrade plan include?

**Q106** — **[L1]** **Format:** Find the defect · **Topic:** mesh boundaries, packet/request path, defect-finding

Find the defect: a team claims the mesh automatically secures every packet including host traffic and all external egress.

**Q107** — **[L2]** **Format:** Short answer · **Topic:** mesh evidence, packet/request path

What evidence proves a workload is meshed rather than merely configured for injection?

**Q108** — **[L2]** **Format:** Scenario · **Topic:** sidecar operations, scenario, packet/request path

How can sidecars affect Jobs, probes and resource budgets?

**Q109** — **[L3]** **Format:** Short answer · **Topic:** mesh limitations, packet/request path

What does a mesh not automatically solve?

**Q110** — **[L3]** **Format:** SRE design · **Topic:** measurement

How should mesh latency overhead be measured?

**Q111** — **[L4]** **Format:** Scenario · **Topic:** control-plane failure, scenario, packet/request path

A mesh control plane is unavailable. What is the first question?

**Q112** — **[L1]** **Format:** Short answer · **Topic:** mesh security, packet/request path

Why is “mesh installed” not equivalent to “mTLS and authorization are correctly enforced”?

### Unit 8 — mTLS, traffic shifting, retries and circuit breaking

**Q113** — **[L2]** **Format:** Short answer · **Topic:** mTLS, packet/request path

Differentiate TLS and mTLS in a service-to-service call.

**Q114** — **[L2]** **Format:** Short answer · **Topic:** strict/permissive, packet/request path

What does strict versus permissive mTLS mean conceptually, and why is the exact configuration version-sensitive?

**Q115** — **[L2]** **Format:** Scenario · **Topic:** mTLS mismatch, scenario, packet/request path, defect-finding

A plaintext client fails after strict mTLS is enabled. Give the evidence-first path.

**Q116** — **[L3]** **Format:** Short answer · **Topic:** security properties, packet/request path

Why is encryption not the same as authorization?

**Q117** — **[L3]** **Format:** Practical · **Topic:** canary split, packet/request path

A route is configured for 90/10 stable/candidate traffic. How do you verify the observed split?

**Q118** — **[L3]** **Format:** Short answer · **Topic:** retry amplification, packet/request path

Compute retry amplification: a request makes 3 attempts at each of 3 serial dependency layers, including the initial attempt. What is the worst-case leaf attempt count if each layer independently retries every downstream attempt?

**Q119** — **[L4]** **Format:** Short answer · **Topic:** retry safety, packet/request path

What makes a retry safe or unsafe?

**Q120** — **[L1]** **Format:** Short answer · **Topic:** timeout budget, packet/request path

Why should per-try timeout be shorter than the overall request deadline?

**Q121** — **[L2]** **Format:** Short answer · **Topic:** circuit breaker, packet/request path

What is a circuit breaker intended to do, and how does it differ from retrying?

**Q122** — **[L2]** **Format:** Find the defect · **Topic:** canary evidence, packet/request path, defect-finding

Find the defect: the canary is declared successful because the manifest specifies 10% candidate traffic.

**Q123** — **[L3]** **Format:** Scenario · **Topic:** long-lived streams, scenario, packet/request path

How should long-lived gRPC/SSE connections affect traffic-shift expectations?

**Q124** — **[L3]** **Format:** Short answer · **Topic:** outlier detection, packet/request path

What is outlier detection, and what can go wrong with aggressive ejection?

**Q125** — **[L4]** **Format:** Practical · **Topic:** fault injection, packet/request path

What should a fault-injection experiment specify before adding delay/abort?

**Q126** — **[L1]** **Format:** Design review · **Topic:** retry ownership, packet/request path

How do application-level and mesh-level retries interact?

**Q127** — **[L1]** **Format:** Security review · **Topic:** mirroring, packet/request path

How should traffic mirroring/shadowing be assessed for a new model version?

**Q128** — **[L2]** **Format:** Short answer · **Topic:** rate limiting

What is the difference between local and global rate limiting at a conceptual level?

**Q129** — **[L2]** **Format:** Scenario · **Topic:** strict rollout, scenario, packet/request path

How should strict mTLS rollout be staged?

**Q130** — **[L2]** **Format:** Short answer · **Topic:** defense in depth, packet/request path

Why must Kubernetes NetworkPolicy remain in the defense-in-depth design even when a mesh has authorization policy?

### Unit 9 — eBPF networking and Cilium overview

**Q131** — **[L2]** **Format:** Short answer · **Topic:** eBPF, packet/request path

What is eBPF at a conceptual level, and why does kernel/version compatibility matter?

**Q132** — **[L2]** **Format:** Short answer · **Topic:** CNI/datapath, packet/request path

Distinguish CNI integration from an eBPF datapath.

**Q133** — **[L2]** **Format:** Short answer · **Topic:** Cilium capabilities, packet/request path

What responsibilities might Cilium provide beyond basic Pod connectivity?

**Q134** — **[L3]** **Format:** Short answer · **Topic:** Hubble, packet/request path

What can Hubble flow evidence tell you, and what can it not prove?

**Q135** — **[L3]** **Format:** Design review · **Topic:** CNI comparison

Compare Cilium and another CNI using an evidence-based decision framework.

**Q136** — **[L3]** **Format:** Scenario · **Topic:** kube-proxy replacement, scenario, packet/request path

What must be checked before enabling kube-proxy replacement?

**Q137** — **[L4]** **Format:** Short answer · **Topic:** CRD availability, packet/request path

Why should a Cilium policy exercise not assume a CRD exists?

**Q138** — **[L1]** **Format:** Short answer · **Topic:** encryption boundary, packet/request path

Explain the difference between transparent network encryption and mTLS.

**Q139** — **[L2]** **Format:** Security review · **Topic:** cluster-wide policy, packet/request path

What are the risks of applying a cluster-wide policy during a learning lab?

**Q140** — **[L2]** **Format:** Scenario · **Topic:** WSL2 constraints, scenario, packet/request path

A Cilium installation fails on WSL2. What is a safe response?

**Q141** — **[L3]** **Format:** Short answer · **Topic:** FQDN/L7, packet/request path

How should FQDN/L7 policy claims be treated?

**Q142** — **[L3]** **Format:** SRE design · **Topic:** performance

Why is an eBPF performance comparison method more useful than a single headline number?

### Unit 10 — Network troubleshooting: DNS, latency and packet loss

**Q143** — **[L1]** **Format:** Short answer · **Topic:** methodology, packet/request path

State the evidence-first troubleshooting sequence used in this module.

**Q144** — **[L1]** **Format:** Short answer · **Topic:** curl timing, packet/request path

What do curl's name lookup, connect, appconnect, start-transfer and total timing fields broadly represent?

**Q145** — **[L2]** **Format:** Scenario · **Topic:** ICMP, scenario, packet/request path

A `ping` to a Service IP fails but a bounded TCP request succeeds. What is the correct conclusion?

**Q146** — **[L2]** **Format:** Short answer · **Topic:** ss retransmits, packet/request path

What does `ss -ti` contribute, and what is its limitation?

**Q147** — **[L2]** **Format:** Short answer · **Topic:** interface drops, packet/request path

Why should `ip -s link` counters be collected as a time interval rather than a single absolute value?

**Q148** — **[L3]** **Format:** Packet capture · **Topic:** TCP handshake, scenario, packet/request path, defect-finding

What can a tcpdump capture showing SYN packets without visible SYN-ACKs suggest?

**Q149** — **[L3]** **Format:** Short answer · **Topic:** conntrack, packet/request path

What does `conntrack -S` require, and why is deliberate exhaustion unacceptable?

**Q150** — **[L3]** **Format:** Scenario · **Topic:** MTU, scenario, packet/request path

A small request works but a large payload stalls. Name likely hypotheses and the next discriminating tests.

**Q151** — **[L4]** **Format:** Short answer · **Topic:** traceroute, packet/request path

Explain why a traceroute/mtr intermediate-hop loss percentage can mislead.

**Q152** — **[L1]** **Format:** Scenario · **Topic:** DNS policy, scenario, packet/request path

A DNS lookup fails only in a Pod selected by egress default-deny. What is the investigation?

**Q153** — **[L2]** **Format:** Security review · **Topic:** diagnostic toolbox, packet/request path

What is the safest way to use a netshoot-style image?

**Q154** — **[L2]** **Format:** Short answer · **Topic:** kubectl debug, packet/request path

Why is `kubectl debug` not a guaranteed option?

**Q155** — **[L3]** **Format:** Short answer · **Topic:** HTTP status, packet/request path

Interpret 502, 503, 504 and 499 without overclaiming.

**Q156** — **[L3]** **Format:** Short answer · **Topic:** latency statistics

Why can a single request not establish p95 or p99 latency?

**Q157** — **[L4]** **Format:** Security review · **Topic:** pcap hygiene, packet/request path

What is the risk of packet capture artifacts and how should they be handled?

**Q158** — **[L1]** **Format:** Scenario · **Topic:** timeout ladder, scenario, packet/request path

How should a suspected timeout-ladder mismatch be investigated?

**Q159** — **[L1]** **Format:** Short answer · **Topic:** Hubble, packet/request path

What evidence does Hubble add if Cilium is installed?

**Q160** — **[L2]** **Format:** Scenario · **Topic:** debug restrictions, scenario, packet/request path

Why might a diagnostic Pod be blocked by Pod Security or NetworkPolicy?

**Q161** — **[L2]** **Format:** SRE design · **Topic:** runbook

What should a network incident runbook record beyond commands?

**Q162** — **[L2]** **Format:** Short answer · **Topic:** transport symptoms, packet/request path

Explain the difference between timeout, refusal and reset as symptoms.

**Q163** — **[L3]** **Format:** Practical · **Topic:** tc netem, packet/request path

How should `tc netem` be used in a training environment?

**Q164** — **[L3]** **Format:** Short answer · **Topic:** postmortem

What is the purpose of a postmortem's detection-gap section?

### Cross-unit architecture and capstone

**Q165** — **[L2]** **Format:** Architecture review · **Topic:** capstone path, scenario, packet/request path

Review the capstone request path for a public model-scoring API. What are the main trust boundaries to document?

**Q166** — **[L2]** **Format:** Scenario · **Topic:** internal dependencies, scenario, packet/request path

A capstone review finds Postgres and Redis exposed through external-facing Services. What is the concern and the safer direction?

**Q167** — **[L2]** **Format:** Practical · **Topic:** policy acceptance, packet/request path

What acceptance evidence should prove the model-api can call feature-service but an unauthorized namespace cannot?

**Q168** — **[L3]** **Format:** Design review · **Topic:** ETL egress, packet/request path

How would you review ETL external API egress without using public endpoints in this exercise?

**Q169** — **[L3]** **Format:** Scenario · **Topic:** canary, scenario, packet/request path

A canary has 90/10 configured routing but candidate errors are higher. What decision evidence is needed before promotion?

**Q170** — **[L3]** **Format:** Practical · **Topic:** streaming acceptance, packet/request path

How should gRPC or SSE acceptance differ from a short HTTP health check?

**Q171** — **[L4]** **Format:** Scenario · **Topic:** mTLS authorization, scenario, packet/request path

A mesh mTLS test succeeds, but the application still accepts unauthorized operations. Explain why this is possible.

**Q172** — **[L1]** **Format:** Design review · **Topic:** mesh choice

What should an architecture decision record say about Linkerd versus Istio for this roadmap?

**Q173** — **[L2]** **Format:** Scenario · **Topic:** Cilium fallback, scenario, packet/request path

A Cilium lab is not compatible with the learner's kernel. What is an acceptable completion path?

**Q174** — **[L2]** **Format:** SRE design · **Topic:** rollback

What should be in a capstone rollback plan for a TLS or policy change?

**Q175** — **[L3]** **Format:** Security review · **Topic:** secrets

How should the team prevent secret leakage in manifests, diagnostics and evidence artifacts?

**Q176** — **[L3]** **Format:** SRE design · **Topic:** SLO

Which metrics would you use for a network/API SLO and why?

**Q177** — **[L4]** **Format:** Short answer · **Topic:** evidence, packet/request path

What is the difference between configured state and observed state in the capstone?

**Q178** — **[L1]** **Format:** Architecture review · **Topic:** TLS boundaries, packet/request path

A production-like design uses ingress TLS plus mesh mTLS. What needs to be explicit about the two TLS legs?

**Q179** — **[L1]** **Format:** Source reasoning · **Topic:** source limits

How should a reviewer handle a feature that appears in the syllabus but its detailed lesson or capstone file is unavailable?

**Q180** — **[L2]** **Format:** Short answer · **Topic:** reproducibility

What evidence should accompany a claim that a lab is reproducible?

**Q181** — **[L2]** **Format:** Scenario · **Topic:** readiness vs SLO, scenario, packet/request path

A reviewer sees a passing readiness probe but the endpoint is slow. What is the right interpretation?

**Q182** — **[L2]** **Format:** Design review · **Topic:** negative tests, packet/request path

What should a capstone negative-test matrix include?

**Q183** — **[L3]** **Format:** SRE design · **Topic:** telemetry correlation, packet/request path

How should evidence from logs, metrics, traces and packet captures be correlated?

**Q184** — **[L3]** **Format:** Design review · **Topic:** resource budget

What is the minimum safe resource strategy for a laptop capstone?

## Answer Key and Explanations

Use these after attempting the corresponding questions. Answers are model answers, not the only acceptable wording. Any implementation-specific behavior must be checked against the learner's installed version. No sample output below is presented as captured evidence.

### Q001 — network model

**Model answer:** The baseline describes Pod-to-Pod communication without NAT, node-to-Pod communication without NAT, agent-to-Pod communication, and IP-based identity/reachability assumptions. It is a conceptual contract, not a guarantee of one implementation, route topology, security policy, or cloud behavior; validate the selected CNI and environment.

**Evidence/source concept:** Unit 1 — Kubernetes networking model, CNI and Pod networking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q002 — IP identity

**Model answer:** B. A node IP identifies a node interface/address. Pod IPs identify Pod network endpoints; a ClusterIP is a virtual Service address; a headless Service returns endpoint addresses through DNS rather than allocating a normal ClusterIP. Distractors confuse different scopes.

**Evidence/source concept:** Unit 1 — Kubernetes networking model, CNI and Pod networking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q003 — network namespaces

**Model answer:** Containers in a Pod normally share a network namespace and its interfaces/loopback address, so they can communicate through localhost if one listens on the relevant port. Different Pods have separate network namespaces and distinct Pod IPs; localhost always refers to the current network namespace.

**Evidence/source concept:** Unit 1 — Kubernetes networking model, CNI and Pod networking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q004 — cross-node path

**Model answer:** Resolve the destination Pod IP, inspect the source route and CNI configuration, identify whether the CNI uses overlay encapsulation or routed/native networking, then inspect node routes/interfaces and approved flow evidence. Cross-node traffic does not prove an overlay: some CNIs use native routing or cloud-native networking.

**Evidence/source concept:** Unit 1 — Kubernetes networking model, CNI and Pod networking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q005 — CNI implementation

**Model answer:** It hard-codes one implementation's topology. CNI implementations may use bridges, veth pairs, routes, overlays, eBPF datapaths or other mechanisms. The runbook should discover the installed CNI, inspect its documented interfaces and use implementation-aware evidence.

**Evidence/source concept:** Unit 1 — Kubernetes networking model, CNI and Pod networking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q006 — CNI versus Service datapath

**Model answer:** The CNI integrates container runtime networking setup, including Pod interfaces/addressing and network connectivity according to the plugin's design. kube-proxy historically implements Service virtual-IP forwarding on many clusters; some CNIs can replace that datapath. Exact division depends on deployment configuration.

**Evidence/source concept:** Unit 1 — Kubernetes networking model, CNI and Pod networking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q007 — CNI selection

**Model answer:** Select A, B, C and D. A sound decision record weighs policy capabilities, visibility, encryption, performance, ecosystem, operations, compatibility and migration risk. Vendor identity alone is not a decision criterion.

**Evidence/source concept:** Unit 1 — Kubernetes networking model, CNI and Pod networking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q008 — CNI failure

**Model answer:** Check Pod events and node assignment; verify node readiness and runtime/CNI health; inspect the installed CNI DaemonSet/agent and logs; confirm CNI config/binaries and IPAM capacity using the implementation's supported diagnostics. Avoid deleting many Pods or restarting nodes before preserving evidence.

**Evidence/source concept:** Unit 1 — Kubernetes networking model, CNI and Pod networking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q009 — MTU and PMTUD

**Model answer:** Encapsulation adds headers, reducing the inner packet size that fits the underlay MTU. If effective MTU/PMTUD is mishandled, small packets may work while larger packets stall. Verify the actual tunnel, MTUs and packet path rather than applying a universal MTU number.

**Evidence/source concept:** Unit 1 — Kubernetes networking model, CNI and Pod networking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q010 — network architecture

**Model answer:** An overlay encapsulates traffic between nodes; routed networking relies on routes for Pod CIDRs; cloud-native networking integrates with provider networking/address allocation. Trade-offs include encapsulation overhead, route scale, IP consumption, operational complexity and provider coupling; implementations vary.

**Evidence/source concept:** Unit 1 — Kubernetes networking model, CNI and Pod networking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q011 — IPAM/CIDR

**Model answer:** Inventory current Pod/node/service CIDRs, per-node Pod capacity, IPAM allocation, route advertisements, overlap with VPC/VPN/on-prem ranges, dual-stack requirements, migration compatibility and rollback. CIDR changes are architectural migrations, not a quick local tweak.

**Evidence/source concept:** Unit 1 — Kubernetes networking model, CNI and Pod networking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q012 — hostNetwork

**Model answer:** False. It changes namespace/isolation and port behavior, can increase exposure and conceal the actual CNI defect. Use only for a justified workload with reviewed security and scheduling implications; diagnose the normal Pod path first.

**Evidence/source concept:** Unit 1 — Kubernetes networking model, CNI and Pod networking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q013 — address identity

**Model answer:** Correlate Pod status/Pod IP, Node status/internal/external addresses, and Service spec/ClusterIP with the source/destination tuple seen by the relevant observation point. A Service IP may be virtual and translated in the datapath; a capture point may see a different tuple after NAT.

**Evidence/source concept:** Unit 1 — Kubernetes networking model, CNI and Pod networking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q014 — CNI migration

**Model answer:** Risks include CIDR overlap, IPAM disruption, datapath/policy semantic changes, kernel incompatibility, route/MTU changes, observability gaps and rollback complexity. Test on a disposable environment, inventory dependencies, stage by node/cluster, define success and rollback criteria, and preserve access to recovery tooling.

**Evidence/source concept:** Unit 1 — Kubernetes networking model, CNI and Pod networking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q015 — ADR

**Model answer:** Context/constraints, requirements, alternatives, policy/security needs, performance and observability method, kernel/runtime/Kubernetes compatibility checks, IP/CIDR plan, operations/upgrade skills, resource cost, migration plan, failure modes, rollback and measurable acceptance criteria.

**Evidence/source concept:** Unit 1 — Kubernetes networking model, CNI and Pod networking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q016 — veth and routes

**Model answer:** It can support a hypothesis that a veth pair participates in the visible path, if interfaces and namespaces are correctly identified. It does not alone prove the full CNI architecture, Service routing path, cross-node transport, or root cause. Correlate with CNI documentation, routes and packet/flow evidence.

**Evidence/source concept:** Unit 1 — Kubernetes networking model, CNI and Pod networking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q017 — Service types

**Model answer:** ClusterIP provides an internal virtual IP; NodePort exposes a port on nodes; LoadBalancer requests integration with a load-balancing implementation; ExternalName maps DNS to an external name; headless Service omits the normal ClusterIP and exposes endpoint DNS records. Actual external behavior depends on provider/controller support.

**Evidence/source concept:** Unit 2 — Services, kube-proxy and cluster DNS lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q018 — port mapping

**Model answer:** Clients address Service port 80; the selected backend is expected to accept traffic on target port 8081. Verify the resolved endpoint port and actual listener; named targetPorts must resolve to a valid named container port when used.

**Evidence/source concept:** Unit 2 — Services, kube-proxy and cluster DNS lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q019 — EndpointSlice

**Model answer:** EndpointSlices represent endpoint addresses and associated port/condition data for a Service. The Service can exist with no selected or ready backends, so inspect EndpointSlices, Pod labels and readiness as well as the Service spec.

**Evidence/source concept:** Unit 2 — Services, kube-proxy and cluster DNS lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q020 — Service diagnosis

**Model answer:** Verify context/namespace/name/port; inspect Service selector and targetPort; inspect EndpointSlices and endpoint readiness; verify the process listener. Then investigate DNS from the source Pod, policy, Service datapath, routing/MTU and application evidence. DNS success is not backend reachability proof.

**Evidence/source concept:** Unit 2 — Services, kube-proxy and cluster DNS lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q021 — kube-proxy

**Model answer:** kube-proxy implements Service forwarding on many clusters, but modes and implementations vary; some CNIs replace the Service datapath. Inspect the actual deployment and version rather than assuming iptables, IPVS or kube-proxy is present.

**Evidence/source concept:** Unit 2 — Services, kube-proxy and cluster DNS lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q022 — CoreDNS

**Model answer:** CoreDNS serves cluster DNS records and commonly forwards queries it cannot answer according to its configuration. Check exact query/result, Pod resolver config, CoreDNS health/logs, Service/EndpointSlices, upstream behavior and DNS policy. A DNS symptom alone does not establish CoreDNS as root cause.

**Evidence/source concept:** Unit 2 — Services, kube-proxy and cluster DNS lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q023 — ndots

**Model answer:** Resolver search behavior may try candidate names using configured suffixes before or alongside an absolute query, and retries can multiply requests. The exact sequence depends on resolver library, name shape, caching and client behavior; observe actual queries instead of assuming a fixed count.

**Evidence/source concept:** Unit 2 — Services, kube-proxy and cluster DNS lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q024 — FQDN

**Model answer:** A trailing dot conventionally marks a DNS name as absolute, avoiding resolver search-suffix expansion for that name. Validate how the actual client library accepts and uses it; do not change cluster-wide resolver settings without evidence.

**Evidence/source concept:** Unit 2 — Services, kube-proxy and cluster DNS lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q025 — resolver mismatch

**Model answer:** The application may use a different resolver library, cache, custom DNS client, sidecar or query name. Test the exact name from the same workload and correlate DNS logs/metrics and application errors; one tool's success is limited evidence.

**Evidence/source concept:** Unit 2 — Services, kube-proxy and cluster DNS lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q026 — NodeLocal DNSCache

**Model answer:** It can provide a node-local caching DNS path that reduces latency and load on central DNS in supported setups. Verify it is installed, its configuration, the Pod resolver path, metrics and behavior for the cluster's version; it is not universally present.

**Evidence/source concept:** Unit 2 — Services, kube-proxy and cluster DNS lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q027 — DNS policy

**Model answer:** DNS may use TCP for larger responses, truncation fallback or other resolver/server behavior. A policy that permits only UDP/53 can fail for queries that require TCP. Validate the actual DNS path and allow only the necessary resolver destinations/transports.

**Evidence/source concept:** Unit 2 — Services, kube-proxy and cluster DNS lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q028 — LoadBalancer pending

**Model answer:** It usually means no configured controller/provider has provisioned an external address yet, or provisioning is delayed/failed. Inspect events, controller/provider integration and environment support. In kind, a LoadBalancer implementation/helper may be required; the Service type alone does not create cloud infrastructure.

**Evidence/source concept:** Unit 2 — Services, kube-proxy and cluster DNS lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q029 — headless Service

**Model answer:** A headless Service exposes endpoint-oriented DNS records instead of a normal virtual ClusterIP. Clients may see individual endpoint addresses and must account for endpoint churn, readiness and their own balancing/caching behavior.

**Evidence/source concept:** Unit 2 — Services, kube-proxy and cluster DNS lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q030 — rollout endpoints

**Model answer:** Endpoint state changes propagate asynchronously, while existing TCP connections can remain open and app shutdown/draining behavior may differ from new endpoint selection. Observe readiness, termination, proxy behavior and active connections; removing an endpoint is not identical to instantly terminating every existing connection.

**Evidence/source concept:** Unit 2 — Services, kube-proxy and cluster DNS lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q031 — conntrack

**Model answer:** Correlate new-connection failures with authorized node/platform metrics and available counters such as `conntrack -S` where supported. Verify kernel/tool availability `[VERIFY]`; do not flush conntrack or tune sysctls without evidence and a reviewed change plan.

**Evidence/source concept:** Unit 2 — Services, kube-proxy and cluster DNS lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q032 — DNS SLO

**Model answer:** Define success as a correct expected DNS response for the exact in-cluster name, with latency/error thresholds and a measurement window. Run a bounded probe from a representative namespace/resolver path, track failures/latency, avoid high query volume and pair it with app-level reachability checks.

**Evidence/source concept:** Unit 2 — Services, kube-proxy and cluster DNS lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q033 — selectorless Service

**Model answer:** They can represent endpoints not selected by Pod labels, but operators must manage correctness, reachability, lifecycle and security themselves. Validate ownership, endpoint ports/conditions and whether external destinations are appropriate; never treat manual endpoints as automatic service discovery.

**Evidence/source concept:** Unit 2 — Services, kube-proxy and cluster DNS lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q034 — DNS errors

**Model answer:** SERVFAIL indicates the queried DNS server could not successfully complete the query. It does not uniquely prove CoreDNS itself is broken; inspect upstream forwarding, DNSSEC/resolver issues where relevant, logs, policy and the exact queried name.

**Evidence/source concept:** Unit 2 — Services, kube-proxy and cluster DNS lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q035 — Ingress object/controller

**Model answer:** The Ingress object declares desired HTTP routing; a controller watches it and configures an implementation/data plane. Creating the object alone does not ensure traffic is served. Check controller presence, class, events and status.

**Evidence/source concept:** Unit 3 — Ingress controllers and Gateway API lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q036 — traffic direction

**Model answer:** North–south generally means client/external-to-cluster traffic; east–west means service-to-service traffic. L4 routes by transport endpoints/protocol, while L7 can use HTTP attributes such as host/path/headers. Actual boundaries depend on architecture.

**Evidence/source concept:** Unit 3 — Ingress controllers and Gateway API lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q037 — IngressClass

**Model answer:** It associates an Ingress with a controller class where that controller uses it. A resource can exist but be ignored or not programmed by the intended controller. Verify the installed controller's class configuration and status/events; behavior is implementation-specific.

**Evidence/source concept:** Unit 3 — Ingress controllers and Gateway API lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q038 — desired vs observed

**Model answer:** Apply success means the API accepted the object, not that a controller reconciled it or that the data path works. Check class, controller logs/status/events, backend Service/EndpointSlices, DNS, TLS and a controlled end-to-end request.

**Evidence/source concept:** Unit 3 — Ingress controllers and Gateway API lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q039 — Gateway API

**Model answer:** GatewayClass describes a class of Gateway implementation; Gateway represents an instantiated traffic-handling point/listeners; HTTPRoute describes HTTP routing rules and attachment to a parent Gateway. Exact API versions, fields and controller support are `[VERIFY]` against installed CRDs/docs.

**Evidence/source concept:** Unit 3 — Ingress controllers and Gateway API lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q040 — ReferenceGrant

**Model answer:** It governs certain cross-namespace references in Gateway API so a target namespace can explicitly allow a reference from another namespace. Validate the exact resource types and API version against the installed Gateway API specification/controller; do not assume cross-namespace references are implicitly allowed.

**Evidence/source concept:** Unit 3 — Ingress controllers and Gateway API lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q041 — HTTPRoute status

**Model answer:** Confirm Gateway API CRDs and controller exist; inspect route parentRefs, listener/hostname compatibility, status conditions/events, backend references and controller logs. Status details vary by API/controller version; use installed docs and treat absent CRDs as an environment limitation.

**Evidence/source concept:** Unit 3 — Ingress controllers and Gateway API lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q042 — Ingress vs Gateway API

**Model answer:** Ingress is a simpler established HTTP routing API with behavior often extended through controller-specific annotations; Gateway API models roles/listeners/routes and richer portable intent in supported implementations. Compare controller conformance, maturity, multi-tenancy, migration, feature coverage, security and operations for the selected environment.

**Evidence/source concept:** Unit 3 — Ingress controllers and Gateway API lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q043 — annotations

**Model answer:** They may have implementation-specific semantics, version changes or unsafe defaults and can make migrations difficult. Inventory annotations, consult the selected controller's maintained documentation and security advisories, test behavior and replace only after validating equivalent semantics.

**Evidence/source concept:** Unit 3 — Ingress controllers and Gateway API lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q044 — HTTP status

**Model answer:** Identify the responding hop using headers cautiously, access/error logs, request/trace IDs and timing; inspect backend endpoints, protocol and upstream connection state. These codes are not unique root-cause labels and can be generated by different proxies/apps.

**Evidence/source concept:** Unit 3 — Ingress controllers and Gateway API lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q045 — streaming

**Model answer:** Verify protocol support/translation, idle and total timeouts, buffering, connection draining, keep-alives, retry semantics and maximum duration. A short ordinary HTTP request does not validate streaming behavior; test with the chosen controller and client versions.

**Evidence/source concept:** Unit 3 — Ingress controllers and Gateway API lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q046 — weighted routing

**Model answer:** Route a controlled, non-sensitive sample to stable/candidate backends, tag each version, send a documented number of requests and count observed versions with confidence/noise caveats. Weights are routing configuration; persistence, balancing algorithms, connection reuse and small sample sizes can alter observed counts.

**Evidence/source concept:** Unit 3 — Ingress controllers and Gateway API lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q047 — route debugging

**Model answer:** Inspect resource status and events first, then controller logs and referenced Gateway/listener/Service/endpoints. Identify the exact rejected field/reference and compare against installed CRD schema and controller docs; do not guess a status condition or apply fields unsupported by the cluster.

**Evidence/source concept:** Unit 3 — Ingress controllers and Gateway API lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q048 — controller selection

**Model answer:** Maintenance/security status, supported Kubernetes/API versions, conformance, required features, performance method, observability, upgrade/rollback, security history, licensing/governance, community/vendor support and operator skill. Verify current maintenance status from authoritative project sources.

**Evidence/source concept:** Unit 3 — Ingress controllers and Gateway API lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q049 — client IP

**Model answer:** NAT, load balancers, proxies and `externalTrafficPolicy` can change the source address visible at a hop. `X-Forwarded-For` and PROXY protocol require trusted-proxy configuration; never trust arbitrary client-supplied forwarding headers.

**Evidence/source concept:** Unit 3 — Ingress controllers and Gateway API lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q050 — multi-tenancy

**Model answer:** Prevent unauthorized route attachment, cross-namespace backend references, host/path collisions, untrusted TLS secret use and shared-controller policy leakage. Use namespace boundaries, explicit attachment/reference controls and controller-supported policy; verify API semantics and tenant isolation with tests.

**Evidence/source concept:** Unit 3 — Ingress controllers and Gateway API lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q051 — HA/PDB

**Model answer:** A controller rollout or node drain can reduce serving capacity or interrupt reconciliation/data-plane availability. Verify replica count, topology, PDB, readiness and implementation architecture; a PDB alone does not guarantee end-to-end availability.

**Evidence/source concept:** Unit 3 — Ingress controllers and Gateway API lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q052 — migration

**Model answer:** Inventory current routes/annotations and semantics; verify Gateway API CRDs/controller conformance; build equivalent routes in parallel on a local/test path; test TLS, errors, headers, timeouts and canary behavior; compare telemetry; shift traffic gradually with rollback. Do not assume a conversion tool preserves all behavior.

**Evidence/source concept:** Unit 3 — Ingress controllers and Gateway API lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q053 — LoadBalancer

**Model answer:** kind does not automatically reproduce every cloud provider's load-balancer controller. A local helper/provider may be needed. Inspect events and installed integration; do not infer a broken Kubernetes Service solely from a pending external address.

**Evidence/source concept:** Unit 4 — Load balancers and external traffic management lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q054 — L4/L7

**Model answer:** L4 distributes transport connections/flows without needing HTTP semantics; L7 can route based on HTTP host/path/header and often terminates TLS. L7 offers richer routing but adds protocol and proxy considerations; exact features depend on implementation.

**Evidence/source concept:** Unit 4 — Load balancers and external traffic management lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q055 — externalTrafficPolicy

**Model answer:** Cluster can route to endpoints across nodes and may obscure original source IP depending on path; Local generally limits forwarding to local endpoints and can preserve source IP in supported paths, but may cause uneven traffic or health-check constraints. Verify provider/CNI behavior and exact semantics.

**Evidence/source concept:** Unit 4 — Load balancers and external traffic management lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q056 — node path

**Model answer:** Inspect node readiness, endpoints local to each node, service traffic policy, health checks, node/firewall/port mappings and provider load-balancer status. Compare the actual path and source IP; kind and cloud providers differ substantially.

**Evidence/source concept:** Unit 4 — Load balancers and external traffic management lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q057 — health checks

**Model answer:** An assigned address only indicates provisioning state, not healthy backends, correct routes, firewall access, TLS or application success. Verify health-check status, controller events, endpoint readiness and a controlled request from the intended client network.

**Evidence/source concept:** Unit 4 — Load balancers and external traffic management lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q058 — draining

**Model answer:** Draining lets existing connections finish or close in a controlled way while new traffic stops going to a backend. Readiness removal, load-balancer health checks, proxy draining and application shutdown must be coordinated; otherwise long-lived requests may reset or time out.

**Evidence/source concept:** Unit 4 — Load balancers and external traffic management lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q059 — timeout ladder

**Model answer:** The outer client/LB deadline and inner proxy/app/dependency deadlines need coherent semantics and enough budget for retries. Record whether each is connect, idle, per-try or total timeout; inconsistent values can produce 499/504 symptoms and orphaned work.

**Evidence/source concept:** Unit 4 — Load balancers and external traffic management lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q060 — egress NAT

**Model answer:** Many short-lived outbound connections can consume NAT/conntrack state and ephemeral ports; failures may be destination-specific or intermittent. Correlate connection counts, reuse patterns, errors and supported platform counters. Avoid arbitrary kernel tuning or deliberate exhaustion.

**Evidence/source concept:** Unit 4 — Load balancers and external traffic management lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q061 — kind fidelity

**Model answer:** A local helper can validate a bounded local path but does not reproduce provider health checks, topology, routing, multi-zone failover, quotas or managed control-plane behavior. State the fidelity limit and use provider-specific staging evidence for cloud acceptance.

**Evidence/source concept:** Unit 4 — Load balancers and external traffic management lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q062 — health checks

**Model answer:** TCP checks whether a connection can be established to a port; HTTP checks can validate an application-level response at a path/status. Neither automatically proves full business functionality. Select a check matching the failure mode and avoid coupling it to every dependency.

**Evidence/source concept:** Unit 4 — Load balancers and external traffic management lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q063 — TLS boundary

**Model answer:** Passthrough forwards encrypted TLS to a backend that terminates it; termination decrypts at the proxy; re-encryption terminates one TLS session and establishes another to the backend. Each changes visibility, certificate ownership and trust boundaries.

**Evidence/source concept:** Unit 4 — Load balancers and external traffic management lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q064 — global traffic

**Model answer:** Teach the concepts—health-based steering, failover, DNS TTL and regional blast radius—using diagrams and simulations. Do not imply a local kind cluster validates real global routing or multi-region failover; no paid/public infrastructure is required for conceptual assessment.

**Evidence/source concept:** Unit 4 — Load balancers and external traffic management lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q065 — algorithms

**Model answer:** Define traffic distribution, connection duration, request cost, locality, latency/error SLOs and workload mix; measure representative traffic and tail latency. Algorithm labels alone are insufficient because persistent connections and uneven request costs can skew observed load.

**Evidence/source concept:** Unit 4 — Load balancers and external traffic management lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q066 — forwarded headers

**Model answer:** Forwarding headers are client-controlled unless a trusted proxy boundary sanitizes and appends them. Configure trusted proxy ranges/protocol, strip untrusted incoming headers as appropriate, and never use untrusted client-supplied IP metadata as an authentication factor.

**Evidence/source concept:** Unit 4 — Load balancers and external traffic management lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q067 — policy boundary

**Model answer:** It describes selected Pod ingress/egress L3/L4 traffic policy when the CNI enforces it. It does not inherently authenticate workload identity, provide universal L7 HTTP policy or guarantee enforcement in every network implementation.

**Evidence/source concept:** Unit 5 — Network policies and zero-trust segmentation lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q068 — additive policy

**Model answer:** For an isolated direction, traffic allowed by any applicable policy rule is permitted; rules are additive rather than ordered deny/allow ACLs. The exact Pod isolation is based on policy selectors and ingress/egress policy types. Check both source and destination policy context.

**Evidence/source concept:** Unit 5 — Network policies and zero-trust segmentation lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q069 — selector mismatch

**Model answer:** The selector matches no intended Pods because label keys differ. Inspect live labels and the policy selector, then correct one side in a disposable test and verify both allowed and denied flows. Do not infer enforcement solely from YAML.

**Evidence/source concept:** Unit 5 — Network policies and zero-trust segmentation lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q070 — DNS egress

**Model answer:** A workload may need to reach cluster DNS before it can resolve its dependencies; denying UDP/TCP 53 to the actual DNS endpoints breaks name resolution. Discover DNS labels/namespaces and verify the CNI implementation, then add the narrow rule needed.

**Evidence/source concept:** Unit 5 — Network policies and zero-trust segmentation lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q071 — CNI enforcement

**Model answer:** Confirm the installed CNI supports and enforces Kubernetes NetworkPolicy and that the policy was selected/applied to the target Pods. A policy object accepted by the API does not prove the datapath enforces it.

**Evidence/source concept:** Unit 5 — Network policies and zero-trust segmentation lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q072 — least privilege

**Model answer:** Identify exact namespaces/labels/ports and required direction. Apply narrow ingress rules at destinations and egress rules at sources where needed, include DNS to the real resolver, and verify allowed paths plus denied unrelated paths. Keep database access internal and avoid broad namespace-wide exceptions.

**Evidence/source concept:** Unit 5 — Network policies and zero-trust segmentation lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q073 — namespace selector

**Model answer:** Namespace selectors may match every Pod in that namespace, including jobs or workloads with different trust levels. Combine namespace and Pod selectors when supported by the intended rule, label namespaces deliberately, and review label governance and policy blast radius.

**Evidence/source concept:** Unit 5 — Network policies and zero-trust segmentation lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q074 — egress control

**Model answer:** Prefer explicit destination/port constraints where stable and feasible, use CNI-specific FQDN controls only after verifying support, and consider an egress gateway/proxy for centralized policy. Vanilla Kubernetes NetworkPolicy does not provide portable FQDN policy; avoid opening all egress as a shortcut.

**Evidence/source concept:** Unit 5 — Network policies and zero-trust segmentation lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q075 — SSRF

**Model answer:** Egress segmentation can reduce reachable destinations and help limit SSRF impact, but it is not a complete application-level SSRF defense or identity system. Validate URLs/redirects, restrict destinations, protect metadata paths and use least privilege at multiple layers.

**Evidence/source concept:** Unit 5 — Network policies and zero-trust segmentation lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q076 — policy rollout

**Model answer:** Inventory expected flows, collect available flow/log evidence, draft least-privilege policy, test positive and negative cases in a lab, stage to a small workload set, monitor drops/errors, and define rollback. Do not globally default-deny without dependency mapping and owner sign-off.

**Evidence/source concept:** Unit 5 — Network policies and zero-trust segmentation lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q077 — desired vs observed

**Model answer:** The object is desired API configuration; enforcement depends on the CNI/controller/datapath and successful reconciliation. Verify implementation status/logs and actual allowed/denied tests. A successful `kubectl apply` is not proof of blocking.

**Evidence/source concept:** Unit 5 — Network policies and zero-trust segmentation lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q078 — policy and mesh

**Model answer:** NetworkPolicy narrows network reachability at L3/L4; mesh authorization may enforce authenticated identity and application-level conditions depending on the selected mesh. Both must be configured and tested; neither should be assumed to replace the other.

**Evidence/source concept:** Unit 5 — Network policies and zero-trust segmentation lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q079 — safe operations

**Model answer:** It broadens lateral movement and egress, may conceal the real selector/DNS issue, and changes the environment under investigation. Instead inspect applicable policies and enforcement, run a narrow controlled test, and apply a time-bounded minimal change with approval/rollback.

**Evidence/source concept:** Unit 5 — Network policies and zero-trust segmentation lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q080 — policy testing

**Model answer:** Positive tests for approved ingress→model-api, model-api→feature-service/database and required DNS; negative tests for unauthorized namespaces, unexpected ports and forbidden egress. Include policy-enforcement prerequisite, labels, rollout behavior and failure evidence.

**Evidence/source concept:** Unit 5 — Network policies and zero-trust segmentation lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q081 — L7/FQDN policy

**Model answer:** The portable Kubernetes NetworkPolicy API primarily expresses Pod/namespace and IP/port based L3/L4 controls; it does not provide general HTTP path or FQDN matching. CNI extensions may add features, but syntax/semantics are implementation-specific `[VERIFY]`.

**Evidence/source concept:** Unit 5 — Network policies and zero-trust segmentation lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q082 — policy diagnosis

**Model answer:** Compare live labels and policy selectors, confirm which Pod is isolated, inspect DNS endpoint labels/namespace and policy ports, then test exact query from selected and unselected Pods. Confirm CNI enforcement. This separates rule selection from an omitted DNS exception.

**Evidence/source concept:** Unit 5 — Network policies and zero-trust segmentation lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q083 — certificate meaning

**Model answer:** When correctly validated, it binds a public key to identities in the certificate under a trust chain and validity constraints. It does not automatically authorize the user/workload, guarantee the app is safe, or prove that the caller is permitted to access an operation.

**Evidence/source concept:** Unit 6 — TLS termination and certificate lifecycle lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q084 — SAN

**Model answer:** The client verifies that the requested hostname matches the certificate's Subject Alternative Name under its validation rules and that the chain/time/trust are valid. Do not rely on a Common Name-only assumption; use current TLS client behavior and documentation.

**Evidence/source concept:** Unit 6 — TLS termination and certificate lifecycle lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q085 — SNI

**Model answer:** SNI communicates the intended server name during TLS negotiation so a server can select a certificate/route. Connecting by IP or omitting the expected hostname can select a default certificate; test with the intended hostname/SNI and preserve hostname verification.

**Evidence/source concept:** Unit 6 — TLS termination and certificate lifecycle lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q086 — termination modes

**Model answer:** Passthrough preserves TLS to the backend; termination decrypts at ingress; re-encryption creates a new TLS connection to the backend. Document which hop holds keys, where identity is authenticated, which traffic is visible and what trust/certificate chain each leg uses.

**Evidence/source concept:** Unit 6 — TLS termination and certificate lifecycle lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q087 — TLS validation

**Model answer:** `-k` disables normal certificate verification, so success can hide expired, mismatched or untrusted certificates. Test with correct hostname/SNI and trusted CA; fix the chain/name/expiry rather than making insecure bypass a production control.

**Evidence/source concept:** Unit 6 — TLS termination and certificate lifecycle lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q088 — cert-manager

**Model answer:** Certificate resources express desired certificate state; cert-manager controllers reconcile them through an Issuer/ClusterIssuer and related request/order/challenge resources as applicable, then publish certificate/key material in a Secret. Exact resource flow and API versions should be checked against the installed cert-manager version.

**Evidence/source concept:** Unit 6 — TLS termination and certificate lifecycle lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q089 — local CA

**Model answer:** Use a local-only test endpoint and a lab CA/self-signed certificate, store keys with restrictive permissions, create only lab-scoped Kubernetes Secrets, verify the chain and hostname, and clean up keys/secrets. Do not use public ACME accounts, real domains or production credentials.

**Evidence/source concept:** Unit 6 — TLS termination and certificate lifecycle lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q090 — renewal diagnosis

**Model answer:** Inspect Certificate/Issuer status and events, related CertificateRequest/order/challenge resources if applicable, controller logs, Secret state, issuer readiness, DNS/HTTP challenge prerequisites if used, permissions and version-specific docs. Preserve evidence and avoid deleting resources as the first step.

**Evidence/source concept:** Unit 6 — TLS termination and certificate lifecycle lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q091 — private keys

**Model answer:** Use least-privilege RBAC, limit which workloads/controllers can read the Secret, protect etcd with appropriate encryption/access controls, avoid printing key contents, restrict backups and rotate compromised keys. A Kubernetes Secret is not automatically a complete secret-management solution.

**Evidence/source concept:** Unit 6 — TLS termination and certificate lifecycle lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q092 — certificate chain

**Model answer:** The client builds a trust path from the served leaf through intermediate certificates to a trusted root according to validation rules. Omitting a needed intermediate can cause some clients to fail even when others have cached it; inspect the served chain and test with the intended trust store.

**Evidence/source concept:** Unit 6 — TLS termination and certificate lifecycle lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q093 — client divergence

**Model answer:** Compare client trust stores, hostname/SNI, system time, certificate chain, TLS versions/ciphers/ALPN, proxy path and DNS destination. Capture exact verification errors; do not immediately weaken TLS or assume one client is authoritative.

**Evidence/source concept:** Unit 6 — TLS termination and certificate lifecycle lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q094 — expiry monitoring

**Model answer:** Monitor certificate identity/hostname, remaining lifetime, renewal status, issuer readiness and served certificate on the actual endpoint, including whether rotation propagated. Alert early enough for remediation and test renewal paths; a valid Secret does not prove ingress serves it.

**Evidence/source concept:** Unit 6 — TLS termination and certificate lifecycle lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q095 — security properties

**Model answer:** Encryption protects confidentiality in transit; authentication establishes peer identity; authorization decides whether that identity may perform an action. mTLS can authenticate both TLS peers, but authorization still requires policy and correct identity mapping.

**Evidence/source concept:** Unit 6 — TLS termination and certificate lifecycle lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q096 — ALPN

**Model answer:** ALPN negotiates an application protocol such as HTTP/2 during TLS. A connection can complete TLS yet fail at the application protocol layer if client/proxy/backend expectations differ. Inspect negotiated protocol and implementation-specific logs.

**Evidence/source concept:** Unit 6 — TLS termination and certificate lifecycle lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q097 — backend encryption

**Model answer:** TLS termination at ingress may leave backend traffic unencrypted unless re-encryption or mesh TLS is configured. Document each trust boundary, certificate validation and identity/authorization behavior; do not assume client-side HTTPS encrypts every internal hop.

**Evidence/source concept:** Unit 6 — TLS termination and certificate lifecycle lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q098 — TLS acceptance

**Model answer:** Record exact local hostname/SNI, trusted CA, certificate SAN/expiry/chain, negotiated protocol, expected HTTP result and negative test for an invalid hostname/untrusted CA. Protect private key material and delete temporary files/secrets after the test.

**Evidence/source concept:** Unit 6 — TLS termination and certificate lifecycle lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q099 — control/data plane

**Model answer:** The control plane configures/distributes policy and proxy state; the data plane handles workload traffic through proxies or an implementation-specific datapath. Control-plane outage effects depend on cached configuration and design; do not assume all traffic instantly stops or that every feature continues unchanged.

**Evidence/source concept:** Unit 7 — Service mesh fundamentals: Istio and Linkerd lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q100 — sidecar

**Model answer:** A proxy is added to the workload Pod and handles configured inbound/outbound traffic, creating additional hops, resources, startup/health interactions and debugging points. Verify injection and actual interception rather than assuming a namespace label means every Pod is meshed.

**Evidence/source concept:** Unit 7 — Service mesh fundamentals: Istio and Linkerd lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q101 — mesh comparison

**Model answer:** Compare capabilities required, installation/upgrade complexity, ecosystem, policy/routing needs, observability, compatibility and resource footprint measured under the same workload. Do not assert universal resource numbers; measure N runs, median/p95 and CPU/memory on the learner's machine.

**Evidence/source concept:** Unit 7 — Service mesh fundamentals: Istio and Linkerd lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q102 — selected mesh

**Model answer:** The available Unit 7 lesson explicitly selects Linkerd sidecar mode for the hands-on path; Istio is comparison/awareness unless the authoritative source is intentionally revised. Keep Unit 8 assumptions consistent and verify the selected release/install compatibility before a lab.

**Evidence/source concept:** Unit 7 — Service mesh fundamentals: Istio and Linkerd lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q103 — injection

**Model answer:** Check namespace/Pod labels and annotations, injection webhook/control-plane health, Pod creation time, admission events, image/init-container state and the mesh's supported status command. Exact commands are release-sensitive; consult the selected Linkerd release docs rather than assuming injection succeeded.

**Evidence/source concept:** Unit 7 — Service mesh fundamentals: Istio and Linkerd lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q104 — mesh/policy

**Model answer:** NetworkPolicy may block traffic to/from proxies or control plane; policy must account for ports/identities as implemented; mesh policy can deny authenticated requests even when network traffic is allowed; and a mesh does not replace CNI enforcement. Verify the actual proxy path and CNI semantics.

**Evidence/source concept:** Unit 7 — Service mesh fundamentals: Istio and Linkerd lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q105 — upgrade

**Model answer:** Compatibility matrix for Kubernetes/kernel/CRDs, staged control-plane/proxy rollout, backups of relevant configuration, canary namespace/workload, health and latency measurements, rollback plan, policy compatibility, and a clear success/abort gate. Avoid upgrading every component simultaneously on a constrained lab.

**Evidence/source concept:** Unit 7 — Service mesh fundamentals: Istio and Linkerd lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q106 — mesh boundaries

**Model answer:** Mesh coverage is limited by enrollment/interception/configuration and architecture; host traffic and some external paths may bypass it. Map the actual request path, verify enrollment and egress policy, and retain network-level controls where required.

**Evidence/source concept:** Unit 7 — Service mesh fundamentals: Istio and Linkerd lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q107 — mesh evidence

**Model answer:** Inspect the live Pod spec for proxy/init or relevant data-plane artifacts, use version-matched mesh status/identity tools, and send a controlled request with proxy telemetry. Namespace labels alone show intent, not successful injection or traffic interception.

**Evidence/source concept:** Unit 7 — Service mesh fundamentals: Istio and Linkerd lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q108 — sidecar operations

**Model answer:** Proxy startup/termination may affect Job completion; probes may be intercepted or depend on app startup order; sidecars consume CPU/memory and can alter tail latency. Test these cases and configure lifecycle/probe integration according to selected mesh docs.

**Evidence/source concept:** Unit 7 — Service mesh fundamentals: Istio and Linkerd lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q109 — mesh limitations

**Model answer:** It does not guarantee application correctness, secure all host/external traffic, prevent every lateral path, replace NetworkPolicy, validate business authorization or make retries safe. It adds capabilities and complexity that need explicit coverage and testing.

**Evidence/source concept:** Unit 7 — Service mesh fundamentals: Istio and Linkerd lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q110 — measurement

**Model answer:** Define representative request shape, concurrency and warm-up; measure baseline and meshed runs over repeated samples; compare median/p95/p99, CPU/memory and error rates while recording noise and versions. Do not claim causality from one run or compare unlike workloads.

**Evidence/source concept:** Unit 7 — Service mesh fundamentals: Istio and Linkerd lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q111 — control-plane failure

**Model answer:** Determine which functions are affected and whether existing data-plane proxies retain usable configuration; inspect control-plane health and proxy sync/status using the selected mesh's docs. Do not infer immediate traffic outage without evidence; behavior varies by mesh/version and feature.

**Evidence/source concept:** Unit 7 — Service mesh fundamentals: Istio and Linkerd lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q112 — mesh security

**Model answer:** Installation alone does not prove workload enrollment, identity issuance, peer policy, authorization rules or expected path coverage. Verify actual identity/policy status and both allowed and denied requests, and distinguish encryption from authorization.

**Evidence/source concept:** Unit 7 — Service mesh fundamentals: Istio and Linkerd lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q113 — mTLS

**Model answer:** TLS authenticates the server to the client in the usual server-authenticated configuration; mTLS also authenticates the client using its certificate/identity. Neither alone determines whether the identity is authorized to call an operation.

**Evidence/source concept:** Unit 8 — mTLS, traffic shifting, retries and circuit breaking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q114 — strict/permissive

**Model answer:** Strict mode requires the expected mutual-authenticated traffic under the selected mesh policy; permissive modes may accept more than one mode during migration. Exact policy resources and semantics differ between Linkerd/Istio and releases, so verify the selected implementation docs.

**Evidence/source concept:** Unit 8 — mTLS, traffic shifting, retries and circuit breaking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q115 — mTLS mismatch

**Model answer:** Confirm workload enrollment and identity, inspect peer policy and proxy logs/status, compare a known-meshed client with the plaintext client, and capture only authorized lab metadata if needed. Fix the intended identity/enrollment/policy; do not disable strict mode globally as a shortcut.

**Evidence/source concept:** Unit 8 — mTLS, traffic shifting, retries and circuit breaking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q116 — security properties

**Model answer:** Encryption protects data in transit; authentication binds a connection to a peer identity; authorization evaluates whether that identity can perform a requested action. A valid mTLS connection can still be forbidden from calling a route or method.

**Evidence/source concept:** Unit 8 — mTLS, traffic shifting, retries and circuit breaking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q117 — canary split

**Model answer:** Send a documented, bounded sample of requests to a controlled test path, identify backend version for each response, count outcomes and report sample size/variance. Configured weights express desired routing, not guaranteed exact proportions for every small sample or long-lived connection.

**Evidence/source concept:** Unit 8 — mTLS, traffic shifting, retries and circuit breaking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q118 — retry amplification

**Model answer:** Under the stated simplified model, 3 × 3 × 3 = 27 leaf attempts per original request. Real behavior depends on where retries are implemented and what failures are retried; the point is that nested retries multiply load. Set one clear retry owner/budget and measure.

**Evidence/source concept:** Unit 8 — mTLS, traffic shifting, retries and circuit breaking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q119 — retry safety

**Model answer:** Safety depends on operation idempotency, failure stage, whether the server may already have applied the operation, retryable error conditions, deadline, backoff/jitter and a bounded budget. Retrying non-idempotent writes can duplicate side effects unless the application uses idempotency controls.

**Evidence/source concept:** Unit 8 — mTLS, traffic shifting, retries and circuit breaking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q120 — timeout budget

**Model answer:** It leaves budget for subsequent permitted attempts and response handling. The exact relationship must account for backoff, connection setup and downstream deadlines; otherwise retries can continue after the caller has timed out.

**Evidence/source concept:** Unit 8 — mTLS, traffic shifting, retries and circuit breaking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q121 — circuit breaker

**Model answer:** A breaker temporarily stops or limits calls to a failing dependency based on configured signals, allowing recovery and protecting capacity. Retries repeat selected attempts and can worsen overload. Thresholds and behavior are implementation-specific; test both recovery and false-positive risk.

**Evidence/source concept:** Unit 8 — mTLS, traffic shifting, retries and circuit breaking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q122 — canary evidence

**Model answer:** Configuration does not prove observed traffic split or candidate health. Measure version-tagged requests, error/latency metrics and sample size; set promotion/abort thresholds and preserve rollback.

**Evidence/source concept:** Unit 8 — mTLS, traffic shifting, retries and circuit breaking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q123 — long-lived streams

**Model answer:** Existing streams may stay on the backend selected at connection establishment and not reflect a new per-request weight; idle/maximum duration and draining matter. Test stream lifecycle and reconnect behavior separately from short HTTP requests.

**Evidence/source concept:** Unit 8 — mTLS, traffic shifting, retries and circuit breaking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q124 — outlier detection

**Model answer:** It removes or deprioritizes endpoints that meet configured failure criteria. Aggressive thresholds can eject healthy endpoints due to noisy/transient failures and concentrate load on fewer backends. Validate implementation semantics and monitor capacity and recovery.

**Evidence/source concept:** Unit 8 — mTLS, traffic shifting, retries and circuit breaking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q125 — fault injection

**Model answer:** Target namespace/workload, exact fault and duration, allowed request path, expected signal, stop condition, owner/approval, blast radius, rollback and positive/negative verification. Use only disposable local resources or explicitly authorized test systems.

**Evidence/source concept:** Unit 8 — mTLS, traffic shifting, retries and circuit breaking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q126 — retry ownership

**Model answer:** Both may retry the same operation, multiplying attempts and obscuring ownership. Map retry policy by hop, choose one primary retry owner where feasible, propagate deadlines, use idempotency and verify actual attempt counts in telemetry.

**Evidence/source concept:** Unit 8 — mTLS, traffic shifting, retries and circuit breaking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q127 — mirroring

**Model answer:** Review whether mirrored requests contain personal/sensitive data, whether side effects are suppressed, how output is isolated, and how load/cost are bounded. Shadow traffic is not automatically safe or representative; do not mirror production payloads in this zero-budget exercise.

**Evidence/source concept:** Unit 8 — mTLS, traffic shifting, retries and circuit breaking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q128 — rate limiting

**Model answer:** Local limits are enforced within an instance/proxy and may allow aggregate throughput to scale with replica count; global limits coordinate across instances and require shared state/service or distributed coordination. Exact capabilities and failure modes are implementation-specific.

**Evidence/source concept:** Unit 8 — mTLS, traffic shifting, retries and circuit breaking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q129 — strict rollout

**Model answer:** Inventory clients and paths, verify mesh identity coverage, test policy in permissive/observe mode if supported, fix non-meshed clients, enable strict for a small scope, test allowed and denied paths, monitor errors, then expand with rollback criteria. Follow the selected mesh's exact semantics.

**Evidence/source concept:** Unit 8 — mTLS, traffic shifting, retries and circuit breaking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q130 — defense in depth

**Model answer:** Mesh authorization is enforced at covered proxy/application layers and may not cover every path; NetworkPolicy can restrict network reachability at L3/L4. Validate both systems and their interactions rather than treating either as a universal substitute.

**Evidence/source concept:** Unit 8 — mTLS, traffic shifting, retries and circuit breaking lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q131 — eBPF

**Model answer:** eBPF lets verified programs run at supported kernel hooks for tasks including networking and observability. Available hooks/helpers/features and operational constraints depend on kernel, distribution and implementation; verify support on the target host rather than assuming all Linux/WSL2 environments are equivalent.

**Evidence/source concept:** Unit 9 — eBPF networking and Cilium overview lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q132 — CNI/datapath

**Model answer:** CNI integration describes how runtime networking is configured; an eBPF datapath describes a way traffic processing/policy may be implemented in the kernel. A CNI can use eBPF, but CNI and eBPF are not synonyms.

**Evidence/source concept:** Unit 9 — eBPF networking and Cilium overview lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q133 — Cilium capabilities

**Model answer:** Depending on configuration/release, it can provide networking, policy, Service datapath features and flow visibility through Hubble. Verify the installed release, CRDs, kernel support and enabled components before asserting any feature is active.

**Evidence/source concept:** Unit 9 — eBPF networking and Cilium overview lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q134 — Hubble

**Model answer:** If Cilium/Hubble is installed and observes the relevant path, flow events can show endpoints, verdicts and available protocol context. They do not guarantee every flow is observed, prove application business success, or exist in clusters without Cilium/Hubble.

**Evidence/source concept:** Unit 9 — eBPF networking and Cilium overview lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q135 — CNI comparison

**Model answer:** Compare policy semantics, observability, datapath/performance method, encryption, IPAM/routing, kernel compatibility, operations, upgrade/rollback, ecosystem and support. Measure representative workload and verify features in the intended release; avoid universal benchmark claims.

**Evidence/source concept:** Unit 9 — eBPF networking and Cilium overview lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q136 — kube-proxy replacement

**Model answer:** Verify Cilium release and Kubernetes compatibility, kernel features, Service semantics required by workloads, installation values, routing/IPAM mode, host/NodePort behavior, observability, rollback and test coverage. Do not enable it solely because eBPF is available.

**Evidence/source concept:** Unit 9 — eBPF networking and Cilium overview lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q137 — CRD availability

**Model answer:** Custom resources are available only when their CRDs are installed and compatible. Check installed CRDs and version-matched schema/docs before applying CiliumNetworkPolicy or cluster-wide policy; otherwise use an illustrative/read-only exercise.

**Evidence/source concept:** Unit 9 — eBPF networking and Cilium overview lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q138 — encryption boundary

**Model answer:** Network encryption such as a CNI-supported tunnel protects traffic at the network layer according to its configuration; mTLS authenticates TLS peers and protects the application connection. Encryption at one layer does not automatically establish application identity or authorization.

**Evidence/source concept:** Unit 9 — eBPF networking and Cilium overview lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q139 — cluster-wide policy

**Model answer:** A cluster-wide policy can affect unrelated namespaces and control/data-plane components, causing broad outage or lockout. Keep review-only unless a disposable cluster and exact scope are verified; prefer namespace/workload-scoped exercises and explicit cleanup.

**Evidence/source concept:** Unit 9 — eBPF networking and Cilium overview lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q140 — WSL2 constraints

**Model answer:** Capture versions and installer/status errors, check the official Cilium/kind/kernel compatibility requirements and available kernel features. Do not keep retrying mutations or assume Windows host support equals the Linux environment's support; use the lesson's read-only/analysis alternative if prerequisites fail.

**Evidence/source concept:** Unit 9 — eBPF networking and Cilium overview lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q141 — FQDN/L7

**Model answer:** As Cilium-specific extensions whose exact support depends on release, CRDs, DNS proxy and configuration. Verify the installed documentation/schema and test controlled allowed/denied flows; do not attribute these capabilities to vanilla Kubernetes NetworkPolicy.

**Evidence/source concept:** Unit 9 — eBPF networking and Cilium overview lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q142 — performance

**Model answer:** Performance depends on workload, kernel, hardware, traffic pattern, policy complexity, observability and measurement method. Define baseline, repeat runs, measure throughput/latency/CPU/memory and error rate, record versions/noise and disclose limits rather than generalizing one benchmark.

**Evidence/source concept:** Unit 9 — eBPF networking and Cilium overview lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q143 — methodology

**Model answer:** Define symptom → locate likely layer → isolate failing hop → gather evidence → rank hypotheses → test one hypothesis → apply smallest safe fix → verify recovery → record prevention. Preserve timestamps and distinguish symptom, cause, contributing factor and detection gap.

**Evidence/source concept:** Unit 10 — Network troubleshooting: DNS, latency and packet loss lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q144 — curl timing

**Model answer:** They separate DNS lookup, TCP connection, TLS handshake completion, time to first response byte and whole transfer duration. Variables include earlier phases and are affected by connection reuse/proxying; use the installed curl documentation and repeat measurements.

**Evidence/source concept:** Unit 10 — Network troubleshooting: DNS, latency and packet loss lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q145 — ICMP

**Model answer:** ICMP echo is unavailable/filtered/rate-limited or follows different handling, while the tested TCP path succeeded. Do not treat ping failure as proof of application unreachability; test the actual protocol/port and correlate evidence.

**Evidence/source concept:** Unit 10 — Network troubleshooting: DNS, latency and packet loss lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q146 — ss retransmits

**Model answer:** It can expose supported per-socket TCP details including retransmission-related data. Output depends on kernel/iproute2 and namespace; it is evidence for a connection, not proof of root cause or a complete path-wide loss metric.

**Evidence/source concept:** Unit 10 — Network troubleshooting: DNS, latency and packet loss lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q147 — interface drops

**Model answer:** Counters are often cumulative and may include unrelated traffic. Record a baseline and later value with timestamps, identify the interface/namespace and correlate with the incident window before attributing drops to the failing request.

**Evidence/source concept:** Unit 10 — Network troubleshooting: DNS, latency and packet loss lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q148 — TCP handshake

**Model answer:** At that capture point, the observed handshake attempt did not show a corresponding SYN-ACK in the capture window. Possible causes include listener/path/filter/return-path issues or capture placement/visibility; compare captures at multiple authorized points and check socket/listener evidence.

**Evidence/source concept:** Unit 10 — Network troubleshooting: DNS, latency and packet loss lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q149 — conntrack

**Model answer:** It requires compatible userspace tooling, kernel/netfilter support and appropriate privileges `[VERIFY]`. Exhaustion can disrupt unrelated host traffic; use approved metrics/counters and a safe analysis exercise rather than generating resource exhaustion.

**Evidence/source concept:** Unit 10 — Network troubleshooting: DNS, latency and packet loss lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q150 — MTU

**Model answer:** Consider MTU/PMTUD black hole, proxy body/buffering limits, TLS/protocol behavior and slow backend processing. Compare payload sizes, phase timing, interface/tunnel MTUs and approved packet evidence; do not lower MTU globally without proof.

**Evidence/source concept:** Unit 10 — Network troubleshooting: DNS, latency and packet loss lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q151 — traceroute

**Model answer:** Routers may rate-limit or filter probes while forwarding transit traffic, and return paths can be asymmetric. Loss at an intermediate hop that does not persist to the destination is not proof of end-to-end packet loss; pair with actual application tests.

**Evidence/source concept:** Unit 10 — Network troubleshooting: DNS, latency and packet loss lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q152 — DNS policy

**Model answer:** Verify CNI enforcement, Pod labels/policy selection, `/etc/resolv.conf`, DNS Service/EndpointSlices and egress rules for the actual resolver over required UDP/TCP. Compare a known-good source and make the smallest policy correction, then test allowed and denied flows.

**Evidence/source concept:** Unit 10 — Network troubleshooting: DNS, latency and packet loss lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q153 — diagnostic toolbox

**Model answer:** Use an approved image with verified provenance/tag or digest, a dedicated namespace, minimal privileges and narrowly scoped RBAC; avoid host networking/privileged mode unless explicitly approved. Record cleanup and remember its network identity may differ from the failing Pod.

**Evidence/source concept:** Unit 10 — Network troubleshooting: DNS, latency and packet loss lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q154 — kubectl debug

**Model answer:** It depends on Kubernetes version, target/mode, RBAC, admission policy, runtime and approved debug image. Check official docs and cluster policy; use read-only API inspection or an approved dedicated diagnostic Pod when unavailable.

**Evidence/source concept:** Unit 10 — Network troubleshooting: DNS, latency and packet loss lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q155 — HTTP status

**Model answer:** 502 commonly indicates a gateway's upstream interaction failed; 503 indicates the responder is unavailable; 504 indicates a gateway timed out; 499 is commonly an NGINX log code for client-closed requests. These meanings depend on hop/implementation; correlate status, headers, logs, timing and request IDs.

**Evidence/source concept:** Unit 10 — Network troubleshooting: DNS, latency and packet loss lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q156 — latency statistics

**Model answer:** Percentiles describe a distribution over a defined sample/window. One request supplies one observation; collect enough representative samples, record warm-up, concurrency, request mix, variance and measurement noise, and compare equivalent windows.

**Evidence/source concept:** Unit 10 — Network troubleshooting: DNS, latency and packet loss lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q157 — pcap hygiene

**Model answer:** Captures may expose IPs, DNS names, metadata and unencrypted payload/credentials. Use narrow filters, short bounded captures, restrictive permissions, approved storage/retention and redaction; ordinary TLS payload is encrypted, but metadata remains sensitive.

**Evidence/source concept:** Unit 10 — Network troubleshooting: DNS, latency and packet loss lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q158 — timeout ladder

**Model answer:** Measure connect/TLS/TTFB/total and correlate request IDs across ingress, mesh, app and dependency. Compare each component's timeout semantics and retry budget; fix coherent deadlines/cancellation behavior, then verify user response and downstream work stop appropriately.

**Evidence/source concept:** Unit 10 — Network troubleshooting: DNS, latency and packet loss lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q159 — Hubble

**Model answer:** It can provide Cilium-observed flow and policy verdict context, depending on enabled components/version. It does not exist universally, cannot be assumed to see every path, and cannot alone prove application-level success.

**Evidence/source concept:** Unit 10 — Network troubleshooting: DNS, latency and packet loss lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q160 — debug restrictions

**Model answer:** Admission standards may reject privileged or host-level settings; policy may isolate the diagnostic Pod or prevent DNS/target access. Request time-bounded approved access, use least privilege and inspect policy/admission events rather than disabling controls broadly.

**Evidence/source concept:** Unit 10 — Network troubleshooting: DNS, latency and packet loss lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q161 — runbook

**Model answer:** Impact/start/detection, cluster/context/scope, known-good and failing path, timestamped evidence, ranked hypotheses, command classification, mitigation approval/rollback, verification, communications, root cause/contributors/detection gaps and owner/due date prevention actions.

**Evidence/source concept:** Unit 10 — Network troubleshooting: DNS, latency and packet loss lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q162 — transport symptoms

**Model answer:** Timeout means no acceptable response arrived within the wait; refusal commonly indicates an active rejection/no listener; reset indicates a TCP reset was received/generated. They narrow hypotheses but do not alone identify the responsible hop; correlate packet/socket/app evidence.

**Evidence/source concept:** Unit 10 — Network troubleshooting: DNS, latency and packet loss lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q163 — tc netem

**Model answer:** Only on a known disposable namespace/interface with permissions, after recording current qdisc state and defining bounded impairment plus exact restoration. Syntax/availability are `[VERIFY]`; if scope or rollback is uncertain, use an analysis-only exercise. Never impair an unknown host interface.

**Evidence/source concept:** Unit 10 — Network troubleshooting: DNS, latency and packet loss lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q164 — postmortem

**Model answer:** It identifies why monitoring, tests or operational controls did not detect/prevent the issue earlier, without blaming an individual. Convert findings into owned, dated actions with measurable completion criteria and preserve evidence-based reasoning.

**Evidence/source concept:** Unit 10 — Network troubleshooting: DNS, latency and packet loss lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q165 — capstone path

**Model answer:** Document client→ingress/Gateway TLS, ingress→model-api transport, model-api→feature-service, database/cache access, ETL external egress, metrics access and optional mesh identity. State where TLS terminates/restarts, which identities are authenticated/authorized and which dependencies remain internal.

**Evidence/source concept:** Cross-unit architecture and capstone lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q166 — internal dependencies

**Model answer:** External exposure expands attack surface and bypasses the intended internal trust boundary. Use internal-only Service types and least-privilege network/policy access, confirm no public route/LB is created, and test only approved local paths.

**Evidence/source concept:** Cross-unit architecture and capstone lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q167 — policy acceptance

**Model answer:** Capture the policy and live labels, confirm CNI enforcement, run a positive request from the approved model-api path and a negative request from a controlled unauthorized source, and record timestamps/results. Policy YAML alone is not proof of enforcement.

**Evidence/source concept:** Cross-unit architecture and capstone lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q168 — ETL egress

**Model answer:** Use architecture/policy review or a controlled local mock endpoint; define allowed destination/protocol and deny unrelated egress. Validate implementation-specific FQDN/eGateway support before using it and do not probe third-party networks.

**Evidence/source concept:** Cross-unit architecture and capstone lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q169 — canary

**Model answer:** Use version-tagged request counts, error rate, latency percentiles, sample size, resource use and relevant SLO/guardrails; confirm routing actually produced enough candidate observations. Keep promotion/abort thresholds and rollback explicit; configured weight alone is not acceptance evidence.

**Evidence/source concept:** Cross-unit architecture and capstone lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q170 — streaming acceptance

**Model answer:** Test streaming establishment, data continuity, idle/maximum-duration timeouts, reconnect/draining, cancellation and protocol handling. A quick HTTP 200 does not prove long-lived stream reliability; test in a controlled local environment and record limitations.

**Evidence/source concept:** Cross-unit architecture and capstone lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q171 — mTLS authorization

**Model answer:** mTLS authenticates peer identity and encrypts the connection, but application/mesh authorization may still be absent, too broad or incorrectly scoped. Verify identity and authorization separately with both positive and negative requests.

**Evidence/source concept:** Cross-unit architecture and capstone lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q172 — mesh choice

**Model answer:** Preserve the available lesson's Linkerd sidecar hands-on assumption; compare Istio as awareness unless the controlling source is deliberately changed. Record required features, measured resource footprint method, operational complexity, policy/routing needs, compatibility and rollback; do not fabricate benchmark values.

**Evidence/source concept:** Cross-unit architecture and capstone lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q173 — Cilium fallback

**Model answer:** Use the documented awareness/analysis path: explain architecture and policy/flow evidence from source-backed examples, mark local feature tests `[VERIFY]`, and do not force installation or alter the host kernel. Record exact compatibility check and limitation.

**Evidence/source concept:** Cross-unit architecture and capstone lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q174 — rollback

**Model answer:** State trigger/threshold, approver, last known-good configuration, scoped rollback command/process, data-plane verification, negative security tests and communication owner. Preserve evidence and avoid broad deletion or disabling all policy; rollback must restore security posture as well as availability.

**Evidence/source concept:** Cross-unit architecture and capstone lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q175 — secrets

**Model answer:** Use placeholders and lab-only credentials; never commit private keys/tokens or dump Secret data/environment variables. Restrict file permissions, redact headers/pcaps/logs, use least-privilege RBAC and document artifact retention/deletion.

**Evidence/source concept:** Cross-unit architecture and capstone lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q176 — SLO

**Model answer:** Choose user-relevant availability/error and latency indicators such as request success ratio and latency percentiles, supplemented by DNS success/latency, endpoint health and dependency saturation. Define window, denominator, exclusions and alert threshold; do not use raw infrastructure counters as a substitute for user impact.

**Evidence/source concept:** Cross-unit architecture and capstone lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q177 — evidence

**Model answer:** Configured state is API/manifests and intended weights/policies; observed state is controller status, endpoint selection, actual request distribution, identity, TLS negotiation, errors and measured telemetry. Acceptance needs both, with version and environment recorded.

**Evidence/source concept:** Cross-unit architecture and capstone lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q178 — TLS boundaries

**Model answer:** Identify client-facing certificate/SNI/trust and ingress termination, then the backend mesh identity, peer policy and authorization. Clarify whether ingress-to-workload traffic is re-encrypted, how certificates rotate and which components can see plaintext at each boundary.

**Evidence/source concept:** Cross-unit architecture and capstone lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q179 — source limits

**Model answer:** Assess only the source-supported scope, disclose the missing file, mark detailed implementation claims `[VERIFY]` and test the method of verification rather than invented specifics. Do not silently replace the roadmap with general assumptions.

**Evidence/source concept:** Cross-unit architecture and capstone lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q180 — reproducibility

**Model answer:** Record OS/kernel, Docker/kind/Kubernetes and controller/CNI versions, commands actually run, context/namespace, expected versus observed results, logs/events, resource footprint, cleanup and unresolved issues. If not run, label it as authored/expected rather than tested.

**Evidence/source concept:** Cross-unit architecture and capstone lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q181 — readiness vs SLO

**Model answer:** Readiness indicates the configured probe passed, not that every request path or dependency meets latency SLO. Correlate endpoint-level request timings, CPU throttling, queueing, dependencies and probe semantics; do not treat readiness as a complete performance test.

**Evidence/source concept:** Cross-unit architecture and capstone lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q182 — negative tests

**Model answer:** Unauthorized namespace/source, forbidden port/path, invalid hostname/untrusted certificate, plaintext-to-strict-mTLS mismatch, forbidden egress and invalid route/policy cases as applicable. For each, specify expected denial evidence and confirm the legitimate path still works.

**Evidence/source concept:** Cross-unit architecture and capstone lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q183 — telemetry correlation

**Model answer:** Use UTC timestamps, request/trace IDs, source/destination, namespace, Pod revision and endpoint identity; account for clock skew and sampling. Each signal has blind spots, so conclusions should combine independent evidence and label uncertainty.

**Evidence/source concept:** Cross-unit architecture and capstone lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

### Q184 — resource budget

**Model answer:** Sequence heavy components rather than running a mesh, Cilium/Hubble and full observability stack together; measure actual footprint, keep one selected mesh and small sample apps, remove optional components after each milestone, and use analysis-only alternatives when capacity/compatibility is insufficient.

**Evidence/source concept:** Cross-unit architecture and capstone lesson and the corresponding source-backed concept identified in the coverage matrix. Where implementation/version support is material, verify the installed API/schema and official documentation before acting.

## Troubleshooting Decision Drills

| Symptom | First discriminating check | Likely causes to rank | Next evidence |
|---|---|---|---|
| Service resolves but request fails | Inspect Service ports/selectors and EndpointSlices | wrong targetPort/listener; no ready endpoints; policy/datapath | Pod readiness, listener, source-specific policy and bounded request |
| DNS timeout | Read Pod `/etc/resolv.conf`; test exact query | CoreDNS endpoint issue; DNS egress blocked; upstream/return path | CoreDNS status/logs, policy, query name/type and resolver |
| Ingress returns 502/503/504 | Identify emitting hop from correlated logs/headers | backend connect/protocol failure; no healthy backend; timeout budget | controller status/events, endpoints, app logs and phase timings |
| TLS verification fails | Check hostname/SNI, expiry and trust chain | wrong cert selected; expired/missing intermediate; trust mismatch | served certificate, termination point, client trust store |
| Small payload works, large stalls | Compare payload sizes and phase timing | MTU/PMTUD; proxy body/buffering limits; slow backend | MTUs, approved capture evidence, controller limits and traces |
| Only one source Pod fails | Compare namespace, labels, node and resolver config | policy selector/identity; node path; mesh enrollment | applicable policies, source-to-source test and flow logs |
| Intermittent new connections fail | Correlate time window with connection errors/counters | conntrack/SNAT pressure; ephemeral ports; listener/backlog pressure | approved metrics, `ss`, supported `nstat`/conntrack evidence |
| Client times out but app continues | Compare timeout semantics across hops | client deadline shorter than upstream work; retry amplification | request ID timeline, per-hop logs/traces and cancellation evidence |
| Ping fails but TCP succeeds | Test the actual protocol/port | ICMP filtering/rate limit; different path handling | bounded TCP request and destination logs |
| Route exists but external traffic fails | Check controller/class/Gateway acceptance | controller absent/mismatch; backend protocol/endpoint issue; local NAT/port mapping | status/events, controller logs, backend Service and local path |

## Capstone Readiness Assessment

**Scope note:** the detailed capstone file was not available separately. This is an integration assessment based only on the capstone themes in the uploaded prompt and available syllabus, not a claim about exact project-specific acceptance criteria.

### Scenario

You are reviewing a local, zero-budget secure ingress and mTLS design for a FastAPI model-scoring API. It calls an internal feature service and Postgres/Redis; an ETL worker calls external APIs; metrics are exposed through a controlled internal path; the team wants a model-version canary. The laptop budget is approximately 4 CPU, 8 GB RAM and 30 GB disk. No public domain, public endpoint, managed cloud or real credentials are allowed.

### Review tasks

1. Draw the client → ingress/Gateway → Service/EndpointSlice → model-api → feature-service/database path and identify every trust boundary.
2. State where TLS terminates, whether backend traffic is re-encrypted, and how workload identity, authentication and authorization differ.
3. Propose least-privilege NetworkPolicy and optional mesh policy for approved paths; include DNS and ETL egress, while noting CNI enforcement prerequisites.
4. Define a 90/10 canary verification plan using version-tagged requests, error/latency guardrails and a minimum evidence window; do not treat configured weights as measured outcomes.
5. Create a failure matrix for wrong targetPort, DNS egress blocked, expired/mismatched certificate, strict-mTLS/plaintext mismatch and timeout-ladder mismatch.
6. Define SLI/SLO signals and correlate metrics/logs/traces/request IDs across ingress, mesh, app and dependency.
7. Specify rollback trigger, owner, last known-good state, positive and negative tests, and cleanup.
8. State how the design changes if Cilium/Gateway API/controller/mesh is unavailable or incompatible; provide a safe analysis-only fallback.
9. List environment/version evidence and what remains `[VERIFY]`.

### 100-point rubric

| Area | Points | Poor | Adequate | Strong | Exemplary |
|---|---:|---|---|---|---|
| Architecture/path | 15 | Missing hops | Main path named | Trust boundaries and endpoints correct | Alternatives and failure paths explicit |
| Security boundaries | 20 | Broad/public exposure | Basic TLS/policy | Least privilege, identity/authz distinct | Positive/negative tests and layered controls |
| Traffic/canary | 15 | Weights assumed to prove outcome | Basic sample test | Version tags, sample size and guardrails | Rollback and statistical limitations explicit |
| Troubleshooting/evidence | 20 | Random restarts | Some checks | Ranked hypotheses and discriminating tests | Correlated evidence and uncertainty managed |
| SLO/observability | 10 | No user signal | Basic metrics | Defined latency/error windows | Logs/metrics/traces with IDs and detection gaps |
| Safety/rollback | 15 | Unsafe or unguarded changes | Cleanup stated | Context guard, scope, rollback and tests | Least privilege, evidence preservation and residual risks |
| Resource/version discipline | 5 | Assumes all components | Notes some constraints | Sequencing and `[VERIFY]` | Measured local budget plan and analysis fallback |

**Acceptance evidence checklist:** architecture diagram; live Service/EndpointSlice/Pod evidence where lab is run; policy positive/negative results; served certificate/SNI/trust evidence; actual mTLS identity evidence if mesh exists; measured version-tagged canary results; request timing and SLO window; rollback record; environment versions; cleanup verification. If not executed, mark as expected/illustrative and do not claim acceptance.

## Remediation Plan

| Missed area / question IDs | Revisit | Remediation action |
|---|---|---|
| Q001–Q016 | `01-kubernetes-networking-model-cni-and-pod-networking.md` | Re-read the weak concept, redo the relevant local/read-only lab, capture evidence and explain the fix without relying on memory. |
| Q017–Q034 | `02-services-kube-proxy-and-cluster-dns.md` | Re-read the weak concept, redo the relevant local/read-only lab, capture evidence and explain the fix without relying on memory. |
| Q035–Q052 | `03-ingress-controllers-and-gateway-api.md` | Re-read the weak concept, redo the relevant local/read-only lab, capture evidence and explain the fix without relying on memory. |
| Q053–Q066 | `04-load-balancers-and-external-traffic-management.md` | Re-read the weak concept, redo the relevant local/read-only lab, capture evidence and explain the fix without relying on memory. |
| Q067–Q082 | `05-network-policies-and-zero-trust-segmentation.md` | Re-read the weak concept, redo the relevant local/read-only lab, capture evidence and explain the fix without relying on memory. |
| Q083–Q098 | `06-tls-termination-and-certificate-lifecycle-with-cert-manager.md` | Re-read the weak concept, redo the relevant local/read-only lab, capture evidence and explain the fix without relying on memory. |
| Q099–Q112 | `07-service-mesh-fundamentals-istio-and-linkerd.md` | Re-read the weak concept, redo the relevant local/read-only lab, capture evidence and explain the fix without relying on memory. |
| Q113–Q130 | `08-mtls-traffic-shifting-retries-and-circuit-breaking.md` | Re-read the weak concept, redo the relevant local/read-only lab, capture evidence and explain the fix without relying on memory. |
| Q131–Q142 | `09-ebpf-networking-and-cilium-overview.md` | Re-read the weak concept, redo the relevant local/read-only lab, capture evidence and explain the fix without relying on memory. |
| Q143–Q164 | `10-network-troubleshooting-dns-latency-and-packet-loss.md` | Re-read the weak concept, redo the relevant local/read-only lab, capture evidence and explain the fix without relying on memory. |
| Q165–Q184 | M04 capstone themes in syllabus and this assessment | Rebuild the request-path/trust-boundary review; note that detailed capstone source was unavailable. |

**Foundational gaps:** revisit L1 DNS, Service, Pod/node/Service IP and TLS concepts. **Applied gaps:** repeat selector/port/route/policy review. **Production design gaps:** practice SLO, timeout, canary, draining and rollback reasoning. **Expert troubleshooting gaps:** correlate phase timings, packets, kernel counters and path evidence. **Safety gaps:** repeat context guards, local-only scope, least privilege, capture hygiene and source/version verification before any mutation.

## Appendix A — Coverage Matrix

| Mandatory topic / source concept | Question IDs | Answer IDs |
|---|---|---|
| Unit 1 — Kubernetes networking model, CNI and Pod networking: network model | Q001 | Q001 |
| Unit 1 — Kubernetes networking model, CNI and Pod networking: IP identity | Q002 | Q002 |
| Unit 1 — Kubernetes networking model, CNI and Pod networking: network namespaces | Q003 | Q003 |
| Unit 1 — Kubernetes networking model, CNI and Pod networking: cross-node path | Q004 | Q004 |
| Unit 1 — Kubernetes networking model, CNI and Pod networking: CNI implementation | Q005 | Q005 |
| Unit 1 — Kubernetes networking model, CNI and Pod networking: CNI versus Service datapath | Q006 | Q006 |
| Unit 1 — Kubernetes networking model, CNI and Pod networking: CNI selection | Q007 | Q007 |
| Unit 1 — Kubernetes networking model, CNI and Pod networking: CNI failure | Q008 | Q008 |
| Unit 1 — Kubernetes networking model, CNI and Pod networking: MTU and PMTUD | Q009 | Q009 |
| Unit 1 — Kubernetes networking model, CNI and Pod networking: network architecture | Q010 | Q010 |
| Unit 1 — Kubernetes networking model, CNI and Pod networking: IPAM/CIDR | Q011 | Q011 |
| Unit 1 — Kubernetes networking model, CNI and Pod networking: hostNetwork | Q012 | Q012 |
| Unit 1 — Kubernetes networking model, CNI and Pod networking: address identity | Q013 | Q013 |
| Unit 1 — Kubernetes networking model, CNI and Pod networking: CNI migration | Q014 | Q014 |
| Unit 1 — Kubernetes networking model, CNI and Pod networking: ADR | Q015 | Q015 |
| Unit 1 — Kubernetes networking model, CNI and Pod networking: veth and routes | Q016 | Q016 |
| Unit 2 — Services, kube-proxy and cluster DNS: Service types | Q017 | Q017 |
| Unit 2 — Services, kube-proxy and cluster DNS: port mapping | Q018 | Q018 |
| Unit 2 — Services, kube-proxy and cluster DNS: EndpointSlice | Q019 | Q019 |
| Unit 2 — Services, kube-proxy and cluster DNS: Service diagnosis | Q020 | Q020 |
| Unit 2 — Services, kube-proxy and cluster DNS: kube-proxy | Q021 | Q021 |
| Unit 2 — Services, kube-proxy and cluster DNS: CoreDNS | Q022 | Q022 |
| Unit 2 — Services, kube-proxy and cluster DNS: ndots | Q023 | Q023 |
| Unit 2 — Services, kube-proxy and cluster DNS: FQDN | Q024 | Q024 |
| Unit 2 — Services, kube-proxy and cluster DNS: resolver mismatch | Q025 | Q025 |
| Unit 2 — Services, kube-proxy and cluster DNS: NodeLocal DNSCache | Q026 | Q026 |
| Unit 2 — Services, kube-proxy and cluster DNS: DNS policy | Q027 | Q027 |
| Unit 2 — Services, kube-proxy and cluster DNS: LoadBalancer pending | Q028 | Q028 |
| Unit 2 — Services, kube-proxy and cluster DNS: headless Service | Q029 | Q029 |
| Unit 2 — Services, kube-proxy and cluster DNS: rollout endpoints | Q030 | Q030 |
| Unit 2 — Services, kube-proxy and cluster DNS: conntrack | Q031 | Q031 |
| Unit 2 — Services, kube-proxy and cluster DNS: DNS SLO | Q032 | Q032 |
| Unit 2 — Services, kube-proxy and cluster DNS: selectorless Service | Q033 | Q033 |
| Unit 2 — Services, kube-proxy and cluster DNS: DNS errors | Q034 | Q034 |
| Unit 3 — Ingress controllers and Gateway API: Ingress object/controller | Q035 | Q035 |
| Unit 3 — Ingress controllers and Gateway API: traffic direction | Q036 | Q036 |
| Unit 3 — Ingress controllers and Gateway API: IngressClass | Q037 | Q037 |
| Unit 3 — Ingress controllers and Gateway API: desired vs observed | Q038 | Q038 |
| Unit 3 — Ingress controllers and Gateway API: Gateway API | Q039 | Q039 |
| Unit 3 — Ingress controllers and Gateway API: ReferenceGrant | Q040 | Q040 |
| Unit 3 — Ingress controllers and Gateway API: HTTPRoute status | Q041 | Q041 |
| Unit 3 — Ingress controllers and Gateway API: Ingress vs Gateway API | Q042 | Q042 |
| Unit 3 — Ingress controllers and Gateway API: annotations | Q043 | Q043 |
| Unit 3 — Ingress controllers and Gateway API: HTTP status | Q044 | Q044 |
| Unit 3 — Ingress controllers and Gateway API: streaming | Q045 | Q045 |
| Unit 3 — Ingress controllers and Gateway API: weighted routing | Q046 | Q046 |
| Unit 3 — Ingress controllers and Gateway API: route debugging | Q047 | Q047 |
| Unit 3 — Ingress controllers and Gateway API: controller selection | Q048 | Q048 |
| Unit 3 — Ingress controllers and Gateway API: client IP | Q049 | Q049 |
| Unit 3 — Ingress controllers and Gateway API: multi-tenancy | Q050 | Q050 |
| Unit 3 — Ingress controllers and Gateway API: HA/PDB | Q051 | Q051 |
| Unit 3 — Ingress controllers and Gateway API: migration | Q052 | Q052 |
| Unit 4 — Load balancers and external traffic management: LoadBalancer | Q053 | Q053 |
| Unit 4 — Load balancers and external traffic management: L4/L7 | Q054 | Q054 |
| Unit 4 — Load balancers and external traffic management: externalTrafficPolicy | Q055 | Q055 |
| Unit 4 — Load balancers and external traffic management: node path | Q056 | Q056 |
| Unit 4 — Load balancers and external traffic management: health checks | Q057, Q062 | Q057, Q062 |
| Unit 4 — Load balancers and external traffic management: draining | Q058 | Q058 |
| Unit 4 — Load balancers and external traffic management: timeout ladder | Q059 | Q059 |
| Unit 4 — Load balancers and external traffic management: egress NAT | Q060 | Q060 |
| Unit 4 — Load balancers and external traffic management: kind fidelity | Q061 | Q061 |
| Unit 4 — Load balancers and external traffic management: TLS boundary | Q063 | Q063 |
| Unit 4 — Load balancers and external traffic management: global traffic | Q064 | Q064 |
| Unit 4 — Load balancers and external traffic management: algorithms | Q065 | Q065 |
| Unit 4 — Load balancers and external traffic management: forwarded headers | Q066 | Q066 |
| Unit 5 — Network policies and zero-trust segmentation: policy boundary | Q067 | Q067 |
| Unit 5 — Network policies and zero-trust segmentation: additive policy | Q068 | Q068 |
| Unit 5 — Network policies and zero-trust segmentation: selector mismatch | Q069 | Q069 |
| Unit 5 — Network policies and zero-trust segmentation: DNS egress | Q070 | Q070 |
| Unit 5 — Network policies and zero-trust segmentation: CNI enforcement | Q071 | Q071 |
| Unit 5 — Network policies and zero-trust segmentation: least privilege | Q072 | Q072 |
| Unit 5 — Network policies and zero-trust segmentation: namespace selector | Q073 | Q073 |
| Unit 5 — Network policies and zero-trust segmentation: egress control | Q074 | Q074 |
| Unit 5 — Network policies and zero-trust segmentation: SSRF | Q075 | Q075 |
| Unit 5 — Network policies and zero-trust segmentation: policy rollout | Q076 | Q076 |
| Unit 5 — Network policies and zero-trust segmentation: desired vs observed | Q077 | Q077 |
| Unit 5 — Network policies and zero-trust segmentation: policy and mesh | Q078 | Q078 |
| Unit 5 — Network policies and zero-trust segmentation: safe operations | Q079 | Q079 |
| Unit 5 — Network policies and zero-trust segmentation: policy testing | Q080 | Q080 |
| Unit 5 — Network policies and zero-trust segmentation: L7/FQDN policy | Q081 | Q081 |
| Unit 5 — Network policies and zero-trust segmentation: policy diagnosis | Q082 | Q082 |
| Unit 6 — TLS termination and certificate lifecycle: certificate meaning | Q083 | Q083 |
| Unit 6 — TLS termination and certificate lifecycle: SAN | Q084 | Q084 |
| Unit 6 — TLS termination and certificate lifecycle: SNI | Q085 | Q085 |
| Unit 6 — TLS termination and certificate lifecycle: termination modes | Q086 | Q086 |
| Unit 6 — TLS termination and certificate lifecycle: TLS validation | Q087 | Q087 |
| Unit 6 — TLS termination and certificate lifecycle: cert-manager | Q088 | Q088 |
| Unit 6 — TLS termination and certificate lifecycle: local CA | Q089 | Q089 |
| Unit 6 — TLS termination and certificate lifecycle: renewal diagnosis | Q090 | Q090 |
| Unit 6 — TLS termination and certificate lifecycle: private keys | Q091 | Q091 |
| Unit 6 — TLS termination and certificate lifecycle: certificate chain | Q092 | Q092 |
| Unit 6 — TLS termination and certificate lifecycle: client divergence | Q093 | Q093 |
| Unit 6 — TLS termination and certificate lifecycle: expiry monitoring | Q094 | Q094 |
| Unit 6 — TLS termination and certificate lifecycle: security properties | Q095 | Q095 |
| Unit 6 — TLS termination and certificate lifecycle: ALPN | Q096 | Q096 |
| Unit 6 — TLS termination and certificate lifecycle: backend encryption | Q097 | Q097 |
| Unit 6 — TLS termination and certificate lifecycle: TLS acceptance | Q098 | Q098 |
| Unit 7 — Service mesh fundamentals: Istio and Linkerd: control/data plane | Q099 | Q099 |
| Unit 7 — Service mesh fundamentals: Istio and Linkerd: sidecar | Q100 | Q100 |
| Unit 7 — Service mesh fundamentals: Istio and Linkerd: mesh comparison | Q101 | Q101 |
| Unit 7 — Service mesh fundamentals: Istio and Linkerd: selected mesh | Q102 | Q102 |
| Unit 7 — Service mesh fundamentals: Istio and Linkerd: injection | Q103 | Q103 |
| Unit 7 — Service mesh fundamentals: Istio and Linkerd: mesh/policy | Q104 | Q104 |
| Unit 7 — Service mesh fundamentals: Istio and Linkerd: upgrade | Q105 | Q105 |
| Unit 7 — Service mesh fundamentals: Istio and Linkerd: mesh boundaries | Q106 | Q106 |
| Unit 7 — Service mesh fundamentals: Istio and Linkerd: mesh evidence | Q107 | Q107 |
| Unit 7 — Service mesh fundamentals: Istio and Linkerd: sidecar operations | Q108 | Q108 |
| Unit 7 — Service mesh fundamentals: Istio and Linkerd: mesh limitations | Q109 | Q109 |
| Unit 7 — Service mesh fundamentals: Istio and Linkerd: measurement | Q110 | Q110 |
| Unit 7 — Service mesh fundamentals: Istio and Linkerd: control-plane failure | Q111 | Q111 |
| Unit 7 — Service mesh fundamentals: Istio and Linkerd: mesh security | Q112 | Q112 |
| Unit 8 — mTLS, traffic shifting, retries and circuit breaking: mTLS | Q113 | Q113 |
| Unit 8 — mTLS, traffic shifting, retries and circuit breaking: strict/permissive | Q114 | Q114 |
| Unit 8 — mTLS, traffic shifting, retries and circuit breaking: mTLS mismatch | Q115 | Q115 |
| Unit 8 — mTLS, traffic shifting, retries and circuit breaking: security properties | Q116 | Q116 |
| Unit 8 — mTLS, traffic shifting, retries and circuit breaking: canary split | Q117 | Q117 |
| Unit 8 — mTLS, traffic shifting, retries and circuit breaking: retry amplification | Q118 | Q118 |
| Unit 8 — mTLS, traffic shifting, retries and circuit breaking: retry safety | Q119 | Q119 |
| Unit 8 — mTLS, traffic shifting, retries and circuit breaking: timeout budget | Q120 | Q120 |
| Unit 8 — mTLS, traffic shifting, retries and circuit breaking: circuit breaker | Q121 | Q121 |
| Unit 8 — mTLS, traffic shifting, retries and circuit breaking: canary evidence | Q122 | Q122 |
| Unit 8 — mTLS, traffic shifting, retries and circuit breaking: long-lived streams | Q123 | Q123 |
| Unit 8 — mTLS, traffic shifting, retries and circuit breaking: outlier detection | Q124 | Q124 |
| Unit 8 — mTLS, traffic shifting, retries and circuit breaking: fault injection | Q125 | Q125 |
| Unit 8 — mTLS, traffic shifting, retries and circuit breaking: retry ownership | Q126 | Q126 |
| Unit 8 — mTLS, traffic shifting, retries and circuit breaking: mirroring | Q127 | Q127 |
| Unit 8 — mTLS, traffic shifting, retries and circuit breaking: rate limiting | Q128 | Q128 |
| Unit 8 — mTLS, traffic shifting, retries and circuit breaking: strict rollout | Q129 | Q129 |
| Unit 8 — mTLS, traffic shifting, retries and circuit breaking: defense in depth | Q130 | Q130 |
| Unit 9 — eBPF networking and Cilium overview: eBPF | Q131 | Q131 |
| Unit 9 — eBPF networking and Cilium overview: CNI/datapath | Q132 | Q132 |
| Unit 9 — eBPF networking and Cilium overview: Cilium capabilities | Q133 | Q133 |
| Unit 9 — eBPF networking and Cilium overview: Hubble | Q134 | Q134 |
| Unit 9 — eBPF networking and Cilium overview: CNI comparison | Q135 | Q135 |
| Unit 9 — eBPF networking and Cilium overview: kube-proxy replacement | Q136 | Q136 |
| Unit 9 — eBPF networking and Cilium overview: CRD availability | Q137 | Q137 |
| Unit 9 — eBPF networking and Cilium overview: encryption boundary | Q138 | Q138 |
| Unit 9 — eBPF networking and Cilium overview: cluster-wide policy | Q139 | Q139 |
| Unit 9 — eBPF networking and Cilium overview: WSL2 constraints | Q140 | Q140 |
| Unit 9 — eBPF networking and Cilium overview: FQDN/L7 | Q141 | Q141 |
| Unit 9 — eBPF networking and Cilium overview: performance | Q142 | Q142 |
| Unit 10 — Network troubleshooting: DNS, latency and packet loss: methodology | Q143 | Q143 |
| Unit 10 — Network troubleshooting: DNS, latency and packet loss: curl timing | Q144 | Q144 |
| Unit 10 — Network troubleshooting: DNS, latency and packet loss: ICMP | Q145 | Q145 |
| Unit 10 — Network troubleshooting: DNS, latency and packet loss: ss retransmits | Q146 | Q146 |
| Unit 10 — Network troubleshooting: DNS, latency and packet loss: interface drops | Q147 | Q147 |
| Unit 10 — Network troubleshooting: DNS, latency and packet loss: TCP handshake | Q148 | Q148 |
| Unit 10 — Network troubleshooting: DNS, latency and packet loss: conntrack | Q149 | Q149 |
| Unit 10 — Network troubleshooting: DNS, latency and packet loss: MTU | Q150 | Q150 |
| Unit 10 — Network troubleshooting: DNS, latency and packet loss: traceroute | Q151 | Q151 |
| Unit 10 — Network troubleshooting: DNS, latency and packet loss: DNS policy | Q152 | Q152 |
| Unit 10 — Network troubleshooting: DNS, latency and packet loss: diagnostic toolbox | Q153 | Q153 |
| Unit 10 — Network troubleshooting: DNS, latency and packet loss: kubectl debug | Q154 | Q154 |
| Unit 10 — Network troubleshooting: DNS, latency and packet loss: HTTP status | Q155 | Q155 |
| Unit 10 — Network troubleshooting: DNS, latency and packet loss: latency statistics | Q156 | Q156 |
| Unit 10 — Network troubleshooting: DNS, latency and packet loss: pcap hygiene | Q157 | Q157 |
| Unit 10 — Network troubleshooting: DNS, latency and packet loss: timeout ladder | Q158 | Q158 |
| Unit 10 — Network troubleshooting: DNS, latency and packet loss: Hubble | Q159 | Q159 |
| Unit 10 — Network troubleshooting: DNS, latency and packet loss: debug restrictions | Q160 | Q160 |
| Unit 10 — Network troubleshooting: DNS, latency and packet loss: runbook | Q161 | Q161 |
| Unit 10 — Network troubleshooting: DNS, latency and packet loss: transport symptoms | Q162 | Q162 |
| Unit 10 — Network troubleshooting: DNS, latency and packet loss: tc netem | Q163 | Q163 |
| Unit 10 — Network troubleshooting: DNS, latency and packet loss: postmortem | Q164 | Q164 |
| Cross-unit architecture and capstone: capstone path | Q165 | Q165 |
| Cross-unit architecture and capstone: internal dependencies | Q166 | Q166 |
| Cross-unit architecture and capstone: policy acceptance | Q167 | Q167 |
| Cross-unit architecture and capstone: ETL egress | Q168 | Q168 |
| Cross-unit architecture and capstone: canary | Q169 | Q169 |
| Cross-unit architecture and capstone: streaming acceptance | Q170 | Q170 |
| Cross-unit architecture and capstone: mTLS authorization | Q171 | Q171 |
| Cross-unit architecture and capstone: mesh choice | Q172 | Q172 |
| Cross-unit architecture and capstone: Cilium fallback | Q173 | Q173 |
| Cross-unit architecture and capstone: rollback | Q174 | Q174 |
| Cross-unit architecture and capstone: secrets | Q175 | Q175 |
| Cross-unit architecture and capstone: SLO | Q176 | Q176 |
| Cross-unit architecture and capstone: evidence | Q177 | Q177 |
| Cross-unit architecture and capstone: TLS boundaries | Q178 | Q178 |
| Cross-unit architecture and capstone: source limits | Q179 | Q179 |
| Cross-unit architecture and capstone: reproducibility | Q180 | Q180 |
| Cross-unit architecture and capstone: readiness vs SLO | Q181 | Q181 |
| Cross-unit architecture and capstone: negative tests | Q182 | Q182 |
| Cross-unit architecture and capstone: telemetry correlation | Q183 | Q183 |
| Cross-unit architecture and capstone: resource budget | Q184 | Q184 |
| Module prerequisites, safety, evidence and source/version discipline | Q001, Q008, Q014, Q024, Q041, Q063, Q081, Q107, Q131, Q154, Q165, Q178 | Same IDs; confirm source availability notes and human verification appendix |

## Appendix B — Claim and Source Register

| Claim ID | Question ID(s) | Claim or answer dependency | Source document + section | Confidence | Tag |
|---|---|---|---|---|---|
| C001 | Q001–Q016 | Pod/node/Service IP, namespaces, CNI responsibilities and networking trade-offs | Unit 1 lesson §§1.2–1.9; syllabus Unit 1 | Source-supported concepts; implementation varies | [VERIFY] CNI-specific topology |
| C002 | Q017–Q034 | Service types, targetPort, EndpointSlices, DNS/search, kube-proxy and conntrack | Unit 2 lesson §§2.3–2.6; Kubernetes Services/DNS docs named in syllabus | Source-supported concepts | [VERSION-SENSITIVE] datapath mode |
| C003 | Q035–Q052 | Ingress/controller boundary, Gateway API resources, status, route behavior | Unit 3 lesson §§3.3–3.6; syllabus Unit 3 | Source-supported concepts | [VERIFY] CRDs/controller |
| C004 | Q053–Q066 | L4/L7 load balancing, externalTrafficPolicy, NAT and draining | Unit 4 lesson §§4.3–4.6; syllabus Unit 4 | Source-supported concepts | [VERIFY] provider behavior |
| C005 | Q067–Q082 | NetworkPolicy selection/enforcement, DNS egress and least privilege | Unit 5 lesson §§5.3–5.9; Kubernetes NetworkPolicy docs named in syllabus | Source-supported concepts | [VERIFY] CNI enforcement |
| C006 | Q083–Q098 | TLS identity/chain/SNI, cert-manager lifecycle and key protection | Unit 6 lesson §§6.3–6.9; cert-manager docs named in syllabus | Source-supported concepts | [VERSION-SENSITIVE] cert-manager API |
| C007 | Q099–Q112 | Mesh control/data plane, sidecars, Linkerd selected path and Istio comparison | Unit 7 lesson §§7.3–7.9; syllabus Unit 7 | Source-supported; selected lesson uses Linkerd sidecar mode | [VERIFY] release/commands |
| C008 | Q113–Q130 | mTLS, traffic shifting, retries, circuit breakers and timeout budgets | Unit 8 lesson §§8.3–8.9; syllabus Unit 8 | Source-supported concepts | [VERIFY] mesh policy/API |
| C009 | Q131–Q142 | eBPF/Cilium/Hubble, kube-proxy replacement, policy extensions | Unit 9 lesson §§9.2–9.9; syllabus Unit 9 | Awareness-level concepts; feature support conditional | [VERIFY] kernel/CRDs |
| C010 | Q143–Q164 | Evidence-first troubleshooting, DNS, curl timing, packet capture, MTU and incident response | Unit 10 lesson §§10.2–10.14; syllabus Unit 10 | Source-supported concepts; no lab execution claimed | [VERIFY] tool/kernel availability |
| C011 | Q165–Q184 | Secure ingress/mTLS capstone integration and acceptance evidence | Uploaded practice prompt and syllabus capstone themes; detailed project file unavailable | Assessment-design inference where exact project detail is missing | [OPEN — SOURCE GAP] |

**Source note:** this register points to the accessible lesson sections and the available syllabus prompt. It is not a claim that every version-specific official page was live-checked during this authoring pass. Consult the current official docs for installed versions before executing implementation-specific steps.

## Appendix C — Audit Report

| Pass | Result | Defects found / fixes applied | Residual risk or follow-up |
|---|---|---|---|
| 1. Source fidelity | PASS WITH LIMITATION | Preserved roadmap unit order, available lessons and Linkerd sidecar assumption. | Exact prompt pack and detailed capstone files unavailable. |
| 2. Coverage completeness | PASS WITH LIMITATION | Questions cover Units 1–10, cross-unit safety and capstone themes listed in the uploaded prompt. | Capstone-specific requirements cannot be verified without project file. |
| 3. Count/distribution | PASS | Question IDs are continuous; count and category tags are generated from the question records. | Human review should confirm question quality and level assignment. |
| 4. Answer-key integrity | PASS | Every question record generates a matching answer heading using the same ID. | Answers are model answers; reviewers may accept equivalent evidence-based responses. |
| 5. Technical correctness | PASS WITH LIMITATION | Avoided universal claims for CNI/controller/mesh/kernel behavior; emphasized evidence and conditional branches. | Live execution and external source validation not performed. |
| 6. Version/currency | PASS WITH LIMITATION | Version-sensitive APIs, controllers, CRDs and tools are explicitly conditional/`[VERIFY]`. | Human must verify installed version and current official docs. |
| 7. Security/safety | PASS | No public/third-party probing required; local-only mutation, least privilege, capture hygiene and rollback emphasized. | Learner must enforce guards when doing optional labs. |
| 8. Pedagogical validity | PASS WITH LIMITATION | Mixed formats, L1–L4 tags, scenario/path/defect flags and explanations included. | Human curriculum review recommended for ambiguity and difficulty calibration. |
| 9. Cross-consistency | PASS | Blueprint, question IDs, answers, remediation, coverage and claim register generated from the same records. | Source-specific capstone acceptance mapping remains open. |
| 10. Adversarial final review | PASS WITH LIMITATION | No fabricated lab outputs/benchmarks or claim of live testing; source gaps disclosed. | Manual review and learner-run validation remain required. |

## Appendix D — Human Verification Checklist

| Area | What to check | Official documentation / safe validation |
|---|---|---|
| Kubernetes / CNI | Check cluster version, CNI name/version, Pod CIDRs, IPAM and kernel/runtime support | consult Kubernetes networking docs and the selected CNI's official compatibility/install docs; validate in disposable kind cluster or read-only inventory. |
| CoreDNS / kube-proxy | Inspect actual DNS deployment/Corefile, resolver path, Service datapath mode and EndpointSlices | consult Kubernetes DNS, Services and kube-proxy docs; run bounded exact-name DNS and Service tests. |
| Ingress / Gateway API | Check controller presence/class, Gateway API CRDs and installed versions, supported route/status fields and controller maintenance/security status | consult current controller docs and Gateway API conformance docs; test local route and backend. |
| Load balancer | Verify local LB helper/provider, `externalTrafficPolicy`, source-IP path and health checks | consult the provider/controller docs; use local-only requests and document kind fidelity limits. |
| NetworkPolicy | Verify the CNI enforces policy and inspect labels/selectors, DNS egress and allowed/denied paths | consult Kubernetes NetworkPolicy docs and CNI docs; use disposable namespace and positive/negative tests. |
| cert-manager / TLS | Check cert-manager version, Certificate/Issuer API and renewal behavior | consult cert-manager docs; test local CA, SNI, SAN, expiry and chain without public ACME or real credentials. |
| Service mesh | Verify selected Linkerd release/Kubernetes compatibility, injection, policy API and CLI commands | consult official Linkerd docs; measure baseline/meshed behavior only if resources allow. Istio is comparison unless source assumptions are intentionally changed. |
| Cilium / eBPF | Verify kernel/host support, Cilium release, installed CRDs, kube-proxy replacement and Hubble availability | consult official Cilium docs; use awareness/read-only alternative if unsupported. |
| Troubleshooting tools | Verify curl timing variables, `tcpdump`, `ss`, `iproute2`, `nstat`, `conntrack` and `tc` availability/syntax | consult installed man pages, official kernel/iproute2 docs and distribution docs; avoid privileged mutation unless scope and rollback are known. |
| Capstone source | Locate and inspect `Projects/README.md` and `Projects/01-secure-ingress-and-mtls-for-data-and-ml-apis.md` | compare exact acceptance criteria with this assessment and update only after source review. |

## Appendix E — Sign-off

- **Content status:** DRAFT-AUDITED
- **Audit date:** 2026-10-28
- **Auditor:** AI self-audit (human verification required)
- **Question count:** 184
- **Scenario-tagged questions:** 43
- **Packet/request-path questions:** 153
- **Defect-finding questions:** 22
- **Unresolved items count:** 3 major source/environment groups (exact prompt pack unavailable; detailed capstone files unavailable; no live version/lab verification performed), plus component-specific `[VERIFY]` items.

An AI self-audit is not a substitute for running labs on the learner's own throwaway kind cluster or checking current official documentation. The bank was authored and structurally checked, but commands, manifests, live controllers and labs were not executed. No other repository file was modified by this generation step.

