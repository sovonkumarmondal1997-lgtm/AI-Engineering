# Error Hierarchies for Libraries

> **Module 1.20 · Lesson 08 · Python 3.12+**  
> Focus: design errors around caller recovery actions, translate failures at system boundaries, and make the exception contract testable.

## 1. Learning objectives and prerequisites

By the end of this lesson, you should be able to:

- Explain why exception classes, inheritance, attributes, and chaining are part of a library's public API.
- Distinguish invalid caller input, configuration defects, expected domain outcomes, transient operational failures, and programming bugs.
- Design a small, shallow `fetchkit` hierarchy that lets callers catch a stable library-owned root exception.
- Translate selected vendor/stdlib exceptions at adapters while preserving diagnostic causes without leaking vendor types into the public contract.
- Write retry logic that uses semantic categories and operation idempotency rather than retrying every failure.
- Test public exception types, stable message fragments, structured attributes, cause chains, and pickle round-trips.
- Avoid swallowing cancellation, logging the same exception at every layer, and exposing secrets in error text.

### Prerequisites

You should know Python classes and inheritance, `try`/`except`/`else`/`finally`, context managers, type hints, `pytest.raises`, and the basics of HTTP requests and retries. This lesson builds on the module's API design, plugin registry, and backward-compatibility lessons.

## 2. Exception mental model

An exception is both a runtime control-flow signal and a public contract. Callers write code like `except FetchError:` and `except TransientFetchError:`. If a library changes which type it raises, a caller's recovery logic may stop working even when the error message looks similar.

A useful hierarchy describes **what a caller can reasonably do next**:

- Fix an argument or configuration.
- Authenticate or request access.
- Treat a resource as absent.
- Correct malformed input or an unsupported response.
- Retry an operation when the failure is plausibly transient and retrying is safe.
- Escalate an unexpected defect rather than disguising it as an operational failure.

Prefer this over organizing exceptions solely by internal module (`http_errors`, `json_errors`, `cache_errors`). A caller usually should not need to know which private module happened to raise an error.

```text
Exception
└── FetchError                 # Catch all documented fetchkit failures
    ├── TransientFetchError    # A retry may succeed; safety still matters
    │   ├── TransportError
    │   ├── TimeoutFetchError
    │   └── RateLimitError
    └── PermanentFetchError    # Blind retry is not expected to help
        ├── NotFoundError
        ├── AuthenticationError
        ├── ProtocolError
        └── ParseError

FetchError + ValueError
├── ValidationError            # Caller-supplied value is invalid
└── ConfigError                # Configuration is invalid
```

This is a deliberately small taxonomy. Add a class only when callers need to handle that category differently. Avoid a deep tree that mirrors every implementation component.

## 3. Beginner exception design

### 3.1 Exceptions, return codes, and sentinel values

Use exceptions for failures that interrupt the normal operation and need to travel up the call stack. A result object or `None` can be better for an ordinary, expected outcome, such as a cache lookup that commonly misses.

| Technique | Appropriate when | Main risk |
|---|---|---|
| Raise a domain exception | Operation failed and caller needs a recovery path | Poor taxonomy forces message parsing |
| Return a result object | Success and failure are both expected outcomes, especially with partial success | Callers may forget to inspect status |
| Return `None` / sentinel | One simple, documented absence case | Ambiguity if `None` is also valid data |
| Return integer/status code | Interop boundary or API explicitly defines status codes | Numeric codes often lose context and composability |

Do not use exceptions for routine branching in a hot path when a simple result communicates the outcome better. Conversely, do not return `False` for a failure if callers need to know whether it was a timeout, authentication failure, or invalid response.

### 3.2 Built-ins versus library-owned exceptions

Use built-in exceptions when they accurately express a programming contract. For example, `TypeError` is appropriate when a function receives the wrong kind of argument, and `ValueError` when a value has the right broad type but is outside the accepted domain. Do not wrap every `TypeError` or `ValueError` raised anywhere in the implementation: it could be a programming bug.

Use a library-owned exception when the failure is a documented part of the library's domain. A stable root allows callers to catch all expected library failures without catching unrelated exceptions from their own code.

```python
from __future__ import annotations

import math


class FetchError(Exception):
    """Base class for documented fetchkit operational/domain failures."""


class TransientFetchError(FetchError):
    """A failure that may clear with time; retry only when safe."""

    def __init__(self, message: str, retry_after: float | None = None) -> None:
        try:
            finite_delay = retry_after is None or math.isfinite(retry_after)
        except OverflowError:
            finite_delay = False
        if retry_after is not None and (
            isinstance(retry_after, bool)
            or not isinstance(retry_after, (int, float))
            or not finite_delay
            or retry_after < 0
        ):
            raise ValueError("retry_after must be a finite, non-negative number or None")
        super().__init__(message)
        self.retry_after = float(retry_after) if retry_after is not None else None

    def __reduce__(self) -> tuple[type[TransientFetchError], tuple[str, float | None]]:
        # Preserve custom state across pickle, including the optional delay.
        return (type(self), (str(self), self.retry_after))


class PermanentFetchError(FetchError):
    """A failure for which an identical blind retry is not expected to help."""


class ValidationError(FetchError, ValueError):
    """A caller-supplied value violates fetchkit's documented constraints."""


class ConfigError(FetchError, ValueError):
    """The supplied fetchkit configuration is invalid."""


class TransportError(TransientFetchError):
    """A classified transport failure that may be transient."""


class TimeoutFetchError(TransientFetchError):
    """A timeout classified as transient by the adapter and operation policy."""


class RateLimitError(TransientFetchError):
    """The remote service rate-limited the request; honor retry guidance."""


class NotFoundError(PermanentFetchError):
    """The requested resource is absent under the service's semantics."""


class AuthenticationError(PermanentFetchError):
    """Credentials are missing or rejected; retrying unchanged is not useful."""


class ProtocolError(PermanentFetchError):
    """The remote peer violated the protocol expected by fetchkit."""


class ParseError(PermanentFetchError):
    """The response could not be parsed as the requested representation."""
```

The example is complete as a class definition and needs no third-party dependencies. The multiple inheritance in `ValidationError` and `ConfigError` is intentional: callers may catch the stable `FetchError` root or use `ValueError` when that is the documented contract. Do not add builtin base classes casually; inheritance is itself API surface.

### 3.3 Error messages: context without secrets

A useful message says what failed, gives safe context, and suggests a next action when known. Structured attributes are better than forcing callers to parse a string.

Good:

```python
raise ValidationError("url must use http or https; received scheme 'file'")
raise ConfigError("timeout must be greater than zero")
raise NotFoundError("resource was not found (status=404)")
```

Avoid:

```python
# Bad: could expose an authorization header, signed URL, or response body.
raise FetchError(f"Request failed: {request!r}; headers={headers!r}")
```

Do not include passwords, bearer tokens, cookies, full signed URLs, private response bodies, or unsanitized user input. Sanitize CR/LF and other control characters before putting user-controlled values into logs. If URL context is needed, prefer a sanitized origin/path and omit query strings that may contain credentials.

### 3.4 What callers should distinguish

- **Invalid input/configuration:** fix the argument or configuration; do not retry unchanged.
- **Unavailable resource:** decide whether absence is expected in the domain; do not assume it is transient.
- **Operational transient:** retry only if the adapter has classified the failure and the operation is safe to repeat.
- **Unexpected programming failure:** preserve the traceback and fix the defect; do not relabel it as a network error.

`FetchError` should cover documented library failures, not every exception that can escape Python code. `KeyboardInterrupt`, `SystemExit`, cancellation, and programming defects must not be indiscriminately converted to `FetchError`.

## 4. Intermediate hierarchy and translation

### 4.1 Translate at boundaries

A vendor client may expose its own exception hierarchy. Catch only the known exceptions that have a deliberate mapping to `fetchkit`'s public categories. Keep the vendor dependency inside the adapter. `raise PublicError(...) from exc` preserves the original cause for debugging while callers can catch the library-owned type.

The following self-contained example uses stand-in vendor exceptions, so the core lesson runs without installing an HTTP client. A real adapter would catch the actual documented exception classes from its chosen vendor.

```python
from collections.abc import Callable

from fetchkit.errors import (
    AuthenticationError,
    ProtocolError,
    TimeoutFetchError,
    TransportError,
)


class VendorConnectError(Exception):
    """Stand-in for a vendor library's connection exception."""


class VendorReadTimeout(Exception):
    """Stand-in for a vendor library's read-timeout exception."""


class VendorAuthenticationFailure(Exception):
    """Stand-in for a vendor library's authentication exception."""


class VendorMalformedResponseError(Exception):
    """Stand-in for a vendor library's malformed-response exception."""


def translate_vendor_call[T](operation: Callable[[], T]) -> T:
    """Run a vendor operation and translate only recognized failures."""
    try:
        return operation()
    except VendorConnectError as exc:
        raise TransportError("connection failed; retry may succeed") from exc
    except VendorReadTimeout as exc:
        raise TimeoutFetchError("request timed out; check operation retry safety") from exc
    except VendorAuthenticationFailure as exc:
        raise AuthenticationError("authentication failed; check configured credentials") from exc
    except VendorMalformedResponseError as exc:
        raise ProtocolError("remote response was rejected by the adapter") from exc
```

This example uses Python 3.12's PEP 695 type-parameter syntax. It deliberately does not catch `Exception`; unknown failures pass through unchanged so programming defects remain visible. In a production adapter, the mapping must follow the vendor library's documented semantics, not merely the names of its exception classes.

### 4.2 Chaining and intentional suppression

Use `raise NewError(...) from exc` when translating an underlying failure. `__cause__` then identifies the original exception, and the traceback shows the causal relationship.

```python
try:
    decode_payload(payload)
except UnicodeDecodeError as exc:
    raise ParseError("response body is not valid UTF-8") from exc
```

Use `from None` only when deliberately hiding a low-level detail from the displayed traceback because it is irrelevant or sensitive. It suppresses display of the implicit context; it does not erase the original exception object from every diagnostic mechanism. Prefer safe, useful public context over exposing secrets.

```python
try:
    load_private_key(config_path)
except PermissionError:
    # Do not expose local paths or operating-system details in this public message.
    raise ConfigError("could not read configured credentials; check file permissions") from None
```

Do not suppress a cause simply to make a traceback look tidy. Record sanitized diagnostic context at a suitable boundary if the low-level cause is necessary for operations, and ensure logs are access-controlled.

### 4.3 Translate only at deliberate boundaries

A useful rule of thumb:

- **Raise:** the current layer detects a domain failure it owns (for example, an unsupported content type).
- **Wrap/translate:** an external exception crosses a public boundary and should become a stable library type.
- **Propagate:** the exception already matches the documented contract, or it is an unexpected bug that should remain visible.
- **Suppress with `from None`:** only when the low-level context should not appear in the public traceback; keep a safe, actionable message.

Do not wrap `ValueError` around an entire function just because some inputs can be invalid. It may convert a bug inside your code into a misleading user error. Validate explicitly at the public boundary, then allow unexpected internal failures to propagate.

### 4.4 Retry semantics are not just inheritance

`TransientFetchError` means “may be transient,” not “always repeat the operation.” Retry decisions also require:

1. **Operation semantics:** Is the request idempotent, or does it use a stable idempotency key?
2. **Failure timing:** Did the request fail before the server could commit a side effect, or is the outcome unknown?
3. **Budget:** Is the attempt/deadline budget still available?
4. **Server guidance:** Is there a `Retry-After` value, and can it be honored?
5. **Failure classification:** Was this a known transport/timeout/rate-limit case, not an arbitrary exception?

A timeout after a write is ambiguous: the server may have committed the operation. A rate limit can be transient, but retrying too soon violates the service contract. Authentication errors, invalid input, malformed protocol responses, and most deterministic parse errors should not be blindly retried.

## 5. Advanced production considerations

### 5.1 Public contract and vendor independence

Public exceptions need stable names, inheritance, attributes, and documented meanings. Adding a new subclass is often additive, but changing a raised type, moving a class, or changing its base classes can break callers' `except` clauses and `isinstance` checks. Treat those changes as compatibility-sensitive and follow the module's deprecation policy.

Keep vendor exceptions out of signatures and documented `Raises:` sections. A cause chain can still reveal a vendor exception to advanced diagnostic code (`exc.__cause__`); the public contract should promise the `fetchkit` type, not that the cause is hidden. If exposing the cause is a security concern, do not include sensitive objects or secret-bearing messages in it, and use deliberate suppression only when justified.

### 5.2 Structured attributes and pickling

Use stable fields for machine-readable facts such as `status_code`, `retry_after`, `field`, or a sanitized `request_id`. Do not make consumers parse the message. Avoid storing whole request/response objects, credentials, or huge payloads on exceptions.

Exceptions often need to cross process boundaries. The default pickle reconstruction uses the exception's `args`, which may not preserve custom attributes if the constructor has extra parameters. Test a round trip and implement `__reduce__` when needed. Never assume an exception is picklable just because it inherits `Exception`.

```python
import pickle

error = RateLimitError("rate limit reached", 2.5)
restored = pickle.loads(pickle.dumps(error))
assert isinstance(restored, RateLimitError)
assert str(restored) == str(error)
assert restored.retry_after == 2.5
```

Only pickle exceptions from trusted sources; pickle is not a safe interchange format for untrusted data.

### 5.3 Async cancellation and cleanup

In asynchronous code, cancellation is control flow, not a normal transient request failure. Do not catch `BaseException` or convert `asyncio.CancelledError` into `TransientFetchError`. On supported Python versions, cancellation should generally propagate after `finally` blocks release resources. `asyncio.TaskGroup` can aggregate child failures into an `ExceptionGroup`; handle only the categories you own and do not flatten every member into one generic exception.

```python
import asyncio


async def fetch_async() -> bytes:
    try:
        return await perform_async_request()
    except asyncio.CancelledError:
        # Optional cleanup belongs in finally/context managers; cancellation propagates.
        raise
```

`perform_async_request` is an illustrative adapter function supplied by an application; this fragment is not a standalone runnable program. Resource cleanup should be expressed with `async with` or `try/finally`, and cleanup errors should not silently replace the primary failure unless the contract explicitly says so.

### 5.4 Logging and observability

A library should generally raise exceptions and expose useful context; the application decides whether to log, retry, return an HTTP response, or exit. Avoid `print()` and `sys.exit()` in library code. Log an exception once at an application or service boundary with a correlation ID and sanitized fields, not at every layer where it propagates. Duplicate logs inflate alert counts and obscure the origin.

If a library provides logging hooks, treat logger names, levels, and structured fields as part of its operational interface. Do not log credentials or entire request objects. Sanitize user-controlled text to reduce log injection risk. For auth failures, use messages that do not reveal whether a particular account exists when that distinction is sensitive.

### 5.5 External contracts and aggregation

When mapping to REST, CLI, or agent-tool schemas, map stable exception categories to stable external codes. For example, a CLI can map invalid input to exit code 2 and an unhandled operational failure to a documented nonzero code; an HTTP adapter can map `NotFoundError` to 404. These are application-level policies and should not be hard-coded into a general-purpose library's exception class.

For batch operations, Python 3.11+ `ExceptionGroup` may preserve multiple independent failures. If partial success is a normal business outcome, a result object containing successes and failures may be clearer than raising an exception group. Choose based on whether the caller should treat the operation as failed as a whole.

For distributed AI/data services, a product may need additional **capacity/quota**, **policy rejection**, or **degraded/partial-result** categories. Add them only when callers genuinely have different recovery actions: capacity may require waiting or reducing demand; a policy rejection generally requires changing the request or escalating to a human; partial results may be better represented by a result object than by a failure exception. Do not infer these categories solely from an HTTP status code without the service contract.

## 6. Exception taxonomy and recovery table

The following table is a starting contract for the example library, not a universal classification of all network failures.

| Public exception | Meaning | Typical caller action | Retry default | Illustrative CLI exit code* | Important caveat |
|---|---|---|---|---|---|
| `FetchError` | Base class for documented fetchkit failures | Catch at a broad library boundary; inspect subtype | No blanket retry | 1 (generic library failure) | Broad catch should not hide programming bugs |
| `ValidationError` | Caller value violates input contract | Correct the value | No | 2 (usage/input error) | Inherits `ValueError` intentionally |
| `ConfigError` | Configuration cannot be used | Correct configuration/permissions | No | 2 (usage/config error) | Do not expose secret paths or credentials |
| `TransientFetchError` | Classified failure may clear with time | Apply bounded policy if operation is safe | Conditional | 4 (transient failure after exhaustion) | Category alone does not prove retry safety |
| `TransportError` | Adapter classified transport problem as transient | Retry safe/idempotent operation within budget | Conditional | 4 | Some transport errors occur after side effects |
| `TimeoutFetchError` | Adapter classified timeout as potentially transient | Check deadline and idempotency before retry | Conditional | 4 | Server may have completed the request |
| `RateLimitError` | Service declined/limited request due to rate | Honor `retry_after`, back off with jitter | Usually later, if safe | 4 | Retry budget and service policy still apply |
| `PermanentFetchError` | Repeating unchanged is not expected to help | Change request/configuration or escalate | No | 3 (permanent remote failure) | Parent category, not a retry signal |
| `NotFoundError` | Resource does not exist under domain semantics | Treat as absent or correct identifier | No | 3, or a domain-specific not-found code | Some eventually consistent systems differ |
| `AuthenticationError` | Credentials rejected | Refresh/fix credentials or permissions | No unchanged retry | 3, or a documented auth code | Do not disclose account-existence details |
| `ProtocolError` | Remote response violates expected protocol | Escalate, inspect compatibility | No | 3 | Could indicate service change or adapter defect |
| `ParseError` | Response representation is invalid/unexpected | Inspect content/schema or server response | Usually no | 3 | Retry only if response may be transiently incomplete and contract supports it |
| `TypeError` / unrelated `ValueError` | Likely programming misuse or defect | Fix code; inspect traceback | No | Usually 70 for an uncaught software defect | Do not wrap indiscriminately |
| `asyncio.CancelledError` | Task cancellation | Propagate; release resources | No automatic retry | Application-specific shutdown/interrupt code | Do not swallow or translate as a request failure |

*The exit-code column is an **illustrative application policy**, not a fetchkit guarantee or a universal standard. A library should expose semantic exceptions; a CLI adapter chooses and documents its own exit codes.

A type hierarchy helps route recovery, but actual retry decisions should be made at a layer that knows operation semantics, idempotency, deadlines, and the service's contract.

## 7. `fetchkit` implementation

This implementation is a minimal, executable demonstration of the public exception contract and retry boundary. It has no third-party dependencies. In production, replace the stand-in vendor exception classes with the actual dependency's documented types and keep the mapping inside the adapter module.

### 7.1 `fetchkit/errors.py`

```python
from __future__ import annotations

import math


class FetchError(Exception):
    """Base class for documented fetchkit failures."""


class TransientFetchError(FetchError):
    """A failure that may clear with time; retry only if safe."""

    def __init__(self, message: str, retry_after: float | None = None) -> None:
        try:
            finite_delay = retry_after is None or math.isfinite(retry_after)
        except OverflowError:
            finite_delay = False
        if retry_after is not None and (
            isinstance(retry_after, bool)
            or not isinstance(retry_after, (int, float))
            or not finite_delay
            or retry_after < 0
        ):
            raise ValueError("retry_after must be a finite, non-negative number or None")
        super().__init__(message)
        self.retry_after = float(retry_after) if retry_after is not None else None

    def __reduce__(self) -> tuple[type[TransientFetchError], tuple[str, float | None]]:
        return (type(self), (str(self), self.retry_after))


class PermanentFetchError(FetchError):
    """A failure for which an identical blind retry is not expected to help."""


class ValidationError(FetchError, ValueError):
    """Caller input is invalid."""


class ConfigError(FetchError, ValueError):
    """Configuration is invalid or cannot be used."""


class TransportError(TransientFetchError):
    """A known transport failure classified as potentially transient."""


class TimeoutFetchError(TransientFetchError):
    """A timeout classified as potentially transient."""


class RateLimitError(TransientFetchError):
    """The remote service has asked the caller to slow down."""


class NotFoundError(PermanentFetchError):
    """The requested resource was not found."""


class AuthenticationError(PermanentFetchError):
    """Credentials were missing or rejected."""


class ProtocolError(PermanentFetchError):
    """The remote peer returned an unsupported or invalid protocol response."""


class ParseError(PermanentFetchError):
    """A response could not be parsed as the expected representation."""
```

### 7.2 `fetchkit/adapters/vendor.py`

```python
from collections.abc import Callable
from typing import TypeVar

from fetchkit.errors import (
    AuthenticationError,
    ProtocolError,
    TimeoutFetchError,
    TransportError,
)

T = TypeVar("T")


class VendorConnectError(Exception):
    """Test double for a vendor connection error."""


class VendorReadTimeout(Exception):
    """Test double for a vendor read timeout."""


class VendorAuthenticationFailure(Exception):
    """Test double for a vendor authentication error."""


class VendorMalformedResponseError(Exception):
    """Test double for a known malformed-response failure."""


def call_vendor(operation: Callable[[], T]) -> T:
    """Call a vendor operation and translate known exceptions only."""
    try:
        return operation()
    except VendorConnectError as exc:
        raise TransportError("connection failed; retry may succeed") from exc
    except VendorReadTimeout as exc:
        raise TimeoutFetchError("request timed out; check retry safety") from exc
    except VendorAuthenticationFailure as exc:
        raise AuthenticationError("authentication failed; check configured credentials") from exc
    except VendorMalformedResponseError as exc:
        raise ProtocolError("remote response was rejected by the adapter") from exc
```

Notice that unknown `RuntimeError`, `TypeError`, and other exceptions are not translated. This is intentional: only known boundary failures should become public domain exceptions.

### 7.3 Retry policy with bounded attempts

```python
from collections.abc import Callable
from time import sleep
from typing import TypeVar

from fetchkit.errors import TransientFetchError

T = TypeVar("T")


def run_with_retry(
    operation: Callable[[], T],
    *,
    max_attempts: int = 3,
    idempotent: bool,
    sleep_fn: Callable[[float], None] = sleep,
) -> T:
    """Retry classified transient failures only when repeating is safe.

    `max_attempts` includes the first attempt. This minimal example uses
    constant backoff; production code should add a deadline, jitter, and
    service-specific Retry-After handling. `retry_after` is validated as finite
    and non-negative, but this teaching helper does not enforce a wall-clock
    deadline or cap a server-provided delay; production callers must do so.
    """
    if isinstance(max_attempts, bool) or not isinstance(max_attempts, int) or max_attempts < 1:
        raise ValueError("max_attempts must be a positive integer")
    if not idempotent and max_attempts > 1:
        # A caller may still request one attempt for a non-idempotent operation.
        max_attempts = 1

    for attempt in range(1, max_attempts + 1):
        try:
            return operation()
        except TransientFetchError as exc:
            if attempt == max_attempts:
                raise
            delay = exc.retry_after if exc.retry_after is not None else min(0.25 * attempt, 2.0)
            sleep_fn(max(0.0, delay))
    raise AssertionError("unreachable")
```

The retry helper catches only `TransientFetchError`. It does not catch `FetchError`, `Exception`, or `BaseException`; permanent failures and bugs propagate. In a production design, a timeout or transport category should only be emitted when the adapter has enough evidence to classify it. For writes with an ambiguous outcome, require a server-supported idempotency key or do not retry.

### 7.4 Public import surface: `fetchkit/__init__.py`

```python
from fetchkit.errors import (
    AuthenticationError,
    ConfigError,
    FetchError,
    NotFoundError,
    ParseError,
    PermanentFetchError,
    ProtocolError,
    RateLimitError,
    TimeoutFetchError,
    TransientFetchError,
    TransportError,
    ValidationError,
)

__all__ = [
    "AuthenticationError",
    "ConfigError",
    "FetchError",
    "NotFoundError",
    "ParseError",
    "PermanentFetchError",
    "ProtocolError",
    "RateLimitError",
    "TimeoutFetchError",
    "TransientFetchError",
    "TransportError",
    "ValidationError",
]
```

An explicit export list documents the supported import surface. It does not make other module attributes inaccessible, and the project should still avoid documenting private implementation details as stable API.

### 7.5 Example use by a caller

```python
from fetchkit import FetchError, TransientFetchError

try:
    result = get_resource("https://example.invalid/data")  # application adapter
except TransientFetchError:
    # Apply an application-owned retry policy only if the operation is safe.
    raise
except FetchError as exc:
    # Convert to an application response, structured log, or user-facing error.
    handle_fetch_failure(exc)
```

`get_resource` and `handle_fetch_failure` are placeholders supplied by the consuming application; the example demonstrates the catch ordering, not a complete HTTP client. Catch the more specific type first, then the root. Never log and re-raise at every layer.

## 8. Tests and practical exercises

The tests below assume the package layout shown in Section 7 and `pytest` installed. Save them as `tests/test_errors.py`. They use only the standard library and pytest; no network or vendor installation is required.

```python
import pickle

import pytest

from fetchkit import (
    AuthenticationError,
    ConfigError,
    FetchError,
    NotFoundError,
    PermanentFetchError,
    RateLimitError,
    TimeoutFetchError,
    TransientFetchError,
    TransportError,
    ValidationError,
)
from fetchkit.adapters.vendor import (
    VendorAuthenticationFailure,
    VendorConnectError,
    VendorReadTimeout,
    call_vendor,
)
from fetchkit.retry import run_with_retry


def test_validation_error_is_library_error_and_value_error() -> None:
    error = ValidationError("url scheme must be http or https")
    assert isinstance(error, FetchError)
    assert isinstance(error, ValueError)
    assert "http or https" in str(error)


def test_config_error_is_actionable() -> None:
    with pytest.raises(ConfigError, match="timeout must be greater than zero"):
        raise ConfigError("timeout must be greater than zero")


def test_vendor_connection_error_is_translated_and_chained() -> None:
    def fail() -> None:
        raise VendorConnectError("vendor internal details")

    with pytest.raises(TransportError) as captured:
        call_vendor(fail)

    assert isinstance(captured.value.__cause__, VendorConnectError)
    assert "connection failed" in str(captured.value)


def test_vendor_timeout_is_translated() -> None:
    def fail() -> None:
        raise VendorReadTimeout("vendor timeout")

    with pytest.raises(TimeoutFetchError) as captured:
        call_vendor(fail)
    assert isinstance(captured.value.__cause__, VendorReadTimeout)


def test_known_malformed_vendor_response_is_translated() -> None:
    from fetchkit.adapters.vendor import VendorMalformedResponseError
    from fetchkit import ProtocolError

    def fail() -> None:
        raise VendorMalformedResponseError("malformed response")

    with pytest.raises(ProtocolError) as captured:
        call_vendor(fail)
    assert isinstance(captured.value.__cause__, VendorMalformedResponseError)


def test_from_none_suppresses_displayed_context_deliberately() -> None:
    def load_credentials() -> None:
        try:
            raise PermissionError("private path /home/user/.secrets")
        except PermissionError:
            raise ConfigError("could not read configured credentials; check permissions") from None

    with pytest.raises(ConfigError) as captured:
        load_credentials()
    assert captured.value.__cause__ is None
    assert captured.value.__suppress_context__ is True
    assert isinstance(captured.value.__context__, PermissionError)
    assert "/home/user/.secrets" not in str(captured.value)


def test_authentication_error_does_not_leak_vendor_message() -> None:
    def fail() -> None:
        raise VendorAuthenticationFailure("Authorization: bearer secret-token")

    with pytest.raises(AuthenticationError) as captured:
        call_vendor(fail)
    assert "secret-token" not in str(captured.value)
    assert isinstance(captured.value.__cause__, VendorAuthenticationFailure)


def test_unknown_programming_error_is_not_translated() -> None:
    def fail() -> None:
        raise RuntimeError("implementation bug")

    with pytest.raises(RuntimeError, match="implementation bug"):
        call_vendor(fail)


def test_retry_repeats_transient_failure_for_idempotent_operation() -> None:
    calls = 0
    delays: list[float] = []

    def operation() -> str:
        nonlocal calls
        calls += 1
        if calls < 3:
            raise TransportError("temporary connection failure")
        return "ok"

    result = run_with_retry(operation, max_attempts=3, idempotent=True, sleep_fn=delays.append)
    assert result == "ok"
    assert calls == 3
    assert delays == [0.25, 0.5]


def test_retry_does_not_retry_permanent_error() -> None:
    calls = 0

    def operation() -> str:
        nonlocal calls
        calls += 1
        raise NotFoundError("resource not found")

    with pytest.raises(PermanentFetchError):
        run_with_retry(operation, max_attempts=4, idempotent=True, sleep_fn=lambda _: None)
    assert calls == 1


def test_non_idempotent_operation_is_not_retried() -> None:
    calls = 0

    def operation() -> str:
        nonlocal calls
        calls += 1
        raise RateLimitError("slow down", 0.1)

    with pytest.raises(RateLimitError):
        run_with_retry(operation, max_attempts=4, idempotent=False, sleep_fn=lambda _: None)
    assert calls == 1


def test_transient_exception_pickle_preserves_custom_attribute() -> None:
    original = RateLimitError("rate limit reached", 2.5)
    restored = pickle.loads(pickle.dumps(original))
    assert type(restored) is RateLimitError
    assert str(restored) == str(original)
    assert restored.retry_after == 2.5


def test_negative_retry_after_is_rejected() -> None:
    with pytest.raises(ValueError, match="finite, non-negative"):
        RateLimitError("slow down", -5.0)


def test_retry_argument_validation() -> None:
    with pytest.raises(ValueError, match="positive integer"):
        run_with_retry(lambda: "unused", max_attempts=0, idempotent=True)

    with pytest.raises(ValueError, match="positive integer"):
        run_with_retry(lambda: "unused", max_attempts=True, idempotent=True)


@pytest.mark.parametrize("retry_after", [-1, float("inf"), float("nan"), True, 10**1000])
def test_retry_after_rejects_invalid_values(retry_after: object) -> None:
    with pytest.raises(ValueError, match="finite, non-negative"):
        RateLimitError("slow down", retry_after)  # type: ignore[arg-type]
```

### Exercise: test `from None`

Add a test for a boundary that maps a low-level `PermissionError` to `ConfigError` using `raise ... from None`. Verify the public message is actionable and safe. Remember: `__cause__` is `None`; the original exception can still be available as `__context__`, with `__suppress_context__` true.

### Exercise: error contract table

For each public exception, document: stable meaning, structured attributes, whether the caller may retry, what must change before retrying, and which external code (if any) an application maps it to. Test those claims rather than only checking that an exception was raised.

### Exercise: exception aggregation

Create a batch parser that can either return a partial-success result or raise an `ExceptionGroup`. Explain which design better serves callers when each item can fail independently.

## 9. Common mistakes

The roadmap explicitly calls out these three mistakes; use them as review gates.

### Mistake 1: Raising bare `Exception` or relying on message text as the API

**Bad:**

```python
raise Exception("fetch failed")
```

Callers cannot safely distinguish an authentication failure from a retryable transport problem without parsing a string. **Better:** raise a documented subtype such as `AuthenticationError` or `TransportError`, and give the exception stable structured attributes when needed.

### Mistake 2: Leaking third-party exception types

**Bad:** a public `fetchkit` method documents `httpx.ConnectError` and lets vendor-specific exceptions escape directly. That couples users to a particular transport dependency and makes future replacement harder.

**Better:** catch the vendor's known exception at the adapter boundary and raise `TransportError(...) from exc`. Keep the cause for diagnosis, but promise the library-owned type in the public API. Do not translate unknown exceptions.

### Mistake 3: Exception classes that cannot be pickled

A subclass with custom constructor parameters may not restore its extra state using default exception pickling. Implement `__reduce__` when necessary and add a round-trip test for every exception that is expected to cross process boundaries. Do not promise picklability unless tested.

### Additional anti-patterns

- **Catching `Exception` and continuing:** hides bugs and may return corrupt partial results. Catch only expected categories at a clear boundary.
- **Catching `BaseException`:** may swallow `KeyboardInterrupt`, `SystemExit`, and cancellation. Almost never appropriate in ordinary library code.
- **Retrying every timeout:** the operation may have committed already, and retrying can duplicate side effects.
- **Logging at every layer:** produces duplicate stack traces and alert noise. Usually log once at the application boundary.
- **Including full request objects in messages:** leaks credentials and creates noisy, unstable error strings.
- **Using exceptions as an undocumented status protocol:** callers end up parsing messages or relying on accidental inheritance. Document type, attributes, and recovery guidance.

## 10. Self-check questions with model answers

### 1. Why organise exceptions by recovery action rather than by module?

Because callers need to decide what to do: fix input, update credentials, treat a resource as absent, retry safely, or investigate a defect. A module-based tree reflects internal implementation rather than stable caller needs. Recovery-based categories reduce coupling and let internals be refactored while the public error contract remains stable.

### 2. Show wrapping an `httpx` error while preserving the cause, and test `__cause__`.

With `httpx` installed, a production adapter can use the actual exception type:

```python
import httpx

from fetchkit.errors import TransportError


def call_httpx(client: httpx.Client, url: str) -> httpx.Response:
    try:
        return client.get(url)
    except httpx.ConnectError as exc:
        raise TransportError("connection failed; retry may succeed") from exc
```

A test can inject a fake client or monkeypatch `client.get` to raise `httpx.ConnectError`, then assert `isinstance(captured.value, TransportError)` and `isinstance(captured.value.__cause__, httpx.ConnectError)`. This adapter example requires the optional `httpx` dependency; the core examples above do not.

### 3. Make an exception with extra attributes that survives a `pickle` round-trip.

`TransientFetchError` stores `retry_after` and implements `__reduce__` to reconstruct the concrete subclass with both `str(self)` and the delay. The test in Section 8 verifies the restored type, message, and attribute. Pickle only trusted data and only make this a supported contract if the project needs cross-process transfer.

## 11. Summary and completion checklist

A good exception API is shallow, stable, documented, actionable, and organized around recovery. Translate known third-party failures at boundaries, preserve useful causes, keep messages free of secrets, and let unexpected bugs propagate. A transient classification is only one input to a retry decision; operation idempotency, timing, deadlines, and service guidance matter too.

- [ ] Every documented library failure has a library-owned root exception.
- [ ] Subclasses represent distinct caller recovery actions, not every internal module.
- [ ] Built-in `TypeError`/`ValueError` remain available for appropriate programming and validation contracts.
- [ ] Messages are actionable and do not expose secrets or unsanitized sensitive data.
- [ ] Vendor exceptions are translated selectively, with `raise ... from exc` where useful.
- [ ] Unknown bugs and cancellation are not swallowed or converted into transient failures.
- [ ] Retry logic is bounded and checks classification, idempotency, and deadlines.
- [ ] Tests cover public types, causes, attributes, safe messages, and pickling if promised.
- [ ] Logs are emitted at a deliberate boundary and are sanitized.
- [ ] Compatibility policy treats exception inheritance and exposed types as public API.

## 12. Authoritative references

### Source roadmap

- `roadmap-Design-Patterns-and-Library-API-Design.md`, Module 1.20, Lesson 08 — *Error hierarchies for libraries*. This lesson preserves the roadmap's focus on recovery-oriented categories, vendor-boundary translation, cause chains, pickling, retry taxonomy, observability, cancellation, security, and its three self-checks.
- `Roadmap_ptree.md`, Stage 1, Module 1.20 — confirms this lesson's place in the sequence between API compatibility and sans-I/O library design.

### Python documentation

- Python documentation, **Built-in Exceptions**: https://docs.python.org/3/library/exceptions.html
- Python documentation, **Errors and Exceptions**: https://docs.python.org/3/tutorial/errors.html
- Python documentation, **`pickle` — Python object serialization**: https://docs.python.org/3/library/pickle.html
- Python documentation, **`asyncio` exceptions and task cancellation**: https://docs.python.org/3/library/asyncio-exceptions.html
- Python documentation, **`asyncio.TaskGroup` and task groups**: https://docs.python.org/3/library/asyncio-task.html#task-groups
- Python documentation, **`ExceptionGroup` and `except*`**: https://docs.python.org/3/library/exceptions.html#ExceptionGroup
- pytest documentation, **Assertions about expected exceptions**: https://docs.pytest.org/en/stable/how-to/assert.html#assertions-about-expected-exceptions

### Design guidance

- Use the exception contract as a versioned public API: stable names, inheritance, attributes, and documented recovery semantics matter more than exact incidental wording.
- For vendor adapters, consult the selected dependency's official exception documentation and map only the documented failure types whose semantics are understood.
- For distributed services, align retry decisions with idempotency, deadlines, rate-limit guidance, and the service's published error semantics; do not infer retry safety from HTTP status or exception class alone.
