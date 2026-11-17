# Unit 8 — Argo Rollouts, Flagger, and Traffic-Based Analysis

**Target file:** `08-argo-rollouts-flagger-and-traffic-based-analysis.md` | **Module:** M08 | **Stage:** 2E  
**Estimated time:** 12–18 hours, split across sessions | **Prerequisites:** Kubernetes Deployments/Services, readiness probes, HPA/PDB, Git, Helm/Kustomize, and Unit 7 progressive-delivery foundations  
**Core tools:** `kind`, `kubectl`, Argo Rollouts controller and CLI plugin, a local test service, optional local router/metrics provider  
**Awareness-level topics:** Flagger provider breadth, multi-region rollout governance, policy-engine patterns, advanced mesh integrations  
**Last reviewed:** 2026-10-28  
**Tool baseline assumed:** Kubernetes API compatible with the chosen `kind` node image; Argo Rollouts `argoproj.io/v1alpha1`; use a release tag or `<VERSION>` placeholder selected from official release documentation. Do not use `latest` as a production pin. `[VERIFY]`  
**Footprint:** Core labs: approximately 2–3 CPU, 3–5 GiB RAM, 10–15 GiB free disk for the local cluster and images. Optional router/metrics components add resource use; stop or delete them between labs. These are planning estimates, not measured results.

> **Status and provenance:** This is a teaching artifact. Commands and manifests are provided for learner execution; output marked **Representative `[ILLUSTRATIVE]`** is invented for explanation, not captured from a live cluster. No cluster execution is claimed. Verify all version-sensitive CRD fields against the installed schema before applying.

## 1. Learning outcomes

By the end of this unit, the learner should be able to:

- **[L1]** Explain why a native Deployment rolling update is not equivalent to metric-gated progressive delivery.
- **[L1]** Describe the Rollout, ReplicaSet, Service, AnalysisTemplate, AnalysisRun, and Experiment relationships.
- **[L1]** Install Argo Rollouts on a disposable `kind` cluster, inspect its CRDs/controller, and use the CLI plugin safely.
- **[L2]** Run replica-based canary and blue-green releases, including manual promotion, abort, preview checks, and traffic verification.
- **[L2]** Distinguish controller status from actual user traffic, and measure the real stable/canary split.
- **[L2]** Define analysis success, failure, and inconclusive outcomes so missing metrics cannot silently pass as healthy.
- **[L3]** Design candidate-versus-stable analysis windows, traffic preconditions, and Job-based data/ML checks.
- **[L3]** Diagnose HPA, PDB, GitOps ownership, route integration, and rollout-capacity interactions.
- **[L3]** Compare Argo Rollouts and Flagger using operational fit rather than declaring a universal winner.
- **[L4]** Operate upgrades, provider outages, stuck rollouts, abort drills, RBAC, and incident evidence with an explicit recovery plan.

## 2. How to use this lesson: safety, prerequisites, and laptop budget

Work through the labs in order. Use a throwaway cluster named `rollouts-lab`, namespace `scoring-lab`, and synthetic traffic only. Do not point commands at production. Before every mutating command, confirm the active context:

```bash
kubectl config current-context
kubectl cluster-info
kubectl get nodes -o wide
```

Expected pattern: the context is the disposable local cluster and its node is `Ready`. If the context is unexpected, stop. Keep a record of `kind`, Kubernetes, Argo Rollouts controller, and plugin versions. The CLI plugin and controller should be compatible; an older plugin may not understand newer fields.

### Component sequencing

| Phase | Components | Estimated footprint | Exit condition |
|---|---|---:|---|
| A | `kind`, scoring API, Argo Rollouts controller/plugin | 2–3 CPU, 3–4 GiB RAM | Replica canary and abort evidence saved |
| B | Reuse same cluster; add one compatible router only if verified | 2–3 CPU, 4–5 GiB RAM | Actual route split measured, or fallback blocker documented |
| C | Stop router if needed; add minimal metrics provider or use `web`/`job` provider after schema verification | 2–3 CPU, 4–5 GiB RAM | success/failure/no-data behavior proven |
| D | Blue-green and Job pre-promotion test | 2–3 CPU, 3–4 GiB RAM | preview and active traffic verified |
| E | Optional Flagger walkthrough or separate disposable cluster | Depends on provider | Comparison record completed |

Do not install Argo CD, Flux, Argo Rollouts, Flagger, Prometheus, an ingress controller, and a service mesh all at once. The lab does not require Argo CD or Flux. If you later test Flagger with Flux, use a separate phase and establish single ownership before deploying anything. On WSL2, `localhost` in a container means that container itself, not the Windows host or a different container. Use Kubernetes Services/DNS inside the cluster and `kubectl port-forward` for host access.

## 3. Repository cross-links and scope boundaries

The roadmap snapshot available during authoring identifies the following M08 sequence. Validate files in your working checkout before relying on a relative link:

- Unit 1 — GitOps principles and desired-state reconciliation (`01-gitops-principles-and-desired-state-reconciliation.md`): desired state and control-loop foundations. The file was not present in the current M08 working folder listing; verify its location before linking.
- Unit 2 — Argo CD Applications, Projects, and sync policies (`02-argo-cd-applications-projects-and-sync-policies.md`): Argo CD sync behavior; this unit does not re-teach it. The file was not present in the current M08 working folder listing; verify its location before linking.
- [Unit 3 — Flux controllers and Kustomize/Helm reconciliation](03-flux-controllers-and-kustomize-helm-reconciliation.md): Flux operational model and ownership.
- [Unit 4 — Repository layout and multi-environment promotion](04-repository-layout-and-multi-environment-promotion.md): environment promotion conventions.
- [Unit 5 — Configuration and secret reference management](05-configuration-and-secret-reference-management.md): configuration and secret references; do not put credentials in manifests.
- [Unit 6 — Deployment drift detection and reconciliation](06-deployment-drift-detection-and-reconciliation.md): field ownership, drift, and break-glass.
- [Unit 7 — Progressive delivery with canary and blue-green releases](07-progressive-delivery-with-canary-and-blue-green-releases.md): plain Kubernetes strategies and traffic measurement.
- `09-release-health-analysis-and-automated-abort.md`: deeper release-health policy and automated-abort design, if present.
- `10-feature-flags-and-dark-launches.md`, `11-database-and-data-platform-migration-safety.md`, `12-backward-compatible-pipeline-and-api-releases.md`, and `13-release-evidence-and-audit-trails.md`: feature flags, data compatibility, contracts, and evidence. Confirm exact paths in the checkout.

Prerequisite cross-module handoffs: M03 covers readiness, HPA, PDB, RBAC and admission; M04 covers ingress, Gateway API and service mesh; M10 covers SLOs/error budgets; M11 covers full observability; M12 covers policy-as-code; M14 covers multi-cluster/fleet operations. These are handoffs, not substitutes for the safety checks in this unit.

## 4. Why rollout controllers exist

A Deployment provides a useful rolling update with readiness gating and replica-management semantics. It does not, by itself, define a multi-step traffic plan with pauses, metric analysis, explicit manual promotion, traffic-router coordination, or automated rollback based on application signals. A rollout controller makes those decisions explicit and records state transitions.

The controller does not make a poor metric meaningful. If the canary receives no real traffic, a success-rate query returns an empty vector, or telemetry arrives after the next step, an apparently green rollout can still be unsafe. The control system is only as reliable as its observations and its abort path.

```text
Git desired Rollout + Pod template
              |
              v
      Rollouts controller -----> ReplicaSets / Pods
              |                         |
              |                         v
              +----> router config --> actual requests
              |                         |
              v                         v
      AnalysisTemplate <--- metrics / Job / web provider
              |
       pass / fail / inconclusive
              |
     pause / promote / abort
              |
              v
      verify route + version + SLO
              |
       evidence / incident record
```

Keep four states distinct:

1. **Git desired state**: the reviewed manifest and image reference.
2. **Kubernetes object/controller state**: Rollout status, ReplicaSets, pods, pause conditions and analysis runs.
3. **Traffic-router state**: weights, destinations, header routes and endpoint readiness.
4. **Observed application behavior**: requests actually served, latency/errors, business outputs, and downstream effects.

No single state proves the other three. Promotion is not complete until real traffic and application behavior are checked.

## 5. Argo Rollouts architecture and resource model

Argo Rollouts is a Kubernetes controller plus CRDs for progressive delivery. A `Rollout` uses `apiVersion: argoproj.io/v1alpha1` in documented examples; `[VERIFY]` the installed CRD and documentation for the chosen release. It replaces the Deployment controller as the owner of the workload's ReplicaSets when used as the primary workload object. Do not leave a separate Deployment managing the same application at the same time.

### Core objects

| Object | Purpose | Operational question |
|---|---|---|
| `Rollout` | Declares template, replicas, strategy, steps and analysis | What should be released and under what policy? |
| ReplicaSet | Owns a revision's pods | Which revision is running, ready, or scaled? |
| Stable Service | Identifies the stable revision for traffic routing | Is stable still serving requests after abort? |
| Canary Service | Identifies the candidate revision for router integrations | Is the candidate receiving real traffic? |
| Preview Service | Exposes the new revision before blue-green promotion | Can preview tests run without exposing users? |
| `AnalysisTemplate` | Names metric or Job checks and their conditions | What evidence determines pass/fail/inconclusive? |
| `ClusterAnalysisTemplate` | Cluster-scoped reusable analysis definition | Is shared policy governed and versioned? |
| `AnalysisRun` | A concrete execution of analysis | What did this rollout evaluate, and what was the result? |
| `Experiment` | Runs temporary ReplicaSet variants for comparisons | What short controlled comparison is being made? |

Canary strategy steps commonly include `setWeight`, `pause`, `analysis`, `setCanaryScale`, and `experiment`, but the exact step types and field behavior are version-sensitive. `[VERIFY]` the installed schema with `kubectl explain rollout.spec.strategy.canary.steps --recursive` and official Argo Rollouts canary documentation.

### Lifecycle sketch

```text
New Pod template detected
       |
       v
Create/update candidate ReplicaSet
       |
       v
Wait for candidate readiness
       |
       v
Apply next step: weight / pause / analysis
       |
       +-- analysis failure ------> abort / return traffic to stable
       |
       +-- inconclusive ---------> hold / require explicit decision
       |
       +-- pass ----------------> next step or promotion
                                  |
                                  v
                         candidate becomes stable
                         old revision scaled down per policy
```

The exact sequence depends on strategy and router integration. Always inspect status, events, ReplicaSets, Services, and actual requests rather than assuming the diagram is a literal state machine for every version.

## 6. Install on `kind` and run the first replica-based canary

### 6.1 Prerequisites and install

Host shell (WSL2 Ubuntu): install Docker, `kind`, `kubectl`, and `curl` using their official instructions. Choose and pin a Kubernetes node image compatible with your local `kind` release. Then:

```bash
kind create cluster --name rollouts-lab
kubectl config use-context kind-rollouts-lab
kubectl create namespace scoring-lab
kubectl create namespace argo-rollouts
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/<VERSION>/download/install.yaml
kubectl -n argo-rollouts rollout status deployment/argo-rollouts --timeout=180s
kubectl get crd rollouts.argoproj.io
kubectl explain rollout.spec.strategy --api-version=argoproj.io/v1alpha1
```

Replace `<VERSION>` with a release tag verified from the official [Argo Rollouts releases](https://github.com/argoproj/argo-rollouts/releases) page; do not paste angle brackets into the URL. If the tagged asset path differs, follow that release's installation instructions. The command shown is a template, not a claim that it has been run. Check the deployment name with `kubectl -n argo-rollouts get deploy` before using `rollout status`.

Install the plugin for your operating system from the same release. On Linux, use the release asset for `kubectl-argo-rollouts-linux-amd64` or the correct architecture, verify its checksum where provided, mark it executable, and put it in `PATH`. Then run:

```bash
kubectl argo rollouts version
kubectl argo rollouts help
kubectl -n argo-rollouts get pods -o wide
kubectl get crd | grep argoproj.io
```

Use `kubectl argo rollouts dashboard` only for local access. Bind only to loopback unless you deliberately configure safe network access. Recent releases changed dashboard binding defaults for security; `[VERIFY]` current release behavior in the release notes. Do not expose the dashboard to a public interface.

### 6.2 A small synthetic service

The lesson's examples use a public test image as a conceptual stand-in. For deterministic version identity and fault injection, build a local `scoring-api` image that returns JSON including `version`, `request_id`, and optional `fault_mode`. Keep its implementation simple and local; do not add external dependencies. If you use a public image in a quick first pass, verify its API and replace it before attempting the failure labs.

Illustrative response contract:

```json
{"service":"scoring-api","version":"stable","fault_mode":"none"}
```

The candidate should report `version: canary`. An optional `FAULT_MODE=error` can return HTTP 503; `FAULT_MODE=slow` can add a controlled delay. These are application behaviors, not Kubernetes features. The later labs require a real local app implementing this contract or a clearly marked mock. Never claim that a generic image implements this interface.

### 6.3 Complete first replica-based Rollout

Save as `lab-a/rollout-scoring-api.yaml`. This manifest uses an illustrative local image name; build/import it into `kind` or replace it with a verified image that implements the response contract. `setWeight` without a traffic router affects replica scaling rather than precise per-request weighting.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: scoring-api
  namespace: scoring-lab
spec:
  replicas: 4
  revisionHistoryLimit: 3
  selector:
    matchLabels:
      app: scoring-api
  template:
    metadata:
      labels:
        app: scoring-api
    spec:
      containers:
        - name: app
          image: scoring-api:stable
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 8080
          readinessProbe:
            httpGet:
              path: /health/ready
              port: http
            initialDelaySeconds: 2
            periodSeconds: 3
          resources:
            requests:
              cpu: 50m
              memory: 64Mi
            limits:
              cpu: 250m
              memory: 128Mi
  strategy:
    canary:
      steps:
        - setWeight: 25
        - pause: {}
        - setWeight: 50
        - pause:
            duration: 30s
```

`/health/ready` and port 8080 must exist in the local app; adapt them if the app differs. The sample values are `[ILLUSTRATIVE]`. No `stableService` or `canaryService` is required for a replica-based strategy with no traffic router.

```bash
kubectl apply -f lab-a/rollout-scoring-api.yaml
kubectl -n scoring-lab get rollout,rs,pods -o wide
kubectl -n scoring-lab describe rollout scoring-api
kubectl argo rollouts -n scoring-lab get rollout scoring-api --watch
```

When a new image/template is committed to the manifest, the controller creates a candidate ReplicaSet and progresses through steps. To exercise a candidate update, change `image: scoring-api:stable` to the locally available `scoring-api:canary`, then apply the updated manifest. Use a new digest or distinct local image name for real tests; mutable tags can obscure what was deployed.

Manual controls (confirm exact plugin syntax with `kubectl argo rollouts help` for the installed version):

```bash
kubectl argo rollouts -n scoring-lab promote scoring-api
kubectl argo rollouts -n scoring-lab abort scoring-api
kubectl argo rollouts -n scoring-lab retry scoring-api
kubectl argo rollouts -n scoring-lab undo scoring-api
```

These actions are not interchangeable. `promote` advances a paused rollout; `abort` stops the current update and returns the controller toward the stable revision; `retry` restarts a failed/aborted attempt according to current state; `undo` rolls back to a prior revision. `[VERIFY]` exact command and semantics against the installed plugin help and official CLI docs before using them. After any action, inspect actual Service endpoints, pod image IDs, rollout conditions, and requests. A successful CLI exit code is not proof of user recovery.

### 6.4 Verify version served

Use a local port-forward or a test pod. For example:

```bash
kubectl -n scoring-lab port-forward service/scoring-api 18080:80
```

This requires a Service manifest and a service port 80 targeting container port 8080; add the Service below if needed:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: scoring-api
  namespace: scoring-lab
spec:
  selector:
    app: scoring-api
  ports:
    - name: http
      port: 80
      targetPort: http
```

A shared Service selects pods by labels and does not provide exact request-weighted traffic. A single request returning `stable` or `canary` proves only that one request reached that version. Use a counter over many requests for any split claim.

## 7. Traffic routing and actual-weight verification

### 7.1 Router-controlled versus replica-based weights

Replica-based rollout: if one of ten ready endpoints is canary, the theoretical share is roughly 10% under equal independent selection, but connection reuse, endpoint distribution, unequal request cost, readiness and HPA can change the observed share. Router-controlled weights express a requested traffic distribution at the routing layer; the real split still must be measured.

| Router family | Potential fit | Caveat |
|---|---|---|
| Gateway API | `HTTPRoute` backend weights, if controller supports the needed API and version | Gateway API conformance does not mean every controller supports every feature identically; verify route status and implementation docs. |
| Ingress controller | Some products offer annotations or custom resources for weighted backends | Standard Kubernetes Ingress has no portable generic weighted-backend field. Never copy a vendor annotation to another controller. |
| Service mesh | Fine-grained routing and richer traffic policy | Higher memory and operational complexity; optional for an 8 GiB laptop. |
| Cloud load balancer | Can integrate with vendor target groups and routing | Cloud-specific, often not a zero-budget local lab. |

Argo Rollouts traffic-router integrations are release- and provider-specific. Verify the exact plugin, controller, Kubernetes/Gateway API versions, and documented constraints. The official Argo Rollouts traffic-management documentation and the router's compatibility matrix are the source of truth. Do not label a fallback replica lab as a successful route-weighted lab.

### 7.2 Generic Gateway API reference pattern `[VERIFY]`

The following is a **reference shape**, not guaranteed copy-paste configuration. Confirm that Gateway API CRDs are installed and that the chosen controller supports weighted `HTTPRoute` backends and any Rollouts plugin integration. The backend Services must exist and select the intended stable/canary pods.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: scoring-api
  namespace: scoring-lab
spec:
  parentRefs:
    - name: lab-gateway
  hostnames:
    - scoring.local
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /
      backendRefs:
        - name: scoring-api-stable
          port: 80
          weight: 90
        - name: scoring-api-canary
          port: 80
          weight: 10
```

This route does not automatically connect itself to Argo Rollouts. The actual traffic-router plugin or controller-specific integration must be configured according to its own docs. Header-based test routes (`setHeaderRoute` or equivalent) are also plugin-specific; `[VERIFY]` before use.

Inspect:

```bash
kubectl get httproute -n scoring-lab scoring-api -o yaml
kubectl describe httproute -n scoring-lab scoring-api
kubectl get events -n scoring-lab --sort-by=.lastTimestamp
kubectl get svc,endpointslice -n scoring-lab -o wide
kubectl get pods -n scoring-lab --show-labels
```

Look for accepted/resolved references and controller-specific conditions. The precise status condition set depends on Gateway API version and implementation. If the route is accepted but canary receives zero requests, inspect actual backend references, selectors, endpoints, host/path match, listener attachment, and the controller plugin's events. Route object status is not traffic telemetry.

### 7.3 Measure at least 1,000 requests

Use a local endpoint that returns a JSON `version` field. Save as `measure-split.py`:

```python
#!/usr/bin/env python3
"""Count actual responses by version; standard library only."""
import collections
import json
import sys
import urllib.error
import urllib.request

url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:18080/"
count = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
counts = collections.Counter()
failures = 0
for _ in range(count):
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            body = json.loads(response.read().decode("utf-8"))
            counts[str(body.get("version", "missing-version"))] += 1
    except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
        failures += 1
received = sum(counts.values())
print(f"requested={count} received={received} failures={failures}")
for version, number in sorted(counts.items()):
    pct = (100.0 * number / received) if received else 0.0
    print(f"{version}: {number} ({pct:.2f}% of successful responses)")
```

Run from the host shell against a port-forward or local route. This script counts completed HTTP responses, not dropped packets or requests that never reached the client. Record the intended weight, request count, successful responses, failures, stable count, candidate count, and observed candidate percentage. Do not fill in measured counts until you run it.

| Intended split `[ILLUSTRATIVE]` | Requested requests | Stable count | Candidate count | Failures | Observed candidate % |
|---|---:|---:|---:|---:|---:|
| 90/10 | 1,000 | ______ | ______ | ______ | ______ |
| 50/50 | 1,000 | ______ | ______ | ______ | ______ |
| 100/0 after abort | 1,000 | ______ | ______ | ______ | ______ |

Sampling variation is expected; connection pooling, retries and request mix can bias results. If a candidate gets 0% traffic, treat analysis as **inconclusive/unsafe**, not as a healthy canary.

## 8. Blue-green Rollouts and preview/promotion checks

Blue-green runs a stable active version and a candidate preview version. Promotion changes which revision the active Service targets. It preserves a fast rollback option only while the old version and compatible data remain available. Service selector or route changes are control-plane operations, not guarantees of instantaneous global data-plane switching.

### 8.1 Example manifest

Save as `lab-d/bluegreen.yaml`. Image and readiness path are illustrative and must match your local app. Verify fields against the installed CRD.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: scoring-api-active
  namespace: scoring-lab
spec:
  selector:
    app: scoring-api
  ports:
    - name: http
      port: 80
      targetPort: http
---
apiVersion: v1
kind: Service
metadata:
  name: scoring-api-preview
  namespace: scoring-lab
spec:
  selector:
    app: scoring-api
  ports:
    - name: http
      port: 80
      targetPort: http
---
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: scoring-api
  namespace: scoring-lab
spec:
  replicas: 3
  revisionHistoryLimit: 3
  selector:
    matchLabels:
      app: scoring-api
  template:
    metadata:
      labels:
        app: scoring-api
    spec:
      containers:
        - name: app
          image: scoring-api:stable
          ports:
            - name: http
              containerPort: 8080
          readinessProbe:
            httpGet:
              path: /health/ready
              port: http
  strategy:
    blueGreen:
      activeService: scoring-api-active
      previewService: scoring-api-preview
      autoPromotionEnabled: false
      scaleDownDelaySeconds: 30
```

Important: both Services have the same selector in this teaching shape because the controller updates revision-specific pod-template labels used by Rollouts; confirm exact selector mutation/label behavior for the installed version and inspect the rendered Services after applying. Do not assume a static `app` label alone differentiates stable and preview. If the installed schema rejects the manifest or the Services do not target the intended ReplicaSets, stop and follow the official blue-green example for that release. `prePromotionAnalysis`, `postPromotionAnalysis`, and `scaleDownDelaySeconds` are version-sensitive fields and should be added only after validating `kubectl explain rollout.spec.strategy.blueGreen --recursive`.

A blue-green readiness workflow:

1. Apply the Rollout and Services; confirm stable active traffic.
2. Update the pod template to the candidate image digest.
3. Wait for preview pods to be ready.
4. Run smoke, contract, data-quality, and latency checks against the preview Service.
5. Inspect active and preview endpoints and verify version identity.
6. Promote only after evidence and an authorized decision; otherwise abort/revert.
7. Verify actual requests are served by the new stable revision.
8. Keep the old ReplicaSet available for the agreed rollback window; only scale it down when the data and release safety plan permits.

`scaleDownDelaySeconds` delays scaling down the previous ReplicaSet; it does not by itself drain every connection or guarantee rollback safety. In-flight requests, long-lived connections, clients with cached endpoints, and external side effects need their own handling.

## 9. AnalysisTemplate, ClusterAnalysisTemplate, AnalysisRun, and Experiment

`AnalysisTemplate` defines reusable metric checks. `ClusterAnalysisTemplate` provides a cluster-scoped reusable template. An `AnalysisRun` is a concrete evaluation with measurements and an outcome. `Experiment` runs temporary versions/ReplicaSets to compare behavior; it is not automatically a statistically sound product A/B experiment.

The exact provider fields and expression engine semantics are version-sensitive. Before applying an analysis manifest:

```bash
kubectl explain analysistemplate.spec --recursive
kubectl explain clusteranalysistemplate.spec --recursive
kubectl explain analysisrun.status --recursive
kubectl get crd analysistemplates.argoproj.io -o yaml
```

### 9.1 Provider choices

| Provider | Good use | Risk / verification |
|---|---|---|
| Prometheus | Error rate, latency, saturation, traffic preconditions | Query labels, result type, empty-vector semantics, and `successCondition` expression need testing. |
| `web` | Query a local JSON endpoint or small metric adapter | HTTP response shape and provider fields are version-specific; protect endpoint and bound timeout. |
| `job` | Smoke test, contract test, synthetic data validation | Job exit status is only as meaningful as its assertions; set resource limits and timeout. |
| Datadog, New Relic, Wavefront, Kayenta, CloudWatch | Existing enterprise telemetry | Awareness only here; provider schema, credentials, permissions, and support vary by release. `[VERIFY]` |

Metric credentials should be stored in an approved secret system and mounted/referenced with least privilege. Do not put API keys in Git, command history, or analysis manifests.

### 9.2 Illustrative Prometheus analysis template

This example is a schema pattern; verify the installed version and adapt the query/labels. A query that returns an empty vector must not be allowed to pass simply because the expression does not evaluate to false.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: scoring-api-error-rate
  namespace: scoring-lab
spec:
  args:
    - name: service
      value: scoring-api
  metrics:
    - name: error-rate
      interval: 1m
      count: 3
      failureLimit: 1
      successCondition: "len(result) == 1 && result[0] < 0.02"
      failureCondition: "len(result) == 1 && result[0] >= 0.02"
      provider:
        prometheus:
          address: http://prometheus.monitoring.svc:9090
          query: |
            sum(rate(http_requests_total{service="{{args.service}}",status=~"5.."}[5m]))
            /
            clamp_min(sum(rate(http_requests_total{service="{{args.service}}"}[5m])), 1)
```

`len(result)` and boolean expression behavior must be validated against the exact Argo Rollouts release; do not assume this snippet is guaranteed compatible without testing. Prometheus must actually expose the `http_requests_total` metric with these labels. The sample threshold and intervals are `[ILLUSTRATIVE]`, not service standards. `clamp_min` prevents a zero denominator from becoming division-by-zero, but it does not prove there was enough traffic. Add an explicit traffic-volume precondition and treat missing/insufficient samples as inconclusive or failed according to policy.

Apply and inspect only after the Prometheus Service exists and the CRD schema has been verified:

```bash
kubectl apply -f analysis-template.yaml
kubectl -n scoring-lab get analysistemplate scoring-api-error-rate -o yaml
kubectl -n scoring-lab get analysisrun -o wide
kubectl -n scoring-lab describe analysisrun analysisrun-example-name  # replace with the name returned above
```

Use a concrete AnalysisRun name copied from the `get` output; angle-bracket text is a placeholder, not a runnable argument.

### 9.3 Outcome policy

- **Successful:** the required number of valid measurements meet the success condition, and traffic/sample preconditions were met.
- **Failed:** a defined failure condition is met or failure policy is exceeded.
- **Inconclusive:** available evidence is insufficient or falls between explicitly defined conditions. Hold for investigation; do not auto-promote.
- **Error:** the provider or query execution failed. Treat as unsafe/inconclusive or fail-closed according to an explicit release policy; never reinterpret provider outage as application health.

Fields such as `failureLimit`, `inconclusiveLimit`, `interval`, `count`, `initialDelay`, and `args` have version-specific semantics. `[VERIFY]` with `kubectl explain analysistemplate.spec.metrics --recursive` and official analysis documentation. Build a test matrix for normal values, above-threshold values, empty results, malformed results, provider timeout, and low traffic before production use.

## 10. Canary-versus-stable analysis, windows, and anti-flapping

Absolute thresholds answer “is the candidate above a limit?” Comparative analysis also asks “is the candidate materially worse than stable under similar conditions?” The second question can control for time-of-day variation, but it can be fooled if stable and canary receive different request types or if the metric labels are wrong.

Example review questions:

- Are stable and canary distinguished by a reliable version label or ReplicaSet hash?
- Does the query return one numeric sample per revision, or an empty vector?
- Are both cohorts receiving enough requests to compare?
- Does the query's unit match the threshold (ratio vs percentage; seconds vs milliseconds)?
- Does the evaluation window exceed scrape, aggregation, and telemetry propagation delay?
- Are retries or duplicate samples hiding user-visible failures?

Labels such as `rollouts-pod-template-hash`, `canary`, or `stable` depend on instrumentation and controller integration. `[VERIFY]` by querying actual metrics and inspecting the installed Rollout/Service labels. Do not copy a label from an example and assume it exists.

### Timing example `[ILLUSTRATIVE]`

| Time | Event | What analysis can see |
|---|---|---|
| 12:00:00 | Candidate begins receiving traffic; 5xx defect starts | New errors occur, but scrape has not completed |
| 12:00:15 | Short analysis evaluates | Query may still show old/empty samples; unsafe early pass possible |
| 12:00:30 | Scrape records errors | Data begins entering metrics pipeline |
| 12:01:00 | Aggregation and query window include error samples | Failure becomes visible |
| 12:01:15 | Evaluation occurs after configured delay | Corrected policy detects regression before next step |

The rollout cannot react faster than the metric pipeline. Longer steps alone are not enough; require minimum sample counts, guard missing data, and choose an evaluation cadence consistent with telemetry delay. Repeated testing against the same noisy data can create false positives; testing many metrics/steps raises the chance of a false alarm. Autocorrelation means adjacent samples are not independent. For low traffic, extend the window or classify as inconclusive rather than claiming statistical confidence.

Step analysis evaluates at a point in the rollout. Background analysis, where supported and configured, evaluates during progression. Use step analysis for explicit gates at defined exposure levels; use background analysis for continuous observation when its lifecycle and abort behavior are understood. Do not let overlapping windows or delayed metrics create a false green signal.

## 11. Job-based data/ML checks and Experiments

A Kubernetes Job can test a candidate in a repeatable, isolated way before or during a rollout. Examples include:

- replay a synthetic dataset through stable and candidate model endpoints and compare output distributions;
- check row counts, null rates, schema, freshness, and a bounded sample of data;
- run an API contract test against candidate and verify old-client compatibility.

A Job's exit code should reflect explicit assertions. Include timeout/deadline, bounded retries, CPU/memory requests and limits, and read-only input credentials. Use synthetic fixtures; avoid real customer data. Make the Job idempotent. If it writes data, isolate its output to a disposable namespace/table/bucket and avoid duplicate side effects.

### Example smoke-test Job pattern

This job assumes a local image `scoring-smoke-test:local` that performs HTTP assertions against the preview Service and exits non-zero on failure. Build/import the image first. It is a reference pattern, not a claim that the image exists.

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: scoring-preview-smoke
  namespace: scoring-lab
spec:
  backoffLimit: 0
  activeDeadlineSeconds: 60
  template:
    metadata:
      labels:
        app: scoring-preview-smoke
    spec:
      restartPolicy: Never
      containers:
        - name: smoke
          image: scoring-smoke-test:local
          imagePullPolicy: IfNotPresent
          env:
            - name: BASE_URL
              value: http://scoring-api-preview.scoring-lab.svc.cluster.local
          resources:
            requests:
              cpu: 50m
              memory: 64Mi
            limits:
              cpu: 250m
              memory: 128Mi
```

A successful Job only proves its assertions passed for its tested cases. It does not prove rare paths, peak load, or downstream nightly consumers are safe. Use `Experiment` for a bounded version comparison where the installed API and strategy support it; do not confuse this controller resource with randomization, sample-size planning, or causal analysis required for a product A/B test. `[VERIFY]` exact Experiment fields and semantics against the installed CRD.

## 12. HPA, PDB, capacity, and advanced rollout controls

Progressive delivery consumes extra capacity: stable and candidate may coexist, blue-green can require near-doubling application capacity, and analysis Jobs add temporary pods. Calculate CPU, memory, connection pools, downstream quotas, and node scheduling before increasing replicas. Use `requests` that reflect real needs; limits and throttling can distort latency analysis.

- **HPA:** stable and candidate may need separate scaling policies or a Rollout-targeted HPA. Whether HPA targets the Rollout and how dynamic stable scaling interacts with traffic routing are `[VERIFY]` for the selected release. Inspect `kubectl explain horizontalpodautoscaler.spec.scaleTargetRef` and Argo Rollouts HPA documentation.
- **PDB:** controls voluntary disruption budgets; it does not guarantee application-level request completion or make a traffic switch safe.
- **Anti-affinity/topology spread:** reduce correlated failure but may make candidate scheduling impossible on a small local cluster.
- **`dynamicStableScale`, `abortScaleDownDelaySeconds`:** version-sensitive Rollout controls. `[VERIFY]` schema, exact semantics, and interactions with HPA/abort before adopting them.
- **Router failure:** stop progression and inspect actual routes. Do not assume abort automatically repaired every external route; prove stable-only traffic after abort.

Capacity worksheet `[ILLUSTRATIVE]`:

| Item | Stable | Candidate/preview | Analysis/overhead | Total requirement |
|---|---:|---:|---:|---:|
| CPU requests | ____ | ____ | ____ | ____ |
| Memory requests | ____ | ____ | ____ | ____ |
| Replicas | ____ | ____ | ____ | ____ |
| Connections / downstream quota | ____ | ____ | ____ | ____ |
| Required headroom | ____ | ____ | ____ | ____ |

If the cluster cannot schedule candidate pods, a stalled rollout is a capacity problem—not a reason to disable readiness or force promotion.

## 13. Argo CD/GitOps integration and field ownership

A GitOps controller manages declarative desired state. Argo Rollouts manages progression and may mutate runtime-controlled fields, ReplicaSets, Services, and status. Conflict occurs when GitOps continuously re-applies a value that the rollout controller must change, or when both a Deployment and Rollout are present for the same app.

Ownership map example:

| Field/resource | Declarative owner | Runtime controller | Rule |
|---|---|---|---|
| Pod template image digest | Git review / promotion PR | Rollouts observes change | Change through reviewed Git path |
| Rollout strategy/steps | Git | Rollouts executes | Git owns policy, not runtime status |
| ReplicaSets/pods | Rollouts | Rollouts | Do not manage independently in Git |
| Traffic weights | Rollouts plus supported router integration | Router/plugin | One defined writer for weights |
| AnalysisRun/status | Rollouts | Rollouts | Observe status; do not hand-edit |
| Service selector labels used by routing | Explicitly documented integration contract | Rollouts/router as supported | Do not use broad ignores to hide drift |

Argo CD health interpretation for Rollout CRDs depends on installed version and customization. `[VERIFY]` official Argo CD custom-health documentation and local resource health. If a Rollout is healthy in Kubernetes but degraded/out-of-sync in Argo CD, inspect the exact diff, health customization, and field managers. If Argo CD is green but requests fail, investigate application and traffic telemetry; UI status is not a substitute for service verification.

Converting a Deployment to a Rollout requires a controlled migration. Do not simply apply a Rollout with the same selector while leaving the Deployment active: both can control overlapping pods. Inventory ownership, prepare a rollback plan, choose whether to replace the Deployment or use the documented `workloadRef` pattern, verify the installed schema, and rehearse on a disposable namespace. `[VERIFY]` conversion semantics and `workloadRef` behavior for the exact version. Record rollout events, image digests, approval, analysis results, actual traffic split, and abort/promotion actions; see Unit 13 for release evidence.

## 14. Flagger architecture and Rollouts-versus-Flagger comparison

Flagger is a progressive-delivery controller that watches a target workload and a `Canary` custom resource, then coordinates primary/canary workload state, traffic shifting, metric checks, and webhook gates. The CRD API group is commonly `flagger.app`; verify the installed API version and provider support before applying examples. Flagger can integrate with multiple mesh/ingress/Gateway providers, but support and compatibility are not interchangeable.

Concepts to recognize:

- `Canary`: declares target workload, service/routing settings, analysis schedule and promotion policy.
- Primary/canary resources: Flagger's operating model may create a primary copy and scale the original target workload down; verify exact behavior for the provider/version.
- `MetricTemplate`: reusable query/provider definition.
- Webhooks: pre-rollout, rollout, confirm-traffic-increase, confirm-promotion, post-rollout or load-test hooks depending on version/configuration. Hook names and semantics are `[VERIFY]`.
- GitOps: Flagger is commonly paired with Flux workflows; Argo CD can interoperate but needs careful ownership/tracking of controller-created resources. Do not have GitOps and Flagger both independently own the same mutable fields.

Current maintenance/community status changes over time. Verify the official Flagger repository release activity, issue/maintenance notes, docs, and provider matrix during selection; do not infer status from an old tutorial.

| Dimension | Argo Rollouts | Flagger |
|---|---|---|
| Workload model | `Rollout` CRD replaces Deployment controller behavior for the workload | `Canary` CRD orchestrates target workload and controller-managed primary/canary resources |
| Progression | Explicit steps, pauses, promotion/abort | Analysis iterations and traffic progression driven by Canary policy |
| Analysis | `AnalysisTemplate`, `AnalysisRun`, providers and Jobs | Metric providers, `MetricTemplate`, webhooks/load tests |
| Router integration | Provider/plugin-specific; verify supported integration and release | Provider-specific mesh/ingress/Gateway support; verify current matrix |
| Blue-green / experiments | Native strategies and Experiment object, with version checks | Capabilities vary by provider and current Flagger release; verify |
| CLI/UX | `kubectl argo rollouts`, dashboard | Kubernetes resources, events/logs, metrics and provider tooling |
| GitOps fit | Natural fit with Argo CD but also usable with other GitOps controllers under ownership rules | Commonly used with Flux; Argo CD needs careful resource tracking/ownership |
| Complexity | CRDs, controller, optional router/metrics | CRDs, controller, provider integrations, metrics/webhooks |
| Best fit | Teams wanting explicit rollout step control and Rollouts-native analysis | Teams wanting provider-integrated progressive delivery and Flagger's operating model |

Choose based on team skills, router compatibility, analysis requirements, controller ownership, evidence needs, resource budget, upgrade burden, and support/maintenance signals. Neither is mandatory for every service. Plain Deployment rolling updates may be enough for low-risk internal services with good readiness checks and no need for metric-gated traffic progression.

### Guided Flagger reference shape `[VERIFY]`

Do not apply the following as a guaranteed manifest; confirm current schema and provider-specific fields in official Flagger docs first:

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: scoring-api
  namespace: scoring-lab
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: scoring-api
  progressDeadlineSeconds: 60
  service:
    port: 80
  analysis:
    interval: 1m
    threshold: 5
    maxWeight: 50
    stepWeight: 10
```

API version, required fields, strategy and service fields are provider/version-sensitive. Check `kubectl get crd canaries.flagger.app -o yaml`, `kubectl explain canary.spec --recursive`, and the official Flagger Canary documentation. Any displayed status should be marked **Representative `[ILLUSTRATIVE]`** unless captured from a real run.

## 15. Production operations, upgrades, RBAC, notifications, and recovery

### Controller/CRD upgrades

1. Record current controller, CRD, plugin, router and metric-provider versions.
2. Read release notes for breaking changes and migration notes.
3. Back up CRDs and rollout/analysis resources using sanitized manifests; never export secret values into evidence.
4. Test schema and existing manifests in a disposable cluster with the target version.
5. Upgrade controller and CRDs in the documented order; verify leader/replica health and rollout reconciliation.
6. Rehearse downgrade/recovery. CRD schema changes may not be safely reversible just by rolling back a controller image.
7. Keep a change record and monitor all in-flight rollouts through the upgrade.

### Failure recovery matrix

| Failure | Check current traffic first | Safe containment | Recovery and proof |
|---|---|---|---|
| Controller unavailable mid-rollout | Route weights, Services, endpoints, current versions | Freeze further release changes; do not blindly scale/delete pods | Restore controller/version, inspect Rollout status/events, measure stable/candidate traffic |
| Metrics provider unavailable | Last valid sample time and candidate exposure | Hold progression; apply fail-closed/inconclusive policy | Restore provider, validate query manually, re-run analysis only under approval |
| Rollout stuck at pause | Pause condition, events, analysis status | Keep current traffic exposure bounded | Confirm required checks and authorized promotion/abort; capture decision |
| Router plugin failure | Route config, controller events, actual split | Route to known stable path only using documented safe method | Fix integration, test split with ≥1,000 requests, prove abort and promotion paths |
| HPA/capacity conflict | Desired/available replicas, pending pods, resource saturation | Stop step advancement; preserve stable capacity | Correct target/requests/floors and rehearse scaling/abort |
| GitOps conflict | Git diff, Rollout spec/status, events and managed fields | Avoid repeated manual edits; identify field owner | Narrow ownership contract, update Git, reconcile once, verify no churn |

### Manual intervention governance

Only an authorized release owner/on-call should promote, abort, retry, or undo. Require a ticket/incident ID, reason, current traffic evidence, risk assessment, approver, command/action, timestamp, resulting revision, and verification. A CI job may gate promotion, but must use short-lived least-privilege identity, emit audit evidence, and not bypass policy by patching resources without review.

RBAC should separate read-only observation from promotion/abort privileges. Avoid cluster-admin for routine release actions. Restrict metric-provider credentials to read-only queries where possible; Jobs should use narrow service accounts and read-only data access. Retain controller events and analysis results long enough to support incident review. Notifications should contain useful resource identifiers and links without leaking credentials or sensitive payloads.

## 16. Fault injection and automated-abort drill

The objective is to prove the safety mechanism in a local cluster. Use a candidate build with a controlled `FAULT_MODE=error` or `FAULT_MODE=slow` environment variable. Set an explicit precondition: stable is healthy, candidate identity is visible, route or replica exposure is known, and the rollback path has been rehearsed.

Expected flow:

1. Commit/apply the candidate template through the intended desired-state path.
2. Verify candidate pods ready and actually receiving traffic.
3. Confirm metric samples include candidate requests and are fresh enough.
4. Observe the configured analysis result.
5. On failure, verify progression stops/aborts and traffic returns to stable.
6. Measure actual stable/candidate requests after abort and verify application health recovers.
7. Revert the Git desired image or commit a fixed image; an abort in live cluster state does not automatically amend Git.
8. Record timeline and preserve sanitized evidence.

| Event | Timestamp | Evidence | Expected/observed |
|---|---|---|---|
| Candidate requested | ____ | Git commit / Rollout spec | ____ |
| Candidate first request | ____ | Version counter | ____ |
| Fault visible in metric | ____ | Query result timestamp | ____ |
| Analysis failed/inconclusive | ____ | AnalysisRun | ____ |
| Abort action | ____ | Event/command record | ____ |
| Stable traffic recovered | ____ | 1,000-request measurement | ____ |
| Git fixed/reverted | ____ | PR/commit | ____ |

Do not fill “observed” fields with invented numbers. If the local setup cannot support router-based analysis, record the blocker and perform a manual abort drill only; do not claim automated abort was proven.

## 17. Policy-as-code and golden paths

At Awareness level, policy rules can require tier-0 Rollouts to reference an approved analysis template, forbid production auto-promotion without analysis, and require image digests, readiness probes, resource requests, and an abort owner. Kyverno/Gatekeeper syntax and admission context are version-specific `[VERIFY]`; test policy against valid and invalid fixtures before enforcement. False positives can block emergency recovery, so define a reviewed exception path with expiry and audit evidence.

A golden path should provide a supported Rollout skeleton, approved analysis templates, required labels, standard dashboard/alerts, safe RBAC, traffic verification scripts, release evidence format, and a rollback drill. Avoid a single global threshold for all services. Link policy implementation to M12 and full observability to M11.

## 18. Rollout observability and query scale

Observe both control-plane and application signals:

- controller reconciliation/errors and queue/latency metrics, where exposed by the chosen version;
- Rollout phase, pause condition, ReplicaSet readiness, AnalysisRun outcomes and Kubernetes events;
- route weights, accepted/resolved route conditions, endpoint membership, and measured version split;
- per-version error rate, latency percentiles, saturation, queue depth, data freshness, and domain/ML quality signals;
- analysis query errors, empty samples, staleness, and provider latency.

Use stable, bounded labels such as service, environment, version and region. Avoid user IDs, request IDs or unbounded feature values as Prometheus labels. Recording rules can reduce repeated expensive query cost, but test that they preserve the candidate/stable distinction. Rollout telemetry proves controller decisions; application SLO telemetry proves user impact. They are related but not interchangeable.

## 19. Incident casebook

Each incident should be handled with a repeatable sequence: protect users, inspect actual traffic, preserve evidence, identify the owning controller/field, restore safe behavior, then fix the desired state and add a regression test.

### Case 1 — Analysis returned no data but promoted

- **Symptoms:** candidate progresses while query dashboard shows gaps or zero series.
- **Evidence:** AnalysisRun measurements, raw provider response, query labels, scrape timestamps, candidate request count.
- **Likely cause:** empty vector did not evaluate as failure, query label mismatch, no candidate traffic, or provider error treated as benign.
- **Immediate action:** stop progression; if exposure is unsafe, use the authorized abort path and verify stable traffic.
- **Durable fix:** explicit result-length/traffic guards; empty and provider-error fixtures; inconclusive/fail-closed policy; alert on missing series.
- **Prevention test:** deliberately remove the metric series and prove the rollout cannot promote.
- **Lesson:** no data is not evidence of health.

### Case 2 — Stable Service selector changed during abort and traffic black-holed

- **Symptoms:** abort reported but requests fail or no endpoints match.
- **Evidence:** Service selectors, pod labels, EndpointSlices, rollout events, route config, request counter.
- **Likely cause:** manual selector patch, integration mismatch, controller and GitOps fighting, or assumptions about stable labels.
- **Immediate action:** inspect before changing; restore a known-good route/selector using the documented integration recovery procedure.
- **Durable fix:** define one owner for selector/route fields; test abort and rollback against the exact version.
- **Prevention test:** run a bad candidate and verify stable endpoints and 1,000 post-abort requests.

### Case 3 — Candidate received 0% real traffic

- **Symptoms:** analysis is green but candidate request counter stays at zero.
- **Evidence:** route status, backend references, Service/EndpointSlice, host/path/header match, router plugin logs, per-version metrics.
- **Likely cause:** plugin failure, wrong backend name, no ready candidate endpoints, host mismatch, or test traffic bypassing router.
- **Immediate action:** classify as inconclusive and stop progression.
- **Durable fix:** add a minimum candidate request precondition and route smoke test.
- **Prevention test:** fail a release when candidate request count remains zero.

### Case 4 — Rollout and Deployment both existed

- **Symptoms:** duplicate pods, conflicting replica counts, multiple revisions and unpredictable Service endpoints.
- **Evidence:** Deployments, Rollouts, ReplicaSets, ownerReferences, labels, events and Git history.
- **Likely cause:** incomplete migration or duplicate declarative ownership.
- **Immediate action:** map which object owns each pod; do not delete resources blindly.
- **Durable fix:** execute a migration plan with rollback and one workload controller; remove duplicate ownership only after verifying traffic and owner references.
- **Prevention test:** CI policy rejects duplicate workload definitions with overlapping selector/namespace.

### Case 5 — Abort scaled down candidate but route remained at 20%

- **Symptoms:** candidate endpoints disappear while router continues sending a share of traffic to candidate, causing failures.
- **Evidence:** live route weights, endpoints, router logs, plugin status, request failures, Rollout events.
- **Likely cause:** router integration failed during abort or route state is not controlled by the expected plugin.
- **Immediate action:** route traffic to stable using the documented provider-specific recovery method and verify actual split.
- **Durable fix:** test route cleanup on abort and controller restart; alert on nonzero candidate weight with zero candidate endpoints.
- **Prevention test:** automated post-abort traffic check.

### Case 6 — Metrics-provider outage froze all rollouts

- **Symptoms:** AnalysisRuns error or remain inconclusive; multiple releases stall.
- **Evidence:** provider health, query latency/errors, stale timestamps, controller events, number of affected rollouts.
- **Likely cause:** shared provider outage or overloaded queries.
- **Immediate action:** stop new promotions; keep exposure bounded; do not override gates broadly.
- **Durable fix:** provider SLOs, query timeouts, bounded retry policy, cached dashboards but not stale-as-fresh decisions, capacity planning, documented manual review route.
- **Prevention test:** inject provider timeout and verify no rollout auto-promotes.

## 20. Hands-on labs A–F

All labs use synthetic data and a disposable `kind` cluster. Commands are learner-run. Save YAML, command transcripts, sanitized status output, measured request counts, and cleanup evidence. Estimated footprints are approximate.

### Lab A — Replica-based Rollout canary

**Objective/level:** L1–L2; install controller, deploy stable/candidate revisions, manually promote and abort. **Time:** 60–90 minutes. **Footprint:** 2–3 CPU, 3–4 GiB RAM, 10 GiB disk.

**Files:** `lab-a/rollout-scoring-api.yaml` (Section 6.3), `lab-a/service.yaml` (Section 6.4), local app image or verified substitute.

**Steps:**
1. Confirm `kind-rollouts-lab` context and versions.
2. Install Argo Rollouts using a pinned release and verify CRD/controller readiness.
3. Build/import stable and candidate images into `kind`.
4. Apply manifest and Service; verify pods and ready endpoints.
5. Change template image/digest to candidate and apply.
6. Watch rollout/ReplicaSets. At a pause, record status, then run manual `promote` in one attempt.
7. Recreate a fresh attempt with a deliberately bad candidate; use `abort` in a separate attempt.
8. Measure response versions before and after each action; distinguish replica ratio from request weight.

**Expected pattern `[ILLUSTRATIVE]`:** Rollout reaches a pause, CLI displays a paused state, and the candidate ReplicaSet has some ready replicas. The exact output depends on version and local app. **Do not invent observed traffic counts.**

**Troubleshooting:** image pull errors mean image not imported or wrong tag; unready pods mean probe/port mismatch; no candidate responses may reflect low replica share or no traffic. Check pods, endpoints and actual version response before promotion.

**Cleanup:**
```bash
kubectl delete namespace scoring-lab
kubectl delete namespace argo-rollouts
kind delete cluster --name rollouts-lab
```
These commands delete the lab namespace/controller and the entire named disposable cluster. Verify the context/name first; never run against a shared cluster.

**Evidence/pass criteria:** plugin/controller versions; manifest; rollout/ReplicaSet status; separate promote and abort transcripts; measured pre/post version responses; cleanup proof. Pass only when the learner can explain why a replica ratio is not an exact traffic percentage.

### Lab B — Traffic-routed canary with verified weights and analysis success path

**Objective/level:** L2–L3; route actual traffic and validate analysis. **Time:** 2–4 hours. **Footprint:** 3–4 CPU, 4–5 GiB RAM if a compatible router fits.

**Prerequisites:** completed Lab A; local app returns version identity; supported router and Argo Rollouts integration verified against official compatibility docs. Gateway API alone is not sufficient proof of plugin support.

**Steps:**
1. Choose one router only. Install its CRDs/controller using a pinned release, or stop and use the replica fallback if support cannot be verified.
2. Create separate stable/canary Services with verified selectors/endpoints.
3. Configure the documented Rollouts traffic-routing integration for that router. Do not assume the generic `HTTPRoute` sample in Section 7 automatically integrates.
4. Inspect route conditions, plugin/controller events and endpoints.
5. Send at least 1,000 synthetic requests using `measure-split.py`; record actual counts, failures and intended weight.
6. Add a local metric provider and an `AnalysisTemplate` based on the installed CRD. Validate query labels and normal-success path before attaching it to a Rollout.
7. Trigger a step and verify the AnalysisRun result and actual traffic.

**If no supported router can be verified:** document controller/version, docs checked, missing integration, and exact blocker. Complete the measured replica-weighted portion, and mark the route-weighted portion **NOT EXECUTED**. Do not claim success.

**Evidence/pass criteria:** route manifest, compatibility reference, route status/events, ≥1,000-request measurement, actual split table, query test outputs, AnalysisRun result. Pass only if actual traffic reaches candidate and the success path is supported by valid measurements.

### Lab C — Failure path and automated abort

**Objective/level:** L3–L4; prove bad-candidate detection and recovery. **Time:** 90–150 minutes. **Footprint:** 3 CPU, 4 GiB RAM plus the selected provider.

**Steps:**
1. Start with known-good stable traffic and a tested manual abort path.
2. Build a candidate with `FAULT_MODE=error` (or `slow`) and a version identifier.
3. Configure analysis to evaluate candidate errors, with explicit traffic and sample preconditions; verify expression semantics against the installed version.
4. Expose candidate to a small step and wait long enough for telemetry propagation.
5. Capture deployment time, first candidate request, metric sample time, AnalysisRun decision, abort event, route/endpoint state, and stable recovery.
6. Run `measure-split.py` after abort and verify candidate exposure is zero or within the documented safe policy.
7. Revert the desired Git change or commit a fixed image. Confirm live abort alone did not rewrite Git.

**Expected pattern `[ILLUSTRATIVE]`:** error samples appear after metric delay; analysis fails; progression stops; stable traffic recovers after route/replica correction. Actual timing and counts must be measured.

**Failure modes:** no candidate traffic invalidates analysis; stale query can pass; expression errors may produce Error/Inconclusive; route can remain nonzero after abort. Do not bypass the gate to “finish” the lab.

**Pass criteria:** evidence timeline, raw query test, AnalysisRun, actual post-abort traffic measurement, Git fix/revert commit, and a test proving provider errors cannot pass.

### Lab D — Blue-green Rollout with Job pre-promotion analysis

**Objective/level:** L2–L3; validate preview and gate promotion on smoke-test result. **Time:** 90 minutes. **Footprint:** 2–3 CPU, 3–4 GiB RAM.

**Files:** `lab-d/bluegreen.yaml` from Section 8, `lab-d/smoke-job.yaml` from Section 11, and a local `scoring-smoke-test:local` image that asserts the preview endpoint's version and readiness.

**Steps:**
1. Verify `activeService`, `previewService`, `autoPromotionEnabled`, and `prePromotionAnalysis` against the installed CRD.
2. Apply Services and Rollout; confirm active version and preview endpoint behavior.
3. Update candidate template and wait for readiness.
4. Run the smoke Job against preview. Ensure the test exits nonzero for wrong version or failed health.
5. Attach a `Job`-provider analysis template using exact current schema; confirm the AnalysisRun blocks promotion on failed Job.
6. Run a successful candidate attempt, approve promotion, and verify actual active traffic.
7. Repeat with the failing smoke-test variant and verify promotion is blocked.

**Expected pattern `[ILLUSTRATIVE]`:** successful Job reports `Complete`; failing Job reports `Failed`; the failed analysis does not promote. Exact conditions and template fields must be validated locally.

**Pass criteria:** preview/active evidence, Job logs and exit status, analysis result, post-promotion request version, rollback-window decision, cleanup record.

### Lab E — “No data” safety lab

**Objective/level:** L3–L4; prove empty samples do not silently pass. **Time:** 60–120 minutes. **Footprint:** 2–3 CPU, 3–4 GiB RAM with a stub provider; more if Prometheus is used.

**Test matrix:**

| Case | Provider result | Required policy outcome |
|---|---|---|
| Normal healthy traffic | One valid sample below threshold | Success only if sample/traffic preconditions met |
| Regression | One valid sample above failure threshold | Failed/abort according to policy |
| Empty series | No sample | Inconclusive or failed; never success by accident |
| Provider timeout | Error/timeout | Hold/fail-closed according to policy |
| Insufficient traffic | Low request count | Inconclusive/hold; do not promote |
| Malformed value | Wrong type/shape | Error/inconclusive, alert and investigate |

**Steps:**
1. Test query/provider independently with canned healthy and failing values.
2. Configure a deliberately unsafe example only in a disposable namespace to understand the failure mode; do not connect it to any production rollout.
3. Remove the series and capture actual provider result and AnalysisRun state.
4. Add result-length guards or explicit inconclusive semantics verified for the installed version.
5. Repeat all cases and show the bad/empty case cannot promote.

**Important:** exact expression syntax and the difference between empty result, metric error and inconclusive are version-sensitive. If you cannot verify the installed semantics, keep the manifest as a reference only and do not run a potentially unsafe copy-paste expression.

**Pass criteria:** complete test matrix, schema/version record, proof that empty/error/low-traffic cases do not produce a successful promotion, and alert/runbook for provider outage.

### Lab F — Argo Rollouts versus Flagger comparison

**Objective/level:** L3–L4; make a defensible tool choice. **Time:** 60–90 minutes. **Footprint:** read-only walkthrough requires no additional cluster; optional Flagger install requires a separate resource phase and compatible router/metrics provider.

**Steps:**
1. Fill the comparison matrix in Section 14 for your selected environment.
2. Read current Flagger Canary, metrics, webhook and provider docs; record release/version and maintenance signals checked.
3. Review the reference `Canary` shape and identify fields requiring schema verification.
4. Map workload ownership: GitOps controller, Flagger/Rollouts, router, metrics provider and human release owner.
5. Choose one tool for a hypothetical service and document why the alternative is rejected or deferred.

**Representative output `[ILLUSTRATIVE]`:** a read-only review may show a Canary object waiting on analysis and events explaining metric evaluation; this is not evidence that a Flagger cluster was run.

**Pass criteria:** completed comparison, exact sources consulted, unresolved compatibility items, decision record, and explicit choice whether optional Flagger execution is feasible within budget.

## 21. Troubleshooting playbook

For every symptom, first check current traffic and blast radius; then collect evidence; then change one thing at a time.

| Symptom | Evidence and diagnostic order | Likely causes | Safe mitigation / prevention |
|---|---|---|---|
| Rollout stuck at pause | Rollout status, pause conditions, events, step index | Manual pause or waiting gate | Confirm metrics and owner; promote/abort only with approval; record action |
| AnalysisRun inconclusive/error | Run measurements, provider response, query logs, timestamps | Empty vector, timeout, malformed data, condition gaps | Hold progression; fix query/provider; test empty and error fixtures |
| No data but rollout appears green | Raw query, sample count, traffic counter, label names | Success condition not guarding empty results | Stop progression; require valid sample count and traffic precondition |
| Candidate gets 0% traffic | Route status, backend refs, Service endpoints, per-version counter | Router plugin/host/path mismatch or no endpoints | Treat as inconclusive; correct integration and prove ≥1,000-request split |
| Configured and observed weights differ | Intended weight, response counts, retries/connections, endpoint distribution | Sampling, connection reuse, bad router integration | Increase sample, measure at correct hop, verify route plugin support |
| Router accepted but no shift | Route conditions/events, controller logs, backend endpoints | Wrong parent/listener, plugin unsupported, bad references | Inspect implementation docs and route status; rollback to stable if unsafe |
| Header test route misses | Request header, exact match, route rule order, plugin support | Header name/value mismatch or unsupported feature | Verify exact `setHeaderRoute`/router syntax; use dedicated test request |
| CPU healthy but latency/business signal regresses | p95/p99, queue depth, downstream timings, domain/model output | CPU not a sufficient leading indicator | Pause/abort by the approved policy; add domain signals and baseline comparison |
| Too little traffic | Candidate request count, denominator, time window | Low usage or routing failure | Hold/inconclusive; extend window or use synthetic/replay traffic with caveats |
| Metric lag unsafe promotion | scrape timestamps, query window, ingestion delay, decision time | Analysis interval too short | Increase delay/window and require fresh samples; test delayed pipeline |
| HPA/capacity oscillation | HPA events, pending pods, desired/available replicas, throttling | Shared target, low floors, scaling lag | Stop progression, preserve stable capacity, revise independent policies and rehearse |
| GitOps overwrites rollout state | Git diff, resource status, events, managed fields | Same field has two writers | Define ownership; narrow any ignore; commit policy not runtime-generated state |
| Cohort not sticky | request identity, version counter per session, retry logs | random routing or unstable identity | Use supported cookie/header/hash cohort; test privacy and session consistency |
| Rollback leaves candidate traffic | route weight, endpoints, post-abort 1,000-request test | router cleanup failure or selector mismatch | Restore stable routing with documented method; alert on nonzero candidate traffic |
| Deployment and Rollout double-run | Deployments, Rollouts, ownerReferences, ReplicaSets | Incomplete conversion | Map ownership; execute controlled migration; add duplicate-owner policy |
| Job analysis hangs/misleads | Job conditions/logs, deadline, exit code, assertions | no deadline, retries mask failure, smoke too shallow | Set timeout/resource limits, assert version/output, use `backoffLimit: 0` for deterministic lab |
| Flagger resources conflict with GitOps | Canary, target Deployment, primary/canary objects, events | both controllers own generated resources | Follow provider-specific adoption model; one writer per field; avoid blind pruning |
| Controller/provider restarts mid-rollout | controller pods/events, analysis timestamps, route state | control-plane interruption | Freeze promotion, inspect actual traffic, restore service, resume only after consistency checks |

## 22. Reusable runbooks and checklists

### 22.1 Rollout design decision record

```text
Service / owner: [SERVICE] / [OWNER]
Risk tier and rationale: [TIER] / [RATIONALE]
Stable/candidate image digests: [DIGESTS]
Strategy: [rolling | replica-canary | route-canary | blue-green]
Router/provider/version: [DETAILS]
Minimum candidate requests and window: [VALUES + RATIONALE]
Leading indicators: [METRICS]
Lagging/domain/ML indicators: [METRICS]
Missing-data policy: [INCONCLUSIVE or FAIL-CLOSED]
Promotion gates: [CONDITIONS]
Abort trigger and authorized owner: [TRIGGER] / [OWNER]
Rollback / roll-forward and data compatibility: [PLAN]
Capacity and cost estimate: [CALCULATION]
Evidence location: [SANITIZED PATH]
Approvers and date: [APPROVALS]
```

### 22.2 Release-readiness checklist

- [ ] Candidate image is immutable/digest-pinned and provenance checked.
- [ ] Stable and candidate identities are observable in responses/metrics.
- [ ] Readiness, smoke, contract and data checks pass.
- [ ] Minimum traffic/sample and metric freshness conditions are explicit.
- [ ] Empty series, provider timeout and malformed values do not pass.
- [ ] Actual routing split measured; candidate receives real requests.
- [ ] Capacity/HPA/PDB and downstream quotas reviewed.
- [ ] Abort tested; post-abort stable traffic and health verified.
- [ ] Git desired state after abort/revert is understood.
- [ ] Incident owner, approver, rollback window and evidence path recorded.

### 22.3 AnalysisTemplate review checklist

- [ ] Provider schema verified against installed CRD/version.
- [ ] Query tested against known healthy, failing, empty and malformed results.
- [ ] Units, labels, aggregation window and threshold rationale documented.
- [ ] Candidate traffic/sample minimum enforced.
- [ ] `successCondition`, `failureCondition`, `failureLimit` and inconclusive behavior understood.
- [ ] Provider timeout/error policy cannot silently pass.
- [ ] Credentials least-privilege and absent from Git.
- [ ] Alerting, owner and expiry/review date defined.

### 22.4 Metric-provider outage runbook

1. Stop new promotions and identify affected Rollouts.
2. Check actual traffic, current candidate exposure, last valid sample and provider health.
3. Hold/abort according to risk tier; do not bypass gates globally.
4. Restore provider, validate queries manually, and verify fresh samples.
5. Re-run analysis only after approval and after confirming the candidate still has valid exposure.
6. Capture timeline, provider error, affected releases, and corrective action.

### 22.5 Stuck-rollout intervention record

```text
Incident/change ID: [ID]
Rollout / namespace / current revision: [IDENTIFIERS]
Current traffic split and evidence: [MEASURED]
Current controller/analysis state: [STATUS]
Last valid metric timestamp: [TIME]
Action proposed: [PROMOTE / ABORT / RETRY / UNDO / HOLD]
Risk and rollback plan: [PLAN]
Approver and executor: [ROLES]
Action timestamp and command: [RECORD]
Post-action traffic/health verification: [EVIDENCE]
Git desired-state follow-up: [PR/COMMIT]
```

### 22.6 Abort/rollback evidence timeline

Record rollout start, candidate first request, each metric sample timestamp, analysis result, route/replica state, abort command/action, stable recovery, Git revert/fix-forward, and final incident close. Sanitize secrets, tokens, customer identifiers, and sensitive request payloads.

### 22.7 GitOps ownership map

For each resource and mutable field, record: desired-state owner, runtime writer, allowed human actor, conflict behavior, alert, test, and evidence source. Do not permit two controllers to write the same field without an explicit, tested contract.

### 22.8 Controller upgrade checklist

- [ ] Version compatibility and release notes reviewed.
- [ ] CRD schema changes and existing manifests tested.
- [ ] Backups of CRDs/resources sanitized and secured.
- [ ] Router and metrics provider compatibility confirmed.
- [ ] In-flight rollout behavior rehearsed.
- [ ] Controller/CRD/plugin upgrade order documented.
- [ ] Rollback/recovery plan tested.
- [ ] Post-upgrade traffic, AnalysisRuns, events and controller health verified.

### 22.9 Incident and corrective-action record

```text
Impact and duration: [FACTS]
Detection signal: [METRIC/EVENT]
Timeline: [TIMESTAMPS]
Candidate exposure: [MEASURED]
Root cause: [EVIDENCE-BASED]
Contributing factors: [FACTS]
Immediate recovery: [ACTIONS]
Git desired-state correction: [PR/COMMIT]
Prevention tests: [TESTS]
Owners/due dates: [ACTIONS]
Follow-up SLI: [MEASURE]
```

## 23. Knowledge check and assessment

### 23.1 Conceptual questions with answers

1. **What does Argo Rollouts add beyond a Deployment?** Explicit progression, pauses, analysis integration and supported traffic-router coordination; it does not guarantee valid metrics or safe rollback.
2. **Why is replica weight not request weight?** Requests are affected by endpoint selection, connection reuse, load skew, readiness and retries.
3. **What is an AnalysisRun?** A concrete execution of one or more analysis metrics from templates with measurements/outcomes.
4. **What does inconclusive mean operationally?** Evidence does not justify pass or fail; progression should pause for policy-defined handling.
5. **Why is empty metric data dangerous?** A missing series can accidentally bypass a threshold check unless result shape and traffic preconditions are guarded.
6. **What does blue-green preview provide?** A way to test the candidate before routing active traffic; it does not prove every production path.
7. **Why inspect real traffic after abort?** Controller status can disagree with router state, endpoint membership or observed requests.
8. **Does PDB guarantee no dropped requests?** No; it governs voluntary disruption availability, not application-level completion or routing propagation.
9. **Why separate GitOps and rollout field ownership?** Reconciliation fights can reset weights/replicas or cause repeated churn.
10. **What is `ClusterAnalysisTemplate` for?** A cluster-scoped reusable analysis definition, subject to the installed CRD's schema.
11. **Is an Experiment a full A/B test?** No; product A/B testing also requires sound assignment, sample planning, metric interpretation and causal design.
12. **Why must HPA behavior be tested with canary?** Scaling lag and shared targets can reduce stable capacity or distort candidate exposure.
13. **What is the danger of leaving both Deployment and Rollout?** Duplicate workload controllers can create competing ReplicaSets or double-run the service.
14. **What should happen when the metric provider fails?** Hold/fail closed or become inconclusive per explicit policy; never treat provider failure as health.
15. **Why is a successful smoke Job insufficient for release safety?** Its assertions may not cover rare paths, production load, data corruption or downstream consumers.
16. **Why verify the Flagger maintenance status?** Project support, provider compatibility and release cadence can change.
17. **What does a rollback not reverse automatically?** Git desired state, external side effects, emitted messages, or incompatible data writes.
18. **Why measure at least 1,000 requests in the lab?** It provides a more informative empirical split than a few requests, though it does not guarantee statistical confidence for every traffic distribution.

### 23.2 Scenario questions with model answers

1. **Tier-0 API, high traffic, supported Gateway router:** choose route-weighted canary with strict candidate/stable comparison, minimum requests, delayed windows, manual checkpoints and tested abort; explain router compatibility and error-budget context.
2. **Low-risk internal admin tool, low traffic:** a rolling update may be enough; canary analysis on sparse traffic could be inconclusive and operationally expensive.
3. **Nightly ETL pipeline:** run candidate on a data slice or shadow/parallel dataset and compare row counts, schema, quality and outputs before promotion; avoid duplicate writes.
4. **Streaming consumer:** use a separate canary consumer group against a mirrored topic, compare lag and output, and protect ordering/idempotency; do not have both versions write duplicate side effects.
5. **ML inference service with drifted predictions:** replay a synthetic or approved dataset and compare output distribution, calibration/error proxies, fallback ratio and latency; HTTP 5xx alone is insufficient.
6. **Candidate receives zero traffic but metrics are green:** mark inconclusive, stop progression, inspect router/endpoints and add a minimum candidate request precondition.
7. **Metrics provider outage after 10% exposure:** hold or abort according to risk tier; do not promote based on stale data; verify current routing and restore provider.
8. **New version writes schema that old version cannot read:** rollback may be unsafe; use expand/contract migration, compatibility window, and a roll-forward/compensating plan before release.
9. **Blue-green preview passes smoke but 100% traffic fails:** inspect load, connection pools, downstream saturation, rare paths and capacity; preserve old environment and switch back only if data compatibility permits.
10. **Flagger and Argo CD both prune generated resources:** freeze changes, inventory ownership and live dependencies, disable unsafe pruning during migration, then establish a single ownership model and verify before cleanup.

### 23.3 Manifest/schema/query review questions

1. **A Rollout references a Service with a misspelled name.** Defect: traffic integration cannot target intended backend; validate references and inspect route/controller events before promotion.
2. **An analysis checks `result[0] < threshold` but never checks result length.** Defect: empty-result semantics may not produce the intended failure; add verified result-shape guard and test empty response.
3. **A manifest includes a guessed `HTTPRoute` weight annotation.** Defect: standard Ingress/Gateway behavior is not portable; use the selected implementation's official API and verify status.
4. **Both Deployment and Rollout use the same selector.** Defect: double ownership; plan a controlled migration and ensure only one workload controller owns the pods.
5. **An analysis interval is shorter than metric ingestion delay.** Defect: stale/empty samples can pass; align delay, query window and minimum sample policy.
6. **A Job has no deadline and retries indefinitely.** Defect: rollout can stall with unbounded resource use; add deadline, retry policy and clear assertions.
7. **A metric uses a label `canary` that the application never emits.** Defect: empty vector; inspect actual series and test query before attaching to a rollout.

### 23.4 Troubleshooting questions: evidence → diagnosis → action → prevention

1. **Candidate never appears in responses:** inspect endpoint membership, route status and version counter → likely no routing or no ready pods → hold progression → add route smoke and candidate-traffic precondition.
2. **Analysis fails despite healthy dashboard:** inspect query raw result, labels, units and timestamps → likely mismatched query or stale data → do not force promote → unit-test queries against canned values.
3. **Abort succeeded but errors continue:** inspect route weight and candidate endpoints → candidate route remains or client connections persist → restore stable route and verify traffic → add post-abort request test.
4. **Pods oscillate during rollout:** inspect HPA events, requests, pending pods and capacity → scaling/ownership conflict → freeze step changes and preserve stable capacity → test independent scaling policy.
5. **Argo CD repeatedly marks Rollout OutOfSync:** inspect field-level diff and runtime ownership → GitOps reapplying controller-owned fields → fix ownership map and narrow ignore if justified → add drift regression test.

### 23.5 Practical assessment

Design a release for `scoring-api` with a candidate image digest and a known stable baseline. Submit:

- selected strategy and why it fits service risk and local capabilities;
- router/provider compatibility evidence or an honest replica-only limitation;
- minimum candidate traffic, sample count, and analysis window with rationale;
- one technical and one domain/ML signal;
- explicit success/failure/inconclusive and provider-outage behavior;
- manual/automatic abort path and authorized owner;
- capacity estimate, GitOps ownership map, and rollback/data-compatibility plan;
- measured traffic split and a fault-injection timeline, or a clearly labelled not-executed plan.

**Scoring rubric (100 points):** strategy and risk rationale 15; routing and actual traffic evidence 15; query correctness/no-data safety 20; abort/recovery proof 20; capacity and ownership 10; data compatibility 10; sanitized evidence and audit record 10. A claimed automated abort without actual evidence receives no credit for the abort-proof portion.

## 24. Final readiness checklist and completion gate

- [ ] I can explain the difference between Deployment rolling updates, replica canary, route canary and blue-green.
- [ ] I can inspect Rollout, ReplicaSet, Service, route and AnalysisRun state without guessing.
- [ ] I measured actual traffic rather than inferring it from configured weights.
- [ ] Empty/no-data, low traffic, stale metrics and provider errors do not silently pass.
- [ ] I tested manual abort and verified stable traffic recovered.
- [ ] I completed a Job-based preview/smoke pattern and understand its coverage limits.
- [ ] I documented GitOps ownership and avoided a Deployment/Rollout double-run.
- [ ] I recorded capacity, HPA/PDB and downstream compatibility risks.
- [ ] I compared Flagger fairly and verified its current support signals before a tool decision.
- [ ] I saved sanitized manifests, versions, status, metrics, timestamps, incident record and cleanup evidence.

| Lab | Evidence required | Learner status |
|---|---|---|
| A — Replica canary | Version record, rollout/ReplicaSet status, promote and abort transcripts, traffic check | [ ] Not started [ ] Complete |
| B — Traffic routing | Router/version compatibility, route status, ≥1,000 request counts, analysis success path | [ ] Not started [ ] Complete [ ] Blocked/not executed |
| C — Automated abort | Fault injection, metric timestamps, AnalysisRun, route state, stable recovery, Git fix | [ ] Not started [ ] Complete [ ] Manual-only |
| D — Blue-green + Job | Preview test, Job outcome, analysis gate, active traffic and rollback window | [ ] Not started [ ] Complete |
| E — No-data safety | Empty/healthy/failing/error/low-traffic matrix, proof no unsafe promotion | [ ] Not started [ ] Complete |
| F — Tool comparison | Completed matrix, Flagger source checks, decision record | [ ] Not started [ ] Complete |

Completion requires demonstrated evidence, not merely reading the lesson. If router compatibility cannot be verified, mark that lab blocked/not executed and retain the fallback evidence without overstating the result.

## 25. Source and `[VERIFY]` register

Official documentation consulted for source orientation includes the Argo Rollouts repository/release notes and official Canary, Analysis and installation documentation; Flagger's official metrics and webhook docs. These references establish the documented capabilities but do not validate the learner's exact local versions. The following remain explicit verification tasks:

| Claim / feature | Source of truth | Version/environment sensitivity | Verification command/check | Status |
|---|---|---|---|---|
| Rollout API version and strategy schema | Argo Rollouts official CRD/install docs | Controller and CRD release | `kubectl explain rollout.spec.strategy --recursive`; inspect CRD | Needs verification |
| Canary step list and semantics | Argo Rollouts Canary docs | Release-sensitive step types | `kubectl explain rollout.spec.strategy.canary.steps --recursive` | Needs verification |
| CLI promote/abort/retry/undo syntax | Argo Rollouts CLI docs and plugin help | Plugin/controller skew | `kubectl argo rollouts version`; `kubectl argo rollouts help` | Needs verification |
| Dashboard binding defaults | Release notes / dashboard docs | Recent security changes | Check exact release notes; keep local-only access | Needs verification |
| Traffic-router plugins | Argo Rollouts traffic-management docs and router compatibility matrix | Provider, controller and API versions | Inspect official integration page and controller release docs | Needs verification |
| Gateway API weighted `HTTPRoute` | Gateway API docs and selected controller docs | CRDs and controller implementation | `kubectl get crd httproutes.gateway.networking.k8s.io`; inspect route conditions | Needs verification |
| Header route / `setHeaderRoute` | Selected Argo Rollouts plugin docs | Plugin-specific | Search selected release docs and test with synthetic request | Needs verification |
| Blue-green `activeService`, `previewService`, pre/post analysis, delay | Argo Rollouts BlueGreen docs | CRD version | `kubectl explain rollout.spec.strategy.blueGreen --recursive` | Needs verification |
| Analysis provider fields and expression behavior | Argo Rollouts Analysis docs | Provider and expression engine version | `kubectl explain analysistemplate.spec.metrics --recursive`; test empty/invalid results | Needs verification |
| `len(result)` and no-data behavior | Analysis docs plus installed controller test | Expression semantics | Use a disposable AnalysisRun with normal, empty, malformed and error results | Needs verification |
| Prometheus metric labels/query | Application instrumentation and Prometheus docs | App version, labels, scrape config | Query raw series and inspect labels/timestamps | Illustrative |
| `abortScaleDownDelaySeconds`, `dynamicStableScale`, HPA target | Argo Rollouts docs | Version and strategy-specific | `kubectl explain rollout.spec --recursive`; test on disposable cluster | Needs verification |
| Argo CD health for Rollout CRD | Argo CD custom health docs and installed config | Argo CD version/customization | Inspect UI/status and resource health customization | Needs verification |
| Deployment-to-Rollout / `workloadRef` migration | Argo Rollouts docs | Version and migration mode | Inspect schema/docs; rehearse with disposable workload | Needs verification |
| Flagger API version and `Canary` fields | Flagger official docs and CRDs | Release/provider | `kubectl get crd canaries.flagger.app -o yaml`; `kubectl explain canary.spec --recursive` | Needs verification |
| Flagger provider list and maintenance status | Official Flagger repository/releases/docs | Current project state | Review current releases, repo notices, provider matrix and recent issues | Needs verification |
| Job provider behavior | Argo Rollouts Analysis docs | Controller/Job provider schema | Validate CRD, run known-pass and known-fail Jobs | Needs verification |
| Actual traffic measurement method | `measure-split.py` and application response contract | Client retries, connection reuse, route hop | Run ≥1,000 requests and preserve counts/errors | Illustrative until run |
| Controller restart/abort route recovery | Controller and router integration docs | Provider-specific | Fault-inject only in disposable cluster and inspect real route | Needs verification |

### Audit sign-off

- **Scope audit:** Unit 8 L1–L4 topics and six separate labs are represented in this lesson.
- **Technical audit:** examples identify assumptions and version-sensitive fields; manifests and commands must still be validated against the chosen installed CRD/router versions before use.
- **Evidence audit:** representative examples are labelled; no live cluster run, traffic measurement, or automated abort is claimed.
- **Repository safety:** the requested target lesson was created in the working directory. The available `Roadmap(9).md` snapshot and M08 curriculum prompt were inspected; a separately named `Roadmap_ptree.md` was not available. No other file was intentionally modified during this generation step.
- **Human verification required:** perform labs and close the `[VERIFY]` register before treating any pattern as operationally validated.

**UNIT-08-STATUS: DRAFT-AUDITED**

An AI self-audit does not replace running the labs against the selected Argo Rollouts, Flagger, Kubernetes, router, and metrics-provider versions. All output examples in this lesson are expected or illustrative unless explicitly captured by the learner.
