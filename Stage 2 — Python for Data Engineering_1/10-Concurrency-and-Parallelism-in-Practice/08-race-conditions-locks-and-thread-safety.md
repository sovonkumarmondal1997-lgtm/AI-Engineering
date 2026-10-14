# Race Conditions, Locks, and Thread Safety

## 1. Why This Topic Matters

Concurrency increases throughput by allowing work to overlap. It also creates a new class of correctness problems: two workers can observe, modify, or publish the same state at nearly the same time.

The central principle of this module is:

> **Concurrency is not successful merely because multiple workers run simultaneously. A concurrent program is successful only when its results are correct, shared state is safe, failures are handled, deadlocks are avoided, resources are not corrupted, required state transitions are atomic, contention is testable, and production behavior is predictable.**

A production Data Engineering system commonly has shared state even when the main workload is partitioned:

- counters
- dictionaries and caches
- authentication tokens
- output files
- checkpoint records
- watermarks
- database rows
- job leases
- partition ownership
- operational metadata

The most important engineering question is therefore not:

> "Which lock should I use?"

It is:

> **"Can I design the system so that fewer workers need to share mutable state in the first place?"**

Locks are important, but they are one tool inside a larger correctness strategy.

---

## 2. Learning Objectives

By the end of this module, you should be able to:

- explain a race condition from first principles
- reproduce a timing-dependent race
- identify read-modify-write and check-then-act races
- explain why `counter += 1` is not a correctness guarantee across threads
- use `threading.Lock` with `with`
- use `asyncio.Lock` appropriately
- design small critical sections
- understand `RLock`, `Event`, `Condition`, and `Barrier`
- identify and reproduce deadlocks
- prevent major deadlock classes through consistent lock ordering
- avoid holding locks while waiting on queues or slow I/O
- use `queue.Queue` for thread-safe communication
- reduce shared mutable state through ownership and message passing
- use immutable inputs and per-worker state
- use `contextvars` for task-local context such as run IDs
- distinguish task-local context from shared-state synchronization
- reason about races across processes
- protect shared files and use atomic replacement where appropriate
- protect watermarks and other database-backed state
- use transactions, row locks, conditional updates, and PostgreSQL advisory locks
- stress-test timing-sensitive concurrent code
- use randomized delays and `sys.setswitchinterval()` as testing aids
- understand why free-threaded Python makes synchronization correctness even more important
- design production Data Engineering workflows around explicit ownership and synchronization boundaries

---

## 3. Prerequisites

This topic follows earlier concurrency modules. You should already have encountered:

- threads
- `ThreadPoolExecutor`
- processes
- `ProcessPoolExecutor`
- `asyncio`
- tasks
- `TaskGroup`
- cancellation
- timeouts
- semaphores
- queues

Those concepts are refreshed only when necessary.

This module focuses on **correctness under concurrency**, not on re-teaching concurrency fundamentals.

---

# Beginner Level

## 4. The Core Problem: Shared Mutable State

### What is shared state?

State is information that can change over time.

Examples:

```text
counter = 10
token = "abc..."
cache = {...}
watermark = 100
output file = "part-000.parquet"
```

State becomes **shared** when more than one concurrent worker can access it.

State becomes especially dangerous when it is both:

1. shared, and
2. mutable.

For example:

```python
counter = 0
```

If sixteen threads can modify `counter`, all sixteen workers participate in the correctness story.

A useful mental model is:

```text
multiple workers
       +
same mutable state
       +
uncontrolled timing
       =
potential race condition
```

### Common shared state in Data Engineering

| Shared state | Typical workers | Potential problem |
|---|---|---|
| Counter | extraction threads | lost increments |
| Token | async API tasks | refresh stampede |
| Cache | workers | duplicate initialization |
| File | processes | conflicting writes |
| Watermark | overlapping jobs | lost update |
| Database row | job runs | conflicting transitions |
| Partition metadata | workers | duplicate ownership |
| Output path | workers | corrupted or overwritten output |

### The first design question

Before adding synchronization, ask:

> Can ownership be partitioned so that each worker owns its state?

If yes, the architecture may become substantially simpler.

---

## 5. What Is a Race Condition?

A **race condition** occurs when correctness depends on the timing or ordering of concurrent operations.

Suppose two workers update a counter.

Initial value:

```text
counter = 10
```

Worker A:

```text
read 10
add 1
write 11
```

Worker B:

```text
read 10
add 1
write 11
```

One possible interleaving is:

```text
Time →
A: READ 10
B: READ 10
A: MODIFY 10 → 11
B: MODIFY 10 → 11
A: WRITE 11
B: WRITE 11
```

Expected:

```text
12
```

Actual:

```text
11
```

The update from A and the update from B were not both reflected in the final state.

### Why this is a correctness problem

The program can:

- pass some tests
- fail under load
- fail only on certain machines
- fail only with particular timing
- produce different results across runs

That makes races especially dangerous in production.

---

## 6. Deterministic vs Nondeterministic Execution

Sequential code usually has a predictable ordering:

```text
A
↓
B
↓
C
```

Concurrent code may permit:

```text
A → B → C
```

or:

```text
B → A → C
```

or:

```text
A → C → B
```

If all interleavings are safe, concurrency is easier to reason about.

If some interleavings are unsafe, correctness becomes timing-dependent.

### Important distinction

Nondeterministic execution does **not** automatically mean incorrect execution.

A concurrent system can have nondeterministic ordering while producing deterministic correct results.

For example, if three independent partitions are processed in any order and each worker writes a distinct partition:

```text
worker 1 → partition A
worker 2 → partition B
worker 3 → partition C
```

the completion order can vary without corrupting the result.

The engineering goal is therefore not to eliminate all nondeterminism.

The goal is to ensure that **valid interleavings all preserve the required invariants**.

---

## 7. Read-Modify-Write Races

Many races have this structure:

```text
READ
  ↓
MODIFY
  ↓
WRITE
```

For example:

```python
counter = counter + 1
```

Conceptually:

```text
old = counter
new = old + 1
counter = new
```

Two workers can interleave these steps.

### Broken example

```python
counter = 0

def increment() -> None:
    global counter
    old = counter
    counter = old + 1
```

If two workers execute this concurrently:

```text
A: old = 0
B: old = 0
A: counter = 1
B: counter = 1
```

One increment is lost.

### Why the expression looks deceptively simple

Source code:

```python
counter += 1
```

is one source-level statement.

That does not mean it should be treated as one universal indivisible state transition for concurrent-program reasoning.

The operation logically needs to:

1. obtain the current value
2. calculate a new value
3. publish the new value

A race can exist whenever another worker can intervene between the logically relevant steps.

---

## 8. The `counter += 1` Problem

Do not memorize:

> "`counter += 1` is always unsafe."

The technically useful statement is:

> **Do not use the apparent simplicity of a Python expression as your synchronization strategy. If multiple threads must update shared mutable state while preserving an invariant, make the required synchronization explicit.**

The CPython GIL does not turn arbitrary multi-step shared-state logic into a transaction.

For example, this is unsafe as a design when correctness requires every increment to be preserved:

```python
counter += 1
```

The correct solution is to define the synchronization boundary:

```python
with lock:
    counter += 1
```

The lock protects the entire logical read-modify-write operation.

### Important GIL clarification

The GIL is not a correctness mechanism for application-level shared state.

It does not guarantee:

- atomicity of arbitrary application workflows
- safe coordination with external state
- safe file updates
- safe database state transitions
- safe check-then-act sequences
- absence of races in code involving blocking operations or native extensions

---

## 9. Reproducing a Race Condition with Threads

A race is timing-dependent, so a demonstration should deliberately create an opportunity for interleaving.

The following example separates the read from the write.

### Problem

We want 100 workers to increment a shared counter once.

Expected result:

```text
100
```

### Broken Code

```python
from concurrent.futures import ThreadPoolExecutor
import threading

counter = 0


def increment() -> None:
    global counter

    current = counter
    # Deliberately yield the operating system scheduler.
    threading.Event().wait(0)
    counter = current + 1


def main() -> None:
    global counter
    counter = 0

    with ThreadPoolExecutor(max_workers=20) as executor:
        list(executor.map(lambda _: increment(), range(100)))

    print("expected:", 100)
    print("actual:  ", counter)


if __name__ == "__main__":
    main()
```

This is a demonstration, not a guarantee that every machine will produce the same incorrect value.

A stronger demonstration can use a synchronization barrier to make many workers read before writes.

### What Happens

A possible execution:

```text
worker A reads 0
worker B reads 0
worker C reads 0

A writes 1
B writes 1
C writes 1
```

Many increments collapse into fewer updates.

### Why It Happens

The shared invariant is:

```text
each successful call increments the counter exactly once
```

The broken implementation does not protect the full state transition.

### Reproduction principle

A useful race test often combines:

- many workers
- repeated execution
- deliberate yield points
- assertions
- timing variation

Do not write tests that assume a race will reproduce once.

---

# Intermediate Level: Locks and Critical Sections

## 10. Fixing Races with `threading.Lock`

A `threading.Lock` provides mutual exclusion among threads using that lock.

### Basic pattern

```python
import threading

counter = 0
lock = threading.Lock()


def increment() -> None:
    global counter

    with lock:
        counter += 1
```

Only one thread at a time can execute the protected region through that lock.

### What `with lock:` means

Conceptually:

```text
acquire lock
     ↓
enter critical section
     ↓
execute protected code
     ↓
release lock
```

The context manager also ensures release when an exception leaves the block.

That is safer than manually writing:

```python
lock.acquire()
try:
    ...
finally:
    lock.release()
```

Although the manual pattern is still useful when you need unusual control over lock ownership.

### Complete corrected example

```python
from concurrent.futures import ThreadPoolExecutor
import threading

counter = 0
lock = threading.Lock()


def increment() -> None:
    global counter

    with lock:
        counter += 1


def main() -> None:
    global counter
    counter = 0

    with ThreadPoolExecutor(max_workers=20) as executor:
        list(executor.map(lambda _: increment(), range(1_000)))

    expected = 1_000
    assert counter == expected, (counter, expected)
    print("counter:", counter)


if __name__ == "__main__":
    main()
```

### Why the fix works

The lock makes the logical state transition:

```text
read → modify → write
```

mutually exclusive.

A thread cannot enter the protected section while another thread holding the same lock is inside it.

---

## 11. Critical Sections

A **critical section** is a region of code that accesses shared state and must not be concurrently modified in a way that violates correctness.

For example:

```python
with lock:
    counter += 1
```

The critical section is small.

### A bad critical section

```python
with lock:
    slow_network_call()
    database_query()
    file_upload()
    counter += 1
```

This is usually poor design.

The lock is being held while unrelated slow operations occur.

That causes other workers to wait unnecessarily.

### Better

```python
slow_network_call()

with lock:
    counter += 1
```

The general principle is:

> **Protect the shared state transition, not every operation that happens to occur nearby.**

### Trade-off

Too little protection:

```text
race
↓
incorrect state
```

Too much protection:

```text
contention
↓
less parallelism
↓
lower throughput
```

---

## 12. Lock Scope and Lock Granularity

Lock granularity is the size of the state protected by a lock.

A single global lock:

```python
global_lock = threading.Lock()
```

is simple but may serialize unrelated work.

Suppose workers update independent counters:

```text
partition A
partition B
partition C
```

A single lock may unnecessarily make:

```text
A → B → C
```

execute serially.

A more granular design might use ownership or independent locks.

### But finer-grained locking is not automatically better

More locks introduce:

- more coordination
- more complex invariants
- lock-ordering requirements
- more opportunities for deadlock
- harder debugging

The correct question is:

> What is the smallest synchronization boundary that preserves the invariant without making the design unnecessarily complicated?

---

## 13. `asyncio.Lock`

Threads and asyncio tasks require different synchronization primitives.

Use:

```python
threading.Lock
```

for synchronization between threads.

Use:

```python
asyncio.Lock
```

for synchronization among asyncio tasks.

### Basic pattern

```python
import asyncio

counter = 0
lock = asyncio.Lock()


async def increment() -> None:
    global counter

    async with lock:
        counter += 1
```

### Why they are different

`asyncio.Lock` participates in cooperative async scheduling.

A task waits asynchronously for the lock instead of blocking the event-loop thread in the same way a synchronous blocking lock can.

### Do not do this casually

```python
lock = threading.Lock()

async def bad() -> None:
    with lock:
        await slow_operation()
```

Holding a synchronous thread lock across an `await` can create serious problems, especially if another task needs that lock to make progress.

For async code, use an async synchronization design.

### Cancellation consideration

An async task waiting for a lock may be cancelled.

Therefore:

- keep critical sections small
- avoid unnecessary awaits inside them
- make state transitions cancellation-safe
- do not assume that a task will always finish after acquiring a lock

The `async with` pattern is the normal foundation:

```python
async with lock:
    ...
```

---

## 14. Check-Then-Act Races

A second major race pattern is:

```python
if not exists:
    create()
```

This is called **check-then-act**.

The problem is that the check and the action are separate operations.

### Broken timeline

```text
Worker A: checks → does not exist
Worker B: checks → does not exist

Worker A: creates
Worker B: creates
```

The assumption:

> "I checked that it did not exist, therefore I can safely create it."

is invalid unless the check and action are synchronized by the relevant authority.

### Common examples

- file creation
- cache initialization
- token refresh
- checkpoint creation
- job ownership
- database row creation
- output partition publication

---

## 15. File Existence/Create Races

Consider:

```python
from pathlib import Path

path = Path("checkpoint.txt")

if not path.exists():
    path.write_text("created")
```

Two workers can both observe that the file is absent.

### Safer principle

Prefer an operation whose semantics perform the required atomicity at the resource boundary.

For example, exclusive file creation can be expressed with operating-system file semantics rather than a separate existence check.

```python
from pathlib import Path

path = Path("checkpoint.txt")

try:
    with path.open("x", encoding="utf-8") as handle:
        handle.write("created")
except FileExistsError:
    pass
```

The important design is:

```text
create-if-absent
```

rather than:

```text
check
+
create
```

### Production lesson

When an external system can perform the atomic conditional operation for you, prefer that over trying to coordinate the operation solely in Python memory.

---

## 16. Token Refresh Races

Token refresh is a common Data Engineering concurrency problem.

Imagine 100 concurrent API requests all receive:

```text
401 Unauthorized
```

Each task concludes:

```text
token is invalid
→ refresh token
```

Without coordination:

```text
100 tasks
    ↓
100 refresh requests
```

This is a **token refresh stampede**.

Possible consequences include:

- unnecessary load
- provider rate limiting
- refresh-token rotation conflicts
- multiple replacement tokens
- inconsistent shared token state

### Safe pattern

Use:

1. shared token state
2. `asyncio.Lock`
3. re-check the token after acquiring the lock
4. refresh only if it is still invalid

### Example

```python
from dataclasses import dataclass
import asyncio
import time


@dataclass
class TokenState:
    access_token: str
    expires_at: float


token_state = TokenState("initial", time.time() + 300)
token_lock = asyncio.Lock()


def token_is_valid() -> bool:
    return token_state.expires_at > time.time() + 30


async def refresh_access_token() -> None:
    # Replace with the real provider call.
    await asyncio.sleep(0.05)

    token_state.access_token = "new-token"
    token_state.expires_at = time.time() + 300


async def ensure_valid_token() -> str:
    if token_is_valid():
        return token_state.access_token

    async with token_lock:
        # Re-check after waiting for the lock.
        if not token_is_valid():
            await refresh_access_token()

        return token_state.access_token
```

### Why the second check matters

Suppose:

```text
Task A checks → invalid
Task B checks → invalid

A acquires lock
A refreshes
A releases

B acquires lock
```

If B blindly refreshes again, the lock has prevented simultaneous refreshes but has not prevented duplicate refreshes.

The second check changes the logic:

```text
B acquires lock
B checks again
token is now valid
B reuses token
```

This pattern generalizes to many check-then-act problems.

---

## 17. Races in `asyncio`

A common misconception is:

> "Asyncio is single-threaded, so races cannot happen."

That is false.

Asyncio tasks can interleave at suspension points.

Consider:

```python
import asyncio

counter = 0


async def increment() -> None:
    global counter

    current = counter
    await asyncio.sleep(0)
    counter = current + 1
```

The `await` creates a scheduling opportunity.

### Possible execution

```text
Task A reads 0
Task A awaits

Task B reads 0
Task B awaits

Task A writes 1
Task B writes 1
```

Expected:

```text
2
```

Actual:

```text
1
```

### The key idea

An `await` can create a race opportunity when:

```text
check/read
   ↓
await
   ↓
action/write
```

The state may have changed while the task was suspended.

### Fix

```python
counter_lock = asyncio.Lock()


async def increment() -> None:
    global counter

    async with counter_lock:
        current = counter
        await asyncio.sleep(0)
        counter = current + 1
```

However, do not blindly put arbitrary slow operations inside the lock. Redesign the operation if the awaited work does not need mutual exclusion.

---

# Synchronization Primitives

## 18. Other Synchronization Primitives

Locks are not the only synchronization mechanism.

Different primitives express different coordination requirements.

| Primitive | Mental model | Typical purpose |
|---|---|---|
| `Lock` | one owner at a time | mutual exclusion |
| `RLock` | same thread may re-enter | nested/reentrant ownership |
| `Event` | a flag becomes set | one-way notification |
| `Condition` | wait for a state predicate | coordinated state transitions |
| `Barrier` | all participants meet | phase synchronization |
| `Queue` | messages move between workers | ownership/message passing |

Using the wrong primitive often produces unnecessarily complicated code.

---

## 19. RLock

`threading.RLock` is a **reentrant lock**.

A normal `Lock` cannot be acquired twice by the same thread without first releasing it.

An `RLock` allows the owning thread to acquire it repeatedly, provided it releases it the corresponding number of times.

### Example

```python
import threading

lock = threading.RLock()


def outer() -> None:
    with lock:
        inner()


def inner() -> None:
    with lock:
        print("inner section")


outer()
```

With a normal `Lock`, this pattern can deadlock because `outer()` owns the lock and `inner()` attempts to acquire it again.

### When it is useful

An `RLock` can help when:

- a call graph contains legitimate nested access to the same protected object
- a class method calls another method that uses the same synchronization boundary
- refactoring makes nested lock acquisition unavoidable

### Risks

An `RLock` can hide poor ownership design.

If code constantly needs reentrant acquisition, ask whether the state abstraction itself should be redesigned.

Do not use `RLock` simply because a normal `Lock` caused a deadlock.

---

## 20. Event

An `Event` represents a simple shared signal.

Mental model:

```text
not ready
    ↓
event.set()
    ↓
ready
```

### Example: worker waits for readiness

```python
import threading

ready = threading.Event()


def worker() -> None:
    print("waiting for system readiness")
    ready.wait()
    print("system is ready")


thread = threading.Thread(target=worker)
thread.start()

# Initialization work...
ready.set()

thread.join()
```

### Typical uses

- service is ready
- shutdown requested
- configuration loaded
- one-time initialization completed
- stop signal

### When not to use it

An event is not a general replacement for a lock.

It tells workers about a state transition; it does not by itself protect mutable state.

---

## 21. Condition

A `Condition` coordinates workers around a state predicate.

Mental model:

```text
state is not ready
       ↓
wait
       ↓
another worker changes state
       ↓
notify
       ↓
re-check predicate
```

### Example

```python
import threading

condition = threading.Condition()
items: list[int] = []


def consumer() -> int:
    with condition:
        while not items:
            condition.wait()

        return items.pop(0)


def producer(value: int) -> None:
    with condition:
        items.append(value)
        condition.notify()
```

### Why the `while` matters

Do not write:

```python
if not items:
    condition.wait()
```

and assume the condition remains true after waking.

The correct mental model is:

```python
while not predicate():
    condition.wait()
```

The state must be re-checked.

### When to use

Conditions are useful when workers need to wait for a particular shared-state predicate.

If simple producer-consumer communication is sufficient, a queue is often easier to reason about.

---

## 22. Barrier

A `Barrier` coordinates a fixed number of participants at a synchronization point.

Example:

```python
import threading

barrier = threading.Barrier(3)


def worker(name: str) -> None:
    print(name, "finished phase 1")
    barrier.wait()
    print(name, "started phase 2")


threads = [
    threading.Thread(target=worker, args=(f"worker-{i}",))
    for i in range(3)
]

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()
```

The workers do not proceed beyond the barrier until the required participants arrive.

### Practical uses

- staged algorithms
- coordinated test scenarios
- parallel preparation followed by a common phase
- demonstrations of synchronization

### Failure considerations

A barrier assumes the expected participants will arrive.

If one participant crashes or abandons the phase, other workers can wait indefinitely unless the barrier is configured and handled with appropriate timeout/error behavior.

Use barriers carefully in long-lived production pipelines.

---

# Deadlocks

## 23. Deadlocks

A deadlock occurs when concurrent workers wait forever for conditions that cannot become true.

A common pattern is circular waiting.

```text
Thread 1 owns Lock A
Thread 1 waits for Lock B

Thread 2 owns Lock B
Thread 2 waits for Lock A
```

Neither can continue.

### Four useful deadlock conditions

A classic deadlock can involve:

1. mutual exclusion
2. hold and wait
3. no preemption
4. circular wait

You do not need to memorize the list to debug a system, but it helps identify why the system is stuck.

---

## 24. How Deadlocks Happen

### Broken example

```python
import threading
import time

lock_a = threading.Lock()
lock_b = threading.Lock()


def worker_one() -> None:
    with lock_a:
        time.sleep(0.05)
        with lock_b:
            print("worker one")


def worker_two() -> None:
    with lock_b:
        time.sleep(0.05)
        with lock_a:
            print("worker two")
```

Possible timeline:

```text
Thread 1              Thread 2
--------              --------
acquire A             acquire B
wait for B            wait for A
```

Both wait forever.

### Why timing matters

The deadlock may appear only when the scheduling interleaving is unfortunate.

That makes deadlocks similar to races in one important respect:

> Normal testing may fail to expose them.

---

## 25. Lock Ordering

A standard strategy for avoiding lock-order deadlocks is:

> **Always acquire multiple locks in a consistent global order.**

For example:

```text
Lock A
  ↓
Lock B
```

Every worker follows:

```text
A → B
```

Never:

```text
worker 1: A → B
worker 2: B → A
```

### Corrected example

```python
import threading

lock_a = threading.Lock()
lock_b = threading.Lock()


def worker_one() -> None:
    with lock_a:
        with lock_b:
            print("worker one")


def worker_two() -> None:
    with lock_a:
        with lock_b:
            print("worker two")
```

The workers may contend, but they do not form the same circular wait.

### Production rule

If a system needs multiple locks, document their acquisition order.

For example:

```text
1. pipeline lock
2. partition lock
3. metadata lock
```

Do not rely on developers remembering the order informally.

---

## 26. Locks + Queues

A particularly dangerous pattern is holding a lock while waiting for a queue.

### Broken pattern

```text
thread acquires lock
        ↓
queue.get()
        ↓
consumer needs same lock
        ↓
consumer cannot acquire lock
        ↓
producer/consumer cannot progress
```

Example:

```python
with state_lock:
    item = queue.get()
    process_item(item)
```

If progress toward producing or consuming the required item depends on another worker acquiring `state_lock`, the system can deadlock.

### Better design

Do not hold the unrelated lock while waiting:

```python
item = queue.get()

with state_lock:
    update_shared_state(item)

process_item(item)
```

The exact order depends on the invariant, but the principle is:

> **Do not hold a lock while performing an operation that may block waiting for another participant whose progress could require that same lock.**

---

## 27. Deadlock Detection and Timeouts

Timeouts are a safety mechanism.

They can turn:

```text
wait forever
```

into:

```text
wait for a bounded period
→ report failure
→ recover or abort
```

For threads, lock acquisition can use a timeout:

```python
if not lock.acquire(timeout=2.0):
    raise TimeoutError("Could not acquire lock")
try:
    ...
finally:
    lock.release()
```

For async code, an operation can be bounded with a timeout:

```python
import asyncio


async def acquire_with_timeout(lock: asyncio.Lock) -> None:
    async with asyncio.timeout(2.0):
        await lock.acquire()

    try:
        ...
    finally:
        lock.release()
```

### Important limitation

A timeout does not fix a bad synchronization design.

It only prevents indefinite waiting.

Production systems should also:

- log which operation timed out
- include identifiers
- capture lock ownership/context where possible
- expose metrics
- decide whether to retry, fail, or degrade
- avoid silently converting a deadlock into data loss

---

## 28. Smaller Critical Sections

Critical-section size directly affects contention.

Bad:

```python
with lock:
    fetch()
    transform()
    upload()
    update_metadata()
```

Better when the invariant permits:

```python
data = fetch()
result = transform(data)
upload(result)

with lock:
    update_metadata()
```

### But do not split blindly

If the invariant requires:

```text
read state
+
validate
+
update state
```

to happen atomically, splitting it can reintroduce a race.

The goal is not:

> "Make every lock block tiny."

The goal is:

> **Make the synchronization boundary exactly large enough to preserve the required invariant and no larger.**

---

# Safer Architecture

## 29. Thread-Safe Data Structures

A thread-safe data structure provides synchronization for its supported operations.

Python's:

```python
queue.Queue
```

is a common example.

It is designed for communication among threads.

This does **not** mean:

> "Every operation in my pipeline is now thread-safe."

It means the queue's documented coordination operations are protected appropriately.

---

## 30. `queue.Queue` and Message Passing

Compare:

```text
Shared list
    +
many locks
    +
many workers
```

with:

```text
Producer
   ↓
queue.Queue
   ↓
Consumer
```

### Example

```python
from queue import Queue
from threading import Thread

queue: Queue[int | None] = Queue()


def producer() -> None:
    for value in range(10):
        queue.put(value)

    queue.put(None)


def consumer() -> None:
    while True:
        value = queue.get()
        try:
            if value is None:
                return

            print("processing", value)
        finally:
            queue.task_done()


producer_thread = Thread(target=producer)
consumer_thread = Thread(target=consumer)

consumer_thread.start()
producer_thread.start()

producer_thread.join()
queue.join()
consumer_thread.join()
```

### Why this reduces races

The producer owns the act of producing.

The consumer owns the act of consuming.

They exchange messages instead of both mutating one shared collection.

### Production lesson

Message passing often turns a synchronization problem into a data-flow problem.

That is frequently easier to reason about.

---

## 31. Avoiding Shared Mutable State

The strongest race-condition strategy is often:

> **Do not create the shared mutable state.**

Suppose 16 workers all update:

```python
shared_results: dict[str, int]
```

The first instinct may be:

```python
results_lock = threading.Lock()
```

A different architecture is:

```text
worker 1 → local result
worker 2 → local result
worker 3 → local result
...
worker 16 → local result
```

Then:

```text
aggregate results
```

once at a controlled boundary.

### Why this helps

Fewer shared objects mean:

- fewer locks
- fewer interleavings
- fewer deadlocks
- easier testing
- clearer ownership
- simpler recovery

---

## 32. Per-Worker Ownership

A Data Engineering system often has natural ownership boundaries.

For example:

```text
worker 1 → partition 1
worker 2 → partition 2
worker 3 → partition 3
```

Each worker writes only its assigned output:

```text
part-001.parquet
part-002.parquet
part-003.parquet
```

rather than:

```text
all workers → same output file
```

### Ownership rule

A useful engineering rule is:

> **If one worker can own a piece of state exclusively, do not synchronize access to it among all workers.**

Partition ownership is therefore both a performance strategy and a correctness strategy.

---

## 33. Immutability

Immutable values cannot be changed after creation.

Examples include:

```python
coordinates = (10, 20)
```

or:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class TaskInput:
    source_id: str
    partition_id: int
```

Multiple workers can safely read the same immutable input without coordinating writes to it.

### Why immutability helps

If:

```text
many readers
+
no mutation
```

then there is no write-write race on that object.

### Do not overstate immutability

Immutable Python inputs do not make external systems immutable.

You can still race on:

- files
- databases
- APIs
- caches
- shared services

Immutability reduces one class of shared-memory mutation; it does not eliminate concurrency problems everywhere.

---

## 34. Per-Task State

Avoid:

```python
current_run_id = None
current_partition = None
```

as mutable global state when multiple tasks can change them.

Prefer local task state:

```python
async def process_partition(run_id: str, partition_id: int) -> None:
    ...
```

Now the values belong to that invocation.

### Better ownership

```text
task A
  ├── run_id = A
  └── partition = 1

task B
  ├── run_id = B
  └── partition = 2
```

instead of:

```text
global run_id
global partition
```

Per-task state makes reasoning local.

---

## 35. `contextvars`

`contextvars` provides task-local/context-local values that can flow through asynchronous execution without putting mutable request metadata into global variables.

### Example

```python
import asyncio
from contextvars import ContextVar

run_id: ContextVar[str] = ContextVar("run_id", default="unknown")


async def process_partition(partition_id: int) -> None:
    print(
        f"run={run_id.get()} partition={partition_id}"
    )


async def main() -> None:
    run_id.set("run-2026-10-01")

    await asyncio.gather(
        process_partition(1),
        process_partition(2),
    )


asyncio.run(main())
```

This is useful for:

- run IDs
- request IDs
- correlation IDs
- source IDs
- logging metadata

### Important distinction

`contextvars` does **not** synchronize shared mutable state.

This:

```python
run_id.set("A")
```

does not protect:

```python
shared_dictionary["key"] = value
```

Use `contextvars` for **context propagation**, not mutual exclusion.

---

# Cross-Process and External State

## 36. Cross-Process Race Conditions

Threads share a process's memory.

Separate processes normally have separate Python memory spaces.

Therefore:

```text
threading.Lock
```

does not automatically protect a shared external resource from multiple processes.

Example:

```text
Process A ──┐
            ├── same file
Process B ──┘
```

or:

```text
Process A ──┐
            ├── same database row
Process B ──┘
```

A thread lock in Process A is invisible to Process B.

### Production rule

Synchronize at the boundary where the state is actually shared.

If the shared state is:

- a file → use filesystem-safe ownership/atomic operations
- a database row → use database synchronization
- a distributed lease → use the coordinating system
- a queue → use the queue's coordination semantics

---

## 37. Shared Files and Atomic Renames

Suppose two workers both write:

```text
output/part-000.parquet
```

Possible problems:

- overwrite
- interleaved writes
- truncated output
- partially visible output
- one worker publishes incomplete data

### Safer ownership model

```text
worker 1 → part-worker-001.parquet
worker 2 → part-worker-002.parquet
```

Then a separate commit/merge phase can publish the completed set.

### Atomic replacement pattern

A common local-filesystem publication pattern is:

```text
write temporary file
       ↓
flush/close as required
       ↓
atomic rename/replace
       ↓
final path
```

Python example:

```python
from pathlib import Path
import os


def publish_atomically(final_path: Path, content: bytes) -> None:
    temporary_path = final_path.with_suffix(final_path.suffix + ".tmp")

    with temporary_path.open("wb") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())

    os.replace(temporary_path, final_path)
```

### Important filesystem qualification

Do not assume identical atomicity guarantees across every filesystem, network filesystem, object store, or distributed storage system.

The correctness of this pattern depends on the semantics of the storage system.

For object stores, a local filesystem rename pattern is not automatically equivalent to a transactional object publication.

---

## 38. Concurrent Watermark Updates

Watermarks are especially important in Data Engineering.

Suppose two job runs overlap.

Initial state:

```text
watermark = 100
```

Run A processes through:

```text
150
```

Run B processes through:

```text
120
```

Possible execution:

```text
A reads 100
B reads 100

A processes → 150
B processes → 120

A writes 150
B writes 120
```

Final state:

```text
120
```

The system lost the progress represented by 150.

This is a **lost-update race**.

### Why it matters

A watermark is not merely a number.

It represents a correctness boundary:

```text
data before watermark
    ↓
already processed
```

If the watermark moves backward incorrectly, later extraction logic may:

- reprocess data
- create duplicates
- violate incremental assumptions
- skip data if combined with other faulty logic

---

## 39. Database Transactions and Row Locks

A database can become the synchronization authority for shared pipeline state.

Conceptually:

```text
BEGIN
  ↓
lock/read state
  ↓
validate
  ↓
update
  ↓
COMMIT
```

### Important qualification

A transaction alone does not automatically eliminate all races.

Correctness depends on:

- transaction isolation
- locking behavior
- constraints
- ordering
- application logic
- the exact invariant being protected

### Row lock example

PostgreSQL supports:

```sql
SELECT watermark
FROM pipeline_state
WHERE pipeline_id = $1
FOR UPDATE;
```

The transaction can then validate and update the locked row.

Conceptually:

```text
BEGIN
  ↓
SELECT ... FOR UPDATE
  ↓
validate current watermark
  ↓
UPDATE
  ↓
COMMIT
```

### Trade-offs

Row locking can introduce:

- blocking
- contention
- deadlocks
- reduced throughput

It is appropriate when serialized access to a particular row is part of the correctness requirement.

---

## 40. PostgreSQL Advisory Locks

PostgreSQL advisory locks allow the application to define a lock key and let PostgreSQL coordinate ownership.

They are useful when the synchronization concept is not naturally represented by one database row.

Examples:

```text
only one run for source X
only one schema migration for pipeline Y
only one maintenance operation for dataset Z
```

PostgreSQL provides functions such as:

```sql
SELECT pg_advisory_lock(12345);
```

and:

```sql
SELECT pg_try_advisory_lock(12345);
```

The `try` form can attempt acquisition without waiting indefinitely.

### Example concept

```text
job A → advisory key 5001 → acquires
job B → advisory key 5001 → cannot acquire

job A finishes
job A releases

job B → can acquire
```

### Important distinction

An advisory lock is an application coordination mechanism implemented by the database.

It does not automatically protect arbitrary resources unless all relevant participants honor the same lock protocol.

### When it fits

Use it when:

- the database is already the coordination authority
- the lock represents an application-level resource
- you need "one at a time" behavior
- a row lock would be awkward

---

## 41. Conditional `UPDATE` Patterns

Another approach is optimistic concurrency.

Suppose current state is:

```text
watermark = 100
```

A worker expects 100 and wants to update it to 150.

Use:

```sql
UPDATE pipeline_state
SET watermark = $1
WHERE pipeline_id = $2
  AND watermark = $3;
```

Parameters:

```text
new_value = 150
pipeline_id = "orders"
expected_old_value = 100
```

### Why this works

The update succeeds only if the state is still what the worker expected.

The database returns the affected-row count.

If:

```text
rowcount = 1
```

the expected state was still present.

If:

```text
rowcount = 0
```

another worker changed the state first.

This is a database form of:

```text
compare-and-swap
```

### Why it can be attractive

It can avoid holding a lock across a long application workflow.

Instead:

```text
perform work
↓
attempt conditional commit
↓
detect contention
```

The application can then retry, reconcile, or abort according to its semantics.

---

# Testing and Debugging

## 42. Stress Testing Concurrent Code

Normal unit tests often miss races.

A test may pass:

```text
1 run
10 runs
100 runs
```

and fail on:

```text
run 347
```

The reason is that the failure depends on timing.

### Stress-testing principles

Use:

- many workers
- repeated execution
- randomized scheduling
- deliberate yield points
- different worker counts
- assertions after each run
- invariant checks
- failure logging

### Example structure

```python
for attempt in range(1_000):
    state = run_concurrent_scenario()

    assert state == expected_state, {
        "attempt": attempt,
        "state": state,
    }
```

### What to test

Do not test only:

```text
"did the function return?"
```

Test the invariant:

```text
"did every required update occur exactly once?"
```

or:

```text
"did the watermark never move backward?"
```

or:

```text
"did every partition have exactly one owner?"
```

---

## 43. Randomized Delays

Small randomized delays can increase scheduling variation.

Thread example:

```python
import random
import time

time.sleep(random.uniform(0, 0.002))
```

Async example:

```python
await asyncio.sleep(random.uniform(0, 0.002))
```

### Correct purpose

Randomized delays are useful for:

- demonstrations
- stress tests
- reproducing timing-sensitive bugs

They are **not** synchronization.

Never "fix" a production race by adding:

```python
time.sleep(0.1)
```

That only changes timing.

A race requires a correctness mechanism, not a lucky delay.

---

## 44. `sys.setswitchinterval()`

CPython provides:

```python
import sys

sys.setswitchinterval(0.001)
```

This controls the interpreter's thread-switching interval at a conceptual level.

A shorter interval can increase opportunities for thread interleaving and make timing-sensitive behavior easier to observe in some demonstrations.

### Important limitations

It does not:

- guarantee a race
- guarantee a context switch at a particular source-code line
- make code thread-safe
- replace proper synchronization

Treat it as a debugging/testing aid.

Example:

```python
import sys

sys.setswitchinterval(0.001)
```

Use this carefully and restore the default if a test suite or environment depends on normal interpreter behavior.

---

## 45. Free-Threaded Python and Race Conditions

The GIL must not be treated as a synchronization primitive.

In standard GIL-enabled CPython, the GIL limits simultaneous execution of Python bytecode in a process. That does not make application-level shared state automatically correct.

For example, the following can still be logically unsafe:

```python
if key not in cache:
    cache[key] = expensive_create()
```

The issue is the application-level invariant, not merely whether two Python bytecode instructions execute at exactly the same instant.

Other sources of concurrency include:

- native extensions
- blocking operations
- external systems
- file systems
- databases
- network services

### Free-threaded Python

Supported free-threaded Python builds can execute Python code on multiple threads without the traditional global interpreter lock.

That makes correct synchronization even more important for code that shares mutable state.

The engineering conclusion is:

> **Do not design correctness around the assumption that the GIL will serialize your application.**

This topic connects directly to the later discussion of free-threaded Python and choosing a concurrency model.

---

# Progressive Runnable Examples

## 46. Example 1 — Simple Shared Counter Race

### Problem

100 threads increment one shared counter.

### Broken Code

```python
from concurrent.futures import ThreadPoolExecutor
import threading

counter = 0


def increment() -> None:
    global counter
    current = counter
    threading.Event().wait(0)
    counter = current + 1


def main() -> None:
    global counter
    counter = 0

    with ThreadPoolExecutor(max_workers=20) as executor:
        list(executor.map(lambda _: increment(), range(100)))

    print("expected:", 100)
    print("actual:  ", counter)


if __name__ == "__main__":
    main()
```

### What Happens

The result can be below 100.

### Why It Happens

Multiple threads can read the same old value before either writes its update.

### Corrected Code

```python
from concurrent.futures import ThreadPoolExecutor
import threading

counter = 0
lock = threading.Lock()


def increment() -> None:
    global counter

    with lock:
        counter += 1


def main() -> None:
    global counter
    counter = 0

    with ThreadPoolExecutor(max_workers=20) as executor:
        list(executor.map(lambda _: increment(), range(100)))

    assert counter == 100
    print("counter:", counter)


if __name__ == "__main__":
    main()
```

### Why the Fix Works

The complete state transition is protected.

### Production Lesson

If a counter is genuinely shared, protect the invariant. If possible, use per-worker counters and aggregate later.

---

## 47. Example 2 — Deterministic Lost-Update Demonstration

A barrier can make the demonstration easier to reproduce.

```python
import threading

counter = 0
barrier = threading.Barrier(2)


def increment() -> None:
    global counter

    current = counter
    barrier.wait()
    counter = current + 1


threads = [
    threading.Thread(target=increment),
    threading.Thread(target=increment),
]

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

print("expected:", 2)
print("actual:  ", counter)
```

Both workers read before either performs the write.

The intended invariant is violated predictably for this two-worker demonstration.

---

## 48. Example 3 — Excessive Lock Scope

### Problem

```python
def process() -> None:
    with lock:
        data = download()
        transformed = transform(data)
        upload(transformed)
        metrics["completed"] += 1
```

The lock protects the metric update but also serializes unrelated work.

### Better

```python
def process() -> None:
    data = download()
    transformed = transform(data)
    upload(transformed)

    with lock:
        metrics["completed"] += 1
```

### Production Lesson

Lock the invariant, not the entire workflow.

---

## 49. Example 4 — Async Race

### Broken Code

```python
import asyncio

counter = 0


async def increment() -> None:
    global counter

    current = counter
    await asyncio.sleep(0)
    counter = current + 1


async def main() -> None:
    global counter
    counter = 0

    await asyncio.gather(*(increment() for _ in range(100)))

    print("expected:", 100)
    print("actual:  ", counter)


asyncio.run(main())
```

### Fixed

```python
import asyncio

counter = 0
lock = asyncio.Lock()


async def increment() -> None:
    global counter

    async with lock:
        current = counter
        counter = current + 1


async def main() -> None:
    global counter
    counter = 0

    await asyncio.gather(*(increment() for _ in range(100)))

    assert counter == 100


asyncio.run(main())
```

Notice that the unnecessary `await` was removed from the critical section.

---

## 50. Example 5 — Check-Then-Act

### Broken

```python
from pathlib import Path

path = Path("state.txt")

if not path.exists():
    path.write_text("initialized", encoding="utf-8")
```

### Safer

```python
from pathlib import Path

path = Path("state.txt")

try:
    with path.open("x", encoding="utf-8") as handle:
        handle.write("initialized")
except FileExistsError:
    pass
```

### Production Lesson

Prefer atomic conditional operations at the resource boundary.

---

## 51. Example 6 — Token Refresh Stampede

### Broken

```python
if not token_is_valid():
    await refresh_token()
```

Many tasks can reach the same condition.

### Fixed

```python
if not token_is_valid():
    async with token_lock:
        if not token_is_valid():
            await refresh_token()
```

### Production Lesson

The second check inside the lock is essential.

---

## 52. Example 7 — RLock

```python
import threading

lock = threading.RLock()


def update_outer() -> None:
    with lock:
        update_inner()


def update_inner() -> None:
    with lock:
        print("safe nested acquisition")


update_outer()
```

Use this only when nested ownership is part of the intended design.

---

## 53. Example 8 — Event

```python
import threading

ready = threading.Event()


def worker() -> None:
    ready.wait()
    print("starting work")


thread = threading.Thread(target=worker)
thread.start()

# Initialization completes here.
ready.set()

thread.join()
```

---

## 54. Example 9 — Condition

```python
import threading

condition = threading.Condition()
items: list[int] = []


def consumer() -> int:
    with condition:
        while not items:
            condition.wait()

        return items.pop(0)


def producer(value: int) -> None:
    with condition:
        items.append(value)
        condition.notify()
```

---

## 55. Example 10 — Barrier

```python
import threading

barrier = threading.Barrier(3)


def worker(name: str) -> None:
    print(name, "phase 1 complete")
    barrier.wait()
    print(name, "phase 2 started")


threads = [
    threading.Thread(target=worker, args=(f"worker-{i}",))
    for i in range(3)
]

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()
```

---

## 56. Example 11 — Deadlock

### Broken Code

```python
import threading
import time

a = threading.Lock()
b = threading.Lock()


def one() -> None:
    with a:
        time.sleep(0.1)
        with b:
            print("one")


def two() -> None:
    with b:
        time.sleep(0.1)
        with a:
            print("two")


t1 = threading.Thread(target=one)
t2 = threading.Thread(target=two)

t1.start()
t2.start()

t1.join()
t2.join()
```

This can hang indefinitely.

### Fixed

```python
def one() -> None:
    with a:
        with b:
            print("one")


def two() -> None:
    with a:
        with b:
            print("two")
```

Both functions use the same lock order.

---

## 57. Example 12 — Queue-Based Message Passing

```python
from queue import Queue
from threading import Thread

work: Queue[int | None] = Queue()


def producer() -> None:
    for partition in range(10):
        work.put(partition)

    work.put(None)


def consumer() -> None:
    while True:
        item = work.get()
        try:
            if item is None:
                return

            print("processing partition", item)
        finally:
            work.task_done()


producer_thread = Thread(target=producer)
consumer_thread = Thread(target=consumer)

consumer_thread.start()
producer_thread.start()

producer_thread.join()
work.join()
consumer_thread.join()
```

The consumer owns processing of each queue message rather than competing over a shared mutable list.

---

## 58. Example 13 — Per-Worker Ownership

Instead of:

```python
shared_results = {}

with ThreadPoolExecutor(max_workers=8) as executor:
    ...
```

design:

```python
def process_partition(partition_id: int) -> tuple[int, int]:
    # Worker-owned local state.
    rows_processed = 0

    # Process only this partition.
    rows_processed += 100

    return partition_id, rows_processed
```

Then aggregate:

```python
results = dict(
    executor.map(process_partition, range(8))
)
```

The aggregation boundary is explicit.

---

## 59. Example 14 — `contextvars` Run ID

```python
import asyncio
from contextvars import ContextVar

run_id: ContextVar[str] = ContextVar("run_id", default="unknown")


async def process(partition_id: int) -> None:
    print(
        f"run={run_id.get()} partition={partition_id}"
    )


async def main() -> None:
    run_id.set("run-42")

    await asyncio.gather(
        process(1),
        process(2),
        process(3),
    )


asyncio.run(main())
```

This provides task-local context without a mutable global run ID.

---

## 60. Example 15 — Two-Process Shared File Risk

The following demonstrates the design risk rather than promising a deterministic corruption pattern.

```python
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path


def write_same_file(worker_id: int) -> None:
    path = Path("shared-output.txt")

    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"worker={worker_id}\n")


if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=4) as executor:
        list(executor.map(write_same_file, range(20)))
```

Appending may be workable under some filesystem semantics, but it should not be treated as a general transactional publication mechanism.

For structured pipeline output, prefer explicit partition ownership and controlled publication.

---

## 61. Example 16 — Conditional Watermark Update

Conceptual PostgreSQL statement:

```sql
UPDATE pipeline_state
SET watermark = :new_value
WHERE pipeline_id = :pipeline_id
  AND watermark = :expected_old_value;
```

Application logic:

```text
rowcount = 1
    → update succeeded

rowcount = 0
    → another writer changed the state
    → reconcile/retry/fail according to pipeline semantics
```

This is often preferable to blindly overwriting shared progress.

---

## 62. Example 17 — Row Lock

Conceptual transaction:

```sql
BEGIN;

SELECT watermark
FROM pipeline_state
WHERE pipeline_id = :pipeline_id
FOR UPDATE;

-- Validate and perform the state transition.

UPDATE pipeline_state
SET watermark = :new_value
WHERE pipeline_id = :pipeline_id;

COMMIT;
```

The lock is held by the database transaction, not by a Python `threading.Lock`.

---

## 63. Example 18 — PostgreSQL Advisory Lock

Conceptually:

```sql
SELECT pg_try_advisory_lock(5001);
```

If successful:

```text
run pipeline
```

Then:

```sql
SELECT pg_advisory_unlock(5001);
```

The exact lifecycle should account for transaction/session semantics and failure handling.

---

## 64. Example 19 — Stress Test

```python
from concurrent.futures import ThreadPoolExecutor
import threading

counter = 0
lock = threading.Lock()


def increment() -> None:
    global counter
    current = counter
    threading.Event().wait(0)
    counter = current + 1


def run_once(workers: int = 20, operations: int = 100) -> int:
    global counter
    counter = 0

    with ThreadPoolExecutor(max_workers=workers) as executor:
        list(executor.map(lambda _: increment(), range(operations)))

    return counter


failures = 0

for attempt in range(1_000):
    result = run_once()

    if result != 100:
        failures += 1
        print("race observed:", attempt, result)
        break

print("failures:", failures)
```

A race may appear quickly, or it may require a different machine, workload, or stronger scheduling perturbation.

That uncertainty is itself an important lesson.

---

# Production Data Engineering

## 65. Production Data Engineering Patterns

Concurrency correctness becomes much easier when synchronization boundaries map to data ownership.

### Pattern 1 — Partition ownership

```text
source
  ↓
partition assignment
  ├── worker A → partition 1
  ├── worker B → partition 2
  └── worker C → partition 3
```

Each worker owns:

- input partition
- temporary state
- output partition

Only shared metadata requires synchronization.

### Pattern 2 — Queue-based work distribution

```text
producer
   ↓
queue
   ↓
workers
   ↓
partition-specific outputs
```

The queue coordinates ownership rather than requiring all workers to mutate a common collection.

### Pattern 3 — Database as coordination authority

Use database synchronization for state that is already durable database state:

```text
job A ──┐
        ├── pipeline_state row
job B ──┘
```

Possible mechanisms:

- transaction
- row lock
- conditional update
- advisory lock

### Pattern 4 — Atomic publication

Do not expose partially written output.

Use:

```text
private temporary output
        ↓
validation
        ↓
publication/rename
```

where the storage system's semantics support the required atomicity.

### Pattern 5 — Minimize shared state

Prefer:

```text
local worker state
+
explicit result
+
controlled aggregation
```

over:

```text
many workers
+
large shared dictionary
+
many locks
```

---

## 66. Complete Progressive Example

Consider a concurrent extraction platform.

Each worker:

1. processes a partition
2. writes output
3. records progress
4. contributes to pipeline state

The system must avoid:

- duplicate output
- lost updates
- conflicting writes
- corrupted shared state
- deadlocks

### Design A — Lock-Heavy Shared-State Design

A naive architecture might use:

```text
16 workers
    ↓
shared dictionary
    ↓
global lock
    ↓
shared output manager
    ↓
shared watermark
```

Potential problems:

- broad lock scope
- high contention
- complicated lock ownership
- deadlock risk if multiple locks are introduced
- difficult failure recovery
- unclear output ownership

A lock can make the dictionary mutation safe without making the overall workflow safe.

### Design B — Ownership + Message Passing + Transactional State

A different architecture:

```text
                 ┌───────────────┐
source → planner │ work queue    │
                 └──────┬────────┘
                        ↓
              ┌───────────────────┐
              │ partition workers │
              └───────────────────┘
                 ↓      ↓      ↓
              part-1  part-2  part-3
                 \      |      /
                  \     |     /
                   progress events
                         ↓
                 state coordinator
                         ↓
                  database state
```

Worker responsibilities:

```text
worker owns partition
worker owns local intermediate state
worker writes unique output
worker emits completion/progress
```

Coordinator responsibilities:

```text
validate state transitions
commit durable metadata
enforce cross-run synchronization
```

### Why Design B may be easier to reason about

The architecture moves synchronization boundaries to places where state is naturally authoritative.

Workers do not need a giant shared dictionary.

Output ownership is explicit.

Durable shared state is protected by the database.

### But it is not universally superior

Design A can be reasonable when:

- the shared state is tiny
- lock scope is obvious
- the lifetime is short
- the number of workers is small
- the correctness invariant is simple

Design B introduces:

- more components
- more messages
- more operational state
- potentially more latency

Architecture should therefore be selected from requirements and failure modes, not from a blanket rule that "locks are bad."

---

## 67. Synchronization Decision Framework

When you discover shared state, ask in this order:

### Question 1 — Can I eliminate sharing?

If yes:

```text
ownership
```

is usually simpler than:

```text
lock
```

### Question 2 — Can I communicate through messages?

If yes:

```text
queue → worker
```

may be easier to reason about.

### Question 3 — Is the state external?

If yes, synchronize at the external authority:

```text
database
filesystem
service
```

### Question 4 — Is the update conditional?

If yes, consider:

```text
conditional UPDATE
```

or another atomic compare-and-swap style operation.

### Question 5 — Is serialized ownership required?

If yes, consider:

```text
row lock
advisory lock
lease
```

according to the actual system.

### Question 6 — Is in-process shared state unavoidable?

Then use the smallest suitable primitive:

```text
Lock
RLock
Condition
Event
Barrier
```

---

# Debugging Exercises

## 68. Debugging Exercise 1 — Counter Sometimes Lower Than Expected

### Broken code

```python
counter = 0


def increment() -> None:
    global counter

    current = counter
    yield_control()
    counter = current + 1
```

### Symptom

Expected:

```text
1000
```

Observed:

```text
812
```

### Diagnosis

The operation is read-modify-write.

### Root cause

Two workers can read the same value before either publishes its update.

### Correction

Protect the state transition with a `threading.Lock`, or redesign as per-worker counters followed by aggregation.

### Prevention

Stress-test the invariant rather than a single execution.

---

## 69. Debugging Exercise 2 — Two Tasks Refresh the Same Token

### Symptom

Authentication provider shows a burst of refresh calls.

### Root cause

Check-then-act:

```python
if invalid:
    refresh()
```

Multiple tasks make the same decision.

### Correction

```python
if invalid:
    async with lock:
        if invalid:
            refresh()
```

### Prevention

Test with many concurrent tasks all receiving an invalid-token response.

---

## 70. Debugging Exercise 3 — Two Locks Cause Intermittent Hangs

### Symptom

Pipeline occasionally freezes.

### Diagnosis

Inspect lock acquisition order.

### Likely root cause

```text
worker A: lock A → lock B
worker B: lock B → lock A
```

### Correction

Establish one global order.

### Prevention

Document and enforce lock ordering.

---

## 71. Debugging Exercise 4 — Consumer Pipeline Freezes

### Symptom

Queue contains no visible progress.

### Investigation

A worker holds:

```python
with lock:
    queue.get()
```

### Root cause

The worker is waiting for a queue item while holding a lock needed by another participant.

### Correction

Do not hold the lock across the blocking queue operation.

### Prevention

Review every blocking call inside a critical section.

---

## 72. Debugging Exercise 5 — Watermark Moves Backward

### Symptom

Final watermark is 120 although one run reached 150.

### Root cause

Lost update:

```text
A reads 100
B reads 100
A writes 150
B writes 120
```

### Correction options

- row lock
- conditional update
- advisory lock
- serialized job ownership

### Prevention

Make the watermark transition an explicit concurrency-controlled state transition.

---

## 73. Debugging Exercise 6 — Two Workers Write the Same Output

### Symptom

Output is overwritten or incomplete.

### Root cause

No explicit output ownership.

### Correction

Assign unique output paths:

```text
worker-001 → part-001
worker-002 → part-002
```

Then publish/merge under controlled semantics.

### Prevention

Make output partition ownership part of the pipeline contract.

---

## 74. Debugging Exercise 7 — `contextvars` Behaves Differently From Shared State

### Symptom

A task sees its own run ID even though another task has a different run ID.

### Diagnosis

That is expected behavior for task-local context.

### Root cause

`contextvars` provides context isolation, not global shared-state synchronization.

### Correction

Use:

```text
contextvars → request/run metadata
locks/transactions → shared mutable state
```

### Prevention

Keep these responsibilities conceptually separate.

---

# Hands-On Exercises

## 75. Basic Exercises

### Exercise 1 — Reproduce a Counter Race

**Objective:** observe a lost update.

**Scenario:** 20 threads increment a shared counter.

**Requirements:**
- use `ThreadPoolExecutor`
- use at least 100 operations
- separate read and write
- add a yield opportunity

**Expected result:** observed value can be below the expected value.

**Hints:**
- identify the read-modify-write sequence
- do not add a lock yet

**Validation:** repeat enough times to observe incorrect state or use a controlled barrier demonstration.

---

### Exercise 2 — Protect the Counter

**Objective:** make the previous exercise correct.

**Requirements:**
- use `threading.Lock`
- use `with lock:`
- keep the critical section small

**Expected result:** invariant holds across repeated executions.

**Validation:** run 1,000 attempts.

---

### Exercise 3 — Measure Before and After

Record:

```text
attempts
failures
elapsed time
```

Compare:

```text
broken correctness
```

with:

```text
correct synchronization
```

Do not optimize for speed until correctness is established.

---

### Exercise 4 — Event

Build a worker that waits until initialization is complete.

Requirements:

- worker waits on `Event`
- initializer calls `set()`
- worker proceeds afterward

Validation:

```text
worker must not start before readiness
```

---

### Exercise 5 — Barrier

Create three workers with two phases.

Validation:

```text
no worker may begin phase 2 until all required workers reach the barrier
```

---

## 76. Moderate Exercises

### Exercise 6 — Async Check-Then-Act Race

Create two asyncio tasks that both initialize shared state.

Requirements:

- include an `await` between check and action
- demonstrate duplicate initialization

Validation:

- count initialization calls

---

### Exercise 7 — Async Lock Fix

Protect the previous example with `asyncio.Lock`.

Validation:

```text
initialization_count == 1
```

---

### Exercise 8 — Token Refresh Race

Simulate many concurrent 401 responses.

Requirements:

- 100 tasks
- shared token
- simulated refresh operation
- measure refresh count

Expected safe behavior:

```text
refresh_count ≈ 1
```

for one invalid-token episode, assuming the refresh succeeds and all tasks coordinate through the same state.

---

### Exercise 9 — Fix Token Refresh

Use:

```python
asyncio.Lock
```

and a second validity check inside the lock.

Validation:

- no unnecessary duplicate refreshes

---

### Exercise 10 — Queue-Based Design

Build a producer-consumer pipeline using `queue.Queue`.

Requirements:

- no shared mutable list for work
- producer creates partition tasks
- consumers process them
- use `task_done()` and `join()`

Validation:

- every partition is processed exactly once

---

## 77. Hard Exercises

### Exercise 11 — Reproduce a Deadlock

Create two locks and two workers that acquire them in opposite order.

Requirements:

- make the deadlock observable
- use a timeout or watchdog in the test harness

Validation:

- prove that workers can stop making progress

---

### Exercise 12 — Fix Lock Ordering

Establish a global order.

Validation:

- repeated execution produces no deadlock under the test workload

---

### Exercise 13 — Reduce Critical Section Size

Start with:

```python
with lock:
    expensive_operation()
    shared_update()
```

Refactor so only the shared update is protected.

Validation:

- preserve correctness
- measure reduced contention

---

### Exercise 14 — Protect Shared File Output

Build a deliberately unsafe output design.

Then redesign using:

- partition ownership
- temporary files
- controlled publication

Validation:

- no worker overwrites another worker's partition

---

### Exercise 15 — Protect Concurrent Watermark Updates

Simulate overlapping job runs.

Implement at least two solutions:

- row lock
- conditional update

Validation:

- watermark cannot move to an invalid older state

---

### Exercise 16 — Stress Test a Race 1,000 Times

Build a race scenario.

Run it at least 1,000 times.

Collect:

```text
attempt number
workers
expected state
observed state
```

Validation:

- test demonstrates whether the implementation preserves the invariant

---

## 78. Advanced Exercises

### Exercise 17 — Conditional Watermark Updates

Implement:

```sql
UPDATE pipeline_state
SET watermark = :new_value
WHERE pipeline_id = :id
  AND watermark = :expected_old_value
```

Requirements:

- detect `rowcount == 0`
- handle contention explicitly

---

### Exercise 18 — PostgreSQL Advisory Lock

Implement a single-source job lock using an advisory key.

Requirements:

- acquire using `pg_try_advisory_lock`
- handle lock contention
- release reliably
- log the lock key

---

### Exercise 19 — Row Lock vs Conditional Update

Compare:

```text
SELECT ... FOR UPDATE
```

with:

```text
conditional UPDATE
```

Document:

- contention behavior
- transaction duration
- failure behavior
- retry semantics
- throughput implications

Do not declare one universally better.

---

### Exercise 20 — Lock-Free Partition Ownership

Design a pipeline where:

```text
one partition
→ one owner
→ one output
```

No shared mutable Python dictionary should be used for normal worker progress.

---

### Exercise 21 — `contextvars` Run IDs

Create a concurrent async pipeline with:

```text
run_id
source_id
partition_id
```

Use `contextvars` for logging context.

Validation:

- log records must contain the correct run ID for each task

---

### Exercise 22 — Concurrent ETL State Manager

Design a state manager that remains correct when two job runs overlap.

Include:

- ownership
- transaction boundary
- watermark
- partition status
- retries
- crash recovery
- duplicate execution

Document the invariants before writing synchronization code.

---

# Trade-offs

## 79. Locking Is Not Free

A lock introduces coordination.

Costs can include:

- contention
- reduced parallelism
- acquisition/release overhead
- deadlock risk
- starvation
- debugging complexity
- scheduling effects
- reduced throughput

### Contention

If 32 workers spend most of their time waiting for one lock:

```text
32 workers
    ↓
one lock
    ↓
mostly serialized execution
```

The program may still be correct but fail to achieve the desired concurrency.

### Starvation

Some synchronization designs can cause a worker to wait much longer than others.

Do not assume fairness unless the synchronization primitive explicitly provides the semantics you need.

### Locking vs ownership

Compare:

```text
shared mutable state
+
locks
```

with:

```text
ownership
+
message passing
```

The second may reduce synchronization entirely.

---

## 80. Shared State vs Ownership vs Database Synchronization

| Strategy | Strength | Cost |
|---|---|---|
| Shared state + lock | simple local coordination | contention/deadlocks |
| Ownership + message passing | clear responsibility | more explicit data flow |
| Database synchronization | durable external authority | database contention/latency |
| Atomic/conditional operation | small synchronization boundary | requires supported primitive |

Choose according to where the state lives and what invariant must hold.

---

# Common Mistakes

## 81. Assuming the GIL Makes Code Thread-Safe

Incorrect:

> "The GIL prevents races."

Correct:

> The GIL is an implementation mechanism in CPython; it is not a general application-level synchronization protocol.

---

## 82. Assuming One Test Run Proves Correctness

A race can remain invisible for thousands of executions.

Use stress testing and invariant-based assertions.

---

## 83. Locking Too Much Code

A lock around network, database, or file I/O can destroy useful concurrency.

---

## 84. Locking Too Little Code

Protecting only the write while leaving the read outside the critical section can still produce a lost update.

---

## 85. Holding Locks During I/O

Slow I/O creates long critical sections.

Move I/O outside the lock when the invariant permits.

---

## 86. Inconsistent Lock Ordering

Multiple locks require a documented acquisition order.

---

## 87. Using the Wrong Primitive

Examples:

- using `Event` when mutual exclusion is required
- using `Lock` when message passing is simpler
- using `threading.Lock` inside async workflows
- using `RLock` to hide unclear ownership

---

## 88. Forgetting That Processes Do Not Share Normal Python Memory

A `threading.Lock` in one process does not protect a file or database row from another process.

---

## 89. Using Python Locks to Protect Database State

If the shared state is a database row and multiple processes or services can modify it, use database synchronization.

---

## 90. Updating a Watermark Before Durable Completion

Do not advance a durable progress marker before the corresponding data processing/publication is safely complete.

Otherwise:

```text
watermark says done
data is not actually durable
```

can create correctness failures after a crash.

---

## 91. Writing Multiple Workers to the Same File

Prefer unique output ownership.

---

## 92. Using Random Sleeps as Synchronization

A delay changes timing.

It does not establish a correctness guarantee.

---

## 93. Swallowing Exceptions in Concurrent Workers

A synchronization design is incomplete if worker failures silently disappear.

Always make worker failure visible to the orchestration layer.

---

## 94. Assuming `contextvars` Synchronize Shared State

They isolate context; they do not lock mutable data.

---

## 95. Using Locks When Ownership Would Be Simpler

Before adding a lock, ask:

> Can I give this state one owner?

If yes, the race may disappear rather than merely being controlled.

---

# Production Checklist

## 96. Shared State

- [ ] All shared mutable state is identified.
- [ ] Ownership is explicit.
- [ ] Shared state is minimized.
- [ ] Mutable global state is justified.
- [ ] State invariants are documented.

## Thread Safety

- [ ] Critical sections are protected.
- [ ] Locks are correctly scoped.
- [ ] Lock scope is small.
- [ ] Slow I/O is outside critical sections where possible.
- [ ] Lock ordering is documented when multiple locks exist.

## Async Safety

- [ ] `asyncio.Lock` is used where appropriate.
- [ ] Check-then-act races are protected.
- [ ] `await` boundaries are reviewed for state races.
- [ ] Cancellation interactions are considered.
- [ ] Synchronous blocking locks are not casually held across `await`.

## Deadlocks

- [ ] Lock acquisition order is consistent.
- [ ] Locks are not held while waiting on queues.
- [ ] Blocking operations inside critical sections are justified.
- [ ] Synchronization timeouts exist where operationally appropriate.
- [ ] Deadlock symptoms are observable.

## Cross-Process State

- [ ] Shared files have explicit ownership.
- [ ] Publication semantics are understood.
- [ ] Atomic replacement is used where supported and appropriate.
- [ ] Database state updates are atomic or conditional.
- [ ] Concurrent job runs are controlled.

## Testing

- [ ] Race conditions have stress tests.
- [ ] Tests run repeatedly.
- [ ] Randomized scheduling/delays are used where useful.
- [ ] Results are validated against invariants.
- [ ] Failure cases are tested.
- [ ] Worker counts are varied.
- [ ] Tests do not depend on one lucky timing sequence.

## Production

- [ ] No hidden shared mutable state.
- [ ] No unexplained locks.
- [ ] No lock held across slow external operations without justification.
- [ ] No silent lost updates.
- [ ] No unbounded contention.
- [ ] Concurrency behavior is measurable and observable.
- [ ] Ownership boundaries are explicit.
- [ ] Cross-process coordination occurs at the correct authority.

---

# Interview Questions

## 97. Basic

### Question 1
What is a race condition?

**Model answer:** A race condition occurs when correctness depends on the timing or ordering of concurrent operations.

### Question 2
What is a read-modify-write operation?

**Model answer:** It reads existing state, computes a new value from it, and writes the new value. Without appropriate synchronization, multiple workers can read the same old value and overwrite each other's updates.

### Question 3
Why is `counter += 1` not a synchronization mechanism?

**Model answer:** The expression represents a logical read-modify-write state transition. Its source-code appearance as one statement does not establish an application-level atomicity guarantee across concurrent workers.

### Question 4
What is a critical section?

**Model answer:** A region that accesses shared state and must be protected from conflicting concurrent access to preserve an invariant.

### Question 5
Why use `with lock:`?

**Model answer:** It provides structured acquisition and release and ensures the lock is released when control leaves the block, including exception paths.

---

## 98. Intermediate

### Question 6
What is the difference between `threading.Lock` and `asyncio.Lock`?

**Model answer:** `threading.Lock` is for synchronization among threads; `asyncio.Lock` integrates with asyncio task scheduling and should be used for shared state coordinated among asyncio tasks.

### Question 7
Why can races happen in asyncio?

**Model answer:** Tasks interleave at suspension points such as `await`. If a task reads or checks state, awaits, and then acts on the old assumption, another task can change the state during the suspension.

### Question 8
What is a check-then-act race?

**Model answer:** The program checks a condition and then performs an action based on that observation, but another worker can change the state between the check and the action.

### Question 9
Why does token refresh require a second check inside the lock?

**Model answer:** Multiple tasks may observe an invalid token before one acquires the lock. After waiting, a task must re-check because another task may already have refreshed the token.

### Question 10
What is an `RLock`?

**Model answer:** A reentrant lock that allows the owning thread to acquire the same lock multiple times, with corresponding releases.

---

## 99. Advanced

### Question 11
How does lock ordering prevent deadlocks?

**Model answer:** If all participants acquire multiple locks in one consistent global order, the circular-wait pattern caused by opposite acquisition order is prevented.

### Question 12
Why should locks not normally be held while waiting on a queue?

**Model answer:** The operation needed to satisfy the queue wait may depend on another worker that requires the same lock, creating a circular dependency.

### Question 13
When would you use `queue.Queue` instead of a shared list protected by a lock?

**Model answer:** When the problem is naturally producer-consumer communication. A queue explicitly models ownership transfer and provides thread-safe queue operations.

### Question 14
Why does per-worker ownership reduce races?

**Model answer:** A worker that exclusively owns its state does not need synchronization with other workers for that state. Synchronization is moved to a smaller aggregation or publication boundary.

### Question 15
What is `contextvars` useful for?

**Model answer:** Propagating task-local or context-local metadata such as run IDs and request IDs. It is not a replacement for locks or other shared-state synchronization.

---

## 100. Senior Data Engineer

### Question 16
How would you protect a watermark when two pipeline runs can overlap?

**Model answer:** First define the watermark invariant and ownership semantics. Depending on requirements, use serialized job ownership, a transaction with row locking, a conditional update, or a PostgreSQL advisory lock. The choice depends on contention, retry semantics, transaction duration, and whether the state transition should be optimistic or serialized.

### Question 17
Why is a Python lock insufficient for a database watermark?

**Model answer:** Python locks coordinate participants that use that lock in the same synchronization domain. Other processes or services can modify the database independently. The database must enforce the relevant shared-state invariant.

### Question 18
Compare row locks and conditional updates.

**Model answer:** Row locks explicitly serialize access to the selected state while the transaction holds the lock. Conditional updates use an expected old value and detect whether the state changed. Conditional updates can reduce lock duration but require explicit conflict handling.

### Question 19
When would an advisory lock be appropriate?

**Model answer:** When the application needs a database-coordinated lock for a logical resource that is not naturally represented by one row, such as one active pipeline run per source.

### Question 20
How would you test a race that occurs once every few hundred runs?

**Model answer:** Create an invariant-based stress test, run the scenario repeatedly, increase worker count, add controlled randomized delays or yield points, collect failure context, and make the test fail on the first invariant violation. The test should not depend on a single timing sequence.

### Question 21
Does the GIL make shared mutable Python state safe?

**Model answer:** No. The GIL is not an application-level transaction mechanism. Correctness must be designed explicitly.

### Question 22
Why does free-threaded Python increase the importance of synchronization?

**Model answer:** True concurrent execution of Python code removes an implicit serialization assumption present in traditional GIL-enabled execution. Code that relies on accidental timing or interpreter serialization becomes more exposed to actual concurrent interleavings.

---

# Architecture Questions

## 101. Design a Concurrent Ingestion System With Shared State

### Requirements

- multiple workers
- partitioned extraction
- progress tracking
- unique output
- retries
- overlapping runs possible

### Assumptions

- workers may run in different processes
- durable state is stored in PostgreSQL
- output is partitioned

### Design

```text
scheduler
   ↓
partition planner
   ↓
work queue
   ↓
workers
   ├── local state
   ├── unique output
   └── progress event
             ↓
        PostgreSQL
```

### Synchronization boundary

- queue owns work distribution
- filesystem/object store owns output publication
- PostgreSQL owns durable progress state

### Failure modes

- worker crashes
- duplicate task delivery
- overlapping runs
- stale progress
- partial output

### Trade-offs

This design introduces more explicit coordination but reduces shared mutable worker state.

---

## 102. Design a Watermark Mechanism for Overlapping Runs

### Requirements

Two runs may process the same source concurrently.

### Options

#### Option A — Row lock

```text
BEGIN
↓
SELECT ... FOR UPDATE
↓
validate
↓
UPDATE
↓
COMMIT
```

Good when serialized state transitions are required.

#### Option B — Conditional update

```sql
UPDATE pipeline_state
SET watermark = :new_value
WHERE pipeline_id = :id
  AND watermark = :expected_old_value;
```

Good when optimistic conflict detection fits the workflow.

#### Option C — Advisory lock

Use one logical key per source.

Good when the requirement is:

```text
only one active run for source X
```

### Architecture decision

The correct choice depends on:

- whether overlapping runs should be allowed
- how long work takes
- how conflicts are resolved
- whether the database is already the coordination authority
- retry semantics

---

## 103. Design Partitioned Output Without Conflicting Writes

### Requirement

100 workers process 100 partitions.

### Design

```text
partition 1 → part-00001
partition 2 → part-00002
...
partition 100 → part-00100
```

No two workers own the same output path.

Use temporary paths during writing and controlled publication.

### Key invariant

```text
one partition
→ one owner
→ one output artifact
```

This eliminates an entire class of write races.

---

## 104. Design Token Refresh for 500 Concurrent API Tasks

### Requirements

- 500 concurrent tasks
- shared access token
- refresh on authentication failure
- avoid refresh stampede

### Design

```text
task
  ↓
use token
  ↓
401
  ↓
acquire asyncio.Lock
  ↓
re-check token
  ├── valid → reuse
  └── invalid → refresh once
```

### Failure modes

- refresh failure
- refresh token rotation
- cancellation
- provider rate limit
- simultaneous expiry

### Important principle

The lock should protect the token state transition, not the entire API workload.

---

## 105. Design a Concurrent ETL Pipeline With Minimal Shared State

Prefer:

```text
planner
  ↓
partition ownership
  ↓
worker-local state
  ↓
unique output
  ↓
completion message
  ↓
state coordinator
```

Avoid:

```text
all workers
  ↓
one giant shared dictionary
  ↓
one giant lock
```

The second design may work, but it creates a larger synchronization surface.

---

## 106. One Run Per Source

Suppose only one job may process a source at a time.

Possible strategies:

| Mechanism | Synchronization authority | Main consideration |
|---|---|---|
| Python lock | one process | insufficient across processes/services |
| File lock | filesystem | depends on filesystem semantics |
| Database row lock | PostgreSQL | transactional ownership |
| Advisory lock | PostgreSQL | logical application resource |
| Conditional state | PostgreSQL | optimistic conflict detection |
| Distributed coordination service | external | operational complexity |

Do not select by popularity.

Select based on:

- participant scope
- durability
- failure behavior
- operational environment
- required lease semantics
- contention

---

# Advanced Engineering Mindset

## 107. Questions to Ask Before Shipping Concurrent Code

Ask:

1. What state is shared?
2. Who owns the state?
3. Can the state be immutable?
4. Can workers communicate through queues?
5. Does this operation actually need a lock?
6. How small can the critical section be?
7. Could two operations interleave here?
8. Is there a check-then-act sequence?
9. Can two workers acquire locks in opposite order?
10. Is a lock being held during I/O?
11. Is the shared state inside Python memory or outside the process?
12. What happens if two job runs overlap?
13. What happens if the process crashes?
14. What happens if a worker is cancelled?
15. Is the update atomic?
16. Can optimistic concurrency work?
17. Can database synchronization solve the problem?
18. Can ownership eliminate the race entirely?
19. How will the race be tested?
20. How will the system prove correctness under contention?

These questions are more valuable than memorizing synchronization APIs.

---

# Production Review Example

## 108. Review This Design

Suppose an engineer proposes:

```python
with global_lock:
    response = call_api()
    write_file(response)
    update_watermark()
```

### Review

Potential problems:

1. API latency is inside the lock.
2. File I/O is inside the lock.
3. The watermark may represent external work.
4. A worker failure while holding the lock can complicate progress.
5. Other workers are unnecessarily serialized.
6. The lock only protects threads using that lock; it does not protect other processes.
7. The file and database have different synchronization authorities.

### Better questions

- Can each worker own its output?
- Can API calls happen without the lock?
- Can output be published atomically?
- Can watermark update be a transaction?
- Should the watermark use a row lock or conditional update?
- Should only one run own the source?
- Can progress be communicated as a message?

The point is not to replace one lock with another automatically.

The point is to redesign the synchronization boundary around the actual invariants.

---

# Complete Correctness Pattern

## 109. The Production Concurrency Hierarchy

A useful hierarchy is:

```text
1. Eliminate shared state
        ↓
2. Give state one owner
        ↓
3. Communicate through messages
        ↓
4. Use immutable values
        ↓
5. Use atomic/conditional operations
        ↓
6. Use appropriate locks
        ↓
7. Use database/external synchronization
        ↓
8. Stress-test the invariant
```

This is not a rigid law.

It is a design heuristic.

The earlier levels often reduce the need for the later levels.

---

# Common Failure Patterns

## 110. Failure Pattern: Lock Everything

Symptom:

```text
correct but slow
```

Root cause:

```text
critical sections are too broad
```

Fix:

- identify exact invariant
- reduce lock scope
- move I/O outside
- partition state

---

## 111. Failure Pattern: No Lock Because "It Usually Works"

Symptom:

```text
passes local tests
fails under load
```

Root cause:

```text
timing-dependent race
```

Fix:

- define invariant
- synchronize state transition
- add stress test

---

## 112. Failure Pattern: Async Lock Around Entire Workflow

Symptom:

```text
async application becomes serial
```

Root cause:

```python
async with lock:
    await network()
    await database()
    await file_operation()
```

Fix:

- identify exactly what state needs protection
- perform independent work outside the lock
- protect only the required transition

---

## 113. Failure Pattern: Python Lock for External State

Symptom:

```text
two processes still update the same state
```

Root cause:

```text
lock exists only in one Python synchronization domain
```

Fix:

```text
filesystem/database/distributed authority
```

must enforce the invariant.

---

# Self-Assessment

## 114. Knowledge Checklist

- [ ] I can explain a race condition.
- [ ] I can reproduce a race.
- [ ] I understand read-modify-write.
- [ ] I understand check-then-act.
- [ ] I can use `threading.Lock`.
- [ ] I can use `asyncio.Lock`.
- [ ] I understand critical sections.
- [ ] I can use `RLock`.
- [ ] I can use `Event`.
- [ ] I can use `Condition`.
- [ ] I can use `Barrier`.
- [ ] I can identify deadlocks.
- [ ] I can prevent deadlocks through lock ordering.
- [ ] I understand why locks should not cover slow I/O.
- [ ] I can use `queue.Queue` for safe communication.
- [ ] I can design without shared mutable state.
- [ ] I understand per-worker ownership.
- [ ] I understand immutability.
- [ ] I understand per-task state.
- [ ] I understand `contextvars`.
- [ ] I can reason about cross-process races.
- [ ] I understand atomic file replacement.
- [ ] I can protect shared watermark state.
- [ ] I understand row locks.
- [ ] I understand conditional `UPDATE`.
- [ ] I understand PostgreSQL advisory locks.
- [ ] I can write stress tests for races.
- [ ] I understand randomized-delay testing.
- [ ] I understand `sys.setswitchinterval()`.
- [ ] I understand why free-threaded Python increases synchronization requirements.
- [ ] I can design a production-safe concurrent Data Engineering workflow.

---

# Summary

## 115. Final Summary

The goal of concurrent programming is not:

> **"Put a lock around everything."**

The goal is:

1. **Identify shared state.**
2. **Define the invariant that must remain true.**
3. **Minimize shared mutable state.**
4. **Prefer ownership and message passing when possible.**
5. **Use immutable data for shared inputs where appropriate.**
6. **Protect unavoidable shared state.**
7. **Keep critical sections only as large as necessary.**
8. **Establish consistent lock ordering.**
9. **Avoid locks during slow operations.**
10. **Use the synchronization authority that actually owns the state.**
11. **Protect cross-process state with filesystem/database/external mechanisms as appropriate.**
12. **Stress-test behavior under contention.**
13. **Design for correctness before optimizing concurrency.**

The most important mental model is:

```text
shared state
    ↓
who owns it?
    ↓
can sharing be eliminated?
    ↓
if not, what invariant must be protected?
    ↓
what is the smallest synchronization boundary?
    ↓
what happens under contention?
    ↓
what happens on failure/cancellation/crash?
    ↓
how will correctness be tested?
```

A production-grade concurrent Data Engineering system is one where these questions have explicit answers.

---

# Interview and Architecture Master Review

## 116. Rapid-Fire Questions

1. What is a race condition?
2. What is a read-modify-write race?
3. What is a check-then-act race?
4. Why can `counter += 1` be unsafe as shared-state logic?
5. What does `threading.Lock` protect?
6. Why prefer `with lock:`?
7. What is a critical section?
8. Why should critical sections be small?
9. Why can `asyncio` still have races?
10. Why can an `await` create a race opportunity?
11. When is `RLock` appropriate?
12. What problem does `Event` solve?
13. What problem does `Condition` solve?
14. What problem does `Barrier` solve?
15. What is a deadlock?
16. How does lock ordering prevent deadlocks?
17. Why should a lock not normally be held while waiting on a queue?
18. What does a timeout do for synchronization?
19. Why is `queue.Queue` useful?
20. Why is message passing often safer than shared mutable state?
21. What is per-worker ownership?
22. How does immutability help?
23. What is per-task state?
24. What are `contextvars`?
25. Why are `contextvars` not a lock?
26. Why does a thread lock not protect another process?
27. How can atomic file replacement help?
28. What is a watermark race?
29. How can `SELECT ... FOR UPDATE` help?
30. What is a conditional update?
31. What is a PostgreSQL advisory lock?
32. How do you stress-test a race?
33. What does randomized delay accomplish?
34. What does `sys.setswitchinterval()` accomplish?
35. Why does the GIL not guarantee application correctness?
36. Why does free-threaded Python increase the importance of synchronization?
37. When should ownership replace locking?
38. How do you decide between row locking and conditional update?
39. How do you prevent multiple job runs from conflicting?
40. How do you prove a concurrent pipeline is correct?

---

# Production Readiness Gate

## 117. You Are Ready to Move On When

You should be able to take a concurrent pipeline design and identify:

```text
shared state
      ↓
ownership
      ↓
race opportunities
      ↓
critical sections
      ↓
lock boundaries
      ↓
deadlock risks
      ↓
external synchronization
      ↓
failure behavior
      ↓
stress-test strategy
```

You should be able to explain not only **how** to add a lock, but also **why the lock is needed**, **what invariant it protects**, **what it costs**, and **whether the lock should exist at all**.

The production-level skill is not memorizing synchronization primitives.

It is learning to design concurrency so that correctness follows from explicit ownership, controlled state transitions, appropriate synchronization boundaries, and repeatable testing under contention.
