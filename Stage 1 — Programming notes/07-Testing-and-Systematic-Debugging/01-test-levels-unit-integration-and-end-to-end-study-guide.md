# Test Levels: Unit, Integration, and End-to-End — Study Guide

**Source:** `01-test-levels-unit-integration-and-end-to-end.md`  
**Position:** Stage 1 → Module 07 — Testing and Systematic Debugging → Lesson 01  
**Includes:** Complete lesson summary, roadmap/current-level assessment, all 16 coding exercises, six debugging cases, mini-project, and knowledge-check answers.

# Part A — Complete Lesson Summary

## 1. Software testing

Software testing deliberately runs code with known inputs and compares the actual result with an expected result. A test is a repeatable procedure that records whether the comparison passed or failed.

```python
def add(a, b):
    return a + b

assert add(2, 3) == 5
```

The basic sequence is **input → execute → observe → compare**. A **test case** is one concrete scenario: inputs, expected result, and checking logic. `add(2, 3) == 5` and `add(-1, 1) == 0` are different test cases.

- **Expected behavior:** what the specification says should happen.
- **Actual behavior:** what the program really does.
- **Pass:** actual and expected match for this case.
- **Failure:** the test ran, but the expectation was not met.
- **Error:** the test could not complete normally, for example because collection, import, fixture setup, an unexpected exception, or the environment prevented the check.

Testing replaces intuition and one-time manual checks with repeatable evidence.

## 2. Why test software?

Testing supports correctness, regression prevention, refactoring safety, maintainability, confidence, executable documentation, collaboration, and release safety.

A **regression** is previously correct behavior becoming incorrect after a later change. A **bug/defect** is incorrect software behavior.

```python
def apply_discount(price: float, percent: float) -> float:
    return price * (1 - percent / 100)

def test_apply_discount_twenty_percent():
    assert apply_discount(200.0, 20) == 160.0
```

If the implementation is changed to `return price - percent`, the test fails: the wrong result is 180. A weaker case such as `apply_discount(100, 10) == 90` would accidentally pass even with the bug. Test data must distinguish correct behavior from plausible incorrect behavior.

## 3. Testing versus debugging

- **Testing asks:** “Does the system behave as expected?” It detects a mismatch.
- **Debugging asks:** “Why is the system behaving incorrectly?” It investigates the root cause.

A failing test gives a reproducible symptom. Debugging traces the inputs and execution to find the cause. After the fix, rerunning the test confirms the correction. Testing and debugging are complementary, not interchangeable.

## 4. Test anatomy: Arrange–Act–Assert

```python
def test_apply_discount_ten_percent():
    # Arrange
    price = 100.0
    percent = 10

    # Act
    result = apply_discount(price, percent)

    # Assert
    assert result == 90.0
```

- **Arrange:** prepare inputs, objects, configuration, and state.
- **Act:** execute the behavior under test.
- **Assert:** compare actual behavior with the expected result.
- **Teardown/cleanup:** release temporary files, database rows, or other state created by setup.

Expected results should come from the specification or independent calculation, not from simply observing the implementation and copying its output.

## 5. Assertions

An assertion declares that a condition must be true. If false, Python raises `AssertionError`; pytest displays useful actual-versus-expected detail.

```python
assert add(2, 3) == 5
```

Weak:

```python
assert result is not None
```

Strong:

```python
assert result == 90.0
```

An assertion should verify the specific property the test claims to check. Python's `assert` is appropriate in tests, but not for mandatory runtime validation, authorization, or user-input checks: `python -O` can disable assertions. Use explicit exceptions such as `ValueError` in application code.

## 6. Test scope and the three levels

**Scope** is how much of the system a test executes.

1. **Unit test:** one function, method, small class, or cohesive piece of logic in isolation.
2. **Integration test:** components interacting across a meaningful boundary.
3. **End-to-end (E2E) test:** a complete representative workflow from external request/input to final observable result through the application.

Small-scope tests are usually fast and pinpoint failures. Large-scope tests are more realistic but slower, need more infrastructure, and can fail because of many layers. Select scope deliberately.

## 7. What is a unit?

A unit is not universally one function. It may be a function, method, small stateful class, or cohesive business rule spanning tightly related private helpers. The boundary depends on architecture. The important qualities are focus, speed, isolation, and determinism.

## 8. Unit testing

Unit testing checks one unit's behavior while controlling its dependencies. Strong unit tests are:

- **Fast:** normally milliseconds.
- **Isolated:** independent of other tests and external state.
- **Deterministic:** same inputs yield the same result every run.
- **Focused:** one behavior/scenario per test.
- **Repeatable:** stable across machines and times.
- **Readable:** the name and body make the behavior clear.

```python
def calculate_total(price: float, quantity: int) -> float:
    return price * quantity

def test_calculate_total():
    assert calculate_total(9.99, 3) == pytest.approx(29.97)
```

Use `pytest.approx` for floating-point calculations because binary floating-point cannot exactly represent many decimal fractions.

A focused invalid-input test:

```python
def test_apply_discount_rejects_negative_percent():
    with pytest.raises(ValueError):
        apply_discount(100.0, -5)
```

Avoid `test_everything()` combining unrelated discount, total, and addition behavior. Separate tests make failures diagnosable.

Unit tests are useful for business rules, transformations, calculations, validation, parsing, branches, and error handling. Test meaningful branches separately; a temperature classifier, for example, needs distinct freezing, cool, and warm cases.

## 9. First pytest test and discovery

```python
# calculator.py
def add(a: int, b: int) -> int:
    return a + b

# test_calculator.py
from calculator import add

def test_add():
    assert add(2, 3) == 5
```

Pytest recognizes test files named `test_*.py` or `*_test.py` and functions beginning with `test_`. These are naming conventions, not special Python syntax. Pytest imports the file, collects matching functions, and runs them.

```bash
uv run pytest
uv run pytest -q
uv run pytest path/to/test_file.py
uv run pytest path/to/test_file.py::test_name
```

A dot means a passing test; `F` means a failure. The summary reports counts and duration. Exit code `0` means success; non-zero means a failure or an error prevented successful execution. CI can use this exit code to gate later stages.

## 10. What unit tests should and should not test

Test logic: business rules, transformations, calculations, validation, parsing, branches, and exception behavior.

Avoid direct dependence on real databases, external APIs, network services, cloud services, and production infrastructure in ordinary unit tests. These make tests slower, expose them to shared state, transient outages, and changing external data. Real boundary behavior belongs in integration tests.

Dependencies differ:

| Dependency | Typical treatment |
|---|---|
| Pure function | Call directly |
| In-memory Python object/dict | Usually safe directly |
| Real filesystem | Integration test or controlled stand-in |
| Real database | Integration test |
| Real network/API | Integration test |
| Third-party service | Sandbox, realistic test double, or contract check |

## 11. Isolation and dependency doubles

Consider:

```python
def get_exchange_rate(client):
    response = client.fetch("/rates/USD")
    return response["rate"]
```

Calling a live exchange-rate service in a unit test makes the test slow, dependent on today's rate, and vulnerable to network failure. A unit test should verify that the function requests the intended path and extracts the returned rate—not whether the provider is online.

Three common **test doubles**:

- **Stub:** returns a fixed, predetermined value.
- **Fake:** has a simplified but working implementation, such as an in-memory dictionary repository.
- **Mock:** records how it was called so the test can inspect methods, arguments, or call count.

```python
class StubClient:
    def __init__(self):
        self.requested_paths = []

    def fetch(self, path: str) -> dict:
        self.requested_paths.append(path)
        return {"rate": 1.1}

def test_get_exchange_rate():
    client = StubClient()
    result = get_exchange_rate(client)
    assert result == 1.1
    assert client.requested_paths == ["/rates/USD"]
```

The assertions verify the extracted rate and requested endpoint. Recording the path makes this a lightweight mock-like double.

## 12. Unit-testing a service with dependencies

```python
class PaymentService:
    def __init__(self, repository, notifier):
        self._repository = repository
        self._notifier = notifier

    def process_payment(self, order_id: str, amount: float) -> str:
        if amount <= 0:
            raise ValueError("amount must be positive")
        payment_id = self._repository.save_payment(order_id, amount)
        self._notifier.send(order_id, f"Payment of {amount} received")
        return payment_id
```

Stub repository/notifier objects can record saved payments and sent messages. Test the returned payment ID, exact `(order_id, amount)` passed to persistence, and exact notification message. Also test that zero/negative amounts raise `ValueError`. This tests the service's own validation and orchestration, not whether a real database or email system works.

## 13. Over-mocking

Mocking is a tool, not an absolute good. Excessive mocking causes:

- **Brittle tests:** harmless internal refactoring breaks tests.
- **Implementation coupling:** tests assert how code is written rather than observable behavior.
- **False confidence:** mocks always return convenient values while the real repository, notifier, or client may be broken.

Mock genuine external dependencies to keep unit tests deterministic. Also write integration tests that exercise the real adapters. Do not mock every interaction everywhere.

## 14. Pure and impure code

A **pure function** returns the same output for the same inputs and has no observable external side effects:

```python
def calculate_total(price: float, quantity: int) -> float:
    return price * quantity
```

An **impure function** performs side effects or depends on external state:

```python
def save_order(order_id: str, total: float) -> None:
    database.execute(
        "INSERT INTO orders (id, total) VALUES (?, ?)", (order_id, total)
    )
```

Pure calculations, transformations, and validation are easy to unit-test. Persistence and network effects should be tested against real test dependencies at integration level. A unit test can still isolate an impure component's decision logic using a controlled dependency.

## 15. Integration testing and boundaries

Integration testing verifies components working together across a meaningful boundary. It answers questions a stubbed unit test cannot: does real SQL execute, does the schema match, does filesystem behavior work, and does an HTTP client send and parse real HTTP correctly?

Common boundaries:

- Application ↔ database.
- Application ↔ filesystem.
- Application ↔ API/HTTP service.
- Service ↔ queue/message broker.
- Pipeline ↔ object storage.

Example repository:

```python
class PaymentRepository:
    def __init__(self, connection):
        self._connection = connection

    def save_payment(self, order_id: str, amount: float) -> str:
        cursor = self._connection.execute(
            "INSERT INTO payments (order_id, amount) VALUES (?, ?)",
            (order_id, amount),
        )
        return str(cursor.lastrowid)

    def get_payment(self, payment_id: str):
        return self._connection.execute(
            "SELECT order_id, amount FROM payments WHERE id = ?",
            (payment_id,),
        ).fetchone()
```

An integration test uses real SQLite, creates the schema, saves a payment, retrieves it, and asserts the row. `sqlite3.connect(":memory:")` creates a real database engine instance that is fresh and disposable. A pytest fixture can `yield` the connection and close it afterward. Use Postgres/MySQL containers when engine-specific behavior matters and SQLite is not representative.

Filesystem example:

```python
def save_report(directory: Path, name: str, data: dict) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.json"
    path.write_text(json.dumps(data))
    return path

def load_report(path: Path) -> dict:
    return json.loads(path.read_text())
```

Use pytest's `tmp_path` to save then reload a report; assert the file exists and the dictionary round-trips. `tmp_path` is a fresh real temporary directory per test and is automatically cleaned up. This checks directory creation, path construction, JSON serialization, and filesystem behavior.

API integration example:

```python
class WeatherClient:
    def __init__(self, http_client, base_url: str):
        self._http_client = http_client
        self._base_url = base_url

    def get_temperature(self, city: str) -> float:
        response = self._http_client.get(f"{self._base_url}/weather/{city}")
        response.raise_for_status()
        return response.json()["temperature"]
```

Test against a local test server. Check the returned value is numeric and not boolean (`bool` is a subclass of `int`). If the API contract guarantees a decimal, normalize explicitly with `float(...)`; if the test server has a known fixture, assert the exact value. Integration tests can verify authentication, URL/method/payload, status handling, response parsing, and payload shape.

For third-party services, choices range from in-process mock, local fake/test server, provider sandbox, to live service. Prefer sandbox or realistic test service. Avoid ordinary tests calling production APIs: they may charge money, send messages, rate-limit, or fail for reasons outside your code. Contract-oriented tests verify assumptions about API shape without needing a live call every time.

## 16. End-to-end testing

An E2E test exercises a complete representative workflow through the real application layers, from request/input to final observable result. It catches wiring defects that isolated tests miss: incorrect request mapping, missing configuration, broken dependency injection, or mismatched API/service/repository expectations.

E2E tests are slow, costly, harder to diagnose, and need a running test environment. Use them for critical workflows such as registration, payment, or order placement—not every branch and invalid input. Detailed logic coverage belongs in unit tests; real boundary checks belong in integration tests.

| Aspect | Unit | Integration | E2E |
|---|---|---|---|
| Scope | One unit | Component boundary | Whole workflow |
| Dependencies | None/controlled | Real test dependencies | Full test stack |
| Speed | Fastest | Medium | Slowest |
| Realism | Lower | Real boundary | Real workflow |
| Infrastructure | Minimal | DB/filesystem/server | Running application |
| Diagnosis | Precise | Component/boundary | Broad/multi-layer |
| Maintenance | Usually low | Moderate | Highest |

One order feature can have a unit test for discount arithmetic, an integration test for repository persistence, and an E2E test for the HTTP request and final persisted total.

## 17. Test pyramid and alternatives

The **test pyramid** is a heuristic: many unit tests at the base, fewer integration tests in the middle, and fewer E2E tests at the top. It reflects speed, cost, feedback, and maintenance; it is not a law. Thin business logic with many service boundaries may need more integration tests; workflow-heavy products may justify selected E2E checks. Other models (testing trophy/honeycomb) emphasize different balances. Choose based on architecture and risk, not a fixed percentage.

## 18. Suites, organization, naming, fixtures, and test data

A **test suite** is a collection of tests. A **test layer** groups tests by scope. A maintainable layout:

```text
tests/
├── unit/
├── integration/
└── e2e/
```

Mirror source packages where useful. Pytest discovers files named `test_*.py` or `*_test.py` and functions starting with `test_`.

Prefer behavior-oriented names:

```python
def test_apply_discount_rejects_negative_percent():
    ...
```

A **fixture** is reusable setup and optional teardown requested by name:

```python
@pytest.fixture
def sample_cart():
    return [{"price": 10.0, "quantity": 2}]

def test_cart_total(sample_cart):
    assert calculate_cart_total(sample_cart) == 20.0

def test_cart_has_one_item(sample_cart):
    assert len(sample_cart) == 1
```

Fixtures can supply common objects, records, temporary directories, database connections, schemas, and cleanup. Keep fixture scope appropriate; fresh per-test state is often safest.

Test data categories:
- **Minimal:** smallest input demonstrating one behavior.
- **Realistic:** representative of normal production use.
- **Boundary:** values at or immediately around limits.
- **Invalid:** malformed/out-of-range values that must be rejected.

## 19. Isolation, determinism, flaky tests, and environments

Isolation means both that a unit test controls its external dependencies and that tests do not contaminate each other through shared files, database rows, globals, environment variables, or mutable fixtures.

A **deterministic test** produces the same result every run. Nondeterminism can come from current time, random values, network state, concurrency/scheduling, changing external data, or shared state. Control these sources: inject a fixed clock, seed randomness where appropriate, use known fixtures, generate unique IDs, isolate resources, and avoid uncontrolled network calls.

A **flaky test** intermittently passes and fails without code changes. Common causes:
- Real network calls or service-readiness races.
- Tests sharing rows/files or assuming execution order.
- Time boundaries such as midnight.
- Unseeded randomness.
- Concurrency/timing assumptions.
- Environment/configuration differences.

Do not simply rerun until green; investigate the cause.

Environments may be local, CI, staging, or production. Keep configuration explicit. Unit environments should be minimal/offline; integration environments should use disposable databases, temporary directories, or local test servers; E2E environments should run the full app with safe test credentials and data. Never use production secrets or destructive production data.

**Setup and teardown** create and clean resources. A pytest fixture's `yield` separates setup before the test from cleanup afterward. For database isolation use a fresh database/schema, transaction rollback, unique IDs, and reliable cleanup. Parallel runs must not share conflicting state.

## 20. E2E journeys, diagnosis, negative tests, and regression

Choose E2E journeys by business criticality: payment, registration, order placement, and other workflows where failure matters. Diagnose a failed E2E request by checking the request, application logs, layer inputs/outputs, configuration, and dependency health. Narrow the failing boundary before changing code.

Assertions should verify status, identifiers, totals, persisted state, and contract fields. For example:

```python
assert response.status_code == 201
assert response.json()["order_id"] is not None
assert response.json()["total"] == expected_total
```

`response is not None` is too weak: it may pass when the total is wrong.

- **Happy path:** ordinary valid use succeeds.
- **Negative test:** invalid input/prohibited operation is rejected.
- **Boundary test:** check values at and around limits, such as 0%, 100%, -1%, and 101%.
- **Regression test:** permanently captures a real bug so it cannot silently return.

For a discovered bug: reproduce it with a failing test, fix the code, rerun the same test, and keep the test permanently.

## 21. Coverage, quality, coupling, and behavior

**Coverage** measures the proportion of lines or branches executed. It does not prove meaningful verification: a line may execute while assertions check almost nothing. High coverage is not equivalent to high-quality tests.

Test quality depends on meaningful assertions, representative data, isolation, determinism, focused names, and whether the test catches plausible defects. **Test coupling** occurs when a test depends on internal implementation details. Prefer observable behavior over exact private method calls, helper names, or unnecessary call counts. A behavior-preserving refactor should not break tests.

Integration tests trade speed/maintenance for realism at boundaries. E2E tests cost even more for workflow confidence. Keep both deliberate and risk-based.

## 22. Test strategy and CI/CD

Plan by asking:
1. What business behavior matters most?
2. Which logic is pure and unit-testable?
3. What are the real integration boundaries?
4. Which workflows justify E2E?
5. What failures would be most costly?
6. What is the cheapest reliable check for each risk?

A sensible CI pipeline:

```text
code
  ↓
uv sync --locked
  ↓
Ruff format/lint checks
  ↓
type checking
  ↓
unit tests
  ↓
integration tests
  ↓
E2E tests
  ↓
build/deploy
```

`uv sync --locked` requires the committed lock file to be current and prevents CI silently changing dependency resolution. Run fast, cheap, high-signal checks before expensive ones. Failures should gate later stages. Exact ordering and parallelization can vary.

A common frequency strategy is unit tests on every push, integration tests on every PR, and E2E on merge/nightly. Some projects can run every layer on each PR; decide from runtime, infrastructure cost, and risk. Preserve logs/reports as CI artifacts to support diagnosis.

## 23. Backend, data pipeline, ML, AI, and agentic systems

For backend services: unit-test validation, calculations, and service orchestration with controlled repositories/notifiers; integration-test repository SQL and real database behavior; E2E-test critical HTTP request-to-persisted-result journeys.

For data pipelines:
- Unit-test parsing, schema validation, normalization, filtering, aggregation, and transformation using fixed records.
- Integration-test filesystem, database, object storage, or queue interactions against real test destinations.
- E2E-test the complete input-to-output pipeline when the workflow is critical.
Verify schema, row counts, values, rejected records, and persisted output at the correct level.

For ML systems, separate software correctness from model quality:
- Software tests verify preprocessing, feature construction, request/response validation, wrappers, serialization, error handling, and service integration.
- Model evaluation measures prediction/task quality with appropriate datasets and metrics.
For an inference service, unit-test preprocessing/wrapper code with fixed fixtures or a fake model; integration-test serving/API boundaries; E2E-test the full request/response path. Model-quality evaluation is separate.

For AI applications, unit-test deterministic prompt construction, parsing, validation, routing, and response handling. Use fixed model-response fixtures for software tests and sandbox/controlled servers for provider integration.

For agents, separate planner/orchestration, tool selection/argument construction, tool execution/adapters, and final response construction. Unit-test deterministic parts; integration-test real tool adapters; E2E-test representative user-request-to-result journeys. Since model output is nondeterministic, avoid exact-string assertions. Assert stable properties: required fields, valid structure, tool constraints, and task-relevant outcomes. A successful HTTP status does not prove the agent produced a correct result.

## 24. Contracts, production checks, smoke tests, maintenance

**Contract testing** records what one service expects from another—request/response shape, fields, types, and status behavior—and checks those assumptions independently without a live provider call on every run.

Production testing must be safe, narrow, observable, and non-destructive. Avoid real charges, real customer messages, destructive data mutation, or secret exposure. Use test accounts, sandboxes, read-only checks, and safeguards.

A **smoke test** is a small, fast, safe post-deployment check that the system is not catastrophically broken (health endpoint, critical dependency connectivity, harmless representative request). It does not replace the full test suite.

Tests are code and need maintenance: remove obsolete tests, update expectations when specifications change, keep regression tests, investigate flaky tests, and keep the suite fast. Avoid unnecessary infrastructure, use safe fixtures, parallelize only when isolation permits, and select appropriate CI layers.

Common beginner mistakes: testing implementation rather than behavior; weak assertions; live network calls in unit tests; over-mocking; shared mutable data; relying on test order; missing cleanup; uncontrolled time/randomness; one giant test/file; treating coverage as proof; using E2E for every branch; confusing model evaluation with software testing.

## 25. Illustrative order project and mini-project

The source's illustrative structure:

```text
src/orders/
    service.py
tests/
    unit/test_service.py
    integration/test_repository.py
    e2e/test_order_workflow.py
```

The service contains business behavior; unit tests use a stub repository; integration tests use a disposable real database; E2E tests send a request through the running application and check the final result.

The lesson's “Apply Discount to Order” code:

```python
def apply_discount(price: float, percent: float) -> float:
    if not (0 <= percent <= 100):
        raise ValueError("percent must be between 0 and 100")
    return price * (1 - percent / 100)

class OrderService:
    def __init__(self, repository):
        self._repository = repository

    def apply_order_discount(self, order_id: str, percent: float) -> float:
        order = self._repository.get_order(order_id)
        discounted_total = apply_discount(order.total, percent)
        self._repository.update_total(order_id, discounted_total)
        return discounted_total
```

Design:
- **Unit:** test arithmetic for ordinary, boundary (0 and 100), and invalid (-1 and 101) percentages; test service orchestration with a stub repository.
- **Integration:** test `OrderRepository.update_total` against a real disposable SQLite database and verify persistence.
- **E2E:** send `PATCH /orders/{id}/discount` to the running test app and verify returned and persisted totals.
- **Fixtures:** `sample_order` and `test_database`.
- **Configuration:** test-only database URL/default, never production credentials.
- **CI:** unit on push, integration on PR, E2E on merge (adapt to cost and risk).

## 26. Interview/architecture concepts

Be ready to explain test/assertion, unit versus integration versus E2E, isolation, stubs/fakes/mocks, over-mocking, flaky-test causes, the pyramid as a heuristic, strategy by risk, disposable databases, API sandboxes, CI order, and behavior versus implementation.

For large repositories, organize by level and mirror source structure. Use disposable fixtures. Select E2E tests by business criticality. For AI providers, use fixed fixtures for unit tests, sandbox integration, and a small set of live smoke/E2E checks with behavioral assertions. For agents, test deterministic orchestration separately from real adapters and nondeterministic model responses.

## 27. Glossary and mental model

- **Test:** executable comparison of actual and expected behavior.
- **Test case:** one input/expectation scenario.
- **Assertion:** condition that must hold.
- **Unit / integration / E2E:** isolated logic / real component boundary / complete workflow.
- **Test suite:** collection of tests; **test layer:** grouping by scope.
- **Fixture:** reusable setup and teardown.
- **Stub / fake / mock:** fixed response / simplified working implementation / call-recording stand-in.
- **Test double:** umbrella term for stand-ins.
- **Isolation:** independence from external or shared state.
- **Deterministic / flaky:** same result each run / intermittent pass and fail without code change.
- **Regression test:** permanent check for a previously discovered bug.
- **Coverage:** measured executed lines or branches.
- **Smoke test:** quick safe post-deployment health check.
- **Contract:** recorded expectation between services.
- **CI/CD:** automated integration/deployment pipeline.

Final mental model: **Does this logic work?** (unit); **do these components really work together?** (integration); **does the complete critical workflow work?** (E2E). Testing detects incorrect behavior; debugging finds its cause. Choose the cheapest test level that genuinely verifies the risk.

---

# Part B — Project-Tree and Current-Level Assessment

## Roadmap position

This lesson is **Stage 1 — Programming & Computational Thinking → Module 07 — Testing and Systematic Debugging → Lesson 01**.

Known Module 07 sequence:

1. `01-test-levels-unit-integration-and-end-to-end.md` — current.
2. `02-pytest-assertions-fixtures-and-parametrization.md`
3. `03-arrange-act-assert-and-test-design.md`
4. `04-boundary-invalid-and-regression-tests.md`
5. `05-debuggers-breakpoints-and-call-stacks.md`
6. `06-tracebacks-logging-and-minimal-reproductions.md`
7. `07-mocking-and-test-doubles.md`
8. `README.md` and `practice-questions.md`.

The wider Stage 1 tree builds from computational thinking and Python fundamentals through control flow, collections/algorithms, files/structured data/CLI, and modules/packages/dependencies/code quality before testing. Later modules cover OOP/data modelling, advanced Python, standard library, binary/text processing, modern language features, advanced testing, performance, packaging, internals, design patterns, visualization, security, refactoring/review, and gap lessons.

## Current-level assessment

Your completed work before this lesson includes functions and return values, scope, pure functions and side effects, exceptions/validation, lists/dictionaries/sets, algorithms, file handling, pathlib, CSV, JSON, encodings, argparse, streams/exit codes, logging, environment configuration, imports, package layout, `pyproject.toml`/`uv`, dependency management/SemVer, Ruff, type hints/type checking, and documentation. You have also completed the Module 1.6 cumulative practice set.

This is a suitable prerequisite base. Your current level is beginner progressing toward intermediate Python engineering. You have the foundations needed for pytest tests, basic fixtures, constructor-injected dependencies, temporary paths, SQLite, and layered project structure.

**What this lesson adds:** systematic testing and test-level selection. It does not yet make you advanced in pytest parametrization, fixture architecture, mocking APIs, debugger use, or test architecture; those are separate Module 07 lessons.

**Scope discipline:** solutions use concepts already introduced in the course: Python functions/classes/imports, pytest, pathlib, JSON, SQLite, `uv`, Ruff, and type hints. No unrelated frameworks are introduced.

---

# Part C — All 16 Coding Exercises with Line-by-Line Explanations

## Level 1 — Basic

### 1. Unit test for `square`

```python
def square(n: int) -> int:
    return n * n

def test_square():
    assert square(4) == 16
```

- `square` multiplies its input by itself.
- `test_square` starts with `test_`, so pytest discovers it.
- `square(4)` executes the function.
- `assert` checks that the result is exactly 16.
- It is a unit test: pure logic, no external dependency.

### 2. Classify test levels

- `calculate_total([...])` directly: **unit** — one calculation in isolation.
- `OrderRepository.save_order` against a real database: **integration** — repository/database boundary.
- Full `POST /orders` request through the application: **E2E** — complete request workflow.

Scope determines the level, not the test's name.

### 3. Assertion for a 50% discount

```python
assert apply_discount(50.0, 50) == 25.0
```

The function receives a price of 50 and discount of 50 percent. The assertion checks the exact expected result, 25, rather than merely checking that a value exists.

### 4. Happy and invalid age cases

```python
import pytest

def validate_age(age: int) -> None:
    if age < 0:
        raise ValueError("age cannot be negative")

def test_validate_age_accepts_valid_age():
    validate_age(30)

def test_validate_age_rejects_negative_age():
    with pytest.raises(ValueError):
        validate_age(-1)
```

- The first test passes if age 30 does not raise.
- `pytest.raises(ValueError)` declares that the invalid call must raise that exception.
- Separate tests make each behavior independently diagnosable.

## Level 2 — Moderate

### 5. Unit-test a service with a stub repository

```python
class StubOrderRepository:
    def __init__(self):
        self.saved_orders = []

    def save_order(self, customer_id, items, total):
        self.saved_orders.append((customer_id, items, total))
        return "order-123"

class OrderService:
    def __init__(self, repository):
        self._repository = repository

    def create_order(self, customer_id, items):
        total = sum(item["price"] * item["quantity"] for item in items)
        return self._repository.save_order(customer_id, items, total)

def test_create_order_passes_correct_total():
    repository = StubOrderRepository()
    service = OrderService(repository)
    items = [{"price": 10.0, "quantity": 2}, {"price": 5.0, "quantity": 1}]

    order_id = service.create_order(7, items)

    assert order_id == "order-123"
    assert repository.saved_orders[0][0] == 7
    assert repository.saved_orders[0][2] == 25.0
```

- The stub records the call instead of writing to a real database.
- The service receives the repository through its constructor.
- The total is `10 × 2 + 5 × 1 = 25`.
- The test checks returned ID, customer ID, and total passed to persistence.
- It verifies service logic, not real database behavior.

### 6. SQLite integration test

```python
import sqlite3
import pytest

class OrderRepository:
    def __init__(self, connection):
        self._connection = connection

    def save_order(self, customer_id, total):
        cursor = self._connection.execute(
            "INSERT INTO orders (customer_id, total) VALUES (?, ?)",
            (customer_id, total),
        )
        return str(cursor.lastrowid)

    def get_order(self, order_id):
        return self._connection.execute(
            "SELECT customer_id, total FROM orders WHERE id = ?",
            (order_id,),
        ).fetchone()

@pytest.fixture
def test_database():
    connection = sqlite3.connect(":memory:")
    connection.execute(
        "CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER, total REAL)"
    )
    yield connection
    connection.close()

def test_save_and_get_order(test_database):
    repository = OrderRepository(test_database)
    order_id = repository.save_order(7, 25.0)
    saved_order = repository.get_order(order_id)
    assert saved_order == (7, 25.0)
```

- `:memory:` creates a real in-memory SQLite database.
- The fixture creates the table before yielding the connection.
- The repository executes actual SQL to insert and select.
- The assertion verifies the retrieved customer and total.
- `connection.close()` runs during fixture teardown.
- This is integration testing because real SQL executes against a database engine.

### 7. Fixture used by two tests

```python
import pytest

@pytest.fixture
def sample_cart():
    return [
        {"price": 10.0, "quantity": 2},
        {"price": 5.0, "quantity": 1},
    ]

def calculate_cart_total(items):
    return sum(item["price"] * item["quantity"] for item in items)

def test_cart_total(sample_cart):
    assert calculate_cart_total(sample_cart) == 25.0

def test_cart_item_count(sample_cart):
    assert len(sample_cart) == 2
```

- Pytest sees the `sample_cart` parameter and supplies the fixture.
- Both tests use the same defined sample shape.
- The fixture removes duplicated setup; default function scope gives each test a fresh result.

### 8. Filesystem integration with `tmp_path`

```python
import json

def save_report(directory, name, data):
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path

def load_report(path):
    return json.loads(path.read_text(encoding="utf-8"))

def test_save_and_load_report(tmp_path):
    data = {"total": 100, "items": 3}
    report_path = save_report(tmp_path / "reports", "summary", data)
    loaded = load_report(report_path)
    assert report_path.exists()
    assert loaded == data
```

- `tmp_path` is a fresh temporary directory managed by pytest.
- `mkdir` creates the reports directory.
- `/` joins path components portably.
- `json.dumps` converts the dictionary to JSON text; `write_text` writes it.
- `read_text` reads it; `json.loads` converts it back to a dictionary.
- Assertions verify file existence and correct round-trip data.
- The test uses real filesystem behavior without touching production files.

## Level 3 — Hard

### 9. User-registration test strategy

- **Unit:** test email format, password strength, and other deterministic validation rules independently.
- **Integration:** test the repository against a disposable real test database; save a user and retrieve the correct fields.
- **E2E:** send `POST /register` through the running application and verify response and confirmation workflow.
- **Reason:** validation is isolated logic; persistence is a database boundary; registration is a critical business workflow.

### 10. Diagnose “connection refused”

- If intended as a **unit test**, remove the real network dependency and use a stub/fake.
- If intended as an **integration test**, start a controlled test server, verify readiness, set timeouts, and classify the test correctly.
- Investigate service availability, startup timing, configuration, and network errors. Do not blindly rerun until green.

### 11. Reorganize a mixed test file

```text
tests/
├── unit/
│   ├── test_discount.py
│   └── test_validation.py
├── integration/
│   ├── test_order_repository.py
│   └── test_file_processor.py
└── e2e/
    └── test_order_workflow.py
```

Move tests according to actual scope: isolated logic, a real component boundary, or a complete workflow. CI and developers can then select a layer independently.

### 12. Replace a weak API assertion

```python
assert response.status_code == 201
assert response.json()["order_id"] is not None
assert response.json()["total"] == expected_total
```

- First line checks successful creation.
- Second checks the response identifies the created order.
- Third checks the business result.
- These verify meaningful behavior, unlike `response is not None`.

## Level 4 — Advanced

### 13. Production backend test architecture

- Unit-test business rules and calculations with no external dependencies; run on every push/PR.
- Integration-test repository/database, filesystem, queue, and API boundaries using disposable infrastructure; run on PRs.
- E2E-test a small set of critical customer journeys; run on merge/nightly or every PR if affordable.
- CI: locked dependency sync → Ruff → type checking → unit → integration → E2E.
- Save logs and reports as CI artifacts.
- Weight effort by business cost of an undetected defect.

### 14. CI stages in order

```text
1. uv sync --locked
2. Ruff format/lint checks
3. Type checker
4. Unit tests
5. Integration tests
6. E2E tests
7. Build/deploy
```

`uv sync --locked` installs reviewed dependency versions and fails if the lock file is stale. Ruff/type checks are cheap. Unit tests are the fastest layer. Integration and E2E require more infrastructure and time. Fast checks first give early feedback and prevent spending on later stages after an obvious failure. Each stage should gate the next.

### 15. Data pipeline testing

- **Unit:** parse, validate schema, normalize, and transform fixed records.
- **Integration:** write to a real disposable storage destination and read the result back.
- **E2E:** run test input through the full pipeline to final test storage when the workflow is critical.
- Verify schema, row counts, values, rejected records, and persistence.
- Do not mock storage in a test intended to prove storage works.

### 16. Agentic AI workflow testing

- **Unit:** fixed-input tests for deterministic prompt construction, rule-based tool selection, argument validation, response parsing, and schema checks.
- **Integration:** test real tool adapters against controlled services/sandboxes; verify auth, request/response shape, and errors.
- **E2E:** test representative user request → planner → tool selection → tool execution → final response.
- Avoid exact model-generated sentence matching. Assert required fields, valid structure, tool constraints, and task-relevant behavior.
- Keep model-quality evaluation separate from software tests.

---

# Part D — Debugging Lab: All Six Cases

1. **Wrong expected value:** 10% off 100 is 90, not 91. Correct the test expectation using the specification or independent arithmetic; do not alter correct code to satisfy a wrong test.
2. **Missing database table:** `no such table: orders` means fixture setup is incomplete. Add `CREATE TABLE orders ...` before yielding the connection.
3. **E2E 500 instead of 201:** inspect logs across API/service/repository. The example API passes a plain list while service expects dictionaries with `price` and `quantity`. Fix request parsing and keep the test as regression protection.
4. **Test-data contamination:** two tests assume customer ID 1 in shared DB state. Generate unique IDs and use fresh fixtures/cleanup.
5. **Time-related flake:** code and test independently call `datetime.now()`; midnight may occur between calls. Inject a fixed clock/time.
6. **Weak assertion:** `response is not None` misses an incorrect total. Assert status, ID, total, and other important response fields.

---

# Part E — Mini-Project: Apply Discount to Order

## Test plan

| Layer | Target | Dependency | Required checks |
|---|---|---|---|
| Unit | `apply_discount` | None | Normal, 0%, 100%, -1%, 101% |
| Unit | `OrderService.apply_order_discount` | Stub repository | Correct lookup, calculation, update, return |
| Integration | `OrderRepository.update_total` | Disposable SQLite DB | Updated total persists |
| E2E | `PATCH /orders/{id}/discount` | Running test application | Response and persisted total correct |

Suggested structure:

```text
tests/
├── unit/
│   ├── test_discount.py
│   └── test_order_service.py
├── integration/
│   └── test_order_repository.py
└── e2e/
    └── test_apply_discount_workflow.py
```

Acceptance criteria:
- Invalid percentages raise `ValueError`.
- 0% leaves total unchanged; 100% produces zero.
- Service passes correct order ID and discounted total to repository.
- Integration proves real SQL persistence.
- E2E proves the request reaches persistence and returns the correct outcome.
- Fixtures are fresh/disposable; configuration uses test-only credentials.
- CI runs cheap deterministic checks before expensive tests.

---

# Part F — Knowledge Check Answers

1. A test is an executable check; a test case is its particular input/expectation scenario.
2. Input, execution, observation, comparison.
3. Testing detects incorrect behavior; debugging finds why.
4. Arrange, Act, Assert.
5. Strong assertions check specific expected behavior; weak ones check only broad existence.
6. Unit boundaries depend on architecture and cohesive behavior.
7. Fast, isolated, deterministic, focused, repeatable, readable (any three).
8. Real databases, live APIs, networks, cloud services, production infrastructure.
9. Stub returns fixed data; fake has simplified working behavior; mock records calls.
10. Excessive mocking couples tests to internals and hides real integration defects.
11. Pure functions have no external side effects; impure functions perform or depend on external effects/state.
12. Integration tests verify real interactions with dependencies.
13. Database, filesystem, API, queue, object storage (any three).
14. E2E verifies the complete wired workflow from request to final result.
15. No; the pyramid is a heuristic adapted to architecture and risk.
16. Suite is a collection; layer groups tests by scope.
17. Behavior-focused names make failures understandable immediately.
18. Fixture is reusable setup/teardown requested by a test.
19. Minimal isolates a case; realistic resembles normal use; boundary tests limits; invalid data should be rejected.
20. Tests do not affect one another through shared mutable state.
21. Deterministic means same result each run; time, randomness, network, concurrency, and shared state can break it.
22. Flaky means intermittent pass/fail without code changes; blind retries hide problems.
23. Regression test permanently protects behavior after a bug is found.
24. Coverage measures execution, not meaningful correctness verification.
25. Behavior testing checks observable outcomes; implementation testing checks internals and creates fragile coupling.
26. E2E is expensive, so prioritize critical workflows.
27. Fast checks provide early feedback before expensive stages.
28. Software tests verify surrounding code; model evaluation measures prediction/task quality.
29. LLM output is nondeterministic; behavioral assertions are more robust than exact strings.
30. Smoke test is a small safe post-deployment check, not a replacement for the full suite.

---

# Completion Checklist

- [x] All lesson topics summarized.
- [x] Core code patterns and examples explained.
- [x] Roadmap position and current-level assessment included.
- [x] All 16 coding exercises solved.
- [x] All six debugging-lab cases addressed.
- [x] Mini-project test architecture designed.
- [x] All 30 knowledge checks answered.
- [ ] Next lesson not started; waiting for your instruction.
