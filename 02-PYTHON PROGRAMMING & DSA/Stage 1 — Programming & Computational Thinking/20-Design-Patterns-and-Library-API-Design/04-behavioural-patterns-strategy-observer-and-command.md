# Behavioural Patterns: Strategy, Observer, and Command

> **Stage:** 1 — Programming & Computational Thinking  
> **Module:** 1.20 — Design Patterns and Library API Design  
> **Lesson:** 04 — Behavioural patterns: Strategy, Observer, and Command  
> **Target:** Python 3.12+  
> **Running case study:** `fetchkit`, a small data-fetching library

## 1. Objectives and prerequisites

By the end of this lesson, you should be able to:

- Explain how behavioural patterns organize collaboration, decisions, and the flow of work.
- Express Strategy with a function, callable object, or `Protocol`; recognize `sorted(key=...)` as a strategy-taking API.
- Build an Observer/publish-subscribe system with explicit registration, removal, ordering, and exception semantics.
- Represent work as Commands that can be logged, queued, retried, replayed, or compensated; distinguish these properties rather than assuming every command supports all of them.
- Compare Template Method inheritance with function injection.
- Recognize State, Chain of Responsibility, Iterator, Visitor, Mediator, and Memento designs and their Pythonic forms.
- Design retry policies and event delivery with deterministic tests, including fake clocks and fake clients.
- Explain async backpressure, delivery guarantees, idempotency, command history, and observer lifecycle risks.
- Extend `fetchkit` with a retry strategy, lifecycle events, and a replayable `FetchCommand` with an idempotency key.

### Prerequisites

The roadmap builds this lesson on Module 1.8 (composition, inheritance, protocols, dependency inversion, and separation of side effects), Module 1.9's state-machine concepts, Module 1.11's data model, Module 1.12's decorators/registries, Module 1.13's `contextvars` and weak references, and Modules 1.7/1.16's testing and mocking. Lesson 05 covers plugin/registry architectures in greater depth; later backend and agent stages revisit task queues and tool calls. This lesson introduces those connections without attempting to teach the later modules in full.

## 2. Behavioural-pattern foundations

A **behavioural design pattern** describes how responsibilities, algorithms, state changes, or notifications flow among collaborators. Structural patterns focus on how components are connected; creational patterns focus on how objects are created; behavioural patterns focus on **who does what, under which policy, and how collaborators communicate**.

| Pattern family | Core question | Examples |
|---|---|---|
| Creational | How should the needed object be created? | Factory, Builder |
| Structural | How should objects be connected or wrapped? | Adapter, Facade, Proxy |
| Behavioural | How should work or decisions vary and flow? | Strategy, Observer, Command, State |

Patterns are vocabulary, not goals. Begin with direct code. Introduce a named pattern when it clarifies a real variation point, removes repeated branching, enables a meaningful test seam, or defines a stable collaboration contract. A pattern should reduce total complexity, not merely move code into more classes.

The three central patterns answer different questions:

- **Strategy:** “Which algorithm or policy should run?”
- **Observer:** “Who needs to be informed that something happened?”
- **Command:** “How can this requested operation be represented and managed as a unit?”

They combine naturally: a `FetchCommand` asks a `Fetcher` to perform work, a retry Strategy decides whether another attempt is allowed, and Observer subscribers receive request/retry/success/error events.

## 3. Beginner patterns

### 3.1 Strategy: interchangeable algorithms

**Definition and mental model.** Strategy encapsulates a family of algorithms behind a compatible callable contract. The caller supplies the algorithm instead of hard-coding every choice in a branching statement.

**Why it exists.** A growing `if kind == ...` ladder couples the caller to each algorithm and makes each new variant require editing central control flow. A strategy makes the variation explicit and independently testable.

**Mechanics.** The caller invokes a callable at a defined point. Python functions are first-class values: they can be passed as arguments, stored in dictionaries, returned from factories, or wrapped with `functools.partial`. A class is justified when the strategy has meaningful state, configuration, lifecycle, or multiple related methods.

A standard-library example is `sorted(records, key=...)`: sorting is the fixed algorithm; the supplied `key` function is the strategy for deriving each item's sort key.

```python
from collections.abc import Callable, Iterable
from decimal import Decimal
from dataclasses import dataclass

@dataclass(frozen=True)
class Item:
    name: str
    price: Decimal
    discount: Decimal

Pricing = Callable[[Item], Decimal]

def total(items: Iterable[Item], pricing: Pricing) -> Decimal:
    return sum((pricing(item) for item in items), start=Decimal("0"))

def regular_price(item: Item) -> Decimal:
    return item.price

def discounted_price(item: Item) -> Decimal:
    return item.price * (Decimal("1") - item.discount)

cart = [Item("book", Decimal("20"), Decimal("0.10"))]
print(total(cart, regular_price))
print(total(cart, discounted_price))
```

Expected output:

```text
20
18.00
```

**Function versus class strategy.** Function strategies are concise and easy to compose. Callable objects or `Protocol` implementations fit policies with state or several operations.

```python
from typing import Protocol

class RetryDecision(Protocol):
    def should_retry(self, attempt: int, error: Exception) -> bool: ...

class RetryTransientFailures:
    def should_retry(self, attempt: int, error: Exception) -> bool:
        return isinstance(error, TimeoutError) and attempt < 3
```

The protocol is useful if consumers need a policy object with `should_retry`; it would be unnecessary if one simple function is enough.

**Use it when:** algorithms vary independently, configuration selects a policy, or each variant needs isolated tests. **Avoid it when:** there is one stable algorithm and no credible variation point. **Trade-offs/failures:** a strategy registry can hide invalid names; callable signatures can drift; stateful strategies can become order-dependent. Validate configuration at startup and test each implementation against the same contract.

**Simplest alternative:** a small `if` statement. Do not replace a clear two-branch conditional with an elaborate strategy hierarchy without evidence that variants will grow or change independently.

### 3.2 Template Method versus function injection

**Template Method** defines a stable algorithm in a base class and leaves selected steps to subclasses. Function injection keeps the algorithm in one function and passes variable steps as callables.

```python
from collections.abc import Callable, Iterable
from typing import TypeVar

T = TypeVar("T")
U = TypeVar("U")

def transform_all(
    values: Iterable[T],
    normalize: Callable[[T], U],
    keep: Callable[[U], bool],
) -> list[U]:
    return [result for value in values if keep(result := normalize(value))]

print(transform_all([" A ", "", " B "], str.strip, bool))
```

Expected output: `['A', 'B']`.

Function injection is usually simpler when only a few steps vary. Template Method can be useful when subclasses are already a meaningful family and the algorithm's invariants must remain centralized. Inheritance-based hooks can create fragile override contracts and hidden execution order; function injection makes dependencies visible at the call site.

**Testing:** test the fixed algorithm with simple spy functions, then test specialized policies separately. **Failure mode:** use inheritance reflexively even though passing a function is enough.

### 3.3 Observer and publish-subscribe

**Definition.** Observer lets a subject notify interested subscribers when something happens. In a publish-subscribe form, a publisher emits a named event/topic and subscribers register interest without direct references from the publisher to each consumer.

**Why it exists.** Request logging, metrics, audit records, UI refreshes, and optional integrations should not force the core operation to import and call every interested subsystem directly.

**Mechanics.** Subscribers register a callable and receive an unsubscribe handle. Publishing takes a snapshot of the subscriber list so registration/removal during a notification does not mutate the iteration in progress. The event bus must define whether handler exceptions stop delivery, whether ordering is guaranteed, and whether nested publication is allowed.

```python
from collections import defaultdict
from collections.abc import Callable
from typing import Any

Handler = Callable[[dict[str, Any]], None]

class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[Handler]] = defaultdict(list)

    def subscribe(self, topic: str, handler: Handler) -> Callable[[], None]:
        self._subscribers[topic].append(handler)
        active = True

        def unsubscribe() -> None:
            nonlocal active
            if active:
                active = False
                try:
                    self._subscribers[topic].remove(handler)
                except ValueError:
                    pass
        return unsubscribe

    def publish(self, topic: str, event: dict[str, Any]) -> None:
        for handler in tuple(self._subscribers[topic]):
            handler(event)
```

This minimal example propagates subscriber exceptions. That is a valid possible contract, but it means one failing handler prevents later handlers from running. For operational telemetry, a common alternative is to isolate exceptions and report them to an error hook/logger. The integrated `fetchkit` implementation later in this lesson uses exception isolation so telemetry does not convert a successful fetch into a failure.

**Synchronous versus asynchronous delivery.** A synchronous observer runs in the publisher's call stack. It is easy to reason about but adds subscriber latency and failure coupling. An asynchronous queue decouples producer and consumer timing but introduces queue capacity, shutdown, ordering, and delivery guarantees. “Publish succeeded” does not automatically mean every async subscriber processed the event.

**Use it when:** multiple independent components need the same fact. **Avoid it when:** a direct function call expresses a required dependency more clearly. **Trade-offs/failures:** hidden control flow, subscriber leaks, re-entrancy, exception propagation, and non-deterministic ordering if concurrency is added. **Testing:** assert registration/removal, delivery order, error policy, nested publication, and no delivery after unsubscribe.

### 3.4 Command: represent an operation as data

**Definition.** A Command packages a request as an object or callable. Separating the request from the code that schedules or executes it makes it possible to queue, log, retry, record, inspect, or sometimes reverse the operation.

**Mechanics.** A command usually has explicit inputs and an execution method. A `dataclass` can make those inputs visible. `functools.partial` is a lightweight command-like callable when all that is needed is binding arguments; a class is more appropriate for durable identity, validation, serialization, or an inverse operation.

```python
from functools import partial
from collections.abc import Callable

Command = Callable[[], str]

def greet(name: str, prefix: str = "Hello") -> str:
    return f"{prefix}, {name}!"

command: Command = partial(greet, "Ada", prefix="Welcome")
print(command())
```

Expected output: `Welcome, Ada!`.

A class-based command can carry an idempotency key and explicit serialization methods. But **not every command can be undone**: sending an email, charging a payment, or fetching a remote URL has no guaranteed inverse. Undo may require a compensating action, not a literal rollback.

**Use it when:** work must be queued, audited, retried, deduplicated, or represented in history. **Avoid it when:** a direct function call is clearer and no command lifecycle is needed. **Trade-offs/failures:** large payloads, stale serialized schemas, unsafe retries, and a false assumption that undo is universally possible. **Testing:** test input validation, stable serialization, idempotency behavior, failure handling, and inverse/compensation separately.

### 3.5 A first command history: only undo what has a valid inverse

Text editing is a good undo/redo example because inserting text can be reversed by deleting exactly the inserted range. The history should record the inverse data, not simply assume that rerunning an arbitrary command will reverse it.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class InsertText:
    position: int
    text: str

class TextBuffer:
    def __init__(self) -> None:
        self.text = ""

    def apply(self, command: InsertText) -> None:
        if not 0 <= command.position <= len(self.text):
            raise ValueError("position outside buffer")
        self.text = self.text[:command.position] + command.text + self.text[command.position:]

    def undo(self, command: InsertText) -> None:
        end = command.position + len(command.text)
        if self.text[command.position:end] != command.text:
            raise RuntimeError("cannot safely undo: buffer changed")
        self.text = self.text[:command.position] + self.text[end:]

class History:
    def __init__(self, buffer: TextBuffer) -> None:
        self.buffer = buffer
        self._undo: list[InsertText] = []
        self._redo: list[InsertText] = []

    def execute(self, command: InsertText) -> None:
        self.buffer.apply(command)
        self._undo.append(command)
        self._redo.clear()

    def undo(self) -> None:
        if not self._undo:
            return
        command = self._undo[-1]
        self.buffer.undo(command)  # mutate history only after the inverse succeeds
        self._undo.pop()
        self._redo.append(command)

    def redo(self) -> None:
        if not self._redo:
            return
        command = self._redo[-1]
        self.buffer.apply(command)  # keep redo entry if reapplication fails
        self._redo.pop()
        self._undo.append(command)

buffer = TextBuffer()
history = History(buffer)
history.undo()  # empty history is a no-op
history.execute(InsertText(0, "hello"))
print(buffer.text)
history.undo()
print(repr(buffer.text))
history.redo()
print(buffer.text)
history.undo()
history.execute(InsertText(0, "new"))
history.redo()  # a new edit after undo clears redo history
assert buffer.text == "new"

# A stale undo must fail without discarding the history entry.
history.execute(InsertText(3, "!"))
buffer.text = "externally changed"
try:
    history.undo()
except RuntimeError:
    pass
else:
    raise AssertionError("stale undo should fail")
assert len(history._undo) == 2
```

Expected output:

```text
hello
''
hello
```

The buffer verifies the expected text before undoing, preventing a stale history entry from silently deleting unrelated content. In a real editor, commands also need careful handling for selection, cursor positions, concurrent edits, and grouped transactions.

## 4. Intermediate patterns

### 4.1 State: make legal transitions explicit

**Definition.** State pattern moves state-dependent behaviour out of scattered conditionals into explicit states and transitions. Python can often start with an `Enum` and transition table; separate state classes are justified only when each state has substantial distinct behaviour.

```python
from enum import Enum, auto

class JobState(Enum):
    READY = auto()
    RUNNING = auto()
    SUCCEEDED = auto()
    FAILED = auto()

class JobEvent(Enum):
    START = auto()
    SUCCEED = auto()
    FAIL = auto()
    RETRY = auto()

TRANSITIONS: dict[tuple[JobState, JobEvent], JobState] = {
    (JobState.READY, JobEvent.START): JobState.RUNNING,
    (JobState.RUNNING, JobEvent.SUCCEED): JobState.SUCCEEDED,
    (JobState.RUNNING, JobEvent.FAIL): JobState.FAILED,
    (JobState.FAILED, JobEvent.RETRY): JobState.READY,
}

def transition(state: JobState, event: JobEvent) -> JobState:
    try:
        return TRANSITIONS[(state, event)]
    except KeyError:
        raise ValueError(f"invalid transition: {state.name} + {event.name}") from None

print(transition(JobState.READY, JobEvent.START).name)
```

Expected output: `RUNNING`.

**Why/use:** explicit transitions make illegal state changes visible and testable. Use `match` when state behavior is small; use state classes or a workflow library when transitions carry complex actions, guards, persistence, visualization, or orchestration. **Failure modes:** state explosion, missing transitions, hidden side effects inside transition functions. Test every legal transition and representative illegal transitions. Libraries such as `transitions` and `python-statemachine` can help, but a table is easier to inspect for small state spaces.

### 4.2 Chain of Responsibility and middleware

A chain passes a request through ordered handlers. A handler may reject, transform, handle, or pass the request onward. Examples include validation → authentication → rate limit → endpoint, logging filters, and request middleware.

```python
from collections.abc import Callable

Request = dict[str, str]
Handler = Callable[[Request, Callable[[Request], str]], str]

def require_token(request: Request, next_handler: Callable[[Request], str]) -> str:
    if not request.get("token"):
        return "unauthorized"
    return next_handler(request)

def endpoint(request: Request) -> str:
    return f"hello {request['user']}"

def invoke(request: Request) -> str:
    return require_token(request, endpoint)

print(invoke({"user": "Ada"}))
print(invoke({"user": "Ada", "token": "test"}))
```

Expected output:

```text
unauthorized
hello Ada
```

The order is part of the contract: authentication before expensive work can save resources; error mapping outside retries may normalize the final failure, while error mapping inside retries may change which failures are retried. Too many middleware layers obscure control flow. Test both each handler and the composed chain.

### 4.3 Iterator and generator as built-in behavioural tools

The Iterator pattern provides sequential access without exposing the underlying collection representation. Python's iterator protocol (`__iter__`, `__next__`) and generators make a custom Iterator class unnecessary for many cases.

```python
from collections.abc import Iterable, Iterator

def nonempty_lines(lines: Iterable[str]) -> Iterator[str]:
    for line in lines:
        stripped = line.strip()
        if stripped:
            yield stripped

print(list(nonempty_lines([" a ", "", " b "])))
```

Expected output: `['a', 'b']`.

Generators are lazy and can process streams without materializing everything, but they are usually single-pass and can hide I/O or exceptions until iteration. Test empty input, early termination, exceptions during iteration, and resource cleanup where generators own resources.

### 4.4 Visitor alternatives: `singledispatch` and `match`

Visitor separates an operation from the types of values it handles. Traditional Visitor classes can become verbose in Python. `functools.singledispatch` is useful when dispatch is based on the first argument's runtime type; structural pattern matching is useful when shape or fields matter.

```python
from functools import singledispatch

@singledispatch
def describe(value: object) -> str:
    return f"object:{type(value).__name__}"

@describe.register
def _(value: int) -> str:
    return f"integer:{value}"

@describe.register
def _(value: list) -> str:
    return f"list-length:{len(value)}"

print(describe(4))
print(describe([1, 2]))
```

Expected output:

```text
integer:4
list-length:2
```

Use dispatch when types are stable and adding operations is common. If adding new data types is the common change, methods/polymorphism may be more appropriate. Broad registrations can mask unsupported inputs; test fallback behavior and subtype dispatch.

### 4.5 Mediator versus direct calls

A **Mediator** centralizes coordination among components so each component does not need to know all the others. An event bus is mediator-like when it coordinates participants, but Observer emphasizes notification to subscribers. These patterns overlap; intent matters.

Use direct calls for required, local, synchronous dependencies (`fetcher.cache_result(result)`). Use a mediator/event bus when independent components must coordinate without a growing mesh of direct references. The cost is indirect control flow and harder tracing. Keep event names, payload schemas, and ownership explicit; avoid a hidden process-global bus.

### 4.6 Memento: immutable snapshots

Memento stores enough state to restore an earlier state without exposing internal mutation. Immutable dataclasses plus `dataclasses.replace` can work well for small snapshots.

```python
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class Settings:
    retries: int
    timeout_seconds: float

current = Settings(retries=2, timeout_seconds=3.0)
snapshot = current
current = replace(current, retries=4)
current = snapshot
print(current)
```

Expected output: `Settings(retries=2, timeout_seconds=3.0)`.

A reference to an immutable value is a safe snapshot; a reference to a mutable nested list is not deeply immutable. For complex object graphs, define what is copied and whether external resources can be restored. Test restoration and aliasing boundaries.

### 4.7 Serializable commands, retries, idempotency, and dead letters

A serializable command should carry versioned, data-only inputs (for example, URL, request ID, and idempotency key), not a live socket, open file, lambda, or arbitrary object graph. A `to_dict()` method should emit a stable schema; decoding must validate untrusted input. Queue consumers should record attempt counts, classify permanent versus transient errors, and move exhausted messages to a dead-letter queue for inspection/replay.

An **idempotency key** identifies one logical operation across retries. It only prevents duplicate effects if the receiver or durable store enforces the key atomically. Merely placing a string on a command does not make execution idempotent.

Retry only when the failure is plausibly transient and repeating the operation is safe. A GET request is defined as safe by HTTP semantics in typical usage, but a buggy endpoint may still have side effects. A POST that charges money must not be blindly retried unless the server provides an idempotency contract. Timeouts are ambiguous: the server may have completed the operation even if the client did not receive the response.

**Undo/redo:** use inverse commands when the inverse is valid; for external irreversible effects, use a compensating action or admit that undo is unavailable. Dead-letter replay should preserve the original idempotency identity when replaying the same logical operation, and use a new key only when deliberately creating a new operation.

### 4.8 Observer pitfalls and lifecycle

- **Ordering:** an ordinary list gives registration-order delivery in a synchronous bus; concurrent consumers may complete out of order unless ordering is enforced.
- **Exceptions:** fail-fast delivery is simple but couples subscribers. Isolated delivery requires an explicit error reporting channel; silently swallowing errors is unacceptable.
- **Re-entrancy:** a handler may publish another event. Define whether nested delivery is immediate (depth-first) or queued (breadth-first). Guard against infinite event loops.
- **Mutation:** iterate over a snapshot or use a carefully designed copy-on-write structure. Removing a handler while publishing should have documented semantics: a snapshot means it may still receive the event already in progress.
- **Memory leaks:** a long-lived bus strongly references bound methods and can keep subscriber instances alive. Return unsubscribe handles, scope the bus, or use weak references such as `weakref.WeakMethod` when their semantics are appropriate. Weak subscriptions can disappear when no strong reference remains, which must be documented.
- **Sync/async mismatch:** do not call an `async def` handler as if it were synchronous; the result is a coroutine, not completed work. Maintain distinct sync and async contracts or detect and schedule awaitables deliberately.

Tests should cover these as observable contract decisions, not as accidental implementation details.

### 4.9 Strategy registries and signature validation

A registry maps stable names to implementations and is covered more deeply in Lesson 05. For a small application, an injected mapping is often sufficient. Validate unknown names at startup and validate callable contracts where feasible.

```python
from collections.abc import Callable
from typing import TypeAlias

RetryFunction: TypeAlias = Callable[[int, Exception], bool]
RETRY_POLICIES: dict[str, RetryFunction] = {
    "never": lambda attempt, error: False,
    "timeouts": lambda attempt, error: isinstance(error, TimeoutError) and attempt < 3,
}

def choose_policy(name: str) -> RetryFunction:
    try:
        return RETRY_POLICIES[name]
    except KeyError:
        raise ValueError(f"unknown retry policy {name!r}; choose from {sorted(RETRY_POLICIES)}") from None

print(choose_policy("timeouts")(1, TimeoutError()))
```

Expected output: `True`.

Type hints and static checking catch many mismatches but do not validate arbitrary runtime plugin callables. If callables come from third parties, test their contract and avoid depending on fragile introspection alone; decorators and builtins may not expose signatures uniformly.

## 5. Advanced event and command architecture

### 5.1 Async events, bounded queues, and backpressure

An asynchronous event bus can enqueue events and let workers deliver them. A **bounded queue** applies backpressure: producers wait or reject/drop work when capacity is exhausted. An unbounded queue turns a slow subscriber into unbounded memory growth.

```python
import asyncio
from dataclasses import dataclass

@dataclass(frozen=True)
class MetricEvent:
    name: str
    value: float

async def consume(queue: asyncio.Queue[MetricEvent | None]) -> None:
    while True:
        event = await queue.get()
        try:
            if event is None:
                return
            print(f"{event.name}={event.value}")
        finally:
            queue.task_done()

async def demo_queue() -> None:
    queue: asyncio.Queue[MetricEvent | None] = asyncio.Queue(maxsize=2)
    async with asyncio.TaskGroup() as group:
        group.create_task(consume(queue))
        await queue.put(MetricEvent("fetch.success", 1.0))
        await queue.put(None)
        await queue.join()

asyncio.run(demo_queue())
```

Expected output: `fetch.success=1.0`.

The bounded queue does not itself guarantee durable delivery. In-memory events are lost on process failure. Delivery guarantees need precise language:

- **At-most-once:** an event may be lost, but is not intentionally redelivered.
- **At-least-once:** retries may duplicate delivery; consumers need idempotency.
- **Effectively-once business effect:** usually achieved by durable deduplication/transactions around the effect, not by magical exactly-once transport.

`asyncio.TaskGroup` gives structured concurrency: child tasks are awaited and failures are surfaced as the group exits. It does not automatically isolate each handler's exception; choose whether one handler failure cancels siblings, gets collected, or is routed to an error queue. Graceful shutdown needs producer stop, sentinel/drain policy, `queue.join()`, and task cancellation rules.

For cross-thread dispatch, use `queue.Queue` or thread-safe loop scheduling rather than mutating a normal subscriber list from arbitrary threads. A synchronous event bus with a lock can protect registry mutation, but callbacks should generally execute outside the lock to avoid deadlocks and lock convoying. Copy-on-write subscriber snapshots are useful when publishes are frequent and subscriptions rare.

### 5.2 Hook systems and `pluggy`

A hook system is useful when an extension point should call multiple implementations in a defined order. `pluggy`, used by pytest, provides hook specifications and implementations, including concepts such as `firstresult` (stop at the first non-`None` result) and hook wrappers (surround a hook call with before/after behavior). A registry answers “which implementation is selected?”; a hook system often answers “which registered implementations should run, and how are their results combined?”

Use a hook framework when the extension contract and ecosystem justify it. For a handful of callbacks, a typed list of callables is easier to understand. Document payload mutability, ordering, exception policy, sync/async behavior, and plugin compatibility. Test hooks through public extension points rather than reaching into private registry state.

### 5.3 Strategy patterns in AI and data systems

Strategies are natural for:

- scoring functions for search results,
- retrievers and rerankers,
- sampling algorithms,
- evaluation metrics,
- prompt selection or routing policies,
- retry/backoff and circuit-breaker policies.

Prefer pure strategies where practical: same input and configuration yields the same output, with no hidden network or global-state dependency. Pure functions are easier to test, cache, compare, and reproduce. For generic input/output strategies, a protocol can make the contract explicit:

```python
from typing import Protocol, TypeVar

In_contra = TypeVar("In_contra", contravariant=True)
Out_co = TypeVar("Out_co", covariant=True)

class Strategy(Protocol[In_contra, Out_co]):
    def __call__(self, value: In_contra, /) -> Out_co: ...
```

A retrieval strategy might accept a query and return ranked document IDs; an evaluation strategy might accept a prediction/reference pair and return a score. Type the meaningful boundary, but avoid over-generalizing a one-use function into a framework.

### 5.4 Policy objects, fake clocks, and deterministic tests

Retry and circuit-breaker policies often depend on attempt number, exception classification, elapsed time, and jitter. Inject time/sleep/randomness rather than testing against wall-clock delays. A fake clock can advance instantly and make boundary cases reproducible. Keep policy (the decision) separate from execution (performing the sleep/request), so tests can prove the policy without waiting.

A deterministic policy test should cover: no retry for permanent failures; retry only up to the configured limit; deadline exhaustion; and the exact delay sequence. Production retry loops also need a total deadline, cancellation handling, observability, and a cap on attempts. The integrated example rejects negative or non-finite delays returned by a custom policy. Backoff without jitter can synchronize many clients and create a thundering herd.

### 5.5 Observability and correlation IDs

Events can feed structured logs, metrics, and traces. `contextvars` can carry a correlation ID through async call chains without adding the parameter to every function. Context is not a replacement for explicit command identity, and propagation across process/queue boundaries must be serialized explicitly.

```python
from contextvars import ContextVar
from uuid import uuid4

correlation_id: ContextVar[str] = ContextVar("correlation_id", default="-")

def handle_request() -> str:
    token = correlation_id.set(str(uuid4()))
    try:
        return f"request_id={correlation_id.get()}"
    finally:
        correlation_id.reset(token)

print(handle_request().startswith("request_id="))
```

Expected output: `True`.

Always reset context tokens in `finally`; otherwise a reused task context can leak identity between operations. Log structured fields such as command ID, attempt, outcome, duration, and correlation ID. Avoid logging secrets or full sensitive payloads.

### 5.6 Production anti-patterns

- **Callback hell:** deeply nested callbacks obscure sequencing. Prefer named functions, a pipeline, or structured async code.
- **Hidden global event bus:** makes tests order-dependent and creates hidden coupling. Inject a bus or scope it to the application.
- **Observer mutates publisher state:** subscribers should generally receive immutable event snapshots and not mutate the object being published.
- **Oversized commands:** storing megabytes of data in a queue command increases serialization, retention, and privacy risks. Store a stable reference to payload data when safe, with explicit retention/access rules.
- **State explosion:** a state enum with hundreds of ad hoc combinations is often a sign to decompose state, define invariants, or use a workflow engine.
- **Retry everything:** retries can multiply side effects and load. Classify failures, require idempotency for effectful operations, and cap time/attempts.

## 6. Comparative decision table

| Need | First choice | Consider another approach when | Main risk |
|---|---|---|---|
| Swap one algorithm | Function Strategy | Strategy has state or multiple related operations | Over-engineering a single variant |
| Notify independent listeners | Observer/event bus | One collaborator is required for correctness | Hidden flow, leaks, exception coupling |
| Queue or audit an operation | Command object or `partial` | No lifecycle or identity is needed | False assumptions about replay/undo |
| Centralize fixed algorithm with variable steps | Function injection | A coherent subclass family already exists | Fragile base-class hooks |
| Enforce legal state transitions | Enum + transition table | Complex workflow/persistence/visualization is required | Missing transitions/state explosion |
| Apply ordered cross-cutting checks | Middleware/Chain | Only one simple conditional exists | Order-dependent bugs and indirection |
| Traverse data lazily | Generator/iterator | Data must be random-access or replayable | Single-pass consumption surprises |
| Add type-specific operations | `singledispatch`/`match` | Behavior naturally belongs to each type | Fallbacks hiding unsupported values |
| Coordinate many independent components | Mediator/hook system | A direct call is clearer | God mediator and opaque control flow |
| Restore prior local state | Immutable snapshot/Memento | State includes external irreversible effects | Shallow snapshots and invalid rollback |

## 7. `fetchkit` implementation

This integrated example uses deterministic dependencies only. It has a pluggable retry policy, request/retry/success/error events, and a replayable command with an idempotency key. The idempotency store shown here is in-memory and process-local; it demonstrates semantics, not a production durable exactly-once system.

### 7.1 Complete implementation

Save as `fetchkit_behavioural.py`.

```python
from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
import logging
from math import isfinite
from time import monotonic, sleep
from typing import Protocol
from urllib.parse import urlsplit

logger = logging.getLogger(__name__)

def validate_http_url(url: object) -> str:
    if not isinstance(url, str):
        raise ValueError("url must be a string")
    try:
        parts = urlsplit(url)
        port = parts.port  # accessing .port validates its syntax and range
    except ValueError as exc:
        raise ValueError("url must be a valid HTTP(S) URL") from exc
    if parts.scheme not in {"http", "https"} or not parts.hostname:
        raise ValueError("url must be a valid HTTP(S) URL with a hostname")
    if port == 0:
        raise ValueError("url port must be between 1 and 65535")
    return url


class FetchError(Exception):
    """Base exception for fetchkit failures."""


class TransientFetchError(FetchError):
    """A failure that policy may permit retrying."""


class PermanentFetchError(FetchError):
    """A failure that should not be retried."""


class HttpClient(Protocol):
    def get(self, url: str, *, timeout: float) -> str: ...


class Clock(Protocol):
    def monotonic(self) -> float: ...
    def sleep(self, seconds: float) -> None: ...


@dataclass(frozen=True)
class SystemClock:
    def monotonic(self) -> float:
        return monotonic()

    def sleep(self, seconds: float) -> None:
        sleep(seconds)


@dataclass(frozen=True)
class RetryContext:
    attempt: int
    error: Exception
    elapsed_seconds: float


class RetryPolicy(Protocol):
    def should_retry(self, context: RetryContext) -> bool: ...
    def delay_seconds(self, context: RetryContext) -> float: ...


@dataclass(frozen=True)
class ExponentialRetry:
    max_attempts: int = 3
    base_delay_seconds: float = 0.0

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        if not isfinite(self.base_delay_seconds) or self.base_delay_seconds < 0:
            raise ValueError("base_delay_seconds must be finite and >= 0")

    def should_retry(self, context: RetryContext) -> bool:
        return (
            isinstance(context.error, TransientFetchError)
            and context.attempt < self.max_attempts
        )

    def delay_seconds(self, context: RetryContext) -> float:
        return self.base_delay_seconds * (2 ** (context.attempt - 1))


@dataclass(frozen=True)
class FetchEvent:
    name: str
    url: str
    attempt: int = 0
    detail: str = ""


EventHandler = Callable[[FetchEvent], None]
EventErrorHandler = Callable[[FetchEvent, Exception], None]


class EventBus:
    """Synchronous registration-order delivery with isolated handler errors."""

    def __init__(self, on_handler_error: EventErrorHandler | None = None) -> None:
        self._subscribers: dict[str, list[EventHandler]] = {}
        self._on_handler_error = on_handler_error

    def subscribe(self, event_name: str, handler: EventHandler) -> Callable[[], None]:
        handlers = self._subscribers.setdefault(event_name, [])
        handlers.append(handler)
        active = True

        def unsubscribe() -> None:
            nonlocal active
            if not active:
                return
            active = False
            try:
                handlers.remove(handler)
            except ValueError:
                pass
        return unsubscribe

    def publish(self, event: FetchEvent) -> None:
        # Snapshot semantics: changes affect later publishes, not this delivery.
        for handler in tuple(self._subscribers.get(event.name, ())):
            try:
                handler(event)
            except Exception as exc:
                if self._on_handler_error is None:
                    logger.error(
                        "event subscriber failed for %s",
                        event.name,
                        exc_info=(type(exc), exc, exc.__traceback__),
                    )
                    continue
                try:
                    self._on_handler_error(event, exc)
                except Exception:
                    # Report failure of the reporting hook too; never let it
                    # prevent later subscribers from receiving the event.
                    logger.exception("event error-reporting hook failed")
                    logger.error(
                        "original event subscriber failure for %s",
                        event.name,
                        exc_info=(type(exc), exc, exc.__traceback__),
                    )
                # Telemetry failure does not fail the fetch operation.


@dataclass(frozen=True)
class FetchConfig:
    timeout_seconds: float = 5.0

    def __post_init__(self) -> None:
        if not isfinite(self.timeout_seconds) or self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be finite and > 0")


@dataclass(frozen=True)
class FetchResult:
    url: str
    body: str
    attempts: int


class Fetcher:
    def __init__(
        self,
        *,
        client: HttpClient,
        cache: dict[str, FetchResult],
        clock: Clock,
        retry_policy: RetryPolicy,
        config: FetchConfig = FetchConfig(),
        events: EventBus | None = None,
    ) -> None:
        self._client = client
        self._cache = cache
        self._clock = clock
        self._retry_policy = retry_policy
        self._config = config
        self._events = events or EventBus()

    def fetch(self, url: str, *, idempotency_key: str | None = None) -> FetchResult:
        validate_http_url(url)
        if idempotency_key is not None and (
            not isinstance(idempotency_key, str) or not idempotency_key.strip()
        ):
            raise ValueError("idempotency_key must be a non-empty string when supplied")
        cache_key = url if idempotency_key is None else idempotency_key
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            # A key reused for a different URL is a caller error, not a cache hit.
            if cached.url != url:
                raise ValueError("idempotency key was already used for a different URL")
            return cached

        started = self._clock.monotonic()
        attempt = 0
        while True:
            attempt += 1
            self._events.publish(FetchEvent("request", url, attempt))
            try:
                body = self._client.get(url, timeout=self._config.timeout_seconds)
            except Exception as raw_error:
                if isinstance(raw_error, FetchError):
                    error = raw_error
                elif isinstance(raw_error, (TimeoutError, ConnectionError)):
                    error = TransientFetchError(str(raw_error))
                else:
                    error = PermanentFetchError(str(raw_error))
                context = RetryContext(attempt, error, self._clock.monotonic() - started)
                if self._retry_policy.should_retry(context):
                    delay = self._retry_policy.delay_seconds(context)
                    if not isfinite(delay) or delay < 0:
                        raise ValueError("retry policy returned a non-finite or negative delay")
                    self._events.publish(FetchEvent("retry", url, attempt, str(error)))
                    if delay:
                        self._clock.sleep(delay)
                    continue
                self._events.publish(FetchEvent("error", url, attempt, str(error)))
                if error is raw_error:
                    raise
                raise error from raw_error
            else:
                result = FetchResult(url=url, body=body, attempts=attempt)
                self._cache[cache_key] = result
                self._events.publish(FetchEvent("success", url, attempt))
                return result

    def invalidate(self, key: str) -> None:
        self._cache.pop(key, None)


@dataclass(frozen=True)
class FetchCommand:
    url: str
    idempotency_key: str

    def __post_init__(self) -> None:
        validate_http_url(self.url)
        if not isinstance(self.idempotency_key, str) or not self.idempotency_key.strip():
            raise ValueError("idempotency_key must be a non-empty string")

    def to_dict(self) -> dict[str, str]:
        return {"version": "1", "url": self.url, "idempotency_key": self.idempotency_key}

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> FetchCommand:
        if data.get("version") != "1":
            raise ValueError("unsupported command version")
        try:
            url = data["url"]
            idempotency_key = data["idempotency_key"]
        except KeyError as exc:
            raise ValueError(f"missing command field: {exc.args[0]}") from exc
        if not isinstance(url, str) or not isinstance(idempotency_key, str):
            raise ValueError("url and idempotency_key must be strings")
        return cls(url=url, idempotency_key=idempotency_key)

    def execute(self, fetcher: Fetcher) -> FetchResult:
        return fetcher.fetch(self.url, idempotency_key=self.idempotency_key)


# Composition root: construct dependencies and wire the object graph in one place.
def build_fetcher(
    *, client: HttpClient, cache: dict[str, FetchResult] | None = None,
    clock: Clock | None = None, retry_policy: RetryPolicy | None = None,
    config: FetchConfig = FetchConfig(), events: EventBus | None = None,
) -> Fetcher:
    return Fetcher(
        client=client,
        cache={} if cache is None else cache,
        clock=SystemClock() if clock is None else clock,
        retry_policy=ExponentialRetry() if retry_policy is None else retry_policy,
        config=config,
        events=events,
    )
```

### 7.2 Execution flow and design decisions

1. `FetchCommand` validates the URL and stable idempotency key at construction.
2. `execute()` delegates to `Fetcher`; the command does not own an HTTP client or global configuration.
3. `Fetcher` validates its URL, checks the injected cache, and emits `request` before each attempt.
4. The injected `RetryPolicy` decides whether a classified transient error can be retried. The policy does not sleep; `Fetcher` uses the injected clock to execute its chosen delay.
5. `retry`, `success`, and `error` events are emitted at explicit points. The synchronous bus isolates subscriber exceptions and delivers to a snapshot in registration order.
6. The successful result is cached under the idempotency key (or URL when no key is supplied). The included cache is deliberately simple; it is not a multi-process durable idempotency store. It also detects accidental reuse of the same key for a different URL within this fetcher.

**Retry safety:** this example is designed for HTTP GET-style retrieval. It classifies `TimeoutError` and `ConnectionError` as potentially transient, preserves `FetchError` classifications, and treats other unclassified exceptions as permanent. Production adapters should classify vendor-specific connection resets and HTTP status errors according to the client's contract. Never blindly retry an operation that may have committed a non-idempotent side effect.

**Cache caveat:** the key above allows a command's result to be replayed locally, but an idempotency key should normally be scoped by operation and tenant and backed by durable storage with atomic claim/write semantics. This demonstration rejects reuse of the same key for a different URL. The plain dictionary is neither durable nor a concurrency-safe idempotency ledger: concurrent calls can both miss the cache and execute the client before either stores a result. Invalidate by the exact key used to cache the result; invalidating a URL will not invalidate an entry cached under a distinct idempotency key.

### 7.3 Deterministic fakes and tests

Save as `test_fetchkit_behavioural.py` and run `python -m pytest -q`.

```python
import pytest

from fetchkit_behavioural import (
    EventBus, ExponentialRetry, FetchCommand, FetchConfig, FetchEvent,
    Fetcher, FetchResult, PermanentFetchError, RetryContext,
    TransientFetchError, build_fetcher,
)


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


class FakeClient:
    def __init__(self, outcomes: list[str | Exception]) -> None:
        self.outcomes = list(outcomes)
        self.calls: list[tuple[str, float]] = []

    def get(self, url: str, *, timeout: float) -> str:
        self.calls.append((url, timeout))
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def make_fetcher(outcomes: list[str | Exception], *, bus: EventBus | None = None):
    client = FakeClient(outcomes)
    clock = FakeClock()
    fetcher = build_fetcher(
        client=client, clock=clock,
        retry_policy=ExponentialRetry(max_attempts=3, base_delay_seconds=0.25),
        config=FetchConfig(timeout_seconds=2.0), events=bus,
    )
    return fetcher, client, clock


def test_retry_then_success_uses_fake_clock_and_emits_ordered_events():
    seen: list[str] = []
    bus = EventBus()
    for name in ("request", "retry", "success", "error"):
        bus.subscribe(name, lambda event, name=name: seen.append(f"{name}:{event.attempt}"))
    fetcher, client, clock = make_fetcher([TimeoutError("temporary"), "payload"], bus=bus)

    result = fetcher.fetch("https://example.test/data")

    assert result == FetchResult("https://example.test/data", "payload", 2)
    assert len(client.calls) == 2
    assert clock.sleeps == [0.25]
    assert seen == ["request:1", "retry:1", "request:2", "success:2"]


def test_command_serialization_and_replay_use_same_idempotency_key():
    fetcher, client, _ = make_fetcher(["payload"])
    command = FetchCommand("https://example.test/data", "tenant-a:job-42")
    restored = FetchCommand.from_dict(command.to_dict())

    first = restored.execute(fetcher)
    second = restored.execute(fetcher)

    assert first == second
    assert len(client.calls) == 1


def test_empty_idempotency_key_and_invalid_url_are_rejected():
    with pytest.raises(ValueError, match="idempotency_key"):
        FetchCommand("https://example.test", "  ")
    fetcher, _, _ = make_fetcher(["unused"])
    with pytest.raises(ValueError, match="url"):
        fetcher.fetch("file:///etc/passwd")
    with pytest.raises(ValueError, match="hostname"):
        FetchCommand("https://", "job-1")
    with pytest.raises(ValueError, match="valid HTTP"):
        FetchCommand("https://example.test:bad", "job-1")
    with pytest.raises(ValueError, match="idempotency_key"):
        fetcher.fetch("https://example.test", idempotency_key="  ")


def test_invalid_config_is_rejected_at_construction():
    with pytest.raises(ValueError, match="timeout_seconds"):
        FetchConfig(timeout_seconds=0)
    with pytest.raises(ValueError, match="timeout_seconds"):
        FetchConfig(timeout_seconds=float("inf"))


def test_permanent_error_is_not_retried():
    fetcher, client, clock = make_fetcher([PermanentFetchError("bad request")])
    with pytest.raises(PermanentFetchError):
        fetcher.fetch("https://example.test/data")
    assert len(client.calls) == 1
    assert clock.sleeps == []


def test_unclassified_client_error_is_permanent_not_retried():
    fetcher, client, clock = make_fetcher([ValueError("invalid response")])
    with pytest.raises(PermanentFetchError, match="invalid response"):
        fetcher.fetch("https://example.test/data")
    assert len(client.calls) == 1
    assert clock.sleeps == []


def test_serialized_command_rejects_wrong_field_types():
    with pytest.raises(ValueError, match="must be strings"):
        FetchCommand.from_dict({"version": "1", "url": 42, "idempotency_key": "job-1"})
    with pytest.raises(ValueError, match="missing command field"):
        FetchCommand.from_dict({"version": "1", "url": "https://example.test"})


def test_unsubscribe_is_idempotent_and_stops_future_delivery():
    bus = EventBus()
    seen: list[str] = []
    unsubscribe = bus.subscribe("success", lambda event: seen.append(event.url))
    unsubscribe()
    unsubscribe()
    bus.publish(FetchEvent("success", "https://example.test"))
    assert seen == []


def test_subscriber_exception_is_reported_but_does_not_block_later_subscribers():
    failures: list[str] = []
    seen: list[str] = []
    bus = EventBus(on_handler_error=lambda event, exc: failures.append(str(exc)))
    bus.subscribe("success", lambda event: (_ for _ in ()).throw(RuntimeError("observer failed")))
    bus.subscribe("success", lambda event: seen.append(event.url))

    bus.publish(FetchEvent("success", "https://example.test"))

    assert failures == ["observer failed"]
    assert seen == ["https://example.test"]


def test_error_reporter_failure_is_logged_and_delivery_continues(caplog):
    def broken_reporter(event, exc):
        raise RuntimeError("reporter failed")

    bus = EventBus(on_handler_error=broken_reporter)
    seen: list[str] = []
    bus.subscribe("success", lambda event: (_ for _ in ()).throw(ValueError("handler failed")))
    bus.subscribe("success", lambda event: seen.append("later"))

    with caplog.at_level("ERROR"):
        bus.publish(FetchEvent("success", "https://example.test"))

    assert seen == ["later"]
    assert "event error-reporting hook failed" in caplog.text
    assert "original event subscriber failure" in caplog.text


def test_registration_order_and_snapshot_semantics_when_unsubscribing_during_publish():
    bus = EventBus()
    seen: list[str] = []
    unsubscribe_second = lambda: None
    def first(event: FetchEvent) -> None:
        seen.append("first")
        unsubscribe_second()
    bus.subscribe("success", first)
    unsubscribe_second = bus.subscribe("success", lambda event: seen.append("second"))
    bus.subscribe("success", lambda event: seen.append("third"))

    bus.publish(FetchEvent("success", "https://example.test"))
    assert seen == ["first", "second", "third"]  # already in snapshot
    seen.clear()
    bus.publish(FetchEvent("success", "https://example.test"))
    assert seen == ["first", "third"]


def test_reentrant_publication_is_nested_and_finite():
    bus = EventBus()
    seen: list[str] = []
    def on_start(event: FetchEvent) -> None:
        seen.append("start")
        bus.publish(FetchEvent("success", event.url))
    bus.subscribe("request", on_start)
    bus.subscribe("success", lambda event: seen.append("success"))

    bus.publish(FetchEvent("request", "https://example.test"))
    assert seen == ["start", "success"]


def test_invalidate_uses_the_cache_key():
    fetcher, client, _ = make_fetcher(["first", "second"])
    url = "https://example.test/data"
    assert fetcher.fetch(url).body == "first"
    fetcher.invalidate(url)
    assert fetcher.fetch(url).body == "second"
    assert len(client.calls) == 2


def test_idempotency_key_reuse_for_a_different_url_is_rejected():
    fetcher, client, _ = make_fetcher(["first"])
    fetcher.fetch("https://example.test/a", idempotency_key="same-key")
    with pytest.raises(ValueError, match="different URL"):
        fetcher.fetch("https://example.test/b", idempotency_key="same-key")
    assert len(client.calls) == 1


def test_retry_policy_boundaries():
    policy = ExponentialRetry(max_attempts=2, base_delay_seconds=0.5)
    transient = RetryContext(1, TransientFetchError("temporary"), 0.0)
    last_attempt = RetryContext(2, TransientFetchError("temporary"), 0.0)
    permanent = RetryContext(1, PermanentFetchError("permanent"), 0.0)
    assert policy.should_retry(transient)
    assert not policy.should_retry(last_attempt)
    assert not policy.should_retry(permanent)
    assert policy.delay_seconds(transient) == 0.5
```

These tests intentionally pin down behavior: event handlers run in registration order; unsubscription during publication affects later publications but not the current snapshot; re-entrant events run immediately (nested/depth-first); observer exceptions are reported and isolated; a permanent error is not retried; and a command replay returns the cached result for the same key in this process-local demonstration.

### 7.4 Wrapper and policy alternatives

The retry policy is a Strategy because `Fetcher` delegates the decision to an injected contract. A function-based variant is also valid:

```python
from collections.abc import Callable

RetryPredicate = Callable[[int, Exception], bool]

def retry_transient(attempt: int, error: Exception) -> bool:
    return isinstance(error, TransientFetchError) and attempt < 3

policy: RetryPredicate = retry_transient
print(policy(1, TransientFetchError("temporary")))
```

Expected output: `True`.

Use a function when the policy needs only its arguments. Use a protocol/class when decision and delay are related operations or the policy has immutable configuration. Both can be correct; consistency and clear typing matter more than choosing a class by default.

## 8. Testing and hands-on exercises

Work through the exercises in order. The expected outcomes are part of the task; write tests rather than relying on visual inspection.

### Exercise 1 — Replace a three-branch conditional with Strategy

Given `if kind == "lexical"`, `elif kind == "semantic"`, and `else`, create a mapping from validated names to scoring functions. Add an unknown-name error that lists supported values.

**Expected outcome:** adding a new score implementation does not require editing the selection function; tests cover every strategy and unknown names.

### Exercise 2 — Add a bounded async event queue

Adapt the async queue example so the queue has capacity one. Make a consumer wait on an `asyncio.Event`, enqueue one event, then demonstrate that a second producer blocks until the consumer proceeds.

**Expected outcome:** backpressure is observable without unbounded memory or real network calls. Ensure tasks are awaited and queue items call `task_done()` exactly once.

### Exercise 3 — Add a deadline-aware retry policy

Extend `RetryContext` with a deadline or total budget. Use `FakeClock` to test that a retry is rejected when the next delay would exceed the deadline.

**Expected outcome:** tests run instantly, use no wall-clock sleep, and verify the exact retry boundary.

### Exercise 4 — Implement an inverse command

Extend `TextBuffer` with a `DeleteText` command that records the deleted text before removal. Make undo restore that exact text and redo delete it again.

**Expected outcome:** insertion and deletion round-trip correctly; invalid positions fail; history clears redo after a new command following undo.

### Exercise 5 — Contract-test event subscribers

Write tests for no delivery after unsubscribe, duplicate registration behavior, handler exceptions, re-entrant publication, and ordering. Decide and document whether duplicate registration is allowed.

**Expected outcome:** the bus contract is explicit and tests do not depend on private data structures.

### Exercise 6 — Choose a command idempotency scope

Explain whether a key should be scoped by tenant, operation type, and API version. Simulate two commands with the same key but different URLs.

**Expected outcome:** the integrated example rejects a key reused for a different URL in the same fetcher. Explain why a production idempotency store also needs tenant/operation scope, atomic persistence, expiration policy, and concurrency handling.

### Exercise 7 — Compare function and class strategies

Implement the same retry decision once as a function and once as a frozen policy dataclass. Compare signature clarity, configuration, testability, and extension cost.

**Expected outcome:** explain why neither style is inherently superior; choose the lightest interface that fits actual variation.

## 9. Common mistakes and troubleshooting

The roadmap's required mistakes are:

1. **Subscribers that raise and break other subscribers.** Decide whether event delivery is fail-fast or isolated. For operational events, report subscriber failures through a separate error channel; do not silently swallow them.
2. **Mutating the subscriber list while iterating.** Publish from a snapshot or use a deliberate concurrency-safe registry. Document that a removed handler may still run in the in-flight snapshot.
3. **Using inheritance (Template Method) where passing a function is simpler.** Keep fixed control flow in one place and inject only the variable step when that is sufficient.

Additional production pitfalls:

- Treating every exception as transient and retrying unsafe operations.
- Assuming an idempotency key works without atomic receiver-side deduplication.
- Claiming commands are undoable when the side effect has no valid inverse.
- Publishing mutable event payloads that subscribers can change under one another.
- Forgetting to unsubscribe long-lived bound-method subscribers and retaining entire object graphs.
- Making re-entrant publication unbounded or accidentally recursive.
- Confusing synchronous callbacks with async handlers and dropping coroutine objects.
- Using an unbounded queue and allowing slow subscribers to exhaust memory.
- Assuming in-memory queues, command histories, or caches survive process failure.
- Adding a global event bus or a registry that hides dependencies from tests.
- Making commands contain large sensitive payloads rather than stable references with access controls.
- Failing to record command schema versions or validate replayed serialized input.
- Overusing a state machine framework for a handful of simple transitions—or maintaining an enormous untested transition table.

When debugging, first identify the promised semantics: delivery order, retry classification, deduplication scope, command reversibility, queue capacity, and shutdown behavior. Then add a deterministic test for that contract before changing the implementation.

## 10. Self-check questions and model answers

### 1. Turn a three-branch `if kind == ...` into a Strategy implemented as functions and justify.

**Model answer:** Define a typed callable contract, map validated names to functions, and select the function once at configuration/startup. For example, `SCORERS = {"length": score_length, "priority": score_priority}` and `scorer = SCORERS[name]`. Raise a helpful `ValueError` for unknown names. This is justified when the variants are genuine alternatives that should be independently tested or extended; a short stable conditional may be simpler when no variation is expected.

### 2. Where can an observer-based design leak memory and how do you prevent it?

**Model answer:** A long-lived event bus holds strong references to registered handlers. A bound method holds its instance, so a subscription can keep an otherwise unused object alive. Return and use an unsubscribe handle, scope the bus to a shorter lifecycle, or use weak references such as `weakref.WeakMethod` when disappearing subscribers are acceptable. Test lifecycle behavior; weak references are not a substitute for clear ownership.

### 3. Implement undo/redo for a small text editor using commands and test it.

**Model answer:** Use immutable `InsertText(position, text)` commands, a buffer that applies/validates them, and separate undo/redo stacks. Undo verifies that the inserted substring is still present before removing it; redo reapplies it. A new command after undo clears the redo stack. Tests cover execute → undo → redo, invalid positions, empty history, and stale history. For operations without a valid inverse, use a compensating action or do not offer undo.

## 11. Summary and completion checklist

Behavioural patterns organize variation and collaboration. Strategy selects an algorithm; Observer publishes facts to interested listeners; Command gives an operation identity and lifecycle. State makes legal transitions explicit, Chain of Responsibility composes ordered handlers, generators provide lazy iteration, `singledispatch`/`match` offer Pythonic Visitor alternatives, Mediator centralizes coordination, and Memento captures restorable state.

Before moving on, verify that you can:

- [ ] Explain Strategy, Observer, and Command in terms of the problem each solves.
- [ ] Implement a function-based strategy and explain when a policy object is warranted.
- [ ] Explain why `sorted(key=...)` is a strategy-taking API.
- [ ] Define event ordering, subscriber exceptions, re-entrancy, and unsubscribe semantics.
- [ ] Explain why event subscribers can leak memory and how lifecycle ownership helps.
- [ ] Build and serialize a small command with validated fields and an idempotency key.
- [ ] Distinguish retryability, idempotency, replay, undo, and compensation.
- [ ] Test retry policies with a fake clock instead of real sleeps.
- [ ] Explain bounded queues, backpressure, at-least-once delivery, and idempotent consumers.
- [ ] Identify when `TaskGroup`, `pluggy`, a state-machine library, or a direct function call is appropriate.
- [ ] Run the `fetchkit` tests and explain every asserted contract.

## 12. Authoritative references

Use the official documentation as the source of truth for Python runtime behavior and third-party framework semantics:

- Python `collections.abc` and callable typing: https://docs.python.org/3/library/collections.abc.html and https://docs.python.org/3/library/typing.html
- `functools.partial` and `singledispatch`: https://docs.python.org/3/library/functools.html
- Generators and iterator protocol: https://docs.python.org/3/reference/datamodel.html#emulating-container-types
- `dataclasses`: https://docs.python.org/3/library/dataclasses.html
- `enum`: https://docs.python.org/3/library/enum.html
- `contextvars`: https://docs.python.org/3/library/contextvars.html
- `weakref.WeakMethod`: https://docs.python.org/3/library/weakref.html#weakref.WeakMethod
- `asyncio.Queue` and task groups: https://docs.python.org/3/library/asyncio-queue.html and https://docs.python.org/3/library/asyncio-task.html#task-groups
- `queue.Queue` for thread coordination: https://docs.python.org/3/library/queue.html
- `pluggy` documentation: https://pluggy.readthedocs.io/
- HTTP method semantics (including safety and idempotency): https://www.rfc-editor.org/rfc/rfc9110.html
- pytest documentation: https://docs.pytest.org/

This lesson follows Module 1.20's Lesson 04 syllabus. Detailed plugin discovery belongs to Lesson 05; public API contracts, deprecation, and sans-I/O design are handled in later lessons. Distributed queues, durable workflow execution, and AI-agent tool orchestration are introduced here only to establish the behavioural-pattern concepts needed in later stages.
