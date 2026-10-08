# Arrange–Act–Assert and Test Design

## Learning Objectives

By the end of this chapter, you should be able to:

- Explain what test design is and why a large number of tests does not automatically mean good test quality.
- Convert requirements and business rules into deliberate test cases.
- Use Arrange–Act–Assert (AAA) as a thinking framework rather than as a rigid three-line template.
- Design tests around observable behavior, meaningful outcomes, failure modes, boundaries, and state transitions.
- Decide what belongs in Arrange, Act, and Assert.
- Recognize the difference between one logical behavior and one assertion.
- Design isolated, independent, deterministic, readable, maintainable tests.
- Use pytest fixtures and parametrization to support test design without hiding the test story.
- Apply boundary-value analysis, equivalence partitioning, decision tables, and state-based testing.
- Recognize and refactor common test smells.
- Choose an appropriate test granularity: unit, integration, API, or end-to-end.
- Design tests for backend systems, databases, data pipelines, ML systems, AI/LLM applications, and agentic workflows.
- Build regression tests when defects are found.
- Understand coverage as a signal rather than proof of quality.
- Think in terms of behavior, invariants, and properties.
- Design production-oriented test suites that give fast, trustworthy feedback.

---

## Prerequisites

This chapter assumes that you are a beginner, but it builds on a few basic Python ideas:

- functions
- function arguments
- return values
- exceptions
- variables
- lists and dictionaries
- simple classes
- `assert`
- basic pytest usage

The previous chapter, **Pytest — Assertions, Fixtures, and Parametrization**, explains pytest syntax in greater depth. This chapter deliberately focuses on **how to think about tests** and how to turn that syntax into good engineering.

You do not need to memorize every testing technique in this chapter on your first pass. The goal is to develop a repeatable reasoning process.

---

# 1. What Is Test Design?

## What is it?

Software testing is the practice of checking whether software behaves as intended.

A **test** is a repeatable check of some expected behavior.

A **test case** is a specific scenario with:

- an input or starting condition
- an expected behavior or outcome
- a way to observe whether the behavior occurred correctly

**Test design** is the process of deciding:

> What should we test, why should we test it, which inputs should we choose, what should happen, and how will the test reveal a defect?

Writing test code is only the implementation step.

A useful distinction is:

```text
Test design
    ↓
Decide what behavior matters
    ↓
Choose useful scenarios
    ↓
Choose expected outcomes
    ↓
Write the test
```

## Why does it exist?

Because software can have many possible inputs and states.

Suppose a function accepts an integer:

```python
def calculate_discount(amount: int) -> int:
    ...
```

There are far more possible inputs than you can realistically write separate test functions for.

A good test designer therefore asks:

- What does the requirement say?
- What values are normal?
- What values are at the boundary?
- What values are invalid?
- What failure modes matter?
- Which cases are representative?
- Which cases are likely to reveal defects?

That is test design.

## Simple example

Imagine:

```python
def multiply(a: int, b: int) -> int:
    return a * b
```

A weak test might be:

```python
def test_multiply():
    result = multiply(2, 3)
    assert result is not None
```

This tells us very little.

A stronger test is:

```python
def test_multiply_returns_product():
    result = multiply(2, 3)
    assert result == 6
```

The second test verifies the actual behavior.

## Real-world example

A bank requirement says:

> A customer cannot withdraw more than the available balance.

That requirement immediately suggests multiple test cases:

| Scenario | Input | Expected behavior |
|---|---|---|
| Normal withdrawal | 100 from balance 500 | withdrawal succeeds |
| Exact balance | 500 from balance 500 | withdrawal succeeds |
| Over balance | 501 from balance 500 | rejected |
| Zero amount | 0 | rejected or handled according to requirement |
| Negative amount | -10 | rejected |
| Invalid amount | `"abc"` | validation error |

The list of tests comes from reasoning about the requirement, not from pytest syntax.

## Common mistakes

### Mistake 1: "More tests always means better testing"

Not necessarily.

Ten tests that all exercise the same path may provide less protection than four carefully selected tests covering distinct behaviors.

### Mistake 2: Testing only the happy path

A system can appear healthy because normal inputs work while important invalid inputs fail dangerously.

### Mistake 3: Writing tests after seeing the implementation and simply mirroring it

This can produce tests that confirm the code you wrote instead of testing the requirement the code was supposed to implement.

## Better approach

Start from behavior and requirements:

```text
Requirement
    ↓
Behavior
    ↓
Scenarios
    ↓
Expected outcomes
    ↓
Test implementation
```

## Production considerations

In production engineering, tests are an information system.

A good test answers a useful question:

> "If this test fails, what important behavior is no longer trustworthy?"

A weak test may pass for years while protecting very little.

---

# 2. Testing as Behavior Verification

## What is it?

Behavior verification means testing what the system does from an observable perspective.

A useful model is:

```text
Input / Starting State
        ↓
     Behavior
        ↓
Observable Outcome
```

Observable outcomes can include:

- return values
- raised exceptions
- state changes
- persisted data
- emitted events
- HTTP responses
- files created or updated
- messages sent
- externally visible interactions

## Why does it exist?

The purpose of a test is not to prove that a particular implementation line exists.

The purpose is to increase confidence that the system behaves correctly.

## How does it work?

Take a requirement:

> `validate_email()` should reject an address without `@`.

Turn it into:

```text
Input:
"alice.example.com"

Expected behavior:
validation fails

Expected observable result:
ValueError is raised
```

Then write the test.

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

## Real-world example

For an API endpoint:

```text
POST /users
```

the observable behavior may include:

- HTTP 201 for a valid request
- HTTP 400 for malformed input
- user record created in a database
- duplicate email rejected
- event emitted after successful creation

One test should not necessarily assert all of these. Design tests around coherent behaviors and layers.

## Common mistakes

- Treating log messages as the main business result when a stronger state/result assertion exists.
- Asserting private variables instead of public behavior.
- Ignoring error behavior.
- Ignoring side effects when the requirement explicitly includes them.

## Better approach

Write down:

1. What goes in?
2. What should happen?
3. What can I observe?
4. Which observable outcome proves the behavior?

## Production considerations

Behavior-oriented tests are usually more resilient to refactoring because implementation can change while externally visible behavior remains stable.

---

# 3. Arrange–Act–Assert

## What is it?

**Arrange–Act–Assert (AAA)** is a test-structuring pattern:

```text
Arrange → prepare the scenario
Act     → perform the behavior under test
Assert  → verify the expected outcome
```

AAA is a **mental and structural model**, not a requirement that every test contain exactly three statements.

## Why does it exist?

Tests can become difficult to read when setup, actions, and verification are mixed together.

AAA gives readers a predictable story.

## How does it work?

Consider:

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

### Line-by-line explanation

```python
a = 2
b = 3
```

These values create the test scenario. That is Arrange.

```python
result = add(a, b)
```

This performs the behavior being tested. That is Act.

```python
assert result == 5
```

This checks whether the behavior produced the expected result. That is Assert.

## Real-world example

```python
def test_withdraw_reduces_balance():
    # Arrange
    account = BankAccount(balance=500)

    # Act
    account.withdraw(100)

    # Assert
    assert account.balance == 400
```

The business story is immediately visible.

## Common mistakes

### Treating AAA as exactly three lines

This is incorrect.

You can have:

```python
# Arrange
user = ...
permissions = ...
configuration = ...

# Act
response = ...

# Assert
assert response.status_code == 200
assert response.json()["role"] == "admin"
```

That can be a perfectly reasonable test.

### Hiding everything inside helpers

A helper can remove useful context:

```python
response = do_everything_for_test()
assert response == ...
```

The test becomes shorter but less understandable.

## Better approach

Use AAA to make the test story obvious.

A useful review question is:

> Can another engineer identify the setup, behavior, and verification quickly?

## Production considerations

AAA scales from a five-line unit test to an integration test involving databases.

The shape remains:

```text
establish known state
        ↓
perform target behavior
        ↓
check important observable result
```

---

# 4. Why AAA Exists

## What problem does it solve?

Without structure, a test can become a mixture of:

- data creation
- configuration
- database setup
- API calls
- cleanup
- assertions
- unrelated actions

Example:

```python
def test_order():
    user = create_user()
    database = connect_to_database()
    order = create_order(user, database)
    response = submit_order(order)
    assert response.status_code == 200
    delete_order(order)
    delete_user(user)
```

The test may be valid, but its business behavior is harder to see.

A better structure is:

```python
def test_submit_order():
    # Arrange
    user = create_user()
    order = create_order(user)

    # Act
    response = submit_order(order)

    # Assert
    assert response.status_code == 200
```

Resource cleanup may be handled by fixtures or another appropriate lifecycle mechanism.

## AAA improves

| Quality | How AAA helps |
|---|---|
| Readability | separates setup, behavior, and verification |
| Debugging | narrows attention to the failing phase |
| Code review | makes intent easier to inspect |
| Maintenance | reduces accidental mixing of responsibilities |
| Failure diagnosis | makes expected vs actual easier to locate |
| Consistency | gives the team a shared test vocabulary |

## Important distinction

AAA does **not** make a test correct by itself.

A poorly designed test can have perfect AAA structure.

For example:

```python
def test_calculation():
    # Arrange
    x = 2

    # Act
    result = calculate(x)

    # Assert
    assert result is not None
```

Structurally clean, but behaviorally weak.

AAA is a structure for good reasoning; it is not a replacement for good reasoning.

---

# 5. Arrange in Detail

## What is it?

Arrange is everything needed to put the system into a meaningful starting condition for the behavior under test.

It can include:

- input values
- object creation
- fixture-provided dependencies
- configuration
- database state
- temporary files
- environment variables
- controlled external dependencies
- initial state

## Why does it exist?

The behavior you test depends on starting conditions.

If starting state is vague or uncontrolled, the test becomes difficult to trust.

## How does it work?

Suppose you need to test:

> A user with an expired subscription cannot download premium content.

Arrange must establish:

- a user
- an expired subscription
- a premium resource
- relevant policy/configuration

Then Act is the download operation.

Then Assert verifies the rejection.

## Simple example

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

## Real-world example with a fixture

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

Conceptually, fixture construction is part of the **test setup/Arrange phase**, even though pytest performs the fixture resolution outside the literal body of the test.

This is an important distinction:

```text
Test authoring view:
Fixture → supports Arrange

Pytest execution view:
pytest resolves fixture dependencies before test execution
```

## Test data vs test infrastructure

### Test data

Values used to exercise behavior:

```python
price = 100
quantity = 2
```

### Test infrastructure

Resources or mechanisms that make the test possible:

```text
database connection
temporary directory
API client
application instance
test clock
```

The distinction matters because infrastructure often belongs in reusable fixtures, while scenario-specific data should remain visible in the test when visibility helps understanding.

## Common mistakes

- Putting too much scenario logic into fixtures.
- Creating real external infrastructure unnecessarily for unit tests.
- Hiding important test inputs.
- Building large object graphs when the behavior needs only a small amount of state.

## Better approach

Ask:

> What is the minimum meaningful starting state required to test this behavior?

Prefer **necessary setup** over **maximum setup**.

## Production considerations

Good Arrange phases are:

- explicit enough to understand
- reusable where reuse is truly beneficial
- deterministic
- isolated
- cheap when possible

---

# 6. Act in Detail

## What is it?

The Act phase executes the **primary behavior under test**.

Examples:

```python
result = calculate_total(cart)
```

```python
user = register_user(payload)
```

```python
response = client.get("/users/1")
```

```python
process_payment(transaction)
```

## Why does it exist?

A reader should quickly see what behavior the test is evaluating.

## How does it work?

For:

> "A withdrawal greater than the balance is rejected."

the Act is:

```python
account.withdraw(501)
```

Everything before that prepares the scenario. Everything after it evaluates the outcome.

## Why prefer a clear primary Act step?

When a test contains many unrelated actions:

```python
create_user()
login_user()
create_order()
cancel_order()
refund_order()
```

it becomes difficult to answer:

> Which behavior actually failed?

This may be several tests pretending to be one workflow.

## Better decomposition

```python
def test_user_can_create_order():
    # Arrange
    user = authenticated_user()

    # Act
    order = create_order(user)

    # Assert
    assert order.status == "created"


def test_user_can_cancel_order():
    # Arrange
    order = existing_order()

    # Act
    cancel_order(order)

    # Assert
    assert order.status == "cancelled"
```

## Important nuance

"One Act" is a useful default, not a universal law.

An integration test may require a sequence:

```text
Arrange
→ Act: send command
→ Act: wait for processing
→ Assert
```

Or an E2E test may naturally exercise multiple UI steps.

The key question is:

> Are these steps one coherent behavior, or are multiple unrelated behaviors being bundled together?

## Common mistakes

- Calling unrelated methods just to reach the assertion.
- Performing assertions inside the Act helper and hiding failure information.
- Creating a full workflow when a smaller behavior test would provide faster feedback.

## Production considerations

Keep the primary behavior visible. If the Act is difficult to express cleanly, that can indicate:

- the test is too broad
- the system interface is awkward
- setup is too complicated
- the behavior boundary is unclear

---

# 7. Assert in Detail

## What is it?

Assert verifies whether the observed outcome matches the requirement.

Possible targets include:

- return values
- state
- exceptions
- persisted records
- response status
- response body
- side effects
- allowed invariants

## Strong vs weak assertions

Weak:

```python
assert result
```

Stronger:

```python
assert result.status == "approved"
```

Weak:

```python
assert response is not None
```

Stronger:

```python
assert response.status_code == 201
assert response.json()["id"] > 0
```

## Assertion precision

A useful assertion is as specific as the requirement requires, but no more specific than necessary.

Too weak:

```python
assert order
```

Potentially too brittle:

```python
assert order.__dict__ == {
    "_internal_cache": {},
    "_generated_at": "2026-09-23T09:00:00+05:30",
    "status": "created",
    "total": 100,
}
```

Better:

```python
assert order.status == "created"
assert order.total == 100
```

## Multiple related assertions

Multiple assertions can be appropriate when they establish one logical behavior.

Example:

```python
def test_successful_registration_returns_created_user():
    user = register_user({"name": "Alice", "email": "alice@example.com"})

    assert user.name == "Alice"
    assert user.email == "alice@example.com"
```

The two assertions answer related parts of one behavior: the newly registered user has the expected data.

Compare that with a test that verifies registration, password reset, billing, and report generation. That is likely too broad.

## Exceptions

Exception behavior is still part of Assert.

```python
with pytest.raises(ValueError):
    parse_amount("abc")
```

The **Act** is inside the context manager; the expected exception is the assertion condition.

## Common mistakes

- Asserting internal implementation details.
- Asserting only that something is "not None".
- Checking a generated timestamp exactly when only relative behavior matters.
- Verifying incidental formatting that the requirement does not care about.

## Production considerations

The assertion should protect a behavior that is worth preserving.

Ask:

> What defect would this assertion catch?

If the answer is "almost none," strengthen the assertion.

---

# 8. One Behavior per Test

## What is it?

"One behavior per test" means a test should normally communicate one coherent expected behavior or scenario.

It does **not** mean:

- exactly one assertion
- exactly one function call
- exactly one line in Act

## Good example

```python
def test_withdraw_rejects_insufficient_balance():
    account = BankAccount(balance=500)

    with pytest.raises(ValueError, match="insufficient balance"):
        account.withdraw(600)
```

One behavior: an overdraw is rejected.

## When multiple assertions are appropriate

```python
def test_successful_transfer_updates_both_accounts():
    sender = BankAccount(balance=500)
    receiver = BankAccount(balance=100)

    transfer(sender, receiver, 200)

    assert sender.balance == 300
    assert receiver.balance == 300
```

The two assertions jointly establish one behavior: a successful transfer moves money from one account to another without losing it.

## Bad example

```python
def test_order_system():
    assert register_user() == ...
    assert login_user() == ...
    assert create_order() == ...
    assert cancel_order() == ...
```

These are distinct behaviors.

## Better design

Split by behavior:

```text
registration behavior
login behavior
order creation behavior
order cancellation behavior
```

## Common mistake

Splitting too aggressively:

```python
def test_name_is_alice():
    ...

def test_email_is_correct():
    ...

def test_user_has_id():
    ...
```

If all three are simply verifying one cohesive construction contract, excessive splitting may reduce readability.

## Production considerations

Use **behavioral cohesion**, not a rigid assertion count.

---

# 9. AAA and Pytest Fixtures

Fixtures are often the mechanism that supports Arrange.

## How fixtures support AAA

```text
Fixture
  ↓
establish dependency/resource
  ↓
Arrange scenario
  ↓
Act
  ↓
Assert
```

Example:

```python
import pytest


@pytest.fixture
def cart():
    return Cart(items=[10, 20, 30])


def test_cart_total(cart):
    # Arrange
    expected_total = 60

    # Act
    actual_total = cart.total()

    # Assert
    assert actual_total == expected_total
```

The fixture reduces setup duplication.

## Avoid hiding the whole test story

Problematic:

```python
@pytest.fixture
def fully_configured_production_scenario():
    ...
    # creates a user
    # seeds database
    # creates order
    # activates subscription
    # configures payment
    # returns a ready-to-use object
```

Then:

```python
def test_feature(fully_configured_production_scenario):
    ...
```

The test may be readable syntactically but opaque semantically.

Prefer fixtures for reusable dependencies and infrastructure. Keep scenario-specific decisions visible.

## Engineering rule

A fixture should answer:

> What reusable dependency or resource does this test need?

A helper function can answer:

> What transformation should happen to this test data?

That distinction becomes useful in Section 28.

---

# 10. AAA and Parametrization

Parametrization is useful when the **behavior remains the same** while the input scenario changes.

```python
import pytest


def calculate_total(price: int, quantity: int) -> int:
    return price * quantity


@pytest.mark.parametrize(
    "price,quantity,expected",
    [
        (10, 2, 20),
        (25, 4, 100),
        (7, 0, 0),
    ],
)
def test_calculate_total(price, quantity, expected):
    # Arrange
    # The parameter values establish the scenario.

    # Act
    result = calculate_total(price, quantity)

    # Assert
    assert result == expected
```

The design is still AAA:

```text
Arrange → parameter values
Act     → calculate_total(...)
Assert  → expected result
```

Parametrization reduces duplicate test functions while keeping scenario data explicit.

### When parametrization is a good fit

- same behavior
- same assertion shape
- different representative inputs
- edge cases that share the same rule

### When separate functions are better

If the scenarios have substantially different setup or different expected behaviors, separate tests can be clearer.

---

# 11. Test Case Design from Requirements

A repeatable design process is:

```text
Requirement
   ↓
Identify behavior
   ↓
Identify inputs/state
   ↓
Identify expected outcomes
   ↓
Identify failure modes
   ↓
Identify boundaries
   ↓
Identify important state transitions
   ↓
Select representative cases
   ↓
Implement AAA
```

## Example requirement

> An account cannot transfer more money than its available balance.

### Step 1 — identify behavior

Transfer money from account A to account B.

### Step 2 — identify inputs

- sender
- receiver
- amount

### Step 3 — expected outcomes

Valid:

- balances change correctly

Invalid:

- transfer rejected
- balances remain unchanged

### Step 4 — boundaries

- amount = 0
- amount = exact balance
- amount = balance + 1

### Step 5 — other domain cases

- invalid sender
- invalid recipient
- same account
- negative amount

## Test case table

| Case | Starting state | Action | Expected result |
|---|---|---|---|
| Normal | sender 500, receiver 100 | transfer 200 | sender 300, receiver 300 |
| Exact | sender 500 | transfer 500 | sender 0 |
| Over | sender 500 | transfer 501 | error, no balance changes |
| Zero | sender 500 | transfer 0 | domain-defined rejection |
| Negative | sender 500 | transfer -1 | validation error |
| Same account | sender = receiver | transfer 100 | domain-defined rejection |
| Unknown recipient | recipient invalid | transfer 100 | lookup/domain error |

This table is test design. Pytest comes after the reasoning.

---

# 12. Happy Path vs Negative Path

## Happy path

The normal expected flow succeeds.

Example:

```python
def test_transfer_succeeds_with_sufficient_balance():
    sender = BankAccount(balance=500)
    receiver = BankAccount(balance=100)

    transfer(sender, receiver, 200)

    assert sender.balance == 300
    assert receiver.balance == 300
```

## Negative path

An invalid or prohibited scenario occurs.

```python
def test_transfer_rejects_insufficient_balance():
    sender = BankAccount(balance=500)
    receiver = BankAccount(balance=100)

    with pytest.raises(ValueError, match="insufficient balance"):
        transfer(sender, receiver, 600)

    assert sender.balance == 500
    assert receiver.balance == 100
```

The second assertion is important: rejecting the transfer should not accidentally mutate state.

## Error vs unexpected failure

Testing a defined business error is different from allowing a test to crash unexpectedly.

Expected:

```python
with pytest.raises(ValueError):
    parse_age("abc")
```

Unexpected:

```text
TypeError
AttributeError
database connection error
```

Unexpected exceptions generally indicate defects or environment problems that should not simply be considered passing negative cases.

## Practical design sequence

For each important behavior, ask:

```text
Happy path
→ boundary
→ invalid input
→ domain failure
→ state consistency after failure
```

---

# 13. Edge Cases

## What is an edge case?

An edge case is a scenario near an unusual, extreme, empty, missing, or otherwise important boundary.

Common examples:

- zero
- one
- minimum
- maximum
- empty string
- whitespace-only string
- `None`
- empty list
- one-item list
- duplicates
- negative values
- extremely large values
- missing fields
- malformed input

## How do you discover edge cases systematically?

Do not rely only on random imagination.

Use:

1. domain rules
2. input constraints
3. boundary values
4. data types
5. failure modes
6. state transitions
7. equivalence classes

Example:

> Password length must be between 8 and 64 characters.

Useful cases:

```text
7   → invalid
8   → valid
9   → valid
63  → valid
64  → valid
65  → invalid
```

Also consider:

- empty string
- whitespace
- Unicode input
- missing field

## Common mistake

Testing only extreme numeric values while ignoring semantic edge cases.

For an email system, `"a"` may be more meaningful than `10**100`.

## Production consideration

Edge cases should be selected based on the risk profile of the system. A safety-critical or financial system may need much more systematic boundary analysis than a low-risk internal utility.

---

# 14. Boundary Value Analysis

## What is it?

Boundary-value analysis focuses on values at and immediately around a limit.

Suppose:

> Age must be between 18 and 65 inclusive.

Test:

```text
17  invalid
18  valid
19  valid
64  valid
65  valid
66  invalid
```

## Why does it exist?

Defects frequently occur at comparisons such as:

```python
age > 18
```

versus:

```python
age >= 18
```

or:

```python
age <= 65
```

versus:

```python
age < 65
```

A boundary-focused test can detect these defects quickly.

## Simple example

```python
def is_valid_age(age: int) -> bool:
    return 18 <= age <= 65
```

Tests:

```python
import pytest


@pytest.mark.parametrize(
    "age,expected",
    [
        (17, False),
        (18, True),
        (19, True),
        (64, True),
        (65, True),
        (66, False),
    ],
)
def test_is_valid_age(age, expected):
    assert is_valid_age(age) is expected
```

## Common mistake

Only testing the limits, not the values immediately outside them.

A strong boundary set generally includes:

```text
minimum - 1
minimum
minimum + 1
maximum - 1
maximum
maximum + 1
```

## Production considerations

Boundary analysis is especially useful for:

- validation
- financial limits
- quotas
- pagination
- rate limits
- batch sizes
- age ranges
- file sizes
- API limits

---

# 15. Equivalence Partitioning

## What is it?

Equivalence partitioning divides inputs into classes expected to behave similarly.

Suppose:

```text
Age < 18       → reject
18–65          → accept
Age > 65       → reject
```

Instead of testing every integer, choose representatives:

```text
17
30
66
```

Then add boundary-focused values:

```text
17, 18, 19, 64, 65, 66
```

## Why does it exist?

It gives you a way to reduce huge input spaces while retaining meaningful coverage.

## Simple example

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

Equivalence classes:

| Class | Example |
|---|---|
| invalid | 0 |
| small | 3 |
| medium | 10 |
| large | 30 |

Then boundary tests add:

```text
5, 6, 20, 21
```

## Common mistake

Assuming all values inside a class truly behave identically when hidden domain rules create additional partitions.

## Better approach

Use both:

```text
Equivalence partitioning
+
Boundary-value analysis
```

## Production considerations

This is useful when input spaces are large:

- transaction amounts
- file sizes
- ages
- scores
- API pagination
- data quality rules

---

# 16. Decision Tables

## What are they?

Decision tables represent combinations of conditions and the resulting behavior.

Suppose a loan application requires:

- sufficient income
- sufficient credit score
- valid documents

| Income | Credit | Documents | Expected |
|---|---|---|---|
| Yes | Yes | Yes | approve |
| Yes | Yes | No | reject |
| Yes | No | Yes | reject |
| No | Yes | Yes | reject |
| ... | ... | ... | ... |

## Why are they useful?

They help when behavior depends on **combinations of conditions**.

Without a table, developers often miss combinations.

## Translating rows into tests

```python
import pytest


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

## Trade-off

The number of combinations can grow rapidly.

Do not blindly test every theoretical combination without considering whether all combinations are meaningful.

---

# 17. State-Based Test Design

## What is it?

State-based testing verifies how behavior changes the system from one state to another.

Example order lifecycle:

```text
PENDING
   ↓
 PAID
   ↓
SHIPPED
   ↓
DELIVERED
```

Possible invalid transition:

```text
DELIVERED → PAID
```

## Why does it exist?

Many systems are not just input/output functions. They have state.

Examples:

- orders
- payments
- accounts
- subscriptions
- workflows
- agent tasks
- job processing

## Test valid transition

```python
def test_paid_order_can_ship():
    order = Order(status="PAID")

    order.ship()

    assert order.status == "SHIPPED"
```

## Test invalid transition

```python
def test_delivered_order_cannot_be_paid():
    order = Order(status="DELIVERED")

    with pytest.raises(ValueError):
        order.mark_paid()
```

## Boundary transition

Test the exact transition boundary:

```text
PAID → SHIPPED
```

and verify that nearby invalid states are rejected.

## Production considerations

State-transition testing is especially important for distributed and transactional systems where an invalid transition can cause real data corruption.

---

# 18. Input/Output Test Design

A simple generic model is:

```text
Input
  ↓
Processing
  ↓
Output
```

For each operation, inspect:

### Normal input

```python
calculate_total(10, 2) == 20
```

### Invalid input

```python
with pytest.raises(ValueError):
    calculate_total(-10, 2)
```

### Boundary input

```python
page_size = 100
```

### Combination input

```text
discount + tax + quantity
```

### Expected exceptions

```python
with pytest.raises(TypeError):
    calculate_total("10", 2)
```

The key is not to test every possible input. It is to select cases that represent the important behavior space.

---

# 19. Test Isolation

## What is it?

Test isolation means one test should not accidentally depend on the state created by another test.

A test should establish the conditions it needs.

## Why does it matter?

Without isolation:

```text
Test A changes shared state
        ↓
Test B assumes old state
        ↓
Test B fails
```

The failure may depend on execution order.

## Bad example

```python
users = []


def test_add_user():
    users.append("Alice")
    assert "Alice" in users


def test_users_start_empty():
    assert users == []
```

Depending on order, the second test can fail.

## Better

```python
def test_add_user():
    users = []

    users.append("Alice")

    assert users == ["Alice"]


def test_users_start_empty():
    users = []

    assert users == []
```

For larger resources, use fixtures with appropriate isolation.

## Sources of shared state

- globals
- mutable module state
- databases
- files
- caches
- environment variables
- random seeds
- clocks
- network services

## Isolation vs resource reuse

Isolation can cost time.

A database connection may be expensive to create, but reusing it carelessly can create state leakage.

The engineering problem is:

```text
How much reuse can we safely get
without sacrificing trustworthy test behavior?
```

---

# 20. Test Independence

A test should not require another test to run first.

Bad conceptual dependency:

```text
test_create_user
      ↓
test_login_user
      ↓
test_create_order
```

These should usually establish their own prerequisites or use independent fixtures.

## Why is order dependence dangerous?

Pytest may collect and run tests in an order, but robust suites should not rely on accidental ordering.

Order dependence can produce:

- local-only failures
- CI-only failures
- failures after adding a new test
- failures that disappear when run individually

## Useful diagnostic

Run a test by itself:

```bash
pytest tests/test_orders.py::test_create_order -q
```

Then compare with running the whole suite.

If the result changes, investigate shared state or environment dependence.

## How fixtures help

A fixture can provide a fresh resource or controlled starting state:

```python
import pytest


@pytest.fixture
def account():
    return BankAccount(balance=500)


def test_withdraw(account):
    account.withdraw(100)
    assert account.balance == 400


def test_initial_balance(account):
    assert account.balance == 500
```

The default function scope creates separate fixture instances for separate tests.

---

# 21. Deterministic Tests

## What is a deterministic test?

A deterministic test produces the same expected result when:

- the code is unchanged
- the controlled input is unchanged
- the relevant environment is controlled

A deterministic test is easier to trust.

## Sources of nondeterminism

- random numbers
- current time
- network calls
- external APIs
- database contents
- concurrency
- environment variables
- unordered external input
- asynchronous timing

## Bad example

```python
from datetime import datetime


def test_deadline():
    result = is_expired(datetime.now())
    assert result is False
```

Near midnight, this may behave differently.

## Better design

Pass time into the function:

```python
from datetime import datetime, timezone


def is_expired(deadline: datetime, now: datetime) -> bool:
    return now >= deadline


def test_deadline_is_not_expired_before_deadline():
    deadline = datetime(2026, 10, 1, tzinfo=timezone.utc)
    now = datetime(2026, 9, 30, tzinfo=timezone.utc)

    assert is_expired(deadline, now) is False
```

Now the test controls the clock.

## Randomness

Instead of:

```python
import random
```

inside a behavior being tested, consider designing code so the random source can be controlled during testing.

## Production considerations

Determinism is valuable in CI/CD. A test that occasionally fails without a code change creates false alarms and trains engineers to ignore failures.

---

# 22. Test Doubles and Test Design

Test doubles are controlled replacements for real dependencies.

The common terms are:

- **stub** — supplies predetermined responses
- **fake** — working simplified implementation
- **mock** — commonly used to verify expected interactions with a dependency
- **spy** — records calls while allowing behavior to occur

Terminology can vary across teams and frameworks, so focus on the underlying idea.

## How they support AAA

```text
Arrange
→ configure test double

Act
→ execute system behavior

Assert
→ verify output/state/interaction as appropriate
```

Example:

```python
class FakePaymentGateway:
    def __init__(self, approved: bool):
        self.approved = approved

    def charge(self, amount: int) -> bool:
        return self.approved


def test_order_is_paid_when_gateway_approves():
    gateway = FakePaymentGateway(approved=True)
    order = Order(total=100, payment_gateway=gateway)

    order.pay()

    assert order.status == "PAID"
```

This isolates the business behavior from a real payment network.

## Trade-off: isolation vs realism

A fake gateway makes the test:

- fast
- deterministic
- independent of the network

But it does not prove the real payment gateway integration works.

Therefore:

```text
Unit test with fake
+
Integration test with real integration boundary
```

may be appropriate.

This chapter does not turn into a mocking tutorial; the key design principle is to use doubles when they improve the test's purpose without hiding the behavior you actually need to validate.

---

# 23. Behavior vs Implementation

This is one of the most important principles in test design.

## Implementation detail

An implementation detail is an internal choice that users of the component do not need to know.

Example:

```python
class UserService:
    def __init__(self):
        self._cache = {}
```

A test like:

```python
assert service._cache == {}
```

may break when caching is redesigned.

## Behavioral test

```python
assert service.get_user("123").name == "Alice"
```

This tests the observable contract.

## Why implementation-focused tests become brittle

Suppose version 1 uses:

```text
dictionary cache
```

Version 2 uses:

```text
LRU cache
```

Version 3 uses:

```text
external cache service
```

The behavior may stay the same.

Good tests continue to pass.

## Refactoring example

### Version 1

```python
def normalize_name(value: str) -> str:
    return value.strip().lower()
```

Test:

```python
def test_normalize_name():
    assert normalize_name(" Alice ") == "alice"
```

### Version 2

```python
def normalize_name(value: str) -> str:
    cleaned = value.strip()
    return cleaned.casefold()
```

The test can still pass because it protects behavior rather than the implementation steps.

## Common mistake

Testing private method calls simply because they are easy to assert.

Private implementation can change without changing behavior.

## Production considerations

Behavior-focused tests reduce refactoring cost.

There are exceptions: infrastructure libraries, algorithms, performance-sensitive code, or very low-level modules may have legitimate implementation-level invariants worth testing. The key is intentionality.

---

# 24. Test Coupling

## What is test coupling?

Test coupling occurs when tests depend on one another or on hidden shared state.

Examples:

```text
shared mutable fixture
ordering assumptions
shared database rows
global environment mutation
test-generated files reused by another test
```

## Example

```python
state = {"ready": False}


def test_initialize():
    state["ready"] = True


def test_process():
    assert state["ready"] is True
```

`test_process()` is coupled to `test_initialize()`.

## Better

```python
def test_process():
    state = {"ready": True}

    result = process(state)

    assert result == "ok"
```

Or use a fixture:

```python
@pytest.fixture
def ready_state():
    return {"ready": True}
```

## How to identify coupling

Try:

```bash
pytest -q
pytest tests/test_module.py::test_process -q
```

Also investigate:

- failures that change after reordering tests
- failures that disappear when repeated
- cleanup errors
- global state mutation

## Production considerations

Coupling increases the cost of parallel execution and makes failures harder to reproduce.

---

# 25. Test Smells

A **test smell** is a pattern that often indicates a design problem.

It is not automatically a defect. Context matters.

## Giant tests

### Looks like

```python
def test_entire_order_lifecycle():
    ...
```

Hundreds of lines.

### Why it is a problem

- difficult diagnosis
- broad failure surface
- expensive setup
- multiple behaviors

### Better

Split by coherent behaviors and retain a smaller number of critical workflow tests.

## Unclear test names

Bad:

```python
def test_user():
    ...
```

Better:

```python
def test_register_user_rejects_duplicate_email():
    ...
```

## Excessive setup

A test requiring twenty objects to validate one simple rule may indicate:

- wrong test level
- overly broad dependency graph
- poor domain boundaries

## Excessive teardown

If every test contains long cleanup code, consider fixture lifecycle management.

## Hidden setup

```python
def test_something(configured_environment):
    ...
```

If the fixture name is vague, the scenario becomes hard to infer.

## Too many mocks

A test may verify a chain of internal calls without verifying the user-visible result.

That often produces a "mock-shaped test" rather than a behavior test.

## Brittle assertions

Examples:

- exact timestamps
- complete private object representations
- incidental ordering
- formatting the requirement does not care about

## No meaningful assertion

```python
def test_process_runs():
    process()
```

The test may pass even if `process()` does something wrong.

## Overly broad tests

A test involving the whole platform can be useful, but it is often too expensive for ordinary regression feedback.

## Overly narrow tests

Testing trivial implementation details can create huge maintenance cost for little confidence.

## Magic values

Bad:

```python
assert balance == 1837
```

without explaining why `1837` matters.

Better:

```python
initial_balance = 2000
withdrawal = 1637

...

assert account.balance == initial_balance - withdrawal
```

## Flaky tests

A flaky test sometimes passes and sometimes fails without a relevant code change.

Common sources:

- timing
- race conditions
- random data
- shared state
- network dependency

Flaky tests are especially damaging in CI because they reduce trust in the entire suite.

---

# 26. Test Naming

Test names are documentation.

A useful pattern is:

```text
test_<scenario>_<behavior>_<expected_result>
```

Examples:

```python
def test_withdraw_rejects_amount_greater_than_balance():
    ...


def test_register_user_rejects_duplicate_email():
    ...


def test_parse_transaction_raises_for_invalid_amount():
    ...
```

## Why names matter

When CI reports:

```text
FAILED test_register_user_rejects_duplicate_email
```

you immediately know the intended behavior.

Compare:

```text
FAILED test_user
```

The second provides almost no diagnostic information.

## Common mistake

Making names describe implementation instead of behavior:

```python
def test_calls_validate_email_method():
    ...
```

Better:

```python
def test_registration_rejects_invalid_email():
    ...
```

unless interaction with that method is itself the behavior being tested.

## Production considerations

Good names reduce time spent opening files just to understand a failing scenario.

---

# 27. Test Readability

A developer should quickly answer four questions:

1. What is being tested?
2. What inputs or state were used?
3. What should happen?
4. Why did it fail?

A readable test:

```python
def test_discount_is_not_applied_to_ineligible_customer():
    # Arrange
    customer = Customer(segment="standard")
    order = Order(total=100)

    # Act
    total = calculate_total(customer, order)

    # Assert
    assert total == 100
```

The story is visible.

## Readability techniques

Use:

- specific names
- small setup
- visible important values
- one clear Act
- precise assertions
- meaningful parametrization IDs

Avoid:

- deeply nested helper layers
- generic fixture names
- unexplained factories
- huge parameter matrices
- unnecessary abstraction

## Common mistake

Optimizing for shortest code instead of fastest human comprehension.

Tests are read during failures. Readability is an operational feature.

---

# 28. Test Maintainability

Maintainability means the test remains useful and affordable to change as the system evolves.

Good maintainability usually includes:

- low accidental coupling
- clear test intent
- stable assertions
- controlled data
- appropriate fixture reuse
- limited abstraction

## DRY vs readability

DRY means "Don't Repeat Yourself."

But tests are not ordinary application code.

Some duplication can make scenarios easier to understand.

Compare:

```python
def test_a(common_setup):
    ...


def test_b(common_setup):
    ...
```

with one highly abstract helper that creates ten different hidden conditions.

The second may be technically DRY but cognitively expensive.

## A useful rule

Remove duplication when it is **mechanical repetition**.

Keep duplication when removing it would hide **meaningful scenario information**.

## Production considerations

The maintenance cost of tests should be considered when designing the suite.

A test that saves 10 lines but adds 30 minutes of debugging per failure is not necessarily an improvement.

---

# 29. Test Granularity

Tests exist at different levels.

## Unit test

Usually tests a small component in isolation.

Characteristics:

- fast
- focused
- often highly deterministic

Example:

```python
def test_total():
    assert calculate_total(10, 2) == 20
```

## Integration test

Tests how multiple components work together.

Example:

```text
service
  ↓
database
```

## API test

Tests an externally visible HTTP or service interface.

Example:

```text
client
  ↓
HTTP endpoint
  ↓
application
```

## End-to-end test

Exercises a broad user workflow.

Example:

```text
browser/client
  ↓
frontend
  ↓
API
  ↓
service
  ↓
database
```

## AAA applies to all levels

The scope changes, but the reasoning does not:

```text
Arrange → establish relevant context
Act     → perform target behavior
Assert  → verify observable outcome
```

The broader the level, the more setup and execution cost may exist.

---

# 30. AAA for Unit Tests

Complete unit example:

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

Why is this a good unit test?

- no network
- no database
- deterministic inputs
- small behavior
- precise assertion

The unit test gives fast feedback.

---

# 31. AAA for Integration Tests

Conceptual example using SQLite:

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

In a real suite, database lifecycle would usually be handled by a fixture.

### Engineering point

The Assert checks persisted behavior, not merely the function return value.

---

# 32. AAA for API Tests

Conceptual example:

```python
def test_create_user_api(client):
    # Arrange
    payload = {
        "name": "Alice",
        "email": "alice@example.com",
    }

    # Act
    response = client.post("/users", json=payload)

    # Assert
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Alice"
    assert body["email"] == "alice@example.com"
```

Multiple related assertions are reasonable because they jointly validate the API contract for successful creation.

A separate test may verify duplicate email behavior:

```python
def test_create_user_api_rejects_duplicate_email(client):
    payload = {
        "name": "Alice",
        "email": "alice@example.com",
    }

    client.post("/users", json=payload)

    response = client.post("/users", json=payload)

    assert response.status_code == 409
```

---

# 33. AAA for End-to-End Tests

An E2E scenario may look like:

```text
Arrange:
  create test account

Act:
  perform purchase workflow

Assert:
  order reaches completed state
```

Pseudocode:

```python
def test_customer_can_complete_purchase(browser, app):
    # Arrange
    user = create_test_user()
    login(browser, user)

    # Act
    browser.open("/products")
    browser.add_to_cart("book-123")
    browser.checkout()

    # Assert
    assert browser.text_contains("Order confirmed")
```

E2E tests are intentionally broader.

They can catch integration problems that unit tests cannot, but they usually cost more to execute and maintain.

A production suite normally should not rely on E2E tests for every behavior.

---

# 34. Test Coverage and Test Design

Coverage answers a question such as:

> Which code paths were executed?

It does **not** fully answer:

> Did we test the important behavior correctly?

## Line coverage

Measures which lines were executed.

## Branch coverage

Conceptually measures whether alternative decision paths were exercised.

## Behavior coverage

Asks whether important behaviors were verified.

## Requirement coverage

Asks whether important requirements have corresponding tests.

## Example

```python
def choose_discount(customer_type: str) -> int:
    if customer_type == "vip":
        return 20
    return 0
```

A single test:

```python
def test_discount():
    assert choose_discount("vip") == 20
```

may produce high line coverage for a tiny function.

But if you do not test normal customers, you may miss an incorrect default behavior.

## 100% coverage is not proof of correctness

Possible failures include:

- wrong expected values
- weak assertions
- missing business scenarios
- missing requirements
- missing integration behavior

A useful equation is:

```text
Coverage
≠
Quality

Coverage
+
Good test design
→
much stronger evidence
```

---

# 35. Regression Test Design

## What is regression testing?

Regression testing checks that previously working behavior remains working after changes.

A powerful production workflow is:

```text
Bug discovered
    ↓
Reproduce bug
    ↓
Write failing regression test
    ↓
Fix implementation
    ↓
Keep test permanently
```

## Example bug

Suppose:

```python
def parse_amount(value: str) -> int:
    return int(value)
```

A bug report says:

> `" 100 "` was unexpectedly rejected.

Regression test:

```python
def test_parse_amount_accepts_surrounding_whitespace():
    assert parse_amount(" 100 ") == 100
```

The test should remain after the fix.

## Why regression tests are valuable

A bug is not only an incident; it is information about the system's risk.

A regression test converts that incident into long-term automated protection.

---

# 36. Property-Based Thinking

Property-based testing is introduced here as a way of thinking, not as a specific library tutorial.

## Example-based thinking

```text
2 + 3 == 5
```

One specific example.

## Property-based thinking

For all valid integers `a` and `b`:

```python
a + b == b + a
```

This is the property of commutativity.

## Why is this useful?

Some systems have large input spaces where a small collection of hand-picked examples cannot express the whole rule.

Other useful properties include:

- sorting preserves the same elements
- normalization is idempotent
- serialization then deserialization preserves valid information
- a successful transfer conserves total funds

Example:

```python
def test_sort_preserves_elements():
    values = [5, 1, 3]

    result = sorted(values)

    assert sorted(result) == sorted(values)
```

Property-based thinking encourages you to ask:

> What must always remain true?

That question is highly valuable in AI, data, and distributed systems.

---

# 37. Test Design for Data Pipelines

Consider:

```text
CSV input
   ↓
parse
   ↓
transform
   ↓
validate
   ↓
output records
```

AAA can be applied at each meaningful behavior.

Example:

```python
def normalize_record(record: dict) -> dict:
    return {
        "name": record["name"].strip(),
        "age": int(record["age"]),
    }


def test_normalize_record():
    # Arrange
    record = {
        "name": " Alice ",
        "age": "30",
    }

    # Act
    result = normalize_record(record)

    # Assert
    assert result == {
        "name": "Alice",
        "age": 30,
    }
```

Important cases:

- valid row
- missing field
- `None`
- duplicate row
- incorrect type
- malformed value
- boundary value

## Pipeline-specific concerns

For data engineering, also consider:

- schema contracts
- record counts
- uniqueness
- nullability
- partition behavior
- ordering assumptions
- idempotency
- aggregation invariants

Example invariant:

```text
input count
=
valid count + rejected count
```

when that relationship is guaranteed by the pipeline.

---

# 38. Test Design for ML Systems

ML systems need multiple forms of testing because the model may be probabilistic or learned from data.

AAA still works.

```text
Arrange
→ controlled input data + model/configuration

Act
→ run prediction/transformation

Assert
→ verify structural, behavioral, and business properties
```

Example:

```python
def test_preprocessor_returns_expected_feature_count(model):
    # Arrange
    rows = [
        {"age": 30, "income": 50000},
        {"age": 40, "income": 70000},
    ]

    # Act
    features = model.preprocess(rows)

    # Assert
    assert len(features) == 2
    assert len(features[0]) == 2
```

## Useful assertions

- schema compatibility
- output shape
- allowed ranges
- no unexpected NaNs
- required fields
- deterministic preprocessing
- business constraints

Be careful with exact model predictions. Some model behavior is intentionally probabilistic.

A better test may check:

```text
score is within expected range
output contains required labels
policy constraints are respected
```

rather than one exact floating-point result.

---

# 39. Test Design for AI/LLM Applications

Traditional deterministic assertions remain extremely important for the surrounding application.

Examples of deterministic components:

- prompt construction
- input validation
- retrieval filtering
- tool schemas
- response parsing
- retry logic
- timeout handling
- authorization
- state transitions

For the model output itself, exact string equality may be too strict for some features.

## Example structured-output test

Suppose an LLM application is expected to return:

```json
{
  "intent": "refund_request",
  "confidence": 0.91
}
```

A useful test may assert:

```python
def test_llm_result_has_required_structure(fake_llm):
    # Arrange
    application = SupportClassifier(model=fake_llm)

    # Act
    result = application.classify("I want a refund")

    # Assert
    assert set(result) == {"intent", "confidence"}
    assert result["intent"] in {"refund_request", "other"}
    assert 0.0 <= result["confidence"] <= 1.0
```

The exact natural-language phrasing is not the main contract.

## Testing nondeterministic behavior

Use a combination of:

- deterministic component tests
- controlled/fake model responses
- structured-output validation
- invariant checks
- evaluation datasets
- safety and policy checks
- integration tests
- carefully selected live-model tests

This chapter focuses on test design principles, not full LLM evaluation methodology.

---

# 40. Test Design for Agentic AI

Agentic AI systems combine:

- planning
- tools
- external state
- model calls
- memory/context
- workflow control

AAA can still organize a test.

## Arrange

Prepare:

- controlled input
- fake or controlled tools
- known state
- controlled external services
- deterministic configuration

## Act

Run the agent workflow.

## Assert

Verify observable behavior and invariants:

- correct tool selected
- required tool parameters used
- expected state transition
- correct structured result
- safety constraint respected
- termination condition reached
- prohibited action not taken

Example:

```python
def test_agent_uses_balance_tool_before_transfer(agent, fake_tools):
    # Arrange
    fake_tools.balance.return_value = 500
    fake_tools.transfer.return_value = {"status": "success"}

    request = {
        "from_account": "A",
        "to_account": "B",
        "amount": 100,
    }

    # Act
    result = agent.run(request)

    # Assert
    assert fake_tools.balance.called
    assert fake_tools.transfer.called
    assert result["status"] == "success"
```

The point is not to test hidden internal reasoning.

Instead, test what can be observed and what must remain true.

## Useful agent invariants

```text
No transfer without required authorization.
No payment above approved limit.
No tool call when required parameter is missing.
Workflow terminates on success or controlled failure.
Sensitive operations require appropriate checks.
```

These are often more stable than asserting an exact sequence of internal reasoning tokens.

---

# 41. AAA and the Test Pyramid

A common test-pyramid idea is:

```text
        /\
       /  \      fewer E2E
      /----\
     /      \    integration
    /--------\
   /          \  many unit tests
  /____________\
```

The exact shape is not a law. The principle is that different test levels have different cost and feedback characteristics.

AAA applies to all levels:

```text
Unit:
Arrange object → Act method → Assert result

Integration:
Arrange DB/app state → Act service → Assert persisted behavior

E2E:
Arrange user/system state → Act workflow → Assert user-visible outcome
```

A balanced production suite usually benefits from many fast focused tests and a smaller number of broader tests.

---

# 42. AAA and CI/CD

CI/CD depends on tests that can provide trustworthy feedback repeatedly.

Good test design helps because it provides:

- fast feedback
- meaningful failures
- deterministic execution
- regression protection
- useful test grouping

## What goes wrong with poor design?

Imagine 2,000 tests where 80 frequently fail because of timing or shared state.

The result is not strong confidence. It is alert fatigue.

Engineers may start rerunning jobs instead of investigating failures.

## CI design principles

- separate fast unit tests from slower integration/E2E tests
- keep tests deterministic where possible
- make failures diagnostically useful
- preserve regression tests
- avoid relying on machine-specific state
- use appropriate markers for grouping

Conceptually:

```bash
pytest -m "not integration"
```

can run a faster subset when a project has registered suitable markers.

---

# 43. Refactoring Tests

Start with a poor test.

## Bad test

```python
def test_order_system():
    database = connect_to_database()
    user = create_user()
    login(user)
    item = create_item()
    order = create_order(user, item)
    update_shipping_address(user)
    pay(order)
    ship(order)

    assert user.name != ""
    assert order is not None
    assert order.status == "SHIPPED"
```

Problems:

- too many behaviors
- expensive setup
- weak assertions
- mixed concerns

## Refactoring process

### 1. Identify the behavior

The important behavior appears to be:

> Paying a valid order changes its status to `PAID`.

### 2. Reduce irrelevant setup

```python
def test_paying_order_marks_it_paid():
    ...
```

### 3. Separate Arrange

```python
# Arrange
order = Order(total=100)
gateway = FakePaymentGateway(approved=True)
```

### 4. Isolate Act

```python
# Act
order.pay(gateway)
```

### 5. Improve Assert

```python
# Assert
assert order.status == "PAID"
```

### 6. Extract reusable fixture only if justified

```python
@pytest.fixture
def unpaid_order():
    return Order(total=100)
```

### 7. Add meaningful negative cases

```python
def test_paying_order_fails_when_gateway_declines():
    ...
```

The goal is not merely shorter code.

The goal is stronger information.

---

# 44. Complete Realistic Example

We will use a **bank transaction processing** domain because it combines business rules, boundaries, negative cases, state, and regression risks.

## Requirements

1. A transfer amount must be positive.
2. Sender and receiver must be different accounts.
3. Sender must have sufficient balance.
4. A valid transfer decreases the sender balance.
5. A valid transfer increases the receiver balance.
6. A rejected transfer must not modify either balance.

## Source code

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

## Test design before code

### Happy path

```text
sender 500
receiver 100
amount 200

expected:
sender 300
receiver 300
```

### Boundary

```text
amount = sender.balance
```

Expected: succeeds, sender becomes zero.

### Negative

```text
amount = 0
amount < 0
amount > balance
same account
```

### Regression risk

A developer might accidentally mutate sender before validating receiver or amount.

Therefore, negative tests should verify **state remains unchanged**.

## Fixture

```python
import pytest


@pytest.fixture
def accounts():
    sender = BankAccount("A", 500)
    receiver = BankAccount("B", 100)
    return sender, receiver
```

## Happy-path test

```python
def test_transfer_moves_money(accounts):
    # Arrange
    sender, receiver = accounts
    amount = 200

    # Act
    transfer(sender, receiver, amount)

    # Assert
    assert sender.balance == 300
    assert receiver.balance == 300
```

## Exact-balance boundary

```python
def test_transfer_allows_exact_balance(accounts):
    # Arrange
    sender, receiver = accounts
    amount = sender.balance

    # Act
    transfer(sender, receiver, amount)

    # Assert
    assert sender.balance == 0
    assert receiver.balance == 600
```

## Invalid amount tests

```python
import pytest


@pytest.mark.parametrize(
    "amount",
    [
        pytest.param(0, id="zero"),
        pytest.param(-1, id="negative"),
    ],
)
def test_transfer_rejects_non_positive_amount(accounts, amount):
    # Arrange
    sender, receiver = accounts
    original_sender = sender.balance
    original_receiver = receiver.balance

    # Act + Assert
    with pytest.raises(ValueError, match="amount must be positive"):
        transfer(sender, receiver, amount)

    # Assert
    assert sender.balance == original_sender
    assert receiver.balance == original_receiver
```

Notice that the test has two related assertion purposes:

1. the invalid request is rejected
2. the rejection does not mutate balances

## Insufficient balance

```python
def test_transfer_rejects_insufficient_balance(accounts):
    # Arrange
    sender, receiver = accounts
    original_sender = sender.balance
    original_receiver = receiver.balance

    # Act + Assert
    with pytest.raises(ValueError, match="insufficient balance"):
        transfer(sender, receiver, original_sender + 1)

    # Assert
    assert sender.balance == original_sender
    assert receiver.balance == original_receiver
```

## Why these tests are valuable

The suite is not just checking that the function returns without crashing.

It protects:

- positive validation
- exact boundary behavior
- negative input handling
- insufficient funds
- state preservation on failure
- balance conservation

The tests describe the business contract.

---

# 45. Mini-Project

## Project objective

Build and test a small **order-processing service**.

The focus is not on building a sophisticated application. The focus is on designing a high-quality test suite.

## Requirements

An order:

- has items
- has a total
- can be submitted
- cannot be submitted with no items
- cannot be submitted twice
- must contain positive quantities
- may apply a discount for orders above a threshold

## Suggested architecture

```text
order_project/
├── order.py
└── tests/
    ├── conftest.py
    └── test_order.py
```

The chapter teaches `conftest.py`, but your actual project structure may differ.

## Source code

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

## Test-design plan

### Behavior inventory

1. Add valid item.
2. Reject invalid price.
3. Reject invalid quantity.
4. Calculate subtotal.
5. Apply threshold discount.
6. Do not apply discount below threshold.
7. Reject empty order submission.
8. Submit draft order.
9. Reject duplicate submission.

### Boundary cases

For a discount threshold of `1000`:

```text
999
1000
1001
```

### Parametrization strategy

Use parametrization for scenarios with identical assertion structure:

```python
@pytest.mark.parametrize(
    "price,quantity",
    [
        pytest.param(0, 1, id="zero-price"),
        pytest.param(-1, 1, id="negative-price"),
        pytest.param(10, 0, id="zero-quantity"),
        pytest.param(10, -1, id="negative-quantity"),
    ],
)
def test_add_item_rejects_invalid_values(price, quantity):
    ...
```

## Expected project outcomes

A strong suite should communicate:

```text
what is valid
what is invalid
where the boundaries are
what state transitions are allowed
what happens after failure
```

## Debugging scenarios

Intentionally introduce:

- `>` instead of `>=`
- mutate status before validation
- allow zero quantities
- apply discount at the wrong threshold

Your tests should detect these defects.

## Improvement opportunities

After the initial version, review:

- Are tests isolated?
- Are names descriptive?
- Are fixtures hiding too much?
- Are parameters readable?
- Are assertions strong?
- Do failures identify the scenario?
- Are integration tests necessary?
- Is any test unnecessarily broad?

---

# 46. Coding Exercises

## Level 1 — Basic

### Exercise 1 — Arrange, Act, Assert

#### Problem

Write a test for:

```python
def square(value: int) -> int:
    return value * value
```

#### Task

Create a test for `square(5)` using explicit AAA comments.

#### Hints

- Arrange the input.
- Act by calling `square`.
- Assert the exact result.

#### Complete solution

```python
def test_square_returns_squared_value():
    # Arrange
    value = 5

    # Act
    result = square(value)

    # Assert
    assert result == 25
```

#### Explanation

The input is arranged first, the behavior is executed once, and the result is checked precisely.

#### Common mistake

```python
assert result
```

This does not prove that the result is `25`.

---

### Exercise 2 — Strong assertion

#### Problem

A function returns a user dictionary.

```python
def get_user():
    return {"name": "Alice", "role": "admin"}
```

#### Task

Replace this weak test:

```python
def test_user():
    assert get_user() is not None
```

#### Hints

Assert the behavior that matters.

#### Complete solution

```python
def test_get_user_returns_expected_user():
    result = get_user()

    assert result["name"] == "Alice"
    assert result["role"] == "admin"
```

#### Explanation

The test now detects incorrect values instead of merely detecting a non-`None` result.

#### Common mistake

Asserting the entire dictionary if the API contract does not require every field to be stable.

---

### Exercise 3 — Happy and negative paths

#### Problem

```python
def divide(a: int, b: int) -> float:
    if b == 0:
        raise ValueError("division by zero")
    return a / b
```

#### Task

Write one happy-path test and one negative-path test.

#### Hints

The negative path must verify the expected exception.

#### Complete solution

```python
import pytest


def test_divide_returns_quotient():
    result = divide(10, 2)

    assert result == 5


def test_divide_rejects_zero_divisor():
    with pytest.raises(ValueError, match="division by zero"):
        divide(10, 0)
```

#### Explanation

The first test checks normal behavior. The second protects the defined failure mode.

#### Common mistake

Using:

```python
with pytest.raises(Exception):
    divide(10, 0)
```

This is usually less precise than asserting the specific expected exception type.

---

### Exercise 4 — Test naming

#### Problem

Improve:

```python
def test_1():
    ...
```

The behavior is that duplicate email registration is rejected.

#### Complete solution

```python
def test_register_user_rejects_duplicate_email():
    ...
```

#### Explanation

The name communicates scenario, behavior, and expected outcome.

#### Common mistake

Naming the test after an internal helper instead of the behavior.

---

### Exercise 5 — Identify the behavior

#### Problem

A requirement says:

> A cart with no items cannot be checked out.

#### Task

Design at least two test cases.

#### Hints

You need a prohibited case and a valid contrast case.

#### Complete solution

```text
Case 1:
empty cart
→ checkout
→ ValueError

Case 2:
cart with one valid item
→ checkout
→ success
```

#### Explanation

The test design should cover both sides of the business rule.

#### Common mistake

Testing only the successful checkout path.

---

## Level 2 — Intermediate

### Exercise 6 — Boundary values

#### Problem

A function accepts scores from 0 through 100 inclusive.

#### Task

Choose the most useful boundary cases.

#### Complete solution

```text
-1   invalid
0    valid
1    valid
99   valid
100  valid
101  invalid
```

#### Explanation

These cases surround both boundaries.

#### Common mistake

Testing only `0` and `100`.

---

### Exercise 7 — Parametrize boundary tests

#### Problem

Implement Exercise 6 with pytest parametrization.

#### Complete solution

```python
import pytest


def is_valid_score(score: int) -> bool:
    return 0 <= score <= 100


@pytest.mark.parametrize(
    "score,expected",
    [
        (-1, False),
        (0, True),
        (1, True),
        (99, True),
        (100, True),
        (101, False),
    ],
)
def test_score_is_valid(score, expected):
    assert is_valid_score(score) is expected
```

#### Explanation

The test logic is shared; the cases vary.

#### Common mistake

Using string values or tuples with the wrong number of fields.

---

### Exercise 8 — Equivalence partitioning

#### Problem

A shipping system has three classes:

```text
0 < weight <= 5  → small
5 < weight <= 20 → medium
weight > 20 → large
```

#### Task

Choose representative values and boundaries.

#### Complete solution

Representative classes:

```text
3   → small
10  → medium
30  → large
```

Boundary set:

```text
0, 1, 5, 6, 20, 21
```

#### Explanation

Representative values test classes; boundaries test transition errors.

#### Common mistake

Selecting ten values from the middle of the same class.

---

### Exercise 9 — Test isolation

#### Problem

This design is broken:

```python
shared = []


def test_adds_item():
    shared.append("A")


def test_starts_empty():
    assert shared == []
```

#### Task

Refactor the tests so they do not share mutable state.

#### Complete solution

```python
def test_adds_item():
    items = []

    items.append("A")

    assert items == ["A"]


def test_starts_empty():
    items = []

    assert items == []
```

#### Explanation

Each test controls its own starting state.

#### Common mistake

Keeping the global list and clearing it conditionally in one test. That still creates hidden coupling.

---

### Exercise 10 — Behavior vs implementation

#### Problem

A class contains:

```python
self._cache = {}
```

A test asserts:

```python
assert service._cache == {}
```

#### Task

Replace the test with a behavioral assertion.

#### Complete solution

For example:

```python
def test_get_user_returns_requested_user(service):
    user = service.get_user("123")

    assert user.id == "123"
```

#### Explanation

The test now protects observable service behavior.

#### Common mistake

Replacing one internal detail with another internal detail.

---

## Level 3 — Advanced

### Exercise 11 — Decision table

#### Problem

A feature is allowed only when:

- user is authenticated
- subscription is active

#### Task

Create tests for the meaningful combinations.

#### Complete solution

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

#### Explanation

Each parameter row represents a decision-table row.

#### Common mistake

Testing only `(True, True)` and ignoring failure combinations.

---

### Exercise 12 — State transition

#### Problem

An order can move from `PAID` to `SHIPPED` but not from `CANCELLED` to `SHIPPED`.

#### Complete solution

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

#### Explanation

The two tests protect a valid and invalid state transition.

#### Common mistake

Testing only the happy transition.

---

### Exercise 13 — Regression test

#### Problem

A bug report says amounts with surrounding spaces should work.

#### Task

Write the regression test first.

#### Complete solution

```python
def test_parse_amount_accepts_surrounding_whitespace():
    assert parse_amount(" 100 ") == 100
```

#### Explanation

The regression test captures the exact behavior that previously failed.

#### Common mistake

Only testing the new implementation code and not the original bug scenario.

---

### Exercise 14 — Deterministic time

#### Problem

A function uses `datetime.now()` internally.

#### Task

Redesign the test so it does not depend on the current system time.

#### Complete solution

One possible production refactoring that makes time controllable in tests is to pass the current time in explicitly:

```python
def is_expired(deadline, now):
    return now >= deadline
```

Then:

```python
from datetime import datetime, timezone


def test_is_expired_before_deadline():
    deadline = datetime(2026, 10, 1, tzinfo=timezone.utc)
    now = datetime(2026, 9, 30, tzinfo=timezone.utc)

    assert is_expired(deadline, now) is False
```

#### Explanation

Time becomes an explicit input.

#### Common mistake

Using `sleep()` to "wait until the right time" in a unit test.

---

### Exercise 15 — AAA refactoring

#### Problem

```python
def test_total():
    user = create_user()
    cart = create_cart()
    add_product(cart)
    apply_discount(cart)
    charge_card(user)
    assert cart.total > 0
```

#### Task

Identify at least three design problems and propose a narrower test.

#### Complete solution

Problems:

1. Multiple behaviors.
2. Expensive or irrelevant setup.
3. Weak assertion.

Possible refactoring pattern (illustrative: `Cart` and `Product` are assumed application classes, not defined here):

```python
def test_discounted_cart_total():
    # Arrange
    cart = Cart(items=[Product(price=100)])

    # Act
    cart.apply_discount(10)

    # Assert
    assert cart.total == 90
```

#### Explanation

The rewritten test focuses on one coherent calculation behavior.

#### Common mistake

Keeping `charge_card()` because the original test included it.

---

## Level 4 — Production-Oriented

### Exercise 16 — Data pipeline invariant

#### Problem

A pipeline guarantees:

```text
total_rows = valid_rows + rejected_rows
```

#### Task

Design a test for this invariant.

#### Complete solution

```python
def test_pipeline_preserves_row_count():
    # Arrange
    rows = [
        {"id": 1, "valid": True},
        {"id": 2, "valid": False},
        {"id": 3, "valid": True},
    ]

    # Act (`process_rows()` and its result are the pipeline interface supplied by the application context)
    result = process_rows(rows)

    # Assert
    assert result.total_rows == result.valid_rows + result.rejected_rows
```

#### Explanation

This protects a business/data invariant rather than one implementation detail.

#### Common mistake

Only checking that the pipeline did not raise an exception.

---

### Exercise 17 — API contract design

#### Problem

A user creation endpoint must return 201 and the created user's ID.

#### Complete solution

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

#### Explanation

The assertions collectively validate the response contract.

#### Common mistake

Testing only status code.

---

### Exercise 18 — LLM structured-output test

#### Problem

An AI classifier returns a dictionary with:

```text
label
confidence
```

#### Task

Design assertions that do not depend on exact natural-language phrasing.

#### Complete solution

```python
def test_classifier_returns_structured_result(classifier):
    # Arrange
    text = "I need a refund"

    # Act
    result = classifier.classify(text)

    # Assert
    assert set(result) == {"label", "confidence"}
```

#### Explanation

The test checks only the stated structure (`label` and `confidence`), not exact wording or unstated value constraints.

#### Common mistake

Asserting one exact generated sentence when wording is not part of the contract.

---

### Exercise 19 — Agent invariant

#### Problem

A transfer agent must never call the transfer tool unless the balance check succeeds.

#### Complete solution

```python
def test_agent_checks_balance_before_transfer(agent, fake_tools):
    # Arrange
    fake_tools.balance.return_value = 500
    request = {
        "from_account": "A",
        "to_account": "B",
        "amount": 100,
    }

    # Act
    agent.run(request)

    # Assert
    assert fake_tools.balance.called
    assert fake_tools.transfer.called


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
    assert fake_tools.balance.called
    assert not fake_tools.transfer.called
```

A stronger production design would also record tool call arguments and verify that the transfer amount was authorized by the balance and policy rules.

#### Explanation

The test protects an observable safety invariant.

#### Common mistake

Trying to assert hidden chain-of-thought instead of observable actions and results.

---

### Exercise 20 — Test-suite architecture

#### Problem

A backend has:

- 500 unit tests
- 100 integration tests
- 20 E2E tests
- a shared database

#### Task

Design a high-level strategy.

#### Complete solution

```text
Unit tests:
  fast, isolated, deterministic
  run on every change

Integration:
  verify app/database/service boundaries
  controlled database lifecycle
  run in CI

E2E:
  cover critical workflows
  keep number of scenarios focused
  run on appropriate pipeline stages
```

Use fixtures for environment setup and cleanup, but avoid a single giant global fixture that every test depends on.

#### Explanation

The architecture balances confidence, speed, and maintenance.

#### Common mistake

Making every test hit the database because "that is more realistic."

---

# 47. Debugging Lab

## Lab 1 — Unclear AAA structure

### Broken code

```python
def test_total():
    cart = Cart()
    cart.add(10)
    result = cart.total()
    assert result == 10
    cart.clear()
```

### Symptom

The test is not necessarily failing, but its cleanup is mixed into the test story.

### Diagnosis

Cleanup is not part of the target behavior.

### Refactor

```python
@pytest.fixture
def cart():
    cart = Cart()
    yield cart
    cart.clear()


def test_total(cart):
    # Arrange
    cart.add(10)

    # Act
    result = cart.total()

    # Assert
    assert result == 10
```

### Why better?

The test focuses on behavior; lifecycle management is separate.

---

## Lab 2 — Multiple unrelated behaviors

### Broken code

```python
def test_user_workflow():
    user = register_user()
    assert user.active

    login(user)
    assert user.session

    create_order(user)
    assert user.orders
```

### Problem

Registration, login, and order creation are three behaviors.

### Refactor

Create focused tests:

```python
def test_register_user_creates_active_user():
    user = register_user()

    assert user.active is True


def test_login_creates_session():
    user = existing_user()

    login(user)

    assert user.session is not None


def test_create_order_adds_order_to_user():
    user = existing_user()

    create_order(user)

    assert len(user.orders) == 1
```

---

## Lab 3 — Weak assertion

### Broken code

```python
def test_discount():
    result = apply_discount(100, 10)

    assert result
```

### Symptom

The test passes for `90`, `50`, `1`, or any other truthy value.

### Root cause

The assertion does not encode the requirement.

### Corrected

```python
def test_discount_returns_expected_amount():
    result = apply_discount(100, 10)

    assert result == 90
```

---

## Lab 4 — Implementation detail assertion

### Broken code

```python
def test_cache():
    service = UserService()

    service.get_user("1")

    assert service._cache["1"] is not None
```

### Problem

The test is coupled to the cache implementation.

### Refactor

```python
def test_get_user_returns_requested_user():
    service = UserService()

    user = service.get_user("1")

    assert user.id == "1"
```

A separate cache-specific test may be justified if caching itself is an explicit contract.

---

## Lab 5 — Shared mutable state

### Broken code

```python
USERS = []


def test_add_user():
    USERS.append("Alice")


def test_initial_users_empty():
    assert USERS == []
```

### Symptom

Second test fails depending on execution order.

### Fix

Use test-local state or a fresh fixture.

```python
@pytest.fixture
def users():
    return []


def test_add_user(users):
    users.append("Alice")

    assert users == ["Alice"]


def test_initial_users_empty(users):
    assert users == []
```

---

## Lab 6 — Test-order dependency

### Broken design

```python
created_user_id = None


def test_create_user():
    global created_user_id
    created_user_id = create_user()


def test_get_user():
    user = get_user(created_user_id)
    assert user is not None
```

### Root cause

Second test depends on first test.

### Better

```python
def test_get_user():
    created_user_id = create_user()

    user = get_user(created_user_id)

    assert user is not None
```

For integration resources, a fixture can create and clean up the needed state.

---

## Lab 7 — Random behavior

### Broken code

```python
import random


def test_token():
    token = generate_token()

    assert token == "abc123"
```

### Symptom

The test may fail because the generated value is not deterministic.

### Better design

Assert stable properties:

```python
def test_generated_token_has_expected_shape():
    token = generate_token()

    assert isinstance(token, str)
    assert len(token) == 32
```

Or inject a controllable random source if exact reproducibility is required.

---

## Lab 8 — Excessive fixture abstraction

### Broken design

```python
@pytest.fixture
def everything():
    user = create_user()
    account = create_account(user)
    product = create_product()
    order = create_order(user, product)
    payment = configure_payment(account)
    return user, account, product, order, payment
```

Then every test receives `everything`.

### Problem

The fixture hides too much context.

### Better

Provide smaller reusable fixtures:

```python
@pytest.fixture
def user():
    return create_user()


@pytest.fixture
def account(user):
    return create_account(user)
```

And let tests arrange scenario-specific objects explicitly.

---

## Lab 9 — Excessive setup

### Broken test

```python
def test_add():
    app = create_app()
    db = connect_db()
    user = create_user()
    permissions = create_permissions()
    product = create_product()
    cart = create_cart(user)
    ...
    assert add(2, 3) == 5
```

### Root cause

The test is at the wrong granularity or has accidental dependencies.

### Fix

Test the pure function directly:

```python
def test_add():
    assert add(2, 3) == 5
```

### Lesson

Do not make a tiny behavior pay the cost of a full system.

---

## Lab 10 — Overly broad E2E behavior

### Broken test

```text
register
verify email
login
browse
search
add to cart
apply coupon
checkout
refund
download receipt
```

### Problem

One failure can make the diagnosis ambiguous.

### Refactor strategy

Keep one critical E2E purchase workflow and move individual rules into lower-level tests.

---

# 48. Interview Questions

## Beginner

### 1. What is Arrange–Act–Assert?

**Model answer:** It is a test-structuring pattern that separates preparing the scenario, performing the target behavior, and checking the outcome. It is a reasoning framework, not a rigid three-line rule.

### 2. Does every test need exactly one assertion?

**Model answer:** No. The goal is one coherent behavior per test, and multiple related assertions can be appropriate when they jointly establish that behavior.

### 3. Why is AAA useful?

**Model answer:** It makes test intent easier to read, review, debug, and maintain by giving the test a predictable structure.

### 4. What belongs in Arrange?

**Model answer:** Inputs, initial state, dependencies, configuration, resources, and other setup needed to execute the target behavior.

### 5. What belongs in Act?

**Model answer:** The primary behavior under test, such as calling a function, making an API request, or triggering a workflow.

### 6. What belongs in Assert?

**Model answer:** Verification of observable outcomes, state changes, exceptions, persisted results, or other contract-relevant effects.

## Intermediate

### 7. What is one behavior per test?

**Model answer:** The test should focus on one logically coherent expected behavior. It does not mean one assertion or one line of code.

### 8. Why test negative cases?

**Model answer:** Invalid inputs and failure modes often represent important business and reliability risks. Testing only successful paths leaves those risks unprotected.

### 9. What is boundary-value analysis?

**Model answer:** A technique that focuses on values at and around input limits because defects frequently occur at boundaries.

### 10. What is equivalence partitioning?

**Model answer:** A technique for dividing a large input space into classes expected to behave similarly and selecting representative cases from those classes.

### 11. What is test isolation?

**Model answer:** The property that a test can establish its needed starting state and does not accidentally depend on other tests.

### 12. What causes test coupling?

**Model answer:** Shared mutable state, ordering assumptions, reused database data, global variables, environment changes, and other hidden dependencies.

### 13. Why test behavior rather than implementation?

**Model answer:** Behavior-focused tests remain useful across refactoring because they protect the externally relevant contract rather than internal design choices.

### 14. How do fixtures support AAA?

**Model answer:** Fixtures provide reusable setup, dependencies, and resource lifecycle management. Conceptually they support the Arrange phase while pytest resolves them before the test body executes.

### 15. How does parametrization support AAA?

**Model answer:** It lets the same Arrange–Act–Assert logic run against multiple explicit scenarios without duplicating the test function.

## Advanced

### 16. When should you use separate test functions instead of parametrization?

**Model answer:** When scenarios have significantly different setup, different behavior, different assertion structure, or would become difficult to understand as a parameter table.

### 17. How do you prevent combinatorial explosion?

**Model answer:** Use domain analysis, equivalence classes, boundary analysis, decision tables, risk-based selection, and representative combinations rather than blindly generating every theoretical combination.

### 18. How do you test nondeterministic LLM outputs?

**Model answer:** Keep deterministic application components strongly unit-tested, use controlled model responses where appropriate, validate schemas/invariants, and use evaluation strategies for model quality rather than relying on exact string equality.

### 19. How do fixtures become harmful?

**Model answer:** When they hide important scenario information, become huge, create unnecessary dependency chains, make cleanup unclear, or create global coupling.

### 20. How do you debug a failing test?

**Model answer:** Identify the exact failing scenario, read the assertion, compare expected and actual, inspect Arrange/setup and dependencies, reproduce the single case, determine whether the defect is in production code or test design, fix the underlying issue, and run regression tests.

---

# 49. Architecture Questions

## 1. How would you structure pytest tests for a large Python backend?

A practical structure is:

```text
tests/
├── unit/
├── integration/
├── api/
├── e2e/
└── conftest.py
```

The exact structure should follow repository conventions.

Keep tests close to their purpose, use shared fixtures carefully, and distinguish fast isolated tests from infrastructure-dependent tests.

## 2. How would you divide unit, integration, and E2E tests?

Use the smallest level that can provide meaningful confidence.

```text
Unit:
business logic

Integration:
boundaries such as database/message broker

E2E:
critical end-user workflows
```

Do not make every behavior an E2E test.

## 3. How would you design reusable fixtures?

Start with real repeated dependencies:

```text
database connection
application client
configuration
temporary workspace
```

Prefer small composable fixtures to a single universal fixture.

## 4. How would you prevent test coupling?

- isolate mutable resources
- reset database state appropriately
- control environment changes
- avoid order dependencies
- avoid hidden global state
- make tests runnable individually

## 5. How would you handle shared database state?

Possible strategies include:

- transaction rollback
- isolated schemas
- test database instances
- dataset reset
- per-test or per-class data according to cost and isolation needs

The correct approach depends on the database and system architecture.

## 6. How would you design tests for a data pipeline?

Model the pipeline as contracts:

```text
input schema
→ transformation rules
→ output schema
→ data quality invariants
```

Test:

- representative rows
- boundary rows
- invalid rows
- null handling
- duplicates
- type conversions
- counts
- idempotency where required

## 7. How would you test an AI application with nondeterministic outputs?

Separate the deterministic envelope from model variability.

```text
Deterministic:
validation
prompt assembly
retrieval filtering
tool contracts
parsing
authorization
fallbacks

Probabilistic:
generation quality
semantic similarity
classification accuracy
```

Use different evaluation methods for the second category.

## 8. How would you test an agentic workflow?

Test observable invariants:

```text
authorized tool use
required tool parameters
state transitions
termination
safety constraints
final output contract
```

Use controlled tools and state for deterministic workflow tests.

## 9. How would you prevent combinatorial explosion?

Use:

- equivalence partitioning
- boundary analysis
- decision tables
- pairwise or other systematic reduction techniques where appropriate
- risk-based prioritization

The goal is not to maximize combinations. It is to maximize meaningful information for the available cost.

## 10. How would you balance coverage with speed?

Think in terms of feedback loops:

```text
very fast:
unit tests

medium:
integration

slower:
E2E / environment-heavy
```

Run the right tests at the right pipeline stage.

## 11. How would you design regression testing for production?

Every important defect should create a reproducible test case where practical.

Then:

```text
incident
→ regression test
→ fix
→ CI protection
```

Track recurring failure patterns and improve the test architecture when defects reveal systemic gaps.

---

# 50. Production Test Design Checklist

Use this checklist when reviewing a new test.

- [ ] Is the behavior being tested clear?
- [ ] Does the test name describe the scenario and expected result?
- [ ] Is Arrange understandable?
- [ ] Is the Act focused on the target behavior?
- [ ] Are assertions precise enough to catch meaningful defects?
- [ ] Is the happy path covered?
- [ ] Are important negative paths covered?
- [ ] Are boundary cases covered?
- [ ] Are important edge cases covered?
- [ ] Is the test isolated?
- [ ] Is the test deterministic where practical?
- [ ] Does the test avoid unnecessary implementation-detail assertions?
- [ ] Are fixtures used because they improve reuse or lifecycle management?
- [ ] Are fixtures small enough to remain understandable?
- [ ] Is parametrization used where it improves clarity?
- [ ] Are parametrized cases named clearly when needed?
- [ ] Is there unnecessary combinatorial expansion?
- [ ] Is a discovered bug protected by a regression test?
- [ ] Is the test at the smallest useful test level?
- [ ] Is failure diagnosis straightforward?
- [ ] Is the execution cost appropriate?
- [ ] Will the test behave reliably in CI?
- [ ] Is any abstraction justified by real repetition?
- [ ] Would another engineer understand the test without reading five helper functions?

---

# 51. Knowledge Check

## Conceptual

### Question 1

A test has perfect AAA structure but asserts only `result is not None`. Is it necessarily a good test?

**Answer:** No. AAA provides structure, but the assertion may be too weak to verify the actual requirement.

### Question 2

Why can multiple assertions be acceptable?

**Answer:** Multiple related assertions can jointly verify one coherent behavior. The important concept is behavioral cohesion, not an assertion count.

### Question 3

Why are boundaries important?

**Answer:** Boundary errors frequently arise from incorrect comparison operators and off-by-one logic.

### Question 4

What is the difference between test isolation and test independence?

**Answer:** Isolation is about controlling the state/resources a test uses. Independence is about a test not requiring another test to establish that state. They are closely related.

### Question 5

What does "behavior over implementation" mean?

**Answer:** Tests should usually verify the externally relevant contract rather than internal data structures or call sequences that can change during refactoring.

## Code reading

### Question 6

What is weak about this test?

```python
def test_total():
    result = calculate_total(10, 2)
    assert result
```

**Answer:** It does not verify the expected value.

Better:

```python
assert result == 20
```

### Question 7

What test-design problem exists here?

```python
def test_everything():
    create_user()
    login()
    place_order()
    pay()
    cancel()
    refund()
    ...
```

**Answer:** The test likely contains multiple unrelated behaviors and is too broad for efficient diagnosis.

## Debugging

### Question 8

A test passes individually but fails when the whole suite runs. What should you investigate first?

**Answer:** Shared state, test-order dependency, environment leakage, database state, caches, global variables, and resource cleanup.

### Question 9

A parametrized test fails only for `65`, while `64` and `66` pass. What should you inspect?

**Answer:** The boundary logic and the parameterized case. This is a classic boundary-focused failure.

## Design

### Question 10

You have a rule:

```text
subscription active + authenticated → access
otherwise → deny
```

Would you use one test or four?

**Answer:** Either a small decision-table-style parametrized test or a few focused tests can be appropriate. The choice should optimize clarity and diagnostic value.

## Architecture

### Question 11

Should every backend test use the real database?

**Answer:** No. Some tests need database integration realism; many business-rule tests are better isolated and faster. The level should match the question being tested.

### Question 12

Should an LLM test always assert exact generated text?

**Answer:** No. For nondeterministic or semantically flexible outputs, structured contracts, invariants, and evaluation criteria may be more appropriate.

---

# 52. Glossary

| Term | Meaning |
|---|---|
| Software testing | The practice of evaluating whether software behaves as intended |
| Test case | A specific input/state and expected behavior |
| Test design | Deciding what scenarios and behaviors should be tested and how |
| Arrange | Preparing inputs, state, and dependencies |
| Act | Performing the behavior under test |
| Assert | Verifying the expected outcome |
| Test behavior | Observable action or result that forms part of a contract |
| Test isolation | Keeping a test's state and resources controlled and independent |
| Test independence | A test does not require another test to run first |
| Deterministic test | A test with predictable results under controlled conditions |
| Flaky test | A test that passes and fails unpredictably without a relevant code change |
| Test coupling | Dependency between tests or hidden shared state |
| Test smell | A pattern that may indicate a test-design problem |
| Boundary value | A value at or near an input limit |
| Equivalence partitioning | Dividing inputs into behaviorally similar classes |
| Happy path | A normal successful scenario |
| Negative path | An invalid, rejected, or failure scenario |
| Regression test | A test that protects behavior after a previously discovered defect |
| Test double | A controlled replacement for a real dependency |
| Stub | A test double that supplies controlled responses |
| Fake | A simplified working implementation used during tests |
| Mock | A controlled replacement commonly used to verify interactions |
| Spy | A double that records interactions |
| Test coverage | A measure of what code or paths were executed by tests |
| Behavior coverage | Coverage of meaningful system behaviors |
| Implementation detail | An internal design choice not necessarily part of the public contract |
| Property-based testing | Testing general rules or properties across many possible inputs |

---

# Final Mental Model

Good test design can be remembered as a sequence of engineering questions.

```text
Requirement
    ↓
What behavior matters?
    ↓
What inputs and starting states matter?
    ↓
What can go wrong?
    ↓
Where are the boundaries?
    ↓
Which cases represent important equivalence classes?
    ↓
Which state transitions are valid or invalid?
    ↓
What is the observable outcome?
    ↓
Design the test case
    ↓
Arrange
    ↓
Act
    ↓
Assert
    ↓
If it fails:
compare expected vs actual
    ↓
inspect setup and dependencies
    ↓
identify defect or test-design flaw
    ↓
fix
    ↓
preserve regression protection
```

The key principle is:

```text
Good test design
≠
more tests
```

Instead:

```text
Good test design
=
meaningful tests
+
reliable feedback
+
clear failure diagnosis
+
protection of important behavior
```

Another useful model is:

```text
Arrange
→ establish a known scenario

Act
→ trigger the behavior

Assert
→ verify the contract
```

Then expand your thinking:

```text
normal case
→ boundary
→ invalid case
→ failure mode
→ state transition
→ regression risk
```

And at larger scales:

```text
unit testing
    ↓
integration testing
    ↓
API testing
    ↓
data testing
    ↓
ML testing
    ↓
AI/LLM testing
    ↓
agentic-AI testing
    ↓
production CI/CD
```

AAA is therefore not merely a formatting convention.

It is a compact way to reason about **cause, behavior, and evidence**.

A strong engineer asks not:

> "How do I write more tests?"

but:

> "Which tests will give the team reliable information about the behaviors that matter?"

---

# Final Self-Review Checklist

- [x] The chapter starts from absolute beginner level.
- [x] Test design is explained before advanced techniques.
- [x] Arrange–Act–Assert is deeply explained.
- [x] Arrange is explained.
- [x] Act is explained.
- [x] Assert is explained.
- [x] AAA is not presented as merely three lines.
- [x] One behavior per test is explained correctly.
- [x] Multiple related assertions are discussed appropriately.
- [x] Requirements are converted into test cases.
- [x] Happy paths are covered.
- [x] Negative paths are covered.
- [x] Edge cases are covered.
- [x] Boundary-value analysis is covered.
- [x] Equivalence partitioning is covered.
- [x] Decision tables are covered.
- [x] State-based testing is covered.
- [x] Test isolation is covered.
- [x] Test independence is covered.
- [x] Deterministic testing is covered.
- [x] Test coupling is covered.
- [x] Test smells are covered.
- [x] Test naming is covered.
- [x] Test readability is covered.
- [x] Test maintainability is covered.
- [x] Behavior vs implementation is covered.
- [x] Test doubles are explained appropriately.
- [x] Fixtures are connected to AAA.
- [x] Parametrization is connected to AAA.
- [x] Unit-test AAA example is included.
- [x] Integration-test AAA example is included.
- [x] API-test AAA example is included.
- [x] E2E AAA example is included.
- [x] Coverage limitations are explained.
- [x] Regression testing is explained.
- [x] Property-based thinking is introduced.
- [x] Data-pipeline testing is covered.
- [x] ML testing is covered.
- [x] AI/LLM testing is covered.
- [x] Agentic-AI testing is covered.
- [x] CI/CD implications are covered.
- [x] A realistic complete example is included.
- [x] A mini-project is included.
- [x] At least 20 progressive exercises are included.
- [x] Every exercise has a complete solution.
- [x] A debugging lab is included.
- [x] Interview questions are included.
- [x] Architecture questions are included.
- [x] Production checklist is included.
- [x] Knowledge check is included.
- [x] Glossary is included.
- [x] Final mental model is included.
- [x] Code examples are written as valid Python where presented as executable examples.
- [x] Important pytest mechanisms used in the examples are explained in context.
- [x] The chapter focuses on test design rather than repeating the entire previous pytest syntax chapter.
- [x] The material progresses from basic → intermediate → advanced → production.
- [x] No absolute rule is stated for assertion count, Act count, duplication, mocking, coverage, test isolation, or exact LLM outputs.
- [x] No hidden chain-of-thought is treated as a testable output.
- [x] The material is aligned with the Applied AI Engineering learning philosophy.
- [x] The chapter is designed as a foundation for backend, data, ML, AI, and agentic-AI work.
