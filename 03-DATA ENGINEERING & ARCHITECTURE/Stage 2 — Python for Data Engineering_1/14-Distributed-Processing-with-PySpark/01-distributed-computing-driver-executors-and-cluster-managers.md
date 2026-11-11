# Distributed Computing: Driver, Executors, and Cluster Managers

> **Module:** Stage 2 — Python for Data Engineering  
> **Module 2.14:** Distributed Processing with PySpark  
> **Topic 01:** Distributed computing: driver, executors, and cluster managers  
> **Target:** Apache Spark 4.x / PySpark 4.x  
> **Level:** Beginner → Advanced Data Engineering  
>
> This topic establishes the architectural mental model required for every later PySpark topic. The goal is not to memorize Spark terminology. The goal is to understand how a PySpark application becomes distributed work, how that work is scheduled, how data is divided, how failures are recovered, and where Python, the JVM, executors, and cluster managers fit.

---

## 1. Learning Objectives

By the end of this topic, you should be able to:

- Explain why distributed computing exists and when a single machine is no longer the right execution boundary.
- Distinguish vertical scaling from horizontal scaling.
- Explain shared-nothing architecture and its trade-offs.
- Explain Spark's application architecture: **application, driver, worker node, executor, cluster manager, partition, task, job, and stage**.
- Explain the difference between a worker node and an executor.
- Explain why the driver coordinates work rather than processing every data row.
- Explain how partitions create distributed parallelism.
- Explain the relationship between executor cores, task slots, partitions, and task execution waves.
- Explain the execution hierarchy:

```text
Application
   ↓
Job
   ↓
Stage
   ↓
Task
   ↓
Partition
```

- Explain why shuffles conceptually create stage boundaries without prematurely diving into shuffle optimization.
- Explain data locality and why cloud object storage changes traditional locality assumptions.
- Explain Spark's lineage-based fault tolerance, task retries, executor failures, and recomputation.
- Explain speculative execution and stragglers.
- Explain the classic PySpark Python/JVM architecture, Py4J, Python workers, serialization, and Arrow at a conceptual level.
- Explain how Spark Connect changes the client/server architecture.
- Compare local mode, Spark Standalone, YARN, and Kubernetes at an architectural level.
- Explain when Spark is unnecessary and when single-node engines such as DuckDB or Polars may be more appropriate.
- Run and reason about a small `hello_cluster.py` application.
- Explain Spark architecture in an interview or production-design discussion without relying on memorized definitions.

---

## 2. Prerequisites

This topic assumes that you already understand basic:

- Python
- CPU cores and RAM
- disk and files
- processes
- networking
- operating-system fundamentals
- pandas/Polars/DuckDB concepts
- SQL
- Parquet and data formats
- batch data processing
- data pipelines

You do **not** need prior knowledge of Spark internals or distributed-systems terminology.

### Connections to earlier modules

| Earlier module | Connection to this topic |
|---|---|
| Module 2.4 — Arrow, Polars, DuckDB | Establishes the single-node baseline and the point at which distributed execution may become useful. |
| Module 2.5 — Data formats | Parquet/file layout influences how distributed systems read data. |
| Module 2.6 — SQL | Query execution concepts provide useful background for distributed execution. |
| Module 2.10 — Concurrency | Parallelism, CPU cores, task execution, and stragglers connect directly to Spark. |
| Module 2.12 — Transformation/Pipeline Design | Pure transformations and pipeline structure become useful patterns for Spark jobs. |

This topic does **not** re-teach those modules.

---

# Part I — Why Distributed Computing Exists

## 3. Why Distributed Computing Exists

A single computer is surprisingly powerful. Modern machines can have many CPU cores, large amounts of RAM, fast SSDs, and high network bandwidth.

But a single machine still has physical limits.

### 3.1 CPU limitations

Suppose a machine has:

```text
8 CPU cores
```

At a high level, only a limited number of CPU-intensive operations can execute simultaneously.

You can make the machine faster by adding cores, but eventually you reach:

- hardware limits
- diminishing returns
- memory bandwidth limits
- synchronization overhead
- cost constraints

### 3.2 RAM limitations

Suppose a dataset is:

```text
1 TB
```

and your machine has:

```text
64 GB RAM
```

The dataset cannot simply be loaded entirely into memory.

That does not mean the data cannot be processed. It means the system must process it in pieces, stream it, or use disk-backed techniques.

### 3.3 Disk limitations

Disk is much larger than RAM, but it is slower.

Large workloads may spend substantial time:

- reading files
- writing intermediate results
- sorting
- spilling intermediate data to disk

### 3.4 Network limitations

Distributed computing introduces another resource:

```text
Network bandwidth
```

If data must move between machines, the network becomes part of the execution cost.

This is one of the most important distributed-computing principles:

> **Distributed processing trades some local resource limitations for coordination and network complexity.**

### 3.5 Processing-time limitations

Even when a dataset fits on one machine, the computation may take too long.

For example:

```text
Dataset: 2 TB
Single machine processing time: 9 hours
Required processing window: 2 hours
```

Adding machines can allow independent portions of the workload to execute concurrently.

But the improvement is not automatically linear because distributed systems introduce:

- network communication
- scheduling
- serialization
- coordination
- startup overhead
- data movement
- skew
- failures and retries

---

## 4. Single-Machine vs Distributed Processing

### Single-machine model

```text
                One Machine
        ┌─────────────────────────┐
        │ CPU                     │
        │ RAM                     │
        │ Disk                    │
        │                         │
        │ Dataset + Computation   │
        └─────────────────────────┘
```

Everything is constrained by one machine's resources.

### Distributed model

```text
                 Cluster
      ┌──────────────────────────────┐
      │                              │
      │  Machine 1    Machine 2      │
      │  CPU/RAM      CPU/RAM        │
      │      │           │           │
      │      └─────┬─────┘           │
      │            Network            │
      │      ┌──────┴──────┐          │
      │  Machine 3    Machine 4      │
      │  CPU/RAM      CPU/RAM        │
      │                              │
      └──────────────────────────────┘
```

The workload is divided into pieces that can execute concurrently.

### Numerical example

Suppose:

```text
Dataset = 1 TB
Machine A = 8 CPU cores
```

Instead of asking one machine to perform every operation, a cluster could conceptually provide:

```text
Machine A = 8 cores
Machine B = 8 cores
Machine C = 8 cores
Machine D = 8 cores

Total = 32 cores
```

If the workload can be divided effectively, multiple portions can execute at the same time.

However:

```text
4 × machine count ≠ automatically 4 × performance
```

The workload may be limited by:

- serial portions
- network transfer
- disk throughput
- skew
- coordination
- insufficient parallelism
- excessive task overhead

---

# Part II — Scaling

## 5. Vertical vs Horizontal Scaling

### 5.1 Vertical scaling — scale up

Vertical scaling means making one machine more powerful.

```text
Before:

┌────────────────────┐
│ 8 CPU / 32 GB RAM  │
└────────────────────┘

After:

┌──────────────────────────┐
│ 32 CPU / 256 GB RAM      │
└──────────────────────────┘
```

You increase:

- CPU
- RAM
- disk capacity
- disk throughput

### Advantages

- simple architecture
- fewer machines
- less network coordination
- easier operational model

### Limitations

- hardware ceiling
- increasingly expensive machines
- a single machine remains a major failure boundary
- not every workload scales efficiently by adding resources to one host

---

### 5.2 Horizontal scaling — scale out

Horizontal scaling means adding machines.

```text
Before:

┌──────────────┐
│ One machine  │
└──────────────┘

After:

┌──────────────┐  ┌──────────────┐
│ Machine 1    │  │ Machine 2    │
└──────────────┘  └──────────────┘
        │                 │
        └───────┬─────────┘
                │
        ┌───────┴─────────┐
        │ Machine 3       │
        └─────────────────┘
```

The workload is distributed across machines.

### Comparison

| Dimension | Vertical scaling | Horizontal scaling |
|---|---|---|
| Strategy | Bigger machine | More machines |
| CPU | Add cores | Add hosts/cores |
| RAM | Add memory | Add memory across hosts |
| Network | Mostly local | Becomes critical |
| Complexity | Lower | Higher |
| Hardware ceiling | Strong | Higher aggregate capacity |
| Failure model | Large single-host boundary | Individual nodes can fail |
| Distributed coordination | Minimal | Required |

Spark is designed primarily around distributed, horizontally scalable execution.

---

## 6. Shared-Nothing Architecture

A shared-nothing system gives processing nodes independent resources.

Conceptually:

```text
                 Cluster
                    │
       ┌────────────┼────────────┐
       │            │            │
       ▼            ▼            ▼
   Machine 1    Machine 2    Machine 3
   CPU/RAM      CPU/RAM      CPU/RAM
   Disk         Disk         Disk
       │            │            │
       └─────── Network ─────────┘
```

Each machine owns its:

- CPU
- memory
- local resources
- local disk

Machines communicate over the network when coordination or data transfer is required.

### Why it scales

Adding machines adds aggregate:

- CPU capacity
- memory capacity
- storage capacity
- task execution capacity

### Why it is harder

The system now has to deal with:

- network latency
- network failures
- machine failures
- coordination
- data placement
- retries
- uneven workloads
- serialization

The fundamental trade-off is:

> **Scale and parallelism increase, but distributed-system complexity also increases.**

---

# Part III — MapReduce to Spark

## 7. MapReduce → Spark

MapReduce was an important model for large-scale data processing.

A simplified MapReduce workflow looks like:

```text
Input
  ↓
Map
  ↓
Intermediate data
  ↓
Reduce
  ↓
Output
```

The map phase processes records independently.

The reduce phase combines records by key.

A major characteristic of classic MapReduce was heavy reliance on disk between processing stages.

Spark emerged to provide a more flexible execution engine with:

- DAG-based execution
- optimized execution plans
- broader transformation composition
- memory-aware execution
- reusable distributed datasets
- SQL/DataFrame APIs

The important architectural transition is:

```text
MapReduce-style
fixed processing pattern

          ↓

Spark
general DAG execution engine
```

Spark can construct a directed acyclic graph (DAG) of computation and optimize/execute that graph as distributed stages and tasks.

The purpose here is not to study MapReduce history. It is to understand why Spark's execution model is structured around a general distributed DAG.

---

# Part IV — Spark Application Architecture

## 8. Spark Application Architecture

A Spark application consists conceptually of:

- an application
- a driver
- executors
- worker nodes
- a cluster manager
- partitions
- tasks
- jobs
- stages

A simplified architecture is:

```text
                       Spark Application
                              │
                              ▼
                         ┌─────────┐
                         │ Driver  │
                         └────┬────┘
                              │
                    requests resources
                              │
                              ▼
                     ┌────────────────┐
                     │ Cluster Manager│
                     └───────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
          Worker 1       Worker 2       Worker 3
              │              │              │
          Executor        Executor        Executor
              │              │              │
        ┌─────┼─────┐  ┌────┼─────┐  ┌────┼─────┐
        ▼     ▼     ▼  ▼    ▼      ▼  ▼    ▼     ▼
      Task  Task  Task Task Task  Task Task Task Task
        │     │     │    │   │      │   │    │     │
     Partition ...       Partitions       ...
```

The important distinction is:

```text
Driver      → coordinates
Executors   → execute distributed work
Workers     → provide machines/resources
Cluster mgr → allocates resources
Tasks       → perform work on partitions
Partitions  → divide data for parallel processing
```

---

## 9. End-to-End Application Flow

A simplified application lifecycle is:

```text
1. Submit Spark application
          ↓
2. Driver starts
          ↓
3. Driver requests resources
          ↓
4. Cluster manager allocates resources
          ↓
5. Executors start on worker nodes
          ↓
6. Driver builds/coordinates execution
          ↓
7. Data is divided into partitions
          ↓
8. Tasks are assigned to executor task slots
          ↓
9. Executors process partitions
          ↓
10. Tasks complete / retry if necessary
          ↓
11. Results are produced
          ↓
12. Application finishes
```

This is the mental model to carry into every later Spark topic.

---

# Part V — Driver, Workers, and Executors

## 10. Driver

The **driver** is the coordinating process for a Spark application.

Think:

```text
Driver = coordinator
Executor = worker
```

This is a useful simplification, but the driver has several concrete responsibilities.

### Driver responsibilities

The driver is responsible for things such as:

- coordinating the application
- maintaining application-level state
- interacting with Spark's execution machinery
- planning/organizing work
- scheduling work
- communicating with executors
- tracking task and stage progress
- receiving metadata and appropriate results

At the conceptual level:

```text
Python application
       ↓
     Driver
       ↓
  distributed work
       ↓
 Executors
```

### SparkSession and the driver

A `SparkSession` is the primary entry point used by modern PySpark applications.

Conceptually:

```text
Python code
    ↓
SparkSession
    ↓
Spark execution environment
```

The detailed configuration of `SparkSession` belongs to Topic 02. Here the important idea is that the Spark application has a coordinating driver-side context.

### The driver is NOT the data-processing machine

A common misconception is:

> "The driver processes the whole dataset."

That is wrong.

Suppose:

```text
Dataset = 1 TB
```

The driver does not normally load 1 TB into its own memory and process every row.

Instead:

```text
Driver
  │
  ├── coordinates
  │
  ├── schedules
  │
  └── tracks
       │
       ▼
Executors
  │
  ├── process partition A
  ├── process partition B
  ├── process partition C
  └── ...
```

The driver can nevertheless be overloaded if application code attempts to bring too much data back to it.

For example, operations such as large `collect()` calls can cause driver memory pressure.

### Driver bottlenecks

A driver can become a bottleneck through:

- excessive application metadata
- huge result collection
- excessive coordination
- poor application design
- driver-side Python processing
- large objects held in driver memory

Therefore:

> Distributed processing does not mean "the driver can safely receive unlimited data."

### What happens if the driver fails?

The driver is central to application coordination. A driver failure can terminate the application because the application loses its coordinator.

This is different from losing an individual executor: Spark can often recover work from an executor failure without restarting the entire application.

---

## 11. Worker Nodes

A **worker node** is a machine that provides resources for distributed Spark execution.

Conceptually:

```text
Worker Node
┌──────────────────────────┐
│ CPU                      │
│ RAM                      │
│ Local disk               │
│ Network                  │
│                          │
│ Executor process         │
└──────────────────────────┘
```

A worker is a physical or virtual machine/container host.

### Critical distinction

```text
Worker Node ≠ Executor
```

A worker node is the machine/resource host.

An executor is a process running for a Spark application.

Depending on deployment architecture, a worker can host one or more executor processes.

The relationship is therefore:

```text
Worker Node
     │
     └── Executor process
              │
              ├── task slots
              ├── memory
              └── application work
```

---

## 12. Executors

An **executor** is a process associated with a Spark application that performs distributed tasks.

Executors provide:

- CPU capacity for tasks
- memory for execution
- storage for cached data
- local resources for shuffle-related work
- communication with the driver

### Example

Suppose an application has:

```text
3 executors
4 cores per executor
```

Conceptually:

```text
Executor 1 → 4 task slots
Executor 2 → 4 task slots
Executor 3 → 4 task slots

Total ≈ 12 concurrent task slots
```

If a stage contains:

```text
48 partitions
```

there may be approximately:

```text
12 tasks executing
36 tasks waiting
```

Then another wave can execute as task slots become free:

```text
Wave 1 → tasks 1–12
Wave 2 → tasks 13–24
Wave 3 → tasks 25–36
Wave 4 → tasks 37–48
```

This is why:

> **Number of partitions does not equal number of simultaneously executing tasks.**

Concurrency is constrained by available resources.

### Executor lifecycle

Conceptually:

```text
Resource allocated
       ↓
Executor starts
       ↓
Executor registers/communicates
       ↓
Executor receives tasks
       ↓
Executor executes tasks
       ↓
Executor may cache/store intermediate data
       ↓
Application completes
       ↓
Executor terminates
```

Executors can also disappear unexpectedly because of:

- machine failure
- process failure
- resource exhaustion
- container termination
- network failure

Spark's fault-tolerance mechanisms are designed to recover appropriate lost work.

---

# Part VI — Cluster Managers

## 13. Cluster Managers

A **cluster manager** allocates cluster resources to applications.

At a high level, it answers questions such as:

- Where can the application run?
- How much CPU can it receive?
- How much memory can it receive?
- Where should executors be started?
- What resources are currently available?

Conceptually:

```text
Spark Application
       │
       ▼
Cluster Manager
       │
       ├── resources
       ├── CPU
       ├── memory
       └── placement
              │
       ┌──────┼──────┐
       ▼      ▼      ▼
    Worker  Worker  Worker
```

Spark can run using several cluster-management models.

---

## 14. Local Mode

Local mode runs Spark on one machine.

Common forms include:

```text
local
local[2]
local[*]
```

Conceptually:

- `local` → local execution with a single execution thread
- `local[2]` → use two local execution threads
- `local[*]` → use the available logical processors for local execution

For learning and development, `local[*]` is extremely useful.

### Example

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("HelloLocal")
    .master("local[*]")
    .getOrCreate()
)

df = spark.range(1_000_000)

print(df.count())

spark.stop()
```

### What happens conceptually?

```text
Python application
        ↓
Local Spark execution
        ↓
One machine
        ↓
Local execution resources
```

The workload is still represented using Spark's distributed execution concepts, but the resources belong to one machine.

### Why local mode is useful

- learning
- development
- fast feedback
- unit/integration testing
- small experiments

### Why local mode is not a real cluster

A local run does not reproduce every property of a multi-machine environment.

It does not faithfully reproduce:

- cross-machine network transfer
- worker-machine failure
- executor placement across hosts
- real cluster resource contention
- all distributed networking behaviour

Therefore:

> A successful local run does not prove that a Spark job will behave identically on a cluster.

---

## 15. Spark Standalone

Spark Standalone is Spark's own cluster-management system.

A conceptual cluster:

```text
                 Spark Master
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
      Worker 1   Worker 2   Worker 3
          │          │          │
      Executor    Executor    Executor
```

The Spark Standalone master coordinates resource allocation.

Workers provide resources.

Executors perform application work.

### Why it is useful for learning

A small Docker Compose cluster can make distributed behaviour visible without requiring a cloud platform.

For example:

```text
Docker Compose
├── Spark Master
├── Spark Worker 1
├── Spark Worker 2
└── Spark Worker 3
```

This is particularly useful for observing:

- multiple workers
- executors
- task distribution
- executor failure
- retries
- Spark UI behaviour

### Production considerations

Standalone is straightforward and useful, but organizations may instead standardize on:

- Kubernetes
- YARN
- managed Spark platforms

The correct choice depends on the organization's existing infrastructure and operational model.

---

## 16. YARN

**YARN (Yet Another Resource Negotiator)** became common in Hadoop ecosystems.

At a high level:

```text
            YARN
             │
     ┌───────┴────────┐
     ▼                ▼
ResourceManager   NodeManagers
     │                │
     └──── resource ──┘
              │
        Spark application
```

Important components include:

- **ResourceManager** — cluster-level resource coordination
- **NodeManager** — manages resources on individual nodes

Spark integrates with YARN so that Spark applications can request and receive cluster resources.

### Why it matters to Data Engineers

You may encounter Spark running on YARN in established Hadoop-based data platforms.

You do not need to become a Hadoop administrator to understand Topic 01.

The key mental model is:

```text
YARN = resource-management environment
Spark = distributed computation engine
```

---

## 17. Kubernetes

Spark can run on Kubernetes using containerized Spark workloads.

A conceptual architecture is:

```text
             Kubernetes Cluster
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
     Driver Pod          Executor Pods
                              │
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
                Executor   Executor   Executor
```

Important concepts include:

- driver pod
- executor pods
- Kubernetes scheduler
- CPU/memory requests and limits
- container images
- networking
- ephemeral executor processes

### Why Kubernetes is useful for Spark

Kubernetes provides a standardized container orchestration environment.

Spark applications can therefore participate in an organization's broader container platform.

### Production considerations

A production Spark-on-Kubernetes platform requires attention to:

- resource requests/limits
- container images
- networking
- authentication
- storage
- observability
- scheduling
- failure behaviour

Those details are outside the scope of this topic.

---

## 18. Cluster Manager Comparison

| Model | Resource management | Typical use | Main advantage | Main consideration |
|---|---|---|---|---|
| Local | Local machine | Learning, development, testing | Very simple | Not a multi-machine cluster |
| Spark Standalone | Spark's own manager | Small/self-managed Spark clusters | Simple Spark-native architecture | Separate cluster-management platform |
| YARN | Hadoop/YARN | Established Hadoop environments | Mature resource management in Hadoop ecosystems | Hadoop-oriented operational environment |
| Kubernetes | Kubernetes | Containerized/cloud-native environments | Integrates Spark with container orchestration | More infrastructure concepts |
| Managed Spark platform | Provider/platform manages infrastructure | Cloud/lakehouse environments | Reduced infrastructure management | Platform-specific behaviour/cost |

The important skill is not memorizing a winner.

The skill is understanding:

```text
Spark
  ↓
needs resources
  ↓
cluster manager/platform
  ↓
allocates resources
  ↓
executors run
```

---

# Part VII — Partitions, Cores, and Tasks

## 19. Partitions

A **partition** is a logical portion of a distributed dataset and a fundamental unit of parallel processing in Spark.

For example:

```text
1 billion rows
       ↓
100 partitions
```

Conceptually:

```text
Partition 1
Partition 2
Partition 3
...
Partition 100
```

Spark can process these partitions independently where the computation allows it.

### Partition is not the same as file

A common confusion is:

```text
partition = file
```

That is not generally correct.

A Spark in-memory partition is an execution concept.

A filesystem partition created by writing with partition columns is a storage-layout concept.

A physical input file may also be split into execution partitions.

These concepts are related but not interchangeable.

### Partition is not a database partition

A database partition is a database-storage/data-management concept.

A Spark execution partition is primarily about distributed computation.

---

## 20. Cores and Task Slots

A CPU core is a processing resource.

For Spark execution, executor cores provide capacity for concurrent task execution.

Suppose:

```text
Executor 1 → 4 cores
Executor 2 → 4 cores
Executor 3 → 4 cores
```

Conceptually:

```text
≈ 12 concurrent task slots
```

Now consider:

```text
48 partitions
```

The stage may execute in waves:

```text
Wave 1 → 12 tasks
Wave 2 → 12 tasks
Wave 3 → 12 tasks
Wave 4 → 12 tasks
```

Now consider only:

```text
5 partitions
```

Even if 12 task slots are available:

```text
5 partitions → at most 5 tasks for that stage
```

The cluster cannot invent additional partitions to create more work.

This is why too few partitions can underutilize available resources.

### Important limitation

Do not interpret:

```text
1 partition = 1 CPU core
```

as a permanent rule.

The actual relationship is:

```text
Partition
   ↓
Task
   ↓
Task executes using available executor resources
```

The number of concurrent tasks depends on available resources.

---

# Part VIII — Jobs, Stages, and Tasks

## 21. Jobs

A **job** is a unit of Spark execution triggered by an action.

For example:

```python
df.count()
```

can trigger a Spark job.

Another action, such as:

```python
df.write.parquet("/output")
```

can trigger another job.

Conceptually:

```text
Application
   ├── Job 1
   ├── Job 2
   └── Job 3
```

One application can therefore contain multiple jobs.

The complete transformation/action model is taught later in Topic 04. Here, the important point is:

> **An action causes Spark to execute the required computation, producing a job.**

---

## 22. Stages

A **stage** is a portion of a Spark job that can be executed as a group of tasks without crossing a shuffle boundary.

Conceptually:

```text
Stage 1
Read → Filter → Map
        │
        ▼
      Shuffle
        │
        ▼
Stage 2
GroupBy → Aggregate → Write
```

A shuffle can require data to be redistributed between partitions and machines.

That redistribution creates a boundary in the execution graph.

The detailed mechanics of shuffles and join strategies belong to Topic 07.

For Topic 01, remember:

> **Stage boundaries are associated with dependencies that require redistribution, especially shuffle boundaries.**

---

## 23. Tasks

A **task** is a unit of work executed for one partition of a stage.

For example:

```text
Stage
  ↓
200 partitions
  ↓
approximately 200 tasks
```

Those tasks do not necessarily execute simultaneously.

If the application has only:

```text
20 available task slots
```

then execution occurs in waves:

```text
Wave 1 → 20 tasks
Wave 2 → 20 tasks
...
Wave 10 → remaining tasks
```

### Task lifecycle

Conceptually:

```text
Task scheduled
      ↓
Executor receives task
      ↓
Partition processed
      ↓
Task succeeds
      ↓
Result/metadata reported
```

If the task fails:

```text
Task fails
    ↓
Retry may occur
    ↓
Successful completion
```

The exact retry behaviour depends on the failure and application configuration.

---

# Part IX — Execution Hierarchy

## 24. Application → Job → Stage → Task → Partition

This hierarchy must become second nature.

```text
Application
   │
   ├── Job 1
   │     │
   │     ├── Stage 1
   │     │      ├── Task → Partition
   │     │      ├── Task → Partition
   │     │      └── Task → Partition
   │     │
   │     └── Stage 2
   │            ├── Task → Partition
   │            └── Task → Partition
   │
   └── Job 2
         └── ...
```

### The concepts

**Application**

The complete Spark application.

**Job**

A unit of execution triggered by an action.

**Stage**

A portion of a job separated by execution dependencies such as shuffle boundaries.

**Task**

A unit of execution for a partition within a stage.

**Partition**

A portion of the distributed dataset processed by a task.

### A realistic mental model

Suppose:

```text
One Spark application
        ↓
Action
        ↓
Job
        ↓
Stage 1
        ↓
100 partitions
        ↓
100 tasks
        ↓
Executors execute tasks in waves
        ↓
Shuffle boundary
        ↓
Stage 2
        ↓
new partition/task set
```

This hierarchy is the foundation for understanding the Spark UI later.

---

# Part X — Data Locality

## 25. Data Locality

In distributed systems, **data locality** means trying to perform computation close to where the data is located.

Why?

Because moving computation is often cheaper than moving large amounts of data.

Conceptually:

```text
Data
 │
 └── Machine A
        │
        └── Run computation near Machine A
```

instead of:

```text
Data on Machine A
       │
       └── network ──► Machine B
                         │
                         └── computation
```

### Locality levels

A simplified hierarchy is:

```text
Local
  ↓
Rack-local
  ↓
Remote
```

The closer the computation is to the data, the less network transfer may be required.

### Cloud object storage changes the picture

Modern Spark platforms frequently read from:

- Amazon S3
- Google Cloud Storage
- Azure Data Lake Storage

In these architectures, the data is often not sitting on the local disk of the executor machine.

Conceptually:

```text
             Object Storage
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
    Executor    Executor    Executor
```

The traditional "move computation to the disk containing the data" model becomes less direct.

Network access to object storage is expected.

This is one reason file layout, partitioning, throughput, and data movement remain important in cloud Spark systems.

Detailed cloud-storage architecture belongs to later modules.

---

# Part XI — Fault Tolerance

## 26. Why Distributed Systems Need Fault Tolerance

In a single-machine program:

```text
Machine fails
    ↓
Program fails
```

In a cluster:

```text
10 machines
    ↓
1 machine fails
```

The system should ideally continue or recover rather than losing the entire computation.

Failures can include:

- executor failure
- worker failure
- machine failure
- task failure
- network failure
- lost partition

Spark is designed to recover appropriate lost work.

---

## 27. Lineage

One of Spark's key ideas is **lineage**.

Conceptually:

```text
Source
  ↓
Transformation A
  ↓
Transformation B
  ↓
Transformation C
```

Spark can retain enough information about how derived data was produced to recompute lost partitions when appropriate.

Suppose:

```text
Partition P7
```

was lost because an executor failed.

Spark may reconstruct the lost partition by re-executing the necessary upstream computation.

```text
Source
  ↓
Transformation A
  ↓
Transformation B
  ↓
Recompute P7
```

This is preferable to restarting the entire application from scratch.

### Important mental model

```text
Executor failure
      ↓
Some work lost
      ↓
Spark identifies affected work
      ↓
Tasks can be retried/recomputed
      ↓
Application continues when recovery succeeds
```

This is one of the reasons Spark can tolerate individual worker/executor failures.

---

## 28. Task Retries and Executor Failures

### Task failure

A task can fail because of:

- transient errors
- corrupted input
- resource problems
- executor/process failure
- application exceptions

A failed task may be retried.

### Executor failure

Suppose:

```text
Executor 2
```

fails while processing several partitions.

Spark can lose the work that was associated with that executor and recompute affected work as necessary.

Conceptually:

```text
Executor 1 → healthy
Executor 2 → FAILED
Executor 3 → healthy
                  │
                  ▼
          Lost task results
                  │
                  ▼
             recompute
```

The application does not necessarily restart from zero.

### Important distinction

```text
Executor failure
    ≠
Driver failure
```

An executor is a worker process for the application.

The driver is the application's coordinator.

Losing the driver is much more fundamental to the application's continued execution.

---

# Part XII — Speculative Execution

## 29. Stragglers

A **straggler** is an unusually slow task.

Imagine:

```text
Task 1 → 10 sec
Task 2 → 11 sec
Task 3 → 9 sec
Task 4 → 8 sec
Task 5 → 60 min
```

Even though most tasks finish quickly, the stage cannot finish until its required tasks finish.

Therefore:

```text
Stage completion
       ↓
waits for slow task
```

One slow task can delay the entire downstream computation.

---

## 30. Speculative Execution

Spark can use **speculative execution** to launch another attempt of an unusually slow task.

Conceptually:

```text
Original Task 5
     │
     └── running unusually slowly
              │
              ▼
       Speculative copy
              │
       ┌──────┴──────┐
       ▼             ▼
 Original        Speculative
   task             task
       │             │
       └─────┬───────┘
             ▼
      first successful result
```

### When it helps

Speculation can help when slowness is caused by:

- a problematic machine
- transient resource contention
- an unhealthy executor

### When it does not solve the underlying problem

If the task is genuinely slow because it has much more data than other tasks, launching another copy does not necessarily solve the fundamental issue.

That situation may be related to data skew, which is covered in Topic 09.

### Cost

Speculation uses additional resources because work may execute twice.

Therefore:

> Speculation is a resilience/performance mechanism, not a substitute for understanding why tasks are slow.

---

# Part XIII — PySpark Internal Architecture

## 31. Classic PySpark Python/JVM Architecture

PySpark is not simply "Spark rewritten in Python."

Classic PySpark combines:

- Python
- JVM-based Spark execution
- communication between Python and JVM processes
- Python worker processes for Python-specific execution

A conceptual architecture is:

```text
Python Application
        │
        ▼
Python Driver
        │
        │ Py4J
        ▼
Spark JVM
        │
        ▼
Cluster / Executors
        │
        ├── JVM execution
        │
        └── Python Worker
                 │
                 └── Python UDF
```

### Python driver

Your application code is commonly written in Python:

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("Example")
    .getOrCreate()
)
```

Python communicates with the Spark JVM.

### Py4J

In classic PySpark, **Py4J** provides a bridge between Python and JVM-side Spark components.

Conceptually:

```text
Python
   │
   │ Py4J
   ▼
JVM
```

This does not mean every Spark operation becomes a Python-level row-by-row call.

That distinction is extremely important.

---

## 32. Not Every DataFrame Operation Runs in Python

Consider:

```python
df.filter(df.amount > 100).select("customer_id")
```

The DataFrame API constructs Spark expressions.

Spark can represent those operations in its JVM-side execution system.

Conceptually:

```text
Python API call
       ↓
Spark logical representation
       ↓
JVM Spark execution
```

The Python code is expressing the computation.

It is not necessarily processing each row in Python.

This is one reason Spark's built-in functions are important.

---

## 33. Python Workers

When Spark must execute Python-specific user logic, Python worker processes can be involved.

Conceptually:

```text
JVM Executor
      │
      ▼
Python Worker
      │
      ▼
Python function
```

This creates a process boundary.

Data may need to move:

```text
JVM
 ↓
serialization/transfer
 ↓
Python worker
 ↓
Python execution
 ↓
serialization/transfer
 ↓
JVM
```

That boundary can introduce overhead.

---

## 34. Python UDF Execution Boundary

A simplified model:

```text
DataFrame built-in function
          │
          ▼
     JVM execution
```

versus:

```text
Python UDF
    │
    ▼
JVM
    │
    ▼
Python worker
    │
    ▼
Python function
    │
    ▼
JVM
```

This is why built-in Spark functions are generally preferred when equivalent functionality exists.

The detailed performance comparison between built-ins, Python UDFs, and pandas UDFs belongs to Topic 11.

Here the architectural lesson is:

> **Crossing the JVM/Python boundary can have a cost.**

---

# Part XIV — Arrow

## 35. Arrow's Role

Apache Arrow provides a columnar memory/data interchange format used to make certain Python/JVM data transfers more efficient.

In this module, the important connection is:

```text
Spark JVM
    │
    │ Arrow
    ▼
Python / pandas
```

Arrow can reduce some serialization overhead compared with traditional row-oriented transfer.

This becomes especially important for:

- pandas UDFs
- vectorized Python processing
- certain conversions between Spark and pandas

You have already encountered Arrow in earlier modules. Here, remember its architectural role:

> **Arrow helps move columnar data efficiently across language/runtime boundaries.**

It does not mean that all PySpark operations automatically run through Python or Arrow.

---

# Part XV — Spark Connect

## 36. Classic PySpark vs Spark Connect

Classic PySpark conceptually looks like:

```text
Classic PySpark

Python
  │
  ▼
JVM Spark Driver
  │
  ▼
Executors
```

Spark Connect introduces a client/server architecture:

```text
Spark Connect

Python Client
     │
     │ logical plan / requests
     ▼
Spark Connect Server
     │
     ▼
Executors
```

### Classic architecture

The Python application participates closely with the Spark driver-side runtime.

### Spark Connect architecture

The Python process can act as a thin client.

The client communicates with a remote Spark server, which handles Spark-side execution.

### Why this matters

Spark Connect can provide:

- separation between client and compute
- remote Spark execution
- a cleaner client/server boundary
- easier interaction with remote Spark environments

### Important limitation

The API surface is not identical to classic Spark.

For example, the RDD API is not available through Spark Connect.

Therefore:

```text
Classic PySpark ≠ Spark Connect
```

They share the Spark programming model but have different architectural boundaries.

---

## 37. When Spark Connect Is Useful

Spark Connect can be useful when:

- compute is remote
- clients should remain lightweight
- applications need a client/server separation
- interactive tools need access to a remote Spark environment

It is not simply:

```text
SSH into a server
```

It is an application protocol and client/server architecture for interacting with Spark.

Detailed Spark Connect usage is outside this topic.

---

# Part XVI — When Not to Use Spark

## 38. Spark Is Not Automatically the Right Answer

Distributed processing has real costs.

Spark can introduce:

- cluster startup overhead
- infrastructure requirements
- operational complexity
- network communication
- serialization
- scheduling overhead
- debugging complexity
- resource costs

Therefore:

> **Large data does not automatically mean Spark is the right answer.**

---

## 39. When a Single-Node Engine May Be Better

Spark may be unnecessary when:

### The data fits comfortably on one machine

For example:

```text
Dataset = 20 GB
Machine = 128 GB RAM
```

If the workload can be processed efficiently on one machine, introducing a distributed cluster may add complexity without enough benefit.

### DuckDB or Polars already solves the problem

If DuckDB or Polars can process the workload within the required processing window, a single-node solution may be preferable.

### The workload requires low-latency lookup

Spark is primarily a large-scale data-processing engine.

A low-latency point-lookup system may require a database, cache, or specialized serving system instead.

### Jobs are tiny and frequent

If a job takes:

```text
5 seconds of computation
```

but requires:

```text
30 seconds of cluster startup
```

the distributed infrastructure may dominate the workload.

### The operational complexity is not justified

Sometimes the correct engineering decision is:

```text
Keep it simple.
```

---

## 40. Spark Decision Framework

Use this as a first architectural filter:

```text
Does the workload fit comfortably on one machine?
              │
          ┌───┴───┐
         Yes      No
          │        │
          ▼        ▼
 Can DuckDB/     Consider
 Polars handle    distributed
 it efficiently?  processing
     │
 ┌───┴───┐
Yes      No
 │        │
 ▼        ▼
Prefer    Re-evaluate
single-   workload and
node      requirements
```

Then consider:

- dataset size
- processing time
- latency
- cost
- reliability requirements
- operational complexity
- available infrastructure
- scaling requirements

The final architecture should be driven by workload requirements, not by the assumption that distributed technology is always more advanced.

---

# Part XVII — Real-World Data Engineering Examples

## 41. Example 1 — 20 GB Dataset

Suppose:

```text
20 GB Parquet dataset
```

and:

```text
128 GB RAM machine
```

A well-designed DuckDB or Polars workload may process it efficiently.

Using Spark could add:

- cluster startup
- executor management
- network overhead
- operational complexity

The correct conclusion is not "20 GB can never use Spark."

The correct conclusion is:

> If a single machine comfortably satisfies the performance and reliability requirements, distributed processing may not be justified.

---

## 42. Example 2 — 2 TB Daily Dataset

Suppose a pipeline receives:

```text
2 TB every day
```

and must process it within a constrained nightly window.

If a single machine cannot meet:

- memory requirements
- processing-time requirements
- throughput requirements

then distributed processing becomes a strong architectural candidate.

A conceptual Spark architecture might be:

```text
Object Storage
      │
      ▼
Spark Application
      │
      ▼
Driver
      │
      ▼
Cluster Manager
      │
 ┌────┼────┐
 ▼    ▼    ▼
Exec Exec Exec
 │    │    │
Tasks across partitions
```

---

## 43. Example 3 — Large Fact Table + Small Dimension

Suppose:

```text
Fact table      = 500 GB
Customer table  = 500 MB
```

A distributed engine can process the large fact table across many tasks.

The small dimension may be a candidate for broadcasting in a later join-optimization discussion.

The architectural point for Topic 01 is:

```text
Large data
    ↓
partitioned execution
    ↓
multiple tasks
    ↓
multiple executors
```

Detailed broadcast-join strategy belongs to Topic 07.

---

## 44. Example 4 — Executor Failure

Suppose:

```text
Executor 2
```

fails while processing several partitions.

Spark can identify the affected work and schedule replacement attempts where possible.

Conceptually:

```text
Executor 1 → tasks complete
Executor 2 → FAIL
Executor 3 → tasks complete

Lost work
   ↓
recompute/retry
   ↓
another executor
```

The entire application does not necessarily restart.

---

## 45. Example 5 — One Slow Task

Suppose:

```text
Task 1 → 10 sec
Task 2 → 12 sec
Task 3 → 11 sec
Task 4 → 9 sec
Task 5 → 45 min
```

The stage can be held up by Task 5.

Possible causes include:

- unhealthy executor
- resource contention
- unusually large partition
- data skew

Speculative execution can help with some straggler causes.

Detailed skew diagnosis belongs to Topic 09.

---

## 46. Example 6 — Driver Out of Memory

Suppose a large DataFrame contains:

```text
500 million rows
```

and application code attempts to bring all rows to the driver.

Conceptually:

```text
Executors
   │
   │ huge result
   ▼
Driver
   │
   ▼
Memory exhaustion
```

The lesson is:

> The driver is a coordinator, not a replacement for distributed storage and processing.

---

# Part XVIII — Hands-On Lab: `hello_cluster.py`

## 47. Lab Goals

You will:

1. Create a Spark application.
2. Run a word count.
3. Run it in local mode.
4. Run it on a small Spark Standalone cluster.
5. Observe the Spark UI.
6. Identify application, job, stage, task, and executor concepts.
7. Identify which executor processes tasks.
8. Interrupt a worker during execution.
9. Observe retry/recomputation behaviour.
10. Compare the workload conceptually with DuckDB or Polars.
11. Record observations.

---

## 48. Step 1 — Create the Application

Create:

```text
jobs/hello_cluster.py
```

Example:

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def main() -> None:
    spark = (
        SparkSession.builder
        .appName("HelloCluster")
        .getOrCreate()
    )

    df = (
        spark.range(0, 10_000_000)
        .select((F.col("id") % 100).alias("bucket"))
    )

    counts = (
        df.groupBy("bucket")
        .count()
    )

    counts.write.mode("overwrite").parquet("output/word-count")

    spark.stop()


if __name__ == "__main__":
    main()
```

This example uses generated numeric data rather than an external text file so that the architecture can be studied without introducing unrelated ingestion complexity.

---

## 49. What the Code Means

### `SparkSession`

```python
SparkSession.builder
    .appName("HelloCluster")
    .getOrCreate()
```

creates or retrieves the Spark entry point.

### `spark.range`

```python
spark.range(0, 10_000_000)
```

creates a distributed DataFrame representing a range of IDs.

### Transformation

```python
.select(...)
```

describes a computation.

### Aggregation

```python
.groupBy("bucket").count()
```

requires grouped processing.

At the architecture level, this may require data redistribution and therefore can create a stage boundary.

### Write

```python
counts.write.parquet(...)
```

is an action that causes Spark to execute the required computation.

---

## 50. Run in Local Mode

A conceptual submission is:

```bash
spark-submit \
  --master local[*] \
  jobs/hello_cluster.py
```

Architecture:

```text
Python Application
       ↓
Local Spark
       ↓
One machine
       ↓
Local execution resources
```

Observe the application in the Spark UI.

---

## 51. Run on Spark Standalone

A small learning cluster might look like:

```text
                 Spark Master
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
      Worker 1   Worker 2   Worker 3
          │          │          │
      Executor    Executor    Executor
```

Submit the same application to the Standalone master.

The exact master URL depends on your local Docker Compose environment.

For example, a conceptual command is:

```bash
spark-submit \
  --master spark://spark-master:7077 \
  jobs/hello_cluster.py
```

The command should be adapted to the actual service name and port in your cluster.

---

## 52. What to Find in the Spark UI

Identify:

### Application

The overall application.

### Job

The execution triggered by the action.

### Stages

The execution sections separated by required dependencies.

### Tasks

The individual units processing partitions.

### Executors

The processes performing the distributed work.

### Executor assignment

Determine which executor processed individual tasks.

Write down:

```text
Application:
Job:
Stages:
Tasks:
Executors:
Workers:
```

Do not merely look at the numbers. Explain what each number means.

---

# Part XIX — Worker-Failure Experiment

## 53. Kill One Worker

Run the application on a small Docker Compose cluster.

While a sufficiently long-running job is executing:

1. Identify Worker 1.
2. Stop the worker container.
3. Observe the Spark UI.
4. Observe executor/task changes.
5. Determine whether tasks are retried.
6. Determine whether lost work is recomputed.
7. Record what happened.

Conceptually:

```text
Before

Worker 1 → Executor A
Worker 2 → Executor B
Worker 3 → Executor C

              ↓

Worker 2 fails

Worker 1 → Executor A
Worker 2 → FAILED
Worker 3 → Executor C

              ↓

Affected work
       ↓
retry/recompute
       ↓
available executor resources
```

### Questions to answer

- Which component failed?
- Did the driver fail?
- Which tasks were affected?
- Did the application terminate?
- Which work was recomputed?
- Why was the lost work recoverable?

---

# Part XX — Spark vs DuckDB/Polars Comparison

## 54. Compare the Same Workload

Run an equivalent aggregation using DuckDB or Polars on one machine.

Record:

| Engine | Hardware | Dataset | Runtime | Notes |
|---|---|---|---|---|
| Spark local | | | | |
| Spark cluster | | | | |
| DuckDB | | | | |
| Polars | | | | |

Do not assume Spark must win.

The purpose of this experiment is to understand:

- distributed overhead
- single-node efficiency
- workload size
- startup costs
- network costs
- parallelism
- operational complexity

### Key question

> At what workload size or processing requirement does distributed execution become useful on your hardware?

The answer is workload- and environment-dependent.

---

# Part XXI — Architecture Debugging Exercises

## 55. Exercise 1 — Driver OOM

### Symptoms

The application crashes while attempting to return a very large result.

### Likely architectural cause

Too much data is being brought to the driver.

### Investigation

Ask:

- Is the application collecting large datasets?
- Is the driver being used as a data-processing node?
- How much data is being returned?

### Conceptual fix

Keep large data distributed and return only appropriately sized results.

### Do not do

Do not simply keep increasing driver memory without understanding why the application is collecting the data.

---

## 56. Exercise 2 — Executor Dies

### Symptoms

An executor disappears during execution.

### Likely architectural causes

Possible causes include:

- machine failure
- process failure
- resource exhaustion
- container termination
- network failure

### Investigation

Determine:

- which executor disappeared
- which tasks were running there
- whether tasks were retried
- whether the application recovered

### Conceptual fix

Understand and use Spark's retry/recomputation behaviour; then investigate the underlying infrastructure/resource cause.

### Do not do

Do not assume that every executor failure means the entire application must restart.

---

## 57. Exercise 3 — One Task Is Much Slower

### Symptoms

Most tasks complete quickly while one task remains active.

### Possible causes

- straggler
- uneven partition
- data skew
- unhealthy executor

### Investigation

Compare task durations and partition sizes.

### Conceptual fixes

Depending on the root cause:

- investigate the slow worker
- investigate partition distribution
- use appropriate skew/performance techniques later

### Do not do

Do not blindly add executors.

More executors cannot automatically accelerate one already-running slow task.

---

## 58. Exercise 4 — Many Executors, Poor Utilization

### Symptoms

The cluster has substantial resources, but utilization is low.

### Possible causes

- too few partitions
- insufficient parallel work
- small workload
- long dependency chain
- waiting on a limited stage

### Investigation

Reason from:

```text
Partitions
    ↓
Tasks
    ↓
Available task slots
```

If there are only five tasks and fifty available task slots, the cluster cannot use all fifty slots for that stage.

---

## 59. Exercise 5 — Python UDF Becomes Expensive

### Symptoms

A previously simple DataFrame operation becomes much slower after adding Python logic.

### Architectural cause

The computation may now cross:

```text
JVM
 ↓
Python worker
 ↓
JVM
```

### Investigation

Ask:

- Is a Python UDF being used?
- Could a Spark built-in expression perform the same logic?
- Is data being serialized between runtimes?

### Conceptual fix

Prefer built-in Spark expressions when they provide equivalent functionality.

Detailed UDF benchmarking belongs to Topic 11.

---

## 60. Exercise 6 — Worker Disappears

### Symptoms

One worker machine/container disappears.

### Investigation

Distinguish:

```text
Worker failure
vs
Executor failure
vs
Driver failure
```

Then determine which application resources were lost and whether Spark can recompute affected work.

---

# Part XXII — Common Misconceptions

## 61. Misconception: "Spark is just pandas on multiple machines."

**Correct mental model:** Spark is a distributed execution engine with a driver, executors, tasks, partitions, execution stages, and cluster-level scheduling.

The DataFrame API may feel familiar, but the execution model is fundamentally different.

---

## 62. Misconception: "The driver processes the data."

**Correct mental model:**

```text
Driver → coordinates
Executors → process distributed work
```

The driver may receive results and metadata, but it is not intended to process every row of a large dataset.

---

## 63. Misconception: "Every executor processes the entire dataset."

**Correct mental model:**

```text
Dataset
  ↓
Partitions
  ↓
Tasks
  ↓
Executors
```

Each task processes a partition or relevant execution unit.

---

## 64. Misconception: "One partition equals one CPU core."

A partition creates a task of work.

Task concurrency depends on available executor resources.

```text
Partitions → Tasks → Available task slots
```

---

## 65. Misconception: "More executors always means faster jobs."

More executors may help if there is enough parallel work and the workload scales.

They can also introduce:

- resource contention
- scheduling overhead
- network pressure
- higher cost

---

## 66. Misconception: "More partitions always means better performance."

Too few partitions can underutilize resources.

Too many partitions can create excessive scheduling overhead and tiny tasks.

Partition tuning is a later topic.

---

## 67. Misconception: "A worker node is the same thing as an executor."

They are different:

```text
Worker = machine/resource host
Executor = application process
```

---

## 68. Misconception: "A job equals a stage."

A job can contain multiple stages.

```text
Job
 ├── Stage 1
 ├── Stage 2
 └── ...
```

---

## 69. Misconception: "A stage equals a task."

A stage contains multiple tasks.

```text
Stage
 ├── Task 1
 ├── Task 2
 ├── Task 3
 └── ...
```

---

## 70. Misconception: "Spark always keeps all data in RAM."

Spark can use memory and disk resources.

Distributed execution is not equivalent to "everything must fit in RAM."

---

## 71. Misconception: "Spark never uses disk."

Disk can be involved in:

- input/output
- intermediate data
- spilling
- shuffle-related processing

The detailed mechanics belong to later topics.

---

## 72. Misconception: "If one executor dies, the entire application always fails."

Executor failures can often be recovered through task retries and recomputation.

Driver failure is a different architectural event.

---

## 73. Misconception: "Python code always runs inside the executor JVM."

Python-specific logic can execute in Python worker processes.

The Spark JVM and Python worker are separate runtime processes.

---

## 74. Misconception: "Spark Connect is simply remote SSH."

Spark Connect is a client/server architecture.

```text
Python Client
      ↓
Spark Connect Server
      ↓
Spark execution
```

---

## 75. Misconception: "Spark should be used whenever data is large."

Data size is only one consideration.

Also consider:

- processing time
- latency
- cost
- complexity
- single-node capability
- reliability
- operational requirements

---

## 76. Misconception: "Distributed computing is automatically faster."

Distributed execution has overhead.

For small workloads:

```text
distributed overhead > parallelism benefit
```

A highly optimized single-node engine can outperform a cluster on many workloads.

---

# Part XXIII — Production Engineering Considerations

## 77. Why This Architecture Matters in Production

Understanding Spark architecture affects:

### Production pipelines

You need to understand where processing happens and where failures occur.

### Lakehouses

Large datasets commonly require distributed transformation.

### ETL/ELT

Spark can execute large transformations across many workers.

### Batch processing

A fixed processing window requires enough distributed throughput.

### Cloud platforms

Cloud clusters add resource allocation, object storage, networking, and cost considerations.

### Reliability

Executor failures must be distinguishable from driver/application failures.

### Performance

You need to understand:

```text
partitions
tasks
cores
executors
network
```

before performance tuning can make sense.

### Cost

More machines cost more.

The goal is not maximum infrastructure.

The goal is sufficient resources for the required workload.

### Capacity planning

A production engineer should be able to reason from:

```text
Input volume
    ↓
Partitioning
    ↓
Tasks
    ↓
Task slots
    ↓
Executors
    ↓
Workers
    ↓
Processing window
```

---

# Part XXIV — Interview Preparation

## 78. Basic Questions

### 1. What problem does distributed computing solve?

**Answer guidance:** Explain single-machine CPU, memory, storage, and processing-time limits, then explain horizontal scaling and parallel execution.

### 2. What is vertical scaling?

**Answer guidance:** Increasing resources on one machine, such as CPU or RAM.

### 3. What is horizontal scaling?

**Answer guidance:** Adding machines and distributing computation/data across them.

### 4. What is a Spark application?

**Answer guidance:** The complete application execution coordinated by a driver and using executors to perform distributed work.

### 5. What is the Spark driver?

**Answer guidance:** The coordinating process responsible for application-level execution coordination, scheduling, and tracking.

### 6. What is an executor?

**Answer guidance:** An application-associated process that executes tasks and provides resources for distributed work.

### 7. What is a worker node?

**Answer guidance:** A machine that provides resources on which executor processes can run.

### 8. What is a partition?

**Answer guidance:** A logical portion of distributed data and a fundamental unit of parallel processing.

### 9. What is a task?

**Answer guidance:** A unit of work that processes a partition for a stage.

### 10. What is a cluster manager?

**Answer guidance:** The resource-management layer that allocates CPU/memory and helps place application resources.

---

## 79. Intermediate Questions

### 1. Explain driver versus executor.

**Answer guidance:** Driver coordinates; executors execute distributed tasks and hold application execution resources.

### 2. Explain worker versus executor.

**Answer guidance:** Worker is the host machine; executor is a process associated with an application.

### 3. How are 48 partitions processed with 12 task slots?

**Answer guidance:** Approximately 12 tasks can execute concurrently, so the work proceeds in multiple waves.

### 4. What creates a stage boundary?

**Answer guidance:** Dependencies requiring redistribution, especially shuffle boundaries.

### 5. Can a stage have many tasks?

**Answer guidance:** Yes. Tasks correspond to the stage's relevant partitions.

### 6. Why doesn't Spark process every row on the driver?

**Answer guidance:** The driver coordinates distributed work; executors process partitions.

### 7. Why is network communication important in distributed systems?

**Answer guidance:** Machines must exchange data and coordination information, and network transfer can become a major cost.

### 8. Why is local mode not equivalent to a cluster?

**Answer guidance:** It lacks genuine multi-machine behaviour, cross-host network effects, and realistic worker/executor failure boundaries.

### 9. What is lineage?

**Answer guidance:** Information describing how derived data was produced so lost work can be recomputed.

### 10. What is speculative execution?

**Answer guidance:** Launching another attempt of an unusually slow task to mitigate stragglers.

---

## 80. Advanced Questions

### 1. Why can an executor failure be recoverable while a driver failure is much more serious?

**Answer guidance:** Executors are workers whose lost task work can often be retried/recomputed; the driver is the application's central coordinator.

### 2. Explain the relationship among partition, task, core, and executor.

**Answer guidance:** A stage has partitions; tasks process those partitions; executor cores provide concurrent task capacity.

### 3. Why doesn't adding executors guarantee linear speedup?

**Answer guidance:** Parallelism can be limited by dependencies, data movement, skew, I/O, coordination, and serial work.

### 4. Explain data locality.

**Answer guidance:** Scheduling computation near data can reduce network transfer; cloud object storage changes the traditional local-disk model.

### 5. Explain Py4J in classic PySpark.

**Answer guidance:** It provides a bridge between Python and JVM-side Spark components.

### 6. Why can Python UDFs introduce overhead?

**Answer guidance:** Python-specific execution can require communication and serialization across a JVM/Python process boundary.

### 7. Does every DataFrame operation execute in a Python worker?

**Answer guidance:** No. Spark built-in DataFrame expressions can execute in Spark's JVM-based engine.

### 8. What role does Arrow play?

**Answer guidance:** It provides an efficient columnar interchange path for certain JVM/Python data transfers and vectorized operations.

### 9. How does Spark Connect differ from classic PySpark?

**Answer guidance:** Connect introduces a thin client/server boundary where the client communicates with a remote Spark server.

### 10. When might DuckDB outperform Spark?

**Answer guidance:** On workloads that fit efficiently on one machine, especially when cluster startup and distributed coordination outweigh the benefit of distribution.

---

## 81. Scenario-Based Questions

### 1. You have 10 TB of daily data and a two-hour processing window. What architectural questions do you ask?

**Answer guidance:** Assess single-node feasibility, required throughput, partitioning, cluster capacity, network/storage bandwidth, reliability, and cost.

### 2. One executor disappears during a production job. What do you investigate?

**Answer guidance:** Identify affected tasks, executor/worker failure cause, retries, recomputation, and infrastructure/resource errors.

### 3. You have 100 task slots but only 5 partitions. Why is utilization low?

**Answer guidance:** There are only five units of stage-level work, so the stage cannot use all available task slots.

### 4. A developer says "increase driver memory because Spark is slow." What do you ask first?

**Answer guidance:** Determine whether the driver is actually memory-bound or whether the problem is executor computation, I/O, network, partitioning, or data collection.

### 5. A Spark application works locally but behaves differently on a cluster. Why?

**Answer guidance:** Multi-machine scheduling, network communication, resource allocation, serialization, executor behaviour, and failure boundaries differ.

### 6. A single task runs for 45 minutes while others finish in 20 seconds. What architectural concepts do you consider?

**Answer guidance:** Stragglers, partition imbalance, data skew, executor health, and speculative execution.

### 7. A Python UDF makes a pipeline dramatically slower. What is your first architectural hypothesis?

**Answer guidance:** The computation may be crossing the JVM/Python worker boundary and paying serialization/process overhead.

### 8. An application has tiny workloads arriving every few seconds. Should you automatically introduce Spark?

**Answer guidance:** No. Evaluate cluster startup, operational overhead, latency requirements, and whether a single-node or serving-oriented system is more appropriate.

### 9. Your organization already runs Kubernetes. What Spark deployment option might align with that infrastructure?

**Answer guidance:** Spark on Kubernetes is a natural candidate, but evaluate operational requirements, resource management, networking, storage, and platform standards.

### 10. A team wants to run a 20 GB transformation on a large Spark cluster. What questions should you ask?

**Answer guidance:** Determine whether DuckDB/Polars can meet the processing requirement more simply and cheaply, and whether the workload actually benefits from distributed execution.

---

# Part XXV — Practice Exercises

## 82. Beginner Exercises

### Exercise 1 — Architecture Vocabulary

Define, in your own words:

- driver
- executor
- worker
- cluster manager
- partition
- task
- job
- stage

Then draw their relationships.

### Exercise 2 — Scaling

A machine has:

```text
8 cores
32 GB RAM
```

Explain two ways to increase capacity:

- vertical scaling
- horizontal scaling

### Exercise 3 — Task Waves

Given:

```text
24 partitions
8 task slots
```

Draw the execution waves.

### Exercise 4 — Driver vs Executor

Explain why this statement is wrong:

> "The driver should load the entire dataset because it controls the job."

### Exercise 5 — Single Node vs Cluster

Given a 10 GB dataset and a powerful single machine, list the questions you would ask before deciding to use Spark.

---

## 83. Intermediate Exercises

### Exercise 1 — Execution Hierarchy

Draw:

```text
Application
→ Jobs
→ Stages
→ Tasks
→ Partitions
```

using a hypothetical application containing two jobs.

### Exercise 2 — Executor Capacity

Given:

```text
4 executors
5 cores each
```

calculate the approximate task-slot capacity and explain how 73 partitions would execute.

### Exercise 3 — Failure

Draw what happens when one of three executors fails while processing tasks.

### Exercise 4 — Data Locality

Compare processing a file on local disk with processing data from object storage.

### Exercise 5 — Cluster Manager

Choose an appropriate conceptual deployment model for:

1. local learning
2. self-managed Spark cluster
3. Hadoop ecosystem
4. containerized organization

Explain your reasoning.

---

## 84. Advanced Exercises

### Exercise 1 — Architecture Review

Design a cluster for a hypothetical 2 TB nightly pipeline.

Specify:

- workers
- executors
- cores
- partitions
- task concurrency
- cluster manager

Do not optimize exact numbers yet. Focus on the architecture.

### Exercise 2 — Failure Analysis

An executor fails after completing 20 of its assigned tasks.

Explain:

1. What was lost?
2. What remains?
3. What can Spark recompute?
4. Why doesn't the entire application necessarily restart?

### Exercise 3 — Python Boundary

Trace this conceptual operation:

```text
Python UDF
```

from Python application to executor-side Python execution and back.

### Exercise 4 — Spark Connect

Draw classic PySpark and Spark Connect architectures side-by-side and explain the boundary difference.

### Exercise 5 — Spark or DuckDB?

A 50 GB dataset takes 20 seconds in DuckDB and 2 minutes in a Spark cluster.

Explain why Spark may still be the wrong choice for that workload.

---

## 85. Architecture Exercises

### Exercise 1

Draw a three-worker Spark Standalone cluster with:

```text
1 driver
3 workers
1 executor per worker
4 cores per executor
```

Then show 24 partitions executing in waves.

### Exercise 2

Design an architecture where the driver runs separately from executor workers.

Explain each network relationship.

### Exercise 3

Design the failure path when Worker 2 disappears.

### Exercise 4

Design the same conceptual application on Kubernetes.

Replace worker-host terminology with driver/executor pods while keeping the Spark execution concepts clear.

### Exercise 5

Design a decision tree for:

```text
DuckDB vs Polars vs Spark
```

using:

- data size
- processing time
- latency
- operational complexity
- cost
- scaling requirement

---

# Part XXVI — Final Architecture Exercise

## 86. Scenario

> A company receives **5 TB of daily event data**. The data is stored in object storage. The pipeline must process the data nightly using a small Spark cluster. The pipeline must tolerate executor failures and complete within a fixed processing window.

Do not read the expected reasoning until you have designed your own architecture.

---

## 87. Your Design

Specify:

### Driver

Where does the driver run?

### Workers

How many worker resources are conceptually required?

### Executors

How are executors distributed?

### Cores

How do executor cores influence task concurrency?

### Partitions

How will the 5 TB workload be divided for distributed execution?

### Tasks

How do tasks relate to partitions?

### Cluster manager

Which cluster manager would you consider?

### Data flow

How does data move from object storage into distributed processing?

### Failure recovery

What happens when an executor fails?

---

## 88. Questions You Must Answer

1. Why is Spark appropriate?
2. How does the application start?
3. Where does the driver run?
4. How are executors created?
5. How is data partitioned?
6. How are tasks executed?
7. How are jobs and stages formed conceptually?
8. What happens if an executor dies?
9. What happens if one task becomes a straggler?
10. How does PySpark interact with JVM execution?
11. Would Spark Connect be useful?
12. Which cluster manager could be used and why?

---

## 89. Expected Reasoning Framework

A strong architecture answer should follow this chain:

```text
5 TB daily workload
        ↓
Single-machine feasibility assessment
        ↓
Distributed processing justified
        ↓
Object storage
        ↓
Spark application
        ↓
Driver
        ↓
Cluster manager
        ↓
Worker resources
        ↓
Executors
        ↓
Partitions
        ↓
Tasks
        ↓
Parallel execution
        ↓
Failures / retries / recomputation
        ↓
Completion within processing window
```

The exact number of workers, executors, cores, and partitions cannot be selected responsibly without workload measurements and infrastructure constraints.

The architectural reasoning comes first.

---

# Part XXVII — Mastery Checkpoint

## 90. Mastery Checklist

Before moving to Topic 02, you should be able to check every item below.

### Distributed Computing

- [ ] Explain why distributed computing exists.
- [ ] Explain CPU, RAM, disk, and processing-time limits.
- [ ] Explain vertical scaling.
- [ ] Explain horizontal scaling.
- [ ] Explain scale-up vs scale-out.
- [ ] Explain shared-nothing architecture.
- [ ] Explain the trade-offs of distribution.

### Spark Architecture

- [ ] Explain a Spark application.
- [ ] Explain the driver.
- [ ] Explain an executor.
- [ ] Explain a worker node.
- [ ] Explain a cluster manager.
- [ ] Explain the difference between worker and executor.
- [ ] Explain the relationship between driver and executors.

### Execution Model

- [ ] Explain partitions.
- [ ] Explain cores/task slots.
- [ ] Explain tasks.
- [ ] Explain jobs.
- [ ] Explain stages.
- [ ] Explain the application → job → stage → task → partition model.
- [ ] Explain execution waves.
- [ ] Explain the conceptual role of shuffle boundaries.

### Distributed Systems

- [ ] Explain data locality.
- [ ] Explain why cloud object storage changes locality assumptions.
- [ ] Explain lineage.
- [ ] Explain task retry.
- [ ] Explain executor failure.
- [ ] Explain lost-partition recomputation.
- [ ] Explain speculative execution.
- [ ] Explain stragglers.

### PySpark Internals

- [ ] Explain Python driver code.
- [ ] Explain the Spark JVM.
- [ ] Explain Py4J.
- [ ] Explain Python workers.
- [ ] Explain serialization/process-boundary overhead.
- [ ] Explain why built-in Spark expressions can execute in the JVM.
- [ ] Explain Arrow's conceptual role.
- [ ] Explain the architecture of a Python UDF at a high level.

### Spark Connect

- [ ] Explain classic PySpark architecture.
- [ ] Explain Spark Connect architecture.
- [ ] Explain the client/server boundary.
- [ ] Explain why Spark Connect is different from SSH.
- [ ] Explain the RDD API limitation.

### Cluster Managers

- [ ] Explain local mode.
- [ ] Explain Spark Standalone.
- [ ] Explain YARN.
- [ ] Explain Kubernetes.
- [ ] Explain managed Spark platforms conceptually.
- [ ] Compare their roles without confusing resource management with Spark computation.

### Architecture Decisions

- [ ] Explain when Spark is appropriate.
- [ ] Explain when Spark is unnecessary.
- [ ] Compare Spark with single-node processing conceptually.
- [ ] Explain operational and cost trade-offs.

### Practical Mastery

- [ ] Run the `hello_cluster.py` lab.
- [ ] Run a Spark application in local mode.
- [ ] Run it on a small standalone cluster.
- [ ] Identify application, jobs, stages, tasks, and executors in the Spark UI.
- [ ] Observe executor/worker failure behaviour.
- [ ] Compare Spark with DuckDB or Polars.
- [ ] Explain the complete architecture aloud without notes.

---

# Part XXVIII — Key Takeaways

## 91. The Mental Model to Remember

The most important model in this topic is:

```text
                    Spark Application
                           │
                           ▼
                        Driver
                           │
                    Cluster Manager
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
       Worker 1         Worker 2         Worker 3
          │                │                │
       Executor         Executor         Executor
          │                │                │
       Task slots       Task slots       Task slots
          │                │                │
       Partitions       Partitions       Partitions
```

And the execution hierarchy is:

```text
Application
   ↓
Job
   ↓
Stage
   ↓
Task
   ↓
Partition
```

The relationship is not simply:

```text
"Spark = pandas on many machines."
```

A better mental model is:

```text
Distributed data
      ↓
Partitions
      ↓
Tasks
      ↓
Executor resources
      ↓
Workers
      ↓
Cluster
```

with the driver coordinating the application.

---

## 92. The Production Mental Model

When looking at a Spark workload, ask:

```text
1. Why does this need distribution?
2. Where is the driver?
3. Where are the executors?
4. Which cluster manager allocates resources?
5. How is the data partitioned?
6. How many tasks can run concurrently?
7. Where can data move across machines?
8. What happens if an executor fails?
9. What happens if a task becomes a straggler?
10. Where does Python cross the JVM boundary?
11. Is Spark actually necessary?
```

These questions form the foundation for the rest of Module 2.14.

---

# 93. Glossary

| Term | Meaning |
|---|---|
| **Application** | The complete Spark application being executed. |
| **Driver** | The coordinating process for a Spark application. |
| **Executor** | An application-associated process that executes distributed tasks. |
| **Worker node** | A machine that provides resources for Spark execution. |
| **Cluster manager** | Resource-management layer that allocates CPU/memory and places application resources. |
| **Partition** | A logical portion of distributed data and a unit of parallel processing. |
| **Task** | A unit of work that processes a partition for a stage. |
| **Job** | A unit of Spark execution triggered by an action. |
| **Stage** | A portion of a job separated by dependencies such as shuffle boundaries. |
| **Task slot** | Conceptual execution capacity provided by executor cores for concurrent tasks. |
| **Lineage** | Information describing how derived data was produced so lost work can be recomputed. |
| **Straggler** | An unusually slow task that can delay stage completion. |
| **Speculative execution** | Running an additional attempt of a slow task to mitigate stragglers. |
| **Py4J** | A bridge used by classic PySpark to communicate between Python and JVM components. |
| **Python worker** | A Python process used for Python-specific execution on executors. |
| **Arrow** | A columnar data-interchange mechanism used for efficient data movement in supported Python/JVM workflows. |
| **Spark Connect** | Spark's client/server architecture in which a client communicates with a remote Spark server. |
| **Shared-nothing** | Architecture in which machines have independent CPU, memory, and local resources and communicate over a network. |
| **Data locality** | Executing computation close to the data to reduce data movement. |
| **Shuffle** | Redistribution of data between partitions/machines; introduced here as an execution boundary concept and covered deeply later. |
| **Local mode** | Spark execution using resources on one machine. |
| **Spark Standalone** | Spark's own cluster-management system. |
| **YARN** | A resource-management system widely used in Hadoop ecosystems. |
| **Kubernetes** | Container orchestration platform capable of managing Spark driver and executor workloads. |

---

# 94. Topic 01 Completion Standard

You are ready for **Topic 02 — SparkSession, Configuration, and Deploy Modes** only when you can explain, without notes:

```text
Why distributed computing exists
        ↓
Vertical vs horizontal scaling
        ↓
Shared-nothing architecture
        ↓
Spark application
        ↓
Driver
        ↓
Cluster manager
        ↓
Workers
        ↓
Executors
        ↓
Partitions
        ↓
Tasks
        ↓
Stages
        ↓
Jobs
        ↓
Fault tolerance
        ↓
PySpark Python/JVM boundary
        ↓
Spark Connect
        ↓
When Spark should NOT be used
```

You should also be able to run the cluster lab and explain what you observe.

The goal is not to memorize these words.

The goal is to be able to reason about a Spark system as an engineer.
