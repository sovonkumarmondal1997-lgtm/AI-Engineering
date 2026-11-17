# GIL Internals and Subinterpreters

> **Target:** CPython 3.12–3.14. Examples use standard-library APIs unless explicitly marked version-sensitive. Always record `sys.version`, build type, operating system, CPU count, and whether the interpreter is free-threaded before comparing results. Exact timings and implementation details are not cross-version contracts.

## Learning outcomes

By the end of this lesson, you should be able to:

1. Explain what the Global Interpreter Lock (GIL) protects and why it does not make application-level sequences thread-safe.
2. Predict when threads help: blocking I/O and native code that releases the GIL versus CPU-bound pure Python.
3. Describe the switching interval and eval-breaker conceptually, without mistaking implementation details for language guarantees.
4. Benchmark threads, processes, subinterpreters, and free-threaded builds fairly.
5. Diagnose races, contention, convoy effects, deadlocks, and unsafe `fork` usage.
6. Distinguish ordinary GIL-enabled CPython, per-interpreter GILs in subinterpreters, and free-threaded CPython builds.
7. Use locks, queues, executors, process pools, shared memory, and alternative concurrency models appropriately.
8. Understand the broad mechanisms and ecosystem implications of PEP 703 free-threaded CPython.

## Prerequisites and mental model

You should know functions, loops, exceptions, basic operating-system processes/threads, and how to run a Python script. Familiarity with `threading`, `multiprocessing`, and `concurrent.futures` helps.

**Mental model:** a thread is a path of execution; a process is an OS isolation/resource boundary; an interpreter owns Python runtime state. In conventional CPython, a GIL generally serializes execution of Python bytecode within one interpreter. Blocking I/O and some native extensions release it, allowing another thread to run or native work to proceed concurrently. Subinterpreters can have separate interpreter state and separate GILs when configured to do so. A free-threaded build changes the runtime so Python threads can execute in parallel without the traditional global lock, but it does not make shared application logic automatically correct.

```text
GIL-enabled interpreter
  Thread A ─┐
            ├── one interpreter-wide GIL ── Python execution serialized
  Thread B ─┘       (blocking I/O / some native work may release it)

Subinterpreters (supported configurations)
  Interpreter A + its GIL     Interpreter B + its GIL
       separate runtime state; explicit data exchange required

Free-threaded CPython build
  Thread A ──┐
  Thread B ──┼── can execute Python in parallel; shared state still needs design
  Thread C ──┘
```

The GIL is a **CPython implementation detail**, not a general requirement of the Python language. Other Python implementations may use different execution and synchronization models.

## 1. What the GIL protects—and what it does not

The Global Interpreter Lock is a mutex used by conventional GIL-enabled CPython to coordinate access to interpreter state. Historically, it simplified reference counting and ensured that only one thread at a time executed Python bytecode in a given interpreter. It also simplified assumptions in much of the C extension ecosystem.

That does **not** mean the GIL is a universal application lock. It does not protect a logical transaction spanning multiple operations, make external resources thread-safe, prevent races in native code that releases the GIL, or guarantee a compound Python statement behaves atomically under every version/build.

### A shared-counter race

```python
import threading

counter = 0

def increment_many(count):
    global counter
    for _ in range(count):
        counter += 1

threads = [threading.Thread(target=increment_many, args=(100_000,))
           for _ in range(4)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

print(counter)
```

On a conventional GIL-enabled CPython build, this example may appear to produce the expected total on some versions and runs. That observation is not a thread-safety contract. `counter += 1` is a read-modify-write sequence at the language level; thread switches, bytecode changes, callbacks, and free-threaded execution can expose lost updates. Never rely on this program's output as proof that increments are atomic.

### Fix it with a lock

```python
import threading

counter = 0
lock = threading.Lock()

def increment_many(count):
    global counter
    for _ in range(count):
        with lock:
            counter += 1

threads = [threading.Thread(target=increment_many, args=(100_000,))
           for _ in range(4)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

print(counter)  # 400000
```

The lock protects the complete read-modify-write sequence. Its cost is contention: all threads serialize around the critical section. For a high-volume counter, per-thread counters followed by a merge can reduce contention.

### Check-then-act is also a race

```python
# Unsafe pattern when shared by multiple threads:
if key not in cache:
    cache[key] = build_value(key)
```

Two threads can both observe the key as absent and both build the value. Even if individual dictionary operations are safe on a given build, the sequence is not an atomic transaction. Use a lock around the whole operation, a suitable cache abstraction, or a design that tolerates duplicate computation.

**Real-world example:** two request threads both check that a payment has not been processed, then both charge the card. A GIL does not provide the business-level transaction. Use database constraints/idempotency keys and transactional coordination, not an assumption about Python scheduling.

## 2. CPU-bound versus I/O-bound threads

### CPU-bound pure Python

In conventional GIL-enabled CPython, threads running CPU-heavy pure-Python loops do not normally execute Python bytecode in parallel in one interpreter. Threads can still be useful for responsiveness or coordinating work, but adding more CPU-bound threads often adds scheduling and lock overhead without increasing throughput.

### I/O-bound work

Blocking operations such as many socket, file, and sleep operations release the GIL while waiting. Another thread can execute Python during that wait. Threads are therefore often useful for blocking libraries and workloads that spend much time waiting on independent I/O.

### Native extensions

A C extension can release the GIL around work that does not access Python objects, commonly using C API macros such as `Py_BEGIN_ALLOW_THREADS` / `Py_END_ALLOW_THREADS` (subject to the API and build requirements). NumPy releases the GIL for many operations on numeric arrays, and compression or hashing libraries may release it for significant native work. This is operation-specific: not every function in a library releases the GIL, and native code must not access Python objects unsafely while the GIL is released.

Pure Python does not spontaneously release the GIL just because a loop is long. It can call an extension that releases it, block in I/O, or yield to an event loop, but those are different mechanisms.

## 3. Switching interval and eval breaker

`sys.getswitchinterval()` returns the interpreter's ideal thread-switching interval in seconds; `sys.setswitchinterval()` changes it. A common default is `0.005` seconds (5 ms), but code should query the running interpreter rather than assume a fixed value.

```python
import sys

print("switch interval:", sys.getswitchinterval())
# Optional experiment only; restore the original value afterward.
old = sys.getswitchinterval()
try:
    sys.setswitchinterval(0.002)
    print("new interval:", sys.getswitchinterval())
finally:
    sys.setswitchinterval(old)
```

This interval is not a hard real-time scheduling guarantee. OS scheduling, blocking calls, native code, and runtime state affect when a thread actually runs. Conceptually, CPython's evaluator uses an **eval breaker**/pending-work mechanism to notice that it should handle a thread switch or other pending runtime work at suitable points. Exact flags, checks, and implementation functions change across releases.

The GIL's scheduling policy changed significantly in CPython 3.2 compared with the older design, reducing some unfairness/convoy behavior. It still does not guarantee equal CPU time or strict priority ordering for every thread.

## 4. Benchmarking concurrency fairly

A benchmark must compare equivalent work. Control input size, warm-up, interpreter/build, CPU affinity if practical, process startup, result transfer, and number of trials. Use `time.perf_counter()`, run several trials, and report a median and spread. Do not use a single noisy wall-clock result to declare a concurrency model faster.

### Benchmark harness: threads, processes, and serial baseline

Save as `concurrency_bench.py`:

```python
import concurrent.futures
import os
import statistics
import time

N = 2_000_000
REPEATS = 3

def cpu_task(n):
    # Deliberately CPU-bound pure Python; return a value to prevent dead work.
    total = 0
    for i in range(n):
        total += (i % 97)
    return total

def timed(label, runner):
    samples = []
    for _ in range(REPEATS):
        start = time.perf_counter()
        result = runner()
        samples.append(time.perf_counter() - start)
        assert result is not None
    print(f"{label:18} median={statistics.median(samples):.3f}s samples={samples}")

def serial():
    return [cpu_task(N) for _ in range(4)]

def threads():
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        return list(pool.map(cpu_task, [N] * 4))

def processes():
    # Process creation/serialization overhead is included in this simple test.
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:
        return list(pool.map(cpu_task, [N] * 4))

if __name__ == "__main__":
    print("Python process PID:", os.getpid())
    # Warm up one task before timing the variants.
    cpu_task(10_000)
    timed("serial", serial)
    timed("4 threads", threads)
    timed("4 processes", processes)
```

Run with `python concurrency_bench.py`. Timings are representative only; do not expect fixed numbers. On a conventional GIL-enabled build, the CPU-bound thread version often does not outperform serial execution. Processes may scale across CPU cores but pay startup, IPC, and serialization costs. Results depend on the machine and workload.

**Question:** What changes when the work is blocking I/O? Replace `cpu_task` with a function that calls `time.sleep(0.1)` and compare equivalent batches. Threads can overlap waits; process startup can dominate short tasks. This is a different workload and should be reported separately.

**What the benchmark does not prove:** it does not measure every workload, isolate scheduler overhead perfectly, or guarantee performance on a free-threaded build. Repeat with realistic task sizes, warm-up, varied worker counts, and the actual deployment environment. If available, use `py-spy --gil` to inspect time spent waiting for the GIL; use `perf` or an appropriate profiler for broader CPU behavior.

## 5. Locks, queues, executors, and contention

Choose synchronization primitives based on the invariant you need to preserve:

- `threading.Lock`: simple mutual exclusion.
- `threading.RLock`: re-entrant lock when the same thread must acquire the same lock recursively; it is not automatically safer than `Lock`.
- `Condition`: wait for a state predicate while coordinating with a lock; always re-check the predicate in a loop.
- `Semaphore`: limit concurrent access to a resource pool.
- `Event`: signal a state change to waiting threads.
- `Barrier`: coordinate a fixed group of threads at a phase boundary.
- `queue.Queue`: safe producer/consumer handoff with synchronization.
- `concurrent.futures`: task/result abstraction using thread or process executors.
- `itertools.count`: can be useful for generating a sequence of values, but do not treat it as a portable, general-purpose atomic counter for coordinating compound shared-state updates across Python implementations/builds. Use a lock or a dedicated synchronized design when correctness depends on atomicity.

### Queue-based producer/consumer

```python
import queue
import threading

work = queue.Queue()
results = []

def worker():
    while True:
        item = work.get()
        try:
            if item is None:
                return
            results.append(item * item)
        finally:
            work.task_done()

thread = threading.Thread(target=worker)
thread.start()
for number in range(5):
    work.put(number)
work.put(None)
work.join()
thread.join()
print(sorted(results))
```

Output:

```text
[0, 1, 4, 9, 16]
```

The queue synchronizes handoff; `results.append()` is used here by a single worker. With multiple workers, appending is individually supported by conventional CPython behavior, but use explicit synchronization or a queue if the whole result-handling sequence has an invariant.

### Contention, convoy effects, and deadlocks

**Contention** occurs when threads compete for a lock or resource. A **convoy effect** occurs when a slow or descheduled owner/contender delays other work, reducing throughput. Fine-grained locks can improve parallelism but make correctness harder; coarse-grained locks simplify reasoning but can serialize a workload.

Practical rules:
1. Keep critical sections small, but do not split a logical invariant into unsafe fragments.
2. Acquire multiple locks in a consistent global order.
3. Avoid calling unknown callbacks while holding a lock.
4. Prefer queues and ownership transfer over shared mutable state where feasible.
5. Diagnose contention before redesigning; more threads can worsen throughput.

An atomic-looking built-in operation is not a substitute for an application-level invariant. The roadmap notes that some individual list/dict operations are safe on conventional builds; do not extrapolate that to arbitrary sequences or all free-threaded/extension scenarios.

## 6. Processes, shared memory, and other concurrency models

### Process pools

`multiprocessing` and `ProcessPoolExecutor` use separate processes, so conventional GILs are separate and CPU-bound pure Python can run on multiple cores. Costs include process startup, duplicated interpreter/runtime memory, serialization, IPC, and failure management.

Use the `if __name__ == "__main__":` guard in scripts that may use `spawn` (especially Windows/macOS and explicitly selected start methods). Start methods include `spawn`, `fork`, and `forkserver`, but availability and defaults are platform/version-specific. Python 3.14 changed the default away from `fork` on supported POSIX systems; query `multiprocessing.get_start_method()` rather than assuming. Forking a multithreaded process can be unsafe and has produced warnings in recent Python releases; prefer `spawn` or `forkserver` unless you have a clear, tested reason otherwise.

### Shared memory

`multiprocessing.shared_memory` can exchange large buffers without pickling every value. It requires explicit lifecycle management, synchronization, and a clear data layout. Shared memory is not automatically a safe shared Python-object heap: it is most straightforward for bytes and packed numeric data.

### Decision table

| Workload/constraint | Candidate model | Main trade-off |
|---|---|---|
| Many concurrent blocking calls | Threads | Simple with blocking libraries; shared-state races need control |
| Many network connections with async-capable libraries | `asyncio` | Efficient cooperative I/O; blocking code stalls the event loop |
| CPU-bound pure Python on conventional CPython | Processes | Parallel CPU execution; startup and serialization costs |
| Numeric work in a native library that releases GIL | Vectorization / native library, sometimes threads | Depends on operation and data size |
| Separate interpreter state inside one process | Subinterpreters | Lower process boundary cost but extension/data-sharing constraints |
| CPU-bound Python with a supported free-threaded build | Free-threaded threads | Parallelism potential; compatibility and synchronization costs |
| Distributed or cluster-scale work | Distributed systems (e.g. Dask/Ray/Spark) | Operational complexity and data movement |

## 7. Subinterpreters and per-interpreter GIL

A process can host multiple Python interpreters. Each interpreter has its own interpreter state and module state; subinterpreters are not equivalent to threads sharing one interpreter or to fully isolated OS processes.

PEP 684 introduced a per-interpreter GIL for CPython's C API, implemented in CPython 3.12. This allows separate interpreters to run with separate GILs in supported configurations. Subinterpreters still share a process address space, so native global state and extension modules that assume a single interpreter can be problematic. Python objects generally cannot simply be shared arbitrarily across interpreter boundaries; communication commonly uses channels/queues, serialized messages, or shared-memory buffers.

PEP 554 described a high-level API direction; PEP 734 covers channels. Availability and API shape are version-sensitive. In Python 3.14, `concurrent.interpreters` and `InterpreterPoolExecutor` are available for supported builds; check the exact 3.14 documentation and build rather than assuming this API exists on 3.12/3.13.

### Example: feature detection

```python
import sys

print("Python:", sys.version.split()[0])
try:
    import concurrent.interpreters as interpreters
except ImportError:
    print("high-level concurrent.interpreters API unavailable")
else:
    print("concurrent.interpreters available:", interpreters)
```

The result depends on interpreter version and build. This is a feature-detection example, not a runnable cross-version subinterpreter task example.

### Extension compatibility

C extensions may have process-global mutable state or assume one interpreter. Multi-phase module initialization (PEP 489) and per-module state help make extensions compatible with multiple interpreters. Extensions must declare/support the relevant interpreter compatibility requirements; a module that imports successfully in one interpreter is not proof it is safe in several.

Use subinterpreters when you want lower-cost interpreter isolation and compatible extensions, and where communication can be explicit. Use processes when stronger OS-level isolation, crash containment, or broad extension compatibility matters more. Neither is a security sandbox by default.

## 8. Free-threaded CPython and PEP 703

PEP 703 proposed making the GIL optional in CPython. Free-threaded builds are available experimentally/optionally beginning with CPython 3.13 and continue to evolve in 3.14. A conventional build and a free-threaded build are distinct build configurations; the `t` ABI tag is used for free-threaded builds (for example, wheels tagged with a `cp314t` interpreter tag). Not every extension or wheel is compatible.

### Detecting build and GIL state

```python
import sys

print("implementation:", sys.implementation.name)
print("version:", sys.version)
print("free-threaded build flag:", getattr(sys, "_is_gil_enabled", None))
if hasattr(sys, "_is_gil_enabled"):
    print("GIL currently enabled:", sys._is_gil_enabled())
```

`sys._is_gil_enabled()` is a private/version-specific diagnostic available in relevant free-threaded CPython builds; feature-detect it. The build may be free-threaded while the GIL is enabled at runtime, for example because of runtime configuration or an extension compatibility requirement. Do not infer runtime GIL state solely from a filename or ABI tag.

The `PYTHON_GIL` environment variable can control GIL behavior in relevant free-threaded builds (`0` to disable and `1` to enable, subject to version/build constraints). Confirm the target release documentation and test at process startup; it is not a universal environment setting for ordinary CPython builds. For C extensions, the `Py_mod_gil` module slot (where supported) communicates a module’s GIL requirements/compatibility to the runtime; declaring compatibility is not a substitute for actually auditing and testing native code.

### What changes internally (appropriate high-level view)

Without a single global lock protecting all interpreter execution, CPython needs more careful coordination for object lifetime and shared mutable objects. PEP 703 and the implementation include strategies such as:

- **Biased and deferred reference counting:** reduce contention and reference-count updates for selected cases; reclamation rules become more complex.
- **Per-object locks / critical sections:** coordinate mutations to shared container/object state where needed.
- **mimalloc-based allocation:** allocator strategy adapted for free-threaded execution, including per-thread allocation structures/caches.
- **Immortalization and runtime optimizations:** selected long-lived objects can avoid some reference-count writes.
- **Specialization constraints:** optimizations must remain correct when multiple threads can mutate state concurrently.

These are implementation mechanisms, not guarantees that every operation is lock-free or that Python-level data races disappear. A per-container lock can protect an individual container operation while a compound check-then-act sequence remains racy.

### Extension readiness and deployment

Before deploying a free-threaded build:
1. Verify that every critical C extension has a compatible wheel/build and explicitly supports free-threaded operation.
2. Review extension thread-safety declarations and `Py_mod_gil` support where applicable; check the relevant version's C API docs.
3. Run correctness tests under concurrent stress, not just speed benchmarks.
4. Benchmark single-thread performance as well as scaling: free-threaded builds can have overhead in some workloads, although the overhead has been reduced over releases.
5. Measure memory, including per-thread allocator caches and concurrent temporary allocations.
6. Roll out behind staged deployment/canaries with a tested fallback to a conventional build.

Free-threaded execution can enable CPU parallelism in Python code, but it does not fix algorithmic bottlenecks, lock contention, I/O latency, unsafe extension globals, deadlocks, or incorrect synchronization.

## 9. Thread-local state, `contextvars`, and signal/shutdown behavior

`threading.local()` stores data local to a thread. `contextvars` supports context-local values that follow asynchronous task contexts more appropriately than thread-local state alone. They solve different scoping problems; neither is a synchronization primitive for shared mutable objects.

Python signal handlers are generally executed in the main Python thread of the main interpreter, not an arbitrary worker thread. Do not design a worker to depend on receiving a Python signal handler directly. Use an event, queue, or other explicit cancellation mechanism.

Daemon threads do not keep the process alive at shutdown and may be stopped abruptly; use non-daemon threads and explicit stop/join protocols when cleanup matters. Avoid starting complex work from destructors during interpreter shutdown.

## 10. Race-analysis exercise: find the invariant, not just the statement

Analyze the following patterns. For each, state the shared state, the invariant, the interleaving that can violate it, and the synchronization boundary required.

```python
# A. Check then act
if account.balance >= amount:
    account.balance -= amount

# B. Shared counter
counter += 1

# C. Shared cache
if key not in cache:
    cache[key] = build_value(key)

# D. Iteration while another thread mutates a list
for item in shared_items:
    process(item)
```

Suggested analysis:
- A: two threads can both observe sufficient balance and both debit; protect the transaction with a lock and, for real financial systems, enforce the invariant in the durable transactional system too.
- B: read-modify-write can lose updates; lock, use per-thread counters and merge, or use a suitable concurrent design.
- C: duplicate work or inconsistent initialization can occur; lock around the full sequence or use a cache API with appropriate semantics.
- D: mutation can change what is visited or cause errors/logic bugs; coordinate mutation/iteration or iterate over a snapshot if snapshot semantics are appropriate.

Do not claim a particular interleaving is guaranteed to occur in one run. Race conditions are about possible execution schedules and correctness, not whether a short demonstration happens to fail.

## 11. Benchmark exercise: threads, processes, and free-threaded/subinterpreters

**Question:** How does one CPU-bound workload compare across concurrency models on the actual deployment environment?

**Setup:** use the harness in Section 4. If available, repeat on conventional CPython 3.13, free-threaded CPython 3.13t, and/or 3.14t. If using `InterpreterPoolExecutor`, use the API documented for the installed CPython 3.14 build. Do not fabricate missing comparisons when a build or API is unavailable.

**Procedure:**
1. Record version, build/GIL state, CPU model/count, OS, power mode, and environment variables.
2. Warm up the workload and compare equivalent total work.
3. Run serial, 1/2/4/8 threads, process pools, and available interpreter/free-threaded variants.
4. Include startup and data-transfer costs in one end-to-end measurement; separately measure steady-state task execution if that is the real production question.
5. Run multiple trials, report median and spread, and watch memory as worker count increases.
6. Use realistic task sizes and inspect GIL contention where possible.

**Expected observations:** on a conventional build, CPU-bound pure Python threads often do not scale with cores; processes may scale at sufficient task sizes; free-threaded builds may scale but have overhead/compatibility trade-offs; subinterpreters can run with separate GILs where supported but have initialization and communication costs. Results vary by workload, machine, extension set, and Python release.

**Interpretation:** choose the model by measured end-to-end throughput, latency, memory, startup, isolation, and operational constraints—not a slogan about the GIL.

**What it does not prove:** one benchmark cannot predict all applications or prove thread safety. It does not isolate the effect of one runtime change unless the experimental controls support that conclusion.

## 12. Common mistakes and troubleshooting

| Mistake | Why it fails | Better approach |
|---|---|---|
| Using threads for CPU-bound pure Python and expecting automatic speed-up | Traditional GIL serializes Python bytecode in one interpreter | Benchmark processes, native code, subinterpreters, or free-threaded builds where available |
| Assuming the GIL makes `x += 1` atomic | Compound logic is not an application transaction | Use a lock, queue, or per-worker accumulation |
| Calling `fork` from a multithreaded program | Locks and runtime state can be inherited in unsafe states | Prefer `spawn`/`forkserver` unless tested requirements dictate otherwise |
| Benchmarking once | Scheduler noise, warm-up, turbo/power state, and process startup distort results | Repeat, warm up, report median/spread, record environment |
| Assuming every extension works in free-threaded or subinterpreter mode | Extensions may use global state or assume a single GIL/interpreter | Verify compatibility and stress-test critical dependencies |
| Assuming subinterpreters are a security sandbox | Interpreters share a process address space and native runtime | Use process/OS isolation for security boundaries |
| Assuming free-threaded mode removes synchronization needs | Shared invariants can still race; locks can still contend | Audit shared state and test concurrent correctness |

For a production incident, record the interpreter/build, determine whether the workload is CPU- or I/O-bound, inspect contention, and reduce the problem to a minimal reproducible case. Use `py-spy --gil`, OS profilers, thread dumps, and structured lock diagnostics as appropriate. A profile shows where time is spent; it does not replace a correctness proof.

## 13. Concept map and decision workflow

```text
Workload
  ├── mostly waiting on I/O → asyncio (async-capable APIs) or threads (blocking APIs)
  ├── CPU-bound pure Python
  │     ├── conventional build → process pool
  │     ├── compatible subinterpreters → interpreter pool (version-sensitive)
  │     └── compatible free-threaded build → threads, benchmark carefully
  └── numeric/native work
        └── vectorize or use native libraries; confirm whether the operation releases GIL

Any model with shared state
  └── define invariant → choose ownership/queue/lock → test interleavings and failure paths

Before deployment
  └── benchmark end-to-end + correctness stress + memory + extension compatibility
```

## 14. Self-check questions with answers

### 1. Why do I/O-bound threads benefit despite the GIL?

**Answer:** Many blocking I/O operations release the GIL while waiting. Another thread can run Python during that wait, so independent waits overlap. The GIL limits parallel execution of Python bytecode in one conventional interpreter; it does not prevent all concurrency.

### 2. What changes in a free-threaded build, and what does it not fix?

**Answer:** A free-threaded CPython build can allow multiple threads to execute Python code in parallel without the traditional global GIL. It needs additional coordination for reference counting, object/container mutation, and allocation; mechanisms include biased/deferred reference counting, per-object locks/critical sections, and a mimalloc-based allocator strategy. It does not automatically fix application data races, compound-operation invariants, deadlocks, contention, unsafe native extensions, or I/O bottlenecks. Extension compatibility and runtime GIL state must be checked for the specific build.

### 3. Benchmark one CPU-bound task using threads, processes, and (if available) a free-threaded build or interpreter pool, and explain the numbers.

**Answer:** Use Sections 4 and 11. Keep total work equivalent, warm up, repeat trials, report median/spread, and record the interpreter/build and hardware. Conventional GIL-enabled threads often show little CPU-bound speed-up; processes may scale once work amortizes startup/serialization; free-threaded builds and interpreter pools may scale when supported, but runtime overhead, extension compatibility, memory, and data transfer can dominate. If a target build/API is unavailable, state that limitation rather than inventing results.

## Summary

- The GIL is a CPython runtime lock, not a general-purpose application lock or a Python-language guarantee.
- Blocking I/O and some native operations release the GIL; CPU-bound pure-Python threads generally do not execute bytecode in parallel in one conventional interpreter.
- A time-slice/switch interval is a scheduling hint, not a real-time guarantee; eval-breaker internals are version-specific.
- Compound operations need explicit synchronization even when individual container operations are protected on a given build.
- Processes, subinterpreters, native/vectorized code, async I/O, and free-threaded CPython solve different problems and have different costs.
- Subinterpreters can have per-interpreter GILs, but object sharing and extension compatibility require care.
- PEP 703 free-threaded builds enable Python-level parallelism but do not remove races, deadlocks, compatibility checks, or measurement requirements.
- Benchmark the real workload end-to-end, include memory and startup costs, and deploy changes gradually.

## References

1. Python `threading` documentation: https://docs.python.org/3/library/threading.html
2. `sys.getswitchinterval` and runtime APIs: https://docs.python.org/3/library/sys.html#sys.getswitchinterval
3. `concurrent.futures`: https://docs.python.org/3/library/concurrent.futures.html
4. `multiprocessing` and start methods: https://docs.python.org/3/library/multiprocessing.html
5. `queue`: https://docs.python.org/3/library/queue.html
6. PEP 703 — Making the Global Interpreter Lock Optional in CPython: https://peps.python.org/pep-0703/
7. PEP 684 — A Per-Interpreter GIL: https://peps.python.org/pep-0684/
8. PEP 554 — Multiple Interpreters in the Stdlib: https://peps.python.org/pep-0554/
9. PEP 734 — Multiple Interpreter Communication: https://peps.python.org/pep-0734/
10. PEP 489 — Multi-phase extension module initialization: https://peps.python.org/pep-0489/
11. Python/C API thread state and GIL: https://docs.python.org/3/c-api/threads.html
12. Python 3.12 “What’s New”: https://docs.python.org/3/whatsnew/3.12.html
13. Python 3.13 “What’s New”: https://docs.python.org/3/whatsnew/3.13.html
14. Python 3.14 “What’s New”: https://docs.python.org/3/whatsnew/3.14.html
15. `py-spy` documentation: https://github.com/benfred/py-spy
