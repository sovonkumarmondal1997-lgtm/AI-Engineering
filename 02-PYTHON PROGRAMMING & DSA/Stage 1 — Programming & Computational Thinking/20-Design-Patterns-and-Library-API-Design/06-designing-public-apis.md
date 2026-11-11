# Lesson 06 — Designing Public APIs

> **Audience:** Python developers moving from internal code to libraries other people import.  
> **Baseline:** Python 3.12+, with strict static checking for new public code.  
> **Running case study:** `fetchkit`, a small, synchronous data-fetching library whose public contract should survive internal refactors.

## 1. Objectives and prerequisites

By the end of this lesson, you should be able to:

- distinguish a documented public contract from an implementation detail and reduce accidental API surface;
- design a predictable package layout, exports, names, signatures, types, exceptions, and documentation;
- make invalid inputs harder to express without making ordinary use verbose;
- plan extension points and result/configuration types that can evolve;
- test the API as an external user would, including public imports and runnable documentation;
- evaluate stability, compatibility, discoverability, performance, and ownership promises before release.

### Prerequisites and roadmap placement

This is Module 1.20, Lesson 06 in Stage 1 — Programming & Computational Thinking. The module tree places it after Pythonic patterns, creational patterns, structural patterns, behavioural patterns, and plugin/registry patterns; it precedes backward compatibility and deprecation policy, library error hierarchies, sans-I/O design, and anti-pattern refactoring. That order matters: a public API is where earlier design choices become contracts.

The roadmap assumes familiarity with encapsulation, composition, `Protocol`, dependency inversion, Python's data model, decorators and registries, modern signatures and errors, packaging/versioning, and tests. Use Python 3.12+ and run `mypy --strict` or strict Pyright against public code and examples. Tools such as `ruff`, `pytest`, `griffe`, `import-linter`, Sphinx, and MkDocs support the workflow; they are tools, not Python language guarantees.

## 2. Public API mental model

An API is the set of names, operations, inputs, outputs, errors, and behavioural promises through which one component is used by another. A Python library's public API includes more than its functions: signatures, default values, exceptions, result shapes, import paths, resource ownership, sync/async behaviour, ordering, and sometimes timing or error wording all shape user expectations.

**The public API is the product users depend on.** Internal code can be refactored freely only to the extent that observable behaviour stays within the promised contract. Users may rely on undocumented details too (Hyrum's law: with enough users, every observable behaviour will be depended on by someone). Documentation and explicit exports reduce ambiguity, but cannot prevent every dependency on implementation details.

### Public, private, and accidentally public

- A name without a leading underscore is conventionally public.
- A leading underscore (for example, `_parse_headers`) signals non-public/internal use by convention; Python does not enforce access control.
- `__all__` declares the names intended for `from module import *` and is useful as an explicit export list. It does **not** make other names inaccessible, stop `import package._internal`, or guarantee that tools/users cannot inspect internals.
- Documented names are the clearest intended contract. Undocumented public-looking names can still become de facto API.
- Keep internals in modules such as `_client.py` or `_internal/`; re-export stable names from the package root so users need not import implementation paths.
- `py.typed` (PEP 561) marks an installed package as providing inline type information. Include it in the distribution when applicable; annotations alone do not guarantee downstream type checkers will see them.

### What is part of the contract?

| Surface | Examples of contract decisions |
|---|---|
| Names/imports | `from fetchkit import fetch`, supported Python versions |
| Signatures | parameter names, requiredness, keyword-only options, defaults |
| Values | return types, units, ordering, mutability, laziness |
| Errors | exception classes and when they are raised |
| Side effects | logging, network activity, file writes, cleanup |
| Concurrency | thread safety, async safety, cancellation semantics |
| Performance | documented complexity, streaming vs buffering, import cost |
| Extension | callbacks, `Protocol`s, plugin registration and compatibility |
| Serialization | JSON/config schema versions, CLI output and exit codes |

Avoid promising incidental details. If iteration order, exact error text, or timing is not intended to be stable, say so and test only the actual contract.

## 3. Beginner principles

### 3.1 Package layout and the clean import surface

A small package might use:

```text
fetchkit/
    __init__.py       # supported imports and __all__
    _client.py        # implementation details
    _models.py        # internal model definitions, selectively re-exported
    _errors.py        # public exception hierarchy
    py.typed          # package marker for inline typing
```

Users should be able to write `from fetchkit import Fetcher, FetchResult, FetchError, fetch` without depending on `fetchkit._client`. The root module should be intentionally small: importing a library should not unexpectedly open sockets, scan directories, load every optional backend, or mutate global state. Re-exporting from `__init__.py` is a design choice; avoid circular imports by keeping dependency direction clear.

### 3.2 Names that explain intent

Use verbs for operations (`fetch`, `parse`, `write`), nouns for types (`Fetcher`, `FetchResult`), and one vocabulary throughout. Prefer `is_cached`, `has_content`, `timeout_seconds`, and `max_attempts` to ambiguous booleans or unexplained units. Include units in names or use a validated value type. Use singular names for one object and plural names for collections.

Avoid APIs like `fetch(url, True, False, 10)`: callers cannot tell what the flags mean. Prefer explicit keyword-only options or an enum:

```python
from enum import Enum


class CacheMode(Enum):
    OFF = "off"
    READ_THROUGH = "read_through"


class DemoClient:
    def get_before(self, url: str, use_cache: bool, verify_tls: bool, mode: str) -> str:
        return f"{url}: cache={use_cache}, tls={verify_tls}, mode={mode}"

    def fetch_after(
        self, url: str, *, timeout_seconds: float = 10.0,
        cache_mode: CacheMode = CacheMode.READ_THROUGH,
    ) -> str:
        return f"{url}: timeout={timeout_seconds}, cache={cache_mode.value}"


client = DemoClient()
print(client.get_before("https://example.test", True, False, "fast"))
print(client.fetch_after("https://example.test", timeout_seconds=10.0))
```

### 3.3 Required, optional, and keyword-only parameters

Put required parameters first. Give optional parameters defaults only when the default is meaningful and stable. Prefer keyword-only parameters for configuration that may grow:

```python
def fetch(url: str, *, timeout_seconds: float = 10.0) -> str:
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be greater than zero")
    # A deterministic stand-in for the transport call.
    return f"Would fetch {url!r} with a {timeout_seconds:g}-second timeout"


print(fetch("https://example.test"))
```

A boolean parameter is not automatically wrong. It becomes a *boolean trap* when the call site hides meaning, multiple flags create interacting modes, or the flag changes the operation's semantics. Replace semantic modes with separate functions or an enum when that improves clarity. Do not add a flag merely to avoid naming a second operation.

### 3.4 Types: accept abstractions, return useful values

Accept the least restrictive abstraction that expresses what you need: `Iterable[str]` when iterating once, `Mapping[str, str]` when reading key/value pairs, or a `Protocol` for a collaborator. Return a concrete, documented result model when callers benefit from stable named fields. This rule is a heuristic, not a prohibition on returning iterators, protocols, or abstractions when they are the natural contract.

Annotate every public parameter and return value. Avoid `Any` unless dynamic typing is genuinely part of the boundary. Use `Literal` for a small closed set, `Enum` when values have behaviour/identity, and validated value objects for nontrivial invariants. A type annotation does not validate runtime input by itself.

### 3.5 Docstrings, exceptions, and copyable examples

Document semantics, units, defaults, side effects, ownership, and expected errors—not just the parameter names. State which exception classes callers may catch. Library code should normally raise exceptions rather than print messages; applications decide how to display them. Do not expose a vendor's exception or response type unless that dependency is intentionally part of your public contract.

A good quick start is short, complete, and runnable. Treat documentation examples as tests (doctest or pytest). A sample that omits imports, assumes hidden state, or silently requires an optional dependency is not a reliable API example.

## 4. Intermediate usability and extension

### 4.1 Least astonishment and progressive disclosure

The ordinary case should be easy to express, while advanced cases remain possible. In this deliberately dependency-injected `fetchkit` example, the smallest valid call is `fetch(url, transport=...)` because the library does not create a hidden global client; a production package could offer a separate convenience API only if its transport ownership and lifecycle were explicit. Defaults should be unsurprising, documented, and stable. Advanced controls should not burden every beginner call. Do not change a default silently: a default affects every caller who omitted that argument and is therefore a behavioural contract.

### 4.2 Make invalid states difficult to represent

Use enums or `Literal` instead of arbitrary magic strings, validate invariants at construction boundaries, and prefer immutable result objects when mutation would be surprising. For example, a result should not permit a negative elapsed duration if that concept is meaningful in the domain. Do not over-model simple values: a custom `Url` class is useful only if it enforces semantics or adds meaningful operations.

```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class RetryPolicy:
    max_attempts: int = 3

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
```

### 4.3 Result objects, tuples, iterators, and pagination

A tuple is concise for a fixed, obvious pair; a named immutable result object is often better when fields need documentation or may evolve. A dataclass can gain a field with a default more safely than changing tuple arity, though compatibility still depends on how callers construct, compare, serialize, or pattern-match it.

Return a list when the result is naturally finite and reasonably sized. Return an iterator when streaming or laziness is part of the contract; document when errors occur and who owns the underlying resource. For large remote collections, define pagination explicitly: stable cursor semantics, page limits, ordering, and what happens when data changes between pages. Name synchronous and asynchronous APIs clearly (`fetch` and `afetch`, or a separate `fetchkit.aio` module); don't return a coroutine from a function whose name and docs imply synchronous completion.

### 4.4 Configuration objects and deliberate extension points

Once configuration has several related options, use a validated configuration object rather than a long list of positional flags. A builder is justified when construction has staged steps or invariants; it is not automatically superior to a dataclass. Avoid catch-all `**kwargs` unless the accepted keys are validated and documented.

Design callbacks and plugin interfaces as contracts. A `Protocol` can describe a structural collaborator without forcing inheritance. Define callback arguments, invocation timing, exception behaviour, concurrency, and ownership. A plugin registry should have explicit names, duplicate rules, and lifecycle semantics (Lesson 05); do not make a mutable process-global registry the default if independent clients/tests need different implementations.

### 4.5 Documentation and usability testing

Provide the right layers of documentation:

- **Quick start / README:** smallest complete useful task.
- **How-to guides:** solve a specific real-world problem.
- **Reference:** exact signatures, options, exceptions, and return values.
- **Explanation:** rationale, trade-offs, architecture, and constraints.
- **Examples:** larger end-to-end tasks that are executable and maintained.

Write the README before implementation. Try the example as a new user: are imports discoverable, defaults understandable, errors actionable, and configuration easy to express? Ask a teammate to use it without coaching and record friction. Type-check public examples using strict `mypy` or strict Pyright; a passing unit suite does not prove the public typing experience is good.

## 5. Advanced stability and governance

### 5.1 Hyrum's law and public-surface audits

Before release, inspect more than `__all__`: public-looking module attributes, documented import paths, return types, CLI output, exception classes, environment variables, loggers, ordering, serialization, and timing can all attract dependencies. Decide which behaviours are promised and test those. Don't lock every incidental detail into snapshots; snapshots are a signal for review, not an automatic command to preserve every accidental export forever.

Classify APIs as **stable**, **provisional**, or **experimental**. Put experimental features in a clear namespace such as `fetchkit.experimental`, document their status, and define a removal policy. Semantic versioning is a project/release policy whose meaning depends on the published compatibility promise; a major version is not a substitute for migration notes or deprecation discipline.

### 5.2 Design for future extension

- Prefer keyword-only extension parameters so future options do not change positional meaning.
- Use a typed configuration object when options form a coherent group; validate unknown keys rather than silently accepting typos.
- Prefer evolvable result models over positional tuples when fields may grow.
- Choose closed enums when the set is intentionally closed; use registries/protocols when third parties must extend it.
- Version wire formats and persisted configuration independently from Python class names. Do not assume a dataclass representation is a stable JSON schema.
- For deprecations, announce the replacement, emit an appropriate warning when feasible, provide a migration window, and test both old and new paths while supported.

### 5.3 One design, many interfaces

The same API principles apply across:

- **CLI:** stable flags, help text, exit codes, output formats, and stderr/stdout conventions.
- **Configuration files:** schema version, required keys, defaults, unknown-key policy, and useful line/key diagnostics.
- **REST/JSON:** explicit request/response schemas, status codes, idempotency, pagination, and versioning.
- **SDKs:** idiomatic names and types without leaking transport/vendor objects unintentionally.
- **Agent/tool schemas:** narrow argument schemas, explicit side effects, bounded output, and errors that support safe recovery. Tool descriptions are part of the contract.

Keep naming and semantics consistent across layers, but do not force every transport to share a shape that is awkward for its users.

### 5.4 Errors, observability, performance, and ownership

Document exception types and their boundaries. Logging is also observable: use a library-specific logger, avoid configuring the application's root logger, and do not print. Metrics names and labels can become operational contracts; avoid unbounded-cardinality labels such as raw URLs or user IDs.

State whether results are buffered or streamed, whether operations are thread-safe, whether async calls are cancellation-safe, and who closes sockets/files/iterators. Prefer explicit `close()` and context-manager protocols for owned resources. Do not claim thread safety simply because individual dictionary operations are atomic in a particular interpreter. Keep imports lightweight and defer optional dependencies until they are actually needed.

### 5.5 API review and governance

For a significant public change, write a short RFC: problem, target users, proposed call sites, alternatives, failure modes, typing, performance, compatibility, migration, documentation, and test plan. In CI, combine:

- public import tests and `__all__` snapshots;
- tests for documented behaviour and exceptions;
- strict type checking of package code and user-facing examples;
- an API diff tool such as `griffe` or equivalent;
- linting and dependency-boundary checks such as `import-linter` where useful.

API snapshots should be reviewed intentionally. A diff tells you that a surface changed; it does not tell you whether the change is wrong. Discoverability also matters: `help(fetchkit.fetch)`, IDE completion, a short root namespace, useful errors, and fast imports all improve the first-use experience.

## 6. Before-and-after API examples

### Example A — positional booleans and magic strings

```python
from enum import Enum


class CacheMode(Enum):
    OFF = "off"
    READ_THROUGH = "read_through"


class Client:
    def get_before(self, url: str, use_cache: bool, verify_tls: bool, mode: str) -> str:
        return f"{url}: cache={use_cache}, tls={verify_tls}, mode={mode}"

    def fetch_after(
        self, url: str, *, timeout_seconds: float = 10.0,
        cache_mode: CacheMode = CacheMode.READ_THROUGH,
    ) -> str:
        return f"{url}: timeout={timeout_seconds}, cache={cache_mode.value}"


client = Client()
print(client.get_before("https://example.test", True, False, "fast"))
print(client.fetch_after("https://example.test", timeout_seconds=5.0))
```

Use `Enum` if these values form a named domain. A `Literal["off", "read", "read_write"]` can be simpler for a small static set. Validate at runtime at external boundaries; static types do not protect callers who pass unchecked JSON or `Any`.

### Example B — vendor leakage and unstable tuple shape

```python
from dataclasses import dataclass


@dataclass
class VendorResponse:
    status_code: int
    content: bytes


def fetch_before(url: str) -> tuple[VendorResponse, int]:
    # Illustrates the coupling: callers receive a vendor-owned object.
    return VendorResponse(status_code=200, content=b"ok"), 200


@dataclass(frozen=True, slots=True)
class FetchResult:
    url: str
    status_code: int
    body: bytes


def fetch_after(url: str) -> FetchResult:
    return FetchResult(url=url, status_code=200, body=b"ok")


print(fetch_before("https://example.test"))
print(fetch_after("https://example.test"))
```

A wrapper should expose only the fields the library is willing to support. If callers need raw transport access, offer a deliberately named escape hatch with an explicit stability statement instead of leaking it accidentally.

### Example C — long signature versus configuration object

```python
from dataclasses import dataclass


class DemoTransport:
    pass


class FetcherBefore:
    def __init__(self, timeout: float, retries: int, backoff: float,
                 cache: bool, parser: object, sink: object,
                 headers: dict[str, str], verify_tls: bool) -> None:
        self.timeout = timeout


@dataclass(frozen=True)
class FetcherConfig:
    timeout_seconds: float = 10.0


class FetcherAfter:
    def __init__(self, transport: DemoTransport, *, config: FetcherConfig) -> None:
        self.transport = transport
        self.config = config


before = FetcherBefore(10.0, 3, 0.5, True, object(), object(), {}, True)
after = FetcherAfter(DemoTransport(), config=FetcherConfig())
print(before.timeout, after.config.timeout_seconds)
```

Do not introduce a config class for two unrelated values just to look architectural. The right abstraction is the one that makes invariants and intent clearer.

### Example D — default changes are breaking behaviour

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class FetchResult:
    url: str
    timeout_seconds: float


def fetch(url: str, *, timeout_seconds: float = 10.0) -> FetchResult:
    # This stand-in demonstrates the signature/default contract, not network I/O.
    return FetchResult(url=url, timeout_seconds=timeout_seconds)


print(fetch("https://example.test"))  # Uses the published 10-second default.
# Changing the default to 60.0 changes behaviour for every caller omitting it.
```

If a default must change, explain why, announce it, consider a deprecation period or new named policy, and test the transition. A default is not merely an implementation detail when users can omit it.

## 7. `fetchkit` API implementation

The following is a small complete package illustrating a deliberately narrow public surface. It does not perform real network I/O: `Transport` is injected so the public API can be tested without external services. The transport response shape is a public `Protocol`; the final result contains library-owned values.

### 7.1 `fetchkit/_errors.py`

```python
class FetchError(Exception):
    """Base class for errors raised by fetchkit."""


class InvalidURLError(FetchError, ValueError):
    """Raised when a URL argument is invalid."""


class TransportError(FetchError):
    """Raised when the configured transport cannot complete a fetch."""
```

### 7.2 `fetchkit/_client.py`

```python
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Protocol
from urllib.parse import urlsplit

from ._errors import InvalidURLError, TransportError


@dataclass(frozen=True, slots=True)
class FetchResult:
    """Transport-independent response values returned by :func:`fetch`."""

    url: str
    status_code: int
    body: bytes


class TransportResponse(Protocol):
    """Structural response contract consumed by fetchkit adapters."""

    status_code: int
    body: bytes


class Transport(Protocol):
    """Structural interface implemented by an injected transport."""

    def get(self, url: str, *, timeout_seconds: float) -> TransportResponse: ...


@dataclass(frozen=True, slots=True)
class FetcherConfig:
    """Validated options for a :class:`Fetcher`."""

    timeout_seconds: float = 10.0

    def __post_init__(self) -> None:
        value = self.timeout_seconds
        try:
            is_finite = isfinite(value) if not isinstance(value, bool) else False
        except (OverflowError, TypeError):
            is_finite = False
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not is_finite
            or value <= 0
        ):
            raise ValueError("timeout_seconds must be a finite number greater than zero")


class Fetcher:
    """Fetch data through an injected synchronous transport."""

    def __init__(
        self,
        transport: Transport,
        *,
        config: FetcherConfig | None = None,
    ) -> None:
        self._transport = transport
        self._config = config if config is not None else FetcherConfig()

    def fetch(self, url: str) -> FetchResult:
        """Fetch *url* and return transport-independent response data.

        Raises:
            InvalidURLError: if the URL is not an absolute HTTP(S) URL.
            TransportError: if the transport raises an exception.
        """
        _validate_url(url)
        try:
            response = self._transport.get(
                url, timeout_seconds=self._config.timeout_seconds
            )
        except TransportError:
            raise
        except Exception as exc:
            raise TransportError("configured transport failed") from exc

        # Protocol annotations help static checking but do not validate a
        # third-party adapter at runtime. Translate missing/broken response
        # attributes at this boundary rather than leaking AttributeError.
        try:
            status_code = response.status_code
            body = response.body
        except Exception as exc:
            raise TransportError(
                "configured transport returned an unreadable response"
            ) from exc

        # Reject malformed values rather than silently coercing them (for
        # example, bytes(3) becomes NUL bytes rather than representing a body).
        if (
            isinstance(status_code, bool)
            or not isinstance(status_code, int)
            or not 100 <= status_code <= 599
        ):
            raise TransportError("configured transport returned an invalid status_code")
        if not isinstance(body, bytes):
            raise TransportError("configured transport returned a non-bytes body")

        return FetchResult(url=url, status_code=status_code, body=body)


def _validate_url(url: str) -> None:
    if not isinstance(url, str):
        raise InvalidURLError("url must be a string")
    try:
        parsed = urlsplit(url)
        # Accessing .port validates malformed/out-of-range explicit ports.
        _ = parsed.port
    except ValueError as exc:
        raise InvalidURLError("url contains an invalid authority or port") from exc
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise InvalidURLError("url must be an absolute HTTP(S) URL")


def fetch(
    url: str,
    *,
    transport: Transport,
    config: FetcherConfig | None = None,
) -> FetchResult:
    """Fetch one URL using an explicitly supplied transport.

    This convenience function is dependency-injected: it does not create a
    hidden global client or perform network I/O on import.
    """
    return Fetcher(transport, config=config).fetch(url)
```

### 7.3 `fetchkit/__init__.py`

```python
from ._client import (
    Fetcher, FetcherConfig, FetchResult, Transport, TransportResponse, fetch
)
from ._errors import FetchError, InvalidURLError, TransportError

__all__ = [
    "Fetcher",
    "FetcherConfig",
    "FetchResult",
    "Transport",
    "TransportResponse",
    "fetch",
    "FetchError",
    "InvalidURLError",
    "TransportError",
]
```

### 7.4 `fetchkit/py.typed`

Create an empty file named `py.typed` and include it in the built distribution. Packaging configuration must explicitly include it where the build backend does not include package data by default.

### 7.5 User-facing quick start

```python
from dataclasses import dataclass

from fetchkit import FetchResult, fetch


@dataclass(frozen=True)
class DemoResponse:
    status_code: int
    body: bytes


class DemoTransport:
    def get(self, url: str, *, timeout_seconds: float) -> DemoResponse:
        return DemoResponse(status_code=200, body=b"hello")


result: FetchResult = fetch(
    "https://example.test/data",
    transport=DemoTransport(),
)
assert result.status_code == 200
assert result.body == b"hello"
```

This quick start uses a fake transport, so it is deterministic and requires no external service. A production adapter can implement the same `Transport` protocol. The example deliberately avoids returning a third-party HTTP response type.

## 8. API tests and review checklist

### 8.1 `tests/test_public_api.py`

These tests import the package as a user would. They check intended exports, the basic contract, input validation, exception wrapping, and the documentation example's behaviour.

```python
from dataclasses import dataclass

import pytest
import fetchkit
from fetchkit import (
    FetchError,
    Fetcher,
    FetcherConfig,
    FetchResult,
    InvalidURLError,
    TransportError,
    fetch,
)


@dataclass(frozen=True)
class FakeResponse:
    status_code: int
    body: bytes


class FakeTransport:
    def __init__(self, response: FakeResponse | None = None) -> None:
        self.response = response or FakeResponse(200, b"ok")
        self.calls: list[tuple[str, float]] = []

    def get(self, url: str, *, timeout_seconds: float) -> FakeResponse:
        self.calls.append((url, timeout_seconds))
        return self.response


def test_public_exports_are_explicit() -> None:
    assert set(fetchkit.__all__) == {
        "Fetcher", "FetcherConfig", "FetchResult", "Transport",
        "TransportResponse", "fetch", "FetchError", "InvalidURLError",
        "TransportError",
    }
    for name in fetchkit.__all__:
        assert hasattr(fetchkit, name)


def test_fetch_returns_library_owned_result_and_passes_timeout() -> None:
    transport = FakeTransport(FakeResponse(201, b"created"))
    result = fetch(
        "https://example.test/item",
        transport=transport,
        config=FetcherConfig(timeout_seconds=2.5),
    )
    assert result == FetchResult(
        url="https://example.test/item", status_code=201, body=b"created"
    )
    assert transport.calls == [("https://example.test/item", 2.5)]


def test_fetcher_instance_uses_default_config() -> None:
    transport = FakeTransport()
    result = Fetcher(transport).fetch("http://example.test/")
    assert result.body == b"ok"
    assert transport.calls == [("http://example.test/", 10.0)]


@pytest.mark.parametrize("url", [
    "", "/relative", "ftp://example.test/a", "https:///missing-host",
    "http://example.test:bad-port/", "http://:/",
])
def test_invalid_url_raises_public_exception(url: str) -> None:
    with pytest.raises(InvalidURLError):
        fetch(url, transport=FakeTransport())


@pytest.mark.parametrize("timeout", [0, -1, float("nan"), float("inf"), True])
def test_invalid_timeout_is_rejected_at_configuration_boundary(timeout: float) -> None:
    with pytest.raises(ValueError, match="timeout_seconds"):
        FetcherConfig(timeout_seconds=timeout)  # type: ignore[arg-type]


def test_transport_exception_is_wrapped_and_chained() -> None:
    class BrokenTransport:
        def get(self, url: str, *, timeout_seconds: float) -> FakeResponse:
            raise OSError("private transport detail")

    with pytest.raises(TransportError) as exc_info:
        fetch("https://example.test", transport=BrokenTransport())
    assert isinstance(exc_info.value.__cause__, OSError)
    assert isinstance(exc_info.value, FetchError)


@pytest.mark.parametrize("status_code", [True, 99, 600, "200"])
def test_invalid_transport_status_is_rejected(status_code: object) -> None:
    class MalformedTransport:
        def get(self, url: str, *, timeout_seconds: float) -> FakeResponse:
            return FakeResponse(status_code, b"ok")  # type: ignore[arg-type]

    with pytest.raises(TransportError, match="invalid status_code"):
        fetch("https://example.test", transport=MalformedTransport())


def test_non_bytes_transport_body_is_rejected_not_coerced() -> None:
    class MalformedTransport:
        def get(self, url: str, *, timeout_seconds: float) -> FakeResponse:
            return FakeResponse(200, 3)  # type: ignore[arg-type]

    with pytest.raises(TransportError, match="non-bytes body"):
        fetch("https://example.test", transport=MalformedTransport())


def test_missing_transport_response_attribute_is_translated() -> None:
    class MalformedTransport:
        def get(self, url: str, *, timeout_seconds: float) -> object:
            return object()

    with pytest.raises(TransportError, match="unreadable response"):
        fetch("https://example.test", transport=MalformedTransport())  # type: ignore[arg-type]
```

The broad `except Exception` in the example is a deliberate boundary policy: it normalizes arbitrary adapter failures into `TransportError` while preserving the original cause. A production library should decide explicitly whether cancellation-like exceptions, programming errors, or particular vendor errors should propagate instead. Never copy a catch-all boundary without making that policy decision.

### 8.2 Type-check and documentation checks

Run the checks from the project root after installing the package in editable mode or setting up the project environment:

```bash
python -m pytest -q
mypy --strict fetchkit tests
# Alternative: pyright --strict
ruff check fetchkit tests
```

The snippets use Python 3.12-compatible syntax. Strict typing should also be run against a standalone file containing the README quick start, because a package can type-check internally while giving users poor inference or protocol diagnostics. If using doctest, keep examples deterministic and avoid hidden network dependencies.

### 8.3 Public API review checklist

- [ ] The README's first example is complete, short, and runnable.
- [ ] Public imports work from the package root; users do not need private paths.
- [ ] `__all__` is intentional, reviewed, and snapshot-tested; no claim is made that it enforces access control.
- [ ] Every public function/method has precise parameter and return annotations and a useful docstring.
- [ ] Parameter names communicate units; configuration is keyword-only where appropriate.
- [ ] No unexplained positional booleans, magic strings, or silent mode switches.
- [ ] Defaults are documented and changes have an explicit compatibility plan.
- [ ] Public results and exceptions are library-owned unless vendor leakage is intentional.
- [ ] Invalid inputs fail early with actionable errors; errors do not leak secrets.
- [ ] Side effects, logging, resource ownership, laziness, concurrency, and cancellation semantics are documented where relevant.
- [ ] `py.typed` is packaged; public examples pass strict type checking.
- [ ] Tests import the package as an external user would and exercise the documented path.
- [ ] Public API snapshots/API diffs are reviewed rather than blindly accepted.
- [ ] Experimental APIs are clearly labelled and have a removal/deprecation policy.
- [ ] Import-time work is minimal; optional dependencies are lazy.
- [ ] Release notes describe breaking changes and migration steps.

### 8.4 Snapshot and API-diff tests

A small export snapshot can be maintained as a test (as above) or a dedicated golden file. For larger libraries, use `griffe` or a comparable API-diff tool to compare releases. Include public signatures and documented names, not private object internals. Every diff should be reviewed by a maintainer: sometimes a snapshot change is an intentional addition, and sometimes a harmless-looking annotation or default change is breaking.

## 9. Common mistakes

The roadmap explicitly calls out these mistakes; treat each as a release-blocking review question:

1. **Exposing implementation types.** Returning `requests.Response` or another vendor object makes that dependency part of your public contract. Prefer a library-owned result model or intentionally document the escape hatch.
2. **Magic strings and boolean flags.** Values such as `"fast"`, `"auto"`, and chains of booleans hide semantics and make typos easy. Use explicit names, enums, `Literal`, or separate operations where appropriate.
3. **Changing defaults silently.** A new timeout, retry count, cache mode, or verification setting changes behaviour for every caller that omitted the option. Document and manage it as a compatibility change.

Additional frequent failure modes:

- treating underscore conventions or `__all__` as security boundaries;
- documenting internal behaviour as stable without intending to support it;
- exposing every implementation module at the package root;
- accepting `Any` or unchecked `**kwargs` everywhere;
- returning tuples whose positions callers must memorize;
- building a complex builder when a dataclass is sufficient;
- introducing a global client or registry that makes tests interfere with one another;
- catching every exception and erasing useful failure context;
- claiming thread safety, async safety, or constant-time behaviour without evidence;
- writing docs after implementation and discovering the API is awkward only at release time;
- snapshotting incidental implementation details instead of the supported contract;
- importing optional, heavy dependencies during package import.

## 10. Self-check questions with model answers

### 1. List five ways an API can make misuse hard.

**Model answer:** (1) Use keyword-only options with descriptive names and units. (2) Replace magic strings with `Enum` or `Literal` and validate untrusted runtime inputs. (3) Validate configuration/value objects at construction. (4) Return typed, documented result objects and a coherent exception hierarchy instead of ambiguous tuples or `None`-for-error. (5) Make side effects, ownership, defaults, and error cases explicit in docs and tests. Other valid answers include strict typing, safe defaults, small public surfaces, and clear deprecation policy.

### 2. Apply `__all__`, `_internal` modules, and a snapshot test to lock the public surface of `fetchkit`.

**Model answer:** Keep implementation in `_client.py` and `_errors.py`, re-export only intended names from `fetchkit/__init__.py`, and declare the exact list in `__all__`. Add a test that compares the public list to an approved expected set and verifies each name resolves. Treat the snapshot as a review gate—not an access-control mechanism—and separately test documented signatures and behaviour.

### 3. Write the README quick-start before implementation and revise the API after trying to write the examples.

**Model answer:** Start with the desired user workflow, for example importing `fetch` and `FetchResult` from the package root and making one deterministic call. Try to express the workflow without private imports, unexplained flags, or hidden setup. If the example needs many parameters or a vendor-specific object, simplify the public API or add a clear configuration/adapter abstraction. Execute the example in CI and type-check it in strict mode.

## 11. Summary and completion checklist

A good public API makes common work obvious, makes misuse difficult, keeps implementation details replaceable, and tells users what is stable. The important unit of design is not an isolated function but the whole observable contract: names, signatures, values, errors, side effects, docs, performance, and lifecycle.

- [ ] I can explain the difference between public convention, documented contract, and accidental surface.
- [ ] I can design a package root with deliberate re-exports and explicit `__all__`.
- [ ] I can explain keyword-only options, boolean traps, abstract inputs, and library-owned results.
- [ ] I can use `Enum`/`Literal` and validated configuration without overengineering.
- [ ] I can distinguish eager collections from lazy iterators and sync from async contracts.
- [ ] I can write a README example first and make it executable and strictly typed.
- [ ] I can describe how Hyrum's law, semantic versioning, deprecation, and API-diff checks affect releases.
- [ ] I can document errors, logging, metrics, ownership, concurrency, and import cost.
- [ ] I have tested the public API from the consumer's import perspective.
- [ ] I can critique real APIs using concrete examples rather than taste alone.

## 12. Authoritative references

### Roadmap sources

- `Roadmap_ptree.md` — Stage 1 tree, Module 1.20, and the intended placement of `06-designing-public-apis.md`.
- `roadmap-Design-Patterns-and-Library-API-Design.md` — Module 1.20 Lesson 06 requirements, common mistakes, and all three self-check questions.

### Python and packaging references

- Python documentation, **The import system**: <https://docs.python.org/3/reference/import.html>
- Python documentation, **Packages**: <https://docs.python.org/3/tutorial/modules.html#packages>
- Python documentation, **Typing**: <https://docs.python.org/3/library/typing.html>
- Python documentation, **`dataclasses`**: <https://docs.python.org/3/library/dataclasses.html>
- Python documentation, **`enum`**: <https://docs.python.org/3/library/enum.html>
- PEP 8, **Style Guide for Python Code**: <https://peps.python.org/pep-0008/>
- PEP 561, **Distributing and Packaging Type Information**: <https://peps.python.org/pep-0561/>
- PEP 484, **Type Hints**: <https://peps.python.org/pep-0484/>
- Python Packaging User Guide: <https://packaging.python.org/>

### Tools and API-evolution references

- mypy documentation: <https://mypy.readthedocs.io/>
- Pyright documentation: <https://microsoft.github.io/pyright/>
- pytest documentation: <https://docs.pytest.org/>
- griffe documentation: <https://mkdocstrings.github.io/griffe/>
- Semantic Versioning 2.0.0: <https://semver.org/>

### Real API critique: three examples

The roadmap suggests real API critiques such as `requests`, `httpx`, `pathlib`, `subprocess.run`, sklearn estimators, or SDKs. The following critiques are conceptual and should be revisited against the installed/current versions before using them as a version-specific reference.

1. **`pathlib.Path`** — *Strengths:* object-oriented path operations, operator support for path joining, and methods grouped around the path abstraction make common filesystem tasks discoverable. *Trade-off:* `Path` combines path representation with filesystem operations, so code that wants pure lexical path manipulation must distinguish `PurePath` from concrete `Path`; users can accidentally perform I/O when they intended only to transform a path. *Lesson for `fetchkit`:* make side-effect boundaries clear and use distinct abstractions when lexical and I/O behaviour differ.
2. **`subprocess.run`** — *Strengths:* one standard entry point covers arguments, timeout, environment, capture, and checking; `check=True` raises `CalledProcessError`, and timeout is explicit. *Trade-off:* the API has many keyword options with interactions, and safe command construction still requires callers to understand argument lists versus `shell=True`, text/encoding behaviour, and captured output. *Lesson for `fetchkit`:* keyword-only options and sensible defaults help, but docs must explain interactions and security-sensitive choices; don't hide important execution modes behind booleans.
3. **`httpx` client API** — *Strengths:* explicit `Client`/`AsyncClient` separation communicates sync versus async use; client objects make connection pooling, shared configuration, and lifecycle ownership visible. *Trade-off:* users must learn when to use top-level helpers versus a long-lived client and must close client resources correctly; sync and async variants duplicate some concepts. *Lesson for `fetchkit`:* progressive disclosure is useful, but make resource ownership and async naming explicit and avoid silently creating long-lived global clients.

These are design evaluations, not claims that the libraries are defective. A good critique names a concrete use case, identifies the trade-off, and proposes an alternative with costs—not merely a stylistic preference.
