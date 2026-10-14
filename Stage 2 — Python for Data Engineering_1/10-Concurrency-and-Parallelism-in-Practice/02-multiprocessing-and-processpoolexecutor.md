# 02. Multiprocessing and `ProcessPoolExecutor`

> **Stage 2 --- Python for Data Engineering**\
> **Module 2.10 --- Concurrency and Parallelism in Practice**\
> **Topic 02 --- Multiprocessing and ProcessPoolExecutor**

## Learning Objectives

By the end of this chapter you should be able to:

-   Explain why processes exist.
-   Identify CPU-bound versus I/O-bound workloads.
-   Explain the role of the GIL in standard GIL-enabled CPython.
-   Use `multiprocessing` and `ProcessPoolExecutor`.
-   Understand `Future`, `submit()`, and `map()`.
-   Use the `__main__` guard correctly.
-   Explain pickling and process boundaries.
-   Design process-friendly functions and task payloads.
-   Explain `fork`, `spawn`, and `forkserver`.
-   Tune `chunksize`.
-   Use `initializer=` and `initargs`.
-   Explain `max_tasks_per_child`.
-   Size workers against real CPU availability.
-   Account for container CPU limits and headroom.
-   Use partition-based processing.
-   Explain shared memory, memory mapping, and Arrow IPC.
-   Detect process × thread oversubscription.
-   Design fork-safe database and resource handling.
-   Handle worker exceptions, `BrokenProcessPool`, stuck work,
    interrupts, and shutdown.
-   Benchmark and prove whether multiprocessing actually helps.
-   Design a production-grade process-based Data Engineering pipeline.

------------------------------------------------------------------------

## 1. Why Processes Exist

Consider:

``` python
def expensive_work(value):
    return expensive_python_calculation(value)
```

For 10,000 records:

``` text
10,000 records
      |
      v
expensive Python calculation
      |
      v
CPU time
```

When the dominant cost is Python computation rather than waiting for a
network or disk, the workload is CPU-bound.

In a standard GIL-enabled CPython build, a process gives the workload
another interpreter and another GIL:

``` text
Process 1 -> CPU core
Process 2 -> CPU core
Process 3 -> CPU core
Process 4 -> CPU core
```

This enables true parallel execution of Python code across CPU cores.

The cost is substantial:

-   process startup;
-   separate interpreter memory;
-   serialization;
-   inter-process communication;
-   scheduling;
-   failure handling;
-   lifecycle management.

> **Processes are useful because they provide parallel CPU execution,
> but they are not free.**

------------------------------------------------------------------------

## 2. CPU-Bound vs I/O-Bound

  Workload                 Typical bottleneck   Processes useful?
  ------------------------ -------------------- -----------------------------------
  API requests             Network              Usually not first choice
  File download            Network/disk         Usually not first choice
  Pure-Python parsing      CPU                  Yes
  Pure-Python validation   CPU                  Yes
  Compression              Depends              Benchmark
  NumPy computation        Native CPU           Often let NumPy parallelize
  Polars computation       Native CPU           Usually let Polars manage threads
  DuckDB query             Native engine        Usually let DuckDB manage threads

These are heuristics, not laws.

Always start with:

``` text
classify -> measure -> identify bottleneck -> choose model
```

A process pool should solve a demonstrated bottleneck, not a theoretical
one.

------------------------------------------------------------------------

## 3. Process vs Thread

``` text
Threads:
multiple threads
      |
same process memory
      |
same interpreter
      |
same GIL in standard CPython

Processes:
multiple processes
      |
separate interpreters
      |
separate memory
      |
each process has its own GIL
```

  Characteristic    Thread           Process
  ----------------- ---------------- -------------------
  Memory            Shared           Separate
  Interpreter       Same             Separate
  GIL               Shared           One per process
  Communication     Low overhead     Serialization/IPC
  Startup           Lower            Higher
  Memory            Lower            Higher
  Pure-Python CPU   Limited by GIL   Strong candidate
  I/O               Excellent        Often unnecessary
  Isolation         Lower            Higher

Threads remain useful for I/O and for native libraries that release the
GIL.

------------------------------------------------------------------------

## 4. What Is a Process?

A process is an operating-system execution context with its own:

-   address space;
-   Python interpreter;
-   Python objects;
-   threads;
-   operating-system resources;
-   scheduling state.

The separation is valuable:

``` text
Parent
  |
  +---- Worker A
  |       |
  |       +-- interpreter
  |       +-- memory
  |
  +---- Worker B
          |
          +-- interpreter
          +-- memory
```

But separate memory means a normal Python object cannot simply be
treated as shared state.

------------------------------------------------------------------------

## 5. `multiprocessing`

Python's lower-level `multiprocessing` module gives direct process
control:

``` python
import multiprocessing as mp


def worker(value):
    return value * value


if __name__ == "__main__":
    process = mp.Process(target=worker, args=(10,))
    process.start()
    process.join()
```

Use lower-level primitives when you need direct lifecycle or IPC
control.

For many Data Engineering workloads, a pool abstraction is easier:

``` text
many tasks
   |
bounded workers
   |
results
```

That is the role of `ProcessPoolExecutor`.

------------------------------------------------------------------------

## 6. `ProcessPoolExecutor`

``` python
from concurrent.futures import ProcessPoolExecutor


def square(value):
    return value * value


def main():
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(square, range(10)))

    print(results)


if __name__ == "__main__":
    main()
```

Important concepts:

-   **executor** --- manages the pool;
-   **worker** --- executes a function;
-   **task** --- one unit of work;
-   **Future** --- represents asynchronous work;
-   **result** --- returned value or exception;
-   **shutdown** --- worker cleanup.

The context manager is normally the safest starting pattern.

------------------------------------------------------------------------

## 7. Futures and `submit()`

``` text
submit()
   |
   v
Future
   |
   v
worker executes
   |
   +--> result
   |
   +--> exception
```

Example:

``` python
from concurrent.futures import ProcessPoolExecutor


def square(value):
    return value * value


if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=2) as executor:
        future = executor.submit(square, 10)

        try:
            result = future.result()
            print(result)
        except Exception as exc:
            print(f"worker failed: {exc!r}")
```

A worker exception is surfaced when the result is retrieved.

Never silently discard futures in a production pipeline.

------------------------------------------------------------------------

## 8. `map()`

For homogeneous work:

``` python
with ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(square, range(100)))
```

`map()` is convenient, but its simplicity can hide task-management
costs.

For heterogeneous jobs or when you need task metadata, use `submit()`
and retain the corresponding futures.

------------------------------------------------------------------------

## 9. The `__main__` Guard

Always protect process-pool orchestration:

``` python
def main():
    ...


if __name__ == "__main__":
    main()
```

This matters because `spawn` starts a fresh interpreter that imports the
module. Without the guard, module-level process creation can execute
again in the child and lead to recursive creation.

The guard also:

-   improves testability;
-   separates import from execution;
-   makes cross-platform behavior safer.

Unsafe:

``` python
executor = ProcessPoolExecutor()
results = list(executor.map(worker, items))
```

Safe:

``` python
def main():
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(worker, items))


if __name__ == "__main__":
    main()
```

------------------------------------------------------------------------

## 10. Pickling and the Process Boundary

A simplified model is:

``` text
Parent
  |
  | pickle
  v
Worker
  |
  | unpickle
  v
function
```

Return values travel back through a similar boundary.

Therefore:

``` python
executor.submit(process_dataframe, huge_dataframe)
```

may be expensive even if `process_dataframe()` itself is fast.

Costs include:

-   serialization CPU;
-   deserialization CPU;
-   memory allocations;
-   communication;
-   copies;
-   latency.

> **A process pool creates a data-movement boundary as well as a
> CPU-execution boundary.**

------------------------------------------------------------------------

## 11. What Should Cross the Boundary?

Generally process-friendly:

``` text
int
float
str
bytes
list
dict
tuple
small configuration
paths
partition IDs
keys
```

Prefer module-level worker functions:

``` python
def process_partition(path: str) -> dict:
    ...
```

Commonly problematic:

-   lambdas;
-   nested/local functions;
-   closures;
-   live database connections;
-   open file handles;
-   locks;
-   active clients;
-   arbitrary third-party objects.

Do not use the simplistic rule that only primitive values work. Actual
picklability depends on the object and serialization mechanism.

------------------------------------------------------------------------

## 12. Process-Friendly Function Design

Prefer:

``` text
Parent
  |
  | "/data/part-017.parquet"
  v
Worker
  |
  +--> read
  +--> validate
  +--> transform
  +--> write output
  +--> return statistics
```

Avoid:

``` text
Parent
  |
  +--> load 2 GB DataFrame
  |
  +--> serialize 2 GB
  |
  +--> transfer 2 GB
  |
Worker
  |
  +--> deserialize
```

The parent should usually send **references to data**, not giant data
objects.

------------------------------------------------------------------------

## 13. Large DataFrames

A DataFrame can contain:

-   large native buffers;
-   strings;
-   Python objects;
-   metadata;
-   extension arrays;
-   indexes.

Passing it between processes may create large serialization and memory
costs.

A better Data Engineering design is often:

``` python
def process_partition(path: str):
    data = read_partition(path)
    result = transform(data)
    write_output(result, path)
    return {"path": path, "records": len(data)}
```

The exact data library is workload-specific.

The architectural principle is not.

------------------------------------------------------------------------

# 14. Start Methods

Python supports three important multiprocessing start methods:

``` text
fork
spawn
forkserver
```

They differ in:

-   startup;
-   inherited state;
-   isolation;
-   resource safety;
-   thread interaction.

Platform defaults differ, and Python versions evolve. In particular,
Linux process-start defaults changed in Python 3.14, so production
systems should not casually assume a historical default.

------------------------------------------------------------------------

## 15. `fork`

Conceptually:

``` text
Parent
  |
 fork
  |
  v
Child inherits process state
```

Copy-on-write can make initial memory handling efficient.

But the child can inherit state involving:

-   file descriptors;
-   locks;
-   database connections;
-   sockets;
-   thread-related state;
-   native-library runtime state.

Therefore:

> **`fork` is not automatically safe.**

------------------------------------------------------------------------

## 16. `spawn`

Conceptually:

``` text
Parent
  |
  v
fresh interpreter
  |
  v
imports module
  |
  v
worker starts
```

Advantages:

-   clean interpreter state;
-   fewer inherited resources.

Costs:

-   startup;
-   imports;
-   pickling;
-   strict main-guard requirements.

`spawn` can be useful when inherited state is a concern.

------------------------------------------------------------------------

## 17. `forkserver`

Conceptually:

``` text
Parent
  |
  v
fork server
  |
  +--> worker
  +--> worker
```

A server process creates workers.

This can provide a controlled process-creation model that avoids
directly forking a complex parent state.

Availability and trade-offs depend on platform and Python environment.

------------------------------------------------------------------------

## 18. Choosing a Start Method

  Method         Startup            Inherited state   Primary concern
  -------------- ------------------ ----------------- -------------------------
  `fork`         Generally low      Significant       Fork safety
  `spawn`        Generally higher   Minimal           Startup/import/pickling
  `forkserver`   Intermediate       Controlled        Availability/lifecycle

Do not rank them universally.

Choose based on:

-   platform;
-   Python version;
-   libraries;
-   threads;
-   external resources;
-   reproducibility requirements.

------------------------------------------------------------------------

## 19. Explicit Start Methods

Use:

``` python
import multiprocessing as mp

ctx = mp.get_context("spawn")
```

Then:

``` python
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp


def worker(value):
    return value * value


def main():
    ctx = mp.get_context("spawn")

    with ProcessPoolExecutor(
        max_workers=4,
        mp_context=ctx,
    ) as executor:
        print(list(executor.map(worker, range(10))))


if __name__ == "__main__":
    main()
```

Explicit selection makes behavior deliberate.

------------------------------------------------------------------------

# 20. `chunksize`

For many tiny tasks:

``` python
executor.map(
    function,
    items,
    chunksize=100,
)
```

can reduce coordination overhead.

Conceptually:

``` text
100,000 tiny tasks
       |
       v
many scheduling operations
```

versus:

``` text
100,000 tiny tasks
       |
       v
larger batches
       |
       v
less coordination
```

But large chunks can reduce load balancing.

------------------------------------------------------------------------

## 21. Chunksize Experiment

Test:

``` text
1
10
100
1000
10000
```

Example:

``` python
from concurrent.futures import ProcessPoolExecutor
from time import perf_counter


def tiny_cpu_task(value):
    total = 0
    for i in range(100):
        total += (value + i) % 17
    return total


def benchmark(chunksize):
    start = perf_counter()

    with ProcessPoolExecutor(max_workers=4) as executor:
        results = list(
            executor.map(
                tiny_cpu_task,
                range(100_000),
                chunksize=chunksize,
            )
        )

    return perf_counter() - start, sum(results)


if __name__ == "__main__":
    for size in (1, 10, 100, 1000, 10000):
        elapsed, checksum = benchmark(size)
        print(size, elapsed, checksum)
```

Measure:

-   runtime;
-   CPU;
-   memory;
-   throughput.

There is no universal best `chunksize`.

------------------------------------------------------------------------

# 22. Worker Initialization

Use:

``` python
ProcessPoolExecutor(
    max_workers=4,
    initializer=initialize_worker,
    initargs=(config,),
)
```

Good uses:

-   worker-local configuration;
-   lookup tables;
-   parser initialization;
-   process-local clients;
-   native runtime configuration.

Example:

``` python
LOOKUP = {}


def initialize_worker(lookup):
    global LOOKUP
    LOOKUP = lookup


def enrich(value):
    return LOOKUP.get(value, "UNKNOWN")
```

Initialization occurs once per worker rather than once per task.

Do not use it to hide an enormous data-transfer problem.

------------------------------------------------------------------------

# 23. `max_tasks_per_child`

Example:

``` python
ProcessPoolExecutor(
    max_workers=4,
    max_tasks_per_child=1000,
)
```

Conceptually:

``` text
worker
  |
  +--> task
  +--> task
  +--> ...
  +--> task 1000
  |
  v
replacement worker
```

Useful when long-lived workers exhibit gradual memory growth.

Trade-offs:

-   more startup;
-   repeated initialization;
-   lower worker reuse.

It is not a substitute for fixing a real memory leak.

------------------------------------------------------------------------

# 24. CPU Sizing

Inspect available CPU capacity:

``` python
import os

print(os.process_cpu_count())
```

Do not automatically use:

``` text
workers = CPU count
```

Production sizing must consider:

-   physical cores;
-   logical CPUs;
-   container quotas;
-   native-library threads;
-   memory;
-   operating-system overhead;
-   other services.

------------------------------------------------------------------------

## 25. Container CPU Limits

A container may run on a host with 64 CPUs but be entitled to only a
fraction of that capacity.

Therefore:

``` text
host CPU count
      !=
application CPU entitlement
```

Worker sizing should respect the environment in which the process
actually executes.

Leave headroom for:

-   parent orchestration;
-   monitoring;
-   logging;
-   storage;
-   other workloads.

------------------------------------------------------------------------

# 26. Partition-Based Data Engineering

A common input:

``` text
data/
├── part-000.parquet
├── part-001.parquet
├── part-002.parquet
└── ...
```

Architecture:

``` text
Parent
  |
  +--> Worker 1 -> part-000
  +--> Worker 2 -> part-001
  +--> Worker 3 -> part-002
  +--> Worker 4 -> part-003
```

Worker lifecycle:

``` text
read partition
     |
validate / transform
     |
write worker-owned output
     |
return compact statistics
```

This is often more efficient than transferring huge in-memory objects.

------------------------------------------------------------------------

# 27. Shared Memory

Python provides:

``` python
multiprocessing.shared_memory
```

Conceptually:

``` text
Process A ----+
              |
              v
        shared memory
              ^
              |
Process B ----+
```

Potential benefits:

-   avoid repeated copies;
-   efficient access to large numeric buffers.

Costs:

-   lifecycle;
-   ownership;
-   synchronization;
-   cleanup;
-   complexity.

Shared memory is an advanced option, not the default.

------------------------------------------------------------------------

# 28. Memory-Mapped Files

A memory-mapped file provides a file-backed representation:

``` text
Disk
 |
 v
memory mapping
 |
 +--> Process A
 +--> Process B
```

Useful for:

-   large data;
-   random access;
-   file-backed sharing;
-   reducing giant Python-object copies.

Performance still depends on:

-   storage;
-   filesystem;
-   access pattern;
-   page cache;
-   memory pressure.

------------------------------------------------------------------------

# 29. Arrow IPC

Arrow IPC is a columnar representation useful for process-friendly
analytical data exchange.

Relevant properties:

-   columnar representation;
-   efficient native memory layout;
-   compact serialization;
-   interoperability.

Use it when a structured, process-friendly representation is useful.

Do not assume Arrow IPC is automatically better than simple partitioned
files.

------------------------------------------------------------------------

# 30. Share Data or Re-read It?

### Send object

``` text
Parent -> serialize -> worker -> deserialize
```

### Send path

``` text
Parent -> path -> worker -> read
```

### Shared representation

``` text
Parent/producer
      |
      v
shared representation
      |
      +--> worker
      +--> worker
```

Compare:

  Approach         Main advantage                  Main cost
  ---------------- ------------------------------- ----------------------------
  Send object      Immediate data availability     Serialization/memory
  Send path        Simple and low coordination     Worker reads data
  Shared memory    Avoid large transfers           Complexity/lifecycle
  Memory mapping   File-backed access              Layout/storage constraints
  Arrow IPC        Efficient structured exchange   Extra representation

Default toward compact references when workers can independently load
the data.

------------------------------------------------------------------------

# 31. Oversubscription

Suppose:

``` text
8 processes
x
8 native threads each
=
64 runnable threads
```

on an 8-core machine.

This may be slower than a smaller configuration.

The key question is:

> **How many layers of parallelism are active?**

------------------------------------------------------------------------

# 32. NumPy / BLAS

NumPy may call native libraries that create worker threads.

Conceptually:

``` text
ProcessPoolExecutor
        x
BLAS/native threads
        =
oversubscription
```

Variables such as:

``` text
OMP_NUM_THREADS
```

may control some runtimes.

The exact control depends on the underlying BLAS/runtime.

Always measure.

------------------------------------------------------------------------

# 33. Polars

Polars may already use multiple threads.

Experiment:

``` text
8 processes
+
default Polars threading
```

versus:

``` text
8 processes
+
POLARS_MAX_THREADS=1
```

Measure:

-   runtime;
-   CPU utilization;
-   memory.

The result is workload- and machine-dependent.

------------------------------------------------------------------------

# 34. DuckDB and PyArrow

DuckDB and PyArrow may also parallelize internally.

Before adding a process pool, ask:

> **Is the library already parallelizing the workload?**

Sometimes:

``` text
one process
+
native parallel engine
```

is simpler and faster than:

``` text
many processes
+
many native threads
```

Benchmark the actual pipeline.

------------------------------------------------------------------------

# 35. Fork Safety

Avoid inheriting process-sensitive resources through `fork`.

Examples:

-   database connections;
-   network sockets;
-   locks;
-   thread pools;
-   file handles;
-   native runtime state.

Production principle:

> **Create process-local resources inside the worker.**

------------------------------------------------------------------------

# 36. Database Connections

Avoid:

``` text
Parent opens DB connection
        |
        v
fork
        |
        v
workers inherit connection
```

Prefer:

``` text
Worker starts
    |
    v
worker opens connection
    |
    v
worker performs work
    |
    v
worker closes connection
```

Example:

``` python
def process_partition(path):
    connection = open_database_connection()

    try:
        return process_with_connection(connection, path)
    finally:
        connection.close()
```

The connection belongs to the process that created it.

------------------------------------------------------------------------

# 37. Threads Across `fork`

Forking while active threads exist can be dangerous because the child
can inherit lock state without inheriting the full parent thread set.

Possible results:

-   deadlocks;
-   inconsistent runtime state;
-   library-specific failures.

When complex threading already exists, evaluate a fresh-process model
such as `spawn`.

------------------------------------------------------------------------

# 38. Worker Exceptions

``` python
future = executor.submit(process_partition, path)

try:
    result = future.result()
except Exception as exc:
    log_failure(path, exc)
    raise
```

A production system should associate errors with:

-   partition;
-   input;
-   task ID;
-   relevant record range;
-   worker context.

A bare traceback is often insufficient operational context.

------------------------------------------------------------------------

# 39. `BrokenProcessPool`

A broken pool means the executor cannot continue normal operation.

Possible causes:

-   unexpected worker termination;
-   worker crash;
-   abrupt process termination;
-   resource/infrastructure failure.

Production response:

``` text
detect
  |
log context
  |
identify valid outputs
  |
decide restart/retry
```

Do not assume automatic recovery is safe.

Retry requires appropriate:

-   idempotency;
-   output semantics;
-   partition ownership;
-   side-effect control.

------------------------------------------------------------------------

# 40. Stuck Workers and Timeouts

``` python
future.result(timeout=10)
```

means:

> Stop waiting after 10 seconds.

It does **not** necessarily mean:

> Kill the worker.

Therefore:

``` text
Future timeout != worker termination
```

Design long-running work with:

-   bounded tasks;
-   observable progress;
-   idempotent outputs;
-   explicit process lifecycle;
-   external supervision where required.

------------------------------------------------------------------------

# 41. Ctrl+C

`Ctrl+C` may raise `KeyboardInterrupt` in the parent.

You must decide:

-   whether pending work is cancelled;
-   what happens to running workers;
-   which outputs are valid;
-   whether the job can resume;
-   how cleanup occurs.

Example:

``` python
def main(paths):
    executor = ProcessPoolExecutor(max_workers=4)

    try:
        futures = [
            executor.submit(process_partition, path)
            for path in paths
        ]

        for future in futures:
            future.result()

    except KeyboardInterrupt:
        print("Interrupted")
        raise

    finally:
        executor.shutdown(
            wait=True,
            cancel_futures=True,
        )


if __name__ == "__main__":
    main(paths)
```

Cancellation does not necessarily stop already-running CPU work.

------------------------------------------------------------------------

# 42. Clean Shutdown

Normal:

``` python
with ProcessPoolExecutor(max_workers=4) as executor:
    ...
```

Explicit:

``` python
executor.shutdown(
    wait=True,
    cancel_futures=True,
)
```

Important distinctions:

-   `wait=True` waits for running work;
-   `cancel_futures=True` cancels pending futures where supported;
-   running work is not automatically terminated.

Clean shutdown should prevent:

-   orphan workers;
-   ambiguous output;
-   resource leaks;
-   false success.

------------------------------------------------------------------------

# 43. Benchmarking

For a CPU-bound pure-Python workload compare:

``` text
Sequential
    vs
ThreadPoolExecutor
    vs
ProcessPoolExecutor
```

Measure:

-   wall time;
-   CPU utilization;
-   per-core utilization;
-   peak memory;
-   serialization overhead;
-   throughput;
-   task completion rate.

Use:

``` python
from time import perf_counter

start = perf_counter()
# workload
elapsed = perf_counter() - start
```

Repeat runs rather than trusting one measurement.

------------------------------------------------------------------------

# 44. Speed-up

``` text
speedup = sequential_time / parallel_time
```

Example:

``` text
Sequential = 100 seconds
Parallel   = 30 seconds

Speed-up = 3.33x
```

Four cores do not imply 4x speed-up.

Reasons include:

-   startup;
-   serialization;
-   scheduling;
-   sequential portions;
-   memory bandwidth;
-   uneven work;
-   I/O;
-   contention.

------------------------------------------------------------------------

# 45. Data Engineering Use Cases

## JSONL validation

``` text
many JSONL files
      |
      v
CPU-heavy Python validation
      |
      v
ProcessPoolExecutor
```

Use one file or partition as a unit of work.

## File parsing

``` text
200 files
   |
workers
   |
parse + validate
   |
Parquet outputs
```

## CPU-heavy enrichment

``` text
partition
   |
expensive pure-Python function
   |
enriched output
```

## Partition processing

``` text
100 partitions
   |
workers
   |
one output per partition
```

Processes are appropriate when the dominant computation is genuinely
CPU-bound, sufficiently independent, and not already efficiently
parallelized by a native engine.

------------------------------------------------------------------------

# 46. Production Architecture

``` text
                    Parent Process
                         |
                         v
                  Partition List
                         |
            +------------+------------+
            |            |            |
            v            v            v
        Worker 1     Worker 2      Worker N
            |            |            |
            v            v            v
        Partition A  Partition B  Partition N
            |            |            |
            v            v            v
          Output A    Output B     Output N
            \            |            /
             \           |           /
              +----------+----------+
                         |
                         v
                  Final Validation
```

The parent owns orchestration.

Workers own their partitions and outputs.

This reduces shared state and simplifies retry.

------------------------------------------------------------------------

# 47. Output Correctness

Always compare:

``` text
Sequential result
       ==
ProcessPool result
```

If ordering is not guaranteed:

``` python
sorted(...)
```

or deterministic key-based normalization can be used.

Check:

-   missing records;
-   duplicates;
-   corrupted output;
-   aggregates;
-   schemas;
-   nondeterministic ordering;
-   partial files.

> **A faster result that is wrong is a production bug.**

------------------------------------------------------------------------

# 48. Atomic Output Publication

Use a conceptual pattern:

``` text
worker_output.tmp
      |
successful completion
      |
atomic rename
      |
worker_output.parquet
```

A final output name should mean the output was successfully produced and
published.

The exact atomicity guarantee depends on the target filesystem.

------------------------------------------------------------------------

# 49. Worker-Owned Outputs

Prefer:

``` text
Worker 1 -> partition-001.parquet
Worker 2 -> partition-002.parquet
Worker 3 -> partition-003.parquet
```

Avoid:

``` text
Worker 1 --+
Worker 2 --+--> same output file
Worker 3 --+
```

unless synchronization is explicitly designed.

Worker-owned outputs make retry and correctness easier.

------------------------------------------------------------------------

# 50. Hands-On Lab

## `parallel_parse.py`

The following is the complete exercise specification. The external file
is intentionally not created as part of this Markdown deliverable.

Requirements:

1.  Implement `parse_file(path) -> stats`.
2.  Use a primarily pure-Python CPU-heavy workload.
3.  Process approximately 200 files.
4.  Use `ProcessPoolExecutor`.
5.  Write one Parquet output per worker-owned partition.
6.  Compare sequential, threaded, and process execution.
7.  Compare available `fork`, `spawn`, and `forkserver` contexts.
8.  Tune `chunksize` for 100,000 tiny tasks.
9.  Use `initializer=` to load a lookup table once per worker.
10. Run a Polars-heavy workload in 8 processes.
11. Compare default Polars threading with `POLARS_MAX_THREADS=1`.
12. Deliberately terminate one worker.
13. Handle `BrokenProcessPool`.
14. Compare all parallel outputs with the sequential baseline.

### CPU-heavy function

``` python
def cpu_heavy_transform(value: int) -> int:
    total = 0

    for i in range(10_000):
        total += (value * i) % 97

    return total
```

### Worker contract

``` python
def parse_file(path: str) -> dict:
    # read
    # validate
    # transform
    # write worker-owned output
    # return compact statistics
    ...
```

### Sequential baseline

``` python
def run_sequential(paths):
    return [parse_file(path) for path in paths]
```

### Process execution

``` python
with ProcessPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(parse_file, paths))
```

### Start-method experiment

``` python
import multiprocessing as mp

ctx = mp.get_context("spawn")

with ProcessPoolExecutor(
    max_workers=8,
    mp_context=ctx,
) as executor:
    results = list(executor.map(parse_file, paths))
```

### Worker initialization

``` python
LOOKUP = {}


def initialize_worker(lookup):
    global LOOKUP
    LOOKUP = lookup


def enrich(value):
    return LOOKUP.get(value, "UNKNOWN")
```

### Crash injection

``` python
import os


def crash_worker(value):
    if value == 5:
        os._exit(1)

    return value * 2
```

Use abrupt termination only for controlled failure testing.

------------------------------------------------------------------------

# 51. Failure-Injection Lab

  -----------------------------------------------------------------------
  Failure                 What happened?          Production lesson
  ----------------------- ----------------------- -----------------------
  Lambda worker           Serialization failure   Use module-level
                                                  functions

  Large DataFrame         High                    Pass compact references
                          serialization/memory    
                          cost                    

  Missing main guard      Recursive/import-time   Protect orchestration
                          pool creation           

  Forked DB connection    Unsafe inherited state  Create connections in
                                                  workers

  Oversubscription        More parallelism made   Control all threading
                          work slower             layers

  Worker exception        Future contains         Always retrieve/check
                          exception               results

  Worker crash            Pool may become broken  Handle pool-level
                                                  failure

  Stuck worker            Future never completes  Timeout is not
                                                  termination

  Ctrl+C                  Parent interrupted      Design shutdown and
                                                  recovery
  -----------------------------------------------------------------------

For every failure ask:

``` text
What happened?
Why?
How do we detect it?
How do we fix it?
What is the production lesson?
```

------------------------------------------------------------------------

# 52. Memory Experiment

Compare:

``` text
1,000,000 submitted tasks
```

against:

``` text
bounded/chunked task management
```

Measure:

-   number of futures;
-   memory;
-   execution time.

Important lesson:

> **Task management itself consumes memory.**

A process pool can run out of memory because of orchestration even when
each worker task is small.

------------------------------------------------------------------------

# 53. Pickling Experiment

Compare:

``` text
A. small integers
B. large Python object
C. large DataFrame
D. file path
```

Measure:

``` text
serialization cost
memory cost
runtime
```

Then explain why:

``` text
path / partition ID
```

is often preferable to:

``` text
huge Python object
```

when workers can independently read the data.

------------------------------------------------------------------------

# 54. Process-Sizing Experiment

Benchmark:

``` text
1 worker
2 workers
4 workers
8 workers
16 workers
```

Measure:

-   wall time;
-   CPU utilization;
-   memory;
-   throughput.

The curve usually flattens or degrades after a workload-specific point.

------------------------------------------------------------------------

# 55. Oversubscription Experiment

Run:

``` text
8 processes
+
Polars-heavy workload
```

with:

``` text
default threading
```

and:

``` text
POLARS_MAX_THREADS=1
```

Record:

-   runtime;
-   CPU;
-   memory.

Do not generalize one benchmark result to every machine.

------------------------------------------------------------------------

# 56. Advanced Trade-offs

  --------------------------------------------------------------------------------------
  Approach          Advantage         Cost/Risk              Appropriate when
  ----------------- ----------------- ---------------------- ---------------------------
  Sequential        Simple            Slow                   Small workload

  Threads           Low overhead      GIL for pure Python    I/O

  Processes         CPU parallelism   Serialization/memory   Pure-Python CPU

  Shared memory     Avoid copies      Complexity             Large shared data

  Memory mapping    File-backed       Storage/layout         Large file data
                    access            constraints            

  Native library    Optimized         Oversubscription risk  NumPy/Polars/DuckDB/Arrow
  threading                                                  
  --------------------------------------------------------------------------------------

No approach is universally best.

------------------------------------------------------------------------

# 57. Common Mistakes

1.  Using processes for I/O-bound work without justification.
2.  Forgetting the main guard.
3.  Sending giant DataFrames.
4.  Using lambdas.
5.  Using nested functions.
6.  Ignoring pickling overhead.
7.  Assuming one start method is universally correct.
8.  Forking with database connections.
9.  Forking while threads are active.
10. Creating too many workers.
11. Ignoring container CPU limits.
12. Oversubscribing native libraries.
13. Repeating initialization per task.
14. Creating millions of futures.
15. Ignoring `chunksize`.
16. Ignoring worker failures.
17. Ignoring `BrokenProcessPool`.
18. Assuming future timeouts kill workers.
19. Writing shared files unsafely.
20. Not validating against a sequential baseline.
21. Assuming more workers always means faster.
22. Ignoring memory.
23. Ignoring startup cost.
24. Treating multiprocessing as a universal optimization.

------------------------------------------------------------------------

# 58. Debugging Checklist

``` text
1. Is the workload actually CPU-bound?
2. Is it pure Python?
3. Does the sequential baseline exist?
4. Are arguments/results expensive to pickle?
5. Is the main guard present?
6. Which start method is being used?
7. How many workers?
8. What CPU limit does the process actually have?
9. Are native libraries also using threads?
10. Is memory the bottleneck?
11. Are workers crashing?
12. Is BrokenProcessPool occurring?
13. Are tasks stuck?
14. Is Ctrl+C handled correctly?
15. Are outputs correct?
16. Is the parallel version actually faster?
```

------------------------------------------------------------------------

# 59. Senior System-Design Exercise

## Scenario

You have:

> 200 JSONL files containing 50 million records. Each record requires
> expensive pure-Python validation and enrichment. The sequential
> pipeline takes 3 hours. The machine has 16 CPU cores and 64 GB RAM.

Design:

-   process count;
-   task granularity;
-   input representation;
-   output strategy;
-   pickling strategy;
-   start method;
-   worker initialization;
-   memory strategy;
-   chunking;
-   error handling;
-   crash recovery;
-   benchmark methodology;
-   correctness verification;
-   oversubscription controls.

## Model Solution

### Process count

Start by benchmarking:

``` text
4
8
12
16
```

workers.

Select based on measured throughput, memory, and CPU utilization rather
than CPU count alone.

### Task granularity

Use file/partition tasks. Subdivide only exceptionally large files if
necessary.

### Input representation

Pass paths or partition IDs.

### Output

Each worker writes one output partition.

### Pickling

Transfer compact metadata only.

### Start method

Choose deliberately based on environment and resource safety.

### Initialization

Load small worker-local lookup structures once.

### Memory

Budget:

``` text
parent
+
workers
+
native buffers
+
temporary files
```

against 64 GB.

### Chunking

Use file-level work for the main pipeline; tune `chunksize` for
tiny-task experiments.

### Failure handling

Track partition-level success/failure and make outputs idempotent.

### Crash recovery

Retry only safely repeatable partitions.

### Correctness

Compare record counts, checksums, schemas, aggregates, missing records,
and duplicates against the sequential baseline.

### Oversubscription

Control native threads when workers invoke Polars, NumPy, BLAS, DuckDB,
or PyArrow.

------------------------------------------------------------------------

# 60. Production Checklist

## Workload

-   [ ] Confirm CPU-bound.
-   [ ] Confirm pure Python or understand native-library behavior.
-   [ ] Establish sequential baseline.

## Process design

-   [ ] Use `ProcessPoolExecutor` when justified.
-   [ ] Correct `__main__` guard.
-   [ ] Deliberate start method.
-   [ ] Appropriate worker count.
-   [ ] CPU headroom.

## Serialization

-   [ ] Arguments are process-friendly.
-   [ ] No unnecessary huge objects.
-   [ ] Minimize serialization.
-   [ ] Prefer paths/partition IDs.

## Memory

-   [ ] Understand per-process memory.
-   [ ] Avoid unnecessary copies.
-   [ ] Consider mmap/shared memory/Arrow IPC only when justified.
-   [ ] Consider worker recycling.

## Native libraries

-   [ ] Check internal threading.
-   [ ] Prevent oversubscription.
-   [ ] Configure native thread counts where appropriate.

## Reliability

-   [ ] Handle worker exceptions.
-   [ ] Handle `BrokenProcessPool`.
-   [ ] Handle stuck work.
-   [ ] Handle Ctrl+C.
-   [ ] Clean shutdown.
-   [ ] Never treat partial output as success.

## Correctness

-   [ ] Compare with sequential baseline.
-   [ ] Detect missing records.
-   [ ] Detect duplicates.
-   [ ] Verify deterministic output where required.

## Performance

-   [ ] Measure wall time.
-   [ ] Measure CPU.
-   [ ] Measure memory.
-   [ ] Measure serialization.
-   [ ] Tune worker count.
-   [ ] Tune `chunksize`.

------------------------------------------------------------------------

# 61. Final Mental Model

``` text
CPU-bound pure Python
        |
        v
Sequential baseline
        |
        v
Can processes help?
        |
        v
ProcessPoolExecutor
        |
        v
Small serializable inputs
        |
        v
Explicit process configuration
        |
        v
Appropriate worker count
        |
        v
Chunk tasks
        |
        v
Initialize workers once
        |
        v
Avoid shared state
        |
        v
Avoid oversubscription
        |
        v
Handle worker failures
        |
        v
Clean shutdown
        |
        v
Measure
        |
        v
Compare with baseline
        |
        v
Prove correctness
        |
        v
Keep only if the evidence supports it
```

> **Multiprocessing is not automatically an optimization. It is an
> engineering trade-off between CPU parallelism, serialization, memory,
> process startup, complexity, and correctness.**

------------------------------------------------------------------------

# 62. Exit Criteria

You should be able to:

-   [ ] Explain processes.
-   [ ] Explain CPU-bound pure-Python workloads.
-   [ ] Explain why standard CPython threads are limited for pure-Python
    CPU work.
-   [ ] Use `ProcessPoolExecutor`.
-   [ ] Use `submit()`.
-   [ ] Use `map()`.
-   [ ] Understand Futures.
-   [ ] Handle worker exceptions.
-   [ ] Explain the main guard.
-   [ ] Explain pickling.
-   [ ] Identify problematic arguments.
-   [ ] Explain `fork`.
-   [ ] Explain `spawn`.
-   [ ] Explain `forkserver`.
-   [ ] Select a start method deliberately.
-   [ ] Explain and tune `chunksize`.
-   [ ] Use `initializer=`.
-   [ ] Explain `max_tasks_per_child`.
-   [ ] Size workers appropriately.
-   [ ] Account for container CPU limits.
-   [ ] Explain shared memory.
-   [ ] Explain memory-mapped files.
-   [ ] Explain Arrow IPC.
-   [ ] Explain oversubscription.
-   [ ] Recognize native-library parallelism.
-   [ ] Control native thread counts when appropriate.
-   [ ] Explain fork safety.
-   [ ] Keep database connections process-local.
-   [ ] Handle `BrokenProcessPool`.
-   [ ] Understand timeout limitations.
-   [ ] Handle Ctrl+C.
-   [ ] Implement clean shutdown.
-   [ ] Benchmark sequential versus process execution.
-   [ ] Measure CPU and memory.
-   [ ] Validate parallel output against a sequential baseline.
-   [ ] Design a production-grade process-based Data Engineering
    workload.

------------------------------------------------------------------------

## Final Takeaway

Do not mechanically add a process pool to every slow loop.

Reason in this order:

``` text
What is the bottleneck?
        |
        v
Is it CPU-bound?
        |
        v
Is it primarily Python?
        |
        v
What crosses the process boundary?
        |
        v
How expensive is serialization?
        |
        v
How much memory does each worker need?
        |
        v
Does the underlying library already parallelize?
        |
        v
How many CPUs are actually available?
        |
        v
What happens when a worker fails?
        |
        v
Are outputs idempotent and correct?
        |
        v
Does measurement prove a real improvement?
```

The production-quality decision is the one supported by evidence,
correctness checks, and an explicit understanding of the trade-offs.
