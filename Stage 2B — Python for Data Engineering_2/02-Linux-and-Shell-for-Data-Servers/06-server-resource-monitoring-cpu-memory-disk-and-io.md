# Server Resource Monitoring: CPU, Memory, Disk, and I/O

> **Stage 2B — Gap Module G2: Linux and Shell for Data Servers**
>
> **Topic 06:** Server resource monitoring: CPU, memory, disk, and I/O  
> **Level:** Beginner → Intermediate → Advanced → Production  
> **Primary skill:** Evidence-based Linux server performance diagnosis for Data Engineers

---

## Module Purpose

A production Data Engineer eventually hears statements such as:

- "The API extraction is suddenly slow."
- "PostgreSQL queries are timing out."
- "The Spark job is stuck."
- "The Python process disappeared."
- "The server is completely frozen."
- "Kafka consumers are falling behind."
- "The database has too many connections."
- "The batch pipeline was fine yesterday but is slow today."

None of those statements identifies the root cause.

> **"The job is slow" is a symptom, not a diagnosis.**

This module teaches you to turn that symptom into evidence.

The central diagnostic sequence is:

```text
SYMPTOM
   ↓
MEASURE
   ↓
IDENTIFY SATURATED RESOURCE
   ↓
IDENTIFY RESPONSIBLE PROCESS
   ↓
UNDERSTAND WHY
   ↓
APPLY SAFE FIX
   ↓
VERIFY
   ↓
DOCUMENT
```

You will learn to distinguish:

```text
CPU-bound
Memory-bound
I/O-bound
Connection-bound
Application-bound
Unknown
```

and to correlate system-wide and per-process evidence using:

```text
uptime
nproc
top
free -h
vmstat
iostat
pidstat
ss
dmesg
journalctl -k
/proc/pressure/*
sar
```

The goal is **not** to memorize commands.

The goal is to answer:

> **What question does this tool answer, what evidence matters, what hypothesis does it support, and what should I check next?**

---

# 1. Why Server Resource Monitoring Matters

Data Engineering workloads are resource-intensive because they frequently process large volumes of data, perform transformations, communicate with databases and APIs, and run concurrently.

Typical examples include:

- Python ingestion processes reading millions of records.
- pandas transformations loading large datasets into RAM.
- PostgreSQL queries performing scans, joins, sorts, and writes.
- Spark jobs spilling intermediate data to local storage.
- Parquet generation and compression.
- Large file transfers and checksum operations.
- Batch jobs running concurrently on a shared server.
- Database connection pools growing unexpectedly.
- Log files and temporary files generating sustained writes.
- Containers competing for CPU and memory.

A useful first distinction is:

```text
Application symptom
        ↓
System evidence
        ↓
Resource bottleneck
        ↓
Responsible workload
        ↓
Root cause
```

For example:

```text
Spark job is slow
        ↓
CPU only 30%
        ↓
iowait is high
        ↓
disk utilization is high
        ↓
Spark executor is generating heavy spill I/O
        ↓
storage is the bottleneck
```

The conclusion is much stronger than:

> "Spark is slow."

## 1.1 The questions you should ask

When a server is slow, ask:

```text
Is CPU saturated?

Is memory under pressure?

Is swap active?

Is the disk saturated?

Is I/O latency high?

Are processes blocked?

Are connections piling up?

Did the kernel kill a process?

Did this happen in the past?

Which process is responsible?

What changed?
```

## 1.2 Production principle: measure before restart

A restart can make symptoms disappear temporarily while destroying valuable evidence.

For example:

```text
Server slow
   ↓
Restart
   ↓
Server looks healthy
```

This does **not** establish the root cause.

Instead:

```text
Server slow
   ↓
Collect evidence
   ↓
Classify resource pressure
   ↓
Identify process
   ↓
Investigate cause
   ↓
Apply safe remediation
   ↓
Verify
```

> **Do not blindly restart a production server before collecting enough evidence to understand what is happening, unless an approved emergency procedure explicitly requires immediate recovery.**

---

# 2. The Data Engineer's Performance Mental Model

Think of a Linux server as a set of constrained resources shared by processes.

```text
                     Linux Server
                          |
        +-----------------+-----------------+
        |                 |                 |
       CPU              Memory            Storage
        |                 |                 |
     cores            RAM/cache           disks
     threads            swap             I/O
        |                 |                 |
        +-----------------+-----------------+
                          |
                       Network
                          |
                    connections
```

A workload consumes one or more of these resources.

For example:

### CPU-heavy Python transformation

```text
Python process
     ↓
high CPU
     ↓
runnable work
     ↓
CPU saturation
```

### Memory-heavy pandas job

```text
pandas
  ↓
large DataFrame
  ↓
RAM pressure
  ↓
reclaim / swap
  ↓
latency
```

### Storage-heavy Spark job

```text
Spark
  ↓
shuffle/spill
  ↓
temporary disk writes
  ↓
I/O queue
  ↓
high latency
```

### Connection problem

```text
Python extractor
      ↓
database connections
      ↓
connections accumulate
      ↓
database/client resource pressure
```

## 2.1 The core production loop

Use this loop repeatedly:

```text
Question
   ↓
Metric
   ↓
Command
   ↓
Observation
   ↓
Hypothesis
   ↓
Next command
   ↓
Confirmation
   ↓
Remediation
   ↓
Verification
```

For example:

```text
Question:
Why is my Data Engineering job slow?

        ↓

Check:
uptime + nproc

        ↓

Question:
Is CPU pressure plausible?

        ↓

Check:
vmstat + top + pidstat

        ↓

Question:
Is storage causing delays?

        ↓

Check:
iostat

        ↓

Question:
Which process is responsible?

        ↓

Check:
pidstat

        ↓

Question:
Is memory pressure involved?

        ↓

Check:
free + vmstat + PSI

        ↓

Question:
Was something OOM-killed?

        ↓

Check:
dmesg + journalctl -k

        ↓

Question:
Did this happen earlier?

        ↓

Check:
sar

        ↓

Diagnosis
   ↓
Fix
   ↓
Verification
   ↓
Runbook
```

This diagnostic mindset is more important than memorizing syntax.

---

# 3. What Resources Exist on a Linux Server?

At this level, focus on five broad categories:

| Resource | What it represents | Typical Data Engineering symptom |
|---|---|---|
| CPU | Compute capacity | transformations take longer |
| Memory | Working memory for processes and kernel | swapping, OOM, severe latency |
| Disk/storage | Persistent and temporary data | slow reads/writes, spill delays |
| I/O | Movement between processes and devices | high wait, queueing, blocked work |
| Network/connections | Communication capacity and sockets | timeouts, connection buildup |

There is also a sixth category that is useful in production diagnosis:

```text
Kernel and scheduling behavior
```

Linux decides which runnable work gets CPU time, manages memory, queues I/O, and can terminate processes under severe resource exhaustion.

The same workload can therefore look different depending on where it is waiting.

---

# 4. CPU Fundamentals

## 4.1 What is a CPU?

The CPU executes instructions.

For a Data Engineer, CPU capacity matters when a workload performs computation such as:

- parsing records
- transforming strings
- compression
- hashing
- serialization
- joins
- sorting
- Python computation
- database execution
- Spark tasks

A CPU-bound workload has enough work to execute that the available compute capacity becomes the limiting factor.

## 4.2 Physical cores, logical CPUs, and threads

A modern server can expose:

```text
physical sockets
    ↓
physical cores
    ↓
logical CPUs
```

A logical CPU is a schedulable execution context visible to the operating system.

The exact relationship depends on hardware and virtualization.

Do not assume:

```text
logical CPU = physical core
```

because technologies such as simultaneous multithreading can expose multiple logical CPUs per physical core.

## 4.3 Discover CPU capacity

Use:

```bash
nproc
```

Example:

```text
8
```

Interpretation:

> The current environment exposes 8 processing units to the command.

This is useful when interpreting load average and CPU pressure.

Also useful when deeper inspection is required:

```bash
nproc --all
```

Depending on the environment, container CPU constraints may make the effective execution capacity different from the host's physical hardware.

---

# 5. CPU Utilisation

CPU utilisation is commonly presented as a percentage.

The important conceptual categories include:

- user CPU
- system CPU
- idle
- I/O wait
- other platform/kernel-specific categories

## 5.1 User CPU

Time spent executing user-space code.

A Python process performing computation can contribute substantial user CPU.

## 5.2 System CPU

Time spent executing kernel code on behalf of workloads.

Examples include:

- system calls
- kernel networking
- filesystem operations
- memory management

High system CPU can therefore be relevant when a workload performs substantial I/O or kernel interaction.

## 5.3 Idle

CPU capacity with no runnable work requiring execution.

## 5.4 I/O wait

I/O wait represents CPU time associated with the system waiting for I/O completion under the metric's accounting semantics.

It is **not** equivalent to:

> "The CPU is doing useful work."

A machine can have relatively modest user CPU while applications remain slow because they are waiting on storage.

---

# 6. CPU Cores and Threads

Suppose:

```bash
nproc
```

returns:

```text
8
```

A rough mental model is:

```text
8 logical execution units
```

Now consider:

```text
load average: 2.0
```

On an 8-CPU system, that load is very different from the same value on a 2-CPU system.

This is why load must be interpreted relative to available CPU capacity.

## 6.1 Data Engineering implication

A parallel job may intentionally consume many CPUs.

High CPU is not automatically a problem.

The real questions are:

```text
Is the CPU usage expected?

Is the workload supposed to be parallel?

Are other important workloads being starved?

Is latency acceptable?

Is CPU saturation sustained?

Did the workload change?
```

A batch Spark transformation at 95% CPU may be healthy.

A production API host at 95% CPU for a sustained period may be a serious incident.

Context matters.

---

# 7. Load Average

Load average is one of the most commonly misunderstood Linux metrics.

Run:

```bash
uptime
```

Example:

```text
 16:20:11 up 12 days,  4:10,  3 users,  load average: 2.10, 1.80, 1.50
```

The values represent:

```text
2.10 → 1-minute load
1.80 → 5-minute load
1.50 → 15-minute load
```

## 7.1 What load represents

Linux load average broadly reflects work that is:

- runnable and waiting for CPU, and
- in certain uninterruptible states, commonly associated with waiting on I/O.

This is why load is **not simply CPU percentage**.

## 7.2 Why CPU count matters

Consider:

```text
load = 2
```

### On a 2-CPU system

```text
load / CPUs = 2 / 2 = 1
```

The system may be at or around full scheduling capacity.

### On an 8-CPU system

```text
load / CPUs = 2 / 8 = 0.25
```

There is much more CPU capacity relative to the load.

### On a 32-CPU system

```text
load / CPUs = 2 / 32 = 0.0625
```

The same numeric load has a very different meaning.

## 7.3 Load is not a root-cause metric

Do not conclude:

```text
load = 12
→ CPU problem
```

Instead:

```text
load = 12
→ compare with nproc
→ inspect vmstat
→ inspect top
→ inspect iostat
→ inspect pidstat
```

A high load can coexist with significant I/O pressure.

---

# 8. Interpreting Load with Other Tools

A useful first correlation is:

```bash
uptime
nproc
vmstat 1
```

Suppose:

```text
nproc → 8
load → 12
```

You still do not know the root cause.

Now suppose `vmstat 1` shows:

```text
r  b
12 0
```

This suggests substantial runnable work.

Now suppose:

```text
r  b
2  8
```

There is less runnable work but more blocked work.

That changes the investigation.

The next step may be:

```bash
iostat -xz 1
```

rather than immediately looking for a CPU-heavy process.

---

# 9. Interactive Process Monitoring

Use:

```bash
top
```

`top` gives a live view of processes and system activity.

Typical questions:

```text
Which process is consuming CPU?

Which process consumes memory?

Is one process dominating the machine?

Are many processes competing?

What is the process state?

What is the PID?

What is the parent process?

How long has it been running?
```

## 9.1 What to look for

Important fields commonly include:

- PID
- user
- process state
- CPU%
- memory%
- virtual/resident memory information
- elapsed/runtime information
- command

Exact columns vary by Linux distribution and `top` version.

## 9.2 Data Engineering examples

You may see:

```text
python ingest.py
java ... Spark
postgres
airflow-worker
```

The command tells you **who is consuming resources**.

It does not necessarily tell you **why**.

For that, correlate with:

```text
vmstat
iostat
pidstat
application logs
```

## 9.3 Optional htop

`htop` can provide a more interactive interface:

```bash
htop
```

It is useful when installed, but this module does not depend on it.

Production environments often have only the standard tools.

---

# 10. Memory Fundamentals

Memory diagnosis begins with a distinction:

```text
RAM capacity
```

is not the same thing as:

```text
memory currently available to new workloads
```

Linux intentionally uses otherwise-unused memory for useful caching.

Important concepts:

```text
RAM
Process memory
Page cache
Buffers
Free memory
Available memory
Swap
Memory pressure
```

---

# 11. free -h

Run:

```bash
free -h
```

Example:

```text
               total        used        free      shared  buff/cache   available
Mem:            15Gi        8Gi        1Gi        500Mi       6Gi         6Gi
Swap:            4Gi        0Gi        4Gi
```

Exact output varies by Linux version.

## 11.1 `total`

Total memory visible to the environment.

## 11.2 `used`

Memory considered used according to the tool's accounting.

Do not interpret this column without understanding cache.

## 11.3 `free`

Memory that is currently unused.

## 11.4 `shared`

Memory associated with shared-memory mechanisms and related accounting.

Exact semantics can vary by version.

## 11.5 `buff/cache`

Memory used by buffers and filesystem/page cache.

This memory can often be reclaimed when applications need it.

## 11.6 `available`

The most useful high-level field for many operational questions:

> How much memory can the system make available to applications without severe memory pressure?

It is an estimate, not a promise.

---

# 12. Used vs Available Memory

One of the most important Linux memory lessons is:

> **Low free memory does not automatically mean the server is running out of memory.**

Example:

```text
total       = 16 GiB
free        = 1 GiB
buff/cache  = 8 GiB
available   = 7 GiB
```

A beginner may say:

> "Only 1 GiB is free. The server is almost out of RAM."

That conclusion is premature.

Linux can reclaim useful cache.

The better question is:

```text
How much memory is actually available to workloads?
```

Start with:

```bash
free -h
```

Then correlate with:

```bash
vmstat 1
```

and:

```bash
cat /proc/pressure/memory
```

and process-level evidence from:

```bash
top
```

---

# 13. Buffers and Cache

Caching improves performance.

Suppose a database repeatedly reads the same file.

Instead of fetching it from storage every time:

```text
disk
  ↓
page cache
  ↓
process
```

A later read may use cached memory.

This means Linux may intentionally make:

```text
free
```

look small.

That is not necessarily unhealthy.

A healthy machine can have:

```text
low free
high cache
high available
```

The warning signs are instead things such as:

```text
available memory falling sharply
swap activity increasing
reclaim pressure
high memory PSI
OOM events
process failures
```

---

# 14. Memory Pressure

A useful conceptual progression is:

```text
Normal memory utilisation
        ↓
Available memory decreases
        ↓
Cache/reclaim pressure
        ↓
Swap activity
        ↓
Latency increases
        ↓
Processes slow down
        ↓
Severe pressure
        ↓
OOM killer
```

The exact path is workload and kernel dependent.

## 14.1 Why the server can appear to hang

Under severe memory pressure, the machine may spend significant time reclaiming pages or swapping.

Applications can become extremely slow.

The user may describe this as:

> "The server is frozen."

It may still be alive but spending most of its effort handling memory pressure.

---

# 15. Swap

Swap provides storage-backed space that can be used for memory management when RAM is under pressure.

Check it with:

```bash
free -h
```

and:

```bash
vmstat 1
```

## 15.1 Swap is not automatically bad

Seeing:

```text
Swap used: 500 MiB
```

does not prove an active incident.

Some pages may have been swapped earlier and remain there without causing current pressure.

The more important question is:

```text
Is the system actively swapping now?
```

In `vmstat`, fields such as:

```text
si
so
```

represent swap-in and swap-out activity in typical Linux `vmstat` output.

Sustained non-zero activity under workload pressure deserves investigation.

## 15.2 Why excessive swapping hurts

Storage is much slower than RAM.

A workload that repeatedly moves pages between RAM and swap can experience large latency increases.

This is commonly associated with:

```text
memory-bound workload
```

rather than:

```text
CPU-bound workload
```

## 15.3 Do not blindly disable swap

The correct response to swap activity is diagnosis.

Ask:

```text
Why is memory under pressure?

Which process consumes memory?

Is the workload expected?

Is the limit too low?

Is concurrency too high?

Is a leak present?

Is capacity insufficient?
```

---

# 16. vmstat

`vmstat` is one of the most valuable system-wide diagnostic tools.

Basic:

```bash
vmstat
```

Continuous sampling:

```bash
vmstat 1
```

This requests approximately one sample per second until interrupted.

## 16.1 What vmstat helps answer

It can help answer:

```text
Is there runnable CPU work?

Are processes blocked?

Is memory under pressure?

Is swap active?

Is I/O activity occurring?

Are context switches increasing?

Is the CPU spending time in user/system/wait/idle states?
```

Exact fields vary by platform.

A typical output includes groups such as:

```text
procs
memory
swap
io
system
cpu
```

---

# 17. Run Queue

In common `vmstat` output:

```text
r
```

represents runnable processes/threads.

High `r` relative to CPU capacity can indicate CPU scheduling pressure.

For example:

```text
nproc = 8
r = 15
```

suggests more runnable work than available execution units at that instant.

But one sample is not enough.

Look for sustained behavior.

---

# 18. Blocked Processes

A common `vmstat` field:

```text
b
```

represents processes blocked in uninterruptible sleep.

A high value can be a clue that workloads are waiting on resources such as I/O.

Do not interpret `b` as a direct diagnosis.

Correlate with:

```bash
iostat -xz 1
```

and:

```bash
pidstat -d 1
```

---

# 19. Context Switching

Context switches occur when the CPU changes from one execution context to another.

`vmstat` commonly reports:

```text
cs
```

for context switches.

High context switching can occur for legitimate reasons.

Do not use a single number as a universal threshold.

Ask:

```text
Did context switching change?

Is the workload highly concurrent?

Are many short-lived tasks running?

Is CPU time being spent on scheduling overhead?

Is the application architecture creating excessive concurrency?
```

The important operational skill is correlation, not threshold memorization.

---

# 20. I/O Wait

I/O wait is a critical concept for Data Engineers.

A machine can have:

```text
CPU utilisation = moderate
```

while the workload remains very slow.

Why?

Because the workload may be waiting for storage.

Examples:

- Spark spill
- large database scans
- Parquet writes
- temporary sort files
- compression
- checkpoint writes
- large file reads
- log-heavy applications

A useful distinction:

```text
CPU-bound
    ↓
available compute is the bottleneck
```

versus:

```text
I/O-bound
    ↓
work is delayed by storage or another I/O path
```

High I/O wait is evidence, not a complete root cause.

---

# 21. Disk I/O Fundamentals

Storage performance has several dimensions.

Do not reduce disk performance to:

```text
"disk percentage"
```

Understand:

```text
Throughput
IOPS
Latency
Queue depth
Utilisation
```

## 21.1 Throughput

Amount of data transferred per unit time.

Example:

```text
500 MB/s
```

This matters for large sequential reads/writes.

## 21.2 IOPS

I/O operations per second.

Small random operations may be constrained by IOPS rather than raw throughput.

## 21.3 Latency

How long an I/O operation takes.

High latency can make applications slow even when throughput does not look extreme.

## 21.4 Queueing

Requests may wait because the device or storage stack is busy.

Queueing can increase latency.

## 21.5 Utilisation

A device utilization percentage indicates how busy the device was according to the tool's accounting.

It is not the same as:

```text
disk capacity used
```

That distinction is critical.

---

# 22. iostat

Basic:

```bash
iostat
```

A common diagnostic form is:

```bash
iostat -xz 1
```

The exact fields vary by `sysstat` version and platform.

Important concepts include:

- device
- reads/writes
- throughput
- IOPS
- queueing
- latency/service time
- utilization

## 22.1 Why `-xz` is useful

On systems where supported, this provides extended statistics and suppresses devices with no activity.

Always consult:

```bash
iostat --help
```

or:

```bash
man iostat
```

because option behavior can differ across versions.

## 22.2 What you are trying to establish

You are not asking:

> "Is the disk percentage high?"

You are asking:

```text
Is storage saturated?

Is latency elevated?

Is queueing elevated?

Is throughput high?

Is the workload read-heavy or write-heavy?

Which device is involved?
```

---

# 23. Disk Utilisation

Suppose:

```text
device = nvme0n1
utilisation = very high
latency = elevated
queue = elevated
```

That is stronger evidence of storage pressure than utilization alone.

Now correlate with:

```bash
pidstat -d 1
```

to identify processes generating I/O.

Then correlate with the workload:

```text
Spark spill?
PostgreSQL scan?
Parquet write?
Temporary sort?
Large file transfer?
```

---

# 24. Throughput vs IOPS vs Latency

Consider two workloads.

### Workload A: large sequential write

```text
large files
high throughput
relatively few operations
```

### Workload B: many small random writes

```text
small operations
high IOPS requirement
latency-sensitive
```

Both can stress storage differently.

A storage system can have apparently reasonable throughput while a latency-sensitive workload still performs badly.

Therefore:

```text
Throughput
≠
IOPS
≠
Latency
≠
Queue depth
```

---

# 25. Recognising Disk-Bound Workloads

Suppose:

```text
Spark job is slow.

CPU = moderate
Memory = healthy
iowait = high
Disk utilisation = high
Disk latency = high
```

A reasonable hypothesis is:

```text
storage is the bottleneck
```

But confirm it.

Use:

```bash
vmstat 1
iostat -xz 1
pidstat -d 1
```

Then identify the workload.

For example:

```text
Spark executor
    ↓
shuffle spill
    ↓
temporary disk writes
    ↓
device queue
    ↓
high latency
    ↓
task delay
```

## 25.1 Common Data Engineering causes

Disk pressure may come from:

- temporary files
- Spark spill files
- database reads
- database writes
- checkpoints
- large sorts
- compression
- logs
- concurrent jobs
- local staging
- large file transfers

The correct remediation depends on the cause.

---

# 26. pidstat

System-wide tools answer:

> "What is the machine doing?"

`pidstat` helps answer:

> **"Which process is doing it?"**

Basic:

```bash
pidstat 1
```

Depending on platform/version, CPU and I/O-oriented options can be used to focus the output.

Examples:

```bash
pidstat -u 1
```

for CPU-oriented process statistics, and:

```bash
pidstat -d 1
```

for I/O-oriented process statistics.

Consult:

```bash
pidstat --help
```

when available options differ by platform.

## 26.1 Correlation pattern

A powerful pattern is:

```text
vmstat
   +
iostat
   +
pidstat
   +
top
```

Example:

```text
vmstat → high I/O wait
iostat → busy storage device
pidstat → python process generating I/O
top → python process is part of ingestion workload
```

Now you have a defensible hypothesis.

---

# 27. Per-Process Diagnosis

Suppose:

```text
iostat
→ high disk activity
```

That does not tell you which process is responsible.

Use:

```bash
pidstat -d 1
```

Then investigate the process.

Questions:

```text
What is its PID?

Who owns it?

What command is it running?

What workload does it represent?

Is its behavior expected?

Did it recently start?

Is it generating temporary files?

Is it performing a database or Spark operation?
```

System-wide saturation plus process-level evidence is much stronger than either alone.

---

# 28. OOM Killer

The Linux kernel can invoke the Out-Of-Memory (OOM) killer when memory exhaustion becomes severe and reclaim cannot maintain safe operation.

A typical incident looks like:

```text
Memory pressure
    ↓
reclaim
    ↓
swap / severe pressure
    ↓
available memory becomes critically constrained
    ↓
kernel selects a process
    ↓
process is terminated
```

This is why a Python process may simply "disappear."

## 28.1 OOM does not mean "largest process died"

Linux considers multiple factors when choosing a victim.

Conceptually, the selection is influenced by memory importance and OOM scoring rather than a simple:

```text
kill largest PID
```

Modern kernels and cgroup contexts can also affect the scope and selection.

You should investigate the actual kernel evidence.

---

# 29. Investigating OOM with dmesg

Try:

```bash
dmesg | grep -i -E 'oom|out of memory|killed process'
```

Some environments restrict unprivileged access to kernel messages.

You may need appropriate privileges.

Example evidence might resemble:

```text
Out of memory: Killed process 2418 (python) ...
```

Do not invent exact fields from memory.

The actual kernel message is authoritative for that incident.

## 29.1 What to extract

Record:

```text
time
PID
process name
memory condition
kill event
cgroup/context if reported
```

Then correlate with:

```text
top
free -h
vmstat
application logs
systemd/journal logs
```

---

# 30. journalctl -k

Kernel messages may also be available through:

```bash
journalctl -k
```

Search:

```bash
journalctl -k | grep -i -E 'oom|out of memory|killed process'
```

This can be useful when:

- `dmesg` has limited visibility
- you need journal timestamps
- the system stores kernel messages in the journal

Again, exact output and availability depend on distribution and logging configuration.

---

# 31. Reconstructing an OOM Incident

Suppose:

```text
14:03 — pandas process starts
14:07 — memory usage rises
14:09 — swap activity increases
14:10 — memory PSI increases
14:11 — Python process disappears
14:11 — kernel log reports OOM kill
```

This gives you an evidence chain:

```text
Workload
  ↓
memory growth
  ↓
pressure
  ↓
kernel OOM decision
  ↓
process termination
```

That is an incident reconstruction.

It is much better than:

> "Python crashed."

---

# 32. Network Connections and Ports

Resource diagnosis is not only CPU, memory, and disk.

A workload can be blocked by excessive or abnormal network connections.

Use:

```bash
ss
```

A useful overview:

```bash
ss -tulpn
```

For TCP connections:

```bash
ss -tan
```

Exact visibility into process ownership can require appropriate privileges.

## 32.1 What `ss` can show

Depending on options:

- listening sockets
- established connections
- local address/port
- remote address/port
- TCP states
- process association

Important TCP states include:

```text
LISTEN
ESTABLISHED
TIME-WAIT
CLOSE-WAIT
SYN-SENT
SYN-RECV
```

Interpret states in context rather than treating one state as automatically bad.

---

# 33. Connection Leaks

Consider:

```text
Python extractor
      ↓
PostgreSQL
      ↓
connections keep increasing
```

A common cause is incorrect connection lifecycle management.

For example:

```python
connection = connect()
query(connection)
# connection never closed
```

A safer pattern is to use context management or explicit cleanup according to the database client.

The operational investigation can begin with:

```bash
ss -tan
```

Then correlate with application/database metrics.

If PostgreSQL is involved, inspect the database's own connection/activity information using the appropriate database tooling.

## 33.1 Why this becomes a resource problem

Too many connections can consume:

- process resources
- memory
- file descriptors
- database worker capacity
- network/socket resources

Therefore a connection leak can become a system-wide incident.

---

# 34. Pressure Stall Information — Advanced

Pressure Stall Information (PSI) measures how much work is delayed because resources are under pressure.

Inspect:

```bash
cat /proc/pressure/cpu
cat /proc/pressure/memory
cat /proc/pressure/io
```

PSI is valuable because utilization alone does not always describe the user-visible impact of contention.

A simple mental model:

```text
Utilisation
→ How busy is the resource?

PSI
→ How much work is actually being delayed because of pressure?
```

---

# 35. PSI: `some` and `full`

Typical PSI output contains fields such as:

```text
some avg10=... avg60=... avg300=... total=...
full avg10=... avg60=... avg300=... total=...
```

Conceptually:

- `some` indicates that at least some eligible work was stalled.
- `full` indicates a stronger condition in which the relevant workload is fully stalled under the metric's definition.

The exact interpretation is resource-specific.

Do not memorize a universal threshold.

Use PSI as another evidence stream.

---

# 36. CPU PSI

Inspect:

```bash
cat /proc/pressure/cpu
```

CPU pressure can reveal contention that a simple CPU percentage may not communicate clearly.

For example:

```text
CPU utilisation is high
+
CPU PSI is elevated
```

supports a stronger contention hypothesis.

But:

```text
CPU utilisation is moderate
+
CPU PSI is elevated
```

may still indicate meaningful scheduling pressure depending on workload and measurement semantics.

---

# 37. Memory PSI

Inspect:

```bash
cat /proc/pressure/memory
```

Memory PSI can help distinguish:

```text
RAM is used
```

from:

```text
work is actually being delayed by memory pressure
```

This is especially useful for:

- pandas workloads
- large Python processes
- concurrent batch jobs
- containers with memory limits

---

# 38. I/O PSI

Inspect:

```bash
cat /proc/pressure/io
```

I/O PSI can complement:

```bash
vmstat 1
iostat -xz 1
pidstat -d 1
```

A strong storage diagnosis often combines:

```text
I/O wait / blocked work
+
storage latency/queueing
+
process-level I/O
+
I/O PSI
```

No single metric is always sufficient.

---

# 39. Historical Monitoring with sar

Real-time tools answer:

> "What is happening now?"

Production incidents often ask:

> **"What happened at 3 a.m.?"**

If the incident is over, `top` cannot show you the past.

Historical monitoring requires data to have been collected.

A common Linux solution is:

```text
sysstat
   ↓
sar
```

---

# 40. sysstat

`sysstat` provides performance-collection and reporting utilities on many Linux distributions.

Installation and service setup vary by distribution.

After installation, verify your environment rather than assuming a particular package-management or collection-service configuration.

Use:

```bash
sar --help
```

and:

```bash
man sar
```

to inspect available metrics.

---

# 41. sar Examples

Common examples include:

```bash
sar -q
```

for load/run-queue related information,

```bash
sar -r
```

for memory utilization information,

```bash
sar -S
```

for swap-related information on systems that support it,

```bash
sar -W
```

for swapping activity on systems that support it,

```bash
sar -b
```

for I/O transfer statistics, and:

```bash
sar -n DEV
```

for network device statistics.

Exact options and fields can vary by `sysstat` version.

## 41.1 Historical diagnosis

Suppose:

```text
03:00 incident
09:00 investigation
```

At 09:00:

```text
CPU = normal
Memory = normal
Disk = normal
```

That does not mean the incident did not happen.

Use historical data:

```text
sar
   ↓
03:00–03:30
   ↓
load
CPU
memory
swap
I/O
network
```

Then correlate with application logs and service logs.

---

# 42. Real-Time vs Historical Monitoring

| Question | Best starting point |
|---|---|
| What is happening now? | `top`, `vmstat`, `iostat`, `pidstat` |
| What is the load? | `uptime` |
| How much memory is available? | `free -h` |
| Which process is active? | `top`, `pidstat` |
| What happened three hours ago? | `sar` |
| Did the kernel report an OOM event? | `dmesg`, `journalctl -k` |
| What connections exist? | `ss` |

The operational lesson is:

> **Real-time tools diagnose the present; historical telemetry reconstructs the past.**

---

# 43. cgroups — Advanced

Linux control groups, or **cgroups**, provide mechanisms for grouping processes and accounting for and controlling resource usage.

A useful conceptual model:

```text
Process
   ↓
cgroup
   ↓
kernel resource accounting/enforcement
```

Cgroups are important because modern Data Engineering environments frequently use:

- containers
- systemd services
- resource limits
- isolated workloads

---

# 44. cgroups and systemd

A systemd-managed service can be associated with a cgroup.

Conceptually:

```text
systemd service
      ↓
resource configuration
      ↓
cgroup
      ↓
kernel enforcement
```

This connects Topic 05 with Topic 06.

For example, a service can have CPU or memory limits configured through systemd.

The exact configuration and available controls depend on the systemd version and cgroup hierarchy.

---

# 45. Containers and Resource Limits

Container platforms commonly use cgroups to enforce limits.

Conceptually:

```text
Container
   ↓
processes
   ↓
cgroup
   ↓
CPU / memory constraints
```

This explains an important diagnostic trap:

> A process can appear to have plenty of host capacity available while being constrained by its container or service-level limit.

Therefore, when diagnosing a containerized workload, consider:

```text
host capacity
+
container limit
+
actual container usage
```

Do not assume host-level `free` or CPU availability tells the entire story.

This module does not teach full Docker or Kubernetes administration.

---

# 46. Metrics Systems and Node Exporter Awareness

Command-line tools are excellent for immediate diagnosis.

Production platforms also need:

- historical visibility
- dashboards
- alerting
- trends
- fleet-level monitoring

A common architecture is:

```text
Linux host
   ↓
node exporter
   ↓
metrics
   ↓
Prometheus
   ↓
dashboard / alerting
```

This module only introduces the architecture.

It is not a Prometheus or Grafana course.

## 46.1 Why both are needed

CLI tools:

```text
fast
local
interactive
excellent during incidents
```

Metrics systems:

```text
historical
centralized
fleet-wide
alertable
trend-oriented
```

A strong Data Engineer needs both operational skills.

---

# 47. The Core Diagnosis Method

This is the most important section of the module.

Use:

```text
SYMPTOM
   ↓
MEASURE
   ↓
IDENTIFY SATURATED RESOURCE
   ↓
IDENTIFY RESPONSIBLE PROCESS
   ↓
UNDERSTAND WHY
   ↓
APPLY SAFE FIX
   ↓
VERIFY
   ↓
DOCUMENT
```

## 47.1 Step 1 — Describe the symptom

Bad:

```text
Server is broken.
```

Better:

```text
PostgreSQL query latency increased from 200 ms to 8 s.
```

Better still:

```text
At 14:05 UTC, API extraction latency increased 10×.
The issue affects all concurrent extraction workers.
```

Specific symptoms produce better investigations.

## 47.2 Step 2 — Measure

Start with broad evidence.

A useful first pass may include:

```bash
date
uptime
nproc
free -h
vmstat 1 5
top -b -n 1 | head -n 30
```

Then move to the suspected resource.

Do not run a huge command collection blindly.

The next command should answer a question.

## 47.3 Step 3 — Identify the saturated resource

Classify the evidence:

```text
CPU
Memory
I/O
Network/connections
Application
Unknown
```

## 47.4 Step 4 — Identify the responsible process

Use:

```bash
top
pidstat 1
```

and, when needed:

```bash
ps
```

or service/container-specific tools.

## 47.5 Step 5 — Understand why

Ask:

```text
What workload is running?

Is the behavior expected?

What changed?

Did concurrency increase?

Did input size increase?

Did a deployment change behavior?

Did storage become slower?

Did a limit change?

Is there a leak?
```

## 47.6 Step 6 — Apply a safe fix

Potential actions include:

```text
tune
limit
reduce concurrency
move workload
fix application
fix query
fix connection handling
increase capacity
scale
```

## 47.7 Step 7 — Verify

Never stop at:

> "I changed something."

Verify:

```text
resource pressure decreased
+
application latency improved
+
error rate improved
+
no new failure appeared
```

## 47.8 Step 8 — Document

Record:

```text
symptom
evidence
root cause
fix
verification
follow-up
```

---

# 48. Which Tool Answers Which Question?

| Question | Tool | What to look for | Limitation |
|---|---|---|---|
| How many CPUs? | `nproc` | logical CPU count | does not measure load |
| What is system load? | `uptime` | 1/5/15-minute load | load is not CPU % |
| Which process uses CPU/RAM? | `top` | PID, CPU%, memory%, state | snapshot/live view, not historical |
| How much memory is available? | `free -h` | `available`, swap | not a process-level explanation |
| Is system pressure occurring? | `vmstat` | run queue, blocked work, swap, CPU | needs correlation |
| Is storage saturated? | `iostat` | utilization, latency, queueing, throughput | does not identify application cause alone |
| Which process generates I/O? | `pidstat` | per-process CPU/I/O | may need workload correlation |
| Was a process OOM-killed? | `dmesg`, `journalctl -k` | OOM/kernel evidence | access/retention varies |
| What connections exist? | `ss` | listening/established states | not an application diagnosis |
| Is work stalled by pressure? | `/proc/pressure/*` | PSI | interpretation requires context |
| What happened earlier? | `sar` | historical resource metrics | only as good as collected history |
| What limits apply? | cgroups/systemd/container inspection | CPU/memory boundaries | implementation differs |
| What does the fleet look like? | metrics systems | trends/alerts/dashboards | requires telemetry infrastructure |

---

# 49. Data Engineering Failure Scenarios

## Scenario 1 — CPU Saturation

### Symptom

A large transformation suddenly becomes slow.

### Investigation

Start:

```bash
uptime
nproc
```

Then:

```bash
vmstat 1
```

and:

```bash
top
```

Then:

```bash
pidstat -u 1
```

### Reasoning

Suppose:

```text
nproc = 8
load = 14
run queue is consistently high
CPU utilization is near capacity
python process dominates CPU
```

Hypothesis:

```text
CPU saturation caused by Python workload
```

But verify:

- Is the process expected?
- Did input size change?
- Did concurrency increase?
- Is another process competing?

---

## Scenario 2 — Memory Pressure

### Symptom

A pandas transformation becomes progressively slower.

Investigate:

```bash
free -h
vmstat 1
top
cat /proc/pressure/memory
```

Evidence might show:

```text
available memory falling
swap-in/swap-out increasing
memory PSI elevated
python process consuming most RAM
```

Hypothesis:

```text
memory pressure
```

Next question:

```text
Why did memory consumption increase?
```

Potential causes:

- larger input
- inefficient DataFrame representation
- accidental data duplication
- concurrency increase
- memory leak
- resource limit

---

## Scenario 3 — OOM Killer

### Symptom

A Python process disappears unexpectedly.

Investigate:

```bash
dmesg | grep -i -E 'oom|out of memory|killed process'
```

and:

```bash
journalctl -k | grep -i -E 'oom|out of memory|killed process'
```

Identify:

```text
time
PID
process
memory condition
kill event
```

Then correlate with:

```bash
free -h
vmstat 1
top
```

---

## Scenario 4 — Disk-Bound Data Job

### Symptom

A large sort is extremely slow.

Run:

```bash
vmstat 1
```

then:

```bash
iostat -xz 1
```

then:

```bash
pidstat -d 1
```

Suppose:

```text
CPU moderate
memory healthy
iowait high
storage latency high
device utilization high
```

Hypothesis:

```text
storage bottleneck
```

Now identify the process and the reason for its I/O.

---

## Scenario 5 — Connection Leak

### Symptom

A Python extractor repeatedly opens database connections.

Start:

```bash
ss -tan
```

Look for abnormal growth in relevant states and remote endpoints.

Correlate with:

```text
application logs
database connection/activity metrics
connection-pool configuration
```

Then:

```text
stop leak
↓
close/release connections
↓
verify connection count stabilizes
```

---

## Scenario 6 — Historical Incident

### Symptom

The server was slow at 03:00 but is healthy now.

Real-time commands may show nothing unusual.

Use historical data:

```bash
sar -q
sar -r
sar -S
sar -W
sar -b
sar -n DEV
```

where supported.

Then correlate timestamps with:

```text
system logs
service logs
application logs
deployment events
scheduled jobs
```

---

# 50. Hands-On Lab — `server_lab/06/`

Create:

```text
server_lab/
└── 06/
    ├── README.md
    ├── cpu/
    ├── io/
    ├── memory/
    ├── connections/
    ├── historical/
    ├── break-fix/
    └── runbook.md
```

Use a disposable Linux practice environment.

> **Run only on a disposable practice environment. Never run stress/OOM experiments on production.**

---

# 51. Lab 1 — CPU-Heavy Workload

The goal is to create controlled CPU activity and diagnose it.

A safe example is a bounded Python computation.

```bash
python3 - <<'PY'
import hashlib

data = b"x" * 1024
for i in range(500000):
    hashlib.sha256(data + str(i).encode()).digest()
print("done")
PY
```

Do not use an unbounded loop on a production system.

While it runs, observe:

```bash
uptime
nproc
top
vmstat 1
pidstat -u 1
```

Record:

```text
CPU count:
Load:
Run queue:
CPU utilization:
Responsible PID:
Command:
Duration:
```

Then answer:

```text
Is CPU saturated?

How do you know?

Which process is responsible?

Is the CPU usage expected?
```

---

# 52. Lab 2 — Disk-Heavy Workload

Use a disposable filesystem and bounded data.

For example, create a moderate test file:

```bash
dd if=/dev/zero of=/tmp/io-lab.bin bs=1M count=512 status=progress
```

Then read it:

```bash
dd if=/tmp/io-lab.bin of=/dev/null bs=1M status=progress
```

Observe:

```bash
vmstat 1
iostat -xz 1
pidstat -d 1
```

Do not assume the workload will saturate every storage system.

Your objective is diagnosis, not maximum destruction.

Answer:

```text
Is the workload CPU-bound or I/O-bound?

What evidence supports your conclusion?

Which device is involved?

Which process generates I/O?
```

Clean up:

```bash
rm -f /tmp/io-lab.bin
```

---

# 53. Lab 3 — Controlled Memory Pressure

Memory experiments can destabilize a server.

Use:

- a disposable VM,
- a constrained container/cgroup,
- or another isolated lab environment.

Do **not** run an uncontrolled memory allocator on a production server.

First observe:

```bash
free -h
vmstat 1
cat /proc/pressure/memory
```

Then create **bounded** memory pressure appropriate to your lab's available RAM.

If demonstrating an actual OOM event, use a disposable environment and explicitly understand the resource boundary before starting.

Afterward inspect:

```bash
dmesg | grep -i -E 'oom|out of memory|killed process'
```

and:

```bash
journalctl -k | grep -i -E 'oom|out of memory|killed process'
```

Record:

```text
pressure before
pressure during
swap behavior
OOM evidence
PID
process
recovery behavior
```

> **Never run an uncontrolled OOM experiment on production.**

---

# 54. Lab 4 — Connection Leak

If PostgreSQL is available in the practice environment, create a deliberately bounded test script that opens connections and holds them briefly.

Illustrative pattern:

```python
import time
import psycopg

connections = []

for _ in range(5):
    connections.append(
        psycopg.connect(
            "host=127.0.0.1 port=5432 dbname=lab user=lab"
        )
    )
    time.sleep(1)

print("Connections held for 60 seconds")
time.sleep(60)

for conn in connections:
    conn.close()
```

Use lab credentials only.

Observe:

```bash
ss -tan
```

If permitted, correlate with PostgreSQL activity information.

Then verify:

```text
connections increase
→ script ends
→ connections close
→ connection count returns toward baseline
```

The point is to learn lifecycle diagnosis, not to create a production outage.

---

# 55. Lab 5 — Historical Investigation

Install and configure `sysstat` according to your Linux distribution.

Generate a controlled workload.

Collect data.

Later, investigate with:

```bash
sar -q
sar -r
sar -S
sar -W
sar -b
sar -n DEV
```

Answer:

```text
What happened?

When?

Was CPU elevated?

Was memory pressure visible?

Was swap active?

Was I/O elevated?

Was network activity unusual?
```

The exercise is complete only when you can support the answer with historical evidence.

---

# 56. Lab 6 — First-Five-Commands Exercise

Scenario:

```text
"The server is slow."
```

Do not memorize a universal sequence.

Instead choose five commands and justify each one.

A reasonable starting set on a generic Linux server might be:

```bash
uptime
nproc
free -h
vmstat 1 5
top -b -n 1 | head -n 30
```

But a different first-five sequence can be correct when the symptom is more specific.

For example, if the incident is explicitly:

> "Storage writes are timing out."

you may prioritize:

```bash
iostat -xz 1 5
pidstat -d 1 5
df -h
```

The learning objective is **reasoned command selection**.

---

# 57. Break/Fix Exercises

For every exercise, record:

```text
Symptom
Evidence
Hypothesis
Command
Observation
Root cause
Fix
Verification
Runbook entry
```

## Break/Fix 1 — Unexpected CPU-Heavy Process

Create or identify a bounded CPU-heavy process.

Diagnose:

```text
uptime
nproc
top
pidstat
vmstat
```

Determine:

```text
expected or unexpected?
responsible PID?
root cause?
safe action?
```

---

## Break/Fix 2 — Memory Pressure and Swap

Create controlled memory pressure in a disposable environment.

Diagnose:

```text
free
vmstat
PSI
top
```

Determine:

```text
normal cache use or real pressure?
active swap or historical swap?
responsible process?
```

---

## Break/Fix 3 — High I/O Wait

Create a bounded I/O workload.

Diagnose:

```text
vmstat
iostat
pidstat
```

Determine:

```text
device?
latency?
queue?
responsible process?
```

---

## Break/Fix 4 — OOM-Killed Process

Use an isolated environment.

Find kernel evidence:

```bash
dmesg
journalctl -k
```

Determine:

```text
time
PID
process
memory condition
kill event
```

---

## Break/Fix 5 — Database Connections Piling Up

Use a disposable PostgreSQL environment.

Observe:

```bash
ss -tan
```

Then correlate with application/database evidence.

Determine:

```text
normal connection pool behavior?
leak?
unexpected concurrency?
```

---

## Break/Fix 6 — Historical Slowdown

Simulate or use recorded telemetry.

The server is healthy now.

Use:

```bash
sar
```

to determine what happened during the historical window.

---

# 58. Troubleshooting Decision Tree

Use this production-style decision tree as a starting point:

```text
SERVER IS SLOW
      |
      +--> Is CPU pressure plausible?
      |       |
      |       +--> uptime + nproc
      |       |
      |       +--> vmstat + top + pidstat
      |       |
      |       +--> identify CPU-heavy process
      |
      +--> CPU not clearly saturated?
      |       |
      |       +--> Is I/O wait / blocked work elevated?
      |               |
      |               +--> vmstat
      |               +--> iostat
      |               +--> pidstat -d
      |               +--> identify storage/process
      |
      +--> Is memory availability falling?
      |       |
      |       +--> free -h
      |       +--> vmstat
      |       +--> memory PSI
      |       |
      |       +--> Is swap actively moving?
      |               |
      |               +--> investigate memory pressure
      |
      +--> Did a process disappear?
      |       |
      |       +--> dmesg
      |       +--> journalctl -k
      |       |
      |       +--> OOM evidence?
      |
      +--> Are connections abnormal?
      |       |
      |       +--> ss
      |       +--> application/database evidence
      |
      +--> Is the incident over now?
              |
              +--> sar
              +--> logs
              +--> deployment/scheduled-job timeline
```

## 58.1 Important rule

Do not force the incident into the first branch that looks plausible.

For example:

```text
load high
```

does not automatically mean:

```text
CPU root cause
```

Use multiple signals.

---

# 59. First Five Commands When a Server Is Slow

There is no universal sequence, but for a generic Linux server a strong initial baseline is:

```bash
uptime
nproc
free -h
vmstat 1 5
top -b -n 1 | head -n 30
```

## 59.1 Why these commands?

### `uptime`

Question:

> Is system load elevated?

### `nproc`

Question:

> How much CPU capacity is exposed?

### `free -h`

Question:

> Is memory availability concerning?

### `vmstat 1 5`

Question:

> Is the system showing runnable, blocked, swap, I/O, or CPU pressure?

### `top`

Question:

> Which process appears responsible?

Then branch into:

```bash
iostat -xz 1
pidstat -d 1
ss -tan
dmesg
journalctl -k
sar
```

as evidence dictates.

---

# 60. Production Runbook — Linux Server Is Slow

## Symptom

Users report:

```text
API slow
batch job slow
Spark job delayed
database query latency increased
server unresponsive
```

Record:

```text
start time
affected workload
affected users
first observed symptom
recent changes
```

## First Evidence

Run appropriate baseline checks:

```bash
date
uptime
nproc
free -h
vmstat 1 5
top -b -n 1 | head -n 30
```

Capture output where operational policy permits.

## CPU Investigation

Use:

```bash
uptime
nproc
vmstat 1
top
pidstat -u 1
```

Look for:

```text
high sustained CPU
high runnable queue
CPU-heavy process
unexpected concurrency
```

Do not treat high CPU as automatically bad.

## Memory Investigation

Use:

```bash
free -h
vmstat 1
cat /proc/pressure/memory
top
```

Look for:

```text
low available memory
reclaim pressure
active swapping
high memory PSI
large process
```

## I/O Investigation

Use:

```bash
vmstat 1
iostat -xz 1
pidstat -d 1
cat /proc/pressure/io
```

Look for:

```text
high wait
high latency
queueing
high device utilization
responsible process
```

## Process Investigation

Use:

```bash
top
pidstat
```

Then determine:

```text
PID
owner
command
service
workload
resource behavior
```

## Network/Connection Investigation

Use:

```bash
ss -tan
ss -tulpn
```

where appropriate.

Look for:

```text
unexpected connection growth
abnormal TCP states
unexpected listening sockets
remote endpoint concentration
```

Correlate with application/database evidence.

## Kernel/OOM Investigation

Use:

```bash
dmesg
journalctl -k
```

Search:

```bash
dmesg | grep -i -E 'oom|out of memory|killed process'
```

and:

```bash
journalctl -k | grep -i -E 'oom|out of memory|killed process'
```

Record kernel evidence.

## Historical Investigation

If the incident is no longer active:

```bash
sar -q
sar -r
sar -S
sar -W
sar -b
sar -n DEV
```

Then correlate timestamps with logs.

## Root-Cause Classification

Classify as:

```text
CPU-bound
Memory-bound
I/O-bound
Connection-bound
Application-bound
Unknown
```

If unknown, explicitly document what evidence is missing.

## Safe Remediation

Potential actions:

```text
tune
limit
reduce concurrency
move workload
fix application
fix query
fix connection handling
increase capacity
scale
```

Choose the least risky action that addresses the demonstrated cause.

## Verification

Confirm:

```text
resource pressure reduced
workload latency improved
error rate improved
no secondary failure introduced
```

## Documentation

Record:

```text
symptom
timeline
commands/evidence
hypothesis
root cause
remediation
verification
follow-up
```

---

# 61. Safe Remediation Decision Framework

Do not jump from:

```text
resource high
```

to:

```text
kill process
```

Instead ask:

```text
Is the process expected?

Who owns it?

What workload is it running?

What will happen if I stop it?

Is there a safer way to reduce pressure?

Is there an approved runbook?

Is this production or a lab?

Can I preserve evidence first?
```

Possible actions:

### Tune

Change a workload configuration when the root cause is a known inefficiency.

### Limit

Apply an appropriate resource boundary.

### Reduce concurrency

Prevent multiple jobs from competing for the same scarce resource.

### Move workload

Run the job on a more appropriate host.

### Fix application

Correct a leak or inefficient processing pattern.

### Fix query

Optimize a demonstrated database bottleneck.

### Fix connection handling

Close or pool connections correctly.

### Increase capacity

Add resources when demand is legitimate and sustained.

### Scale

Use horizontal or vertical scaling where the platform supports it.

---

# 62. Common Mistakes

## 62.1 Panicking about low `free` memory

Wrong:

```text
free = 500 MiB
→ server is out of memory
```

Why dangerous:

Linux uses RAM for useful cache.

Better:

```bash
free -h
vmstat 1
cat /proc/pressure/memory
```

---

## 62.2 Treating load average as CPU percentage

Wrong:

```text
load = 10
→ CPU = 100%
```

Why wrong:

Load includes runnable work and certain blocked states.

Always compare with:

```bash
nproc
vmstat
```

---

## 62.3 Ignoring CPU count

A load of 4 means different things on:

```text
2 CPUs
8 CPUs
32 CPUs
```

---

## 62.4 Looking at CPU only

A workload can be slow because of:

```text
memory
I/O
connections
application behavior
```

---

## 62.5 Ignoring I/O wait

Low user CPU does not prove the system is healthy.

Storage waits can dominate latency.

---

## 62.6 Ignoring swap

Do not panic over any swap usage.

Do not ignore sustained swap activity either.

Investigate:

```text
si/so
memory PSI
available memory
process memory
```

---

## 62.7 Assuming low CPU means a healthy server

A server with:

```text
CPU = 20%
I/O wait = high
```

can still be severely constrained.

---

## 62.8 Assuming high CPU automatically means root cause

High CPU may be expected.

The application may be performing exactly the computation it was designed to perform.

The question is whether CPU contention explains the symptom.

---

## 62.9 Restarting before collecting evidence

Restarting may erase:

- process state
- transient metrics
- kernel context
- useful application state

Collect evidence first when operationally safe.

---

## 62.10 Killing processes without understanding ownership

A process may belong to:

- systemd
- Airflow
- a container
- Spark
- PostgreSQL
- another operator

Stopping it manually can create a second incident.

---

## 62.11 Ignoring OOM evidence

If a process disappears, check the kernel.

Do not automatically assume:

```text
application bug
```

or:

```text
network problem
```

---

## 62.12 Ignoring historical metrics

A normal server at 09:00 does not prove it was normal at 03:00.

---

## 62.13 Looking only at system-wide metrics

System-wide:

```text
disk busy
```

is not enough.

Find:

```text
which process?
```

---

## 62.14 Confusing throughput with latency

A disk can sustain high throughput while a latency-sensitive workload still experiences unacceptable latency.

---

## 62.15 Confusing disk utilization with disk capacity

These are different:

```text
device busy
```

and:

```text
filesystem full
```

Disk capacity investigation belongs to later filesystem/disk-management material, while this topic focuses on performance behavior.

---

## 62.16 Treating `ss` as a complete application diagnosis

`ss` tells you about sockets and TCP state.

It does not by itself explain:

```text
why connections exist
```

---

## 62.17 Stress-testing memory on production

This can cause:

- OOM
- service failure
- cascading outages
- data loss depending on workload behavior

Use a disposable environment.

---

# 63. Command Reference

## `uptime`

**Purpose:** load and uptime overview.

```bash
uptime
```

**Look at:** 1/5/15-minute load.

**Use when:** starting an investigation.

**Cannot tell you:** root cause.

---

## `nproc`

**Purpose:** available logical CPU count.

```bash
nproc
```

**Look at:** number of processing units visible to the command.

**Use when:** interpreting load/CPU pressure.

**Cannot tell you:** current CPU saturation.

---

## `top`

**Purpose:** live process/system view.

```bash
top
```

**Look at:** PID, CPU%, memory%, state, command.

**Use when:** identifying resource-heavy processes.

**Cannot tell you:** historical behavior.

---

## `free -h`

**Purpose:** memory overview.

```bash
free -h
```

**Look at:** available, cache, swap.

**Use when:** diagnosing memory pressure.

**Cannot tell you:** which process is responsible.

---

## `vmstat`

**Purpose:** system-wide virtual memory, process, I/O, and CPU behavior.

```bash
vmstat 1
```

**Look at:** run queue, blocked work, swap, I/O, context switches, CPU.

**Use when:** determining what the system is waiting on.

**Cannot tell you:** complete application-level root cause.

---

## `iostat`

**Purpose:** storage/device performance.

```bash
iostat -xz 1
```

**Look at:** utilization, throughput, latency, queueing.

**Use when:** investigating I/O bottlenecks.

**Cannot tell you:** which application is responsible by itself.

---

## `pidstat`

**Purpose:** per-process resource statistics.

```bash
pidstat 1
```

CPU:

```bash
pidstat -u 1
```

I/O:

```bash
pidstat -d 1
```

**Look at:** process-specific activity.

**Use when:** connecting system-wide symptoms to a process.

**Cannot tell you:** business-level root cause without application context.

---

## `ss`

**Purpose:** socket and connection inspection.

```bash
ss -tan
```

Listening sockets:

```bash
ss -tulpn
```

**Look at:** endpoints and TCP states.

**Use when:** investigating connections and ports.

**Cannot tell you:** why the application created each connection.

---

## `dmesg`

**Purpose:** kernel message inspection.

```bash
dmesg
```

**Look at:** OOM, device, kernel, and hardware-related messages.

**Use when:** investigating kernel-level events.

**Cannot tell you:** full application history.

---

## `journalctl -k`

**Purpose:** kernel journal messages.

```bash
journalctl -k
```

**Look at:** kernel events with journal context.

**Use when:** reconstructing kernel incidents.

**Cannot tell you:** events that were never logged/retained.

---

## PSI

```bash
cat /proc/pressure/cpu
cat /proc/pressure/memory
cat /proc/pressure/io
```

**Purpose:** resource pressure/stall information.

**Use when:** determining how much work is being delayed.

**Cannot tell you:** complete root cause without correlation.

---

## `sar`

Examples:

```bash
sar -q
sar -r
sar -S
sar -W
sar -b
sar -n DEV
```

**Purpose:** historical performance reporting.

**Use when:** investigating past incidents.

**Cannot tell you:** history that was never collected.

---

# 64. Practice Questions

## Conceptual

1. Why is "the server is slow" not a diagnosis?
2. What is the difference between physical cores and logical CPUs?
3. Why must load average be interpreted relative to CPU count?
4. Why is load average not equivalent to CPU percentage?
5. What is the difference between free and available memory?
6. Why does Linux use page cache?
7. What is swap?
8. Why is swap usage not automatically a failure?
9. What is I/O wait?
10. What is the difference between throughput, IOPS, and latency?
11. What is a run queue?
12. What does `pidstat` add beyond `top`?
13. What is the OOM killer?
14. Why is the largest process not necessarily the OOM victim?
15. What does PSI measure?
16. Why is historical monitoring important?
17. What are cgroups?
18. Why do containers care about cgroups?
19. Why can low CPU coexist with severe application latency?
20. Why should evidence be collected before restarting?

## Command Interpretation

### Question 1

```text
nproc
8
```

What does this tell you?

### Question 2

```text
load average: 12.0, 11.5, 10.8
```

Is the machine necessarily CPU-saturated?

What additional evidence do you need?

### Question 3

```text
Mem:
total       16Gi
free         1Gi
buff/cache   8Gi
available    7Gi
```

Is this necessarily a memory emergency?

Explain.

### Question 4

```text
vmstat
r = 16
b = 0
```

On an 8-CPU system, what hypothesis does this support?

### Question 5

```text
vmstat
r = 2
b = 10
```

What should you investigate next?

### Question 6

```text
CPU = moderate
iowait = high
disk utilization = high
disk latency = high
```

What is your leading hypothesis?

What command should you run to identify the responsible process?

### Question 7

```text
free -h
Swap used = 2Gi
```

Can you conclude that the server is currently thrashing?

Why or why not?

### Question 8

A Python process disappears.

Which commands can provide kernel evidence?

### Question 9

A database application's connection count increases every minute.

What would you inspect?

### Question 10

The incident ended three hours ago.

Which tool may provide historical resource evidence?

---

# 65. Scenario-Based Practice

## Scenario A — CPU

A Spark job is slow.

Evidence:

```text
nproc = 16
load = 18
CPU utilization ≈ 95%
run queue consistently elevated
one Spark process consumes most CPU
```

Answer:

1. Is CPU saturation plausible?
2. Which evidence supports it?
3. What would you investigate next?
4. Is high CPU necessarily a bug?

---

## Scenario B — Memory

A pandas process becomes progressively slower.

Evidence:

```text
available memory falling
swap-in increasing
memory PSI increasing
Python process grows continuously
```

Answer:

1. What resource is under pressure?
2. What process is likely responsible?
3. What application-level questions should you ask?
4. What remediation options exist?

---

## Scenario C — Storage

A large Parquet write becomes very slow.

Evidence:

```text
CPU = 35%
memory = healthy
iowait = elevated
device utilization = high
latency = elevated
pidstat shows Python writing heavily
```

Answer:

1. Is CPU the bottleneck?
2. What resource is likely saturated?
3. What evidence should be preserved?
4. What workload changes could reduce pressure?

---

## Scenario D — OOM

A Python process disappeared.

Evidence:

```text
journalctl -k
→ Out of memory
→ Killed process ... python ...
```

Answer:

1. What happened?
2. What additional evidence should you collect?
3. Why should you avoid simply restarting without investigation?
4. What application-level causes should you consider?

---

## Scenario E — Connections

A PostgreSQL host reports increasing connections.

Evidence:

```text
ss -tan
→ increasing ESTABLISHED connections
```

Answer:

1. Is this sufficient to prove a connection leak?
2. What application evidence is needed?
3. What database evidence is needed?
4. What safe mitigation may be appropriate?

---

## Scenario F — Historical

At 03:00 a batch pipeline was slow.

At 09:00:

```text
CPU normal
memory normal
I/O normal
```

Answer:

1. Why does this not disprove the incident?
2. What historical data would you inspect?
3. What logs should be correlated with the timestamp?

---

# 66. Interview Practice

## Beginner

### 1. What is load average?

**Model answer:**  
Load average is a measure of runnable work plus certain tasks waiting in uninterruptible states. It is reported over 1, 5, and 15 minutes and must be interpreted relative to available CPU capacity. It is not simply CPU utilization.

### 2. What does `nproc` tell you?

**Model answer:**  
It reports the number of processing units available to the command's environment. It is useful when interpreting load and CPU capacity.

### 3. Why can Linux have low free memory and still be healthy?

**Model answer:**  
Linux uses otherwise-unused memory for page cache and buffers. The `available` estimate is generally more useful for determining how much memory can be made available to workloads.

### 4. What is swap?

**Model answer:**  
Swap is storage-backed space used as part of Linux memory management. Active swapping can become expensive because storage is much slower than RAM.

### 5. What is I/O wait?

**Model answer:**  
It represents CPU time associated with waiting for I/O completion under Linux CPU accounting. High I/O wait can indicate that workloads are being delayed by storage or another I/O path.

---

## Intermediate

### 6. How do you determine whether a job is CPU-bound or I/O-bound?

**Model answer:**  
Correlate multiple signals. Use `uptime` and `nproc` for load/capacity, `vmstat` for runnable and blocked work and CPU states, `iostat` for storage behavior, and `pidstat`/`top` to identify the process. A CPU-bound workload typically shows sustained compute contention, while an I/O-bound workload shows evidence of storage or I/O waiting.

### 7. How do you use `vmstat`?

**Model answer:**  
I use it as a system-wide correlation tool. I inspect the run queue, blocked processes, swap activity, I/O behavior, context switches, and CPU states, preferably as a time series with `vmstat 1`.

### 8. What does `iostat` tell you?

**Model answer:**  
It reports device-level I/O activity such as throughput, operations, queueing, latency/service time, and utilization. It helps determine whether storage is a bottleneck.

### 9. How do you identify the process causing high I/O?

**Model answer:**  
First establish that I/O pressure exists with `vmstat` and `iostat`, then use `pidstat -d` and process information to identify the workload generating I/O.

### 10. How do you investigate an OOM kill?

**Model answer:**  
Inspect kernel evidence using `dmesg` and `journalctl -k`, identify the time, PID, process name, and memory condition, then correlate with `free`, `vmstat`, PSI, process metrics, and application logs.

### 11. How would you investigate database connections piling up?

**Model answer:**  
Use `ss` to inspect socket and connection states, then correlate the connection growth with application connection-pool behavior and database activity. I would determine whether the growth is expected concurrency or a lifecycle/leak problem before changing limits.

---

## Advanced

### 12. Why can load average be high while CPU utilization is not?

**Model answer:**  
Load includes runnable work and certain uninterruptible states. A system can therefore accumulate load from tasks waiting on I/O even when CPU execution itself is not fully saturated.

### 13. How does PSI differ from utilization metrics?

**Model answer:**  
Utilization describes how busy a resource is, while PSI describes how much work is delayed because of resource pressure. PSI can therefore provide a more direct signal of contention impact.

### 14. How do cgroups relate to container resource limits?

**Model answer:**  
Cgroups provide kernel-level grouping and accounting/enforcement mechanisms. Container runtimes commonly use them to apply CPU and memory boundaries to groups of processes.

### 15. How would you investigate a slowdown that occurred three hours ago?

**Model answer:**  
Use historical telemetry such as `sar`, if it was configured and retained, then correlate resource trends with system, service, and application logs and with scheduled jobs or deployment events.

### 16. How do you distinguish application latency from system resource saturation?

**Model answer:**  
Measure both. If system-wide resource pressure and process-level evidence correlate with the latency window, resource saturation is more likely. If resources remain healthy while application latency increases, investigate application behavior, dependencies, database/query performance, or external services.

### 17. How would you design a production diagnosis workflow?

**Model answer:**

```text
Symptom
→ baseline measurements
→ classify resource
→ identify process
→ correlate with workload
→ identify change/cause
→ choose safe remediation
→ verify
→ document
```

The workflow should preserve evidence and avoid reflexive restarts.

---

# 67. Final Knowledge Check

You should be able to answer **yes** to all of these before considering Topic 06 complete.

- Can I interpret load average relative to CPU count?
- Can I distinguish load average from CPU percentage?
- Can I use `uptime`?
- Can I use `nproc`?
- Can I identify CPU-heavy processes with `top`?
- Can I distinguish free memory from available memory?
- Can I interpret buffers/cache?
- Can I use `free -h`?
- Can I identify memory pressure?
- Can I identify active swap behavior?
- Can I explain why low free memory may be normal?
- Can I use `vmstat`?
- Can I interpret the run queue?
- Can I interpret blocked processes?
- Can I explain I/O wait?
- Can I use `iostat`?
- Can I distinguish throughput, IOPS, latency, and utilization?
- Can I recognize a disk-bound workload?
- Can I use `pidstat`?
- Can I connect system-wide pressure to a responsible process?
- Can I investigate OOM kills?
- Can I use `dmesg`?
- Can I use `journalctl -k`?
- Can I inspect network connections with `ss`?
- Can I recognize a possible connection leak?
- Can I use PSI?
- Can I explain `some` and `full` conceptually?
- Can I investigate historical problems with `sar`?
- Can I explain the role of `sysstat`?
- Can I explain cgroups at a practical level?
- Can I explain container/systemd resource limits conceptually?
- Can I explain node-exporter/metrics-system awareness?
- Can I diagnose a server without blindly restarting it?
- Can I identify the responsible process?
- Can I choose the next command based on a question?
- Can I write a production runbook?

If any answer is "no," return to the corresponding section and repeat the lab.

---

# 68. Production Decision Framework

When someone says:

> **"The server is slow."**

Do not immediately restart it.

Think:

```text
1. What exactly is slow?
        ↓
2. When did it start?
        ↓
3. Is CPU saturated?
        ↓
4. Is memory under pressure?
        ↓
5. Is storage saturated?
        ↓
6. Are connections abnormal?
        ↓
7. Which process is responsible?
        ↓
8. What changed?
        ↓
9. What is the safest remediation?
        ↓
10. Did the fix actually work?
```

If the answer remains unknown:

```text
Unknown
```

is a valid classification.

Do not manufacture certainty from weak evidence.

---

# 69. Three-Minute Operator Reference

```text
SERVER SLOW?
    |
    +--> uptime
    |
    +--> nproc
    |
    +--> free -h
    |
    +--> vmstat 1
    |
    +--> top
    |
    +--> CPU?
    |      └── pidstat -u 1
    |
    +--> I/O?
    |      ├── iostat -xz 1
    |      └── pidstat -d 1
    |
    +--> MEMORY?
    |      ├── free -h
    |      ├── vmstat 1
    |      └── PSI
    |
    +--> PROCESS DISAPPEARED?
    |      ├── dmesg
    |      └── journalctl -k
    |
    +--> CONNECTIONS?
    |      └── ss -tan
    |
    +--> INCIDENT OVER?
           └── sar
```

Mental model:

```text
Symptom
→ Resource
→ Process
→ Cause
→ Fix
→ Verify
```

---

# 70. Data Engineering Mental Models

## Model 1 — CPU

```text
nproc
= how much CPU capacity exists?

uptime
= how much load is building?

top
= who is consuming it?

pidstat
= which process is contributing?
```

## Model 2 — Memory

```text
free
= unused now

available
= estimated memory that can be made available

cache
= useful reclaimable memory

vmstat
= is memory pressure occurring?

PSI
= how much work is being delayed?

OOM logs
= did the kernel terminate something?
```

## Model 3 — Storage

```text
vmstat
= is the system waiting?

iostat
= what is the device doing?

pidstat
= who is generating I/O?

application context
= why is that process doing I/O?
```

## Model 4 — Historical

```text
top
= now

vmstat
= now over a sampling window

iostat
= now over a sampling window

sar
= what happened earlier?
```

## Model 5 — Production diagnosis

```text
SYMPTOM
   ↓
RESOURCE
   ↓
PROCESS
   ↓
CAUSE
   ↓
FIX
   ↓
VERIFY
```

---

# 71. Scope Boundaries

This module intentionally does **not** become a full course on:

- Prometheus
- Grafana
- Kubernetes
- Docker administration
- Spark internals
- PostgreSQL administration
- filesystem administration
- advanced networking

Those technologies appear only where necessary to explain resource diagnosis.

## 71.1 What this topic assumes

You should already be comfortable with basic Linux concepts from earlier stages/topics, including:

- shell navigation
- files and directories
- processes at a basic level
- permissions
- environment variables
- basic SSH
- basic Docker usage from G1 where relevant

## 71.2 What this topic adds

This topic adds:

```text
server resource observation
+
performance interpretation
+
resource saturation diagnosis
+
per-process correlation
+
kernel/OOM investigation
+
connection inspection
+
pressure metrics
+
historical performance investigation
+
cgroup/resource-limit awareness
```

---

# 72. Operational Safety Rules

## Rule 1 — Use disposable environments for stress

Any experiment that may exhaust:

- CPU
- memory
- disk
- connections

must be isolated.

> **Run only on a disposable practice environment. Never run stress/OOM experiments on production.**

## Rule 2 — Preserve evidence

Before restarting or killing a process when operationally safe:

```text
capture
→ understand
→ act
```

## Rule 3 — Do not expose credentials

Examples should use placeholders such as:

```text
DB_HOST
DB_USER
DB_NAME
```

Never place real credentials in scripts or command history.

## Rule 4 — Avoid false precision

Performance behavior depends on:

- Linux distribution
- kernel version
- virtualization
- hardware
- container limits
- storage implementation
- workload

Treat thresholds as context-dependent unless a specific platform defines an operational SLO.

---

# 73. Final Mental Model

```text
UPTIME
= What is the system load?

NPROC
= How much CPU capacity exists?

TOP
= Which processes are consuming resources?

FREE
= How much memory is actually available?

VMSTAT
= What is the system waiting on?

IOSTAT
= Is storage the bottleneck?

PIDSTAT
= Which process is causing the load?

SS
= What network connections exist?

DMESG / JOURNALCTL -K
= Did the kernel report a failure?

PSI
= How much are workloads being delayed by resource pressure?

SAR
= What happened in the past?

CGROUPS
= What resource boundaries are being enforced?

DIAGNOSIS
= Symptom → Resource → Process → Cause → Fix → Verify
```

The learner should finish this module able to hear:

```text
"The server is slow."
```

and calmly investigate it instead of immediately restarting the machine.

---

# 74. Roadmap Coverage Audit

| Roadmap requirement | Covered? | Where taught |
|---|---|---|
| Load average | ✅ Covered | §7 Load Average |
| `uptime` | ✅ Covered | §7 and command reference |
| `nproc` | ✅ Covered | §4 and §6 |
| CPU interpretation | ✅ Covered | §4–§6 |
| Interactive monitoring | ✅ Covered | §9 |
| Memory used/available | ✅ Covered | §10–§12 |
| Buffers/cache | ✅ Covered | §13 |
| `free -h` | ✅ Covered | §11 |
| `vmstat` | ✅ Covered | §16 |
| Run queue | ✅ Covered | §17 |
| Swap | ✅ Covered | §15 |
| I/O wait | ✅ Covered | §20 |
| `iostat` | ✅ Covered | §22 |
| Disk utilisation | ✅ Covered | §23 |
| Disk latency | ✅ Covered | §21–§24 |
| `pidstat` | ✅ Covered | §26–§27 |
| Per-process diagnosis | ✅ Covered | §27 |
| OOM killer | ✅ Covered | §28–§31 |
| `dmesg` | ✅ Covered | §29 |
| `journalctl -k` | ✅ Covered | §30 |
| `ss` | ✅ Covered | §32–§33 |
| Connection leaks | ✅ Covered | §33 |
| PSI | ✅ Covered | §34–§38 |
| `/proc/pressure/*` | ✅ Covered | §34–§38 |
| `sar` | ✅ Covered | §39–§42 |
| `sysstat` | ✅ Covered | §40 |
| Historical diagnosis | ✅ Covered | §42 and §56 |
| cgroups | ✅ Covered | §43–§45 |
| Container/systemd resource limits | ✅ Covered | §44–§45 |
| Node exporter/metrics awareness | ✅ Covered | §46 |
| Diagnosis methodology | ✅ Covered | §47 |
| CPU saturation lab | ✅ Covered | §51 |
| Memory exhaustion lab | ✅ Covered | §53 |
| Disk I/O lab | ✅ Covered | §52 |
| Connection leak lab | ✅ Covered | §54 |
| Historical investigation lab | ✅ Covered | §55 |
| First-five-commands runbook | ✅ Covered | §56 and §59 |
| Checkpoint | ✅ Covered | §67 |
| Common mistakes | ✅ Covered | §62 |

---

# 75. Module Completion Criteria

Topic 06 is complete when the learner can independently perform this workflow on a practice Linux server:

```text
1. Receive a vague performance symptom.
2. Convert it into a precise question.
3. Establish a baseline.
4. Measure CPU capacity and load.
5. Inspect memory availability and pressure.
6. Inspect I/O behavior.
7. Identify abnormal connections when relevant.
8. Identify the responsible process.
9. Check kernel evidence for OOM/resource failures.
10. Use PSI when contention is ambiguous.
11. Use sar for historical incidents.
12. Consider cgroup/resource limits.
13. Form a root-cause hypothesis.
14. Apply a safe remediation.
15. Verify the result.
16. Write a concise runbook entry.
17. Explain the diagnosis aloud.
```

The expected professional behavior is:

```text
Do not guess.
Do not panic.
Do not blindly restart.
Do not rely on one metric.

Measure.
Correlate.
Diagnose.
Fix safely.
Verify.
Document.
```

---

# 76. Final Quality and Safety Audit

## Scope

- Topic 06 remains focused on Linux server resource monitoring.
- Prometheus/Grafana, Docker, Kubernetes, Spark internals, PostgreSQL administration, filesystem administration, and networking are not taught as separate courses.

## Progression

The module progresses:

```text
Basic
→ Intermediate
→ Advanced
→ Production
```

## Diagnostic methodology

The module repeatedly teaches:

```text
question
→ metric
→ command
→ output
→ interpretation
→ hypothesis
→ next command
→ confirmation
→ remediation
```

## Data Engineering relevance

Examples connect resource behavior to:

- Python
- pandas
- PostgreSQL
- APIs
- Spark
- batch pipelines
- ingestion
- large files
- spill
- concurrent workloads
- database connections

## Safety

Stress experiments explicitly require:

```text
Run only on a disposable practice environment.
Never run stress/OOM experiments on production.
```

## Platform variation

The module warns that command output, fields, options, kernel behavior, cgroup implementation, and logging availability can vary across Linux distributions, kernel versions, containers, virtualization environments, and `sysstat` versions.

## Evidence-first operations

The module reinforces:

```text
measure before restart
diagnose from evidence
identify the responsible process
verify the fix
document the incident
```

---

# 77. Topic 06 Completion Statement

After completing this module, the learner should be able to operate a Linux Data Engineering server with a production-oriented performance mindset:

```text
"The server is slow."
        ↓
"What exactly is slow?"
        ↓
"What resource is under pressure?"
        ↓
"Which process is responsible?"
        ↓
"Why is it happening?"
        ↓
"What changed?"
        ↓
"What is the safest fix?"
        ↓
"Did the fix work?"
        ↓
"What should the runbook say?"
```

That is the core skill of **server resource monitoring and evidence-based performance diagnosis**.
