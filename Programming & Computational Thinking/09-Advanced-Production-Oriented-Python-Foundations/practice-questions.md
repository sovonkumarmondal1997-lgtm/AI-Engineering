# Advanced Production-Oriented Python Foundations
# Practice Questions

## How to Use This Practice Set

This file contains exactly **44 practice questions** covering the eleven source chapters for `09-Advanced-Production-Oriented-Python-Foundations`.

Use each question in this order:

1. Read **Problem** only.
2. Try to solve it independently.
3. Write and run your own code.
4. Test expected and edge-case behavior.
5. Debug before looking at the guidance.
6. Read **How to Think About the Problem**.
7. Compare your implementation with the provided solution.
8. Explain the solution in your own words.

Do not immediately read the solution. The goal is to build engineering judgment, not just recognize an answer.

## Difficulty Model

- **Basic (1–11):** foundational reasoning, direct API use, output prediction, and small implementations.
- **Moderate (12–22):** combines two or three concepts and requires more behavioral reasoning.
- **Hard (23–33):** debugging, memory/performance reasoning, design decisions, and multiple interacting concepts.
- **Advanced (34–44):** realistic production-oriented scenarios, multi-concept architecture, constraints, failure handling, and Applied AI context.

The questions are grounded in the actual eleven source chapters rather than using the filenames alone as a topic list.
# Part I — Basic Questions

### Question 1 — Read the Iterator Protocol by Hand

#### Difficulty
Basic

#### Topics Covered
- iterables vs iterators
- iter()
- next()
- StopIteration

#### Problem
You are given a list of document IDs. A teammate says that calling `iter()` is unnecessary because the list itself is already an iterator. Determine what is actually happening and manually consume the iterator.

#### What You Need to Do
Write a short program that creates an iterator, calls `next()` three times, then safely handles the fourth `next()` when the iterator is exhausted.

#### How to Think About the Problem
Separate the two ideas: the list is the iterable, while `iter(list)` produces an iterator that keeps iteration state. Then reason about what happens after each `next()` call and what signals exhaustion.

#### Solution
```python
document_ids = ["doc-1", "doc-2", "doc-3"]

it = iter(document_ids)

print(next(it))
print(next(it))
print(next(it))

try:
    print(next(it))
except StopIteration:
    print("iterator exhausted")
```

#### Solution Explanation
`iter(document_ids)` creates an iterator over the list. The iterator remembers where it is, so each `next()` advances to the next item. After the third item there is nothing left; the iterator signals that fact with `StopIteration`.

This demonstrates why an iterable and an iterator are different. A list can create multiple independent iterators, while a particular iterator instance has one current position and can become exhausted.

#### Key Concepts Reinforced
- An iterable can produce an iterator.
- An iterator implements the iteration protocol through `__iter__()` and `__next__()`.
- `StopIteration` signals normal exhaustion.

#### Common Mistakes
- Assuming every iterable is itself an iterator.
- Calling `next()` on the list directly.
- Expecting an exhausted iterator to restart automatically.

#### Production Connection
Streaming document pipelines frequently consume iterators one item at a time. Understanding exhaustion prevents subtle bugs when a generator or iterator is passed through multiple processing stages.


### Question 2 — Write a Metadata-Preserving Decorator

#### Difficulty
Basic

#### Topics Covered
- higher-order functions
- decorators
- closures
- functools.wraps

#### Problem
Create a decorator that logs a function call and then executes the original function. The original function has a meaningful name and docstring that should remain visible after decoration.

#### What You Need to Do
Implement the decorator using `*args` and `**kwargs`, apply it with `@`, and verify that the decorated function still exposes the original `__name__` and `__doc__`.

#### How to Think About the Problem
A decorator receives one callable and returns another callable. The wrapper should forward arguments unchanged. Because the wrapper replaces the original function object at the name binding, use `functools.wraps` so important metadata is copied to the wrapper.

#### Solution
```python
from functools import wraps

def log_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_call
def add(a, b):
    """Add two numbers."""
    return a + b

print(add(2, 3))
print(add.__name__)
print(add.__doc__)
```

#### Solution Explanation
The decorator factory is not needed here because no configuration is supplied. `log_call` receives `add`, creates `wrapper`, and returns it. `@log_call` is equivalent to rebinding `add` to the returned wrapper.

`@wraps(func)` copies useful metadata and establishes `__wrapped__`, which is valuable for debugging and introspection.

#### Key Concepts Reinforced
- Functions are objects.
- Decorators are higher-order functions.
- `*args`/`**kwargs` forward arbitrary calls.
- `functools.wraps` preserves metadata.

#### Common Mistakes
- Forgetting to return the wrapper.
- Writing a wrapper that drops keyword arguments.
- Assuming decoration changes only behavior and never affects introspection.

#### Production Connection
Observability decorators are common in application code, but preserving metadata makes debugging, tracing, testing, and tooling much easier.


### Question 3 — Build a Resource Context Manager

#### Difficulty
Basic

#### Topics Covered
- context managers
- with
- __enter__
- __exit__
- cleanup
- exception propagation

#### Problem
A small in-memory resource has a clear lifecycle: it must be opened before use and closed after use, even if the body raises an exception.

#### What You Need to Do
Implement a class-based context manager that prints `open`, returns the resource from `__enter__`, guarantees cleanup through `__exit__`, and lets the exception propagate to an outer handler.

#### How to Think About the Problem
The key requirement is deterministic cleanup. `__enter__` prepares and returns the resource. `__exit__` always runs when the `with` block leaves, including exceptional exit. Return `False` so the exception remains visible.

#### Solution
```python
class Resource:
    def __enter__(self):
        print("open")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("close")
        return False

    def read(self):
        return "data"

try:
    with Resource() as resource:
        print(resource.read())
        raise ValueError("example failure")
except ValueError as exc:
    print("handled:", exc)
```

#### Solution Explanation
The `with` statement enters the resource, executes the body, and then calls `__exit__` on normal or exceptional exit. Returning `False` means the `ValueError` is not suppressed, so the outer `except` can handle it.

This is the core reason context managers are preferable to scattered manual cleanup calls: the lifecycle boundary is explicit and failure-safe.

#### Key Concepts Reinforced
- `with` defines a resource-management boundary.
- `__enter__` prepares/returns the resource.
- `__exit__` performs cleanup and can suppress exceptions only deliberately.

#### Common Mistakes
- Putting cleanup after the `with` body.
- Returning `True` accidentally and hiding failures.
- Assuming cleanup is skipped when the body raises.

#### Production Connection
Files, locks, temporary state, and transaction-like resources benefit from deterministic lifecycle management.


### Question 4 — Choose Lazy or Eager Transformation

#### Difficulty
Basic

#### Topics Covered
- generator expressions
- comprehensions
- lazy evaluation
- materialization

#### Problem
You need the sum of squares of one million integers. Compare a list comprehension with a generator expression and choose the representation that matches the operation.

#### What You Need to Do
Write both versions, then identify which one materializes all intermediate values and which one produces values lazily. Use `sum()` to consume the generator.

#### How to Think About the Problem
Ask first whether the final consumer needs the whole collection. `sum()` can consume an iterable incrementally, so a generator expression avoids creating a million-element result list.

#### Solution
```python
n = 1_000_000

eager = [x * x for x in range(n)]
lazy = (x * x for x in range(n))

print(sum(lazy))
print(len(eager))
```

#### Solution Explanation
The list comprehension computes and stores every square immediately. The generator expression stores the recipe and produces each square as `sum()` requests it.

This is not a rule that generators are always faster. They can reduce peak memory for one-pass consumers, but the best choice depends on reuse, materialization needs, debugging needs, and workload characteristics.

#### Key Concepts Reinforced
- Comprehensions are eager materialization.
- Generator expressions are lazy.
- `sum()` can consume an iterable without requiring a list.

#### Common Mistakes
- Saying lazy always means faster.
- Using the generator twice and expecting it to restart.
- Materializing unnecessarily when only one aggregate is needed.

#### Production Connection
Large ETL and document-processing workloads often benefit from streaming transformations that avoid holding every intermediate record in memory.


### Question 5 — Accept Any Compatible Typed Processor

#### Difficulty
Basic

#### Topics Covered
- Protocol
- structural typing
- Callable
- type annotations

#### Problem
Two different classes both provide a `process(text: str) -> str` method. You want a function to accept either implementation without forcing them to inherit from the same base class.

#### What You Need to Do
Define a Protocol describing the required behavior and write a typed function that accepts any compatible object.

#### How to Think About the Problem
The requirement is behavioral rather than inheritance-based. A Protocol expresses the interface. The function should depend on the capability it needs, not on one concrete class.

#### Solution
```python
from typing import Protocol

class TextProcessor(Protocol):
    def process(self, text: str) -> str:
        ...

class UpperProcessor:
    def process(self, text: str) -> str:
        return text.upper()

class PrefixProcessor:
    def process(self, text: str) -> str:
        return "DOC: " + text

def run_processor(processor: TextProcessor, text: str) -> str:
    return processor.process(text)

print(run_processor(UpperProcessor(), "hello"))
print(run_processor(PrefixProcessor(), "hello"))
```

#### Solution Explanation
`TextProcessor` is a structural contract. Neither concrete class needs to inherit from it. Static type checkers can verify compatibility based on the method signature.

This makes APIs extensible while keeping the implementation decoupled from concrete classes.

#### Key Concepts Reinforced
- Protocols express structural typing.
- Type hints document interfaces.
- Consumers should depend on required behavior.

#### Common Mistakes
- Adding unnecessary inheritance just to satisfy typing.
- Using `Any` and losing the contract.
- Assuming a Protocol automatically validates every runtime value.

#### Production Connection
Typed interfaces are useful at AI pipeline boundaries such as document processors, embedding adapters, and model-provider adapters.


### Question 6 — Model a Small Workflow with Enum States

#### Difficulty
Basic

#### Topics Covered
- Enum
- state machines
- transitions
- invalid states

#### Problem
A document can be `PENDING`, `PROCESSING`, `COMPLETED`, or `FAILED`. An invalid transition should raise an error rather than silently corrupting workflow state.

#### What You Need to Do
Define an Enum and a transition table. Implement a `transition` function that accepts the current state and an event, returning the next state or raising `ValueError`.

#### How to Think About the Problem
Represent states separately from events, then define the legal edges explicitly. This is safer than scattering string comparisons across the application.

#### Solution
```python
from enum import Enum

class State(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

TRANSITIONS = {
    (State.PENDING, "start"): State.PROCESSING,
    (State.PROCESSING, "success"): State.COMPLETED,
    (State.PROCESSING, "fail"): State.FAILED,
}

def transition(current: State, event: str) -> State:
    try:
        return TRANSITIONS[(current, event)]
    except KeyError as exc:
        raise ValueError(f"invalid transition: {current.value} + {event}") from exc

state = State.PENDING
state = transition(state, "start")
state = transition(state, "success")

print(state)
```

#### Solution Explanation
The Enum gives the state machine a controlled vocabulary. The transition table defines only valid edges, so an unsupported event/state combination fails explicitly.

A transition table is often easier to inspect and test than deeply nested conditionals.

#### Key Concepts Reinforced
- Enums prevent magic-value drift.
- State machines define explicit transitions.
- Invalid transitions should be observable and testable.

#### Common Mistakes
- Using arbitrary strings everywhere.
- Allowing any state change.
- Confusing an enum member with its `.value`.

#### Production Connection
Workflow state machines appear in document processing, agent execution, evaluation jobs, and asynchronous processing pipelines.


### Question 7 — Normalize an Event Timestamp to UTC

#### Difficulty
Basic

#### Topics Covered
- datetime
- timezone-aware datetime
- UTC
- ZoneInfo
- astimezone

#### Problem
An event arrives with a timezone-aware timestamp in a regional timezone. The system needs a UTC representation for storage and comparison.

#### What You Need to Do
Parse an ISO timestamp, convert it to UTC, and print both the original and normalized representation.

#### How to Think About the Problem
First make sure the parsed value is aware. Then use `astimezone()` to convert the same instant to UTC. Do not use `replace(tzinfo=...)` to perform a conversion; that changes the attached timezone metadata rather than converting the instant.

#### Solution
```python
from datetime import datetime, timezone

event_time = datetime.fromisoformat("2026-09-24T14:30:00+05:30")
utc_time = event_time.astimezone(timezone.utc)

print(event_time)
print(utc_time)
print(utc_time.tzinfo)
```

#### Solution Explanation
The input includes an explicit `+05:30` offset, so it is timezone-aware. `astimezone(timezone.utc)` computes the equivalent instant in UTC.

The production rule is to choose one canonical internal representation and convert at system boundaries. UTC is commonly used for storage, event comparison, and interoperating between services.

#### Key Concepts Reinforced
- Naive vs aware datetimes.
- `astimezone()` converts an instant.
- UTC provides a canonical reference.

#### Common Mistakes
- Using `replace(tzinfo=timezone.utc)` as a conversion.
- Mixing naive and aware datetimes.
- Dropping timezone information during serialization.

#### Production Connection
Timestamp normalization is fundamental for AI job scheduling, event logs, model evaluation records, and distributed processing.


### Question 8 — Count Failures and Find the Most Common Category

#### Difficulty
Basic

#### Topics Covered
- Counter
- counting
- most_common
- missing-key behavior

#### Problem
You collect validation outcomes from document processing. You need frequency counts and the top two failure categories.

#### What You Need to Do
Use `Counter` to count the events, demonstrate the special missing-key behavior, and retrieve the top two categories.

#### How to Think About the Problem
This is a frequency-counting problem, which is exactly the semantic job that `Counter` communicates. The missing-key result is `0`, unlike a normal dict lookup.

#### Solution
```python
from collections import Counter

events = ["missing_id", "invalid_email", "missing_id", "missing_id", "invalid_email"]
counts = Counter(events)

print(counts["missing_id"])
print(counts["unknown"])
print(counts.most_common(2))
```

#### Solution Explanation
`Counter(events)` stores an element-to-count mapping. `counts["unknown"]` returns `0` because a missing count is treated as zero. `most_common(2)` returns the two highest-frequency entries as `(element, count)` pairs.

#### Key Concepts Reinforced
- `Counter(iterable)` counts elements.
- Missing Counter keys return zero.
- `most_common(n)` supports top-N analysis.

#### Common Mistakes
- Expecting `KeyError` for a missing count.
- Treating `Counter.update()` like `dict.update()`.
- Assuming every counting problem needs manual dictionary initialization.

#### Production Connection
Frequency analysis is useful for validation failures, HTTP status distributions, model prediction labels, and AI tool-call outcomes.


### Question 9 — Memoize a Deterministic Function

#### Difficulty
Basic

#### Topics Covered
- functools.cache
- memoization
- cache hits
- hashable arguments

#### Problem
A recursive Fibonacci implementation recalculates the same subproblems repeatedly. Add memoization without building a custom cache dictionary.

#### What You Need to Do
Use `@cache`, call the function repeatedly, and clear the cache before a final run.

#### How to Think About the Problem
The function is deterministic: the same integer input always produces the same result. Integer arguments are hashable, so they can serve as cache keys. `@cache` stores results for reuse.

#### Solution
```python
from functools import cache

@cache
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(fibonacci(20))

fibonacci.cache_clear()
print(fibonacci(10))
```

#### Solution Explanation
The first evaluation populates the cache. Recursive calls that revisit an already-computed `n` become cache hits instead of repeating the recursion.

`cache_clear()` resets the memoized state, which is useful in tests and when cached values must be intentionally discarded.

#### Key Concepts Reinforced
- Memoization stores results by arguments.
- `@cache` is unbounded.
- Arguments used as cache keys must be hashable.
- Caches have state and a lifetime.

#### Common Mistakes
- Caching a function with side effects.
- Passing a list to a cached function.
- Assuming `cache` supplies TTL or distributed sharing.

#### Production Connection
Memoization is useful for deterministic parsing, repeated configuration computation, and other expensive pure transformations. External or time-sensitive data requires a separate freshness strategy.


### Question 10 — Explain Aliasing Without Copying

#### Difficulty
Basic

#### Topics Covered
- object identity
- references
- assignment
- mutation
- is

#### Problem
A developer expects `b = a` to make an independent list. Predict the output and explain why mutating one name changes what the other name observes.

#### What You Need to Do
Write a program that demonstrates aliasing, then create an independent top-level copy and verify the identity difference.

#### How to Think About the Problem
Assignment binds another name to the same object. Mutation changes the shared object's state. A shallow copy creates a distinct outer container, which is enough for a flat list of immutable values.

#### Solution
```python
import copy

a = [1, 2]
b = a

a.append(3)

print(a)
print(b)
print(a is b)

c = copy.copy(a)
c.append(4)

print(a)
print(c)
print(a is c)
```

#### Solution Explanation
After `b = a`, both names refer to the same list, so `a.append(3)` is visible through `b`. `copy.copy(a)` creates a different outer list; changes to `c` no longer mutate `a`.

This distinction matters before choosing shallow or deep copy: first ask whether you need another object or another reference.

#### Key Concepts Reinforced
- Names refer to objects.
- Assignment is binding, not copying.
- `is` checks identity.
- Shallow copy creates a new outer container.

#### Common Mistakes
- Using `is` to compare values.
- Assuming every assignment copies.
- Using `deepcopy()` automatically for every mutation concern.

#### Production Connection
Aliasing bugs are common when batches, configuration objects, agent state, and shared in-memory data structures are reused across processing stages.


### Question 11 — Run Two Independent I/O Tasks Concurrently

#### Difficulty
Basic

#### Topics Covered
- concurrency
- asyncio
- coroutines
- tasks
- event loop

#### Problem
Two independent operations each need one second of simulated I/O waiting. The program should allow their waiting periods to overlap.

#### What You Need to Do
Write an async program that creates two tasks, waits for both, and reports their results. Explain why this demonstrates concurrency rather than CPU parallelism.

#### How to Think About the Problem
Define the operations as coroutine functions, schedule them as Tasks, and let the event loop switch between them while they are awaiting. `asyncio.sleep()` simulates non-blocking waiting.

#### Solution
```python
import asyncio

async def fetch(name: str) -> str:
    await asyncio.sleep(1)
    return f"{name} complete"

async def main() -> None:
    task_a = asyncio.create_task(fetch("A"))
    task_b = asyncio.create_task(fetch("B"))

    results = await asyncio.gather(task_a, task_b)
    print(results)

asyncio.run(main())
```

#### Solution Explanation
Calling `create_task()` schedules both coroutine objects. While one task is suspended at `await asyncio.sleep(1)`, the event loop can progress the other task. `gather()` waits for both results.

No CPU-heavy computation is being parallelized here. The example demonstrates overlapping I/O-style waiting through asynchronous concurrency.

#### Key Concepts Reinforced
- Concurrency is not automatically parallelism.
- A coroutine can be scheduled as a Task.
- `asyncio.run()` manages the top-level event loop.
- `await` cooperatively suspends the current coroutine.

#### Common Mistakes
- Calling `fetch()` and expecting immediate execution.
- Using `time.sleep()` inside the coroutine and blocking the event loop.
- Assuming async code automatically uses multiple CPU cores.

#### Production Connection
This pattern maps directly to independent LLM, embedding, search, storage, or metadata API calls when their service limits and dependencies allow concurrent requests.


# Part II — Moderate Questions

### Question 12 — Identify the Blocking Call in an Async Function

#### Difficulty
Moderate

#### Topics Covered
- asyncio
- blocking vs awaiting
- event loop
- concurrency

#### Problem
An asynchronous function calls `time.sleep(1)`. Two tasks are created, but the program behaves almost sequentially. Identify and fix the problem.

#### What You Need to Do
Replace the blocking sleep with the cooperative async equivalent and explain why the event loop can then make progress on another task.

#### How to Think About the Problem
Look for operations that hold the event-loop thread while waiting. `time.sleep()` blocks the thread; `await asyncio.sleep()` suspends the coroutine and gives the event loop an opportunity to run other tasks.

#### Solution
```python
import asyncio

async def fetch(name: str) -> str:
    await asyncio.sleep(1)
    return f"{name} complete"

async def main() -> None:
    results = await asyncio.gather(
        fetch("A"),
        fetch("B"),
    )
    print(results)

asyncio.run(main())
```

#### Solution Explanation
The corrected function has no blocking sleep. Each task reaches `await asyncio.sleep(1)`, suspends, and allows other scheduled tasks to progress.

The important mental model is not "async is faster." It is "the event loop can use otherwise-idle waiting time to make progress on other coroutines.

#### Key Concepts Reinforced
- Blocking is different from awaiting.
- The event loop coordinates cooperative progress.
- Async is especially useful for I/O-bound workloads.

#### Common Mistakes
- Using blocking I/O inside the event loop.
- Assuming every synchronous library call becomes non-blocking just because it is inside `async def`.
- Equating concurrency with parallel CPU execution.

#### Production Connection
An AI service can accidentally serialize thousands of requests if a blocking client or `time.sleep()` runs in its event loop. Recognizing the blocking boundary is an operational skill.


### Question 13 — Stream Data Through a Context-Managed Generator

#### Difficulty
Moderate

#### Topics Covered
- generators
- context managers
- lazy evaluation
- resource lifetime

#### Problem
You need to process many lines from a resource without loading the entire input into memory. The resource must still close deterministically.

#### What You Need to Do
Create a context manager that exposes a generator-like iteration interface and process the values one at a time.

#### How to Think About the Problem
Separate two concerns: the context manager owns the resource lifetime; the generator controls how values are produced. Keep the stream lazy and the cleanup deterministic.

#### Solution
```python
from contextlib import contextmanager

@contextmanager
def open_lines(lines):
    try:
        yield (line.strip() for line in lines)
    finally:
        print("resource closed")

with open_lines(["a", "b", "c"]) as stream:
    for line in stream:
        print(line)
```

#### Solution Explanation
The generator expression yields one normalized line at a time. The `with` block establishes the lifetime boundary and the `finally` in the context manager guarantees cleanup.

This combination is powerful: laziness controls memory, while the context manager controls the lifetime of the resource that produces the stream.

#### Key Concepts Reinforced
- Generators provide lazy production.
- Context managers provide deterministic lifecycle handling.
- Composition matters when processing large inputs.

#### Common Mistakes
- Reading all records into a list first.
- Letting the resource outlive the context manager accidentally.
- Confusing generator exhaustion with resource cleanup.

#### Production Connection
Large document or log pipelines commonly combine streaming iteration with deterministic cleanup so memory and external resources remain bounded.


### Question 14 — Build a Typed Decorator That Preserves the Callable Contract

#### Difficulty
Moderate

#### Topics Covered
- typing
- ParamSpec
- TypeVar
- decorators
- wraps

#### Problem
You want a timing/logging decorator that preserves the decorated function's parameter and return-type relationship for a static type checker.

#### What You Need to Do
Use `ParamSpec` and `TypeVar` so the decorator accepts an arbitrary callable and returns a callable with the same signature. Preserve runtime metadata as well.

#### How to Think About the Problem
The decorator transforms behavior without intentionally changing the callable contract. `ParamSpec` captures the parameter list, while `TypeVar` captures the return type. `wraps` handles runtime metadata.

#### Solution
```python
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def trace(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@trace
def multiply(a: int, b: int) -> int:
    return a * b

print(multiply(3, 4))
```

#### Solution Explanation
`Callable[P, R]` says: accept some callable whose parameters are represented by `P` and whose result is `R`. The wrapper forwards exactly those captured parameters and returns `R`.

This is stronger than typing the decorator as `Callable[..., Any]`, because the latter loses useful information.

#### Key Concepts Reinforced
- `ParamSpec` captures callable parameters.
- `TypeVar` captures a reusable type relationship.
- `wraps` preserves runtime metadata.
- Static typing and runtime behavior solve different problems.

#### Common Mistakes
- Using `Any` everywhere.
- Changing the wrapper signature accidentally.
- Expecting type hints to validate runtime arguments automatically.

#### Production Connection
Typed decorators are useful for instrumentation layers around model clients, tool handlers, preprocessing functions, and other reusable application callables.


### Question 15 — Validate a Typed State Transition Boundary

#### Difficulty
Moderate

#### Topics Covered
- Enum
- state machines
- Protocol
- typing
- transition logic

#### Problem
You want a typed workflow engine where events can be handled by a state-transition object without hard-coding one concrete implementation.

#### What You Need to Do
Define an Enum for states, a Protocol for a transition handler, and a small implementation that rejects invalid transitions.

#### How to Think About the Problem
The Enum controls the vocabulary of valid states. The Protocol expresses what the caller needs from a handler. Keep transition validation in one place so invalid state changes cannot silently propagate.

#### Solution
```python
from enum import Enum
from typing import Protocol

class State(Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"

class TransitionHandler(Protocol):
    def next_state(self, current: State, event: str) -> State:
        ...

class BasicHandler:
    def next_state(self, current: State, event: str) -> State:
        allowed = {
            (State.PENDING, "start"): State.RUNNING,
            (State.RUNNING, "finish"): State.DONE,
        }
        try:
            return allowed[(current, event)]
        except KeyError as exc:
            raise ValueError("invalid transition") from exc

def advance(handler: TransitionHandler, state: State, event: str) -> State:
    return handler.next_state(state, event)

state = advance(BasicHandler(), State.PENDING, "start")
print(state)
```

#### Solution Explanation
The Enum controls the vocabulary of valid states. The Protocol expresses what the caller needs from a handler. The transition table defines the legal state/event combinations.

This separates workflow semantics from the concrete implementation and gives static tools a clear boundary.

#### Key Concepts Reinforced
- Enum as controlled state vocabulary.
- Protocol as a structural contract.
- Transition tables as explicit workflow rules.

#### Common Mistakes
- Using unrestricted strings for states.
- Making the Protocol depend on a concrete implementation.
- Allowing invalid transitions and fixing them downstream.

#### Production Connection
Typed workflow boundaries are useful for document processing, agent execution, evaluation jobs, and other stateful AI systems.


### Question 16 — Group a Stream and Count Its Failures

#### Difficulty
Moderate

#### Topics Covered
- defaultdict
- Counter
- generators
- stream processing

#### Problem
A generator emits validation records such as `{"category": ..., "status": ...}`. You need per-category totals and a global count of failures without materializing all records.

#### What You Need to Do
Consume the generator once, group records with `defaultdict`, and count failure statuses with `Counter`.

#### How to Think About the Problem
Because the input is a one-shot stream, do all required aggregation during one pass. `defaultdict(list)` is useful if you actually need grouped records; if you only need counts per group, a nested counting structure may use less memory.

#### Solution
```python
from collections import Counter, defaultdict

def records():
    yield {"category": "email", "status": "ok"}
    yield {"category": "email", "status": "fail"}
    yield {"category": "id", "status": "fail"}

groups = defaultdict(list)
failures = Counter()

for record in records():
    groups[record["category"]].append(record)
    if record["status"] == "fail":
        failures[record["category"]] += 1

print(dict(groups))
print(failures)
```

#### Solution Explanation
The generator produces records lazily. The loop consumes each record exactly once. `defaultdict(list)` avoids repeated missing-key checks; `Counter` expresses the global frequency of failures.

The important trade-off is memory: storing the complete grouped records defeats some streaming benefits. A production design should store only what downstream logic actually requires.

#### Key Concepts Reinforced
- One-pass streaming.
- Automatic grouping with `defaultdict`.
- Frequency analysis with `Counter`.
- Memory depends on what you retain.

#### Common Mistakes
- Attempting to iterate the generator twice.
- Grouping every record when only counts are needed.
- Treating `defaultdict` as a persistence layer.

#### Production Connection
This pattern appears in ingestion validation, event aggregation, data-quality monitoring, and AI preprocessing pipelines.


### Question 17 — Expire a Job Using an Aware Datetime

#### Difficulty
Moderate

#### Topics Covered
- datetime
- timezone-aware values
- timedelta
- Enum state

#### Problem
A job is valid for 30 minutes after creation. Its state is `PENDING` until checked. The system must mark it `EXPIRED` when the deadline has passed, using timezone-aware timestamps.

#### What You Need to Do
Define an Enum for the job state, calculate an aware deadline from the creation timestamp, and implement an expiration check.

#### How to Think About the Problem
Use one time basis for both creation and comparison. The simplest safe rule is to store aware UTC datetimes and compare them with an aware UTC `now`.

#### Solution
```python
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum

class JobState(Enum):
    PENDING = "pending"
    EXPIRED = "expired"

@dataclass
class Job:
    created_at: datetime
    state: JobState = JobState.PENDING

    @property
    def deadline(self) -> datetime:
        return self.created_at + timedelta(minutes=30)

    def refresh(self, now: datetime) -> None:
        if now > self.deadline:
            self.state = JobState.EXPIRED

created = datetime.now(timezone.utc)
job = Job(created_at=created)

job.refresh(created + timedelta(minutes=31))
print(job.state)
```

#### Solution Explanation
The deadline is derived from an aware UTC creation time. The comparison uses another aware UTC value, avoiding naive/aware comparison errors.

The Enum keeps the lifecycle state explicit. In a larger state machine, expiration would be one legal event or transition rather than a free-form assignment.

#### Key Concepts Reinforced
- Aware datetime comparisons.
- `timedelta` for duration arithmetic.
- Enums for explicit state.
- UTC as a canonical internal representation.

#### Common Mistakes
- Comparing aware and naive datetimes.
- Storing a local wall-clock time and treating it as UTC.
- Encoding state as arbitrary strings.

#### Production Connection
AI job queues, evaluation runs, agent deadlines, and model-processing jobs need explicit time semantics to avoid incorrect expiration behavior.


### Question 18 — Measure Whether a Cache Is Actually Helping

#### Difficulty
Moderate

#### Topics Covered
- lru_cache
- cache_info
- hit/miss behavior
- memoization

#### Problem
A deterministic function is expensive, but you do not know whether callers repeat inputs often enough to justify caching. Add a bounded cache and inspect its metrics.

#### What You Need to Do
Use `lru_cache(maxsize=3)`, call the function with repeated and unique inputs, and inspect `cache_info()`.

#### How to Think About the Problem
A cache is an optimization hypothesis. Test it by creating a workload with repeated keys, then inspect hits, misses, current size, and configured capacity.

#### Solution
```python
from functools import lru_cache

@lru_cache(maxsize=3)
def square(x: int) -> int:
    return x * x

for value in [1, 2, 3, 1, 2, 4, 1]:
    square(value)

print(square.cache_info())
print(square.cache_parameters())
```

#### Solution Explanation
`cache_info()` reports cache behavior including hits, misses, maximum size, and current size. `cache_parameters()` exposes configuration such as `maxsize` and `typed`.

This is preferable to claiming that caching is beneficial without measuring the actual input distribution.

#### Key Concepts Reinforced
- Bounded caching.
- LRU eviction capacity.
- `cache_info()` for observability.
- `cache_parameters()` for configuration introspection.

#### Common Mistakes
- Benchmarking only a warm cache.
- Assuming a high cache size is always better.
- Ignoring memory or stale-data considerations.

#### Production Connection
In an AI service, cache metrics help determine whether repeated parsing, metadata, embedding preparation, or deterministic computation is actually reusable.


### Question 19 — Fix a Nested Copy Bug

#### Difficulty
Moderate

#### Topics Covered
- shallow copy
- deep copy
- nested mutable objects
- object graphs

#### Problem
A template contains nested lists. Two jobs should start from independent nested data, but changing one job currently changes the other.

#### What You Need to Do
Demonstrate why a shallow copy is insufficient and repair the implementation with `deepcopy`.

#### How to Think About the Problem
The outer dictionary can be copied while its nested list remains shared. When the requirement is an independent nested object graph, `deepcopy()` recursively copies supported nested objects and tracks shared references/cycles during the operation.

#### Solution
```python
from copy import copy, deepcopy

template = {
    "tags": ["ai", "python"],
    "options": {"retries": 3},
}

job_a = copy(template)
job_a["tags"].append("production")
print(template["tags"])

job_b = deepcopy(template)
job_b["tags"].append("streaming")
job_b["options"]["retries"] = 5

print(template)
print(job_b)
```

#### Solution Explanation
After `copy(template)`, `job_a["tags"]` refers to the same nested list as `template["tags"]`, so the mutation leaks back.

`deepcopy()` creates an independent nested graph, so later mutations in `job_b` do not change the original. It is more expensive and can have custom-class semantics, so it should be used only when an independent object graph is really required.

#### Key Concepts Reinforced
- Shallow copy duplicates only the outer container.
- `deepcopy()` recursively copies nested objects.
- Copying is a semantic decision, not just a safety reflex.

#### Common Mistakes
- Thinking `copy()` is recursively independent.
- Using `deepcopy()` on very large graphs without measuring cost.
- Ignoring custom object copy behavior.

#### Production Connection
Nested request state, configuration templates, and agent session objects can accidentally share mutable state if ownership boundaries are unclear.


### Question 20 — Maintain a Sliding Window of Recent Events

#### Difficulty
Moderate

#### Topics Covered
- deque
- maxlen
- sliding windows
- Counter

#### Problem
An inference monitor only needs the most recent five status values. Older values should disappear automatically.

#### What You Need to Do
Use a bounded `deque` and maintain a `Counter` from the current window when statistics are needed.

#### How to Think About the Problem
`deque(maxlen=5)` expresses the retention policy directly. The oldest element is automatically discarded when a sixth element arrives. Because the window changes over time, derive its current statistics from its current contents rather than keeping stale counts without updating them.

#### Solution
```python
from collections import Counter, deque

window = deque(maxlen=5)

for status in ["ok", "fail", "ok", "timeout", "ok", "fail"]:
    window.append(status)

counts = Counter(window)

print(list(window))
print(counts)
```

#### Solution Explanation
After six appends, only the latest five values remain. `Counter(window)` computes the frequency distribution of the retained window.

This example favors correctness and clarity. For extremely high-rate workloads, maintaining incremental counts can reduce repeated scans, but then the code must correctly decrement the value removed from the left.

#### Key Concepts Reinforced
- Bounded buffers.
- `deque(maxlen=...)`.
- Sliding-window statistics.
- Memory can be intentionally bounded.

#### Common Mistakes
- Expecting six values after six appends.
- Forgetting that maxlen discards old data.
- Maintaining a second counter without accounting for evictions.

#### Production Connection
Sliding windows are useful for recent inference failures, latency monitoring, recent agent actions, and bounded event histories.


### Question 21 — Use partial for a Callable and partialmethod for a Class Method

#### Difficulty
Moderate

#### Topics Covered
- functools.partial
- partialmethod
- partial arguments
- callbacks
- method binding

#### Problem
An existing function needs fixed production configuration, and a class needs a convenient method that fixes one argument of another method.

#### What You Need to Do
Use `partial` for the free function and `partialmethod` inside the class. Show the resulting calls and explain why normal `partial()` is not the same tool inside a class definition.

#### How to Think About the Problem
`partial` adapts an arbitrary callable by storing fixed arguments. `partialmethod` is designed for methods so normal instance binding remains part of the method call.

#### Solution
```python
from functools import partial, partialmethod

def process_record(record: dict, mode: str, strict: bool) -> str:
    suffix = "strict" if strict else "relaxed"
    return f"{mode}:{suffix}:{record['id']}"

production_processor = partial(
    process_record,
    mode="production",
    strict=True,
)

class Greeter:
    def greet(self, greeting: str, name: str) -> str:
        return f"{greeting}, {name}"

    say_hello = partialmethod(greet, "Hello")

print(production_processor({"id": "a"}))
print(Greeter().say_hello("Alice"))
```

#### Solution Explanation
The first partial stores `mode="production"` and `strict=True`, leaving `record` for the caller.

Inside `Greeter`, `partialmethod` prepares the `greeting` argument while preserving normal method binding for `self`. This is why `Greeter().say_hello("Alice")` works naturally.

#### Key Concepts Reinforced
- Partial application.
- Pre-filled positional/keyword arguments.
- `partialmethod` for method-oriented adaptation.
- Descriptor/method binding distinction.

#### Common Mistakes
- Using `partial` where `partialmethod` is the clearer class-level tool.
- Trying to pre-bind `self` manually.
- Using partial when a named wrapper or richer configuration object would be clearer.

#### Production Connection
These tools can adapt processing callbacks and class behaviors, but complex configuration or business logic is often clearer in a named function or configuration object.


### Question 22 — Inspect a Task's Lifecycle Without Blocking on a Result Too Early

#### Difficulty
Moderate

#### Topics Covered
- asyncio.Task
- done()
- result()
- task lifecycle

#### Problem
You create an async task that finishes later. You want to inspect whether it is complete without calling `result()` prematurely.

#### What You Need to Do
Write an async program that creates a task, checks `done()`, awaits the task, and then safely reads the result.

#### How to Think About the Problem
`result()` is for completed tasks; before completion it can raise an invalid-state condition. The reliable pattern is to await the task when you need completion, then inspect the result.

#### Solution
```python
import asyncio

async def work() -> int:
    await asyncio.sleep(0)
    return 42

async def main() -> None:
    task = asyncio.create_task(work())

    print("done before await:", task.done())

    result = await task
    print("done after await:", task.done())
    print("result:", result)

asyncio.run(main())
```

#### Solution Explanation
Immediately after scheduling, the task may not have completed. Awaiting the task establishes the completion boundary. After the await returns, `done()` is true and the result is available.

A Task is an application-level scheduling object built around an awaitable. This differs from thinking of the coroutine object itself as already running.

#### Key Concepts Reinforced
- Coroutine vs Task.
- Task lifecycle.
- `done()` and `result()`.
- The event loop schedules Tasks.

#### Common Mistakes
- Calling `result()` before completion.
- Assuming `create_task()` blocks until completion.
- Confusing coroutine creation with task scheduling.

#### Production Connection
Task lifecycle reasoning is important for agent orchestration, concurrent tool calls, and asynchronous AI pipelines.


# Part III — Hard Questions

### Question 23 — Diagnose a Memory-Heavy Streaming Refactor

#### Difficulty
Hard

#### Topics Covered
- generators
- materialization
- tracemalloc
- memory trade-offs

#### Problem
A document pipeline changed from a generator expression to a list comprehension because the list was convenient. Peak memory increased dramatically. The final operation only needs a single aggregate.

#### What You Need to Do
Refactor the pipeline to stay lazy and show how `tracemalloc` can compare traced memory before and after processing.

#### How to Think About the Problem
First identify whether the consumer requires random access or repeated traversal. If it only needs an aggregate, keep the transformation lazy. Then measure rather than relying on intuition about memory.

#### Solution
```python
import tracemalloc

def values():
    for number in range(100_000):
        yield number * number

tracemalloc.start()

result = sum(values())

current, peak = tracemalloc.get_traced_memory()
print("result:", result)
print("current:", current)
print("peak:", peak)

tracemalloc.stop()
```

#### Solution Explanation
`values()` yields one value at a time, so `sum()` does not need a full materialized list. `tracemalloc` tracks Python memory allocations during the traced interval; it is useful for comparing code paths but does not represent every native allocation in a whole process.

A correct optimization starts by identifying the lifetime and retention of intermediate objects, then measuring the effect of the refactor.

#### Key Concepts Reinforced
- Lazy streaming can reduce intermediate materialization.
- `tracemalloc` measures traced Python allocations.
- Peak memory and final result size are different concerns.

#### Common Mistakes
- Assuming `sys.getsizeof()` tells the full memory cost.
- Using `list(...)` just for convenience.
- Claiming a generator always uses less total memory in every workload.

#### Production Connection
This is directly relevant to large document, token, and event pipelines where materializing intermediate collections can create avoidable memory pressure.


### Question 24 — Repair a Decorator-Order Bug

#### Difficulty
Hard

#### Topics Covered
- decorators
- decorator order
- wraps
- introspection

#### Problem
Two decorators are stacked: one logs calls and one changes a function's behavior. A test expects the outer layer to see the original function name, but the metadata is missing and the log order is surprising.

#### What You Need to Do
Fix the decorators so each layer preserves metadata, then explain the order in which the decorators are applied and executed.

#### How to Think About the Problem
Remember that stacked decorators apply from the closest decorator to the function outward, while calls pass through the outer wrapper first. Use `wraps` in every wrapper so introspection survives the stack.

#### Solution
```python
from functools import wraps

def log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("log-before")
        result = func(*args, **kwargs)
        print("log-after")
        return result
    return wrapper

def double_result(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return 2 * func(*args, **kwargs)
    return wrapper

@log
@double_result
def compute(x: int) -> int:
    """Return the input."""
    return x

print(compute(5))
print(compute.__name__)
```

#### Solution Explanation
Python interprets the stack conceptually as `compute = log(double_result(compute))`. A call first enters `log`'s wrapper, then calls the `double_result` wrapper, which finally calls the original `compute`.

Without `wraps` on either wrapper, metadata such as `__name__` and `__doc__` would describe the outer wrapper rather than the original function. The order is part of the program's semantics, so decorators should be stacked deliberately.

#### Key Concepts Reinforced
- Decorator application order.
- Runtime call order.
- `functools.wraps` at every wrapper layer.
- Introspection can expose composition mistakes.

#### Common Mistakes
- Reading stacked decorators top-to-bottom as execution order.
- Using `wraps` on only one layer.
- Assuming decorator order is cosmetic.

#### Production Connection
Instrumentation, retries, authorization checks, caching, and logging can interact through decorator order. Production code should document non-obvious stacks.


### Question 25 — Use ExitStack for Dynamically Chosen Resources

#### Difficulty
Hard

#### Topics Covered
- contextlib.ExitStack
- context managers
- cleanup
- dynamic resources

#### Problem
A workflow receives a variable number of resource-like context managers. You cannot easily write one fixed `with` statement because the number of resources is determined at runtime.

#### What You Need to Do
Use `ExitStack` to enter all resources and guarantee that every entered context is exited even if later setup or processing fails.

#### How to Think About the Problem
The important idea is dynamic resource ownership. `ExitStack` becomes the single lifecycle boundary that records entered contexts and unwinds them in reverse order.

#### Solution
```python
from contextlib import ExitStack, contextmanager

@contextmanager
def resource(name: str):
    print(f"open {name}")
    try:
        yield name
    finally:
        print(f"close {name}")

names = ["A", "B", "C"]

with ExitStack() as stack:
    resources = [stack.enter_context(resource(name)) for name in names]
    print("using:", resources)
```

#### Solution Explanation
Each call to `enter_context()` enters a context and registers its cleanup with the stack. When the outer `with ExitStack()` exits, the contexts are unwound in reverse order.

This is exactly the sort of lifecycle management that becomes difficult to express with manual `try/finally` blocks when resources are dynamic.

#### Key Concepts Reinforced
- Dynamic context management.
- Deterministic cleanup.
- Reverse-order unwinding.
- `ExitStack` as a lifecycle coordinator.

#### Common Mistakes
- Entering resources without registering cleanup.
- Assuming cleanup order is arbitrary.
- Replacing deterministic cleanup with a list of `close()` calls that may be skipped on failure.

#### Production Connection
Batch processors, plugin systems, and configurable document workflows sometimes need to acquire a dynamic set of resources safely.


### Question 26 — Design a Generic Typed Repository with a Structural Contract

#### Difficulty
Hard

#### Topics Covered
- TypeVar
- Generic
- Protocol
- TypedDict
- Literal
- type safety

#### Problem
You want a reusable in-memory repository boundary. Records have a fixed identifier and a constrained status vocabulary, while the repository should remain generic over the value type.

#### What You Need to Do
Define a typed record shape using `TypedDict`, use `Literal` for the status field, define a generic Protocol and implementation, and demonstrate storing one record.

#### How to Think About the Problem
Separate the record's static shape from the repository's generic behavior. `TypedDict` documents dictionary structure, `Literal` constrains known values, and `TypeVar` connects the repository's stored type. The Protocol expresses the consumer-facing interface.

#### Solution
```python
from typing import Generic, Literal, Protocol, TypeVar, TypedDict

Status = Literal["ready", "failed"]

class Record(TypedDict):
    id: str
    status: Status

T = TypeVar("T")

class Repository(Protocol[T]):
    def put(self, key: str, value: T) -> None:
        ...
    def get(self, key: str) -> T | None:
        ...

class MemoryRepository(Generic[T]):
    def __init__(self) -> None:
        self._data: dict[str, T] = {}

    def put(self, key: str, value: T) -> None:
        self._data[key] = value

    def get(self, key: str) -> T | None:
        return self._data.get(key)

repo: Repository[Record] = MemoryRepository()
repo.put("doc-1", {"id": "doc-1", "status": "ready"})

print(repo.get("doc-1"))
```

#### Solution Explanation
`Record` describes the expected keys and value types for a dictionary-like record. `Status` prevents an arbitrary string from being the intended status at static-analysis time. `Repository[T]` keeps the value type consistent across `put()` and `get()`.

The runtime repository still stores ordinary dictionaries. Typing provides an explicit contract to developers and static tools; it does not itself perform full runtime validation.

#### Key Concepts Reinforced
- `TypedDict` for dictionary-shaped contracts.
- `Literal` for constrained values.
- Generic type parameters preserve relationships.
- Protocols define structural interfaces.

#### Common Mistakes
- Confusing `TypedDict` with a runtime model validator.
- Replacing the generic type with `Any`.
- Using one concrete record class when the repository should remain reusable.

#### Production Connection
Typed storage boundaries are valuable around document metadata, model artifacts, evaluation records, and tool outputs.


### Question 27 — Make a Time-Aware State Transition

#### Difficulty
Hard

#### Topics Covered
- Enum
- state machine
- datetime
- timezone
- timedelta

#### Problem
A job enters `RUNNING` and must automatically become `TIMED_OUT` after five minutes. The transition must only occur from `RUNNING` and must use aware UTC timestamps.

#### What You Need to Do
Implement a job state Enum, store a deadline, and provide a method that performs only the valid timeout transition.

#### How to Think About the Problem
Treat timeout as a state-machine transition with a time-based guard. Keep the deadline as an aware UTC datetime. Do not mutate unrelated states when the guard is false.

#### Solution
```python
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum

class State(Enum):
    RUNNING = "running"
    TIMED_OUT = "timed_out"
    COMPLETED = "completed"

@dataclass
class Job:
    state: State
    deadline: datetime

    def refresh(self, now: datetime) -> None:
        if self.state is State.RUNNING and now >= self.deadline:
            self.state = State.TIMED_OUT

started = datetime.now(timezone.utc)
job = Job(State.RUNNING, started + timedelta(minutes=5))

job.refresh(started + timedelta(minutes=5))
print(job.state)
```

#### Solution Explanation
The guard checks both the current state and the deadline. If the job is already `COMPLETED`, the timeout logic cannot incorrectly overwrite it.

This is an important production pattern: time itself is not the state transition. A timestamp supplies a guard; the state machine still determines whether the transition is legal.

#### Key Concepts Reinforced
- State-machine guards.
- Aware UTC timestamps.
- Duration arithmetic with `timedelta`.
- Explicit lifecycle states.

#### Common Mistakes
- Letting any state become timed out.
- Using local wall-clock strings for comparison.
- Treating a deadline as a duration that can be recomputed differently in different timezones.

#### Production Connection
AI jobs, agent tasks, and evaluation runs often have deadlines. Explicit state plus explicit time semantics makes timeout behavior auditable.


### Question 28 — Aggregate Model Outcomes with Counter and defaultdict

#### Difficulty
Hard

#### Topics Covered
- Counter
- defaultdict
- arithmetic
- grouping
- data processing

#### Problem
You have event counts for two batches of model outcomes. You need combined counts, common outcomes, and model-level grouping of the raw events.

#### What You Need to Do
Use `Counter` for frequency arithmetic and `defaultdict(list)` for grouping raw events by model.

#### How to Think About the Problem
Use each structure for the semantic problem it expresses. Counter arithmetic is appropriate for aggregate counts; defaultdict handles grouped collection initialization.

#### Solution
```python
from collections import Counter, defaultdict

batch_a = Counter({"ok": 8, "error": 2, "timeout": 1})
batch_b = Counter({"ok": 5, "error": 1, "timeout": 3})

combined = batch_a + batch_b
common = batch_a & batch_b

events_by_model = defaultdict(list)
events_by_model["model-a"].extend(["ok", "error"])
events_by_model["model-b"].extend(["ok", "timeout", "ok"])

print(combined)
print(common)
print(dict(events_by_model))
```

#### Solution Explanation
`batch_a + batch_b` adds counts element by element and retains positive results. `&` takes the minimum count for keys present in both counters.

The grouped event structure is separate because grouping raw events and counting aggregate categories are different access patterns.

#### Key Concepts Reinforced
- Counter arithmetic.
- `&` as minimum-count intersection.
- `defaultdict(list)` for grouping.
- Choosing a data structure by semantic intent.

#### Common Mistakes
- Thinking `Counter - Counter` is a full signed subtraction.
- Using a plain dict with repeated missing-key checks everywhere.
- Mixing grouping and aggregation into one structure without a clear purpose.

#### Production Connection
Model monitoring systems often need both global outcome frequencies and per-model breakdowns. Keeping those responsibilities explicit improves observability design.


### Question 29 — Repair an Unsafe AI Cache Key

#### Difficulty
Hard

#### Topics Covered
- lru_cache
- cache keys
- model versioning
- cache invalidation
- partial

#### Problem
A deterministic text transformation is cached only by `text`. The transformation changes when the model version or preprocessing version changes. Old results are being reused incorrectly.

#### What You Need to Do
Redesign the function signature so the cache key includes all result-determining dimensions, and create a specialized processor with `partial`.

#### How to Think About the Problem
A cache key must contain every input dimension that can change the result. Version fields are not metadata decorations; they are part of the semantic input to the cached computation.

#### Solution
```python
from functools import lru_cache, partial

@lru_cache(maxsize=128)
def preprocess(model_id: str, model_version: str,
               preprocessing_version: str, text: str) -> str:
    return (
        f"{model_id}:{model_version}:{preprocessing_version}:"
        f"{text.strip().lower()}"
    )

production_preprocess = partial(
    preprocess,
    model_id="embedder",
    model_version="v3",
    preprocessing_version="p7",
)

print(production_preprocess(" Hello "))
print(production_preprocess(" Hello "))
print(preprocess.cache_info())
```

#### Solution Explanation
The cache now distinguishes results by model identity, model version, preprocessing version, and text. Changing a version creates a different key rather than silently reusing an older result.

`partial` fixes stable production configuration while preserving `text` as the remaining argument. This improves reuse without hiding the cache semantics.

#### Key Concepts Reinforced
- Cache keys encode semantic inputs.
- Model/configuration versions can require invalidation.
- Bounded caches control retention.
- `partial` specializes a callable.

#### Common Mistakes
- Caching only by raw text.
- Assuming `cache_clear()` is the only invalidation strategy.
- Using a version outside the function signature where it cannot affect the cache key.

#### Production Connection
This pattern applies to deterministic preprocessing and embedding preparation. For real model/API calls, also consider freshness, privacy, authorization, and distributed cache requirements.


### Question 30 — Find Why Objects Stay Reachable

#### Difficulty
Hard

#### Topics Covered
- object graph
- reachability
- gc
- weakref
- memory retention

#### Problem
A registry keeps objects alive even after the application no longer needs them. You want to track objects without owning their lifetime.

#### What You Need to Do
Replace a strong registry with `weakref.WeakValueDictionary`, then demonstrate that objects can disappear when no strong references remain.

#### How to Think About the Problem
A normal dict stores strong references. A weak-value dictionary stores references that do not keep the target alive. The key is to distinguish "track this object" from "own this object.

#### Solution
```python
import gc
import weakref

class Session:
    pass

registry = weakref.WeakValueDictionary()

session = Session()
registry["s1"] = session

print("before:", list(registry))

del session
gc.collect()

print("after:", list(registry))
```

#### Solution Explanation
The registry observes the session without becoming its owner. Once the last strong reference is removed and the object becomes reclaimable, the weak entry can disappear.

`gc.collect()` here is a diagnostic aid for making collection behavior easier to observe. It is not the general fix for memory problems; ownership and retention are the real design concerns.

#### Key Concepts Reinforced
- Strong vs weak references.
- Weak registries.
- Reachability and object lifetime.
- `gc` as a diagnostic/control tool.

#### Common Mistakes
- Assuming weak references work for every Python object.
- Using weak references where strong ownership is actually required.
- Calling `gc.collect()` instead of fixing unwanted retention.

#### Production Connection
Weak registries can be useful for caches, listeners, object tracking, or metadata associated with objects whose lifecycle is owned elsewhere.


### Question 31 — Repair a Shared-Counter Race

#### Difficulty
Hard

#### Topics Covered
- threading
- race condition
- Lock
- shared mutable state

#### Problem
Two threads repeatedly increment a shared counter. The final value is sometimes lower than expected on a given runtime because the read-modify-write sequence is not treated as one application-level critical section.

#### What You Need to Do
Protect the shared update with a `threading.Lock` and explain why explicit synchronization is clearer than relying on implementation-specific atomicity assumptions.

#### How to Think About the Problem
The logical operation is a sequence: read current value, add one, write the result. Treat that sequence as a critical section. A lock establishes mutual exclusion for the protected update.

#### Solution
```python
import threading

counter = 0
lock = threading.Lock()

def increment_many(times: int) -> None:
    global counter
    for _ in range(times):
        with lock:
            counter += 1

threads = [
    threading.Thread(target=increment_many, args=(10_000,)),
    threading.Thread(target=increment_many, args=(10_000,)),
]

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

print(counter)
```

#### Solution Explanation
Each thread must acquire the lock before executing the shared update. `with lock:` guarantees release even if the body fails.

The key engineering lesson is that application-level correctness should not depend on a vague claim that some individual operation is "atomic." Protect the invariant explicitly.

#### Key Concepts Reinforced
- Race conditions arise around shared mutable state.
- A lock protects a critical section.
- Thread safety is a design property, not a magic feature of Python.

#### Common Mistakes
- Locking too little of the critical section.
- Holding locks across slow I/O unnecessarily.
- Assuming the GIL makes all multi-step operations safe.

#### Production Connection
Background workers and in-memory counters often need explicit synchronization when multiple threads mutate shared application state.


### Question 32 — Choose Threads, Processes, or Async for Three Workloads

#### Difficulty
Hard

#### Topics Covered
- I/O-bound vs CPU-bound
- threads
- asyncio
- process pools
- executors
- GIL

#### Problem
You have three workloads: (A) many network waits, (B) CPU-heavy pure-Python transformations, and (C) a synchronous function that should run without blocking an async service. Choose suitable execution models.

#### What You Need to Do
Give a minimal implementation sketch for B and C, and explain the model that should be used for A when the network client supports non-blocking async I/O.

#### How to Think About the Problem
Classify the workload before choosing the mechanism. I/O waiting benefits from overlapping waits; CPU-heavy pure-Python work may need separate processes on traditional CPython builds; synchronous code called from an async service may be isolated in a thread pool when appropriate.

#### Solution
```python
import asyncio
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

def cpu_like(x: int) -> int:
    total = 0
    for value in range(x):
        total += value * value
    return total

def sync_like(x: int) -> int:
    return x + 1

async def main() -> None:
    # A: use asyncio tasks when the network API itself is non-blocking.
    print("A: asyncio for independent I/O")

    # B: separate processes can provide CPU parallelism.
    with ProcessPoolExecutor() as pool:
        values = list(pool.map(cpu_like, [10_000, 20_000]))
        print("B:", values)

    # C: isolate a synchronous function from the event-loop thread.
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=2) as pool:
        result = await loop.run_in_executor(pool, sync_like, 7)
        print("C:", result)

if __name__ == "__main__":
    asyncio.run(main())
```

#### Solution Explanation
Workload A is conceptually an asyncio problem when the network API is itself asynchronous. Workload B is CPU-bound and can use separate processes for real CPU parallelism. Workload C is synchronous code that would otherwise block the event-loop thread, so a thread pool can isolate it.

The exact choice still depends on serialization cost, library behavior, worker count, rate limits, and deployment constraints. The GIL is relevant to traditional CPython behavior but is not a statement that Python can never use parallel hardware.

#### Key Concepts Reinforced
- Workload classification precedes model selection.
- Thread pools are useful for compatible synchronous work.
- Process pools provide process isolation and can enable CPU parallelism.
- Async requires non-blocking operations to realize its benefits.
- The GIL is an implementation-specific concurrency consideration.

#### Common Mistakes
- Choosing asyncio solely because it sounds faster.
- Running heavy CPU work directly in the event loop.
- Ignoring process startup and serialization costs.
- Treating the GIL as a universal statement about every Python implementation.

#### Production Connection
AI pipelines often mix all three patterns: concurrent external API calls, CPU-heavy preprocessing, and synchronous libraries around an asynchronous service.


### Question 33 — Control a Producer-Consumer Pipeline

#### Difficulty
Hard

#### Topics Covered
- queue.Queue
- producer-consumer
- backpressure
- blocking
- worker pool

#### Problem
A producer can create work faster than a consumer can process it. An unbounded backlog would increase memory indefinitely.

#### What You Need to Do
Use a bounded `queue.Queue`, a worker thread, and `task_done()`/`join()` so the producer experiences natural backpressure.

#### How to Think About the Problem
A bounded queue places a finite limit on in-flight buffered work. When the queue fills, `put()` can block until capacity becomes available. `task_done()` and `join()` provide a completion accounting mechanism.

#### Solution
```python
from queue import Queue
from threading import Thread

work = Queue(maxsize=2)

def worker() -> None:
    while True:
        item = work.get()
        try:
            if item is None:
                return
            print("processed", item)
        finally:
            work.task_done()

thread = Thread(target=worker)
thread.start()

for item in range(5):
    work.put(item)

work.join()
work.put(None)
thread.join()
```

#### Solution Explanation
`Queue(maxsize=2)` limits buffered work. The worker removes items with `get()`, processes them, and calls `task_done()` in `finally` so accounting remains correct.

The sentinel terminates the worker after all real work has been drained. The important production concept is that queue capacity is also a memory-control decision.

#### Key Concepts Reinforced
- Producer-consumer architecture.
- Bounded queues implement backpressure.
- `task_done()` and `join()` coordinate completion.
- Queue abstractions are synchronization-oriented.

#### Common Mistakes
- Using an unbounded queue without considering memory.
- Forgetting `task_done()`.
- Using a raw deque as if it were a full synchronization abstraction.

#### Production Connection
Document ingestion, inference request pipelines, and batch workers use bounded queues to keep incoming load from overwhelming downstream processing.


# Part IV — Advanced Questions

### Question 34 — Design a Memory-Bounded Document Pipeline

#### Difficulty
Advanced

#### Topics Covered
- generators
- context managers
- typing
- Enum
- datetime
- Counter/defaultdict/deque
- production reasoning

#### Problem
Design a single-process document pipeline that reads records lazily, tracks workflow states, groups outcomes by document type, keeps only the latest ten events, and avoids materializing the entire input.

#### What You Need to Do
Provide a compact implementation that combines the source-file concepts without introducing external frameworks. Explain why each structure is used and what it does not solve.

#### How to Think About the Problem
Separate the pipeline into semantic responsibilities: generator for lazy input, Enum for state, aware UTC timestamp for event time, `defaultdict` for grouping, `Counter` for frequencies, and bounded `deque` for recent history. Keep the context manager responsible for lifecycle.

#### Solution
```python
from collections import Counter, defaultdict, deque
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Iterator

class State(Enum):
    RECEIVED = "received"
    PROCESSED = "processed"
    FAILED = "failed"

@dataclass(frozen=True)
class Document:
    document_id: str
    kind: str

@dataclass(frozen=True)
class Event:
    document_id: str
    kind: str
    state: State
    timestamp: datetime

@contextmanager
def document_source(items: list[Document]) -> Iterator[Iterator[Document]]:
    print("source opened")
    try:
        yield iter(items)
    finally:
        print("source closed")

def process_documents(items: list[Document]) -> tuple[Counter, dict, deque]:
    counts = Counter()
    by_kind = defaultdict(list)
    recent = deque(maxlen=10)

    with document_source(items) as source:
        for document in source:
            state = (
                State.PROCESSED
                if document.document_id != "bad"
                else State.FAILED
            )
            event = Event(
                document.document_id,
                document.kind,
                state,
                datetime.now(timezone.utc),
            )
            counts[state] += 1
            by_kind[document.kind].append(event)
            recent.append(event)

    return counts, dict(by_kind), recent

counts, groups, recent = process_documents([
    Document("1", "pdf"),
    Document("2", "pdf"),
    Document("bad", "pdf"),
    Document("3", "text"),
])

print(counts)
print(groups)
print(list(recent))
```

#### Solution Explanation
The input is iterated rather than converted into one giant intermediate list. The Enum expresses workflow state, the aware UTC timestamp gives event records a consistent time basis, and the three collections encode distinct access patterns.

`Counter` answers "how many?", `defaultdict(list)` answers "which events belong to this group?", and `deque(maxlen=10)` answers "what recent history do we retain?" The context manager owns the source lifecycle.

This remains an in-memory single-process design. It does not provide durability, distributed coordination, or unbounded data retention.

#### Key Concepts Reinforced
- Choose structures by access pattern.
- Streaming controls intermediate materialization.
- Explicit state/time semantics improve correctness.
- Bounded memory is an architectural property.

#### Common Mistakes
- Returning all grouped events when only counts are required.
- Using naive datetimes.
- Assuming a bounded recent buffer is a durable event store.

#### Production Connection
This resembles the shape of a production AI document ingestion worker while remaining intentionally small enough to reason about in one file.


### Question 35 — Build Bounded Async Fan-Out with Timeout and Cancellation

#### Difficulty
Advanced

#### Topics Covered
- asyncio
- TaskGroup
- Semaphore
- timeouts
- cancellation
- backpressure

#### Problem
An AI application needs to call many independent remote operations. You must avoid unbounded concurrency and stop waiting forever on a slow operation.

#### What You Need to Do
Implement a bounded asynchronous fan-out using a semaphore and `TaskGroup`. Apply a per-call timeout and explain what cancellation means for the task group.

#### How to Think About the Problem
Concurrency should be deliberately bounded. Put the remote operation behind a semaphore, wrap it in a timeout, and create child tasks under a structured concurrency boundary. A failure or cancellation should not leave an unowned task tree running indefinitely.

#### Solution
```python
import asyncio

async def remote_call(item: int) -> str:
    await asyncio.sleep(0.01)
    return f"result-{item}"

async def bounded_call(
    semaphore: asyncio.Semaphore,
    item: int,
) -> str:
    async with semaphore:
        async with asyncio.timeout(1):
            return await remote_call(item)

async def process(items: list[int]) -> list[str]:
    semaphore = asyncio.Semaphore(3)
    results: list[str] = []

    async with asyncio.TaskGroup() as group:
        tasks = [
            group.create_task(bounded_call(semaphore, item))
            for item in items
        ]

    for task in tasks:
        results.append(task.result())

    return results

print(asyncio.run(process(list(range(10)))))
```

#### Solution Explanation
The semaphore limits the number of operations in the protected section to three. `asyncio.timeout()` provides a deadline for each call. `TaskGroup` gives the created tasks a structured lifetime tied to the surrounding scope.

In a real system, you would also define retry policy, classify failures, respect service rate limits, instrument latency, and decide what partial results mean. The example's main purpose is to make bounded concurrency and cancellation ownership concrete.

#### Key Concepts Reinforced
- Bounded concurrency.
- Semaphore as a concurrency limit.
- TaskGroup as structured concurrency.
- Timeouts and cancellation are related but distinct controls.

#### Common Mistakes
- Creating thousands of tasks without a limit.
- Assuming a timeout makes external work magically disappear everywhere.
- Collecting results before tasks have completed.
- Ignoring failure propagation within a TaskGroup.

#### Production Connection
This is the core shape of safe LLM/tool/embedding fan-out: concurrency is a resource budget, not an unlimited switch.


### Question 36 — Design a Safe Deterministic Preprocessing Cache

#### Difficulty
Advanced

#### Topics Covered
- lru_cache
- cache keys
- partial
- model/config versioning
- cache invalidation

#### Problem
A deterministic document-normalization function depends on the text, normalization version, and model-preparation version. Production callers use a fixed configuration, and the cache must have a finite size.

#### What You Need to Do
Implement an LRU-cached function whose signature contains every result-determining input, create a specialized callable with `partial`, and expose cache metrics.

#### How to Think About the Problem
Treat configuration that changes the result as part of the cache key. Use `lru_cache` when you need bounded retention and metrics. Use `partial` only to pre-bind stable configuration.

#### Solution
```python
from functools import lru_cache, partial

@lru_cache(maxsize=256)
def normalize(
    normalization_version: str,
    model_prep_version: str,
    text: str,
) -> str:
    return f"{normalization_version}|{model_prep_version}|{text.strip().lower()}"

production_normalize = partial(
    normalize,
    normalization_version="norm-4",
    model_prep_version="prep-7",
)

print(production_normalize(" Hello "))
print(production_normalize(" Hello "))

print(normalize.cache_info())
print(normalize.cache_parameters())

normalize.cache_clear()
print(normalize.cache_info())
```

#### Solution Explanation
The function signature makes the semantic cache key explicit. A change in either version creates a distinct entry. The bounded LRU cache limits retained entries, while `cache_info()` gives an engineer evidence about reuse.

`partial` adapts the general function to a production configuration without duplicating the normalization code. `cache_clear()` remains available when a deliberate global reset is appropriate.

#### Key Concepts Reinforced
- Result-determining inputs belong in cache keys.
- LRU bounds retention.
- Partial application specializes callables.
- Cache observability supports evidence-based optimization.

#### Common Mistakes
- Caching only the text.
- Using `@cache` when unbounded growth is unacceptable.
- Treating cache clear as a substitute for precise invalidation.

#### Production Connection
This mirrors a realistic AI preprocessing boundary. Real deployments additionally need privacy, tenant, authorization, model lifecycle, and distributed-cache considerations.


### Question 37 — Investigate Memory Growth in a Long-Running Worker

#### Difficulty
Advanced

#### Topics Covered
- object lifetime
- gc
- tracemalloc
- weakref
- caches
- memory retention

#### Problem
A worker's memory grows after every batch. The code keeps a module-level list of processed documents and a diagnostic registry. You need to determine whether the objects are still strongly referenced.

#### What You Need to Do
Create a small reproduction, inspect traced allocations, and repair ownership so completed documents are no longer retained merely for diagnostics.

#### How to Think About the Problem
First identify the owner of each long-lived reference. A list that grows forever is an intentional strong retention path. A weak registry can track objects without owning them. Use `tracemalloc` to observe allocation behavior, then fix the root retention path rather than repeatedly forcing GC.

#### Solution
```python
import gc
import tracemalloc
import weakref

class Document:
    pass

retained: list[Document] = []
observed = weakref.WeakSet()

def process_batch(size: int) -> None:
    for _ in range(size):
        doc = Document()
        observed.add(doc)
        retained.append(doc)

tracemalloc.start()

process_batch(1_000)
current, peak = tracemalloc.get_traced_memory()
print("retained:", len(retained))
print("observed:", len(observed))
print("current:", current)
print("peak:", peak)

retained.clear()
gc.collect()

print("after clear:", len(retained))
tracemalloc.stop()
```

#### Solution Explanation
`retained` is a strong reference to every document, so the documents remain reachable. `observed` is weak and therefore does not keep them alive.

Clearing `retained` removes the ownership path. `gc.collect()` can then make reclamation observable for unreachable cyclic garbage, but the real fix is to stop retaining objects longer than required.

`tracemalloc` helps locate allocation behavior within its tracing scope, but it is not a complete view of native memory or operating-system RSS.

#### Key Concepts Reinforced
- Reachability determines whether objects can be reclaimed.
- Strong references extend lifetime.
- Weak references are observation without ownership.
- Measure retention before changing GC behavior.

#### Common Mistakes
- Calling GC repeatedly without removing strong references.
- Confusing allocation with retention.
- Assuming traced Python allocations equal total process memory.

#### Production Connection
This is a common long-running worker failure mode in document processors, inference services, and agent runtimes.


### Question 38 — Create a Typed, Instrumented Resource Processor

#### Difficulty
Advanced

#### Topics Covered
- Protocol
- decorators
- context managers
- typing
- function metadata

#### Problem
Build a small processing component that (a) depends on a typed structural interface, (b) logs calls through a decorator, and (c) manages a resource lifetime explicitly.

#### What You Need to Do
Define the Protocol, a decorator that preserves metadata, and a class-based context manager. Compose them in a small end-to-end call.

#### How to Think About the Problem
Keep interfaces, cross-cutting behavior, and resource ownership separate. The Protocol defines what the processor can do; the decorator adds observability; the context manager controls setup/cleanup.

#### Solution
```python
from functools import wraps
from typing import Protocol

class Processor(Protocol):
    def process(self, text: str) -> str:
        ...

def traced(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("start:", func.__name__)
        result = func(*args, **kwargs)
        print("end:", func.__name__)
        return result
    return wrapper

class ProcessingSession:
    def __enter__(self):
        print("session opened")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("session closed")
        return False

class UpperProcessor:
    @traced
    def process(self, text: str) -> str:
        return text.upper()

def run(session: ProcessingSession, processor: Processor, text: str) -> str:
    with session:
        return processor.process(text)

print(run(ProcessingSession(), UpperProcessor(), "hello"))
```

#### Solution Explanation
The `Processor` Protocol keeps `run()` independent of `UpperProcessor`. The decorator adds tracing without changing the call contract, and `wraps` preserves metadata. The context manager gives the session a deterministic lifecycle.

This separation is a small example of production-oriented composition: dependencies are explicit, cross-cutting behavior is localized, and cleanup is not hidden inside business logic.

#### Key Concepts Reinforced
- Structural typing.
- Decorator composition.
- Deterministic resource management.
- Separation of concerns.

#### Common Mistakes
- Coupling the runner to one concrete processor.
- Forgetting `wraps`.
- Putting resource cleanup in a decorator when lifecycle is the real concern.

#### Production Connection
The same shape can support typed model-provider adapters, document processors, evaluation strategies, and resource-scoped inference operations.


### Question 39 — Handle an Ambiguous Local Time Safely

#### Difficulty
Advanced

#### Topics Covered
- datetime
- ZoneInfo
- DST
- fold
- aware datetimes

#### Problem
A regional clock repeats an hour during the autumn DST transition. Two local timestamps look identical on the wall clock but represent different instants. Your event pipeline must preserve which occurrence was intended.

#### What You Need to Do
Construct both occurrences using the timezone's `fold` value, convert them to UTC, and show that the resulting instants differ.

#### How to Think About the Problem
A repeated wall-clock time is ambiguous. `fold=0` and `fold=1` distinguish the two occurrences for timezone-aware datetime handling. Convert both to UTC before storing/comparing them.

#### Solution
```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

zone = ZoneInfo("America/New_York")

first = datetime(2026, 11, 1, 1, 30, tzinfo=zone, fold=0)
second = datetime(2026, 11, 1, 1, 30, tzinfo=zone, fold=1)

print(first.astimezone(timezone.utc))
print(second.astimezone(timezone.utc))
print(first.astimezone(timezone.utc) != second.astimezone(timezone.utc))
```

#### Solution Explanation
The local clock value `01:30` occurs twice around the fall-back transition. `fold` identifies which occurrence is intended. Converting each aware datetime to UTC reveals distinct instants.

The production lesson is that local wall-clock strings are not always sufficient to identify an event. For durable event systems, preserve timezone-aware semantics and normalize to a canonical representation when crossing system boundaries.

#### Key Concepts Reinforced
- Geographic timezones.
- DST ambiguity.
- `fold` distinguishes repeated local times.
- UTC normalization.

#### Common Mistakes
- Treating a local timestamp as globally unique.
- Dropping timezone information.
- Using `replace(tzinfo=...)` as if it converted an instant.

#### Production Connection
Scheduling, AI job deadlines, event logs, and cross-region data processing are vulnerable to DST bugs when local times are treated as simple numbers.


### Question 40 — Build an In-Memory AI Event Monitor

#### Difficulty
Advanced

#### Topics Covered
- Counter
- defaultdict
- deque
- datetime
- Applied AI monitoring

#### Problem
An inference service emits events containing `model`, `status`, `latency_ms`, and a UTC timestamp. You need global status counts, per-model event grouping, and bounded recent history.

#### What You Need to Do
Implement an in-memory monitor with clear data-structure responsibilities and a method that returns simple statistics.

#### How to Think About the Problem
Map each requirement to one structure: Counter for frequency, defaultdict for grouping, deque for bounded history. Use UTC-aware datetimes for events. Avoid pretending that this in-memory monitor is durable or distributed.

#### Solution
```python
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class InferenceEvent:
    request_id: str
    model: str
    status: str
    latency_ms: float
    timestamp: datetime

class Monitor:
    def __init__(self, recent_limit: int = 10) -> None:
        self.status_counts = Counter()
        self.model_counts = Counter()
        self.events_by_model = defaultdict(list)
        self.recent_events = deque(maxlen=recent_limit)

    def ingest(self, event: InferenceEvent) -> None:
        self.status_counts[event.status] += 1
        self.model_counts[event.model] += 1
        self.events_by_model[event.model].append(event)
        self.recent_events.append(event)

    def stats(self) -> dict[str, object]:
        failure_counts = Counter(
            event.status
            for event in self.recent_events
            if event.status != "ok"
        )
        return {
            "statuses": self.status_counts.most_common(),
            "models": self.model_counts.most_common(),
            "recent_failures": failure_counts.most_common(),
        }

monitor = Monitor(recent_limit=3)

for i, status in enumerate(["ok", "error", "ok", "timeout"], start=1):
    monitor.ingest(
        InferenceEvent(
            request_id=str(i),
            model="model-a",
            status=status,
            latency_ms=20 + i,
            timestamp=datetime.now(timezone.utc),
        )
    )

print(monitor.stats())
print(len(monitor.recent_events))
```

#### Solution Explanation
The monitor keeps three different indexes because they answer different questions. Counts are easy to inspect for aggregate distributions, grouped events support per-model analysis, and `maxlen` prevents recent history from growing without bound.

The model is intentionally local to one process. A production monitoring system would need durable/event-stream infrastructure and explicit concurrency controls if multiple workers ingest into shared state.

#### Key Concepts Reinforced
- Semantic data-structure selection.
- Bounded in-memory history.
- UTC-aware event timestamps.
- Applied AI observability.

#### Common Mistakes
- Using one structure for every query.
- Letting `events_by_model` grow forever without a retention policy.
- Treating local state as a distributed monitoring system.

#### Production Connection
This is a small but realistic foundation for inference monitoring, evaluation telemetry, and agent/tool outcome analysis.


### Question 41 — Orchestrate Independent and Dependent Agent Tools

#### Difficulty
Advanced

#### Topics Covered
- asyncio
- TaskGroup
- Enum/state machine
- fan-out/fan-in
- timeouts

#### Problem
An agent needs three independent read-only tools and then a final summarization step that depends on all three results. Tool calls should be concurrent, but the summary must remain sequential after fan-in.

#### What You Need to Do
Implement the orchestration with a state Enum, concurrent Tasks, and a final aggregation step. Keep timeouts around each tool call.

#### How to Think About the Problem
First identify the dependency graph. The three tools can fan out concurrently. The summary is a fan-in stage because it depends on all results. Model the workflow state explicitly so the orchestration has visible lifecycle stages.

#### Solution
```python
import asyncio
from enum import Enum

class AgentState(Enum):
    READY = "ready"
    TOOLS_RUNNING = "tools_running"
    READY_TO_SUMMARIZE = "ready_to_summarize"
    DONE = "done"

async def tool(name: str) -> str:
    await asyncio.sleep(0.01)
    return f"{name}-result"

async def run_agent() -> tuple[AgentState, str]:
    state = AgentState.READY
    state = AgentState.TOOLS_RUNNING

    async with asyncio.TaskGroup() as group:
        tasks = [
            group.create_task(asyncio.wait_for(tool(name), timeout=1))
            for name in ["search", "catalog", "history"]
        ]

    results = [task.result() for task in tasks]
    state = AgentState.READY_TO_SUMMARIZE

    summary = " | ".join(results)
    state = AgentState.DONE
    return state, summary

print(asyncio.run(run_agent()))
```

#### Solution Explanation
The dependency graph drives the concurrency model. The three tool calls have no dependency on one another, so they can be scheduled concurrently. The final summary waits until all tasks are complete, which creates the fan-in boundary.

The Enum makes the workflow stages explicit. `wait_for()` adds a per-tool timeout. In a larger system, failure policies, cancellation propagation, and partial-result handling would need explicit design.

#### Key Concepts Reinforced
- Fan-out/fan-in.
- TaskGroup.
- Timeouts.
- State-machine vocabulary applied to orchestration.

#### Common Mistakes
- Trying to run dependent steps concurrently.
- Creating unbounded tasks.
- Treating a timeout as equivalent to successful completion.
- Hiding workflow state in implicit booleans.

#### Production Connection
This is a common pattern for agent tool orchestration when several read-only tools can run independently before synthesis.


### Question 42 — Refactor a Materializing ETL Stage into a Streaming Pipeline

#### Difficulty
Advanced

#### Topics Covered
- generator expressions
- yield
- Counter
- deque
- memory
- performance trade-offs

#### Problem
A pipeline currently builds three large lists: normalized records, grouped records, and recent records. Memory grows with input size even though only aggregate counts and a small recent window are needed.

#### What You Need to Do
Refactor the design so normalization remains lazy, aggregation is one-pass, and recent records are retained only in a bounded deque.

#### How to Think About the Problem
Start from requirements instead of existing containers. If downstream code needs only counts and recent history, do not retain the entire normalized dataset or grouped raw records. Use a generator for transformation and structures that match the actual queries.

#### Solution
```python
from collections import Counter, deque

def normalized(records):
    for record in records:
        yield record.strip().lower()

def summarize(records):
    counts = Counter()
    recent = deque(maxlen=5)

    for record in normalized(records):
        counts[record] += 1
        recent.append(record)

    return counts, recent

records = ["A", "B", "A", "C", "A", "D", "E"]
counts, recent = summarize(records)

print(counts)
print(list(recent))
```

#### Solution Explanation
The original data is transformed lazily by `normalized()`. The loop consumes one record at a time, updating a Counter and a bounded recent buffer.

The refactor changes the memory model: there is no growing list of all normalized records. This is a direct example of choosing laziness and bounded retention based on downstream access requirements.

#### Key Concepts Reinforced
- Streaming transformations.
- One-pass aggregation.
- Bounded recent history.
- Memory-aware data structure selection.

#### Common Mistakes
- Keeping a full list before aggregation.
- Using a deque without considering what information is discarded.
- Assuming a generator itself stores all produced values.

#### Production Connection
The same pattern is useful in data ingestion, log aggregation, document processing, and AI evaluation streams.


### Question 43 — Explain Why a Cached Mutable Object Changes Everywhere

#### Difficulty
Advanced

#### Topics Covered
- functools.cache
- mutable return values
- object identity
- GC/lifetime
- shared state

#### Problem
A cached function returns a list. A caller mutates the returned list, and a later caller unexpectedly sees that mutation. Explain the object-lifetime and aliasing behavior and repair the design.

#### What You Need to Do
Show the shared mutable result, then change the function to return an immutable representation that callers cannot accidentally mutate in place.

#### How to Think About the Problem
A cache stores the returned object itself. Every cache hit can therefore return the same object reference. The problem is not garbage collection; the object is intentionally strongly retained by the cache.

#### Solution
```python
from functools import cache

@cache
def tags_for(document_id: str) -> tuple[str, ...]:
    return ("ai", "python", document_id)

first = tags_for("doc-1")
second = tags_for("doc-1")

print(first is second)
print(first)

updated = first + ("production",)
print(updated)
print(tags_for("doc-1"))
```

#### Solution Explanation
The cache intentionally holds the returned tuple. Because the tuple is immutable, callers cannot mutate its internal state. `first is second` can be true because the same cached object is returned on repeated calls; identity reuse is not itself an error when the value is immutable.

The production principle is to avoid exposing a mutable cached object when callers are expected to treat the result as independent state. Alternatives include returning immutable values, copying at the boundary, or designing ownership explicitly.

#### Key Concepts Reinforced
- Caches retain returned objects.
- Identity and equality are different concepts.
- Immutable return values reduce shared-state surprises.
- Cache state affects object lifetime.

#### Common Mistakes
- Assuming each cache hit constructs a new result.
- Calling `deepcopy()` automatically without considering cost.
- Blaming GC when a cache is the strong owner of the object.

#### Production Connection
Cached mutable model metadata, configuration objects, or agent state can become hidden shared state. Production APIs should make ownership and mutability obvious.


### Question 44 — Design a Complete Python-Foundation Pipeline Under Production Constraints

#### Difficulty
Advanced

#### Topics Covered
- generators
- context managers
- typing
- state machines
- datetime
- collections
- cache
- object lifetime
- concurrency

#### Problem
Design a small standard-library-only pipeline for processing AI documents. Requirements: stream input, validate state transitions, use UTC event timestamps, count outcomes, retain only recent events, cache a deterministic normalization step with a bounded LRU cache, and process independent documents concurrently without unlimited in-flight work.

#### What You Need to Do
Provide a compact architecture and runnable implementation that demonstrates the boundaries. Then explain which problems the example intentionally does not solve.

#### How to Think About the Problem
Work from constraints in this order: (1) streaming input, (2) explicit document state, (3) deterministic normalization cache, (4) bounded recent monitoring, and (5) bounded concurrency. Avoid turning one object into the owner of every concern. Keep resource lifetime separate and make the concurrency limit explicit.

#### Solution
```python
import asyncio
from collections import Counter, deque
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from functools import lru_cache
from typing import Iterator

class State(Enum):
    RECEIVED = "received"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass(frozen=True)
class Document:
    document_id: str
    text: str

@dataclass(frozen=True)
class Event:
    document_id: str
    state: State
    timestamp: datetime

@contextmanager
def document_stream(items: list[Document]) -> Iterator[Iterator[Document]]:
    try:
        yield iter(items)
    finally:
        print("stream closed")

@lru_cache(maxsize=128)
def normalize(text: str) -> str:
    return " ".join(text.strip().lower().split())

class Monitor:
    def __init__(self) -> None:
        self.counts = Counter()
        self.recent = deque(maxlen=20)

    def record(self, event: Event) -> None:
        self.counts[event.state] += 1
        self.recent.append(event)

async def process_one(
    document: Document,
    monitor: Monitor,
    limit: asyncio.Semaphore,
) -> None:
    async with limit:
        try:
            normalized = normalize(document.text)
            await asyncio.sleep(0)
            event = Event(
                document.document_id,
                State.COMPLETED if normalized else State.FAILED,
                datetime.now(timezone.utc),
            )
        except Exception:
            event = Event(
                document.document_id,
                State.FAILED,
                datetime.now(timezone.utc),
            )
        monitor.record(event)

async def run(documents: list[Document]) -> Monitor:
    monitor = Monitor()
    limit = asyncio.Semaphore(3)

    with document_stream(documents) as stream:
        async with asyncio.TaskGroup() as group:
            for document in stream:
                group.create_task(process_one(document, monitor, limit))

    return monitor

documents = [
    Document("1", " Hello   World "),
    Document("2", "AI systems"),
    Document("3", " "),
]

monitor = asyncio.run(run(documents))

print(monitor.counts)
print(list(monitor.recent))
print(normalize.cache_info())
```

#### Solution Explanation
This integrates the roadmap's foundations without pretending to be a full production platform.

- The generator-style stream boundary avoids requiring a second copy of the input.
- `Enum` makes processing outcomes explicit.
- UTC-aware datetimes make event timestamps comparable.
- `lru_cache` memoizes deterministic normalization with bounded capacity.
- `Counter` provides outcome frequency.
- `deque(maxlen=20)` bounds recent event retention.
- `Semaphore` limits concurrent work.
- `TaskGroup` gives tasks a structured lifetime.
- The context manager owns stream lifecycle.

There are important limitations. `Monitor` is shared mutable state inside one event loop and would need a deliberate synchronization strategy if the design changed to threads or processes. The cache is process-local. Event history is not durable. There is no external API rate-limit model, retry policy, persistent queue, or distributed coordination. Those omissions are intentional because the source modules provide foundations for these concepts rather than a complete distributed platform.

#### Key Concepts Reinforced
- Cross-topic composition.
- Streaming vs materialization.
- Explicit state/time semantics.
- Bounded caching and bounded concurrency.
- Object ownership and process-local state.

#### Common Mistakes
- Adding every feature to one global mutable object.
- Treating local cache/history as durable infrastructure.
- Launching unbounded work.
- Using naive timestamps.
- Confusing concurrency with distributed durability.

#### Production Connection
This is the closest practice exercise to the learner's eventual Applied AI Engineering work: combine language features according to explicit workload, ownership, memory, timing, and concurrency constraints.


# Final Review

## What You Should Be Able to Do After These 44 Questions

- Distinguish iterable, iterator, generator, generator expression, and one-shot exhaustion behavior.
- Write and debug decorators, closures, metadata preservation, decorator order, and typed callable wrappers.
- Manage resources with `with`, `__enter__`, `__exit__`, `contextmanager`, and dynamic cleanup patterns.
- Choose lazy versus eager processing based on access pattern and memory requirements.
- Use advanced typing concepts such as Protocols, generics, TypeVar, ParamSpec, TypedDict, Literal, and callable contracts where appropriate.
- Model controlled states and transitions using Enum-based state machines.
- Handle timezone-aware datetimes, UTC normalization, durations, deadlines, and DST ambiguity.
- Select Counter, defaultdict, and deque by semantic intent and access pattern.
- Reason about memoization, cache keys, cache lifetime, LRU eviction, partial application, and stale-result risks.
- Explain object identity, references, mutation, copying, reachability, garbage collection, weak references, and memory retention.
- Distinguish sequential execution, concurrency, parallelism, threads, processes, coroutines, Tasks, Futures, event loops, executors, synchronization, timeouts, cancellation, backpressure, and structured concurrency.
- Apply these foundations to streaming data, AI preprocessing, RAG-style pipelines, inference monitoring, agent orchestration, and other in-memory Applied AI patterns without assuming external frameworks.

## Final Topic Coverage Map

| Source chapter | Meaningful practice coverage |
|---|---|
| 01 — Iterables, Iterators, Generators | Q1, Q4, Q13, Q23, Q42 |
| 02 — Decorators | Q2, Q14, Q24, Q38 |
| 03 — Context Managers | Q3, Q13, Q25, Q34, Q38 |
| 04 — Generator Expressions and Memory Trade-offs | Q4, Q23, Q34, Q42 |
| 05 — Advanced Typing Essentials | Q5, Q14, Q15, Q26, Q38, Q44 |
| 06 — Enums and State Machines | Q6, Q15, Q17, Q27, Q34, Q41, Q44 |
| 07 — Datetime, Timezones and Timestamps | Q7, Q17, Q27, Q34, Q39, Q41, Q44 |
| 08 — Counter, defaultdict and deque | Q8, Q16, Q20, Q28, Q34, Q40, Q42, Q44 |
| 09 — functools, cache and partial | Q9, Q18, Q21, Q29, Q36, Q43, Q44 |
| 10 — Object Model and Garbage Collection | Q10, Q19, Q30, Q37, Q43, Q44 |
| 11 — Concurrency Vocabulary | Q11, Q12, Q22, Q31, Q32, Q33, Q35, Q41, Q44 |

## Final Self-Check

Before considering the practice set complete, confirm:

- [ ] Exactly 44 questions exist.
- [ ] Basic = 11.
- [ ] Moderate = 11.
- [ ] Hard = 11.
- [ ] Advanced = 11.
- [ ] Numbering runs continuously from 1 through 44.
- [ ] Every question presents the problem before the solution.
- [ ] Every question contains a thinking section, complete solution, explanation, key concepts, common mistakes, and production connection.
- [ ] Questions include coding, debugging, output prediction, refactoring, design, trade-off, memory, concurrency, and production-oriented scenarios.
- [ ] Moderate, Hard, and Advanced questions deliberately combine source concepts.
- [ ] Applied AI contexts test the Python foundations instead of external frameworks.
- [ ] No separate answer key is required because every solution is in this file.
- [ ] The set remains focused on the eleven source chapters.

## Final Engineering Loop

```text
Understand
    ↓
Predict
    ↓
Plan
    ↓
Implement
    ↓
Test
    ↓
Debug
    ↓
Refactor
    ↓
Explain
```

The objective is not simply to get all 44 answers correct. The objective is to become able to explain **why** a Python design works, where it can fail, how its memory/performance behavior changes under load, and which standard-library tool best matches the problem.
