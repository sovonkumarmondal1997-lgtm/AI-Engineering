# Boundary, Invalid, and Regression Tests — Complete Study Guide

**Stage 1 — Programming & Computational Thinking**  
**Module 07 — Testing and Systematic Debugging**  
**Lesson 04**

> This guide follows the attached lesson. It teaches the chapter's concepts and examples, assesses the current roadmap position, and solves all 25 coding exercises. The exercise-solution section is kept below 3,500 words; the lesson explanation is below 7,500 words.

---

# Part A — Complete Lesson Summary and Teaching Notes

## 1. The purpose of this chapter

Earlier lessons introduced pytest, assertions, fixtures, parametrization, and Arrange–Act–Assert (AAA). This lesson answers a different question:

**Given a requirement, which test cases should we create, and why?**

A good test suite is not simply a large number of tests. It is a carefully selected set of meaningful scenarios, correct expected outcomes, reliable execution, and useful protection against previously discovered defects.

The chapter's learning sequence is:

`requirement → valid/invalid behavior → boundaries → edge cases → equivalence classes → failure modes → bug reproduction → regression test → maintained suite`.

## 2. Valid, invalid, boundary, edge, failure, and regression

A **valid input** is permitted by the system contract. An **invalid input** violates that contract. Validity must come from the written requirement, not a developer's intuition.

Example: age must be from 18 through 65, inclusive.

| Value | Classification |
|---:|---|
| 17 | Invalid; immediately below minimum |
| 18 | Valid; minimum boundary |
| 19 | Valid; just inside minimum |
| 64 | Valid; just inside maximum |
| 65 | Valid; maximum boundary |
| 66 | Invalid; immediately above maximum |

A **boundary** is a limit at which required behavior changes. An **edge case** is an unusual or extreme scenario, such as an empty list, one-item list, Unicode text, duplicate record, very large value, or leap day. An edge case may also be a boundary case.

A **failure case** is an operation that cannot or must not succeed: insufficient balance, invalid credentials, missing field, unavailable resource, duplicate transaction, or forbidden state transition. Correctly rejecting a failure case is often successful application behavior.

A **regression** occurs when a behavior that previously worked becomes broken after a code, dependency, configuration, schema, or architecture change. A **regression test** preserves protection for that behavior, especially when added in response to a real defect.

Example: `parse_amount(" 100 ")` returned `100` in Version 1, but Version 2 raises `ValueError`. If surrounding whitespace is part of the supported contract, Version 2 introduced a regression.

The basic defect workflow is:

```text
bug discovered
→ reproduce it
→ write a test that fails on the buggy code
→ fix the implementation
→ confirm the test passes
→ keep the test
```

## 3. Why happy-path-only testing is insufficient

A happy-path test proves that one normal valid scenario works. For a withdrawal operation, `withdraw(500, 100) == 400` is useful, but it says nothing about withdrawing exactly the balance, one unit more than the balance, zero, a negative amount, a wrong type, `None`, an inactive account, or an extremely large amount.

The source example:

```python
def withdraw(balance: int, amount: int) -> int:
    if amount <= 0:
        raise ValueError("amount must be positive")
    if amount > balance:
        raise ValueError("insufficient balance")
    return balance - amount
```

The first condition rejects zero and negative amounts. The second rejects amounts greater than the balance. Only then is the remaining balance returned. A complete test design includes ordinary success, important boundaries, invalid types and values, and relevant failure modes.

Real systems contain limits such as transaction amount, balance, rate limit, payload size, batch size, page size, retry count, timeout, and token budget. These are natural places to derive tests.

## 4. Valid domains, invalid domains, and contracts

A **domain** is the set of inputs a function or system is designed to accept. Examples from the lesson:

- Age: valid `18–65`; invalid below 18, above 65, wrong type, missing, or `None`.
- Quantity: valid `1–100`; invalid `<= 0`, `> 100`, wrong type, `None`, or missing.
- Username: valid length `3–20`; possible invalid cases include 2 or 21 characters, empty, missing, `None`, or unsupported characters.
- Percentage: valid `0–100` inclusive; invalid below 0, above 100, wrong type, or `None`.

The example `is_valid_percentage(value)` returns `0 <= value <= 100`. A parametrized pytest table checks `0, 1, 50, 99, 100` as valid and `-1, 101` as invalid.

Do not assume that an unusual value is invalid. Zero may be valid; an empty collection may be valid; `False` may be a legitimate setting. Ask:

1. What is explicitly allowed?
2. What is explicitly forbidden?
3. What is unspecified?

Unspecified behavior should be clarified or treated according to the existing documented contract—not invented.

## 5. Happy-path and negative testing

A **happy path** is valid input processed normally to the expected result. The `add(2, 3)` example uses AAA:

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

The test sets up two values, calls the function, and checks the exact expected result. `assert result` would be weak because any truthy result could pass.

**Negative testing** deliberately supplies invalid, unexpected, malformed, or prohibited inputs and verifies the correct rejection or handling. Examples include invalid amount, wrong type, missing field, malformed date, unauthorized request, invalid state transition, and duplicate operation.

Crucial distinction: a negative test should usually **pass** when the application correctly rejects invalid input.

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

`pytest.raises` tells pytest that `ValueError` is expected. The test passes when that exception is raised. In the source, `parse_age()` calls `.isdigit()` without checking the input type first; a float could therefore raise an accidental `AttributeError`. A deliberate wrong-type contract needs explicit type validation.

Negative cases include:
- invalid values, e.g. withdrawal `-1`;
- wrong types, e.g. a float passed to a string parser;
- missing required fields;
- malformed strings such as an invalid date;
- unauthorized actions;
- impossible state transitions, such as `DELIVERED → PAID`.

Avoid three mistakes: writing an invalid-input test without asserting the expected outcome; accepting any `Exception` when the contract specifies `ValueError` or `TypeError`; and checking only the exception while ignoring state that must remain unchanged.

## 6. Boundaries and Boundary Value Analysis (BVA)

A boundary is a limit where classification or behavior changes. For `1 <= quantity <= 100`, the useful neighborhood is:

```text
0   just outside minimum
1   minimum
2   just inside minimum
99  just inside maximum
100 maximum
101 just outside maximum
```

Boundary defects often arise from `>` instead of `>=`, `<` instead of `<=`, off-by-one arithmetic, slicing, pagination, loop termination, or confusion between inclusive and exclusive limits.

**Boundary Value Analysis (BVA)** systematically selects values around limits. The classic pattern is:

`minimum−1, minimum, minimum+1, maximum−1, maximum, maximum+1`.

The source's pytest example uses `@pytest.mark.parametrize` to pair each quantity with its expected Boolean result. Explicit IDs such as `below-minimum`, `minimum`, `just-above-minimum`, `just-below-maximum`, `maximum`, and `above-maximum` make failures easier to diagnose.

Testing only the exact minimum and maximum misses defects immediately outside the valid range.

## 7. Boundaries are not only numeric

A boundary is defined by a change in required behavior, not by the data type.

- **Numeric:** temperature `-20–50`; test `-21, -20, -19, 49, 50, 51`.
- **String length:** username `3–20` characters; test lengths `2, 3, 4, 19, 20, 21`.
- **Collection size:** maximum 10 records; test `0, 1, 9, 10, 11`.
- **Date/time:** just before, exactly at, and just after expiry, midnight, billing period, timeout, month/year transition, leap day, or daylight-saving transition where applicable.
- **File size:** values around the application's configured maximum (the lesson's example is 5 MB).
- **Pagination:** page size `1–100`; test `0, 1, 2, 99, 100, 101`.
- **Rate limit:** if the application defines 100 requests per minute, use controlled test infrastructure near that threshold; do not run uncontrolled load against production.
- **Database:** maximum string length, numeric precision, `NULL`, uniqueness, foreign-key existence, and batch-size constraints.
- **Resources:** file size, timeout, queue capacity, connection-pool size, memory budget, batch size, and retry count.
- **Business rules:** transaction limit, credit-score threshold, eligibility age, or discount threshold.

The contract must define the semantics. For example, “three retries” may mean three retries after the first attempt or three total attempts.

## 8. String and collection boundaries

For a username length of `3–20`, BVA values have lengths `2, 3, 4, 19, 20, 21`. The source implements this with `3 <= len(value) <= 20` and parametrizes strings such as `"ab"`, `"abc"`, `"abcd"`, `"a" * 19`, `"a" * 20`, and `"a" * 21`.

Length validity is not format validity. A string of valid length can still contain unsupported characters, whitespace, reserved names, or Unicode normalization issues. The contract should define whether length means characters, bytes, code points, or another representation. `"abc"` and three emoji can have different byte lengths and practical implications.

For a batch with a maximum of 10 records, test sizes `0, 1, 9, 10, 11`. Zero may be valid, invalid, or a special case—never assume. One item may exercise a different code path from an empty list. Duplicates matter because `[1, 1, 1]` has length 3 but only one unique value. The lesson's `is_valid_batch(records)` returns `len(records) <= 10`; `list(range(size))` creates the requested number of records.

These collection cases matter in ETL batches, bulk APIs, queues, database inserts, ML batches, vector retrieval, and agent tool arguments.

## 9. Date and time boundaries

Time boundaries include start/end of day, expiry, timeout, subscription renewal, billing period, month/year transitions, leap day, and daylight-saving changes.

Prefer passing an explicit timestamp to a function rather than depending on the real current time or using `sleep()`:

```python
from datetime import datetime, timezone

def is_expired(deadline: datetime, now: datetime) -> bool:
    return now >= deadline
```

The source tests the exact deadline as expired and one second before it as not expired. This makes the inclusive rule explicit. Avoid `datetime.now()` in deterministic unit assertions, sleeping to reach a boundary, ignoring time zones, or assuming undocumented end-of-day semantics. Distributed systems must define UTC vs business timezone, inclusive vs exclusive, and instant vs calendar date.

## 10. API, database, and resource boundaries

For an API `page_size` of `1–100`, test `0, 1, 2, 99, 100, 101`. The conceptual API test sends `GET /items` with `page_size` and checks the expected status (400 for invalid values and 200 for valid values). Depending on the API contract, also verify response schema, error code/body, and side effects. Do not assert incidental formatting.

For databases, distinguish the application contract from implementation details. “Application rejects a username longer than 20 characters” is different from “database column is `VARCHAR(20)`.” Both may matter, but test them at the appropriate layer. Database constraints remain useful safety nets even when application validation exists.

For resource limits, test the actual configured limit. Clarify retry semantics before testing retry counts. Do not test arbitrary numbers without understanding what they mean.

## 11. Equivalence partitioning and combining it with BVA

**Equivalence partitioning** divides a large input space into classes expected to behave similarly. For age rules `<18 → reject`, `18–65 → accept`, and `>65 → reject`, representatives might be `17, 30, 66`. It avoids attempting every possible value.

**BVA** asks what happens around transitions; **equivalence partitioning** asks which groups should behave alike.

For age `18–65`:
- partitions: `<18`, `18–65`, `>65`;
- representative values: `17, 30, 66`;
- boundary neighborhood: `17, 18, 19, 64, 65, 66`.

Use partitioning to reduce the broad domain, then give extra attention to high-risk boundaries. Without partitioning, the suite can become huge; without BVA, off-by-one defects may be missed.

## 12. A taxonomy of invalid inputs

Invalid input is not one homogeneous category. The lesson identifies:

1. invalid value (`percentage=150`);
2. invalid type (`age="30"` when integer is required);
3. missing value (required `email` key absent);
4. empty value (`name=""`);
5. explicit `None`;
6. malformed format (`"2026-99-99"`);
7. unsupported value (`currency="XYZ"`);
8. duplicate value (repeated transaction ID);
9. conflicting values (e.g. `status="PAID"` and `cancelled=True`);
10. unexpected extra fields;
11. invalid encoding;
12. invalid state;
13. unauthorized input;
14. oversized input.

This taxonomy helps prevent a test suite from repeatedly checking one simple invalid case while overlooking qualitatively different failure modes.

## 13. Invalid types and Python's `bool` detail

The source's `validate_age(age)` raises `TypeError("age must be an integer")` when `not isinstance(age, int)`. Test valid integer values and wrong types such as string, float, `None`, list, dictionary, and `object()`.

Important Python detail: `bool` is a subclass of `int`, so `isinstance(True, int)` is `True`. If booleans are not valid integer inputs, use:

```python
isinstance(value, int) and not isinstance(value, bool)
```

and test both `True` and `False`.

Type validation and value validation are different. `25` may be the correct type but outside a required age range. `"25"` may represent a meaningful number but violate an API contract that requires an integer. “Convertible” does not automatically mean “valid.”

## 14. Missing, empty, `None`, zero, and `False`

These are distinct states:

- **Missing:** the key does not exist, e.g. `{}`.
- **Empty:** the key exists with an empty value, e.g. `{"username": ""}`.
- **None:** the key exists with an explicit no-value marker, e.g. `{"username": None}`.
- **Zero:** a numeric value, e.g. `quantity = 0`.
- **False:** a Boolean value, e.g. `enabled = False`.

The lesson's `validate_quantity()` gives `None` the error “quantity is required,” zero the error “quantity must be positive,” and otherwise returns the value. Avoid using `if not value` unless the contract truly intends to combine `0`, `False`, `""`, `[]`, `{}`, and `None`.

## 15. Malformed input and exception testing

Malformed input violates a format or structural expectation: invalid email, JSON, CSV, UUID, URL, date, or corrupted file. The source's `parse_date()` calls `datetime.strptime(value, "%Y-%m-%d")`; tests pass malformed values such as `"2026-99-99"`, `"not-a-date"`, and `"2026/01/01"` and expect `ValueError`.

A useful failure test asks:
- which exception type is part of the contract?
- is the message stable and meaningful enough to assert?
- should state remain unchanged after the failure?
- for APIs, what status, error code, and error schema are required?

`pytest.raises(ValueError)` verifies the type. `match=` checks a meaningful stable part of the message and uses regular-expression matching. Exact full-message equality can be brittle unless the exact wording is contractually promised. A specific exception is safer than `pytest.raises(Exception)`, which could accidentally accept an unrelated `AttributeError`.

## 16. Parametrized boundary and invalid tests

`@pytest.mark.parametrize` runs the same test function with several input cases. A table such as `(age, expected_valid)` makes the requirement visible. `pytest.param(..., id="below-minimum")` provides a readable case name in failure output.

Parametrization is useful when the behavior, setup, and assertion structure are the same and only the scenario changes. Use separate tests when cases have different setup, different expected exception types, different side effects, or substantially different meanings. A giant parameter matrix can hide unrelated behavior.

For invalid cases, a table can include `("abc", ValueError)` and `(None, TypeError)` if the contract deliberately defines different exception types. Separate tests may be clearer when the failure semantics differ significantly.

## 17. Edge cases, failure modes, and error contracts

A **boundary case** is directly tied to a defined limit. An **edge case** is unusual or extreme but need not be a formal limit. The maximum list size can be both. Classification is less important than asking whether the scenario could reveal meaningful incorrect behavior.

A **failure mode** is a way the system can fail: invalid amount, insufficient balance, inactive account, duplicate request, unknown account, timeout, database unavailable, or permission failure. Convert important failure modes into observable tests.

For a transfer requiring an active account and sufficient balance, test inactive account, insufficient balance, invalid amount, and unknown account. A failed payment may also need to leave the order unpaid, avoid duplicate payment records, preserve inventory, keep retry state correct, and return the correct failure contract.

Error messages matter exactly only when an API specification, stable CLI output, automation, or documentation promises exact wording. Otherwise assert the exception type or a stable semantic fragment. Error type often communicates the failure category more reliably than incidental wording.

## 18. Regression testing and writing the test first

Regression testing verifies that changes do not break behavior that should continue working. A regression may follow refactoring, database migration, a new feature, dependency upgrade, performance optimization, caching, concurrency change, or architecture migration.

A bug-driven workflow is:

```text
bug discovered
→ understand requirement
→ reproduce bug
→ write failing test
→ confirm failure
→ fix production code
→ run regression test
→ run related tests
→ keep regression test
```

Why test first? If the new test fails on the buggy implementation, it demonstrates that the test detects the actual defect. Fixing code first and writing a test that already passes may still add value, but it does not prove the original bug was reproduced.

Source example: a bank transfer accepts a negative amount because the implementation checks only `amount > sender.balance`. A test expects `ValueError("amount must be positive")` for `-1`. Before the fix, no exception is raised and balances can change in the wrong direction (sender 500 becomes 501; receiver 100 becomes 99). Add `if amount <= 0: raise ValueError(...)` before the insufficient-balance check.

A stronger test checks both the expected exception and unchanged balances. This protects the invariant: **rejected transaction → no balance mutation**.

A regression test must reproduce the exact reported bug. If `" 100 "` is rejected, testing only `"100"` does not reproduce it. Ask: “Would this exact defect cause this test to fail if it returned?”

## 19. Regression tests, refactoring, and new features

Refactoring should change implementation without unintentionally changing behavior. A test should assert the public behavior, not an internal technique. For example, if normalization changes from `.lower()` to `.casefold()`, contract-level tests should verify the intended output. A test that checks whether a private `_used_strip` flag was set is coupled to implementation; a test that checks `parser.parse(" 100 ") == 100` protects behavior.

New features can break old behavior. When adding discounts to an order total, keep a regression test for the old no-discount total as well as a new test for the discount threshold. Test old and new behavior.

## 20. Maintaining the regression suite and choosing its level

A regression suite grows with discovered defects, but runtime and maintenance cost grow too. Keep tests that reproduce real defects, protect high-risk contracts, provide unique information, and fail diagnostically. Review apparent duplicates by identifying the behavior protected and the unique failure each test catches. “Invalid input rejected” and “rejected input leaves state unchanged” can be complementary.

Use the lowest practical level that reliably reproduces the defect:
- **Unit:** isolated algorithm or rule.
- **Integration:** interaction between components/services/adapters.
- **API:** externally visible API contract.
- **E2E:** broad critical user workflow when lower levels cannot reproduce it.

This is a heuristic, not an absolute rule. Do not delete an integration test for a cross-service defect merely because unit tests cover each component separately.

## 21. Applying the ideas to production systems

### Unit and API tests
Unit boundary tests should be fast and explicit. API boundaries include page size, payload size, required fields, query length, retries, rate limits, and supported values. Verify status, schema, error code/body, and side effects where those are contractual.

### Data pipelines
Data regressions can appear as dropped rows, changed schema, increased nulls, duplicate changes, or altered aggregates rather than exceptions. A change from 100 output records to 95 may be caused by a filter, join, parser, or null-handling change. Test row count only when row preservation is required; also test schema, null rates, duplicates, business transformations, and invariants.

### ML systems
Separate ordinary software regressions from model performance drift. Software regressions include changed preprocessing, missing/reordered features, output shape changes, or serving schema changes. Model drift/performance changes include accuracy or precision decline and feature distribution shifts; these require evaluation and monitoring, not simply a unit regression test. The source example checks that two input rows produce two predictions.

### AI/LLM applications
Application limits include document length, token budgets, retrieval count, retry count, timeout, and tool-argument size. Test your application's documented limits rather than assuming provider-specific token limits. Prefer stable contracts: JSON/schema, required fields, allowed values, parser behavior, tool calls, retrieval constraints, safety rules, and fallback behavior. Exact natural-language equality may be unsuitable when wording is nondeterministic.

The source classifier example checks that `intent` and `confidence` exist and that confidence is between 0 and 1.

### Agentic AI
Test observable workflow behavior: authorization, balance/policy checks, tool invocation and arguments, state transitions, final structured result, errors, and termination. Example workflow: user request → retrieve balance → validate policy → call transfer tool → return structured result. Verify the balance tool is called before transfer. Do not test hidden reasoning; test observable outputs and safety invariants. Test approval threshold `999, 1000, 1001` for a 1,000-unit limit.

## 22. Test data and readability

Choose test data that is representative, deterministic, minimal, readable, purposeful, and explicit about expected behavior.

- Inline values suit tiny obvious cases.
- Parametrization suits repeated test logic.
- Fixture factories suit realistic objects created repeatedly.
- Named constants make business limits clear, e.g. `MAX_TRANSACTION_AMOUNT = 1_000_000`.
- Structured cases (the source shows a frozen dataclass with `name`, `amount`, and `expected_valid`) help when each case has several fields.

Do not build a complex framework for a simple six-value test. Prefer readable scenario names and meaningful assertions over minimum character count.

## 23. Common mistakes to avoid

The lesson identifies twelve recurring mistakes:
1. Testing only happy paths.
2. Testing only exact boundaries and forgetting neighboring values.
3. Forgetting just-outside values.
4. Treating `None` and empty as identical.
5. Writing an invalid test without an expected exception/result.
6. Using weak assertions such as `result is not None`.
7. Creating enormous parameter tables.
8. Keeping duplicate regression tests without unique value.
9. Writing a regression test that does not reproduce the bug.
10. Asserting fragile full error messages.
11. Confusing software regression with model drift.
12. Treating coverage as proof of correctness.

Coverage shows code was executed; it does not prove the assertion was meaningful.

## 24. Debugging a boundary or regression test failure

For a boundary failure:
1. Read the requirement.
2. Identify the intended minimum/maximum and inclusive/exclusive semantics.
3. Check the selected test values.
4. Compare expected and actual.
5. Inspect the implementation.
6. Decide whether code or test is inconsistent with the requirement.
7. Reproduce the one failing case independently (pytest can select a test node and parameter ID).
8. Fix the underlying cause.
9. Preserve the regression test.
10. Run related tests because a boundary fix can affect neighboring values.

For a regression failure, identify the protected behavior, review recent code/config/dependency changes, reproduce, compare old and current behavior, identify root cause, fix, rerun the regression, then run broader related tests. A failing test is evidence, not proof that production code is wrong.

## 25. Complete realistic example — transaction validation

The source builds `Account` and `Transaction` classes and `validate_transaction()` around these requirements: amount must be an integer, greater than zero, at most 1,000,000; account must exist and be active; balance must be sufficient; transaction ID must not already exist in a caller-owned set.

Important implementation details:
- `MAX_TRANSACTION_AMOUNT` is a named constant.
- `account is None` is rejected.
- Boolean amounts are rejected explicitly because `bool` subclasses `int`.
- Zero/negative amounts and amounts above the maximum are rejected.
- Inactive account, insufficient balance, and duplicate ID are rejected.
- The validator only reads `processed_ids`; the caller owns and updates it after success.

The test strategy covers happy path, minimum/maximum, just-outside values, wrong types, Boolean values, missing account, inactive account, insufficient balance, unique/duplicate transaction ID, and unchanged state after rejection. The example is an in-memory validation example; its set does not provide persistent, concurrent, or distributed idempotency.

The source demonstrates a regression where changing `amount <= 0` to `amount < 0` accidentally accepts zero. The zero-amount test catches it.

## 26. Guided mini-project — transaction validation service

The source mini-project extends the transaction validator into a small service. Requirements include amount range `1–100,000`, rejecting zero/negative/over-limit/non-integer amounts, rejecting inactive accounts, and preserving balances on rejected transfers. It proposes a project structure with application code and tests, then a test strategy split into happy path, boundary, invalid-input, state-invariant, and regression cases.

A fixture creates reusable accounts. Tests cover valid transfer, minimum and maximum, below/above range, wrong type, inactive account, insufficient balance, and state preservation. Further cases include duplicates and a regression for zero being accepted after an incorrect comparison change. The project review asks whether fixtures isolate transaction IDs, parameter IDs are readable, cases are meaningful, assertions precise, and any production defect could still pass.

## 27. Interview and architecture knowledge from the chapter

The source includes 22 interview questions and 10 architecture questions. The core answers are:

- Boundary testing and BVA select values at/around limits; negative testing verifies invalid inputs are handled, and the negative test passes on correct rejection.
- Equivalence partitioning reduces input space; combine it with BVA to focus on transitions.
- `None`, empty, and zero are distinct semantic states.
- Regression tests should reproduce the real bug; not all should be E2E.
- Use risk-based representative cases and separate tests when parametrization hides different behavior.
- Test both expected failure and unchanged state when failure must be side-effect-free.
- Software regression differs from model drift.
- LLM tests should focus on stable schemas, tool use, retrieval, fallbacks, and safety constraints; agent tests should focus on observable workflow invariants.
- For large backends, derive tests from contracts, equivalence classes, boundaries, and failure modes; organize them into fast unit, targeted integration, API, and selected E2E layers.
- For data systems, protect schema, row-count rules, nulls, duplicates, business transformations, and invariants.
- For monorepos, place tests near the protected behavior and classify them for CI.
- Control runtime by avoiding duplication and choosing the smallest reliable test level.

## 28. Production checklist, glossary, and final mental model

Before shipping, verify: happy path; valid/invalid domains; types; missing/empty/`None`; unsupported/malformed values; minimum/maximum; just-inside/just-outside; expected exception and stable error contract; unchanged state after rejection; real bug reproduction; appropriate regression level; isolation; deterministic data; readable IDs; precise assertions; useful CI runtime.

Glossary highlights:
- **BVA:** systematic selection around boundaries.
- **Equivalence partitioning:** grouping inputs expected to behave alike.
- **Invariant:** property that must remain true.
- **Failure contract:** defined rejection/handling behavior.
- **Schema regression:** unexpected data-contract change.
- **Model drift:** change in model/data behavior over time.
- **Test isolation:** preventing shared-state leakage.
- **Representative value:** selected member of an equivalence class.

The final mental model:

```text
requirement
→ valid and invalid domains
→ equivalence classes
→ boundaries
→ just inside / at / just outside
→ meaningful edge cases
→ failure modes
→ expected rejection and state safety
→ bug reproduction
→ failing regression test
→ fix
→ passing regression test
→ retain in CI
```

The chapter's key principle is: **good testing is meaningful scenarios + correct expectations + reliable failures + useful regression protection—not simply more test cases.**

---

# Part B — Project-Tree and Current-Level Assessment

## Roadmap position

This lesson belongs to:

`Stage 1 — Programming & Computational Thinking → Module 07 — Testing and Systematic Debugging → Lesson 04`.

The Module 07 sequence is:

1. Test Levels: Unit, Integration, and End-to-End — completed.
2. Pytest: Assertions, Fixtures, and Parametrization — completed.
3. Arrange–Act–Assert and Test Design — completed.
4. Boundary, Invalid, and Regression Tests — this lesson.
5. Debuggers, Breakpoints, and Call Stacks — not started.
6. Tracebacks, Logging, and Minimal Reproductions — not started.
7. Mocking and Test Doubles — not started.
8. Module README and practice questions.

The wider Stage 1 project tree progresses from computational thinking and Python fundamentals through control flow/functions, collections/algorithms, files/structured data/CLI, modules/packages/dependencies/code quality, and testing. Later modules cover OOP/data modelling, advanced Python, standard library, binary/text processing, modern Python, advanced testing, performance, packaging, internals, design patterns, visualization, security, refactoring/review, and gap lessons.

## Your current level and appropriate scope

Your completed foundation includes Python variables, functions, arguments/returns, conditionals/loops, exceptions and validation, lists/dictionaries/sets, problem-solving, files, pathlib, CSV/JSON, encoding, CLI, streams/exit codes, logging, environment configuration, imports/packages, `pyproject.toml`/`uv`, dependency management, Ruff, type hints, documentation, and the first three Module 07 lessons.

You are a beginner progressing toward intermediate Python engineering. This lesson appropriately builds on pytest assertions, `pytest.raises`, fixtures, parametrization, and AAA already covered. The solutions below use those concepts and ordinary Python functions/classes/collections. They do not introduce new testing frameworks or jump ahead to the debugger and mocking lessons.

**Learning status:** Lesson 04 is covered by this guide; Lesson 05 is not started. Do not advance until you request it.

---

# Part C — All 25 Coding Exercises with Step-by-Step Explanations

The explanations below follow the source's exercise order. For compactness, repeated pytest syntax is explained when first used and then the case-specific lines are explained.

## Level 1 — Basic

### Exercise 1 — Classify values

Requirement: age `18–65` inclusive.

```text
17 → invalid; below minimum
18 → valid; minimum
19 → valid; just inside minimum
64 → valid; just inside maximum
65 → valid; maximum
66 → invalid; above maximum
```

**Why:** the six values are minimum−1, minimum, minimum+1, maximum−1, maximum, maximum+1. Testing only 18 and 65 misses off-by-one defects.

### Exercise 2 — Happy-path test

```python
def test_add_returns_sum():
    a = 2
    b = 3
    result = add(a, b)
    assert result == 5
```

- `a` and `b` arrange the input.
- `add(a, b)` performs the action.
- `result` stores the returned value.
- `assert result == 5` checks the exact contract.

### Exercise 3 — Negative test

```python
import pytest

def test_parse_age_rejects_string():
    with pytest.raises(TypeError, match="age must be an integer"):
        parse_age("30")
```

- Import pytest to use its exception assertion.
- The test name states the scenario.
- `pytest.raises` expects a `TypeError`.
- `match` checks the meaningful message fragment.
- `"30"` is deliberately a string, not an integer.
- The test passes when the function rejects it correctly.

### Exercise 4 — Choose boundary values

For quantity `1–100`, use `0, 1, 2, 99, 100, 101`. These cover outside, exact limit, and inside on both ends.

### Exercise 5 — Identify edge cases

For a list of records, test: empty list, one-item list, duplicate records, very large list, and missing/`None` list. Each probes a different assumption about collection contents or shape.

## Level 2 — Intermediate

### Exercise 6 — Parametrize boundaries

```python
import pytest

@pytest.mark.parametrize(
    "score,expected",
    [(-1, False), (0, True), (1, True),
     (99, True), (100, True), (101, False)],
)
def test_score_boundaries(score, expected):
    assert is_valid_score(score) is expected
```

- `parametrize` declares two arguments per case.
- Each tuple supplies a score and its expected result.
- The function runs once per tuple.
- `is_valid_score(score)` invokes the application rule.
- `is expected` checks the Boolean result exactly.

### Exercise 7 — Test missing and `None` separately

```python
def test_username_missing_from_payload_is_rejected():
    with pytest.raises(ValueError, match="username is missing"):
        validate_username({})

def test_username_none_is_rejected():
    with pytest.raises(ValueError, match="username is required"):
        validate_username({"username": None})
```

- `{}` means the key is absent.
- `{"username": None}` means the key exists with an explicit `None`.
- Separate tests assert the two different error contracts.
- Do not combine them using `if not value`.

### Exercise 8 — Malformed date

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

- One parameter is declared: `value`.
- Each `pytest.param` supplies one input and a readable ID.
- The function receives each string in turn.
- `pytest.raises(ValueError)` checks the parser's expected rejection.

### Exercise 9 — Combine BVA and equivalence classes

For `0 < weight <= 20`:

```text
<=0 invalid | 1–20 valid | >20 invalid
Boundary set: 0, 1, 2, 19, 20, 21
```

Partitioning identifies broad behavior groups; BVA adds focused checks around transitions. A typical value such as 10 alone is insufficient.

### Exercise 10 — Detect a weak regression test

Bug: `" 100 "` stopped being accepted. This is weak:

```python
def test_amount_is_integer():
    assert parse_amount("100") == 100
```

It tests clean input, not the reported whitespace bug. Use:

```python
def test_parse_amount_accepts_surrounding_whitespace():
    assert parse_amount(" 100 ") == 100
```

The input now reproduces the exact defect.

## Level 3 — Advanced

### Exercise 11 — Boundary with expected exceptions

```python
import pytest

@pytest.mark.parametrize(
    "amount",
    [pytest.param(0, id="below-minimum"),
     pytest.param(101, id="above-maximum")],
)
def test_amount_boundaries_are_rejected(amount):
    with pytest.raises(ValueError):
        validate_amount(amount)

@pytest.mark.parametrize(
    "amount",
    [pytest.param(1, id="minimum"),
     pytest.param(100, id="maximum")],
)
def test_boundary_amounts_are_accepted(amount):
    assert validate_amount(amount) == amount
```

- The first table contains invalid values and expects `ValueError`.
- The second table contains valid exact boundaries.
- Separate functions make acceptance and rejection semantics clear.
- The equality assertion verifies the accepted value is returned unchanged.

### Exercise 12 — Preserve state after invalid input

```python
def test_rejected_transfer_does_not_change_balances():
    sender = Account("A", balance=500)
    receiver = Account("B", balance=100)

    with pytest.raises(ValueError, match="insufficient balance"):
        transfer(sender, receiver, 501)

    assert sender.balance == 500
    assert receiver.balance == 100
```

- Create independent sender and receiver objects.
- Attempt to transfer 501 when only 500 is available.
- Assert the expected exception.
- Then assert both original balances remain unchanged.
- This tests the failure contract and the state invariant.

### Exercise 13 — API boundary matrix

| Scenario | Input | Expected |
|---|---:|---|
| Below minimum | 0 | 400 |
| Minimum | 1 | 200 |
| Just inside | 2 | 200 |
| Just below maximum | 99 | 200 |
| Maximum | 100 | 200 |
| Above maximum | 101 | 400 |
| Missing | omitted | Contract-specific error |
| Malformed | `"abc"` | Contract-specific error |

The matrix makes the API contract reviewable. Do not invent status codes for missing/malformed values if the specification does not define them.

### Exercise 14 — Choose regression level

If a defect appears because a service sends the wrong type to a database adapter, use an integration regression test if the service-adapter interaction is needed to reproduce it. Add a unit test for independently meaningful validation, but do not pretend that it replaces the integration reproduction.

### Exercise 15 — Regression after refactoring

If output order is contractual:

```python
def test_transform_preserves_required_order():
    result = transform([3, 1, 2])
    assert result == [3, 1, 2]
```

If order is not contractual:

```python
def test_transform_contains_expected_records():
    result = transform([3, 1, 2])
    assert sorted(result) == [1, 2, 3]
```

The function call obtains the transformed result. The assertion must encode the documented contract, not an incidental implementation order.

## Level 4 — Production-oriented

### Exercise 16 — Data-pipeline amount boundary

```python
import pytest

@pytest.mark.parametrize(
    "value,expected_valid",
    [(-1, False), (0, True), (1, True),
     (999_999, True), (1_000_000, True), (1_000_001, False)],
)
def test_transaction_amount_boundaries(value, expected_valid):
    assert validate_amount(value) is expected_valid

@pytest.mark.parametrize("value", [None, "100"])
def test_transaction_amount_rejects_wrong_input_types(value):
    with pytest.raises(TypeError):
        validate_amount(value)
```

- First table checks the numeric domain `0–1,000,000`.
- Each row supplies a value and expected Boolean.
- The second table separates wrong types from numeric range failures.
- `TypeError` is the stated contract for `None` and string input.

### Exercise 17 — LLM document-size limit

```python
import pytest

@pytest.mark.parametrize(
    "size,expected",
    [(49_999, True), (50_000, True), (50_001, False)],
)
def test_document_size_limit(size, expected):
    document = "a" * size
    assert validate_document(document) is expected
```

- Test just inside, exactly at, and just outside the application's 50,000-character limit.
- `"a" * size` constructs a string of the required length.
- The assertion checks the validator's Boolean contract.
- Use the application's configured limit, not an assumed provider token limit.

### Exercise 18 — Agent transaction approval boundary

```python
import pytest

@pytest.mark.parametrize(
    "amount,requires_approval",
    [(999, False), (1000, False), (1001, True)],
)
def test_transfer_approval_boundary(agent, amount, requires_approval):
    result = agent.evaluate_transfer(amount)
    assert result["requires_approval"] is requires_approval
```

- The fixture supplies the application agent.
- Each amount represents below, at, and above the threshold.
- `evaluate_transfer` returns a mapping.
- The assertion checks the observable approval decision, not nondeterministic model wording.

### Exercise 19 — Cross-service regression strategy

1. Reproduce the defect at the service A/service B integration boundary.
2. Add an integration test that reliably reproduces the interaction.
3. Add unit tests for independent rules where useful.
4. Keep the integration test because it captures the actual cross-service defect.
5. Add API/E2E coverage only if it protects additional externally visible behavior.

Do not delete the integration test merely because isolated unit tests exist.

### Exercise 20 — Review apparently redundant regression tests

For each candidate:

```text
identify protected behavior
→ identify unique defect caught
→ compare with other tests
→ remove only if unique protection remains elsewhere
→ run suite
→ inspect diagnostics
```

The decision is evidence-based; reducing test count is not the goal.

### Exercise 21 — Representative values for age 0–120

Use `-1, 0, 1, 119, 120, 121`, plus one interior representative such as `60`. Add wrong-type/format cases as appropriate. Do not invent an age-18 business threshold when the given contract says 0–120.

### Exercise 22 — Find the hidden payment failure mode

Beyond expecting an exception, verify required invariants such as:
- order remains unpaid;
- payment record is not duplicated;
- inventory is not reduced;
- retry state is correct;
- client receives the defined failure response.

Only assert behaviors required by the contract. An exception alone does not prove rollback.

### Exercise 23 — ETL schema regression

```python
def test_output_schema_contains_required_columns():
    result = transform(input_rows())
    assert set(result.columns) == {"id", "amount", "currency"}
```

- Run the transform on known input rows.
- Read the output column names.
- Compare the set with the required schema.
- This catches removal of `currency`; row count alone would not.

### Exercise 24 — Parser whitespace regression

```python
import pytest

@pytest.mark.parametrize(
    "value,expected",
    [("100", 100), (" 100", 100), ("100 ", 100), (" 100 ", 100)],
)
def test_parse_amount_accepts_whitespace(value, expected):
    assert parse_amount(value) == expected
```

The table covers clean input, leading whitespace, trailing whitespace, and both. Each case is parsed and compared with the expected integer. It preserves the historical whitespace behavior.

### Exercise 25 — Regression plus transaction boundary

```python
import pytest

@pytest.mark.parametrize(
    "amount,expected_valid",
    [(999, True), (1000, True), (1001, False)],
)
def test_transaction_limit_boundary(amount, expected_valid):
    assert is_valid_transaction_amount(amount) is expected_valid
```

- Declare amount and expected validity.
- Test immediately below, exactly at, and above the 1,000 limit.
- The table both reproduces the discovered threshold behavior and protects adjacent boundary semantics.

---

# Part D — All 10 Debugging Labs

1. **Off-by-one age:** `18 < age < 65` wrongly rejects 18 and 65. Use `18 <= age <= 65`.
2. **Maximum amount:** `1 <= amount < 1000` rejects 1000 even though the maximum is inclusive. Use `<= 1000`.
3. **Zero quantity accepted:** `quantity < 0` lets zero through when quantity must be positive. Use `quantity <= 0` and retain a test expecting `ValueError`.
4. **Valid page-size boundaries rejected:** `1 < size < 100` excludes 1 and 100. Use `1 <= size <= 100`.
5. **`None` treated as valid:** `if not name: return True` conflates empty and `None`. Explicitly reject `None` if the contract says name is required.
6. **Empty batch crashes:** indexing `records[0]` raises `IndexError` for an empty list. Handle empty input according to the contract (return a documented value or raise a domain exception).
7. **Wrong expected exception:** the test expects `TypeError`, but malformed string format is contractually `ValueError`. Fix the test to assert `ValueError`.
8. **Whitespace regression:** a refactor rejects `" 100 "` despite historical support. Keep a behavior test that parses it to 100.
9. **Implementation-detail test:** checking private `_used_strip` couples the test to implementation. Assert `parser.parse(" 100 ") == 100` instead.
10. **Wrong test expectation:** a test says 1000 is invalid, but the requirement says maximum 1000 inclusive. Correct the expectation; a failing test does not automatically mean production code is wrong.

Debugging rule: compare both test and implementation against the requirement before changing either.

---

# Part E — Knowledge Check Answers

1. For quantity 1–100: `0` invalid; `1` valid minimum; `2` valid just inside; `99` valid just inside maximum; `100` valid maximum; `101` invalid.
2. `assert result is not None` is weak because it does not prove correctness; assert the expected value (e.g. `20`) when that is the contract.
3. The negative test passes when `ValueError` is correctly raised inside `pytest.raises`.
4. `17` is immediately below the minimum age and catches incorrect acceptance below 18.
5. Representative classes: `50` valid, `-1` invalid below, `101` invalid above; add BVA around 0 and 100.
6. `parse_amount(" 100 ") == 100` is stronger because it reproduces the whitespace bug.
7. `ValueError` is better than broad `Exception` because it rejects unrelated implementation defects.
8. No: if rejection must preserve state, assert the sender balance is unchanged as well as the exception.
9. Use an integration regression test when incompatible schemas between services cause the bug.
10. Exact LLM text can vary; assert stable schema, labels, invariants, tool calls, and safety constraints.
11. Verify observable authorization, checks, tool calls/arguments, state transitions, final result, and termination.
12. A regression test may be removed only when evidence shows another test provides equivalent or better protection and no unique information is lost.

---

# Part F — Interview and Architecture Review

## 22 interview questions — concise model answers

1. **Boundary testing:** test values at and around behavior limits.
2. **BVA:** systematically test min−1, min, min+1, max−1, max, max+1.
3. **Negative testing:** supply invalid/prohibited inputs and verify correct handling.
4. **Should a negative test fail?** No; correct rejection makes it pass.
5. **Invalid input:** violates the defined contract.
6. **Edge case:** unusual/extreme scenario, sometimes overlapping a boundary.
7. **Regression:** previously working behavior breaks after a change.
8. **Regression test:** protects established behavior, especially a discovered bug.
9. **Why neighbors?** Catch off-by-one and comparison defects.
10. **Equivalence partitioning:** group inputs expected to behave alike.
11. **BVA + partitioning:** partition the domain, then focus on transition points.
12. **Why distinguish None/empty/zero?** They have different meanings and may have different rules.
13. **Why reproduce bug?** Proves the test detects the exact defect.
14. **Every regression E2E?** No; use lowest reliable reproducing level.
15. **Weak assertions?** They allow incorrect behavior to pass.
16. **Avoid huge suites?** Use partitions, boundaries, risk, and representative combinations.
17. **Separate tests vs parametrization?** Separate when setup, behavior, or assertions differ materially.
18. **Test failure without mutation?** Assert exception and state invariants.
19. **Software regression vs model drift?** Code contract break vs changing model/data quality.
20. **LLM regression?** Stable schemas, tool calls, retrieval, fallback, safety—not brittle exact prose.
21. **Agent regression?** Observable tool calls, arguments, authorization, state, termination, and result.
22. **Valuable regression test?** Unique, meaningful, reproducible, diagnostic protection.

## 10 architecture questions — core approach

1. Derive backend tests from domain contracts, partitions, boundaries, failure modes, and risk.
2. Manage large case sets with parametrization, structured data, representative values, and split behavior groups.
3. Use inline/parametrized cases for small tables and structured case objects for complex cases.
4. In a monorepo, organize fast local tests → service tests → integration → API → selected E2E.
5. Choose the smallest level that reliably reproduces the defect without losing the relevant interaction.
6. For pipelines, test schema, row-count rules, nulls, duplicates, transformations, and invariants.
7. Schema tests should verify required names/types/nullability/semantics without over-constraining intended evolution.
8. For nondeterministic LLMs, separate deterministic application contract tests from model-quality evaluation.
9. For agents, test stable observable workflow invariants and control external tools/state.
10. Control suite runtime with test-level selection, isolation, reduced duplication, and useful CI tiers.

---

# Part G — Completion Checklist

- [x] Valid vs invalid input and contract-driven classification.
- [x] Happy path and negative testing.
- [x] Boundary definition and BVA.
- [x] Numeric, string, collection, date/time, API, database, and resource boundaries.
- [x] Equivalence partitioning and combination with BVA.
- [x] Invalid value/type/missing/empty/None/malformed/unsupported/duplicate/conflicting/oversized inputs.
- [x] Python Boolean-as-integer nuance.
- [x] Exception type and message testing.
- [x] Parametrization and readable IDs.
- [x] Edge cases and failure-mode thinking.
- [x] Regression workflow, test-first reproduction, and state safety.
- [x] Regression test placement and suite maintenance.
- [x] Data pipeline, ML, LLM, and agentic AI applications.
- [x] Test data design, readability, common mistakes, and debugging workflows.
- [x] Realistic transaction example and guided mini-project.
- [x] All 25 coding exercises, 10 debugging labs, 22 interview questions, 10 architecture questions, and 12 knowledge checks.

**Lesson status:** Module 07, Lesson 04 covered. Lesson 05 remains untouched until you request it.
