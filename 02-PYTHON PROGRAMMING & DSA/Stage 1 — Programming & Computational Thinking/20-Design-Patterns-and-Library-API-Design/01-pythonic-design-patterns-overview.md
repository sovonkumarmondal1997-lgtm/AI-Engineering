# Pythonic Design Patterns Overview

> **Stage:** 1 — Programming & Computational Thinking  
> **Module:** 20 — Design Patterns and Library API Design  
> **Lesson:** 01 — Pythonic design patterns overview  
> **Target runtime:** Python 3.12+  
> **Level:** Beginner foundations → intermediate pattern selection → advanced design judgment  
> **Case study:** `fetchkit`, a small data-fetching library

## 1. Learning objectives

By the end of this lesson, you should be able to:

- Define a design pattern in terms of its **name, problem, solution, and consequences**.
- Distinguish the GoF creational, structural, and behavioural families, and map every classic GoF pattern to a plausible Pythonic expression.
- Recognise when Python functions, closures, modules, decorators, generators, context managers, duck typing, `Protocol`, `dataclasses`, and `enum` make a class-heavy pattern unnecessary.
- Recognise architectural patterns used in data and AI systems without confusing them with the GoF catalogue.
- Decide when an abstraction earns its cost, using real variants or measurable design pain as evidence.
- Read patterns in established Python libraries and explain the design forces they address.
- Apply SOLID, composition, interface-oriented design, the Law of Demeter, YAGNI, and the rule of three without turning them into rigid laws.
- Record a design choice with context, forces, decision, and alternatives, then revisit it as requirements evolve.
- Evolve the `fetchkit` example while preserving simple, testable boundaries.

## 2. Prerequisites and required knowledge

This lesson assumes familiarity with the following Stage 1 topics. If one is unfamiliar, review the indicated lesson before treating the corresponding advanced section as mastery material.

| Prerequisite | Roadmap location | Why it matters here |
|---|---|---|
| Encapsulation, abstraction, composition | Module 1.8, lesson 01 | Patterns organise responsibilities and dependencies. |
| Inheritance and polymorphism | Module 1.8, lesson 02 | Helps compare subclass-based designs with composition. |
| Protocols and dependency inversion | Module 1.8, lesson 05 | Makes implementation boundaries explicit without requiring inheritance. |
| Side effects and layered design | Module 1.8, lessons 07–08 | Separates HTTP, cache, parsing, and output effects. |
| Data model, ABCs, and mixins | Module 1.11 | Helps reason about Python interfaces and object behaviour. |
| Decorators, registries, and DSLs | Module 1.12 | Relevant to wrappers and extension points. |
| Signatures, errors, and deprecations | Module 1.15 | Patterns affect public contracts and error semantics. |
| Entry points and versioning | Module 1.18 | Relevant to third-party plugin systems. |
| Testing and mocking | Modules 1.7 and 1.16 | Lets us validate behaviour instead of trusting architecture diagrams. |
| Code smells and refactoring | Module 1.23 (preview) | Helps detect when an abstraction is harmful. |

**Suggested tools:** `uv`, `pytest`, `mypy --strict` or `pyright`, `ruff`, and optionally `hypothesis`. The examples in this lesson use the standard library unless otherwise stated. Code blocks marked **Runnable example** are intended to run as written on Python 3.12+; tables and architecture sketches are explanatory, not executable programs.

## 3. Why this topic matters

A design pattern is not a target to implement. It is a reusable explanation of a recurring design problem and a family of solutions with known consequences. Patterns help teams manage change, reduce accidental coupling, and communicate intent with a compact vocabulary: “use a strategy for the retry decision” communicates more than “add another function parameter and branch.”

Python changes the implementation choices. A Java-style Strategy may need an interface and several classes; in Python, a callable can often express the same variation. A classic Iterator can become a generator. A resource-lifetime class may be unnecessary when a context manager already provides deterministic cleanup. The design problem remains real even when the class diagram disappears.

Our running case study is `fetchkit`. Its conceptual flow is:

```text
URL → HTTP source → response bytes → parser → parsed records → output sink
             ↘ cache       ↘ retry policy / timeout
```

The first version should be simple. Later variants might use a fake HTTP source in tests, a cache, a CSV or JSON parser, retry policies, and different output sinks. The lesson is about choosing boundaries only when they solve a demonstrated problem; later lessons cover factory/builder, structural, behavioural, and plugin patterns in depth.

## 4. Beginner foundations

### 4.1 What counts as a design pattern?

**Definition and mental model.** A pattern is a named, reusable approach to a recurring design problem in a context. A useful description has four parts:

1. **Name** — a shared label, such as Strategy or Adapter.
2. **Problem** — the conditions that make the design difficult.
3. **Solution** — the shape of the collaboration or dependency structure.
4. **Consequences** — benefits, costs, constraints, and failure modes.

**Why it exists.** A pattern gives engineers a compact way to discuss a design and reuse experience. It does not guarantee correctness: the context and forces still matter.

**How it works.** The pattern directs responsibilities and dependencies. Strategy, for example, moves an algorithm that varies behind a stable callable/interface. The caller delegates to the selected algorithm rather than owning every branch.

**Minimal example — Strategy as a function (runnable):**

```python
from collections.abc import Callable, Iterable
from decimal import Decimal
from dataclasses import dataclass

@dataclass(frozen=True)
class Item:
    price: Decimal
    discount: Decimal = Decimal("0")

def total(items: Iterable[Item], pricing: Callable[[Item], Decimal]) -> Decimal:
    return sum((pricing(item) for item in items), start=Decimal("0"))

def regular_price(item: Item) -> Decimal:
    return item.price

def discounted_price(item: Item) -> Decimal:
    return item.price * (Decimal("1") - item.discount)

cart = [Item(Decimal("10.00"), Decimal("0.10")), Item(Decimal("5.00"))]
print(total(cart, regular_price))
print(total(cart, discounted_price))
```

Expected output:

```text
15.00
14.0000
```

The callable is the varying policy; `total` does not need a base class or a hierarchy. The function's type annotation documents the expected contract. A runtime `Protocol` or explicit validation may be warranted if strategies are supplied by external plugins, but is unnecessary for two local functions.

**Realistic engineering example.** `fetchkit` may choose between a conservative retry policy for ordinary HTTP reads and a no-retry policy for requests with non-repeatable side effects. A policy function can be injected and tested with a fake response.

**Use it when:** the same workflow needs genuinely different algorithms, policies, or behaviours. **Avoid it when:** there is one stable algorithm and no likely variation; a simple function is enough.

**Trade-offs and failure modes:** a strategy boundary improves testability and change isolation but adds indirection and a contract that must be understood. An overly generic `Callable[..., object]` hides the contract; an interface with one implementation and no realistic variation may be speculative.

**Simplest alternative:** one direct function. Introduce a strategy parameter only when the variation is meaningful or a test seam is valuable.

**Exercise:** add a `content_length` strategy that charges a fixed amount per byte. Expected outcome: `total` remains unchanged; only the passed callable changes.

### 4.2 The three GoF families

The classic Gang of Four (GoF) catalogue groups 23 patterns into three families. These are categories, not a ranking of importance.

| Family | Main question | Examples | Typical Pythonic options |
|---|---|---|---|
| **Creational** | How should objects be selected or constructed? | Factory Method, Abstract Factory, Builder, Prototype, Singleton | Functions, named constructors, registries, dataclasses, dependency injection, modules |
| **Structural** | How should components be composed or wrapped? | Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy | Composition, wrappers, `Protocol`, functions/decorators, module facades, caching |
| **Behavioural** | How should responsibilities and algorithms collaborate? | Strategy, Observer, Command, State, Iterator, Visitor, and others | Callables, generators, callbacks, event hooks, enums, dispatch tables, `match` |

**Mental model:** creational patterns control *which object and how it is made*; structural patterns control *how parts fit together*; behavioural patterns control *who does what and how decisions or events flow*.

**Why it matters:** family labels help locate a problem, but they do not decide the implementation. Python's built-in language and library features often provide a lighter solution.

**Exercise:** for each `fetchkit` change—choose a parser, wrap a source with caching, notify metrics on retries—identify the family. Expected answers: creational/selection, structural, behavioural respectively (the exact pattern depends on implementation).

### 4.3 Why patterns exist: change, coupling, and communication

- **Managing change:** put a likely-to-vary decision behind a boundary. If cache policy changes weekly but parsing is stable, keep them separate.
- **Reducing coupling:** depend on a small behaviour contract rather than a vendor's entire SDK. This reduces the number of modules that must change during a vendor migration.
- **Communicating intent:** a name such as Adapter signals that translation occurs at a boundary; Strategy says a policy is interchangeable; Observer says one event can notify multiple listeners.

A pattern does not remove coupling; it moves and makes it explicit. More interfaces mean more names, navigation, tests, and opportunities for mismatch. A boundary is useful only if it aligns with a real axis of change.

**Internal flow example:** when `fetchkit` calls a `Source` protocol, control enters the concrete HTTP adapter, performs I/O, and returns bytes. Tests can supply a fake source that returns known bytes without opening a socket. The boundary changes where I/O is performed, not the fact that I/O has side effects.

**When to use:** when a dependency is volatile, costly to exercise in tests, owned by another team/vendor, or has a different semantic contract. **When not to use:** to wrap every internal function merely to make the architecture look layered.

**Exercise:** name one likely-to-change part of a data-fetching library and one stable part. Expected outcome: a reasoned boundary, not a requirement to create two classes.

### 4.4 Python's pattern-reducing toolbox

#### First-class functions and closures

**Definition.** Functions are values: they can be assigned, passed, returned, and stored. A closure is a function that retains access to variables from its enclosing lexical scope.

**How it works.** Passing a function delegates behaviour. Returning a function can package configuration and state without defining a new class. This often replaces Strategy, Command, and small factories.

```python
from collections.abc import Callable

def make_prefixer(prefix: str) -> Callable[[str], str]:
    def apply(value: str) -> str:
        return f"{prefix}{value}"
    return apply

warning = make_prefixer("WARN: ")
print(warning("retrying"))
```

Expected output: `WARN: retrying`

**Engineering example:** a parser registry can map format names to parser functions. A closure can capture a validated configuration value for a small policy. Avoid closures that hide mutable state, retain large objects unexpectedly, or make debugging harder than a small named class.

**Use when:** the behaviour is small and the callable signature is clear. **Prefer a class when:** state has several fields, lifecycle matters, or a richer explicit API improves clarity. **Exercise:** create `make_key_normalizer(case_sensitive: bool)`; expected outcome: the returned function normalizes keys according to the captured option.

#### Modules as shared namespaces (and “singleton” caution)

Python imports normally cache a module object in `sys.modules` within an interpreter, so a module can provide one shared namespace and module-level functions/data. This is often enough for constants or stateless utilities; it is not a universal, process-wide singleton guarantee. Separate processes have separate module state; reloads, unusual import paths, and test isolation can complicate assumptions.

```python
# fetchkit/defaults.py
DEFAULT_TIMEOUT_SECONDS = 10.0
```

Consumers import the constant instead of constructing a `DefaultsManager` object. Do not use module globals for mutable per-request state or hidden service dependencies. Explicitly pass a cache/client when isolation, concurrency, or multiple configurations matter.

**Simplest alternative:** a constant in the module that owns it. **Exercise:** decide whether an HTTP client should be global or injected. Expected answer: inject it when tests, multiple configurations, lifecycle management, or worker isolation matter; share it deliberately only with a documented lifetime and concurrency model.

#### Decorators and wrappers

A decorator takes a callable and returns a callable, often adding logging, timing, authorization, or caching. It is related to the object Decorator pattern but is not identical in every case; the classic object pattern wraps an object behind the same interface, while Python's `@decorator` syntax commonly wraps a function.

```python
from collections.abc import Callable
from functools import wraps
from typing import TypeVar

T = TypeVar("T")

def trace_calls(fn: Callable[..., T]) -> Callable[..., T]:
    @wraps(fn)
    def wrapped(*args: object, **kwargs: object) -> T:
        print(f"calling {fn.__name__}")
        return fn(*args, **kwargs)
    return wrapped

@trace_calls
def parse_count(text: str) -> int:
    return len(text.split(","))

print(parse_count("a,b,c"))
```

Expected output:

```text
calling parse_count
3
```

`wraps` preserves useful metadata. This simplified typing does not preserve a precise parameter signature for static type checkers; production decorators that form a public API may need `ParamSpec` and `TypeVar` to preserve it. Decorators can obscure stack traces and complicate ordering, so use them for coherent cross-cutting behaviour, not every line of logic.

**Exercise:** add a decorator that measures elapsed time without changing the wrapped function's return value. Expected outcome: the function's result remains the same; timing is an observable side effect.

#### Iterators and generators

An **iterable** can produce an iterator; an **iterator** yields values one at a time; a **generator function** uses `yield` to create an iterator lazily. This is the natural Python expression of Iterator and supports streaming without loading all records into memory.

```python
from collections.abc import Iterable, Iterator

def nonempty_lines(lines: Iterable[str]) -> Iterator[str]:
    for line in lines:
        stripped = line.strip()
        if stripped:
            yield stripped

print(list(nonempty_lines([" alpha ", "", " beta "])))
```

Expected output: `['alpha', 'beta']`

**Engineering example:** `fetchkit` may stream parsed records to a sink. Laziness reduces peak memory, but a generator is usually single-pass, exceptions can occur during iteration rather than function invocation, and consumers must not assume results are reusable. Network streaming also requires clear resource ownership and cancellation semantics.

**Use when:** data is large or naturally incremental. **Avoid when:** callers require random access or repeated traversal and the result is small enough to materialize. **Exercise:** given `records = [{"id": "a", "status": "ok"}, {"id": "b", "status": "error"}]`, write a generator that yields only records whose `status` equals `"ok"`. Expected outcome: the generator yields the first dictionary only, one record at a time; it does not build a second list eagerly.

#### Context managers

A context manager coordinates setup and cleanup, normally through `with`. It is the Pythonic resource-lifetime pattern: acquire a lock, open a file, or manage a transaction, then release/commit/rollback according to the context manager's contract even when an exception occurs.

```python
from pathlib import Path

path = Path("example.txt")
with path.open("w", encoding="utf-8") as stream:
    stream.write("fetchkit\n")
# The file is closed here, including if the body raised an exception.
```

**Engineering example:** a database session or temporary file used during a fetch should have a clear owner and lifetime. Context managers do not automatically make operations transactional; the particular manager defines what exit means. Avoid swallowing exceptions unless that is explicitly its contract.

**Trade-off:** deterministic cleanup and readable scope versus nested scopes or manager complexity. **Exercise:** use `contextlib.ExitStack` to open several files and ensure all close if a later open fails. Expected outcome: resources acquired earlier are still released.

#### Duck typing and `Protocol`

**Duck typing** means code uses an object's behaviour rather than requiring a particular concrete class. `typing.Protocol` documents a structural interface for static type checking: a class can satisfy it by implementing the required members without inheriting from it.

```python
from typing import Protocol

class Source(Protocol):
    def fetch(self, url: str, *, timeout: float) -> bytes: ...

class FakeSource:
    def fetch(self, url: str, *, timeout: float) -> bytes:
        return b"sample payload"

def read_payload(source: Source, url: str) -> bytes:
    return source.fetch(url, timeout=2.0)

print(read_payload(FakeSource(), "https://example.test/data"))
```

Expected output: `b'sample payload'`

A protocol is not automatically runtime validation. Unless decorated with `@runtime_checkable`, it is primarily a static typing construct; even runtime-checkable protocols only check limited attribute presence, not full semantic correctness. A contract test should verify behaviour.

**Engineering example:** an HTTP source, an in-memory fake, and a recorded-fixture source can all satisfy `Source`. This supports ports-and-adapters without making the domain depend on `requests` or another vendor type.

**Use when:** callers need only a small behavioural contract. **Avoid when:** the protocol duplicates a concrete class without adding a real boundary or becomes a giant “everything” interface. **Exercise:** define a `Sink` protocol with `write(records: Iterable[dict[str, str]]) -> None`; expected outcome: two unrelated sink classes can satisfy the same contract.

#### `dataclasses` and `enum`

`dataclasses.dataclass` generates common data-model methods such as `__init__` and `__repr__`, and optionally equality/order methods. `frozen=True` prevents normal attribute reassignment but does not recursively freeze nested mutable objects. `enum.Enum` gives a finite set of named values rather than scattered magic strings.

```python
from dataclasses import dataclass
from enum import Enum

class FetchStatus(Enum):
    OK = "ok"
    RETRYABLE_ERROR = "retryable_error"
    PERMANENT_ERROR = "permanent_error"

@dataclass(frozen=True)
class FetchResult:
    url: str
    status: FetchStatus
    body: bytes = b""

result = FetchResult("https://example.test", FetchStatus.OK, b"hello")
print(result.status.value, len(result.body))
```

Expected output: `ok 5`

**Engineering example:** use an immutable `FetchResult` to communicate a result without passing mutable internal response objects through the system. Use an enum for a state with a fixed set of values. Do not use an enum if callers genuinely need arbitrary user-defined values.

**Trade-offs:** less boilerplate and clearer value semantics, but generated equality or freezing may not match every domain rule. **Simplest alternative:** a plain function returning a tuple for a tiny private operation; a dataclass is often clearer when fields have names or the value crosses a boundary. **Exercise:** add a `status_code: int | None` field and explain when `None` is valid. Expected outcome: the field is explicit and its meaning documented.

### 4.5 A pattern is not always a class

| Classic idea | Lightweight Pythonic expression | A class or framework is justified when… |
|---|---|---|
| Strategy | Function or callable object | Policy has meaningful state, lifecycle, or a richer contract. |
| Command | Function, closure, or `functools.partial` | It needs durable identity, serialization, retries, audit metadata, or undo. |
| Factory | Function or dictionary of constructors | Creation has lifecycle, family coordination, validation, or complex dependencies. |
| Singleton | Module-level constant/function; explicit shared instance | A resource has a deliberate lifetime and sharing/concurrency contract. |
| Iterator | Generator or iterator protocol | A custom collection needs special iteration state or multiple views. |
| Decorator | Function decorator or object wrapper | The wrapped object has a multi-method interface or stateful lifecycle. |
| State | `Enum` plus transition table or `match` | States have complex independent behaviour and transitions. |
| Value Object | `dataclass` or small immutable type | Validation, equality, invariants, or domain semantics need explicit methods. |

The correct question is not “which pattern should I implement?” but “what is changing, what must remain stable, and what is the simplest design that makes that relationship clear?”

## 5. Intermediate: catalogue and selection

### 5.1 Complete GoF catalogue with Pythonic mappings

The following table covers the complete 23-pattern GoF catalogue named in the module roadmap. The Pythonic form is a starting point, not a claim that the construct automatically implements the pattern in every use.

#### Creational patterns

| Pattern | Problem it addresses | Pythonic form / alternative | Main caution |
|---|---|---|---|
| **Factory Method** | Let construction vary behind a stable creation operation. | Named constructor (`from_env`), classmethod, or factory function. | Do not create a factory class for a single trivial constructor. |
| **Abstract Factory** | Create compatible families of related objects. | Dataclass containing constructor callables; a small `Protocol` with creation methods. | Families must be genuinely coordinated; otherwise inject individual dependencies. |
| **Builder** | Assemble a complex object in controlled steps. | Keyword-only arguments, configuration dataclass, fluent builder, `dataclasses.replace`. | Builders can allow invalid partial states or hide required fields. |
| **Prototype** | Create a new object based on an existing one. | `copy.copy`, `copy.deepcopy`, or `dataclasses.replace`. | Shallow and deep copy differ; external resources are rarely safe to clone blindly. |
| **Singleton** | Ensure one shared instance in a defined scope. | Module-level object or an instance created once at the composition root and injected. | Global mutable state harms tests; process/thread/fork lifetimes are not interchangeable. |

#### Structural patterns

| Pattern | Problem it addresses | Pythonic form / alternative | Main caution |
|---|---|---|---|
| **Adapter** | Convert one interface or data model to another. | A wrapper translating a vendor client into an application `Protocol`. | Translate exceptions and semantics too, not just method names. |
| **Bridge** | Vary abstraction and implementation independently. | Composition of two protocols (for example, report × renderer). | Can be needless indirection if the two axes never vary independently. |
| **Composite** | Treat an individual and a group uniformly. | Recursive data structures, tree nodes, or a common protocol for pipeline stages. | Recursive traversal and mutation rules can become hard to reason about. |
| **Decorator** | Add behaviour while preserving an interface. | Function decorator or an object wrapper delegating to the wrapped object. | Ordering matters; wrappers may change errors, metadata, timing, or identity. |
| **Facade** | Provide a simple entry point over a complex subsystem. | A small public function/module coordinating internal steps. | A facade can become a god object if it exposes every internal detail. |
| **Flyweight** | Share common immutable state to reduce memory use. | Interned values, enums, cached factories, `__slots__` where measured. | Sharing mutable state causes surprising cross-object effects; measure first. |
| **Proxy** | Control access to another object. | Lazy-loading, caching, access-control, or remote wrapper with the same contract. | Transparency is difficult: identity, equality, errors, and pickling can differ. |

#### Behavioural patterns

| Pattern | Problem it addresses | Pythonic form / alternative | Main caution |
|---|---|---|---|
| **Chain of Responsibility** | Pass a request through ordered handlers until handled or rejected. | Middleware functions, filter chains, ordered callables. | Order and stop/continue semantics must be explicit. |
| **Command** | Represent a request as something that can be queued, logged, retried, or undone. | Function, closure, `functools.partial`, or a dataclass command. | Durable commands need serialization/versioning and idempotency semantics. |
| **Iterator** | Traverse a sequence without exposing its representation. | `iter`, `next`, generator functions/expressions. | Iterators are often single-pass and can defer exceptions. |
| **Mediator** | Reduce direct many-to-many communication among components. | A narrowly scoped event bus or coordinator. | A global mediator can hide control flow and become a god object. |
| **Memento** | Capture state for restoration or undo. | Immutable dataclass snapshot, `copy`, or `dataclasses.replace`. | Deep copying can be expensive or invalid for resources; define snapshot boundaries. |
| **Observer** | Notify interested parties when something happens. | Callbacks, logging handlers, signals, event hooks. | Handler failures, ordering, re-entrancy, and memory leaks need policy. |
| **State** | Change behaviour according to an object's current state. | `Enum` plus transition table or `match`; state objects for complex states. | Unchecked transitions and state explosion are common failure modes. |
| **Strategy** | Swap one algorithm or policy for another. | Callable, callable object, or `Protocol`. | An interface with one stable implementation may be overengineering. |
| **Template Method** | Keep an algorithm skeleton while subclasses customise hooks. | Hook functions, higher-order functions, or a base class only when inheritance fits. | Inheritance couples extension to base-class internals. |
| **Visitor** | Add operations over a family of object types. | `functools.singledispatch`, pattern matching, or explicit methods. | Dispatch may be awkward when the type set changes frequently. |

### 5.2 Architectural patterns for data and AI systems

Architectural patterns operate at a larger scale than the GoF object-level catalogue. They describe how subsystems, data flow, storage, or failure handling are organised.

| Pattern | Mental model and execution flow | Use when | Risks / simpler alternative |
|---|---|---|---|
| **Pipeline** | Each stage transforms or forwards data: source → decode → validate → parse → sink. | Transformations have clear input/output contracts and can be tested separately. | Too many tiny stages obscure flow; start with ordinary functions. Streaming requires clear backpressure and error propagation. |
| **Plugin architecture** | A host defines a contract, discovers implementations, validates compatibility, and invokes selected plugins. | Third parties or separately deployed teams must extend capabilities without editing core code. | Plugins are executable code; discovery side effects, version mismatch, and trust boundaries matter. A passed-in mapping may suffice for internal extensibility. |
| **Repository** | A domain-facing interface hides persistence queries and storage details. | Multiple persistence adapters or meaningful domain query boundaries exist. | A generic CRUD repository can obscure SQL features and duplicate an ORM. Use direct ORM/session calls if that is clearer. |
| **Unit of Work** | Collect changes within a boundary, then commit atomically or roll back. | Several changes must share a transaction and lifecycle. | It is not a distributed transaction across unrelated services; transaction scope and failure handling must be explicit. |
| **Ports and adapters (hexagonal)** | Core logic declares ports; external adapters implement them for HTTP, database, filesystem, or model providers. | Domain logic should survive vendor or framework changes and be testable without external I/O. | Too many ports around stable details create ceremony. Define ports around actual dependency boundaries. |
| **Event-driven / pub-sub** | Producers publish events; subscribers react, often without direct calls between them. | Independent consumers need decoupling or asynchronous processing. | Ordering, delivery guarantees, retries, duplicate events, observability, and backpressure are not automatic. Direct calls may be simpler. |
| **Retry / circuit breaker** | Retry policy repeats selected transient failures; a circuit breaker temporarily rejects calls when a dependency is unhealthy. | Remote calls fail transiently and the system needs bounded recovery behaviour. | Retries can amplify load or duplicate side effects; breaker state needs time and concurrency semantics. |
| **Idempotent consumer** | A consumer records a stable operation/event identifier and ensures duplicate delivery does not repeat the effect. | At-least-once queues or retryable jobs can redeliver messages. | Deduplication storage and the business write must be coordinated; “check then write” can race. |

These patterns are especially relevant to data/AI systems: a model-provider port makes a vendor replaceable; a pipeline separates retrieval, transformation, and evaluation; an idempotent consumer protects a job from duplicate queue delivery. Details of production pipelines belong to the later data-engineering stage; here, learn the design vocabulary and trade-offs.

### 5.3 A practical decision rule

Start with the simplest working design. Consider a pattern when either:

- there are **two or three real variants** that need the same workflow, or
- measurable design pain already exists: duplicated logic, change amplification, hard-to-isolate tests, repeated conditionals, resource-lifecycle bugs, or unclear ownership.

This is a heuristic, not a waiting period. Abstract earlier when a high-risk boundary is already clear—for example, external HTTP I/O is expensive and unreliable, and deterministic tests are required before a second production source exists. Do not invent hypothetical variants merely to justify an interface.

A quick decision sequence:

1. **State the pain.** What change, test, or failure is difficult today?
2. **Identify the axis of variation.** Which part changes independently from the rest?
3. **Choose the lightest boundary.** Function, module, dataclass, protocol, wrapper, or larger architecture?
4. **Compare with direct code.** Is the indirection buying testability or change isolation?
5. **Test the boundary.** Use fakes or contract tests to verify behaviour.
6. **Review the evidence.** Keep the abstraction only if the benefit survives maintenance and runtime costs.

**Exercise:** you have one JSON parser and no plugin users. Should you build a plugin manager? Expected answer: usually no. A `parse_json` function is enough. If multiple external parser packages must register themselves independently, the problem changes and a registry may earn its cost.

### 5.4 Reading patterns in real Python libraries

These are conceptual readings of public library APIs, not claims that a library implements every pattern exactly as the GoF definition. Use the library documentation/source to inspect concrete behaviour and version-specific details.

| Library | Pattern 1 | Pattern 2 | Why the expression is Pythonic |
|---|---|---|---|
| `logging` | **Observer-like:** handlers receive log records from loggers. | **Chain/Strategy-like:** filters decide whether records pass; handlers select output behaviour. | Handlers and filters are configured objects behind a stable logging API. Propagation and filter ordering are part of the operational contract. |
| `pathlib` | **Facade-like:** `Path` offers a cohesive interface over platform path semantics and filesystem operations. | **Strategy/adapter-like at the implementation boundary:** concrete path flavours represent platform-specific path rules. | Users work with `Path` methods rather than hand-assembling platform-specific string operations. The exact internals are not a textbook pattern exercise. |
| SQLAlchemy | **Unit of Work:** a `Session` tracks pending changes and coordinates flush/transaction behaviour. | **Identity Map:** within a session, database identity maps to a managed in-memory object. | The ORM exposes a coherent session API, but transaction boundaries and session scope must be designed deliberately. |
| `requests` | **Adapter:** transport adapters provide a boundary between a session and transport implementations. | **Strategy-like configuration:** mounted adapters can vary transport behaviour by URL prefix. | `Session` and `HTTPAdapter` are explicit extension points; retries are commonly configured through adapter/urllib3 support rather than an arbitrary hidden global. |
| `pytest` | **Plugin / hooks:** plugins contribute behaviour at defined hook points. | **Dependency injection-like fixtures:** tests request named fixtures and pytest resolves their dependencies. | Extension contracts and fixture scopes avoid requiring application code to subclass a central framework base class. |
| `argparse` | **Builder-like configuration:** parser and argument definitions are accumulated declaratively. | **Command-line dispatch:** parsed arguments select program behaviour, often via `set_defaults(func=...)` or a dispatch table. | A fluent/declarative standard-library API builds parser state; it is not necessary to invent a separate builder class for ordinary CLIs. |

**How to inspect responsibly:** read the official docs for the public contract, then inspect source only to answer a focused question. Avoid treating implementation details as a stable API. A pattern analogy is a learning tool, not proof that the library follows a particular textbook implementation.

**Exercise:** choose one library above, identify a public extension point, and write down (a) the contract, (b) what varies, and (c) what would be harder if the extension point were absent. Expected outcome: a specific example rather than only a pattern label.

### 5.5 Documenting a design decision

A concise design note should record **context, forces, decision, and alternatives considered**.

- **Context:** the situation and constraints.
- **Forces:** competing requirements (testability, latency, simplicity, compatibility, ownership, reliability).
- **Decision:** the chosen design and the reason it best balances the forces.
- **Alternatives:** credible options considered and why they were rejected.

Example for `fetchkit`:

> **Context:** `Fetcher` must retrieve content from HTTP and be tested without live network access.  
> **Forces:** predictable tests, a small public API, support for one initial HTTP implementation, and low maintenance overhead.  
> **Decision:** accept a `Source` protocol-compatible object in the internal composition root; provide a default HTTP adapter. Keep the public `fetch(url)` convenience function.  
> **Alternatives:** (1) call `requests.get` directly throughout the parser and orchestration code—rejected because it spreads vendor coupling; (2) build a plugin discovery framework now—rejected because there is only one built-in source and no third-party extension requirement.

**Use when:** a choice is consequential, non-obvious, or expensive to reverse. **Avoid:** writing an ADR for every local variable or pretending a short note eliminates the need to revisit assumptions. **Exercise:** document why `fetchkit` starts with a function parser registry or direct parser function. Expected outcome: the note explains forces and alternatives, not just the selected pattern name.

## 6. Advanced: principles and design judgment

### 6.1 SOLID as a set of design questions

SOLID is a collection of heuristics, not five rules that require one class per noun.

| Principle | Definition / mental model | `fetchkit` example | Failure mode if misapplied |
|---|---|---|---|
| **Single Responsibility (SRP)** | A module should have one coherent reason to change. | HTTP transport, parsing, and output formatting change for different reasons. | Splitting every line into a class produces fragmentation rather than cohesion. |
| **Open/Closed (OCP)** | Common changes should be possible through extension without repeatedly editing stable core logic. | Inject a parser callable instead of adding parser-specific branches throughout `Fetcher`. | Premature plugin frameworks can be more costly than a small `if` statement. |
| **Liskov Substitution (LSP)** | A subtype should preserve the behavioural promises expected of its base contract. | A fake source must obey timeout and exception semantics expected by callers, not merely have a `fetch` method. | Signature compatibility alone does not prove semantic compatibility. |
| **Interface Segregation (ISP)** | Clients should not depend on methods they do not use. | Separate `Reader` and `Writer` ports if components need only one capability. | Do not fragment a naturally cohesive contract into dozens of tiny protocols without evidence. |
| **Dependency Inversion (DIP)** | High-level policy should not depend directly on low-level details; both depend on an abstraction where useful. | Fetch orchestration depends on `Source`, not a concrete HTTP vendor. | An abstraction that only mirrors a concrete class can add no meaningful independence. |

**Internal flow:** the composition root creates the concrete HTTP adapter, cache, parser, and sink, then passes them to the orchestration layer. The orchestration uses contracts; it does not construct or import every vendor implementation. This makes the dependency direction visible and tests easier to isolate.

**When to use:** to ask whether responsibilities, contracts, and dependencies are coherent. **When not to use:** as a scorecard that rewards maximum interface count. **Exercise:** identify which SOLID principle is most relevant when a parser imports an HTTP SDK only to read a response body. Expected answer: primarily dependency inversion / separation of concerns; an adapter may also be useful if it translates the vendor contract.

### 6.2 Composition over inheritance and programming to an interface

**Composition** builds behaviour by combining objects or functions. **Inheritance** reuses or specialises behaviour through an “is-a” relationship. Prefer composition when components need to vary independently or when inheritance would expose implementation details. Inheritance is appropriate when substitutability is real and the base class defines a stable contract.

“Program to an interface” means the caller relies on a behavioural contract, not a concrete implementation. In Python that contract may be a `Protocol`, a callable signature, or documented duck-typed behaviour—not necessarily an abstract base class.

```python
from collections.abc import Callable

Parser = Callable[[bytes], list[dict[str, str]]]

def parse_payload(body: bytes, parser: Parser) -> list[dict[str, str]]:
    return parser(body)
```

This function composes with any compatible parser. It does not need `JsonParserBase` and `CsvParserBase` merely to share a call signature.

**Trade-offs:** composition keeps choices local but may require explicit wiring. Inheritance can share invariant behaviour but risks fragile base-class coupling and deep method-resolution paths. **Exercise:** choose inheritance or composition for adding a retry policy to an HTTP source. Expected answer: usually composition/wrapping, because retry policy is a behaviour that can vary independently of the transport.

### 6.3 Law of Demeter

The Law of Demeter is a heuristic: a component should communicate primarily with its immediate collaborators rather than navigating long chains of unrelated objects. `fetcher.client.session.headers.update(...)` couples a caller to several internal representation details. Prefer a focused method such as `fetcher.configure_headers(...)` only if that operation belongs in the public contract—or configure the client at the composition root.

It is not a ban on chained expressions: `Path("data").parent` or fluent builders can be perfectly clear. The concern is knowledge of internal object graphs, not the number of dots alone.

**Failure mode:** “fixing” every chain with forwarding methods creates a facade full of pass-throughs. **Exercise:** refactor a caller that reaches into three private objects. Expected outcome: reduce knowledge of internals without adding meaningless delegation.

### 6.4 YAGNI, DRY, and the rule of three

- **YAGNI — You Aren't Gonna Need It:** do not build speculative capabilities without evidence that they are needed.
- **DRY — Don't Repeat Yourself:** avoid duplicated *knowledge or rules*, not every repeated line of syntax. Two similar blocks may represent different business rules and should remain separate if they change independently.
- **Rule of three:** tolerate a first straightforward implementation, observe the second, and consider abstraction when a third real instance reveals a stable common shape. The roadmap's “two or three real variants” guideline is deliberately approximate.

**Counter-example: abstract earlier.** If an external HTTP dependency makes unit tests slow, flaky, or network-dependent, create a small `Source` seam before a second production adapter exists. The measurable testability problem is already real. Security, transaction, and resource-lifecycle boundaries may also justify earlier design work.

**Comparison:** direct duplication is easiest to read initially; a good abstraction reduces future change amplification; a wrong abstraction forces unrelated cases into one shape. **Exercise:** three parsers share a 4-line validation helper but differ in error semantics. Expected outcome: share only the genuinely common rule; do not force them into a large base class merely because they all parse.

### 6.5 The cost model of abstraction

Every abstraction has costs. Evaluate at least these dimensions:

1. **Indirection:** the reader must follow more functions, objects, or registrations to understand execution.
2. **Cognitive load:** contracts and lifecycle rules must be learned and remembered.
3. **Runtime cost:** wrapper calls, allocations, dispatch, copying, locks, and serialization can add latency or memory. Often small, but measure when the hot path matters.
4. **Testing overhead:** interfaces and fakes can simplify tests, while generic frameworks may require many fixtures and contract suites.
5. **Accidental complexity:** machinery exists because the chosen design demands it, not because the domain does.
6. **Speculative generality:** features and extension points are built for hypothetical future cases that have not appeared.

A useful test is whether the abstraction reduces total complexity across implementation, testing, operations, and future changes. Do not optimize only line count or class count.

**Engineering example:** adding a `CachingSource` wrapper can make caching independently testable. Adding five abstract base classes, a dynamic factory registry, and a plugin lifecycle for one cache backend probably does not.

**Exercise:** list one benefit and two costs of introducing a generic `StorageBackendFactoryProvider`. Expected outcome: benefits are concrete (e.g. independent backend selection); costs include more indirection and a new contract to maintain. If the only use case is one backend, keep it simple.

### 6.6 Distributed-system pattern awareness

These patterns are included for recognition, not full implementation; later backend, data, and AI stages cover their operational details.

| Pattern | Definition and flow | When it helps | Key trade-off / failure mode |
|---|---|---|---|
| **Saga** | A multi-step business operation uses local transactions with compensating actions for completed steps when later steps fail. | Work spans services without one shared ACID transaction. | Compensation is not always a true inverse; partial failure and recovery state must be explicit. |
| **Outbox** | Write a business change and an event record in the same local database transaction; a relay publishes the event later. | Avoids losing an event between database commit and message publication. | Delivery can be duplicated; consumers still need idempotency and relay monitoring. |
| **CQRS** | Separate command/write responsibilities from query/read models. | Read and write workloads or models have materially different needs. | More models, synchronization, and operational complexity; do not split a simple CRUD app reflexively. |
| **Circuit breaker** | Track failures and temporarily reject calls to a dependency, later permitting a probe/half-open attempt. | A failing remote dependency would otherwise consume resources through repeated calls. | Thresholds and state transitions require careful time/concurrency handling; it does not replace timeouts. |
| **Bulkhead** | Isolate resource pools or concurrency limits so one workload cannot consume everything. | Independent dependencies or tenants need failure/resource isolation. | Capacity is fragmented; limits and rejection behaviour must be observable. |
| **Backpressure** | A downstream consumer signals or enforces that upstream production must slow or bound its work. | Streaming, queues, and fan-out could otherwise grow memory/latency without bound. | Dropping, buffering, blocking, and rejecting each have different semantics. |
| **Fan-out / fan-in** | Send work to multiple branches and combine their results. | Parallel independent retrievals or evaluations reduce wall-clock latency. | Partial failure, cancellation, ordering, rate limits, and tail latency complicate aggregation. |
| **Map-reduce** | Map independent items to intermediate results, then reduce/aggregate them. | Large datasets can be partitioned into independent work and combined. | Partition skew, serialization, shuffle costs, and non-associative reductions can invalidate assumptions. |

For `fetchkit`, retrying a GET may be reasonable when the error is transient, but retrying an arbitrary write can duplicate effects. A circuit breaker does not make a request safe to retry; idempotency and timeouts are separate concerns. A bounded queue does not guarantee delivery; it only bounds resource use according to its policy.

### 6.7 Architecture Decision Records, smells, and module boundaries

An **Architecture Decision Record (ADR)** is a short, version-controlled record of an important architectural choice, often with status, context, decision, consequences, and alternatives. It preserves why a design exists so future maintainers can distinguish an intentional trade-off from an accident.

**Pattern smells** include:

- applying a pattern because a textbook lists it, not because a problem exists;
- class names such as `AbstractFooFactoryManager` that accumulate abstractions without clarifying responsibility;
- one-implementation interfaces with no meaningful test seam or expected variation;
- deep inheritance hierarchies that make behaviour depend on hidden base-class details;
- a “god object” coordinating unrelated tasks;
- a global event bus or mutable singleton that hides dependencies;
- registries that mutate unpredictably at import time;
- adapters that leak vendor exceptions or expose vendor-specific types throughout the core.

**Module boundaries** should follow cohesive responsibilities and dependency direction. If HTTP, parsing, caching, and output each change for different reasons, modules can make those boundaries explicit. But a separate module for every tiny helper can make navigation worse.

**Conway's law** observes that system designs tend to reflect communication structures of the organisations that build them. It is a useful organisational force, not a deterministic law. If data-platform, model-serving, and product teams own different contracts, boundaries and ownership need explicit coordination; splitting code to mirror every team can still create excessive network calls and brittle interfaces.

**Public vs internal API:** public names, signatures, defaults, exceptions, and documented behaviour become compatibility commitments. Internal implementation can evolve more freely, although undocumented details may still attract user dependencies (Hyrum's law). This lesson previews the concern; Module 20 lesson 06 treats API design directly.

**Evolutionary design:** begin with a simple design, keep tests around behaviour, and refactor when real pressure appears. Tests are a safety net, not a substitute for design judgement. Use contract tests when multiple implementations must obey the same protocol.

**Exercise:** write a brief ADR for whether cache is a wrapper or an internal branch. Expected outcome: the choice is tied to cache invalidation, testability, wrapper order, and expected variants—not to the prestige of a named pattern.

## 7. Worked examples

### 7.1 Direct code versus a strategy

Suppose one implementation has a branch for a single parser format. Direct code is the simplest correct choice:

```python
def parse_text(text: str, format_name: str) -> list[str]:
    if format_name == "comma":
        return [part.strip() for part in text.split(",")]
    raise ValueError(f"unsupported format: {format_name!r}")
```

If two or three formats now share a stable calling convention, use a mapping of functions:

```python
from collections.abc import Callable

Parser = Callable[[str], list[str]]

def parse_comma(text: str) -> list[str]:
    return [part.strip() for part in text.split(",")]

def parse_pipe(text: str) -> list[str]:
    return [part.strip() for part in text.split("|")]

PARSERS: dict[str, Parser] = {"comma": parse_comma, "pipe": parse_pipe}

def parse(text: str, format_name: str) -> list[str]:
    try:
        parser = PARSERS[format_name]
    except KeyError:
        raise ValueError(f"unsupported format {format_name!r}; choose from {sorted(PARSERS)}") from None
    return parser(text)

assert parse("a, b", "comma") == ["a", "b"]
assert parse("a | b", "pipe") == ["a", "b"]
```

**Why this is better at this point:** adding a parser means registering a callable rather than expanding a central conditional. **Why it may not be better earlier:** with one format, the registry is extra indirection. A global registry is also not automatically the right design for a public library; dependency injection of a mapping can make tests and isolation simpler.

### 7.2 Adapter and protocol boundary

A vendor client may return a complex response object and raise vendor-specific exceptions. The core should depend on a small contract and an adapter should translate at the boundary. Illustrative pseudocode—the vendor SDK is intentionally not imported:

```python
from typing import Protocol

class Source(Protocol):
    def fetch(self, url: str, *, timeout: float) -> bytes: ...

class VendorSource:
    """Illustrative adapter; replace `vendor_client` with a real SDK client."""
    def __init__(self, vendor_client: object) -> None:
        self._client = vendor_client

    def fetch(self, url: str, *, timeout: float) -> bytes:
        # Actual implementation depends on the selected vendor SDK.
        raise NotImplementedError("illustrative adapter boundary")
```

The boundary is useful because it names what the core needs. A production adapter must define timeout semantics, status handling, body decoding, exception translation, and resource ownership. Merely renaming a vendor method is not a complete adapter.

### 7.3 Retry policy as a strategy, not a magic loop

A retry policy should be explicit about which errors are retryable, maximum attempts, and delay/backoff. This small pure decision function illustrates selection without sleeping or performing I/O:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class RetryDecision:
    retry: bool
    reason: str

def decide_retry(*, attempt: int, max_attempts: int, transient: bool) -> RetryDecision:
    if attempt < 1 or max_attempts < 1:
        raise ValueError("attempt and max_attempts must be positive")
    if not transient:
        return RetryDecision(False, "failure is not transient")
    if attempt >= max_attempts:
        return RetryDecision(False, "attempt limit reached")
    return RetryDecision(True, "transient failure; another attempt is allowed")

assert decide_retry(attempt=1, max_attempts=3, transient=True).retry is True
assert decide_retry(attempt=3, max_attempts=3, transient=True).retry is False
```

Expected outcome: first attempt can be retried when the failure is transient and the limit allows it; the final permitted attempt is not followed by another. This example intentionally does not implement HTTP calls, jitter, deadlines, cancellation, or circuit-breaker state. Those belong in a later, tested implementation. In production, retry only operations whose semantics permit repetition, apply timeouts/deadlines, and avoid retry storms.

### 7.4 Testing the contract instead of the implementation class

A protocol boundary permits a fake with deterministic behaviour:

```python
from typing import Protocol

class Source(Protocol):
    def fetch(self, url: str, *, timeout: float) -> bytes: ...

class FakeSource:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload
        self.calls: list[tuple[str, float]] = []

    def fetch(self, url: str, *, timeout: float) -> bytes:
        self.calls.append((url, timeout))
        return self.payload

def get_text(source: Source, url: str) -> str:
    return source.fetch(url, timeout=1.5).decode("utf-8")

fake = FakeSource(b"hello")
assert get_text(fake, "https://example.test") == "hello"
assert fake.calls == [("https://example.test", 1.5)]
```

The test asserts an externally observable contract. It does not assert private call order or implementation details that are free to change. In a full test suite, add invalid UTF-8 behaviour, timeout forwarding, and adapter-specific contract tests. The fake must model the semantic contract, not merely satisfy a type checker.

## 8. `fetchkit` case-study evolution

This section ties the lesson together without prematurely implementing the full later lessons.

### 8.1 Initial design: keep the path visible

At first, use a small function that fetches bytes, parses them, and writes records. Do not add a generic framework until you know which decisions vary. Conceptually:

```text
fetch(url) → HTTP GET → bytes → parser → records → sink
```

The initial version can use one concrete HTTP library and one parser if that is all the product needs. Keep parsing pure where possible; keep network access at the edge. Test parsing directly with byte/string fixtures and test the HTTP adapter separately.

### 8.2 Add a source seam when testability requires it

When network tests are slow or flaky, define a small `Source` protocol and pass a source into internal orchestration. Provide a default HTTP adapter at the composition root. Tests use `FakeSource`. This is a deliberate boundary even before a second production source exists because it resolves a measurable testability problem.

### 8.3 Add cache as a separate concern

A cache can be a wrapper implementing the same `Source` contract, or a small explicit cache step. Choose based on invalidation, visibility, and composition needs. A wrapper makes caching reusable; an inline branch may be simpler for one local cache. Decide cache key semantics, expiry, stale-data behaviour, and thread-safety. Never assume a dictionary cache is safe for concurrent access merely because individual operations are often atomic in a given interpreter.

### 8.4 Add parser variation only when real formats appear

Use a direct function for one parser. When formats genuinely vary, a mapping from stable names to parser callables may be enough. Move to a plugin registry only when independent extension/discovery is a requirement. Validate unknown formats with a useful error; do not import arbitrary user-supplied module paths without a trust model.

### 8.5 Add retry policy with explicit semantics

Treat retry as a policy, not an unbounded loop. Make attempts, eligible failures, deadline, backoff, and jitter explicit. Use a fake clock or injected delay function in tests rather than sleeping. A retry wrapper can be composed with a source, but wrapper order changes behaviour: cache-before-retry may cache only the final successful result depending on implementation; retry-before-cache can have different failure and observability semantics. Document the actual stack and test it.

### 8.6 Keep output sinks separate from retrieval

A CSV writer and a JSON writer have different output concerns from HTTP retrieval. A `Sink` protocol or two simple functions may be appropriate. Do not force a shared base class unless the common contract is stable and useful. Avoid passing a mutable internal response object to a sink; pass the minimal data the sink needs.

### 8.7 Target shape—not mandatory architecture

A reasonable later shape might be:

```text
fetchkit/
  __init__.py             # small public facade
  _fetcher.py             # orchestration
  _source.py              # Source contract and HTTP adapter
  _cache.py               # cache wrapper/policy
  _parsers.py             # parser functions / optional registry
  _sinks.py               # output contracts and implementations
  _retry.py               # retry decision and wrapper
  _errors.py              # library-facing errors (later lesson)
```

This is a candidate, not a required directory tree. Keep files together when that is clearer. Public API shape and compatibility receive dedicated attention in later module lessons. This lesson should leave `fetchkit` with named responsibilities, testable seams where justified, and no speculative plugin system.

## 9. Common mistakes and anti-patterns

The roadmap highlights three core mistakes; the expanded list below makes their consequences concrete.

1. **Translating Java patterns class-for-class.** A `Strategy` interface plus one class per algorithm can be needless if each algorithm is a simple function. Start with callables; introduce richer objects when state or lifecycle warrants them.
2. **Introducing abstractions before a second use case exists.** The rule of three is a heuristic, not a prohibition. Abstract earlier for measurable pain such as deterministic testing or a security boundary; otherwise avoid hypothetical generality.
3. **Treating patterns as goals instead of tools.** “We need an Observer” is not a problem statement. Say what must be decoupled, who owns failures, and what ordering/delivery semantics are required.
4. **Singleton abuse and hidden global state.** Globals make test order and worker lifecycle matter; they can hide dependencies and cause cross-test contamination.
5. **Deep inheritance and god objects.** A long base-class chain or one `FetcherManagerFactoryService` often makes changes harder to localise.
6. **One-implementation interfaces without a reason.** A protocol is valuable when it names a meaningful boundary, not merely because the codebase has a type annotation.
7. **Stringly typed APIs.** Magic strings spread typos and undocumented states; use enums or constrained literal types when the set is genuinely finite.
8. **Overly broad protocols.** A fat interface forces consumers to depend on capabilities they do not need; split by real client needs, not mechanically.
9. **Leaky adapters.** Vendor exceptions and response objects escape into core code, defeating the boundary.
10. **Unsafe retries.** Retrying non-idempotent work can duplicate effects; retries without limits/timeouts can amplify outages.
11. **Observer hazards.** Subscribers can raise, unsubscribe during notification, re-enter publishing, or remain strongly referenced and leak memory. Define ordering and error-isolation policies; snapshot subscriber collections during iteration where appropriate.
12. **Unbounded async work.** Unbounded queues and fan-out can exhaust memory. Use bounded queues, cancellation, timeouts, and backpressure policies appropriate to the system.
13. **Abstraction by code similarity alone.** Two snippets may encode different business rules. DRY knowledge, not superficial syntax.
14. **Confusing an analogy with an implementation guarantee.** A module is often a useful shared namespace, but not a universal process-wide singleton; a `Protocol` is not full runtime validation; a decorator does not automatically preserve every signature or semantic property.
15. **Skipping tests because the pattern is familiar.** Tests should verify behaviour, boundary contracts, failures, and composition order—not the mere existence of classes.

## 10. Hands-on exercises

Complete these in order. Use Python 3.12+, type hints, and tests. Do not proceed by adding classes automatically; explain why each abstraction earns its cost.

### Exercise A — Replace a branch with a callable strategy

Start with a function that supports one parsing format. Add a second real format, then compare a conditional with a dictionary of parser callables.

**Requirements:**
- Define a `Parser` callable type.
- Reject unknown names with a useful `ValueError`.
- Test both formats and the invalid-format case.
- Write two sentences explaining why the mapping is now justified.

**Expected outcome:** parser selection is isolated; parsing behaviour is tested independently; no base class is required.

### Exercise B — Make `fetchkit` testable without HTTP

Define `Source` as a `Protocol` and implement `FakeSource` with deterministic bytes. Inject it into a function that decodes a response.

**Requirements:** test the returned value, URL, and timeout; test invalid UTF-8 handling; do not call the network.

**Expected outcome:** the test is fast and repeatable. Explain why a protocol documents a contract but does not prove semantic correctness on its own.

### Exercise C — Choose the right cache boundary

Compare (1) a dictionary cache inside `Fetcher` and (2) a `CachingSource` wrapper. Consider cache invalidation, composition, concurrency, and observability.

**Requirements:** do not implement a production cache; write a short decision note with context, forces, decision, and alternatives.

**Expected outcome:** one choice is defended against the actual requirements. Either design can be correct.

### Exercise D — Library-pattern field study (mandatory)

Compare at least **three** well-known Python libraries. The roadmap suggests `logging`, `pathlib`, SQLAlchemy, `requests`, `pytest`, and `argparse`; choose any three or more. Identify at least two patterns per library and explain how each is expressed Pythonically.

For each pattern, record:

1. The public API or extension point you inspected.
2. The design problem/force it addresses.
3. The Python construct used (callable, handler, protocol, facade, fixture, adapter, declarative builder, etc.).
4. The benefit and a trade-off/failure mode.
5. One sentence distinguishing the observed API from a textbook pattern analogy.

Write a one-page comparison. Do not claim an internal pattern without evidence from documentation or source. Prefer official documentation and stable public contracts.

**Expected outcome:** at least six grounded pattern observations across three libraries, with evidence and nuance rather than pattern-name guessing.

### Exercise E — Pattern selection review

For each scenario, choose the lightest design and justify it:

1. One JSON parser, no third-party extensions.
2. Two parsers selected by configuration.
3. Third-party packages independently register parsers.
4. HTTP access makes unit tests flaky.
5. A job may be delivered twice by a queue.
6. A failing remote dependency is being retried indefinitely.

**Expected outcomes:** (1) direct function; (2) callable mapping or simple factory; (3) registry/plugin mechanism with a trust and compatibility contract; (4) source port/fake adapter; (5) idempotent consumer with durable deduplication semantics; (6) bounded retry policy and likely timeout/circuit-breaker analysis. Justify exceptions where requirements differ.

### Exercise F — ADR and abstraction cost

Write a one-page ADR for a proposed generic `FetcherBackendManager`. Include context, forces, decision, alternatives, consequences, and revisit conditions. Then list its indirection, cognitive, runtime, and testing costs.

**Expected outcome:** the decision can be challenged and revisited; “extensibility” alone is not treated as proof of value.

### Exercise G — Small test suite

Using `pytest`, write tests for `decide_retry` from Section 7.3. Cover a transient failure with attempts remaining, a permanent failure, the attempt limit, and invalid attempt counts.

Example test file:

```python
import pytest

# Import RetryDecision and decide_retry from the module where you saved them.

def test_transient_failure_can_retry() -> None:
    assert decide_retry(attempt=1, max_attempts=3, transient=True).retry is True

def test_permanent_failure_does_not_retry() -> None:
    assert decide_retry(attempt=1, max_attempts=3, transient=False).retry is False

def test_attempt_limit_stops_retry() -> None:
    assert decide_retry(attempt=3, max_attempts=3, transient=True).retry is False

@pytest.mark.parametrize("attempt,max_attempts", [(0, 3), (1, 0)])
def test_invalid_attempt_counts_raise(attempt: int, max_attempts: int) -> None:
    with pytest.raises(ValueError):
        decide_retry(attempt=attempt, max_attempts=max_attempts, transient=True)
```

Expected outcome: five logical cases pass when the implementation is placed in an importable module. The import line is intentionally left to the learner because the lesson does not prescribe a repository layout.

## 11. Self-check questions and model answers

### 1. Which GoF patterns become “a function” or “a module” in Python? Give examples.

**Model answer:** Strategy often becomes a function passed as a callable; Command can be a function, closure, or `functools.partial` when it only needs to package an action; simple Factory Method can be a factory function or named classmethod constructor. A module can provide a shared namespace for constants and stateless functions, replacing a class used only to group global utilities. Modules are not a universal singleton for all processes or all resource lifetimes. The problem and consequences determine whether a class remains useful.

### 2. State the rule of three and give a counter-example where you would abstract earlier.

**Model answer:** The rule of three says to let a first implementation be straightforward, observe a second real case, and consider abstraction when a third real case reveals a stable common contract. It is a heuristic, not a strict rule. I would abstract earlier if direct HTTP calls make unit tests dependent on network availability: a small `Source` protocol and fake source solve a measurable testability problem before a second production adapter exists. Similar early boundaries can be justified by security, transaction, or resource-lifecycle risks.

### 3. Pick a pattern from the standard library and explain the forces it resolves.

**Model answer:** `logging` handlers are observer-like: a logger emits a record and configured handlers route it to destinations such as a stream or file. This separates the code producing a log event from the code choosing its destination, supports multiple outputs, and centralises filtering/formatting configuration. The trade-offs include handler configuration, propagation and ordering semantics, and the need to avoid duplicate handlers or leaking file resources. The analogy describes the collaboration; it is not a claim that every detail maps one-to-one to the GoF Observer class diagram.

## 12. Lesson summary and completion checklist

The key skill is design judgement: recognise a recurring problem, understand its forces, and choose the lightest solution that preserves a useful contract. Python's first-class functions, modules, decorators, generators, context managers, duck typing, protocols, dataclasses, and enums remove much boilerplate, but they do not remove the need to reason about ownership, failure, concurrency, or compatibility.

Use this checklist before moving on:

- [ ] I can describe a pattern by name, problem, solution, and consequences.
- [ ] I can distinguish creational, structural, behavioural, and architectural patterns.
- [ ] I can explain at least five cases where Python constructs replace class-heavy implementations.
- [ ] I can map all 23 GoF patterns to an idiomatic Python option and name a caution for each.
- [ ] I can justify a pattern using two or three real variants or measurable design pain, and explain when to abstract earlier.
- [ ] I can identify at least two pattern-like design choices in each of three Python libraries.
- [ ] I can explain the SOLID principles, composition over inheritance, interface-oriented design, Law of Demeter, YAGNI, DRY, and rule of three as heuristics.
- [ ] I can describe abstraction costs and at least four distributed-system patterns at a high level.
- [ ] I can write an ADR with context, forces, decision, alternatives, and revisit conditions.
- [ ] I can identify pattern smells and evolve `fetchkit` with tests rather than speculative machinery.

## 13. References

The following authoritative references support the language/library features and named libraries discussed here. The catalogue and selection heuristics follow the supplied Module 1.20 roadmap; the external references help verify current public contracts.

- Python documentation — [Functions](https://docs.python.org/3/tutorial/controlflow.html#defining-functions), [Data model and iterators](https://docs.python.org/3/reference/datamodel.html#emulating-container-types), [Generators](https://docs.python.org/3/howto/functional.html#generators), [Context managers](https://docs.python.org/3/library/contextlib.html), [Decorators and `functools`](https://docs.python.org/3/library/functools.html), [Dataclasses](https://docs.python.org/3/library/dataclasses.html), [Enums](https://docs.python.org/3/library/enum.html), [Typing and `Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol), [Modules and imports](https://docs.python.org/3/tutorial/modules.html).
- Python standard library — [`logging`](https://docs.python.org/3/library/logging.html), [`pathlib`](https://docs.python.org/3/library/pathlib.html), [`argparse`](https://docs.python.org/3/library/argparse.html), [`copy`](https://docs.python.org/3/library/copy.html), [`contextlib.ExitStack`](https://docs.python.org/3/library/contextlib.html#contextlib.ExitStack).
- SQLAlchemy — [Session basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html).
- Requests — [Transport adapters](https://requests.readthedocs.io/en/latest/user/advanced/#transport-adapters).
- pytest — [Writing plugins](https://docs.pytest.org/en/stable/how-to/writing_plugins.html), [Fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html).
- PEP 544 — [Protocols: Structural subtyping](https://peps.python.org/pep-0544/).
- Martin Fowler — [Patterns of Enterprise Application Architecture](https://martinfowler.com/eaaCatalog/), [Circuit Breaker](https://martinfowler.com/bliki/CircuitBreaker.html).
- Michael Nygard — [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions).

**Scope note:** this is an overview lesson. It names distributed-system patterns for recognition, but does not claim to provide production-ready implementations of queues, transactions, circuit breakers, plugin isolation, or async orchestration. Those require system-specific failure models, operational controls, and tests.
