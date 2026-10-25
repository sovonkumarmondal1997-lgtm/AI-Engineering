# Production Cluster Architecture and Control Plane

> **Stage 2E --- Production DevOps & Platform Engineering** · **M03 ---
> Production Kubernetes Operations** · **Unit 1**

  -----------------------------------------------------------------------------------------------
  Metadata                            Value
  ----------------------------------- -----------------------------------------------------------
  Target file                         `01-production-cluster-architecture-and-control-plane.md`

  Estimated time                      10--14 hours including labs and evidence review

  Prerequisites                       Stages 0--2D, M01 container images, M02 CI/CD, Linux, Git,
                                      Docker, basic Pod/Deployment use

  Core tools                          `kind`, `kubectl`, Docker-compatible runtime, shell,
                                      Kubernetes API discovery

  Awareness                           `kubeadm`, minikube, EKS/GKE/AKS, admission webhooks, API
                                      Priority and Fairness, audit logging

  Last reviewed                       2026-10-25 (authoring date; live docs not checked in this
                                      pass)

  Kubernetes baseline assumed         Select a supported minor and compatible kind node image;
                                      **\[VERIFY\]** official support and version-skew policy

  Safety                              Learning lab only; not a production runbook to execute
                                      blindly
  -----------------------------------------------------------------------------------------------

**Purpose.** This lesson teaches how an API request becomes a running
workload, which component owns each transition, and what changes when
the control plane is impaired. Commands and output examples are
illustrative unless labelled as learner-observed evidence. Version-,
distribution-, and environment-sensitive claims are marked `[VERIFY]`.

## Table of contents

1.  [Why production cluster architecture
    matters](#1-why-production-cluster-architecture-matters)
2.  [Learning objectives mapped to
    L1--L4](#2-learning-objectives-mapped-to-l1l4)
3.  [Concept map and vocabulary](#3-concept-map-and-vocabulary)
4.  [Kubernetes mental model: declarative API and
    reconciliation](#4-kubernetes-mental-model-declarative-api-and-reconciliation)
5.  [Component-by-component
    architecture](#5-component-by-component-architecture)
6.  [The full request path: `kubectl apply` to running
    container](#6-the-full-request-path-kubectl-apply-to-running-container)
7.  [Beginner lab: inspect a cluster
    safely](#7-beginner-lab-inspect-a-cluster-safely)
8.  [Three-node kind topology and lab
    setup](#8-three-node-kind-topology-and-lab-setup)
9.  [Intermediate lab: trace one Deployment end to
    end](#9-intermediate-lab-trace-one-deployment-end-to-end)
10. [API-server interruption experiment in
    kind](#10-api-server-interruption-experiment-in-kind)
11. [Advanced design: HA control planes and etcd
    topology](#11-advanced-design-ha-control-planes-and-etcd-topology)
12. [Advanced request path, admission, audit, and
    scheduler](#12-advanced-request-path-admission-audit-and-scheduler)
13. [Failure semantics: what works when the API server is
    down](#13-failure-semantics-what-works-when-the-api-server-is-down)
14. [Managed versus self-managed
    Kubernetes](#14-managed-versus-self-managed-kubernetes)
15. [Expert operations: saturation, certificates, webhooks, fleet
    conformance](#15-expert-operations-saturation-certificates-webhooks-fleet-conformance)
16. [SRE lens](#16-sre-lens)
17. [Security lens](#17-security-lens)
18. [Production design checklist](#18-production-design-checklist)
19. [Hands-on lab index](#19-hands-on-lab-index)
20. [Self-check questions](#20-self-check-questions)
21. [Evidence artifacts](#21-evidence-artifacts)
22. [Interview and design-review
    questions](#22-interview-and-design-review-questions)
23. [Common failures and
    troubleshooting](#23-common-failures-and-troubleshooting)
24. [Cross-module boundaries and forward
    references](#24-cross-module-boundaries-and-forward-references)
25. [Sources, claim register, and verification
    notes](#25-sources-claim-register-and-verification-notes)
26. [Mandatory audit report and
    sign-off](#26-mandatory-audit-report-and-sign-off)

------------------------------------------------------------------------

## 1. Why production cluster architecture matters

A Kubernetes incident can look like an application failure while the
root cause is the API server, etcd, scheduler, a controller, a webhook,
a kubelet, or the network/storage integration. Confusing these layers
leads to harmful actions: repeated manifest writes during an API outage,
restarting healthy application processes because a dependency is slow,
or editing static-pod files without understanding kubelet
reconciliation.

Architecture literacy helps an engineer distinguish the **control
plane** (API and controllers coordinating state) from the **data plane**
(nodes and network paths serving workloads), identify the component
responsible for the next action, and gather evidence before changing
anything. It also informs HA design, managed-service responsibilities,
webhook policy, cluster count, capacity planning, and incident runbooks.
The goal is not memorizing component names; it is having a model that
can be tested with objects, events, status, and logs.

### Running example: data pipeline

We will use a FastAPI scoring API (`Deployment`), a queue worker, a
small PostgreSQL or Redis dependency (`StatefulSet`, lab-only), a
bounded ETL (`Job`), and a scheduled refresh (`CronJob`). M01 supplies
image/digest/non-root practices; M02 supplies CI/CD hand-off.
Workload-controller details are expanded in Unit 4, networking in M04,
storage in M05, and SLOs in M10. Do not use toy manifests with customer
data or credentials.

## 2. Learning objectives mapped to L1--L4

1.  **\[L1\]** Explain desired state, observed state, reconciliation,
    API objects, controllers, watches, events, conditions, labels,
    selectors, and owner references.
2.  **\[L1\]** Distinguish the primary responsibilities of API server,
    etcd, scheduler, controller manager, kubelet, CRI runtime,
    kube-proxy, CNI, and CSI.
3.  **\[L1\]** Trace a typical `kubectl apply` request to container
    startup and readiness.
4.  **\[L2\]** Safely inspect context, versions, API discovery, nodes,
    Pods, events, and object ownership.
5.  **\[L2\]** Inspect kind static-pod manifests and certificate
    metadata without editing manifests or rotating certificates.
6.  **\[L3\]** Compare stacked/external etcd and calculate quorum with
    assumptions stated.
7.  **\[L3\]** Explain admission-webhook failure policy, scheduler
    filtering/scoring, leader election, audit evidence, and
    control-plane capacity signals.
8.  **\[L3\]** Explain what can continue during API-server
    unavailability and what orchestration actions are impaired.
9.  **\[L4\]** Run a bounded experiment only on a disposable kind
    cluster and record expected versus observed behavior.
10. **\[L4\]** Produce a cluster-design ADR, diagnostic path, and
    fleet-conformance checklist with owners and unresolved verification
    items.

## 3. Concept map and vocabulary

  -----------------------------------------------------------------------
  Term                    Precise definition      Common misconception
  ----------------------- ----------------------- -----------------------
  `kube-apiserver`        Kubernetes API          It does not directly
                          endpoint; processes API run every container.
                          requests and exposes    
                          API objects.            

  `etcd`                  Strongly consistent     It is not the workload
                          key-value store for     database or a
                          Kubernetes API state.   substitute for app
                                                  backups.

  Scheduler               Chooses a feasible node It does not start the
                          for an unscheduled Pod  container.
                          and records a binding.  

  Controller              Repeatedly observes     It is not a one-shot
                          state and attempts to   script that runs only
                          reconcile actual state  after `apply`.
                          toward desired state.   

  Kubelet                 Node agent that ensures It does not choose a
                          assigned Pods run       Deployment's replica
                          according to their      count.
                          specifications.         

  CRI                     Interface between       CRI is not CNI or CSI.
                          kubelet and a container 
                          runtime.                

  CNI                     Interface family used   Kubernetes does not
                          by networking           ship one universal CNI
                          implementations to      implementation.
                          configure Pod           
                          networking.             

  CSI                     Interface used by       CSI internals are not
                          storage drivers to      taught here; see M05.
                          integrate storage.      

  `kube-proxy`            Common Service          It may be replaced or
                          forwarding              absent in some
                          implementation,         implementations.
                          depending on            
                          distribution.           

  Desired state           Intent in an API        Accepted manifest does
                          object, such as three   not mean three ready
                          replicas.               Pods exist.

  Observed state          API status, events,     One `get` snapshot
                          conditions, and         proves complete health.
                          node/runtime            
                          observations.           

  Reconciliation          Compare-and-act loop    It is not instantaneous
                          attempting to reduce    or guaranteed to
                          desired/observed gap.   succeed.

  Watch                   API mechanism for       A watch is not a
                          observing object        permanent durable event
                          changes.                log.

  Owner reference         Metadata expressing     Labels alone do not
                          ownership and informing establish ownership.
                          garbage collection.     

  Admission               Request stage that can  Admission and RBAC
                          mutate or reject        authorization are the
                          objects before          same check.
                          persistence.            

  Quorum                  Minimum number of etcd  Three members tolerate
                          voting members needed   two failures.
                          for a majority.         

  Failure domain          Boundary where failures Different Pod names
                          may be correlated,      imply independent
                          e.g. host, rack, zone,  failure domains.
                          region.                 
  -----------------------------------------------------------------------

``` mermaid
flowchart TB
  U["Operator / kubectl"] -->|"HTTPS request"| API["kube-apiserver"]
  API --> AUTH["AuthN → AuthZ → Admission"]
  AUTH --> ETCD[("etcd: persisted API state")]
  API <--> CTRL["Controllers"]
  API <--> SCH["kube-scheduler"]
  API <--> K1["kubelet on worker A"]
  API <--> K2["kubelet on worker B"]
  SCH -->|"bind Pod to node"| API
  K1 --> CRI1["CRI runtime"]
  K2 --> CRI2["CRI runtime"]
  CRI1 --> P1["Container / Pod"]
  CRI2 --> P2["Container / Pod"]
  K1 -.-> NET["CNI networking"]
  K1 -.-> STO["CSI storage"]
  P1 --> SVC["Service data plane"]
  P2 --> SVC
```

The diagram is conceptual. Implementations may combine, replace, or
externally manage components.

## 4. Kubernetes mental model: declarative API and reconciliation

### 4.1 Objects describe intent

A Deployment with `spec.replicas: 3` declares desired state. It does not
prove three Pods exist, are scheduled, are ready, or serve traffic. The
API server can accept the Deployment; the Deployment controller
creates/updates a ReplicaSet; the ReplicaSet controller creates Pods;
the scheduler assigns Pods; kubelets ask the runtime to start
containers; readiness and status observations arrive later.

### 4.2 Reconciliation is a loop

A controller reads/watches objects, compares desired and observed state,
computes actions, submits changes through the API, then repeats after
events or retries. It can be delayed, rate-limited, blocked by
permissions, or unable to reach dependencies. API success means the
request was accepted, not that every downstream controller completed.

### 4.3 Labels, selectors, owners, events, conditions

-   **Labels** classify objects; **selectors** query or associate
    objects by label criteria.
-   **Owner references** express object ownership (for example,
    ReplicaSet → Pod).
-   **Events** are useful diagnostic clues, but retention and
    completeness vary. No event does not prove nothing happened.
-   **Conditions** summarize status. Read `reason`, `message`, and
    timestamps, not only a top-level phase.
-   **Watches** notify clients of changes; after reconnect, controllers
    must re-establish a correct view of current state.

``` bash
kubectl get deploy,rs,pods -n default -o wide
kubectl get pods -n default --show-labels
kubectl describe deployment scoring-api
kubectl get events -A --sort-by=.metadata.creationTimestamp
kubectl get pod <POD_NAME> -o yaml
```

Replace placeholders with observed names. Confirm context before
mutating commands.

### 4.4 Analogy and limit

Think of the API server as the request desk, etcd as the durable ledger,
controllers as teams reconciling the ledger with desired outcomes, the
scheduler as an assignment planner, and kubelets as node-local
operators. The analogy hides concurrency, retries, authorization, and
distribution-specific behavior; use real object status and logs as
evidence.

## 5. Component-by-component architecture

### 5.1 Control plane

-   **`kube-apiserver`:** exposes the API; handles request processing.
    Controllers and scheduler are separate API clients.
-   **`etcd`:** persists API state. Availability depends on quorum,
    network latency, member health, and storage performance. An API
    endpoint responding does not by itself prove etcd will remain
    healthy under load.
-   **`kube-scheduler`:** filters infeasible nodes, scores feasible
    nodes, and binds a Pod. `Pending` can result from resource requests,
    taints, affinity, volume constraints, or control-plane issues.
-   **`kube-controller-manager`:** runs built-in controllers. The
    Deployment controller maintains ReplicaSets; other controllers
    handle other resource types. Exact composition/flags vary by
    distribution.
-   **`cloud-controller-manager`:** integrates with a cloud provider
    where that architecture uses it (e.g. node or load-balancer
    integration). It may be absent, externalized, or provider-managed in
    local/managed environments.

### 5.2 Node side

-   **`kubelet`:** observes assigned Pod specifications and coordinates
    local container lifecycle and health reporting.
-   **CRI runtime:** pulls images and creates/starts/stops containers.
    Docker may host kind node containers, but that host runtime is
    distinct from the runtime inside the Kubernetes node.
-   **`kube-proxy`:** traditionally watches Services/EndpointSlices and
    programs forwarding rules. Some distributions use replacement
    implementations; inspect rather than assume.
-   **CNI:** configures Pod networking; **CSI:** integrates storage. M04
    teaches networking/NetworkPolicy; M05 teaches PV/PVC/CSI and
    stateful storage.

### 5.3 Supporting mechanisms

-   **Admission controllers/webhooks:** can mutate or reject requests. A
    broad fail-closed webhook can block unrelated changes if its rules
    match broadly.
-   **API aggregation:** lets an aggregated API server serve an API
    group through the extension mechanism; it introduces another
    dependency.
-   **Leader election:** coordinates which replica performs leader-only
    work. It does not guarantee the leader is healthy or remove failover
    delay.
-   **Certificates:** secure/authenticate communication. Inspecting
    expiry is not rotation.
-   **Audit logging:** records configured API request events; policy,
    storage, access control, and retention determine what can be
    reconstructed.

  Boundary                    Concern                                 Full treatment
  --------------------------- --------------------------------------- -----------------
  Kubernetes API              Objects, auth, admission, persistence   This lesson
  CRI                         Kubelet/runtime lifecycle               M01/M03 context
  CNI                         Pod networking                          M04
  CSI                         Storage provisioning/attachment/mount   M05
  Image identity              Digest, provenance, non-root            M01/M12
  CI/CD                       Tested artifact hand-off                M02
  GitOps                      Reconciliation from Git                 M08
  Secrets/workload identity   Secret distribution and identity        M09

## 6. The full request path: `kubectl apply` to running container

For a typical Deployment create/update (not every object follows an
identical sequence):

1.  **Target selection:** `kubectl` resolves context, namespace,
    credentials, and endpoint.
2.  **Authentication:** API server establishes caller identity.
3.  **Authorization:** checks whether that identity may perform the verb
    on the resource.
4.  **Admission/validation:** applicable admission logic can mutate or
    reject; API validation checks schema/semantics.
5.  **Persistence:** accepted state is stored in etcd; success is not
    application readiness.
6.  **Reconciliation:** Deployment controller creates/updates
    ReplicaSet; ReplicaSet controller creates Pods.
7.  **Scheduling:** scheduler finds a feasible node and binds the Pod.
8.  **Runtime:** kubelet asks CRI to pull/start the container and
    reports status.
9.  **Networking/storage:** CNI and, when needed, CSI participate.
10. **Readiness:** probes/status determine readiness; Service forwarding
    depends on programmed data-plane state.

``` mermaid
sequenceDiagram
  participant K as kubectl
  participant A as API server
  participant E as etcd
  participant D as Deployment controller
  participant R as ReplicaSet controller
  participant S as Scheduler
  participant L as kubelet
  participant C as CRI runtime
  K->>A: Create/patch Deployment
  A->>A: AuthN, AuthZ, admission, validation
  A->>E: Persist accepted object
  A-->>K: API response (not readiness)
  A-->>D: Watch/update
  D->>A: Create/update ReplicaSet
  A-->>R: ReplicaSet observed
  R->>A: Create Pod
  A-->>S: Unscheduled Pod observed
  S->>A: Bind Pod to node
  A-->>L: Assigned Pod observed
  L->>C: Pull/start via CRI
  C-->>L: Runtime status
  L->>A: Pod status/conditions
```

``` bash
kubectl config current-context
kubectl get deployment,replicaset,pod -n default -o wide
kubectl describe deployment scoring-api
kubectl describe pod <POD_NAME>
kubectl get events -A --sort-by=.metadata.creationTimestamp
kubectl get pod <POD_NAME> -o jsonpath='{.metadata.ownerReferences}'
```

These prove API-reported state and ownership; they do not prove
end-to-end request success or independent failure domains.

## 7. Beginner lab: inspect a cluster safely

### 7.1 Safety gate

``` bash
kubectl config current-context
kubectl config get-contexts
kubectl cluster-info
kubectl version
```

If the selected context is not the disposable cluster you intend to
inspect, stop. A context name alone does not prove the target is safe.

### 7.2 Read-only orientation

``` bash
kubectl api-resources
kubectl explain deployment
kubectl explain deployment.spec.template.spec
kubectl get nodes -o wide
kubectl get namespaces
kubectl get pods -A -o wide
kubectl get events -A --sort-by=.metadata.creationTimestamp
```

**Expected output --- example; yours will differ:**

``` text
NAME                       STATUS   ROLES           AGE   VERSION
m03-arch-lab-control-plane  Ready    control-plane   3m    vX.Y.Z
m03-arch-lab-worker         Ready    <none>          2m    vX.Y.Z
m03-arch-lab-worker2        Ready    <none>          2m    vX.Y.Z
```

This illustrates the output shape, not observed evidence. Save your
actual version and node names. Read event `Reason`, `Message`, involved
object, and timestamp; events may expire or aggregate. `Forbidden`
indicates an authorization boundary, not proof the object is absent.

### 7.3 Save evidence locally

``` bash
mkdir -p evidence/unit-01
kubectl config current-context > evidence/unit-01/context.txt
kubectl version > evidence/unit-01/versions.txt
kubectl get nodes -o wide > evidence/unit-01/nodes.txt
kubectl api-resources > evidence/unit-01/api-resources.txt
kubectl get events -A --sort-by=.metadata.creationTimestamp > evidence/unit-01/events.txt
```

These commands write local files, not cluster state. Redact tokens,
certificate data, internal hostnames, and sensitive names before
sharing.

## 8. Three-node kind topology and lab setup

### 8.1 Simulation caveats and budget

kind runs Kubernetes nodes as containers. It does not create independent
physical hosts or availability zones; nodes share the host kernel and
compete for CPU/RAM/disk/network. WSL2 may differ in filesystem, DNS,
networking, and resource accounting. A kind cluster does not prove
production HA, real node-loss resilience, cloud load-balancer behavior,
production PV behavior, or real machine autoscaling.

**\[ASSUMPTION\]** One control plane plus two workers may fit on a
laptop with roughly 4 CPU cores, 8 GB RAM and 30 GB disk if competing
workloads are limited; this is not guaranteed. A third worker is
optional and may exceed the budget.

### 8.2 Choose a supported image

Before creating the cluster, check official Kubernetes support and
version-skew policy, then kind's node-image compatibility for your
installed kind release. Record the selected Kubernetes minor and exact
node image tag. Do not hard-code "current." The tag below is a
placeholder and must be replaced with a verified reference.

Save as `kind-m03-arch.yaml`:

``` yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4 # [VERIFY] against installed kind config schema
name: m03-arch-lab
nodes:
  - role: control-plane
    image: kindest/node:<NODE_IMAGE_TAG>
  - role: worker
    image: kindest/node:<NODE_IMAGE_TAG>
  - role: worker
    image: kindest/node:<NODE_IMAGE_TAG>
```

Do not include angle brackets literally. Schema and image compatibility
are **\[VERIFY\]** items. Keep the same verified node image for all
nodes.

### 8.3 Preflight and create

``` bash
kind version
kubectl version --client
docker info
kind get clusters
```

If the name already exists, inspect it before deciding whether to reuse
or delete it. Confirm the intended target immediately before creation:

``` bash
printf 'Intended disposable cluster: m03-arch-lab\n'
kind get clusters
```

After replacing the image placeholder with a verified tag:

``` bash
kind create cluster --config kind-m03-arch.yaml --name m03-arch-lab
```

The config and CLI both identify the name for clarity; if the installed
kind version rejects this combination, consult its help and use one
authoritative name declaration rather than guessing flags.

Verify:

``` bash
kubectl config current-context
kubectl get nodes -o wide
kubectl cluster-info
kubectl version
```

The context should identify `kind-m03-arch-lab` under standard kind
naming. If it does not, stop before applying manifests. Add a third
worker only if resources permit and after reviewing the destructive
implications of recreating a disposable cluster.

### 8.4 Cleanup

Before deletion, verify context and cluster name:

``` bash
kubectl config current-context
kind get clusters
```

Only if the target is the intended throwaway cluster:

``` bash
kind delete cluster --name m03-arch-lab
```

Deletion destroys in-cluster state. Never delete a cluster with
uncertain ownership or purpose.

## 9. Intermediate lab: trace one Deployment end to end

### 9.1 Preconditions

``` bash
kubectl config current-context
kubectl get nodes -o wide
```

Proceed only on the disposable `kind-m03-arch-lab` context. This is an
inspection example, not a complete production workload standard.

### 9.2 Manifest

Save as `scoring-api-lab.yaml`:

``` yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scoring-api
  namespace: default
  labels:
    app.kubernetes.io/name: scoring-api
    app.kubernetes.io/part-of: pipeline-lab
spec:
  replicas: 2
  selector:
    matchLabels:
      app.kubernetes.io/name: scoring-api
  template:
    metadata:
      labels:
        app.kubernetes.io/name: scoring-api
        app.kubernetes.io/part-of: pipeline-lab
    spec:
      securityContext:
        runAsNonRoot: true
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: web
          image: registry.k8s.io/e2e-test-images/agnhost:2.45
          args: ["netexec", "--http-port=8080"]
          ports:
            - name: http
              containerPort: 8080
          resources:
            requests:
              cpu: 50m
              memory: 64Mi
            limits:
              cpu: 250m
              memory: 128Mi
          readinessProbe:
            httpGet:
              path: /healthz
              port: http
            initialDelaySeconds: 2
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /healthz
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: scoring-api
  namespace: default
spec:
  selector:
    app.kubernetes.io/name: scoring-api
  ports:
    - name: http
      port: 80
      targetPort: http
```

**\[VERIFY\]** The example image, args, `/healthz` endpoint, and
non-root compatibility must be tested before use. If the image does not
support the configured identity or endpoint, substitute a verified lab
image and record the change; do not silently remove security controls.
For a production API, use your M01-built digest-pinned image and a
deliberate health contract.

### 9.3 Apply and trace

``` bash
kubectl config current-context
kubectl get nodes -o wide
kubectl apply -f scoring-api-lab.yaml
kubectl rollout status deployment/scoring-api --timeout=120s
kubectl get deployment,replicaset,pods -l app.kubernetes.io/name=scoring-api -o wide
kubectl describe deployment scoring-api
kubectl get events --sort-by=.metadata.creationTimestamp
```

`apply` is mutating: execute only after verifying the disposable
context. Inspect owner references and node placement:

``` bash
kubectl get rs -l app.kubernetes.io/name=scoring-api -o jsonpath='{range .items[*]}{.metadata.name}{" owner="}{.metadata.ownerReferences[0].name}{"\n"}{end}'
kubectl get pods -l app.kubernetes.io/name=scoring-api -o jsonpath='{range .items[*]}{.metadata.name}{" owner="}{.metadata.ownerReferences[0].name}{" node="}{.spec.nodeName}{"\n"}{end}'
```

A JSONPath expression may need adjustment if an object has no owner
reference. An empty result is not proof of success.

### 9.4 Inspect kind static Pods

``` bash
kind get nodes --name m03-arch-lab
docker exec m03-arch-lab-control-plane sh -c 'ls -l /etc/kubernetes/manifests'
docker exec m03-arch-lab-control-plane sh -c 'for f in /etc/kubernetes/manifests/*.yaml; do echo "=== $f"; sed -n "1,100p" "$f"; done'
```

Select the node whose name ends in `control-plane`; adjust the container
name/runtime command for Podman or a non-default name. The directory
commonly contains static-pod manifests for API server, scheduler,
controller manager, and etcd in a kubeadm-based kind node, but exact
files/flags vary. **Inspect; do not casually edit or delete these
files.** Kubelet manages static Pods from them.

``` bash
docker logs m03-arch-lab-control-plane --tail 100
kubectl get pods -n kube-system -o wide
kubectl get events -A --sort-by=.metadata.creationTimestamp
```

Not all distributions expose control-plane components as ordinary Pods.
Managed services may hide their processes/logs. Host node-container logs
are not necessarily equivalent to a component-specific log.

**Expected output --- example; yours will differ:**

``` text
NAME          READY   UP-TO-DATE   AVAILABLE
scoring-api   2/2     2            2
```

This shows the intended output shape only; it does not prove independent
machines/zones or business-level correctness.

### 9.5 Cleanup

Confirm context and target before deleting:

``` bash
kubectl config current-context
kubectl get deployment scoring-api
```

Then, only on the disposable context:

``` bash
kubectl delete -f scoring-api-lab.yaml
```

Capture evidence first if you need it.

## 10. API-server interruption experiment in kind

> **⚠ DESTRUCTIVE --- KIND SANDBOX ONLY.** Never run this against
> production, a managed cluster, or an uncertain context. It may
> temporarily make the lab API unavailable. Prepare recovery first.

### 10.1 Purpose and limits

This experiment asks whether already-running containers stop immediately
when API access is interrupted. Existing processes can often continue
while their node/runtime remains healthy, but API reads/writes and
orchestration actions are impaired. The method below pauses the **entire
control-plane node container**, not just the API server; it also affects
kubelet and other processes in that node. It is a coarse simulation, not
a clean API-server-only outage.

### 10.2 Preconditions and strict assertions

-   The cluster is disposable and contains no valuable data.
-   Section 9 workload is running and baseline evidence is saved.
-   A second terminal is ready for recovery.
-   You have verified the host runtime's pause/unpause semantics.
    **\[VERIFY\]** Docker/Podman and kind behavior.

``` bash
kubectl config current-context
kind get clusters
kind get nodes --name m03-arch-lab
docker ps --format '{{.Names}}'
```

Proceed only if context and container names identify the throwaway
cluster. Otherwise stop. Record baseline:

``` bash
kubectl get pods -o wide
kubectl get deployment scoring-api
kubectl get events --sort-by=.metadata.creationTimestamp
docker inspect m03-arch-lab-control-plane --format '{{.State.Status}}'
```

### 10.3 Bounded interruption

Limit the first run to **15 seconds or less**. Do not kill processes,
edit static manifests, or delete the node container in this introductory
drill.

``` bash
# Re-check target immediately before mutation.
kubectl config current-context
docker inspect m03-arch-lab-control-plane --format '{{.Name}} {{.State.Status}}'

# ⚠ DESTRUCTIVE — KIND SANDBOX ONLY
docker pause m03-arch-lab-control-plane
```

During pause, use bounded read-only observation:

``` bash
kubectl get pods --request-timeout=3s
docker inspect m03-arch-lab-control-plane --format '{{.State.Status}}'
```

Do not hammer the API with retries. A failed query is possible, not
guaranteed to produce a particular message.

### 10.4 Recovery---run immediately

``` bash
docker unpause m03-arch-lab-control-plane
docker inspect m03-arch-lab-control-plane --format '{{.State.Status}}'
kubectl get nodes --request-timeout=30s
kubectl get pods -o wide --request-timeout=30s
kubectl get events --sort-by=.metadata.creationTimestamp
```

If recovery is not prompt, stop experimenting; inspect host runtime
state/logs and consult kind troubleshooting for the installed version.
Do not delete/recreate the cluster until useful evidence is saved and
state loss is acceptable.

### 10.5 Expected versus observed worksheet

  -------------------------------------------------------------------------------------------
  Question          Hypothesis        Observed result     Evidence
  ----------------- ----------------- ------------------- -----------------------------------
  Was the scoring   Pausing freezes   `[fill in]`         `api-interruption-pods.txt`
  container present processes in the                      
  after recovery?   control-plane                         
                    node, but workers                     
                    are separate                          
                    containers;                           
                    observe the                           
                    actual                                
                    workload/node                         
                    placement.                            

  Did `kubectl get` API requests may  `[fill in]`         `api-interruption-api.txt`
  complete during   time out/fail.                        
  pause?                                                  

  Could a new       API writes should `[not attempted]`   Worksheet
  object be         fail if API is                        
  created?          unreachable; do                       
                    not attempt a                         
                    write during                          
                    outage.                               

  Did a new Pod     Scheduling needs  `[fill in]`         `api-interruption-scheduling.txt`
  schedule?         functioning                           
                    API/scheduler                         
                    paths.                                

  Did controllers   Controllers in    `[fill in]`         `api-interruption-events.txt`
  reconcile?        paused node                           
                    cannot execute                        
                    during pause.                         

  Did the cluster   Expected, but     `[fill in]`         `api-interruption-recovery.txt`
  recover after     verify rather                         
  unpause?          than assume.                          
  -------------------------------------------------------------------------------------------

A process-level API-server kill may be rapidly restarted because the API
server is a static Pod managed by kubelet. Only attempt that advanced
variation after researching and testing a reliable recovery procedure.
This experiment does not prove multi-AZ resilience, etcd quorum
tolerance, cloud load-balancer behavior, or universal Service traffic
continuity.

## 11. Advanced design: HA control planes and etcd topology

### 11.1 Stacked versus external etcd

In **stacked etcd**, each control-plane node also runs an etcd member.
This reduces separate hosts and can simplify operations, but couples
failures: a node loss may remove both an API server and an etcd member.

In **external etcd**, etcd runs on infrastructure separate from
control-plane nodes. This can separate failure domains and allow
independent sizing, but adds hosts, network paths, certificates,
monitoring, and operational complexity. External etcd is not
automatically more reliable; placement, quorum, latency, backup, and
operator skill still matter.

### 11.2 Quorum math

For `N` voting members, ordinary majority quorum is `floor(N/2) + 1`.

  -----------------------------------------------------------------------
           Voting members                  Quorum     Members that may be
                                                        unavailable while
                                                        retaining quorum,
                                                     assuming independent
                                                                 failures
  ----------------------- ----------------------- -----------------------
                        1                       1                       0

                        3                       2                       1

                        5                       3                       2

                        7                       4                       3
  -----------------------------------------------------------------------

Odd counts are common because adding an even-numbered member can add
cost without increasing tolerated failures versus the preceding odd
count: three requires two votes and four still requires three. These
examples assume ordinary majority voting; verify current etcd guidance
and distribution recommendations **\[VERIFY\]**. Three members in one
failure domain may all disappear in one correlated event. Network
partition and disk latency can also destroy useful quorum even if
processes appear alive.

### 11.3 API endpoint and failure domains

HA designs usually expose a stable API endpoint through a load balancer
or equivalent strategy. Review: - independent control-plane/etcd failure
domains; - endpoint health checks and failover behavior; - API-to-etcd
network latency and storage durability; - certificate lifecycle and
component credentials; - scheduler/controller availability and
leader-election behavior; - backup/restore separately from HA; -
incident access when a region or network is impaired.

Multiple API servers sharing one failed etcd quorum are not a
functioning control plane. A load balancer does not make a single API
server HA.

### 11.4 Trade-off matrix

  ----------------------------------------------------------------------------------------------------
  Option         Benefit                  Cost                   Main risk           Choose when
  -------------- ------------------------ ---------------------- ------------------- -----------------
  Stacked etcd   Fewer hosts, simpler     Coupled                One node failure    Simplicity meets
                 topology                 capacity/maintenance   removes two roles   availability
                                                                                     needs

  External etcd  Separate                 More hosts, network    More moving parts;  Team can operate
                 scaling/failure-domain   and certificate work   bad latency hurts   etcd as a
                 control                                         API                 critical tier

  Managed        Provider operates much   Service constraints    Shared              Provider workflow
  control plane  control-plane lifecycle  and cost               responsibilities    fits requirements
                                                                 misunderstood       

  Self-managed   Maximum configuration    Team owns upgrades,    Skills/automation   Team has mature
                 control                  certificates, etcd,    gaps create outages platform
                                          HA, on-call                                operations

  One cluster    Fewer duplicated         Shared blast radius    Noisy               Trust/lifecycle
                 services                 and tenancy complexity neighbor/policy     requirements
                                                                 coupling            align

  Multiple       Isolation and upgrade    More cost and fleet    Drift and           Isolation,
  clusters       rings                    management             fragmented          geography,
                                                                 observability       compliance
                                                                                     justify it
  ----------------------------------------------------------------------------------------------------

### 11.5 Capacity considerations

There is no universal safe Pod or node count for every control plane.
Capacity depends on API request rate, object churn, list/watch patterns,
admission latency, controller work, etcd storage/disk latency, and
distribution/version. Measure: - API latency and errors by verb/resource
where exposed; - etcd member health, disk latency and database size
where exposed; - scheduler Pending/latency evidence; - controller work
queues and reconciliation lag where exposed; - webhook latency/errors; -
audit volume and retention growth.

Metrics names and availability vary; verify before writing alerts.

## 12. Advanced request path, admission, audit, and scheduler

### 12.1 Admission webhook blast radius

Webhooks mutate or validate matching API requests. They become
dependencies of those requests.

-   **Fail closed:** a failed webhook may reject matching requests. This
    protects policy but can block deployments and recovery.
-   **Fail open:** requests may proceed without the webhook's decision.
    Availability improves but policy enforcement may be bypassed.
-   **Timeouts:** slow calls add latency or cause failure; exact
    supported values are **\[VERIFY\]**.
-   **Scope:** narrow resource, operation, and namespace matching.
    Exclusions need ownership and expiry; broad exclusions can become
    policy holes.
-   **Dependency cycles:** avoid a webhook whose own recovery requires
    the policy path it blocks.
-   **Availability:** monitor webhook replicas, latency, errors, and its
    dependencies; rehearse recovery.

Before changing webhook policy, identify the owner, matching rules,
affected operations, and an approved break-glass procedure. Never
casually disable admission on a real cluster.

### 12.2 API Priority and Fairness (APF)

APF provides request classification/concurrency-management mechanisms
intended to reduce starvation between request flows. Resource
configuration, defaults, metrics, and behavior are version-sensitive.
**\[VERIFY\]** official APF docs for the chosen minor. Do not copy
configuration from another cluster without traffic analysis and rollback
criteria.

### 12.3 Audit logs

Audit records may show who attempted a change, which resource/verb was
targeted, and request stage/result, depending on policy. Audit logs are
not a full record of application behavior. Request bodies may contain
sensitive data and verbose policies create volume.

A production design defines event stages/resource coverage, policy
ownership, secure storage/access/retention, privacy, ingestion failure
monitoring, and how responders query records during an outage. Managed
providers may route logs through provider systems; verify setup and
cost.

### 12.4 Scheduler: filter, score, bind

1.  **Filter:** exclude nodes that fail constraints (resource requests,
    node selectors/affinity, taints/tolerations, volume constraints,
    plugins).
2.  **Score:** rank feasible nodes by configured plugins and weights.
3.  **Bind:** record the chosen node for the Pod.

``` bash
kubectl describe pod <POD_NAME> -n <NAMESPACE>
kubectl get events -n <NAMESPACE> --sort-by=.metadata.creationTimestamp
kubectl get nodes --show-labels
kubectl describe node <NODE_NAME>
```

A Ready node does not prove a particular Pod fits. Check requests
against allocatable resources, taints, affinity, topology, volumes, and
scheduler/API health.

### 12.5 Controllers and leader election

Controllers observe and reconcile state. Leader election coordinates
which replica performs leader-only work. It reduces duplicate work only
if the application respects leadership; it does not guarantee a leader
is healthy or remove failover delay. Identify the controller responsible
for the object and inspect status/logs where accessible.

## 13. Failure semantics: what works when the API server is down

"API server down" can mean endpoint/network failure, process failure,
etcd quorum loss, TLS/authentication failure, or severe latency.
Distinguish these causes.

  -----------------------------------------------------------------------
  Capability              Likely behavior         Caveat
  ----------------------- ----------------------- -----------------------
  Existing container      Often continues on a    Runtime/node/workload
  process                 healthy node            dependencies still
                                                  matter

  Existing local request  May continue            Database, DNS, storage,
  serving                                         or network can fail
                                                  separately

  `kubectl get/apply`     Fails/times out if API  Client DNS/TLS/auth can
                          cannot be reached       look similar

  New scheduling          Impaired/unavailable    Scheduler needs API
                                                  interaction

  Controller              Impaired if controllers Recovery may lag after
  reconciliation          cannot use API          API returns

  Node/Pod status updates Delayed/unavailable to  API status can be stale
                          API clients             while process runs

  Service data plane      May continue using      Depends on network
                          programmed state        implementation, node
                                                  health and outage
                                                  duration

  New configuration       Cannot be reliably      Avoid repeated mutation
  changes                 submitted/observed      attempts during
                                                  uncertainty

  Autoscaling             Often impaired when API Metrics pipeline may
                          actions are required    also be affected
  -----------------------------------------------------------------------

**Principle:** existing workloads can continue while control-plane
operations are impaired, but this is not a promise of universal service
availability. Confirm the fault domain, preserve serving capacity, avoid
uncoordinated mutations, and follow the cluster/provider incident
procedure.

## 14. Managed versus self-managed Kubernetes

  ------------------------------------------------------------------------------------
  Concern                   Managed EKS/GKE/AKS      Self-managed
                            (typical; verify service 
                            tier)                    
  ------------------------- ------------------------ ---------------------------------
  API server/etcd hosts     Provider operates much   Organization provisions/operates
                            of the control-plane     them
                            infrastructure           

  Upgrades                  Provider offers          Team plans and executes lifecycle
                            supported workflows;     
                            customer validates and   
                            schedules according to   
                            service rules            

  Node pools                Customer commonly        Team owns
                            configures               provisioning/lifecycle/capacity
                            sizing/placement;        
                            provider tools vary      

  Certificates              Provider may manage many Team owns applicable lifecycle
                            control-plane            
                            certificates             

  Add-ons/network/storage   Shared responsibility    Team owns integration and
                            varies by component      compatibility

  Audit/logging             Provider-specific setup, Team designs and operates
                            retention, access, cost  collection

  Incident response         Provider handles         Team handles both layers
                            provider-owned           
                            infrastructure; customer 
                            handles                  
                            workload/configuration   

  Backup/DR                 Managed control plane    Team designs cluster/workload
                            does not automatically   backup
                            back up all application  
                            data                     
  ------------------------------------------------------------------------------------

Never assume identical feature exposure, upgrade cadence, support
policy, or control-plane visibility across providers or service tiers.

Before adoption, answer: who is paged for API/etcd/node/admission
faults; which logs/metrics are exposed and retained; who initiates
upgrades; which add-ons are provider-managed; what is the documented
degraded-control-plane recovery process; what data needs independent
backup; and how escalation works.

## 15. Expert operations: saturation, certificates, webhooks, fleet conformance

### 15.1 API-server saturation diagnostic path

**Symptoms:** elevated request latency/errors, slow `kubectl`, delayed
controller progress, timeouts, growing operational backlog.

First read-only checks, if the endpoint is reachable and access
permitted:

``` bash
kubectl config current-context
kubectl get --raw='/readyz' --request-timeout=5s
kubectl get --raw='/livez' --request-timeout=5s
kubectl get events -A --sort-by=.metadata.creationTimestamp
kubectl get pods -A -o wide
```

Health paths, access controls, output, and availability are
**\[VERIFY\]**. Failure does not distinguish saturation from DNS,
network, TLS, authentication, or etcd problems.

Gather provider/control-plane metrics/logs. Investigate request
latency/errors, high-churn controllers and list/watch traffic, webhook
latency, etcd health/disk latency, large/expensive requests, client
retry storms, and audit volume. Mitigation follows platform ownership
and change control. Do not randomly restart components or change
APF/admission policy without evidence and rollback criteria.

### 15.2 Certificate inspection (not rotation)

TLS symptoms may result from expiry, wrong CA, hostname mismatch, clock
skew, or unrelated network failure. On a local kubeadm-style kind node,
paths are **\[VERIFY\]**:

``` bash
docker exec m03-arch-lab-control-plane sh -c 'find /etc/kubernetes/pki -maxdepth 2 -type f -name "*.crt" -print'
docker exec m03-arch-lab-control-plane sh -c 'command -v openssl || true'
docker exec m03-arch-lab-control-plane sh -c 'openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -subject -issuer -dates'
```

The final command works only if that path and OpenSSL exist. Never
print, copy, or upload private keys. Inspection is not rotation.

**Production boundary:** do not rotate production certificates as part
of this lesson. For kubeadm, consult version-matched
certificate-management docs for topology, backups, renewal order,
component restarts and recovery. Managed services may not expose
certificate files or this workflow.

### 15.3 Webhook outage runbook

**Alert:** API requests fail/time out while webhook latency/errors rise.

1.  **Triage:** confirm context; identify matching operations and
    webhook owner.
2.  **Hypotheses:** unavailable Pods, Service selector mismatch,
    certificate trust/expiry, DNS/network, slow dependency, fail-closed
    policy.
3.  **Evidence:** webhook config/rules, endpoints, logs, latency, audit
    records if enabled.
4.  **Mitigate:** restore webhook health or use only an approved,
    narrow, time-limited exception. Do not broadly disable controls.
5.  **Follow up:** alert on latency/errors, test fail-open/closed
    behavior, document exclusions/expiry, rehearse recovery.

### 15.4 One cluster or multiple clusters?

Use multiple clusters when isolation, geography, compliance, independent
lifecycle/upgrade rings, or blast-radius requirements outweigh
duplicated services and fleet-management cost. Fewer clusters may suit
teams sharing a trust boundary and operational lifecycle with strong
tenancy controls.

  -------------------------------------------------------------------------
  Factor                  Fewer clusters          More clusters
  ----------------------- ----------------------- -------------------------
  Trust/compliance        Similar requirements    Hard isolation/different
                                                  regulation

  Blast radius            Small, governed         Critical services need
                          workloads               independent
                                                  failure/upgrade domains

  Operations              Small team/limited      Mature fleet operations
                          platform capacity       

  Geography               One region meets needs  Regional
                                                  locality/data-residency

  Cost                    Avoid duplicated        Isolation justifies cost
                          add-ons                 

  Upgrades                Shared cadence works    Separate upgrade rings
                                                  needed
  -------------------------------------------------------------------------

M14 covers multi-cluster architecture in depth.

### 15.5 Fleet version/policy conformance

Maintain inventory of cluster owner, provider/distribution,
region/environment, current and target minor, upgrade ring, exception
owner, and review date. Compare versions with support policy; detect
deprecated APIs before upgrades; validate security baselines; track
drift and exception expiry; stage upgrades through rings; retain
evidence. Use approved provider APIs/inventory sources; do not assume
all clusters are reachable from one `kubectl` context. Upgrade execution
belongs to Unit 8; full security baselines belong to M12.

### 15.6 Cluster-design ADR

Reusable template:

``` markdown
# ADR-NNN: <decision title>
- Status: Proposed | Accepted | Superseded
- Date:
- Decision owner:
- Reviewers:
- Context and constraints:
- Options considered:
- Decision:
- Positive and negative consequences:
- Failure modes and mitigations:
- Security/compliance impact:
- Cost/capacity impact:
- Validation plan and success criteria:
- Revisit triggers:
- Evidence/references:
```

**Illustrative filled decision:** A small platform team operating a 24×7
scoring API with no existing etcd on-call expertise may prefer a managed
control plane after verifying provider SLOs, supported versions, audit
access, regional design, node responsibilities, escalation, and cost.
Consequences include less direct control-plane maintenance but provider
constraints and continuing customer ownership of workload resilience,
node pools, policy, and recovery. Revisit after compliance changes,
repeated provider SLO misses, material cost variance, or a new need for
unsupported control-plane customization. This example is not a universal
recommendation.

### 15.7 Staff-SRE review questions

-   Are control-plane and etcd members spread across independent failure
    domains?
-   What is tested when quorum is lost, a webhook fails, or the API is
    slow?
-   Can responders collect evidence when the API is unavailable?
-   Is every alert owned, with a safe 3 a.m. mitigation?
-   Does "HA" have an SLO, measured failure test, and recovery evidence?
-   Are workload backups separate from API state backups?
-   Can a bad policy/certificate rollout prevent its own repair?
-   Are deprecated APIs detected before support windows close?

Reject claims based only on Pod replica count, a green dashboard without
SLOs, or "managed" meaning "no operational responsibility."

## 16. SRE lens

### 16.1 Useful SLIs

  -----------------------------------------------------------------------
  SLI                     Possible measurement    Caution
  ----------------------- ----------------------- -----------------------
  API availability        Successful eligible     Define endpoints and
                          requests / eligible     request classes
                          requests                

  API latency             Latency distribution by Averages hide tail
                          verb/resource           latency

  API error rate          Errors grouped by       Auth/client/server
                          cause/status            errors differ

  Scheduling latency      Pod creation to         Pending may be user
                          binding, where          constraints
                          measurable              

  Rollout success         Deployment reaches      Not business
                          target availability     correctness
                          within deadline         

  Control-loop lag        Desired change to       Metrics differ by
                          observed convergence    controller

  Webhook availability    Successful/fast         Include
                          admission calls         fail-open/closed policy
                                                  impact

  Recovery time           Detection to restored   Measure per scenario
                          service/control plane   
  -----------------------------------------------------------------------

Set SLOs from service requirements and observed baselines. M10 covers
SRE/SLOs; M11 covers observability implementation.

### 16.2 Failure modes and blast radius

-   API server/etcd degradation: broad API and control-loop impact.
-   Admission webhook outage: matching requests fail if fail-closed.
-   Scheduler degradation: new Pods may remain Pending while existing
    workloads continue.
-   Controller failure: convergence slows for owned resource types.
-   Node/kubelet/runtime failure: impacts workloads on that node until
    recovery/rescheduling.
-   Certificate/trust failure: breaks communication and can resemble
    network failure.
-   Excessive list/watch traffic: consumes API/etcd capacity and can
    amplify retries.

### 16.3 Runbook: API latency/error alert

1.  **Triage:** verify cluster/context, alert window, and whether
    failures are global or client/resource-specific.
2.  **Separate layers:** test reachability and health endpoints where
    permitted; inspect DNS/TLS/authentication and provider telemetry.
3.  **Check changes:** webhooks, CRDs/aggregated APIs, controller
    rollouts, high-churn jobs, monitoring agents, upgrades.
4.  **Mitigate safely:** follow platform procedure; reduce harmful
    request storms or restore the failed dependency; avoid unreviewed
    restarts.
5.  **Verify:** API SLIs, scheduling, controller convergence, and
    application SLIs return to baseline.
6.  **Follow up:** timeline, root cause, detection gap, owner, due date,
    evidence.

### 16.4 Cost and capacity

Include HA topology, cross-zone traffic, audit retention, observability,
support tiers, backups, and on-call capacity. Under-provisioning raises
latency/recovery time; over-provisioning does not fix bad client
behavior or a failing webhook. M15 covers capacity/FinOps.

## 17. Security lens

  --------------------------------------------------------------------------------------------
  Threat                  Control                          Verification evidence
  ----------------------- -------------------------------- -----------------------------------
  Wrong-context mutation  Context/target check,            `kubectl config current-context`,
                          least-privilege kubeconfig       change review

  Unauthorized API access Authentication and               `kubectl auth can-i` plus RBAC
                          least-privilege authorization    review

  Unsafe workload spec    Admission policy and Pod         Policy config and denied-request
                          security controls                evidence

  Compromised credential  Protect                          Access audit and lifecycle evidence
                          certificates/credentials;        
                          approved lifecycle               

  Admission dependency    Narrow scope, monitor health,    Rules, SLOs, drill
  outage                  rehearse recovery                

  Audit loss/tampering    Restrict access, retention,      Pipeline config and access logs
                          durable storage/integrity        

  Excessive node          Harden node/runtime; protect     Node access/security review
  privileges              node credentials                 

  Untrusted image         Digest/provenance/supply-chain   M01/M12 evidence
                          controls                         
  --------------------------------------------------------------------------------------------

Authentication identifies a caller; authorization decides whether it may
perform an operation; admission may mutate or reject an otherwise
authorized request. `kubectl auth can-i` checks a particular
authorization decision, not admission or all RBAC.

``` bash
kubectl auth can-i get pods -n default
kubectl auth can-i create deployments -n default
```

Run only against the intended context. Use official Kubernetes
security/threat-model materials, current NSA/CISA Kubernetes hardening
guidance, and the applicable CIS Kubernetes Benchmark. Confirm editions
and applicability. This lesson is not a full PSS baseline, network
segmentation, secret management, supply-chain attestation, or
cluster-hardening program; see M04, M09, M12.

## 18. Production design checklist

-   [ ] **Version/support:** cluster minor and provider support window
    recorded; version-skew policy reviewed. Evidence: inventory/release
    reference.
-   [ ] **API endpoint:** HA/failover documented and tested. Evidence:
    architecture diagram and approved test; requires platform/provider
    access.
-   [ ] **etcd:** topology, quorum, member health, disk latency,
    backup/restore ownership documented. Evidence: runbook and restore
    test.
-   [ ] **Failure domains:** correlated failures reviewed. Evidence:
    host/zone topology; kind cannot prove this.
-   [ ] **API health:** availability/latency/error SLIs and alerts
    defined. Evidence: dashboard and owner.
-   [ ] **Admission:** webhook owners, scope, timeouts, failure
    policies, exclusions, recovery documented. Evidence: config review
    and drill.
-   [ ] **Authorization:** least-privilege roles reviewed. Evidence:
    RBAC inventory and `auth can-i` samples; command alone is
    insufficient.
-   [ ] **Certificates:** expiry monitoring and approved
    renewal/rotation procedure documented. Evidence: certificate
    inventory/alerts; never export private keys.
-   [ ] **Audit:** policy, access, retention, storage and cost approved.
    Evidence: sample event and retention settings.
-   [ ] **Scheduling:** Pending-Pod triage covers requests, taints,
    affinity, storage, scheduler health. Evidence: tested runbook.
-   [ ] **Controller ownership:** critical resources have a known
    controller and owner. Evidence: ownership map.
-   [ ] **Managed responsibilities:** provider/customer split and
    escalation path written. Evidence: responsibility matrix.
-   [ ] **Version conformance:** inventory, deprecated API detection,
    upgrade rings, exception expiry maintained. Evidence: drift report.
-   [ ] **Recovery test:** bounded control-plane degradation drill
    measured. Evidence: incident-style timeline.
-   [ ] **Workload data:** app backup/restore tested separately from
    etcd. Evidence: M05/M13.
-   [ ] **Change safety:** mutations have context checks, review,
    rollback criteria and owner. Evidence: runbook/PR policy.
-   [ ] **Observability boundaries:** control-plane, node and
    application telemetry distinguished. Evidence: dashboard map.

## 19. Hands-on lab index

  ---------------------------------------------------------------------------------------------------------------------------------
  ID         Goal            Steps                  Evidence                       Cleanup      Stretch           kind caveat
  ---------- --------------- ---------------------- ------------------------------ ------------ ----------------- -----------------
  L1-A       Safe inspection Section 7 read-only    Context/version/nodes/events   None         Explain a         Local API only
                             commands                                                           condition/event   

  L1-B       Three-node      Section 8              Config, tag, version, nodes    Delete only  Add worker if     No independent
             topology        config/create/verify                                  named        budget permits    hosts/AZs
                                                                                   disposable                     
                                                                                   cluster                        

  L1-C       Deployment      Section 9              Ownership chain and events     Delete only  Compare rollout   Runtime/network
             trace           apply/inspect                                         lab manifest timeline          may differ

  L1-D       Control-plane   Section 10 bounded     Before/during/after worksheet  Unpause,     Compare with      Pauses more than
             interruption    pause/unpause                                         verify       provider docs     API server
                                                                                   recovery                       

  L1-E       Design ADR      Sections 11--15        ADR and reviewer objections    No mutation  Fleet inventory   Paper exercise
                                                                                                schema            does not prove HA
  ---------------------------------------------------------------------------------------------------------------------------------

All labs use only the disposable `m03-arch-lab` cluster. Save evidence
before cleanup. Re-running create/delete without checking current state
is not safe or idempotent.

## 20. Self-check questions

**Q1. A Deployment apply succeeds. What is proven?**\
**Answer:** The API accepted the operation. It does not prove
scheduling, startup, readiness, or request success.\
**Tempting error:** conflating persistence with reconciliation.

**Q2. Which component selects a node?**\
**Answer:** The scheduler filters, scores and binds. Kubelet starts
assigned containers.\
**Tempting error:** confusing node-local lifecycle with cluster-wide
placement.

**Q3. Why is a Pod Pending when nodes are Ready?**\
**Answer:** Requests may not fit; taints, affinity, volume constraints,
admission or scheduler issues may block it.\
**Tempting error:** node readiness does not prove every Pod is feasible.

**Q4. Quorum for five voting etcd members?**\
**Answer:** Three (`floor(5/2)+1`); under ordinary majority assumptions,
two may be unavailable.\
**Tempting error:** using half rather than majority.

**Q5. Why prefer odd etcd member counts?**\
**Answer:** Four requires three votes, the same quorum as three, so the
extra member does not improve tolerated member failures versus three.\
**Tempting error:** more members do not automatically mean
proportionally more fault tolerance.

**Q6. Do all containers stop if API server is down?**\
**Answer:** Not necessarily; existing processes often continue on
healthy nodes while API writes, scheduling, reconciliation and status
updates degrade. Data-plane behavior varies.\
**Tempting error:** treating Kubernetes as one process.

**Q7. What does `kubectl auth can-i` prove?**\
**Answer:** Permission for a specific verb/resource/scope for the
current identity/context; not admission success or a complete RBAC
audit.\
**Tempting error:** ignoring other request stages.

**Q8. Main risk of broad fail-closed admission?**\
**Answer:** A webhook outage can block matching requests, including
recovery changes.\
**Tempting error:** policy enforcement without availability planning.

**Q9. Does kind prove multi-zone HA?**\
**Answer:** No; its node containers share host kernel and underlying
machine.\
**Tempting error:** node count is not independent failure-domain count.

**Q10. How is certificate inspection different from rotation?**\
**Answer:** Inspection reads metadata; rotation changes credentials and
may require coordinated component changes/restarts and recovery
planning.\
**Tempting error:** assuming a read-only check validates renewal safety.

## 21. Evidence artifacts

Create `evidence/unit-01/` locally. Never include private keys, bearer
tokens, or raw kubeconfig credentials.

  ------------------------------------------------------------------------------------------
  Artifact                             Contents                      Acceptance criterion
  ------------------------------------ ----------------------------- -----------------------
  `context.txt`                        Current context               Target unambiguous

  `versions.txt`                       kind/kubectl versions, node   Exact observed values,
                                       tag, Kubernetes version       no "latest" assumption

  `kind-m03-arch.yaml`                 Verified three-node config    Placeholder replaced
                                                                     only after verification

  `nodes.txt`                          `kubectl get nodes -o wide`   Topology visible

  `api-resources.txt`                  API discovery                 Saved with environment
                                                                     context

  `deployment.yaml`                    Applied lab manifest          Matches
                                                                     context/evidence

  `deployment-trace.txt`               Deployment/ReplicaSet/Pod     Chain explained
                                       ownership and placement       

  `events.txt`                         Timestamp-sorted events       Events interpreted with
                                                                     caveats

  `static-pod-manifests.txt`           Read-only manifest            No secrets included
                                       listing/metadata              

  `api-interruption-before.txt`        Baseline                      Captured before
                                                                     mutation

  `api-interruption-during.txt`        Bounded observations          Timestamps and errors
                                                                     recorded

  `api-interruption-after.txt`         Recovery state                Recovery verified, not
                                                                     assumed

  `api-interruption-observations.md`   Expected vs observed          Hypothesis separated
                                       worksheet                     from evidence

  `cluster-design-adr.md`              Filled ADR                    Alternatives, owner,
                                                                     validation and revisit
                                                                     triggers

  `production-checklist.md`            Checklist with                Local simulation not
                                       evidence/owners               treated as production
                                                                     proof

  `verification-log.md`                Sources checked, versions,    Open questions explicit
                                       unresolved items              
  ------------------------------------------------------------------------------------------

## 22. Interview and design-review questions

### 1. Walk through a Deployment request.

**Model answer:** Confirm kubeconfig context. `kubectl` submits an API
request; authentication identifies the caller, authorization checks
permission, admission may mutate/reject, and accepted state is
persisted. The Deployment controller reconciles a ReplicaSet, the
ReplicaSet controller creates Pods, scheduler binds them to feasible
nodes, and kubelet uses CRI to start containers. CNI/CSI may
participate. I distinguish API success from readiness and use
owners/events/conditions/logs to verify transitions.

### 2. Choose stacked or external etcd.

**Model answer:** Start from availability goals, failure domains,
latency, operational skill, and cost. Stacked etcd is simpler but
couples node failure with API/etcd roles. External etcd separates tiers
but adds hosts/network/certificate/monitoring work. Calculate quorum,
examine correlated failures, define backup/restore ownership, and test.
External etcd is not automatically more available.

### 3. What keeps running during API outage?

**Model answer:** Existing containers may continue under kubelet/runtime
while nodes are healthy. New API operations, scheduling, controller
reconciliation and status updates are impaired. Service forwarding may
continue with programmed state, but depends on implementation, node
health and duration. First distinguish API reachability from
TLS/authentication, etcd, and client network failures.

### 4. A webhook outage blocks deployments---what do you do?

**Model answer:** Confirm matching operations, inspect webhook
rules/endpoints/latency/certificates and audit evidence, and page the
owner. Avoid broadly disabling policy. Use only an approved
narrow/time-limited mitigation if permitted, restore health, verify
policy enforcement, and add alerting/recovery drills.

### 5. One cluster or many?

**Model answer:** Compare trust/compliance, blast radius, geography,
upgrade rings, team maturity, cost and fleet-management complexity. One
cluster simplifies operations but increases shared blast radius; many
clusters isolate but duplicate services and create drift risk. Record
measurable requirements and revisit triggers in an ADR.

## 23. Common failures and troubleshooting

  -----------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Symptom           Hypotheses               First safe command                                              Evidence                    Mitigation/prevention
  ----------------- ------------------------ --------------------------------------------------------------- --------------------------- --------------------------------
  API unreachable   Wrong context/endpoint,  `kubectl config current-context`; `kubectl cluster-info`        Context, error, endpoint,   Separate
                    DNS/network, API                                                                         provider telemetry          network/TLS/auth/control-plane
                    process, TLS/auth,                                                                                                   causes; follow runbook
                    etcd/provider                                                                                                        

  Pod Pending       Requests, taints,        `kubectl describe pod <POD> -n <NS>`                            Events, requests, node      Fix constraint/capacity; don't
                    affinity, volume,                                                                        labels/taints               delete randomly
                    scheduler                                                                                                            

  Control-plane Pod Managed/hidden, static   `kubectl get pods -A -o wide`                                   Distribution docs, node     Confirm architecture before
  absent            Pod, different                                                                           manifest, provider console  declaring missing
                    namespace/distribution                                                                                               

  Webhook timeout   Unavailable/slow         `kubectl get events -A --sort-by=.metadata.creationTimestamp`   Config, endpoints, logs,    Restore dependency; approved
                    webhook,                                                                                 latency, audit              narrow mitigation
                    DNS/network/cert, broad                                                                                              
                    matching                                                                                                             

  TLS/certificate   Expiry, wrong CA,        `kubectl cluster-info` and approved inspection                  Error, cert dates/issuer,   Version-specific runbook; no
  failure           hostname, clock skew                                                                     clock                       blind rotation

  Ready nodes but   No feasible node,        `kubectl describe pod <POD> -n <NS>`                            Events, resources,          Correct constraints or capacity;
  no scheduling     scheduler/API issue                                                                      taints/affinity             verify scheduler

  Wrong cluster     Context drift            `kubectl config current-context`                                Context list, history,      Stop; use explicit approved
  mutation risk                                                                                              audit                       context and review

  `Forbidden`       Identity lacks           `kubectl auth can-i <verb> <resource> -n <NS>`                  Identity, namespace,        Approved least-privilege access;
                    permission or wrong                                                                      bindings                    no admin workaround
                    context/namespace                                                                                                    

  Rollout stalls    Controller/API           `kubectl rollout status deployment/<NAME> --timeout=10s`        Deployment/ReplicaSet/Pod   Preserve serving capacity;
                    impairment, admission,                                                                   status, events              diagnose before retrying
                    scheduling, readiness                                                                                                

  Slow `kubectl`    API saturation,          `kubectl get --raw='/readyz' --request-timeout=5s` if permitted API, webhook, etcd/provider Platform-owned mitigation;
                    list/watch load,                                                                         telemetry                   reduce request storm
                    webhook/etcd latency                                                                                                 
  -----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Some diagnostics require cluster-admin/provider access. Read-only
outputs may still contain sensitive infrastructure metadata.

## 24. Cross-module boundaries and forward references

  ------------------------------------------------------------------------
  Module                  This lesson covers      Deferred content
  ----------------------- ----------------------- ------------------------
  M01                     Image identity/non-root Image construction,
                          as context              optimization,
                                                  registry/digest
                                                  mechanics

  M02                     Tested artifact         Pipeline
                          hand-off context        implementation/release
                                                  promotion

  M04                     CNI and Service         Ingress, DNS,
                          boundaries              NetworkPolicy
                                                  enforcement, mesh

  M05                     CSI boundary and        PV/PVC, CSI, durability,
                          StatefulSet storage     operators
                          mention                 

  M06                     Direct manifests as lab Helm/Kustomize packaging
                          inputs                  and overlays

  M08                     Reconciliation concepts GitOps and progressive
                                                  delivery

  M09                     Auth/certificate        Secret
                          concepts                distribution/workload
                                                  identity

  M10                     SLIs and incident       Full SLO/error-budget
                          runbook structure       management

  M11                     Logs/events/metrics as  Monitoring stack and
                          evidence categories     telemetry pipeline

  M12                     API security/admission  Full hardening,
                          architecture            provenance and
                                                  supply-chain program

  M13                     etcd role and recovery  Organization-level
                          need                    backup/DR

  M14                     Cluster-count decision  Multi-cluster
                          factors                 architecture/fleet
                                                  operations

  M15                     Capacity/cost           Detailed capacity
                          considerations          modeling and FinOps
  ------------------------------------------------------------------------

A forward reference is not a claim that the deferred capability is
complete.

## 25. Sources, claim register, and verification notes

### 25.1 Official sources to consult

**Live documentation was not opened in this authoring pass.** These are
the source names/topics to consult for the chosen Kubernetes/kind
version, not a claim of completed verification:

1.  Kubernetes documentation --- **Kubernetes Components**.
2.  Kubernetes documentation --- **The Kubernetes API**, API concepts
    and discovery.
3.  Kubernetes documentation --- **Controllers** and **Deployments**.
4.  Kubernetes documentation --- **kube-scheduler** and scheduling
    framework.
5.  Kubernetes documentation --- **Kubelet** and **Container Runtime
    Interface (CRI)**.
6.  Kubernetes documentation --- **Admission Controllers** and **Dynamic
    Admission Control**.
7.  Kubernetes documentation --- **API Priority and Fairness**.
8.  Kubernetes documentation --- **Auditing**.
9.  Kubernetes documentation --- **Version and Version Skew Support
    Policy**.
10. Kubernetes documentation --- **Certificates** and kubeadm
    certificate management.
11. Kubernetes documentation --- **Troubleshooting Clusters** and API
    server health endpoints.
12. kind documentation --- **Quick Start**, configuration, node images,
    troubleshooting.
13. etcd documentation --- cluster membership, quorum, failure modes and
    operational guidance.
14. NSA/CISA --- **Kubernetes Hardening Guidance** (verify
    edition/applicability).
15. Center for Internet Security --- **CIS Kubernetes Benchmark**
    (verify version/distribution).
16. Provider docs --- EKS/GKE/AKS control-plane responsibility, audit
    logging, version policy and upgrade process for the exact service
    tier.

### 25.2 Claim register

  ---------------------------------------------------------------------------------------
  Claim/area                 Status                           Required verification
  -------------------------- -------------------------------- ---------------------------
  Component responsibilities General architecture;            Kubernetes Components docs
                             distribution details vary        for selected release

  Request-processing order   Conceptual; exact path varies by API and admission docs
                             request/object                   

  `kind.x-k8s.io/v1alpha4`   Version-sensitive                Installed kind config
  schema                                                      schema/release docs

  Node-image compatibility   Not selected here                kind node-image list and
                                                              Kubernetes support/skew
                                                              policy

  `agnhost` args, endpoint,  Must test                        Image docs and Pod
  non-root                                                    events/logs

  Static-pod paths           Common kind/kubeadm pattern      Inspect disposable node;
                                                              kubeadm docs

  `/healthz`, `/livez`,      Access/version-sensitive         Official health endpoint
  `/readyz`                                                   docs and permissions

  Certificate paths/OpenSSL  Environment-specific             Inspect disposable node
                                                              only

  Quorum formula             Majority-voting assumption       Official etcd clustering
                                                              docs

  APF config/metrics         Version-sensitive                Official APF docs for
                                                              chosen minor

  Webhook timeout/failure    Verify current behavior          Dynamic Admission Control
  policy                                                      docs/config

  `kube-proxy` presence      Distribution-specific            Inspect actual network
                                                              implementation

  Service traffic during API Implementation-dependent         Cluster/provider-specific
  outage                                                      test/docs

  Managed-service            Provider/tier-specific           Exact provider docs and
  responsibility                                              contract

  API metric names           Version/distribution-sensitive   Official metrics/provider
                                                              telemetry

  Pause/unpause experiment   Coarse simulation, not           Runtime and kind docs
                             production proof                 
  ---------------------------------------------------------------------------------------

### 25.3 Verification log template

``` text
Date checked:
Kubernetes minor:
kind version:
kind node image tag:
Host OS / WSL2 version:
Container runtime and version:
Support/skew policy checked:
kind config schema checked:
Example image/endpoint verified:
Health endpoint behavior checked:
Certificate inspection path checked:
Runtime pause/unpause behavior checked:
Commands actually executed:
Tests not executed:
Open [VERIFY] items:
```

### 25.4 Explicit limitations

-   No cluster was created by this authoring process.
-   No `kubectl`, kind, Docker/Podman, certificate, API interruption, or
    manifest-apply command was executed for this artifact.
-   Live official documentation was not consulted; source list is a
    checklist, not completed verification.
-   Output examples are illustrative, not learner-observed.
-   This is not a production certificate-rotation guide, etcd restore
    procedure, full hardening standard, or production HA proof.
-   Version-sensitive details and image behavior remain subject to the
    claim register.

## 26. Mandatory audit report and sign-off

### Ten-pass audit

  ------------------------------------------------------------------------------------------
  Pass                  Audit question                 Result            Notes
  --------------------- ------------------------------ ----------------- -------------------
  1\. Scope fidelity    Only Unit 1, with later        Pass with         Deferred modules
                        modules not silently taught in boundaries        are identified
                        full?                                            

  2\. Section order     Are the required major         Pass              Sections 1--26
                        sections present and ordered?                    follow the
                                                                         requested structure

  3\. L1--L4            Foundations to fleet/incident  Pass              Labs, HA, failure
  progression           reasoning?                                       semantics, runbooks
                                                                         included

  4\. Architecture      Components, request path,      Pass              Implementation
  coverage              watches/events/owners,                           caveats included
                        CRI/CNI/CSI?                                     

  5\. Lab safety        Mutations gated and            Pass with         Named disposable
                        destructive drill bounded?     environment       cluster; pause
                                                       caveats           affects whole node
                                                                         container

  6\. Production        HA, quorum, webhook blast      Pass              No universal sizing
  realism               radius, capacity, ownership?                     or availability
                                                                         promises

  7\. Security          Authn/authz/admission, certs,  Pass              Full
                        audit, least privilege?                          hardening/secrets
                                                                         deferred

  8\.                   Labs, expected-vs-observed,    Pass              Examples explicitly
  Evidence/assessment   ADR, self-checks?                                illustrative

  9\. Source integrity  Unverified claims marked; no   Pass with         Official docs not
                        false live-doc claim?          unresolved        opened; claim
                                                       verification      register included

  10\.                  Were                           Not executed      Static content
  Execution/sign-off    commands/manifest/experiment                     review only
                        executed?                                        
  ------------------------------------------------------------------------------------------

### Unresolved before practical use

-   Replace `<NODE_IMAGE_TAG>` only after checking installed kind
    release, Kubernetes support and skew policy.
-   Verify kind config schema and cluster-creation behavior for
    installed version.
-   Verify example image, arguments, health endpoint, and non-root
    compatibility.
-   Verify Docker/Podman pause/unpause and node-container name before
    the interruption drill.
-   Consult official docs for health endpoints, APF, certificates, etcd,
    and provider responsibility.
-   Execute labs only in disposable kind; capture actual outputs and
    failures.
-   Do not use this lesson to rotate production certificates or
    interrupt a production control plane.

### Sign-off

This is a complete instructional draft with safety boundaries, labs,
troubleshooting, evidence requirements, and a verification register. It
has **not** been validated by executing commands or consulting live
official documentation in this authoring pass. Treat it as
source-aligned learning material requiring environment-specific
verification, not as a verified production runbook. Only this standalone
Markdown artifact is intended; no repository files were changed.
