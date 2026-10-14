# Roadmap — Module 2.10: Concurrency and Parallelism in Practice

This is the learning roadmap for the tenth module of Stage 2, **Python for
Data Engineering**. It tells you **what** to learn about concurrent and
parallel Python, **in what order**, **how** to learn each topic, and **how
to prove to yourself** that you have learned it before you move on.

In Stage 1 you learned the **vocabulary**: concurrency vs parallelism,
synchronous vs asynchronous, blocking vs non-blocking, I/O-bound vs
CPU-bound. This module is the **practice**. Data engineering is full of
work that is slow only because it runs one thing at a time: calling an API
50,000 times, downloading 3,000 files from object storage, loading 200
tables, parsing 10 GB of JSON. Done well, concurrency turns an 8-hour job
into 20 minutes. Done badly, it gets you rate-limited, corrupts shared
state, exhausts database connections, deadlocks, or silently loses the
error that should have failed the job.

The goal is not to use the fanciest model. The goal is to pick the
**simplest model that meets the requirement**, bound it, make it correct,
make it shut down cleanly, and prove the speed-up with measurements.

---

## 1. Module outcome

By the end of this module you will be able to:

- Run I/O-bound work in parallel with **threads** and
  `ThreadPoolExecutor`, collecting results and errors correctly.
- Run CPU-bound work on all cores with **processes** and
  `ProcessPoolExecutor`, and control pickling, start methods, chunking, and
  memory.
- Write **asyncio** programs with coroutines, tasks, and the event loop —
  and never block the loop.
- Use **TaskGroups**, cancellation, and timeouts for structured, safe
  concurrency.
- Build high-throughput **async HTTP extractors** with `httpx.AsyncClient`
  that respect rate limits and survive failures.
- **Bound** concurrency with semaphores and worker pools, and explain the
  difference between a concurrency limit and a rate limit.
- Build multi-stage **producer–consumer pipelines** with queues, back
  pressure, batching, and clean shutdown.
- Find and fix **race conditions** and deadlocks with locks and better
  designs.
- Explain the **GIL**, free-threaded Python, and subinterpreters, and
  **choose a concurrency model** for any data engineering workload with
  evidence.

---

## 2. Prerequisites

This module builds on earlier stages and Modules 2.1–2.9. It does **not**
re-teach them.

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| CPU cores, caches, processes, threads, scheduling, signals | Stage 0 — How Computers Work / OS Fundamentals | What the OS actually does when you start threads and processes |
| **Concurrency vocabulary** (concurrency vs parallelism, blocking, I/O vs CPU-bound) | Stage 1 — Module 1.9 | Concepts are **not** re-taught; this module puts them into code |
| Generators, context managers, decorators, object model | Stage 1 — Module 1.9 | Async generators and context managers, retry decorators |
| Pure functions, separating side effects | Stage 1 — Module 1.8 | Pure functions are safe to run in parallel |
| Profiling and measuring before optimizing | Stage 1 — Module 1.10 | Every speed-up must be measured |
| NumPy, pandas, Polars, DuckDB internals | Stage 2 — Modules 2.2–2.4 | Many libraries already run in parallel and release the GIL |
| Connection pools, transactions from Python, async driver awareness | Stage 2 — Module 2.7 | Concurrent database access and pool sizing |
| HTTP clients, auth, pagination, rate limits, retries | Stage 2 — Module 2.9 | Async extraction re-uses all of these; they are **not** re-taught |

**Tools needed:**

- Python 3.13 or newer via `uv` (`uv python install 3.14`), plus a
  **free-threaded build** for Topic 09 (for example `uv python install
  3.14t`).
- `uv add httpx "psycopg[binary,pool]" tenacity pyarrow polars numpy
  pytest pytest-asyncio` (or `anyio` for async tests).
- Your **mock API** from Module 2.9 (with latency, rate limits, and
  failure switches), MinIO, and PostgreSQL in Docker.
- A sampling profiler such as `py-spy` (optional) to see what threads and
  processes are doing.
- `htop` or `top` to watch CPU usage per core while experiments run.

---

## 3. How the module is organised

The nine topics are grouped into four phases. Work through them **in
order**.

```text
Phase A — Threads and Processes                 (Basics → Intermediate)
  01 threading and ThreadPoolExecutor
  02 multiprocessing and ProcessPoolExecutor

Phase B — asyncio                               (Intermediate → Advanced)
  03 asyncio: event loop, coroutines, and tasks
  04 TaskGroups, cancellation, and timeouts
  05 Async HTTP extraction with httpx

Phase C — Coordination and Correctness          (Intermediate → Advanced)
  06 Semaphores and bounded concurrency
  07 Queues and producer–consumer pipelines
  08 Race conditions, locks, and thread safety

Phase D — Choosing a Model                      (Advanced)
  09 The GIL, free-threaded Python, and choosing a model

Consolidate
  practice-questions.md
  Module mini-project: a concurrent extract–transform–load engine
```

The dependency chain:

```text
01 ──► 02 ──► 03 ──► 04 ──► 05 ──► 06 ──► 07 ──► 08 ──► 09
threads procs  async   safe    real    limit   connect  keep it  choose
for I/O for    basics  async   async   how     stages   correct  with
        CPU                    work    much                      evidence
```

Why this order:

- Executors (01–02) give the simplest working speed-ups and introduce
  futures, which asyncio also uses.
- asyncio basics (03) come before structured concurrency (04), which is
  required before building real async extractors (05).
- Bounding (06) and queues (07) apply to all three models and are easier
  once you have seen all three.
- Race conditions (08) come after you have built enough concurrent code to
  appreciate how shared state goes wrong.
- Choosing a model (09) needs measured experience with everything above,
  plus the GIL and free-threading background.

---

## 4. Suggested schedule

About **4 weeks at 8–10 hours per week**.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — threads · Topic 02 — processes |
| 2 | Topic 03 — asyncio basics · Topic 04 — TaskGroups, cancellation, timeouts |
| 3 | Topic 05 — async HTTP · Topic 06 — bounded concurrency · Topic 07 — queues |
| 4 | Topic 08 — race conditions · Topic 09 — GIL and choosing a model · practice questions · mini-project |

---

## 5. How to study every topic (the concurrency loop)

```text
Read → Write the sequential baseline → Classify the work → Predict the speed-up
→ Add concurrency → Bound it → Inject failures → Test shutdown
→ Measure → Write it down → Explain aloud
```

1. **Read** the topic file once, fully.
2. **Write the sequential baseline** first and keep it. It is your
   correctness reference and your speed reference.
3. **Classify the work**: I/O-bound (waiting on network or disk) or
   CPU-bound (Python computation), and whether the heavy parts run inside
   a native library that releases the GIL.
4. **Predict the speed-up** (for example "50 requests at 200 ms each with
   10 workers ≈ 1 second") before running anything.
5. **Add concurrency** with the model the topic teaches.
6. **Bound it**: a maximum number of workers, in-flight tasks, open
   connections, and memory.
7. **Inject failures**: exceptions in one task, timeouts, slow tasks,
   `429`s, a killed process, `Ctrl+C`.
8. **Test shutdown**: no lost errors, no orphan threads or processes, no
   half-written output, no leaked connections.
9. **Measure** wall time, CPU usage per core, peak memory, and — for
   network work — requests per second and error counts. Compare with your
   prediction.
10. **Write down** the rule you learned in `module-2.10-notes.md`.
11. **Explain aloud** why the measured speed-up matches (or does not match)
    your prediction.

**Always assert that the concurrent result equals the sequential result**
(sorting if order is not guaranteed). A faster wrong answer is a bug.

Keep one `concurrency_lab/` `uv` project:

```text
concurrency_lab/
├── src/concurrency_lab/   # one module per topic
├── benchmarks/            # timing scripts and results CSVs
└── tests/                 # sync and async tests, including failure and shutdown tests
```

---

## 6. Phase A — Threads and Processes (Basics → Intermediate)

### Topic 01 — [threading and ThreadPoolExecutor](01-threading-and-threadpoolexecutor.md)

**Why it comes first:** Threads are the smallest change that speeds up
I/O-bound code — downloading files, calling APIs, running queries — and
they work with the ordinary blocking libraries you already use.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | `threading.Thread`, `start()`, `join()`; why threads help I/O-bound work (the GIL is released while waiting on I/O) |
| Basics | `concurrent.futures.ThreadPoolExecutor` as the default way to use threads: `submit()` returning a `Future`, `result()`, and `with` for clean shutdown |
| Basics | `executor.map()` (results in input order) vs `as_completed()` (results as they finish) |
| Intermediate | **Error handling**: exceptions are stored in the future and re-raised by `result()`; collecting all errors vs failing fast; never losing an exception |
| Intermediate | `concurrent.futures.wait()` with `FIRST_COMPLETED` / `FIRST_EXCEPTION`, and `shutdown(cancel_futures=True)` |
| Intermediate | Choosing `max_workers` for I/O work: limited by the remote system (rate limits, connection pools), not by your CPU count |
| Intermediate | Per-thread resources: sharing a thread-safe HTTP client or connection pool vs one client per thread (`threading.local`) |
| Advanced | Memory: submitting a million tasks at once creates a million futures — submitting in bounded batches (and the `buffersize` option of `Executor.map` in recent Python versions) |
| Advanced | Daemon threads, and why they can lose work at interpreter exit |
| Advanced | Thread-safety of common libraries: which clients, pools, and objects may be shared (checked in library docs) |
| Advanced | Logging from threads: thread names in log records, and tracing which task produced which error |

**How to learn it**

1. Read the topic file.
2. Download 500 files from MinIO sequentially, then with 4, 16, 64, and 256
   threads; plot time against worker count and explain the curve.
3. Make 5% of downloads fail and check that you see every failure.

**Hands-on exercise — `threaded_downloads.py`**

1. Write `download_all(keys, max_workers)` using `ThreadPoolExecutor` and
   `as_completed`, writing each file atomically.
2. Collect successes and failures into a run report; fail the run if the
   failure rate exceeds a threshold.
3. Add a "fail fast" mode that cancels pending work on the first error.
4. Run 50 database queries in parallel through a psycopg connection pool
   (Module 2.7) and show what happens when `max_workers` exceeds the pool
   size.
5. Process 1,000,000 small tasks without creating 1,000,000 futures at
   once; measure memory both ways.
6. Test: results equal the sequential version; every exception is
   reported.

**Checkpoint — you are ready to move on when you can:**

- [ ] Use `ThreadPoolExecutor` with `submit`, `map`, and `as_completed`.
- [ ] Explain why threads speed up I/O-bound work in CPython.
- [ ] Handle and report every exception from worker threads.
- [ ] Choose `max_workers` from external limits, not guesses.

**Common mistakes:** ignoring futures so exceptions vanish; hundreds of
threads hammering an API; sharing non-thread-safe objects; submitting
unbounded numbers of tasks.

---

### Topic 02 — [multiprocessing and ProcessPoolExecutor](02-multiprocessing-and-processpoolexecutor.md)

**Why here:** Threads do not speed up pure-Python CPU work in the standard
(GIL) build. Processes do — at the cost of start-up time, data copying, and
memory.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | `ProcessPoolExecutor` for CPU-bound Python work; each worker is a separate interpreter with its own memory and its own GIL |
| Basics | The `if __name__ == "__main__":` guard and why it is required |
| Basics | **Pickling**: arguments and results are serialised between processes — functions must be importable (no lambdas or nested functions), and large objects are expensive to send |
| Intermediate | **Start methods**: `fork`, `spawn`, `forkserver`; platform defaults differ (and changed on Linux in Python 3.14) — set it explicitly for reproducible behaviour |
| Intermediate | `chunksize` in `map()` to reduce overhead for many small tasks |
| Intermediate | Worker set-up with `initializer=` (open a file, load a lookup table once per worker) and `max_tasks_per_child` to limit memory growth |
| Intermediate | Sizing: `os.process_cpu_count()` / CPU limits in containers; leaving headroom for the OS |
| Intermediate | Designing tasks for processes: pass file paths or partition ids, not big DataFrames; each worker reads and writes its own partition |
| Advanced | Sharing data without copying: `multiprocessing.shared_memory`, memory-mapped files (Module 2.2), and Arrow IPC files (Module 2.4) |
| Advanced | **Oversubscription**: NumPy/BLAS, Polars, DuckDB, and PyArrow already use multiple threads; many processes × many threads each = slower; controlling threads per process (`OMP_NUM_THREADS`, `POLARS_MAX_THREADS`, DuckDB `threads`) |
| Advanced | Fork-safety: open connections, locks, and threads do not survive `fork()` correctly — create connections inside workers |
| Advanced | Failure handling: a worker crashing (`BrokenProcessPool`), timeouts for stuck workers, and `Ctrl+C` behaviour |

**How to learn it**

1. Read the topic file.
2. Parse and validate 200 JSON Lines files (CPU-heavy per-record Python
   logic) sequentially, with threads, and with processes; explain the
   results.
3. Try to send a lambda and a 2 GB DataFrame to a worker; observe the
   error and the cost.

**Hands-on exercise — `parallel_parse.py`**

1. Write `parse_file(path) -> stats` (pure Python validation and
   transformation per record) and run it over 200 files with
   `ProcessPoolExecutor`; each worker writes its own Parquet output.
2. Compare `fork`, `spawn`, and `forkserver` start-up times.
3. Tune `chunksize` for 100,000 tiny tasks and plot the effect.
4. Load a lookup table once per worker with `initializer=`.
5. Run a Polars-heavy task in 8 processes with default Polars threading,
   then with `POLARS_MAX_THREADS=1`; measure oversubscription.
6. Kill one worker mid-run and handle `BrokenProcessPool` cleanly.

**Checkpoint:**

- [ ] Explain why processes speed up CPU-bound Python but threads may not.
- [ ] Explain pickling limits and how to design tasks around them.
- [ ] Choose a start method and explain the trade-offs.
- [ ] Avoid oversubscription with multi-threaded libraries.

**Common mistakes:** sending large data to workers instead of paths;
missing the `__main__` guard; forking with open database connections;
running processes on top of libraries that already use every core.

---

## 7. Phase B — asyncio (Intermediate → Advanced)

### Topic 03 — [asyncio: event loop, coroutines, and tasks](03-asyncio-event-loop-coroutines-and-tasks.md)

**Why here:** For thousands of concurrent I/O operations (API calls,
downloads), threads become heavy. asyncio runs them all on one thread with
an event loop — but only if nothing blocks the loop.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Coroutines (`async def`), `await`, and `asyncio.run(main())` as the single entry point |
| Basics | The **event loop**: one thread switching between tasks whenever one awaits I/O |
| Basics | Calling a coroutine does not run it — it must be awaited or wrapped in a task |
| Basics | `asyncio.create_task()` for concurrent execution; `asyncio.gather()` for waiting on several awaitables |
| Intermediate | **Never block the loop**: `time.sleep`, blocking HTTP clients, blocking database drivers, and heavy CPU work freeze every task |
| Intermediate | Escape hatches: `asyncio.to_thread()` for blocking calls; `loop.run_in_executor()` with a process pool for CPU work |
| Intermediate | `gather(..., return_exceptions=True)` vs letting the first exception propagate |
| Intermediate | Keeping references to tasks (unreferenced tasks can be garbage-collected); background task sets |
| Intermediate | Async context managers (`async with`), async iterators (`async for`), and async generators — the async versions of Stage 1 patterns |
| Advanced | asyncio **debug mode** (`PYTHONASYNCIODEBUG=1`, `asyncio.run(..., debug=True)`) to detect slow callbacks and never-awaited coroutines |
| Advanced | Mixing sync and async code: calling async code from sync code (only at the edges) and the "function colour" problem |
| Advanced | Async database drivers (`psycopg.AsyncConnection`, `AsyncConnectionPool` from Module 2.7) |
| Advanced | Alternative event loops (e.g. `uvloop`) and the `anyio` compatibility layer — awareness |

**How to learn it**

1. Read the topic file.
2. Write a coroutine that sleeps with `time.sleep` and one with
   `asyncio.sleep`; run 100 of each concurrently and explain the times.
3. Turn on debug mode and find the blocking call in a provided script.

**Hands-on exercise — `async_basics.py`**

1. Fetch 1,000 simulated I/O operations (`asyncio.sleep` with random
   latency) sequentially, with `gather`, and with `create_task`.
2. Add one blocking call and one CPU-heavy function; show the whole
   program stalling; fix them with `to_thread` and a process pool
   executor.
3. Write an async generator that yields pages from a simulated paginated
   source, and consume it with `async for`.
4. Query PostgreSQL concurrently with `AsyncConnectionPool` and compare
   with the threaded version from Topic 01.
5. Write async tests with `pytest-asyncio` (or `anyio`).

**Checkpoint:**

- [ ] Explain the event loop and what `await` does.
- [ ] Run coroutines concurrently with tasks and `gather`.
- [ ] Identify and fix code that blocks the event loop.
- [ ] Explain when asyncio is better than threads and when it is not.

**Common mistakes:** forgetting `await`; blocking calls inside coroutines;
creating tasks without keeping references; using asyncio for CPU-bound
work.

---

### Topic 04 — [TaskGroups, cancellation, and timeouts](04-taskgroups-cancellation-and-timeouts.md)

**Why here:** Loose tasks leak, hide exceptions, and keep running after a
failure. Structured concurrency makes async programs predictable: every
task has an owner, a lifetime, and a deadline.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **`asyncio.TaskGroup`**: `async with asyncio.TaskGroup() as tg: tg.create_task(...)` — all tasks finish (or are cancelled) before the block exits |
| Basics | If one task fails, the group cancels the others and raises an **`ExceptionGroup`** |
| Basics | Handling exception groups with `except*` |
| Intermediate | **Cancellation**: `task.cancel()`, `asyncio.CancelledError`, and cleanup in `finally` / `async with` blocks |
| Intermediate | Never swallowing `CancelledError` (re-raise it after cleanup) |
| Intermediate | **Timeouts**: `asyncio.timeout()` / `asyncio.timeout_at()` context managers and `asyncio.wait_for()`; per-operation timeouts vs an overall run deadline |
| Intermediate | TaskGroup vs `gather`: when you want "all or nothing" and when you want "collect every result and error" |
| Advanced | `asyncio.shield()` for work that must finish (e.g. committing a checkpoint) — and its limits |
| Advanced | **Graceful shutdown**: handling `SIGINT`/`SIGTERM` (e.g. from Docker or an orchestrator), stopping new work, finishing or cancelling in-flight work, saving state, and exiting with the right code |
| Advanced | Designing idempotent, cancellable steps so a cancelled run can be resumed (building on checkpoints from Module 2.9) |
| Advanced | Timeouts in threads and processes for comparison: `future.result(timeout=...)` does not stop the underlying work |

**How to learn it**

1. Read the topic file.
2. Run 20 tasks where task 7 fails; compare `gather`, `gather(...,
   return_exceptions=True)`, and `TaskGroup`, and record what each does to
   the other 19 tasks.
3. Press `Ctrl+C` during a run and trace what happens to every task.

**Hands-on exercise — `structured_async.py`**

1. Rewrite the Topic 03 exercise with `TaskGroup`; handle the resulting
   `ExceptionGroup` with `except*`, separating retryable from fatal errors.
2. Give each operation a 2-second timeout and the whole run a 60-second
   deadline.
3. Write a task that holds a resource (a file being written); cancel it
   and prove the resource is cleaned up and no partial file remains.
4. Implement graceful shutdown on `SIGINT` and `SIGTERM`: stop scheduling,
   let in-flight tasks finish within 10 seconds, cancel the rest, save a
   checkpoint with `shield`, and exit with a non-zero code.
5. Test cancellation and timeout behaviour.

**Checkpoint:**

- [ ] Use `TaskGroup` and handle `ExceptionGroup` with `except*`.
- [ ] Cancel tasks safely with cleanup.
- [ ] Apply per-operation timeouts and an overall deadline.
- [ ] Shut down an async job gracefully on a signal.

**Common mistakes:** catching `CancelledError` and continuing;
fire-and-forget tasks; no overall deadline; assuming a timeout on a future
stops the work behind it.

---

### Topic 05 — [Async HTTP extraction with httpx](05-async-http-extraction-with-httpx.md)

**Why here:** This is the most common real use of asyncio in data
engineering: extracting from APIs at high throughput. You combine Module
2.9's client design with Topics 03–04.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | `httpx.AsyncClient`: one client per run, `async with`, `await client.get(...)` |
| Basics | Connection limits (`httpx.Limits`), timeouts, and HTTP/2 multiplexing with the async client |
| Intermediate | Porting your Module 2.9 client: async auth flows (token refresh shared safely between concurrent tasks), async retries (`tenacity` supports coroutines), and `Retry-After` handling |
| Intermediate | **What can run concurrently**: independent requests (by id, by date window, by account) vs cursor pagination (each page depends on the previous one) — concurrency across windows, sequential within a window |
| Intermediate | Async rate limiting: sharing one limiter across all tasks (token bucket as an async context manager) |
| Intermediate | Streaming responses asynchronously (`client.stream`) and writing to disk without blocking the loop (`to_thread` for file writes, or batching) |
| Advanced | Token refresh stampede: 100 tasks see `401` at once — one refresh guarded by an `asyncio.Lock`, the others wait |
| Advanced | Adaptive throughput: slowing down when `429`s appear, speeding up when the source is healthy (awareness of AIMD-style control) |
| Advanced | Landing results: batching records from many concurrent requests into Parquet/JSON Lines files and checkpointing completed windows |
| Advanced | Measuring throughput and latency percentiles (from Module 2.2) per endpoint |

**How to learn it**

1. Read the topic file.
2. Extract the same 50,000 records from your mock API (with 200 ms latency
   and a rate limit) using sequential httpx, a thread pool, and
   `AsyncClient`; compare time, CPU, and memory.
3. Draw which requests in a cursor-paginated API can run in parallel and
   which cannot.

**Hands-on exercise — `async_extractor.py`**

1. Build `AsyncCustomersClient` with shared `AsyncClient`, OAuth
   client-credentials auth with a lock around refresh, `tenacity` retries,
   and a shared async token bucket.
2. Split a 90-day extraction into 1-day windows; run windows concurrently
   inside a `TaskGroup`, pages sequentially inside each window.
3. Land each window's records to a Parquet file and record completed
   windows in a checkpoint; kill the run and resume only incomplete
   windows.
4. Force token expiry during a run with 100 concurrent tasks; prove exactly
   one refresh happens.
5. Report requests per second, `429` count, p95 latency, and total time.

**Checkpoint:**

- [ ] Build an async API extractor with auth, retries, and rate limits.
- [ ] Decide which requests can run concurrently.
- [ ] Prevent token-refresh stampedes.
- [ ] Resume a concurrent extraction from checkpoints.

**Common mistakes:** a new `AsyncClient` per request; concurrent requests
that ignore the provider's limits; blocking file writes inside the loop;
parallelising dependent cursor pages.

---

## 8. Phase C — Coordination and Correctness (Intermediate → Advanced)

### Topic 06 — [Semaphores and bounded concurrency](06-semaphores-and-bounded-concurrency.md)

**Why here:** Unbounded concurrency is the most common production mistake:
10,000 tasks start at once, open 10,000 connections, and take down the
source or your own process. Every concurrent program needs explicit
bounds.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Why bound: remote limits, connection pools, file descriptors, memory, and fairness to other users of the source |
| Basics | `asyncio.Semaphore` and `threading.Semaphore`: at most N holders at a time; `BoundedSemaphore` for catching release bugs |
| Basics | Pattern: `async with sem: await fetch(...)` |
| Intermediate | **Concurrency limit vs rate limit**: "at most 10 requests in flight" is not "at most 10 requests per second" — most extractors need both |
| Intermediate | Bounding task creation, not just execution: a fixed pool of N worker tasks pulling from a queue vs creating 1,000,000 tasks that wait on a semaphore |
| Intermediate | Layered limits: per host, per API key, per database, and global |
| Intermediate | Matching limits across layers: HTTP client connection limits, database pool size, semaphore sizes, and worker counts should agree |
| Advanced | Bounding memory: limiting in-flight data (bytes, rows) rather than task count when payload sizes vary |
| Advanced | Finding the best concurrency level by experiment (throughput vs latency vs error rate curve) |
| Advanced | Adaptive concurrency limits that shrink on errors or rising latency (awareness) |

**How to learn it**

1. Read the topic file.
2. Launch 10,000 concurrent requests against your mock API with no bound;
   observe errors, file-descriptor limits, and memory. Then bound them.
3. Plot throughput and p95 latency for concurrency levels 1, 2, 4, …, 256.

**Hands-on exercise — `bounded.py`**

1. Build `bounded_gather(coros, limit)` with a semaphore and
   `bounded_map(func, items, workers)` with a fixed worker pool; compare
   memory for 1,000,000 items.
2. Combine a concurrency limit of 20 with a rate limit of 50 requests per
   second; verify both hold using server-side logs of the mock API.
3. Add per-host limits for two different APIs extracted in the same run.
4. Bound a concurrent PostgreSQL load so it never exceeds the pool size.
5. Produce a concurrency-level experiment chart and pick a level with a
   written justification.

**Checkpoint:**

- [ ] Bound concurrency with semaphores and worker pools.
- [ ] Explain the difference between a concurrency limit and a rate limit.
- [ ] Align limits across HTTP clients, pools, and workers.
- [ ] Choose a concurrency level from measurements.

**Common mistakes:** a semaphore per task (which bounds nothing); creating
millions of waiting tasks; bounding requests but not memory; limits that
disagree between layers.

---

### Topic 07 — [Queues and producer–consumer pipelines](07-queues-and-producer-consumer-pipelines.md)

**Why here:** Real pipelines have stages that run at different speeds:
extraction is network-bound, parsing is CPU-bound, and loading is
database-bound. Queues connect the stages and keep each one busy without
letting any of them run away.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Producer–consumer: producers put work items, consumers take them |
| Basics | `queue.Queue` (threads), `asyncio.Queue` (async), `multiprocessing.Queue` (processes) |
| Basics | `put`, `get`, `task_done()`, and `join()` to wait for all work |
| Intermediate | **Back pressure** with `maxsize`: a full queue makes fast producers wait instead of filling memory |
| Intermediate | Shutting down consumers: sentinel values ("poison pills"), one per consumer, or the queue `shutdown()` method (Python 3.13+) |
| Intermediate | **Multi-stage pipelines**: extract → parse → batch → load, each stage with its own workers and bounded queue |
| Intermediate | **Batching consumers**: collecting records until N rows or T seconds, then writing one Parquet file or one `COPY` batch |
| Advanced | Error propagation: a failing stage must stop the pipeline (or route bad items to a dead-letter list), not hang it |
| Advanced | Mixing models: async extraction feeding a process pool for CPU-heavy parsing, feeding async database loading |
| Advanced | Ordering: when stage outputs must keep input order and how to restore it (sequence numbers) |
| Advanced | Monitoring: queue depth over time shows which stage is the bottleneck |
| Advanced | In-process queues vs external queues and logs (Kafka and message brokers — Module 2.16): durability, restarts, and multiple machines |

**How to learn it**

1. Read the topic file.
2. Draw a three-stage pipeline with worker counts and queue sizes, then
   predict which stage will be the bottleneck.
3. Log queue depths every second during a run and confirm or correct your
   prediction.

**Hands-on exercise — `pipeline.py`**

1. Build an async pipeline: 1 producer paginating the mock API → queue
   (`maxsize=1000`) → 4 transformer tasks → queue → 1 batch writer writing
   Parquet every 50,000 records or 5 seconds.
2. Replace the transformers with a process pool (via `run_in_executor`) for
   a CPU-heavy transformation and measure the change.
3. Implement clean shutdown with `shutdown()` or sentinels; prove that
   every record is written exactly once.
4. Make one transformer raise an exception; ensure the whole pipeline stops
   with a clear error (or routes the record to a dead-letter file) rather
   than hanging.
5. Chart queue depths and identify the bottleneck; rebalance workers and
   re-measure.

**Checkpoint:**

- [ ] Build a multi-stage pipeline with bounded queues.
- [ ] Shut down producers and consumers cleanly.
- [ ] Batch records efficiently in a consumer.
- [ ] Propagate errors without deadlocks or hangs.
- [ ] Find a bottleneck from queue depths.

**Common mistakes:** unbounded queues (memory blow-up); forgetting
`task_done()` so `join()` never returns; one sentinel for many consumers;
a consumer crash that leaves the producer blocked forever.

---

### Topic 08 — [Race conditions, locks, and thread safety](08-race-conditions-locks-and-thread-safety.md)

**Why here:** Once several threads or tasks share anything — a counter, a
dict, a file, a token — the order of operations stops being predictable.
Race conditions are the hardest bugs to reproduce and the easiest to ship.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What a race condition is: the result depends on timing |
| Basics | Read-modify-write races: `counter += 1` is not atomic across threads |
| Basics | `threading.Lock` and `with lock:`; `asyncio.Lock` for coroutines |
| Intermediate | **Check-then-act** races: "if file does not exist, create it", "if token expired, refresh it" |
| Intermediate | Races in asyncio: any `await` between a check and an action lets another task run |
| Intermediate | Other primitives: `RLock`, `Event` (signal "ready" or "stop"), `Condition`, `Barrier` |
| Intermediate | **Deadlocks**: two locks taken in different orders; a lock held while waiting on a queue; fixes (lock ordering, timeouts, smaller critical sections) |
| Intermediate | Thread-safe data structures (`queue.Queue`) and designs that avoid sharing: each worker owns its data and results are combined at the end |
| Advanced | Designing without locks: immutability, message passing through queues, per-task state, `contextvars` for per-task context (e.g. run ids in logs) |
| Advanced | Races outside Python memory: two processes writing the same file or partition, two job runs updating the same watermark — solved with atomic renames, database transactions and row locks (Module 2.6), or advisory locks |
| Advanced | Testing for races: stress tests with many workers and repetitions, randomised delays, and `sys.setswitchinterval` to force more thread switches |
| Advanced | Why free-threaded Python (Topic 09) exposes races that the GIL used to hide |

**How to learn it**

1. Read the topic file.
2. Reproduce a lost-update race on a shared counter with threads, and a
   check-then-act race in asyncio; make both fail reliably.
3. Create a deadlock with two locks and fix it by consistent ordering.

**Hands-on exercise — `races.py`**

1. Count records across 16 threads with a plain shared counter, a locked
   counter, and per-worker counters summed at the end; compare correctness
   and speed.
2. Reproduce the token-refresh race (two tasks refreshing at once) and fix
   it with a lock plus a re-check inside the lock.
3. Reproduce two processes appending to the same output file; fix it by
   giving each worker its own file and merging, or by atomic renames.
4. Reproduce two concurrent job runs advancing the same watermark; fix it
   with a PostgreSQL advisory lock or a conditional `UPDATE`.
5. Write stress tests that run each scenario 1,000 times and fail if any
   run produces a wrong result.

**Checkpoint:**

- [ ] Explain and reproduce a race condition.
- [ ] Fix races with locks, and prefer designs that avoid shared state.
- [ ] Explain and prevent deadlocks.
- [ ] Protect shared state across processes and job runs.
- [ ] Write stress tests that expose races.

**Common mistakes:** assuming "it worked in testing" means it is
race-free; holding locks during slow I/O; locks around everything
(serialising the program); forgetting that separate processes do not share
Python locks.

---

## 9. Phase D — Choosing a Model (Advanced)

### Topic 09 — [The GIL, free-threaded Python, and choosing a model](09-gil-free-threaded-python-and-choosing-a-model.md)

**Why last:** With hands-on experience of threads, processes, and asyncio,
you can now understand the GIL precisely, evaluate Python's newer options,
and choose a model with evidence instead of folklore.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The **Global Interpreter Lock**: one thread executes Python bytecode at a time in the standard CPython build; I/O and many native libraries release it |
| Basics | Why NumPy, Polars, DuckDB, and PyArrow can use many cores from threads: their heavy work runs in native code without the GIL |
| Intermediate | **Free-threaded Python** (PEP 703): a separate CPython build without the GIL — experimental in 3.13, officially supported (but not the default) from 3.14; installing it (e.g. `3.14t`), checking with `sys._is_gil_enabled()` |
| Intermediate | Free-threading trade-offs: slower single-threaded performance, C-extension compatibility (packages must support it), and races that the GIL used to hide (Topic 08) |
| Intermediate | **Subinterpreters** (`concurrent.interpreters` and `InterpreterPoolExecutor` in Python 3.14): isolated interpreters in one process — awareness and when they may help |
| Intermediate | **Amdahl's law**: the sequential part of a job limits the maximum speed-up |
| Advanced | **Decision framework** for data engineering workloads: |
| Advanced | – Few to hundreds of blocking I/O operations → threads (`ThreadPoolExecutor`) |
| Advanced | – Thousands of concurrent network operations with async-capable libraries → asyncio |
| Advanced | – CPU-bound pure Python → processes (or free-threaded threads when your dependencies support it) |
| Advanced | – CPU-bound work inside NumPy / Polars / DuckDB / Arrow → let the library parallelise; do not add processes on top |
| Advanced | – Data too big for one machine → distributed engines (Spark in Module 2.14; Dask and Ray in Module 2.21) |
| Advanced | Hidden costs: complexity, debugging, testing, and operations — and when sequential code is the right answer |
| Advanced | Where concurrency lives in production: inside one task vs across tasks in an orchestrator (Module 2.13) vs across machines |

**How to learn it**

1. Read the topic file.
2. Run the same CPU-bound pure-Python benchmark with threads on the
   standard build and on the free-threaded build; run a NumPy-heavy
   benchmark with threads on the standard build. Explain all three
   results.
3. Apply the decision framework to ten workloads from earlier modules and
   defend each choice.

**Hands-on exercise — `model_bakeoff/`**

1. Choose four workloads: (a) download 2,000 objects from MinIO, (b) call
   an API 20,000 times, (c) validate 5 million records in pure Python,
   (d) aggregate a large Parquet dataset with Polars.
2. Implement each sequentially, with threads, with processes, and (where it
   makes sense) with asyncio; run (c) also with threads on the
   free-threaded build.
3. Measure wall time, CPU usage per core, and peak memory; compute the
   speed-up and compare it with Amdahl's-law expectations.
4. Write an ADR recommending a model per workload, including the cost in
   code complexity.

**Checkpoint:**

- [ ] Explain the GIL precisely, including when it is released.
- [ ] Explain free-threaded Python and its current trade-offs.
- [ ] Apply Amdahl's law to a pipeline.
- [ ] Choose a concurrency model for any workload and justify it with
      measurements.

**Common mistakes:** "Python can't do parallelism" (it can — processes,
native libraries, and free-threading); processes around libraries that
already use all cores; switching to free-threaded Python without checking
dependency support; adding concurrency where the bottleneck is elsewhere.

---

## 10. Consolidate — practice questions

When all nine topics are done, open
[`practice-questions.md`](practice-questions.md). For every question:

1. Classify the work: I/O-bound, CPU-bound in Python, or CPU-bound in a
   native library.
2. Identify external limits: rate limits, connection pools, CPU cores,
   memory.
3. Choose a model and write one sentence of justification.
4. Write the sequential baseline, then the concurrent version.
5. Bound it, handle failures, and implement clean shutdown.
6. Prove the results match the baseline and measure the speed-up.

---

## 11. Module mini-project — a concurrent extract–transform–load engine

This is the proof that you have finished the module.

**Scenario:** A nightly job extracts 2 million records from a rate-limited
API (your mock API with 150 ms latency, 100 requests per second, and cursor
pagination per day window), applies a CPU-heavy pure-Python enrichment to
every record, writes Parquet to MinIO, and loads PostgreSQL. The current
sequential job takes about 9 hours. The target is under 30 minutes on a
4-core machine.

Build `concurrent_etl/`, a `uv` project and CLI with:

1. **Extract** — `httpx.AsyncClient` with shared auth (single refresh under
   a lock), retries honouring `Retry-After`, a shared token-bucket rate
   limit, a concurrency limit, and day windows extracted concurrently
   inside a `TaskGroup`.
2. **Transform** — CPU-heavy enrichment in a `ProcessPoolExecutor` fed from
   an `asyncio.Queue`, with a start method set explicitly, a per-worker
   initializer loading reference data, and batched tasks.
3. **Load** — a batching consumer writing Parquet files to MinIO and
   loading PostgreSQL with `COPY` through an async connection pool whose
   size matches the loader concurrency.
4. **Flow control** — bounded queues between every stage, queue-depth
   metrics logged every 10 seconds, and a dead-letter file for bad
   records.
5. **Correctness** — no shared mutable state without protection; per-window
   checkpoints; watermarks advanced only after loading; results identical
   to the sequential baseline.
6. **Shutdown** — `SIGINT`/`SIGTERM` handling that stops extraction,
   drains or cancels in-flight work within a deadline, saves checkpoints,
   and exits non-zero; a resumed run completes only the missing windows.
7. **Evidence** — a benchmark table: sequential, threads-only,
   asyncio-only, asyncio + processes, and (for the transform stage) the
   free-threaded build; plus an ADR explaining the final design.
8. **Tests** — unit tests for every component; async tests for
   cancellation, timeouts, and shutdown; stress tests for races; an
   end-to-end test comparing output with the sequential baseline.

**Grading yourself:** the run meets the time target without exceeding the
API's rate limit or the database's connection limit; interrupting it at any
moment and resuming produces exactly the same output as an uninterrupted
run; every error is reported; and your ADR's choices match your
measurements.

---

## 12. Module self-assessment — exit criteria

Only move to Module 2.11 when you can tick every box without looking at your
notes:

- [ ] I can speed up I/O-bound work with `ThreadPoolExecutor` and handle
      every error.
- [ ] I can speed up CPU-bound work with `ProcessPoolExecutor` and control
      pickling, start methods, and oversubscription.
- [ ] I can write asyncio programs that never block the event loop.
- [ ] I can use TaskGroups, cancellation, timeouts, and graceful shutdown.
- [ ] I can build rate-limited, resumable async API extractors.
- [ ] I can bound concurrency and memory, and tell concurrency limits from
      rate limits.
- [ ] I can build multi-stage queue pipelines with back pressure and clean
      shutdown.
- [ ] I can find and fix race conditions and deadlocks.
- [ ] I can explain the GIL and free-threading and choose a model with
      evidence.
- [ ] I have finished all practice questions and the mini-project.

---

## 13. Recommended reading and references

| Resource | Relevant topics |
| --- | --- |
| Python documentation — `concurrent.futures`, `threading`, `multiprocessing`, `queue` | 01, 02, 07, 08 |
| Python documentation — `asyncio` (coroutines and tasks, TaskGroup, timeouts, queues, synchronisation primitives, developing with asyncio) | 03–08 |
| PEP 703 (making the GIL optional), PEP 779 (free-threading support status), and the Python "free-threading" HOWTO | 09 |
| PEP 734 and the `concurrent.interpreters` documentation | 09 |
| httpx documentation — async support | 05 |
| psycopg documentation — async connections and pools | 03, 07 |
| *Python Concurrency with asyncio* — Matthew Fowler (Manning) | 03–07 |
| *Fluent Python*, 2nd edition — Luciano Ramalho, chapters on concurrency models and asyncio | 01–04, 09 |
| *High Performance Python*, 3rd edition — Micha Gorelick and Ian Ozsvald (O'Reilly) | 02, 09 |

---

## 14. Where this module leads

| This module's idea | Where it goes deeper |
| --- | --- |
| Validating records concurrently | 2.11 Data Validation, Contracts, and Quality |
| Checkpoints, resumability, and pipeline state | 2.12 Transformation Patterns and Pipeline Design |
| Parallel tasks across a workflow; pools and concurrency limits in Airflow | 2.13 Orchestration and Workflow Management |
| Distributed parallelism across machines | 2.14 Distributed Processing with PySpark |
| Durable queues, consumer groups, and back pressure at scale | 2.16 Streaming and Event-Driven Data |
| Parallel object-storage transfers | 2.17 Cloud Storage and Cloud Data Platforms |
| CPU and memory limits for containers and pods | 2.18 Containers, Infrastructure, and CI/CD |
| Testing concurrent and async code | 2.19 Testing Data Pipelines |
| Metrics and traces across concurrent tasks | 2.20 Observability — OpenTelemetry |
| Dask, Ray, Numba, and benchmarking | 2.21 Performance, Scaling, and Cost Optimization |
| Async APIs for serving data | 2.22 Serving Data for Analytics, ML, and AI |

Concurrency is a tool, not a goal. The habits you build here — start from a
sequential baseline, classify the work, bound everything, never lose an
error, shut down cleanly, and prove the speed-up — are what let you make
pipelines dramatically faster without making them fragile.
