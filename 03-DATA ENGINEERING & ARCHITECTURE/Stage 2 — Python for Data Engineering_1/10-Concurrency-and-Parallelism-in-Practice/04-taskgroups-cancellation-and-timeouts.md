# TaskGroups, Cancellation, and Timeouts

> Stage 2 → Python for Data Engineering → Module 2.10 → Concurrency and Parallelism in Practice  
> Python 3.13+  
> **Core principle:** Every concurrent task should have an owner, a lifetime, and a deadline.

## 1. Why This Topic Matters

Asynchronous concurrency is useful when a Data Engineering workflow must wait on many I/O operations without blocking the event loop. But concurrency alone is not production safety.

A production pipeline must answer:

- Who owns each task?
- When does the task stop?
- What happens when one task fails?
- What happens to sibling tasks?
- What happens when the process is cancelled?
- How long may an operation wait?
- How long may the whole workflow run?
- Are resources cleaned up?
- Is durable state saved safely?
- Can interrupted work resume?

`asyncio.TaskGroup`, cancellation, and timeout scopes provide the building blocks for answering these questions.

The central model is:

```text
                    STRUCTURED CONCURRENCY
                            |
          +-----------------+-----------------+
          |                 |                 |
       Ownership          Lifetime          Deadline
          |                 |                 |
      Who owns it?     When does it stop?  How long?
          |                 |                 |
          +-----------------+-----------------+
                            |
              predictable failure + cleanup
```

## 2. Learning Objectives

By the end of this file you should be able to:

- explain structured concurrency;
- create and manage tasks with `asyncio.TaskGroup`;
- explain TaskGroup lifecycle and waiting;
- explain failure propagation and sibling cancellation;
- handle `ExceptionGroup` with `except*`;
- understand `asyncio.CancelledError`;
- write cancellation-safe coroutines;
- clean up with `finally` and async context managers;
- use `asyncio.timeout()`, `asyncio.timeout_at()`, and `asyncio.wait_for()`;
- distinguish per-operation timeouts from overall deadlines;
- compare TaskGroup with `asyncio.gather()`;
- use `asyncio.shield()` appropriately;
- design graceful SIGINT/SIGTERM shutdown;
- stop new work, drain safe work, and cancel the rest;
- save checkpoints safely;
- design idempotent, cancellable, resumable pipeline steps;
- understand thread/process future timeout behavior;
- debug and architect production asynchronous workflows.

## 3. Prerequisites

This topic follows `03-asyncio-event-loop-coroutines-and-tasks.md`.

Assume familiarity with:

- `async def`;
- `await`;
- `asyncio.run()`;
- the event loop;
- coroutines;
- `asyncio.create_task()`;
- `asyncio.gather()`;
- basic async context managers.

A **task** is a scheduled coroutine with an identity and lifecycle. Structured concurrency asks:

> Who owns this task, and what scope defines its lifetime?

---

# 4. The Problem with Unstructured Async Tasks

This is easy to write:

```python
asyncio.create_task(work_a())
asyncio.create_task(work_b())
asyncio.create_task(work_c())
```

But who owns these tasks?

If `work_b()` fails:

```text
A ───────────────────────── running
B ─────── X failure
C ───────────────────────── running
```

The caller may not have a clear rule for:

- cancelling A and C;
- observing their exceptions;
- closing resources;
- saving state;
- deciding when the operation is actually over.

Unstructured tasks can therefore produce:

- orphaned work;
- hidden failures;
- leaked resources;
- work continuing after the caller failed;
- difficult shutdown;
- inconsistent checkpoints.

---

# 5. What Is Structured Concurrency?

Structured concurrency gives concurrent work an explicit scope.

Instead of:

```python
asyncio.create_task(work_a())
asyncio.create_task(work_b())
```

use:

```python
async with asyncio.TaskGroup() as tg:
    tg.create_task(work_a())
    tg.create_task(work_b())
```

The mental model becomes:

```text
parent operation
|
+-- TaskGroup
    |
    +-- Task A
    +-- Task B
    +-- Task C
```

The parent owns the group, and the group owns its children.

Three questions should always be answerable:

1. **Who owns this task?**
2. **What is its lifetime?**
3. **What is its deadline?**

This is the foundation for predictable failure, cancellation, cleanup, and shutdown.

---

# 6. TaskGroup Mental Model

`asyncio.TaskGroup` is an asynchronous context manager.

```python
async with asyncio.TaskGroup() as tg:
    tg.create_task(operation_a())
    tg.create_task(operation_b())
```

A simplified lifecycle is:

```text
enter group
   |
create tasks
   |
tasks run
   |
+--+-------------------+
|                      |
all succeed           failure
|                      |
wait/exit          cancel siblings
|                      |
+----------+-----------+
           |
       cleanup/wait
           |
       group exits
```

The group is not a result list. It is primarily a **lifecycle and failure-management scope**.

---

# 7. asyncio.TaskGroup Basics

## Example 1: Two successful tasks

```python
import asyncio


async def work(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return f"{name} finished"


async def main() -> None:
    tasks: list[asyncio.Task[str]] = []

    async with asyncio.TaskGroup() as tg:
        tasks.append(tg.create_task(work("customers", 1)))
        tasks.append(tg.create_task(work("orders", 2)))

    for task in tasks:
        print(task.result())


asyncio.run(main())
```

### Execution flow

```text
main
 |
 +-- TaskGroup
      |
      +-- customers
      +-- orders
      |
      +-- wait for both
 |
read results
```

The TaskGroup waits for its child tasks before successful exit.

## Example 2: Several partitions

```python
async def load_partition(partition_id: int) -> str:
    await asyncio.sleep(1)
    return f"partition-{partition_id}"


async def load_all(partitions: list[int]) -> list[str]:
    tasks: list[asyncio.Task[str]] = []

    async with asyncio.TaskGroup() as tg:
        for partition_id in partitions:
            tasks.append(
                tg.create_task(load_partition(partition_id))
            )

    return [task.result() for task in tasks]
```

This is a common Data Engineering pattern: a parent operation owns several independent partition tasks.

---

# 8. Creating Tasks Inside a TaskGroup

Prefer:

```python
tg.create_task(coro)
```

when the task belongs to the current structured scope.

For example:

```python
async with asyncio.TaskGroup() as tg:
    for partition_id in partitions:
        tg.create_task(process_partition(partition_id))
```

This communicates:

```text
ingestion run
    owns
    partition tasks
```

The relationship matters when the run fails, is cancelled, times out, or shuts down.

---

# 9. TaskGroup Lifecycle

A TaskGroup has four important conceptual phases:

1. enter the scope;
2. create child tasks;
3. wait for normal completion or react to failure/cancellation;
4. exit only after the child lifecycle has been resolved.

Do not think of:

```python
async with asyncio.TaskGroup()
```

as merely shorter syntax for `create_task()`.

It defines a structured ownership boundary.

---

# 10. What Happens When a Task Fails?

Suppose:

```text
Task A ───────────────────────✓
Task B ─────────── X failure
Task C ─────────────── running
```

For a non-cancellation failure in a child, the TaskGroup begins cancelling remaining sibling tasks.

Conceptually:

```text
1. B raises an exception.
2. TaskGroup observes the failure.
3. A/C that are still active receive cancellation.
4. Cancelled tasks execute cleanup.
5. TaskGroup waits for the child lifecycle to settle.
6. The failure is surfaced when the group exits.
```

Timeline:

```text
Task A ─────────────────────────✓
Task B ──────────── X failure
Task C ───────────── cancel ─ cleanup
                         |
                         v
                    group exits
```

This is one of the major reasons TaskGroup exists: related work fails as a structured unit instead of leaving unrelated child tasks running without a clear owner.

---

# 11. Sibling Task Cancellation

Example:

```python
import asyncio


async def worker(name: str, delay: float, fail: bool = False) -> None:
    try:
        await asyncio.sleep(delay)

        if fail:
            raise RuntimeError(f"{name} failed")

        print(f"{name} completed")
    except asyncio.CancelledError:
        print(f"{name} cancelled")
        raise
    finally:
        print(f"{name} cleanup")


async def main() -> None:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(worker("A", 1))
        tg.create_task(worker("B", 2, fail=True))
        tg.create_task(worker("C", 10))


asyncio.run(main())
```

When B fails, C does not simply continue for ten seconds as if nothing happened.

C receives cancellation and gets a chance to clean up.

### Data Engineering implication

If a logical ingestion stage consists of:

```text
download customers
download orders
write metadata
```

and the stage cannot be considered valid after a critical failure, structured sibling cancellation prevents unrelated child work from continuing indefinitely.

---

# 12. ExceptionGroup

Concurrent operations can produce multiple exceptions.

Python represents multiple related exceptions with `ExceptionGroup`.

Conceptually:

```text
ExceptionGroup
|
+-- ValueError
+-- TimeoutError
+-- RuntimeError
```

TaskGroup uses exception-group semantics when multiple relevant failures need to be represented.

The important mental model is:

```text
concurrent work
      |
      +-- failure 1
      +-- failure 2
      +-- failure 3
      |
      v
ExceptionGroup
```

Timing matters: once a TaskGroup begins cancelling siblings, some siblings may receive `CancelledError` before they can raise their original planned exception. Therefore you must not assume every task always contributes its intended exception.

---

# 13. Handling ExceptionGroup with except*

Use `except*` for exception groups.

```python
try:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(validate())
        tg.create_task(process())
except* ValueError as group:
    print("validation failures:", group)
except* TimeoutError as group:
    print("timeout failures:", group)
```

Compare:

```python
except ValueError:
    ...
```

with:

```python
except* ValueError:
    ...
```

The second form is designed to match relevant exceptions within an exception group.

Use categories that reflect real recovery semantics. Do not invent a large hierarchy of arbitrary exception classes merely to make concurrency look sophisticated.

---

# 14. Cancellation Fundamentals

Calling:

```python
task.cancel()
```

requests cancellation.

It does **not** mean:

```text
instant machine-level kill
```

A useful model is:

```text
task.cancel()
    |
    v
cancellation requested
    |
    v
coroutine reaches an async cancellation opportunity
    |
    v
CancelledError
    |
    +-- cleanup
    |
    +-- re-raise
```

Cancellation is therefore cooperative at the coroutine/application level.

Blocking synchronous code running on the event-loop thread can prevent prompt cancellation.

For example:

```python
import time


async def bad() -> None:
    time.sleep(60)
```

This blocks the event loop and prevents other async work from making progress.

---

# 15. asyncio.CancelledError

A cancellation-aware coroutine normally does this:

```python
async def worker() -> None:
    try:
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        print("cleanup before cancellation")
        raise
```

The final:

```python
raise
```

is essential.

It says:

> I performed my cleanup, but the operation remains cancelled.

Do not silently convert cancellation into successful completion.

---

# 16. What Cancellation Actually Does

Consider:

```python
async def operation() -> None:
    print("start")
    await asyncio.sleep(10)
    print("finish")
```

If another task calls:

```python
task.cancel()
```

the cancellation is delivered through asynchronous control flow.

The task should reach an appropriate await/cancellation point.

This is why code such as:

```python
while True:
    do_large_blocking_operation()
```

is unsuitable for an asyncio task if the blocking operation prevents the event loop from running.

Cancellation is not a universal interrupt mechanism for arbitrary Python code.

---

# 17. Writing Cancellation-Safe Coroutines

A cancellation-safe coroutine should:

- release resources;
- avoid false completion;
- avoid corrupting durable state;
- allow cancellation to propagate;
- keep cleanup bounded.

Example:

```python
async def process_partition(partition_id: int) -> None:
    resource = await acquire_resource()

    try:
        await extract_partition(partition_id)
        await write_partition(partition_id)
    except asyncio.CancelledError:
        print(f"{partition_id} cancelled")
        raise
    finally:
        await resource.close()
```

The structure is:

```text
acquire
  |
try
  |
work
  |
cancel/failure?
  |
cleanup
  |
propagate
```

---

# 18. finally and Cancellation Cleanup

Use `finally` for cleanup that must run regardless of normal completion, failure, or cancellation.

```python
async def write_batch(batch) -> None:
    writer = await open_writer()

    try:
        await writer.write(batch)
    finally:
        await writer.close()
```

Data Engineering resources can include:

- network clients;
- files;
- temporary outputs;
- database transactions;
- batch writers;
- leases.

Cancellation halfway through output is particularly important.

Prefer patterns such as:

```text
temporary output
      |
complete write
      |
validate
      |
atomic finalize
      |
checkpoint
```

over:

```text
write final file
      |
cancel halfway
      |
partial final file
```

---

# 19. Async Context Managers and Cancellation

Async context managers express resource ownership:

```python
async with resource_manager() as resource:
    await resource.process()
```

They provide a structured cleanup boundary.

The important lifecycle is:

```text
__aenter__
   |
resource acquired
   |
work
   |
cancellation/failure/success
   |
__aexit__
```

They do not magically make external side effects transactional, but they provide a strong cleanup structure.

---

# 20. Why You Must Not Swallow CancelledError

### Bad

```python
async def bad_worker() -> None:
    try:
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        print("cancelled")
        return
```

This turns cancellation into normal return.

### Worse

```python
async def very_bad_worker() -> None:
    while True:
        try:
            await do_work()
        except asyncio.CancelledError:
            continue
```

This can make shutdown effectively impossible.

### Good

```python
async def good_worker() -> None:
    try:
        await do_work()
    except asyncio.CancelledError:
        await cleanup()
        raise
```

Cancellation is control flow. Preserve it.

---

# 21. Timeouts: Why They Exist

External operations can hang.

Without a timeout:

```text
request
  |
waiting
  |
waiting
  |
waiting forever
```

This can cause:

- occupied connections;
- stuck tasks;
- missed SLAs;
- shutdown problems;
- unbounded resource usage.

A timeout is a deadline constraint.

Typical layers:

```text
HTTP request       10s
partition          60s
stage              5m
whole run          30m
shutdown           15s
```

Each should correspond to a real operational requirement.

---

# 22. asyncio.timeout()

Basic usage:

```python
import asyncio


async def operation() -> str:
    await asyncio.sleep(2)
    return "done"


async def main() -> None:
    try:
        async with asyncio.timeout(1):
            print(await operation())
    except TimeoutError:
        print("timed out")


asyncio.run(main())
```

The timeout mechanism uses cancellation internally.

Conceptually:

```text
deadline reached
      |
      v
cancellation requested
      |
      v
CancelledError enters operation
      |
      v
timeout scope exposes TimeoutError
```

Therefore timeout design and cancellation-safe coroutine design are inseparable.

---

# 23. asyncio.timeout_at()

`asyncio.timeout_at()` uses an absolute event-loop clock deadline.

```python
import asyncio


async def main() -> None:
    loop = asyncio.get_running_loop()
    deadline = loop.time() + 10

    try:
        async with asyncio.timeout_at(deadline):
            await operation()
    except TimeoutError:
        print("deadline exceeded")
```

### Relative vs absolute

```text
timeout(10)
    = approximately 10 seconds from now

timeout_at(deadline)
    = stop at this absolute event-loop deadline
```

Absolute deadlines are useful when nested functions must share one time budget.

---

# 24. asyncio.wait_for()

`wait_for()` applies a timeout to an awaitable:

```python
result = await asyncio.wait_for(
    operation(),
    timeout=5,
)
```

It is natural when the requirement is:

> Wait for this particular operation, but not longer than five seconds.

When its timeout expires, the awaited operation is cancellation-requested.

Use it when an individual awaitable is the natural scope.

---

# 25. Per-Operation Timeout vs Overall Deadline

These solve different problems.

| Concern | Per-operation timeout | Overall deadline |
|---|---|---|
| Scope | one operation | entire workflow |
| Example | API request ≤ 10s | job ≤ 5m |
| Purpose | bound one dependency | bound total execution |
| Common APIs | `wait_for`, `timeout` | `timeout`, `timeout_at` |

A pipeline may need both:

```text
overall deadline
|
+-- operation A timeout
+-- operation B timeout
+-- operation C timeout
```

A common mistake is to give every nested operation a fresh large timeout.

Example:

```text
A = 60s
B = 60s
C = 60s
```

does not mean the workflow is limited to 60 seconds.

An absolute deadline lets every operation consume only the remaining budget.

---

# 26. TaskGroup + Timeout Patterns

## Pattern A: Overall timeout around a group

```python
async with asyncio.timeout(30):
    async with asyncio.TaskGroup() as tg:
        tg.create_task(load("A"))
        tg.create_task(load("B"))
        tg.create_task(load("C"))
```

If the outer deadline expires, cancellation propagates into the group.

## Pattern B: Per-task timeout

```python
async def load_with_timeout(name: str) -> None:
    async with asyncio.timeout(5):
        await load(name)
```

Then:

```python
async with asyncio.TaskGroup() as tg:
    tg.create_task(load_with_timeout("A"))
    tg.create_task(load_with_timeout("B"))
```

If the timeout escapes the child task, it is a task failure and can cause sibling cancellation.

If the application catches the timeout and records it as an expected partition-level result, the parent semantics are different.

The key question is:

> Should this timeout fail the logical group, or only this unit of work?

---

# 27. TaskGroup vs asyncio.gather()

| Feature | TaskGroup | `gather()` |
|---|---|---|
| Structured task scope | Yes | Depends on caller |
| Explicit task ownership | Strong | Less explicit |
| Failure lifecycle | Structured | Different gather semantics |
| Sibling cancellation | TaskGroup failure semantics | Not equivalent to TaskGroup |
| Exception model | ExceptionGroup | Gather result/exception behavior |
| Result collection | task references | result list |
| Best fit | related work with shared lifecycle | straightforward concurrent awaits/results |

Do not conclude:

> `gather()` is always wrong.

For example:

```python
results = await asyncio.gather(
    fetch_metadata(),
    fetch_configuration(),
)
```

can be perfectly appropriate.

Prefer TaskGroup when several tasks form one owned operation whose failure and cancellation should be coordinated.

---

# 28. asyncio.shield()

Basic form:

```python
await asyncio.shield(critical_operation())
```

Normally:

```text
outer cancellation
      |
      v
awaited work cancelled
```

With shielding:

```text
outer cancellation
      |
      +--> outer await cancelled
      |
      +--> protected awaitable is not cancelled by that outer cancellation
```

But shielding does **not** mean:

> The underlying task can never be cancelled.

A separate holder of the task can still cancel it explicitly.

Shielding is therefore a narrow tool, not a general shutdown strategy.

---

# 29. Shielding Critical Work

A plausible use is a small checkpoint commit:

```python
await asyncio.shield(save_checkpoint())
```

Only consider this when the operation is:

- small;
- bounded;
- idempotent;
- correctness-critical;
- safe to finish during shutdown.

For example:

```text
main work
   |
reach safe boundary
   |
small durable checkpoint
   |
shutdown continues
```

Do not shield:

```text
entire ingestion job
```

because then shutdown can be delayed by work that should have been cancelled.

---

# 30. Limits and Risks of asyncio.shield()

`shield()` does not:

- prevent explicit cancellation of the underlying task;
- survive process termination;
- make an operation automatically idempotent;
- make a long operation appropriate for shutdown.

Think:

> protect a tiny critical transition

not:

> disable cancellation.

A good alternative to shielding is often redesign:

```text
make operation small
+
make it idempotent
+
make it resumable
```

Then cancellation becomes less dangerous.

---

# 31. Graceful Shutdown

Graceful shutdown means:

1. receive shutdown request;
2. stop scheduling new work;
3. allow safe in-flight work to finish;
4. cancel work that cannot finish within the shutdown budget;
5. clean resources;
6. save safe checkpoint/state;
7. exit correctly.

Diagram:

```text
SIGTERM / SIGINT
       |
       v
Stop new work
       |
       v
Finish safe in-flight work
       |
       v
Shutdown deadline
       |
       v
Cancel remaining work
       |
       v
Cleanup
       |
       v
Checkpoint
       |
       v
Exit
```

---

# 32. SIGINT and SIGTERM

`SIGINT` is commonly produced by `Ctrl+C` during local operation.

`SIGTERM` is commonly used by service managers and orchestration environments to request termination.

The application should translate these signals into a normal asynchronous shutdown path.

Do not put complex async cleanup directly into the signal handler. Instead, let the handler communicate:

```text
shutdown requested
```

and let normal async control flow perform the cleanup.

---

# 33. Stop New Work, Finish In-Flight Work, Cancel the Rest

Classify work as:

```text
not started
in flight
completed
```

During shutdown:

```text
not started
    → do not start

in flight
    → finish if safe and within deadline

in flight after deadline
    → cancel

completed
    → remain durably committed
```

This prevents a shutdown race where the system keeps consuming input and creating new tasks while simultaneously trying to terminate.

---

# 34. Saving Checkpoints During Shutdown

Suppose:

```text
window-001 → complete
window-002 → complete
window-003 → in progress
window-004 → pending
```

Shutdown occurs during window 003.

The checkpoint must not say:

```text
window-003 → complete
```

unless its durable output actually exists.

A safe sequence is:

```text
process window
     |
durable output
     |
confirm success
     |
checkpoint complete
```

not:

```text
checkpoint complete
     |
process window
```

The next run should be able to:

```text
recognize 001/002
resume or reconcile 003
process 004
```

---

# 35. Idempotent and Cancellable Pipeline Steps

Cancellation changes how pipeline steps should be designed.

### Unsafe

```text
update checkpoint
     |
write output
```

If cancellation occurs after the checkpoint, state falsely claims success.

### Safer

```text
write output
     |
confirm durable success
     |
update checkpoint
```

Idempotency makes replay safe.

For example, a partition can have a stable identity:

```text
partition_id = 42
```

and the sink can use that identity to ensure replaying partition 42 does not create an incorrect duplicate.

---

# 36. Resumable Data Engineering Workflows

A resumable workflow stores durable progress outside task memory.

Example:

| Window | State |
|---|---|
| 001 | committed |
| 002 | committed |
| 003 | in_progress |
| 004 | pending |

After cancellation:

```text
committed → do not unnecessarily repeat
in_progress → safely retry/reconcile
pending → process
```

The key relationship is:

```text
cancellation safety
+
idempotency
+
checkpointing
=
resumability
```

Cancellation is therefore not only an asyncio concern. It is a data correctness concern.

---

# 37. Timeouts in Threads and Processes

The timeout behavior of futures is different.

Consider:

```python
future.result(timeout=5)
```

This means:

> Wait up to five seconds for the result.

It does **not** mean:

> Kill the worker after five seconds.

Example:

```python
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import time


def blocking_work() -> str:
    time.sleep(20)
    return "done"


with ThreadPoolExecutor(max_workers=1) as executor:
    future = executor.submit(blocking_work)

    try:
        print(future.result(timeout=2))
    except TimeoutError:
        print("caller stopped waiting")
```

The worker can still be running.

The same conceptual distinction applies to `ProcessPoolExecutor`.

| Model | Timeout | Automatically stops underlying work? |
|---|---|---|
| asyncio timeout | cancellation-based | requests cancellation of async work; code must cooperate |
| ThreadPool future | `result(timeout=...)` | No |
| ProcessPool future | `result(timeout=...)` | No |

This is a critical distinction when choosing a concurrency model.

---

# 38. Common Failure Patterns

## Fire-and-forget

```python
asyncio.create_task(work())
```

with no owner.

**Danger:** unclear lifetime and shutdown behavior.

## Swallowed cancellation

```python
except asyncio.CancelledError:
    return
```

**Danger:** cancellation looks like success.

## No timeout

**Danger:** external dependency can hang forever.

## Only local timeouts

**Danger:** workflow can still exceed its total SLA.

## Treating TaskGroup and gather as identical

**Danger:** failure semantics are different.

## Shielding too much

**Danger:** shutdown cannot stop work promptly.

## Checkpoint before durable completion

**Danger:** next run can skip missing data.

## No shutdown deadline

**Danger:** graceful shutdown can itself hang forever.

## Continue scheduling during shutdown

**Danger:** drain never completes.

## Assuming future timeout kills worker

**Danger:** thread/process work can continue in background.

## Assuming cancellation is instant

**Danger:** cleanup and blocking code still matter.

---

# 39. Debugging Structured Concurrency

When a task never finishes, ask:

```text
Who owns it?
What deadline applies?
Is it blocked synchronously?
Is it waiting on I/O?
Was cancellation requested?
Was CancelledError swallowed?
Is cleanup blocked?
Is new work still being scheduled?
```

Useful task names:

```python
tg.create_task(
    process_partition(42),
    name="partition-42",
)
```

Useful log fields:

```text
run_id
task_name
partition_id
operation
deadline
started_at
cancelled
completed
error_type
```

Example:

```python
import logging

logger = logging.getLogger(__name__)


async def process_partition(partition_id: int) -> None:
    logger.info("partition_started", extra={"partition_id": partition_id})

    try:
        await do_work(partition_id)
    except asyncio.CancelledError:
        logger.info("partition_cancelled",
                    extra={"partition_id": partition_id})
        raise
    finally:
        logger.info("partition_cleanup",
                    extra={"partition_id": partition_id})
```

Focus debugging on lifecycle transitions, not only stack traces.

---

# 40. Production Data Engineering Patterns

## Pattern 1: Partition ownership

```text
run
 |
 +-- TaskGroup
      |
      +-- partition A
      +-- partition B
      +-- partition C
```

## Pattern 2: Bounded external operation

```text
API call
  |
timeout
  |
success / retry / failure
```

## Pattern 3: Durable state

```text
work
 |
durable output
 |
checkpoint
```

## Pattern 4: Resumability

```text
durable checkpoint
+
idempotent sink
+
replay
=
safe recovery
```

## Pattern 5: Graceful shutdown

```text
signal
 |
stop new work
 |
drain
 |
deadline
 |
cancel
 |
cleanup
 |
checkpoint
 |
exit
```

---

# 41. Complete Progressive Example

The following skeleton combines TaskGroup, cancellation, timeouts, cleanup, checkpointing, idempotency, and resumability.

```python
import asyncio
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Partition:
    partition_id: int


class CheckpointStore:
    def __init__(self) -> None:
        self.completed: set[int] = set()

    async def mark_complete(self, partition_id: int) -> None:
        # Replace with a real durable store in production.
        await asyncio.sleep(0.05)
        self.completed.add(partition_id)


async def extract(partition: Partition) -> list[dict[str, int]]:
    await asyncio.sleep(1)
    return [{"partition_id": partition.partition_id}]


async def write_output(
    partition: Partition,
    records: list[dict[str, int]],
) -> None:
    await asyncio.sleep(0.2)


async def process_partition(
    partition: Partition,
    checkpoints: CheckpointStore,
) -> None:
    try:
        async with asyncio.timeout(10):
            records = await extract(partition)
            await write_output(partition, records)

            # State is advanced only after successful output.
            await checkpoints.mark_complete(
                partition.partition_id
            )

    except asyncio.CancelledError:
        logger.info(
            "partition_cancelled",
            extra={"partition_id": partition.partition_id},
        )
        raise

    finally:
        logger.info(
            "partition_cleanup",
            extra={"partition_id": partition.partition_id},
        )


async def run_job(partitions: list[Partition]) -> None:
    checkpoints = CheckpointStore()

    loop = asyncio.get_running_loop()
    deadline = loop.time() + 30

    async with asyncio.timeout_at(deadline):
        async with asyncio.TaskGroup() as tg:
            for partition in partitions:
                tg.create_task(
                    process_partition(partition, checkpoints),
                    name=f"partition-{partition.partition_id}",
                )
```

### Execution flow

```text
overall deadline
       |
    TaskGroup
       |
  +----+----+----+
  |    |    |    |
 P1   P2   P3   P4
  |    |    |    |
 timeout per partition
  |    |    |    |
 extract → write → checkpoint
```

### Failure behavior

If a partition raises a non-cancellation exception, TaskGroup failure semantics can cancel its siblings.

If the business requirement says partitions must fail independently, catch/classify that failure inside the partition task and record it explicitly rather than letting it escape as a group-fatal error.

---

# 42. Production Example: Concurrent Ingestion Windows

Imagine an extractor processes:

```text
window_1
window_2
window_3
window_4
```

Each window:

1. makes asynchronous API requests;
2. validates the response;
3. writes output;
4. updates a checkpoint only after successful durable completion.

Requirements:

- TaskGroup;
- per-operation timeout;
- overall deadline;
- cancellation;
- cleanup;
- checkpoint;
- idempotency;
- graceful shutdown;
- resumability.

### One window fails

```text
window_1 → complete
window_2 → failure
window_3 → running
window_4 → running
```

If the windows form one logical stage:

```text
window_2 failure
       |
       v
cancel siblings
       |
cleanup
       |
group failure
```

### One window times out

If timeout escapes:

```text
timeout
   |
TaskGroup sees child failure
   |
sibling cancellation
```

If timeout is an expected partition-level outcome, handle it inside the task and record:

```text
window_2 = retryable_timeout
```

The correct choice depends on business semantics.

### SIGTERM arrives

```text
SIGTERM
   |
DRAINING
   |
stop new windows
   |
finish safe in-flight work
   |
shutdown deadline
   |
cancel remaining
   |
checkpoint safe work
   |
exit
```

The next run resumes from durable state.

---

# 43. Failure Scenarios

## Scenario 1 — One TaskGroup task fails

**Symptom:** child raises.

**Expected:** sibling cancellation begins.

**Debug:** inspect exception group and cleanup logs.

**Lesson:** failure propagation is part of lifecycle design.

## Scenario 2 — Several tasks fail

**Symptom:** multiple exceptions may be present.

**Expected:** relevant failures can be represented by `ExceptionGroup`.

**Debug:** use `except*` where appropriate.

## Scenario 3 — A task is cancelled

**Expected:** cleanup executes and cancellation normally propagates.

## Scenario 4 — CancelledError swallowed

**Symptom:** shutdown hangs or parent sees misleading success.

**Fix:** cleanup + `raise`.

## Scenario 5 — Operation exceeds timeout

**Expected:** cancellation is used to enforce the timeout.

**Debug:** verify the operation is cancellation-cooperative.

## Scenario 6 — Overall deadline expires

**Expected:** work inside the timeout scope is cancellation-requested.

## Scenario 7 — Checkpoint save is cancelled

**Expected:** do not claim the checkpoint is committed unless durable completion is known.

**Possible tool:** a small, bounded, idempotent critical checkpoint can sometimes be shielded.

## Scenario 8 — SIGTERM during extraction

**Expected:**

```text
stop new work
→ drain
→ shutdown deadline
→ cancel
→ cleanup
→ checkpoint
→ exit
```

## Scenario 9 — Resource held during cancellation

**Root cause:** missing `finally` or incorrect async context manager.

**Fix:** explicit lifecycle cleanup.

## Scenario 10 — Thread future times out

**Expected:** caller stops waiting; worker may continue.

---

# 44. Hands-On Exercises

## Beginner

### 1. Three-task TaskGroup

Create three tasks with different delays.

**Verify:** total execution is approximately bounded by the slowest task rather than the sum.

### 2. One task fails

Make one child raise `RuntimeError`.

**Observe:** sibling behavior and TaskGroup failure.

### 3. Cancellation

Cancel a worker and correctly handle `CancelledError`.

### 4. Cleanup

Create a fake resource and close it in `finally`.

### 5. Swallowed cancellation

Create and then fix:

```python
except asyncio.CancelledError:
    return
```

## Intermediate

### 6. Per-operation timeout

Run five tasks and apply a two-second timeout.

Record success versus timeout.

### 7. Overall deadline

Give a workflow one absolute ten-second deadline.

### 8. TaskGroup vs gather

Run the same failure scenario with both and compare lifecycle behavior.

### 9. ExceptionGroup

Create tasks that can raise different exception types and handle them with `except*`.

### 10. Cancellation-safe resource operation

Cancel during acquisition/use/write and verify cleanup.

## Advanced

### 11. SIGINT shutdown

Translate Ctrl+C into an asynchronous shutdown path.

### 12. SIGTERM shutdown

Implement service-style graceful termination.

### 13. Shutdown deadline

Give shutdown ten seconds, then cancel remaining work.

### 14. Checkpoint persistence

Persist completed partition state only after durable output.

### 15. Resume after cancellation

Cancel during partition 3 and safely resume on restart.

### 16. Shielded checkpoint

Compare shielded and unshielded checkpoint behavior.

### 17. Swallowed cancellation bug

Demonstrate a shutdown hang and repair it.

### 18. Shutdown race

Prevent new tasks from being created after shutdown begins.

## Production Challenge

Build an asynchronous ingestion runner with:

- multiple independent tasks;
- TaskGroup;
- failure propagation;
- timeout;
- cancellation;
- graceful shutdown;
- checkpoint;
- resumability;
- clean resources.

For each exercise verify:

- expected behavior;
- failure behavior;
- cancellation behavior;
- durable state;
- cleanup.

---

# 45. Debugging Exercises

## Debugging 1 — Swallowed CancelledError

### Broken

```python
async def worker() -> None:
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("cancelled")
        return
```

### Root cause

Cancellation was converted into normal completion.

### Corrected

```python
async def worker() -> None:
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("cancelled")
        raise
```

---

## Debugging 2 — Missing Cleanup

### Broken

```python
async def process() -> None:
    resource = await acquire_resource()
    await use(resource)
    await resource.close()
```

### Problem

Cancellation during `use()` skips `close()`.

### Corrected

```python
async def process() -> None:
    resource = await acquire_resource()

    try:
        await use(resource)
    finally:
        await resource.close()
```

---

## Debugging 3 — Timeout Misunderstood

A developer believes:

```python
await asyncio.wait_for(blocking_function(), timeout=5)
```

will forcibly stop arbitrary blocking CPU work.

### Root cause

Async cancellation is not a universal mechanism for interrupting arbitrary synchronous execution.

### Fix

Keep blocking work out of the event-loop thread and choose an appropriate thread/process strategy.

---

## Debugging 4 — Incorrect TaskGroup Assumption

**Assumption:** a failed child leaves all siblings running.

**Correction:** TaskGroup failure semantics include cancellation of remaining sibling tasks.

---

## Debugging 5 — Shielding Too Much

### Broken

```python
await asyncio.shield(run_entire_two_hour_job())
```

### Problem

Shutdown can no longer promptly stop the large operation through the outer cancellation path.

### Fix

Shield only a small, bounded, correctness-critical operation if truly necessary.

---

## Debugging 6 — Shutdown Never Finishes

### Broken

```python
async def worker() -> None:
    while True:
        try:
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            continue
```

### Root cause

Cancellation is intentionally ignored.

### Fix

Clean up and re-raise.

---

## Debugging 7 — Checkpoint Too Early

### Broken

```text
checkpoint = complete
      |
write output
```

### Correct

```text
write output
      |
durable success
      |
checkpoint = complete
```

---

# 46. Interview Questions

## Basic

1. Why does TaskGroup exist?
2. What does structured concurrency mean?
3. What happens when one TaskGroup task fails?
4. What is `ExceptionGroup`?
5. Why is `CancelledError` special?

## Intermediate

6. Why should `CancelledError` normally be re-raised?
7. How does timeout relate to cancellation?
8. `timeout()` versus `wait_for()`?
9. Why use `timeout_at()`?
10. TaskGroup versus `gather()`?

## Advanced

11. What does `shield()` do?
12. Why can shielding be dangerous?
13. How should a pipeline handle SIGTERM?
14. Why does checkpoint timing matter?
15. Does `Future.result(timeout=...)` kill the worker?
16. How would you design cancellation-safe ETL?

### Model answer themes

A strong senior-level answer should discuss:

```text
ownership
lifetime
deadlines
failure propagation
cancellation
cleanup
durable state
idempotency
recovery
```

rather than only naming APIs.

---

# 47. Architecture Questions

## 1. Design a graceful shutdown for a two-hour ingestion job

Use:

```text
signal
→ stop new work
→ drain safe work
→ bounded shutdown
→ cancel
→ checkpoint
→ exit
```

Make partitions independently resumable.

## 2. Stop within 30 seconds of SIGTERM

Define a shutdown budget:

```text
T0 + 30 seconds
```

Stop new work immediately, drain safe work, then cancel remaining work before the deadline.

## 3. Independently resumable partitions

Store durable partition state:

```text
partition_id
status
checkpoint
output identity
updated_at
```

Advance only after durable success.

## 4. Timeout layers

Use:

```text
workflow deadline
  |
stage/partition timeout
  |
individual dependency timeout
```

Each boundary should represent a real operational requirement.

## 5. Cancellation-safe checkpointing

Write durable output first, then commit checkpoint state. Consider shielding only a small critical commit.

## 6. TaskGroup versus manually managed tasks

Use TaskGroup when work shares a logical lifecycle. Long-lived independent components still need explicit ownership and shutdown design.

## 7. No partial final files

Use:

```text
temporary output
→ complete
→ validate
→ atomic finalize
→ checkpoint
```

---

# 48. Advanced Thinking

Before starting concurrent work, ask:

1. Who owns this task?
2. How long may it live?
3. What is its deadline?
4. What happens if it fails?
5. What happens to siblings?
6. What happens if it is cancelled?
7. What resources does it hold?
8. How is cleanup guaranteed?
9. What is the per-operation timeout?
10. What is the overall deadline?
11. Can the work be resumed?
12. When is state committed?
13. What happens during SIGTERM?
14. What happens if shutdown occurs during checkpointing?
15. Is shielding really necessary?
16. Can idempotency remove the need for shielding?
17. Does the selected timeout actually stop the underlying work?

These questions turn asyncio knowledge into production engineering judgment.

---

# 49. Production Checklist

## Task lifecycle

- [ ] Every task has an owner.
- [ ] Task lifetime is bounded.
- [ ] No uncontrolled background tasks.
- [ ] Task names are useful for debugging where appropriate.

## Failure handling

- [ ] Sibling cancellation is understood.
- [ ] `ExceptionGroup` is handled appropriately.
- [ ] Errors cannot disappear silently.
- [ ] Failure semantics match the logical operation.

## Cancellation

- [ ] `CancelledError` is not accidentally swallowed.
- [ ] Cleanup runs during cancellation.
- [ ] Operations are cancellation-safe.
- [ ] Blocking synchronous code does not stall the event loop.

## Timeouts

- [ ] Individual operations have appropriate timeouts.
- [ ] Overall workflows have deadlines when required.
- [ ] Timeout values are justified.
- [ ] Nested operations respect the remaining budget.

## Shutdown

- [ ] SIGINT is handled.
- [ ] SIGTERM is handled.
- [ ] New work stops.
- [ ] In-flight work is managed.
- [ ] Shutdown has a deadline.
- [ ] Resources are closed.

## State

- [ ] Checkpoints are updated only after durable success.
- [ ] Work can resume after cancellation.
- [ ] Steps are idempotent.
- [ ] Partial output cannot be mistaken for final output.

## Production

- [ ] No leaked connections.
- [ ] No orphaned tasks.
- [ ] No infinite shutdown.
- [ ] Failure behavior is tested.
- [ ] Replay/resume behavior is tested.

---

# 50. Summary

Structured concurrency gives asynchronous work explicit ownership and lifecycle.

```text
TaskGroup
   ↓
ownership
   ↓
failure propagation
   ↓
sibling cancellation
   ↓
cleanup
```

Cancellation is a request, not an instant kill:

```python
task.cancel()
```

should generally lead to:

```python
except asyncio.CancelledError:
    cleanup()
    raise
```

Timeouts use cancellation internally.

Use:

```python
asyncio.timeout(...)
```

for a scoped timeout,

```python
asyncio.timeout_at(...)
```

for an absolute deadline,

and:

```python
asyncio.wait_for(...)
```

for an individual awaitable.

TaskGroup and `gather()` are not interchangeable abstractions.

`asyncio.shield()` is a narrow mechanism for protecting a small critical operation from an outer cancellation path. It is not a way to make work permanently uncancellable.

Graceful shutdown is a lifecycle:

```text
signal
→ stop new work
→ finish safe in-flight work
→ shutdown deadline
→ cancel remaining
→ cleanup
→ checkpoint
→ exit
```

For Data Engineering, the deeper relationship is:

```text
structured concurrency
+
cancellation safety
+
timeouts
+
idempotency
+
durable checkpoints
+
resumability
=
predictable asynchronous pipelines
```

---

# 51. Self-Assessment

- [ ] I can explain structured concurrency.
- [ ] I can explain why `asyncio.TaskGroup` exists.
- [ ] I can use TaskGroup.
- [ ] I understand TaskGroup lifecycle.
- [ ] I understand failure propagation.
- [ ] I can explain sibling cancellation.
- [ ] I understand `ExceptionGroup`.
- [ ] I can use `except*`.
- [ ] I understand `CancelledError`.
- [ ] I can write cancellation-safe coroutines.
- [ ] I can use `finally` for cleanup.
- [ ] I can use async context managers safely.
- [ ] I understand `asyncio.timeout()`.
- [ ] I understand `asyncio.timeout_at()`.
- [ ] I understand `asyncio.wait_for()`.
- [ ] I understand per-operation timeout versus overall deadline.
- [ ] I can compare TaskGroup and `gather()`.
- [ ] I understand `asyncio.shield()`.
- [ ] I know why excessive shielding is dangerous.
- [ ] I can design SIGINT/SIGTERM shutdown.
- [ ] I can stop scheduling new work during shutdown.
- [ ] I can manage in-flight work.
- [ ] I can save checkpoints safely.
- [ ] I can design idempotent and cancellable steps.
- [ ] I can design resumable workflows.
- [ ] I understand thread/process future timeout behavior.
- [ ] I understand why `Future.result(timeout=...)` does not kill underlying work.
- [ ] I can debug swallowed cancellation.
- [ ] I can debug shutdown hangs.
- [ ] I can reason about ExceptionGroup.
- [ ] I can design cancellation-safe Data Engineering pipelines.

---

# 52. Final Review

Before considering this topic complete, you should be able to explain:

```text
TaskGroup
    ↓
structured ownership
    ↓
failure propagation
    ↓
sibling cancellation
    ↓
ExceptionGroup
    ↓
CancelledError
    ↓
cleanup
    ↓
timeouts
    ↓
absolute deadlines
    ↓
shielding
    ↓
graceful shutdown
    ↓
checkpointing
    ↓
idempotency
    ↓
resumability
```

The production learning loop is:

```text
build
  ↓
inject failures
  ↓
test cancellation
  ↓
test shutdown
  ↓
verify cleanup
  ↓
verify checkpoint correctness
  ↓
replay/resume
  ↓
measure and debug
```

The goal is not simply to know how to start concurrent tasks.

The goal is to make asynchronous work:

**owned, bounded, cancellable, observable, recoverable, and correct.**
