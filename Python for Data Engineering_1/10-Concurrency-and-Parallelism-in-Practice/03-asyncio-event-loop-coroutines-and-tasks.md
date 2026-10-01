# Asyncio: Event Loop, Coroutines, and Tasks

> **Stage 2 --- Python for Data Engineering**\
> **Module 2.10 --- Concurrency and Parallelism in Practice**\
> **Phase B --- asyncio**

**Core principle:** Concurrency is a tool, not a goal. Start from a
sequential baseline, classify the work, bound everything, never lose an
error, shut down cleanly, and prove the speed-up.

## Learning Objectives

By the end of this chapter, you should be able to explain and
demonstrate:

-   why asynchronous programming exists;
-   sequential versus concurrent execution;
-   CPU-bound versus I/O-bound work;
-   blocking versus non-blocking operations;
-   coroutine functions and coroutine objects;
-   `async def` and `await`;
-   awaitables, Tasks, Futures, and the event loop;
-   cooperative scheduling;
-   `asyncio.create_task()` and `asyncio.gather()`;
-   task lifecycle, ownership, exceptions, and references;
-   async context managers, iterators, and generators;
-   why blocking work damages an event loop;
-   `asyncio.to_thread()` and `run_in_executor()`;
-   the sync/async function boundary;
-   async database access and connection pools;
-   asyncio applications in Data Engineering;
-   when asyncio does not help;
-   how asyncio relates to threads and processes;
-   debugging, testing, measurement, and production design.

------------------------------------------------------------------------

# 1. Introduction

`asyncio` is Python's standard-library framework for writing concurrent
programs around an event loop, coroutines, and tasks.

The problem it addresses is **waiting**. Data Engineering programs
frequently wait for HTTP APIs, databases, object storage, sockets,
external services, and timers.

A useful real-world analogy is a worker handling many I/O requests. The
worker should not stand idle while one external system is responding if
other independent work can make progress.

``` text
Start A
  |
  | A waits for network response
  v
Start B
  |
  | B waits
  v
Start C
  |
  v
Resume whichever operation becomes ready
```

The analogy is only intuition. Technically, asyncio commonly uses one
event-loop thread that cooperatively schedules many tasks.

## Why this matters in Data Engineering

A typical ingestion workflow may contact:

``` text
customers API
orders API
products API
payments API
metadata service
database
object storage
```

If these operations are independent and dominated by network waiting,
asynchronous concurrency may reduce wall-clock time.

It is not automatically faster. A database bottleneck, rate limit,
CPU-heavy transformation, storage bottleneck, or excessive task overhead
can make more concurrency useless or harmful.

------------------------------------------------------------------------

# 2. The Problem: Waiting

Start with ordinary synchronous Python:

``` python
import time


def fetch(name):
    print(f"Starting {name}")
    time.sleep(2)
    print(f"Finished {name}")


fetch("A")
fetch("B")
fetch("C")
```

The execution is approximately:

``` text
A: [start ===== wait ===== finish]
B:                          [start ===== wait ===== finish]
C:                                                    [start ===== wait ===== finish]
```

Total wall-clock time is approximately:

``` text
2 + 2 + 2 = 6 seconds
```

ignoring small overhead.

During `sleep`, the current thread cannot make progress on the next
call.

Important terms:

  Term              Meaning
  ----------------- -----------------------------------------------
  CPU work          Computation performed by the processor
  I/O latency       Time spent waiting for an external system
  Blocking          Current execution cannot make useful progress
  Wall-clock time   Real elapsed time
  Throughput        Work completed per unit time

The first engineering question is therefore:

> **What is the program actually waiting for?**

------------------------------------------------------------------------

# 3. CPU-Bound vs I/O-Bound

## CPU-bound work

CPU-bound work spends most of its time computing.

Examples:

-   compression;
-   encryption;
-   expensive calculations;
-   complex pure-Python transformations;
-   CPU-heavy parsing;
-   expensive Python loops.

``` text
Input -> CPU computation -> Output
```

## I/O-bound work

I/O-bound work spends substantial time waiting for an external system.

Examples:

-   HTTP API requests;
-   database queries;
-   object storage;
-   network calls;
-   external services;
-   file or stream waits.

``` text
Python -> external system -> wait -> response
```

Asyncio primarily targets I/O-bound concurrency.

  -----------------------------------------------------------------------
  Work type       Main bottleneck         Asyncio usually Typical
                                                   helps? alternative
  --------------- ------------------ -------------------- ---------------
  HTTP requests   Network wait                      Often Threads

  DB queries      Network/database                  Often Async driver or
                  wait                                    threads

  CPU-heavy       CPU                          Usually no Processes /
  Python                                                  suitable native
                                                          execution

  Native NumPy    Native CPU                      Depends Library-level
  work                                                    parallelism

  File/network    I/O wait                          Often Async APIs or
  I/O                                                     threads
  -----------------------------------------------------------------------

Do not treat this table as a universal rule. Always measure the real
workload.

------------------------------------------------------------------------

# 4. Synchronous vs Concurrent Execution

Sequential execution:

``` text
Task A
  |
  v
wait
  |
  v
Task B
  |
  v
wait
  |
  v
Task C
```

Concurrent execution:

``` text
Start A ---- wait ---------------- resume A
       \
        +-- Start B ---- wait ----- resume B
             \
              +-- Start C -- wait -- resume C
```

Concurrency means multiple units of work can make progress during
overlapping periods.

Parallelism means multiple units of work execute at the same time,
typically using multiple execution resources.

Asyncio can provide concurrency without requiring multiple CPU cores.

A crucial distinction:

``` text
Concurrency != Parallelism
```

Do not describe asyncio as "doing many CPU operations simultaneously on
one CPU."

------------------------------------------------------------------------

# 5. What Is Asynchronous Programming?

### Beginner explanation

Asynchronous programming lets a task effectively say:

> "I cannot make useful progress right now. I am waiting. Let other work
> run and return to me when my operation is ready."

### Technical explanation

An asynchronous coroutine can suspend at an `await` point. The event
loop can then execute other ready work.

Key concepts:

-   **asynchronous operation** --- work whose completion can be awaited;
-   **non-blocking** --- does not prevent the event-loop thread from
    servicing other work;
-   **suspension** --- coroutine temporarily stops executing;
-   **resumption** --- coroutine continues later;
-   **cooperative scheduling** --- coroutines yield through suspension
    points;
-   **event loop** --- scheduler coordinating asynchronous work.

Typical model:

``` text
One event-loop thread
       |
       +--> Task A
       +--> Task B
       +--> Task C
       +--> timers
       +--> I/O readiness
```

The event loop is only useful if tasks cooperate. A long blocking
operation on its thread can stop other tasks from progressing.

------------------------------------------------------------------------

# 6. Your First Async Function

``` python
async def fetch():
    print("hello")
```

`async def` defines a **coroutine function**.

Calling it produces a **coroutine object**:

``` python
result = fetch()
print(result)
```

The body does not execute like an ordinary synchronous function call.

A top-level application can execute it with:

``` python
import asyncio


async def fetch():
    print("hello")


asyncio.run(fetch())
```

At a high level, `asyncio.run()`:

1.  creates/manages an event loop;
2.  runs the supplied top-level coroutine;
3.  finalizes asynchronous generators;
4.  performs loop shutdown;
5.  closes the loop.

------------------------------------------------------------------------

# 7. Coroutines and Their Runtime Sequence

Consider:

``` python
import asyncio


async def fetch():
    print("start")
    await asyncio.sleep(2)
    print("finish")


asyncio.run(fetch())
```

The runtime sequence is:

``` text
1. Define coroutine function
2. Call fetch()
3. Create coroutine object
4. asyncio.run() starts the async execution environment
5. Event loop schedules the coroutine
6. Coroutine prints "start"
7. Coroutine reaches await
8. Coroutine suspends
9. Event loop waits for timer readiness while servicing other work
10. Timer becomes ready
11. Coroutine resumes
12. Coroutine prints "finish"
13. Coroutine completes
14. asyncio.run() finalizes the run
```

A useful lifecycle is:

``` text
running
   |
   | await operation not ready
   v
waiting
   |
   | operation ready
   v
runnable
   |
   v
running
   |
   v
completed
```

------------------------------------------------------------------------

# 8. Understanding `await`

`await` is central to asyncio.

``` python
result = await something
```

### Beginner explanation

The current coroutine says:

> "I need this asynchronous result before I continue. While I am
> waiting, let the event loop run other ready work."

### Technical explanation

`await` suspends the current coroutine until an **awaitable** completes.

Important awaitable categories include:

-   coroutine objects;
-   `asyncio.Task`;
-   `asyncio.Future`;
-   compatible objects implementing the awaitable protocol.

A useful conceptual relationship is:

``` text
Coroutine
    |
    | scheduled as
    v
Task
    |
    v
event-loop scheduling machinery
    |
    v
Future/readiness/result
```

Do not interpret:

``` python
await something
```

as:

> "Run this in parallel."

It means the current coroutine waits for an awaitable while giving the
event loop an opportunity to progress other work.

Compare:

``` python
await asyncio.sleep(2)
```

with:

``` python
import time
time.sleep(2)
```

The first suspends asynchronously. The second blocks the current thread.

------------------------------------------------------------------------

# 9. The Event Loop

The event loop is the central scheduler.

``` text
                 +------------------+
                 |    Event Loop    |
                 +------------------+
                    |    |     |
                    v    v     v
                  Task A Task B Task C
                    |      |      |
                 waiting  ready  waiting
                    |             |
                    +------^------+
                           |
                    I/O / timer ready
```

Conceptually, it repeatedly handles:

-   ready tasks;
-   timers;
-   I/O readiness;
-   callbacks;
-   suspended tasks whose awaited operations became ready.

When a coroutine reaches an await:

``` text
Task starts
    |
    v
Coroutine runs
    |
    v
await
    |
    v
Coroutine suspends
    |
    v
Event loop runs other ready tasks
    |
    v
I/O/timer becomes ready
    |
    v
Task becomes runnable
    |
    v
Coroutine resumes
    |
    v
Task completes
```

This is **cooperative scheduling**.

A coroutine must reach a suspension point for the event loop to regain
control.

------------------------------------------------------------------------

# 10. Cooperative Multitasking

Good:

``` python
async def good():
    await asyncio.sleep(1)
```

Bad:

``` python
import time


async def bad():
    time.sleep(1)
```

The second function is declared asynchronous but performs a blocking
operation.

If `bad()` runs on the event-loop thread:

``` text
Task A
  |
  | time.sleep(1)
  v
EVENT LOOP BLOCKED
  |
  +--> Task B waits
  +--> Task C waits
  +--> other callbacks wait
```

Compare this with preemptive thread scheduling:

  Property          Typical threads        asyncio
  ----------------- ---------------------- -----------------------------
  Scheduler         OS/runtime             Event loop
  Yield             May be preemptive      Cooperative
  Blocking call     Blocks that thread     Can block whole loop thread
  Common strength   General blocking I/O   Async I/O concurrency

The consequence is important:

> Asyncio makes blocking mistakes more visible because one blocking call
> can affect many logical tasks sharing the event loop.

------------------------------------------------------------------------

# 11. First Concurrent Async Program

Start with:

``` python
import asyncio


async def work(name):
    print(f"start {name}")
    await asyncio.sleep(2)
    print(f"finish {name}")
```

Sequential async execution is still sequential:

``` python
async def main():
    await work("A")
    await work("B")
    await work("C")


asyncio.run(main())
```

Approximate duration: 6 seconds.

Now schedule tasks:

``` python
async def main():
    task_a = asyncio.create_task(work("A"))
    task_b = asyncio.create_task(work("B"))
    task_c = asyncio.create_task(work("C"))

    await task_a
    await task_b
    await task_c
```

The tasks can overlap their waits:

``` text
0s                         2s
|--------------------------|
A: start --------wait------finish
B: start --------wait------finish
C: start --------wait------finish
```

The result is approximately 2 seconds for the simulated workload, rather
than 6 seconds.

That speed-up comes from overlapping waiting, not CPU parallelism.

------------------------------------------------------------------------

# 12. Tasks

An asyncio Task is an independently scheduled execution of a coroutine.

``` python
task = asyncio.create_task(work())
```

Conceptual lifecycle:

``` text
created
  |
  v
scheduled
  |
  v
running
  |
  +---- await ----> waiting
  |                   |
  |                   v
  |                runnable
  |                   |
  +-------------------+
  |
  +---- success ----> completed
  |
  +---- exception --> failed
  |
  +---- cancellation -> cancelled
```

A Task can eventually contain:

-   a successful result;
-   an exception;
-   cancellation state.

Tasks matter because they give asynchronous work an explicit lifecycle
and identity.

------------------------------------------------------------------------

# 13. `asyncio.create_task()`

`create_task()` schedules a coroutine as a Task.

``` python
import asyncio


async def fetch(name):
    print(f"start {name}")
    await asyncio.sleep(1)
    print(f"finish {name}")
    return name


async def main():
    task1 = asyncio.create_task(fetch("A"))
    task2 = asyncio.create_task(fetch("B"))

    result1 = await task1
    result2 = await task2

    print(result1, result2)


asyncio.run(main())
```

Use it when independent work should be scheduled concurrently.

Do not use it merely because an operation is asynchronous.

If B depends on A:

``` python
a = await fetch_a()
b = await fetch_b(a)
```

creating both concurrently may be incorrect.

Concurrency must preserve business dependencies.

------------------------------------------------------------------------

# 14. `await` vs `create_task()`

``` python
await fetch("A")
await fetch("B")
```

means:

``` text
A completes
   |
   v
B starts
```

By contrast:

``` python
task_a = asyncio.create_task(fetch("A"))
task_b = asyncio.create_task(fetch("B"))

await task_a
await task_b
```

schedules both before waiting for their results.

  Concern                          `await coroutine()`   `create_task(coroutine())`
  -------------------------------- --------------------- --------------------------------
  Creates independent Task         No                    Yes
  Explicit concurrent scheduling   No                    Yes
  Lifecycle object                 Coroutine execution   Task
  Error ownership                  Current await         Task result/exception
  Good for dependencies            Yes                   Only when concurrency is valid

The important question is:

> Should these operations overlap?

------------------------------------------------------------------------

# 15. `asyncio.gather()`

`gather()` is a convenient way to await multiple operations.

``` python
import asyncio


async def fetch(name):
    await asyncio.sleep(1)
    return name


async def main():
    results = await asyncio.gather(
        fetch("A"),
        fetch("B"),
        fetch("C"),
    )
    print(results)


asyncio.run(main())
```

`gather()` returns results in input order.

Even if completion order is:

``` text
B -> C -> A
```

the result list is:

``` text
[A, B, C]
```

With independent operations, this is useful for deterministic result
association.

## Exceptions

Ordinary gather:

``` python
try:
    results = await asyncio.gather(
        fetch("A"),
        fetch("B"),
        fetch("C"),
    )
except Exception as exc:
    print(f"failure: {exc}")
```

Collection-style handling:

``` python
results = await asyncio.gather(
    fetch("A"),
    fetch("B"),
    fetch("C"),
    return_exceptions=True,
)
```

With `return_exceptions=True`, exceptions can appear as values:

``` python
[
    "A",
    ValueError("B failed"),
    "C",
]
```

Inspect them explicitly:

``` python
for result in results:
    if isinstance(result, Exception):
        print(f"failure: {result}")
```

This chapter introduces the behavior. Structured cancellation and
`TaskGroup` belong to the next lesson.

------------------------------------------------------------------------

# 16. Exception Handling

A failed Task stores an exception.

``` python
import asyncio


async def failing():
    raise ValueError("something failed")
```

If scheduled:

``` python
task = asyncio.create_task(failing())
```

the exception is associated with the task.

Awaiting it propagates the failure:

``` python
try:
    await task
except ValueError as exc:
    print(f"caught: {exc}")
```

A production system must make failures visible.

``` text
Task
 |
 +--> result
 |
 +--> exception
 |
 +--> cancellation
```

Do not create asynchronous work without deciding how its result and
failure state will be observed.

------------------------------------------------------------------------

# 17. Task References and Lifetime

Explicit background tasks should have an ownership model.

A useful pattern is:

``` python
background_tasks = set()


def start_background_work():
    task = asyncio.create_task(background_work())
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)
```

The point is not to memorize a garbage-collection myth.

The point is lifecycle ownership:

``` text
Who created the task?
Who observes its result?
Who observes its exception?
Who decides when it may stop?
What resources does it depend on?
```

For production systems, background work must not become invisible work.

------------------------------------------------------------------------

# 18. Async Context Managers

Asynchronous resources may need asynchronous acquisition and cleanup.

``` python
import httpx


async def fetch():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://example.com")
        response.raise_for_status()
        return response.text
```

The structure is:

``` text
async with resource
       |
       v
acquire
       |
       v
use
       |
       v
cleanup
```

This matters for:

-   HTTP clients;
-   database connections;
-   cursors;
-   sockets;
-   streams.

Repeatedly creating clients for every request can waste connection setup
and prevent useful connection reuse.

Detailed HTTP extraction belongs to the dedicated HTTP lesson.

------------------------------------------------------------------------

# 19. Async Iterators

An async iterator can obtain the next value asynchronously.

Relevant protocol concepts:

-   `__aiter__()`;
-   `__anext__()`;
-   `StopAsyncIteration`;
-   `async for`.

Example:

``` python
import asyncio


class AsyncCounter:
    def __init__(self, limit):
        self.current = 0
        self.limit = limit

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.current >= self.limit:
            raise StopAsyncIteration

        value = self.current
        self.current += 1

        await asyncio.sleep(0.1)
        return value


async def main():
    async for value in AsyncCounter(5):
        print(value)


asyncio.run(main())
```

Async iteration is useful when producing the next value may require I/O
or another asynchronous wait.

------------------------------------------------------------------------

# 20. Async Generators

An async generator uses `async def` and `yield`.

``` python
import asyncio


async def generate_records():
    for i in range(10):
        await asyncio.sleep(0.1)
        yield i


async def main():
    async for record in generate_records():
        print(record)


asyncio.run(main())
```

This supports incremental streaming:

``` text
API pagination
      |
      v
async generator
      |
      v
record
      |
      v
processing
      |
      v
storage
```

Instead of materializing all records first, the consumer can process
values incrementally.

This is especially useful for Data Engineering workloads involving:

-   API pagination;
-   streaming responses;
-   incremental record processing;
-   memory-sensitive pipelines.

------------------------------------------------------------------------

# 21. The Most Important Rule: Never Block the Event Loop

Bad:

``` python
async def bad():
    time.sleep(5)
```

Good:

``` python
async def good():
    await asyncio.sleep(5)
```

The difference is architectural.

Blocking operations that can damage event-loop responsiveness include:

-   `time.sleep()`;
-   synchronous HTTP clients;
-   synchronous database drivers;
-   blocking cloud SDK calls;
-   blocking file operations;
-   CPU-heavy transformations;
-   compression;
-   expensive parsing;
-   long pure-Python loops.

Simply writing:

``` python
async def function():
    blocking_call()
```

does **not** make `blocking_call()` asynchronous.

A useful diagnostic question is:

> "What exactly is this line doing while the event loop is supposed to
> be serving other tasks?"

------------------------------------------------------------------------

# 22. Detecting Blocking Code

Enable asyncio debug mode:

``` bash
PYTHONASYNCIODEBUG=1 python app.py
```

or:

``` python
import asyncio


async def main():
    ...


asyncio.run(main(), debug=True)
```

Debugging workflow:

``` text
Measure
  |
  v
Inspect event-loop behavior
  |
  v
Find synchronous/blocking calls
  |
  v
Measure individual operations
  |
  v
Inspect CPU and I/O
  |
  v
Inspect pool/service limits
  |
  v
Compare against sequential baseline
```

Useful evidence includes:

-   slow callbacks;
-   event-loop latency;
-   operation timings;
-   CPU utilization;
-   network latency;
-   database latency;
-   task counts;
-   connection-pool utilization.

An application can contain `async def` everywhere and still behave
almost synchronously if blocking operations dominate.

------------------------------------------------------------------------

# 23. `asyncio.to_thread()`

For a suitable blocking synchronous operation:

``` python
await asyncio.to_thread(blocking_function)
```

Example:

``` python
import asyncio
import time


def blocking_operation():
    time.sleep(2)
    return "done"


async def main():
    result = await asyncio.to_thread(
        blocking_operation
    )
    print(result)


asyncio.run(main())
```

Mental model:

``` text
Event-loop thread
       |
       | await to_thread(...)
       v
worker thread
       |
       | blocking function
       v
result
       |
       v
event loop resumes
```

Useful for:

-   legacy synchronous libraries;
-   blocking adapters;
-   suitable filesystem work;
-   synchronous SDKs.

It is not a universal CPU-parallelism mechanism.

Consider:

-   thread overhead;
-   thread safety;
-   shared state;
-   library behavior;
-   CPU characteristics.

------------------------------------------------------------------------

# 24. `run_in_executor()`

A more explicit executor bridge is:

``` python
loop = asyncio.get_running_loop()

result = await loop.run_in_executor(
    None,
    blocking_function,
)
```

Explicit thread-pool example:

``` python
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time


def blocking_function():
    time.sleep(1)
    return "done"


async def main():
    loop = asyncio.get_running_loop()

    with ThreadPoolExecutor(max_workers=4) as executor:
        result = await loop.run_in_executor(
            executor,
            blocking_function,
        )

    print(result)


asyncio.run(main())
```

Conceptually:

``` text
asyncio event loop
       |
       +--> ThreadPoolExecutor
       |
       +--> ProcessPoolExecutor
```

`to_thread()` is convenient for simple blocking thread work.
`run_in_executor()` is useful when explicit executor control matters.

Detailed process execution belongs to the preceding lesson.

# 25. The Sync/Async "Function Color" Problem

Async behavior often propagates through a call stack.

``` python
async def fetch():
    ...


async def process():
    data = await fetch()
    return data
```

Because `fetch()` is asynchronous, callers often become asynchronous
too:

``` text
async main()
    |
    v
async process()
    |
    v
async fetch()
```

This is sometimes called the "function color" problem.

The practical consequence is that async design affects:

-   libraries;
-   application APIs;
-   tests;
-   service boundaries;
-   CLI entry points.

Incorrect:

``` python
def process():
    data = fetch()
```

Correct inside an async boundary:

``` python
async def process():
    data = await fetch()
    return data
```

At a synchronous application boundary, a top-level runner such as
`asyncio.run()` can bridge into the async part.

The key design question is:

> Where should synchronous and asynchronous execution meet?

------------------------------------------------------------------------

# 26. Async Database Access

Async database access allows database/network waits to cooperate with
the event loop.

Relevant concepts:

-   synchronous database driver;
-   asynchronous database driver;
-   async connection;
-   async cursor;
-   async query;
-   async connection pool.

A conceptual PostgreSQL example using modern `psycopg` async APIs:

``` python
import asyncio
import psycopg


async def main():
    async with await psycopg.AsyncConnection.connect(
        "postgresql://..."
    ) as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT 1")
            row = await cur.fetchone()
            print(row)


asyncio.run(main())
```

Execution flow:

``` text
async main()
    |
    v
acquire async connection
    |
    v
execute query
    |
    v
await database/network operation
    |
    | event loop can progress other tasks
    v
database response
    |
    v
resume coroutine
    |
    v
fetch result
    |
    v
cleanup
```

## Async connection pools

A pool creates a reusable set of connections:

``` text
             Connection Pool
          +-------------------+
Task A -->| Connection 1      |
Task B -->| Connection 2      |
Task C -->| Connection 3      |
          | ...               |
          | Connection N      |
          +-------------------+
                    |
                    v
                PostgreSQL
```

If the pool has 10 connections, creating 1,000 tasks does not create
1,000 simultaneous database connections.

The pool is a capacity boundary.

This becomes central in the later bounded-concurrency lesson.

------------------------------------------------------------------------

# 27. Async Resource Management

Use the lifecycle:

``` text
Acquire
   |
   v
Use
   |
   v
Cleanup
```

Common resources:

  Resource        Acquisition   Use          Cleanup
  --------------- ------------- ------------ ---------
  HTTP client     Open client   Requests     Close
  DB connection   Acquire       Queries      Release
  Cursor          Create        Fetch        Close
  Socket          Connect       Read/write   Close
  Stream          Open          Consume      Close

Prefer structured lifecycle management:

``` python
async with resource:
    ...
```

The production goal is not merely "avoid leaks." It is predictable
ownership.

A task should not accidentally outlive:

-   its HTTP client;
-   its database connection;
-   its output stream;
-   its parent workflow.

------------------------------------------------------------------------

# 28. Asyncio and Data Engineering

Asyncio is most useful when the workflow spends substantial time waiting
for external systems.

## 28.1 SaaS API extraction

A conceptual architecture:

``` text
                  Async tasks
                      |
        +-------------+-------------+
        |             |             |
        v             v             v
   customers       orders       products
        |             |             |
        +-------------+-------------+
                      |
                      v
                 JSON records
                      |
                      v
                  processing
                      |
                      v
                   landing
```

Why asyncio may help:

-   network latency is significant;
-   requests are independent;
-   an async-compatible client exists;
-   the service permits useful concurrency.

Risks:

-   rate limits;
-   server capacity;
-   authentication;
-   retries;
-   pagination dependencies;
-   downstream write capacity.

Detailed HTTP extraction, retries, and rate limiting belong to the later
HTTP module.

## 28.2 Multi-endpoint ingestion

Suppose a pipeline needs:

``` text
customers
orders
products
payments
subscriptions
```

If they are independent, their network waits can overlap.

If the workflow is actually:

``` text
customer
   |
   v
customer-specific token
   |
   v
customer orders
```

then there is a dependency and concurrency must respect it.

## 28.3 Database extraction

Async database drivers can help when many independent operations spend
time waiting on the database/network.

But if the database is saturated:

``` text
more asyncio
     |
     v
more queries
     |
     v
more database contention
     |
     v
worse throughput
```

Asyncio cannot create database capacity.

## 28.4 Object storage

Network-bound object operations can often overlap when the client
supports async I/O.

The bottlenecks may instead be:

-   bandwidth;
-   object-store request limits;
-   connection limits;
-   downstream processing.

## 28.5 File ingestion

Do not force local file operations into an async abstraction without a
reason.

Depending on the workload, ordinary synchronous file I/O or
`to_thread()` may be more appropriate.

## 28.6 Metadata collection

A platform may query multiple independent systems:

``` text
catalog A
database B
catalog C
storage D
API E
```

These are often latency-heavy and independent, making async
orchestration a reasonable candidate.

------------------------------------------------------------------------

# 29. Asyncio vs Threading vs Processes

  -------------------------------------------------------------------------------------------------------------------------
  Model                 Primary use     Scheduling    CPU-bound Python  I/O-bound   Memory      Complexity   Data
                                                                        work                                 Engineering
                                                                                                             use
  --------------------- --------------- ------------- ----------------- ----------- ----------- ------------ --------------
  ThreadPoolExecutor    Blocking        Threads       Limited by        Strong      Shared      Moderate     Legacy SDKs,
                        synchronous                   runtime                                                blocking I/O
                        work                          characteristics                                        

  ProcessPoolExecutor   CPU-heavy work  Processes     Strong candidate  Possible    Separate    Higher       CPU-heavy
                                                                                    process                  transforms
                                                                                    memory                   

  asyncio               Async I/O       Cooperative   Usually poor fit  Strong      Often       Moderate     High-latency
                        orchestration   event loop                                  efficient                APIs, async DB
                                                                                    per task                 
  -------------------------------------------------------------------------------------------------------------------------

These models can be combined.

Example:

``` text
                  asyncio
                     |
        +------------+------------+
        |            |            |
      API A        API B        API C
        |            |            |
        +------------+------------+
                     |
                     v
                  records
                     |
                     v
             CPU-heavy enrichment
                     |
                     v
             ProcessPoolExecutor
                     |
                     v
                  storage
```

The principle is:

> Use the execution model that matches the bottleneck.

------------------------------------------------------------------------

# 30. When Asyncio Does Not Help

Asyncio may provide little or no benefit when:

-   the workload is CPU-bound pure Python;
-   a native library already performs efficient parallel work;
-   the workload is tiny;
-   there is only one operation;
-   operations cannot overlap;
-   dependencies are synchronous and blocking;
-   the database server is the bottleneck;
-   the API rate limit is the bottleneck;
-   downstream storage is saturated;
-   task-management overhead exceeds useful overlap;
-   complexity increases without measurable benefit.

More concurrency can make things slower:

``` text
Concurrency 1
    |
    v
reasonable throughput

Concurrency 20
    |
    v
higher throughput

Concurrency 100
    |
    v
contention

Concurrency 1000
    |
    v
memory pressure + failures + throttling
```

The optimum is workload-specific.

------------------------------------------------------------------------

# 31. Asyncio + CPU-Bound Work

This does not make CPU work asynchronous:

``` python
async def cpu_heavy():
    for _ in range(10_000_000):
        expensive_operation()
```

If the coroutine performs long CPU work without yielding:

``` text
Event loop
    |
    v
CPU-heavy coroutine
    |
    | long computation
    v
other tasks wait
```

Possible boundaries include:

-   `asyncio.to_thread()` for suitable blocking work;
-   `ThreadPoolExecutor`;
-   `ProcessPoolExecutor`;
-   native libraries;
-   specialized data-processing engines.

The important architecture is:

``` text
Async I/O
    |
    v
records
    |
    v
CPU execution boundary
    |
    v
processed records
```

Do not use asyncio as a substitute for CPU parallelism.

------------------------------------------------------------------------

# 32. Async HTTP Data Engineering Experiment

The following educational experiment compares equivalent sequential and
concurrent simulated HTTP work.

``` python
import asyncio
import random
import time


async def simulated_request(request_id: int) -> dict[str, object]:
    delay = random.uniform(0.2, 0.5)
    await asyncio.sleep(delay)

    return {
        "request_id": request_id,
        "delay": delay,
    }


async def sequential_run():
    results = []

    for request_id in range(10):
        results.append(
            await simulated_request(request_id)
        )

    return results


async def concurrent_run():
    tasks = [
        asyncio.create_task(
            simulated_request(request_id)
        )
        for request_id in range(10)
    ]

    return await asyncio.gather(*tasks)


async def main():
    start = time.perf_counter()
    sequential = await sequential_run()
    sequential_elapsed = time.perf_counter() - start

    start = time.perf_counter()
    concurrent = await concurrent_run()
    concurrent_elapsed = time.perf_counter() - start

    sequential.sort(key=lambda row: row["request_id"])
    concurrent.sort(key=lambda row: row["request_id"])

    print(f"sequential: {sequential_elapsed:.3f}s")
    print(f"concurrent: {concurrent_elapsed:.3f}s")
    print("outputs equal:", sequential == concurrent)

    if concurrent_elapsed:
        print(
            "speed-up:",
            sequential_elapsed / concurrent_elapsed,
        )


asyncio.run(main())
```

The experiment demonstrates overlap of waiting.

Actual performance depends on:

-   latency;
-   concurrency;
-   server limits;
-   connection reuse;
-   failures;
-   retries;
-   network conditions.

Never promise linear scaling.

------------------------------------------------------------------------

# 33. Async Pagination Concept

A cursor-based pagination pattern can be represented as:

``` python
async def fetch_pages():
    cursor = None

    while True:
        page = await fetch_page(cursor)

        for record in page["data"]:
            yield record

        cursor = page.get("next_cursor")

        if not cursor:
            break
```

Architecture:

``` text
page 1
  |
  v
cursor 2
  |
  v
page 2
  |
  v
cursor 3
  |
  v
page 3
```

If page 2 requires the cursor produced by page 1, those pages are
sequentially dependent.

By contrast, independent time windows might be concurrent:

``` text
Window A ----\
Window B -----\
Window C ------+--> concurrent extraction
Window D -----/
```

Async generators are useful because records can be consumed
incrementally.

Detailed pagination, retry, rate-limit, and checkpoint design belongs to
the dedicated ingestion lesson.

------------------------------------------------------------------------

# 34. Async PostgreSQL Example

A small conceptual pattern:

``` python
import asyncio
import psycopg


async def read_value(
    conn: psycopg.AsyncConnection,
    value: int,
) -> int:
    async with conn.cursor() as cur:
        await cur.execute(
            "SELECT %s",
            (value,),
        )
        row = await cur.fetchone()

    return row[0]


async def main():
    async with await psycopg.AsyncConnection.connect(
        "postgresql://..."
    ) as conn:
        result = await read_value(conn, 42)
        print(result)


asyncio.run(main())
```

Important flow:

``` text
connection acquisition
       |
       v
cursor acquisition
       |
       v
await query
       |
       v
database/network wait
       |
       v
resume
       |
       v
fetch result
       |
       v
release cursor
       |
       v
release connection
```

Pool size is an explicit concurrency boundary.

Do not equate:

``` text
number of tasks
```

with:

``` text
number of simultaneous database operations
```

------------------------------------------------------------------------

# 35. Testing Async Code

A common stack is `pytest` with `pytest-asyncio`.

Example:

``` python
import pytest


@pytest.mark.asyncio
async def test_fetch():
    result = await fetch()
    assert result == expected_value
```

Good async tests cover:

-   successful results;
-   expected exceptions;
-   deterministic output;
-   async dependency behavior;
-   resource cleanup;
-   equivalent sequential/concurrent outputs.

A mocked async dependency should preserve its async contract:

``` python
async def fake_fetch():
    return {"id": 1}
```

Then:

``` python
result = await fake_fetch()
```

Advanced cancellation and shutdown testing belong to the next lesson.

------------------------------------------------------------------------

# 36. `asyncio.run()` and Event-Loop Lifecycle

A conventional CLI boundary is:

``` python
asyncio.run(main())
```

At a high level it:

1.  creates/manages the event loop;
2.  runs the main coroutine;
3.  finalizes asynchronous generators;
4.  performs shutdown;
5.  closes the loop.

Avoid repeatedly doing:

``` python
asyncio.run(operation_a())
asyncio.run(operation_b())
asyncio.run(operation_c())
```

for tiny operations in one application.

Prefer a single application-level async lifecycle where appropriate:

``` python
async def main():
    await operation_a()
    await operation_b()
    await operation_c()


asyncio.run(main())
```

## Running-loop error

This is problematic:

``` python
async def main():
    asyncio.run(other())
```

If an event loop is already running, Python can raise:

``` text
RuntimeError:
asyncio.run() cannot be called from a running event loop
```

Inside async code, use:

``` python
await other()
```

------------------------------------------------------------------------

# 37. Async Contexts in Real Applications

Different environments own event loops differently.

### CLI

``` text
synchronous entry point
        |
        v
asyncio.run()
        |
        v
async application
```

### Async framework

A framework may already own the loop:

``` python
async def handler():
    result = await operation()
    return result
```

### Notebook

A notebook may already have an active event loop, so calling
`asyncio.run()` can be inappropriate.

### Worker process

A worker can have its own async lifecycle depending on the architecture.

The principle is:

> Know who owns the event loop before choosing how to enter async code.

------------------------------------------------------------------------

# 38. Performance Measurement

Use `time.perf_counter()` for elapsed-time measurement:

``` python
import time

start = time.perf_counter()

# operation

elapsed = time.perf_counter() - start
print(f"{elapsed:.3f}s")
```

Measure:

-   wall-clock time;
-   operation count;
-   throughput;
-   latency;
-   concurrency;
-   failures.

A useful experiment is:

``` text
Sequential baseline
        |
        v
Measure
        |
        v
Concurrent implementation
        |
        v
Measure
        |
        v
Compare equivalent results
        |
        v
Calculate observed speed-up
```

A simple speed-up metric:

``` text
sequential time
---------------
concurrent time
```

Performance claims without measurement are hypotheses.

------------------------------------------------------------------------

# 39. Common Misconceptions

  -----------------------------------------------------------------------
  Misconception                       Reality
  ----------------------------------- -----------------------------------
  asyncio means parallelism           It is primarily an I/O concurrency
                                      model

  `async def` makes code non-blocking Blocking code inside it can still
                                      block

  `await` creates a thread            It suspends a coroutine

  `await` means parallel execution    It waits for an awaitable while
                                      allowing loop progress

  More tasks always increase          Excessive concurrency can hurt
  throughput                          performance

  Async code cannot block             Blocking code can block the
                                      event-loop thread

  asyncio replaces multiprocessing    CPU workloads may require processes
                                      or other models

  asyncio is always faster than       It depends on the workload and
  threads                             dependencies

  One event loop means one operation  Multiple tasks can overlap their
  at a time                           waiting

  CPU-heavy work belongs in asyncio   CPU-heavy work can stall the event
                                      loop

  Async DB means unlimited DB         Pool/server capacity still limits
  concurrency                         concurrency
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 40. Mini Project --- Async Data Fetcher

The project below is self-contained and demonstrates:

-   20 simulated endpoints;
-   sequential baseline;
-   asyncio concurrency;
-   timing;
-   output comparison;
-   one failed request;
-   error reporting;
-   event-loop blocking;
-   `asyncio.to_thread()`.

``` python
from __future__ import annotations

import asyncio
import random
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class Result:
    endpoint_id: int
    payload: str


class SimulatedAPIError(RuntimeError):
    pass


async def simulated_endpoint(endpoint_id: int) -> Result:
    await asyncio.sleep(random.uniform(0.05, 0.15))

    if endpoint_id == 7:
        raise SimulatedAPIError(
            f"endpoint {endpoint_id} failed"
        )

    return Result(
        endpoint_id=endpoint_id,
        payload=f"payload-{endpoint_id}",
    )


async def sequential_fetch(endpoint_ids):
    results = []
    errors = []

    for endpoint_id in endpoint_ids:
        try:
            results.append(
                await simulated_endpoint(endpoint_id)
            )
        except SimulatedAPIError as exc:
            errors.append(str(exc))

    return results, errors


async def concurrent_fetch(endpoint_ids):
    tasks = [
        asyncio.create_task(
            simulated_endpoint(endpoint_id)
        )
        for endpoint_id in endpoint_ids
    ]

    outcomes = await asyncio.gather(
        *tasks,
        return_exceptions=True,
    )

    results = []
    errors = []

    for outcome in outcomes:
        if isinstance(outcome, Exception):
            errors.append(str(outcome))
        else:
            results.append(outcome)

    return results, errors


def blocking_operation():
    time.sleep(0.5)
    return "blocking operation complete"


async def demonstrate_to_thread():
    result = await asyncio.to_thread(
        blocking_operation
    )
    print(result)


async def demonstrate_blocking_damage():
    async def bad_task():
        print("bad task: blocking")
        time.sleep(0.5)
        print("bad task: complete")

    async def good_task():
        print("good task: yielding")
        await asyncio.sleep(0.5)
        print("good task: complete")

    start = time.perf_counter()

    await asyncio.gather(
        bad_task(),
        good_task(),
    )

    print(
        "blocking demonstration:",
        time.perf_counter() - start,
    )


async def main():
    endpoint_ids = list(range(20))

    start = time.perf_counter()
    sequential_results, sequential_errors = (
        await sequential_fetch(endpoint_ids)
    )
    sequential_elapsed = (
        time.perf_counter() - start
    )

    start = time.perf_counter()
    concurrent_results, concurrent_errors = (
        await concurrent_fetch(endpoint_ids)
    )
    concurrent_elapsed = (
        time.perf_counter() - start
    )

    sequential_results.sort(
        key=lambda item: item.endpoint_id
    )
    concurrent_results.sort(
        key=lambda item: item.endpoint_id
    )

    print("sequential:", sequential_elapsed)
    print("concurrent:", concurrent_elapsed)

    print(
        "results equal:",
        sequential_results == concurrent_results,
    )

    print("sequential errors:", sequential_errors)
    print("concurrent errors:", concurrent_errors)

    if concurrent_elapsed:
        print(
            "speed-up:",
            sequential_elapsed / concurrent_elapsed,
        )

    await demonstrate_blocking_damage()
    await demonstrate_to_thread()


if __name__ == "__main__":
    asyncio.run(main())
```

The important outcome is not a guaranteed speed-up number.

The experiment teaches:

``` text
equivalent work
+
visible failures
+
measured elapsed time
+
correct result comparison
```

------------------------------------------------------------------------

# 41. Debugging Exercises

Attempt these before reading the answer key.

## Exercise 1 --- Missing await

``` python
async def fetch():
    await asyncio.sleep(0.1)
    return "data"


async def main():
    result = fetch()
    print(result)
```

**Expected behavior:** `"data"` is not produced as intended.

**Task:** Explain what `result` is and correct the program.

**Hint:** Calling an async function creates a coroutine object.

------------------------------------------------------------------------

## Exercise 2 --- Blocking sleep

``` python
async def a():
    time.sleep(1)
    print("A")


async def b():
    await asyncio.sleep(0.1)
    print("B")
```

**Expected behavior:** B is delayed.

**Task:** Replace the blocking operation.

**Hint:** Use an async sleep.

------------------------------------------------------------------------

## Exercise 3 --- Forgotten task lifecycle

``` python
async def main():
    asyncio.create_task(background())
    print("main complete")
```

**Task:** Design explicit ownership and completion handling.

**Hint:** Retain and await the Task when appropriate.

------------------------------------------------------------------------

## Exercise 4 --- Synchronous HTTP

``` python
async def fetch(url):
    response = requests.get(url)
    return response.json()
```

**Task:** Explain why this can block the event loop and identify an
async-native alternative.

------------------------------------------------------------------------

## Exercise 5 --- CPU-heavy loop

``` python
async def transform(records):
    for record in records:
        expensive_python_calculation(record)
```

**Task:** Explain why it can stall other tasks and identify an execution
boundary.

------------------------------------------------------------------------

## Exercise 6 --- Wrong `gather()` handling

``` python
results = await asyncio.gather(
    fetch_a(),
    fetch_b(),
    return_exceptions=True,
)

for result in results:
    print(result["id"])
```

**Task:** Correctly handle exception objects.

------------------------------------------------------------------------

## Exercise 7 --- Resource cleanup

``` python
async def load():
    client = create_async_client()
    return await client.get(url)
```

**Task:** Redesign the lifecycle using an async context manager if
supported.

------------------------------------------------------------------------

## Exercise 8 --- Incorrect `asyncio.run()`

``` python
async def process():
    asyncio.run(fetch())
```

**Task:** Fix the nested event-loop boundary.

------------------------------------------------------------------------

# 42. Debugging Exercise Answer Key

### 1. Missing await

``` python
async def main():
    result = await fetch()
    print(result)
```

### 2. Blocking sleep

``` python
async def a():
    await asyncio.sleep(1)
    print("A")
```

### 3. Task lifecycle

``` python
async def main():
    task = asyncio.create_task(background())
    print("main complete")
    await task
```

### 4. Synchronous HTTP

Use an async-native client such as `httpx.AsyncClient` where
appropriate:

``` python
import httpx


async def fetch(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
```

In a production extractor, client lifetime should normally be broader
than one request.

### 5. CPU-heavy loop

Move suitable CPU-heavy work to an appropriate execution boundary, such
as a process pool or specialized compute engine. Do not assume
`async def` makes it concurrent.

### 6. `gather()` exceptions

``` python
for result in results:
    if isinstance(result, Exception):
        print(f"failure: {result}")
    else:
        print(result["id"])
```

### 7. Resource cleanup

Conceptually:

``` python
async def load():
    async with create_async_client() as client:
        return await client.get(url)
```

### 8. Nested `asyncio.run()`

Inside async code:

``` python
async def process():
    await fetch()
```

------------------------------------------------------------------------

# 43. Coding Exercises

## Basic

### 1. First coroutine

**Objective:** Define and execute an async function.

**Requirements:**

-   define `async def hello()`;
-   print a message;
-   execute it correctly.

**Constraints:** Use `asyncio.run()` at the top level.

**Expected behavior:** The message is printed once.

**Hint:** Start with `asyncio.run(hello())`.

### 2. Async sleep

**Objective:** Demonstrate asynchronous waiting.

**Requirements:**

-   print `"start"`;
-   await `asyncio.sleep(1)`;
-   print `"finish"`.

**Constraint:** Do not use `time.sleep()`.

### 3. Sequential async calls

**Objective:** Prove that async syntax alone does not imply concurrency.

Run:

``` python
await work("A")
await work("B")
await work("C")
```

**Expected behavior:** Each operation completes before the next begins.

## Moderate

### 4. `create_task()`

Create three tasks before awaiting them.

**Expected behavior:** Their waits overlap.

### 5. `gather()`

Run five independent operations with `asyncio.gather()`.

Verify result order.

### 6. Exception handling

Run three tasks, make one fail, and demonstrate both normal `gather()`
and `return_exceptions=True`.

### 7. Async generator

Create an async generator producing 20 records with simulated latency.

Consume it with `async for`.

## Hard

### 8. Async API simulation

Simulate 50 endpoints, measure sequential and concurrent versions, and
verify equivalent results.

### 9. Async database simulation

Simulate independent database queries with asynchronous waits and run
them concurrently.

### 10. Blocking isolation

Create a synchronous blocking function and execute it through:

``` python
await asyncio.to_thread(blocking_function)
```

For every exercise, the engineering goal is to explain why the chosen
model is appropriate, not merely to make the code run.

------------------------------------------------------------------------

# 44. Coding Exercise Solutions

## Solution 1

``` python
import asyncio


async def hello():
    print("hello")


asyncio.run(hello())
```

## Solution 2

``` python
import asyncio


async def work():
    print("start")
    await asyncio.sleep(1)
    print("finish")


asyncio.run(work())
```

## Solution 3

``` python
import asyncio


async def work(name):
    print(f"start {name}")
    await asyncio.sleep(1)
    print(f"finish {name}")


async def main():
    await work("A")
    await work("B")
    await work("C")


asyncio.run(main())
```

## Solution 4

``` python
import asyncio


async def work(name):
    await asyncio.sleep(1)
    return name


async def main():
    tasks = [
        asyncio.create_task(work("A")),
        asyncio.create_task(work("B")),
        asyncio.create_task(work("C")),
    ]

    results = [await task for task in tasks]
    print(results)


asyncio.run(main())
```

## Solution 5

``` python
results = await asyncio.gather(
    work("A", 0.3),
    work("B", 0.1),
    work("C", 0.2),
)
```

The output order corresponds to the input order.

## Solution 6

``` python
results = await asyncio.gather(
    work("A"),
    work("B"),
    work("C"),
    return_exceptions=True,
)

for result in results:
    if isinstance(result, Exception):
        print("failure:", result)
    else:
        print("success:", result)
```

## Solution 7

``` python
async def generate_records():
    for record_id in range(20):
        await asyncio.sleep(0.05)
        yield {
            "id": record_id,
            "value": f"value-{record_id}",
        }


async def main():
    async for record in generate_records():
        print(record)
```

## Solution 8

Use `time.perf_counter()` around equivalent sequential and concurrent
implementations, then compare normalized results.

## Solution 9

``` python
async def query_database(query_id):
    await asyncio.sleep(0.2)
    return {"query_id": query_id, "rows": 10}


async def main():
    results = await asyncio.gather(
        *(query_database(i) for i in range(5))
    )
    print(results)
```

## Solution 10

``` python
def blocking_operation():
    time.sleep(1)
    return "done"


async def main():
    result = await asyncio.to_thread(
        blocking_operation
    )
    print(result)
```

------------------------------------------------------------------------

# 45. Interview Questions

## Basic

### 1. What is a coroutine?

A coroutine is asynchronous computation defined through `async def`;
calling the coroutine function produces a coroutine object that can be
awaited or scheduled.

### 2. What is an event loop?

It coordinates ready asynchronous tasks, timers, callbacks, and I/O
readiness.

### 3. What does `await` do?

It suspends the current coroutine until an awaitable completes.

### 4. Why does `time.sleep()` block asyncio?

It blocks the event-loop thread.

### 5. What is a Task?

A Task schedules a coroutine as independently managed asynchronous
execution.

### 6. Coroutine versus Task?

A coroutine object represents asynchronous computation. A Task is an
asyncio scheduling object that runs a coroutine.

### 7. What does `create_task()` do?

It schedules a coroutine as a Task.

### 8. What does `gather()` do?

It awaits multiple awaitables and collects results in input order.

### 9. Why can asyncio improve API extraction?

Independent network waits can overlap.

### 10. When does asyncio not help?

When the workload is CPU-bound, sequential, too small, blocked by
synchronous dependencies, or constrained elsewhere.

## Moderate

### 1. Why does async syntax not guarantee non-blocking behavior?

Because arbitrary synchronous code can still execute inside `async def`.

### 2. What is cooperative scheduling?

Coroutines voluntarily suspend at await points so the event loop can run
other work.

### 3. Why can a database pool limit async throughput?

Because the number of available database connections is finite.

### 4. What does `return_exceptions=True` change?

It causes `gather()` to return exceptions as results instead of
propagating them through the gather call in the normal way.

### 5. Why reuse an HTTP client?

Connection pooling and resource reuse can reduce setup overhead.

### 6. What is an async generator?

A generator that can await between yielded values and is consumed with
`async for`.

### 7. What is `to_thread()`?

A bridge for executing a suitable blocking synchronous function in a
worker thread.

### 8. Why does CPU-heavy code block asyncio?

Because it executes on the event-loop thread unless moved elsewhere.

### 9. Why is task ownership important?

Every task can produce a result, exception, or cancellation state that
must be observed and managed.

### 10. Why benchmark concurrency?

Because theoretical overlap does not guarantee real-world speed-up.

## Hard

### 1. Why can 1,000 tasks be slower than 10?

Scheduling, memory, network, server, connection, retry, and downstream
contention can dominate useful work.

### 2. How would you debug an async application that behaves synchronously?

Search for blocking operations, enable debug mode, instrument latency,
inspect CPU use, inspect pool limits, and compare with a sequential
baseline.

### 3. Why is cursor pagination often sequential?

The next cursor may be produced only by the previous page.

### 4. How can async and process execution be combined?

Use asyncio for I/O orchestration and a process-based boundary for
CPU-heavy processing.

### 5. Why can more API concurrency hurt?

It can trigger rate limits, server overload, throttling, retries, and
connection pressure.

### 6. Why does `await` not create parallelism?

It suspends the coroutine and lets the event loop schedule other ready
work.

### 7. Why can synchronous dependencies force architecture changes?

They can block the event-loop thread, requiring an async-native
replacement or execution boundary.

### 8. Why can an async DB client still be slow?

Database query execution, locks, server CPU, I/O, connection
acquisition, and storage can dominate.

### 9. How should sequential and concurrent outputs be compared?

Normalize nondeterministic ordering with a stable key where appropriate,
then compare logical results and failures.

### 10. What is the most important async production rule?

Do not block the event loop with operations that prevent other required
work from progressing.

## Advanced

### 1. How would you decide whether asyncio belongs in a 100,000-record extractor?

Start with the sequential baseline, classify the workload, inspect API
latency and independence, verify async library support, understand
service limits, prototype measured concurrency, and validate equivalent
outputs.

### 2. An async extractor is slower than the synchronous one. What do you inspect?

Blocking calls, task count, connection reuse, rate limits, retries, pool
capacity, CPU work, downstream bottlenecks, and measurement methodology.

### 3. How would you combine asyncio with CPU-heavy enrichment?

Keep I/O orchestration asynchronous and move CPU-heavy work to an
appropriate process/native execution boundary.

### 4. Why can `to_thread()` be a poor CPU solution?

Threads are primarily useful here for blocking operations; CPU-bound
Python may require a different execution model.

### 5. Why is unbounded concurrency dangerous?

It can turn external capacity limits into memory growth, throttling,
failures, and instability.

### 6. How would you diagnose an occasional async hang?

Inspect blocking calls, unresolved awaits, resource exhaustion, external
latency, connection pools, task state, and event-loop responsiveness.

### 7. What does event-loop ownership mean?

It means knowing which application/framework component creates and
controls the loop so that nested loop creation is avoided.

### 8. Why is resource cleanup part of concurrency correctness?

Because tasks may hold connections, sockets, cursors, or clients, and
failure to release them can exhaust shared capacity.

### 9. Why is task count not a performance metric?

Because tasks are logical scheduling units; useful throughput depends on
I/O latency, capacity, and resource constraints.

### 10. Explain asyncio to a production Data Engineer.

Asyncio efficiently coordinates I/O-bound concurrent work. Coroutines
suspend at await points, Tasks represent independently scheduled
coroutine execution, and the event loop resumes ready work. It is
valuable when waiting can overlap, but it does not turn CPU-heavy Python
into parallel computation or remove downstream capacity limits.
Production use requires explicit resource management, error visibility,
bounded workload design, and measured performance.

------------------------------------------------------------------------

# 46. Architecture Questions

## Scenario 1 --- 100,000 API records

Decision sequence:

``` text
What is the bottleneck?
       |
       v
Is it I/O?
       |
       v
Can operations overlap?
       |
       v
Does the client support async?
       |
       v
What are source limits?
       |
       v
What is downstream capacity?
       |
       v
What baseline exists?
       |
       v
What does measurement show?
```

Do not start with a target task count.

## Scenario 2 --- Async slower than synchronous

Investigate:

``` text
blocking dependency
      +
excessive task creation
      +
connection setup
      +
rate limits
      +
retries
      +
CPU work
      +
downstream bottleneck
      +
invalid benchmark
```

Fix the actual bottleneck.

## Scenario 3 --- 1,000 tasks, service limit 100

There is a mismatch between application concurrency and service
capacity.

The architecture needs bounded concurrency. The detailed semaphore
pattern belongs to the next coordination lesson.

## Scenario 4 --- Async pipeline hangs

Inspect:

-   event-loop blocking;
-   unresolved async operations;
-   external-service latency;
-   resource exhaustion;
-   connection pools;
-   task lifecycle;
-   missing timeouts;
-   shutdown behavior.

Detailed cancellation and timeout mechanics belong to the next lesson.

## Scenario 5 --- Network is fast, database is slow

Measure:

-   connection acquisition;
-   pool saturation;
-   query latency;
-   locks;
-   database CPU;
-   database I/O;
-   transaction behavior.

Do not increase API concurrency merely because the API is fast.

## Scenario 6 --- Async extraction plus CPU-heavy enrichment

A reasonable architecture is:

``` text
async extraction
      |
      v
records
      |
      v
CPU execution boundary
      |
      v
transformation
      |
      v
storage
```

The event loop should not become the CPU worker.

------------------------------------------------------------------------

# 47. Real-World Data Engineering Scenarios

## 47.1 SaaS API extraction

**Problem:** Thousands of high-latency requests.

**Why asyncio may help:** Network waits can overlap.

**Architecture:**

``` text
async tasks
    |
    +--> API request
    +--> API request
    +--> API request
    |
    v
records
    |
    v
landing
```

**Risks:** rate limits, authentication, pagination, retries, downstream
capacity.

**Observability:** request count, latency, failures, records,
throughput, concurrency.

## 47.2 Multi-endpoint ingestion

Independent endpoints can overlap:

``` text
customers \
orders     \
products    +--> event loop
payments   /
```

But dependent endpoints should preserve dependency order.

## 47.3 Incremental extraction

Asyncio can coordinate independent requests after a watermark/window is
determined.

Asyncio itself does not solve:

-   watermark correctness;
-   duplicate handling;
-   source consistency;
-   checkpoint correctness.

## 47.4 Database extraction

Async database clients can overlap independent database waits.

The database remains a finite-capacity system.

## 47.5 Object storage

Async network operations may overlap, but bandwidth and storage-service
limits remain.

## 47.6 Metadata collection

Asyncio can be useful for querying many independent metadata services.

## 47.7 Concurrent validation

Independent external validation calls can overlap network waits.

## 47.8 Async orchestration around CPU workers

``` text
API/network I/O
      |
      v
asyncio
      |
      v
records
      |
      v
CPU workers
      |
      v
output
```

This is often more realistic than forcing every stage into asyncio.

------------------------------------------------------------------------

# 48. Progressive Lab: Sequential to Production-Oriented Async

## Version 1 --- Sequential

``` python
import time


def fetch(name):
    time.sleep(1)
    return name


start = time.perf_counter()

results = [
    fetch("A"),
    fetch("B"),
    fetch("C"),
]

print(results)
print(time.perf_counter() - start)
```

## Version 2 --- `async def`

``` python
import asyncio


async def fetch(name):
    await asyncio.sleep(1)
    return name


async def main():
    results = [
        await fetch("A"),
        await fetch("B"),
        await fetch("C"),
    ]
    print(results)


asyncio.run(main())
```

This remains sequential.

## Version 3 --- `create_task()`

``` python
async def main():
    task_a = asyncio.create_task(fetch("A"))
    task_b = asyncio.create_task(fetch("B"))
    task_c = asyncio.create_task(fetch("C"))

    results = [
        await task_a,
        await task_b,
        await task_c,
    ]

    print(results)
```

## Version 4 --- `gather()`

``` python
async def main():
    results = await asyncio.gather(
        fetch("A"),
        fetch("B"),
        fetch("C"),
    )
    print(results)
```

## Version 5 --- Error handling

``` python
async def fetch(name):
    await asyncio.sleep(0.1)

    if name == "B":
        raise ValueError("B failed")

    return name


async def main():
    results = await asyncio.gather(
        fetch("A"),
        fetch("B"),
        fetch("C"),
        return_exceptions=True,
    )

    for result in results:
        if isinstance(result, Exception):
            print("failure:", result)
        else:
            print("success:", result)
```

## Version 6 --- Async generator

``` python
async def records():
    for i in range(5):
        await asyncio.sleep(0.1)
        yield {"id": i}
```

## Version 7 --- Blocking adapter

``` python
def blocking_lookup():
    time.sleep(1)
    return "done"


async def main():
    result = await asyncio.to_thread(
        blocking_lookup
    )
    print(result)
```

## Version 8 --- Data Engineering workflow

``` python
import asyncio


async def fetch_source(source):
    await asyncio.sleep(0.2)
    return [
        {"source": source, "value": 1},
        {"source": source, "value": 2},
    ]


async def extract_all(sources):
    batches = await asyncio.gather(
        *(fetch_source(source) for source in sources)
    )

    records = []

    for batch in batches:
        records.extend(batch)

    return records


async def main():
    sources = [
        "customers",
        "orders",
        "products",
        "payments",
    ]

    records = await extract_all(sources)

    for record in records:
        print(record)


asyncio.run(main())
```

This progression is intentional:

``` text
sequential
   |
   v
async function
   |
   v
tasks
   |
   v
gather
   |
   v
error handling
   |
   v
async streaming
   |
   v
blocking isolation
   |
   v
Data Engineering workflow
```

------------------------------------------------------------------------

# 49. Correctness Requirement

Whenever comparing sequential and concurrent implementations:

1.  Perform equivalent work.
2.  Compare outputs.
3.  Explain ordering differences.
4.  Measure wall-clock time.
5.  Do not assume linear speed-up.
6.  Normalize nondeterministic ordering when logical order is
    irrelevant.

For example:

``` python
sequential.sort(key=lambda row: row["id"])
concurrent.sort(key=lambda row: row["id"])

assert sequential == concurrent
```

Do not compare accidental completion order when the business requirement
does not define such an order.

Correctness comes before optimization.

------------------------------------------------------------------------

# 50. Production Mental Model

Before using asyncio, ask:

1.  Is the workload I/O-bound?
2.  Can operations overlap?
3.  Are async-compatible libraries available?
4.  What is the external service concurrency limit?
5.  What is the database pool capacity?
6.  What happens if a task fails?
7.  How will resources be cleaned up?
8.  How will blocking code be isolated?
9.  How will performance be measured?
10. How will the workflow shut down?

The production sequence is:

``` text
Correctness
    |
    v
Resource safety
    |
    v
Error visibility
    |
    v
Observability
    |
    v
Measured performance
    |
    v
Optimization
```

Do not reverse this order.

------------------------------------------------------------------------

# 51. Final Mental Model

``` text
Application
    |
    v
asyncio.run()
    |
    v
Event Loop
    |
    v
Tasks
    |
    v
Coroutines
    |
    v
await
    |
    +-------------------+
    |                   |
    v                   |
I/O waits / timers      |
    |                   |
    +--> event loop ----+
         runs ready tasks
                |
                v
        coroutine resumes
                |
                v
          Task completes
                |
                +--> result
                |
                +--> exception
```

And the execution-model decision:

``` text
                Workload
                   |
          +--------+--------+
          |                 |
       I/O-bound         CPU-bound
          |                 |
          v                 v
       asyncio /         processes /
       threads           native compute /
                         suitable workers
```

------------------------------------------------------------------------

# 52. Common Production Failure Modes

## Hidden blocking call

``` text
async application
       |
       v
sync SDK
       |
       v
event loop blocked
       |
       v
latency spike
```

Use an async-native dependency or isolate the blocking call.

## Unbounded tasks

``` text
1,000,000 records
       |
       v
1,000,000 tasks
       |
       v
memory + connection pressure
```

Later bounded-concurrency and queue patterns solve this more
systematically.

## Downstream saturation

``` text
more async requests
       |
       v
database/storage overloaded
       |
       v
throughput decreases
```

## Resource leak

``` text
task
 |
 +--> connection
 +--> cursor
 +--> stream
 |
 X cleanup forgotten
```

Use explicit resource ownership and async context managers.

## Silent failure

``` text
create_task()
     |
     X
exception never meaningfully observed
```

Define who owns and observes every important background task.

------------------------------------------------------------------------

# 53. Production Checklist

### Workload

-   [ ] I/O-bound nature established.
-   [ ] Independent operations identified.
-   [ ] Sequential baseline measured.

### Dependencies

-   [ ] Async-compatible libraries evaluated.
-   [ ] Blocking dependencies identified.
-   [ ] Blocking adapters have an explicit execution boundary.

### Capacity

-   [ ] External service limits known.
-   [ ] Database pool capacity known.
-   [ ] Storage capacity known.
-   [ ] Concurrency is not blindly unbounded.

### Correctness

-   [ ] Equivalent outputs verified.
-   [ ] Ordering requirements understood.
-   [ ] Exceptions are observable.
-   [ ] Task ownership is explicit.

### Resources

-   [ ] HTTP clients have an intentional lifecycle.
-   [ ] Database connections are released.
-   [ ] Cursors and streams are released.
-   [ ] Async context managers are used where appropriate.

### Performance

-   [ ] `time.perf_counter()` or equivalent measurement used.
-   [ ] Throughput measured.
-   [ ] Latency measured.
-   [ ] Failure rates measured.
-   [ ] Speed-up compared with a sequential baseline.

### Debugging

-   [ ] Asyncio debug mode can be enabled.
-   [ ] Blocking calls can be identified.
-   [ ] Task lifecycle can be inspected.
-   [ ] External latency is observable.

### Architecture

-   [ ] CPU-heavy work is separated from the event loop.
-   [ ] Database pool capacity is respected.
-   [ ] External service capacity is respected.
-   [ ] Application event-loop ownership is understood.
-   [ ] Cleanup and shutdown responsibilities are explicit.

------------------------------------------------------------------------

# 54. Final Production Principle

The most important lesson is not:

> "Use asyncio."

It is:

> **Choose asyncio when asynchronous I/O concurrency solves a measured
> bottleneck, preserve correctness, keep blocking work away from the
> event-loop thread, manage resources and errors explicitly, respect
> downstream capacity, and measure the result.**

A production Data Engineer should reason:

``` text
What is the bottleneck?
        |
        v
Is the workload I/O-bound?
        |
        v
Can operations overlap?
        |
        v
Are async-compatible dependencies available?
        |
        v
What capacity limits exist?
        |
        v
How will failures be handled?
        |
        v
How will resources be cleaned up?
        |
        v
How will performance be measured?
        |
        v
Is asyncio actually better than the simpler alternative?
```

That is the difference between knowing asyncio syntax and understanding
asynchronous systems.

------------------------------------------------------------------------

# 55. Topic Completion Standard

You are ready to move to the next asyncio topic when you can explain,
without memorizing wording:

1.  why asynchronous programming exists;
2.  why I/O-bound work is a common asyncio target;
3.  why CPU-bound Python is different;
4.  what `async def` defines;
5.  what a coroutine object is;
6.  what `await` actually does;
7.  what the event loop does;
8.  why asyncio uses cooperative scheduling;
9.  what a Task represents;
10. why `create_task()` changes execution behavior;
11. how `gather()` works;
12. how exceptions propagate through Tasks;
13. why task ownership matters;
14. why `async with` matters;
15. what async iterators and generators provide;
16. why blocking calls damage event-loop responsiveness;
17. when `asyncio.to_thread()` is appropriate;
18. when `run_in_executor()` is useful;
19. why async behavior can propagate through a call stack;
20. how async database access works conceptually;
21. why connection pools constrain concurrency;
22. where asyncio fits in Data Engineering;
23. where asyncio does not help;
24. how asyncio compares with threads and processes;
25. how to prove that concurrency benefits a real workload.

------------------------------------------------------------------------

# 56. Final Summary

Asyncio is a concurrency model for efficiently coordinating I/O-bound
work.

The event loop executes ready tasks cooperatively. Coroutines suspend at
`await` points. Tasks provide independently scheduled coroutine
execution. Blocking operations must not run directly on the event-loop
thread. Async context managers provide structured resource lifecycle
management. Async generators support incremental streaming.
`asyncio.to_thread()` and executors provide boundaries for suitable
blocking synchronous dependencies.

For Data Engineering, asyncio can be valuable for:

-   high-latency API extraction;
-   independent network requests;
-   async database access;
-   object-storage operations;
-   metadata collection;
-   concurrent external validation;
-   asynchronous orchestration around separate CPU workers.

It does not automatically solve:

-   CPU-bound computation;
-   downstream saturation;
-   database bottlenecks;
-   rate limits;
-   unbounded workload production;
-   resource management;
-   error handling;
-   checkpoint correctness.

The final mental model is:

``` text
Classify workload
       |
       v
Build sequential baseline
       |
       v
Measure
       |
       v
Overlap appropriate I/O
       |
       v
Keep event loop unblocked
       |
       v
Manage tasks/resources/errors
       |
       v
Respect capacity
       |
       v
Measure again
       |
       v
Keep asyncio only if it improves the real system
```

> **Asyncio is a concurrency tool, not a performance guarantee.**

The goal is not maximum concurrency.

The goal is a system that is **correct, observable, bounded,
maintainable, and measurably faster when concurrency is actually
appropriate**.
