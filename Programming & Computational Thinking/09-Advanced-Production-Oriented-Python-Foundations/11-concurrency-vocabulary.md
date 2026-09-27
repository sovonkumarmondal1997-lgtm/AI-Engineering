# Python Concurrency Vocabulary

> **Stage 1 → Programming & Computational Thinking → 09-Advanced-Production-Oriented-Python-Foundations**
>
> **Purpose:** Build the vocabulary and mental model required to reason about concurrency before moving into deeper concurrent programming, distributed systems, backend engineering, data engineering, ML systems, and AI infrastructure.

## How to Use This Chapter

This chapter deliberately moves from **BEGINNER → INTERMEDIATE → ADVANCED → PRODUCTION-ORIENTED**.

For each major idea, follow this sequence:

1. understand the problem;
2. learn the vocabulary;
3. build a simple mental model;
4. see a small Python example;
5. understand runtime behavior;
6. examine trade-offs;
7. connect the idea to real systems;
8. practice with exercises and debugging;
9. apply the concept to Applied AI Engineering.

This is **not** a complete advanced concurrency course. The goal is to understand the vocabulary, mechanics, trade-offs, and model-selection decisions well enough to continue into deeper concurrency and distributed-systems topics.

> **Version note:** Examples in this chapter are written for modern CPython/Python 3.14-era APIs. Some behavior is implementation-specific or version-sensitive and is labeled as such. Standard Python language semantics should not be confused with CPython implementation details.

## 1. Why Concurrency Matters

Modern software spends a large amount of time waiting.

A backend service may wait for:

- a database;
- an HTTP API;
- object storage;
- a file;
- a DNS lookup;
- a message queue;
- a model endpoint;
- an embedding API;
- a vector database.

Consider:

```text
Request
  ↓
Call database
  ↓
Call external API
  ↓
Read file
  ↓
Call LLM
  ↓
Return response
```

If these operations are independent and mostly involve waiting, a sequential program may spend much of its time doing nothing useful on the CPU.

### Sequential mental model

```text
A ────────→ done
            ↓
B ────────→ done
            ↓
C ────────→ done
            ↓
D ────────→ done
```

### Concurrent mental model

```text
A ────────┐
B ────────┼────→ results
C ────────┤
D ────────┘
```

The concurrent design does **not** necessarily execute A, B, C, and D at the same instant. It means their waiting periods can overlap and the system can make progress on another task while one task is waiting.

### Why this matters operationally

Concurrency can improve:

- **latency** — how long one request takes to complete;
- **throughput** — how much work completes per unit of time;
- **utilization** — how effectively available resources are kept busy;
- **responsiveness** — how quickly a service can continue doing useful work;
- **resource overlap** — especially when work alternates between computation and I/O.

But concurrency also introduces costs:

- more complicated control flow;
- shared-state bugs;
- cancellation complexity;
- rate-limit pressure;
- queue growth;
- memory pressure;
- synchronization overhead;
- harder debugging.

The engineering objective is therefore not **maximum concurrency**. It is **appropriate concurrency for the workload and constraints**.

# PART I — FOUNDATIONAL VOCABULARY

## 2. What Is Concurrency?

In simple language:

> **Concurrency is managing multiple tasks whose execution can overlap in time.**

Imagine one person cooking three dishes. The person may:

1. start boiling water;
2. while the water heats, chop vegetables;
3. while vegetables cook, check the oven;
4. return to the pot when it is ready.

Only one pair of hands may be actively doing one physical action at a time, yet multiple activities are in progress.

That is a useful intuition for concurrency.

### What concurrency does not mean

Concurrency does not automatically mean:

- two CPU cores;
- simultaneous machine instructions;
- faster CPU computation;
- parallel execution.

A single-threaded event loop can achieve useful concurrency for I/O-bound tasks.

### Runtime view

Think of a scheduler managing work:

```text
Task A → waiting for network
Task B → ready to run
Task C → waiting for database

Scheduler:
    run B
    check A
    run another ready task
    resume A when its I/O is ready
```

The scheduler may be an event loop, an operating system, a thread pool, or another execution system.

### Where engineers encounter concurrency

- web servers;
- API clients;
- workers;
- message consumers;
- ETL pipelines;
- asynchronous applications;
- model-serving infrastructure;
- agent orchestration;
- background jobs.

---

## 3. What Is Parallelism?

**Parallelism** means independent work is actually executing at the same time using multiple execution resources.

A simple picture is:

```text
CPU Core 1 → Task A
CPU Core 2 → Task B
```

If both cores execute useful instructions simultaneously, the work is parallel.

### Concurrency versus parallelism

| Concept | Meaning | Typical goal |
|---|---|---|
| Sequential execution | One flow of work at a time | Simplicity / predictability |
| Concurrency | Multiple tasks can make progress during overlapping periods | Responsiveness / throughput |
| Parallelism | Multiple computations execute simultaneously | Reduce computation time / increase throughput |

These models can coexist.

For example, a service may:

- use an event loop for concurrent network requests;
- use a process pool for CPU-heavy preprocessing;
- use a GPU for parallel numerical computation.

### Key rule

> **Concurrency is about structure and progress. Parallelism is about simultaneous execution.**

---

## 4. Concurrency vs Parallelism vs Sequential Execution

### Sequential

```text
A → B → C
```

A must finish before B starts, and B must finish before C starts.

### Concurrent

```text
A ───┐
B ───┼──→ completion
C ───┘
```

A, B, and C can overlap in time.

### Parallel

```text
Core 1: A
Core 2: B
Core 3: C
```

The work executes simultaneously on distinct execution resources.

### Real systems combine models

A production AI service can look like:

```text
Incoming requests
       ↓
Async web server
       ↓
Concurrent I/O
       ↓
Bounded worker pool
       ↓
CPU preprocessing
       ↓
GPU inference
```

Different layers may use different forms of concurrency and parallelism.

### Why the distinction matters

Calling something "parallel" when it is only concurrent can lead to a bad design decision.

For example:

- ten asynchronous HTTP requests can overlap waiting;
- that does not mean ten Python CPU computations are executing simultaneously.

The correct question is always:

> **What resource is doing the work, and what is the workload waiting for?**

# PART II — WORKLOAD TYPES

## 5. Synchronous vs Asynchronous

### Synchronous

A synchronous operation is normally expressed as:

```text
start → wait → finish → next
```

Example:

```python
def fetch_report():
    response = do_network_call()
    return response
```

When `do_network_call()` blocks, the current execution flow waits.

### Asynchronous

An asynchronous operation can be expressed as:

```text
start → suspend while waiting → resume when ready
```

Example:

```python
async def fetch_report():
    response = await do_async_network_call()
    return response
```

The key point is not the word "async". The important point is **what happens during the wait**.

### Asynchronous does not mean parallel

An event loop can have one thread and still manage many I/O-bound tasks concurrently.

```text
Task A → waiting for socket
Task B → running
Task C → waiting for database
Task D → ready
```

The event loop can resume a task when its awaited operation can make progress.

---

## 6. Blocking vs Non-Blocking

### Blocking

A blocking call keeps the executing thread waiting until the operation completes.

```python
import time

time.sleep(1)
```

During the sleep, that thread does not continue executing the next statement.

### Non-blocking or cooperatively suspending

In asyncio code:

```python
import asyncio

await asyncio.sleep(1)
```

The current coroutine is suspended, allowing the event loop to run other ready tasks.

### Important nuance

"Non-blocking" is context-dependent. A library may expose asynchronous APIs that allow the event loop to keep making progress, while a synchronous library may block the thread.

### Common production bug

```python
async def handler():
    time.sleep(5)  # blocks the event-loop thread
    return "done"
```

Usually the intent is:

```python
async def handler():
    await asyncio.sleep(5)
    return "done"
```

A real CPU-heavy synchronous function can also stall an event loop even if it does not call `sleep()`.

---

## 7. I/O-Bound vs CPU-Bound

Before selecting a concurrency model, classify the workload.

### I/O-bound

An I/O-bound workload spends a significant portion of its time waiting for external resources.

Examples:

- HTTP requests;
- database queries;
- file reads;
- object storage;
- DNS/network operations;
- external LLM APIs.

### CPU-bound

A CPU-bound workload spends most of its time doing computation.

Examples:

- CPU-heavy parsing;
- compression;
- image transforms;
- large pure-Python numerical loops;
- expensive feature transformations.

### Mixed workload

Many production workloads are mixed:

```text
Read → CPU transform → HTTP → CPU transform → database
```

This is why architecture decisions must be based on measurement rather than a slogan such as "always use async."

| Workload | Main bottleneck | Candidate approaches |
|---|---|---|
| I/O-bound | Waiting | asyncio / threads |
| CPU-bound | Computation | processes / process pool / native parallelism |
| Mixed | Depends on stage | Combine models |

# PART III — PROGRAM EXECUTION VOCABULARY

## 8. Process

A **process** is an operating-system execution environment with its own process identity and memory resources.

In Python:

```python
import os

print(os.getpid())
```

The output is a process identifier (PID).

### Mental model

```text
Operating System
│
├── Process 1001
│   └── Python program
│
├── Process 1002
│   └── Python program
│
└── Process 1003
    └── Python program
```

Processes generally have separate memory spaces.

That gives process-based designs stronger isolation than threads, but process communication requires explicit mechanisms and can involve serialization and copying.

### When processes are useful

- CPU-heavy workloads;
- isolation;
- independent worker failures;
- process-level scaling;
- avoiding traditional CPython GIL limitations for Python-level CPU work.

### Costs

- process startup;
- memory overhead;
- inter-process communication;
- serialization/pickling;
- platform-specific startup behavior.

---

## 9. Thread

A **thread** is an execution flow inside a process.

Threads in the same process normally share the process's memory.

```text
Process
├── Thread A
├── Thread B
└── Thread C
```

Example:

```python
import threading

print(threading.current_thread())
```

A real thread:

```python
import threading

def worker():
    print("worker running")

thread = threading.Thread(target=worker)
thread.start()
thread.join()
```

### Why threads are useful

Threads can be a practical model for I/O-bound synchronous libraries:

```text
Thread A → waiting for HTTP
Thread B → processing response
Thread C → waiting for database
```

### Why shared memory matters

A thread can directly access an object created by another thread.

That is convenient, but shared mutable state introduces synchronization requirements.

---

## 10. Task

The word **task** is broader than "thread" or "process."

It can mean an item of work at the application level.

In asyncio, an `asyncio.Task` is a wrapper around a coroutine that schedules that coroutine for execution by the event loop.

```text
coroutine object
      ↓
asyncio.Task
      ↓
event loop schedules it
```

Do not assume every library uses "task" in exactly the same way. Always check the framework's definition.

---

## 11. Coroutine

A **coroutine function** is defined with `async def`.

```python
async def fetch_data():
    return "data"
```

Calling the function:

```python
coro = fetch_data()
```

creates a **coroutine object**. It does not mean the coroutine has completed.

You can think of the relationship as:

```text
async def function
       ↓
coroutine function

call it
       ↓
coroutine object

schedule/await it
       ↓
execution progresses
```

A coroutine normally progresses at `await` points.

Example:

```python
import asyncio

async def fetch_data():
    await asyncio.sleep(0.1)
    return "data"

async def main():
    result = await fetch_data()
    print(result)

asyncio.run(main())
```

### Important distinction

A coroutine is **not automatically a Task**.

You can directly `await` a coroutine, or schedule it with `asyncio.create_task()`.

---

## 12. Awaitable

An **awaitable** is an object that can be used with `await`.

The major categories include:

- coroutine objects;
- `asyncio.Task`;
- `asyncio.Future`;
- objects implementing `__await__`.

Conceptually:

```text
awaitable
   ↓
await
   ↓
current coroutine suspends
   ↓
event loop can run other work
```

Do not interpret `await` as "pause the whole Python program." It suspends the current coroutine while the surrounding execution system can continue making progress.

---

## 13. Callable, Worker, and Unit of Work

Concurrency systems often manipulate **callables**:

```python
def process(item):
    return item * 2
```

A callable can be:

- a function;
- a bound method;
- a callable object;
- in some APIs, a partial function.

Executor APIs accept callables as work units:

```python
future = executor.submit(process, 10)
```

This separation is useful:

```text
WHAT work?
    ↓
callable

HOW is work executed?
    ↓
thread / process / event-loop task
```

That distinction is foundational to `concurrent.futures`.

# PART IV — THE EVENT LOOP

## 14. Event Loop

The **event loop** is the coordination mechanism at the heart of asyncio.

Its job is approximately:

1. identify ready work;
2. resume a coroutine;
3. let the coroutine run until it completes, returns, or reaches an await point;
4. monitor asynchronous I/O and timers;
5. resume tasks when their awaited operations become ready.

### Mental model

```text
                 ┌──────────────────┐
                 │    Event Loop    │
                 └────────┬─────────┘
                          │
             ┌────────────┼─────────────┐
             ↓            ↓             ↓
          Task A        Task B        Task C
             │            │             │
          waiting       ready         waiting
             │            │
             └──── I/O/timer readiness
```

The event loop is a scheduler/coordinator. It does not magically create CPU parallelism.

### A small example

```python
import asyncio

async def work(name, delay):
    await asyncio.sleep(delay)
    print(f"{name} done")

async def main():
    await asyncio.gather(
        work("A", 0.2),
        work("B", 0.1),
    )

asyncio.run(main())
```

Both coroutines can make progress during overlapping periods.

---

## 15. `asyncio.run()`

`asyncio.run(coro())` is a common top-level entry point for running an asynchronous program.

```python
import asyncio

async def main():
    print("hello")

asyncio.run(main())
```

Conceptually:

```text
create/manage event-loop execution
        ↓
run main coroutine
        ↓
clean up loop-related resources
        ↓
return result / propagate error
```

### Practical rule

Use `asyncio.run()` as an application entry point rather than wrapping every individual async operation in its own call.

Inside an already-running event loop, calling `asyncio.run()` is generally the wrong model.

---

## 16. `async` and `await`

`async def` defines a coroutine function:

```python
async def main():
    ...
```

`await` waits for an awaitable:

```python
result = await get_result()
```

Example:

```python
import asyncio

async def main():
    print("start")
    await asyncio.sleep(1)
    print("end")

asyncio.run(main())
```

Compare:

```python
import time

time.sleep(1)
```

with:

```python
await asyncio.sleep(1)
```

The first blocks the current thread. The second suspends the current coroutine so the event loop can schedule other work.

---

## 17. `asyncio.create_task()`

`asyncio.create_task()` schedules a coroutine as an asyncio Task.

```python
import asyncio

async def work(name, delay):
    await asyncio.sleep(delay)
    return name

async def main():
    task_a = asyncio.create_task(work("A", 0.2))
    task_b = asyncio.create_task(work("B", 0.1))

    result_a = await task_a
    result_b = await task_b

    print(result_a, result_b)

asyncio.run(main())
```

### Why use a Task?

Without scheduling, simply creating coroutine objects does not make them independently scheduled.

Task creation says, conceptually:

```text
Here is a coroutine.
Please schedule it as independent async work.
```

### Trade-off

Creating tasks is cheap relative to creating processes, but it is not free.

Thousands or millions of tasks can still create:

- memory pressure;
- scheduler overhead;
- downstream load;
- cancellation complexity.

---

## 18. `asyncio.Task`

A Task tracks the execution state of a scheduled coroutine.

Useful methods and functions include:

- `asyncio.current_task()`;
- `asyncio.all_tasks()`;
- `Task.done()`;
- `Task.result()`;
- `Task.exception()`;
- `Task.cancel()`;
- `Task.cancelled()`;
- `Task.add_done_callback()`;
- `Task.get_name()`;
- `Task.set_name()`.

### Lifecycle

```text
created
   ↓
scheduled
   ↓
running
   ↓
waiting at await
   ↓
running again
   ↓
completed
   ├── success
   ├── failure
   └── cancellation
```

Example:

```python
import asyncio

async def work():
    await asyncio.sleep(0.05)
    return 42

async def main():
    task = asyncio.create_task(work(), name="answer-task")

    print(task.get_name())
    print(task.done())

    result = await task

    print(result)
    print(task.done())
    print(task.result())

asyncio.run(main())
```

Do not call `result()` before a task is complete; doing so raises an `InvalidStateError` in the relevant situation.

`exception()` likewise requires an appropriate completed state.

---

## 19. `asyncio.gather()`

`asyncio.gather()` is useful when several awaitables should be awaited together and their results collected.

```python
import asyncio

async def fetch(name, delay):
    await asyncio.sleep(delay)
    return name

async def main():
    results = await asyncio.gather(
        fetch("A", 0.2),
        fetch("B", 0.1),
        fetch("C", 0.15),
    )
    print(results)

asyncio.run(main())
```

The result preserves the input ordering of the awaitables even if they finish in another order.

### When useful

- independent I/O operations;
- fan-out/fan-in work;
- collecting multiple results.

### Be careful

If the number of operations is enormous, submitting everything at once may overwhelm:

- memory;
- a downstream API;
- connection pools;
- rate limits.

Bounded concurrency is often the next design step.

---

## 20. `asyncio.wait()` and `asyncio.as_completed()`

### `asyncio.wait()`

`asyncio.wait()` lets you wait according to conditions such as:

- all tasks;
- first completed;
- first exception.

Example:

```python
import asyncio

async def work(delay, value):
    await asyncio.sleep(delay)
    return value

async def main():
    tasks = {
        asyncio.create_task(work(0.2, "A")),
        asyncio.create_task(work(0.1, "B")),
    }

    done, pending = await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_COMPLETED,
    )

    print("done:", len(done))
    print("pending:", len(pending))

    for task in pending:
        task.cancel()

asyncio.run(main())
```

### `asyncio.as_completed()`

Use `as_completed()` when you want results in completion order.

```python
import asyncio

async def work(delay, value):
    await asyncio.sleep(delay)
    return value

async def main():
    tasks = [
        asyncio.create_task(work(0.2, "A")),
        asyncio.create_task(work(0.1, "B")),
    ]

    async for completed in asyncio.as_completed(tasks):
        result = await completed
        print(result)

asyncio.run(main())
```

The exact iteration interface has evolved across Python versions; verify the API contract for the version you deploy.

---

## 21. `asyncio.sleep()`

`asyncio.sleep(delay)` suspends the current coroutine for the given delay.

```python
await asyncio.sleep(0.5)
```

Unlike `time.sleep()` in async code, this allows the event loop to continue running other tasks.

Use it for:

- simulation;
- scheduled delays;
- retry backoff;
- pacing.

Do not use it as a synchronization primitive when a proper event, lock, or condition expresses the required behavior more accurately.

# PART V — FUTURES

## 22. Future

A **Future** is a placeholder for a result that will become available later.

```text
Future
 ├── pending
 ├── result
 └── exception
```

An application can register callbacks or await the future depending on the concurrency framework.

### `asyncio.Future`

Important methods include:

- `done()`;
- `result()`;
- `exception()`;
- `cancel()`;
- `cancelled()`;
- `add_done_callback()`;
- `set_result()`;
- `set_exception()`.

Example:

```python
import asyncio

async def main():
    loop = asyncio.get_running_loop()
    future = loop.create_future()

    loop.call_later(0.05, future.set_result, "ready")

    result = await future
    print(result)

asyncio.run(main())
```

### Important distinction

`asyncio.Future` and `concurrent.futures.Future` are **different classes for different concurrency ecosystems**.

Do not treat them as interchangeable.

### Task versus Future

A useful mental model is:

```text
Coroutine
   ↓ scheduled by asyncio
Task
   ↓ behaves like a Future-like result holder
Future
   ↓
result / exception / cancellation
```

A Task is specialized for driving a coroutine; a Future is a lower-level placeholder abstraction.

For normal application code, developers usually create Tasks/coroutines rather than manually constructing Futures.

---

# PART VI — THREADING VOCABULARY

## 23. `threading`

The `threading` module provides a higher-level interface for managing threads.

Example:

```python
import threading

def worker():
    print(f"running in {threading.current_thread().name}")

thread = threading.Thread(target=worker, name="worker-1")
thread.start()
thread.join()
```

Important terminology:

- thread identity;
- thread lifecycle;
- shared memory;
- synchronization;
- thread-safe operations.

### Useful APIs

| API | Purpose |
|---|---|
| `Thread` | Represents a thread |
| `start()` | Begins thread execution |
| `join()` | Waits for thread completion |
| `is_alive()` | Checks whether it is running |
| `current_thread()` | Returns the current thread |
| `main_thread()` | Returns the main thread |
| `enumerate()` | Lists active threads |
| `active_count()` | Counts active threads |

---

## 24. Thread Synchronization

Threads share memory, so this can happen:

```text
Thread A ─┐
          ├── shared state
Thread B ─┘
```

Suppose both execute:

```text
read value
modify value
write value
```

If their operations interleave unexpectedly, the result may be incorrect.

Vocabulary:

- **shared state** — data visible to multiple execution contexts;
- **race condition** — correctness depends on timing/interleaving;
- **critical section** — code that must not be concurrently modified;
- **synchronization** — coordinating execution to preserve correctness;
- **mutual exclusion** — only one execution context enters a protected region at a time.

The safest design is often to reduce shared mutable state rather than adding more locks.

---

## 25. `threading.Lock`

A `Lock` is a synchronization primitive for mutual exclusion.

```python
import threading

lock = threading.Lock()

with lock:
    # critical section
    ...
```

The core methods are:

```python
lock.acquire()
lock.release()
```

A lock can also support `acquire(blocking=False)` and timeout-based acquisition.

### Why `with` is preferred

```python
with lock:
    update_shared_state()
```

is easier to make correct than:

```python
lock.acquire()
try:
    update_shared_state()
finally:
    lock.release()
```

Both can be correct; the context-manager form reduces cleanup mistakes.

---

## 26. `RLock`, `Semaphore`, `BoundedSemaphore`, `Event`, `Condition`, `Barrier`

These primitives solve different coordination problems.

### `RLock`

A reentrant lock can be acquired multiple times by the same thread.

Useful when nested calls may need the same lock.

```python
import threading

lock = threading.RLock()

with lock:
    with lock:
        print("same thread acquired twice")
```

### `Semaphore`

A semaphore limits how many threads may enter a region concurrently.

```python
import threading

sem = threading.Semaphore(3)

with sem:
    use_limited_resource()
```

Conceptually:

```text
permits = 3
Thread A → permit
Thread B → permit
Thread C → permit
Thread D → waits
```

This is a useful primitive for limiting concurrency.

### `BoundedSemaphore`

Similar to `Semaphore`, but checks that releases do not exceed the configured bound.

### `Event`

An Event is a shared flag that threads can wait for.

```python
import threading

ready = threading.Event()

# worker:
ready.wait()

# coordinator:
ready.set()
```

### `Condition`

A condition lets threads wait for a state change while coordinating access to shared state.

### `Barrier`

A barrier allows a fixed number of threads to wait until all participating threads reach the same synchronization point.

### Selection principle

Do not memorize primitive names in isolation.

Ask:

> **What state or coordination problem am I trying to express?**

# PART VII — THREAD-SAFE COMMUNICATION

## 27. Queues

A queue provides a cleaner communication model than directly sharing mutable collections.

### Producer-consumer pattern

```text
Producer
   ↓
 Queue
   ↓
Consumer
```

A bounded queue can also provide natural backpressure:

```text
Producer → bounded queue → Consumer
               ↑
        blocks when full
```

---

## 28. `queue.Queue`

`queue.Queue` is a synchronized FIFO queue designed for multi-producer/multi-consumer threaded use.

```python
from queue import Queue

q = Queue(maxsize=100)
q.put("job")
job = q.get()
```

Relevant methods:

- `put()`;
- `put_nowait()`;
- `get()`;
- `get_nowait()`;
- `task_done()`;
- `join()`;
- `qsize()`;
- `empty()`;
- `full()`.

### Timeout-aware example

```python
from queue import Queue, Empty

q = Queue(maxsize=2)
q.put("job")

item = q.get(timeout=0.5)
q.task_done()

try:
    q.get(timeout=0.01)
except Empty:
    print("no item arrived")
```

### Task tracking

```python
q.put("job-1")
q.put("job-2")

# consumers:
job = q.get()
process(job)
q.task_done()

q.join()
```

`join()` waits until every enqueued task has received a corresponding `task_done()` call.

### Production warning

Forgetting `task_done()` can leave `join()` waiting indefinitely.

---

## 29. `SimpleQueue`, `PriorityQueue`, and `LifoQueue`

### `SimpleQueue`

A simpler FIFO queue when advanced task-tracking behavior is not needed.

```python
from queue import SimpleQueue

q = SimpleQueue()
q.put("a")
print(q.get())
```

### `PriorityQueue`

Items are retrieved by priority order.

```python
from queue import PriorityQueue

q = PriorityQueue()
q.put((10, "low"))
q.put((1, "high"))

print(q.get())  # (1, "high")
```

### `LifoQueue`

Acts like a stack:

```python
from queue import LifoQueue

q = LifoQueue()
q.put("a")
q.put("b")

print(q.get())  # b
```

### Version note

Modern Python 3.13+ also provides queue shutdown behavior and `queue.ShutDown`. That is useful in graceful worker termination designs; it should be learned alongside shutdown semantics in the Python version you deploy.

---

## 30. Queue Backpressure

Suppose producers are faster than consumers:

```text
Producer rate: 10,000 jobs/s
Consumer rate: 1,000 jobs/s
```

An unbounded queue may grow until memory pressure becomes the failure mode.

A bounded queue changes the system:

```text
Producer
   ↓
bounded queue
   ↓
Consumer

queue full
   ↓
producer waits/rejects according to policy
```

Backpressure is therefore a **system-control mechanism**, not merely a queue feature.

---

# PART VIII — MULTIPROCESSING

## 31. Processes and `multiprocessing`

The `multiprocessing` module starts independent Python processes.

```python
from multiprocessing import Process

def worker():
    print("child process")

if __name__ == "__main__":
    p = Process(target=worker)
    p.start()
    p.join()
```

### Why the `__main__` guard matters

Process-start behavior differs by platform and start method. Code that creates processes should generally protect the entry point with:

```python
if __name__ == "__main__":
    ...
```

### Trade-offs

Processes give stronger isolation but introduce:

- startup overhead;
- separate address spaces;
- inter-process communication;
- serialization;
- more complex lifecycle management.

---

## 32. `multiprocessing.Process`

Important APIs:

- `Process(...)`;
- `start()`;
- `join()`;
- `is_alive()`;
- `terminate()`;
- `kill()` where supported;
- `close()`;
- `exitcode`.

Example:

```python
from multiprocessing import Process
import os
import time

def worker():
    print("child pid:", os.getpid())
    time.sleep(0.1)

if __name__ == "__main__":
    p = Process(target=worker)
    p.start()

    print("alive:", p.is_alive())
    p.join()

    print("exitcode:", p.exitcode)
```

### `terminate()` versus `kill()`

Both are forceful termination mechanisms. They do not provide the same graceful semantics as letting a worker complete or implementing application-level cancellation.

Do not use process termination as your default form of normal shutdown.

---

# PART IX — EXECUTORS

## 33. Executor

An **Executor** provides a high-level interface for executing callables asynchronously.

Mental model:

```text
submit(callable)
       ↓
    Executor
       ↓
    worker
       ↓
    Future
```

The major implementations in `concurrent.futures` are:

- `ThreadPoolExecutor`;
- `ProcessPoolExecutor`;
- modern Python versions also include `InterpreterPoolExecutor` as a related execution model.

Executors let application code focus on submitting work rather than manually managing every worker.

---

## 34. `ThreadPoolExecutor`

Example:

```python
from concurrent.futures import ThreadPoolExecutor

def square(x):
    return x * x

with ThreadPoolExecutor(max_workers=4) as executor:
    future = executor.submit(square, 5)
    print(future.result())
```

Important APIs:

- `submit()`;
- `map()`;
- `shutdown()`.

### `submit()`

Returns a `concurrent.futures.Future`.

```python
future = executor.submit(square, 10)
result = future.result()
```

### `map()`

Convenient for applying a callable across an iterable.

```python
with ThreadPoolExecutor(max_workers=4) as executor:
    for result in executor.map(square, range(5)):
        print(result)
```

### When threads fit

Thread pools are often useful for I/O-bound synchronous functions.

---

## 35. `ProcessPoolExecutor`

Example:

```python
from concurrent.futures import ProcessPoolExecutor

def square(x):
    return x * x

if __name__ == "__main__":
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(square, range(5)))
        print(results)
```

Use it when separate processes are useful, particularly for CPU-heavy work.

### Costs

Inputs and outputs may need serialization.

Workers have process startup and communication overhead.

Functions submitted to a process pool must be serializable under the executor's requirements.

### Do not use it mechanically

For tiny computations, process overhead can dominate the actual work.

---

## 36. `concurrent.futures.Future`

A futures-executor Future represents a result that may become available later.

Relevant methods include:

- `cancel()`;
- `cancelled()`;
- `running()`;
- `done()`;
- `result()`;
- `exception()`;
- `add_done_callback()`.

Example:

```python
from concurrent.futures import ThreadPoolExecutor

def work():
    return 42

with ThreadPoolExecutor() as executor:
    future = executor.submit(work)

    print(future.done())
    print(future.result())
```

### Two Future ecosystems

| Future | Used with |
|---|---|
| `asyncio.Future` | asyncio/event-loop concurrency |
| `concurrent.futures.Future` | executor-based concurrency |

Do not confuse them.

# PART X — THE GIL

## 37. Python GIL

The **Global Interpreter Lock (GIL)** is a CPython implementation concept.

In traditional GIL-enabled CPython, the GIL limits how multiple threads execute Python-level bytecode concurrently, so CPU-bound pure-Python workloads generally do not gain straightforward multi-core execution merely by adding threads.

That does **not** mean "Python cannot do parallelism."

Python systems can use:

- multiple processes;
- process pools;
- native libraries that release the GIL;
- GPU computation;
- free-threaded CPython builds in supported environments.

### Why threads still help

For I/O-bound workloads, threads can overlap waiting:

```text
Thread A → network wait
Thread B → network wait
Thread C → process a ready response
```

CPython can also release the GIL around some blocking or native operations.

### Free-threaded Python

CPython has supported free-threaded builds beginning with Python 3.13, where the GIL can be disabled in a distinct build/configuration.

Do not silently assume that:

```text
Python 3.14
=
every Python process is free-threaded
```

It is a distinct deployment mode with ecosystem compatibility considerations.

### Engineering takeaway

When someone says:

> "The GIL means threads are useless."

that is too broad.

The accurate question is:

> **What workload, Python implementation/build, libraries, and resources are involved?**

# PART XI — RACE CONDITIONS AND CORRECTNESS

## 38. Race Condition

A race condition occurs when the correctness of a result depends on an uncontrolled timing/interleaving between concurrent operations.

A classic pattern is:

```text
read
  ↓
modify
  ↓
write
```

Imagine:

```text
counter = 10

Thread A: read 10
Thread B: read 10
Thread A: write 11
Thread B: write 11
```

The expected result for two increments is 12, but the interleaving above produces 11.

The deeper issue is not that "increment" is a single magical action. It is that a multi-step state transition was allowed to interleave unsafely.

---

## 39. Atomicity

An operation is **atomic** when it behaves as one indivisible operation relative to a particular concurrency context.

Do not make blanket claims such as:

> "All Python operations are atomic."

The real answer depends on:

- Python implementation;
- version;
- operation;
- object type;
- execution mode;
- surrounding code.

### Engineering rule

If correctness depends on multiple operations being observed or executed as one consistent state transition, use an explicit synchronization or coordination strategy.

---

## 40. Thread Safety

A component is **thread-safe** when it can be used concurrently according to its documented guarantees without violating its correctness contract.

Thread-safe does not mean:

- your entire workflow is safe;
- your data model is race-free;
- every sequence of calls is atomic.

Example:

```python
if not cache.contains(key):
    cache.add(key)
```

Even if each individual method were safe, the combined check-then-act sequence may still race.

### Better question

Instead of:

> "Is this object thread-safe?"

ask:

> "Which operations are synchronized, and is my entire state transition safe?"

## 41. Deadlock

A deadlock occurs when concurrent execution becomes permanently blocked because each participant is waiting for something that another participant will not release.

Classic example:

```text
Thread A:
    holds Lock 1
    waits for Lock 2

Thread B:
    holds Lock 2
    waits for Lock 1
```

### Four classic conditions

The classic deadlock conditions are:

1. mutual exclusion;
2. hold and wait;
3. no preemption;
4. circular wait.

Breaking any one of these can prevent that particular deadlock pattern.

### Common prevention strategies

- consistent lock ordering;
- small critical sections;
- avoid nested locks where possible;
- timeouts;
- message passing;
- reducing shared mutable state.

Example of consistent ordering:

```python
def update_both(a_lock, b_lock):
    first, second = sorted(
        (a_lock, b_lock),
        key=id,
    )

    with first:
        with second:
            update_shared_state()
```

The exact pattern should be adapted to the application's ownership model; the important idea is **consistent ordering**.

---

## 42. Other Concurrency Failure Modes

### Starvation

A task waits indefinitely because other work repeatedly gets the resources it needs first.

### Livelock

Tasks are active but keep reacting to each other without making useful progress.

### Lost update

Two workers compute from stale state and one update overwrites the other.

### Duplicate work

Multiple workers perform the same expensive operation because no coordination prevents duplication.

### Cancellation bug

A task is cancelled while holding or owning resources and cleanup is incomplete.

### Resource exhaustion

Concurrency exceeds available:

- connections;
- file descriptors;
- memory;
- API quotas;
- GPU capacity;
- queue capacity.

### Priority inversion

A higher-priority activity is delayed by lower-priority work holding a resource it needs.

These are different failure modes even though they can all appear as "the concurrent program is stuck or slow."

# PART XII — ASYNC CONCURRENCY CONTROL

## 43. Async Synchronization

Asyncio has synchronization primitives designed for coroutine-based concurrency.

Important primitives:

- `asyncio.Lock`;
- `asyncio.Event`;
- `asyncio.Condition`;
- `asyncio.Semaphore`;
- `asyncio.BoundedSemaphore`;
- `asyncio.Queue`.

### `asyncio.Lock`

```python
import asyncio

lock = asyncio.Lock()

async def update():
    async with lock:
        mutate_shared_state()
```

Use an async lock when multiple coroutines need coordinated access to state inside the same async execution environment.

A `threading.Lock` is not interchangeable with an `asyncio.Lock`.

### `asyncio.Semaphore`

```python
sem = asyncio.Semaphore(5)

async def call_service():
    async with sem:
        return await external_call()
```

This limits the number of concurrent calls.

### `asyncio.Queue`

```python
queue = asyncio.Queue(maxsize=100)
```

It can coordinate async producers and consumers and provides a natural location for backpressure.

---

## 44. Timeouts

Production calls to external systems should usually have explicit time bounds.

Why?

Without a timeout:

```text
request
  ↓
downstream hangs
  ↓
worker waits
  ↓
concurrency slots remain occupied
  ↓
queue grows
  ↓
service degrades
```

Asyncio provides APIs such as:

- `asyncio.timeout()`;
- `asyncio.wait_for()`.

### `asyncio.timeout()`

```python
import asyncio

async def fetch():
    await asyncio.sleep(2)

async def main():
    try:
        async with asyncio.timeout(0.1):
            await fetch()
    except TimeoutError:
        print("timed out")

asyncio.run(main())
```

### `asyncio.wait_for()`

```python
import asyncio

async def fetch():
    await asyncio.sleep(2)

async def main():
    try:
        await asyncio.wait_for(fetch(), timeout=0.1)
    except TimeoutError:
        print("timed out")

asyncio.run(main())
```

Use timeout APIs according to the cancellation and ownership semantics of your application.

---

## 45. Timeout vs Cancellation

A **timeout** is a policy:

> "This operation must not take longer than X."

**Cancellation** is a control signal:

> "This work should stop."

A timeout often triggers cancellation of the underlying async work.

They should nevertheless be treated as distinct concepts.

Production design should specify:

- who owns the task;
- who can cancel it;
- what cleanup happens;
- whether partial work is safe;
- whether downstream operations must also be cancelled.

---

## 46. Cancellation

A Task can be cancelled:

```python
task.cancel()
```

Cancellation is generally cooperative. An `asyncio.CancelledError` is raised at the next opportunity in the task.

Example:

```python
import asyncio

async def worker():
    try:
        while True:
            await asyncio.sleep(1)
    finally:
        print("cleanup")

async def main():
    task = asyncio.create_task(worker())
    await asyncio.sleep(0.05)

    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        print("worker cancelled")

asyncio.run(main())
```

### Cleanup rule

Use `try/finally` for resources that require cleanup.

If you catch `CancelledError` explicitly for cleanup logic, generally allow it to propagate after cleanup unless you have a specific reason to suppress cancellation.

Swallowing cancellation can interfere with structured concurrency tools such as TaskGroup and timeout contexts.

---

## 47. Backpressure

Backpressure means slowing, limiting, buffering, or rejecting incoming work when downstream capacity is lower than incoming demand.

### Example

```text
Producer
   ↓↓↓↓↓↓↓↓↓
bounded queue
   ↓
Consumer
```

If the producer is much faster than the consumer, something must happen.

Possible policies:

- wait;
- queue up to a limit;
- reject;
- drop;
- sample;
- batch;
- rate-limit;
- reduce concurrency.

### AI examples

Backpressure is important when:

- embedding APIs have quotas;
- LLM APIs rate-limit requests;
- vector databases have connection limits;
- GPU inference has finite capacity;
- document queues can grow without bound.

Backpressure is a system-level control strategy, not merely a programming trick.

# PART XIII — STRUCTURED CONCURRENCY

## 48. Structured Concurrency

Structured concurrency organizes concurrent work so that task lifetime and ownership are explicit.

Mental model:

```text
Parent scope
├── Child task A
├── Child task B
└── Child task C

exit scope
   ↓
all child work is accounted for
```

Important ideas:

- task ownership;
- bounded lifetime;
- cancellation propagation;
- predictable cleanup;
- grouped error handling.

## `asyncio.TaskGroup`

Modern asyncio provides `TaskGroup`.

```python
import asyncio

async def work(name, delay):
    await asyncio.sleep(delay)
    return name

async def main():
    async with asyncio.TaskGroup() as tg:
        task_a = tg.create_task(work("A", 0.2))
        task_b = tg.create_task(work("B", 0.1))

    print(task_a.result())
    print(task_b.result())

asyncio.run(main())
```

TaskGroup provides a structured scope in which the group waits for its tasks.

If one task fails with an exception other than cancellation, remaining tasks in the group are cancelled as part of the group semantics.

### Why this matters

Compare:

```text
"Here are some tasks I created somewhere."
```

with:

```text
"This scope owns these child tasks."
```

The second model makes lifecycle and failure behavior easier to reason about.

---

# PART XIV — CONCURRENCY DESIGN PATTERNS

## 49. Producer-Consumer

```text
Producer(s)
     ↓
   Queue
     ↓
Consumer(s)
```

Use when work arrives at one rate and is processed at another.

Typical uses:

- message processing;
- file ingestion;
- AI document jobs;
- background workers.

Trade-offs:

- queue size;
- latency;
- ordering;
- failure handling;
- retry behavior;
- persistence.

---

## 50. Worker Pool

A worker pool creates a fixed or bounded number of workers.

```text
               ┌→ Worker 1
Jobs → Pool ───┼→ Worker 2
               └→ Worker 3
```

Benefits:

- limits concurrency;
- reuses worker resources;
- smooths bursts;
- reduces task explosion.

---

## 51. Fan-Out and Fan-In

### Fan-out

One request starts multiple independent operations:

```text
          ┌→ Search
Request ──┼→ Database
          ├→ Metadata
          └→ Model API
```

### Fan-in

Results are combined:

```text
Search ───┐
Database ─┼→ aggregate
Metadata ─┘
```

Fan-out is useful only when the operations are independent enough to overlap safely.

Dependencies may force a sequential chain.

---

## 52. Pipeline

A pipeline divides work into stages:

```text
Stage 1 → Stage 2 → Stage 3
```

A production data pipeline might be:

```text
load
  ↓
parse
  ↓
clean
  ↓
embed
  ↓
store
```

Different stages may have different bottlenecks.

That creates an important design question:

> Where should concurrency be applied, and where should backpressure exist?

---

## 53. Rate-Limited Concurrency

Suppose an API allows only 20 in-flight requests.

A semaphore expresses the concurrency limit:

```python
import asyncio

limit = asyncio.Semaphore(20)

async def call_api(item):
    async with limit:
        return await api_call(item)
```

This does not automatically enforce every rate-limit policy. For example, a service may have both:

- maximum concurrent requests;
- requests-per-second quota.

A semaphore controls concurrency, not every possible form of rate limiting.

# PART XV — CONCURRENCY AND APPLIED AI

## 54. Applied AI Engineering Connections

Concurrency appears throughout modern AI systems.

### LLM API orchestration

Suppose five independent model calls are needed:

```text
Request
 ├── LLM A
 ├── LLM B
 ├── LLM C
 ├── LLM D
 └── LLM E
```

Parallelizing or concurrently overlapping those I/O-bound calls may reduce wall-clock latency.

But production constraints include:

- provider rate limits;
- concurrency quotas;
- timeouts;
- retries;
- cancellation;
- cost;
- output ordering.

### Embedding generation

```text
Documents
  ↓
Chunking
  ↓
bounded concurrent embedding calls
  ↓
Vector database
```

Too much concurrency can cause:

- API throttling;
- memory growth;
- connection exhaustion;
- retry storms.

### RAG ingestion

A practical pipeline may be:

```text
document queue
      ↓
parsing workers
      ↓
chunking
      ↓
bounded embedding concurrency
      ↓
vector-store writes
```

Each stage can have a different capacity.

### Agent tool execution

An agent may need:

```text
Search
Database
Inventory API
User profile
```

If those operations are independent, the orchestration layer may fan them out concurrently.

If step B depends on A's result, the dependency forces sequencing.

### Inference services

Concurrency appears in:

- request admission;
- batching;
- preprocessing;
- queueing;
- GPU scheduling;
- result postprocessing.

Do not confuse:

```text
Python concurrency
```

with:

```text
GPU parallelism
```

and do not confuse either with:

```text
distributed concurrency across machines
```

These are different layers.

---

## 55. LLM API Concurrency: A Concrete Example

A safe starting point is bounded concurrency.

```python
import asyncio

sem = asyncio.Semaphore(5)

async def call_llm(prompt):
    async with sem:
        return await fake_llm_call(prompt)

async def process_all(prompts):
    tasks = [
        asyncio.create_task(call_llm(prompt))
        for prompt in prompts
    ]
    return await asyncio.gather(*tasks)
```

This still creates one Task per prompt, so for very large input sets you may prefer a bounded worker architecture rather than creating hundreds of thousands of tasks at once.

### Design ladder

```text
Small workload
    ↓
gather()

Larger workload
    ↓
bounded worker pool / semaphore

Very large workload
    ↓
durable queue + workers + retry policy
```

The architecture should follow the workload.

---

## 56. Python Concurrency vs Distributed Concurrency vs GPU Parallelism

### Python concurrency

Happens inside a process using mechanisms such as:

- threads;
- asyncio tasks;
- executors.

### Distributed concurrency

Work is spread across:

- processes;
- containers;
- machines;
- queues;
- services.

Example:

```text
API
 ↓
Message broker
 ├── Worker 1
 ├── Worker 2
 ├── Worker 3
 └── Worker 4
```

### GPU parallelism

A GPU executes numerical workloads using many hardware execution resources according to its execution model.

```text
Python service
      ↓
GPU runtime
      ↓
GPU kernels / tensor operations
```

A Python service can be concurrent while the GPU performs parallel computation underneath.

These concepts interact but are not interchangeable.

# PART XVI — PRODUCTION CASE STUDY

## 57. Production Case Study: Concurrent Document Processing

Scenario:

```text
10,000 documents
      ↓
text extraction
      ↓
chunking
      ↓
embedding API
      ↓
vector database
```

### Naive sequential design

```text
document 1 → extract → embed → store → done
document 2 → extract → embed → store → done
document 3 → ...
```

This can leave the process waiting repeatedly on I/O.

### Concurrent design

```text
                ┌→ document worker 1
documents → queue├→ document worker 2
                ├→ document worker 3
                └→ document worker 4
```

### Required controls

#### Concurrency limit

Do not make 10,000 API calls in flight simply because 10,000 documents exist.

#### Queue

Use a queue or durable broker to decouple arrival rate from processing rate.

#### Timeout

Every network dependency needs a failure boundary.

#### Retry

Retries must have:

- limits;
- backoff;
- classification of retryable errors.

#### Rate limit

A provider may enforce requests-per-second or concurrent-request limits.

#### Cancellation

Shutdown should stop accepting new work and give active work a controlled path to terminate.

#### Backpressure

Do not allow a fast producer to create unlimited pending work.

#### Memory control

Do not hold all:

- documents;
- chunks;
- embeddings;
- responses

in RAM unnecessarily.

#### Observability

Measure:

- task latency;
- queue depth;
- in-flight work;
- success rate;
- retry count;
- timeout count;
- provider error count;
- memory usage.

### Architectural lesson

Concurrency is not one switch.

It is a set of decisions about:

```text
work units
→ scheduling
→ concurrency limit
→ ownership
→ failure
→ cancellation
→ queueing
→ backpressure
→ observability
```

# PART XVII — DEBUGGING AND TESTING

## 58. Debugging Concurrency

Concurrency bugs are difficult because timing matters.

A bug may:

- disappear when logging is added;
- disappear under a debugger;
- happen once in 10,000 executions;
- depend on machine load;
- depend on network latency.

### Practical debugging workflow

```text
1. Reproduce
2. Reduce
3. Instrument
4. Identify shared state
5. Identify ownership
6. Identify synchronization
7. Inspect timing
8. Fix
9. Stress test
10. Add regression coverage
```

### Logging

Include context such as:

- request ID;
- task ID;
- thread name;
- process ID;
- timestamps;
- state transitions.

Avoid logging sensitive payloads merely to debug concurrency.

---

## 59. Testing Concurrent Systems

Useful test layers:

| Test type | Purpose |
|---|---|
| Unit | Individual behavior |
| Integration | Interaction with real components |
| Stress | Repeated execution under pressure |
| Load | Behavior under expected/peak demand |
| Failure injection | Retry/timeout/cancellation behavior |
| Regression | Prevent known race/deadlock bugs from returning |

### Why one successful run is insufficient

A concurrency bug may require a particular interleaving.

Therefore:

```text
passes once
```

does not prove:

```text
always correct
```

### Useful testing ideas

- repeat critical tests;
- randomize timing in controlled test environments;
- test timeouts;
- test cancellation;
- test queue saturation;
- test worker shutdown;
- verify no tasks are leaked.

---

## 60. Testing an Async Function

Example:

```python
import asyncio

async def fetch_value():
    await asyncio.sleep(0)
    return 42
```

A test framework such as pytest with async support can run the coroutine.

Conceptual test:

```python
async def test_fetch_value():
    result = await fetch_value()
    assert result == 42
```

The important idea is that the test should observe behavior rather than depend on a fragile sleep duration.

---

## 61. Testing Cancellation

A cancellation test should prove that:

1. cancellation reaches the task;
2. cleanup executes;
3. the cancellation contract is preserved.

Example:

```python
import asyncio

async def worker(log):
    try:
        await asyncio.sleep(10)
    finally:
        log.append("cleaned")

async def test_cancellation():
    log = []

    task = asyncio.create_task(worker(log))
    await asyncio.sleep(0)

    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        pass

    assert log == ["cleaned"]
```

The exact test harness may vary, but the behavioral principle is stable.

---

## 62. Performance: Latency, Throughput, and Utilization

### Latency

Time for one operation.

### Throughput

Amount of work completed over a period.

### Utilization

How much available capacity is being used.

### Concurrency can improve throughput without improving every latency

For example, ten concurrent requests may increase throughput but also increase queueing and downstream contention.

### More workers can make a system slower

```text
Too little concurrency
    ↓
underutilization

Reasonable concurrency
    ↓
good overlap

Too much concurrency
    ↓
contention / throttling / memory pressure / overhead
```

Therefore:

> **Concurrency level is a tunable system parameter, not a badge of architectural quality.**

# PART XVIII — COMMON MISTAKES

## 63. Common Beginner Mistakes

### 1. "Concurrency means parallelism."

**Why wrong:** Concurrency can exist on one thread through task scheduling.

**Correction:** Separate overlapping progress from simultaneous execution.

### 2. "Async always makes code faster."

**Why wrong:** Async mainly helps workloads that can benefit from overlapping waits.

**Correction:** Identify the bottleneck first.

### 3. Blocking the event loop

```python
async def bad():
    import time
    time.sleep(5)
```

**Correction:** Use an async-compatible API or explicitly isolate blocking work.

### 4. Creating unlimited tasks

```python
tasks = [asyncio.create_task(work(x)) for x in huge_input]
```

**Why risky:** large task counts consume memory and may overload downstream systems.

### 5. Ignoring API rate limits

Concurrency can turn:

```text
10 requests
```

into:

```text
10,000 requests in a short interval
```

### 6. Forgetting timeouts

A slow dependency can consume all concurrency slots.

### 7. Ignoring cancellation

Work may continue after the caller no longer needs it.

### 8. Sharing mutable state unnecessarily

The more shared mutable state exists, the more synchronization becomes necessary.

### 9. Assuming threads speed up CPU-bound Python code

Traditional GIL-enabled CPython limits Python-level CPU concurrency in a way that makes threads a poor default for that workload.

### 10. Assuming multiprocessing is free

Processes have startup, memory, and serialization overhead.

### 11. Using locks as a universal solution

Locks prevent certain races but can introduce deadlocks and contention.

### 12. Ignoring backpressure

Unlimited incoming work is not a scaling strategy.

### 13. Increasing worker count without measurement

More workers may simply move the bottleneck downstream.

### 14. Confusing concurrency with GPU parallelism

A concurrent Python service and a parallel GPU kernel are different execution mechanisms.

### 15. Using concurrency when sequential code is enough

Complexity has a cost. Simpler code is often better when concurrency does not solve a real bottleneck.

# PART XIX — HANDS-ON CODING EXERCISES

## 64. Coding Exercises

The exercises intentionally build from vocabulary to implementation.

### Level 1 — Sequential Baseline

**Objective:** Learn to measure a baseline before adding concurrency.

**Starter code:**

```python
import time

def work(delay):
    time.sleep(delay)
    return delay

start = time.perf_counter()

results = [work(0.1) for _ in range(3)]

elapsed = time.perf_counter() - start
print(results)
print(elapsed)
```

**Task:** Record the elapsed time.

**Expected behavior:** The calls happen one after another.

**Hint:** Do not change the workload yet.

---

### Level 2 — I/O-Bound or CPU-Bound?

Classify these workloads:

1. five HTTP requests;
2. SHA-like CPU-heavy hashing loops;
3. reading a large file;
4. external database query;
5. pure-Python image transformation loop.

**Expected skill:** Recognize the dominant waiting/computation behavior before selecting a model.

**Hint:** Ask what the program is doing while it waits.

---

### Level 3 — Basic Thread

Create two `threading.Thread` objects.

**Objective:** Understand thread lifecycle.

Requirements:

- create;
- start;
- print a message;
- join.

**Hint:** `join()` waits for completion.

---

### Level 4 — ThreadPoolExecutor

Use `ThreadPoolExecutor` to run five independent I/O-like functions.

**Constraints:**

- no more than three workers;
- collect all results.

**Expected behavior:** The pool reuses a bounded number of threads.

**Hint:** `executor.submit()` returns a Future.

---

### Level 5 — First Async Function

Write:

```python
async def work():
    ...
```

Then run it using:

```python
asyncio.run(...)
```

**Objective:** Understand coroutine syntax and the event-loop entry point.

---

### Level 6 — `create_task()`

Start three independent coroutine tasks.

Requirements:

- create all tasks before awaiting them individually;
- record completion order.

**Objective:** Observe concurrency.

**Hint:** Use different `asyncio.sleep()` delays.

---

### Level 7 — `gather()`

Rewrite Level 6 using `asyncio.gather()`.

**Objective:** Learn fan-out/fan-in result collection.

---

### Level 8 — Concurrency Limit

Create 100 async jobs but allow at most five to be active at once.

**Required concept:** `asyncio.Semaphore`.

**Expected behavior:** No more than five jobs enter the protected region concurrently.

---

### Level 9 — Timeout

Wrap a simulated slow dependency in:

```python
asyncio.timeout(...)
```

**Expected behavior:** Slow work is cancelled/terminated according to timeout semantics and a timeout is handled.

---

### Level 10 — Cancellation

Create a long-running task.

Cancel it after a short delay.

Requirements:

- use `try/finally`;
- verify cleanup occurred.

---

### Level 11 — Producer-Consumer

Use `asyncio.Queue` or `queue.Queue`.

Requirements:

- producer creates jobs;
- consumers process jobs;
- queue has a bound;
- shutdown behavior is defined.

---

### Level 12 — Deadlock Diagnosis

Study:

```python
import threading

lock_a = threading.Lock()
lock_b = threading.Lock()

def worker_a():
    with lock_a:
        with lock_b:
            print("A")

def worker_b():
    with lock_b:
        with lock_a:
            print("B")
```

**Task:** Explain the deadlock risk.

**Hint:** Compare lock acquisition order.

---

### Level 13 — Backpressure

Design a bounded queue for an embedding pipeline.

**Task:** Explain what happens when producers are faster than consumers.

**Expected answer topics:**

- queue fills;
- producer waits/rejects;
- memory remains bounded;
- throughput remains constrained by downstream capacity.

---

### Level 14 — Structured Concurrency

Rewrite an independent-task example using `asyncio.TaskGroup`.

**Objective:** Understand task ownership and group lifecycle.

---

### Level 15 — Model Selection

Given:

- synchronous HTTP library;
- CPU-heavy preprocessing;
- async database driver;
- external LLM with rate limit.

Choose a suitable concurrency strategy per stage.

**Expected skill:** Architecture rather than API memorization.

---

# PART XX — MINI PROJECT

## 65. Mini Project: Concurrent AI Document Processing Simulator

### Scenario

Simulate:

```text
Load document
   ↓
Extraction
   ↓
Embedding API call
   ↓
Storage call
```

Process a configurable number of documents.

### Phase 1 — Sequential

Implement a sequential baseline.

Measure:

- total time;
- completed documents;
- failures.

### Phase 2 — Thread-Based

Use `ThreadPoolExecutor`.

Control:

- worker count;
- exception handling;
- graceful shutdown.

### Phase 3 — Async

Use:

- coroutine functions;
- `create_task()` or `TaskGroup`;
- `gather()`;
- timeout handling.

### Phase 4 — Bounded Concurrency

Add:

```python
asyncio.Semaphore(limit)
```

Measure the effect of different limits.

### Phase 5 — Backpressure

Instead of creating one task for every document immediately, use a bounded queue/worker design.

### Phase 6 — Retry

Add:

- maximum attempts;
- exponential backoff;
- retryable versus non-retryable errors.

Do not allow retries to create an uncontrolled retry storm.

### Phase 7 — Cancellation

Support cancellation of the batch.

Expected behavior:

- stop accepting new work;
- cancel active async work when appropriate;
- release resources;
- preserve clear final state.

### Phase 8 — Metrics

Track:

- submitted;
- completed;
- failed;
- timed out;
- retried;
- cancelled;
- average latency;
- queue depth;
- in-flight count.

### Benchmark methodology

Do not compare only one run.

Run:

- sequential baseline;
- several worker counts;
- several async concurrency limits.

Record:

| Configuration | Runtime | Throughput | Errors | Peak memory |
|---|---:|---:|---:|---:|
| Sequential | measure | measure | measure | measure |
| 2 workers | measure | measure | measure | measure |
| 4 workers | measure | measure | measure | measure |
| Async limit 5 | measure | measure | measure | measure |
| Async limit 20 | measure | measure | measure | measure |

### Expected observations

Possible outcomes:

- concurrency reduces waiting for I/O;
- too much concurrency increases failures;
- rate limits become visible;
- queue size controls memory;
- retries can amplify load;
- the "fastest" configuration is not always the safest production configuration.

### Production improvements

A real system would likely add:

- durable queue;
- idempotency;
- persistence;
- distributed workers;
- observability;
- dead-letter handling;
- authentication;
- service-level limits;
- graceful deployment shutdown.

Do not implement those infrastructure components as part of this vocabulary chapter.

# PART XXI — INTERVIEW QUESTIONS

## 66. Interview Questions

### Beginner

**Q1. What is concurrency?**

Model answer: A way of structuring multiple tasks so their progress can overlap in time. It does not necessarily mean simultaneous CPU execution.

**Q2. What is parallelism?**

Model answer: Actual simultaneous execution of independent work using multiple execution resources.

**Q3. What is a process?**

Model answer: An operating-system execution environment with its own process identity and memory resources.

**Q4. What is a thread?**

Model answer: An execution flow inside a process. Threads in a process normally share memory.

**Q5. What is a coroutine?**

Model answer: A Python async computation produced by an `async def` function, which can suspend at `await`.

**Q6. What is an event loop?**

Model answer: A scheduler/coordinator that manages asynchronous tasks, I/O readiness, timers, and coroutine resumption.

### Intermediate

**Q7. What is the difference between coroutine and Task?**

Model answer: A coroutine object represents async work that can be awaited. A Task schedules a coroutine for execution by the asyncio event loop.

**Q8. What is a Future?**

Model answer: A placeholder for a result that will become available later.

**Q9. Why use a queue?**

Model answer: To decouple producers and consumers and coordinate work safely, often with bounded capacity.

**Q10. Why are threads useful for I/O-bound work?**

Model answer: Threads can overlap waiting in synchronous APIs. They share process memory, which makes communication easy but requires synchronization when mutable state is shared.

**Q11. When might a process pool be appropriate?**

Model answer: For CPU-heavy work where separate processes provide isolation and can use multiple CPU cores, while accounting for process and serialization overhead.

### Advanced

**Q12. What is the GIL?**

Model answer: A CPython implementation mechanism that, in GIL-enabled builds, limits concurrent execution of Python-level bytecode in multiple threads. It does not mean Python lacks parallelism.

**Q13. Why can `asyncio` improve latency?**

Model answer: It can overlap independent I/O waits so one coroutine can suspend while another progresses.

**Q14. What causes a deadlock?**

Model answer: A set of tasks become permanently blocked waiting on resources held by one another, often through circular lock dependencies.

**Q15. What is backpressure?**

Model answer: A control mechanism that prevents producers from overwhelming downstream consumers by limiting, delaying, buffering, or rejecting work.

**Q16. Why can unlimited concurrency be dangerous?**

Model answer: It can exhaust memory, sockets, connection pools, provider quotas, CPU, or downstream capacity.

**Q17. How would you control LLM API concurrency?**

Model answer: Establish an explicit concurrency limit, use timeouts, classify retryable errors, enforce rate limits, apply backpressure, and observe queue/in-flight/error metrics.

**Q18. How would you design cancellation?**

Model answer: Define ownership, cancellation boundaries, cleanup behavior, what downstream operations should be cancelled, and whether partial completion is safe.

---

# PART XXII — PRODUCTION ARCHITECTURE QUESTIONS

## 67. Scenario 1 — LLM API Fan-Out

A request requires five independent external AI calls.

### Analysis questions

- Can the calls truly run independently?
- Are they I/O-bound?
- Is async support available?
- What is the concurrency limit?
- What are provider rate limits?
- What timeout applies?
- What happens if one call fails?
- Should sibling calls continue?
- Can the whole operation be cancelled?

### Reasoning

If calls are independent I/O, concurrency can reduce wall-clock waiting.

A safe design often looks like:

```text
request
  ↓
create bounded concurrent calls
  ↓
collect results
  ↓
validate/aggregate
  ↓
return
```

The design should explicitly define partial-failure behavior.

---

## 68. Scenario 2 — 100,000 Documents

### Questions

- Should the service create 100,000 in-memory tasks?
- Should work be held in RAM?
- Where is the queue?
- What is the concurrency limit?
- What is the retry policy?
- What is the backpressure mechanism?

### Reasoning

At this scale, a durable queue plus workers is often more appropriate than one process trying to keep all work in memory.

The key concept is not "use async". The key concept is:

```text
durable work ownership
→ bounded concurrency
→ retry policy
→ backpressure
→ observability
```

---

## 69. Scenario 3 — CPU-Heavy Preprocessing

Large documents require expensive pure-Python preprocessing.

### Decision

Consider:

- process pool;
- multiprocessing;
- optimized native libraries;
- moving computation to a dedicated service;
- GPU/vectorized execution where appropriate.

Asyncio alone does not turn CPU work into parallel CPU execution.

---

## 70. Scenario 4 — Agent Tool Execution

An agent needs:

```text
Search A
Search B
Database C
Then Tool D using A + B
```

### Reasoning

A/B/C can potentially fan out concurrently if independent.

D must wait for the dependencies it needs.

The graph is:

```text
        ┌→ A ─┐
Request ┼→ B ─┼→ D
        └→ C ─┘
```

Concurrency should follow the **dependency graph**, not an arbitrary "parallelize everything" rule.

---

## 71. Scenario 5 — Production API

A FastAPI service receives high concurrent traffic.

Ask:

- what blocks?
- which dependencies are shared?
- what connection pools exist?
- what are downstream limits?
- how is work queued?
- where is backpressure applied?
- how are requests timed out?
- how does shutdown work?
- what metrics identify overload?

### Reasoning

A robust service needs more than a framework setting.

Think:

```text
admission
→ bounded concurrency
→ downstream limits
→ timeout
→ cancellation
→ queue/backpressure
→ observability
→ graceful shutdown
```

---

# PART XXIII — KNOWLEDGE CHECK

## 72. Knowledge Check

### Terminology

1. Define concurrency.
2. Define parallelism.
3. Define process.
4. Define thread.
5. Define coroutine.
6. Define Task.
7. Define Future.
8. Define event loop.
9. Define race condition.
10. Define deadlock.
11. Define backpressure.

### Code reading

What happens here?

```python
import asyncio

async def work():
    await asyncio.sleep(0.01)
    return 1

async def main():
    coro = work()
    task = asyncio.create_task(work())

    print(type(coro))
    print(task.done())

    result = await task
    print(result)

asyncio.run(main())
```

**Answer:** `coro` is a coroutine object. `task` is a scheduled asyncio Task. The task is initially unfinished, then completes and produces `1`.

### Output prediction

```python
import asyncio

async def work(name, delay):
    await asyncio.sleep(delay)
    print(name)

async def main():
    await asyncio.gather(
        work("slow", 0.2),
        work("fast", 0.1),
    )

asyncio.run(main())
```

**Answer:** `"fast"` is printed before `"slow"` because the second coroutine has the shorter delay.

### Conceptual

**Why can `await` help an I/O-bound program?**

Because the current coroutine can suspend while another task makes progress.

**Why can unlimited `create_task()` calls be dangerous?**

Because every pending task consumes resources and may trigger large downstream load.

**What happens when two threads update shared state?**

Without appropriate synchronization, timing-sensitive interleavings can cause incorrect results.

**What is backpressure?**

A mechanism that limits or slows incoming work so downstream capacity is not overwhelmed.

### Architecture

**What should you measure before increasing concurrency?**

Measure latency, throughput, queue depth, error rate, downstream saturation, worker utilization, resource usage, and ideally the bottleneck itself.

# PART XXIV — IMPORTANT PYTHON APIs

## 73. Asyncio API Coverage

This section is a reference map. Earlier sections provide the main teaching examples.

### `asyncio.run(coro, *, debug=None)`

Runs a top-level coroutine.

Use for application entry points.

### `asyncio.create_task(coro, *, name=None, context=None, eager_start=None, **kwargs)`

Schedules a coroutine as an asyncio Task.

### `asyncio.current_task()`

Returns the currently running Task, when called from an asyncio context.

### `asyncio.all_tasks()`

Returns unfinished tasks associated with the relevant event loop.

Use primarily for diagnostics and advanced orchestration.

### `asyncio.gather(*aws, return_exceptions=False)`

Runs awaitables concurrently and aggregates their results.

`return_exceptions=True` changes exception collection semantics and should be used deliberately.

### `asyncio.wait(aws, *, timeout=None, return_when=...)`

Waits for tasks/futures according to a completion condition.

Common `return_when` values:

- `FIRST_COMPLETED`;
- `FIRST_EXCEPTION`;
- `ALL_COMPLETED`.

### `asyncio.as_completed(aws, *, timeout=None)`

Yields work as it completes, which is useful for completion-order processing.

### `asyncio.sleep(delay, result=None)`

Suspends the current coroutine and optionally returns a specified result.

### `asyncio.wait_for(aw, timeout)`

Runs an awaitable with a timeout.

### `asyncio.timeout(delay)`

An async context manager that applies a timeout to its enclosed awaitable operations.

### `asyncio.shield(aw)`

Protects an awaitable from cancellation of the surrounding task in specific situations.

It does **not** make the work immortal or globally uncancellable; ownership still matters.

### Synchronization classes

- `asyncio.Lock`;
- `asyncio.Event`;
- `asyncio.Condition`;
- `asyncio.Semaphore`;
- `asyncio.BoundedSemaphore`;
- `asyncio.Queue`.

Use these to express state coordination rather than relying on `sleep()` timing.

### `asyncio.Task`

Key APIs include:

- `done()`;
- `result()`;
- `exception()`;
- `cancel()`;
- `cancelled()`;
- `add_done_callback()`;
- `get_name()`;
- `set_name()`.

### `asyncio.Future`

Key APIs include:

- `done()`;
- `result()`;
- `exception()`;
- `cancel()`;
- `cancelled()`;
- `add_done_callback()`;
- `set_result()`;
- `set_exception()`.

### `asyncio.TaskGroup`

Modern structured-concurrency primitive for scoped task ownership.

Added in Python 3.11.

---

## 74. `threading` API Coverage

Relevant public APIs:

### `Thread`

```python
thread = threading.Thread(target=worker)
thread.start()
thread.join()
```

Other useful methods:

- `is_alive()`;
- `name`;
- `native_id` where available;
- `ident`.

### Thread inspection

- `current_thread()`;
- `main_thread()`;
- `enumerate()`;
- `active_count()`.

### Synchronization

- `Lock`;
- `RLock`;
- `Semaphore`;
- `BoundedSemaphore`;
- `Event`;
- `Condition`;
- `Barrier`.

All have different semantics; choose according to the coordination problem.

---

## 75. `queue` API Coverage

### `Queue(maxsize=0)`

Thread-synchronized FIFO queue.

Key methods:

- `put(item, block=True, timeout=None)`;
- `put_nowait(item)`;
- `get(block=True, timeout=None)`;
- `get_nowait()`;
- `task_done()`;
- `join()`;
- `qsize()`;
- `empty()`;
- `full()`.

### `SimpleQueue()`

Simple unbounded FIFO queue.

### `PriorityQueue(maxsize=0)`

Retrieves lowest-priority items first according to item ordering.

### `LifoQueue(maxsize=0)`

LIFO queue.

### Version-sensitive shutdown

Python 3.13+ includes `Queue.shutdown()` and the `queue.ShutDown` exception. These are relevant to modern worker shutdown design.

---

## 76. `concurrent.futures` API Coverage

### `Executor`

Common methods:

- `submit()`;
- `map()`;
- `shutdown()`.

### `ThreadPoolExecutor`

Thread-based executor.

### `ProcessPoolExecutor`

Process-based executor.

### `Future`

Methods:

- `cancel()`;
- `cancelled()`;
- `running()`;
- `done()`;
- `result()`;
- `exception()`;
- `add_done_callback()`.

### Important distinction

`concurrent.futures.Future` is not the same class as `asyncio.Future`.

---

## 77. `multiprocessing` Foundational API Coverage

Relevant `Process` APIs:

- `start()`;
- `join()`;
- `is_alive()`;
- `terminate()`;
- `kill()`;
- `close()`;
- `exitcode`.

The chapter intentionally stops short of a full multiprocessing communication course.

---

# PART XXV — TECHNICAL DISTINCTIONS TO REMEMBER

## 78. The Critical Distinctions

### Concurrency ≠ Parallelism

One is about overlapping progress; the other is about simultaneous execution.

### Async ≠ Parallel CPU execution

Asyncio is primarily a concurrency model for cooperative asynchronous work.

### Thread ≠ Process

Threads share process memory; processes generally have separate memory spaces.

### Coroutine ≠ Task

A coroutine object is awaitable work. A Task schedules that work in asyncio.

### Task ≠ Future

A Task is specialized around coroutine execution; a Future is a lower-level result placeholder.

### Blocking ≠ Awaiting

A blocking call holds its executing thread. Awaiting suspends the current coroutine.

### Queue ≠ Deque

A `collections.deque` is a general data structure. `queue.Queue` is a synchronization-oriented threaded queue.

### Semaphore ≠ Rate limiter

A semaphore controls concurrent entries. A rate limiter may also enforce time-based quotas.

### Python concurrency ≠ distributed concurrency ≠ GPU parallelism

These exist at different system layers.

# PART XXVI — COMMON DESIGN TRADE-OFFS

## 79. Concurrency Trade-Offs

### Simplicity vs concurrency

Sequential code is easier to reason about.

Introduce concurrency only when it solves a measured or clearly understood problem.

### Latency vs throughput

Batching and concurrency can improve throughput but may increase per-request queueing delay.

### Concurrency vs resource usage

More in-flight work consumes more:

- memory;
- connections;
- sockets;
- CPU;
- downstream capacity.

### Threads vs processes

Threads:

- shared memory;
- low communication cost inside one process;
- useful for I/O;
- synchronization required.

Processes:

- stronger isolation;
- useful for CPU-heavy work;
- more overhead;
- serialization/IPC required.

### Async vs synchronous

Async can be highly effective for large numbers of I/O-bound operations when the libraries are async-compatible.

Synchronous code may be simpler and perfectly adequate when:

- request volume is low;
- workload is small;
- dependencies are synchronous anyway;
- latency targets are easily met.

### Shared state vs message passing

Shared state can be convenient but introduces coordination.

Queues/messages make ownership more explicit.

### Retries vs duplicate work

A retry may increase reliability but can produce duplicate operations.

This matters especially for:

- payments;
- mutations;
- external tool calls;
- model jobs;
- message processing.

Idempotency is therefore a distributed-systems concern that concurrency can expose.

### Queue size vs memory

An unbounded queue can turn overload into memory exhaustion.

### Batching vs latency

Batching can improve throughput but may add waiting.

### Cancellation vs completion guarantees

Cancellation makes systems responsive, but some operations may be difficult to safely interrupt. Define the contract explicitly.

# PART XXVII — FINAL DECISION FRAMEWORK

## 80. How to Choose a Concurrency Model

Ask these questions in order.

### 1. What is the bottleneck?

- I/O wait?
- CPU?
- downstream API?
- queue?
- database?
- GPU?

### 2. What is the workload shape?

- one job;
- small batch;
- many independent jobs;
- long-running stream;
- bursty traffic?

### 3. Does the library support async?

If yes, asyncio may be attractive for many I/O-bound operations.

If not, threads or another model may be appropriate.

### 4. Is shared mutable state required?

If yes, define ownership and synchronization.

### 5. Do tasks need isolation?

If yes, processes or service boundaries may be appropriate.

### 6. Do tasks need bounded concurrency?

If yes, add:

- semaphore;
- bounded worker pool;
- queue;
- admission control.

### 7. Are there dependencies between tasks?

Use the dependency graph to identify what can overlap.

### 8. What happens on failure?

Define:

- retries;
- timeout;
- cancellation;
- partial results;
- idempotency.

### 9. What is the shutdown model?

A production service needs graceful shutdown semantics.

### 10. What will you measure?

At minimum consider:

- latency;
- throughput;
- queue depth;
- in-flight work;
- error rate;
- resource usage.

### Practical decision table

| Situation | First concepts to consider |
|---|---|
| Simple script | Sequential |
| Many network requests | Async / threads |
| CPU-heavy Python work | Processes / process pool |
| Shared memory needed | Threads + synchronization |
| Independent async I/O | Tasks |
| Producer-consumer | Queue |
| External API concurrency limit | Semaphore / bounded concurrency |
| Long-running async service | TaskGroup + cancellation + timeouts |
| Too much incoming work | Backpressure |
| Need a result later | Future |
| Need reusable workers | Executor |
| Need isolation | Processes |

This is a starting point, not a rigid rulebook.

---

# PART XXVIII — PYTHON VERSION AND IMPLEMENTATION NOTES

## 81. Version Compatibility

Concurrency APIs evolve.

Important version-sensitive examples include:

- `asyncio.TaskGroup` — added in Python 3.11;
- `asyncio.timeout()` — modern timeout API;
- queue shutdown APIs — added in Python 3.13;
- free-threaded CPython — supported as a distinct build beginning with Python 3.13;
- some async task-creation signatures and cancellation behaviors can change across versions.

### Engineering rule

Pin and test the Python version used by your application.

Never reason about a production runtime only from memory of an older Python release.

### Language versus implementation

Always distinguish:

```text
Python language semantics
        ≠
CPython implementation details
        ≠
specific deployment mode
```

The GIL is the clearest example.

---

# PART XXIX — PRODUCTION ENGINEERING MINDSET

## 82. Production Requirements

Production concurrency should emphasize:

- correctness before optimization;
- bounded concurrency;
- explicit ownership;
- timeouts;
- cancellation;
- retries;
- rate limits;
- backpressure;
- observability;
- memory limits;
- graceful shutdown.

### Failure cascade

```text
Unbounded concurrency
        ↓
Too many requests
        ↓
Rate limits / connection pressure
        ↓
Timeouts
        ↓
Retries
        ↓
Retry storm
        ↓
Queue growth
        ↓
Memory pressure
        ↓
System instability
```

A mature design breaks this chain by controlling each stage.

### A practical control loop

```text
measure
  ↓
identify bottleneck
  ↓
set a limit
  ↓
observe
  ↓
adjust
```

Do not use concurrency as an unmeasured performance ritual.

# PART XXX — DEBUGGING CHALLENGES

## 83. Debugging Challenge 1 — Blocked Event Loop

Broken code:

```python
import asyncio
import time

async def bad_work():
    time.sleep(2)
    return "done"

async def other():
    await asyncio.sleep(0.1)
    print("other finished")

async def main():
    await asyncio.gather(bad_work(), other())

asyncio.run(main())
```

### Diagnose

Why is `other()` delayed?

### Expected reasoning

`time.sleep()` blocks the event-loop thread.

### Corrected direction

Use an async-compatible wait or move blocking work out of the event-loop path.

---

## 84. Debugging Challenge 2 — Unlimited Tasks

Broken pattern:

```python
tasks = [
    asyncio.create_task(call_api(item))
    for item in huge_dataset
]
```

### Diagnose

Identify at least three risks.

### Expected topics

- memory;
- provider overload;
- connection pressure;
- cancellation complexity.

### Corrected direction

Use bounded concurrency or a worker/queue model.

---

## 85. Debugging Challenge 3 — Lock Ordering

Broken pattern:

```python
def a():
    with lock1:
        with lock2:
            pass

def b():
    with lock2:
        with lock1:
            pass
```

### Diagnose

Explain the circular wait.

### Fix direction

Use a consistent lock ordering or redesign ownership.

---

## 86. Debugging Challenge 4 — Forgotten Queue Acknowledgment

Broken:

```python
from queue import Queue

q = Queue()
q.put("job")

job = q.get()
process(job)

q.join()  # can remain blocked
```

### Diagnose

What is missing?

### Answer

`q.task_done()` must be called when the retrieved task has been fully processed.

---

## 87. Debugging Challenge 5 — Ignored Cancellation

Broken idea:

```python
async def worker():
    while True:
        await something()
        do_more_work()
```

The developer cancels the task but cleanup is not specified.

### Diagnose

What lifecycle questions are missing?

### Expected topics

- cleanup;
- cancellation propagation;
- ownership;
- resource release;
- whether external operations can be cancelled.

---

## 88. Debugging Challenge 6 — Retry Storm

Broken architecture:

```text
API gets slow
  ↓
all workers timeout
  ↓
all workers retry immediately
  ↓
API gets even slower
```

### Diagnose

How would you add backpressure?

### Expected topics

- bounded concurrency;
- retry backoff;
- retry budget;
- jitter;
- timeout;
- circuit-breaking concepts where appropriate;
- observability.

# PART XXXI — FINAL PRODUCTION CHECKLIST

## 89. Concurrency Readiness Checklist

Before shipping a concurrent component, ask:

- [ ] Is the workload classified as I/O-bound, CPU-bound, or mixed?
- [ ] Is concurrency actually needed?
- [ ] Is the concurrency level bounded?
- [ ] Is shared mutable state minimized?
- [ ] Is ownership explicit?
- [ ] Are timeouts defined?
- [ ] Is cancellation defined?
- [ ] Are retries bounded?
- [ ] Are rate limits respected?
- [ ] Is backpressure implemented?
- [ ] Can queues grow without bound?
- [ ] Is memory usage observable?
- [ ] Are task leaks possible?
- [ ] Is graceful shutdown defined?
- [ ] Are failure boundaries clear?
- [ ] Is the design tested under stress?
- [ ] Are downstream systems protected?
- [ ] Are logs traceable with request/task IDs?
- [ ] Are performance claims based on measurement?
- [ ] Is implementation-specific behavior clearly documented?

---

# PART XXXI-A — ASYNC PRIMITIVE API DETAILS

## 89-A. `asyncio.Queue` Methods

An `asyncio.Queue` is the async counterpart of the producer-consumer idea discussed earlier.

Common operations include:

- `put(item)` — asynchronously waits until an item can be inserted;
- `put_nowait(item)` — attempts insertion without waiting;
- `get()` — asynchronously waits for an item;
- `get_nowait()` — attempts retrieval without waiting;
- `task_done()` — marks a previously retrieved item as processed;
- `join()` — waits until all tracked items are marked done;
- `qsize()` — reports the current size;
- `empty()` — reports whether the queue currently appears empty;
- `full()` — reports whether the bounded queue is currently full.

Example:

```python
import asyncio

async def producer(queue):
    for item in range(3):
        await queue.put(item)

async def consumer(queue):
    while True:
        item = await queue.get()
        try:
            print("processing", item)
        finally:
            queue.task_done()
        if item == 2:
            break

async def main():
    queue = asyncio.Queue(maxsize=2)

    producer_task = asyncio.create_task(producer(queue))
    consumer_task = asyncio.create_task(consumer(queue))

    await producer_task
    await queue.join()
    await consumer_task

asyncio.run(main())
```

The important lesson is ownership: a retrieved item should eventually receive its corresponding `task_done()` call.

---

## 89-B. Async Synchronization Method Vocabulary

The classes listed earlier have method-level semantics that matter:

### `asyncio.Lock`

Core operations:

- `acquire()`;
- `release()`;
- `locked()`;
- `async with lock`.

### `asyncio.Event`

Core operations:

- `set()`;
- `clear()`;
- `is_set()`;
- `wait()`.

### `asyncio.Semaphore`

Core operations:

- `acquire()`;
- `release()`;
- `locked()`.

Use a semaphore to limit simultaneous access to a constrained resource.

### `asyncio.BoundedSemaphore`

Uses the semaphore model while enforcing the configured upper bound on releases.

### `asyncio.Condition`

Key concepts include:

- `acquire()`;
- `release()`;
- `wait()`;
- `notify()`;
- `notify_all()`.

A condition is appropriate when code needs to wait for a state change while coordinating access to shared state.

### Why method-level knowledge matters

Do not memorize:

```text
"asyncio.Lock = synchronization"
```

as the complete model.

Know what the program actually does:

```text
acquire
   ↓
protected state transition
   ↓
release
```

and:

```text
wait for condition
   ↓
state changes
   ↓
notification
   ↓
re-check condition
```

The synchronization primitive expresses the coordination rule; the application still owns the correctness policy.
# PART XXXII — FINAL CONCURRENCY VOCABULARY MAP

## 90. Vocabulary Map

```text
Concurrency
├── Threads
│   ├── Shared memory
│   ├── Locks
│   ├── Race conditions
│   └── ThreadPoolExecutor
│
├── Async
│   ├── Coroutine
│   ├── Awaitable
│   ├── Task
│   ├── Future
│   ├── Event Loop
│   ├── Semaphore
│   ├── Queue
│   └── TaskGroup
│
└── Processes
    ├── Isolation
    ├── multiprocessing
    └── ProcessPoolExecutor
```

### System reasoning map

```text
Workload
   ↓
I/O-bound or CPU-bound?
   ↓
Dependencies?
   ↓
Shared state?
   ↓
Concurrency model
   ↓
Synchronization
   ↓
Timeouts
   ↓
Cancellation
   ↓
Backpressure
   ↓
Observability
```

This is the mental path you should take before selecting a Python concurrency primitive.

---

# PART XXXIII — IF YOU REMEMBER ONLY 20 THINGS

## 91. If You Remember Only 20 Things

1. **Concurrency is not the same as parallelism.**
2. **Async does not automatically mean parallel CPU execution.**
3. **Classify the workload before choosing a model.**
4. **I/O-bound and CPU-bound workloads stress different resources.**
5. **Threads share process memory.**
6. **Processes generally provide separate memory spaces and stronger isolation.**
7. **A coroutine is not automatically a Task.**
8. **The event loop coordinates asynchronous work.**
9. **`await` suspends the current coroutine rather than necessarily blocking the whole program.**
10. **Blocking calls can stall an event loop.**
11. **Unlimited concurrency is dangerous.**
12. **Shared mutable state creates correctness risks.**
13. **Synchronization protects correctness; it is not free.**
14. **Queues are powerful producer-consumer boundaries.**
15. **Timeouts prevent indefinite ownership of scarce resources.**
16. **Cancellation must be designed, not assumed.**
17. **Backpressure protects downstream capacity and memory.**
18. **The GIL is a CPython implementation concern, not a statement that Python has no parallelism.**
19. **More workers do not automatically mean more performance.**
20. **Production concurrency requires limits, observability, failure handling, and graceful shutdown.**

---

# PART XXXIV — FINAL MENTAL MODEL

## 92. Final Mental Model

Think about a concurrent system as a set of work units moving through controlled execution.

```text
Work
 ↓
Classify workload
 ↓
Identify dependencies
 ↓
Choose execution model
 ↓
Schedule
 ↓
Synchronize
 ↓
Bound concurrency
 ↓
Apply timeout
 ↓
Handle cancellation
 ↓
Apply backpressure
 ↓
Observe
 ↓
Measure and tune
```

### One final distinction

When you hear:

> "We need concurrency."

do not immediately choose `asyncio`.

Ask:

1. What work is being done?
2. What is it waiting for?
3. Can operations overlap safely?
4. What resource is scarce?
5. How many operations can be in flight?
6. What happens if one fails?
7. What happens if the caller cancels?
8. How does the system shut down?
9. How is overload controlled?
10. How will success be measured?

That is the beginning of production concurrency reasoning.

---

# Appendix A — Compact API Reference

| API / Type | Core idea | Typical use |
|---|---|---|
| `asyncio.run()` | Run top-level coroutine | Async application entry point |
| `asyncio.create_task()` | Schedule coroutine | Independent async work |
| `asyncio.gather()` | Await many results | Fan-out/fan-in |
| `asyncio.wait()` | Wait by completion condition | Advanced task coordination |
| `asyncio.as_completed()` | Consume completion order | Streaming result handling |
| `asyncio.sleep()` | Async suspension | Delays/backoff/simulation |
| `asyncio.timeout()` | Timeout scope | External dependencies |
| `asyncio.wait_for()` | Timeout one awaitable | Time-bounded operation |
| `asyncio.shield()` | Protect awaitable from outer cancellation | Specialized cancellation control |
| `asyncio.Lock` | Async mutual exclusion | Shared coroutine state |
| `asyncio.Semaphore` | Bound concurrent entries | API/worker limits |
| `asyncio.Queue` | Async producer-consumer | Pipelines/work queues |
| `asyncio.TaskGroup` | Structured concurrency | Owned child tasks |
| `threading.Thread` | OS-thread execution | I/O-bound sync work |
| `threading.Lock` | Thread mutual exclusion | Shared state |
| `queue.Queue` | Synchronized FIFO | Thread workers |
| `Process` | Separate process | Isolated/CPU-heavy work |
| `ThreadPoolExecutor` | Thread worker pool | Blocking I/O / sync callables |
| `ProcessPoolExecutor` | Process worker pool | CPU-heavy work |
| `Future` | Future result placeholder | Executor result handling |

---

# Appendix B — Suggested Progression After This Chapter

This chapter is vocabulary-first.

A natural next progression is:

```text
Vocabulary
   ↓
Asyncio programming
   ↓
Threading in depth
   ↓
Multiprocessing
   ↓
Synchronization
   ↓
Distributed systems
   ↓
Message queues
   ↓
Production worker architecture
   ↓
AI inference orchestration
   ↓
AI infrastructure
```

The purpose of this chapter is to make the later topics easier to reason about.

---

# References and Version Notes

Use the Python documentation for the exact API contract of the Python version being deployed:

- Python `asyncio` tasks and TaskGroup:
  https://docs.python.org/3/library/asyncio-task.html
- Python `threading`:
  https://docs.python.org/3/library/threading.html
- Python `queue`:
  https://docs.python.org/3/library/queue.html
- Python `concurrent.futures`:
  https://docs.python.org/3/library/concurrent.futures.html
- Python `multiprocessing`:
  https://docs.python.org/3/library/multiprocessing.html

For implementation-sensitive topics, especially the GIL and free-threaded CPython, consult the current CPython documentation for the deployment build you actually use.

> **Final rule:** Choose concurrency based on **workload, access pattern, dependencies, capacity, correctness requirements, and measured behavior** — not because a particular concurrency technology is fashionable.
