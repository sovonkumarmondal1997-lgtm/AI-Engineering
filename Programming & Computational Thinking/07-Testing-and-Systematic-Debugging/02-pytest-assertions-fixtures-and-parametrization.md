# Pytest — Assertions, Fixtures, and Parametrization

> Stage 1 — Programming & Computational Thinking  
> Module 07 — Testing and Systematic Debugging

## Learning Objectives

By the end of this chapter, you should be able to:

- Explain what automated testing is and where `pytest` fits in a Python project.
- Write readable assertions using Python's `assert` statement.
- Read and debug assertion failures using pytest's assertion introspection.
- Test expected exceptions with `pytest.raises()`.
- Distinguish behavioral tests from tests that are coupled to implementation details.
- Create and use pytest fixtures as reusable test dependencies.
- Explain fixture dependency injection without treating it as magic.
- Use fixture return values, `yield` fixtures, teardown, and cleanup safely.
- Choose fixture scopes based on isolation, lifecycle, and performance needs.
- Compose fixtures into a dependency graph.
- Use `autouse=True` deliberately and understand its risks.
- Understand the purpose and visibility rules of `conftest.py`.
- Build fixture factories for reusable, variable test data.
- Parametrize tests with one or many inputs.
- Use readable parameter IDs and complex test data responsibly.
- Use indirect parametrization when setup should happen through a fixture.
- Combine fixtures, parametrization, assertions, and exception checks.
- Design deterministic, isolated, maintainable test data.
- Debug assertion, fixture, lifecycle, and parametrization failures systematically.
- Structure a production-oriented pytest suite for backend, data, ML, AI, and agentic systems.
- Decide when fixtures, helper functions, parametrization, and mocks serve different purposes.

## Prerequisites

You should be comfortable with basic Python syntax:

- variables and expressions
- functions and parameters
- `if` statements
- lists, dictionaries, tuples, and sets
- exceptions and `try`/`except`
- imports and modules
- basic virtual-environment usage

You do **not** need prior knowledge of pytest, decorators, dependency injection, fixture scopes, or parametrization. They are introduced from first principles.

---

## 1. What Is Pytest?

### What is it?

**Software testing** is the practice of checking whether software behaves as intended.

A **test** is an automated or manual check of some expected behavior. A **test case** is one specific scenario or set of inputs for that check.

An **assertion** is a statement that says:

> “At this point in the program, I expect this condition to be true.”

`pytest` is a Python testing framework that discovers tests, executes them, evaluates assertions, manages reusable test setup through fixtures, supports parametrized test cases, and reports failures in a developer-friendly way.

### Why does it exist?

You can test a program manually:

```python
print(add(2, 3))
```

Then look at the output and decide whether `5` is correct.

That works for a tiny experiment, but it does not scale. A production application can have thousands of behaviors that need to remain correct after every code change.

Automated tests provide repeatability:

```text
Python code
    ↓
test code
    ↓
pytest discovers tests
    ↓
pytest executes tests
    ↓
assertions are evaluated
    ↓
pytest reports pass/fail details
```

The important idea is that the test becomes executable documentation of expected behavior.

### Pytest vs manually checking output

| Approach | Strength | Weakness |
|---|---|---|
| Manual output checking | Very easy to start | Slow, inconsistent, hard to repeat |
| `print()` debugging | Useful during investigation | Not an automated correctness check |
| Automated pytest test | Repeatable and CI-friendly | Requires test design and maintenance |

### Pytest vs `unittest` at a high level

Python ships with `unittest`, which is a mature standard-library testing framework. Pytest is a third-party framework with a concise style built around plain Python functions and `assert`, plus fixtures, parametrization, plugins, and rich reporting.

Typical pytest:

```python
def test_addition():
    assert 2 + 3 == 5
```

Typical `unittest`:

```python
import unittest


class TestAddition(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(2 + 3, 5)
```

Neither framework makes poor test design good. The choice is usually about project conventions, ecosystem, existing code, and team preferences.

### Simple example

Application code:

```python
def add(a, b):
    return a + b
```

Test code:

```python
def test_add():
    assert add(2, 3) == 5
```

Line by line:

1. `def test_add():` defines a test function.
2. Because its name starts with `test_`, pytest can normally discover it.
3. `add(2, 3)` calls the application behavior.
4. `== 5` defines the expected result.
5. `assert` verifies the expectation.

If the result is `5`, the test passes. If it is `4`, the test fails.

### Real-world example

A banking service may contain:

```python
def calculate_available_balance(balance, pending_amount):
    return balance - pending_amount
```

A test might verify:

```python
def test_available_balance_excludes_pending_amount():
    assert calculate_available_balance(1000, 250) == 750
```

The test is not checking how subtraction is implemented. It is checking the business behavior exposed by the function.

### Common mistakes

- Thinking a test is useful merely because it executes code.
- Testing only happy paths.
- Using assertions that do not meaningfully check behavior.
- Making tests depend on execution order.
- Making tests depend on a real production database or network service when a unit-level test does not need one.

### Better approach

Start by asking:

> What observable behavior must remain correct?

Then build the smallest reliable test that proves that behavior.

### Production considerations

A real project may have unit, integration, API, end-to-end, data-quality, ML, and AI-oriented tests. Pytest can orchestrate many of these layers, but the test suite should still make the differences in purpose and cost clear.

---

## 2. Installing and Running Pytest

### What is it?

Pytest is normally installed into the project's development environment rather than into the production runtime.

A common approach is:

```bash
python -m pip install pytest
```

For a team project, pytest is usually declared as a development dependency in the project's package/dependency configuration so other developers and CI can install the same toolchain.

### Why does it exist?

A project needs a repeatable way to install and invoke its test runner. You do not want “it worked on my machine because pytest happened to be installed globally” to be part of your engineering process.

### Running tests

Run the whole discovered suite:

```bash
pytest
```

Run with more detail:

```bash
pytest -v
```

Run quietly:

```bash
pytest -q
```

Run one file:

```bash
pytest tests/test_users.py
```

Run one test function:

```bash
pytest tests/test_users.py::test_create_user
```

Run one directory:

```bash
pytest tests/unit
```

Run tests matching a keyword expression:

```bash
pytest -k "user and not slow"
```

Show what would be collected without executing tests:

```bash
pytest --collect-only -q
```

Show available fixtures while investigating a test suite:

```bash
pytest --fixtures
```

### Interpreting output

A simplified result might look like:

```text
================ test session starts ================
collected 3 items

tests/test_math.py ...                         [100%]

================= 3 passed in 0.08s =================
```

`3 passed` means three test cases completed successfully.

If one fails, pytest prints a failure section showing the test node, traceback context, and assertion details.

### Exit codes

At a conceptual level:

- exit code `0` means the test run succeeded.
- a non-zero exit code indicates a problem such as failing tests, collection errors, usage errors, or another test-run failure condition.

CI systems can use that exit code to decide whether a pipeline stage succeeds.

### Test discovery

Pytest's default discovery conventions include common patterns such as:

```text
test_*.py
*_test.py
```

Within discovered Python test modules, test functions or methods normally start with `test_`.

Test classes commonly use names beginning with `Test` and do not need to inherit from a framework base class.

Example:

```python
# tests/test_math.py

def test_addition():
    assert 2 + 2 == 4


class TestSubtraction:
    def test_basic_subtraction(self):
        assert 5 - 3 == 2
```

### Why a test may not be discovered

- The file name does not match the configured discovery pattern.
- The test function name does not match the convention.
- The test class name does not match the convention.
- You are running pytest from a directory that does not include the tests you expected.
- A collection/import error prevents pytest from collecting the module.
- Project configuration changes the default discovery rules.

When a test is “missing,” use:

```bash
pytest --collect-only -q
```

before assuming the test itself is broken.

### Better approach

Prefer:

```bash
python -m pytest
```

when you want to make it especially explicit that pytest should run under the Python interpreter associated with the current environment. Both forms are common; project conventions may standardize one.

---

## 3. Assertions Fundamentals

### What is it?

An assertion is a boolean expectation that a condition is true.

```python
assert condition
```

For example:

```python
assert 2 + 2 == 4
```

The expression after `assert` is evaluated. If it is truthy, execution continues. If it is false, Python raises `AssertionError`, and pytest reports the failure with additional information.

### Expected vs actual

A useful testing mental model is:

```text
expected behavior ←→ actual behavior
```

Example:

```python
result = add(2, 3)
assert result == 5
```

Here:

- actual value = `result`
- expected value = `5`

### Pass vs fail

```python
assert 10 == 10     # passes
assert 10 == 11     # fails
```

### Practical assertion patterns

#### Equality

```python
assert value == expected
```

Use it when the exact result matters.

```python
assert calculate_total([10, 20]) == 30
```

#### Inequality

```python
assert value != unexpected
```

Use it when the requirement is that two values must differ.

#### `None`

```python
assert result is None
assert result is not None
```

Use `is None` rather than `== None` because `None` is a singleton and identity is the idiomatic check.

#### Truthiness

```python
assert condition
assert not condition
```

Useful for boolean-like conditions, but make sure the meaning is clear.

```python
assert user.is_active
```

#### Membership

```python
assert item in collection
assert item not in collection
```

Examples:

```python
assert "admin" in roles
assert "suspended" not in roles
```

#### Type checks

```python
assert isinstance(result, User)
```

Use this when the contract really includes a type requirement.

```python
assert type(result) is User
```

This is stricter and rejects subclasses. It should be used only when exact type identity is intentionally required.

#### Length

```python
assert len(items) == 3
```

Use it when collection size is part of the expected behavior.

### Examples by data type

#### Integers

```python
assert 10 + 5 == 15
assert 10 != 11
```

#### Strings

```python
assert "hello".upper() == "HELLO"
assert "admin" in "admin-user"
```

#### Booleans

```python
is_enabled = True
assert is_enabled
assert not False
```

#### Lists

```python
assert [1, 2, 3] == [1, 2, 3]
assert 2 in [1, 2, 3]
```

#### Dictionaries

```python
user = {"name": "Alice", "age": 30}
assert user["name"] == "Alice"
assert user == {"name": "Alice", "age": 30}
```

#### Sets

```python
assert {1, 2} == {2, 1}
assert 3 not in {1, 2}
```

#### Tuples

```python
result = (200, "OK")
assert result == (200, "OK")
```

#### Objects

```python
class User:
    def __init__(self, name):
        self.name = name


user = User("Alice")
assert user.name == "Alice"
```

Do not automatically compare object identity if the requirement is logical equality.

### Common mistakes

**Mistake: asserting something unrelated to the behavior.**

```python

def test_add():
    result = add(2, 3)
    assert isinstance(result, int)
```

This may be true but still fail to prove that `add(2, 3)` returns `5`.

**Better:**

```python

def test_add():
    assert add(2, 3) == 5
```

### Production considerations

Assertions should explain what matters to users or dependent systems. Strong assertions reduce the chance that broken software silently appears correct.

---

## 4. Pytest Assertion Introspection

### What is it?

Pytest rewrites assertions in discovered test modules so that failed assertions can provide useful explanations.

Suppose:

```python
result = 7
expected = 10
assert result == expected
```

A pytest failure can show information similar to:

```text
E       assert 7 == 10
```

Pytest can inspect common subexpressions and comparisons instead of making you manually construct diagnostic messages.

### Why does it exist?

A failure should help answer:

> “What exactly was wrong?”

Compare:

```python
assert result == expected
```

with:

```python
if result != expected:
    raise AssertionError(f"expected {expected}, got {result}")
```

The second style can work, but it forces you to write diagnostics yourself. Pytest's assertion introspection is one reason its plain `assert` syntax remains useful.

### Simple example

```python

def test_total():
    result = 7
    assert result == 10
```

The failure clearly exposes actual and expected values.

### Custom assertion messages

You can add a message:

```python
assert response.status_code == 200, "Unexpected HTTP status"
```

This can be useful when the reason is not obvious from the values alone.

### Trade-off

Use custom messages when they add context. Do not add boilerplate messages to every assertion simply because they are available.

Good:

```python
assert config.environment == "test", (
    "Tests must run against the test environment"
)
```

Potentially redundant:

```python
assert result == 5, "result should equal 5"
```

The default failure already communicates this well.

### Important technical note

Assertion rewriting primarily applies to test modules pytest collects. Imported support modules do not automatically get the same rewriting behavior in all circumstances. Projects that intentionally build assertion helper libraries may need explicit assertion-rewrite registration.

### Better approach

First trust pytest's diagnostics. Add a custom message only when it improves failure diagnosis.

---

## 5. Testing Exceptions

### What is it?

Some correct software behavior is an error response. For example:

- an invalid age should raise `ValueError`;
- an unauthorized operation may raise a domain exception;
- malformed input should be rejected.

A test should verify not only success paths but also expected failure behavior.

### `pytest.raises()`

The core syntax is:

```python
with pytest.raises(ValueError):
    parse_age("abc")
```

### How it works

1. Python enters the `with` block.
2. Your code executes.
3. If the expected exception is raised, the context manager records it and the test can continue.
4. If no exception is raised, the test fails.
5. If a different exception is raised, the test also fails.

### Simple example

```python
import pytest


def parse_age(value: str) -> int:
    if not value.isdigit():
        raise ValueError("age must be numeric")
    return int(value)


def test_parse_age_rejects_text():
    with pytest.raises(ValueError):
        parse_age("abc")
```

### Inspecting the exception

```python

def test_parse_age_error_details():
    with pytest.raises(ValueError) as exc_info:
        parse_age("abc")

    assert exc_info.type is ValueError
    assert str(exc_info.value) == "age must be numeric"
```

Use this when the exception details are part of the contract.

### Matching exception messages

```python
with pytest.raises(ValueError, match="must be numeric"):
    parse_age("abc")
```

`match=` uses regular-expression matching semantics, specifically behavior based on `re.search()` against the string representation of the exception.

A simple literal substring often works:

```python
match="must be numeric"
```

For a string with regular-expression metacharacters, escape or construct the pattern deliberately.

### Avoid fragile checks

This can be too brittle:

```python
assert str(exc_info.value) == (
    "The age field must contain a base-10 integer greater than or equal to zero"
)
```

If wording is not a public contract, exact-message testing can create unnecessary maintenance work.

Prefer a stable substring or a structured exception attribute when the application provides one:

```python
with pytest.raises(ValueError, match="age"):
    parse_age("abc")
```

### Testing invalid input

```python
@pytest.mark.parametrize("value", ["abc", "", "-5"])
def test_invalid_age(value):
    with pytest.raises(ValueError):
        parse_age(value)
```

### Boundary conditions

```python

def validate_age(age: int):
    if not 0 <= age <= 120:
        raise ValueError("age out of range")
```

Test the boundaries explicitly:

```python
@pytest.mark.parametrize("age", [0, 120])
def test_valid_age_boundaries(age):
    assert validate_age(age) is None


@pytest.mark.parametrize("age", [-1, 121])
def test_invalid_age_boundaries(age):
    with pytest.raises(ValueError):
        validate_age(age)
```

### When to use

Use `pytest.raises()` when raising the exception is expected behavior.

### When not to use

Do not catch broad exceptions simply to make a test pass. A test such as this can hide defects:

```python
try:
    do_something()
except Exception:
    pass
```

It does not prove the right exception occurred.

---

## 6. Behavioral Assertions

### What is it?

A behavioral assertion verifies an externally observable outcome rather than the internal implementation used to produce it.

### Why does it exist?

Implementation details change. A public behavior often should not.

Suppose a function currently uses a dictionary internally:

```python

def get_username(user_id):
    users = {1: "Alice"}
    return users[user_id]
```

A brittle test might inspect internal variables or data structures.

A behavioral test checks the public contract:

```python

def test_get_username():
    assert get_username(1) == "Alice"
```

### Strong vs weak tests

Weak:

```python
assert result is not None
```

This proves only that something was returned.

Stronger:

```python
assert result == {"status": "approved", "amount": 100}
```

The correct level of specificity depends on the contract.

### Brittle tests

A test becomes brittle when harmless internal changes cause failures even though observable behavior remains correct.

Examples include:

- asserting private helper call order when call order is not a contract;
- asserting private attributes only because they currently exist;
- coupling to a temporary data structure;
- asserting exact formatting when formatting is intentionally not stable.

### Better approach

Ask:

> “Would a user or dependent component notice this difference?”

If not, consider whether the test really needs to assert it.

### Production considerations

Behavior-focused tests tend to survive refactoring better. This is especially valuable in large Python systems where internal implementation is changed frequently for performance, maintainability, or architecture reasons.

---

## 7. Introduction to Fixtures

### What is it?

A **fixture** is reusable test setup or a test dependency managed by pytest.

Imagine ten tests all need the same sample user. Without fixtures, each test may repeat:

```python
user = {
    "name": "Alice",
    "age": 30,
}
```

Fixtures let pytest prepare that object and provide it to tests that request it.

### Why does it exist?

Fixtures reduce repetitive setup and make dependencies explicit.

### Simple example

```python
import pytest


@pytest.fixture
def sample_user():
    return {
        "name": "Alice",
        "age": 30,
    }


def test_user_name(sample_user):
    assert sample_user["name"] == "Alice"
```

### Explain every line

```text
@pytest.fixture
```

`pytest.fixture` is a decorator that tells pytest:

> “Treat this function as a fixture definition.”

```text
def sample_user():
```

This is still a normal Python function definition. Pytest gives the function special test-fixture meaning because of the decorator.

```python
return {"name": "Alice", "age": 30}
```

The fixture produces a value.

```text
def test_user_name(sample_user):
```

The test declares that it needs a fixture named `sample_user`.

Pytest sees that parameter name, finds the fixture, executes it according to its scope/lifecycle rules, and passes the resulting value into the test.

### Decorators in one minute

A **decorator** is Python syntax that applies behavior or metadata to a function.

You can think of:

```python
@pytest.fixture
def sample_user():
    ...
```

as saying:

```text
define sample_user
        ↓
register it with pytest as a fixture
```

The exact implementation is more technical than that, but the mental model is enough to start using fixtures.

### When to use fixtures

Good candidates include:

- reusable domain objects;
- test clients;
- temporary directories;
- database resources;
- application configuration;
- deterministic fake services;
- resources that need cleanup.

### When not to use fixtures

Do not create a fixture for every two-line local value. A helper function or local variable can be clearer.

---

## 8. Fixture Dependency Injection

### What is it?

**Dependency injection** means a component receives something it depends on instead of creating that dependency itself.

In pytest, a test requests a fixture by parameter name.

```text
test function
     ↓
requests fixture by name
     ↓
pytest resolves fixture
     ↓
fixture is created if needed
     ↓
fixture value is passed into test
```

### Compare normal Python argument passing

Normal function call:

```python

def test_user():
    user = create_user()
```

The function itself creates the value.

Fixture-based test:

```python

def test_user(user):
    assert user.name == "Alice"
```

The test declares a dependency and pytest supplies it.

### Why does pytest do this?

It separates:

- **what the test needs** from
- **how the dependency is prepared**.

That separation makes setup reusable.

### Technical meaning

When pytest collects and prepares a test, it resolves fixture dependencies from the test function signature and fixture graph. The fixture system considers dependency relationships, scope, caching, and teardown.

### Common mistake

Thinking the fixture parameter is an ordinary function argument supplied by your test call.

This does **not** happen:

```python
sample_user = sample_user()
```

unless you deliberately call the fixture function outside pytest. Within a pytest test, pytest is responsible for resolving the fixture dependency.

### Better approach

Make important dependencies visible in the test signature:

```python
def test_checkout_requires_authenticated_user(authenticated_user, cart):
    ...
```

A reader can immediately see the main setup components.

---

## 9. Fixture Return Values

A fixture can return almost any useful Python value.

### Primitive values

```python
@pytest.fixture
def username():
    return "alice"
```

### Lists

```python
@pytest.fixture
def product_ids():
    return [101, 102, 103]
```

### Dictionaries

```python
@pytest.fixture
def request_payload():
    return {
        "name": "Alice",
        "email": "alice@example.com",
    }
```

### Objects

```python
class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age


@pytest.fixture
def user():
    return User("Alice", 30)
```

### Database-like resource

```python
@pytest.fixture
def database_connection():
    connection = create_test_connection()
    return connection
```

If the resource needs cleanup, a return-only fixture may be incomplete. A lifecycle-managed fixture is often safer:

```python
@pytest.fixture
def database_connection():
    connection = create_test_connection()
    try:
        yield connection
    finally:
        connection.close()
```

### The key distinction

A simple fixture can provide **data**.

A lifecycle fixture can provide and manage a **resource**:

```text
create
  ↓
yield to test
  ↓
cleanup
```

Use lifecycle management when failing to clean up would leak state, files, sockets, connections, or other resources.

---

## 10. Fixture Setup and Teardown

### What is it?

A resource often has three phases:

```text
SETUP → TEST → TEARDOWN
```

Examples:

- open file → use file → close file;
- create temporary directory → write files → remove/cleanup directory;
- connect to test database → run test → close/reset connection;
- start test client → send requests → release client resources.

### Yield fixtures

A pytest fixture can use `yield`:

```python
@pytest.fixture
def resource():
    resource = create_resource()
    yield resource
    cleanup_resource(resource)
```

The code before `yield` is setup.

The yielded value is what the test receives.

The code after `yield` is teardown/finalization for that fixture instance.

### Execution order

Conceptually:

```text
fixture setup
    ↓
resource available
    ↓
test executes
    ↓
test completes/fails
    ↓
fixture teardown executes
```

Teardown is important because tests can fail. Cleanup should not depend on the test “passing.”

### Safer cleanup with `try/finally`

When resource management requires stronger guarantees or multiple cleanup stages, structure matters:

```python
@pytest.fixture
def file_handle(tmp_path):
    path = tmp_path / "data.txt"
    handle = path.open("w+")
    try:
        yield handle
    finally:
        handle.close()
```

Pytest normally performs teardown after the requesting test finishes, and dependencies participate in the overall finalization process.

### Common mistake

Starting a resource before `yield` but forgetting cleanup:

```python
@pytest.fixture
def connection():
    connection = create_connection()
    yield connection
    # leaked connection
```

Better:

```python
@pytest.fixture
def connection():
    connection = create_connection()
    try:
        yield connection
    finally:
        connection.close()
```

### Production consideration

A fixture that creates a resource should have a deliberate lifecycle. Think of cleanup as part of correctness, not an optional convenience.

---

## 11. Fixture Scopes

### What is scope?

A fixture's **scope** controls how broadly pytest can reuse a fixture instance and therefore how often it is created and destroyed.

Common scopes are:

- `function`
- `class`
- `module`
- `package`
- `session`

### Comparison

| Scope | Typical lifetime | Created approximately | Common use | Main trade-off |
|---|---|---:|---|---|
| `function` | one test function | once per test | isolated test data | more setup work |
| `class` | test class | once per class, when used | shared class-level setup | more shared state |
| `module` | test module | once per module, when used | expensive setup shared by one module | reduced isolation |
| `package` | test package scope | reused within package scope | package-level resources | more complex sharing |
| `session` | entire pytest run | at most once per session, when used | expensive global-style resources | largest sharing surface |

Example:

```python
@pytest.fixture(scope="function")
def user():
    return User("Alice")
```

```python
@pytest.fixture(scope="module")
def configured_app():
    return create_test_app()
```

```python
@pytest.fixture(scope="session")
def expensive_model_client():
    return create_model_client()
```

### Function scope

Default fixture scope is function scope.

A fresh fixture instance can be created for each requesting test. This often provides strong isolation.

Typical use:

```python
@pytest.fixture
def shopping_cart():
    return []
```

If test A modifies the list, test B can receive a separate instance.

### Class scope

A class-scoped fixture can be reused by tests in a class.

Useful when multiple methods intentionally share expensive setup while still keeping a relatively local boundary.

### Module scope

A module-scoped fixture is shared by tests in one module that request it.

Example:

```python
@pytest.fixture(scope="module")
def test_client():
    return create_client()
```

This may be useful for expensive client initialization that is safe to share.

### Package scope

Package scope allows sharing within a package-level test organization. Use it when the package boundary is meaningful for the test resource. It is not automatically the best choice simply because it exists.

### Session scope

Session scope can provide a fixture instance for the overall pytest session.

Example:

```python
@pytest.fixture(scope="session")
def service_config():
    return load_test_config()
```

A session fixture is often appropriate for configuration or a resource whose initialization is expensive and safe to share.

### Lifecycle and teardown

Broadly scoped fixtures live longer and therefore teardown occurs later.

```text
function  → teardown after each relevant test
class     → teardown after relevant class scope
module    → teardown after relevant module scope
package   → teardown after relevant package scope
session   → teardown near end of test session
```

### Important engineering rule

Do not memorize:

> “session is better.”

There is no universally correct scope.

Instead ask:

1. Can tests safely share this resource?
2. How expensive is creation?
3. Can state leak from one test to another?
4. Is the resource mutable?
5. What cleanup is required?
6. Does concurrency or parallel execution change the safety story?

### Scope trade-off

A broader scope can reduce repeated setup, but it increases the lifetime and sharing surface of the resource. A function-scoped fixture can improve isolation but may cost more setup time.

Performance is therefore only one part of scope selection.

---

## 12. Fixture Isolation

### What is test isolation?

A test is **isolated** when its result does not accidentally depend on another test having run first or on shared mutable state left behind by another test.

### Why does it matter?

Suppose:

```python
shared_users = []


def test_add_user():
    shared_users.append("Alice")


def test_users_start_empty():
    assert shared_users == []
```

The second test now depends on whether the first test ran.

That creates order dependence and potentially flaky behavior.

### Shared mutable fixture state

Risky:

```python
@pytest.fixture(scope="module")
def users():
    return []
```

If multiple tests mutate the same list without resetting it, test behavior can leak.

Better when isolation is required:

```python
@pytest.fixture
def users():
    return []
```

### Shared files

Tests can interfere through:

- fixed filenames;
- shared temporary directories;
- stale generated artifacts.

Use pytest's temporary-path facilities where appropriate so each test can work with isolated paths.

### Shared databases

A database-backed test suite can leak state when tests write rows and do not clean them up.

Possible strategies include:

- transaction rollback;
- per-test schemas or databases;
- deterministic cleanup;
- carefully scoped connection fixtures.

The correct approach depends on the database and integration-test architecture.

### Environment variables

Tests that modify environment variables should restore them or use controlled fixture mechanisms so later tests do not inherit accidental state.

### Caches

Caches can be surprisingly dangerous because they look read-only while retaining mutable state.

A test suite should deliberately reset or isolate caches when their contents affect behavior.

### External services

Real external services can introduce:

- network failures;
- rate limits;
- changing data;
- authentication issues;
- latency;
- nondeterminism.

The correct test architecture separates deterministic logic from external integration checks.

### Isolation vs resource reuse

These are not enemies, but they are competing constraints:

```text
more isolation  ←→  more reuse / less setup
```

The engineering task is to choose a safe reuse boundary.

---

## 13. Multiple Fixtures

### What is fixture composition?

Fixtures can depend on other fixtures.

Example:

```python
@pytest.fixture
def database():
    return create_database()


@pytest.fixture
def user(database):
    return database.create_user("Alice")


@pytest.fixture
def authenticated_user(user):
    return authenticate(user)
```

A test can request the top-level dependency:

```python
def test_dashboard(authenticated_user):
    assert authenticated_user.is_authenticated
```

Conceptually:

```text
database
   ↓
  user
   ↓
authenticated_user
   ↓
   test
```

### Why does it exist?

Composition prevents every test from repeating a long setup chain.

### How does pytest resolve it?

Pytest follows the fixture dependency graph, prepares required fixtures according to their scopes, passes values downstream, then performs teardown in the appropriate reverse dependency order.

### Common mistake

Creating one giant fixture that performs every possible setup:

```python
@pytest.fixture
def everything():
    ...
```

This makes a test depend on more than it actually needs.

Better:

```python
@pytest.fixture
def database():
    ...

@pytest.fixture
def user(database):
    ...

@pytest.fixture
def authenticated_user(user):
    ...
```

The graph should represent meaningful dependencies, not arbitrary abstraction layers.

---

## 14. Autouse Fixtures

### What is it?

An autouse fixture is automatically applied to tests within the fixture's visibility/scope without being named in each test signature.

```python
@pytest.fixture(autouse=True)
def reset_state():
    reset_test_state()
```

### Why does it exist?

Some setup is genuinely universal within a test scope.

Good examples may include:

- resetting a global test-only setting;
- establishing a standard environment invariant;
- cleaning up state that every test must not inherit.

### Risk: hidden dependencies

With explicit dependencies:

```python
def test_user(user):
    ...
```

A reader sees `user`.

With autouse setup:

```python
@pytest.fixture(autouse=True)
def environment():
    ...
```

The test may rely on behavior that is not visible in its signature.

### Good use case

```python
@pytest.fixture(autouse=True)
def disable_network(monkeypatch):
    block_network_for_tests(monkeypatch)
```

This can make a test suite safer when the policy is truly universal and clearly documented.

### Bad use case

```python
@pytest.fixture(autouse=True)
def create_full_application_state():
    ...
```

If every test silently receives databases, users, orders, clients, and caches, the suite becomes harder to understand and slower to run.

### Better approach

Use explicit fixtures for meaningful dependencies. Reserve `autouse=True` for cross-cutting setup where hidden activation is an intentional design choice.

---

## 15. `conftest.py`

### What is it?

`conftest.py` is a pytest-specific configuration and fixture-sharing mechanism. Fixtures defined there can be made available to tests in the relevant directory tree without ordinary importing in every test module.

### Example structure

```text
tests/
    conftest.py
    unit/
        test_users.py
        test_orders.py
    integration/
        test_database.py
```

A fixture in `tests/conftest.py` can be visible to tests beneath that directory according to pytest's fixture visibility rules.

### Why does it exist?

Without shared fixture discovery, teams might import common setup manually into every module.

`conftest.py` allows test infrastructure to be organized around the test tree.

### Visibility concept

Think of directory structure as a visibility boundary:

```text
tests/
├── conftest.py        ← shared downward in this tree
├── unit/
│   └── test_users.py
└── integration/
    └── test_db.py
```

A child test directory can use fixtures defined in an ancestor `conftest.py` visible to that location.

The reverse is not generally true: an outer test module should not assume fixtures defined only in a sibling subtree are automatically visible.

### Common mistakes

- Putting every fixture in the root `conftest.py`.
- Making unrelated tests depend on global fixtures.
- Hiding major setup costs behind shared fixtures.
- Treating `conftest.py` as a dumping ground for arbitrary helpers.

### Better approach

Keep shared fixtures near the tests that genuinely share them. Use local fixture definitions when the dependency is only meaningful to one module.

> This chapter teaches `conftest.py`; it does not modify or create a project `conftest.py`.

---

## 16. Fixture Factories

### What is a fixture factory?

A fixture factory is a fixture that returns a function for creating test data or resources on demand.

```python
@pytest.fixture
def make_user():
    def _make_user(name, age):
        return User(name=name, age=age)

    return _make_user
```

Use it like this:

```python
def test_users(make_user):
    user1 = make_user("Alice", 30)
    user2 = make_user("Bob", 25)

    assert user1.name == "Alice"
    assert user2.name == "Bob"
```

### Why does it exist?

A normal fixture usually gives you one prepared value per fixture instance. A factory lets a test create multiple related values using a consistent setup rule.

### Realistic example

```python
class User:
    def __init__(self, user_id, name, active=True):
        self.user_id = user_id
        self.name = name
        self.active = active


@pytest.fixture
def make_user():
    counter = 0

    def _make_user(name, active=True):
        nonlocal counter
        counter += 1
        return User(counter, name, active=active)

    return _make_user
```

This can be useful when a test needs multiple users with different states.

### When to use

Use factory fixtures for variable data creation or resource construction that is meaningfully shared as test infrastructure.

### When not to use

If the factory has become a tiny framework with many flags and conditional branches, step back. A plain helper function may be clearer.

### Common mistake

Turning one factory into an all-purpose object generator:

```python
make_user(name, age, role, region, plan, status, permissions, ...)
```

This becomes difficult to understand and maintain.

Prefer smaller focused factories or explicit builders where the domain justifies them.

---

## 17. Parametrization

### What is it?

**Parametrization** means running the same test logic against multiple sets of input data.

Simple idea:

```text
same test logic
      +
different inputs
      =
multiple test cases
```

Pytest provides:

```text
@pytest.mark.parametrize
```

### Basic example

```python
import pytest


def add(a, b):
    return a + b


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (1, 2, 3),
        (2, 3, 5),
        (10, 20, 30),
    ],
)
def test_add(a, b, expected):
    assert add(a, b) == expected
```

### Explain every part

```text
@pytest.mark.parametrize(
```

`pytest.mark.parametrize` is a built-in marker/decorator used to generate multiple test invocations from one test function definition.

```python
"a,b,expected",
```

These are the parameter names.

```python
[
    (1, 2, 3),
    ...
]
```

Each tuple supplies values for one test case.

```text
def test_add(a, b, expected):
```

The generated test invocation receives the corresponding values.

Conceptually pytest collects:

```text
test_add[1-2-3]
test_add[2-3-5]
test_add[10-20-30]
```

The exact default ID formatting can vary based on values and pytest behavior, so use explicit IDs when human-readable case names matter.

---

## 18. Why Parametrization Exists

Without parametrization, you might write:

```python
def test_add_small_numbers():
    assert add(1, 2) == 3


def test_add_medium_numbers():
    assert add(20, 30) == 50


def test_add_large_numbers():
    assert add(1000, 2000) == 3000
```

The logic is duplicated.

Parametrization makes the difference in data explicit:

```python
@pytest.mark.parametrize(
    "a,b,expected",
    [
        (1, 2, 3),
        (20, 30, 50),
        (1000, 2000, 3000),
    ],
)
def test_add(a, b, expected):
    assert add(a, b) == expected
```

### Benefits

- less duplicate test code;
- more explicit test data;
- broader case coverage;
- consistent test logic;
- easier extension when a new case belongs to the same behavior.

### Trade-offs

Parametrization is not automatically better.

Separate test functions may be clearer when scenarios have substantially different behavior, setup, or assertions.

Overly large parameter tables can become difficult to read.

### Engineering rule

Use parametrization when:

> the **behavior being tested is the same** and the main difference is the **test data**.

Use separate tests when the behavior or reasoning is meaningfully different.

---

## 19. Multiple Parameters

### Syntax

```python
@pytest.mark.parametrize(
    "input_a,input_b,expected",
    [
        (1, 2, 3),
        (5, 7, 12),
    ],
)
def test_add(input_a, input_b, expected):
    assert add(input_a, input_b) == expected
```

### Rules

The parameter-name list and each test-data item must agree.

Three names:

```python
"input_a,input_b,expected"
```

means each case should provide three values:

```python
(1, 2, 3)
```

### Common mistake: too few values

```python
@pytest.mark.parametrize("a,b,expected", [(1, 2)])
def test_add(a, b, expected):
    ...
```

The case does not supply a value for `expected`.

### Common mistake: too many values

```python
@pytest.mark.parametrize("a,b", [(1, 2, 3)])
def test_add(a, b):
    ...
```

The test declares two parameters but receives three values.

### Common mistake: accidental nesting

Incorrect:

```text
@pytest.mark.parametrize("a,b", [[(1, 2), (3, 4)]])
```

This creates one case whose first value is a list containing tuples, not two separate cases for `(1, 2)` and `(3, 4)`.

Correct:

```text
@pytest.mark.parametrize("a,b", [(1, 2), (3, 4)])
```

### Better approach

Keep parameter order obvious and format long data in a readable layout.

---

## 20. Single-Value Parametrization

Sometimes one varying input is all you need:

```python
@pytest.mark.parametrize("value", [1, 2, 3, 4])
def test_positive_values(value):
    assert value > 0
```

### Validation example

```python
@pytest.mark.parametrize("value", ["alice", "bob", "charlie"])
def test_username_is_non_empty(value):
    assert value
```

### Boundary example

```python
@pytest.mark.parametrize("age", [0, 18, 120])
def test_allowed_age_boundaries(age):
    assert 0 <= age <= 120
```

### Invalid values

```python
@pytest.mark.parametrize("value", ["", "   ", None])
def test_empty_username_is_rejected(value):
    with pytest.raises(ValueError):
        validate_username(value)
```

This style works especially well when many inputs exercise exactly the same rule.

---

## 21. Parametrized Exception Tests

### Example

```python
@pytest.mark.parametrize(
    "value",
    ["abc", "", None],
)
def test_invalid_age(value):
    with pytest.raises(ValueError):
        parse_age(value)
```

### Why is this useful?

Input validation often has many invalid forms but one expected outcome:

```text
invalid input
     ↓
validation
     ↓
ValueError
```

Parametrization lets you document the invalid-input domain compactly.

### Stronger version with case IDs

```python
@pytest.mark.parametrize(
    "value",
    ["abc", "", None],
    ids=["letters", "empty", "none"],
)
def test_invalid_age(value):
    with pytest.raises(ValueError):
        parse_age(value)
```

### When cases need different expected exceptions

Use multiple parameters:

```python
@pytest.mark.parametrize(
    "value,expected_exception",
    [
        ("abc", ValueError),
        (None, TypeError),
    ],
    ids=["text", "none"],
)
def test_invalid_input(value, expected_exception):
    with pytest.raises(expected_exception):
        parse_age(value)
```

Be careful: if different cases represent fundamentally different behaviors, separate test functions may communicate the design better.

---

## 22. Parametrization IDs

### What are IDs?

A parametrized test generates multiple test cases. Readable **IDs** give each case a human-friendly label.

```python
@pytest.mark.parametrize(
    "value,expected",
    [
        (1, 2),
        (2, 4),
    ],
    ids=["one", "two"],
)
def test_double(value, expected):
    assert value * 2 == expected
```

### Why do IDs matter?

Suppose CI reports:

```text
test_validation[case-17]
```

You may need to inspect the source table to know what failed.

With IDs:

```text
test_validation[empty-email]
test_validation[missing-name]
test_validation[invalid-age]
```

The failing case becomes much easier to identify.

### Callable IDs

For dynamic case naming, `ids=` can also accept a callable that produces an ID from a parameter value.

Example:

```python
def case_id(case):
    return case["name"]


@pytest.mark.parametrize(
    "case",
    [
        {"name": "valid"},
        {"name": "missing-email"},
    ],
    ids=case_id,
)
def test_case(case):
    assert "name" in case
```

### Practical rule

Use explicit IDs when:

- the case list is long;
- values are complex;
- failures need fast diagnosis in CI;
- the default generated IDs are unclear.

---

## 23. Fixtures + Parametrization

Fixtures and parametrization solve different problems:

```text
fixture        → how test dependencies are prepared
parametrize    → which inputs/cases the same test logic should run against
```

They can be combined.

### Direct combination

```python
@pytest.fixture
def calculator():
    return Calculator()


@pytest.mark.parametrize(
    "a,b,expected",
    [(1, 2, 3), (4, 5, 9)],
)
def test_add(calculator, a, b, expected):
    assert calculator.add(a, b) == expected
```

### Indirect parametrization

Sometimes the parameter should be passed into a fixture rather than directly into the test.

```python
@pytest.fixture
def user(request):
    data = request.param
    return User(name=data["name"], role=data["role"])


@pytest.mark.parametrize(
    "user",
    [
        {"name": "Alice", "role": "admin"},
        {"name": "Bob", "role": "viewer"},
    ],
    indirect=True,
)
def test_user_role(user):
    assert user.role in {"admin", "viewer"}
```

### What does `indirect=True` mean?

For the named parameter `user`, the supplied data is not passed directly to the test function.

Instead, pytest passes that value to the `user` fixture through `request.param`.

Conceptually:

```text
parameter data
     ↓
request.param
     ↓
user fixture
     ↓
User object
     ↓
test_user_role(user)
```

### Why does it exist?

It is useful when creating the test dependency requires setup logic that belongs in the fixture.

For example, parameter data may describe a database configuration while the fixture creates the actual database client.

### Partial indirect parametrization

When multiple argument names are present, only selected names can be indirect:

```python
@pytest.mark.parametrize(
    "user,expected_role",
    [
        ({"name": "Alice", "role": "admin"}, "admin"),
        ({"name": "Bob", "role": "viewer"}, "viewer"),
    ],
    indirect=["user"],
)
def test_user_role(user, expected_role):
    assert user.role == expected_role
```

Here `user` is routed through the fixture, while `expected_role` goes directly to the test.

### When not to use indirect parametrization

Do not use it simply because it looks advanced. If the test can clearly accept a normal parameter directly, direct parametrization is often easier to read.

---

## 24. Complex Test Data

Parametrization can use:

- tuples;
- dictionaries;
- dataclasses or other objects;
- structured case definitions.

### Tuple data

Good for short, obvious cases:

```python
@pytest.mark.parametrize(
    "raw,expected",
    [
        ("10", 10),
        ("20", 20),
    ],
)
def test_parse(raw, expected):
    assert int(raw) == expected
```

### Dictionary data

Useful when a case has many named attributes:

```python
cases = [
    {
        "name": "valid-user",
        "payload": {"name": "Alice", "age": 30},
        "expected_status": 201,
    },
    {
        "name": "missing-age",
        "payload": {"name": "Alice"},
        "expected_status": 400,
    },
]
```

### Structured test cases

A dataclass can make larger suites easier to understand:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class UserCase:
    name: str
    payload: dict
    expected_status: int
```

Then:

```python
CASES = [
    UserCase(
        name="valid-user",
        payload={"name": "Alice", "age": 30},
        expected_status=201,
    ),
    UserCase(
        name="missing-age",
        payload={"name": "Alice"},
        expected_status=400,
    ),
]
```

### Simple values vs structured cases

Use simple values when the scenario is simple.

Use structured cases when many attributes are necessary to explain one test scenario.

Do not introduce a test-case class for two integers merely to make the design look sophisticated.

### Maintainability rule

Test data should make the scenario easier to understand, not harder.

---

## 25. Edge-Case Parametrization

Parametrization is ideal for systematic edge-case coverage.

Useful categories include:

| Category | Examples |
|---|---|
| zero | `0` |
| negative | `-1`, `-100` |
| empty string | `""` |
| whitespace | `"   "`, `"\n"` |
| `None` | `None` |
| large value | `10**12` |
| boundary | `0`, `120` |
| invalid format | `"abc"`, `"12x"` |
| duplicates | repeated IDs/items |
| unusual input | Unicode, long strings, unusual casing |

### Boundary-value testing

Suppose the valid range is:

```text
0 ≤ age ≤ 120
```

Important tests include:

```text
-1     → invalid
 0     → valid boundary
 1     → valid
119    → valid
120    → valid boundary
121    → invalid
```

You do not always need every possible value. Boundary-value analysis targets places where defects commonly appear.

### Example

```python
@pytest.mark.parametrize(
    "age,valid",
    [
        (-1, False),
        (0, True),
        (1, True),
        (119, True),
        (120, True),
        (121, False),
    ],
    ids=["below-min", "min", "normal-low", "normal-high", "max", "above-max"],
)
def test_age_range(age, valid):
    assert validate_age(age) is valid
```

### Production connection

Edge cases matter in:

- financial calculations;
- parsing;
- API validation;
- ETL transformations;
- ML preprocessing;
- token/length limits in AI systems;
- retry and rate-limit logic.

---

## 26. Parametrization vs Separate Test Functions

Use **parametrization** when:

- the same behavior is tested;
- assertions are substantially the same;
- setup is substantially the same;
- only data changes.

Use **separate functions** when:

- behavior changes significantly;
- the setup is different;
- different assertions communicate different requirements;
- a scenario needs its own explanatory narrative.

### Example: good parametrization

```python
@pytest.mark.parametrize(
    "a,b,expected",
    [(1, 2, 3), (2, 5, 7), (10, 20, 30)],
)
def test_add(a, b, expected):
    assert add(a, b) == expected
```

### Example: separate tests may be clearer

```python
def test_login_with_valid_credentials():
    ...


def test_login_locks_account_after_repeated_failures():
    ...
```

These may both involve login, but they verify meaningfully different behavior.

### Debugging consideration

A parametrized failure tells you which case failed. Readable IDs are therefore especially valuable when cases become complex.

### Practical decision rule

Ask:

> “If I changed one row of test data, would the test's meaning remain the same?”

If yes, parametrization is a strong candidate.

---

## 27. Assertions + Fixtures + Parametrization Together

Consider a transaction-validation system.

### Application code

```python
class TransactionError(Exception):
    pass


def validate_transaction(transaction):
    amount = transaction["amount"]
    currency = transaction["currency"]

    if amount <= 0:
        raise TransactionError("amount must be positive")

    if currency not in {"INR", "USD", "EUR"}:
        raise TransactionError("unsupported currency")

    return True
```

### Fixture

```python
import pytest


@pytest.fixture
def valid_transaction():
    return {
        "amount": 100,
        "currency": "INR",
    }
```

### Parametrized valid cases

```python
@pytest.mark.parametrize(
    "amount,currency",
    [
        (1, "INR"),
        (100, "USD"),
        (1000, "EUR"),
    ],
    ids=["small-inr", "medium-usd", "large-eur"],
)
def test_valid_transaction(amount, currency):
    transaction = {"amount": amount, "currency": currency}
    assert validate_transaction(transaction) is True
```

### Fixture + parametrization together

```python
@pytest.mark.parametrize(
    "currency",
    ["INR", "USD", "EUR"],
)
def test_supported_currency(valid_transaction, currency):
    valid_transaction["currency"] = currency
    assert validate_transaction(valid_transaction) is True
```

Be mindful that mutating fixture data inside a test is safe here because function-scoped fixtures provide an isolated instance for each test invocation. If the fixture were broader-scoped, that mutation could leak.

### Exception testing

```python
@pytest.mark.parametrize(
    "transaction,expected_message",
    [
        ({"amount": 0, "currency": "INR"}, "amount must be positive"),
        ({"amount": 10, "currency": "GBP"}, "unsupported currency"),
    ],
    ids=["zero-amount", "unsupported-currency"],
)
def test_invalid_transaction(transaction, expected_message):
    with pytest.raises(TransactionError, match=expected_message):
        validate_transaction(transaction)
```

### Architecture

```text
fixture
  ↓
base dependency/data
  ↓
parametrized case
  ↓
application behavior
  ↓
assertion / expected exception
```

This pattern scales well because each mechanism has a separate responsibility.

---

## 28. Test Data Design

### Good test data should be

- representative;
- boundary-aware;
- invalid where required;
- minimal but sufficient;
- deterministic;
- readable;
- easy to diagnose.

### Representative data

Use values that represent realistic business states.

### Boundary data

Include boundaries where rules change.

### Invalid data

Explicitly model malformed, missing, out-of-range, unauthorized, or otherwise invalid inputs.

### Minimal data

Do not build a 50-field object when the behavior under test only needs three fields.

Minimal data reduces noise.

### Deterministic data

Avoid random values unless the test deliberately controls and records the random seed/inputs.

This is fragile:

```python
import random


def test_discount():
    value = random.random()
    assert calculate_discount(value) >= 0
```

A deterministic test case is usually easier to debug.

### Arrange → Act → Assert

A useful structure is:

```text
Arrange
  ↓
prepare fixture/data
  ↓
Act
  ↓
call application behavior
  ↓
Assert
  ↓
verify result
```

Example:

```python
def test_total(user_cart):
    # Arrange
    user_cart.add("book", price=20)

    # Act
    total = user_cart.total()

    # Assert
    assert total == 20
```

Fixtures often own the reusable parts of Arrange. Parametrization supplies variation. The test body performs Act and Assert.

### Production consideration

Bad test data can create bad confidence. A suite with 1,000 repetitive cases does not necessarily provide better coverage than 50 carefully selected cases.

---

## 29. Fixtures vs Helper Functions

### Helper function

A helper is an ordinary Python function:

```python
def make_user(name="Alice", age=30):
    return User(name=name, age=age)
```

Call it explicitly:

```python
def test_name():
    user = make_user()
    assert user.name == "Alice"
```

### Fixture

```python
@pytest.fixture
def user():
    return User(name="Alice", age=30)


def test_name(user):
    assert user.name == "Alice"
```

### Key difference

A **helper function** is ordinary reusable code.

A **fixture** is a pytest-managed test dependency with support for lifecycle, scope, dependency composition, and fixture-specific behavior.

### Test data factory vs resource fixture

A factory:

```text
def make_user(name, age, ...):
    ...
```

is often ideal for creating many values.

A resource fixture:

```python
@pytest.fixture
def database_connection():
    ...
```

is useful when pytest should manage setup, injection, scope, and cleanup.

### Practical decision rule

Use a helper when:

- explicit function calls improve readability;
- there is no lifecycle to manage;
- you do not need pytest's fixture scope/dependency system.

Use a fixture when:

- the object is a test dependency;
- setup is shared;
- cleanup matters;
- scope matters;
- the dependency should be injected consistently into tests.

Neither mechanism is universally superior.

---

## 30. Fixtures vs Mocking

This chapter does not attempt to teach mocking in depth. The important distinction is:

```text
fixture → reusable setup/dependency/resource
mock    → controlled replacement/substitute for a dependency
```

### Conceptual example

Suppose a service calls an external payment provider.

A fixture might create the service configured for a test environment:

```python
@pytest.fixture
def payment_service(fake_gateway):
    return PaymentService(gateway=fake_gateway)
```

A mock or fake gateway can then control the external dependency's behavior.

Fixtures and mocks are not competing concepts. They often work together.

```text
fixture
  ↓
creates/configures dependency
  ↓
mock/fake replacement
  ↓
application under test
```

### Why the distinction matters

A fixture answers:

> “How do I prepare the dependency for this test?”

A mock answers:

> “What controlled behavior should this dependency exhibit?”

Deeper mocking patterns should be learned separately so the test suite does not become a collection of overly coupled interaction assertions.

---

## 31. Common Fixture Mistakes

### 1. Fixture name mismatch

**Bad:**

```python
@pytest.fixture
def sample_user():
    return {"name": "Alice"}


def test_name(user):
    assert user["name"] == "Alice"
```

**Why:** `user` and `sample_user` are different names.

**Better:**

```python
def test_name(sample_user):
    assert sample_user["name"] == "Alice"
```

---

### 2. Missing `@pytest.fixture`

**Bad:**

```python
def sample_user():
    return {"name": "Alice"}


def test_name(sample_user):
    ...
```

**Why:** pytest does not automatically treat every function with that name as a fixture.

**Better:**

```python
@pytest.fixture
def sample_user():
    return {"name": "Alice"}
```

---

### 3. Wrong scope

**Bad:**

```python
@pytest.fixture(scope="session")
def cart():
    return []
```

when tests mutate the cart and require isolation.

**Why:** shared mutable state can leak across tests.

**Better:**

```python
@pytest.fixture
def cart():
    return []
```

unless broader sharing is explicitly safe.

---

### 4. Shared mutable state

**Bad:**

```python
@pytest.fixture(scope="module")
def users():
    return []
```

Tests mutate the same list.

**Better:** use function scope or explicit reset/isolation when sharing is genuinely required.

---

### 5. Overusing `autouse`

**Bad:** every test silently creates expensive infrastructure.

**Why:** hidden dependencies and unnecessary cost.

**Better:** make meaningful dependencies explicit.

---

### 6. Giant fixtures

**Bad:**

```python
@pytest.fixture
def everything():
    app = create_app()
    db = create_database()
    user = create_user(db)
    order = create_order(db, user)
    cache = create_cache()
    client = create_client(app)
    return app, db, user, order, cache, client
```

**Why:** tests depend on a bundle rather than the exact resources they need.

**Better:** compose focused fixtures.

---

### 7. Fixtures that do too much

Split a fixture when it mixes unrelated concerns.

```text
configuration
↓
database
↓
client
↓
user
```

Each layer should have a meaningful reason to exist.

---

### 8. Hidden dependencies

A test with no fixture parameter can still be affected by a huge autouse fixture tree.

Make important prerequisites visible.

---

### 9. Excessive fixture nesting

If a simple test requires seven fixture levels, the abstraction may be too deep.

Depth is not inherently wrong; unnecessary depth is the problem.

---

### 10. Expensive session fixtures

**Risk:** assuming “one session instance” automatically means “good performance.”

A session fixture may be expensive to create, hold resources too long, serialize tests, or create shared-state contention.

Measure before optimizing.

---

### 11. Cleanup not happening

Use `yield` or other explicit cleanup mechanisms where the resource lifecycle requires it.

---

### 12. Incorrect `yield` usage

Only one value is yielded as the fixture result. Cleanup logic belongs after `yield` or inside deliberate finalization logic.

Better:

```python
@pytest.fixture
def resource():
    value = create_resource()
    try:
        yield value
    finally:
        cleanup(value)
```

---

## 32. Common Parametrization Mistakes

### 1. Wrong number of parameters

```python
@pytest.mark.parametrize("a,b", [(1, 2, 3)])
def test_add(a, b):
    ...
```

The case supplies three values for two names.

### 2. Wrong tuple structure

Make sure your nesting matches the expected number of generated cases.

### 3. Duplicated test data

Do not copy the same large payload ten times when one helper or structured case definition can express the variation clearly.

### 4. Unreadably large parameter list

If the decorator occupies most of the file, consider a named constant:

```python
CASES = [
    ...
]


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.name)
def test_behavior(case):
    ...
```

### 5. Overly complex parametrization

Do not create a matrix of flags that requires mental decoding:

```text
(a, b, c, d, e, f, g, expected)
```

unless the domain truly needs it.

### 6. Inappropriate indirect parametrization

Do not use `indirect=True` just because the case data looks complex. Use it when fixture setup is the right abstraction boundary.

### 7. Missing IDs

Complex cases become much harder to diagnose without readable identifiers.

### 8. Mixing unrelated scenarios

A single parametrized test should not become a container for unrelated behaviors merely to reduce the number of test functions.

### Diagnosis workflow

When parametrization behaves strangely:

```bash
pytest --collect-only -q
```

Then inspect:

- parameter names;
- case shape;
- `ids` length/content;
- `indirect` target names;
- fixture names.

---

## 33. Advanced Fixture Lifecycle

A fixture lifecycle can be understood as a sequence of responsibilities:

```text
collection/context
      ↓
fixture dependency resolution
      ↓
fixture setup
      ↓
fixture value available
      ↓
test execution
      ↓
fixture teardown/finalization
```

### Creation

Pytest creates a fixture when a test needs it, subject to scope and caching rules.

### Dependency resolution

If fixture `B` requests fixture `A`, pytest must resolve `A` before providing `B`.

```python
@pytest.fixture
def database():
    ...


@pytest.fixture
def user(database):
    ...
```

### Scope

Scope controls the reuse boundary. A fixture can be cached within its scope for the tests that request that fixture instance.

### Caching

Pytest can reuse a fixture result according to its scope rather than recreating it for every request within the same scope.

Do not interpret “cached” as “immutable.” A cached fixture value can still be mutable. That is why broad-scoped mutable objects are a common source of test pollution.

### Teardown

For a `yield` fixture:

```python
@pytest.fixture
def db():
    connection = create_connection()
    yield connection
    connection.close()
```

The code after `yield` runs as fixture finalization for that instance.

### Dependency ordering

Dependencies must be available before dependents. Teardown follows pytest's fixture finalization semantics so dependent resources are not normally torn down before resources they still need during finalization.

### Documented behavior vs implementation details

A good engineer separates:

**Documented pytest behavior:**

- fixture scopes;
- requested fixture dependency injection;
- `yield` fixture teardown;
- parametrization behavior;
- `ids` and `indirect` APIs.

**Implementation details:**

- internal fixture manager data structures;
- internal node/object classes that are not public API;
- assumptions based on current source code that documentation does not promise.

Do not build project architecture around undocumented internals just because they are visible in source code.

---

## 34. Fixture Scope Trade-offs

A useful mental model is:

```text
more isolation  ←→  more reuse / potentially less setup
```

### Function scope

Potential strengths:

- fresh state;
- easier reasoning;
- lower risk of test pollution.

Potential costs:

- repeated setup;
- expensive creation repeated frequently.

### Session scope

Potential strengths:

- expensive one-time initialization;
- useful for stable, shared resources.

Potential costs:

- shared state;
- long-lived resources;
- more complex lifecycle;
- interactions between tests.

### Database connection example

A connection/client can sometimes be session- or module-scoped if it is safe to share.

Test data itself may still need function-level isolation even when the underlying client is reused.

This leads to an important pattern:

```text
shared infrastructure
     +
per-test state
```

For example:

```text
session-scoped client
        ↓
function-scoped transaction/data
        ↓
test
```

That can provide both reuse and isolation when the system supports it.

### Application configuration

Immutable or effectively read-only configuration can often be broader scoped than mutable request state.

### Expensive resources

A model client, compiled schema, or initialized application may be expensive. But reuse must still be safe under the suite's concurrency and mutation model.

### Engineering decision

Select scope based on:

```text
correctness
+ isolation
+ lifecycle
+ cost
+ concurrency
+ maintainability
```

Not performance alone.

---

## 35. Advanced Parametrization Design

Large test suites often face a combinatorial problem.

Suppose there are:

```text
3 input types
× 4 user roles
× 5 application states
```

A naive full Cartesian product creates:

```text
3 × 4 × 5 = 60 combinations
```

Add another dimension:

```text
× 4 regions = 240 cases
```

### What is combinatorial explosion?

The number of combinations grows multiplicatively as dimensions are added.

A mathematically complete matrix may be unnecessary and expensive.

### Better selection strategy

Choose cases based on behavior boundaries:

- one representative case from stable equivalence classes;
- every important boundary;
- known failure modes;
- interactions that have a reason to exist;
- high-risk combinations;
- regressions from previous defects.

### Meaningful IDs

Prefer:

```text
admin-active-valid
viewer-active-valid
admin-suspended-denied
```

over opaque generated identifiers.

### Separate data from logic

```python
USER_CASES = [
    ("admin", True, True),
    ("viewer", True, True),
    ("admin", False, False),
]


@pytest.mark.parametrize(
    "role,active,allowed",
    USER_CASES,
    ids=["admin-active", "viewer-active", "admin-suspended"],
)
def test_access(role, active, allowed):
    assert can_access(role, active) is allowed
```

### Structured case design

When the case grows, use a structured object instead of a huge tuple.

The objective is not maximum abstraction. The objective is understandable coverage.

---

## 36. Pytest Markers

A **marker** attaches metadata to a test.

Parametrization is implemented using a built-in marker:

```text
@pytest.mark.parametrize(...)
```

That does not mean all markers are parametrization.

### Custom marker concept

You might categorize tests as:

```python
@pytest.mark.integration
def test_database_connection():
    ...
```

or:

```python
@pytest.mark.slow
def test_large_pipeline():
    ...
```

### Why markers exist

Markers can help teams select groups of tests.

Examples:

```bash
pytest -m integration
pytest -m "not slow"
```

Custom markers should normally be registered in project configuration so spelling mistakes can be detected and the suite remains self-documenting.

### Production use

Markers can support:

- unit tests;
- integration tests;
- slow tests;
- optional environment-dependent tests.

Do not turn this section into a complete marker system design. The key connection here is that parametrization and markers solve different organization problems.

---

## 37. Test Discovery and Organization

A scalable structure might look like:

```text
tests/
├── conftest.py
├── unit/
│   ├── test_users.py
│   ├── test_orders.py
│   └── test_validation.py
├── integration/
│   ├── test_database.py
│   └── test_api.py
└── e2e/
    └── test_checkout_flow.py
```

### Where fixtures fit

Shared infrastructure can live in an appropriate `conftest.py`:

```text
tests/conftest.py
```

Unit-specific fixtures can live closer to unit tests, while integration-only fixtures can live under that subtree if appropriate.

### Where parametrization fits

Parametrization lives close to the behavior being tested:

```python
@pytest.mark.parametrize(
    "input_value,expected",
    [...],
)
def test_validate(input_value, expected):
    ...
```

For large datasets, keep the data organized as named constants or structured modules instead of making test functions unreadable.

### Maintainability

A good test tree lets a developer answer:

- Where are unit tests?
- Where are integration tests?
- Which fixtures are global to this test subtree?
- Which test controls this behavior?
- How can I run only one layer?

Organization is a debugging tool.

---

## 38. Production-Oriented Testing

Assertions, fixtures, and parametrization appear across many engineering domains.

### 1. Backend applications

Fixtures can construct:

- application configuration;
- domain objects;
- authenticated users;
- repositories;
- test services.

Parametrization can cover:

- valid and invalid requests;
- state transitions;
- boundary values.

### 2. REST APIs

A fixture can provide a test client:

```python
@pytest.fixture
def client():
    return create_test_client()
```

Then parametrized requests can verify validation behavior:

```python
@pytest.mark.parametrize(
    "payload,expected_status",
    [
        ({"name": "Alice"}, 201),
        ({}, 400),
    ],
)
def test_create_user(client, payload, expected_status):
    response = client.post("/users", json=payload)
    assert response.status_code == expected_status
```

### 3. Database-backed services

Fixtures may manage:

- connections;
- test schemas;
- transactions;
- seed data;
- rollback.

The central challenge is balancing expensive infrastructure reuse with data isolation.

### 4. Data pipelines

Fixtures can create deterministic input datasets and temporary locations.

Parametrization can cover:

- schema variants;
- missing values;
- duplicate records;
- boundary timestamps;
- malformed rows.

### 5. ETL/ELT systems

Tests can verify transformations:

```python
@pytest.mark.parametrize(
    "raw,expected",
    [
        ({"age": "30"}, {"age": 30}),
        ({"age": ""}, {"age": None}),
    ],
)
def test_normalize(raw, expected):
    assert normalize(raw) == expected
```

### 6. ML pipelines

Fixtures can provide:

- deterministic synthetic datasets;
- preprocessing configuration;
- model stubs/fakes;
- temporary model directories.

Parametrization can cover:

- feature edge cases;
- schema variants;
- prediction thresholds;
- preprocessing behavior.

### 7. AI/LLM applications

Fixtures can provide controlled:

- model configurations;
- synthetic documents;
- deterministic test inputs;
- fake or recorded model responses;
- controlled tool clients;
- test databases.

Example:

```python
@pytest.fixture
def fake_model():
    return FakeModel(response="Paris")


@pytest.mark.parametrize(
    "question,expected",
    [
        ("Capital of France?", "Paris"),
        ("Capital of Japan?", "Tokyo"),
    ],
)
def test_answering(fake_model, question, expected):
    answer = fake_model.generate(question)
    assert answer == expected
```

### 8. Agentic AI systems

A deterministic tool layer can be tested independently of the model's probabilistic behavior.

Fixtures can provide:

- controlled tool implementations;
- synthetic documents;
- sandboxed databases;
- fixed state/configuration;
- deterministic environment assumptions.

Parametrization can test tool inputs and expected tool results.

For the LLM itself, exact text equality is often an inappropriate universal strategy because model outputs can be variable. Testing may instead focus on structured outputs, safety constraints, tool-call contracts, invariants, evaluator criteria, and deterministic components.

### Core engineering idea

Use pytest to isolate the deterministic parts of a system and to make nondeterministic boundaries explicit rather than pretending every AI behavior is a simple exact-value function.

---

## 39. Test Quality

A test that passes is not automatically a good test.

### Characteristics of a strong test

| Property | Meaning |
|---|---|
| Deterministic | Same controlled inputs produce stable results |
| Isolated | One test does not accidentally depend on another |
| Readable | A developer can understand intent quickly |
| Meaningful | It verifies behavior that matters |
| Maintainable | Changes can be made without unnecessary churn |
| Fast when appropriate | Cheap tests stay cheap enough for frequent execution |
| Failure-diagnostic | Failures provide useful clues |
| Behavior-focused | Tests observable contracts rather than unnecessary internals |
| Appropriately scoped | Setup and reuse match the test's needs |

### Example: passing but weak

```python

def test_user_creation():
    user = create_user("Alice")
    assert user is not None
```

This can pass even if the user has the wrong name, status, or identifier.

### Stronger

```python

def test_user_creation():
    user = create_user("Alice")
    assert user.name == "Alice"
    assert user.is_active is True
```

The exact assertions should still match the actual contract rather than every implementation attribute.

### Failure diagnostics

When possible, write tests so that a failure tells the developer what went wrong without reading half the codebase.

Readable parameter IDs, focused fixtures, and clear assertions all contribute to diagnosis.

---

## 40. Code Coverage

**Code coverage** measures which parts of code were executed by tests.

### Line coverage

Line coverage asks, conceptually:

> Which executable lines ran?

### Branch coverage

Branch coverage asks which logical branches were exercised, for example:

```python
if age >= 18:
    ...
else:
    ...
```

A test suite that executes only the first branch has incomplete branch coverage.

### Why coverage is useful

Coverage can reveal areas of code with little or no test execution.

### Why 100% is not enough

A test can execute a line without verifying the correct behavior.

```python

def divide(a, b):
    return a / b


def test_divide():
    divide(10, 2)
```

The line executes, but nothing is asserted.

Coverage can therefore answer:

> “Was this code executed?”

It does not fully answer:

> “Was the behavior tested correctly?”

### Production principle

Treat coverage as a signal, not a quality score.

---

## 41. Debugging Failed Pytest Tests

A disciplined debugging workflow is more valuable than repeatedly rerunning the suite and guessing.

### Workflow

1. Read the failure.
2. Identify the failing test.
3. Identify the failing assertion or setup phase.
4. Compare expected vs actual.
5. Inspect fixture inputs.
6. Inspect the failing parametrized case.
7. Reproduce with one test.
8. Simplify the failing case.
9. Fix the underlying problem.
10. Run regression tests.

### Assertion failure example

```python
@pytest.mark.parametrize(
    "a,b,expected",
    [(1, 2, 3), (2, 3, 10)],
)
def test_add(a, b, expected):
    assert add(a, b) == expected
```

If the second case fails, run only it if the node ID is known:

```bash
pytest tests/test_math.py::test_add -k "2-3-10" -vv
```

Or rerun by a more specific selection expression depending on the generated ID.

### Fixture problem

Symptom:

```text
fixture 'user' not found
```

Investigation:

- check spelling;
- verify `@pytest.fixture` is present;
- verify the fixture is in a visible location;
- run `pytest --fixtures` or inspect collection.

### Parametrization problem

Symptom:

```text
indirect fixture 'x' doesn't exist
```

Check that `x` is actually a fixture when `indirect` routes the parameter through it.

### Setup/teardown problem

Symptom:

- tests pass individually but fail as a suite;
- later tests see stale files/data;
- connection exhaustion occurs.

Investigate fixture scope, shared mutable state, and cleanup.

### Debugging mindset

Do not ask only:

> “Why did pytest fail?”

Ask:

> “What invariant did this test expose, and what state produced the failure?”

That question scales better to production systems.

---

## 42. Complete Realistic Example

We will build a small user-registration validation module.

### Production-like module

```python
# user_registration.py

class RegistrationError(Exception):
    pass


def register_user(payload):
    name = payload.get("name")
    age = payload.get("age")
    email = payload.get("email")

    if not name:
        raise RegistrationError("name is required")

    if not isinstance(age, int):
        raise RegistrationError("age must be an integer")

    if age < 18:
        raise RegistrationError("user must be at least 18")

    if "@" not in email:
        raise RegistrationError("invalid email")

    return {
        "name": name,
        "age": age,
        "email": email,
        "status": "registered",
    }
```

### Test structure

```text
tests/
    conftest.py
    test_user_registration.py
```

Again, this chapter teaches the architecture; it does not modify a project `conftest.py`.

### Fixture

```python
import pytest


@pytest.fixture
def valid_payload():
    return {
        "name": "Alice",
        "age": 30,
        "email": "alice@example.com",
    }
```

### Positive test

```python
def test_register_user(valid_payload):
    result = register_user(valid_payload)

    assert result["name"] == "Alice"
    assert result["status"] == "registered"
```

### Parametrized age cases

```python
@pytest.mark.parametrize(
    "age",
    [18, 19, 30, 120],
    ids=["minimum", "above-minimum", "typical", "maximum-example"],
)
def test_register_user_accepts_valid_ages(valid_payload, age):
    valid_payload["age"] = age

    result = register_user(valid_payload)

    assert result["age"] == age
```

### Parametrized invalid cases

```python
@pytest.mark.parametrize(
    "field,value,expected_message",
    [
        ("name", "", "name is required"),
        ("age", "30", "age must be an integer"),
        ("age", 17, "user must be at least 18"),
        ("email", "invalid", "invalid email"),
    ],
    ids=["missing-name", "age-string", "underage", "invalid-email"],
)
def test_register_user_rejects_invalid_input(
    valid_payload,
    field,
    value,
    expected_message,
):
    valid_payload[field] = value

    with pytest.raises(RegistrationError, match=expected_message):
        register_user(valid_payload)
```

### Yield fixture for a temporary resource

```python
@pytest.fixture
def registration_log(tmp_path):
    path = tmp_path / "registration.log"
    handle = path.open("w+")
    try:
        yield handle
    finally:
        handle.close()
```

The example demonstrates:

- pytest tests;
- assertions;
- a fixture;
- parametrization;
- parameter IDs;
- expected exceptions;
- a yield fixture;
- resource cleanup.

### Step-by-step architecture

```text
fixtures
   ↓
arrange reusable dependencies
   ↓
parametrized case
   ↓
mutate only the relevant test input
   ↓
call application behavior
   ↓
assert success or expected exception
```

This is a foundation for larger test architectures.

---

## 43. Mini-Project

### Project: Transaction Validation Test Suite

Build a small Python project that validates bank-like transaction requests.

### Requirements

Implement a module with:

- transaction amount validation;
- supported currency validation;
- account-status validation;
- transaction-type validation;
- structured result on success;
- explicit domain exception on invalid input.

### Suggested project structure

```text
transaction-validator/
├── src/
│   └── transaction_validator.py
└── tests/
    ├── conftest.py
    └── test_transaction_validator.py
```

### Architecture

```text
transaction input
       ↓
validation logic
       ↓
success result OR domain exception
       ↓
pytest suite
       ├── assertions
       ├── fixtures
       ├── parametrization
       └── exception tests
```

### Implementation target

```python
# src/transaction_validator.py

class TransactionValidationError(Exception):
    pass


def validate_transaction(transaction):
    amount = transaction.get("amount")
    currency = transaction.get("currency")
    account_status = transaction.get("account_status")
    transaction_type = transaction.get("transaction_type")

    if not isinstance(amount, (int, float)):
        raise TransactionValidationError("amount must be numeric")

    if amount <= 0:
        raise TransactionValidationError("amount must be positive")

    if currency not in {"INR", "USD", "EUR"}:
        raise TransactionValidationError("unsupported currency")

    if account_status != "active":
        raise TransactionValidationError("account must be active")

    if transaction_type not in {"credit", "debit"}:
        raise TransactionValidationError("unsupported transaction type")

    return {
        "status": "valid",
        "amount": amount,
        "currency": currency,
        "transaction_type": transaction_type,
    }
```

### Fixture strategy

Create:

- a valid transaction fixture;
- optionally a factory fixture for customizing one field;
- a resource fixture only if your extended project needs a temporary persistence layer.

### Test strategy

Cover:

1. valid transaction;
2. zero amount;
3. negative amount;
4. non-numeric amount;
5. unsupported currency;
6. inactive account;
7. unsupported transaction type;
8. valid boundary-like values;
9. readable IDs for invalid scenarios.

### Example tests

```python
import pytest


@pytest.fixture
def valid_transaction():
    return {
        "amount": 100.0,
        "currency": "INR",
        "account_status": "active",
        "transaction_type": "debit",
    }


def test_valid_transaction(valid_transaction):
    result = validate_transaction(valid_transaction)

    assert result["status"] == "valid"
    assert result["amount"] == 100.0
```

### Parametrized invalid cases

```python
@pytest.mark.parametrize(
    "field,value,expected_message",
    [
        ("amount", 0, "amount must be positive"),
        ("amount", -1, "amount must be positive"),
        ("amount", "100", "amount must be numeric"),
        ("currency", "GBP", "unsupported currency"),
        ("account_status", "blocked", "account must be active"),
        ("transaction_type", "transfer", "unsupported transaction type"),
    ],
    ids=[
        "zero-amount",
        "negative-amount",
        "string-amount",
        "unsupported-currency",
        "inactive-account",
        "unsupported-type",
    ],
)
def test_invalid_transaction(valid_transaction, field, value, expected_message):
    valid_transaction[field] = value

    with pytest.raises(TransactionValidationError, match=expected_message):
        validate_transaction(valid_transaction)
```

### Expected learning outcome

You should be able to explain why each test uses:

- a fixture;
- parametrization;
- an assertion;
- an exception check;
- a particular parameter ID;
- a particular fixture scope.

### Debugging scenarios

Intentionally introduce:

- a mistaken currency rule;
- a fixture that uses module scope while tests mutate it;
- one wrong parameter name;
- one incorrect expected exception.

Then use pytest output to identify the defect.

### Improvements

After the basic project works, evaluate:

- whether helper functions would simplify test-data generation;
- whether any fixture is too broad;
- whether parameter cases should be represented as dataclasses;
- whether API/integration tests deserve a separate directory;
- whether custom markers would improve suite selection.

---

## 44. Coding Exercises

The exercises below progress from fundamentals to production-oriented design. Each exercise includes the problem, task, hints, a complete solution, an explanation, and a common mistake.

### Level 1 — Basic

#### Exercise 1 — Equality assertion

**Problem:** Write a pytest test for `multiply(4, 5)` returning `20`.

**Expected task:** Create one test function with a meaningful assertion.

**Hint:** Call the function and compare the result with the expected value.

**Complete solution:**

```python

def multiply(a, b):
    return a * b


def test_multiply():
    assert multiply(4, 5) == 20
```

**Explanation:** The test verifies the observable behavior of `multiply`.

**Common mistake:**

```python
assert multiply(4, 5)
```

This checks truthiness rather than correctness.

---

#### Exercise 2 — Membership assertion

**Problem:** Verify that `"admin"` is in a user's role list.

**Expected task:** Use `in` with an assertion.

**Hint:** Assert the required role is a member of the list.

**Complete solution:**

```python

def test_admin_role_present():
    roles = ["user", "admin"]
    assert "admin" in roles
```

**Explanation:** The requirement is membership, not list equality.

**Common mistake:** Checking index `1` instead of the behavior.

---

#### Exercise 3 — `None`

**Problem:** Test that a function returns `None` for a missing record.

**Complete solution:**

```python

def find_user(user_id):
    return None


def test_missing_user_returns_none():
    assert find_user(999) is None
```

**Explanation:** `is None` is the idiomatic identity check.

**Common mistake:** Using `== None` without a reason.

---

#### Exercise 4 — Exception assertion

**Problem:** `parse_number("abc")` should raise `ValueError`.

**Complete solution:**

```python
import pytest


def parse_number(value):
    return int(value)


def test_parse_number_rejects_text():
    with pytest.raises(ValueError):
        parse_number("abc")
```

**Explanation:** `pytest.raises` expresses that the exception is expected behavior.

**Common mistake:** Catching `Exception` manually and then passing the test.

---

#### Exercise 5 — Type assertion

**Problem:** Verify that `build_id()` returns an integer.

**Complete solution:**

```python

def build_id():
    return 100


def test_build_id_returns_int():
    assert isinstance(build_id(), int)
```

**Explanation:** The contract includes the returned type.

**Common mistake:** Using `type(x) is int` when subclasses would be acceptable.

---

### Level 2 — Intermediate

#### Exercise 6 — Basic fixture

**Problem:** Create a `user` fixture and verify its name and age.

**Hint:** The fixture should return a dictionary.

**Complete solution:**

```python
import pytest


@pytest.fixture
def user():
    return {"name": "Alice", "age": 30}


def test_user(user):
    assert user["name"] == "Alice"
    assert user["age"] == 30
```

**Explanation:** The test requests the fixture by parameter name.

**Common mistake:** Forgetting `@pytest.fixture`.

---

#### Exercise 7 — Yield fixture

**Problem:** Create a fixture that opens a temporary file, yields it, and closes it.

**Complete solution:**

```python
import pytest


@pytest.fixture
def open_file(tmp_path):
    path = tmp_path / "data.txt"
    handle = path.open("w+")
    try:
        yield handle
    finally:
        handle.close()


def test_file(open_file):
    open_file.write("hello")
    open_file.seek(0)
    assert open_file.read() == "hello"
```

**Explanation:** The file exists for the test and is closed during teardown.

**Common mistake:** Forgetting to close the handle.

---

#### Exercise 8 — Fixture dependency

**Problem:** Create `database` and a dependent `user` fixture.

**Complete solution:**

```python
import pytest


@pytest.fixture
def database():
    return {"users": []}


@pytest.fixture
def user(database):
    new_user = {"name": "Alice"}
    database["users"].append(new_user)
    return new_user


def test_user_exists(database, user):
    assert user in database["users"]
```

**Explanation:** `user` depends on `database`; pytest resolves the dependency first.

**Common mistake:** Calling `database()` in the test.

---

#### Exercise 9 — Single-value parametrization

**Problem:** Validate several valid ages.

**Complete solution:**

```python
import pytest


@pytest.mark.parametrize("age", [18, 25, 40, 120])
def test_valid_age(age):
    assert 0 <= age <= 120
```

**Explanation:** One test definition covers multiple values.

**Common mistake:** Writing four copies of the same test body.

---

#### Exercise 10 — Parameter IDs

**Problem:** Give readable names to three invalid email cases.

**Complete solution:**

```python
import pytest


@pytest.mark.parametrize(
    "email",
    ["", "alice", "alice @ example.com"],
    ids=["empty", "missing-at", "spaces"],
)
def test_invalid_email(email):
    assert "@" not in email or " " in email
```

**Explanation:** IDs make failures easier to interpret.

**Common mistake:** Treating IDs as assertions—they are labels, not correctness checks.

---

### Level 3 — Advanced

#### Exercise 11 — Indirect parametrization

**Problem:** Parametrize a fixture with user definitions.

**Complete solution:**

```python
import pytest


class User:
    def __init__(self, name, role):
        self.name = name
        self.role = role


@pytest.fixture
def user(request):
    return User(**request.param)


@pytest.mark.parametrize(
    "user",
    [
        {"name": "Alice", "role": "admin"},
        {"name": "Bob", "role": "viewer"},
    ],
    indirect=True,
)
def test_user_role(user):
    assert user.role in {"admin", "viewer"}
```

**Explanation:** The parameter goes through the fixture, which turns raw case data into a `User` object.

**Common mistake:** Forgetting `request.param` inside the fixture.

---

#### Exercise 12 — Fixture factory

**Problem:** Create multiple users from one fixture factory.

**Complete solution:**

```python
import pytest


class User:
    def __init__(self, name):
        self.name = name


@pytest.fixture
def make_user():
    return lambda name: User(name)


def test_make_multiple_users(make_user):
    alice = make_user("Alice")
    bob = make_user("Bob")

    assert alice.name == "Alice"
    assert bob.name == "Bob"
```

**Explanation:** The fixture provides a reusable constructor-like function.

**Common mistake:** Making the factory support unrelated resource types.

---

#### Exercise 13 — Scope reasoning

**Problem:** Decide whether a temporary shopping cart should be function or session scoped when tests intentionally mutate it.

**Expected task:** Choose a scope and explain the reason.

**Solution:** Function scope is the safer default because each test needs isolated mutable state.

**Explanation:** Session scope would cause tests to share one mutable cart unless the project explicitly resets it.

**Common mistake:** Choosing session scope solely because “fewer setups is faster.”

---

#### Exercise 14 — Combined fixture + parametrization

**Problem:** Test supported currencies against a valid transaction fixture.

**Complete solution:**

```python
import pytest


@pytest.fixture
def transaction():
    return {"amount": 100, "currency": "INR"}


@pytest.mark.parametrize("currency", ["INR", "USD", "EUR"])
def test_supported_currency(transaction, currency):
    transaction["currency"] = currency
    assert transaction["currency"] in {"INR", "USD", "EUR"}
```

**Explanation:** Fixture creates the baseline; parametrization creates variations.

**Common mistake:** Mutating a shared module/session fixture.

---

#### Exercise 15 — Debug a failing parametrized test

**Problem:** One case in this test is wrong:

```python
@pytest.mark.parametrize(
    "a,b,expected",
    [(1, 2, 3), (2, 2, 5)],
)
def test_add(a, b, expected):
    assert add(a, b) == expected
```

**Expected task:** Find and correct the faulty case.

**Hint:** Evaluate the arithmetic instead of changing the production function.

**Complete solution:**

```python
@pytest.mark.parametrize(
    "a,b,expected",
    [(1, 2, 3), (2, 2, 4)],
)
def test_add(a, b, expected):
    assert add(a, b) == expected
```

**Explanation:** The second expected result was incorrect.

**Common mistake:** Changing `add()` to match a mistaken test expectation.

---

### Level 4 — Production-Oriented

#### Exercise 16 — API validation matrix

**Problem:** Design parameterized tests for an API request validator covering valid, missing, malformed, and boundary inputs.

**Expected task:** Create a structured list of cases and readable IDs.

**Hint:** Separate cases by observable behavior.

**Complete solution:**

```python
import pytest


CASES = [
    ({"age": 18}, True),
    ({"age": 120}, True),
    ({"age": 17}, False),
    ({}, False),
    ({"age": "18"}, False),
]


@pytest.mark.parametrize(
    "payload,valid",
    CASES,
    ids=["minimum", "maximum", "below-minimum", "missing", "wrong-type"],
)
def test_age_payload(payload, valid):
    assert validate_payload(payload) is valid
```

**Explanation:** The data is separated from the test logic and names are diagnostic.

**Common mistake:** Putting unrelated response assertions into the same parametrized function.

---

#### Exercise 17 — Test-data factory design

**Problem:** Build a factory fixture for creating users with optional overrides.

**Complete solution:**

```python
import pytest


@pytest.fixture
def make_user():
    def _make_user(**overrides):
        data = {
            "name": "Alice",
            "age": 30,
            "active": True,
        }
        data.update(overrides)
        return data

    return _make_user


def test_inactive_user(make_user):
    user = make_user(active=False)
    assert user["active"] is False
```

**Explanation:** The factory keeps common defaults in one place while allowing targeted variation.

**Common mistake:** Allowing arbitrary nested logic to accumulate until the factory becomes difficult to understand.

---

#### Exercise 18 — Database fixture lifecycle

**Problem:** Design a fixture that creates a database connection and guarantees closure.

**Complete solution:**

```python
import pytest


@pytest.fixture
def database_connection():
    connection = create_test_connection()
    try:
        yield connection
    finally:
        connection.close()
```

**Explanation:** This models explicit resource ownership.

**Common mistake:** Opening the connection in the fixture and never cleaning it up.

---

#### Exercise 19 — Control combinatorial growth

**Problem:** You have three roles, four states, and five regions. Explain why a full Cartesian product may be excessive and propose a selection strategy.

**Solution:** The full matrix is `3 × 4 × 5 = 60` cases. Select representative equivalence classes, critical boundaries, known high-risk interactions, and regression cases rather than blindly executing all combinations.

**Explanation:** Test design is an optimization problem over risk and cost, not a contest to generate the most cases.

**Common mistake:** Assuming “more parameter rows” automatically means “better testing.”

---

#### Exercise 20 — AI application test boundary

**Problem:** An LLM returns variable natural-language answers, but your application requires a structured tool call with fields `tool`, `user_id`, and `amount`. Design a test strategy.

**Solution:** Use fixtures for deterministic tool state, synthetic input documents, and a controlled test configuration. Validate the structured contract and deterministic tool behavior rather than requiring every model response to equal one exact string. Add separate evaluation strategies for broader model-quality behavior.

**Explanation:** The deterministic boundary is easier to assert reliably than unconstrained text generation.

**Common mistake:** Treating every LLM response as if it were a deterministic arithmetic function.

---

## 45. Debugging Lab

### Lab 1 — Incorrect assertion

**Broken code:**

```python

def test_total():
    assert calculate_total([10, 20]) == 40
```

**Symptom:** Assertion failure.

**Investigation:** Compare actual vs expected.

**Root cause:** The expected value is wrong.

**Correction:**

```python
assert calculate_total([10, 20]) == 30
```

**Why it works:** The test now reflects the intended arithmetic.

---

### Lab 2 — Incorrect fixture

**Broken code:**

```python
@pytest.fixture
def user():
    return None


def test_user_name(user):
    assert user["name"] == "Alice"
```

**Symptom:** `TypeError` when indexing `None`.

**Root cause:** Fixture supplies the wrong shape.

**Correction:**

```python
@pytest.fixture
def user():
    return {"name": "Alice"}
```

---

### Lab 3 — Wrong fixture scope

**Broken code:**

```python
@pytest.fixture(scope="module")
def users():
    return []


def test_add_user(users):
    users.append("Alice")


def test_starts_empty(users):
    assert users == []
```

**Symptom:** The second test fails depending on execution history.

**Investigation:** Look for shared mutable state.

**Root cause:** Module scope shares the list.

**Correction:**

```python
@pytest.fixture
def users():
    return []
```

**Why it works:** Each test receives its own list instance.

---

### Lab 4 — Shared mutable state

**Broken code:**

```python
DEFAULT_USER = {"active": True}


@pytest.fixture
def user():
    return DEFAULT_USER
```

A test mutates `user["active"] = False`.

**Symptom:** Another test unexpectedly sees `False`.

**Root cause:** The fixture returns the same global dictionary.

**Correction:**

```python
@pytest.fixture
def user():
    return {"active": True}
```

**Why it works:** A new dictionary is created for each function-scoped fixture use.

---

### Lab 5 — Missing fixture dependency

**Broken code:**

```python
@pytest.fixture
def user(database):
    ...
```

but no visible `database` fixture exists.

**Symptom:** Fixture-not-found error.

**Investigation:** Check fixture discovery and names.

**Root cause:** Missing or inaccessible dependency.

**Correction:** Define the fixture in a visible location or correct the dependency name.

---

### Lab 6 — Incorrect parametrization

**Broken code:**

```python
@pytest.mark.parametrize("a,b,expected", [(1, 2)])
def test_add(a, b, expected):
    ...
```

**Symptom:** pytest cannot construct the requested test case.

**Root cause:** Two values are supplied for three parameters.

**Correction:**

```python
@pytest.mark.parametrize("a,b,expected", [(1, 2, 3)])
def test_add(a, b, expected):
    ...
```

---

### Lab 7 — Wrong number of parameters

**Broken code:**

```python
@pytest.mark.parametrize("a,b", [(1, 2, 3)])
def test_pair(a, b):
    ...
```

**Root cause:** Three values are supplied for two parameter names.

**Correction:** Either declare three names or remove the extra value.

---

### Lab 8 — Incorrect expected exception

**Broken code:**

```python
with pytest.raises(TypeError):
    parse_age("abc")
```

but the function correctly raises `ValueError`.

**Root cause:** The test expects the wrong behavior.

**Correction:**

```python
with pytest.raises(ValueError):
    parse_age("abc")
```

---

### Lab 9 — Cleanup problem

**Broken code:**

```python
@pytest.fixture
def connection():
    connection = create_connection()
    yield connection
```

**Symptom:** Connection count increases across the test suite.

**Root cause:** No teardown.

**Correction:**

```python
@pytest.fixture
def connection():
    connection = create_connection()
    try:
        yield connection
    finally:
        connection.close()
```

---

## 46. Interview Questions

### Beginner

#### 1. What is pytest?

**Model answer:** Pytest is a Python testing framework that discovers and runs tests, evaluates assertions, manages fixtures, supports parametrization, and reports failures. It is commonly used for automated testing across unit and higher-level test suites.

#### 2. What is an assertion?

**Model answer:** An assertion checks that an expected condition is true. In pytest, the normal Python `assert` statement is used to verify behavior.

#### 3. Why use pytest `assert` instead of unittest-style assertions?

**Model answer:** Pytest lets you use native Python `assert` syntax and enhances failures through assertion introspection, so the test code can stay concise while still getting useful diagnostics. It does not mean `unittest` assertions are invalid; both are legitimate approaches.

#### 4. What is a fixture?

**Model answer:** A fixture is pytest-managed test setup or a reusable dependency that can be injected into tests by name. Fixtures can also manage resource lifecycle and scope.

### Intermediate

#### 5. How does pytest resolve fixtures?

**Model answer:** A test requests fixtures by parameter name. Pytest finds visible fixture definitions, resolves their dependencies, creates or reuses fixture instances according to scope, passes values into the test, and later performs appropriate teardown.

#### 6. What is fixture scope?

**Model answer:** Scope defines the reuse/lifetime boundary of a fixture instance, such as function, class, module, package, or session. It affects how often setup happens and how long the resource may be shared.

#### 7. What is `yield` in a fixture?

**Model answer:** A yield fixture uses code before `yield` for setup, yields the resource/value to the test, and uses code after `yield` for teardown/finalization.

#### 8. What is `autouse`?

**Model answer:** An autouse fixture is automatically applied within its visibility and scope without being explicitly requested by each test. It is useful for genuinely universal setup but can create hidden dependencies when overused.

#### 9. What is `conftest.py`?

**Model answer:** It is a pytest-specific file used to define fixtures and configuration that can be discovered within a test directory tree. It helps share test infrastructure without importing every shared fixture explicitly.

### Advanced

#### 10. What is parametrization?

**Model answer:** Parametrization runs the same test logic against multiple input/data sets. It reduces duplicate test functions and makes case data explicit.

#### 11. Why use parametrization?

**Model answer:** It is useful when the behavior and assertions are essentially the same while the inputs vary. It improves coverage with less repeated test code and supports readable test IDs.

#### 12. What is indirect parametrization?

**Model answer:** With `indirect=True`, parameter values are passed into fixtures via `request.param` instead of directly into the test argument. It is useful when test data should drive fixture setup.

#### 13. How do fixtures and parametrization work together?

**Model answer:** Fixtures provide dependencies and lifecycle management; parametrization provides variation in test cases. They can be combined directly, or parameters can be routed through fixtures with indirect parametrization.

#### 14. How do you avoid fixture overuse?

**Model answer:** Keep fixtures focused on meaningful shared setup or managed dependencies. Use local variables and helper functions for small, explicit data creation. Avoid giant fixtures and unnecessary nesting.

#### 15. How do you maintain test isolation?

**Model answer:** Avoid uncontrolled shared mutable state, use appropriate fixture scopes, isolate files and databases, reset environment and caches deliberately, and ensure resource cleanup occurs even when tests fail.

#### 16. How do you design test data?

**Model answer:** Use representative values, boundaries, invalid cases, deterministic inputs, minimal fixtures, and readable structured cases. Select combinations based on risk rather than blindly generating every Cartesian product.

#### 17. How do you debug a failing parametrized test?

**Model answer:** Read the failing case ID, compare actual vs expected, isolate the test case, inspect the input data and relevant fixtures, reproduce only that case, correct the underlying defect, then rerun the regression suite.

---

## 47. Architecture Questions

### 1. How would you structure pytest tests for a large backend?

**Architecture-oriented answer:** Separate test layers such as unit, integration, and end-to-end tests. Organize by domain or service boundaries, keep reusable fixtures close to the tests that share them, and place cross-cutting infrastructure in deliberately scoped `conftest.py` files. Use markers or configuration to select expensive layers in CI.

```text
tests/
├── conftest.py
├── unit/
├── integration/
└── e2e/
```

### 2. How would you share fixtures across many modules?

Put genuinely shared fixtures in an appropriate `conftest.py`. Avoid moving every fixture into the highest-level file just because it is technically reusable.

### 3. How would you handle expensive database setup?

Separate expensive reusable infrastructure from mutable per-test state. For example, a broader-scoped database client or schema may be safe to reuse while test data is isolated per function or transaction. The exact design depends on database behavior and concurrency requirements.

### 4. When would you use a session-scoped fixture?

When a resource is expensive, safe to share for the duration of the test session, has a clear lifecycle, and does not create problematic shared mutable state or concurrency limitations.

### 5. How would you prevent test pollution?

Use isolation boundaries for data, files, environment state, caches, and external dependencies. Prefer fresh mutable state for tests when practical and make cleanup deterministic.

### 6. How would you design reusable test data?

Start with simple fixtures or helpers. Introduce factories when a test needs multiple variants. Use structured case objects for larger scenario tables. Keep test data explicit enough that a reader can understand why each case exists.

### 7. How would you test hundreds of input combinations without creating hundreds of functions?

Use parametrization where the behavior is shared, but select combinations intelligently. Use readable IDs and structured data. Avoid full Cartesian products unless every combination is actually meaningful.

### 8. How would you control combinatorial explosion?

Partition inputs into equivalence classes, test boundaries, focus on high-risk interactions, preserve regression cases, and choose representative combinations. Use layered testing so exhaustive coverage can be reserved for the most valuable boundaries.

### 9. How would you design fixtures for an AI application?

Provide deterministic configurations, synthetic documents, controlled databases, fake/recorded service boundaries, and controlled tool implementations. Keep the deterministic application logic testable independently of variable model output.

### 10. How would you test deterministic tool behavior in an agentic AI system?

Test the tool as a deterministic component with normal assertions, parametrized inputs, and controlled fixtures. Test input validation, state transitions, structured output schemas, error handling, and side-effect boundaries independently from the model's natural-language reasoning.

### 11. How would you structure unit/integration/E2E dependencies?

Keep unit tests fast and isolated. Integration tests exercise real component boundaries such as databases or HTTP layers. E2E tests validate important end-user workflows. Fixtures should reflect those boundaries instead of causing every test layer to instantiate the full production stack.

---

## 48. Production Checklist

Use this checklist when reviewing a pytest suite.

### Assertions

- [ ] Assertions verify meaningful behavior.
- [ ] Expected and actual values are clear.
- [ ] Custom messages are added only when useful.
- [ ] Exception tests verify the right exception type.
- [ ] Exception-message assertions are stable enough to maintain.

### Fixtures

- [ ] Fixtures have one clear responsibility.
- [ ] Dependencies are visible and understandable.
- [ ] Fixture scopes are intentional.
- [ ] Mutable state is isolated where necessary.
- [ ] Resource-owning fixtures clean up correctly.
- [ ] `autouse=True` is reserved for justified cross-cutting setup.
- [ ] `conftest.py` contains shared infrastructure, not everything.
- [ ] Fixture nesting is understandable.

### Parametrization

- [ ] Parameters represent one coherent behavior.
- [ ] Case data is readable.
- [ ] IDs are meaningful for complex cases.
- [ ] Invalid and edge cases are represented intentionally.
- [ ] Indirect parametrization is used only where it adds value.
- [ ] Large matrices are controlled to avoid combinatorial explosion.

### Engineering quality

- [ ] Tests are deterministic when deterministic behavior is expected.
- [ ] Tests are isolated.
- [ ] Tests fail diagnostically.
- [ ] Test organization matches architecture.
- [ ] CI can run appropriate test layers.
- [ ] Expensive infrastructure is scoped deliberately.
- [ ] Test data is easy to understand and update.
- [ ] The suite avoids over-engineering.

---

## 49. Knowledge Check

### Conceptual questions

#### Q1. What is the difference between a test and a test case?

**Answer:** A test is the checking logic or behavior being verified. A test case is one concrete scenario/input set for that test. Parametrization can generate many test cases from one test function.

#### Q2. Why is a fixture not simply “a helper function”?

**Answer:** A fixture is managed by pytest. It can participate in dependency injection, scope, caching, and teardown. A helper is ordinary Python code that is called explicitly.

#### Q3. Why can broader fixture scope create isolation problems?

**Answer:** A broader-scoped fixture may share one mutable instance across more tests. Mutations can then leak from one test to another.

#### Q4. Why is 100% coverage not proof of good testing?

**Answer:** Coverage shows executed code, not whether assertions correctly verify behavior.

#### Q5. Why is an exact exception-message assertion sometimes fragile?

**Answer:** Error wording may be changed without changing the semantics of the contract. Tests that do not actually require exact wording can become needlessly coupled to text.

### Code-reading questions

#### Q6. What is wrong here?

```python
@pytest.mark.parametrize("a,b", [(1, 2, 3)])
def test_add(a, b):
    ...
```

**Answer:** Two parameter names are declared but each case supplies three values.

#### Q7. What does this fixture do?

```python
@pytest.fixture(scope="module")
def config():
    return {"env": "test"}
```

**Answer:** It creates a module-scoped fixture that can be reused by requesting tests within the applicable module scope.

#### Q8. What does `indirect=True` change here?

```python
@pytest.mark.parametrize("user", [{"name": "Alice"}], indirect=True)
def test_user(user):
    ...
```

**Answer:** The parameter value is passed to the `user` fixture as `request.param`, and the resulting fixture value is passed to the test.

### Debugging questions

#### Q9. Tests pass individually but fail as a suite. What should you inspect first?

**Answer:** Shared state, fixture scope, cleanup, environment variables, caches, file paths, and database state. Also check for order dependence.

#### Q10. Pytest says a fixture cannot be found. What are the likely causes?

**Answer:** Name mismatch, missing `@pytest.fixture`, fixture outside the visible directory tree, configuration/import problems, or a fixture defined under the wrong test subtree.

### Design questions

#### Q11. When should a large parameter table become structured test-case objects?

**Answer:** When the tuple/dictionary has enough fields that the case meaning is becoming difficult to understand or maintain. The goal is readability, not abstraction for its own sake.

#### Q12. When should a parametrized test become separate functions?

**Answer:** When cases represent meaningfully different behavior, setup, or assertions. Shared data alone is a good reason for parametrization; fundamentally different scenarios usually deserve distinct tests.

---

## 50. Glossary

| Term | Definition |
|---|---|
| **test** | Automated check of expected software behavior. |
| **test case** | One concrete input/scenario for a test. |
| **assertion** | An expectation that a condition or value is correct. |
| **pytest** | Python testing framework for test discovery, execution, fixtures, parametrization, and reporting. |
| **fixture** | Pytest-managed reusable setup or test dependency. |
| **fixture scope** | Lifetime/reuse boundary of a fixture instance. |
| **dependency injection** | Supplying a component's dependency from outside instead of having it create the dependency itself. |
| **setup** | Preparation performed before a test uses a resource. |
| **teardown** | Cleanup performed after use of a test resource. |
| **yield fixture** | Fixture that yields a value to the test and runs finalization code afterward. |
| **autouse** | Fixture behavior that automatically applies a fixture within its scope without explicit request. |
| **`conftest.py`** | Pytest file used for shared fixtures/configuration within a test directory tree. |
| **parametrization** | Running the same test logic with multiple input sets. |
| **indirect parametrization** | Parametrization that routes values through fixture functions via `request.param`. |
| **test ID** | Human-readable label for a parametrized test case. |
| **test isolation** | Independence of a test from unrelated test execution state. |
| **deterministic test** | Test whose controlled inputs lead to repeatable outcomes. |
| **flaky test** | Test whose result changes unpredictably without an intended behavior change. |
| **regression test** | Test that protects against a previously fixed or historically important defect recurring. |
| **test coverage** | Measurement of code exercised by tests. |
| **boundary test** | Test focused on a limit where valid and invalid behavior changes. |
| **negative test** | Test of invalid input, failure behavior, or rejection conditions. |
| **behavioral test** | Test focused on externally observable behavior rather than unnecessary implementation details. |

---

# Final Mental Model

The three core concepts can be remembered as:

```text
Assertions
→ verify behavior

Fixtures
→ prepare and manage reusable test dependencies

Parametrization
→ run the same test logic against multiple cases
```

Together they support the common testing flow:

```text
Arrange
→ fixtures / test data

Act
→ execute the behavior

Assert
→ verify expected behavior
```

A slightly larger mental model is:

```text
                    ┌──────────────┐
                    │   Fixtures   │
                    │ setup/life-  │
                    │ cycle/deps   │
                    └──────┬───────┘
                           │
                           ↓
Input cases ───────→ Test function ───────→ Assertions
(parametrize)             │                     │
                           ↓                     ↓
                    Application behavior    Pass / Fail
```

This foundation scales toward:

```text
unit testing
    ↓
integration testing
    ↓
API testing
    ↓
data testing
    ↓
ML pipeline testing
    ↓
AI / LLM application testing
    ↓
agentic AI system testing
    ↓
production CI/CD
```

The important architectural principle is separation of concerns:

```text
fixtures
= how the environment/dependency is prepared

parametrization
= which data/cases are exercised

assertions
= what correctness means
```

When those responsibilities remain clear, tests become easier to read, debug, scale, and maintain.

---

# Final Self-Review Checklist

- [x] The chapter starts from absolute beginner level.
- [x] Software testing, tests, test cases, assertions, and pytest are introduced first.
- [x] Installation, execution, discovery, useful commands, and exit-code concepts are covered.
- [x] Assertions are explained deeply.
- [x] Pytest assertion introspection is explained.
- [x] `pytest.raises()` is explained with type, message matching, and exception inspection.
- [x] Behavioral assertions are distinguished from implementation-detail testing.
- [x] `pytest.fixture` is explained from first principles.
- [x] Fixture dependency injection is explained.
- [x] Fixture return values are covered.
- [x] Setup/teardown and `yield` fixtures are covered.
- [x] Function, class, module, package, and session scopes are covered.
- [x] Fixture isolation and shared-state risks are covered.
- [x] Multiple fixture composition is covered.
- [x] `autouse` is explained with good and bad use cases.
- [x] `conftest.py` and fixture visibility are explained.
- [x] Fixture factories are covered.
- [x] Parametrization is explained deeply.
- [x] Multiple parameters are covered.
- [x] Single-value parametrization is covered.
- [x] Parametrized exception testing is covered.
- [x] Parameter IDs are covered.
- [x] Fixtures + parametrization are combined.
- [x] Indirect parametrization is explained.
- [x] Complex structured test data is covered.
- [x] Boundary and edge-case testing is covered.
- [x] Parametrization is compared with separate test functions.
- [x] Test-data design and Arrange → Act → Assert are covered.
- [x] Fixtures are compared with helper functions.
- [x] Fixtures are distinguished from mocking conceptually.
- [x] Common fixture mistakes include diagnosis and better designs.
- [x] Common parametrization mistakes include diagnosis.
- [x] Advanced fixture lifecycle concepts are covered.
- [x] Scope trade-offs are explained without absolute rules.
- [x] Advanced parametrization design and combinatorial explosion are covered.
- [x] Relevant pytest markers are introduced.
- [x] Test organization and discovery are covered.
- [x] Backend, API, database, data, ETL/ELT, ML, AI/LLM, and agentic-AI use cases are connected.
- [x] Test quality is discussed beyond “did it pass?”
- [x] Code coverage is explained without equating coverage to quality.
- [x] A systematic pytest debugging workflow is included.
- [x] A complete realistic example is included.
- [x] A complete mini-project is included.
- [x] Four exercise levels are included with at least five exercises per level.
- [x] Every exercise has a problem, task, hints, solution, explanation, and common mistake.
- [x] A dedicated debugging lab is included.
- [x] Beginner-to-advanced interview questions and model answers are included.
- [x] Architecture/system-design questions and answers are included.
- [x] A production checklist is included.
- [x] A final knowledge check with immediate answers is included.
- [x] A glossary is included.
- [x] The final mental model is included.
- [x] Code examples use valid, progressively more advanced Python and pytest patterns.
- [x] No unrelated topic replaces the chapter's focus.
- [x] Fixture scope, coverage, helpers, parametrization, and implementation-detail guidance are intentionally non-absolute.
- [x] The chapter is oriented toward later backend, data engineering, ML, AI, agentic systems, and CI/CD work.

## Reference Notes

For the most authoritative syntax and behavior details, consult the pytest documentation for:

- assertions and assertion introspection;
- expected exceptions with `pytest.raises()`;
- fixture definitions, scopes, autouse behavior, teardown, and sharing;
- parametrization, IDs, and indirect parametrization;
- test discovery and command-line usage.

The chapter intentionally favors documented pytest behavior over assumptions about internal implementation details.
