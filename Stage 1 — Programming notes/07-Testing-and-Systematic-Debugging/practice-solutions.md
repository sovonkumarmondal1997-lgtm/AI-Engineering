# Module 07 — Testing and Systematic Debugging
## Cumulative Practice Questions: 28 Complete Solutions

**Scope:** Stage 1 · Module 07 — Testing and Systematic Debugging  
**Supporting knowledge:** Module 06 — imports, packages, dependency boundaries, type hints, and test-environment dependencies  
**Purpose:** Complete all 28 questions with readable Python/pytest examples and line-by-line explanations.

---

## 1. Learning position and project-tree assessment

The supplied practice set contains **28 questions** arranged in four bands: Basic (1–7), Moderate (8–14), Hard (15–21), and Advanced (22–28). It draws on the Module 07 lessons already covered:

- Test levels: unit, integration, and end-to-end (E2E).
- Pytest assertions, fixtures, fixture teardown, and parametrization.
- Arrange–Act–Assert (AAA), test design, and strong behavioral assertions.
- Boundary, invalid-input, and regression testing.
- Debuggers, breakpoints, stepping, variables, and call stacks.
- Tracebacks, exception propagation/chaining, logging, and minimal reproducible examples.
- Test doubles: dummy, stub, fake, mock, and spy.
- `unittest.mock`: `Mock`, `side_effect`, `return_value`, `ANY`, `sentinel`, patching, call history, `spec`, `spec_set`, autospec, `mock_open`, `AsyncMock`, and property patching.
- Integration strategy for files, databases, APIs, data pipelines, LLM applications, and agentic workflows.

The practice set also intentionally uses selected Module 06 concepts: import lookup locations, `src/` package layout, `Protocol`, dependency injection, and installed test dependencies.

### Current level

The recorded learning sequence places you at **Stage 1 → Module 07**, with Lessons 01–07 completed. You have already studied the Python foundations needed for these exercises: functions, exceptions, collections, files, CLI programs, logging, configuration, imports, package layout, dependency management, Ruff, type hints, and documentation. Your current level is best described as **beginner progressing toward intermediate**: you can now work with practical pytest tests and test doubles, while the advanced questions are intended to develop engineering judgment rather than assume production experience.

### How the existing Stage 1 projects connect

1. **Personal Expense Ledger CLI:** unit-test calculations and validation; use temporary files for file integration; test CLI behavior at its public boundary.
2. **Log Investigation and Reliability CLI:** test parsing and filtering as units; use real temporary log files for filesystem integration; test exit codes and stdout/stderr behavior.
3. **Data Quality and Transformation Pipeline (`orders.csv`, `dqpipe`):** unit-test parsing, validation, transformation, and quality rules; integrate with a real controlled database or file boundary where relevant; do not claim a mocked writer proves persistence.
4. **Rule-Based Risk Review Engine (`transactions.csv`, `rules.toml`, `riskreview`):** unit-test deterministic rules and decisions; test configuration/file boundaries with temporary resources; verify end-to-end decisions through the CLI or public application interface.

The solutions below stay within the concepts taught in Modules 06–07. Some questions refer to application functions/classes such as `UserService`, `process_order`, or `run_agent` without supplying their implementations. Those names are treated as the exercise's assumed system-under-test interface; the test examples show how to exercise that interface, not an invented implementation.

---

# Basic — Questions 1–7

## Question 1 — Classify the test level

**Answer**

1. `calculate_tax()` with no external dependency: **unit test**.
2. Repository using a real SQLite database: **integration test**.
3. Application startup followed by a complete registration workflow: **E2E test**.

**Reasoning**

- A unit test checks one local behavior, such as a pure calculation, while keeping external infrastructure out.
- An integration test checks whether application code works with a real boundary—in this case, SQLite.
- An E2E test checks a complete user-visible workflow across the application.

Unit tests are normally fastest. E2E tests are normally broadest and usually slower and more expensive to maintain. Pytest does not determine the test level; the behavior and boundary do.

## Question 2 — Write a precise pytest assertion

```python
def test_double_returns_twice_the_input():
    # Arrange
    value = 7

    # Act
    result = double(value)

    # Assert
    assert result == 14
```

**Line-by-line**

- `def test_double_returns_twice_the_input():` — pytest discovers this function because its name begins with `test_`.
- `value = 7` — Arrange: define the input.
- `result = double(value)` — Act: execute the behavior once and store its result.
- `assert result == 14` — Assert: verify the exact contract, not merely that the result is truthy.

If the function returns `15`, pytest's assertion introspection reports the failed expression and compared values. This is more useful than a vague `assert result`.

## Question 3 — Fixture plus AAA

```python
import pytest

@pytest.fixture
def user_service():
    return UserService()

def test_get_user_returns_expected_name(user_service):
    # Arrange
    user_id = 1

    # Act
    user = user_service.get_user(user_id)

    # Assert
    assert user["name"] == "Alice"
```

**Line-by-line**

- `import pytest` — imports the test framework.
- `@pytest.fixture` — registers the following function as a fixture.
- `user_service()` — creates the reusable service dependency.
- `return UserService()` — provides a service instance to each test that requests it.
- `test_get_user_returns_expected_name(user_service)` — pytest injects the fixture because the parameter name matches the fixture name.
- `user_id = 1` — scenario-specific Arrange data stays visible in the test.
- `user_service.get_user(user_id)` — Act: call the behavior under test.
- `assert user["name"] == "Alice"` — Assert the required observable result.

This assumes `UserService` is provided by the application. Keep fixtures focused; do not hide the whole scenario inside a giant fixture.

## Question 4 — Parametrize valid quantity boundaries

```python
import pytest

@pytest.mark.parametrize(
    "quantity",
    [1, 2, 99, 100],
    ids=["min", "min-plus-one", "max-minus-one", "max"],
)
def test_quantity_boundaries_are_valid(quantity):
    assert validate_quantity(quantity) is True
```

**Line-by-line**

- `pytest.mark.parametrize` tells pytest to run the same test function for multiple inputs.
- `"quantity"` names the test parameter that receives each value.
- `[1, 2, 99, 100]` covers the inclusive minimum, one above it, one below the maximum, and the maximum.
- `ids=[...]` gives each generated case a useful name in test output.
- `quantity` receives one value per run.
- `validate_quantity(quantity)` executes the validator.
- `is True` checks the specified Boolean result exactly.

The valid interval is `[1, 100]`. Invalid just-outside values such as `0` and `101` belong in negative tests.

## Question 5 — Assert invalid input and its exception

```python
import pytest

def test_validate_age_rejects_zero():
    with pytest.raises(ValueError, match="age must be positive"):
        validate_age(0)
```

**Line-by-line**

- `pytest.raises(...)` tells pytest that the enclosed operation must raise the specified exception.
- `ValueError` is the expected exception type.
- `match=...` checks a meaningful message fragment without requiring an unnecessarily brittle full-message comparison.
- `validate_age(0)` is the single operation expected to fail.

Keep only the expected failing operation inside the context manager. Otherwise, an unrelated `ValueError` could make the test pass.

Alternative when you need to inspect the exception:

```python
with pytest.raises(ValueError) as exc_info:
    validate_age(0)

assert "age must be positive" in str(exc_info.value)
```

`exc_info.value` is the captured exception object; `str(...)` obtains its message.

## Question 6 — Read a traceback and add safe logging

The immediate failure is:

- Exception: `ValueError`.
- Location: `service.py`, line 18, in `process_order`.
- Failing operation: `int(order["amount"])`.
- Likely input defect: `'10O'` contains the letter `O`, not the digit `0`.

```python
import logging

logger = logging.getLogger(__name__)

logger.warning(
    "invalid order amount format; order_id=%s",
    order["id"],
)
```

**Line-by-line**

- `import logging` — imports Python's standard logging module.
- `logging.getLogger(__name__)` — creates/retrieves a module-named logger.
- `logger.warning(...)` — records a warning-level diagnostic.
- The message identifies the failure category and includes a safe order identifier.
- `order["id"]` is passed as a formatting argument; do not log the full order dictionary if it may contain customer or payment data.

A traceback shows where the exception surfaced. A log can add carefully selected runtime context. Neither automatically proves the complete root cause.

## Question 7 — Mock an email dependency and verify the interaction

```python
from unittest.mock import Mock, ANY

def test_registration_sends_welcome_email():
    email_service = Mock()
    user = {"id": 42, "email": "alice@example.test"}

    register_user(user, email_service)

    email_service.send.assert_called_once_with(
        to="alice@example.test",
        subject="Welcome",
        body=ANY,
    )
```

**Line-by-line**

- `Mock` creates a test double that records calls.
- `ANY` is a matcher for an argument whose exact value is not part of this test's contract.
- `email_service = Mock()` replaces the real email-provider dependency.
- `user = {...}` provides controlled test data.
- `register_user(...)` executes the application behavior with the mock injected.
- `assert_called_once_with(...)` verifies one call and the important keyword arguments.
- `body=ANY` avoids coupling this test to an irrelevant or variable body string.

A useful call-history assertion checks the recipient and subject, not merely that some method was called. `sentinel` can provide a unique identity marker when needed; `reset_mock()` clears recorded call history when a deliberately reused mock needs a fresh observation phase.

---

# Moderate — Questions 8–14

## Question 8 — Fixture factory and parametrized roles

```python
import pytest

@pytest.fixture
def user_factory():
    created = []

    def make_user(role: str) -> dict[str, str]:
        user = {"name": "Alice", "role": role}
        created.append(user)
        return user

    yield make_user
    created.clear()

@pytest.mark.parametrize(
    "role",
    ["admin", "viewer"],
    ids=["admin", "viewer"],
)
def test_user_role_is_preserved(user_factory, role):
    # Arrange
    user = user_factory(role)

    # Act
    result = user["role"]

    # Assert
    assert result == role
```

**Line-by-line**

- `@pytest.fixture` registers the factory fixture.
- `created = []` tracks objects created during this fixture's lifetime.
- `make_user(role)` is an inner factory function; it creates a new dictionary for each call.
- `created.append(user)` records the created object for fixture cleanup.
- `return user` gives the test its fresh object.
- `yield make_user` provides the factory to the test and divides fixture setup from teardown.
- `created.clear()` runs after the test, including when the test fails.
- The default fixture scope is `function`, so each test case gets a fresh fixture instance.
- `parametrize` runs the test once with `admin` and once with `viewer`.
- The test requests both the fixture and the current role.
- Arrange creates a fresh user; Act reads its role; Assert verifies it.

The factory separates test-data creation from the scenario. Avoid a shared mutable global user dictionary, which can make tests order-dependent.

## Question 9 — Boundary, invalid, and regression cases

```python
import pytest

@pytest.mark.parametrize(
    "value,expected",
    [
        ("a", True),
        ("abcdefgh", True),
        ("", False),
        ("abcdefghi", False),
    ],
    ids=["min", "max-regression", "empty", "max-plus-one"],
)
def test_parse_code_length_boundaries(value, expected):
    assert is_valid_code(value) is expected
```

**Line-by-line**

- The decorator tells pytest that each row supplies `value` and `expected`.
- `"a"` is the minimum valid length (1).
- `"abcdefgh"` is the maximum valid length (8).
- `""` is the empty invalid value (length 0).
- `"abcdefghi"` is just above the maximum (length 9).
- `ids` names the cases; `max-regression` explicitly identifies the historical defect.
- The test calls the validator and compares its Boolean result to the expected result.

The `"abcdefgh"` case directly reproduces the reported regression: length 8 used to be accepted but was later rejected. Keep this exact case permanently after the fix.

## Question 10 — Debug a calculation using a breakpoint and call stack

The expected result is `1062`, but the code returns `1080`.

```python
def discount(total):
    return total * 10 // 100

def taxable(total):
    return total - discount(total)

def final_total(total):
    breakpoint()
    return taxable(total) + int(total * 18 / 100)
```

**Debugging walkthrough**

1. Place `breakpoint()` inside `final_total`, where the original input and both calculations are visible.
2. Inspect `total`: it should be `1000`.
3. Step into `taxable()` to inspect the discount calculation.
4. `discount(1000)` is `100`, so taxable amount is `900`.
5. Step back to `final_total`.
6. Step over the tax expression and inspect the tax: the current code computes `18%` of `1000`, or `180`.
7. The intended calculation uses the taxable amount: `18%` of `900`, or `162`.
8. Therefore `900 + 162 = 1062`.

Corrected implementation:

```python
def final_total(total):
    taxable_amount = taxable(total)
    tax = int(taxable_amount * 18 / 100)
    return taxable_amount + tax
```

- `taxable_amount` stores the result after discount.
- `tax` is calculated from that discounted amount.
- The return combines the taxable amount and tax.

Useful `pdb` commands from the lesson: `p` inspect a value, `s` step into, `n` step over, `r` run until the current function returns, `w` show the stack, and `c` continue. The call stack shows the active call path; a traceback instead records the path associated with an exception.

## Question 11 — Log an exception and preserve it

```python
import logging

logger = logging.getLogger(__name__)

def fetch_data(client):
    try:
        return client.fetch()
    except TimeoutError:
        logger.exception("external data fetch failed")
        raise
```

**Line-by-line**

- The named logger identifies the module producing the record.
- `fetch_data(client)` receives the dependency rather than constructing it internally.
- `try` surrounds the external operation that may time out.
- `return client.fetch()` returns successful data unchanged.
- `except TimeoutError` catches the specific failure the function knows how to diagnose.
- `logger.exception(...)` records an ERROR-level log with the active exception traceback; use it inside an exception handler.
- Bare `raise` re-raises the same exception while preserving its traceback.

Logging and exception handling are separate concerns: the log records diagnostics; the exception still propagates so the appropriate higher layer can decide whether to retry or fail.

## Question 12 — Patch the lookup location

Given `service.py` contains `from utils import get_data`, `process()` resolves the name `get_data` in the `service` module namespace. Patch `service.get_data`, not `utils.get_data`.

```python
from unittest.mock import patch

def test_process_uses_controlled_data():
    with patch("service.get_data", return_value="fake-data"):
        assert process() == "FAKE-DATA"
```

**Line-by-line**

- `patch` temporarily replaces a name or attribute.
- `patch("service.get_data", ...)` targets the binding that `process()` actually reads.
- `return_value="fake-data"` configures the replacement function's result.
- The `with` block ensures the original binding is restored automatically.
- `process()` uppercases the controlled value, so the expected result is `"FAKE-DATA"`.

`patch.object()` is natural when you already have the object:

```python
client = Client()

with patch.object(client, "send", return_value="fake"):
    assert client.send({"x": 1}) == "fake"
```

It temporarily replaces the `send` attribute on this particular `client` object. Always patch the lookup point used by the system under test.

## Question 13 — Simulate a transient failure with `side_effect`

```python
from unittest.mock import Mock

def test_fetch_retries_once():
    api = Mock()
    api.fetch.side_effect = [
        TimeoutError("temporary timeout"),
        {"status": "ok", "value": 42},
    ]

    result = fetch_with_retry(api, attempts=2)

    assert result == {"status": "ok", "value": 42}
    assert api.fetch.call_count == 2
```

**Line-by-line**

- `Mock()` creates a controlled API dependency.
- `api.fetch.side_effect` supplies outcomes in sequence.
- The first item raises `TimeoutError`.
- The second item is returned by the next call.
- `fetch_with_retry(..., attempts=2)` exercises the retry logic.
- The first assertion verifies the final business result.
- `call_count == 2` verifies that exactly two attempts occurred.

This is deterministic: no real network or timing-dependent failure is required. Use `side_effect` for sequences; use `return_value` for a fixed response.

## Question 14 — Control environment and configuration safely

```python
import os
from unittest.mock import PropertyMock, patch

class Settings:
    @property
    def region(self):
        return "real-region"

settings = {"mode": "production", "enabled": False}

def test_feature_configuration(monkeypatch):
    monkeypatch.setenv("FEATURE_X", "1")

    with patch.dict(settings, {"mode": "test", "enabled": True}):
        with patch.multiple(
            os.path,
            exists=lambda path: True,
            isfile=lambda path: False,
        ):
            with patch.object(
                Settings, "region", new_callable=PropertyMock
            ) as region:
                region.return_value = "test-region"

                assert os.environ["FEATURE_X"] == "1"
                assert settings["mode"] == "test"
                assert settings["enabled"] is True
                assert Settings().region == "test-region"
```

**Line-by-line**

- `PropertyMock` is used to replace a property descriptor.
- `Settings.region` is a property on the class.
- `settings` is a mutable dictionary representing module-level configuration.
- `monkeypatch.setenv` temporarily sets the environment variable; pytest restores it after the test.
- `patch.dict` temporarily updates the dictionary and restores its prior contents on exit.
- `patch.multiple` temporarily replaces both `os.path.exists` and `os.path.isfile`.
- `patch.object` targets the property on the class, not on one instance.
- `new_callable=PropertyMock` creates a property-compatible mock.
- `region.return_value` determines the value returned when the property is read.
- The assertions verify that each controlled value is visible inside the test.

The nested context managers restore their patches automatically. In real tests, patch only the state the behavior depends on; do not use every patching API just to demonstrate it.

---

# Hard — Questions 15–21

## Question 15 — Diagnose an incorrect mock configuration

The original mock has `side_effect` on the mock object itself. That only controls calls such as `client("data")`. If production code calls `client.fetch("data")`, configure the child method instead.

```python
from unittest.mock import Mock, DEFAULT

client = Mock()

def fetch_side_effect(kind):
    if kind == "health":
        return {"ok": True}
    return DEFAULT

client.fetch.return_value = {"status": "fallback"}
client.fetch.side_effect = fetch_side_effect

assert client.fetch("data") == {"status": "fallback"}
```

**Line-by-line**

- `client = Mock()` creates the client double.
- `fetch_side_effect(kind)` models special behavior for the `health` request.
- The health branch returns its explicit response.
- `DEFAULT` tells the mock to fall back to its configured `return_value`.
- `client.fetch.return_value` defines that fallback response.
- `client.fetch.side_effect` attaches the function to the method the application actually calls.
- The final assertion verifies the fallback result.

To diagnose a mismatch, inspect:

```python
print(client.call_args)       # calls made directly on client(...)
print(client.method_calls)    # calls made on child methods
print(client.mock_calls)      # direct, child, and chained calls
```

A common cause is configuring `client.return_value` while the application invokes `client.fetch()`. Unconfigured child attributes can return nested mocks rather than realistic data.

## Question 16 — Use `create_autospec`

```python
import pytest
from unittest.mock import create_autospec

def test_mail_client_interface():
    client = create_autospec(MailClient, instance=True)

    client.send_email(
        "alice@example.test",
        "Welcome",
        "Hello",
    )

    with pytest.raises(AttributeError):
        client.send_emial("alice@example.test", "Welcome", "Hello")

    with pytest.raises(TypeError):
        client.send_email("alice@example.test", "Welcome")
```

**Line-by-line**

- `create_autospec` builds a mock constrained by the real interface.
- `instance=True` means the dependency is used as an instance of `MailClient`.
- The first call uses the correct method and all three required arguments.
- `send_emial` is misspelled; the spec causes an `AttributeError`.
- The second bad call omits the required `body` argument; signature checking causes a `TypeError`.

Differences:

- `spec` restricts which attributes can be accessed based on the specification.
- `spec_set` also prevents assigning attributes that are not on the specification.
- `autospec`/`create_autospec` additionally uses callable signatures, helping catch incorrect argument lists.

Autospec improves interface fidelity; it does not prove the external service behaves correctly.

## Question 17 — Mock an async dependency with `AsyncMock`

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_load_user_awaits_client():
    client = AsyncMock()
    client.fetch_user.return_value = {"id": 7, "name": "Alice"}

    result = await load_user(client, 7)

    assert result == "Alice"
    client.fetch_user.assert_awaited_once_with(7)
```

**Line-by-line**

- `AsyncMock` models an asynchronous dependency.
- `@pytest.mark.asyncio` tells the configured `pytest-asyncio` plugin to run this async test.
- `client.fetch_user.return_value` is the value produced when the async mock is awaited.
- `await load_user(...)` executes the async system under test.
- The result assertion verifies the application behavior.
- `assert_awaited_once_with(7)` verifies the dependency was awaited exactly once with the correct ID.

This assumes `pytest-asyncio` is installed and configured. It is a third-party pytest plugin, not part of pytest itself. A normal `Mock` call assertion alone does not prove that an async operation was awaited.

## Question 18 — Choose `mock_open` or a real temporary file

Unit-style test:

```python
from unittest.mock import mock_open, patch

def test_count_lines_reads_file():
    mocked_file = mock_open(read_data="a\nb\nc\n")

    with patch("service.open", mocked_file):
        assert count_lines("data.txt") == 3

    mocked_file.assert_called_once_with(
        "data.txt", "r", encoding="utf-8"
    )
```

**Line-by-line**

- `mock_open` creates a controlled file-like object.
- `read_data` supplies the exact content returned by reading.
- `patch("service.open", ...)` replaces the name used by `service.py`.
- `count_lines(...)` runs against the controlled stream.
- The result assertion checks the number of lines.
- `assert_called_once_with` checks the path, mode, and encoding passed to `open`.

Filesystem integration-style test:

```python
def test_count_lines_with_real_file(tmp_path):
    path = tmp_path / "data.txt"
    path.write_text("a\nb\nc\n", encoding="utf-8")

    assert count_lines(path) == 3
```

- `tmp_path` is a pytest fixture providing a fresh temporary directory.
- `/ "data.txt"` composes a path safely with `pathlib`.
- `write_text` creates a real file using UTF-8.
- `count_lines(path)` exercises actual filesystem behavior.

`mock_open` is fast and controlled; `tmp_path` validates real path and file semantics. A mocked file test does not prove real filesystem behavior.

## Question 19 — Turn a production failure into a regression test

```python
from unittest.mock import Mock

def test_missing_amount_is_handled():
    api = Mock()
    api.fetch.return_value = {
        "id": "order-17",
        "status": "ready",
    }

    result = process_order(api)

    assert result["status"] == "invalid"
    assert result["reason"] == "missing amount"
```

**Line-by-line**

- `Mock()` replaces the external API.
- `api.fetch.return_value` supplies a deterministic malformed response: the `amount` field is missing.
- `process_order(api)` exercises the application parser/handler without contacting the real API.
- The first assertion verifies the application returns the invalid status.
- The second verifies the documented reason.

**Regression workflow**

1. Extract the smallest response that reproduces the production defect.
2. Make the test fail against the old implementation.
3. Fix the parser or error-handling logic.
4. Run the focused regression test.
5. Run the broader suite.
6. Keep the regression case permanently.

The expected result follows the exercise's stated contract. If the real application contract differs, the test must follow that contract rather than force this example's output.

## Question 20 — Remove duplicate and unsafe logging

A sensible design logs the exception once at the request/operation boundary that has useful operational context, then propagates it. Lower layers should not repeatedly log the same exception unless they add distinct information for a clear reason.

```python
import logging

logger = logging.getLogger(__name__)

def repository_call(client):
    return client.fetch()

def service_call(client):
    return repository_call(client)

def handle_request(client, request_id):
    try:
        return service_call(client)
    except TimeoutError:
        logger.exception(
            "request failed; request_id=%s",
            request_id,
        )
        raise
```

**Line-by-line**

- The module uses a named logger.
- `repository_call` performs the dependency operation without duplicating the same error log.
- `service_call` delegates to the repository layer.
- `handle_request` is the boundary with a safe request identifier.
- The `try` block runs the workflow.
- `except TimeoutError` handles only the relevant failure type.
- `logger.exception` records the traceback and request ID.
- Bare `raise` preserves the original exception for higher-level handling.

Also check logger configuration: attaching handlers to both child and ancestor loggers while propagation is enabled can duplicate records. Do not log full customer payloads, credentials, tokens, or payment details. Prefer safe identifiers and carefully selected metadata.

## Question 21 — Design a data-pipeline test boundary

For a unit test of transformation logic, keep the input rows and transformation code real. Replace the database writer only if the function under test includes a staging/writer interaction.

```python
from unittest.mock import Mock

def test_transform_and_stage_normalizes_amounts_and_uses_writer():
    writer = Mock()
    rows = [
        {"id": 1, "amount": "10.50"},
        {"id": 2, "amount": "7.00"},
    ]

    result = transform_and_stage(rows, writer)

    assert result == [
        {"id": 1, "amount": 10.50},
        {"id": 2, "amount": 7.00},
    ]
    assert writer.method_calls
```

**Line-by-line**

- `Mock()` replaces the writer boundary.
- `rows` supplies controlled input records.
- `transform_and_stage(...)` executes the real transformation/staging orchestration.
- The first assertion verifies normalized numeric amounts and preserved IDs.
- `writer.method_calls` verifies that the writer boundary was used.

The source exercise does not define the writer's exact method name, so this generic call-history check is only illustrative. In a real project, prefer a precise assertion such as `writer.write.assert_called_once_with(expected_rows)` once the actual interface is known.

For a pure transformer test, call the transformer directly and omit the writer completely.

**Integration test:** use the real repository/writer with a real controlled database, create the required schema, write rows, read them back, and verify persistence. This catches SQL, schema mapping, transaction, and connectivity problems that a mock cannot prove.

---

# Advanced — Questions 22–28

## Question 22 — Layered strategy for a multi-dependency backend

| Layer | What to exercise | Suitable boundary |
|---|---|---|
| Unit | Business rules, retry decisions, request mapping | Real business logic; mocks/stubs/fakes for dependencies |
| Contract | Request/response shapes and required fields | Contract fixtures or a controlled provider contract |
| Integration | SQL, Redis semantics, queue acknowledgment/retry, API adapter behavior | Real controlled PostgreSQL/Redis/broker/API sandbox where behavior matters |
| E2E | A small number of critical user workflows | Running application and its required test dependencies |

**Practical decisions**

- PostgreSQL: mock repository calls in unit tests; use a real test database for SQL, schema, transaction, and persistence integration.
- Redis: use a fake for simple cache decisions; use real controlled Redis when TTL, serialization, locking, or server semantics matter.
- REST API: use stubs/mocks for deterministic unit behavior; contract tests or a sandbox for actual schema/auth/status compatibility.
- Message queue: mock producer calls for orchestration; use a real test broker for delivery, acknowledgment, ordering, and retry semantics.
- Logging: assert important records where logging behavior is the subject of the test; do not make every business test depend on exact log formatting.

Keep E2E scenarios few and focused on critical workflows. This balances fast feedback from unit tests with real-boundary confidence from contract/integration tests.

## Question 23 — Resilient API client test matrix

| Scenario | Deterministic unit test | Higher-level validation | Key assertion |
|---|---|---|---|
| Timeout | Yes, mocked transport | Optional controlled endpoint/sandbox | Retry decision and terminal error |
| Retry then success | Yes, `side_effect` | Useful for adapter validation | Attempts and final parsed response |
| 401/403 | Yes | Contract/sandbox where practical | No inappropriate retry; correct error mapping |
| Malformed success body | Yes | Contract test if schema drift is a risk | Validation error or documented fallback |
| Normal success | Yes | Integration/contract | Correct parsed result |

```python
from unittest.mock import Mock

def test_client_retries_timeout_then_succeeds():
    transport = Mock()
    transport.request.side_effect = [
        TimeoutError("temporary"),
        {"status": 200, "data": {"id": 10}},
    ]

    result = fetch_resource(transport, retries=1)

    assert result["id"] == 10
    assert transport.request.call_count == 2
```

**Line-by-line**

- `Mock()` replaces the transport boundary.
- `side_effect` supplies a timeout on the first request and a successful response on the second.
- `fetch_resource(..., retries=1)` allows one retry after the initial attempt.
- `result["id"] == 10` verifies the final business result.
- `call_count == 2` verifies the initial attempt plus one retry.

Do not stop at the attempt count: verify the final result or error. A mocked response is not authoritative documentation for the real external API; add contract/integration validation.

## Question 24 — Reduce a large pipeline failure to an MRE

The failure is `ValueError: invalid literal for int() ... '9O1'` in a two-million-record job.

**Reduction sequence**

1. Use the traceback/log context to identify the transformation stage and field.
2. Locate the record containing the exact value `'9O1'`.
3. Save only that record and any minimum required companion data.
4. Call the transformer directly, bypassing unrelated ingestion and database writes.
5. Confirm the reduced input still triggers the same exception.
6. Inspect the parsing/validation path.
7. Fix the code according to the intended data contract.
8. Turn the exact failing input into a regression test.

```python
import pytest

def test_transform_handles_invalid_numeric_amount():
    row = {"amount": "9O1"}

    with pytest.raises(ValueError):
        transform_row(row)
```

**Line-by-line**

- `pytest` provides exception assertions.
- `row` preserves the exact malformed field value.
- `pytest.raises(ValueError)` states the expected behavior for this example.
- `transform_row(row)` executes the smallest relevant path.

The exercise describes the failure but does not define whether the desired product behavior is to raise or return a structured invalid-row result. This example preserves the original exception behavior; if the pipeline contract requires graceful rejection, assert that contract instead.

An MRE must be as small as possible **while still reproducing the same failure**. If reducing the data makes the bug disappear, the reproduction is no longer valid.

## Question 25 — Test LLM application logic without claiming model quality

```python
from unittest.mock import Mock

def test_llm_response_is_validated_and_used():
    llm = Mock()
    llm.generate.return_value = {
        "label": "refund_request",
        "confidence": 0.91,
    }

    result = classify_message(llm, "I need a refund")

    assert result["label"] == "refund_request"
    assert 0.0 <= result["confidence"] <= 1.0

def test_malformed_llm_response_uses_fallback():
    llm = Mock()
    llm.generate.return_value = {
        "confidence": "not-a-number",
    }

    result = classify_message(llm, "hello")

    assert result["label"] == "fallback"
```

**Line-by-line**

- `Mock()` replaces the probabilistic LLM provider.
- `generate.return_value` supplies a fixed structured response.
- `classify_message(...)` runs the deterministic application pipeline.
- The first assertions verify the label and confidence range.
- The second test supplies a malformed response with no valid label and a nonnumeric confidence.
- The fallback assertion checks the application's recovery contract.

These tests establish that parsing, validation, and fallback logic work for controlled inputs. They do **not** establish real model accuracy, semantic quality, safety, refusal behavior, latency, or reliability. Those require evaluation with real model calls and representative evaluation data.

## Question 26 — Test an agentic orchestration boundary

Happy-path unit test:

```python
from unittest.mock import Mock

def test_agent_routes_to_weather_tool():
    llm = Mock()
    tools = Mock()

    llm.generate.return_value = {
        "tool": "weather",
        "arguments": {"city": "Kolkata"},
    }
    tools.weather.return_value = {
        "temperature": 30,
        "condition": "clear",
    }

    result = run_agent(
        llm,
        tools,
        "What is the weather in Kolkata?",
    )

    assert result["temperature"] == 30
    tools.weather.assert_called_once_with(city="Kolkata")
```

**Line-by-line**

- `llm` replaces the model decision boundary.
- `tools` replaces external tool execution.
- `llm.generate.return_value` supplies a deterministic tool choice and arguments.
- `tools.weather.return_value` supplies a controlled tool result.
- `run_agent(...)` executes the orchestration path.
- The result assertion verifies the observable output.
- The call assertion verifies correct routing and arguments.

Failure/fallback test:

```python
def test_agent_uses_fallback_after_tool_failure():
    llm = Mock()
    tools = Mock()

    llm.generate.return_value = {
        "tool": "search",
        "arguments": {"query": "example"},
    }
    tools.search.side_effect = TimeoutError("temporary")

    result = run_agent(llm, tools, "Find example")

    assert result["status"] == "fallback"
```

- The model mock chooses the search tool.
- `side_effect` makes the tool fail deterministically.
- `run_agent` exercises the failure/recovery path.
- The assertion verifies the documented fallback status.

The exercise does not define the internal state-machine implementation, so tests should be built around the actual public orchestration contract. Unit tests can verify tool selection, arguments, state transitions, retry/fallback, and termination. Real integration/E2E/evaluation is still needed for real model behavior, retrieval quality, external API/browser behavior, latency, and critical workflows. Do not test hidden chain-of-thought; test observable actions and outcomes.

## Question 27 — Reduce mock complexity with a Protocol and dependency injection

```python
from typing import Protocol

class UserRepository(Protocol):
    def get_user(self, user_id: int) -> dict[str, object]:
        ...

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def display_name(self, user_id: int) -> str:
        user = self.repository.get_user(user_id)
        return str(user["name"])
```

**Line-by-line**

- `Protocol` defines a structural interface: an object satisfies it by providing the required method with a compatible shape.
- `UserRepository` describes only the capability the service needs.
- `get_user` accepts an integer ID and returns a dictionary-like record.
- `...` marks the protocol method declaration; it is not a concrete repository implementation.
- `UserService.__init__` receives the repository from outside.
- `self.repository = repository` stores the injected dependency.
- `display_name` asks the repository for one user.
- `str(user["name"])` returns the name as a string.

Test with an autospecced mock:

```python
from unittest.mock import create_autospec

def test_display_name():
    repository = create_autospec(
        UserRepository,
        instance=True,
    )
    repository.get_user.return_value = {
        "id": 1,
        "name": "Alice",
    }

    service = UserService(repository)

    assert service.display_name(1) == "Alice"
```

- `create_autospec` creates a mock constrained by the protocol interface.
- `instance=True` models an instance dependency.
- `return_value` supplies a deterministic user record.
- `UserService(repository)` injects the mock rather than constructing infrastructure internally.
- The assertion verifies the service's public behavior.

This removes nested patch chains because construction is outside the service. The production service depends on a small explicit contract, not on the concrete database/client implementation. Keep a separate integration test for the real repository and database.

## Question 28 — Diagnose a production failure end-to-end

**Immediate interpretation**

- The test failure is associated with `PaymentService.charge`.
- `PaymentGatewayError` is raised in `gateway.py` and chained from an underlying exception using `raise ... from exc`.
- The debug log provides a request ID and amount, but does not by itself prove the gateway is the root cause.
- The likely test defect is the patch target: the test patches `gateway.Gateway`, while `service.py` imported `Gateway` into its own namespace. The service therefore uses `service.Gateway`.

Corrected unit test:

```python
from unittest.mock import patch

def test_charge():
    with patch("payments.service.Gateway") as gateway_cls:
        gateway = gateway_cls.return_value
        gateway.charge.return_value = {"status": "approved"}

        result = PaymentService().charge(500)

        assert result["status"] == "approved"
        gateway.charge.assert_called_once_with(500)
```

**Line-by-line**

- `patch` temporarily replaces the dependency.
- `"payments.service.Gateway"` is the lookup location used by `PaymentService` after the `from ... import ...` binding.
- `gateway_cls` is the patched class/constructor.
- `.return_value` is the instance returned when `PaymentService` constructs `Gateway`.
- `gateway.charge.return_value` controls the method's result.
- `PaymentService().charge(500)` executes the unit under test.
- The first assertion checks the public result.
- The second checks that the gateway received the expected amount once.

**Investigation and validation sequence**

1. Run only the failing test to reduce noise.
2. Read the traceback from the test frame down to `service.py` and `gateway.py`.
3. Inspect exception chaining: `PaymentGatewayError` preserves the original cause, which can reveal the lower-level failure.
4. Inspect the import statement in `service.py`.
5. Patch the name in the namespace where the service looks it up.
6. Verify the mock is actually used by asserting its meaningful call.
7. Keep a deterministic regression test for the import-binding/mock-target failure.
8. Run the focused test, then the Module 07 suite.
9. Add contract/integration coverage against a controlled real gateway sandbox or test boundary. A mocked gateway does not prove real payment-provider compatibility.
10. Keep logs safe: request ID can be useful; log amounts only if policy permits. Never log credentials, tokens, card details, or full payment/customer payloads.

**Module 06 package/environment checks**

- Confirm the test runner imports the intended installed package from the configured `src/` layout rather than an unintended local copy.
- Confirm the test environment is synchronized with the project's declared dependencies and lock file.
- Run the project's established lint/type/test checks after the package refactor.

The likely immediate problem is the wrong mock lookup target, not proof that the production gateway is broken. The correct engineering loop is evidence → focused reproduction → inspect imports and exception cause → fix → regression test → real-boundary validation.

---

## Final coverage and completion checklist

| Skill area | Questions |
|---|---:|
| Unit, integration, E2E and layered strategy | 1, 21–23, 25, 26, 28 |
| Assertions, invalid inputs, regression | 2, 5, 9, 19, 24, 25 |
| Fixtures, fixture teardown, parametrization | 3, 4, 8, 9 |
| AAA and boundary-focused test design | 2–5, 8–9, 13 |
| Debugger, breakpoints, call stack | 10 |
| Tracebacks, exception propagation/chaining, logging | 6, 11, 20, 24, 28 |
| MRE and production debugging workflow | 19, 24, 28 |
| Test doubles and mock interactions | 7, 13–18, 21–27 |
| Patching and import lookup location | 12, 14–16, 28 |
| Data-pipeline test architecture | 21, 22, 24 |
| LLM and agentic AI testing boundaries | 25–26 |
| Protocol and dependency injection | 27–28 |

- [x] All 28 questions answered.
- [x] Code examples include explanations of the important lines.
- [x] Solutions stay within the taught Module 06–07 concepts.
- [x] External dependencies are replaced only where the test boundary calls for it.
- [x] Real integration is retained where mocks cannot prove database, filesystem, queue, or provider behavior.
- [x] LLM/agent tests distinguish deterministic application logic from real model/tool quality.
- [x] No next module or lesson is started by this practice guide.

**Learning status:** This completes the 28-question cumulative practice set for Module 07. It does not start a new module.
