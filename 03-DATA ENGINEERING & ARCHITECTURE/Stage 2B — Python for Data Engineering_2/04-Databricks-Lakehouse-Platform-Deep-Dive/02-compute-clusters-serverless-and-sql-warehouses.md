# Compute, Clusters, Serverless and SQL Warehouses

> **Module:** G4 — Databricks Lakehouse Platform Deep Dive  
> **Topic:** 02 — Compute, Clusters, Serverless and SQL Warehouses  
> **Phase:** A — Platform Foundations  
> **Prerequisite:** Topic 01 — Databricks Architecture, Workspaces and Planes  
> **Level:** Beginner → Production Data Engineer → Senior platform reasoning

> **Scope boundary:** This module teaches Databricks compute architecture, classic clusters, serverless compute, SQL warehouses, lifecycle, sizing, scaling, access modes, security, networking, performance, cost, troubleshooting, and production selection. It does not reteach Apache Spark internals, Delta internals, Structured Streaming, or detailed Lakeflow orchestration.

---

## 1. What You Will Learn

By the end of this topic, you should be able to:

1. Explain Databricks compute and how it differs from the workspace and persistent storage.
2. Explain clusters, drivers, workers, runtimes, node types, and lifecycle.
3. Distinguish interactive development compute from production job compute.
4. Explain auto-termination and autoscaling.
5. Select compute based on CPU, memory, storage, network, workload, and SLA requirements.
6. Explain access modes as both security and execution-model decisions.
7. Explain shared versus isolated compute.
8. Explain classic and serverless compute and their trade-offs.
9. Explain SQL warehouses and serverless SQL warehouses.
10. Reason about SQL concurrency, latency, queueing, and cost.
11. Explain Photon at a practical architectural level.
12. Connect compute choices to Unity Catalog and networking.
13. Design compute policies and cost guardrails.
14. Diagnose driver, worker, network, SQL, startup, and capacity failures.
15. Benchmark compute scientifically rather than blindly increasing capacity.
16. Design development, staging, and production compute strategies.
17. Defend compute decisions in a senior Data Engineering interview.

### Core question

> **What workload am I running, who is running it, what execution model does it need, what security/network constraints exist, what performance and concurrency are required, and what is the cheapest reliable compute model that satisfies those requirements?**

---

## 2. Why Compute Is a Platform Engineering Concern

A beginner often thinks:

```text
Open Databricks
    ↓
Create cluster
    ↓
Run notebook
```

Production engineering requires:

```text
Workload
   ↓
Execution model
   ↓
Compute type
   ↓
Access mode
   ↓
Sizing
   ↓
Scaling
   ↓
Lifecycle
   ↓
Identity / security
   ↓
Networking
   ↓
Performance
   ↓
Cost
   ↓
Observability
```

Poor compute decisions can cause:

- excessive spend,
- slow jobs,
- startup delays,
- unstable workloads,
- insufficient concurrency,
- security failures,
- dependency conflicts,
- idle-resource waste,
- noisy neighbors,
- difficult incident response.

**Senior principle:** compute is an engineering decision, not a button.

---

## 3. Compute Mental Model

```text
Databricks Workspace
        |
        +----------------------+
        |                      |
   Interactive            Automated
   Development              Jobs
        |                      |
        +----------+-----------+
                   |
                Compute
                   |
       +-----------+-----------+
       |                       |
 Classic Compute          Serverless
       |                       |
       +-----------+-----------+
                   |
             Governed Data
                   |
        +----------+----------+
        |          |          |
       S3        ADLS        GCS
```

Compute is generally **ephemeral execution capacity**.

Persistent data belongs in appropriate storage systems.

```text
Compute = processing capacity
Storage = persistent data
```

This separation is fundamental to lakehouse architecture.

---

## 4. Compute Terminology

| Term | Meaning |
|---|---|
| Compute | Resources used to execute workloads |
| Cluster | A compute environment consisting of one or more nodes |
| Driver | Coordinates a Spark application |
| Worker | Executes distributed tasks |
| Runtime | Software environment used by compute |
| Node type | CPU/memory/storage/network characteristics of a machine |
| Autoscaling | Dynamically adjusting worker capacity |
| Auto-termination | Stopping idle compute |
| Access mode | Security/isolation model for compute |
| SQL warehouse | SQL-oriented compute service |
| Serverless | Managed compute abstraction |
| Photon | Databricks-native execution engine for supported workloads |
| Job compute | Compute intended for automated execution |
| Interactive compute | Compute intended for development and analysis |

Product labels and supported settings can evolve. Verify current Databricks documentation before production implementation.

---

## 5. Cluster Fundamentals

A cluster is a collection of compute resources used to execute workloads.

```text
Cluster
   |
   +-- Driver
   |
   +-- Worker 1
   +-- Worker 2
   +-- Worker 3
```

### Driver

The driver coordinates the Spark application.

Conceptually it:

- coordinates execution,
- creates/uses execution plans,
- schedules work,
- communicates with workers,
- maintains application-level state.

The driver is not simply “the biggest worker.”

### Workers

Workers execute distributed tasks.

```text
Driver
   |
   +---- Task ----> Worker 1
   +---- Task ----> Worker 2
   +---- Task ----> Worker 3
```

A workload can fail because of:

- driver pressure,
- worker capacity,
- data skew,
- memory pressure,
- shuffle pressure,
- network limits,
- runtime/dependency problems.

Detailed Spark execution internals belong to the Spark-focused roadmap modules.

---

## 6. Driver vs Worker Failure

### Driver failure

Typical symptoms:

- driver out-of-memory,
- driver process crash,
- notebook command failure,
- application termination.

Common causes:

- collecting too much data,
- large driver-side Python objects,
- excessive driver-side processing,
- very large application state,
- unsuitable driver capacity.

### Worker failure

Typical symptoms:

- worker/executor OOM,
- task retries,
- failed stages,
- worker loss.

Common causes:

- oversized partitions,
- skew,
- memory-intensive joins,
- aggregations,
- insufficient worker capacity.

### Senior diagnostic rule

Do not immediately increase the entire cluster.

First ask:

> **Which process is constrained, why is it constrained, and would additional capacity actually remove the bottleneck?**

---

## 7. Interactive Compute

Interactive compute is designed for human-driven work.

Typical uses:

- notebook development,
- debugging,
- exploration,
- profiling,
- ad-hoc analysis,
- experimentation.

### Advantages

- rapid feedback,
- convenient iteration,
- developer-friendly workflow.

### Risks

- idle resources,
- oversized user-created clusters,
- configuration drift,
- shared-resource contention,
- production work accidentally executed interactively.

### Guardrails

Development compute should generally have:

- auto-termination,
- approved node types,
- reasonable worker limits,
- cost tags,
- controlled access.

---

## 8. Job Compute

Job-oriented compute is designed around automated execution.

```text
Scheduler / Job
       |
       v
Job Compute
       |
       v
Workload
       |
       v
Release / Terminate
```

Benefits:

- controlled lifecycle,
- cleaner production isolation,
- clearer cost attribution,
- repeatability,
- reduced dependence on human sessions.

### Anti-pattern

```text
Production Job
      |
      v
Developer's Interactive Cluster
```

This creates:

- ownership risk,
- accidental termination,
- configuration drift,
- excessive permissions,
- idle cost,
- weak reproducibility.

**Production principle:** critical automation should have a controlled execution environment and machine identity.

---

## 9. Cluster Lifecycle

A simplified lifecycle is:

```text
Configured
   ↓
Starting
   ↓
Running
   ↓
Scaling
   ↓
Idle
   ↓
Terminated
```

### Startup

Provisioning and initialization can include:

- compute allocation,
- runtime initialization,
- dependency installation,
- network initialization,
- startup configuration.

Startup time matters for:

- short jobs,
- frequent jobs,
- interactive development,
- strict SLAs.

### Running

Compute is available for workload execution.

### Idle

Idle compute can still generate cost depending on the compute model.

### Terminated

Active compute capacity is released. Persistent data should remain in appropriate storage.

---

## 10. Auto-Termination

Auto-termination stops compute after an idle period.

```text
No activity
    |
    | idle timeout
    v
Terminate
```

### Too short

Can cause:

- repeated startup latency,
- poor developer experience,
- excessive initialization overhead.

### Too long

Can cause:

- idle spend,
- forgotten clusters,
- resource waste.

### Production rule

> Use the shortest practical idle timeout that does not materially damage the workload or developer workflow.

Development environments normally benefit from stronger idle controls than continuously scheduled production workloads.

---

## 11. Autoscaling

Autoscaling adjusts worker capacity as workload demand changes.

```text
Low demand  →  2 workers
High demand →  8 workers
Demand falls → 3 workers
```

### Benefits

- elasticity,
- better resource utilization,
- improved cost/performance for variable workloads.

### What autoscaling cannot fix

Autoscaling does not automatically fix:

- bad joins,
- data skew,
- excessive shuffles,
- serial processing,
- inefficient UDFs,
- driver bottlenecks,
- poor data layout,
- unnecessary scans.

If the workload is inefficient, autoscaling may simply make an inefficient workload more expensive.

### Min/max strategy

```text
Minimum = baseline capacity
Maximum = safety/performance ceiling
```

Choose limits using workload size, SLA, concurrency, and budget.

---

## 12. Node Types and Sizing

Node/instance characteristics influence:

- CPU,
- memory,
- local storage,
- network bandwidth,
- cost.

### CPU-oriented workloads

Useful when transformations are computationally intensive.

### Memory-oriented workloads

Useful when operations require substantial memory.

### Storage-oriented workloads

Useful when local storage characteristics matter.

### Do not choose the biggest machine by default

A larger machine can:

- cost much more,
- hide inefficient logic,
- reduce flexibility,
- increase failure impact.

Use measured evidence.

### Sizing loop

```text
Estimate
  ↓
Choose baseline
  ↓
Run representative workload
  ↓
Measure
  ↓
Identify bottleneck
  ↓
Adjust
  ↓
Benchmark again
```

Measure:

- runtime,
- CPU,
- memory,
- shuffle,
- I/O,
- worker utilization,
- startup,
- failures,
- cost.

---

## 13. Access Modes

Access mode is a production security and execution-model decision.

Before selecting it, ask:

1. Who can use the compute?
2. Which identities execute code?
3. Is compute shared?
4. Which data can be accessed?
5. What libraries/runtime behaviors are required?
6. What isolation is required?
7. Does the workload use Unity Catalog?
8. Is it interactive or automated?

### Key principle

> **Compute configuration is also a security configuration.**

Access mode should not be treated as merely a performance switch.

Exact access-mode names, capabilities, and restrictions are version-sensitive. Verify the current Databricks documentation for the selected runtime and workload.

---

## 14. Shared Compute

Shared compute can improve utilization when multiple users/workloads can safely coexist.

### Benefits

- better utilization,
- less duplicated infrastructure,
- convenient collaboration.

### Risks

- noisy neighbors,
- workload interference,
- dependency conflicts,
- permission complexity,
- larger blast radius.

Use shared compute only when the workload and security model support it.

---

## 15. Isolated Compute

Isolated compute can be appropriate when:

- workloads have different security requirements,
- dependencies conflict,
- production needs a separate execution boundary,
- regulated workloads require stronger isolation,
- resource contention is unacceptable.

Trade-off:

```text
More isolation
      ↓
More operational complexity
      ↓
Potentially lower utilization
```

Isolation should be justified by risk and workload requirements, not by habit.

---

## 16. Serverless Compute

Serverless moves more infrastructure management to Databricks.

The user focuses more on:

- workload,
- configuration,
- permissions,
- data,
- performance,
- cost.

Databricks handles more of the infrastructure lifecycle.

### Potential benefits

- less infrastructure administration,
- managed scaling,
- simpler developer experience,
- potentially faster startup in supported scenarios.

### Serverless does NOT mean

- no servers,
- no cost,
- no security,
- no networking,
- every workload is supported,
- every workload is cheaper.

Still evaluate:

- identity,
- governance,
- network connectivity,
- workload support,
- region availability,
- dependencies,
- performance,
- cost.

---

## 17. Classic vs Serverless

| Dimension | Classic Compute | Serverless Compute |
|---|---|---|
| Infrastructure management | More visible | More abstracted |
| Provisioning | More explicit | More managed |
| Networking | Important | Still important |
| Security | Platform + cloud configuration | Managed infrastructure + workload governance |
| Scaling | Configurable/managed by mode | More managed in supported services |
| Operational overhead | Higher | Lower in supported cases |
| Customization | Workload-dependent | Workload-dependent |
| Cost | Resource/service driven | Service-specific managed pricing |
| Best fit | Requirements needing specific infrastructure behavior | Workloads benefiting from managed compute |

### Selection rule

Use serverless when the current platform capabilities satisfy:

- workload requirements,
- network requirements,
- security requirements,
- dependency requirements,
- performance requirements,
- cost objectives.

Do not make “serverless everywhere” an architecture principle.

---

## 18. SQL Warehouses

A SQL warehouse is compute designed primarily for SQL analytics.

Typical uses:

- Databricks SQL,
- dashboards,
- BI tools,
- interactive analytics,
- SQL-centric workloads.

```text
Analyst / BI Tool
        |
        v
SQL Warehouse
        |
        v
Unity Catalog
        |
        v
Lakehouse Data
```

### SQL warehouse vs Spark-oriented compute

| Workload | Starting point |
|---|---|
| Python Spark ETL | Spark-oriented compute |
| Scala Spark ETL | Spark-oriented compute |
| Notebook development | Interactive compute |
| Automated Spark ETL | Job compute |
| BI dashboards | SQL warehouse |
| SQL analytics | SQL warehouse |
| High-concurrency SQL serving | SQL warehouse |
| Streaming | Streaming-capable compute |
| ML training | ML-oriented compute |

A workload containing SQL is not automatically a SQL-warehouse workload. Choose based on the execution model and serving requirements.

---

## 19. Serverless SQL Warehouses

Serverless SQL warehouses provide a more managed SQL execution model.

```text
BI / SQL
   |
Serverless SQL Warehouse
   |
Governed Data
```

Potential benefits:

- less infrastructure administration,
- managed scaling,
- simpler SQL serving,
- reduced cluster-management burden.

Evaluate:

- pricing,
- concurrency,
- latency,
- regional availability,
- feature support,
- networking,
- workload compatibility.

Exact behavior evolves; verify current product documentation.

---

## 20. SQL Warehouse Sizing and Concurrency

Do not size a warehouse only by total data volume.

Consider:

- concurrent users,
- query complexity,
- latency targets,
- dashboard frequency,
- peak demand,
- query queueing,
- caching,
- data layout,
- cost.

Example:

```text
5 analysts
```

and

```text
500 concurrent BI users
```

are fundamentally different serving problems even if they query the same tables.

### Two important dimensions

```text
Capacity
   = how much execution work can be handled

Concurrency
   = how many workloads need service at the same time
```

Benchmark both.

---

## 21. SQL Warehouse Performance

A slow dashboard can result from:

- inefficient SQL,
- excessive data scanned,
- poor table layout,
- insufficient capacity,
- high concurrency,
- queueing,
- poor workload isolation.

Use:

```text
Baseline
  ↓
Measure query latency
  ↓
Check concurrency
  ↓
Check queueing
  ↓
Inspect query behavior
  ↓
Change one variable
  ↓
Benchmark
```

Do not respond to every slow query by making the warehouse larger.

---

## 22. Photon

Photon is Databricks' native vectorized execution engine for supported workloads.

Conceptually:

```text
SQL / Supported DataFrame Workload
             |
             v
          Photon
             |
             v
      Optimized execution
```

Photon can improve performance for supported workloads without requiring the engineer to rewrite the entire application.

### Photon is not

- a universal replacement for Spark,
- a guarantee of faster execution for every workload,
- a substitute for good SQL,
- a substitute for correct data layout,
- a substitute for query-plan analysis.

### Senior principle

Benchmark representative workloads.

Do not make unsupported blanket claims such as “Photon always gives X% improvement.”

---

## 23. Compute and Unity Catalog

Compute and governance are connected:

```text
Identity
   |
   v
Compute
   |
   v
Unity Catalog
   |
   v
Governed Data
```

Before approving production compute, ask:

1. Which identity executes?
2. Which access mode is used?
3. Which catalog/schema/object is accessed?
4. What permissions are required?
5. Does the compute model support the governance requirements?
6. Are cloud-level permissions also required?

The detailed Unity Catalog architecture is Topic 04; this module establishes the compute relationship.

---

## 24. Compute and Networking

For a private database:

```text
Compute
   |
   +--> DNS
   |
   +--> Route
   |
   +--> Firewall / Security Group
   |
   +--> Private Connectivity
   |
   v
Database
```

For object storage:

```text
Compute
   |
   v
Cloud Network / Endpoint
   |
   v
S3 / ADLS / GCS
```

A compute selection that ignores network architecture can fail in production.

### Timeout vs authentication

A connection timeout often points toward:

- DNS,
- route,
- firewall,
- endpoint,
- network reachability.

A connection reaching the service and receiving an authentication rejection points toward:

- credentials,
- identity,
- authorization.

Treat these as different hypotheses.

---

## 25. Compute Policies

Compute policies provide guardrails around what users can create/configure.

Conceptually, policies can constrain:

- node types,
- worker counts,
- autoscaling,
- runtime choices,
- auto-termination,
- tags,
- approved configuration,
- access.

Without policy:

```text
Developer
   |
   +--> Huge cluster
   +--> No auto-termination
   +--> Missing tags
```

With policy:

```text
Developer
   |
   v
Approved Policy
   |
   +--> Allowed size
   +--> Allowed runtime
   +--> Idle timeout
   +--> Required tags
```

Policies convert organizational standards into enforceable platform controls.

---

## 26. Cost Model

A useful reasoning model is:

```text
Cost
≈
Resource/service rate
×
Usage
×
Scale
+
Associated cloud/platform charges
```

This is not a billing formula.

Major drivers include:

- cluster size,
- duration,
- autoscaling,
- SQL warehouse usage,
- serverless usage,
- idle time,
- workload frequency,
- concurrency,
- data transfer,
- storage.

### Common cost traps

```text
Idle cluster
Oversized cluster
Unbounded autoscaling
Always-on development compute
Overprovisioned SQL warehouse
Unoptimized queries
Missing cost ownership
```

---

## 27. Cost Controls

Use:

1. auto-termination,
2. compute policies,
3. approved node types,
4. rightsizing,
5. job compute,
6. serverless where economically appropriate,
7. SQL warehouse controls,
8. tags,
9. environment ownership,
10. usage monitoring,
11. budgets,
12. periodic rightsizing.

### Key principle

> **The cheapest compute is not the smallest compute; it is the compute that completes the required workload reliably at the lowest total cost.**

A tiny cluster that runs ten times longer may cost more than a properly sized cluster.

---

## 28. Performance Engineering

Use evidence:

```text
Baseline
   ↓
Measure
   ↓
Identify bottleneck
   ↓
Change one variable
   ↓
Measure again
```

Potential bottlenecks:

- CPU,
- memory,
- disk,
- network,
- shuffle,
- skew,
- driver,
- startup,
- concurrency,
- storage I/O.

### Bad workflow

```text
Job slow
   ↓
Double cluster size
```

### Better workflow

```text
Job slow
   ↓
Measure
   |
   +--> CPU?
   +--> Memory?
   +--> Shuffle?
   +--> Skew?
   +--> Driver?
   +--> Storage?
   +--> Concurrency?
   ↓
Targeted change
   ↓
Benchmark
```

---

## 29. Compute Selection Framework

### Step 1 — Workload type

Identify:

- interactive notebook,
- batch ETL,
- streaming,
- SQL analytics,
- BI serving,
- ML training,
- development/testing.

### Step 2 — Execution requirements

Ask:

- Python?
- SQL?
- Spark?
- special libraries?
- GPUs?
- long-running?
- high concurrency?

### Step 3 — Security

Ask:

- single user?
- shared users?
- regulated data?
- service principal?
- Unity Catalog?

### Step 4 — Networking

Ask:

- private database?
- private storage?
- external API?
- special network path?

### Step 5 — Performance

Ask:

- latency,
- throughput,
- concurrency,
- startup time,
- SLA.

### Step 6 — Cost

Ask:

- frequency,
- budget,
- idle behavior,
- peak demand,
- cost attribution.

### Step 7 — Select and benchmark

```text
Requirements
   ↓
Compute model
   ↓
Configuration
   ↓
Benchmark
   ↓
Production guardrails
```

---

## 30. Decision Matrix

| Workload | Starting Point | Primary Concern |
|---|---|---|
| Notebook development | Interactive compute | Productivity + idle cost |
| Automated batch Spark | Job compute | Reliability + lifecycle |
| SQL BI | SQL warehouse | Concurrency + latency |
| Dashboard | SQL warehouse | Interactive performance |
| Python Spark ETL | Job compute | Runtime + cost |
| Streaming | Streaming-capable compute | Stability + continuous operation |
| ML training | ML-capable compute | CPU/GPU + memory |
| Ad-hoc SQL | SQL warehouse | Startup/concurrency/cost |
| CI/CD | Deployment tooling + service identity | Security + reproducibility |

This is a starting point, not a universal rule.

---

## 31. Hands-On Labs

### Lab 1 — Cluster Anatomy

Draw:

```text
Driver
  |
  +-- Worker
  +-- Worker
  +-- Worker
```

Explain driver responsibility, worker responsibility, driver failure, and worker failure.

**Success criterion:** identify the likely constrained component before changing cluster size.

### Lab 2 — Interactive vs Job Compute

A developer runs a notebook manually and a production ETL runs hourly.

Select compute for each.

**Expected:** interactive compute for development; controlled job-oriented compute for production.

### Lab 3 — Autoscaling Benchmark

Compare a representative workload using:

```text
Min = 2
Max = 8
```

versus a fixed-size configuration.

Record runtime, worker count, CPU, memory, failures, and cost proxy.

### Lab 4 — Auto-Termination

Compare practical idle settings such as 10, 30, and 60 minutes.

Measure developer startup impact and idle-cost exposure.

### Lab 5 — SQL Warehouse Benchmark

Measure:

- query latency,
- concurrency,
- queueing,
- capacity,
- cost.

Compare at least two capacity configurations.

### Lab 6 — Classic vs Serverless

For one batch and one interactive workload, compare:

- startup,
- performance,
- capabilities,
- networking,
- permissions,
- cost,
- operational effort.

### Lab 7 — Compute Policy Design

Design policy requirements preventing:

- excessive development clusters,
- missing auto-termination,
- unapproved runtimes,
- missing cost tags.

### Lab 8 — Driver vs Worker Failure

Run controlled experiments for driver-side and worker-side memory pressure.

Record:

- symptom,
- evidence,
- root cause,
- corrective action,
- prevention.

---

## 32. Troubleshooting and Break/Fix

Use:

```text
Symptom
  ↓
Evidence
  ↓
Hypothesis
  ↓
Targeted test
  ↓
Root cause
  ↓
Fix
  ↓
Verification
  ↓
Prevention
```

### Incident 1 — Cluster takes too long to start

Investigate:

- compute model,
- provisioning,
- runtime initialization,
- libraries,
- configuration,
- startup behavior.

Do not immediately increase cluster size.

### Incident 2 — Driver out of memory

Investigate:

- collect/toPandas patterns,
- driver-side objects,
- query-plan size,
- driver-side Python processing.

Prefer removing unnecessary driver-side data movement before simply increasing capacity.

### Incident 3 — Workers out of memory

Investigate:

- partition sizes,
- skew,
- joins,
- aggregations,
- worker memory.

Fix workload behavior before blindly scaling.

### Incident 4 — Compute is expensive but underutilized

Investigate:

- idle time,
- auto-termination,
- node size,
- interactive clusters,
- job frequency.

Apply policy, lifecycle controls, and rightsizing.

### Incident 5 — More workers do not improve runtime

Investigate:

- skew,
- serial work,
- driver bottleneck,
- storage I/O,
- query plan,
- shuffle.

More workers do not guarantee linear scaling.

### Incident 6 — SQL dashboard is slow under load

Investigate:

- concurrency,
- warehouse capacity,
- query complexity,
- queueing,
- data layout,
- caching behavior.

### Incident 7 — Serverless cannot reach a dependency

Investigate:

- current serverless network model,
- supported private connectivity,
- DNS,
- firewall,
- identity,
- dependency availability,
- current platform capability.

### Incident 8 — Production job works interactively but fails as a job

Compare:

```text
Interactive User
vs
Production Service Principal
```

Check permissions, secrets, runtime, libraries, configuration, catalog/data access, and network.

---

## 33. Common Architecture Mistakes

1. Choosing the largest cluster by default.
2. Treating autoscaling as a substitute for optimization.
3. Leaving interactive clusters running.
4. Running production jobs on personal interactive compute.
5. Ignoring driver memory.
6. Ignoring worker memory.
7. Confusing driver and worker failures.
8. Sizing SQL warehouses only by data volume.
9. Ignoring concurrency.
10. Assuming serverless is always cheaper.
11. Assuming serverless has no networking requirements.
12. Ignoring access mode.
13. Ignoring Unity Catalog compatibility.
14. Allowing unrestricted cluster creation.
15. Failing to tag compute.
16. Treating performance tuning as “add workers.”
17. Measuring runtime but not cost.
18. Changing multiple benchmark variables simultaneously.
19. Benchmarking with unrealistic data.
20. Treating development and production compute identically.

---

## 34. Production Architecture Patterns

### Pattern A — Development

```text
Developer
   |
Workspace
   |
Interactive Compute
   |
Unity Catalog
   |
Development Data
```

Guardrails:

- auto-termination,
- approved node sizes,
- tags,
- limited production access.

### Pattern B — Production Batch

```text
Scheduler
   |
Job
   |
Service Principal
   |
Job Compute
   |
Unity Catalog
   |
Cloud Storage
```

### Pattern C — BI Analytics

```text
BI Tool
   |
SQL Warehouse
   |
Unity Catalog
   |
Lakehouse Data
```

### Pattern D — Hybrid Enterprise

```text
                    Databricks
                         |
          +--------------+--------------+
          |                             |
     Data Engineering              Analytics
          |                             |
     Job Compute                  SQL Warehouse
          |                             |
          +--------------+--------------+
                         |
                    Unity Catalog
                         |
                    Cloud Storage
```

Use specialized compute for materially different workload classes instead of forcing everything onto one compute type.

---

## 35. Architecture Decision Records

### ADR-001 — Interactive vs Job Compute

**Context:** development and production have different lifecycle and security requirements.

**Decision:** use interactive compute for development and controlled job compute for production automation where appropriate.

**Reasons:** lifecycle, isolation, cost attribution, reproducibility, machine identity.

**Trade-off:** more deployment/configuration work.

### ADR-002 — Classic vs Serverless

**Context:** workloads have different infrastructure and operational requirements.

**Decision:** choose per workload.

**Evaluate:** networking, security, capabilities, dependencies, performance, operations, cost.

### ADR-003 — Autoscaling

**Context:** workload demand varies.

**Decision:** use autoscaling where measured workload behavior benefits from dynamic capacity.

**Trade-off:** scaling cannot fix poor algorithms and may complicate cost prediction.

### ADR-004 — Compute Governance

**Context:** unrestricted compute creation can create security and cost problems.

**Decision:** enforce compute policies for approved capacity, runtime, lifecycle, tags, and access.

**Trade-off:** stronger controls reduce user flexibility.

---

## 36. Performance Benchmarking Framework

Never benchmark by runtime alone.

Record:

| Metric | Purpose |
|---|---|
| Runtime | User/business latency |
| Input size | Normalization |
| Output size | Work validation |
| CPU | CPU bottleneck |
| Memory | Memory bottleneck |
| Shuffle | Distributed movement |
| Worker count | Capacity |
| Startup | Lifecycle overhead |
| Concurrency | Serving behavior |
| Cost proxy | Economic efficiency |
| Failures/retries | Reliability |

### Benchmark protocol

1. Fix the dataset.
2. Fix the workload.
3. Change one variable.
4. Run multiple trials.
5. Record results.
6. Compare median and percentile behavior.
7. Compare cost.
8. Document the decision.

Bad:

```text
A: one run
B: one run
B faster → done
```

Better:

```text
Same workload
Same data

A: multiple trials
B: multiple trials

Compare:
runtime
variance
resource utilization
cost
failure rate
```

---

## 37. Cost Optimization Playbook

### Step 1 — Find idle resources

Identify:

- interactive clusters,
- long idle periods,
- unused warehouses.

### Step 2 — Find oversized resources

Compare:

```text
Allocated capacity
vs
Observed utilization
```

### Step 3 — Improve workload efficiency

Before scaling:

- reduce unnecessary scans,
- optimize joins,
- fix skew,
- improve partitioning,
- optimize SQL,
- improve table layout.

### Step 4 — Apply governance

Use:

- policies,
- tags,
- auto-termination,
- approved sizes,
- ownership.

### Step 5 — Measure unit economics

Useful measures include:

```text
Cost / job
Cost / successful pipeline run
Cost / TB processed
Cost / BI workload
```

---

## 38. Security Checklist

Before approving production compute:

- [ ] Who can create it?
- [ ] Who can use it?
- [ ] Which access mode is used?
- [ ] Which identity executes code?
- [ ] Is production automation using service principals?
- [ ] Which Unity Catalog data can it access?
- [ ] Is network access appropriate?
- [ ] Are secrets managed correctly?
- [ ] Are libraries/dependencies controlled?
- [ ] Are compute policies enforced?
- [ ] Are tags and ownership defined?
- [ ] Is auditability sufficient?
- [ ] Is the compute model appropriate for regulated data?

---

## 39. Reliability Checklist

- [ ] Production jobs do not depend on personal interactive clusters.
- [ ] Compute lifecycle is controlled.
- [ ] Failures are observable.
- [ ] Retry behavior is appropriate.
- [ ] Driver capacity is sufficient.
- [ ] Worker capacity is sufficient.
- [ ] Autoscaling has sensible limits where used.
- [ ] Network dependencies are documented.
- [ ] Runtime/dependency versions are controlled.
- [ ] Production configuration is reproducible.
- [ ] Cost guardrails exist.
- [ ] Workload identity is explicit.

---

## 40. Interview Preparation

### Q1. What is a Databricks cluster?

A compute environment used to execute workloads. In Spark workloads, a driver coordinates execution while workers execute distributed tasks.

**Follow-up:** What distinguishes driver and worker failures?

### Q2. Interactive vs job compute?

Interactive compute is optimized for human development; job compute is optimized for controlled automated execution.

### Q3. Why avoid a developer's cluster for production?

It introduces lifecycle, ownership, security, configuration-drift, and cost risks.

### Q4. What is autoscaling?

Dynamic adjustment of worker capacity based on demand. It improves elasticity but does not repair inefficient workload logic.

### Q5. Why might more workers not help?

The bottleneck could be skew, serial work, driver pressure, storage, shuffle, or query logic.

### Q6. What is a SQL warehouse?

SQL-oriented compute for analytics, BI, dashboards, and SQL-centric workloads.

### Q7. SQL warehouse vs Spark compute?

Use SQL warehouses for SQL-centric analytics/serving; use Spark-oriented compute for distributed programmatic processing.

### Q8. What is serverless?

A managed compute abstraction in which Databricks handles more infrastructure lifecycle. It does not eliminate servers, security, networking, or cost.

### Q9. How do you size a SQL warehouse?

Based on concurrency, latency, query complexity, workload volume, dashboard patterns, and cost.

### Q10. What is Photon?

A Databricks-native vectorized execution engine for supported workloads. Benchmark rather than assuming a universal speedup.

### Q11. What is a compute policy?

A governance mechanism that constrains compute configuration such as capacity, runtime, lifecycle, tags, and access.

### Q12. How do you control compute cost?

Use auto-termination, policies, rightsizing, job compute, appropriate serverless/SQL usage, tags, monitoring, and workload optimization.

### Q13. Driver OOM vs worker OOM?

Driver OOM generally indicates excessive driver-side state/data movement; worker OOM indicates distributed task/executor memory pressure.

### Q14. How do you choose classic vs serverless?

Evaluate workload, networking, security, supported capabilities, dependencies, performance, operational overhead, region, and cost.

---

## 41. Practice Questions

### Basic — 10

1. What is Databricks compute?
2. What is the role of the driver?
3. What is the role of workers?
4. What is interactive compute?
5. What is job compute?
6. What does auto-termination do?
7. What is autoscaling?
8. What is a SQL warehouse?
9. What is serverless compute?
10. What is Photon?

### Moderate — 10

11. Why should production jobs avoid a developer's interactive cluster?
12. Explain driver versus worker memory failures.
13. Why does adding workers not always improve performance?
14. How would you choose SQL warehouse size?
15. Why are compute policies important?
16. Explain compute and Unity Catalog as an architectural relationship.
17. Explain compute and networking as an architectural relationship.
18. Compare classic and serverless.
19. Explain why idle compute is a cost problem.
20. Design a development compute policy.

### Hard — 5

21. A Spark ETL job becomes much slower after a major data-volume increase. Design the investigation.
22. A SQL dashboard becomes slow under high concurrency. Diagnose the likely bottlenecks.
23. A production job succeeds interactively but fails under its service principal. Build the troubleshooting plan.
24. A company wants all workloads on serverless. Build the decision framework.
25. Design compute for an enterprise with interactive development, batch ETL, streaming, BI, and ML.

---

## 42. Final Capstone

### Scenario

Design compute for a production lakehouse with:

- 80 Data Engineers,
- 300 analysts,
- batch ETL,
- near-real-time pipelines,
- BI dashboards,
- ML workloads,
- PII,
- development/staging/production,
- strict cost controls.

### Your design must specify

1. Interactive compute strategy.
2. Job compute strategy.
3. Serverless strategy.
4. SQL warehouse strategy.
5. Access modes.
6. Compute policies.
7. Autoscaling.
8. Auto-termination.
9. Node sizing.
10. Service-principal execution.
11. Unity Catalog integration.
12. Network requirements.
13. Cost attribution.
14. Performance benchmarking.
15. Observability.

### Model architecture

```text
                         Databricks Account
                                |
             +------------------+------------------+
             |                  |                  |
            DEV               STAGING             PROD
             |                  |                  |
       Interactive          Validation         Controlled
         Compute              Compute           Compute
             |                  |                  |
             +------------------+------------------+
                                |
                         Unity Catalog
                                |
          +---------------------+---------------------+
          |                     |                     |
      Batch ETL             BI / SQL              ML
          |                     |                     |
     Job Compute          SQL Warehouse       ML Compute
          |                     |                     |
          +---------------------+---------------------+
                                |
                          Cloud Storage
```

### Model production policy

- Development compute is bounded by policy and auto-termination.
- Production ETL uses controlled job execution and service identities.
- BI uses SQL warehouses sized using measured concurrency.
- Serverless is used where current platform capabilities satisfy requirements.
- Streaming and ML receive specialized compute where necessary.
- Unity Catalog governs data access.
- Networking is designed around actual dependencies.
- Cost is measured by workload and environment.
- Performance changes are benchmarked.

This is a starting architecture, not a universal template.

---

## 43. Roadmap Coverage Audit

| Required Area | Covered? |
|---|---:|
| Compute fundamentals | Yes |
| Clusters | Yes |
| Driver/workers | Yes |
| Interactive compute | Yes |
| Job compute | Yes |
| Lifecycle | Yes |
| Auto-termination | Yes |
| Autoscaling | Yes |
| Node types | Yes |
| Compute sizing | Yes |
| Access modes | Yes |
| Shared/isolated compute | Yes |
| Serverless | Yes |
| Classic vs serverless | Yes |
| SQL warehouses | Yes |
| Serverless SQL | Yes |
| SQL concurrency | Yes |
| Photon | Yes |
| Unity Catalog relationship | Yes |
| Networking | Yes |
| Compute policies | Yes |
| Cost management | Yes |
| Performance engineering | Yes |
| Selection framework | Yes |
| Hands-on labs | Yes |
| Break/fix | Yes |
| Common mistakes | Yes |
| Production architectures | Yes |
| ADRs | Yes |
| Benchmarking | Yes |
| Security | Yes |
| Reliability | Yes |
| Interview preparation | Yes |
| Practice questions | Yes |
| Capstone | Yes |

**Audit conclusion:** Topic 02 is covered as a production-oriented compute engineering module rather than a UI-only walkthrough.

---

## 44. Completion Checklist

### Fundamentals

- [ ] Explain compute.
- [ ] Explain driver and worker roles.
- [ ] Distinguish interactive and job compute.
- [ ] Explain lifecycle.
- [ ] Explain auto-termination.
- [ ] Explain autoscaling.
- [ ] Explain node sizing.

### Serverless

- [ ] Explain serverless.
- [ ] Explain what serverless does not eliminate.
- [ ] Compare serverless and classic.
- [ ] Evaluate networking and security requirements.

### SQL

- [ ] Explain SQL warehouses.
- [ ] Distinguish SQL warehouse and Spark compute.
- [ ] Reason about concurrency.
- [ ] Size using workload evidence.
- [ ] Explain serverless SQL conceptually.

### Production

- [ ] Design compute policies.
- [ ] Control idle compute.
- [ ] Diagnose driver/worker failures.
- [ ] Diagnose slow jobs without blindly scaling.
- [ ] Measure cost.
- [ ] Benchmark compute.
- [ ] Design environment-specific compute.
- [ ] Defend compute choices in an interview.

---

## 45. Final Operating Standard

You are ready to progress when you can take an arbitrary production workload and reason through:

```text
Workload
   ↓
Execution model
   ↓
Interactive / Job / SQL / Serverless
   ↓
Access mode
   ↓
Identity
   ↓
Compute sizing
   ↓
Scaling
   ↓
Networking
   ↓
Governance
   ↓
Performance
   ↓
Cost
   ↓
Observability
   ↓
Production guardrails
```

### Senior principle

> **Choose the cheapest adequate compute model that satisfies the workload's security, networking, performance, reliability, concurrency, and operational requirements.**

Do not:

- choose compute by habit,
- choose only by machine size,
- treat serverless as magic,
- treat SQL warehouses as generic Spark clusters,
- treat autoscaling as optimization,
- treat larger clusters as a substitute for bottleneck analysis.

---

## Current-Documentation Safety Note

Databricks compute products, access modes, serverless capabilities, SQL warehouse behavior, Photon support, runtime versions, CLI syntax, Terraform provider resources, pricing, quotas, and cloud-specific networking evolve.

Before production implementation:

1. Verify current Databricks documentation for the target cloud and region.
2. Verify compute/access-mode capabilities.
3. Verify SQL warehouse/serverless behavior.
4. Verify pricing and usage metrics.
5. Verify Terraform provider resources and versions.
6. Benchmark representative workloads.
7. Do not infer production behavior from an outdated tutorial or UI screenshot.

**Stable architecture should be learned deeply; version-sensitive implementation details should be verified immediately before execution.**
