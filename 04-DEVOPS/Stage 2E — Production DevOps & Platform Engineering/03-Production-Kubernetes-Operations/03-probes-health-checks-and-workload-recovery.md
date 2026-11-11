# Probes, Health Checks, and Workload Recovery

**Module:** Stage 2E --- Production DevOps & Platform Engineering / M03\
**Unit:** 3\
**Target file:** `03-probes-health-checks-and-workload-recovery.md`\
**Estimated time:** 12--16 hours, including labs, review, and evidence
capture\
**Prerequisites:** Linux and shell basics; Git and Docker; basic Pod and
Deployment usage; M03 Unit 1 cluster/control-plane concepts; M03 Unit 2
namespaces and resource governance; M01 image fundamentals; M02 CI/CD
basics; Python basics\
**Core tools:** `kubectl`, `kind`, Docker or a compatible container
runtime, Python 3, FastAPI, Uvicorn, `curl` or Python `urllib`, shell
utilities\
**Awareness:** kubelet and controllers; Services and EndpointSlices;
rollout status; node conditions and taints; worker heartbeat semantics;
SLOs; autoscaler interactions; Kubernetes security guidance\
**Last reviewed:** 2026-10-25; not live-verified against current
documentation\
**Kubernetes baseline assumed:** Kubernetes APIs commonly available in
recent supported releases; exact minor-version support, gRPC probe
behavior, readiness-gate details, node-failure timing, and endpoint
inspection commands require `[VERIFY]` against the actual target cluster
version and its official API reference.

> **Execution and evidence status:** This is a teaching artifact.
> Commands, manifests, and labs have not been executed as part of
> writing this file. Outputs labeled "Example --- yours will differ" are
> illustrative, not observed results. Validate every version-sensitive
> detail and run the exercises only in a disposable local `kind`
> cluster.

------------------------------------------------------------------------

## 1. Why This Matters in Production

A scoring API can be running as a process while unable to answer
requests because its model is still loading or a required dependency is
unavailable. A badly designed liveness check may interpret a database
outage as a dead application, repeatedly restart every replica, and
remove capacity exactly when the service needs it most. Conversely, a
process can remain alive while its worker loop is deadlocked, leaving a
queue to age silently. Probes are therefore recovery signals, not a
complete definition of health: the handler, thresholds, dependency
semantics, controller behavior, and application's restart safety must
agree. The goal is to detect the condition that each probe is meant to
detect without amplifying the incident.

## 2. Learning Objectives

By the end of this unit, the learner should be able to:

1.  **\[L1\]** Explain the distinct operational effects of startup,
    liveness, and readiness probes.
2.  **\[L1\]** Read Pod conditions, container states, restart counts,
    events, and `CrashLoopBackOff` without confusing symptoms with root
    causes.
3.  **\[L2\]** Configure an HTTP-based FastAPI service with shallow
    liveness and bounded, dependency-aware readiness.
4.  **\[L2\]** Choose probe handlers and timing parameters from startup
    measurements, latency, load, and detection objectives rather than
    copied defaults.
5.  **\[L2\]** Diagnose image-pull and init-container failures
    separately from probe failures.
6.  **\[L3\]** Identify probe anti-patterns, quantify false-positive
    restarts and readiness flapping, and explain rollout interactions.
7.  **\[L3\]** Design health semantics for non-HTTP workers and state
    the limitations of heartbeat checks.
8.  **\[L4\]** Run a bounded local recovery drill, compare event
    timelines before and after correcting deep liveness, and write a
    safe recovery runbook.
9.  **\[L4\]** Defend restart-safe processing practices including
    idempotency, retry limits, checkpointing, and acknowledgement order.
10. **\[L4\]** Propose fleet-level standards, exception handling,
    version verification, and canary rollout controls for probe
    configuration.

## 3. Prerequisites and Scope Boundaries

### Required preparation

-   A disposable local `kind` cluster. The intended shape is one
    control-plane node and two workers if laptop capacity allows; a
    one-node cluster is acceptable for most probe semantics.
-   `kubectl` configured for the disposable cluster. Verify the context
    before every state-changing command.
-   Docker or another supported container runtime configured for `kind`.
-   Python 3 and a virtual environment for the FastAPI example.
-   Familiarity with `kubectl get`, `describe`, `logs`, `apply`,
    `delete`, and YAML indentation.
-   Enough disk and RAM to build and run a small local image. The stated
    baseline is approximately 4 CPU, 8 GB RAM, and 30 GB free disk;
    actual use depends on the host, runtime, and image cache.

### Scope included here

This unit teaches probe semantics, application health endpoints, timing
design, diagnostic interpretation, local recovery drills, worker-health
signals, restart safety, and fleet-level probe governance. It includes a
small illustrative FastAPI app and manifests inline so the lesson is
self-contained.

### Deliberately deferred

-   Deployment/StatefulSet/Job/CronJob controller behavior in depth:
    Unit 4. This unit covers only the rollout symptoms needed to
    diagnose probe-related failures.
-   PodDisruptionBudgets and detailed graceful shutdown: Unit 5.
-   HPA/KEDA and autoscaler configuration: Unit 6. This unit explains
    probe and cold-start interactions only.
-   Node placement, affinity, and topology design: Unit 7.
-   RBAC and Pod Security Standards: Unit 9, while this unit still
    follows least privilege.
-   Deep Services, DNS, NetworkPolicy, Ingress, and service-mesh
    behavior: M04.
-   Storage internals: M05.
-   Full SLO/error-budget and incident-management framework: M10.
-   Full metrics/logging/tracing platform: M11.
-   Organization-wide backup and disaster recovery: M13.

These boundaries do not excuse an incomplete explanation of probe
behavior. The unit explains the local mechanism and points to the later
module only for deeper treatment.

## 4. Concept Map and Vocabulary

### Recovery path overview

``` mermaid
flowchart TD
    A[Application process starts] --> B{Startup probe configured?}
    B -- Yes --> C[Startup probe evaluates initialization]
    C -- Fails within budget --> D[Kubelet may restart container under restart policy]
    C -- Succeeds --> E[Liveness and readiness probes become eligible]
    B -- No --> E
    E --> F{Liveness result}
    F -- Failure threshold reached --> G[Kubelet restarts container according to policy]
    F -- Success --> H[Process continues]
    E --> I{Readiness result}
    I -- Not ready --> J[Pod/container readiness becomes false]
    J --> K[Service endpoint eligibility/traffic routing is updated asynchronously]
    I -- Ready --> L[Eligible for normal Service traffic, subject to other conditions]
    G --> M[Container restarts; application must reconstruct safe state]
    M --> C
    H --> N[Workload controller observes desired/current state]
    N --> O[Controller may create replacement Pods if a Pod is lost and controller owns it]
    O --> P[Scheduler assigns unscheduled Pods when needed]
```

The diagram is conceptual, not a strict synchronous sequence. The
kubelet evaluates container probes and reports status; API objects and
endpoint state are reconciled asynchronously. A container restart inside
an existing Pod is different from a controller creating a replacement
Pod. A scheduler does not restart a container.

### Vocabulary

  ------------------------------------------------------------------------
  Term                    Precise definition       Common misconception
  ----------------------- ------------------------ -----------------------
  Startup probe           A probe used to          It is simply another
                          determine whether        name for readiness.
                          application startup has  
                          completed enough for     
                          liveness/readiness       
                          probing to proceed.      

  Liveness probe          A signal used to detect  It should fail whenever
                          a local application      any dependency is
                          condition from which     unavailable.
                          restarting the container 
                          may help.                

  Readiness probe         A signal indicating      Failure automatically
                          whether the instance     restarts the container.
                          should be considered     
                          ready for normal         
                          traffic.                 

  Probe failure           A failed probe result    It proves the whole
                          according to the handler application is broken.
                          and configured           
                          thresholds.              

  Container restart       Kubelet/runtime restart  A new Pod is
                          behavior for a container necessarily created.
                          within its Pod, subject  
                          to restart policy and    
                          failure conditions.      

  Pod phase               High-level Pod lifecycle `CrashLoopBackOff` is a
                          phase such as `Pending`, Pod phase.
                          `Running`, `Succeeded`,  
                          or `Failed`.             

  Container state         The current state        It is interchangeable
                          (`Waiting`, `Running`,   with Pod phase.
                          or `Terminated`) and     
                          related details for a    
                          container.               

  `CrashLoopBackOff`      A waiting reason         It is the root cause
                          commonly shown while     rather than a symptom.
                          Kubernetes backs off     
                          repeated container       
                          restarts.                

  Readiness               A condition reflecting   It proves
                          readiness of the Pod,    business-level
                          including relevant       correctness or SLO
                          container readiness and  compliance.
                          any configured readiness 
                          gates.                   

  EndpointSlice           An API resource          A ready Pod is
                          representing endpoint    guaranteed to receive
                          information for a        every request.
                          Service.                 

  Init container          A container that must    It is a substitute for
                          complete before          every dependency retry
                          application containers   loop.
                          start, unless            
                          restartable sidecar      
                          semantics apply under    
                          the cluster              
                          version/configuration.   

  Heartbeat               A periodic signal that a A fresh heartbeat
                          worker is alive or       always proves useful
                          recently made progress.  work is occurring.

  Idempotency             A property allowing      Retrying is safe just
                          repeated execution of    because the process
                          the same logical         restarted.
                          operation without        
                          unintended additional    
                          effects.                 

  `not-ready` /           Node-related taints used They imply a universal
  `unreachable` taints    in Kubernetes            fixed eviction
                          node-failure handling    deadline.
                          and scheduling/eviction  
                          behavior.                

  Readiness gate          An additional Pod        It is the same thing as
                          readiness condition      a readiness probe.
                          supplied through a       
                          documented               
                          external/controller      
                          mechanism.               
  ------------------------------------------------------------------------

### Five different questions, five different mechanisms

1.  **Can the process start?** Startup behavior and startup probe.
2.  **Can this instance safely serve normal requests now?** Readiness.
3.  **Is the local process stuck in a condition a restart is likely to
    repair?** Liveness.
4.  **Should a lost Pod be recreated and scheduled elsewhere?** Workload
    controller and scheduler, subject to desired state and cluster
    capacity.
5.  **Can the application recover data and side effects correctly?**
    Application-level retry, idempotency, checkpoint, transaction, and
    acknowledgement design.

No single probe answers all five.

## 5. Level 1 --- Beginner: Probe and Recovery Fundamentals

### L1.1 Liveness, readiness, and startup

**Liveness** answers a narrow question: is the local application in a
condition where a container restart is a reasonable recovery action? A
liveness endpoint should usually be cheap and local. It should not fail
merely because a shared database, queue, remote model service, or
third-party API is down. If every replica restarts during a shared
dependency outage, the restart wave can increase load, reset useful
caches, delay recovery, and reduce capacity.

**Readiness** answers a different question: should this instance receive
normal traffic now? A readiness failure does not itself restart the
container. It changes readiness state; the Service's endpoint/traffic
machinery then reconciles which endpoints are eligible. This process is
asynchronous and exact behavior depends on Service configuration and the
cluster implementation/version. Readiness is appropriate for a required
dependency that makes successful requests impossible, provided the check
is bounded and does not create load amplification.

**Startup** protects slow initialization. If model loading, cache
warmup, schema initialization, or runtime compilation takes longer than
a normal liveness budget, a startup probe can provide an initialization
budget before liveness/readiness probes are run. A startup probe
configured with an insufficient budget can still cause restart loops; a
huge budget can hide a genuinely broken startup for too long.

### L1.2 Handler types

  ------------------------------------------------------------------------
  Handler           What it checks    Strength          Limitation /
                                                        caution
  ----------------- ----------------- ----------------- ------------------
  HTTP              Kubelet makes an  Natural for web   A successful
                    HTTP request to   APIs; can expose  status proves only
                    the configured    separate `/live`  that endpoint's
                    endpoint and      and `/ready`      contract. Keep the
                    interprets the    semantics.        handler cheap.
                    response                            Verify redirects
                    according to                        and edge cases in
                    documented probe                    the target-version
                    rules.                              docs.

  TCP               Attempts a TCP    Useful for        A listening port
                    connection to the services whose    does not prove
                    configured port.  minimal health    correct responses,
                                      contract is a     model
                                      listening socket. availability, or
                                                        progress.

  Exec              Runs a command in Useful for a      Adds
                    the container     worker with no    process/resource
                    context and       HTTP endpoint or  overhead; the
                    judges            a local progress  image may not
                    success/failure   signal.           contain a shell or
                    according to the                    utility. Do not
                    probe contract.                     assume a
                                                        distroless image
                                                        has `sh`, `cat`,
                                                        or `ps`.

  gRPC              Uses Kubernetes'  Can integrate     `[VERIFY]` Check
                    documented gRPC   with a gRPC       target Kubernetes
                    health-probe      health service.   API version and
                    mechanism when                      the official gRPC
                    supported and                       probe
                    correctly                           documentation for
                    configured.                         support,
                                                        service-name
                                                        behavior, TLS/auth
                                                        limitations, and
                                                        supported fields.
                                                        Do not copy HTTP
                                                        fields into gRPC
                                                        configuration
                                                        without checking
                                                        the schema.
  ------------------------------------------------------------------------

The handlers are not interchangeable. Pick the least complex mechanism
that represents the intended health contract.

### L1.3 Timing fields and detection budget

Common probe fields include:

-   `initialDelaySeconds`: delay before the kubelet begins probing a
    container.
-   `periodSeconds`: interval between probe attempts, subject to probe
    execution and scheduling behavior.
-   `timeoutSeconds`: how long an individual probe is allowed to run
    before it is considered failed.
-   `successThreshold`: consecutive successes required to transition
    from failure to success; for liveness and startup probes, the API
    has constraints that must be checked against the target version.
-   `failureThreshold`: consecutive failures needed before a probe is
    considered failed.
-   Startup-probe budget: commonly reasoned about using
    `failureThreshold × periodSeconds`, with important caveats. This is
    a planning approximation, not a universal exact deadline. Probe
    execution time, scheduling, initialization, and implementation
    details affect observed timing.

Do not set these values by copying a blog's YAML. Measure startup
distributions and request latency under representative load. Decide how
quickly the system must detect failure, how much transient slowness it
should tolerate, and what false-positive cost is acceptable. If a
request routinely takes longer than the probe timeout under load, the
probe may measure overload rather than process health.

A simple planning example---not a universal default:

-   Observed model initialization: 45--70 seconds in a local test.
-   Desired startup allowance: enough to cover measured high-percentile
    startup plus a margin for the local environment.
-   Liveness should not begin evaluating before startup has succeeded if
    a startup probe is used.
-   Readiness should remain false until the instance can serve the
    intended request contract.
-   A later load test must verify that the chosen timeout and period do
    not flap under CPU throttling or cold-cache conditions.

### L1.4 Restart policy, state, and `CrashLoopBackOff`

A Pod's `restartPolicy` influences whether a terminated container is
restarted in that Pod. Common values are `Always`, `OnFailure`, and
`Never`; workload controllers and workload type affect which policies
are valid or conventional. `[VERIFY]` Confirm exact allowed values and
semantics in the API reference for the target resource and Kubernetes
version. A liveness failure is acted on by the kubelet, but the
resulting behavior remains subject to the container/Pod restart
semantics.

Distinguish these observations:

-   **Pod phase:** a coarse lifecycle summary. `Running` does not
    guarantee readiness.
-   **Pod conditions:** for example, `Ready` and `ContainersReady`;
    other conditions depend on lifecycle and version.
-   **Container `state`:** current `Waiting`, `Running`, or `Terminated`
    state.
-   **`lastState`:** information about the previous container state,
    often useful after a restart.
-   **`restartCount`:** a counter of restarts reported for the
    container; interpret it over a time window and alongside
    events/logs.
-   **Waiting reason:** such as `CrashLoopBackOff` or an
    image-pull-related reason.
-   **Events:** recent control-plane/kubelet observations; events may
    expire or be aggregated.
-   **Logs:** current logs and, after a restart, potentially
    previous-container logs.

`CrashLoopBackOff` is a backoff-related **container waiting reason**,
not a Pod phase and not a diagnosis. Causes can include application
exit, bad arguments, missing configuration, failed startup, OOM
termination, failed liveness checks, or other runtime failures. Start
with `describe`, events, current and previous logs, exit code/reason,
configuration, resource pressure, and probe settings.

### L1.5 Recovery layers

  ----------------------------------------------------------------------------------
  Layer             Typical mechanism           What it can do     What it cannot
                                                                   promise
  ----------------- --------------------------- ------------------ -----------------
  Detection         Probe, process exit, node   Surface a          Detect all
                    status, monitoring          particular         business errors
                                                observed failure   or silent data
                                                condition          corruption

  Traffic removal   Readiness and endpoint      Reduce normal      Remove every
                    reconciliation              traffic to an      in-flight request
                                                unready endpoint   instantly or
                                                                   prove zero errors

  Process restart   Kubelet/runtime under       Recover from some  Fix bad code,
                    restart semantics           local deadlocks or invalid
                                                process failures   credentials,
                                                                   corrupt data, or
                                                                   an unavailable
                                                                   remote service

  Pod replacement   Workload controller         Create replacement Guarantee
                    reconciles desired replicas Pods when its      immediate
                    after Pod loss              desired state      scheduling,
                                                requires them      capacity, or data
                                                                   recovery

  Scheduling        Scheduler binds an          Select a node      Make an
                    unscheduled Pod to a        according to       infeasible Pod
                    feasible node               constraints and    schedulable or
                                                current cluster    restore a failed
                                                state              node

  Node-failure      Node                        Detect/report node Guarantee one
  handling          controller/kubelet/taints   conditions and     universal
                    and configured tolerations  eventually trigger eviction or
                                                configured         replacement time
                                                handling           

  Application       Retries, idempotency,       Preserve           Be supplied
  recovery          checkpoints, reconciliation correctness across automatically by
                                                retries/restarts   Kubernetes
                                                when designed      
                                                correctly          
  ----------------------------------------------------------------------------------

### L1.6 First diagnostic pass

Run read-only commands first. Confirm the current context and namespace;
add `-n <namespace>` explicitly when not using the intended namespace.

``` bash
kubectl config current-context
kubectl get pods -o wide
kubectl describe pod <pod-name>
kubectl logs <pod-name> --all-containers=true
kubectl logs <pod-name> --previous
kubectl get events --sort-by=.metadata.creationTimestamp
```

Purpose and interpretation:

-   `current-context` confirms which cluster the client targets; it does
    not prove the cluster is disposable.
-   `get pods -o wide` shows phase, readiness, restart counts, IP/node
    placement, and other columns. Column presentation varies by client
    version.
-   `describe pod` summarizes conditions, container state, probe
    configuration, and recent events.
-   `logs --all-containers=true` helps find errors across application
    and sidecar containers.
-   `logs --previous` requests logs from the previous terminated
    container instance when available; it may fail if no previous
    instance exists or logs are unavailable.
-   Events are useful but not durable forensic storage. Capture them
    during the incident.

**Example --- yours will differ** (illustrative only):

``` text
NAME                    READY   STATUS             RESTARTS   AGE
scoring-api-abc123       0/1     CrashLoopBackOff   5          4m
```

Interpretation: the container is not ready and has restarted repeatedly.
The displayed waiting reason does not say why. Inspect `describe`,
`lastState`, exit code, events, and logs before changing probes.

For image-pull errors, inspect `describe pod` and the image reference,
registry credentials, network/registry reachability, and node
architecture compatibility. A probe cannot repair an image that the
runtime cannot pull.

## 6. Level 2 --- Intermediate: Designing Health Checks for Data Services

### L2.1 Define the health contract before writing YAML

For a data/AI platform, separate the contract by component:

  ---------------------------------------------------------------------------------------
  Component         Readiness should   Liveness should   Startup concerns
                    represent          represent         
  ----------------- ------------------ ----------------- --------------------------------
  FastAPI scoring   The instance can   Local event       Model loading, tokenizer
  API               accept the         loop/process is   initialization, GPU/runtime
                    intended scoring   responsive        warmup, cache creation
                    request; required  enough, or a      
                    model is loaded;   known local       
                    critical           unrecoverable     
                    dependency is      condition is      
                    sufficiently       present           
                    available if the                     
                    API cannot                           
                    function without                     
                    it                                   

  Queue consumer    Consumer can       Worker loop is    Client initialization,
                    accept work and    not irrecoverably partition/lease assignment,
                    required local     stuck, based on a local cache loading
                    state is           defensible local  
                    initialized;       signal            
                    dependency                           
                    availability may                     
                    gate readiness                       

  Stateful          The dependency's   Local process     Recovery/replay/initialization
  dependency        documented         recovery          can be lengthy
                    health/readiness   condition         
                    contract           supported by that 
                                       system            

  Batch ETL Job     The process is     A local stuck     Input discovery, schema/config
                    executing and can  condition if      load, checkpoint restoration
                    make progress; Job reliably          
                    success/failure    detectable        
                    semantics remain                     
                    primary                              

  Scheduled refresh The refresh        Local process     Model/data snapshot loading and
                    process has        state             validation
                    initialized and                      
                    can safely run                       
  ---------------------------------------------------------------------------------------

A Pod can be `Running` but not ready. A Pod can be ready while a
business-level defect still produces incorrect scores. Health endpoints
must be intentionally narrow and observable.

### L2.2 FastAPI health endpoint design

The following self-contained example uses only local simulated state; it
does not require a database or queue. It illustrates the **shape** of
health contracts, not a production dependency client. It includes a
startup delay, a liveness endpoint independent of dependency state, and
readiness that becomes false when the simulated dependency is
unavailable.

Save as `app.py` in a learner-created working directory:

``` python
import asyncio
import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response, status
from pydantic import BaseModel

STARTUP_SECONDS = float(os.getenv("STARTUP_SECONDS", "5"))
DEPENDENCY_AVAILABLE = os.getenv("DEPENDENCY_AVAILABLE", "true").lower() == "true"
MODEL_READY = False
STARTED_AT = time.monotonic()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global MODEL_READY
    # Illustrative bounded model initialization; replace with real loading in a real service.
    await asyncio.sleep(max(0.0, STARTUP_SECONDS))
    MODEL_READY = True
    yield
    MODEL_READY = False

app = FastAPI(title="Illustrative Scoring API", lifespan=lifespan)

class ScoreRequest(BaseModel):
    features: list[float]

@app.get("/health/live")
async def live():
    # Deliberately does not call a database, queue, or remote model server.
    # Successful response means the local ASGI app can handle this small request.
    return {"status": "live"}

@app.get("/health/ready")
async def ready(response: Response):
    # Simulated dependency signal. Real checks must be bounded and designed carefully.
    dependency_ok = os.getenv("DEPENDENCY_AVAILABLE", "true").lower() == "true"
    if not MODEL_READY or not dependency_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not-ready"}
    return {"status": "ready"}

@app.get("/health/startup")
async def startup(response: Response):
    if not MODEL_READY:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "starting"}
    return {"status": "started"}

@app.post("/score")
async def score(request: ScoreRequest):
    if not MODEL_READY:
        return Response(status_code=503)
    # Illustrative scoring placeholder; not a real model prediction.
    return {"score": sum(request.features) / max(1, len(request.features))}
```

**Important implementation caveats**

-   In this minimal example, `DEPENDENCY_AVAILABLE` is read from the
    environment at request time, so changing the process environment
    from outside the process is not a supported simulation technique.
    For the local failure test, use the alternate code variant below
    that exposes a guarded local toggle, or restart the app with the
    variable changed. In Kubernetes, changing a Pod environment variable
    generally requires replacing the Pod; do not imply that editing a
    ConfigMap automatically mutates the environment of an existing
    process.
-   A real application should use its framework's lifespan/startup
    facilities for model loading, bound initialization time, handle
    exceptions, and expose readiness only after required state is valid.
-   `/health/live` does not prove the model returns correct results. It
    only proves that a minimal local handler can execute.
-   `STARTED_AT` is intentionally unused in the basic sample and may be
    removed; it is not an authoritative startup metric.

For a live local dependency toggle, replace the example's dependency
flag section and readiness handler with this explicit in-memory switch.
This is **for a disposable local lab only**, not a public production
control endpoint:

``` python
from fastapi import HTTPException

dependency_ok = True

@app.get("/lab/dependency/{state}")
async def set_dependency_state(state: str):
    global dependency_ok
    if state not in {"up", "down"}:
        raise HTTPException(status_code=400, detail="state must be up or down")
    dependency_ok = state == "up"
    return {"dependency_simulated": "available" if dependency_ok else "unavailable"}

@app.get("/health/ready")
async def ready(response: Response):
    if not MODEL_READY or not dependency_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not-ready"}
    return {"status": "ready"}
```

Do not expose `/lab/dependency/{state}` in production. It is an
unauthenticated state-changing route included only to make the local
exercise deterministic. If you use this variant, remove the earlier
`/health/ready` function so the app has exactly one readiness handler.
In Kubernetes labs, isolate the namespace and use only the disposable
local cluster.

### L2.3 Run the app and smoke-test it

Create a virtual environment and install dependencies in the learner's
working directory:

``` bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install fastapi uvicorn
uvicorn app:app --host 127.0.0.1 --port 8000
```

In a second terminal:

``` bash
curl -i http://127.0.0.1:8000/health/live
curl -i http://127.0.0.1:8000/health/startup
curl -i http://127.0.0.1:8000/health/ready
curl -i -X POST http://127.0.0.1:8000/score \
  -H 'content-type: application/json' \
  -d '{"features":[1.0,2.0,3.0]}'
```

The startup endpoint may return a not-started response until the
illustrative delay completes. Test both before and after that point. The
exact timing depends on process scheduling and host load.

**Example --- yours will differ**:

``` text
HTTP/1.1 200 OK
content-type: application/json
...
{"status":"live"}
```

A `200` here demonstrates only the local health endpoint's stated
contract. It is not proof of end-to-end scoring correctness.

For a lightweight automated check, save as `test_health.py`:

``` python
from fastapi.testclient import TestClient
from app import app

def test_live_is_independent_of_dependency_state():
    with TestClient(app) as client:
        response = client.get("/health/live")
        assert response.status_code == 200
        assert response.json()["status"] == "live"

def test_startup_and_ready_after_lifespan():
    with TestClient(app) as client:
        # TestClient lifespan handling may depend on installed Starlette/httpx versions.
        # If this fails due to dependency-version incompatibility, pin compatible versions
        # according to the official FastAPI testing guidance rather than altering semantics.
        assert client.get("/health/startup").status_code == 200
        assert client.get("/health/ready").status_code == 200
```

Run:

``` bash
python -m pip install pytest httpx
pytest -q
```

The test client runs lifespan behavior when used as a context manager in
supported versions. `[VERIFY]` Confirm compatibility among the installed
FastAPI, Starlette, and HTTPX versions if the test fails before reaching
assertions. Do not misdiagnose a test-dependency mismatch as a
Kubernetes probe failure.

### L2.4 Kubernetes Deployment and Service

Kubernetes needs a container image. The manifest below intentionally
uses a placeholder:

`IMAGE_REPLACE_WITH_A_REAL_IMAGE_BUILT_FOR_KIND`

Do not apply the manifest until replacing the placeholder with an image
you built and loaded into the local `kind` cluster, or with a real
accessible image reference you control. No published image URL is
asserted here.

Illustrative `Dockerfile` (save inline to `Dockerfile` in the app
directory):

``` dockerfile
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 STARTUP_SECONDS=5
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn
COPY app.py /app/app.py
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

This is a teaching image, not a complete hardened production image. It
does not pin package hashes, use a lock file, or include a full
supply-chain process; M01 covers image engineering. Ensure the non-root
user can read application files. Build and import into kind using a
unique local tag:

``` bash
docker build -t probes-lab:0.1.0 .
kind load docker-image probes-lab:0.1.0 --name probes-lab
```

The cluster name must match the actual disposable cluster. The following
manifest is valid only after the image field is replaced with
`probes-lab:0.1.0` or another verified reference:

``` yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scoring-api
  namespace: probes-lab
  labels:
    app.kubernetes.io/name: scoring-api
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: scoring-api
  template:
    metadata:
      labels:
        app.kubernetes.io/name: scoring-api
    spec:
      terminationGracePeriodSeconds: 10
      containers:
        - name: api
          image: probes-lab:0.1.0
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 8000
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
          startupProbe:
            httpGet:
              path: /health/startup
              port: http
            periodSeconds: 2
            timeoutSeconds: 1
            failureThreshold: 40
          livenessProbe:
            httpGet:
              path: /health/live
              port: http
            periodSeconds: 10
            timeoutSeconds: 2
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /health/ready
              port: http
            periodSeconds: 5
            timeoutSeconds: 2
            failureThreshold: 2
            successThreshold: 1
---
apiVersion: v1
kind: Service
metadata:
  name: scoring-api
  namespace: probes-lab
spec:
  selector:
    app.kubernetes.io/name: scoring-api
  ports:
    - name: http
      port: 80
      targetPort: http
```

These resource values and timings are **illustrative only**, not sizing
advice or a universal production recommendation. The startup budget is
deliberately generous for a short local demo. Measure real startup time
and load behavior before selecting production settings.

Create the namespace and apply only after the context/image checks:

``` bash
kubectl config current-context
kubectl create namespace probes-lab
kubectl apply -f deployment-and-service.yaml
kubectl -n probes-lab rollout status deployment/scoring-api --timeout=180s
kubectl -n probes-lab get pods -o wide
kubectl -n probes-lab get svc
```

The file name `deployment-and-service.yaml` is a learner-created file
containing the manifest above; it is not created automatically by this
lesson.

### L2.5 Readiness and Service endpoint effects

Inspect endpoints using the API available in your target version:

``` bash
kubectl -n probes-lab get endpointslices
kubectl -n probes-lab get endpointslices -o yaml
```

`EndpointSlice` is the modern API for representing Service endpoints in
Kubernetes. `[VERIFY]` Check whether `discovery.k8s.io/v1` and the
`kubectl get endpointslices` resource alias are available in the
cluster. A cluster/client may use a different display format. Readiness
affects endpoint eligibility, but endpoint reconciliation is
asynchronous and actual traffic also depends on client behavior,
proxies, connection reuse, and in-flight requests. Do not infer zero
traffic solely from a readiness transition.

### L2.6 Init containers and image-pull errors

Init containers are appropriate for bounded, prerequisite work that must
finish before the app container starts, such as rendering a local
configuration file or waiting for a carefully specified local setup
step. They run before app containers and can prevent application startup
until they succeed. Failure/retry behavior depends on Pod restart policy
and init-container semantics; `[VERIFY]` check the target API docs,
especially for restartable sidecars or newer features.

Avoid an init container that loops indefinitely waiting for a remote
dependency when the application could instead expose readiness and retry
safely. It can hold a Pod in initialization, delay diagnosis, and
obscure whether the dependency is actually required. Avoid using init
containers as a substitute for dependency orchestration, schema
migration governance, or application-level retries.

For `ImagePullBackOff` / `ErrImagePull`, investigate:

1.  image name, tag, registry, digest, and architecture;
2.  `imagePullPolicy`;
3.  imagePullSecrets/service-account configuration where applicable;
4.  registry availability and node network/DNS path;
5.  local kind image import and cluster name;
6.  runtime events from `kubectl describe pod`.

A probe cannot run if the container never starts. Do not tune probe
thresholds to "fix" an image pull failure.

## 7. Level 3 --- Advanced: Probe Reliability and Failure Semantics

### L3.1 Anti-pattern catalogue

  -----------------------------------------------------------------------
  Bad configuration       Production risk         Corrected design
  ----------------------- ----------------------- -----------------------
  Liveness checks a       Shared dependency       Keep liveness local;
  database/queue/remote   outage triggers         let readiness express
  model server and fails  simultaneous restarts;  whether the instance
  when it is unavailable  recovery becomes slower can serve requests
                          and more expensive      under the dependency
                                                  condition

  Same endpoint and       Startup may be killed   Define three contracts
  semantics for startup,  prematurely; an         and test each
  liveness, and readiness instance may receive    transition
                          traffic before          
                          initialized; transient  
                          dependency failure      
                          restarts the process    

  Tiny timeout and low    CPU throttling or brief Measure response-time
  failure threshold       scheduling delays cause distributions and load;
  copied without          false failures and      choose a deliberate
  measurements            restart loops           detection budget

  Readiness check         Endpoint churn, uneven  Use bounded checks,
  alternates rapidly      traffic, retry storms,  hysteresis through
  between success and     poor rollout stability  sensible thresholds,
  failure                                         cached health where
                                                  appropriate, and
                                                  explicit recovery
                                                  criteria

  Probe does expensive    Probe traffic adds      Keep it cheap,
  queries or mutates      load, causes side       read-only, bounded, and
  state                   effects, or worsens a   safe to call repeatedly
                          dependency incident     

  Health response returns Information disclosure  Return minimal status;
  stack traces, tokens,   and reconnaissance      send detailed
  model paths, or                                 diagnostics to
  dependency diagnostics                          access-controlled
                                                  logs/telemetry

  Exec probe assumes      Probe fails on          Use a suitable HTTP/TCP
  `sh`/`curl`/`ps` exists minimal/distroless      probe or a small
                          image despite a healthy executable
                          app                     intentionally included
                                                  in the image

  Heartbeat file is       A deadlocked worker can Track progress as well
  updated by a separate   appear healthy          as process liveness;
  timer, not actual work                          define what "progress"
  progress                                        means

  Startup budget is too   Restart loop during     Measure cold/warm
  small for cold starts   model load              startup and budget for
                                                  justified variance;
                                                  keep failure detection
                                                  bounded

  Startup budget is       Bad config or failed    Use a measured budget,
  extremely large without model load remains      clear startup errors,
  alerting                hidden too long         and rollout monitoring

  Readiness probes call   Fan-out load and        Use bounded, minimal
  every dependency        correlated failure      checks; consider cached
  serially on every       during dependency       state and carefully
  period                  degradation             designed aggregation

  Readiness is used as a  API reports ready while Separate health from
  substitute for business outputs are wrong or    correctness checks,
  validation              data is corrupt         canaries, data
                                                  validation, and SLO
                                                  monitoring
  -----------------------------------------------------------------------

### L3.2 Deep-liveness failure mode

Consider a scoring API with five replicas and a shared feature database.
During a database slowdown, each `/health/live` call times out. The
kubelet restarts the API containers. Restarting drops warm model/cache
state and creates new database connection attempts. All replicas become
less capable at the same time; traffic is concentrated on remaining
endpoints, and the database receives more connection churn. A readiness
check could instead make instances unready when they cannot serve
requests, while the process remains running and can recover when the
dependency returns.

A dependency-aware liveness probe is not categorically impossible, but
it needs an application-specific justification showing that restart is
likely to repair the local condition and that the dependency outage
won't cause fleet-wide restart amplification. That is an exception
requiring evidence and review, not the default pattern.

### L3.3 Timing and false-positive design

Probe timings are a detection policy, not an exact universal deadline.
Consider:

-   **Application response latency:** a timeout must be long enough for
    a healthy handler under expected CPU and I/O conditions.
-   **Load and CPU throttling:** a lightweight handler may still be
    delayed when the container is starved.
-   **Failure detection objective:** how long can the system remain
    stuck before action is useful?
-   **False-positive cost:** what happens if a healthy but slow process
    is restarted?
-   **Startup distribution:** use measured cold-start percentiles plus
    an explicit margin.
-   **Recovery behavior:** restart may take longer than waiting for a
    transient dependency to recover.
-   **Probe period and thresholds:** larger thresholds tolerate
    transient failure but delay detection; smaller thresholds detect
    faster but may amplify noise.
-   **Probe handler cost:** the health check itself consumes CPU,
    memory, sockets, and downstream capacity.
-   **Replica count and shared dependencies:** the same probe policy can
    create synchronized failures across many replicas.

Use a staged experiment: measure normal response times, add realistic
CPU/memory pressure, observe transitions, and choose thresholds. Never
treat `periodSeconds × failureThreshold` as an exact deadline. Startup
probe budgeting is similarly approximate.

### L3.4 Worker health without HTTP

For a consumer or ETL worker, possible signals include:

-   **Exec process check:** verify a purpose-built executable can
    inspect a local worker state. Avoid brittle shell pipelines and
    assumptions about image tools.
-   **Heartbeat file:** worker updates a timestamp or sequence counter
    after meaningful progress; probe checks freshness.
-   **Progress metric:** last completed message/record/checkpoint time,
    queue lag, or work-item age. These are often better operational
    signals than process existence but may belong in monitoring rather
    than a probe.
-   **Supervisor state:** a process supervisor can report whether the
    worker loop is running, if that signal is trustworthy.

A heartbeat has failure modes. A timer thread can keep updating while
the main work loop is deadlocked. A stale file can be misread if the
timestamp format, wall clock, or container restart behavior is
inconsistent. A process can be healthy but legitimately idle because no
work is available. A worker can be making progress but not be able to
acknowledge work due to a downstream outage. Define "progress"
explicitly and separate local liveness from readiness to consume.

Prefer a monotonic counter or monotonic time within a process for
elapsed-time comparisons where possible; a file persisted across restart
requires a design that distinguishes a previous process's heartbeat from
the current process. Avoid using wall-clock timestamps across nodes
without accounting for clock skew. An exec probe that launches a process
every period can itself become costly at fleet scale.

### L3.5 Rollout interactions

-   `minReadySeconds` specifies a period a newly created Pod should be
    ready without interruption before the Deployment considers it
    available. `[VERIFY]` Confirm exact behavior in the current
    Deployment API docs.
-   `progressDeadlineSeconds` controls when the Deployment controller
    reports lack of rollout progress. It is not a universal hard
    rollback timer and does not itself prove that the new application is
    correct.
-   Readiness is a rollout gate: a new replica that never becomes ready
    can block rollout progress or availability goals.
-   A startup probe can intentionally delay readiness until
    initialization is complete; a budget that is too long may delay a
    rollout, while a budget that is too short can create restarts.
-   `kubectl rollout status` reports rollout progress, not semantic
    correctness or user-visible SLO success.
-   If the image cannot be pulled, probe configuration is not the cause
    of the initial failure.
-   A failed rollout can reflect a bad probe, bad application config,
    unavailable dependency, resource pressure, unschedulable Pod, failed
    image pull, or controller/cluster issue. Diagnose from evidence
    rather than assuming the probe is wrong.

### L3.6 Pod readiness gates and external conditions

A readiness gate allows additional conditions to participate in Pod
readiness through the documented Pod spec/status mechanism and a
controller or integration that sets the condition. It is useful when an
external system must confirm a condition before a Pod is considered
ready. It is not a probe handler and does not create the external
controller that populates the condition.

`[VERIFY]` Check the exact `readinessGates` field, condition type
behavior, and API semantics in the target version's Pod API reference.
Confirm the owning controller is trusted, has narrowly scoped
permissions, and reports condition transitions reliably. A readiness
gate that is never set can keep Pods unready indefinitely.

### L3.7 Node failure, taints, and tolerations

Kubernetes node-health detection and handling involves kubelet status,
node controller behavior, node conditions, taints such as
`node.kubernetes.io/not-ready` and `node.kubernetes.io/unreachable`, and
Pod tolerations. `tolerationSeconds` can influence how long a Pod
tolerates a matching taint before eviction behavior applies, depending
on the taint, controller, and configuration.

Do not state a universal node-failure detection or eviction time.
Heartbeat intervals, node-monitor settings, controller behavior, API
connectivity, version, and cluster configuration can change the
timeline. `[VERIFY]` Check the current node-pressure/node-failure
documentation and the actual cluster configuration before using exact
values in a runbook.

A Pod restart on a healthy node is not the same as a node failure. A
controller may create replacement Pods after a Pod is considered lost,
but scheduling still requires a feasible node and sufficient capacity.
In a local kind cluster, worker nodes are containers; stopping one can
demonstrate some control-plane observations but does not faithfully
model physical node failure, cloud control-plane behavior, network
partitions, storage failure, or production eviction timing.

### L3.8 Measuring correctness and false-positive restarts

Track probe behavior with an explicitly defined observation window. Do
not assume a standard metric name exists across every stack.

  -----------------------------------------------------------------------
  Indicator               Example definition      Use
  ----------------------- ----------------------- -----------------------
  Time to ready           Timestamp of first      Detect slow
                          stable ready condition  initialization and
                          minus container start   rollout delays
                          time; define whether    
                          restarts reset the      
                          clock                   

  Probe-attributed        Number of restarts with Compare
  restart rate            evidence of             services/versions
                          liveness/startup probe  without using raw
                          failure in a window     counts alone
                          divided by              
                          container-hours or      
                          container-start         
                          opportunities, with     
                          denominator stated      

  False-positive restart  Restarts judged         Assess probe precision;
  rate                    unnecessary after       requires a review label
                          incident review divided or reliable
                          by all restarts         adjudication process
                          attributed to probe     
                          failures in the window  

  Readiness flapping      Count of ready/unready  Find unstable health
                          transitions per Pod per contracts
                          time window, optionally 
                          normalized by Pod-hours 

  Rollout readiness delay Time from rollout start Detect startup
                          or Pod creation to      regressions
                          stable readiness;       
                          define start/end events 
                          consistently            

  User-visible request    Failed eligible         Check whether health
  error rate              requests divided by     signals correlate with
                          total eligible requests user outcomes
                          in a defined window     

  Ready capacity          Ready replicas or       Determine whether
                          measured serving        readiness removal
                          capacity divided by     creates risk
                          required/desired        
                          capacity; state the     
                          capacity model          
  -----------------------------------------------------------------------

A restart count is a clue, not a verdict. Correlate events, previous
logs, termination reason/exit code, probe configuration, latency,
resource pressure, and user-visible errors. Some restarts are correct
recovery; some are caused by application exits; some are caused by
liveness mistakes.

### L3.9 Advanced trade-offs

  ----------------------------------------------------------------------------------------------------------
  Option             Benefit              Cost                               Risk            Choose when
  ------------------ -------------------- ---------------------------------- --------------- ---------------
  Shallow local      Limits               May not detect every business      A silent local  A restart can
  liveness           dependency-induced   deadlock                           failure may     repair a local
                     restart storms                                          persist if no   stuck condition
                                                                             local signal    and
                                                                             detects it      dependencies
                                                                                             may fail
                                                                                             independently

  Dependency-aware   Stops routing normal More logic and potential           Flapping or     A dependency is
  readiness          traffic to an        dependency check load              fleet-wide      essential for
                     instance that cannot                                    unready state   the instance's
                     serve                                                                   request
                                                                                             contract

  Cached dependency  Reduces per-probe    Health can be stale                Instance may    Bounded
  health             fan-out                                                 stay ready      staleness is
                                                                             briefly after   acceptable and
                                                                             dependency      updates are
                                                                             failure         reliable

  Direct bounded     More current view    Adds latency/load to dependency    Cascading load  The check is
  dependency check                                                           during outage   cheap, bounded,
                                                                                             and only one or
                                                                                             few critical
                                                                                             dependencies
                                                                                             exist

  Exec probe         Works for non-HTTP   Process overhead and image         Missing         A purpose-built
                     processes            coupling                           binaries or     local check is
                                                                             brittle scripts the simplest
                                                                                             reliable signal

  Startup probe      Protects slow        Delays liveness-based recovery     Misconfigured   Startup time
                     initialization       during startup                     large budget    varies or is
                                                                             hides a broken  longer than
                                                                             startup         ordinary
                                                                                             liveness budget

  More tolerant      Reduces false        Slower failure detection           Longer stuck    Healthy latency
  thresholds         positives                                               intervals       is variable and
                                                                                             restarts are
                                                                                             costly

  Aggressive         Faster detection     Sensitive to transient delay       Restart storm   The local
  thresholds                                                                 under load      failure signal
                                                                                             is highly
                                                                                             reliable and
                                                                                             rapid recovery
                                                                                             matters

  External readiness Coordinates          Requires                           Gate can remain A verified
  gate               readiness with a     controller/ownership/permissions   false or be     external
                     separate control                                        spoofed         condition must
                     plane                                                                   be met before
                                                                                             serving
  ----------------------------------------------------------------------------------------------------------

## 8. Level 4 --- Expert: Recovery Drills, Runbooks, and Fleet Standards

### L4.1 Safe recovery principles

Kubernetes can observe certain signals and restart or replace workloads
according to its control loops. It cannot automatically repair:

-   a software defect that recurs on every restart;
-   corrupt source data or invalid output;
-   deadlocked business logic that the health check does not observe;
-   a remote service that remains unavailable;
-   invalid credentials or bad configuration;
-   an image that cannot be pulled;
-   duplicate side effects from a retried message;
-   a lost checkpoint or incorrect acknowledgement order;
-   a model that loads successfully but produces incorrect predictions.

Before restarting a workload, ask whether restart is likely to restore
useful service, whether it will amplify load, and whether in-flight work
is safe to repeat. A restart is an operational action, not a correctness
proof.

### L4.2 Restart-safe batch and queue processing

For a batch ETL or consumer, design around at-least-once retry
possibilities unless the actual platform guarantees and application
semantics establish otherwise. Do not claim "exactly once" merely
because a consumer commits offsets.

A robust conceptual pattern:

1.  Read a work item and stable identity (message ID, batch partition,
    or input record key).
2.  Validate input and determine an idempotency key.
3.  Perform side effects through an idempotent upsert, deduplication
    key, or transaction boundary where available.
4.  Persist output/checkpoint only after the intended durable work is
    complete.
5.  Acknowledge/commit the message only when the application's
    documented correctness condition is satisfied.
6.  On restart, resume from a checkpoint that does not skip uncommitted
    work; duplicate delivery should not duplicate externally visible
    effects.
7.  Bound retries, classify permanent versus transient failures, and
    send poison work to an explicit failure path rather than retrying
    forever.
8.  Emit safe progress signals and retain enough evidence to reconcile
    partial completion.

Exact ordering depends on the queue, database, transaction model, and
delivery guarantees. Verify those guarantees in the chosen system's
official docs. This unit does not implement a production queue or
database transaction.

### L4.3 Chaos-style recovery drills: what they prove

A local drill should test a hypothesis and record observations, not
manufacture a claim of production fidelity.

  -----------------------------------------------------------------------------
  Drill             Safe action         Can help demonstrate  Cannot prove
  ----------------- ------------------- --------------------- -----------------
  Pod deletion      Delete one known    A controller may      Node failure
                    Pod in a disposable recreate a Pod to     behavior, zero
                    namespace after     match desired replica downtime, durable
                    context/name guard  count                 state recovery

  Dependency outage Toggle a lab-only   Deep liveness can     Production
                    dependency          cause restarts;       dependency
                    simulator or stop a readiness can remove  timing, network
                    lab-only dependency eligibility           partitions, real
                    container by exact                        database behavior
                    name                                      

  Worker failure    Delete a known      Controller            Real queue
                    worker Pod or       restart/replacement   acknowledgement
                    terminate only a    and application       guarantees or
                    disposable lab      restart behavior      data correctness
                    process                                   

  kind worker       Stop one exact kind Some node-condition   Cloud/physical
  container stop    node container only and replacement       node failure,
                    after verifying     observations          production
                    cluster name and                          eviction timing,
                    container name; use                       storage and
                    a disposable                              network failure
                    cluster only                              fidelity

  Slow              Use bounded         Startup probe's       Real model-load
  initialization    `STARTUP_SECONDS`   gating role           distributions,
                    in a toy app                              GPU
                                                              initialization,
                                                              production
                                                              cold-start
                                                              behavior
  -----------------------------------------------------------------------------

If laptop capacity or runtime makes the node-stop experiment unreliable,
use the inspection/simulation path and record the limitation. Do not
stop arbitrary Docker containers, use wildcards, or run destructive
steps against a shared or production cluster.

### L4.4 Incident case --- liveness tied to a slow dependency took the API down

**\[ILLUSTRATIVE INCIDENT DATA --- not an observed incident\]**

**Service:** five-replica scoring API.\
**Dependency:** shared feature database.\
**Symptom:** elevated request failures, rising container restarts, and
readiness capacity collapsing during database latency spike.

#### Timeline

  -----------------------------------------------------------------------
  Time                    Illustrative            Interpretation
                          observation             
  ----------------------- ----------------------- -----------------------
  10:00:00                Database latency rises; Shared dependency
                          some API requests       degradation begins
                          exceed their deadline   

  10:00:20                Deep `/health/live`     Liveness is measuring
                          requests begin timing   dependency latency
                          out                     rather than local
                                                  recoverability

  10:00:40                Multiple replicas       Probe policy may be
                          restart; previous logs  triggering restarts
                          show no application     
                          crash before probe      
                          failure                 

  10:01:00                Cold model/cache        Restarts amplify
                          initialization          recovery cost
                          increases CPU and       
                          connection churn        

  10:01:30                Ready capacity falls    Traffic concentrates on
                          and user-facing errors  fewer endpoints
                          increase                

  10:03:00                Dependency latency      Recovery lags behind
                          improves, but API       dependency recovery
                          replicas are still      
                          warming                 
  -----------------------------------------------------------------------

Times are illustrative and are not a timing guarantee.

#### Hypotheses and tests

1.  **Hypothesis:** liveness failures precede the restarts.\
    **Test:** inspect Pod events and `describe`; compare probe failure
    timestamps with `lastState`, restart count, and previous logs.
2.  **Hypothesis:** all replicas share the same dependency failure.\
    **Test:** correlate readiness transitions, dependency telemetry, and
    request failures. Do not expose sensitive diagnostics through health
    endpoints.
3.  **Hypothesis:** restart churn is adding load.\
    **Test:** compare startup durations, connection attempts,
    CPU/memory, and dependency request rates before/after mitigation.
4.  **Alternative:** containers are exiting independently or being
    OOM-killed.\
    **Test:** inspect termination reason/exit code, resource limits,
    node pressure, and application logs. Do not assume the probe is root
    cause from restart count alone.

#### Root cause

The liveness endpoint performed a synchronous, slow dependency check and
failed during a shared dependency latency spike. The kubelet interpreted
repeated failures as evidence that restarting the local application was
appropriate. That assumption was wrong for this failure mode.

#### Immediate mitigation

-   If operationally safe and authorized, roll back the probe
    configuration or deploy a reviewed configuration that makes liveness
    local.
-   Preserve events, `describe`, current/previous logs, rollout status,
    and relevant metrics before cleanup.
-   Avoid simultaneously restarting all replicas. Use a controlled
    rollout and monitor ready capacity and user-visible errors.
-   If the API genuinely cannot serve any request without the database,
    readiness may remove endpoints while the process remains running;
    verify that this does not overload remaining replicas.

#### Corrected design

-   Liveness checks local responsiveness or a well-defined local
    unrecoverable state.
-   Readiness checks model initialization and a minimal bounded signal
    for required dependencies.
-   The dependency signal has a timeout and a defined stale-data/refresh
    policy.
-   Application requests use their own bounded dependency timeouts,
    retries with jitter, and circuit-breaking/backpressure where
    appropriate.
-   A startup probe covers model initialization based on measured
    cold-start behavior.
-   Health endpoints expose only minimal status, not credentials or
    stack traces.

#### Prevention and lessons

-   Add probe review to service templates and production readiness
    review.
-   Test dependency outage behavior in a disposable environment before
    rollout.
-   Alert on user-visible errors, ready capacity, and probe-attributed
    restarts together.
-   Canary the new probe policy and watch a defined observation window.
-   Treat a restart as a recovery action with costs, not as a universal
    response to degraded dependencies.

### L4.5 Fleet and organizational controls

1.  **Shared standards:** define endpoint semantics, allowed handlers,
    default timeout/threshold ranges, and rules against deep liveness.
    Standards must remain guidance informed by measurements, not magic
    values.
2.  **Template ownership:** one named platform team owns the base
    template and versioning. Service teams own their dependency contract
    and evidence.
3.  **Exception policy:** require a documented reason, failure-mode
    analysis, blast-radius estimate, owner, expiry/review date, and test
    evidence for unusual probe behavior.
4.  **Review gates:** static checks can flag missing probes or
    suspicious deep-liveness patterns, but cannot prove semantic
    correctness. Require code review and runtime test evidence.
5.  **Version compatibility:** test against supported Kubernetes minors
    and managed/local distributions. Mark gRPC, readiness-gate, and node
    timing assumptions explicitly.
6.  **Rollout monitoring:** canary new templates; watch readiness delay,
    restarts, request errors, and capacity before fleet-wide promotion.
7.  **Safe defaults:** never deploy an unverified new probe policy to
    every service simultaneously.
8.  **Incident learning:** convert false-positive restarts and readiness
    flapping into test cases, not only documentation.
9.  **Ownership and lifecycle:** stale exception records should expire;
    templates should have a deprecation path.
10. **Auditability:** store the manifest version, application version,
    observation window, and actual evidence with each rollout decision.

### L4.6 Node-failure and kind limits

A node-loss drill is optional and only for a disposable cluster. `kind`
models nodes as containers and is excellent for local
API/manifest/control-loop learning, but it is not a faithful simulation
of all production node failure modes. Exact node condition transition,
taint application, toleration handling, eviction, and replacement timing
are version/configuration dependent.

If conducting a node drill:

-   Confirm the exact context and cluster name.
-   Inspect kind node container names before any action.
-   Stop only the explicitly identified worker container belonging to
    the disposable cluster.
-   Capture `kubectl get nodes -o wide`, `kubectl describe node <node>`,
    Pod placement, events, and controller state over time.
-   Do not assume a Pod was evicted or a node failed until the learner
    actually observes it.
-   Restore/cleanup using the exact identified resource and kind
    workflow; never use broad wildcard container commands.

## 9. SRE Lens

### 9.1 Probes are a reliability mechanism, not the reliability design

Probe correctness depends on the application health contract, recovery
semantics, workload topology, dependency behavior, and operational
evidence. A probe that is "green" is not a complete SLI. A probe that
fails is not automatically a user-visible outage. Connect probe
observations to service outcomes.

### 9.2 Useful indicators

Define metric names and labels locally; the names below are descriptive,
not claims of universal built-in metric names.

-   **Time-to-ready:** first stable ready timestamp minus container
    start timestamp. State how restarts and multiple readiness
    transitions are handled.
-   **Probe-attributed restart rate:** count of restarts supported by
    probe-failure evidence divided by container-hours or another
    explicitly stated exposure denominator during a fixed window.
-   **False-positive restart rate:** reviewed restarts classified as
    unnecessary divided by all reviewed probe-attributed restarts in the
    same window. State the classification process and include "unknown"
    rather than guessing.
-   **Readiness flapping:** ready/unready transitions per Pod-hour, with
    an agreed minimum transition gap if debouncing is used in analysis.
-   **Rollout readiness delay:** rollout start to stable ready capacity;
    record rollout version and cluster context.
-   **User-visible error rate:** failed eligible requests divided by all
    eligible requests for the same service/window; define exclusions
    consistently.
-   **Ready capacity:** available serving capacity divided by required
    capacity, using replica count only if replicas are a meaningful
    proxy for throughput.

Do not optimize restart rate to zero without context: a restart can be
correct. Optimize for correct detection and safe recovery.

### 9.3 SLI/SLO connection

Probe status can support availability diagnosis, but user-facing SLIs
should reflect request success and latency. For a scoring API, track
successful valid requests and latency percentiles; for a consumer, track
processing lag/age and durable completion; for ETL, track freshness,
completeness, and successful partition completion. Ready replica count
is a capacity indicator, not a substitute for business outcome. Full SLO
design is deferred to M10.

### 9.4 Blast radius, capacity, and cost

A shared dependency can make every replica's deep health check fail at
once. Restarting all replicas consumes CPU and memory, repeats
initialization, resets caches, creates connection bursts, and can worsen
a dependency incident. Readiness can also remove too much capacity if
every replica depends on the same unavailable service; in that case, the
system needs explicit degraded-mode semantics or a controlled rejection
strategy rather than a probe trick.

Probe traffic scales with replica count and period. Exec probes may
create processes; HTTP probes create requests; deep dependency checks
create downstream work. Startup checks may extend rollout time.
Aggressive readiness transitions can interact with autoscaling and cold
starts: if ready capacity drops while new replicas need long
initialization, scale-up may lag behind demand. Full autoscaler tuning
is Unit 6.

### 9.5 Runbook snippet

**Alert/symptom:** restart count increasing, ready capacity falling, or
elevated request errors.

1.  **Initial read-only triage:** verify context and namespace; capture
    `get pods -o wide`, `describe pod`, events, current/previous logs,
    Deployment status, and user-visible error/latency evidence.
2.  **Hypothesis:** classify likely cause as probe failure, application
    exit, OOM, image pull, configuration, node pressure, scheduling, or
    dependency outage.
3.  **Test:** compare event times, container `lastState`, exit
    code/reason, readiness transitions, dependency latency, and startup
    duration. Change one variable at a time in a canary or lab.
4.  **Mitigation:** if a probe is amplifying a dependency outage, apply
    a reviewed liveness correction through the normal change path; do
    not make unreviewed fleet-wide edits.
5.  **Verify recovery:** confirm stable readiness, lower restart rate,
    restored user-facing request success/latency, and dependency load
    recovery over an agreed window.
6.  **Follow-up:** preserve scrubbed evidence, identify prevention work,
    add a regression test, and review template/exception policy.

## 10. Security Lens

### 10.1 Minimal health endpoints

-   Do not return credentials, tokens, environment variables, connection
    strings, internal stack traces, filesystem paths, model artifact
    locations, or detailed dependency diagnostics from public health
    endpoints.
-   Health endpoints should perform bounded, low-cost work. Do not let a
    probe become an unauthenticated debug or admin endpoint.
-   A lab-only dependency toggle is state-changing and must never be
    exposed in a production service.
-   Exec probes run inside the container's security context. Avoid shell
    injection, arbitrary command execution, unnecessary utilities, and
    assumptions about the image contents.
-   Do not grant privileged mode, host mounts, host PID/network access,
    or broad Kubernetes permissions for probes.
-   Probes do not provide authorization, network isolation,
    vulnerability prevention, or proof of data integrity.

### 10.2 Concrete checks

Inspect the configured probes and container security context:

``` bash
kubectl -n probes-lab get deployment scoring-api -o yaml
kubectl -n probes-lab describe deployment scoring-api
kubectl -n probes-lab get pod -l app.kubernetes.io/name=scoring-api -o yaml
```

Review:

-   health endpoints return only intended fields;
-   no credentials or secrets appear in manifests, command output,
    events, or evidence files;
-   `exec` handlers are narrow and deterministic;
-   container runs non-root where supported and does not require
    unnecessary privileges;
-   no lab-only control route exists in the production build;
-   readiness/liveness checks cannot trigger state mutation;
-   endpoint traffic exposure matches the intended Service and network
    controls.

These commands inspect API objects; they do not prove the endpoint
response contains no sensitive data. Test the actual endpoint and review
application code. Scrub evidence before sharing it.

### 10.3 Security references

-   **Kubernetes documentation, "Security" and "Pod Security
    Standards"** --- use the official Kubernetes documentation site;
    `[VERIFY]` select the current section relevant to workload
    hardening.
-   **NSA/CISA, "Kubernetes Hardening Guidance"** --- relevant as a
    broad hardening source; `[VERIFY]` check the current edition and
    exact recommendation before attributing a specific probe rule.
-   **CIS Kubernetes Benchmark** --- use only the benchmark version and
    controls applicable to the actual cluster distribution; `[VERIFY]`
    do not infer that a benchmark control mandates a particular health
    endpoint design.
-   **Kubernetes API reference for Pod and Probe types** ---
    authoritative for schema and field constraints; `[VERIFY]` match the
    cluster's minor version.

These are source pointers, not a claim that their current contents were
consulted live for this lesson.

## 11. Hands-On Lab Set

### Lab A --- Observe the three probe types

**Goal:** Observe startup gating, readiness changes, and
liveness-triggered restarts as separate effects.

**Estimated footprint:** approximately 1 CPU, 0.5--1.5 GB RAM, and 1--2
GB disk including the local image; actual usage varies by host/runtime.

**Prerequisites:** disposable kind cluster, Docker, `kubectl`, FastAPI
example and Dockerfile from Section 6. `[VERIFY]` Ensure local `kind`
and Kubernetes versions support the manifest fields used.

**Safety/context guard:** Run this before applying or deleting
resources:

``` bash
kubectl config current-context
kubectl get nodes -o wide
```

Proceed only if the context is the explicitly disposable lab cluster.
Use namespace `probes-lab` and the exact resource names in this lesson.

**Steps**

1.  Save the FastAPI example and Dockerfile from Section 6. Replace the
    health handler with the lab-toggle variant only if doing the
    dependency lab; for Lab A, the simple endpoints are enough.

2.  Build and load the image as described in Section 6.4. Confirm `kind`
    cluster name matches `kind load`.

3.  Create namespace and apply the Deployment/Service manifest after
    replacing the image placeholder.

4.  Observe startup while the delay is active:

    ``` bash
    kubectl -n probes-lab get pods -w
    kubectl -n probes-lab describe pod <pod-name>
    kubectl -n probes-lab get events --sort-by=.metadata.creationTimestamp
    ```

5.  After startup, inspect readiness and endpoint state:

    ``` bash
    kubectl -n probes-lab get pods -o wide
    kubectl -n probes-lab get endpointslices -o yaml
    ```

6.  To demonstrate liveness restart in a controlled variant, use a
    lab-only app version with an explicit local liveness-failure toggle,
    and set the toggle only in the disposable app. Do not use a
    dependency outage as a liveness trigger in the corrected design. If
    using the deep-liveness version, label it clearly as the
    anti-pattern and follow Lab C.

7.  Capture `describe`, events, current/previous logs, restart count,
    Pod conditions, and endpoint readiness at each transition.

**Expected evidence:** `environment-and-context.txt`, Pod describe
output before/after, event timeline, restart counts, readiness/endpoint
observations. All sample output is representative until the learner
captures actual output.

**Interpretation questions**

-   Which observation indicates startup completed?
-   What changed when readiness became false?
-   What evidence proves a container restarted rather than a new Pod
    merely being created?
-   Did endpoint state change immediately or after reconciliation?

**Success criteria:** learner explains startup/readiness/liveness
independently and captures actual event/log evidence without calling
expected output "observed."

**Cleanup**

``` bash
kubectl config current-context
kubectl -n probes-lab delete deployment scoring-api --ignore-not-found
kubectl -n probes-lab delete service scoring-api --ignore-not-found
kubectl delete namespace probes-lab --wait=true
kubectl get namespace probes-lab
```

The final command should report that the namespace is not found after
deletion; exact output is version/client-dependent. Verify no lab
resources remain before reusing the namespace.

**Stretch:** repeat with a measured startup delay and compare
time-to-ready under idle versus CPU-loaded local conditions.

**kind caveat:** local timing depends on host scheduling, Docker, WSL2,
cgroups, and nested containers; this is not a production performance
benchmark.

### Lab B --- Slow model initialization and startup probe

**Goal:** Show why a slow but healthy initializer should not be treated
as a dead process.

**Estimated footprint:** 1 CPU, 0.5--1.5 GB RAM, 1--2 GB disk for
image/build cache.

**Prerequisites:** Lab A app and local image. The example uses a bounded
sleep as a model-load simulation, not a real ML model.

**Safety/context guard**

``` bash
kubectl config current-context
kubectl get nodes -o wide
```

Only continue in the disposable cluster.

**Steps**

1.  Build the app with `STARTUP_SECONDS=25` as an illustrative slow
    initialization. For example, set the environment variable in the
    Deployment, not in a shared environment.

2.  Create two test Deployments in the lab namespace using distinct
    labels/names: one with an appropriate startup probe and one
    comparison variant without it. Use a separate manifest for each;
    ensure selectors do not overlap.

3.  In the no-startup-probe variant, configure liveness to begin early
    enough that the deliberately slow app can fail liveness before
    initialization finishes. This is a controlled comparison only; label
    the manifest `ANTI-PATTERN — COMPARISON ONLY`.

4.  Observe each Pod's events, restarts, readiness timeline, and rollout
    status:

    ``` bash
    kubectl -n probes-lab get pods -w
    kubectl -n probes-lab describe pod <pod-name>
    kubectl -n probes-lab get events --sort-by=.metadata.creationTimestamp
    kubectl -n probes-lab rollout status deployment/<deployment-name> --timeout=180s
    ```

5.  Record the configured delay and actual observed times. Do not report
    a synthetic sleep duration as a measured production model-load
    distribution.

6.  Restore the corrected manifest and verify the app becomes ready
    without unnecessary restarts.

**Expected evidence:** both manifests, creation/startup timestamps,
events, restart count, time-to-ready calculation, and interpretation of
any version-specific difference. Representative examples are not
observations.

**Interpretation questions**

-   Did the no-startup variant restart before the application could
    initialize?
-   How did the startup probe gate liveness/readiness?
-   How much margin is justified by actual cold-start measurements?
-   What other root causes could make a startup probe fail?

**Success criteria:** explain the trade-off between too-small and
too-large startup budgets and identify the sleep as a simulation.

**Cleanup**

``` bash
kubectl config current-context
kubectl -n probes-lab delete deployment slow-start-with-startup slow-start-without-startup --ignore-not-found
kubectl -n probes-lab get deployments
```

Verify the two named test Deployments are absent; then clean up the
namespace when all labs are complete.

**Stretch:** repeat with CPU limits and compare startup distribution. Do
not treat a single local run as a statistically reliable percentile.

**kind caveat:** local scheduling and container limits can distort
timing; this lab demonstrates control flow, not production cold-start
latency.

### Lab C --- Mandatory deep-liveness dependency restart storm

**Goal:** Demonstrate the dangerous pattern in an isolated lab, capture
a before/after timeline, then correct it.

**Estimated footprint:** 1--2 CPU, 1--2 GB RAM, 2--3 GB disk for
image/cache. Keep replicas low and the outage bounded.

**Prerequisites:** a disposable kind cluster; lab-only FastAPI
dependency toggle from Section 6.2; local image; `kubectl`; `curl` from
a local client or a temporary in-cluster client image the learner
controls.

**Safety rules**

-   This is the only lab that deliberately includes the **ANTI-PATTERN
    --- DO NOT COPY**.
-   Never run it against a production/shared cluster.
-   Use one replica and a lab-only namespace.
-   Set a short, explicit outage window and restore dependency state
    immediately after evidence capture.
-   The dependency toggle route is intentionally unsafe for production
    and must not be included in a production image.
-   If any context/name check is uncertain, stop without applying or
    deleting anything.

**Context guard**

``` bash
kubectl config current-context
kubectl get nodes -o wide
kubectl get namespace probes-lab
```

Verify that the context is the disposable kind cluster you created for
this lesson. If the cluster name/context is not recognizable, stop.

**Step 1 --- Build the flawed variant**

For the flawed lab version only, make `/health/live` fail when the
simulated dependency flag is false. Do not combine this with the
corrected design. The deliberately flawed handler has the following
semantics:

``` python
@app.get("/health/live")
async def live(response: Response):
    # ANTI-PATTERN — DO NOT COPY:
    # liveness fails when a shared dependency is simulated as unavailable.
    if not dependency_ok:
        response.status_code = 503
        return {"status": "dependency-unavailable"}
    return {"status": "live"}
```

Use the guarded lab toggle route from Section 6.2. Keep readiness
dependency-aware as well. Build a clearly distinct image tag, for
example `probes-lab-deep-live:0.1.0`, and import it into the disposable
kind cluster. Do not reuse this image for production.

**Step 2 --- Apply the flawed manifest**

Use a one-replica Deployment with a short but bounded liveness
configuration so the effect is visible in a local lab. The following
values are **illustrative lab settings**, not production
recommendations:

``` yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: deep-live-demo
  namespace: probes-lab
  labels:
    app.kubernetes.io/name: deep-live-demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: deep-live-demo
  template:
    metadata:
      labels:
        app.kubernetes.io/name: deep-live-demo
    spec:
      containers:
        - name: api
          image: probes-lab-deep-live:0.1.0
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 8000
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
          livenessProbe:
            httpGet:
              path: /health/live
              port: http
            periodSeconds: 3
            timeoutSeconds: 1
            failureThreshold: 2
          readinessProbe:
            httpGet:
              path: /health/ready
              port: http
            periodSeconds: 3
            timeoutSeconds: 1
            failureThreshold: 1
```

Apply the manifest only after confirming the local image exists in the
kind nodes. Use `kubectl apply -f <your-lab-manifest.yaml>` with the
exact file you created. Then wait for the Pod to become ready before
starting the outage.

**Step 3 --- Capture baseline**

``` bash
date -Is
kubectl -n probes-lab get pods -o wide
kubectl -n probes-lab describe pod <pod-name>
kubectl -n probes-lab get events --sort-by=.metadata.creationTimestamp
kubectl -n probes-lab logs <pod-name> --all-containers=true
kubectl -n probes-lab get endpointslices -o yaml
```

Save outputs as `probe-timeline-before.txt`, `pod-describe-before.txt`,
and `events-before.txt`. Use actual outputs; redact any sensitive data.

**Step 4 --- Stop the simulated dependency**

From a local client that can reach the lab Pod, call the lab-only state
toggle route using port-forwarding:

``` bash
kubectl -n probes-lab port-forward deployment/deep-live-demo 18000:8000
```

In another terminal, confirm context, then:

``` bash
curl -i http://127.0.0.1:18000/lab/dependency/down
date -Is
```

This does not stop a real database. It toggles the sample app's
in-memory dependency state. This is intentionally safer and more
repeatable than killing an arbitrary dependency container. It
demonstrates the health-contract error, not real database latency or
connection failure.

**Step 5 --- Observe the flawed behavior**

For a bounded period, capture:

``` bash
date -Is
kubectl -n probes-lab get pods -w
kubectl -n probes-lab get events --sort-by=.metadata.creationTimestamp
kubectl -n probes-lab describe pod <pod-name>
kubectl -n probes-lab logs <pod-name> --all-containers=true
kubectl -n probes-lab logs <pod-name> --previous
kubectl -n probes-lab get endpointslices -o yaml
```

Capture restart count and container `lastState`. If the Pod restarts
before you can restore the toggle, the in-memory flag may reset to its
default on restart; record this as a limitation and re-trigger only if
safe. The sample is a simulator, not a persistent dependency service.

**Expected versus observed:** expected pattern is repeated liveness
failures and container restarts while the simulated dependency is down.
It is not guaranteed to happen on a precise schedule. If it does not
occur, inspect whether the correct image/handler was loaded, whether the
route state persisted, and whether the probe is configured as intended.
Do not claim a restart storm unless evidence shows repeated restarts.

**Step 6 --- Correct the design**

Change `/health/live` to check only local responsiveness. Keep
`/health/ready` dependency-aware with bounded behavior. Remove the lab
toggle route from the corrected image. Build/import a new tag and update
the Deployment through the manifest. If the dependency is down,
readiness should become false while liveness remains successful; the
process should not restart solely because the simulated dependency is
unavailable.

**Step 7 --- Repeat and compare**

Capture the same commands and save `probe-timeline-after.txt`,
`pod-describe-after.txt`, `events-after.txt`, logs, restart counts, and
endpoint state. Compare timestamps and transition sequences rather than
only total restart counts.

  -----------------------------------------------------------------------
  Observation             Before: deep liveness   After: local liveness
  ----------------------- ----------------------- -----------------------
  Dependency state        Unavailable in          Unavailable in
                          simulator               simulator

  Liveness result         Expected to fail under  Expected to remain
                          the flawed contract     successful if local
                                                  handler is healthy

  Readiness               Expected false while    Expected false while
                          dependency unavailable  dependency unavailable

  Restart count           May increase due to     Should not increase
                          liveness failures       solely due to
                                                  dependency readiness
                                                  failure

  Service endpoint        Readiness               Same readiness
  eligibility             reconciliation may      principle applies
                          remove the endpoint     

  Evidence required       Events/describe/logs    Same evidence, same
                          must show what happened observation window
  -----------------------------------------------------------------------

**Interpretation questions**

-   Did liveness failure precede the restart?
-   Was readiness false in both versions?
-   Did the endpoint state follow readiness after reconciliation?
-   Did restarting reset the simulated dependency state?
-   Which observations are a simulator artifact rather than a production
    guarantee?
-   Could a deep readiness check itself overload a real dependency?

**Success criteria:** the learner has a before/after evidence set and
can explain why the corrected design separates local recoverability from
dependency availability.

**Cleanup**

``` bash
kubectl config current-context
kubectl -n probes-lab delete deployment deep-live-demo --ignore-not-found
kubectl -n probes-lab delete service deep-live-demo --ignore-not-found
kubectl -n probes-lab get pods
```

Verify the exact named Deployment/Service are absent. After all labs,
delete the namespace and verify absence. Do not run broad Docker
cleanup.

**Stretch:** implement a bounded cached dependency-health signal and
document the maximum acceptable staleness and failure behavior.

**kind caveat:** the dependency is simulated by application state; it
does not model network partitions, connection pool exhaustion, database
locks, or production dependency timing. kind is not a benchmark.

### Lab D --- Worker health and recovery drill

**Goal:** Explore health for a worker with no HTTP endpoint, including
the limits of a heartbeat.

**Estimated footprint:** under 1 CPU, 0.5 GB RAM, negligible disk beyond
the local image/cluster.

**Prerequisites:** Python 3 or a small shell/Python worker in a
disposable image; disposable kind cluster; `kubectl`. Use a
purpose-built script instead of assuming a distroless image contains
shell utilities.

**Safety/context guard**

``` bash
kubectl config current-context
kubectl get nodes -o wide
```

Only use the disposable cluster and a namespace dedicated to this lab.

**Inline worker example**

Save as `worker.py` in the learner's working directory:

``` python
import os
import time
from pathlib import Path

heartbeat = Path(os.getenv("HEARTBEAT_PATH", "/tmp/worker-heartbeat"))
mode = os.getenv("WORKER_MODE", "progress")

while True:
    if mode == "deadlocked":
        # Illustrative failure: process remains alive but stops updating progress.
        while True:
            time.sleep(60)
    heartbeat.write_text(str(time.monotonic()), encoding="utf-8")
    time.sleep(2)
```

A simplistic exec probe could call a purpose-built checker that
validates heartbeat freshness, but avoid shell assumptions. In a
production image, include a small checker executable intentionally,
define how it distinguishes a current process from stale state, and
bound its execution time. The sample above is not a production queue
consumer and does not implement acknowledgements or checkpoints.

**Steps**

1.  Build a local worker image with `worker.py` and a small checker
    script; run it in a single-replica Deployment in the lab namespace.

2.  Establish baseline heartbeat updates and record the interval.

3.  Switch the lab worker into `deadlocked` mode by changing the
    Deployment environment and applying the change. This causes a Pod
    replacement, so it is not a perfect "process becomes deadlocked in
    place" simulation; record that limitation. Alternatively, include a
    lab-only control signal inside a purpose-built process if you need
    in-place state change.

4.  Observe whether a heartbeat-based check fails and whether a restart
    occurs. Distinguish a restart in the same Pod from a
    controller-created replacement Pod.

5.  Delete only the known worker Pod after verifying context and name:

    ``` bash
    kubectl config current-context
    kubectl -n probes-lab get pods -o wide
    kubectl -n probes-lab delete pod <exact-worker-pod-name>
    kubectl -n probes-lab get pods -w
    ```

    This delete is allowed only in the disposable lab namespace. Do not
    substitute a wildcard or a real workload name.

6.  Record heartbeat age, Pod UID/name changes, restart count, events,
    and controller behavior. Discuss how a stale heartbeat could be a
    false positive if the worker is legitimately idle or a false
    negative if a separate timer still runs while work is deadlocked.

**Expected evidence:** worker health observations, `describe`, event
timeline, heartbeat values/ages, restart/replacement observations, and a
short note on false positives/false negatives. Output is representative
until captured.

**Interpretation questions**

-   Does the heartbeat represent process liveness or useful work
    progress?
-   How would the design handle an idle queue?
-   How would the design distinguish a stale file from a new process?
-   What application state must be checkpointed before restart?

**Success criteria:** learner defines the worker's progress contract,
describes the heartbeat limitations, and safely observes one named Pod
deletion/replacement.

**Cleanup**

``` bash
kubectl config current-context
kubectl -n probes-lab delete deployment worker-health-demo --ignore-not-found
kubectl -n probes-lab get pods
```

Verify the named Deployment is absent. Delete the namespace after all
labs and verify it is gone.

**Stretch:** add a monotonic progress counter that increments only after
a work item is durably completed; explain why a timer heartbeat is
weaker.

**kind caveat:** this is a local toy worker. It does not prove real
queue delivery, offset/acknowledgement, or exactly-once processing
semantics.

### Optional Lab E --- Restart-safe batch processing simulation

**Goal:** Demonstrate idempotency and checkpoint order without claiming
a real queue guarantee.

**Estimated footprint:** under 1 CPU, under 0.5 GB RAM, negligible disk.

**Inline toy logic**

``` python
def process_batch(items, completed_keys, output):
    """Illustrative in-memory simulation, not durable exactly-once processing."""
    for item in items:
        key = item["id"]
        if key in completed_keys:
            continue
        # In a real system, the side effect and idempotency record need a durable
        # atomicity strategy appropriate to the database/queue.
        output[key] = item["value"] * 2
        completed_keys.add(key)
```

Run the same batch twice and observe that the in-memory set avoids
duplicate effects in this process. Then explain why a process restart
loses the set unless it is persisted, and why separate writes to output
and checkpoint can still create duplicates or loss. A real
implementation needs a durable transaction/idempotency design suited to
its data store and queue guarantees.

**Success criteria:** learner states the difference between a toy set
and a durable idempotency mechanism, and identifies the point at which a
checkpoint/acknowledgement becomes safe.

**Cleanup:** remove the local temporary working directory only after
confirming it contains no evidence the learner needs. No cluster
resources are required for this optional simulation.

## 12. Production Checklist

Mark each item only after evidence or review. This checklist does not
guarantee readiness or uptime.

### Probe semantics and timing

-   [ ] **Design/review:** liveness detects a local condition for which
    restart is a defensible recovery action.
-   [ ] **Design/review:** readiness represents whether this instance
    should receive normal traffic.
-   [ ] **Design/review:** startup probe protects measured
    initialization time and has a justified bounded budget.
-   [ ] **Command/review:** handler type is supported by the target
    Kubernetes version; gRPC/API details are `[VERIFY]` checked.
-   [ ] **Design/review:** `timeoutSeconds`, `periodSeconds`,
    `failureThreshold`, `successThreshold`, and startup budget have
    written rationale.
-   [ ] **Evidence:** timing and response latency were measured under
    normal and representative loaded conditions.
-   [ ] **Design/review:** readiness remains stable during expected
    transient conditions and has a defined dependency policy.
-   [ ] **Design/review:** health endpoints are cheap, bounded,
    repeatable, and read-only.
-   [ ] **Design/review:** no liveness check depends on a shared remote
    dependency without an approved exception and evidence.

### Application and recovery

-   [ ] **Command:** startup, liveness, readiness, and dependency
    behavior are tested independently.
-   [ ] **Review:** model loading and initialization failures have clear
    logs and do not expose sensitive details through health endpoints.
-   [ ] **Review:** worker progress semantics are explicit; a timer
    heartbeat is not mistaken for completed work.
-   [ ] **Review:** retry, idempotency, checkpoint, duplicate handling,
    and acknowledgement order are documented.
-   [ ] **Review:** a restart does not silently lose work or repeat
    unsafe side effects.
-   [ ] **Command:** image-pull failures and init-container failures are
    diagnosed separately from probe failures.
-   [ ] **Command:** container state, `lastState`, restart count, Pod
    conditions, and events are captured during an incident.
-   [ ] **Review:** controller replacement, scheduling, node failure,
    and application recovery are not conflated.

### Traffic, rollout, and capacity

-   [ ] **Command:** Service endpoint/readiness behavior is observed
    using the supported EndpointSlice API or equivalent.
-   [ ] **Command:** Deployment status and `kubectl rollout status` are
    reviewed; rollout status is not treated as correctness proof.
-   [ ] **Review:** `minReadySeconds` and `progressDeadlineSeconds` are
    understood for the target Deployment.
-   [ ] **Review:** readiness removal cannot leave the service with
    insufficient serving capacity without alerting/mitigation.
-   [ ] **Review:** probe cost and dependency fan-out are included in
    capacity estimates.
-   [ ] **Review:** startup delays and cold starts are considered in
    scale-up and rollout planning; full tuning is deferred to Unit 6.
-   [ ] **Review:** node-failure/toleration assumptions are marked
    `[VERIFY]` and are not stated as universal timing guarantees.

### Security and operations

-   [ ] **Command/review:** no health response or evidence file includes
    secrets, credentials, tokens, environment dumps, or stack traces.
-   [ ] **Review:** exec probes use minimal, known commands and do not
    assume tools exist in distroless images.
-   [ ] **Review:** no privileged container, host access, or broad RBAC
    is introduced for health checks.
-   [ ] **Review:** probe templates have an owner, compatibility policy,
    exception process, and expiry/review date.
-   [ ] **Review:** new defaults are canaried before fleet-wide rollout.
-   [ ] **Evidence:** restart rate, false-positive classifications,
    readiness flapping, time-to-ready, and user-visible outcomes are
    measured with defined denominators/windows.
-   [ ] **Evidence:** runbook includes read-only triage, hypothesis,
    test, mitigation, verification, and follow-up.
-   [ ] **Review:** `kind` simulation limitations are documented and no
    production fidelity is claimed.
-   [ ] **Command:** all lab resources are cleaned up and cleanup is
    verified.

## 13. Self-Check Questions and Answer Key

### Q1 --- Database outage and restart storm \[L2/L3\]

A shared database slows down. All API replicas have a liveness endpoint
that synchronously queries that database. Restarts increase. What is the
leading hypothesis and the safer default design?

**Answer:** The liveness check is coupling a shared dependency's
availability to local process restart. Confirm with event timestamps,
`describe`, previous logs, database latency, and restart history. Keep
liveness local and use bounded readiness semantics for whether the
instance can serve requests. A database outage does not automatically
mean restarting every API process will help.

**Tempting wrong answer:** "Increase replicas immediately." More
replicas may increase dependency load and does not fix the incorrect
health contract.

### Q2 --- Distinguish the three probes \[L1\]

What is the direct effect of readiness failure versus liveness failure,
and how does startup fit?

**Answer:** Readiness marks the instance not ready for normal traffic
and does not itself restart the container. Liveness failure can lead to
container restart after the configured failure condition, subject to
restart policy. Startup probing protects initialization and gates
liveness/readiness until startup succeeds according to documented
behavior.

**Tempting wrong answer:** "All failed probes restart the Pod." They
have different semantics, and a container restart is not the same as Pod
replacement.

### Q3 --- Diagnose `CrashLoopBackOff` \[L1/L2\]

A Pod shows `CrashLoopBackOff` and five restarts. What does that prove,
and what do you inspect?

**Answer:** It indicates repeated restart/backoff behavior, not the root
cause or Pod phase. Inspect `describe`, current and previous logs,
`lastState`, exit code/reason, events, probe settings, configuration,
OOM/node pressure, and image/runtime issues.

**Tempting wrong answer:** "The liveness probe is wrong." It may be, but
application exits, OOM kills, bad config, and other failures are
possible.

### Q4 --- Slow model initialization \[L2\]

A model takes 60 seconds to initialize, but liveness begins failing
after 10 seconds. What should be changed?

**Answer:** Measure cold-start behavior and configure an appropriate
startup probe budget so liveness/readiness probing is gated during
initialization. Then ensure readiness stays false until the model is
actually usable. Avoid copying an arbitrary large budget; too large a
budget delays detection of broken startup.

**Tempting wrong answer:** "Set liveness timeout to 60 seconds." A
per-probe timeout is not the same as a startup budget and may make every
health request slow.

### Q5 --- Worker without HTTP \[L3\]

A consumer has no HTTP server. Is a heartbeat file sufficient to prove
health?

**Answer:** Not by itself. A file can be stale, updated by an unrelated
timer, or fresh while the business loop is deadlocked. Define whether
the signal represents process liveness or actual progress, account for
idle periods and clock assumptions, and pair it with lag/age/completion
observability. Use a minimal exec checker only if the image includes it
and its overhead is acceptable.

**Tempting wrong answer:** "Check that the file exists." Existence says
little about freshness or progress.

### Q6 --- Image pull or probe failure? \[L2\]

A Pod has `ImagePullBackOff` and no container has started. Should you
relax the liveness probe?

**Answer:** No. Probe execution cannot fix a container that cannot be
pulled/started. Inspect the image reference, tag/digest, registry
reachability/authentication, imagePullSecrets, architecture, local kind
image import, and events.

**Tempting wrong answer:** "Increase `initialDelaySeconds`." There is no
running container to probe.

### Q7 --- Restart-safe queue consumer \[L4\]

A worker writes an output row and then acknowledges a message. It
crashes between those steps and receives the message again. How do you
prevent duplicate output?

**Answer:** Use a stable idempotency key/deduplication strategy and a
durable side-effect/checkpoint design consistent with the queue and
database guarantees. Make repeated processing safe; choose
transaction/commit ordering based on documented semantics. Do not claim
exactly-once behavior from the probe or restart policy.

**Tempting wrong answer:** "Use liveness to restart faster." Restart
speed does not provide idempotency.

### Q8 --- Node failure and kind \[L3/L4\]

A kind worker container stops. Can the learner conclude that production
Pods are evicted after a fixed number of seconds?

**Answer:** No. kind nodes are containers and do not model every
production failure mode. Node detection, taints, toleration seconds,
eviction, controller replacement, and scheduling depend on
version/configuration and actual observations. Record the local
timeline, verify current docs, and state the simulation's limits.

**Tempting wrong answer:** "Yes, Kubernetes always evicts after X
seconds." There is no universal guarantee suitable for all
configurations.

### Q9 --- Readiness false but process alive \[L2/L3\]

A Pod is `Running` but `0/1` ready. Is it necessarily broken?

**Answer:** No. `Running` describes a Pod phase and does not mean it is
ready. Readiness can be false due to startup, dependency state, or
another readiness condition. Inspect Pod conditions, container states,
probe results, events, and application behavior.

**Tempting wrong answer:** "Restart it." First determine why it is not
ready and whether restart would help.

### Q10 --- Restart count rises after a release \[L3/L4\]

What evidence is needed before labeling the new probe policy a failure?

**Answer:** Compare restart attribution (events/probe failures/exit
reasons), readiness transitions, startup times, logs, user-visible
errors/latency, resource pressure, and a consistent observation window.
Distinguish expected recovery from false positives and compare against
the previous version/canary.

**Tempting wrong answer:** "Any increase in restart count proves the
probe is bad." Some restarts are appropriate, and counts need context.

## 14. Evidence Artifacts

Suggested learner-created directory; this lesson does **not** create it
automatically:

``` text
evidence/
└── m03-unit-03-probes-recovery/
    ├── environment-and-context.txt
    ├── app-source-and-tests.txt
    ├── deployment-before.yaml
    ├── deployment-after.yaml
    ├── probe-timeline-before.txt
    ├── probe-timeline-after.txt
    ├── pod-describe-before.txt
    ├── pod-describe-after.txt
    ├── events-before.txt
    ├── events-after.txt
    ├── logs-and-restart-counts.txt
    ├── readiness-endpoint-observations.txt
    ├── worker-health-observations.txt
    ├── recovery-runbook-exercise.md
    └── learner-design-decisions.md
```

  ----------------------------------------------------------------------------------------------------------------------------
  Artifact                                What it should contain                                       Review notes
  --------------------------------------- ------------------------------------------------------------ -----------------------
  `environment-and-context.txt`           Date/time, OS/runtime, kind version, Kubernetes server       Do not include
                                          version, kubectl version, cluster name/context, node count,  credentials, tokens, or
                                          namespace                                                    private host details
                                                                                                       beyond what is
                                                                                                       necessary

  `app-source-and-tests.txt`              Exact source variant used, dependency versions, test command Preserve the version
                                          and actual result                                            that produced the
                                                                                                       observations; redact
                                                                                                       secrets

  `deployment-before.yaml`                Exact flawed or comparison manifest before correction        Clearly label the
                                                                                                       deep-liveness variant
                                                                                                       as anti-pattern

  `deployment-after.yaml`                 Corrected local-liveness/dependency-readiness manifest       Record image tag/digest
                                                                                                       used

  `probe-timeline-before.txt`             Timestamped commands and observations before correction      Distinguish wall-clock
                                                                                                       timestamps from
                                                                                                       approximate elapsed
                                                                                                       times

  `probe-timeline-after.txt`              Same capture procedure after correction                      Use the same
                                                                                                       observation window
                                                                                                       where feasible

  `pod-describe-before.txt`               Full `describe` output before correction                     Redact any sensitive
                                                                                                       labels/annotations or
                                                                                                       environment data

  `pod-describe-after.txt`                Full `describe` output after correction                      Capture actual state,
                                                                                                       not a reconstructed
                                                                                                       expected output

  `events-before.txt`                     `kubectl get events --sort-by=.metadata.creationTimestamp`   Events may be
                                          before correction                                            aggregated or expire;
                                                                                                       capture promptly

  `events-after.txt`                      Same command after correction                                Include context and
                                                                                                       capture timestamp

  `logs-and-restart-counts.txt`           Current and previous logs, restart counts, last termination  Scrub secrets, user
                                          reason, relevant timestamps                                  data, and stack traces
                                                                                                       not needed for the
                                                                                                       lesson

  `readiness-endpoint-observations.txt`   HTTP status/body from health endpoints and EndpointSlice     Label expected output
                                          observations                                                 separately from actual
                                                                                                       output

  `worker-health-observations.txt`        Heartbeat/progress signal, Pod state, deletion/replacement   State what the signal
                                          observations                                                 means and its
                                                                                                       limitations

  `recovery-runbook-exercise.md`          Symptom, hypothesis, tests, mitigation, verification,        Include a safe
                                          follow-up                                                    rollback/stop condition

  `learner-design-decisions.md`           Probe contract, timing rationale, failure-mode analysis,     Include why each
                                          alternatives, unresolved verification items                  threshold was chosen
                                                                                                       and the data used
  ----------------------------------------------------------------------------------------------------------------------------

Evidence must clearly separate: - **Expected/representative output:** a
predicted pattern from the lesson. - **Actual observed output:** copied
from the learner's own run with context, timestamp, and version. -
**Interpretation:** the learner's explanation of what the evidence
proves and does not prove.

Do not store secrets in the evidence folder. Scrub tokens, credentials,
connection strings, customer data, internal hostnames, and unnecessary
stack traces before sharing evidence.

## 15. Interview and Design-Review Questions

### 1. A scoring API's liveness endpoint queries a feature database. During a database outage, every replica restarts. How would you redesign it?

**Senior-level model answer:** I would first establish causality from
probe-failure events, container `lastState`, previous logs, dependency
latency, readiness transitions, and request outcomes. I would move
liveness to a local recoverability signal and use readiness for the
minimum dependency condition required to serve requests, with bounded
work and a documented stale-health policy. I would assess whether every
replica becoming unready creates a capacity cliff and whether
degraded-mode responses are possible. I would test the change with a
dependency-outage drill, compare restart/readiness timelines, canary it,
and monitor user-visible error rate and ready capacity. I would not
assume readiness alone fixes the underlying dependency outage.

### 2. How do you select startup, liveness, and readiness thresholds for a model-serving service with variable cold starts?

**Senior-level model answer:** I would measure cold-start distributions
across representative image, model, hardware, cache, and resource
conditions. Startup budget would cover the measured distribution plus an
explicit safety margin, while still bounding how long a broken startup
can remain undetected. Liveness would begin after startup and target a
local condition where restart is likely to help. Readiness would remain
false until the model and required serving path are usable. I would test
under CPU throttling and dependency degradation, examine false-positive
restart rate and time-to-ready, and canary the policy. I would avoid
presenting a product of timing fields as an exact deadline.

### 3. A worker has no HTTP endpoint. What health contract would you use, and what failure modes remain?

**Senior-level model answer:** I would define separate process-liveness
and progress signals. A purpose-built exec check may inspect local
worker state, but I would account for process overhead and image
contents. A progress heartbeat should advance only on a meaningful
milestone and must account for legitimate idleness, stale state across
restarts, and clock behavior. Queue lag, oldest-work age, completion
rate, and failed-work counts should be monitored separately. I would not
make every delayed message a liveness failure; I would classify
dependency outages, backpressure, poison messages, and local deadlocks
before deciding whether restart is useful.

### 4. A Deployment rollout stalls with new Pods unready. How do you determine whether probes are responsible?

**Senior-level model answer:** I would inspect Deployment
status/conditions and rollout status, then inspect representative new
Pods: events, container state, image pull status, init containers,
startup/liveness/readiness failures, logs, resource requests/limits,
scheduling, and dependency health. I would check whether the endpoint
contract matches startup and dependency semantics. `minReadySeconds` and
`progressDeadlineSeconds` affect rollout interpretation but do not prove
application correctness. I would compare against the previous version
and use a controlled rollback if user impact is material. I would not
relax probes before establishing the cause.

### 5. What controls would prevent one faulty probe template from causing a fleet-wide incident?

**Senior-level model answer:** I would version shared templates, assign
ownership, define probe semantics and exception policy, test across
supported Kubernetes versions, and require service-specific dependency
contracts. Static policy can flag suspicious deep liveness and missing
probes, but runtime drills are needed to validate semantics. Changes
would be canaried with rollout monitoring and clear rollback criteria. I
would track time-to-ready, probe-attributed restart rate, readiness
flapping, ready capacity, and user-visible outcomes. Exceptions would
have evidence, an owner, a review/expiry date, and a blast-radius
analysis.

## 16. Sources, Claim Register, and Verification Notes

### Source hierarchy and live-verification status

This lesson was drafted without live verification of official
documentation. The sources below are canonical document titles or stable
entry points to check; the claim register does not imply that their
current pages were opened or that any commands were executed. Where an
exact API detail, default, timing, or compatibility point may vary, it
is explicitly marked `[VERIFY]`.

Primary sources to consult before using this lesson as a production
standard:

1.  Kubernetes documentation, **"Configure Liveness, Readiness and
    Startup Probes"** --- canonical concepts and probe configuration.
    URL:
    `https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/`
2.  Kubernetes documentation, **"Pod Lifecycle"** --- Pod phases,
    container states, restart behavior, and lifecycle concepts. URL:
    `https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/`
3.  Kubernetes API reference, **Probe / HTTPGetAction / TCPSocketAction
    / ExecAction / GRPCAction** --- exact fields and constraints for the
    cluster minor version. Entry point:
    `https://kubernetes.io/docs/reference/kubernetes-api/`
4.  Kubernetes documentation, **"Services"** and EndpointSlices ---
    endpoint and traffic concepts. URL:
    `https://kubernetes.io/docs/concepts/services-networking/service/`
5.  Kubernetes documentation, **"Deployments"** --- rollout progress,
    availability, and relevant fields. URL:
    `https://kubernetes.io/docs/concepts/workloads/controllers/deployment/`
6.  Kubernetes documentation, **"Nodes"** and node-pressure /
    node-failure handling --- node conditions, taints, and tolerations.
    URL: `https://kubernetes.io/docs/concepts/architecture/nodes/`
7.  Kubernetes documentation, **"Init Containers"** --- initialization
    ordering and failure behavior. URL:
    `https://kubernetes.io/docs/concepts/workloads/pods/init-containers/`
8.  kind documentation, **Quick Start / configuration / known
    limitations** --- local cluster creation and node-container caveats.
    URL: `https://kind.sigs.k8s.io/`
9.  FastAPI documentation, **Testing** and application lifespan events
    --- test-client and startup behavior. URL:
    `https://fastapi.tiangolo.com/`
10. Uvicorn documentation --- server invocation and runtime behavior.
    URL: `https://www.uvicorn.org/`
11. Google, **Site Reliability Engineering** book and workbook ---
    cascading failures, monitoring, incident response. Entry point:
    `https://sre.google/books/`
12. NSA/CISA, **"Kubernetes Hardening Guidance"** --- general Kubernetes
    security recommendations. `[VERIFY]` Check current edition and exact
    recommendation.
13. CIS, **"CIS Kubernetes Benchmark"** ---
    distribution/version-specific security benchmark. `[VERIFY]` Check
    the applicable benchmark edition and controls.

If any canonical URL redirects or the relevant page is moved, navigate
from the publisher's official documentation site and record the exact
page consulted. Do not cite a section number unless verified.

### Claim Register

Confidence describes confidence in the general statement, not proof that
the current version-specific documentation was checked. Since no live
source consultation occurred during this drafting task, source
verification remains open for all claims marked `[VERIFY]`.

  ------------------------------------------------------------------------------------------------------------------------
  ID             Claim                                    Source document +         Confidence     Tag / verification
                                                          section/title                            needed
  -------------- ---------------------------------------- ------------------------- -------------- -----------------------
  C01            Startup probes are intended to protect   Kubernetes, "Configure    High           `[VERIFY]` Confirm
                 slow application initialization and gate Liveness, Readiness and                  current behavior and
                 liveness/readiness probing until startup Startup Probes"                          any version-specific
                 succeeds.                                                                         edge cases

  C02            Readiness failure does not itself        Kubernetes, "Configure    High           `[VERIFY]` Validate
                 restart the container; it changes        Liveness, Readiness and                  against target version
                 readiness state.                         Startup Probes"                          and restart-policy
                                                                                                   context

  C03            Liveness failure can lead to container   Kubernetes, "Configure    High           `[VERIFY]` Check
                 restart according to kubelet/probe and   Liveness, Readiness and                  current API constraints
                 restart-policy behavior.                 Startup Probes"; Pod API                 and exact semantics
                                                          reference                                

  C04            TCP probes verify connection             Kubernetes, "Configure    High           General semantic claim;
                 establishment, not application-level     Liveness, Readiness and                  confirm current wording
                 correctness.                             Startup Probes"                          

  C05            Exec probes execute a command in the     Kubernetes, "Configure    High           `[VERIFY]` Check exact
                 container context and may add            Liveness, Readiness and                  execution details and
                 process/resource overhead.               Startup Probes"; Probe                   field constraints
                                                          API reference                            

  C06            gRPC probe support and fields have       Kubernetes Probe API      High           `[VERIFY]` Verify
                 version-specific constraints and should  reference; probe                         target minor, health
                 be checked against the target API.       configuration docs                       protocol behavior,
                                                                                                   TLS/auth limitations

  C07            `initialDelaySeconds`, `periodSeconds`,  Kubernetes Probe API      High           `[VERIFY]` Check
                 `timeoutSeconds`, `successThreshold`,    reference                                default values,
                 and `failureThreshold` influence probe                                            constraints, and
                 timing and transitions.                                                           handler-specific
                                                                                                   limitations

  C08            Multiplying startup `failureThreshold`   Kubernetes probe          High           Record measured timing;
                 by `periodSeconds` is a planning         documentation; inference                 do not use as exact
                 approximation, not an exact universal    from periodic checks and                 deadline
                 deadline.                                scheduling                               

  C09            `CrashLoopBackOff` is a container        Kubernetes, "Pod          High           `[VERIFY]` Confirm
                 waiting/backoff reason, not a Pod phase  Lifecycle";                              current presentation
                 or root cause.                           `kubectl describe`                       and reason taxonomy
                                                          diagnostics                              

  C10            Pod phase, Pod conditions, container     Kubernetes, "Pod          High           `[VERIFY]` Check target
                 state, restart count, and waiting reason Lifecycle"                               API fields and client
                 are distinct signals.                                                             output

  C11            Service endpoint eligibility is updated  Kubernetes, "Services";   High           `[VERIFY]` Check exact
                 from readiness-related state through     EndpointSlice API                        conditions and
                 asynchronous control loops.                                                       dataplane behavior for
                                                                                                   target setup

  C12            A successful HTTP health response proves Design inference; FastAPI High           Validate
                 only the contract represented by that    health endpoint example                  application-specific
                 endpoint.                                                                         semantics and status
                                                                                                   handling

  C13            Deep liveness checks against shared      Google SRE, cascading     High           General reliability
                 dependencies can amplify outages through failures; Kubernetes                     inference; test
                 synchronized restarts.                   probe guidance                           service-specific
                                                                                                   failure modes

  C14            A startup probe can protect a slow model Kubernetes probe          High           Measure actual model
                 load from premature liveness failures.   documentation;                           initialization
                                                          application design                       distribution
                                                          inference                                

  C15            Image-pull errors cannot be fixed by     Kubernetes Pod lifecycle  High           `[VERIFY]` Check target
                 changing probe timing because the        and image-pull                           event/reason strings
                 container has not started to be probed.  troubleshooting concepts                 and runtime details

  C16            Init containers run prerequisite work    Kubernetes, "Init         High           `[VERIFY]` Check
                 before application containers; failures  Containers"                              restartable
                 affect startup progression.                                                       sidecar/init semantics
                                                                                                   in target version

  C17            Deployment `minReadySeconds` affects     Kubernetes, "Deployments" High           `[VERIFY]` Confirm
                 when a Pod is considered available.                                               current field
                                                                                                   definition

  C18            Deployment `progressDeadlineSeconds`     Kubernetes, "Deployments" High           `[VERIFY]` Confirm
                 reports lack of progress and does not                                             current rollout
                 prove business correctness.                                                       controller behavior and
                                                                                                   field semantics

  C19            Pod readiness gates allow additional Pod Kubernetes Pod API        Medium         `[VERIFY]` Confirm
                 conditions to participate in readiness.  reference                                exact field and
                                                                                                   condition behavior in
                                                                                                   target minor

  C20            `not-ready` and `unreachable` taints and Kubernetes, "Nodes";      High           `[VERIFY]` Confirm
                 tolerations participate in node-failure  taints/tolerations docs                  actual controller
                 handling.                                                                         settings and cluster
                                                                                                   behavior

  C21            `tolerationSeconds` and node-monitoring  Kubernetes node-failure   High           `[VERIFY]` Record
                 configuration affect node-failure        documentation; Pod API                   target configuration;
                 timing; there is no universal timing     reference                                do not hard-code a
                 guarantee.                                                                        universal deadline

  C22            A heartbeat file may remain fresh while  Worker-health design      High           Test the actual
                 business work is deadlocked if a         analysis                                 worker's heartbeat
                 separate timer updates it.                                                        implementation

  C23            A heartbeat file may be stale during     Worker-health design      High           Define idle semantics,
                 legitimate idle periods or after process analysis                                 process identity, and
                 restart.                                                                          time source

  C24            Restart safety for queue/batch work      Google SRE reliability    High           `[VERIFY]` Verify exact
                 requires                                 principles;                              delivery/transaction
                 idempotency/checkpoint/acknowledgement   queue/database-specific                  guarantees of chosen
                 semantics supplied by the application    docs to be selected                      queue and store
                 and underlying system.                                                            

  C25            A restart does not repair bad code,      General recovery model;   High           Service-specific
                 invalid credentials, corrupt data, or a  Kubernetes controllers do                incident analysis still
                 permanently unavailable dependency.      not repair application                   required
                                                          logic                                    

  C26            `kubectl logs --previous` can retrieve   kubectl command reference High           `[VERIFY]` Confirm
                 previous-container logs when available.  / Pod diagnostics                        behavior for selected
                                                                                                   container/runtime and
                                                                                                   log retention

  C27            EndpointSlice API is the modern          Kubernetes, "Services";   High           `[VERIFY]` Confirm
                 representation for Service endpoint      EndpointSlice API                        API/resource alias
                 information.                             reference                                available in target
                                                                                                   cluster

  C28            kind uses containers as cluster nodes    kind documentation and    High           `[VERIFY]` Review
                 and does not faithfully model every      architecture                             current kind caveats
                 production node failure mode.                                                     and chosen runtime

  C29            Probe traffic and exec-process creation  Kubernetes probe          High           Measure actual
                 can add resource cost at fleet scale.    semantics; capacity                      request/process cost
                                                          inference                                for the workload

  C30            Probe status is not a complete SLI or    Google SRE, monitoring    High           Define service-specific
                 proof of business-level correctness.     and SLI concepts; design                 user outcome metrics
                                                          inference                                

  C31            `ImagePullBackOff` is a symptom of       Kubernetes Pod lifecycle  High           `[VERIFY]` Confirm
                 retry/backoff while image pulling fails, and image-pull                           exact event/reason
                 and should be investigated via           troubleshooting docs                     presentation
                 image/runtime events.                                                             

  C32            A Pod can be `Running` but not ready.    Kubernetes, "Pod          High           `[VERIFY]` Check target
                                                          Lifecycle"; Pod                          API presentation
                                                          conditions                               

  C33            Readiness flapping can cause endpoint    Reliability inference;    High           Validate impact in the
                 churn and uneven traffic.                Kubernetes Services                      actual dataplane
                                                          behavior                                 

  C34            A canary rollout and explicit exception  SRE practice and          High           Define
                 policy reduce blast radius from shared   organizational design                    organization-specific
                 probe defaults.                          inference                                approval and rollback
                                                                                                   controls

  C35            Kubernetes controllers reconcile desired Kubernetes controller and High           `[VERIFY]` Verify exact
                 state asynchronously;                    scheduler architecture                   component details for
                 replacement/scheduling is distinct from  docs                                     the target distribution
                 container restart.                                                                
  ------------------------------------------------------------------------------------------------------------------------

## 17. Final Self-Audit and Sign-Off

This audit reviews the lesson's content and structure. It does not
represent execution of commands, successful lab completion, or live
verification of official documentation.

  ---------------------------------------------------------------------------------------------------------------------------
  Pass                Result (PASS / Defects found                       Corrections applied          Residual risk
                      FIXED / OPEN)                                                                   
  ------------------- -------------- ----------------------------------- ---------------------------- -----------------------
  1\. Syllabus        FIXED          Broad Unit 3 scope could be         Included L1--L4, FastAPI,    Human reviewer should
  coverage                           underrepresented                    handlers, timing, recovery,  compare against the
                                                                         worker health, node          authoritative syllabus
                                                                         behavior, labs,              and roadmap tree
                                                                         SRE/security, evidence,      
                                                                         claim register               

  2\. Probe/API       OPEN           Some details are version-specific   Separated                    Check exact API schema
  semantics                          and not live-checked                liveness/readiness/startup   and status/redirect
                                                                         and marked                   behavior against target
                                                                         gRPC/readiness-gate/API      minor
                                                                         details `[VERIFY]`           

  3\. Manifest/code   OPEN           Image references and package        Placeholder image is         Build the image, run
  consistency                        compatibility cannot be verified    explicit; build/load steps   tests, validate
                                     without building/running            and sample source are inline selectors/ports/paths
                                                                                                      and FastAPI dependency
                                                                                                      compatibility

  4\. Command and lab OPEN           No commands or labs were executed   Added context guards,        Execute in disposable
  reproducibility                                                        exact-name operations,       kind; local output and
                                                                         evidence capture, and        timing may differ
                                                                         cleanup verification         

  5\.                 OPEN           Current Kubernetes/kind/FastAPI     Added explicit `[VERIFY]`    Verify target
  Version-sensitive                  docs were not checked live          markers and source list      Kubernetes minor, kind
  behavior                                                                                            version, API fields,
                                                                                                      gRPC, readiness gates,
                                                                                                      and node timing

  6\. Security and    FIXED          Lab toggle is state-changing and    Clearly isolated and labeled Review built
  information                        unsafe for production               lab-only; corrected image    image/source and
  exposure                                                               must remove it; health       evidence for secrets
                                                                         output kept minimal          before any sharing

  7\. Recovery        FIXED          Risk of conflating restart,         Explicit recovery-layer      Validate
  semantics and                      readiness, Pod replacement,         table, incident case,        application-specific
  failure analysis                   scheduling, and app recovery        runbook, and restart-safety  retry/idempotency
                                                                         guidance                     guarantees

  8\. Teaching        PASS           Risk of overexpanding               Kept those topics to         Compare exact roadmap
  progression and                    rollout/autoscaling/observability   diagnostic context and       naming/order against
  module boundaries                                                      stated later module          attached roadmap tree
                                                                         boundaries                   

  9\. Adversarial     FIXED          Deep liveness, stale heartbeat,     Added anti-pattern and       Production behavior
  production/SRE                     flapping, dependency fan-out, and   trade-off tables,            must be measured; no
  review                             false-positive risks needed         measurement definitions, and generic threshold is
                                     explicit treatment                  exception controls           universally safe

  10\. Lab safety and OPEN           Node-stop behavior may be           Kept node stop optional,     Run only in disposable
  local-resource                     unreliable on laptop/WSL2;          required context/name guard, kind; stop if
  feasibility                        runtime-specific constraints remain prohibited broad destructive context/cluster
                                                                         commands, offered            identity is uncertain
                                                                         inspection/simulation        
                                                                         alternative                  
  ---------------------------------------------------------------------------------------------------------------------------

### Required review points

1.  Unit 3 topics are represented across the four levels, but a human
    should compare the content against the authoritative syllabus before
    sign-off.
2.  Liveness, readiness, and startup are explicitly differentiated.
3.  `CrashLoopBackOff` is described as a waiting/backoff reason, not a
    Pod phase or root cause.
4.  Probe timing is described as a detection policy rather than an exact
    universal deadline.
5.  HTTP/TCP/exec/gRPC handlers are differentiated; gRPC and API edge
    cases are marked for verification.
6.  Deep liveness is labeled `ANTI-PATTERN — DO NOT COPY`; the
    dependency simulator lab includes a corrected design and
    before/after timeline procedure.
7.  Readiness and Service endpoint effects are described as asynchronous
    and not a guarantee of instant zero traffic.
8.  Image-pull and init-container failure paths are separated from probe
    failure.
9.  Worker health without HTTP, stale heartbeat, and progress semantics
    are covered.
10. Rollout interactions, readiness gates, node taints, and toleration
    timing include verification notes.
11. Kubernetes recovery is not overstated; application correctness and
    data recovery remain application responsibilities.
12. Idempotency, checkpoints, duplicate processing, and acknowledgement
    order are addressed.
13. Autoscaler/cold-start interactions are discussed without replacing
    Unit 6.
14. Destructive actions are restricted to a disposable cluster with
    context/name checks; optional node stop is explicitly bounded.
15. Each lab includes cleanup and cleanup verification.
16. Outputs are labeled representative and are not claimed as observed.
17. No paid cloud service or managed cluster is required.
18. Claim register and source notes state that live verification was not
    performed.
19. The requested deliverable is one lesson file; no companion artifact
    is part of this lesson.

### Final status

**Content status:** DRAFT-AUDITED\
**Audit date:** 2026-10-25; not live-verified\
**Auditor:** AI self-audit (human verification required)\
**Open verification items:** 10 review passes remain open or carry
residual risk; exact Kubernetes/API/runtime verification is required
before production use\
**Execution status:** Commands/labs not executed unless explicitly
evidenced

A self-audit is not a substitute for executing the examples in a
disposable `kind` cluster and verifying version-sensitive claims against
current official documentation. Do not treat the lesson as
production-approved until a human reviewer checks the exact Kubernetes
minor version, builds and tests the sample image, validates manifests
and application dependencies, runs the labs safely, and reviews actual
evidence.
