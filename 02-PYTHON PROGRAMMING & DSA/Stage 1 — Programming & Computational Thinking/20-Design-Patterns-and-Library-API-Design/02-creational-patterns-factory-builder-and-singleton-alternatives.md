# Creational Patterns: Factory, Builder, and Singleton Alternatives

> **Stage 1 — Programming & Computational Thinking** · **Module 20 — Design Patterns and Library API Design** · **Lesson 02**  
> **Target runtime:** Python 3.12+ · **Suggested checks:** `pytest`, `mypy --strict` or `pyright`, `ruff`

## 1. Learning objectives

By the end of this lesson, you should be able to:

- Explain why object-creation code becomes difficult to maintain as variants, configuration, and resource lifetimes grow.
- Choose deliberately among a constructor, named class method, factory function, registry-driven factory, abstract factory, builder, and configuration object.
- Use `copy`, `deepcopy`, and `dataclasses.replace` appropriately when creating related objects.
- Replace unnecessary singleton classes with module-level values, injected dependencies, cached factories, or explicit lazy initialization.
- Separate configuration validation from dependency construction using a composition root.
- Type factories with `type[T]`, `Callable`, callable `Protocol`s, `Self`, `Literal`, and overloads where they add value.
- Reason about object lifetime, async resource cleanup, threads, processes, and forked workers.
- Test construction logic with fakes, boundary tests, and property-based invariants.
- Refactor the `fetchkit` example so its `Fetcher` is assembled from validated configuration and replaceable HTTP, cache, clock, and retry-policy dependencies.

## 2. Prerequisites

This lesson builds on the supplied Module 20 roadmap and assumes familiarity with:

- Functions, arguments, exceptions, modules, imports, and basic type hints.
- Classes, dataclasses, composition, inheritance, and encapsulation.
- `Protocol` and dependency inversion at an introductory level.
- Decorators, registries, generators, context managers, and modern Python signatures.
- Unit tests, fakes/mocks, and the difference between unit and integration tests.

Relevant earlier modules in the project tree are Stage 1 Modules 1.8 (object-oriented design and dependency boundaries), 1.11 (data model), 1.12 (metaprogramming and registries), 1.15 (modern signatures and errors), 1.16 (advanced testing), 1.18 (packaging and entry points), and 1.23 (code reading and refactoring). This lesson introduces only the creation-related portion of those ideas; it does not replace the later lessons on structural patterns, public APIs, or plugin systems.

## 3. The object-creation problem and mental models

### 3.1 What is a creational pattern?

A **creational pattern** organizes *how objects are selected, configured, assembled, or obtained*. It is useful when construction itself has meaningful variation or policy. It is not a requirement to wrap every call to a class constructor.

Imagine a small data-fetching library called `fetchkit`. Its `Fetcher` eventually needs:

- an HTTP client to obtain bytes,
- a cache to reuse prior responses,
- a parser to interpret the bytes,
- a clock for timestamps and deterministic tests,
- a retry policy to decide whether another attempt is appropriate,
- output sinks for results.

At first, one constructor may be enough. As configuration and deployment variants grow, a single `Fetcher(...)` call can become a long list of unrelated arguments, a chain of `if` statements, or code that silently creates network clients and reads environment variables. Those are signals to clarify construction—not automatic proof that a pattern is required.

### 3.2 Why creation code becomes hard to maintain

Creation logic often accumulates four kinds of change:

1. **Selection:** choose JSON versus CSV, one HTTP implementation versus another, or one cloud-provider family versus another.
2. **Configuration:** parse environment variables, validate timeouts, and normalize URLs.
3. **Assembly:** ensure the cache, client, policy, and fetcher use compatible settings.
4. **Lifetime:** decide who owns, closes, shares, or recreates an expensive resource.

When these concerns are mixed into domain logic, tests become harder to isolate and a change in one dependency can force edits throughout the codebase. A factory or composition root centralizes the decisions; dependency injection keeps the resulting objects replaceable.

### 3.3 The creation flow

A useful production flow is:

```text
raw configuration (environment / file / CLI)
                  |
                  v
          parse and validate
                  |
                  v
        immutable typed settings
                  |
                  v
       composition root / factory
          |       |       |
          v       v       v
       client   cache   retry policy
          \       |       /
           \      |      /
                  v
               Fetcher
                  |
                  v
             application
```

The composition root is the place where concrete implementations are selected and connected. The rest of the application receives the completed dependency graph instead of searching globally for services.

### 3.4 Minimal example: start with the constructor

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Source:
    url: str
    timeout_seconds: float = 10.0

source = Source("https://example.test/data", timeout_seconds=3.0)
print(source.timeout_seconds)
```

Expected output:

```text
3.0
```

This is already a good creation API: the required value is explicit, the optional value has a sensible default, and the object is immutable at the attribute level. Add a factory only when there is additional policy to centralize.

**Use a direct constructor when** the caller already has the values and construction is simple. **Do not add a factory merely to rename `Source(...)` to `make_source(...)`.** The simplest alternative is usually the best starting point.

**Exercise:** Add a validation rule that rejects an empty URL. Expected outcome: `Source("")` raises `ValueError`, and valid URLs still construct successfully. Note that this example's `frozen=True` prevents reassignment of fields; it does not recursively freeze mutable values held by fields.

## 4. Beginner concepts

### 4.1 Simple factory function

**Definition and mental model.** A simple factory is a function that chooses and returns an object. It centralizes a construction decision behind a small call.

**Problem solved.** Callers no longer duplicate a branching decision or need to know every concrete implementation.

**Internal flow:** validate the key → select a constructor → construct the object → return it. Construction errors should retain useful context rather than being swallowed.

```python
from dataclasses import dataclass
from typing import Protocol

class Writer(Protocol):
    def write(self, text: str) -> str: ...

@dataclass(frozen=True)
class JsonWriter:
    def write(self, text: str) -> str:
        return f'{{"value": {text!r}}}'

@dataclass(frozen=True)
class CsvWriter:
    def write(self, text: str) -> str:
        return f"value\n{text}"


def make_writer(kind: str) -> Writer:
    if kind == "json":
        return JsonWriter()
    if kind == "csv":
        return CsvWriter()
    raise ValueError(f"unknown writer {kind!r}; choose 'csv' or 'json'")

print(make_writer("csv").write("hello"))
```

Expected output:

```text
value
hello
```

A factory is especially useful when the caller's choice is runtime data, such as validated configuration. If the choice is fixed at the call site and no policy exists, direct construction is clearer.

**Trade-offs and failure modes:** a factory can become a god factory that knows about unrelated components; an unvalidated key can produce cryptic `KeyError`s; a factory that performs network I/O makes tests slow and startup failure harder to localize. Keep selection narrow and usually keep external I/O out of construction.

**Testing strategy:** test each supported key, unknown keys, and that the selected implementation satisfies the expected contract. For a larger factory, inject the constructors or test its registry separately.

**Exercise:** Add a `TextWriter`. Expected outcome: `make_writer("text")` returns it, and an unsupported name produces a helpful `ValueError`.

### 4.2 Registry-driven factory

A registry maps stable identifiers to constructors or callables. It is a good fit when the set of implementations is extensible or maintained separately from the selection logic.

```python
from collections.abc import Callable

class PlainWriter:
    def write(self, text: str) -> str:
        return text

WRITERS: dict[str, Callable[[], Writer]] = {
    "json": JsonWriter,
    "csv": CsvWriter,
    "plain": PlainWriter,
}


def make_registered_writer(kind: str) -> Writer:
    try:
        constructor = WRITERS[kind]
    except KeyError:
        available = ", ".join(sorted(WRITERS))
        raise ValueError(f"unknown writer {kind!r}; available: {available}") from None
    return constructor()

print(make_registered_writer("plain").write("ok"))
```

Expected output: `ok`.

The registry stores constructors, not pre-created writer instances, so each call creates a new object. A registry of instances has different sharing and lifetime semantics. If registration is mutable, define conflict rules, test isolation, and whether the registry is frozen after startup. For a small closed set, an `if`/`elif` function may be easier to understand.

### 4.3 Constructor, class method, and factory function

These forms overlap but communicate different intent.

| Form | Best when | Example | Main trade-off |
|---|---|---|---|
| `__init__` constructor | Caller already has valid fields | `Source(url, timeout_seconds=5)` | Should not hide unrelated I/O or complex selection |
| Named class method | Alternate input representation or named construction path | `Source.from_env(env)` | Keep the name precise and validation centralized |
| Module-level factory | Selection/assembly is policy outside one class | `make_writer("csv")` | Can become a god factory if too broad |
| Registry factory | Implementations are extensible or selected by key | `make_registered_writer("plain")` | Registration and duplicate-key policy add complexity |
| Builder | Many optional parts or staged construction with cross-field invariants | `RequestBuilder(...).header(...).build()` | More API surface and mutable intermediate state |
| Configuration object | Many related settings form a coherent unit | `FetcherConfig(timeout_seconds=...)` | A config object should not become an unvalidated bag of everything |

A named alternative constructor is often the cleanest way to express conversion from another representation:

```python
from dataclasses import dataclass
from collections.abc import Mapping

@dataclass(frozen=True)
class FetcherConfig:
    base_url: str
    timeout_seconds: float = 10.0

    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> "FetcherConfig":
        try:
            base_url = env["FETCHKIT_BASE_URL"]
        except KeyError:
            raise ValueError("FETCHKIT_BASE_URL is required") from None
        try:
            timeout = float(env.get("FETCHKIT_TIMEOUT_SECONDS", "10"))
        except ValueError as exc:
            raise ValueError("FETCHKIT_TIMEOUT_SECONDS must be numeric") from exc
        if not base_url.startswith(("https://", "http://")):
            raise ValueError("FETCHKIT_BASE_URL must use http or https")
        if timeout <= 0:
            raise ValueError("FETCHKIT_TIMEOUT_SECONDS must be positive")
        return cls(base_url=base_url, timeout_seconds=timeout)

print(FetcherConfig.from_env({"FETCHKIT_BASE_URL": "https://example.test"}))
```

Expected output:

```text
FetcherConfig(base_url='https://example.test', timeout_seconds=10.0)
```

`from_env()` accepts a mapping rather than reading `os.environ` directly. This makes the method deterministic and easy to test. A thin outer function can pass `os.environ` in production. The constructor remains useful for already-parsed values, while `from_env()` owns parsing and validation for environment-derived values.

**Exercise:** Test a missing environment key, a non-numeric timeout, zero timeout, and a valid environment mapping. Expected outcome: invalid input fails before any client or network resource is created.

## 5. Intermediate patterns

### 5.1 Abstract Factory

**Definition.** An Abstract Factory provides a way to create a *family of related objects* that are intended to work together. It is not merely a function that creates one object.

**Mental model:** select a provider family once, then ask it for compatible clients. For example, a cloud family may create a storage client, queue client, and secrets client for the same provider and environment.

In Python, the family contract can be a `Protocol`; a concrete dataclass can hold constructor callables. This often avoids a deep class hierarchy.

```python
from dataclasses import dataclass
from typing import Protocol
from collections.abc import Callable

class BlobStore(Protocol):
    def read(self, key: str) -> bytes: ...

class MessageQueue(Protocol):
    def publish(self, topic: str, payload: bytes) -> None: ...

@dataclass(frozen=True)
class CloudFamily:
    make_blob_store: Callable[[], BlobStore]
    make_queue: Callable[[], MessageQueue]

@dataclass(frozen=True)
class CloudResources:
    blobs: BlobStore
    queue: MessageQueue

def create_cloud_resources(family: CloudFamily) -> CloudResources:
    return CloudResources(
        blobs=family.make_blob_store(),
        queue=family.make_queue(),
    )
```

**Flow:** composition root selects a family → factory calls its constructors → the application receives a compatible bundle. The factory does not have to know the vendor-specific classes.

**Use it when:** combinations must remain compatible, such as a provider-specific storage/queue pair or a test family of fakes. **Avoid it when:** there is only one independent object or no compatibility constraint; a direct constructor is simpler.

**Trade-offs/failure modes:** families can hide which resources are created; constructors may allocate expensive resources unexpectedly; inconsistent families can still be passed if their contract is too weak. Prefer explicit resource ownership and lifecycle management. Test each family against the same protocol contract and test the wiring without external services.

**Exercise:** Create a `FakeCloudFamily` with in-memory implementations. Expected outcome: `create_cloud_resources()` returns both fakes without network access.

### 5.2 Builder

**Definition.** A Builder assembles a more complex object through a sequence of named operations, then validates and emits the final product.

**Why it exists.** A constructor with many optional parameters can be difficult to read, especially when settings have cross-field constraints. A builder can make intent explicit and keep the final result valid.

**Internal flow:** create a mutable builder → apply configuration steps → validate all invariants at `build()` → copy mutable inputs → return a separate immutable result. Intermediate builder state is not the product and must not escape as if it were valid.

```python
from dataclasses import dataclass
from urllib.parse import urlsplit

@dataclass(frozen=True)
class HttpRequest:
    url: str
    headers: tuple[tuple[str, str], ...]
    params: tuple[tuple[str, str], ...]

class HttpRequestBuilder:
    def __init__(self, url: str) -> None:
        self._url = url
        self._headers: dict[str, str] = {}
        self._params: dict[str, str] = {}

    def header(self, name: str, value: str) -> "HttpRequestBuilder":
        if not name.strip():
            raise ValueError("header name cannot be empty")
        self._headers[name] = value
        return self

    def param(self, name: str, value: str) -> "HttpRequestBuilder":
        if not name.strip():
            raise ValueError("parameter name cannot be empty")
        self._params[name] = value
        return self

    def build(self) -> HttpRequest:
        parsed = urlsplit(self._url)
        try:
            _port = parsed.port
        except ValueError as exc:
            raise ValueError("url must contain a valid port") from exc
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("url must be an absolute http(s) URL with a host")
        return HttpRequest(
            url=self._url,
            headers=tuple(sorted(self._headers.items())),
            params=tuple(sorted(self._params.items())),
        )

request = (
    HttpRequestBuilder("https://example.test/items")
    .header("Accept", "application/json")
    .param("page", "2")
    .build()
)
print(request)
```

Expected output:

```text
HttpRequest(url='https://example.test/items', headers=(('Accept', 'application/json'),), params=(('page', '2'),))
```

The product uses tuples rather than dictionaries, so its nested collections are immutable too. `frozen=True` alone would not make a field containing a mutable dictionary immutable. This design also snapshots the builder's state: later builder changes do not mutate an already-built request.

**Use a builder when:** construction has meaningful stages, many optional parts, or invariants that are clearer when validated together. **Do not use it when:** a dataclass constructor with keyword arguments is already readable. `functools.partial` can preconfigure a callable; `dataclasses.replace` can make a modified copy of an existing dataclass without introducing a fluent builder.

**Trade-offs/failure modes:** builders add mutable state and another type; reusing a builder may unintentionally carry old settings into the next product; validation only in the builder can be bypassed if callers construct the product directly. If the product's invariant is essential, validate in the product or expose construction only through a controlled API. Keep `build()` deterministic and avoid opening sockets or writing files there.

**Testing strategy:** assert the exact immutable result, invalid input failures, independence of two built products, and that the returned product does not change when the builder is modified later.

**Exercise:** Build two requests from the same builder with different headers and decide whether reuse should be supported. Expected outcome: document the semantics; preferably each build is a snapshot, and tests prove earlier products remain unchanged.

### 5.3 Prototype: copy an existing object

**Definition.** Prototype creates a new object based on an existing instance, often changing a small subset of its fields.

Python already has several mechanisms:

- `copy.copy(x)` creates a shallow copy; nested objects remain shared.
- `copy.deepcopy(x)` recursively copies many nested objects, subject to custom copy behavior and objects that cannot sensibly be copied.
- `dataclasses.replace(x, field=value)` constructs a new dataclass instance with selected fields changed. It calls the class constructor and `__post_init__`, and it is shallow for unchanged fields.

```python
from copy import copy, deepcopy
from dataclasses import dataclass, replace

@dataclass
class JobConfig:
    name: str
    labels: list[str]

original = JobConfig("daily", ["batch"])
shallow = copy(original)
deep = deepcopy(original)
changed = replace(original, name="hourly")

shallow.labels.append("shared")
print(original.labels)  # shallow copy shares the list
print(deep.labels)      # deep copy has an independent list
print(changed.name, changed.labels)
```

Expected output:

```text
['batch', 'shared']
['batch']
hourly ['batch', 'shared']
```

**Use it when:** an existing configuration is a natural template and copying semantics are understood. **Avoid it when:** the object owns sockets, locks, transactions, generators, or other resources with nontrivial identity/lifecycle. Deep-copying a large object graph can be expensive or invalid. For immutable dataclasses, `replace()` is often the clearest option.

**Failure mode:** assuming `replace()` deep-copies nested state, or using `deepcopy()` to duplicate a resource that must not be duplicated. Test aliasing explicitly whenever nested mutability matters.

**Exercise:** Replace `labels` with a new list using `replace(original, labels=[*original.labels, "urgent"])`. Expected outcome: the new object has the added label, and the original list is unaffected by mutations to the new list.

### 5.4 Singleton alternatives

A **Singleton** restricts a class to one instance, often globally. The classic metaclass or `__new__` implementation is rarely the first choice in Python because module imports already cache module objects in a process, and explicit dependency injection is easier to reason about.

#### Alternative A: module-level instance

```python
# settings.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Defaults:
    timeout_seconds: float = 10.0

DEFAULTS = Defaults()
```

This is simple for immutable constants or process-wide immutable defaults. Import caching means ordinary imports reuse the module object within that interpreter process. It does **not** mean one instance across processes, nor does it make mutable module state thread-safe. Avoid a mutable global settings object whose values tests or callers can change behind each other's backs.

#### Alternative B: dependency injection

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    timeout_seconds: float

class ReportService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def timeout(self) -> float:
        return self._settings.timeout_seconds

service = ReportService(Settings(timeout_seconds=2.5))
print(service.timeout())
```

Expected output: `2.5`.

The object may be shared by the composition root when sharing is appropriate, but the service does not enforce global identity. Tests can inject a different settings object without resetting process-wide state. This is usually the best alternative to a singleton settings class.

#### Alternative C: cached factory

```python
from functools import cache

@cache
def default_parser() -> "Parser":
    return Parser()

class Parser:
    def parse(self, text: str) -> list[str]:
        return text.split()
```

This example demonstrates a cached factory; for clarity in real code, define `Parser` before `default_parser()`, or keep the annotation quoted as above. The first call constructs and caches the object; later calls with the same cache key reuse it. `functools.cache` is unbounded and keeps references to arguments and results until cleared. It is not a resource lifecycle manager and does not guarantee that concurrent first calls invoke the wrapped function only once. Do not use it to manage sockets or clients that must be closed deterministically.

#### Alternative D: explicit lazy initialization

Lazy initialization postpones expensive creation until a resource is needed. If a shared instance must be initialized once per process, protect initialization with a lock and define how it is reset or closed. The lock protects the initialization path, not the resource's later operations.

```python
from collections.abc import Callable
from threading import Lock
from typing import Protocol

class Client(Protocol):
    def close(self) -> None: ...

class LazyClient:
    def __init__(self, factory: Callable[[], Client]) -> None:
        self._factory = factory
        self._lock = Lock()
        self._client: Client | None = None

    def get(self) -> Client:
        # Keep initialization and shutdown serialized. This intentionally takes
        # the lock on every access; optimize only after measuring contention.
        with self._lock:
            if self._client is None:
                self._client = self._factory()
            return self._client

    def close(self) -> None:
        # The owner must stop users of the returned client before closing it.
        with self._lock:
            client = self._client
            self._client = None
            if client is not None:
                client.close()
```

Define `Client` before using the class. The lock serializes initialization and `close()` calls, but it does not make the client's operations thread-safe or protect a caller that continues using a previously returned client during shutdown. The owner must quiesce users before closing. This deliberately locks every `get()` for a simple synchronization contract; optimize only after measuring contention. A failed factory call leaves `_client` unset so a later call may retry initialization.

#### Why not a metaclass or `__new__` singleton?

Such designs hide object identity behind ordinary construction, making tests order-dependent and complicating subclassing, reset behavior, threads, and process forks. They also blur ownership: which component closes the shared client? A process-global socket/client created before `fork()` must not be assumed safe in child processes; recreate process-bound resources in each worker after fork. A singleton does not solve resource pooling, thread safety, or lifecycle management by itself.

**When to use a singleton-like scope:** immutable process-wide metadata or a resource with a deliberately defined process-wide lifetime. **When not to:** mutable application settings, user/request-specific state, test-controlled dependencies, or resources whose lifecycle differs by worker/task. Prefer explicit injection or a composition-root-owned instance.

### 5.5 Dependency injection, composition roots, and service locators

**Dependency injection (DI)** means an object receives the collaborators it needs rather than creating or globally locating them. It is a design technique, not necessarily a framework.

**Composition root** is the small part of the program that knows concrete implementations and wires them together. It commonly runs at startup, after configuration validation.

```python
class CsvParser:
    def parse(self, text: str) -> list[str]:
        return [line for line in text.splitlines() if line]

class Fetcher:
    def __init__(self, parser: CsvParser) -> None:
        self._parser = parser

# Composition root / application startup:
parser = CsvParser()
fetcher = Fetcher(parser)
```

This explicit wiring is usually enough. A **service locator** instead exposes a global `get_service("parser")` lookup. That hides dependencies from the constructor signature and can fail at runtime when a registration is missing. DI containers can be useful for large object graphs and scoped lifetimes, but should not obscure the dependency graph. Start with manual wiring; adopt a container when lifecycle/scope management or graph complexity provides measurable value.

**Trade-offs:** injection adds constructor parameters, but makes dependencies visible and tests deterministic. Too much injection can create a constructor with many unrelated dependencies—a signal to split responsibilities or bundle a coherent set in a typed configuration/dependency object, not to hide them in a global locator.

### 5.6 `cached_property` and lazy derived values

`functools.cached_property` computes a value on first attribute access and stores it on the instance. It is appropriate for expensive, stable derived values whose invalidation rules are clear.

```python
from functools import cached_property

class DatasetSummary:
    def __init__(self, rows: tuple[tuple[str, ...], ...]) -> None:
        self.rows = rows

    @cached_property
    def row_count(self) -> int:
        print("computing row count")
        return len(self.rows)

summary = DatasetSummary((("a",), ("b",)))
print(summary.row_count)
print(summary.row_count)
```

Expected output:

```text
computing row count
2
2
```

The cached attribute can become stale if its inputs mutate; deleting the attribute allows recomputation. In Python 3.12+, `cached_property` no longer includes the old undocumented per-property lock, so concurrent access may compute the value more than once. The getter should be idempotent or use explicit synchronization if duplicate computation is unsafe. It generally requires an instance `__dict__`, so it does not work on every `__slots__`-only class.

### 5.7 Object pools and resource ownership

An **object pool** reuses a bounded set of expensive resources, such as database connections. It is not the same as a singleton: a pool manages multiple resources, acquisition, release, capacity, and health.

Use a maintained pool implementation where available rather than building one casually. A production pool needs:

- bounded capacity and a defined wait/timeout behavior;
- acquisition and release semantics, including exception paths;
- health checks and stale-resource handling;
- shutdown/close behavior;
- concurrency safety and observability for exhaustion;
- a policy for process forks and worker startup.

A generic sketch of correct ownership is:

```python
from contextlib import contextmanager
from collections.abc import Iterator

class ConnectionPool:
    def acquire(self) -> "Connection": ...
    def release(self, connection: "Connection") -> None: ...

@contextmanager
def connection_from(pool: ConnectionPool) -> Iterator["Connection"]:
    connection = pool.acquire()
    try:
        yield connection
    finally:
        pool.release(connection)
```

This is illustrative pseudocode because `Connection` and the concrete pool are intentionally not defined here. The `finally` block is the important lifecycle guarantee. In production, prefer a real pool library with tested concurrency and failure behavior. Connection pooling details are developed further in the later data-engineering stage; this lesson focuses on creation and ownership.

## 6. Advanced production considerations

### 6.1 Choosing the creation API

Use the least powerful mechanism that expresses the requirement clearly.

| Requirement | Default choice | Upgrade when… |
|---|---|---|
| Validated fields already available | Constructor + dataclass | Cross-field invariants need a named creation path |
| Parse environment/file/serialized representation | `from_env()`, `from_dict()`, or another named class method | Selection spans unrelated types |
| Choose one implementation from a key | Factory function | The set is extensible or registration is valuable |
| Create compatible families | Abstract Factory / family of callables | Several products must vary together |
| Many staged options and final invariants | Builder | Keyword arguments remain easy to read |
| Reuse an existing object's values | `replace`, `copy`, `deepcopy` | Custom cloning semantics are needed |
| Reuse a shared dependency | Composition root + DI | A well-defined shared lifetime is required |
| Expensive stable derived value | `cached_property` | Invalidation/concurrency requires explicit policy |
| Reuse bounded external resources | Resource pool | Capacity, health, and lifecycle management are necessary |

Avoid constructors that open network connections, create files, or contact cloud services. Constructors should generally establish local object state and validate local invariants. Resource acquisition belongs in an explicit factory/startup function or context manager with a clear cleanup path.

### 6.2 Typing factories

Python's type system can express common factory shapes without building a large hierarchy.

#### A generic class constructor: `type[T]`

```python
from typing import TypeVar

T = TypeVar("T")

def instantiate(cls: type[T]) -> T:
    return cls()

class Token:
    pass

assert isinstance(instantiate(Token), Token)
```

This type is appropriate only when `cls()` is valid for every accepted `T`. If constructors need arguments, model those arguments explicitly or accept a callable with the required signature.

#### Callable protocol

```python
from typing import Protocol, TypeVar

T_co = TypeVar("T_co", covariant=True)

class Factory(Protocol[T_co]):
    def __call__(self) -> T_co: ...
```

A callable protocol can name a factory dependency in a constructor. If the callable takes arguments, include them in `__call__`. Keep protocol variance and generic bounds as simple as possible; do not force advanced typing syntax into a small function that `Callable[[], T]` already describes.

#### `Self` for fluent builders

```python
from typing import Self

class HeaderBuilder:
    def __init__(self) -> None:
        self._headers: dict[str, str] = {}

    def header(self, name: str, value: str) -> Self:
        self._headers[name] = value
        return self
```

`Self` preserves the concrete subclass type in fluent chains. It is appropriate when a method returns the same instance. It does not make mutable builder state safe to share across threads.

#### `Literal` and overloads for closed registries

```python
from typing import Literal, overload

@overload
def make_format(name: Literal["json"]) -> JsonWriter: ...

@overload
def make_format(name: Literal["csv"]) -> CsvWriter: ...

@overload
def make_format(name: str) -> Writer: ...

def make_format(name: str) -> Writer:
    if name == "json":
        return JsonWriter()
    if name == "csv":
        return CsvWriter()
    raise ValueError(f"unsupported format {name!r}; choose 'csv' or 'json'")
```

This is a closed-key illustration: callers using literal keys get precise return types. A public API that accepts arbitrary strings should expose the runtime unknown-key error too, and overloads should reflect the actual accepted inputs. If the registry is open to third-party plugins, static overloads cannot enumerate all future plugins; a common `Protocol` return type is more honest.

### 6.3 Manual wiring versus a DI container

Manual wiring is transparent and has almost no framework cost. It is ideal for small and medium applications where the composition root is readable. A DI container can help when there are many dependencies, scoped lifetimes, conditional bindings, or complicated async startup/shutdown. It introduces framework vocabulary and another configuration layer, so it should solve an observed problem.

| Dimension | Manual wiring | DI container |
|---|---|---|
| Discoverability | Direct Python calls | May require container introspection |
| Initial complexity | Low | Higher setup and concepts |
| Large object graph | Can become verbose | Can centralize graph configuration |
| Lifetimes/scopes | Explicit code | Often built-in, but must be understood |
| Debugging | Ordinary stack traces | May include resolution errors and framework layers |
| Testing | Pass fakes directly | Override bindings or create test containers |

Do not use a container as a global service locator. Keep dependency resolution near the composition root and keep application objects explicit about what they need.

### 6.4 Request/task scopes and async resources

A dependency may be application-scoped, request-scoped, or task-scoped. A database connection should not casually be shared across unrelated requests; a request-specific transaction must not outlive its request. An async client often needs explicit asynchronous startup and cleanup.

```python
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

class AsyncClient:
    async def aclose(self) -> None:
        ...

@asynccontextmanager
async def open_client() -> AsyncIterator[AsyncClient]:
    client = AsyncClient()  # local construction; real clients may open resources here
    try:
        yield client
    finally:
        await client.aclose()
```

This is an illustrative lifecycle shape, not a real network client. In application code, use the client library's documented async context manager when available. Create the resource inside the correct event loop/lifespan and close it in that same lifecycle. Do not create an async client at import time or reuse it across event loops unless the library explicitly supports that usage.

### 6.5 Fail-fast configuration and startup

Parse configuration and validate it before constructing expensive dependencies. Invalid timeout values, missing required URLs, conflicting settings, or unsupported implementation names should fail during startup with a clear error, not on the first production request.

A robust order is:

1. Read raw values from environment/config files/CLI.
2. Parse and validate them into a typed config object.
3. Construct dependencies using those validated values.
4. Run safe startup checks where appropriate (for example, verify required configuration and optionally check service health with a bounded timeout).
5. Publish the ready application object.
6. Close owned resources during shutdown.

Do not confuse validation with availability: a URL can be syntactically valid while the remote service is down. Network health checks should be explicit, bounded, observable, and have a deliberate policy for whether startup must fail.

### 6.6 Thread and process safety

- A shared instance is not automatically thread-safe. Protect mutable shared state with a lock or use immutable data and thread-safe primitives.
- `functools.cache` and `lru_cache` keep cached references; their internal cache data structures are thread-safe, but the wrapped function may run more than once during concurrent first calls.
- A lock around lazy initialization prevents competing threads from initializing at once only if all creation paths use that lock. It does not make the client itself safe for concurrent requests.
- After `fork()`, inherited file descriptors and client internals may be in an invalid state. Create process-bound clients and pools in each child worker after fork, or follow the library's documented process model.
- Do not rely on import-time creation for process-sensitive resources. Prefer worker startup hooks or explicit factories.
- Avoid double-checked locking unless there is a real need and the synchronization contract is clear. A simple lock around the whole initialization path is easier to review; optimize only if initialization contention matters.

### 6.7 Testing factories and builders

Creation code is policy and deserves direct tests.

- **Factory tests:** each valid key, invalid key, constructor arguments, and constructor failure behavior.
- **Config tests:** missing fields, malformed values, lower/upper boundaries, and cross-field constraints.
- **Builder tests:** valid fluent chains, invalid final state, snapshot immutability, and no mutation leakage between builds.
- **Composition-root tests:** assert the correct fake dependencies are passed to the service; no network or database access is needed.
- **Resource tests:** cleanup occurs on normal return and exception; repeated startup/shutdown does not leak resources.
- **Property-based tests:** when using Hypothesis, generate many valid and invalid configurations to test invariants rather than a handful of examples. For instance, every accepted timeout must be greater than zero, and every built request URL must use HTTP or HTTPS.

Test doubles should model the contract the application actually uses, not every method in a third-party SDK. A fake clock and fake HTTP client are especially valuable because tests become deterministic and do not sleep or contact the network.

## 7. Comparative decision guide

Use this checklist before introducing a creation abstraction:

1. Is there more than one real variant, or a measurable pain such as duplicated branching, change amplification, or hard-to-test construction?
2. Does the abstraction centralize a stable decision, or merely add a layer of indirection?
3. Is object lifetime explicit: who owns it, shares it, closes it, and recreates it after a process boundary?
4. Can configuration be validated before side effects begin?
5. Can tests inject fakes without monkeypatching globals or resetting singleton state?
6. Does the resulting API make invalid states difficult to construct?

A useful rule of thumb from the roadmap is to start with the simplest code and introduce a pattern when there are **two or three real variants** or measurable design pain. This is not a law. Abstract earlier when a safety boundary, external contract, or expensive irreversible operation requires an explicit seam before a second implementation exists. Do not abstract merely because a pattern has a name.

## 8. `fetchkit` case-study evolution

This section brings the ideas together. The code is a small, runnable teaching model rather than a complete HTTP library. It intentionally does not perform real network requests; a production HTTP adapter would implement the `HttpClient` protocol and apply its own timeout, TLS, proxy, and response-size policies.

### 8.1 Version 1: simple but tightly coupled

```python
import os

class FetcherV1:
    def fetch(self, path: str) -> str:
        base_url = os.environ["FETCHKIT_BASE_URL"]
        timeout = float(os.environ.get("FETCHKIT_TIMEOUT_SECONDS", "10"))
        # Pretend this line calls a real HTTP client.
        return f"GET {base_url.rstrip('/')}/{path.lstrip('/')} timeout={timeout}"

# FetcherV1().fetch("items") reads the environment on every call.
```

This is easy to begin with but has problems: environment access is hidden in domain behavior, malformed settings fail late, tests depend on process state, and client/cache/clock/retry behavior cannot be substituted independently.

### 8.2 Version 2: typed dependencies and validated configuration

The following code is self-contained and can be saved as `fetchkit_demo.py`. It uses protocols to describe only the operations `Fetcher` needs, immutable configuration and retry policy values, and injected fakes for tests.

```python
from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable, Mapping
from math import isfinite
from typing import Protocol
from urllib.parse import urlsplit


@dataclass(frozen=True)
class HttpRequest:
    url: str
    headers: tuple[tuple[str, str], ...]
    params: tuple[tuple[str, str], ...]


class HttpRequestBuilder:
    def __init__(self, url: str) -> None:
        self._url = url
        self._headers: dict[str, str] = {}
        self._params: dict[str, str] = {}

    def header(self, name: str, value: str) -> HttpRequestBuilder:
        if not name.strip():
            raise ValueError("header name cannot be empty")
        self._headers[name] = value
        return self

    def param(self, name: str, value: str) -> HttpRequestBuilder:
        if not name.strip():
            raise ValueError("parameter name cannot be empty")
        self._params[name] = value
        return self

    def build(self) -> HttpRequest:
        parsed = urlsplit(self._url)
        try:
            _port = parsed.port
        except ValueError as exc:
            raise ValueError("url must contain a valid port") from exc
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("url must be an absolute http(s) URL with a host")
        return HttpRequest(
            url=self._url,
            headers=tuple(sorted(self._headers.items())),
            params=tuple(sorted(self._params.items())),
        )


@dataclass(frozen=True)
class FetcherConfig:
    base_url: str
    timeout_seconds: float = 10.0
    max_attempts: int = 3

    def __post_init__(self) -> None:
        parsed = urlsplit(self.base_url)
        try:
            _port = parsed.port
        except ValueError as exc:
            raise ValueError("base_url must contain a valid port") from exc
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("base_url must be an absolute http(s) URL with a host")
        if not isfinite(self.timeout_seconds) or self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be finite and positive")
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")

    @classmethod
    def from_mapping(cls, values: Mapping[str, str]) -> FetcherConfig:
        try:
            base_url = values["FETCHKIT_BASE_URL"]
        except KeyError:
            raise ValueError("FETCHKIT_BASE_URL is required") from None
        try:
            timeout = float(values.get("FETCHKIT_TIMEOUT_SECONDS", "10"))
            attempts = int(values.get("FETCHKIT_MAX_ATTEMPTS", "3"))
        except ValueError as exc:
            raise ValueError("timeout and max attempts must be numeric") from exc
        return cls(base_url, timeout, attempts)


class HttpClient(Protocol):
    def get(self, url: str, *, timeout_seconds: float) -> str: ...


class Cache(Protocol):
    def get(self, key: str) -> str | None: ...
    def set(self, key: str, value: str) -> None: ...


class Clock(Protocol):
    def now(self) -> float: ...


class RetryPolicy(Protocol):
    def should_retry(self, attempt: int, error: Exception) -> bool: ...


@dataclass(frozen=True)
class FixedRetryPolicy:
    max_attempts: int

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")

    def should_retry(self, attempt: int, error: Exception) -> bool:
        transient = isinstance(error, (TimeoutError, ConnectionError))
        return transient and attempt < self.max_attempts


class Fetcher:
    def __init__(
        self,
        config: FetcherConfig,
        client: HttpClient,
        cache: Cache,
        clock: Clock,
        retry_policy: RetryPolicy,
    ) -> None:
        self._config = config
        self._client = client
        self._cache = cache
        self._clock = clock
        self._retry_policy = retry_policy
        self._last_fetched_at: float | None = None

    @property
    def last_fetched_at(self) -> float | None:
        """Timestamp of the last successful network fetch, if any."""
        return self._last_fetched_at

    def fetch(self, path: str) -> str:
        normalized_path = path.lstrip("/")
        url = f"{self._config.base_url.rstrip('/')}/{normalized_path}"
        cached = self._cache.get(url)
        if cached is not None:
            return cached

        attempt = 1
        while True:
            try:
                body = self._client.get(
                    url, timeout_seconds=self._config.timeout_seconds
                )
            except (TimeoutError, ConnectionError) as exc:
                if not self._retry_policy.should_retry(attempt, exc):
                    raise
                attempt += 1
                continue

            # Cache and clock failures are not transport failures and must not
            # cause another HTTP request. Their error policy is separate.
            fetched_at = self._clock.now()
            self._cache.set(url, body)
            self._last_fetched_at = fetched_at
            return body


class InMemoryCache:
    def __init__(self) -> None:
        self._values: dict[str, str] = {}

    def get(self, key: str) -> str | None:
        return self._values.get(key)

    def set(self, key: str, value: str) -> None:
        self._values[key] = value


@dataclass
class FakeClock:
    value: float = 100.0

    def now(self) -> float:
        return self.value


class FakeHttpClient:
    def __init__(self, responses: list[str | Exception]) -> None:
        self._responses = list(responses)
        self.calls: list[tuple[str, float]] = []

    def get(self, url: str, *, timeout_seconds: float) -> str:
        self.calls.append((url, timeout_seconds))
        response = self._responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def build_fetcher(
    values: Mapping[str, str],
    *,
    client: HttpClient | None = None,
    client_factory: Callable[[FetcherConfig], HttpClient] | None = None,
    cache: Cache | None = None,
    clock: Clock | None = None,
) -> Fetcher:
    """Validate config before asking a factory to allocate an HTTP client."""
    if client is not None and client_factory is not None:
        raise ValueError("provide client or client_factory, not both")

    config = FetcherConfig.from_mapping(values)
    if client is None:
        if client_factory is None:
            raise ValueError("provide a client or client_factory")
        selected_client = client_factory(config)
    else:
        selected_client = client

    selected_cache = cache if cache is not None else InMemoryCache()
    selected_clock = clock if clock is not None else FakeClock()
    policy = FixedRetryPolicy(config.max_attempts)
    return Fetcher(config, selected_client, selected_cache, selected_clock, policy)
```

The code demonstrates a policy choice: `Fetcher` receives collaborators, and the composition root selects defaults. The fallback uses `is None` rather than `cache or InMemoryCache()` so a valid dependency with false truthiness is not accidentally replaced. `FixedRetryPolicy` is deliberately minimal; it retries only `TimeoutError` and `ConnectionError`, and a production policy would add bounded backoff/jitter, respect deadlines, and avoid retrying non-idempotent operations without safeguards. The retry boundary surrounds only the HTTP call: cache or clock failures are not mistaken for transport failures and cannot trigger a duplicate request.

### 8.3 Version 3: composition root and tests

Append the following tests to `test_fetchkit_demo.py` after importing the definitions above (or place the implementation in `fetchkit_demo.py` and import them). These tests use no real network and no sleeps.

```python
import pytest

from fetchkit_demo import (
    FakeClock,
    FakeHttpClient,
    FetcherConfig,
    InMemoryCache,
    build_fetcher,
)


def test_factory_wires_dependencies_and_fetches() -> None:
    client = FakeHttpClient(["payload"])
    cache = InMemoryCache()
    clock = FakeClock(123.0)
    fetcher = build_fetcher(
        {"FETCHKIT_BASE_URL": "https://example.test", "FETCHKIT_TIMEOUT_SECONDS": "2"},
        client=client,
        cache=cache,
        clock=clock,
    )

    assert fetcher.fetch("/items") == "payload"
    assert client.calls == [("https://example.test/items", 2.0)]
    assert fetcher.last_fetched_at == 123.0
    assert fetcher.fetch("items") == "payload"  # cache hit; no second HTTP call
    assert len(client.calls) == 1
    assert fetcher.last_fetched_at == 123.0  # cache hits do not rewrite fetch time


def test_retries_then_succeeds() -> None:
    client = FakeHttpClient([TimeoutError("temporary"), "ok"])
    fetcher = build_fetcher(
        {"FETCHKIT_BASE_URL": "https://example.test", "FETCHKIT_MAX_ATTEMPTS": "2"},
        client=client,
    )
    assert fetcher.fetch("health") == "ok"
    assert len(client.calls) == 2


@pytest.mark.parametrize(
    "values",
    [
        {},
        {"FETCHKIT_BASE_URL": "file:///tmp/data"},
        {"FETCHKIT_BASE_URL": "https://"},
        {"FETCHKIT_BASE_URL": "https://example.test:bad"},
        {"FETCHKIT_BASE_URL": "https://example.test", "FETCHKIT_TIMEOUT_SECONDS": "0"},
        {"FETCHKIT_BASE_URL": "https://example.test", "FETCHKIT_MAX_ATTEMPTS": "0"},
        {"FETCHKIT_BASE_URL": "https://example.test", "FETCHKIT_TIMEOUT_SECONDS": "fast"},
        {"FETCHKIT_BASE_URL": "https://example.test", "FETCHKIT_TIMEOUT_SECONDS": "nan"},
    ],
)
def test_invalid_configuration_fails_before_fetch(values: dict[str, str]) -> None:
    client = FakeHttpClient([])
    with pytest.raises(ValueError):
        build_fetcher(values, client=client)
    assert client.calls == []


def test_config_boundary_values() -> None:
    assert FetcherConfig("http://localhost", 0.001, 1).max_attempts == 1
    for invalid_timeout in (-0.001, float("nan"), float("inf")):
        with pytest.raises(ValueError):
            FetcherConfig("http://localhost", invalid_timeout, 1)


def test_non_transport_error_is_not_retried() -> None:
    client = FakeHttpClient([ValueError("invalid request"), "must not be used"])
    fetcher = build_fetcher(
        {"FETCHKIT_BASE_URL": "https://example.test", "FETCHKIT_MAX_ATTEMPTS": "3"},
        client=client,
    )
    with pytest.raises(ValueError, match="invalid request"):
        fetcher.fetch("items")
    assert len(client.calls) == 1


def test_cache_failure_does_not_repeat_http_request() -> None:
    class FailingCache:
        def get(self, key: str) -> str | None:
            return None

        def set(self, key: str, value: str) -> None:
            raise RuntimeError("cache unavailable")

    client = FakeHttpClient(["payload", "must not be used"])
    fetcher = build_fetcher(
        {"FETCHKIT_BASE_URL": "https://example.test", "FETCHKIT_MAX_ATTEMPTS": "3"},
        client=client,
        cache=FailingCache(),
    )
    with pytest.raises(RuntimeError, match="cache unavailable"):
        fetcher.fetch("items")
    assert len(client.calls) == 1


def test_client_factory_runs_only_after_validated_configuration() -> None:
    created: list[FetcherConfig] = []

    def make_client(config: FetcherConfig) -> FakeHttpClient:
        created.append(config)
        return FakeHttpClient(["ok"])

    with pytest.raises(ValueError):
        build_fetcher({}, client_factory=make_client)
    assert created == []

    fetcher = build_fetcher(
        {"FETCHKIT_BASE_URL": "https://example.test"},
        client_factory=make_client,
    )
    assert fetcher.fetch("items") == "ok"
    assert len(created) == 1
```

Run with:

```bash
python -m pytest -q
```

Expected test result: **16 passed** (eight invalid-configuration cases plus the wiring/cache, retry, boundary, non-transport failure, cache-failure, client-factory-ordering, builder-snapshot, and builder-validation tests). If you copy only part of the code, ensure the imports and module names match your file layout.

**Important production boundaries:**

- The simple fake cache is not thread-safe and is unbounded. A real cache needs a capacity/eviction policy, concurrency behavior, and invalidation semantics.
- A real HTTP adapter must enforce timeouts, validate TLS behavior, constrain redirects and response sizes, and consider SSRF if callers can control URLs. Those details belong in the HTTP/security lessons, not in this creation-pattern lesson.
- The injected clock records `last_fetched_at` only after a successful network fetch and cache write; cache hits leave that timestamp unchanged. The example uses numeric clock values for deterministic tests. If timestamps are persisted or exposed as wall-clock time, define timezone and clock semantics explicitly.
- A retry policy should distinguish transient from permanent failures and respect idempotency. Retrying every `Exception` is illustrative only and should not be copied into production.
- The factory creates the in-memory cache if none is supplied; ownership of external clients is not transferred or closed by `Fetcher`. In production, document whether the caller or the composition root owns and closes each resource.

### 8.4 Builder produces an immutable fetch request

The `HttpRequestBuilder` above is the builder portion of the case study. Its result stores headers and parameters as tuples, so the product is immutable at both the dataclass field and collection level. The implementation is included in the runnable `fetchkit_demo.py` block, so it can be tested with the rest of the case study. If `fetchkit` later needs more complex request construction, this is a reasonable extension point; for the current minimal fetch API, a URL plus keyword options may remain simpler.

Add these tests to `test_fetchkit_demo.py` to verify builder invariants and snapshot semantics:

```python
from dataclasses import FrozenInstanceError

import pytest

from fetchkit_demo import HttpRequestBuilder


def test_builder_returns_immutable_snapshot() -> None:
    builder = HttpRequestBuilder("https://example.test/items")
    builder.header("Accept", "application/json")
    first = builder.param("page", "1").build()
    builder.param("page", "2")
    second = builder.build()

    assert first.params == (("page", "1"),)
    assert second.params == (("page", "2"),)
    with pytest.raises(FrozenInstanceError):
        first.url = "https://other.test"  # type: ignore[misc]


def test_builder_rejects_invalid_url_and_empty_header() -> None:
    with pytest.raises(ValueError, match="url"):
        HttpRequestBuilder("file:///tmp/data").build()
    with pytest.raises(ValueError, match="host"):
        HttpRequestBuilder("https://").build()
    with pytest.raises(ValueError, match="port"):
        HttpRequestBuilder("https://example.test:bad").build()
    with pytest.raises(ValueError, match="header name"):
        HttpRequestBuilder("https://example.test").header("  ", "x")
```

### 8.5 Singleton global state versus injection

A fragile design might have `settings = Settings.from_env()` at import time and let every `Fetcher` read it globally. That causes hidden dependencies and makes test cases interfere. Instead, `build_fetcher()` receives a mapping and explicit client/cache/clock dependencies. Tests construct independent graphs and can prove that one test's settings do not affect another. If an application wants one shared HTTP client, create it once in the composition root and inject it into the services that should share it; close it during application shutdown.

## 9. Tests and hands-on exercises

### Exercise 1 — Improve the simple factory

Add a `make_parser(format_name: str)` factory with CSV and JSON implementations. Test both supported formats and the unknown-format message. Keep selection separate from parsing.

**Expected outcome:** adding a format requires one explicit registration/selection change; unsupported values fail with a clear error.

### Exercise 2 — Constructor or builder?

Design a `RetryConfig` with `max_attempts`, `base_delay_seconds`, and `max_delay_seconds`. Decide whether a frozen dataclass constructor is sufficient or a builder is justified. Validate that attempts are at least one, delays are non-negative, and maximum delay is not less than base delay.

**Expected outcome:** invalid configurations cannot be accepted. Prefer the dataclass unless staged configuration makes the builder materially clearer.

### Exercise 3 — Copy semantics

Create a dataclass containing a nested dictionary and list. Compare `copy.copy`, `copy.deepcopy`, and `dataclasses.replace`. Mutate the nested objects and record which instances change.

**Expected outcome:** shallow copy and `replace` share unchanged nested objects; `deepcopy` recursively copies many nested objects, subject to object-specific behavior.

### Exercise 4 — Remove a singleton

Refactor a global settings singleton into a `Settings` dataclass passed to a service constructor. Write two tests with different timeouts and prove that the services remain independent.

**Expected outcome:** no global reset fixture is needed and test order does not affect the result.

### Exercise 5 — Composition root

Extend `build_fetcher()` to accept a parser dependency or parser factory. The HTTP client factory seam in the case study demonstrates the same ordering: validate configuration before resource creation. Add a test proving invalid configuration does not call the client factory.

**Expected outcome:** invalid configuration fails fast and the composition root remains the only place that selects concrete dependencies.

### Exercise 6 — Property-based invariant (optional Hypothesis)

Write a Hypothesis test that generates positive timeout values and asserts that `FetcherConfig` accepts them. Generate zero and negative values separately and assert rejection. Keep strategies bounded and account for floating-point edge cases such as NaN: if your API must reject NaN and infinity, add explicit `math.isfinite()` validation and test it.

**Expected outcome:** tests verify the invariant over many generated examples, not just one hand-picked timeout. Do not add Hypothesis as a required runtime dependency; it belongs in development/test dependencies.

## 10. Common mistakes and anti-patterns

1. **Singleton via metaclass for convenience.** It hides identity, creates global coupling, complicates reset and lifecycle, and does not solve thread/process safety. Prefer injection or an explicitly shared instance owned by the composition root.
2. **Constructors that open files or connections.** Hidden I/O makes object creation slow and failure-prone. Use explicit startup factories/context managers with cleanup.
3. **Builders that allow invalid intermediate states to escape.** Keep builder state private and validate at `build()`; ensure the final product itself cannot violate critical invariants through another construction path.
4. **God factories.** A single factory that constructs every unrelated service becomes a second application with tangled conditionals. Split by cohesive family or concern.
5. **Mutable global configuration.** It causes test-order dependence and unclear ownership. Parse settings once, validate them, and inject the immutable result.
6. **Boolean-flag parameter explosions.** Calls such as `create_client(True, False, True)` are hard to interpret. Prefer keyword-only named options, enums, or separate focused functions when the flags express distinct modes.
7. **Using a builder for every object.** A simple dataclass with keyword arguments is often clearer and easier for type checkers.
8. **Assuming `frozen=True` is deep immutability.** A frozen dataclass can still contain a mutable list or dictionary. Use immutable nested values or defensive copies when the contract requires it.
9. **Treating a cache as a lifecycle manager.** Caching an object does not ensure it is closed, healthy, safe across threads, or valid after fork.
10. **Overusing a DI container or service locator.** A container is useful only when it pays for its complexity; global lookup hides dependencies and moves failures to runtime.
11. **Creating resources before validating configuration.** Validate cheap inputs first so bad settings do not leave partially created clients, pools, or files.
12. **Overgeneralizing the retry policy.** Retrying every exception can hide permanent errors, amplify load, and duplicate side effects. Use explicit transient-error classification, bounded attempts, backoff, deadlines, and idempotency safeguards.

## 11. Self-check questions with model answers

### 1. Why prefer `Foo.from_env()` over `Foo(env=...)` with many optional arguments?

`from_env()` names the input representation and owns parsing and validation at a clear boundary. It keeps `__init__` focused on already-parsed values, avoids a constructor overloaded with environment-specific optional arguments, and makes the behavior testable by passing a mapping. It also makes failure messages about missing or malformed environment values precise. If there are only one or two simple fields and no distinct parsing path, a separate method may be unnecessary.

### 2. Replace a metaclass-singleton settings object with dependency injection and show the test benefit.

Use a frozen `Settings` dataclass and pass it to each service constructor. The composition root can create one shared settings instance for production, but tests can pass different instances. For example, one test injects a 1-second timeout and another injects a 5-second timeout; neither test needs to mutate or reset global singleton state. This improves isolation, parallel test safety, and clarity about each service's dependencies.

### 3. Implement a fluent builder that produces an immutable object and test its invariants.

Use `HttpRequestBuilder` from Section 5.2. Chain `.header()` and `.param()` calls, then call `.build()`. `build()` validates the URL and converts internal dictionaries to sorted tuples in a frozen `HttpRequest`. Tests should assert the expected product, reject an invalid URL or empty field name, and prove that later builder changes do not mutate a previously built request. The final product—not only the builder—must preserve the invariant.

## 12. Lesson summary and completion checklist

Creational patterns are about making construction policy explicit while keeping the simplest valid design. Python's constructors, named class methods, functions, registries, dataclasses, and callable protocols already solve many common cases. Abstract Factory is useful for compatible product families; Builder is useful when staged construction and cross-field validation improve clarity; Prototype is usually handled by explicit copy operations. Singleton classes are often better replaced with immutable module-level defaults, explicit dependency injection, a cached pure factory, or a deliberately managed per-process resource.

The `fetchkit` refactor demonstrates the production boundary: validate configuration first, then wire injectable collaborators in a composition root. Keep resource ownership, concurrency, async cleanup, and process lifecycle explicit. Test creation policy with fakes and boundary tests; add a pattern when real variants or measurable design pain justify its cost.

Checklist:

- [ ] I can explain the difference between a constructor, class method, factory, registry, Abstract Factory, and Builder.
- [ ] I can validate configuration before constructing dependencies.
- [ ] I can explain shallow versus deep copying and `dataclasses.replace` semantics.
- [ ] I can replace singleton global state with injected dependencies.
- [ ] I understand that cached/lazy construction does not automatically guarantee lifecycle, thread safety, or fork safety.
- [ ] I can write a composition root that assembles `fetchkit` with fake dependencies.
- [ ] I can test invalid inputs, boundary values, and immutable builder results.
- [ ] I can justify a pattern by variants, measurable pain, or a required safety boundary—not by fashion.

## 13. References

- Python documentation, **Classes**: https://docs.python.org/3/tutorial/classes.html
- Python documentation, **`dataclasses`**: https://docs.python.org/3/library/dataclasses.html
- Python documentation, **`copy` — shallow and deep copy operations**: https://docs.python.org/3/library/copy.html
- Python documentation, **`functools` — `cache` and `cached_property`**: https://docs.python.org/3/library/functools.html
- Python documentation, **`typing` — `Protocol`, `Self`, `Literal`, overloads, and `TypeVar`**: https://docs.python.org/3/library/typing.html
- Python documentation, **`contextlib` — synchronous and asynchronous context managers**: https://docs.python.org/3/library/contextlib.html
- Python documentation, **`threading`**: https://docs.python.org/3/library/threading.html
- Python documentation, **`os.fork` and process behavior**: https://docs.python.org/3/library/os.html#os.fork
- Python documentation, **`multiprocessing` programming guidelines**: https://docs.python.org/3/library/multiprocessing.html
- Hypothesis documentation: https://hypothesis.readthedocs.io/
- The supplied `roadmap-Design-Patterns-and-Library-API-Design.md`, Module 20, Lesson 02 — authoritative scope, progression, common mistakes, and self-checks.
- The supplied `Roadmap_ptree.md`, Stage 1 — project-tree placement for `20-Design-Patterns-and-Library-API-Design/`.
