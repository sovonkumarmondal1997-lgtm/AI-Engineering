# Unit 7 — Progressive Delivery with Canary and Blue-Green Releases

**Target file:** `07-progressive-delivery-with-canary-and-blue-green-releases.md` | **Module:** M08 | **Stage:** 2E  
**Estimated time:** 12–20 hours including the six labs; optional Gateway API integration adds time.  
**Prerequisites:** Git, container images, Kubernetes Deployments/Services/probes/HPA/PDB, Kustomize/Helm basics, GitOps reconciliation, networking fundamentals.  
**Core tools:** `kubectl`, Docker, `kind`, `curl`, Python 3; optional Gateway API implementation and `hey`/`wrk` if already installed.  
**Awareness-level topics:** rollout controllers (Unit 8), automated metric analysis and abort (Unit 9), feature flags (Unit 10), database migration safety (Unit 11), contract compatibility (Unit 12), release evidence (Unit 13), fleet rollout (M14).  
**Last reviewed:** 2026-10-28.  
**Tool baseline assumed:** Kubernetes `apps/v1` Deployments and Services; Gateway API `gateway.networking.k8s.io/v1` `HTTPRoute` where the installed controller supports it. Exact local versions and implementation-specific routing behavior: `[VERIFY]`.  
**Footprint:** Core labs generally fit a local `kind` cluster with 4 CPU, 8 GB RAM and 30 GB disk if labs are run sequentially. A Gateway implementation is optional and may need additional resources. No paid service, real cloud account, production cluster, credentials, or customer data is required.

> **Truth and safety:** All scenarios and sample values are `[ILLUSTRATIVE]` unless stated otherwise. Commands are learner-run instructions, not evidence that a cluster was tested by the author. Expected outputs are representative patterns, not captured results. Use a throwaway local cluster and synthetic requests only.

## 1. How to use this lesson and lab safety/budget

Read the strategy and decision sections first. Run one lab at a time, capture its evidence, and delete its lab resources before starting an optional router. Before every Kubernetes write, confirm the active context and namespace. The examples intentionally use the `progressive-lab` namespace and the `kind-progressive-lab` context name; adapt the context only after verifying it is your disposable cluster.

```bash
# Host/WSL2 shell. These commands create a disposable local cluster.
kind create cluster --name progressive-lab
kubectl config current-context
kubectl cluster-info
kubectl create namespace progressive-lab
kubectl config set-context --current --namespace=progressive-lab
```

Expected pattern: the current context is `kind-progressive-lab`, the API server responds, and the namespace exists. If the context is not the disposable cluster, stop. Do not run cleanup against an unknown context. On WSL2, `localhost` inside a Pod or container is that Pod/container, not the Windows host or another container. Use Kubernetes Services from inside the cluster; for host access, use `kubectl port-forward` or a verified host-port configuration.

A plain Kubernetes lab is intentionally not an automated progressive-delivery controller. Human-triggered traffic shifts and aborts are manual. Unit 8 covers Argo Rollouts/Flagger configuration; Unit 9 covers automated release-health analysis. This unit teaches the strategy, the underlying Kubernetes/routing behavior, and how to measure whether a rollout is safe.

## 2. Prerequisites and cross-links

- [Unit 1 — GitOps principles and desired-state reconciliation](01-gitops-principles-and-desired-state-reconciliation.md): desired state, reconciliation loops, and ownership.
- [Unit 2 — Argo CD Applications, Projects, and sync policies](02-argo-cd-applications-projects-and-sync-policies.md) and [Unit 3 — Flux controllers and Kustomize/Helm reconciliation](03-flux-controllers-and-kustomize-helm-reconciliation.md): controller behaviors and drift prevention.
- [Unit 4 — Repository layout and multi-environment promotion](04-repository-layout-and-multi-environment-promotion.md): promote the same artifact and separate environment configuration.
- [Unit 5 — Configuration and secret reference management](05-configuration-and-secret-reference-management.md): keep credentials out of manifests and traffic captures.
- [Unit 6 — Deployment drift detection and reconciliation](06-deployment-drift-detection-and-reconciliation.md): prevent GitOps from overwriting a rollout controller's owned fields.
- [Unit 8 — Argo Rollouts, Flagger, and traffic-based analysis](08-argo-rollouts-flagger-and-traffic-based-analysis.md): controller-managed steps, routing integrations, and analysis.
- [Unit 9 — Release health analysis and automated abort](09-release-health-analysis-and-automated-abort.md), [Unit 10 — Feature flags and dark launches](10-feature-flags-and-dark-launches.md), [Unit 11 — Database and data-platform migration safety](11-database-and-data-platform-migration-safety.md), [Unit 12 — Backward-compatible pipeline and API releases](12-backward-compatible-pipeline-and-api-releases.md), and [Unit 13 — Release evidence and audit trails](13-release-evidence-and-audit-trails.md).
- M03 Unit 5: readiness, endpoint propagation and termination behavior; M03 topics on Deployments, HPA, PDB and Kubernetes access. M04 Unit 3: Ingress/Gateway API routing; M04 Unit 4: load balancing and external traffic; M04 Unit 8: service-mesh traffic shifting. M10 covers SLOs/error budgets; M14 covers multi-cluster/fleet delivery. Exact cross-module filenames are intentionally not guessed because the available roadmap snapshot did not expose all of them.

This lesson assumes you know how to deploy a service, not that you have already operated a canary. A Deployment rollout controls ReplicaSets and Pods. A router controls which requests reach which backend. An analysis system evaluates signals and decides whether a step can proceed. Those are distinct responsibilities.

## 3. Progressive delivery fundamentals

### 3.1 Why progressive delivery exists

**[ILLUSTRATIVE]** At 10:02, a team releases `scoring-api:v2`. Readiness succeeds and HTTP 5xx stays low, so the rollout reaches 100%. At 10:12, p99 latency doubles under the full production concurrency profile and prediction fallbacks increase. The canary did not fail because the team tested only the wrong signals and advanced before enough representative traffic arrived. The story is fictional; it illustrates that a successful deployment is not proof of a successful release.

A **deployment** places a version in the environment. A **release** exposes behavior to some or all users or downstream systems. Progressive delivery separates these steps: deploy a candidate, expose a controlled cohort, observe valid signals, then promote or abort. The objective is not “zero risk”; it is to bound exposure, learn from representative traffic, and recover quickly when evidence is unfavorable.

```text
Build + verify immutable artifact
             |
             v
Deploy candidate alongside stable
             |
             v
Expose a bounded cohort / traffic share
             |
             v
Collect enough valid baseline + candidate evidence
        /             |              \
     PASS          INCONCLUSIVE       FAIL
      |                 |               |
 increase step      hold / gather      abort / route stable
      |                 |               |
      +------ repeat ---+-------> verify recovery and record
```

- **Stable:** the currently trusted version receiving normal traffic.
- **Candidate:** the version being evaluated.
- **Promotion:** increasing exposure after evidence meets the predeclared gate.
- **Abort:** stop increasing exposure and direct traffic away from the candidate where safe.
- **Rollback:** restore a prior application/configuration version. It is not always safe if new data, messages, or external side effects cannot be reversed.

### 3.2 Learning outcomes

| Level | Measurable outcome |
|---|---|
| L1 | Explain blast radius and distinguish deployment from release; correctly compare seven strategies. |
| L1 | Explain why replica ratio is not a precise request percentage and why a raw healthy Pod is not sufficient evidence. |
| L2 | Apply blue-green and replica-weighted patterns in a disposable cluster; record failures and observed version distribution. |
| L2 | Inspect a Gateway API route's status and measure actual split over at least 1,000 synthetic requests when a compatible controller is available. |
| L2 | Define stable/candidate signals, minimum sample, evaluation window, and explicit pass/fail/inconclusive outcomes. |
| L3 | Design a release plan for HTTP, batch, streaming, and ML workloads with ownership, compatibility, capacity, and abort paths. |
| L3 | Diagnose metric lag, cohort instability, HPA interaction, routing drift, and non-rollbackable side effects. |
| L4 | Produce risk-tiered release policy, incident evidence, and operational metrics without treating sample thresholds as universal. |
| L4 | Demonstrate a tested abort path and document evidence that traffic returned to stable and service signals recovered. |

### 3.3 Glossary

| Term | Precise meaning | Common misconception |
|---|---|---|
| Progressive delivery | Controlled exposure with evidence-gated promotion or abort | A synonym for a rolling update |
| Canary | Limited candidate exposure followed by staged decisions | Necessarily means exactly 5% of requests |
| Blue-green | Two independently deployable environments; a routing decision selects active traffic | A Service selector switch is globally instantaneous |
| Replica-weighted | Traffic distribution emerges from the relative ready endpoints behind a shared Service | Replica ratio guarantees request ratio |
| Route-weighted | A router distributes requests according to configured backend weights | Configured weight equals observed split exactly |
| Baseline | Reference behavior measured over a relevant comparison window | A fixed historical average always matches current load |
| Inconclusive | Evidence is absent, delayed, or too small to support a safe decision | Missing metrics means the candidate passed |
| Abort | Stop candidate exposure and invoke a safe recovery plan | Every change can be rolled back without side effects |
| Shadow/mirror | Duplicate eligible requests to a candidate while normally discarding its response | Mirrored traffic is harmless by default |

## 4. Strategy comparison and decision matrix

| Strategy | Purpose / traffic model | Capacity cost | Rollback characteristics | Requirements and main failure modes | Choose / avoid |
|---|---|---:|---|---|---|
| Recreate | Stop old Pods, then start new Pods | Low to moderate | Simple version reversal, but downtime may occur | Workload can tolerate interruption; fails for strict availability or slow startup | Choose for non-critical workloads that cannot run two versions; avoid for availability-sensitive APIs |
| Rolling update | Gradually replace Pods within a Deployment; readiness gates replacement progression | Usually modest surge | Roll back Deployment revision, but old fleet may already be scaled down | `maxSurge`, `maxUnavailable`, readiness and capacity; does not supply request percentages or metric-aware abort | Good default for low-risk compatible services; insufficient alone for controlled traffic experiments |
| Blue-green | Run two full versions and switch a Service/router | Roughly two environments during overlap | Fast control-plane reversal if old version remains healthy and compatible | Capacity, endpoint propagation, in-flight connections, shared DB compatibility | Choose when clean switch and preview tests matter; avoid when duplicate capacity is unaffordable or schema compatibility is absent |
| Canary | Increase candidate exposure by replica ratio or routing weights | Extra candidate capacity | Stop and route back to stable; safety depends on side effects | Valid sample, signals, stable baseline, abort path; false confidence from low traffic or bad metrics | Choose for risky user-facing or ML changes; avoid pretending tiny samples prove safety |
| A/B test | Assign cohorts to compare product/business outcomes | Variable | End experiment assignment; not necessarily deployment rollback | Randomization, cohort consistency, experiment design and guardrails | Use for product hypotheses; not by itself a release safety mechanism |
| Shadow/mirror | Duplicate requests to candidate, ignore candidate response | Extra compute and potentially downstream load | Stop mirroring; no user response switch needed | PII, consent, duplicate writes, idempotency, cost, biased mirrored traffic | Use for read-only validation; avoid uncontrolled side effects or sensitive payload replication |
| Feature flag | Deploy code, selectively enable behavior | Usually low infrastructure overhead | Disable flag quickly if behavior is safely reversible | Flag lifecycle, config security, test matrix, stale flags | Useful for decoupling code deploy from exposure; not a substitute for deployment health checks |

Kubernetes native rolling updates can control `maxSurge` and `maxUnavailable`, and readiness influences availability accounting. They do **not** by themselves provide percentage-based request routing, metric-aware pause/abort, or an intact old fleet that can be switched back instantly. Kubernetes documents the rolling-update behavior and its constraints in the [Deployment documentation](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) and [update tutorial](https://kubernetes.io/docs/tasks/run-application/update-deployment/). 

## 5. Canary design: traffic, duration, signals, failure behavior

Every canary requires four explicit decisions:

1. **How much is exposed?** Define request percentage, user cohort, data slice, or replica ratio. State whether this is configured or measured.
2. **For how long and how much valid sample?** Set a minimum request/event count and an evaluation window that includes metric propagation delay and representative load. A time limit alone is insufficient.
3. **Which signals are evaluated?** Include technical health and domain/business/ML outcomes, compared side by side against stable.
4. **What happens on fail, inconclusive, or missing metrics?** Define who stops the release, how stable traffic is restored, and what evidence proves recovery. Missing data must not silently pass.

**[ILLUSTRATIVE]** A medium-risk API might progress 5% → 25% → 50% → 100%, with each step held until a minimum request sample and a complete metric window are available. Example thresholds might compare candidate 5xx rate and p95/p99 latency against stable plus absolute service guardrails. These numbers are not standards. A low-volume service may need hours, replay, or synthetic checks rather than a five-minute canary. A tier-0 service should use slower progression and stronger evidence, especially when error-budget consumption is already high.

### Leading and lagging signals

- **Leading:** readiness failures, startup errors, saturation, queue depth, throttling, dependency timeouts, data freshness, fallback ratio, schema validation failures.
- **Lagging:** user-reported defects, conversion/quality loss, nightly batch failures, downstream data corruption, accumulated latency or error-budget burn.
- **Domain/ML:** prediction latency, model error proxies, output distribution shifts, fallback/default response ratio, feature freshness, queue lag, confidence/calibration monitors where validated.

Use baseline-versus-candidate comparisons because absolute values move with traffic and time of day. Comparison does not eliminate confounding: route cohorts may differ, requests may be correlated, and candidate traffic may be too small. Define eligibility, sample minimum, windows, tolerance, and the inconclusive state before rollout.

## 6. Plain Kubernetes blue-green implementation

### 6.1 Files and manifests

The following is a complete minimal lab. It uses `hashicorp/http-echo:1.0.0` as a simple synthetic HTTP responder. For production, use an approved immutable image digest, non-root configuration, security context, probes appropriate to the application, and image provenance. The lab image tag is for demonstration and is not a production pin.

Save as `blue-green.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scoring-api-blue
  namespace: progressive-lab
spec:
  replicas: 2
  selector:
    matchLabels:
      app: scoring-api
      color: blue
  template:
    metadata:
      labels:
        app: scoring-api
        color: blue
        version: stable
    spec:
      containers:
        - name: responder
          image: hashicorp/http-echo:1.0.0
          args: ["-listen=:8080", "-text=stable-blue"]
          ports:
            - name: http
              containerPort: 8080
          readinessProbe:
            httpGet: { path: /, port: http }
            initialDelaySeconds: 1
            periodSeconds: 2
          resources:
            requests: { cpu: 25m, memory: 32Mi }
            limits: { cpu: 200m, memory: 64Mi }
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scoring-api-green
  namespace: progressive-lab
spec:
  replicas: 2
  selector:
    matchLabels:
      app: scoring-api
      color: green
  template:
    metadata:
      labels:
        app: scoring-api
        color: green
        version: candidate
    spec:
      containers:
        - name: responder
          image: hashicorp/http-echo:1.0.0
          args: ["-listen=:8080", "-text=candidate-green"]
          ports:
            - name: http
              containerPort: 8080
          readinessProbe:
            httpGet: { path: /, port: http }
            initialDelaySeconds: 1
            periodSeconds: 2
          resources:
            requests: { cpu: 25m, memory: 32Mi }
            limits: { cpu: 200m, memory: 64Mi }
---
apiVersion: v1
kind: Service
metadata:
  name: scoring-api
  namespace: progressive-lab
spec:
  selector:
    app: scoring-api
    color: blue
  ports:
    - name: http
      port: 80
      targetPort: http
```

The Deployment selectors are disjoint (`color: blue` versus `color: green`) so they do not manage the same Pods. The Service selector initially routes to blue. Apply and wait:

```bash
# WSL2/host shell; verify current context first.
kubectl config current-context
kubectl apply -f blue-green.yaml
kubectl -n progressive-lab rollout status deployment/scoring-api-blue --timeout=120s
kubectl -n progressive-lab rollout status deployment/scoring-api-green --timeout=120s
kubectl -n progressive-lab get pods -l app=scoring-api -o wide
kubectl -n progressive-lab get endpointslices -l kubernetes.io/service-name=scoring-api
```

Check the active version:

```bash
kubectl -n progressive-lab port-forward service/scoring-api 18080:80
# In a second host shell:
curl -fsS http://127.0.0.1:18080/
```

**Expected pattern:** the response contains `stable-blue`. EndpointSlices and Pod readiness should show ready blue endpoints. Exact Pod names and output are environment-specific.

### 6.2 Switch, verify, and reverse

```bash
# Promote green: changes only the Service selector.
kubectl -n progressive-lab patch service scoring-api --type=merge \
  -p '{"spec":{"selector":{"app":"scoring-api","color":"green"}}}'
kubectl -n progressive-lab get endpointslices -l kubernetes.io/service-name=scoring-api
curl -fsS http://127.0.0.1:18080/

# Roll back routing to blue if predeclared checks fail.
kubectl -n progressive-lab patch service scoring-api --type=merge \
  -p '{"spec":{"selector":{"app":"scoring-api","color":"blue"}}}'
curl -fsS http://127.0.0.1:18080/
```

A selector patch is a control-plane update, **not a globally instantaneous data-plane switch**. The API server accepts the new desired selector, controllers update EndpointSlices, proxies/routers observe updates, and existing connections may continue to the prior endpoint. Long-lived streams, keep-alive connections, client retries, DNS caches, and external routers complicate the switch. Readiness establishes a Pod's eligibility signal; it does not prove every dependency or business workflow works. Keep blue alive through a defined rollback window and ensure both versions are compatible with the shared database and messages.

### 6.3 Measure dropped requests during a switch

With port-forward active, save `switch-measure.sh`:

```bash
#!/usr/bin/env bash
set -u
URL="${URL:-http://127.0.0.1:18080/}"
COUNT="${COUNT:-500}"
OUT="${OUT:-switch-results.tsv}"
printf 'request\tresult\tresponse\n' > "$OUT"
for i in $(seq 1 "$COUNT"); do
  body=$(curl --max-time 2 -sS -w '\tHTTP:%{http_code}' "$URL" 2>/dev/null) || body='CURL_ERROR'
  if [[ "$body" == *'HTTP:200' ]]; then result=success; else result=failure; fi
  printf '%s\t%s\t%s\n' "$i" "$result" "${body//$'\t'/ }" >> "$OUT"
done
awk -F '\t' 'NR>1 {total++; if ($2=="success") ok++; else fail++} END {printf "total=%d success=%d failure=%d failure_rate=%.4f\n",total,ok,fail,(total?fail/total:0)}' "$OUT"
```

Run a baseline, then start the script in one shell while switching Service selector from another. Record results; do not insert invented counts into the worksheet.

| Trial | Requests | Switch timing | Failures | Failure rate | Notes |
|---|---:|---|---:|---:|---|
| Baseline | 500 | No switch | ___ | ___ | ___ |
| Switch 1 | 500 | Patch during request loop | ___ | ___ | ___ |
| Mitigated switch | 500 | Readiness precheck + wait + retry client | ___ | ___ | ___ |

**[ILLUSTRATIVE] expected pattern:** baseline is usually stable; a switch may show zero or some failures depending on timing and local networking. Zero observed failures does not prove zero risk under production concurrency. A mitigation can include pre-switch readiness and smoke checks, a router with explicit drain behavior, client retries with idempotency, and retaining the old environment. Retrying writes is unsafe unless idempotency/duplicate behavior is designed. Repeat with the same request count and disclose that localhost port-forward traffic is not representative of a production load balancer.

## 7. Plain Kubernetes replica-weighted canary implementation

A shared Service selecting both stable and candidate Pods distributes traffic across eligible endpoints. With 9 stable Pods and 1 candidate Pod, the rough expectation is one in ten endpoint choices to candidate, not a precise 10% request guarantee. A single candidate among ten is coarse; with fewer replicas, each replica changes the nominal ratio dramatically. Unequal request duration, connection reuse, session affinity, readiness, uneven load, and HPA decisions can distort actual distribution.

Save as `replica-canary.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scoring-api-stable
  namespace: progressive-lab
spec:
  replicas: 9
  selector:
    matchLabels: { app: scoring-api, track: stable }
  template:
    metadata:
      labels: { app: scoring-api, track: stable }
    spec:
      containers:
        - name: responder
          image: hashicorp/http-echo:1.0.0
          args: ["-listen=:8080", "-text=stable"]
          ports: [{ name: http, containerPort: 8080 }]
          readinessProbe: { httpGet: { path: /, port: http }, periodSeconds: 2 }
          resources: { requests: { cpu: 25m, memory: 32Mi }, limits: { cpu: 200m, memory: 64Mi } }
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scoring-api-candidate
  namespace: progressive-lab
spec:
  replicas: 1
  selector:
    matchLabels: { app: scoring-api, track: candidate }
  template:
    metadata:
      labels: { app: scoring-api, track: candidate }
    spec:
      containers:
        - name: responder
          image: hashicorp/http-echo:1.0.0
          args: ["-listen=:8080", "-text=candidate"]
          ports: [{ name: http, containerPort: 8080 }]
          readinessProbe: { httpGet: { path: /, port: http }, periodSeconds: 2 }
          resources: { requests: { cpu: 25m, memory: 32Mi }, limits: { cpu: 200m, memory: 64Mi } }
---
apiVersion: v1
kind: Service
metadata:
  name: scoring-api-shared
  namespace: progressive-lab
spec:
  selector: { app: scoring-api }
  ports: [{ name: http, port: 80, targetPort: http }]
---
apiVersion: v1
kind: Service
metadata:
  name: scoring-api-stable
  namespace: progressive-lab
spec:
  selector: { app: scoring-api, track: stable }
  ports: [{ name: http, port: 80, targetPort: http }]
---
apiVersion: v1
kind: Service
metadata:
  name: scoring-api-candidate
  namespace: progressive-lab
spec:
  selector: { app: scoring-api, track: candidate }
  ports: [{ name: http, port: 80, targetPort: http }]
```

The three Services intentionally expose different views: `scoring-api-shared` selects both tracks for replica-weighted testing; `scoring-api-stable` and `scoring-api-candidate` select one track each for Gateway API routing. Apply only after considering whether the earlier blue-green objects would confuse your measurements. The selectors deliberately use `app: scoring-api` at the shared Service and distinct `track` labels at each Deployment selector. `kubectl apply -f replica-canary.yaml` then wait for both Deployments. To change the ratio, scale the two Deployments separately:

```bash
kubectl -n progressive-lab scale deployment/scoring-api-candidate --replicas=2
kubectl -n progressive-lab scale deployment/scoring-api-stable --replicas=8
kubectl -n progressive-lab get pods -l app=scoring-api --show-labels
```

Use the request measurement script in Lab B to count `stable` versus `candidate` responses over at least 1,000 requests. A sample count is a measurement of this particular test, not a guarantee for future traffic. Avoid letting an HPA and GitOps both independently write the same `spec.replicas` field; decide whether HPA owns scale and define a compatible GitOps strategy (Unit 6). In a real canary, stable and candidate need independent capacity planning and enough candidate replicas to avoid an overloaded test cohort.

## 8. Gateway API / Ingress route-weighted canary

### 8.1 HTTPRoute example

Gateway API `HTTPRoute` defines backend references and supports relative weights in its API. Whether a particular controller version implements the required behavior, header matches, and status conditions must be checked: `[VERIFY]`. Standard Kubernetes Ingress has **no portable generic backend-weight field**; NGINX annotations and other controller extensions are implementation-specific.

Example `scoring-route.yaml` (requires an already installed, compatible Gateway API controller, Gateway, and two Services in the same permitted namespace arrangement):

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: scoring-api
  namespace: progressive-lab
spec:
  parentRefs:
    - name: lab-gateway
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /
      backendRefs:
        - name: scoring-api-stable
          port: 80
          weight: 95
        - name: scoring-api-candidate
          port: 80
          weight: 5
    - matches:
        - headers:
            - type: Exact
              name: x-canary-test
              value: "true"
          path:
            type: PathPrefix
            value: /preview
      backendRefs:
        - name: scoring-api-candidate
          port: 80
```

This is a teaching pattern, not a universal drop-in: route precedence, cross-namespace permissions, parent listener configuration, header matching, and backend Service ports must match the installed implementation. The two Services must select distinct stable/candidate Pods. A route with multiple rules may have precedence semantics that need review; ensure the preview match is actually selected and does not conflict with the catch-all rule. `[VERIFY]` the final route ordering and conformance against the controller's docs before applying.

Verification steps (run in the host shell):

```bash
kubectl api-resources | grep -E 'gatewayclasses|gateways|httproutes'
kubectl get crd httproutes.gateway.networking.k8s.io
kubectl -n progressive-lab get httproute scoring-api -o yaml
kubectl -n progressive-lab describe httproute scoring-api
kubectl -n progressive-lab get events --sort-by=.lastTimestamp
kubectl -n progressive-lab get gateway
```

Inspect `status.parents[].conditions` and confirm that the route is accepted and programmed by the intended parent, and that backend references resolve. Exact condition details depend on the installed Gateway API/controller version. An accepted route is not proof that the request reaches the expected backend: measure responses. If the router cannot implement weighted routing locally, complete the replica-weighted lab and mark route-weighted implementation **not run**; retain this as a guided design exercise rather than faking success.

### 8.2 Measure actual route split over at least 1,000 requests

Assume `BASE_URL` is the reachable local Gateway address and that stable/candidate return body tokens `stable` and `candidate`. The script records failures separately; it does not count them as stable traffic.

Save `measure-split.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
: "${BASE_URL:?Set BASE_URL to the reachable local Gateway URL}"
N="${N:-1000}"
OUT="${OUT:-split-results.tsv}"
printf 'request\tclass\tstatus\tbody\n' > "$OUT"
for i in $(seq 1 "$N"); do
  tmp=$(mktemp)
  status=$(curl -sS --max-time 3 -o "$tmp" -w '%{http_code}' "$BASE_URL/" 2>/dev/null || printf '000')
  body=$(cat "$tmp" 2>/dev/null || true); rm -f "$tmp"
  case "$body" in
    *candidate*) class=candidate ;;
    *stable*) class=stable ;;
    *) class=unknown ;;
  esac
  printf '%s\t%s\t%s\t%s\n' "$i" "$class" "$status" "${body//$'\t'/ }" >> "$OUT"
done
awk -F '\t' 'NR>1 {n++; c[$2]++; if ($3 !~ /^2/) bad++} END {printf "total=%d stable=%d candidate=%d unknown=%d non_2xx=%d\n",n,c["stable"],c["candidate"],c["unknown"],bad; if(n>0) printf "candidate_fraction_of_classified=%.4f\n",c["candidate"]/(c["candidate"]+c["stable"])}' "$OUT"
```

Run `BASE_URL=http://127.0.0.1:<verified-port> N=1000 ./measure-split.sh` after setting a real local address/port. Do not paste an unverified port into production. Record the measured counts:

| Configured weights | Total requests | Stable | Candidate | Unknown/errors | Observed candidate share of classified |
|---|---:|---:|---:|---:|---:|
| 95:5 | 1,000+ | ___ | ___ | ___ | ___ |
| 75:25 | 1,000+ | ___ | ___ | ___ | ___ |

Observed split will vary due to sampling and implementation details. For independent requests under an idealized Bernoulli 5% assignment, random variation is expected; persistent large deviations suggest route mismatch, endpoint problems, client connection behavior, a bad measurement classifier, or unsupported controller behavior. A configured weight is a routing intent, not evidence. Use a header test only when the controller's header-match behavior is verified and the request includes the exact header/path/host expected by the route.

## 9. Cohorts, sticky sessions, and session affinity

If a user can land on stable for one request and candidate on the next, a multi-step workflow may see inconsistent responses, incompatible cookies, or state that one version cannot read. Use a consistent assignment mechanism where the router supports it: signed cookie, stable user identifier hash, or explicit test header. Avoid exposing personal identifiers in logs; use opaque cohort keys and appropriate retention controls.

Kubernetes Service `sessionAffinity: ClientIP` is not automatically equivalent to application-level cohort assignment. NAT can group many users behind one source IP, clients may change networks, and HTTP connection reuse can bias request counts. Header/cookie routing is controller-specific; verify support and precedence. Test at least: repeated requests from one cohort stay on the intended version, a new cohort is assigned correctly, retries do not change assignment unexpectedly, and session state remains compatible during coexistence.

Pseudocode for a deterministic cohort assignment (conceptual, not a Kubernetes feature):

```python
import hashlib

def cohort_for(user_key: str, candidate_percent: int = 5) -> str:
    bucket = int(hashlib.sha256(user_key.encode()).hexdigest()[:8], 16) % 100
    return "candidate" if bucket < candidate_percent else "stable"
```

Production use must define identity normalization, secret/salt rotation if applicable, privacy, cohort changes, and how assignments are enforced at the router. Do not use raw email addresses or other PII as a routing header.

## 10. Health signals, stable-baseline comparison, and sample size

| Signal | Why compare stable and candidate | Caveats / response |
|---|---|---|
| HTTP 5xx / error rate | Detects regressions relative to current traffic | Small denominators create unstable rates; inspect error class and route |
| p50/p95/p99 latency | Detects tail regressions often hidden by averages | Percentiles need sufficient samples; compare same request classes |
| CPU/memory, throttling | Finds saturation and resource regressions | Low CPU does not mean low latency; inspect dependency and queue waits |
| Queue depth / consumer lag | Finds throughput mismatch | Lag may take longer to surface than HTTP errors |
| Prediction latency / fallback ratio | Captures ML-serving behavior | Validate fallback semantics and input mix |
| Output distribution / quality proxy | Detects model or preprocessing shifts | Distribution changes may be intended; compare replay labels and guardrails |
| Data freshness / row-count / schema violations | Detects pipeline-specific damage | HTTP metrics cannot detect silent data corruption |
| Business outcome | Connects release to actual product value | Often delayed and confounded; use guardrails, not a single metric |

Define metric windows from the full path: event time → scrape/collection → aggregation → transport/storage → query evaluation → decision. If telemetry takes 90 seconds to become queryable, a 30-second step can evaluate before the defect appears. The rollout may pass stale or empty data. `[ILLUSTRATIVE]` timeline:

| Event time | Metric arrival | Evaluation | Decision | Risk |
|---|---|---|---|---|
| 10:00:00 candidate begins | — | 10:00:30 | pass based on stale data | unsafe |
| 10:00:10 latency regression starts | 10:01:40 | 10:00:30 | defect not visible yet | unsafe |
| 10:01:00 next step starts | — | 10:01:30 | still stale | unsafe |
| 10:01:40 regression metric available | 10:02:00 | failure can now be observed | delayed abort |

Statistical power in practical terms means having enough independent, representative observations to distinguish a meaningful regression from noise. Requests are not always independent: one user session may produce many correlated requests; load patterns and retries can bias samples. Repeatedly checking many metrics/thresholds raises false-positive risk, while broad thresholds and short windows raise false-negative risk. Establish windows, minimum samples, and guardrails using historical service data. For low traffic, classify the result as inconclusive, extend the window, replay safe synthetic traffic, or use shadow comparison. Synthetic traffic can miss production data shape, authentication, concurrency, or dependency behavior; it complements real traffic, not replaces it.

**[ILLUSTRATIVE] step schedule:** 5% → 25% → 50% → 100%. At each step require (a) minimum eligible sample, (b) full telemetry delay plus evaluation window, (c) no absolute guardrail breach, (d) acceptable candidate-vs-stable difference, and (e) no missing critical metric. If any critical metric is missing, do not treat that as pass.

## 11. Advanced service, stateful, batch, streaming, and ML scenarios

### Batch / ETL

Run candidate logic against a bounded data slice or in parallel to stable, write outputs to a separate versioned location, and compare row counts, schema, key uniqueness, null rates, aggregates, freshness, and sampled row-level differences. Do not let both versions write to the same production destination unless writes are idempotent and ownership is explicit. Prefer “write new output → validate → switch consumer pointer → retain prior output for recovery.” Preserve lineage and input partition identifiers so reruns are explainable.

### Streaming consumer

Run a candidate consumer group against a mirrored topic or controlled replay, not by casually joining the production consumer group and changing partition ownership. Compare lag, deserialize failures, output counts, ordering assumptions, and side effects. A separate consumer group can duplicate writes or emit duplicate events; route output to an isolated sink until correctness is proven. Preserve offsets and replay procedures. Rollback does not rewind downstream side effects automatically.

### ML/model release

Treat the model, feature preprocessing, schema, thresholds, and serving code as a compatibility unit. Replay a representative, privacy-approved dataset against stable and candidate; compare latency, fallback ratio, prediction distribution, calibrated quality where labels exist, and slice-level behavior. Shadow traffic is useful only if candidate requests cannot mutate state or emit real side effects. A distribution shift is a signal to investigate, not automatic proof of failure. Link the evidence to the model and feature-pipeline versions.

### Stateful services and database compatibility

Blue and green commonly share a database, so both versions must operate safely against the same schema and data during the overlap window. Prefer expand-and-contract migrations: add backward-compatible fields first, deploy code that tolerates both forms, migrate data, then remove old fields only after all old consumers are gone. For irreversible writes, design roll-forward or compensating actions. See Unit 11 for migration safety and Unit 12 for API/pipeline compatibility.

## 12. HPA/PDB/capacity and GitOps field ownership

Keep stable and candidate capacity explicit. An HPA may scale each workload differently based on utilization and traffic; candidate can overload before enough replicas become ready. A capacity worksheet should include stable peak demand, candidate test demand, per-Pod request/limit, startup time, surge allowance, node headroom, queue backlog, and a safe replica floor. Do not assume a low traffic percentage means low compute cost: a small number of slow candidate requests can occupy many connections.

A PodDisruptionBudget constrains some voluntary evictions; it does not guarantee application-level request success, protect against every failure, or provide a traffic-draining strategy. Readiness, PDB, routing, termination grace, preStop behavior, client retries, and connection draining solve different parts of the problem. Validate them together.

**Single-owner rule:** one controller/tool owns a field at a time. GitOps should declare stable desired configuration; a rollout controller may own dynamic traffic weights and rollout state; HPA may own scale. Do not have Argo CD/Flux continuously rewrite the same weights/replicas that another controller is changing. Agree on field boundaries and test reconciliation. Argo CD health assessment for Rollout CRDs is version/configuration-sensitive: `[VERIFY]` installed Argo CD docs/configuration and inspect the live Application status. Unit 6 covers drift and field ownership; Unit 8 covers controller implementation. Do not infer automated abort from a plain Deployment.

### Routing mechanisms compared

| Mechanism | Precision | Cost / complexity | Typical risks |
|---|---|---|---|
| Replica-based Service | Coarse, endpoint-proportional | Lowest | Uneven request load, HPA interaction, no metric-aware routing |
| Gateway / ingress weights | Request routing intent; actual split must be measured | Moderate | Controller differences, route precedence, stale config, connection reuse |
| Service mesh | Rich traffic policies and telemetry when supported | Highest operational overhead | Control-plane/data-plane complexity, resource cost, policy interaction |

Under an 8 GB laptop budget, do not install all three. Use replica-based labs first. Add one Gateway implementation only if the environment has sufficient resources and the controller's current documentation confirms the exact required features. M04 Unit 8 covers mesh fundamentals.

## 13. Preview tests, post-deploy verification, multi-region awareness, and cost

Before switching blue-green traffic, require a preview checklist: candidate Pods ready; configuration and identity valid; smoke test passes; critical dependency integration test passes; resource saturation is acceptable under a safe local load; schema/data-quality check passes where relevant; and a rollback owner is available. Record artifact digest, config revision, test results, route change, approver, and rollback deadline.

After promotion, continue synthetic checks, error/latency comparison, queue/freshness monitoring, business/ML guardrails, and downstream validation through the rollback window. A successful `kubectl patch` only proves the API accepted a change; it does not prove users reach the candidate or the service recovered.

At Awareness level, multi-cluster/region rollout can progress by a low-risk cluster or region, then a wider cohort, while accounting for regional data residency, traffic routing, replication lag, capacity, and rollback coordination. Change windows and compliance requirements must be validated against the organization's actual policy; this lesson does not claim certification. Extra capacity, longer release time, duplicate telemetry, and operator burden are costs to compare against reduced incident exposure.

Canaries cannot reliably catch every slow leak, rare path, data corruption, low-frequency consumer contract break, issue that appears only at 100% load, or nightly downstream failure. Defense in depth includes contract tests, replay/shadow diffing, schema validation, load testing, synthetic probes, feature flags, data-quality monitors, consumer-version telemetry, and post-release observation (Units 9–12).

## 14. Governance, rollout metrics, abort-first design, and non-rollbackable changes

Use risk tiers rather than one policy for every service. Tier-0 services should normally require a documented progressive strategy, owner-approved signals, an explicit abort path, and a rehearsed recovery. Low-risk internal services may use a well-configured rolling update. Exceptions should name an owner, reason, expiry/review date, compensating controls, and approver. If error-budget policy calls for a release freeze, a canary is not permission to ignore that freeze; refer to M10's SLO/error-budget policy.

Define operational metrics with scope and denominator:

- **Change failure rate:** releases causing a defined rollback, hotfix, incident, or SLO-impacting regression / all releases in the same cohort and time period. Publish the event definition to avoid inconsistent counting.
- **MTTR / time to rollback:** specify whether timing ends at decision, traffic restoration, or SLO recovery; report more than one timestamp if useful.
- **Automated-release share:** releases completing required steps without manual intervention / eligible releases. Define what “fully automated” means.
- **Automation abort share:** rollouts aborted by automation / rollouts with automation enabled. A higher number may mean better detection or a noisy policy; interpret with outcomes.
- **Canary-detected vs post-rollout defects:** defects first detected before full exposure versus after full rollout. Deduplicate incidents and state the detection window.

Set targets from historical data and service objectives, not universal numbers. For every release, design the abort path before promotion: stable route restoration, candidate scale/stop procedure, recovery verification, owner, evidence, and handling of side effects. Rollback may be impossible if new code wrote data the old code cannot read, sent irreversible messages, charged a payment, or triggered external automation. In these cases, use roll-forward, compensating actions, or a safe compatibility layer. A rollback drill is a release-readiness requirement, not an afterthought.

For multi-service releases, order changes by compatibility: deploy tolerant consumers/providers in the right sequence, avoid lock-step releases, and keep old/new versions mutually compatible during the coexistence window. See Unit 12 for detailed API/pipeline contracts and Unit 11 for data migrations.

## 15. Incident casebook

All incidents below are `[ILLUSTRATIVE]`. Use the same pattern in a real incident: reduce blast radius first, preserve evidence, then diagnose and implement a durable fix.

| Incident | Symptoms and evidence | Diagnosis and immediate containment | Durable fix and prevention test |
|---|---|---|---|
| Canary passed on errors; latency regressed at 100% | Error rate stayed flat; p95/p99 rose under full concurrency; candidate CPU may look normal | Route traffic to stable if compatible; inspect latency by version, request class, dependency spans, queue depth and connection pools | Add latency/saturation/domain guardrails; load test at representative concurrency; test a 100%-load-only regression in pre-release testing |
| Step interval shorter than metric lag | Candidate promoted before metric series changed; query timestamps lag decision | Stop progression and route stable; inspect event timestamps, scrape/aggregation windows, query freshness and controller decision logs | Enforce a minimum data freshness and sample gate; simulate lag in CI; missing/stale metric => inconclusive |
| Sticky cohort flip-flopped | Same user sees different version; state/cookie schema differs; logs show alternating version | Stabilize cohort assignment or route affected cohort to stable; preserve session and request IDs without logging PII | Test deterministic cohort persistence, retries, cookie migration and cross-version compatibility |
| Blue-green switch dropped connections | 5xx/timeouts during Service selector switch; old connections still exist | Switch back if safe; inspect endpoint changes, termination events, client retries and connection lifetime | Add readiness/smoke precheck, supported draining, idempotent retries and measured switch test; keep old environment through rollback window |
| Canary and HPA fought | Replica oscillation, pending Pods, saturation, capacity collapse | Reduce candidate exposure, restore safe capacity and inspect HPA metrics/events/requests/limits | Define separate scale ownership, minimum replicas and headroom; test peak load and autoscaling lag before rollout |
| Both versions wrote DB; rollback unsafe | Old version errors reading new-format rows; duplicate messages or schema mismatch | Stop further writes if safe; preserve logs and database backup/transaction evidence; decide roll-forward or compensating action with data owner | Expand-contract migration, N-1 read/write compatibility tests, isolated dual-run output and rehearsed restore/compensation |

Incident response roles: application owner diagnoses behavior and compatibility; platform team owns router/controller and capacity; SRE/on-call coordinates impact, timeline and SLO status; security/privacy reviews mirrored data and access when applicable; data owner approves irreversible data repair. Collect artifact digests, Git/PR revision, route config, request distribution, candidate/stable signals, controller events, timestamps and decisions.

## 16. Hands-on labs A–F

### Lab A — Blue-green switch with dropped-request measurement

**Level/time/resources:** L2, 45–75 minutes, local `kind`, `curl`, 2 small Deployments. **Objective:** measure request failures during a Service selector change and evaluate a mitigation.

1. Create the disposable cluster/namespace in Section 1 and apply `blue-green.yaml` from Section 6.
2. Wait until both Deployments are ready and confirm the Service initially returns `stable-blue`.
3. Run `switch-measure.sh` once without a switch; save the TSV and summary as baseline evidence.
4. Run it again while changing the Service selector from blue to green in another shell. Record actual failures, not a guessed count.
5. Apply one mitigation: wait for both endpoints and candidate smoke test before switch; keep the old environment alive; test a client retry only for safe idempotent GET requests. Repeat the same request count.
6. Compare before/after failure rate and document the limitations of localhost port-forward measurements.

**Expected pattern `[ILLUSTRATIVE]`:** the script produces a total, success, failure and failure-rate summary. Your counts will differ. If there are zero failures, write “zero observed in this sample,” not “no dropped requests are possible.”

**Troubleshooting:** If curl cannot connect, verify port-forward process and Service endpoints before concluding the app failed. If the response never changes, inspect Service selector and EndpointSlices. If the image cannot be pulled, inspect Pod events and image access; do not silently replace the result with a fictional success.

**Cleanup:** stop the port-forward and run `kubectl -n progressive-lab delete -f blue-green.yaml` only when ready to remove these lab objects. Retain the TSV separately if needed. **Pass:** baseline and switch measurements exist, mitigation is repeated, and the result explains both what was measured and what it cannot prove.

### Lab B — Replica-weighted and route-weighted canary

**Level/time/resources:** L2, 60–120 minutes for replica path; Gateway route path is optional and may take longer. **Objective:** compare configured intent to observed traffic over at least 1,000 requests.

1. Apply `replica-canary.yaml`, wait for stable and candidate Deployments, and port-forward `scoring-api-shared` to a host port.
2. Use `measure-split.sh` with `BASE_URL` pointing to the local service. Run at least `N=1000`; save `split-results.tsv`.
3. Change replica counts (for example 9:1, then 8:2) and repeat. Keep HPA disabled for this deterministic lab so it does not alter the replica ratio.
4. If a compatible Gateway controller is already available or can be installed within the budget, configure the two backend Services and `HTTPRoute` in Section 8. Verify route status and measure at least 1,000 requests for each configured split.
5. If no compatible router is available, mark route weighting **guided design / not run**. Do not describe replica weighting as route weighting.

| Trial | Intended ratio | Requests | Observed stable | Observed candidate | Unknown/non-2xx | Interpretation |
|---|---|---:|---:|---:|---:|---|
| Replica | 9:1 | ___ | ___ | ___ | ___ | ___ |
| Replica | 8:2 | ___ | ___ | ___ | ___ | ___ |
| Route (if supported) | 95:5 | ___ | ___ | ___ | ___ | ___ |

**Troubleshooting:** candidate count near zero: inspect labels, Service selector, candidate readiness, route status, path/host/header matches and response classifier. If actual split differs, inspect connection reuse and measurement design. **Cleanup:** delete only the manifest used in this lab and any optional Gateway resources created for it. **Pass:** measured results cover 1,000+ requests, errors are separated from version counts, and unsupported routing is honestly recorded as not run.

### Lab C — Too-fast analysis thought-and-measure experiment

**Level/time/resources:** L3, 30–45 minutes, Python 3 only. **Objective:** demonstrate that decision intervals shorter than metric delay can pass a broken candidate.

Save as `metric-lag-lab.py`:

```python
#!/usr/bin/env python3
"""Deterministic simulation; not a live metrics system or rollout controller."""
from dataclasses import dataclass

@dataclass
class Observation:
    event_time: int
    arrival_time: int
    value: float

# [ILLUSTRATIVE] latency is healthy at first; regression becomes visible after 100 s.
observations = [Observation(0, 20, 100.0), Observation(100, 160, 250.0)]
threshold_ms = 150.0

def visible_value(at_time: int):
    visible = [o for o in observations if o.arrival_time <= at_time]
    return visible[-1].value if visible else None

for eval_time in (60, 120, 180):
    value = visible_value(eval_time)
    if value is None:
        decision = "INCONCLUSIVE_NO_DATA"
    elif value > threshold_ms:
        decision = "FAIL_ABORT"
    else:
        decision = "PASS_FOR_THIS_EVALUATION_ONLY"
    print(f"evaluation={eval_time}s visible_latency={value} decision={decision}")
```

Run `python3 metric-lag-lab.py`. Output is **simulated by the script**, not captured from Kubernetes. Compare evaluation at 60 seconds with the regression event at 100 seconds and metric arrival at 160 seconds. Adjust the evaluation times to 180 seconds and observe that the regression becomes visible. Then propose a safe gate requiring a fresh sample, sufficient sample size, and a window that includes propagation delay.

| Event time | Metric arrival | Evaluation time | Decision | Outcome |
|---:|---:|---:|---|---|
| 0 s | 20 s | 60 s | ___ | ___ |
| 100 s regression | 160 s | 120 s | ___ | ___ |
| 100 s regression | 160 s | 180 s | ___ | ___ |

**Troubleshooting:** `None` means no visible observation; it is not healthy. The simulation is deliberately simple and does not model query aggregation or correlated samples. **Pass:** learner identifies the unsafe early pass, distinguishes event time from arrival time, and documents a no-data policy that is not success.

### Lab D — Strategy-selection worksheet for five services

**Level/time/resources:** L3, 45–60 minutes, no cluster required. Complete each field with reasoning rather than a strategy name only.

| Service | Starting recommendation `[ILLUSTRATIVE]` | Required signals / slicing | Compatibility and abort questions |
|---|---|---|---|
| Tier-0 synchronous API | Route-weighted canary with slow, gated steps; blue-green may support fast routing reversal | 5xx, p99, saturation, dependency latency, domain guardrails; representative request cohorts | Can old/new share DB? Who can abort? How is stable traffic verified? |
| Low-risk internal service | Rolling update if downtime and blast radius are acceptable | Readiness, error rate, resource headroom, smoke test | Is a full duplicate environment worth its cost? |
| Batch/ETL | Parallel run on isolated slice/output and diff | Row counts, schema, freshness, aggregate and row-level checks | Can output be replayed? Are writes isolated/idempotent? |
| Streaming consumer | Candidate consumer group on mirrored/replayed topic with isolated sink | Lag, deserialize errors, ordering, output counts, duplicate side effects | How are offsets and writes recovered? |
| ML inference/model service | Canary plus replay/shadow comparison where side effects are disabled | Latency, fallback ratio, output distribution, slice quality, feature freshness | Are model and preprocessing versions coupled? Can old model read current features? |

For each row add: risk tier, minimum sample/window, step size, pass/fail/inconclusive rules, capacity cost, data compatibility, rollback/roll-forward plan, owner, and evidence. Defend why a simpler strategy is insufficient or why an elaborate one is not worth the cost. **Pass:** all five worksheets are complete and each contains a measurable abort condition.

### Lab E — Baseline-versus-candidate signal review

**Level/time/resources:** L3, 30–45 minutes, spreadsheet or Python optional. Data below is synthetic `[ILLUSTRATIVE]`:

| Metric | Stable | Candidate | Absolute guardrail | Initial assessment |
|---|---:|---:|---:|---|
| 5xx rate | 0.4% | 0.5% | < 1.0% | Both pass absolute guardrail; compare relative change and uncertainty |
| p99 latency | 220 ms | 340 ms | < 400 ms | Absolute threshold passes but candidate is materially slower |
| CPU saturation | 55% | 58% | < 85% | Similar, but does not negate latency regression |
| fallback ratio | 1.0% | 4.5% | < 5.0% | Candidate approaches guardrail; investigate domain impact |
| valid candidate requests | 12 | 12 | Minimum 500 `[ILLUSTRATIVE]` | INCONCLUSIVE; do not promote |
| freshness metric | 2 min | missing | Must be present | INCONCLUSIVE/unsafe, not pass |

Review both absolute limits and stable-relative deltas. Explain why the latency regression should hold the rollout despite passing an absolute threshold; explain why missing/low-volume data must not pass. **Pass:** written decisions state metric availability, sample size, relative comparison and action for each row.

### Lab F — Release readiness and abort drill

**Level/time/resources:** L2/L3, 45–60 minutes. Use the local blue-green lab only. **Objective:** practice an abort before any automated rollout controller is introduced.

1. Fill in the rollout plan template in Section 18 and identify the person responsible for abort.
2. Confirm stable is active and healthy; capture baseline response and readiness state.
3. Introduce a harmless candidate defect by changing the candidate responder text to `candidate-degraded` or making the smoke test fail; do not add unsafe privileges or production endpoints.
4. Trigger the candidate exposure in the lab and detect the predeclared failure. Manually switch the Service back to blue. This is a **manual abort**, not automatic analysis.
5. Verify response content is stable, the stable Deployment remains ready, and synthetic checks recover. Record timestamps, route patch, observed errors and evidence.
6. Decide whether the defect can be rolled back or requires a roll-forward/compensating action; discuss database side effects even though this lab uses a stateless responder.

**Pass:** abort is performed from a written precondition, stable traffic is verified after the switch, recovery evidence is saved, and the learner explicitly states the limitations of a manual selector patch. If using only plain Kubernetes, do not claim automatic abort.

## 17. Reusable templates and checklists

### 17.1 Progressive-delivery strategy decision record

```yaml
service: <service-name>
owner: <team-or-role>
risk_tier: <tier>
chosen_strategy: <rolling|blue-green|replica-canary|route-canary|shadow|other>
reason: <why-this-fits-the-risk-and-capacity>
traffic_mechanism: <service-selector|replica-ratio|gateway|ingress-specific|mesh>
field_owners:
  deployment_replicas: <gitops|hpa|rollout-controller>
  route_weights: <gitops|rollout-controller|operator>
compatibility_window: <duration-and-compatibility-contract>
abort_owner: <role>
rollback_or_roll_forward: <procedure-reference>
verification_evidence: <artifact-location>
exception_expiry: <date-or-not-applicable>
reviewed_by: <approver>
```

### 17.2 Canary rollout plan

```yaml
release_id: <change-id>
stable_artifact_digest: <digest>
candidate_artifact_digest: <digest>
steps: [<traffic-or-cohort-steps>]
minimum_requests_per_step: <evidence-based-number>
minimum_window: <duration-including-metric-delay>
required_metrics: [<errors>, <latency>, <saturation>, <domain-signal>]
absolute_guardrails: <service-specific-values-and-source>
relative_guardrails: <candidate-vs-stable-rule>
missing_or_stale_data: inconclusive
promotion_owner: <role>
abort_owner: <role>
abort_action: <route-stable-and-verify>
rollback_window: <duration>
preflight_checks: [<readiness>, <smoke>, <compatibility>, <capacity>]
post_promotion_checks: [<synthetic>, <domain>, <downstream>]
```

### 17.3 Release readiness / rollback checklist

- [ ] Correct artifact digest and configuration revision verified.
- [ ] Stable and candidate are compatible with shared data/schema and downstream contracts.
- [ ] Candidate readiness and smoke/integration checks pass.
- [ ] Capacity headroom, HPA behavior and resource requests reviewed.
- [ ] Metrics have known freshness, minimum sample, and explicit missing-data behavior.
- [ ] Stable baseline and candidate are compared on equivalent request classes.
- [ ] Abort owner, trigger, routing action and recovery check are documented.
- [ ] Side effects, idempotency and compensating actions are understood.
- [ ] Evidence destination and incident/change ID are recorded.

### 17.4 Blue-green switch checklist

- [ ] Both environments are healthy and compatible with current database/data contracts.
- [ ] Candidate preview tests passed; old environment retained through rollback window.
- [ ] Router/Service change scope and exact selector/route are reviewed.
- [ ] In-flight connection, drain, timeout and retry implications are understood.
- [ ] Synthetic traffic measurement is running and baseline recorded.
- [ ] After switch, actual response/version, endpoints and user-facing signals are verified.
- [ ] Rollback is tested and stable traffic is verified before closing the change.

### 17.5 Incident timeline / evidence checklist

```text
Incident/change ID: <id>
Service / environment: <name>
Stable and candidate artifact/config revisions: <references>
First candidate exposure time: <UTC timestamp>
First adverse signal time and event time: <UTC timestamp>
Metric arrival/query freshness: <timestamps>
Decision / abort time: <UTC timestamp>
Traffic restored to stable time: <UTC timestamp>
SLO/application recovery time: <UTC timestamp>
Evidence: <sanitized route diff, request counts, metrics, events, Git/PR>
Root cause / contributing factors: <facts separated from hypotheses>
Corrective action / owner / due date: <record>
```

### 17.6 Post-release verification record

```text
Release ID: <id>
Candidate artifact/config: <digest/revision>
Observed traffic split: <measured counts and denominator>
Error/latency baseline vs candidate: <window and values>
Domain/ML/data checks: <results and sample size>
Downstream checks: <results or not applicable with reason>
Rollback window ended: <time and approver>
Open issues / owner: <items>
```

### 17.7 Risk exception record

```text
Service and release: <name/id>
Standard strategy not used: <strategy>
Reason and evidence: <specific constraint>
Risk assessment: <blast radius / reversibility / data effects>
Compensating controls: <checks and monitoring>
Approver: <role>
Exception starts / expires: <timestamps>
Review date and re-entry plan: <date / steps>
```

## 18. Troubleshooting playbook

| Symptom | Evidence and safe diagnostic sequence | Likely causes | Mitigation and prevention |
|---|---|---|---|
| Blue-green switch produces connection errors | Compare request timestamps with Service selector and EndpointSlice changes; inspect Pod termination and client retries | Endpoint propagation, existing connections, insufficient readiness, abrupt termination | Route back if safe; verify readiness and drain; use bounded idempotent retries; rehearse measured switch |
| Candidate receives almost no traffic | Inspect Service/route selectors, Pod readiness, route status, response body classifier and header/path | Label mismatch, no ready endpoints, route precedence, wrong host/path | Fix selector/route; run direct candidate smoke test; measure actual version tokens |
| Split differs from replica ratio or route weights | Inspect request count denominator, connection reuse, EndpointSlices, router conditions and endpoint load | Sampling noise, sticky connections, unsupported feature, uneven load | Increase sample, use per-request counter, validate router support, avoid equating config with measurement |
| Route accepted but traffic does not shift | Inspect `HTTPRoute` parent conditions/events, backend refs, listener hostname/port, route precedence | Accepted but wrong host, no programmed data plane, unresolved backend, controller limitation | Test exact host/path; verify controller documentation; revert to stable route until confirmed |
| Header test route does not match | Inspect exact header spelling/value, path, host, match order, and controller support | Header missing, route precedence, case/value mismatch, unsupported feature | Send exact test request; verify status and use an implementation-supported match |
| CPU looks healthy but latency/business signal regresses | Compare stable/candidate by request class; inspect queue, dependency, model fallback, tail latency and freshness | Lock contention, downstream wait, cold cache, algorithmic regression | Hold/abort; add domain and latency gates; test representative concurrency and input slices |
| Too little traffic for decision | Record denominator, eligible requests, window and metric freshness | Low volume or cohort bias | Mark inconclusive; extend window or use safe replay/synthetic checks; do not promote on no data |
| Metric lag causes unsafe promotion | Compare event, arrival, query and decision timestamps | Window shorter than pipeline delay; stale series treated as current | Gate on freshness and sample; inject lag in CI; fail closed to inconclusive |
| HPA causes oscillation/capacity pressure | Inspect HPA status/events, metrics, pending Pods, requests/limits and each version's load | Shared HPA target, replica floor too low, slow scale-up, competing writers | Reduce exposure; set ownership and capacity headroom; test HPA separately before canary |
| GitOps overwrites rollout state | Compare Git diff, live route/replicas and field ownership/controller events | GitOps and rollout controller own same field | Establish single field owner; adjust declarative boundary; verify reconciliation without competing writes |
| Cohort is not sticky | Correlate opaque cohort ID and version assignment across repeated requests | Client identity changes, router policy unsupported, affinity only by source IP | Use supported deterministic cohort routing; test retries, cookies and state compatibility |
| Rollback leaves candidate traffic or side effects | Measure responses after rollback; inspect route and EndpointSlices; check queue/database/event sinks | Multiple routes, existing connections, mirrored side effects, irreversible writes | Restore route and verify; stop side effects safely; compensate/roll forward; add post-abort checks |

Never start with destructive cleanup. First identify current context, live traffic, object ownership, and whether the suspected change is reversible. Preserve evidence before changing route or replica state when incident safety permits.

## 19. Glossary (operational extension)

- **EndpointSlice:** Kubernetes API object that tracks Service backend endpoints; see the [official EndpointSlice documentation](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/).
- **Connection draining:** a coordinated period in which a backend stops receiving new requests while existing requests/connections finish where the implementation supports it.
- **Metric propagation delay:** time between a real event and a query returning that event in the form used by the rollout decision.
- **N-1 compatibility:** the previous application version can safely operate with data written by the current version during the rollback window.
- **Inconclusive:** the evidence cannot justify either promotion or failure; the safe action is to hold, gather evidence, or follow a defined fallback.

## 20. Knowledge check and interview questions

### 20.1 Fifteen conceptual questions with answers

1. **Why separate deployment from release?** Deployment makes the artifact available; release controls who receives its behavior. Separation allows limited exposure and evidence-based decisions.
2. **Does a healthy Deployment prove the candidate is safe?** No. Readiness is not proof of business correctness, representative latency, or downstream data integrity.
3. **What do `maxSurge` and `maxUnavailable` control?** Temporary extra Pods and allowed unavailable Pods during a rolling update; neither defines request traffic percentage.
4. **Why is 1 of 10 Pods not a guaranteed 10% canary?** Traffic depends on endpoint selection, connection reuse, load duration, affinity, readiness and client behavior.
5. **What is the key difference between route-weighted and replica-weighted canary?** A router expresses per-request backend weights; replica weighting approximates share through endpoint population.
6. **Why compare candidate to stable?** It controls some shared temporal noise, but does not remove cohort bias or statistical uncertainty.
7. **What is a minimum sample gate for?** To avoid decisions from a denominator too small to detect meaningful changes. It must be derived from the service, not copied universally.
8. **What should happen when a critical metric is missing?** Treat the decision as inconclusive or unsafe and hold/abort according to policy, never silently pass.
9. **Why can a selector patch drop requests?** Control-plane state propagates asynchronously; in-flight connections and router/client behavior are separate.
10. **Does a PDB prevent all request failures?** No. It constrains eligible voluntary disruptions; it is not an application-level availability guarantee.
11. **Why can HPA and canary interfere?** Independent scale decisions alter capacity and observed traffic, and competing field writers may fight.
12. **Why are mirrored requests risky?** They can expose sensitive data, double load, or trigger writes/messages unless candidate side effects are isolated.
13. **When is rollback unsafe?** When new writes/events/external effects are incompatible or irreversible; use compatibility, roll-forward or compensating actions.
14. **Why is a canary not sufficient for ETL?** Silent row-level corruption and downstream failures may not produce HTTP errors; compare isolated outputs and data-quality signals.
15. **What proves a successful abort?** Stable traffic is measured again and service/domain signals recover; a successful command alone is not enough.

### 20.2 Eight strategy-selection scenarios

1. **Tier-0 API with meaningful traffic:** choose a route-weighted canary with baseline comparison, sufficient windows, capacity headroom and tested abort; justify against simple rolling update.
2. **Low-volume internal admin endpoint:** a rolling update plus smoke tests may be proportionate; a canary based on tiny error counts could be inconclusive.
3. **ETL transformation with expensive writes:** parallel isolated output and data diff; do not route a fraction of HTTP requests to test data correctness.
4. **Streaming consumer with side effects:** isolated consumer group and sink/replay; verify offsets, ordering and duplicate handling before switching production consumption.
5. **ML inference with costly prediction calls:** canary plus replay or shadow with side effects disabled; compare latency, fallback and distribution, and quality where labels exist.
6. **Stateful web app with sticky sessions:** use stable cohort assignment and cross-version state compatibility; do not assume Service ClientIP affinity is sufficient.
7. **A feature whose behavior can be toggled independently:** combine a safe deployment with a feature flag, but keep technical release gates and flag cleanup.
8. **A service with non-rollbackable schema changes:** use expand-contract and roll-forward/compensation plan before traffic exposure; a fast route switch cannot reverse incompatible data.

### 20.3 Five manifest/command review questions

1. **Defect:** stable and candidate Deployment selectors both match `app: scoring-api` and have no unique selector. **Answer:** controller ownership can overlap or be invalid depending on the exact selector; make each Deployment selector uniquely identify its own Pods while the Service may select both intentionally.
2. **Defect:** Service selector says `track: candidate`, but candidate Pods use `track: canary`. **Answer:** the Service has no matching endpoints; compare labels and EndpointSlices before blaming the router.
3. **Defect:** route weight is configured 90:10 and report claims exact 10% candidate without measurement. **Answer:** configuration is intent; measure versioned response counts and separate errors/unknown responses.
4. **Defect:** analysis treats an empty metric vector as zero errors. **Answer:** no series is not zero; classify missing data as inconclusive/unsafe and check freshness/labels.
5. **Defect:** `kubectl delete pods -l app=scoring-api` is used as a “rollback.” **Answer:** deletion is not rollback and controllers may recreate Pods; restore the intended route/artifact/config, verify traffic, and use lab-scoped cleanup only when appropriate.

### 20.4 Five troubleshooting scenarios: evidence → diagnosis → mitigation → prevention

1. **5xx rises after switch:** correlate errors with route/EndpointSlice timestamps; likely readiness/endpoint/draining issue; route back if safe and verify; prevent with switch rehearsal and readiness smoke checks.
2. **Candidate split is zero:** inspect route conditions, host/path/header and candidate endpoints; likely match or backend issue; restore stable-only route until fixed; add a request-level split test.
3. **Latency gate passes too early:** inspect metric timestamps/freshness; likely pipeline delay; stop progression and re-evaluate after full window; test delay in CI.
4. **HPA scales candidate to zero or too late:** inspect HPA target and metric availability; likely capacity/ownership mismatch; hold exposure and restore safe replica floor; document scale owner and test under load.
5. **Rollback still hits candidate:** inspect all matching routes, Services, endpoints and persistent connections; likely a second route or connection reuse; restore stable route and verify measured responses; include route enumeration and post-abort traffic proof.

### 20.5 Practical assessment

Design a release for a fictional `scoring-api` with stable version `v1`, candidate `v2`, shared database, moderate traffic, and a model preprocessing change. Submit: strategy and reason; stable/candidate routing; required technical/domain signals; minimum sample and window with metric delay; missing-data behavior; capacity and HPA ownership; data compatibility; abort owner and recovery check; post-promotion observation; and a risk exception if any gate is omitted. **Pass criteria:** every choice is defended, all thresholds are tied to a stated evidence source or marked illustrative, and rollback does not assume that database writes can be undone automatically.

### 20.6 Senior-level interview/design-review questions

1. **How would you choose between blue-green and route-weighted canary?** Explain risk, traffic, capacity, data compatibility, route support and rollback behavior.
2. **Why can a 5% canary miss a defect?** Insufficient sample, non-representative cohort, rare path, delayed metric, high-load-only failure or downstream lag.
3. **How do you prevent false promotion from stale telemetry?** Track freshness, enforce sample/window gates, align evaluation with propagation delay, and fail closed to inconclusive.
4. **How do you coordinate GitOps with a rollout controller?** Define single field owners, keep dynamic fields out of competing reconciliation, and test sync/health behavior for installed versions.
5. **What does a PDB guarantee?** Only specified voluntary disruption constraints within its semantics; not request-level success or protection from all failures.
6. **How would you canary an ML model?** Version model plus preprocessing, replay representative data, compare latency/fallback/distribution and validated quality slices, and isolate side effects.
7. **How would you roll back after incompatible writes?** Stop further harm, determine recoverability, use roll-forward or compensating actions, and preserve evidence; do not blindly restore old code.
8. **What evidence closes an abort incident?** Route and artifact revisions, measured stable traffic, recovery of technical/domain signals, event timeline, and assigned follow-up actions.

## 21. Final readiness checklist and completion gate

- [ ] Can explain all seven strategies and their limitations.
- [ ] Can distinguish deployment health from release health.
- [ ] Can measure actual traffic split and state the denominator.
- [ ] Can run the blue-green switch experiment and record dropped-request measurements honestly.
- [ ] Can explain replica weighting versus route weighting and verify Gateway API/controller compatibility.
- [ ] Can define sample/window, metric freshness, stable baseline, and inconclusive behavior.
- [ ] Can reason about HPA/PDB, readiness, draining, cohorts, and GitOps field ownership.
- [ ] Can design batch, streaming, and ML/model rollout checks with side-effect protection.
- [ ] Can complete the five-service strategy worksheet and baseline comparison.
- [ ] Has rehearsed a manual abort and verified stable traffic recovery.
- [ ] Has retained sanitized evidence and documented unresolved compatibility checks.

| Lab | Evidence to retain | Status |
|---|---|---|
| A — Blue-green switch | Baseline/switch/mitigated TSV, failure-rate calculation, limitations | [ ] Not run / [ ] Complete |
| B — Replica + route canary | 1,000+ request counts, route status, split comparison; route lab explicitly marked if unsupported | [ ] Not run / [ ] Complete |
| C — Too-fast analysis | Simulation output, timeline and corrected gate | [ ] Not run / [ ] Complete |
| D — Strategy worksheet | Five fully defended service decisions | [ ] Not run / [ ] Complete |
| E — Signal review | Baseline/candidate decisions including low-data and missing-data cases | [ ] Not run / [ ] Complete |
| F — Abort drill | Timeline, stable-response check, recovery evidence and manual-abort note | [ ] Not run / [ ] Complete |

Completion gate: the learner can demonstrate a measured, bounded release and a safe abort path; can explain where evidence is insufficient; and can preserve a clear ownership boundary between GitOps, autoscaling, routing, and rollout tooling. Completing the lesson alone does not establish production readiness.

When all labs are finished and evidence is saved, the optional whole-cluster cleanup is scoped to the explicitly named lab cluster:

```bash
# Host/WSL2 shell. Destructive: removes the entire disposable kind cluster named below.
# First verify the cluster name and that no useful workloads or evidence remain in it.
kind get clusters
kind delete cluster --name progressive-lab
```

Do not run the cluster deletion if you reused the cluster for anything outside this lesson. Namespace-scoped lab cleanup is preferred when preserving other local exercises.

## 22. Source/verification register

| Claim / feature | Source of truth | Version/environment sensitivity | Verification command/check | Status |
|---|---|---|---|---|
| Deployment rolling update, `maxSurge`, `maxUnavailable` | [Kubernetes Deployment docs](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/); [update tutorial](https://kubernetes.io/docs/tasks/run-application/update-deployment/) | Kubernetes API version and cluster | `kubectl explain deployment.spec.strategy`; inspect live Deployment | Verified against official docs consulted; validate installed cluster |
| Service selector and EndpointSlice behavior | [EndpointSlices docs](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/) | kube-proxy/CNI/router and propagation | `kubectl get endpointslices -l kubernetes.io/service-name=scoring-api -o yaml` | Verified against official docs consulted; observed lab behavior not run |
| HTTPRoute backend weights | [Gateway API HTTPRoute reference](https://gateway-api.sigs.k8s.io/reference/api-types/httproute/); [traffic splitting guide](https://gateway-api.sigs.k8s.io/guides/user-guides/traffic-splitting/) | Controller conformance and installed CRDs | `kubectl get crd httproutes.gateway.networking.k8s.io`; inspect route conditions and run 1,000+ requests | Verified API concept; controller support `[VERIFY]` |
| HTTPRoute header matches / precedence | [Gateway API HTTP routing](https://gateway-api.sigs.k8s.io/guides/user-guides/http-routing/) | Controller implementation and route merge behavior | Inspect controller docs, route status, test exact host/path/header | API concept verified; exact deployment `[VERIFY]` |
| Ingress weighted routing | Specific ingress-controller official docs (not selected universally) | Controller/version-specific annotation or feature | Identify controller/version, verify its docs and test split | Needs verification; no portable generic Ingress weight assumed |
| Request counter methodology | `measure-split.sh` included in this lesson | Client concurrency, keep-alive, network path, sample | Run script; compare response class counts with HTTP status and route config | Illustrative until learner runs it |
| Argo CD health semantics for Rollout CRDs | Installed Argo CD docs/configuration and Unit 8 | Version and custom health configuration | Inspect installed health customizations and Application status | Needs verification |
| Readiness, connection draining, session behavior | Kubernetes probes/termination docs plus router/client documentation | App protocol, router, client and mesh behavior | Test continuous requests during switch; inspect endpoints/events | Needs verification in target implementation |
| PDB behavior | [Kubernetes PDB docs](https://kubernetes.io/docs/tasks/run-application/configure-pdb/) | Eviction path and controller behavior | Inspect PDB status and test only in disposable cluster | Official concept reviewed; app-level outcome not guaranteed |
| Blue-green switch and drop measurement | Local scripts/manifests in this lesson | Local `kind`, port-forward, image availability | Run Lab A and retain TSV | Not executed by authoring environment |
| Metric delay simulation | `metric-lag-lab.py` in Lab C | Deterministic illustrative inputs | `python3 metric-lag-lab.py` | Simulation design; learner-run output only |
| Sample thresholds and step schedules | Service-specific historical evidence and SLOs | Traffic, risk, metrics and domain | Review against actual service SLO, volume and incident history | Illustrative; not a standard |

### Cross-unit boundary notes

- Unit 8 owns detailed Argo Rollouts and Flagger configuration, analysis providers, and rollout-controller integrations. This lesson does not install or configure those controllers.
- Unit 9 owns full automated release-health analysis and abort implementation; Lab F here is a manually triggered abort when using plain Kubernetes.
- Unit 10 deepens feature-flag lifecycle and dark launches; Unit 11 owns database/data-platform migration safety; Unit 12 owns API and pipeline compatibility; Unit 13 owns durable release evidence.
- M03 covers Deployments, readiness, HPA and PDB; M04 covers Ingress, Gateway API and mesh. M10 covers SLO/error-budget policy; M14 covers fleet/region rollout. Exact cross-module filenames were not confirmed in the available snapshot, so no guessed links are supplied.

### Final audit sign-off

- Scope audit: all Unit 7 curriculum themes and six labs represented in this lesson.
- Technical audit: manifests, commands, and scripts were reviewed for internal consistency; Python script is provided as source but was not executed against a cluster by this authoring environment.
- Measurement integrity: no measured request counts or live controller outputs are fabricated. Learner measurement cells are blank; simulation is labelled as simulation.
- Version verification: Gateway API resource support, route precedence, exact controller features, Argo CD Rollout health behavior, and local network/controller configuration remain `[VERIFY]` items.
- Repository safety: only the target lesson was intentionally written by this task; the output is under the working directory because a writable external repository checkout was not available. No sibling lesson, roadmap, syllabus, or project file was intentionally changed.

`UNIT-07-STATUS: DRAFT-AUDITED`
