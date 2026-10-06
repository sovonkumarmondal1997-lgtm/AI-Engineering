# Resource Limits and Laptop Capacity

> **Stage 2B — Docker Essentials for Data Labs**  
> **Topic 08 — Resource Limits and Laptop Capacity**  
> **Phase D — Keeping Your Machine Healthy**

This module teaches how to measure, limit, budget, and safely operate Docker-based Data Engineering workloads on a finite development machine.

The central mental model is:

```text
Laptop Capacity
      ↓
Docker / WSL2 Available Capacity
      ↓
Container Resource Usage
      ↓
Per-Container Limits
      ↓
Stack Footprint
      ↓
Capacity Budget
      ↓
Safe Local Data Engineering Lab
```

The goal is not merely to make containers start. The goal is to make them run **comfortably, predictably, and safely**.

---

## 1. Learning Objectives

By the end of this module, you should be able to:

- Explain why a laptop has finite CPU and memory capacity.
- Distinguish physical host capacity from capacity available to Docker.
- Explain how Docker Desktop and WSL2 can affect available capacity.
- Understand the Linux host case.
- Measure container resource consumption with `docker stats`.
- Interpret CPU, memory, network I/O, block I/O, and PID information.
- Distinguish idle usage from loaded usage.
- Set per-container memory limits with `--memory`.
- Set CPU limits with `--cpus`.
- Explain what happens when memory limits are exceeded.
- Recognize exit code `137` as an important diagnostic clue while avoiding the assumption that it proves an OOM event by itself.
- Explain CPU throttling and why CPU pressure normally slows work rather than killing the container.
- Understand JVM memory in Kafka, Spark, Flink, and other JVM-based Data Engineering services.
- Explain why JVM heap must fit inside the container memory limit with deliberate headroom.
- Estimate the approximate memory footprint of a multi-service Data Engineering stack.
- Build a personal laptop lab budget.
- Use only the services required for a particular exercise.
- Understand Compose profiles at an operational level.
- Stop idle stacks and services.
- Explain swap and why excessive swap can make a machine appear to hang.
- Decide when a workload should move from a laptop to a cloud VM.
- Compare local convenience and capacity against cloud cost and operational overhead.
- Conduct safe resource-limit experiments.
- Measure first, estimate second, and make capacity decisions from evidence.

---

## 2. Why Laptop Capacity Matters in Data Engineering

Data Engineering laboratories are unusually good at consuming local resources because a realistic workflow often requires several infrastructure services simultaneously.

A small exercise might need:

```text
PostgreSQL
+
Redis
```

A larger exercise might need:

```text
PostgreSQL
+
MinIO
+
Redis
+
Kafka
+
Schema Registry
```

A more ambitious streaming or distributed-processing lab might add:

```text
Spark
+
Flink
+
Airflow
+
Monitoring
```

The resource footprint can grow quickly.

### A useful comparison

A laptop may be perfectly comfortable running:

```text
PostgreSQL + Redis
```

and become uncomfortable when asked to run:

```text
Kafka + Spark + Airflow + Flink
```

at the same time.

That does not mean Docker is broken.

It means the workload is approaching the physical limits of the machine.

### "It runs" versus "it runs comfortably"

These are different engineering outcomes.

```text
"It runs"
    ↓
Containers start
    ↓
Some commands work
```

versus:

```text
"It runs comfortably"
    ↓
Services are responsive
    ↓
CPU has headroom
    ↓
Memory has headroom
    ↓
The OS remains responsive
    ↓
Workloads behave predictably
```

A professional local lab should target the second state.

### The fundamental equation

```text
Total available resources
        -
OS / Docker overhead
        -
Other applications
        -
Container workloads
        =
Remaining capacity
```

Then:

```text
Remaining capacity
        ↓
Can the next Data Engineering service safely run?
```

This is the beginning of capacity planning.

---

## 3. CPU and Memory Fundamentals

Only the operating-system concepts needed for Docker resource management are covered here.

### 3.1 CPU

The CPU executes instructions.

A machine may have:

```text
2 cores
4 cores
8 cores
12 cores
16 cores
```

or more.

Modern CPUs may also expose logical processors/threads, so the exact number reported by the operating system is not always the same as the number of physical cores.

Check the logical processor count on Linux with:

```bash
nproc
```

### CPU utilization

CPU utilization describes how much processor capacity a workload is using.

Conceptually:

```text
Low CPU usage
    ↓
CPU has spare capacity
```

and:

```text
High CPU usage
    ↓
CPU is doing substantial work
```

High CPU is not automatically bad.

A CPU-heavy batch job may intentionally use most available CPU.

The engineering question is:

> Is the CPU usage appropriate for the workload, and is the machine still responsive?

### CPU contention

Suppose three containers simultaneously need CPU:

```text
Container A → CPU demand
Container B → CPU demand
Container C → CPU demand
```

If their combined demand exceeds the available CPU:

```text
CPU contention
```

occurs.

The workloads compete for processor time.

### CPU throttling

When a container has a CPU limit, Docker/runtime controls how much CPU time it can consume.

If the workload wants more than its allowed share:

```text
CPU demand
    >
CPU allowance
    ↓
throttling
    ↓
slower execution
```

CPU throttling is therefore different from memory exhaustion.

---

## 4. Memory

Memory, usually RAM, holds data and program state needed by actively running processes.

Examples include:

```text
PostgreSQL process memory
Kafka JVM memory
Python process memory
Docker runtime overhead
OS memory
```

### Memory allocation

Applications request memory as they work.

A service can therefore have a small baseline footprint and a substantially larger loaded footprint.

For example, these values are illustrative:

```text
PostgreSQL
Idle:   200 MB
Loaded: 700 MB
```

The exact values depend on:

- image;
- configuration;
- workload;
- operating system;
- dataset;
- caching;
- runtime behavior.

Do not treat illustrative values as universal benchmarks.

### Memory pressure

Memory pressure occurs when available memory becomes constrained.

A rough progression is:

```text
Normal memory use
      ↓
Available memory decreases
      ↓
Memory pressure
      ↓
Swap may increase
      ↓
Performance can degrade severely
      ↓
Processes may eventually fail or be killed
```

### Why memory exhaustion is particularly dangerous

CPU contention often means:

```text
work becomes slower
```

Memory exhaustion can mean:

```text
process/container terminates
```

or, before that:

```text
system becomes extremely slow
```

because of heavy memory-management and swap activity.

---

## 5. Host Capacity vs Docker Capacity

Always distinguish:

```text
Physical machine capacity
        ↓
Operating system
        ↓
Docker Desktop / WSL2 / Docker Engine
        ↓
Available container capacity
        ↓
Individual container limits
```

The exact hierarchy depends on the host platform.

### Native Linux

When Docker Engine runs directly on Linux, containers generally operate much closer to the host's physical resources.

That does not mean containers automatically get unlimited resources.

Per-container limits can still restrict them.

### Docker Desktop on Windows/macOS

Docker Desktop uses a managed runtime environment rather than simply exposing every host resource directly to Linux containers.

The practical result is:

```text
Laptop RAM
    ≠ necessarily
RAM available to containers
```

and:

```text
Laptop CPU capacity
    ≠ necessarily
CPU capacity configured for the container runtime
```

### Why this matters

If a laptop has substantial RAM but the Docker runtime is configured with a smaller memory boundary, the containers cannot simply assume the full physical RAM is available.

Capacity planning must therefore begin with the **effective runtime capacity**, not just the specification printed on the laptop box.

---

## 6. Docker Desktop Capacity

On Windows and macOS, Docker Desktop provides the environment in which Linux containers run.

The exact UI and resource-management model can vary by Docker Desktop release and platform, so do not memorize a particular settings screen.

Instead, understand the operational question:

> How much CPU and memory can the Docker runtime actually use right now?

### Capacity layers

Conceptually:

```text
Physical laptop
      ↓
Host operating system
      ↓
Docker Desktop runtime
      ↓
Containers
```

If the runtime has an intermediate resource boundary, that boundary matters to every container.

### Practical verification

Start with Docker runtime information:

```bash
docker info
```

Then measure actual running containers:

```bash
docker stats
```

The combination gives you a better operational picture than relying only on host specifications.

### Docker Desktop resource settings

If your Docker Desktop environment exposes explicit CPU or memory allocation controls, document the selected values.

Record:

```text
Host RAM:
Host logical CPUs:
Docker runtime memory:
Docker runtime CPU:
```

Then document why the selected capacity is appropriate for the current lab.

### Important principle

Do not maximize Docker's allocation simply because the slider allows it.

The host also needs resources for:

- the operating system;
- browser;
- IDE;
- terminal;
- database clients;
- documentation;
- other applications.

The objective is a usable development machine, not maximum Docker consumption.

---

## 7. WSL2 Capacity

WSL2 is particularly relevant to Windows-based Data Engineering development.

The conceptual architecture is:

```text
Windows Host
     ↓
WSL2 Linux Environment
     ↓
Docker / Linux Container Runtime
     ↓
Containers
```

The exact architecture varies with the Docker Desktop configuration, but the resource-planning principle remains the same:

> Windows, WSL2, Docker, and containers participate in the same finite machine-resource budget.

### Why WSL2 matters

If WSL2 has a configured resource boundary or is under memory pressure, the Data Engineering stack running through that environment is affected.

You should therefore distinguish:

```text
Windows host RAM
```

from:

```text
effective Linux/Docker capacity
```

### Practical approach

Do not rely on an old screenshot or fixed UI path.

Instead:

1. Identify the current Docker/WSL2 configuration.
2. Determine the effective memory/CPU available to the runtime.
3. Measure running workloads.
4. Document the selected resource budget.

### Platform boundary

Topic 10 covers broader Docker Desktop, WSL2, and platform differences.

This topic only uses WSL2 where it directly affects:

```text
resource availability
+
capacity planning
+
Data Engineering lab behavior
```

---

## 8. Linux Host Capacity

On Linux, Docker Engine commonly runs directly on the host.

Start with basic host capacity:

```bash
free -h
```

This provides a human-readable view of memory.

Check logical CPU count:

```bash
nproc
```

You can also inspect CPU details with:

```bash
lscpu
```

and memory information with:

```bash
cat /proc/meminfo
```

These are diagnostic tools, not a complete Linux performance course.

### Host versus container

A Linux machine might have:

```text
Host RAM: 32 GB
```

while a container is configured with:

```text
Memory limit: 2 GB
```

The container does not get 32 GB simply because the host has 32 GB.

Think:

```text
Host capacity
      ↓
Container resource boundary
      ↓
Application
```

### Why this distinction matters

A container may be resource-constrained even while the host still has substantial free capacity.

Conversely, a host can be under memory pressure even when no individual container appears to be using a huge amount.

Both levels must be considered.

---

## 9. Measuring Resources with `docker stats`

The primary measurement command for this module is:

```bash
docker stats
```

It continuously reports resource usage for running containers.

To inspect one container:

```bash
docker stats <container>
```

Example:

```bash
docker stats postgres
```

### Important columns

Typical output includes:

- `CPU %`
- `MEM USAGE / LIMIT`
- `MEM %`
- `NET I/O`
- `BLOCK I/O`
- `PIDS`

The exact presentation can vary by Docker version.

### Why `docker stats` matters

Without measurement:

```text
"I think Kafka uses a lot of memory."
```

With measurement:

```text
"Kafka currently uses approximately X memory under this workload."
```

The second statement is more useful for capacity planning.

### Example

Illustrative output might conceptually look like:

```text
CONTAINER   CPU %   MEM USAGE / LIMIT    MEM %   NET I/O    BLOCK I/O
postgres    2.1%    210MiB / 2GiB        10%     ...        ...
redis       0.4%     18MiB / 512MiB       4%     ...        ...
kafka       6.5%    780MiB / 2GiB        39%     ...        ...
```

These numbers are illustrative, not benchmarks.

### Operational interpretation

Do not simply record the largest number.

Ask:

```text
Is this idle or loaded?
Is the container approaching its limit?
Is CPU usage expected?
Is memory growing?
Is network traffic expected?
Is block I/O unusually high?
```

---

## 10. Understanding CPU Usage

CPU reporting can be confusing because the meaning of a percentage depends on the runtime and reporting model.

### Key ideas

- CPU usage represents processor consumption.
- Multi-core systems can produce values above 100% depending on how Docker reports CPU usage.
- CPU percentage should be interpreted in context.
- A high percentage is not automatically a failure.
- Sustained high CPU across multiple services can indicate contention.

### Example

Suppose:

```text
Kafka: 80% CPU
PostgreSQL: 40% CPU
Python: 70% CPU
```

That does not automatically mean the machine is broken.

Ask:

```text
How many CPUs are available?
Are these values sustained?
What workload is running?
Is the host responsive?
Are other services waiting for CPU?
```

### CPU measurement exercise

Run:

```bash
docker stats
```

Record:

```text
Service
CPU at idle
CPU under workload
```

Then compare the values.

---

## 11. Understanding Memory Usage

The most important memory display is:

```text
MEM USAGE / LIMIT
```

For example:

```text
512 MB / 1 GB
```

means approximately half of the configured container memory limit is currently being used.

The associated percentage is approximately:

```text
512 MB
---------
1 GB

≈ 50%
```

The exact displayed value depends on Docker's accounting and units.

### Why the limit matters

Suppose two containers each use:

```text
500 MB
```

Container A:

```text
500 MB / 1 GB
```

Container B:

```text
500 MB / 8 GB
```

The absolute usage is the same.

The capacity risk is not.

Container A is much closer to its configured boundary.

### Memory percentage as a pressure signal

High memory percentage should trigger a question:

```text
Is the workload expected to use this much?
```

If the service normally runs at 40% and suddenly approaches 95%, investigate.

If the service is intentionally configured to use most of its limit for a bounded workload, the interpretation may be different.

---

## 12. Idle vs Loaded Resource Usage

This is one of the most important capacity-planning concepts.

### Idle

A service is running but doing little work.

Example:

```text
Kafka
Idle memory = measured value
Idle CPU = measured value
```

### Loaded

The service is processing a realistic workload.

Example:

```text
Kafka
Loaded memory = measured value
Loaded CPU = measured value
```

### Why both matter

Suppose:

```text
Service
Idle:   250 MB
Loaded: 1.1 GB
```

If you plan the lab using only:

```text
250 MB
```

you may badly underestimate the real footprint.

### Capacity planning rule

> **Idle measurements describe baseline cost; loaded measurements describe workload capacity.**

### Recommended measurement process

```text
Start service
    ↓
Wait for initialization
    ↓
Record idle usage
    ↓
Run realistic workload
    ↓
Record loaded usage
    ↓
Compare
    ↓
Use the measurements in the capacity budget
```

---

## 13. Building a Capacity Table

Create a table from real measurements.

| Service | Idle Memory | Loaded Memory | CPU Idle | CPU Loaded | Proposed Limit |
|---|---:|---:|---:|---:|---:|
| PostgreSQL | measure | measure | measure | measure | choose |
| MinIO | measure | measure | measure | measure | choose |
| Redis | measure | measure | measure | measure | choose |
| Kafka | measure | measure | measure | measure | choose |
| Schema Registry | measure | measure | measure | measure | choose |

### Three types of numbers

Always label numbers as one of:

```text
Measured
Estimated
Illustrative
```

For example:

```text
Kafka loaded memory:
Measured: 1.05 GB
```

is fundamentally different from:

```text
Kafka expected memory:
Estimated: 1.2 GB
```

and:

```text
Kafka example:
Illustrative: 1.2 GB
```

Never present an invented number as a universal benchmark.

### Why the table matters

This table becomes the foundation for:

```text
stack footprint
      ↓
laptop budget
      ↓
profile selection
      ↓
cloud decision
```

---

## 14. Per-Container Memory Limits

Docker can constrain container memory.

Example:

```bash
docker run --memory=512m <image>
```

This establishes a memory boundary for the container.

### Why use memory limits?

Memory limits can:

- prevent one workload from consuming an uncontrolled amount of memory;
- make experiments predictable;
- expose bad sizing assumptions;
- protect the rest of a local lab;
- make resource behavior easier to study.

### Important distinction

A memory limit is a **resource boundary**, not a guarantee that the application will efficiently use that memory.

For example:

```text
--memory=2g
```

does not mean:

```text
"Give my application exactly 2 GB of useful application memory."
```

It means approximately:

```text
"Constrain this container to this memory boundary under Docker's memory accounting."
```

The application, runtime, libraries, and operating system behavior still matter.

---

## 15. Memory Limit Units

Common Docker memory suffixes include:

```text
m
g
```

Examples:

```bash
docker run --memory=512m <image>
```

and:

```bash
docker run --memory=1g <image>
```

### Read them as

```text
512m ≈ 512 megabytes
1g   ≈ 1 gigabyte
```

Use explicit, readable values when teaching and operating local labs.

### Practical rule

Do not choose:

```text
--memory=512m
```

because it "sounds reasonable."

Choose it because:

```text
Measured workload
+
application requirements
+
headroom
```

support the decision.

---

## 16. What Happens When Memory Limits Are Exceeded

The critical mental model is:

```text
Container memory usage
        ↓
Approaches limit
        ↓
Application requests more memory
        ↓
Memory pressure / OOM condition
        ↓
Process or container may be killed
```

The roadmap's key behavior is:

> **Memory limit exceeded → the container can be killed.**

### Exit code 137

An exit code of:

```text
137
```

is an important diagnostic signal.

It is commonly associated with:

```text
128 + 9
```

where signal 9 is `SIGKILL`.

An OOM-related kill can therefore result in exit code `137`.

However:

> **Do not claim that exit code 137 alone proves Docker OOM.**

Correlate the exit code with:

- container configuration;
- memory usage;
- runtime inspection;
- logs;
- host/runtime evidence;
- the workload being executed.

### Inspect the container

```bash
docker ps -a
```

Then:

```bash
docker inspect <container>
```

Look at the container state and resource-related information.

### Why this matters

The correct engineering question is not:

```text
"Did I see 137?"
```

It is:

```text
"Does the evidence support a memory/resource kill as the reason this process stopped?"
```

---

## 17. Memory-Limit Troubleshooting

Use a compact evidence-driven workflow:

```text
Container exits
      ↓
Check status
      ↓
Check exit code
      ↓
Check logs
      ↓
Inspect memory configuration
      ↓
Inspect workload
      ↓
Determine whether OOM/resource pressure is likely
      ↓
Fix sizing
      ↓
Re-run
      ↓
Verify
```

Useful commands:

```bash
docker ps -a
docker logs <container>
docker inspect <container>
docker stats
```

### Example

Suppose:

```text
Kafka exited
Exit code: 137
```

Do not immediately conclude:

```text
"Docker is broken."
```

Instead investigate:

```text
What was the memory limit?
What was the JVM heap?
What was the workload?
Was memory usage approaching the limit?
Was there evidence of an OOM kill?
```

Then fix the resource relationship.

---

## 18. CPU Limits

Docker can constrain CPU consumption.

Example:

```bash
docker run --cpus=0.5 <image>
```

Conceptually:

```text
CPU allowance
≈
half of one CPU core's worth of CPU time
```

subject to runtime scheduling and platform behavior.

### Why use CPU limits?

CPU limits can:

- keep a CPU-heavy experiment from monopolizing the laptop;
- make throttling behavior measurable;
- provide isolation between local services;
- improve predictability.

### Important distinction

A CPU limit is not the same thing as a CPU reservation.

This module focuses on:

```text
limiting CPU consumption
```

rather than production cluster scheduling semantics.

---

## 19. What Happens When CPU Limits Are Reached?

The core model is:

```text
CPU demand > CPU allowance
        ↓
CPU throttling
        ↓
Work progresses more slowly
```

Contrast this with memory:

```text
Memory over limit
→ possible kill / OOM behavior
```

versus:

```text
CPU demand over allowance
→ throttling / slower execution
```

### Why this distinction matters

Suppose a Python program takes:

```text
10 seconds
```

without a CPU constraint.

With:

```bash
--cpus=0.5
```

it may take substantially longer.

The process does not normally need to be killed simply because it wants more CPU than its limit.

It is constrained in how much CPU time it can consume.

---

## 20. CPU-Limit Experiment

The roadmap requires a CPU-heavy Python experiment.

### Objective

Measure the effect of:

```bash
--cpus=0.5
```

on a CPU-bound workload.

### Safe workload

Use a bounded computation.

For example, a Python program can perform repeated integer calculations for a fixed number of iterations.

Example conceptual program:

```python
total = 0

for i in range(50_000_000):
    total += (i * i) % 97

print(total)
```

Choose an iteration count appropriate for your machine. The experiment must remain bounded.

### Baseline

Run without the restrictive CPU limit.

Measure execution time:

```bash
time docker run --rm <cpu-test-image>
```

Record:

```text
CPU limit:
Execution time:
Observed CPU:
```

### Limited run

Run:

```bash
time docker run --rm --cpus=0.5 <cpu-test-image>
```

While it runs, observe:

```bash
docker stats
```

### Compare

Create:

| Run | CPU Limit | Runtime | Observation |
|---|---:|---:|---|
| Baseline | unrestricted / higher limit | measure | measure |
| Limited | `0.5` | measure | slower expected |

### Interpretation

The expected lesson is:

```text
Lower CPU allowance
        ↓
More throttling
        ↓
Longer execution time
```

The exact slowdown depends on the workload, host, runtime, and competing activity.

Do not expect a universal exact 2× runtime.

---

## 21. Memory-Limit Experiment

The memory experiment should be controlled and bounded.

### Objective

Observe a container failing because its configured memory boundary is too small for the workload.

### Safety requirement

Do not create an uncontrolled memory bomb.

Use a deliberately small container limit and a bounded workload that allocates memory in controlled increments.

### Experiment progression

```text
1. Start with a small limit.
2. Run a bounded memory workload.
3. Observe behavior.
4. Inspect the container state.
5. Inspect the exit status.
6. Inspect logs and runtime evidence.
7. Increase the memory limit.
8. Re-run.
9. Compare the outcomes.
```

### Example conceptual Python workload

```python
chunks = []

for _ in range(100):
    chunks.append(bytearray(10 * 1024 * 1024))

print("allocation completed")
```

This example can allocate substantial memory, so choose a lower iteration count or allocation size appropriate to the configured limit.

Do not run a workload that could consume uncontrolled host memory.

### What to record

```text
Memory limit:
Approximate workload:
Exit code:
Observed logs:
Container state:
Result after increasing limit:
```

### Key lesson

```text
Application demand
>
container memory boundary
```

can produce process/container termination.

---

## 22. JVM Services in Containers

Many important Data Engineering services use the JVM.

Examples include:

- Kafka;
- Spark;
- Flink;
- some catalog services;
- other JVM-based infrastructure.

The common mistake is to think:

```text
JVM memory
=
heap only
```

That is incomplete.

A better model is:

```text
Container memory limit
        ↓
JVM process
        ├── Heap
        ├── Non-heap memory
        ├── Native memory
        ├── Threads
        ├── Direct/off-heap buffers
        └── Runtime/process overhead
```

### Central rule

> **The JVM heap must fit inside the container memory limit with sufficient headroom for everything else.**

This is one of the most important capacity-management rules in this module.

---

## 23. JVM Heap vs Container Memory

Consider:

```text
Container memory limit = 1 GB
JVM heap = 1 GB
```

This is unsafe as a general sizing strategy.

Why?

Because the JVM process needs memory beyond the Java heap.

Conceptually:

```text
1 GB container
    ├── 1 GB heap
    ├── native memory
    ├── threads
    ├── direct buffers
    └── runtime overhead
```

The total demand can exceed the container boundary.

### Better conceptual sizing

For example:

```text
Container limit = 2 GB

JVM heap = 1.0–1.3 GB
Remaining capacity = headroom
```

These values are illustrative.

There is no universal rule that says:

```text
"Always allocate exactly 60% to heap."
```

Actual sizing depends on:

- application;
- JVM version;
- workload;
- concurrency;
- buffers;
- framework;
- configuration;
- container environment.

### Professional principle

> **Treat the container limit as the outer budget and the JVM heap as only one line item inside that budget.**

---

## 24. Kafka JVM Sizing

Kafka is an excellent example because it is commonly used in Data Engineering labs and is JVM-based.

Conceptually:

```text
Kafka container
      ↓
JVM
      ↓
Heap
+
Non-heap/native memory
+
Network buffers
+
Threads
+
Other process overhead
```

### Unsafe relationship

```text
Container limit = 1 GB
JVM heap = 1 GB
```

The heap consumes essentially the entire outer budget before accounting for the rest of the process.

### Better relationship

```text
Container limit
      >
JVM heap
      +
required overhead
      +
headroom
```

### Image-specific configuration

Different Kafka images/distributions expose JVM sizing through different environment variables or configuration mechanisms.

Therefore:

> **Always read the image documentation and existing Compose configuration before assuming a variable name.**

Do not treat a generic environment variable as universal across Kafka images.

### Required experiment

The roadmap asks you to:

1. Run Kafka with a memory limit smaller than its configured heap.
2. Observe the failure.
3. Inspect the evidence.
4. Fix the heap/container relationship.
5. Re-run.
6. Verify stability.

The learning objective is not a particular Kafka tuning value.

It is:

```text
Container memory
      ↓
JVM heap
      ↓
non-heap overhead
      ↓
headroom
```

must be coherent.

---

## 25. Spark and Flink JVM Awareness

Spark and Flink introduce additional complexity.

A simplistic model:

```text
Spark/Flink memory
=
heap
+
framework overhead
+
off-heap/native/direct memory
+
process overhead
```

Therefore:

```text
container limit
```

must account for the total process footprint, not merely a single heap number.

### Important boundary

This module does not become a complete Spark or Flink memory-management course.

You only need enough awareness to answer:

```text
Will this framework fit safely inside the container's memory boundary?
```

### Practical implication

If a laptop is already close to capacity with:

```text
Kafka
+
PostgreSQL
+
MinIO
```

adding:

```text
Spark
+
Flink
```

may produce significant contention even if each service can individually start.

---

## 26. Application Memory vs Container Memory

Distinguish two layers.

### Application setting

Examples:

```text
JVM heap
Spark memory configuration
Flink memory configuration
Python process behavior
```

### Container setting

Example:

```bash
--memory=2g
```

The relationship is:

```text
Application memory configuration
        ↓
must fit within
        ↓
Container memory limit
        ↓
must fit within
        ↓
Available runtime capacity
        ↓
must fit within
        ↓
Laptop capacity
```

### Why this matters

If you set:

```text
JVM heap = 4 GB
```

but:

```text
container limit = 2 GB
```

the configuration is incoherent.

If:

```text
container limit = 8 GB
```

but the laptop's Docker runtime only has:

```text
4 GB
```

of effective capacity remaining, the stack is still not viable.

Capacity must be reasoned about at every layer.

---

## 27. Capacity Estimation

The first approximation is:

```text
Stack footprint
≈
sum of service resource requirements
```

For example, these are **illustrative values only**:

```text
PostgreSQL   500 MB
MinIO        300 MB
Redis        100 MB
Kafka        1.2 GB
Registry     500 MB
--------------------
Approx       2.6 GB
```

Do not treat these as benchmarks.

### Add the missing budget categories

A realistic laptop budget must also account for:

```text
Service footprint
+
Docker/WSL2 overhead
+
OS usage
+
IDE/browser/other applications
+
workload growth
+
headroom
```

Therefore:

```text
Safe lab budget
>
simple sum of service idle footprints
```

### Why this is only an estimate

Resource use changes with:

- workload;
- data volume;
- concurrency;
- caching;
- JVM behavior;
- application configuration;
- runtime;
- platform.

Capacity estimation should therefore be continuously improved with measurements.

---

## 28. Idle vs Loaded Capacity Planning

Use the following model:

```text
Expected stack footprint
=
idle baseline
+
workload growth
+
headroom
```

This is a conceptual planning model, not a mathematical guarantee.

### Idle baseline

Useful for:

```text
"What does this stack cost just to remain running?"
```

### Loaded footprint

Useful for:

```text
"What does this stack cost during the actual exercise?"
```

### Headroom

Headroom protects against:

- bursts;
- unexpected allocations;
- application initialization;
- cache growth;
- workload variation;
- other host activity.

Do not use a universal headroom percentage as a law.

A small deterministic lab and a volatile streaming workload need different margins.

---

## 29. CPU Capacity Planning

Apply the same discipline to CPU.

Consider:

- logical CPU count;
- baseline host usage;
- service demand;
- CPU limits;
- contention;
- burst workloads.

### Example

Suppose a machine has:

```text
8 logical CPUs
```

and currently:

```text
OS + IDE + browser
```

consume meaningful CPU.

It would be incorrect to reason:

```text
"I have 8 CPUs, therefore I can run any eight containers."
```

Container count is not capacity.

Workload demand is capacity.

### Better model

```text
Host CPU capacity
      -
background CPU demand
      -
service CPU demand
      -
burst/headroom requirement
      =
usable CPU budget
```

---

## 30. Full Stage 2 Streaming Stack Estimation

The learner should estimate the footprint of a larger Stage 2 streaming stack.

Start with measured services:

```text
PostgreSQL
MinIO
Redis
Kafka
Schema Registry
```

Then add other services required by the current Stage 2 exercise, such as Spark, Flink, or Airflow when applicable.

### Separate three categories

```text
Measured
```

Values obtained from `docker stats` during a real workload.

```text
Estimated
```

Values predicted from previous observations or reasonable assumptions.

```text
Illustrative
```

Values used only to explain the method.

### Example planning table

| Service | Measurement Type | Idle Memory | Loaded Memory | Planning Value |
|---|---|---:|---:|---:|
| PostgreSQL | measured | record | record | choose |
| MinIO | measured | record | record | choose |
| Redis | measured | record | record | choose |
| Kafka | measured | record | record | choose |
| Schema Registry | measured/estimated | record | record | choose |
| Spark | estimated | record | record | choose |
| Flink | estimated | record | record | choose |
| Airflow | estimated | record | record | choose |

The point is not to manufacture a precise number.

The point is to construct a transparent capacity model.

---

## 31. Personal Laptop Lab Budget

Create a personal Data Engineering lab budget.

Example structure:

```text
Laptop RAM: 16 GB

OS / other applications reserve: ______

Docker / WSL2 effective capacity: ______

Safe local lab budget: ______
```

Then define profiles.

### Profile A — SQL

```text
PostgreSQL
```

### Profile B — Object storage

```text
PostgreSQL
+
MinIO
+
Redis
```

### Profile C — Streaming

```text
Kafka
+
required dependencies
+
PostgreSQL if required
```

### Profile D — Full streaming stack

```text
PostgreSQL
+
MinIO
+
Redis
+
Kafka
+
Schema Registry
+
other required services
```

The learner decides which combinations are safe using measurements.

### Important principle

> **Do not copy another person's laptop budget. Measure your own environment.**

---

## 32. Running Only the Services You Need

A common beginner mistake is:

> "I have a Compose file containing 12 services, so I should run all 12."

That is unnecessary.

The better workflow is:

```text
Exercise
   ↓
Identify required services
   ↓
Start only those services
   ↓
Stop everything else
```

### SQL exercise

Run:

```text
PostgreSQL
```

### Object-storage exercise

Run:

```text
MinIO
```

plus any actual dependency.

### Streaming exercise

Run:

```text
Kafka
+
required dependencies
```

### Distributed-processing exercise

Run:

```text
Spark/Flink
+
only required infrastructure
```

### Why this matters

Every running service has some resource footprint.

Reducing unnecessary services:

```text
smaller memory footprint
+
less CPU contention
+
less background I/O
+
better laptop responsiveness
```

This is one of the easiest capacity optimizations because it requires no hardware upgrade.

---

## 33. Stopping Idle Stacks

Use:

```bash
docker compose stop
```

when you want to stop services without tearing down their runtime objects.

Or target individual services when appropriate:

```bash
docker compose stop kafka
```

### Why this matters

A heavy stack left running for days may continuously consume:

- memory;
- CPU;
- network resources;
- block I/O;
- background application activity.

The laptop may appear slower even when you are not actively using the Data Engineering stack.

### Good operational habit

```text
Finish exercise
      ↓
Stop unused heavy services
      ↓
Continue normal laptop work
```

### Common mistake

> Leaving heavy stacks running in the background for days.

Treat local infrastructure as infrastructure that should have an operational lifecycle.

---

## 34. Compose Profiles

Compose profiles can group optional services.

Conceptually:

```text
core
streaming
analytics
```

For example:

```text
core profile
    ↓
PostgreSQL + Redis

streaming profile
    ↓
Kafka + Schema Registry

analytics profile
    ↓
Spark-related services
```

The exact service grouping depends on the project's Compose file.

### Operational use

If the provided stack defines profiles, inspect them and run only the profile required for the exercise.

For example:

```bash
docker compose --profile streaming up -d
```

The exact profile name must match the Compose configuration.

### Important boundary

This module teaches how to **read and use** profiles.

It does not become an advanced Compose-authoring lesson.

### Capacity benefit

Profiles create an operational boundary:

```text
Exercise
    ↓
Required profile
    ↓
Required services
    ↓
Smaller resource footprint
```

---

## 35. Swap

Swap uses storage as an extension of memory when RAM pressure occurs.

Conceptually:

```text
RAM
 ↓
Memory pressure
 ↓
Swap activity
 ↓
Storage I/O
 ↓
Much slower execution
```

### Important point

Swap is not equivalent to RAM.

RAM is fast working memory.

Storage is much slower.

Therefore:

```text
More swap
≠
More free RAM
```

### Why swap can be useful

Swap can sometimes prevent immediate process failure when memory pressure occurs.

But that does not mean the machine remains performant.

A workload can survive while becoming painfully slow.

---

## 36. Why a Lab Can Appear to Hang

A Data Engineering lab may appear frozen even though processes have not crashed.

One possible chain is:

```text
High memory pressure
+
Swap activity
+
Heavy I/O
+
CPU contention
=
Machine appears to hang
```

### Important distinction

```text
Crash
```

means a process failed or was terminated.

```text
Hang-like behavior
```

can mean the system is technically still working but making extremely slow progress.

### Symptoms may include

- terminal commands take a long time;
- Docker commands respond slowly;
- IDE becomes sluggish;
- browser tabs become unresponsive;
- services take minutes to respond;
- disk activity becomes unusually high.

### Investigation

Check container usage:

```bash
docker stats
```

Check host memory:

```bash
free -h
```

Check CPU:

```bash
nproc
```

and use platform-appropriate host monitoring tools.

### Professional lesson

> **Do not interpret every slow system as an application bug. First ask whether the machine is under resource pressure.**

---

## 37. Swap vs OOM

These behaviors are related but different.

### Swap pressure

May cause:

- extreme slowness;
- high storage I/O;
- poor responsiveness;
- long pauses.

### OOM-related termination

May cause:

- process/container termination;
- exit code clues such as `137`;
- application failure.

They are not mutually exclusive.

A machine can experience:

```text
memory pressure
      ↓
swap activity
      ↓
continued pressure
      ↓
eventual process/container failure
```

depending on platform and runtime behavior.

### Operational lesson

```text
Swap can delay failure
```

but:

```text
swap does not create additional high-performance RAM
```

---

## 38. Safe Resource Experiments

Resource experiments should teach behavior without destabilizing the host.

### Never intentionally

- consume all host RAM;
- freeze the operating system;
- create uncontrolled disk exhaustion;
- use fork bombs;
- permanently disable system resources;
- corrupt persistent data;
- deliberately destabilize the machine.

### Safe strategy

Use:

```text
small limits
+
bounded workloads
+
short experiments
+
continuous observation
```

### Experiment progression

```text
Measure
  ↓
Apply small constraint
  ↓
Observe
  ↓
Interpret
  ↓
Restore
  ↓
Verify
```

The goal is understanding, not damage.

---

## 39. Moving Workloads to a Cloud VM

Eventually, a laptop may no longer be the appropriate execution environment.

Ask:

- How much RAM does the laptop have?
- How many CPUs are available?
- How long does the workload run?
- Does the workload need to stay online?
- Is the full stack required simultaneously?
- Can the stack be reduced?
- Is collaboration required?
- Is a stable network endpoint required?
- Is the workload worth paying to run remotely?

### First attempt: reduce the workload

Before moving to the cloud:

```text
Can I run fewer services?
```

Then:

```text
Can I use profiles?
```

Then:

```text
Can I stop idle services?
```

Then:

```text
Can I apply sensible resource limits?
```

Only then ask:

```text
Should this move to a remote VM?
```

### Cloud is not automatically better

Cloud provides:

- remote capacity;
- dedicated/controlled resources;
- longer-running environments;
- collaboration possibilities;
- networking options.

But it also introduces:

- recurring cost;
- network latency;
- administration;
- security responsibilities;
- data transfer considerations;
- potential idle charges.

---

## 40. Cloud VM Cost Trade-Off

Compare the two environments.

### Laptop

```text
Laptop
+
Already purchased
+
Local convenience
+
No per-hour compute bill
+
Finite capacity
+
Shares resources with daily work
```

### Cloud VM

```text
Cloud VM
+
Pay-as-you-go capacity
+
Remote access
+
Potentially more predictable resources
+
Can run while laptop is off
-
Recurring cost
-
Network dependency
-
Security/maintenance responsibility
```

### Decision principle

The right question is not:

> "Is cloud more powerful?"

The right question is:

> **"Is the value of predictable additional capacity worth the recurring cost and operational overhead?"**

### Example decision

If a lab runs for:

```text
20 minutes
```

a laptop may be ideal.

If a service needs to run:

```text
24 hours/day
```

for a collaborative experiment, a small VM may become more sensible.

The correct answer depends on workload and economics.

---

## 41. Capacity Decision Framework

Use this decision tree:

```text
Does workload fit comfortably on laptop?
          │
        YES
          ↓
     Run locally
          │
         NO
          ↓
Can services be reduced?
          │
        YES
          ↓
Use profiles / stop idle services
          │
         NO
          ↓
Can sensible limits keep machine usable?
          │
        YES
          ↓
Run with controlled limits
          │
         NO
          ↓
Move workload to a suitable VM /
remote environment
```

### Key principle

Always optimize the workload before increasing infrastructure.

```text
Reduce
  ↓
Measure
  ↓
Limit
  ↓
Budget
  ↓
Upgrade infrastructure only when necessary
```

---

# 42. Hands-On `docker_lab/08/`

This section contains the complete Topic 08 practical exercise.

The learner should use the current Data Engineering lab stack and record actual measurements.

---

## Exercise 1 — Measure PostgreSQL

Start only the PostgreSQL service required by the current lab.

Use:

```bash
docker stats
```

or:

```bash
docker stats <postgres-container>
```

Record:

```text
Idle CPU:
Idle memory:
Memory limit:
```

Then run a realistic workload.

Examples:

- insert test rows;
- execute analytical queries;
- run a Python ingestion workload;
- perform a controlled batch operation.

Record:

```text
Loaded CPU:
Loaded memory:
```

Do not invent the values.

---

## Exercise 2 — Measure MinIO

Run MinIO.

Record:

```text
Idle CPU:
Idle memory:
Loaded CPU:
Loaded memory:
```

Create a representative object-storage workload if appropriate.

For example:

```text
upload files
list objects
read objects
```

The workload should be bounded.

---

## Exercise 3 — Measure Redis

Run Redis.

Measure:

```bash
docker stats <redis-container>
```

Record:

```text
Idle CPU:
Idle memory:
Loaded CPU:
Loaded memory:
```

Generate a controlled workload if needed.

For example:

```text
write keys
read keys
delete keys
```

---

## Exercise 4 — Measure Kafka

Run Kafka.

Record:

```text
Idle memory:
Loaded memory:
Idle CPU:
Loaded CPU:
Configured memory limit:
JVM heap configuration:
```

Use a representative streaming workload.

For example:

```text
produce messages
consume messages
```

Do not treat the measured values as universal Kafka requirements.

They describe **your current image, configuration, runtime, and workload**.

---

## Exercise 5 — Build the Capacity Table

Fill this with real measurements:

| Service | Idle Memory | Loaded Memory | Idle CPU | Loaded CPU | Proposed Limit |
|---|---:|---:|---:|---:|---:|
| PostgreSQL | | | | | |
| MinIO | | | | | |
| Redis | | | | | |
| Kafka | | | | | |

Then answer:

1. Which service has the largest idle footprint?
2. Which service grows most under load?
3. Which service consumes the most CPU?
4. Which service has the largest gap between idle and loaded memory?
5. Which proposed limit has the strongest evidence behind it?

---

## Exercise 6 — Project the Full Stage 2 Stack

Add:

- PostgreSQL;
- MinIO;
- Redis;
- Kafka;
- Schema Registry;
- other services required by the current Stage 2 lab.

Use this model:

```text
Estimated stack footprint
=
measured service values
+
estimated services
+
headroom
```

Clearly label each number:

```text
Measured
Estimated
Illustrative
```

### Example

| Service | Type | Planning Memory |
|---|---|---:|
| PostgreSQL | Measured | your value |
| MinIO | Measured | your value |
| Redis | Measured | your value |
| Kafka | Measured | your value |
| Schema Registry | Estimated/Measured | your value |
| Spark | Estimated | your value |
| Flink | Estimated | your value |

Then calculate:

```text
Total planning footprint
```

and compare it with:

```text
effective Docker/WSL2 capacity
```

and:

```text
laptop total RAM
```

---

## Exercise 7 — Kafka Memory Failure

The roadmap requires a deliberately mismatched Kafka memory configuration.

### Objective

Create:

```text
Container memory limit
<
Configured JVM heap
```

Use a disposable lab only.

### Procedure

1. Configure a deliberately small container memory limit.
2. Configure a JVM heap larger than that limit.
3. Start Kafka.
4. Observe the behavior.
5. Inspect status.
6. Inspect logs.
7. Inspect exit status.
8. Determine whether resource pressure explains the failure.
9. Correct the JVM/container relationship.
10. Re-run.
11. Verify stability.

Useful commands:

```bash
docker ps -a
```

```bash
docker logs <kafka-container>
```

```bash
docker inspect <kafka-container>
```

```bash
docker stats
```

### Expected lesson

A configuration such as:

```text
container = 1 GB
heap      = 1 GB
```

does not provide room for:

```text
native memory
+
threads
+
buffers
+
runtime overhead
```

### Fix

The corrected relationship should be:

```text
container limit
>
JVM heap
+
non-heap/native overhead
+
headroom
```

The exact values depend on the Kafka image and workload.

---

## Exercise 8 — CPU Throttling

Run a CPU-heavy Python workload with:

```bash
--cpus=0.5
```

Measure execution time.

Compare it against:

```bash
--cpus=1
```

or another less restrictive setting.

Record:

```text
CPU limit:
Execution time:
Observed CPU:
Observed behavior:
```

### Expected lesson

```text
Lower CPU allowance
        ↓
more throttling
        ↓
longer execution
```

Do not expect an exact proportional relationship.

---

## Exercise 9 — Docker/WSL2 Memory Budget

Record:

```text
Host RAM:
Host logical CPUs:
Docker/WSL2 effective memory:
Docker/WSL2 effective CPU:
```

Document the selected runtime capacity and explain why you selected it.

### Example reasoning

```text
Laptop RAM = 16 GB
Daily workload = browser + IDE + terminal
Data Engineering workload = Kafka + PostgreSQL + Redis

Decision:
Do not allocate nearly all RAM to Docker.
Reserve sufficient capacity for the host.
Measure the resulting stack.
```

Use your actual values.

---

## Exercise 10 — Personal Lab Budget

Create:

```text
Machine:
RAM = ______
CPU = ______

OS/other applications reserve:
______ 

Docker/WSL2 effective capacity:
______

Safe Data Engineering lab budget:
______
```

Then create profiles:

```text
Profile A — SQL
Services = __________________
Estimated memory = ___________

Profile B — Object Storage
Services = __________________
Estimated memory = ___________

Profile C — Streaming
Services = __________________
Estimated memory = ___________

Profile D — Full Stack
Services = __________________
Estimated memory = ___________
```

Finally answer:

> Which services can safely run together on my machine?

Base the answer on your measurements.

---

# 43. Break/Fix Resource Lab

All failures in this section must remain controlled.

For every experiment record:

```text
Expected behavior
Observed behavior
Evidence
Root cause
Corrective action
Verification
```

---

## Failure 1 — Memory Limit Too Low

Configure a bounded workload with a deliberately small memory limit.

Observe:

```text
application failure
or
container termination
```

Investigate:

```bash
docker ps -a
docker inspect <container>
docker logs <container>
```

Determine whether memory pressure explains the result.

---

## Failure 2 — JVM Heap Too Large

Use:

```text
container memory limit
<
JVM heap
```

Diagnose:

```text
Why is the configuration unsafe?
What memory exists outside the heap?
What headroom is missing?
```

Correct the configuration.

---

## Failure 3 — CPU Limit Too Low

Run a CPU-bound workload with:

```bash
--cpus=0.5
```

Observe:

```text
higher runtime
+
CPU throttling
```

Explain why the container normally continues running instead of being killed simply because it wants more CPU.

---

## Failure 4 — Too Many Services

Start a deliberately oversized but controlled local stack.

Monitor:

```bash
docker stats
```

and the host.

Observe:

```text
memory pressure
CPU contention
responsiveness
```

Stop unnecessary services.

Compare the machine before and after.

---

## Failure 5 — Heavy Stack Left Running

Leave a heavy stack running while performing unrelated work.

Observe background resource usage.

Then:

```bash
docker compose stop
```

Stop the unused stack and compare host responsiveness.

### Lesson

Infrastructure should have a lifecycle.

```text
Start
→
Use
→
Measure
→
Stop when no longer needed
```

---

# 44. Real-World Data Engineering Scenarios

## Scenario 1 — 8 GB Laptop

A learner has an 8 GB machine.

They want to run:

```text
Kafka
+
Spark
+
Airflow
+
Flink
+
PostgreSQL
+
MinIO
+
Redis
```

### Correct reasoning

Do not immediately say:

```text
"Impossible."
```

or:

```text
"It will definitely work."
```

Instead:

```text
Measure
  ↓
Identify required services
  ↓
Remove unnecessary services
  ↓
Use profiles
  ↓
Apply controlled limits
  ↓
Measure loaded behavior
```

An 8 GB machine has substantially less room for a large multi-service stack than a higher-memory machine, but the exact safe workload depends on the runtime and workload.

---

## Scenario 2 — 16 GB Laptop

A learner has:

```text
16 GB RAM
```

They want:

```text
PostgreSQL
+
MinIO
+
Redis
+
Kafka
```

This may be a reasonable local lab, but the decision should still be based on:

```text
measured service usage
+
Docker/WSL2 capacity
+
host applications
+
workload
```

Then add Spark or Flink only after evaluating the remaining capacity.

---

## Scenario 3 — Kafka Keeps Dying

Configuration:

```text
memory limit = 1 GB
JVM heap     = 1 GB
```

### Questions

- What is wrong?
- What memory exists outside the heap?
- Why is the container limit too tight?
- What evidence would you collect?
- How would you correct the relationship?

### Strong answer

The heap consumes essentially the entire outer memory budget. Kafka also needs native/non-heap memory, threads, buffers, and process overhead. The heap should be reduced or the container limit increased, with deliberate headroom based on workload.

---

## Scenario 4 — Laptop Becomes Extremely Slow

No container obviously crashed.

The learner reports:

> "Docker did not fail, but my whole laptop feels frozen."

Investigate:

```text
memory pressure
swap activity
CPU contention
docker stats
host resource usage
```

The likely problem may be resource saturation rather than a service-level crash.

---

## Scenario 5 — Heavy Stack Runs Overnight

The learner leaves:

```text
Kafka
+
Spark
+
Flink
+
Airflow
+
PostgreSQL
```

running for days.

Even when the workload is low, services may maintain:

- memory allocations;
- background threads;
- timers;
- network activity;
- internal housekeeping.

The correct operational habit is:

```text
Stop unused heavy stacks.
```

---

## Scenario 6 — Move to a Cloud VM

The learner has repeatedly measured:

```text
laptop memory pressure
+
CPU contention
+
swap
+
poor responsiveness
```

They have already reduced unnecessary services and applied sensible limits.

At this point a small cloud VM may be reasonable.

Compare:

```text
Expected workload duration
+
required capacity
+
cloud hourly/monthly cost
+
operational overhead
```

against:

```text
hardware upgrade
+
local convenience
+
lab usage frequency
```

---

# 45. Capacity Planning Principles

## Principle 1 — Measure before guessing

Use:

```bash
docker stats
```

and host measurements.

Do not build a resource budget from intuition alone.

---

## Principle 2 — Record idle and loaded usage

Idle usage tells you baseline cost.

Loaded usage tells you what the exercise actually costs.

---

## Principle 3 — Keep host capacity in mind

A container budget that consumes the entire laptop is not a good development budget.

---

## Principle 4 — Set sensible container limits

Limits can prevent uncontrolled resource consumption.

But arbitrary limits can also cause unnecessary failures.

Use evidence.

---

## Principle 5 — Leave headroom

Do not size a service so tightly that normal workload variation immediately hits the boundary.

---

## Principle 6 — JVM heap must fit inside container memory

Think:

```text
Container limit
>
heap
+
non-heap/native memory
+
threads
+
buffers
+
headroom
```

---

## Principle 7 — Run only necessary services

The easiest optimization is often:

```text
Do less.
```

If an exercise needs PostgreSQL, do not automatically run Kafka, Spark, and Flink.

---

## Principle 8 — Stop idle heavy stacks

A running stack is still infrastructure consuming resources.

---

## Principle 9 — Swap is not free RAM

Swap can prevent immediate failure in some conditions, but severe swap activity can make the system extremely slow.

---

## Principle 10 — Use controlled experiments

Resource management is best learned by:

```text
measure
→
limit
→
observe
→
interpret
```

---

## Principle 11 — Distinguish measured values from estimates

Never turn an illustrative number into an undocumented benchmark.

---

## Principle 12 — Reassess capacity as workloads grow

A stack that fits today may not fit after:

```text
more data
+
more services
+
more concurrency
```

---

## Principle 13 — Move heavy workloads off the laptop when necessary

There is no engineering virtue in repeatedly freezing the development machine.

---

## Principle 14 — Include cost in capacity planning

Cloud capacity has a monetary cost.

Local capacity has an opportunity cost:

```text
slow laptop
+
lost productivity
+
limited workload size
```

A good engineer considers both.

---

# 46. Common Mistakes

## Mistake 1 — Unlimited stacks that freeze the laptop

Launching every service at once without understanding the resource budget can consume the machine.

### Better approach

```text
Measure
→
select required services
→
apply limits
→
observe
```

---

## Mistake 2 — JVM heaps larger than container limits

Example:

```text
Container = 1 GB
Heap = 2 GB
```

This is fundamentally incoherent.

### Better approach

```text
Container
>
heap
+
overhead
+
headroom
```

---

## Mistake 3 — Leaving heavy stacks running for days

Background infrastructure still consumes resources.

### Better approach

Stop unused stacks.

---

## Mistake 4 — Measuring only idle memory

Idle services can look small.

Loaded services can grow substantially.

### Better approach

Measure both.

---

## Mistake 5 — Ignoring host memory usage

A container can look fine while the host is under pressure because several containers and other applications collectively consume memory.

### Better approach

Monitor:

```text
container
+
runtime
+
host
```

---

## Mistake 6 — Treating swap as normal RAM

Swap may keep a workload alive while making the machine painfully slow.

### Better approach

Treat heavy swap activity as a capacity warning.

---

## Mistake 7 — Applying arbitrary memory limits

A random:

```bash
--memory=512m
```

may simply cause a service to fail.

### Better approach

Measure first.

---

## Mistake 8 — Setting CPU limits too aggressively

A CPU limit can make legitimate workloads unusably slow.

### Better approach

Compare baseline and constrained runtime.

---

## Mistake 9 — Assuming every service has the same resource profile

Redis, PostgreSQL, Kafka, Spark, and Flink have different workload characteristics.

### Better approach

Measure each service.

---

## Mistake 10 — Treating illustrative benchmarks as universal

A number from one laptop is not a universal capacity requirement.

---

## Mistake 11 — Forgetting non-heap JVM memory

A heap setting is not the total JVM footprint.

---

## Mistake 12 — Running the entire Stage 2 stack for every exercise

This wastes resources.

### Better approach

Use profiles or targeted services.

---

## Mistake 13 — Ignoring service dependencies when reducing a stack

Do not stop a required dependency just because the service itself looks optional.

Understand the architecture first.

---

## Mistake 14 — Moving to the cloud without considering cost

Cloud capacity is not free.

---

## Mistake 15 — Moving to the cloud when simple service reduction would solve the problem

Sometimes:

```text
stop Spark
```

is a better solution than:

```text
rent a VM
```

---

# 47. Mental Models

## Mental Model 1 — Laptop = finite infrastructure

```text
Laptop
=
finite infrastructure
```

It has a hard physical resource boundary.

---

## Mental Model 2 — Docker does not create infinite resources

```text
Docker
≠
infinite CPU/RAM
```

Docker packages and runs workloads. It does not create hardware capacity.

---

## Mental Model 3 — Resource hierarchy

```text
Host capacity
      ↓
Docker runtime capacity
      ↓
Container allocation
```

When the runtime imposes an intermediate boundary.

Exact behavior differs by platform.

---

## Mental Model 4 — Memory over limit

```text
Memory over limit
→
possible process/container kill
```

---

## Mental Model 5 — CPU over limit

```text
CPU demand over allowance
→
throttling
→
slower work
```

---

## Mental Model 6 — JVM heap

```text
JVM heap
<
container memory limit
```

with meaningful headroom.

---

## Mental Model 7 — Idle versus loaded

```text
Idle measurement
≠
Loaded measurement
```

---

## Mental Model 8 — Persistence is separate from capacity

```text
Persistence
≠
resource capacity
```

A volume can preserve data while a container is resource-constrained.

---

## Mental Model 9 — More services means a larger footprint

```text
More services
→
larger resource footprint
```

---

## Mental Model 10 — Run only what the exercise needs

```text
Exercise
→
required services
→
smaller footprint
→
healthier laptop
```

---

## Mental Model 11 — Swap

```text
Swap
=
overflow mechanism
not
free RAM
```

---

## Mental Model 12 — Capacity planning

```text
Capacity planning
=
measurement
+
estimation
+
headroom
+
trade-offs
```

---

# 48. Capacity Diagrams

## Resource hierarchy

```text
Physical Laptop
      │
      ├── OS
      │
      ├── IDE / Browser / Other Applications
      │
      └── Docker Runtime
             │
             ├── PostgreSQL
             ├── MinIO
             ├── Redis
             ├── Kafka
             └── Other Services
```

## Memory hierarchy

```text
Container Memory Limit
        │
        └── JVM Service
              │
              ├── Heap
              ├── Non-Heap
              ├── Direct Buffers
              ├── Threads
              └── Native / Runtime Overhead
```

## Capacity planning

```text
Measured Services
       ↓
Idle Footprint
       +
Loaded Footprint
       +
Headroom
       ↓
Stack Budget
       ↓
Laptop Capacity Decision
```

## Resource-pressure progression

```text
Normal
  ↓
Memory pressure
  ↓
Swap activity
  ↓
Severe slowdown
  ↓
Possible process/container failure
```

---

# 49. Command Reference

## `docker stats`

### Purpose

Continuously monitor running container resource usage.

### Syntax

```bash
docker stats
```

### What to look for

```text
CPU %
MEM USAGE / LIMIT
MEM %
NET I/O
BLOCK I/O
PIDS
```

### Operational interpretation

Use it to establish:

```text
baseline
+
loaded usage
+
resource pressure
```

---

## `docker stats <container>`

### Purpose

Monitor one container.

### Example

```bash
docker stats kafka
```

### Use when

You want to focus on a specific service during an experiment.

---

## `docker run --memory=512m`

### Purpose

Set a container memory boundary.

### Example

```bash
docker run --rm --memory=512m <image>
```

### What to look for

Whether the workload remains within the configured boundary.

---

## `docker run --memory=1g`

### Purpose

Set a larger memory boundary.

### Example

```bash
docker run --rm --memory=1g <image>
```

---

## `docker run --cpus=0.5`

### Purpose

Limit CPU consumption.

### Example

```bash
docker run --rm --cpus=0.5 <image>
```

### What to look for

Longer execution time for CPU-bound workloads.

---

## `docker inspect <container>`

### Purpose

Inspect runtime state and configuration.

### Example

```bash
docker inspect kafka
```

### Useful for

- state;
- exit code;
- resource configuration;
- mounts;
- networking;
- runtime configuration.

---

## `docker ps`

### Purpose

List running containers.

```bash
docker ps
```

Use it to identify currently active workloads.

---

## `docker ps -a`

### Purpose

List running and stopped containers.

```bash
docker ps -a
```

Especially useful after a resource-related failure.

---

## `free -h`

### Purpose

Inspect Linux host memory.

```bash
free -h
```

### What to look for

- total;
- used;
- available;
- swap.

---

## `nproc`

### Purpose

Show the number of available logical processors in the current environment.

```bash
nproc
```

### Operational use

Use it as one input to CPU capacity planning.

---

## `lscpu`

### Purpose

Inspect CPU information on Linux.

```bash
lscpu
```

Use when you need more context than `nproc` provides.

---

## `cat /proc/meminfo`

### Purpose

Inspect Linux memory information.

```bash
cat /proc/meminfo
```

Use when deeper Linux-level memory information is useful.

Do not turn this into a full Linux memory administration workflow.

---

# 50. Practice Questions

## Beginner

1. What is laptop capacity?
2. Why does Docker consume host resources?
3. What does `docker stats` show?
4. What is CPU utilization?
5. What is memory usage?
6. What is the difference between host capacity and container capacity?
7. Why can Docker have less available memory than the physical laptop?
8. What is the difference between idle and loaded usage?

## Intermediate

1. What does `--memory` do?
2. What does `--cpus` do?
3. What happens when memory exceeds a container limit?
4. What happens when CPU demand exceeds its CPU allowance?
5. What is exit code `137`?
6. Why does exit code `137` need correlation with other evidence?
7. Why does a JVM heap need headroom?
8. Why is `1 GB container + 1 GB heap` unsafe?
9. Why measure idle and loaded usage?
10. Why should a local stack have a resource budget?
11. Why can a machine become slow without any container crashing?
12. Why is swap not equivalent to RAM?

## Advanced

1. How would you size Kafka on a 16 GB development machine?
2. How would you estimate the full Stage 2 streaming-stack footprint?
3. How would you decide which Compose profiles can run together?
4. How would you design a personal laptop lab budget?
5. Why can Spark or Flink require more memory than their heap setting alone suggests?
6. How would you troubleshoot a laptop that becomes extremely slow while Docker is running?
7. When should you move a workload to a cloud VM?
8. How would you compare local hardware constraints with cloud cost?
9. How would you distinguish measured values from planning estimates?
10. How would you safely test a memory limit?
11. How would you measure CPU throttling?
12. How would you reduce the resource footprint of a Data Engineering lab without changing hardware?

These questions test reasoning rather than memorization.

---

# 51. Interview Practice

## 1. How do you monitor Docker container resource usage?

**Strong answer:**

I use `docker stats` for container-level CPU, memory, network I/O, block I/O, and PID visibility. I correlate those measurements with host-level resource usage and workload activity because container usage alone does not describe the entire machine's capacity.

---

## 2. What does `docker stats` tell you?

**Strong answer:**

It provides a live operational view of running container resource consumption. Important fields include CPU percentage, memory usage and limit, memory percentage, network I/O, block I/O, and process count. I use it to establish idle baselines, loaded behavior, and resource pressure.

---

## 3. How do Docker memory limits work?

**Strong answer:**

A Docker memory limit establishes an outer resource boundary for the container. If the workload requires more memory than the boundary permits, memory pressure can result in process or container termination. I would investigate the workload, configured limit, runtime evidence, and exit state rather than assuming the cause from one signal alone.

---

## 4. What happens when a container exceeds its memory limit?

**Strong answer:**

The container can experience an OOM-related termination. Exit code `137` is an important clue because it commonly corresponds to a process receiving `SIGKILL`, but I would correlate that signal with runtime and memory evidence before claiming Docker OOM as the root cause.

---

## 5. What does exit code 137 indicate?

**Strong answer:**

It represents `128 + 9`, corresponding to termination by signal 9, `SIGKILL`. In containerized workloads it is commonly seen during OOM-related termination, but exit code 137 alone is not proof of a Docker memory-limit violation. I would inspect container configuration and runtime evidence.

---

## 6. What happens when a CPU limit is reached?

**Strong answer:**

The workload is generally throttled to its CPU allowance. A CPU-bound process therefore takes longer to complete instead of normally being killed simply because it wants more CPU.

---

## 7. What is the difference between CPU throttling and an OOM kill?

**Strong answer:**

CPU throttling limits how much CPU time a container can consume and typically manifests as slower execution. An OOM-related event occurs when memory pressure exceeds what the process/runtime can sustain and may terminate the process or container.

---

## 8. How would you size Kafka memory in Docker?

**Strong answer:**

I would first measure idle and representative loaded memory. Then I would identify the Kafka JVM heap configuration and ensure that the heap fits below the container memory limit with headroom for native memory, threads, direct buffers, and runtime overhead. I would validate the configuration under the actual workload rather than relying on a universal percentage.

---

## 9. Why should JVM heap be smaller than container memory?

**Strong answer:**

The heap is only one part of JVM process memory. The process also consumes native memory, thread stacks, direct buffers, metadata, libraries, and other runtime resources. If the heap consumes the entire container limit, the rest of the process has no safe budget.

---

## 10. What other memory does a JVM process consume besides heap?

**Strong answer:**

It can consume non-heap JVM memory, native allocations, thread stacks, direct/off-heap buffers, class metadata, loaded libraries, and other runtime/process overhead.

---

## 11. How would you estimate the resource footprint of a Data Engineering stack?

**Strong answer:**

I would measure individual services at idle and under realistic load, build a service-level capacity table, add the planning values, account for Docker/WSL2 and host overhead, include workload growth and headroom, and then compare the result with the machine's effective capacity.

---

## 12. Why are idle measurements insufficient?

**Strong answer:**

Idle measurements describe baseline resource consumption but may significantly underestimate the service under real workload. Capacity planning should include representative loaded measurements because Data Engineering services can grow in memory and CPU usage during ingestion, streaming, query execution, or distributed processing.

---

## 13. How does swap affect container workloads?

**Strong answer:**

Swap uses storage as an overflow mechanism when memory is under pressure. It can prevent immediate failure in some situations but is much slower than RAM. Heavy swap activity can make a laptop appear frozen even though processes are still technically running.

---

## 14. How would you troubleshoot a laptop that becomes extremely slow while running Docker?

**Strong answer:**

I would inspect container usage with `docker stats`, inspect host memory and swap, look for CPU contention, identify the largest workloads, and determine whether the system is swapping or otherwise resource constrained. I would then stop unnecessary services, reduce the workload, apply sensible limits, and verify responsiveness.

---

## 15. When would you move a workload to a cloud VM?

**Strong answer:**

I would first reduce unnecessary services, use profiles, stop idle stacks, and apply reasonable limits. If the workload still consistently exceeds comfortable laptop capacity or needs to remain online, collaborate remotely, or use dedicated capacity, I would evaluate a cloud VM based on capacity, duration, network requirements, and cost.

---

## 16. How would you design a development laptop resource budget?

**Strong answer:**

I would measure host capacity, establish the Docker/WSL2 effective capacity, reserve resources for the operating system and normal applications, measure individual service idle and loaded usage, define lab profiles, and document which combinations are safe. I would revisit the budget as the stack grows.

---

## 17. What are common mistakes when running Kafka, Spark, or Flink locally?

**Strong answer:**

Common mistakes include running every service simultaneously, allocating JVM heaps equal to or larger than container limits, ignoring non-heap memory, measuring only idle usage, ignoring host pressure and swap, leaving heavy stacks running indefinitely, and treating cloud migration as the first solution instead of reducing unnecessary local workload.

---

# 52. Final Knowledge Check

You should be able to explain all of the following without looking at this module:

1. What is laptop capacity?
2. What resources do Docker containers consume?
3. How much CPU and memory are available to Docker?
4. How does Docker Desktop affect available capacity?
5. How can WSL2 affect available capacity?
6. How does Docker Engine on Linux differ conceptually from a VM-backed runtime?
7. How do you measure container resource usage?
8. What does `docker stats` show?
9. What does `--memory` do?
10. What does `--cpus` do?
11. What happens when memory usage exceeds a container limit?
12. What does exit code `137` indicate?
13. Why does `137` require correlation with other evidence?
14. What happens when CPU demand exceeds the CPU allowance?
15. What is CPU throttling?
16. Why does a JVM heap need headroom?
17. Why can Kafka fail when its heap is equal to or larger than the container memory limit?
18. What memory exists outside a JVM heap?
19. How do Spark and Flink complicate memory sizing?
20. How do you estimate a stack's resource footprint?
21. Why should idle and loaded measurements both be collected?
22. Why can swap make a machine appear to hang?
23. When should you stop unused services?
24. How can Compose profiles help reduce resource usage?
25. How would you build a personal laptop lab budget?
26. When should a workload move to a cloud VM?
27. How would you compare cloud cost against local capacity?
28. How would you safely experiment with resource limits?

### Practical mastery test

Perform this sequence without following a command-by-command tutorial:

```text
Measure host/runtime capacity
        ↓
Measure PostgreSQL
        ↓
Measure MinIO
        ↓
Measure Redis
        ↓
Measure Kafka
        ↓
Record idle usage
        ↓
Generate realistic load
        ↓
Record loaded usage
        ↓
Build capacity table
        ↓
Estimate full stack
        ↓
Set a personal lab budget
        ↓
Run CPU-limit experiment
        ↓
Run memory-limit experiment
        ↓
Run Kafka JVM-sizing experiment
        ↓
Evaluate swap behavior
        ↓
Select appropriate Compose profile
        ↓
Decide whether local or cloud capacity is appropriate
```

---

# 53. Module Completion Checklist

```text
[ ] I understand that a laptop is a finite compute environment.
[ ] I understand CPU capacity.
[ ] I understand memory capacity.
[ ] I understand CPU contention.
[ ] I understand CPU throttling.
[ ] I understand memory pressure.
[ ] I understand host capacity versus Docker capacity.
[ ] I understand Docker Desktop resource allocation conceptually.
[ ] I understand WSL2 resource capacity conceptually.
[ ] I can inspect Linux host memory with free -h.
[ ] I can inspect logical CPUs with nproc.
[ ] I can use docker stats.
[ ] I can interpret CPU %.
[ ] I can interpret memory usage and memory limit.
[ ] I can interpret memory percentage.
[ ] I understand network I/O and block I/O at a practical level.
[ ] I can measure idle usage.
[ ] I can measure loaded usage.
[ ] I can build a capacity table.
[ ] I can set --memory.
[ ] I can set --cpus.
[ ] I understand memory-limit failure behavior.
[ ] I understand exit code 137 as a diagnostic clue.
[ ] I can distinguish memory failure from CPU throttling.
[ ] I understand JVM heap versus total process memory.
[ ] I can reason about Kafka JVM sizing.
[ ] I understand Spark/Flink memory awareness.
[ ] I understand application memory versus container memory.
[ ] I can estimate a multi-service stack footprint.
[ ] I can distinguish measured values from estimates.
[ ] I can create a laptop lab budget.
[ ] I can select only the services required for an exercise.
[ ] I understand Compose profiles operationally.
[ ] I know when to stop idle stacks.
[ ] I understand swap.
[ ] I understand why a lab can appear to hang.
[ ] I can perform safe resource experiments.
[ ] I can decide when a cloud VM may be appropriate.
[ ] I understand local versus cloud cost trade-offs.
[ ] I can perform the complete docker_lab/08 exercise.
[ ] I can explain the complete capacity-management mental model.
```

---

# 54. Roadmap Coverage Audit

The Topic 08 specification requires complete coverage of the following areas.

| Roadmap requirement | Covered |
|---|---|
| How much memory and CPU Docker has available | Yes |
| Docker Desktop settings/capacity | Yes |
| WSL2 limits/capacity | Yes |
| Whole-host resources on Linux | Yes |
| `docker stats` | Yes |
| Per-container memory limits | Yes |
| `--memory` | Yes |
| CPU limits | Yes |
| `--cpus` | Yes |
| Compose settings awareness | Yes |
| Memory-limit behavior | Yes |
| CPU-limit behavior | Yes |
| Memory kill behavior | Yes |
| Exit code 137 | Yes |
| CPU throttling | Yes |
| JVM services in containers | Yes |
| Kafka | Yes |
| Spark | Yes |
| Flink | Yes |
| Catalog/JVM service awareness | Yes |
| JVM heap headroom | Yes |
| Stack footprint estimation | Yes |
| Idle vs loaded memory | Yes |
| Capacity estimation | Yes |
| Required-service profiles | Yes |
| Stopping idle stacks | Yes |
| Swap | Yes |
| Labs appearing to hang | Yes |
| Cloud VM decision | Yes |
| Cloud cost trade-offs | Yes |
| PostgreSQL measurement | Yes |
| MinIO measurement | Yes |
| Kafka measurement | Yes |
| Redis measurement | Yes |
| Full Stage 2 stack projection | Yes |
| Kafka heap/container-limit failure | Yes |
| Kafka heap fix | Yes |
| CPU-heavy Python with `--cpus=0.5` | Yes |
| Docker/WSL2 memory exercise | Yes |
| Personal laptop lab budget | Yes |
| Break/fix exercises | Yes |
| Common mistakes | Yes |
| Checkpoint/knowledge check | Yes |

### Technical accuracy principles

The module intentionally avoids several common overclaims:

1. `exit code 137` is treated as a strong diagnostic clue, not automatic proof of Docker OOM.
2. CPU percentage is interpreted in runtime context.
3. JVM heap is not treated as total JVM memory.
4. Illustrative memory numbers are explicitly labeled rather than presented as benchmarks.
5. Headroom is treated as workload-dependent rather than a universal percentage.
6. Docker Desktop and WSL2 interfaces are described conceptually rather than with potentially stale UI paths.
7. Kafka JVM configuration is treated as image/distribution-dependent.
8. Resource experiments are bounded to avoid destabilizing the host.

---

# 55. Scope Boundary

This module focuses on:

```text
Resource limits
+
Laptop capacity
+
Measurement
+
Capacity estimation
+
Safe local Data Engineering workloads
```

It does **not** become a complete course on:

- Docker networking;
- Docker volumes;
- environment variables;
- Docker Compose authoring;
- container troubleshooting;
- Docker cleanup;
- Docker Desktop platform administration;
- WSL2 administration;
- Spark memory internals;
- Flink memory internals;
- Kafka performance tuning;
- JVM garbage collection;
- Linux kernel memory management;
- Kubernetes resource requests/limits;
- cloud infrastructure administration.

Those topics may be referenced when necessary, but the learning objective remains resource management for local Data Engineering labs.

---

# 56. Final Professional Takeaway

A professional Data Engineer should think about a laptop as a small infrastructure platform with a finite capacity budget.

The complete mental model is:

```text
Measure
   ↓
Understand
   ↓
Limit
   ↓
Size
   ↓
Budget
   ↓
Run
   ↓
Monitor
   ↓
Adjust
```

The most important principles are:

```text
Docker does not create hardware capacity.
```

```text
A running container still consumes resources.
```

```text
Idle usage is not loaded usage.
```

```text
Memory limits can cause process/container termination.
```

```text
CPU limits generally produce throttling and slower execution.
```

```text
JVM heap is only part of JVM memory.
```

```text
The JVM heap must fit inside the container limit with headroom.
```

```text
Swap is not free RAM.
```

```text
Running fewer services is often the easiest capacity optimization.
```

```text
A cloud VM is a capacity and cost decision, not an automatic upgrade.
```

The mature Data Engineering mindset is therefore:

> **Do not ask only whether the stack can start. Ask whether the machine can run the workload predictably, with sufficient headroom, while remaining usable for the engineer.**

That is the purpose of resource limits and laptop capacity management.
