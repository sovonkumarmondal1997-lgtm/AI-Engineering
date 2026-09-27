# Testing and Systematic Debugging — Practice Questions

## Instructions

This practice set contains exactly **28 questions** covering the concepts taught across Module 07 — Testing and Systematic Debugging. The difficulty progresses from foundational application to production-oriented engineering judgment.

Each question shows the **Problem first** and the **Solution afterward**. Try to solve the problem before reading the solution. Most questions are practical Python/pytest/debugging exercises; advanced questions require you to choose appropriate test levels, isolation boundaries, diagnostics, and test doubles rather than simply memorizing APIs.

Some questions naturally integrate Module 06 knowledge where it supports testing work, especially Python imports, package structure, dependency boundaries, type-oriented interfaces, and test-environment dependencies.

---

## Basic — Questions 1–7

## Question 1 — Classify the Test Level

### Difficulty
Basic

### Problem

A function `calculate_tax()` performs pure arithmetic. A second test calls a repository backed by a real SQLite database. A third test starts the application and verifies a complete user-registration workflow through its public interface.

Classify each test as **unit**, **integration**, or **end-to-end (E2E)** testing and explain the boundary being exercised.

### Requirements

- Classify all three tests.
- Explain what each test isolates or connects.
- State which test is normally fastest and which is broadest.

### Expected Outcome

You should be able to identify the test layer from the components involved, not from the test function name.

### Solution

```text
1. calculate_tax() with no external dependency
   → Unit test

2. Repository + real SQLite database
   → Integration test

3. Application startup + complete registration workflow
   → End-to-end test
```

The unit test focuses on one local behavior. The integration test validates a boundary between application code and the database. The E2E test validates the complete workflow through the system.

### How to Solve It

1. Ask what the test is trying to prove.
2. Identify whether it uses one unit, multiple components, or the whole workflow.
3. Mark the boundary:
   - local function/class → unit
   - component + real dependency → integration
   - complete user/system workflow → E2E.
4. Compare the amount of infrastructure involved.

### Why This Works

The testing pyramid is useful because tests at different layers provide different trade-offs. Unit tests tend to be fast and isolated; integration tests validate real component boundaries; E2E tests give broad workflow confidence but are typically slower and more expensive to maintain.

### Common Mistake

Calling every automated test a “unit test” simply because pytest runs it. The framework does not determine the test level; the test boundary does.

### Key Learning

Choose the test layer based on the behavior and boundary you need to verify.

## Question 2 — Write a Precise Pytest Assertion

### Difficulty
Basic

### Problem

You are given:

```python
def double(value: int) -> int:
    return value * 2
```

Write a pytest test for `double(7)`. Then explain what pytest assertion introspection adds when the expected value is wrong.

### Requirements

- Use pytest style assertions.
- Keep the test readable using Arrange → Act → Assert.
- Explain the diagnostic value of assertion introspection.

### Expected Outcome

The test should fail clearly if the function returns anything other than `14`.

### Solution

```python
def test_double_returns_twice_the_input():
    # Arrange
    value = 7

    # Act
    result = double(value)

    # Assert
    assert result == 14
```

If the implementation returned `15`, pytest can show the compared values and the failed expression, making the failure easier to diagnose than a generic boolean failure.

### How to Solve It

1. Put the input in Arrange.
2. Call the function once in Act.
3. Assert the behavior you care about.
4. Do not add an assertion that tests an implementation detail such as a local variable.

### Why This Works

The `assert` statement expresses the expected behavior, while pytest enhances the failure report through assertion introspection. This keeps the test concise and the failure diagnostic.

### Common Mistake

Using a vague assertion such as `assert result` would accept many incorrect numeric values. The assertion should express the actual contract.

### Key Learning

Assertions should verify the behavior that matters, and strong assertions make failures easier to understand.

## Question 3 — Fixture + Arrange–Act–Assert

### Difficulty
Basic

### Problem

Three tests need the same `UserService()` object. Write a pytest fixture and one test that retrieves a user by ID. Keep the test body easy to read.

### Requirements

- Create a `user_service` fixture.
- Use the fixture through pytest dependency injection.
- Preserve a clear Arrange, Act, Assert structure.

### Expected Outcome

The service construction belongs in reusable test infrastructure while the test body should still reveal the behavior being verified.

### Solution

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

This assumes `UserService` is available in the test environment.

### How to Solve It

1. Identify the reusable dependency: `UserService()`.
2. Move only that shared setup into the fixture.
3. Request the fixture by parameter name.
4. Keep scenario-specific input and assertions local to the test.

### Why This Works

Fixtures are pytest-managed test dependencies and setup/teardown mechanisms. They can reduce repeated infrastructure without hiding the test's actual story.

### Common Mistake

Creating a giant fixture that also creates users, configures a database, prepares unrelated data, and asserts behavior. That hides the Arrange phase and makes tests harder to understand.

### Key Learning

Use fixtures for meaningful reusable setup; keep the test's behavior visible.

## Question 4 — Parametrize Boundary Cases

### Difficulty
Basic

### Problem

A validator accepts quantities from `1` through `100`, inclusive. Write one parametrized pytest test that checks the key boundary values `1`, `2`, `99`, and `100` are accepted.

### Requirements

- Use `pytest.mark.parametrize`.
- Include the four boundary values.
- Give the cases readable IDs.

### Expected Outcome

The same test logic should execute for each valid boundary-adjacent case.

### Solution

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

### How to Solve It

1. Identify the allowed interval `[1, 100]`.
2. Select boundary-focused examples instead of random values.
3. Reuse the same assertion because the expected behavior is the same for all four cases.
4. Add IDs so CI failures identify the failing case quickly.

### Why This Works

Parametrization lets you vary data without duplicating test structure. Readable IDs turn generated cases into useful diagnostics.

### Common Mistake

Using only `50` because it is a “normal” value. That checks the middle of the valid range but tells you little about boundary behavior.

### Key Learning

Boundary-value testing and parametrization work well together when multiple cases share one behavior and assertion pattern.

## Question 5 — Assert an Invalid Input

### Difficulty
Basic

### Problem

The function below rejects non-positive ages:

```python
def validate_age(age: int) -> None:
    if age <= 0:
        raise ValueError("age must be positive")
```

Write a pytest test for `age=0` that checks both the exception type and the meaningful part of the message.

### Requirements

- Use `pytest.raises`.
- Assert `ValueError`.
- Check the message without making the test unnecessarily fragile.

### Expected Outcome

The test should prove that invalid input is rejected with the intended exception contract.

### Solution

```python
import pytest


def test_validate_age_rejects_zero():
    with pytest.raises(ValueError, match="age must be positive"):
        validate_age(0)
```

For more detailed inspection, the exception can be captured:

```python
with pytest.raises(ValueError) as exc_info:
    validate_age(0)

assert "age must be positive" in str(exc_info.value)
```

### How to Solve It

1. Put only the operation expected to fail inside `pytest.raises`.
2. Specify the exception class.
3. Verify only the message content that is part of the useful contract.

### Why This Works

Invalid-input tests protect the negative path. Narrow exception assertions also avoid hiding unrelated failures behind an overly broad expectation.

### Common Mistake

Wrapping a large block inside `pytest.raises(ValueError)` can accidentally pass if any unrelated operation raises `ValueError`. The expected failing operation should be obvious.

### Key Learning

Test invalid behavior explicitly; do not treat rejected input as an unimportant edge case.

## Question 6 — Read the Traceback and Add Useful Logging

### Difficulty
Basic

### Problem

A test fails with:

```text
Traceback (most recent call last):
  File "service.py", line 18, in process_order
    amount = int(order["amount"])
ValueError: invalid literal for int() with base 10: '10O'
```

Identify the immediate failure location and write one useful log statement that records safe diagnostic context without logging sensitive data.

### Requirements

- Identify the exception type.
- Identify the line and failing operation.
- Give one `logger` call using a named logger.
- Do not log credentials, tokens, or raw sensitive customer data.

### Expected Outcome

The likely problem is malformed input: the string contains the letter `O`, not the digit `0`.

### Solution

Immediate failure:

```text
service.py:18
int(order["amount"])
ValueError
```

Useful logging:

```python
import logging

logger = logging.getLogger(__name__)

logger.warning(
    "invalid order amount format; order_id=%s",
    order["id"],
)
```

Only use an identifier that is safe to log under the application's data policy.

### How to Solve It

1. Read the exception type and message.
2. Find the deepest frame shown for the failing operation.
3. Inspect the input that reached that operation.
4. Add context that helps diagnosis without copying the entire payload into logs.

### Why This Works

A traceback points to where an exception surfaced, while logging can add runtime context such as a safe identifier or processing stage. Neither alone necessarily proves the complete root cause.

### Common Mistake

Logging the entire `order` dictionary “for debugging.” That can leak personal or financial information and creates long-lived security and privacy risk.

### Key Learning

Use tracebacks for failure location and logs for carefully selected operational context.

## Question 7 — Use a Simple Mock and Verify an Interaction

### Difficulty
Basic

### Problem

A registration service sends a welcome email after creating a user. For the unit test, you do not want to contact the real email provider. Configure a mock email service and verify the important interaction.

### Requirements

- Use `Mock`.
- Configure a simple behavior if needed.
- Verify the relevant arguments.
- Demonstrate one useful call-history assertion.

### Expected Outcome

The test should validate application behavior while keeping the real email provider out of the unit test.

### Solution

```python
from unittest.mock import Mock, ANY, sentinel


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

A sentinel can also be useful when a test needs a unique marker value:

```python
marker = sentinel.registration_marker
mock = Mock(return_value=marker)
assert mock() is marker
```

After a reusable mock has been used in multiple phases, `reset_mock()` can clear recorded interaction state.

### How to Solve It

1. Replace the external dependency with a mock.
2. Exercise the system under test.
3. Assert the behavior that crosses the dependency boundary.
4. Use `ANY` for a nondeterministic argument only where exact equality is not part of the contract.

### Why This Works

Mocks are especially useful for interaction verification at external boundaries. `ANY` avoids coupling the test to an irrelevant nondeterministic value; `sentinel` provides a unique object when identity matters.

### Common Mistake

Asserting only `email_service.assert_called_once()` even though the recipient is the important contract. That checks occurrence but not correctness of the interaction.

### Key Learning

A mock test should verify the meaningful interaction, not merely prove that “some call happened.”

---

## Moderate — Questions 8–14

## Question 8 — Fixture Factory + Parametrized Cases

### Difficulty
Moderate

### Problem

A test suite creates users with different roles. Each test case needs a fresh user object, and the role varies across cases. Design a fixture factory plus parametrization so the same behavior test can run for `admin` and `viewer`.

### Requirements

- Use a fixture that returns a factory function.
- Parametrize the role values.
- Keep each test isolated from the other case.

### Expected Outcome

Each parametrized test case should get its own fresh test object through the fixture factory.

### Solution

```python
import pytest


@pytest.fixture
def user_factory():
    def make_user(role: str) -> dict[str, str]:
        return {"name": "Alice", "role": role}

    return make_user


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

### How to Solve It

1. Separate test infrastructure from test data.
2. Use a fixture factory when the test needs multiple fresh objects rather than one fixed fixture value.
3. Let parametrization supply the scenario variation.

### Why This Works

Fixtures manage reusable setup/lifecycle, while parametrization controls which cases are executed. A factory fixture makes per-case data creation explicit and avoids sharing mutable user dictionaries across cases.

### Common Mistake

Using one mutable global user dictionary and changing its role for each case. That creates hidden shared state and can cause order-dependent failures.

### Key Learning

Use fixtures for dependency/setup management and parametrization for meaningful variation.

## Question 9 — Boundary + Invalid + Regression Test

### Difficulty
Moderate

### Problem

A parser should accept a string length from `1` to `8`. A bug report says the application previously accepted length `8` but a recent change rejects it. Design a small regression set that covers valid boundaries and one invalid case.

### Requirements

- Include the minimum, maximum, just-outside values, and an empty string.
- Identify which case directly reproduces the reported regression.
- Write the pytest test using parametrization.

### Expected Outcome

The suite should protect both the general boundary and the exact historical bug.

### Solution

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

The `max-regression` case is the regression test for the reported bug.

### How to Solve It

1. Start from the requirement: valid lengths are `1..8`.
2. Add `min`, `max`, `min-1`, and `max+1` where those are meaningful.
3. Include the exact historical failure case.
4. Use one test when the expected behavior is the same across cases.

### Why This Works

Boundary testing finds defects near limits, while regression testing preserves a known bug fix. A regression case is not merely “another example”; it protects behavior that already failed historically.

### Common Mistake

Testing only the current happy path and assuming the bug cannot return. Without the historical case, a future change can reintroduce the same defect.

### Key Learning

A strong regression suite records the exact previously broken behavior and places it next to the broader boundary model.

## Question 10 — Debug a Failing Calculation with the Call Stack

### Difficulty
Moderate

### Problem

Consider:

```python
def discount(total):
    return total * 10 // 100


def taxable(total):
    return total - discount(total)


def final_total(total):
    return taxable(total) + int(total * 18 / 100)
```

A test expects `1062` for `1000` but gets `1079`. Describe how you would debug this systematically with a breakpoint and the call stack.

### Requirements

- State where you would place the first breakpoint.
- State what variables you would inspect.
- Use step into/step over appropriately.
- Explain what the call stack tells you.

### Expected Outcome

The debugging process should move from the observed wrong result toward the first incorrect intermediate value.

### Solution

A reasonable session is:

```text
breakpoint in final_total()
↓
inspect total = 1000
↓
step into taxable()
↓
inspect discount = 100
↓
step out to final_total()
↓
inspect taxable = 900
↓
step over tax calculation
↓
inspect final components
```

The call stack at a paused point conceptually shows:

```text
final_total
  ↓
taxable
    ↓
discount
```

You are looking for the first intermediate value that no longer matches the expected model.

### How to Solve It

1. Break at the highest useful point that still exposes the relevant inputs.
2. Inspect arguments before stepping into helpers.
3. Step into a helper when its internal result is suspicious.
4. Step out after verifying the helper.
5. Compare expected and actual intermediate values.

### Why This Works

The debugger exposes the live call stack and current local state. This is different from a traceback: the traceback describes a past exception path; the live stack shows where execution is paused now.

### Common Mistake

Stopping at the final return line and staring only at `1079`. That delays the discovery of which intermediate calculation first became incorrect.

### Key Learning

Debugging becomes systematic when you inspect the value transitions through the call chain rather than guessing from the final symptom.

## Question 11 — Log an Exception Without Losing Its Traceback

### Difficulty
Moderate

### Problem

Write a handler for an external-service operation that:

1. logs the failure with a traceback, and
2. re-raises the same exception so the caller can still decide how to recover.

### Requirements

- Use a named logger.
- Use `logger.exception()` correctly.
- Preserve the original exception.
- Do not use `print()` as the operational logging mechanism.

### Expected Outcome

The handler should add diagnostic information and let the original exception propagate.

### Solution

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

`logger.exception()` is intended to be used inside an exception handler and includes exception information in the log record.

### How to Solve It

1. Keep the `try` focused on the operation you expect to fail.
2. Catch the specific exception you can meaningfully diagnose or handle.
3. Log useful context at the appropriate level.
4. Use bare `raise` when you want to preserve the current exception and traceback.

### Why This Works

Logging and exception control flow solve different problems. The log records diagnostic context; `raise` preserves the exception path so higher layers can continue handling it.

### Common Mistake

Replacing `raise` with `raise TimeoutError("fetch failed")` without chaining or cause preservation. That can throw away useful context about the original failure.

### Key Learning

Log intentionally, preserve exception context, and let the correct layer decide recovery.

## Question 12 — Patch Where the Object Is Used

### Difficulty
Moderate

### Problem

You have:

`utils.py`

```python
def get_data():
    return "real-data"
```

`service.py`

```python
from utils import get_data


def process():
    return get_data().upper()
```

A test uses `patch("utils.get_data")`, but `process()` still returns `REAL-DATA`. Fix the test and explain why. Also show a case where `patch.object()` would be natural.

### Requirements

- Identify the lookup location.
- Patch the correct name used by `service.py`.
- Provide the corrected test.
- Show one concise `patch.object()` example.

### Expected Outcome

The patch must replace the name that `service.py` resolves when `process()` executes.

### Solution

Correct patch:

```python
from unittest.mock import patch


def test_process_uses_controlled_data():
    with patch("service.get_data", return_value="fake-data"):
        assert process() == "FAKE-DATA"
```

Why? `service.py` imported `get_data` into its own module namespace, so `process()` looks up `service.get_data`, not `utils.get_data`.

`patch.object()` is convenient when the target object is already available:

```python
from unittest.mock import patch


class Client:
    def send(self, payload):
        return "real"


def test_client_method():
    client = Client()
    with patch.object(client, "send", return_value="fake"):
        assert client.send({"x": 1}) == "fake"
```

### How to Solve It

1. Trace the import statement.
2. Ask: “What exact name does the code under test read?”
3. Patch that name in the consumer module.
4. Prefer a context manager/decorator so cleanup is automatic.
5. Use `patch.object()` when you have the concrete target object and attribute.

### Why This Works

Patching changes a binding for the duration of the patch. Python import statements such as `from utils import get_data` bind a name in `service.py`; replacing `utils.get_data` later does not retroactively change that existing binding.

### Common Mistake

Choosing the module where the function was originally defined instead of the namespace where the system under test looks it up.

### Key Learning

Patch the dependency at the lookup point used by the code under test.

## Question 13 — Simulate a Transient Failure with side_effect

### Difficulty
Moderate

### Problem

An API client should retry once when the first request times out, then return the successful response. Write a test using `side_effect` with sequential outcomes and assert both the final result and the number of attempts.

### Requirements

- Simulate `TimeoutError` on the first call.
- Return a success response on the second call.
- Assert the final result.
- Assert the number of attempts without over-specifying unrelated internal calls.

### Expected Outcome

The test should deterministically exercise the retry path without a real network dependency.

### Solution

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

The iterable `side_effect` supplies the first exception, then the second response.

### How to Solve It

1. Identify the sequence needed to reach the retry branch.
2. Configure the dependency, not the system under test, with that sequence.
3. Exercise the retry logic once.
4. Assert the externally meaningful result and attempt count.

### Why This Works

`side_effect` is useful for controlled failure simulation and sequential behavior. It makes transient failures reproducible and allows the unit test to focus on retry logic.

### Common Mistake

Using `return_value` for the first call and then manually changing the mock halfway through the test. That mixes setup with execution and makes the test harder to reason about.

### Key Learning

Use `side_effect` when the dependency must produce a deliberate sequence of outcomes.

## Question 14 — Control Configuration Without Real Environment State

### Difficulty
Moderate

### Problem

A module reads a feature flag from `os.environ`, calls two configuration functions, and exposes a computed property. Design a pytest test that safely overrides these values and restores the original state automatically. Use a mix of `monkeypatch`, `patch.dict`, `patch.multiple`, and `PropertyMock` where appropriate.

### Requirements

- Override one environment variable.
- Temporarily update a dictionary-based settings object.
- Patch two attributes together.
- Override a property for the test.
- Ensure all changes are automatically restored.

### Expected Outcome

The test should control configuration locally without permanently changing the process environment or module globals.

### Solution

```python
import os
from unittest.mock import PropertyMock, patch


class Settings:
    @property
    def region(self):
        return "real-region"


settings = {"mode": "production", "enabled": False}


def test_feature_configuration(monkeypatch):
    # Environment-variable control
    monkeypatch.setenv("FEATURE_X", "1")

    # Dictionary control
    with patch.dict(settings, {"mode": "test", "enabled": True}):
        # Multiple attribute patching
        with patch.multiple(
            os.path,
            exists=lambda path: True,
            isfile=lambda path: False,
        ):
            # Property patching
            with patch.object(Settings, "region", new_callable=PropertyMock) as region:
                region.return_value = "test-region"
                assert os.environ["FEATURE_X"] == "1"
                assert settings["mode"] == "test"
                assert settings["enabled"] is True
                assert Settings().region == "test-region"
```

After the test, `monkeypatch` and the patch context managers restore the prior state.

### How to Solve It

1. Identify which state lives in the environment and which lives in Python objects.
2. Use `monkeypatch` for pytest-managed mutation such as environment variables.
3. Use `patch.dict` for temporary dictionary changes.
4. Use `patch.multiple` when grouping closely related attribute replacements improves readability.
5. Use `PropertyMock` specifically for a property descriptor.

### Why This Works

These tools create temporary changes with automatic cleanup. The main engineering goal is not to use every patching API; it is to isolate mutable external state while keeping teardown reliable.

### Common Mistake

Manually assigning `os.environ["FEATURE_X"] = "1"` and forgetting to restore it. A later test may inherit the modified state and become order-dependent.

### Key Learning

Control nondeterministic configuration with scoped, automatically cleaned-up test patches.

---

## Hard — Questions 15–21

## Question 15 — Diagnose an Incorrect Mock Configuration

### Difficulty
Hard

### Problem

A unit test for an API adapter is failing unexpectedly:

```python
from unittest.mock import Mock, DEFAULT

client = Mock(return_value={"status": "fallback"})


def route(kind):
    if kind == "health":
        return {"ok": True}
    return DEFAULT

client.side_effect = route

result = build_response(client, "data")
```

The developer expected `{"status": "fallback"}` for `"data"`, but the test receives a mock object or the wrong structure. Diagnose the issue and provide a correct approach.

### Requirements

- Explain how a callable `side_effect` interacts with `return_value` and `DEFAULT`.
- Provide corrected code for the intended `data` case.
- Explain how you would inspect `call_args`, `method_calls`, or `mock_calls` if the wrong method is being invoked.

### Expected Outcome

The problem is that the callable side effect is attached to the mock itself, but `build_response()` may be calling `client.fetch(...)` rather than `client(...)`. Also, `DEFAULT` only falls back to the mock's configured return value when the side effect is executed for that mock call.

### Solution

If `build_response()` expects `client.fetch()`, configure the child mock explicitly:

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

If the production code actually calls the mock itself, then the original shape can work:

```python
client = Mock(return_value={"status": "fallback"})


def route(kind):
    if kind == "health":
        return {"ok": True}
    return DEFAULT

client.side_effect = route
```

During debugging, inspect what was really called:

```python
print(client.call_args)
print(client.method_calls)
print(client.mock_calls)
```

Use these observations to align the mock with the actual interface.

### How to Solve It

1. First inspect the production call shape: `client(...)` or `client.fetch(...)`?
2. Configure the mock at that exact boundary.
3. If using a callable `side_effect`, remember that returning `DEFAULT` tells the mock to use its configured default return behavior.
4. Inspect call history when the mock appears to be ignored or returns an unexpected nested mock.

### Why This Works

Unrestricted mocks dynamically create child mocks. If the return value for a nested method is not configured, you may receive another `Mock` instead of the expected data structure. Call history helps reveal which boundary the code actually used.

### Common Mistake

Configuring `client.return_value` when the application calls `client.fetch()`, or assuming a nested method automatically returns a realistic dictionary.

### Key Learning

When a mock behaves strangely, inspect the actual call shape before changing assertions. The mock configuration must match the production interface.

## Question 16 — Use autospec, spec, spec_set, and create_autospec

### Difficulty
Hard

### Problem

You have a typed client:

```python
class MailClient:
    def send_email(self, to: str, subject: str, body: str) -> None:
        ...
```

A test currently uses `Mock()` and accidentally calls `send_emial(...)` and later `send_email(to, subject)`. The mock lets both mistakes through. Rewrite the test setup using `create_autospec()` and explain how `spec` and `spec_set` differ.

### Requirements

- Use `create_autospec`.
- Demonstrate one misspelled attribute being rejected.
- Demonstrate one incorrect call signature being caught.
- Distinguish `spec` from `spec_set`.

### Expected Outcome

The mock should behave like the real interface closely enough to catch obvious interface drift or test typos.

### Solution

```python
from unittest.mock import create_autospec


def test_mail_client_interface():
    client = create_autospec(MailClient, instance=True)

    # Correct call
    client.send_email(
        "alice@example.test",
        "Welcome",
        "Hello",
    )

    # These should fail because they do not match the interface:
    # client.send_emial(...)
    # client.send_email("alice@example.test", "Welcome")
```

Conceptually:

```text
spec
→ limits the mock to attributes found on the specification

spec_set
→ additionally prevents assigning attributes that are not on the specification

autospec / create_autospec
→ uses the real object's callable signatures to make the mock closer to the interface
```

A simple `Mock(spec=MailClient)` helps catch unknown attributes but is not the same as full signature-aware autospeccing.

### How to Solve It

1. Start from the real interface.
2. Build the mock from that interface rather than from an unconstrained `Mock()`.
3. Use `instance=True` when the production dependency is used as an instance.
4. Treat `spec` and `spec_set` as attribute/interface restrictions; use autospec when signature fidelity matters.

### Why This Works

Mocks can otherwise become so permissive that tests pass despite typos or interface drift. Autospeccing increases alignment with the real dependency and therefore reduces one class of false confidence.

### Common Mistake

Assuming `spec=True` automatically validates every argument signature. Attribute restrictions and signature checking are related but distinct concerns.

### Key Learning

Make a test double match the dependency interface closely when that boundary is important enough to justify the stronger coupling.

## Question 17 — Mock Async Code Correctly

### Difficulty
Hard

### Problem

An async service calls:

```python
class APIClient:
    async def fetch_user(self, user_id: int) -> dict:
        ...
```

Write a pytest test for a function `load_user(client, user_id)` that awaits the client and returns the user's name. The test must use `AsyncMock` and verify the await interaction.

### Requirements

- Use `AsyncMock`.
- Configure the awaited result.
- Run the async test with pytest-compatible async support already present in the environment.
- Assert the result and an await assertion.

### Expected Outcome

The test should exercise the async boundary without making a real network call.

### Solution

```python
from unittest.mock import AsyncMock


async def test_load_user_awaits_client():
    client = AsyncMock()
    client.fetch_user.return_value = {"id": 7, "name": "Alice"}

    result = await load_user(client, 7)

    assert result == "Alice"
    client.fetch_user.assert_awaited_once_with(7)
```

Useful await-state checks include:

```python
client.fetch_user.assert_awaited()
client.fetch_user.assert_awaited_once()
client.fetch_user.assert_awaited_with(7)
assert client.fetch_user.await_count == 1
```

### How to Solve It

1. Find the actual async boundary.
2. Replace the async dependency with `AsyncMock`, not a normal `Mock`.
3. Configure `return_value` on the async mock so awaiting it produces the desired result.
4. Assert the application result and the meaningful await interaction.

### Why This Works

Async functions return awaitable behavior. `AsyncMock` is designed to model async call/await semantics and provides await-specific assertions that a normal `Mock` does not provide.

### Common Mistake

Using `Mock()` for an async function and then asserting `assert_called_once_with()`. That can test the call shape while missing the crucial question of whether the coroutine was actually awaited.

### Key Learning

For async boundaries, test both the returned behavior and the await contract that matters to the application.

## Question 18 — Choose mock_open or a Real Temporary File

### Difficulty
Hard

### Problem

A file-processing function opens a text file, reads its contents, and counts lines. You need two tests:

1. a unit test focused on how the function reacts to a controlled file stream, and
2. an integration-style test that verifies actual filesystem behavior.

Design both tests and explain why `mock_open()` is appropriate for the first while a temporary file may be better for the second.

### Requirements

- Use `mock_open()` in the unit test.
- Assert the `open()` call.
- Use a real temporary file for filesystem behavior.
- Explain the realism trade-off.

### Expected Outcome

The first test isolates file-opening behavior; the second validates the real filesystem boundary.

### Solution

Unit-style test:

```python
from unittest.mock import mock_open, patch


def test_count_lines_reads_file():
    m = mock_open(read_data="a\nb\nc\n")

    with patch("service.open", m):
        assert count_lines("data.txt") == 3

    m.assert_called_once_with("data.txt", "r", encoding="utf-8")
```

Real temporary-file test:

```python
def test_count_lines_with_real_file(tmp_path):
    path = tmp_path / "data.txt"
    path.write_text("a\nb\nc\n", encoding="utf-8")

    assert count_lines(path) == 3
```

The first test is fast and completely controlled. The second proves that the code actually interacts correctly with the filesystem.

### How to Solve It

1. Decide which behavior is under test.
2. For a unit test, replace the external file handle with controlled data.
3. For boundary/integration confidence, create a real temporary resource.
4. Avoid using the mock-based test as proof that the operating system and file semantics work exactly as expected.

### Why This Works

Mocking a file opening isolates application logic. A real temporary file exercises serialization, encoding, path handling, actual file operations, and cleanup more realistically. Neither layer replaces the other.

### Common Mistake

Using `mock_open()` for every file test, then assuming the application is proven against real filesystem behavior.

### Key Learning

Choose the test double based on the behavior you need to prove: local logic or a real resource boundary.

## Question 19 — Turn a Production Failure into a Regression Test

### Difficulty
Hard

### Problem

A production log says:

```text
ERROR failed to parse upstream response
ValueError: missing field: amount
```

The API sometimes returns an object without `amount`. The application currently crashes. Describe and implement a regression workflow using a controlled dependency response.

### Requirements

- Reproduce the malformed response deterministically.
- Write a failing pytest test before the fix.
- Control the API response with a test double.
- Verify the corrected behavior.
- Keep the regression case after the fix.

### Expected Outcome

The malformed payload should become a stable test input representing the historical production failure.

### Solution

```python
from unittest.mock import Mock


def test_missing_amount_is_handled():
    api = Mock()
    api.fetch.return_value = {"id": "order-17", "status": "ready"}

    result = process_order(api)

    assert result["status"] == "invalid"
    assert result["reason"] == "missing amount"
```

Workflow:

```text
production symptom
    ↓
controlled malformed response
    ↓
failing regression test
    ↓
fix parser/handler
    ↓
rerun focused test
    ↓
run broader regression suite
```

The exact assertion depends on the intended application contract; the important point is that the historical failure becomes a repeatable case.

### How to Solve It

1. Extract the smallest input that still reproduces the defect.
2. Replace the external service with a controlled response.
3. Encode the historical failure as a test.
4. Fix the production logic.
5. Rerun the test and keep it permanently as regression protection.

### Why This Works

Regression tests convert a one-time defect into a durable safety check. A mock or stub makes the failure deterministic without requiring the production API to fail again.

### Common Mistake

Writing only a happy-path test after fixing the parser. That proves the normal path but does not protect against reintroducing the malformed-response bug.

### Key Learning

A bug is not fully protected until its smallest reliable reproduction is encoded as a regression test.

## Question 20 — Diagnose Duplicate and Misleading Logging

### Difficulty
Hard

### Problem

A request is processed by three layers. A single failure produces three error log entries, and one entry includes a full customer payload. Explain why this is a problem and redesign the logging behavior.

### Requirements

- Identify the duplication problem.
- Decide where the exception should be logged.
- Preserve useful context without repeating the same traceback at every layer.
- Remove sensitive payload data from the log.

### Expected Outcome

A good design logs an exception where the layer has enough context to make the event operationally useful, while upper layers should either propagate the exception or log only additional context when genuinely necessary.

### Solution

A reasonable design:

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
        logger.exception("request failed; request_id=%s", request_id)
        raise
```

Do not repeat the same logging pattern independently at every layer. For example, an inner layer can propagate the exception while the request boundary records the operational event:

```python
try:
    repository_call(client)
except TimeoutError:
    logger.exception("request failed; request_id=%s", request_id)
    raise
```

Unless an additional log entry adds distinct, safe information and the architecture intentionally requires it, avoid logging the same exception again. Prefer identifiers and safe metadata over raw customer content.

### How to Solve It

1. Identify the exception's natural ownership boundary.
2. Decide where a traceback adds operational value.
3. Propagate without re-logging the same event everywhere.
4. Add only new context when needed.
5. Sanitize or omit sensitive fields.

### Why This Works

Duplicate logging increases noise, inflates log volume, and makes one incident look like multiple independent failures. Sensitive payload logging creates a separate security/privacy problem. Logging should preserve signal rather than simply maximize output.

### Common Mistake

Treating “more logs” as automatically better diagnostics. Another common mistake is logging the entire request because it seems convenient for debugging.

### Key Learning

Good observability is contextual and intentional: enough information to diagnose, without duplicated events or unsafe data.

## Question 21 — Design a Data-Pipeline Test Boundary

### Difficulty
Hard

### Problem

A data pipeline looks like:

```text
input file
  ↓
parser
  ↓
validator
  ↓
transformer
  ↓
database writer
```

For a unit test of the transformer, decide which components should be real and which should be replaced. Then describe one integration test that should use a real dependency.

### Requirements

- Keep the unit test isolated.
- Choose an appropriate test double for the database boundary.
- Include meaningful valid/invalid behavior.
- Add one integration test against a real controlled database boundary or equivalent integration environment.

### Expected Outcome

The unit test should focus on transformation behavior and not prove database connectivity or SQL correctness.

### Solution

Unit test strategy:

```text
input rows → real
transformer → real
validator → real or controlled, depending on the test goal
database writer → fake/stub/mock
```

Example:

```python
from unittest.mock import Mock


def test_transformer_normalizes_amounts():
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
```

Integration test concept:

```text
real application code
      ↓
real repository/database boundary
      ↓
verify persisted rows
```

That integration layer is the appropriate place to discover problems in SQL, schema mapping, transactions, or database connectivity.

### How to Solve It

1. Start from the behavior being tested.
2. Keep pure transformation logic real.
3. Replace boundaries whose real infrastructure would distract from that unit's behavior.
4. Add a separate integration test for the real database contract.

### Why This Works

Mocking the database can prove that the application called a repository or writer correctly, but it cannot prove SQL syntax, schema compatibility, transaction semantics, or actual persistence. Those require integration coverage.

### Common Mistake

Mocking the database and then claiming the whole pipeline is tested end-to-end.

### Key Learning

Data pipelines need multiple layers: fast unit tests for transformations plus real boundary tests for persistence and integration behavior.

---

## Advanced — Questions 22–28

## Question 22 — Design a Layered Strategy for a Multi-Dependency Backend

### Difficulty
Advanced

### Problem

A backend service depends on:

- PostgreSQL
- Redis
- an external REST API
- a message queue
- a logging/diagnostics subsystem

Design a practical testing strategy across **unit, contract, integration, and E2E** layers. You must decide where mocks, stubs, fakes, temporary resources, and real dependencies belong.

### Requirements

- Give at least one example of each test layer.
- Identify sensible test doubles.
- Explain what real integration should validate.
- Keep E2E scenarios focused on critical workflows.
- Explain how the strategy balances speed and realism.

### Expected Outcome

The answer should be a layered strategy rather than “mock everything” or “use everything for every test.”

### Solution

A strong strategy could look like:

```text
UNIT
- real business logic
- mocks/stubs/fakes for external boundaries
- deterministic failure simulation

CONTRACT
- verify request/response shapes for important external interfaces
- detect interface drift

INTEGRATION
- real PostgreSQL in a controlled test environment
- real Redis or a controlled integration environment when its behavior matters
- real queue/broker test environment for producer/consumer semantics
- external API sandbox/controlled test service where available

E2E
- complete critical workflows through the real application boundary
- keep scenarios limited and stable
```

For unit tests, a repository may use a fake or mock depending on whether the focus is state behavior or interaction. The message queue consumer's acknowledgment/retry semantics should have real integration coverage because a mock cannot prove broker behavior. The REST API boundary benefits from contract/integration coverage so a locally configured mock does not become the only source of truth.

### How to Solve It

1. Map each dependency to the behavior you need to prove.
2. Use the cheapest reliable test double in unit tests.
3. Add contract or integration coverage where mocks can become stale.
4. Reserve E2E for complete workflows rather than every branch.
5. Use realistic failure tests for timeouts, malformed responses, and retries.

### Why This Works

Production confidence comes from complementary layers. Unit tests give fast isolation; contract and integration tests protect real boundaries; E2E tests verify that the whole workflow still works.

### Common Mistake

Declaring “all five dependencies are external, so all five must be mocked in every test.” That creates false confidence and can leave real integration failures undetected.

### Key Learning

Choose the test layer from the contract you need to prove, not from a blanket rule about mocks.

## Question 23 — Design a Resilient API Client Test Matrix

### Difficulty
Advanced

### Problem

An API client has:

- a timeout
- retry-on-timeout behavior
- a non-retryable authorization failure
- a malformed successful response
- a successful retry

Design a test matrix and identify which cases are best handled with unit mocks and which should also have integration or contract coverage.

### Requirements

- Include all five scenarios.
- Use `side_effect` for at least one retry scenario.
- Explain what to assert for attempts, final outcome, and errors.
- Distinguish mocked tests from external-boundary validation.

### Expected Outcome

The unit suite should deterministically cover the decision logic, while integration/contract coverage should confirm the client still matches the external API contract.

### Solution

A useful matrix:

| Scenario | Unit test | Contract/integration | Key assertions |
|---|---|---|---|
| Timeout | Yes | Optional/appropriate depending on environment | retry decision, final failure |
| Retry succeeds | Yes | Yes where practical | 2 attempts, final response |
| 401/403 | Yes | Yes for contract behavior | non-retry behavior, error mapping |
| Malformed response | Yes | Yes if contract drift is a risk | validation error/fallback |
| Normal success | Yes | Yes | parsed result |

Example retry unit test:

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

The exact contract/integration setup depends on the external service's test environment; the key point is that mocked responses are not proof that the real service still returns the same schema.

### How to Solve It

1. Separate decision logic from real transport.
2. Enumerate success, retryable failure, non-retryable failure, malformed response, and terminal failure.
3. Make every unit scenario deterministic.
4. Add real-boundary validation for interface drift.

### Why This Works

A retry algorithm can be fully tested without a live service, but the live service can still change its response schema, status behavior, or authentication contract. This is why contract/integration tests complement mocks.

### Common Mistake

Asserting only `call_count == 2` and forgetting to verify the final application behavior. Another mistake is treating a fake response body as authoritative API documentation.

### Key Learning

Test the retry decision deterministically, then separately verify the real external contract.

## Question 24 — Reduce a Large Data-Pipeline Failure to an MRE

### Difficulty
Advanced

### Problem

A batch job processes 2 million records. One record causes:

```text
ERROR transform failed
ValueError: invalid literal for int() with base 10: '9O1'
```

The full pipeline includes file ingestion, validation, transformation, database writes, and logging. Describe how you would create a minimal reproducible example and then turn it into a regression test.

### Requirements

- Reduce the dataset.
- Remove irrelevant dependencies where possible.
- Preserve the failing input.
- Capture the traceback/log context.
- Make the reproduction deterministic.
- Add a regression test after the fix.

### Expected Outcome

The final reproduction should preserve the smallest input that still triggers the failure, ideally one record plus the transformation logic needed to fail.

### Solution

A systematic reduction:

```text
2,000,000-row job
      ↓
find failing record
      ↓
extract one or a few relevant records
      ↓
run transformer without database/output side effects
      ↓
reproduce ValueError deterministically
      ↓
inspect exact field/value
      ↓
fix parser/validation
      ↓
encode malformed record as regression case
```

Possible regression test:

```python
import pytest


def test_transform_rejects_or_handles_letter_o_in_numeric_field():
    row = {"amount": "9O1"}

    with pytest.raises(ValueError):
        transform_row(row)
```

If the intended contract is graceful rejection instead of raising, assert that contract instead. The important step is preserving the exact historical failure as a deterministic test.

### How to Solve It

1. Find the smallest failing input.
2. Remove components that do not participate in reproducing the defect.
3. Keep the same malformed value and transformation path.
4. Capture enough traceback/log evidence to identify the faulty operation.
5. Convert the reproduction into a regression test.

### Why This Works

A minimal reproducible example is a diagnostic tool, not merely a tiny program. It should be as small as possible **while still reproducing the bug**. Removing too much can destroy the failure.

### Common Mistake

Reducing the input so aggressively that the bug disappears, then concluding the problem is fixed.

### Key Learning

Minimize for relevance, not for an arbitrary line count. Preserve the smallest reproduction that still fails.

## Question 25 — Test an LLM Application Without Pretending to Test Model Quality

### Difficulty
Advanced

### Problem

An application does:

```text
user text
  ↓
LLM client
  ↓
JSON-like structured response
  ↓
validator
  ↓
business logic
```

Design a deterministic unit test that uses a mocked LLM response to verify parsing, validation, and fallback behavior. Then state what this test does **not** establish about the real model.

### Requirements

- Mock the LLM client.
- Use a deterministic structured response.
- Cover at least one malformed-response case.
- Assert application behavior.
- Clearly separate orchestration testing from model evaluation.

### Expected Outcome

The mocked test should validate application control flow around the model boundary, not the model's semantic quality.

### Solution

```python
from unittest.mock import Mock


def test_llm_response_is_validated_and_used():
    llm = Mock()
    llm.generate.return_value = {
        "label": "refund_request",
        "confidence": 0.91,
    }

    result = classify_message(
        llm,
        "I need a refund",
    )

    assert result["label"] == "refund_request"
    assert 0.0 <= result["confidence"] <= 1.0
```

Malformed-response case:

```python

def test_malformed_llm_response_uses_fallback():
    llm = Mock()
    llm.generate.return_value = {"confidence": "not-a-number"}

    result = classify_message(llm, "hello")

    assert result["label"] == "fallback"
```

These tests prove that the application validates and handles the response as designed. They do not prove the actual model is accurate, useful, safe, or reliable on real inputs.

### How to Solve It

1. Replace the probabilistic model output with a deterministic known response.
2. Test the parser/validator/business logic around that boundary.
3. Add malformed and missing-field cases.
4. Keep model evaluation as a separate concern using real models and evaluation data.

### Why This Works

Mocking makes orchestration deterministic, which is valuable for unit tests. But the real LLM may produce different content, formatting, latency, refusal behavior, or quality characteristics that a static mock cannot reveal.

### Common Mistake

Treating a passing mocked LLM test as evidence that “the model works.” The test has proven application behavior around a simulated model response.

### Key Learning

Mock the model boundary to test application logic; evaluate model quality with real evaluation methodology.

## Question 26 — Test an Agentic AI Orchestration Boundary

### Difficulty
Advanced

### Problem

An agent executes:

```text
Agent
  ↓
LLM chooses tool
  ↓
tool router
  ↓
external API
  ↓
validated result
  ↓
final response
```

Design a test strategy for the orchestration logic that does not call the real LLM, search service, API, database, or browser automation.

### Requirements

- Identify which boundaries can be mocked/stubbed/faked.
- Test tool routing and state transitions.
- Test at least one tool failure and retry/fallback path.
- State which properties require real integration or E2E testing.

### Expected Outcome

The unit layer should deterministically simulate model decisions and tool outcomes while validating observable agent behavior.

### Solution

A unit-style orchestration setup:

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

    result = run_agent(llm, tools, "What is the weather in Kolkata?")

    assert result["temperature"] == 30
    tools.weather.assert_called_once_with(city="Kolkata")
```

Failure-path test:

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

What still needs higher-level testing:

```text
real model behavior
real tool execution
real retrieval quality
real service integration
real latency characteristics
critical end-to-end workflows
```

The mocked layer should test observable routing, tool invocation, state transitions, and recovery—not hidden reasoning.

### How to Solve It

1. Define observable agent contracts.
2. Replace each external boundary independently.
3. Feed deterministic model decisions.
4. Simulate tool results, failures, and retries.
5. Add real integration/E2E coverage for the boundaries that mocks cannot validate.

### Why This Works

Agent systems have a deterministic orchestration layer surrounding probabilistic and external components. Mocked tests can strongly validate routing and recovery logic, but they cannot establish real model quality or real-world tool behavior.

### Common Mistake

Trying to assert hidden chain-of-thought or exact internal reasoning. The test should focus on observable actions, arguments, state transitions, and outcomes.

### Key Learning

For agentic systems, test the deterministic orchestration boundary with controlled doubles and reserve real evaluation/integration for the parts that are inherently external or probabilistic.

## Question 27 — Refactor Mock Hell with Dependency Injection and a Protocol

### Difficulty
Advanced

### Problem

A service constructor creates three concrete clients internally and the test requires a long chain of nested patches and mocks. Redesign the boundary so the service receives a dependency that follows a small typed interface. Then show how the test becomes simpler.

### Requirements

- Introduce a small Python `Protocol` for the dependency boundary.
- Use dependency injection.
- Prefer a small fake or mock aligned with that interface.
- Explain why this reduces mock complexity.
- Keep the focus on behavior rather than internal implementation details.

### Expected Outcome

The redesigned service should depend on an explicit boundary instead of constructing unrelated infrastructure internally.

### Solution

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

Simple test double:

```python
from unittest.mock import create_autospec


def test_display_name():
    repository = create_autospec(UserRepository, instance=True)
    repository.get_user.return_value = {"id": 1, "name": "Alice"}

    service = UserService(repository)

    assert service.display_name(1) == "Alice"
```

The important architectural change is that the service no longer decides how the repository is constructed. The boundary is explicit, injectable, and easy to substitute.

### How to Solve It

1. Find the code that constructs concrete infrastructure internally.
2. Extract the smallest interface the service actually needs.
3. Inject that dependency through the constructor.
4. Build a focused fake or autospecced mock in the unit test.
5. Keep integration tests for the real repository/database boundary.

### Why This Works

Dependency injection makes dependencies explicit and testable. A small protocol reduces the temptation to mock a huge framework object, while type hints document the expected interface. This is also naturally aligned with modular package design from Module 06.

### Common Mistake

Replacing one complicated patch chain with another large mock object that mirrors every private method of a framework client. That moves the complexity rather than reducing it.

### Key Learning

Good architecture often reduces the need for complicated mocks: isolate business logic behind small, explicit dependency boundaries.

## Question 28 — Diagnose a Production Failure End-to-End

### Difficulty
Advanced

### Problem

A CI job fails after a package refactor. The project uses a `src/` package layout. The failure report contains:

```text
FAILED tests/test_payment.py::test_charge

Traceback (most recent call last):
  File "src/payments/service.py", line 41, in charge
    result = self.gateway.charge(amount)
  File "src/payments/gateway.py", line 22, in charge
    raise PaymentGatewayError("gateway request failed") from exc
payments.errors.PaymentGatewayError: gateway request failed
```

A debug log shows:

```text
ERROR charge failed request_id=req-1842 amount=500
``

The unit test mocks `gateway.Gateway`, but `service.py` imports `Gateway` into its own namespace. The mock is therefore not replacing the object used by `PaymentService`.

Design the complete investigation, fix, regression protection, and test-layer follow-up. Also explain what you would check in the package/test environment after the refactor.

### Requirements

- Identify the immediate test failure and likely mock problem.
- Explain how the traceback and exception chaining help.
- State where to patch.
- Describe a deterministic regression test.
- Distinguish unit, integration, and E2E follow-up tests.
- Include safe logging and reproduction steps.
- Include one Module 06 package/environment check relevant to the refactor.

### Expected Outcome

The immediate defect is likely a wrong patch target, not proof that the real payment gateway is broken. The investigation should verify the import binding, reproduce the failure, correct the test double, then add/strengthen boundary coverage so real gateway integration is not silently ignored.

### Solution

Investigation:

```text
1. Run only the failing test.
2. Read the traceback from the test frame into the service/gateway call chain.
3. Inspect the exception chain: PaymentGatewayError was raised from the original exception.
4. Inspect the mock configuration and import style.
5. Confirm whether the application reads service.Gateway or gateway.Gateway.
6. Patch the lookup location used by service.py.
```

Likely correction:

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

Reproduction/regression path:

```text
CI failure
  ↓
focused failing test
  ↓
verify wrong patch target
  ↓
correct patch
  ↓
add/keep regression case for imported binding
  ↓
run focused test
  ↓
run Module 07 regression suite
  ↓
run real payment integration/contract coverage
```

Safe diagnostic logging should keep the request ID and only log amounts/metadata permitted by policy. Do not log credentials or payment details just because a failure occurred.

Package/environment follow-up:

- verify the test runner is importing the intended package from the project’s configured `src/` layout;
- verify the test environment has the expected project dependencies installed from the project's dependency configuration/lock workflow;
- run the normal project type/lint checks if they are part of the established quality gate.

These checks support the refactor but do not replace the behavioral diagnosis.

### How to Solve It

1. Narrow the failure to one test.
2. Use traceback evidence to locate the failing boundary.
3. Inspect exception chaining for preserved cause information.
4. Trace imports to determine the lookup namespace.
5. Verify the mock actually replaces the dependency used by the service.
6. Reproduce deterministically with a controlled dependency.
7. Fix the test or production code as appropriate.
8. Add regression protection.
9. Restore confidence in the real external boundary with integration/contract coverage.
10. Check package/environment correctness after a module/package refactor.

### Why This Works

This is a complete production debugging loop: failure → evidence → reproduction → root-cause hypothesis → controlled experiment → fix → regression test → broader validation. The traceback identifies the active failure path, logging adds safe runtime context, mocking isolates the unit, and integration coverage checks the real dependency boundary.

### Common Mistake

Assuming the traceback proves that the gateway itself is broken, or simply changing the assertion until the test passes. Another common mistake is fixing the mock while never adding a real integration/contract check for the external boundary.

### Key Learning

A reliable engineer connects tests, imports, mocks, tracebacks, logs, reproduction, and integration coverage into one evidence-driven workflow.

---

# Final Coverage Summary

| Topic | Questions |
|---|---|
| Unit / Integration / E2E | 1, 21, 22, 23, 25, 26, 28 |
| pytest assertions / `pytest.raises` | 2, 5, 19, 24, 25 |
| Fixtures | 3, 8 |
| Parametrization | 4, 8, 9 |
| Arrange–Act–Assert and test design | 2, 3, 8, 9, 13, 21 |
| Boundary / invalid testing | 4, 5, 9, 19, 23, 24, 25 |
| Regression testing | 9, 19, 24, 28 |
| Debugging / debugger / call stack | 10, 15, 28 |
| Tracebacks / exception propagation / chaining | 6, 11, 19, 24, 28 |
| Logging / diagnostics / safe context | 6, 11, 20, 24, 28 |
| Minimal reproducible examples | 19, 24, 28 |
| Test doubles | 7, 14, 18, 21, 22 |
| Mocking APIs / patching / call assertions | 7, 12, 13, 14, 15, 16, 17, 18, 21, 23, 25, 26, 27, 28 |
| `Mock`, `MagicMock` concepts, `return_value`, `side_effect` | 7, 13, 15, 16, 17, 21, 23, 25, 26, 27 |
| `patch`, `patch.object`, lookup-target reasoning | 12, 28 |
| `patch.dict`, `patch.multiple`, `PropertyMock`, `monkeypatch` | 14 |
| `autospec`, `spec`, `spec_set`, `create_autospec` | 16, 27 |
| `mock_open` / temporary resources | 18 |
| `AsyncMock` | 17 |
| API / database / message / external dependency strategy | 21, 22, 23, 28 |
| LLM application testing | 25 |
| Agentic AI testing | 26 |
| Dependency injection / Protocol boundary | 27, 28 |
| Production testing strategy | 22, 23, 28 |
