# Unit 5 — Network Policies and zero-trust segmentation

**Target file:** `05-network-policies-and-zero-trust-segmentation.md` | **Module:** M04 | **Stage:** 2E  
**Estimated time:** 12–16 hours  
**Prerequisites:** Linux/TCP-IP/DNS/HTTP fundamentals; Kubernetes Pods, Services, namespaces, Deployments, probes, and M03 rollout operations; M01 images and M02 CI/CD.  
**Core tools:** `kubectl`, `kind`, Docker, `curl`, `getent`/`nslookup` where installed, shell, YAML editor, and the chosen CNI's official diagnostics.  
**Awareness tools:** Cilium/Hubble, Calico flow visibility and policy extensions, policy schema/lint tools, policy simulators, service-mesh authorization.  
**Last reviewed:** 2026-10-28 (authoring date; no live upstream verification performed).  
**Verification status:** Reasoned review only; not executed. CNI compatibility, install commands, CNI-specific diagnostics, `endPort` support, and vendor-policy features require current official-document verification.

## Table of Contents

- [5.0 Why this matters in production](#50-why-this-matters-in-production)
- [5.1 Learning objectives](#51-learning-objectives)
- [5.2 Concept map and vocabulary](#52-concept-map-and-vocabulary)
- [5.3 Level 1 — Beginner: Foundations](#53-level-1--beginner-foundations)
- [5.4 Level 2 — Intermediate: Working Practice](#54-level-2--intermediate-working-practice)
- [5.5 Level 3 — Advanced: Production Engineering](#55-level-3--advanced-production-engineering)
- [5.6 Level 4 — Expert: Operating at Scale and Under Failure](#56-level-4--expert-operating-at-scale-and-under-failure)
- [5.7 SRE lens](#57-sre-lens)
- [5.8 Security lens](#58-security-lens)
- [5.9 Production checklist](#59-production-checklist)
- [5.10 Hands-on lab set](#510-hands-on-lab-set)
- [5.11 Self-check questions](#511-self-check-questions)
- [5.12 Evidence artifacts](#512-evidence-artifacts)
- [5.13 Common interview and design-review questions](#513-common-interview-and-design-review-questions)
- [5.14 Sources and verification notes](#514-sources-and-verification-notes)
- [Appendix A — Claim Register](#appendix-a--claim-register)
- [Appendix B — Audit Report](#appendix-b--audit-report)
- [Appendix C — Human Verification Checklist](#appendix-c--human-verification-checklist)
- [Appendix D — Known Limitations and Assumptions](#appendix-d--known-limitations-and-assumptions)
- [Appendix E — Sign-off](#appendix-e--sign-off)

## 5.0 Why this matters in production

A default-deny policy can stop DNS and prevent a model API from resolving its feature service or completing startup dependencies. A compromised workload may move laterally to Redis or Postgres if network paths are not deliberately constrained. An ETL worker with unrestricted egress can reach destinations that its business role does not require, while an operator may falsely believe it is isolated because a `NetworkPolicy` object exists. NetworkPolicy is effective only when the network implementation enforces it, so policy intent must be tested with real allowed and denied flows.

## 5.1 Learning objectives

- **L1:** Explain packet direction, namespace/pod selectors, and default NetworkPolicy behavior; capture baseline and post-policy evidence in Lab A.
- **L1/L2:** Verify whether the active CNI actually enforces NetworkPolicy using positive and negative tests, rather than relying on API objects; complete Lab A.
- **L2:** Implement default-deny ingress/egress, DNS UDP/TCP 53, and the API-to-feature-service path with consistent selectors; complete Lab B.
- **L2:** Build a source × destination × port allow/deny matrix test that fails on unexpected results and saves a readable report; complete Lab C.
- **L2/L3:** Diagnose a deliberately removed DNS allowance, restore it, and prove recovery; complete Lab D.
- **L3:** Defend a zero-trust segmentation design that covers app dependencies, metrics scraping, and ETL egress limitations; complete Lab E.
- **L3/L4:** Explain the limits of `ipBlock`, NAT, `hostNetwork`, metadata/API-server paths, probes, webhooks, and mesh authorization.
- **L4:** Design policy-as-code validation, ephemeral-cluster tests, namespace-label governance, drift detection, scoped rollback, and exception ownership.

## 5.2 Concept map and vocabulary

### Flow model before YAML

```text
Source workload/namespace
    -> destination workload/namespace
    -> destination port + protocol
    -> purpose + owner
    -> expected allow/deny
    -> positive/negative test + retained evidence
```

Example intended flow inventory:

| Source | Destination | Protocol/port | Purpose | Expected result |
|---|---|---|---|---|
| `ingress-system` controller Pods | `ml-api` Pods in `ml-platform` | TCP/8080 | External route forwards to model API | Allow |
| `ml-api` Pods | `feature-service` Pods | TCP/8081 | Feature lookup | Allow |
| `ml-api` Pods | `postgres` Pods | TCP/5432 | Model metadata/data dependency, if used | Allow only if required |
| `feature-service` Pods | `redis` Pods | TCP/6379 | Feature cache | Allow only if required |
| `metrics-system` scraper Pods | API metrics endpoint | TCP/9090 | Scraping | Allow |
| `etl-worker` Pods | local mock egress service | TCP/8080 | Controlled egress exercise | Allow only to intended test peer |
| `etl-worker` Pods | unrelated application Pods | TCP/8081 | Not part of ETL contract | Deny |
| Any selected workload | CoreDNS Pods | UDP/53 and TCP/53 | Name resolution | Allow |

### Glossary

| Term | Definition | Common misconception |
|---|---|---|
| NetworkPolicy | Namespaced Kubernetes API object expressing L3/L4 ingress and/or egress rules for selected Pods | Creating the object proves packets are filtered |
| Policy-enforcing CNI | Network implementation that enforces Kubernetes NetworkPolicy semantics | Every CNI or kind default setup enforces policy |
| Pod selector | Selects Pods in the policy's namespace when used as `spec.podSelector` | A label selector selects Services by name |
| Namespace selector | Selects namespaces by labels | It selects a namespace by its display name unless the name label is present |
| Peer | Source/destination selection in an ingress/egress rule | A peer always means a single Pod |
| Default-deny | Policy selecting a Pod and declaring an ingress/egress direction with no allowed rules for that direction | It blocks every possible host/control-plane path on every CNI |
| Additive allow | For a direction, traffic allowed by any applicable NetworkPolicy allow rule is allowed | Standard NetworkPolicy has a global deny-overrides rule order |
| `ipBlock` | CIDR-based peer selection with optional exclusions | It is a portable FQDN policy or behaves identically across every NAT path |
| `policyTypes` | Declares ingress and/or egress isolation directions for the selected Pods | It is an ordered priority list |
| `endPort` | Optional upper port bound for a port range where supported | It is safe to assume every older cluster/CNI supports it |
| Egress | Traffic initiated from a selected Pod toward a destination | Ingress policy alone controls outbound connections |
| Ingress | Traffic arriving at a selected Pod | Allowing egress from a source automatically allows traffic to an isolated destination |
| CNI | Container Network Interface plugin(s) implementing pod networking and potentially policy | CNI identity alone proves a particular feature is enabled |
| `hostNetwork` | Pod shares the host network namespace | Ordinary Pod-level NetworkPolicy necessarily isolates all its host traffic |
| Service mesh authorization | Mesh-specific identity and/or L7 policy, depending on implementation | NetworkPolicy provides user identity or HTTP path authorization |

### Policy selection and evaluation

```text
For a given destination Pod:
  Does any NetworkPolicy select the Pod for ingress?
    No  -> Kubernetes NetworkPolicy does not isolate ingress for this Pod.
    Yes -> ingress is isolated; only ingress flows allowed by applicable rules pass.

For a given source Pod:
  Does any NetworkPolicy select the Pod for egress?
    No  -> Kubernetes NetworkPolicy does not isolate egress for this Pod.
    Yes -> egress is isolated; only egress flows allowed by applicable rules pass.

For each direction:
  allowed flows = union of flows permitted by all applicable policies.
  Standard NetworkPolicy has no portable ordered deny-overrides evaluation.
```

An ingress rule is evaluated at the destination Pod; an egress rule is evaluated at the source Pod. For a connection from A to B, both ends' applicable isolation rules matter: A's egress must permit the destination and B's ingress must permit the source. Return traffic for an allowed connection is stateful in standard NetworkPolicy semantics, but details involving NAT, node/host paths, and implementation-specific datapaths must be verified with the selected CNI.

### Selector semantics that frequently cause security bugs

- `spec.podSelector: {}` selects all Pods in the NetworkPolicy's own namespace.
- A missing/omitted `podSelector` is not the same as an explicit empty selector; the API requires a pod selector for a NetworkPolicy, and an empty selector is a valid “all Pods in this namespace” selection.
- A peer with both `namespaceSelector` and `podSelector` in the **same peer object** means namespaces matching the namespace selector **AND** Pods matching the pod selector within those namespaces.
- Separate peer list entries are alternatives (**OR**): a matching namespace peer OR a matching pod peer can satisfy the rule.
- Namespace names are not automatically labels. Kubernetes commonly labels namespaces with `kubernetes.io/metadata.name`; verify that label exists before using it in policy.
- Namespace labels and workload labels are security inputs. Only trusted automation/operators should be able to mutate labels that grant access.

## 5.3 Level 1 — Beginner: Foundations

### What NetworkPolicy does—and does not do

Kubernetes NetworkPolicy describes which connections are permitted for selected Pods at the IP/port/protocol layer. It is not an authentication system, workload identity system, TLS configuration, HTTP authorization engine, WAF, or universal host firewall. Whether a policy is enforced depends on the network implementation. The API can accept a policy even if the active datapath ignores it.

**[ASSUMPTION] CNI for this lesson:** no established M04 CNI choice is confirmed in the supplied prompt context. The lesson therefore plans two separate `kind` environments: first, a disposable default-kind-networking demonstration to observe whether the default path enforces policy; second, a new disposable cluster using a documented, policy-enforcing CNI. The recommended enforcement-lab candidate is **Calico**, subject to current kind/Kubernetes compatibility and installation verification. Do not treat this recommendation as a verified current compatibility statement. Do not replace the CNI in a working cluster.

Official entry points:
- Kubernetes NetworkPolicy: https://kubernetes.io/docs/concepts/services-networking/network-policies/
- kind: https://kind.sigs.k8s.io/docs/
- Project Calico documentation: https://docs.tigera.io/calico/latest/

Current install manifests, versions, compatibility matrix, and kind integration are `[VERIFY: consult the exact Calico release's official installation instructions and supported-platform matrix before use]`. No install command is intentionally guessed here.

### A first reachability test

Use only a disposable `kind` cluster and local-only HTTP traffic. This initial lab phase is read-only with respect to cluster configuration; create a fresh cluster only after confirming Docker/kind resource availability.

**Lab A, Phase A — baseline default-CNI behavior**

- **Goal:** Compare actual traffic behavior before and after creating a NetworkPolicy under the cluster's current/default networking.
- **Prerequisites:** Docker, kind, kubectl, curl; no public endpoint.
- **Context guard:** the example cluster name is `m04-u5-default`. After creating it, require the context to be exactly `kind-m04-u5-default`.
- **Resource estimate:** 2 tiny Pods; approximately a small fraction of the 8 GB RAM budget, but actual image/runtime usage varies.
- **Steps:** create a fresh cluster using the installed kind version's official documented procedure; assert context; create the test namespace/workloads below; prove reachability; apply a restrictive policy; repeat the same request.
- **Expected output (example — yours will differ):** before-policy request returns HTTP 200. After-policy request may still succeed if the active CNI does not enforce NetworkPolicy. This is a platform observation, not a failed learner task.
- **Interpretation:** the existence of a policy object is not enforcement evidence. If the policy blocks traffic, record the actual CNI and its configuration rather than assuming default behavior.
- **Evidence:** current context, `kubectl get nodes`, CNI Pods/config, baseline and post-policy request results, policy YAML, events.
- **Pass criteria:** state whether enforcement was demonstrated and cite packet/request evidence.
- **Cleanup:** delete the namespace and test cluster; verify cluster name no longer appears in `kind get clusters`.
- **Stretch goal:** repeat on a fresh cluster with the verified policy-enforcing CNI in Phase B.
- **Cannot prove:** production CNI performance, cloud policy behavior, or host/metadata isolation.

Create `manifests/network-policy/baseline-test.yaml`:

```yaml
# File: manifests/network-policy/baseline-test.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: policy-baseline
---
apiVersion: v1
kind: Pod
metadata:
  name: source
  namespace: policy-baseline
  labels:
    app: source
spec:
  containers:
    - name: client
      image: curlimages/curl:8.10.1
      command: ["sh", "-c", "sleep 36000"]
      resources:
        requests:
          cpu: 10m
          memory: 16Mi
        limits:
          cpu: 100m
          memory: 64Mi
---
apiVersion: v1
kind: Pod
metadata:
  name: destination
  namespace: policy-baseline
  labels:
    app: destination
spec:
  containers:
    - name: server
      image: hashicorp/http-echo:1.0.0
      args: ["-listen=:8080", "-text=destination-ok"]
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
---
apiVersion: v1
kind: Service
metadata:
  name: destination
  namespace: policy-baseline
spec:
  selector:
    app: destination
  ports:
    - name: http
      port: 8080
      targetPort: http
```

The image tags are examples; check source, current security posture, architecture, and pin a reviewed digest before using in a durable environment `[VERIFY]`. For the lesson's basic lab, these Pods have no credentials and no external exposure.

Read-only guard and apply:

```bash
kubectl config current-context
kind get clusters
```

Before any mutation, confirm the selected cluster is the disposable one:

```bash
kubectl config current-context | grep -Fx 'kind-m04-u5-default'
```

If the assertion fails, stop. Then:

```bash
kubectl apply -f manifests/network-policy/baseline-test.yaml
kubectl wait -n policy-baseline --for=condition=Ready pod/source --timeout=120s
kubectl wait -n policy-baseline --for=condition=Ready pod/destination --timeout=120s
kubectl exec -n policy-baseline source -- curl --connect-timeout 2 --max-time 4 -sS -i http://destination:8080/
```

**Expected output (example — yours will differ):** HTTP 200 and body `destination-ok`. The Service DNS name is namespace-local. If it fails, first check Pod readiness, endpoints, and DNS; do not interpret an unverified baseline failure as policy enforcement.

Create `manifests/network-policy/baseline-deny-destination.yaml`:

```yaml
# File: manifests/network-policy/baseline-deny-destination.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-destination-ingress
  namespace: policy-baseline
spec:
  podSelector:
    matchLabels:
      app: destination
  policyTypes:
    - Ingress
  ingress: []
```

Apply and retest:

```bash
kubectl apply -f manifests/network-policy/baseline-deny-destination.yaml
kubectl get networkpolicy -n policy-baseline
kubectl exec -n policy-baseline source -- curl --connect-timeout 2 --max-time 4 -sS -i http://destination:8080/
```

**Expected output (example — yours will differ):** if the current CNI enforces NetworkPolicy, the request should fail or time out; if it does not, it may still return HTTP 200. Record which result occurred and identify the actual CNI. `kubectl get networkpolicy` only proves the API object exists.

### What just happened?

The API stored a rule selecting the destination Pod and isolating its ingress with no allowed ingress peers. A policy-enforcing datapath should deny new ingress connections to that Pod unless another applicable policy allows them. If traffic continues, the policy may not be enforced by the active network implementation. The correct response is to verify CNI identity/configuration and repeat on a supported enforcement CNI—not to add more YAML and assume the network is secure.

### Beginner mistakes

| Symptom | Likely cause | Safe fix |
|---|---|---|
| Policy exists but traffic still succeeds | CNI does not enforce NetworkPolicy or enforcement is not active | Verify CNI docs/config and test in a fresh compatible cluster |
| DNS fails after default-deny egress | No UDP/TCP 53 allow rule to actual DNS Pods | Discover DNS Pods/labels and add scoped rules |
| Rule selects no Pods | Label or namespace mismatch | Inspect `kubectl get pods --show-labels` and policy selectors |
| Expected deny test returns connection refused immediately | Destination server/port may not be listening; this does not prove policy denial | Check endpoints and server logs, then use a known-good baseline |
| Positive flow fails after allow rule | Wrong source selector, destination selector, namespace label, port, or protocol | Inspect both endpoints and test each direction |
| Broad namespace label grants access | Label is treated as a security boundary but is mutable | Restrict label mutation and test namespace-label changes |

## 5.4 Level 2 — Intermediate: Working Practice

### Shared namespace/workload contract

All manifests below use this contract:

| Namespace | Labels | Workloads | Ports/purpose |
|---|---|---|---|
| `ingress-system` | `kubernetes.io/metadata.name=ingress-system` (verify) | ingress/gateway controller | TCP/80 listener in a lab controller if installed |
| `ml-platform` | `kubernetes.io/metadata.name=ml-platform`, `security.example.com/zone=application` | `model-api`, `feature-service`, `etl-worker` | API TCP/8080, feature TCP/8081, ETL local mock TCP/8080 |
| `data-store` | `kubernetes.io/metadata.name=data-store`, `security.example.com/zone=data` | `postgres`, `redis` | TCP/5432, TCP/6379 |
| `metrics-system` | `kubernetes.io/metadata.name=metrics-system`, `security.example.com/zone=observability` | Prometheus-like scraper | scraper initiates TCP/9090 to selected metrics endpoint |
| `kube-system` | existing cluster labels | CoreDNS Pods | DNS UDP/53 and TCP/53; discover actual labels/ports |

The `security.example.com/zone` labels are illustrative policy inputs. Namespace names and label values must be verified in the lab. The well-known `kubernetes.io/metadata.name` namespace label is commonly applied by Kubernetes, but inspect the actual namespace labels before relying on it.

**Important:** the controller policy below assumes the controller Pods carry `app.kubernetes.io/name: ingress-controller` in `ingress-system`. That label is a contract for this lesson, not a claim about every controller chart. Verify and adjust the selector to the installed controller's actual labels. If no ingress controller is installed, use a dedicated local test client with the same intended source label for the policy lab; do not expose it externally.

### Discover DNS and workload labels before policy

```bash
kubectl get pods -n kube-system --show-labels
kubectl get svc -n kube-system
kubectl get ns --show-labels
kubectl get pods -A --show-labels
```

**Expected output (example — yours will differ):** CoreDNS Pods and their actual labels/namespace, namespace labels, and workload labels. If CoreDNS runs in a different namespace or uses different labels, update the policy peer to match the observed deployment.

### Default-deny and minimum allow policies

The following policies are split by workload responsibility to keep the allowed flows auditable. Apply them only after the CNI-enforcement lab has passed. They assume all listed namespaces and Pods exist and the label contract above is applied.

Create `manifests/network-policy/namespace-labels.yaml`:

```yaml
# File: manifests/network-policy/namespace-labels.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ml-platform
  labels:
    security.example.com/zone: application
---
apiVersion: v1
kind: Namespace
metadata:
  name: data-store
  labels:
    security.example.com/zone: data
---
apiVersion: v1
kind: Namespace
metadata:
  name: metrics-system
  labels:
    security.example.com/zone: observability
---
apiVersion: v1
kind: Namespace
metadata:
  name: ingress-system
  labels:
    security.example.com/zone: ingress
```

Do not use this file to overwrite labels on pre-existing production namespaces. It is intended for a fresh disposable cluster. If the namespaces already exist, inspect and apply labels via an approved, scoped operation.

Create `manifests/network-policy/default-deny.yaml`:

```yaml
# File: manifests/network-policy/default-deny.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: ml-platform
spec:
  podSelector: {}
  policyTypes:
    - Ingress
  ingress: []
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-egress
  namespace: ml-platform
spec:
  podSelector: {}
  policyTypes:
    - Egress
  egress: []
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: data-store
spec:
  podSelector: {}
  policyTypes:
    - Ingress
  ingress: []
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-egress
  namespace: data-store
spec:
  podSelector: {}
  policyTypes:
    - Egress
  egress: []
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: metrics-system
spec:
  podSelector: {}
  policyTypes:
    - Ingress
  ingress: []
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-egress
  namespace: metrics-system
spec:
  podSelector: {}
  policyTypes:
    - Egress
  egress: []
```

**Important direction detail:** a namespace-level default-deny egress policy selects every Pod in that namespace and isolates its egress. It does not automatically deny ingress to a destination in a different namespace; the destination namespace's ingress policy governs that end of the flow. Both sides need compatible rules for the connection to succeed.

### DNS allowance — UDP and TCP port 53

Discover CoreDNS's actual namespace/labels first. The following policy assumes CoreDNS Pods in `kube-system` have `k8s-app: kube-dns`; verify before applying.

Create `manifests/network-policy/allow-dns.yaml`:

```yaml
# File: manifests/network-policy/allow-dns.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns-egress
  namespace: ml-platform
spec:
  podSelector: {}
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
          podSelector:
            matchLabels:
              k8s-app: kube-dns
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
```

The `namespaceSelector` and `podSelector` are in the same peer object, so they combine with AND semantics: destination Pods must match `kube-system` and `k8s-app=kube-dns`. If the actual DNS Pods use different labels or namespace, change the selectors based on discovery. This rule allows DNS egress from all Pods in `ml-platform`; tighten `podSelector` if only some workloads require it.

If policies isolate egress in `data-store` or `metrics-system` and those workloads need DNS, add equivalent namespace-scoped DNS policies there. Do not assume an allow in `ml-platform` covers Pods in another namespace.

### Allow ingress controller → model API

Create `manifests/network-policy/allow-ingress-to-api.yaml`:

```yaml
# File: manifests/network-policy/allow-ingress-to-api.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-ingress-controller-to-model-api
  namespace: ml-platform
spec:
  podSelector:
    matchLabels:
      app: model-api
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: ingress-system
          podSelector:
            matchLabels:
              app.kubernetes.io/name: ingress-controller
      ports:
        - protocol: TCP
          port: 8080
```

This permits TCP/8080 to `model-api` Pods from matching controller Pods in `ingress-system`. It does not create an ingress controller, configure an Ingress/Gateway route, permit client traffic to the controller, or allow other sources to the API. Verify the controller's actual Pod labels and the API's actual listening port.

### Allow model API → feature service

Create `manifests/network-policy/allow-api-to-feature.yaml`:

```yaml
# File: manifests/network-policy/allow-api-to-feature.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-model-api-to-feature
  namespace: ml-platform
spec:
  podSelector:
    matchLabels:
      app: feature-service
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: model-api
      ports:
        - protocol: TCP
          port: 8081
```

Because the peer contains only a `podSelector`, it selects `model-api` Pods in the same namespace as the policy. This is destination ingress policy. The source API's egress must also be permitted if its egress is isolated; the DNS rule alone does not permit TCP/8081.

Create `manifests/network-policy/allow-api-egress-to-feature.yaml`:

```yaml
# File: manifests/network-policy/allow-api-egress-to-feature.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-model-api-egress-to-feature
  namespace: ml-platform
spec:
  podSelector:
    matchLabels:
      app: model-api
  policyTypes:
    - Egress
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: feature-service
      ports:
        - protocol: TCP
          port: 8081
```

### Allow application → Postgres/Redis

These are examples of narrowly scoped dependencies; only keep flows that the actual app requires. This contract uses API → Postgres and feature service → Redis.

Create `manifests/network-policy/allow-data-store-ingress.yaml`:

```yaml
# File: manifests/network-policy/allow-data-store-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-model-api-to-postgres
  namespace: data-store
spec:
  podSelector:
    matchLabels:
      app: postgres
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: ml-platform
          podSelector:
            matchLabels:
              app: model-api
      ports:
        - protocol: TCP
          port: 5432
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-feature-service-to-redis
  namespace: data-store
spec:
  podSelector:
    matchLabels:
      app: redis
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: ml-platform
          podSelector:
            matchLabels:
              app: feature-service
      ports:
        - protocol: TCP
          port: 6379
```

The same peer combines namespace and Pod selector with AND semantics. The `ml-platform` source Pods need corresponding egress allowances to the `data-store` namespace on TCP/5432 or TCP/6379. For example, create `manifests/network-policy/allow-app-egress-to-data.yaml`:

```yaml
# File: manifests/network-policy/allow-app-egress-to-data.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-model-api-to-postgres-egress
  namespace: ml-platform
spec:
  podSelector:
    matchLabels:
      app: model-api
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: data-store
          podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-feature-service-to-redis-egress
  namespace: ml-platform
spec:
  podSelector:
    matchLabels:
      app: feature-service
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: data-store
          podSelector:
            matchLabels:
              app: redis
      ports:
        - protocol: TCP
          port: 6379
```

### Metrics scraping

For the lab contract, the scraper initiates TCP/9090 to an explicitly labeled API metrics endpoint. This is an illustrative port contract, not a default Prometheus port. The model API Deployment must expose a listener on 9090 for this flow to work; if it does not, change the port and policy to match the actual metrics endpoint.

Create `manifests/network-policy/allow-metrics-scrape.yaml`:

```yaml
# File: manifests/network-policy/allow-metrics-scrape.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-scraper-to-api-metrics
  namespace: ml-platform
spec:
  podSelector:
    matchLabels:
      app: model-api
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: metrics-system
          podSelector:
            matchLabels:
              app: metrics-scraper
      ports:
        - protocol: TCP
          port: 9090
```

This policy does not deploy a scraper or metrics listener. Verify scraper labels and target port; also verify whether the metrics collector's own egress is isolated and needs DNS or other rules.

### ETL egress restriction: portable policy versus FQDN

Standard Kubernetes NetworkPolicy does not provide portable FQDN/hostname-based peers. Do not write `to: - dnsName: api.example.com` in a standard NetworkPolicy. For the zero-budget lab, ETL calls a local mock Service, and a policy permits only that local destination. Real production egress to changing public IPs requires a separate design such as a CNI-specific FQDN-aware policy, a controlled egress proxy/gateway, or firewall/NAT controls. Each is implementation-specific and must be reviewed against current docs.

Create `manifests/network-policy/allow-etl-to-mock.yaml`:

```yaml
# File: manifests/network-policy/allow-etl-to-mock.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-etl-to-local-mock
  namespace: ml-platform
spec:
  podSelector:
    matchLabels:
      app: etl-worker
  policyTypes:
    - Egress
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: mock-external-api
      ports:
        - protocol: TCP
          port: 8080
```

The mock is in the same namespace in this example. This rule permits ETL egress only to the selected local mock on TCP/8080, plus any other flows allowed by other applicable egress policies (including DNS). It does not express a public hostname allowlist.

### Flow matrix

| Source | Destination | Port/protocol | Expected result under the complete contract | Reason |
|---|---|---|---|---|
| Ingress controller in `ingress-system` | `model-api` in `ml-platform` | TCP/8080 | Allow | Explicit API ingress + source match |
| Unrelated Pod in `ml-platform` | `model-api` | TCP/8080 | Deny | Not an allowed ingress peer |
| `model-api` | `feature-service` | TCP/8081 | Allow | Source egress and destination ingress rules |
| `feature-service` | `model-api` | TCP/8080 | Deny unless separately required | No reverse flow rule |
| `model-api` | `postgres` in `data-store` | TCP/5432 | Allow | Explicit DB egress and ingress rules |
| `feature-service` | `redis` in `data-store` | TCP/6379 | Allow | Explicit cache egress and ingress rules |
| `etl-worker` | local mock in `ml-platform` | TCP/8080 | Allow | Explicit local mock egress |
| `etl-worker` | unrelated Pod in `ml-platform` | TCP/8081 | Deny | No matching allow rule |
| Workload in `ml-platform` | CoreDNS | UDP/53 | Allow if DNS labels match | Explicit DNS egress |
| Workload in `ml-platform` | CoreDNS | TCP/53 | Allow if DNS labels match | TCP fallback/large-response behavior |
| `metrics-scraper` | model API metrics listener | TCP/9090 | Allow if listener and selectors exist | Explicit scraper ingress rule |
| Arbitrary external IP | any selected app Pod | any | Deny unless another applicable rule/path allows it | Default-deny plus explicit allow-list; NAT/host path caveats remain |

### Positive and negative tests

A test result is meaningful only if the baseline flow is known to work and the destination is listening. Use the test Pods and mock workloads created for the lab; do not probe third-party systems.

Commands for discovery:

```bash
kubectl get pods -A --show-labels
kubectl get svc -A
kubectl get endpointslices -A
kubectl get networkpolicy -A
```

**Expected output (example — yours will differ):** workload labels, Service/EndpointSlice state, and policy list. This is setup evidence, not enforcement proof. Follow it with positive and negative connection attempts.

### `endPort`, IP blocks, NAT, and host-level caveats

`endPort` can express a port range in API versions/implementations that support it. It is not required for this lesson's exact-port policies. Verify API schema and selected CNI support before using a range `[VERIFY]`.

`ipBlock` is CIDR-based and does not resolve DNS names. Traffic may be subject to Service translation, Pod/node NAT, routing, or provider-specific processing that changes which address a policy sees. The Kubernetes docs warn that behavior around Service IP translation and `ipBlock` can vary by network implementation. Do not assume `ipBlock` reliably blocks all host-level, metadata, or API-server access.

Kubelet probes, node-originated traffic, admission webhooks, metrics collectors, `hostNetwork` Pods, and control-plane/API-server paths may not follow a simple ordinary Pod-to-Pod path. Verify the actual CNI documentation and test in a safe cluster. Vanilla NetworkPolicy is not a universal host firewall.

### Anti-patterns

| Anti-pattern | Why it is dangerous | Safer alternative |
|---|---|---|
| Apply default-deny without DNS allow | Breaks service discovery and external hostname resolution | Add verified UDP/TCP 53 rule and test recovery |
| Treat API object existence as enforcement | CNI may ignore policy | Prove allowed and denied traffic on the actual CNI |
| Allow all ports from an entire namespace | Label drift or new Pods can widen access | Use stable governed labels and least-privilege port rules |
| Put a hostname into standard `ipBlock` | Invalid semantics; IPBlock is CIDR, not FQDN | Use controlled egress proxy or verified CNI-specific feature |
| Assume a policy deny overrides all allows | Standard NetworkPolicy allows are additive | Review the union of applicable policies and vendor-specific semantics separately |
| Trust mutable namespace labels | A label change can expand the peer set | RBAC/admission controls, code review, drift detection |
| Assume policy protects host/metadata endpoints | Host-level and NAT paths have caveats | Add platform-specific controls and verify residual paths |
| Use NetworkPolicy as authentication | L3/L4 reachability is not user/workload identity | Add TLS, application authn/authz, and mesh identity policy where appropriate |

## 5.5 Level 3 — Advanced: Production Engineering

### Zero-trust segmentation as an operating model

Zero trust is not a YAML pattern. For each flow, define the caller, destination, protocol/port, purpose, owner, identity requirements, and verification evidence. NetworkPolicy provides a useful L3/L4 reachability layer; application authentication, TLS, service-mesh identity/authorization, host protections, and egress controls address different trust boundaries.

Recommended rollout sequence:

1. **Observe:** inventory current flows using app logs, CNI flow visibility if supported, and bounded connection tests. Do not infer a complete inventory from a single capture.
2. **Audit:** map each observed flow to a business purpose and owner; identify unexplained flows and DNS/probe/webhook dependencies.
3. **Stage:** add policies to a non-critical namespace/workload; verify CNI enforcement and positive/negative tests.
4. **Enforce:** introduce default-deny in small scopes, with required DNS and application paths included before isolation.
5. **Monitor:** watch policy test failures, DNS failures, application errors, scrape gaps, and support incidents.
6. **Review:** revisit after workload/label/port changes; expire temporary exceptions.

### Trade-off table

| Option | Benefit | Cost | Risk | Choose when |
|---|---|---|---|---|
| Namespace-level default-deny plus explicit allow | Clear baseline and small blast radius | Requires flow inventory and maintenance | Missing a required path can cause outage | Workloads have known dependencies and ownership |
| Broad namespace allow | Simple initial connectivity | Weak segmentation and large trust domain | Lateral movement and label drift | Only as a time-bounded migration step with an explicit removal plan |
| Vanilla NetworkPolicy for in-cluster L3/L4 | Portable API model across supporting CNIs | No portable FQDN or L7 identity rules | NAT/host-level edge cases | Requirements are IP/port/protocol based |
| CNI-specific FQDN/L7 policy | Can express richer egress/application rules | Vendor coupling and feature/version constraints | False confidence if DNS/proxy path differs | Feature is supported, documented, tested, and operationally owned |
| Egress proxy/gateway | Central egress logging, policy, and stable controls | Additional hop, capacity, availability, and TLS complexity | Proxy outage or bypass path | Public egress destinations are dynamic and must be governed |
| Mesh authorization | Identity-aware and possibly L7 access control | Sidecar/ambient architecture and operational complexity | Mesh policy and NetworkPolicy can disagree | Workload identity and L7 authorization are required |
| Policy-as-code CI | Repeatable review and regression protection | Test environment and maintenance | Static validation can miss datapath behavior | Policies change frequently or many teams share a cluster |

### Namespace and label governance

- Treat `security.example.com/zone` and any namespace label used in an allow rule as security-sensitive.
- Grant permission to mutate these labels only to the platform/team responsible for namespace provisioning.
- Create namespaces from reviewed templates with default-deny and baseline allow rules; verify the template before workload admission.
- Require owners and purpose for exceptions; give exceptions an expiry/review date.
- Detect selector drift and policy deletion through GitOps reconciliation, cluster audits, and tests.
- Avoid policy selectors that match arbitrary labels users can freely set to gain access.
- Review namespace creation and label changes as security-sensitive changes, not merely metadata edits.

### Egress, DNS, and data/AI workload design

For the FastAPI model API, allow only feature-service and required database paths. Keep Postgres, Redis, and metrics endpoints internal. The ETL worker's public API access is the difficult case: DNS resolves a hostname to changing addresses, while standard NetworkPolicy peers are Pod/namespace selectors or CIDRs. A static CIDR allowlist may be brittle and provider-dependent. Prefer a governed egress proxy/gateway or a verified CNI-specific FQDN feature when business requirements justify it. Also evaluate metadata endpoints and Kubernetes API-server access separately; vanilla NetworkPolicy may not block all node/host paths.

### Probes, webhooks, and scraping

A readiness/liveness/startup probe can originate from kubelet/node context or follow a runtime/CNI-specific path. A default-deny ingress policy may therefore interact differently with probes than with ordinary Pod-to-Pod requests. Admission webhooks and metrics scrapers also initiate connections along paths that may not match the application's main flow. For each path, record source, destination, protocol/port, and evidence. Test in the chosen CNI and do not add broad node CIDRs until the path is understood.

### Policy-as-code and analyzers

Recommended CI stages:

1. YAML parse and Kubernetes schema validation against the target API version.
2. Policy lint and selector/namespace consistency checks.
3. Unit-style policy intent tests for every required allow and deny.
4. Ephemeral-cluster test using the same CNI family/version as the target environment.
5. Positive and negative packet tests to prove enforcement.
6. Drift comparison between version-controlled manifests and live policy objects.
7. Owner approval for changes to namespace labels, default-deny, egress, and exceptions.
8. A scoped rollback procedure and test evidence retained with the change.

Static analyzers can reveal selector overlap or unintended paths but do not replace live enforcement tests. Cilium/Hubble and Calico policy/flow tools are implementation-specific awareness examples; verify current command names, feature support, and license/installation details before use. `AdminNetworkPolicy` and `BaselineAdminNetworkPolicy` are version/maturity-sensitive and must not be assumed available in every cluster.

### Defended design lab — Lab E

- **Goal:** Recommend a policy architecture for the model API, feature service, Postgres/Redis, ETL worker, ingress controller, and metrics scraper.
- **Prerequisites:** Labs A–D, flow matrix, no cloud account.
- **Context guard:** design-only; no cluster mutation required.
- **Resource estimate:** no additional resources.
- **Steps:** fill a flow inventory with owner/purpose; compare vanilla NetworkPolicy, CNI-specific FQDN/L7 policy, egress proxy, and mesh authorization; state what each control does and does not enforce; write rollout/rollback and exception rules.
- **Expected output (example — yours will differ):** a short ADR and risk register; no numeric performance claims expected.
- **Interpretation:** a strong design separates network reachability from identity, TLS, application authorization, and host/metadata controls.
- **Evidence:** `architecture-decision-record.md`, flow inventory, policy matrix, unresolved verification items.
- **Pass criteria:** no hostname is misrepresented as a standard NetworkPolicy peer; internal services remain internal; owners and rollback are explicit.
- **Cleanup:** no resources created; ensure notes contain no credentials.
- **Stretch goal:** define CI gates and exception expiry automation.
- **Cannot prove:** actual CNI enforcement, provider egress behavior, or policy performance without implementation testing.

## 5.6 Level 4 — Expert: Operating at Scale and Under Failure

### Failure scenarios

| Symptom | Hypothesis | Test | Likely root cause | Mitigation | Prevention |
|---|---|---|---|---|---|
| DNS fails after default-deny | DNS egress rule absent or selector wrong | Resolve a known in-cluster Service; inspect actual CoreDNS Pods/labels and policy | Rule doesn't select DNS Pods, misses TCP/53, or is applied in wrong namespace | Restore verified DNS rule; retest resolution and app dependency | CI test for UDP/TCP DNS; namespace template includes DNS rule |
| Policy object exists but denied flow still works | CNI does not enforce policy or datapath is misconfigured | Run a known-good baseline and denied-flow test; inspect CNI identity/health | Default CNI or CNI configuration doesn't enforce NetworkPolicy | Stop rollout; use a verified policy-enforcing CNI in a disposable cluster | Preflight enforcement test; cluster admission/governance |
| API cannot reach feature service | Source egress or destination ingress missing; selector/port mismatch | Inspect both policies, labels, endpoints, and connection test | One side of the flow not allowed | Add the least-privilege rule in the correct namespace/direction | Automated source × destination × port matrix |
| Scrapes disappear | Metrics target port/labels wrong or scraper path isolated | Compare scrape target errors, Pod labels, listener, policy logs | Port mismatch or scraper selector not matching | Restore only the required scraper-to-target path | Include scraping in namespace onboarding tests |
| Namespace label drift widens access | A peer selector matches a changed namespace label | Compare live labels to Git; inspect RBAC/audit history | Unauthorized or accidental label mutation | Restore reviewed label and re-test; preserve audit evidence | Restrict label mutation and add drift alerts |
| New CNI release changes enforcement | Compatibility/regression in CNI datapath | Run pre/post upgrade policy suite and inspect CNI status/logs | Version/config regression | Roll back using documented CNI procedure; avoid in-place improvisation | Staged upgrades and ephemeral-cluster CI |
| Policy applied to wrong namespace | Manifest namespace or context incorrect | Inspect current context, object namespace, selectors, and audit log | Wrong context or copied manifest | Stop changes, revert only the known incorrect object with approved change control | Mandatory context guards and CI namespace assertions |
| ETL cannot reach external hostname | DNS blocked, no FQDN-aware policy, egress proxy/CIDR mismatch | Test local DNS path and local mock; inspect policy and egress route | Vanilla policy cannot match hostname or required DNS is blocked | Restore DNS; route through approved egress proxy or verified CNI-specific policy | Document egress owner and destination policy |
| Readiness/webhook behavior breaks | Node/control-plane path differs from ordinary Pod traffic | Inspect events/webhook logs and test the real source path | Policy assumes Pod-to-Pod semantics | Add only a verified required path or adjust architecture | Test probes/webhooks before enforcement |
| Metadata/API server remains reachable | Host-level or pre/post-NAT path outside assumed policy | Use authorized platform-specific tests; inspect CNI docs and cloud controls | NetworkPolicy doesn't cover the relevant host path | Apply platform firewall/IMDS controls and least-privilege workload identity | Threat model metadata/API server separately |

### Policy-as-code, namespace vending, and fleet governance

- **Namespace vending:** create namespaces from a reviewed template, attach stable security labels, apply default-deny and required baseline rules, and run positive/negative smoke tests before admitting workloads.
- **Policy-as-code:** require versioned YAML, schema validation, linting, policy-intent tests, owner review, and an ephemeral CNI-backed enforcement test.
- **Drift detection:** compare live policy objects and labels against desired state; alert on policy deletion, unexpected namespace labels, and out-of-band changes.
- **Failure containment:** begin with one workload or namespace; avoid global default-deny changes without staged validation and an approved rollback.
- **Ownership:** platform team owns CNI capability and baseline templates; service team owns flow purpose and application ports; security owns threat-model review and exception requirements; SRE owns indicators, incident response, and recovery evidence.
- **Change strategy:** pin CNI versions; verify compatibility in a disposable cluster; preserve manifests and current configuration; deploy in stages; define rollback triggers; capture before/after policy tests.
- **Emergency rollback:** restore the specific last-known-good policy or label. Do not delete every NetworkPolicy cluster-wide as an unreviewed response. A temporary scoped allow may be used only with approval, expiry, and audit evidence.

## 5.7 SRE lens

### Measurable indicators

| Signal | Numerator / denominator | Window and collection | Notes |
|---|---|---|---|
| Allowed-path success ratio | Successful requests/connections for intended allowed flows / all attempts for those flows | Fixed test window; matrix-test output and application logs | Exclude infrastructure setup failures from policy assertions but record them separately |
| Denied-path assertion success | Denied test cases that are actually blocked / all valid denied test cases | Each CI run or defined test window | A refused connection caused by a dead server is not proof of policy enforcement |
| DNS success ratio | Successful resolutions / all controlled DNS test attempts from isolated workloads | Lab run or service-owner-defined window | Test both UDP and TCP behavior where feasible |
| Policy test pass rate | Passing expected allow/deny cases / all valid policy cases executed | Per change and rolling release window | Include test suite version and CNI version |
| Unapproved communication paths | Observed/confirmed flows without an owner or documented purpose | Review window and flow-inventory source | Flow visibility may be incomplete |
| Time to detect/recover | Defined incident start to alert; alert to verified recovery | Incident timeline | Define timestamps consistently and distinguish mitigation from permanent fix |

Do not prescribe numeric SLO targets without service requirements and a measured baseline. Derive SLOs from user impact, criticality, acceptable error budget, and dependency expectations. A policy rollout can consume the application availability error budget even if the CNI itself is healthy.

### Blast radius

A default-deny policy in a shared namespace can break multiple applications, DNS, scraping, and startup. A bad namespace selector can allow lateral movement across tenants. A CNI regression can affect the whole cluster. A label mutation may widen access without changing any NetworkPolicy YAML. Keep policies scoped, changes staged, and rollback ownership clear.

### Incident runbook: default-deny blocks DNS

**Alert:** model API startup or requests fail after a policy rollout; logs show name-resolution errors.

1. **Triage:** record time, namespace, policy change, current context, affected Pods, DNS errors, and CNI health.
2. **Discriminate:** from an authorized debug Pod, test DNS resolution; inspect actual CoreDNS namespace/labels; check whether the workload's egress is isolated and whether UDP and TCP 53 rules match. Confirm that the destination DNS Pod is reachable and ready.
3. **Mitigate:** restore the last-known-good scoped DNS allow rule or revert the specific policy change under the approved process. Do not delete all policies as a first action.
4. **Validate:** resolve the intended in-cluster Service, test API → feature service, and rerun both allow and deny matrix cases.
5. **Follow-up:** add a DNS regression test, selector check, policy owner, and deployment checklist entry.

## 5.8 Security lens

| Threat / trust boundary | Control | Residual risk |
|---|---|---|
| Lateral movement from compromised Pod | Default-deny ingress/egress plus explicit flow allowlist | Allowed ports remain reachable; app vulnerabilities still matter |
| Unauthorized ingress to model API | Destination ingress policy restricted to verified controller identity/labels | Labels are not cryptographic identity; controller compromise still matters |
| Unauthorized egress from ETL | Allow only local mock in lab; production egress proxy/CNI-aware policy/firewall | Vanilla NetworkPolicy has no portable FQDN matching |
| DNS tunneling/abuse | Restrict DNS sources/destinations where feasible; monitor resolver behavior | NetworkPolicy cannot inspect DNS query contents portably |
| Metadata endpoint access | Cloud/platform IMDS controls, workload identity, host firewall, CNI-specific protections | Vanilla NetworkPolicy may not block host-level/pre-NAT paths |
| Kubernetes API-server access | RBAC, service-account token minimization, API network controls, workload identity | NetworkPolicy alone is not API authorization and may not cover all paths |
| Mutable namespace/pod labels | RBAC/admission controls, code review, drift detection | Trusted operator or automation can still make mistakes |
| Overly broad selectors | Selector linting and flow matrix tests | A correct selector can become broad as labels change |
| `hostNetwork` or privileged workloads | Pod Security, admission controls, node hardening, CNI-specific host policy | Ordinary Pod policy may not isolate host network traffic |
| Non-enforcing CNI | Preflight positive/negative enforcement tests and supported CNI configuration | API objects can create false confidence |
| Webhook/probe/scraper disruption | Explicit source-path inventory and pre-enforcement tests | Source path may change across runtime/CNI upgrades |
| Policy bypass via alternate route | Threat-model NAT, host, node, Service, and external paths | Vanilla policy is not a complete perimeter firewall |

NetworkPolicy does **not** provide authentication, workload identity, L7 authorization, encryption, WAF behavior, complete host/metadata isolation, or complete egress governance. Use TLS and application authentication, mesh authorization where appropriate, workload identity, node/host controls, and egress gateways as complementary layers. M09 owns secrets/identity details; M12 owns supply-chain/security controls.

## 5.9 Production checklist

- [ ] Policy-enforcing CNI and version are identified and verified; enforcement was demonstrated with positive and negative tests.
- [ ] Flow inventory lists source, destination, protocol/port, purpose, owner, expected result, and evidence.
- [ ] Default-deny policies are applied in a scoped rollout after baseline dependencies are inventoried.
- [ ] DNS selectors match actual DNS Pods/namespaces and allow both UDP and TCP port 53 where needed.
- [ ] Every policy's `podSelector`, `namespaceSelector`, peer combination, `policyTypes`, port, and direction are reviewed.
- [ ] Controller, API, feature service, database/cache, metrics scraper, and ETL flows are explicitly tested.
- [ ] Probes, webhooks, node/control-plane-originated traffic, and metrics scraping are verified in the selected environment.
- [ ] ETL design does not claim vanilla NetworkPolicy supports FQDN rules.
- [ ] `ipBlock`, NAT, `hostNetwork`, metadata, and API-server limitations are documented and covered by appropriate platform controls.
- [ ] Namespace labels used for access are governed by RBAC/admission and monitored for drift.
- [ ] Positive and negative matrix tests run in CI or an ephemeral cluster with the target CNI family/version.
- [ ] CNI upgrades are staged and followed by policy enforcement tests.
- [ ] Policy deletion/label drift has detection, owner, and response steps.
- [ ] Exceptions have purpose, owner, approval, expiry/review date, and compensating controls.
- [ ] Rollback restores a scoped last-known-good policy and preserves audit evidence.
- [ ] SLI denominators, windows, alert ownership, runbook, and error-budget impact are documented.
- [ ] All lab namespaces, Pods, policies, scripts, and throwaway clusters are removed.

## 5.10 Hands-on lab set

Five labs are described. The labs are **not executed** in this authoring session. Current CNI installation and compatibility must be verified before Phase B; do not run an unverified installation command. The primary enforcement candidate is Calico under the labelled assumption in §5.3.

### Lab A — Does this CNI enforce NetworkPolicy?

- **Goal:** Demonstrate baseline reachability, then apply a restrictive policy and observe whether traffic is actually blocked.
- **Prerequisites:** Docker, kind, kubectl, curl; reviewed image tags.
- **Context guard:** after creating the disposable cluster, assert `kind-m04-u5-default`; if context differs, stop.
- **Resource estimate:** 2 small Pods; resource use varies with image cache and host.
- **Steps:** apply `baseline-test.yaml`; wait for both Pods; run the baseline curl; apply `baseline-deny-destination.yaml`; repeat the same curl; record the CNI identity/config and results.
- **Expected output (example — yours will differ):** baseline returns `destination-ok`; after policy, a policy-enforcing CNI should block the request, while a non-enforcing default setup may still allow it.
- **Interpretation:** only a known-good baseline plus changed behavior and CNI evidence demonstrates enforcement in this test.
- **Evidence:** context, nodes, CNI identity/Pods, YAML, policy object, before/after curl output.
- **Pass criteria:** state the observed result and its limits; do not infer enforcement from `kubectl get networkpolicy`.
- **Cleanup:** `kubectl delete namespace policy-baseline --wait=true`; delete the cluster; verify `kind get clusters` no longer lists it.
- **Stretch:** repeat on the fresh enforcement cluster in Lab B.
- **Cannot prove:** production CNI performance or host/metadata protection.

### Lab B — Policy-enforcing CNI, default-deny, and DNS

- **Goal:** Create a fresh cluster with a verified policy-enforcing CNI and prove default-deny behavior plus DNS allowance.
- **Prerequisites:** Lab A evidence; current official CNI/kind docs; sufficient disk/RAM.
- **Context guard:** create a separate cluster named `m04-u5-enforce`; assert `kind-m04-u5-enforce`. Do not replace CNI in a working cluster.
- **Resource estimate:** 2 workload Pods plus CNI components; CNI footprint varies and may be significant on an 8 GB laptop. Check vendor minimums first and close other heavy containers.
- **Steps:** verify supported Kubernetes version and official installation path; create a fresh cluster using the CNI's documented kind procedure; apply CNI; wait for all CNI components to be healthy; rerun baseline/deny test; apply default-deny and DNS policy after discovering DNS labels; test in-cluster Service DNS over the normal resolver path.
- **Expected output (example — yours will differ):** CNI components ready; known-good flow allowed before policy; denied flow blocked after policy; DNS lookup succeeds after the verified DNS rule is applied.
- **Interpretation:** a passing policy test proves only the tested flow/path in this environment. If CNI health is uncertain, mark the lab blocked and do not proceed to app segmentation.
- **Evidence:** version matrix, official install reference, cluster config, CNI status/logs, before/after request and DNS results.
- **Pass criteria:** positive and negative traffic assertions pass on a verified enforcing CNI.
- **Cleanup:** remove test namespaces/policies; delete the dedicated cluster; verify absent from `kind get clusters`.
- **Stretch:** automate the test in a disposable CI job.
- **Cannot prove:** all CNI features, production performance, or cloud-specific host-path behavior.
- **⚠ DESTRUCTIVE:** deleting `m04-u5-enforce` deletes the entire disposable cluster. Read-only alternative: inspect it with `kubectl get all -A` and `kind get clusters` before deletion.

### Lab C — End-to-end segmentation and automated matrix

- **Goal:** Enforce the model API → feature service → database/cache paths, ingress-controller source, scraper path, and local ETL mock egress.
- **Prerequisites:** Lab B passed; verified CNI; a disposable cluster; a reviewed workload image set and test script.
- **Context guard:** require `kind-m04-u5-enforce`; capture a read-only inventory before applying policies.
- **Resource estimate:** small API/feature/mock/database/cache Pods and a scraper test Pod; keep the lab lean and avoid installing a full service mesh/Prometheus stack.
- **Steps:** create the namespaces and labels; deploy test workloads with stable labels and ports; verify all baseline flows; apply default-deny; apply DNS and minimum allow policies; run positive/negative matrix tests; record every case.
- **Expected output (example — yours will differ):** intended flows succeed and prohibited flows time out/fail under enforcement; test report marks each expected result and observed result.
- **Interpretation:** if a negative test fails because the server is down, classify it as an infrastructure/test error, not a successful policy deny.
- **Evidence:** manifests, context, endpoint state, policy list, matrix report, application logs, CNI flow evidence where supported.
- **Pass criteria:** all intended cases pass; all denied cases are blocked for a demonstrated policy reason; no result is fabricated.
- **Cleanup:** delete only the lab namespaces and temporary scripts; confirm no Pods/policies remain, then delete the disposable cluster when finished.
- **Stretch:** add schema/lint checks and run the test in CI.
- **Cannot prove:** external FQDN enforcement using vanilla NetworkPolicy or complete metadata/API-server isolation.

### Lab D — Break DNS deliberately and recover

- **Goal:** Demonstrate a DNS outage caused by a missing egress allowance and prove recovery.
- **Prerequisites:** Lab B/C complete; DNS policy currently allows both UDP/TCP 53; verified CNI.
- **Context guard:** assert `kind-m04-u5-enforce` and confirm the exact DNS policy name/namespace before mutation.
- **Resource estimate:** no new workload if existing test Pods are available.
- **Steps:** save the current DNS policy; run a successful DNS query; delete only the lab DNS policy; repeat query with a timeout; inspect policy and DNS labels; reapply the saved policy; rerun DNS and API-to-feature tests.
- **Expected output (example — yours will differ):** DNS succeeds before removal, fails or times out after removal when egress is isolated and the test depends on DNS, then succeeds after restoration.
- **Interpretation:** a DNS failure alone is not sufficient; verify the policy was the cause and that the resolver/Pods were healthy.
- **Evidence:** policy before/after, DNS output, events/logs, recovery output, timestamps.
- **Pass criteria:** failure and recovery are both reproducible and only the intended lab policy is changed.
- **Cleanup:** restore policy, verify DNS and allowed/denied matrix, delete lab namespace/policy resources.
- **Stretch:** test UDP and TCP resolver paths where tooling supports explicit transport selection.
- **Cannot prove:** all DNS tunneling detection or production resolver behavior.

### Lab E — Policy-as-code and drift

- **Goal:** Detect an incorrect selector or missing allow rule in validation/ephemeral enforcement tests.
- **Prerequisites:** Lab C matrix script, YAML parser/schema/lint tooling selected and version-pinned by the learner.
- **Context guard:** static validation is read-only; any cluster test must assert `kind-m04-u5-enforce`.
- **Resource estimate:** static lint requires little resource; ephemeral CNI cluster may consume meaningful laptop RAM/disk.
- **Steps:** store test copies in `evidence-m04-u5/`, not the repository; run YAML/schema validation; run positive/negative matrix; deliberately change a test copy's selector or remove one required allow rule; confirm CI/test exits non-zero; restore file and rerun.
- **Expected output (example — yours will differ):** lint may detect schema problems; the behavioral test should fail when a required path is broken. A linter alone may not detect a semantically wrong selector.
- **Interpretation:** static checks and live datapath checks detect different classes of errors.
- **Evidence:** tool/version output, before/after test copy, test exit code, report, drift comparison.
- **Pass criteria:** deliberate regression is caught and restored; production manifests remain untouched.
- **Cleanup:** remove temporary test copies and ephemeral cluster; verify no lab resources remain.
- **Stretch:** add namespace-label drift and exception-expiry checks.
- **Cannot prove:** all policy interactions or vendor-specific semantics.

### Automated source × destination × port matrix test

The following test design is intended for the local lab. It requires that the learner create a diagnostic client Pod with `app: policy-test-client` in `ml-platform` and a reachable `feature-service` on TCP/8081. It performs only bounded requests to an in-cluster Service. It distinguishes an expected deny from a test-infrastructure error by requiring a positive control to pass first. A failed connection is not classified as a policy deny unless the matching positive control succeeds and the test topology is known healthy.

Create `scripts/network-policy-matrix.sh`:

```bash
# File: scripts/network-policy-matrix.sh
#!/usr/bin/env bash
set -u

EXPECTED_CONTEXT="${EXPECTED_CONTEXT:-kind-m04-u5-enforce}"
NAMESPACE="${NAMESPACE:-ml-platform}"
CLIENT_POD="${CLIENT_POD:-policy-test-client}"
POSITIVE_URL="${POSITIVE_URL:-http://feature-service.ml-platform.svc.cluster.local:8081/health}"
NEGATIVE_URL="${NEGATIVE_URL:-http://model-api.ml-platform.svc.cluster.local:8080/health}"
TIMEOUT="${TIMEOUT:-3}"
OUT="${OUT:-network-policy-matrix.csv}"

current="$(kubectl config current-context 2>/dev/null || true)"
if [ "$current" != "$EXPECTED_CONTEXT" ]; then
  echo "ERROR: expected context '$EXPECTED_CONTEXT', got '$current'; refusing test" >&2
  exit 2
fi

if ! kubectl get pod "$CLIENT_POD" -n "$NAMESPACE" >/dev/null 2>&1; then
  echo "ERROR: test client Pod not found in $NAMESPACE" >&2
  exit 2
fi

printf 'case,source,destination,port,expected,observed,result\n' > "$OUT"

probe() {
  name="$1"; src="$2"; dst="$3"; port="$4"; expected="$5"; url="$6"
  if kubectl exec -n "$NAMESPACE" "$CLIENT_POD" -- \
       curl --connect-timeout "$TIMEOUT" --max-time "$TIMEOUT" \
       -sS -o /dev/null -w '%{http_code}' "$url" >/tmp/np-matrix-curl.out 2>/tmp/np-matrix-curl.err; then
    code="$(cat /tmp/np-matrix-curl.out)"
    if [ "$code" -ge 200 ] && [ "$code" -lt 400 ]; then observed="allow"; else observed="http-$code"; fi
  else
    rc=$?
    if grep -qiE 'Could not resolve|resolve host' /tmp/np-matrix-curl.err; then
      observed="dns-error"
    elif grep -qiE 'timed out|Failed to connect|Connection refused|No route to host' /tmp/np-matrix-curl.err; then
      observed="connect-failure"
    else
      observed="test-error-rc-$rc"
    fi
  fi

  if [ "$expected" = "allow" ] && [ "$observed" = "allow" ]; then result="PASS"
  elif [ "$expected" = "deny" ] && [ "$observed" = "connect-failure" ]; then result="PASS-CANDIDATE"
  else result="FAIL"
  fi

  printf '%s,%s,%s,%s,%s,%s,%s\n' "$name" "$src" "$dst" "$port" "$expected" "$observed" "$result" >> "$OUT"
  printf '%-24s expected=%-5s observed=%-20s result=%s\n' "$name" "$expected" "$observed" "$result"
}

# Positive control must pass before a connection failure can be interpreted as a policy deny.
probe "positive-feature-control" "policy-test-client" "feature-service" "8081/TCP" "allow" "$POSITIVE_URL"
if ! tail -n 1 "$OUT" | grep -q ',allow,allow,PASS$'; then
  echo "ERROR: positive control failed; deny assertions are inconclusive" >&2
  echo "Report: $OUT"
  exit 1
fi

probe "negative-api-path" "policy-test-client" "model-api" "8080/TCP" "deny" "$NEGATIVE_URL"

if grep -q ',FAIL$' "$OUT"; then
  echo "ERROR: one or more matrix cases failed; inspect $OUT and temporary curl diagnostics" >&2
  exit 1
fi

echo "Report: $OUT"
echo "Note: PASS-CANDIDATE is not proof by itself; corroborate with policy selectors, CNI enforcement evidence, and a known-good target."
```

**Important script limitation:** this starter script uses a fixed source Pod and two HTTP destinations, so it is not a full arbitrary multi-namespace matrix runner. Extend it only after the base case is validated. It writes a temporary diagnostic file under `/tmp`; inspect it only for lab use and remove it after the test. A production-grade CI test should use a unique temporary directory, trap cleanup, avoid fixed shared `/tmp` filenames, test each source identity/port explicitly, and classify expected denies only after the positive control and target health checks pass.

Blank matrix table — fill only with observed results:

| Source | Destination | Port/protocol | Expected | Observed | Pass/fail | Evidence |
|---|---|---|---|---|---|---|
| `policy-test-client` | `feature-service` | TCP/8081 | Allow | learner fills | learner fills | |
| `policy-test-client` | `model-api` | TCP/8080 | Deny | learner fills | learner fills | |
| `model-api` | `feature-service` | TCP/8081 | Allow | learner fills | learner fills | |
| `feature-service` | `redis` | TCP/6379 | Allow | learner fills | learner fills | |
| `etl-worker` | local mock | TCP/8080 | Allow | learner fills | learner fills | |
| `etl-worker` | unrelated service | TCP/8081 | Deny | learner fills | learner fills | |
| `ml-platform` workload | CoreDNS | UDP/53 and TCP/53 | Allow | learner fills | learner fills | |
| `metrics-scraper` | API metrics endpoint | TCP/9090 | Allow | learner fills | learner fills | |

### Cleanup and no-leftover-state check

For each lab, verify the exact context before deleting resources. A safe namespace cleanup for the disposable cluster is:

```bash
kubectl config current-context | grep -Fx 'kind-m04-u5-enforce'
kubectl get all -A
kubectl get networkpolicy -A
kubectl get namespaces
```

**Expected output (example — yours will differ):** resources and policies for the lab namespaces are listed. This is a read-only pre-delete inventory.

**⚠ DESTRUCTIVE — target: entire disposable cluster `m04-u5-enforce`.** This removes the cluster and all its resources. If you need a read-only alternative, keep the cluster and inspect the above output instead. Before deletion, assert the context again; then use the current kind documentation's cluster deletion command and verify the cluster is absent from `kind get clusters`. Do not remove CNI CRDs or shared cluster resources from any non-disposable cluster.

## 5.11 Self-check questions

1. **Does a `NetworkPolicy` object prove that packets are filtered?**  
   **Answer:** No. The active network implementation must support and enforce NetworkPolicy. Prove it with a known-good baseline plus positive and negative traffic tests. **Tempting wrong answer:** “`kubectl get networkpolicy` lists it, therefore traffic is blocked.” That only proves API state.

2. **What happens when no policy selects a Pod for ingress?**  
   **Answer:** Kubernetes NetworkPolicy does not isolate ingress for that Pod; other network controls can still block traffic. **Tempting wrong answer:** “All traffic is guaranteed reachable.” That ignores routes, firewalls, application listeners, and other controls.

3. **How do applicable NetworkPolicy allows combine?**  
   **Answer:** For a direction, allowed traffic is the union of rules across all applicable policies. Standard NetworkPolicy has no portable ordered deny-overrides mechanism. **Tempting wrong answer:** “A more specific deny always overrides a broad allow.” That is not the standard API's rule model.

4. **What is the meaning of a peer with both `namespaceSelector` and `podSelector` in the same object?**  
   **Answer:** The destination/source Pods must match the Pod selector and be in namespaces matching the namespace selector. **Tempting wrong answer:** “Either selector can match.” Separate peer list entries, not fields within one peer object, provide the OR alternative.

5. **Why can default-deny egress break DNS?**  
   **Answer:** DNS queries are egress traffic from the workload; a default-deny egress policy must be paired with an allow rule to the actual DNS Pods on UDP and TCP 53. **Tempting wrong answer:** “DNS is cluster infrastructure, so it bypasses policy.” That is not a portable assumption.

6. **Does an egress allow from A automatically allow ingress to isolated B?**  
   **Answer:** No. A's egress policy and B's ingress policy independently govern the connection. **Tempting wrong answer:** “Once A is allowed, B must accept it.” Destination ingress isolation still applies.

7. **Can vanilla NetworkPolicy allow a public hostname such as `api.example.com`?**  
   **Answer:** No portable FQDN peer exists in standard NetworkPolicy. Use verified CIDRs only where appropriate, a controlled egress proxy/gateway, or a documented CNI-specific capability. **Tempting wrong answer:** Putting a hostname in `ipBlock`; it expects CIDRs, not DNS names.

8. **What does `podSelector: {}` select?**  
   **Answer:** All Pods in the policy's namespace. **Tempting wrong answer:** “All Pods in the cluster.” NetworkPolicy is namespaced.

9. **Why is a connection refusal not enough to prove a policy deny?**  
   **Answer:** The target may be down, the port may not listen, or routing/DNS may fail. First prove the same path works before policy and confirm target health. **Tempting wrong answer:** Treating every failed curl as successful isolation.

10. **Does NetworkPolicy reliably block metadata endpoints and all `hostNetwork` traffic?**  
    **Answer:** No universal guarantee; NAT, host-level paths, runtime/CNI behavior, and platform implementation matter. Add platform-specific controls and verify the actual path. **Tempting wrong answer:** Assuming a Pod selector is a complete host firewall.

11. **Why test probes, webhooks, and metrics separately?**  
    **Answer:** Their traffic may originate from node or control-plane context and differ from ordinary Pod-to-Pod traffic. **Tempting wrong answer:** Assuming all requests share the same source identity/path.

12. **What does a policy simulator prove?**  
    **Answer:** It can analyze the model it understands, but it does not necessarily prove live packet enforcement. Verify simulator assumptions and run real tests on the chosen CNI. **Tempting wrong answer:** Treating a static graph as a live datapath test.

## 5.12 Evidence artifacts

Keep evidence under `evidence-m04-u5/` outside the repository. Never include credentials, tokens, customer data, or sensitive packet payloads.

- `environment-inventory.txt` — OS/WSL2/native Linux, Docker/kind/Kubernetes versions, current context, nodes, CNI identity/health, namespace labels.
- `default-cni-baseline.txt` — baseline connectivity, policy YAML, post-policy connectivity, and interpretation.
- `cni-compatibility.md` — chosen CNI version, official compatibility source, installation reference, known limitations.
- `cni-health.txt` — CNI Pods/status/log excerpts and enforcement proof.
- `namespace-labels.yaml` — test namespace labels used by selectors.
- `policies/` — exact test manifests applied, including default-deny, DNS, app/database/cache, metrics, and ETL rules.
- `positive-negative-matrix.csv` — source, destination, port/protocol, expected, observed, result, evidence.
- `dns-break-recovery.txt` — before/removal/after DNS outputs and policy snapshots.
- `selector-review.md` — actual labels and why each selector is scoped correctly.
- `flow-inventory.csv` — source, destination, port, purpose, owner, expected outcome, test.
- `ci-validation.txt` — schema/lint tool versions, command, exit status, and deliberate-regression result.
- `drift-review.md` — desired versus live policy/namespace-label state and remediation.
- `incident-timeline.md` — alert, triage, mitigation, recovery validation, follow-up.
- `cleanup-verification.txt` — context, resources/policies/namespaces removed, and cluster absence.
- `claim-register-review.md` — source links, resolved/unresolved `[VERIFY]` items.

## 5.13 Common interview and design-review questions

### 1. How do Kubernetes NetworkPolicy rules compose?

**Model answer:** A policy selects Pods in its namespace and isolates ingress and/or egress directions through `policyTypes` and rule presence. For an isolated direction, traffic is allowed if any applicable policy permits it; standard NetworkPolicy is additive and has no ordered deny-overrides semantics. A connection from source A to destination B must satisfy A's egress policy if isolated and B's ingress policy if isolated. CNI enforcement and NAT/host paths must be verified.

### 2. How do you prove a CNI enforces NetworkPolicy?

**Model answer:** Use a fresh disposable cluster and a known-good baseline connection. Apply a policy that selects the destination and denies the tested ingress, then repeat the same request while verifying the destination remains healthy. Inspect the CNI identity/configuration and its documented NetworkPolicy support. Run positive and negative tests and retain evidence. A policy object or static simulation alone is insufficient.

### 3. How would you roll out default-deny without causing an outage?

**Model answer:** Inventory flows and owners; verify the CNI; apply policies to a non-critical workload; add DNS over UDP/TCP 53 and all required app, probe, webhook, and scraper paths; test positive/negative cases; monitor application/DNS/scrape errors; expand scope gradually; and preserve a scoped rollback. Never start with an unreviewed cluster-wide policy change.

### 4. What are the limits of `ipBlock` and standard NetworkPolicy for egress?

**Model answer:** `ipBlock` expresses CIDRs, not hostnames. DNS results can change, and Service translation/NAT/host-level paths can affect which addresses are seen. Standard NetworkPolicy has no portable FQDN rule and is not a universal metadata/host firewall. Use verified CIDR controls only where stable, or a governed egress proxy/gateway or CNI-specific feature with explicit compatibility testing.

### 5. How do you combine NetworkPolicy and service-mesh authorization?

**Model answer:** NetworkPolicy is an L3/L4 reachability layer enforced by the CNI; a service mesh can add workload identity and L7 authorization/retries/mTLS depending on implementation. Use NetworkPolicy to constrain which workloads can communicate at the network level, then mesh/application controls for identity and request semantics. Test interactions and avoid assuming one layer overrides or replaces the other.

## 5.14 Sources and verification notes

This lesson was authored without live documentation browsing or cluster execution. URLs below are official entry points to verify; they are not a claim that current contents or versions were checked during authoring.

1. **Kubernetes Network Policies** — https://kubernetes.io/docs/concepts/services-networking/network-policies/  
   Standard API semantics, ingress/egress isolation, additive rules, selectors, `ipBlock`, and implementation caveats.
2. **Kubernetes NetworkPolicy API reference** — https://kubernetes.io/docs/reference/kubernetes-api/networking/network-policy-v1/  
   API fields and schema; verify the target cluster version and `endPort` support.
3. **kind documentation** — https://kind.sigs.k8s.io/docs/  
   Cluster lifecycle, configuration, and CNI installation considerations.
4. **Project Calico documentation** — https://docs.tigera.io/calico/latest/  
   Candidate policy-enforcing CNI; verify exact release, kind instructions, compatibility, and current install procedure.
5. **Cilium documentation** — https://docs.cilium.io/  
   Awareness of CNI-specific policy/flow visibility and FQDN/L7 features; not used by the mandatory lab unless separately selected and verified.
6. **Cilium Hubble documentation** — https://docs.cilium.io/en/stable/observability/hubble/  
   Flow visibility, version-specific capabilities and commands require verification.
7. **Kubernetes DNS debugging** — https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/  
   DNS troubleshooting and cluster-specific DNS discovery.
8. **Kubernetes probes** — https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/  
   Probe semantics; actual network path and policy interaction require CNI/runtime testing.
9. **Google SRE Book** — https://sre.google/sre-book/table-of-contents/  
   SLI/SLO, monitoring, incident response, and error-budget concepts.
10. **Kubernetes admission controllers** — https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/  
    Admission/webhook architecture; specific traffic path must be verified in the target environment.
11. **Cross-module M04 lessons:** [Unit 1](01-kubernetes-networking-model-cni-and-pod-networking.md), [Unit 2](02-services-kube-proxy-and-cluster-dns.md), [Unit 3](03-ingress-controllers-and-gateway-api.md), [Unit 4](04-load-balancers-and-external-traffic-management.md), [Unit 6](06-tls-termination-and-certificate-lifecycle-with-cert-manager.md), [Unit 8](08-mtls-traffic-shifting-retries-and-circuit-breaking.md), [Unit 9](09-network-policy-troubleshooting-and-observability.md), and [Unit 10](10-network-troubleshooting-dns-latency-and-packet-loss.md).

### Verification notes

| Item | What must be checked | Status |
|---|---|---|
| Default kind CNI policy enforcement | Identify the actual CNI and test known-good flow before/after policy | `[VERIFY]` local environment |
| Calico installation in kind | Exact version, supported Kubernetes versions, official kind procedure, resource needs | `[VERIFY]` current release |
| DNS namespace/labels | Discover actual DNS Pods and labels; verify namespace-name label | `[VERIFY]` cluster-specific |
| `endPort` | Target API schema and selected CNI support | `[VERSION-SENSITIVE]` |
| `ipBlock` and NAT | CNI documentation for Service/Pod translation and host paths | `[VERIFY]` implementation-specific |
| Probes/webhooks/scraping | Actual traffic source and policy interaction | `[VERIFY]` runtime/CNI-specific |
| Cilium/Calico-specific FQDN/L7/flow tools | Feature support, exact schema/CLI, maturity and version | `[VERIFY]` vendor-specific |
| AdminNetworkPolicy/BaselineAdminNetworkPolicy | API availability/maturity and implementation support | `[VERSION-SENSITIVE]` |
| Metadata/API-server isolation | Platform-specific network path and separate controls | `[VERIFY]` platform-specific |

## Appendix A — Claim Register

Confidence is about the general concept, not verification of the user's actual cluster/CNI version.

| ID | Claim | Source document + section/title | Confidence (High/Med/Low) | Tag |
|---|---|---|---|---|
| NP01 | A Pod not selected by a NetworkPolicy is not isolated in that direction by Kubernetes NetworkPolicy | Kubernetes Network Policies — default behavior | High | General; other controls still apply |
| NP02 | A CNI/network implementation must enforce policy for packet filtering to occur | Kubernetes Network Policies — prerequisites | High | `[VERIFY]` actual CNI |
| NP03 | NetworkPolicy is namespaced and selects Pods with `podSelector` | Kubernetes NetworkPolicy API reference | High | General |
| NP04 | For a direction, applicable NetworkPolicy allows combine additively | Kubernetes Network Policies — behavior | High | General; vendor policy APIs may differ |
| NP05 | Source egress and destination ingress isolation are independent | Kubernetes Network Policies — behavior | High | General |
| NP06 | Same peer's namespace and Pod selectors combine with AND semantics | Kubernetes NetworkPolicy API reference | High | General |
| NP07 | Separate peer list entries are alternative matches | Kubernetes NetworkPolicy API reference | High | General |
| NP08 | Standard NetworkPolicy uses CIDR `ipBlock`, not portable FQDN peers | Kubernetes Network Policies — `ipBlock` | High | General |
| NP09 | Service NAT and host-level paths can complicate `ipBlock` behavior | Kubernetes Network Policies — caveats | Med | `[VERIFY]` CNI/provider |
| NP10 | DNS may require UDP and TCP port 53 | Kubernetes DNS debugging; network protocol behavior | High | Verify actual DNS labels/path |
| NP11 | Default-deny egress can break DNS and application discovery | Kubernetes NetworkPolicy semantics; operational inference | High | General |
| NP12 | Probe/webhook/node-originated paths may differ from ordinary Pod-to-Pod traffic | Kubernetes probe/admission docs and CNI docs | Med | `[VERIFY]` runtime/CNI |
| NP13 | `endPort` support and semantics are API/version-sensitive | Kubernetes NetworkPolicy API reference | Med | `[VERSION-SENSITIVE]` |
| NP14 | `hostNetwork` and metadata/API-server paths are not universally blocked by vanilla NetworkPolicy | Kubernetes Network Policies — limitations; platform docs | High | `[VERIFY]` platform-specific controls |
| NP15 | Cilium FQDN/L7 features are implementation-specific | Cilium official docs | High | `[VERIFY]` feature/version |
| NP16 | Calico policy/flow capabilities are implementation-specific | Calico official docs | High | `[VERIFY]` feature/version |
| NP17 | AdminNetworkPolicy/BaselineAdminNetworkPolicy maturity/availability is not universal | Kubernetes API enhancement/docs | Med | `[VERSION-SENSITIVE]`; verify current status |
| NP18 | NetworkPolicy does not provide authentication or application-level authorization | Kubernetes Network Policies; security architecture | High | General |
| NP19 | Labels used by policy selectors are security-sensitive inputs | Kubernetes label selector semantics; security design | High | General |
| NP20 | A policy simulator does not necessarily prove live datapath enforcement | Tool documentation and test-design principle | High | `[VERIFY]` selected tool |
| NP21 | Namespace default-deny can create broad blast radius | NetworkPolicy semantics; SRE design inference | High | General |
| NP22 | CNI upgrade requires regression testing of policy behavior | CNI docs; operational recommendation | High | Engineering recommendation |
| NP23 | A local kind result does not establish cloud or production CNI behavior | kind and CNI documentation; environment boundary | High | General |
| NP24 | NetworkPolicy alone does not guarantee metadata endpoint isolation | Kubernetes/CNI/cloud platform docs | High | `[VERIFY]` actual platform |
| NP25 | DNS and application dependencies should be explicitly tested before enforcing default-deny | SRE rollout recommendation | High | Engineering recommendation |

## Appendix B — Audit Report

**Audit date:** 2026-10-28  
**Auditor:** AI self-audit (requires human verification)  
**Execution status:** **reasoned review only; not executed**

| Pass | Audit | Status (PASS/FIXED/OPEN) | Defects found | Fixes applied | Residual risk |
|---|---|---|---|---|---|
| 1 | Roadmap completeness | FIXED | Current CNI and exact lab setup are not established by this prompt alone | Added explicit CNI assumption, full required topics, five labs, and appendices | Must compare against complete roadmap/master syllabus |
| 2 | Technical accuracy | OPEN | Enforcement, NAT, probes, hostNetwork, and vendor features are implementation-specific | Added caveats, independent ingress/egress model, additive allow semantics, and verification gates | No live CNI/API validation performed |
| 3 | Executability | OPEN | Exact CNI installation and a fully general matrix runner cannot be finalized without a chosen, verified environment; sample workload contract still needs deployment verification | Added coherent example policies and context-guarded starter matrix script | Script covers only a small subset and requires local workload/port adaptation |
| 4 | Currency | OPEN | Current Calico compatibility, `endPort`, and AdminNetworkPolicy maturity were not checked live | Marked version-sensitive items `[VERIFY]` | Human must verify exact versions and schemas |
| 5 | Security correctness | FIXED | False confidence from YAML-only review and public FQDN claims are major risks | Required positive/negative tests; no public egress target; documented NetworkPolicy limits | Actual threat model and cluster paths need review |
| 6 | Fabrication scan | FIXED | Expected output and lab success could be mistaken for observed measurements | Marked outputs illustrative; no results fabricated; execution status explicit | Human must record real evidence |
| 7 | Pedagogy | PASS | None identified in section sequence | Packets/flow inventory precede YAML; L1–L4 progression included | Learner usability requires feedback |
| 8 | Cross-file consistency | OPEN | Exact shared CNI and full master syllabus were not independently inspected during this authoring pass | Cross-module boundaries and sibling references included | Verify file paths and roadmap contract |
| 9 | Adversarial review | OPEN | CNI enforcement and host/metadata paths remain unresolved without the actual platform | Added failure matrix, security threat table, runbook, and caveats | Human security/CNI review required |
| 10 | Lab safety/feasibility | FIXED | CNI replacement and wrong-context changes could disrupt a working cluster | Separate throwaway clusters, context guards, no host route changes, no public probing, scoped cleanup | Learner must verify resources and cluster context before mutation |

## Appendix C — Human Verification Checklist

### Kubernetes NetworkPolicy API and selectors
- [ ] Verify `networking.k8s.io/v1` schema and current docs: https://kubernetes.io/docs/reference/kubernetes-api/networking/network-policy-v1/
- [ ] Run `kubectl explain networkpolicy.spec`, `kubectl explain networkpolicy.spec.egress`, and `kubectl explain networkpolicy.spec.ingress` against the target cluster.
- [ ] Review each `podSelector`, `namespaceSelector`, peer list, `policyTypes`, protocol, and port; confirm AND/OR behavior.
- [ ] Verify `endPort` support before adding port ranges.

### kind configuration and selected CNI
- [ ] Record `kind version`, Docker version, Kubernetes node image/version, and `kubectl version`.
- [ ] Verify current official kind/CNI instructions and compatibility matrix.
- [ ] Identify actual CNI components/configuration and confirm NetworkPolicy enforcement support.
- [ ] Create a new disposable cluster for CNI installation; do not replace networking in a working cluster.

### CNI enforcement proof
- [ ] Run a known-good baseline request before policy.
- [ ] Apply a restrictive policy selecting the destination Pod and repeat the same request.
- [ ] Confirm the destination listener and endpoint are healthy.
- [ ] Record CNI identity/config and positive/negative results; do not use policy-object existence as proof.

### DNS namespace, labels, UDP/TCP
- [ ] Run `kubectl get pods -n kube-system --show-labels` and identify actual DNS Pods/labels/namespace.
- [ ] Verify `kubernetes.io/metadata.name` namespace labels exist before using them.
- [ ] Confirm egress rules allow both UDP/53 and TCP/53 where needed.
- [ ] Test DNS before policy, after default-deny, after allow rule, and after deliberate removal/recovery.

### `ipBlock`, NAT, hostNetwork, metadata/API server
- [ ] Read the chosen CNI's docs on `ipBlock`, Service translation, node traffic, `hostNetwork`, and pre/post-NAT policy evaluation.
- [ ] Verify platform-specific IMDS protections separately; do not rely on vanilla NetworkPolicy alone.
- [ ] Verify API-server access paths, ServiceAccount token use, and RBAC independently.

### `endPort` and current API behavior
- [ ] Check the target API reference and cluster schema for `endPort`.
- [ ] Test any port-range policy on the actual CNI; do not infer support from YAML acceptance alone.

### Probes, webhooks, metrics scraping
- [ ] Identify probe source/path for the chosen runtime/CNI and test under default-deny.
- [ ] Identify admission webhook source, destination, port, and control-plane/node path.
- [ ] Verify scraper Pod labels, metrics listener port, and egress/ingress policy on both sides.
- [ ] Include these tests before enforcing broad namespace policies.

### Policy-as-code and CI
- [ ] Pin YAML schema/lint tool versions and record exact commands.
- [ ] Run static checks plus ephemeral-cluster positive/negative tests.
- [ ] Deliberately break a test copy's selector/allow rule and confirm CI exits non-zero.
- [ ] Compare live policy and namespace labels to desired state; verify drift detection.

### Cilium/Calico awareness features
- [ ] For Calico, verify exact policy features and kind install instructions in the selected release docs.
- [ ] For Cilium, verify FQDN/L7 policy, Hubble, and command support for the exact release.
- [ ] Do not apply vendor-specific CRDs unless installed, version-verified, and explicitly in scope.

### AdminNetworkPolicy/BaselineAdminNetworkPolicy
- [ ] Check current Kubernetes API maturity/availability and implementation support.
- [ ] Verify CRD/API group, version, installation prerequisites, and policy semantics before using.
- [ ] Keep this lesson's baseline labs on standard `networking.k8s.io/v1` NetworkPolicy unless an explicitly verified extension is selected.

## Appendix D — Known Limitations and Assumptions

- **[ASSUMPTION] CNI:** no established M04 CNI is confirmed in the supplied prompt context. Calico is the proposed enforcement-lab candidate, but current kind compatibility, installation steps, and resource requirements have not been verified.
- The default kind networking path's NetworkPolicy behavior must be observed on the actual kind version and configuration; do not assume an API object is enforced.
- No CNI install, cluster creation, manifest application, DNS break/recovery, or matrix test was executed. All expected outputs are illustrative.
- The example image tags require source/security review and preferably digest pinning before reuse. Do not use these samples as a production image policy.
- The controller label `app.kubernetes.io/name: ingress-controller`, DNS label `k8s-app: kube-dns`, namespace labels, service ports, and metrics port 9090 are explicit example-contract assumptions; discover actual labels and listeners.
- The matrix script is a starter for a narrow local test, not a complete generalized test engine. Its negative-case classification requires a healthy positive control and corroborating CNI/policy evidence; test errors must not be mislabeled as denies.
- Vanilla NetworkPolicy has no portable FQDN rules and is not a universal host firewall. `ipBlock`, NAT, metadata/API-server paths, `hostNetwork`, probes, and control-plane/node traffic require platform-specific verification.
- Cilium/Calico-specific FQDN/L7/flow capabilities and AdminNetworkPolicy/BaselineAdminNetworkPolicy maturity are version-sensitive and are not required for the standard policy manifests here.
- kind/WSL2 behavior cannot establish production cloud behavior, policy performance, host security, or egress provider guarantees.
- Cross-module scope: M04 Units 1–4 cover network model, Services/DNS, ingress/Gateway routing, and load balancing; Unit 8 owns mesh authorization/mTLS/traffic controls; Units 9–10 own deeper network-policy and network troubleshooting/observability; M03 owns production operations/hardening; M06 Helm/Kustomize; M08 progressive delivery; M09 secrets/identity; M10 SLOs; M11 observability; M12 supply-chain/security; M14 multi-cluster networking; M15 egress/load-balancer cost.

## Appendix E — Sign-off

- **Content status:** `DRAFT-AUDITED`
- **Audit date:** 2026-10-28 (authoring date; live verification not performed)
- **Auditor:** `AI self-audit (requires human verification)`
- **Execution status:** `not executed` — reasoned review only; not executed.
- **Open/unverified items:** 10 grouped areas:
  1. Current Calico release, maintenance/support, kind integration, Kubernetes compatibility, install and cleanup steps.
  2. Actual CNI and baseline NetworkPolicy enforcement behavior in the learner's environment.
  3. Actual DNS namespace, labels, ports, and namespace-name labels.
  4. Workload/controller/scraper labels and actual listener ports.
  5. `endPort` schema and CNI support.
  6. `ipBlock`/NAT/hostNetwork/pre-post-NAT behavior.
  7. Probe, webhook, control-plane/node-originated, and metrics-scraping paths.
  8. Cilium/Calico-specific FQDN/L7/flow tooling and version compatibility.
  9. AdminNetworkPolicy/BaselineAdminNetworkPolicy maturity and implementation support.
  10. Live validation of all manifests, test scripts, cleanup, and policy enforcement.

**AI self-audit is not a live-cluster test or independent human review.** Before production use, verify current official docs, execute the labs in disposable clusters, inspect the actual CNI datapath, and obtain platform/security review.
