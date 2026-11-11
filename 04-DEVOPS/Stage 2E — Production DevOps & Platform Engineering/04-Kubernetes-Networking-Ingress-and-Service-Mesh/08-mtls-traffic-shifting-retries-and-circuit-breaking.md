# mTLS, traffic shifting, retries and circuit breaking

## Unit 8 — mTLS, traffic shifting, retries and circuit breaking
**Target file:** `08-mtls-traffic-shifting-retries-and-circuit-breaking.md` | **Estimated time:** 8–12 hours including four local labs | **Prerequisites:** M04 Units 1–7; Kubernetes Services, NetworkPolicy, TLS, workload identity concepts, and a disposable `kind` cluster  
**Core tools:** Kubernetes, `kind`, `kubectl`, Linkerd CLI, Gateway API `HTTPRoute`, local `curl`/Python test client | **Awareness:** Istio-specific `PeerAuthentication`, `DestinationRule`, Envoy circuit breaking, SPIFFE, Gateway API | **Last reviewed:** 2026-10-28 (authoring date; not a full compatibility audit) | **Kubernetes/tool baseline assumed:** a recent `kind`-supported Kubernetes release; exact Linkerd, Kubernetes, Gateway API CRD and CLI versions must be verified together before running manifests.

> **Status: DRAFT-AUDITED.** This unit uses **Linkerd sidecar mode**, matching the choice recorded in Unit 7. Official Linkerd feature/reference pages for automatic mTLS, authorization policy, retries, `HTTPRoute`, traffic shifting and circuit breaking were consulted. The current release/CRD compatibility matrix was not fully audited, and no command, manifest, or lab was executed in a cluster. This is an educational lab plan, not a production change procedure.

**Cross-unit mesh contract:** Unit 7 selected **Linkerd sidecar mode** as an explicit `[ASSUMPTION]`; use that same choice for this unit and the M04 capstone unless a source-backed review changes all three. Do not copy Istio YAML into the Linkerd lab. Linkerd automatically provides mTLS between meshed workloads, but by default can accept plaintext from non-meshed sources; the lab therefore uses Linkerd authorization policy/default inbound policy to test the intended authenticated-only access. **[VERIFY]** Confirm the current installed release, Gateway API resource versions, authorization CRDs, and policy semantics before applying examples.

**Shared M04 example — [ASSUMPTION, inherited from Unit 7]:** namespace `ml-platform`; `model-api` listens on TCP/8080; `feature-service` on TCP/8081; Postgres on TCP/5432; Redis on TCP/6379. The model API has stable and candidate versions selected behind one logical Service/route. ETL calls external APIs; metrics scraping and batch Jobs are separate callers that must be inventoried. Confirm the final repository contract before combining manifests.

### 8.0 Why this matters in production

A strict identity policy can break a metrics scraper or a scheduled job that was not enrolled in the mesh, even while the main application remains healthy. Retries that were intended to hide a transient failure can multiply load across several call layers and overwhelm the feature service during recovery. A configured 90/10 canary split can also differ from a finite observed sample, especially when connections are reused, requests are retried, or streams stay open for a long time. This unit teaches how to prove identity and access behavior, measure routing instead of assuming it, and constrain retries and failure experiments so a reliability feature does not become an outage amplifier.

### 8.1 Learning objectives

1. **[L1]** Distinguish TLS from mTLS and explain encryption, peer authentication, workload identity, and authorization as separate properties.
2. **[L1]** Trace a request through Linkerd proxies and identify the NetworkPolicy and application authorization boundaries.
3. **[L2]** Stage an authenticated-only policy rollout, test an authorized meshed client and an unmeshed client, and collect identity-related evidence.
4. **[L2]** Configure and measure 90/10 and 50/50 routing using a version-verified Linkerd-supported `HTTPRoute` configuration.
5. **[L3]** Calculate retry amplification, design a timeout ladder, and explain when retries are unsafe because an operation is not idempotent.
6. **[L3]** Distinguish Linkerd endpoint-level failure accrual from a generic application circuit breaker or Istio/Envoy connection-pool controls.
7. **[L3]** Run a bounded local fault experiment with a stated hypothesis, stop condition, evidence plan, and recovery procedure.
8. **[L4]** Build CI checks that validate both intended success and intended denial/failure, not only YAML syntax.
9. **[L4]** Diagnose strict-policy, canary, retry-storm, stream-timeout, and endpoint-ejection incidents using competing hypotheses.
10. **[L4]** Produce an auditable policy decision with measured results, rollback gates, ownership, and unresolved verification items.

### 8.2 Concept map and vocabulary

### Request path before configuration

```text
model-client application
        |
        v
source Linkerd proxy  ---- identity certificate / mTLS handshake ----+
        |                                                            |
        v                                                            |
Kubernetes network + CNI-enforced NetworkPolicy                      |
        |                                                            |
        v                                                            |
destination Linkerd proxy <-------------------------------------------+
        |
        +--> Linkerd inbound policy / route policy (where supported)
        |
        v
feature-service application
        |
        +--> application-level authorization / business validation
```

The drawing is a logical path, not a packet capture. Linkerd's proxy establishes authenticated, encrypted transport between meshed peers. NetworkPolicy independently governs network reachability. Mesh authorization determines which supported identities/traffic may reach a protected port or route. The application still decides whether the request is valid and allowed to perform a business action.

### TLS versus mTLS

```text
TLS:
Client ---------------- encrypted channel ----------------> Server
Client validates server certificate; server-side client identity
is not necessarily authenticated by TLS.

mTLS:
Client <--------------- encrypted channel ----------------> Server
Client validates server identity AND server validates client identity.
Both validations depend on trust configuration, certificate validity,
name/identity matching, and the actual endpoint being reached.
```

Encryption does not prove the intended workload identity by itself. A packet capture containing unreadable bytes is consistent with encryption but does not establish that the right peer certificate was presented, that the expected identity was authenticated, or that authorization allowed only the intended caller. Use the mesh's documented identity diagnostics and positive/negative access tests alongside any capture.

### Glossary

| Term | Precise definition | Common misconception |
|---|---|---|
| TLS | Protocol that protects a connection with confidentiality and integrity and normally authenticates the server to the client | TLS automatically authenticates both peers |
| mTLS | TLS with client and server authentication | mTLS itself defines application permissions |
| Workload identity | An identity associated with a running workload, commonly tied to a Kubernetes ServiceAccount in a mesh | A Pod IP is a stable identity |
| Trust domain | Namespace/domain within which identity names are interpreted and trusted | All clusters or meshes automatically share one trust domain |
| Mesh CA/issuer | Component or key hierarchy that issues workload certificates and trust material | It is the same thing as the ingress certificate managed by cert-manager |
| Permissive/transition policy | A rollout state intended to allow old and new communication paths while inventory is completed; exact behavior is implementation-specific | Every mesh has a portable “permissive mTLS” switch |
| Strict/authenticated-only policy | A policy that requires an authenticated/meshed caller for the protected resource according to the selected implementation | Strict transport security automatically denies every unmeshed path unless policy semantics say so |
| Authorization | Decision about whether an authenticated principal may perform an action | Authentication is authorization |
| Retry | Another attempt after a qualifying failure or timeout | Every failed request is safe to repeat |
| Retry budget | A bound on extra attempts or retry load over a defined scope | A retry count alone always limits total system amplification |
| Idempotency | Repeating an operation has the same intended effect as performing it once | HTTP POST is automatically safe to retry |
| Deadline | Maximum total time the caller is willing to wait for an operation | A per-attempt timeout is the overall deadline |
| Timeout ladder | Coordinated time limits across client, ingress, mesh, application, and dependency | Every downstream timeout should exceed every upstream timeout |
| Retry amplification | Multiplication of attempts as retries occur at multiple layers | Configured retries equal observed retries |
| Circuit breaker | Mechanism that stops or limits calls to a failing dependency to permit recovery | A breaker repairs the dependency |
| Failure accrual / endpoint ejection | Proxy tracks endpoint failures and temporarily avoids an endpoint under supported behavior | Every mesh has identical ejection thresholds and recovery semantics |
| Traffic shifting | Routing a target share of requests to different backends | A 90/10 setting guarantees exactly 90/10 for every sample |
| Mirroring/shadowing | Sending a copy of traffic to another backend for observation | Mirrored writes are harmless |
| NetworkPolicy | Kubernetes API for network reachability policy, enforced by a compatible CNI | Mesh identity policy replaces CNI enforcement |
| Fault injection | Deliberately adding a controlled failure/delay to test resilience | It is safe to inject faults into production without guardrails |

### Policy boundary table

| Control | Main question it answers | What it does not replace |
|---|---|---|
| Mesh mTLS/workload identity | Who is the peer on this meshed connection, and is transport protected? | Authorization to perform business actions |
| Mesh authorization policy | Which supported identities/traffic may reach a protected service/route? | CNI network reachability, app-level business checks |
| Kubernetes NetworkPolicy | Which selected Pods can reach which network peers/ports? | HTTP method/path authorization or workload certificate validation |
| Application authorization | May this principal perform this business operation on this data? | Network segmentation and transport encryption |
| Ingress/load balancer TLS | How is traffic protected/authenticated at the edge termination point? | Automatic end-to-end encryption across every internal hop |
| Application TLS inside mesh | Is the application protocol itself encrypted/authenticated in addition to the mesh hop? | Mesh L7 visibility when application TLS is opaque to the proxy |

### 8.3 Level 1 — Beginner: Foundations

### What mTLS proves—and what it does not

With TLS, a client commonly validates the server's certificate and establishes encryption and integrity for the connection. With mTLS, the server also authenticates a client certificate. In a service mesh, the proxy manages the workload certificate and connection on behalf of the application. Linkerd's official automatic-mTLS documentation describes authenticated, encrypted communication between meshed applications and explains that non-meshed sources can be accepted by default unless policy restricts them. See [Linkerd Automatic mTLS](https://linkerd.io/docs/features/automatic-mtls/).

The identity is not merely the source IP address. Pod IPs change; NAT and proxies can obscure network addresses; an identity system ties a credential to a workload principal. SPIFFE is a set of specifications for workload identity concepts and formats, but this lesson does not assume a separate SPIFFE/SPIRE deployment. Linkerd's own identity issuance and trust configuration must be understood from its official documentation.

A mesh-managed workload certificate is distinct from the public/edge certificate handled by an Ingress or Gateway and cert-manager in Unit 6. Do not upload the mesh CA private key to application namespaces or treat a mesh certificate as a public browser certificate. Certificate rotation and trust-anchor lifecycle are security-critical platform responsibilities.

### Permissive versus strict: avoid a false portable abstraction

Istio documents peer-authentication modes such as permissive and strict in its own API. Linkerd's model is different: it automatically uses mTLS between meshed workloads, while inbound policy controls which authenticated or unauthenticated traffic is accepted. Do **not** copy Istio's `PeerAuthentication` YAML into a Linkerd cluster. The rollout goal is portable—inventory callers, prove enrollment, test expected access, then require authenticated callers—but the configuration is implementation-specific.

A safe rollout begins with observation and inventory. Include Deployments, StatefulSets, Jobs/CronJobs, probes, metrics scrapers, ingress controllers, administrative/debug clients, and any external or unmeshed caller. If strict authenticated-only policy is enabled before those paths are understood, a service may look healthy while observability or scheduled processing silently fails.

### Simple example

`model-client → source proxy → network/NetworkPolicy → destination proxy → feature-service`

- The source and destination proxies establish the mesh mTLS connection when both workloads are enrolled and identity/trust are valid.
- The destination proxy can apply supported inbound/route authorization.
- NetworkPolicy can still block the connection before it reaches the destination.
- The application validates input, caller-level business permissions, and side effects.
- A packet capture can show endpoints, TCP behavior, and encrypted records, but normally cannot alone prove the peer identity or policy decision. Mesh diagnostics and negative tests are required.

### Retries, deadlines, and breakers in plain language

Suppose `model-api` calls `feature-service`, which calls Redis. A timeout at Redis may cause the feature service to retry; the model API may also retry the feature-service call; and a client may retry the model API. If each layer independently retries, one original request can become many downstream attempts. That extra load can delay healthy work, increase queues, and create more timeouts, which trigger still more retries.

A retry is reasonable only when the failure is retryable, the remaining deadline permits another attempt, the extra load is acceptable, and repeating the operation is safe. A circuit breaker/failure-accrual mechanism limits calls to a failing endpoint; it does not replace deadlines or repair the endpoint. A timeout stops waiting at a boundary, but cancellation may not stop work already running in an application or database.

### Guided read-only walk-through

```bash
# File: commands/inspect-mtls-baseline.sh
set -euo pipefail
EXPECTED_CONTEXT="kind-m04-mesh-lab"
ACTUAL_CONTEXT="$(kubectl config current-context)"
if [[ "${ACTUAL_CONTEXT}" != "${EXPECTED_CONTEXT}" ]]; then
  printf 'Refusing: expected context %s, got %s\n' \
    "${EXPECTED_CONTEXT}" "${ACTUAL_CONTEXT}" >&2
  exit 20
fi
kubectl --context "${EXPECTED_CONTEXT}" get namespace ml-platform --show-labels
kubectl --context "${EXPECTED_CONTEXT}" -n ml-platform get deploy,pod,svc,endpointslice
kubectl --context "${EXPECTED_CONTEXT}" -n ml-platform get networkpolicy
kubectl --context "${EXPECTED_CONTEXT}" get crd | grep -E 'linkerd|gateway.networking.k8s.io' || true
```

Expected output is **[ILLUSTRATIVE]**: existing namespace labels, workloads, Services, EndpointSlices, NetworkPolicies, and installed CRDs. A missing namespace or CRD is not proof that the cluster is broken; the sample may not be deployed and the selected Linkerd release may use different resources. This command is read-only, except it still depends on the current kubeconfig and context. It does not prove mTLS or authorization.

### 8.4 Level 2 — Intermediate: Working Practice

### Verify the selected Linkerd version before applying policy

The current official Linkerd documentation describes automatic mTLS, authorization policies, Gateway API `HTTPRoute`/`GRPCRoute`, retries/timeouts, traffic shifting, and endpoint-level circuit breaking. These are not all the same feature class: traffic policy uses specific supported APIs, while Linkerd's failure accrual is not a direct copy of Istio's Envoy `DestinationRule` connection-pool/outlier-detection model.

Before applying any manifest:

1. Confirm `kubectl config current-context` is the explicitly named disposable cluster.
2. Run `linkerd version` and the current documented `linkerd check` command.
3. Inspect installed CRDs and compare them with the current Linkerd reference pages.
4. Check the official release notes and Kubernetes compatibility matrix for the chosen release.
5. Confirm that the installed Gateway API version supports the fields being used. Linkerd's current documentation says `HTTPRoute` can configure backend weights, request/backend timeouts, and retry behavior; exact schema support is release-sensitive.
6. Inspect the manifest and run a server-side dry-run where the cluster supports it; a dry-run validates schema/admission but does not prove runtime behavior.

**[VERIFY]** Do not apply this lesson's example API versions blindly. The `HTTPRoute` examples below use `gateway.networking.k8s.io/v1` as a version-gated template; check the installed CRD's served versions and the chosen Linkerd release before use. Linkerd policy resources in examples use `policy.linkerd.io/v1alpha1`; verify every CRD and schema first.

### Automatic mTLS and authenticated-only inbound access

Linkerd's automatic mTLS is not a cluster-wide “deny all plaintext” switch. By default, Linkerd accepts traffic from non-meshed sources unless an inbound policy restricts it. The supported policy model includes concepts such as `Server`, `HTTPRoute`, `MeshTLSAuthentication`, `NetworkAuthentication`, `ServerAuthorization`, and `AuthorizationPolicy`; exact resource relationships and API versions must be verified. See [Linkerd Authorization Policy](https://linkerd.io/docs/features/server-policy/) and its [reference](https://linkerd.io/docs/reference/authorization-policy/).

For a protected `feature-service`, a safe design process is:

1. Identify the exact port/route that must be protected.
2. Identify the client Kubernetes ServiceAccount/mesh identity.
3. Confirm both Pods are actually meshed and the identity is visible using documented diagnostics.
4. Define a policy that allows only the intended authenticated identity/route using current Linkerd policy docs.
5. Test an authorized meshed caller (must succeed).
6. Test a different meshed identity (must be denied if excluded).
7. Test a controlled unmeshed client (must be denied by the intended policy).
8. Verify probes, metrics, Jobs, CronJobs, and admin clients still have a deliberate path.
9. Capture events/logs and remove the temporary test client.

The precise policy YAML is deliberately not fabricated here. The official Linkerd reference has evolved and policy CRDs have versioned schemas. Build the exact resource using the selected release's examples, then include it in the learner's evidence. **[VERIFY: Linkerd Authorization Policy reference, installed `policy.linkerd.io` CRDs, and `kubectl explain` for each field.]**

### Identity verification and packet capture

Use multiple forms of evidence:

- `linkerd check` for installation/control-plane checks.
- The current Linkerd command documented for proxy/workload diagnostics, after confirming the syntax in the installed CLI help.
- A positive authorized request and negative unauthorized/plaintext request.
- Application and proxy logs/events.
- A packet capture only if needed, with a documented capture point and a bounded local test.

Packet capture caveats:
- Capturing inside a Pod, a kind node container, WSL2, and Windows may expose different interfaces, addresses, NAT translations, or namespaces.
- Encrypted records do not reveal HTTP path/body without appropriate keys and protocol visibility; do not attempt to extract private keys.
- Seeing TLS-like ciphertext alone does not prove that the expected workload identity was verified.
- A capture may miss traffic due to offloads, wrong interface, namespace boundaries, or timing.
- Do not capture real payloads or store sensitive packet dumps in the repository.

### Weighted routing for stable/candidate model versions

The routing path is:

```text
model-client -> Linkerd outbound proxy -> HTTPRoute backend weights
                                  |-> model-api-stable Service
                                  |-> model-api-candidate Service
```

Linkerd documents Gateway API `HTTPRoute` backend weights for traffic shifting. Its earlier SMI `TrafficSplit` functionality is deprecated in current documentation in favor of dynamic request routing; do not start a new lab on the old API unless a legacy environment explicitly requires it. See [Linkerd Traffic Shifting](https://linkerd.io/2-edge/tasks/traffic-shifting/) and [HTTPRoute reference](https://linkerd.io/docs/reference/httproute/).

**[VERIFY]** Confirm the exact Gateway API version, required CRDs, route attachment model, parent Service, and Linkerd release support before applying the following shape. This is a schema illustration, not a ready-to-apply manifest:

```yaml
# File: manifests/unit-08/model-api-weighted-route.template.yaml
# [VERIFY] Confirm apiVersion and supported HTTPRoute fields against installed CRDs.
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: model-api
  namespace: ml-platform
spec:
  parentRefs:
    - name: model-api
      # [VERIFY] Include a section/port only if the selected route attachment requires it.
  rules:
    - backendRefs:
        - name: model-api-stable
          port: 8080
          weight: 90
        - name: model-api-candidate
          port: 8080
          weight: 10
```

The example is intentionally a template. Depending on the selected implementation, an HTTPRoute parent relationship, `Service` parent, route status, namespace attachment, and backend namespace may need to be configured differently. Check route status/conditions and confirm that both backend Services have ready endpoints. Do not expose a public listener to test a local canary.

For header-based internal tester routing, first verify whether the chosen Linkerd/Gateway API implementation supports the desired match/header semantics and route precedence. Do not assume that a route rule from Istio's `VirtualService` is portable to Linkerd.

### Repeatable local request-counting script

This script is designed to call only a local endpoint. It requires a version field in each response, e.g. JSON `{"model_version":"stable"}` or `{"model_version":"candidate"}`. It deliberately requires the learner to set a local port-forward endpoint and explicitly confirm the disposable context. The script does not set up a route and has not been executed.

```bash
# File: commands/count-model-versions.sh
set -euo pipefail

EXPECTED_CONTEXT="kind-m04-mesh-lab"
ACTUAL_CONTEXT="$(kubectl config current-context)"
if [[ "${ACTUAL_CONTEXT}" != "${EXPECTED_CONTEXT}" ]]; then
  echo "Refusing: current context is not ${EXPECTED_CONTEXT}" >&2
  exit 20
fi

: "${LOCAL_ENDPOINT:?Set LOCAL_ENDPOINT to a local-only port-forward URL}"
: "${CONFIRM_DISPOSABLE_CLUSTER:?Set CONFIRM_DISPOSABLE_CLUSTER=yes after checking context}"
if [[ "${CONFIRM_DISPOSABLE_CLUSTER}" != "yes" ]]; then
  echo "Refusing: disposable-cluster confirmation missing" >&2
  exit 21
fi
if [[ "${LOCAL_ENDPOINT}" != http://127.0.0.1:* && "${LOCAL_ENDPOINT}" != http://localhost:* ]]; then
  echo "Only http://127.0.0.1:PORT or http://localhost:PORT endpoints are allowed" >&2
  exit 22
fi

REQUESTS="${REQUESTS:-1000}"
DELAY_SECONDS="${DELAY_SECONDS:-0.02}"
if ! [[ "${REQUESTS}" =~ ^[0-9]+$ ]] || (( REQUESTS < 1000 || REQUESTS > 10000 )); then
  echo "REQUESTS must be between 1000 and 10000" >&2
  exit 23
fi
if ! command -v curl >/dev/null 2>&1 || ! command -v python3 >/dev/null 2>&1; then
  echo "curl and python3 are required" >&2
  exit 24
fi

TMP_DIR="$(mktemp -d)"
cleanup() { rm -rf -- "${TMP_DIR}"; }
trap cleanup EXIT INT TERM
: > "${TMP_DIR}/responses.jsonl"
: > "${TMP_DIR}/errors.txt"

i=1
while (( i <= REQUESTS )); do
  if body="$(curl --fail --silent --show-error --max-time 3 \
      "${LOCAL_ENDPOINT%/}/predict" 2>>"${TMP_DIR}/errors.txt")"; then
    printf '%s\n' "${body}" >> "${TMP_DIR}/responses.jsonl"
  else
    printf 'request=%s failed\n' "${i}" >> "${TMP_DIR}/errors.txt"
  fi
  sleep "${DELAY_SECONDS}"
  ((i += 1))
done

python3 - "${TMP_DIR}/responses.jsonl" "${TMP_DIR}/errors.txt" <<'PY'
import collections, json, pathlib, sys
rows = pathlib.Path(sys.argv[1]).read_text().splitlines()
errors = pathlib.Path(sys.argv[2]).read_text().splitlines()
counts = collections.Counter()
malformed = 0
for row in rows:
    try:
        obj = json.loads(row)
        version = obj.get("model_version")
        if version in ("stable", "candidate"):
            counts[version] += 1
        else:
            counts["unknown_version"] += 1
    except Exception:
        malformed += 1
print("Observed response counts [ILLUSTRATIVE FORMAT; values below are actual only when script is run]:")
print(f"stable={counts['stable']} candidate={counts['candidate']} unknown_version={counts['unknown_version']}")
print(f"malformed={malformed} failed_requests={len(errors)}")
total = sum(counts.values())
if total:
    print(f"counted_response_total={total}")
    print(f"stable_pct={100 * counts['stable'] / total:.3f}")
    print(f"candidate_pct={100 * counts['candidate'] / total:.3f}")
if errors or malformed or counts["unknown_version"]:
    sys.exit(2)
PY
```

The script bounds request count and rate and only accepts localhost endpoints. It does not automatically know the actual configured weights and therefore cannot calculate target deviation until the learner records the target. If the local API returns a different response schema, adapt and review the parser before running. It reports actual values only when executed; no output is supplied here.

### 8.5 Level 3 — Advanced: Production Engineering

### Canary calculations and interpretation

Configured weights are routing targets, not a promise that each finite sample will exactly match them. For each run:

- `observed percentage = version responses / total counted responses × 100`
- `absolute deviation (percentage points) = |observed percentage − configured target percentage|`

Define the denominator before running the test. This lesson's recommended report keeps successful responses, HTTP errors, transport failures, malformed responses, and unknown-version responses separate. Do not quietly remove errors from the report to make the split look correct. If retries cause one logical client request to reach multiple backends, response counts alone may not equal backend attempt counts; collect proxy/backend evidence if available.

| Target | Total requests | Stable count | Stable % | Candidate count | Candidate % | Stable deviation (pp) | Candidate deviation (pp) | Errors/retries | Duration | Run |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| 90/10 |  |  |  |  |  |  |  |  |  | 1 |
| 90/10 |  |  |  |  |  |  |  |  |  | 2 |
| 50/50 |  |  |  |  |  |  |  |  |  | 1 |
| 50/50 |  |  |  |  |  |  |  |  |  | 2 |

For a 90/10 target and 1,000 independently sampled requests, a result near 900/100 is plausible but not guaranteed. Statistical variation, route attachment mistakes, uneven connection reuse, endpoint readiness, client behavior, retries, and persistent streams can all affect observations. A weighted route generally acts on requests/streams according to implementation semantics; do not assume every TCP connection is an independent request. Test multiple runs, confirm route status and endpoints, and report the sample method.

### Retry ownership and idempotency

Before enabling retries, write down the retry owner: client library, mesh proxy, application, or dependency client. Avoid uncoordinated retry layers. A retry policy should define:
- **Retryable conditions:** specific status codes or transport outcomes that indicate a transient failure, not every error.
- **Attempt cap:** total attempts versus additional retries; make the distinction explicit.
- **Per-attempt timeout:** how long one backend attempt may run.
- **Overall deadline:** how long the caller is willing to wait, including all attempts and backoff.
- **Backoff/jitter:** a delay strategy that reduces synchronized retry bursts; confirm whether the chosen layer supports it rather than inventing fields.
- **Retry budget:** bound extra load by a documented policy or client-level budget.
- **Idempotency:** a request identifier/deduplication contract or naturally idempotent operation before retrying a side effect.
- **Observability:** original requests, retry attempts, errors, and downstream load are distinct counts.

Linkerd's current retry reference documents annotations such as `retry.linkerd.io/http`, `retry.linkerd.io/grpc`, `retry.linkerd.io/limit`, and `retry.linkerd.io/timeout`, and warns about interactions with `ServiceProfile`. Exact annotation support is release-sensitive; consult [Linkerd Retries](https://linkerd.io/docs/reference/retries/) and [Retries and Timeouts](https://linkerd.io/2-edge/features/retries-and-timeouts/) before using them. The reference currently describes a retry limit as the number of retries, with a documented default; this lesson avoids relying on that default and requires an explicit verified limit.

### Retry amplification: worked arithmetic

Assume three sequential layers each permit **up to three total attempts** for the same logical operation, and every attempt at a layer can invoke the next layer. In the pathological case where all retry layers are exercised, the deepest dependency can see up to:

\[
A_{\max}=3\times3\times3=27
\]

attempts per original request. For `d` retrying layers with `a_i` total attempts per layer:

\[
A_{\max}=\prod_{i=1}^{d} a_i
\]

This is a bounded worst-case illustration for the stated call graph, not a prediction. Some layers may not retry certain errors, deadlines may expire, or an upper layer may cancel before all lower attempts happen. Conversely, if “3 retries” means three extra attempts plus the original, that layer allows four total attempts, not three. Always record total attempts and retry count separately.

Retry amplification can turn partial failure into overload. If a dependency is already slow, retries create more in-flight work, lengthen queues, occupy connection pools, and consume CPU. The resulting latency causes more deadlines to expire, which may trigger more retries. Under load, a small retry rate can have a large effect at a deep dependency. Prefer explicit retry budgets, low bounded attempts, exponential backoff with jitter where supported, and an overall deadline that limits the time and work spent on one request.

### Timeout ladder

A coherent illustrative timeout ladder for a simple synchronous prediction request might be:

| Layer | Illustrative limit | What it bounds | Design rationale |
|---|---:|---|---|
| Client overall deadline | 2.0 s | End-to-end caller wait | Hard outer budget; **[ILLUSTRATIVE]** |
| Ingress/LB request timeout | 1.8 s | Time at edge hop | Leaves a small margin before client deadline; adjust to real deployment |
| Mesh overall request timeout | 1.5 s | Proxy-managed request lifetime where supported | Shorter than ingress; must include retries if implementation semantics say so |
| Mesh per-backend attempt | 400 ms | One backend attempt | Leaves time for bounded retry and response propagation |
| Application processing budget | 1.2 s | App's own work budget | Application should stop starting work when deadline is exhausted |
| Feature-service/Redis call | 250 ms | Dependency operation | Leaves budget for model scoring and response; cancellation semantics must be verified |

These values are **[ILLUSTRATIVE]**, not recommendations for every model API. The actual order depends on intended cancellation, drain, and buffering semantics. Define one deadline budget and allocate it backward from the caller's objective. A per-try timeout must be shorter than the overall deadline, and retry attempts plus backoff must fit inside the overall budget. If the application cannot cancel downstream work, a client timeout may stop waiting while the dependency continues consuming resources.

### Linkerd retries and timeouts: verified concepts, version-gated syntax

Linkerd documents retry and timeout configuration for Services and Gateway API `HTTPRoute`/`GRPCRoute`. The current reference says retries are outbound/client-side behavior: the source workload must be meshed for the proxy to apply them. It also documents route-level annotations taking precedence over Service-level retry annotations and warns that annotation-based retries conflict with `ServiceProfile` retry configuration. Some behaviors have changed across Linkerd releases, including how timeouts compose with retries. **[VERSION-SENSITIVE]** See the official references and verify exact semantics for the selected release.

Template only—confirm annotation values, supported fields, request path, route attachment and schema before use:

```yaml
# File: manifests/unit-08/retry-policy.template.yaml
# [VERIFY] Current Linkerd docs and installed API/schema are authoritative.
apiVersion: v1
kind: Service
metadata:
  name: feature-service
  namespace: ml-platform
  annotations:
    retry.linkerd.io/http: "502,503,504"
    retry.linkerd.io/limit: "1"
    retry.linkerd.io/timeout: "200ms"
    timeout.linkerd.io/request: "800ms"
spec:
  selector:
    app: feature-service
  ports:
    - name: http
      port: 8081
      targetPort: 8081
```

This is a **version-gated teaching template**, not a validated manifest. Confirm the current annotation set and whether the timeout semantics compose as intended. A Service annotation may affect every matching request path and can be too broad; route-level scope may be safer. Never enable retry behavior for a side-effecting endpoint without an idempotency contract. Linkerd retries may have request-body and protocol limitations; the current official reference documents restrictions, so large bodies and streaming endpoints require explicit tests.

### gRPC and long-lived streams

gRPC calls can be unary (one request/one response) or streaming. Server-Sent Events (SSE), WebSockets, and other long-lived connections have different failure semantics from a short unary request. A route retry does not transparently replay an established stream after bytes have been sent. Retrying a partially processed streaming request can duplicate work or lose state. For streaming endpoints, define application-level resume/reconnect semantics, event IDs, deduplication, idle timeout, and client cancellation behavior. Test a stream through the exact selected proxy and route configuration. Do not assume an HTTP timeout applies to all stream phases in the same way.

### Circuit breaking, failure accrual, and outlier behavior

A circuit breaker is a pattern that reduces calls to a failing dependency so it can recover. Application breakers often model closed/open/half-open states; a mesh may implement a different mechanism. Linkerd's official circuit-breaking reference describes endpoint-level failure accrual for HTTP requests: the outbound proxy tracks endpoint failures and may avoid a failing Pod endpoint. That is not the same as claiming Linkerd supports every Envoy-style connection-pool limit or Istio `DestinationRule` field. See [Linkerd Circuit Breaking](https://linkerd.io/docs/reference/circuit-breaking/).

| Mechanism | Scope | What it protects | Limitation |
|---|---|---|---|
| Linkerd endpoint-level failure accrual | Individual endpoints selected by the outbound proxy | Avoids repeatedly sending requests to endpoints with a failure pattern | Exact thresholds/recovery are implementation-specific; does not equal every connection-pool breaker |
| Application circuit breaker | A caller/dependency client | Can express application-specific error thresholds, half-open probes, and business-aware fallbacks | Must be implemented and operated correctly |
| Bulkhead / bounded queue | Thread pool, semaphore, queue, or dependency pool | Prevents one dependency from consuming all resources | Does not identify or repair a bad endpoint |
| Istio/Envoy connection-pool/outlier features | Istio/Envoy-specific configuration | Can control supported connection pools, pending requests, and endpoint ejection | Not portable to Linkerd; verify version-specific fields |
| Kubernetes readiness/endpoint membership | Pod/Service endpoint lifecycle | Removes unready Pods from normal Service endpoint selection | Readiness is not a substitute for request-level failure tracking |

Conceptually:
- **Closed:** normal requests are sent.
- **Open:** calls are rejected or bypass the failing endpoint.
- **Half-open:** a limited probe tests recovery.
This is a generic application-breaker model, not a promise that Linkerd's endpoint failure-accrual state machine exposes these exact states or CLI fields.

Round-robin, least-request/least-connections, and exponentially weighted moving average (EWMA) load balancing each make different assumptions. Round-robin distributes selections cyclically; least-request tries to avoid endpoints with more active work; EWMA can weight recent latency. None is universally best. Choose based on request duration variability, endpoint capacity, queueing, connection reuse, and verified implementation behavior.

### Fault injection, mirroring, rate limits, and egress

Fault injection is a controlled experiment: state a hypothesis, inject one bounded delay or failure, define an abort threshold, collect evidence, and restore the system. Linkerd's current docs include traffic shifting and fault-injection examples, but exact supported route behavior and schema must be verified. Do not assume every Linkerd release supports Istio's `VirtualService` fault fields.

Mirroring duplicates requests to a shadow backend. It can double compute cost, expose sensitive payloads, and repeat side effects. Use synthetic data, disable writes, and explicitly identify which fields may be copied. A shadow model should return a result that is discarded; do not allow mirrored requests to write to Postgres/Redis or trigger external ETL effects.

Local rate limiting constrains a process/proxy; global rate limiting requires coordination and can introduce its own dependency/failure modes. Verify what the chosen Linkerd release supports rather than treating rate limiting as a portable mesh capability. Likewise, Linkerd egress behavior, DNS control, and Istio `ServiceEntry` are not interchangeable. `ServiceEntry` is Istio-specific; it must not appear in Linkerd manifests. Routing to an external destination is not the same as enforcing all egress policy—NetworkPolicy/CNI and external firewall/DNS controls remain relevant.

Application TLS nested inside mesh mTLS can create double encryption. The mesh may see an opaque TCP stream instead of HTTP semantics, reducing L7 routing/retry/telemetry visibility. Choose termination/passthrough deliberately, document trust boundaries, and test the real protocol. Unit 6 owns ingress TLS/cert-manager; M09 owns broader identity and secrets governance.

### 8.6 Level 4 — Expert: Operating at Scale and Under Failure

### Policy-as-code and CI validation

A successful YAML parse is not enough. A safe CI suite should validate:
1. schema against the exact installed CRDs;
2. compatibility of Kubernetes, Linkerd, Gateway API and proxy versions;
3. route attachment and backend readiness;
4. authorized client succeeds;
5. unauthorized meshed identity is denied;
6. unmeshed client is denied where the policy requires it;
7. 90/10 and 50/50 traffic distribution is measured over bounded samples;
8. retry count is bounded and side-effect safety is tested;
9. injected fault triggers the expected bounded degradation;
10. recovery and cleanup return the system to baseline.

Run integration tests on an ephemeral cluster and fail CI if required resources are not cleaned up. A dry-run cannot prove that mTLS is active or that the backend weights behave as expected. Use explicit timeouts and cleanup traps, but do not let a cleanup trap hide the original test failure.

### Retry and policy standards

Set organization-wide standards for retry ownership, maximum attempts, retryable conditions, idempotency requirements, timeout budgets, and the kinds of endpoints that may be retried. Reject unlimited retries and unspecified end-to-end deadlines for synchronous service calls. Require explicit approval for retrying writes or requests with external side effects. Treat client and proxy retries as one combined attempt budget, not independent defaults.

For strict inbound policy, inventory non-meshed callers and provide a migration path. Metrics scrapers, kubelet probes, Jobs/CronJobs, admin tools and ingress components can have different identities and network paths. Avoid broad unauthenticated exceptions as a quick fix; scope an exception to the required port/source and remove it after the caller is enrolled or the path is otherwise secured.

### Incident matrix

| Incident | Symptom | Competing hypotheses | First evidence | Safe mitigation | Prevention / owner |
|---|---|---|---|---|---|
| Retry storm took down `feature-service` | Error rate and concurrency rise together | Mesh retry policy, client retry loop, slow Redis, retrying writes | Request/attempt counts, per-hop latency, app logs, dependency pool/queue state | Freeze rollout, cap retries, protect dependency, shed load if documented | Service owner + platform; retry budget and load test |
| Strict mTLS/policy broke metrics scraper | App requests work but telemetry disappears | Scraper unmeshed, wrong identity, NetworkPolicy blocks path, wrong target port | Scrape errors, Pod enrollment, policy status, proxy diagnostics, CNI flow evidence | Restore only a reviewed narrow scrape path or enroll scraper | Observability owner; test scrape identity during policy rollout |
| Canary split differs from target | Candidate count too high/low | Wrong route attachment, no ready backends, finite sample, retries, persistent streams | Route status, backend endpoints, response-version counts, errors/retries | Pause shift and restore previous known-good route | Release owner; repeatable traffic test and route conditions |
| Breaker/ejection removes all endpoints | Requests fail although Pods exist | Threshold too aggressive, all endpoints share fault, health checks misleading | Endpoint health, proxy logs, response codes, readiness and ejection evidence | Stop load, disable only the bad test policy in disposable lab, restore healthy endpoints | Service/platform; ejection test with stop condition |
| Identity issuer/trust issue | Handshakes fail across many workloads | Expiry, trust mismatch, clock skew, control-plane identity failure | Mesh identity diagnostics, certificate status, proxy logs, control-plane health | Follow documented identity recovery procedure; avoid blind trust reset | Security/platform; expiry monitoring and rotation rehearsal |
| gRPC/SSE stream cut off | Streams fail at a fixed duration or after retry change | Idle timeout, request deadline, LB/proxy timeout, app cancellation | Client/server timestamps, proxy config, stream logs, controlled reproduction | Revert changed timeout; restore reconnect/resume behavior | App owner; stream-specific tests |
| NetworkPolicy blocks proxy/control plane | Proxy checks or peer requests fail | Wrong selector, port/protocol mismatch, missing egress allow, CNI behavior | Policy YAML, labels, endpoints, DNS/control-plane test, CNI evidence | Add narrowly scoped verified allow rule in lab | Network/platform; maintain path matrix |

### Rollback and ownership

A strict policy rollback must not accidentally reopen more traffic than intended. Record the previous policy and a narrow rollback command/manifest, then test the rollback in the same throwaway cluster. When an incident affects production, follow the organization's approved change process; this unit's commands are not authorization to change production.

| Area | Accountable owner | Required evidence |
|---|---|---|
| Mesh and CRD version compatibility | Platform team | Compatibility matrix, release notes, schema checks |
| Workload identity and trust | Platform/security | Issuer lifecycle, expiry signals, rotation runbook |
| Service authorization | Security + service owner | Identity inventory, positive/negative tests |
| Retry/timeout policy | Service owner + platform | Call graph, deadline budget, retry ownership, load test |
| Canary route | Release owner | Route status, backend health, measured distribution, rollback gate |
| SLO/error budget | Service owner / SRE | M10-defined indicators and freeze/rollback policy |
| Telemetry | Observability team | Scraper identity/path, metric definition, data handling |
| Incident response | On-call owner | Alert → triage → mitigation → validation → follow-up |
| Lab cleanup | Learner / lab owner | No test fault, no temporary client, healthy baseline request |

### 8.7 SRE lens

### Indicators and guardrails

Track request success, latency p50/p95/p99 where the sample supports it, retry attempts per logical request, timeout rate, backend attempt rate, endpoint-ejection/failure-accrual behavior, canary distribution, identity/authentication denials, proxy restarts, and policy/config propagation. Exact metric names are **[VERIFY]** against the selected Linkerd release and telemetry setup; this lesson intentionally does not invent them.

Mesh telemetry supports but does not replace application SLIs. A successful proxy-level response may still represent a business failure, and a low proxy error rate can hide work being retried several times. Record both logical request counts and backend attempt counts when possible.

### Alert → triage → mitigation → validation → follow-up

1. **Alert:** request errors/latency, retry amplification, canary guardrail, identity denial, or proxy/endpoint health crosses a service-specific threshold.
2. **Triage:** identify the affected scope—one endpoint, one service, namespace, proxy fleet, control plane, identity issuer, or dependency. Compare app logs with proxy and route evidence.
3. **Mitigation:** freeze canary movement; stop fault injection; restore last known-good routing/policy; cap retries; or remove the faulty endpoint from test traffic using documented controls. Avoid disabling security policy broadly.
4. **Validation:** send a bounded known-good request, verify success and expected identity, confirm retry/endpoint counts return to normal, and check that metrics scraping recovered.
5. **Follow-up:** preserve sanitized evidence, identify the triggering change, add a regression test, and assign an owner/date for the prevention action.

### Error-budget gates

M10 owns formal SLOs/error budgets. For this lab, define the gate before shifting: if request success, latency, or error-budget burn exceeds the service's agreed guardrail, stop the shift and restore the last known-good route. Do not invent a universal threshold such as a fixed p95 increase. Use service-specific objectives and compare against a baseline measured under comparable conditions.

### 8.8 Security lens

| Threat | Control | Verification test | Residual risk |
|---|---|---|---|
| Identity spoofing/misconfiguration | Mesh-managed identity and trusted issuer; least-privilege service accounts | Authorized and unauthorized identity tests; inspect mesh identity diagnostics | Compromised workload can misuse its legitimate identity |
| mTLS mistaken for authorization | Explicit Linkerd policy plus application authorization | Negative request test from a different identity and disallowed method/path where supported | Incorrectly broad policy or application logic remains possible |
| Unmeshed workload/plaintext bypass | Enrollment inventory and authenticated-only inbound policy where required | Test controlled unmeshed client and inspect live Pod proxy state | Host-network/special workloads and bypass paths need separate treatment |
| Overbroad authorization | Narrow identity/route scope and reviewed policy changes | Positive/negative tests and policy diff review | Misclassified identity or unintended route attachment |
| Issuer/trust expiry or clock skew | Expiry monitoring, controlled rotation and recovery plan | Identity diagnostics, validity status and bounded handshake test | A test may miss an alternate trust path or stale client |
| Sensitive traffic mirroring | Synthetic payloads, no side effects, restricted shadow service | Inspect route/mirror config and shadow writes/logs | Metadata and supposedly synthetic fields can still be sensitive |
| NetworkPolicy/mesh-policy confusion | Maintain separate CNI flow matrix and mesh authorization tests | Test network reachability and identity authorization independently | CNI-specific semantics and host traffic need separate validation |
| Application TLS nested in mesh | Document termination points and protocol visibility | Test request visibility and identity on each hop | Proxy may not inspect L7 content when application TLS is opaque |
| Strict policy breaks probes/Jobs/metrics | Caller inventory, identity-aware rollout and tests | Probe, scrape, Job/CronJob and admin-client tests | New callers may be introduced without inventory updates |
| Fault-injection endpoint/config remains | Throwaway namespace, explicit expiry/cleanup check | Inspect routes/config and send a post-cleanup health request | Failed cleanup may leave a persistent rule |
| Retry duplicates side effects | Idempotency keys/deduplication and retry allowlist | Repeat the same request in test and verify exactly one business effect | External systems may not support idempotency |
| Supply-chain or privilege abuse | Pinned reviewed release artifacts, least-privilege RBAC, M12 controls | Inspect image provenance/RBAC and change audit | Upstream compromise or cluster-admin compromise remains high impact |

A service mesh does not automatically make a cluster “zero trust.” mTLS authenticates a peer and protects a connection; authorization defines allowed communication; NetworkPolicy restricts network reachability; application authorization protects business actions. The layers should reinforce each other.

### 8.9 Production checklist

- [ ] Record exact Kubernetes, Linkerd CLI/control-plane/proxy and Gateway API versions.
- [ ] Confirm Linkerd sidecar mode matches Unit 7 and the capstone; do not silently switch to Istio.
- [ ] Inventory Deployments, Jobs/CronJobs, probes, metrics scrapers, ingress, admin clients and unmeshed callers.
- [ ] Verify live proxy enrollment and workload identity, not just namespace labels.
- [ ] Define intended inbound policy and run authorized-positive and unauthorized-negative tests.
- [ ] Verify strict-policy effects on probes, metrics, batch jobs and administrative workflows.
- [ ] Confirm NetworkPolicy allows required proxy, DNS, control-plane and telemetry flows without broad bypasses.
- [ ] Define retry owner, retryable conditions, total attempts, retry budget and idempotency contract.
- [ ] Define per-attempt timeout and overall deadline; validate the timeout ladder against client/ingress/app behavior.
- [ ] Verify route attachment, backend readiness and supported `HTTPRoute` weight syntax.
- [ ] Run at least 1,000 local requests each at 90/10 and 50/50; report errors and deviations without fabricating results.
- [ ] Test a bounded local fault and confirm a stop condition and recovery path.
- [ ] Verify the selected Linkerd endpoint failure-accrual capability and do not assume Istio/Envoy feature parity.
- [ ] Define canary freeze/rollback guardrails using service-specific SLOs.
- [ ] Confirm streaming/gRPC behavior and idempotency before retrying those paths.
- [ ] Verify fault/mirror configuration is removed and no test endpoint is exposed.
- [ ] Record evidence, owner, rollback route and unresolved `[VERIFY]` items.

### 8.10 Hands-on lab set

| Lab | Required outcome | Evidence | Cleanup |
|---|---|---|---|
| 1 — Staged authenticated-only access | Authorized meshed caller succeeds; unauthorized meshed and unmeshed callers match intended policy | Identity/proxy evidence, positive/negative test matrix, policy diff | Restore prior policy and remove test client |
| 2 — Weighted canary | 1,000+ local requests at 90/10 and 50/50; calculate observed split and deviation | Raw response counts, route status, blank/filled measurement table | Restore stable route; remove candidate/test client |
| 3 — Retry/deadline/fault | Bounded failure/delay, retry amplification arithmetic, timeout correction | Request/attempt counts, latency/error table, fault and recovery evidence | Remove fault/retry policy and verify healthy requests |
| 4 — Failure accrual / circuit behavior | Test supported Linkerd endpoint-level failure accrual; document limitations | Endpoint outcomes, logs/metrics if verified, recovery evidence | Stop test load, restore healthy endpoint, remove test policy |

### Global safety and budget

Use only a disposable cluster whose context is confirmed as `kind-m04-mesh-lab`. Plan for approximately 4 CPU cores, 8 GB RAM and 30 GB free disk, but these are learner-provided planning assumptions, not measured requirements for Linkerd. Stop Cilium/Hubble and any full observability stack before the mesh labs. Keep the request rate bounded; do not expose a public endpoint or use real secrets/data. On WSL2, localhost and packet-capture interfaces may differ across Windows, WSL2, Docker, kind nodes and Pods. `kind` does not reproduce cloud load balancers, multi-AZ behavior or production fleet scale.

Before **every mutation**, verify context and the disposable-cluster condition:

```bash
# File: commands/guard-unit-08.sh
set -euo pipefail
EXPECTED_CONTEXT="kind-m04-mesh-lab"
ACTUAL_CONTEXT="$(kubectl config current-context)"
if [[ "${ACTUAL_CONTEXT}" != "${EXPECTED_CONTEXT}" ]]; then
  printf 'Refusing mutation: expected %s, got %s\n' \
    "${EXPECTED_CONTEXT}" "${ACTUAL_CONTEXT}" >&2
  exit 20
fi
if [[ "${CONFIRM_DISPOSABLE_CLUSTER:-}" != "yes" ]]; then
  echo "Set CONFIRM_DISPOSABLE_CLUSTER=yes only after confirming this cluster is disposable" >&2
  exit 21
fi
kubectl --context "${EXPECTED_CONTEXT}" cluster-info
kubectl --context "${EXPECTED_CONTEXT}" get nodes
```

This guard checks the current context and an explicit confirmation string; it cannot independently prove that the cluster contains no valuable workloads. Inspect ownership and cluster inventory before use. Run it again immediately before each mutating operation.

### Lab 1 — Staged strict mTLS with proof of encryption and blocked plaintext

**Goal:** prove an authorized meshed caller can reach `feature-service`, then verify that the selected Linkerd inbound policy blocks an unmeshed client and an unauthorized meshed identity. **Time:** 90–150 minutes. **Resource plan:** existing Linkerd control plane plus sample app and one temporary test client; do not add a second mesh or dashboard. **Prerequisites:** Lab 2 of Unit 7 completed, sample Services healthy, and exact Linkerd policy CRDs verified.

1. **Inventory and baseline.** Guard context; record namespace labels, Pods/containers, ServiceAccounts, endpoints, existing inbound policy and NetworkPolicies. Capture a successful baseline request. Inventory metrics scrapers, probes, Jobs/CronJobs, ingress and admin clients.
2. **Confirm identities.** Verify both source and destination Pods have the Linkerd proxy and the current documented diagnostics show expected identities. If proxy enrollment is incomplete, stop; do not test strict policy yet.
3. **Generate policy from current official docs.** Consult [Linkerd Authorization Policy](https://linkerd.io/docs/reference/authorization-policy/) and confirm installed `Server`, `MeshTLSAuthentication`, `ServerAuthorization`, and/or `AuthorizationPolicy` schemas as appropriate. Do not paste Istio `PeerAuthentication` or invented Linkerd fields. Apply only a reviewed policy that scopes the intended destination port/route and caller identity.
4. **Positive test.** Send a bounded request from the authorized meshed `model-client` identity. Expected output **[ILLUSTRATIVE]**: HTTP success and a response from the expected feature service.
5. **Negative tests.** Use a separate meshed ServiceAccount/identity that is not allowed, and a controlled unmeshed test Pod. Expected results **[ILLUSTRATIVE]**: requests denied according to the intended policy. If either succeeds, stop and inspect actual policy scope/route attachment; do not claim enforcement.
6. **Encryption evidence.** Use the selected release's documented Linkerd identity/diagnostic command and, if needed, a bounded local packet capture on a known interface. Verify that the request traverses the meshed proxy path and identity diagnostics report the expected peer. Ciphertext alone is not sufficient proof of identity. Do not save keys or sensitive payloads.
7. **Abort/rollback.** Abort if the authorized caller fails, metrics/probes unexpectedly break, or policy scope exceeds the sample. Restore the captured policy state and retest the baseline. Do not “fix” the lab by opening all unauthenticated traffic.
8. **Expected evidence [ILLUSTRATIVE]:** positive and negative test matrix, Pod/proxy evidence, identity diagnostics, policy diff, packet-capture method/limitations, and restored health. No actual result is prefilled.

| Caller | Expected result under intended lab policy | Actual result | Evidence / explanation |
|---|---|---|---|
| Authorized meshed identity | Allow |  |  |
| Unauthorized meshed identity | Deny |  |  |
| Unmeshed/plaintext test client | Deny |  |  |
| Metrics scraper / probe | Deliberate allow or enrolled identity; document which |  |  |

**Cleanup and post-cleanup verification:** restore intended policy, delete only the temporary test client after guarding context, and verify sample request success, metrics scrape/probe health, no temporary Pod remains, and the final policy matches the intended baseline. Save sanitized evidence. This lab was not executed during authoring.

### Lab 2 — 90/10 and 50/50 canary over at least 1,000 requests

**Goal:** route requests between stable and candidate model API Services and measure the observed distribution. **Time:** 90–150 minutes. **Resource plan:** two tiny API deployments, Linkerd, and a bounded local request client. **Prerequisites:** version-compatible `HTTPRoute` backend weights verified; stable and candidate Services return a version field; route remains local-only.

1. Guard the context. Verify the two backend Services and their ready endpoints. Confirm the Gateway API CRDs and Linkerd support for the chosen route parent and weight fields.
2. Apply a reviewed `HTTPRoute` template with stable/candidate weights 90/10. Check route status/conditions and test one request.
3. Use `kubectl port-forward` to a local-only Service/route as appropriate. Ensure `LOCAL_ENDPOINT` is `http://127.0.0.1:PORT` or `http://localhost:PORT`; do not bind to a public interface.
4. Run the script in Section 8.4 with `REQUESTS=1000` and a bounded delay. Repeat for a second run if the laptop remains responsive. Capture errors and version counts.
5. Change the weights to 50/50 through a guarded, reviewed mutation. Check route status and backend readiness again. Repeat at least 1,000 requests for each measured target distribution.
6. Calculate observed percentages and absolute percentage-point deviation using the formula in Section 8.5. Keep failures and unknown-version responses visible; record the denominator and whether the script counts successful versioned responses separately from errors.
7. If a header-based tester route is desired, add it only after verifying the selected Linkerd/Gateway API supports the exact match and precedence semantics. Do not make the test route publicly reachable.
8. **Expected output [ILLUSTRATIVE]:** a version-count summary with stable/candidate counts, percentages, errors, malformed/unknown versions and run duration. This lesson does not claim that the script was run or that a particular split was observed.

| Target | Total sent | Stable count / % | Candidate count / % | Errors | Retries (if measurable) | Deviation (pp) | Duration / method |
|---|---:|---|---|---:|---|---|---|
| 90/10 run 1 |  |  |  |  |  |  |  |
| 90/10 run 2 |  |  |  |  |  |  |  |
| 50/50 run 1 |  |  |  |  |  |  |  |
| 50/50 run 2 |  |  |  |  |  |  |  |

**Cleanup:** restore the stable route/weight and verify requests return the expected stable behavior; remove the candidate deployment only after confirming no route references it. Stop port-forwards and delete test resources only after context guard. Verify no public Service/route/listener was created and the app is healthy. A finite local request sample is not proof of production canary safety.

### Lab 3 — Fault injection, retry amplification, and timeout correction

**Goal:** compare baseline, bounded failure, retry behavior and corrected timeout/deadline policy. **Time:** 90–180 minutes. **Resource plan:** local sample app and one deliberately failing/delayed backend; no full observability stack. **Prerequisites:** retry syntax verified against current Linkerd docs and a safe, idempotent GET endpoint or synthetic scoring request with no side effects.

1. Define a hypothesis, e.g. “one transient 503 is retried at most the configured bound, but persistent failure returns within the overall deadline.” Define a stop condition before injecting the fault.
2. Record baseline request count, successes/errors, latency, downstream attempt count if observable, and resource samples.
3. Confirm the selected Linkerd release's retry annotations or Gateway API fields, retryable response codes, request body limitations, and timeout composition. If exact syntax cannot be verified, do not apply the retry configuration; complete the arithmetic and observation plan instead.
4. Set a small explicit retry bound and per-attempt timeout shorter than the overall deadline. Ensure the operation is idempotent and retries have one clearly named owner. Avoid enabling both app and mesh retries without a combined budget.
5. Inject a local bounded delay or failure using a test-only backend/route. Do not use an external destination. The fault should expire automatically or have a documented immediate removal step.
6. Run a small, rate-limited request sample. Record logical client requests separately from backend attempts. Compare theoretical amplification with observed behavior; the two numbers need not match.
7. Tune the policy or timeout ladder and repeat the same test. Verify the caller finishes within its deadline and retries stop at the configured limit. Do not assert that application work was cancelled unless the app/dependency evidence proves it.
8. **Expected output [ILLUSTRATIVE]:** a before/during/after table, retry arithmetic, observed errors/latency and recovery evidence. No numeric result is prefilled.

| Condition | Logical requests | Backend attempts | Success/errors | Median/p95 if supported | Deadline respected? | Notes |
|---|---:|---:|---|---|---|---|
| Baseline |  |  |  |  |  |  |
| Fault without retry |  |  |  |  |  |  |
| Fault with bounded retry |  |  |  |  |  |  |
| Corrected timeout/retry |  |  |  |  |  |  |

**Cleanup:** remove fault route/handler and temporary retry/timeout config; verify no injected error/delay remains, a known-good request succeeds, request count returns to baseline behavior, and no temporary resource remains. Save only synthetic/sanitized data. If Linkerd's exact behavior cannot be safely configured in the selected release, document the unsupported/unverified component rather than inventing a field.

### Lab 4 — Circuit breaking / endpoint failure accrual with evidence

**Goal:** observe only the endpoint-level failure-accrual behavior supported by the selected Linkerd release and compare it with an application breaker conceptually. **Time:** 60–120 minutes. **Resource plan:** two local backend replicas (one healthy, one controlled failure) and low-rate client. **Prerequisites:** official Linkerd circuit-breaking reference reviewed and the exact supported failure-accrual configuration/observability confirmed.

1. State a hypothesis and stop condition. Example: “Repeated qualifying failures from one test endpoint may cause the outbound proxy to avoid that endpoint according to documented failure-accrual behavior.”
2. Verify whether the selected release exposes a configurable failure-accrual strategy or only documented behavior. Do not invent a threshold field. If configuration is not supported or cannot be verified, observe the documented default behavior only if the official guide supplies a safe test; otherwise mark this portion untested.
3. Run a small baseline request sample with both endpoints healthy. Record per-version/endpoint outcomes if available.
4. Enable only the verified test behavior or deliberately make one local backend return a controlled error. Limit requests and stop if the healthy endpoint starts failing or the overall error threshold is crossed.
5. Capture response counts and documented proxy diagnostics/metrics. Metric names are `[VERIFY]`; if unavailable, use response counts, Pod logs and event evidence.
6. Stop the fault and verify recovery behavior. Do not assume an exact half-open state or recovery interval unless the selected implementation documents it.
7. Compare the observed proxy endpoint behavior with an application-level breaker/bulkhead: an application breaker can be business-aware and manage concurrency/queues, while endpoint failure accrual is proxy-level and implementation-specific.
8. **Expected output [ILLUSTRATIVE]:** a timeline showing baseline, fault onset, response behavior, fault removal and recovery; no benchmark or ejection count is prefilled.

| Phase | Fault active? | Requests | Errors | Endpoint evidence | Stop condition reached? | Recovery verified? |
|---|---|---:|---:|---|---|---|
| Baseline | No |  |  |  |  |  |
| Fault | Yes |  |  |  |  |  |
| Recovery | No |  |  |  |  |  |

**Cleanup:** stop the request generator, remove the failing handler/configuration, verify both backends are healthy, restore route/policy state, and confirm a known-good request succeeds. Check that no temporary fault route, retry policy, test client or port-forward remains. Do not add a fifth lab or install another mesh solely to compare circuit-breaker APIs.

### 8.11 Self-check questions

1. **Why is mTLS not authorization?**  
   **Answer:** mTLS authenticates the peer and protects the connection; authorization decides which action/resource the authenticated identity may access. Application authorization still protects business operations. **Tempting wrong answer:** “Any certificate signed by the trusted mesh CA can call every endpoint.” Trust is not a blanket permission.

2. **How do you verify identity separately from encryption?**  
   **Answer:** Use documented mesh identity diagnostics, confirm the source/destination proxies and expected peer identity, and run positive/negative access tests. Packet capture can support the transport analysis but unreadable bytes alone do not prove identity. **Tempting wrong answer:** “TLS-looking packets prove the correct workload was authenticated.”

3. **Why can strict inbound policy break Jobs or metrics scrapers?**  
   **Answer:** They may be unmeshed, use a different ServiceAccount/identity, or follow a distinct probe/scrape path. Inventory and test them before enforcing policy. **Tempting wrong answer:** “If the Deployment works, all callers are covered.”

4. **Why may a 90/10 route not produce exactly 900/100 responses?**  
   **Answer:** Finite sampling, backend readiness, connection/request semantics, retries, sticky behavior, route attachment, and errors affect observed counts. **Tempting wrong answer:** “Configured weights are exact per-sample quotas.”

5. **How do you calculate retry amplification?**  
   **Answer:** For the stated call graph, if each of three layers permits three total attempts, worst-case deepest-layer attempts can reach `3 × 3 × 3 = 27` per original request. **Tempting wrong answer:** “Three retries means three total attempts.” It usually means three additional attempts plus the original, unless the API defines otherwise.

6. **Why do retries need idempotency and a budget?**  
   **Answer:** A repeated write or external side effect can duplicate effects, and retries add load. Define retryable failures, total attempts, deadline, and idempotency/deduplication. **Tempting wrong answer:** “A 5xx response proves the server did not perform the operation.”

7. **How do you construct a timeout ladder?**  
   **Answer:** Start with the caller's overall deadline, allocate smaller budgets to upstream hops and per-attempt work, include backoff/retries, and test cancellation behavior. **Tempting wrong answer:** “Set every timeout to the same large number.” That leaves ambiguous cancellation and can exceed the caller's deadline.

8. **How is a mesh endpoint breaker different from an application breaker?**  
   **Answer:** Linkerd documents endpoint-level failure accrual for HTTP requests; an application breaker may manage business-aware failure thresholds, queues, and half-open probes. **Tempting wrong answer:** “All meshes expose the same Envoy circuit-breaker settings.”

9. **Can NetworkPolicy block a correctly configured mesh request?**  
   **Answer:** Yes. The CNI enforces network reachability independently and can block the peer, DNS, or control-plane path. **Tempting wrong answer:** “The proxy bypasses NetworkPolicy.”

10. **Why is traffic mirroring risky for sensitive payloads?**  
    **Answer:** It duplicates data and workload, may expose personal or confidential fields, and can repeat side effects. Use synthetic data and a read-only shadow backend. **Tempting wrong answer:** “Shadow traffic is safe because its response is discarded.”

11. **When should a canary be frozen or rolled back?**  
    **Answer:** When pre-agreed service SLO/error-budget guardrails, error rates, latency, or security checks breach. M10 defines the formal policy. **Tempting wrong answer:** “Continue until the candidate receives enough traffic even if the service is unhealthy.”

12. **What if the chosen mesh does not support a desired feature?**  
    **Answer:** State the gap and either demonstrate a verified supported behavior or leave that component untested. **Tempting wrong answer:** “Copy a similar-looking CRD from another mesh.” Similar names do not imply compatible semantics.

### 8.12 Evidence artifacts

Use a local evidence tree such as `evidence/unit-08/`. This is guidance only; do not create repository files other than the lesson as part of this authoring task.

- `versions.txt` — OS/WSL2, Docker, kind, Kubernetes, Linkerd CLI/control-plane/proxy and Gateway API CRD versions.
- `context-and-inventory.txt` — disposable context confirmation, namespace, ServiceAccounts, workloads, endpoints and NetworkPolicies.
- `mtls-identity-evidence.txt` — sanitized diagnostics showing expected identity/trust; no private keys.
- `mtls-positive-negative-tests.csv` — authorized, unauthorized and unmeshed client results.
- `packet-capture-method.md` — interface/location, capture command source, limitations and redaction notes; no sensitive payloads.
- `route-status.txt` — HTTPRoute conditions, backend readiness, configured weights and schema/version.
- `canary-90-10.csv` / `canary-50-50.csv` — raw version counts, errors, target/observed percentages, percentage-point deviation and run duration.
- `retry-amplification.md` — call graph, total attempts per layer, theoretical bound, observed backend attempts and caveats.
- `timeout-ladder.md` — deadline budget, layer timeout, cancellation semantics and owner.
- `fault-experiment.csv` — hypothesis, fault window, stop condition, request outcomes and recovery.
- `breaker-evidence.txt` — verified endpoint behavior and available diagnostics; do not invent metric names.
- `cleanup-proof.txt` — baseline request, absence of temporary clients/fault config/port-forwards and resource inventory.
- `unresolved-verification.md` — current-version fields and behaviors still awaiting confirmation.

Never store private keys, real credentials, raw Kubernetes Secrets, customer data, or unredacted sensitive payloads. The measurement tables remain blank until a learner executes the tests.

### 8.13 Common interview and design-review questions

1. **How do mTLS, workload identity, authorization, NetworkPolicy, and application TLS complement one another?**  
   **Model answer:** mTLS protects the connection and authenticates peers; workload identity provides the principal; mesh authorization decides supported service/route access; NetworkPolicy limits network reachability; application authorization protects business actions. Application TLS can add an independent encrypted layer but may hide L7 data from the proxy. Evidence should include identity diagnostics, positive/negative tests, CNI reachability checks, and app-level authorization tests.

2. **How do you stage a strict-mTLS rollout without breaking Jobs, probes, or telemetry?**  
   **Model answer:** Inventory every caller and workload class; prove enrollment/identity; observe existing flows; apply a narrow policy to one service; test authorized, unauthorized and unmeshed callers; verify probes, scrapes, Jobs and admin clients; expand by ring with rollback gates. Evidence is the caller inventory, policy diff, positive/negative test matrix and recovered telemetry. Do not assume Istio permissive-mode YAML applies to Linkerd.

3. **Why can a configured 90/10 canary produce a different measured split?**  
   **Model answer:** Weights are routing targets, not exact finite-sample quotas. Route attachment, endpoint readiness, connection reuse, retries, long-lived streams and failed responses affect observed counts. Send at least 1,000 local requests per target, repeat runs, count errors separately, and calculate absolute percentage-point deviation. Evidence includes route conditions, backend readiness and response counts.

4. **How do you prevent retry amplification in a multi-hop call graph?**  
   **Model answer:** Assign retry ownership, define retryable conditions, explicit total attempts, per-attempt timeout and overall deadline, use bounded backoff/jitter where supported, and require idempotency for side effects. Calculate the worst-case attempt product across layers and measure logical requests versus backend attempts. Evidence includes configuration, call graph, request/attempt counts and load test.

5. **How do you decide where to place timeouts, circuit breakers, and outlier detection?**  
   **Model answer:** Work backward from the caller's deadline, ensure per-attempt budgets fit inside it, and align cancellation semantics across ingress, proxy, application and dependency. Use application breakers for business-aware failure isolation and queues; use only the selected mesh's documented endpoint failure behavior. Evidence includes a timeout ladder, fault test, endpoint health and recovery proof. Do not claim Linkerd exposes every Envoy/Istio breaker field.

### 8.14 Sources and verification notes

### Consulted sources

- **Linkerd, “Automatic mTLS.”** https://linkerd.io/docs/features/automatic-mtls/ — consulted for mesh mTLS concepts, identity issuance, authenticated transport, and the default acceptance of plaintext from non-meshed sources.
- **Linkerd, “Authorization Policy.”** https://linkerd.io/docs/features/server-policy/ — consulted for the policy model and the fact that policy enforcement depends on proxy enrollment.
- **Linkerd, “Authorization Policy Reference.”** https://linkerd.io/docs/reference/authorization-policy/ — consulted for current policy concepts/resources and identity-based authorization.
- **Linkerd, “Retries.”** https://linkerd.io/docs/reference/retries/ — consulted for retry annotations and configuration caveats.
- **Linkerd, “Retries and Timeouts.”** https://linkerd.io/2-edge/features/retries-and-timeouts/ — consulted for outbound retry behavior, timeout composition and safety warnings; edge docs are version-sensitive and must not be treated as a stable release pin.
- **Linkerd, “HTTPRoute Reference.”** https://linkerd.io/docs/reference/httproute/ — consulted for backend weights and request/backend timeout concepts.
- **Linkerd, “Traffic Shifting.”** https://linkerd.io/2-edge/tasks/traffic-shifting/ — consulted for Gateway API traffic shifting and the deprecation status of the SMI TrafficSplit path; current route details need release verification.
- **Linkerd, “Circuit Breaking.”** https://linkerd.io/docs/reference/circuit-breaking/ — consulted for endpoint-level failure-accrual behavior.
- **Linkerd, “HTTP, HTTP/2, and gRPC Proxying.”** https://linkerd.io/docs/features/http-grpc/ — consulted for HTTP/gRPC L7 behavior and application-TLS visibility caveats.
- **Available M04 roadmap copy (`Roadmap(5).md`), master syllabus (`PROMPT-Kubernetes-Networking-Ingress-and-Service-Mesh(9).md`), Units 5–7, and uploaded Unit 8 prompt.** Consulted for scope, cross-unit boundaries, sample namespace/ports and Linkerd sidecar-mode choice. Unit 8 prompt is the controlling requirements source.

### Official references to verify

- Linkerd current supported stable release and Kubernetes compatibility matrix.
- Current Linkerd CLI installation and control-plane/proxy upgrade procedure.
- Current Linkerd policy CRDs and schemas, including served API versions for `Server`, `HTTPRoute`, `MeshTLSAuthentication`, `NetworkAuthentication`, `ServerAuthorization`, and `AuthorizationPolicy`.
- Current inbound default policy semantics and exact procedure to require authenticated callers while preserving intended probes/scrapers/jobs.
- Current `HTTPRoute` route attachment, backend weight, retry and timeout support for the selected release and Gateway API CRDs.
- Current retry annotation values, default/limit semantics, request-body restrictions, `ServiceProfile` interactions and timeout/retry composition.
- Current Linkerd endpoint failure-accrual configuration and diagnostics; do not infer Istio/Envoy connection-pool parity.
- Kubernetes official docs for NetworkPolicy, probes, Pod lifecycle, Jobs/CronJobs, resource metrics, and admission.
- SPIFFE specifications for workload identity and trust-domain concepts.
- Gateway API specification and GAMMA materials for supported route semantics.
- Google SRE Book/Workbook for overload, retries, canary rollout, SLOs and incident response.

### Unresolved verification items

1. Exact Linkerd CLI/control-plane/proxy version and Kubernetes compatibility for the learner's environment.
2. Exact installed Gateway API CRD version, route parent/attachment model and schema support.
3. Current policy CRD API versions/fields and the safest precise configuration for the intended strict/authenticated-only test.
4. Exact Linkerd diagnostics command for showing workload identity and proxy health in the chosen release.
5. Whether the existing shared sample app exposes the expected `model_version` field and local `/predict` endpoint.
6. Whether the learner has Metrics API/metrics source and any usable packet-capture tooling in WSL2.
7. Exact retry annotation and timeout composition for the selected Linkerd release.
8. Exact endpoint failure-accrual tuning/telemetry available in the chosen release.
9. Real 90/10 and 50/50 measured counts, latency, errors, retries, and cleanup outcomes; no results have been fabricated.
10. Confirm Unit 8 and capstone still use Linkerd sidecar mode; the Unit 7 choice is explicitly marked as an assumption pending full cross-file confirmation.

### Runtime execution status

**Reasoned review only; commands and labs were not executed in this environment.** Selected official Linkerd feature/reference pages were accessed, but the full current compatibility matrix and all API schemas were not audited, and no cluster was available for runtime validation. No performance results, canary counts, or incident reproductions are claimed. This AI self-audit is not independent external validation.

## Appendix A — Command and manifest reference

| Command/configuration | Purpose | Safe use / expected evidence | Version/implementation caveat |
|---|---|---|---|
| `kubectl config current-context` | Check active context | Must match `kind-m04-mesh-lab` before mutation | Does not prove cluster contains no valuable work |
| `kind get clusters` | Inventory local kind clusters | Identify the lab cluster before create/delete | Local kind version/runtime dependent |
| `linkerd version` | Inspect CLI and server version | Record CLI/control-plane version evidence | Exact output differs by release |
| `linkerd check` | Validate Linkerd installation | Readiness/health diagnostics | Not proof of app-level request success |
| `kubectl get crd` | Inspect installed APIs | Confirm route and policy CRDs and served versions | Do not delete shared CRDs blindly |
| `kubectl explain <kind>.spec --api-version=<group/version>` | Inspect API schema where supported | Verify fields before authoring manifest | Exact kind/group/version must be discovered first |
| `kubectl apply --dry-run=server -f <file>` | Ask API server to validate schema/admission | Review errors before applying | Does not prove runtime semantics or traffic behavior |
| `kubectl get httproute -n ml-platform -o yaml` | Inspect route status/config | Check parent and backend conditions | Requires Gateway API CRD and RBAC |
| `kubectl get pods -n ml-platform -o wide` | Inspect workloads | Readiness, Pod IP, restart counts | Not proof of identity |
| Linkerd identity/proxy diagnostics | Verify peer identity and proxy health | Use command from selected release's official CLI help | Exact command must be verified; not fabricated here |
| `retry.linkerd.io/*` annotations | Configure supported retry behavior | Apply only after reading current retry reference | Version-sensitive; interactions with ServiceProfile and route policy matter |
| `HTTPRoute.spec.rules[].backendRefs[].weight` | Weighted backend routing | Validate route status and count versioned responses | Gateway API version/implementation support must be checked |
| Linkerd policy resources | Restrict inbound access by identity/route | Positive/negative tests | Verify API version and all fields in installed CRDs |
| Local `curl` request loop | Generate bounded requests | Only localhost endpoint, explicit count and delay | Must preserve response/error accounting |
| `kubectl top pods` | Sample CPU/memory | Use only if metrics source is available | Metrics API may be absent |
| **⚠ DESTRUCTIVE** official mesh policy rollback | Restore prior test policy | Guard context, capture current state, verify requests afterward | No generic delete command is provided; restore exact reviewed state |

## Appendix B — Troubleshooting decision trees

### B1. Authorized workload cannot connect after strict/authenticated-only policy

- **Symptom:** a previously successful request is denied or times out.
- **Hypotheses:** source/destination not meshed, identity mismatch, wrong route/port scope, policy reference incorrect, NetworkPolicy blocks the path, app itself unhealthy.
- **First evidence:** Pod/container list, events, current policy/CRDs, Service endpoints, proxy diagnostics, application logs and a bounded request.
- **Interpretation:** distinguish transport/identity failure, authorization denial, network reachability, and application error.
- **Safe mitigation:** restore the last known-good sample policy or fix the narrowly scoped identity/route reference; do not open all unauthenticated traffic.
- **Prevention:** positive/negative policy tests and caller inventory.

### B2. Plaintext/unmeshed client unexpectedly succeeds or fails

- **Symptom:** the unmeshed test does not match the expected policy result.
- **Hypotheses:** policy does not cover the port, default inbound policy differs, test path bypasses intended Service, source is actually meshed, or route/policy CRD is not active.
- **First evidence:** live source Pod containers, actual destination/port, current policy and status, Service endpoints, proxy diagnostics.
- **Interpretation:** default mTLS between meshed peers does not by itself prove plaintext from every source is denied.
- **Safe mitigation:** stop test and correct policy using the selected release docs; re-run both positive and negative cases.
- **Prevention:** assert test-client enrollment state and test exact path.

### B3. Metrics scraper/probe/Job fails after policy change

- **Symptom:** app traffic works but scraping, probes, or batch jobs fail.
- **Hypotheses:** caller unmeshed, identity not allowed, port/selector mismatch, NetworkPolicy block, sidecar lifecycle issue.
- **First evidence:** scraper/job/probe events and logs, Pod proxy presence, target port, policy and CNI reachability.
- **Interpretation:** different callers may have different identity and protocol paths.
- **Safe mitigation:** restore only the required reviewed path or enroll the caller; do not disable security broadly.
- **Prevention:** caller inventory and dedicated scrape/Job tests before strict policy.

### B4. Canary distribution differs from target

- **Symptom:** stable/candidate counts differ from configured weight.
- **Hypotheses:** route not attached, backend not ready, wrong Service/port, finite sample, retries, long-lived connections, unknown version response.
- **First evidence:** route conditions, backend endpoint state, raw version counts, errors/retries and run conditions.
- **Interpretation:** configured weights are not exact per-sample quotas; route attachment must be proven.
- **Safe mitigation:** freeze shift, validate route status and backend readiness, restore stable routing if guardrails breach.
- **Prevention:** repeatable local 1,000+ request tests and explicit result accounting.

### B5. Retry storm or downstream amplification

- **Symptom:** backend attempts/concurrency increase faster than logical requests.
- **Hypotheses:** retries at several layers, retrying non-idempotent operation, retrying persistent errors, too-long per-try timeout, deadline mismatch.
- **First evidence:** client request count, backend attempts, retry config at each layer, per-hop latency, dependency queues/pools.
- **Interpretation:** multiply total attempts per layer for a worst-case bound; compare to observed counts.
- **Safe mitigation:** stop rollout/fault, cap attempts, restore bounded timeout and protect dependency capacity.
- **Prevention:** retry owner, idempotency contract, retry budget and load tests.

### B6. Timeouts occur at different hops or streams are cut off

- **Symptom:** client sees timeout while backend continues, or gRPC/SSE ends at a fixed duration.
- **Hypotheses:** client/ingress/mesh/app timeout mismatch, stream idle timeout, deadline not propagated, work not cancellable.
- **First evidence:** timestamped client/server logs, configured timeout ladder, proxy diagnostics and stream-specific reproduction.
- **Interpretation:** request timeout and response/idle timeout can differ; cancellation may not stop dependency work.
- **Safe mitigation:** revert the most recent timeout change, restore a coherent budget, validate reconnect/resume behavior.
- **Prevention:** end-to-end deadline tests and separate unary/stream tests.

### B7. Circuit breaker/failure accrual removes too many endpoints

- **Symptom:** service errors rise although Pods exist.
- **Hypotheses:** every endpoint shares a fault, thresholds too aggressive, wrong endpoint health, retry load triggers correlated failures.
- **First evidence:** endpoint readiness, proxy logs/diagnostics, per-endpoint responses, app logs and dependency health.
- **Interpretation:** endpoint ejection is not proof the application is repaired; a whole fleet can be unhealthy at once.
- **Safe mitigation:** stop test load, remove the injected fault, restore healthy endpoints and documented policy.
- **Prevention:** explicit stop condition and recovery test in a throwaway cluster.

### B8. Fault-injection configuration remains active

- **Symptom:** errors/delay persist after test window.
- **Hypotheses:** wrong route edited, separate resource remains, old Pod/template still has fault behavior, rollback applied to wrong context.
- **First evidence:** guarded context, route/resource inventory, current policy diff, request test and Pod template.
- **Interpretation:** successful apply/delete command does not prove every relevant rule was removed.
- **Safe mitigation:** stop client load, inspect ownership, restore exact baseline resource and verify known-good request.
- **Prevention:** save baseline, scope faults to a lab-only route, cleanup verification and evidence checklist.

## Appendix C — Claim register

Confidence refers to the general claim as written, not validation of the learner's specific cluster. `VERIFY` indicates release/environment confirmation is still required.

| ID | Section | Claim | Source/document section | Confidence | Status tag | Verification needed |
|---|---|---|---|---|---|---|
| U8-C01 | 8.3 | Linkerd automatically uses mTLS between meshed applications and may accept non-meshed plaintext by default | Linkerd Automatic mTLS | High | Consulted | Confirm selected release and policy configuration |
| U8-C02 | 8.4 | Linkerd authorization policy can constrain traffic to meshed workloads and identity-based access | Linkerd Authorization Policy / Reference | High | Consulted | Verify exact CRD versions and fields |
| U8-C03 | 8.4–8.5 | Linkerd supports retries/timeouts on documented Service/route configuration paths | Linkerd Retries / HTTPRoute reference | High | Consulted, version-sensitive | Verify exact release syntax and interactions |
| U8-C04 | 8.4–8.5 | Linkerd documents Gateway API backend weights for traffic shifting; older SMI TrafficSplit path is deprecated in current docs | Linkerd Traffic Shifting / HTTPRoute reference | High | Consulted, version-sensitive | Verify Gateway API version and route attachment |
| U8-C05 | 8.5 | Linkerd endpoint-level failure accrual is not identical to every Envoy/Istio connection-pool breaker feature | Linkerd Circuit Breaking; architecture distinction | High | Consulted | Verify current configurable strategy and diagnostics |
| U8-C06 | 8.5 | Three layers each allowing three total attempts can yield a worst-case factor of 27 under stated call-graph assumptions | Explicit arithmetic in lesson | High | Derived | Validate actual retry semantics for configured layers |
| U8-C07 | 8.5 | Weighted routing is a target distribution, not a guarantee for every finite sample | Gateway API/Linkerd routing semantics and statistical reasoning | High | General principle | Verify implementation-specific balancing behavior |
| U8-C08 | 8.5 | Retry safety depends on idempotency, budgets and total deadlines | Linkerd retry guidance; SRE engineering principle | High | Consulted/inferred | Check application side-effect semantics |
| U8-C09 | 8.3–8.8 | mTLS does not replace application authorization or NetworkPolicy | Security-layer distinction | High | General principle | Test actual CNI and application controls |
| U8-C10 | 8.4 | The `HTTPRoute` template is a schema-gated illustration, not validated manifest | Authoring limitation | High | VERIFY | Confirm installed CRDs and server-side dry-run |
| U8-C11 | 8.4 | Linkerd retry annotation examples are release-sensitive and can conflict with ServiceProfile config | Linkerd Retries reference | High | Consulted, version-sensitive | Confirm current docs and absence of conflicting ServiceProfile |
| U8-C12 | 8.4 | Linkerd retry/timeout behavior occurs on outbound/source proxy path | Linkerd retries/timeouts docs | High | Consulted, version-sensitive | Verify selected release and protocol |
| U8-C13 | 8.5 | Application TLS inside mesh can hide L7 request semantics from proxy | Linkerd HTTP/gRPC proxying docs | High | Consulted | Verify actual protocol termination path |
| U8-C14 | 8.10 | The request script restricts endpoint to localhost and bounds request count/rate | Script authored in lesson | High | Authored, not executed | Run lint/review and test only on disposable lab |
| U8-C15 | All | No lab or command was executed during authoring | Runtime status | High | Runtime limitation | Human execution and evidence required |
| U8-C16 | All | Unit 7's Linkerd sidecar choice is used for cross-unit consistency | Available Unit 7 lesson | High | ASSUMPTION inherited | Confirm against capstone and authoritative prompt pack |
| U8-C17 | 8.4 | Policy template API versions and route attachment require installed-schema verification | Official reference pages and authoring caution | High | VERIFY | Confirm selected release CRDs |
| U8-C18 | 8.6 | SLO-based canary freeze/rollback should use service-specific guardrails | Google SRE principles / M10 boundary | High | General guidance | Obtain approved service-specific SLOs |

## Appendix D — Ten-pass audit and correction log

This is an internal AI self-audit, not an independent external validation.

| Pass | Result | Checks performed | Defects found / corrections made | Unresolved risks |
|---|---|---|---|---|
| 1. Completeness | PASS WITH LIMITATIONS | Required sections 8.0–8.14, Appendices A–E, four labs, diagrams/tables, calculations and evidence list | Included all required headings, four lab outcomes, canary tables and decision/incident tables | Unit 8/capstone prompt pack was not available for full direct inspection |
| 2. Technical correctness | PASS WITH LIMITATIONS | TLS/mTLS, identity/authz boundaries, retry arithmetic, timeout ladder, weighted routing and failure-accrual concepts | Explicitly distinguished Linkerd from Istio; avoided claiming portable permissive-mode behavior | Exact runtime behavior depends on selected Linkerd/Gateway API release |
| 3. Command/manifest validity | PASS WITH LIMITATIONS | Context guard, local-only script, schema-verification instructions, version-gated templates | Avoided inventing a Linkerd policy YAML and marked HTTPRoute/annotation templates for verification | Scripts/templates were not executed or server-validated |
| 4. Currency | PASS WITH LIMITATIONS | Consulted current official Linkerd feature/reference pages for mTLS, policy, retries, HTTPRoute, shifting and circuit breaking | Tagged edge/release-sensitive references and deprecated SMI TrafficSplit path | Full release matrix and installed CRDs not audited |
| 5. Security | PASS WITH LIMITATIONS | No production endpoints/secrets, caller inventory, identity/authz distinction, mirroring privacy and cleanup warnings | Added positive/negative tests and NetworkPolicy interaction | Actual lab policy and caller identity unknown |
| 6. Fabrication scan | PASS WITH LIMITATIONS | Searched for unsupported numbers, versions, metrics, benchmark results and claims of execution | Measurement tables blank; illustrative values tagged; no performance winner asserted | Some exact current syntax remains explicitly unresolved |
| 7. Executability | PASS WITH LIMITATIONS | Four lab procedures, guard, bounded request counts, stop conditions, evidence and cleanup | Included local-only endpoint guard and safe alternatives if feature syntax cannot be verified | Requires learner's sample app, current CRDs and runtime validation |
| 8. Pedagogy | PASS | L1–L4 progression, glossary, request path, examples, arithmetic, tables and answer keys | Explained concepts before templates | Learner must adapt to actual sample response schema |
| 9. Cross-file consistency | PASS WITH LIMITATIONS | Checked Unit 7 choice and Unit 5 namespace/port assumptions; respected M08/M10 boundaries | Kept Linkerd sidecar mode and `ml-platform` example | Unit 8/capstone prompts were not directly inspected; assumption must be confirmed |
| 10. Adversarial review | PASS WITH LIMITATIONS | Reviewed retry multiplication, idempotency, timeout conflicts, finite-sample canary interpretation, fault cleanup and mesh-specific feature gaps | No fake Istio YAML or fabricated Linkerd breaker equivalence; optional/unsupported behavior left unclaimed | Human must verify exact release schemas and run bounded tests |

## Appendix E — Human verification checklist and sign-off

- [ ] Confirm exact target path: `Stage 2E — Production DevOps & Platform Engineering/04-Kubernetes-Networking-Ingress-and-Service-Mesh/08-mtls-traffic-shifting-retries-and-circuit-breaking.md`.
- [ ] Confirm master M04 syllabus and prompt pack coverage and exact section sequence.
- [ ] Confirm Unit 7 and capstone use Linkerd sidecar mode; reconcile all three if a source-backed decision changes.
- [ ] Verify current Linkerd/Kubernetes/CLI/control-plane/proxy compatibility.
- [ ] Verify Gateway API CRD version, route attachment and `HTTPRoute` weight/timeouts/retry support.
- [ ] Verify current policy CRD API versions/fields and inbound policy semantics.
- [ ] Run authorized meshed positive test, unauthorized meshed negative test, and unmeshed/plaintext negative test.
- [ ] Verify identity separately from packet encryption; redact packet captures and do not retain keys/secrets.
- [ ] Verify probes, metrics scrapers, Jobs/CronJobs and admin clients are intentionally handled.
- [ ] Execute 90/10 and 50/50 tests with at least 1,000 local requests each; record actual counts/errors/deviations.
- [ ] Verify retry ownership, attempt count, idempotency, deadline and timeout ladder.
- [ ] Execute only bounded local fault and failure-accrual experiments; record stop condition and recovery.
- [ ] Verify NetworkPolicy interaction and post-test health.
- [ ] Remove fault/route/test resources, stop port-forwards and verify cleanup.
- [ ] Confirm no public endpoint, real secret, sensitive payload, or unrelated repository edit was created.
- [ ] Leave measured tables blank until real evidence is collected; do not prefill successful sign-off.

**Reviewer:** ______________________________  
**Date:** ______________________________  
**Environment / OS / WSL2 details:** ______________________________  
**Kubernetes / Linkerd / Gateway API versions:** ______________________________  
**Result:** ______________________________  
**Outstanding verification items:** ______________________________  
**Human review completed:** Yes / No

**Content status:** `DRAFT-AUDITED`  
**Hands-on mesh:** Linkerd sidecar mode `[ASSUMPTION inherited from Unit 7; confirm with capstone before execution]`  
**Runtime status:** Reasoned review only; commands and labs were not executed in this environment.
