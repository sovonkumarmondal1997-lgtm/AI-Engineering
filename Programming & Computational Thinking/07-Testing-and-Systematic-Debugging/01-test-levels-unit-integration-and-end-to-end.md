# Test Levels: Unit, Integration, and End-to-End

## Learning Objectives

By the end of this chapter you will be able to:

- Explain what software testing is, what a test case actually consists
  of, and why testing exists as a discrete engineering discipline
  rather than an afterthought.
- Distinguish testing from debugging precisely, and explain how the two
  activities work together rather than substitute for each other.
- Write assertions in plain Python and with `pytest`, and distinguish a
  strong, meaningful assertion from a weak one.
- Explain what a "unit" is, why its exact boundary is a judgment call
  rather than a fixed rule, and write isolated, fast, deterministic
  unit tests for pure and impure code alike.
- Explain mocks, fakes, and stubs at a conceptual level sufficient to
  use them correctly in unit tests, and recognize when mocking has gone
  too far.
- Explain what integration testing verifies, identify integration
  boundaries (database, filesystem, API, external service), and write
  integration tests that exercise real interactions rather than
  simulated ones.
- Explain what end-to-end testing verifies, and why it should focus on
  critical workflows rather than exhaustively duplicating unit-level
  coverage.
- Compare unit, integration, and end-to-end tests directly — scope,
  speed, isolation, realism, infrastructure, and failure diagnosis —
  and apply the same feature across all three levels correctly.
- Explain the test pyramid as a heuristic, not a law, and reason about
  when a project's architecture justifies a different distribution.
- Organize a test suite (`tests/unit/`, `tests/integration/`,
  `tests/e2e/`), name tests to communicate behavior, and use `pytest`
  fixtures for reusable setup.
- Explain test determinism, flaky tests, and test isolation, and apply
  practical strategies to prevent tests from interfering with each
  other or with themselves across runs.
- Explain regression testing, test coverage's real meaning and limits,
  and the difference between testing behavior and testing
  implementation details.
- Design a CI test strategy that runs Ruff, type checking, and layered
  test suites in a sensible order, and reason about test execution
  strategy for pull requests versus full/nightly runs.
- Apply test-level thinking to backend services, data pipelines, ML
  systems, and AI/agentic systems — including the distinction between
  testing software behavior and evaluating model quality, and between
  deterministic and nondeterministic system boundaries.

## Prerequisites

This chapter builds on this course's earlier Programming &
Computational Thinking modules — functions, modules, packages, project
structure, CLI programs (`main(argv) -> int`), file handling, JSON,
configuration, dependency management with `uv`, Ruff, type hints, and
documentation are all assumed knowledge here, reused rather than
re-taught. Where relevant, this chapter shows how testing interacts
with each of those, rather than repeating what they are.

## 1. What Is Software Testing?

**What is software testing?** Software testing is the practice of
running a piece of code deliberately, with known inputs, and checking
whether what actually happens matches what you expect to happen. A
**test** is one specific, repeatable procedure that does exactly this —
run some code, observe the result, compare it against an expectation —
and records whether that comparison succeeded or failed.

Start from the simplest possible example:

```python
def add(a, b):
    return a + b
```

To test this function, you need four things, in order:

```
give input               →   a = 2, b = 3
        ↓
execute behavior           →   result = add(a, b)
        ↓
observe result                →   result is now 5
        ↓
compare with expectation         →   is result == 5 ?
```

If the comparison holds, the test **passes** — the code's **actual
behavior** matched its **expected behavior** for this specific input.
If it doesn't, the test **fails** — actual and expected diverged, which
is exactly the signal that something is wrong, either in the code or in
the expectation itself.

A test **failure** is not the same thing as a test **error**:

```
TEST FAILURE  →  the test ran, and the expected behavior was not satisfied
TEST ERROR    →  the test could not complete normally — a setup, collection,
                 fixture, import, or environment problem (or another
                 unexpected exception) prevented the intended check
```

**What is a test case?** A **test case** is one concrete instance of
this whole procedure — one specific set of inputs, one specific
expected result, and the logic that checks the two match. `add(2, 3) ==
5` is a test case for `add`; `add(-1, 1) == 0` is a *different* test
case for the exact same function, checking a different input.
**Expected behavior** is what you, the author (or the specification),
believe the code *should* do; **actual behavior** is what the code
*actually* does when it runs. A **passing test** is one where these
match; a **test failure** is one where they don't.

**Why do software systems need tests at all?** Because without running
this input → execute → observe → compare procedure deliberately and
repeatedly, the only way to know whether `add` genuinely computes a sum
correctly is to trust that it does — and trust, alone, doesn't scale
past a trivial program, doesn't survive a future change to the code,
and gives no early warning when something breaks. §2 develops this
motivation in full; this section's job is only to establish, precisely,
what a test *is* before asking why it matters.

## 2. Why Test Software?

Testing exists to serve several distinct, concrete engineering goals —
not "quality" as a vague abstraction, but specific, nameable problems it
solves.

- **Correctness** — a test gives you direct, repeatable evidence that a
  piece of code does what it's supposed to do for the inputs you've
  actually checked, rather than relying on a one-time manual check or
  intuition.
- **Regression prevention** — once a test exists and passes, running it
  again after a later change immediately reveals if that change broke
  something the test covers. A **regression** is exactly this: behavior
  that used to be correct becoming incorrect again, usually as a side
  effect of an unrelated change.
- **Refactoring safety** — a suite of passing tests lets you restructure
  *how* code is written (its implementation) with confidence that its
  observable *behavior* hasn't changed, because the tests would fail if
  it had (§56 develops this distinction in full).
- **Maintainability** — tests make it safe for someone other than the
  original author (including the original author, months later) to
  change code without having to manually re-verify every existing
  behavior by hand.
- **Confidence** — a passing suite is concrete evidence a change is
  safe to ship, replacing "I'm fairly sure this works" with "here is
  what was actually checked, and it passed."
- **Documentation of behavior** — a well-named, well-written test
  states, unambiguously and in executable form, what a piece of code is
  actually supposed to do — often more precisely and more durably than
  a comment, since a comment can silently go stale while a wrong test
  fails loudly.
- **Collaboration** — tests let a team change shared code without each
  person needing to personally understand and re-verify every other
  part of the system a change might have touched.
- **Release safety** — a project with a meaningful test suite can gate
  a release on "do the tests still pass," converting release confidence
  from a guess into a checked fact.

**A concrete regression example**, showing exactly what these terms
mean together:

```python
def apply_discount(price: float, percent: float) -> float:
    return price * (1 - percent / 100)
```

A test exists and passes:
```python
def test_apply_discount_ten_percent():
    assert apply_discount(100.0, 10) == 90.0
```

Later, someone "simplifies" the function:
```python
def apply_discount(price: float, percent: float) -> float:
    return price - percent   # BUG: treats percent as a flat amount, not a percentage
```

Running the existing test again still **passes** —
`apply_discount(100.0, 10)` returns `90.0` either way (`100 - 10 == 90`),
so this *weak* test does **not** detect the regression: the buggy
implementation happens to return the same result for that particular
input. A better-chosen test does detect it:
```python
def test_apply_discount_twenty_percent():
    assert apply_discount(200.0, 20) == 160.0   # old code: 160.0; new (buggy) code: 180.0
```
A weak or poorly chosen test can fail to detect a real regression. This is a **regression** — correct behavior (`apply_discount` computing
a true percentage discount) became incorrect as a side effect of an
unrelated-seeming "simplification." A **bug** is any instance of
incorrect behavior; a **defect** is often used interchangeably with
"bug," particularly in more formal/production contexts, to mean a
flaw in the software that causes it to behave incorrectly. A
well-chosen test existing *before* this change is precisely what turns a
silent, undiscovered regression into an immediate, loud test failure.

## 3. Testing vs. Debugging

This distinction matters enough to state with complete precision before
this chapter goes any further, because the two activities are easy to
conflate and serve genuinely different purposes.

**Testing asks**: *"Does the system behave as expected?"* Its job is to
**detect** that something is wrong (or confirm that nothing is), across
a known, repeatable set of inputs.

**Debugging asks**: *"Why is the system behaving incorrectly?"* Its job
is to **investigate** an already-known failure and find its root cause.

```
TESTING                              DEBUGGING
   │                                     │
"Is this correct?"                   "Why is this wrong?"
   │                                     │
runs code against expectations        investigates a specific failure
   │                                     │
produces PASS / FAIL                  produces a root-cause explanation
```

**How they work together**, in a realistic sequence: a test fails —
`test_apply_discount_twenty_percent` reports `160.0 != 180.0`. That
failure is testing's job done correctly: it detected that something is
wrong, precisely and immediately. **Debugging now begins**: you read
the failing test's inputs and expected value, trace through
`apply_discount`'s actual code, and discover the flat-subtraction bug
from §2. Fixing the bug and re-running the test is how you confirm the
fix actually worked — testing again, now with a different, satisfying
result.

**Why this distinction matters practically**: a project that only ever
debugs (chasing bugs reported by users, in production, with no
systematic tests) has no early-detection mechanism at all — every bug
is discovered the hard way, after it's already shipped. A project that
tests without knowing how to debug efficiently has plenty of red
failures but no efficient way to actually resolve them. Module 07's
later chapters on debuggers, tracebacks, and minimal reproductions build
out the *debugging* half of this pair in depth; this chapter is
specifically about the *testing* half — and, in particular, about
*which level* of test (unit, integration, or end-to-end) is the right
tool for detecting a given kind of problem.

## 4. Test Cases

Every test case, regardless of its scale, has the same underlying
anatomy — commonly organized using the **Arrange-Act-Assert** pattern.

```
ARRANGE   →   set up whatever the test needs (inputs, objects, state)
ACT        →   execute the behavior being tested
ASSERT      →   check the actual result against the expected result
```

A concrete example, with each stage labeled:

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

- **Setup (Arrange)** — preparing everything the test needs *before*
  the behavior under test runs: input values, objects, files,
  configuration. For a simple case like this, setup is trivial (two
  local variables); §35 and §45 cover more substantial setup, including
  reusable fixtures and cleanup.
- **Input** — the specific values fed into the behavior being tested
  (`price`, `percent` here).
- **Execution (Act)** — actually calling the code under test, exactly
  once, with the arranged input.
- **Expected result** — what the test author believes the correct
  outcome should be, established *before* looking at what the code
  actually produces (a test written by discovering the actual output
  and then asserting on that is a much weaker check — it merely
  confirms "the code does what it currently does," not "the code does
  what it *should* do").
- **Assertion (Assert)** — the actual comparison between the observed,
  actual result and the expected result.
- **Cleanup (Teardown), where necessary** — releasing or resetting
  anything the setup stage created that could otherwise persist and
  affect later tests (a temporary file, a database row) — not needed
  for this trivial example, but essential once tests touch real
  external state (§45 covers this in depth).

Module 07's own next chapter,
[03-arrange-act-assert-and-test-design.md](03-arrange-act-assert-and-test-design.md),
develops Arrange-Act-Assert as a complete test-design discipline; this
chapter introduces it only to the depth needed to read and write the
test examples that follow.

## 5. Assertions

**What is an assertion?** An assertion is a statement in code that
declares "this must be true right now" — if it is, execution continues
silently; if it isn't, an error is raised immediately, reporting the
failure.

```python
assert add(2, 3) == 5
```

**Why assertions exist**: they are the actual mechanism that turns
"observe the result" into "compare with expectation and fail loudly if
it doesn't match" — without an assertion, running `add(2, 3)` and
merely looking at the output requires a human to notice, every time,
whether it's correct. An assertion automates that comparison and makes
a mismatch impossible to silently miss.

**Expected vs. actual, and assertion failure**: when an assertion's
condition is `False`, Python raises `AssertionError`. Under `pytest`
(introduced fully in §9–§10), a failing assertion is reported with rich
detail — showing both what was expected and what was actually produced
— without you needing to write that reporting yourself:

```python
def test_add():
    assert add(2, 3) == 6   # deliberately wrong, to show failure output
```

```
    def test_add():
>       assert add(2, 3) == 6
E       assert 5 == 6
E        +  where 5 = add(2, 3)
```

**Good assertions vs. weak assertions**: a **weak** assertion checks
far less than it could, giving a false sense of coverage:
```python
assert result is not None   # weak — passes for almost any non-None result
```
A **stronger** assertion checks the actual, specific value that matters:
```python
assert result == 90.0   # strong — verifies the exact expected outcome
```
§49 develops assertion quality into a full, dedicated topic once more
realistic examples (API responses, computed objects) are available to
illustrate it — the principle to hold onto from here forward: **an
assertion should verify the specific thing the test claims to be
testing, not merely that "something" happened.**

**A caveat about Python's `assert` statement**: `assert condition` is the
right tool for test assertions, including pytest tests. Application
runtime validation, however, should not rely on `assert` for conditions
that must always be enforced (user input, permissions, required
arguments) — Python can disable assertions entirely when run with
optimization (`python -O`), silently skipping those checks. Raise an
explicit exception such as `ValueError` instead.

## 6. Test Scope

**Test scope** is how much of a system a single test actually exercises
when it runs — from one small, isolated piece of logic, up to an entire
running application.

```
SMALL SCOPE                MEDIUM SCOPE                 LARGE SCOPE
one function/method     several components working    a complete, running
in isolation               together                       system end to end
```

This spectrum of scope is exactly what gives rise to the three test
**levels** this entire chapter is about:

- **Unit tests** (§7–§19) — small scope: one function, method, or small,
  isolated piece of logic.
- **Integration tests** (§20–§26) — medium scope: components
  interacting across a meaningful boundary (application and database,
  service and filesystem).
- **End-to-end tests** (§27) — large scope: an entire workflow, from a
  user or external request all the way through to a final, observable
  result.

**Why test scope matters**: a test's scope directly determines its
speed, its realism, its infrastructure needs, and how precisely a
failure points at the actual problem — a small-scope test runs in
milliseconds and, when it fails, narrows the problem down to almost
exactly one place; a large-scope test runs slower, needs more
infrastructure, and, when it fails, could be caused by almost anything
along the entire path it exercises. Every remaining section in this
chapter is, in one way or another, about understanding this tradeoff
precisely enough to choose the right scope deliberately, rather than by
habit or accident.

## 7. What Is a Unit?

**A "unit" is the smallest piece of code being tested in isolation** —
most often a single function or method, but not *always* exactly one
function.

A unit can reasonably be:
- **A function** — the most common, clearest case (`add`, `calculate_total`).
- **A method** — a function that happens to live on a class.
- **A small class** — when a class's behavior only makes sense evaluated
  as a whole (several methods that share and mutate internal state
  together).
- **An isolated piece of business logic** — a specific rule or
  calculation, even if its implementation happens to span a couple of
  tightly coupled private helper functions that are never meaningfully
  tested apart from each other.

**Why the exact definition varies by architecture and team**: whether
"a unit" means exactly one function or a small cluster of tightly
related functions/methods is genuinely a judgment call, shaped by how a
specific codebase is organized — a team with many small, independent
pure functions will naturally write one test per function; a team with
a small class whose methods only make sense together will more
naturally test the class as one cohesive unit. **This chapter does not
claim there is one universal definition of "unit"** — the properties
that actually matter (§11: fast, isolated, deterministic, focused) are
what define a good unit test, regardless of exactly how large the "unit"
itself is drawn.

## 8. Unit Testing

**Unit testing** is the practice of testing one unit (§7) on its own,
with its dependencies controlled, so the test verifies *that specific
unit's* behavior and nothing else.

The defining characteristics, introduced here and developed fully in
§11–§19:

- **Isolated behavior** — the test exercises the unit itself, not
  whatever else the unit happens to call into.
- **Controlled dependencies** — anything the unit depends on (another
  function, an external service) is either genuinely simple enough not
  to matter, or deliberately replaced with something predictable (§16).
- **Fast execution** — with no real database, network call, or
  filesystem access involved, a unit test typically runs in
  milliseconds.
- **Deterministic inputs** — the same input, given to the same code,
  produces the same result every single time the test runs, with no
  dependency on the current time, randomness, or external state.

```python
def calculate_total(price: float, quantity: int) -> float:
    return price * quantity
```

```python
def test_calculate_total():
    assert calculate_total(9.99, 3) == pytest.approx(29.97)
```

(Floating-point results are compared with `pytest.approx` rather than
`==`, since binary floats cannot represent most decimals exactly; `pytest`
is imported with `import pytest`.)

This is unit testing in its simplest, purest form: `calculate_total`
has no dependencies at all beyond its own arguments, so testing it in
isolation requires no special setup, no mocking, and no external
infrastructure whatsoever — exactly the shape §9 walks through in full,
line by line.

## 9. First Unit Test

Using `pytest` — the test framework this course, and the overwhelming
majority of real Python projects, use — write and run your first real
unit test, explained without assuming any prior `pytest` knowledge.

```python
# calculator.py
def add(a: int, b: int) -> int:
    return a + b
```

```python
# test_calculator.py
from calculator import add


def test_add():
    assert add(2, 3) == 5
```

**Reading this line by line:**

- **`from calculator import add`** — an ordinary import, exactly as
  covered in this course's module on imports and modules; the test file
  imports the function it intends to test.
- **`def test_add():`** — an ordinary Python function. `pytest`
  recognizes it as a **test** specifically because its name starts with
  `test_` — this is a **naming convention** `pytest` looks for during
  **test discovery** (§10), not special Python syntax.
- **`assert add(2, 3) == 5`** — the actual check (§5): call `add` with
  known inputs, and assert the result equals the expected value.

**Running it:**
```bash
uv run pytest test_calculator.py
```
```
test_calculator.py .                                                    [100%]

1 passed in 0.01s
```

The single `.` represents one passing test; `1 passed in 0.01s`
confirms it. If the assertion had failed, `pytest` would instead print
a `F`, followed by a detailed failure report showing exactly which line
failed and what the actual versus expected values were — exactly the
output format shown in §5.

**Why no special setup was needed**: `add` has no dependencies at all —
no file, no database, no network call — so this test needed nothing
beyond the function itself and one assertion. This is deliberately the
simplest possible case; §14–§19 build up from here toward testing code
that *does* have dependencies.

## 10. Pytest Basics for This Topic

This section teaches only the `pytest` mechanics needed to understand
test levels — not a complete `pytest` reference (Module 07's next
chapter, `02-pytest-assertions-fixtures-and-parametrization.md`, covers
`pytest` itself in full depth).

**Test file naming**: `pytest` automatically discovers files matching
`test_*.py` or `*_test.py` — `test_calculator.py` (as used above) is
the conventional form this course uses throughout.

**Test function naming**: within a discovered file, `pytest` looks for
functions whose names start with `test_` — `test_add`, not `add_test`
or `check_add`. This convention is what let `pytest test_calculator.py`
find and run `test_add` automatically, with no manual registration
step.

**`assert`**: as covered in §5 — `pytest` enhances Python's built-in
`assert` statement, giving detailed, readable failure output without
requiring any special assertion-method syntax (unlike some other
languages' test frameworks, which require something like
`assertEqual(a, b)`).

**Test discovery**: the automatic process by which `pytest`, given a
directory, finds every file matching the naming convention above,
imports it, and collects every matching test function inside it —
running `uv run pytest` with no arguments at all, from a project's root,
discovers and runs *every* test in the project this way.

**Running `pytest`**, the commands this chapter's examples use:

```bash
uv run pytest                          # discover and run every test in the project
uv run pytest -q                        # "quiet" mode — more compact output
uv run pytest path/to/test_file.py       # run only the tests in one specific file
uv run pytest path/to/test_file.py::test_name   # run one specific test function
```

**Test output**: a `.` per passing test, an `F` per failing test, in
the order they run; a summary line (`3 passed in 0.02s`, or `2 passed,
1 failed in 0.03s`) at the end.

**Failure output**: for each failing test, `pytest` prints the specific
line that failed, the values involved (per §5's example), and a
traceback showing exactly where the failure occurred.

**Exit codes**: `pytest` returns exit code `0` if every test passed, and
a non-zero exit code if any test failed (or an error prevented tests
from running at all) — directly reusable in a CI pipeline (§60) exactly
the way this course's earlier CLI/exit-code material used a program's
own exit code to signal success or failure to whatever invoked it.

## 11. Unit Test Characteristics

Strong unit tests reliably share six properties — worth checking any
unit test you write against this list directly.

- **Fast** — milliseconds, not seconds. `test_add` (§9) runs
  essentially instantly because it touches nothing beyond a plain
  function call.
- **Isolated** — a unit test's outcome depends only on the unit under
  test and its own inputs, not on other tests having run first, not on
  the current time, not on real external systems.
- **Deterministic** — the exact same test, run a thousand times,
  produces the exact same result every time (§38 develops this fully).
- **Focused** — a unit test verifies one specific behavior. A test named
  `test_add` that also happens to check logging output, error handling
  for a completely different function, and a database side effect all
  at once has stopped being focused, and become several tests
  pretending to be one.
- **Repeatable** — running it again, on a different machine, at a
  different time, produces the same outcome — a direct consequence of
  being isolated and deterministic.
- **Readable** — a developer unfamiliar with the test should be able to
  understand what behavior it's checking, and why it failed, without
  needing to trace through unrelated setup.

```python
# Focused and readable
def test_apply_discount_rejects_negative_percent():
    with pytest.raises(ValueError):
        apply_discount(100.0, -5)


# Unfocused — testing several unrelated things in one test
def test_everything():
    assert apply_discount(100.0, 10) == 90.0
    assert calculate_total(9.99, 3) == pytest.approx(29.97)
    assert add(2, 2) == 4
```

The second example isn't wrong in the sense of being incorrect — each
assertion is individually true — but when it fails, the test's name
(`test_everything`) tells you nothing about *which* of three unrelated
behaviors actually broke, and fixing one bug might require wading
through assertions about two features that have nothing to do with it.

## 12. What Unit Tests Should Test

Unit tests are the right tool specifically for **logic** — code whose
correctness can be judged purely from its inputs and outputs, without
needing any real external system involved.

- **Business rules** — `apply_discount`'s percentage calculation; a
  loyalty-tier eligibility rule; a pricing policy.
- **Transformations** — converting one data shape into another (a raw
  dict into a domain object, a CSV row into a validated record).
- **Calculations** — totals, averages, tax, statistics — any pure
  arithmetic or aggregation logic.
- **Validation logic** — is this input acceptable? (`validate_email`,
  `validate_positive_int`, directly reusing this course's earlier
  input-validation chapter's own functions as unit-testable examples).
- **Parsing logic** — turning raw text/bytes into structured data (a
  date string into a `datetime`, a config line into a key-value pair).
- **Branching logic** — every distinct path through an `if`/`elif`/
  `else` structure, or a `match` statement, each exercised by its own
  test case.
- **Error handling** — that a function raises the *right* exception,
  under the *right* condition (`test_apply_discount_rejects_negative_percent`
  above).

```python
def classify_temperature(celsius: float) -> str:
    if celsius < 0:
        return "freezing"
    if celsius < 20:
        return "cool"
    return "warm"


def test_classify_temperature_freezing():
    assert classify_temperature(-5) == "freezing"


def test_classify_temperature_cool():
    assert classify_temperature(10) == "cool"


def test_classify_temperature_warm():
    assert classify_temperature(25) == "warm"
```

Three separate tests, one per branch — each one focused, each one
telling you precisely which branch broke if it ever fails.

## 13. What Unit Tests Should Not Depend On

Unit tests generally avoid direct dependence on:

- **Real databases** — a genuine connection to a real (even a local
  test) database.
- **Real external APIs** — an actual network call to a third-party
  service.
- **Network services** — any real socket/HTTP call at all, even to
  something running locally.
- **Cloud services** — object storage, managed queues, anything
  requiring real network access and real credentials.
- **Production infrastructure** — anything that exists outside the
  test's own process.

**Why**, stated as four concrete, connected reasons:

- **Speed** — a real database query or network call takes
  milliseconds-to-seconds *per call*; a unit-test suite with hundreds
  or thousands of tests doing this becomes minutes-to-hours slow,
  destroying the fast feedback loop unit tests exist to provide.
- **Isolation** — a test depending on a real, shared external system can
  be affected by *other* things happening to that system (another
  test's leftover data, another process's concurrent writes), directly
  violating §11's isolation property.
- **Reliability** — a real network call can fail for reasons that have
  nothing to do with whether your code is correct (the service is
  briefly down, a transient network blip) — a test that fails for
  reasons unrelated to the code it's testing is worse than useless; it
  actively erodes trust in the whole suite (§39 develops this into
  "flaky tests" in full).
- **Reproducibility** — a real external system's state can change over
  time (new data added, a record deleted) — a test passing today and
  failing tomorrow, with no code change in between, defeats the entire
  purpose of a repeatable, deterministic check.

This is precisely why testing code that genuinely needs a database, a
filesystem, or a network service is a *different* test level —
integration testing (§20 onward) — not a failure of unit testing to
"handle" these cases; it's a deliberate, correct separation of concerns
between test levels.

## 14. Test Isolation

**Isolation**, in the unit-testing sense, means a test's result depends
only on the code under test and the inputs the test itself provides —
nothing external, shared, or incidental.

```python
def get_exchange_rate(client):
    response = client.fetch("/rates/USD")
    return response["rate"]
```

If `test_get_exchange_rate` calls this with a **real** HTTP client,
hitting a real exchange-rate service, several problems appear at once:
the test's **speed** now depends on real network latency; its
**result** now depends on whatever rate the real service happens to
return *today*, which could differ from what it returned yesterday
(making the test **non-deterministic**, §38); and its **reliability**
now depends on that external service being reachable at all, at the
exact moment the test happens to run, in CI or otherwise.

**Why isolation matters**, restated directly: a unit test for
`get_exchange_rate` should verify that the function correctly calls
`client.fetch("/rates/USD")` and correctly extracts `"rate"` from
whatever comes back — **not** whether a specific external service is
currently up, or what today's actual USD exchange rate happens to be.
Those are legitimate things to verify, but at a *different* test level
(integration, §25–§26), against a controlled, predictable stand-in for
the client (§16), not a live network dependency inside what's supposed
to be a fast, isolated unit test.

## 15. Dependencies in Unit Tests

Not every dependency is equally problematic for a unit test — the right
response depends on what *kind* of dependency it actually is.

| Dependency category | Example | Typically appropriate for a unit test? |
|---|---|---|
| **Pure function dependency** | calling another pure function with no side effects | Yes — often fine to call directly, no isolation needed |
| **In-memory dependency** | a plain Python object/dict held only in memory | Yes — cheap, fast, deterministic, no isolation concern |
| **Filesystem dependency** | reading/writing a real file on disk | Usually not — real I/O; typically belongs at the integration level (§24), or is replaced with a controlled stand-in |
| **Database dependency** | a real database connection/query | No — belongs at the integration level (§23) |
| **Network dependency** | an HTTP call to any real service | No — belongs at the integration level (§25) |
| **External service dependency** | a third-party API, a payment gateway | No — belongs at the integration (or contract, §68) level |

**Why dependency type affects test level**: a pure or in-memory
dependency introduces none of §13's four problems (speed, isolation,
reliability, reproducibility) — calling it directly inside a unit test
is perfectly fine, and often simpler and more honest than fabricating a
stand-in for something that was never actually risky to call. A
filesystem, database, network, or external-service dependency
introduces every one of those problems, which is exactly why it either
needs to be replaced with something controlled (§16) for a *unit* test,
or the test itself needs to become an *integration* test that
deliberately, knowingly accepts the real dependency as part of what
it's verifying.

## 16. Mocking Concepts

Three related, but genuinely distinct, ideas — introduced here only as
needed to understand unit testing with dependencies (§17); Module 07's
dedicated chapter,
[07-mocking-and-test-doubles.md](07-mocking-and-test-doubles.md),
covers mocking as a complete topic in its own right.

- **Stub** — a simplified stand-in that returns a fixed, predetermined
  value when called, with no real logic behind it. A stub for
  `get_exchange_rate`'s client might always return `{"rate": 1.1}`,
  regardless of what's asked.
- **Fake** — a stand-in with a real, working (but simplified)
  implementation — a fake database might be a plain Python dictionary
  that behaves *like* a database for the test's purposes (you can
  store and retrieve records), without being a real database engine at
  all.
- **Mock** — a stand-in that, beyond returning a value, also **records
  how it was called** — allowing a test to assert not just on the
  result, but on the fact that a specific method was called, with
  specific arguments, a specific number of times.

```python
class StubClient:
    def fetch(self, path: str) -> dict:
        return {"rate": 1.1}


def test_get_exchange_rate():
    result = get_exchange_rate(StubClient())
    assert result == 1.1
```

**Why mocking (in this broad, general sense — stubs, fakes, and mocks
together) is commonly used in unit testing**: it's precisely the
mechanism that lets `get_exchange_rate` be unit-tested at all, without
violating §13's "no real network dependency" guidance — `StubClient`
gives `get_exchange_rate` something that satisfies its actual
interface (an object with a `.fetch()` method), fully under the test's
control, with a fully predictable, deterministic result.

This chapter deliberately does not go further into `unittest.mock`'s
actual API, patching mechanics, or call-assertion syntax — that is
squarely `07-mocking-and-test-doubles.md`'s job; what matters here is
recognizing *why* these tools exist and roughly what each term means,
so §17–§18 can be read with real understanding.

## 17. Unit Testing with Dependencies

A realistic example — a payment service depending on a repository and a
notification service — showing exactly what a unit test isolates and
what it deliberately does not exercise for real.

```python
# payment_service.py
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

```python
# test_payment_service.py
class StubRepository:
    def save_payment(self, order_id: str, amount: float) -> str:
        return "payment-123"


class StubNotifier:
    def __init__(self):
        self.sent = []

    def send(self, order_id: str, message: str) -> None:
        self.sent.append((order_id, message))


def test_process_payment_saves_and_notifies():
    repository = StubRepository()
    notifier = StubNotifier()
    service = PaymentService(repository, notifier)

    payment_id = service.process_payment("order-1", 49.99)

    assert payment_id == "payment-123"
    assert notifier.sent == [("order-1", "Payment of 49.99 received")]


def test_process_payment_rejects_non_positive_amount():
    service = PaymentService(StubRepository(), StubNotifier())
    with pytest.raises(ValueError):
        service.process_payment("order-1", 0)
```

**What exactly this unit test isolates**: `PaymentService.process_payment`'s
own logic — that it validates the amount, calls the repository to save
the payment, and calls the notifier with the expected message. It
deliberately does **not** verify that `StubRepository` or `StubNotifier`
behave like a real database or a real notification system would — that
verification belongs to integration tests for the *real* repository and
notifier implementations (§20 onward). `StubNotifier`'s `self.sent`
list is a small, purpose-built recording mechanism (closer to a
lightweight mock than a full mocking-framework mock) letting the test
assert *what* was sent, without any real email/SMS/push infrastructure
involved at all.

## 18. Over-Mocking

Mocking (§16) is a tool, not an unconditional good — used too heavily,
it introduces its own, real problems.

- **Brittle tests** — a test that mocks *every* dependency down to
  granular internal calls can break the moment the implementation
  changes internally, even when the actual, observable behavior hasn't
  changed at all.
- **Implementation coupling** — a test asserting on *exactly how many
  times* an internal method was called, or *exactly which internal
  helper* was invoked, is testing *how* the code is written, not *what*
  it does — directly conflicting with §56's behavior-vs-implementation
  principle.
- **Tests that pass while the real system fails** — the most dangerous
  failure mode: if every dependency in a test is mocked to always
  return a convenient, correct-looking value, the test can pass
  indefinitely even if the *real* repository, notifier, or client would
  actually fail or behave differently in practice. A suite entirely
  built on heavily mocked unit tests, with no integration tests
  verifying the real components actually work together, can give
  100% passing confidence in a system that doesn't actually work.

```python
# Over-mocked — asserts on internal call mechanics, not observable behavior
from unittest.mock import Mock

def test_process_payment_calls_repository_exactly_once():
    repository = Mock()
    notifier = Mock()
    service = PaymentService(repository, notifier)

    service.process_payment("order-1", 49.99)

    repository.save_payment.assert_called_once()   # fragile — breaks if implementation is refactored
```

**When mocking is useful, and when it becomes harmful**: mocking a
genuine external dependency (§13–§15 — a database, a network call) so a
unit test can run fast and deterministically is squarely useful — it's
exactly what §17's `StubRepository`/`StubNotifier` do. Mocking becomes
harmful when it's used to avoid testing *any* real interaction at all,
anywhere in the system — a project needs *some* tests (integration
tests) that exercise the real repository and real notifier, or nothing
ever actually confirms they genuinely work together. This chapter
takes no absolute position that mocking is "always good" or "always
bad" — the engineering judgment is in matching the *amount* and
*target* of mocking to what a specific test is actually trying to
verify.

## 19. Pure vs. Impure Code

**A pure function** always produces the same output for the same input,
and has no observable effect on anything outside itself — no file
write, no network call, no mutation of something outside its own local
scope.

```python
# Pure
def calculate_total(price: float, quantity: int) -> float:
    return price * quantity
```

**An impure function** has a **side effect** — it does something beyond
computing and returning a value: writing to a file, calling a network
service, mutating a shared/global object, printing, or depending on
something outside its own arguments (the current time, `random`,
global state).

```python
# Impure — has a side effect (writes to a database)
def save_order(order_id: str, total: float) -> None:
    database.execute(
        "INSERT INTO orders (id, total) VALUES (?, ?)", (order_id, total)
    )
```

**Why pure functions are often easier to unit test**: a pure function's
correctness depends on nothing but its own arguments — call it, check
the return value, done; there is no side effect to observe, no external
state to set up beforehand or clean up afterward, and no possibility of
the same call producing a different result on a different run. An
impure function like `save_order` needs *something* — a real database
(integration test, §23) or a controlled stand-in (§16, for a unit test
verifying `save_order`'s own logic, such as that it builds the correct
SQL/parameters) — before it can be tested at all, precisely because its
job is to have an effect on something outside itself.

**The practical engineering takeaway**: wherever business logic *can*
be expressed as a pure function (§12's calculations, transformations,
validations), doing so makes it trivially, cheaply unit-testable; the
genuinely impure, side-effect-having parts of a system (persistence,
network calls) are exactly what integration and end-to-end tests exist
to verify, and are often deliberately kept as thin, separate functions
so the *pure* logic around them can be tested in isolation without
dragging the side effect along with it.

## 20. Integration Testing

**What is integration testing?** Integration testing verifies the
interactions between components across a meaningful boundary.
Depending on the architecture and the question being asked, the
participating components may be real, partially substituted, isolated, or
test-environment implementations — but integration tests are especially
valuable for verifying genuine interactions with the real thing on the
other side of the boundary, which is the opposite emphasis from §13–§18's
unit-testing approach of replacing a dependency with a controlled
stand-in.

**Why does it exist?** A unit test proves `PaymentService.process_payment`
calls `repository.save_payment(...)` correctly, *assuming* the
repository behaves the way `StubRepository` pretended it would. It
proves nothing at all about whether the **real** repository — backed by
an actual database — genuinely saves the payment correctly: does the
SQL work, does the schema match, does a real connection actually
succeed? Integration testing exists specifically to answer exactly
these questions, which unit testing, by design, cannot.

**What is being integrated?** Typically real (or realistic test-environment)
pieces, verified working together as they'll actually be used in production:

- **Application + database** — does the repository's SQL actually
  produce the right rows, against a real database engine?
- **Service + repository** — does the service correctly orchestrate a
  *real* repository, not a stub standing in for one?
- **Application + filesystem** — does file-reading/writing/parsing code
  work against a real filesystem?
- **Service + HTTP client** — does an HTTP client correctly send
  requests and parse responses against a real (test) server?
- **Pipeline + storage** — does a data pipeline's output actually land
  correctly in real (test) object storage?

Illustrative example (`real_database` and `PaymentRepository` are assumed
to exist, not defined here):

```python
def test_repository_save_and_fetch_payment(real_database):
    repository = PaymentRepository(real_database)

    payment_id = repository.save_payment("order-1", 49.99)
    saved = repository.get_payment(payment_id)

    assert saved.order_id == "order-1"
    assert saved.amount == 49.99
```

Unlike §17's unit test, this test uses a **real** `PaymentRepository`
against a **real** (test) database connection — it is verifying the
actual SQL and the actual database interaction genuinely work, not
merely that `PaymentService` calls the repository's method correctly.

## 21. Unit vs. Integration

| Aspect | Unit test | Integration test |
|---|---|---|
| **Scope** | One unit, in isolation | Components interacting across a meaningful boundary |
| **Dependencies** | Controlled (stubs/fakes) or none at all | Typically real or realistic test-environment (a test database, filesystem, or service) |
| **Speed** | Milliseconds | Slower — real I/O, real connections (often tens to hundreds of milliseconds, or more) |
| **Environment** | Pure Python process; minimal setup | Needs real infrastructure (a test database, a test server) |
| **Isolation** | Fully isolated from other tests and external state | Partially isolated — shares real infrastructure, needs deliberate cleanup (§45–§46) |
| **Failure types** | Points precisely at the unit's own logic | Can point at the code, the real dependency's configuration, or the boundary between them |
| **Realism** | Lower — dependencies are simulated | Higher — verifies real behavior against a real dependency |
| **Maintenance** | Low — simple, focused, rarely breaks for unrelated reasons | Higher — infrastructure setup/teardown adds real maintenance surface |

**A practical example threading through both**: `PaymentService`'s unit
test (§17) tells you the service's *own logic* — validation, the order
it calls its dependencies in, the message it sends — is correct,
*assuming* its dependencies behave as expected. `PaymentRepository`'s
integration test (§20) tells you the repository's real SQL genuinely
works against a real database. Neither test alone proves the *entire*
payment flow works correctly end to end — that's precisely what §27's
end-to-end tests are for, closing the loop §28–§29 make fully explicit.

## 22. Integration Boundaries

An **integration boundary** is the specific seam between your
application's own code and something external to it (or between two
meaningful components) — a dependency an integration test deliberately
exercises, typically for real.

```
application  ↔  database          (§23)
application  ↔  filesystem          (§24)
application  ↔  API                   (§25)
service  ↔  queue                       (a message broker/task queue)
pipeline  ↔  object storage                (a data pipeline's storage layer)
```

**Why these boundaries matter**: each one represents a place where your
own code's correctness depends on *correctly using* something you don't
fully control — a database's actual SQL dialect and constraints, a
filesystem's actual behavior around paths and permissions, an API's
actual response format and error codes. A unit test, by design, never
exercises the boundary itself (it replaces whatever's on the other side
with a stand-in) — only an integration test genuinely verifies that
your code and the real thing on the other side of the boundary actually
agree with each other. Identifying a system's integration boundaries
explicitly — the practice §59's test-strategy section formalizes — is
the first step toward deciding *where* integration tests are actually
needed, rather than writing them reflexively everywhere or nowhere.

## 23. Database Integration Tests

A realistic example — a repository, a real (test) database, and an
integration test verifying the actual interaction, not a mocked
stand-in.

```python
# repository.py
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
        row = self._connection.execute(
            "SELECT order_id, amount FROM payments WHERE id = ?",
            (payment_id,),
        ).fetchone()
        return row
```

```python
# test_repository_integration.py
import sqlite3
import pytest


@pytest.fixture
def test_database():
    connection = sqlite3.connect(":memory:")
    connection.execute(
        "CREATE TABLE payments (id INTEGER PRIMARY KEY, order_id TEXT, amount REAL)"
    )
    yield connection
    connection.close()


def test_save_and_get_payment(test_database):
    repository = PaymentRepository(test_database)

    payment_id = repository.save_payment("order-1", 49.99)
    row = repository.get_payment(payment_id)

    assert row == ("order-1", 49.99)
```

**Why this verifies actual interaction, not a mocked one**: the SQL
string in `save_payment` — its column names, its parameter order — is
genuinely executed against a real (if in-memory) SQLite database; a
typo in a column name, or a mismatch between the table schema and the
query, would be caught here, exactly the class of bug §13–§18's mocked
unit test structurally cannot catch, since a stub repository never runs
any real SQL at all.

**Test database, schema, setup, cleanup, isolation**: this example uses
SQLite's `:memory:` database — a genuine, real database engine, created
fresh and destroyed automatically at the end of the test, requiring no
external service or Docker container at all. The `CREATE TABLE`
statement establishes the schema the test needs; the `pytest` fixture's
`yield` pattern (covered further in §35) provides setup (creating the
connection and table) before the test runs and cleanup (`connection.close()`)
after it finishes, and — because a fresh in-memory database is created
for *each* test using this fixture — every test gets full isolation
from every other test's data, with no shared, leftover state at all.

**A note on infrastructure**: not every database integration test needs
Docker or a real network-accessible database server — an in-memory or
temporary-file database engine (SQLite, as shown) is often sufficient
and dramatically simpler; a heavier, containerized real database
(Postgres, MySQL) becomes worth the added complexity specifically when
your application depends on that database engine's own particular
behavior in ways a lighter substitute wouldn't faithfully exercise.

## 24. Filesystem Integration Tests

A realistic file-processing example — writing, reading, parsing, and
directory behavior, tested against a real (temporary) filesystem.

```python
# file_processor.py
import json
from pathlib import Path


def save_report(directory: Path, name: str, data: dict) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.json"
    path.write_text(json.dumps(data))
    return path


def load_report(path: Path) -> dict:
    return json.loads(path.read_text())
```

```python
# test_file_processor_integration.py
def test_save_and_load_report(tmp_path):
    directory = tmp_path / "reports"
    data = {"total": 100, "items": 3}

    saved_path = save_report(directory, "summary", data)
    loaded = load_report(saved_path)

    assert saved_path.exists()
    assert loaded == data
```

`tmp_path` is a built-in `pytest` fixture providing a fresh, real,
automatically-cleaned-up temporary directory, unique to each test —
introduced here as a practical tool; §35 covers fixtures more generally.

**Why a real temporary filesystem can be more useful than mocking every
file operation**: mocking `Path.write_text`/`Path.read_text` would let
you verify `save_report` and `load_report` are *called* with certain
arguments, but would tell you nothing about whether directory creation
actually works, whether the JSON serialization round-trips correctly,
or whether path construction (`directory / f"{name}.json"`) produces a
valid, real path — all genuine behaviors of the *real* filesystem and
`pathlib`/`json` modules that a mocked version would simply assume away.
A real temporary directory, automatically cleaned up by `pytest` after
the test finishes, gives the same speed and isolation benefits a unit
test wants (fast, no shared state between tests) while still exercising
the real underlying behavior — which is precisely why this specific
integration boundary is often cheap enough to test for real, rather
than needing to be mocked.

## 25. API Integration Tests

Integration tests for APIs verify that your application's HTTP client
code correctly sends requests to, and correctly interprets responses
from, a real service.

```
application
    ↓
HTTP client
    ↓
test API / service
```

```python
# weather_client.py
class WeatherClient:
    def __init__(self, http_client, base_url: str):
        self._http_client = http_client
        self._base_url = base_url

    def get_temperature(self, city: str) -> float:
        response = self._http_client.get(f"{self._base_url}/weather/{city}")
        response.raise_for_status()
        return response.json()["temperature"]
```

```python
# test_weather_client_integration.py
def test_get_temperature_against_test_server(test_server, http_client):
    client = WeatherClient(http_client, base_url=test_server.url)

    temperature = client.get_temperature("london")

    assert isinstance(temperature, float)
```

**What this discusses that a unit test wouldn't need to**:

- **Authentication** — does the real request actually include the
  credentials/headers the service requires, correctly formatted?
- **Request** — is the URL, method, and payload actually well-formed
  once genuinely serialized and sent?
- **Response** — does the client correctly parse a real HTTP response
  body, not a hand-crafted Python dict standing in for one?
- **Status code** — does `raise_for_status()` genuinely raise for a real
  4xx/5xx response, and genuinely not raise for a real 2xx one?
- **Payload** — does the actual JSON structure returned by the real (or
  test) service match what the client code assumes?

**Test doubles vs. real test services**: a **test double** here means a
lightweight, purpose-built local server (`test_server` above) —
standing in for the real, external weather API, but genuinely
implementing HTTP request/response handling, unlike a pure in-memory
stub that never touches the network at all. This is a meaningfully
different, *stronger* kind of test double than §16's `StubClient` — it
verifies real HTTP mechanics (serialization, status codes, headers)
while still avoiding dependence on the actual, external, production
weather service. §69 compares this and other options for testing
external dependencies directly.

## 26. External Services

Testing code that depends on a genuinely **external** third-party API
requires more care than testing your own database or filesystem, since
you don't control that service at all.

- **Real external service** — calling the actual, live third-party API
  directly from a test.
- **Sandbox** — many third-party services provide a dedicated,
  separate "sandbox" or "test mode" environment, behaving like the real
  service but without real-world side effects (no real charge, no real
  email sent) — the closest thing to "real," without the real
  consequences.
- **Fake** — a locally-run, simplified stand-in implementing enough of
  the real service's behavior to be useful for testing (§25's
  `test_server` is an example of this).
- **Mock** — a controlled, in-process stand-in (§16), predictable and
  fast, but the furthest from realistic.
- **Contract-oriented testing** — a way of verifying your code's
  assumptions about an external service's API *shape* stay correct over
  time, without necessarily calling the real service on every test run
  — introduced conceptually in §68.

**Trade-offs**: a real external service call is maximally realistic but
slow, potentially costly (a payment gateway's real charge), unreliable
(subject to the service's own uptime and rate limits), and
non-deterministic (the service's behavior can change independent of
your own code). A sandbox is the best available middle ground when one
exists. A fake or mock is fastest and most reliable but least
realistic, carrying the exact "tests that pass while the real system
fails" risk §18 already warned about.

**Important, stated explicitly**: **do not call a production external
service from ordinary automated tests.** Doing so risks real-world side
effects (real charges, real emails sent to real people), depends on
that service's availability for your *own* test suite's reliability,
and can violate that service's own terms of use if run repeatedly, at
scale, in CI. Prefer a sandbox where the service provides one; fall back
to a fake or mock, understanding the realism you're trading away by
doing so.

## 27. End-to-End Testing

**What is end-to-end (E2E) testing?** End-to-end testing verifies an
a complete, representative workflow through the system under test —
from the point a user or external caller initiates a request, through
the major application layers and meaningful real boundaries, to the
final, observable behavior, in a production-like setup where
appropriate. External dependencies need not always be real: they may
legitimately be sandboxed, virtualized, substituted, or represented by
realistic test environments when appropriate.

**What does "end-to-end" mean, literally?** From one *end* of the
system (the request coming in) to the other *end* (the response, or
the observable effect, coming out) — the entire path, not a slice of
it.

```
user request
    ↓
API
    ↓
application
    ↓
database
    ↓
response
```

**Why does E2E testing exist?** Because even a project with thorough
unit tests (§8–§19, verifying each piece's logic) *and* thorough
integration tests (§20–§26, verifying each boundary works with its real
dependency) has never actually verified that the **entire chain**,
wired together exactly as it runs in production, produces the correct
final result for a real request. A bug in how two already-individually-
tested pieces are wired together — the API layer passing the wrong
field name to the service layer, say — can slip through both unit and
integration tests individually while still breaking the real, complete
workflow.

Illustrative example (`running_app_client` is assumed to exist, not
defined here):

```python
def test_create_order_end_to_end(running_app_client):
    response = running_app_client.post(
        "/orders",
        json={"customer_id": 42, "items": [{"price": 19.99, "quantity": 2}]},
    )

    assert response.status_code == 201
    order_id = response.json()["order_id"]

    fetched = running_app_client.get(f"/orders/{order_id}")
    assert fetched.json()["total"] == 39.98
```

This test makes a real HTTP request against a genuinely running
application (`running_app_client`), which itself talks to a real (test)
database — exercising the *entire* path from request to response,
exactly as a real user's request would.

**What E2E tests validate**: complete user or business **workflows** —
"can a customer actually create an order and see it reflected
correctly" — not any single function's or component's internal
correctness, which unit and integration tests already cover more
cheaply and more precisely.

## 28. Unit vs. Integration vs. E2E

| Aspect | Unit | Integration | E2E |
|---|---|---|---|
| **Scope** | One unit, isolated | Two+ real components, one boundary | Entire workflow, every real layer |
| **Speed** | Milliseconds | Tens–hundreds of ms (or more) | Often seconds |
| **Isolation** | Full | Partial — shares real infrastructure | Minimal — the whole system, wired together |
| **Realism** | Lowest | Higher | Highest |
| **Infrastructure** | None, or in-process only | One real dependency (test database, test server) | The full application stack |
| **Failure diagnosis** | Points precisely at the unit | Points at the boundary or either side of it | Could be almost anywhere along the whole path |
| **Maintenance** | Lowest | Moderate | Highest |
| **Typical use** | Verifying logic correctness | Verifying a boundary genuinely works | Verifying a critical business workflow actually works end to end |

**One common example across all three levels**, using "calculate an
order's total": a **unit test** checks `calculate_total(price,
quantity)`'s arithmetic directly, with no dependencies at all. An
**integration test** checks that `OrderService`, using a **real**
`OrderRepository` against a real (test) database, correctly persists
and retrieves an order whose total was computed this way. An **E2E
test** checks that a real HTTP `POST /orders` request, hitting the real,
running application, produces the correct total in its real HTTP
response — exercising the API layer, the service layer, and the
database, all wired together exactly as production wires them. §29
develops this exact example into full working code at all three
levels.

## 29. Same Feature at Three Test Levels

Using one feature — **"Create Order"** — worked through fully at each
level, to make the distinction between them unambiguous.

**UNIT — test order total calculation, in complete isolation:**

```python
def calculate_order_total(items: list[dict]) -> float:
    return sum(item["price"] * item["quantity"] for item in items)


def test_calculate_order_total():
    items = [{"price": 9.99, "quantity": 2}, {"price": 5.00, "quantity": 1}]
    assert calculate_order_total(items) == 24.98
```
This verifies **only** the arithmetic — no service, no repository, no
database, no HTTP layer involved at all.

**INTEGRATION — test the order service, using a real repository, against
a real (test) database:**

```python
def test_order_service_creates_and_persists_order(test_database):
    repository = OrderRepository(test_database)
    service = OrderService(repository)

    order_id = service.create_order(
        customer_id=42,
        items=[{"price": 9.99, "quantity": 2}, {"price": 5.00, "quantity": 1}],
    )

    saved = repository.get_order(order_id)
    assert saved.total == 24.98
```
This verifies the service **and** the real repository **and** the real
database genuinely work together correctly — but says nothing about the
HTTP/API layer, since it's never involved here at all.

**E2E — test the complete path, from a real HTTP request to a real
response:**

```python
def test_create_order_via_api(running_app_client):
    response = running_app_client.post(
        "/orders",
        json={
            "customer_id": 42,
            "items": [{"price": 9.99, "quantity": 2}, {"price": 5.00, "quantity": 1}],
        },
    )

    assert response.status_code == 201
    assert response.json()["total"] == 24.98
```
This verifies the **entire** chain: the API correctly receives and
parses the request, correctly calls the service layer, which correctly
calls the real repository, which correctly persists to the real
database, and the API correctly serializes the final response — every
major layer, wired together as production wires them.

**Why this distinction is now unambiguous**: each test verifies a
genuinely different *scope* of the same underlying feature — the unit
test would still pass even if the HTTP layer or database were
completely broken (it never touches either); the integration test would
still pass even if the HTTP API layer had a bug (it never touches the
API at all); only the E2E test would catch a bug in how the layers are
actually wired together, and only the unit test would catch a subtle
arithmetic bug at essentially zero cost, without needing any real
infrastructure to detect it.

## 30. Test Pyramid

**The test pyramid** is a widely used heuristic for how a project's
tests should typically be *distributed* across the three levels:

```
              ▲
             / \
            / E2E \              — fewer
           /-------\
          / INTEGR.  \           — some
         /-------------\
        /   UNIT TESTS    \      — many
       /-------------------\
```

**Many unit tests, fewer integration tests, fewer still E2E tests.**

**Why**, stated as the same four factors §13 and §28 already
established, now applied to the *shape of a whole suite* rather than
one test at a time:

- **Speed** — a suite with mostly fast unit tests runs in seconds; a
  suite with mostly slow E2E tests runs in minutes-to-hours, destroying
  the fast feedback loop a developer needs while actively working.
- **Cost** — integration and E2E tests need real infrastructure (test
  databases, running services) to set up and maintain; unit tests need
  none of that.
- **Feedback** — many fast, focused unit tests give precise,
  immediate signal about exactly what broke; a failing E2E test gives
  much less precise signal about *where*, among everything it touches,
  the actual problem lies (§48 develops this diagnosis difficulty in
  full).
- **Maintenance** — integration and E2E tests are more expensive to
  keep passing as infrastructure and wiring change over time; a large
  suite weighted too heavily toward them becomes a maintenance burden
  that slows the whole team down.

**This chapter does not treat the pyramid as an absolute law.** It is a
**heuristic** describing what tends to work well for a typical
application with substantial internal business logic and a handful of
external dependencies. **Architecture genuinely influences the ideal
distribution**: a thin API layer that's mostly a pass-through to a
well-tested third-party service might reasonably have relatively *more*
integration/E2E tests and fewer unit tests, since there's comparatively
little pure internal logic to unit-test in the first place; a
data-heavy application with substantial internal business logic and
comparatively few external dependencies will naturally skew even more
heavily toward unit tests. §31 introduces an alternative model that
makes this architecture-dependence even more explicit.

## 31. Alternative Test Models

The test pyramid (§30) is the most widely known model, but not the only
one — worth knowing that alternatives exist, conceptually, without
turning this into a debate about which is "correct."

One commonly discussed alternative reshapes the pyramid's emphasis
toward **integration-style tests** as the largest layer, on the
reasoning that for certain architectures (particularly ones where
components are combined in ways that make integration-level tests both
cheap to write *and* highly representative of real usage), a
mid-sized, integration-focused test gives more confidence per unit of
effort than either a narrow unit test or a slow, broad E2E test.

**Why different architectures may favor different distributions**: a
system built from many small, independent, business-logic-heavy
functions naturally rewards many cheap unit tests (the pyramid's
classic shape). A system that's mostly thin orchestration — coordinating
calls between a few well-tested external components with comparatively
little standalone logic of its own — may get more genuine confidence
per test from a smaller number of well-chosen integration-level tests
than from unit-testing thin, nearly-trivial orchestration code in
isolation.

**The point worth taking from this section, deliberately not a
debate**: no single ratio is universally correct for every project. The
useful, durable principle underneath *every* one of these models is the
same one §30 already established — **fast, cheap, reliable tests should
make up the bulk of a suite, and slow, expensive, harder-to-maintain
tests should be reserved for what genuinely needs that level of
realism** — and the *exact* shape that produces should be decided by
looking at your own project's actual architecture (§59 turns this into
a concrete strategy-design process), not by copying a diagram
unconditionally.

## 32. Test Suites

Four related terms, worth being precise about since they're used
constantly from here on:

- **Test** — one specific, executable check (§1) — `test_add` is one
  test.
- **Test case** — the concrete scenario a test represents (§4) — often
  used interchangeably with "test" in casual conversation, though more
  precisely it refers to the specific input/expectation the test
  embodies.
- **Test suite** — a collection of tests, run together — `pytest`,
  pointed at a directory, runs every test it discovers as one suite.
- **Test layer** (or "test level") — a *category* of tests grouped by
  scope (§6) — the unit layer, the integration layer, the E2E layer —
  each potentially organized as its own sub-suite (§33).

```
test suite
├── unit layer        (many individual tests)
├── integration layer   (some individual tests)
└── e2e layer              (few individual tests)
```

**How a project organizes tests**: most real Python projects keep a
single overall `tests/` directory (as this course's project-layout
material already established sits *outside* the package's own source
tree), internally subdivided by layer — exactly the structure §33
details next — so that "run all tests," "run only unit tests," and "run
only integration tests" are each simple, well-defined operations rather
than requiring tests to be picked out individually by hand.

## 33. Test Organization

A realistic project structure, directly extending this course's earlier
project-layout material:

```
project/
├── src/
│   └── app/
│       ├── __init__.py
│       ├── orders.py
│       └── payments.py
└── tests/
    ├── unit/
    │   ├── test_orders.py
    │   └── test_payments.py
    ├── integration/
    │   ├── test_order_repository.py
    │   └── test_payment_repository.py
    └── e2e/
        └── test_create_order_workflow.py
```

**Why this separation helps**: it lets a developer (or CI, §60–§61) run
`uv run pytest tests/unit/` alone, in seconds, for fast local feedback
while actively coding — without waiting for slower integration or E2E
tests that need real infrastructure. It also makes a test's *intended
scope* visible from its file location alone, before even opening the
file — a strong, useful signal for anyone navigating the suite later.

**Organization conventions can vary by project.** Some projects instead
mirror the source tree's own structure within each layer
(`tests/unit/orders/test_calculations.py` alongside
`src/app/orders/calculations.py`); others use `pytest` markers (a
mechanism this chapter does not cover in depth — see
`02-pytest-assertions-fixtures-and-parametrization.md`) to tag tests by
level within a single, unsplit `tests/` directory, rather than
separating them into subdirectories at all. Neither approach is
objectively "the" correct one — the property that actually matters is
that a project's own convention is **consistent and discoverable**, so
anyone reading the suite (or configuring CI to run a subset of it) can
tell, reliably, which tests belong to which level.

## 34. Test Naming

A test's name should communicate **what behavior it verifies**, clearly
enough that a failure report — just the test's name, with no further
context — tells a reader roughly what went wrong.

```python
# Weak — tells you almost nothing when it fails
def test_1():
    assert calculate_total([]) == 0

# Better — states the behavior AND the specific scenario
def test_calculate_total_returns_zero_for_empty_cart():
    assert calculate_total([]) == 0
```

**Why names should communicate behavior**: imagine a CI run reporting
`FAILED test_1` versus
`FAILED test_calculate_total_returns_zero_for_empty_cart` — the second
tells a reader, before even opening the file, exactly what expectation
broke; the first tells them nothing at all, forcing them to open the
file just to find out what's even being checked.

A common, effective naming pattern:
```
test_<unit_under_test>_<expected_behavior>_<condition_if_relevant>
```
```python
def test_apply_discount_rejects_negative_percent(): ...
def test_apply_discount_returns_original_price_when_percent_is_zero(): ...
def test_get_order_raises_not_found_for_unknown_id(): ...
```

Each name, read on its own, states precisely what scenario is being
verified — the actual test body then simply confirms what the name
already promised.

## 35. Test Fixtures

**What is a fixture?** A **fixture** is reusable setup (and, where
needed, teardown) logic that one or more tests can request, rather than
each test repeating the same setup code by hand.

```python
import pytest


@pytest.fixture
def sample_cart():
    return [{"price": 9.99, "quantity": 2}, {"price": 5.00, "quantity": 1}]


def test_calculate_total(sample_cart):
    assert calculate_total(sample_cart) == 24.98


def test_cart_item_count(sample_cart):
    assert len(sample_cart) == 2
```

- **`@pytest.fixture`** marks `sample_cart` as a fixture — a function
  `pytest` knows how to *provide* to any test that asks for it.
- A test **requests** a fixture simply by naming it as a parameter
  (`def test_calculate_total(sample_cart):`) — `pytest` calls the
  fixture function and passes its return value in automatically.
- Both tests above reuse the exact same setup logic, instead of each
  redefining `[{"price": 9.99, ...}, ...]` independently — a direct,
  practical application of the same "don't repeat yourself" principle
  this course has applied to application code all along, now applied to
  test code.

Fixtures with real setup **and** teardown (as already seen in §23's
`test_database` and §24's `tmp_path`) use `yield` instead of `return`:
```python
@pytest.fixture
def test_database():
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE payments (...)")
    yield connection          # the test runs here, receiving `connection`
    connection.close()          # runs after the test finishes, success or failure
```

**This section deliberately does not cover fixture scope, fixture
composition, or every other `pytest` fixture feature in depth** — that
full treatment belongs to
`02-pytest-assertions-fixtures-and-parametrization.md`; what matters
here is understanding what a fixture *is* and why it's the natural tool
for the setup/teardown need integration and E2E tests especially rely
on (§45).

## 36. Test Data

**Test data** is the specific input values a test uses — and its
*quality* directly determines how much a passing test actually proves.

- **Minimal data** — the smallest input that exercises the behavior
  being tested (`calculate_total([])` for "empty cart" behavior) —
  useful for isolating exactly one specific case cleanly.
- **Realistic data** — data resembling what the system will actually
  see in production (a cart with several items, realistic prices) —
  useful for confidence that ordinary, everyday usage genuinely works.
- **Boundary data** — values right at the edge of what's valid (a
  quantity of exactly `0`, a discount of exactly `100`) — exactly where
  off-by-one and edge-case bugs tend to hide (§51 develops boundary
  cases fully).
- **Invalid data** — values that *should* be rejected (a negative
  price, a malformed email) — verifying error-handling logic actually
  fires correctly (§50 covers this as "negative testing").
- **Deterministic data** — fixed, known values, never derived from the
  current time, `random`, or any other source that could differ between
  runs (§38 develops determinism as its own topic).

**Why test data quality matters**: a test using only one, convenient,
"obviously correct" input can pass even when the underlying code is
subtly wrong for values that input never happened to exercise — a
`calculate_total` bug that only manifests for an empty cart would never
be caught by a test that only ever uses a cart with items in it. The
strength of a test's coverage is inseparable from the *quality and
variety* of the data it actually exercises, not merely the fact that
"a test exists."

## 37. Test Isolation and Test Data

Tests can interfere with **each other**, not just with the code they're
testing — a different, additional meaning of "isolation" from §14's.

**Common ways this happens:**

- **Shared files** — two tests writing to the same fixed file path can
  clobber each other's data if run in an unexpected order, or in
  parallel.
- **Shared database rows** — a test that creates a customer with a
  fixed, hardcoded ID can collide with another test doing the same
  thing, or can leave data behind that a *later* test unexpectedly
  depends on (or is broken by).
- **Global state** — a module-level variable or cache mutated by one
  test can silently affect the result of a completely unrelated test
  that runs afterward, in the same process.
- **Environment variables** — a test that sets `os.environ["MODE"] =
  "test"` and never resets it can leave that value in place for every
  subsequent test in the same run.

**Strategies for isolation:**

- **Use fresh, unique test data per test** — `tmp_path` (§24) and an
  in-memory `:memory:` database created fresh per test (§23) are both
  concrete examples of this: each test gets its own, brand-new instance,
  with nothing shared.
- **Clean up explicitly** — a fixture's `yield`-then-teardown pattern
  (§35, §45) ensures state created for one test doesn't leak into the
  next, even if the test itself fails partway through.
- **Avoid hardcoded shared identifiers** — generate a unique ID per
  test run rather than reusing the same fixed customer ID `"1"` across
  every test that happens to need one.
- **Reset or scope global/environment state explicitly** — restore any
  environment variable or global value a test changes, in a teardown
  step, rather than leaving the change in place for whatever runs next.

**Why this matters**: a test suite where tests silently depend on each
other's leftover state produces failures that depend on **run order** —
passing when run alone, but failing (or, worse, passing for the wrong
reason) when run as part of the full suite, or in a different order
than usual. This is one of the most common, most confusing sources of
mysterious test behavior in real projects, and is a direct precursor to
the flaky-test problem §39 covers next.

## 38. Test Determinism

**A deterministic test** produces the exact same result — pass or fail
— every single time it runs, given the same code, regardless of when,
where, or how many times it's run.

**Sources of nondeterminism**, each undermining this guarantee in a
different way:

- **Current time** — `datetime.now()` used inside code under test (or
  inside the test itself) produces a different value every run,
  potentially crossing a day/month boundary between runs and changing
  the result.
- **Randomness** — `random.choice(...)`, an unseeded random ID
  generator, or anything similar can legitimately produce a different
  value each run.
- **Network** — a real network call's timing, availability, and
  response content can all vary between runs (§13, §26).
- **Concurrency** — code involving threads, async tasks, or any kind of
  race condition can produce different orderings — and therefore
  potentially different results — from run to run.
- **Shared state** — exactly §37's problem, restated: a test whose
  result depends on what an *earlier* test happened to leave behind is
  not deterministic on its own.
- **External services** — a real dependency's own data or behavior
  changing over time (§13, §26) between one test run and the next.

**Mitigation strategies, conceptually:**

- Replace real time with an injected, controllable clock (passing a
  fixed `datetime` into the function under test, rather than letting it
  call `datetime.now()` internally).
- Seed randomness explicitly (`random.seed(...)`) wherever a test
  genuinely needs to exercise random-dependent code, so its outcome
  becomes reproducible.
- Use a controlled stand-in (§16) rather than a real network call, for
  anything below the integration-test level.
- Design tests, and the code under test, to avoid unnecessary shared
  mutable state (§37).
- Recognize that some concurrency-related nondeterminism can be
  fundamentally difficult to eliminate entirely — the goal is
  minimizing it wherever practical, not necessarily achieving perfect
  determinism for every conceivable test.

**Why this matters**: a nondeterministic test is not simply "less
reliable" — it actively **undermines trust in the entire suite**, which
§39 develops into a full, dedicated topic.

## 39. Flaky Tests

**A flaky test** is one that sometimes passes and sometimes fails,
*without any change to the code being tested* — the direct, observable
symptom of the nondeterminism §38 describes.

**Why it's dangerous**: once a team has seen a specific test fail "for
no reason" a few times, a very natural, very damaging habit sets in —
**ignoring red (failing) results**, assuming "it's probably just that
flaky test again." The moment a team starts reflexively dismissing test
failures, the entire suite's value as a signal collapses — a *genuine*
regression, hiding among the noise, can slip through unnoticed,
precisely because the team has learned not to trust red results
anymore.

**Common causes**, directly reusing §38's list: unseeded randomness, a
real time-dependent comparison, a real network call inside what should
be a fast, isolated test, a race condition in concurrent code, or
leftover shared state from another test (§37).

**How to diagnose a flaky test**: run it repeatedly, in isolation, and
also as part of the full suite, looking for a pattern — does it fail
only when run after a specific other test (pointing at shared state,
§37)? Does it fail only around specific times (pointing at a
time-dependent comparison)? Does it fail only under load or when run in
parallel (pointing at concurrency or resource contention)? Reading the
test's own dependencies carefully against §38's list of nondeterminism
sources is usually the fastest way to narrow down the actual cause.

**How to reduce flakiness**: address the *actual* source of
nondeterminism directly — seed randomness, inject a controllable clock,
replace a real network call with a controlled stand-in at the
appropriate test level, fix the underlying shared-state or concurrency
issue — rather than working around the symptom.

**This chapter explicitly does not normalize blindly rerunning flaky
tests as a fix.** Automatically retrying a failing test until it
happens to pass can hide a *genuine*, intermittent bug in the code
itself (a real race condition, a real resource leak that only manifests
occasionally) — treating the retry mechanism as "the fix" instead of a
temporary mitigation risks leaving that real problem in production,
undetected, indefinitely. A flaky test deserves the same investigative
rigor as any other unexplained failure — retries, where used at all,
should be a deliberate, narrow, explicitly-justified mitigation, not a
default response to any test that occasionally goes red.

## 40. Test Environments

Four genuinely different environments a test (or the system a test
exercises) can run in, each with a different purpose:

- **Local test environment** — a developer's own machine, running tests
  directly during active development — fastest feedback, but only as
  representative of "real" conditions as the developer's own setup
  happens to be.
- **CI test environment** — an automated, consistent environment
  (created fresh for each run) that runs the suite on every push/pull
  request, independent of any individual developer's local setup —
  exactly the environment this course's earlier dependency-management
  material already established as needing to install from a committed
  lock file, for the same reproducibility reasons.
- **Staging** — a separate, running deployment intended to resemble
  production closely, used for broader validation (often E2E and
  manual testing) before a real release.
- **Production** — the actual, live system real users depend on —
  where testing, if it happens at all, takes the specific, careful,
  non-disruptive forms §70–§71 describe (health checks, smoke tests),
  never ordinary destructive test runs.

**How test level relates to environment**: unit tests (§42) need
essentially no environment beyond a Python interpreter, and run
identically well locally or in CI. Integration tests (§43) need real,
but typically lightweight and disposable, infrastructure (a test
database, a temporary directory) — practical both locally and in CI.
E2E tests (§44) typically need the most complete environment — a fully
running application, wired together the way it will actually run — and
are therefore most naturally run in CI or staging, less often on every
individual local `pytest` invocation during active development.

## 41. Test Configuration

Integration and E2E tests typically need some configuration to know
*where* their real dependencies actually live — directly extending this
course's earlier configuration-management material into a testing
context.

Examples:
- **Database URL** — where the test database actually is (often a
  local, disposable one, per §23, or a dedicated test instance).
- **API endpoint** — the base URL of a test server or sandbox (§25–§26).
- **Test mode** — a flag telling the application under test to behave
  slightly differently for testing purposes (e.g., disabling a real
  outbound email send).
- **Credentials** — whatever a test service genuinely requires to
  authenticate.
- **Feature flags** — enabling/disabling specific behavior for a
  specific test run.

**Safe configuration practices**: exactly this course's earlier
guidance on environment variables and secrets, applied here without
exception — a test-specific `.env.test` (or equivalent) file, containing
**test-only, non-production credentials**, is a reasonable pattern; a
`.env.test.example` template, committed to version control with
placeholder values, documents what's needed without exposing anything
real. **Never include real secrets in test configuration, in test code,
or in a test fixture** — a test database's credentials should be
disposable, test-only values, never real production credentials
reused "just for convenience."

## 42. Unit Test Environment

**Why unit tests should generally require minimal infrastructure**:
this follows directly from §8's and §13's own definitions — a unit
test's entire point is verifying isolated logic, with dependencies
either genuinely absent, or replaced with controlled stand-ins (§16).
Requiring a real database, a real server, or any other infrastructure
just to run the unit-test layer would contradict the very isolation
that makes it a unit test in the first place.

```
pure Python                — a plain interpreter and the project's own dependencies
local dependencies            — anything genuinely lightweight and in-process
mocks/fakes where appropriate    — controlled stand-ins for anything external (§16)
```

**Practical payoff**: a unit-test suite that needs *nothing* beyond
`uv sync` and `uv run pytest tests/unit/` can run identically, and
identically fast, on any developer's machine and in CI, with zero setup
friction — exactly the property that makes it usable as constant,
immediate feedback while actively writing code.

## 43. Integration Test Environment

Integration tests, by design (§20–§26), need **real** infrastructure for
whichever boundary they exercise:

- **Database** — a real (often disposable/in-memory, per §23) database
  instance.
- **Filesystem** — a real, temporary directory (§24).
- **Service** — a real (often local or sandboxed, per §25–§26) HTTP
  server.
- **Message broker** — for a system using one, a real (often local or
  disposable) queue/broker instance.

**Trade-offs**: real infrastructure, even lightweight and disposable,
adds genuine setup cost (starting a test database, provisioning a test
server) and genuine runtime cost (real I/O is slower than an in-process
call) compared to a unit test — exactly the cost §21's comparison table
already quantified. The trade-off is deliberate and worthwhile
specifically *because* it buys real confidence a unit test structurally
cannot provide: that the actual, real interaction genuinely works, not
merely that your code calls a stand-in correctly.

**A practical middle ground worth noting**: lightweight, disposable
infrastructure (SQLite's `:memory:` database, a `tmp_path` temporary
directory, a small local test server) often provides most of an
integration test's real value at a small fraction of the setup cost a
full, separately-provisioned, persistent test environment would
require — worth preferring wherever it faithfully exercises the actual
boundary being tested.

## 44. E2E Test Environment

**Why E2E tests often need a more complete environment**: an E2E test's
entire purpose (§27) is verifying the full, real chain — which means
every real layer that chain passes through needs to actually be
present and running.

```
application       — the real, running service
database             — a real (test) database it actually connects to
API                     — the real HTTP layer, actually listening for requests
frontend, if applicable   — a real UI, if the workflow being tested includes one
```

**Environment provisioning, conceptually**: getting this complete
environment running — starting the application, connecting it to a real
test database, making its API reachable — is itself real setup work,
typically automated (a startup script, a containerized test
environment, or a CI job step that brings the whole stack up before the
E2E suite runs) rather than assembled by hand for every run. This
chapter does not teach the specific mechanics of provisioning such an
environment (containers, orchestration) — the concept to take away is
that E2E testing's realism is inseparable from needing the *most*
complete, most production-like environment of the three test levels,
which is precisely why E2E tests are also the most expensive to set up
and run (§58 develops this trade-off in full).

## 45. Setup and Teardown

Restating and extending §4's Arrange-Act-Assert anatomy specifically
for tests that touch real, external state.

```
SETUP        →   prepare whatever real state/infrastructure the test needs
        ↓
EXECUTION      →   run the behavior being tested (Act + Assert)
        ↓
TEARDOWN         →   clean up whatever setup created, regardless of pass/fail
```

```python
@pytest.fixture
def test_customer(test_database):
    customer_id = test_database.execute(
        "INSERT INTO customers (name) VALUES (?)", ("Test Customer",)
    ).lastrowid
    yield customer_id
    test_database.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
```

**Why cleanup matters specifically for integration and E2E tests**:
unlike a unit test's in-process state (which simply disappears when the
test function returns, with nothing left behind), integration and E2E
tests touch **real, persistent** state — a real database row, a real
file — that will still be there after the test finishes unless
something explicitly removes it. Without teardown, that leftover state
becomes exactly §37's "shared test data" problem: a later test run
might collide with a customer row a previous run never cleaned up, or a
test database might slowly accumulate stale data across many runs until
it no longer represents a clean, known starting state at all.

`pytest`'s `yield`-based fixture pattern (already used in §23, §35, and
above) guarantees the teardown code runs **even if the test itself
fails** — the code after `yield` executes during fixture teardown
regardless of whether the test's own assertions passed, which is
precisely the guarantee that keeps a failing test from also leaving
behind orphaned state that corrupts subsequent runs.

## 46. Database Isolation

For database integration tests specifically, two commonly used
techniques keep each test's data changes from leaking into any other
test.

- **Test transactions with rollback** — begin a database transaction
  before the test runs, let the test freely insert/update/delete data
  as needed, and then **roll back** the transaction after the test
  finishes instead of committing it — every change the test made is
  undone automatically, as if it had never happened, with no manual
  per-row cleanup required at all.
- **Isolated test data per test** — as already used in §23 and §45,
  either a fresh database/table created per test (an in-memory SQLite
  database, recreated for every test using the fixture) or explicit,
  scoped cleanup (deleting exactly the rows a test created, as §45's
  `test_customer` fixture does).

```python
@pytest.fixture
def db_transaction(real_database_connection):
    transaction = real_database_connection.begin()
    yield real_database_connection
    transaction.rollback()   # every change made during the test is undone
```

**Why this is useful**: rollback-based isolation is often faster and
simpler than manual row-by-row cleanup, especially for tests that touch
several tables — the whole transaction disappears at once, with no risk
of forgetting to clean up one specific row. It requires a database and
driver that genuinely support transactions the way this pattern
assumes (most real relational databases do); this chapter introduces
the *concept* rather than a specific framework's exact transaction-
fixture implementation, which varies by project and database.

## 47. End-to-End User Journeys

E2E tests are best framed around **user or business journeys** — a
complete, realistic sequence of actions a real user or external caller
would actually perform — rather than around individual functions.

Examples of realistic E2E journeys:
- **User registration** — submit registration details → account is
  created → confirmation is observable.
- **Login** — submit credentials → session/token is issued → subsequent
  authenticated request succeeds.
- **Create order** — submit an order request → order is persisted →
  order is retrievable with the correct computed total (§29's full
  example).
- **Upload file** — submit a file → it's processed and stored →
  processed result is retrievable.
- **Process transaction** — submit a payment → it's recorded → status
  is correctly reflected afterward.
- **Submit AI request** — submit a prompt/request to an AI-backed
  endpoint → a response is returned → the response satisfies the
  workflow's basic contract (§65–§67 develop what "correct" even means
  for this specific case).

**Why E2E tests should focus on critical workflows, not every small
function**: an E2E test is the most expensive test level to write, run,
and maintain (§58) — spending that cost on a workflow that's central to
the business (checkout, login) is clearly worthwhile; spending the same
cost re-verifying a small validation rule that's *already* thoroughly
covered by a cheap, fast unit test adds little additional confidence
for a much higher ongoing cost. The unit and integration layers already
exist specifically to cover this kind of granular logic more cheaply —
E2E's distinct, irreplaceable value is confirming the *whole, wired-
together system* correctly serves a *real* workflow, which is exactly
where its cost is actually justified.

## 48. E2E Test Failure Diagnosis

**Why E2E failures are often harder to diagnose** than unit or
integration failures: an E2E test exercises every real layer at once
(§27–§28), so a failure could originate almost anywhere along that
entire path.

```
UI                       — did the request even get sent correctly?
API                          — did the request reach the right endpoint, correctly parsed?
application                     — did the business logic behave correctly?
database                            — did the data get persisted/retrieved correctly?
network                                — did a request between layers fail or time out?
external dependency                       — did a third-party service behave unexpectedly?
```

A single failed assertion (`assert response.json()["total"] == 24.98`)
tells you only that the **final observable output** was wrong — not
*which* of these six layers actually caused it.

**How logs and diagnostics help**: exactly why this course's earlier
logging chapter matters directly here — well-structured logs at each
layer (the API layer logging the request it received, the service
layer logging what it computed, the repository layer logging what it
persisted) let you trace a failing E2E test's actual path after the
fact, narrowing down *which* layer's behavior first diverged from
expectation, without needing to re-run the whole system under a
debugger from scratch. Module 07's own upcoming chapters on
tracebacks, logging, and minimal reproductions
([06-tracebacks-logging-and-minimal-reproductions.md](06-tracebacks-logging-and-minimal-reproductions.md))
build this diagnostic skill out in full — the point to take from this
section specifically is *why* E2E failures need that skill more acutely
than a unit test's precise, narrow failure ever does.

## 49. Test Assertion Quality

Directly extending §5's introduction to assertions, now with more
realistic examples showing the difference between a weak and a strong
check.

**Weak:**
```python
assert response is not None
```
This passes for almost *any* non-`None` response — an empty dict, an
error object, a completely wrong payload — telling you almost nothing
about whether the response is actually **correct**.

**Stronger:**
```python
assert response.status_code == 201
assert response.json()["order_id"] == expected_id
assert response.json()["total"] == 24.98
```
Each of these checks something **specific and meaningful**: the correct
HTTP status for a successful creation, the correct identifier being
returned, and the correct computed value — a failure in any one of
these points precisely at what actually went wrong, rather than merely
"something was returned."

**Why assertions should verify meaningful behavior, not just
presence/absence**: a test's entire value comes from what it actually
*checks* — a test with a weak assertion can pass even when the
underlying behavior is subtly, significantly wrong, giving a false
sense of security that's arguably worse than having no test at all
(since it looks like coverage exists, when it doesn't meaningfully
verify anything). Whenever writing or reviewing a test, it's worth
asking directly: "if the code were subtly broken in a realistic way,
would this specific assertion actually catch it?"

## 50. Negative Testing

**Negative testing** verifies that a system correctly **rejects**
invalid input or behaves correctly under a failure condition — the
deliberate counterpart to testing that valid input is handled
correctly (§51 covers the "happy path" side directly).

Examples:
- **Invalid input** — `calculate_total` given a negative quantity;
  `apply_discount` given a percent over 100.
- **Missing field** — a request payload missing a required field.
- **Unauthorized request** — a request made without valid
  authentication/authorization.
- **Nonexistent record** — fetching an order ID that doesn't exist.
- **Invalid configuration** — a service started with a malformed or
  missing required configuration value.

```python
def test_create_order_rejects_empty_items():
    with pytest.raises(ValueError):
        create_order(customer_id=1, items=[])


def test_get_order_returns_404_for_unknown_id(running_app_client):
    response = running_app_client.get("/orders/does-not-exist")
    assert response.status_code == 404
```

**Connecting to boundary validation**: this directly reuses this
course's earlier input-validation material — a function or endpoint's
validation logic is precisely what negative tests exist to verify is
actually enforced, not merely present in the code. A validation rule
that exists in the code but is never actually tested against invalid
input provides no real evidence it works correctly — negative tests are
what turn "we wrote validation logic" into "we've confirmed the
validation logic actually rejects what it's supposed to."

## 51. Happy Path vs. Edge Cases

Four related categories, worth distinguishing precisely for any given
feature:

- **Happy path** — the normal, expected, everything-goes-right
  scenario: a valid cart, correctly totaled.
- **Edge case** — an unusual, but still valid, scenario that sits at
  the margins of normal usage: a cart with exactly one item, a cart
  with a very large quantity.
- **Boundary case** — a value sitting exactly at the edge of a valid
  range: a discount of exactly `0`, exactly `100`, or a quantity of
  exactly `1` when `0` is the invalid minimum.
- **Invalid case** — something that should be explicitly rejected: a
  negative quantity, a discount of `150`.

```python
def apply_discount(price: float, percent: float) -> float:
    if not (0 <= percent <= 100):
        raise ValueError("percent must be between 0 and 100")
    return price * (1 - percent / 100)


def test_apply_discount_happy_path():
    assert apply_discount(100.0, 25) == 75.0

def test_apply_discount_boundary_zero_percent():
    assert apply_discount(100.0, 0) == 100.0

def test_apply_discount_boundary_hundred_percent():
    assert apply_discount(100.0, 100) == 0.0

def test_apply_discount_invalid_negative_percent():
    with pytest.raises(ValueError):
        apply_discount(100.0, -1)

def test_apply_discount_invalid_over_hundred_percent():
    with pytest.raises(ValueError):
        apply_discount(100.0, 101)
```

**How different test levels can cover these**: happy-path and boundary/
invalid cases for a pure calculation like `apply_discount` are cheapest
and most precisely covered at the **unit** level, exactly as shown
above. The *same* categories apply at the integration and E2E levels
too, just applied to a larger scope — an integration test's happy path
might be "a valid order is correctly persisted," its edge case "an
order with the maximum allowed number of line items," and its invalid
case "an order referencing a nonexistent customer ID is rejected by the
repository layer." The categories (happy/edge/boundary/invalid) are
independent of test level — what changes across levels is *how much of
the system* each category is checked against.

## 52. Regression Testing

**A regression test** protects behavior that previously worked against
being unintentionally broken again. It is very commonly added after a
real bug is discovered — capturing that exact failure so it can never
silently reappear — but that is not the only way a regression test can
originate.

```
reproduce bug
    ↓
write regression test        (a test that fails, demonstrating the bug)
    ↓
fix bug
    ↓
keep test permanently          (now passing, and staying in the suite forever)
```

Walking through this concretely, extending §2's `apply_discount` bug:

```python
# The bug: a "simplification" broke percentage-based discounting
def apply_discount(price: float, percent: float) -> float:
    return price - percent   # WRONG — treats percent as a flat amount

# Step 1: reproduce the bug as a failing test
def test_apply_discount_twenty_percent():
    assert apply_discount(200.0, 20) == 160.0   # FAILS against the buggy code above

# Step 2: fix the bug
def apply_discount(price: float, percent: float) -> float:
    return price * (1 - percent / 100)

# Step 3: the same test now passes — and stays in the suite forever
```

**Why the test is kept permanently, not deleted once the bug is
fixed**: its entire purpose is preventing this *specific* bug from
silently coming back in the future — exactly the "regression
prevention" reason testing exists at all, from §2. Deleting it the
moment the bug is fixed would throw away the one piece of evidence that
would catch this exact mistake if it were ever reintroduced, by anyone,
for any reason, later.

## 53. Test Coverage

**Test coverage** is a measurable statistic — most commonly, the
percentage of a codebase's lines (**line coverage**) or the percentage
of possible branches through conditional logic (**branch coverage**)
that are actually executed by the test suite at least once.

```python
def classify_temperature(celsius: float) -> str:
    if celsius < 0:
        return "freezing"
    if celsius < 20:
        return "cool"
    return "warm"
```

A test suite that only ever calls `classify_temperature(-5)` exercises
only the `"freezing"` branch. The `"cool"` and `"warm"` return lines are
never executed by any test at all, so they could be completely broken
with no test ever noticing. Additional tests (for example, one for `10`
and one for `25`) are required to exercise the other paths. **Line
coverage** (which lines ran) and **branch coverage** (which decision
outcomes were taken) are different measurements, and neither proves the
code is correct.

**A further, more meaningful (but harder to measure) idea**:
**behavior coverage** — not merely "was this line executed," but "was
the actual *behavior* this line represents genuinely verified by a
meaningful assertion." A line can be executed by a test whose
assertion is weak (§49) or entirely absent, technically counting toward
coverage while verifying nothing at all.

**Why high test coverage does not automatically mean high-quality
testing**: a test that calls a function and asserts nothing meaningful
about its result (or asserts something trivially true) still counts
fully toward line/branch coverage, while providing close to zero real
protection against a bug. Coverage measures **execution**, not
**verification** — it can tell you a line was *run*, never that it was
*correctly checked*.

**This chapter does not reduce testing strategy to a percentage.**
Coverage is a useful, cheap *signal* — a codebase sitting at 15%
coverage almost certainly has real, meaningful gaps worth
investigating — but chasing a specific coverage number as a goal in
itself can actively produce worse tests, by incentivizing exactly the
weak-assertion, execute-but-don't-verify pattern above, purely to make
a number go up.

## 54. Test Quality

Gathering this chapter's recurring themes into one explicit checklist —
worth running any test you write, or review, against directly:

- **Meaningful** — verifies something real about the code's behavior,
  not merely that it ran without crashing (§49, §53).
- **Deterministic** — the same result, every run (§38).
- **Isolated where appropriate** — a unit test isolated from real
  dependencies (§13–§14); an integration/E2E test isolated from *other
  tests'* leftover state (§37, §45–§46) even while deliberately
  exercising real dependencies of its own.
- **Maintainable** — doesn't need to be rewritten every time an
  unrelated implementation detail changes (§18, §55–§56).
- **Readable** — a reader can understand what's being verified and why
  it failed, from the test's name and body alone (§34).
- **Fast enough** — appropriate to its level: a unit test fast enough to
  run constantly during development; an integration/E2E test fast
  enough to run comfortably in CI without becoming a bottleneck.
- **Behavior-focused** — verifies observable outcomes, not internal
  implementation mechanics (§18, §56).

A test that satisfies every property on this list is, by this
chapter's own definition, a genuinely good test — and every earlier
section in this chapter has been building toward exactly one or more of
these properties.

## 55. Test Coupling

**Test coupling** (specifically, **implementation coupling**) happens
when a test's correctness depends not on a unit's *observable behavior*,
but on *how* that behavior happens to be implemented internally —
making the test fragile in a specific, avoidable way.

```python
# Fragile — coupled to an internal implementation detail
from unittest.mock import Mock

def test_process_order_calls_repository_save_exactly_once():
    repository = Mock()
    service = OrderService(repository)

    service.process_order(order)

    assert repository.save.call_count == 1   # breaks if the implementation is refactored
                                                # to (correctly) retry once on a transient failure
```

If `OrderService.process_order` is later refactored to retry a failed
save once (a genuine, desirable behavior improvement, with no change to
its *observable* contract — orders still get saved correctly), this
test breaks, even though nothing actually went wrong from a user's
perspective. The test was coupled to an implementation detail (calling
`save` exactly once) that was never actually part of the function's
real, observable contract.

**How tests become fragile this way**: by asserting on *internal
mechanics* — exact call counts to internal collaborators, the exact
sequence of internal method calls, private attribute values — rather
than on what a caller of the unit actually observes (its return value,
its externally visible side effects). §18's over-mocking discussion and
this section describe the same underlying problem from two angles: over-
mocking is *how* implementation coupling most commonly creeps in;
implementation coupling is *why* it's a problem.

## 56. Behavior vs. Implementation

**Test behavior; avoid unnecessary implementation details.** This is
the direct, positive principle §55 was building toward, worked through
with a concrete refactoring example.

**Before refactoring:**
```python
def calculate_total(items: list[dict]) -> float:
    total = 0.0
    for item in items:
        total += item["price"] * item["quantity"]
    return total
```

**After refactoring — same observable behavior, different
implementation:**
```python
def calculate_total(items: list[dict]) -> float:
    return sum(item["price"] * item["quantity"] for item in items)
```

**Which tests should continue passing, and why:**
```python
def test_calculate_total():
    items = [{"price": 9.99, "quantity": 2}, {"price": 5.00, "quantity": 1}]
    assert calculate_total(items) == 24.98
```
This test asserts only on `calculate_total`'s **return value** for a
given input — its **observable behavior** — and continues to pass
unchanged after the refactor, exactly as it should: the function's
*contract* (same inputs produce the same output) hasn't changed at all,
only its internal mechanics (a `for` loop versus a generator
expression) have.

A test asserting something like "the function uses a `for` loop
internally" (an inherently strange thing to test, included here only to
make the contrast explicit) would have broken for no behaviorally
meaningful reason at all — exactly the fragility §55 describes.

**The governing principle, restated as this section's own core
takeaway**: a test should be written so that it **passes unchanged**
through any refactor that preserves observable behavior, and **fails**
only when observable behavior genuinely changes — this is both the
definition of a good test's stability and the direct enabler of §2's
"refactoring safety" benefit.

## 57. Integration Test Trade-offs

Gathering §21, §23–§26, and §43's discussion into one explicit
trade-off summary, worth consulting when deciding whether a specific
integration test is worth writing.

- **Realism** — genuinely higher than a unit test; verifies an actual
  boundary actually works, not merely that your code calls a stand-in
  correctly.
- **Speed** — genuinely slower than a unit test; real I/O has real
  latency, even against lightweight, local infrastructure.
- **Infrastructure** — requires something real (even if disposable) to
  exist and be reachable — a genuine setup cost a unit test never
  incurs.
- **Maintenance** — changes to a real dependency's schema, API shape, or
  configuration can break an integration test even when your own code's
  logic hasn't changed at all — a maintenance cost unique to this level.

**When integration tests are worth their cost**: specifically at
**boundaries** (§22) where the actual interaction between your code and
something real genuinely matters and isn't already implied by a unit
test's stubbed assumption — a repository's actual SQL, a client's
actual request/response handling. They are generally **not** worth
writing merely to re-verify pure logic a unit test already covers more
cheaply and more precisely — that would pay integration testing's real
costs (speed, infrastructure, maintenance) for no additional confidence
over what the unit test already provides.

## 58. E2E Test Trade-offs

- **Realism** — the highest of the three levels; the only level that
  verifies the *entire, wired-together* system actually works for a
  real workflow.
- **Slower execution** — the slowest of the three, often by a wide
  margin, since every real layer's latency compounds along the whole
  path.
- **Infrastructure** — the most demanding of the three: a fully running
  application, connected to real (test) dependencies, exactly as §44
  described.
- **Flakiness** — the most exposed to nondeterminism (§38), since it has
  the most real, external moving parts of any test level, each a
  potential source of an intermittent failure.
- **Diagnosis complexity** — the hardest to debug when it fails, exactly
  as §48 detailed, since a failure could originate in any of several
  real layers.

**Why E2E tests should generally focus on critical workflows**:
restating §47's conclusion directly in trade-off terms — given how
expensive, slow, and comparatively fragile E2E tests are per test, a
suite that tries to E2E-test *everything* (rather than reserving E2E
specifically for the small number of workflows where its unique realism
genuinely matters) pays this level's full cost repeatedly, for
confidence the unit and integration layers could often have provided
far more cheaply. A small, carefully chosen set of E2E tests covering a
system's most critical, highest-value business workflows delivers most
of this level's real benefit without its costs compounding
unsustainably as the suite grows.

## 59. Test Strategy

A **test strategy** is a deliberate, upfront set of decisions about
*which* test level to apply *where* — replacing "we wrote whatever
tests occurred to us" with an actual, reasoned plan.

The questions a real test strategy answers, for a given system:

- **What should be unit tested?** — the system's actual business logic,
  calculations, validations, and branching (§12) — generally, as much
  of this as practical, since it's the cheapest, fastest, most precise
  test level available.
- **What should be integration tested?** — each genuine boundary (§22)
  the system has with something real it depends on — a database, a
  filesystem, an external API — specifically where the *real*
  interaction matters and isn't already covered by a unit test's
  stubbed assumption.
- **What should be E2E tested?** — the system's small number of
  critical business workflows (§47), not every possible path through
  the system.
- **What dependencies exist?** — an explicit inventory of the system's
  actual integration boundaries (§15, §22), since this directly
  determines where integration tests are even needed at all.
- **What are the critical business workflows?** — the handful of
  end-to-end journeys (§47) whose failure would matter most, and which
  therefore justify E2E's real cost.
- **What failures are most costly?** — a payment being processed
  incorrectly is far more costly than a cosmetic display bug; a test
  strategy should weight its investment toward the areas where an
  undetected failure would actually hurt the most.

**Applying this to a realistic system** produces a concrete answer, not
an abstract principle — exactly what §75's complete example project and
§78's mini-project both demonstrate in full, working detail.

## 60. Testing in CI/CD

A professional CI pipeline, directly extending this course's earlier
dependency-management and Ruff material with the test stages this
chapter has been building toward:

```
code
    ↓
uv sync                      — install the exact, locked dependencies
    ↓
Ruff                          — formatting and linting
    ↓
type checking                   — static type consistency
    ↓
unit tests                        — fast, isolated, run first among the test layers
    ↓
integration tests                     — real boundaries, run next
    ↓
E2E tests                                — the full, wired-together system, run last
    ↓
build/deploy
```

**Why this ordering, and why it may vary**: earlier stages are
deliberately faster and cheaper to run than later ones — Ruff catches
formatting/lint issues in seconds; unit tests run in seconds-to-a-few-
minutes; integration and E2E tests take progressively longer and need
progressively more infrastructure. Running cheap, fast checks **first**
gives the fastest possible feedback on the most common classes of
problems, and avoids spending an E2E suite's real time and
infrastructure cost on a change that a two-second lint check would have
already rejected. **Exact ordering can genuinely vary by project** — some
teams run type checking before Ruff, or unit and integration tests in
parallel rather than strictly sequentially — the durable principle is
"cheap, fast, high-signal checks before expensive, slow ones," not one
single universally mandated order.

**Fast feedback, pipeline stages, test failures, exit codes,
artifacts**: each stage's failure should stop the pipeline (or at least
clearly flag it) before wasting time on later, more expensive stages —
exactly the same exit-code-driven gating this course's earlier CLI
material established (`pytest`'s non-zero exit code on any failure,
§10, is what actually allows a CI system to detect "tests failed" and
halt the pipeline automatically). **Artifacts** — logs, coverage reports,
or other output a test run produces — are commonly saved by CI
specifically so a failure can be investigated after the fact without
needing to reproduce it locally from scratch, directly supporting the
diagnosis work §48 and Module 07's later debugging chapters cover.

## 61. Test Execution Strategy

Beyond simply *having* unit, integration, and E2E suites, teams commonly
separate **when** and **how often** each runs.

```
fast unit suite         — run constantly: on every save, every pull request, every commit
integration suite          — run on every pull request, or on a slightly less frequent trigger
E2E suite                     — run on merge to main, nightly, or before a release
```

**Why teams may separate these**:

- **Developer workflow** — a developer actively writing code wants the
  fastest possible feedback loop; running the full E2E suite on every
  local save would be far too slow to be useful, while the unit suite
  running in seconds fits naturally into constant, rapid iteration.
- **Pull requests** — a PR is a natural gate for both the unit *and*
  integration suites (fast enough to not meaningfully slow down review),
  giving strong confidence before a change is merged.
- **Nightly/full suites** — a full E2E run, or an especially slow or
  broad integration suite, can reasonably run on a schedule (nightly)
  rather than blocking every single PR, trading a small delay in
  catching E2E-level regressions for a much faster PR feedback loop.
- **Release validation** — before an actual release/deployment, running
  the complete suite (unit, integration, *and* E2E) one final time
  provides the strongest available confidence immediately before
  shipping.

**This chapter does not prescribe one universal schedule.** The right
balance depends on a project's actual suite runtime, its infrastructure
cost, and how costly a missed regression would be at each stage — a
small project with a fast, cheap E2E suite might reasonably run
everything on every PR; a larger project with a slow, expensive E2E
suite is far more likely to need the nightly/release-gated split
described above.

## 62. Testing Backend Services

A realistic backend example — an API service — tested at all three
levels, tying together everything this chapter has built.

```python
# service.py
class OrderService:
    def __init__(self, repository):
        self._repository = repository

    def create_order(self, customer_id: int, items: list[dict]) -> str:
        if not items:
            raise ValueError("order must have at least one item")
        total = sum(item["price"] * item["quantity"] for item in items)
        return self._repository.save_order(customer_id, items, total)
```

**Unit test** — the service's own logic, with a controlled repository:
```python
def test_create_order_rejects_empty_items():
    service = OrderService(StubOrderRepository())
    with pytest.raises(ValueError):
        service.create_order(customer_id=1, items=[])


def test_create_order_computes_correct_total():
    stub_repo = StubOrderRepository()
    service = OrderService(stub_repo)

    service.create_order(
        customer_id=1, items=[{"price": 9.99, "quantity": 2}]
    )

    assert stub_repo.last_saved_total == 19.98
```

**Integration test** — the service, with a **real** repository against
a real (test) database:
```python
def test_create_order_persists_correctly(test_database):
    repository = OrderRepository(test_database)
    service = OrderService(repository)

    order_id = service.create_order(
        customer_id=1, items=[{"price": 9.99, "quantity": 2}]
    )

    saved = repository.get_order(order_id)
    assert saved.total == 19.98
```

**E2E test** — the full, running API:
```python
def test_create_order_via_api(running_app_client):
    response = running_app_client.post(
        "/orders", json={"customer_id": 1, "items": [{"price": 9.99, "quantity": 2}]}
    )
    assert response.status_code == 201
    assert response.json()["total"] == 19.98
```

Exactly the same "one feature, three levels" pattern §29 introduced —
now shown for a backend service specifically, the most common real-
world context this whole chapter's material applies to.

## 63. Testing Data Pipelines

A data-pipeline example — input file → parser → validator →
transformation → storage — with each stage showing how test levels
apply.

```
input file
    ↓
parser              — turns raw text into structured records
    ↓
validator               — rejects malformed records
    ↓
transformation              — computes derived fields
    ↓
storage                        — persists the final result
```

**Unit tests** — each pure stage, tested independently:
```python
def test_parse_row_extracts_fields():
    row = parse_row("alice,30,engineer")
    assert row == {"name": "alice", "age": 30, "role": "engineer"}


def test_validate_row_rejects_negative_age():
    with pytest.raises(ValidationError):
        validate_row({"name": "alice", "age": -1, "role": "engineer"})


def test_transform_row_adds_seniority_flag():
    row = transform_row({"name": "alice", "age": 30, "role": "engineer"})
    assert row["is_senior"] is False
```

**Integration test** — the pipeline's real storage step, against a real
(test) destination:
```python
def test_store_records_writes_to_real_database(test_database):
    store_records(test_database, [{"name": "alice", "age": 30}])
    rows = test_database.execute("SELECT * FROM records").fetchall()
    assert len(rows) == 1
```

**E2E test** — the whole pipeline, from a real input file to real,
persisted output:
```python
def test_pipeline_end_to_end(tmp_path, test_database):
    input_file = tmp_path / "input.csv"
    input_file.write_text("alice,30,engineer\nbob,45,manager\n")

    run_pipeline(input_file, test_database)

    rows = test_database.execute("SELECT name FROM records").fetchall()
    assert {row[0] for row in rows} == {"alice", "bob"}
```

**Why this maps cleanly onto the same three levels**: parsing,
validation, and transformation are pure, isolated logic — ideal unit-
test material, exactly per §12 and §19. Storage is a genuine
integration boundary (§22) — worth verifying against a real destination.
The complete pipeline, from a real input file to real, persisted
output, is precisely what an E2E test for a data pipeline looks like —
the same "unit tests the logic, integration tests the boundary, E2E
tests the whole chain" shape, simply applied to a pipeline instead of a
web API.

## 64. Testing ML Systems

Testing an ML system requires distinguishing two genuinely different
activities this section is careful never to blur.

- **Software behavior testing** — does the *code* around the model
  behave correctly? This is exactly what unit/integration/E2E testing
  (as covered throughout this chapter) already applies to.
- **Model-quality evaluation** — is the *model itself* producing good
  predictions? This is a fundamentally different activity — evaluating
  accuracy, precision, or other statistical metrics against a held-out
  dataset — that belongs to ML evaluation practice, not to this
  chapter's software-testing vocabulary.

**What each test level covers for the software side of an ML system**:

- **Preprocessing** — unit test: given raw input, does the
  preprocessing function correctly produce the exact expected feature
  vector? (Pure, deterministic logic — ideal unit-test material.)
  ```python
  def test_preprocess_scales_feature_correctly():
      result = preprocess({"age": 30})
      assert result["age_scaled"] == pytest.approx(0.5)
  ```
- **Feature transformation** — same idea: pure, deterministic
  transformations, unit-tested directly.
- **Model wrapper** — unit test: given a *controlled, fake* model
  (returning a fixed, known prediction), does the wrapper correctly
  call it and correctly shape its output? This deliberately does
  **not** test whether the real model's predictions are *good* — only
  that the wrapping code around it behaves correctly.
  ```python
  def test_model_wrapper_formats_prediction():
      fake_model = FakeModel(fixed_prediction=0.83)
      wrapper = ModelWrapper(fake_model)
      result = wrapper.predict({"age": 30})
      assert result == {"score": 0.83, "label": "high"}
  ```
- **Inference API** — integration/E2E test: does a real HTTP request to
  the inference endpoint return a correctly *shaped* response (right
  status code, right JSON structure), using the real, loaded model —
  still not judging whether the *prediction itself* is "good," only
  that the request/response mechanics work correctly.
- **Storage** — integration test: are predictions/logs correctly
  persisted, exactly like any other database integration test (§23).
- **Complete prediction workflow** — E2E test: does a full request →
  preprocessing → model → response chain work correctly end to end,
  verifying the *software's* correctness, not the model's predictive
  quality.

**Why these two activities must not be confused**: a software test
asserting `assert prediction["score"] == 0.83` against a *fake* model is
testing that the wrapper correctly passes through and formats whatever
the model returns — it says nothing about whether `0.83` is actually a
*good* prediction for that input, which is a question about the real,
trained model's statistical quality, evaluated through entirely
different means (held-out test sets, accuracy/precision metrics) that
belong to ML evaluation, not to `pytest`-style software testing at all.

## 65. Testing AI Systems

Practical testing of an AI system focuses on the **software** around a
model call — request construction, response handling, orchestration
logic — while treating the model's own output as something to design
*around* carefully, given its nondeterminism.

- **Model clients** — unit test with a stubbed/faked client (§16),
  exactly like any other network-dependent code (§14–§17): does the
  client correctly build a request and correctly parse a *known,
  fixed* response?
- **Prompt construction** — a pure, deterministic function (given these
  inputs, build this prompt string) — ideal, cheap unit-test material:
  ```python
  def test_build_prompt_includes_user_question():
      prompt = build_prompt(user_question="What is the refund policy?")
      assert "What is the refund policy?" in prompt
  ```
- **Tool execution** — unit test each tool function's own logic
  directly (exactly like any other function, §12), independent of
  whether an actual model ever decides to call it.
- **Response parsing** — unit test: given a *fixed, known* raw model
  response (a realistic fixture, not a live call), does the parsing
  code correctly extract the structured result it's supposed to?
- **Orchestration** — integration test: does the orchestration logic
  correctly sequence a call to a (still stubbed, for now) model client,
  a tool call, and a final response assembly?
- **Retries** — unit/integration test: given a client that *fails* a
  fixed number of times before succeeding (a controlled stand-in,
  §16), does the retry logic behave exactly as designed (correct number
  of attempts, correct backoff, correct final behavior on exhausted
  retries)?
- **Fallbacks** — same approach: given a controlled failure from the
  primary path, does the fallback path correctly engage?

**Deterministic vs. nondeterministic model behavior**: the *code*
around a model call (request building, response parsing, retry logic)
is ordinary, deterministic software, testable exactly like any other
code in this chapter, using controlled stand-ins for the model itself.
The model's own *output*, when a real model is actually involved, is
frequently nondeterministic (§67 develops this fully) — which is
precisely why practical AI-system testing keeps these two concerns
separate: test the surrounding software deterministically and
thoroughly; treat the model's real output as something evaluated
differently, never asserted on with brittle, exact-match checks.

## 66. Testing Agentic AI Systems

A realistic agent architecture, and how each test level applies to it:

```
user
    ↓
agent
    ↓
planner
    ↓
tool selection
    ↓
tool execution
    ↓
state update
    ↓
final response
```

**UNIT — test tool-selection logic in isolation:**
```python
def test_select_tool_chooses_search_for_question_intent():
    tool = select_tool(intent="question", available_tools=["search", "calculator"])
    assert tool == "search"
```
This verifies the *selection logic itself* — given a known intent and a
known set of available tools, does it choose correctly — with no real
model call, no real tool execution, and no real orchestration involved
at all.

**INTEGRATION — test the agent plus a real tool adapter:**
```python
def test_agent_correctly_invokes_search_tool(real_search_tool):
    agent = Agent(tools=[real_search_tool])
    result = agent.run_tool("search", query="refund policy")
    assert "refund" in result.lower()
```
This verifies the *real* tool adapter's own behavior — that calling it
through the agent's own interface genuinely works — still without
necessarily involving a real, live model call to *decide* which tool to
use.

**E2E — test the complete path, user request → agent → tools → final
response:**
```python
def test_agent_handles_refund_question_end_to_end(running_agent_client):
    response = running_agent_client.post(
        "/agent", json={"message": "What is your refund policy?"}
    )
    assert response.status_code == 200
    assert "refund" in response.json()["answer"].lower()
```
This verifies the entire, real, wired-together chain — but note the
assertion: it checks that the word `"refund"` appears in the answer,
**not** that the answer exactly matches one specific, hardcoded string
— a direct, necessary consequence of the model's own nondeterminism,
developed fully in §67.

**Why each level still applies cleanly here**: tool-selection logic
(when it's ordinary, deterministic code rather than a model decision)
is pure, testable logic — unit-test material. A real tool's actual
behavior is a genuine integration boundary. The complete user-request-
to-final-response path is exactly what an E2E test verifies for any
system — an agentic system is simply a system whose internal wiring
happens to include a model call, not a fundamentally different kind of
thing to test.

## 67. Nondeterministic Systems

Systems containing **randomness**, **external APIs**, **LLMs**, or
**asynchronous operations** genuinely challenge the determinism (§38)
this chapter has otherwise insisted on — worth addressing directly
rather than glossing over.

**Deterministic test boundaries**: the practical resolution is drawing
a clear line between the parts of a system that *can* and *should* be
tested deterministically (prompt construction, response parsing, retry
logic, tool-selection logic when it's ordinary code) and the parts that
genuinely cannot be (a real model's actual generated text, a real
external service's exact real-time response) — testing thoroughly and
deterministically on one side of that line, and testing differently,
deliberately, on the other.

**Controlled inputs**: for the deterministic side, use fixed, known
inputs and fixed, known (stubbed/faked, §16) responses — exactly this
chapter's approach throughout §65–§66.

**Test doubles**: for the nondeterministic side, when the code's own
logic (not the model's judgment) is what's actually being verified,
replace the real, nondeterministic dependency with a controlled stand-
in — a fake model client returning a fixed response — so the *test*
itself remains deterministic even though the *real* dependency isn't.

**Behavioral assertions**: when a test genuinely needs to involve real,
nondeterministic output (an E2E test against a real model, for
instance), assert on **properties** of the output rather than an exact
match — does the response contain certain expected content, satisfy a
length constraint, pass a structural check (valid JSON, a required
field present) — rather than `assert response == "exact expected
sentence"`.

```python
# Fragile — exact-match assertion against nondeterministic model output
assert response.json()["answer"] == "Our refund policy allows returns within 30 days."

# More robust — behavioral assertion
assert "30 days" in response.json()["answer"]
assert response.json()["answer"] != ""
```

**This chapter does not claim exact output matching is always
inappropriate for AI systems** — a model configured deterministically
(fixed seed, temperature `0`, a specific pinned model version) in a
tightly controlled test context can sometimes support closer-to-exact
assertions. The general, safer default for real model calls, absent
that level of control, is behavioral assertion — checking that the
*shape and key properties* of a response are correct, not that its
*exact text* matches a single hardcoded expectation.

## 68. Contract Testing Concept

**Contract testing**, introduced here conceptually — not as a complete
framework tutorial — addresses a specific gap the earlier test levels
don't fully cover: verifying that two independently-developed services
continue to agree on the *shape* of the API between them, without
necessarily running a full integration test against the real, live
other service on every single test run.

- **Service expectations** — what one service (the **consumer**)
  actually relies on from another (the **producer**) — specific fields,
  specific types, specific status codes.
- **API contracts** — a recorded, explicit statement of those
  expectations, checked independently against both sides.
- **Producer/consumer compatibility** — the producer's team can verify,
  independently, that their service still satisfies every contract a
  known consumer depends on; the consumer's team can verify,
  independently, that their own code's assumptions still match the
  recorded contract — without either team needing to run the *other*
  team's full, real service just to find out.

**Why this matters, briefly**: in a system built from several
independently-deployed services (increasingly common for backend and
AI-platform architectures), a full integration test against every real
dependent service can become slow, fragile, and organizationally
difficult to coordinate (a required service simply not being available
in your own test environment). Contract testing offers a middle ground
between a fully mocked unit test (fast, but blind to real API drift)
and a full, real integration test (realistic, but expensive and
sometimes impractical) — worth knowing the term and the concept exists;
this chapter does not teach a specific contract-testing framework or
tool in depth.

## 69. Testing External Dependencies

Bringing §16 and §26's discussions together into one direct comparison
of the options for testing anything genuinely external.

| Approach | Speed | Realism | Reliability | Typical use |
|---|---|---|---|---|
| **Mock** | Fastest | Lowest | Highest (fully controlled) | Unit tests verifying your own code's logic |
| **Fake** | Fast | Moderate | High | Unit/integration tests needing more realistic behavior than a fixed-value mock |
| **Sandbox** | Slower | High | Depends on the sandbox's own uptime | Integration tests against a real (non-production) version of a third-party service |
| **Real test service** | Slowest | Highest | Depends entirely on the real service's availability | Rare — reserved for cases where nothing else provides sufficient confidence |

**Trade-offs, stated directly**: moving down this table trades
**speed** and **reliability** for **realism** — a mock is fast and
completely predictable but proves nothing about the real dependency's
actual behavior; a real test service proves the most but is the
slowest, least reliable, and (per §26) potentially unsafe to depend on
for ordinary, frequent test runs. The right choice, for any given test,
depends on exactly what that specific test is trying to verify: your
own code's logic (mock/fake, likely a unit test) versus the real
interaction itself (sandbox, likely an integration test) — restating
§15 and §22's guidance one final time, now as a single, unified
decision table.

## 70. Production Testing

**Pre-production testing** — everything this chapter has covered so
far (unit, integration, E2E) — runs against test environments, with
test data, before a change ever reaches real users.

**Production verification** is a different, much narrower activity:
safely confirming a **live**, already-running production system is
healthy, without performing destructive or state-changing test actions
against real user data.

Safe, conceptual techniques:
- **Health checks** — a lightweight endpoint/command confirming the
  service is up and its critical dependencies (database, downstream
  services) are reachable.
- **Smoke tests** (§71) — a small, safe set of checks confirming the
  most basic, critical functionality works immediately after a
  deployment.
- **Synthetic checks** — periodic, automated requests simulating real
  usage (a scheduled, harmless "search for X" request) to continuously
  confirm the system behaves correctly over time, not just immediately
  after deployment.
- **Canary validation** — routing a small fraction of real traffic to a
  new version first, monitoring it closely, before rolling it out to
  everyone — a deployment-safety practice that overlaps with testing's
  goals (catching a problem before it affects everyone) without being
  an automated test in the `pytest` sense.

**Keeping this conceptual and safe**: none of these techniques involve
running a project's ordinary, destructive `pytest` suite against a real
production database or real user accounts — production testing is
specifically about *safe*, *non-destructive*, *observational*
verification of a live system's health, a fundamentally different
activity from the test levels this chapter has otherwise focused on.

## 71. Smoke Tests

**A smoke test** is a small, fast set of checks run immediately after a
deployment, verifying that the most basic, critical functionality
works at all — not a thorough test of every feature, but a quick
"did anything catch fire" check.

A simple production deployment example:
```python
def test_smoke_service_responds():
    response = requests.get("https://api.example.com/health", timeout=5)
    assert response.status_code == 200


def test_smoke_can_fetch_a_known_public_resource():
    response = requests.get("https://api.example.com/products/1", timeout=5)
    assert response.status_code == 200
```

**Why "smoke test"**: the name comes from hardware testing — power on a
device and check whether smoke comes out, as the most basic possible
"did this catastrophically fail" check, before investing in more
thorough testing. Applied to software: run a small number of safe,
read-only checks against the freshly deployed production system,
confirming it's not catastrophically broken, before considering the
deployment successful.

**Where this fits relative to the rest of this chapter**: a smoke test
is typically the *last* automated check in a deployment pipeline — after
unit, integration, and E2E tests have already passed against a
pre-production environment (§60), a smoke test's job is specifically
confirming the *actual, live, newly deployed* system is healthy, which
no pre-production test, by definition, can verify on its own.

## 72. Test Maintenance

Tests are code, and — like any code — require ongoing maintenance, not
a one-time investment.

- **Obsolete tests** — tests verifying behavior that no longer exists
  or no longer matters (a feature that was removed, a code path that's
  now unreachable) — these should be deleted, not left indefinitely
  passing (or worse, quietly failing and ignored) for behavior nobody
  cares about anymore.
- **Duplicated tests** — several tests verifying the exact same
  behavior, adding maintenance cost (every one needs updating if the
  behavior legitimately changes) without adding any real additional
  confidence.
- **Flaky tests** (§39) — need investigation and fixing, not permanent
  tolerance.
- **Slow tests** — a test that's grown unnecessarily slow (often because
  it drifted toward a higher test level than it actually needs, or
  accumulated unnecessary real I/O) degrades the whole suite's feedback
  loop, and is worth revisiting for whether it could be rewritten at a
  cheaper level.
- **Brittle tests** — tests coupled to implementation details (§55)
  that break on every harmless refactor, training the team to distrust
  (or resent) the suite.

**When to refactor or remove a test**: a test should be **refactored**
when it's testing genuinely valuable behavior but doing so in a fragile
or unclear way (§34, §54–§56's quality checklist); it should be
**removed** when the behavior it verifies is genuinely gone, or when
it's a true duplicate of another, better test covering the exact same
ground. Treating a test suite as a static, "write once" artifact — never
revisited, never pruned — is precisely how a suite accumulates the kind
of drag (slow, flaky, brittle, redundant) that eventually leads teams to
stop trusting or running it at all.

## 73. Test Suite Performance

**Test runtime** compounds directly into a project's **feedback loop** —
the time between making a change and knowing whether it broke
something. A unit suite that takes 3 seconds supports constant,
rapid iteration; one that takes 20 minutes does not, regardless of how
good its individual tests are.

**Parallelism, conceptually**: many `pytest` setups can run independent
tests concurrently (across multiple CPU cores) rather than strictly one
after another, meaningfully reducing total suite runtime for a large
suite of otherwise-independent tests — this works cleanly specifically
*because* well-isolated tests (§14, §37) don't depend on shared,
mutable state; a suite with hidden inter-test dependencies can produce
incorrect, order-dependent results when parallelized, which is yet
another concrete, practical reason isolation (§37) matters beyond
correctness alone.

**Test grouping**: organizing tests by level (§33) directly supports
running only the fast, cheap subset (`tests/unit/`) during active
development, and reserving the full suite (including slower
integration/E2E layers) for CI or pre-merge checks (§61) — a direct,
practical application of test organization to test *performance*, not
merely tidiness.

**Kept practical**: this chapter does not teach the specific mechanics
or configuration of parallel test execution — the concept to take away
is that a suite's *runtime*, not just its individual tests' quality, is
itself something worth actively managing as a project and its test
suite both grow.

## 74. Common Beginner Mistakes

**1. Testing only happy paths.**
*Why it happens:* the happy path is the easiest scenario to think of
first, and the most satisfying to see pass. *Why it's problematic:*
real bugs disproportionately hide in edge, boundary, and invalid cases
(§51) — a suite covering only happy paths misses most of what actually
breaks in production. *Better approach:* deliberately write at least
one boundary and one invalid-input test for every piece of validation
or branching logic (§50–§51).

**2. Testing only implementation details.**
*Why it happens:* it can feel more thorough to assert on internal
mechanics. *Why it's problematic:* creates the fragile, coupled tests
§55 describes, breaking on harmless refactors. *Better approach:*
assert on observable behavior (§56).

**3. Confusing unit and integration tests.**
*Why it happens:* the boundary can feel blurry, especially for a
function that both computes something and touches a dependency.
*Why it's problematic:* a "unit" test that secretly makes a real
database call inherits all of §13's problems (speed, isolation,
reliability, reproducibility) while being mistaken for something fast
and isolated. *Better approach:* explicitly ask "which boundary is this test actually verifying?" — if it
exercises a real interaction across a meaningful boundary (a database,
the filesystem, an HTTP service), it's an integration test, and belongs in `tests/integration/`, not `tests/unit/` (§33).

**4. Making every test E2E.**
*Why it happens:* an E2E test feels the most "realistic" and reassuring.
*Why it's problematic:* pays E2E's full cost (§58) for confidence a
cheaper unit or integration test could often provide, and produces a
slow, fragile, hard-to-diagnose suite overall. *Better approach:* apply
the test pyramid's heuristic (§30) — reserve E2E for critical workflows
(§47), push everything else down to a cheaper level.

**5. Mocking everything.**
*Why it happens:* mocking feels like the "correct," modern way to write
unit tests. *Why it's problematic:* produces exactly §18's risk — tests
that pass while the real system fails, because nothing ever exercises a
real dependency. *Better approach:* mock genuine external dependencies
in unit tests; write real integration tests for the boundaries that
matter (§57).

**6. Mocking nothing.**
*Why it happens:* it feels simpler to just use real dependencies
everywhere. *Why it's problematic:* produces exactly §13's problems —
a slow, unreliable, non-deterministic "unit" suite that's actually an
integration suite in disguise. *Better approach:* apply §15's dependency
categorization — pure/in-memory dependencies can be used directly;
filesystem/database/network dependencies need a controlled stand-in at
the unit level.

**7. Sharing mutable state between tests.**
*Why it happens:* reusing a variable, fixture, or file across tests
seems convenient. *Why it's problematic:* produces order-dependent,
unreliable results — exactly §37's failure mode. *Better approach:*
fresh, isolated test data per test (§37, §45–§46).

**8. Relying on test order.**
*Why it happens:* tests happening to pass when run in a specific,
familiar order can go unnoticed as an actual dependency. *Why it's
problematic:* breaks the moment tests are run in a different order, in
parallel (§73), or as a subset — exactly the kind of failure that's
baffling because "nothing changed." *Better approach:* every test
should pass regardless of what ran before it (§11's isolation
property, §37).

**9. Ignoring flaky tests.**
*Why it happens:* rerunning until green feels faster than investigating.
*Why it's problematic:* trains a team to distrust red results,
potentially hiding a real, intermittent bug (§39). *Better approach:*
diagnose the actual source of nondeterminism (§38–§39) rather than
retrying blindly.

**10. Writing weak assertions.**
*Why it happens:* `assert result is not None` is quick to write and
"technically" checks something. *Why it's problematic:* provides a
false sense of coverage (§49, §53). *Better approach:* assert on the
specific, meaningful value or property the test claims to verify.

**11. Chasing coverage percentage.**
*Why it happens:* a coverage number is easy to measure and easy to
report. *Why it's problematic:* incentivizes weak, execute-but-don't-
verify tests written purely to move the number (§53). *Better
approach:* use coverage as a signal for *where gaps might exist*, never
as the actual measure of test quality.

**12. Using production services in tests.**
*Why it happens:* it can seem like the "most realistic" option. *Why
it's problematic:* risks real side effects, depends on an external
service's availability for your own suite's reliability, and can
violate terms of use (§26). *Better approach:* use a sandbox, fake, or
mock (§69), reserving real production calls for the safe, narrow
production-verification techniques in §70–§71.

**13. Creating huge, unfocused E2E suites.**
*Why it happens:* it can feel thorough to E2E-test every feature. *Why
it's problematic:* pays E2E's high cost (§58) repeatedly, for
confidence a cheaper test level often already provides, and creates a
slow, hard-to-maintain suite. *Better approach:* restrict E2E to
critical workflows (§47), pushing everything else down to unit/
integration.

**14. Ignoring cleanup.**
*Why it happens:* a test's own assertions feel like "the important
part," with cleanup seeming like an afterthought. *Why it's
problematic:* leaves real, leftover state that corrupts later test runs
(§37, §45). *Better approach:* use `yield`-based fixtures (§35, §45) so
teardown runs automatically, even when a test fails.

## 75. Complete Example Project

A realistic project — **"Order Management Service"** — shown
conceptually, demonstrating this entire chapter's structure applied to
one coherent system.

```
project/
├── src/
│   └── orders/
│       ├── __init__.py
│       ├── models.py        # Order, OrderItem — plain data structures
│       ├── service.py         # OrderService — business logic + orchestration
│       ├── repository.py       # OrderRepository — real database access
│       └── api.py                # HTTP layer — routes requests to OrderService
└── tests/
    ├── unit/
    │   └── test_service.py
    ├── integration/
    │   └── test_repository.py
    └── e2e/
        └── test_order_workflow.py
```

**One feature — "Create Order" — tested at all three levels:**

```python
# src/orders/service.py
class OrderService:
    def __init__(self, repository):
        self._repository = repository

    def create_order(self, customer_id: int, items: list[dict]) -> str:
        if not items:
            raise ValueError("order must have at least one item")
        total = sum(item["price"] * item["quantity"] for item in items)
        return self._repository.save_order(customer_id, items, total)
```

```python
# tests/unit/test_service.py
class StubRepository:
    def save_order(self, customer_id, items, total):
        self.last_total = total
        return "order-1"


def test_create_order_rejects_empty_items():
    service = OrderService(StubRepository())
    with pytest.raises(ValueError):
        service.create_order(customer_id=1, items=[])


def test_create_order_computes_total():
    repo = StubRepository()
    service = OrderService(repo)
    service.create_order(customer_id=1, items=[{"price": 9.99, "quantity": 2}])
    assert repo.last_total == 19.98
```

```python
# tests/integration/test_repository.py
def test_save_and_get_order(test_database):
    repository = OrderRepository(test_database)
    order_id = repository.save_order(1, [{"price": 9.99, "quantity": 2}], 19.98)
    saved = repository.get_order(order_id)
    assert saved.total == 19.98
```

```python
# tests/e2e/test_order_workflow.py
def test_create_order_via_api(running_app_client):
    response = running_app_client.post(
        "/orders", json={"customer_id": 1, "items": [{"price": 9.99, "quantity": 2}]}
    )
    assert response.status_code == 201
    assert response.json()["total"] == 19.98
```

Every piece of this project maps directly onto a concept this chapter
has covered: `models.py` holds pure data; `service.py` holds pure,
unit-testable business logic; `repository.py` is the integration
boundary (§22–§23); `api.py` is the E2E entry point (§27); and
`tests/` mirrors the exact three-way split §33 established.

## 76. Debugging Lab

Five realistic test failures. For each: symptoms, investigation, root
cause, solution, and prevention.

**1. A unit test failure.**
```python
def test_apply_discount():
    assert apply_discount(100.0, 10) == 91.0   # expected value looks wrong
```
*Symptoms:* `AssertionError: assert 90.0 == 91.0`. *Investigation:*
compare the test's expected value against the function's actual,
documented contract. *Root cause:* the test itself has the wrong
expected value — `100.0 * (1 - 10/100) == 90.0`, not `91.0`; this is a
bug in the *test*, not the code. *Solution:* correct the assertion to
`== 90.0`. *Prevention:* compute expected values independently (by
hand, or from the spec) rather than copying whatever the code
currently outputs.

**2. An integration test failure.**
```python
def test_save_order(test_database):
    repository = OrderRepository(test_database)
    repository.save_order(1, [], 0.0)
```
```
sqlite3.OperationalError: no such table: orders
```
*Symptoms:* a database error, not an assertion failure. *Investigation:*
check the fixture that's supposed to create the schema. *Root cause:*
the `test_database` fixture forgot to `CREATE TABLE orders` before
yielding the connection. *Solution:* add the missing schema-creation
statement to the fixture. *Prevention:* keep schema setup inside the
fixture itself (§23, §35), never assumed to exist from "somewhere else."

**3. An E2E test failure.**
```python
def test_create_order_via_api(running_app_client):
    response = running_app_client.post("/orders", json={"customer_id": 1, "items": [...]})
    assert response.status_code == 201
```
```
AssertionError: assert 500 == 201
```
*Symptoms:* an unexpected server error, not a validation failure.
*Investigation:* per §48, check application logs from each layer to
narrow down where the 500 originated. *Root cause:* the API layer was
passing `items` as a plain list where the service layer expected a list
of dicts with `"price"`/`"quantity"` keys — a wiring bug between two
already-individually-tested layers. *Solution:* fix the API layer's
request-parsing code to build the correct shape. *Prevention:* this is
precisely the class of bug E2E tests exist to catch (§27) — keep it in
the suite as a regression test (§52) going forward.

**4. Test data contamination.**
```python
def test_create_order_for_customer_1(test_database):
    ...  # creates a customer with id=1

def test_another_feature_for_customer_1(test_database):
    ...  # ALSO assumes customer id=1 doesn't already exist — fails intermittently
```
*Symptoms:* the second test passes when run alone, but fails when run
after the first. *Investigation:* run the tests in different orders and
individually, per §39's flaky-test diagnosis approach. *Root cause:*
both tests hardcode the same customer ID and share the same database
without cleanup — exactly §37's shared-state problem. *Solution:* use
unique, generated IDs per test, and ensure teardown removes what each
test creates. *Prevention:* fresh, isolated fixtures per test (§37,
§45–§46).

**5. Flaky behavior.**
```python
def test_process_order_id_is_recent():
    order_id = generate_order_id()   # includes a timestamp
    assert order_id.startswith(datetime.now().strftime("%Y%m%d"))
```
*Symptoms:* fails occasionally, seemingly at random, especially near
midnight. *Investigation:* review the test against §38's nondeterminism
sources — this one calls `datetime.now()` twice, once inside the code
under test and once inside the test itself, with a real (if small)
chance of the date rolling over between the two calls. *Root cause:*
current-time dependence without a controlled, injected clock.
*Solution:* inject a fixed, known `datetime` into both the function
under test and the assertion, rather than each independently calling
`datetime.now()`. *Prevention:* never let a test and the code it's
testing independently query "now" — control time explicitly (§38).

**6. An incorrect assertion (a weak-assertion bug).**
```python
def test_create_order():
    response = create_order(customer_id=1, items=[...])
    assert response is not None   # passes even if the order was created WRONG
```
*Symptoms:* the test passes, but a real bug (the wrong total being
saved) ships anyway. *Investigation:* the test "passed" — the
investigation here starts from a bug report, not a test failure, which
is itself the actual symptom of the problem. *Root cause:* the
assertion (§49) never checked anything specific about the *correctness*
of the response, only that *something* was returned. *Solution:*
rewrite the assertion to check the actual, expected total and fields.
*Prevention:* apply §49's habit directly — for every assertion, ask "if
the code were subtly wrong, would this actually catch it?"

## 77. Coding Exercises

### Level 1 — Basic

**1. Write a unit test.**
*Task:* write a `pytest` test for
`def square(n: int) -> int: return n * n`, verifying `square(4) == 16`.
*Hint:* follow §9's exact pattern. *Solution:*
```python
def test_square():
    assert square(4) == 16
```
*Explanation:* a pure function with no dependencies — the simplest
possible unit test.

**2. Identify unit vs. integration vs. E2E.**
*Task:* classify each: (a) testing `calculate_total([...])` directly;
(b) testing `OrderRepository.save_order` against a real database; (c)
testing a full `POST /orders` HTTP request. *Solution:* (a) unit; (b)
integration; (c) E2E. *Explanation:* scope (§6) is the deciding factor
in each case — one function in isolation, one real boundary, or the
whole chain.

**3. Create assertions.**
*Task:* write an assertion verifying `apply_discount(50.0, 50) == 25.0`.
*Solution:* `assert apply_discount(50.0, 50) == 25.0`. *Explanation:*
directly compares the actual return value to the specific expected
result (§5, §49).

**4. Test happy and invalid cases.**
*Task:* for `def validate_age(age: int) -> None: if age < 0: raise
ValueError(...)`, write one happy-path and one invalid-input test.
*Solution:*
```python
def test_validate_age_accepts_valid_age():
    validate_age(30)   # should not raise

def test_validate_age_rejects_negative_age():
    with pytest.raises(ValueError):
        validate_age(-1)
```

### Level 2 — Moderate

**5. Test a module with dependencies.**
*Task:* write a unit test for `OrderService.create_order` (§62) using a
stub repository, verifying the correct total is passed to
`save_order`. *Hint:* record the arguments the stub receives, per §17.
*Solution:* see §62's unit-test example directly. *Explanation:* the
stub isolates the service's own logic from any real persistence
concern.

**6. Create an integration test.**
*Task:* write an integration test for `OrderRepository.save_order`
against an in-memory SQLite database (§23), verifying a saved order can
be retrieved with the correct total. *Solution:* see §23's
`test_save_and_get_payment` pattern, adapted to `save_order`/`get_order`.

**7. Use a fixture.**
*Task:* write a `pytest` fixture providing a reusable, sample list of
order items, and use it in two different tests. *Solution:* see §35's
`sample_cart` fixture pattern directly.

**8. Test filesystem/database interaction.**
*Task:* write an integration test for a function that writes a report
to a file and reads it back, using `tmp_path`. *Solution:* see §24's
`test_save_and_load_report` example directly.

### Level 3 — Hard

**9. Design a multi-layer test strategy.**
*Task:* for a "user registration" feature (validation logic, a
repository, and an HTTP endpoint), decide what belongs at each test
level, and justify each choice. *Solution:* unit-test the validation
logic (email format, password strength) in isolation; integration-test
the repository against a real test database (does a user actually get
persisted correctly); E2E-test the full `POST /register` → confirmation
flow, since registration is a critical business workflow (§47, §59).

**10. Diagnose a flaky test.**
*Task:* given a test that occasionally fails with a "connection refused"
error, diagnose the likely cause and propose a fix. *Hint:* check §13's
"what unit tests should not depend on" and §38's nondeterminism sources.
*Solution:* the test is very likely making a real network call that
should either be replaced with a stub/fake (if it's meant to be a unit
test) or made more resilient and clearly classified as an integration
test with proper retry/timeout handling for the real service it depends
on.

**11. Separate unit/integration/E2E tests.**
*Task:* given a single, unsorted `tests/test_everything.py` file mixing
all three levels, propose the reorganized directory structure.
*Solution:* apply §33's structure — split into `tests/unit/`,
`tests/integration/`, and `tests/e2e/`, moving each existing test into
the directory matching its actual scope (§6).

**12. Improve a weak assertion.**
*Task:* rewrite `assert response is not None` (for a `POST /orders`
response) into a set of strong, meaningful assertions. *Solution:*
```python
assert response.status_code == 201
assert response.json()["order_id"] is not None
assert response.json()["total"] == expected_total
```
*Explanation:* directly applies §49's principle — verify the specific,
meaningful properties, not merely "something was returned."

### Level 4 — Advanced

**13. Design a production test architecture.**
*Task:* for a backend service, design the complete test-level and CI
strategy (unit/integration/E2E placement, CI stage ordering, execution
frequency). *Solution:* apply §59's strategy questions and §60–§61's
CI pipeline shape directly — unit tests on every save/PR, integration
tests on every PR, E2E tests on merge/nightly, matching §61's
reasoning about cost versus feedback speed.

**14. Create a CI testing strategy.**
*Task:* write out the CI pipeline stages, in order, for a project using
`uv`, Ruff, a type checker, and this chapter's three test levels.
*Solution:* see §60's full pipeline diagram directly, and justify the
ordering using its "cheap and fast before expensive and slow"
principle.

**15. Test a backend/data/ML system.**
*Task:* for a data pipeline with a parsing stage and a storage stage,
identify which parts are unit-testable and which need integration
tests. *Solution:* apply §63 directly — parsing/validation/
transformation are pure, unit-testable logic; storage is a genuine
integration boundary needing a real (test) destination.

**16. Design a testing strategy for an agentic AI workflow.**
*Task:* for the agent architecture in §66 (planner → tool selection →
tool execution → response), design what belongs at each test level, and
explain how nondeterminism is handled. *Solution:* unit-test
deterministic logic (tool selection when rule-based, prompt
construction, response parsing) with fixed inputs and fixed expected
outputs; integration-test real tool adapters; E2E-test the full
request-to-response path using behavioral assertions (§67) rather than
exact-match assertions, since the model's own output is nondeterministic.

## 78. Mini Project — Production-Ready Multi-Level Testing System

**Project**: design (conceptually, within this lesson — no files created
outside this document) a complete, multi-level test system for one
business feature: **"Apply Discount to Order."**

**Application code:**
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

**Unit tests** (`tests/unit/test_discount.py`) — what each verifies, and
why it belongs here: `apply_discount`'s own arithmetic, across happy
path, boundary (`0`, `100`), and invalid (`-1`, `101`) cases (§51) —
pure logic, no dependencies (§19), fastest possible feedback.
`OrderService.apply_order_discount`'s own orchestration logic, using a
stub repository (§16–§17) — verifies the service calls the repository
correctly and computes the right discounted total, without needing a
real database.

**Integration test** (`tests/integration/test_order_repository.py`) —
what it verifies: that `OrderRepository.update_total`, run against a
real (in-memory) test database, genuinely persists the new total
correctly (§23). Dependency used: a real, disposable SQLite database via
a `pytest` fixture (§35, §46).

**E2E test** (`tests/e2e/test_apply_discount_workflow.py`) — what it
verifies: a real `PATCH /orders/{id}/discount` request, against the
fully running application, correctly returns and persists the
discounted total (§27, §29). Dependency used: the complete, running
application stack (§44).

**Test fixtures and test data**: a `sample_order` fixture (§35)
providing a known order with a known total; an in-memory
`test_database` fixture (§23) for the integration and E2E layers.

**Configuration**: a `DISCOUNT_TEST_DB_URL` (or equivalent in-memory
default) used only by the integration/E2E layers, never containing real
production credentials (§41).

**CI test strategy**: unit tests run on every push; integration tests
run on every pull request; the E2E test runs on merge to the main
branch — directly applying §60–§61's reasoning about cost versus
feedback speed to this one, concrete feature.

This mini-project demonstrates the complete "one feature, three levels,
one CI strategy" shape this entire chapter has built toward, applied
consistently and end to end.

## 79. Interview Questions

**Beginner**

- *What is software testing?* Running code deliberately with known
  inputs and comparing the actual result to an expected one (§1).
- *What is a unit test?* A test verifying one small unit — typically a
  function or method — in isolation from its real dependencies (§7–§8).
- *What is an integration test?* A test verifying that components interact
  correctly across a meaningful boundary (§20).
- *What is an E2E test?* A test verifying a complete workflow, from a
  request through the major application layers to the final observable
  result (§27).
- *What is an assertion?* A statement declaring "this must be true,"
  raising an error immediately if it isn't (§5).

**Intermediate**

- *Unit vs. integration?* Scope and dependency reality — a unit test
  isolates one piece of logic with controlled dependencies; an
  integration test verifies a real interaction with a real dependency
  (§21).
- *Why isolate unit tests?* For speed, reliability, determinism, and
  precise failure diagnosis (§13–§14).
- *Why use integration tests?* Because a unit test's stubbed
  dependencies prove nothing about whether the real interaction
  actually works (§20).
- *What causes flaky tests?* Nondeterminism — unseeded randomness,
  real time, real network calls, concurrency, or shared state (§38–§39).
- *What is the test pyramid?* A heuristic: many fast unit tests, fewer
  integration tests, fewer still E2E tests — justified by speed, cost,
  feedback, and maintenance, not an absolute law (§30).

**Advanced**

- *How do you decide which test level to use?* By identifying whether
  the behavior is pure logic (unit), a real boundary (integration), or
  a critical, complete workflow (E2E) — formalized as a test strategy
  (§59).
- *How do you test database interactions?* With a real (often
  lightweight/disposable) test database, using transaction rollback or
  isolated data per test (§23, §46).
- *How do you test external APIs?* Prefer a sandbox or a realistic test
  double over the real production service; never call a live production
  external service from ordinary tests (§25–§26, §69).
- *How do you prevent test coupling?* Assert on observable behavior, not
  internal implementation mechanics (§55–§56).
- *How do you design CI test stages?* Cheap, fast checks first (Ruff,
  types, unit tests), progressively more expensive checks later
  (integration, then E2E), gating the pipeline on each stage's success
  (§60).

**Production**

- *Design a testing strategy for a large backend system.* Apply §59's
  questions: unit-test business logic, integration-test each real
  boundary, E2E-test critical workflows only, weighted by failure cost.
- *Design testing for a data pipeline.* Unit-test parsing/validation/
  transformation as pure functions; integration-test the storage
  boundary; E2E-test the full pipeline against a real input file and
  real (test) storage (§63).
- *Design testing for an ML inference service.* Unit-test preprocessing
  and the model wrapper (using a fake model); integration/E2E-test the
  inference API's request/response shape — while keeping model-quality
  evaluation entirely separate from this software-testing activity
  (§64).
- *Design testing for an agentic AI system.* Unit-test deterministic
  logic (tool selection, prompt construction, parsing) with fixed
  inputs; integration-test real tool adapters; E2E-test the full
  request-to-response path with behavioral, not exact-match, assertions
  (§66–§67).
- *How do you balance unit, integration, and E2E tests?* Use the test
  pyramid as a starting heuristic, then adjust based on the specific
  system's actual architecture and where its real risk concentrates
  (§30–§31, §59).

## 80. Architecture Questions

- **How should tests be organized in a large Python repository?**
  Mirror the source tree under a top-level `tests/` directory, split
  by level (`unit/`, `integration/`, `e2e/`) so both a human and CI can
  reliably select a subset by directory (§33).
- **Where should integration infrastructure live?** As disposable,
  test-scoped fixtures wherever practical (in-memory databases,
  temporary directories, ephemeral local servers) rather than a shared,
  persistent environment multiple test runs could silently collide on
  (§43, §46).
- **How should test environments be isolated?** Each test run should get
  its own fresh, disposable state (a fresh in-memory database, a fresh
  temporary directory) rather than sharing mutable infrastructure across
  runs or across developers (§37, §40, §46).
- **How should CI execute different test levels?** Fast, cheap layers
  first, gating progressively more expensive layers, exactly per §60's
  pipeline — with integration/E2E potentially running less frequently
  than unit tests, per §61's execution-strategy reasoning.
- **How should E2E tests be selected?** By business criticality (§47),
  not exhaustiveness — a small, deliberately chosen set of workflows
  whose failure would matter most, not every possible path through the
  system (§58–§59).
- **How should an AI platform test model-provider integrations?**
  Unit-test the client code against fixed, known response fixtures
  (§65); integration-test against a sandbox where the provider offers
  one; reserve real, live-provider calls for a small, deliberately
  chosen set of E2E/smoke checks, using behavioral assertions (§67, §71).
- **How should an agent system be tested across orchestration and
  tools?** Unit-test each tool's own logic and any deterministic
  orchestration logic independently; integration-test real tool
  adapters; E2E-test the complete user-request-to-response path with
  assertions tolerant of the model's own nondeterminism (§66–§67).

## 81. Knowledge Check

1. What is the difference between a test and a test case?
2. What four steps does "give input → execute behavior → observe result
   → compare with expectation" describe?
3. How does testing differ from debugging?
4. What are the three stages of Arrange-Act-Assert?
5. What's the difference between a strong assertion and a weak one?
6. Why is there no single universal definition of "a unit"?
7. Name three characteristics of a strong unit test.
8. What kinds of dependencies should a unit test generally avoid?
9. What is the difference between a mock, a fake, and a stub?
10. What is over-mocking, and why is it a problem?
11. What is the difference between a pure function and an impure one?
12. What does an integration test verify that a unit test cannot?
13. Name three integration boundaries.
14. What does an E2E test verify that neither a unit nor an integration
    test can?
15. Is the test pyramid an absolute law? Why or why not?
16. What is the difference between a test suite and a test layer?
17. Why should test names communicate behavior?
18. What is a `pytest` fixture, and why is it useful?
19. What is the difference between minimal, realistic, boundary, and
    invalid test data?
20. What is test isolation, in the "tests interfering with each other"
    sense?
21. What is a deterministic test, and name two sources of
    nondeterminism.
22. What is a flaky test, and why shouldn't it just be rerun until
    green?
23. What is a regression test, and when is one commonly written?
24. Why doesn't high test coverage guarantee high-quality testing?
25. What is the difference between testing behavior and testing
    implementation details?
26. Why should E2E tests focus on critical workflows rather than
    everything?
27. In a CI pipeline, why do fast checks typically run before slow
    ones?
28. What is the key difference between testing software behavior and
    evaluating ML model quality?
29. Why are exact-match assertions often inappropriate for real LLM
    output?
30. What is a smoke test, and how does it differ from a full test
    suite?

**Answers**

1. A test is one executable check; a test case is the specific
   scenario (input + expectation) it represents (§1, §4).
2. The basic mechanics of any test, regardless of level (§1).
3. Testing asks "does this behave as expected"; debugging asks "why is
   this behaving incorrectly" (§3).
4. Arrange (set up), Act (execute), Assert (check the result) (§4).
5. A strong assertion checks a specific, meaningful value; a weak one
   checks only broad presence/absence, like `is not None` (§5, §49).
6. Because what counts as "a unit" is a judgment call shaped by a
   project's own architecture, not a fixed, universal rule (§7).
7. Any three of: fast, isolated, deterministic, focused, repeatable,
   readable (§11).
8. Real databases, real external APIs, network services, cloud
   services, production infrastructure (§13).
9. A stub returns a fixed value; a fake has a real, simplified working
   implementation; a mock additionally records how it was called (§16).
10. Mocking so heavily that tests become brittle, coupled to
    implementation, and can pass while the real system fails (§18).
11. A pure function always returns the same output for the same input
    with no side effects; an impure function has a side effect
    (writes, network calls, mutation) (§19).
12. That a real interaction with a real dependency actually works, not
    merely that code calls a stand-in correctly (§20–§21).
13. Any three of: application↔database, application↔filesystem,
    application↔API, service↔queue, pipeline↔object storage (§22).
14. That the entire, wired-together system produces the correct result
    for a real request, including how the layers are actually
    connected (§27–§28).
15. No — it's a heuristic; architecture can justify a different
    distribution (§30–§31).
16. A test suite is a collection of tests run together; a test layer is
    a category of tests grouped by scope (unit/integration/E2E) (§32).
17. So a failure's name alone communicates what behavior broke, without
    needing to open the file (§34).
18. Reusable setup (and teardown) logic a test can request rather than
    repeating by hand (§35).
19. Minimal isolates one specific case; realistic resembles real usage;
    boundary sits at valid/invalid edges; invalid should be rejected
    (§36).
20. Tests unintentionally affecting each other's results via shared
    files, database rows, global state, or environment variables (§37).
21. A test producing the same result every run; sources include current
    time, randomness, network, concurrency, and shared state (§38).
22. A test that intermittently passes/fails with no code change;
    retrying blindly can hide a genuine, intermittent bug rather than
    fixing it (§39).
23. A test written specifically because a real bug was found, kept
    permanently to prevent that exact bug from silently reappearing
    (§52).
24. Coverage measures whether a line was *executed*, not whether it was
    *meaningfully verified* by a real assertion (§53).
25. Testing behavior verifies observable outcomes; testing
    implementation details asserts on internal mechanics, producing
    fragile tests (§55–§56).
26. Because E2E tests are the slowest and most expensive test level per
    test; that cost is best spent where it matters most (§47, §58).
27. To give the fastest possible feedback on the most common problems
    before spending time/infrastructure on slower, more expensive
    checks (§60).
28. Software behavior testing verifies the *code* around a model is
    correct; model-quality evaluation verifies the *model's own
    predictions* are good — a fundamentally different activity (§64).
29. Because a real model's output is frequently nondeterministic; a
    behavioral assertion (checking key properties) is more robust than
    an exact string match (§67).
30. A smoke test is a small, fast, safe check confirming a freshly
    deployed system isn't catastrophically broken; it does not replace
    a full pre-production test suite (§71).

## 82. Glossary

- **Test** — one specific, executable check comparing actual behavior
  to expected behavior.
- **Test case** — the specific input/expectation scenario a test
  represents.
- **Assertion** — a statement declaring something must be true, failing
  immediately if it isn't.
- **Unit test** — a test verifying one small unit in isolation from its
  real dependencies.
- **Integration test** — a test verifying that components interact
  correctly across a meaningful boundary.
- **End-to-end (E2E) test** — a test verifying a complete, representative
  workflow, from request to final observable result, through the major
  application layers.
- **Test suite** — a collection of tests run together.
- **Fixture** — reusable setup (and teardown) logic a test can request.
- **Mock** — a controlled stand-in that also records how it was called.
- **Fake** — a stand-in with a real, simplified working implementation.
- **Stub** — a stand-in returning a fixed, predetermined value.
- **Test double** — the general term covering mocks, fakes, and stubs
  collectively.
- **Isolation** — a test's independence from real external dependencies
  and/or from other tests' state.
- **Deterministic test** — a test producing the same result every run.
- **Flaky test** — a test that intermittently passes and fails with no
  code change.
- **Regression test** — a test protecting previously working behavior
  from being unintentionally broken again; commonly written after a real
  bug is found and kept permanently.
- **Test coverage** — the measured proportion of code (lines/branches)
  actually executed by a test suite.
- **Test pyramid** — the heuristic that a healthy suite has many unit
  tests, fewer integration tests, and fewer still E2E tests.
- **Smoke test** — a small, fast, safe check confirming a freshly
  deployed system isn't catastrophically broken.
- **Test environment** — the context (local, CI, staging, production)
  a test or system runs in.
- **Test data** — the specific input values a test uses.
- **Contract (testing)** — a recorded statement of what one service
  expects from another, checkable independently on each side.
- **E2E** — abbreviation for end-to-end.
- **CI/CD** — Continuous Integration / Continuous Deployment; the
  automated pipeline that runs tests (and other checks) on every code
  change.

## 83. Final Mental Model

```
UNIT TESTS
    ↓
"Does this small piece of logic work?"

INTEGRATION TESTS
    ↓
"Do these components work together?"

END-TO-END TESTS
    ↓
"Does the complete user/business workflow work?"
```

- **Unit tests provide fast feedback** — milliseconds, isolated,
  precise about exactly what broke.
- **Integration tests validate boundaries** — do the real database,
  filesystem, or API interactions your code depends on actually work.
- **E2E tests validate critical workflows** — does the entire,
  wired-together system correctly serve the handful of journeys that
  matter most.

And the two governing principles this entire chapter has built toward:

- **Testing verifies behavior. Debugging investigates failures.** They
  are distinct, complementary activities (§3) — testing detects that
  something is wrong; debugging finds out why.
- **Good test strategy uses the right level for the right risk.** Not
  "as many tests as possible," and not "the most realistic test
  possible for everything" — a deliberate match between a behavior's
  actual risk and the cheapest test level that can genuinely verify it
  (§59).

## Final Takeaways

- A test is a repeatable procedure — input, execution, observation,
  comparison — that turns "I believe this works" into "here is what was
  actually checked, and it passed" (§1–§2).
- Testing and debugging are different activities working together:
  testing detects that something is wrong; debugging investigates why
  (§3).
- A unit is not universally one function — it's whatever small,
  isolated piece of logic a project reasonably tests on its own, with
  its dependencies controlled (§7–§19).
- Integration tests exist specifically to verify what a unit test's
  controlled dependencies cannot: that a real interaction with a real
  boundary genuinely works (§20–§26).
- E2E tests verify the entire, wired-together system serves a real
  workflow correctly — and are worth their high cost specifically for a
  system's most critical journeys, not everything it can do (§27,
  §47, §58).
- The test pyramid is a heuristic, not a law — many fast unit tests,
  fewer integration tests, fewer still E2E tests, adjusted for a
  project's actual architecture (§30–§31).
- A test's value comes from what it actually verifies — meaningful
  assertions, real isolation, genuine determinism — not from its mere
  existence, its coverage percentage, or how "realistic" it looks
  (§49, §53–§54).
- Good tests verify observable behavior, not internal implementation —
  a test that breaks on every harmless refactor has been coupled to the
  wrong thing (§55–§56).
- A deliberate test strategy — matching unit, integration, and E2E to
  actual logic, actual boundaries, and actual critical workflows — beats
  either testing everything the same way or testing by habit (§59).
- Backend services, data pipelines, ML systems, and agentic AI systems
  all use the exact same three test levels — the only genuinely new
  consideration AI/ML systems add is separating deterministic software
  correctness from nondeterministic model output, and evaluating each
  with the right tool for what it actually is (§64–§67).






