# Threading and ThreadPoolExecutor

> **Module:** Stage 2 — Python for Data Engineering  
> **Topic:** 01 — Threading and ThreadPoolExecutor  
> **Audience:** Beginner progressing toward production Data Engineering  
> **Python target:** Python 3.13+ where version-specific behavior is discussed

---

## 1. Learning Objectives

By the end of this chapter, you should be able to:

- explain what a thread is and why threads exist;
- distinguish sequential execution from concurrency;
- distinguish concurrency from parallelism at the level required for Python Data Engineering;
- identify I/O-bound workloads;
- explain why threads can improve I/O-bound work;
- explain the introductory relationship between threads and the CPython GIL;
- create and manage `threading.Thread`;
- use `start()` and `join()` correctly;
- understand a basic thread lifecycle;
- explain why manually creating many threads becomes difficult to manage;
- use `concurrent.futures.ThreadPoolExecutor`;
- submit work with `submit()`;
- understand what a `Future` represents;
- retrieve results with `result()`;
- use `executor.map()`;
- use `as_completed()`;
- map completed futures back to their original inputs;
- collect every worker exception;
- distinguish collect-all and fail-fast policies;
- use `wait()` with `ALL_COMPLETED`, `FIRST_COMPLETED`, and `FIRST_EXCEPTION`;
- cancel pending work with `shutdown(cancel_futures=True)` where appropriate;
- shut down executors cleanly;
- select `max_workers` using workload and external-system limits rather than CPU-count guessing;
- reason about HTTP/API limits, database pools, object storage, file descriptors, memory, and fairness;
- distinguish shared thread-safe resources from unsafe shared mutable objects;
- use `threading.local` when per-thread state is appropriate;
- avoid submitting enormous numbers of futures at once;
- understand bounded submission and `Executor.map(..., buffersize=...)` on Python versions that support it;
- understand why daemon threads are inappropriate for critical data-processing work;
- make logs thread-aware;
- build a production-oriented threaded downloader;
- measure sequential and concurrent performance;
- inject and report failures;
- write downloaded files atomically;
- compare threaded results with a sequential correctness baseline;
- recognize when more threads are making the system worse rather than better.

The central question for this chapter is:

> **When should I use threads in a Data Engineering workload, how should I implement them safely, how should I bound them, how should I handle failures, and how do I prove that concurrency actually improved the job?**

---

# 2. Core Principle

> **Threads are a tool for overlapping waiting, not a magic switch for making Python code faster.**

For an I/O-heavy workload, the basic idea is:

```text
I/O-bound work
    ↓
CPU spends significant time waiting
    ↓
another thread can run
    ↓
waiting periods overlap
    ↓
wall-clock time can decrease
```

For CPU-bound pure-Python work, the situation is different:

```text
CPU-bound Python work
    ↓
threads contend for Python execution
    ↓
standard CPython's GIL limits simultaneous Python-bytecode execution
    ↓
threads are generally not the mechanism for CPU parallelism
```

Do not confuse this with a rule that "threads are slow." Threads can be extremely effective when the dominant cost is waiting on an external system.

The engineering objective is not:

> Use as many threads as possible.

It is:

> Use enough bounded concurrency to improve useful throughput while preserving correctness, respecting external limits, controlling memory, and keeping failures observable.

---

# 3. Prerequisites

This topic assumes you already have a working foundation in:

- Python functions;
- exceptions;
- context managers;
- generators;
- logging;
- HTTP clients;
- database connections;
- database connection pools;
- object storage;
- rate limits;
- basic performance measurement.

You do not need to know concurrency beforehand. This chapter introduces the concepts progressively.

A common Data Engineering combination looks like:

```text
HTTP client
     +
connection/resource pool
     +
ThreadPoolExecutor
     ↓
concurrent I/O extraction
```

The thread pool is not a replacement for the client, database, object store, or connection pool. It is an execution mechanism around work that spends time waiting.

---

# 4. What Is a Thread?

## What is it?

A **thread** is an execution path inside a process.

A process provides an address space and operating-system resources. A process can contain multiple threads:

```text
Process
│
├── Thread 1
├── Thread 2
├── Thread 3
└── Thread 4
```

Threads in the same process share the process's memory and many process-level resources.

This is useful because workers can access common resources without requiring inter-process communication.

It is also dangerous because shared mutable state can create correctness problems.

A useful mental model is:

```text
Process
│
├── shared memory/resources
│
├── Thread A → execution path
├── Thread B → execution path
└── Thread C → execution path
```

The operating system/runtime schedules runnable threads. A thread can also spend time blocked or waiting, for example while an HTTP response or database query is pending.

## Why do threads exist?

Threads allow a process to have multiple independently progressing execution paths.

For Data Engineering, that is valuable when one operation spends substantial time waiting:

```text
Thread A → sends HTTP request → waits
Thread B → sends HTTP request → waits
Thread C → reads object → waits
Thread D → runs a small amount of Python
```

While one thread is waiting for I/O, another can use available execution time.

## Shared memory: useful and dangerous

The same-process model makes communication convenient:

```text
Thread A ─┐
Thread B ─┼──→ shared process memory
Thread C ─┘
```

But shared mutable state means multiple threads may interact with the same object.

That creates a broad category of risks:

```text
shared mutable state
       ↓
multiple execution paths
       ↓
ordering/coordination problem
       ↓
possible race/correctness bug
```

Locks and detailed race-condition mechanics belong to the later concurrency topic. For this chapter, establish the rule:

> Prefer returning values from worker functions and aggregating results centrally rather than having many workers mutate the same shared data structure.

---

# 5. Concurrency vs Sequential Execution

Consider five independent downloads.

A sequential implementation behaves approximately like:

```text
download A ──────┐
                 ↓
download B ──────┐
                 ↓
download C ──────┐
                 ↓
download D ──────┐
                 ↓
download E ──────┘
```

If every download takes approximately one second of waiting:

```text
1 + 1 + 1 + 1 + 1 ≈ 5 seconds
```

A concurrent implementation can overlap the waits:

```text
Thread 1 → download A ─────────
Thread 2 → download B ─────────
Thread 3 → download C ─────────
Thread 4 → download D ─────────
Thread 5 → download E ─────────
```

In an idealized case, wall-clock time approaches the longest individual operation rather than the sum of all operations.

Real systems never scale perfectly. There is scheduling overhead, network variability, connection setup, remote-server work, throttling, contention, and other constraints.

Therefore:

> **Concurrency reduces elapsed time only when the workload has waiting that can safely overlap and the surrounding system has capacity to handle the additional concurrency.**

---

# 6. I/O-Bound vs CPU-Bound Work

This distinction is one of the most important ideas in this chapter.

## I/O-bound workloads

An I/O-bound operation spends a meaningful portion of its lifetime waiting for external I/O.

Examples:

- HTTP requests;
- API calls;
- downloading objects;
- reading remote files;
- database queries;
- waiting for a remote service;
- uploading files.

Conceptually:

```text
send request
    ↓
wait
    ↓
response arrives
    ↓
small amount of Python work
```

Threads can overlap those waits.

## CPU-bound workloads

CPU-bound work spends most of its time performing computation.

Examples:

- large pure-Python mathematical loops;
- CPU-heavy transformations;
- expensive Python parsing;
- computational algorithms.

Conceptually:

```text
execute Python computation
execute Python computation
execute Python computation
...
```

For standard CPython, the GIL means only one thread executes Python bytecode at a time. Threads can still run while another thread is blocked in I/O, which is why they remain useful for I/O-heavy programs.

Do not turn this section into a complete GIL or multiprocessing lesson. The important boundary is:

```text
I/O-bound
    → threads are often useful

CPU-bound pure Python
    → threads are generally not the primary CPU-parallelism tool
```

---

# 7. A First Sequential Example

Start with a deliberately simple simulation:

```python
import time


def download_file(file_id: int) -> str:
    time.sleep(1)
    return f"file-{file_id}"


for file_id in range(5):
    print(download_file(file_id))
```

The `sleep()` is standing in for an external wait.

Approximate timeline:

```text
file 0: ██████████
file 1:           ██████████
file 2:                      ██████████
file 3:                                 ██████████
file 4:                                            ██████████

          approximately 5 seconds
```

This is not a real downloader. It is a controlled experiment that makes the concurrency concept visible.

---

# 8. `threading.Thread`

Python's low-level threading primitive is `threading.Thread`.

```python
import threading
import time


def worker(name: str) -> None:
    print(f"{name} starting")
    time.sleep(1)
    print(f"{name} finished")


thread = threading.Thread(
    target=worker,
    args=("worker-1",),
)

thread.start()
thread.join()
```

## What happened?

```text
create Thread
    ↓
start()
    ↓
thread executes target
    ↓
thread finishes
    ↓
join()
    ↓
caller knows the thread has finished
```

### `target`

`target` specifies the callable the thread should execute.

### `args`

`args` supplies positional arguments to the target.

### `start()`

`start()` asks Python to begin execution in a new thread.

### `join()`

`join()` waits for the thread to finish.

---

# 9. `start()` vs `run()`

This distinction is easy to get wrong.

Correct:

```python
thread.start()
```

This starts a new thread.

By contrast:

```python
thread.run()
```

directly invokes the thread's target in the current execution path. It does not provide the normal new-thread behavior that `start()` provides.

A small demonstration:

```python
import threading


def worker() -> None:
    print("worker running")


thread = threading.Thread(target=worker)

print("before")
thread.run()
print("after")
```

The target runs synchronously from the caller's perspective.

Now compare:

```python
thread = threading.Thread(target=worker)

print("before")
thread.start()
thread.join()
print("after")
```

The second version actually starts a separate thread and then waits for it with `join()`.

Rule:

> Use `start()` when you intend to start the thread. `run()` is the target-execution method, not the normal public mechanism for starting concurrent execution.

---

# 10. `join()`

Suppose you create several threads:

```python
import threading
import time


def worker(name: str) -> None:
    time.sleep(1)
    print(f"{name} complete")


threads: list[threading.Thread] = []

for i in range(5):
    thread = threading.Thread(
        target=worker,
        args=(f"worker-{i}",),
    )
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()

print("all workers complete")
```

The first loop starts the workers.

The second loop waits for them.

```text
start worker 0
start worker 1
start worker 2
start worker 3
start worker 4

then:

join worker 0
join worker 1
join worker 2
join worker 3
join worker 4

all workers complete
```

`join()` is important because a Data Engineering program normally needs an explicit completion boundary before declaring a unit of work successful.

Do not confuse:

```text
start all work
```

with:

```text
wait for all work
```

Those are separate operations.

---

# 11. Basic Thread Lifecycle

A useful conceptual lifecycle is:

```text
Created
   ↓
Started
   ↓
Runnable
   ↓
Running
   ↓
Waiting / blocked
   ↓
Finished
```

The operating system and runtime decide exactly when runnable threads execute.

For I/O-heavy workloads, a thread may spend a lot of time in a waiting state.

For example:

```text
Thread A
    ↓
HTTP request
    ↓
waiting for server
    ↓
response arrives
    ↓
process response
```

While A is waiting, another worker can make progress.

Do not infer that you control exact OS scheduling order. You do not.

---

# 12. Why Raw `threading.Thread` Becomes Difficult

Manually creating threads is useful for understanding the primitive, but ordinary Data Engineering jobs usually have a higher-level problem:

```text
many independent tasks
        ↓
many workers
        ↓
need result collection
        ↓
need exception collection
        ↓
need cancellation
        ↓
need lifecycle management
        ↓
need bounded task submission
        ↓
need clean shutdown
```

If you manually create a thread for every task, you quickly end up implementing your own worker pool, task queue, result tracking, and shutdown system.

That is why Python provides:

```python
concurrent.futures.ThreadPoolExecutor
```

For ordinary I/O-bound task pools, this is usually a much cleaner abstraction.

---

# 13. ThreadPoolExecutor

The executor gives you a pool of reusable worker threads.

```python
from concurrent.futures import ThreadPoolExecutor


def fetch(item: int) -> str:
    return f"processed-{item}"


with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(fetch, item)
        for item in range(10)
    ]

    for future in futures:
        print(future.result())
```

Conceptually:

```text
ThreadPoolExecutor
        │
        ├── worker thread 1
        ├── worker thread 2
        ├── worker thread 3
        └── worker thread 4

submitted tasks
        ↓
worker pool
        ↓
Future objects
```

The executor manages worker threads for you.

The context manager:

```python
with ThreadPoolExecutor(...) as executor:
    ...
```

also gives the executor a clear lifecycle boundary and performs normal shutdown when the block exits.

---

# 14. What Is a Future?

A `Future` represents work that has been submitted but may not have completed yet.

Think of it as a receipt for work:

```text
submit task
    ↓
Future returned immediately
    ↓
worker eventually executes task
    ↓
Future becomes complete
    ↓
caller retrieves result/error
```

A simplified conceptual state model is:

```text
Pending
   ↓
Running
   ↓
Finished
```

or:

```text
Pending
   ↓
Cancelled
```

A `Future` gives you useful operations such as:

```python
future.result()
future.exception()
future.done()
future.cancel()
future.cancelled()
```

### `result()`

Returns the worker's return value.

If the worker raised an exception, `result()` re-raises that exception in the thread calling `result()`.

### `exception()`

Returns the exception object if the task failed, or `None` when no exception was raised.

### `done()`

Reports whether the future completed or was cancelled.

### `cancel()`

Attempts to cancel work that has not started.

Cancellation generally cannot safely stop arbitrary work that is already running.

---

# 15. `submit()`

The basic API is:

```python
future = executor.submit(function, argument)
```

For example:

```python
from concurrent.futures import ThreadPoolExecutor


def fetch(item: int) -> str:
    return f"item-{item}"


with ThreadPoolExecutor(max_workers=4) as executor:
    future_a = executor.submit(fetch, 1)
    future_b = executor.submit(fetch, 2)

    print(future_a.result())
    print(future_b.result())
```

The important distinction is:

```text
executor.submit(...)
        ↓
returns Future immediately
        ↓
work executes independently
        ↓
future.result()
        ↓
retrieve outcome
```

Do not write:

```python
future = executor.submit(fetch, item)
# assume the result is already available
```

The Future is a handle to potentially unfinished work.

---

# 16. Result Collection: Direct Future Iteration

A common pattern is:

```python
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(fetch, item)
        for item in items
    ]

    for future in futures:
        result = future.result()
        print(result)
```

This has an important ordering property.

Suppose:

```text
Task A = 5 seconds
Task B = 1 second
Task C = 2 seconds
```

If `futures` is `[A, B, C]`, the main thread waits for A before retrieving B and C.

That does not mean B and C were not running. They may already have completed. It means the consumer is retrieving results in submission order.

This distinction matters when individual tasks have highly variable durations.

---

# 17. `executor.map()`

For simple transformations, `map()` is concise:

```python
from concurrent.futures import ThreadPoolExecutor


def fetch(item: int) -> str:
    return f"processed-{item}"


items = range(10)

with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(fetch, items)

    for result in results:
        print(result)
```

A key property:

> Results are yielded in input order.

That makes `map()` convenient when you want the output sequence to correspond to the input sequence.

It is less flexible when you need to react to whichever task finishes first, attach detailed per-input failure metadata, or implement complex fail-fast behavior.

---

# 18. `map()` vs `as_completed()`

| Feature | `executor.map()` | `as_completed()` |
|---|---|---|
| Result ordering | Input order | Completion order |
| Process fast results early | Limited by result consumption order | Yes |
| Per-task exception handling | Less flexible | Very flexible |
| Input-to-result association | Implicit by position | Explicit mapping is useful |
| Good for | Simple homogeneous work | Variable-duration production tasks |

Consider:

```text
Task A = 5 sec
Task B = 1 sec
Task C = 2 sec
```

With ordered result consumption:

```text
A result → after 5 sec
B result → may already be ready
C result → may already be ready
```

With `as_completed()`:

```text
B completes → process B
C completes → process C
A completes → process A
```

For heterogeneous I/O workloads, `as_completed()` is often the more useful control structure.

---

# 19. `as_completed()`

A production-oriented pattern is:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed


def fetch(item: int) -> str:
    return f"processed-{item}"


items = [10, 20, 30, 40]

with ThreadPoolExecutor(max_workers=4) as executor:
    future_to_item = {
        executor.submit(fetch, item): item
        for item in items
    }

    for future in as_completed(future_to_item):
        item = future_to_item[future]

        try:
            result = future.result()
        except Exception as exc:
            print(f"{item} failed: {exc!r}")
        else:
            print(f"{item} succeeded: {result}")
```

The important production pattern is:

```text
Future → original input
```

Why?

Because the Future itself does not automatically tell your application which business object it represents.

For a downloader, you need:

```text
Future → object key
Future → destination path
Future → request ID
Future → partition ID
Future → database query ID
```

This lets logs and failure reports identify the actual failed work.

---

# 20. Exceptions Live in Futures

Consider:

```python
def fetch(item: int) -> str:
    if item == 5:
        raise RuntimeError("download failed")

    return str(item)
```

Now:

```python
with ThreadPoolExecutor(max_workers=4) as executor:
    future = executor.submit(fetch, 5)
```

The exception is associated with the Future.

It does not necessarily appear in the submitting thread at the exact moment `submit()` is called.

The exception becomes visible when you inspect the Future, for example:

```python
future.result()
```

which re-raises the worker exception.

Or:

```python
exc = future.exception()
```

which lets you inspect it.

The critical production rule is:

> **If you submit work and never observe the Future, you can lose important worker failures.**

This is one of the most dangerous beginner mistakes with concurrent pipelines.

---

# 21. Collecting All Errors

For independent work, you often want the whole run report rather than stopping at the first failure.

```python
from concurrent.futures import ThreadPoolExecutor, as_completed


def fetch(item: int) -> str:
    if item % 10 == 0:
        raise RuntimeError(f"failed item {item}")

    return f"processed-{item}"


items = range(1, 51)
successes: list[str] = []
failures: list[dict[str, str]] = []

with ThreadPoolExecutor(max_workers=8) as executor:
    future_to_item = {
        executor.submit(fetch, item): item
        for item in items
    }

    for future in as_completed(future_to_item):
        item = future_to_item[future]

        try:
            result = future.result()
        except Exception as exc:
            failures.append(
                {
                    "item": str(item),
                    "error": repr(exc),
                }
            )
        else:
            successes.append(result)

print(f"successes={len(successes)}")
print(f"failures={len(failures)}")
```

This design gives you:

```text
successes
+
failures
+
original input identity
+
exception details
```

That information can feed a run report, retry policy, alert, or downstream decision.

---

# 22. Collect-All vs Fail-Fast

Neither strategy is universally correct.

## Collect-all

Use when tasks are independent and it is useful to know the complete failure set.

```text
submit work
    ↓
process all independent tasks
    ↓
collect successes and failures
    ↓
evaluate failure policy
```

Examples:

- download a batch of independent objects;
- fetch independent API records;
- process independent partitions.

## Fail-fast

Use when continuing is not useful or could make the situation worse.

```text
critical failure
    ↓
stop/cancel pending work where possible
    ↓
allow running work to finish safely
    ↓
collect final state
    ↓
fail the run
```

Examples:

- a required prerequisite becomes unavailable;
- a critical schema validation fails;
- continuing would create invalid downstream output.

Make the policy explicit.

Do not accidentally implement fail-fast behavior merely because one call to `result()` raised an exception.

---

# 23. `wait()`

`concurrent.futures.wait()` is useful when you want to reason about a group of Futures as a set.

```python
from concurrent.futures import (
    ThreadPoolExecutor,
    wait,
    ALL_COMPLETED,
    FIRST_COMPLETED,
    FIRST_EXCEPTION,
)
```

Basic use:

```python
done, not_done = wait(
    futures,
    return_when=ALL_COMPLETED,
)
```

The main modes are:

### `ALL_COMPLETED`

Return when every Future is complete.

### `FIRST_COMPLETED`

Return as soon as any Future completes.

### `FIRST_EXCEPTION`

Return when any Future finishes by raising an exception. If no exception occurs, behavior effectively waits until all complete.

Example:

```python
done, not_done = wait(
    futures,
    return_when=FIRST_COMPLETED,
)

for future in done:
    print(future.result())
```

Another:

```python
done, not_done = wait(
    futures,
    return_when=FIRST_EXCEPTION,
)
```

`wait()` is useful when you want a snapshot of completed versus unfinished Futures.

`as_completed()` is generally more convenient when you want to consume results one by one as they finish.

---

# 24. Fail-Fast With `wait()`

A simplified pattern is:

```python
from concurrent.futures import (
    ThreadPoolExecutor,
    wait,
    FIRST_EXCEPTION,
)


def work(item: int) -> str:
    if item == 7:
        raise RuntimeError("critical failure")
    return str(item)


items = range(20)

executor = ThreadPoolExecutor(max_workers=4)

try:
    futures = [
        executor.submit(work, item)
        for item in items
    ]

    done, not_done = wait(
        futures,
        return_when=FIRST_EXCEPTION,
    )

    failed = []

    for future in done:
        exc = future.exception()
        if exc is not None:
            failed.append(exc)

    if failed:
        executor.shutdown(cancel_futures=True)
        raise RuntimeError(
            f"run failed with {len(failed)} observed exception(s)"
        )

    for future in not_done:
        future.result()

finally:
    # In real code, structure shutdown carefully so the desired
    # cancellation/wait policy is explicit.
    pass
```

The exact lifecycle policy should be designed deliberately rather than copied mechanically.

The key idea is:

```text
detect critical failure
        ↓
cancel pending work where possible
        ↓
do not pretend running threads can be killed safely
        ↓
clean up resources
```

---

# 25. Clean Shutdown

The executor context manager is the simplest normal pattern:

```python
with ThreadPoolExecutor(max_workers=8) as executor:
    ...
```

When the block exits, the executor performs normal shutdown behavior and waits for submitted work as part of its normal lifecycle.

For explicit control:

```python
executor.shutdown(wait=True)
```

For pending cancellation:

```python
executor.shutdown(
    wait=True,
    cancel_futures=True,
)
```

The important distinction is:

```text
cancel pending work
        ≠
kill running work
```

`cancel_futures=True` affects futures that have not started running.

Already-running functions are not safely force-killed by the executor.

Therefore a production task should be designed so that running operations have their own reasonable timeouts and resource cleanup.

---

# 26. Choosing `max_workers`

This is a production engineering decision, not a magic constant.

A common mistake is:

```text
CPU count = 16
therefore max_workers = 16
```

For I/O-bound workloads, CPU count is often only one small input to the decision.

The correct worker count is frequently constrained by the external system.

Consider:

```text
API concurrency limit = 20
database pool = 10
object-storage behavior = provider dependent
file descriptors = finite
memory = finite
```

A configuration such as:

```python
ThreadPoolExecutor(max_workers=100)
```

may be technically valid but operationally harmful.

Potential consequences:

- connection-pool contention;
- API throttling;
- HTTP 429 responses;
- increased latency;
- memory growth;
- file-descriptor pressure;
- remote-service overload;
- retries amplifying traffic;
- lower overall throughput.

The practical principle is:

> **Concurrency must be bounded by the narrowest meaningful system constraint.**

---

# 27. Worker Count vs External Capacity

Think in layers:

```text
Thread workers
      ↓
HTTP/client connection capacity
      ↓
provider concurrency/rate limits
      ↓
remote service
```

Or:

```text
Thread workers
      ↓
DB connection pool
      ↓
database
```

Increasing the first layer does not automatically increase the capacity of the layers below it.

Example:

```text
ThreadPoolExecutor = 50
PostgreSQL pool     = 10
```

At most the pool may permit only a limited number of active database operations at once.

The remaining workers can wait for a connection.

That may be useful if the pool and workload are intentionally designed that way, but blindly increasing workers does not create additional database capacity.

---

# 28. Rate Limits Are Concurrency Limits' Cousin

A provider can constrain you in several ways:

```text
requests per second
requests per minute
simultaneous requests
connections
bandwidth
```

These are not interchangeable.

For example:

```text
max concurrent requests = 20
```

does not necessarily mean:

```text
20 requests per second
```

A request may take several seconds.

When selecting `max_workers`, understand the actual provider limits and the behavior of the client.

The engineering target is:

```text
useful throughput
within provider limits
without excessive latency or errors
```

---

# 29. Threads and Connection Pools

Suppose you need to execute 50 independent database queries.

You have:

```text
ThreadPoolExecutor = 50 workers
PostgreSQL pool     = 10 connections
```

You should expect contention around the database connection pool.

The important observation is:

> **More worker threads do not create more database connections.**

If 50 workers all require a connection but only 10 are available, some workers wait.

An experiment should compare:

```text
workers = pool size
workers > pool size
```

and measure:

- total runtime;
- throughput;
- individual latency;
- time waiting for connections;
- pool utilization;
- database load.

The correct configuration depends on the workload and database capacity.

---

# 30. Shared Thread-Safe Resources

Never assume a library object is thread-safe.

Check the library's documentation for the specific object and usage pattern.

Potential resources include:

- HTTP clients;
- sessions;
- database connection pools;
- database connections;
- cursors;
- SDK clients;
- caches;
- mutable application state.

The rule is:

> **Thread safety is a property of a particular implementation and usage pattern, not a property you should guess from the object's name.**

For example, a connection pool may be designed for concurrent use while an individual database cursor may have very different guarantees.

Do not infer:

```text
pool is thread-safe
therefore every connection/cursor returned by it can be shared freely
```

That conclusion does not automatically follow.

---

# 31. Shared Pool vs Per-Thread Resource

Three common designs are:

| Design | Advantages | Risks |
|---|---|---|
| Shared thread-safe pool | Reuses resources efficiently | Requires documented thread-safe behavior |
| One resource per thread | Stronger isolation | More resource consumption |
| Thread-local resource | Convenient per-thread state | Lifecycle and resource-count concerns |

There is no universal winner.

The design depends on the library, resource cost, lifetime, transaction model, and concurrency level.

---

# 32. Per-Thread Resources With `threading.local`

Python provides thread-local storage:

```python
import threading

thread_local = threading.local()


def create_resource():
    # Replace with an appropriate library-specific resource.
    return object()


def get_resource():
    if not hasattr(thread_local, "resource"):
        thread_local.resource = create_resource()

    return thread_local.resource
```

Each thread gets its own `resource` attribute.

Conceptually:

```text
Thread A
    → thread_local.resource = A-resource

Thread B
    → thread_local.resource = B-resource

Thread C
    → thread_local.resource = C-resource
```

This can be useful for per-thread clients, sessions, or state when the library's design makes that appropriate.

But thread-local storage does not solve every lifecycle problem.

You still need to consider:

- how many threads exist;
- how expensive each resource is;
- how resources are closed;
- what happens when the executor shuts down;
- whether the library already provides a safe shared pool.

---

# 33. Avoid Unsafe Shared Mutable State

This is risky:

```python
results = []

def worker(item: int) -> None:
    results.append(process(item))
```

Do not use this pattern merely because it appears convenient.

A safer design is:

```python
def worker(item: int) -> str:
    return process(item)
```

and then:

```python
results = []

for future in as_completed(futures):
    results.append(future.result())
```

Now the worker produces a value and the coordinating thread aggregates it.

This design makes ownership clearer:

```text
worker
   ↓
returns result
   ↓
central aggregation
```

Rather than:

```text
many workers
   ↓
shared mutable object
   ↓
coordination complexity
```

Detailed locks, race conditions, and synchronization primitives belong to the later topic on thread safety and shared state.

---

# 34. Unbounded Task Submission

This pattern looks concise:

```python
futures = [
    executor.submit(process, item)
    for item in million_items
]
```

But if there are one million items, you may create approximately one million Future objects.

That can consume substantial memory.

The crucial distinction is:

```text
worker count
```

versus:

```text
number of submitted tasks
```

They are not the same thing.

You might have:

```text
16 worker threads
+
1,000,000 submitted futures
```

Only a small number are actively running, but the program may still retain a very large amount of task bookkeeping.

---

# 35. Bounded Task Submission

A bounded design keeps only a controlled amount of outstanding work.

One simple approach is batching:

```python
from itertools import islice


def batched(iterable, size):
    iterator = iter(iterable)

    while batch := list(islice(iterator, size)):
        yield batch
```

Then:

```python
from concurrent.futures import ThreadPoolExecutor


def process(item: int) -> str:
    return str(item * 2)


items = range(1_000_000)

with ThreadPoolExecutor(max_workers=16) as executor:
    for batch in batched(items, 1_000):
        futures = [
            executor.submit(process, item)
            for item in batch
        ]

        for future in futures:
            print(future.result())
```

The exact batch size is an engineering parameter.

Larger batches may improve throughput but increase memory and delay failure visibility.

Smaller batches reduce outstanding work but can add coordination overhead.

---

# 36. `Executor.map(..., buffersize=...)`

Recent Python versions provide a `buffersize` option for executor `map()`.

Its purpose is to avoid eagerly having an unbounded amount of mapped work waiting to be yielded.

Conceptually:

```text
large input iterable
       ↓
controlled submission buffer
       ↓
worker pool
       ↓
results consumed by caller
```

A version-aware example:

```python
from concurrent.futures import ThreadPoolExecutor


def process(item: int) -> int:
    return item * 2


items = range(1_000_000)

with ThreadPoolExecutor(max_workers=16) as executor:
    results = executor.map(
        process,
        items,
        buffersize=1_000,
    )

    for result in results:
        consume(result)
```

**Python-version note:** do not assume `buffersize` exists in older Python releases. Check the Python version and the corresponding `Executor.map()` documentation before using it.

The engineering principle matters more than the spelling of the API:

> **Do not let a huge input iterable silently turn into an enormous amount of outstanding executor bookkeeping.**

---

# 37. One Million Task Memory Experiment

A useful experiment compares three approaches.

## Approach A — immediate submission

```python
futures = [
    executor.submit(process, item)
    for item in million_items
]
```

## Approach B — bounded batches

```text
read batch
    ↓
submit batch
    ↓
collect batch
    ↓
release references
    ↓
next batch
```

## Approach C — `map()` with `buffersize`

Use this where the installed Python version supports it.

Measure:

- peak memory;
- total runtime;
- throughput;
- correctness;
- time to first completed result;
- number of outstanding tasks.

The experiment demonstrates a critical idea:

```text
max_workers controls active worker concurrency.

It does NOT automatically bound how many tasks your application may have submitted.
```

---

# 38. Atomic File Writes

Concurrent downloading introduces an output-integrity problem.

Unsafe pattern:

```text
download
    ↓
open(final_path, "wb")
    ↓
write
    ↓
process crashes
    ↓
partial file remains at final_path
```

A downstream process may see the path and incorrectly assume the file is complete.

A safer conceptual pattern is:

```text
download
    ↓
temporary path
    ↓
complete write
    ↓
flush/close
    ↓
atomic rename/replace
    ↓
final path
```

A practical implementation can use `tempfile` and `os.replace()`:

```python
import os
import tempfile
from pathlib import Path


def write_atomically(destination: Path, data: bytes) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        mode="wb",
        dir=destination.parent,
        prefix=f".{destination.name}.",
        delete=False,
    ) as temporary:
        temporary.write(data)
        temporary_path = Path(temporary.name)

    try:
        os.replace(temporary_path, destination)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise
```

The exact durability guarantees depend on the filesystem and workload. The important pipeline property is:

> A completed destination path should represent a complete file rather than an interrupted partial write.

---

# 39. Thread-Aware Logging

Concurrent logs become difficult to interpret if every message looks identical.

Configure the thread name:

```python
import logging


logging.basicConfig(
    format="%(asctime)s %(threadName)s %(levelname)s %(message)s",
    level=logging.INFO,
)
```

Then:

```python
logging.info("starting download")
```

can identify the worker thread in the log output.

Production logs should ideally contain enough context to answer:

```text
Which run?
Which input?
Which worker?
Which operation?
How long?
What happened?
```

Useful fields include:

```text
run_id
item_id
thread_name
operation
duration
status
error
```

For example:

```text
2026-10-02T01:20:01 worker_3 INFO download_started item=object-17
2026-10-02T01:20:02 worker_3 INFO download_finished item=object-17 duration=1.02
```

Thread names are particularly useful during incident investigation.

---

# 40. Daemon Threads

Python threads can be marked daemon:

```python
thread.daemon = True
```

A daemon thread is treated as background work that should not keep the interpreter alive indefinitely.

That sounds convenient, but it is dangerous for critical data-processing work.

If the process exits while daemon work is incomplete:

```text
critical download
      ↓
daemon thread
      ↓
process exits
      ↓
work can be abandoned
```

For a Data Engineering pipeline, abandoned work can mean:

- incomplete downloads;
- missing records;
- incomplete writes;
- skipped cleanup;
- misleading success status.

Rule:

> **Do not rely on daemon threads for critical data processing.**

Use explicit lifecycle management instead.

---

# 41. Executor Shutdown Lifecycle

A production executor should have a clear lifecycle:

```text
start
  ↓
submit work
  ↓
process
  ↓
collect results/errors
  ↓
stop new work
  ↓
wait for running work / cancel pending work as policy requires
  ↓
release resources
  ↓
exit cleanly
```

The context manager handles ordinary shutdown:

```python
with ThreadPoolExecutor(max_workers=8) as executor:
    ...
```

Explicit shutdown is useful when the application needs special failure handling:

```python
executor.shutdown(
    wait=True,
    cancel_futures=True,
)
```

Remember:

```text
pending work → may be cancelled
running work → is not safely force-killed
```

Design the worker operation itself with sensible timeouts and cleanup.

---

# 42. Failure Injection

Concurrency code should be tested under failure, not only success.

Useful injected failures include:

- 5% download failures;
- request timeout;
- connection error;
- malformed response;
- missing object;
- database query failure.

A good test asks:

```text
Does every failure appear in the run report?

Are successful results still available?

Can partial output be mistaken for complete output?

Does the overall run status follow the configured failure policy?
```

For example:

```python
import random


def download(key: str) -> bytes:
    if random.random() < 0.05:
        raise TimeoutError(f"simulated timeout: {key}")

    return f"data-for-{key}".encode()
```

For deterministic tests, prefer a deterministic failure set rather than relying on randomness.

---

# 43. Failure Rate

For a batch:

```python
failure_rate = failed / total
```

Suppose:

```text
total  = 500
failed = 25
```

Then:

```text
failure_rate = 25 / 500
             = 0.05
             = 5%
```

A production pipeline can define a threshold:

```python
if failure_rate > failure_threshold:
    raise RuntimeError("failure-rate threshold exceeded")
```

This is often more useful than simply checking:

```python
if failures:
    fail()
```

because some workloads can tolerate a small amount of recoverable failure while others cannot.

The policy must be explicit and business-appropriate.

---

# 44. Fail-Fast Mode

A downloader can expose:

```python
fail_fast: bool = False
```

### Normal mode

```text
task fails
   ↓
record failure
   ↓
continue independent work
   ↓
produce complete report
```

### Fail-fast mode

```text
critical task fails
   ↓
record failure
   ↓
stop scheduling additional work where possible
   ↓
cancel pending futures
   ↓
allow already-running operations to finish safely
   ↓
shut down
   ↓
return failure status
```

Do not claim that a Python thread pool can safely terminate an arbitrary running thread.

The correct mental model is cooperative lifecycle control, not forced thread termination.

---

# 45. Hands-On Project: Threaded Download Engine

## Goal

Build a production-oriented downloader that can download 500 objects from MinIO and compare sequential execution with multiple thread counts.

Compare:

```text
Sequential
4 workers
16 workers
64 workers
256 workers
```

The core interface should be conceptually:

```python
def download_all(
    keys,
    max_workers,
):
    ...
```

A production version should also expose policy parameters such as:

```python
def download_all(
    keys,
    max_workers,
    *,
    failure_threshold=0.0,
    fail_fast=False,
):
    ...
```

The exact API can be adapted to your MinIO client.

---

# 46. Project Requirements

The implementation must:

1. use `ThreadPoolExecutor`;
2. use `as_completed`;
3. write downloaded files atomically;
4. track successful downloads;
5. track failures;
6. include the original object key with every failure;
7. produce a run report;
8. support a configurable failure-rate threshold;
9. fail the overall run when the threshold is exceeded;
10. support fail-fast mode;
11. verify concurrent results against a sequential baseline;
12. log worker/thread information;
13. measure wall-clock runtime;
14. record throughput;
15. record error count.

A useful result structure is:

```python
from dataclasses import dataclass


@dataclass
class DownloadResult:
    key: str
    destination: str
    success: bool
    error: str | None = None
```

A run report might contain:

```python
{
    "total": 500,
    "successful": 492,
    "failed": 8,
    "failure_rate": 0.016,
    "runtime_seconds": 14.2,
    "throughput_files_per_second": 34.65,
}
```

The actual benchmark values must come from your environment.

---

# 47. A Self-Contained Downloader Skeleton

The following example demonstrates the control flow without assuming a particular MinIO deployment.

```python
from __future__ import annotations

import logging
import os
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable


logging.basicConfig(
    format=(
        "%(asctime)s %(threadName)s "
        "%(levelname)s %(message)s"
    ),
    level=logging.INFO,
)


@dataclass
class DownloadResult:
    key: str
    destination: str
    success: bool
    error: str | None = None


def atomic_write_bytes(
    destination: Path,
    data: bytes,
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)

    temporary_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            delete=False,
        ) as temporary:
            temporary.write(data)
            temporary_path = Path(temporary.name)

        os.replace(temporary_path, destination)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def download_all(
    keys: Iterable[str],
    max_workers: int,
    download_one: Callable[[str], bytes],
    destination_for: Callable[[str], Path],
    *,
    failure_threshold: float = 0.0,
    fail_fast: bool = False,
) -> list[DownloadResult]:

    keys = list(keys)

    results: list[DownloadResult] = []

    with ThreadPoolExecutor(
        max_workers=max_workers,
        thread_name_prefix="download",
    ) as executor:

        future_to_key = {
            executor.submit(download_one, key): key
            for key in keys
        }

        stop_processing = False

        for future in as_completed(future_to_key):
            key = future_to_key[future]

            try:
                data = future.result()
                destination = destination_for(key)

                atomic_write_bytes(destination, data)

            except Exception as exc:
                logging.exception(
                    "download failed key=%s",
                    key,
                )

                results.append(
                    DownloadResult(
                        key=key,
                        destination=str(destination_for(key)),
                        success=False,
                        error=repr(exc),
                    )
                )

                if fail_fast:
                    stop_processing = True

                    # Cancel work that has not started.
                    for pending_future in future_to_key:
                        if pending_future is not future:
                            pending_future.cancel()

                    # The context manager still performs normal cleanup.
                    break

            else:
                logging.info(
                    "download succeeded key=%s",
                    key,
                )

                results.append(
                    DownloadResult(
                        key=key,
                        destination=str(destination),
                        success=True,
                    )
                )

        if stop_processing:
            # The context manager will wait for running work.
            # Do not pretend running threads can be force-killed.
            pass

    total = len(keys)
    failed = sum(not result.success for result in results)

    failure_rate = failed / total if total else 0.0

    if failure_rate > failure_threshold:
        raise RuntimeError(
            f"failure-rate threshold exceeded: "
            f"{failure_rate:.2%} > {failure_threshold:.2%}"
        )

    return results
```

This example demonstrates the architecture, but a production implementation should additionally consider:

- bounded submission for very large key sets;
- client-specific connection pooling;
- request timeouts;
- retries where safe and appropriate;
- checksums or object metadata;
- storage path validation;
- structured logging;
- metrics;
- retry classification;
- graceful cancellation;
- resource cleanup.

Do not add those concerns blindly. Add them according to the requirements of the actual pipeline.

---

# 48. Important Limitation in the Skeleton

The example above submits all keys at once:

```python
future_to_key = {
    executor.submit(download_one, key): key
    for key in keys
}
```

That is acceptable for a small 500-object exercise.

It is not automatically appropriate for millions of objects.

For a large workload, use bounded submission or a supported `map(..., buffersize=...)` strategy.

This distinction is important:

```text
500 tasks
    → simple submission may be fine

1,000,000 tasks
    → design task submission deliberately
```

Do not copy a small-batch pattern into a million-item production job without analyzing memory.

---

# 49. MinIO Benchmark

Run the same 500-object workload with:

```text
1. Sequential
2. 4 threads
3. 16 threads
4. 64 threads
5. 256 threads
```

Record measured values:

| Workers | Runtime | Throughput | Errors | Peak Memory |
|---:|---:|---:|---:|---:|
| 1 | | | | |
| 4 | | | | |
| 16 | | | | |
| 64 | | | | |
| 256 | | | | |

Do not fill this table with invented numbers.

The point of the experiment is to measure your actual environment.

For throughput:

```python
throughput = successful_files / runtime_seconds
```

Also record:

- total errors;
- remote-service throttling;
- connection behavior;
- CPU utilization;
- peak memory.

---

# 50. Interpreting the Worker-Count Curve

A typical conceptual curve is:

```text
runtime
  ^
  |\
  | \
  |  \
  |   \____
  |        \__
  +--------------------> worker count
```

Initially:

```text
more workers
    ↓
more waiting overlapped
    ↓
lower wall time
```

Eventually:

```text
more workers
    ↓
external system saturated
    ↓
contention/throttling/overhead
    ↓
little improvement or worse performance
```

Potential causes of degradation:

- connection exhaustion;
- API throttling;
- server overload;
- network contention;
- memory growth;
- context-switching overhead;
- queue contention;
- increased retry traffic;
- database pool waiting.

The objective is not:

```text
maximum worker count
```

It is:

```text
best useful throughput
within correctness and system constraints
```

---

# 51. Failure-Rate Experiment

Inject approximately 5% failures.

The run should report:

```text
total
successful
failed
failure_rate
```

For example:

```python
failure_rate = failed / total
```

Then apply:

```python
if failure_rate > threshold:
    fail the run
```

A good experiment tests at least:

```text
threshold = 0%
threshold = 1%
threshold = 5%
threshold = 10%
```

Do not assume these thresholds are universally correct. They are experiment parameters.

The engineering question is:

> What failure rate is acceptable for this particular pipeline and why?

---

# 52. Database Connection Pool Exercise

Use 50 independent database queries.

Compare:

```text
max_workers = pool size
```

against:

```text
max_workers > pool size
```

Measure:

- total runtime;
- average query latency;
- tail latency if available;
- connection wait;
- pool utilization;
- database load;
- throughput.

A useful conceptual model is:

```text
ThreadPoolExecutor
        ↓
50 workers
        ↓
PostgreSQL connection pool
        ↓
10 connections
        ↓
database
```

If only 10 connections can actively serve the workload, 50 worker threads do not turn that into 50 simultaneous database connections.

This experiment teaches an important production principle:

> **Concurrency at one layer does not create capacity at another layer.**

---

# 53. One Million Small Tasks

Design an experiment comparing:

```text
Approach A
1,000,000 futures submitted immediately

versus

Approach B
bounded task submission
```

Optionally include:

```text
Approach C
executor.map(..., buffersize=...)
```

where supported.

Measure:

- peak memory;
- runtime;
- throughput;
- time to first useful result;
- correctness.

The most important observation should be:

```text
worker count != task count
```

A pool with 16 workers can still have one million outstanding Future objects if the application submits them all.

---

# 54. Correctness Verification

Every concurrency benchmark must compare output with a known-correct baseline.

Run:

```text
sequential implementation
        ↓
reference result
```

Then:

```text
threaded implementation
        ↓
candidate result
```

Compare them:

```python
assert concurrent_result == sequential_result
```

If output ordering is intentionally unspecified:

```python
assert sorted(concurrent_result) == sorted(sequential_result)
```

The exact comparison should reflect the contract of the pipeline.

The rule is:

> **A faster wrong result is a bug, not an optimization.**

Never report a concurrency improvement without checking correctness.

---

# 55. Simple Speed-Up Model

Suppose:

```text
50 requests
average latency = 200 ms
```

A rough sequential estimate is:

```text
50 × 200 ms
= 10,000 ms
≈ 10 seconds
```

With 10 effective concurrent requests, an idealized estimate is:

```text
50 / 10 = 5 waves

5 × 200 ms
≈ 1 second
```

This is only a model.

Real results differ because of:

- network variability;
- connection setup;
- server processing;
- rate limits;
- client overhead;
- scheduling;
- contention;
- nonuniform request durations.

Never promise a 10× speed-up merely because you use 10 threads.

---

# 56. Common Data Engineering Threading Patterns

## Pattern 1 — Parallel API calls

```text
IDs
 ↓
ThreadPoolExecutor
 ↓
HTTP requests
 ↓
results
```

Suitable when:

- calls are independent;
- the client supports the intended concurrent usage;
- provider limits are respected;
- response handling is bounded.

Watch for:

- rate limits;
- timeouts;
- retries;
- connection limits;
- API ordering requirements.

## Pattern 2 — Parallel object downloads

```text
object keys
 ↓
workers
 ↓
MinIO/S3
 ↓
local files
```

Watch for:

- connection limits;
- disk bandwidth;
- atomic writes;
- duplicate destinations;
- partial files;
- object-not-found failures.

## Pattern 3 — Parallel independent database queries

```text
query/partition identifiers
 ↓
workers
 ↓
connection pool
 ↓
database
```

Watch for:

- pool size;
- database CPU;
- locks;
- query contention;
- server-side limits;
- transaction semantics.

## Pattern 4 — Parallel file processing

```text
file paths
 ↓
workers
 ↓
independent transformations
```

This is suitable when each operation is sufficiently I/O-bound.

If the transformation itself is heavily CPU-bound pure Python, reassess whether threads are appropriate.

For every pattern ask:

1. Is the work actually I/O-bound?
2. Is the work independent?
3. What limits concurrency?
4. What happens when one task fails?
5. How is correctness verified?
6. How are outputs written safely?
7. How will operators observe the run?

---

# 57. Debugging Scenario 1 — Failures Disappear

### Symptom

The program finishes quickly but reports no errors even though 10% of tasks failed.

### Likely cause

The application submitted Futures but never inspected them.

For example:

```python
for item in items:
    executor.submit(fetch, item)
```

The returned Future is discarded.

### How to investigate

Inspect whether every Future is eventually observed through:

```python
future.result()
```

or:

```python
future.exception()
```

### Correct fix

Keep a Future-to-input mapping:

```python
future_to_item = {
    executor.submit(fetch, item): item
    for item in items
}
```

Then consume with `as_completed()`.

### Production prevention

Make "every submitted Future must have an observation path" part of the design review.

---

# 58. Debugging Scenario 2 — 500 Threads Make the API Slower

### Symptom

Increasing workers from 32 to 500 increases total runtime.

### Likely causes

- provider throttling;
- connection contention;
- client-side overhead;
- network saturation;
- server overload;
- retries amplifying traffic.

### Investigation

Measure:

- request latency;
- HTTP status codes;
- 429 responses;
- connection utilization;
- throughput;
- error rate.

### Correct fix

Reduce concurrency to a level supported by the API and client.

### Production prevention

Benchmark a worker-count curve rather than selecting the largest number that runs.

---

# 59. Debugging Scenario 3 — 50 Workers, 10 DB Connections

### Symptom

Many worker threads are blocked waiting for database connections.

### Likely cause

The thread pool is larger than the connection pool.

### Investigation

Measure:

```text
worker count
pool size
connection wait
query latency
throughput
```

### Correct fix

Align concurrency with database capacity rather than assuming more workers help.

### Production prevention

Treat the connection pool as a first-class constraint during concurrency design.

---

# 60. Debugging Scenario 4 — Memory Explodes

### Symptom

Memory grows dramatically when processing one million tasks.

### Likely cause

One million Futures were created and retained.

### Investigation

Look at task count versus worker count.

```text
16 workers
+
1,000,000 Futures
```

is still a million-object bookkeeping problem.

### Correct fix

Use bounded submission or `map(..., buffersize=...)` where supported.

### Production prevention

Always ask:

> How many tasks can be outstanding at once?

---

# 61. Debugging Scenario 5 — Partial Downloaded File

### Symptom

A file exists but is incomplete.

### Likely cause

The worker wrote directly to the final destination and was interrupted.

### Investigation

Compare file size/checksum with expected metadata.

### Correct fix

Write to a temporary path and atomically replace the final path only after a successful complete write.

### Production prevention

Make atomic output part of the downloader contract.

---

# 62. Debugging Scenario 6 — Program Exits Too Early

### Symptom

Not all downloads finish.

### Likely causes

- threads were started without an appropriate completion boundary;
- lifecycle management was incorrect;
- daemon threads were used for critical work.

### Correct fix

Use:

```python
thread.join()
```

for manually managed threads or an executor context manager for a thread pool.

### Production prevention

Make completion and shutdown explicit.

---

# 63. Debugging Scenario 7 — Logs Cannot Identify Failures

### Symptom

Logs contain:

```text
download failed
download failed
download failed
```

but no useful identity.

### Likely cause

The logs do not include input or worker context.

### Correct fix

Include:

```text
run_id
item_id
thread_name
operation
error
```

### Production prevention

Use thread-aware structured logging from the beginning.

---

# 64. Debugging Scenario 8 — `future.result()` Raises Unexpectedly

### Symptom

The main thread receives an exception when calling:

```python
future.result()
```

### Explanation

The worker raised an exception.

`Future.result()` re-raises that worker exception in the caller.

### Correct handling

```python
try:
    result = future.result()
except Exception as exc:
    record_failure(exc)
```

Do not treat this behavior as an executor bug.

It is the mechanism by which worker failures become observable.

---

# 65. Debugging Scenario 9 — `map()` Delays Fast Results

### Symptom

A fast task appears not to be processed even though it completed.

### Likely cause

The consumer is waiting for an earlier input's result because `map()` yields results in input order.

### Correct fix

Use `as_completed()` when completion-order processing is required.

### Production prevention

Choose result-collection semantics intentionally.

---

# 66. Debugging Scenario 10 — Daemon Thread Loses Work

### Symptom

The process exits and background work is incomplete.

### Likely cause

Critical work was assigned to daemon threads.

### Correct fix

Use explicit lifecycle management and non-daemon worker behavior for critical processing.

### Production prevention

Treat all critical data movement as work that must have a defined completion and shutdown policy.

---

# 67. Common Beginner Mistakes

## Mistake 1 — One thread per tiny task

Creating thousands of ad hoc threads adds lifecycle and resource overhead.

Use a pool when the workload is naturally a collection of tasks.

## Mistake 2 — Threads for CPU-bound Python

Do not assume threads create CPU parallelism for pure Python under standard CPython.

## Mistake 3 — Ignoring Futures

If you submit work and discard the Future, worker exceptions can disappear from your control flow.

## Mistake 4 — Never calling `result()`

If you need reliable error reporting, inspect outcomes.

## Mistake 5 — Assuming exceptions automatically fail the main program

Worker exceptions are associated with their Futures.

## Mistake 6 — Too many workers

More concurrency can cause throttling and contention.

## Mistake 7 — Ignoring external limits

The API, database, connection pool, network, storage service, and OS can all impose constraints.

## Mistake 8 — Submitting millions of Futures

Task count and worker count are different.

## Mistake 9 — Sharing non-thread-safe objects

Read the library documentation.

## Mistake 10 — Writing directly to final files

Use atomic output where partial files would be harmful.

## Mistake 11 — Daemon threads for critical work

Critical data work needs explicit lifecycle management.

## Mistake 12 — Measuring only runtime

Also measure correctness, throughput, errors, memory, CPU, and external-system behavior.

## Mistake 13 — Assuming more workers always means more speed

Benchmark the curve.

---

# 68. Production Checklist

## Workload

- [ ] Classified as I/O-bound.
- [ ] Sequential baseline exists.
- [ ] Expected speed-up has been estimated.
- [ ] Independent tasks have been identified.

## Executor

- [ ] `ThreadPoolExecutor` is appropriate.
- [ ] `max_workers` is explicitly chosen.
- [ ] Worker count respects external limits.
- [ ] Executor shuts down cleanly.

## Futures

- [ ] Every submitted Future has an observation path.
- [ ] Exceptions are collected.
- [ ] Fail-fast behavior is explicit if required.
- [ ] Pending work can be cancelled where appropriate.

## Resources

- [ ] HTTP/client thread safety has been verified from documentation.
- [ ] Database pool size is aligned with worker concurrency.
- [ ] Shared mutable state is minimized.
- [ ] Per-thread resources are used only when appropriate.
- [ ] `threading.local` is used deliberately rather than automatically.

## Memory

- [ ] Task submission is bounded for large inputs.
- [ ] Million-Future patterns are avoided.
- [ ] `buffersize` is considered where the Python version supports it.
- [ ] Outstanding-task count is understood.

## Output

- [ ] Files are written atomically where required.
- [ ] Partial output cannot be mistaken for complete output.
- [ ] Duplicate destinations are handled.

## Observability

- [ ] Thread names are logged.
- [ ] Input IDs are logged.
- [ ] Runtime is measured.
- [ ] Success count is measured.
- [ ] Failure count is measured.
- [ ] Failure rate is measured.
- [ ] Throughput is measured.
- [ ] External throttling/errors are visible.

## Correctness

- [ ] Concurrent output matches the sequential baseline.
- [ ] Every failure is visible.
- [ ] Failure threshold is defined.
- [ ] Shutdown behavior is tested.
- [ ] Partial failures cannot silently become success.

---

# 69. Interview Questions and Model Answers

## Basic

### 1. What is a thread?

A thread is an execution path within a process. Threads in the same process share process memory and can make progress independently.

### 2. What does `threading.Thread` provide?

It provides a low-level Python abstraction for starting and managing a thread that executes a target callable.

### 3. What does `start()` do?

It starts the thread's concurrent execution.

### 4. What does `join()` do?

It waits for a thread to finish.

### 5. What is `ThreadPoolExecutor`?

It is a high-level executor that manages a pool of worker threads and lets an application submit callable tasks without manually managing every worker thread.

### 6. What is a Future?

A Future represents submitted work whose result or exception may not yet be available.

---

## Intermediate

### 7. Why do threads help I/O-bound workloads?

I/O-bound operations spend time waiting on external systems. While one thread is waiting, another thread can make progress, allowing waiting periods to overlap.

### 8. How are threads related to the GIL?

In standard CPython, the GIL means only one thread executes Python bytecode at a time. Threads can still be effective for I/O because a thread waiting on I/O does not need to continuously execute Python bytecode.

### 9. What is the difference between `map()` and `as_completed()`?

`map()` produces results in input order. `as_completed()` yields Futures in completion order, allowing fast tasks to be processed immediately and enabling flexible per-task error handling.

### 10. How are worker exceptions handled?

Worker exceptions are associated with their Futures. Calling `future.result()` re-raises the exception in the caller.

### 11. Why might I use more workers than CPU cores?

For I/O-bound workloads, workers spend substantial time waiting, so the number of useful concurrent I/O operations can exceed the number of CPU cores.

### 12. What happens if the thread pool is larger than a database connection pool?

Some workers may wait for available connections. Additional workers do not create additional database capacity.

### 13. Why is unbounded submission dangerous?

Submitting huge numbers of tasks can create large numbers of Future objects and consume substantial memory even when only a small number of workers are active.

---

## Advanced

### 14. How would you design a 100,000-file downloader?

I would first establish a sequential baseline, classify the workload as I/O-bound, determine object-storage and client limits, choose bounded worker concurrency, avoid creating 100,000 Futures at once, use `as_completed()` for result collection, write atomically, capture every failure with its object key, expose failure policy, log metrics, and verify concurrent results against a sequential/reference result.

### 15. How would you select `max_workers`?

I would measure the workload and identify external constraints: API concurrency/rate limits, HTTP connection capacity, database pool size, storage behavior, file descriptors, memory, network bandwidth, and remote latency. I would benchmark several values and choose the point that provides useful throughput without excessive errors or resource contention.

### 16. How would you prevent memory blow-up?

I would bound the number of outstanding tasks using batches, a controlled producer/consumer design, or `Executor.map(..., buffersize=...)` where supported.

### 17. How would you implement fail-fast behavior?

I would detect critical exceptions, record the failure, stop scheduling additional work where possible, cancel pending Futures, allow already-running operations to finish safely, shut down cleanly, and mark the overall run as failed.

### 18. How would you handle partial output?

I would write to a temporary path and atomically rename/replace the final destination only after the complete write succeeds.

### 19. How would you handle thread-safe resource sharing?

I would verify the library's documented thread-safety guarantees. If a shared pool/client is designed for concurrent use, I would use it within those guarantees. If a resource must be isolated per worker, I would consider per-thread resources or `threading.local`, while accounting for lifecycle and resource costs.

---

## Senior Architecture

### 20. When would you choose threads instead of another concurrency model?

For this topic's scope, threads are a strong fit when work is primarily I/O-bound, operations are independent, and the client libraries work well with threads. The decision should also account for provider limits, required concurrency, observability, complexity, and the capabilities of the chosen libraries.

### 21. How would you design a threaded API extractor under provider limits?

I would define the provider's rate and concurrency limits, configure bounded worker concurrency, use a thread-safe or appropriately isolated client, use request timeouts, classify errors, avoid retry storms, collect every Future outcome, log request identity and duration, and benchmark throughput while monitoring provider responses.

### 22. How would you coordinate a thread pool with a database connection pool?

I would treat the connection pool as a downstream capacity constraint. I would benchmark worker counts around the pool size, measure connection wait and database load, and avoid assuming that additional workers increase database throughput.

### 23. How would you prove threading improved a pipeline?

I would preserve a correct sequential baseline, run the concurrent version under equivalent conditions, verify outputs are equivalent, and compare wall-clock time, throughput, memory, CPU, error rate, and external-system behavior.

### 24. How would you detect that increased concurrency is hurting performance?

I would look for a flattening or worsening throughput curve, rising latency, more 429s/timeouts, connection-pool waits, higher memory, higher CPU overhead, or increased failure/retry rates.

### 25. How would you design failure handling for millions of independent tasks?

I would avoid creating millions of Futures at once, use bounded task submission, associate each Future with its input identity, collect successes and failures, define retry/failure policies, support cancellation for pending work, produce a durable run report, and make the overall success criterion explicit.

### 26. What evidence would make you choose sequential execution instead?

If the workload is small, external systems are already saturated, concurrency produces no material speed-up, correctness becomes substantially more complex, or operational limits make parallel execution counterproductive, a sequential implementation may be the better engineering choice.

---

# 70. Final Knowledge Check

## Concept Questions

1. Why can five one-second I/O waits potentially complete in roughly one second of wall time when performed concurrently?
2. Why does the GIL not make threads useless for I/O-bound workloads?
3. What is the difference between a worker and a Future?
4. Why is `start()` different from `run()`?
5. Why is `join()` necessary for manually managed critical work?
6. Why does `map()` preserve input ordering?
7. Why is `as_completed()` useful for variable-duration tasks?
8. Why do worker exceptions need explicit observation?
9. What is the difference between cancelling a pending Future and stopping running work?
10. Why can the correct `max_workers` be larger than CPU count?

## Code-Reading Questions

Consider:

```python
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(fetch, item)
        for item in items
    ]

    for future in futures:
        print(future.result())
```

Answer:

1. How many worker threads are available?
2. Does `submit()` block until the task finishes?
3. In what order are results consumed?
4. What happens if one worker raises?
5. What happens to the other submitted tasks?
6. Why might `as_completed()` be preferable?

## Debugging Questions

1. Why could a program report success even though worker tasks failed?
2. Why could 256 workers be slower than 64?
3. Why could a 50-worker pool spend most of its time waiting for 10 database connections?
4. Why could one million submitted tasks consume too much memory?
5. Why can a final file path contain partial data after a failed download?
6. Why can a daemon thread lose critical work?
7. Why are thread names useful during incidents?

## Performance Questions

1. What should be measured besides wall-clock time?
2. What does a plateau in the worker-count curve mean?
3. What could cause performance to degrade as workers increase?
4. Why is a benchmark incomplete without correctness verification?
5. Why should provider throttling be included in benchmark analysis?

## Architecture Questions

1. Design a 500-object downloader.
2. Design a 100,000-object downloader without creating 100,000 Futures at once.
3. Design a 50-query database extraction using a 10-connection pool.
4. Design a fail-fast extraction mode.
5. Design a collect-all extraction mode.
6. Design observability for a threaded ingestion job.
7. Define a failure-rate threshold policy.
8. Explain when you would intentionally choose sequential execution.

## Production Trade-Off Questions

For each scenario, explain the trade-off:

### Scenario A

```text
API limit = 20 concurrent requests
workers = 100
```

### Scenario B

```text
DB pool = 10
workers = 10
```

### Scenario C

```text
DB pool = 10
workers = 50
```

### Scenario D

```text
1,000,000 tasks
workers = 16
all futures submitted immediately
```

### Scenario E

```text
500 downloads
workers = 1, 4, 16, 64, 256
```

Your answer should address:

```text
throughput
latency
memory
external limits
errors
correctness
operational complexity
```

---

# 71. Important Distinctions

Keep these distinctions clear:

```text
Thread
    vs
Process
```

```text
Concurrency
    vs
Parallelism
```

```text
I/O-bound
    vs
CPU-bound
```

```text
Thread
    vs
ThreadPoolExecutor
```

```text
Future
    vs
future.result()
```

```text
map()
    vs
as_completed()
```

```text
Concurrency
    vs
Rate limit
```

```text
Worker count
    vs
Task count
```

```text
Cancel pending work
    vs
Stop running work
```

```text
Shared resource
    vs
Thread-local resource
```

```text
Fast execution
    vs
Correct execution
```

A production engineer must reason about all of these independently.

---

# 72. Threading Limitations

Threads are not the universal concurrency solution.

Reconsider this approach when:

- work is CPU-bound pure Python;
- concurrency is extremely high and the libraries are designed around asynchronous I/O;
- work must exceed one machine;
- the database is already the bottleneck;
- the API is already rate-limited;
- shared-state requirements make correctness difficult;
- the threading model adds complexity without meaningful performance improvement.

Later topics cover other concurrency mechanisms in more depth.

This chapter intentionally does not turn into a full lesson on:

- multiprocessing;
- `ProcessPoolExecutor`;
- `asyncio`;
- `TaskGroup`;
- async HTTP extraction;
- semaphores;
- queues;
- detailed race conditions;
- locks;
- GIL/free-threaded Python;
- distributed computing.

The boundary is intentional.

---

# 73. Production Design Principles

Throughout this chapter, reinforce these principles:

1. Start with a sequential baseline.
2. Classify the workload.
3. Use threads primarily for I/O-bound work.
4. Bound concurrency.
5. Respect external limits.
6. Never lose worker exceptions.
7. Keep resource sharing explicit.
8. Avoid unbounded task submission.
9. Write outputs safely.
10. Shut down cleanly.
11. Measure the result.
12. Prove the concurrent output matches the baseline.

These principles are more important than memorizing executor syntax.

---

# 74. A Production Review Framework

Before approving a threaded Data Engineering job, ask:

## Workload

```text
What is waiting?
How much of the runtime is I/O?
Are tasks independent?
```

## Capacity

```text
What limits concurrency?
API?
Database?
Connection pool?
Storage?
Network?
Memory?
File descriptors?
```

## Executor

```text
Why this worker count?
What happens if it doubles?
What happens if it is cut in half?
```

## Task submission

```text
How many Futures can exist simultaneously?
Can the input be millions of records?
Is submission bounded?
```

## Failure

```text
Where do exceptions go?
Can every failure be identified?
What is retryable?
What is fatal?
What is fail-fast?
What is collect-all?
```

## Output

```text
Can partial output look complete?
Are writes atomic?
Can two workers target the same destination?
```

## Resources

```text
Is the client thread-safe?
Is the pool thread-safe?
Are connections/cursors shareable?
Should resources be thread-local?
```

## Observability

```text
Can we identify the input?
The thread?
The operation?
The duration?
The error?
The run?
```

## Correctness

```text
Does concurrent output match the sequential/reference result?
```

## Performance

```text
What is the measured speed-up?
Where does scaling plateau?
What becomes the bottleneck?
```

---

# 75. Final Mental Model

The complete process should become:

```text
Sequential baseline
        ↓
Classify workload
        ↓
Confirm I/O-bound
        ↓
Choose ThreadPoolExecutor
        ↓
Set bounded max_workers
        ↓
Submit work
        ↓
Track Futures
        ↓
Collect every result/error
        ↓
Write outputs safely
        ↓
Measure throughput
        ↓
Compare against baseline
        ↓
Tune within external limits
        ↓
Shutdown cleanly
```

Each stage has a purpose.

### 1. Sequential baseline

You need a known-correct reference.

### 2. Classify workload

Concurrency is not automatically appropriate.

### 3. Confirm I/O-bound

Threads are particularly useful when work spends substantial time waiting.

### 4. Choose `ThreadPoolExecutor`

The executor provides reusable worker management and a Future-based interface.

### 5. Set bounded `max_workers`

The number should reflect the actual system constraints.

### 6. Submit work

Submit independent operations to the executor.

### 7. Track Futures

Every important unit of work needs an observable outcome.

### 8. Collect every result/error

Never allow failures to disappear silently.

### 9. Write outputs safely

Use atomic output when partial files would be harmful.

### 10. Measure throughput

Measure actual performance rather than assuming concurrency helped.

### 11. Compare against baseline

Verify that the faster implementation produces the correct result.

### 12. Tune within external limits

Optimize within API, database, storage, network, memory, and operational constraints.

### 13. Shut down cleanly

The job is not complete until resources and worker lifecycle are handled correctly.

---

# 76. Final Production Mental Model in One Sentence

> **Use threads to overlap independent I/O waits, use `ThreadPoolExecutor` to manage bounded worker concurrency, observe every Future, respect downstream capacity, control memory, write outputs safely, handle failures explicitly, and prove the result is both faster and correct.**

---

# 77. Final Checkpoint

You are ready to move beyond this topic when you can explain, without memorizing a recipe:

1. why a thread can help an API downloader;
2. why the same reasoning does not automatically make CPU-heavy pure-Python code faster;
3. why `ThreadPoolExecutor` is preferable to manually creating one thread for every ordinary task;
4. what a Future represents;
5. why `future.result()` matters;
6. why `as_completed()` is useful;
7. when `map()` is simpler;
8. how to collect every worker exception;
9. how to implement collect-all versus fail-fast behavior;
10. what `FIRST_COMPLETED` and `FIRST_EXCEPTION` mean;
11. what `shutdown(cancel_futures=True)` can and cannot do;
12. how to choose `max_workers`;
13. why a database pool constrains useful database concurrency;
14. why API rate limits constrain useful API concurrency;
15. why thread-safe resources and per-thread resources are different designs;
16. how `threading.local` works at a conceptual level;
17. why one million Futures can be a memory problem;
18. how bounded submission solves that class of problem;
19. when `buffersize` is useful and why Python-version awareness matters;
20. why daemon threads are inappropriate for critical data movement;
21. how thread-aware logging helps incident response;
22. why atomic file writes matter;
23. how to benchmark 500 MinIO downloads with 1, 4, 16, 64, and 256 workers;
24. how to inject 5% failures and apply a failure threshold;
25. how to compare 50 database queries against a connection-pool limit;
26. how to compare one million immediate submissions with bounded submission;
27. how to verify concurrent results against a sequential baseline;
28. how to recognize a concurrency configuration that is hurting rather than helping.

If you can answer those questions and complete the hands-on experiments with measured evidence, you have moved from knowing Python thread syntax to reasoning about threaded I/O as a production Data Engineering mechanism.

---

# 78. Topic Summary

The essential progression is:

```text
threading.Thread
    ↓
start()
    ↓
join()
    ↓
understand I/O waiting
    ↓
ThreadPoolExecutor
    ↓
submit()
    ↓
Future
    ↓
result()
    ↓
map()
    ↓
as_completed()
    ↓
exception handling
    ↓
wait()
    ↓
fail-fast / collect-all
    ↓
clean shutdown
    ↓
bounded max_workers
    ↓
external limits
    ↓
connection pools
    ↓
thread-safe/shared resources
    ↓
thread-local resources
    ↓
bounded task submission
    ↓
buffersize
    ↓
atomic output
    ↓
thread-aware logging
    ↓
benchmarking
    ↓
correctness verification
    ↓
production design
```

The deepest lesson is not an API call.

It is a way of thinking:

```text
Workload
   +
External capacity
   +
Bounded concurrency
   +
Observable failures
   +
Controlled memory
   +
Safe output
   +
Measured performance
   +
Verified correctness
```

That is what turns threading from a syntax exercise into a production Data Engineering capability.
