# Resilient Data Pipeline on Kubernetes

> **Content status: DRAFT-AUDITED.** This local learning capstone is not production certification. Code, manifests, commands, and drills were not executed in this authoring pass. Outputs are illustrative unless explicitly labelled as learner-measured evidence.

## Project metadata
| Field | Value |
| --- | --- |
| Stage/module/unit | Stage 2E — Production DevOps & Platform Engineering / M03 — Production Kubernetes Operations / Unit 13 — Capstone |
| Target path | `Stage 2E — Production DevOps & Platform Engineering/03-Production-Kubernetes-Operations/Projects/01-resilient-data-pipeline-on-kubernetes.md` |
| Effort | 28–45 hours, planning estimate |
| Prerequisites | Linux/WSL2, Git, Docker, Python basics, YAML, kubectl basics, M01 images and M02 CI/CD |
| Core tools | Docker, kind, kubectl, Python 3, pytest, make, curl, jq |
| Awareness-only | Prometheus/Grafana, VPA, managed node autoscaler, managed Kubernetes |
| Lab target | Disposable kind cluster: one control-plane node and three workers; stage work on 4 CPU / 8 GB RAM / 30 GB disk |
| Baseline | Record actual Kubernetes, kind, kubectl, node image and etcd versions; `[VERIFY]` before execution |
| Last reviewed | 2026-10-25 |

## Executive summary and production problem statement
This capstone builds a locally verifiable operating baseline for a shared data platform consisting of a model-scoring HTTP API, queue consumer, stateful dependency, ETL Job and nightly CronJob. It addresses resource contention, harmful liveness probes, disruption during node drain, duplicate scheduled work, HPA oscillation, overprivileged ServiceAccounts and untested recovery. The goal is evidence-based operations—not a hello-world Deployment.

`kind` exercises Kubernetes APIs and workflows, but does not reproduce cloud load balancers, real multi-zone failure domains, managed control-plane recovery, provider node pools, or production SLOs. Distinguish measured local results, illustrative output, engineering inference and unresolved production checks throughout.

## Learning outcomes mapped to L1–L4
| Level | Capability | Evidence |
| --- | --- | --- |
| L1 | Explain control/data plane, namespaces, resources, probes, controllers, identities and Pod states. | Architecture and preflight record |
| L2 | Deploy five workload roles, diagnose a single failure and prove idempotent replay. | Tests, rollout evidence, ETL replay result |
| L3 | Correlate resource pressure, readiness, PDB, HPA, placement and quota; choose scoped mitigations. | Drain/load timeline, HPA observations, game-day reports |
| L4 | Design fleet-level policy/runbooks, handle uncertainty and distinguish local from production claims. | ADRs, upgrade gates, recovery plan, fidelity matrix |

## Scope, non-goals, assumptions, and success criteria
**In scope:** five workload roles; requests/limits, quota/LimitRange, probes, explicit ServiceAccounts, non-root security, PSS Restricted, least-privilege RBAC, PDB, graceful shutdown, HPA where compatible, simulated placement, upgrade preflight, backup/restore boundaries and incident response.

**Non-goals:** production-grade ML evaluation, HA database/broker, enterprise secret management, full monitoring platform or production-certified DR. One local PostgreSQL replica is not HA. CronJob controls do not provide exactly-once business effects.

**Success:** assemble the system without inventing missing pieces; run tests and supported checks; prove same-run ETL replay safety; measure drain and scaling outcomes; execute six drills individually; document limits. A blocked test is recorded `BLOCKED` or `OPEN`, never passed by assumption.

## Architecture and end-to-end data flow
```mermaid
flowchart LR
Client -->|POST /score| API[FastAPI scoring API]
API -->|transaction| DB[(PostgreSQL StatefulSet)]
Worker[Queue consumer] -->|claim and complete| DB
ETL[ETL Job] -->|idempotent run_id + row_key| DB
Cron[Nightly CronJob] --> ETL
Ops[Operator] -->|observe / hypothesize / test / fix / verify / document| Kube[Kubernetes API and controllers]
Kube --> Scheduler[Scheduler and kubelets]
Kube --> Metrics[Metrics API / optional Metrics Server]
```
1. API validates a request, calculates a transparent toy score and writes a work item.
2. Worker processes pending work. The database-backed queue is a bounded teaching choice, not a high-throughput broker.
3. ETL writes deterministic rows keyed by `(run_id, row_key)`; a database uniqueness constraint protects replay of the same logical run.
4. CronJob creates batch work on a schedule. `concurrencyPolicy: Forbid` does not guarantee global exactly-once business effects.
5. Kubernetes reconciles desired state; application correctness still depends on transaction boundaries, idempotency, retries and observability.

## Proposed learner workspace (illustrative, not an existing repository tree)
```text
resilient-data-pipeline/
  app/main.py
  app/tests/test_app.py
  requirements.txt Dockerfile Makefile versions.txt
  kind/cluster.yaml
  manifests/00-namespace.yaml
  manifests/01-governance.yaml
  manifests/02-postgres.yaml
  manifests/03-workloads.yaml
  manifests/04-rbac.yaml
  manifests/05-hpa-pdb-placement.yaml
  manifests/06-batch.yaml
  scripts/context-guard.sh bootstrap.sh record-versions.sh
  scripts/conformance.sh audit-rbac.sh verify-placement.sh
  scripts/load-test.sh chaos-drill.sh backup-plan.sh
  evidence/{preflight,versions,workloads,drain-test,autoscaling,placement,security,upgrade-rehearsal,backup-restore,chaos,runbooks,conformance,results}/
```

## Prerequisite and safety preflight
| Phase | Approximate incremental budget | Reduction |
| --- | --- | --- |
| Bootstrap | 0.5–1 CPU, 1–2 GB RAM, 1–3 GB disk | Create cluster before image builds |
| Core workloads | 2–3 CPU, 3–5 GB RAM, 5–10 GB disk | Start with one worker replica |
| HPA/load | 1–2 CPU and 1–2 GB RAM transient | Shorten tests if host pressure rises |
| Blue/green | Potentially +2–4 GB RAM and several GB disk | Optional; delete first cluster before second |
In WSL2, verify Docker resource limits, free disk and host stability. Bind mounts across Windows/WSL filesystems can be slower; DNS and port-forward behavior may differ. Record these conditions. Pause load tests if the host becomes unstable. Use a disposable, uniquely named cluster only.
```yaml
# File: kind/cluster.yaml
# Verify kind config API compatibility with installed kind.
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: resilient-pipeline
nodes:
  - role: control-plane
  - role: worker
  - role: worker
  - role: worker
```
```bash
# File: scripts/context-guard.sh
#!/usr/bin/env bash
set -euo pipefail
: "${CLUSTER_NAME:?Set exact disposable cluster name}"
EXPECTED="kind-${CLUSTER_NAME}"
command -v kubectl >/dev/null
ACTUAL="$(kubectl config current-context 2>/dev/null || true)"
[[ "$ACTUAL" == "$EXPECTED" ]] || {
  printf 'ERROR: expected=%q actual=%q; refusing operation\n' "$EXPECTED" "$ACTUAL" >&2
  exit 11
}
kubectl cluster-info >/dev/null
echo "Context guard passed: $EXPECTED"
```
```bash
# File: scripts/record-versions.sh
#!/usr/bin/env bash
set -euo pipefail
{
  date -u +recorded_at=%FT%TZ
  docker version
  kind version
  kubectl version --client -o yaml
  kubectl version -o yaml
  python3 --version
  make --version | head -n 1
} > versions.txt
mkdir -p evidence/versions
cp versions.txt "evidence/versions/versions-$(date -u +%Y%m%dT%H%M%SZ).txt"
```
```bash
# File: scripts/bootstrap.sh
#!/usr/bin/env bash
set -euo pipefail
export CLUSTER_NAME="${CLUSTER_NAME:-resilient-pipeline}"
command -v docker >/dev/null; command -v kind >/dev/null; command -v kubectl >/dev/null
docker info >/dev/null
FREE_KB="$(df -Pk . | awk 'NR==2 {print $4}')"
[[ "${FREE_KB:-0}" -ge 8000000 ]] || { echo "Need about 8 GB free disk" >&2; exit 20; }
EXPECTED="kind-${CLUSTER_NAME}"
if kind get clusters | grep -Fxq "$CLUSTER_NAME"; then
  [[ "$(kubectl config current-context 2>/dev/null || true)" == "$EXPECTED" ]] || {
    echo "Existing cluster; current context mismatch; refusing" >&2; exit 21;
  }
else
  kind create cluster --name "$CLUSTER_NAME" --config kind/cluster.yaml --wait 120s
fi
[[ "$(kubectl config current-context)" == "$EXPECTED" ]] || exit 22
kubectl get nodes -o wide | tee evidence-nodes.txt
./scripts/record-versions.sh
```
Example — yours will differ: node inventory should eventually show one control-plane and three Ready workers. A bootstrap failure requires inspection of `kind get clusters`, current context, Docker containers and Events; do not delete resources by broad pattern.
```bash
# File: scripts/down.sh
#!/usr/bin/env bash
set -euo pipefail
: "${CLUSTER_NAME:?Set exact disposable cluster name}"
EXPECTED="kind-${CLUSTER_NAME}"
ACTUAL="$(kubectl config current-context 2>/dev/null || true)"
[[ "$ACTUAL" == "$EXPECTED" ]] || { echo "Wrong context; refusing teardown" >&2; exit 31; }
printf 'Delete disposable cluster %s? Type exact name: ' "$CLUSTER_NAME"
read -r CONFIRM
[[ "$CONFIRM" == "$CLUSTER_NAME" ]] || { echo "Cancelled"; exit 32; }
kind delete cluster --name "$CLUSTER_NAME"
echo "Cluster deleted; host evidence retained."
```
Removing a kind cluster deletes its local cluster data. Evidence outside the cluster is intentionally retained. Do not manually remove kubeconfig contexts without understanding their ownership.

## Milestone 0 — Preflight and safety
**Estimate:** 2–3 hours. **Goal:** known disposable context and version record. Tasks: validate tools/Docker/disk; inspect topology; bootstrap; confirm four nodes; record versions; create evidence directories; explain kind limitations.

**Acceptance:** exact `kind-resilient-pipeline` context; four Ready nodes; versions captured; no secrets in evidence. If any check fails, stop before deploying.
```bash
# File: scripts/milestone0-checks.sh
#!/usr/bin/env bash
set -euo pipefail
export CLUSTER_NAME="${CLUSTER_NAME:-resilient-pipeline}"
./scripts/context-guard.sh
kubectl get nodes -o wide
kubectl get --raw='/readyz?verbose'
mkdir -p evidence/{preflight,versions,architecture,baseline,workloads,resource-sizing,drain-test,autoscaling,placement,security,upgrade-rehearsal,backup-restore,chaos,runbooks,conformance,results}
```

## Application implementation
### Design decision: PostgreSQL as a bounded stateful dependency
PostgreSQL provides transactions and uniqueness constraints for a small queue table and ETL ledger. It is a single local replica, not HA. Before production use, review concurrency, leases, stuck-processing recovery, indexes, pooling, backpressure, migrations, retention, TLS, authentication and backup. Resolve the actual image digest through M01's configured registry; never invent it.
```text
# File: requirements.txt
fastapi==0.115.12
uvicorn[standard]==0.34.0
psycopg[binary]==3.2.6
pytest==8.3.5
httpx==0.28.1
```
[VERIFY] These package pins are illustrative, not live-verified for currency or compatibility. Generate and review the project's actual lockfile before claiming reproducibility.
```python
# File: app/main.py
from __future__ import annotations
import json, os, time, uuid
from datetime import datetime, timezone
from contextlib import contextmanager
from typing import Any
import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://pipeline_app:example-password-do-not-use@postgres:5432/pipeline")
ROLE = os.environ.get("APP_ROLE", "api")
POLL_SECONDS = float(os.environ.get("POLL_SECONDS", "1"))
app = FastAPI(title="Resilient Pipeline Demo")

class ScoreRequest(BaseModel):
    record_id: str = Field(min_length=1, max_length=128)
    features: list[float] = Field(min_length=1, max_length=128)

def score(features: list[float]) -> float:
    """Transparent deterministic toy scoring; not model evaluation."""
    return round(sum(features) / len(features), 6)

@contextmanager
def connection():
    conn = psycopg.connect(DATABASE_URL, connect_timeout=3)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_schema() -> None:
    with connection() as conn, conn.cursor() as cur:
        cur.execute("""CREATE TABLE IF NOT EXISTS work_items (
          id TEXT PRIMARY KEY, record_id TEXT NOT NULL, payload JSONB NOT NULL,
          score DOUBLE PRECISION NOT NULL,
          status TEXT NOT NULL DEFAULT 'pending'
            CHECK (status IN ('pending','processing','done','failed')),
          created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          updated_at TIMESTAMPTZ NOT NULL DEFAULT now())""")
        cur.execute("""CREATE TABLE IF NOT EXISTS etl_rows (
          run_id TEXT NOT NULL, row_key TEXT NOT NULL, value DOUBLE PRECISION NOT NULL,
          created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          PRIMARY KEY (run_id,row_key))""")
        cur.execute("""CREATE TABLE IF NOT EXISTS etl_runs (
          run_id TEXT PRIMARY KEY, status TEXT NOT NULL,
          started_at TIMESTAMPTZ NOT NULL DEFAULT now(), finished_at TIMESTAMPTZ)""")

@app.on_event("startup")
def startup() -> None:
    if ROLE == "api":
        for attempt in range(8):
            try:
                init_schema()
                return
            except Exception as exc:
                print(json.dumps({"event":"schema_wait","attempt":attempt+1,"error_type":type(exc).__name__}))
                time.sleep(min(attempt + 1, 5))
        print('{"event":"schema_unavailable"}')
        # Keep process alive for diagnosis; readiness remains false.

@app.get("/healthz")
def healthz() -> dict[str,str]:
    # Liveness checks process responsiveness, not a transient DB dependency.
    return {"status":"alive"}

@app.get("/readyz")
def readyz() -> dict[str,str]:
    try:
        with connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        return {"status":"ready"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="dependency_unavailable") from exc

@app.get("/metrics-lite")
def metrics_lite() -> dict[str,int]:
    try:
        with connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM work_items WHERE status='pending'")
            return {"pending_work":cur.fetchone()[0]}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="dependency_unavailable") from exc

@app.post("/score")
def score_record(request: ScoreRequest) -> dict[str,Any]:
    result = score(request.features)
    item_id = str(uuid.uuid4())
    try:
        with connection() as conn, conn.cursor() as cur:
            cur.execute("INSERT INTO work_items(id,record_id,payload,score) VALUES(%s,%s,%s::jsonb,%s)",
                        (item_id, request.record_id, json.dumps(request.model_dump()), result))
        print(json.dumps({"event":"score_accepted","item_id":item_id,"record_id":request.record_id}))
        return {"item_id":item_id,"record_id":request.record_id,"score":result}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="write_unavailable") from exc

def run_worker_once() -> bool:
    # Demonstration only: production needs recovery for rows stuck in processing.
    with connection() as conn, conn.cursor() as cur:
        cur.execute("""SELECT id FROM work_items WHERE status='pending'
          ORDER BY created_at FOR UPDATE SKIP LOCKED LIMIT 1""")
        row = cur.fetchone()
        if row is None:
            return False
        cur.execute("UPDATE work_items SET status='processing',updated_at=now() WHERE id=%s",(row[0],))
        cur.execute("UPDATE work_items SET status='done',updated_at=now() WHERE id=%s",(row[0],))
        print(json.dumps({"event":"work_completed","item_id":row[0]}))
        return True

def run_etl(run_id: str, rows: int=10) -> int:
    with connection() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO etl_runs(run_id,status) VALUES(%s,'running') ON CONFLICT(run_id) DO NOTHING",(run_id,))
        cur.execute("SELECT status FROM etl_runs WHERE run_id=%s",(run_id,))
        status = cur.fetchone()[0]
        if status == "complete":
            cur.execute("SELECT count(*) FROM etl_rows WHERE run_id=%s",(run_id,))
            return cur.fetchone()[0]
        for i in range(rows):
            cur.execute("""INSERT INTO etl_rows(run_id,row_key,value) VALUES(%s,%s,%s)
              ON CONFLICT(run_id,row_key) DO UPDATE SET value=EXCLUDED.value""",
              (run_id,f"row-{i:04d}",round(i*1.25,3)))
        cur.execute("UPDATE etl_runs SET status='complete',finished_at=now() WHERE run_id=%s",(run_id,))
        cur.execute("SELECT count(*) FROM etl_rows WHERE run_id=%s",(run_id,))
        return cur.fetchone()[0]

def main() -> None:
    if ROLE == "worker":
        init_schema()
        while True:
            try:
                if not run_worker_once(): time.sleep(POLL_SECONDS)
            except Exception as exc:
                print(json.dumps({"event":"worker_error","error_type":type(exc).__name__}))
                time.sleep(min(POLL_SECONDS*2,10))
    elif ROLE == "etl":
        init_schema()
        run_id = os.environ.get("ETL_RUN_ID") or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        print(json.dumps({"event":"etl_complete","run_id":run_id,"row_count":run_etl(run_id,int(os.environ.get("ETL_ROWS","10")))}))
    else:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT","8080")))

if __name__ == "__main__":
    main()
```
```python
# File: app/tests/test_app.py
from app.main import score

def test_score_is_deterministic():
    assert score([1.0, 3.0]) == 2.0
    assert score([2.0, 2.0]) == 2.0

def test_empty_features_rejected():
    from pydantic import ValidationError
    from app.main import ScoreRequest
    try:
        ScoreRequest(record_id="r1", features=[])
    except ValidationError:
        return
    raise AssertionError("empty features should fail validation")

def test_etl_replay_integration():
    import os, pytest
    if not os.environ.get("TEST_DATABASE_URL"):
        pytest.skip("TEST_DATABASE_URL not configured; database idempotency remains unverified")
    import app.main as m
    old = m.DATABASE_URL
    m.DATABASE_URL = os.environ["TEST_DATABASE_URL"]
    try:
        m.init_schema()
        assert m.run_etl("fixed-replay-test",10) == 10
        assert m.run_etl("fixed-replay-test",10) == 10
        with m.connection() as c, c.cursor() as cur:
            cur.execute("SELECT count(*) FROM etl_rows WHERE run_id=%s",("fixed-replay-test",))
            assert cur.fetchone()[0] == 10
    finally:
        m.DATABASE_URL = old
```
```dockerfile
# File: Dockerfile
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
RUN useradd --create-home --uid 10001 appuser
USER 10001:10001
EXPOSE 8080
CMD ["python","-m","app.main"]
```
Build/test example (output is illustrative; yours will differ):
```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q app/tests
docker build -t resilient-pipeline:dev .
```
A skipped DB integration test is not a pass for idempotency. Run it against a disposable test database. Pin the Docker base image by a verified digest in the actual project, and publish/load the resulting image through the configured M01 registry workflow. Do not assume an unknown registry endpoint.

## Milestone 1 — Minimal end-to-end system
**Estimate:** 4–6 hours. Build the image, resolve digest, deploy PostgreSQL/API/worker, smoke-test health and data flow, then test ETL in a disposable database. **Acceptance:** API accepts one request, worker transitions work to done, ETL writes expected rows, and logs/evidence are saved.
```yaml
# File: manifests/00-namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: pipeline
  labels:
    app.kubernetes.io/part-of: resilient-data-pipeline
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
    # Pin enforce-version after verifying Kubernetes minor version:
    # pod-security.kubernetes.io/enforce-version: "vX.Y" # [VERIFY]
---
apiVersion: v1
kind: Namespace
metadata:
  name: pipeline-test
  labels:
    app.kubernetes.io/part-of: resilient-data-pipeline
    pod-security.kubernetes.io/enforce: restricted
```
```yaml
# File: manifests/01-governance.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: pipeline-quota
  namespace: pipeline
spec:
  hard:
    requests.cpu: "3"
    requests.memory: 3Gi
    limits.cpu: "5"
    limits.memory: 5Gi
    pods: "30"
    persistentvolumeclaims: "3"
---
apiVersion: v1
kind: LimitRange
metadata:
  name: pipeline-defaults
  namespace: pipeline
spec:
  limits:
  - type: Container
    defaultRequest: {cpu: 100m, memory: 128Mi}
    default: {cpu: 500m, memory: 512Mi}
    min: {cpu: 25m, memory: 32Mi}
    max: {cpu: "2", memory: 2Gi}
```
```yaml
# File: manifests/02-postgres.yaml
apiVersion: v1
kind: Service
metadata: {name: postgres, namespace: pipeline}
spec:
  selector: {app: postgres}
  ports:
  - {name: postgres, port: 5432, targetPort: postgres}
---
apiVersion: v1
kind: Secret
metadata: {name: postgres-demo-auth, namespace: pipeline}
type: Opaque
stringData:
  username: pipeline_app
  password: example-password-do-not-use
---
apiVersion: v1
kind: ServiceAccount
metadata: {name: postgres, namespace: pipeline}
automountServiceAccountToken: false
---
apiVersion: apps/v1
kind: StatefulSet
metadata: {name: postgres, namespace: pipeline}
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels: {app: postgres}
  template:
    metadata:
      labels: {app: postgres}
    spec:
      serviceAccountName: postgres
      automountServiceAccountToken: false
      securityContext:
        fsGroup: 999
        seccompProfile: {type: RuntimeDefault}
      containers:
      - name: postgres
        # Replace placeholder with digest verified from actual registry. Not runnable yet.
        image: postgres:16-alpine@sha256:REPLACE_WITH_VERIFIED_DIGEST
        ports: [{name: postgres, containerPort: 5432}]
        env:
        - {name: POSTGRES_DB, value: pipeline}
        - name: POSTGRES_USER
          valueFrom: {secretKeyRef: {name: postgres-demo-auth, key: username}}
        - name: POSTGRES_PASSWORD
          valueFrom: {secretKeyRef: {name: postgres-demo-auth, key: password}}
        resources:
          requests: {cpu: 200m, memory: 256Mi}
          limits: {cpu: "1", memory: 768Mi}
        securityContext:
          allowPrivilegeEscalation: false
          capabilities: {drop: ["ALL"]}
          runAsNonRoot: true
          runAsUser: 999
          runAsGroup: 999
          seccompProfile: {type: RuntimeDefault}
        startupProbe:
          exec: {command: ["sh","-c","pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB""]}
          periodSeconds: 5
          failureThreshold: 30
        readinessProbe:
          exec: {command: ["sh","-c","pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB""]}
          periodSeconds: 5
          timeoutSeconds: 2
          failureThreshold: 3
        livenessProbe:
          exec: {command: ["sh","-c","pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB""]}
          periodSeconds: 10
          timeoutSeconds: 2
          failureThreshold: 6
        volumeMounts: [{name: data, mountPath: /var/lib/postgresql/data}]
  volumeClaimTemplates:
  - metadata: {name: data}
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests: {storage: 1Gi}
```
**[VERIFY]** Confirm the exact PostgreSQL image's UID, writable directories, `fsGroup`, startup behavior and Restricted PSS compatibility. Do not weaken policy blindly if it fails. PVC persistence in kind is not a backup. The Secret contains only a fake demo value; do not commit real credentials. Production should use a proper secret manager/rotation and not inline credentials in a URL.
```yaml
# File: manifests/03-workloads.yaml
apiVersion: v1
kind: ServiceAccount
metadata: {name: pipeline-api, namespace: pipeline}
automountServiceAccountToken: false
---
apiVersion: v1
kind: ServiceAccount
metadata: {name: pipeline-worker, namespace: pipeline}
automountServiceAccountToken: false
---
apiVersion: v1
kind: ServiceAccount
metadata: {name: pipeline-batch, namespace: pipeline}
automountServiceAccountToken: false
---
apiVersion: apps/v1
kind: Deployment
metadata: {name: scoring-api, namespace: pipeline}
spec:
  replicas: 3
  selector:
    matchLabels: {app: scoring-api}
  template:
    metadata:
      labels: {app: scoring-api}
    spec:
      serviceAccountName: pipeline-api
      automountServiceAccountToken: false
      terminationGracePeriodSeconds: 30
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
        runAsGroup: 10001
        seccompProfile: {type: RuntimeDefault}
      containers:
      - name: api
        # Replace registry and digest using actual M01 workflow.
        image: registry.local/resilient-pipeline:dev@sha256:REPLACE_WITH_VERIFIED_DIGEST
        imagePullPolicy: IfNotPresent
        env:
        - {name: APP_ROLE, value: api}
        - {name: DATABASE_URL, value: postgresql://pipeline_app:example-password-do-not-use@postgres:5432/pipeline}
        - {name: PORT, value: "8080"}
        ports: [{name: http, containerPort: 8080}]
        resources:
          requests: {cpu: 100m, memory: 128Mi}
          limits: {cpu: 500m, memory: 384Mi}
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities: {drop: ["ALL"]}
          runAsNonRoot: true
          runAsUser: 10001
          runAsGroup: 10001
          seccompProfile: {type: RuntimeDefault}
        startupProbe:
          httpGet: {path: /healthz, port: http}
          periodSeconds: 5
          failureThreshold: 24
        readinessProbe:
          httpGet: {path: /readyz, port: http}
          periodSeconds: 5
          timeoutSeconds: 2
          failureThreshold: 3
        livenessProbe:
          httpGet: {path: /healthz, port: http}
          periodSeconds: 10
          timeoutSeconds: 2
          failureThreshold: 3
        lifecycle:
          preStop:
            exec: {command: ["sh","-c","sleep 5"]}
---
apiVersion: v1
kind: Service
metadata: {name: scoring-api, namespace: pipeline}
spec:
  selector: {app: scoring-api}
  ports: [{name: http, port: 80, targetPort: http}]
---
apiVersion: apps/v1
kind: Deployment
metadata: {name: queue-worker, namespace: pipeline}
spec:
  replicas: 1
  selector:
    matchLabels: {app: queue-worker}
  template:
    metadata:
      labels: {app: queue-worker}
    spec:
      serviceAccountName: pipeline-worker
      automountServiceAccountToken: false
      terminationGracePeriodSeconds: 20
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
        runAsGroup: 10001
        seccompProfile: {type: RuntimeDefault}
      containers:
      - name: worker
        image: registry.local/resilient-pipeline:dev@sha256:REPLACE_WITH_VERIFIED_DIGEST
        command: ["python","-m","app.main"]
        env:
        - {name: APP_ROLE, value: worker}
        - {name: DATABASE_URL, value: postgresql://pipeline_app:example-password-do-not-use@postgres:5432/pipeline}
        - name: POLL_SECONDS
          value: "1.0"
        resources:
          requests: {cpu: 100m, memory: 128Mi}
          limits: {cpu: 500m, memory: 384Mi}
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities: {drop: ["ALL"]}
          runAsNonRoot: true
          runAsUser: 10001
          runAsGroup: 10001
          seccompProfile: {type: RuntimeDefault}
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: {name: scoring-api-pdb, namespace: pipeline}
spec:
  minAvailable: 2
  selector:
    matchLabels: {app: scoring-api}
```
**Digest placeholders are intentionally non-runnable.** Replace `registry.local` only if M01 confirms that exact registry endpoint is reachable from kind nodes. Resolve real digests, validate manifests, then deploy. The API readiness check includes PostgreSQL because it cannot durably accept work without it; liveness checks process responsiveness to avoid cascading restarts. The sample `preStop` sleep is not a universal guarantee of zero dropped requests.

## Milestone 2 — Bounded and secure workloads
**Estimate:** 4–6 hours. Apply namespaces and governance first; verify PSS behavior against the actual Kubernetes version; use explicit ServiceAccounts; inspect all resource requests/limits, references and probes; record actual right-sizing observations only if Metrics Server is available.

Requests affect scheduling and CPU HPA utilization; CPU limits can throttle, memory limit breaches can cause OOM termination, quota can reject admission, and LimitRange defaults are guardrails—not measurements. Namespace isolation and quota are not complete security boundaries.
```yaml
# File: manifests/04-rbac.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata: {name: pipeline-auditor, namespace: pipeline}
rules:
- apiGroups: [""]
  resources: ["pods","services","events","persistentvolumeclaims"]
  verbs: ["get","list","watch"]
- apiGroups: ["apps"]
  resources: ["deployments","statefulsets","replicasets"]
  verbs: ["get","list","watch"]
- apiGroups: ["batch"]
  resources: ["jobs","cronjobs"]
  verbs: ["get","list","watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata: {name: pipeline-auditor, namespace: pipeline}
subjects:
- kind: ServiceAccount
  name: pipeline-batch
  namespace: pipeline
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: pipeline-auditor
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata: {name: pipeline-deployer, namespace: pipeline}
rules:
- apiGroups: ["apps"]
  resources: ["deployments","statefulsets"]
  verbs: ["get","list","watch","create","update","patch"]
- apiGroups: [""]
  resources: ["services","configmaps"]
  verbs: ["get","list","watch","create","update","patch"]
- apiGroups: ["batch"]
  resources: ["jobs","cronjobs"]
  verbs: ["get","list","watch","create","update","patch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata: {name: pipeline-deployer, namespace: pipeline}
subjects:
- kind: ServiceAccount
  name: pipeline-batch
  namespace: pipeline
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: pipeline-deployer
```
This is a namespace-scoped demonstration, not a complete enterprise identity model. Review whether the combined deployer/auditor bindings are too broad for the exercise. Runtime app ServiceAccounts need no RoleBinding because the app talks to PostgreSQL, not the Kubernetes API.
```yaml
# File: manifests/anti-pattern-admin.yaml
# ANTI-PATTERN — DO NOT COPY; do not apply to shared clusters.
apiVersion: v1
kind: ServiceAccount
metadata: {name: pipeline-admin, namespace: pipeline}
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata: {name: pipeline-admin-binding}
subjects:
- kind: ServiceAccount
  name: pipeline-admin
  namespace: pipeline
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
```
```bash
# File: scripts/audit-rbac.sh
#!/usr/bin/env bash
set -euo pipefail
CLUSTER_NAME="${CLUSTER_NAME:-resilient-pipeline}"
[[ "$(kubectl config current-context 2>/dev/null || true)" == "kind-${CLUSTER_NAME}" ]] || exit 51
kubectl -n pipeline get serviceaccounts,roles,rolebindings
for sa in pipeline-api pipeline-worker pipeline-batch; do
  echo "== $sa =="
  kubectl auth can-i --list --as="system:serviceaccount:pipeline:${sa}" -n pipeline
done
```
`--as` needs permission to impersonate the requested identity. A Forbidden result can indicate caller impersonation is not authorized; do not grant broad impersonation merely to make the audit pass. No Secret data should be listed.

## Milestone 3 — Resilience under disruption
**Estimate:** 4–7 hours. A PDB constrains certain voluntary evictions through the eviction API; it does not prevent involuntary failures. With three API replicas and `minAvailable: 2`, a drain may be blocked if capacity/topology cannot place replacements. Zero dropped requests is the target, not a promise; save actual request outcomes and interpret failures.
```bash
# File: scripts/load-test.sh
#!/usr/bin/env bash
set -euo pipefail
CLUSTER_NAME="${CLUSTER_NAME:-resilient-pipeline}"
[[ "$(kubectl config current-context 2>/dev/null || true)" == "kind-${CLUSTER_NAME}" ]] || exit 61
OUT="${1:-evidence/drain-test/requests.csv}"
mkdir -p "$(dirname "$OUT")"
LOG="$(mktemp)"
kubectl -n pipeline port-forward svc/scoring-api 18080:80 >"$LOG" 2>&1 &
PID=$!
trap 'kill "$PID" 2>/dev/null || true; rm -f "$LOG"' EXIT
for _ in $(seq 1 30); do curl -fsS http://127.0.0.1:18080/healthz >/dev/null 2>&1 && break; sleep 1; done
echo 'timestamp,request,status,elapsed_ms' > "$OUT"
for i in $(seq 1 300); do
  ts="$(date -u +%FT%TZ)"; start="$(date +%s%3N)"
  status="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 3     -X POST http://127.0.0.1:18080/score -H 'Content-Type: application/json'     -d "{"record_id":"drain-$i","features":[1,2,3]}" || echo CURL_ERROR)"
  end="$(date +%s%3N)"
  echo "$ts,$i,$status,$((end-start))" >> "$OUT"
  sleep 0.1
done
echo "Inspect non-2xx/CURL_ERROR counts, Pod events, endpoints and timeline."
```
```bash
# File: scripts/drain-worker.sh
#!/usr/bin/env bash
set -euo pipefail
CLUSTER_NAME="${CLUSTER_NAME:-resilient-pipeline}"
EXPECTED="kind-${CLUSTER_NAME}"
[[ "$(kubectl config current-context 2>/dev/null || true)" == "$EXPECTED" ]] || exit 62
NODE="${1:?Usage: scripts/drain-worker.sh <exact-worker-node-name>}"
kubectl get nodes -o wide
kubectl get node "$NODE" >/dev/null
echo "⚠ DESTRUCTIVE: drain exact disposable node $NODE. Inspect PDB and capacity first."
printf 'Type exact node name to continue: '; read -r CONFIRM
[[ "$CONFIRM" == "$NODE" ]] || { echo Cancelled; exit 63; }
kubectl cordon "$NODE"
kubectl drain "$NODE" --ignore-daemonsets --delete-emptydir-data --timeout=120s || {
  echo "Drain blocked/failed. Keep evidence; inspect PDB, capacity, Events. Do not force-delete by default." >&2
  exit 64
}
echo "Drain complete; keep cordoned until verification and explicit uncordon."
```
Before using drain, inspect the exact node names; adapt a strict allow-list to actual worker names rather than trusting arbitrary input. Capture PDB, readiness, Events, endpoints, placement and request CSV. If requests fail, inspect port-forward limitations, available replicas, readiness, capacity and shutdown behavior. Report the actual dropped-request count.

## Milestone 4 — Scaling and placement
**Estimate:** 3–6 hours. HPA scales Pods, not kind nodes. CPU utilization depends on requests and metrics availability. Verify the exact API server and Metrics Server compatibility; any kind-specific TLS/address workaround is development-only, not a production default.
```yaml
# File: manifests/05-hpa-pdb-placement.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata: {name: scoring-api, namespace: pipeline}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: scoring-api
  minReplicas: 3
  maxReplicas: 6
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 65
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0
    scaleDown:
      stabilizationWindowSeconds: 180
      policies:
      - type: Percent
        value: 25
        periodSeconds: 60
```
[VERIFY] Confirm `autoscaling/v2`, `behavior`, and metrics support in the actual cluster. Do not install an unverified Metrics Server command. Save HPA status, Events, replica timeline and metric availability; `<unknown>` means scaling has not been demonstrated.
```bash
# File: scripts/label-and-taint-workers.sh
#!/usr/bin/env bash
set -euo pipefail
CLUSTER_NAME="${CLUSTER_NAME:-resilient-pipeline}"
[[ "$(kubectl config current-context 2>/dev/null || true)" == "kind-${CLUSTER_NAME}" ]] || exit 71
mapfile -t NODES < <(kubectl get nodes -o name | sed 's#node/##' | grep -E "^${CLUSTER_NAME}-worker")
[[ "${#NODES[@]}" -eq 3 ]] || { echo "Expected three worker names; inspect manually" >&2; exit 72; }
kubectl label node "${NODES[0]}" pool=api --overwrite
kubectl label node "${NODES[1]}" pool=batch --overwrite
kubectl label node "${NODES[2]}" pool=stateful --overwrite
kubectl taint node "${NODES[1]}" workload=batch:NoSchedule --overwrite
echo "Labels/taint simulate policy; they do not create cloud node pools."
```
```bash
# File: scripts/verify-placement.sh
#!/usr/bin/env bash
set -euo pipefail
CLUSTER_NAME="${CLUSTER_NAME:-resilient-pipeline}"
[[ "$(kubectl config current-context 2>/dev/null || true)" == "kind-${CLUSTER_NAME}" ]] || exit 81
kubectl -n pipeline get pods -l app=scoring-api -o wide
COUNT="$(kubectl -n pipeline get pods -l app=scoring-api -o jsonpath='{range .items[*]}{.status.phase}{"\t"}{.spec.nodeName}{"\n"}{end}' |
  awk 'NF==2 && $1=="Running" {print $2}' | sort -u | wc -l | tr -d ' ')"
[[ "$COUNT" -ge 2 ]] || { echo "FAIL: fewer than two nodes host Running API Pods" >&2; exit 82; }
echo "PASS: two or more distinct nodes; readiness/topology constraints need separate review."
```
Hard node constraints can leave Pods Pending when CPU/memory, selectors, taints or topology rules are infeasible. Labels/taints simulate scheduling policy, not independent physical failure domains.

## Milestone 5 — Scheduled work, idempotency, backup boundaries, upgrade readiness
**Estimate:** 4–8 hours. The central data correctness rule is that retries/replays must not duplicate the intended business effect.
```yaml
# File: manifests/06-batch.yaml
apiVersion: batch/v1
kind: Job
metadata: {name: etl-manual-example, namespace: pipeline}
spec:
  backoffLimit: 2
  activeDeadlineSeconds: 300
  template:
    metadata:
      labels: {app: etl}
    spec:
      restartPolicy: Never
      serviceAccountName: pipeline-batch
      automountServiceAccountToken: false
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
        runAsGroup: 10001
        seccompProfile: {type: RuntimeDefault}
      containers:
      - name: etl
        image: registry.local/resilient-pipeline:dev@sha256:REPLACE_WITH_VERIFIED_DIGEST
        command: ["python","-m","app.main"]
        env:
        - {name: APP_ROLE, value: etl}
        - {name: DATABASE_URL, value: postgresql://pipeline_app:example-password-do-not-use@postgres:5432/pipeline}
        - {name: ETL_RUN_ID, value: manual-demo-run-001}
        resources:
          requests: {cpu: 100m, memory: 128Mi}
          limits: {cpu: 500m, memory: 384Mi}
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities: {drop: ["ALL"]}
          runAsNonRoot: true
          runAsUser: 10001
          runAsGroup: 10001
          seccompProfile: {type: RuntimeDefault}
---
apiVersion: batch/v1
kind: CronJob
metadata: {name: nightly-etl, namespace: pipeline}
spec:
  schedule: "0 2 * * *"
  concurrencyPolicy: Forbid
  startingDeadlineSeconds: 300
  successfulJobsHistoryLimit: 2
  failedJobsHistoryLimit: 3
  jobTemplate:
    spec:
      backoffLimit: 2
      activeDeadlineSeconds: 300
      template:
        metadata:
          labels: {app: etl}
        spec:
          restartPolicy: Never
          serviceAccountName: pipeline-batch
          automountServiceAccountToken: false
          securityContext:
            runAsNonRoot: true
            runAsUser: 10001
            runAsGroup: 10001
            seccompProfile: {type: RuntimeDefault}
          containers:
          - name: etl
            image: registry.local/resilient-pipeline:dev@sha256:REPLACE_WITH_VERIFIED_DIGEST
            command: ["python","-m","app.main"]
            env:
            - {name: APP_ROLE, value: etl}
            - {name: DATABASE_URL, value: postgresql://pipeline_app:example-password-do-not-use@postgres:5432/pipeline}
            # Demo replay key only; production needs distinct stable business-window IDs.
            - {name: ETL_RUN_ID, value: nightly-demo-run}
            resources:
              requests: {cpu: 100m, memory: 128Mi}
              limits: {cpu: 500m, memory: 384Mi}
            securityContext:
              allowPrivilegeEscalation: false
              readOnlyRootFilesystem: true
              capabilities: {drop: ["ALL"]}
              runAsNonRoot: true
              runAsUser: 10001
              runAsGroup: 10001
              seccompProfile: {type: RuntimeDefault}
```
**Important:** the fixed CronJob run ID is a demonstration of replay, not a valid distinct nightly partition strategy. For real scheduled processing derive a stable key from the intended UTC business window using a verified mechanism. Do not assume CronJob exposes a particular annotation or env substitution. Unique `(run_id,row_key)` protects the same logical run; it cannot fix an incorrect run ID or external side effects outside the transaction.
### Upgrade readiness and blue/green rehearsal
```bash
# File: scripts/api-scan.sh
#!/usr/bin/env bash
set -euo pipefail
# Heuristic only; use a maintained scanner and official release notes too.
if grep -RInE 'apiVersion: (extensions/v1beta1|apps/v1beta1|apps/v1beta2|networking.k8s.io/v1beta1|policy/v1beta1)' manifests; then
  echo "Review candidate deprecated APIs against target release" >&2
  exit 91
fi
echo "No patterns found; this does NOT prove APIs are current."
```
Go/no-go: record source/target versions and release notes; review skew policy, removed APIs, CRDs/operators/webhooks/CNI/CSI/ingress compatibility; confirm backups, restore evidence, PDB headroom, replicas/readiness and capacity; test rollback; canary a low-risk environment; abort on incompatibility, failed backups or health regressions. A fresh second kind cluster is a blue/green redeployment rehearsal, not an in-place control-plane upgrade. Never run kubeadm upgrade commands against kind.
### etcd backup and restore
An etcd snapshot, Kubernetes object export, PostgreSQL application backup, PV backup and managed-service recovery are different. An etcd snapshot does not itself back up the PostgreSQL PVC. Store snapshots outside the cluster/container being recovered and verify integrity. Restore commands depend on actual etcd version, topology, endpoints, certificates and kind node image. If the exact supported restore method cannot be established from current documentation and inspection, keep the restore as a human-reviewed non-destructive plan; do not guess paths or restore flags and never overwrite the active cluster as a first test.
```bash
# File: scripts/backup-plan.sh
#!/usr/bin/env bash
set -euo pipefail
CLUSTER_NAME="${CLUSTER_NAME:-resilient-pipeline}"
[[ "$(kubectl config current-context 2>/dev/null || true)" == "kind-${CLUSTER_NAME}" ]] || exit 101
mkdir -p evidence/backup-restore
{
  date -u +recorded_at=%FT%TZ
  kubectl config current-context
  kind get clusters
  kubectl get nodes -o wide
  kubectl -n pipeline get statefulsets,pods,pvc -o wide
  echo "Inventory only: this is not an etcd snapshot or PV backup."
} | tee evidence/backup-restore/pre-restore-inventory.txt
```

## Milestone 6 — Game day, audit, and portfolio evidence
**Estimate:** 5–8 hours. Run one fault at a time. Every drill requires a context guard, exact target, preconditions, written hypothesis, explicit confirmation, baseline evidence, action, observation, recovery, cleanup and a reflection. Never auto-run the full suite.
### Drill 1 — Kill one API Pod
**Hypothesis:** Deployment should replace it; Service availability depends on remaining Ready endpoints and capacity.

**Evidence:** Capture Pod UID, readiness, restart/events, request outcomes and recovery time.

**Bounded action:** Delete one exact scoring-api Pod only after context guard and typed confirmation.

**Guard:** exact `kind-resilient-pipeline` context, inspect target and health, then typed confirmation of exact target.

**Recovery/cleanup:** restore the original replica/spec or uncordon the exact node only after inspection; verify Ready Pods, API health and data correctness; confirm temporary objects are gone. Save actual result under `evidence/chaos/`. Use `BLOCKED` if unsafe or unsupported.
### Drill 2 — Kill worker Pod
**Hypothesis:** Deployment should replace it; unfinished work must remain recoverable/idempotent.

**Evidence:** Capture worker logs, backlog and any stuck processing rows.

**Bounded action:** Delete one selected worker Pod; inspect database state before repeating.

**Guard:** exact `kind-resilient-pipeline` context, inspect target and health, then typed confirmation of exact target.

**Recovery/cleanup:** restore the original replica/spec or uncordon the exact node only after inspection; verify Ready Pods, API health and data correctness; confirm temporary objects are gone. Save actual result under `evidence/chaos/`. Use `BLOCKED` if unsafe or unsupported.
### Drill 3 — Drain worker node
**Hypothesis:** PDB/capacity constrain voluntary eviction; request success is measured, not assumed.

**Evidence:** Capture request CSV, PDB, Events, node/pod timeline.

**Bounded action:** Use guarded drain script and exact disposable node.

**Guard:** exact `kind-resilient-pipeline` context, inspect target and health, then typed confirmation of exact target.

**Recovery/cleanup:** restore the original replica/spec or uncordon the exact node only after inspection; verify Ready Pods, API health and data correctness; confirm temporary objects are gone. Save actual result under `evidence/chaos/`. Use `BLOCKED` if unsafe or unsupported.
### Drill 4 — Make PostgreSQL unavailable
**Hypothesis:** API readiness should fail; liveness should not restart API solely for DB outage.

**Evidence:** Capture readiness, restart count, DB events, HTTP responses and recovery.

**Bounded action:** Only after confirmation scale StatefulSet to zero; restore replica immediately after evidence.

**Guard:** exact `kind-resilient-pipeline` context, inspect target and health, then typed confirmation of exact target.

**Recovery/cleanup:** restore the original replica/spec or uncordon the exact node only after inspection; verify Ready Pods, API health and data correctness; confirm temporary objects are gone. Save actual result under `evidence/chaos/`. Use `BLOCKED` if unsafe or unsupported.
### Drill 5 — Exhaust test quota
**Hypothesis:** Admission should reject an object exceeding quota.

**Evidence:** Capture quota status, create rejection, Events and cleanup.

**Bounded action:** Use pipeline-test namespace; create bounded objects and stop after first rejection.

**Guard:** exact `kind-resilient-pipeline` context, inspect target and health, then typed confirmation of exact target.

**Recovery/cleanup:** restore the original replica/spec or uncordon the exact node only after inspection; verify Ready Pods, API health and data correctness; confirm temporary objects are gone. Save actual result under `evidence/chaos/`. Use `BLOCKED` if unsafe or unsupported.
### Drill 6 — Remove required toleration
**Hypothesis:** Pod constrained to tainted node should remain Pending if no eligible node exists.

**Evidence:** Capture scheduler Events, taint, Pod spec and placement after fix.

**Bounded action:** Use isolated test manifest; restore toleration and remove temporary objects.

**Guard:** exact `kind-resilient-pipeline` context, inspect target and health, then typed confirmation of exact target.

**Recovery/cleanup:** restore the original replica/spec or uncordon the exact node only after inspection; verify Ready Pods, API health and data correctness; confirm temporary objects are gone. Save actual result under `evidence/chaos/`. Use `BLOCKED` if unsafe or unsupported.

## Conformance verification and Makefile
```bash
# File: scripts/conformance.sh
#!/usr/bin/env bash
set -euo pipefail
CLUSTER_NAME="${CLUSTER_NAME:-resilient-pipeline}"
EXPECTED="kind-${CLUSTER_NAME}"
ACTUAL="$(kubectl config current-context 2>/dev/null || true)"
[[ "$ACTUAL" == "$EXPECTED" ]] || { echo "FAIL context"; exit 111; }
mkdir -p evidence/conformance
REPORT="evidence/conformance/report-$(date -u +%Y%m%dT%H%M%SZ).txt"
FAIL=0
check() {
  local label="$1"; shift
  if "$@"; then echo "PASS $label" | tee -a "$REPORT"
  else echo "FAIL $label" | tee -a "$REPORT"; FAIL=1; fi
}
check "namespace" kubectl get namespace pipeline
check "API deployment" kubectl -n pipeline get deployment scoring-api
check "worker deployment" kubectl -n pipeline get deployment queue-worker
check "Postgres StatefulSet" kubectl -n pipeline get statefulset postgres
check "PDB" kubectl -n pipeline get pdb scoring-api-pdb
check "quota" kubectl -n pipeline get resourcequota pipeline-quota
check "LimitRange" kubectl -n pipeline get limitrange pipeline-defaults
check "CronJob" kubectl -n pipeline get cronjob nightly-etl
check "API rollout" kubectl -n pipeline rollout status deployment/scoring-api --timeout=30s
check "worker rollout" kubectl -n pipeline rollout status deployment/queue-worker --timeout=30s
echo "MANUAL REVIEW OPEN: digests, non-root/PSS, RBAC least privilege, ETL replay, drain loss, HPA, backup/restore, upgrades, cleanup" | tee -a "$REPORT"
if [[ "$FAIL" -ne 0 ]]; then echo "OVERALL FAIL: $REPORT"; exit 1; fi
echo "AUTOMATED CHECKS PASS; MANUAL REVIEW OPEN: $REPORT" | tee -a "$REPORT"
```
```makefile
# File: Makefile
SHELL := /usr/bin/env bash
.SHELLFLAGS := -euo pipefail -c
CLUSTER_NAME ?= resilient-pipeline
.PHONY: up deploy verify chaos backup restore-test down
up:
	CLUSTER_NAME="$(CLUSTER_NAME)" ./scripts/bootstrap.sh
deploy:
	CLUSTER_NAME="$(CLUSTER_NAME)" ./scripts/context-guard.sh
	kubectl apply -f manifests/00-namespace.yaml
	kubectl apply -f manifests/01-governance.yaml
	kubectl apply -f manifests/02-postgres.yaml
	kubectl apply -f manifests/03-workloads.yaml
	kubectl apply -f manifests/04-rbac.yaml
	kubectl apply -f manifests/06-batch.yaml
	kubectl apply -f manifests/05-hpa-pdb-placement.yaml
verify:
	CLUSTER_NAME="$(CLUSTER_NAME)" ./scripts/conformance.sh
chaos:
	@echo "Select one individually guarded drill; this target does not run chaos automatically."
backup:
	CLUSTER_NAME="$(CLUSTER_NAME)" ./scripts/backup-plan.sh
restore-test:
	@echo "HUMAN-GATED: validate exact etcd restore method and isolated target before any destructive action."
down:
	CLUSTER_NAME="$(CLUSTER_NAME)" ./scripts/down.sh
```
Manifests must have registry/digest placeholders replaced before deployment. The HPA object may fail if metrics/API support is absent. `restore-test` intentionally does not execute a guessed destructive procedure. `make verify` reports object/rollout checks separately from manual review; object existence does not prove data correctness or runtime security.

## Five incident runbooks
### Runbook 1 — CrashLoopBackOff storm
**Severity/impact:** classify from actual customer/service impact.

**Symptoms and immediate safety:** SEV based on customer impact. Capture `describe`, current and `--previous` logs, Events, termination reason, image digest, resources and probes. Branch: process exception, bad config, OOMKilled, failed probe, filesystem/UID mismatch or dependency. Preserve evidence; stop rollout/rollback to known-good digest only after review. Verify Ready replicas and request/data correctness. Prevent with startup budgets, probe review and staged rollout.

**Diagnostic baseline:** `kubectl get pods -A -o wide`; `kubectl describe` the exact object; `kubectl get events --sort-by=.metadata.creationTimestamp`; inspect relevant logs including `kubectl logs <pod> -c <container> --previous` where applicable. Add only commands for the confirmed target.

**Decision / recovery / verification:** preserve UTC timeline and output; choose the lowest-risk mitigation supported by evidence; define rollback/stop condition; verify health and data correctness; record prevention, escalation owner and evidence path. Redact credentials, Secret data, kubeconfig and private endpoints.
### Runbook 2 — Stuck node drain
**Severity/impact:** classify from actual customer/service impact.

**Symptoms and immediate safety:** Inspect exact context/node, PDB `disruptionsAllowed`, replicas, readiness, topology, quota, capacity, finalizers and termination hooks. Do not force-delete by default. Determine whether PDB blocks eviction or replacement Pods cannot schedule; add safe capacity or change maintenance plan. Verify workloads healthy and node state intentional. Prevent with maintenance rehearsal and disruption-budget review.

**Diagnostic baseline:** `kubectl get pods -A -o wide`; `kubectl describe` the exact object; `kubectl get events --sort-by=.metadata.creationTimestamp`; inspect relevant logs including `kubectl logs <pod> -c <container> --previous` where applicable. Add only commands for the confirmed target.

**Decision / recovery / verification:** preserve UTC timeline and output; choose the lowest-risk mitigation supported by evidence; define rollback/stop condition; verify health and data correctness; record prevention, escalation owner and evidence path. Redact credentials, Secret data, kubeconfig and private endpoints.
### Runbook 3 — ResourceQuota admission block
**Severity/impact:** classify from actual customer/service impact.

**Symptoms and immediate safety:** Capture rejected create/update, quota usage, LimitRange defaults and requested resources. Identify hard quota exhaustion, defaults, or object count. Reduce requests only if measurement supports it; otherwise seek approved quota/capacity change. Verify admission and workload health. Prevent with quota alerts and sizing reports.

**Diagnostic baseline:** `kubectl get pods -A -o wide`; `kubectl describe` the exact object; `kubectl get events --sort-by=.metadata.creationTimestamp`; inspect relevant logs including `kubectl logs <pod> -c <container> --previous` where applicable. Add only commands for the confirmed target.

**Decision / recovery / verification:** preserve UTC timeline and output; choose the lowest-risk mitigation supported by evidence; define rollback/stop condition; verify health and data correctness; record prevention, escalation owner and evidence path. Redact credentials, Secret data, kubeconfig and private endpoints.
### Runbook 4 — HPA runaway/thrashing
**Severity/impact:** classify from actual customer/service impact.

**Symptoms and immediate safety:** Capture HPA status/events, metrics, requests, CPU throttling, replicas, latency and node pressure. Check missing metrics/requests, stabilization, capacity, downstream bottlenecks and wrong signal. Change one setting at a time. Verify replica trajectory and error/latency over an agreed window. Prevent with load tests and capacity guardrails.

**Diagnostic baseline:** `kubectl get pods -A -o wide`; `kubectl describe` the exact object; `kubectl get events --sort-by=.metadata.creationTimestamp`; inspect relevant logs including `kubectl logs <pod> -c <container> --previous` where applicable. Add only commands for the confirmed target.

**Decision / recovery / verification:** preserve UTC timeline and output; choose the lowest-risk mitigation supported by evidence; define rollback/stop condition; verify health and data correctness; record prevention, escalation owner and evidence path. Redact credentials, Secret data, kubeconfig and private endpoints.
### Runbook 5 — etcd restore/control-plane recovery
**Severity/impact:** classify from actual customer/service impact.

**Symptoms and immediate safety:** Treat as high severity by actual impact. Stop ad-hoc mutations; identify managed/self-managed control plane, exact etcd topology/version, quorum, members, snapshot, certificates and recovery authority. Use only provider-supported or version-matched official procedure in an isolated target. Never guess paths or overwrite the only copy. Verify API/control plane, object reconciliation, application data and PV data separately; measure actual RTO. If procedure is not verified, escalate and leave restore OPEN.

**Diagnostic baseline:** `kubectl get pods -A -o wide`; `kubectl describe` the exact object; `kubectl get events --sort-by=.metadata.creationTimestamp`; inspect relevant logs including `kubectl logs <pod> -c <container> --previous` where applicable. Add only commands for the confirmed target.

**Decision / recovery / verification:** preserve UTC timeline and output; choose the lowest-risk mitigation supported by evidence; define rollback/stop condition; verify health and data correctness; record prevention, escalation owner and evidence path. Redact credentials, Secret data, kubeconfig and private endpoints.

## Architecture Decision Records (ADRs)
### ADR-001 — PostgreSQL database-backed queue
Options: broker+DB, database queue, in-memory. Choose database tables to reduce local components and demonstrate transactions/idempotency. Trade-off: simple but limited throughput and single-replica dependency. Revisit for scale, fan-out or delivery guarantees.
### ADR-002 — Shared image with role modes
Options: separate images or shared image with `APP_ROLE`. Choose shared image for teaching simplicity. Trade-off: coupled release/dependencies and larger image. Split when privileges, release cadence or dependency sets diverge.
### ADR-003 — Probe separation
Options: dependency-aware liveness or process liveness + dependency-aware readiness. Choose the latter to avoid cascading restarts. Trade-off: process may remain alive while unready. Revisit if degraded mode/local buffering is implemented.
### ADR-004 — Three API replicas and PDB
Options: one replica, two/minAvailable 1, three/minAvailable 2. Choose three/minAvailable 2 subject to capacity. Trade-off: more resources; PDB can block drains and does not prevent involuntary failures. Revisit with measured capacity/SLO.
### ADR-005 — ETL unique run and row keys
Options: scheduler-only control, application idempotency, unsupported exactly-once claim. Choose unique DB key and transaction. Protects same-run writes but not external side effects or wrong run IDs. Revisit when sinks/partitions change.
### ADR-006 — kind for local operations
Options: managed cluster or kind. Choose kind for zero-budget practice. Trade-off: no cloud HA/load balancer/provider recovery proof. Revisit when production target is known.
### ADR-007 — digest-pinned images
Options: mutable tag or verified digest. Choose digest after registry resolution. Trade-off: explicit digest management needed. Revisit when signing/attestation policy is defined.
### ADR-008 — human-gated etcd restore
Options: guessed command, verified isolated procedure, documented blocker. Choose no destructive restore until topology/version/access are verified. Trade-off: DR acceptance remains OPEN until drill. Revisit after human-reviewed procedure.

## Before/after measurements and results
| Measure | Baseline | After | Method/evidence | Status |
| --- | --- | --- | --- | --- |
| Availability during drain | Not measured | Not measured | Request CSV, status counts, PDB/Events/timeline | OPEN |
| Recovery after Pod/node loss | Not measured | Not measured | Failure and first sustained healthy response timestamps | OPEN |
| HPA scale-up/down time | Not measured | Not measured | HPA Events, replica timeline, metrics | OPEN |
| etcd restore RTO | Not measured | Not measured | Only after human-approved isolated restore | OPEN |
| Resource utilization/waste | Not measured | Not measured | `kubectl top` if metrics available | OPEN |
| Pods without limits | Not measured | Not measured | Inspect all containers and init containers | OPEN |
| ETL duplicate effect | Not measured | Not measured | Query row count by exact run_id before/after replay | OPEN |
A target RTO is a planning objective. Measured RTO is elapsed time to verified recovery. Never populate this table with invented results.

## Acceptance criteria and definition of done
| Area | Observable criterion | Verification |
| --- | --- | --- |
| Safety | Every mutation has exact context guard and per-drill confirmation; teardown exact cluster. | Script + human review |
| Bootstrap | Four nodes Ready; versions/context recorded. | Actual output |
| Workloads | API, worker, PostgreSQL, ETL Job, CronJob references and SAs correct. | Rollout and object review |
| Security | Non-root, no privilege escalation, dropped capabilities, seccomp, resources, PSS/RBAC reviewed. | Admission/audit evidence |
| Health | Readiness/liveness differ; dependency outage does not cause avoidable liveness storm. | Fault test |
| Data correctness | Same-run replay has intended unique row count; retry/partial failure analyzed. | DB integration test |
| Governance | Quota/LimitRange behavior and right-sizing evidence recorded. | Test + measurements |
| Disruption | Drain outcomes captured; zero dropped requests target is measured honestly. | Load evidence |
| Autoscaling | Metrics, HPA events, limits and kind node-scaling gap documented. | Timeline |
| Placement | Verifier checks distinct-node placement and limitations. | Script + review |
| Upgrade | API scan and go/no-go runbook cover skew, add-ons, backup and abort. | Manual review |
| Recovery | Safe restore evidence or documented blocker with human-reviewed plan. | OPEN unless proven |
| Game day | Six drills separately documented, recovered and cleaned. | Evidence review |
| Conformance | Automated pass/fail is separate from manual checks. | `make verify` output |
| Documentation | Diagram, ADRs, runbooks, measurements, coverage, claim register, audit present. | Review |
| Cleanup | Temporary resources gone; intended evidence retained. | Post-cleanup check |

## 100-point grading rubric
| Area | Pts | Poor | Adequate | Strong | Exemplary |
| --- | --- | --- | --- | --- | --- |
| Architecture/correctness | 12 | Disconnected roles | Basic flow | Verified flow | Failure boundaries reasoned |
| Workloads/idempotency | 14 | Missing roles/unsafe replay | Workloads run | Replay/retry proven | Partial failure/external side effects analyzed |
| Resource governance | 10 | No bounds | Basic limits | Quota + sizing evidence | Fairness/capacity trade-offs measured |
| Resilience/shutdown | 12 | No drain evidence | Basic PDB/drain | Request outcomes captured | Failure/rollback limits analyzed |
| Autoscaling/placement | 8 | Assertions only | Basic attempt | Metrics and placement evidence | Thrashing/capacity trade-offs justified |
| Security | 12 | Privileged/broad RBAC | Basic hardening | PSS/RBAC checks | Threat boundaries and secrets reviewed |
| Recovery/upgrades | 10 | No plan | Untested runbook | Compatibility and safe plan | Isolated recovery evidence and RPO/RTO reasoning |
| Verification/observability | 8 | No checks | Basic smoke test | Pass/fail evidence | Automated/manual and uncertainty distinguished |
| Docs/evidence | 8 | Missing artifacts | Most artifacts | Coherent artifacts | Reproducible, redacted portfolio |
| Safety/cleanup | 6 | Unsafe target/no cleanup | Partial guards | All drills guarded | Fail-closed automation |
Passing threshold: 80/100 **and no failed safety gate**. Wrong-context mutation, unconfirmed destructive action, published secrets, or unverified destructive restore fails the safety gate regardless of points. This score does not prove production readiness.

## Common failure modes and troubleshooting decision trees
| Symptom | Evidence first | Possible branches | Safe action |
| --- | --- | --- | --- |
| Pod Pending | Describe, Events, requests, quota, labels/taints, PVC | Capacity, affinity, taint, quota, PVC | Fix demonstrated constraint; don't remove all placement rules |
| ImagePullBackOff | Exact image/digest and Pod Events | Wrong registry, missing digest, auth, image not loaded | Use configured M01 workflow; no guessed digest |
| CrashLoopBackOff | Previous logs, termination reason, probes, resources, volume | App error, OOM, probe, UID/permissions | Preserve evidence; fix cause or reviewed rollback |
| Readiness fail/liveness OK | Ready endpoint, DB events, config | DB down, auth/config mismatch | Repair dependency; avoid liveness coupling |
| HPA unknown | HPA describe, metrics API, requests | Metrics missing, requests absent, API mismatch | Verify metrics path; don't claim scaling tested |
| Drain blocked | PDB, capacity, placement, quota, finalizers | PDB, no destination, hook/finalizer | Do not force-delete by default |
| Quota rejection | Admission response, quota usage, defaults | Quota full, default request, object count | Measured request or approved quota change |
| ETL duplicate/partial | run_id, row keys, transaction and Job logs | Wrong run ID, external side effect, missing unique key | Stable idempotency key and replay test |
| PVC stuck | PVC/PV/StorageClass events | No provisioner, placement/storage mismatch | Verify kind storage path; don't delete PVC first |
| Forbidden | Exact verb/resource/scope, authorized `can-i` | RBAC, auth, admission, impersonation | Reviewed least-privilege binding |

## Evidence directory and portfolio-safe submission
```text
evidence/
  preflight/ versions/ architecture/ baseline/ workloads/
  resource-sizing/ drain-test/ autoscaling/ placement/
  security/ upgrade-rehearsal/ backup-restore/ chaos/
  runbooks/ conformance/ results/
```
Every evidence item records UTC timestamp, exact context, namespace/object, command/test version, expected result, actual result, status (`PASS`, `FAIL`, `BLOCKED`, `SKIPPED`), path and notes. Redact kubeconfig, tokens, Secret values, personal data, private endpoints and unnecessary cluster detail. Do not dump Secrets or all environment variables.

## Kind-versus-production fidelity matrix
| Topic | kind can test | kind cannot prove |
| --- | --- | --- |
| API/controllers | Local schema/admission/reconciliation/rollout | Managed control-plane HA |
| Drain/node failure | Eviction, scheduling, replica replacement | Real zone/physical failure or cloud LB |
| Node pools | Labels, taints, selectors, spread | Cloud autoscaling groups or physical domains |
| Storage | PVC behavior with configured local provisioner | Cloud durability, replication, storage SLA |
| HPA | Pod scaling if metrics works | Node autoscaling or production cost/latency |
| etcd | Potential isolated rehearsal after verified access | Managed-service DR semantics |
| Security | RBAC/PSS/Service/namespace behavior | Complete tenant isolation or enterprise perimeter |
| SLO | This exact local test result | Production SLO attainment |

## Cleanup and reset procedure
```bash
# File: scripts/cleanup-test-resources.sh
#!/usr/bin/env bash
set -euo pipefail
CLUSTER_NAME="${CLUSTER_NAME:-resilient-pipeline}"
[[ "$(kubectl config current-context 2>/dev/null || true)" == "kind-${CLUSTER_NAME}" ]] || exit 121
kubectl -n pipeline get pods,jobs,cronjobs,pvc,pdb,hpa
echo "Inspect exact temporary Job names before deletion; no wildcard cleanup is automatic."
kubectl -n pipeline get jobs -o name
printf 'Type CLEANUP to continue after reviewing labels and names: '
read -r CONFIRM
[[ "$CONFIRM" == CLEANUP ]] || { echo Cancelled; exit 122; }
kubectl -n pipeline delete jobs -l app=etl --ignore-not-found
echo "Inspect remaining resources; cluster teardown is separate."
```
Inspect labels before cleanup because they can vary during edits. Preserve evidence intentionally. For final teardown use the guarded exact-name script, then verify the cluster is absent. Avoid `kubectl delete all` and wildcard context matching.

## Stretch goals (bounded)
- Add structured JSON logs and request/run correlation IDs.
- Add a lease/outbox design and simulate worker crash between claim and side effect.
- Add NetworkPolicy only after verifying kind CNI enforcement.
- Add Prometheus only if resources permit and images/versions are pinned.
- Explore VPA recommendation-only mode after checking HPA compatibility.
- Add SBOM/signing/attestation and protected promotion from M02.

## Self-review checklist and learner reflection
- [ ] Every mutation used exact context guard.
- [ ] Image digests are actual, verified values.
- [ ] Readiness and liveness have distinct purposes.
- [ ] Same-run ETL replay verified intended row count.
- [ ] Drain request outcomes were measured, not assumed.
- [ ] PDB limitations are understood.
- [ ] HPA metrics and Pod-vs-node scaling distinction are documented.
- [ ] Application ServiceAccounts have no unnecessary API permissions.
- [ ] No Secret data or kubeconfig was published.
- [ ] etcd restore is safely verified or explicitly OPEN.
- [ ] Evidence distinguishes PASS/FAIL/BLOCKED/SKIPPED.
- [ ] Cleanup was verified and evidence retained.
Reflection: What evidence changed your initial hypothesis? Which control reduced risk versus only improved visibility? Which local result must not be extrapolated to production? What unresolved item has the largest blast radius?

## Content coverage matrix — M03 Units 1–11
| Unit | Sections | Lab/check | Evidence |
| --- | --- | --- | --- |
| 1 Architecture/control plane | Architecture, preflight, fidelity | Bootstrap/readiness | Versions and node inventory |
| 2 Namespace/quota/limits | Governance and quota runbook | Quota rejection | Quota usage and sizing |
| 3 Probes/recovery | Health endpoints, probe design, CrashLoop runbook | DB outage drill | Probe/restart/readiness timeline |
| 4 Controllers/Jobs/CronJobs | Deployment/StatefulSet/Job/CronJob manifests | ETL replay | Rollout, Job history, query |
| 5 PDB/shutdown | PDB and drain procedures | Drain/load test | PDB, request CSV, timeline |
| 6 Autoscaling | HPA and observations | Load/scaling experiment | Metrics/HPA timeline |
| 7 Placement | Labels/taints/verifier | Missing toleration drill | Placement and scheduler Events |
| 8 Upgrade compatibility | API scan/go-no-go | Optional blue/green | Version matrix and decision |
| 9 RBAC/PSS | ServiceAccounts/RBAC/anti-pattern | Security review | Audit/admission evidence |
| 10 etcd/recovery | Backup boundary/runbook | Human-gated restore | Snapshot evidence or OPEN blocker |
| 11 Troubleshooting | Decision trees and six drills | Game day | Events/logs/timeline |

## Appendix A — Claim and source register
Source status: roadmap-tree variants, M03 syllabus-generation prompt and Unit 1–11 lesson files were available locally. Official documentation URLs below are authoritative starting points but were not live-checked during this authoring pass. Version-sensitive claims remain `[VERIFY]`.
| ID | Claim/design | Section | Source type | Source/document section | Version-sensitive? | Status |
| --- | --- | --- | --- | --- | --- | --- |
| C01 | Control-plane and worker responsibilities differ | Architecture | Lesson + official docs | Unit 1; cluster architecture | No | [VERIFY] |
| C02 | Controllers reconcile desired/observed state | Architecture | Lesson + official docs | Unit 1; controllers | No | [VERIFY] |
| C03 | kind does not prove managed production HA | Scope | Inference + kind docs | kind overview | No | Design limit |
| C04 | Requests affect scheduling; CPU limits can throttle | Resources | Lesson + official docs | Unit 2; resource management | Context-sensitive | [VERIFY] |
| C05 | Memory pressure/limit may result in OOM termination | Resources | Lesson + official docs | Unit 2; resource management | Environment-sensitive | [VERIFY] |
| C06 | ResourceQuota can reject admission | Quota | Lesson + official docs | Unit 2; quota docs | No | [VERIFY] |
| C07 | LimitRange defaults are guardrails, not sizing measurement | Quota | Lesson + inference | Unit 2; LimitRange | No | Design rationale |
| C08 | Readiness and liveness serve different purposes | Probes | Lesson + official docs | Unit 3; probe docs | Fields version-sensitive | [VERIFY] |
| C09 | Startup probe can gate other probe behavior | Probes | Lesson + official docs | Unit 3; probe docs | Yes | [VERIFY] |
| C10 | Dependency-aware liveness can amplify outage | Probes | Inference | Unit 3; probe design | No | Test locally |
| C11 | Deployment selector must match Pod labels | Workloads | Lesson + official docs | Unit 4; Deployment | No | [VERIFY] |
| C12 | StatefulSet identity/storage differs from Deployment | Workloads | Lesson + official docs | Unit 4; StatefulSet | Provisioner-specific | [VERIFY] |
| C13 | Job/CronJob do not guarantee exactly-once business effect | Batch | Lesson + inference | Unit 4; Jobs/CronJobs | Behavior context | [VERIFY] |
| C14 | Forbid constrains overlapping Jobs from one CronJob | Batch | Official docs + inference | CronJob docs | Yes | [VERIFY] |
| C15 | PDB constrains some voluntary evictions, not involuntary failure | Resilience | Lesson + official docs | Unit 5; PDB | Context-sensitive | [VERIFY] |
| C16 | Graceful shutdown requires application behavior too | Resilience | Lesson + inference | Unit 5; termination | Implementation-specific | Test |
| C17 | HPA CPU utilization needs metrics and resource requests | HPA | Lesson + official docs | Unit 6; HPA | Yes | [VERIFY] |
| C18 | HPA scales Pods, not kind nodes | HPA | Lesson + inference | Unit 6; kind | No | [VERIFY setup] |
| C19 | Taints/tolerations and affinity affect scheduling feasibility | Placement | Lesson + official docs | Unit 7; scheduling | No | [VERIFY] |
| C20 | Kind labels/taints do not create cloud node pools | Placement | Inference | Unit 7; kind | No | Design limit |
| C21 | Version skew/deprecation needs actual target/source versions | Upgrade | Lesson + official docs | Unit 8; release policy | Yes | [VERIFY] |
| C22 | Fresh kind cluster is not an in-place managed upgrade | Upgrade | Inference | Unit 8; kind | No | Design limit |
| C23 | Authentication, authorization and admission differ | Security | Lesson + official docs | Unit 9; authn/authz | No | [VERIFY] |
| C24 | RBAC bindings scope permissions to subjects and scope | Security | Lesson + official docs | Unit 9; RBAC | No | [VERIFY] |
| C25 | PSS label level/version must match target baseline | Security | Lesson + official docs | Unit 9; PSS | Yes | [VERIFY] |
| C26 | etcd snapshot alone is not a PV/application data backup | Recovery | Lesson + inference | Unit 10; backups | Topology-specific | [VERIFY] |
| C27 | etcd restore commands depend on exact topology/version/access | Recovery | Lesson + inference | Unit 10; recovery | Yes | OPEN |
| C28 | Pod reason is symptom; Events/logs differentiate causes | Troubleshooting | Lesson + official docs | Unit 11; debugging | No | [VERIFY] |
| C29 | Service selector/endpoints mismatch can cause reachability issue | Troubleshooting | Lesson + official docs | Unit 11; Services | No | [VERIFY] |
| C30 | Diagnostic bundles can leak sensitive content | Evidence | Inference | Unit 11; evidence | No | Redaction required |
| C31 | Digest must be resolved from actual registry output | Supply chain | Inference + M01 | Local registry workflow | Yes | OPEN |
| C32 | Single PostgreSQL replica is not HA | Architecture | Design choice | This project | No | Explicit limit |
| C33 | Unique run/row key supports same-run DB idempotency | Data correctness | Inference | Application schema | DB-dependent | Run integration test |
| C34 | Fixed CronJob run ID is not a nightly partition strategy | Data correctness | Inference | Batch design | No | Replace for real use |
| C35 | Port-forward load test has measurement blind spots | Drain | Inference | Load test design | Environment-dependent | Document method |
| C36 | Object existence checks do not prove runtime/data correctness | Conformance | Inference | Conformance script | No | Manual review |
### Official documentation starting points (not live-verified in this pass)
- https://kubernetes.io/docs/concepts/architecture/
- https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
- https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/
- https://kubernetes.io/docs/concepts/workloads/controllers/job/
- https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/
- https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
- https://kubernetes.io/docs/concepts/workloads/pods/probes/
- https://kubernetes.io/docs/concepts/workloads/pods/disruptions/
- https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/
- https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/
- https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/
- https://kubernetes.io/docs/concepts/security/pod-security-standards/
- https://kubernetes.io/docs/reference/access-authn-authz/rbac/
- https://kubernetes.io/docs/tasks/administer-cluster/safely-drain-node/
- https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/
- https://kind.sigs.k8s.io/docs/user/quick-start/
- https://etcd.io/docs/

## Appendix B — Ten-pass audit report
| Pass | Result | Evidence / risk | Change or human verification |
| --- | --- | --- | --- |
| 1. Roadmap/tree fidelity | OPEN | Roadmap-tree variants and syllabus prompt available; canonical repository checkout/diff unavailable. | Human confirms canonical path and diff. |
| 2. Completeness | FIXED | Five workload roles, six drills, five runbooks, eight ADRs, rubric, evidence, coverage matrix included. | Human runs milestones and records blockers. |
| 3. Technical accuracy | OPEN | No cluster execution or live docs verification. | Validate API versions, image behavior, HPA/PSS/CronJob semantics and commands. |
| 4. Executability/consistency | OPEN | Snippets not executed; image digest/registry placeholders intentional. | Resolve placeholders, YAML validate and test. |
| 5. Version currency | OPEN | Actual Kubernetes/kind/etcd baseline unknown. | Record versions and consult release/skew docs. |
| 6. Security | OPEN | Hardening/RBAC examples included; PostgreSQL UID/PSS and secret wiring need verification. | Run admission review and move credentials to secret refs. |
| 7. Reliability/SRE | OPEN | Probes/PDB/idempotency/HPA/placement/recovery covered; drills not run. | Run drills and preserve actual evidence. |
| 8. Pedagogy | FIXED | Progression from preflight to game day and reflection provided. | Learner records assumptions. |
| 9. Resource/lab safety | OPEN | Staged budgets included; actual 8 GB fit not measured. | Measure WSL2/Docker use; stage/stop if pressured. |
| 10. Adversarial SRE review | OPEN | Residual risks: digest placeholders, simplified DB queue, fixed demo run ID, Postgres PSS compatibility, restore method, port-forward blind spots, no execution. | Resolve in Appendix C before claiming completion. |

## Appendix C — Human verification checklist
| Topic | Exact check | Pass condition |
| --- | --- | --- |
| Kubernetes/kind baseline | Record client/server versions, kind version and node image digest; inspect release/skew docs. | Target API fields supported. |
| Manifest schemas | Run `kubectl apply --dry-run=server -f <manifest>` on exact disposable cluster after placeholders resolved. | Schema/admission pass; runtime still separate. |
| Images/registry | Inspect M01 registry configuration; build/push/load and resolve digests. | Actual immutable digest reachable by kind nodes. |
| PostgreSQL security | Check UID, writable paths, fsGroup, probes, PSS Restricted. | Runs non-root under policy. |
| Secrets | Use fake-only local secret and secretKeyRef; remove inline password before submission. | No credentials in source/logs. |
| Python tests | Resolve dependency lock and run unit + DB integration tests. | No skipped criterion claimed as passed. |
| Metrics/HPA | Verify Metrics Server install, TLS/address workaround, HPA API and requests. | Actual metrics and scale timeline captured. |
| PDB/drain | Check selectors, disruptionsAllowed, capacity and node names. | Actual request loss and recovery recorded. |
| CronJob/idempotency | Verify schedule semantics, run IDs, retries and same-run replay. | Correct rows and duplicate suppression proven. |
| RBAC/PSS | Review roles/bindings, `can-i`, PSS labels/version and impersonation. | Least privilege evidenced. |
| etcd restore | Inspect topology/version/access and official restore procedure; isolate target. | Human-approved safe restore or explicitly OPEN. |
| WSL2 | Record Docker resources, free disk, DNS and port-forward behavior. | No host instability; deviations documented. |
| API scan | Use maintained scanner plus official release notes; grep is only heuristic. | All APIs/dependencies reviewed. |
| Evidence privacy | Review outputs for Secret data, tokens, kubeconfig and personal data. | Redacted before sharing. |
| Repository diff | Inspect `git status --short` and diff after copying into repo. | Exactly intended target file changed. |

## Appendix D — Limitations and sign-off
| Field | Status |
| --- | --- |
| Content status | DRAFT-AUDITED |
| Audit date | 2026-10-25 |
| Auditor | AI self-audit; human lab verification required |
| Open items | 15 verification topics listed in Appendix C; runtime/source verification remains open |
| Tests/labs executed | Not executed in this authoring pass |
| Official docs live-checked | No; URLs are verification starting points |
| Repository diff inspected | No repository checkout/diff available |
| Production certification | Not certified; local learning exercise |
### Final sign-off
- [ ] Canonical path and one-file-only diff verified.
- [ ] Image/base-image digests resolved from actual registry output.
- [ ] Server-side dry run and Python/DB tests executed.
- [ ] API, worker, stateful dependency, ETL Job and CronJob flow verified.
- [ ] Same-run ETL replay verified.
- [ ] Drain/load test measured; HPA/placement/RBAC/PSS checked.
- [ ] etcd restore is safely rehearsed or remains OPEN.
- [ ] Six drills executed individually and cleaned up.
- [ ] Evidence redacted; `make verify` and manual review recorded.
