# Structural Patterns: Adapter, Facade, and Proxy

> **Stage:** 1 — Programming & Computational Thinking  
> **Module:** 1.20 — Design Patterns and Library API Design  
> **Lesson:** 03 — Structural patterns: Adapter, Facade, and Proxy  
> **Target:** Python 3.12+  
> **Running case study:** `fetchkit`, a small data-fetching library

## 1. Learning objectives

By the end of this lesson, you should be able to:

- Explain how structural patterns organize relationships between objects and how they differ from creational and behavioural patterns.
- Define an application-owned `Protocol` and adapt a vendor-shaped HTTP or storage client to it.
- Distinguish an Adapter, Facade, object-wrapping Decorator, and Proxy by their intent—not merely by their use of composition.
- Use duck typing, composition, delegation, `__getattr__`, `singledispatchmethod`, `ExitStack`, and context managers appropriately.
- Recognize Composite, Bridge, and Flyweight designs and explain ports-and-adapters architecture.
- Compose cache, retry, timeout, authentication, rate-limit, tracing, and metrics wrappers while reasoning about order, error semantics, idempotency, and cache invalidation.
- Test adapters against deterministic fakes and recorded fixtures without live credentials.
- Identify when wrappers improve isolation and when they add needless indirection.

## 2. Prerequisites

This lesson builds on the roadmap's Module 1.8 topics (encapsulation, composition, inheritance, protocols, dependency inversion, and layered design), Module 1.11 (Python data model), Module 1.12 (delegation and decorators), and Modules 1.7/1.16 (testing, fakes, and test isolation). You should be comfortable defining functions and classes, raising exceptions, using type hints, and writing basic `pytest` tests.

The module roadmap places this lesson after Lesson 02 on creational patterns and before Lesson 04 on behavioural patterns. It is not intended to teach the entire public-API lesson or the later sans-I/O lesson; those topics are referenced only where they clarify structural design.

## 3. Structural-pattern mental model

A **design pattern** is a named response to a recurring design problem. Structural patterns focus on how components are connected, wrapped, or composed. They do not primarily decide *which object to create* (creational patterns) or *how responsibilities and algorithms vary over time* (behavioural patterns).

| Family | Main question | Examples |
|---|---|---|
| Creational | How should the required object be created? | Factory, Builder |
| Structural | How should objects be connected or presented? | Adapter, Facade, Proxy, Decorator |
| Behavioural | How should work or decisions flow between collaborators? | Strategy, Observer, Command |

A useful mental model is **boundary, entry point, and interception**:

- **Adapter:** translate across a boundary where two interfaces do not match.
- **Facade:** give a caller a smaller, more convenient entry point to a subsystem.
- **Object-wrapping Decorator:** preserve an object's interface while adding behaviour.
- **Proxy:** stand in for another object and control access to it.

These intents can overlap. A caching wrapper can be both a Decorator (it adds behaviour while preserving the interface) and a Proxy (it controls whether the underlying object is accessed). Name the intent that matters to the design, and document observable semantics.

## 4. Beginner patterns and examples

### 4.1 Adapter: translate an external interface into an owned contract

**Definition and mental model.** An Adapter converts one interface into another expected by its client. Think of a plug adapter: the device keeps its expected connector while the adapter translates to the socket available at the boundary.

**Why it exists.** Vendor SDKs differ in method names, argument shape, return types, and exception types. If domain logic depends directly on those details, a vendor migration spreads changes through the codebase. An adapter confines that translation to one boundary.

**Internal flow.** The application calls its own port; the adapter translates the call and arguments; the vendor client performs I/O; the adapter translates the response or exception back to application-owned types.

#### Before: vendor details leak into core code

```python
# Illustrative anti-pattern: the application knows a vendor's method and response shape.
def load_record(vendor_client: object, bucket: str, key: str) -> bytes:
    response = vendor_client.get_object(Bucket=bucket, Key=key)  # type: ignore[attr-defined]
    return response["Body"].read()
```

This is difficult to type-check and test without reproducing the vendor's API. A change to the SDK affects callers.

#### After: define a small port and adapt the vendor

```python
from typing import Protocol


class Reader(Protocol):
    def read(self, key: str) -> bytes: ...


class VendorObjectClient(Protocol):
    def get_object(self, *, Bucket: str, Key: str) -> dict[str, object]: ...


class StorageAdapter:
    """Translate a vendor-shaped object client into the Reader contract."""

    def __init__(self, client: VendorObjectClient, bucket: str) -> None:
        self._client = client
        self._bucket = bucket

    def read(self, key: str) -> bytes:
        response = self._client.get_object(Bucket=self._bucket, Key=key)
        body = response["Body"]
        read_method = getattr(body, "read", None)
        if not callable(read_method):
            raise TypeError("vendor response Body must provide read()")
        data = read_method()
        if not isinstance(data, bytes):
            raise TypeError("vendor response Body.read() must return bytes")
        return data


class FakeBody:
    def __init__(self, data: bytes) -> None:
        self._data = data

    def read(self) -> bytes:
        return self._data


class FakeVendorClient:
    def __init__(self, objects: dict[str, bytes]) -> None:
        self.objects = objects
        self.calls: list[tuple[str, str]] = []

    def get_object(self, *, Bucket: str, Key: str) -> dict[str, object]:
        self.calls.append((Bucket, Key))
        return {"Body": FakeBody(self.objects[Key])}


vendor = FakeVendorClient({"reports/today.csv": b"id,total\n1,42\n"})
reader: Reader = StorageAdapter(vendor, bucket="analytics")
print(reader.read("reports/today.csv").decode().splitlines()[0])
print(vendor.calls)
```

Expected output:

```text
id,total
[('analytics', 'reports/today.csv')]
```

**Use it when:** integrating a third-party SDK, database driver, object store, HTTP transport, or LLM provider whose interface should not become your domain interface.

**Avoid it when:** the external interface already matches the small contract and adding a wrapper would merely rename every method without adding translation, validation, or isolation.

**Trade-offs and failure modes:** the adapter adds a class and a boundary to test. It can leak vendor exceptions or vendor-specific response objects unless it translates them deliberately. Avoid pretending to support capabilities that the vendor does not provide. Use a focused `Reader` or `Writer` protocol when a consumer needs only one capability; do not force read-only clients to implement writes.

**Simplest alternative:** call the vendor directly in a small script. That is acceptable for a one-off script; a reusable library benefits from an owned contract once multiple callers or tests depend on it.

**Testing strategy:** test the adapter against a fake with the vendor-shaped API, including missing fields, wrong body types, vendor exceptions, and argument translation. Add contract tests for every adapter so each implementation satisfies the same application-owned expectations.

**Exercise.** Add a `Writer` protocol and a fake vendor `put_object` method. Verify that `StorageAdapter`-style translation passes the correct bucket, key, and bytes. Expected outcome: domain-facing code never needs to know the vendor's keyword names.

### 4.2 Facade: simplify a subsystem's public entry point

**Definition and mental model.** A Facade provides a small, coherent API over a subsystem with multiple collaborators. It hides orchestration, not necessarily every capability.

**Why it exists.** A fetch may require URL validation, transport invocation, status handling, retries, parsing, and output selection. Making every caller orchestrate those steps creates duplication and exposes internal sequencing as a de facto API.

**Internal flow.** A caller invokes one facade method; the facade coordinates internal collaborators in the required order and returns a stable result or raises a documented application exception.

```python
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Document:
    url: str
    text: str


class HttpSource(Protocol):
    def get(self, url: str) -> bytes: ...


class Parser(Protocol):
    def parse(self, url: str, body: bytes) -> Document: ...


class TextParser:
    def parse(self, url: str, body: bytes) -> Document:
        return Document(url=url, text=body.decode("utf-8"))


class Fetcher:
    """Facade over transport and parsing; dependencies are injected."""

    def __init__(self, source: HttpSource, parser: Parser) -> None:
        self._source = source
        self._parser = parser

    def fetch(self, url: str) -> Document:
        if not url.startswith(("http://", "https://")):
            raise ValueError("url must use http:// or https://")
        body = self._source.get(url)
        return self._parser.parse(url, body)


class StaticSource:
    def get(self, url: str) -> bytes:
        return b"rows=3"


fetcher = Fetcher(StaticSource(), TextParser())
print(fetcher.fetch("https://data.example.test/items").text)
```

Expected output: `rows=3`.

**Use it when:** callers need one stable operation and should not coordinate internal modules. A facade is especially useful at a package boundary, e.g. `fetchkit.fetch(url)`.

**Avoid it when:** it becomes a god object that exposes every internal option or accumulates unrelated responsibilities. A facade should coordinate; specialized collaborators should still own transport, parsing, cache, and policy behaviour.

**Trade-offs:** callers gain simplicity, but advanced callers may need an explicit escape hatch to configure dependencies. Document defaults and supported customization rather than forwarding every internal parameter. Test the facade's orchestration and error contract with fake collaborators.

**Simplest alternative:** call the components directly. Prefer that inside well-defined internal workflows where a facade would add no meaningful boundary.

**Exercise.** Add a parser that returns the number of rows and expose `Fetcher.count_rows(url)`. Decide whether this belongs in the facade or a parser. Expected outcome: justify the decision using responsibility and API stability, not pattern terminology alone.

### 4.3 Object-wrapping Decorator versus Python function decorator

The word *decorator* describes two related but distinct mechanisms.

- An **object-wrapping Decorator** implements the same protocol as the wrapped object and delegates calls while adding behaviour. It is a structural GoF pattern.
- A **Python function decorator** is a callable that receives a function (or other callable) and returns a replacement callable, often using `@decorator` syntax. It may implement Decorator-like behaviour, but it can also register, validate, or transform functions.

```python
from typing import Protocol


class ByteSource(Protocol):
    def get(self, key: str) -> bytes: ...


class MemorySource:
    def get(self, key: str) -> bytes:
        return key.encode("utf-8")


class PrefixingSource:
    """Object decorator: same interface, added behaviour."""

    def __init__(self, inner: ByteSource, prefix: bytes) -> None:
        self._inner = inner
        self._prefix = prefix

    def get(self, key: str) -> bytes:
        return self._prefix + self._inner.get(key)


source: ByteSource = PrefixingSource(MemorySource(), b"cached:")
print(source.get("item"))
```

Expected output: `b'cached:item'`.

Function-decorator example:

```python
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def announce(fn: Callable[P, R]) -> Callable[P, R]:
    @wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"calling {fn.__name__}")
        return fn(*args, **kwargs)
    return wrapper


@announce
def double(value: int) -> int:
    return value * 2

print(double(4))
```

Expected output:

```text
calling double
8
```

`ParamSpec` helps preserve the callable's parameter types for static type checkers; `@wraps` preserves metadata such as the name and docstring. Runtime introspection and exact signature preservation still require care.

**Use object decorators** when you need a composable object implementing a protocol, such as `CachingFetcher(inner)`. **Use function decorators** for cross-cutting callable behaviour such as logging, registration, or timing. Avoid either when a direct function call or explicit helper is clearer.

**Failure modes:** dropping exceptions, changing return types, hiding method signatures, forgetting `@wraps`, or adding wrappers whose only purpose is to rename a call. Test both normal results and exceptional paths.

**Exercise.** Add a function decorator that logs elapsed time using an injected clock. Expected outcome: the wrapped function's return value and exceptions remain unchanged, and tests use a deterministic fake clock.

### 4.4 Proxy: control access to a subject

**Definition and mental model.** A Proxy presents an interface compatible with a subject and controls access to it. It may defer expensive initialization, cache results, check authorization, or forward calls to a remote resource.

**Internal flow.** The caller uses the proxy; the proxy checks a policy or state; it either returns a local result, initializes/contacts the subject, rejects the call, or forwards the operation.

```python
from collections.abc import Callable
from typing import Protocol


class Dataset(Protocol):
    def row_count(self) -> int: ...


class ExpensiveDataset:
    def __init__(self, rows: list[dict[str, str]]) -> None:
        print("loading dataset")
        self._rows = rows

    def row_count(self) -> int:
        return len(self._rows)


class LazyDatasetProxy:
    def __init__(self, loader: Callable[[], Dataset]) -> None:
        self._loader = loader
        self._subject: Dataset | None = None

    def _get_subject(self) -> Dataset:
        if self._subject is None:
            self._subject = self._loader()
        return self._subject

    def row_count(self) -> int:
        return self._get_subject().row_count()


proxy = LazyDatasetProxy(lambda: ExpensiveDataset([{"id": "1"}, {"id": "2"}]))
print("proxy created")
print(proxy.row_count())
print(proxy.row_count())
```

Expected output:

```text
proxy created
loading dataset
2
2
```

The loader is typed as `Callable[[], Dataset]`, making the deferred dependency explicit to readers and static type checkers. Lazy initialization must also define concurrency semantics: without a lock, simultaneous first calls can invoke the loader more than once. If loading has side effects or is expensive, guard initialization and decide how failures are cached or retried.

**Use it when:** access itself needs policy—lazy loading, authorization, remote calls, caching, or resource ownership. **Avoid it when:** direct dependency injection already provides the needed boundary and a proxy only conceals the real object.

**Trade-offs and failure modes:** transparent proxies are rarely fully transparent. `isinstance(proxy, ConcreteType)` may be false; object identity differs; equality/hash behavior may change; pickling may fail; introspection may expose proxy methods rather than subject methods. Prefer explicit protocol methods to broad `__getattr__` forwarding when the contract is small and important.

**Exercise.** Add a permission check that rejects access when `allowed` is false. Expected outcome: denied access never calls the subject; tests assert both the raised exception and zero underlying calls.

## 5. Intermediate structural techniques

### 5.1 Composite

**Intent:** treat individual objects and groups of objects through the same interface. A directory tree and a pipeline of transformations are common examples.

```python
from collections.abc import Iterable
from typing import Protocol


class Stage(Protocol):
    def run(self, value: str) -> str: ...


class StripStage:
    def run(self, value: str) -> str:
        return value.strip()


class UpperStage:
    def run(self, value: str) -> str:
        return value.upper()


class Pipeline:
    def __init__(self, stages: Iterable[Stage]) -> None:
        self._stages = tuple(stages)

    def run(self, value: str) -> str:
        for stage in self._stages:
            value = stage.run(value)
        return value


print(Pipeline([StripStage(), UpperStage()]).run("  hello  "))
```

Expected output: `HELLO`.

Use Composite when clients genuinely need to treat a leaf and a group uniformly. A simple list of functions may be enough for a small transformation chain. Deep recursive composites need cycle prevention, traversal rules, and clear failure semantics.

### 5.2 Bridge

**Intent:** separate two dimensions that should vary independently. For example, a `Report` abstraction can delegate rendering to an injected `Renderer`, allowing HTML and text renderers to evolve independently of report types.

```python
from typing import Protocol


class Renderer(Protocol):
    def render(self, title: str, body: str) -> str: ...


class TextRenderer:
    def render(self, title: str, body: str) -> str:
        return f"{title}\n{body}"


class HtmlRenderer:
    def render(self, title: str, body: str) -> str:
        return f"<h1>{title}</h1><p>{body}</p>"


class Report:
    def __init__(self, renderer: Renderer) -> None:
        self._renderer = renderer

    def render(self, title: str, body: str) -> str:
        return self._renderer.render(title, body)


print(Report(TextRenderer()).render("Daily", "3 rows"))
```

Expected output:

```text
Daily
3 rows
```

Bridge is useful when two independent variation axes would otherwise produce a class-per-combination hierarchy. For one renderer and one report type, direct composition may be simpler.

### 5.3 Flyweight

**Intent:** share intrinsic, immutable state across many logical objects to reduce memory usage. A common pattern is a cached factory for immutable configuration or metadata, not sharing mutable per-request state.

```python
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True, slots=True)
class ColumnSpec:
    name: str
    kind: str


@lru_cache(maxsize=128)
def column_spec(name: str, kind: str) -> ColumnSpec:
    return ColumnSpec(name, kind)


first = column_spec("id", "integer")
second = column_spec("id", "integer")
print(first is second)
```

Expected output: `True`.

This example intentionally caches immutable values. The cache retains references until eviction or clearing; unbounded caches can grow without limit. `slots=True` can reduce per-instance overhead, but it is not by itself the Flyweight pattern. Measure memory before introducing sharing, and never accidentally share mutable request-specific state.

### 5.4 Delegation helpers

#### `__getattr__`

`__getattr__` runs only when ordinary attribute lookup fails. It can forward unknown attributes to an inner object:

```python
class LoggingProxy:
    def __init__(self, inner: object) -> None:
        self._inner = inner

    def __getattr__(self, name: str) -> object:
        print(f"forwarding {name}")
        return getattr(self._inner, name)
```

This is convenient but weakens discoverability and typing, and can hide misspellings. It does not automatically preserve special-method behavior such as iteration or context management, because Python looks up many special methods on the type rather than through ordinary instance attribute access. Prefer explicit delegation for public contracts.

#### `functools.singledispatchmethod`

Use `singledispatchmethod` when method behavior should dispatch on the runtime type of the first non-`self` argument. It is a type-directed dispatch tool, not a universal substitute for adapters or a plugin registry.

```python
from functools import singledispatchmethod


class SizeOf:
    @singledispatchmethod
    def size(self, value: object) -> int:
        raise TypeError(f"unsupported type: {type(value).__name__}")

    @size.register
    def _(self, value: bytes) -> int:
        return len(value)

    @size.register
    def _(self, value: str) -> int:
        return len(value.encode("utf-8"))


print(SizeOf().size("é"))  # UTF-8 uses two bytes for this character.
```

Expected output: `2`.

Use it for a stable set of type-specific operations. If the variation is a business policy or runtime configuration, an explicit strategy object may be clearer.

#### `ExitStack` and context-managed wrappers

`contextlib.ExitStack` composes a variable number of context managers and cleanup callbacks. It is useful when a pipeline acquires resources conditionally or dynamically.

```python
from contextlib import ExitStack
from pathlib import Path


def read_first_lines(paths: list[Path]) -> list[str]:
    with ExitStack() as stack:
        files = [stack.enter_context(path.open(encoding="utf-8")) for path in paths]
        return [file.readline().rstrip("\n") for file in files]
```

This function assumes the paths exist and are readable; production code should handle or propagate `OSError` according to its contract. The key guarantee is that already-opened files are closed if a later open fails. A wrapper around a resource should explicitly implement `__enter__`/`__exit__` or use `contextmanager`; do not assume `__getattr__` forwards context-manager semantics.

### 5.5 Ports-and-adapters (hexagonal architecture)

Ports-and-adapters is an **architectural pattern**, not one GoF pattern. The application core defines ports—small interfaces describing required capabilities—and infrastructure adapters implement those ports for HTTP, databases, filesystems, storage, or LLM vendors.

```text
Caller / CLI / service
        |
        v
  Fetcher facade (application workflow)
        |
  +-----+-------+
  |             |
HTTP port    Parser port
  |             |
HTTP adapter  parser implementation
  |
Vendor SDK / HTTP transport
```

The dependency direction is intentional: core logic depends on application-owned contracts; infrastructure implements them. This supports tests, provider migrations, and reuse across environments. It does not mean every class needs a protocol. Create a port where it marks a real boundary or enables a useful substitution.

### 5.6 Layered facades and interface segregation

A public facade can expose `fetchkit.fetch(url)` while internal modules own transport, parsing, caching, and policy. Keep the facade small: a stable entry point should not expose every internal knob. Provide explicit configuration or dependency injection for advanced use cases.

Prefer small protocols when consumers need different capabilities:

```python
from typing import Protocol


class Reader(Protocol):
    def read(self, key: str) -> bytes: ...


class Writer(Protocol):
    def write(self, key: str, data: bytes) -> None: ...
```

A read-only component can depend on `Reader` without receiving write capability. This improves substitution and reduces accidental coupling. If a consumer truly needs both operations, it may accept both ports or a combined protocol.

### 5.7 Application examples beyond fetchkit

- **LLM provider adapter:** translate an application-owned `CompletionProvider.complete(prompt, options)` contract to one vendor's request/response schema, translating vendor rate-limit and authentication errors into application exceptions. A second provider adapter should pass the same contract tests. No live credentials are needed to test the translation.
- **Lazy dataset proxy:** defer loading a large dataset until first access. Define thread-safety, retry-after-load-failure, and close semantics explicitly.
- **Memory-mapped array proxy:** expose a small dataset interface while opening a memory map on demand. Ensure file handles are closed and that slices do not outlive the mapping unexpectedly.
- **Remote model client proxy:** forward calls to a remote inference service while enforcing timeouts, authentication, batching, and observability. The proxy is not a substitute for explicit network failure handling.

## 6. Advanced wrapper and architecture design

### 6.1 Wrapper order changes semantics

Wrappers compose like nested function calls. The outer wrapper sees the operation first and receives the inner wrapper's result or exception.

```text
Cache(Retry(HTTP))  -> cache stores the final result after retry policy runs
Retry(Cache(HTTP))  -> retry sees the cache's result; cached transient failures can defeat retry
```

The second behavior is especially important if the cache stores HTTP responses regardless of status. A `503` response is a returned value, not an exception; if the cache stores it, an outer retry wrapper can repeatedly receive the same cached `503` without making another request. A safer default is usually **retry inside cache** for status-aware HTTP fetching: `Cache(Retry(HTTP))`, so only the final response is cached. Alternatively, make the cache store only successful results and document that policy.

Ordering depends on semantics, not naming:

- **Timeout:** place it around the operation whose total duration it must bound. Per-attempt timeout differs from an overall deadline across retries. Retrying can exceed an intended total deadline unless the policy tracks remaining time.
- **Authentication:** apply before the request reaches the transport; refresh-on-401 requires a carefully bounded retry and must not loop indefinitely.
- **Rate limiting:** decide whether the limiter counts logical operations or each network attempt. A limiter inside retry typically accounts for every attempt; outside retry it may account only once per logical operation.
- **Tracing/metrics:** place spans and counters at levels that match the metric definition—one logical fetch versus each transport attempt. Use correlation IDs to connect them.
- **Caching:** cache keys must include all response-affecting inputs, including relevant headers, parameters, tenant identity, and authorization scope. Never share private responses across tenants by using an underspecified key.
- **Idempotency:** retries can duplicate side effects. Prefer retrying safe/idempotent operations; for writes, use server-supported idempotency keys or another explicit deduplication mechanism.

Document wrapper order as part of the composition root and test it with fake clocks and fake clients.

### 6.2 Error semantics and anti-corruption layers

An adapter should translate foreign models and exceptions at the boundary. For example, a provider's `VendorRateLimitError` can become `TransientFetchError`; a malformed payload can become `InvalidResponseError`. Preserve the original exception as the cause using `raise DomainError(...) from exc` so diagnostics remain available.

Do not catch every `Exception` and convert it into one generic error. That hides programming errors and breaks callers' ability to distinguish transient failures, invalid input, and permanent failures. Define which errors pass through, which are translated, and which are retryable.

A Domain-Driven Design **anti-corruption layer** protects domain vocabulary from a foreign model. Translate vendor field names, enums, timestamps, and error codes into application-owned types. For evolving vendor schemas, use recorded fixtures and contract tests; avoid silently accepting unknown fields when they may indicate a breaking upstream change.

### 6.3 Transparent proxy limits and contract preservation

A wrapper that claims to implement a protocol should preserve the observable contract, not necessarily every implementation detail. Consider:

- **Signatures and typing:** explicit methods are easier to type-check. `ParamSpec` and `TypeVar` help generic function decorators; they do not automatically make arbitrary object proxies transparent.
- **Context managers:** explicitly implement or wrap `__enter__`/`__exit__`; for async resources use `__aenter__`/`__aexit__` or `asynccontextmanager`.
- **Sync versus async:** do not return a coroutine from an API advertised as synchronous. Build distinct sync/async wrappers or share only genuinely synchronous policy logic.
- **Identity and equality:** a proxy is not normally identical to its subject. Forwarding `__eq__` without consistent `__hash__` can violate hash-container expectations.
- **`isinstance` and introspection:** callers may see the proxy type, not the subject. Do not promise concrete-type identity unless you can actually preserve it.
- **Pickling:** the subject, loader, lock, and transport may not be serializable. Define serialization deliberately or reject it clearly.
- **Thread safety:** a shared cache needs synchronization or a documented concurrency contract. Avoid holding a global lock during slow network I/O; use per-key coordination if duplicate concurrent misses are costly.

### 6.4 Timeouts, retry budgets, and cancellation

A timeout policy should specify whether it enforces a timeout per transport attempt or an overall deadline. In this case study, `BaseFetcher` passes a finite, positive timeout to the injected HTTP client; that is a **transport-enforced per-attempt timeout**, not a generic wrapper that can safely interrupt arbitrary synchronous Python code. A thread timeout does not safely terminate a blocked call. For async code, use cancellation-aware primitives and ensure cleanup runs. If an overall deadline matters, the retry policy must track remaining time and pass a smaller timeout to each attempt. Retries should use bounded attempts, backoff, jitter, and a retryable-error/status policy. The case study retries only explicitly translated `TransportError` exceptions and configured HTTP statuses; arbitrary exceptions pass through. Do not retry validation failures or authentication failures indefinitely.

### 6.5 Performance and indirection

Each wrapper adds at least another call boundary and more state to understand. In most network-bound code this overhead is usually small relative to I/O, but tiny hot-loop operations may be sensitive. More important costs often include cache memory, lock contention, extra network attempts, stale data, and debugging complexity. Benchmark representative workloads before removing a clear boundary. Prefer three comprehensible wrappers over one large object with hidden branches—but do not stack wrappers without a reason.

## 7. Pattern comparison table

| Pattern | Primary intent | Typical Python form | Distinguishing question | Main risk |
|---|---|---|---|---|
| Adapter | Translate interface/data/errors | Small class implementing an owned `Protocol` | “How do I make this external component fit my contract?” | Vendor details leak through |
| Facade | Simplify subsystem use | `Fetcher.fetch()` coordinating collaborators | “What is the one operation most callers need?” | God facade with too many options |
| Object Decorator | Add behaviour while preserving interface | `CachingFetcher(inner)` | “How can I add a capability compositionally?” | Contract/signature drift |
| Proxy | Control access to a subject | Lazy/cache/auth/remote stand-in | “Should access be deferred, checked, or forwarded?” | Broken identity or hidden behavior |
| Composite | Treat leaves and groups uniformly | Pipeline or tree implementing same protocol | “Should a group be usable where one component is expected?” | Deep trees/cycles/opaque failures |
| Bridge | Vary abstraction and implementation independently | `Report(renderer)` | “Would two variation axes multiply subclasses?” | Overdesign when only one axis varies |
| Flyweight | Share intrinsic immutable state | Cached immutable value factory | “Can repeated immutable data be shared safely?” | Memory retention or shared mutable state |

An implementation may satisfy more than one row. Classify by the problem it solves and the contract it promises.

## 8. `fetchkit` case-study implementation and tests

This section combines the lesson's ideas into one deterministic, runnable module. It uses a response object so retry logic can inspect HTTP status codes. The cache stores returned responses, including error statuses; this intentionally makes wrapper order observable.

### 8.1 Complete runnable implementation

Save the following as `fetchkit_structural.py`:

```python
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from math import isfinite
from typing import Protocol
from urllib.parse import urlsplit


class FetchError(Exception):
    """Base exception exposed by fetchkit."""


class TransportError(FetchError):
    """A known transport failure that the retry policy may retry."""


class InvalidResponseError(FetchError):
    """The external response could not be translated to fetchkit's contract."""


@dataclass(frozen=True, slots=True)
class HttpResponse:
    status: int
    body: bytes


class HttpClient(Protocol):
    def get(self, url: str, *, timeout_seconds: float) -> HttpResponse: ...


class VendorHttpClient(Protocol):
    def request(self, method: str, url: str, *, timeout: float) -> object: ...


class HttpClientAdapter:
    """Translate a vendor-shaped request API into fetchkit's HTTP port."""

    def __init__(self, vendor: VendorHttpClient) -> None:
        self._vendor = vendor

    def get(self, url: str, *, timeout_seconds: float) -> HttpResponse:
        # Translate only the transport failure types this adapter explicitly owns.
        # Do not catch TypeError around the call: that could hide a vendor bug.
        try:
            raw = self._vendor.request("GET", url, timeout=timeout_seconds)
        except OSError as exc:
            raise TransportError("vendor transport failed") from exc

        try:
            status = getattr(raw, "status_code")
            body = getattr(raw, "content")
        except AttributeError as exc:
            raise InvalidResponseError("vendor response lacks status_code/content") from exc
        # bool is an int subclass, but it is not a valid HTTP status code.
        if type(status) is not int or not 100 <= status <= 599 or not isinstance(body, bytes):
            raise InvalidResponseError("vendor response has invalid status or content type")
        return HttpResponse(status=status, body=body)


class FetchTransport(Protocol):
    def get(self, url: str) -> HttpResponse: ...


class BaseFetcher:
    """Small transport facade: validates URL and calls the injected HTTP port."""

    def __init__(self, client: HttpClient, *, timeout_seconds: float = 3.0) -> None:
        if not isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be finite and positive")
        self._client = client
        self._timeout_seconds = timeout_seconds

    def get(self, url: str) -> HttpResponse:
        try:
            parsed = urlsplit(url)
        except ValueError as exc:
            raise ValueError("url must be a valid absolute HTTP(S) URL") from exc
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or any(character.isspace() for character in parsed.netloc)
        ):
            raise ValueError("url must be a valid absolute HTTP(S) URL")
        return self._client.get(url, timeout_seconds=self._timeout_seconds)


class RetryFetcher:
    """Retry configured status responses and translated TransportError only."""

    def __init__(
        self,
        inner: FetchTransport,
        *,
        attempts: int = 3,
        retryable_statuses: frozenset[int] = frozenset({429, 500, 502, 503, 504}),
        sleep: Callable[[float], None] = lambda _seconds: None,
    ) -> None:
        if attempts < 1:
            raise ValueError("attempts must be at least 1")
        self._inner = inner
        self._attempts = attempts
        self._retryable_statuses = retryable_statuses
        self._sleep = sleep

    def get(self, url: str) -> HttpResponse:
        for attempt in range(1, self._attempts + 1):
            try:
                response = self._inner.get(url)
            except TransportError:
                if attempt == self._attempts:
                    raise
                self._sleep(0.1 * attempt)
                continue
            if response.status not in self._retryable_statuses:
                return response
            if attempt < self._attempts:
                self._sleep(0.1 * attempt)
        return response


class CachingFetcher:
    """Cache responses by URL, including status responses, for demonstration."""

    def __init__(self, inner: FetchTransport) -> None:
        self._inner = inner
        self._cache: dict[str, HttpResponse] = {}

    def get(self, url: str) -> HttpResponse:
        if url not in self._cache:
            self._cache[url] = self._inner.get(url)
        return self._cache[url]

    def invalidate(self, url: str | None = None) -> None:
        if url is None:
            self._cache.clear()
        else:
            self._cache.pop(url, None)


class FetcherFacade:
    """Public entry point for fetching and decoding successful text responses."""

    def __init__(self, transport: FetchTransport) -> None:
        self._transport = transport

    def fetch_text(self, url: str) -> str:
        response = self._transport.get(url)
        if not 200 <= response.status < 300:
            raise FetchError(f"HTTP status {response.status} for {url}")
        try:
            return response.body.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise InvalidResponseError("response body is not valid UTF-8") from exc


class FakeResponse:
    def __init__(self, status_code: int, content: bytes) -> None:
        self.status_code = status_code
        self.content = content


class FakeVendorClient:
    def __init__(self, responses: list[tuple[int, bytes]]) -> None:
        self._responses = list(responses)
        self.calls: list[tuple[str, str, float]] = []

    def request(self, method: str, url: str, *, timeout: float) -> FakeResponse:
        self.calls.append((method, url, timeout))
        if not self._responses:
            raise AssertionError("fake response queue exhausted")
        status, content = self._responses.pop(0)
        return FakeResponse(status, content)


def build_fetcher(vendor: VendorHttpClient) -> FetcherFacade:
    """Composition root: construct and order infrastructure wrappers here."""
    adapter = HttpClientAdapter(vendor)
    base = BaseFetcher(adapter, timeout_seconds=2.0)
    retrying = RetryFetcher(base, attempts=3)
    cached = CachingFetcher(retrying)  # cache only the final result after retries
    return FetcherFacade(cached)


if __name__ == "__main__":
    vendor = FakeVendorClient([(503, b"busy"), (200, b"ready")])
    fetcher = build_fetcher(vendor)
    print(fetcher.fetch_text("https://api.example.test/status"))
    print(len(vendor.calls))
```

Expected output:

```text
ready
2
```

The `build_fetcher` function is the **composition root**: it chooses concrete adapters and wrapper order. The facade's caller does not need to know how the vendor API works or how retries and caching are composed.

### 8.2 Why this composition order?

`CachingFetcher(RetryFetcher(BaseFetcher(...)))` caches the result after retry handling. A transient `503` is not cached as the final result if a later attempt succeeds. Compare that with `RetryFetcher(CachingFetcher(BaseFetcher(...)))`: because the cache returns the first `503` on every retry, the retry wrapper never reaches the underlying HTTP client again.

This sample deliberately caches all HTTP responses to make the failure mode visible. A production cache may instead cache only selected successful responses, respect `Cache-Control`, include headers/tenant identity in keys, and apply TTL/invalidation rules.

### 8.3 Tests

Save the following as `test_fetchkit_structural.py` next to the implementation and run `python -m pytest -q`:

```python
import pytest

from fetchkit_structural import (
    BaseFetcher,
    CachingFetcher,
    FetchError,
    FetcherFacade,
    HttpClientAdapter,
    InvalidResponseError,
    RetryFetcher,
    TransportError,
    FakeVendorClient,
    build_fetcher,
)


URL = "https://api.example.test/status"


def test_adapter_translates_vendor_response_and_arguments() -> None:
    vendor = FakeVendorClient([(200, b"ok")])
    adapter = HttpClientAdapter(vendor)
    response = adapter.get(URL, timeout_seconds=1.25)
    assert (response.status, response.body) == (200, b"ok")
    assert vendor.calls == [("GET", URL, 1.25)]




def test_adapter_translates_transport_failure_and_chains_cause() -> None:
    class BrokenVendor:
        def request(self, method: str, url: str, *, timeout: float) -> object:
            raise OSError("connection reset")

    with pytest.raises(TransportError, match="vendor transport failed") as exc_info:
        HttpClientAdapter(BrokenVendor()).get(URL, timeout_seconds=1.0)  # type: ignore[arg-type]
    assert isinstance(exc_info.value.__cause__, OSError)


def test_adapter_rejects_invalid_status_codes() -> None:
    class BadStatusVendor:
        def request(self, method: str, url: str, *, timeout: float) -> object:
            return type("Response", (), {"status_code": True, "content": b"not a valid status"})()

    with pytest.raises(InvalidResponseError, match="invalid status"):
        HttpClientAdapter(BadStatusVendor()).get(URL, timeout_seconds=1.0)  # type: ignore[arg-type]


def test_retry_retries_translated_transport_error_but_not_arbitrary_errors() -> None:
    class FlakyTransport:
        def __init__(self) -> None:
            self.calls = 0

        def get(self, url: str) -> object:
            self.calls += 1
            if self.calls == 1:
                raise TransportError("temporary transport failure")
            return type("Response", (), {"status": 200, "body": b"ok"})()

    flaky = FlakyTransport()
    response = RetryFetcher(flaky).get(URL)  # type: ignore[arg-type]
    assert (response.status, response.body) == (200, b"ok")
    assert flaky.calls == 2

    class ProgrammingErrorTransport:
        def get(self, url: str) -> object:
            raise TypeError("programming error")

    with pytest.raises(TypeError, match="programming error"):
        RetryFetcher(ProgrammingErrorTransport()).get(URL)  # type: ignore[arg-type]


def test_adapter_translates_malformed_vendor_response() -> None:
    class BadVendor:
        def request(self, method: str, url: str, *, timeout: float) -> object:
            return object()

    with pytest.raises(InvalidResponseError, match="lacks status_code/content"):
        HttpClientAdapter(BadVendor()).get(URL, timeout_seconds=1.0)  # type: ignore[arg-type]


def test_cache_avoids_second_transport_call_and_can_invalidate() -> None:
    vendor = FakeVendorClient([(200, b"one"), (200, b"two")])
    base = BaseFetcher(HttpClientAdapter(vendor))
    cache = CachingFetcher(base)
    assert cache.get(URL).body == b"one"
    assert cache.get(URL).body == b"one"
    assert len(vendor.calls) == 1
    cache.invalidate(URL)
    assert cache.get(URL).body == b"two"
    assert len(vendor.calls) == 2


def test_retry_inside_cache_retries_before_caching_final_response() -> None:
    vendor = FakeVendorClient([(503, b"busy"), (200, b"ready")])
    fetcher = build_fetcher(vendor)
    assert fetcher.fetch_text(URL) == "ready"
    assert len(vendor.calls) == 2
    assert fetcher.fetch_text(URL) == "ready"
    assert len(vendor.calls) == 2


def test_cache_inside_retry_can_cache_transient_status_and_defeat_retry() -> None:
    vendor = FakeVendorClient([(503, b"busy"), (200, b"ready")])
    base = BaseFetcher(HttpClientAdapter(vendor))
    wrong_order = RetryFetcher(CachingFetcher(base), attempts=3)
    response = wrong_order.get(URL)
    assert response.status == 503
    # All retries read the cached 503; the queued 200 is never requested.
    assert len(vendor.calls) == 1


def test_facade_translates_non_success_status_to_domain_error() -> None:
    vendor = FakeVendorClient([(404, b"missing")])
    fetcher = FetcherFacade(BaseFetcher(HttpClientAdapter(vendor)))
    with pytest.raises(FetchError, match="HTTP status 404"):
        fetcher.fetch_text(URL)


def test_invalid_url_is_rejected_before_transport_call() -> None:
    vendor = FakeVendorClient([(200, b"unused")])
    fetcher = FetcherFacade(BaseFetcher(HttpClientAdapter(vendor)))
    for invalid_url in ("file:///etc/passwd", "https://", "https://bad host/path"):
        with pytest.raises(ValueError, match=r"valid absolute HTTP\(S\) URL"):
            fetcher.fetch_text(invalid_url)
    assert vendor.calls == []


def test_timeout_must_be_positive() -> None:
    vendor = FakeVendorClient([(200, b"unused")])
    for invalid_timeout in (0, -1, float("inf"), float("nan")):
        with pytest.raises(ValueError, match="timeout_seconds must be finite and positive"):
            BaseFetcher(HttpClientAdapter(vendor), timeout_seconds=invalid_timeout)


def test_retry_attempt_count_must_be_positive() -> None:
    vendor = FakeVendorClient([(200, b"unused")])
    base = BaseFetcher(HttpClientAdapter(vendor))
    with pytest.raises(ValueError, match="attempts must be at least 1"):
        RetryFetcher(base, attempts=0)


def test_invalid_utf8_is_translated_and_chained() -> None:
    vendor = FakeVendorClient([(200, b"\xff")])
    fetcher = FetcherFacade(BaseFetcher(HttpClientAdapter(vendor)))
    with pytest.raises(InvalidResponseError, match="not valid UTF-8") as exc_info:
        fetcher.fetch_text(URL)
    assert isinstance(exc_info.value.__cause__, UnicodeDecodeError)
```

The tests cover interface translation, translated transport failures and exception chaining, malformed vendor responses, cache hits and invalidation, wrapper-order semantics, HTTP error handling, invalid URL and timeout boundaries, retry configuration, and the rule that arbitrary programming errors are not retried. The fake is deterministic and does not require a network connection or credentials.

**Important production caveats:** this teaching implementation intentionally omits jitter, a total retry deadline, status-aware cache policy, TTL, cache-key variation, synchronization, cancellation, and telemetry. Those omissions are explicit scope boundaries—not recommendations to omit them in a production client. `FakeVendorClient` raises when its queue is exhausted so unexpected calls fail loudly instead of returning fabricated data.

## 9. Hands-on exercises

### Exercise 1 — Two storage adapters

Define an application-owned `Reader` protocol. Implement a local filesystem adapter and a vendor-shaped object-storage adapter. Write one parameterized contract test suite that checks the same read behavior for both. Include missing-key semantics and decide whether each adapter translates a vendor exception or lets a documented standard exception pass through.

**Expected outcome:** consumers depend only on `Reader`; each adapter owns its translation rules; tests do not require credentials.

### Exercise 2 — Add a `RateLimitedFetcher`

Wrap `FetchTransport` with a rate limiter that receives an injected clock/sleep function. Test that each actual network attempt consumes a permit. Compare `RateLimitedFetcher(RetryFetcher(base))` with `RetryFetcher(RateLimitedFetcher(base))` and state whether the limiter counts logical fetches or attempts.

**Expected outcome:** deterministic tests demonstrate the chosen accounting semantics without real delays.

### Exercise 3 — Cache policy and invalidation

Change the cache to cache only 2xx responses. Add an explicit invalidation method and, optionally, a TTL. Test that a `503` is not cached, that a successful result is cached, and that invalidation causes a fresh call. If cache keys can vary by tenant or headers, demonstrate how the key includes those dimensions.

**Expected outcome:** failure responses do not poison the cache; invalidation and key semantics are explicit.

### Exercise 4 — LLM provider anti-corruption layer

Define a `CompletionProvider` protocol that accepts a prompt and returns an application-owned immutable result. Implement two deterministic fake vendor adapters with different request and response field names. Translate rate-limit and malformed-response exceptions. Run the same contract tests against both adapters.

**Expected outcome:** domain code uses one contract, vendor schemas remain at the edge, and no live API key is needed.

### Exercise 5 — Proxy or direct dependency?

Consider a large dataset loaded from a memory-mapped file. Propose a lazy proxy, specify when it opens the mapping, how it closes it, what happens if initialization fails, and whether concurrent first access may load twice. Then compare the proxy with explicit dependency injection of a dataset loader.

**Expected outcome:** your decision accounts for resource lifetime and concurrency, not just a desire to use a pattern.

## 10. Common mistakes and troubleshooting

1. **Depending directly on vendor SDK types throughout the application.** Keep vendor-specific names, response objects, and exception codes inside adapters. Translate to owned types at the boundary.
2. **Facades exposing every internal option.** A facade should simplify common use. Put advanced dependency wiring in an explicit configuration/composition root rather than forwarding every internal parameter.
3. **Wrapping without preserving error semantics.** Decide which exceptions are translated, which are retryable, and which pass through. Chain translated exceptions with `raise ... from exc`.
4. **Confusing an Adapter with a Facade.** Adapter changes interface; Facade simplifies a subsystem. One adapter can be used by a facade, but the intents are different.
5. **Calling every wrapper a Proxy.** Decorator adds behaviour while preserving the interface; Proxy controls access. A concrete wrapper can be both—explain which property matters.
6. **Retrying cached transient responses.** If a cache stores `503`, an outer retry wrapper may repeatedly read the same cached response. Put retry inside cache or cache only appropriate successful responses.
7. **Ignoring cache invalidation and key correctness.** Stale data, cross-tenant leakage, or ignoring response-affecting headers can become correctness or security defects.
8. **Using `__getattr__` as a universal transparency mechanism.** Special methods, typing, identity, introspection, and pickling may not forward as expected. Prefer explicit methods for stable public contracts.
9. **Sharing mutable state in a Flyweight.** Share immutable intrinsic state, not per-request mutable data. Bound caches and monitor retention.
10. **Treating wrappers as free.** Each layer adds control flow and potential failure modes. Keep a written order, test the composition, and measure hot paths before optimizing.
11. **Confusing timeout with retry budget.** A timeout per attempt does not guarantee a bounded total operation. Use an overall deadline or budget when required.
12. **Retrofitting async semantics into sync wrappers.** Sync and async contracts differ in cancellation and resource management. Use a clear separate API or carefully factored common policy logic.

When debugging a wrapper chain, inspect the concrete composition order, log each logical operation and each attempt separately, preserve exception causes, and test each wrapper in isolation before testing the full chain.

## 11. Self-check questions with model answers

### 1. How does an adapter differ from a facade? From a proxy?

**Model answer:** An Adapter translates one interface or data/error model into another interface expected by its client. A Facade offers a simpler entry point over several subsystem components and coordinates them. A Proxy stands in for a subject and controls access—for example, by lazy initialization, caching, authorization, or remote forwarding. All may use composition, so classify by intent and observable contract rather than class shape.

### 2. Compose retry, cache, and timeout wrappers; argue for an order and test it.

**Model answer:** For status-aware HTTP reads, a defensible arrangement is `Cache(Retry(TransportWithPerAttemptTimeout))`: the transport enforces a timeout on each attempt, retry handles retryable outcomes, and cache stores the final result. This lesson's `BaseFetcher` configures the timeout at the transport boundary rather than pretending a generic synchronous wrapper can forcibly stop arbitrary code. If an overall deadline matters, the retry policy must also track the remaining budget; per-attempt timeouts alone can exceed the desired total duration. A cache that stores `503` responses should not sit inside a retry wrapper, because retries can repeatedly receive the cached failure. Tests should queue `503` then `200`, assert two transport calls and a final `200`, then assert a subsequent cache hit adds no call. Also test cache invalidation, non-retryable statuses, and deadline exhaustion.

### 3. Define a `Protocol` for LLM completion providers and write two adapters with contract tests.

**Model answer:** Define a small contract such as `complete(prompt: str, *, max_tokens: int) -> Completion`, where `Completion` is an application-owned frozen dataclass. Implement `ProviderAAdapter` and `ProviderBAdapter` that map each vendor's request fields, parse its response, and translate rate-limit or malformed-response errors. A shared contract suite checks successful completion shape, empty/malformed responses, and error translation for both adapters. Fakes or recorded fixtures make the suite deterministic and credential-free. The lesson's Exercise 4 is the implementation task.

## 12. Summary and completion checklist

Structural patterns help isolate incompatible interfaces, simplify subsystem use, control access, and compose independent capabilities. Their value comes from a real boundary or recurring design pain—not from adding classes by default.

- [ ] I can explain the difference between creational, structural, and behavioural patterns.
- [ ] I can distinguish Adapter, Facade, object Decorator, and Proxy by intent.
- [ ] I can define small application-owned `Protocol` contracts and implement adapters.
- [ ] I can explain Composite, Bridge, and Flyweight, including when simpler composition is enough.
- [ ] I understand the limits of `__getattr__`, `singledispatchmethod`, and context-manager delegation.
- [ ] I can explain ports-and-adapters and keep vendor details at infrastructure boundaries.
- [ ] I can justify wrapper order and test its effect on retries, cache results, and rate limits.
- [ ] I can preserve exception causes and define cache invalidation and concurrency behavior.
- [ ] I can identify when a proxy or wrapper creates more complexity than value.
- [ ] I completed the fetchkit tests and at least one hands-on exercise.

## 13. Authoritative references

The following references support the language and library mechanics used in this lesson. Pattern choices and the `fetchkit` design are teaching examples aligned to the supplied Module 1.20 roadmap.

- Python typing — `Protocol`: <https://docs.python.org/3/library/typing.html#typing.Protocol>
- Python typing — callable annotations, `ParamSpec`, and generics: <https://docs.python.org/3/library/typing.html>
- Python `functools` — `singledispatchmethod`, `wraps`, and `lru_cache`: <https://docs.python.org/3/library/functools.html>
- Python `contextlib` — `ExitStack`, `contextmanager`, and async context managers: <https://docs.python.org/3/library/contextlib.html>
- Python data model — attribute access and special method lookup: <https://docs.python.org/3/reference/datamodel.html>
- pytest documentation — assertions and parametrization: <https://docs.pytest.org/en/stable/how-to/assert.html> and <https://docs.pytest.org/en/stable/how-to/parametrize.html>
- Martin Fowler, “Gateway” and related enterprise application patterns: <https://martinfowler.com/eaaCatalog/>
- Alistair Cockburn, “Hexagonal Architecture”: <https://alistair.cockburn.us/hexagonal-architecture/>
- Source syllabus: `roadmap-Design-Patterns-and-Library-API-Design.md`, Lesson 03; project placement: `Roadmap_ptree.md`, Stage 1, Module 20.
