# Mocking and Test Doubles — Complete Study Guide

**Stage 1 — Programming & Computational Thinking**  
**Module 07 — Testing and Systematic Debugging**  
**Lesson 07**

Source analyzed: `07-mocking-and-test-doubles(1).md` (102,726 bytes; 3,135 lines; 59 numbered sections).

This guide teaches the lesson's foundations, Python mocking APIs, examples and architecture applications; reviews the Stage 1 project tree and current learning level; solves all 24 coding exercises; and diagnoses all 12 debugging labs.

---

# Part A — Complete Lesson Summary (under 6,500 words)

## 1. Why tests sometimes replace real dependencies

A function may depend on a database, external API, payment service, email provider, queue, cloud service, clock, or random generator. Calling all real dependencies in every test can make tests slow, expensive, flaky, credential-dependent, network-dependent, stateful, and capable of unwanted side effects. It can also be difficult to force rare events such as timeouts, rate limits, malformed responses, or service outages.

A **test double** is a replacement for a real dependency during a test. It lets us control what that dependency returns or how it behaves, isolate the code under test, reproduce failures, and make tests deterministic.

This does not mean “mock everything.” The purpose of each test decides which dependency should be replaced and which should remain real:

```text
Unit test        → isolate local behavior with selected doubles
Contract test    → validate assumptions at a service boundary
Integration test → exercise real components/dependency semantics
End-to-end test  → exercise a realistic complete workflow
```

The same API may be mocked in a unit test and exercised for real in a sandbox integration test. These tests answer different questions.

## 2. Five types of test doubles

Testing terminology varies somewhat between teams and books. These are useful conceptual distinctions.

| Type | Purpose | Example |
|---|---|---|
| Dummy | Satisfies a required parameter but is not used | `object()` as an unused logger |
| Stub | Supplies predetermined responses/data | Repository always returns Alice |
| Fake | Lightweight working implementation | In-memory repository |
| Mock | Configurable replacement that records/verifies interactions | Assert email sent exactly once |
| Spy | Observes calls while real behavior may execute | `Mock(wraps=calculator.add)` |

### Dummy

```python
def process(value: int, logger) -> int:
    return value * 2

assert process(3, object()) == 6
```

The second argument only fills the required parameter. The test does not use it, configure it, or verify a call.

A more explicit dummy can fail if accidentally used:

```python
class DummyNotifier:
    def send(self, message: str) -> None:
        raise AssertionError("Notifier should not be used")
```

Use a dummy only when the dependency is irrelevant to the tested behavior.

### Stub

```python
class StubUserRepository:
    def get_user(self, user_id: int) -> dict[str, object]:
        return {"id": user_id, "name": "Alice"}

def get_user_name(user_id: int, repository) -> str:
    return repository.get_user(user_id)["name"]

assert get_user_name(1, StubUserRepository()) == "Alice"
```

The stub provides controlled data. It is simple, fast, and deterministic, but it can be unrealistic if its response does not reflect the real contract. Stubs are useful for success, empty, missing, and failure responses.

### Fake

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

A fake is a simplified but working implementation. It can support realistic state changes without starting PostgreSQL or another service. But it does not prove production SQL, constraints, transactions, isolation, indexes, permissions, or driver behavior. Use real integration tests for those.

### Mock

A mock can control responses and record interactions:

```python
from unittest.mock import Mock

email = Mock()
email.send("alice@example.test", "Welcome")
email.send.assert_called_once_with("alice@example.test", "Welcome")
```

Use interaction verification when the interaction itself is part of the contract—for example, a payment must be charged exactly once or a message must be published to a specific topic.

### Spy

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

The real method runs; the spy observes the call. Use this only when observing the interaction adds meaningful evidence.

## 3. State verification versus interaction verification

**State verification** checks the result or externally observable state:

```python
assert account.balance == 90
assert response.status == "accepted"
assert output == expected_output
```

**Interaction verification** checks collaboration:

```python
payment_client.charge.assert_called_once_with(
    order_id="A-100",
    amount_cents=5000,
)
```

State-focused tests often survive refactoring. Interaction checks are important when the side effect itself matters, such as exactly-once charging, publishing a message, invalidating a cache, or invoking authorization. Excessive interaction assertions make tests brittle; too few may miss important side effects. Choose based on the contract.

## 4. Python's `unittest.mock` toolkit

`unittest.mock` is part of Python's standard library. No paid service or third-party mocking package is required for the core examples.

```python
from unittest.mock import (
    ANY, DEFAULT, AsyncMock, MagicMock, Mock,
    PropertyMock, call, create_autospec, mock_open,
    patch, sentinel,
)
```

It provides configurable mock objects, temporary patching, call history, async mocks, property/file helpers, and interface constraints.

### `Mock`

```python
mock = Mock(name="payment_client")
mock.charge.return_value = {"status": "accepted"}

result = mock.charge("order-123", 5000)
assert result["status"] == "accepted"
mock.charge.assert_called_once_with("order-123", 5000)
```

A `Mock` creates callable child attributes as needed, records calls, and can be configured.

Important properties:

- `return_value`: value returned when the mock is called.
- `side_effect`: exception, callable, or sequence controlling calls.
- `called`: whether it has been called.
- `call_count`: number of calls.
- `call_args`: most recent call.
- `call_args_list`: all direct calls.
- `method_calls`: calls to child methods/attributes.
- `mock_calls`: broader history, including chained child calls.
- `reset_mock()`: resets call history; it does not automatically remove configured behavior.

Call assertions:

| Assertion | Meaning |
|---|---|
| `assert_called()` | At least one call |
| `assert_called_once()` | Exactly one call |
| `assert_called_with(...)` | Most recent call has these arguments |
| `assert_called_once_with(...)` | Exactly one call with these arguments |
| `assert_any_call(...)` | At least one matching call |
| `assert_has_calls([...])` | Required calls appear; ordering depends on `any_order` |
| `assert_not_called()` | No call |

Call history example:

```python
worker = Mock()
for value in [1, 2, 3]:
    worker(value)

assert worker.call_count == 3
assert [item.args[0] for item in worker.call_args_list] == [1, 2, 3]
```

Fresh mocks per test are generally clearer than sharing and resetting mutable call history. Deep chains such as `client.users.accounts.billing.fetch()` often signal an overly broad production interface.

### `MagicMock`

`MagicMock` is like `Mock`, but supports many Python special/dunder methods such as context management, indexing, iteration, and length.

```python
items = MagicMock()
items.__len__.return_value = 3
items.__getitem__.side_effect = ["a", "b", "c"]

assert len(items) == 3
assert items[0] == "a"
```

Context manager:

```python
resource = MagicMock()
resource.__enter__.return_value = "HANDLE"

with resource as handle:
    assert handle == "HANDLE"

resource.__enter__.assert_called_once()
resource.__exit__.assert_called_once()
```

Use ordinary `Mock` for normal calls/attributes. Use `MagicMock` only when the tested code relies on special Python protocols; extra behavior is not automatically better.

### `return_value`

```python
mock = Mock()
mock.return_value = 42
assert mock() == 42

client = Mock()
client.fetch_user.return_value = {"id": 1, "name": "Alice"}
```

This is a simple stub-like setup. Configure the response shape the application actually consumes. A nested attribute left unconfigured may return another mock rather than a string/dict expected by the application.

### `side_effect`

Three main forms:

1. **Exception** — force a failure:

```python
client.fetch.side_effect = TimeoutError("service timed out")
```

2. **Callable** — compute a response for each call:

```python
def respond(user_id: int) -> dict[str, object]:
    if user_id == 1:
        return {"id": 1, "name": "Alice"}
    raise KeyError(user_id)

client.fetch.side_effect = respond
```

3. **Iterable** — provide sequential results/exceptions:

```python
client.fetch.side_effect = [
    TimeoutError("first attempt"),
    {"status": "ok"},
]
```

Each call consumes the next item. This is useful for retries. It is stateful: reusing the mock after the iterable is consumed can produce `StopIteration`. A callable side effect is called later by the mock; it is not the result of calling the function during setup.

### `call`, `ANY`, `sentinel`, and `DEFAULT`

`call` constructs expected call records:

```python
mailer.send.assert_has_calls([call("A"), call("B")])
```

`ANY` matches any value in one argument position:

```python
client.send("orders", request_id)
client.send.assert_called_once_with("orders", ANY)
```

Use it only for genuinely nondeterministic/non-contractual values; too many `ANY` values weaken assertions.

`sentinel` creates unique readable marker objects:

```python
client.send(sentinel.request_id)
client.send.assert_called_once_with(sentinel.request_id)
```

`DEFAULT` tells a `side_effect` function to fall back to the mock's configured `return_value`:

```python
mock = Mock(return_value="normal")

def effect(value: int):
    if value < 0:
        return "special"
    return DEFAULT

mock.side_effect = effect
assert mock(-1) == "special"
assert mock(2) == "normal"
```

## 5. Patching: temporary replacement of names and attributes

Patching temporarily replaces a name/object attribute and restores it when the context exits. Prefer context managers or decorators because cleanup is automatic.

```python
with patch("service.get_current_user") as mock_get_user:
    mock_get_user.return_value = {"id": 1}
    ...
```

Manual `start()`/`stop()` patcher lifecycle exists, but requires careful cleanup in `finally`; use it only when needed.

### The most important rule: patch where used

Suppose:

```python
# utils.py
def get_data():
    return "real-data"

# service.py
from utils import get_data

def process():
    return get_data()
```

The import binds `get_data` in the `service` module. Therefore:

```python
with patch("service.get_data", return_value="fake"):
    assert service.process() == "fake"
```

Patching `utils.get_data` may not replace the already-bound name in `service`. Always ask: **which exact name does the system under test look up at runtime?**

### `patch.object()`

Replaces an attribute on an object or class:

```python
client = TokenClient()
with patch.object(client, "get_token", return_value="test-token"):
    assert client.get_token() == "test-token"
```

It can target instance methods, class methods/attributes, or other attributes. For class methods, `autospec=True` can preserve signature/binding behavior more faithfully.

### `patch.dict()`

Temporarily changes a mapping such as `os.environ`, then restores it:

```python
with patch.dict(os.environ, {"APP_MODE": "test"}):
    assert os.environ["APP_MODE"] == "test"
```

`clear=True` can replace the visible mapping contents, but use carefully. Never put real credentials or tokens in fixtures.

### `patch.multiple()`

Changes several attributes on one target in one context:

```python
with patch.multiple(MyService, timeout=1, retries=2):
    ...
```

Use when the changes form one coherent setup; separate patches may be clearer when their reasons differ.

### `spec`, `spec_set`, `autospec`, `create_autospec`

Unrestricted mocks are permissive and can hide misspelled attributes or invalid calls.

```python
class EmailClient:
    def send_email(self, to: str, subject: str, body: str) -> None:
        ...

client = create_autospec(EmailClient, instance=True)
client.send_email("a@example.test", "Subject", "Body")
```

- `spec`: restricts available attributes to the target interface.
- `spec_set`: also restricts setting attributes not present on the target.
- `autospec=True`: creates mocks based on the target's interface and signatures.
- `create_autospec()`: creates an autospecced mock directly.

Autospec helps catch interface/signature mistakes but does not prove semantic compatibility with a real external provider.

### `PropertyMock`

Properties are descriptors accessed as attributes. Patch the property on the class:

```python
class User:
    @property
    def is_admin(self) -> bool:
        return False

user = User()
with patch.object(type(user), "is_admin", new_callable=PropertyMock) as prop:
    prop.return_value = True
    assert user.is_admin is True
    prop.assert_called_once_with()
```

### `mock_open()`

A simple replacement for `open()` that supports `with`:

```python
def read_config(path: str) -> str:
    with open(path, "r", encoding="utf-8") as file:
        return file.read()

opener = mock_open(read_data="mode=test\n")
with patch("builtins.open", opener):
    assert read_config("config.txt") == "mode=test\n"
opener.assert_called_once_with(
    "config.txt", "r", encoding="utf-8"
)
```

For writing, assert both the `open()` arguments and `opener().write(...)`. `mock_open` is a simplified model; use a real temporary directory/file when path, permissions, newline, or filesystem semantics are part of the requirement. `pyfakefs` is a third-party option, not standard library.

### `AsyncMock`

Use `AsyncMock` for asynchronous callables; an ordinary `Mock` may return a non-awaitable value and cannot correctly record awaiting.

```python
api = AsyncMock(return_value={"ok": True})
result = await api("/health")

assert result == {"ok": True}
api.assert_awaited_once_with("/health")
```

Await-related inspection includes `assert_awaited()`, `assert_awaited_once()`, `assert_awaited_with()`, `assert_awaited_once_with()`, `await_count`, `await_args`, and `await_args_list`. Async context managers use methods such as `__aenter__` and `__aexit__`. A mocked async tool test checks orchestration, not real provider latency or reliability.

## 6. Mocking failures, retries, time, randomness, and environment

A key benefit of test doubles is forcing rare failures predictably.

```python
def load_profile(client):
    try:
        return client.fetch()
    except TimeoutError:
        return {"status": "degraded"}
```

Test:

```python
client = Mock()
client.fetch.side_effect = TimeoutError("temporary outage")
assert load_profile(client) == {"status": "degraded"}
```

Retry example:

```python
def fetch_with_retry(client, attempts=3):
    last_error = None
    for _ in range(attempts):
        try:
            return client.fetch()
        except TimeoutError as exc:
            last_error = exc
    raise last_error
```

Configure sequential `side_effect` values to test timeout then success, exhausted retries, and final error. Assert attempt count when it is part of the contract. Avoid asserting arbitrary sleep calls unless backoff timing itself is the behavior being tested.

Time, randomness, UUIDs, and timestamps are nondeterministic inputs. Prefer dependency injection:

```python
class Clock(Protocol):
    def now(self) -> datetime: ...

class FixedClock:
    def now(self) -> datetime:
        return datetime(2030, 1, 2, tzinfo=timezone.utc)
```

Likewise, inject a random/token source:

```python
def make_id(token_source=token_hex) -> str:
    return token_source(4)
```

Patching legacy time APIs can be useful, but an injected clock/random source is often clearer.

Environment variables are global process state. Use `patch.dict()` or pytest's `monkeypatch` so changes are undone:

```python
def test_feature_enabled(monkeypatch):
    monkeypatch.setenv("FEATURE_X", "on")
    assert is_feature_enabled() is True
```

Never store real secrets in source control, tests, fixtures, or CI logs.

## 7. Filesystems, databases, HTTP APIs, queues, and cloud services

Choose the test mechanism based on what must be proven.

| Dependency | Unit-level double | Real integration evidence |
|---|---|---|
| Filesystem | `mock_open` for simple call/content behavior | `tmp_path`/temporary directory for actual OS semantics |
| Database | Mock/stub repository for business logic | Real controlled DB for SQL, schema, transactions, constraints |
| HTTP API | Mock response/client for local client logic | Contract test, sandbox, or controlled endpoint |
| Message queue | Mock broker for message construction/handler decisions | Real/test broker for ack, ordering, visibility, duplicates, dead letters |
| Cloud service | Mock SDK boundary for requested arguments | Emulator/test account for IAM, encryption, region, network, SDK/service behavior |

### Database example

```python
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

This verifies business logic and the repository interaction. It does not prove SQL is valid or transactions work.

### HTTP example

A client test can configure a response with `status_code=200` and `json.return_value={"status": "paid"}`. Also cover timeout, 401/403, 404, 429, 500/503, malformed JSON, missing fields, and retryable failures. A mock validates local code against a simulated response, not the current provider contract.

### Queue example

A mock broker can verify message construction, acknowledgement decisions, retry, and dead-letter routing. A real broker/test instance is needed for delivery semantics, ordering, duplicate delivery, visibility timeouts, and acknowledgement behavior.

### Cloud example

Mocks validate requested bytes/metadata/arguments. Real integration evidence is required for bucket policy, permissions, encryption, region, networking, SDK behavior, and actual cloud service semantics. Use isolated test accounts, least-privilege credentials, and generic data.

## 8. Design for testability: dependency injection, protocols, pure functions

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

Now a test can pass a mock, stub, or fake without patching a constructor. Common forms are function injection, parameter injection, constructor injection, and protocol-based injection.

```python
class UserRepository(Protocol):
    def get_user(self, user_id: int) -> dict[str, object]: ...
```

A production repository and an in-memory fake can both satisfy this structural interface without inheriting from it. Keep protocols narrow; do not reproduce a huge concrete SDK interface.

Pure functions often need no mocks:

```python
def calculate_total(price: int, tax_rate: float) -> int:
    return round(price * (1 + tax_rate))
```

The more business logic is isolated from external side effects, the less mocking is required. Push I/O to boundaries; keep decision logic deterministic and test it directly.

## 9. Over-mocking and mock hell

**Over-mocking** means so many mocks, patches, and interaction assertions are used that tests specify implementation details instead of behavior.

Symptoms:
- huge mock setup and many exact call assertions;
- harmless refactors break tests;
- tests pass while integrations are broken;
- deep `return_value` chains;
- complex fixture factories;
- many constructor patches.

“Mock hell” is the informal version: `mock.a.return_value.b.return_value.c...`.

Improve it by identifying the business contract, introducing a narrow interface, injecting that interface, preferring a fake/simple stub when appropriate, and retaining only meaningful interaction assertions. If test setup is much larger than the behavior, inspect the design.

## 10. pytest, monkeypatch, AAA, boundaries, regression, and debugging

pytest works naturally with `unittest.mock`: tests can use fixtures, parametrization, `pytest.raises`, and mocks together. Create a fresh stateful mock per test unless sharing is deliberate.

pytest's `monkeypatch` fixture temporarily modifies attributes, mappings, environment variables, and working directory; it automatically undoes changes. Operations include `setattr`, `setitem`, `delattr`, `delitem`, `setenv`, `delenv`, `chdir`, and `context()` for nested cleanup.

Use `patch` when mock-specific behavior/call assertions are needed; use `monkeypatch` when temporary process/name changes are the main goal. Both must patch the name used by the system under test.

Mocking fits AAA:

```text
Arrange → configure test double
Act     → call system under test
Assert  → verify result/state and only meaningful interactions
```

Mocks can force boundary cases—timeout, missing dependency, empty/malformed/oversized response, auth failure, throttling—but cannot replace real boundary validation.

Regression workflow: reproduce defect → encode exact dependency behavior with a controlled double → observe failing test → fix → keep regression test. When a mock-based test fails, read the traceback and ask whether the application, test setup, patch target, response shape, side effect, spec, or mock contract is wrong.

## 11. Applications to data pipelines, ML, LLMs, agents, and contracts

### Data pipelines

```text
input → parser → validator → transformer → database → object storage
```

Use small fixtures for parser/validator tests; mock repository/storage boundaries for deterministic unit tests of orchestration. Still integration-test serialization, schema, database, and object-store behavior.

```python
def run_pipeline(record, repository, storage):
    clean = transform(record)
    repository.save(clean)
    storage.put(clean)
```

A unit test can assert both outputs received the transformed record. It does not prove the actual database/object store works.

### ML systems

Mock `model.predict()` to test application branching, fallback, input validation, response formatting, and error handling. Stub feature-store data for missing-feature scenarios. This does not validate model quality, calibration, drift, data quality, feature correctness, or scientific validity; use real models and evaluation datasets for those.

### LLM applications

Mock provider responses to test parsing, schema validation, retries, fallback, tool-call handling, limits, and malformed responses. A mocked response does not test actual model quality, reasoning, prompt sensitivity, latency, provider safety behavior, or output distribution. Real evaluation and selected provider integration tests remain necessary.

### Agentic AI systems

Mock LLM/tool/search/database boundaries to test routing, state transitions, tool invocation, argument construction, retries, fallback, errors, and stop conditions. Do not infer real model/tool/retrieval quality from a mocked test. Test observable state and tool calls, not hidden reasoning.

### Contract testing

Mocks can become stale. For example, a mock may return `{"status": "success"}` while the provider changes to `{"state": "success"}`. Unit tests still pass, production breaks. Contract testing validates that consumer assumptions match provider contracts through schemas, provider/consumer tests, API specifications, or integration environments.

## 12. Common mistakes and complete realistic example

Twenty recurring mistakes and their remedies:

1. Patch wrong location → patch runtime lookup name.
2. Mock everything → add contract/integration/E2E coverage.
3. Mock private implementation → assert observable behavior.
4. Overuse exact call assertions → assert only contractual interactions.
5. Forget autospec → constrain important Python interfaces.
6. Misconfigure `side_effect` → distinguish exception/callable/iterable.
7. Confuse Mock/MagicMock → use MagicMock for protocols/dunder methods.
8. Mock async with Mock → use AsyncMock and await assertions.
9. Assume mocked DB proves SQL → real DB integration test.
10. Assume mocked API proves provider → contract/sandbox integration.
11. Use unrealistic fake responses → use documented/sanitized representative payloads.
12. Test mock setup, not application → assert outcome and necessary interactions.
13. Deep mock chains → narrow interfaces or fakes.
14. Giant fixtures → keep setup focused.
15. Leave patch active → context manager/decorator/monkeypatch.
16. Mock pure functions → call them directly.
17. Ignore failure paths → use side_effect/stubs.
18. Ignore integration boundaries → add contract/integration tests.
19. Unconstrained mocks drift → autospec/protocols/contracts.
20. Ignore contract tests → validate external assumptions independently.

### User registration service

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

Test:

```python
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
    "alice@example.test", "Alice"
)
```

This verifies service behavior and welcome-email interaction. Configure `email_service.send_welcome.side_effect = TimeoutError(...)` to test the documented failure/retry policy. Add real integration coverage for DB schema/transactions, email provider protocol, auth, and delivery when critical.

## 13. Mini-project: Resilient External API Client

The source's project is self-contained and requires no paid API or credentials. It injects a transport interface:

```text
Application → ResilientClient → Transport Protocol
                              → production HTTP transport
Unit tests → Mock transport
Integration → local server/sandbox
```

Files:

```text
resilient-client/
├── models.py
├── client.py
└── test_client.py
```

`models.py`:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ApiResponse:
    status_code: int
    payload: dict[str, object]
```

`client.py`:

```python
import time
from dataclasses import dataclass
from typing import Protocol
from models import ApiResponse

class Transport(Protocol):
    def get(self, path: str, timeout: float) -> ApiResponse: ...

class RetryableStatusError(Exception):
    """Raised for HTTP statuses treated as retryable."""

@dataclass
class ResilientClient:
    transport: Transport
    attempts: int = 3
    backoff_seconds: float = 0.0

    def __post_init__(self) -> None:
        if self.attempts < 1:
            raise ValueError("attempts must be at least 1")

    def get_json(self, path: str) -> dict[str, object]:
        last_error: Exception | None = None
        for attempt in range(1, self.attempts + 1):
            try:
                response = self.transport.get(path, timeout=2.0)
                if response.status_code == 200:
                    return response.payload
                if response.status_code in {429, 500, 502, 503, 504}:
                    raise RetryableStatusError(
                        f"retryable status: {response.status_code}"
                    )
                raise ValueError(
                    f"non-retryable status: {response.status_code}"
                )
            except (TimeoutError, RetryableStatusError) as exc:
                last_error = exc
                if attempt == self.attempts:
                    raise
                time.sleep(self.backoff_seconds)
        raise AssertionError(f"unreachable: {last_error}")
```

`test_client.py` (main cases):

```python
from unittest.mock import Mock
import pytest
from client import ResilientClient, RetryableStatusError
from models import ApiResponse

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

def test_non_retryable_status_is_not_retried():
    transport = Mock()
    transport.get.return_value = ApiResponse(400, {})
    client = ResilientClient(transport, attempts=3)
    with pytest.raises(ValueError, match="non-retryable status: 400"):
        client.get_json("/items/1")
    transport.get.assert_called_once_with("/items/1", timeout=2.0)

@pytest.mark.parametrize("status", [429, 500, 502, 503, 504])
def test_retryable_status_then_success(status):
    transport = Mock()
    transport.get.side_effect = [
        ApiResponse(status, {}),
        ApiResponse(200, {"value": 42}),
    ]
    client = ResilientClient(transport, attempts=2)
    assert client.get_json("/items/1") == {"value": 42}
    assert transport.get.call_count == 2

def test_exhausted_retryable_status_raises_final_error():
    transport = Mock()
    transport.get.return_value = ApiResponse(503, {})
    client = ResilientClient(transport, attempts=2)
    with pytest.raises(RetryableStatusError, match="retryable status: 503"):
        client.get_json("/items/1")
    assert transport.get.call_count == 2

def test_unrelated_runtime_error_is_not_retried():
    transport = Mock()
    transport.get.side_effect = RuntimeError("bug in transport")
    client = ResilientClient(transport, attempts=3)
    with pytest.raises(RuntimeError, match="bug in transport"):
        client.get_json("/items/1")
    transport.get.assert_called_once_with("/items/1", timeout=2.0)

@pytest.mark.parametrize("attempts", [0, -1])
def test_attempts_must_be_at_least_one(attempts):
    with pytest.raises(ValueError, match="attempts must be at least 1"):
        ResilientClient(Mock(), attempts=attempts)
```

Run from the project directory with Python 3.10+:

```bash
python -m pytest
```

`attempts` means total attempts including the first and must be at least one. The tests validate retry/status logic against a mock transport, not the real HTTP transport or provider. A real integration test against a controlled endpoint/sandbox is still required. Production may inject a sleep/backoff function to make timing policy easier to test.

## 14. Production strategy, security, and final mental model

A mature test strategy is a portfolio:

| Layer | Typical setup | What it proves |
|---|---|---|
| Unit | Mock/stub/fake | Fast local behavior |
| Contract | Provider/consumer contract and realistic payloads | Interface compatibility |
| Integration | Real test dependency/emulator | Boundary semantics |
| E2E | Realistic stack | Important workflow |

Choose mocks for slow, costly, nondeterministic, side-effecting, or hard-to-fail dependencies when testing local behavior. Use real resources when SQL, filesystem, provider, queue, cloud, or transaction semantics are the requirement. Balance risk, cost, volatility, speed, realism, and maintenance—not a fixed test percentage.

Security rules:
- never put real API keys or production credentials in code/fixtures;
- avoid real customer/payment data;
- sanitize logs and recordings;
- avoid destructive production operations;
- use test accounts/sandboxes and least-privilege credentials;
- protect sensitive fixtures;
- make test configuration clearly non-production;
- minimize/protect AI prompts and responses containing sensitive information.

Core sequence:

```text
understand behavior
→ identify external boundary
→ decide what must be proven
→ test pure logic directly
→ choose smallest useful double
→ control failures/nondeterminism
→ patch the lookup name
→ verify outcome and important interactions
→ add contract/integration/E2E evidence where needed
→ review for over-mocking and false confidence
```

**Mocking is a technique, not a testing strategy.** A strong engineer can explain why a dependency is isolated and where real integration evidence comes from.

---

# Part B — Roadmap and Current-Level Assessment

## 1. Exact roadmap position

The attachment is **Module 07 — Testing and Systematic Debugging, Lesson 07 — Mocking and Test Doubles**. The lesson itself labels its roadmap position as Stage 1, Module 1.7; the broader Stage 1 tree uses folder `07-Testing-and-Systematic-Debugging`.

Module 07 sequence:

1. Test Levels: Unit, Integration, and End-to-End — completed.
2. Pytest: Assertions, Fixtures, and Parametrization — completed.
3. Arrange–Act–Assert and Test Design — completed.
4. Boundary, Invalid, and Regression Tests — completed.
5. Debuggers, Breakpoints, and Call Stacks — completed.
6. Tracebacks, Logging, and Minimal Reproductions — completed.
7. Mocking and Test Doubles — current lesson.
8. Module README and practice questions.

The Stage 1 tree also progresses through computational thinking; Python core/data types; control flow/functions/scope/errors; problem-solving/collections/algorithmic habits; files/structured data/CLI; modules/packages/dependencies/code quality; OOP/data modelling/functional style; advanced production-oriented Python; production habits; advanced data model/object design; metaprogramming; standard library; bytes/binary/text; modern Python; advanced testing; profiling/performance; packaging; CPython internals; design patterns/API design; visualization/notebooks; secure Python; code reading/refactoring/review; and functions/OOP gap lessons.

## 2. Current skills and project relevance

You have already studied Python fundamentals, collections, functions, exceptions, file/CSV/JSON handling, paths, CLI, logging, configuration, modules/packages, dependencies, Ruff, typing, documentation, pytest, fixtures, parametrization, AAA, boundaries, regression, debugger operations, tracebacks, logging, and MREs. That is the correct prerequisite foundation for this lesson.

Your four Stage 1 projects are:

1. **Personal Expense Ledger CLI** — validation, calculations, persistence, CLI, tests.
2. **Log Investigation and Reliability CLI** — diagnostic records, parsing, reporting, and failure investigation.
3. **Data Quality and Transformation Pipeline** — `orders.csv`; `dqpipe` package (`cli.py`, `config.py`, `pipeline.py`, `rules.py`); tests, configuration, data contract.
4. **Rule-Based Risk Review Engine** — `transactions.csv`, `rules.toml`; `riskreview` package (`cli.py`, `engine.py`, `io.py`, `models.py`, `rules.py`); tests and golden decision data.

Mocking is directly useful for isolating pipeline orchestration from storage, testing rule-engine business logic without a database, simulating malformed external records, and testing failure/retry behavior. Real integration tests must still validate CSV/file behavior, schemas, persistence, and actual interfaces.

**Current level:** beginner progressing toward intermediate Python engineering. The exercises below use functions, classes, protocols, dictionaries, exceptions, pytest, and previously learned test concepts. Async examples are included because the lesson explicitly teaches `AsyncMock`; treat them as focused examples rather than a requirement to advance into a separate async-programming module.

---

# Part C — All 24 Coding Exercises with Step-by-Step Solutions

## Beginner

### 1. Identify the double

```python
def process(value: int, logger) -> int:
    return value * 2

assert process(3, object()) == 6
```

`object()` fills the required logger parameter. The function never uses it, so it is a **dummy**, not a mock.

### 2. Create a stub

```python
class StubRepository:
    def get_user(self, user_id: int) -> dict[str, object]:
        return {"id": user_id, "name": "Alice"}
```

The class defines the test dependency. `get_user()` returns predetermined data; it does not connect to a database.

### 3. Build a fake

```python
class InMemoryRepository:
    def __init__(self) -> None:
        self._data: dict[int, dict[str, object]] = {}

    def save(self, user: dict[str, object]) -> None:
        self._data[int(user["id"])] = user

    def get(self, user_id: int) -> dict[str, object]:
        return self._data[user_id]
```

`__init__` creates local storage. `save()` uses the user's ID as key. `get()` retrieves the stored record. This is working in-memory behavior, not a simulation of production SQL.

### 4. Basic mock

```python
email = Mock()
email.send("alice@example.test", "Welcome")
email.send.assert_called_once_with("alice@example.test", "Welcome")
```

`Mock()` creates the double. `send()` records the call. The assertion verifies exactly one call with both expected arguments.

### 5. `return_value`

```python
client = Mock()
client.fetch.return_value = {"status": "ok"}
assert client.fetch()["status"] == "ok"
```

Configure the child method's result. Calling `fetch()` returns the dictionary; indexing retrieves `"ok"`.

### 6. Exception `side_effect`

```python
client.fetch.side_effect = TimeoutError("timeout")

with pytest.raises(TimeoutError, match="timeout"):
    client.fetch()
```

The configured call raises `TimeoutError`. `pytest.raises` makes the test pass only when the expected exception occurs.

## Intermediate

### 7. Sequential `side_effect`

```python
client.fetch.side_effect = [
    TimeoutError("first"),
    {"status": "ok"},
]
```

First call raises the timeout; second returns success. The iterable is consumed in order, so use a fresh mock for an independent test.

### 8. Inspect call history

```python
worker = Mock()
for value in [1, 2, 3]:
    worker(value)

assert worker.call_count == 3
assert [item.args[0] for item in worker.call_args_list] == [1, 2, 3]
```

The loop makes three calls. `call_count` checks quantity. `call_args_list` stores each call; `.args[0]` reads its first positional argument.

### 9. `call` and `assert_has_calls`

```python
mailer = Mock()
mailer.send("A")
mailer.send("B")
mailer.send.assert_has_calls([call("A"), call("B")])
```

The calls are recorded in order. `call(...)` creates expected call records; `assert_has_calls` verifies the sequence appears.

### 10. `ANY`

```python
client = Mock()
client.send("orders", "generated-id")
client.send.assert_called_once_with("orders", ANY)
```

The destination `"orders"` is contractual. The generated ID is nondeterministic, so `ANY` accepts any value in that position.

### 11. Patch the correct location

If `service.py` contains `from utils import get_data`, patch `service.get_data`:

```python
with patch("service.get_data", return_value="fake"):
    assert service.process() == "fake"
```

The import bound a name inside `service`. `process()` resolves that name there, not by looking it up again in `utils`.

### 12. `patch.object`

```python
with patch.object(client, "fetch", return_value={"ok": True}):
    assert client.fetch() == {"ok": True}
```

The context temporarily replaces the instance's `fetch` method. The original attribute is restored after the block.

### 13. `patch.dict`

```python
with patch.dict(os.environ, {"FEATURE_X": "on"}):
    assert os.environ["FEATURE_X"] == "on"
```

The environment mapping is changed for the block. The patch restores the prior mapping when the block exits.

### 14. `patch.multiple`

```python
with patch.multiple(MyService, timeout=1, retries=2):
    ...
```

Both class attributes are temporarily changed together. They are restored after the context exits.

### 15. Autospec

```python
client = create_autospec(EmailClient, instance=True)
```

The mock is constrained by `EmailClient`'s interface/signatures. It helps detect misspelled methods and incorrect calls, but cannot validate external provider behavior.

### 16. `mock_open`

```python
opener = mock_open(read_data="hello")
with patch("builtins.open", opener):
    read_file("a.txt")
opener.assert_called_once_with("a.txt", "r", encoding="utf-8")
```

`mock_open` provides controlled file content. The patch replaces built-in `open` while `read_file` executes. The final assertion verifies filename, mode, and encoding. Use `tmp_path` for real filesystem semantics.

### 17. `AsyncMock`

```python
async def example_async_test():
    api = AsyncMock(return_value={"ok": True})
    result = await api("/health")
    assert result == {"ok": True}
    api.assert_awaited_once_with("/health")
```

`AsyncMock` behaves like an async callable. `await` obtains the configured result; the await assertion verifies the coroutine was actually awaited with the path.

### 18. Retry testing

```python
client.fetch.side_effect = [
    TimeoutError("temporary"),
    {"status": "ok"},
]
assert fetch_with_retry(client, attempts=2) == {"status": "ok"}
assert client.fetch.call_count == 2
```

The first attempt fails, the second succeeds. The result assertion checks behavior; `call_count` checks the two attempts required by the retry contract.

## Advanced and production-oriented

### 19. Dependency injection

```python
def process(client):
    return client.fetch()
```

Instead of constructing `RealClient()` inside the function, receive the client as an argument. The caller controls the dependency; tests can pass a mock/fake without patching a constructor.

### 20. Protocol boundary

```python
class Repository(Protocol):
    def get(self, user_id: int) -> dict[str, object]: ...
```

The protocol states the minimum operation the service needs. Any object providing a compatible `get()` can be injected. Keep the protocol narrow.

### 21. Database testing strategy

Use a mock/stub repository for the unit test of “inactive user becomes active.” Separately use a real controlled database integration test for SQL, schema, constraints, and transaction behavior. These tests prove different things.

### 22. LLM parser test

```python
llm = Mock()
llm.generate.return_value = '{"intent":"refund"}'
result = parse_intent(llm.generate())
assert result.intent == "refund"
```

The mock returns a deterministic JSON string. The parser converts it into the application result. This proves parser behavior for that payload, not that a real LLM reliably generates it.

### 23. Agent tool routing

```python
llm = AsyncMock(return_value={"tool": "search", "query": "pytest"})
search = AsyncMock(return_value=["doc-1"])

result = await run_agent("Find pytest docs", llm, search)

search.assert_awaited_once_with("pytest")
```

The fake LLM response selects search. The search double supplies a deterministic result. The assertion verifies the orchestrator awaited search with the selected query. It does not validate real model tool-selection quality or retrieval relevance.

### 24. Choose the right test layer

Requirement: “Validate that our SQL query correctly inserts a row under the production schema.”

**Answer:** Integration test against a real controlled database/test database. A mock can verify that `execute()` was called, but cannot prove SQL syntax, schema compatibility, constraints, or transaction behavior.

---

# Part D — All 12 Debugging Labs

1. **Wrong patch target:** `service.py` imported `get_data` directly from `utils`; patch `service.get_data`, not `utils.get_data`, because that is the name resolved at runtime.
2. **Incorrect `return_value` shape:** if code expects `response["name"]`, configure `{"name": "Alice", "status": "ok"}`, not a generic nested `Mock`.
3. **Wrong iterable `side_effect`:** two retry attempts need two configured outcomes. Add the success result after the first timeout; otherwise the next call raises `StopIteration`.
4. **Weak call assertion:** `assert_called_once()` does not validate arguments. If recipient and subject are part of the contract, use `assert_called_once_with("Alice", "Welcome")`.
5. **Incorrect async mock:** an async function must be replaced with `AsyncMock`, then checked with `assert_awaited_once()` or `assert_awaited_once_with(...)`.
6. **Missing autospec:** a loose mock may accept a two-argument `send_email` call even though the real method requires three arguments. Use `create_autospec(EmailClient, instance=True)`.
7. **Mock configured but not injected:** creating `mock = Mock(...)` does not affect `RealClient()`. Pass the mock to `process(mock)` or patch the correct lookup name.
8. **Over-mocked test:** tests assert every private helper call/order in a pure transformation. Test the final behavior and mock only external boundaries.
9. **Nested mock returns another mock:** `client.get_user.return_value.profile.email` may itself be a mock, not a string. Configure an explicit dict/dataclass or use a small fake.
10. **Property patched incorrectly:** a property is a class descriptor. Use `patch.object(type(user), "is_admin", new_callable=PropertyMock)` and set its `return_value`.
11. **Mocked SQL mistaken for DB validation:** `db.execute.assert_called_once()` proves an interaction only. Add a repository integration test against a real controlled DB.
12. **Stale API fixture:** the mock expects `{"status": "success"}` while the provider now returns `{"state": "success"}`. Add contract/integration coverage and maintain representative versioned fixtures.

---

# Part E — Interview, Architecture, and Knowledge Review

## 20 interview questions

1. **Test double?** Replacement for a real dependency during a test.
2. **Stub vs mock?** Stub supplies controlled answers; mock also records/verifies interactions.
3. **Mock vs fake?** Mock is interaction/configuration focused; fake is a simplified working implementation.
4. **Dummy vs stub?** Dummy fills a required slot; stub provides relevant controlled behavior/data.
5. **Patching?** Temporarily replacing a name or attribute during a test.
6. **Why patch where used?** Imports can bind a local name; the system under test resolves that runtime name.
7. **Autospec?** Creates a mock constrained by a target's interface/signature.
8. **Mock vs MagicMock?** MagicMock supports many Python special methods/protocols.
9. **side_effect vs return_value?** Fixed result versus exception/callable/sequence behavior.
10. **Async mocking?** Use AsyncMock and await-specific assertions.
11. **Over-mocking?** Excessive doubles/assertions that couple tests to internals and create false confidence.
12. **When not to mock?** When real SQL, filesystem, API, queue, or integration behavior must be proven.
13. **External API testing?** Mock local client logic; add contract/sandbox integration coverage.
14. **Database testing?** Mock repository for business unit tests; real DB for SQL/schema/transaction behavior.
15. **Retry testing?** Sequence failures/success with side_effect; verify attempts and final outcome.
16. **Mock reliability trade-off?** Faster deterministic tests, but unrealistic mocks can hide integration failures.
17. **LLM application tests?** Mock responses for parser/orchestration; real evaluation for model quality/provider behavior.
18. **Agent tests?** Mock boundaries for deterministic routing/state/tool orchestration; add real evaluations/integrations.
19. **Why prefer fake?** It may provide clearer working behavior than a large set of mock expectations.
20. **Main design lesson?** Explicit narrow dependency boundaries reduce complicated patching.

## 12 architecture questions

1. **Service with five external dependencies:** unit-test core logic with selected doubles; add contracts for APIs/schemas, integration tests for critical real boundaries, and a small E2E journey set.
2. **Which dependencies to mock?** Slow, costly, nondeterministic, side-effecting, or difficult-to-fail dependencies when testing local behavior—not every dependency automatically.
3. **Which need integration tests?** SQL, serialization, provider protocol, queue semantics, IAM/network configuration, and critical cloud integrations.
4. **Prevent stale mocks:** autospec Python interfaces, maintain contract tests, derive sanitized fixtures from documented contracts, and periodically run integration suites.
5. **Payment API:** mock decision/client behavior; simulate timeouts, 429/500, and duplicates; verify idempotency; use provider sandbox/contract tests; never use production credentials.
6. **Database repository:** use real controlled DB tests for SQL, schema, transactions, constraints, and migrations.
7. **Queue consumer:** unit-test handler with message doubles; integration-test ack, retry, duplicate delivery, ordering, and dead-letter behavior.
8. **AI agent:** mock LLM/tools for orchestration and state; validate arguments and transitions; add real-model evaluation, retrieval evaluation, and selected integrations.
9. **Speed vs realism:** fast deterministic unit tests plus sufficient contract/integration/E2E evidence based on risk.
10. **Detect false confidence:** compare mocks to real contracts, run integration tests in CI, and identify critical boundaries with no real validation.
11. **Mocking architecture smells:** deep chains, repeated constructor patches, giant fixtures, excessive private call assertions, and mock-only interfaces.
12. **Reduce mocking through architecture:** isolate side effects, inject dependencies, define narrow protocols/adapters, and keep domain logic pure where practical.

## 20 knowledge-check answers

1. A test double replaces a real dependency in a test.
2. Dummy fills a dependency slot; stub returns controlled behavior/data.
3. Fake is a working simplified implementation; mock verifies interactions.
4. MagicMock supports special/dunder methods and Python protocols.
5. `return_value` supplies a normal result; `side_effect` raises, calls a function, or supplies sequential outcomes.
6. Patching temporarily replaces a reachable name/attribute.
7. Patch where the system under test looks up the dependency.
8. Autospec constrains mocks to the target interface/signature.
9. `spec` constrains available attributes; `spec_set` also restricts setting attributes.
10. `mock_open` replaces `open()` for simple file tests/context-manager use.
11. AsyncMock models async callables and records awaits.
12. `monkeypatch` temporarily changes attributes, mappings, environment, or working directory and restores them.
13. Dependency injection supplies dependencies from outside the function/class.
14. Reduce over-mocking to avoid brittle implementation coupling and false confidence.
15. Mocked API tests do not prove the real API works; add contract/integration coverage.
16. Mocked database tests do not prove SQL works; use a real controlled DB.
17. Mocked LLM tests validate application handling of predetermined responses, not model quality.
18. Agent mocks test routing, tool args, state, retries, and termination behavior.
19. Use a real temporary filesystem when OS filesystem semantics are part of the contract.
20. Explicit narrow dependency boundaries make code easier to test.

---

# Part F — Glossary and Completion Checklist

| Term | Meaning |
|---|---|
| Test double | Replacement for a real dependency in a test |
| Dummy | Placeholder dependency not used by the tested behavior |
| Stub | Supplies predetermined responses |
| Fake | Simplified working implementation |
| Mock | Configurable double that records/verifies interactions |
| Spy | Observes calls while real behavior may execute |
| State verification | Checks result or resulting state |
| Interaction verification | Checks dependency calls |
| `return_value` | Value returned by a mock call |
| `side_effect` | Exception, callable, or sequence controlling calls |
| Patching | Temporary replacement of a name/attribute |
| Autospec | Mock constrained by target interface/signature |
| `spec` / `spec_set` | Attribute constraints on a mock |
| `MagicMock` | Mock with special-method support |
| `AsyncMock` | Mock for asynchronous callables/awaits |
| `PropertyMock` | Mock for property descriptor access |
| `mock_open` | Simplified mock replacement for `open()` |
| Dependency injection | Supplying dependencies from outside |
| Protocol | Structural interface describing required operations |
| Contract test | Checks compatibility at a component/service boundary |
| Over-mocking | Excessive mocks that couple tests to implementation |
| Mock hell | Complicated nested mock setup |
| False confidence | Passing tests that miss important production risks |

Completion checklist:
- [ ] Distinguish dummy, stub, fake, mock, and spy.
- [ ] Choose state vs interaction verification deliberately.
- [ ] Use Mock, MagicMock, patch, patch.object, patch.dict, patch.multiple.
- [ ] Configure return_value and side_effect.
- [ ] Inspect call history and select useful call assertions.
- [ ] Use call, ANY, sentinel, and DEFAULT appropriately.
- [ ] Use autospec/spec/spec_set/create_autospec.
- [ ] Mock properties, file operations, and async functions when appropriate.
- [ ] Patch environment safely and patch where used.
- [ ] Use pytest monkeypatch and dependency injection.
- [ ] Recognize over-mocking/mock hell.
- [ ] Know when real temporary resources/integration tests are better.
- [ ] Separate mocked application tests from contract/integration tests.
- [ ] Apply the approach to pipelines, ML, LLM, and agentic workflows without overclaiming what mocks prove.
- [ ] Keep test credentials/data safe.

**Lesson status:** Module 07, Lesson 07 — Mocking and Test Doubles — covered in this guide. The Module 07 cumulative README/practice questions and later modules are not started by this document. Wait for the learner's instruction before advancing.
