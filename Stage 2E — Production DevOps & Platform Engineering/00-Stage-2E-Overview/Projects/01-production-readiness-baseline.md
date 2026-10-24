# Project 01 — Production Readiness Baseline

> Audit an inherited prototype, prove which risks are real, harden it, and leave behind evidence another engineer can verify.

| Field | Value |
|---|---|
| Difficulty | Beginner-to-intermediate; intended as the first hands-on project in Stage 2E |
| Estimated time | 10–16 focused hours; allow extra time for cluster troubleshooting |
| Prerequisites | Complete the Gate In skills listed in [prerequisites and exit criteria](../prerequisites-and-exit-criteria.md) |
| Environment | Local kind cluster only; WSL2/Linux; zero-cost |
| Skills practised | Container build/run, Kubernetes inspection, production-readiness review, probes, resource controls, security context, rollouts, basic operability |
| Last reviewed | 2026-10-24 |

## 1. Why this project exists

A small service begins as a prototype and becomes business-critical before anyone notices.
It answers requests during a demo, so the team assumes it is ready for production.
Then a pod restarts during a deployment and users see errors.
A memory spike causes repeated restarts; nobody knows whether the service is unhealthy or merely slow.
The image runs as root, configuration is baked into the container, and a secret appears in a manifest.
There is no reliable rollback procedure, no runbook, and no agreed measure of acceptable availability.
The on-call engineer has to discover these gaps while the service is already failing.
A production-readiness review (PRR) makes risks visible before launch, assigns evidence and owners, and records explicit go/no-go decisions.
In this project, you inherit that service, audit it without changing it, reproduce selected failure modes, fix the highest-risk issues, and prove the result.

The purpose is not to make a toy service “enterprise-grade.” It is to practise a repeatable review method: **inspect → record → hypothesize → test safely → fix → verify → document**.

## 2. Learning objectives

By the end, you will be able to:

1. **Inspect** a container image and Kubernetes workload using `docker` and `kubectl`.
2. **Record** 20 or more production-readiness findings with severity and reproducible evidence.
3. **Demonstrate** how replica count, probes, resource limits, and termination behaviour affect availability.
4. **Harden** a small service using Kubernetes probes, resource controls, non-root execution, read-only root filesystem, and controlled rollouts.
5. **Expose** health and basic RED metrics without deploying a full monitoring stack.
6. **Verify** a rollback and a configuration restore using recorded commands and outcomes.
7. **Write** a concise runbook and draft SLI/SLO that another engineer can follow.
8. **Explain** which local simulations are useful and which production properties remain unproven.

## 3. Scenario and rules of engagement

You are the new on-call owner of `lab-readiness-api`, a service inherited from a prototype. It currently returns a greeting and has a diagnostic path that can be slow or fail on demand. The baseline is deliberately under-engineered but should still answer ordinary requests.

### Constraints

- Use a local kind cluster. Do not point any destructive command at a shared, staging, or production cluster.
- Use the dedicated namespace `lab-readiness`; do not use the `default` namespace.
- Keep the work zero-cost. No cloud account, paid service, hosted registry, or paid monitoring product is required.
- Do not add a service mesh, GitOps controller, Terraform, Helm, or a full observability stack in this project.
- Do not commit real credentials, kubeconfigs, tokens, or private registry credentials.
- Keep a written hypothesis before every break test. If the observed behaviour differs from the prediction, record the difference instead of editing the evidence.
- Save terminal output, relevant YAML, timestamps, and a short interpretation. A command alone is not proof that the expected behaviour occurred.
- Use only a cluster context you created for this lab. Before any destructive action, run `kubectl config current-context` and confirm it is the expected kind context.
- The time-box is 10–16 focused hours. If a test is blocked by a missing local capability, record it as **Not demonstrated** and use the closest safe simulation; do not silently claim success.

### Workflow

1. **Audit first:** inspect the provided baseline and complete the audit table before changing anything.
2. **Prove:** run only the selected controlled experiments, with a hypothesis and cleanup.
3. **Fix:** make the smallest changes that address the recorded risks.
4. **Prove again:** repeat the same checks and compare before/after evidence.
5. **Operationalize:** write the runbook, SLI/SLO draft, restore note, rollback drill, and retrospective.

### Lab fidelity limits

A kind cluster is a local test environment, not a production environment.

- A worker container being stopped or drained is a **simulation** of node maintenance/failure; it does not reproduce physical host, cloud control-plane, or multi-zone failure.
- Two replicas on one laptop do not prove independent failure domains or high availability.
- A local volume does not prove durable backups, cross-region recovery, or storage-provider behaviour.
- NetworkPolicy enforcement depends on the cluster network implementation. The default kind networking setup may not enforce policies as expected; treat enforcement as **[VERIFY]** and record the CNI used.
- `kubectl top` requires metrics support and may not be available. Treat it as **[VERIFY]**; do not install a paid service to make it work.
- OOM behaviour, drain behaviour, termination timing, and scheduling outcomes can vary by runtime and cluster setup. Record observed results.

For environment setup and kind image-loading guidance, use [lab environment setup](../lab-environment-setup.md) and [local kind/minikube/LocalStack lab](../local-lab-kind-minikube-and-localstack.md). The cloud account guide is not needed for this project.

## 4. Project layout

Create a working folder in your roadmap repository. The paths below are the project layout you create; they are not claims that these files already exist.

```text
01-production-readiness-baseline/
├── service/
│   ├── app.py
│   └── Dockerfile
├── k8s/
│   ├── baseline/
│   │   ├── namespace.yaml
│   │   ├── config.yaml
│   │   └── deployment.yaml
│   └── fixed/
│       ├── namespace.yaml
│       ├── config.yaml
│       ├── secret.example.yaml
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── pdb.yaml
│       └── networkpolicy.yaml
├── docs/
│   ├── audit.md
│   ├── before-after.md
│   ├── runbook.md
│   ├── slo-draft.md
│   ├── backup-restore.md
│   ├── rollback-drill.md
│   └── retrospective.md
├── evidence/
│   ├── environment.txt
│   ├── baseline/
│   ├── break-tests/
│   └── fixed/
└── .gitignore
```

- `service/` contains the minimal Python service and container build instructions.
- `k8s/baseline/` contains the initial deployment and its deliberately weak configuration.
- `k8s/fixed/` contains your hardened version. Keep it separate so you can compare.
- `docs/` contains the audit and operability artefacts.
- `evidence/` contains command output and notes. Never store real secrets or kubeconfigs here.
- `.gitignore` excludes generated local artefacts and sensitive files.

Save the current context and tool versions to `evidence/environment.txt` before you start. Do not include environment variables that may contain credentials.

## 5. The sample service (provided)

This project uses Python's standard library to keep the service dependency-light and easy to inspect. The service deliberately keeps the baseline behaviour simple; the fixed version adds signal handling and safer runtime behaviour. Both versions use the same source file, but the source has a `SERVICE_MODE` switch so you can compare the inherited baseline with the hardened behaviour without maintaining two unrelated implementations.

### 5.1 `service/app.py`

```python
#!/usr/bin/env python3
"""Tiny readiness lab service; standard library only."""

import json
import os
import signal
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8080"))
SERVICE_MODE = os.environ.get("SERVICE_MODE", "baseline")
SERVICE_NAME = os.environ.get("SERVICE_NAME", "lab-readiness-api")
STARTED_AT = time.time()

_lock = threading.Lock()
_metrics = {
    "requests_total": 0,
    "request_errors_total": 0,
    "request_duration_seconds_sum": 0.0,
    "request_duration_seconds_count": 0,
}
_stopping = threading.Event()


def log_event(level, message, **fields):
    """Write one JSON object per line to stdout; baseline can opt out."""
    if SERVICE_MODE == "baseline":
        print(f"{level}: {message}", flush=True)
        return
    event = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "level": level,
        "service": SERVICE_NAME,
        "message": message,
    }
    event.update(fields)
    print(json.dumps(event, separators=(",", ":"), sort_keys=True), flush=True)


class Handler(BaseHTTPRequestHandler):
    server_version = "ReadinessLab/1.0"

    def log_message(self, fmt, *args):
        # Avoid default request logs with unstructured formatting.
        log_event("info", "http_access", client=self.client_address[0],
                  detail=fmt % args)

    def _send(self, status, body, content_type="application/json; charset=utf-8"):
        payload = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Connection", "close" if _stopping.is_set() else "keep-alive")
        self.end_headers()
        try:
            self.wfile.write(payload)
        except (BrokenPipeError, ConnectionResetError):
            # The client may have disconnected during a controlled shutdown test.
            pass

    def do_GET(self):
        started = time.monotonic()
        status = 200
        path = urlparse(self.path).path
        try:
            if _stopping.is_set():
                status = 503
                self._send(status, json.dumps({"error": "shutting_down"}))
                return

            if path == "/":
                self._send(200, json.dumps({
                    "service": SERVICE_NAME,
                    "message": "hello",
                    "mode": SERVICE_MODE,
                }))
            elif path in ("/healthz", "/readyz"):
                self._send(200, json.dumps({"status": "ok"}))
            elif path == "/slow":
                # Controlled delay for timeout and termination experiments.
                delay = min(max(float(os.environ.get("SLOW_SECONDS", "3")), 0), 15)
                time.sleep(delay)
                self._send(200, json.dumps({"status": "completed", "delay_seconds": delay}))
            elif path == "/fail":
                status = 500
                self._send(status, json.dumps({"error": "deliberate_failure"}))
            elif path == "/metrics":
                self._send(200, self._render_metrics(), "text/plain; version=0.0.4; charset=utf-8")
            else:
                status = 404
                self._send(status, json.dumps({"error": "not_found"}))
        except (ValueError, OSError) as exc:
            status = 500
            log_event("error", "request_failed", path=path, error_type=type(exc).__name__)
            try:
                self._send(status, json.dumps({"error": "internal_error"}))
            except OSError:
                pass
        finally:
            elapsed = time.monotonic() - started
            with _lock:
                _metrics["requests_total"] += 1
                if status >= 500:
                    _metrics["request_errors_total"] += 1
                _metrics["request_duration_seconds_sum"] += elapsed
                _metrics["request_duration_seconds_count"] += 1

    def _render_metrics(self):
        with _lock:
            m = dict(_metrics)
        # The names and types follow Prometheus text exposition conventions.
        return (
            "# HELP readiness_requests_total Total HTTP requests handled.\n"
            "# TYPE readiness_requests_total counter\n"
            f"readiness_requests_total {m['requests_total']}\n"
            "# HELP readiness_request_errors_total HTTP requests returning 5xx.\n"
            "# TYPE readiness_request_errors_total counter\n"
            f"readiness_request_errors_total {m['request_errors_total']}\n"
            "# HELP readiness_request_duration_seconds Request duration sum in seconds.\n"
            "# TYPE readiness_request_duration_seconds summary\n"
            f"readiness_request_duration_seconds_sum {m['request_duration_seconds_sum']:.6f}\n"
            f"readiness_request_duration_seconds_count {m['request_duration_seconds_count']}\n"
        )


class LabHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def handle_sigterm(signum, frame):
    """Fixed mode marks unready, stops accepting work, and exits cleanly."""
    if SERVICE_MODE == "fixed":
        _stopping.set()
        log_event("info", "shutdown_started", signal=signum)
        threading.Thread(target=httpd.shutdown, daemon=True).start()
    else:
        # The baseline intentionally does not initiate orderly shutdown.
        log_event("warning", "signal_received_without_graceful_shutdown", signal=signum)


httpd = LabHTTPServer((HOST, PORT), Handler)
signal.signal(signal.SIGTERM, handle_sigterm)
signal.signal(signal.SIGINT, handle_sigterm)

if __name__ == "__main__":
    log_event("info", "service_starting", port=PORT, mode=SERVICE_MODE)
    try:
        httpd.serve_forever(poll_interval=0.2)
    finally:
        httpd.server_close()
        log_event("info", "service_stopped")
        sys.exit(0)
```

**Implementation note:** the Python standard-library HTTP server is suitable for this small learning exercise, not a recommendation for a high-throughput public production service. The request handler records basic counters and duration sum/count. This is enough for a `/metrics` smoke test, not a complete histogram-based latency distribution. A later observability module can replace this with an official client library and a real scrape pipeline.

### 5.2 Endpoint contract

| Endpoint | Normal result | Why it exists |
|---|---|---|
| `GET /` | `200` JSON greeting | Main application path |
| `GET /healthz` | `200` JSON status | Liveness probe target: process can answer HTTP |
| `GET /readyz` | `200` JSON status; `503` after fixed-mode shutdown begins | Readiness probe target: instance should receive traffic |
| `GET /slow` | Waits for `SLOW_SECONDS`, then `200` | Controlled request for timeout and termination experiments |
| `GET /fail` | `500` JSON error | Demonstrates error-rate observation |
| `GET /metrics` | Prometheus text exposition | Lightweight metric verification without a monitoring stack |
| Other paths | `404` JSON | Confirms unknown paths do not look successful |

The baseline intentionally logs in a plain text format and does not start graceful shutdown. The fixed mode emits JSON logs and reacts to `SIGTERM`. The service does not store durable business data; the restore exercise therefore covers configuration and manifests, not a database restore.

### 5.3 Run locally

Run these commands from the repository's project directory. They assume Python 3 is installed.

```bash
python3 --version
```

- **Does:** checks the interpreter.
- **Expected:** prints a Python 3 version. Record the exact version in `evidence/environment.txt`; do not assume a particular patch release.

```bash
SERVICE_MODE=baseline PORT=8080 python3 service/app.py
```

- **Does:** starts the baseline service in the foreground.
- **Expected:** a startup log appears and the process remains running. Keep this terminal open.

In a second terminal:

```bash
curl -i http://127.0.0.1:8080/
curl -i http://127.0.0.1:8080/healthz
curl -i http://127.0.0.1:8080/readyz
curl -i http://127.0.0.1:8080/fail
curl -i http://127.0.0.1:8080/metrics
```

- **Does:** exercises the main, health, readiness, failure, and metrics paths.
- **Expected:** the first three return `200`, `/fail` returns `500`, and `/metrics` returns `200` with `# HELP` and `# TYPE` lines.
- **Evidence:** save output to `evidence/local-smoke.txt`. Do not include secrets.

Stop the local process with `Ctrl+C`. If it does not exit, use `Ctrl+C` again and record the result. The graceful-shutdown experiment is primarily performed in the cluster, where Kubernetes sends `SIGTERM`.

### 5.4 Metrics and logging limitations

The metric endpoint uses valid Prometheus text-format conventions for counters and a summary sum/count. It does not provide quantiles or histogram buckets, and the service does not label metrics by path to avoid unbounded label cardinality. The fixed service logs to stdout as JSON. Do not put request bodies, authorization headers, credentials, or environment dumps in logs.

## 6. The baseline deployment (provided)

The baseline is intentionally weak but should work for ordinary requests. The service source is the same file above. The baseline sets `SERVICE_MODE=baseline`.

### 6.1 Choose and record a base image

The Dockerfile uses a placeholder for the Python base-image tag. Before building, replace `<PYTHON_BASE_IMAGE_TAG>` with a currently supported tag chosen from the official Python image documentation. Record the selected tag and the date you checked it in `evidence/environment.txt`. Do not treat this brief as a source of current version advice.

For the baseline, use the same selected base image but retain the other weaknesses so the audit has evidence to find.

### 6.2 `service/Dockerfile`

```dockerfile
# Replace <PYTHON_BASE_IMAGE_TAG> with a currently supported tag.
FROM python:<PYTHON_BASE_IMAGE_TAG>

WORKDIR /app
COPY app.py /app/app.py

# Baseline intentionally runs as the image's default user.
# No USER directive, read-only root filesystem, or healthcheck is configured.
ENV PORT=8080
EXPOSE 8080

CMD ["python", "/app/app.py"]
```

### 6.3 `k8s/baseline/namespace.yaml`

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: lab-readiness
  labels:
    app.kubernetes.io/part-of: production-readiness-baseline
```

### 6.4 `k8s/baseline/config.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: lab-readiness-config
  namespace: lab-readiness
data:
  SERVICE_NAME: "lab-readiness-api"
  SERVICE_MODE: "baseline"
  SLOW_SECONDS: "3"
```

### 6.5 `k8s/baseline/deployment.yaml`

Replace `<LOCAL_IMAGE_TAG>` with the exact local tag you build. The `latest` tag is deliberately used as the image reference in the baseline to make mutability visible; for reproducible testing, build it locally with that tag and record the image ID. Do not use this pattern in a real deployment.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lab-readiness-api
  namespace: lab-readiness
  labels:
    app.kubernetes.io/name: lab-readiness-api
spec:
  replicas: 1
  selector:
    matchLabels:
      app: lab-readiness-api
  template:
    metadata:
      labels:
        app: lab-readiness-api
    spec:
      containers:
        - name: api
          image: lab-readiness-api:latest
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 8080
          envFrom:
            - configMapRef:
                name: lab-readiness-config
          env:
            - name: DEMO_TOKEN
              value: "not-a-real-secret-demo-value"
```

`DEMO_TOKEN` is a fake sentinel value, not a credential. It is included only to demonstrate how a sensitive-looking value can be exposed in workload YAML. Never substitute a real token. The baseline has no Service object; use `kubectl port-forward` for local testing.

### 6.6 Build and load the image into kind

Use the method already documented in [local kind/minikube/LocalStack lab](../local-lab-kind-minikube-and-localstack.md). The commands below show the typical kind workflow; confirm the cluster name and current context before running them.

```bash
kubectl config current-context
kind get clusters
docker build -t lab-readiness-api:latest service/
kind load docker-image lab-readiness-api:latest --name <YOUR_KIND_CLUSTER_NAME>
```

- **Does:** checks the context, lists kind clusters, builds the image, and loads it into the selected local cluster.
- **Expected:** the context is the kind context you created for this lab, the cluster appears in the list, the image build succeeds, and kind reports that it loaded the image.
- Replace `<YOUR_KIND_CLUSTER_NAME>` with the actual local cluster name. Do not type angle-bracket placeholders literally.

### 6.7 Deploy the baseline

```bash
kubectl apply -f k8s/baseline/namespace.yaml
kubectl apply -f k8s/baseline/config.yaml
kubectl apply -f k8s/baseline/deployment.yaml
kubectl -n lab-readiness rollout status deployment/lab-readiness-api --timeout=120s
kubectl -n lab-readiness get pods -o wide
```

- **Does:** creates the dedicated namespace, config, and deployment; waits for rollout; and lists pods.
- **Expected:** one pod reaches `Running`. Since no readiness probe exists, `Running` does not mean the application has passed a meaningful readiness check.

Forward the pod port:

```bash
kubectl -n lab-readiness port-forward deployment/lab-readiness-api 18080:8080
```

In another terminal:

```bash
curl -i http://127.0.0.1:18080/
curl -i http://127.0.0.1:18080/healthz
curl -i http://127.0.0.1:18080/metrics
```

- **Does:** forwards local port `18080` to the pod's `8080` port and checks the service.
- **Expected:** main and health paths return `200`; metrics returns Prometheus text. Stop port-forward with `Ctrl+C`.

**It works. That is the trap.** A successful smoke test establishes only that a narrow happy path worked at that moment. It does not prove safe scheduling, controlled termination, availability during a rollout, recovery, observability, or security.

## 7. The production-readiness checklist (the audit instrument)

Use this checklist before editing any manifests. “Severity if missing” is a suggested default for a small stateless internal service; justify any different severity in your audit. `Blocker` means do not launch until addressed or explicitly accepted by the accountable owner. `Major` means a material reliability/security/operability risk. `Minor` means a meaningful improvement that is not normally a launch blocker by itself.

| # | Area | Question to ask | Why it matters in production | Evidence to collect | Severity if missing | Deepened in |
|---:|---|---|---|---|---|---|
| 1 | Image hygiene | Is the image built from a supported base and an immutable, recorded image reference? | Mutable or unsupported images undermine reproducibility and patching. | Dockerfile, chosen tag/date, image ID or digest strategy | Major | M01 |
| 2 | Image provenance | Can the team identify how the image was built and what source it came from? | Traceability supports incident response and supply-chain review. | Build command, source revision, image ID | Major | M01, M12 |
| 3 | Runtime identity | Does the process run as a non-root user with an explicit security context? | Reduces the impact of application compromise. | `id` inside container; pod `securityContext` | Blocker | M01, M12 |
| 4 | Pod Security Standards | Does the pod align with the Restricted standard where feasible? | A consistent baseline prevents common privilege escalation paths. | Security context and namespace policy decision | Major | M03, M12 |
| 5 | Filesystem | Is the root filesystem read-only, with only required writable paths mounted? | Limits persistence and unexpected writes. | `readOnlyRootFilesystem`, volume mounts, write test | Major | M01, M12 |
| 6 | Startup probe | Is startup time protected from premature liveness restarts? | Slow-starting applications can otherwise restart before initialization completes. | Startup probe config and startup test | Major | M03 |
| 7 | Readiness probe | Does readiness indicate whether the instance should receive traffic? | An unready pod can serve failing requests if it remains in endpoints. | Readiness config and endpoint/traffic observation | Blocker | M03, M04 |
| 8 | Liveness probe | Does liveness detect a process that cannot recover, without checking every dependency? | Poor liveness checks can cause restart loops during downstream outages. | Liveness config and deliberate failure test | Major | M03 |
| 9 | Resources | Are CPU/memory requests and limits chosen from observed behaviour and a safety margin? | Requests affect scheduling and QoS; memory limits can cause OOM kills; CPU limits can throttle. | Resource YAML, observed usage if available, rationale | Major | M03, M15 |
| 10 | QoS | Is the resulting QoS class understood and appropriate? | QoS influences eviction behaviour under node pressure. | `kubectl get pod -o jsonpath=...` or `describe` | Major | M03 |
| 11 | Shutdown | Does the app handle SIGTERM, stop accepting new work, and exit within the grace period? | Abrupt termination can drop in-flight requests. | Signal test, logs, termination settings | Blocker | M03, M10 |
| 12 | Replicas | Are replica count and placement aligned with the required availability? | A single replica has no pod-level redundancy. | Deployment replicas and pod placement | Blocker | M03, M04 |
| 13 | Rollout strategy | Are `maxUnavailable` and `maxSurge` explicit and sensible for the workload? | Poor rollout settings can cause avoidable capacity loss or stalled updates. | Deployment strategy and rollout status | Major | M03 |
| 14 | Disruption budget | Is a PDB defined for voluntary disruptions where needed? | Helps prevent maintenance from evicting too many available replicas at once. | PDB YAML and drain simulation | Major | M03 |
| 15 | Configuration | Is environment-specific config external to the image and reviewed for safe changes? | Rebuilding images for every config change slows recovery and encourages drift. | ConfigMap, env references, image contents | Major | M05 |
| 16 | Secrets | Are credentials kept out of source, image layers, logs, and plain ConfigMaps? Is the storage/access model understood? | Exposed credentials can enable unauthorized access. Base64 encoding is not encryption. | Secret references and repo scan; no real secret values | Blocker | M09, M12 |
| 17 | Logging | Are logs structured, sent to stdout/stderr, and free of secrets? | Structured logs make failures searchable without leaking sensitive data. | Captured stdout and sample JSON parse | Major | M11, M12 |
| 18 | Metrics | Are request rate, errors, and latency represented with a lightweight RED view? | Metrics help distinguish load, failures, and slowness. | `curl /metrics`; names and types | Major | M11 |
| 19 | SLI/SLO | Is there a measurable service-level indicator, target, window, and alert idea? | Teams need an explicit definition of acceptable service behaviour. | `docs/slo-draft.md` and measurement procedure | Major | M10, M11 |
| 20 | Dependency/failure handling | Are timeouts bounded and retry behaviour safe and limited? | Unbounded waits and retries can amplify outages. | Code/config review and `/slow` test | Major | M04, M10 |
| 21 | State and backup | Is state identified, and is backup/restore tested where state exists? | A backup that has never been restored is unproven. | State inventory and restore drill record | Major | M13 |
| 22 | Rollback | Is a previous known-good revision available and is rollback rehearsed? | Rollback limits the duration of a bad release. | `rollout history`, rollback command and result | Blocker | M02, M03 |
| 23 | Runbook | Can an unfamiliar on-call engineer triage common symptoms? | Response quality should not depend on undocumented memory. | `docs/runbook.md` with symptom/check/action | Major | M10, M16 |
| 24 | Ownership/on-call | Is a responsible team/person and escalation route documented? | Alerts without ownership are likely to be ignored or delayed. | Runbook ownership and escalation fields | Major | M10, M16 |
| 25 | Capacity/cost | Are requests justified and is the local resource footprint understood? | Over-requesting wastes capacity; under-requesting causes contention and instability. | Resource rationale and local footprint notes | Minor | M15 |
| 26 | Network boundaries | Is ingress/egress access intentionally limited where the cluster supports it? | Least-privilege networking can reduce lateral movement. | NetworkPolicy and CNI enforcement evidence | Major | M04, M12 |
| 27 | Documentation | Are build, deploy, verify, rollback, and cleanup steps reproducible? | Documentation reduces operational toil and mistakes. | README/runbook and command evidence | Major | M16 |
| 28 | Change evidence | Are fixes linked to the findings they resolve and are before/after results retained? | Reviewers need traceability from risk to remediation. | Audit table, diff, acceptance criteria, evidence folder | Major | M02, M16 |

### Severity guidance

- **Blocker:** a credible route to data exposure, privilege escalation, unbounded outage, or no practical recovery.
- **Major:** a material risk with a plausible mitigation and documented acceptance path.
- **Minor:** an improvement with limited direct launch impact in this small exercise.
- Severity depends on context. A public unauthenticated endpoint, regulated data, or a critical dependency could change the rating substantially.
- This checklist is a learning instrument, not a substitute for the organisation's security policy or formal launch approval.

## 8. Phase 1 — Audit (no changes yet)

**Rule: do not fix anything until the audit table is complete.** You may copy files into `k8s/fixed/`, but do not modify the running baseline or overwrite your original evidence.

### Step 1 — Confirm the lab context

```bash
kubectl config current-context
kind get clusters
kubectl get nodes -o wide
```

- **Does:** identifies the selected context, available kind clusters, and nodes.
- **Expected:** the current context is the lab kind context and the nodes belong to the local cluster you created.
- **If not:** stop. Do not run deployment or destructive commands until the context is correct.

Save the output to `evidence/environment.txt`. Remove any unrelated sensitive data before committing it.

### Step 2 — Capture the baseline inventory

```bash
kubectl -n lab-readiness get all
kubectl -n lab-readiness get deployment lab-readiness-api -o yaml
kubectl -n lab-readiness describe deployment lab-readiness-api
kubectl -n lab-readiness get pods -o wide
kubectl -n lab-readiness describe pod -l app=lab-readiness-api
```

- **Does:** captures declared configuration and the controller's current observations.
- **Expected:** one Deployment and one pod are present; note that a missing Service, probes, resource settings, or rollout configuration may be visible.
- **Evidence:** save the outputs under `evidence/baseline/`. YAML can contain sensitive values; this project uses a fake sentinel only, but inspect before committing.

### Step 3 — Inspect the image

```bash
docker image inspect lab-readiness-api:latest
docker history lab-readiness-api:latest
```

- **Does:** shows image metadata and build layers.
- **Expected:** the image exists locally. Record the image ID and inspect whether the Dockerfile establishes a non-root user or health check.
- **Evidence:** save selected non-sensitive output to `evidence/baseline/image-inspect.txt`.

### Step 4 — Check runtime identity and writable paths

```bash
POD="$(kubectl -n lab-readiness get pod -l app=lab-readiness-api -o jsonpath='{.items[0].metadata.name}')"
kubectl -n lab-readiness exec "$POD" -- id
kubectl -n lab-readiness exec "$POD" -- sh -c 'test -w /app && echo "/app writable" || echo "/app not writable"'
```

- **Does:** checks the process identity and whether `/app` is writable.
- **Expected:** record the actual user/group and write result. Do not assume all base images include a shell; if the command fails because the shell is absent, record that and use image metadata or a temporary diagnostic container in the lab.
- **Evidence:** `evidence/baseline/runtime-identity.txt`.

### Step 5 — Inspect probes, resources, security context, and rollout settings

```bash
kubectl -n lab-readiness get deployment lab-readiness-api -o jsonpath='{.spec.template.spec.containers[0].readinessProbe}{"\n"}{.spec.template.spec.containers[0].livenessProbe}{"\n"}{.spec.template.spec.containers[0].resources}{"\n"}{.spec.template.spec.securityContext}{"\n"}{.spec.strategy}{"\n"}'
kubectl -n lab-readiness get pods -o jsonpath='{range .items[*]}{.metadata.name}{" qos="}{.status.qosClass}{"\n"}{end}'
```

- **Does:** prints selected configuration fields and the pod QoS class.
- **Expected:** missing fields appear empty; record the result rather than treating empty output as a command error.
- **Evidence:** `evidence/baseline/workload-fields.txt`.

### Step 6 — Inspect configuration exposure

```bash
kubectl -n lab-readiness get configmap lab-readiness-config -o yaml
kubectl -n lab-readiness get deployment lab-readiness-api -o yaml
```

- **Does:** shows configuration and environment declarations.
- **Expected:** the fake `DEMO_TOKEN` sentinel is visible in the Deployment. This is not a real credential; do not replace it with one.
- **Evidence:** record the fact and the file/field where it appears. Avoid copying real environment values into audit evidence.

### Step 7 — Check application behaviour and logs

In one terminal:

```bash
kubectl -n lab-readiness port-forward deployment/lab-readiness-api 18080:8080
```

In another:

```bash
curl -sS -i http://127.0.0.1:18080/
curl -sS -i http://127.0.0.1:18080/healthz
curl -sS -i http://127.0.0.1:18080/readyz
curl -sS -i http://127.0.0.1:18080/fail
curl -sS -i http://127.0.0.1:18080/metrics
kubectl -n lab-readiness logs deployment/lab-readiness-api --tail=30
```

- **Does:** verifies response codes, metrics exposition, and log format.
- **Expected:** main/health/readiness return `200`, `/fail` returns `500`, `/metrics` contains `# HELP` and `# TYPE`, and baseline logs are not JSON.
- **Evidence:** `evidence/baseline/smoke-and-logs.txt`.

### Step 8 — Check resource observation availability

```bash
kubectl top pods -n lab-readiness
kubectl top nodes
```

- **Does:** requests resource usage from the Metrics API.
- **Expected:** if metrics support is installed and ready, usage is returned. If the command reports that Metrics API is unavailable, record **Not available [VERIFY]**. Do not infer that usage is zero.

### Step 9 — Complete the audit table

Create `docs/audit.md` using this template. Use one row per finding; refer to the checklist row number. The audit is complete only when every checklist row has a finding, evidence pointer, severity, and a next action or justified “not applicable.”

```markdown
# Production-readiness audit

- Date:
- Cluster/context:
- Image ID:
- Reviewer:
- Scope: local lab only

| Checklist # | Finding | Severity | Evidence path/command | Risk if unchanged | Proposed action | Status |
|---:|---|---|---|---|---|---|
| 1 | | | | | | Open |
| 2 | | | | | | Open |
| ... | | | | | | |
```

Do not write “secure,” “highly available,” or “production-ready” without a bounded claim and evidence. “Two replicas scheduled on this laptop” is a factual observation; “survives a zone failure” is not.

### Verify

- `kubectl config current-context` identifies the intended local kind context.
- The baseline still answers `/` and `/healthz`.
- `docs/audit.md` has a row for every checklist item and evidence for each material finding.
- No fixes have been applied to the baseline.

**Checkpoint:** save the inventory, deployment YAML, image metadata, runtime identity, smoke-test output, and completed `docs/audit.md` under `evidence/baseline/` and `docs/`.

## 9. Phase 2 — Prove the weaknesses (break tests)

Run each test only in the lab namespace and cluster. Before every test:

1. Write the hypothesis and expected observation in `docs/before-after.md`.
2. Run `kubectl config current-context`; confirm the lab context.
3. Confirm the namespace and deployment names.
4. Save the starting state.
5. Run the test, then perform the cleanup exactly as written.
6. If the expected behaviour is not observed, record what happened and why it may differ. Do not force a result by targeting a different cluster.

Create `docs/before-after.md` from the comparison template in Phase 4, adding one row per experiment.

### Test A — Kill the only pod during traffic

**Hypothesis:** with one replica and no readiness probe, deleting the pod during repeated requests creates a period in which requests fail or cannot connect while the replacement starts.

**Procedure:**

```bash
kubectl config current-context
kubectl -n lab-readiness get deployment,pods
```

- **Does:** verifies context and starting state.
- **Expected:** one pod is serving the baseline.

Start a request loop in a terminal:

```bash
while true; do
  date -u +%FT%TZ
  curl --max-time 2 -sS -o /dev/null -w 'http=%{http_code} connect=%{time_connect} total=%{time_total}\n' http://127.0.0.1:18080/ || echo "request_failed"
  sleep 0.2
done
```

- **Does:** sends repeated requests through the port-forward.
- **Expected:** successful requests before disruption; record any failed requests and timestamps. Keep the port-forward terminal open.

In a second terminal, confirm the context again and delete the current pod:

```bash
kubectl config current-context
POD="$(kubectl -n lab-readiness get pod -l app=lab-readiness-api -o jsonpath='{.items[0].metadata.name}')"
kubectl -n lab-readiness delete pod "$POD"
kubectl -n lab-readiness get pods -w
```

- **Does:** deletes only the lab pod and watches its replacement.
- **Expected:** a replacement is created. Request failures may be visible while the pod is absent or the port-forward reconnects. Port-forward behaviour itself can affect the observed gap; label this a local simulation, not a precise production outage measurement.

**Cleanup:** stop the request loop with `Ctrl+C`; wait for a new pod; verify `/healthz` and `/` again. If the port-forward exits, restart it and record that event.

**Verify:** `kubectl -n lab-readiness rollout status deployment/lab-readiness-api --timeout=120s` succeeds and the smoke test returns `200`.

**Checkpoint:** save the request-loop output, pod watch, start/end timestamps, and your interpretation in `evidence/break-tests/test-a-single-replica.txt`.

### Test B — SIGTERM and in-flight requests

**Hypothesis:** baseline mode does not initiate an orderly server shutdown on SIGTERM; a slow request may be interrupted when Kubernetes terminates the pod. The exact outcome depends on request timing, port-forward, runtime, and grace period, so the dropped-request observation is **[VERIFY]**.

**Procedure:**

```bash
kubectl config current-context
kubectl -n lab-readiness get pods -l app=lab-readiness-api
kubectl -n lab-readiness logs deployment/lab-readiness-api --tail=50
```

- **Does:** confirms context and baseline state.
- **Expected:** one pod and baseline-mode logs.

Start a slow request in one terminal:

```bash
curl --max-time 10 -i http://127.0.0.1:18080/slow
```

- **Does:** holds a request open for the configured delay.
- **Expected:** it normally completes after the delay if the pod remains alive.

While the request is running, in a second terminal:

```bash
kubectl config current-context
POD="$(kubectl -n lab-readiness get pod -l app=lab-readiness-api -o jsonpath='{.items[0].metadata.name}')"
kubectl -n lab-readiness delete pod "$POD" --grace-period=1
```

- **Does:** requests a short graceful period for the lab pod to make termination effects easier to observe.
- **Expected:** the pod terminates and is replaced. Whether the request is dropped is **[VERIFY]**; save the actual `curl` outcome and timestamps.

**Cleanup:** wait for the replacement pod, re-check `/healthz`, and restore the standard deployment if you changed any parameters.

**Verify:** deployment has one available replica and the endpoint responds again.

**Checkpoint:** save the slow request output, pod events, and logs as `evidence/break-tests/test-b-sigterm.txt`. Do not claim that a dropped request is guaranteed by every runtime.

### Test C — Memory limit and OOM behaviour

**Hypothesis:** a process that exceeds its container memory limit may be killed and reported as `OOMKilled`; precise behaviour depends on runtime, kernel accounting, and whether the process exceeds the configured cgroup limit. This test is **[VERIFY]** and must use a temporary lab-only Deployment, not the baseline used for the other tests.

The provided app has no memory-hungry endpoint. Do not add an unbounded memory allocation to the main service. Instead, use a short-lived diagnostic pod only if you understand its impact and your local machine has adequate headroom. If you are not confident, skip the destructive experiment and document the safe limitation.

**Procedure (optional; lab only):**

```bash
kubectl config current-context
kubectl -n lab-readiness get pods
```

- **Does:** confirms the context and starting state.
- **Expected:** lab context and baseline workload.

Create a separate diagnostic manifest named `evidence/break-tests/oom-probe.yaml` with a unique name, a deliberately small memory limit, and a bounded process that allocates memory only up to a documented cap. Do not copy an unbounded stress command from the internet. Apply it only after reviewing the manifest. Observe:

```bash
kubectl -n lab-readiness get pod lab-oom-probe -w
kubectl -n lab-readiness describe pod lab-oom-probe
```

- **Does:** watches the diagnostic pod and inspects its termination reason.
- **Expected:** if the allocation exceeds the effective limit, `OOMKilled` may appear. If it does not, record that the experiment did not demonstrate an OOM kill; do not lower the host's safety margin just to force one.

**Cleanup:**

```bash
kubectl -n lab-readiness delete pod lab-oom-probe --ignore-not-found
```

- **Does:** removes the optional diagnostic pod.
- **Expected:** no `lab-oom-probe` remains.

**Verify:** `kubectl -n lab-readiness get pod lab-oom-probe` reports not found, or no matching pod is listed.

**Checkpoint:** save the diagnostic manifest, `describe` output, and explicit result (`Observed OOMKilled`, `Different result`, or `Skipped safely`) in `evidence/break-tests/test-c-memory.txt`.

### Test D — Bad readiness versus bad liveness

**Hypothesis:** a failing readiness probe marks a pod unready and removes it from normal Service endpoints; a failing liveness probe can restart the container. A bad liveness check can therefore create a restart loop, while a bad readiness check can leave a running pod unable to receive traffic. This test uses a temporary copy of the Deployment and must not leave the baseline broken.

**Procedure:**

1. Copy `k8s/baseline/deployment.yaml` to `evidence/break-tests/deployment-bad-readiness.yaml`.
2. In the copy only, add a readiness probe that requests a path that does not exist, such as `/not-a-health-endpoint`, on port `8080`.
3. Review the diff. Confirm namespace remains `lab-readiness` and selector labels still match.
4. Apply the temporary manifest and observe the pod's Ready status.
5. Save `kubectl -n lab-readiness describe pod ...` and the `kubectl get pods` output.
6. Restore the original Deployment immediately.
7. Repeat with a temporary bad liveness probe, using a low failure threshold only if you can observe and clean up safely.

Useful observations:

```bash
kubectl -n lab-readiness get pods -w
kubectl -n lab-readiness describe pod -l app=lab-readiness-api
kubectl -n lab-readiness get events --sort-by=.lastTimestamp
```

- **Does:** shows readiness, probe failures, restarts, and recent events.
- **Expected:** bad readiness should affect Ready status without necessarily restarting the process; bad liveness can lead to restarts after the configured threshold. Exact timing depends on probe settings and is **[VERIFY]**.

**Cleanup:** re-apply `k8s/baseline/deployment.yaml`; wait for rollout; remove temporary files only after preserving the evidence.

**Verify:** pod is Ready and restart count stops increasing after restoring the baseline.

**Checkpoint:** save both probe experiments and explain the difference in `evidence/break-tests/test-d-probes.txt`.

### Test E — Drain simulation with and without a PDB

**Hypothesis:** a PodDisruptionBudget can constrain voluntary evictions when replicas exist, but cannot guarantee availability during involuntary failures or compensate for insufficient replicas. Draining a kind node is a **simulation** and can be affected by cluster topology and node roles.

This test is optional if your local kind cluster has only one node or lacks sufficient capacity. Do not create a large cluster that risks exhausting your laptop.

**Procedure:**

1. Record the kind node count with `kubectl get nodes`.
2. If the cluster is multi-node, identify the worker node intended for the simulation. Do not assume every kind cluster has a worker node.
3. Deploy the fixed version with two replicas and a PDB only after Phase 3 is complete. A PDB test before there are multiple replicas is not informative.
4. Write the hypothesis, context, target node, and cleanup plan in `docs/before-after.md`.
5. Inspect `kubectl -n lab-readiness get pdb` and `kubectl -n lab-readiness describe pdb`.
6. Use `kubectl drain <WORKER_NODE_NAME> --ignore-daemonsets --delete-emptydir-data` only after verifying the target is a local kind worker and understanding that this evicts pods from that node. Do not drain the only node or the control-plane node for this exercise.
7. Observe evictions, PDB status, and remaining pod placement. Then uncordon the node.

**Expected observation:** when a PDB is active and a voluntary eviction would violate its budget, eviction may be blocked. With no PDB, the eviction constraint is absent. Results vary with pod placement, available replicas, and cluster configuration; tag as **[VERIFY]**.

**Cleanup:**

```bash
kubectl config current-context
kubectl uncordon <WORKER_NODE_NAME>
kubectl -n lab-readiness get pods -o wide
kubectl -n lab-readiness rollout status deployment/lab-readiness-api --timeout=120s
```

- **Does:** restores scheduling and verifies recovery.
- **Expected:** the node is schedulable and the workload becomes available again. Replace the placeholder only with the exact worker name observed in `kubectl get nodes`.

If you do not have a safe multi-node cluster, record **Skipped — topology/capacity limitation** and explain the test you would perform in a controlled cluster. Do not claim PDB behaviour was demonstrated.

**Verify:** all nodes intended for this simulation are schedulable and the Deployment reaches its expected availability.

**Checkpoint:** save the node list, PDB status, drain output, uncordon output, and limitations in `evidence/break-tests/test-e-drain-simulation.txt`.

### Test F — Demonstrate configuration exposure safely

**Hypothesis:** a value placed in a Deployment's plain environment declaration is visible to anyone with permission to read that workload. Kubernetes Secret objects improve separation and access control but do not automatically solve every secret-storage or authorization risk.

**Procedure:**

```bash
kubectl config current-context
kubectl -n lab-readiness get deployment lab-readiness-api -o yaml
```

- **Does:** displays the baseline Deployment declaration.
- **Expected:** the fake `DEMO_TOKEN` sentinel is visible under the container environment. No real token is present.

Do not run `env`, `printenv`, or `kubectl get secret -o yaml` against any environment containing real credentials. This lab's sentinel is deliberately fake.

**Cleanup:** no runtime change is needed. Phase 3 removes the inline environment value and uses a Secret reference example with no real credential.

**Verify:** the audit records where the value is declared and explains why base64 is encoding, not encryption.

**Checkpoint:** save a redacted excerpt and explanation in `evidence/break-tests/test-f-secret-exposure.txt`.

## 10. Phase 3 — Fix

Keep the original baseline manifests unchanged. Make changes under `k8s/fixed/` and document the finding numbers each change addresses.

### 10.1 Use an immutable image reference

A tag is not necessarily immutable. Prefer a digest when the build/publish process provides one, or enforce a registry policy that prevents tag mutation and record the exact image digest used. For a local kind exercise, the local image can be loaded by a unique, non-`latest` tag, but that tag alone is not a cryptographic guarantee of immutability.

Choose a supported Python base-image tag from the official image documentation at build time. Record the selected tag and check date. Do not commit unresolved placeholders.

Example build:

```bash
docker build -t lab-readiness-api:prr-01 service/
docker image inspect lab-readiness-api:prr-01 --format '{{.Id}}'
kind load docker-image lab-readiness-api:prr-01 --name <YOUR_KIND_CLUSTER_NAME>
```

- **Does:** builds a locally tagged image, records its image ID, and loads it into kind.
- **Expected:** a successful build and an image ID. Replace the cluster placeholder with the real local kind cluster name.
- **Evidence:** `evidence/fixed/image-build.txt`.

### 10.2 Fixed Dockerfile

Use this as the target Dockerfile. Replace `<PYTHON_BASE_IMAGE_TAG>` with the currently supported tag you selected and recorded. The base image must provide the `python` interpreter and a usable shell for the optional diagnostic commands; if you choose a minimal variant without a shell, adapt diagnostics rather than assuming `/bin/sh` exists.

```dockerfile
FROM python:<PYTHON_BASE_IMAGE_TAG>

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    SERVICE_MODE=fixed \
    SERVICE_NAME=lab-readiness-api

WORKDIR /app
COPY --chown=10001:10001 app.py /app/app.py

USER 10001:10001
EXPOSE 8080

CMD ["python", "/app/app.py"]
```

- **Why:** `USER` makes the intended non-root identity explicit; `PYTHONUNBUFFERED` helps logs reach stdout promptly; `PYTHONDONTWRITEBYTECODE` avoids writing `.pyc` files into a read-only application directory.
- **Verify:** rebuild and inspect the image, then run `docker run --rm --entrypoint python lab-readiness-api:prr-01 -c 'import os; print(os.getuid())'`. Expected output is `10001` on Linux containers.
- **Caution:** this verifies the process identity in the image, not every Kubernetes security control. The pod security context must also be set.

### 10.3 Fixed namespace and ConfigMap

`k8s/fixed/namespace.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: lab-readiness
  labels:
    app.kubernetes.io/part-of: production-readiness-baseline
```

`k8s/fixed/config.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: lab-readiness-config
  namespace: lab-readiness
data:
  SERVICE_NAME: "lab-readiness-api"
  SERVICE_MODE: "fixed"
  SLOW_SECONDS: "3"
```

- **Why:** runtime configuration is separate from the image. Do not put credentials in this ConfigMap.
- **Verify:** `kubectl -n lab-readiness get configmap lab-readiness-config -o yaml` shows only non-sensitive configuration.

### 10.4 Secret handling: safe example only

Do not commit a live Secret manifest containing real values. For this service, the fake `DEMO_TOKEN` is not used by application logic and should be removed entirely rather than carried forward unnecessarily.

If you need to practise a Secret reference, create a local-only object from a dummy value at the command line and do not save its value in Git:

```bash
kubectl config current-context
kubectl -n lab-readiness create secret generic lab-demo-secret --from-literal=DEMO_TOKEN='dummy-not-a-credential'
kubectl -n lab-readiness describe secret lab-demo-secret
```

- **Does:** creates a lab Secret with a fake value and shows metadata without printing the value.
- **Expected:** the Secret exists and its type/key metadata are shown. The literal is not a credential and must never be reused in a real environment.

Kubernetes Secret values are base64-encoded in the API representation; base64 is not encryption. Secret safety also depends on API authorization, encryption-at-rest configuration, audit access, and avoiding leakage into logs, shell history, CI logs, or Git. The detailed secrets module is **M09**. This local project does not prove a production secret-management design.

### 10.5 Fixed Deployment

`k8s/fixed/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lab-readiness-api
  namespace: lab-readiness
  labels:
    app.kubernetes.io/name: lab-readiness-api
spec:
  replicas: 2
  revisionHistoryLimit: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0
      maxSurge: 1
  selector:
    matchLabels:
      app: lab-readiness-api
  template:
    metadata:
      labels:
        app: lab-readiness-api
        app.kubernetes.io/name: lab-readiness-api
    spec:
      terminationGracePeriodSeconds: 20
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
        runAsGroup: 10001
        seccompProfile:
          type: RuntimeDefault
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                topologyKey: kubernetes.io/hostname
                labelSelector:
                  matchLabels:
                    app: lab-readiness-api
      containers:
        - name: api
          image: lab-readiness-api:prr-01
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 8080
          envFrom:
            - configMapRef:
                name: lab-readiness-config
          env:
            - name: PORT
              value: "8080"
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
          resources:
            requests:
              cpu: "100m"
              memory: "64Mi"
            limits:
              cpu: "500m"
              memory: "128Mi"
          startupProbe:
            httpGet:
              path: /healthz
              port: http
            periodSeconds: 2
            timeoutSeconds: 1
            failureThreshold: 15
          readinessProbe:
            httpGet:
              path: /readyz
              port: http
            periodSeconds: 5
            timeoutSeconds: 2
            failureThreshold: 2
          livenessProbe:
            httpGet:
              path: /healthz
              port: http
            periodSeconds: 10
            timeoutSeconds: 2
            failureThreshold: 3
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 3"]
```

**Important review notes before applying:**

- Resource values are initial lab settings, not benchmarks or universal recommendations. Observe behaviour and adjust them based on measured usage and application needs. If the selected base image does not contain `/bin/sh`, remove the `preStop` hook and rely on SIGTERM handling plus a suitable grace period; verify the image before choosing.
- `startupProbe` protects a slow startup; it is not a general dependency health check. `readinessProbe` controls whether the pod should receive traffic. `livenessProbe` should test whether the process is stuck and cannot recover; do not make liveness depend on a remote service.
- `preStop` consumes part of the termination grace period. The service's fixed mode marks readiness false after SIGTERM and calls server shutdown. The exact order and timing of endpoint removal, hook execution, signal delivery, and in-flight request completion depend on Kubernetes and runtime behaviour; verify in the lab.
- Preferred anti-affinity does not guarantee separation. A single-node kind cluster can schedule both replicas on the same node. That is an explicit simulation limit.
- The image tag `prr-01` is a local convenience. For a production pipeline, resolve and deploy an immutable digest or enforce immutable tags.
- If the read-only root filesystem causes the Python runtime or selected base image to write somewhere, identify the path and add a narrowly scoped writable volume rather than disabling read-only mode without explanation.

### 10.6 Service

`k8s/fixed/service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: lab-readiness-api
  namespace: lab-readiness
spec:
  selector:
    app: lab-readiness-api
  ports:
    - name: http
      port: 80
      targetPort: http
  type: ClusterIP
```

- **Why:** provides a stable in-cluster endpoint and a concrete target for readiness/endpoint checks.
- **Verify:** `kubectl -n lab-readiness get endpoints lab-readiness-api` lists ready pod addresses after the Deployment is healthy.

### 10.7 PodDisruptionBudget

`k8s/fixed/pdb.yaml`:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: lab-readiness-api
  namespace: lab-readiness
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: lab-readiness-api
```

- **Why:** constrains voluntary disruptions so at least one selected pod should remain available when the budget is honoured.
- **Verify:** `kubectl -n lab-readiness get pdb lab-readiness-api` shows expected desired/current healthy values once both replicas are ready.
- **Limit:** a PDB does not protect against involuntary failures and cannot create capacity that does not exist. Do not assume it guarantees node- or zone-level availability.

### 10.8 NetworkPolicy example

`k8s/fixed/networkpolicy.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: lab-readiness-api-ingress
  namespace: lab-readiness
spec:
  podSelector:
    matchLabels:
      app: lab-readiness-api
  policyTypes:
    - Ingress
  ingress:
    - ports:
        - protocol: TCP
          port: 8080
```

This example limits selected ingress traffic to the declared port but does not specify `from`, so it permits ingress to that port from any source allowed by the cluster's policy implementation. It is intentionally not presented as a complete least-privilege policy. For an actual allow-list, specify the expected pod/namespace selectors and test from both allowed and disallowed sources.

**[VERIFY]** NetworkPolicy enforcement depends on the CNI. Do not infer enforcement from successful `kubectl apply`. Record the CNI used by your kind setup and test policy behaviour before relying on it. Networking is deepened in **M04**; security controls in **M12**.

### 10.9 Apply fixed manifests in a controlled order

Before replacing the running Deployment, record the baseline image and revision. Ensure the fixed image is loaded into the same kind cluster.

```bash
kubectl config current-context
kubectl -n lab-readiness get deployment lab-readiness-api -o wide
kubectl -n lab-readiness rollout history deployment/lab-readiness-api
```

- **Does:** confirms context, image, and current revision.
- **Expected:** current baseline state is recorded.

Apply:

```bash
kubectl apply -f k8s/fixed/namespace.yaml
kubectl apply -f k8s/fixed/config.yaml
kubectl apply -f k8s/fixed/deployment.yaml
kubectl apply -f k8s/fixed/service.yaml
kubectl apply -f k8s/fixed/pdb.yaml
kubectl apply -f k8s/fixed/networkpolicy.yaml
kubectl -n lab-readiness rollout status deployment/lab-readiness-api --timeout=180s
kubectl -n lab-readiness get deployment,pods,service,pdb -o wide
```

- **Does:** applies the hardened resources and waits for the rollout.
- **Expected:** two pods become Ready, Service and PDB exist, and rollout status succeeds. If a pod fails, inspect events and logs rather than removing security settings blindly.

### 10.10 Resource sizing method

Treat the example requests and limits as a starting hypothesis only.

1. Capture `kubectl top pods -n lab-readiness` if the Metrics API is available. If not, record the limitation and use local process/container observations only as a rough diagnostic.
2. Exercise ordinary and `/slow` traffic; do not use an unbounded load generator.
3. Observe restarts, latency, and resource use under the test load.
4. Set CPU requests to reflect expected scheduling needs and memory requests to reflect expected working set, including realistic variation.
5. Set limits based on platform policy and acceptable failure modes. Memory limits can trigger OOM kills; CPU limits can throttle.
6. Explain the chosen values in `docs/retrospective.md`. Do not copy the example numbers into another service without measurement.

### 10.11 Verify fixed security and readiness settings

```bash
kubectl -n lab-readiness get deployment lab-readiness-api -o yaml
kubectl -n lab-readiness get pods -o jsonpath='{range .items[*]}{.metadata.name}{" ready="}{.status.containerStatuses[0].ready}{" restarts="}{.status.containerStatuses[0].restartCount}{" qos="}{.status.qosClass}{"\n"}{end}'
kubectl -n lab-readiness get endpoints lab-readiness-api
kubectl -n lab-readiness get pdb lab-readiness-api
```

- **Does:** inspects the desired deployment, pod status, Service endpoints, and PDB.
- **Expected:** security contexts, probes, resources, two replicas, endpoints, and PDB are present. Record the observed QoS class; do not assume it from memory.
- **Evidence:** `evidence/fixed/workload-review.txt`.

### Verify

- Fixed image runs as UID `10001`.
- Two replicas become Ready, subject to local scheduling capacity.
- Startup, readiness, and liveness probes are configured with distinct purposes.
- Root filesystem is read-only and privilege escalation is disabled.
- Service, PDB, resource settings, and NetworkPolicy object are present.
- No real secrets are in source or manifests.

**Checkpoint:** save the image ID, fixed YAML, rollout status, pod security/runtime evidence, endpoint list, PDB state, and NetworkPolicy/CNI limitation in `evidence/fixed/`.

## 11. Phase 4 — Prove the fixes (re-run and compare)

Re-run the same experiments where safe. Keep the baseline evidence immutable; add fixed results to `evidence/fixed/`. Do not claim improvement unless the observable changed in the expected direction.

### Comparison template

Create `docs/before-after.md`:

```markdown
# Before/after evidence

- Cluster/context:
- Date:
- Baseline image ID:
- Fixed image ID:
- Test conditions and limitations:

| Test / finding | Hypothesis | Baseline observation | Fixed observation | Evidence paths | Result | Limitations |
|---|---|---|---|---|---|---|
| A: single replica deleted | | | | | | |
| B: SIGTERM / in-flight request | | | | | | |
| C: memory limit (optional) | | | | | | |
| D1: bad readiness | | | | | | |
| D2: bad liveness | | | | | | |
| E: drain/PDB simulation | | | | | | |
| F: fake sentinel exposure | | | | | | |
```

### Repeat Test A against fixed deployment

First ensure the fixed deployment is healthy:

```bash
kubectl config current-context
kubectl -n lab-readiness rollout status deployment/lab-readiness-api --timeout=180s
kubectl -n lab-readiness get pods -o wide
kubectl -n lab-readiness get endpoints lab-readiness-api
```

- **Does:** confirms two ready replicas and Service endpoints.
- **Expected:** both replicas are Ready and listed as endpoints, assuming cluster capacity permits.

Forward the Service:

```bash
kubectl -n lab-readiness port-forward service/lab-readiness-api 18080:80
```

Repeat the request loop from Test A. While it is running, delete only one of the two lab pods:

```bash
kubectl config current-context
kubectl -n lab-readiness get pods -l app=lab-readiness-api
POD="$(kubectl -n lab-readiness get pod -l app=lab-readiness-api -o jsonpath='{.items[0].metadata.name}')"
kubectl -n lab-readiness delete pod "$POD"
kubectl -n lab-readiness get pods -w
```

- **Does:** deletes one pod and observes the Service while another replica should remain.
- **Expected:** the other ready replica may continue serving requests. A port-forward may reconnect or show failures independently of in-cluster Service routing, so do not over-interpret a single local failure. For a stronger test, run a temporary client pod inside the cluster and request the Service by DNS; record the exact method used.

**Cleanup:** stop the loop, wait for two ready replicas, verify `/`, `/readyz`, and `/metrics`, and preserve output.

### Repeat the shutdown test

Use the fixed deployment and a slow request. Observe the shutdown logs and request result. The fixed handler marks readiness false and asks the server to shut down after SIGTERM. It cannot guarantee that every in-flight request completes under every forced termination timing. Record whether the request completed, failed, or timed out and whether the process exited before the grace period.

### Repeat the probe tests

Do not leave deliberately bad probes in the fixed Deployment. Use temporary copies and restore the correct manifest after each test. Confirm the correct readiness and liveness probes recover when the correct manifest is reapplied.

### Repeat the PDB test only if safe

A PDB is meaningful only with sufficient replicas and a safe worker node. If the local topology does not support this, retain the limitation in the evidence and mark the test “Not demonstrated.” A conceptual explanation is not a test result.

### Verify

- Each repeated experiment has baseline and fixed observations.
- The evidence records failures as well as successes.
- Limitations are explicit, especially for port-forward, node drain, CNI enforcement, and resource metrics.
- The fixed deployment is healthy after experiments.

**Checkpoint:** finish `docs/before-after.md` and save fixed test logs under `evidence/fixed/`. Save any failed or inconclusive result rather than deleting it.

## 12. Phase 5 — Operability documents

### 12.1 One-page runbook template

Create `docs/runbook.md` and fill every field. Keep it short enough to use during an incident.

```markdown
# Runbook — lab-readiness-api

## Service overview
- Purpose:
- Owner:
- On-call/escalation:
- Namespace:
- Deployment:
- Service:
- Normal port:
- Dependencies:
- Data/state stored:

## First five minutes
1. Confirm current cluster context and namespace.
2. Check Deployment and pod readiness.
3. Check recent events and container logs.
4. Probe `/healthz`, `/readyz`, and `/metrics`.
5. Decide whether rollback or further diagnosis is safer.

## Checks
- Deployment: `kubectl -n lab-readiness rollout status deployment/lab-readiness-api`
- Pods: `kubectl -n lab-readiness get pods -o wide`
- Events: `kubectl -n lab-readiness get events --sort-by=.lastTimestamp`
- Logs: `kubectl -n lab-readiness logs deployment/lab-readiness-api --tail=100`
- Metrics: `kubectl -n lab-readiness port-forward service/lab-readiness-api 18080:80`, then `curl -i http://127.0.0.1:18080/metrics`

## Common symptoms
| Symptom | Check | Action | Escalate when |
|---|---|---|---|
| Pods not Ready | `describe pod`, events, readiness path | Restore known-good config; inspect logs | Not recovered within the stated local test window |
| Restart count rising | Previous logs, liveness events, exit reason | Compare recent change; roll back if linked to release | Repeated restarts continue |
| 5xx responses | `/metrics`, `/fail` only for controlled test, logs | Confirm if test traffic is deliberate; inspect handler errors | Errors occur on normal requests |
| ImagePullBackOff | Image name/tag, kind image load, pod events | Build/load the intended local image | Image remains unavailable after correction |
| Rollout stalled | `rollout status`, `describe deployment` | Inspect readiness, image, and resource constraints | No safe known-good revision exists |

## Rollback
1. Confirm context.
2. Record current revision and failure evidence.
3. Run `kubectl -n lab-readiness rollout undo deployment/lab-readiness-api`.
4. Wait for rollout status.
5. Re-run `/` and `/healthz`; capture output.
6. Record whether rollback restored service and what remains unresolved.

## Escalation and communications
- Escalation contact:
- What to include in an escalation:
- Incident channel/ticket:
- Update cadence:
- Known limitations:
```

Do not invent a real owner or on-call contact. For this solo lab, enter “Learner / no external on-call” and describe the escalation path as a self-review or mentor review.

### 12.2 SLI/SLO draft template

Create `docs/slo-draft.md`.

```markdown
# SLI/SLO draft — lab-readiness-api

## Service boundary
- User-visible operation:
- Measurement window:
- Traffic source:
- Exclusions (if any):

## SLI
- Definition: successful main-endpoint responses divided by eligible main-endpoint requests.
- Measurement method: controlled client records HTTP status codes; a future metrics pipeline can calculate the ratio.
- Known limitation: this lab's hand-written metrics are process-local and do not persist across restarts.

## Draft SLO
- Target: at least 99% successful eligible requests over a stated 7-day learning window.
- Status: illustrative draft only; not a production commitment.
- Why this target was chosen:
- What counts as an eligible request:
- How failures and missing samples are handled:

## Simple alert idea
- Alert if the observed error ratio exceeds the draft threshold for a sustained interval and there is enough request volume to interpret it.
- Measurement source:
- Evaluation interval:
- Action/runbook:
- False-positive risks:

## Error budget
- Definition: the allowed unsuccessful portion implied by the target over the window.
- Calculation for the chosen target:
- How the team would use it:
```

The 99% target is an **exercise assumption**, not a recommendation for every service. State that the example target implies a 1% error budget over the same eligible-request window, subject to the exact SLI definition. In a real service, choose the SLO from user needs, risk, and observed capability. SLI/SLO and alerting are deepened in **M10** and **M11**.

### 12.3 Backup and restore note

Create `docs/backup-restore.md`.

This service has no durable business data. Do not invent a database backup requirement. The recoverable state for this project is the source, manifests, and configuration in Git.

```markdown
# Backup and restore — lab-readiness-api

## State inventory
- Durable business data: none in this sample service.
- Configuration: ConfigMap manifest in `k8s/fixed/config.yaml`.
- Deployment specification: `k8s/fixed/deployment.yaml`.
- Source: `service/app.py` and `service/Dockerfile`.
- Secret material: no real secret is used or committed.

## Backup method
- Commit reviewed source, manifests, and documentation to version control.
- Do not commit kubeconfig, live Secret YAML, tokens, or shell history.

## Restore drill
- Date/time started:
- Restore source revision:
- Restore command:
- Expected result:
- Actual result:
- Elapsed time:
- Evidence path:
- Deviations and follow-up:

## Limitations
- This is a configuration/source restore drill, not a storage backup or disaster-recovery proof.
- A local Git checkout does not prove off-site backup durability.
```

**Perform the drill:** create a temporary copy of the project or use a clean worktree/clone of your own repository; restore the manifests from the committed revision; apply them to the lab namespace; wait for rollout; test `/` and `/healthz`; record start/end times and the exact commands. If your repository has no remote backup, say so. Do not claim recovery-point or recovery-time objectives were validated by this local drill.

### 12.4 Rollback drill

Create `docs/rollback-drill.md`.

1. Confirm the lab context.
2. Record `kubectl -n lab-readiness rollout history deployment/lab-readiness-api`.
3. Make a reversible, harmless image or annotation change to create a new Deployment revision. Do not deploy an unknown or untrusted image.
4. Wait for the rollout to complete, then capture revision history.
5. Execute `kubectl -n lab-readiness rollout undo deployment/lab-readiness-api`.
6. Wait for rollout status and test `/` and `/healthz`.
7. Capture the revision history after rollback and compare the pod image with the recorded known-good image.
8. Restore the desired fixed manifest using `kubectl apply -f k8s/fixed/deployment.yaml` if needed, then confirm it is healthy.

Commands for the evidence capture:

```bash
kubectl config current-context
kubectl -n lab-readiness rollout history deployment/lab-readiness-api
kubectl -n lab-readiness rollout status deployment/lab-readiness-api --timeout=180s
kubectl -n lab-readiness rollout undo deployment/lab-readiness-api
kubectl -n lab-readiness rollout status deployment/lab-readiness-api --timeout=180s
kubectl -n lab-readiness get deployment lab-readiness-api -o wide
```

- **Does:** records the current revision, waits for the current rollout, rolls back one revision, and verifies the resulting Deployment.
- **Expected:** rollback completes to a prior revision. If no prior revision is available, record the reason and restore by applying the known-good fixed manifest; do not claim `rollout undo` succeeded.
- **Evidence:** save command output, image references, endpoint smoke tests, and elapsed time in `evidence/fixed/rollback-drill.txt`.

### 12.5 Phase 5 Verify

- Runbook has concrete checks, actions, and rollback steps.
- SLI/SLO draft defines numerator, denominator, window, target, and limitations.
- Restore drill was actually performed and timed, or clearly marked not completed.
- Rollback drill has before/after revision evidence.
- Ownership and escalation are honest for a solo learner.

**Checkpoint:** commit `docs/runbook.md`, `docs/slo-draft.md`, `docs/backup-restore.md`, `docs/rollback-drill.md`, and the associated evidence.

## 13. Acceptance criteria

Mark each row `Pass`, `Fail`, or `Not demonstrated`. A `Not demonstrated` result is not a pass; explain the blocker and next step. Every result must point to evidence.

| # | Area | Criterion | How to prove it (command or observable) | Expected result | Pass/Fail |
|---:|---|---|---|---|---|
| 1 | Environment | Current context is the intended local kind cluster | `kubectl config current-context` | Context name matches the lab cluster created for this project | |
| 2 | Environment | Dedicated namespace exists | `kubectl get namespace lab-readiness` | Namespace is `Active` | |
| 3 | Baseline | Baseline deployment reaches Running | `kubectl -n lab-readiness rollout status deployment/lab-readiness-api --timeout=120s` | Command exits successfully | |
| 4 | Baseline | Main endpoint works before fixes | `curl -i http://127.0.0.1:18080/` while baseline port-forward is active | HTTP `200` with service JSON | |
| 5 | Baseline | Failure path is visible | `curl -i http://127.0.0.1:18080/fail` | HTTP `500` | |
| 6 | Audit | All checklist rows have a recorded result | Review `docs/audit.md` against Section 7 | Every checklist number is represented; material findings have evidence and next action | |
| 7 | Audit | Baseline image identity is recorded | `docker image inspect lab-readiness-api:latest --format '{{.Id}}'` | Image ID recorded in evidence | |
| 8 | Audit | Runtime identity was inspected | `kubectl exec ... -- id` or documented alternative | Actual user/group or reason the check could not run is recorded | |
| 9 | Audit | Baseline probe/resource gaps are evidenced | Saved Deployment YAML and selected JSONPath output | Missing fields are visible or explicitly explained | |
| 10 | Break test | Single-pod disruption test includes context check and cleanup | `evidence/break-tests/test-a-single-replica.txt` | Context, hypothesis, request output, recovery, and cleanup are recorded | |
| 11 | Break test | SIGTERM test records actual request outcome | `evidence/break-tests/test-b-sigterm.txt` | Request outcome and timing are recorded; no guaranteed outcome is claimed | |
| 12 | Break test | OOM test is safe and honestly classified | `evidence/break-tests/test-c-memory.txt` | Observed result or explicit safe skip with reason; no unbounded load | |
| 13 | Break test | Readiness and liveness are distinguished | `evidence/break-tests/test-d-probes.txt` | Ready status and restart observations are recorded separately | |
| 14 | Break test | PDB/drain test is safe or marked not demonstrated | `evidence/break-tests/test-e-drain-simulation.txt` | Only local worker drain attempted; otherwise safe skip and topology reason recorded | |
| 15 | Security | Fixed container runs non-root | `docker run --rm --entrypoint python lab-readiness-api:prr-01 -c 'import os; print(os.getuid())'` | Prints `10001` | |
| 16 | Security | Pod security settings are declared | Inspect `k8s/fixed/deployment.yaml` and live Deployment YAML | `runAsNonRoot`, non-root UID/GID, `RuntimeDefault`, no privilege escalation, dropped capabilities, read-only root filesystem | |
| 17 | Security | No real secrets are committed | `git status --short` plus manual review of changed files | No live secret values, kubeconfig, or credentials in staged/committed files | |
| 18 | Runtime | Fixed deployment has startup/readiness/liveness probes | `kubectl -n lab-readiness get deployment lab-readiness-api -o yaml` | All three probe fields exist with documented purpose | |
| 19 | Runtime | Fixed deployment requests and limits are set | Inspect container `resources` in live Deployment YAML | CPU and memory requests/limits exist; rationale recorded | |
| 20 | Runtime | Fixed deployment reaches desired replica count | `kubectl -n lab-readiness get deployment lab-readiness-api` | Desired replicas are 2 and available replicas reach 2, subject to local capacity | |
| 21 | Runtime | Service endpoints include ready pods | `kubectl -n lab-readiness get endpoints lab-readiness-api` | At least one ready address; normally two when both replicas are Ready | |
| 22 | Runtime | PDB exists and selector matches app pods | `kubectl -n lab-readiness get pdb lab-readiness-api -o yaml` | `policy/v1` PDB selects `app: lab-readiness-api` and has `minAvailable: 1` | |
| 23 | Runtime | Rollout strategy is explicit | Inspect `spec.strategy` in fixed Deployment | `RollingUpdate`, `maxUnavailable: 0`, `maxSurge: 1` | |
| 24 | Observability | Metrics endpoint returns exposition | Port-forward Service then `curl -i http://127.0.0.1:18080/metrics` | HTTP `200`, `# HELP`, `# TYPE`, request and error counters present | |
| 25 | Observability | Fixed logs are JSON lines | `kubectl -n lab-readiness logs deployment/lab-readiness-api --tail=20` and parse each line with `python3 -c ...` | Each application log line parses as JSON; document any access-log exception | |
| 26 | Operability | Runbook has symptom/check/action and rollback | Review `docs/runbook.md` | At least five concrete symptoms and executable checks/actions | |
| 27 | Operability | SLI/SLO draft is measurable | Review `docs/slo-draft.md` | Numerator, denominator, window, target, measurement, and alert idea are defined | |
| 28 | Recovery | Restore drill is timed and evidenced | Review `docs/backup-restore.md` and drill output | Source/config restored and service smoke test succeeds, or explicit not-completed status | |
| 29 | Recovery | Rollback drill is evidenced | Review `evidence/fixed/rollback-drill.txt` | Prior revision restored or fallback procedure documented honestly | |
| 30 | Evidence | Before/after comparison is complete | Review `docs/before-after.md` | Every attempted test has paired observations or a documented reason no pair exists | |

### Definition of done

The project is done when all required acceptance criteria have a recorded status, all Blocker findings have been fixed or explicitly marked as unresolved with a reason, the fixed deployment passes its available local checks, the runbook and recovery documents are usable, and the evidence is sufficient for another learner to reproduce the review. “Not demonstrated” must remain visible; do not convert it to “Pass” because the test was difficult to run.

### Hard fails

Any of the following prevents a “Meets baseline” score regardless of points:

- A real secret, credential, or kubeconfig is committed.
- The fixed workload runs as root or silently removes the non-root requirement without documented justification.
- The fixed deployment has no readiness/liveness checks.
- A destructive test was run without verifying the current lab context.
- Evidence is missing for the central before/after claims.
- The learner reports a simulation as proof of production multi-node, multi-zone, or durable-storage behaviour.
- The fixed service is not recoverable to a known-good manifest/image.
- A test left the namespace or cluster in a broken state and cleanup was not completed.

## 14. Deliverables

Commit the following, adapted to your repository's project folder. These are project outputs, not pre-existing roadmap files.

| File | Required contents |
|---|---|
| `service/app.py` | Complete service source used for both modes |
| `service/Dockerfile` | Base-image placeholder resolved to a supported tag; non-root fixed image |
| `k8s/baseline/namespace.yaml` | Dedicated namespace |
| `k8s/baseline/config.yaml` | Non-sensitive baseline config |
| `k8s/baseline/deployment.yaml` | Baseline workload used for the audit |
| `k8s/fixed/namespace.yaml` | Dedicated namespace definition |
| `k8s/fixed/config.yaml` | External non-sensitive runtime configuration |
| `k8s/fixed/deployment.yaml` | Hardened deployment with probes, resources, security context, replicas, and rollout strategy |
| `k8s/fixed/service.yaml` | Stable in-cluster endpoint |
| `k8s/fixed/pdb.yaml` | Voluntary disruption budget |
| `k8s/fixed/networkpolicy.yaml` | Example policy with enforcement caveat documented |
| `docs/audit.md` | Complete checklist audit with evidence pointers |
| `docs/before-after.md` | Hypotheses and baseline/fixed comparisons |
| `docs/runbook.md` | Triage, checks, actions, rollback, escalation |
| `docs/slo-draft.md` | Draft SLI/SLO, target, measurement, alert idea, limitations |
| `docs/backup-restore.md` | State inventory, restore method, performed drill and timing |
| `docs/rollback-drill.md` | Rollback plan and interpretation |
| `docs/retrospective.md` | Resource sizing rationale, lessons, remaining risks |
| `evidence/environment.txt` | Context and tool versions; no credentials |
| `evidence/baseline/` | Baseline inspection, image identity, smoke test, logs |
| `evidence/break-tests/` | Hypotheses, commands, outcomes, cleanup for each attempted test |
| `evidence/fixed/` | Fixed rollout, runtime identity, endpoints, metrics, logs, rollback and restore evidence |
| `.gitignore` | Excludes local secrets and generated sensitive files |

Suggested `.gitignore` essentials:

```gitignore
# Local credentials and cluster access
.kube/
kubeconfig
kubeconfig.*
*.kubeconfig
.env
.env.*
!.env.example
*credentials*
*token*

# Generated local evidence that may contain sensitive output
evidence/private/
evidence/**/secret-dump*
*.pem
*.key

# Python
__pycache__/
*.py[cod]
.venv/
venv/

# Local editor/OS files
.DS_Store
Thumbs.db
```

Review ignore patterns before use. Broad patterns such as `*token*` can hide legitimate documentation or source files; check `git status --ignored` and use `git check-ignore -v <path>` when needed. Do not rely on `.gitignore` alone to prevent secrets from being committed.

Before committing:

```bash
git status --short
git diff --check
git diff --cached --check
```

- **Does:** checks changed files and whitespace errors.
- **Expected:** only intended files are staged, no whitespace errors are reported, and no credentials are included.
- **Caution:** these commands do not perform secret scanning. Manually inspect staged diffs and use a local secret scanner only if you already have one installed.

## 15. Self-scoring rubric

Score each area from 0 to its weight based on the evidence, not on how much YAML was written. Total possible score: **100 points**.

| Area | Weight | Full-credit evidence |
|---|---:|---|
| Audit completeness and severity judgement | 15 | All 28 checklist rows assessed with evidence and reasoned severity |
| Baseline reproduction and break-test safety | 15 | Reproducible baseline; hypotheses, context checks, outcomes, and cleanup |
| Runtime hardening | 20 | Probes, resource settings, shutdown, replicas, rollout strategy, PDB |
| Container and pod security | 15 | Non-root, least privilege, read-only root filesystem, image identity, no real secrets |
| Observability and SLI/SLO | 10 | JSON logs, metrics endpoint, measurable draft SLI/SLO and alert idea |
| Recovery and operability | 15 | Runbook, rollback drill, restore drill, explicit limitations |
| Evidence quality and retrospective | 10 | Before/after comparisons, exact commands/results, lessons and remaining risks |
| **Total** | **100** | |

### Score thresholds

| Score | Level | Meaning |
|---:|---|---|
| 0–59 | Not yet | Major gaps remain; repeat the audit and fix phases. |
| 60–74 | Meets baseline | The core review, fixes, and evidence are present; limitations are honestly documented. |
| 75–89 | Strong | Most findings are tied to reproducible tests and the operational artefacts are practical. |
| 90–100 | Exemplary | Evidence is precise, risk reasoning is nuanced, and the work is reproducible by another learner. |

The score is capped below **Meets baseline** if any hard fail applies. Do not invent or paraphrase proficiency-level definitions from the roadmap's prerequisite file; use [prerequisites and exit criteria](../prerequisites-and-exit-criteria.md) for the official Stage 2E proficiency expectations. This rubric is specific to this project and does not grant a professional certification or guarantee a job outcome.

## 16. Stretch goals (optional)

Complete these only after the core acceptance criteria pass. Each maps to a later module.

1. **Add a HorizontalPodAutoscaler.** Explain the metrics API dependency, define a load profile, and document why CPU utilisation may be a poor scaling signal for some services. **M03/M15**.
2. **Sketch a `ServiceMonitor`-style scrape contract.** Do not install a full monitoring stack for this project; document labels, scrape path, and metric names. **M11**.
3. **Produce an SBOM and scan the image.** Use a free local tool only if already available or installable without payment; record tool/version and findings. Do not claim “zero vulnerabilities” without defining scanner and database freshness. **M12**.
4. **Build a reproducible CI check.** Add syntax checks and image build in a local or free CI environment, without committing secrets. **M02**.
5. **Create a second local kind cluster.** Demonstrate how you would test configuration drift or recovery, but label it a simulation rather than multi-region failover. **M14**.
6. **Estimate resource cost.** Translate requests/limits into a hypothetical capacity estimate using clearly stated assumptions; do not present it as a cloud bill. **M15**.

## 17. Troubleshooting

| Symptom | Likely cause | Fix / verification |
|---|---|---|
| `ImagePullBackOff` | Image tag not loaded into this kind cluster, image name mismatch, or pull policy expects a remote image | Run `docker image ls`, confirm the exact image tag, load it into the correct kind cluster, then inspect pod events |
| `ErrImageNeverPull` | Manifest uses `Never` but image is not present on the selected node | Load the image into kind or use a pull policy appropriate for the local workflow |
| Pod remains `Pending` | Insufficient cluster capacity, scheduling constraints, or resource requests cannot fit | `kubectl describe pod`; inspect events and requests; reduce lab scope or create a safe cluster with adequate capacity |
| `CrashLoopBackOff` with read-only filesystem | Process or base image tries to write to a path that is read-only | Inspect logs and filesystem writes; add a narrowly scoped writable `emptyDir` only for the required path |
| `Permission denied` as non-root | File ownership or writable path assumes root | Inspect Dockerfile ownership and runtime UID; make only required files/paths accessible to UID `10001` |
| Probe fails immediately | Wrong path/port, app not listening on `0.0.0.0`, or startup budget too short | Check pod logs, probe config, named port, and actual startup time; adjust with evidence |
| Readiness fails but pod is Running | Readiness path returns non-2xx or the application is not ready | `describe pod`; `curl` the endpoint through port-forward; do not automatically change liveness |
| Liveness causes repeated restarts | Liveness checks a dependency or uses aggressive thresholds | Make liveness local to process health; use readiness for inability to serve; review events and restart count |
| Port-forward says address already in use | Another local process owns port `18080` | Stop the old port-forward or choose a different local port, such as `18081:80` |
| PDB blocks drain | Eviction would violate `minAvailable`, or not enough replicas are healthy | Check `kubectl describe pdb` and pod placement; restore health or stop the simulation; do not delete pods to bypass the budget |
| `/metrics` unreachable | Port-forward target is wrong, app not Ready, or path/port mismatch | Check Service endpoints and port names; test `/metrics` on the pod via port-forward |
| Logs are not JSON | Baseline mode is still configured or old pods remain | Verify ConfigMap `SERVICE_MODE=fixed`, rollout status, and logs from the new pod |
| `kubectl top` unavailable | Metrics API is not installed or not ready | Record `[VERIFY]`; do not treat missing metrics as zero; this project can continue without it |
| NetworkPolicy has no visible effect | Current CNI does not enforce NetworkPolicy or the policy is too broad | Record CNI, test allowed/denied paths, and do not claim enforcement without observed evidence |
| Rollout stalls | Image cannot start, probes fail, resource settings are too tight, or the cluster lacks capacity | Inspect `rollout status`, pod events, logs, and previous revision; restore the known-good manifest if needed |
| `kubectl drain` hangs | PDB blocks eviction, target is wrong, or daemonsets/local storage complicate drain | Stop and inspect events/PDB; uncordon the node if necessary; never force-delete blindly |
| `preStop` command fails | Selected image lacks `/bin/sh` or `sleep` | Verify image contents; remove the hook or use a supported hook approach and test it |
| Metrics values appear reset | Counters are process-local and restart with the process | Document that limitation; use a monitoring system and appropriate aggregation in M11 |

## 18. Retrospective prompts and interview angle

Answer in `docs/retrospective.md` with evidence references.

1. Which finding would have paged you first, and what signal would have detected it?
2. Which baseline weakness had the highest impact, and which had the highest likelihood?
3. What did the one-replica disruption test actually prove? What did it not prove?
4. Did the fixed version complete an in-flight request during termination? What exact evidence supports your answer?
5. How did resource requests, limits, and QoS affect the pod? Which observations are missing because Metrics API was unavailable?
6. Which security controls are enforced by the manifest, and which remain assumptions about the cluster?
7. What is the difference between readiness, liveness, and startup probes? Give a failure mode for each.
8. What remains unproven about backups, durable storage, node failure, NetworkPolicy, and multi-zone availability?
9. Which two changes would you prioritise before a real launch, and what evidence would you demand?
10. What would you automate in CI or a future platform workflow to prevent the same regression?

### Interview explanation

Explain the project as an engineering story, not as a list of tools:

- **Situation:** you inherited a working but under-engineered service.
- **Task:** audit readiness and reduce the highest-risk failure modes without expanding scope.
- **Action:** capture baseline evidence, write hypotheses, reproduce safe failures, harden the container and workload, and verify the same scenarios after the fix.
- **Result:** cite actual observed changes and evidence paths. If a test was not demonstrated, say so.
- **Trade-off:** distinguish local simulations from production guarantees and explain which later module would deepen each area.

Do not claim production experience from a lab exercise. The value is that you can explain the reasoning, test design, operational limits, and evidence honestly.

## 19. Answer key — SPOILER

> ⚠️ **Spoilers below. Complete Phase 1 and save the audit table before reading this section.**

The baseline includes the following seeded weaknesses. Map each to your own evidence; if your observed image or runtime differs, update the finding rather than blindly copying this answer key.

| Seeded flaw | Checklist rows | Expected severity | Reference fix |
|---|---|---|---|
| Mutable `latest` image tag | 1, 2 | Major | Use a recorded image identity and immutable digest/tag strategy; local `prr-01` is a lab convenience only |
| No explicit non-root user | 3, 4 | Blocker | Set Dockerfile `USER` and pod `runAsNonRoot`, UID/GID |
| No pod/container security context | 3, 4, 5 | Major | Add seccomp `RuntimeDefault`, disable privilege escalation, drop capabilities, and set read-only root filesystem |
| Writable root filesystem | 5 | Major | Set `readOnlyRootFilesystem: true`; add only necessary writable volumes |
| No startup/readiness/liveness probes | 6, 7, 8 | Blocker/Major | Add distinct probes with a documented failure model |
| No resource requests or limits | 9, 10 | Major | Observe use where possible, choose justified requests/limits, and record QoS |
| One replica | 12 | Blocker | Set at least two replicas and document that local topology does not prove independent failure domains |
| No explicit rolling-update parameters | 13 | Major | Set and verify `maxUnavailable`/`maxSurge` |
| No PodDisruptionBudget | 14 | Major | Add `policy/v1` PDB and test only in a safe multi-node simulation |
| Configuration and mode are prototype-oriented | 15 | Major | Use ConfigMap for non-sensitive runtime config; set fixed mode outside the image |
| Fake sensitive-looking token inline in Deployment | 16 | Blocker if real; Major as a teaching example | Remove unused token; use Secret references only when needed; never use a real credential in this project |
| Plain-text baseline logs | 17 | Major | Emit JSON lines to stdout in fixed mode; avoid secret-bearing fields |
| No documented SLI/SLO or alert idea | 18, 19 | Major | Write a measurable draft and a simple alert idea |
| No Service, runbook, rollback drill, or evidence package | 22, 23, 24, 27, 28 | Major | Add Service, runbook, rollback drill, and evidence-linked documentation |

### Why the baseline remains deliberately simple

The baseline is a teaching artefact, not a secure template. Do not reuse it for a real deployment. The fixed version is still only a local learning baseline; a production launch would require context-specific threat modelling, operational ownership, supply-chain controls, environment-specific secrets management, tested disaster recovery, and a review of organisational requirements.

## 20. Cleanup

Do not clean up until all evidence has been saved and reviewed. Confirm the current context before deleting resources.

### Remove project resources

```bash
kubectl config current-context
kubectl -n lab-readiness get all
kubectl delete namespace lab-readiness
kubectl get namespace lab-readiness
```

- **Does:** confirms context, lists project resources, deletes the dedicated namespace, and checks that it is gone.
- **Expected:** namespace deletion completes and the final query reports that the namespace was not found.
- **Safety:** if the context is not the lab context, stop. Never copy/paste the deletion command into a production terminal.

If you created a separate kind cluster solely for this project and no other lab depends on it, confirm the cluster name first:

```bash
kind get clusters
```

Then delete only that named lab cluster:

```bash
kind delete cluster --name <YOUR_KIND_CLUSTER_NAME>
kind get clusters
```

- **Does:** deletes the named local kind cluster and lists remaining clusters.
- **Expected:** the deleted cluster is absent. Replace the placeholder with the exact cluster name shown by `kind get clusters`.

Remove the local image only if no other lab uses it:

```bash
docker image rm lab-readiness-api:latest lab-readiness-api:prr-01
```

- **Does:** removes the two local tags.
- **Expected:** Docker removes tags that exist and are not in use; if a tag is absent or a container still references it, read the message and do not force-delete unrelated images.

### Final cleanup checklist

- [ ] `kubectl -n lab-readiness get all` was captured before deletion.
- [ ] Namespace deletion was confirmed.
- [ ] Any drained node was uncordoned before cluster deletion.
- [ ] Temporary diagnostic pods and bad-probe manifests were removed or retained only as non-sensitive evidence.
- [ ] Port-forward and request-loop processes were stopped.
- [ ] No test container remains running.
- [ ] No secrets, kubeconfigs, or credential-bearing logs were committed.
- [ ] Evidence and retrospective are committed or backed up.
- [ ] If the cluster is shared with another local lab, it was not deleted.

For the wider lab reset sequence, see the reset section in [local kind/minikube/LocalStack lab](../local-lab-kind-minikube-and-localstack.md).

## 21. Reference Sources

Use these authoritative source names when checking details that depend on Kubernetes or tooling versions. This brief intentionally does not pin current tool or base-image versions.

- Kubernetes Documentation — **Liveness, Readiness and Startup Probes**
- Kubernetes Documentation — **Configure Liveness, Readiness and Startup Probes**
- Kubernetes Documentation — **Resource Management for Pods and Containers**
- Kubernetes Documentation — **Pod Quality of Service Classes**
- Kubernetes Documentation — **Pod Security Standards**
- Kubernetes Documentation — **Security Context**
- Kubernetes Documentation — **Deployments**
- Kubernetes Documentation — **Pod Disruptions** and **Disruptions**
- Kubernetes Documentation — **Network Policies**
- Kubernetes Documentation — **Secrets**
- Kubernetes Documentation — **ConfigMaps**
- Kubernetes Documentation — **Service**
- Kubernetes Documentation — **Debugging Applications**
- Kubernetes Documentation — **kubectl rollout**
- kind Documentation — **Quick Start** and **Loading an Image Into Your Cluster**
- Docker Documentation — **Dockerfile reference** and **docker image inspect**
- Prometheus Documentation — **Exposition Formats**
- Google, *Site Reliability Engineering* — service level objectives and monitoring
- Google, *The Site Reliability Workbook* — SLO implementation and alerting
- The Twelve-Factor App — **Config**, **Logs**, and **Disposability**
- CIS Kubernetes Benchmark — **[VERIFY]** version and applicability to the local cluster
- NSA/CISA, *Kubernetes Hardening Guidance* — **[VERIFY]** current edition and applicability

When a source's behaviour depends on the version or local CNI, verify against the installed version and record the version. Do not claim compliance with a benchmark from this project alone.
