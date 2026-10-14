# 06. Semaphores and Bounded Concurrency

> **Stage 2 — Python for Data Engineering**  
> **Module 2.10 — Concurrency and Parallelism in Practice**  
> **Topic 06 — Semaphores and Bounded Concurrency**

## Learning Objectives

By the end of this chapter, you should be able to:

- Explain why unbounded concurrency is dangerous.
- Explain bounded concurrency from first principles.
- Explain a semaphore as a finite set of permits.
- Use `asyncio.Semaphore`.
- Use `threading.Semaphore`.
- Explain `asyncio.BoundedSemaphore`.
- Prevent semaphore leaks.
- Distinguish concurrency limits from rate limits.
- Explain why a semaphore does not automatically bound task creation.
- Design fixed worker pools.
- Compare semaphores with worker pools.
- Build layered limits for APIs, databases, storage, and memory.
- Design per-host, per-API-key, per-database, and global limits.
- Align application concurrency with HTTP and database connection pools.
- Reason about variable-size payloads and memory bounds.
- Design fair resource sharing.
- Measure throughput, latency, p95/p99 latency, and error rate.
- Run concurrency experiments and select limits using evidence.
- Understand the fundamentals of adaptive concurrency.
- Diagnose overload and semaphore-related failures.
- Design production-grade bounded-concurrency Data Engineering pipelines.

---

## Prerequisites

You should already understand:

- Python functions and exceptions.
- `async` / `await`.
- Basic `asyncio` tasks.
- `asyncio.gather()`.
- Basic threads and thread pools.
- HTTP requests and database connections.
- Basic Data Engineering pipelines.

This chapter revisits important concepts from first principles so that the production reasoning is explicit.

---

# 1. Why Unbounded Concurrency Is Dangerous

Suppose a pipeline has 10,000 URLs:

```python
tasks = [
    fetch(url)
    for url in urls
]

await asyncio.gather(*tasks)
```

This code is syntactically simple.

It is not necessarily operationally safe.

If all 10,000 tasks become active, the system may create pressure on:

- sockets;
- file descriptors;
- HTTP connection pools;
- memory;
- DNS resolution;
- CPU;
- remote APIs;
- database connections;
- object-storage clients;
- downstream services.

A simplified failure chain is:

```text
10,000 tasks
     |
     v
10,000 active operations
     |
     +--> too many connections
     +--> too much memory
     +--> API overload
     +--> HTTP 429
     +--> increased latency
     +--> retries
     +--> even more load
     |
     v
cascading failure
```

The key lesson is:

> **`asyncio` makes concurrency cheap to express. It does not make unlimited concurrency safe.**

---

# 2. What Is Bounded Concurrency?

Unbounded:

```text
N requested operations
        |
        v
up to N active operations
```

Bounded:

```text
N requested operations
        |
        v
maximum K active operations
        |
        v
remaining work waits
```

Example:

```text
1,000 requested operations
Concurrency limit = 20

20 active
980 waiting
```

The system deliberately chooses a maximum amount of simultaneous work.

That maximum should be based on resource capacity rather than arbitrary preference.

---

# 3. Concurrency Is a Resource

Treat concurrency like:

- CPU;
- memory;
- database connections;
- file descriptors;
- network bandwidth;
- API quota;
- downstream service capacity.

A useful mental model is:

```text
                  WORKLOAD
                     |
                     v
             Identify resources
                     |
          +----------+----------+
          |          |          |
          v          v          v
        CPU        Memory     Network
          |          |          |
          v          v          v
       capacity   capacity   capacity
          \          |          /
           \         |         /
            +--------+--------+
                     |
                     v
              concurrency bound
```

The purpose is not simply to "make fewer requests."

The purpose is:

> **Keep every important resource inside a safe operating range while extracting as much useful throughput as the system can sustain.**

---

# 4. What Is a Semaphore?

A semaphore is a synchronization primitive representing a finite number of permits.

Imagine:

```text
20 parking spaces
100 cars
```

Only 20 cars can occupy spaces simultaneously.

The semaphore equivalent is:

```text
20 permits
100 tasks
```

The basic lifecycle is:

```text
acquire()
    |
    v
take permit
    |
    v
do work
    |
    v
release()
    |
    v
return permit
```

The semaphore does not perform the work.

It controls who is allowed to enter the protected concurrent region.

---

# 5. Semaphore Internals

Suppose:

```python
sem = asyncio.Semaphore(3)
```

Conceptually:

```text
available permits = 3
```

Three tasks can acquire:

```text
Task A -> permit 1
Task B -> permit 2
Task C -> permit 3
Task D -> waits
Task E -> waits
```

When B releases:

```text
Task B -> release()
             |
             v
       permit available
             |
             v
Task D -> acquire()
```

A useful abstraction is:

```text
available = initial_permits - active_holders
```

A production engineer should also understand that the actual implementation has waiter management and synchronization details. The mental model is deliberately simpler than the internal implementation.

---

# 6. `acquire()` and `release()`

The two fundamental operations are:

```python
await semaphore.acquire()
```

and:

```python
semaphore.release()
```

Conceptually:

```text
acquire
  |
  +-- permit available -> continue
  |
  +-- no permit -> wait

release
  |
  +-- return permit
  |
  +-- allow waiting work to proceed
```

A permit must be released even when the protected operation fails.

That makes cleanup critical.

---

# 7. `asyncio.Semaphore`

Basic creation:

```python
import asyncio

sem = asyncio.Semaphore(10)
```

Basic use:

```python
async with sem:
    await fetch()
```

The context manager performs the equivalent conceptual sequence:

```text
acquire
   |
   v
run body
   |
   +--> success
   |
   +--> exception
   |
   v
release
```

That automatic cleanup is one of the main reasons to prefer `async with`.

---

# 8. Explicit Semaphore Usage

The explicit form is:

```python
await sem.acquire()

try:
    await fetch()
finally:
    sem.release()
```

The `finally` block is essential.

Bad:

```python
await sem.acquire()
await fetch()
sem.release()
```

If `fetch()` raises:

```text
acquire
  |
  v
fetch()
  |
  v
exception
  |
  X
release never happens
```

The permit is leaked.

---

# 9. Basic Async Example

```python
import asyncio
import random


async def fetch(item: int) -> str:
    await asyncio.sleep(random.uniform(0.1, 0.5))
    return f"item-{item}"


async def bounded_fetch(item: int, sem: asyncio.Semaphore) -> str:
    async with sem:
        return await fetch(item)


async def main():
    sem = asyncio.Semaphore(5)

    tasks = [
        asyncio.create_task(bounded_fetch(item, sem))
        for item in range(30)
    ]

    results = await asyncio.gather(*tasks)
    print(results)


if __name__ == "__main__":
    asyncio.run(main())
```

At most five tasks can execute the protected `fetch()` operation at once.

Important:

> The example still creates 30 tasks.

The semaphore bounds **entry into the protected operation**, not necessarily task creation.

That distinction is central to this chapter.

---

# 10. Semaphore Leaks

A semaphore leak occurs when code acquires a permit but fails to return it.

Example:

```python
await sem.acquire()

if invalid:
    return

sem.release()
```

If `invalid` is true:

```text
acquire
  |
  v
early return
  |
  X
permit leaked
```

Eventually:

```text
available permits = 0
```

even though no real work is using them.

New tasks wait forever.

Use:

```python
async with sem:
    ...
```

or:

```python
await sem.acquire()
try:
    ...
finally:
    sem.release()
```

---

# 11. `asyncio.BoundedSemaphore`

Python also provides:

```python
asyncio.BoundedSemaphore
```

Example:

```python
sem = asyncio.BoundedSemaphore(10)
```

It behaves similarly to a semaphore for normal acquisition/release but detects attempts to release beyond the initial bound.

Conceptually:

```text
initial = 10

acquire -> 9
release -> 10

extra release
    |
    v
programming error detected
```

This is useful for catching release bugs.

---

# 12. `Semaphore` vs `BoundedSemaphore`

| Property | `Semaphore` | `BoundedSemaphore` |
|---|---|---|
| Limits simultaneous acquisition | Yes | Yes |
| Tracks permits | Yes | Yes |
| Detects over-release | Not as a primary purpose | Yes |
| Useful for | General permit control | Debugging/correctness around permit ownership |

A `BoundedSemaphore` does not solve leaks.

It helps detect a different class of bug:

> **Returning more permits than were originally available.**

---

# 13. `threading.Semaphore`

For threaded code:

```python
from threading import Semaphore

sem = Semaphore(10)
```

Use:

```python
with sem:
    do_work()
```

or explicitly:

```python
sem.acquire()

try:
    do_work()
finally:
    sem.release()
```

The conceptual model is identical:

```text
finite permits
+
acquire
+
protected work
+
release
```

The difference is the execution model.

`asyncio.Semaphore` coordinates async tasks.

`threading.Semaphore` coordinates threads.

Do not mix the primitives casually.

---

# 14. Semaphore vs Lock

A lock generally represents:

```text
one permit
```

A semaphore can represent:

```text
N permits
```

Therefore:

```text
Lock       -> maximum 1 holder
Semaphore  -> maximum N holders
```

Use a lock for exclusive access.

Use a semaphore when multiple concurrent operations are safe but must be bounded.

---

# 15. Concurrency Limit vs Rate Limit

This distinction is critical.

A concurrency limit answers:

> **How many operations may be active at once?**

A rate limit answers:

> **How many operations may start or complete during a time interval?**

Example:

```text
Concurrency = 10
Rate = 100 requests/second
```

These are different controls.

---

# 16. Why 10 Concurrent Requests Does Not Mean 10 Requests per Second

Suppose:

```text
concurrency = 10
```

and every request completes in:

```text
50 ms
```

A rough steady-state throughput could approach:

```text
10 / 0.05
=
200 requests/second
```

assuming the source and client can sustain it.

Therefore:

```text
10 concurrent
```

does not mean:

```text
10 requests/second
```

The relationship is influenced by service time and bottlenecks.

---

# 17. Concurrency and Rate Together

An API may require:

```text
maximum 20 concurrent requests
maximum 50 requests/second
```

You may need both:

```text
                API
                 ^
                 |
       +---------+---------+
       |                   |
       v                   v
Concurrency limit      Rate limiter
       |                   |
       v                   v
20 active              50/sec
```

A semaphore alone cannot guarantee the rate.

A rate limiter alone may allow too many simultaneous long-running requests.

---

# 18. Little's Law as a Mental Model

For a stable system:

```text
L = λW
```

where:

- `L` = average work in the system;
- `λ` = throughput;
- `W` = average time in the system.

For concurrency planning:

```text
concurrency ≈ throughput × latency
```

Example:

```text
100 requests/sec
×
0.2 sec/request
=
20 concurrent requests
```

This is a useful planning relationship, not a promise of performance.

---

# 19. Bounding Task Execution Is Not Bounding Task Creation

Consider:

```python
sem = asyncio.Semaphore(20)

tasks = [
    asyncio.create_task(bounded_work(item, sem))
    for item in million_items
]

await asyncio.gather(*tasks)
```

The work may be limited to 20 concurrent operations.

But one million task objects may still exist.

Memory pressure can therefore be:

```text
1,000,000 tasks
       |
       v
only 20 active operations
```

This is still potentially a bad design.

---

# 20. Bounding Task Creation

For large workloads, avoid creating millions of waiting tasks.

Better:

```text
input
  |
  v
bounded queue
  |
  +--> worker
  +--> worker
  +--> worker
  +--> worker
```

Only a bounded amount of work is resident in memory.

This is where worker pools and queues become valuable.

---

# 21. Fixed Worker Pools

A worker pool has:

```text
K workers
+
work queue
```

Example:

```python
import asyncio


async def worker(name, queue):
    while True:
        item = await queue.get()

        if item is None:
            queue.task_done()
            return

        try:
            await process(item)
        finally:
            queue.task_done()
```

Then:

```python
queue = asyncio.Queue(maxsize=100)
```

This bounds queued work as well as active work.

---

# 22. Semaphore vs Worker Pool

### Semaphore

```text
Many tasks
   |
   v
Semaphore
   |
   v
K active operations
```

### Worker pool

```text
Bounded queue
   |
   +--> Worker
   +--> Worker
   +--> Worker
   |
   v
K active operations
```

A semaphore is useful when task ownership is naturally distributed across existing tasks.

A worker pool is often better when:

- input volume is huge;
- task creation itself is expensive;
- queue backpressure matters;
- work is naturally producer/consumer;
- fairness needs explicit scheduling.

---

# 23. Async Worker Pool Example

```python
import asyncio


async def process(item):
    await asyncio.sleep(0.1)


async def worker(queue: asyncio.Queue):
    while True:
        item = await queue.get()

        if item is None:
            queue.task_done()
            return

        try:
            await process(item)
        finally:
            queue.task_done()


async def main(items):
    queue = asyncio.Queue(maxsize=100)

    workers = [
        asyncio.create_task(worker(queue))
        for _ in range(10)
    ]

    for item in items:
        await queue.put(item)

    await queue.join()

    for _ in workers:
        await queue.put(None)

    await asyncio.gather(*workers)


if __name__ == "__main__":
    asyncio.run(main(range(1000)))
```

The queue provides backpressure.

The worker count bounds active processing.

---

# 24. Layered Concurrency Limits

Real systems often need several limits simultaneously.

Example:

```text
Global limit = 50

API A = 10
API B = 5
API C = 20

Database writes = 15
Downloads = 8
```

Conceptually:

```text
                    GLOBAL 50
                        |
        +---------------+---------------+
        |               |               |
      APIs           Storage          DB
        |               |               |
    per-host         download       DB writes
      limits           limit           limit
```

A global limit protects the entire process.

Local limits protect individual resources.

---

# 25. Per-Host Limits

Suppose one service allows only 10 concurrent requests.

Use a host-specific semaphore:

```python
host_limits = {
    "api.example.com": asyncio.Semaphore(10),
    "billing.example.com": asyncio.Semaphore(3),
}
```

Then:

```python
sem = host_limits[host]

async with sem:
    await fetch(url)
```

This prevents a high-volume source from consuming all application capacity.

---

# 26. Per-API-Key Limits

Different credentials may have different quotas.

Example:

```text
key-A -> 10 concurrent
key-B -> 5 concurrent
key-C -> 2 concurrent
```

Maintain a mapping:

```python
key_limits = {
    "key-A": asyncio.Semaphore(10),
    "key-B": asyncio.Semaphore(5),
    "key-C": asyncio.Semaphore(2),
}
```

This is a resource-management decision, not merely a coding detail.

---

# 27. Per-Database Limits

Suppose:

```text
database pool = 20 connections
```

Do not automatically run:

```text
100 concurrent DB operations
```

If each operation requires a connection, the application may simply move the queue from the application layer into the database pool.

A better design might be:

```text
DB pool = 20
Application DB concurrency = 15
```

leaving headroom for:

- administrative operations;
- health checks;
- other application paths;
- retries;
- connection churn.

---

# 28. Global Limits

Suppose:

```text
API requests = 30
downloads    = 10
DB writes    = 15
```

A global limit can cap the sum:

```text
global = 40
```

Conceptually:

```python
global_limit = asyncio.Semaphore(40)
```

A request may acquire:

```text
global permit
+
resource-specific permit
```

This introduces ordering and deadlock considerations.

---

# 29. Layered Acquisition Order

If an operation needs multiple permits:

```text
global
  |
  v
host
  |
  v
database
  |
  v
work
```

Every code path should acquire resources in a consistent order.

Bad:

```text
Task A: global -> host
Task B: host -> global
```

This can create circular waiting.

Prefer one documented ordering convention.

For example:

```text
global -> source -> database -> operation
```

Consistency matters more than the exact order.

---

# 30. HTTP Client Connection Limits

A semaphore does not replace the HTTP client's connection pool.

You may have:

```text
Application concurrency = 50
HTTP max connections = 20
```

Then at most 20 connections may be actively usable, depending on client semantics.

This mismatch can create a queue inside the HTTP client.

A useful design is:

```text
application concurrency
        <=
HTTP connection capacity
```

unless there is a deliberate reason for additional application-level queuing.

---

# 31. Database Pool Alignment

Similarly:

```text
application DB concurrency = 50
DB pool = 10
```

does not mean 50 database operations execute concurrently.

It means many application tasks may compete for 10 connections.

That can be valid, but it must be intentional.

Prefer:

```text
workload
  |
  v
bounded DB concurrency
  |
  v
connection pool
```

with capacity derived from measured database behavior.

---

# 32. Bounding Memory

Concurrency is not just about connections.

Suppose:

```text
1 request = 50 MB response
```

and:

```text
concurrency = 100
```

Potential in-flight payload memory:

```text
50 MB × 100
=
5 GB
```

And this excludes:

- Python object overhead;
- buffers;
- parsing structures;
- output staging;
- retries;
- logging.

Therefore:

> **A concurrency limit is also a memory-capacity decision when each operation retains data.**

---

# 33. Bounding Bytes Instead of Task Count

A fixed task count is crude when task sizes vary.

Suppose:

```text
Task A = 1 KB
Task B = 500 MB
```

Counting both as one unit is misleading.

A more advanced design can model:

```text
memory budget = 2 GB
```

and account for estimated payload size.

Conceptually:

```text
large task -> consumes many capacity units
small task -> consumes few capacity units
```

This is sometimes called weighted or capacity-based concurrency.

Python's basic semaphore is count-based, so weighted capacity generally requires an additional abstraction.

---

# 34. Variable-Size Payloads

Suppose a source returns:

```text
1 KB
5 KB
10 MB
500 MB
```

A concurrency setting of 20 does not tell you the memory requirement.

Measure or estimate:

```text
expected in-flight bytes
+
processing expansion factor
+
output buffers
```

For example:

```text
20 × 100 MB average payload
=
2 GB raw payload
```

but a JSON parse can expand memory far beyond raw wire size.

Capacity planning must account for representation.

---

# 35. Fairness

A single global semaphore can create unfairness.

Example:

```text
Tenant A -> 10,000 tasks
Tenant B -> 10 tasks
```

If both share:

```text
Semaphore(20)
```

Tenant A may dominate the available permits.

Fairness can be improved with:

- per-tenant semaphores;
- per-source quotas;
- weighted scheduling;
- separate queues;
- round-robin workers;
- reserved capacity.

The correct mechanism depends on business requirements.

---

# 36. Multi-Source Data Pipelines

Example:

```text
CRM       -> 10 concurrent
Payments  -> 5 concurrent
Warehouse -> 20 concurrent
Global    -> 30 concurrent
```

A reasonable architecture is:

```text
                    Global 30
                        |
       +----------------+----------------+
       |                |                |
     CRM 10         Payments 5      Warehouse 20
       |                |                |
       v                v                v
     API A            API B          API C
```

The limits are independent because the resources are independent.

---

# 37. Measuring Concurrency

Do not choose:

```text
concurrency = 100
```

because it "sounds fast."

Measure:

- throughput;
- latency;
- p50;
- p95;
- p99;
- error rate;
- memory;
- CPU;
- connection utilization;
- HTTP 429 rate;
- database wait time.

---

# 38. Throughput

Throughput is work completed per unit time.

Examples:

```text
requests/sec
records/sec
MB/sec
partitions/minute
```

Increasing concurrency may initially increase throughput:

```text
Concurrency
1 -> 2 -> 4 -> 8 -> 16

Throughput
10 -> 20 -> 38 -> 65 -> 80
```

Eventually:

```text
32 -> 70
64 -> 60
```

The system is now overloaded or hitting another bottleneck.

---

# 39. Latency

Latency is the time required for an operation.

Increasing concurrency may produce:

```text
Concurrency 10 -> 20 -> 40

p50:
100ms -> 110ms -> 150ms

p99:
250ms -> 500ms -> 3s
```

Even if throughput increases, tail latency may become unacceptable.

This is why throughput alone is insufficient.

---

# 40. p95 and p99

If 10,000 requests are measured:

```text
p50 = median
p95 = 95% complete at or below this latency
p99 = 99% complete at or below this latency
```

Tail latency matters because the slowest requests often determine:

- pipeline completion time;
- user-facing behavior;
- retry pressure;
- timeout frequency.

Production concurrency tuning should inspect p95/p99, not only averages.

---

# 41. Error Rate

Track:

```text
errors / total operations
```

Examples:

- HTTP 429;
- HTTP 5xx;
- timeout;
- connection failure;
- database saturation;
- memory errors.

A useful experiment table:

| Concurrency | Throughput | p95 | p99 | Error rate |
|---:|---:|---:|---:|---:|
| 5 | 45/s | 180ms | 300ms | 0.0% |
| 10 | 82/s | 210ms | 380ms | 0.1% |
| 20 | 140/s | 300ms | 700ms | 0.4% |
| 40 | 150/s | 900ms | 3.2s | 4.5% |
| 80 | 120/s | 2.1s | 8.0s | 12% |

Do not choose the maximum throughput blindly.

---

# 42. Finding the Optimal Concurrency Level

Run a controlled experiment:

```text
1
2
4
8
16
32
64
```

For each level record:

```text
throughput
p95
p99
error rate
memory
CPU
```

Look for the operating region where:

```text
throughput is high
+
latency remains acceptable
+
errors remain low
+
memory remains safe
```

The optimal value is usually a region, not a mathematically exact point.

---

# 43. Concurrency Experiment Design

Keep other variables stable:

- same dataset;
- same machine;
- same API/source;
- same client configuration;
- same retry policy;
- same payload mix.

Run repeated trials.

Avoid comparing:

```text
concurrency 10 on Monday
```

with:

```text
concurrency 80 on Friday
```

against a variable external service.

The experiment must isolate the variable you are changing.

---

# 44. Adaptive Concurrency

Static:

```text
concurrency = 20
```

Adaptive:

```text
measure system
     |
     v
increase/decrease concurrency
     |
     v
measure again
```

A simple conceptual controller:

```text
healthy
  |
  v
increase slightly
  |
  v
latency/error rises
  |
  v
decrease
  |
  v
stabilize
```

Adaptive concurrency is not a magic solution.

It introduces control-loop complexity.

---

# 45. Latency-Based Adjustment

Conceptually:

```python
if p95_latency < target:
    concurrency += 1
elif p95_latency > target:
    concurrency = max(1, concurrency // 2)
```

A production controller needs:

- smoothing;
- hysteresis;
- minimum/maximum bounds;
- cooldown periods;
- measurement windows;
- protection against oscillation.

Do not change concurrency on every individual request.

---

# 46. Error-Based Adjustment

For example:

```text
HTTP 429 increases
    |
    v
reduce concurrency
    |
    v
observe
```

Likewise:

```text
5xx rate rises
    |
    v
reduce load
```

But error responses can have multiple causes.

Do not assume every error means concurrency is too high.

---

# 47. Adaptive Concurrency Awareness

Adaptive control requires understanding the source of pressure.

Pressure may come from:

- API rate limits;
- network bandwidth;
- CPU;
- memory;
- database locks;
- database connections;
- storage throughput;
- remote service latency.

If the bottleneck is fixed:

```text
disk throughput = 500 MB/s
```

doubling network concurrency cannot make the disk deliver:

```text
1 GB/s
```

The controller must respond to the actual bottleneck.

---

# 48. Production Architecture

A robust bounded-concurrency ingestion system can look like:

```text
                    Producer
                       |
                       v
                 bounded queue
                       |
             +---------+---------+
             |         |         |
             v         v         v
          Worker    Worker    Worker
             |         |         |
             +---------+---------+
                       |
                       v
                 global limit
                       |
          +------------+------------+
          |            |            |
          v            v            v
       API limit    DB limit    Storage limit
          |            |            |
          v            v            v
        source       database      object store
```

In practice the exact layering depends on ownership of each resource.

---

# 49. Data Engineering Use Cases

## API Extraction

Requirement:

```text
maximum 20 concurrent requests
maximum 50 requests/sec
```

Use:

```text
concurrency semaphore = 20
+
rate limiter = 50/sec
```

Measure:

- throughput;
- p95/p99;
- 429 rate.

---

## Object-Storage Downloads

Requirement:

```text
16 concurrent downloads
```

The bound protects:

- sockets;
- bandwidth;
- memory;
- local disk write pressure.

For large objects, task count alone may be insufficient; use size-aware capacity where necessary.

---

## Database Loading

Example:

```text
DB pool = 20
application DB concurrency = 10
```

The lower application limit leaves connection headroom.

Measure:

- transaction latency;
- lock waits;
- commit throughput;
- connection utilization;
- database CPU.

---

## Multi-Source Ingestion

Example:

```text
CRM       = 10
Payments  = 5
Warehouse = 20
Global    = 30
```

This prevents one source from monopolizing the entire application.

---

## File Processing

Use:

```text
bounded queue
+
fixed workers
```

when millions of files or records exist.

This controls both:

- active work;
- queued memory.

---

# 50. Failure Injection

A production engineer should test failure behavior deliberately.

### Permit leak

```python
async def broken(sem):
    await sem.acquire()
    raise RuntimeError("failure")
```

Observe what happens when the permit is never released.

Fix:

```python
async def safe(sem):
    async with sem:
        raise RuntimeError("failure")
```

### Slow operation

Create operations that take:

```text
10 ms
100 ms
1 s
10 s
```

Observe queueing and tail latency.

### HTTP 429

Simulate a source returning:

```text
429 Too Many Requests
```

Verify that the pipeline:

- records the event;
- respects retry policy;
- does not amplify load.

### Memory pressure

Simulate large payloads.

Observe:

- RSS;
- queue depth;
- concurrency;
- processing latency.

---

# 51. Debugging Bounded Concurrency

When the pipeline stalls, ask:

```text
1. Are permits being released?
2. Is the semaphore shared correctly?
3. Is the task waiting on another resource?
4. Is the connection pool smaller than the semaphore?
5. Is the database pool saturated?
6. Is the HTTP client limiting connections?
7. Are tasks waiting in an unbounded queue?
8. Is the source rate-limited?
9. Is memory pressure causing slowdown?
10. Is one tenant consuming all permits?
```

Useful observability fields include:

```text
active_tasks
queued_tasks
available_permits
in_flight_bytes
http_connections
db_connections
p95_latency
p99_latency
error_rate
429_count
```

---

# 52. Common Mistakes

## 1. Unbounded `asyncio.gather`

```python
await asyncio.gather(
    *(fetch(x) for x in million_items)
)
```

**Why:** easy to write.

**Failure:** enormous task count and memory pressure.

**Production pattern:** bounded worker pool or bounded scheduling.

---

## 2. Assuming asyncio automatically provides safety

**Failure:** concurrency is cheap to express but resources remain finite.

**Pattern:** explicitly identify and bound scarce resources.

---

## 3. Using a semaphore without understanding task creation

**Failure:** one million waiting tasks may exist behind a semaphore of 20.

**Pattern:** bound both active work and queued work when scale requires it.

---

## 4. Confusing rate and concurrency

**Failure:** `Semaphore(10)` does not mean 10 requests/sec.

**Pattern:** use separate rate and concurrency controls.

---

## 5. Forgetting release

**Failure:** permits leak and work eventually stalls.

**Pattern:** `async with` or `try/finally`.

---

## 6. Ignoring connection pools

**Failure:** application concurrency exceeds usable connections.

**Pattern:** align limits intentionally.

---

## 7. Ignoring memory

**Failure:** concurrency multiplies in-flight payloads.

**Pattern:** estimate bytes, not only task count.

---

## 8. One global limit for unrelated resources

**Failure:** a fast API and slow database compete for the same capacity.

**Pattern:** layered resource-specific limits plus a global safety bound.

---

## 9. Starvation

**Failure:** one tenant/source consumes all permits.

**Pattern:** per-tenant limits or fair scheduling.

---

## 10. Optimizing throughput only

**Failure:** throughput rises while p99 and error rates become unacceptable.

**Pattern:** tune using throughput, tail latency, errors, and resource utilization together.

---

## 11. Choosing concurrency without measurement

**Failure:** arbitrary configuration.

**Pattern:** run a controlled concurrency experiment.

---

## 12. Creating a semaphore per task

Bad:

```python
async def worker(item):
    sem = asyncio.Semaphore(10)
    async with sem:
        ...
```

Every task gets its own semaphore.

Therefore there is no global bound.

Correct:

```python
sem = asyncio.Semaphore(10)

async def worker(item):
    async with sem:
        ...
```

The semaphore must be shared by the operations it is intended to bound.

---

## 13. Treating adaptive concurrency as magic

Adaptive control can oscillate, react to noisy measurements, or chase the wrong bottleneck.

Start with a measured static bound.

Add adaptation only when the operational benefit justifies the complexity.

---

# 53. Hands-On Exercise

Build a bounded API-ingestion experiment inside your learning project.

Requirements:

1. Generate 1,000 logical requests.
2. Start with unbounded scheduling.
3. Observe task count and memory.
4. Implement `asyncio.Semaphore(10)`.
5. Test limits:
   - 1
   - 5
   - 10
   - 20
   - 40
   - 80
6. Measure throughput.
7. Measure p95 and p99 latency.
8. Measure error rate.
9. Add a simulated 429 response.
10. Add a rate limiter.
11. Compare semaphore-only versus semaphore + rate limiter.
12. Replace mass task creation with a bounded worker pool.
13. Add per-host limits.
14. Add a global limit.
15. Simulate large payloads.
16. Compare task-count bounding with byte-oriented capacity planning.
17. Inject a semaphore leak.
18. Diagnose the resulting stall.
19. Repeat with correct `async with` cleanup.
20. Produce a short conclusion identifying the safe operating region.

Example experiment table:

| Limit | Throughput | p95 | p99 | Errors | Peak memory |
|---:|---:|---:|---:|---:|---:|
| 1 | | | | | |
| 5 | | | | | |
| 10 | | | | | |
| 20 | | | | | |
| 40 | | | | | |
| 80 | | | | | |

The goal is not to find the largest number.

The goal is to find a defensible operating point.

---

# 54. Knowledge Check

1. Why is unbounded concurrency dangerous?
2. What does `Semaphore(10)` mean?
3. What happens when all permits are occupied?
4. Why is `async with sem` preferred?
5. What is a semaphore leak?
6. How does `BoundedSemaphore` differ from `Semaphore`?
7. Does a semaphore limit task creation?
8. Why can one million waiting tasks still be a problem?
9. What is the difference between concurrency and rate?
10. Why might a semaphore of 10 generate more than 10 requests per second?
11. Why should application DB concurrency usually be related to DB pool size?
12. Why can concurrency increase memory usage?
13. Why might per-host limits be required?
14. Why might a global limit also be required?
15. What metrics should guide concurrency tuning?
16. What does p99 tell you that average latency may hide?
17. What is adaptive concurrency?
18. Why can adaptive control become unstable?
19. When is a worker pool preferable to a semaphore?
20. How do you detect a permit leak?

### Answers

**1.** It can exhaust sockets, memory, connections, quotas, and downstream capacity.

**2.** At most ten holders may have permits simultaneously.

**3.** Additional acquisitions wait until a permit is released.

**4.** It guarantees release when the context exits, including exceptions.

**5.** A permit is acquired but never returned, eventually reducing usable capacity.

**6.** `BoundedSemaphore` detects over-release relative to its initial bound.

**7.** No. It can limit execution while still allowing huge numbers of waiting tasks to exist.

**8.** Task objects themselves consume memory and scheduling resources.

**9.** Concurrency is simultaneous active work; rate is work per unit time.

**10.** If operations complete quickly, ten active operations can cycle many times per second.

**11.** Excess application concurrency simply queues behind the pool or overwhelms the database.

**12.** More active operations can mean more simultaneous payloads, buffers, and parsed objects.

**13.** Different hosts have different capacity and rate limits.

**14.** Resource-specific limits alone may still allow the application as a whole to overload itself.

**15.** Throughput, p95/p99, errors, CPU, memory, connection utilization, and queue depth.

**16.** It exposes tail behavior affecting the slowest fraction of requests.

**17.** Dynamically changing concurrency based on measured system behavior.

**18.** Noisy measurements and aggressive control can cause repeated increases and decreases.

**19.** When task creation must also be bounded and producer/consumer backpressure is important.

**20.** Monitor available permits, queue depth, active operations, and tasks stuck waiting indefinitely.

---

# 55. Interview Questions

## Basic

### What is a semaphore?

A semaphore is a synchronization primitive representing a finite number of permits that limit simultaneous access to a resource or operation.

### What does `Semaphore(10)` mean?

At most ten holders can possess permits at the same time.

### What does `acquire()` do?

It obtains a permit or waits until one becomes available.

### What does `release()` do?

It returns a permit and may allow a waiting operation to proceed.

### What is bounded concurrency?

A design where no more than a configured maximum number of operations are active concurrently.

---

## Intermediate

### What is the difference between `Semaphore` and `BoundedSemaphore`?

Both control permit acquisition. `BoundedSemaphore` additionally detects attempts to release beyond its original capacity.

### Why use `async with`?

It makes permit release exception-safe:

```python
async with sem:
    await operation()
```

### What is concurrency versus rate limiting?

Concurrency limits simultaneous operations.

Rate limiting limits operation frequency over time.

### Why can `Semaphore(10)` still cause high memory usage?

Because it can leave an arbitrarily large number of tasks waiting behind ten active operations.

---

## Advanced

### How do you combine a concurrency limit with a rate limit?

Use independent controls:

```text
semaphore -> maximum active requests
rate limiter -> maximum starts/time
```

Both may be required when a source imposes both constraints.

### How do you align application concurrency with a database pool?

Measure database capacity and keep active database work within a safe fraction of available connections, leaving headroom for other operations.

### How do you choose concurrency experimentally?

Sweep several values and measure throughput, p95/p99, error rate, memory, CPU, and resource utilization.

### How do you bound memory when payload sizes vary?

Use estimates of in-flight bytes or weighted capacity rather than relying only on task count.

---

## Senior

### Design a multi-source extraction platform with per-source limits and a global limit.

Use:

```text
global semaphore
+
per-source semaphores
+
rate limits where required
+
bounded queues
+
observability
```

Ensure consistent resource-acquisition order and explicit ownership of each limit.

### How do you prevent one tenant from starving others?

Use per-tenant quotas, fair scheduling, weighted queues, or reserved capacity.

### How do you detect that concurrency is too high?

Look for:

- throughput flattening;
- p95/p99 growth;
- increasing 429/5xx rates;
- connection saturation;
- database wait time;
- memory pressure.

### How would you design adaptive concurrency?

Start with a safe static bound, collect stable measurements, then adjust gradually within hard minimum and maximum bounds with smoothing and cooldown.

---

# 56. Senior-Level Design Exercise

## Scenario

A Data Engineering platform:

- extracts from five APIs;
- downloads objects from cloud storage;
- loads PostgreSQL;
- APIs have different rate limits;
- PostgreSQL has a 30-connection pool;
- payloads range from 1 KB to 500 MB.

Design:

- global concurrency;
- per-source limits;
- rate limits;
- HTTP connection limits;
- database concurrency;
- memory bounds;
- fairness;
- worker pools;
- monitoring;
- adaptive behavior;
- failure recovery.

## Model Solution

### Global limit

Start with a global bound based on measured process capacity.

Example:

```text
Global active operations = 40
```

This is a starting hypothesis, not a universal recommendation.

### Per-source limits

For example:

```text
API A = 10
API B = 5
API C = 8
API D = 4
API E = 3
```

Actual values must come from source limits and experiments.

### Rate limits

Each API gets its own rate policy where required:

```text
A = 50/sec
B = 10/sec
C = 20/sec
...
```

### HTTP connections

Configure the HTTP client pool consistently with application concurrency.

### Database

With a 30-connection pool, do not automatically use 30 active application writes.

Start below capacity, measure database behavior, and reserve headroom.

### Memory

Because payloads range to 500 MB, task count is insufficient.

Use:

```text
global in-flight byte budget
+
bounded queues
+
streaming where possible
```

### Fairness

Use per-source or per-tenant limits so one high-volume source cannot consume every permit.

### Worker pool

Use bounded producer/consumer queues where the input set is very large.

### Monitoring

Measure:

```text
active operations
queue depth
available permits
in-flight bytes
throughput
p95
p99
429
5xx
timeouts
DB connection utilization
memory
CPU
```

### Adaptive behavior

Only after establishing a safe static baseline.

Reduce concurrency when:

- tail latency rises sharply;
- error rates increase;
- source throttling appears.

Increase gradually when:

- capacity remains available;
- latency is stable;
- error rate remains low.

### Failure recovery

Use idempotent tasks and durable task state so failed partitions can be retried without corrupting output.

---

# 57. Production Checklist

## Concurrency

- [ ] Explicit maximum concurrency.
- [ ] No accidental unbounded execution.
- [ ] Task creation is bounded when input volume is huge.
- [ ] Appropriate semaphore or worker-pool design.
- [ ] Per-resource limits where necessary.
- [ ] Global safety limit.

## Rate

- [ ] Source rate limits identified.
- [ ] Concurrency and rate treated separately.
- [ ] Both enforced when necessary.
- [ ] HTTP 429 behavior monitored.

## Resources

- [ ] HTTP connection limits understood.
- [ ] Database pool size understood.
- [ ] File-descriptor capacity considered.
- [ ] Memory capacity considered.
- [ ] CPU considered where relevant.
- [ ] Storage bandwidth considered.

## Correctness

- [ ] Semaphore permits always released.
- [ ] `async with` or `finally` used.
- [ ] No permit leaks.
- [ ] No inconsistent nested acquisition order.
- [ ] No deadlocks introduced by resource ordering.

## Performance

- [ ] Sequential baseline where appropriate.
- [ ] Throughput measured.
- [ ] p95 measured.
- [ ] p99 measured.
- [ ] Error rate measured.
- [ ] Memory measured.
- [ ] Multiple concurrency levels tested.

## Production

- [ ] Per-source limits.
- [ ] Per-tenant limits where needed.
- [ ] Global limit.
- [ ] Monitoring.
- [ ] Alerting.
- [ ] Failure handling.
- [ ] Capacity assumptions documented.
- [ ] Safe operating region documented.

---

# 58. Final Mental Model

```text
                    WORKLOAD
                       |
                       v
               Identify resources
                       |
          +------------+------------+
          |            |            |
          v            v            v
        API          Database      Memory
          |            |            |
          v            v            v
      rate limit   pool limit    byte budget
          |            |            |
          +------------+------------+
                       |
                       v
                 global bound
                       |
                       v
                bounded queue
                       |
                       v
                bounded workers
                       |
                       v
                 process work
                       |
                       v
                measure results
                       |
          +------------+------------+
          |            |            |
       throughput     p99        errors
          |            |            |
          +------------+------------+
                       |
                       v
               tune concurrency
```

The most important principle is:

> **The purpose of bounded concurrency is not simply to make fewer things run. It is to keep the system operating inside the capacity of every important resource while extracting as much useful throughput as the system can safely sustain.**

---

# 59. Exit Criteria

Do not consider this topic complete until you can independently:

- [ ] Explain why unbounded concurrency is dangerous.
- [ ] Explain bounded concurrency.
- [ ] Explain semaphores from first principles.
- [ ] Use `asyncio.Semaphore`.
- [ ] Use `threading.Semaphore`.
- [ ] Explain `BoundedSemaphore`.
- [ ] Prevent semaphore leaks.
- [ ] Use `async with` correctly.
- [ ] Explain concurrency versus rate limiting.
- [ ] Combine concurrency and rate limits.
- [ ] Explain why a semaphore does not necessarily bound task creation.
- [ ] Build a fixed worker pool.
- [ ] Compare semaphore and worker-pool designs.
- [ ] Design layered limits.
- [ ] Design per-host limits.
- [ ] Design per-API-key limits.
- [ ] Align application concurrency with HTTP connection pools.
- [ ] Align application concurrency with database pools.
- [ ] Explain global limits.
- [ ] Explain memory-based bounds.
- [ ] Explain variable payload sizes.
- [ ] Explain fairness.
- [ ] Measure throughput.
- [ ] Measure p95/p99 latency.
- [ ] Measure error rate.
- [ ] Run a concurrency experiment.
- [ ] Select concurrency using evidence.
- [ ] Explain adaptive concurrency.
- [ ] Diagnose overload.
- [ ] Debug semaphore-related failures.
- [ ] Design production-grade bounded concurrency.

---

## Final Takeaway

Do not become the engineer who solves every performance problem by increasing concurrency.

Become the engineer who asks:

```text
What resource is scarce?
        |
        v
How much capacity does it have?
        |
        v
How many operations can safely be active?
        |
        v
Does task creation also need a bound?
        |
        v
Do I need a rate limit as well?
        |
        v
Are there per-source or per-tenant limits?
        |
        v
What do HTTP/database pools permit?
        |
        v
How much memory can be in flight?
        |
        v
What happens to p95/p99 as concurrency rises?
        |
        v
What happens to error rate?
        |
        v
Does measurement support the chosen limit?
```

The production-quality decision is the one supported by explicit resource constraints, controlled experiments, correct cleanup, fair resource allocation, and evidence from real workload behavior.
