# Practice Questions — Concurrency and Parallelism in Practice

## Module Context

**Stage:** 2 — Python for Data Engineering  
**Module:** 2.10 — Concurrency and Parallelism in Practice  
**Purpose:** Progressive practice from foundational Python concurrency concepts to production-oriented Data Engineering design, debugging, benchmarking, and model selection.

> **Scope rule:** These questions are derived from the supplied Module 2.10 practice specification. They focus on the nine learning files and the concepts explicitly identified there.

---

## How to Use This Practice Set

Work through the questions in order.

For each question:

1. Read the problem before looking at the solution.
2. Try to solve the implementation yourself.
3. Compare your reasoning with the supplied solution.
4. Explain why the selected execution model fits the workload.
5. Identify the production failure modes before moving on.
6. For Hard and Advanced questions, treat the problem as a design-review exercise rather than merely a coding exercise.

The intended learning progression is:

**foundations → implementation → debugging → performance → correctness → failure handling → architecture → production engineering**

---

## Coverage Map

| Learning file / topic | Primary questions |
|---|---|
| 01 — Threading and ThreadPoolExecutor | Q1, Q2, Q11, Q16, Q22, Q32 |
| 02 — Multiprocessing and ProcessPoolExecutor | Q3, Q12, Q17, Q24, Q31, Q35 |
| 03 — asyncio, event loop, coroutines and tasks | Q4, Q5, Q13, Q18, Q25, Q33 |
| 04 — TaskGroups, cancellation and timeouts | Q6, Q14, Q19, Q26, Q34, Q38 |
| 05 — Async HTTP extraction with httpx | Q15, Q20, Q21, Q27, Q31, Q37 |
| 06 — Semaphores and bounded concurrency | Q7, Q20, Q23, Q28, Q31, Q37 |
| 07 — Queues and producer-consumer pipelines | Q8, Q15, Q23, Q29, Q34, Q37 |
| 08 — Race conditions, locks and thread safety | Q9, Q16, Q22, Q30, Q32, Q36 |
| 09 — GIL, free-threaded Python and choosing a model | Q10, Q17, Q24, Q31, Q35, Q40 |

---

# Part 1 — Basic

## Question 1 — Start and Join Worker Threads

### Difficulty

Basic

### Topics Covered

- `threading.Thread`
- `start()`
- `join()`
- thread lifecycle

### Problem

Write a Python program that starts three worker threads. Each worker should print its name, perform a small simulated unit of work, and then finish. The main thread must wait for all three workers before printing `All workers completed`.

### Requirements

1. Use `threading.Thread`.
2. Start all three workers.
3. Use `join()` so the main thread waits for completion.
4. Do not use an executor.

### Expected Outcome

The final completion message must appear only after all workers have finished.

### Solution

```python
import threading
import time


def worker(worker_id: int) -> None:
    print(f"Worker {worker_id} started")
    time.sleep(0.2)
    print(f"Worker {worker_id} finished")


def main() -> None:
    threads = [
        threading.Thread(target=worker, args=(worker_id,))
        for worker_id in range(1, 4)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    print("All workers completed")


if __name__ == "__main__":
    main()
```

### How to Solve It

1. Put the worker logic in a normal function.
2. Construct one `Thread` per unit of work.
3. Call `start()` to make each thread runnable.
4. Call `join()` on every thread before reporting completion.

### Explanation

`start()` schedules the thread to execute its target function. It does not mean that the work has finished.

`join()` is the synchronization point. The main thread blocks until the target thread terminates.

The important distinction is:

```text
create → start → execute concurrently → join → continue
```

For a small number of explicit workers, `threading.Thread` is useful for learning and for situations where direct thread lifecycle control is appropriate. For large numbers of homogeneous tasks, `ThreadPoolExecutor` is generally easier to manage.

### Common Mistakes

- Calling `worker()` instead of passing `worker` to `Thread`.
- Calling `join()` immediately after every `start()`, which serializes the work.
- Forgetting to join threads before exiting.
- Assuming `start()` waits for completion.

### Production Considerations

Production code should usually prefer structured ownership of worker lifecycles and explicit shutdown behavior. Avoid daemon threads for critical ingestion or persistence work because the process can exit while important work is still running.

---

## Question 2 — Process Independent I/O Work with ThreadPoolExecutor

### Difficulty

Basic

### Topics Covered

- `ThreadPoolExecutor`
- `Future`
- `result()`
- I/O-bound workloads

### Problem

You have five independent I/O-like operations. Each operation takes approximately 0.2 seconds. Implement the workload using `ThreadPoolExecutor` and collect the returned values.

### Requirements

1. Use `ThreadPoolExecutor`.
2. Submit five independent tasks.
3. Obtain each task's result through its `Future`.
4. Use a small worker count.

### Expected Outcome

The tasks should overlap rather than execute strictly one after another.

### Solution

```python
from concurrent.futures import ThreadPoolExecutor


def fetch_record(record_id: int) -> str:
    import time

    time.sleep(0.2)
    return f"record-{record_id}"


def main() -> None:
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(fetch_record, record_id)
            for record_id in range(1, 6)
        ]

        for future in futures:
            print(future.result())


if __name__ == "__main__":
    main()
```

### How to Solve It

1. Identify the workload as I/O-bound.
2. Create an executor with a bounded worker count.
3. Submit independent tasks.
4. Store the returned `Future` objects.
5. Call `result()` to obtain completed values.

### Explanation

A `Future` represents work that has been submitted but whose result may not yet be available.

Threads are useful here because the workers spend much of their time waiting. While one worker is waiting, another can make progress.

The executor also owns worker lifecycle management, making this safer and simpler than manually creating many threads.

### Common Mistakes

- Creating one executor per task.
- Using an enormous worker count without measuring.
- Forgetting that `future.result()` propagates worker exceptions.
- Treating threads as a universal solution for CPU-bound pure Python work.

### Production Considerations

The worker count should be tied to the downstream service's capacity, connection limits, latency, and acceptable load—not simply to the number of available CPU cores.

---

## Question 3 — Identify a CPU-Bound Workload

### Difficulty

Basic

### Topics Covered

- CPU-bound work
- `ProcessPoolExecutor`
- process isolation
- GIL awareness

### Problem

Classify the following workloads and choose the appropriate initial execution model:

1. Downloading 10,000 API responses.
2. Computing a CPU-heavy pure-Python transformation for millions of records.
3. Waiting for PostgreSQL queries.
4. Compressing data using a native library that releases the GIL.

### Expected Outcome

Explain whether each workload should initially use sequential execution, threads/asyncio, or processes, and state the key reason.

### Solution

| Workload | Initial model | Reason |
|---|---|---|
| API downloads | asyncio or threads | Mostly waiting on network I/O |
| CPU-heavy pure Python | ProcessPoolExecutor | Processes provide CPU parallelism without relying on GIL-free threads |
| PostgreSQL waits | asyncio or threads | Mostly I/O-bound |
| Native compression that releases the GIL | Benchmark threads/processes/library-native parallelism | Native code may execute concurrently outside the Python interpreter |

### How to Solve It

1. Identify whether the bottleneck is waiting or computation.
2. For waiting, consider asyncio or threads.
3. For CPU-heavy pure Python, consider processes.
4. For native extensions, verify whether the native operation releases the GIL and benchmark.
5. Do not choose a model solely from its reputation.

### Explanation

The central decision is workload classification.

```text
I/O wait → concurrency can overlap waiting
CPU-heavy pure Python → process parallelism is often appropriate
native CPU work → benchmark because the native implementation may already parallelize
```

### Common Mistakes

- Saying "asyncio is always faster."
- Saying "multiprocessing is always faster."
- Ignoring whether a native library releases the GIL.
- Ignoring external resource limits.

### Production Considerations

Model selection should be validated with representative measurements including wall-clock time, CPU utilization, memory, throughput, latency, and error behavior.

---

## Question 4 — Coroutine and `await`

### Difficulty

Basic

### Topics Covered

- coroutine functions
- `await`
- event loop
- `asyncio.run()`

### Problem

Write a small asynchronous program with two coroutines. Each should wait for 0.2 seconds and return a result. Run both concurrently and print the results.

### Solution

```python
import asyncio


async def fetch(name: str) -> str:
    await asyncio.sleep(0.2)
    return f"{name} complete"


async def main() -> None:
    first = asyncio.create_task(fetch("first"))
    second = asyncio.create_task(fetch("second"))

    results = await asyncio.gather(first, second)

    for result in results:
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
```

### How to Solve It

1. Define coroutine functions with `async def`.
2. Use `await` for asynchronous waiting.
3. Create tasks so both operations can progress.
4. Await both with `gather()`.
5. Start the event loop with `asyncio.run()`.

### Explanation

A coroutine is an asynchronous computation. `await` gives the event loop an opportunity to run other ready tasks while the awaited operation is not ready.

`asyncio.run()` owns the top-level event-loop lifecycle.

### Common Mistakes

- Calling `time.sleep()` inside the coroutine.
- Forgetting to await a coroutine.
- Creating tasks but never retaining or awaiting them.
- Calling `asyncio.run()` repeatedly inside an already-running event loop.

### Production Considerations

All blocking synchronous calls must be examined carefully before placing them inside async code. Blocking the event loop can stall unrelated tasks.

---

## Question 5 — Recognize a Blocked Event Loop

### Difficulty

Basic

### Topics Covered

- event loop
- blocking calls
- `asyncio.to_thread()`
- synchronous/asynchronous boundaries

### Problem

Identify the problem in this code:

```python
import asyncio
import time


async def work() -> None:
    time.sleep(2)
    print("done")


asyncio.run(work())
```

Explain why it is problematic in a larger async application and correct it.

### Solution

```python
import asyncio
import time


def blocking_work() -> None:
    time.sleep(2)


async def work() -> None:
    await asyncio.to_thread(blocking_work)
    print("done")


asyncio.run(work())
```

### How to Solve It

1. Identify `time.sleep()` as a blocking synchronous operation.
2. Recognize that it executes on the event-loop thread.
3. Move blocking work to a worker thread.
4. Await the thread operation with `asyncio.to_thread()`.

### Explanation

The problem is not the two-second delay itself. The problem is that the event loop cannot run other coroutines during the blocking call.

`asyncio.to_thread()` is useful when an otherwise synchronous blocking function must be integrated into an async application.

### Common Mistakes

- Replacing every synchronous function with `to_thread()` without considering workload characteristics.
- Assuming `to_thread()` turns CPU-heavy pure Python into unlimited parallel computation.
- Using blocking I/O directly inside async functions.

### Production Considerations

Prefer native asynchronous libraries where available. Use thread offloading deliberately for blocking operations that cannot otherwise be made asynchronous.

---

## Question 6 — Basic TaskGroup Usage

### Difficulty

Basic

### Topics Covered

- `TaskGroup`
- structured concurrency
- task ownership
- cancellation

### Problem

Create three asynchronous tasks inside an `asyncio.TaskGroup`. Each task should perform a short asynchronous operation and return normally.

### Solution

```python
import asyncio


async def worker(worker_id: int) -> None:
    await asyncio.sleep(0.1)
    print(f"worker {worker_id} complete")


async def main() -> None:
    async with asyncio.TaskGroup() as group:
        for worker_id in range(1, 4):
            group.create_task(worker(worker_id))

    print("all workers complete")


if __name__ == "__main__":
    asyncio.run(main())
```

### How to Solve It

1. Create the `TaskGroup` inside an async context.
2. Create child tasks through the group.
3. Let the context manager own the task lifecycle.
4. Continue only after the group completes successfully.

### Explanation

`TaskGroup` provides structured concurrency. The parent scope owns the child tasks, and task completion and failure are tied to that scope.

### Common Mistakes

- Creating tasks outside the group and assuming the group owns them.
- Forgetting that a child exception affects the group.
- Treating `TaskGroup` as merely another spelling of `gather()`.

### Production Considerations

Structured task ownership makes cancellation and failure propagation easier to reason about in production pipelines.

---

## Question 7 — Protect a Resource with a Semaphore

### Difficulty

Basic

### Topics Covered

- `asyncio.Semaphore`
- bounded concurrency
- permit acquisition/release

### Problem

You need to ensure that at most three asynchronous operations execute at once. Write a semaphore-protected worker.

### Solution

```python
import asyncio


async def operation(item: int, semaphore: asyncio.Semaphore) -> None:
    async with semaphore:
        print(f"starting {item}")
        await asyncio.sleep(0.2)
        print(f"finished {item}")


async def main() -> None:
    semaphore = asyncio.Semaphore(3)

    tasks = [
        asyncio.create_task(operation(item, semaphore))
        for item in range(10)
    ]

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
```

### How to Solve It

1. Create the semaphore with three permits.
2. Put the protected operation inside `async with semaphore`.
3. Create tasks for the work.
4. Await all tasks.

### Explanation

Only three tasks can hold a semaphore permit simultaneously.

The semaphore limits protected work, but it does not inherently limit the number of task objects created. That distinction becomes important for very large workloads.

### Common Mistakes

- Acquiring the semaphore but forgetting to release it.
- Assuming the semaphore limits task creation.
- Setting the limit to an arbitrary huge number.

### Production Considerations

For millions of records, combine bounded concurrency with bounded task creation or a worker queue to control memory.

---

## Question 8 — Basic Producer-Consumer Queue

### Difficulty

Basic

### Topics Covered

- `asyncio.Queue`
- `put()`
- `get()`
- `task_done()`
- `join()`

### Problem

Build a simple asynchronous producer-consumer pipeline. The producer should put ten integers into an `asyncio.Queue`; one consumer should process them and call `task_done()`.

### Solution

```python
import asyncio


async def producer(queue: asyncio.Queue[int]) -> None:
    for item in range(10):
        await queue.put(item)


async def consumer(queue: asyncio.Queue[int]) -> None:
    while True:
        item = await queue.get()
        try:
            print(f"processing {item}")
            await asyncio.sleep(0.05)
        finally:
            queue.task_done()


async def main() -> None:
    queue: asyncio.Queue[int] = asyncio.Queue()

    consumer_task = asyncio.create_task(consumer(queue))

    await producer(queue)
    await queue.join()

    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    asyncio.run(main())
```

### How to Solve It

1. Create a queue.
2. Start the consumer.
3. Put work into the queue.
4. Mark each item complete with `task_done()`.
5. Wait for `queue.join()`.
6. Cancel the long-lived consumer.

### Explanation

`queue.join()` waits until every item that has been added has received a matching `task_done()` call.

### Common Mistakes

- Forgetting `task_done()`.
- Calling `task_done()` more than once.
- Calling `join()` before any consumer can process the queue.
- Leaving the consumer running indefinitely.

### Production Considerations

Use `maxsize` when queue growth must be bounded. A bounded queue provides a natural form of backpressure.

---

## Question 9 — Detect a Race Condition

### Difficulty

Basic

### Topics Covered

- race conditions
- shared mutable state
- `threading.Lock`

### Problem

Why can this program produce an incorrect counter?

```python
import threading

counter = 0


def increment() -> None:
    global counter

    for _ in range(10_000):
        counter += 1
```

Explain the correctness problem and show a lock-based solution.

### Solution

```python
import threading

counter = 0
lock = threading.Lock()


def increment() -> None:
    global counter

    for _ in range(10_000):
        with lock:
            counter += 1
```

### How to Solve It

1. Identify `counter` as shared mutable state.
2. Identify `counter += 1` as a read-modify-write operation.
3. Protect the critical section with a lock.
4. Ensure every writer uses the same synchronization policy.

### Explanation

The important issue is the logical operation:

```text
read counter
modify value
write counter
```

Concurrent access can interleave these steps.

A lock makes the critical section mutually exclusive.

### Common Mistakes

- Assuming the GIL makes application-level compound operations safe.
- Locking only some writers.
- Holding the lock around slow unrelated work.

### Production Considerations

Avoid shared mutable state when message passing, immutable values, per-task state, or partition ownership can provide simpler correctness.

---

## Question 10 — Explain the GIL at a Practical Level

### Difficulty

Basic

### Topics Covered

- GIL
- CPU-bound pure Python
- I/O-bound work
- free-threading awareness

### Problem

Explain why Python threads can still be useful for I/O-bound work even though CPython has historically used a Global Interpreter Lock. Then explain why CPU-bound pure-Python workloads often require a different strategy.

### Solution

The practical model is:

- During blocking I/O, a thread can wait while another thread runs.
- Therefore threads can overlap I/O waits.
- For CPU-bound pure-Python bytecode, the GIL historically limits simultaneous execution of Python bytecode in one interpreter.
- Processes can provide parallel CPU execution across interpreter processes.
- Free-threaded Python changes this trade-off, but dependency compatibility and actual benchmark results still matter.

### How to Solve It

1. Separate I/O waiting from CPU computation.
2. Ask whether the work executes mostly in Python bytecode or native code.
3. Consider whether the library releases the GIL.
4. Consider processes or free-threaded builds for suitable CPU workloads.
5. Benchmark the real workload.

### Explanation

The GIL is not equivalent to "Python cannot do concurrency." Concurrency and parallel CPU execution are different concepts.

### Common Mistakes

- Saying the GIL prevents all concurrency.
- Saying free-threaded Python automatically makes every threaded program faster.
- Ignoring native extensions.

### Production Considerations

Treat free-threaded Python as a model-selection option requiring dependency compatibility testing and benchmarking rather than as a universal replacement for processes or asyncio.

---

# Part 2 — Moderate

## Question 11 — Collect Thread Results with `as_completed()`

### Difficulty

Moderate

### Topics Covered

- `ThreadPoolExecutor`
- `Future`
- `as_completed()`
- I/O concurrency
- error propagation

### Problem

Five API calls have different latencies. You want to process each result immediately when it completes rather than waiting in submission order. Implement the pattern.

### Solution

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


def fetch(record_id: int) -> str:
    time.sleep(0.05 * record_id)
    return f"record-{record_id}"


def main() -> None:
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(fetch, record_id): record_id
            for record_id in range(1, 6)
        }

        for future in as_completed(futures):
            record_id = futures[future]
            try:
                result = future.result()
            except Exception as exc:
                print(f"record {record_id} failed: {exc}")
            else:
                print(result)


if __name__ == "__main__":
    main()
```

### How to Solve It

1. Submit independent I/O tasks.
2. Map each `Future` to its input identity.
3. Iterate with `as_completed()`.
4. Call `result()` inside the completion loop.
5. Handle exceptions per completed task.

### Explanation

`as_completed()` is useful when completion order matters operationally. A slow first task does not prevent already-completed later tasks from being processed.

### Common Mistakes

- Losing the mapping between the future and the original record.
- Assuming `as_completed()` suppresses exceptions.
- Calling `result()` without an exception boundary when partial failure is expected.

### Production Considerations

For large inputs, avoid submitting millions of tasks at once. Bound submission or use a queue/worker design.

---

## Question 12 — Make a ProcessPool Worker Picklable

### Difficulty

Moderate

### Topics Covered

- `ProcessPoolExecutor`
- pickling
- importable worker functions
- `__main__` guard

### Problem

A developer wrote:

```python
from concurrent.futures import ProcessPoolExecutor


def main():
    values = [1, 2, 3]

    with ProcessPoolExecutor() as executor:
        results = list(
            executor.map(
                lambda value: value * value,
                values,
            )
        )

    print(results)
```

Explain why the worker design is fragile or invalid for process execution and rewrite it correctly.

### Solution

```python
from concurrent.futures import ProcessPoolExecutor


def square(value: int) -> int:
    return value * value


def main() -> None:
    values = [1, 2, 3]

    with ProcessPoolExecutor() as executor:
        results = list(executor.map(square, values))

    print(results)


if __name__ == "__main__":
    main()
```

### How to Solve It

1. Move the worker to a top-level importable function.
2. Avoid lambdas and nested functions as process workers.
3. Protect process-starting code with `if __name__ == "__main__":`.
4. Pass simple serializable arguments.

### Explanation

Process workers cross a process boundary. Arguments and callable information must be compatible with the process-start mechanism and serialization requirements.

### Common Mistakes

- Using nested functions.
- Using lambdas.
- Starting process pools during module import.
- Passing huge Python objects unnecessarily.

### Production Considerations

Prefer passing partition identifiers, paths, or compact descriptors rather than giant DataFrames. Be explicit about start methods when deployment environments make the default behavior significant.

---

## Question 13 — Gather Independent Async Operations

### Difficulty

Moderate

### Topics Covered

- `asyncio.gather()`
- task scheduling
- exception behavior
- asynchronous I/O

### Problem

Three independent asynchronous API calls should execute concurrently. One may fail. Write code that collects successful results while clearly handling an exception.

### Solution

```python
import asyncio


async def fetch(name: str) -> str:
    await asyncio.sleep(0.1)

    if name == "bad":
        raise RuntimeError("API failure")

    return f"{name} result"


async def main() -> None:
    results = await asyncio.gather(
        fetch("a"),
        fetch("bad"),
        fetch("c"),
        return_exceptions=True,
    )

    for result in results:
        if isinstance(result, Exception):
            print(f"failed: {result}")
        else:
            print(f"success: {result}")


if __name__ == "__main__":
    asyncio.run(main())
```

### How to Solve It

1. Identify that the requests are independent.
2. Await them together with `gather()`.
3. Decide explicitly whether one failure should abort result collection.
4. Use `return_exceptions=True` when partial result inspection is required.

### Explanation

`gather()` is convenient for collecting results from multiple awaitables. Its exception semantics must be chosen deliberately.

### Common Mistakes

- Assuming all tasks are equivalent to a structured `TaskGroup`.
- Swallowing exceptions without recording which operation failed.
- Using unbounded gather for millions of inputs.

### Production Considerations

For large pipelines, combine concurrency limits, bounded task creation, deadlines, retries, and explicit failure handling.

---

## Question 14 — Add an Operation Timeout

### Difficulty

Moderate

### Topics Covered

- `asyncio.timeout()`
- cancellation
- operation deadlines
- cleanup

### Problem

An API operation must complete within two seconds. If it does not, cancel it and return a timeout result.

### Solution

```python
import asyncio


async def fetch() -> str:
    await asyncio.sleep(5)
    return "data"


async def safe_fetch() -> str:
    try:
        async with asyncio.timeout(2):
            return await fetch()
    except TimeoutError:
        return "timed out"


async def main() -> None:
    print(await safe_fetch())


if __name__ == "__main__":
    asyncio.run(main())
```

### How to Solve It

1. Define the deadline around the operation.
2. Use `asyncio.timeout()`.
3. Handle `TimeoutError` at the boundary where timeout policy is decided.
4. Ensure the underlying coroutine can clean up correctly when cancelled.

### Explanation

Timeouts are not merely error messages; they are cancellation boundaries. A timed-out operation must release resources and leave the pipeline in a consistent state.

### Common Mistakes

- Applying a timeout only to a later step rather than the actual operation.
- Catching cancellation indiscriminately.
- Ignoring cleanup.

### Production Considerations

Use operation-level and overall deadlines where appropriate. Make retries aware of the remaining deadline rather than restarting indefinitely.

---

## Question 15 — Bound Concurrent HTTP Requests

### Difficulty

Moderate

### Topics Covered

- `httpx.AsyncClient`
- semaphore
- connection pooling
- bounded concurrency

### Problem

Implement an asynchronous fetcher that requests several URLs while allowing at most three requests to execute concurrently.

### Solution

```python
import asyncio
import httpx


async def fetch(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    url: str,
) -> tuple[str, int]:
    async with semaphore:
        response = await client.get(url)
        response.raise_for_status()
        return url, response.status_code


async def main() -> None:
    urls = [
        "https://example.com",
        "https://example.org",
        "https://example.net",
        "https://www.iana.org",
        "https://www.python.org",
    ]

    semaphore = asyncio.Semaphore(3)

    async with httpx.AsyncClient(timeout=10.0) as client:
        results = await asyncio.gather(
            *(fetch(client, semaphore, url) for url in urls)
        )

    for result in results:
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
```

### How to Solve It

1. Reuse one `AsyncClient`.
2. Create a semaphore with the desired concurrency limit.
3. Acquire the permit around the HTTP operation.
4. Release automatically with `async with`.
5. Gather the independent operations.

### Explanation

The client provides connection pooling, while the semaphore provides an application-level concurrency bound.

These are related but different controls.

### Common Mistakes

- Creating a new HTTP client for every request.
- Setting concurrency far above the upstream service's capacity.
- Treating a concurrency limit as a rate limit.

### Production Considerations

Align HTTP connection limits, semaphore limits, API-key limits, per-host limits, retries, timeouts, and upstream rate-limit policies.

---

## Question 16 — Fix a Thread-Safety Bug

### Difficulty

Moderate

### Topics Covered

- shared mutable state
- `threading.Lock`
- thread safety
- critical sections

### Problem

The following worker updates a shared dictionary:

```python
counts = {}


def record(category: str) -> None:
    counts[category] = counts.get(category, 0) + 1
```

Multiple threads call `record()`. Explain the correctness risk and provide a safe version.

### Solution

```python
import threading

counts: dict[str, int] = {}
counts_lock = threading.Lock()


def record(category: str) -> None:
    with counts_lock:
        counts[category] = counts.get(category, 0) + 1
```

### How to Solve It

1. Identify the dictionary as shared mutable state.
2. Identify the read-modify-write sequence.
3. Protect the whole logical update.
4. Keep unrelated work outside the critical section.

### Explanation

Even if individual dictionary operations have implementation-level guarantees in some circumstances, the combined read-modify-write operation must be reasoned about as a critical section.

### Common Mistakes

- Assuming the GIL guarantees application-level correctness.
- Locking only the write.
- Using a lock around network requests.

### Production Considerations

For high-throughput pipelines, consider partition-local state followed by aggregation, rather than forcing every worker through one global lock.

---

## Question 17 — ProcessPool with `chunksize`

### Difficulty

Moderate

### Topics Covered

- `ProcessPoolExecutor`
- `map()`
- `chunksize`
- task granularity

### Problem

You have 500,000 small CPU-bound transformations. Explain why submitting each item as a separate fine-grained process task can be inefficient and show a `map()` call using `chunksize`.

### Solution

```python
from concurrent.futures import ProcessPoolExecutor


def transform(value: int) -> int:
    total = 0
    for _ in range(10_000):
        total += value * value
    return total


def main() -> None:
    values = range(500_000)

    with ProcessPoolExecutor() as executor:
        results = executor.map(
            transform,
            values,
            chunksize=1_000,
        )

        # Consume incrementally rather than retaining all results.
        for result in results:
            pass


if __name__ == "__main__":
    main()
```

### How to Solve It

1. Recognize that process boundaries have overhead.
2. Identify the tasks as small relative to that overhead.
3. Batch inputs with `chunksize`.
4. Measure multiple chunk sizes rather than assuming one is optimal.

### Explanation

`chunksize` can reduce scheduling and IPC overhead by giving each process larger batches of work.

### Common Mistakes

- Assuming the largest chunksize is always fastest.
- Using huge chunks when load balance matters.
- Ignoring serialization and result-transfer costs.

### Production Considerations

Benchmark representative data. Consider partition-level processing when the workload naturally maps to files, partitions, or other durable units.

---

## Question 18 — Decide Whether `to_thread()` Is Appropriate

### Difficulty

Moderate

### Topics Covered

- `asyncio.to_thread()`
- blocking libraries
- executor integration
- synchronous/asynchronous boundaries

### Problem

An async ingestion service must call a blocking SDK that cannot be replaced. The SDK spends most of its time waiting on network I/O. Should it run directly in the event loop or through `asyncio.to_thread()`?

### Solution

Use `asyncio.to_thread()` as an integration boundary:

```python
import asyncio


def blocking_sdk_call(record_id: int) -> str:
    # Represents a blocking third-party SDK.
    import time

    time.sleep(0.5)
    return f"record-{record_id}"


async def fetch(record_id: int) -> str:
    return await asyncio.to_thread(blocking_sdk_call, record_id)
```

### How to Solve It

1. Determine whether the SDK blocks.
2. Determine whether its work is primarily I/O wait.
3. Keep the event loop free by offloading the blocking call.
4. Bound the number of such calls if the SDK or downstream service has limits.

### Explanation

`to_thread()` is useful for bridging synchronous blocking libraries into asynchronous applications.

### Common Mistakes

- Calling the blocking SDK directly from the event loop.
- Assuming `to_thread()` makes CPU-heavy pure Python parallel.
- Creating unlimited offloaded operations.

### Production Considerations

Treat the thread pool and downstream SDK capacity as resources that need explicit bounds.

---

## Question 19 — Understand TaskGroup Failure Propagation

### Difficulty

Moderate

### Topics Covered

- `TaskGroup`
- cancellation
- `ExceptionGroup`
- `except*`

### Problem

Three child tasks run inside a `TaskGroup`. One raises an exception. Explain what should happen to sibling tasks and show how the caller can handle the resulting exception group.

### Solution

```python
import asyncio


async def worker(name: str) -> None:
    if name == "bad":
        raise ValueError("bad input")

    try:
        await asyncio.sleep(2)
    finally:
        print(f"{name}: cleanup")


async def main() -> None:
    try:
        async with asyncio.TaskGroup() as group:
            group.create_task(worker("good-1"))
            group.create_task(worker("bad"))
            group.create_task(worker("good-2"))
    except* ValueError as exc_group:
        print(f"handled {len(exc_group.exceptions)} ValueError(s)")


if __name__ == "__main__":
    asyncio.run(main())
```

### How to Solve It

1. Create all children inside the group.
2. Allow one child to fail.
3. Understand that sibling tasks are cancelled.
4. Ensure cleanup runs.
5. Handle the resulting `ExceptionGroup` with `except*`.

### Explanation

Structured concurrency ties sibling task lifetime to the parent scope. This makes failure propagation explicit.

### Common Mistakes

- Assuming siblings continue normally after a fatal group failure.
- Swallowing cancellation in cleanup.
- Treating `ExceptionGroup` as an ordinary single exception.

### Production Considerations

Failure policy should distinguish retryable failures, permanent data errors, cancellation, and shutdown signals.

---

## Question 20 — Concurrency Limit Is Not a Rate Limit

### Difficulty

Moderate

### Topics Covered

- concurrency vs rate
- semaphores
- API limits
- HTTP extraction

### Problem

An upstream API permits at most 10 concurrent requests and at most 100 requests per minute. Explain why:

```python
semaphore = asyncio.Semaphore(10)
```

does not by itself enforce both policies.

### Solution

A semaphore enforces the number of in-flight operations. It does not measure how many operations started during a time window.

A separate rate-limiting mechanism is required for the 100-requests-per-minute policy.

### How to Solve It

1. Define concurrency as "in flight at the same time."
2. Define rate as "starts over time."
3. Use the semaphore for the concurrency bound.
4. Add a rate limiter or equivalent scheduling policy for the time-window constraint.

### Explanation

Ten permits could be reused very quickly. If requests complete in 50 ms, the application could issue far more than 100 requests per minute while never having more than ten requests in flight.

### Common Mistakes

- Treating a semaphore as a rate limiter.
- Assuming HTTP connection limits enforce business-level rate limits.
- Ignoring `Retry-After`.

### Production Considerations

Use layered controls:

```text
global concurrency
→ per-host concurrency
→ API-key concurrency
→ rate limit
→ HTTP connection pool
→ database/storage limits
```

The exact policy should reflect the upstream contract.

---

# Part 3 — Hard

## Question 21 — Build a Retry-Aware Async HTTP Worker

### Difficulty

Hard

### Topics Covered

- `httpx.AsyncClient`
- retries
- `Retry-After`
- semaphore
- timeout
- error classification

### Problem

Design an async HTTP worker for an API that can return:

- `200` — success
- `429` — rate limited, possibly with `Retry-After`
- `500` — transient server error
- other `4xx` — likely non-retryable

The worker must use bounded concurrency and a request timeout.

### Solution

```python
import asyncio
import random
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

import httpx


def retry_after_seconds(response: httpx.Response) -> float | None:
    value = response.headers.get("Retry-After")
    if not value:
        return None

    try:
        return max(0.0, float(value))
    except ValueError:
        try:
            target = parsedate_to_datetime(value)
            if target.tzinfo is None:
                target = target.replace(tzinfo=timezone.utc)
            return max(
                0.0,
                (target - datetime.now(timezone.utc)).total_seconds(),
            )
        except (TypeError, ValueError):
            return None


async def fetch(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    url: str,
    max_attempts: int = 4,
) -> httpx.Response:
    for attempt in range(1, max_attempts + 1):
        try:
            async with semaphore:
                response = await client.get(url)

            if response.status_code == 429:
                if attempt == max_attempts:
                    response.raise_for_status()

                delay = retry_after_seconds(response)
                if delay is None:
                    delay = min(2 ** (attempt - 1), 10) + random.random()

                await asyncio.sleep(delay)
                continue

            if response.status_code >= 500:
                if attempt == max_attempts:
                    response.raise_for_status()

                delay = min(2 ** (attempt - 1), 10) + random.random()
                await asyncio.sleep(delay)
                continue

            response.raise_for_status()
            return response

        except httpx.TimeoutException:
            if attempt == max_attempts:
                raise

            delay = min(2 ** (attempt - 1), 10) + random.random()
            await asyncio.sleep(delay)

    raise RuntimeError("unreachable")


async def main() -> None:
    semaphore = asyncio.Semaphore(10)

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await fetch(
            client,
            semaphore,
            "https://example.com",
        )
        print(response.status_code)


if __name__ == "__main__":
    asyncio.run(main())
```

### How to Solve It

1. Reuse one async HTTP client.
2. Bound concurrent HTTP operations.
3. Classify status codes.
4. Respect `Retry-After` when supplied.
5. Apply bounded exponential backoff for suitable transient failures.
6. Set a request timeout.
7. Stop after a finite number of attempts.

### Explanation

Retries are part of concurrency control because retries create additional upstream load. An implementation that retries immediately and indefinitely can turn a transient outage into a sustained overload.

The semaphore should protect actual in-flight requests. Sleeping between retries should not unnecessarily occupy an HTTP concurrency permit.

### Common Mistakes

- Retrying all `4xx` responses.
- Ignoring `Retry-After`.
- Retrying indefinitely.
- Holding a semaphore permit while sleeping between attempts.
- Creating a new client for every request.

### Production Considerations

Add metrics for attempts, status classes, retry delay, timeout count, throughput, and latency percentiles. Ensure downstream writes are idempotent before enabling aggressive retry behavior.

---

## Question 22 — Diagnose a Deadlock

### Difficulty

Hard

### Topics Covered

- `threading.Lock`
- lock ordering
- deadlocks
- critical sections

### Problem

Two threads execute:

```python
lock_a = threading.Lock()
lock_b = threading.Lock()


def worker_one():
    with lock_a:
        with lock_b:
            pass


def worker_two():
    with lock_b:
        with lock_a:
            pass
```

Explain the deadlock scenario and provide a corrected design.

### Solution

Use a consistent lock ordering:

```python
import threading

lock_a = threading.Lock()
lock_b = threading.Lock()


def worker_one():
    with lock_a:
        with lock_b:
            pass


def worker_two():
    with lock_a:
        with lock_b:
            pass
```

A stronger design is to reduce shared state so that both locks are unnecessary.

### How to Solve It

1. Identify the acquisition order in each worker.
2. Observe that each thread can hold one lock while waiting for the other.
3. Establish one global lock ordering.
4. Apply it consistently.
5. Prefer avoiding multiple locks where message passing or ownership partitioning can work.

### Explanation

The original design permits:

```text
Thread A owns A → waits for B
Thread B owns B → waits for A
```

Neither can progress.

### Common Mistakes

- Adding more retries around the deadlock.
- Assuming the scheduler will resolve it.
- Fixing only one code path.

### Production Considerations

Document lock ordering, minimize critical sections, and use lock timeouts where appropriate for diagnostics. Avoid holding locks while performing network or database operations.

---

## Question 23 — Design a Bounded Producer-Consumer Pipeline

### Difficulty

Hard

### Topics Covered

- `asyncio.Queue`
- `maxsize`
- backpressure
- multi-stage pipeline
- batching

### Problem

Design a pipeline:

```text
API extraction → parsing → transformation → batch loading
```

The extractor can produce data faster than the loader can consume it. Show how bounded queues prevent unlimited memory growth.

### Solution

```python
import asyncio


async def extractor(queue: asyncio.Queue[dict]) -> None:
    for record_id in range(100):
        await queue.put({"id": record_id, "raw": f"value-{record_id}"})


async def transformer(
    input_queue: asyncio.Queue[dict],
    output_queue: asyncio.Queue[dict],
) -> None:
    while True:
        record = await input_queue.get()
        try:
            transformed = {
                "id": record["id"],
                "value": record["raw"].upper(),
            }
            await output_queue.put(transformed)
        finally:
            input_queue.task_done()


async def loader(queue: asyncio.Queue[dict]) -> None:
    batch: list[dict] = []

    while True:
        record = await queue.get()
        try:
            batch.append(record)

            if len(batch) >= 10:
                await asyncio.sleep(0.2)  # Simulated database load.
                batch.clear()
        finally:
            queue.task_done()


async def main() -> None:
    raw_queue: asyncio.Queue[dict] = asyncio.Queue(maxsize=20)
    transformed_queue: asyncio.Queue[dict] = asyncio.Queue(maxsize=20)

    extractor_task = asyncio.create_task(extractor(raw_queue))
    transformer_task = asyncio.create_task(
        transformer(raw_queue, transformed_queue)
    )
    loader_task = asyncio.create_task(loader(transformed_queue))

    await extractor_task
    await raw_queue.join()

    transformer_task.cancel()
    try:
        await transformer_task
    except asyncio.CancelledError:
        pass

    await transformed_queue.join()

    loader_task.cancel()
    try:
        await loader_task
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    asyncio.run(main())
```

### How to Solve It

1. Put a bounded queue between each stage.
2. Make producers await `put()`.
3. Make consumers call `task_done()`.
4. Wait for stage completion with `join()`.
5. Shut down long-lived workers explicitly.

### Explanation

When the loader slows down, the transformed queue fills. Eventually the transformer blocks on `put()`, which causes the raw queue to fill, which eventually slows the extractor.

That propagation is backpressure.

### Common Mistakes

- Using an unbounded queue for millions of records.
- Forgetting `task_done()`.
- Treating queue size as merely a performance parameter rather than a memory-control mechanism.
- Shutting down downstream workers before queued work is drained.

### Production Considerations

Monitor queue depth and age, batch sizes, throughput, processing latency, and error counts. Add dead-letter handling for records that cannot be processed successfully.

---

## Question 24 — CPU Transformation after Async Extraction

### Difficulty

Hard

### Topics Covered

- asyncio
- CPU-bound work
- `ProcessPoolExecutor`
- GIL
- mixed architecture

### Problem

An async service downloads JSON records efficiently, but a pure-Python transformation consumes most CPU time. Design a simple architecture that keeps HTTP extraction asynchronous and moves CPU-heavy work to processes.

### Solution

```python
import asyncio
from concurrent.futures import ProcessPoolExecutor


def cpu_transform(record: dict) -> dict:
    value = record["value"]

    total = 0
    for number in value:
        total += number * number

    return {
        "id": record["id"],
        "score": total,
    }


async def fetch_records() -> list[dict]:
    await asyncio.sleep(0.1)
    return [
        {"id": 1, "value": list(range(10_000))},
        {"id": 2, "value": list(range(10_000))},
    ]


async def main() -> None:
    records = await fetch_records()

    loop = asyncio.get_running_loop()

    with ProcessPoolExecutor() as executor:
        transformed = await asyncio.gather(
            *(
                loop.run_in_executor(executor, cpu_transform, record)
                for record in records
            )
        )

    print(transformed)


if __name__ == "__main__":
    asyncio.run(main())
```

### How to Solve It

1. Keep network I/O in asyncio.
2. Identify CPU-heavy pure-Python transformation as a separate stage.
3. Use a process pool for that stage.
4. Pass process-friendly data across the boundary.
5. Bound the amount of work submitted.

### Explanation

A mixed architecture can be appropriate when one part of the workload is I/O-bound and another is CPU-bound.

```text
async HTTP
    ↓
bounded records
    ↓
process pool
    ↓
database/storage
```

### Common Mistakes

- Running CPU-heavy pure Python directly on the event loop.
- Creating a process per record.
- Passing huge data structures unnecessarily.
- Forgetting process startup and serialization costs.

### Production Considerations

Partition work into appropriately sized units. Measure serialization, CPU time, memory, and process utilization rather than assuming the process pool improves end-to-end performance.

---

## Question 25 — Async Iterator for Streaming Results

### Difficulty

Hard

### Topics Covered

- async iterators
- async generators
- streaming
- bounded processing

### Problem

Implement an async generator that yields records one at a time from a simulated remote source. Consume it without first materializing every record in memory.

### Solution

```python
import asyncio
from collections.abc import AsyncIterator


async def stream_records() -> AsyncIterator[dict]:
    for record_id in range(100):
        await asyncio.sleep(0.01)
        yield {"id": record_id}


async def consume() -> None:
    async for record in stream_records():
        print(record["id"])


if __name__ == "__main__":
    asyncio.run(consume())
```

### How to Solve It

1. Use `async def` plus `yield`.
2. Return an async iterator.
3. Consume with `async for`.
4. Process each record incrementally.

### Explanation

Async iteration provides a natural streaming boundary. It avoids requiring the entire result set to be resident in memory before processing starts.

### Common Mistakes

- Converting the generator to a huge list.
- Blocking inside the async generator.
- Assuming streaming automatically solves every memory problem.

### Production Considerations

Streaming should still be paired with bounded downstream queues, bounded batches, and explicit cancellation/shutdown handling.

---

## Question 26 — Diagnose Incorrect Cancellation Handling

### Difficulty

Hard

### Topics Covered

- `CancelledError`
- cancellation
- cleanup
- graceful shutdown

### Problem

Review:

```python
async def worker():
    try:
        while True:
            await do_work()
    except asyncio.CancelledError:
        print("cancelled")
        return
```

Explain why silently returning can be problematic and show a safer pattern when the task does not own a policy to consume cancellation.

### Solution

```python
import asyncio


async def worker() -> None:
    try:
        while True:
            await do_work()
    except asyncio.CancelledError:
        print("cancelled")
        raise


async def do_work() -> None:
    await asyncio.sleep(1)
```

### How to Solve It

1. Recognize cancellation as a control-flow signal.
2. Perform required cleanup in `finally`.
3. Re-raise `CancelledError` unless the task deliberately owns the policy to consume it.
4. Let the parent scope observe cancellation.

### Explanation

Swallowing cancellation can make shutdown semantics incorrect. A parent waiting for cancellation to propagate may instead observe apparent successful completion.

### Common Mistakes

- Treating cancellation as an ordinary failure.
- Catching `Exception` and assuming cancellation is handled correctly in all contexts.
- Forgetting cleanup.

### Production Considerations

Graceful shutdown should coordinate signal handling, task cancellation, queue draining, checkpointing, and resource closure.

---

## Question 27 — Sequential Pagination versus Concurrent Pagination

### Difficulty

Hard

### Topics Covered

- async HTTP
- pagination
- concurrency
- correctness
- API semantics

### Problem

An API returns:

```json
{
  "items": [...],
  "next": "/items?page=2"
}
```

The next page URL is only known after reading the current page. Explain why blindly launching all pages concurrently may be impossible or incorrect. Show the correct sequential pagination pattern.

### Solution

```python
import httpx


async def paginate(client: httpx.AsyncClient, url: str):
    while url:
        response = await client.get(url)
        response.raise_for_status()

        payload = response.json()

        for item in payload["items"]:
            yield item

        url = payload.get("next")
```

### How to Solve It

1. Identify whether page N+1 can be known before page N.
2. If the server supplies the next cursor only after page N, the dependency is sequential.
3. Process or stream each page before following its next link.
4. Use concurrency only where the API exposes independently addressable work.

### Explanation

Concurrency is not automatically correct. Some APIs expose cursor dependencies that impose a sequential control flow.

### Common Mistakes

- Inventing page numbers when the API uses opaque cursors.
- Issuing pages concurrently without knowing that they are independent.
- Ignoring server-provided ordering semantics.

### Production Considerations

Checkpoint the cursor after successful processing and make downstream writes idempotent so the extraction can resume safely.

---

## Question 28 — Diagnose Excessive Concurrency

### Difficulty

Hard

### Topics Covered

- semaphore
- throughput
- latency
- error rate
- benchmarking

### Problem

A benchmark produces:

| Concurrency | Throughput | p95 latency | Error rate |
|---:|---:|---:|---:|
| 4 | 180/s | 120 ms | 0.1% |
| 8 | 310/s | 150 ms | 0.2% |
| 16 | 520/s | 240 ms | 0.8% |
| 32 | 540/s | 900 ms | 6.0% |
| 64 | 470/s | 1,800 ms | 14.0% |

Explain what the results indicate.

### Solution

The benchmark indicates diminishing throughput returns followed by degradation. Increasing concurrency beyond the useful operating range increases latency and error rate while eventually reducing throughput.

A reasonable engineering conclusion is that the useful concurrency range is below the saturation region, subject to further testing against production-like conditions.

### How to Solve It

1. Compare throughput as concurrency rises.
2. Identify where throughput stops improving materially.
3. Examine p95 latency.
4. Examine error rate.
5. Consider the external service and resource limits.

### Explanation

The goal is not maximum concurrency. The goal is an acceptable operating point balancing throughput, latency, reliability, and resource usage.

### Common Mistakes

- Choosing 64 because it has the largest configured concurrency.
- Looking only at average latency.
- Ignoring error rate.
- Treating benchmark results as universally portable.

### Production Considerations

Measure representative payloads, network conditions, upstream behavior, database capacity, memory, and CPU. Track p95/p99 latency and error rates continuously.

---

## Question 29 — Diagnose a Queue Deadlock

### Difficulty

Hard

### Topics Covered

- queues
- `task_done()`
- `join()`
- backpressure
- shutdown

### Problem

A pipeline hangs forever at:

```python
await queue.join()
```

The consumer contains:

```python
item = await queue.get()

if item == "bad":
    raise ValueError("invalid item")

queue.task_done()
```

Explain the bug and correct the consumer.

### Solution

```python
async def consumer(queue):
    while True:
        item = await queue.get()
        try:
            if item == "bad":
                raise ValueError("invalid item")

            await process(item)
        except ValueError as exc:
            print(f"dead-letter: {item}: {exc}")
        finally:
            queue.task_done()
```

### How to Solve It

1. Recognize that every successful `put()` must eventually have a matching `task_done()`.
2. Observe that the exception bypasses the original `task_done()`.
3. Put completion accounting in `finally`.
4. Decide separately how the failed item should be handled.

### Explanation

`queue.join()` waits for the unfinished-task count to reach zero. If one item never receives `task_done()`, the join can block forever.

### Common Mistakes

- Calling `task_done()` only on success.
- Calling it twice.
- Ignoring the failed item rather than routing it to a dead-letter path.

### Production Considerations

Error handling should preserve queue accounting while separating transient processing failure, permanent data failure, and shutdown behavior.

---

## Question 30 — Avoid a Race with Shared State

### Difficulty

Hard

### Topics Covered

- race conditions
- `threading.Lock`
- message passing
- stress testing

### Problem

Ten worker threads update a shared dictionary of per-customer totals. Propose two designs:

1. A lock-based design.
2. A design that minimizes shared mutable state.

### Solution

Lock-based:

```python
import threading

totals: dict[str, float] = {}
lock = threading.Lock()


def add_total(customer_id: str, amount: float) -> None:
    with lock:
        totals[customer_id] = totals.get(customer_id, 0.0) + amount
```

Partition-local design:

```python
def process_partition(records):
    local_totals: dict[str, float] = {}

    for customer_id, amount in records:
        local_totals[customer_id] = (
            local_totals.get(customer_id, 0.0) + amount
        )

    return local_totals
```

The caller can merge partition results after the concurrent stage.

### How to Solve It

1. Identify the shared aggregation state.
2. Decide whether all workers really need to mutate one global object.
3. If yes, protect updates.
4. If not, partition the work and aggregate after the concurrent stage.

### Explanation

The second approach often scales better because it reduces contention and makes ownership explicit.

### Common Mistakes

- Using a global lock around the entire record-processing function.
- Assuming a thread-safe container eliminates logical races.
- Sharing state when partitioning can avoid it.

### Production Considerations

Prefer ownership, immutability, queues, and partition-local state when they simplify correctness and improve throughput.

---

# Part 4 — Advanced

## Question 31 — Design a Million-Record Async Ingestion Pipeline

### Difficulty

Advanced

### Topics Covered

- async HTTP
- semaphores
- queues
- backpressure
- TaskGroup
- CPU transformation
- ProcessPoolExecutor
- database limits
- checkpointing

### Problem

You must ingest 1,000,000 records from several APIs.

Constraints:

- API allows 20 concurrent requests per API key.
- Database has a connection pool of 10.
- Transformation is CPU-heavy pure Python.
- Records must not all be held in memory.
- The pipeline must support graceful cancellation.
- A successful batch should be checkpointed.
- Failed permanent records should go to a dead-letter path.

Design the architecture and explain the execution model at each stage.

### Solution

A suitable conceptual architecture is:

```text
                 ┌──────────────────┐
                 │ Async API Fetch  │
                 │ per-key limits   │
                 └────────┬─────────┘
                          │
                    bounded queue
                          │
                 ┌────────▼─────────┐
                 │ CPU Transform    │
                 │ ProcessPool      │
                 └────────┬─────────┘
                          │
                    bounded queue
                          │
                 ┌────────▼─────────┐
                 │ Batch Loader     │
                 │ DB limit <= 10   │
                 └────────┬─────────┘
                          │
                 checkpoint / DLQ
```

Representative skeleton:

```python
import asyncio
from concurrent.futures import ProcessPoolExecutor


def transform(record: dict) -> dict:
    value = record["value"]
    score = sum(x * x for x in value)
    return {"id": record["id"], "score": score}


async def pipeline() -> None:
    raw_queue = asyncio.Queue(maxsize=1_000)
    transformed_queue = asyncio.Queue(maxsize=500)

    api_limit = asyncio.Semaphore(20)
    db_limit = asyncio.Semaphore(10)

    with ProcessPoolExecutor() as process_pool:
        async with asyncio.TaskGroup() as group:
            group.create_task(
                extract_stage(raw_queue, api_limit)
            )

            for _ in range(4):
                group.create_task(
                    transform_stage(
                        raw_queue,
                        transformed_queue,
                        process_pool,
                    )
                )

            for _ in range(2):
                group.create_task(
                    load_stage(transformed_queue, db_limit)
                )


async def extract_stage(queue, api_limit):
    # Real implementation would use one reusable AsyncClient,
    # bounded task creation, retries, deadlines, and checkpoints.
    ...


async def transform_stage(raw_queue, output_queue, process_pool):
    loop = asyncio.get_running_loop()

    while True:
        record = await raw_queue.get()
        try:
            result = await loop.run_in_executor(
                process_pool,
                transform,
                record,
            )
            await output_queue.put(result)
        finally:
            raw_queue.task_done()


async def load_stage(queue, db_limit):
    while True:
        record = await queue.get()
        try:
            async with db_limit:
                # Batch writes in the real implementation.
                await write_record(record)
        finally:
            queue.task_done()


async def write_record(record):
    await asyncio.sleep(0.01)
```

### How to Solve It

1. Classify HTTP extraction as I/O-bound.
2. Bound API concurrency at the API-key level.
3. Use bounded queues to prevent memory growth.
4. Move pure-Python CPU transformation to a process pool.
5. Bound database concurrency to the actual pool capacity.
6. Batch writes.
7. Checkpoint after durable success.
8. Route permanent failures to a dead-letter mechanism.
9. Use structured cancellation and graceful shutdown.
10. Measure every stage independently.

### Explanation

The important design is not "use asyncio everywhere." Each stage has a different bottleneck.

```text
HTTP → asyncio
CPU pure Python → processes
DB → bounded async/threaded I/O according to driver
queues → backpressure
checkpoint → resumability
```

### Common Mistakes

- Creating one million asyncio tasks.
- Creating one process per record.
- Allowing database concurrency above the connection pool.
- Holding semaphore permits during retry backoff.
- Loading the entire dataset into memory.
- Treating cancellation as failure.

### Production Considerations

Observe queue depth, stage throughput, CPU utilization, API status distribution, retry counts, DB pool saturation, batch latency, checkpoint progress, DLQ volume, and shutdown duration.

---

## Question 32 — Choose Between Threads, Asyncio, and Processes

### Difficulty

Advanced

### Topics Covered

- model selection
- workload classification
- thread safety
- GIL
- blocking libraries
- architecture trade-offs

### Problem

A pipeline has these stages:

1. Existing blocking HTTP SDK.
2. CPU-heavy pure-Python parsing.
3. PostgreSQL writes through a synchronous driver.
4. Small shared in-memory cache accessed by multiple workers.

Choose an execution model for each stage and explain how you would control shared state.

### Solution

A reasonable starting design is:

| Stage | Model | Reason |
|---|---|---|
| Blocking HTTP SDK | threads | Blocking I/O can overlap without rewriting the SDK |
| CPU-heavy pure Python | processes | Avoid relying on GIL-limited CPU parallelism |
| Sync PostgreSQL driver | bounded threads | Blocking I/O; size relative to DB connections |
| Shared cache | lock or redesigned ownership | Protect shared mutable state or avoid sharing |

The architecture may use queues between stages.

### How to Solve It

1. Classify each stage independently.
2. Identify blocking boundaries.
3. Identify CPU-bound pure Python.
4. Match concurrency to resource capacity.
5. Minimize shared mutable state.

### Explanation

A single global concurrency model is not required. Production pipelines often use different models at different boundaries.

### Common Mistakes

- Choosing asyncio because the overall application is an ingestion service.
- Choosing processes for database I/O.
- Ignoring the database connection limit.
- Making the shared cache globally mutable without a synchronization strategy.

### Production Considerations

Prefer the simplest architecture that satisfies throughput, latency, reliability, and operational requirements. Additional concurrency models add complexity and should be justified.

---

## Question 33 — Diagnose Unbounded Async Task Creation

### Difficulty

Advanced

### Topics Covered

- `create_task()`
- task references
- bounded concurrency
- queues
- memory pressure

### Problem

A developer writes:

```python
tasks = [
    asyncio.create_task(fetch(url))
    for url in one_million_urls
]

results = await asyncio.gather(*tasks)
```

Explain the risks and redesign the system.

### Solution

Use bounded task creation with a queue and fixed workers:

```python
import asyncio


async def worker(
    queue: asyncio.Queue[str],
    results: list[str],
) -> None:
    while True:
        url = await queue.get()
        try:
            result = await fetch(url)
            results.append(result)
        finally:
            queue.task_done()


async def fetch(url: str) -> str:
    await asyncio.sleep(0.001)
    return url


async def main(urls: list[str]) -> None:
    queue: asyncio.Queue[str] = asyncio.Queue(maxsize=500)

    results: list[str] = []
    workers = [
        asyncio.create_task(worker(queue, results))
        for _ in range(20)
    ]

    for url in urls:
        await queue.put(url)

    await queue.join()

    for worker_task in workers:
        worker_task.cancel()

    await asyncio.gather(*workers, return_exceptions=True)
```

### How to Solve It

1. Identify that one million tasks create substantial scheduling and memory overhead.
2. Replace task-per-record with a fixed worker count.
3. Bound the queue.
4. Process results incrementally where possible.
5. Shut down workers after the queue drains.

### Explanation

A semaphore alone would not necessarily solve the memory problem if one million tasks were still created and merely waiting for permits.

### Common Mistakes

- Thinking a semaphore makes task creation bounded.
- Calling `gather()` with enormous task lists.
- Retaining every result when downstream processing could be incremental.

### Production Considerations

Bound task count, queue size, response buffering, batch size, and retained results independently.

---

## Question 34 — Graceful Shutdown of a Multi-Stage Pipeline

### Difficulty

Advanced

### Topics Covered

- TaskGroup
- cancellation
- queues
- SIGINT/SIGTERM concepts
- checkpointing
- graceful shutdown

### Problem

A long-running ingestion pipeline receives SIGTERM during processing. Design the shutdown sequence.

### Solution

The desired sequence is:

```text
receive shutdown signal
        ↓
stop accepting new work
        ↓
cancel/stop producers
        ↓
allow safe in-flight work to finish where appropriate
        ↓
drain bounded queues
        ↓
finish or checkpoint durable batches
        ↓
close HTTP/DB resources
        ↓
exit
```

A simplified async structure is:

```python
import asyncio


async def run_pipeline() -> None:
    stop_event = asyncio.Event()

    async def producer() -> None:
        while not stop_event.is_set():
            await produce_one()

    async def consumer() -> None:
        while not stop_event.is_set():
            await consume_one()

    async with asyncio.TaskGroup() as group:
        group.create_task(producer())
        group.create_task(consumer())

        await stop_event.wait()

        # Real code would coordinate stage-specific draining
        # before leaving the structured scope.


async def produce_one() -> None:
    await asyncio.sleep(0.1)


async def consume_one() -> None:
    await asyncio.sleep(0.1)
```

### How to Solve It

1. Define what "graceful" means for each stage.
2. Stop new intake first.
3. Preserve durable in-flight work where possible.
4. Drain or checkpoint bounded queues.
5. Release resource pools.
6. Propagate cancellation correctly.
7. Make restart resumable.

### Explanation

Graceful shutdown is a correctness feature. A pipeline that exits cleanly but loses acknowledged work is not necessarily correct.

### Common Mistakes

- Immediately cancelling every task.
- Continuing to accept new work after shutdown starts.
- Closing a database pool before queued writes finish.
- Treating checkpointing as optional.

### Production Considerations

Define maximum shutdown time and a forced-termination policy. Make downstream writes idempotent so interrupted work can safely resume.

---

## Question 35 — GIL, Free-Threading, and Benchmark Interpretation

### Difficulty

Advanced

### Topics Covered

- GIL
- free-threaded Python
- PEP 703 awareness
- Amdahl's Law
- benchmarking
- model selection

### Problem

A CPU-heavy pure-Python transformation is benchmarked under four designs:

| Design | Runtime |
|---|---:|
| Sequential | 100 s |
| 8 threads | 96 s |
| 8 processes | 16 s |
| Free-threaded build + 8 threads | 18 s |

Explain what conclusions can and cannot be drawn.

### Solution

Supported conclusions:

- Eight ordinary threads did not provide meaningful CPU parallel speedup for this workload.
- Eight processes produced substantial speedup.
- The tested free-threaded build allowed strong threaded CPU parallelism in this benchmark.
- The process and free-threaded results are not automatically transferable to every workload.

The approximate speedups are:

- threads: `100 / 96 ≈ 1.04×`
- processes: `100 / 16 = 6.25×`
- free-threaded: `100 / 18 ≈ 5.56×`

### How to Solve It

1. Compare each design to the sequential baseline.
2. Calculate speedup.
3. Consider the workload characteristics.
4. Examine overhead, memory, compatibility, and operational complexity.
5. Avoid generalizing beyond the benchmark.

### Explanation

Amdahl's Law explains why even highly parallel workloads have a sequential component that limits total speedup.

Free-threaded Python changes the traditional GIL trade-off, but deployment and dependency compatibility remain important.

### Common Mistakes

- Concluding that free-threaded Python always beats processes.
- Ignoring startup and serialization overhead.
- Ignoring native-library parallelism.
- Treating one benchmark as a universal result.

### Production Considerations

Benchmark representative data and the exact Python build/dependency stack used in production.

---

## Question 36 — Debug a Free-Threading Race

### Difficulty

Advanced

### Topics Covered

- free-threading
- race conditions
- shared mutable state
- locks
- stress testing

### Problem

A program was historically tested on a GIL-enabled CPython build and appears correct:

```python
state = {"count": 0}


def update():
    for _ in range(10_000):
        state["count"] += 1
```

It now shows incorrect results under a free-threaded build. Explain the underlying issue and provide a safe design.

### Solution

Use explicit synchronization:

```python
import threading

state = {"count": 0}
lock = threading.Lock()


def update() -> None:
    for _ in range(10_000):
        with lock:
            state["count"] += 1
```

An even better design may avoid shared mutation:

```python
def update_local() -> int:
    return 10_000
```

Then aggregate returned values after concurrent execution.

### How to Solve It

1. Identify the shared mutable counter.
2. Identify the read-modify-write operation.
3. Stop relying on interpreter-level implementation behavior.
4. Use explicit synchronization or eliminate shared state.
5. Stress-test under multiple schedules.

### Explanation

Free-threading makes previously hidden assumptions about serialized interpreter execution more visible. Correctness should come from application-level synchronization or ownership, not from an assumption that the interpreter happens to serialize access.

### Common Mistakes

- Treating free-threading as "remove all locks."
- Assuming a thread-safe container makes compound application logic atomic.
- Testing only one execution.

### Production Considerations

Concurrency tests should deliberately vary timing and execution schedules. Race conditions can remain intermittent even after the obvious code path is fixed.

---

## Question 37 — Design Layered Limits for Multiple APIs and a Database

### Difficulty

Advanced

### Topics Covered

- semaphores
- per-host limits
- API-key limits
- database limits
- queues
- async HTTP
- backpressure

### Problem

An ingestion service calls three APIs:

- API A: 10 concurrent requests
- API B: 5 concurrent requests
- API C: 20 concurrent requests

The service has a global HTTP concurrency budget of 25. The database allows 8 concurrent writes.

Design the concurrency-control strategy.

### Solution

Use layered limits:

```text
Global HTTP semaphore: 25
    ├── API A semaphore: 10
    ├── API B semaphore: 5
    └── API C semaphore: 20

DB semaphore: 8
```

Conceptually:

```python
global_http = asyncio.Semaphore(25)
api_a = asyncio.Semaphore(10)
api_b = asyncio.Semaphore(5)
api_c = asyncio.Semaphore(20)
db_limit = asyncio.Semaphore(8)
```

An API A operation should acquire the global and API A limits around the actual HTTP operation.

### How to Solve It

1. Identify global and resource-specific constraints.
2. Enforce the narrowest relevant upstream limit.
3. Also enforce a global budget.
4. Align DB concurrency with actual connection capacity.
5. Use bounded queues between extraction and loading.

### Explanation

Layered limits prevent one upstream source from consuming all application capacity while still respecting source-specific policies.

### Common Mistakes

- Applying only the global limit.
- Applying only per-host limits.
- Setting database concurrency above connection-pool capacity.
- Holding permits during unrelated downstream work.

### Production Considerations

Monitor utilization and queue depth by resource. Revisit limits when API contracts, DB capacity, or workload characteristics change.

---

## Question 38 — Diagnose Incorrect Timeout Placement

### Difficulty

Advanced

### Topics Covered

- operation deadlines
- overall deadlines
- TaskGroup
- cancellation
- HTTP extraction

### Problem

A pipeline performs:

```text
request
→ parse
→ transform
→ write
```

The developer puts a five-second timeout only around the database write. The requirement is that the complete record operation must finish within five seconds.

Explain the design error and show the correct conceptual structure.

### Solution

The deadline should surround the complete logical operation:

```python
import asyncio


async def process_record(record):
    async with asyncio.timeout(5):
        response = await fetch(record)
        parsed = parse(response)
        transformed = await transform(parsed)
        await write(transformed)
```

### How to Solve It

1. Define the business operation whose completion has a deadline.
2. Place the timeout around that complete operation.
3. Allow cancellation to propagate through each stage.
4. Use smaller internal timeouts only when they represent meaningful sub-operation limits.

### Explanation

A five-second database timeout does not guarantee a five-second end-to-end record deadline. The request and transformation could already consume most of the available time.

### Common Mistakes

- Applying only a downstream timeout.
- Restarting the entire operation indefinitely after each sub-timeout.
- Swallowing cancellation.

### Production Considerations

Use deadline-aware retries so each retry receives only the remaining time budget.

---

## Question 39 — Benchmark a Pipeline Instead of Guessing

### Difficulty

Advanced

### Topics Covered

- sequential baseline
- concurrency
- throughput
- latency
- memory
- benchmarking
- architecture judgment

### Problem

A developer claims:

> "We doubled the number of workers, so the pipeline is twice as fast."

Design a benchmark that can verify or reject the claim.

### Solution

Measure at minimum:

```text
                    sequential
                         ↓
             representative workload
                         ↓
     workers/concurrency = 1, 2, 4, 8, 16, ...
                         ↓
 ┌───────────┬──────────┬────────┬─────────┐
 │ wall time │throughput│ p95/p99│ errors  │
 └───────────┴──────────┴────────┴─────────┘
                         ↓
              CPU + memory + queue depth
```

Example timing harness:

```python
import time


def benchmark(fn, *args, **kwargs):
    start = time.perf_counter()

    result = fn(*args, **kwargs)

    elapsed = time.perf_counter() - start
    return result, elapsed
```

### How to Solve It

1. Establish a sequential baseline.
2. Keep input data constant.
3. Vary only the concurrency/worker parameter.
4. Repeat measurements.
5. Record wall time and throughput.
6. Record latency percentiles where applicable.
7. Record error rate, memory, CPU, and queue depth.
8. Identify the saturation point.

### Explanation

Performance is a measured property of a workload and environment, not a consequence of adding more workers.

### Common Mistakes

- Comparing different input sizes.
- Measuring only one run.
- Measuring only wall-clock time.
- Ignoring failures and latency degradation.
- Benchmarking an unrealistic toy workload.

### Production Considerations

Benchmark with representative payload sizes, API behavior, database capacity, deployment CPU/memory limits, and realistic failure conditions.

---

## Question 40 — Senior Model-Selection and Architecture Review

### Difficulty

Advanced

### Topics Covered

- sequential vs threads vs asyncio vs processes
- free-threaded Python
- GIL
- workload classification
- Amdahl's Law
- resource limits
- observability
- production trade-offs

### Problem

You are reviewing five workloads:

### Workload A

A daily job downloads 500 small files from object storage. The SDK is blocking and reliable.

### Workload B

A service receives independent HTTP requests with high latency and needs high concurrent throughput.

### Workload C

A batch job performs heavy pure-Python CPU transformation over partitioned data.

### Workload D

A transformation uses Polars/NumPy-style native operations that already perform substantial native parallel work.

### Workload E

A small maintenance script processes 20 records once per day and completes in two seconds sequentially.

Choose an initial model for each:

```text
Sequential
Threading / ThreadPoolExecutor
asyncio
ProcessPoolExecutor
Free-threaded Python
Native library parallelism
```

Then explain the production factors that could change your decision.

### Solution

| Workload | Initial choice | Reason |
|---|---|---|
| A | ThreadPoolExecutor | Blocking I/O with a relatively small independent workload |
| B | asyncio | High-latency concurrent network I/O with an async-capable stack |
| C | ProcessPoolExecutor | CPU-heavy pure Python across partitions |
| D | Native library parallelism | The library already performs optimized native computation |
| E | Sequential | Very small workload; concurrency would add unnecessary complexity |

Free-threaded Python may become a candidate for some CPU-heavy threaded workloads after dependency compatibility and benchmark validation.

### How to Solve It

Evaluate each workload against:

1. I/O vs CPU.
2. Blocking vs async-capable APIs.
3. GIL behavior.
4. Native-library behavior.
5. Task count and granularity.
6. Memory overhead.
7. External service limits.
8. Database/storage limits.
9. Failure and cancellation semantics.
10. Operational complexity.
11. Observability requirements.
12. Measured performance.

### Explanation

There is no universally superior concurrency model.

A practical decision tree is:

```text
Is the workload small?
    └─ yes → sequential may be sufficient

Mostly blocking I/O?
    ├─ async-capable → asyncio
    └─ blocking library → threads

CPU-heavy pure Python?
    ├─ processes
    └─ free-threaded Python if compatible and benchmarked

Already native/vectorized?
    └─ use the library's native execution model

Does one machine no longer meet requirements?
    └─ consider distributed processing
```

Amdahl's Law also matters: accelerating one stage does not produce proportional end-to-end speedup if other stages remain sequential or resource-constrained.

### Common Mistakes

- Choosing asyncio for every workload.
- Choosing processes for every CPU-looking task.
- Ignoring native parallelism.
- Introducing concurrency into a workload too small to benefit.
- Ignoring downstream resource limits.
- Making architecture decisions without a sequential baseline.

### Production Considerations

The final design should be explainable in terms of workload characteristics, measured performance, bounded resources, correctness, failure handling, shutdown behavior, and operational complexity.

---

# Final Review

## Concepts Covered

This practice set exercises:

- explicit threads and thread lifecycle
- `ThreadPoolExecutor`
- `Future`
- `result()`
- `map()`
- `as_completed()`
- `wait()` concepts
- `FIRST_COMPLETED` / `FIRST_EXCEPTION` decision points
- executor shutdown
- cancellation of pending executor work
- I/O-bound workload design
- process isolation
- `ProcessPoolExecutor`
- pickling and importable workers
- `__main__` protection
- process start methods
- `chunksize`
- process worker lifecycle
- CPU sizing
- process oversubscription
- large-object transfer
- shared-memory awareness
- mmap/Arrow IPC awareness
- worker failures and broken pools
- asyncio event loops
- coroutine functions
- `await`
- tasks
- `gather()`
- task references
- blocking calls inside async code
- `asyncio.to_thread()`
- executor integration
- async iteration
- async context managers
- TaskGroup
- structured concurrency
- `ExceptionGroup`
- `except*`
- cancellation
- `CancelledError`
- cleanup
- operation and overall deadlines
- shielding awareness
- graceful shutdown
- async HTTP clients
- HTTP connection pooling
- connection limits
- timeouts
- authentication/token refresh awareness
- retries
- `Retry-After`
- async rate limiting
- streaming
- checkpointing
- semaphores
- bounded concurrency
- concurrency versus rate
- layered limits
- queues
- `task_done()`
- `join()`
- bounded queues
- backpressure
- sentinel/shutdown concepts
- multi-stage pipelines
- batching
- dead-letter handling
- ordering
- race conditions
- read-modify-write
- check-then-act
- locks
- `RLock`
- `Event`
- `Condition`
- `Barrier`
- deadlocks
- lock ordering
- lock timeouts
- critical-section sizing
- thread-safe queues
- message passing
- immutable state
- per-task state
- `contextvars`
- database/storage concurrency
- stress testing
- GIL behavior
- native extensions
- free-threaded Python
- PEP 703 awareness
- dependency compatibility
- `sys._is_gil_enabled()` awareness
- subinterpreters / `InterpreterPoolExecutor` awareness
- Amdahl's Law
- workload classification
- sequential execution
- benchmarking
- throughput
- latency
- p95/p99
- memory pressure
- queue depth
- resource limits
- production model selection

---

## Recommended Practice Order

### Pass 1 — Fundamentals

Complete:

```text
Q1 → Q10
```

Goal:

- understand the primitives
- write small working examples
- distinguish I/O from CPU
- understand basic synchronization

### Pass 2 — Composition

Complete:

```text
Q11 → Q20
```

Goal:

- combine primitives
- reason about failure
- introduce bounded concurrency
- understand async/sync boundaries

### Pass 3 — Production Problems

Complete:

```text
Q21 → Q30
```

Goal:

- debug realistic failures
- reason about performance
- design queues and backpressure
- combine multiple concurrency mechanisms

### Pass 4 — Senior Engineering

Complete:

```text
Q31 → Q40
```

Goal:

- design production pipelines
- reason about resource budgets
- evaluate architecture
- interpret benchmarks
- choose the simplest model that satisfies requirements

---

# Module 2.10 Mastery Checklist

## Threading

- [ ] I can explain `Thread.start()` and `join()`.
- [ ] I can use `ThreadPoolExecutor`.
- [ ] I understand `Future.result()`.
- [ ] I can use `map()` and `as_completed()`.
- [ ] I understand worker sizing.
- [ ] I understand bounded submission and task-memory implications.
- [ ] I can reason about thread safety.

## Multiprocessing

- [ ] I can identify CPU-bound pure-Python workloads.
- [ ] I can use `ProcessPoolExecutor`.
- [ ] I understand process isolation.
- [ ] I understand pickling requirements.
- [ ] I use importable worker functions.
- [ ] I understand the `__main__` guard.
- [ ] I understand process start methods.
- [ ] I understand `chunksize`.
- [ ] I can reason about large object transfer.
- [ ] I can recognize worker failure and shutdown problems.

## asyncio

- [ ] I understand the event loop.
- [ ] I can write coroutine functions.
- [ ] I use `await` correctly.
- [ ] I understand task creation.
- [ ] I can use `gather()`.
- [ ] I can identify blocking calls inside async code.
- [ ] I understand `to_thread()`.
- [ ] I can use async iterators and context managers.

## Structured Concurrency

- [ ] I can use `TaskGroup`.
- [ ] I understand structured task ownership.
- [ ] I understand sibling cancellation.
- [ ] I can reason about `ExceptionGroup`.
- [ ] I can use `except*`.
- [ ] I understand `CancelledError`.
- [ ] I preserve cancellation when appropriate.
- [ ] I can apply operation deadlines.
- [ ] I can design graceful shutdown.

## Async HTTP

- [ ] I can reuse an `httpx.AsyncClient`.
- [ ] I understand connection pooling.
- [ ] I can configure timeouts.
- [ ] I can bound concurrent requests.
- [ ] I can distinguish retries from rate limiting.
- [ ] I can respect `Retry-After`.
- [ ] I understand sequential cursor pagination.
- [ ] I can design checkpointing for extraction.

## Bounded Concurrency

- [ ] I can use `asyncio.Semaphore`.
- [ ] I understand permit acquisition and release.
- [ ] I can recognize semaphore leaks.
- [ ] I understand `BoundedSemaphore`.
- [ ] I distinguish concurrency from rate.
- [ ] I can design layered limits.
- [ ] I align concurrency with downstream resource pools.
- [ ] I understand that a semaphore alone does not bound task creation.

## Queues and Backpressure

- [ ] I understand producer-consumer architecture.
- [ ] I can use `asyncio.Queue`.
- [ ] I understand `put()`, `get()`, `task_done()`, and `join()`.
- [ ] I can use bounded queues.
- [ ] I understand backpressure.
- [ ] I can design multi-stage pipelines.
- [ ] I can reason about batching.
- [ ] I can design dead-letter handling.
- [ ] I can monitor queue depth.

## Race Conditions and Thread Safety

- [ ] I can identify read-modify-write races.
- [ ] I can identify check-then-act races.
- [ ] I can use `threading.Lock`.
- [ ] I can use `asyncio.Lock`.
- [ ] I understand deadlocks and lock ordering.
- [ ] I understand critical-section sizing.
- [ ] I know when to avoid shared state.
- [ ] I understand message passing and partition-local state.
- [ ] I can design stress tests for concurrency bugs.

## GIL and Model Selection

- [ ] I understand the practical role of the GIL.
- [ ] I can distinguish I/O concurrency from CPU parallelism.
- [ ] I understand that native extensions may release the GIL.
- [ ] I understand free-threaded Python at a practical level.
- [ ] I understand dependency compatibility considerations.
- [ ] I can interpret CPU-parallel benchmarks.
- [ ] I understand Amdahl's Law.
- [ ] I can compare sequential, threads, asyncio, processes, and free-threaded execution.
- [ ] I understand oversubscription.
- [ ] I know when distributed processing becomes relevant.

## Production Engineering

- [ ] I bound resources.
- [ ] I design for cancellation.
- [ ] I design graceful shutdown.
- [ ] I use retries carefully.
- [ ] I preserve idempotency.
- [ ] I use checkpointing where resumability matters.
- [ ] I respect external rate limits.
- [ ] I respect database connection limits.
- [ ] I control memory growth.
- [ ] I use queue backpressure.
- [ ] I measure throughput and latency.
- [ ] I inspect p95/p99 behavior.
- [ ] I monitor error rates.
- [ ] I establish sequential baselines.
- [ ] I benchmark before making performance claims.
- [ ] I choose the simplest execution model that meets the requirement.

---

# Final Mental Model

Production concurrency is not primarily about creating more workers.

It is about answering seven questions correctly:

1. **What is the workload?**  
   I/O-bound, CPU-bound, mixed, or already parallelized natively?

2. **What execution model fits?**  
   Sequential, threads, `asyncio`, processes, free-threaded Python, or another execution layer?

3. **What resources are limited?**  
   CPU, memory, API concurrency, API rate, connections, queue capacity, or downstream throughput?

4. **How is work bounded?**  
   Worker counts, semaphores, queues, batches, deadlines, and connection pools.

5. **What happens when something fails?**  
   Exceptions, cancellation, retries, dead-letter handling, checkpointing, and resumability.

6. **How is correctness protected?**  
   Locking, ownership, idempotency, ordering, transactions, and avoidance of unsafe shared state.

7. **How do we prove the design is better?**  
   Sequential baseline, throughput, latency, p95/p99, memory, CPU, queue depth, and error rate.

The core engineering principle for Module 2.10 is therefore:

> **Choose the simplest model that meets the requirement, bound it, make it correct, shut it down cleanly, and prove its behavior with measurements.**
