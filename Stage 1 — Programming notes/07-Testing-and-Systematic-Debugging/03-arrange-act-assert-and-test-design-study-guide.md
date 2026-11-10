# Arrange–Act–Assert and Test Design
## Complete Lesson Summary, Roadmap Assessment, and Exercise Solutions

**Roadmap:** Stage 1 — Programming & Computational Thinking  
**Module:** 07 — Testing and Systematic Debugging  
**Lesson:** 03 — Arrange–Act–Assert and Test Design  
**Source:** `03-arrange-act-assert-and-test-design(1).md`

---

# Part A — Complete Lesson Summary

## 1. Test design: deciding what deserves a test

Software testing checks whether software behaves as intended. A **test** is a repeatable check; a **test case** is one concrete scenario containing a starting condition/input, expected behavior, and an observable way to verify it. **Test design** is the engineering process of deciding what to test, why it matters, which scenarios are representative, and what result would reveal a defect. Writing pytest code is only the implementation of that design.

Consider:

```python
def multiply(a: int, b: int) -> int:
    return a * b

def test_multiply():
    result = multiply(2, 3)
    assert result == 6
```

The test checks the product, not merely that a result exists. A weak test such as `assert result is not None` would pass for many incorrect values.

More tests do not automatically mean better testing. Ten tests exercising the same path may protect less than four carefully selected cases covering distinct behaviors. Begin with requirements, then derive behavior, scenarios, expected outcomes, and finally test code:

```text
Requirement → Behavior → Scenarios → Expected outcomes → Test implementation
```

For a bank rule saying a customer cannot withdraw more than their balance, useful cases include a normal withdrawal, exact-balance withdrawal, overdraw, zero, negative amount, and invalid text such as `"abc"`. The cases come from business reasoning, not pytest syntax.

## 2. Behavior verification and observable outcomes

A behavior-oriented test verifies what a component does from the outside:

```text
Input / Starting State → Behavior → Observable Outcome
```

Observable outcomes include return values, exceptions, state changes, persisted data, emitted events, HTTP responses, created/updated files, messages, and externally visible interactions.

Example: if `validate_email()` must reject an address without `@`, define the contract and test it:

```python
import pytest

def validate_email(value: str) -> str:
    if "@" not in value:
        raise ValueError("invalid email")
    return value

def test_validate_email_rejects_missing_at_symbol():
    with pytest.raises(ValueError, match="invalid email"):
        validate_email("alice.example.com")
```

For `POST /users`, the observable contract might include HTTP 201 for valid input, HTTP 400 for malformed input, a database record, duplicate-email rejection, and an event after successful creation. These may deserve separate tests at different layers. Avoid testing private variables when a public outcome exists; do test side effects when they are explicitly part of the requirement.

Behavior tests generally survive refactoring better because internal implementation can change while the public contract remains stable.

## 3. Arrange–Act–Assert (AAA)

AAA is a mental and structural model for organizing a test:

- **Arrange:** prepare inputs, initial state, dependencies, configuration, resources, and test data.
- **Act:** perform the primary behavior under test.
- **Assert:** verify the observable result or contract.

```python
def add(a: int, b: int) -> int:
    return a + b

def test_add_returns_sum():
    # Arrange
    a = 2
    b = 3

    # Act
    result = add(a, b)

    # Assert
    assert result == 5
```

The first two assignments establish the scenario; `add(a, b)` executes the behavior; the assertion checks the expected result.

AAA is not a rule that a test must contain exactly three statements. Arrange can include several values and dependencies; Assert can contain several related checks. AAA improves readability, debugging, code review, maintenance, consistency, and failure diagnosis. It does not make a test correct automatically: `assert result is not None` is weak even when placed in a perfect AAA structure.

A bank example:

```python
def test_withdraw_reduces_balance():
    # Arrange
    account = BankAccount(balance=500)

    # Act
    account.withdraw(100)

    # Assert
    assert account.balance == 400
```

A test can use fixtures for setup and separate teardown, keeping the business behavior visible.

## 4. Arrange in detail: minimum meaningful starting state

Arrange establishes the conditions needed for the behavior. It may include input values, objects, fixtures, configuration, database state, temporary files, environment variables, controlled external dependencies, and initial state.

Example: an expired subscription must not download premium content. Arrange an expired subscription and premium resource; Act by checking download permission; Assert that permission is false:

```python
def test_expired_subscription_cannot_download():
    # Arrange
    subscription_status = "expired"
    resource_type = "premium"

    # Act
    allowed = can_download(subscription_status, resource_type)

    # Assert
    assert allowed is False
```

A fixture can create an object used in Arrange:

```python
import pytest

class User:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

@pytest.fixture
def user():
    return User(name="Alice", age=30)

def test_user_name(user):
    # Arrange
    expected_name = "Alice"

    # Act
    actual_name = user.name

    # Assert
    assert actual_name == expected_name
```

Conceptually, fixture construction supports Arrange; operationally, pytest resolves the fixture before executing the test body. Distinguish **test data** (e.g. `price = 100`, `quantity = 2`) from **test infrastructure** (database connection, temporary directory, API client, app instance, test clock). Use fixtures for reusable dependencies and lifecycle management; keep scenario-specific inputs visible where that improves understanding.

Avoid huge object graphs, real external infrastructure in a unit test, hidden important inputs, and fixtures that contain the whole scenario. Ask: “What is the minimum meaningful starting state?” Prefer necessary setup over maximum setup.

## 5. Act in detail: make the target behavior visible

Act is the primary operation being tested: `calculate_total(cart)`, `register_user(payload)`, `client.get("/users/1")`, or `process_payment(transaction)`.

If the requirement is “a withdrawal greater than the balance is rejected,” the Act is `account.withdraw(501)`. A test with unrelated actions such as create user, login, create order, cancel order, and refund order may be multiple tests bundled together. Split distinct behaviors into focused tests.

“One Act” is a useful default, not a universal law. An integration or E2E test can have a coherent sequence of steps. The question is whether the steps form one logical workflow or combine unrelated behaviors. If the Act is difficult to identify, the test may be too broad, setup too complicated, or the behavior boundary unclear.

## 6. Assert in detail: strong, precise evidence

Assertions can verify return values, state, exceptions, persisted records, response status/body, side effects, and invariants.

Weak:

```python
assert result
assert response is not None
```

Stronger when these are the contract:

```python
assert result.status == "approved"
assert response.status_code == 201
assert response.json()["id"] > 0
```

An assertion should be specific enough to catch meaningful defects but not more specific than the contract. Avoid asserting private object dictionaries, generated timestamps, incidental ordering, or formatting that is not guaranteed.

Multiple related assertions can establish one behavior:

```python
def test_successful_registration_returns_created_user():
    user = register_user({"name": "Alice", "email": "alice@example.com"})
    assert user.name == "Alice"
    assert user.email == "alice@example.com"
```

These jointly verify the created user. Registration, password reset, billing, and report generation are distinct behaviors and normally should not share one test.

Expected exceptions are assertions too:

```python
with pytest.raises(ValueError):
    parse_amount("abc")
```

The call inside the context manager is the Act; the expected exception is the verification. Ask: “What defect would this assertion catch?” If the answer is “almost none,” strengthen it.

## 7. One coherent behavior per test

“One behavior per test” does not mean one assertion or one function call. It means one logically coherent scenario.

A successful transfer can appropriately assert both balances:

```python
def test_successful_transfer_updates_both_accounts():
    sender = BankAccount(balance=500)
    receiver = BankAccount(balance=100)

    transfer(sender, receiver, 200)

    assert sender.balance == 300
    assert receiver.balance == 300
```

Both assertions jointly prove that funds moved correctly. A test that registers, logs in, creates an order, cancels it, and refunds it combines distinct behaviors.

Do not split so aggressively that a cohesive construction contract becomes hard to understand. Use behavioral cohesion, not a rigid assertion count.

## 8. Fixtures and parametrization in AAA

Fixtures commonly support Arrange by supplying reusable dependencies/resources. Avoid fixtures that create a user, seed a database, create an order, activate a subscription, configure payment, and hide all scenario decisions. A fixture should answer “what reusable dependency/resource is needed?” A helper often answers “what transformation should happen to this test data?”

Parametrization works when behavior and assertion shape remain the same but inputs vary:

```python
import pytest

def calculate_total(price: int, quantity: int) -> int:
    return price * quantity

@pytest.mark.parametrize(
    "price,quantity,expected",
    [(10, 2, 20), (25, 4, 100), (7, 0, 0)],
)
def test_calculate_total(price, quantity, expected):
    # Arrange: parameter values establish the scenario.
    # Act
    result = calculate_total(price, quantity)
    # Assert
    assert result == expected
```

The parameters are the Arrange data. Use separate functions when setup, behavior, or assertions differ substantially.

## 9. Deriving test cases from requirements

Use a repeatable process:

```text
Requirement
→ identify behavior
→ identify inputs and starting state
→ define expected outcomes
→ identify failure modes
→ identify boundaries
→ identify state transitions
→ select representative cases
→ implement AAA
```

For a transfer rule (“cannot transfer more than available balance”), inputs include sender, receiver, and amount. Valid outcomes update both balances; invalid outcomes reject and leave both balances unchanged. Consider normal transfer, exact balance, amount above balance, zero, negative amount, same account, and unknown recipient.

A case table makes design explicit:

| Scenario | Starting state/action | Expected result |
|---|---|---|
| Normal | sender 500, receiver 100, transfer 200 | balances 300 and 300 |
| Exact | sender 500, transfer 500 | sender becomes 0 |
| Over | sender 500, transfer 501 | error; no balance changes |
| Zero | transfer 0 | domain-defined rejection |
| Negative | transfer -1 | validation error |
| Same account | sender = receiver | domain-defined rejection |
| Unknown recipient | invalid recipient | lookup/domain error |

## 10. Happy paths, negative paths, and edge cases

The **happy path** is the normal successful flow. A **negative path** is an invalid or prohibited scenario. For insufficient funds, test that the transfer raises the documented exception and both balances remain unchanged. A defined business exception is expected behavior; an unexpected `TypeError`, `AttributeError`, or database connection error is not automatically a passing negative case.

For each important behavior, consider:

```text
happy path → boundary → invalid input → domain failure → state consistency after failure
```

An **edge case** is an unusual, extreme, empty, missing, or important boundary scenario: zero, one, minimum, maximum, empty/whitespace string, `None`, empty/one-item list, duplicates, negative/very large values, missing fields, malformed input. Discover them through domain rules, input constraints, data types, failure modes, state transitions, and equivalence classes. Select cases according to risk; financial/safety-critical systems may need more systematic boundary testing than a small utility.

## 11. Boundary-value analysis

Boundary-value analysis tests values at and immediately around a limit. If age must be between 18 and 65 inclusive, test 17, 18, 19, 64, 65, and 66:

```python
def is_valid_age(age: int) -> bool:
    return 18 <= age <= 65

@pytest.mark.parametrize(
    "age,expected",
    [(17, False), (18, True), (19, True),
     (64, True), (65, True), (66, False)],
)
def test_is_valid_age(age, expected):
    assert is_valid_age(age) is expected
```

This catches off-by-one defects such as `age > 18` instead of `age >= 18`. A useful generic set is minimum−1, minimum, minimum+1, maximum−1, maximum, maximum+1. Boundary testing is useful for validation, financial limits, quotas, pagination, rate limits, batch sizes, ages, file sizes, and API limits.

## 12. Equivalence partitioning

Equivalence partitioning divides a large input space into groups expected to behave similarly, then selects representative values. For age:

```text
age < 18 → reject
18–65    → accept
age > 65 → reject
```

Representatives could be 17, 30, and 66; boundary analysis adds 17, 18, 19, 64, 65, 66.

For shipping weight:

```python
def shipping_category(weight: int) -> str:
    if weight <= 0:
        raise ValueError("weight must be positive")
    if weight <= 5:
        return "small"
    if weight <= 20:
        return "medium"
    return "large"
```

Classes: invalid (0), small (3), medium (10), large (30); boundaries include 5, 6, 20, 21. Use equivalence partitioning plus boundary analysis. Check whether hidden domain rules create additional partitions.

## 13. Decision tables

Decision tables represent combinations of conditions and outcomes. For loan approval, conditions might be sufficient income, acceptable credit, and valid documents. A row with all true may approve; rows missing any required condition reject.

```python
@pytest.mark.parametrize(
    "income_ok,credit_ok,documents_ok,expected",
    [
        (True, True, True, "approved"),
        (True, True, False, "rejected"),
        (True, False, True, "rejected"),
        (False, True, True, "rejected"),
    ],
)
def test_loan_decision(income_ok, credit_ok, documents_ok, expected):
    result = decide_loan(income_ok, credit_ok, documents_ok)
    assert result == expected
```

Decision tables expose combinations that may be missed when tests are improvised. But combinations multiply rapidly; do not blindly test every theoretical combination if some are meaningless or redundant.

## 14. State-based testing

State-based testing checks valid and invalid transitions in systems with state: orders, payments, accounts, subscriptions, workflows, agent tasks, and jobs.

```text
PENDING → PAID → SHIPPED → DELIVERED
```

An invalid transition might be `DELIVERED → PAID`.

```python
def test_paid_order_can_ship():
    order = Order(status="PAID")
    order.ship()
    assert order.status == "SHIPPED"

def test_delivered_order_cannot_be_paid():
    order = Order(status="DELIVERED")
    with pytest.raises(ValueError):
        order.mark_paid()
```

Test both valid transitions and nearby invalid states. This is especially important in distributed and transactional systems where invalid transitions can corrupt data.

## 15. Input/output design

For an input → processing → output operation, consider normal input, invalid input, boundary input, combinations (e.g. discount + tax + quantity), and expected exceptions:

```python
calculate_total(10, 2) == 20

with pytest.raises(ValueError):
    calculate_total(-10, 2)

with pytest.raises(TypeError):
    calculate_total("10", 2)
```

The objective is not every possible input; it is representative, risk-relevant behavior.

## 16. Isolation and independence

**Isolation** means a test controls the state/resources it uses. **Independence** means it does not require another test to run first. Without isolation, Test A may mutate shared state and Test B may fail depending on order.

Bad:

```python
users = []

def test_add_user():
    users.append("Alice")
    assert "Alice" in users

def test_users_start_empty():
    assert users == []
```

Better: create a fresh local list or function-scoped fixture in each test. Shared-state sources include globals, mutable module state, databases, files, caches, environment variables, random seeds, clocks, and network services.

A test should establish its own prerequisites rather than rely on `test_create_user → test_login_user → test_create_order`. Run a failing test alone and in the full suite. If results differ, investigate shared state, fixture scope, cleanup, environment, DB rows, caches, and paths.

Isolation can cost time; safe reuse is acceptable when it does not compromise trustworthy state. For example, a database client may be reused while each test receives isolated data/transaction state.

## 17. Determinism

A deterministic test produces the same result for the same controlled input and relevant environment. Nondeterminism can come from random numbers, current time, networks, external APIs, changing database contents, concurrency, environment variables, unordered input, and async timing.

Avoid tests depending on `datetime.now()` at a timing boundary. Make time an explicit input:

```python
from datetime import datetime, timezone

def is_expired(deadline: datetime, now: datetime) -> bool:
    return now >= deadline

def test_deadline_is_not_expired_before_deadline():
    deadline = datetime(2026, 10, 1, tzinfo=timezone.utc)
    now = datetime(2026, 9, 30, tzinfo=timezone.utc)
    assert is_expired(deadline, now) is False
```

Likewise, control/inject randomness where exact reproducibility is needed. Flaky tests create false alarms and reduce trust in CI.

## 18. Test doubles and behavior vs implementation

A **stub** supplies predetermined responses; a **fake** is a simplified working implementation; a **mock** is commonly used to verify interactions; a **spy** records calls while allowing behavior. Terminology can vary. A fake payment gateway can make an order unit test fast and deterministic, but it does not prove the real gateway integration works. Pair isolated tests with an integration test at the real boundary when needed.

```python
class FakePaymentGateway:
    def __init__(self, approved: bool):
        self.approved = approved

    def charge(self, amount: int) -> bool:
        return self.approved
```

Behavior-focused tests avoid dependence on internals such as `service._cache`. A dictionary cache may later become an LRU or external cache while behavior stays the same. Test `service.get_user("123").name == "Alice"` rather than private storage, unless the internal invariant itself is an explicit contract. Some low-level algorithms, infrastructure libraries, and performance-sensitive modules legitimately need implementation-level invariants.

## 19. Test coupling, smells, naming, readability, maintainability

Test coupling comes from shared mutable fixtures, ordering assumptions, shared DB rows, global environment changes, and files reused between tests. Diagnose by running tests individually and together.

Common **test smells** (warnings, not automatic defects):
- giant tests covering multiple behaviors;
- vague names such as `test_user`;
- excessive setup for a simple rule;
- repeated manual teardown that belongs in fixtures;
- hidden setup behind vague fixtures;
- too many mocks and internal call assertions;
- brittle exact timestamps/private representations/incidental ordering;
- no meaningful assertion;
- overly broad E2E tests or overly narrow implementation-detail tests;
- unexplained magic values;
- flaky timing, race, random, shared-state, or network dependencies.

Name tests for scenario, behavior, and expected outcome, e.g. `test_register_user_rejects_duplicate_email`. Readable tests let a developer answer: what is tested, what state/input was used, what should happen, and why it failed? Use specific names, small setup, visible values, one clear primary Act, precise assertions, and useful parameter IDs.

Maintainability means the suite remains useful and affordable as code changes. DRY is not absolute in tests: remove mechanical repetition, but retain duplication when abstraction would hide meaningful scenario information. Shorter code is not necessarily easier to debug.

## 20. Test granularity and AAA at different levels

- **Unit:** one small component, fast and isolated.
- **Integration:** components work together, e.g. service + database.
- **API:** externally visible HTTP/service interface.
- **E2E:** broad user workflow across frontend/API/service/database.

AAA applies at every level; the scope and cost change. Choose the smallest level that provides meaningful confidence.

Unit example:

```python
class PriceCalculator:
    def calculate(self, price: int, quantity: int) -> int:
        return price * quantity

def test_calculate_returns_price_times_quantity():
    # Arrange
    calculator = PriceCalculator()
    price = 25
    quantity = 4
    # Act
    total = calculator.calculate(price, quantity)
    # Assert
    assert total == 100
```

SQLite integration example (real persistence, in-memory DB):

```python
import sqlite3

def create_user(conn: sqlite3.Connection, name: str) -> int:
    cursor = conn.execute(
        "INSERT INTO users (name) VALUES (?)",
        (name,),
    )
    conn.commit()
    return int(cursor.lastrowid)

def test_create_user_persists_record():
    # Arrange
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    # Act
    user_id = create_user(conn, "Alice")
    # Assert
    row = conn.execute(
        "SELECT id, name FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    assert row == (user_id, "Alice")
    conn.close()
```

In a full suite, fixture-managed cleanup is preferable.

API example:

```python
def test_create_user_api(client):
    payload = {"name": "Alice", "email": "alice@example.com"}
    response = client.post("/users", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Alice"
    assert body["email"] == "alice@example.com"
```

Duplicate email can be a separate test expecting HTTP 409. E2E example: arrange test account/login, act through product page/cart/checkout, assert a visible order confirmation. E2E tests catch broad integration issues but are slower and more brittle; do not use them for every rule.

## 21. Coverage, regression, and property-based thinking

Coverage indicates which lines/branches executed; it does not prove requirements or behaviors were verified. A test can execute `divide(10, 2)` without asserting anything. Requirement/behavior coverage asks whether important behavior is protected. Coverage plus good test design is stronger evidence than coverage alone.

Regression workflow:

```text
Bug discovered → reproduce → write failing regression test
→ fix implementation → keep test permanently
```

Example: a bug says `" 100 "` should parse successfully. Protect it:

```python
def test_parse_amount_accepts_surrounding_whitespace():
    assert parse_amount(" 100 ") == 100
```

Property-based thinking asks what must always be true, not only what happens for one example. For all valid integers, addition is commutative (`a + b == b + a`). Other properties: sorting preserves elements; normalization is idempotent; serialization/deserialization preserves valid information; a transfer conserves total funds. This lesson introduces the idea, not a property-testing library.

## 22. Testing data pipelines, ML, LLMs, and agents

**Data pipeline:** model contracts as input schema → transformation → validation → output schema. Test valid, missing, `None`, duplicate, wrong-type, malformed, and boundary rows. Also test schema contracts, counts, uniqueness, nullability, partitions, ordering assumptions, idempotency, and aggregation invariants. Example:

```python
def normalize_record(record: dict) -> dict:
    return {
        "name": record["name"].strip(),
        "age": int(record["age"]),
    }

def test_normalize_record():
    # Arrange
    record = {"name": " Alice ", "age": "30"}
    # Act
    result = normalize_record(record)
    # Assert
    assert result == {"name": "Alice", "age": 30}
```

A pipeline invariant might be `total_rows == valid_rows + rejected_rows`, if guaranteed by its contract.

**ML:** prepare controlled data/model/configuration; run prediction/preprocessing; assert structure, shape, allowed ranges, no unexpected NaNs, required fields, deterministic preprocessing, and business constraints. Avoid asserting exact predictions when model behavior is probabilistic.

**LLM applications:** strongly test deterministic surrounding components—prompt construction, validation, retrieval filtering, tool schemas, parsing, retries, timeouts, authorization, and state transitions. For generated output, structured schemas, allowed labels, confidence ranges, invariants, evaluation datasets, safety checks, and controlled/fake model responses may be more appropriate than exact sentence matching.

**Agentic AI:** arrange controlled tools, known state, input, and deterministic config; act by running the workflow; assert observable invariants: correct tool, required parameters, authorized state transitions, safe behavior, termination, and structured result. Do not test hidden internal reasoning. Example invariant: never transfer without authorization/balance checks.

## 23. Test pyramid, CI/CD, and refactoring

The test pyramid is a heuristic: many fast unit tests, fewer integration tests, and a smaller number of E2E tests. It is not a law. Different levels provide different confidence/cost.

Poor test design (e.g. many flaky tests) creates alert fatigue. CI should separate fast unit tests from slower integration/E2E, control environment, keep failures diagnostic, and retain regression tests. Registered pytest markers can group suites, e.g. `pytest -m "not integration"`.

Refactor tests by identifying the behavior, removing irrelevant setup, separating Arrange/Act/Assert, strengthening assertions, extracting fixtures only when useful, and adding negative cases. Do not shorten code at the expense of information.

## 24. Complete bank-transfer example

Requirements: amount positive; sender/receiver different; sender has sufficient balance; valid transfer decreases sender and increases receiver; rejected transfer changes neither balance.

```python
class BankAccount:
    def __init__(self, account_id: str, balance: int):
        self.account_id = account_id
        self.balance = balance

def transfer(sender: BankAccount, receiver: BankAccount, amount: int) -> None:
    if amount <= 0:
        raise ValueError("amount must be positive")
    if sender.account_id == receiver.account_id:
        raise ValueError("accounts must be different")
    if amount > sender.balance:
        raise ValueError("insufficient balance")
    sender.balance -= amount
    receiver.balance += amount
```

A fixture creates sender A with 500 and receiver B with 100. Happy path transfers 200 and expects 300/300. Exact-balance transfer uses all 500 and expects sender 0/receiver 600. Invalid amount tests (0, -1) expect `ValueError` and unchanged balances. Insufficient balance expects its domain error and unchanged balances. These tests protect validation, boundaries, negative behavior, state preservation, and conservation—not merely absence of a crash.

## 25. Mini-project: order-processing service

Requirements: order has items and total; can be submitted; empty order cannot be submitted; cannot submit twice; price and quantity positive; discount applies when subtotal is **greater than or equal to** 1000.

```python
class Order:
    DISCOUNT_THRESHOLD = 1000
    DISCOUNT_RATE = 0.10

    def __init__(self):
        self.items = []
        self.status = "DRAFT"

    def add_item(self, price: int, quantity: int) -> None:
        if price <= 0:
            raise ValueError("price must be positive")
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        self.items.append((price, quantity))

    def total(self) -> int:
        subtotal = sum(price * quantity for price, quantity in self.items)
        if subtotal >= self.DISCOUNT_THRESHOLD:
            return int(subtotal * (1 - self.DISCOUNT_RATE))
        return subtotal

    def submit(self) -> None:
        if not self.items:
            raise ValueError("order must contain at least one item")
        if self.status != "DRAFT":
            raise ValueError("order already submitted")
        self.status = "SUBMITTED"
```

Behavior inventory: add valid item; reject invalid price/quantity; calculate subtotal; apply discount; do not discount below threshold; reject empty submission; submit draft; reject duplicate submission. Boundary cases are 999 (no discount), 1000 (discount), and 1001 (discount). Parametrize cases with identical assertion structures. Intentionally change `>=` to `>`, mutate status before validation, allow zero quantity, or apply the wrong threshold; the suite should catch these defects.

## 26. Interview, architecture, checklist, knowledge check, glossary

Be able to explain AAA, one behavior vs one assertion, negative paths, edge/boundary analysis, equivalence classes, decision tables, state transitions, isolation vs independence, test coupling, behavior vs implementation, fixture/parametrization roles, test granularity, coverage limitations, regression, and deterministic LLM/agent testing.

Large backend architecture: organize unit/integration/API/E2E tests; keep fixtures small and local; isolate DB state with transactions, schemas, resets, or test DBs; choose smallest useful level. Data pipelines: test schemas, transformations, nulls, duplicates, counts, idempotency. AI apps: separate deterministic software envelope from probabilistic generation; test tool contracts, authorization, state, and safety invariants. Avoid combinatorial explosion through equivalence classes, boundaries, decision tables, risk-based selection, and representative interactions.

A production test-review checklist asks: Is behavior clear? Is the test named well? Is Arrange understandable? Is Act focused? Are assertions precise? Are happy/negative/boundary cases covered? Is state isolated and deterministic? Are fixtures justified and small? Is parametrization readable? Is there a regression test? Is the test at the smallest useful level? Is failure diagnosis straightforward? Will it run reliably in CI?

Knowledge-check answers:
1. Perfect AAA with `result is not None` is still weak.
2. Multiple assertions are acceptable when they jointly prove one behavior.
3. Boundaries catch off-by-one/comparison errors.
4. Isolation controls state/resources; independence avoids relying on another test.
5. Behavior-over-implementation protects contracts through refactoring.
6. `assert result` is weak; assert exact expected result.
7. A long registration/login/order/pay/cancel/refund test is too broad.
8. For suite-only failure, inspect shared state, order, environment, DB, caches, cleanup.
9. Failure only at 65 suggests boundary logic.
10. Active subscription + authenticated can be tested with a small decision table or focused tests.
11. Not every backend test needs a real DB.
12. LLM tests need not assert exact text; use structure/invariants/evaluation where appropriate.

Glossary: test design (scenario selection); AAA (Arrange/Act/Assert); test isolation (controlled resources/state); independence (no prior-test dependency); deterministic (repeatable under controlled conditions); flaky (intermittent); coupling (hidden shared dependency); boundary value; equivalence partition; happy/negative path; regression test; test double, stub, fake, mock, spy; coverage (executed code/path signal); implementation detail (internal design, not necessarily public contract); property-based thinking (general invariants).

Final mental model:

```text
Requirement → behavior → inputs/state → risks/failure modes
→ boundaries/classes/transitions → observable outcome
→ Arrange → Act → Assert
→ diagnose expected vs actual → fix → regression protection
```

Good test design is not more tests; it is meaningful tests, reliable feedback, clear failure diagnosis, and protection of important behavior.

---

# Part B — Project Tree and Current-Level Assessment

## 1. Roadmap position

The saved `Roadmap_ptree.md` places this lesson in **Stage 1 — Programming & Computational Thinking → Module 07 — Testing and Systematic Debugging**. Stage 1 contains the following modules:

1. Computational Thinking and Program Design
2. Python Core Language and Data Types
3. Control Flow, Functions, Scope, and Errors
4. Problem-Solving, Collections, and Algorithmic Habits
5. Text Files, Structured Data, and CLI Programs
6. Modules, Packages, Dependencies, and Code Quality
7. Testing and Systematic Debugging
8. Object-Oriented Design, Data Modelling, and Functional Style
9. Advanced Production-Oriented Python Foundations
10. Production Habits for Python Programs

The roadmap tree lists nine files under Module 07, including its overview, lesson files, practice material, and project resources. The current sequence is:
- Lesson 01: Test Levels — Unit, Integration, and End-to-End.
- Lesson 02: Pytest — Assertions, Fixtures, and Parametrization.
- Lesson 03: Arrange–Act–Assert and Test Design (this lesson).

The wider roadmap continues into OOP, production Python, and later Data Engineering, DSA, mathematics, ML, deep learning, backend, LLM, RAG, evaluation, agents, safety, inference, LLMOps, and portfolio/career stages. Those later stages are not prerequisites for this lesson.

## 2. Current learning level

Previously completed topics relevant to this lesson:
- Python functions, arguments, return values, conditionals, loops, collections, scope, pure functions, side effects, exceptions, and validation.
- Text files, paths, CSV/JSON, encodings, CLI arguments, standard streams, exit codes, logging, and environment configuration.
- Imports, modules, packages, project layout, `pyproject.toml`, lock files/`uv`, dependency management, Ruff, type hints/type checking, and documentation.
- Module 1.6 cumulative practice.
- Module 07 Lesson 01: test levels.
- Module 07 Lesson 02: pytest assertions, fixtures, fixture scopes, yield/cleanup, parametrization, IDs, and indirect parametrization.

Your current level is **beginner progressing toward intermediate Python engineering**. You have the prerequisites needed to learn test design. This lesson is primarily a reasoning/engineering lesson rather than a new Python syntax chapter.

## 3. Scope discipline

The solutions below use functions, classes only where the lesson supplies them, dictionaries/lists, exceptions, `assert`, pytest fixtures/parametrization, and previously learned concepts. They do not introduce a mocking library tutorial, property-based testing library, advanced async testing, or new frameworks. When an exercise relies on an application interface (`process_rows`, `client`, `agent`, etc.), that dependency is labelled as supplied by the exercise context rather than falsely presented as a complete standalone application.

**Learning boundary:** this guide completes Module 07 Lesson 03 and its exercises. It does not begin Lesson 04.

---

# Part C — All 20 Coding Exercises with Solutions

## Level 1 — Basic

### Exercise 1 — Arrange, Act, Assert

```python
def test_square_returns_squared_value():
    # Arrange
    value = 5
    # Act
    result = square(value)
    # Assert
    assert result == 25
```

- `value = 5` establishes the input.
- `square(value)` executes the function.
- `assert result == 25` verifies the exact contract.
- `square()` is supplied by the exercise.

### Exercise 2 — Strong assertion

```python
def test_get_user_returns_expected_user():
    result = get_user()
    assert result["name"] == "Alice"
    assert result["role"] == "admin"
```

- Call `get_user()` once and store its result.
- Check the expected name.
- Check the expected role.
- This is stronger than only checking `is not None`.

### Exercise 3 — Happy and negative paths

```python
import pytest

def test_divide_returns_quotient():
    result = divide(10, 2)
    assert result == 5

def test_divide_rejects_zero_divisor():
    with pytest.raises(ValueError, match="division by zero"):
        divide(10, 0)
```

- The first test verifies normal division.
- The second verifies the documented `ValueError`.
- The message fragment improves diagnosis.
- Do not use broad `Exception` when the contract specifies `ValueError`.

### Exercise 4 — Test naming

```python
def test_register_user_rejects_duplicate_email():
    ...
```

The name identifies the operation, scenario, and expected behavior. Prefer behavior names over internal helper names.

### Exercise 5 — Identify behavior

```text
Case 1: empty cart → checkout → ValueError
Case 2: cart with one valid item → checkout → success
```

The first case verifies the prohibition; the second gives a valid contrast. Testing only successful checkout leaves the empty-cart rule unprotected.

## Level 2 — Intermediate

### Exercise 6 — Boundary values

For scores from 0 through 100 inclusive:

```text
-1 invalid
0 valid
1 valid
99 valid
100 valid
101 invalid
```

These cover immediately outside, at, and immediately inside both boundaries.

### Exercise 7 — Parametrize boundaries

```python
import pytest

def is_valid_score(score: int) -> bool:
    return 0 <= score <= 100

@pytest.mark.parametrize(
    "score,expected",
    [(-1, False), (0, True), (1, True),
     (99, True), (100, True), (101, False)],
)
def test_score_is_valid(score, expected):
    assert is_valid_score(score) is expected
```

- The function implements the inclusive rule.
- Each tuple supplies one score and its expected boolean.
- Pytest executes the same test for each tuple.
- `is` checks the boolean result explicitly.

### Exercise 8 — Equivalence partitioning

Rule: `0 < weight <= 5 → small`, `5 < weight <= 20 → medium`, `weight > 20 → large`.

Representative cases: 3 → small, 10 → medium, 30 → large. Boundary set: 0, 1, 5, 6, 20, 21. Representatives cover classes; boundary values catch comparison mistakes.

### Exercise 9 — Test isolation

```python
def test_adds_item():
    items = []
    items.append("A")
    assert items == ["A"]

def test_starts_empty():
    items = []
    assert items == []
```

Each test creates its own list. Do not keep a global list and conditionally clear it; that retains hidden coupling.

### Exercise 10 — Behavior vs implementation

```python
def test_get_user_returns_requested_user(service):
    user = service.get_user("123")
    assert user.id == "123"
```

- The test calls the public service operation.
- It checks the requested user identity.
- It does not depend on whether the service uses a dictionary, cache, or another internal representation.

## Level 3 — Advanced

### Exercise 11 — Decision table

```python
import pytest

def can_access_feature(authenticated: bool, active: bool) -> bool:
    return authenticated and active

@pytest.mark.parametrize(
    "authenticated,active,expected",
    [
        (True, True, True),
        (True, False, False),
        (False, True, False),
        (False, False, False),
    ],
)
def test_feature_access(authenticated, active, expected):
    result = can_access_feature(authenticated, active)
    assert result is expected
```

- The function expresses the rule: both conditions must be true.
- Each row covers one combination.
- The assertion compares actual and expected boolean outcomes.

### Exercise 12 — State transition

```python
import pytest

def ship_order(status: str) -> str:
    if status != "PAID":
        raise ValueError("only paid orders can ship")
    return "SHIPPED"

def test_paid_order_can_ship():
    assert ship_order("PAID") == "SHIPPED"

def test_cancelled_order_cannot_ship():
    with pytest.raises(ValueError, match="only paid orders can ship"):
        ship_order("CANCELLED")
```

The first test protects the valid transition; the second protects the invalid transition and its defined error.

### Exercise 13 — Regression test

```python
def test_parse_amount_accepts_surrounding_whitespace():
    assert parse_amount(" 100 ") == 100
```

This captures the reported defect before/while fixing it. Keep the test permanently so the bug cannot silently return. `parse_amount()` is supplied by the application context.

### Exercise 14 — Deterministic time

```python
def is_expired(deadline, now):
    return now >= deadline
```

```python
from datetime import datetime, timezone

def test_is_expired_before_deadline():
    deadline = datetime(2026, 10, 1, tzinfo=timezone.utc)
    now = datetime(2026, 9, 30, tzinfo=timezone.utc)
    assert is_expired(deadline, now) is False
```

- Time is an explicit input rather than being read internally.
- Both datetimes use UTC.
- The test controls the comparison and is independent of the machine clock.
- Do not use `sleep()` to wait for a time boundary.

### Exercise 15 — AAA refactoring

Problems in the original test:
1. It combines user creation, cart creation, product addition, discounting, and card charging.
2. It has unnecessary setup for a cart calculation.
3. `cart.total > 0` is too weak.

Narrow illustrative refactor:

```python
def test_discounted_cart_total():
    # Arrange
    cart = Cart(items=[Product(price=100)])
    # Act
    cart.apply_discount(10)
    # Assert
    assert cart.total == 90
```

- Arrange creates the minimal cart.
- Act applies the discount.
- Assert checks the exact expected total.
- `Cart` and `Product` are assumed application classes, not defined in the exercise.

## Level 4 — Production-oriented

### Exercise 16 — Data-pipeline invariant

```python
def test_pipeline_preserves_row_count():
    # Arrange
    rows = [
        {"id": 1, "valid": True},
        {"id": 2, "valid": False},
        {"id": 3, "valid": True},
    ]
    # Act
    result = process_rows(rows)
    # Assert
    assert result.total_rows == result.valid_rows + result.rejected_rows
```

- Three representative input rows are prepared.
- `process_rows` runs the pipeline (provided by the application).
- The assertion protects the invariant that each input row is either valid or rejected.
- Merely checking that the pipeline does not raise is insufficient.

### Exercise 17 — API contract

```python
def test_create_user_returns_created_resource(client):
    # Arrange
    payload = {"name": "Alice"}
    # Act
    response = client.post("/users", json=payload)
    # Assert
    assert response.status_code == 201
    assert response.json()["id"]
```

- `client` is an application test-client fixture.
- The payload represents the request.
- The POST call executes the API behavior.
- Assertions verify creation status and presence of an ID.
- A stricter contract could assert the ID's type/value if specified.

### Exercise 18 — LLM structured output

```python
def test_classifier_returns_structured_result(classifier):
    # Arrange
    text = "I need a refund"
    # Act
    result = classifier.classify(text)
    # Assert
    assert set(result) == {"label", "confidence"}
```

The test verifies the required output structure without asserting an exact generated sentence. `classifier` is supplied by the application/test fixture. Do not invent additional value constraints that the stated contract did not specify.

### Exercise 19 — Agent invariant

The requirement is: do not call the transfer tool unless balance checking succeeds. A safe test design uses controlled tool doubles and checks observable calls:

```python
def test_agent_does_not_transfer_when_balance_is_insufficient(agent, fake_tools):
    # Arrange
    fake_tools.balance.return_value = 50
    request = {
        "from_account": "A",
        "to_account": "B",
        "amount": 100,
    }
    # Act
    agent.run(request)
    # Assert
    fake_tools.balance.assert_called_once()
    fake_tools.transfer.assert_not_called()
```

- The balance tool is controlled to return 50.
- The request asks to transfer 100.
- The agent executes its workflow.
- The assertions verify the balance check occurred and transfer did not.
- This assumes a mock-style `fake_tools` fixture exposing these assertion methods. The lesson's other example checks call order and transfer arguments; use that only when the tool-double implementation records ordered calls. Do not inspect hidden model reasoning.

### Exercise 20 — Test-suite architecture

```text
Unit:
  fast, isolated, deterministic; run on every change

Integration:
  verify app/database/service boundaries;
  control database lifecycle; run in CI

E2E:
  a small set of critical user workflows;
  run at suitable pipeline stages
```

Use fixtures for setup/cleanup, isolate shared DB state, and avoid one giant global fixture. The design balances confidence, speed, and maintainability. Do not make every test use a real database simply for “realism.”

---

# Part D — All 10 Debugging Labs

1. **Unclear AAA/cleanup mixed in test:** move resource cleanup into a yield fixture with teardown after `yield`; keep the test focused on adding and reading the cart total.
2. **Multiple unrelated behaviors:** split registration, login, and order creation into separate tests, each with its own Arrange, Act, and Assert.
3. **Weak discount assertion:** replace `assert result` with `assert result == 90` for a 10% discount on 100.
4. **Implementation-detail assertion:** replace checking `service._cache["1"]` with a public behavior such as `service.get_user("1").id == "1"`.
5. **Shared mutable state:** replace global `USERS` with test-local state or a fresh function-scoped `users` fixture.
6. **Test-order dependency:** make `test_get_user` create its own user (or request a fixture that does); do not depend on a global ID set by another test.
7. **Random behavior:** do not assert one hard-coded random token. Assert stable properties such as string type and expected length, or inject a controllable random source.
8. **Excessive fixture abstraction:** replace one `everything` fixture with small composable fixtures (e.g. `user`, `account`) and keep scenario-specific setup in each test.
9. **Excessive setup/wrong test level:** a pure `add(2, 3)` behavior should be tested directly; do not create an app, database, user, permissions, product, and cart.
10. **Overly broad E2E:** keep a small critical purchase workflow; move individual registration, search, coupon, checkout, refund, and receipt rules into focused lower-level tests as appropriate.

---

# Part E — Interview and Architecture Review

## Interview questions — concise model answers

1. **What is AAA?** A pattern separating scenario preparation, target action, and outcome verification; not a rigid three-line template.
2. **Exactly one assertion per test?** No; multiple related assertions can prove one coherent behavior.
3. **Why AAA?** Better readability, review, debugging, and maintenance.
4. **Arrange?** Inputs, state, dependencies, configuration, and resources.
5. **Act?** The primary behavior being tested.
6. **Assert?** Observable outcomes, state, exceptions, persistence, and contract effects.
7. **One behavior per test?** One logically coherent expected behavior, not one statement.
8. **Why negative cases?** They protect business rules and failure behavior.
9. **Boundary-value analysis?** Test values at and around limits.
10. **Equivalence partitioning?** Divide input space into behaviorally similar classes and select representatives.
11. **Isolation?** A test controls its own state/resources.
12. **Test coupling?** Shared state, ordering assumptions, reused DB rows, globals, environment leakage.
13. **Behavior over implementation?** Protect the contract so refactoring does not break tests unnecessarily.
14. **Fixtures and AAA?** Fixtures supply reusable Arrange dependencies and manage lifecycle.
15. **Parametrization and AAA?** Same AAA logic runs over multiple explicit scenarios.
16. **Separate tests vs parametrization?** Split when setup, behavior, or assertions materially differ.
17. **Prevent combinatorial explosion?** Use equivalence classes, boundaries, decision tables, risk, and representative interactions.
18. **Nondeterministic LLM output?** Test deterministic components, schemas, invariants, controlled responses, and use evaluation for model quality.
19. **Harmful fixtures?** Huge, opaque, deeply chained, poorly cleaned, or globally coupled fixtures.
20. **Debug failure?** Isolate the case, inspect assertion/setup/dependencies, compare expected and actual, find code vs test-design defect, fix, and rerun regression tests.

## Architecture questions

- **Large backend:** separate unit/integration/API/E2E; keep fixtures close to shared purpose; fast isolated tests should be the broad base.
- **Database state:** use transaction rollback, isolated schemas/test DBs, dataset reset, or per-test data according to cost and isolation needs.
- **Data pipeline:** test input/output schemas, transformations, representative and boundary rows, nulls, duplicates, counts, and idempotency.
- **AI application:** separate deterministic validation, prompt/retrieval/tool contracts, parsing, authorization, retries, and fallbacks from probabilistic generation quality.
- **Agentic workflow:** test tool permissions, arguments, state transitions, termination, safety constraints, and structured output using controlled tools.
- **Combinatorial testing:** reduce combinations with equivalence classes, boundaries, decision tables, pairwise/systematic selection where appropriate, and risk.
- **Coverage vs speed:** fast unit tests first, medium integration tests next, fewer slower E2E tests at appropriate pipeline stages.
- **Regression:** turn each important reproducible defect into a test that remains in CI.

---

# Part F — Production Checklist, Knowledge Check, and Glossary

## Production test-design checklist

- [ ] Behavior and expected outcome are clear.
- [ ] Name describes scenario and result.
- [ ] Arrange is understandable and minimal.
- [ ] Act is focused on the target behavior.
- [ ] Assertions catch meaningful defects.
- [ ] Happy, negative, boundary, and important edge cases are covered.
- [ ] Test is isolated and deterministic where practical.
- [ ] Assertions avoid incidental implementation details.
- [ ] Fixtures are justified, small, and lifecycle-safe.
- [ ] Parametrization and IDs improve clarity.
- [ ] No unnecessary combination explosion.
- [ ] Regression test exists for discovered defect.
- [ ] Test uses the smallest useful level.
- [ ] Failure diagnosis is straightforward and CI execution reliable.
- [ ] Abstractions remove mechanical repetition without hiding the scenario.

## Knowledge-check answers

1. Perfect AAA with only `result is not None` is not necessarily good; the assertion may be weak.
2. Multiple assertions are acceptable when they jointly verify one coherent behavior.
3. Boundaries matter because comparison/off-by-one defects cluster around limits.
4. Isolation controls state/resources; independence means no prior test must run first.
5. Behavior-over-implementation protects the public contract through refactoring.
6. `assert result` is weak because it does not check the expected total; assert the exact result.
7. A register/login/order/pay/cancel/refund test combines too many behaviors.
8. For suite-only failures, inspect shared state, order, environment, DB, caches, globals, and cleanup.
9. Failure only at 65 suggests checking boundary logic and the specific parameter.
10. Authentication + active subscription can be a small decision table or a few focused tests.
11. Not every backend test needs a real database; choose the level that answers the question.
12. LLM tests need not assert exact text; structured contracts, invariants, and evaluation can be more suitable.

## Glossary

- **Test design:** selecting behaviors/scenarios and expected outcomes.
- **AAA:** Arrange, Act, Assert.
- **Test isolation:** controlled state/resources.
- **Test independence:** no dependency on another test's execution.
- **Deterministic test:** repeatable under controlled conditions.
- **Flaky test:** intermittent result without relevant code change.
- **Test coupling:** hidden dependency/shared state between tests.
- **Test smell:** warning pattern suggesting a design issue.
- **Boundary value:** value at or near a limit.
- **Equivalence partitioning:** behaviorally similar input classes.
- **Happy/negative path:** normal success / invalid or rejected scenario.
- **Regression test:** protects against a previously discovered defect.
- **Test double:** controlled replacement for a real dependency.
- **Stub/fake/mock/spy:** predetermined response / simplified implementation / interaction-verifying double / call-recording double.
- **Coverage:** measure of executed lines or branches, not proof of correctness.
- **Implementation detail:** internal design choice not necessarily part of public contract.
- **Property-based thinking:** testing general invariants over many inputs.

---

# Completion Status

- [x] Lesson concepts and examples covered from Sections 1–52.
- [x] AAA and each phase explained.
- [x] Requirement-to-test-case design explained.
- [x] Happy/negative paths, edge cases, boundaries, equivalence classes, decision tables, and state transitions covered.
- [x] Isolation, independence, determinism, test doubles, behavior vs implementation, coupling, smells, naming, readability, and maintainability covered.
- [x] Unit, integration, API, E2E, coverage, regression, and property-based thinking covered.
- [x] Data pipeline, ML, LLM, agentic AI, test pyramid, CI/CD, and refactoring applications covered.
- [x] Complete bank-transfer example and order-processing mini-project covered.
- [x] All 20 coding exercises answered.
- [x] All 10 debugging labs addressed.
- [x] Interview questions, architecture questions, checklist, knowledge check, and glossary included.
- [ ] Module 07 Lesson 04 not started; awaiting instruction.
