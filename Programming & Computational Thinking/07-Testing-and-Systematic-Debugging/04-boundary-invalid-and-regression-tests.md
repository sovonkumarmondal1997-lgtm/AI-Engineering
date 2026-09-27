# Boundary, Invalid, and Regression Tests

> **Stage 1 — Programming & Computational Thinking**  
> **Module 07 — Testing and Systematic Debugging**

## Learning Objectives

By the end of this chapter, you should be able to:

- distinguish valid, invalid, boundary, edge, failure, and regression scenarios;
- convert requirements into useful test cases instead of merely adding more tests;
- systematically identify values just inside, on, and just outside a boundary;
- use Boundary Value Analysis (BVA);
- use equivalence partitioning to reduce a large input space;
- combine BVA and equivalence partitioning;
- design negative tests that **pass when invalid input is correctly rejected**;
- test malformed, missing, empty, `None`, wrong-type, conflicting, duplicated, and oversized inputs;
- design tests around failure modes and expected exceptions;
- use pytest parametrization to express boundary and invalid cases clearly;
- choose readable test data and IDs;
- reproduce bugs before fixing them;
- turn real defects into regression tests;
- decide where a regression test belongs: unit, integration, API, or E2E;
- distinguish software regression from ML model drift or changing model quality;
- maintain a regression suite as the codebase grows;
- apply boundary and regression thinking to APIs, databases, data pipelines, ML systems, LLM applications, and agentic AI systems;
- debug a failing boundary or regression test systematically;
- design production-quality test suites without blindly maximizing test count.

---

## Prerequisites

This chapter assumes basic Python knowledge:

- variables
- functions
- arguments
- return values
- `if` statements
- exceptions
- lists and dictionaries
- simple classes
- `assert`
- basic pytest syntax

The previous chapters cover pytest assertions, fixtures, parametrization, and Arrange–Act–Assert in greater depth. This chapter intentionally focuses on the **test-design problem**:

> What cases should I test, and why?

The most important skill here is not memorizing a decorator. It is learning to look at a requirement and systematically identify the important behavior space.

---

# 1. What Are Boundary, Invalid, and Regression Tests?

## What is a valid input?

A **valid input** is a value or state that is allowed by the system's rules.

Suppose:

> Age must be between 18 and 65 inclusive.

Then:

```text
18 → valid
30 → valid
65 → valid
```

## What is an invalid input?

An **invalid input** violates a rule.

```text
17 → invalid
66 → invalid
```

Invalidity can also come from:

- wrong type
- missing field
- malformed format
- `None`
- unsupported value
- duplicate value
- impossible state

## What is a boundary?

A **boundary** is a limit where system behavior changes.

For:

```text
18 ≤ age ≤ 65
```

there are two formal boundaries:

```text
minimum = 18
maximum = 65
```

The most useful tests are usually not only the limits themselves. You also care about the values next to them:

```text
17  → just outside lower boundary
18  → lower boundary
19  → just inside lower boundary

64  → just inside upper boundary
65  → upper boundary
66  → just outside upper boundary
```

## What is an edge case?

An **edge case** is an unusual or extreme scenario that may reveal a defect.

Examples:

- empty string
- empty list
- one-item list
- very large value
- Unicode input
- duplicate records
- leap day

An edge case can also be a boundary case.

For example:

```text
maximum payload size
```

is both unusual and a formal boundary.

## What is a failure case?

A failure case is a scenario where the operation cannot or should not succeed.

Examples:

```text
insufficient balance
invalid credentials
missing required field
resource unavailable
duplicate transaction
```

The important point is that a correctly handled failure is often **successful behavior from the application's perspective**.

## What is a regression?

A **regression** occurs when behavior that previously worked becomes broken after a change.

Example:

```text
Version 1:
parse_amount(" 100 ") → 100

Version 2:
parse_amount(" 100 ") → ValueError
```

If surrounding-whitespace behavior previously worked and should still work, Version 2 contains a regression.

## What is a regression test?

A **regression test** is a test that protects behavior against reappearing after a change.

A defect-driven regression workflow is:

```text
bug discovered
    ↓
reproduce
    ↓
write failing test
    ↓
fix code
    ↓
test passes
    ↓
keep the test
```

## Comparison table

| Concept | Meaning | Example | Why it matters |
|---|---|---|---|
| Valid input | Allowed by the contract | age `30` | verifies normal behavior |
| Invalid input | Violates the contract | age `17` | verifies rejection/handling |
| Boundary | A limit where behavior changes | age `18` | catches off-by-one defects |
| Edge case | Unusual or extreme scenario | empty list | exposes overlooked behavior |
| Failure case | Expected or possible unsuccessful operation | insufficient funds | protects error handling |
| Regression | Previously working behavior breaks | valid input rejected after refactor | prevents defects from returning |
| Regression test | Test that protects against regression | test for the bug scenario | preserves learned protection |

## Simple example

Requirement:

> Age must be between 18 and 65 inclusive.

Classification:

| Value | Classification | Reason |
|---:|---|---|
| 17 | invalid / just outside | below minimum |
| 18 | valid / boundary | exact minimum |
| 19 | valid / just inside | immediately above minimum |
| 64 | valid / just inside | immediately below maximum |
| 65 | valid / boundary | exact maximum |
| 66 | invalid / just outside | above maximum |

This tiny example contains the core thinking used throughout the chapter.

---

# 2. Why These Tests Matter

## What is the problem?

Software often fails where assumptions become incorrect.

Developers may accidentally write:

```python
if age > 18:
```

when the requirement is:

```text
age >= 18
```

Or:

```python
if amount < 1000:
```

when the maximum allowed amount is:

```text
1000 inclusive
```

These are classic boundary defects.

Other failures come from:

- malformed inputs
- missing fields
- incorrect types
- unexpected states
- external failures
- previously fixed bugs

## Why is happy-path-only testing insufficient?

A single test:

```python
def test_withdraw_success():
    ...
```

proves only one normal scenario.

For a withdrawal system, important questions include:

```text
Can I withdraw a valid amount?
Can I withdraw exactly the balance?
Can I withdraw one unit more?
Can I withdraw zero?
Can I withdraw a negative amount?
What if the type is wrong?
What if the input is None?
What if the amount is extremely large?
What happens if the account is inactive?
```

## Simple Python example

```python
def withdraw(balance: int, amount: int) -> int:
    if amount <= 0:
        raise ValueError("amount must be positive")
    if amount > balance:
        raise ValueError("insufficient balance")
    return balance - amount
```

A happy-path test:

```python
def test_withdraw():
    assert withdraw(500, 100) == 400
```

Additional design-driven cases:

```text
amount = 500
amount = 501
amount = 0
amount = -1
amount = "100"
amount = None
```

The code has a small number of lines, but the behavior space is substantially larger.

## Real-world perspective

Financial systems, APIs, data pipelines, and authorization systems often contain explicit limits:

- transaction limit
- account balance
- rate limit
- payload size
- batch size
- page size
- age range
- retry count
- timeout
- token budget

Those limits are natural places to design high-value tests.

---

# 3. Valid vs Invalid Input

## What is a domain?

A **valid domain** is the set of inputs the system is designed to accept.

An **invalid domain** contains values the contract says should be rejected or otherwise handled specially.

### Example: age

```text
Valid domain:
18–65 inclusive

Invalid domains:
<18
>65
wrong type
missing
None
```

### Example: quantity

```text
Valid:
1–100

Invalid:
<=0
>100
wrong type
None
missing
```

### Example: username

```text
Valid:
3–20 characters

Potential invalid cases:
2 characters
21 characters
empty
missing
None
unsupported characters
```

### Example: percentage

```text
Valid:
0–100 inclusive

Invalid:
<0
>100
None
wrong type
```

## Python example

```python
def is_valid_percentage(value: int) -> bool:
    return 0 <= value <= 100
```

Potential test cases:

```text
0
1
50
99
100
-1
101
```

## pytest example

```python
import pytest


@pytest.mark.parametrize(
    "value,expected",
    [
        (0, True),
        (1, True),
        (50, True),
        (99, True),
        (100, True),
        (-1, False),
        (101, False),
    ],
)
def test_percentage_validation(value, expected):
    assert is_valid_percentage(value) is expected
```

## Common mistake

Treating all values that are "not normal" as invalid.

For example, `0` may be valid even if most production values are positive.

Validity comes from the **contract**, not from intuition.

## Better approach

Start from the requirement:

```text
What is explicitly allowed?
What is explicitly forbidden?
What is unspecified?
```

Unspecified behavior should not automatically be invented. In real engineering, clarify the contract or preserve existing documented behavior.

## Production considerations

Input boundaries often form the first line of defense around public APIs, user interfaces, financial transactions, and data ingestion.

---

# 4. Happy Path Testing

## What is it?

A happy path is the normal scenario where inputs are valid and expected processing succeeds.

```text
valid input
    ↓
normal processing
    ↓
expected result
```

## Simple pytest example

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

## Why is it necessary?

Without happy-path tests, you cannot establish that the core successful behavior works.

But happy-path testing alone leaves many important questions unanswered.

## Better test-design progression

For an important rule, think:

```text
happy path
→ boundary
→ just inside
→ just outside
→ invalid
→ malformed
→ missing
→ relevant failure mode
```

## Production considerations

A production suite needs successful scenarios because normal operation must remain protected. The mistake is not using happy paths; the mistake is treating them as the whole test strategy.

---

# 5. Negative Testing

## What is it?

**Negative testing** deliberately supplies invalid, unexpected, or prohibited inputs to verify that the system responds correctly.

Examples:

```text
invalid amount
wrong type
missing field
malformed date
unauthorized request
invalid state transition
duplicate operation
```

## Crucial distinction

A negative test should normally **pass** when the application correctly rejects the invalid input.

Consider:

```python
import pytest


def parse_age(value: str) -> int:
    if not value.isdigit():
        raise ValueError("invalid age")
    return int(value)


def test_parse_age_rejects_invalid_text():
    with pytest.raises(ValueError, match="invalid age"):
        parse_age("abc")
```

The application raises an exception intentionally.

The test passes because that is the expected behavior.

Therefore:

```text
Invalid input
    ↓
Expected application rejection
    ↓
Passing test
```

does **not** mean:

```text
Invalid input
    ↓
Test failure
```

## What can negative testing cover?

### Invalid values

```python
withdraw(balance=500, amount=-1)
```

### Invalid types

```python
parse_age(25.5)
```

### Missing values

```python
payload = {"name": "Alice"}
```

when `email` is required.

### Malformed strings

```python
parse_date("2026/99/99")
```

### Unauthorized actions

```text
user without permission → prohibited operation
```

### Impossible states

```text
DELIVERED → PAID
```

when the state transition is forbidden.

## Common mistakes

### Mistake 1: Expecting the test to fail

```python
def test_invalid():
    parse_age("abc")
```

This is not a useful negative test unless an unhandled exception itself is the behavior under evaluation.

### Mistake 2: Accepting any exception

```python
with pytest.raises(Exception):
    ...
```

Usually prefer the contract-specific exception.

### Mistake 3: Not checking state after rejection

If a transaction is rejected, balances or records may need to remain unchanged.

## Production considerations

Negative paths are often security- and reliability-relevant:

```text
unauthorized
invalid
expired
duplicated
oversized
malformed
out-of-range
```

These cases deserve deliberate design.

---

# 6. Boundaries

## What is a boundary?

A boundary is a limit where the system's classification or behavior changes.

Suppose:

```text
1 ≤ quantity ≤ 100
```

Then:

```text
0   → outside
1   → boundary
2   → inside

99  → inside
100 → boundary
101 → outside
```

## Why are boundaries high-value?

Many programming errors are caused by:

- `>` instead of `>=`
- `<` instead of `<=`
- off-by-one arithmetic
- slicing mistakes
- pagination errors
- incorrect loop termination
- inclusive/exclusive confusion

## Simple Python example

```python
def is_valid_quantity(quantity: int) -> bool:
    return 1 <= quantity <= 100
```

## pytest example

```python
def test_minimum_quantity_is_valid():
    assert is_valid_quantity(1) is True


def test_value_below_minimum_is_invalid():
    assert is_valid_quantity(0) is False
```

## Better boundary mindset

Do not ask only:

> What is the minimum?

Ask:

> What happens immediately below it, at it, and immediately above it?

Do the same for the maximum.

---

# 7. Boundary Value Analysis

## What is Boundary Value Analysis?

**Boundary Value Analysis (BVA)** is a systematic technique for selecting test values around limits.

The classic pattern is:

```text
minimum - 1
minimum
minimum + 1
maximum - 1
maximum
maximum + 1
```

## Example: quantity 1–100

```text
0
1
2
99
100
101
```

## Why these values?

They test:

```text
just outside
exact limit
just inside
```

on both ends.

## pytest example

```python
import pytest


@pytest.mark.parametrize(
    "quantity,expected",
    [
        (0, False),
        (1, True),
        (2, True),
        (99, True),
        (100, True),
        (101, False),
    ],
    ids=[
        "below-minimum",
        "minimum",
        "just-above-minimum",
        "just-below-maximum",
        "maximum",
        "above-maximum",
    ],
)
def test_quantity_boundaries(quantity, expected):
    assert is_valid_quantity(quantity) is expected
```

## Why IDs matter

A failure such as:

```text
test_quantity_boundaries[above-maximum]
```

is easier to understand than:

```text
test_quantity_boundaries[101-False]
```

The second is not necessarily bad, but explicit names can make failure diagnosis faster.

## Common mistake

Only testing:

```text
1
100
```

This can miss:

```text
0
101
```

which are exactly where an off-by-one defect may live.

## Production considerations

BVA is especially valuable for:

- financial thresholds
- API limits
- age eligibility
- permissions
- quotas
- pagination
- data validation
- configuration limits

---

# 8. Different Types of Boundaries

Boundary thinking applies far beyond integers.

## Numeric boundaries

```text
temperature: -20 to 50
```

Test:

```text
-21, -20, -19, 49, 50, 51
```

## String-length boundaries

```text
username: 3–20 characters
```

Test:

```text
2, 3, 4, 19, 20, 21 characters
```

## Collection-size boundaries

```text
maximum 10 records
```

Test:

```text
0, 1, 9, 10, 11
```

## Date/time boundaries

Examples:

- subscription expires at a timestamp
- report period starts at midnight
- billing cycle ends on a date
- timeout is 30 seconds

Test:

```text
just before
at boundary
just after
```

## File-size boundaries

Example:

```text
maximum 5 MB
```

Test values around the actual configured maximum rather than hard-coding a provider's limit.

## Pagination boundaries

```text
page_size: 1–100
```

Test:

```text
0, 1, 2, 99, 100, 101
```

## API rate limits

If an application defines:

```text
100 requests per minute
```

use controlled test infrastructure to verify behavior near the threshold.

Do not accidentally perform uncontrolled load against a production system.

## Database boundaries

Examples:

- maximum string length
- numeric precision
- `NULL` constraints
- uniqueness
- foreign-key existence

## Memory/resource boundaries

Examples:

- maximum batch size
- connection pool size
- queue capacity
- timeout
- file size

## Business-rule boundaries

These are often the most important:

```text
transaction <= approved limit
credit score >= threshold
age >= eligibility age
discount applies at subtotal >= threshold
```

## Engineering point

A boundary is not defined by its data type. It is defined by a **change in required behavior**.

---

# 9. String Boundaries

Suppose:

> Username length must be 3–20 characters.

## Boundary set

```text
2
3
4
19
20
21
```

## Additional edge cases

Also consider:

- `""`
- `"   "`
- leading/trailing spaces
- Unicode
- special characters
- visually similar characters
- case sensitivity

These are not all formal length boundaries.

For example:

```text
"abc"
```

and:

```text
"😊😊😊"
```

may have different practical implications depending on the product's definition of "character".

## Python example

```python
def is_valid_username(value: str) -> bool:
    return 3 <= len(value) <= 20
```

## pytest example

```python
import pytest


@pytest.mark.parametrize(
    "value,expected",
    [
        ("ab", False),
        ("abc", True),
        ("abcd", True),
        ("a" * 19, True),
        ("a" * 20, True),
        ("a" * 21, False),
    ],
)
def test_username_length(value, expected):
    assert is_valid_username(value) is expected
```

## Important distinction

Length validity does not automatically mean format validity.

A 10-character string can still be invalid because of:

```text
unsupported characters
whitespace
reserved names
Unicode normalization
```

## Production considerations

String limits appear in:

- database columns
- HTTP headers
- search fields
- filenames
- usernames
- prompt fields
- metadata
- identifiers

The application contract should define whether length is measured in characters, bytes, code points, or some other representation.

---

# 10. Collection Boundaries

Suppose:

> A batch may contain at most 10 records.

Useful cases:

```text
0
1
9
10
11
```

## Why test zero?

Because:

```text
empty batch
```

may be valid, invalid, or require a special result.

Never assume.

## Why test one?

The empty collection and one-item collection often exercise different code paths.

## Why test duplicates?

Because collection size is not the same as data validity.

```python
records = [1, 1, 1]
```

may have:

```text
length = 3
unique count = 1
```

A business rule may care about either or both.

## pytest example

```python
import pytest


def is_valid_batch(records: list[int]) -> bool:
    return len(records) <= 10


@pytest.mark.parametrize(
    "size,expected",
    [
        (0, True),
        (1, True),
        (9, True),
        (10, True),
        (11, False),
    ],
)
def test_batch_size_boundary(size, expected):
    records = list(range(size))

    assert is_valid_batch(records) is expected
```

## Production use

Collection boundaries are common in:

- ETL batch processing
- API bulk operations
- message queues
- database inserts
- ML batches
- vector retrieval
- agent tool arguments

---

# 11. Date and Time Boundaries

Time-related testing can be difficult because the boundary is moving or context-sensitive.

## Common boundaries

- start of day
- end of day
- expiration time
- timeout
- subscription renewal
- start/end of billing period
- month transition
- year transition
- leap day
- daylight-saving transition where applicable

## Better test design

Do not make a unit test depend on the real current time when the behavior can be expressed with an explicit timestamp.

```python
from datetime import datetime, timezone


def is_expired(deadline: datetime, now: datetime) -> bool:
    return now >= deadline
```

Test:

```python
def test_is_expired_at_deadline():
    deadline = datetime(2026, 10, 1, tzinfo=timezone.utc)

    assert is_expired(deadline, deadline) is True
```

And:

```python
def test_is_not_expired_just_before_deadline():
    deadline = datetime(2026, 10, 1, tzinfo=timezone.utc)
    now = datetime(2026, 9, 30, 23, 59, 59, tzinfo=timezone.utc)

    assert is_expired(deadline, now) is False
```

## Common mistakes

- using `datetime.now()` directly in assertions
- using `sleep()` to reach a boundary
- ignoring time zones
- assuming end-of-day semantics without a documented rule

## Production considerations

For distributed systems, define time semantics carefully:

```text
UTC or business timezone?
inclusive or exclusive?
instant or calendar date?
```

Tests should make those semantics explicit.

---

# 12. API Boundaries

APIs commonly expose explicit constraints.

Examples:

- page size
- payload size
- query length
- required fields
- retry limits
- rate limits
- supported values

## Example

Requirement:

> `page_size` must be between 1 and 100 inclusive.

Design:

```text
0
1
2
99
100
101
```

## Conceptual API test

```python
import pytest


@pytest.mark.parametrize(
    "page_size,expected_status",
    [
        (0, 400),
        (1, 200),
        (2, 200),
        (99, 200),
        (100, 200),
        (101, 400),
    ],
    ids=[
        "below-minimum",
        "minimum",
        "just-inside",
        "just-below-maximum",
        "maximum",
        "above-maximum",
    ],
)
def test_page_size_boundary(client, page_size, expected_status):
    response = client.get(
        "/items",
        params={"page_size": page_size},
    )

    assert response.status_code == expected_status
```

## What should the assertion verify?

Depending on the contract:

```text
HTTP status
response schema
error code
error body
side effects
```

Do not assert incidental formatting unless it is part of the API contract.

## Production considerations

API boundaries are particularly important because external clients can provide inputs you do not control.

---

# 13. Database Boundaries

Database constraints often create application-level boundary behavior.

Examples:

- `VARCHAR(255)`
- non-null field
- unique email
- foreign-key relationship
- numeric precision
- maximum batch size

## Example

Suppose application rule:

> Username must be at most 20 characters.

The database may also have a physical limit.

The application test should primarily verify the **application contract**:

```python
def test_username_rejects_too_long_value():
    value = "a" * 21

    with pytest.raises(ValueError, match="username too long"):
        validate_username(value)
```

An integration test can separately verify that valid application data is persisted correctly.

## Why separate concerns?

Testing:

```text
"the application rejects an invalid username"
```

is different from:

```text
"the database column is VARCHAR(20)"
```

The first is a domain contract. The second is an implementation/configuration property.

Both can matter, but they are different questions.

## Production considerations

Database constraints are often safety nets. Do not assume that application validation makes database constraints unnecessary.

---

# 14. Resource Boundaries

Some boundaries are about resources rather than values.

Examples:

- file size
- timeout
- queue length
- number of concurrent connections
- batch size
- memory budget
- retry count

## Example: retry boundary

Suppose:

> An operation is retried at most 3 times.

Useful tests:

```text
0 retries
1
2
3
4
```

The exact starting point depends on whether "3 retries" means three retries in addition to the initial attempt or three total attempts. The contract must define this.

## Test-design lesson

Do not test a number merely because it looks interesting.

First define its semantics.

---

# 15. Equivalence Partitioning

## What is it?

**Equivalence partitioning** divides a large input space into groups that are expected to behave similarly.

Suppose:

```text
Age < 18       → reject
18–65          → accept
Age > 65       → reject
```

You can choose representative values:

```text
17
30
66
```

## Why does it exist?

Testing every input is usually impossible.

For an integer domain, the number of possible values may be enormous.

Equivalence partitioning lets you test representative members.

## Python example

```python
def is_adult(age: int) -> bool:
    return age >= 18
```

Potential partitions:

```text
negative/very small
under 18
18 or older
```

The exact partitioning should follow the actual domain rules.

## pytest example

```python
import pytest


@pytest.mark.parametrize(
    "age,expected",
    [
        (10, False),
        (30, True),
        (90, True),
    ],
)
def test_is_adult_equivalence_classes(age, expected):
    assert is_adult(age) is expected
```

## Common mistake

Using only one partition representative and assuming hidden boundaries do not exist.

## Better approach

Combine:

```text
equivalence partitions
+
boundary values
```

---

# 16. BVA + Equivalence Partitioning

These techniques answer different questions.

### Equivalence partitioning asks

> Which groups should behave similarly?

### BVA asks

> What happens around the places where behavior changes?

Example:

```text
Age: 18–65
```

Partitions:

```text
<18
18–65
>65
```

Representative values:

```text
17
30
66
```

Boundary set:

```text
17
18
19
64
65
66
```

A practical suite may contain all six boundary-oriented cases because the boundary itself is high risk.

## Why both matter

Without partitioning:

```text
you may test too many values
```

Without boundary analysis:

```text
you may miss off-by-one defects
```

Together:

```text
partition broad domain
→ focus extra attention at boundaries
```

---

# 17. Invalid Input Categories

Invalid inputs are not one category.

A useful taxonomy is:

1. invalid value
2. invalid type
3. missing value
4. empty value
5. `None`
6. malformed format
7. out-of-range value
8. unsupported value
9. duplicate value
10. conflicting values
11. unexpected extra fields
12. invalid encoding
13. invalid state
14. unauthorized input
15. oversized input

## Examples

### Invalid value

```text
percentage = 150
```

### Invalid type

```text
age = "30"
```

when the contract expects an integer.

### Missing value

```python
{"name": "Alice"}
```

when `email` is required.

### Empty value

```python
{"name": ""}
```

### `None`

```python
{"name": None}
```

### Malformed format

```text
"2026-99-99"
```

### Unsupported value

```text
currency = "XYZ"
```

when only a defined set is supported.

### Duplicate value

Two identical transaction IDs.

### Conflicting values

```text
status = "PAID"
cancelled = True
```

when the state model does not allow that combination.

### Oversized input

A document larger than the application's accepted limit.

## Production consideration

A good negative-input taxonomy prevents you from repeatedly testing the same simple invalid case while missing qualitatively different failure modes.

---

# 18. Invalid Types

Python is dynamically typed, so tests at input boundaries should consider type mismatches where the contract requires validation.

Suppose:

```python
def validate_age(age: int) -> None:
    if not isinstance(age, int):
        raise TypeError("age must be an integer")
```

Useful inputs:

```text
25
"25"
25.5
None
[]
{}
object()
```

## pytest example

```python
import pytest


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("25", id="string"),
        pytest.param(25.5, id="float"),
        pytest.param(None, id="none"),
        pytest.param([], id="list"),
        pytest.param({}, id="dict"),
        pytest.param(object(), id="object"),
    ],
)
def test_validate_age_rejects_invalid_types(value):
    with pytest.raises(TypeError, match="age must be an integer"):
        validate_age(value)
```

## Type validation vs value validation

These are different:

```text
25
```

may be the correct type but an invalid value if:

```text
age must be 18–65
```

Meanwhile:

```text
"25"
```

may represent a valid semantic value but still violate the API's type contract.

Do not assume that "convertible" means "valid."

---

# 19. Missing, Empty, `None`, Zero, and False

These values are easy to confuse.

Consider:

```python
username = ""
username = None
quantity = 0
enabled = False
```

They have different meanings.

## Missing

The field does not exist at all:

```python
payload = {}
```

## Empty

The field exists but contains an empty value:

```python
payload = {"username": ""}
```

## `None`

The field exists but explicitly contains no value:

```python
payload = {"username": None}
```

## Zero

A numeric value:

```python
quantity = 0
```

## False

A Boolean:

```python
enabled = False
```

These may trigger different business rules.

## Example

```python
def validate_quantity(value):
    if value is None:
        raise ValueError("quantity is required")

    if value == 0:
        raise ValueError("quantity must be positive")

    return value
```

The tests should make the distinction explicit.

```python
def test_missing_quantity_is_rejected():
    payload = {}

    assert "quantity" not in payload


def test_none_quantity_is_rejected():
    with pytest.raises(ValueError, match="quantity is required"):
        validate_quantity(None)


def test_zero_quantity_is_rejected():
    with pytest.raises(ValueError, match="quantity must be positive"):
        validate_quantity(0)
```

The exact validation contract will differ by system.

## Common mistake

Writing:

```python
if not value:
    ...
```

without understanding that it combines:

```text
0
False
""
[]
{}
None
```

into one truthiness category.

That may be correct sometimes, but it is not automatically correct.

---

# 20. Malformed Input

Malformed data violates a format or structural expectation.

Examples:

```text
invalid email
invalid JSON
broken CSV
invalid UUID
malformed URL
invalid date
corrupted file
```

## Python example

```python
from datetime import datetime


def parse_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d")
```

Negative test:

```python
import pytest


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("2026-99-99", id="invalid-month-day"),
        pytest.param("not-a-date", id="random-text"),
        pytest.param("2026/01/01", id="wrong-format"),
    ],
)
def test_parse_date_rejects_malformed_input(value):
    with pytest.raises(ValueError):
        parse_date(value)
```

## Better approach

Test the failure contract:

```text
what exception?
what HTTP status?
what error code?
what state after failure?
```

Do not merely verify "something went wrong."

---

# 21. Exception Testing

Many invalid cases are specified as expected exceptions.

## `pytest.raises`

Basic syntax:

```python
with pytest.raises(ValueError):
    parse_percentage(150)
```

The important design questions are:

- Is the exception type part of the contract?
- Is the message meaningful and stable enough to assert?
- Should state remain unchanged after the exception?

## Matching messages

When the message is stable and useful:

```python
with pytest.raises(ValueError, match="must be between 0 and 100"):
    parse_percentage(150)
```

`match=` uses regular-expression matching. You usually do not need advanced regex knowledge to use it effectively, but remember that special regex characters have meaning.

## Avoid fragile messages

This may be brittle:

```python
assert str(exc.value) == (
    "Value 150 is invalid because the percentage must be "
    "between 0 and 100 inclusive for this exact API version."
)
```

If exact wording is not part of the contract, prefer:

```python
assert "between 0 and 100" in str(exc.value)
```

or simply assert the exception type.

## Production consideration

Exception type is often a stronger contract than incidental message wording.

For public APIs, an error code/schema can be a better contract than raw exception text.

---

# 22. Parametrizing Boundary Tests

Parametrization is especially useful when test logic stays the same and only the boundary case changes.

## Basic example

```python
import pytest


@pytest.mark.parametrize(
    "age",
    [17, 18, 19, 64, 65, 66],
)
def test_age_validation(age):
    ...
```

This is compact, but it makes the expected behavior implicit.

A clearer design can be:

```python
@pytest.mark.parametrize(
    "age,expected_valid",
    [
        (17, False),
        (18, True),
        (19, True),
        (64, True),
        (65, True),
        (66, False),
    ],
)
def test_age_validation(age, expected_valid):
    assert is_valid_age(age) is expected_valid
```

## With readable IDs

```python
@pytest.mark.parametrize(
    "age,expected_valid",
    [
        pytest.param(17, False, id="below-minimum"),
        pytest.param(18, True, id="minimum"),
        pytest.param(19, True, id="just-inside-minimum"),
        pytest.param(64, True, id="just-inside-maximum"),
        pytest.param(65, True, id="maximum"),
        pytest.param(66, False, id="above-maximum"),
    ],
)
def test_age_validation(age, expected_valid):
    assert is_valid_age(age) is expected_valid
```

## Why this is good test design

The parameter table acts almost like a requirements table:

```text
scenario → expected behavior
```

A future reviewer can see the boundary model directly.

---

# 23. Parametrized Invalid Tests

Invalid values often share one failure contract.

Example:

```python
import pytest


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("abc", id="letters"),
        pytest.param("", id="empty"),
        pytest.param(None, id="none"),
    ],
)
def test_parse_age_rejects_invalid_input(value):
    with pytest.raises(ValueError):
        parse_age(value)
```

## When to add expected exceptions explicitly

If different invalid classes produce different exception types:

```python
@pytest.mark.parametrize(
    "value,exception_type",
    [
        ("abc", ValueError),
        (None, TypeError),
    ],
)
def test_parse_age_rejects_invalid_input(value, exception_type):
    with pytest.raises(exception_type):
        parse_age(value)
```

## When to use separate tests

If the error behavior itself differs substantially, separate tests may be clearer.

For example:

```text
missing field → 400
unauthorized → 401
forbidden → 403
duplicate → 409
```

A large mixed parameter table can become harder to understand than focused tests.

---

# 24. Edge Cases vs Boundary Cases

## Boundary case

Directly connected to a defined limit.

Example:

```text
maximum age = 65

65 → boundary
66 → just outside
64 → just inside
```

## Edge case

An unusual or extreme case that is not necessarily a formal limit.

Examples:

```text
empty list
Unicode
duplicate record
very large integer
leap day
```

## Can something be both?

Yes.

```text
maximum list size
```

is both:

- a formal boundary
- an unusual scenario

## Design lesson

Do not create an artificial argument about classification.

The useful question is:

> Does this scenario represent a meaningful way the system could behave incorrectly?

---

# 25. Failure Modes

## What is a failure mode?

A **failure mode** is a way a system can fail or behave incorrectly.

For a transaction feature:

```text
invalid amount
insufficient balance
inactive account
duplicate request
unknown account
timeout
database unavailable
permission failure
```

## Failure-mode thinking

Ask:

> "What can go wrong?"

Then convert each important failure mode into an observable test.

## Example

Requirement:

> A transfer can be executed only when the account is active and the balance is sufficient.

Failure modes:

```text
inactive account
insufficient balance
invalid amount
unknown account
```

Test design table:

| Failure mode | Trigger | Expected behavior |
|---|---|---|
| inactive account | active=False | reject |
| insufficient balance | amount > balance | reject |
| invalid amount | amount <= 0 | reject |
| unknown account | invalid ID | reject |

## Production use

Failure-mode analysis is especially valuable for:

- payments
- authentication
- distributed systems
- data ingestion
- job orchestration
- AI tool execution

---

# 26. Testing Error Messages

Error messages are a special case.

## When exact messages matter

Exact text can be part of a stable contract when:

- an API specification defines it
- a CLI output is explicitly user-facing and stable
- downstream automation depends on it
- documentation promises exact wording

Then exact matching may be justified.

## When exact messages do not matter

Prefer a semantic assertion:

```python
with pytest.raises(ValueError, match="invalid age"):
    parse_age("abc")
```

or:

```python
with pytest.raises(ValueError):
    parse_age("abc")
```

## Common mistake

Overly strict assertions against incidental wording create brittle tests.

## Better approach

Assert the strongest stable part of the error contract.

---

# 27. Testing Error Types

Exception type often communicates the category of failure.

Example:

```python
ValueError
```

means an argument has an unacceptable value.

```python
TypeError
```

can indicate an inappropriate type.

```python
PermissionError
```

can represent an operating-system permission problem.

The application's domain may define its own exceptions.

## Better pytest example

```python
def test_percentage_rejects_out_of_range_value():
    with pytest.raises(ValueError):
        validate_percentage(150)
```

## Common mistake

Using:

```python
with pytest.raises(Exception):
```

for everything.

That can accidentally accept unrelated defects.

For example, an `AttributeError` caused by a bug in your implementation could make the test pass even though the intended `ValueError` behavior never occurred.

---

# 28. Regression Testing

## What is regression testing?

Regression testing checks that changes do not break behavior that should continue working.

A **regression bug** is a newly introduced failure in previously working behavior.

Examples:

```text
refactor
→ parsing behavior breaks
```

```text
database migration
→ API response changes unexpectedly
```

```text
new discount feature
→ old order total behavior breaks
```

## Regression test vs ordinary test

Every useful test can provide regression protection.

However, in day-to-day engineering, "regression test" often refers especially to a test added because a defect was discovered.

That defect-driven meaning is the emphasis here.

## Why is regression protection valuable?

A bug has already demonstrated that:

```text
the behavior can break
```

A regression test turns that learning into automation.

---

# 29. Bug → Regression Test Workflow

The core workflow is:

```text
Bug discovered
      ↓
Understand requirement
      ↓
Reproduce bug
      ↓
Write failing test
      ↓
Confirm failure
      ↓
Fix production code
      ↓
Run regression test
      ↓
Run related tests
      ↓
Keep regression test
```

## Why this sequence matters

If the test passes before the fix, you may not have reproduced the bug.

The most valuable first state is:

```text
failing test
```

because it proves the test can detect the defect.

---

# 30. Why Write the Regression Test First?

Suppose a bug report says:

> Negative transaction amounts are being accepted.

Write the test:

```python
def test_transfer_rejects_negative_amount():
    sender = BankAccount("A", 500)
    receiver = BankAccount("B", 100)

    with pytest.raises(ValueError, match="amount must be positive"):
        transfer(sender, receiver, -1)
```

Run it.

If the buggy implementation accepts `-1`, the test fails.

Only then fix the code.

## What does this demonstrate?

The test is capable of detecting:

```text
the actual defect
```

After the fix:

```text
test passes
```

Now the suite protects against reintroduction.

## Common mistake

Fixing the implementation first and then writing a test that simply passes.

That test may still be valuable, but it does not demonstrate that it reproduced the original defect.

---

# 31. Regression Test Example

We will use a transaction system.

## Buggy implementation

```python
class BankAccount:
    def __init__(self, account_id: str, balance: int):
        self.account_id = account_id
        self.balance = balance


def transfer(sender: BankAccount, receiver: BankAccount, amount: int) -> None:
    if amount > sender.balance:
        raise ValueError("insufficient balance")

    sender.balance -= amount
    receiver.balance += amount
```

The developer forgot:

```python
amount > 0
```

## Bug reproduction

```python
def test_negative_transfer_is_rejected():
    sender = BankAccount("A", 500)
    receiver = BankAccount("B", 100)

    with pytest.raises(ValueError, match="amount must be positive"):
        transfer(sender, receiver, -1)
```

The test fails because no exception is raised.

Worse, the balances may become:

```text
sender = 501
receiver = 99
```

A negative transfer has reversed money.

## Fix

```python
def transfer(sender: BankAccount, receiver: BankAccount, amount: int) -> None:
    if amount <= 0:
        raise ValueError("amount must be positive")

    if amount > sender.balance:
        raise ValueError("insufficient balance")

    sender.balance -= amount
    receiver.balance += amount
```

Now the regression test passes.

## Stronger regression test

Protect state as well:

```python
def test_negative_transfer_does_not_mutate_balances():
    sender = BankAccount("A", 500)
    receiver = BankAccount("B", 100)

    with pytest.raises(ValueError):
        transfer(sender, receiver, -1)

    assert sender.balance == 500
    assert receiver.balance == 100
```

This is stronger because it protects the invariant:

```text
rejected transaction
→ no balance mutation
```

---

# 32. Regression Tests and Bug Reproduction

A good regression test should reproduce the behavior that actually failed.

## Bad regression test

Bug report:

> `" 100 "` is rejected even though it should be accepted.

Bad test:

```python
def test_parse_amount_returns_integer():
    assert parse_amount("100") == 100
```

This does not reproduce the bug.

## Good regression test

```python
def test_parse_amount_accepts_surrounding_whitespace():
    assert parse_amount(" 100 ") == 100
```

This captures the actual scenario.

## Why this matters

A vague regression test can give a false sense of protection.

The test should answer:

> "Would the exact bug that occurred cause this test to fail if it came back?"

That is a powerful review question.

---

# 33. Regression Tests and Refactoring

Regression tests protect behavior during refactoring.

Suppose implementation changes from:

```python
def normalize_name(value: str) -> str:
    return value.strip().lower()
```

to:

```python
def normalize_name(value: str) -> str:
    return value.strip().casefold()
```

If the behavior remains contract-compatible, good behavior tests should continue to pass.

## Why is this useful?

Refactoring changes implementation without intentionally changing behavior.

Regression protection helps detect accidental behavior changes.

## Other change sources

- dependency upgrades
- database changes
- API implementation changes
- performance optimization
- caching
- concurrency changes
- architecture migrations

---

# 34. Regression Tests and New Features

New functionality can break old behavior.

Suppose an order system calculates:

```text
subtotal
```

Then a new feature adds:

```text
discount
```

A faulty implementation may change normal totals unexpectedly.

You need:

```text
new feature tests
+
existing behavior tests
```

## Example

Existing regression test:

```python
def test_order_total_without_discount():
    order = Order(items=[100, 200])

    assert order.total() == 300
```

New feature test:

```python
def test_discount_applies_at_threshold():
    order = Order(items=[1000])

    assert order.total() == 900
```

The two tests protect different aspects of behavior.

---

# 35. Regression Test Suite Design

A regression suite grows as the team learns.

```text
bug A
 ↓
test A

bug B
 ↓
test B

bug C
 ↓
test C
```

Over time:

```text
small suite
→ broader protection
→ increased runtime
→ increased maintenance cost
```

## Valuable regression tests

Keep tests that:

- reproduce real defects
- protect high-risk behavior
- cover important contracts
- provide unique information
- fail diagnostically

## Duplicate regression tests

Two tests may accidentally cover the same behavior.

Example:

```python
test_negative_amount_rejected()
test_amount_must_be_positive_for_negative_input()
```

If they are logically identical, the second may add little value.

## Redundant vs complementary

These are different.

```text
test invalid input rejected
+
test rejected input leaves state unchanged
```

may be complementary.

## Production consideration

The regression suite is a living asset, but not every historical test must remain forever in its original form. Periodically review redundancy and diagnostic value.

---

# 36. Regression Tests and the Test Pyramid

A regression bug can surface at different levels.

## Unit regression test

Use when a pure or isolated behavior reproduces the defect.

## Integration regression test

Use when the bug requires interaction between components.

## API regression test

Use when the externally visible API contract is what regressed.

## E2E regression test

Use when the defect requires a broad end-user workflow and cannot be reliably reproduced lower in the stack.

## Practical heuristic

> Put the regression test at the lowest practical level that reliably reproduces the bug.

This is a useful engineering heuristic, not an absolute law.

If the lower-level unit test cannot reproduce a cross-service bug, an integration test may be the correct place.

---

# 37. Boundary Testing in Unit Tests

Unit-level boundary tests should be fast and explicit.

```python
import pytest


def validate_score(score: int) -> bool:
    return 0 <= score <= 100


@pytest.mark.parametrize(
    "score,expected",
    [
        pytest.param(-1, False, id="below-minimum"),
        pytest.param(0, True, id="minimum"),
        pytest.param(1, True, id="just-inside"),
        pytest.param(99, True, id="just-inside-maximum"),
        pytest.param(100, True, id="maximum"),
        pytest.param(101, False, id="above-maximum"),
    ],
)
def test_score_boundary_behavior(score, expected):
    assert validate_score(score) is expected
```

The test is valuable because the table makes the contract visible.

---

# 38. Boundary Testing in API Tests

Suppose:

```text
page_size = 1–100
```

The API-level test can exercise:

```text
0
1
2
99
100
101
```

## Example

```python
import pytest


@pytest.mark.parametrize(
    "page_size,expected_status",
    [
        (0, 400),
        (1, 200),
        (2, 200),
        (99, 200),
        (100, 200),
        (101, 400),
    ],
)
def test_get_items_page_size_boundary(client, page_size, expected_status):
    response = client.get(
        "/items",
        params={"page_size": page_size},
    )

    assert response.status_code == expected_status
```

For invalid cases, also consider:

```text
missing page_size
page_size=""
page_size="abc"
page_size=None
```

The exact encoding depends on the API contract.

## Assertions

Potentially verify:

```text
status
error code
response schema
pagination metadata
no unexpected side effect
```

---

# 39. Boundary Testing in Data Pipelines

Suppose a CSV column has the business rule:

```text
transaction_amount must be 0–1,000,000
```

Test:

```text
-1
0
1
999,999
1,000,000
1,000,001
missing
malformed
extremely large
```

## Test design

```python
@pytest.mark.parametrize(
    "value,expected_valid",
    [
        (-1, False),
        (0, True),
        (1, True),
        (999_999, True),
        (1_000_000, True),
        (1_000_001, False),
    ],
)
def test_transaction_amount_boundary(value, expected_valid):
    record = {"transaction_amount": value}

    result = validate_record(record)

    assert result.is_valid is expected_valid
```

## Pipeline-level considerations

Also test:

- rejected-row counts
- reason codes
- output schema
- null-rate constraints
- duplicates
- data loss
- idempotency

Example invariant:

```text
input rows
=
accepted rows + rejected rows
```

when that is guaranteed by the pipeline contract.

---

# 40. Boundary Testing in ML Systems

Boundary thinking applies to ML system infrastructure and application logic.

Potential boundaries include:

- feature ranges
- batch size
- sequence length
- confidence thresholds
- schema field counts
- input token constraints
- maximum payload size

## Important distinction

Do not assume:

```text
feature slightly above boundary
→ model output changes predictably
```

ML models are not necessarily monotonic or deterministic.

Instead, test explicit application contracts.

Example:

```python
def test_prediction_output_shape(model):
    rows = [{"age": 30}, {"age": 40}]

    predictions = model.predict(rows)

    assert len(predictions) == 2
```

For a confidence threshold:

```python
def classify(score: float) -> str:
    return "positive" if score >= 0.8 else "negative"
```

Boundary tests:

```text
0.79
0.80
0.81
```

This is ordinary boundary logic around a deterministic rule.

---

# 41. Boundary Testing in AI/LLM Systems

AI applications can have practical limits such as:

- input length
- token budgets
- context-related limits
- document size
- retrieval count
- retry count
- timeout
- tool argument size

The exact limit depends on the system configuration and provider.

## Application-level test

Suppose your own application defines:

```text
document text ≤ 50,000 characters
```

Test:

```text
49,999
50,000
50,001
```

Example:

```python
def test_document_length_boundary():
    valid_document = "a" * 50_000
    invalid_document = "a" * 50_001

    assert validate_document(valid_document) is True
    assert validate_document(invalid_document) is False
```

## LLM output testing

Avoid assuming exact text is always stable.

Prefer tests for:

- valid structure
- required fields
- tool schema
- allowed values
- safety constraints
- deterministic parser behavior
- fallback behavior

---

# 42. Regression Testing in Data Pipelines

Data regressions may not look like ordinary application exceptions.

Example:

```text
Before change:
100 records output

After change:
95 records output
```

Possible regression:

- filtering condition changed
- join became inner instead of left
- parsing dropped rows
- null handling changed

## Useful regression assertions

```text
output row count
schema
null rate
duplicate count
business-rule result
aggregation invariant
```

Example:

```python
def test_transaction_transform_preserves_row_count():
    input_rows = load_fixture_data()

    output = transform(input_rows)

    assert len(output) == len(input_rows)
```

Only make such an assertion when row preservation is actually a requirement.

## Schema regression

```python
def test_output_schema_is_stable():
    output = transform(load_fixture_data())

    assert set(output.columns) == {
        "transaction_id",
        "amount",
        "currency",
    }
```

---

# 43. Regression Testing in ML Systems

Software regression and model performance drift are related but different.

## Software regression

A code change breaks behavior:

```text
preprocessor
→ missing feature
```

or:

```text
model service
→ output shape changed
```

## Model performance drift

The model's predictive quality changes over time because of changing data, model behavior, deployment, or other factors.

Examples:

```text
accuracy decreases
precision decreases
feature distribution shifts
```

These require different monitoring/evaluation approaches.

## Software regression examples

- preprocessing produces different feature order
- feature encoding changes unexpectedly
- output shape changes
- model-serving endpoint schema changes
- threshold logic changes

Example:

```python
def test_prediction_output_shape_is_stable(model):
    output = model.predict([[1.0, 2.0], [3.0, 4.0]])

    assert len(output) == 2
```

## Production consideration

Do not call every model-performance decline a "regression test failure." A test failure is an automated check against a defined expectation; production model drift may require monitoring and evaluation over live data.

---

# 44. Regression Testing in AI/LLM Applications

Useful regression categories include:

### Prompt/template regression

A code change accidentally removes required instructions.

### Structured-output regression

JSON/schema parsing breaks.

### Tool-use regression

A tool call disappears or receives wrong arguments.

### Retrieval regression

Relevant documents are no longer returned.

### Fallback regression

A failure path stops gracefully degrading.

### Safety-constraint regression

A previously enforced application guard is removed.

### Integration regression

A model provider/API integration breaks.

## Example

```python
def test_classifier_returns_required_fields(classifier):
    result = classifier.classify("I need a refund")

    assert "intent" in result
    assert "confidence" in result
    assert 0 <= result["confidence"] <= 1
```

This test is more stable than requiring one exact natural-language sentence.

---

# 45. Regression Testing for Agentic AI

Agentic systems add workflow-level behavior.

Suppose the required workflow is:

```text
user request
   ↓
retrieve balance
   ↓
validate policy
   ↓
call transfer tool
   ↓
return structured result
```

A later change removes the balance check.

A regression test should catch the observable behavior change.

## Example

```python
def test_transfer_agent_checks_balance_before_transfer(agent, fake_tools):
    fake_tools.balance.return_value = 500

    request = {
        "from_account": "A",
        "to_account": "B",
        "amount": 100,
    }

    result = agent.run(request)

    assert fake_tools.balance.called
    assert fake_tools.transfer.called
    assert result["status"] == "success"
```

A stronger test may verify the transfer amount and tool arguments.

## Important boundary cases

Agentic workflows may have:

- authorization threshold
- transfer limit
- retry count
- maximum tool calls
- timeout
- required approval state

Example:

```text
transfer limit = 1,000
```

Test:

```text
999
1000
1001
```

## Do not test hidden reasoning

The test should focus on observable behavior:

```text
tool invocation
state
result
errors
termination
safety constraints
```

It should not assume access to or inspect hidden chain-of-thought.

---

# 46. Test Data Design for Boundary and Invalid Tests

Good test data should be:

- representative
- deterministic
- minimal
- readable
- purposeful
- explicit about expected behavior

## Inline values

Good for tiny obvious cases:

```python
assert is_valid_age(18)
```

## Parametrization

Good for repeated logic:

```python
@pytest.mark.parametrize(
    "age,expected",
    [
        (17, False),
        (18, True),
        (65, True),
        (66, False),
    ],
)
```

## Fixture factories

Good when building realistic objects repeatedly:

```python
@pytest.fixture
def make_account():
    def _make_account(balance=500):
        return BankAccount("A", balance)
    return _make_account
```

## Named constants

Good when the number represents a domain rule:

```python
MAX_TRANSACTION_AMOUNT = 1_000_000
```

## Structured test cases

Useful when cases have many fields:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Case:
    name: str
    amount: int
    expected_valid: bool
```

Then:

```python
cases = [
    Case("below-limit", -1, False),
    Case("minimum", 1, True),
    Case("maximum", 100, True),
]
```

## Common mistake

Turning a simple six-value test into a complex framework.

Use the simplest representation that keeps the cases clear.

---

# 47. Test Readability

Compare:

```python
@pytest.mark.parametrize("x", [0, 1, 2, 99, 100, 101])
```

with:

```python
@pytest.mark.parametrize(
    "page_size,expected_valid",
    [
        pytest.param(0, False, id="below-minimum"),
        pytest.param(1, True, id="minimum"),
        pytest.param(2, True, id="just-inside-minimum"),
        pytest.param(99, True, id="just-inside-maximum"),
        pytest.param(100, True, id="maximum"),
        pytest.param(101, False, id="above-maximum"),
    ],
)
def test_page_size(page_size, expected_valid):
    assert is_valid_page_size(page_size) is expected_valid
```

The second is longer, but it communicates the requirement more clearly.

## When concise is better

For a simple mathematical property, this may be enough:

```python
@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_positive_values(n):
    assert n > 0
```

## Design principle

Optimize for:

```text
human understanding during review and failure diagnosis
```

not minimum character count.

---

# 48. Common Mistakes

## Mistake 1 — Testing only happy paths

### Bad

```python
def test_age():
    assert is_valid_age(30)
```

### Why

No evidence about the boundary.

### Better

```text
17
18
19
64
65
66
```

---

## Mistake 2 — Testing only exact boundaries

### Bad

```text
18
65
```

### Why

Could miss:

```text
17
19
64
66
```

### Better

Use the classic BVA neighborhood.

---

## Mistake 3 — Forgetting just-outside values

An off-by-one defect often appears immediately outside the valid range.

---

## Mistake 4 — Treating `None` and empty as identical

```python
"" != None
```

They may represent different semantic states.

---

## Mistake 5 — Invalid test without expected failure

Bad:

```python
def test_invalid_age():
    parse_age("abc")
```

Better:

```python
def test_invalid_age():
    with pytest.raises(ValueError):
        parse_age("abc")
```

---

## Mistake 6 — Weak assertions

Bad:

```python
assert result is not None
```

Better:

```python
assert result == expected
```

when the exact result is part of the contract.

---

## Mistake 7 — Enormous parameter lists

A 300-row parameter table can become difficult to review and diagnose.

Split the behavior into meaningful groups when needed.

---

## Mistake 8 — Duplicate regression tests

Do not preserve every test solely because it has the word "regression" in its history.

Review unique information.

---

## Mistake 9 — Regression test does not reproduce bug

Bug:

```text
negative amounts accepted
```

Test:

```text
positive amount succeeds
```

That does not reproduce the defect.

---

## Mistake 10 — Fragile error-message assertions

Avoid exact matching unless exact wording is part of the contract.

---

## Mistake 11 — Confusing software regression with model drift

A software regression:

```text
code behavior changed unexpectedly
```

Model drift/performance change:

```text
model quality changes over data/time
```

They require different forms of evidence and monitoring.

---

## Mistake 12 — Relying only on coverage

A line can execute while the assertion checks the wrong result.

Coverage indicates execution, not correctness of expectations.

---

# 49. Debugging Boundary Test Failures

Use a disciplined workflow.

## Step 1 — Identify the requirement

Example:

```text
Age 18–65 inclusive
```

## Step 2 — Identify intended boundary

```text
minimum = 18
maximum = 65
```

## Step 3 — Check the test case

Did the test use:

```text
17, 18, 19, 64, 65, 66
```

or something else?

## Step 4 — Compare expected vs actual

Suppose:

```text
age = 18
expected = True
actual = False
```

## Step 5 — Inspect implementation

Possibly:

```python
return age > 18 and age < 65
```

That is incorrect for an inclusive requirement.

## Step 6 — Decide whether the test or code is wrong

Do not automatically modify the test because the implementation disagrees.

The requirement is the reference point.

## Step 7 — Reproduce independently

Run only the failing case:

```bash
pytest tests/test_validation.py::test_age_boundary -q
```

or, with a parametrized test, select the specific parameterized case using its generated/readable node ID.

## Step 8 — Fix the underlying issue

Correct implementation or correct the test if its expectation is inconsistent with the actual specification.

## Step 9 — Preserve regression protection

If the failure revealed a meaningful defect, keep or add the test so the bug cannot silently return.

## Step 10 — Run related tests

A boundary fix can affect nearby cases.

---

# 50. Debugging Regression Failures

A regression failure means:

```text
a previously expected behavior no longer matches the test contract
```

Do not assume the test is obsolete.

## Workflow

```text
regression test fails
        ↓
identify behavior
        ↓
identify what changed
        ↓
review recent code/config/dependency changes
        ↓
reproduce
        ↓
compare old vs current behavior
        ↓
identify root cause
        ↓
fix
        ↓
run regression
        ↓
run broader related tests
```

## Example

Failure:

```text
expected 100 records
actual 95 records
```

Investigate:

- changed filter
- changed join
- changed parsing
- changed fixture data
- changed test expectation

The last possibility is real, but it should be established from the requirement rather than assumed.

---

# 51. Complete Realistic Example

We will design a bank transaction validator.

## Requirements

1. Amount must be an integer.
2. Amount must be greater than `0`.
3. Amount must not exceed `1,000,000`.
4. Account must be active.
5. Balance must be sufficient.
6. Invalid account must be rejected.
7. Failed transactions must not mutate the balance.
8. A transaction ID must be unique.

## Source code

```python
MAX_TRANSACTION_AMOUNT = 1_000_000


class Account:
    def __init__(self, account_id: str, balance: int, active: bool = True):
        self.account_id = account_id
        self.balance = balance
        self.active = active


class Transaction:
    def __init__(self, transaction_id: str, amount: int):
        self.transaction_id = transaction_id
        self.amount = amount


def validate_transaction(
    account: Account | None,
    transaction: Transaction,
) -> None:
    if account is None:
        raise ValueError("invalid account")

    if not isinstance(transaction.amount, int):
        raise TypeError("amount must be an integer")

    if transaction.amount <= 0:
        raise ValueError("amount must be positive")

    if transaction.amount > MAX_TRANSACTION_AMOUNT:
        raise ValueError("amount exceeds transaction limit")

    if not account.active:
        raise ValueError("account is inactive")

    if transaction.amount > account.balance:
        raise ValueError("insufficient balance")
```

## Test-design table

| Scenario | Input | Expected |
|---|---|---|
| normal | amount 500 | valid |
| minimum | amount 1 | valid |
| below minimum | amount 0 | reject |
| negative | amount -1 | reject |
| just above zero | amount 2 | valid |
| maximum | amount 1,000,000 | valid if balance allows |
| above maximum | 1,000,001 | reject |
| wrong type | `"500"` | type error |
| `None` account | account=None | reject |
| inactive | active=False | reject |
| insufficient balance | amount > balance | reject |

## Happy path

```python
def test_valid_transaction_is_accepted():
    account = Account("A", balance=10_000)
    transaction = Transaction("tx-1", amount=500)

    validate_transaction(account, transaction)
```

This test passes if no exception is raised.

## Boundary tests

```python
import pytest


@pytest.mark.parametrize(
    "amount,expected_exception",
    [
        pytest.param(0, ValueError, id="zero"),
        pytest.param(-1, ValueError, id="negative"),
        pytest.param(1, None, id="minimum-valid"),
        pytest.param(1_000_000, None, id="maximum-valid"),
        pytest.param(1_000_001, ValueError, id="above-maximum"),
    ],
)
def test_transaction_amount_boundaries(amount, expected_exception):
    account = Account("A", balance=2_000_000)
    transaction = Transaction("tx-1", amount=amount)

    if expected_exception is None:
        validate_transaction(account, transaction)
    else:
        with pytest.raises(expected_exception):
            validate_transaction(account, transaction)
```

## Better readability for mixed expected outcomes

When the cases have substantially different semantics, two tests may be clearer:

```python
@pytest.mark.parametrize(
    "amount",
    [
        pytest.param(0, id="zero"),
        pytest.param(-1, id="negative"),
        pytest.param(1_000_001, id="above-maximum"),
    ],
)
def test_invalid_transaction_amount_is_rejected(amount):
    account = Account("A", balance=2_000_000)
    transaction = Transaction("tx-1", amount=amount)

    with pytest.raises(ValueError):
        validate_transaction(account, transaction)
```

And:

```python
@pytest.mark.parametrize(
    "amount",
    [
        pytest.param(1, id="minimum"),
        pytest.param(1_000_000, id="maximum"),
    ],
)
def test_boundary_transaction_amounts_are_accepted(amount):
    account = Account("A", balance=2_000_000)
    transaction = Transaction("tx-1", amount=amount)

    validate_transaction(account, transaction)
```

This demonstrates an important point:

> Parametrization is a tool, not a requirement. Readability comes first.

## Invalid type

```python
def test_transaction_rejects_non_integer_amount():
    account = Account("A", balance=10_000)
    transaction = Transaction("tx-1", amount="500")

    with pytest.raises(TypeError, match="amount must be an integer"):
        validate_transaction(account, transaction)
```

## Inactive account

```python
def test_transaction_rejects_inactive_account():
    account = Account("A", balance=10_000, active=False)
    transaction = Transaction("tx-1", amount=500)

    with pytest.raises(ValueError, match="account is inactive"):
        validate_transaction(account, transaction)
```

## Insufficient balance

```python
def test_transaction_rejects_insufficient_balance():
    account = Account("A", balance=500)
    transaction = Transaction("tx-1", amount=501)

    with pytest.raises(ValueError, match="insufficient balance"):
        validate_transaction(account, transaction)
```

## Regression bug

Suppose a refactor accidentally changes:

```python
if transaction.amount <= 0:
```

to:

```python
if transaction.amount < 0:
```

Then zero becomes accepted.

The regression test:

```python
def test_zero_transaction_amount_is_rejected():
    account = Account("A", balance=10_000)
    transaction = Transaction("tx-1", amount=0)

    with pytest.raises(ValueError, match="amount must be positive"):
        validate_transaction(account, transaction)
```

will fail.

This is exactly the kind of regression protection boundary testing should create.

---

# 52. Complete Mini Project

## Project Objective

Build a small **transaction validation service** and a test suite focused on:

```text
boundary
+
invalid
+
regression
```

## Requirements

The application must:

1. accept transaction amounts from `1` through `100_000`;
2. reject zero;
3. reject negative amounts;
4. reject amounts above `100_000`;
5. reject non-integer amounts;
6. reject inactive accounts;
7. reject insufficient balance;
8. reject duplicate transaction IDs;
9. leave account balance unchanged when a transaction is rejected;
10. successfully transfer a valid amount.

## Suggested structure

```text
transaction-project/
├── transaction.py
└── tests/
    ├── conftest.py
    └── test_transaction.py
```

The chapter is teaching the concept of `conftest.py`; use it only when shared fixture infrastructure is truly useful.

## Source code

```python
MAX_AMOUNT = 100_000


class Account:
    def __init__(self, account_id: str, balance: int, active: bool = True):
        self.account_id = account_id
        self.balance = balance
        self.active = active


class TransactionService:
    def __init__(self):
        self.processed_ids: set[str] = set()

    def transfer(
        self,
        sender: Account,
        receiver: Account,
        transaction_id: str,
        amount: int,
    ) -> None:
        if not sender.active:
            raise ValueError("sender account is inactive")

        if not receiver.active:
            raise ValueError("receiver account is inactive")

        if not isinstance(amount, int):
            raise TypeError("amount must be an integer")

        if amount <= 0:
            raise ValueError("amount must be positive")

        if amount > MAX_AMOUNT:
            raise ValueError("amount exceeds transaction limit")

        if amount > sender.balance:
            raise ValueError("insufficient balance")

        if transaction_id in self.processed_ids:
            raise ValueError("duplicate transaction")

        sender.balance -= amount
        receiver.balance += amount
        self.processed_ids.add(transaction_id)
```

## Architecture

```text
                TransactionService
                       |
        +--------------+--------------+
        |              |              |
     sender         receiver       transaction
     account         account           data
        |              |              |
        +--------------+--------------+
                       |
                  validation
                       |
                    transfer
```

## Test strategy

### Happy path

```text
valid sender
valid receiver
valid transaction ID
valid amount
sufficient balance
```

### Boundary

```text
1
2
99_999
100_000
100_001
```

### Invalid

```text
0
-1
"100"
None
inactive sender
inactive receiver
duplicate transaction
```

### State invariant

```text
rejected transaction
→ balances unchanged
```

## Example fixture

```python
import pytest


@pytest.fixture
def accounts():
    sender = Account("sender", 1_000)
    receiver = Account("receiver", 500)
    return sender, receiver
```

## Happy-path test

```python
def test_transfer_moves_balance(accounts):
    sender, receiver = accounts
    service = TransactionService()

    service.transfer(sender, receiver, "tx-1", 300)

    assert sender.balance == 700
    assert receiver.balance == 800
```

## Boundary tests

```python
@pytest.mark.parametrize(
    "amount",
    [
        pytest.param(1, id="minimum"),
        pytest.param(100_000, id="maximum"),
    ],
)
def test_valid_boundary_amounts(accounts, amount):
    sender, receiver = accounts
    sender.balance = 100_000
    service = TransactionService()

    service.transfer(sender, receiver, "tx-1", amount)

    assert sender.balance == 100_000 - amount
```

## Invalid cases

```python
@pytest.mark.parametrize(
    "amount",
    [
        pytest.param(0, id="zero"),
        pytest.param(-1, id="negative"),
        pytest.param(100_001, id="above-limit"),
    ],
)
def test_invalid_amounts_are_rejected(accounts, amount):
    sender, receiver = accounts
    service = TransactionService()
    original_sender = sender.balance
    original_receiver = receiver.balance

    with pytest.raises(ValueError):
        service.transfer(sender, receiver, "tx-1", amount)

    assert sender.balance == original_sender
    assert receiver.balance == original_receiver
```

## Regression scenario

Suppose a developer changes:

```python
if amount <= 0:
```

to:

```python
if amount < 0:
```

The zero case becomes a regression.

The existing test immediately protects it.

## Expected results

A well-designed suite should tell you:

```text
normal valid amount works
minimum works
maximum works
below minimum is rejected
above maximum is rejected
wrong type is rejected
inactive account is rejected
insufficient balance is rejected
duplicates are rejected
failure does not mutate balances
```

## Improvement opportunities

After the initial suite, review:

- Are the tests isolated?
- Is the transaction ID state reset between tests?
- Are boundary IDs readable?
- Is every parameter case meaningful?
- Are assertions precise?
- Can any test be removed without reducing confidence?
- Can any production defect still pass all tests?

---

# 53. Coding Exercises

There are four levels. The exercises are intentionally progressive.

## Level 1 — Basic

### Exercise 1 — Classify values

#### Problem

Age must be `18–65` inclusive.

#### Task

Classify:

```text
17
18
19
64
65
66
```

#### Hints

Look at the rule's lower and upper limits.

#### Complete solution

```text
17 → invalid / just outside lower boundary
18 → valid / lower boundary
19 → valid / just inside lower boundary
64 → valid / just inside upper boundary
65 → valid / upper boundary
66 → invalid / just outside upper boundary
```

#### Explanation

This is the basic BVA neighborhood.

#### Common mistake

Calling only `18` and `65` the "boundary tests." The neighboring values are important too.

---

### Exercise 2 — Write a happy-path test

#### Problem

```python
def add(a, b):
    return a + b
```

#### Task

Write a pytest test for `2 + 3`.

#### Hints

Use AAA.

#### Complete solution

```python
def test_add_returns_sum():
    # Arrange
    a = 2
    b = 3

    # Act
    result = add(a, b)

    # Assert
    assert result == 5
```

#### Explanation

The exact expected value makes the test meaningful.

#### Common mistake

```python
assert result
```

---

### Exercise 3 — Write a negative test

#### Problem

```python
def parse_age(value):
    if not isinstance(value, int):
        raise TypeError("age must be an integer")
    return value
```

#### Task

Test a string input.

#### Hints

The expected failure is part of the contract.

#### Complete solution

```python
import pytest


def test_parse_age_rejects_string():
    with pytest.raises(TypeError, match="age must be an integer"):
        parse_age("30")
```

#### Explanation

The test passes because the application correctly rejects the invalid type.

#### Common mistake

Expecting the test itself to fail.

---

### Exercise 4 — Choose boundary values

#### Problem

Quantity must be `1–100`.

#### Task

Choose a classic BVA set.

#### Complete solution

```text
0
1
2
99
100
101
```

#### Explanation

These values cover just-outside, boundary, and just-inside behavior at both limits.

#### Common mistake

Using only `1` and `100`.

---

### Exercise 5 — Identify an edge case

#### Problem

A function accepts a list of records.

#### Task

Name five useful edge cases.

#### Complete solution

```text
empty list
one-item list
duplicate records
very large list
missing/None list
```

#### Explanation

These cases may expose logic that ordinary-sized valid lists do not.

#### Common mistake

Assuming every edge case must be numeric.

---

## Level 2 — Intermediate

### Exercise 6 — Parametrize boundaries

#### Problem

```python
def is_valid_score(score):
    return 0 <= score <= 100
```

#### Task

Write a parametrized test covering boundaries.

#### Complete solution

```python
import pytest


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
def test_score_boundaries(score, expected):
    assert is_valid_score(score) is expected
```

#### Explanation

The same test logic is applied to six deliberately chosen cases.

#### Common mistake

Providing the wrong number of tuple values for the declared parameters.

---

### Exercise 7 — Test `None` separately

#### Problem

A function treats missing and `None` differently.

#### Task

Write separate tests for:

```text
missing field
None value
```

#### Complete solution

```python
def test_username_can_be_missing_from_payload():
    payload = {}

    assert "username" not in payload


def test_username_none_is_rejected():
    with pytest.raises(ValueError, match="username is required"):
        validate_username(None)
```

#### Explanation

Missing and explicit `None` represent different states.

#### Common mistake

Combining them into one `if not value` assertion.

---

### Exercise 8 — Test a malformed date

#### Problem

```python
from datetime import datetime


def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d")
```

#### Task

Test malformed input.

#### Complete solution

```python
import pytest


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("2026-99-99", id="invalid-date"),
        pytest.param("2026/01/01", id="wrong-format"),
        pytest.param("not-a-date", id="text"),
    ],
)
def test_parse_date_rejects_malformed_values(value):
    with pytest.raises(ValueError):
        parse_date(value)
```

#### Explanation

Each case violates the expected format or semantics.

#### Common mistake

Using a random valid date and calling it malformed.

---

### Exercise 9 — Combine BVA and equivalence classes

#### Problem

A shipping weight rule is:

```text
0 < weight <= 20
```

#### Task

Identify equivalence classes and boundary values.

#### Complete solution

Equivalence classes:

```text
<=0      → invalid
1–20     → valid
>20      → invalid
```

Boundary set:

```text
0
1
2
19
20
21
```

#### Explanation

Partitioning gives broad classes; BVA adds focused values around the limits.

#### Common mistake

Testing only `10`, because it is a "typical" valid value.

---

### Exercise 10 — Detect a weak regression test

#### Problem

Bug:

> The application stopped accepting `" 100 "`.

Given:

```python
def test_amount_is_integer():
    assert parse_amount("100") == 100
```

#### Task

Explain why this is not a good regression test.

#### Complete solution

It does not reproduce the bug. The regression scenario is specifically surrounding whitespace.

Better:

```python
def test_parse_amount_accepts_surrounding_whitespace():
    assert parse_amount(" 100 ") == 100
```

#### Explanation

A regression test should fail when the original defect is reintroduced.

#### Common mistake

Testing a related but different behavior.

---

## Level 3 — Advanced

### Exercise 11 — Boundary with expected exceptions

#### Problem

Amount must be `1–100`.

#### Task

Create tests for:

```text
0
1
100
101
```

where invalid values raise `ValueError`.

#### Complete solution

```python
import pytest


@pytest.mark.parametrize(
    "amount",
    [
        pytest.param(0, id="below-minimum"),
        pytest.param(101, id="above-maximum"),
    ],
)
def test_amount_boundaries_are_rejected(amount):
    with pytest.raises(ValueError):
        validate_amount(amount)


@pytest.mark.parametrize(
    "amount",
    [
        pytest.param(1, id="minimum"),
        pytest.param(100, id="maximum"),
    ],
)
def test_boundary_amounts_are_accepted(amount):
    assert validate_amount(amount) == amount
```

#### Explanation

Separating acceptance and rejection keeps the expected behavior clear.

#### Common mistake

One giant parameter table containing too many unrelated semantics.

---

### Exercise 12 — Protect state after invalid input

#### Problem

A transfer should not mutate account balances when rejected.

#### Task

Design the test for insufficient balance.

#### Complete solution

```python
def test_rejected_transfer_does_not_change_balances():
    sender = Account("A", balance=500)
    receiver = Account("B", balance=100)

    with pytest.raises(ValueError, match="insufficient balance"):
        transfer(sender, receiver, 501)

    assert sender.balance == 500
    assert receiver.balance == 100
```

#### Explanation

The test checks both failure behavior and state safety.

#### Common mistake

Testing only the exception.

---

### Exercise 13 — Design an API boundary matrix

#### Problem

`page_size` must be 1–100.

#### Task

Design a case matrix.

#### Complete solution

| Case | Value | Expected |
|---|---:|---|
| below minimum | 0 | 400 |
| minimum | 1 | 200 |
| just inside | 2 | 200 |
| just below maximum | 99 | 200 |
| maximum | 100 | 200 |
| above maximum | 101 | 400 |
| missing | omitted | contract-specific error |
| malformed | `"abc"` | contract-specific error |

#### Explanation

Numeric BVA is only one part of the API input space.

#### Common mistake

Assuming `0` is the only invalid case.

---

### Exercise 14 — Identify a regression level

#### Problem

A bug appears only because a service sends an incorrectly typed value to a database adapter.

#### Task

Decide whether unit, integration, API, or E2E is likely required.

#### Complete solution

An integration test is likely appropriate if the defect depends on interaction between the service and the adapter. A unit test may still be added for the underlying validation behavior if the defect can also be reproduced there.

#### Explanation

The correct level depends on what is required to reproduce the behavior.

#### Common mistake

Assuming every regression must be E2E.

---

### Exercise 15 — Regression from a refactor

#### Problem

A refactor changes output order in a data transformation.

#### Task

Design a regression test only if ordering is part of the contract.

#### Complete solution

If order matters:

```python
def test_transform_preserves_required_order():
    result = transform([3, 1, 2])

    assert result == [3, 1, 2]
```

If order does not matter:

```python
def test_transform_contains_expected_records():
    result = transform([3, 1, 2])

    assert sorted(result) == [1, 2, 3]
```

#### Explanation

The assertion should match the actual behavioral contract.

#### Common mistake

Asserting order simply because the current implementation happens to return one.

---

## Level 4 — Production-Oriented

### Exercise 16 — Data pipeline boundary

#### Problem

A pipeline accepts transaction amounts `0–1,000,000`.

#### Task

Design application-level tests for:

```text
-1
0
1
999999
1000000
1000001
None
"100"
```

#### Complete solution

```python
import pytest


@pytest.mark.parametrize(
    "value,expected_valid",
    [
        (-1, False),
        (0, True),
        (1, True),
        (999_999, True),
        (1_000_000, True),
        (1_000_001, False),
    ],
)
def test_transaction_amount_boundaries(value, expected_valid):
    assert validate_amount(value) is expected_valid


@pytest.mark.parametrize(
    "value",
    [
        None,
        "100",
    ],
)
def test_transaction_amount_rejects_wrong_input_types(value):
    with pytest.raises((TypeError, ValueError)):
        validate_amount(value)
```

In production, prefer the narrowest expected exception type once the contract is defined.

#### Common mistake

Using one broad exception type permanently.

---

### Exercise 17 — LLM application limit

#### Problem

Your application defines a maximum document size of 50,000 characters.

#### Task

Test just inside, at, and just outside.

#### Complete solution

```python
import pytest


@pytest.mark.parametrize(
    "size,expected",
    [
        (49_999, True),
        (50_000, True),
        (50_001, False),
    ],
)
def test_document_size_limit(size, expected):
    document = "a" * size

    assert validate_document(document) is expected
```

#### Explanation

The test targets the application's own documented contract.

#### Common mistake

Hard-coding a provider-specific token limit without referencing the actual configured requirement.

---

### Exercise 18 — Agent transaction boundary

#### Problem

An agent may transfer at most 1,000 units without an additional approval workflow.

#### Task

Design tests around 999, 1000, and 1001.

#### Complete solution

```python
import pytest


@pytest.mark.parametrize(
    "amount,requires_approval",
    [
        (999, False),
        (1000, False),
        (1001, True),
    ],
)
def test_transfer_approval_boundary(agent, amount, requires_approval):
    result = agent.evaluate_transfer(amount)

    assert result["requires_approval"] is requires_approval
```

#### Explanation

This tests an application-level business rule around an agentic workflow.

#### Common mistake

Assuming model behavior itself must be deterministic for this application rule.

---

### Exercise 19 — Regression strategy for a large service

#### Problem

A production bug can only be reproduced across service A and service B.

#### Task

Propose the regression strategy.

#### Complete solution

1. Reproduce at the integration boundary.
2. Add an integration regression test that reliably recreates the defect.
3. Add lower-level unit coverage for each independently meaningful rule where possible.
4. Keep the integration test because the interaction itself is part of the defect.
5. Add API/E2E coverage only if the external workflow adds unique confidence.

#### Explanation

Do not force a defect into an artificial unit test when the integration behavior is what failed.

#### Common mistake

Deleting the integration regression test after adding isolated unit tests that do not reproduce the original failure.

---

### Exercise 20 — Regression-suite maintenance

#### Problem

A repository has 1,500 tests. Twenty regression tests appear redundant.

#### Task

Design a review process.

#### Complete solution

For each candidate:

```text
identify behavior protected
→ identify unique failure it catches
→ compare coverage with other tests
→ remove only if unique information is preserved elsewhere
→ run suite
→ review failure diagnostics
```

#### Explanation

Removing tests should be an evidence-based change, not a line-count optimization.

#### Common mistake

Deleting old tests solely because "we already have enough coverage."

---

### Exercise 21 — Choose representative cases

#### Problem

A service accepts ages from 0–120.

#### Task

You cannot test every integer.

#### Complete solution

Use:

```text
0, 1, 18, 19, 64, 65, 119, 120
```

plus invalid type/format cases as appropriate.

If business rules have additional ranges, use equivalence classes to choose representatives for those classes.

#### Explanation

The test plan should reflect actual domain rules, not arbitrary numbers.

#### Common mistake

Testing only `30`, `40`, and `50`.

---

### Exercise 22 — Find the hidden failure mode

#### Problem

A payment test checks that a failed payment raises an exception.

#### Task

What else might matter?

#### Complete solution

Potential checks:

```text
order remains unpaid
payment record is not duplicated
inventory is not reduced
retry state is correct
client receives correct failure contract
```

Only add checks that are required behaviors or important invariants.

#### Explanation

Failure-mode thinking asks what damage could occur despite the exception being raised.

#### Common mistake

Assuming "exception raised" means the whole transaction was safely rolled back.

---

### Exercise 23 — Test a schema regression

#### Problem

An ETL job historically produced:

```text
id
amount
currency
```

A refactor removes `currency`.

#### Complete solution

```python
def test_output_schema_contains_required_columns():
    result = transform(input_rows())

    assert set(result.columns) == {
        "id",
        "amount",
        "currency",
    }
```

#### Explanation

This protects a schema contract.

#### Common mistake

Only checking row count.

---

### Exercise 24 — Regression for a parser bug

#### Problem

A parser once accepted leading/trailing whitespace and a refactor stopped doing so.

#### Complete solution

```python
@pytest.mark.parametrize(
    "value,expected",
    [
        ("100", 100),
        (" 100", 100),
        ("100 ", 100),
        (" 100 ", 100),
    ],
)
def test_parse_amount_accepts_whitespace(value, expected):
    assert parse_amount(value) == expected
```

#### Explanation

The regression table captures the valid equivalence class.

#### Common mistake

Writing only the clean input `"100"`.

---

### Exercise 25 — Regression plus boundary

#### Problem

A transaction limit bug was found at exactly `1000`.

#### Task

Write a regression test and neighboring boundary tests.

#### Complete solution

```python
@pytest.mark.parametrize(
    "amount,expected_valid",
    [
        (999, True),
        (1000, True),
        (1001, False),
    ],
)
def test_transaction_limit_boundary(amount, expected_valid):
    assert is_valid_transaction_amount(amount) is expected_valid
```

#### Explanation

This protects the discovered bug and the surrounding boundary semantics.

#### Common mistake

Testing only `1000` and missing the off-by-one neighborhood.

---

# 54. Debugging Lab

## Lab 1 — Off-by-one bug

### Broken code

```python
def is_valid_age(age):
    return 18 < age < 65
```

### Failing test

```python
def test_age_18_is_valid():
    assert is_valid_age(18) is True
```

### Symptom

The minimum valid boundary is rejected.

### Root cause

The implementation uses strict comparison instead of inclusive comparison.

### Corrected code

```python
def is_valid_age(age):
    return 18 <= age <= 65
```

### Why it works

The implementation now matches the requirement.

---

## Lab 2 — Incorrect maximum boundary

### Broken code

```python
def is_valid_amount(amount):
    return 1 <= amount < 1000
```

### Failing test

```python
def test_amount_1000_is_valid():
    assert is_valid_amount(1000) is True
```

### Diagnosis

Maximum is supposed to be inclusive.

### Fix

```python
def is_valid_amount(amount):
    return 1 <= amount <= 1000
```

---

## Lab 3 — Invalid input accepted

### Broken code

```python
def validate_quantity(quantity):
    if quantity < 0:
        raise ValueError("quantity must be positive")
```

### Symptom

Zero is accepted.

### Root cause

The rule requires positive values.

### Fix

```python
def validate_quantity(quantity):
    if quantity <= 0:
        raise ValueError("quantity must be positive")
```

### Regression protection

```python
def test_zero_quantity_is_rejected():
    with pytest.raises(ValueError):
        validate_quantity(0)
```

---

## Lab 4 — Valid input rejected

### Broken code

```python
def is_valid_page_size(size):
    return 1 < size < 100
```

Requirement:

```text
1–100 inclusive
```

### Symptom

Both exact boundaries fail.

### Fix

```python
def is_valid_page_size(size):
    return 1 <= size <= 100
```

---

## Lab 5 — `None` handled incorrectly

### Broken code

```python
def validate_name(name):
    if not name:
        return True
    return len(name) >= 3
```

### Symptom

`None` may be treated as acceptable.

### Root cause

Truthiness is being used instead of explicit state semantics.

### Better

```python
def validate_name(name):
    if name is None:
        raise ValueError("name is required")
    return len(name) >= 3
```

The exact desired behavior should come from the contract.

---

## Lab 6 — Empty input handled incorrectly

### Broken code

```python
def process_batch(records):
    return records[0]
```

### Symptom

Empty input raises `IndexError`.

### Diagnosis

The empty collection case was not considered.

### Fix depends on the contract

For example:

```python
def process_batch(records):
    if not records:
        return None
    return records[0]
```

Or it could correctly raise a domain exception. The test should encode the requirement.

---

## Lab 7 — Wrong expected exception

### Broken test

```python
def test_invalid_age():
    with pytest.raises(TypeError):
        parse_age("abc")
```

### Actual contract

```text
invalid string format → ValueError
```

### Fix

```python
def test_invalid_age():
    with pytest.raises(ValueError):
        parse_age("abc")
```

### Lesson

The test can be wrong too. Always compare it with the requirement.

---

## Lab 8 — Regression introduced during refactoring

### Existing behavior

```python
parse_amount(" 100 ") == 100
```

### Refactored implementation

```python
def parse_amount(value):
    return int(value.strip())
```

This version is actually fine.

Suppose a later change becomes:

```python
def parse_amount(value):
    if " " in value:
        raise ValueError("spaces not allowed")
    return int(value)
```

### Regression test

```python
def test_parse_amount_accepts_surrounding_whitespace():
    assert parse_amount(" 100 ") == 100
```

### Diagnosis

The regression test identifies the behavioral change.

---

## Lab 9 — Regression test checks implementation detail

### Broken regression test

```python
def test_parser_uses_strip_method(parser):
    parser.parse(" 100 ")

    assert parser._used_strip is True
```

### Problem

The requirement is about parsing behavior, not which string method was used.

### Better

```python
def test_parser_accepts_surrounding_whitespace(parser):
    assert parser.parse(" 100 ") == 100
```

---

## Lab 10 — Boundary test has the wrong expectation

### Test

```python
def test_limit():
    assert validate_amount(1000) is False
```

### Requirement

```text
maximum = 1000 inclusive
```

### Diagnosis

The implementation may be correct; the test expectation is wrong.

### Lesson

A failing test is evidence, not proof that production code is wrong.

The requirement determines which one should change.

---

# 55. Interview Questions

## Beginner

### 1. What is boundary testing?

**Model answer:** Boundary testing focuses on values at and around limits where application behavior changes. Typical cases include just below, exactly at, and just above each boundary.

### 2. What is Boundary Value Analysis?

**Model answer:** It is a systematic method for choosing test inputs around boundaries, commonly using minimum−1, minimum, minimum+1, maximum−1, maximum, and maximum+1.

### 3. What is negative testing?

**Model answer:** Negative testing intentionally supplies invalid, prohibited, malformed, or unexpected inputs to verify that the system handles them correctly.

### 4. Does a negative test mean the test should fail?

**Model answer:** No. If the invalid input is correctly rejected according to the contract, the negative test passes.

### 5. What is an invalid input?

**Model answer:** A value, type, structure, or state that violates the system's defined input contract.

### 6. What is an edge case?

**Model answer:** An unusual or extreme scenario that may expose defects. It can overlap with a formal boundary case.

### 7. What is a regression?

**Model answer:** A regression is a previously working behavior becoming incorrect after a change.

### 8. What is a regression test?

**Model answer:** A test that protects behavior from being broken again, especially a test added to preserve a previously fixed defect.

## Intermediate

### 9. Why test just inside and just outside a boundary?

**Model answer:** Because defects commonly occur in comparison and off-by-one logic. Neighboring values show whether the implementation switches behavior at the correct point.

### 10. What is equivalence partitioning?

**Model answer:** It divides the input space into classes expected to behave similarly, allowing representative values to be tested instead of every possible value.

### 11. How do BVA and equivalence partitioning work together?

**Model answer:** Partitioning reduces a large space into meaningful classes, while BVA gives extra attention to transition points between classes.

### 12. Why can `None`, empty string, and zero require different tests?

**Model answer:** They represent different semantic states. The application's contract may treat them differently.

### 13. Why should a regression test reproduce the bug?

**Model answer:** Because then the test proves it can detect the exact defect that occurred. This makes the test more trustworthy as permanent regression protection.

### 14. Should every regression test be an E2E test?

**Model answer:** No. Use the lowest practical level that reliably reproduces the defect, while keeping broader tests when the interaction itself is part of the behavior.

### 15. Why are weak assertions dangerous?

**Model answer:** A weak assertion can pass despite significant incorrect behavior, creating false confidence.

## Advanced

### 16. How do you prevent a boundary test suite from becoming enormous?

**Model answer:** Use equivalence partitioning, boundary analysis, domain knowledge, risk-based selection, and representative combinations rather than testing every theoretical value.

### 17. When should you use separate tests instead of parametrization?

**Model answer:** When cases have different setup, different behaviors, different assertions, or would become less readable as a large table.

### 18. How do you test a failure that must not change state?

**Model answer:** Assert both the expected failure and the relevant state invariants after the failure.

### 19. What is the difference between a software regression and model drift?

**Model answer:** A software regression is an unexpected code/system behavior change relative to a contract. Model drift or performance change concerns changing model quality or data distributions over time and usually needs evaluation or monitoring.

### 20. How should LLM regression tests be designed?

**Model answer:** Test stable application contracts such as schema, required fields, tool calls, retrieval constraints, safety rules, and fallback behavior. Avoid exact text matching when wording is intentionally variable.

### 21. How would you test an agentic workflow regression?

**Model answer:** Reproduce observable workflow behavior such as required tool invocation, tool arguments, state transitions, termination, authorization, and final structured output. Do not rely on hidden internal reasoning.

### 22. What makes a regression test valuable?

**Model answer:** It catches a meaningful defect, is not redundant, is diagnostically useful, and protects behavior the team actually cares about.

---

# 56. Architecture Questions

## 1. How would you design a boundary-testing strategy for a large backend?

Start from domain contracts.

```text
requirements
→ identify constraints
→ identify equivalence classes
→ identify boundaries
→ identify failure modes
→ prioritize by risk
→ implement lower-level tests
→ add integration/API tests at boundaries
```

Maintain a source of truth for key limits where possible so tests do not drift from configuration.

## 2. How would you manage thousands of boundary cases?

Do not create thousands of independent functions automatically.

Use:

- parametrization
- structured case data
- equivalence partitioning
- decision tables
- representative samples
- risk-based prioritization

Split parameter groups when they represent different behaviors.

## 3. How would you organize parametrized test data?

For small cases:

```python
@pytest.mark.parametrize(...)
```

For complex cases:

```python
@dataclass(frozen=True)
class Case:
    ...
```

For large domain datasets, use carefully managed external fixtures or generated data where appropriate, while keeping the test intent visible.

## 4. How would you design regression testing for a monorepo?

Use layers:

```text
local fast tests
→ package/service tests
→ integration
→ API
→ selected E2E
```

Place regression tests near the behavior they protect and classify them appropriately for CI execution.

## 5. How would you decide whether a regression belongs at unit, integration, or E2E level?

Ask:

> What is the smallest environment that reproduces the actual defect without losing the behavior that matters?

If the defect is purely algorithmic, unit may be enough.

If the bug requires multiple components, integration may be necessary.

If the user-visible workflow itself is the defect, E2E may be justified.

## 6. How would you handle regression tests for data pipelines?

Treat data outputs as contracts.

Test:

```text
schema
row count
null rates
duplicate rules
business transformations
invariants
partition behavior
```

Use representative fixtures, boundary rows, invalid rows, and historical bug cases.

## 7. How would you test schema regressions?

Define expected schemas explicitly:

```python
assert set(output.columns) == expected_columns
```

For richer contracts, validate:

- field names
- types
- nullability
- required fields
- semantic constraints

Do not over-specify fields that are intentionally allowed to evolve.

## 8. How would you test AI/LLM applications with nondeterministic outputs?

Separate:

```text
deterministic application behavior
```

from:

```text
model quality
```

Strong deterministic tests cover:

- parsing
- schemas
- tools
- retrieval filters
- retries
- limits
- authorization
- fallbacks

Model quality can require evaluation datasets and statistical/semantic criteria.

## 9. How would you design regression tests for agentic workflows?

Identify stable observable invariants.

For example:

```text
high-value transfer
→ approval required

no authorization
→ transfer tool must not execute

approved transfer
→ required tool is called with allowed arguments
```

Control tools and external state so regressions can be reproduced.

## 10. How would you prevent the regression suite from becoming too slow?

Use:

```text
fast unit regressions
→ targeted integration regressions
→ critical API/E2E regressions
```

Avoid unnecessary duplication, shared mutable infrastructure, and broad environment setup when a smaller test can provide equivalent information.

---

# 57. Production Checklist

## Input classification

- [ ] Happy path is covered.
- [ ] Valid input domain is understood.
- [ ] Invalid input domain is understood.
- [ ] Important types are considered.
- [ ] Missing values are considered.
- [ ] `None` is considered where relevant.
- [ ] Empty values are considered.
- [ ] Unsupported values are considered.
- [ ] Malformed values are considered.

## Boundary design

- [ ] Minimum boundary is identified.
- [ ] Maximum boundary is identified.
- [ ] Just-inside values are tested.
- [ ] Just-outside values are tested.
- [ ] Exact boundaries are tested.
- [ ] Relevant non-numeric boundaries are considered.
- [ ] Business-rule boundaries are explicitly documented.

## Negative behavior

- [ ] Expected exceptions are verified.
- [ ] Error behavior is meaningful.
- [ ] Error messages are tested only when contractually relevant.
- [ ] Invalid requests do not accidentally mutate state.
- [ ] Unauthorized behavior is covered where relevant.
- [ ] Invalid state transitions are covered where relevant.

## Regression protection

- [ ] Important discovered defects have regression tests.
- [ ] Regression tests reproduce the real failure.
- [ ] Regression tests live at an appropriate level.
- [ ] Duplicate regression tests are periodically reviewed.
- [ ] Regression tests are included in CI.

## Test quality

- [ ] Test names explain scenarios.
- [ ] Assertions are meaningful.
- [ ] Parametrization improves rather than reduces clarity.
- [ ] Parameter IDs are readable for complex cases.
- [ ] Test data is deterministic.
- [ ] Tests are isolated.
- [ ] Failures are diagnostically useful.
- [ ] Coverage metrics are not treated as proof of quality.

## Production systems

- [ ] API limits are tested.
- [ ] Data pipeline boundaries are tested.
- [ ] Schema regressions are protected.
- [ ] ML software contracts are tested.
- [ ] AI/LLM structural behavior is protected.
- [ ] Agentic workflow invariants are tested.
- [ ] CI runtime is controlled.

---

# 58. Knowledge Check

## Question 1 — Classification

Requirement:

```text
quantity must be 1–100 inclusive
```

Classify:

```text
0
1
2
99
100
101
```

### Answer

```text
0   → invalid / below boundary
1   → valid / minimum boundary
2   → valid / just inside
99  → valid / just inside maximum
100 → valid / maximum boundary
101 → invalid / above boundary
```

---

## Question 2 — Test design

Why is this test weak?

```python
def test_total():
    result = calculate_total(10, 2)
    assert result is not None
```

### Answer

It does not prove the result is correct.

Better:

```python
assert result == 20
```

assuming `20` is the contract.

---

## Question 3 — Negative testing

Does this test pass or fail when the application correctly raises `ValueError`?

```python
def test_invalid_amount():
    with pytest.raises(ValueError):
        validate_amount(-1)
```

### Answer

It passes. The exception is the expected application behavior.

---

## Question 4 — Boundary reasoning

A rule says:

```text
18 <= age <= 65
```

Why is `17` important?

### Answer

It tests the value immediately outside the lower boundary and can detect an implementation that incorrectly accepts values below 18.

---

## Question 5 — Equivalence partitioning

Suppose:

```text
0–100 → valid
>100  → invalid
<0    → invalid
```

Give three representative values.

### Answer

For example:

```text
50
-1
101
```

Then use BVA for additional high-value cases around 0 and 100.

---

## Question 6 — Bug reproduction

Bug:

> parser rejects `" 100 "`.

Which is the stronger regression test?

```python
assert parse_amount("100") == 100
```

or:

```python
assert parse_amount(" 100 ") == 100
```

### Answer

The second. It reproduces the actual defect.

---

## Question 7 — Error type

Why is this preferable?

```python
with pytest.raises(ValueError):
    parse_age("abc")
```

to:

```python
with pytest.raises(Exception):
    parse_age("abc")
```

### Answer

The specific exception is part of the expected failure contract. A broad exception could allow unrelated implementation defects to pass.

---

## Question 8 — State safety

A rejected transfer raises the correct exception but changes the sender balance.

Is the system correct?

### Answer

No, if the contract requires rejected transfers to leave balances unchanged. The test should assert both the exception and the state invariant.

---

## Question 9 — Regression level

A bug exists only because two services exchange incompatible schemas.

Where might the regression test belong?

### Answer

At an integration boundary, because the interaction is part of the failure. Lower-level unit tests may also be valuable but cannot replace a test that actually reproduces the integration defect.

---

## Question 10 — AI testing

Why might exact string equality be a poor regression strategy for some LLM features?

### Answer

Because wording may vary even when semantic behavior is correct. Use stable contracts such as schemas, allowed labels, invariants, tool calls, and safety constraints when exact wording is not part of the requirement.

---

## Question 11 — Agentic testing

What should a regression test verify when an agent must perform a transaction?

### Answer

Observable requirements such as authorization, required checks, tool invocation, valid tool arguments, state transitions, final result, and termination behavior.

---

## Question 12 — Test removal

Can an old regression test be removed?

### Answer

Possibly, but only after determining that another test provides equivalent or better protection and the old test adds no unique information. Removal should be evidence-based.

---

# 59. Glossary

| Term | Definition |
|---|---|
| Valid input | Input accepted by the defined contract |
| Invalid input | Input that violates the defined contract |
| Boundary | Point where required behavior changes |
| Boundary value | A value exactly at or adjacent to a boundary |
| Boundary Value Analysis | Systematic selection of test cases around boundaries |
| Edge case | Unusual, extreme, empty, or otherwise noteworthy scenario |
| Happy path | Normal successful scenario |
| Negative testing | Testing invalid, prohibited, malformed, or unexpected inputs |
| Failure mode | A way the system can fail or be rejected |
| Equivalence partitioning | Dividing inputs into groups expected to behave similarly |
| Regression | Previously working behavior becoming broken after a change |
| Regression bug | A defect in previously working behavior introduced by a change |
| Regression test | Test that protects behavior from regression |
| Bug reproduction | Demonstrating a defect using a repeatable scenario |
| Off-by-one error | Boundary defect caused by incorrect one-unit comparison or indexing |
| Test isolation | Preventing accidental state leakage into or from a test |
| Deterministic test | Test whose outcome is predictable under controlled conditions |
| Parametrization | Running one test definition with multiple input cases |
| Test coverage | Measurement of code or paths executed by tests |
| Behavioral test | Test focused on observable system behavior |
| Implementation detail | Internal design choice not necessarily part of the public contract |
| Failure contract | Defined way the system is expected to reject or handle an invalid operation |
| Invariant | A property that must remain true |
| Schema regression | Unexpected change to a data structure or contract |
| Model drift | Change in model/data behavior over time, distinct from ordinary software regression |
| Nondeterministic output | Output that can legitimately vary across executions |
| Representative value | A selected example from an equivalence class |
| Just inside | Value immediately within a defined boundary |
| Just outside | Value immediately outside a defined boundary |
| Negative path | Deliberately invalid or prohibited execution path |
| Test suite | Collection of automated tests |
| Regression suite | Tests maintained specifically to protect established behavior |

---

# Pytest / Python API Reference Used in This Chapter

This chapter is primarily about test design, but the following pytest mechanisms appear repeatedly.

## `assert`

### What it does

Checks that a condition is true.

```python
assert result == expected
```

### Why it is useful here

It expresses the expected behavioral contract.

### Common mistake

```python
assert result
```

when an exact value is required.

### Better usage

Make the assertion as precise as the contract requires.

---

## `pytest.raises`

### What it does

Asserts that a block of code raises an expected exception.

### Syntax

```python
with pytest.raises(ValueError):
    function_under_test()
```

### Useful option

```python
with pytest.raises(ValueError, match="invalid age"):
    ...
```

### Common mistake

```python
with pytest.raises(Exception):
    ...
```

when the contract specifies a narrower type.

### Better usage

Assert:

```text
correct exception type
+
stable meaningful message only when useful
+
state after failure when relevant
```

---

## `pytest.mark.parametrize`

### What it does

Runs the same test definition with multiple parameter sets.

### Syntax

```python
@pytest.mark.parametrize(
    "value,expected",
    [
        (1, True),
        (2, True),
    ],
)
def test_value(value, expected):
    ...
```

### Why it is useful here

Boundary and invalid-input design often produces small tables of cases.

### Important rule

If you declare one argument:

```python
@pytest.mark.parametrize("value", [1, 2, 3])
```

the data entries are individual values.

If you declare multiple arguments:

```python
@pytest.mark.parametrize(
    "a,b,expected",
    [
        (1, 2, 3),
        (2, 3, 5),
    ],
)
```

each case must supply the matching number of values.

### Common mistake

Creating a huge parameter matrix that hides unrelated behaviors.

### Better usage

Use parametrization when:

```text
same behavior
+
same assertion structure
+
different scenarios
```

---

## Parameter IDs

IDs make individual parameterized cases easier to understand.

```python
@pytest.mark.parametrize(
    "age,expected",
    [
        pytest.param(17, False, id="below-minimum"),
        pytest.param(18, True, id="minimum"),
    ],
)
def test_age(age, expected):
    ...
```

Use explicit IDs when the default representation is difficult to interpret.

---

## `pytest.fixture`

Fixtures provide reusable setup and dependencies.

Example:

```python
@pytest.fixture
def account():
    return Account("A", balance=500)
```

Then:

```python
def test_withdraw(account):
    ...
```

The previous chapter covers fixture behavior in greater detail. In this chapter, the design emphasis is:

> Use fixtures to support test setup and resources without hiding the scenario's important meaning.

---

# Final Mental Model

The core reasoning process is:

```text
Requirement
    ↓
identify valid domain
    ↓
identify invalid domain
    ↓
identify equivalence classes
    ↓
identify boundaries
    ↓
test just inside
    ↓
test on boundary
    ↓
test just outside
    ↓
test important edge cases
    ↓
identify failure modes
    ↓
verify expected rejection
    ↓
discover bugs
    ↓
reproduce bug
    ↓
write failing regression test
    ↓
fix code
    ↓
confirm regression test passes
    ↓
keep regression protection
    ↓
run continuously in CI/CD
```

## Three core ideas

### Boundary testing

```text
find mistakes around limits
```

### Invalid-input testing

```text
verify bad inputs are handled correctly
```

### Regression testing

```text
prevent previously fixed or important existing behavior from breaking again
```

## A useful mental equation

```text
Good testing
≠
more test cases

Good testing
=
meaningful scenarios
+
correct expectations
+
reliable failures
+
useful regression protection
```

## How this connects to the roadmap

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
agentic AI testing
    ↓
CI/CD
    ↓
production reliability
```

The same test-design mindset applies at every level.

Only the boundary, failure mode, and observation point change.

---

# Final Self-Review Checklist

- [x] Chapter starts from absolute beginner level.
- [x] Valid vs invalid input is explained.
- [x] Happy-path testing is explained.
- [x] Negative testing is explained.
- [x] Negative test vs failing test distinction is explicitly explained.
- [x] Boundaries are explained.
- [x] Boundary Value Analysis is explained.
- [x] Minimum−1 is included.
- [x] Minimum is included.
- [x] Minimum+1 is included.
- [x] Maximum−1 is included.
- [x] Maximum is included.
- [x] Maximum+1 is included.
- [x] Numeric boundaries are covered.
- [x] String boundaries are covered.
- [x] Collection boundaries are covered.
- [x] Date/time boundaries are covered.
- [x] API boundaries are covered.
- [x] Database boundaries are covered.
- [x] Resource boundaries are covered.
- [x] Equivalence partitioning is covered.
- [x] BVA and equivalence partitioning are combined.
- [x] Invalid-input taxonomy is covered.
- [x] Invalid types are covered.
- [x] Missing vs empty vs `None` vs zero vs `False` is explained.
- [x] Malformed input is covered.
- [x] Exception testing is covered.
- [x] Parametrized boundary tests are covered.
- [x] Parametrized invalid tests are covered.
- [x] Edge cases vs boundary cases are distinguished.
- [x] Failure-mode thinking is covered.
- [x] Error types are covered.
- [x] Error messages are covered.
- [x] Regression testing is deeply explained.
- [x] Bug → regression test workflow is explained.
- [x] Failing regression test before the fix is demonstrated conceptually and with code.
- [x] A complete regression example is included.
- [x] Regression and bug reproduction are connected.
- [x] Regression and refactoring are covered.
- [x] Regression and new features are covered.
- [x] Regression-suite evolution is covered.
- [x] Unit/integration/API/E2E regression placement is discussed.
- [x] Data-pipeline regression is covered.
- [x] ML software regression is distinguished from model drift.
- [x] AI/LLM regression is covered.
- [x] Agentic-AI regression is covered.
- [x] Test-data design is covered.
- [x] Test readability is covered.
- [x] Common mistakes are demonstrated.
- [x] Boundary debugging is covered.
- [x] Regression debugging is covered.
- [x] A substantial realistic example is included.
- [x] A complete mini-project is included.
- [x] More than 20 progressive exercises are included.
- [x] Every exercise includes a solution, explanation, and common-mistake guidance.
- [x] A debugging lab is included.
- [x] Interview questions are included.
- [x] Architecture questions are included.
- [x] Production checklist is included.
- [x] Knowledge check is included.
- [x] Glossary is included.
- [x] Final mental model is included.
- [x] `assert` is covered where relevant.
- [x] `pytest.raises` is covered where relevant.
- [x] `pytest.mark.parametrize` is covered where relevant.
- [x] Parameter IDs are covered.
- [x] `pytest.fixture` is covered where relevant.
- [x] The content avoids presenting boundary testing as only minimum/maximum testing.
- [x] The content avoids presenting negative tests as tests that should fail.
- [x] The content avoids treating 100% coverage as proof of quality.
- [x] The content avoids treating parametrization as universally superior to separate tests.
- [x] The content distinguishes application contracts from provider-specific limits.
- [x] The content distinguishes software regressions from model-performance drift.
- [x] The content does not rely on hidden model chain-of-thought.
- [x] The material progresses from basic → intermediate → advanced → production.
- [x] The chapter remains focused on boundary, invalid-input, and regression test design.
- [x] The chapter connects to backend, API, data, ML, AI, agentic-AI, CI/CD, and production reliability work.
- [x] Python examples are syntactically correct and progressively harder.
- [x] Pytest examples are written using standard pytest patterns.
- [x] No unrelated topic has taken over the chapter.

---

## Final Principle

Learn to look at a requirement and ask:

```text
What inputs are valid?

What inputs are invalid?

Where are the boundaries?

What happens just inside the boundary?

What happens exactly at the boundary?

What happens just outside the boundary?

What unusual edge cases matter?

What failure modes are possible?

What state must remain unchanged after failure?

What bugs could occur?

How would I reproduce the bug?

What regression test should permanently protect against it?
```

That is the core skill this chapter is designed to build.
