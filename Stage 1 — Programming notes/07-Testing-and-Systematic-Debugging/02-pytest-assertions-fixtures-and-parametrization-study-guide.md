# Pytest — Assertions, Fixtures, and Parametrization
## Complete Study Guide and Exercise Solutions

**Roadmap:** Stage 1 — Programming & Computational Thinking  
**Module:** 07 — Testing and Systematic Debugging  
**Lesson:** 02 — Pytest: Assertions, Fixtures, and Parametrization  
**Source lesson:** `02-pytest-assertions-fixtures-and-parametrization(1).md`

---

# Part A — Complete Lesson Summary

## 1. What pytest is and why it matters

Software testing checks whether software behaves as intended. A **test** is the checking logic; a **test case** is one concrete input/scenario; an **assertion** states what must be true. `pytest` is a Python testing framework that discovers tests, executes them, evaluates assertions, manages setup and cleanup through fixtures, generates parametrized cases, and reports failures.

Manual checking is fine for a tiny experiment:

```python
print(add(2, 3))
```

But someone must inspect the output every time. An automated test records the expectation:

```python
def add(a, b):
    return a + b

def test_add():
    assert add(2, 3) == 5
```

Pytest discovers `test_add`, calls it, evaluates the assertion, and reports pass/fail. Tests become executable documentation and can run repeatedly in local development and CI.

Python also includes `unittest`. A pytest test is commonly a plain function using `assert`; `unittest` commonly uses a class derived from `unittest.TestCase` and methods such as `self.assertEqual`. Both are valid. Pytest is popular for concise syntax, fixtures, parametrization, plugins, and rich failure reports. A framework does not compensate for weak test design.

A test failure means an assertion or test condition did not hold. A test error means the test could not complete correctly, for example because collection, import, fixture setup, or the environment failed. A test should verify observable behavior, not merely execute code.

## 2. Installing, running, and discovering tests

Pytest is normally a development dependency, not a production runtime dependency. A simple installation is:

```bash
python -m pip install pytest
```

In a managed project, declare it in the development dependency group and install it through the project's environment/lock workflow.

Useful commands:

```bash
pytest                         # discover and run the suite
pytest -v                      # verbose test names
pytest -q                      # concise output
pytest tests/test_users.py     # one file
pytest tests/test_users.py::test_create_user
pytest tests/unit              # one directory
pytest -k "user and not slow"  # select by keyword expression
pytest --collect-only -q       # show collected tests, do not execute
pytest --fixtures              # inspect available fixtures
python -m pytest               # run using the active Python interpreter
```

Typical discovery patterns are `test_*.py` and `*_test.py`; test functions/methods normally start with `test_`, and test classes commonly start with `Test`. A test may not appear because its filename/name does not match, pytest was run from the wrong directory, configuration changed discovery, or import/collection failed. Run `pytest --collect-only -q` to diagnose collection.

A dot in the progress output usually means pass; `F` indicates failure. Exit code `0` means the run succeeded; non-zero indicates failure, collection/usage error, or another unsuccessful run. CI uses this status to gate later pipeline steps.

## 3. Assertions and assertion introspection

An assertion checks a condition:

```python
assert condition
assert 2 + 2 == 4
```

A true condition continues silently; a false condition raises `AssertionError`. Pytest enhances failure output by rewriting assertions in collected test modules and showing useful subexpressions, such as `assert 7 == 10`.

Common patterns:

```python
assert actual == expected       # exact logical equality
assert actual != unexpected
assert value is None
assert value is not None
assert user.is_active            # truthy condition
assert not user.is_blocked
assert "admin" in roles
assert "suspended" not in roles
assert isinstance(result, User)
assert type(result) is User      # exact type only; rejects subclasses
assert len(items) == 3
```

The `is None` form is preferred because `None` is a singleton. Use `isinstance` when subclasses are acceptable; use `type(x) is T` only when exact type identity is part of the contract.

Assertions work with integers, strings, booleans, lists, dictionaries, sets, tuples, and object attributes:

```python
assert [1, 2] == [1, 2]
assert {"name": "Alice"}["name"] == "Alice"
assert {1, 2} == {2, 1}
assert (200, "OK") == (200, "OK")
```

A test such as `assert isinstance(add(2, 3), int)` may pass even when the result is the wrong integer. Prefer `assert add(2, 3) == 5` because it checks the actual contract.

Custom messages add context when needed:

```python
assert config.environment == "test", "Tests must use the test environment"
```

Avoid redundant messages such as `"result should equal 5"` when pytest already shows actual and expected values. Assertion rewriting primarily applies to collected test modules; imported helper modules do not automatically receive identical rewriting in every situation. Assertion-helper libraries may need explicit rewrite registration.

Important distinction: Python's `assert` is suitable in tests, but not for mandatory production validation or security checks because optimized Python (`-O`) can remove assertions.

## 4. Testing expected exceptions with `pytest.raises`

An error can be correct behavior: invalid input may need to raise `ValueError`, a domain exception, or another documented exception.

```python
import pytest

def parse_age(value):
    if not isinstance(value, str):
        raise TypeError("age must be a string")
    if not value.isdigit():
        raise ValueError("age must be numeric")
    return int(value)

def test_parse_age_rejects_text():
    with pytest.raises(ValueError):
        parse_age("abc")
```

The context manager passes only if the expected exception is raised. If nothing is raised, the test fails; if a different exception is raised, the test fails.

Capture details only when they are part of the contract:

```python
def test_parse_age_error_details():
    with pytest.raises(ValueError) as exc_info:
        parse_age("abc")

    assert exc_info.type is ValueError
    assert str(exc_info.value) == "age must be numeric"
```

`match=` checks the exception's string using regular-expression search semantics:

```python
with pytest.raises(ValueError, match="must be numeric"):
    parse_age("abc")
```

Exact full-message checks can be brittle when wording is not a public contract. Prefer a stable substring or structured exception attribute where appropriate. Do not use `try/except Exception: pass`; it can hide the wrong exception and unrelated defects. Parametrize invalid inputs and boundary values, for example age values `0` and `120` as valid boundaries, `-1` and `121` as invalid boundaries.

## 5. Behavioral assertions versus implementation coupling

A behavioral assertion checks externally observable behavior:

```python
def get_username(user_id):
    users = {1: "Alice"}
    return users[user_id]

def test_get_username():
    assert get_username(1) == "Alice"
```

Do not unnecessarily assert private helper call order, internal attributes, temporary data structures, or exact formatting that is not guaranteed by the public contract. Such tests are **brittle**: harmless refactoring breaks them even though users see no difference.

Weak:

```python
assert result is not None
```

Stronger, if this is the contract:

```python
assert result == {"status": "approved", "amount": 100}
```

Ask: “Would a user or dependent component notice this difference?” If not, it may not deserve an assertion. Test meaningful outcomes, not incidental implementation details.

## 6. Fixtures: reusable setup and dependency injection

A **fixture** is pytest-managed setup or a reusable dependency. It avoids repeating the same object construction in many tests.

```python
import pytest

@pytest.fixture
def sample_user():
    return {"name": "Alice", "age": 30}

def test_user_name(sample_user):
    assert sample_user["name"] == "Alice"
```

`@pytest.fixture` decorates/registers the function as a fixture. `sample_user` still is a normal Python function, but pytest manages it. The test requests it by parameter name. Pytest finds the fixture, creates or reuses its value according to scope, and injects the value into the test.

This is **dependency injection**: the test declares what it needs; pytest supplies it. The test does not normally call `sample_user()` itself. Explicit test parameters make dependencies visible:

```python
def test_checkout(authenticated_user, cart):
    ...
```

Fixtures can return primitives, lists, dictionaries, objects, connections, or clients. A fixture returning data is simple; a fixture owning a resource must manage its lifecycle.

Example values:

```python
@pytest.fixture
def username():
    return "alice"

@pytest.fixture
def product_ids():
    return [101, 102, 103]

@pytest.fixture
def request_payload():
    return {"name": "Alice", "email": "alice@example.com"}
```

A fixture can return an application object such as `User("Alice", 30)`. For a resource, setup and cleanup matter.

## 7. Setup, yield, teardown, and cleanup

A resource lifecycle is:

```text
SETUP → TEST USE → TEARDOWN
```

Examples: open/use/close a file; connect/use/close a database connection; create/use/clean a temporary resource.

A yield fixture:

```python
@pytest.fixture
def connection():
    connection = create_connection()
    try:
        yield connection
    finally:
        connection.close()
```

Code before `yield` is setup. The yielded value is injected into the test. Code after `yield` is finalization. `finally` ensures cleanup even if the test fails. A fixture that opens a resource and never closes it leaks connections/files/sockets and can exhaust resources during a long suite.

For a temporary file:

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

`tmp_path` is a pytest built-in fixture that supplies a fresh temporary directory for a test and cleans it up. A fixture's cleanup is part of correctness, not optional housekeeping.

## 8. Fixture scopes and lifecycle trade-offs

Scope controls how broadly a fixture instance can be reused and how long it lives:

| Scope | Approximate reuse boundary | Typical use | Main risk/trade-off |
|---|---|---|---|
| `function` (default) | each test function | mutable test data | repeated setup |
| `class` | test class | shared class setup | shared state |
| `module` | test module | safe shared client | reduced isolation |
| `package` | package scope | package-level resources | more complex sharing |
| `session` | pytest run | expensive stable resource | widest sharing/lifetime |

A broader scope can reduce repeated setup but increases the sharing surface and lifetime. A function-scoped list is recreated per test; a module/session-scoped mutable list can leak mutations. A broad-scoped fixture cannot depend on a narrower-scoped fixture: for example, session scope cannot depend on function scope, causing `ScopeMismatch`.

Choose scope by asking:
1. Can tests safely share this resource?
2. How expensive is setup?
3. Is it mutable?
4. Can state leak?
5. What cleanup is required?
6. Does parallel execution affect safety?

A useful production pattern is **shared infrastructure plus per-test state**: reuse a safe database client at module/session scope while isolating each test's transaction, schema, or data at function scope. Immutable configuration is often safer to share than mutable request state. Never choose session scope solely because it seems faster.

## 9. Isolation and test pollution

Isolation means one test does not depend on another test's execution order or leftover state. Shared mutable lists/dictionaries, fixed filenames, database rows, environment variables, caches, and external services can all cause pollution.

Bad:

```python
DEFAULT_USER = {"active": True}

@pytest.fixture
def user():
    return DEFAULT_USER
```

If one test changes `user["active"]`, another test sees the mutation. Better:

```python
@pytest.fixture
def user():
    return {"active": True}
```

Use temporary paths, unique IDs, transaction rollback, per-test databases/schemas, explicit cleanup, environment restoration, and deliberate cache resets. External services add network failures, rate limits, changing data, authentication issues, latency, and nondeterminism. Keep deterministic logic separate from real integration checks.

Isolation and reuse are a trade-off: maximize safe reuse, not reuse at any cost.

## 10. Fixture composition, autouse, conftest, and factories

Fixtures can depend on other fixtures:

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

def test_dashboard(authenticated_user):
    assert authenticated_user.is_authenticated
```

Pytest resolves dependencies first and finalizes them in the appropriate reverse dependency order. This forms a dependency graph. Avoid one giant `everything` fixture or seven unnecessary layers; each fixture should have a meaningful responsibility.

An **autouse** fixture runs automatically within its visibility/scope without being requested:

```python
@pytest.fixture(autouse=True)
def reset_state():
    reset_test_state()
```

Use it only for genuinely universal setup (for example, enforcing a universal test environment invariant). Overuse creates hidden dependencies and unnecessary cost.

`conftest.py` is pytest's fixture/configuration sharing mechanism. A `tests/conftest.py` fixture can be visible to tests below that directory; child subtrees do not make their fixtures automatically visible to parent or sibling test locations. Keep shared fixtures near tests that truly share them. Do not put everything in the root conftest or use it as a general helper dumping ground. This lesson explains conftest; it does not require creating a project conftest file.

A **fixture factory** returns a function that creates multiple values consistently:

```python
@pytest.fixture
def make_user():
    def _make_user(name, age):
        return User(name=name, age=age)
    return _make_user

def test_users(make_user):
    alice = make_user("Alice", 30)
    bob = make_user("Bob", 25)
    assert alice.name == "Alice"
    assert bob.name == "Bob"
```

Factories are useful for multiple variants. Avoid factories with dozens of unrelated flags. A helper function is explicitly called ordinary Python code; a fixture is pytest-managed and adds injection, scope, caching, dependency composition, and teardown. Use a helper for simple data creation; use a fixture for a test dependency/resource/lifecycle. Fixtures and mocks are not competitors: fixture prepares/configures the dependency; a mock/fake controls its behavior.

## 11. Parametrization fundamentals

**Parametrization** runs the same test logic with multiple sets of inputs. It is useful when cases share behavior and assertions.

```python
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

The parameter-name string defines the function arguments; each tuple is one generated case. Pytest collects multiple test invocations from one function. Default generated IDs depend on values; explicit IDs make failures easier to understand.

Without parametrization, three separate tests would repeat the same body. Parametrization reduces duplication and makes data explicit. But it is not always clearer: use separate functions when scenarios require meaningfully different setup, assertions, or behavior.

For multiple parameters, each case must supply exactly one value per parameter name. Common errors include too few/many values, wrong tuple nesting, duplicated large payloads, unreadable long tuples, unrelated scenarios in one function, inappropriate `indirect=True`, and missing IDs. Use `pytest --collect-only -q` to inspect generated cases.

Single-value parametrization:

```python
@pytest.mark.parametrize("age", [18, 25, 40, 120])
def test_valid_age(age):
    assert 0 <= age <= 120
```

Parametrized exception tests:

```python
@pytest.mark.parametrize(
    "value",
    ["abc", "", "-5"],
    ids=["letters", "empty", "negative-text"],
)
def test_invalid_age(value):
    with pytest.raises(ValueError):
        parse_age(value)
```

Cases can expect different exception types/messages by including those values in the parameter table and using the expected exception in the test design.

## 12. Parameter IDs and indirect parametrization

IDs are diagnostic labels, not assertions:

```python
@pytest.mark.parametrize(
    "email",
    ["", "alice", "alice.example.com"],
    ids=["empty", "missing-at", "dotted-no-at"],
)
def test_email(email):
    ...
```

They make failure output understandable and can be selected using pytest's node IDs or `-k`. A callable `ids=` can derive labels from case data. Prefer meaningful labels over opaque generated IDs for complex cases.

Direct parametrization passes values directly to the test. **Indirect parametrization** routes values through a fixture so setup can transform case data into a dependency:

```python
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

`indirect=True` means pytest passes the raw parameter to the fixture as `request.param`; the fixture builds the object and its result is injected into the test. Partial indirect parametrization is possible when only some parameters should pass through fixtures. Do not use indirect mode merely because data is complex; use it when fixture setup is genuinely the right boundary.

## 13. Complex cases, edge cases, and test-data design

Test data can be tuples, dictionaries, or structured case objects. Use simple tuples for small cases; dictionaries when named fields improve clarity; structured objects when a large case table becomes difficult to read. Separate case data from test logic. Good data is representative, boundary-aware, invalid where required, minimal, deterministic, readable, and diagnosable.

Boundary-value testing checks limits where behavior changes. For age 0–120, test 0 and 120, then invalid -1 and 121. For transaction amount, test zero, negative, non-numeric, boolean, NaN/infinity, and valid positive values. Do not construct a 50-field object when the test needs only three fields.

Avoid uncontrolled random values. If randomness is part of the test, control and record the seed/input. Arrange–Act–Assert remains useful: Arrange with fixtures/case data, Act by calling behavior, Assert the outcome. A thousand repetitive cases do not automatically provide more confidence than a smaller set selected by risk.

## 14. Combining assertions, fixtures, parametrization, and exception checks

These mechanisms have separate jobs:

```text
fixture          = how dependencies/data are prepared
parametrization  = which cases are run
assertion        = what correct behavior means
pytest.raises    = which failure is expected
```

Example transaction validation:

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

@pytest.fixture
def valid_transaction():
    return {"amount": 100, "currency": "INR"}

@pytest.mark.parametrize(
    "currency",
    ["INR", "USD", "EUR"],
)
def test_supported_currency(valid_transaction, currency):
    valid_transaction["currency"] = currency
    assert validate_transaction(valid_transaction) is True

@pytest.mark.parametrize(
    "transaction,message",
    [
        ({"amount": 0, "currency": "INR"}, "amount must be positive"),
        ({"amount": 10, "currency": "GBP"}, "unsupported currency"),
    ],
    ids=["zero-amount", "unsupported-currency"],
)
def test_invalid_transaction(transaction, message):
    with pytest.raises(TransactionError, match=message):
        validate_transaction(transaction)
```

Mutation is safe here because the fixture is function-scoped; mutating a broader-scoped fixture risks leakage.

## 15. Common mistakes and lifecycle mechanics

Fixture mistakes:
1. Fixture name mismatch between definition and test parameter.
2. Missing `@pytest.fixture`.
3. Wrong scope for mutable state.
4. Returning a shared global list/dictionary.
5. Overusing autouse.
6. Giant fixtures that return everything.
7. Fixtures mixing unrelated setup concerns.
8. Hidden dependencies.
9. Excessive fixture nesting.
10. Expensive session fixtures without measuring trade-offs.
11. Missing cleanup.
12. Incorrect yield/finalization logic.

Parametrization mistakes:
1. Wrong number of parameter values.
2. Incorrect tuple/nesting shape.
3. Duplicated large test data.
4. Unreadably large case lists.
5. Overly complex matrices.
6. Indirect parametrization where direct values are enough.
7. Missing meaningful IDs.
8. Mixing unrelated scenarios.

Lifecycle sequence: pytest collects tests, resolves fixture dependencies, creates fixture values as needed, reuses them according to scope/cache rules, runs tests, and finalizes resources. A dependency must exist before its dependent. Teardown follows fixture finalization semantics so dependent resources are finalized before their dependencies. Rely on documented pytest behavior, not private internal manager data structures or undocumented implementation details.

## 16. Scope design and combinatorial growth

Function scope favors isolation but repeats setup. Session scope can reuse expensive stable resources but lengthens resource lifetime and increases shared-state/concurrency risks. A database client may be shared while test data/transactions are per-test. Configuration that is immutable is safer to share than mutable state.

Combinations multiply. Three input types × four roles × five states = 60 cases; adding four regions gives 240. A full Cartesian product may be wasteful. Select representative equivalence classes, important boundaries, high-risk interactions, and known regressions. Use meaningful IDs such as `admin-active-valid`. Keep case data separate from test logic; use structured cases when tuples become opaque.

## 17. Pytest markers

A marker attaches metadata to a test. Parametrization itself is implemented with a built-in marker, but markers also categorize tests:

```python
@pytest.mark.integration
def test_database_connection():
    ...
```

```bash
pytest -m integration
pytest -m "not slow"
```

Register custom markers in project configuration so spelling mistakes are detected and categories are documented. Markers select/group tests; parametrization generates test cases. They solve different problems.

## 18. Test discovery and organization

A maintainable tree can separate layers:

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

Put shared fixtures in the appropriate conftest; keep unit/integration-specific fixtures closer to their tests. Keep parametrization near the behavior it covers; move large case data into named constants or structured modules. Good organization lets a developer quickly locate a test, fixture, or layer and run only the relevant scope.

## 19. Production use: backend, API, database, data, ML, AI, and agents

- **Backend:** fixtures create configuration, domain objects, authenticated users, repositories, and services; parametrization covers valid/invalid requests and state transitions.
- **REST API:** a client fixture supplies the test client; parametrized payloads check expected status codes.
- **Database services:** fixtures manage connection, schema, transactions, seed data, and rollback. Balance expensive infrastructure reuse with per-test data isolation.
- **Data pipelines:** deterministic datasets and temporary locations; parametrize schema variants, missing values, duplicates, timestamps, and malformed rows.
- **ETL/ELT:** test normalization and transformation outputs with fixed input/output pairs.
- **ML:** fixtures provide synthetic datasets, preprocessing configuration, model stubs/fakes, and temporary model directories; parametrize feature edge cases, schema variants, and thresholds.
- **AI/LLM:** controlled configurations, synthetic documents, recorded/fake responses, test DBs, and tool clients. Deterministic software behavior should be tested separately from model quality.
- **Agentic AI:** controlled tool implementations, synthetic documents, sandboxed databases, and deterministic state. Parametrize tool inputs/results. Avoid assuming every generated natural-language answer is identical; verify structured outputs, safety constraints, tool-call contracts, invariants, and deterministic components.

A fake model can map known questions to fixed responses and make orchestration tests deterministic. Model evaluation is a separate activity from ordinary software tests.

## 20. Test quality and coverage

A strong test is deterministic, isolated, readable, meaningful, maintainable, appropriately fast, diagnostic, behavior-focused, and correctly scoped.

Weak:

```python
def test_user_creation():
    user = create_user("Alice")
    assert user is not None
```

Stronger when these are contract fields:

```python
def test_user_creation():
    user = create_user("Alice")
    assert user.name == "Alice"
    assert user.is_active is True
```

**Line coverage** measures which executable lines ran. **Branch coverage** measures which decision paths ran. Coverage reveals unexecuted code, but a test can execute a line without checking the result:

```python
def divide(a, b):
    return a / b

def test_divide():
    divide(10, 2)  # executes code but asserts nothing
```

Therefore, coverage is a signal, not a quality score. It does not prove correct assertions or adequate scenarios.

## 21. Debugging failed pytest tests

Use a deliberate sequence:
1. Read the failure and identify the test.
2. Determine whether failure occurred in assertion, collection, fixture setup, or teardown.
3. Compare expected and actual values.
4. Inspect fixture inputs/scope/state.
5. Inspect the failing parametrized case and its ID.
6. Run only that case.
7. Simplify to the smallest reproduction.
8. Fix the underlying issue.
9. Run the regression test and relevant suite.

Example:

```bash
pytest tests/test_math.py::test_add[2-3-10] -vv
```

This selects a node ID. `-k "2-3-10"` is a keyword substring expression and may select more than one test. If a fixture is missing, check spelling, decorator, visibility, and collection. If tests pass alone but fail together, inspect shared state, scope, cleanup, files, and DB state. Ask what invariant failed and what state caused it.

## 22. Complete realistic example: user registration

Application:

```python
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
    if not isinstance(email, str) or "@" not in email:
        raise RegistrationError("invalid email")
    return {
        "name": name,
        "age": age,
        "email": email,
        "status": "registered",
    }
```

Fixture:

```python
@pytest.fixture
def valid_payload():
    return {
        "name": "Alice",
        "age": 30,
        "email": "alice@example.com",
    }
```

Positive test asserts the returned name and registered status. Parametrize valid ages `[18, 19, 30, 120]` with IDs such as `minimum`, `above-minimum`, `typical`, `maximum-example`. Parametrize invalid fields and values (empty name, age as string, underage, invalid/missing email) with expected exception-message fragments. A `registration_log` yield fixture can open a file under `tmp_path` and close it in `finally`.

The architecture is fixture → arrange reusable dependencies → parametrized case → mutate only the relevant input → call application → assert success or expected exception. This demonstrates assertions, fixture, parametrization, IDs, exception checks, yield, and cleanup.

## 23. Mini-project: transaction validation test suite

Build a module that validates amount, currency, account status, and transaction type, returning a structured success result or raising a domain exception.

Suggested tree:

```text
transaction-validator/
├── src/
│   └── transaction_validator.py
└── tests/
    ├── conftest.py
    └── test_transaction_validator.py
```

Implementation:

```python
import math

class TransactionValidationError(Exception):
    pass

def validate_transaction(transaction):
    amount = transaction.get("amount")
    currency = transaction.get("currency")
    account_status = transaction.get("account_status")
    transaction_type = transaction.get("transaction_type")

    # bool is a subclass of int; reject it explicitly.
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        raise TransactionValidationError("amount must be numeric")
    if not math.isfinite(amount):
        raise TransactionValidationError("amount must be finite")
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

The `bool` check is necessary because `bool` subclasses `int`; otherwise `True` would pass a numeric type check. `math.isfinite` rejects NaN and positive/negative infinity. The fixture supplies a valid transaction. Parametrize invalid amount (0, -1, string, bool, NaN), unsupported currency, inactive account, and unsupported transaction type with readable IDs. Verify the success status and returned fields. Use a factory only if multiple customized records are needed; add a resource fixture only if persistence is introduced.

Intentionally introduce a wrong currency rule, broad mutable fixture, wrong parameter name, or wrong expected exception, then use pytest output to locate the defect. Possible extensions: focused helpers/factories, structured case objects, separate API/integration tests, and registered markers.

## 24. Interview and architecture knowledge

Be prepared to explain:
- pytest vs manual checks and unittest;
- assertion and assertion introspection;
- `pytest.raises` and stable exception contracts;
- behavioral assertions vs implementation coupling;
- fixture vs helper vs mock/fake;
- dependency injection and fixture resolution;
- yield setup/teardown;
- function/class/module/package/session scope;
- autouse and hidden dependencies;
- conftest visibility;
- factory fixtures;
- direct vs indirect parametrization and `request.param`;
- readable IDs and debugging a generated case;
- isolation, pollution, and cleanup;
- controlling combinatorial growth;
- markers vs parametrization;
- coverage vs test quality;
- test architecture for backend, DB, AI, and agents.

For large backends, separate unit/integration/E2E and place fixtures near their shared boundary. For expensive DB setup, reuse a safe client/schema while isolating mutable test data. Use session scope only for stable resources with a clear lifecycle. For AI apps, use deterministic configs, synthetic documents, controlled model responses, and tool clients. Test deterministic agent tool behavior independently of model natural-language variability.

## 25. Glossary and final mental model

- **pytest:** Python framework for discovery, execution, fixtures, parametrization, and reporting.
- **assertion:** executable expectation.
- **fixture:** pytest-managed setup/dependency.
- **scope:** fixture lifetime/reuse boundary.
- **dependency injection:** supplying dependencies from outside.
- **yield fixture:** fixture with setup before yield and teardown after.
- **autouse:** automatically applied fixture.
- **conftest.py:** pytest fixture/configuration sharing file.
- **parametrization:** same test logic over multiple data sets.
- **indirect parametrization:** case data passed through a fixture using `request.param`.
- **test ID:** readable label for a generated case.
- **test isolation:** independence from unrelated state.
- **deterministic/flaky:** repeatable / intermittent result.
- **regression test:** protects against a previously fixed defect.
- **coverage:** measurement of executed lines/branches.
- **boundary/negative test:** limit / invalid behavior test.
- **marker:** metadata used to categorize/select tests.

Remember:

```text
Assertions      → what correctness means
Fixtures        → how dependencies and resources are prepared
Parametrization → which cases are exercised
```

The combined flow is Arrange → Act → Assert. Fixtures often prepare Arrange; parametrization supplies input variations; application code performs Act; assertions and `pytest.raises` verify the result. This foundation supports unit, integration, API, data, ML, AI/LLM, agentic, and CI/CD testing.

---

# Part B — Roadmap and Current-Level Assessment

## 1. Where this lesson sits

This is Stage 1 → Module 07 — Testing and Systematic Debugging → Lesson 02. The preceding lesson, `01-test-levels-unit-integration-and-end-to-end.md`, introduced unit, integration, and end-to-end testing. The next lessons in the known module sequence are:

1. `03-arrange-act-assert-and-test-design.md`
2. `04-boundary-invalid-and-regression-tests.md`
3. `05-debuggers-breakpoints-and-call-stacks.md`
4. `06-tracebacks-logging-and-minimal-reproductions.md`
5. `07-mocking-and-test-doubles.md`

The wider Stage 1 roadmap progresses from computational thinking and Python core language, through control flow/functions/collections, files and CLI, then modules/packages/dependencies/code quality, before testing. Later stages cover OOP/data modelling, advanced Python, standard library, performance, packaging, internals, security, refactoring, and review.

## 2. Your current level and prerequisites

Completed learning before this lesson includes Python functions and parameters, control flow, collections, scope, pure functions and side effects, exceptions and validation, files/pathlib, CSV/JSON, encodings, argparse, streams/exit codes, logging, environment configuration, imports, package layout, `pyproject.toml`/`uv`, dependency management/SemVer, Ruff, type hints/type checking, documentation, and the Module 1.6 cumulative practice set. You have also completed Module 07 Lesson 01 on test levels.

That is a suitable base for this chapter. Your current level is beginner progressing toward intermediate Python engineering. This lesson introduces pytest-specific concepts that were not prerequisites: decorators at a basic level, fixture injection, fixture scopes, yield fixtures, parametrization, IDs, and indirect parametrization. The guide explains them from first principles.

**Learning boundary:** this guide completes Lesson 02 and its practice. It does not start Lesson 03 or introduce advanced mocking/debugger topics.

---

# Part C — All 20 Coding Exercises Solved

The solutions below follow the lesson's exercise order and use only the concepts taught in this lesson and earlier roadmap topics. Each code line is explained by its role.

## Level 1 — Basic

### Exercise 1 — Equality assertion

```python
def multiply(a, b):
    return a * b

def test_multiply():
    assert multiply(4, 5) == 20
```

- `multiply` returns the product of its two inputs.
- `test_multiply` is discovered because its name starts with `test_`.
- The assertion checks the exact result, not merely whether it is truthy.
- Common mistake: `assert multiply(4, 5)` would pass for many wrong non-zero values.

### Exercise 2 — Membership assertion

```python
def test_admin_role_present():
    roles = ["user", "admin"]
    assert "admin" in roles
```

- `roles` is the user's role list.
- `in` checks membership.
- The assertion verifies the required role without depending on its list index.

### Exercise 3 — `None`

```python
def find_user(user_id):
    return None

def test_missing_user_returns_none():
    assert find_user(999) is None
```

- The example function represents a missing lookup.
- The test passes only when the return value is exactly `None`.
- `is None` is preferred to `== None`.

### Exercise 4 — Expected exception

```python
import pytest

def parse_number(value):
    return int(value)

def test_parse_number_rejects_text():
    with pytest.raises(ValueError):
        parse_number("abc")
```

- `int("abc")` raises `ValueError`.
- `pytest.raises(ValueError)` tells pytest that this failure is expected.
- A different exception or no exception makes the test fail.

### Exercise 5 — Type assertion

```python
def build_id():
    return 100

def test_build_id_returns_int():
    assert isinstance(build_id(), int)
```

- `build_id()` produces the value.
- `isinstance` checks that it is an integer (or an instance of an integer subclass).
- Do not use `type(x) is int` unless subclasses must be rejected.

## Level 2 — Intermediate

### Exercise 6 — Basic fixture

```python
import pytest

@pytest.fixture
def user():
    return {"name": "Alice", "age": 30}

def test_user(user):
    assert user["name"] == "Alice"
    assert user["age"] == 30
```

- The decorator registers `user` as a fixture.
- The fixture returns a dictionary.
- The test requests it by the matching parameter name.
- Pytest injects the dictionary.
- The two assertions verify the name and age independently.

### Exercise 7 — Yield fixture

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

- `tmp_path` provides an isolated temporary directory.
- `/` builds the file path.
- `"w+"` opens the file for reading and writing, truncating/creating it.
- `yield` passes the open handle to the test.
- `seek(0)` moves the cursor to the beginning before reading.
- `finally` closes the file even if the test fails.

### Exercise 8 — Fixture dependency

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

- `database` creates an in-memory dictionary structure.
- `user(database)` requests the first fixture; pytest resolves it first.
- The user is appended to the database's users list.
- The test receives both fixture values and verifies membership.
- Do not call `database()` manually in the test.

### Exercise 9 — Single-value parametrization

```python
import pytest

@pytest.mark.parametrize("age", [18, 25, 40, 120])
def test_valid_age(age):
    assert 0 <= age <= 120
```

- The decorator supplies four values.
- Pytest runs the same test body once for each age.
- The assertion verifies the inclusive valid range.

### Exercise 10 — Readable parameter IDs

```python
import pytest
from user_registration import RegistrationError, register_user

@pytest.mark.parametrize(
    "email",
    ["", "alice", "alice.example.com"],
    ids=["empty", "missing-at", "dotted-no-at"],
)
def test_invalid_email(valid_payload, email):
    valid_payload["email"] = email
    with pytest.raises(RegistrationError, match="invalid email"):
        register_user(valid_payload)
```

- `email` receives one invalid value per generated test.
- `ids` labels the cases for readable failure output.
- `valid_payload` is the fixture from the realistic registration example.
- The test changes only the email field.
- `pytest.raises` verifies the domain exception and stable message fragment.
- IDs are labels, not assertions.

## Level 3 — Advanced

### Exercise 11 — Indirect parametrization

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

- The class stores a name and role.
- The fixture reads raw case data from `request.param`.
- `User(**request.param)` expands dictionary keys into constructor keyword arguments.
- `indirect=True` routes each dictionary through the fixture.
- The test receives a `User` object and checks its role is supported.

### Exercise 12 — Fixture factory

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

- The fixture returns a function, not one user.
- The lambda constructs a `User` for each supplied name.
- The test creates two independent objects and checks each name.
- Keep factories focused; do not turn them into general-purpose frameworks.

### Exercise 13 — Scope reasoning

**Answer: use function scope** for a shopping cart that tests intentionally mutate.

```python
@pytest.fixture
def cart():
    return []
```

- The fixture creates a new list for each test.
- One test's append/remove operations cannot leak into another.
- Session scope would share one mutable cart and create order-dependent tests.
- Performance alone is not a reason to widen scope.

### Exercise 14 — Fixture plus parametrization

```python
import pytest

@pytest.fixture
def transaction():
    return {
        "amount": 100,
        "currency": "INR",
        "account_status": "active",
        "transaction_type": "debit",
    }

@pytest.mark.parametrize("currency", ["INR", "USD", "EUR"])
def test_supported_currency(transaction, currency):
    transaction["currency"] = currency
    result = validate_transaction(transaction)
    assert result["status"] == "valid"
    assert result["currency"] == currency
```

- The fixture supplies all required baseline fields.
- Parametrization varies only the currency.
- The test updates the function-scoped fixture instance.
- `validate_transaction` is the mini-project function.
- Assertions verify successful status and the selected currency.

### Exercise 15 — Debug a wrong expected value

```python
@pytest.mark.parametrize(
    "a,b,expected",
    [(1, 2, 3), (2, 2, 4)],
)
def test_add(a, b, expected):
    assert add(a, b) == expected
```

- Each tuple supplies `a`, `b`, and expected output.
- `1 + 2` is 3; `2 + 2` is 4.
- The source's incorrect expected value `5` is a test-data bug.
- Correct the expectation; do not change a correct `add()` function to satisfy a wrong test.

## Level 4 — Production-oriented

### Exercise 16 — API validation matrix

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

- `CASES` separates data from test logic.
- Each tuple contains a payload and expected validity.
- IDs explain the reason for each case.
- `is` checks the boolean result explicitly.
- The application function `validate_payload()` is assumed to be provided by the exercise context.
- Keep unrelated response checks in separate tests.

### Exercise 17 — Factory with optional overrides

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

- The outer fixture returns an inner factory function.
- The dictionary contains default values.
- `**overrides` accepts selected keyword changes.
- `update` replaces only supplied fields.
- The test changes `active` and verifies the result.

### Exercise 18 — Database fixture lifecycle

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

- The connection is created during setup.
- `yield` supplies it to the test.
- `finally` closes it after the test, even after failure.
- `create_test_connection()` is an assumed project helper in this exercise.

### Exercise 19 — Control combinatorial growth

Three roles × four states × five regions = 60 cases. Adding four more dimensions/regions as shown by the source's example can multiply the matrix to 240. Do not generate every combination automatically.

Choose:
- representative equivalence classes;
- important boundaries;
- known failure modes;
- high-risk interactions;
- regression cases.

The aim is risk coverage, not the largest possible case count.

### Exercise 20 — AI application test boundary

Design the suite in layers:

1. Fixture supplies deterministic config, synthetic documents, controlled tool clients, and fixed model responses.
2. Unit tests verify deterministic prompt construction, parsing, schema validation, routing, argument validation, and tool behavior.
3. Integration tests verify real adapters against controlled services/sandboxes.
4. E2E tests cover a small number of representative user-request-to-result workflows.
5. Do not require every LLM answer to equal one exact sentence. Verify structured fields (`tool`, `user_id`, `amount`), schema, safety constraints, tool-call contract, and task-relevant behavior.
6. Keep model-quality evaluation separate from ordinary deterministic software tests.

---

# Part D — Debugging Lab: All Nine Cases

1. **Incorrect assertion:** `calculate_total([10, 20])` should be 30, not 40. Correct the expected value, not correct application code.
2. **Incorrect fixture shape:** fixture returns `None` but test indexes `user["name"]`. Return the expected dictionary/object.
3. **Wrong fixture scope:** module-scoped mutable list is shared. Use function scope when each test needs an empty list.
4. **Shared global dictionary:** fixture returns `DEFAULT_USER`; one test mutates it. Return a fresh dictionary per fixture instance.
5. **Missing fixture dependency:** `user(database)` requests a fixture not defined/visible. Define it in a visible location or correct the name.
6. **Incorrect parametrization:** two parameter names but only one supplied value. Make tuple length match parameter count.
7. **Wrong number of parameters:** two names but three values. Add a third name or remove the extra value.
8. **Incorrect expected exception:** test expects `TypeError`, but contract/function raises `ValueError`. Assert the correct exception.
9. **Missing cleanup:** connection fixture yields but never closes. Put `connection.close()` in teardown, preferably `finally`.

---

# Part E — Knowledge Check Answers

1. **Test vs test case:** test is the checking logic; test case is one concrete scenario/input set.
2. **Fixture vs helper:** pytest manages fixture injection, scope, caching, dependencies, and teardown; helper is explicitly called Python code.
3. **Broad scope risk:** mutable fixture instances may be shared and mutated across tests.
4. **Why 100% coverage is insufficient:** it measures execution, not whether assertions verify correctness.
5. **Exact error message fragility:** wording may change without changing contract semantics.
6. **`parametrize("a,b", [(1, 2, 3)])`:** two names but three values per case.
7. **Module-scoped config:** pytest reuses the fixture within the relevant module scope.
8. **`indirect=True`:** raw case value goes to the fixture through `request.param`.
9. **Tests pass individually but fail together:** inspect shared state, fixture scope, cleanup, environment variables, caches, paths, and database rows.
10. **Fixture not found:** spelling mismatch, missing decorator, wrong directory visibility, configuration/import issue, or fixture in the wrong subtree.
11. **Structured case objects:** use them when large tuples/dictionaries become hard to read and maintain.
12. **Separate tests vs parametrization:** split when scenarios require materially different setup, behavior, or assertions.

---

# Part F — Completion Checklist

- [x] Pytest purpose, installation, execution, discovery, and exit codes.
- [x] Assertions across common Python data types and assertion introspection.
- [x] Expected exceptions, exception details, message matching, and boundary checks.
- [x] Behavioral assertions and implementation coupling.
- [x] Fixture definition, injection, return values, yield, teardown, and cleanup.
- [x] All five fixture scopes and their trade-offs.
- [x] Isolation, fixture composition, autouse, conftest, and factories.
- [x] Parametrization, multiple/single values, IDs, indirect mode, and complex data.
- [x] Boundary test data, fixture/helper/mock distinctions, and common mistakes.
- [x] Lifecycle, markers, discovery, organization, production use, quality, coverage, debugging.
- [x] Realistic registration example and transaction-validation mini-project.
- [x] All 20 coding exercises and all 9 debugging-lab cases.
- [x] All 12 knowledge-check answers.
- [ ] Lesson 03 not started; awaiting your instruction.
