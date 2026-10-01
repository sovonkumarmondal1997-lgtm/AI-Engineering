# Queues and Producer-Consumer Pipelines

> **Stage 2 --- Python for Data Engineering**\
> **Module 2.10 --- Concurrency and Parallelism in Practice**\
> **Phase C --- Coordination and Correctness**

> **Core principle:** Concurrency is a tool, not a goal. Start from a
> sequential baseline, classify the work, bound everything, never lose
> an error, shut down cleanly, and prove the speed-up.

------------------------------------------------------------------------

## Learning Objectives

By the end of this chapter, you should be able to:

1.  Explain what a queue is and why FIFO exists.
2.  Explain the producer-consumer pattern.
3.  Explain decoupling and buffering.
4.  Explain bounded versus unbounded queues.
5.  Explain `maxsize`, `put()`, `get()`, `task_done()`, and `join()`.
6.  Use `queue.Queue` with threads.
7.  Use `asyncio.Queue` with asynchronous tasks.
8.  Use `multiprocessing.Queue` for process-to-process communication.
9.  Design multiple-producer and multiple-consumer systems.
10. Explain worker pools and queue-based load distribution.
11. Explain backpressure and how it propagates through pipeline stages.
12. Design multi-stage Extract → Parse → Transform → Batch → Load
    pipelines.
13. Choose stage-specific concurrency based on measured capacity.
14. Design size-based and time-based batching.
15. Account for worker errors and failed records.
16. Understand dead-letter concepts.
17. Distinguish queue order from completion order.
18. Preserve order with sequence numbers when required.
19. Design sentinel-based and Python 3.13+ queue shutdown.
20. Combine asyncio I/O with process-based CPU workers.
21. Bound memory with queue capacity.
22. Use queue depth as an operational signal.
23. Benchmark throughput, latency, and end-to-end correctness.
24. Debug hangs, deadlocks, missing `task_done()`, worker crashes, and
    shutdown races.
25. Decide when an in-process queue is appropriate and when durable
    external messaging is required.
26. Design a production-grade concurrent Data Engineering pipeline.

------------------------------------------------------------------------

# 1. Introduction

A queue is a coordination mechanism that allows one part of a program to
hand work to another part without requiring both parts to execute at
exactly the same speed or time.

The simplest model is:

``` text
Producer
    |
    v
  Queue
    |
    v
Consumer
```

This looks simple, but it solves several important systems problems:

-   decoupling;
-   buffering;
-   synchronization;
-   workload distribution;
-   controlled concurrency;
-   backpressure;
-   stage isolation.

In Data Engineering, these properties appear everywhere.

A pipeline might look like:

``` text
HTTP API
   |
   v
Extract
   |
   v
Parse
   |
   v
Transform
   |
   v
Batch
   |
   v
PostgreSQL / Object Storage
```

If every stage calls the next stage directly, the stages become tightly
coupled. If each stage communicates through bounded queues, each stage
can have its own workers, capacity, and failure behavior.

The queue is therefore not merely a Python container.

It is a **coordination boundary**.

------------------------------------------------------------------------

# 2. The Restaurant Analogy

Imagine a restaurant kitchen.

``` text
Customers
   |
   v
Order Counter
   |
   v
Order Queue
   |
   +--> Cook 1
   +--> Cook 2
   +--> Cook 3
   |
   v
Completed Food
```

Mapping:

  Restaurant             Data pipeline
  ---------------------- ---------------------
  Customer order         Work item
  Order taker            Producer
  Order queue            Queue
  Cook                   Consumer/worker
  Kitchen capacity       Downstream capacity
  Waiting orders         Buffered work
  Too many orders        Producer pressure
  Limited order space    Bounded queue
  Cooks cannot keep up   Consumer bottleneck

The analogy is useful because it makes the central idea intuitive:

> A producer should not be allowed to create unlimited work merely
> because it can produce faster than the consumer can process.

But the analogy is imperfect.

A real software queue has explicit semantics around:

-   synchronization;
-   blocking;
-   task accounting;
-   cancellation;
-   serialization;
-   process boundaries;
-   failure propagation;
-   shutdown.

------------------------------------------------------------------------

# 3. Why Queues Appear After Bounded Concurrency

A semaphore answers a question such as:

> "How many operations may be active at once?"

A queue answers a different question:

> "Where does work wait when it cannot be processed immediately?"

They can be used together.

``` text
Producer
   |
   v
Bounded Queue
   |
   v
Workers
   |
   v
Semaphore / downstream limit
   |
   v
External system
```

This chapter does not replace the preceding bounded-concurrency lesson.
Instead, it adds **work buffering and stage coordination**.

The important distinction is:

``` text
Concurrency limit
    = how much work is active

Queue
    = where pending work waits
```

------------------------------------------------------------------------

# 4. The Problem With Direct Pipeline Connections

Start with a direct producer-consumer relationship:

``` python
def produce():
    for record in records:
        consume(record)


def consume(record):
    process(record)
```

The producer cannot proceed independently of the consumer.

If extraction takes:

``` text
100 ms
```

and transformation takes:

``` text
1 second
```

then extraction is forced to move at transformation speed.

A queue introduces a buffer:

``` text
Producer
    |
    v
 Queue
    |
    v
Consumer
```

Now the producer and consumer can progress independently for short
periods.

------------------------------------------------------------------------

# 5. Producer Faster Than Consumer

Suppose:

``` text
Producer = 1,000 records/sec
Consumer =   100 records/sec
```

The difference is:

``` text
1,000 - 100 = 900 records/sec
```

So if there are no failures and rates remain constant, the backlog grows
by approximately:

``` text
900 records/sec
```

After 1 second:

``` text
~900 queued records
```

After 10 seconds:

``` text
~9,000 queued records
```

After 60 seconds:

``` text
~54,000 queued records
```

This is a critical systems insight:

> A queue can absorb a temporary mismatch. It cannot eliminate a
> permanent throughput mismatch.

If the producer permanently produces more work than the consumer can
process, an unbounded queue eventually becomes a memory problem.

------------------------------------------------------------------------

# 6. What Is a Queue?

A queue is an ordered collection of work items where the usual policy is
**FIFO**:

> First In, First Out.

Example:

``` text
A -> B -> C -> D
```

If the queue receives:

``` text
A
B
C
D
```

the normal removal order is:

``` text
A
B
C
D
```

Terminology:

  Term          Meaning
  ------------- ---------------------------
  Enqueue       Add an item
  Dequeue       Remove an item
  Producer      Creates work
  Consumer      Processes work
  Worker        A consumer execution unit
  Item          Unit of work
  Queue depth   Number of pending items

The queue gives the producer and consumer a shared coordination point.

------------------------------------------------------------------------

# 7. FIFO Does Not Mean Completion Order

This distinction becomes important later.

Suppose:

``` text
Input:
1
2
3
```

Three workers receive:

``` text
Worker A -> 1
Worker B -> 2
Worker C -> 3
```

Worker C might finish first.

Therefore:

``` text
Queue retrieval order:
1 -> 2 -> 3

Completion order:
3 -> 1 -> 2
```

FIFO controls **retrieval order from the queue**.

It does not guarantee that concurrently processed work completes in the
same order.

If business correctness requires ordering, you need an explicit ordering
strategy.

------------------------------------------------------------------------

# 8. The Producer-Consumer Pattern

The fundamental architecture is:

``` text
Producer
   |
   v
 Queue
   |
   v
Consumer
```

A minimal Python queue:

``` python
from queue import Queue

queue = Queue()

queue.put("record-1")
queue.put("record-2")

print(queue.get())
print(queue.get())
```

Execution:

``` text
queue.put("record-1")
       |
       v
[A]

queue.put("record-2")
       |
       v
[A, B]

queue.get()
       |
       v
returns A

queue.get()
       |
       v
returns B
```

The producer does not need to know how the consumer processes the item.

The consumer does not need to know how the producer generated it.

That is decoupling.

------------------------------------------------------------------------

# 9. A Simple Threaded Producer-Consumer

``` python
from queue import Queue
from threading import Thread
import time


def producer(queue: Queue) -> None:
    for record_id in range(10):
        queue.put(record_id)
        print(f"produced {record_id}")
        time.sleep(0.05)


def consumer(queue: Queue) -> None:
    while True:
        item = queue.get()

        try:
            print(f"consuming {item}")
            time.sleep(0.1)
        finally:
            queue.task_done()


queue = Queue()

producer_thread = Thread(
    target=producer,
    args=(queue,),
)

consumer_thread = Thread(
    target=consumer,
    args=(queue,),
    daemon=True,
)

producer_thread.start()
consumer_thread.start()

producer_thread.join()
queue.join()
```

The important ideas are:

``` text
producer_thread
      |
      v
   Queue
      |
      v
consumer_thread
```

and:

``` python
queue.task_done()
```

which tells the queue:

> "The work item retrieved by this consumer has finished processing."

------------------------------------------------------------------------

# 10. Why Decoupling Matters

Suppose an API extractor produces:

``` text
500 records/sec
```

while a transformer can process:

``` text
300 records/sec
```

Without a queue, extraction and transformation are tightly coupled.

With a queue:

``` text
API
 |
 v
Extractor
 |
 v
Queue
 |
 v
Transformer
```

The extractor can temporarily run faster and build a small buffer.

That buffer absorbs bursts.

But if the difference continues:

``` text
Extractor:   500/sec
Transformer:  300/sec
```

the queue grows.

If the queue is bounded, eventually the extractor must slow down.

This is exactly what we want.

------------------------------------------------------------------------

# 11. Buffering

A queue is a buffer between stages.

Suppose producer and consumer rates fluctuate:

``` text
Time       Producer       Consumer
----------------------------------
t1          800/sec        600/sec
t2          300/sec        700/sec
t3          900/sec        500/sec
t4          400/sec        800/sec
```

A queue can absorb short-term differences.

Conceptually:

``` text
Producer bursts
       |
       v
   +-------+
   | Queue |
   +-------+
       |
       v
Consumer drains
```

The key distinction is:

### Temporary imbalance

A queue is useful.

### Permanent imbalance

A queue only postpones the problem.

If:

``` text
average producer rate > average consumer rate
```

the backlog eventually grows.

------------------------------------------------------------------------

# 12. Queue Growth Mathematics

A simple model is:

``` text
queue_growth_rate =
    producer_rate - consumer_rate
```

If:

``` text
producer = 1000/sec
consumer = 800/sec
```

then:

``` text
growth = +200/sec
```

The queue grows.

If:

``` text
producer = 800/sec
consumer = 800/sec
```

then:

``` text
growth = 0
```

The queue can remain stable around an operating level.

If:

``` text
producer = 600/sec
consumer = 800/sec
```

then:

``` text
growth = -200/sec
```

The queue drains.

This is not a complete performance model because real systems have:

-   variable latency;
-   failures;
-   retries;
-   batching;
-   worker startup costs;
-   downstream limits;
-   bursty arrivals.

But it is an excellent first mental model.

------------------------------------------------------------------------

# 13. Unbounded vs Bounded Queues

An unbounded queue allows the pending backlog to grow until another
resource becomes the limiting factor.

A bounded queue explicitly limits pending work.

``` python
from queue import Queue

unbounded = Queue()

bounded = Queue(maxsize=1000)
```

The production difference is significant.

## Unbounded

``` text
Producer
   |
   v
Unlimited-ish memory growth
   |
   v
Eventually memory pressure
```

## Bounded

``` text
Producer
   |
   v
+----------------+
| Queue max=1000 |
+----------------+
   |
   v
Consumer
```

When the queue fills, the producer can no longer add work normally.

That creates backpressure.

------------------------------------------------------------------------

# 14. `maxsize`

For `queue.Queue`:

``` python
queue = Queue(maxsize=1000)
```

The queue's configured capacity is 1,000 items.

This does not mean:

> "The process can use exactly the memory occupied by 1,000 bytes."

It means the queue can contain up to approximately 1,000 queued items
according to its item-count semantics.

If items are large, the memory footprint can still be large.

------------------------------------------------------------------------

# 15. Blocking `put()`

Default behavior:

``` python
queue.put(item)
```

A producer can wait when the bounded queue is full.

Conceptually:

``` text
Queue full
   |
   v
producer waits
   |
   v
consumer removes item
   |
   v
space becomes available
   |
   v
producer continues
```

This is a basic backpressure mechanism.

You can make the blocking intent explicit:

``` python
queue.put(item, block=True)
```

You can also use a timeout:

``` python
queue.put(
    item,
    block=True,
    timeout=2,
)
```

------------------------------------------------------------------------

# 16. Non-Blocking `put()`

You can request immediate failure:

``` python
from queue import Full

try:
    queue.put(item, block=False)
except Full:
    print("queue is full")
```

This is useful when the application has an explicit policy for queue
saturation.

Possible policies include:

-   retry later;
-   drop low-value work;
-   fail the pipeline;
-   redirect to durable storage;
-   apply a different admission policy.

Do not silently discard records unless data loss is explicitly
acceptable.

------------------------------------------------------------------------

# 17. Backpressure

Backpressure is one of the most important concepts in concurrent data
systems.

### Beginner explanation

Backpressure means:

> When downstream cannot keep up, upstream is forced to slow down.

### Technical explanation

A bounded queue converts downstream capacity pressure into upstream
waiting.

``` text
Fast Producer
     |
     v
Bounded Queue
     |
     v
Slow Consumer
```

As the queue fills:

``` text
Queue fills
    |
    v
Producer blocks
    |
    v
Production rate decreases
    |
    v
Memory remains bounded
```

This is much safer than allowing unlimited backlog.

------------------------------------------------------------------------

# 18. Without Backpressure

Consider:

``` text
Producer: 10,000 records/sec
Consumer: 1,000 records/sec
```

An unbounded design can become:

``` text
10,000/sec in
       |
       v
+--------------------+
| growing memory     |
| growing backlog    |
+--------------------+
       |
       v
1,000/sec out
```

The queue hides the mismatch until memory or another resource becomes
exhausted.

The system may appear healthy initially and then fail catastrophically.

------------------------------------------------------------------------

# 19. With Backpressure

With a bounded queue:

``` text
10,000/sec
    |
    v
+-----------+
| max=5,000 |
+-----------+
    |
    v
1,000/sec
```

Once the queue fills:

``` text
producer blocks
```

The producer cannot continue indefinitely.

This creates a controlled operating boundary.

Backpressure does not increase the consumer's capacity.

It protects the system from unlimited demand.

------------------------------------------------------------------------

# 20. `queue.Queue`

Python's `queue.Queue` is designed for thread-based coordination.

Import:

``` python
from queue import Queue
```

Important methods:

``` python
queue.put(item)
item = queue.get()
queue.task_done()
queue.join()
```

Useful inspection methods include:

``` python
queue.qsize()
queue.empty()
queue.full()
```

But these inspection methods should not be treated as perfectly reliable
synchronization decisions.

For example:

``` python
if not queue.empty():
    item = queue.get()
```

is vulnerable to another thread changing the queue between the two
operations.

Prefer atomic queue operations with explicit blocking/timeout behavior.

------------------------------------------------------------------------

# 21. `get()`

Basic:

``` python
item = queue.get()
```

The consumer waits if no item is available.

With non-blocking behavior:

``` python
from queue import Empty

try:
    item = queue.get(block=False)
except Empty:
    print("nothing available")
```

With timeout:

``` python
try:
    item = queue.get(
        block=True,
        timeout=2,
    )
except Empty:
    print("no item arrived")
```

Timeouts can be useful for periodically checking shutdown state or
health conditions.

------------------------------------------------------------------------

# 22. `task_done()`

Every successful:

``` python
item = queue.get()
```

must eventually have exactly one matching:

``` python
queue.task_done()
```

Correct:

``` python
item = queue.get()

try:
    process(item)
finally:
    queue.task_done()
```

The `finally` is important because processing can fail.

If:

``` python
process(item)
```

raises an exception, the queue still needs to know what happened to the
task according to the application's chosen failure semantics.

------------------------------------------------------------------------

# 23. `join()`

`queue.join()` waits until all items that have been retrieved from the
queue have been marked complete with `task_done()`.

Typical pattern:

``` python
producer()
queue.join()
```

Conceptually:

``` text
put A
put B
put C

unfinished work = 3

get A
task_done()
unfinished work = 2

get B
task_done()
unfinished work = 1

get C
task_done()
unfinished work = 0

queue.join() returns
```

This is a work-accounting mechanism.

It does not mean:

> "The queue is empty at this exact instant and the entire application
> is shut down."

It means the queue's unfinished-task counter has reached zero.

------------------------------------------------------------------------

# 24. The `task_done()` / `join()` Contract

Think of:

``` text
put()
  |
  v
unfinished task count increases

get()
  |
  v
worker owns task

task_done()
  |
  v
unfinished task count decreases

join()
  |
  v
wait until unfinished count == 0
```

The relationship is strict.

### Forgetting `task_done()`

``` python
item = queue.get()
process(item)
# task_done forgotten
```

Then:

``` python
queue.join()
```

may wait forever.

### Calling twice

``` python
queue.task_done()
queue.task_done()
```

for one successful `get()` can raise:

``` text
ValueError: task_done() called too many times
```

This is why the safest consumer pattern is:

``` python
item = queue.get()
try:
    process(item)
finally:
    queue.task_done()
```

------------------------------------------------------------------------

# 25. Multiple Consumers

A queue naturally supports worker pools.

``` text
                 +--> Consumer 1
                 |
Producer --> Queue+--> Consumer 2
                 |
                 +--> Consumer 3
                 |
                 +--> Consumer 4
```

Each worker competes for available items.

A threaded example:

``` python
from queue import Queue
from threading import Thread
import time


def consumer(
    name: str,
    queue: Queue,
) -> None:
    while True:
        item = queue.get()

        try:
            print(f"{name} processing {item}")
            time.sleep(0.1)
        finally:
            queue.task_done()


queue = Queue(maxsize=100)

workers = [
    Thread(
        target=consumer,
        args=(f"worker-{i}", queue),
        daemon=True,
    )
    for i in range(4)
]

for worker in workers:
    worker.start()

for item in range(20):
    queue.put(item)

queue.join()
```

The queue distributes work among consumers.

------------------------------------------------------------------------

# 26. Worker Count

More workers are not automatically better.

Suppose:

``` text
API supports 10 concurrent requests
database has 8 useful connections
CPU has 4 effective cores for this workload
```

A design with 100 consumers may simply create:

-   contention;
-   context switching;
-   connection pressure;
-   retries;
-   rate-limit errors;
-   memory usage.

Worker count should be chosen from:

-   measured stage throughput;
-   CPU capacity;
-   network capacity;
-   API limits;
-   database pool limits;
-   memory;
-   downstream saturation.

------------------------------------------------------------------------

# 27. Multiple Producers

The pattern also supports multiple producers.

``` text
Producer A \
Producer B  \
Producer C   +--> Queue --> Workers
Producer D  /
```

Example use cases:

-   multiple API endpoints;
-   multiple input files;
-   multiple partitions;
-   independent extraction windows;
-   multiple object-store prefixes.

Threaded example:

``` python
from queue import Queue
from threading import Thread


def producer(
    name: str,
    queue: Queue,
    start: int,
) -> None:
    for offset in range(10):
        queue.put(
            {
                "producer": name,
                "value": start + offset,
            }
        )


queue = Queue(maxsize=50)

producers = [
    Thread(
        target=producer,
        args=(f"producer-{i}", queue, i * 10),
    )
    for i in range(3)
]

for thread in producers:
    thread.start()

for thread in producers:
    thread.join()
```

A production design must still define how producer failures are
surfaced.

------------------------------------------------------------------------

# 28. Queue-Based Load Distribution

A shared queue provides a simple work-distribution mechanism:

``` text
                 Queue
               /   |   \
              /    |    \
             v     v     v
           W1     W2     W3
```

If workers have similar processing costs, work tends to distribute
naturally.

If processing costs vary dramatically, one worker may receive a very
expensive item while others finish quickly.

This can create uneven utilization.

Possible responses include:

-   smaller work units;
-   partitioning;
-   prioritization;
-   work stealing in more advanced architectures;
-   explicit scheduling.

Do not assume FIFO alone solves load balancing.

------------------------------------------------------------------------

# 29. `asyncio.Queue`

Asyncio programs should generally coordinate async tasks with:

``` python
asyncio.Queue
```

rather than using a blocking thread queue.

``` python
import asyncio

queue = asyncio.Queue(maxsize=100)
```

Producer:

``` python
await queue.put(item)
```

Consumer:

``` python
item = await queue.get()
```

Accounting:

``` python
queue.task_done()
```

Waiting for all work:

``` python
await queue.join()
```

The important difference is that queue waiting cooperates with the event
loop.

------------------------------------------------------------------------

# 30. Why Not `queue.Queue` Inside Async Tasks?

This is dangerous:

``` python
async def producer(queue):
    queue.put(item)
```

if `queue.put()` can block the event-loop thread.

Similarly:

``` python
async def consumer(queue):
    item = queue.get()
```

can block the event loop.

For asyncio task coordination, use:

``` python
asyncio.Queue
```

so waiting is asynchronous:

``` python
await queue.put(item)
item = await queue.get()
```

------------------------------------------------------------------------

# 31. Complete Async Producer-Consumer

``` python
import asyncio


async def producer(
    queue: asyncio.Queue,
    count: int,
) -> None:
    for record_id in range(count):
        await queue.put(record_id)
        print(f"produced {record_id}")

    print("producer finished")


async def consumer(
    name: str,
    queue: asyncio.Queue,
) -> None:
    while True:
        item = await queue.get()

        try:
            await asyncio.sleep(0.05)
            print(f"{name} processed {item}")
        finally:
            queue.task_done()


async def main() -> None:
    queue = asyncio.Queue(maxsize=10)

    consumers = [
        asyncio.create_task(
            consumer(f"worker-{i}", queue)
        )
        for i in range(3)
    ]

    await producer(queue, count=30)
    await queue.join()

    for task in consumers:
        task.cancel()

    await asyncio.gather(
        *consumers,
        return_exceptions=True,
    )


asyncio.run(main())
```

This demonstrates:

-   bounded queue;
-   async producer;
-   multiple async consumers;
-   `task_done()`;
-   `await queue.join()`;
-   explicit consumer cancellation.

The next sections improve the shutdown design.

------------------------------------------------------------------------

# 32. Async Backpressure

With:

``` python
queue = asyncio.Queue(maxsize=100)
```

and:

``` python
await queue.put(item)
```

the producer waits asynchronously if the queue is full.

Conceptually:

``` text
Producer task
     |
     v
await queue.put()
     |
     | queue full
     v
Task suspended
     |
     v
Other async tasks run
     |
     v
Consumer removes item
     |
     v
Producer resumes
```

This is backpressure without blocking the event-loop thread.

------------------------------------------------------------------------

# 33. A Realistic Async ETL Pipeline

Consider:

``` text
API extraction
      |
      v
Bounded Queue
      |
      v
Transform consumers
      |
      v
Output
```

Example:

``` python
import asyncio


async def api_producer(
    queue: asyncio.Queue,
) -> None:
    for record_id in range(100):
        await asyncio.sleep(0.001)

        await queue.put(
            {
                "id": record_id,
                "value": record_id * 2,
            }
        )


async def transformer(
    name: str,
    queue: asyncio.Queue,
) -> None:
    while True:
        record = await queue.get()

        try:
            await asyncio.sleep(0.01)

            transformed = {
                **record,
                "value": record["value"] + 1,
            }

            print(
                name,
                transformed["id"],
            )
        finally:
            queue.task_done()
```

The producer does not directly invoke the transformer.

That separation is the architectural value.

------------------------------------------------------------------------

# 34. `multiprocessing.Queue`

`multiprocessing.Queue` is designed for communication between processes.

``` python
from multiprocessing import Process, Queue
```

Conceptually:

``` text
Main Process
     |
     v
multiprocessing.Queue
     |
     +----> Worker Process A
     |
     +----> Worker Process B
```

Unlike a normal in-process thread queue, the processes have separate
memory spaces.

Therefore data generally has to cross a process boundary.

That introduces:

-   serialization;
-   copying;
-   pickling;
-   IPC overhead.

------------------------------------------------------------------------

# 35. Process Queue Example

``` python
from multiprocessing import Process, Queue


def worker(queue: Queue) -> None:
    while True:
        item = queue.get()

        if item is None:
            break

        result = item * item
        print(
            f"processed {item} -> {result}"
        )


if __name__ == "__main__":
    queue = Queue()

    workers = [
        Process(
            target=worker,
            args=(queue,),
        )
        for _ in range(2)
    ]

    for worker_process in workers:
        worker_process.start()

    for value in range(10):
        queue.put(value)

    for _ in workers:
        queue.put(None)

    for worker_process in workers:
        worker_process.join()
```

The sentinel is used to tell each process that no more work is coming.

This example intentionally focuses on queue-based process communication
rather than repeating the ProcessPoolExecutor lesson.

------------------------------------------------------------------------

# 36. Queue Types Comparison

  -------------------------------------------------------------------------------------
  Queue                     Execution      Waiting model  Process        Typical use
                            model                         boundary       
  ------------------------- -------------- -------------- -------------- --------------
  `queue.Queue`             Threads        Blocking       No             Threaded
                                                                         pipelines

  `asyncio.Queue`           Asyncio tasks  Async          No             Async
                                           suspension                    pipelines

  `multiprocessing.Queue`   Processes      IPC-oriented   Yes            Process
                                                                         pipelines
  -------------------------------------------------------------------------------------

Additional considerations:

  ---------------------------------------------------------------------------------
  Property          `queue.Queue`       `asyncio.Queue`   `multiprocessing.Queue`
  ----------------- ------------------- ----------------- -------------------------
  Shared address    Yes                 Yes               No
  space                                                   

  Serialization     Usually no          Usually no        Yes
  between workers                                         

  Async-native      No                  Yes               No

  Thread            Yes                 Async tasks       Process IPC
  synchronization                                         

  Typical overhead  Low                 Low               Higher

  Best fit          Blocking/threaded   Async I/O         Process isolation
                    work                                  

  Main cost         Thread contention   Task coordination IPC + serialization
  ---------------------------------------------------------------------------------

Use the queue that matches the execution model.

------------------------------------------------------------------------

# 37. Multi-Stage Pipelines

A real Data Engineering pipeline often has several stages:

``` text
Extract
   |
 Queue A
   |
Parse
   |
 Queue B
   |
Transform
   |
 Queue C
   |
Batch
   |
 Queue D
   |
Load
```

A more detailed architecture:

``` text
API
 |
 v
Extractor Workers
 |
 v
Queue A
 |
 v
Parser Workers
 |
 v
Queue B
 |
 v
Transformer Workers
 |
 v
Queue C
 |
 v
Batcher
 |
 v
Loader Workers
 |
 v
PostgreSQL / Object Storage
```

Each queue separates stages.

This creates:

-   stage isolation;
-   independent worker counts;
-   explicit buffering;
-   backpressure propagation;
-   measurable bottlenecks.

------------------------------------------------------------------------

# 38. Extract → Parse → Transform → Batch → Load

A common Data Engineering progression is:

``` text
Extract
  |
  v
Parse
  |
  v
Transform
  |
  v
Batch
  |
  v
Load
```

Each stage may have a different bottleneck.

For example:

``` text
Extract:    network-bound
Parse:      CPU/light memory
Transform:  CPU-bound
Batch:      memory/latency
Load:       database-bound
```

Therefore, a single global worker count is often a poor abstraction.

------------------------------------------------------------------------

# 39. Stage-Specific Concurrency

Suppose measurements show:

``` text
Extract:    20 useful concurrent requests
Transform:   4 CPU workers
Load:        8 DB connections
```

A sensible architecture might be:

``` text
20 extraction workers
        |
        v
Queue
        |
        v
4 transformation workers
        |
        v
Queue
        |
        v
8 load operations
```

These numbers are examples, not recommendations.

They should come from:

-   source limits;
-   CPU measurements;
-   DB pool capacity;
-   storage throughput;
-   memory budget;
-   latency requirements.

------------------------------------------------------------------------

# 40. Backpressure Propagation

Consider:

``` text
Extract
  |
Queue A
  |
Transform
  |
Queue B
  |
Load
```

Suppose the database becomes slow.

Then:

``` text
Load slows
   |
   v
Queue B fills
   |
   v
Transform workers block on Queue B
   |
   v
Queue A fills
   |
   v
Extract slows
```

This is **backpressure propagation**.

Diagram:

``` text
DATABASE SLOWS
      |
      v
 Queue B fills
      |
      v
 Transform slows
      |
      v
 Queue A fills
      |
      v
 Extract slows
```

This is one of the most important production concepts in pipeline
architecture.

A healthy bounded pipeline lets downstream capacity influence upstream
production before memory becomes unbounded.

------------------------------------------------------------------------

# 41. Queue Depth as an Operational Signal

Queue depth tells you how much work is waiting.

Suppose:

``` text
Queue A: 5
Queue B: 980
Queue C: 10
```

with:

``` text
Queue B maxsize = 1000
```

Queue B is near saturation.

That suggests the stage after Queue B is likely unable to keep up with
the stage before it.

Queue depth alone does not prove the root cause.

You should inspect:

-   consumer throughput;
-   worker utilization;
-   downstream latency;
-   error/retry rate;
-   external service limits.

------------------------------------------------------------------------

# 42. Producer Bottleneck

Scenario:

``` text
Producer = 100 records/sec
Consumer capacity = 1000 records/sec
```

Expected behavior:

``` text
Queue stays mostly empty
```

This suggests the producer is the bottleneck.

Potential causes:

-   slow API;
-   rate limit;
-   source database;
-   network;
-   authentication;
-   extraction logic.

Adding more consumers will not fix this.

------------------------------------------------------------------------

# 43. Consumer Bottleneck

Scenario:

``` text
Producer = 1000 records/sec
Consumer = 100 records/sec
```

Expected behavior:

``` text
Queue depth increases
```

If bounded:

``` text
Queue eventually reaches maxsize
```

Then the producer experiences backpressure.

Potential causes:

-   CPU-heavy transformation;
-   slow database;
-   expensive parsing;
-   downstream rate limit;
-   insufficient worker capacity.

The queue is giving you evidence.

------------------------------------------------------------------------

# 44. Batching

Queues and batching frequently work together.

Without batching:

``` text
record
  |
  v
DB INSERT
```

With batching:

``` text
record
record
record
  |
  v
Batch of 1000
  |
  v
Bulk load
```

Batching can reduce:

-   network round trips;
-   transaction overhead;
-   per-request overhead;
-   database command overhead.

For PostgreSQL, bulk loading techniques such as `COPY` can be much more
appropriate than issuing one insert per record for large ingestion
workloads.

------------------------------------------------------------------------

# 45. Batch Size Trade-Off

Small batches:

``` text
+ low latency
+ lower memory
- more overhead
- more database round trips
```

Large batches:

``` text
+ higher throughput
+ better amortization
- more memory
- higher latency
- larger failure unit
```

There is no universal optimal batch size.

Measure:

-   load throughput;
-   batch duration;
-   memory;
-   transaction duration;
-   failure recovery cost;
-   end-to-end latency.

------------------------------------------------------------------------

# 46. Size-Based Batching

A simple batcher:

``` python
def make_batches(records, batch_size):
    batch = []

    for record in records:
        batch.append(record)

        if len(batch) >= batch_size:
            yield batch
            batch = []

    if batch:
        yield batch
```

For:

``` python
records = range(7)
batch_size = 3
```

the batches are:

``` text
[0, 1, 2]
[3, 4, 5]
[6]
```

The final partial batch must not be forgotten.

------------------------------------------------------------------------

# 47. Async Queue Batching

``` python
import asyncio


async def batcher(
    queue: asyncio.Queue,
    batch_size: int,
) -> list[int]:
    batch = []

    while len(batch) < batch_size:
        item = await queue.get()

        try:
            batch.append(item)
        finally:
            queue.task_done()

    return batch
```

A production batcher usually needs to handle both:

-   size threshold;
-   time threshold.

Otherwise, a low-volume stream can wait indefinitely for enough records.

------------------------------------------------------------------------

# 48. Time-Based Batching

A streaming-style loader may use:

``` text
max 1,000 records
OR
max 5 seconds
```

Whichever happens first.

Conceptually:

``` text
records arrive
   |
   +---- size reaches 1000 ---> flush
   |
   +---- 5 seconds elapsed ---> flush
```

This balances:

-   throughput;
-   latency;
-   memory.

------------------------------------------------------------------------

# 49. Async Size-or-Time Batcher

``` python
import asyncio


async def get_batch(
    queue: asyncio.Queue,
    max_size: int,
    timeout_seconds: float,
):
    batch = []

    while len(batch) < max_size:
        try:
            item = await asyncio.wait_for(
                queue.get(),
                timeout=timeout_seconds,
            )
        except asyncio.TimeoutError:
            break

        batch.append(item)
        queue.task_done()

    return batch
```

This is intentionally educational.

Production batching should carefully consider:

-   cancellation;
-   timeout semantics;
-   task accounting;
-   final shutdown;
-   partial batches;
-   loader failures.

------------------------------------------------------------------------

# 50. Batching Between Queue and Loader

A common architecture is:

``` text
Producer
   |
Queue
   |
Batcher
   |
Batch
   |
Database COPY / bulk insert
```

The queue handles:

``` text
coordination + buffering + backpressure
```

The batcher handles:

``` text
grouping work
```

The loader handles:

``` text
durable output
```

Keeping those responsibilities distinct makes the pipeline easier to
reason about.

------------------------------------------------------------------------

# 51. Error Propagation

Every stage can fail.

``` text
Producer
   |
Queue
   |
Transform
   |
Queue
   |
Loader
```

Examples:

-   API request fails;
-   JSON is malformed;
-   transformation raises;
-   database connection fails;
-   batch write fails.

A critical rule is:

> Never silently lose errors.

A worker that crashes without informing the pipeline can produce a
system that appears alive while silently processing incomplete data.

------------------------------------------------------------------------

# 52. Consumer Failure

Basic pattern:

``` python
item = queue.get()

try:
    process(item)
finally:
    queue.task_done()
```

But `task_done()` only solves task accounting.

It does not decide what the application should do after failure.

Possible policies:

1.  Fail the entire pipeline.
2.  Retry.
3.  Send to a dead-letter destination.
4.  Skip with explicit accounting.
5.  Stop only the affected partition/stage.

The correct choice depends on data correctness requirements.

------------------------------------------------------------------------

# 53. Failure Policy Must Be Explicit

Consider a transformation error:

``` text
record 123
   |
   v
transform
   |
   X
error
```

Possible outcomes:

``` text
Retry
  |
  +--> success
  |
  +--> dead letter

or

Fail pipeline

or

Skip with explicit error accounting
```

Never let the behavior be an accidental consequence of an uncaught
exception.

------------------------------------------------------------------------

# 54. Dead-Letter Concept

A dead-letter destination captures work that could not be successfully
processed.

``` text
Main Queue
    |
    v
Consumer
  /   \
 /     \
success failure
 |       |
 v       v
next    Dead Letter
stage
```

A dead-letter record may include:

``` python
{
    "source_id": "api-7",
    "record": {...},
    "error": "invalid timestamp",
    "exception_type": "ValueError",
    "timestamp": "...",
    "retry_count": 3,
}
```

The exact representation depends on the system.

The important principle is:

> A failed record should be recoverable or explicitly accounted for.

------------------------------------------------------------------------

# 55. Dead-Letter Is Not a Free Retry System

A dead-letter mechanism does not automatically solve:

-   root-cause correction;
-   retry policy;
-   poison records;
-   ordering;
-   deduplication;
-   replay.

It is an accounting and recovery boundary.

For local educational pipelines, a Python list or file may be enough to
demonstrate the concept.

Distributed production systems may use durable queues, object storage,
database tables, or message-system dead-letter facilities.

------------------------------------------------------------------------

# 56. Ordering

With one consumer:

``` text
1 -> 2 -> 3 -> 4
```

processing can naturally follow queue order.

With multiple consumers:

``` text
Queue:
1 2 3 4

W1 gets 1
W2 gets 2
W3 gets 3
W4 gets 4
```

Completion can be:

``` text
3 -> 1 -> 4 -> 2
```

Therefore:

``` text
queue order != completion order
```

If order is irrelevant, do not pay the complexity cost of preserving it.

------------------------------------------------------------------------

# 57. Sequence Numbers

If order matters, attach a sequence number:

``` python
{
    "sequence": 123,
    "record": record,
}
```

Workers can process concurrently.

Results can later be reordered:

``` python
results.sort(
    key=lambda item: item["sequence"]
)
```

This works when the result set can be safely buffered.

For large streams, other strategies include:

-   ordered consumers;
-   partitioning by key;
-   sequence-aware downstream writes;
-   reorder buffers.

Ordering has a cost.

------------------------------------------------------------------------

# 58. Ordering by Key

Sometimes global ordering is unnecessary.

Suppose the requirement is:

> Preserve order for each customer, but different customers may process
> concurrently.

Partitioning can provide:

``` text
Customer A -> partition 1
Customer B -> partition 2
Customer C -> partition 3
```

Then each partition can preserve local order while the system processes
independent partitions concurrently.

This is an important distributed-systems pattern, but the same reasoning
applies to in-process pipeline design.

------------------------------------------------------------------------

# 59. Shutdown Is a Design Problem

A producer-consumer pipeline must answer:

-   How does the producer know it should stop?
-   How do consumers know no more work is coming?
-   What happens to queued work?
-   What happens to in-flight work?
-   What happens to failures?
-   When can resources close?

Do not improvise shutdown after implementing the happy path.

------------------------------------------------------------------------

# 60. Sentinel / Poison-Pill Shutdown

A classic pattern is a sentinel object:

``` python
SENTINEL = object()
```

Consumers recognize it as:

``` text
No more work.
Stop.
```

Example:

``` python
def consumer(queue):
    while True:
        item = queue.get()

        try:
            if item is SENTINEL:
                return

            process(item)
        finally:
            queue.task_done()
```

For multiple consumers, you normally need one sentinel per consumer if
each consumer must independently receive a termination signal.

------------------------------------------------------------------------

# 61. Complete Threaded Sentinel Example

``` python
from queue import Queue
from threading import Thread
import time


SENTINEL = object()


def consumer(
    name: str,
    queue: Queue,
) -> None:
    while True:
        item = queue.get()

        try:
            if item is SENTINEL:
                return

            print(f"{name}: {item}")
            time.sleep(0.05)
        finally:
            queue.task_done()


queue = Queue(maxsize=10)

workers = [
    Thread(
        target=consumer,
        args=(f"worker-{i}", queue),
    )
    for i in range(3)
]

for worker in workers:
    worker.start()

for value in range(20):
    queue.put(value)

for _ in workers:
    queue.put(SENTINEL)

queue.join()

for worker in workers:
    worker.join()
```

The ordering is important:

``` text
produce all work
    |
    v
enqueue sentinels
    |
    v
queue.join()
    |
    v
workers exit
    |
    v
join worker threads
```

The exact lifecycle can vary depending on application requirements.

------------------------------------------------------------------------

# 62. Why One Sentinel Can Be Insufficient

Suppose:

``` text
3 consumers
1 sentinel
```

One worker receives the sentinel and exits.

The other two workers continue waiting for work.

Therefore, a simple pattern is:

``` python
for _ in range(worker_count):
    queue.put(SENTINEL)
```

This is not the only shutdown design, but it is a clear educational
pattern.

------------------------------------------------------------------------

# 63. Python 3.13+ Queue Shutdown

Python 3.13 introduced explicit queue shutdown APIs for `queue.Queue`.

Version requirement:

``` text
Python 3.13+
```

The conceptual API is:

``` python
queue.shutdown()
```

and queue operations can raise:

``` text
queue.ShutDown
```

when the queue has been shut down according to the API's semantics.

The modern API gives the queue itself a shutdown state rather than
requiring application-defined sentinel objects.

Conceptually:

``` text
Queue open
   |
   v
shutdown()
   |
   v
No more producer puts
   |
   v
Consumers drain / terminate according to shutdown mode
```

Python 3.13 also supports immediate shutdown behavior through:

``` python
queue.shutdown(immediate=True)
```

The important distinction is:

### Sentinel shutdown

Application-level protocol:

``` text
special item = stop
```

### Queue shutdown

Queue-level lifecycle:

``` text
queue itself enters shutdown state
```

For new Python 3.13+ code, the built-in shutdown mechanism can make
queue lifecycle explicit. Sentinel patterns remain useful when
compatibility with older Python versions or custom protocols matters.

Always verify the exact Python version in production before relying on
3.13+ APIs.

------------------------------------------------------------------------

# 64. Graceful Shutdown

A graceful pipeline shutdown typically looks like:

``` text
Stop producer
    |
    v
Signal no more work
    |
    v
Allow queued work to drain
    |
    v
Consumers finish
    |
    v
queue.join()
    |
    v
Close resources
    |
    v
Exit
```

The central distinction is:

``` text
graceful
= finish accepted work safely
```

versus:

``` text
immediate
= stop as quickly as possible
```

The correct choice depends on data-loss and consistency requirements.

------------------------------------------------------------------------

# 65. Queue Cancellation Context

Async pipelines introduce cancellation.

Consider:

``` text
Producer
   |
Queue
   |
Consumers
```

If the producer is cancelled:

``` text
producer stops
```

but the queue may still contain work.

If a consumer is cancelled:

``` text
in-flight item
```

may need explicit recovery semantics.

Therefore, cancellation and queue accounting must be considered
together.

This chapter does not repeat the deep cancellation and timeout material
from the preceding asyncio lesson. The queue-specific concern is:

> Cancellation must not leave the pipeline's ownership and accounting
> state ambiguous.

------------------------------------------------------------------------

# 66. Async + Process Workers

A powerful Data Engineering architecture can combine:

``` text
Async I/O
    +
Process CPU execution
```

For example:

``` text
Async API Producer
        |
        v
 asyncio.Queue
        |
        v
CPU-heavy transformation
        |
        v
Process workers
        |
        v
async loader
        |
        v
PostgreSQL / Object Storage
```

Why?

-   API extraction is network-bound.
-   Transformation may be CPU-heavy.
-   Loading may be network/database-bound.

Different stages can use different execution models.

------------------------------------------------------------------------

# 67. Serialization Cost Across Processes

Moving:

``` python
large_python_object
```

through a process queue is not free.

Conceptually:

``` text
Process A
   |
serialize
   |
IPC
   |
deserialize
   |
Process B
```

Costs can include:

-   serialization;
-   copying;
-   memory;
-   IPC;
-   deserialization.

Therefore, process workers are appropriate only when their CPU benefits
outweigh communication costs.

For very large records, consider whether the queue should carry:

``` text
full object
```

or:

``` text
small reference / identifier
```

and let workers retrieve data from shared durable storage.

------------------------------------------------------------------------

# 68. Complete Multi-Stage Async ETL Example

The following is an educational, runnable pipeline demonstrating:

-   bounded queues;
-   extraction;
-   parsing;
-   transformation;
-   batching;
-   loading;
-   multiple workers;
-   queue accounting;
-   error accounting;
-   dead-letter records;
-   explicit shutdown.

``` python
from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RawRecord:
    sequence: int
    payload: str


@dataclass(frozen=True)
class ParsedRecord:
    sequence: int
    value: int


@dataclass(frozen=True)
class TransformedRecord:
    sequence: int
    value: int
    worker: str


@dataclass(frozen=True)
class DeadLetter:
    sequence: int
    stage: str
    error: str


SENTINEL = object()


async def extract(
    output: asyncio.Queue,
    count: int,
) -> None:
    for sequence in range(count):
        await asyncio.sleep(0.001)

        record = RawRecord(
            sequence=sequence,
            payload=str(sequence),
        )

        await output.put(record)


async def parse_worker(
    name: str,
    input_queue: asyncio.Queue,
    output_queue: asyncio.Queue,
) -> None:
    while True:
        item = await input_queue.get()

        try:
            if item is SENTINEL:
                return

            assert isinstance(item, RawRecord)

            parsed = ParsedRecord(
                sequence=item.sequence,
                value=int(item.payload),
            )

            await output_queue.put(parsed)
        except Exception:
            raise
        finally:
            input_queue.task_done()


async def transform_worker(
    name: str,
    input_queue: asyncio.Queue,
    output_queue: asyncio.Queue,
    dead_letters: list[DeadLetter],
) -> None:
    while True:
        item = await input_queue.get()

        try:
            if item is SENTINEL:
                return

            assert isinstance(item, ParsedRecord)

            # Simulated CPU-ish work.
            await asyncio.sleep(0.002)

            # Deterministic injected failures for demonstration.
            if item.sequence % 97 == 0:
                dead_letters.append(
                    DeadLetter(
                        sequence=item.sequence,
                        stage="transform",
                        error="simulated transformation failure",
                    )
                )
                continue

            transformed = TransformedRecord(
                sequence=item.sequence,
                value=item.value * item.value,
                worker=name,
            )

            await output_queue.put(transformed)
        finally:
            input_queue.task_done()


async def batch_loader(
    input_queue: asyncio.Queue,
    batch_size: int,
    loaded: list[TransformedRecord],
) -> None:
    batch: list[TransformedRecord] = []

    while True:
        item = await input_queue.get()

        try:
            if item is SENTINEL:
                if batch:
                    loaded.extend(batch)
                    batch.clear()
                return

            assert isinstance(item, TransformedRecord)

            batch.append(item)

            if len(batch) >= batch_size:
                # Simulate bulk database/object-store write.
                await asyncio.sleep(0.005)
                loaded.extend(batch)
                batch.clear()
        finally:
            input_queue.task_done()


async def run_pipeline() -> tuple[
    list[TransformedRecord],
    list[DeadLetter],
]:
    raw_queue = asyncio.Queue(maxsize=100)
    parsed_queue = asyncio.Queue(maxsize=100)
    transformed_queue = asyncio.Queue(maxsize=100)

    dead_letters: list[DeadLetter] = []
    loaded: list[TransformedRecord] = []

    parse_workers = [
        asyncio.create_task(
            parse_worker(
                f"parser-{i}",
                raw_queue,
                parsed_queue,
            )
        )
        for i in range(2)
    ]

    transform_workers = [
        asyncio.create_task(
            transform_worker(
                f"transformer-{i}",
                parsed_queue,
                transformed_queue,
                dead_letters,
            )
        )
        for i in range(4)
    ]

    loader_task = asyncio.create_task(
        batch_loader(
            transformed_queue,
            batch_size=20,
            loaded=loaded,
        )
    )

    await extract(raw_queue, count=100)

    for _ in parse_workers:
        await raw_queue.put(SENTINEL)

    await raw_queue.join()

    await asyncio.gather(
        *parse_workers,
    )

    for _ in transform_workers:
        await parsed_queue.put(SENTINEL)

    await parsed_queue.join()

    await asyncio.gather(
        *transform_workers,
    )

    await transformed_queue.put(SENTINEL)

    await transformed_queue.join()
    await loader_task

    return loaded, dead_letters


async def main() -> None:
    loaded, dead_letters = await run_pipeline()

    print("loaded:", len(loaded))
    print("dead letters:", len(dead_letters))


if __name__ == "__main__":
    asyncio.run(main())
```

The implementation demonstrates a crucial lifecycle:

``` text
produce raw records
      |
      v
raw queue drains
      |
      v
parser workers stop
      |
      v
parsed queue drains
      |
      v
transform workers stop
      |
      v
transformed queue drains
      |
      v
loader flushes final batch
      |
      v
pipeline completes
```

In a production implementation, worker failures should be propagated
through a structured supervisory mechanism rather than merely allowing
an isolated task to fail.

------------------------------------------------------------------------

# 69. Pipeline Shutdown Ordering

For a multi-stage pipeline:

``` text
Extract
  |
Queue A
  |
Parse
  |
Queue B
  |
Transform
  |
Queue C
  |
Load
```

a safe graceful shutdown generally proceeds from upstream to downstream:

``` text
1. Stop new extraction
2. Let Queue A drain
3. Stop Parse workers
4. Let Queue B drain
5. Stop Transform workers
6. Let Queue C drain
7. Flush Loader
8. Close resources
```

Why?

Because a downstream stage must remain available while upstream work is
still being delivered.

Stopping loaders first can strand work in earlier stages.

------------------------------------------------------------------------

# 70. Queue Observability

A production queue pipeline should expose metrics such as:

### Queue metrics

-   current depth;
-   maximum observed depth;
-   configured capacity;
-   time near capacity;
-   enqueue wait time;
-   dequeue wait time.

### Worker metrics

-   worker count;
-   active workers;
-   idle workers;
-   processing time;
-   failures.

### Pipeline metrics

-   input records;
-   output records;
-   throughput;
-   end-to-end latency;
-   retry count;
-   dead-letter count;
-   batch size;
-   batch flush time.

------------------------------------------------------------------------

# 71. Queue Depth as a Bottleneck Detector

Suppose:

``` text
Queue A: 20
Queue B: 990 / 1000
Queue C: 5
```

This pattern suggests:

``` text
Stage B's downstream consumer is under pressure.
```

But investigate further.

Ask:

``` text
Is Queue B filling?
       |
       +--> Is downstream slow?
       |
       +--> Are downstream workers failing?
       |
       +--> Is the database throttling?
       |
       +--> Is batch loading slow?
       |
       +--> Are retries increasing?
```

Queue depth is a signal, not a diagnosis.

------------------------------------------------------------------------

# 72. Throughput

Throughput measures work completed per unit time.

For records:

``` text
throughput =
records_processed / elapsed_seconds
```

Example:

``` text
100,000 records
/
200 seconds
=
500 records/sec
```

Measure throughput per stage.

For example:

``` text
Extract:    1,500/sec
Parse:      1,200/sec
Transform:    700/sec
Load:         650/sec
```

The pipeline cannot sustainably produce 1,500 records/sec at the final
output if the downstream stages can only sustain 650/sec.

------------------------------------------------------------------------

# 73. Latency

Throughput and latency are different.

A pipeline can have high throughput but high individual-record latency.

Measure:

``` text
record enters pipeline
        |
        v
queue waits
        |
        v
processing
        |
        v
batch wait
        |
        v
load
        |
        v
record becomes durable
```

End-to-end latency includes queue waiting.

This is why queue depth matters even when CPU utilization looks
acceptable.

------------------------------------------------------------------------

# 74. Queue Wait Time

Suppose a record spends:

``` text
2 ms extraction
500 ms waiting in queue
10 ms transform
100 ms batch wait
50 ms load
```

End-to-end latency is approximately:

``` text
662 ms
```

The transformation itself is only 10 ms.

The queue is the major latency contributor.

Therefore, optimization must consider waiting, not only CPU execution
time.

------------------------------------------------------------------------

# 75. Memory Bounding

A simple approximation is:

``` text
queued memory
≈ queue_capacity × average_item_size
```

Example:

``` text
maxsize = 1000
average queued payload = 100 KB
```

Approximate payload memory:

``` text
1000 × 100 KB
= 100,000 KB
≈ 100 MB
```

But this is only an approximation.

Actual memory can include:

-   Python object overhead;
-   nested objects;
-   references;
-   copies;
-   serialization buffers;
-   worker-local batches;
-   library buffers;
-   network buffers.

Therefore:

``` text
queue memory
!= entire pipeline memory
```

------------------------------------------------------------------------

# 76. Queue Size Selection

Do not choose:

``` python
Queue(maxsize=1_000_000)
```

merely because it sounds safe.

Instead:

1.  Establish a baseline.
2.  Measure average item size.
3.  Measure producer rate.
4.  Measure consumer rate.
5.  Measure burst size.
6.  Define memory budget.
7.  Set an initial queue bound.
8.  Run realistic workload.
9.  Observe queue depth.
10. Observe memory.
11. Observe latency.
12. Adjust.

Queue size is a systems parameter.

------------------------------------------------------------------------

# 77. Queue Too Small

A queue can be too small.

For example:

``` text
producer bursts briefly
consumer is healthy
queue maxsize = 1
```

The producer may spend excessive time waiting even though the system
could safely absorb a moderate burst.

Symptoms:

-   unnecessary producer blocking;
-   reduced throughput;
-   higher queue wait;
-   poor burst absorption.

The answer is not automatically "make the queue huge."

Measure.

------------------------------------------------------------------------

# 78. Queue Too Large

A queue can also be too large.

Symptoms:

-   large memory footprint;
-   long queueing latency;
-   delayed failure visibility;
-   slow response to downstream degradation;
-   expensive shutdown/drain time.

A very large queue can hide a bottleneck.

The system may look productive because extraction continues while the
backlog quietly grows.

------------------------------------------------------------------------

# 79. When In-Process Queues Are Appropriate

In-process queues are excellent for:

-   one application;
-   one process or controlled process group;
-   local stage coordination;
-   bounded buffering;
-   worker distribution;
-   low-latency communication;
-   ephemeral pipeline execution.

They are often simple and fast.

------------------------------------------------------------------------

# 80. When In-Process Queues Are Not Enough

Consider an external messaging system when you need:

-   durable messages;
-   process-crash recovery;
-   cross-machine consumers;
-   independent services;
-   replay;
-   long-lived buffering;
-   durable retention;
-   distributed scaling.

Conceptual choices include:

-   Kafka;
-   RabbitMQ;
-   cloud queue services;
-   managed messaging systems.

This chapter does not turn those systems into a separate course.

The important architectural boundary is:

``` text
local coordination
vs
distributed durable messaging
```

------------------------------------------------------------------------

# 81. In-Process Queue vs External Message System

  Characteristic           In-process queue              External message system
  ------------------------ ----------------------------- ---------------------------------
  Durability               Low/ephemeral                 Usually designed for durability
  Process crash recovery   Limited                       Often supported
  Cross-machine            No                            Yes
  Operational complexity   Low                           Higher
  Replay                   Limited                       Often supported
  Local latency            Very low                      Network-dependent
  Ownership                Application                   Messaging infrastructure
  Best use                 Local pipeline coordination   Distributed communication

Exact guarantees depend on the technology and configuration.

Do not assume "external broker" automatically means exactly-once
processing, perfect ordering, or zero data loss.

------------------------------------------------------------------------

# 82. Common Mistakes

## Mistake 1 --- Unbounded queues everywhere

Bad:

``` python
queue = Queue()
```

when workload can grow indefinitely.

Why it fails:

``` text
producer > consumer
      |
      v
unbounded backlog
      |
      v
memory pressure
```

Correct approach:

``` python
queue = Queue(maxsize=...)
```

and choose the bound from measurements.

------------------------------------------------------------------------

## Mistake 2 --- No backpressure

Bad architecture:

``` text
API
 |
 v
append to giant list
 |
 v
slow database
```

Correct:

``` text
API
 |
 v
bounded queue
 |
 v
database workers
```

------------------------------------------------------------------------

## Mistake 3 --- Permanent producer overload

If:

``` text
producer = 1000/sec
consumer = 100/sec
```

the queue cannot solve the mismatch.

You need to address:

-   producer rate;
-   consumer capacity;
-   workload size;
-   architecture.

------------------------------------------------------------------------

## Mistake 4 --- Forgetting `task_done()`

Symptom:

``` python
queue.join()
```

never returns.

Fix:

``` python
item = queue.get()
try:
    process(item)
finally:
    queue.task_done()
```

------------------------------------------------------------------------

## Mistake 5 --- Calling `task_done()` twice

Symptom:

``` text
ValueError: task_done() called too many times
```

Fix:

Exactly one `task_done()` per successful `get()`.

------------------------------------------------------------------------

## Mistake 6 --- Incorrect `join()` expectations

`join()` tracks unfinished task accounting.

It is not a generic:

``` text
"stop everything now"
```

mechanism.

------------------------------------------------------------------------

## Mistake 7 --- No shutdown protocol

Workers can remain blocked forever waiting for work.

Define:

-   sentinel;
-   queue shutdown;
-   cancellation;
-   or another explicit protocol.

------------------------------------------------------------------------

## Mistake 8 --- One sentinel for many consumers

One sentinel usually stops only one consumer.

Use one sentinel per consumer where using this pattern.

------------------------------------------------------------------------

## Mistake 9 --- Ignoring worker exceptions

A worker can die while the producer keeps running.

Result:

``` text
fewer consumers
      |
      v
queue grows
      |
      v
latency increases
```

Failures must be observable.

------------------------------------------------------------------------

## Mistake 10 --- No dead-letter policy

Failed records silently disappear.

Correct approach:

-   retry with bounds;
-   dead-letter;
-   fail pipeline;
-   or explicit skip accounting.

------------------------------------------------------------------------

## Mistake 11 --- Excessive worker count

More workers can increase:

-   contention;
-   memory;
-   external load;
-   context switching;
-   failures.

------------------------------------------------------------------------

## Mistake 12 --- Queue too large

Large queue capacity can hide a downstream bottleneck.

------------------------------------------------------------------------

## Mistake 13 --- Queue too small

A tiny queue can prevent useful burst absorption.

------------------------------------------------------------------------

## Mistake 14 --- Ignoring item size

A queue of 10,000 tiny integers is not equivalent to a queue of 10,000
large nested records.

------------------------------------------------------------------------

## Mistake 15 --- Assuming FIFO means completion order

With multiple workers:

``` text
retrieval order != completion order
```

------------------------------------------------------------------------

## Mistake 16 --- Mixing blocking queues with asyncio

Do not use blocking `queue.Queue` as the normal coordination primitive
between asyncio tasks.

Use:

``` python
asyncio.Queue
```

------------------------------------------------------------------------

## Mistake 17 --- Sending huge objects through process queues

Serialization and copying can dominate performance.

------------------------------------------------------------------------

## Mistake 18 --- No queue-depth monitoring

A full queue is an important operational signal.

------------------------------------------------------------------------

## Mistake 19 --- Losing the final partial batch

Always flush:

``` text
remaining records
```

during normal completion.

------------------------------------------------------------------------

## Mistake 20 --- Infinite retries

Retries can amplify load:

``` text
failure
  |
retry
  |
failure
  |
retry
  |
more load
  |
more failure
```

Retries need bounds and observability.

------------------------------------------------------------------------

# 83. Debugging a Hung Queue Pipeline

When a pipeline appears hung, ask in this order:

1.  Is the producer alive?
2.  Is the queue full?
3.  Are consumers alive?
4.  Are workers blocked?
5.  Is `task_done()` missing?
6.  Is `queue.join()` waiting forever?
7.  Did a worker crash?
8.  Is downstream storage blocked?
9.  Is there a shutdown/sentinel problem?
10. Is a queue being used from the wrong concurrency model?

This converts:

``` text
"the pipeline is stuck"
```

into a structured investigation.

------------------------------------------------------------------------

# 84. Debugging Queue State

For thread queues:

``` python
print("queue depth:", queue.qsize())
print("queue full:", queue.full())
```

These are useful diagnostics.

But do not write synchronization logic such as:

``` python
if queue.qsize() < 10:
    queue.put(item)
```

and assume it is atomic.

Another thread can change the queue immediately.

Use the queue's own synchronization behavior instead.

------------------------------------------------------------------------

# 85. Debugging `queue.join()` Hanging

If:

``` python
queue.join()
```

hangs indefinitely, inspect:

### 1. Every `get()` has a `task_done()`

Search consumer code.

### 2. Worker crashed

A worker may have retrieved an item and failed before accounting for it.

Use:

``` python
try:
    ...
finally:
    queue.task_done()
```

### 3. Sentinel logic

A consumer may have exited before all required work was processed.

### 4. Producer still producing

`join()` cannot complete while new unfinished tasks continue to enter
the queue.

------------------------------------------------------------------------

# 86. Debugging Async Queue Hangs

For asyncio:

``` text
Producer waiting
    |
    v
Queue full
```

or:

``` text
Consumer waiting
    |
    v
Queue empty
```

may both be normal.

The problem is identifying whether the wait is expected.

Inspect:

-   task states;
-   queue depth;
-   worker exceptions;
-   downstream latency;
-   cancellation state;
-   shutdown state.

An async debugger or structured logging can show which stage is waiting.

------------------------------------------------------------------------

# 87. Debugging Worker Crashes

Suppose:

``` text
Producer -> Queue -> 4 workers
```

and one worker crashes.

If errors are not observed:

``` text
3 workers remain
```

and the pipeline may continue at reduced throughput.

A robust design records:

``` text
worker ID
stage
exception
record identifier
timestamp
retry count
```

This makes the failure actionable.

------------------------------------------------------------------------

# 88. Performance Measurement

Always compare:

``` text
sequential baseline
```

with:

``` text
concurrent pipeline
```

Use:

``` python
import time

start = time.perf_counter()

# pipeline

elapsed = time.perf_counter() - start
```

Measure:

-   total elapsed time;
-   throughput;
-   queue wait;
-   processing time;
-   batch load time;
-   failures;
-   output count.

------------------------------------------------------------------------

# 89. Correctness Before Speed

Suppose sequential processing produces:

``` text
10,000 records
```

and concurrent processing produces:

``` text
9,850 records
```

A speed-up is meaningless.

Compare:

-   record count;
-   keys;
-   checksums;
-   aggregate values;
-   error counts;
-   dead-letter counts.

A useful invariant is:

``` text
successful output
+
dead-lettered input
+
explicitly rejected input
=
accounted input
```

The exact equation depends on pipeline semantics, but the principle is
universal:

> Every input should have a known outcome.

------------------------------------------------------------------------

# 90. Mini Project --- Multi-Stage Concurrent ETL Pipeline

## Requirements

Build an educational pipeline with:

``` text
10,000 simulated records
        |
        v
Bounded asyncio.Queue(maxsize=1000)
        |
        v
4 transformation workers
        |
        v
Bounded queue
        |
        v
Batcher
        |
        v
Loader
```

Requirements:

-   producer generates records;
-   queue applies backpressure;
-   transformation simulates CPU work;
-   batch size = 100;
-   time-based flush = 5 seconds;
-   approximately 5% deterministic failures;
-   failures go to a dead-letter collection;
-   queue depth is periodically reported;
-   all errors are accounted for;
-   clean shutdown;
-   sequential baseline;
-   result equality check.

------------------------------------------------------------------------

# 91. Mini Project --- Complete Implementation

``` python
from __future__ import annotations

import asyncio
import hashlib
import time
from dataclasses import dataclass


TOTAL_RECORDS = 10_000
QUEUE_SIZE = 1_000
TRANSFORM_WORKERS = 4
BATCH_SIZE = 100
FLUSH_SECONDS = 5.0


@dataclass(frozen=True)
class Record:
    sequence: int
    value: int


@dataclass(frozen=True)
class Transformed:
    sequence: int
    value: int
    digest: str


@dataclass(frozen=True)
class DeadLetter:
    sequence: int
    error: str


SENTINEL = object()


def sequential_baseline(
    count: int,
) -> tuple[list[Transformed], list[DeadLetter]]:
    results: list[Transformed] = []
    dead_letters: list[DeadLetter] = []

    for sequence in range(count):
        record = Record(
            sequence=sequence,
            value=sequence,
        )

        if sequence % 20 == 0:
            dead_letters.append(
                DeadLetter(
                    sequence=sequence,
                    error="simulated transformation failure",
                )
            )
            continue

        digest = hashlib.sha256(
            str(record.value).encode()
        ).hexdigest()

        results.append(
            Transformed(
                sequence=sequence,
                value=record.value * 2,
                digest=digest,
            )
        )

    return results, dead_letters


async def producer(
    queue: asyncio.Queue,
    count: int,
) -> None:
    for sequence in range(count):
        await queue.put(
            Record(
                sequence=sequence,
                value=sequence,
            )
        )

    for _ in range(TRANSFORM_WORKERS):
        await queue.put(SENTINEL)


async def transform_worker(
    name: str,
    input_queue: asyncio.Queue,
    output_queue: asyncio.Queue,
    dead_letters: list[DeadLetter],
) -> None:
    while True:
        item = await input_queue.get()

        try:
            if item is SENTINEL:
                return

            assert isinstance(item, Record)

            # Simulated CPU-ish transformation.
            # Keep it intentionally small so this educational example
            # remains responsive.
            await asyncio.sleep(0)

            if item.sequence % 20 == 0:
                dead_letters.append(
                    DeadLetter(
                        sequence=item.sequence,
                        error="simulated transformation failure",
                    )
                )
                continue

            digest = hashlib.sha256(
                str(item.value).encode()
            ).hexdigest()

            await output_queue.put(
                Transformed(
                    sequence=item.sequence,
                    value=item.value * 2,
                    digest=digest,
                )
            )
        finally:
            input_queue.task_done()


async def loader(
    queue: asyncio.Queue,
    loaded: list[Transformed],
) -> None:
    batch: list[Transformed] = []
    deadline = asyncio.get_running_loop().time() + FLUSH_SECONDS

    while True:
        remaining = (
            deadline
            - asyncio.get_running_loop().time()
        )

        if remaining <= 0 and batch:
            loaded.extend(batch)
            batch.clear()
            deadline = (
                asyncio.get_running_loop().time()
                + FLUSH_SECONDS
            )

        try:
            item = await asyncio.wait_for(
                queue.get(),
                timeout=max(remaining, 0.001),
            )
        except asyncio.TimeoutError:
            continue

        try:
            if item is SENTINEL:
                if batch:
                    loaded.extend(batch)
                    batch.clear()
                return

            assert isinstance(item, Transformed)

            batch.append(item)

            if len(batch) >= BATCH_SIZE:
                loaded.extend(batch)
                batch.clear()

                deadline = (
                    asyncio.get_running_loop().time()
                    + FLUSH_SECONDS
                )
        finally:
            queue.task_done()


async def queue_monitor(
    queues: list[tuple[str, asyncio.Queue]],
    stop_event: asyncio.Event,
) -> None:
    while not stop_event.is_set():
        metrics = ", ".join(
            f"{name}={queue.qsize()}"
            for name, queue in queues
        )

        print(
            f"[queue-depth] {metrics}"
        )

        try:
            await asyncio.wait_for(
                stop_event.wait(),
                timeout=1.0,
            )
        except asyncio.TimeoutError:
            pass


async def run_pipeline(
    count: int,
) -> tuple[list[Transformed], list[DeadLetter]]:
    input_queue = asyncio.Queue(
        maxsize=QUEUE_SIZE
    )

    output_queue = asyncio.Queue(
        maxsize=QUEUE_SIZE
    )

    dead_letters: list[DeadLetter] = []
    loaded: list[Transformed] = []

    monitor_stop = asyncio.Event()

    monitor_task = asyncio.create_task(
        queue_monitor(
            [
                ("input", input_queue),
                ("output", output_queue),
            ],
            monitor_stop,
        )
    )

    workers = [
        asyncio.create_task(
            transform_worker(
                f"transform-{i}",
                input_queue,
                output_queue,
                dead_letters,
            )
        )
        for i in range(TRANSFORM_WORKERS)
    ]

    loader_task = asyncio.create_task(
        loader(
            output_queue,
            loaded,
        )
    )

    try:
        await producer(
            input_queue,
            count,
        )

        await input_queue.join()

        await asyncio.gather(*workers)

        await output_queue.join()

        await output_queue.put(SENTINEL)

        await loader_task

    finally:
        monitor_stop.set()
        await monitor_task

    loaded.sort(key=lambda row: row.sequence)
    dead_letters.sort(key=lambda row: row.sequence)

    return loaded, dead_letters


async def main() -> None:
    baseline_start = time.perf_counter()

    baseline_results, baseline_dead = (
        sequential_baseline(TOTAL_RECORDS)
    )

    baseline_elapsed = (
        time.perf_counter() - baseline_start
    )

    concurrent_start = time.perf_counter()

    results, dead_letters = await run_pipeline(
        TOTAL_RECORDS
    )

    concurrent_elapsed = (
        time.perf_counter() - concurrent_start
    )

    assert results == baseline_results
    assert dead_letters == baseline_dead

    print()
    print("=== Results ===")
    print("input:", TOTAL_RECORDS)
    print("successful:", len(results))
    print("dead letters:", len(dead_letters))
    print(
        "baseline seconds:",
        round(baseline_elapsed, 4),
    )
    print(
        "concurrent seconds:",
        round(concurrent_elapsed, 4),
    )

    if concurrent_elapsed > 0:
        print(
            "speed-up:",
            round(
                baseline_elapsed
                / concurrent_elapsed,
                2,
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
```

### What this project demonstrates

``` text
bounded input queue
        |
        v
4 transformation workers
        |
        v
bounded output queue
        |
        v
batching loader
```

It also demonstrates:

-   explicit accounting;
-   dead-letter handling;
-   queue monitoring;
-   final batch flushing;
-   sequential correctness baseline.

The transformation stage is intentionally educational. A true CPU-heavy
implementation should use an appropriate process/native execution
boundary rather than pretending that `asyncio.sleep(0)` creates CPU
parallelism.

------------------------------------------------------------------------

# 92. Mini Project Extension --- Async + Process Workers

For a genuinely CPU-heavy transformation:

``` text
Async API extraction
        |
        v
asyncio.Queue
        |
        v
Process workers
        |
        v
asyncio.Queue
        |
        v
Async loader
        |
        v
PostgreSQL / Object Storage
```

Reasoning:

``` text
API I/O
  -> asyncio

CPU-heavy work
  -> processes

Database/network loading
  -> asyncio
```

But remember:

``` text
process queue
+
serialization
+
copying
```

has a cost.

The process architecture should be benchmarked against alternatives.

------------------------------------------------------------------------

# 93. Practical Coding Exercises

## Basic 1 --- FIFO Queue

### Objective

Demonstrate FIFO behavior.

### Requirements

-   enqueue five values;
-   dequeue all five;
-   verify original order.

### Constraints

Use `queue.Queue`.

### Expected behavior

Output:

``` text
1
2
3
4
5
```

### Hint

Use `put()` followed by `get()`.

------------------------------------------------------------------------

## Basic 2 --- Simple Producer-Consumer

### Objective

Separate production and consumption.

### Requirements

-   one producer;
-   one consumer;
-   ten records;
-   use `task_done()`.

### Expected behavior

All ten records are processed.

### Hint

Call `queue.join()` after production.

------------------------------------------------------------------------

## Basic 3 --- `task_done()` / `join()`

### Objective

Understand task accounting.

### Requirements

-   enqueue 20 records;
-   process them;
-   wait using `queue.join()`.

### Hint

Use `finally`.

------------------------------------------------------------------------

## Basic 4 --- Bounded Queue

### Objective

Observe blocking.

### Requirements

-   `maxsize=2`;
-   producer inserts five items;
-   consumer processes slowly.

### Expected behavior

Producer periodically waits for capacity.

### Hint

Add logging around `put()`.

------------------------------------------------------------------------

## Basic 5 --- Multiple Consumers

### Objective

Build a worker pool.

### Requirements

-   one producer;
-   four consumers;
-   100 items.

### Expected behavior

Workers share the workload.

------------------------------------------------------------------------

## Moderate 6 --- Multiple Producers

### Objective

Coordinate independent sources.

### Requirements

-   three producers;
-   one shared bounded queue;
-   three consumers.

### Expected behavior

All produced records are processed exactly once.

------------------------------------------------------------------------

## Moderate 7 --- `asyncio.Queue`

### Objective

Replace blocking coordination with async coordination.

### Requirements

-   async producer;
-   async consumer;
-   bounded queue.

### Expected behavior

No blocking `queue.Queue` calls inside async tasks.

------------------------------------------------------------------------

## Moderate 8 --- Bounded Async Pipeline

### Objective

Demonstrate async backpressure.

### Requirements

-   producer faster than consumers;
-   small queue;
-   log queue depth.

### Expected behavior

Producer waits when queue is full.

------------------------------------------------------------------------

## Moderate 9 --- Sentinel Shutdown

### Objective

Stop multiple workers cleanly.

### Requirements

-   four consumers;
-   one sentinel per consumer.

### Expected behavior

All workers terminate after all work drains.

------------------------------------------------------------------------

## Moderate 10 --- Batching

### Objective

Batch records before loading.

### Requirements

-   batch size 100;
-   final partial batch flushed.

### Expected behavior

No record is lost.

------------------------------------------------------------------------

## Hard 11 --- Multi-Stage Pipeline

### Objective

Build:

``` text
Extract -> Parse -> Transform -> Load
```

with a queue between stages.

### Expected behavior

Each stage can have independent worker counts.

------------------------------------------------------------------------

## Hard 12 --- Backpressure Experiment

### Objective

Measure queue growth.

### Requirements

Run:

``` text
producer = 1000/sec
consumer = 100/sec
```

first with an effectively unbounded queue, then with a bounded queue.

### Expected behavior

The bounded version stops unlimited queue growth.

------------------------------------------------------------------------

## Hard 13 --- Dead-Letter Handling

### Objective

Account for failed records.

### Requirements

-   inject failures;
-   preserve record ID;
-   preserve exception information;
-   verify successful + dead-lettered = input where appropriate.

------------------------------------------------------------------------

## Hard 14 --- Ordering With Sequence Numbers

### Objective

Preserve logical order despite concurrent processing.

### Requirements

-   attach sequence numbers;
-   process concurrently;
-   reorder results.

### Expected behavior

Final output is ordered by sequence.

------------------------------------------------------------------------

## Advanced 15 --- Async + Process Worker Pipeline

### Objective

Separate I/O and CPU execution models.

### Requirements

-   async producer;
-   process-based transformation;
-   async loading;
-   bounded queues.

### Expected behavior

The design explains serialization and capacity costs.

------------------------------------------------------------------------

# 94. Coding Exercise Solutions

## Solution 1

``` python
from queue import Queue

queue = Queue()

for value in range(1, 6):
    queue.put(value)

for _ in range(5):
    print(queue.get())
    queue.task_done()

queue.join()
```

## Solution 2

``` python
from queue import Queue
from threading import Thread


def producer(queue):
    for value in range(10):
        queue.put(value)


def consumer(queue):
    for _ in range(10):
        item = queue.get()

        try:
            print(item)
        finally:
            queue.task_done()


queue = Queue()

producer_thread = Thread(
    target=producer,
    args=(queue,),
)

consumer_thread = Thread(
    target=consumer,
    args=(queue,),
)

producer_thread.start()
consumer_thread.start()

producer_thread.join()
queue.join()
consumer_thread.join()
```

## Solution 3

``` python
from queue import Queue

queue = Queue()

for value in range(20):
    queue.put(value)

while not queue.empty():
    item = queue.get()

    try:
        process(item)
    finally:
        queue.task_done()

queue.join()
```

In production, do not use `empty()` as a synchronization primitive. A
worker loop should normally block on `get()` or use an explicit shutdown
protocol.

## Solution 4

Use:

``` python
queue = Queue(maxsize=2)
```

and log before and after:

``` python
queue.put(item)
```

The producer's elapsed time will increase when the queue is full.

## Solution 5

Create multiple consumer threads sharing the same queue. The queue
distributes work among them.

## Solution 6

All producers call:

``` python
queue.put(...)
```

on the same bounded queue. Consumers retrieve whichever work becomes
available.

## Solution 7

``` python
queue = asyncio.Queue(maxsize=100)

await queue.put(item)
item = await queue.get()
queue.task_done()
```

## Solution 8

Make producer faster than consumer and set a small `maxsize`. Log
timestamps around `await queue.put()`.

## Solution 9

``` python
for _ in consumers:
    await queue.put(SENTINEL)
```

Each consumer exits after receiving its sentinel.

## Solution 10

Accumulate records until:

``` python
len(batch) >= 100
```

then flush, and flush the remaining partial batch during shutdown.

## Solution 11

Use:

``` text
extract_queue
parse_queue
transform_queue
```

with workers dedicated to each stage.

## Solution 12

Measure:

``` python
queue.qsize()
```

over time and compare bounded versus unbounded behavior.

## Solution 13

Capture:

``` python
{
    "record_id": ...,
    "error": ...,
}
```

in a dead-letter collection and assert accounting invariants.

## Solution 14

Attach:

``` python
{"sequence": i, ...}
```

then sort completed results by `sequence`.

## Solution 15

Use an async I/O stage, an explicit process execution boundary for CPU
work, and bounded communication between them. Benchmark serialization
overhead before adopting the design.

------------------------------------------------------------------------

# 95. Debugging Exercises

## Debugging 1 --- Forgotten `task_done()`

### Broken code

``` python
from queue import Queue


queue = Queue()

queue.put("A")

item = queue.get()
print(item)

queue.join()
```

### Expected behavior

The program should finish.

### Symptom

`queue.join()` never returns.

### Learner task

Identify the missing accounting call.

### Hint

Every successful `get()` needs one `task_done()`.

------------------------------------------------------------------------

## Debugging 2 --- Double `task_done()`

### Broken code

``` python
from queue import Queue


queue = Queue()

queue.put("A")

item = queue.get()

queue.task_done()
queue.task_done()
```

### Expected behavior

No exception.

### Symptom

`ValueError`.

### Hint

One successful `get()` corresponds to exactly one completion.

------------------------------------------------------------------------

## Debugging 3 --- One Sentinel, Three Workers

### Broken code

``` python
SENTINEL = object()

for _ in range(3):
    start_worker()

queue.put(SENTINEL)
```

### Expected behavior

All workers stop.

### Symptom

Only one worker stops.

### Hint

Each consumer needs a termination signal under this simple protocol.

------------------------------------------------------------------------

## Debugging 4 --- Async Blocking Queue

### Broken code

``` python
async def producer(queue):
    queue.put("record")
```

where `queue` is a bounded `queue.Queue`.

### Expected behavior

Async tasks remain responsive.

### Symptom

The event loop can block when the queue is full.

### Hint

Use `asyncio.Queue`.

------------------------------------------------------------------------

## Debugging 5 --- Producer Never Stops

### Broken code

``` python
while True:
    queue.put(make_record())
```

### Expected behavior

Pipeline eventually shuts down.

### Symptom

Queue never drains during shutdown.

### Hint

The producer must have an explicit stop condition.

------------------------------------------------------------------------

## Debugging 6 --- Worker Crash

### Broken code

``` python
def worker(queue):
    while True:
        item = queue.get()
        process(item)
        queue.task_done()
```

`process()` can raise.

### Expected behavior

The queue remains correctly accounted for.

### Symptom

`queue.join()` can hang after a failure.

### Hint

Use `try/finally` around processing.

------------------------------------------------------------------------

## Debugging 7 --- Batch Lost at Shutdown

### Broken code

``` python
if len(batch) >= 100:
    load(batch)
    batch.clear()

# function returns here
```

### Expected behavior

Every record is loaded.

### Symptom

The final partial batch disappears.

### Hint

Flush `batch` during normal shutdown.

------------------------------------------------------------------------

## Debugging 8 --- Wrong Completion Assumption

### Broken code

``` python
# Worker results are appended as workers finish.
results.append(result)
```

### Expected behavior

Results preserve input order.

### Symptom

Results appear shuffled.

### Hint

Completion order is not queue order. Add sequence numbers.

------------------------------------------------------------------------

## Debugging 9 --- Queue `join()` Shutdown Race

### Broken code

``` python
queue.join()

for _ in workers:
    queue.put(SENTINEL)
```

### Expected behavior

Workers stop after all work completes.

### Symptom

`join()` can return before workers receive their shutdown signals, and
the lifecycle becomes ambiguous.

### Hint

Separate "work drained" from "workers terminated." Define the shutdown
protocol explicitly.

------------------------------------------------------------------------

## Debugging 10 --- Infinite Retry

### Broken code

``` python
while True:
    try:
        process(item)
        break
    except Exception:
        continue
```

### Expected behavior

Transient failures are retried safely.

### Symptom

A permanently bad record consumes a worker forever.

### Hint

Bound retries and define a dead-letter/failure policy.

------------------------------------------------------------------------

# 96. Debugging Answer Key

### 1

Add:

``` python
queue.task_done()
```

in a `finally` block.

### 2

Call `task_done()` exactly once.

### 3

Send one sentinel per consumer.

### 4

Use:

``` python
asyncio.Queue
```

with:

``` python
await queue.put(...)
```

### 5

Add a stop condition or cancellation/shutdown protocol.

### 6

Use:

``` python
try:
    process(item)
finally:
    queue.task_done()
```

Then decide how the exception is propagated.

### 7

Flush the final partial batch.

### 8

Attach a sequence number and reorder results if ordering is required.

### 9

Design shutdown in stages:

``` text
stop producer
drain work
terminate workers
close resources
```

### 10

Use bounded retry counts, backoff where appropriate, and a dead-letter
path for persistent failures.

------------------------------------------------------------------------

# 97. Interview Questions --- Basic

## 1. What problem does a queue solve?

It decouples producers and consumers, provides buffering, coordinates
work, and can create backpressure when bounded.

## 2. What is FIFO?

First In, First Out.

## 3. What is a producer?

A component that creates work items.

## 4. What is a consumer?

A component that retrieves and processes work items.

## 5. What is buffering?

Temporarily holding work so short-term production and consumption rates
can differ.

## 6. What is backpressure?

A mechanism by which downstream capacity constraints cause upstream
production to slow.

## 7. What is `maxsize`?

The configured capacity bound for queued items.

## 8. What does `task_done()` do?

It marks one previously retrieved queue item as fully processed.

## 9. What does `join()` do?

It waits until the queue's unfinished-task count reaches zero.

## 10. Why use multiple consumers?

To increase throughput when the consumer stage can safely process work
concurrently.

------------------------------------------------------------------------

# 98. Interview Questions --- Moderate

## 1. Why is a bounded queue safer than an unbounded queue?

It prevents unlimited pending work from consuming unbounded memory and
creates backpressure.

## 2. Difference between buffering and backpressure?

Buffering absorbs temporary mismatch. Backpressure controls upstream
production when downstream capacity is insufficient.

## 3. Why can `queue.join()` hang?

Usually because unfinished task accounting is incorrect, such as missing
`task_done()`, a producer that never stops, or broken shutdown logic.

## 4. Why use `asyncio.Queue` for async tasks?

Its waiting semantics cooperate with the event loop.

## 5. Why use `multiprocessing.Queue`?

To communicate work between processes.

## 6. Does FIFO guarantee completion order?

No. Multiple consumers can complete work in any order.

## 7. How can order be preserved?

Sequence numbers, partitioning, ordered consumers, or reorder buffers.

## 8. Why are queues useful in ETL?

They isolate stages, buffer bursts, distribute work, and propagate
capacity pressure.

## 9. What is a dead-letter destination?

A place where failed records are retained for investigation or recovery.

## 10. What should determine queue size?

Memory budget, item size, burst behavior, throughput, latency, and
downstream capacity.

------------------------------------------------------------------------

# 99. Interview Questions --- Hard

## 1. What happens if the producer permanently outpaces the consumer?

An unbounded queue grows indefinitely. A bounded queue fills and
eventually applies backpressure.

## 2. Why can increasing consumers make a pipeline slower?

They may overload the database/API, increase contention, increase
memory, or exceed useful CPU capacity.

## 3. How do you detect a consumer bottleneck?

Queue depth rises toward capacity while producer throughput remains high
and downstream processing capacity is insufficient.

## 4. How does backpressure propagate through multiple queues?

A downstream queue fills, causing its producer stage to block; that
stage stops draining its upstream queue, which then fills and slows its
producer.

## 5. Why can a queue hide a bottleneck?

It buffers work, allowing the producer to appear healthy while backlog
and latency quietly grow.

## 6. Why can process queues be expensive?

Items must cross process boundaries, introducing serialization and IPC
overhead.

## 7. Why is batching important for database loading?

It amortizes network, transaction, and per-operation overhead.

## 8. How do you handle worker failure?

Observe the exception, define whether to fail, retry, dead-letter, or
skip, and preserve input accounting.

## 9. Why should queue depth be monitored?

It provides an early signal of stage imbalance and saturation.

## 10. When is an in-process queue inappropriate?

When work must survive process crashes, cross machine boundaries,
support durable replay, or provide independent service communication.

------------------------------------------------------------------------

# 100. Interview Questions --- Advanced

## 1. An API produces 5,000 records/sec but the database safely loads only 1,000. Design the pipeline.

Use a bounded queue between extraction and loading. Let the queue absorb
temporary bursts, but allow it to fill and apply backpressure. Do not
claim the queue solves the sustained throughput mismatch. Investigate
whether database loading can be optimized or parallelized within safe
limits, and define durable checkpointing/recovery if the workload
requires it.

## 2. A transformation stage is CPU-heavy while extraction is network-bound. Which execution model belongs to each?

Use asynchronous I/O for extraction if the client and workload support
it. Use processes or another suitable CPU execution engine for genuinely
CPU-heavy work. Communicate through bounded queues and measure
serialization overhead.

## 3. Queue B is constantly at 95--100% capacity. What does that indicate?

It strongly suggests the downstream stage of Queue B is unable to
consume work at the rate the upstream stage produces it. Confirm with
consumer throughput, worker utilization, downstream latency, errors, and
retries.

## 4. Memory keeps increasing even though every queue is bounded. What do you inspect?

Queue capacity is only one memory source. Inspect worker-local batches,
large objects, caches, retries, serialization buffers, HTTP/database
buffers, dead-letter accumulation, and object retention.

## 5. Pipeline hangs during shutdown. How do you debug it?

Determine which stage is still producing, which queues contain work,
which workers are alive, whether sentinels reached all consumers,
whether `task_done()` accounting is complete, and whether downstream
resources are blocking.

## 6. A worker fails silently. What should the architecture do?

Make task/worker failure observable, record the stage and record
identifier, propagate failure to the supervisor, and execute the defined
retry/dead-letter/fail-pipeline policy.

## 7. How do you choose queue size?

Start with memory and latency constraints, measure item size and rates,
run realistic bursts, observe queue depth and saturation, then tune
empirically.

## 8. What is the difference between queue order and processing order?

Queue order defines which item becomes available next. Processing order
depends on concurrent workers and their execution durations.

## 9. When would you replace an in-process queue with Kafka or another broker?

When durability, replay, cross-machine communication, independent
service lifecycles, long-lived buffering, or distributed scaling becomes
a requirement.

## 10. Explain the queue as a systems primitive.

A queue is a coordination boundary that decouples production from
consumption, provides controlled buffering, distributes work, and---when
bounded---turns downstream capacity pressure into upstream backpressure.
It does not create capacity. The sustained throughput of the pipeline
remains constrained by its bottleneck stage.

------------------------------------------------------------------------

# 101. Architecture Scenario 1 --- API Faster Than Database

### Scenario

An API can produce:

``` text
5,000 records/sec
```

The database safely ingests:

``` text
1,000 records/sec
```

### Design

``` text
API
 |
 v
Async extraction
 |
 v
Bounded Queue
 |
 v
Batcher
 |
 v
Database loader
```

The queue must be bounded.

Expected behavior:

``` text
API bursts
   |
   v
queue fills
   |
   v
producer slows
```

Do not simply increase queue size indefinitely.

------------------------------------------------------------------------

# 102. Architecture Scenario 2 --- CPU Transformation

### Scenario

Extraction is network-bound, transformation is CPU-heavy.

### Design

``` text
Async API Producer
       |
       v
Bounded Queue
       |
       v
Process Workers
       |
       v
Bounded Queue
       |
       v
Async Loader
```

The architectural reasoning is more important than the exact
implementation.

------------------------------------------------------------------------

# 103. Architecture Scenario 3 --- Queue at 100%

### Scenario

A queue stays at:

``` text
95–100%
```

### Interpretation

Likely downstream saturation.

### Investigation

Check:

-   consumer throughput;
-   worker failures;
-   database latency;
-   API/storage limits;
-   retries;
-   CPU utilization;
-   batch sizes.

Do not immediately add workers.

------------------------------------------------------------------------

# 104. Architecture Scenario 4 --- Memory Growth

### Scenario

All queues are bounded but memory keeps growing.

### Investigation

``` text
Queue memory
+
worker-local objects
+
batch buffers
+
dead-letter collection
+
retry buffers
+
serialization buffers
+
library caches
```

The queue is not necessarily the source of the leak.

------------------------------------------------------------------------

# 105. Architecture Scenario 5 --- Shutdown Hang

### Scenario

Pipeline processes correctly but hangs during shutdown.

### Investigation

``` text
Is producer stopped?
      |
      v
Are all queued items drained?
      |
      v
Did every get receive task_done?
      |
      v
Did every worker receive shutdown?
      |
      v
Did final batch flush?
      |
      v
Are resources closed?
```

This is a lifecycle problem, not necessarily a throughput problem.

------------------------------------------------------------------------

# 106. Architecture Scenario 6 --- Silent Worker Failure

### Scenario

A worker crashes and queue depth increases.

### Design response

Worker supervision should detect:

``` text
worker exited unexpectedly
```

and then decide:

``` text
fail pipeline
or
restart worker
or
retry work
or
dead-letter
```

The correct choice depends on reliability requirements.

------------------------------------------------------------------------

# 107. Queue Design Decision Framework

Before adding a queue, ask:

1.  What produces the work?
2.  What consumes it?
3.  Can production and consumption overlap?
4.  What is the producer rate?
5.  What is consumer capacity?
6.  Can downstream capacity change?
7.  How much memory can the queue consume?
8.  Does ordering matter?
9.  What happens when processing fails?
10. How are failed records recovered?
11. How does shutdown work?
12. Does the queue need durability?
13. Must work survive process crashes?
14. Do multiple machines need access?
15. Is an in-process queue sufficient?
16. Would an external messaging system be more appropriate?

This decision framework prevents the common mistake of selecting a queue
merely because one is available.

------------------------------------------------------------------------

# 108. Production Design Checklist

## Correctness

-   [ ] Every input has a known outcome.
-   [ ] No silent data loss.
-   [ ] Duplicate behavior is understood.
-   [ ] Ordering requirements are explicit.
-   [ ] Batch boundaries are correct.
-   [ ] Final partial batches are flushed.

## Capacity

-   [ ] Queue bounds are defined.
-   [ ] Worker counts are defined from measurements.
-   [ ] Memory budget is understood.
-   [ ] API limits are understood.
-   [ ] Database pool capacity is understood.
-   [ ] Storage capacity is understood.

## Reliability

-   [ ] Worker errors are observable.
-   [ ] Retry policy is bounded.
-   [ ] Dead-letter policy is defined.
-   [ ] Failed records are accounted for.
-   [ ] Recovery behavior is documented.

## Shutdown

-   [ ] Producer can stop.
-   [ ] No new work is admitted after shutdown begins.
-   [ ] Queued work is handled according to policy.
-   [ ] Consumers terminate cleanly.
-   [ ] Final batches are flushed.
-   [ ] Resources are closed.

## Observability

-   [ ] Queue depth is measured.
-   [ ] Maximum queue depth is measured.
-   [ ] Throughput is measured.
-   [ ] Latency is measured.
-   [ ] Processing duration is measured.
-   [ ] Errors are counted.
-   [ ] Retries are counted.
-   [ ] Dead letters are counted.
-   [ ] Batch sizes are measured.

## Performance

-   [ ] Sequential baseline exists.
-   [ ] Concurrent result correctness is verified.
-   [ ] Worker counts are benchmarked.
-   [ ] Queue sizes are benchmarked.
-   [ ] Batch sizes are benchmarked.
-   [ ] External limits are respected.

## Architecture

-   [ ] Execution model matches workload.
-   [ ] CPU work does not block async event loops.
-   [ ] Process serialization cost is understood.
-   [ ] In-process versus external messaging decision is explicit.

------------------------------------------------------------------------

# 109. Final Mental Model

Start simple:

``` text
Producer
   |
   v
Bounded Queue
   |
   v
Consumer
```

Then scale the architecture:

``` text
Producer
   |
   v
Queue A
   |
   v
Parse Workers
   |
   v
Queue B
   |
   v
Transform Workers
   |
   v
Queue C
   |
   v
Batcher
   |
   v
Queue / Loader
   |
   v
Database / Object Storage
```

Queues provide:

-   **decoupling**;
-   **buffering**;
-   **synchronization**;
-   **work distribution**;
-   **controlled concurrency**;
-   **backpressure**.

Queues do not provide:

-   unlimited capacity;
-   automatic durability;
-   automatic retries;
-   automatic correctness;
-   automatic ordering;
-   automatic scaling;
-   automatic failure recovery.

The slowest sustained stage remains a fundamental constraint.

If:

``` text
Extract = 5,000/sec
Parse   = 4,000/sec
Transform = 2,000/sec
Load    = 1,000/sec
```

then the sustainable end-to-end throughput cannot exceed what the
bottleneck architecture can support.

A queue can temporarily hide the difference.

It cannot repeal the laws of throughput.

------------------------------------------------------------------------

# 110. Final Production Principles

Remember these principles:

### 1. Queue between stages when decoupling is useful.

``` text
Stage A -> Queue -> Stage B
```

### 2. Bound queues when memory and downstream capacity matter.

``` python
Queue(maxsize=...)
```

### 3. Backpressure is a feature.

A full queue tells upstream to slow down.

### 4. `task_done()` is accounting.

Every successful `get()` needs exactly one corresponding completion
signal.

### 5. `join()` waits for unfinished work.

It is not a universal shutdown primitive.

### 6. Multiple consumers change completion order.

FIFO does not mean concurrent completion order.

### 7. Batch where downstream systems benefit.

Batch size is a throughput/latency/memory trade-off.

### 8. Never silently lose failures.

Every record should have a known outcome.

### 9. Design shutdown before production.

Know how producers, consumers, queues, batches, and resources terminate.

### 10. Measure queue depth.

It is one of the most useful signals for stage imbalance.

### 11. Match execution models to workload.

``` text
I/O -> asyncio / threads
CPU -> processes / suitable compute
```

### 12. Keep process communication payloads deliberate.

Serialization has a cost.

### 13. Do not use an in-process queue when the system needs durable distributed messaging.

Choose the architecture that matches the durability and deployment
boundary.

### 14. Optimize only after measuring.

Start with:

``` text
sequential baseline
```

then prove that concurrency improves the actual workload.

------------------------------------------------------------------------

# 111. Topic Completion Standard

You are ready to move forward when you can design and explain this
architecture without relying on memorized code:

``` text
API Extraction
      |
      v
Bounded Queue
      |
      v
Parsing Workers
      |
      v
Bounded Queue
      |
      v
CPU Transformation Workers
      |
      v
Bounded Queue
      |
      v
Batcher
      |
      v
Database / Object Storage
```

You should be able to answer:

-   Why is each queue present?
-   Why is each queue bounded?
-   What happens when a downstream stage slows?
-   How does backpressure propagate?
-   Why are worker counts different?
-   What happens if a worker fails?
-   Where do failed records go?
-   Does ordering matter?
-   How is ordering preserved if necessary?
-   How are batches flushed?
-   How does the pipeline shut down?
-   How is queue depth monitored?
-   How is memory bounded?
-   How is throughput measured?
-   How is correctness verified?
-   When would you replace an in-process queue with an external
    messaging system?

The final mental model is:

``` text
Producer
    |
    v
Bounded Queue
    |
    v
Consumer
```

and, for production Data Engineering:

``` text
Extract
    |
Bounded Queue
    |
Parse
    |
Bounded Queue
    |
Transform
    |
Bounded Queue
    |
Batch
    |
Load
```

The core lesson is:

> **Queues decouple pipeline stages, absorb temporary bursts, distribute
> work, and create backpressure when bounded. They help keep memory and
> downstream concurrency under control, but they do not eliminate
> bottlenecks. A production pipeline must explicitly handle errors,
> ordering, batching, observability, and shutdown.**
