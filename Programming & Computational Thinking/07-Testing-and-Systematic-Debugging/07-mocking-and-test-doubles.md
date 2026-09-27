# Mocking and Test Doubles

## Learning Objectives

By the end of this chapter, you should be able to explain why tests sometimes replace real dependencies, distinguish dummy/stub/fake/mock/spy test doubles, use Python's `unittest.mock` safely, patch the name used by the system under test, control failures and nondeterminism, use `pytest.monkeypatch`, design dependency-injected code, and choose between mocks, fakes, temporary resources, contract tests, integration tests, and end-to-end tests. You should also be able to apply these ideas to APIs, databases, queues, cloud services, data pipelines, ML systems, LLM applications, and agentic AI systems.

**Roadmap position:** Stage 1 — Programming & Computational Thinking, Module 1.7 — Testing and Systematic Debugging.

This chapter assumes you already know the basics of unit tests, Arrange-Act-Assert (AAA), fixtures, parametrization, boundary/invalid-input tests, regression tests, debugging, tracebacks, and logging. It does not repeat those chapters; it connects them to test doubles.

## 1. The Problem: Testing Dependencies

A small function can become difficult to test when it depends on the outside world:

```text
Application code
    ↓
Database
    ↓
External API
    ↓
Payment service
    ↓
Email service
```

A test that uses every real dependency may be slow, expensive, flaky, hard to reproduce, dependent on a network connection or credentials, sensitive to external state, capable of creating side effects, and difficult to force into rare failure paths such as timeouts or rate limits.

The core idea is simple:

> Sometimes we want to test our code while controlling what its dependencies do.

This is not an argument for mocking everything. It is an argument for controlling boundaries deliberately.

### Example

Suppose `register_user()` saves a user and sends an email. A unit test that calls the production email provider can accidentally send a real email. A better unit test can replace the email boundary with a controlled test double, while a separate integration or contract test validates the real integration.

### Testing-layer relationship

```text
Unit test
  → isolate business logic with selected test doubles

Integration test
  → exercise real component boundaries

Contract test
  → check that a dependency's interface matches assumptions

End-to-end test
  → exercise a realistic user/system path
```

The same dependency may be mocked in a unit test and real in an integration test. The test layer determines the purpose.

## 2. What Is a Test Double?

A **test double** is a replacement for a real dependency used during testing. The phrase is broader than “mock.”

```text
Production
Application → Real dependency

Test
Application → Test double
```

The double may exist to satisfy a parameter, return controlled data, provide a lightweight working implementation, record interactions, or observe calls.

### Why test doubles exist

They help you control a dependency's behavior, isolate a unit, make tests deterministic, trigger rare failures, remove external side effects, and keep fast feedback loops.

### Terminology caveat

Testing literature and teams do not use these words with perfect uniformity. The following distinctions are useful engineering concepts, not a universal legal taxonomy.

### Simple analogy

Think about training a cashier. You might use an empty prop card terminal (dummy), a simulator that always returns “approved” (stub), a small working payment simulator (fake), a recorder that verifies the cashier used the terminal correctly (mock), or a device that lets the real terminal behavior run while observing it (spy).

### Production consideration

Choose the double based on the test's purpose. The more a test needs to prove real integration behavior, the more likely a real dependency, emulator, sandbox, or contract test is appropriate.

## 3. Types of Test Doubles

| Type | Main purpose | Usually controls behavior? | Usually verifies interaction? | Working implementation? |
|---|---|---:|---:|---:|
| Dummy | Satisfy a required parameter or dependency slot | Sometimes | No | No |
| Stub | Return predetermined responses | Yes | Usually no | No |
| Fake | Provide a simplified working implementation | Yes | Usually not the main purpose | Yes |
| Mock | Replace a dependency and record/verify interactions | Yes | Yes | No, unless configured/wrapped |
| Spy | Observe interactions while real behavior may execute | Sometimes | Yes | Often yes |

A single object can sometimes play multiple conceptual roles depending on how it is configured. For example, a `Mock` object can be used as a stub by setting `return_value`, or as an interaction verifier by using `assert_called_once_with()`. The conceptual role comes from how the test uses it.

### Dummy

A **dummy** is supplied because the production interface requires something, but the particular test does not need to use it.

```python
from typing import Protocol

class Notifier(Protocol):
    def send(self, message: str) -> None: ...


def create_user(user_repository, notifier: Notifier, name: str) -> int:
    # In this simplified example the notifier is not used.
    return user_repository.insert({"name": name})
```

The test can provide a placeholder notifier:

```python
class DummyNotifier:
    def send(self, message: str) -> None:
        raise AssertionError("Notifier should not be used in this test")
```

A dummy is different from a mock because the purpose is not to assert calls. In some test styles, a very small `object()` is enough.

**Use when:** the dependency is structurally required but irrelevant to the behavior under test.

**Do not use when:** you actually need controlled responses or interaction assertions.

**Common misuse:** calling a “mock” a dummy simply because it is present. Name the role by its purpose.

**Production use:** conceptually, dummies are mostly a testing concern rather than a production component.

### Stub

A **stub** supplies predetermined behavior or data. It answers a question the system asks.

```python
def get_user_name(user_id: int, user_repository) -> str:
    user = user_repository.get_user(user_id)
    return user["name"]
```

A stub can provide a deterministic record:

```python
class StubUserRepository:
    def get_user(self, user_id: int) -> dict[str, object]:
        return {"id": user_id, "name": "Alice"}
```

Test:

```python
def test_get_user_name_uses_repository_response():
    repository = StubUserRepository()
    assert get_user_name(1, repository) == "Alice"
```

Stubs are useful for success results, controlled failure results, empty results, feature flags, clocks, authentication providers, and API responses. A stub usually does not need to verify that a particular call happened; the test can verify the result.

**Advantages:** deterministic, simple, readable, fast.

**Disadvantages:** the stub may become unrealistic, and it can fail to represent production edge cases.

**Production example:** a service may depend on a configuration provider. Unit tests can use a stub provider that returns known configuration values.

### Fake

A **fake** is a lightweight, working implementation that follows the same general role as the real dependency but is simpler.

Example boundary:

```text
Production: PostgreSQLUserRepository
Test:       InMemoryUserRepository
```

```python
class InMemoryUserRepository:
    def __init__(self) -> None:
        self._users: dict[int, dict[str, object]] = {}
        self._next_id = 1

    def insert(self, user: dict[str, object]) -> int:
        user_id = self._next_id
        self._next_id += 1
        self._users[user_id] = {**user, "id": user_id}
        return user_id

    def get(self, user_id: int) -> dict[str, object]:
        return self._users[user_id]
```

A fake is more behavior-rich than a simple stub. It can be useful for integration-like tests without requiring a database server. But a fake can diverge from production behavior: SQL constraints, transaction semantics, isolation, indexes, serialization, permissions, and driver quirks are not automatically reproduced.

**Use when:** the simplified implementation gives meaningful behavior and is cheap to run.

**Do not use when:** correctness depends on details the fake cannot represent, such as SQL dialect behavior or a real cloud service's consistency semantics.

**Common misuse:** treating a fake as proof that the production dependency works. It is not.

### Mock

A **mock** replaces a dependency, can control its behavior, and records interactions so the test can verify them.

For example:

```python
email_service.send(...)
```

A mock can verify whether `send()` was called, with what arguments, how many times, and sometimes in what order.

Two verification styles matter:

**State verification** asks what state/result the system produced:

```python
assert result == expected_result
```

**Interaction verification** asks how the system collaborated with a dependency:

```python
email_service.send.assert_called_once_with("alice@example.test", "Welcome")
```

Interaction assertions are useful when the interaction is part of the contract: for example, a payment must be charged exactly once. But excessive assertions can lock a test to internal implementation details.

**Production consideration:** mocks are excellent for isolated behavior and failure simulation, but they do not prove that a real API, database, queue, or model provider works.

### Spy

A **spy** observes calls while the underlying behavior is allowed to execute, depending on the implementation and framework. A spy is useful when you need the real behavior plus evidence about an interaction.

In Python, you can build a spy explicitly or use a mock with `wraps`:

```python
from unittest.mock import Mock

class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b

calculator = Calculator()
spy = Mock(wraps=calculator.add)

assert spy(2, 3) == 5
spy.assert_called_once_with(2, 3)
```

This differs from a pure mock because the wrapped behavior executed. A spy also differs from a stub: the main purpose of a stub is to control the response; the main purpose of a spy is observation.

**Caution:** spies can still couple tests to interaction details. Use them where that observation carries meaning.

## 4. State Verification vs Interaction Verification

The most important design question is not “Which assertion is easiest?” It is “What behavior am I trying to verify?”

### State verification

Test the externally observable result or state transition:

```python
assert account.balance == 90
assert response.status == "accepted"
assert output == expected_output
```

This often survives refactoring because the implementation can change while the behavior stays the same.

### Interaction verification

Test the collaboration itself:

```python
payment_client.charge.assert_called_once_with(order_id="A-100", amount_cents=5000)
```

This is valuable when the interaction itself matters: exactly-once charging, publishing a specific message, invalidating a cache, or calling an authorization boundary.

### Trade-off

```text
More state-focused → often more refactor-friendly
More interaction-focused → often more precise about collaboration
Too much interaction detail → brittle tests
Too little interaction checking → may miss important side effects
```

A strong test suite mixes these styles according to contract, not fashion.

## 5. Python's `unittest.mock`

Python's standard library provides `unittest.mock` for creating mocks, patching objects, configuring behavior, and checking interactions. The core tools in this chapter are standard-library features, so the examples do not require a paid service or a third-party mocking package.

Core APIs covered here include:

```python
from unittest.mock import (
    ANY,
    DEFAULT,
    AsyncMock,
    MagicMock,
    Mock,
    PropertyMock,
    call,
    create_autospec,
    mock_open,
    patch,
    sentinel,
)
```

Other useful ideas include `wraps`, `spec`, `spec_set`, and the `start()`/`stop()` lifecycle methods of patchers. Prefer context managers or decorators when possible so cleanup is automatic.

## 6. `Mock`

`Mock` is the general-purpose mock object. It creates callable objects and child mocks on demand, records calls, and supports configurable behavior.

### Basic creation

```python
from unittest.mock import Mock

mock = Mock(name="payment_client")
mock.charge.return_value = {"status": "accepted"}

result = mock.charge("order-123", 5000)
assert result["status"] == "accepted"
mock.charge.assert_called_once_with("order-123", 5000)
```

### Important attributes and methods

- `return_value`: response returned by calling the mock.
- `side_effect`: exception, callable, or iterable controlling calls.
- `called`: whether it has been called.
- `call_count`: number of direct calls.
- `call_args`: arguments from the most recent call.
- `call_args_list`: list of direct calls.
- `method_calls`: calls to methods/attributes below the mock.
- `mock_calls`: a broader record including chained child calls.
- `reset_mock()`: clears call history and related state; it does not automatically replace your configured behavior.

Assertions include `assert_called()`, `assert_called_once()`, `assert_called_with()`, `assert_called_once_with()`, `assert_any_call()`, `assert_has_calls()`, and `assert_not_called()`.

### Nested mocks

```python
client = Mock()
client.users.get.return_value = {"id": 1}
```

Nested mocks are convenient but can hide design problems. A chain like `client.users.accounts.billing.fetch()` is often a signal to simplify the production interface rather than write a deeper mock.

## 7. `MagicMock`

`MagicMock` is a `Mock` with support for many Python magic/dunder methods, such as context-manager methods and special methods used by containers and iteration.

Examples:

```python
from unittest.mock import MagicMock

items = MagicMock()
items.__len__.return_value = 3
items.__getitem__.side_effect = ["a", "b", "c"]

assert len(items) == 3
assert items[0] == "a"
```

### Context manager example

```python
from unittest.mock import MagicMock

resource = MagicMock()
resource.__enter__.return_value = "HANDLE"

with resource as handle:
    assert handle == "HANDLE"

resource.__enter__.assert_called_once()
resource.__exit__.assert_called_once()
```

### When to use

Use ordinary `Mock` when you only need normal attributes/calls. Use `MagicMock` when Python protocols such as `with`, iteration, indexing, length, or similar dunder methods are part of the code under test. Avoid choosing `MagicMock` automatically; the extra behavior is not inherently better.

## 8. `return_value`

`return_value` says what a mock returns when called.

```python
mock = Mock()
mock.return_value = 42
assert mock() == 42
```

For a method:

```python
client = Mock()
client.fetch_user.return_value = {"id": 1, "name": "Alice"}
```

This is one of the simplest forms of stub-like behavior. It becomes especially useful when a dependency's output drives the code under test.

### Nested return values

```python
service = Mock()
service.client.fetch.return_value = {"ok": True}
```

This works, but deep chains are a design warning. Consider dependency injection of a narrow interface instead of exposing a large object graph to the unit.

## 9. `side_effect`

`side_effect` controls what happens on a call beyond a single fixed `return_value`. It can be:

1. an exception class or instance;
2. a callable;
3. an iterable of results/exceptions.

### Exception

```python
client.fetch.side_effect = TimeoutError("service timed out")
```

### Callable

```python
def respond(user_id: int) -> dict[str, object]:
    if user_id == 1:
        return {"id": 1, "name": "Alice"}
    raise KeyError(user_id)

client.fetch.side_effect = respond
```

### Iterable

```python
client.fetch.side_effect = [
    TimeoutError("first attempt"),
    {"status": "ok"},
]
```

A call consumes the next iterable item. This is useful for retry tests.

### Common mistake

Do not confuse a callable `side_effect` with the result of calling it. The mock calls the function later. Also remember that an iterable side effect is stateful across calls; a reused mock may therefore behave differently after prior tests unless its lifecycle is controlled.

## 10. Call Assertions

Use interaction assertions only when they express a meaningful contract.

| API | Meaning |
|---|---|
| `assert_called()` | Called at least once |
| `assert_called_once()` | Called exactly once |
| `assert_called_with(...)` | Most recent call matched these arguments |
| `assert_called_once_with(...)` | Exactly one call, with these arguments |
| `assert_any_call(...)` | At least one call matched |
| `assert_has_calls([...])` | Required calls appear in call history; order rules depend on `any_order` |
| `assert_not_called()` | No call occurred |

### Inspecting call data

```python
mock.call_args
mock.call_args_list
mock.method_calls
mock.mock_calls
```

`call_args_list` is useful when a function is intentionally called repeatedly.

```python
from unittest.mock import Mock

worker = Mock()
worker(1)
worker(2)
worker(3)

assert worker.call_count == 3
assert [args.args[0] for args in worker.call_args_list] == [1, 2, 3]
```

### `reset_mock()`

```python
worker.reset_mock()
assert worker.call_count == 0
```

Resetting call history can be useful inside a test that intentionally separates phases, but creating a fresh mock per test is often clearer.

## 11. `call`, `ANY`, `sentinel`, and `DEFAULT`

`call` builds expected call objects.

```python
from unittest.mock import call

expected = [call("Alice", 10), call("Bob", 20)]
```

`ANY` matches any value in an argument position:

```python
from unittest.mock import ANY

mailer.send.assert_called_once_with("alice@example.test", ANY, "Hello")
```

Use `ANY` when a value is nondeterministic but its exact value is not the contract. Do not use it everywhere; a broad matcher can weaken a useful assertion.

`sentinel` creates unique, readable marker objects:

```python
from unittest.mock import sentinel

request_id = sentinel.request_id
client.send(request_id)
client.send.assert_called_once_with(sentinel.request_id)
```

`DEFAULT` is a sentinel used by `unittest.mock` configuration patterns, especially when a `side_effect` function should sometimes fall back to the mock's configured `return_value`:

```python
from unittest.mock import DEFAULT, Mock

mock = Mock(return_value="normal")

def effect(x: int):
    if x < 0:
        return "special"
    return DEFAULT

mock.side_effect = effect
assert mock(-1) == "special"
assert mock(2) == "normal"
```

## 12. `patch`

Patching means temporarily replacing an object reachable by code. The replacement is restored when the context manager or decorator exits.

```python
from unittest.mock import patch

with patch("service.get_current_user") as mock_get_user:
    mock_get_user.return_value = {"id": 1}
    ...
```

Useful forms include:

```python
patch(target, new=...)
patch.object(target, attribute, new=...)
patch.dict(mapping, values=...)
patch.multiple(target, ...)
```

A patcher can also be started/stopped manually:

```python
patcher = patch("service.client")
mock_client = patcher.start()
try:
    ...
finally:
    patcher.stop()
```

Manual lifecycle code is more error-prone. Prefer `with patch(...)` or a decorator unless manual control is required.

### Decorator

```python
@patch("service.client")
def test_process(mock_client):
    ...
```

Patching is most powerful when you understand Python imports and names. That leads to the critical rule in the next section.

## 13. Patching Where the Object Is Used

The rule to memorize is:

> **Patch where the object is looked up, not necessarily where it was originally defined.**

Suppose you have:

`utils.py`

```python
def get_data() -> str:
    return "real-data"
```

`service.py`

```python
from utils import get_data


def process() -> str:
    return get_data()
```

When Python executes `from utils import get_data`, `service.py` receives its own name `get_data` bound to the function object. Patching `utils.get_data` later does not automatically rewrite the already-bound name in `service`.

Wrong target for a unit test of `service.process()`:

```python
with patch("utils.get_data", return_value="fake"):
    assert service.process() == "real-data"
```

Correct target:

```python
with patch("service.get_data", return_value="fake"):
    assert service.process() == "fake"
```

### Debugging a patch

Ask: **What exact name does the system under test resolve at runtime?** Then patch that name.

The same principle applies to `pytest.monkeypatch.setattr()`. This is one of the most important practical skills in Python mocking.

## 14. `patch.object()`

`patch.object(target, attribute, ...)` replaces an attribute directly on an object or class.

```python
class TokenClient:
    def get_token(self) -> str:
        return "real-token"

client = TokenClient()

with patch.object(client, "get_token", return_value="test-token"):
    assert client.get_token() == "test-token"
```

It can patch methods, attributes, or class attributes.

For class-level patching:

```python
with patch.object(TokenClient, "get_token", return_value="test-token"):
    assert TokenClient().get_token() == "test-token"
```

When patching methods on classes, `autospec=True` can be important because it preserves the method signature and binding behavior more faithfully.

## 15. `patch.dict()`

`patch.dict()` temporarily changes a mapping and restores it afterward. It is especially useful for configuration dictionaries and `os.environ`.

```python
import os
from unittest.mock import patch

with patch.dict(os.environ, {"APP_MODE": "test"}):
    assert os.environ["APP_MODE"] == "test"

# Original environment is restored here.
```

You can use `clear=True` when you explicitly want to replace the mapping's visible contents for the patch scope. Use this carefully because clearing global configuration can create confusing test conditions.

Never place real credentials, API keys, customer identifiers, or production tokens in a test fixture. Use placeholders or generated test values.

## 16. `patch.multiple()`

`patch.multiple()` lets you patch several attributes on one target in a single call.

```python
from unittest.mock import DEFAULT, patch

class Gateway:
    timeout = 5

    def charge(self):
        ...

with patch.multiple(Gateway, timeout=1, charge=DEFAULT) as patched:
    patched["charge"].return_value = True
    assert Gateway.timeout == 1
    assert Gateway().charge() is True
```

This can reduce repetitive patch blocks. Use it when the grouped changes form one coherent test setup. Separate patches are often clearer when each dependency has a different rationale.

## 17. `autospec`, `spec`, `spec_set`, and `create_autospec`

Unrestricted mocks are permissive. That flexibility can hide interface mistakes.

Suppose production code exposes:

```python
class EmailClient:
    def send_email(self, to: str, subject: str, body: str) -> None:
        ...
```

A loose mock can allow code to accidentally call `send_email("a", "b")` without immediately exposing that the signature is wrong.

### `autospec=True`

```python
with patch("service.EmailClient", autospec=True) as mock_client_cls:
    client = mock_client_cls.return_value
    ...
```

Autospeccing creates mocks based on the target's interface and signatures. It helps catch typos and incorrect calls, though it does not guarantee semantic compatibility with the real system.

### `create_autospec()`

```python
from unittest.mock import create_autospec

client = create_autospec(EmailClient, instance=True)
client.send_email("a@example.test", "Subject", "Body")
```

### `spec`

```python
mock_client = Mock(spec=EmailClient)
```

`spec` constrains attributes to those available on the specification object. It is useful for catching misspelled or nonexistent members, but it is not the same as full signature enforcement in every situation.

### `spec_set`

```python
mock_client = Mock(spec_set=EmailClient)
```

`spec_set` is stricter about setting attributes as well as accessing them.

### Rule of thumb

Use autospeccing at important boundaries when permissive mocks could hide interface drift. Keep the tests readable, and remember that a spec models the Python-side interface, not the behavior of an external service.

## 18. `PropertyMock`

Properties are accessed as attributes rather than called as methods, so a specialized `PropertyMock` is useful when patching a property on a class.

```python
from unittest.mock import PropertyMock, patch

class User:
    @property
    def is_admin(self) -> bool:
        return False

user = User()
with patch.object(type(user), "is_admin", new_callable=PropertyMock) as mock_property:
    mock_property.return_value = True
    assert user.is_admin is True
    mock_property.assert_called_once_with()
```

The class-level target matters because descriptors such as `property` live on the class. Property mocking can be useful, but frequent property patches may indicate the production design is exposing too much hidden behavior.

## 19. `mock_open()`

`mock_open()` creates a mock suitable for replacing `open()` and supports normal `with open(...)` patterns.

```python
from unittest.mock import mock_open, patch


def read_config(path: str) -> str:
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def test_read_config():
    opener = mock_open(read_data="mode=test\n")
    with patch("builtins.open", opener):
        assert read_config("config.txt") == "mode=test\n"
    opener.assert_called_once_with("config.txt", "r", encoding="utf-8")
```

For writing:

```python
from unittest.mock import mock_open, patch


def write_report(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)


def test_write_report():
    opener = mock_open()
    with patch("builtins.open", opener):
        write_report("report.txt", "hello")

    opener.assert_called_once_with("report.txt", "w", encoding="utf-8")
    opener().write.assert_called_once_with("hello")
```

`mock_open(read_data=...)` is intentionally a simple model. For tests where filesystem semantics matter, a real temporary directory/file is often better. If a project needs a more realistic in-memory filesystem, third-party libraries such as `pyfakefs` can be evaluated separately; they are not part of Python's standard library.

## 20. `AsyncMock`

`AsyncMock` is designed for asynchronous callables. When an async function is replaced with an ordinary `Mock`, the test may accidentally produce a non-awaitable value or fail to verify the `await` itself.

```python
from unittest.mock import AsyncMock

async def fetch_user(user_id: int) -> dict[str, object]:
    ...


async def test_fetch_user():
    mock_fetch = AsyncMock(return_value={"id": 1, "name": "Alice"})
    result = await mock_fetch(1)

    assert result["name"] == "Alice"
    mock_fetch.assert_awaited_once_with(1)
```

Relevant await APIs include:

```python
assert_awaited()
assert_awaited_once()
assert_awaited_with(...)
assert_awaited_once_with(...)
await_count
await_args
await_args_list
```

### Async context managers

`AsyncMock` and `MagicMock` can also model async context-manager methods such as `__aenter__` and `__aexit__`.

### Agentic AI relevance

Async API clients, asynchronous tool execution, async database clients, search tools, and event-driven agent orchestration frequently need `AsyncMock`. But the mock only verifies your orchestration behavior; it does not validate the actual provider's latency, protocol, or reliability.

## 21. Mocking Failures and Retries

A major benefit of controlled dependencies is the ability to test failures that are rare or expensive in real life. Examples include:

- API timeout;
- HTTP 500/503;
- authentication failure;
- malformed response;
- database connection failure;
- file not found;
- rate limiting;
- retryable errors.

### Example

```python
from unittest.mock import Mock

client = Mock()
client.fetch.side_effect = TimeoutError("temporary outage")
```

The application can then verify its fallback path:

```python

def load_profile(client) -> dict[str, str]:
    try:
        return client.fetch()
    except TimeoutError:
        return {"status": "degraded"}
```

```python
def test_load_profile_handles_timeout():
    client = Mock()
    client.fetch.side_effect = TimeoutError("temporary outage")

    assert load_profile(client) == {"status": "degraded"}
```

### Retry example

```python
from unittest.mock import Mock


def fetch_with_retry(client, attempts: int = 3):
    last_error = None
    for _ in range(attempts):
        try:
            return client.fetch()
        except TimeoutError as exc:
            last_error = exc
    raise last_error


def test_retries_then_succeeds():
    client = Mock()
    client.fetch.side_effect = [TimeoutError("temporary"), {"status": "ok"}]

    assert fetch_with_retry(client, attempts=2) == {"status": "ok"}
    assert client.fetch.call_count == 2
```

Test the number of attempts when retry count is part of the contract, and test the final result/error. Do not assert arbitrary internal sleep calls unless delay behavior itself is important; a separate clock/backoff policy test can be clearer.

## 22. Mocking Time and Randomness

Time, randomness, UUIDs, and timestamps create nondeterministic inputs. Nondeterministic inputs can make tests flaky even when production code is correct.

### Prefer dependency injection

Instead of hard-coding a call to `datetime.now()`, define a narrow clock dependency:

```python
from datetime import datetime, timezone
from typing import Protocol

class Clock(Protocol):
    def now(self) -> datetime: ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)
```

The test can provide a deterministic clock:

```python
class FixedClock:
    def now(self) -> datetime:
        return datetime(2030, 1, 2, tzinfo=timezone.utc)
```

This is often easier to understand than patching many low-level time APIs.

### Randomness

Give the random source a seam:

```python
from secrets import token_hex

def make_id(token_source=token_hex) -> str:
    return token_source(4)
```

Then a test can pass a deterministic function. The same idea works for UUID factories and timestamp providers.

### Trade-off

Patching a time API can be useful in legacy code, but dependency injection generally makes the production design clearer and keeps tests focused on behavior rather than import mechanics.

## 23. Mocking Environment Variables

Environment variables are global process state. Tests that modify them should restore them after the test.

Using `patch.dict()`:

```python
import os
from unittest.mock import patch


def is_feature_enabled() -> bool:
    return os.getenv("FEATURE_X", "off") == "on"


def test_feature_enabled():
    with patch.dict(os.environ, {"FEATURE_X": "on"}):
        assert is_feature_enabled() is True
```

Using pytest:

```python
def test_feature_enabled(monkeypatch):
    monkeypatch.setenv("FEATURE_X", "on")
    assert is_feature_enabled() is True
```

For safety, use fake values such as `test-token` and do not store real secrets in source control, tests, CI logs, or mock fixtures.

## 24. Mocking Filesystems

There are several strategies, and they serve different purposes:

| Strategy | Good for | Limitation |
|---|---|---|
| `mock_open` | Checking calls and simple file contents | Simplified filesystem semantics |
| `tempfile`/pytest temporary paths | Real file behavior without persistent state | Still uses the real OS filesystem |
| `pathlib` + temporary directory | Integration-like filesystem behavior | Requires filesystem operations |
| `pyfakefs` | More realistic in-memory filesystem modeling | Third-party dependency |

### Temporary file example

```python
from pathlib import Path


def save_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def test_save_text(tmp_path):
    target = tmp_path / "result.txt"
    save_text(target, "hello")
    assert target.read_text(encoding="utf-8") == "hello"
```

This can be stronger than `mock_open` when the contract involves actual file creation, paths, permissions, newline behavior, or interactions among multiple files.

The testing question is: **Do I need to verify that my code called `open()` correctly, or that the resulting filesystem behavior is correct?**

## 25. Mocking Databases

Consider the boundary:

```text
Application → Repository → Database
```

A unit test can replace the repository with a stub or mock. That isolates business logic.

```python
from unittest.mock import Mock


def activate_user(user_id: int, repository) -> None:
    user = repository.get(user_id)
    if user["status"] != "active":
        repository.update_status(user_id, "active")


def test_activate_user_updates_inactive_user():
    repository = Mock()
    repository.get.return_value = {"id": 1, "status": "inactive"}

    activate_user(1, repository)

    repository.update_status.assert_called_once_with(1, "active")
```

But this test does **not** prove the SQL is valid, constraints behave correctly, transactions commit, indexes work, or the production driver behaves as expected. Those belong in repository integration tests using a controlled database environment, a real test database, or an appropriate emulator where available.

A common healthy split is:

```text
Business logic unit tests → mock/stub repository
Repository integration tests → real database/test instance
Service-level tests → selected real boundaries + controlled external systems
```

## 26. Mocking HTTP APIs

For an HTTP client, unit tests can control responses without making a network call. Test success and failure shapes, not only the happy path.

```python
from unittest.mock import Mock


def get_payment_status(client, payment_id: str) -> str:
    response = client.get(payment_id)
    if response.status_code == 404:
        return "missing"
    if response.status_code >= 500:
        raise RuntimeError("payment provider unavailable")
    data = response.json()
    return data["status"]


def test_payment_status_success():
    client = Mock()
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"status": "paid"}
    client.get.return_value = response

    assert get_payment_status(client, "p-1") == "paid"
```

Also test timeout, 401/403, 429, 500/503, malformed JSON, missing fields, and retryable failures.

**Critical limitation:** a mocked API test validates your client logic against your simulated response. It does not validate the current external API contract. Use integration tests, sandboxes, or contract tests for that.

## 27. Mocking Message Queues

For queue producers and consumers, unit tests can replace the broker client:

```text
Producer → publish(message)
Consumer ← consume(message)
```

Unit tests can verify message construction, acknowledgement decisions, retries, and dead-letter routing logic.

```python
from unittest.mock import Mock


def process_message(message: dict[str, str], broker) -> None:
    try:
        handle_order(message)
    except ValueError:
        broker.publish("dead-letter", message)
        broker.ack(message)
        return
    broker.ack(message)


def handle_order(message: dict[str, str]) -> None:
    ...
```

A higher-level test should use a real broker or an appropriate test instance/emulator when delivery semantics, visibility timeouts, ordering, duplicate delivery, or acknowledgement semantics matter. A mock cannot prove those distributed-system behaviors.

## 28. Mocking Cloud Services

Cloud systems often expose object storage, secret managers, queues, notification services, and other APIs. A practical strategy is:

```text
Unit test → mock/stub/fake dependency
Integration test → emulator/test environment/controlled service
Production → real service
```

Use generic test data and avoid cloud credentials in the test suite. For critical integrations, use an isolated cloud test account or sandbox with least-privilege credentials.

A mocked object-store call can validate that your application uploads the expected bytes and metadata. It does not prove bucket policies, permissions, encryption configuration, region settings, network rules, or the real SDK/service interaction are correct. Those require integration or infrastructure-level validation.

## 29. Dependency Injection and Testability

A major lesson from mocking is architectural: code is easier to test when dependencies are explicit.

Hard-coded dependency:

```python
def process():
    client = RealApiClient()
    return client.fetch()
```

Dependency-injected design:

```python
def process(client):
    return client.fetch()
```

Now the test can supply a stub, fake, or mock without patching globals.

Common forms:

- **Function injection:** pass a dependency as a function argument.
- **Parameter injection:** pass a boundary object for the operation.
- **Constructor injection:** store the dependency on a class created with that dependency.
- **Protocol-based injection:** depend on a small interface rather than a concrete implementation.

```python
class UserService:
    def __init__(self, repository, notifier):
        self.repository = repository
        self.notifier = notifier
```

Good architecture often reduces the amount of patching required. If a test needs ten patches to create one scenario, inspect the design before adding an eleventh patch.

## 30. Protocols and Mocking

Python's `typing.Protocol` can express a structural interface: code cares that an object provides the required methods, not that it inherits from a specific base class.

```python
from typing import Protocol

class UserRepository(Protocol):
    def get_user(self, user_id: int) -> dict[str, object]: ...
```

Production:

```python
class ProductionRepository:
    def get_user(self, user_id: int) -> dict[str, object]:
        ...
```

Test fake:

```python
class InMemoryRepository:
    def __init__(self, users: dict[int, dict[str, object]]) -> None:
        self.users = users

    def get_user(self, user_id: int) -> dict[str, object]:
        return self.users[user_id]
```

A mock can also be created from the protocol or another concrete spec. Narrow protocols improve testability because they define smaller boundaries. This is not a complete typing lesson; the testing takeaway is to make dependencies explicit, narrow, and substitutable.

## 31. Mocking vs Pure Functions

Pure functions often need little or no mocking because they do not depend on external state.

```python
def calculate_total(price: int, tax_rate: float) -> int:
    return round(price * (1 + tax_rate))
```

Compare that with:

```python
def calculate_total_from_remote_rules(order_id, api_client, clock, database):
    ...
```

The second design has multiple external seams and therefore requires more test setup.

A valuable architectural principle is:

> The more business logic is isolated from external side effects, the less mocking is required.

Push I/O to boundaries; keep decision logic in small, deterministic functions where practical. This often produces simpler tests than an architecture built around pervasive mocks.

## 32. Over-Mocking

**Over-mocking** means using so many mocks, patches, and interaction assertions that tests become coupled to implementation details instead of behavior.

Symptoms:

- huge mock setup;
- many call assertions;
- tests fail after harmless refactoring;
- tests pass while integrations are broken;
- deeply nested `return_value` chains;
- complex fixture factories.

Bad pattern:

```python
def test_checkout():
    service = Mock()
    service.user_repo.get.return_value = Mock()
    service.user_repo.get.return_value.orders.return_value = Mock()
    service.payment.authorize.return_value = True
    service.logger.info.assert_not_called()
    ...
```

Better design: inject narrow dependencies and verify the checkout behavior. Use an interaction assertion where the payment charge itself is a meaningful contract.

```python
def test_checkout_charges_once(payment_client, order_repo):
    order_repo.get.return_value = {"id": "o-1", "amount_cents": 5000}
    payment_client.charge.return_value = {"status": "accepted"}

    result = checkout("o-1", order_repo, payment_client)

    assert result == "accepted"
    payment_client.charge.assert_called_once_with("o-1", 5000)
```

The goal is not “zero mocks.” The goal is a test that would remain correct if the implementation were refactored without changing behavior.

## 33. Mock Hell

“Mock hell” is an informal term for tests dominated by complicated mock setup.

Typical signs:

```text
mock.a.return_value.b.return_value.c.return_value.d.return_value...
```

### Why it happens

Often the production code exposes a large dependency graph instead of one narrow interface. The test then mirrors that graph.

### Better approach

1. Identify the actual business contract.
2. Introduce a narrow interface.
3. Inject the interface.
4. Prefer a fake or simple stub when behavior is straightforward.
5. Keep one mock at a boundary where interaction matters.

If a test takes more code to configure than the production behavior takes to implement, that is a strong signal to inspect the design.

## 34. When Not to Mock

Use a real or temporary dependency when the dependency itself is what you need to validate. Examples include:

- pure functions;
- temporary files/directories;
- repository integration and SQL;
- serialization/deserialization compatibility;
- API contract tests;
- critical authentication flows;
- important database transactions;
- queue delivery semantics;
- critical integration paths.

### Test pyramid connection

```text
          E2E
           ↑
     Integration
           ↑
       Contract
           ↑
         Unit
```

Unit tests provide fast, isolated feedback. Integration and contract tests verify real boundaries. End-to-end tests validate a realistic system path but are usually more expensive.

There is no universal rule to always mock or never mock. Choose the test layer that can answer the question you actually have.

## 35. pytest + `unittest.mock`

pytest and `unittest.mock` work well together. A pytest test can create a `Mock`, use `patch`, request a fixture, parametrize scenarios, and use `pytest.raises`.

```python
import pytest
from unittest.mock import Mock


def load_name(client):
    response = client.get()
    if response["status"] != "ok":
        raise RuntimeError("load failed")
    return response["name"]


def test_load_name(client_fixture):
    assert load_name(client_fixture) == "Alice"
```

Fixtures can build reusable mocks, but fixture scope should match the state being shared. A mock that records calls is usually best created fresh per test unless sharing is deliberate and reset is explicit.

Example fixture:

```python
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_client():
    return Mock()
```

## 36. pytest `monkeypatch`

pytest's `monkeypatch` fixture provides temporary modifications to attributes, mappings, environment variables, and the working directory. Changes are automatically undone after the requesting test or fixture finishes.

Core operations include:

```python
monkeypatch.setattr(...)
monkeypatch.setitem(...)
monkeypatch.delattr(...)
monkeypatch.delitem(...)
monkeypatch.setenv(...)
monkeypatch.delenv(...)
monkeypatch.chdir(...)
```

There is also `monkeypatch.context()` for a smaller nested cleanup scope.

### Example

```python
def test_env(monkeypatch):
    monkeypatch.setenv("APP_MODE", "test")
    assert os.environ["APP_MODE"] == "test"
```

### `patch` vs `monkeypatch`

Use `unittest.mock.patch` when you want mock-specific behavior and call assertions tightly integrated with the patch. Use `monkeypatch` when temporary replacement of attributes/environment/mappings is the main need. They can be used together.

The same lookup-location principle applies: patch the name used by the system under test.

## 37. Mocking and Arrange-Act-Assert

Mocking fits naturally into AAA:

```text
Arrange → configure the test double
Act     → call the system under test
Assert  → verify result and relevant interactions
```

Example:

```python
def test_send_welcome_email():
    notifier = Mock()

    # Arrange
    notifier.send.return_value = None

    # Act
    send_welcome("Alice", notifier)

    # Assert
    notifier.send.assert_called_once_with("Welcome Alice")
```

Keep most mock setup in Arrange and interaction assertions in Assert. If a test's Arrange section becomes much larger than the Act and Assert sections, reconsider the dependency boundary or use a simpler fake.

## 38. Mocking and Boundary Testing

Mocks are useful for forcing boundary cases that would be difficult to trigger with a real dependency:

- missing dependency;
- timeout;
- empty response;
- malformed payload;
- maximum-size payload;
- failure response;
- authentication failure;
- throttling.

For example:

```python
response = {"items": []}
client.fetch.return_value = response
```

Then test how the application behaves.

But mocking does not replace real boundary tests. A mock can tell you that your code responds to a simulated 500 response. It cannot tell you whether your HTTP client really interprets the provider's latest status/body combination correctly.

Use mocked boundary tests for fast exhaustive behavior coverage and integration/contract tests for reality checks.

## 39. Mocking and Regression Testing

Suppose a dependency once returned malformed data and the application crashed. A regression test can preserve that exact failure mode.

```text
1. Reproduce the bug
2. Encode the dependency behavior with a controlled double
3. Observe the failing test
4. Fix production code
5. Keep the test as a regression guard
```

Example:

```python
def parse_status(client):
    payload = client.fetch()
    return payload["status"]


def test_malformed_response_is_handled():
    client = Mock()
    client.fetch.return_value = {"unexpected": "shape"}

    with pytest.raises(ValueError, match="missing status"):
        parse_status(client)
```

The value of the mock here is reproducibility: the test recreates the exact malformed response every time.

## 40. Mocking and Debugging

Mocks can isolate failures, but a badly configured mock can become the failure itself. When a mock-based test behaves strangely, ask:

1. Did I patch the correct location?
2. Did the replacement actually execute?
3. Is `return_value` the shape the code expects?
4. Is `side_effect` configured correctly?
5. Is the code using another reference to the same dependency?
6. Did import style affect patching?
7. Did autospec/spec change attribute access?
8. Is the mock hiding an integration problem?
9. Is a nested mock returning another mock unexpectedly?
10. Would a small fake make the behavior clearer?

### Traceback connection

When a mocked test fails, read the traceback before changing the mock. The failure location tells you whether the application, the test setup, or the double's contract is wrong. Use logging sparingly to expose important test setup and production boundary context; do not turn tests into noisy log streams.

## 41. Mocking Data Pipelines

Consider:

```text
Input file
   ↓
Parser
   ↓
Validator
   ↓
Transformer
   ↓
Database
   ↓
Object storage
```

A unit test for a transformer can use an in-memory input and a mocked repository/output store. Parser tests can use small fixtures, and validation tests can use parametrized boundary inputs.

Example:

```python
def run_pipeline(record, repository, storage):
    clean = transform(record)
    repository.save(clean)
    storage.put(clean)
```

Unit test:

```python
def test_run_pipeline_persists_transformed_record():
    repository = Mock()
    storage = Mock()

    run_pipeline({"name": " Alice "}, repository, storage)

    repository.save.assert_called_once_with({"name": "Alice"})
    storage.put.assert_called_once_with({"name": "Alice"})
```

Integration tests should still exercise actual serialization, object-store interaction, database schema, and other critical boundaries.

## 42. Mocking ML Systems

An ML application may look like:

```text
Application
   ↓
Feature store
   ↓
Model / predictor
   ↓
Experiment tracker / registry
```

You can mock `model.predict()` to test application branching, fallback behavior, input validation, response formatting, and error handling. You can stub a feature-store response to test missing features.

```python
model = Mock()
model.predict.return_value = {"label": "fraud", "score": 0.91}
```

This does **not** validate model quality, calibration, drift, data quality, feature correctness, or scientific validity. Those require real models and evaluation datasets.

The testing distinction is:

```text
Mocked model call → validates application orchestration
Real model evaluation → validates model behavior/quality
```

## 43. Mocking LLM Applications

A typical LLM application may be:

```text
Application
   ↓
LLM client
   ↓
response parser
   ↓
business logic
```

Mocking the LLM response allows deterministic tests for:

- parsing;
- schema validation;
- retries;
- error handling;
- fallback behavior;
- tool-call handling;
- token/response limits;
- malformed provider responses.

Example:

```python
llm = Mock()
llm.generate.return_value = {
    "text": '{"intent":"refund","confidence":0.95}'
}
```

A parser test can then validate the application logic without making a real model call.

**Important limitation:** a mocked LLM response does not test model quality, actual reasoning, prompt sensitivity, provider latency, provider safety behavior, or production distribution of outputs. Real evaluation suites and controlled provider tests are required for those questions.

## 44. Mocking Agentic AI Systems

Agentic systems often contain several boundaries:

```text
Agent
  ↓
LLM provider
  ↓
Tool selection
  ↓
Tool
  ↓
External service

Additional boundaries: search, DB, vector store, memory, browser, queues
```

A unit-level orchestration test can mock the LLM and individual tools to validate:

- routing;
- state transitions;
- tool invocation;
- argument construction;
- retry/fallback behavior;
- error handling;
- stop conditions.

Example scenario:

```python
llm = AsyncMock()
llm.return_value = {"tool": "search", "arguments": {"query": "Python testing"}}
search = AsyncMock(return_value={"results": ["doc-1"]})
```

The test can assert that the orchestrator chooses `search` and passes the expected query.

What the mocked test does not fully validate:

- actual model quality;
- real tool semantics;
- retrieval quality;
- production latency;
- real-world integration failures;
- unexpected provider behavior.

A mature agent test strategy combines deterministic component tests with real evaluation scenarios and selected integration tests.

## 45. Contract Testing

Mocks can become stale. Imagine a mock assumes:

```json
{"status": "success"}
```

while the real API changes to:

```json
{"state": "success"}
```

Mocked application tests may continue passing.

**Contract testing** checks that the assumptions made by one side of a boundary are compatible with the actual service or published contract. Depending on the architecture, this can be done through provider/consumer contract tests, schema validation, integration environments, or API specification checks.

A healthy approach is not “replace all mocks with contract tests.” It is to cover different risks at different layers:

```text
Unit mock/stub → fast local behavior
Contract test  → interface compatibility
Integration    → real dependency behavior
E2E            → system-level workflow
```

This layered strategy reduces the chance that a fake view of reality becomes the only test evidence.

## 46. Determinism and False Confidence

Tests benefit from predictable inputs and outputs. Common sources of nondeterminism include:

- time;
- randomness;
- network calls;
- external service state;
- asynchronous events;
- LLM outputs.

Test doubles can make these inputs deterministic. But determinism alone is not correctness.

### False confidence example

```text
Mock says: “API returned the object I expected.”
Real API says: “Field name changed last Tuesday.”

Unit test passes. Production breaks.
```

The answer is not to stop mocking. The answer is to add enough integration/contract coverage to validate the boundary.

A strong test suite makes deliberate trade-offs between speed, isolation, realism, maintenance cost, and failure detection.

## 47. Common Mistakes

### 1. Patching the wrong location

**Problem:** mock has no effect.
**Why:** patch targets the original definition, not the name used by the system under test.
**Fix:** patch the lookup location.

### 2. Mocking everything

**Problem:** fast but unrealistic tests.
**Why:** fear of real dependencies.
**Fix:** mix unit, contract, integration, and E2E tests.

### 3. Mocking implementation details

**Problem:** harmless refactoring breaks tests.
**Why:** assertions describe private structure, not behavior.
**Fix:** prefer observable outcomes and meaningful boundary interactions.

### 4. Overusing `assert_called_once_with`

**Problem:** test becomes brittle.
**Why:** exact calls are asserted even though they are not the contract.
**Fix:** assert arguments when they matter; otherwise verify behavior another way.

### 5. Forgetting autospec

**Problem:** misspelled methods or wrong signatures pass.
**Why:** unrestricted mocks are permissive.
**Fix:** use `autospec`/`create_autospec` at important Python interfaces.

### 6. Incorrect `side_effect`

**Problem:** unexpected return values/exceptions.
**Why:** confusing exception, callable, and iterable forms.
**Fix:** test the double itself in a tiny experiment when unsure.

### 7. Confusing `Mock` and `MagicMock`

**Problem:** magic methods do not behave as expected.
**Why:** ordinary mocks do not provide the same special-method support.
**Fix:** use `MagicMock` only when a Python protocol is part of the test.

### 8. Incorrect async mocking

**Problem:** coroutine/await assertions fail or tests accidentally never await.
**Why:** ordinary mocks are used for async callables.
**Fix:** use `AsyncMock` for async boundaries and await-specific assertions.

### 9. Mocking database calls and assuming SQL works

**Problem:** SQL/schema defects reach production.
**Why:** mock validates application behavior, not DB semantics.
**Fix:** add repository integration tests.

### 10. Mocking API calls and assuming the API works

**Problem:** provider changes break production.
**Why:** response fixture is stale.
**Fix:** contract/sandbox/integration coverage.

### 11. Unrealistic fake responses

**Problem:** happy-path behavior is correct only for impossible payloads.
**Fix:** derive fixtures from real documented contracts and representative sanitized samples.

### 12. Testing the mock instead of the application

**Problem:** many assertions about mock setup, little evidence about business behavior.
**Fix:** assert the outcome and only the necessary interactions.

### 13. Deeply nested mocks

**Problem:** mock chains become unreadable.
**Fix:** narrow interfaces or fakes.

### 14. Excessive fixture complexity

**Problem:** a fixture hides important test setup.
**Fix:** keep fixtures focused and discoverable.

### 15. Leaving patches active accidentally

**Problem:** later tests inherit state.
**Fix:** context managers, decorators, or pytest monkeypatch.

### 16. Mocking pure functions unnecessarily

**Problem:** tests become harder to understand.
**Fix:** call the pure function directly.

### 17. Not testing failure paths

**Problem:** retries/fallbacks are unverified.
**Fix:** use `side_effect` or controlled stubs.

### 18. Not testing integration boundaries

**Problem:** unit suite passes while deployments fail.
**Fix:** add contract/integration tests.

### 19. Using mocks that do not match the real interface

**Problem:** test double drifts from production API.
**Fix:** autospec, protocols, contract tests, and representative fixtures.

### 20. Ignoring contract tests

**Problem:** mocks become an outdated local fiction.
**Fix:** verify important external contracts independently.

## 48. Complete Realistic Example — User Registration Service

Consider a service:

```text
CLI/API
   ↓
UserService
   ├──→ UserRepository → Database
   └──→ EmailService   → External Email Provider
```

### Production-oriented boundary design

```python
class UserService:
    def __init__(self, repository, email_service):
        self.repository = repository
        self.email_service = email_service

    def register(self, name: str, email: str) -> int:
        user_id = self.repository.create({"name": name, "email": email})
        self.email_service.send_welcome(email, name)
        return user_id
```

### Dummy

A test for ID validation might pass a notifier that should never be used.

### Stub

A stub repository can always return a known ID so the service can be tested deterministically.

### Fake

An in-memory repository can implement `create()` and `get()` for a broader service test.

### Mock

A mocked email service can verify that the welcome email was sent to the correct address.

```python
from unittest.mock import Mock


def test_register_sends_welcome_email():
    repository = Mock()
    repository.create.return_value = 101
    email_service = Mock()

    service = UserService(repository, email_service)
    result = service.register("Alice", "alice@example.test")

    assert result == 101
    repository.create.assert_called_once_with({
        "name": "Alice",
        "email": "alice@example.test",
    })
    email_service.send_welcome.assert_called_once_with(
        "alice@example.test",
        "Alice",
    )
```

### Failure simulation

If email delivery failure should cause registration to fail or be retried, configure:

```python
email_service.send_welcome.side_effect = TimeoutError("mailer timeout")
```

Then write a test for the service's documented behavior.

### What still needs integration coverage?

- database schema and SQL;
- transaction behavior;
- email provider protocol;
- authentication and authorization;
- actual message delivery boundary if critical.

## 49. Mini-Project — Resilient External API Client

Build a self-contained API client that does not require a paid API or credentials. The “real” transport can be represented by an injected interface, while the unit tests use mocks/stubs.

### Architecture

```text
Application
    ↓
ResilientClient
    ↓
Transport interface
    ↓
HTTP implementation (production)

Unit tests → Mock transport
Integration → Local test server/sandbox
```

### Directory structure

```text
resilient-client/
├── client.py
├── models.py
└── test_client.py
```

### `models.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ApiResponse:
    status_code: int
    payload: dict[str, object]
```

### `client.py`

```python
import time
from dataclasses import dataclass
from typing import Protocol


class Transport(Protocol):
    def get(self, path: str, timeout: float) -> ApiResponse: ...


@dataclass
class ResilientClient:
    transport: Transport
    attempts: int = 3
    backoff_seconds: float = 0.0

    def get_json(self, path: str) -> dict[str, object]:
        last_error: Exception | None = None
        for attempt in range(1, self.attempts + 1):
            try:
                response = self.transport.get(path, timeout=2.0)
                if response.status_code == 200:
                    return response.payload
                if response.status_code in {429, 500, 502, 503, 504}:
                    raise RuntimeError(f"retryable status: {response.status_code}")
                raise RuntimeError(f"non-retryable status: {response.status_code}")
            except (TimeoutError, RuntimeError) as exc:
                last_error = exc
                if attempt == self.attempts:
                    raise
                time.sleep(self.backoff_seconds)

        raise AssertionError(f"unreachable: {last_error}")
```

### `test_client.py`

```python
from unittest.mock import Mock, call
import pytest


def test_success():
    transport = Mock()
    transport.get.return_value = ApiResponse(200, {"value": 42})

    client = ResilientClient(transport, attempts=3)

    assert client.get_json("/items/1") == {"value": 42}
    transport.get.assert_called_once_with("/items/1", timeout=2.0)


def test_retry_then_success(monkeypatch):
    transport = Mock()
    transport.get.side_effect = [
        TimeoutError("temporary"),
        ApiResponse(200, {"value": 42}),
    ]
    sleep = Mock()
    monkeypatch.setattr("client.time.sleep", sleep)

    client = ResilientClient(transport, attempts=2, backoff_seconds=0.1)

    assert client.get_json("/items/1") == {"value": 42}
    assert transport.get.call_count == 2
    sleep.assert_called_once_with(0.1)


def test_exhausted_retries():
    transport = Mock()
    transport.get.side_effect = TimeoutError("down")

    client = ResilientClient(transport, attempts=2)

    with pytest.raises(TimeoutError, match="down"):
        client.get_json("/items/1")

    assert transport.get.call_count == 2
```

### Production note

The example uses `time.sleep` and a mock for deterministic tests. A production implementation may inject a sleep/backoff function or clock so timing policy is easier to test. An actual integration suite should exercise the real HTTP transport against a controlled endpoint or sandbox.

### Test strategy

- **Mock transport:** deterministic unit tests for retries and status handling.
- **Stub/fake transport:** useful when response behavior is richer than simple call assertions.
- **Real temporary configuration:** verify configuration loading without storing real secrets.
- **Autospec:** constrain mock interfaces where appropriate.
- **Regression test:** capture any malformed or retryable response that previously caused a bug.

## 50. Progressive Coding Exercises

The exercises increase from basic role recognition to production-oriented architecture. Each exercise is immediately followed by its solution, code, explanation, and common mistake.

### Beginner — Exercise 1: Identify the Double

**Task:** You pass `object()` into a function only because the function requires a logger parameter and the logger is not used. What kind of test double is this?

**Solution:** Dummy.

**Code:**

```python
def process(value: int, logger) -> int:
    return value * 2

assert process(3, object()) == 6
```

**Explanation:** The object simply satisfies the required parameter. No behavior or interaction is being controlled or asserted.

**Why it works:** The test does not need the logger.

**Common mistake:** Calling every replacement dependency a mock.

### Exercise 2: Create a Stub

**Task:** Write a stub repository that always returns Alice for user ID 1.

**Solution:**

```python
class StubRepository:
    def get_user(self, user_id: int) -> dict[str, object]:
        return {"id": user_id, "name": "Alice"}
```

**Explanation:** The repository supplies predetermined behavior/data.

**Common mistake:** Adding call assertions when the test only needs the returned data.

### Exercise 3: Build a Fake

**Task:** Build an in-memory repository supporting `save()` and `get()`.

**Solution:**

```python
class InMemoryRepository:
    def __init__(self) -> None:
        self._data: dict[int, dict[str, object]] = {}

    def save(self, user: dict[str, object]) -> None:
        self._data[int(user["id"])] = user

    def get(self, user_id: int) -> dict[str, object]:
        return self._data[user_id]
```

**Explanation:** This has working behavior rather than returning one hard-coded answer.

**Common mistake:** Assuming this fake proves the production database behaves the same way.

### Exercise 4: Basic Mock

**Task:** Mock an `email.send()` call and assert it received the correct address.

**Solution:**

```python
from unittest.mock import Mock

email = Mock()
email.send("alice@example.test", "Welcome")
email.send.assert_called_once_with("alice@example.test", "Welcome")
```

**Explanation:** The test is verifying an interaction.

**Common mistake:** Asserting every unrelated internal call.

### Exercise 5: `return_value`

**Task:** Configure `client.fetch()` to return a known payload.

**Solution:**

```python
client = Mock()
client.fetch.return_value = {"status": "ok"}
assert client.fetch()["status"] == "ok"
```

**Common mistake:** Calling `client.fetch.return_value()` by accident when the desired value is already the dict.

### Exercise 6: Exception `side_effect`

**Task:** Make `client.fetch()` raise `TimeoutError`.

**Solution:**

```python
client.fetch.side_effect = TimeoutError("timeout")
```

Then:

```python
with pytest.raises(TimeoutError, match="timeout"):
    client.fetch()
```

**Why it works:** The mock raises the configured exception when called.

### Intermediate — Exercise 7: Sequential `side_effect`

**Task:** Configure two calls: first timeout, second success.

**Solution:**

```python
client.fetch.side_effect = [
    TimeoutError("first"),
    {"status": "ok"},
]
```

**Explanation:** Each call consumes the next item.

**Common mistake:** Reusing the same mock across unrelated tests and forgetting that the iterable has already been consumed.

### Exercise 8: Call History

**Task:** Call a worker three times and assert the inputs are 1, 2, 3.

**Solution:**

```python
from unittest.mock import Mock

worker = Mock()
for value in [1, 2, 3]:
    worker(value)

assert worker.call_count == 3
assert [item.args[0] for item in worker.call_args_list] == [1, 2, 3]
```

### Exercise 9: `call` and `assert_has_calls`

**Task:** Verify that `send("A")` and `send("B")` occurred in order.

**Solution:**

```python
from unittest.mock import call

mailer = Mock()
mailer.send("A")
mailer.send("B")

mailer.send.assert_has_calls([call("A"), call("B")])
```

### Exercise 10: `ANY`

**Task:** Assert a request has a deterministic destination but a nondeterministic request ID.

**Solution:**

```python
from unittest.mock import ANY

client.send("orders", ANY)
client.send.assert_called_once_with("orders", ANY)
```

**Common mistake:** Using `ANY` for every field and accidentally asserting almost nothing.

### Exercise 11: Patching the Correct Location

**Task:** `service.py` uses `from utils import get_data`. Where should the unit test patch?

**Solution:** `service.get_data`.

**Explanation:** The system under test looks up the copied name in `service`.

### Exercise 12: `patch.object`

**Task:** Temporarily replace a method on an instance.

**Solution:**

```python
with patch.object(client, "fetch", return_value={"ok": True}):
    assert client.fetch() == {"ok": True}
```

**Common mistake:** Forgetting cleanup by modifying the attribute manually.

### Exercise 13: `patch.dict`

**Task:** Temporarily enable a feature flag in `os.environ`.

**Solution:**

```python
with patch.dict(os.environ, {"FEATURE_X": "on"}):
    assert os.environ["FEATURE_X"] == "on"
```

### Exercise 14: `patch.multiple`

**Task:** Patch two class attributes in a single context.

**Solution:**

```python
with patch.multiple(MyService, timeout=1, retries=2):
    ...
```

**Explanation:** Both attributes are changed temporarily and restored afterward.

### Exercise 15: Autospec

**Task:** Create an autospecced client instance for `EmailClient`.

**Solution:**

```python
client = create_autospec(EmailClient, instance=True)
```

**Why:** The mock follows the target interface more closely, helping catch signature/interface errors.

### Exercise 16: `mock_open`

**Task:** Test that `open()` is called with a filename and UTF-8 encoding.

**Solution:**

```python
opener = mock_open(read_data="hello")
with patch("builtins.open", opener):
    read_file("a.txt")
opener.assert_called_once_with("a.txt", "r", encoding="utf-8")
```

**Common mistake:** Using `mock_open` for a test whose real requirement is filesystem semantics.

### Exercise 17: `AsyncMock`

**Task:** Mock an async API call and verify it was awaited once.

**Solution:**

```python
async def example_async_test():
    api = AsyncMock(return_value={"ok": True})
    result = await api("/health")
    assert result == {"ok": True}
    api.assert_awaited_once_with("/health")
```

### Exercise 18: Retry Testing

**Task:** Make the first call fail and the second succeed, then verify two attempts.

**Solution:**

```python
client.fetch.side_effect = [TimeoutError("temporary"), {"status": "ok"}]
assert fetch_with_retry(client, attempts=2) == {"status": "ok"}
assert client.fetch.call_count == 2
```

### Advanced — Exercise 19: Dependency Injection

**Task:** Refactor a function that constructs `RealClient()` internally so that the client is passed in.

**Solution:**

```python
def process(client):
    return client.fetch()
```

**Why it works:** The test no longer needs to patch the constructor just to substitute the dependency.

### Exercise 20: Protocol Boundary

**Task:** Define a minimal `Repository` protocol containing `get(id)` and use it as the service dependency.

**Solution:**

```python
from typing import Protocol

class Repository(Protocol):
    def get(self, user_id: int) -> dict[str, object]: ...
```

**Common mistake:** Creating a huge protocol that simply reproduces the concrete client's entire interface. Keep boundaries narrow.

### Exercise 21: Database Testing Strategy

**Task:** Decide whether a test checking business logic for “inactive user → update to active” should mock the repository or connect to PostgreSQL.

**Solution:** Use a mock/stub for the unit test; separately use integration tests for SQL/schema/transaction behavior.

**Why:** The questions are different.

### Exercise 22: LLM Application Test

**Task:** Test a parser that converts a mocked LLM JSON response into a typed application result.

**Solution:** Mock the LLM response with a deterministic payload, then assert parsing and validation behavior.

```python
llm.generate.return_value = '{"intent":"refund"}'
result = parse_intent(llm.generate())
assert result.intent == "refund"
```

**Common mistake:** Treating the passing parser test as evidence that the LLM will produce that JSON reliably.

### Exercise 23: Agent Tool Routing

**Task:** Mock an async LLM tool-selection response and an async search tool. Verify the orchestrator awaits the search tool with the selected query.

**Solution:**

```python
llm = AsyncMock(return_value={"tool": "search", "query": "pytest"})
search = AsyncMock(return_value=["doc-1"])

result = await run_agent("Find pytest docs", llm, search)

search.assert_awaited_once_with("pytest")
```

**Why:** The test isolates orchestration logic. It does not validate the model's real tool selection quality or search relevance.

### Production-Oriented — Exercise 24: Choose the Right Layer

**Task:** For each requirement, choose unit + double, contract, integration, or E2E: “Validate that our SQL query correctly inserts a row under the production schema.”

**Solution:** Integration test against a real controlled database/test database.

**Why:** The real database behavior is part of the requirement. A mock cannot validate SQL semantics.

## 51. Debugging Lab

These examples are intentionally broken. For each one, diagnose the problem rather than immediately changing random mock configuration.

### Lab 1 — Wrong Patch Target

**Broken code:**

```python
# service.py
from utils import get_data

def process():
    return get_data()

# test_service.py
with patch("utils.get_data", return_value="fake"):
    assert process() == "fake"
```

**Expected symptom:** Assertion sees real data.

**How to investigate:** Inspect the import style and ask which name `process()` resolves.

**Diagnosis:** `service.get_data` must be patched.

**Fixed code:**

```python
with patch("service.get_data", return_value="fake"):
    assert process() == "fake"
```

**Lesson:** Patch the lookup location.

### Lab 2 — Incorrect `return_value` Shape

**Broken:**

```python
client.fetch.return_value = Mock()
assert load_name(client) == "Alice"
```

**Symptom:** `load_name()` may receive a mock for a field instead of a string.

**Diagnosis:** The code expects a mapping with `response["name"]`.

**Fixed:**

```python
client.fetch.return_value = {"name": "Alice", "status": "ok"}
```

**Lesson:** Configure the shape the production code consumes, not just a vaguely “successful” mock.

### Lab 3 — Wrong `side_effect`

**Broken:**

```python
client.fetch.side_effect = [TimeoutError("x")]
assert fetch_with_retry(client, attempts=2)["status"] == "ok"
```

**Symptom:** The second call raises `StopIteration` because there is no second iterable item.

**Diagnosis:** The test promised only one call result but configured two attempts.

**Fixed:**

```python
client.fetch.side_effect = [TimeoutError("x"), {"status": "ok"}]
```

### Lab 4 — Incorrect Assertion

**Broken:**

```python
mailer.send("Alice", "Welcome")
mailer.send.assert_called_once()
```

**Symptom:** Test passes, but the contract might be wrong because arguments are not checked.

**Diagnosis:** The test's real requirement includes the destination/subject.

**Fixed:**

```python
mailer.send.assert_called_once_with("Alice", "Welcome")
```

### Lab 5 — Mocking Async Code Incorrectly

**Broken:**

```python
client.fetch = Mock(return_value={"ok": True})
result = await client.fetch()
```

**Symptom:** The result is not awaitable.

**Diagnosis:** `fetch` is async.

**Fixed:**

```python
client.fetch = AsyncMock(return_value={"ok": True})
result = await client.fetch()
client.fetch.assert_awaited_once()
```

### Lab 6 — Missing Autospec

**Broken:**

```python
client = Mock()
client.send_email("a@example.test", "subject")
```

**Symptom:** Test may pass even though the real interface requires a body.

**Diagnosis:** The mock is too permissive.

**Fixed:**

```python
client = create_autospec(EmailClient, instance=True)
```

Then call the real three-argument signature.

### Lab 7 — Mock Configured but Not Used

**Broken idea:**

```python
mock = Mock(return_value="fake")
real_client = RealClient()
assert process(real_client) == "fake"
```

**Symptom:** The configured mock has no effect.

**Diagnosis:** The system under test received the real dependency.

**Fixed:** Pass `mock` into `process(mock)`, or patch the correct lookup location.

### Lab 8 — Over-Mocked Test

**Broken pattern:** A test mocks every helper function inside a pure transformation pipeline and asserts exact call order for every helper.

**Symptom:** Refactoring a private helper breaks many tests.

**Diagnosis:** The tests specify implementation structure rather than output behavior.

**Fixed:** Test pure transformations directly and mock only true external boundaries.

### Lab 9 — Nested Mock Returns Another Mock

**Broken:**

```python
client.get_user.return_value.profile.email
```

**Symptom:** The code gets a mock where a string was expected.

**Diagnosis:** Nested attributes create nested mocks unless configured explicitly.

**Fixed:** Use an explicit dict/dataclass response or a small fake object.

### Lab 10 — Patching a Property Incorrectly

**Broken:**

```python
with patch.object(user, "is_admin", return_value=True):
    assert user.is_admin is True
```

**Symptom:** Ordinary method-style patching does not model the property access correctly.

**Diagnosis:** `is_admin` is a descriptor property.

**Fixed:** Patch the class attribute with `PropertyMock`.

```python
with patch.object(type(user), "is_admin", new_callable=PropertyMock) as prop:
    prop.return_value = True
    assert user.is_admin is True
```

### Lab 11 — Mocking Database SQL

**Broken test:**

```python
db.execute = Mock()
repository.insert(user)
db.execute.assert_called_once()
```

**Symptom:** Test passes while SQL could be syntactically invalid.

**Diagnosis:** Interaction test does not validate SQL execution.

**Fixed strategy:** Keep the unit test if the interaction matters, then add a repository integration test against a controlled real database.

### Lab 12 — Stale External API Fixture

**Broken fixture:**

```python
client.get.return_value = {"status": "success"}
```

**Symptom:** Unit tests pass even though the provider now returns `{"state": "success"}`.

**Diagnosis:** Mock contract drift.

**Fixed strategy:** Add contract/integration coverage, keep fixtures representative and versioned, and update tests from the provider contract rather than guessing.

## 52. Interview Questions

### 1. What is a test double?
A replacement for a real dependency used during testing. It may be a dummy, stub, fake, mock, or spy.

### 2. Stub vs mock?
A stub mainly provides controlled answers; a mock additionally records/validates interactions.

### 3. Mock vs fake?
A mock is primarily a configurable interaction-recording test double; a fake is a lightweight working implementation.

### 4. Dummy vs stub?
A dummy merely satisfies a dependency slot; a stub supplies relevant behavior/data.

### 5. What is patching?
Temporarily replacing a name/object attribute used by code during a test.

### 6. Why patch where the object is used?
Because imports can bind a local/module name to an object. The system under test resolves that local name at runtime.

### 7. What is `autospec`?
A way to create mocks based on a target's interface/signature so incorrect attributes/calls are more likely to be caught.

### 8. Mock vs MagicMock?
`MagicMock` adds support for many magic methods/protocols. Use it when those protocols are part of the code under test.

### 9. `side_effect` vs `return_value`?
`return_value` supplies a normal result; `side_effect` can raise, call a function, or provide sequential outcomes.

### 10. How do you mock async code?
Use `AsyncMock` for async callables and assert with await-specific methods such as `assert_awaited_once_with()`.

### 11. What is over-mocking?
Using so many doubles/assertions that tests become coupled to implementation details and can pass while integrations are broken.

### 12. When should you not mock?
When the real dependency behavior is part of what you need to prove, such as SQL correctness, filesystem semantics, API contracts, or critical integration behavior.

### 13. How do you test external APIs?
Use mocked unit tests for local client logic, plus contract/integration tests against a controlled real endpoint or sandbox.

### 14. How do you test database code?
Unit test business behavior with a repository double, then test repository/SQL behavior against a real controlled database.

### 15. How do you test retries?
Use `side_effect` to model a sequence of failures and successes, then assert meaningful attempt/result behavior. Avoid timing-heavy assertions unless timing is the contract.

### 16. How do mocks affect test reliability?
They can improve determinism and speed, but excessive or unrealistic mocking can create false confidence and stale assumptions.

### 17. How would you test an LLM application?
Mock provider responses for parser/orchestration/error-path tests, then use real-model evaluation and controlled integration tests for actual model quality and provider behavior.

### 18. How would you test an agentic AI system?
Mock individual external boundaries to test deterministic orchestration/state transitions, then combine this with evaluation suites and selected real integrations to validate tool/retrieval/model behavior.

### 19. Why might a fake be better than a mock?
When the dependency behavior is simple enough to implement and a working local model gives more readable, behavior-focused tests.

### 20. What is the biggest mocking design lesson?
Make dependencies explicit and narrow. Good dependency boundaries reduce the need for complicated patching.

## 53. Architecture Questions

### 1. How would you design a test strategy for a service with five external dependencies?
**Model answer:** Keep core business logic unit-tested with selected doubles; define integration tests around important real boundaries; add contract tests for APIs/schemas; add a small number of E2E journeys. Classify each dependency by risk, cost, volatility, and whether its behavior itself must be proven.

### 2. Which dependencies should be mocked?
**Model answer:** Dependencies that make unit tests slow, nondeterministic, costly, side-effecting, or difficult to force into failure. Do not mock simply because something is a dependency.

### 3. Which should use integration tests?
**Model answer:** Boundaries whose actual behavior matters: SQL, serialization, provider protocol, queue semantics, IAM/network configuration, and critical cloud integrations.

### 4. How would you prevent mocks from becoming stale?
**Model answer:** Use autospec for Python interfaces, maintain contract tests for external interfaces, derive fixtures from documented contracts/representative sanitized responses, version meaningful schemas, and periodically run integration tests.

### 5. How would you test a payment API?
**Model answer:** Unit-test payment decision logic with a client double, simulate timeouts/429/500/duplicate calls, assert idempotency behavior, and use a provider sandbox/contract/integration suite for the real API. Never use production payment credentials in tests.

### 6. How would you test a database repository?
**Model answer:** Test business logic separately; run repository tests against a controlled real database to validate SQL, schema, transactions, constraints, and migrations.

### 7. How would you test a queue consumer?
**Model answer:** Unit-test handler logic with message doubles; integration-test acknowledgement, retries, duplicate delivery, ordering where required, and dead-letter semantics against a real or realistic broker environment.

### 8. How would you test an AI agent?
**Model answer:** Test orchestration with mocked LLM/tool boundaries, validate state transitions and tool arguments, use deterministic scenario fixtures, then add real-model evaluation, retrieval evaluation, and selected end-to-end/integration scenarios.

### 9. How would you balance speed vs realism?
**Model answer:** Put the majority of fast deterministic behavior coverage at unit level, but reserve enough integration/contract/E2E coverage to detect real boundary failures. Optimize based on risk, not a fixed percentage.

### 10. How would you detect false confidence from mocks?
**Model answer:** Compare mocked assumptions with real contracts, monitor integration failures, run representative integration suites in CI, and review whether critical boundaries have any real-system validation.

### 11. What architecture signals indicate a mocking problem?
**Model answer:** Deep mock chains, repeated patching of constructors, tests needing many implementation-detail assertions, giant fixture setup, and mock-only interfaces that are hard to relate to production behavior.

### 12. How can architecture reduce mocking?
**Model answer:** Isolate side effects, use dependency injection, define narrow protocols, keep domain logic pure where practical, and put integrations behind small adapters.

## 54. Production Testing Strategy

A production-quality system normally uses multiple testing layers:

```text
                E2E
                 ↑
            Integration
                 ↑
              Contract
                 ↑
               Unit
```

### Unit

Use mocks/stubs/fakes selectively for speed and isolation. Cover decision logic, validation, edge cases, retries, and failure handling.

### Contract

Validate that the assumptions at a boundary remain compatible with the provider/consumer contract.

### Integration

Use real databases, test brokers, sandbox APIs, cloud emulators, or controlled cloud resources when the real boundary matters.

### End-to-end

Exercise important user/system journeys using realistic components. Keep the suite focused because E2E tests are usually more operationally expensive.

### Mapping doubles to layers

| Layer | Common test setup | Main purpose |
|---|---|---|
| Unit | Mock/stub/fake | Fast local behavior |
| Contract | Provider/consumer contract + realistic payloads | Interface compatibility |
| Integration | Real test dependency/emulator | Boundary semantics |
| E2E | Realistic stack | Workflow validation |

A mature test strategy is a portfolio, not a single technique.

## 55. Security Considerations

Testing code must be treated as real software from a security perspective.

- Never put real API keys in source or test fixtures.
- Never commit production credentials.
- Avoid real customer or payment data.
- Sanitize logs generated by tests and applications.
- Avoid destructive operations against production resources.
- Use test accounts and sandboxes.
- Protect sensitive mock fixtures and recordings.
- Use least-privilege credentials for integration environments.
- Make test configuration obviously non-production.

For AI applications, avoid storing real user prompts or responses if they contain sensitive information unless the data is authorized, minimized, and protected according to the organization's policy.

## 56. Production Checklist

### Foundation

- [ ] I understand what a test double is.
- [ ] I can distinguish dummy, stub, fake, mock, and spy.
- [ ] I understand state vs interaction verification.

### Python mocking

- [ ] I can use `Mock`.
- [ ] I can use `MagicMock`.
- [ ] I can use `patch`.
- [ ] I can identify the correct patch target.
- [ ] I can use `side_effect`.
- [ ] I can use `autospec`/`create_autospec`.
- [ ] I can mock async code with `AsyncMock`.
- [ ] I can test file operations with `mock_open`.
- [ ] I can control environment variables safely.

### Test design

- [ ] I avoid unnecessary mocking.
- [ ] I avoid asserting private implementation details without a contract reason.
- [ ] I know when a real dependency or temporary resource is better.
- [ ] I understand integration and contract tests.

### Production

- [ ] I can design a layered test strategy.
- [ ] I can test external APIs safely.
- [ ] I can test database boundaries realistically.
- [ ] I can test retries and failures.
- [ ] I can test LLM orchestration separately from model quality.
- [ ] I can test agentic AI state/tool orchestration.
- [ ] I understand mock-induced false confidence.

### Security

- [ ] No real secrets are stored in tests.
- [ ] Production data is not used casually in fixtures.
- [ ] Integration tests use sandbox/test resources.

### API audit

- [ ] `Mock`, `MagicMock`, `patch`, `patch.object`, `patch.dict`, `patch.multiple`
- [ ] `PropertyMock`, `AsyncMock`, `call`, `ANY`, `sentinel`, `DEFAULT`
- [ ] `create_autospec`, `mock_open`
- [ ] `return_value`, `side_effect`, `called`, `call_count`
- [ ] `call_args`, `call_args_list`, `method_calls`, `mock_calls`, `reset_mock`
- [ ] all seven core call assertions
- [ ] async await assertions
- [ ] pytest `monkeypatch` operations

## 57. Knowledge Check

### Question 1 — What is a test double?
**Answer:** A replacement for a real dependency used during testing.

### Question 2 — Dummy vs stub?
**Answer:** A dummy mainly satisfies a dependency slot; a stub supplies controlled behavior/data.

### Question 3 — Fake vs mock?
**Answer:** A fake is a lightweight working implementation; a mock is commonly used to control and verify interactions.

### Question 4 — Mock vs MagicMock?
**Answer:** `MagicMock` adds support for many special/dunder methods and Python protocols.

### Question 5 — `return_value` vs `side_effect`?
**Answer:** `return_value` gives the normal result; `side_effect` can raise, call a function, or provide sequential outcomes.

### Question 6 — What does patching do?
**Answer:** It temporarily replaces a reachable name/attribute for the test scope.

### Question 7 — Where should you patch?
**Answer:** Where the system under test looks up the object at runtime.

### Question 8 — Why use autospec?
**Answer:** To make mocks adhere more closely to the target interface/signatures and catch certain incorrect calls.

### Question 9 — `spec` vs `spec_set`?
**Answer:** `spec` constrains available attributes; `spec_set` is stricter about setting attributes as well.

### Question 10 — What is `mock_open` for?
**Answer:** Replacing `open()` for simple file operation tests, including context-manager use.

### Question 11 — When use AsyncMock?
**Answer:** For async callables where the test needs a coroutine-like mock and await tracking.

### Question 12 — What is pytest `monkeypatch`?
**Answer:** A fixture for temporary attribute, mapping, environment, and working-directory changes that are automatically undone.

### Question 13 — What is dependency injection?
**Answer:** Supplying a dependency from outside rather than constructing/looking it up inside the function or class.

### Question 14 — Why reduce over-mocking?
**Answer:** To avoid brittle tests, implementation coupling, and false confidence.

### Question 15 — Does a mocked API test prove the external API works?
**Answer:** No. It validates your code against the simulated response. Use contract/integration coverage for real compatibility.

### Question 16 — Does mocking a database prove SQL works?
**Answer:** No. Use real database integration tests for SQL/schema/transaction behavior.

### Question 17 — Does a mocked LLM test model quality?
**Answer:** No. It tests application handling of a predetermined model response.

### Question 18 — How can agent tests use mocks?
**Answer:** Mock LLMs/tools/search/DB boundaries to test orchestration, routing, state, retries, and failures deterministically.

### Question 19 — When is a real temporary filesystem better than `mock_open`?
**Answer:** When actual filesystem semantics are part of the contract.

### Question 20 — What is the architectural lesson?
**Answer:** Explicit, narrow dependency boundaries make code easier to test and reduce the need for complicated mocking.

## 58. Glossary

**Test double** — A replacement for a real dependency used in a test.

**Dummy** — A placeholder used mainly to satisfy a parameter/dependency requirement.

**Stub** — A double that returns controlled, predetermined behavior/data.

**Fake** — A simplified but working implementation of a dependency.

**Mock** — A configurable double commonly used to record and verify interactions.

**Spy** — A double that observes interactions while allowing real behavior to execute, depending on the implementation.

**State verification** — Checking outputs or resulting state.

**Interaction verification** — Checking how a dependency was called.

**Patching** — Temporarily replacing a reachable object/name in a test scope.

**Autospec** — Creating mocks that follow a target's interface/signature more closely.

**Spec** — A constraint based on another object's attributes.

**Magic method / dunder method** — Special Python methods such as `__enter__`, `__iter__`, or `__getitem__`.

**Fixture** — Reusable test setup/data supplied to tests.

**Dependency injection** — Supplying dependencies from outside the code under test.

**Protocol** — A structural interface describing required operations.

**Contract test** — A test that validates compatibility at a service/component boundary.

**Integration test** — A test involving multiple real components or a real dependency boundary.

**E2E test** — A test of a larger end-to-end system workflow.

**Determinism** — Reproducible behavior for the same controlled inputs.

**False confidence** — A situation where tests pass but fail to represent an important production risk.

**Mock hell** — Informal term for highly complicated, deeply nested mock setup and assertions.

## 59. Final Mental Model

Use this sequence when deciding how to test a dependency:

```text
UNDERSTAND THE BEHAVIOR
        ↓
IDENTIFY THE EXTERNAL BOUNDARY
        ↓
ASK WHAT THE TEST MUST PROVE
        ↓
PURE LOGIC? ── yes → test directly
        │
        no
        ↓
CHOOSE THE SMALLEST USEFUL DOUBLE
        ├── Dummy → just satisfy the interface
        ├── Stub  → control the answer
        ├── Fake  → use a lightweight working implementation
        ├── Mock  → verify meaningful interactions
        └── Spy   → observe real behavior
        ↓
CONTROL NONDETERMINISM / FAILURES
        ↓
PATCH THE NAME USED BY THE SYSTEM
        ↓
USE AUTOSPEC / NARROW PROTOCOLS WHEN HELPFUL
        ↓
VERIFY OUTCOME + ONLY IMPORTANT INTERACTIONS
        ↓
ASK: WOULD A REAL BOUNDARY TEST FIND ANOTHER CLASS OF BUG?
        ↓
ADD CONTRACT / INTEGRATION / E2E COVERAGE WHERE NEEDED
        ↓
REVIEW FOR OVER-MOCKING AND FALSE CONFIDENCE
```

### The core principle

> Mocking is a technique, not a testing strategy.

A strong engineer can explain both **why a boundary is isolated** and **where real integration evidence still comes from**.

### Final self-review

Before considering this topic complete, answer “yes” to all of these:

1. Can I distinguish dummy, stub, fake, mock, and spy without relying only on memorized words?
2. Can I choose state vs interaction verification deliberately?
3. Can I use `Mock`, `MagicMock`, `patch`, `patch.object`, `patch.dict`, and `patch.multiple`?
4. Can I configure `return_value` and each major form of `side_effect`?
5. Can I inspect call history and choose an appropriate call assertion?
6. Can I use `ANY`, `sentinel`, and `DEFAULT` when they improve clarity?
7. Can I use `autospec`, `spec`, `spec_set`, and `create_autospec` appropriately?
8. Can I mock properties, file operations, and async functions?
9. Can I patch environment variables and other process state safely?
10. Can I explain the “patch where used” rule using Python import semantics?
11. Can I use `pytest.monkeypatch` correctly?
12. Can I design dependency injection instead of relying on heavy patching?
13. Can I identify over-mocking and mock hell?
14. Can I explain when a real dependency or temporary resource is preferable?
15. Can I separate mocked application tests from contract/integration tests?
16. Can I test database/API/queue/cloud boundaries realistically?
17. Can I test data pipelines and ML application orchestration?
18. Can I test LLM and agentic AI orchestration without claiming model-quality validation?
19. Can I debug a mock-based failure systematically?
20. Can I design a layered production test strategy?

If not, revisit the relevant section and redo the associated exercise.


## Technical References

The chapter is based on the Python standard-library and pytest testing model. For current API details, consult the official documentation:

- Python `unittest.mock`: https://docs.python.org/3.14/library/unittest.mock.html
- Python `unittest.mock` examples: https://docs.python.org/3.14/library/unittest.mock-examples.html
- pytest `monkeypatch`: https://docs.pytest.org/en/latest/how-to/monkeypatch.html

These references are especially useful when a Python version adds or changes mock behavior.
