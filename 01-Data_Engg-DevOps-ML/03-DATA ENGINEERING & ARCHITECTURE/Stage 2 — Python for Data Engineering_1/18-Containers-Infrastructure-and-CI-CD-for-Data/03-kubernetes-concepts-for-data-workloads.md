# Kubernetes Concepts for Data Workloads

> **Stage 2 — Python for Data Engineering**  
> **Module 2.18 — Containers, Infrastructure, and CI/CD for Data**  
> **Topic 03 — Kubernetes Concepts for Data Workloads**
>
> **Audience:** Data Engineers who already understand Docker containers and Docker Compose  
> **Goal:** Become capable of understanding, deploying, sizing, securing, troubleshooting, and architecting data workloads on Kubernetes without turning this module into a Kubernetes administrator course.

---

## 1. Module Outcome

By the end of this module, you should be able to:

- explain why Kubernetes exists and when it is useful for Data Engineering;
- understand clusters, nodes, control planes, Pods, Deployments, Services, and Namespaces;
- use `kubectl` to inspect and debug workloads;
- create and operate a local Kubernetes cluster with `kind`, `k3d`, or minikube;
- choose correctly between a Pod, Deployment, Job, and CronJob;
- run one-time and scheduled Python data pipelines;
- configure retries, deadlines, completion, parallelism, and CronJob concurrency;
- separate configuration from secrets;
- understand why Kubernetes Secret data is not encrypted merely because it is stored in a Secret object;
- size CPU and memory requests and limits for data workloads;
- diagnose CPU throttling and `OOMKilled`;
- use ServiceAccounts and understand workload identity;
- install data platforms with Helm;
- understand Kubernetes Operators and how they relate to Spark, Kafka, and Flink;
- understand Airflow Kubernetes Executor and KubernetesPodOperator;
- understand Spark on Kubernetes;
- reason about HPA, node autoscaling, event-driven scaling, and consumer-lag-driven scaling;
- use node pools, taints, tolerations, and affinity to separate workload classes;
- understand PersistentVolumes and PVCs while maintaining an object-storage-first data architecture;
- understand GitOps through Argo CD and Flux;
- systematically debug common Kubernetes failures;
- design a production-oriented Kubernetes data platform;
- recognize when Kubernetes is unnecessary.

---

# 2. Prerequisites and Scope

## 2.1 Prerequisites

You should already understand:

- Linux/command-line basics;
- Python fundamentals;
- Python data-engineering workflows;
- Docker images and containers;
- Dockerfiles;
- container registries;
- Docker Compose fundamentals.

The previous topic, **Docker Images for Python Pipelines**, is especially important because Kubernetes ultimately runs container images.

The previous topic, **Docker Compose for Local Data Stacks**, provides the transition point:

```text
Docker
  ↓
Docker Compose
  ↓
Kubernetes
```

Compose teaches how multiple containers can work together on a machine. Kubernetes extends the problem to a cluster containing multiple machines and many independently managed workloads.

## 2.2 What This Module Does Not Teach

This is a **Data Engineering Kubernetes module**, not a complete Kubernetes administrator certification course.

We will not deeply teach:

- Kubernetes control-plane administration;
- etcd administration;
- writing custom Kubernetes controllers;
- advanced CNI implementation;
- advanced ingress-controller internals;
- cluster certificate administration;
- complete RBAC administration;
- Terraform;
- CI/CD;
- environment promotion;
- cloud secrets-manager implementation;
- complete Spark performance tuning;
- complete Kafka architecture;
- complete cloud IAM.

Those belong to other roadmap topics or earlier modules.

The focus is:

> **How should a Data Engineer understand and operate real data workloads on Kubernetes?**

---

# 3. The Problem: Why Does Kubernetes Exist?

A single Docker container is relatively easy to run:

```text
Python application
      ↓
Docker image
      ↓
docker run
```

A local Compose stack is also manageable:

```text
PostgreSQL
MinIO
Kafka
Airflow
Pipeline
      ↓
Docker Compose
      ↓
One machine
```

Now imagine a production data platform:

```text
10–100+ workloads
      ↓
multiple machines
      ↓
batch + streaming + APIs
      ↓
failures
      ↓
different CPU/memory requirements
      ↓
scheduling constraints
      ↓
scaling requirements
      ↓
identity/security requirements
```

Manually deciding:

- which machine runs each container;
- what happens when a container dies;
- how replicas are created;
- how services discover one another;
- where workloads are scheduled;
- how resources are constrained;
- how workloads are restarted;
- how batch jobs are retried;
- how nodes are added;
- how workloads are isolated;

becomes operationally expensive.

Kubernetes provides a declarative orchestration layer.

It helps with:

- scheduling;
- desired-state management;
- workload replacement;
- service discovery;
- resource-aware placement;
- scaling;
- workload isolation;
- declarative configuration;
- operational automation.

A useful mental model is:

> Docker packages the workload. Kubernetes manages where and how that workload runs.

---

# 4. Kubernetes Mental Model

At a high level:

```text
Kubernetes Cluster
│
├── Control Plane
│   ├── API Server
│   ├── Scheduler
│   └── Controllers
│
└── Worker Nodes
    ├── Pods
    │   └── Containers
    ├── Networking
    └── Compute Resources
```

## 4.1 Cluster

A **cluster** is the Kubernetes environment containing the control plane and worker nodes.

For a Data Engineer, think:

> "The cluster is the pool of compute and Kubernetes services available to run my data workloads."

## 4.2 Node

A node is a machine that can run Pods.

It may be:

- a virtual machine;
- a physical machine;
- a cloud-managed worker.

Example:

```text
Cluster
│
├── node-1
├── node-2
└── node-3
```

Nodes provide resources such as:

- CPU;
- memory;
- local storage;
- networking.

## 4.3 Control Plane

The control plane manages the cluster.

Important components for a Data Engineer:

### API Server

The Kubernetes API is the primary interface to the cluster.

Commands such as:

```bash
kubectl get pods
kubectl apply -f job.yaml
```

ultimately interact with the Kubernetes API.

### Scheduler

The scheduler decides where unscheduled Pods should run.

It considers factors such as:

- resource requests;
- node availability;
- taints/tolerations;
- affinity;
- other scheduling constraints.

### Controllers

Controllers continuously observe actual state and attempt to move the cluster toward desired state.

You do not need to memorize every controller implementation.

The important Data Engineering concept is:

> Kubernetes continuously reconciles declared intent with observed reality.

---

# 5. Desired State and Reconciliation

This is one of the most important Kubernetes concepts.

Suppose you declare:

```yaml
spec:
  replicas: 3
```

You are saying:

```text
Desired state = 3 replicas
```

Suppose one Pod dies:

```text
Desired = 3
Actual = 2
```

A controller notices the difference:

```text
Desired = 3
Actual = 2
       ↓
Reconciliation
       ↓
Create replacement
       ↓
Actual = 3
```

This is different from manually running:

```bash
docker run ...
docker run ...
docker run ...
```

Kubernetes is declarative.

You describe **what should exist** rather than manually describing every recovery action.

### Data Engineering relevance

This model is useful for:

- Airflow components;
- API services;
- Kafka consumers;
- long-running ingestion services;
- scheduled batch workloads;
- Spark integrations;
- supporting platform components.

### Mental model

> **Kubernetes is a reconciliation engine for desired workload state.**

### Knowledge Check

Before continuing, I should be able to:

- [ ] Explain desired state.
- [ ] Explain actual state.
- [ ] Explain reconciliation.
- [ ] Explain what happens if one replica disappears.

---

# 6. Pods

A **Pod** is the basic Kubernetes scheduling unit.

A Pod contains one or more containers.

A common pattern is:

```text
Pod
└── one application container
```

This is a good default for many data workloads.

## 6.1 Pod Networking

Containers in the same Pod share a network namespace.

They can communicate through localhost within the Pod.

Conceptually:

```text
Pod
├── container A
└── container B

A <---- localhost ----> B
```

## 6.2 Pod Storage

Containers in a Pod can share mounted volumes.

## 6.3 Why Not Manage Individual Pods?

You can create a Pod directly:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pipeline-pod
spec:
  containers:
    - name: pipeline
      image: python:3.12-slim
      command: ["python", "-c"]
      args: ["print('pipeline started')"]
```

But production workloads usually use higher-level controllers:

- Deployment for long-running services;
- Job for one-time work;
- CronJob for scheduled work.

### Mental model

> A Pod is the unit Kubernetes schedules; a container is the process packaged inside it.

### Failure Mode

If you create a standalone Pod for a production pipeline and it terminates, Kubernetes does not automatically give you the workflow semantics of a Job.

Use the primitive that matches the workload.

### Knowledge Check

- [ ] What is a Pod?
- [ ] Why is one container per Pod common?
- [ ] Why should a batch pipeline generally use a Job rather than a manually created Pod?

---

# 7. Deployments

A Deployment manages long-running, usually stateless workloads.

Example:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: data-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: data-api
  template:
    metadata:
      labels:
        app: data-api
    spec:
      containers:
        - name: api
          image: example/data-api:1.0.0
          ports:
            - containerPort: 8000
```

The relationship is approximately:

```text
Deployment
    ↓
ReplicaSet
    ↓
Pods
    ↓
Containers
```

## 7.1 Why Deployments Exist

A Deployment provides a desired number of replicas and manages replacement.

For example:

```text
Desired replicas = 3
```

If one Pod disappears:

```text
3 → 2
```

the controller works toward:

```text
2 → 3
```

## 7.2 Rolling Updates

Deployments also support controlled updates at a high level.

For example:

```text
data-api:1.0
      ↓
data-api:1.1
```

Kubernetes can progressively replace old Pods with new ones according to Deployment strategy.

## 7.3 Deployment vs Batch Job

Do not use a Deployment merely because it can restart a process.

Use:

| Workload | Primitive |
|---|---|
| Long-running API | Deployment |
| Long-running Kafka consumer | Deployment |
| Supporting service | Deployment |
| One-time ETL | Job |
| Scheduled ETL | CronJob |

A Deployment expresses:

> "Keep this service running."

A Job expresses:

> "Complete this unit of work."

That distinction matters greatly in Data Engineering.

### Knowledge Check

- [ ] Why does a Deployment use replicas?
- [ ] Why is a Kafka consumer often a Deployment?
- [ ] Why is a one-time ETL pipeline usually a Job?

---

# 8. Services

Pod IP addresses are not stable application endpoints.

Pods can be:

- replaced;
- rescheduled;
- recreated.

A **Service** provides a stable abstraction for accessing a group of Pods.

Example:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: data-api
spec:
  selector:
    app: data-api
  ports:
    - port: 80
      targetPort: 8000
  type: ClusterIP
```

The important relationship is:

```text
Client
  ↓
Service
  ↓
Pod 1
Pod 2
Pod 3
```

## 8.1 Selector

The Service finds Pods using labels:

```yaml
selector:
  app: data-api
```

Pods must have:

```yaml
labels:
  app: data-api
```

## 8.2 Service DNS

Inside a Kubernetes cluster, workloads can normally reach a Service by its DNS name.

For example:

```text
data-api
```

or, within a namespace:

```text
data-api.data-platform.svc
```

This is a critical difference from the local Docker Compose mental model of `localhost`.

### Data Engineering Example

Suppose a pipeline needs to reach a PostgreSQL Service:

```text
pipeline Pod
    ↓
postgres Service
    ↓
PostgreSQL Pod(s)
```

The pipeline should not assume that a particular PostgreSQL Pod IP remains unchanged.

## 8.3 Service Types

### ClusterIP

Default internal service.

Useful for:

- internal APIs;
- databases;
- internal platform components.

### NodePort

Exposes a port through cluster nodes.

Useful mainly for simple environments and learning.

### LoadBalancer

Common in cloud environments where an external load balancer is provisioned.

Do not treat all three as interchangeable.

### Knowledge Check

- [ ] Why aren't Pod IPs stable application endpoints?
- [ ] What does a Service selector do?
- [ ] What is ClusterIP used for?
- [ ] Why should a data pipeline use a Service rather than hard-code a Pod IP?

---

# 9. Namespaces

Namespaces logically organize Kubernetes resources.

Example:

```text
Kubernetes Cluster
│
├── data-platform
├── airflow
├── streaming
└── spark
```

Namespaces can help separate:

- teams;
- environments;
- platform components;
- workload classes.

Example:

```bash
kubectl get pods -n airflow
kubectl get pods -n streaming
```

Namespaces can also be associated with:

- resource policies;
- access-control policies;
- workload organization.

### Important Security Note

A namespace is not automatically a complete security boundary.

Security also depends on:

- RBAC;
- ServiceAccounts;
- network controls;
- admission policies;
- cloud identity;
- secrets management.

This module only teaches the portions required for data-workload reasoning.

### Example

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: data-platform
```

### Mental model

> A namespace is a logical workspace inside a cluster, not a magic security wall.

### Knowledge Check

- [ ] What problem do namespaces solve?
- [ ] Why are namespaces useful for data platforms?
- [ ] Why is a namespace alone not a complete security boundary?

---

# 10. kubectl

`kubectl` is the primary command-line client for interacting with Kubernetes.

## 10.1 Apply

```bash
kubectl apply -f deployment.yaml
```

Use it to declare/update resources from manifests.

## 10.2 Get

```bash
kubectl get pods
kubectl get deployments
kubectl get jobs
kubectl get cronjobs
```

Use it for high-level state.

Useful variants:

```bash
kubectl get pods -o wide
kubectl get pods -n data-platform
kubectl get all -n data-platform
```

## 10.3 Describe

```bash
kubectl describe pod pipeline-job-abc123
```

Use it for detailed resource information, scheduling details, conditions, mounts, events, and failure clues.

## 10.4 Logs

```bash
kubectl logs pod-name
```

Follow logs:

```bash
kubectl logs -f pod-name
```

For a container with a previous crash:

```bash
kubectl logs --previous pod-name
```

## 10.5 Exec

```bash
kubectl exec -it pod-name -- sh
```

Use this carefully for debugging.

Examples:

```bash
kubectl exec -it pod-name -- env
kubectl exec -it pod-name -- ls -la
```

## 10.6 Delete

```bash
kubectl delete -f deployment.yaml
```

or:

```bash
kubectl delete pod pod-name
```

Be careful: deletion can trigger controller-driven recreation.

## 10.7 Events

```bash
kubectl get events --sort-by=.lastTimestamp
```

Events are often essential when a Pod is not starting.

## 10.8 Standard Debugging Sequence

Start broad:

```text
kubectl get
      ↓
kubectl describe
      ↓
kubectl logs
      ↓
kubectl get events
      ↓
kubectl exec
```

Then inspect:

- configuration;
- resources;
- scheduling;
- networking;
- identity;
- dependencies.

### Common Mistake

Seeing:

```text
Pod exists
```

does not mean:

```text
Application is healthy
```

Inspect the Pod state and application logs.

### Knowledge Check

- [ ] Can I use `get` for high-level state?
- [ ] Can I use `describe` for deeper diagnosis?
- [ ] Can I inspect current and previous logs?
- [ ] Can I inspect cluster events?

---

# 11. Local Kubernetes Clusters

You should practice Kubernetes locally before operating cloud clusters.

Common local options:

- kind;
- k3d;
- minikube.

They are not identical, but all can provide a practical local Kubernetes learning environment.

## 11.1 kind

kind runs Kubernetes nodes using containers.

Typical workflow:

```bash
kind create cluster --name data-learning
kubectl cluster-info
kubectl get nodes
```

Delete:

```bash
kind delete cluster --name data-learning
```

## 11.2 k3d

k3d runs k3s in Docker.

Conceptually:

```bash
k3d cluster create data-learning
kubectl get nodes
```

## 11.3 minikube

minikube provides a local Kubernetes environment with multiple runtime options.

Conceptually:

```bash
minikube start
kubectl get nodes
```

## 11.4 kubeconfig and Context

Kubernetes clients use kubeconfig to know:

- which cluster;
- which API endpoint;
- which credentials/context.

Inspect:

```bash
kubectl config get-contexts
kubectl config current-context
```

### Safety Habit

Before destructive commands, verify:

```bash
kubectl config current-context
kubectl get namespaces
```

A surprisingly common operational failure is running a correct command against the wrong cluster.

### Knowledge Check

- [ ] Can I create a local cluster?
- [ ] Can I identify the current Kubernetes context?
- [ ] Can I list nodes?
- [ ] Can I deploy into a namespace?

---

# 12. First Data Workload: Python Container → Pod

The conceptual relationship is:

```text
Docker Image
     ↓
Kubernetes Pod
     ↓
Container
```

Assume Topic 01 produced:

```text
registry.example.com/data/pipeline:1.0.0
```

Example:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: python-pipeline
spec:
  restartPolicy: Never
  containers:
    - name: pipeline
      image: registry.example.com/data/pipeline:1.0.0
      command: ["python"]
      args: ["-c", "print('Kubernetes data workload started')"]
```

Apply:

```bash
kubectl apply -f python-pod.yaml
```

Inspect:

```bash
kubectl get pod python-pipeline
kubectl describe pod python-pipeline
kubectl logs python-pipeline
```

The purpose is not to build a production pipeline yet.

The purpose is to establish:

```text
Image
 ↓
Pod
 ↓
Container
 ↓
Process
```

### Knowledge Check

- [ ] Can I connect a Docker image to a Kubernetes Pod?
- [ ] Can I inspect the resulting Pod?
- [ ] Can I retrieve application logs?

---

# 13. Jobs: Kubernetes' Core Batch Primitive

Jobs are particularly important for Data Engineers.

A Job represents work that should eventually complete.

Example:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: pipeline-job
spec:
  backoffLimit: 3
  template:
    metadata:
      labels:
        app: pipeline-job
    spec:
      restartPolicy: Never
      containers:
        - name: pipeline
          image: registry.example.com/data/pipeline:1.0.0
          command: ["python"]
          args: ["-m", "pipeline"]
```

## 13.1 Why Jobs Exist

A batch workload has a different lifecycle from an API.

An API:

```text
Start
 ↓
Keep running
```

A batch job:

```text
Start
 ↓
Process data
 ↓
Write result
 ↓
Exit successfully
```

The Job controller understands completion and failure.

## 13.2 Job Status

Useful commands:

```bash
kubectl get jobs
kubectl describe job pipeline-job
kubectl get pods
```

You should understand:

- active;
- succeeded;
- failed;
- completion conditions.

## 13.3 Job Failure

If the container exits unsuccessfully, Kubernetes can create replacement Pods according to Job behavior and retry configuration.

### Data Engineering Failure Mode

Suppose:

```text
Read source
 ↓
Write 500,000 records
 ↓
Crash
```

A retry may execute the write again.

Therefore:

> Kubernetes retries the workload, but Kubernetes does not make your data pipeline idempotent.

Pipeline correctness remains an application/data-engineering responsibility.

### Mental model

> **Job = "complete this work," not "keep this service alive."**

### Knowledge Check

- [ ] Why is Job better than Deployment for one-time ETL?
- [ ] What happens when a Job fails?
- [ ] Why can retries duplicate data?

---

# 14. Job Completion

Jobs support concepts such as:

- `completions`;
- `parallelism`;
- successful completion;
- failure;
- completion mode awareness.

Example:

```yaml
spec:
  completions: 5
  parallelism: 2
```

Interpretation:

```text
Need 5 successful completions
Maximum 2 Pods executing concurrently
```

This is different from:

```yaml
replicas: 5
```

in a Deployment.

## 14.1 Data Processing Example

Imagine five independent partitions:

```text
partition-1
partition-2
partition-3
partition-4
partition-5
```

You may want:

```text
5 completions
2 parallel workers
```

The exact mapping between application work and Job completions must be designed carefully. Kubernetes should not be treated as an automatic distributed-data-processing engine.

### Knowledge Check

- [ ] What does `completions` mean?
- [ ] What does `parallelism` mean?
- [ ] Why are they different?

---

# 15. Job Retries and backoffLimit

Example:

```yaml
spec:
  backoffLimit: 3
```

This controls how many failures Kubernetes will tolerate before considering the Job failed.

## 15.1 Transient Failure

Examples:

- temporary dependency outage;
- transient network error;
- temporary service unavailability.

Retrying may make sense.

## 15.2 Permanent Failure

Examples:

- malformed input;
- invalid credentials;
- programming error;
- incompatible schema.

Blind retries may waste compute and delay diagnosis.

## 15.3 Data Correctness

Suppose:

```text
Job attempt 1
 ↓
writes records
 ↓
fails
 ↓
Job attempt 2
 ↓
writes records again
```

If the destination does not enforce idempotency, duplicates may occur.

Therefore, production pipelines should consider:

- deterministic keys;
- upserts;
- transactional writes;
- checkpoints;
- idempotent partition processing;
- exactly-once mechanisms where appropriate.

Do not confuse Kubernetes retry semantics with data-processing exactly-once semantics.

### Knowledge Check

- [ ] Can I distinguish transient from permanent failure?
- [ ] Why can a Kubernetes retry create duplicate data?
- [ ] What makes a pipeline retry-safe?

---

# 16. Active Deadlines

A batch job can become stuck or run far longer than expected.

Use:

```yaml
spec:
  activeDeadlineSeconds: 3600
```

This sets a maximum active duration for the Job.

## Why It Matters

Without a runtime boundary, a stuck workload can consume:

- CPU;
- memory;
- node capacity;
- downstream connections;
- operational attention.

For data workloads, this is especially useful for:

- scheduled ETL;
- partition processing;
- batch backfills;
- data-quality jobs.

A deadline is not a substitute for fixing slow jobs.

It is an operational safety boundary.

---

# 17. CronJobs

A CronJob creates Jobs according to a schedule.

Example:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: daily-pipeline
spec:
  schedule: "0 2 * * *"
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      backoffLimit: 3
      activeDeadlineSeconds: 3600
      template:
        spec:
          restartPolicy: Never
          containers:
            - name: pipeline
              image: registry.example.com/data/pipeline:1.0.0
              command: ["python", "-m", "pipeline"]
```

## 17.1 The Cron Overlap Problem

Suppose the pipeline should run every hour:

```text
02:00 Run 1 starts
03:00 Run 1 still running
03:00 Run 2 scheduled
```

If overlap is not desired:

```yaml
concurrencyPolicy: Forbid
```

This prevents overlapping Jobs created by the CronJob.

Conceptually:

```text
Run 01 still running
       ↓
Schedule triggers Run 02
       ↓
Forbid
       ↓
Run 02 does not overlap
```

## 17.2 Other Policies

### Allow

Multiple Jobs may run concurrently.

### Forbid

Skip a new run while a previous one is still active.

### Replace

Replace an active run with a new one.

The correct policy depends on workload semantics.

### Data Engineering Consideration

Forbid is often attractive for pipelines that:

- process the same logical period;
- should not overlap;
- can create conflicts when concurrent.

But `Forbid` is not automatically correct. If each run processes an independent partition, concurrency may be desirable.

### Knowledge Check

- [ ] What creates a Job?
- [ ] What does `concurrencyPolicy: Forbid` do?
- [ ] When might concurrent execution actually be desirable?

---

# 18. ConfigMaps

A ConfigMap stores non-secret configuration.

Example:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: pipeline-config
data:
  ENVIRONMENT: "dev"
  BUCKET: "raw-data"
  PIPELINE_MODE: "incremental"
```

A Pod can consume configuration through environment variables:

```yaml
envFrom:
  - configMapRef:
      name: pipeline-config
```

Or a specific key:

```yaml
env:
  - name: PIPELINE_MODE
    valueFrom:
      configMapKeyRef:
        name: pipeline-config
        key: PIPELINE_MODE
```

## Good ConfigMap Data

Examples:

- environment;
- bucket name;
- endpoint;
- pipeline mode;
- feature flags;
- non-sensitive tuning parameters.

## Do Not Put Secrets Here

Do not place:

- passwords;
- API tokens;
- private keys;
- cloud credentials.

Use Secret mechanisms or an external secret system.

### Mental model

> ConfigMap = configuration that is not secret.

---

# 19. Kubernetes Secrets

Kubernetes has a Secret object:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: pipeline-secret
type: Opaque
stringData:
  API_TOKEN: "replace-with-development-value"
```

Using `stringData` makes the manifest easier to read during learning; Kubernetes handles the representation internally.

## Critical Security Warning

Kubernetes Secrets are **not automatically encrypted merely because they are called Secrets**.

Base64 encoding is not encryption.

For example:

```text
plain text
   ↓
base64
   ↓
encoded bytes
```

Anyone who can decode the value can recover it.

Production security depends on:

- access control;
- least-privilege RBAC;
- encryption at rest configuration;
- secure cluster configuration;
- external secret stores where appropriate;
- workload identity;
- secret rotation.

This module does not replace Topic 07, which covers cloud secrets managers.

### Knowledge Check

- [ ] Can I explain ConfigMap vs Secret?
- [ ] Why is Base64 not encryption?
- [ ] What additional controls protect Kubernetes secrets?

---

# 20. Resource Requests and Limits

This is one of the most important topics for Data Engineers.

Example:

```yaml
resources:
  requests:
    cpu: "500m"
    memory: "512Mi"
  limits:
    cpu: "1"
    memory: "1Gi"
```

## 20.1 Requests

Requests represent the resources the scheduler uses when making placement decisions.

Conceptually:

```text
Request:
"I need approximately this much capacity reserved for scheduling."
```

A Pod requesting:

```yaml
memory: "4Gi"
```

cannot be scheduled onto a node if sufficient schedulable memory is unavailable.

## 20.2 Limits

Limits define an upper resource boundary for the container.

For memory, exceeding the effective memory limit can result in termination and `OOMKilled`.

For CPU, a limit can cause CPU throttling.

## 20.3 CPU Throttling

Suppose:

```yaml
limits:
  cpu: "500m"
```

If the application wants substantially more CPU than its allowed CPU budget, it may be throttled.

This can cause:

- slower ETL;
- longer Spark driver activity;
- increased latency;
- missed processing windows.

CPU throttling can be especially confusing because the process may not crash; it may simply become slow.

## 20.4 Noisy Neighbors

A large Spark workload can compete with:

- APIs;
- orchestration components;
- Kafka consumers;
- monitoring workloads.

Resource requests and scheduling policies help prevent uncontrolled contention.

### Mental model

> Requests influence placement. Limits constrain consumption.

### Knowledge Check

- [ ] What does the scheduler use requests for?
- [ ] What happens when a memory limit is exceeded?
- [ ] What is CPU throttling?
- [ ] Why are resource settings important for data workloads?

---

# 21. OOMKilled

`OOMKilled` means the container was terminated because it exceeded its available memory boundary.

Typical scenario:

```text
Python ETL
    ↓
loads data into memory
    ↓
memory increases
    ↓
container reaches memory limit
    ↓
OOMKilled
```

Inspect:

```bash
kubectl describe pod <pod-name>
kubectl get events --sort-by=.lastTimestamp
kubectl logs <pod-name>
```

For restarted containers:

```bash
kubectl logs <pod-name> --previous
```

## 21.1 Do Not Immediately Increase the Limit

There are several possibilities:

1. the application has a memory leak;
2. the algorithm loads too much data at once;
3. the input partition is unexpectedly large;
4. the memory limit is too low;
5. the node is under pressure;
6. the workload's resource model is incorrect.

Blindly increasing memory can hide an application problem.

## 21.2 Data Pipeline Sizing Method

Use:

```text
1. Measure locally
2. Measure peak memory
3. Add a safety margin
4. Set request
5. Set limit
6. Run in Kubernetes
7. Measure actual usage
8. Adjust
```

Do not invent resource values without measurement.

## 21.3 Python Example

Bad pattern:

```python
rows = list(read_entire_dataset())
process(rows)
```

Potentially better:

```python
for batch in read_batches():
    process(batch)
```

Kubernetes resource configuration and application memory design must be considered together.

---

# 22. Data Job Sizing

Sizing is an engineering process, not a guessing game.

For a Python pipeline:

```text
Input size
    ↓
Algorithm behavior
    ↓
Peak memory
    ↓
CPU utilization
    ↓
I/O behavior
    ↓
Resource request/limit
```

Measure:

- peak memory;
- CPU usage;
- runtime;
- concurrency;
- input volume;
- output volume.

For Spark, sizing is more complex because the application includes:

- driver;
- executors;
- executor cores;
- executor memory;
- shuffle;
- serialization;
- cluster capacity.

Spark sizing belongs primarily to the Spark module; here the important concept is:

> Kubernetes schedules the Spark Pods, so Kubernetes resource requests and cluster capacity must align with Spark's requested resources.

---

# 23. ServiceAccounts

A ServiceAccount provides an identity for a workload.

Example:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: pipeline
  namespace: data-platform
```

A Pod can use it:

```yaml
spec:
  serviceAccountName: pipeline
```

## Why ServiceAccounts Exist

A workload should not normally act as a human administrator.

Prefer:

```text
Pipeline
   ↓
pipeline ServiceAccount
   ↓
specific permissions
```

instead of:

```text
Pipeline
   ↓
human administrator credentials
```

Good workload identity design uses narrowly scoped identities.

Example:

```text
Airflow task → airflow ServiceAccount
Spark workload → spark ServiceAccount
Pipeline → pipeline ServiceAccount
```

Do not automatically use one shared high-privilege identity for everything.

---

# 24. Workload Identity

In cloud environments, Kubernetes workloads can often exchange their workload identity for cloud permissions without storing long-lived cloud access keys in containers.

Conceptually:

```text
Kubernetes Pod
      ↓
ServiceAccount
      ↓
Workload Identity
      ↓
Cloud IAM role
      ↓
Object Storage / Warehouse
```

This is preferable to embedding:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```

or equivalent long-lived credentials into application images.

## Data Engineering Example

Suppose a Spark workload needs to read from object storage:

```text
Spark Pod
   ↓
Kubernetes identity
   ↓
Cloud workload identity
   ↓
Read permission
   ↓
Object Storage
```

The application can access the data without shipping a permanent secret inside the image.

This connects directly to the cloud platform concepts from Module 2.17.

### Security Principle

> Give the workload an identity, not a copied human credential.

### Knowledge Check

- [ ] What is a ServiceAccount?
- [ ] Why should workloads not use human credentials?
- [ ] What is workload identity?
- [ ] Why is it preferable to long-lived cloud access keys?

---

# 25. Helm

Helm is a package manager and templating/deployment tool for Kubernetes applications.

A Helm Chart can package:

- Kubernetes manifests;
- templates;
- default values;
- dependencies;
- deployment metadata.

Mental model:

```text
Helm Chart
     +
values.yaml
     ↓
Rendered Kubernetes manifests
     ↓
Kubernetes API
```

## 25.1 Important Concepts

### Chart

The package containing templates and metadata.

### Values

Configuration supplied to templates.

### Templates

Parameterized Kubernetes manifests.

### Release

An installed instance of a chart.

### Repository

A location from which charts can be obtained.

## 25.2 Useful Commands

Inspect available releases:

```bash
helm list
```

Install:

```bash
helm install airflow <chart>
```

Upgrade:

```bash
helm upgrade airflow <chart>
```

Remove:

```bash
helm uninstall airflow
```

Render locally:

```bash
helm template airflow <chart>
```

`helm template` is especially useful for understanding what Kubernetes YAML will actually be generated.

### Knowledge Check

- [ ] What is a Chart?
- [ ] What are values?
- [ ] What is a release?
- [ ] Why is `helm template` useful?

---

# 26. Airflow with Helm

A production Data Engineer may encounter Airflow deployed onto Kubernetes.

The deployment process commonly involves:

```text
Airflow Helm Chart
       +
Airflow configuration values
       ↓
Kubernetes manifests
       ↓
Airflow components
```

The goal here is not to reteach Airflow.

Focus on:

- how Helm packages the deployment;
- how values configure it;
- how Airflow components become Kubernetes workloads;
- how task execution can be delegated to Pods.

A practical learning exercise is to install the official Apache Airflow Helm chart in a local cluster using the chart's current documented values and version.

Always pin the chart/application version in reproducible environments rather than relying blindly on whatever version happens to be latest.

---

# 27. Data Workload Patterns

A useful mapping is:

| Workload | Kubernetes Primitive |
|---|---|
| Long-running API | Deployment |
| One-time ETL | Job |
| Scheduled ETL | CronJob |
| Kafka consumer | Deployment |
| Spark batch | Job / Spark integration |
| Airflow task | Pod-based execution |
| Supporting service | Deployment |

The key is workload lifecycle.

```text
Deployment
= keep running

Job
= finish work

CronJob
= create Jobs on schedule
```

### Knowledge Check

- [ ] Can I choose the correct primitive for an API?
- [ ] Can I choose the correct primitive for ETL?
- [ ] Can I explain why Kafka consumers are commonly Deployments?

---

# 28. Kubernetes Operators

An Operator is a Kubernetes controller pattern that combines:

```text
Controller
+
Domain-specific operational knowledge
```

Operators commonly use:

- Custom Resource Definitions (CRDs);
- reconciliation;
- desired state;
- lifecycle automation.

Conceptually:

```text
Custom Resource
      ↓
Operator
      ↓
Reconciliation
      ↓
Kubernetes workloads/resources
```

## Why Operators Matter for Data Engineering

Complex distributed systems have domain-specific lifecycle concerns.

Examples:

- Spark applications;
- Kafka clusters;
- Flink workloads.

Instead of manually managing every Kubernetes object, an operator can provide a higher-level declarative interface.

Mental model:

> An Operator teaches Kubernetes how to manage a particular class of application.

---

# 29. Spark on Kubernetes

A Spark application can use Kubernetes as its compute scheduler.

Conceptually:

```text
Spark submission
      ↓
Driver Pod
      ↓
Executor Pods
      ↓
Object Storage
```

The Spark driver coordinates the application.

Executors perform distributed work.

Kubernetes manages the Pods that contain these processes.

## Why This Matters

A data platform can use Kubernetes as a common compute substrate:

```text
Airflow
Spark
Kafka consumers
Flink
APIs
```

The same cluster can schedule different workload types, provided resource and scheduling policies are designed correctly.

This module does not repeat Spark architecture, transformations, shuffle tuning, or AQE from Module 2.14.

---

# 30. Spark Operator Awareness

A Spark Operator can provide a declarative Kubernetes representation of Spark applications.

The mental model is:

```text
SparkApplication
      ↓
Spark Operator
      ↓
Driver + Executor Pods
```

The operator handles application lifecycle according to its implementation.

For this roadmap, you need to understand:

- what an operator is;
- why a Spark operator exists;
- what CRDs represent;
- why declarative application management is useful.

You do not need to become an Operator developer.

---

# 31. Kafka Operators

A Kafka Operator can manage Kafka-related resources declaratively.

Conceptually:

```text
Kafka custom resource
       ↓
Kafka Operator
       ↓
Kafka cluster/resources
```

Depending on the operator ecosystem, it may help manage:

- Kafka cluster lifecycle;
- topics;
- users;
- listeners;
- related resources.

Do not treat an operator as a replacement for understanding Kafka.

Module 2.16 remains the source for Kafka architecture and streaming fundamentals.

---

# 32. Flink Operators

The same pattern applies to Flink.

Conceptually:

```text
Flink resource
     ↓
Flink Operator
     ↓
Flink workload
```

The operator can provide declarative lifecycle management.

The important connection is:

```text
Flink
 ↓
Kubernetes resource model
 ↓
Operator reconciliation
```

You need awareness rather than Operator-development expertise.

---

# 33. Airflow Kubernetes Executor

The Kubernetes Executor allows Airflow tasks to execute in Kubernetes Pods.

Conceptually:

```text
Airflow Scheduler
       ↓
Kubernetes API
       ↓
Task Pod
       ↓
Task execution
```

Benefits can include:

- task isolation;
- per-task resource configuration;
- different task environments;
- scalable task execution.

For example:

```text
Task A → 500m CPU / 1Gi
Task B → 2 CPU / 4Gi
Task C → special image
```

This can be valuable when one Airflow DAG contains heterogeneous tasks.

Do not confuse:

```text
Airflow running on Kubernetes
```

with:

```text
Every Airflow task necessarily running in the same Pod
```

The execution model matters.

---

# 34. KubernetesPodOperator

Airflow's KubernetesPodOperator lets an Airflow task launch a Kubernetes Pod.

Conceptually:

```text
Airflow DAG
   ↓
KubernetesPodOperator
   ↓
Pod
   ↓
Python / Spark / custom container
```

Relevant settings include:

- image;
- command;
- environment;
- resources;
- ServiceAccount;
- Pod lifecycle.

A data pipeline might use a purpose-built image:

```text
DAG task
   ↓
pipeline image
   ↓
Kubernetes Pod
   ↓
extract → transform → load
```

This can be useful when task dependencies differ from the Airflow scheduler's environment.

---

# 35. Autoscaling

Autoscaling has multiple layers.

## 35.1 Horizontal Pod Autoscaler

HPA scales Pods based on supported metrics.

Conceptually:

```text
Metric
  ↓
HPA
  ↓
More/fewer Pods
```

For example:

```text
CPU utilization
     ↓
HPA
     ↓
consumer replicas
```

## 35.2 Cluster / Node Autoscaling

If there is no node capacity for a newly requested Pod:

```text
Pending Pod
    ↓
insufficient node capacity
    ↓
node autoscaler
    ↓
new node
    ↓
Pod can schedule
```

Pod autoscaling and node autoscaling solve different problems.

## 35.3 Event-Driven Scaling

Data systems often have workload signals that are more meaningful than CPU.

Kafka consumer lag is a classic example:

```text
Kafka
  ↓
Consumer lag
  ↓
Scaling signal
  ↓
More consumer Pods
  ↓
Higher consumption throughput
```

The exact implementation may use an event-driven autoscaling system, but the engineering principle is the important part.

---

# 36. Consumer-Lag-Driven Scaling

CPU is not always a good proxy for streaming workload demand.

Imagine:

```text
Kafka arrival rate = high
Consumer CPU = moderate
Consumer lag = increasing rapidly
```

CPU-based HPA may not scale soon enough.

A lag-aware strategy can respond to:

```text
lag ↑
  ↓
consumer replicas ↑
  ↓
processing capacity ↑
  ↓
lag ↓
```

But scaling consumers is not automatically safe.

Consider:

- Kafka partition count;
- consumer-group semantics;
- downstream capacity;
- ordering requirements;
- database write throughput;
- checkpoint/state behavior.

Scaling should respect the architecture of the streaming system.

---

# 37. Spot Node Pools

Spot/preemptible capacity can reduce infrastructure cost but can be interrupted.

This makes it attractive for interruption-tolerant workloads such as:

- batch processing;
- some Spark workloads;
- replayable computations.

It is less suitable for workloads requiring uninterrupted availability unless the architecture explicitly tolerates interruption.

A useful classification is:

```text
Batch / replayable
     ↓
often more spot-friendly

Latency-sensitive / stateful
     ↓
requires stronger interruption strategy
```

Do not treat spot capacity as "free compute." It changes failure assumptions.

---

# 38. Scheduling Data Workloads

Consider:

```text
Heavy Spark workload
        +
Latency-sensitive API
        ↓
Resource contention
        ↓
Poor platform behavior
```

Kubernetes scheduling controls can separate these workload classes.

Relevant concepts:

- node pools;
- taints;
- tolerations;
- affinity;
- anti-affinity awareness.

---

# 39. Node Pools

A production cluster may have specialized node groups/pools:

```text
General nodes
    ↓
APIs / platform components

Spark nodes
    ↓
distributed batch workloads

Streaming nodes
    ↓
Kafka/Flink/consumer workloads
```

This is not mandatory for every platform.

Specialization becomes valuable when workloads have materially different:

- CPU/memory profiles;
- interruption tolerance;
- performance requirements;
- scaling behavior.

---

# 40. Taints and Tolerations

A taint can discourage or prevent ordinary Pods from scheduling onto a node.

Mental model:

> **Taint = "Do not schedule here unless you explicitly tolerate it."**

Example conceptual taint:

```text
workload=spark:NoSchedule
```

A Spark workload can declare a matching toleration.

Example:

```yaml
tolerations:
  - key: "workload"
    operator: "Equal"
    value: "spark"
    effect: "NoSchedule"
```

This means the workload is allowed onto that tainted node.

### Important Distinction

A toleration does not force scheduling.

It merely makes the workload eligible for the tainted node.

You may combine tolerations with node affinity.

---

# 41. Affinity

Affinity provides scheduling preferences or requirements.

Example concept:

```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
        - matchExpressions:
            - key: workload
              operator: In
              values:
                - spark
```

This expresses:

```text
Schedule this workload onto nodes labeled for Spark.
```

## Pod Anti-Affinity Awareness

For replicated services, you may prefer replicas to spread across nodes.

Conceptually:

```text
API replica 1 → node-1
API replica 2 → node-2
```

rather than:

```text
API replica 1 → node-1
API replica 2 → node-1
```

This improves resilience to node failure.

---

# 42. Storage: PersistentVolumes and PVCs

Kubernetes storage commonly uses:

```text
Pod
 ↓
PersistentVolumeClaim (PVC)
 ↓
PersistentVolume (PV)
 ↓
Storage backend
```

A PVC requests storage.

Example:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pipeline-cache
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

The cluster's storage system may provision or bind a PersistentVolume.

## StorageClass Awareness

A StorageClass describes how storage is provisioned.

For Data Engineers, the important point is:

> Kubernetes persistent storage is useful for workload-specific durable state, but it should not automatically become the data lake.

---

# 43. Object-Storage-First Architecture

The roadmap's core architectural principle is:

> **Data workloads should generally prefer object storage for durable datasets instead of treating Kubernetes persistent volumes as the data lake.**

Examples:

```text
S3
GCS
ADLS
```

Conceptually:

```text
Kubernetes
   ↓
Ephemeral compute
   ↓
Object Storage
   ↓
Lakehouse
```

Why?

### Scalability

Object storage is designed to scale independently from compute.

### Durability

Durability characteristics are provided by the storage platform rather than tied to individual worker nodes.

### Compute/storage separation

You can destroy and recreate compute without destroying the dataset.

### Lifecycle management

Object storage supports broader lifecycle and retention architectures.

This connects to Module 2.17 without repeating its complete storage curriculum.

### Mental model

> Kubernetes is primarily the compute/orchestration layer; object storage is generally the durable data layer.

---

# 44. GitOps Awareness

GitOps treats Git as a source of desired deployment state.

Conceptually:

```text
Git repository
      ↓
GitOps controller
      ↓
Kubernetes
      ↓
Workloads
```

Two important examples are:

- Argo CD;
- Flux.

## Why GitOps?

Git provides:

- history;
- review;
- auditability;
- reproducibility;
- change visibility.

The controller continuously reconciles cluster state with the desired state represented by Git.

This is philosophically similar to Kubernetes reconciliation itself:

```text
Declared desired state
       ↓
Reconciliation
       ↓
Actual state
```

GitOps adds Git as the source of that declared state.

### Important Scope Boundary

This module only teaches GitOps awareness.

It does not become the roadmap's complete CI/CD or environment-promotion module.

---

# 45. Complete Data Engineering Architecture

A realistic conceptual architecture is:

```text
                         Kubernetes Cluster
                                |
              +-----------------+-----------------+
              |                 |                 |
           Airflow            Spark           Streaming
              |                 |                 |
         Task Pods          Driver Pod        Kafka/Flink
              |                 |                 |
              +-----------------+-----------------+
                                |
                         Object Storage
                       S3 / GCS / ADLS
                                |
                           Data Lakehouse
```

## Responsibilities

### Airflow

Orchestrates data workflows.

### Spark

Performs distributed batch processing.

### Kafka/Flink

Handle streaming/event workloads.

### Kubernetes

Provides:

- compute scheduling;
- workload lifecycle;
- resource management;
- service discovery;
- identity integration;
- autoscaling;
- workload isolation.

### Object Storage

Stores durable datasets.

### Lakehouse

Provides the analytical table/storage layer.

---

# 46. Kubernetes vs Docker Compose

| Capability | Docker Compose | Kubernetes |
|---|---|---|
| Local development | Excellent | Possible |
| Single host | Excellent | Possible |
| Cluster scheduling | Limited | Strong |
| Self-healing | Limited | Strong |
| Horizontal scaling | Limited | Strong |
| Resource scheduling | Basic | Strong |
| Production orchestration | Limited | Designed for it |
| Data workload operators | No general operator model | Supported |
| Multi-node workloads | Not its primary purpose | Core capability |
| Declarative reconciliation | Limited | Core concept |

Why learn Compose first?

Because the mental model progresses naturally:

```text
Compose:
multiple containers on one machine
          ↓
Kubernetes:
multiple workloads across a cluster
```

Compose remains extremely valuable for local development and integration testing.

Kubernetes is not simply "Compose with more YAML."

---

# 47. Debugging Kubernetes Data Workloads

A disciplined debugging sequence is:

```text
1. kubectl get
2. kubectl describe
3. kubectl logs
4. kubectl get events
5. kubectl exec
6. inspect resources
7. inspect configuration
8. inspect networking
9. inspect identity
10. inspect scheduling
```

Do not immediately change five things at once.

First establish the failure.

---

# 48. Debugging: Pending Pod

A Pod in `Pending` means it has not reached the point of successfully running.

Start:

```bash
kubectl get pod <pod>
kubectl describe pod <pod>
kubectl get events --sort-by=.lastTimestamp
```

Investigate:

- resource requests;
- available node capacity;
- node selectors;
- affinity;
- taints;
- tolerations;
- PVC availability.

## Common Scenario

Spark Pod:

```text
Pending
```

because:

```text
requested:
  cpu: 8
  memory: 32Gi
```

but no eligible node has sufficient capacity.

The answer is not necessarily "add more memory."

It may be:

- reduce request;
- change scheduling constraints;
- use the correct node pool;
- add capacity;
- change workload parallelism.

---

# 49. Debugging: CrashLoopBackOff

Start:

```bash
kubectl logs <pod>
kubectl logs <pod> --previous
kubectl describe pod <pod>
```

Possible causes:

- application exception;
- missing environment variable;
- missing secret;
- invalid command;
- dependency failure;
- incorrect configuration;
- application exits immediately.

Example:

```text
CrashLoopBackOff
      ↓
logs --previous
      ↓
"POSTGRES_HOST is not set"
      ↓
inspect ConfigMap / environment
```

The status tells you the symptom; logs often reveal the application-level cause.

---

# 50. Debugging: ImagePullBackOff

Investigate:

```bash
kubectl describe pod <pod>
```

Look for image-related events.

Check:

- image name;
- image tag;
- registry;
- image existence;
- registry authentication;
- architecture;
- image pull policy assumptions.

Example:

```yaml
image: registry.example.com/data/pipeline:1.0.0
```

If the registry does not contain that exact image reference, the workload cannot start.

This connects to Topic 01 without reteaching Docker image construction.

---

# 51. Debugging: OOMKilled

Start:

```bash
kubectl describe pod <pod>
kubectl get events --sort-by=.lastTimestamp
kubectl logs <pod> --previous
```

Determine:

1. What was the memory limit?
2. What was the application doing?
3. Was input volume larger than expected?
4. Is there evidence of a memory leak?
5. Is the algorithm unnecessarily materializing data?
6. Is node pressure involved?

Do not simply raise the limit without understanding the cause.

---

# 52. Debugging: Failed Job

Start:

```bash
kubectl get jobs
kubectl describe job <job>
kubectl get pods
kubectl logs <failed-pod>
```

Then determine:

- application failure;
- dependency failure;
- resource failure;
- scheduling failure;
- configuration failure;
- retry behavior.

If the Job retries, inspect whether the application is safe to retry.

---

# 53. Debugging: CronJob Overlap

Inspect:

```bash
kubectl get cronjobs
kubectl get jobs
```

Check:

```yaml
concurrencyPolicy: Forbid
```

Then reason about:

- schedule frequency;
- average runtime;
- maximum runtime;
- missed schedules;
- whether overlap is actually undesirable.

A scheduler policy should reflect data semantics.

---

# 54. Debugging: Service Connectivity

Suppose:

```text
pipeline → postgres
```

fails.

Check:

```bash
kubectl get svc
kubectl describe svc postgres
kubectl get pods --show-labels
```

Confirm:

- Service exists;
- selector matches Pod labels;
- target port is correct;
- Pods are Ready;
- DNS name is correct.

A common mistake is using:

```text
localhost
```

inside a Pod to reach another Pod.

Inside a container:

```text
localhost
```

means the same Pod/network namespace, not "the Kubernetes cluster."

Use the Service DNS name for another workload.

---

# 55. Debugging: ServiceAccount / Permission Failure

If a workload cannot access a Kubernetes or cloud resource:

Check:

```bash
kubectl get pod <pod> -o yaml
```

Look for:

```yaml
serviceAccountName: pipeline
```

Then inspect the workload's intended identity and permission model.

For cloud access, verify:

```text
Pod
 ↓
ServiceAccount
 ↓
Workload Identity
 ↓
Cloud IAM
```

Do not solve permission problems by copying broad credentials into the container.

---

# 56. Incident Simulation: OOMKilled

## Scenario

A Python ETL job runs successfully locally but becomes:

```text
OOMKilled
```

in Kubernetes.

## Learner Tasks

1. Inspect the Pod.
2. Inspect events.
3. Identify memory request and limit.
4. Inspect previous logs.
5. Measure application memory.
6. Determine whether the algorithm materializes too much data.
7. Increase resources only if justified.
8. Rerun.
9. Compare runtime and peak memory.

## Reference Reasoning

A strong Data Engineer asks:

```text
Is the application inefficient?
       OR
Is the resource limit incorrect?
       OR
Is the input unexpectedly larger?
```

not merely:

```text
Can I make the limit bigger?
```

---

# 57. Incident Simulation: Pending Spark Pod

## Scenario

A Spark workload remains Pending.

## Investigation

```bash
kubectl describe pod <spark-pod>
kubectl get nodes
kubectl get events --sort-by=.lastTimestamp
```

Inspect:

- CPU request;
- memory request;
- node availability;
- node labels;
- affinity;
- taints;
- tolerations.

## Reference Reasoning

If:

```text
Spark request
CPU = 8
Memory = 32Gi
```

but all eligible Spark nodes have less capacity, Kubernetes cannot schedule it.

Possible solutions include:

- capacity adjustment;
- node-pool adjustment;
- resource request correction;
- scheduling-policy correction;
- workload parallelism change.

---

# 58. Incident Simulation: CrashLoopBackOff

## Scenario

A pipeline Pod repeatedly crashes.

Commands:

```bash
kubectl logs <pod>
kubectl logs <pod> --previous
kubectl describe pod <pod>
```

Potential root causes:

- bad configuration;
- missing environment variable;
- missing secret;
- application exception;
- wrong command;
- dependency connectivity.

The key lesson:

> Start with evidence before changing infrastructure.

---

# 59. Incident Simulation: ImagePullBackOff

## Scenario

The cluster cannot pull:

```text
registry.example.com/data/pipeline:1.0.0
```

Check:

```bash
kubectl describe pod <pod>
```

Then verify:

- repository;
- tag;
- registry accessibility;
- image existence;
- credentials;
- architecture.

A production deployment should use deterministic image references and an appropriately configured registry.

---

# 60. Hands-On Lab

## Objective

Build a local Kubernetes data-workload environment progressively.

You may use:

- kind;
- k3d;
- minikube.

## Step 1 — Create Cluster

Example with kind:

```bash
kind create cluster --name data-learning
kubectl config current-context
kubectl get nodes
```

## Step 2 — Create Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: data-platform
```

Apply:

```bash
kubectl apply -f namespace.yaml
```

Verify:

```bash
kubectl get namespace data-platform
```

## Step 3 — Run Python Pod

Use the Python image built in Topic 01 or a suitable test image.

```bash
kubectl apply -f python-pod.yaml
kubectl get pods -n data-platform
kubectl logs -n data-platform python-pipeline
```

## Step 4 — Create Deployment

Deploy a long-running test service.

Validate:

```bash
kubectl get deployment -n data-platform
kubectl get pods -n data-platform
```

## Step 5 — Create Service

Expose the Deployment internally.

Validate:

```bash
kubectl get service -n data-platform
```

## Step 6 — Create Job

Run a one-time pipeline.

```bash
kubectl get jobs -n data-platform
kubectl get pods -n data-platform
```

## Step 7 — Create CronJob

Use:

```yaml
concurrencyPolicy: Forbid
```

Validate:

```bash
kubectl get cronjobs -n data-platform
kubectl get jobs -n data-platform
```

## Step 8 — Add ConfigMap

Inject:

```text
environment
bucket
pipeline mode
```

## Step 9 — Add Secret

Use development-only values.

Do not commit real production credentials.

## Step 10 — Add Resources

Configure:

```yaml
resources:
  requests:
    cpu: "250m"
    memory: "256Mi"
  limits:
    cpu: "1"
    memory: "1Gi"
```

These are learning examples, not universal production sizing values.

## Step 11 — Add ServiceAccount

Create:

```text
pipeline
```

and attach it to the workload.

## Step 12 — Install Airflow with Helm

Use the current official Apache Airflow chart documentation and pin a version suitable for the lab.

Inspect rendered manifests when possible:

```bash
helm template ...
```

## Step 13 — Run a Spark Workload

Use a Spark-on-Kubernetes example appropriate for the Spark version in your environment.

Observe:

```text
Driver Pod
Executor Pods
```

## Step 14 — Introduce Failures

Intentionally produce:

- OOMKilled;
- Pending Pod;
- CrashLoopBackOff;
- ImagePullBackOff;
- CronJob overlap.

Then diagnose each using the methodology in this module.

---

# 61. Required YAML Reference

This section provides compact reference manifests.

## 61.1 Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pipeline
spec:
  restartPolicy: Never
  containers:
    - name: pipeline
      image: example/data-pipeline:1.0.0
      command: ["python"]
      args: ["-m", "pipeline"]
```

## 61.2 Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: data-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: data-api
  template:
    metadata:
      labels:
        app: data-api
    spec:
      containers:
        - name: api
          image: example/data-api:1.0.0
          ports:
            - containerPort: 8000
```

## 61.3 Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: data-api
spec:
  selector:
    app: data-api
  ports:
    - port: 80
      targetPort: 8000
```

## 61.4 Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: data-platform
```

## 61.5 Job

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: pipeline-job
spec:
  backoffLimit: 3
  activeDeadlineSeconds: 3600
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: pipeline
          image: example/data-pipeline:1.0.0
```

## 61.6 CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: daily-pipeline
spec:
  schedule: "0 2 * * *"
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      backoffLimit: 3
      template:
        spec:
          restartPolicy: Never
          containers:
            - name: pipeline
              image: example/data-pipeline:1.0.0
```

## 61.7 ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: pipeline-config
data:
  ENVIRONMENT: "dev"
  BUCKET: "raw-data"
```

## 61.8 Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: pipeline-secret
type: Opaque
stringData:
  API_TOKEN: "development-only-placeholder"
```

## 61.9 ServiceAccount

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: pipeline
```

## 61.10 Resources

```yaml
resources:
  requests:
    cpu: "500m"
    memory: "512Mi"
  limits:
    cpu: "1"
    memory: "1Gi"
```

---

# 62. Scheduling YAML Concepts

## 62.1 Toleration

```yaml
tolerations:
  - key: "workload"
    operator: "Equal"
    value: "spark"
    effect: "NoSchedule"
```

## 62.2 Node Affinity

```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
        - matchExpressions:
            - key: workload
              operator: In
              values:
                - spark
```

## 62.3 PVC

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pipeline-cache
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

These examples illustrate concepts. Actual storage classes, labels, node pools, and capacity depend on the Kubernetes environment.

---

# 63. Autoscaling Concept

A conceptual HPA looks like:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: consumer
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: consumer
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

This is a CPU-based example.

For streaming systems, CPU may not be the best signal. Consumer lag can be more meaningful.

---

# 64. Measurement

The roadmap requires measurement rather than invented performance claims.

Measure:

- Pod startup time;
- Job completion time;
- CPU usage;
- memory usage;
- requested vs actual resources;
- OOM events;
- retry counts;
- scaling behavior.

Useful commands include:

```bash
kubectl get pods
kubectl describe pod <pod>
kubectl get jobs
kubectl get events --sort-by=.lastTimestamp
```

Where metrics-server or another metrics solution is available:

```bash
kubectl top pods
kubectl top nodes
```

Record measurements in a table:

| Workload | Input | CPU Request | Memory Request | Peak CPU | Peak Memory | Runtime | Retries | OOM |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Python ETL | measured | measured | measured | measured | measured | measured | measured | yes/no |

Do not fill the table with fabricated values.

The objective is to learn the measurement loop:

```text
Configure
 ↓
Run
 ↓
Measure
 ↓
Compare
 ↓
Adjust
 ↓
Run again
```

---

# 65. Conceptual Exercises

## Exercise 1 — Why Kubernetes?

Why is Docker insufficient for a large multi-node data platform?

### Solution

Docker packages and runs containers, but production platforms also need cluster scheduling, desired-state reconciliation, workload replacement, service discovery, resource management, scaling, and workload isolation. Kubernetes provides those orchestration capabilities.

---

## Exercise 2 — Cluster vs Node

What is the difference?

### Solution

A cluster is the overall Kubernetes environment. A node is an individual machine inside the cluster capable of running Pods.

---

## Exercise 3 — Pod vs Container

### Solution

A container is the packaged application process. A Pod is Kubernetes' basic scheduling unit and can contain one or more containers sharing network and storage context.

---

## Exercise 4 — Deployment vs Job

### Solution

Deployment expresses a long-running desired service state. Job expresses completion-oriented batch work.

---

## Exercise 5 — Job vs CronJob

### Solution

A Job runs a batch workload to completion. A CronJob creates Jobs according to a schedule.

---

## Exercise 6 — Service Discovery

Why should a pipeline not connect directly to a Pod IP?

### Solution

Pod IPs can change when Pods are replaced. A Service provides a stable endpoint and DNS name.

---

## Exercise 7 — Namespace

Why use namespaces?

### Solution

For organization, workload separation, policy boundaries, and clearer resource management. A namespace alone is not a complete security boundary.

---

## Exercise 8 — Desired vs Actual State

If desired replicas are 3 and actual replicas are 2, what does Kubernetes attempt to do?

### Solution

The appropriate controller reconciles the difference and attempts to restore the desired state of three replicas.

---

## Exercise 9 — ConfigMap vs Secret

### Solution

ConfigMap is for non-secret configuration. Secret is intended for sensitive values, but Kubernetes Secret storage is not automatically encrypted merely because it is a Secret object.

---

## Exercise 10 — Requests vs Limits

### Solution

Requests influence scheduling. Limits establish resource ceilings. Memory limit violations can produce OOMKilled; CPU limits can produce throttling.

---

## Exercise 11 — OOMKilled

What are two possible root causes?

### Solution

The workload may genuinely require more memory, or the application may have poor memory behavior such as materializing too much data or leaking memory.

---

## Exercise 12 — ServiceAccount

Why should workloads use dedicated identities?

### Solution

Least-privilege workload identities reduce the blast radius of compromised workloads and avoid using human credentials.

---

## Exercise 13 — Workload Identity

Explain:

```text
Pod → ServiceAccount → Workload Identity → Cloud IAM → Object Storage
```

### Solution

The Pod receives an identity that can be mapped to cloud permissions, allowing access without storing long-lived cloud credentials inside the container.

---

## Exercise 14 — Helm

Why is Helm useful?

### Solution

It packages complex Kubernetes deployments into reusable charts with parameterized values and versioned releases.

---

## Exercise 15 — Operator

What is an Operator?

### Solution

A Kubernetes controller that encodes domain-specific operational knowledge and reconciles custom resources into the desired application state.

---

## Exercise 16 — Autoscaling

What are the three broad scaling layers?

### Solution

Pod-level horizontal scaling, cluster/node capacity scaling, and event-driven scaling based on workload signals.

---

## Exercise 17 — Taints/Tolerations

What does a toleration do?

### Solution

It permits a Pod to be scheduled onto a node with a matching taint. It does not by itself force placement.

---

## Exercise 18 — Affinity

Why use node affinity?

### Solution

To constrain or prefer placement based on node labels, such as scheduling Spark workloads onto specialized Spark nodes.

---

## Exercise 19 — PV/PVC

What is a PVC?

### Solution

A PersistentVolumeClaim is a workload's request for persistent storage. It can bind to a PersistentVolume provided by the cluster's storage system.

---

## Exercise 20 — GitOps

What does GitOps add to Kubernetes?

### Solution

It makes Git the desired-state source and uses a controller such as Argo CD or Flux to reconcile Kubernetes with that state.

---

## Exercise 21 — Compose vs Kubernetes

When is Compose often preferable?

### Solution

Local development, simple single-host integration environments, and lightweight reproducible stacks.

---

## Exercise 22 — When Not to Use Kubernetes

### Solution

If workloads are small/simple, a managed data service or serverless platform meets requirements, the team is small, or Kubernetes operational complexity provides little benefit, use the simpler platform.

---

# 66. YAML / Coding Exercises

## Exercise 1 — Create a Python Pod

### Objective

Run a Python container as a Kubernetes Pod.

### Code

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: python-pipeline
spec:
  restartPolicy: Never
  containers:
    - name: pipeline
      image: python:3.12-slim
      command: ["python", "-c"]
      args: ["print('hello from Kubernetes')"]
```

### Validation

```bash
kubectl apply -f pod.yaml
kubectl get pods
kubectl logs python-pipeline
```

### Expected Behavior

The Pod completes successfully.

### Common Mistake

Expecting a completed Pod to remain `Running`.

### Troubleshooting

Use:

```bash
kubectl describe pod python-pipeline
kubectl logs python-pipeline
```

---

## Exercise 2 — Convert It to a Deployment

### Objective

Create a long-running workload.

### Solution

Use a long-running process rather than a one-time Python command:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: python-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: python-service
  template:
    metadata:
      labels:
        app: python-service
    spec:
      containers:
        - name: app
          image: python:3.12-slim
          command: ["python", "-c"]
          args: ["import time; time.sleep(3600)"]
```

Validate:

```bash
kubectl get deployment
kubectl get pods
```

---

## Exercise 3 — Add a Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: python-service
spec:
  selector:
    app: python-service
  ports:
    - port: 80
      targetPort: 8000
```

For a real API, ensure the container actually listens on the target port.

### Common Mistake

Creating a Service selector that does not match Pod labels.

---

## Exercise 4 — Create a Batch Job

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: batch-pipeline
spec:
  backoffLimit: 3
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: pipeline
          image: python:3.12-slim
          command: ["python", "-c"]
          args: ["print('batch pipeline completed')"]
```

Validate:

```bash
kubectl get jobs
kubectl get pods
kubectl logs job/batch-pipeline
```

---

## Exercise 5 — CronJob with Forbid

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: scheduled-pipeline
spec:
  schedule: "*/5 * * * *"
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: Never
          containers:
            - name: pipeline
              image: python:3.12-slim
              command: ["python", "-c"]
              args: ["import time; time.sleep(120); print('done')"]
```

### Validation

```bash
kubectl get cronjob
kubectl get jobs
```

### Reasoning

The schedule may occur before the previous run finishes. `Forbid` prevents overlapping executions.

---

## Exercise 6 — Add ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: pipeline-config
data:
  ENVIRONMENT: "dev"
  PIPELINE_MODE: "incremental"
```

Use:

```yaml
envFrom:
  - configMapRef:
      name: pipeline-config
```

---

## Exercise 7 — Add Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: pipeline-secret
type: Opaque
stringData:
  API_TOKEN: "development-only"
```

Consume:

```yaml
env:
  - name: API_TOKEN
    valueFrom:
      secretKeyRef:
        name: pipeline-secret
        key: API_TOKEN
```

Do not commit real secrets.

---

## Exercise 8 — Add Resources

```yaml
resources:
  requests:
    cpu: "250m"
    memory: "256Mi"
  limits:
    cpu: "1"
    memory: "1Gi"
```

### Validation

Where metrics are available:

```bash
kubectl top pod
```

Compare actual usage with requests and limits.

---

## Exercise 9 — Create a ServiceAccount

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: pipeline
```

---

## Exercise 10 — Attach ServiceAccount

```yaml
spec:
  serviceAccountName: pipeline
```

Validate:

```bash
kubectl get pod <pod> -o yaml
```

Confirm the workload references the intended identity.

---

## Exercise 11 — Taints and Tolerations

Imagine a node is tainted:

```text
workload=spark:NoSchedule
```

A Spark Pod may use:

```yaml
tolerations:
  - key: workload
    operator: Equal
    value: spark
    effect: NoSchedule
```

### Troubleshooting

Remember:

> Toleration permits; it does not force placement.

---

## Exercise 12 — Affinity

```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
        - matchExpressions:
            - key: workload
              operator: In
              values:
                - spark
```

Validate that eligible nodes have the expected label.

---

## Exercise 13 — HPA

Create an HPA for a Deployment:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: consumer
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: consumer
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

### Common Mistake

Assuming HPA can function correctly without the required metrics infrastructure.

---

## Exercise 14 — Install Airflow with Helm

### Objective

Understand Helm-based installation rather than memorizing a single command.

### Tasks

1. Choose a compatible Airflow chart version.
2. Add the chart repository according to current official documentation.
3. Inspect chart values.
4. Render manifests with `helm template`.
5. Install into a dedicated namespace.
6. Inspect Pods and Services.
7. Inspect Helm release state.

Useful commands:

```bash
helm list -n airflow
kubectl get pods -n airflow
kubectl get svc -n airflow
```

### Troubleshooting

If a Pod is Pending:

```bash
kubectl describe pod <pod> -n airflow
```

If it crashes:

```bash
kubectl logs <pod> -n airflow
```

---

## Exercise 15 — Spark on Kubernetes

### Objective

Run a Spark application using Kubernetes as the compute scheduler.

### Architecture

```text
Spark application
      ↓
Driver Pod
      ↓
Executor Pods
      ↓
Object Storage
```

### Tasks

1. Verify Kubernetes context.
2. Make the Spark image available to the cluster.
3. Submit a small Spark application.
4. Observe the driver.
5. Observe executor Pods.
6. Inspect resource requests.
7. Inspect application logs.
8. Clean up the workload.

### Troubleshooting

If executor Pods remain Pending, inspect:

```bash
kubectl describe pod <executor-pod>
kubectl get nodes
kubectl get events --sort-by=.lastTimestamp
```

---

# 67. Knowledge Checkpoints

## Checkpoint 1 — Fundamentals

Before continuing, I should be able to:

- [ ] Explain why Kubernetes exists.
- [ ] Explain cluster vs node.
- [ ] Explain control plane at a high level.
- [ ] Explain desired vs actual state.
- [ ] Explain reconciliation.

## Checkpoint 2 — Workloads

- [ ] Explain Pods.
- [ ] Explain Deployments.
- [ ] Choose Deployment vs Job.
- [ ] Explain Services.
- [ ] Explain Namespaces.

## Checkpoint 3 — Batch

- [ ] Create a Job.
- [ ] Explain `backoffLimit`.
- [ ] Explain `activeDeadlineSeconds`.
- [ ] Explain completions and parallelism.
- [ ] Create a CronJob.
- [ ] Explain `concurrencyPolicy`.

## Checkpoint 4 — Configuration and Security

- [ ] Explain ConfigMap.
- [ ] Explain Secret.
- [ ] Explain why Base64 is not encryption.
- [ ] Explain ServiceAccounts.
- [ ] Explain workload identity.

## Checkpoint 5 — Resources

- [ ] Explain requests.
- [ ] Explain limits.
- [ ] Explain CPU throttling.
- [ ] Diagnose OOMKilled.
- [ ] Size a data workload using measurements.

## Checkpoint 6 — Platform Integration

- [ ] Explain Helm.
- [ ] Explain Operators.
- [ ] Explain Spark on Kubernetes.
- [ ] Explain Airflow Kubernetes execution.
- [ ] Explain Kafka/Flink operator awareness.

## Checkpoint 7 — Advanced Operations

- [ ] Explain HPA.
- [ ] Explain node autoscaling.
- [ ] Explain event-driven scaling.
- [ ] Explain consumer-lag scaling.
- [ ] Explain node pools.
- [ ] Explain taints/tolerations.
- [ ] Explain affinity.
- [ ] Explain PV/PVC.
- [ ] Explain object-storage-first architecture.
- [ ] Explain GitOps.

## Checkpoint 8 — Production Reasoning

- [ ] Diagnose Pending Pods.
- [ ] Diagnose CrashLoopBackOff.
- [ ] Diagnose ImagePullBackOff.
- [ ] Diagnose OOMKilled.
- [ ] Diagnose service connectivity.
- [ ] Diagnose identity problems.
- [ ] Decide when Kubernetes is unnecessary.

---

# 68. Final Practical Assessment

# Project — Run a Data Pipeline on Kubernetes

## Scenario

A Python data pipeline currently runs in Docker Compose.

The engineering team wants scheduled workloads to run on Kubernetes.

Build the following conceptual environment:

```text
Local Kubernetes Cluster
        |
        +-- Namespace
        |
        +-- Python Pipeline Job
        |
        +-- CronJob
        |
        +-- ConfigMap
        |
        +-- Secret
        |
        +-- ServiceAccount
        |
        +-- Resource requests/limits
        |
        +-- Airflow via Helm
        |
        +-- Spark job
```

## Requirements

The final implementation must demonstrate:

- correct workload primitives;
- resource sizing;
- retry configuration;
- active deadline;
- CronJob overlap protection;
- configuration separation;
- secret handling;
- ServiceAccount;
- workload identity explanation;
- debugging;
- scheduling;
- storage architecture;
- object-storage-first design.

## Required Failure Simulations

Intentionally create:

1. `OOMKilled`;
2. Pending Pod;
3. CrashLoopBackOff;
4. ImagePullBackOff;
5. CronJob overlap.

Then diagnose and recover each.

## Assessment Rubric

| Area | Evidence of Mastery |
|---|---|
| Architecture | Can explain why each Kubernetes primitive is used |
| Workload selection | Correctly chooses Job/CronJob/Deployment |
| Batch reliability | Correct retry/deadline/concurrency reasoning |
| Security | Uses identity and avoids hard-coded credentials |
| Resources | Uses measurement-driven requests/limits |
| Scheduling | Can reason about node pools and placement |
| Storage | Uses object-storage-first design |
| Debugging | Finds root causes systematically |
| Platform integration | Understands Airflow/Spark/operator relationships |
| Architecture judgment | Knows when Kubernetes is unnecessary |

---

# 69. Production Design Scenario

## Problem

Design a Kubernetes-based data platform for a company processing both batch and streaming workloads.

Requirements:

- Airflow;
- Spark;
- Kafka;
- Flink awareness;
- object storage;
- workload identity;
- separate workload classes;
- resource management;
- autoscaling;
- scheduling;
- failure recovery;
- security;
- cost awareness.

## Required Reasoning Chain

For each workload, reason through:

```text
Workload
   ↓
Container
   ↓
Pod
   ↓
Resource requirements
   ↓
Scheduling
   ↓
Identity
   ↓
Storage
   ↓
Scaling
   ↓
Failure recovery
   ↓
Observability
```

## Reference Architecture

```text
                         Git
                          |
                       GitOps
                          |
                   Kubernetes Cluster
                          |
       +------------------+------------------+
       |                  |                  |
    Airflow             Spark            Streaming
       |                  |                  |
    Task Pods          Driver/Exec       Kafka/Flink
       |                  |                  |
       +------------------+------------------+
                          |
                    Object Storage
                  S3 / GCS / ADLS
                          |
                     Lakehouse
```

## Reference Design Reasoning

### Airflow

Use Kubernetes-aware task execution when task isolation and heterogeneous resources are valuable.

### Spark

Use dedicated resource classes/node pools when Spark workloads materially compete with other services.

### Streaming

Use long-running Deployments or operator-managed workloads and scale using signals appropriate to streaming behavior.

### Identity

Use ServiceAccounts and cloud workload identity rather than long-lived cloud credentials.

### Storage

Use object storage for durable datasets and lakehouse data.

### Scheduling

Separate heavy workloads using node pools, labels, taints/tolerations, and affinity where justified.

### Scaling

Use:

- HPA for appropriate stateless workloads;
- node autoscaling for cluster capacity;
- event-driven scaling for workload signals;
- consumer lag for streaming when appropriate.

### Failure Recovery

Use:

- Job retries;
- deadlines;
- application idempotency;
- Pod replacement;
- resilient storage;
- appropriate workload scheduling.

### Cost

Use:

- workload sizing;
- autoscaling;
- spot capacity for interruption-tolerant batch workloads;
- object storage;
- avoiding unnecessary always-on compute.

---

# 70. Kubernetes vs Simpler Alternatives

Kubernetes is powerful, but power has an operational cost.

Consider Kubernetes when you have meaningful requirements around:

- multiple workload classes;
- multi-node scheduling;
- workload isolation;
- autoscaling;
- heterogeneous resources;
- custom operators;
- workload identity;
- platform standardization;
- complex compute orchestration.

Kubernetes may be unnecessary when:

- the team is small;
- workloads are simple;
- a managed Spark service is available;
- a managed Kafka service is available;
- serverless processing meets requirements;
- there are only a few workloads;
- Kubernetes operational complexity outweighs its benefits.

The key architectural principle is:

> **Technical possibility ≠ technical necessity.**

A Senior Data Engineer should choose the simplest platform that satisfies the requirements.

---

# 71. When to Prefer Managed Services

Instead of:

```text
Self-managed Kafka on Kubernetes
```

you may choose:

```text
Managed Kafka
```

Instead of:

```text
Spark cluster on Kubernetes
```

you may choose:

```text
Managed Spark
```

Instead of:

```text
Self-managed Airflow
```

you may choose:

```text
Managed orchestration
```

The decision depends on:

- operational expertise;
- workload requirements;
- compliance;
- cost;
- customization;
- vendor constraints;
- availability requirements.

Kubernetes is an architectural option, not a requirement for being a serious Data Engineer.

---

# 72. Senior Data Engineer Interview Questions

## 1. Why Kubernetes for Data Engineering?

A strong answer:

Kubernetes provides a common orchestration layer for heterogeneous data workloads, including batch Jobs, long-running consumers, Airflow task Pods, Spark workloads, and supporting services. Its value comes from scheduling, reconciliation, resource management, scaling, identity integration, and workload isolation.

## 2. Docker vs Kubernetes?

Docker packages and runs containers. Kubernetes orchestrates containerized workloads across a cluster and manages desired state, scheduling, replacement, service discovery, and scaling.

## 3. Pod vs Container?

A container is an application process packaged with its dependencies. A Pod is Kubernetes' scheduling unit and can contain one or more containers sharing network and storage context.

## 4. Deployment vs Job?

Deployment is for long-running desired state. Job is for completion-oriented batch processing.

## 5. Job vs CronJob?

Job executes batch work. CronJob creates Jobs on a schedule.

## 6. What is backoffLimit?

It limits how many Job failures Kubernetes tolerates before considering the Job failed.

## 7. What is activeDeadlineSeconds?

It establishes a maximum active runtime boundary for a Job, helping prevent runaway workloads.

## 8. What is concurrencyPolicy?

It determines how a CronJob behaves when a new schedule occurs while a previous Job is still active.

## 9. Why use Forbid?

When overlapping runs are undesirable because they could conflict or process the same logical data simultaneously.

## 10. ConfigMap vs Secret?

ConfigMap stores non-secret configuration. Secret is intended for sensitive values, but its default Base64 representation is not encryption.

## 11. Why is Base64 not encryption?

Base64 is an encoding. Anyone with the encoded value can decode it.

## 12. Requests vs Limits?

Requests influence scheduling. Limits define resource boundaries.

## 13. Why OOMKilled?

A container can be terminated after exceeding its effective memory boundary. The root cause may be application memory behavior, incorrect sizing, or unusual input.

## 14. What is CPU throttling?

When a container reaches its CPU limit, its CPU consumption can be throttled, slowing execution without necessarily crashing the process.

## 15. Why use a ServiceAccount?

To provide workload identity and avoid using human credentials.

## 16. What is workload identity?

A mechanism for mapping workload identity to cloud permissions without embedding long-lived cloud credentials in the workload.

## 17. Why avoid cloud keys in Pods?

They create credential leakage and rotation risks and often grant more access than necessary.

## 18. What is Helm?

A Kubernetes package/deployment mechanism based on charts, templates, values, and releases.

## 19. What is an Operator?

A controller that embeds domain-specific operational knowledge and reconciles custom resources.

## 20. Why use a Spark Operator?

To manage Spark applications declaratively through Kubernetes resources and operator reconciliation.

## 21. How does Spark run on Kubernetes?

A driver runs in a Pod and creates/coordinates executor Pods that perform distributed computation.

## 22. What is Airflow Kubernetes Executor?

An Airflow execution model where tasks can execute in separate Kubernetes Pods.

## 23. What is KubernetesPodOperator?

An Airflow operator that launches a Kubernetes Pod for a task.

## 24. What is HPA?

Horizontal Pod Autoscaler changes the number of Pod replicas based on configured metrics.

## 25. Why isn't CPU always enough for Kafka scaling?

Consumer lag can represent backlog directly, while CPU may remain moderate even as unprocessed messages accumulate.

## 26. What are node pools?

Groups of nodes designed for particular workload classes or resource characteristics.

## 27. What are taints and tolerations?

Taints restrict which workloads can schedule onto nodes; tolerations allow matching workloads to be considered for those nodes.

## 28. What is affinity?

Scheduling preference or requirement based on node or Pod relationships.

## 29. Why prefer object storage for durable datasets?

It separates durable data from compute, scales independently, and fits lakehouse/data-platform architectures better than treating worker-attached persistent storage as the data lake.

## 30. What is GitOps?

A deployment model where Git represents desired state and a controller such as Argo CD or Flux reconciles Kubernetes with that state.

## 31. How do you debug a Pending Pod?

Inspect `kubectl describe`, events, resource requests, available nodes, taints, tolerations, affinity, selectors, and storage constraints.

## 32. How do you debug CrashLoopBackOff?

Inspect current and previous logs, Pod events, configuration, environment variables, secrets, commands, and dependency connectivity.

## 33. How do you debug ImagePullBackOff?

Inspect Pod events and verify image name, tag, registry, authentication, architecture, and availability.

## 34. When should you not use Kubernetes?

When the workload is simple enough for a managed or serverless service, the team cannot justify the operational complexity, or Kubernetes provides little incremental value.

---

# 73. Production Checklist

Before calling a Kubernetes data workload production-ready, ask:

## Workload

- [ ] Is the correct primitive used?
- [ ] Is the image deterministic?
- [ ] Is the workload idempotent where retries are possible?

## Resources

- [ ] Are requests defined?
- [ ] Are limits justified?
- [ ] Has peak memory been measured?
- [ ] Has CPU behavior been measured?

## Reliability

- [ ] Are retries configured appropriately?
- [ ] Is there a deadline?
- [ ] Can duplicate processing occur?
- [ ] Is CronJob overlap intentional?

## Security

- [ ] Is a dedicated ServiceAccount used?
- [ ] Are permissions least-privilege?
- [ ] Are long-lived cloud keys avoided?
- [ ] Are secrets handled appropriately?

## Scheduling

- [ ] Is workload placement intentional?
- [ ] Are node pools justified?
- [ ] Are taints/tolerations used correctly?
- [ ] Is affinity necessary?

## Storage

- [ ] Is durable data outside ephemeral Pods?
- [ ] Is object storage preferred for lake data?
- [ ] Are PVCs used only where appropriate?

## Operations

- [ ] Can the team inspect logs?
- [ ] Can the team inspect events?
- [ ] Can the team diagnose Pending?
- [ ] Can the team diagnose OOMKilled?
- [ ] Can the team diagnose CrashLoopBackOff?
- [ ] Can the team diagnose ImagePullBackOff?

## Architecture

- [ ] Is Kubernetes actually necessary?
- [ ] Would a managed service reduce operational burden?
- [ ] Is the platform complexity justified by requirements?

---

# 74. Final Mastery Checklist

You have mastered this topic when you can independently:

### Fundamentals

- [ ] Explain why Kubernetes exists.
- [ ] Explain cluster, node, control plane, and worker node.
- [ ] Explain desired and actual state.
- [ ] Explain reconciliation.
- [ ] Explain Pods.
- [ ] Explain Deployments.
- [ ] Explain Services.
- [ ] Explain Namespaces.

### CLI

- [ ] Use `kubectl apply`.
- [ ] Use `kubectl get`.
- [ ] Use `kubectl describe`.
- [ ] Use `kubectl logs`.
- [ ] Use `kubectl exec`.
- [ ] Use `kubectl delete`.
- [ ] Inspect events.

### Local Kubernetes

- [ ] Create a cluster with kind, k3d, or minikube.
- [ ] Inspect kubeconfig/context.
- [ ] Deploy a workload.

### Batch

- [ ] Create Jobs.
- [ ] Explain completion.
- [ ] Explain parallelism.
- [ ] Configure `backoffLimit`.
- [ ] Configure `activeDeadlineSeconds`.
- [ ] Create CronJobs.
- [ ] Use `concurrencyPolicy`.

### Configuration/Security

- [ ] Use ConfigMaps.
- [ ] Use Secrets.
- [ ] Explain Base64 limitations.
- [ ] Use ServiceAccounts.
- [ ] Explain workload identity.

### Resources

- [ ] Configure requests.
- [ ] Configure limits.
- [ ] Explain CPU throttling.
- [ ] Diagnose OOMKilled.
- [ ] Perform measurement-driven sizing.

### Platform Integration

- [ ] Explain Helm.
- [ ] Understand Airflow Helm deployment.
- [ ] Explain Operators.
- [ ] Explain Spark on Kubernetes.
- [ ] Explain Spark Operator awareness.
- [ ] Explain Kafka Operator awareness.
- [ ] Explain Flink Operator awareness.
- [ ] Explain Airflow Kubernetes Executor.
- [ ] Explain KubernetesPodOperator.

### Scaling and Scheduling

- [ ] Explain HPA.
- [ ] Explain node autoscaling.
- [ ] Explain event-driven scaling.
- [ ] Explain Kafka lag scaling.
- [ ] Explain spot node pools.
- [ ] Explain node pools.
- [ ] Explain taints.
- [ ] Explain tolerations.
- [ ] Explain affinity.

### Storage and Delivery

- [ ] Explain PV/PVC.
- [ ] Explain object-storage-first architecture.
- [ ] Explain GitOps.
- [ ] Recognize Argo CD and Flux.

### Debugging

- [ ] Diagnose Pending Pods.
- [ ] Diagnose CrashLoopBackOff.
- [ ] Diagnose ImagePullBackOff.
- [ ] Diagnose OOMKilled.
- [ ] Diagnose Job failures.
- [ ] Diagnose CronJob overlap.
- [ ] Diagnose Service connectivity.
- [ ] Diagnose identity/permission problems.

### Architecture

- [ ] Design a Kubernetes data platform.
- [ ] Explain workload classes.
- [ ] Explain resource sizing.
- [ ] Explain scheduling.
- [ ] Explain scaling.
- [ ] Explain identity.
- [ ] Explain durable storage.
- [ ] Explain failure recovery.
- [ ] Explain cost trade-offs.
- [ ] Decide when Kubernetes is unnecessary.

---

# 75. Final Mental Model

If you remember only one architecture, remember this:

```text
                    Kubernetes
                         |
       +-----------------+-----------------+
       |                 |                 |
    Airflow            Spark           Streaming
       |                 |                 |
    Task Pods        Driver/Exec      Kafka/Flink
       |                 |                 |
       +-----------------+-----------------+
                         |
                   Object Storage
                         |
                    Lakehouse
```

And reason about every workload through:

```text
Workload
   ↓
Container Image
   ↓
Pod
   ↓
Resource Requirements
   ↓
Scheduling
   ↓
Identity
   ↓
Storage
   ↓
Scaling
   ↓
Failure Recovery
   ↓
Observability
```

The central Data Engineering principle is:

> **Kubernetes manages compute and workload orchestration; your data architecture must still provide correctness, idempotency, durable storage, security, observability, and sensible operational boundaries.**

And the senior-level architectural principle is:

> **Use Kubernetes when its orchestration capabilities solve a real problem—not simply because the workload can run on Kubernetes.**

---

# 76. What Comes Next in Module 2.18

This topic establishes Kubernetes workload concepts.

The next topics build the surrounding production platform:

```text
03 Kubernetes concepts
        ↓
04 Terraform basics
        ↓
05 CI pipelines
        ↓
06 Environment promotion
        ↓
07 Cloud secrets managers
```

Keep the boundaries clear:

- Kubernetes teaches workload orchestration.
- Terraform teaches infrastructure as code.
- CI teaches automated validation/build workflows.
- Environment promotion teaches dev/staging/prod delivery.
- Cloud secrets managers teach dedicated secret-management systems.

The result should be a coherent production platform rather than five disconnected technologies.

---

# 77. Final Assessment Questions

Before moving forward, answer these without looking at the module:

1. Why is Kubernetes useful for data workloads?
2. What is the difference between a cluster and a node?
3. What is a Pod?
4. Why is a Deployment different from a Job?
5. Why is a CronJob different from a Job?
6. What does `backoffLimit` control?
7. Why might retrying a failed ETL job duplicate data?
8. What does `activeDeadlineSeconds` protect against?
9. What does `concurrencyPolicy: Forbid` prevent?
10. Why use a Service?
11. Why should a workload not use another Pod's IP directly?
12. What is a Namespace?
13. What does `kubectl describe` tell you that `kubectl get` may not?
14. Why are ConfigMaps not suitable for passwords?
15. Why is Base64 not encryption?
16. What is the difference between CPU/memory requests and limits?
17. Why does `OOMKilled` happen?
18. What is CPU throttling?
19. Why should workloads have dedicated ServiceAccounts?
20. What is workload identity?
21. Why is workload identity better than embedding cloud keys?
22. What is Helm?
23. What is a Kubernetes Operator?
24. How does Spark map onto Kubernetes?
25. How can Airflow launch task Pods?
26. Why might Kafka consumer lag be a better scaling signal than CPU?
27. What is the difference between HPA and node autoscaling?
28. Why might Spark use a dedicated node pool?
29. What is a taint?
30. What is a toleration?
31. What is node affinity?
32. What is a PVC?
33. Why should durable lake data generally live in object storage?
34. What is GitOps?
35. How do you diagnose a Pending Pod?
36. How do you diagnose CrashLoopBackOff?
37. How do you diagnose ImagePullBackOff?
38. How do you investigate OOMKilled?
39. Why is Kubernetes not automatically the best solution for every data platform?
40. What is the simplest platform that satisfies your requirements?

If you can answer these and complete the practical assessment, you have moved from "I have seen Kubernetes" to:

> **"I can reason about Kubernetes as a Data Engineer."**

---

# 78. Module Completion Standard

Do not mark this module complete merely because you read the YAML.

Mark it complete when you have actually:

- created a local cluster;
- deployed a Pod;
- deployed a Deployment;
- exposed a workload with a Service;
- created a Namespace;
- created a Job;
- configured Job retries;
- configured a deadline;
- created a CronJob;
- tested `concurrencyPolicy`;
- created a ConfigMap;
- created a Secret using development-only values;
- configured resource requests/limits;
- observed actual resource behavior;
- diagnosed an OOMKilled workload;
- created a ServiceAccount;
- explained workload identity;
- rendered a Helm chart;
- deployed a data platform component with Helm;
- observed Spark driver/executor Pods;
- explained Airflow Kubernetes execution;
- explained operator-managed data workloads;
- reasoned about HPA and node scaling;
- used scheduling constraints;
- inspected a PVC;
- designed an object-storage-first architecture;
- explained GitOps;
- diagnosed Pending, CrashLoopBackOff, and ImagePullBackOff;
- completed the final production architecture exercise;
- justified when Kubernetes should not be used.

That is the difference between memorizing Kubernetes terminology and gaining production-oriented Data Engineering competence.
