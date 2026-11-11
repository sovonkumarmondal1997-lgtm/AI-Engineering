# Practice Questions — Module 1.24: Functions and OOP Gap Lessons

**Target:** Python 3.12+ · **Question set:** 40 questions · **Suggested time:** 4–6 focused sessions

## 1. Assessment instructions

Attempt Sections A and B before reading the answer key. For code questions, write the smallest clear implementation that meets the contract, then add tests. For design questions, explain the trade-offs rather than naming a pattern without justification. Unless a question says otherwise, assume Python 3.12+ and ordinary CPython semantics; avoid relying on memory addresses or timing.

Suggested workflow:

1. Answer each question in a separate file or notebook cell.
2. For tracing questions, predict the exact output before running the code.
3. For coding questions, write tests for normal inputs, boundaries, and invalid inputs.
4. Review your answers against the key only after completing a section.
5. Record the lesson numbers for any missed concept and revisit that lesson.

## 2. Module scope and difficulty legend

The source roadmap describes Module 1.24 as a gap-filling and consolidation module: Lessons 01–07 focus on functions and callables; Lessons 08–10 build class, construction, and inheritance fundamentals; Lesson 11 consolidates class design review. Advanced metaclasses, descriptors, and deep MRO internals belong to later modules and are intentionally not required here.

- **Beginner:** explain a core concept, trace a short snippet, or make a local correction.
- **Intermediate:** combine concepts, implement a reusable helper, or test behavior and edge cases.
- **Advanced:** reason about API design, state, compatibility, production constraints, or refactoring trade-offs.

The eight output-prediction questions are marked **OUTPUT PREDICTION** and indexed again after Section B.

---

## 3. Section A — Functions: Questions 1–20 (Lessons 01–07)

### Q1 — Functions as values and dispatch tables
**Difficulty:** Beginner · **Lesson:** 01

A data pipeline supports `"trim"`, `"lower"`, and `"upper"` operations. Write a typed `transform(text: str, operation: str) -> str` using a dispatch dictionary of module-level functions rather than a long `if/elif` chain. Unknown operation names must raise a `ValueError` with the unknown name in the message. Include two tests.

### Q2 — Callback registration versus callback invocation
**Difficulty:** Beginner · **Lesson:** 01

A scheduler API accepts `Callable[[], None]`. A developer writes `register(cleanup())` instead of `register(cleanup)`. Explain the semantic difference, identify when each form is correct, and show a minimal test that proves registration does not run the callback immediately.

### Q3 — Bound methods and callable inspection
**Difficulty:** Intermediate · **Lesson:** 01

Given:

```python
class Exporter:
    def export(self, rows: list[str]) -> int:
        return len(rows)

exporter = Exporter()
handler = exporter.export
```

Explain what `handler.__self__` and `handler.__func__` refer to, why `callable(handler)` is true, and how to invoke the underlying function explicitly with `exporter`. State why code should generally prefer `handler(rows)` over manually calling `__func__`.

### Q4 — Lambda readability and operator helpers
**Difficulty:** Beginner · **Lesson:** 02

Rewrite `sorted(records, key=lambda row: row["timestamp"])` using an appropriate standard-library helper. Then consider `lambda record: normalize(record["email"])`. Explain when a named `def` is preferable, including debugging and type/documentation considerations.

### Q5 — OUTPUT PREDICTION: closure counter
**Difficulty:** Beginner · **Lesson:** 03

What does this print? Explain which variable is retained and why the two calls share state.

```python
def make_counter():
    count = 0

    def increment():
        nonlocal count
        count += 1
        return count

    return increment

counter = make_counter()
print(counter(), counter(), counter())
```

### Q6 — Closure versus callable class
**Difficulty:** Intermediate · **Lesson:** 03, 06

Implement `make_threshold(minimum: int) -> Callable[[int], bool]`, returning a predicate that checks whether a value is at least `minimum`. Then describe two signs that would justify replacing this closure with a callable class. Include tests for values below, equal to, and above the threshold.

### Q7 — OUTPUT PREDICTION: late-bound loop lambdas
**Difficulty:** Beginner · **Lesson:** 04

What does this print in Python 3.12+? Explain the result, then show two correct ways to produce multipliers for 1, 2, and 3.

```python
functions = [lambda value: value * n for n in range(1, 4)]
print([fn(10) for fn in functions])
```

### Q8 — `nonlocal`, `global`, and `UnboundLocalError`
**Difficulty:** Intermediate · **Lesson:** 04

Diagnose this code without running it first:

```python
total = 10

def add_to_total(amount: int) -> int:
    total += amount
    return total
```

Why does it fail? Give one solution that intentionally updates module state and one preferable solution that returns a new value without global mutation. Explain the role of `nonlocal` in a nested function and why it does not solve this module-level example.

### Q9 — OUTPUT PREDICTION: mutable default argument
**Difficulty:** Beginner · **Lesson:** 04, 07

What does this print, and how should the function be corrected?

```python
def append_tag(tag: str, tags: list[str] = []) -> list[str]:
    tags.append(tag)
    return tags

print(append_tag("raw"))
print(append_tag("clean"))
print(append_tag("ready", []))
```

### Q10 — Choosing comprehensions, `map`, `filter`, and `reduce`
**Difficulty:** Intermediate · **Lesson:** 05

Given `values = [3, -2, 0, 5, -1]`, produce a list of squares of positive values. Show the clearest implementation using a comprehension, and then an equivalent `map`/`filter` version. Explain why `reduce` is not the best tool here. Include an empty-input test.

### Q11 — Stable sorting and mixed-direction keys
**Difficulty:** Intermediate · **Lesson:** 05

Each record is a dictionary with `"team"`, `"score"`, and `"player"`. Sort by team ascending, score descending, and player ascending as a deterministic tie-breaker. Explain stability and why `reverse=True` on a single tuple key would reverse every component. Provide a test with ties.

### Q12 — Implement and test `top_k`
**Difficulty:** Advanced · **Lesson:** 05, 07

Implement `top_k(items, k, *, key=None, reverse=False)` with type hints and `heapq`. Match the observable ordering of `sorted(items, key=key, reverse=reverse)[:k]`: with the default `reverse=False`, return the first `k` items in ascending key order; with `reverse=True`, return the first `k` in descending key order. Reject negative `k` with `ValueError`, reject non-integer `k` with `TypeError`, return `[]` for `k == 0`, do not mutate the input, and return all items in the selected order when `k` exceeds the input length. Explain and test tie stability. Include empty-input and `key=None` cases.

### Q13 — OUTPUT PREDICTION: class attribute shadowing
**Difficulty:** Beginner · **Lesson:** 08

What does this print? Explain the class attribute, instance lookup, and shadowing.

```python
class Pipeline:
    mode = "batch"

first = Pipeline()
second = Pipeline()
first.mode = "stream"
print(Pipeline.mode, first.mode, second.mode)
```

### Q14 — OUTPUT PREDICTION: invalid `__init__` return
**Difficulty:** Intermediate · **Lesson:** 09

What happens when this code runs? Name the exception type and explain why `__init__` is not a factory return method.

```python
class BadConfig:
    def __init__(self, value: int) -> None:
        self.value = value
        return self

config = BadConfig(3)
```

### Q15 — Callable object, `partial`, or closure?
**Difficulty:** Advanced · **Lesson:** 01, 03, 06

A pipeline repeatedly applies a configurable scale factor. Compare a plain function, `functools.partial`, a closure, and a callable class. Recommend one for (a) a one-off fixed factor, (b) a private one-method configured predicate, and (c) a stateful transformer with public configuration and a call counter. Justify the trade-offs and show one typed implementation.

### Q16 — Injecting time into a retry policy
**Difficulty:** Advanced · **Lesson:** 06, 07

Design a small retry helper whose waiting behavior is testable without real sleeps. It must accept a callable operation, a maximum attempt count, and injected `sleep` and `clock` dependencies (or explain why a clock is not needed for your exact policy). Define what happens when the operation succeeds, fails repeatedly, or receives an invalid attempt count. Provide a fake-based test; do not use timing-dependent sleeps.

### Q17 — Function API review: purity and error handling
**Difficulty:** Intermediate · **Lesson:** 07

Review this function:

```python
def normalize_rows(rows, cache={}):
    result = []
    for row in rows:
        row["email"] = row["email"].strip().lower()
        cache[row["id"]] = row
        result += [row]
    return result
```

Identify at least four design defects. Refactor it so input mappings are not mutated, shared default state is removed, the output contract is typed, and missing or malformed email data produces a clear error. Provide tests for input preservation and invalid input.

### Q18 — OUTPUT PREDICTION: bound-method identity and equality
**Difficulty:** Advanced · **Lesson:** 01, 06

What does this print on Python 3.12+? Explain why identity and equality differ for repeated bound-method access.

```python
class Worker:
    def run(self) -> None:
        pass

worker = Worker()
print(worker.run is worker.run)
print(worker.run == worker.run)
```

### Q19 — Picklability and execution boundaries
**Difficulty:** Advanced · **Lesson:** 02, 06

A task is submitted to a process pool on a supported platform. Explain why a lambda or a nested closure is often unsuitable as a submitted target, while an importable module-level function or suitable callable instance can work. Give a portable design recommendation and distinguish serialization constraints from ordinary in-process thread execution.

### Q20 — Function refactoring plan and evidence
**Difficulty:** Advanced · **Lesson:** 07

A 90-line function reads a file, parses records, validates business rules, formats errors, and writes a report. Propose a safe sequence of at least five refactoring steps. For each step, name a test or evidence to collect. Include purity, dependency injection, error behavior, complexity/performance measurements, and a rule for deciding when to stop refactoring.

---

## 4. Section B — Classes: Questions 21–40 (Lessons 08–11)

### Q21 — Class versus instance fundamentals
**Difficulty:** Beginner · **Lesson:** 08

Write an `Account` class with a validated owner name and non-negative opening balance. Each instance must have independent balance state. Demonstrate two instances and explain `self`, `type(account)`, and `isinstance(account, Account)`. Include tests that prevent a negative opening balance.

### Q22 — Encapsulation and invariants
**Difficulty:** Intermediate · **Lesson:** 08, 11

Design a `JobQueue` that stores jobs privately, exposes a read-only snapshot, and provides `enqueue` and `dequeue` methods. State its invariants and explain how returning the internal list would let callers break them. Include tests for empty dequeue and external mutation of the returned snapshot.

### Q23 — OUTPUT PREDICTION: copying versus calling `__init__` again
**Difficulty:** Advanced · **Lesson:** 08, 09

What does this print? Explain the difference between constructing a new object, copying an object, and manually calling `__init__` again. Why is the last action usually a design smell?

```python
import copy

class Box:
    def __init__(self, items: list[str]) -> None:
        self.items = items

original = Box(["a"])
cloned = copy.copy(original)
original.__init__(["b"])
print(original.items, cloned.items, original is cloned)
```

### Q24 — OUTPUT PREDICTION: `super()` constructor chaining
**Difficulty:** Intermediate · **Lesson:** 10

What does this print, in order? Explain why `super()` means “next implementation in the MRO,” not a hard-coded parent call.

```python
class Base:
    def __init__(self) -> None:
        print("Base")
        super().__init__()

class Child(Base):
    def __init__(self) -> None:
        print("Child")
        super().__init__()

Child()
```

### Q25 — `__new__` versus `__init__`
**Difficulty:** Intermediate · **Lesson:** 09

Explain the ordinary class-call sequence involving `__new__` and `__init__`. Why must `__init__` return `None`? Give a valid use case for overriding `__new__` and one reason ordinary application classes should usually not override it.

### Q26 — Alternative constructors and boundary parsing
**Difficulty:** Intermediate · **Lesson:** 09

Implement a `Config` class that validates a non-empty `environment` and a positive integer `batch_size`. Add `@classmethod from_dict(cls, data: Mapping[str, object]) -> Config`, translating missing or invalid fields into a helpful `ValueError`. Keep parsing separate from the invariant-enforcing constructor. Test both valid and invalid dictionaries.

### Q27 — Immutable built-in subclass
**Difficulty:** Advanced · **Lesson:** 09

Implement `Celsius(float)` so that construction rejects temperatures below absolute zero (`-273.15 °C`). Explain why validation must occur in `__new__` for an immutable `float` subclass, and provide tests for the lower boundary and an invalid value.

### Q28 — Overriding and substitutability
**Difficulty:** Intermediate · **Lesson:** 10

A base `Notifier.send(message: str) -> bool` returns whether delivery succeeded. A subclass overrides `send` but raises an exception for messages the base accepts and changes the return type to `None`. Explain the substitutability problem and write a contract test pattern that every notifier implementation should satisfy.

### Q29 — Composition versus inheritance
**Difficulty:** Advanced · **Lesson:** 10, 11

A notification system has `EmailRetryingUrgentNotifier`, `EmailRetryingNotifier`, `SmsRetryingUrgentNotifier`, and similar subclasses for every combination of transport, retry policy, and urgency. Sketch a composition-based design with a `Transport` protocol, a retry policy dependency, and an urgency/configuration value. Discuss the trade-offs and how you would test each collaborator.

### Q30 — Dataclass versus handwritten value object
**Difficulty:** Intermediate · **Lesson:** 08, 11

Model `Money` with amount and currency. Define equality semantics and a clear invariant that the currency is non-empty and normalized. Compare a frozen dataclass with a handwritten class. State when generated equality is suitable and why a mutable object with custom equality should not casually be hashable. Provide tests for equality and invalid currency.

### Q31 — Dependency injection and protocols
**Difficulty:** Advanced · **Lesson:** 06, 11

A `ReportService` needs a clock and a report writer. Define small `Protocol` interfaces and inject both dependencies through the constructor. Demonstrate a fake clock and fake writer in a test. Explain why constructing concrete network/database clients inside `ReportService.__init__` makes testing and configuration harder.

### Q32 — Diagnose shared mutable class state
**Difficulty:** Intermediate · **Lesson:** 08, 11

Explain why two instances of this class can observe the same entries after only one instance calls `add`. Identify the shared mutable-state defect and correct it.

```python
class Registry:
    entries: list[str] = []

    def add(self, entry: str) -> None:
        self.entries.append(entry)

first = Registry()
second = Registry()
first.add("alpha")
print(first.entries, second.entries)
```

### Q33 — Equality, identity, representation, and hashing
**Difficulty:** Advanced · **Lesson:** 08, 11

For a value object `Point(x, y)`, explain when `p1 == p2` should be true even if `p1 is p2` is false. Propose a useful `repr`. State the relationship between equality and hashing and explain why a mutable point that changes its hash fields after insertion into a set is unsafe.

### Q34 — Resource lifecycle and state transitions
**Difficulty:** Advanced · **Lesson:** 11

Design a small `Job` state model with allowed transitions `pending → running → succeeded|failed`. Reject illegal transitions without corrupting state. Explain how idempotent transition operations should behave and what additional considerations arise if transitions trigger I/O or async cancellation. Include tests for valid and invalid transitions.

### Q35 — Constructor chaining and parent invariants
**Difficulty:** Intermediate · **Lesson:** 09, 10

A `SavingsAccount` subclasses `Account`, whose constructor validates the owner and initial balance. The child adds a non-negative interest rate. Show a correct constructor that preserves the parent invariant using `super()`. Then explain the defect caused by omitting parent initialization and how tests detect it.

### Q36 — Distinguish construction from instance invocation
**Difficulty:** Advanced · **Lesson:** 06, 09

Trace the two different call protocols in this snippet. Identify which expression creates an instance and which invokes an already-created object's `__call__`; explain the event order.

```python
class Multiplier:
    def __init__(self, factor: int) -> None:
        print("init")
        self.factor = factor

    def __call__(self, value: int) -> int:
        print("call")
        return self.factor * value

multiply_by_three = Multiplier(3)
print(multiply_by_three(4))
```

### Q37 — Test shallow-copy aliasing
**Difficulty:** Advanced · **Lesson:** 09, 11

Explain why `copy.copy` does not call `__init__` again and why the copied list is initially aliased. Write two assertions that demonstrate the outer objects are distinct but their `rows` attributes initially refer to the same list.

```python
import copy

class Batch:
    def __init__(self, rows: list[int]) -> None:
        self.rows = rows
        print("initialized")

source = Batch([1, 2])
clone = copy.copy(source)
assert source is not clone
assert source.rows is clone.rows
clone.rows.append(3)
assert source.rows == clone.rows == [1, 2, 3]
```

### Q38 — Type design and public API evolution
**Difficulty:** Advanced · **Lesson:** 11

A public class currently has `Processor(path, mode, retry, timeout)` with four positional parameters. Propose a backward-compatible evolution toward a configuration object or keyword-only options. Explain how `Protocol`, `Literal` or an enum, and `@override` can help without making typing a substitute for runtime validation. Include a migration and deprecation plan.

### Q39 — Class review checklist and severity
**Difficulty:** Advanced · **Lesson:** 11

Review this illustrative class (it is a teaching example, not source code from an earlier project):

```python
class Manager:
    cache = {}

    def __init__(self, client, items=[]):
        self.client = client
        self.items = items

    def run(self, data):
        self.client.save(data)
        self.cache[data["id"]] = data
        self.items.append(data)
        return data["status"]
```

Identify at least five findings, rank them by severity, and recommend fixes and tests. Distinguish correctness risks from maintainability improvements. Explain whether the class should necessarily be deleted or renamed.

### Q40 — Joint function-and-class review / mini-project plan
**Difficulty:** Advanced · **Lesson:** 07, 11 (module capstone)

Plan the complete roadmap `gapcheck` mini-project. Include `compose`, `pipe`, closure-based `once` and `memoize`, late-binding-safe `bind_loop`, `top_k(items, k, key=...)`, a callable `RetryPolicy`, a `RateLimiter` with injected clock, `partial`-based adapters, `Money`, `Account`/`SavingsAccount` with constructor chaining and template-method/contract tests, `Celsius(float)`, and `Config.from_env`/`Config.from_dict`. Specify module boundaries; at least eight test categories; CI gates for Ruff (including applicable `B023`, `E731`, `PLR`, `C901`, and `FBT` rules), strict mypy, pytest, and a project branch-coverage target of at least 90%. Explain how each late-binding and construction pitfall will have a failing-then-passing regression test. Plan a `REVIEW.md` for two functions and two classes from an available Stage 1 project, with prioritized findings, before/after code, metrics, and at least eight small commits. If source code is unavailable, label substitute examples as illustrative and document the evidence gap rather than claiming to have audited unseen code.

---

## 5. Eight-question output-prediction index

| Question | Required topic | Lesson |
|---|---|---|
| Q5 | Closure counter and `nonlocal` | 03 |
| Q7 | Loop lambdas and late binding | 04 |
| Q9 | Mutable default argument | 04, 07 |
| Q13 | Class-attribute shadowing | 08 |
| Q14 | Invalid `__init__` return value | 09 |
| Q24 | `super()` constructor call order | 10 |
| Q18 | Bound-method identity and equality | 01 |
| Q23 | Copying versus manually invoking `__init__` | 08–09 |

Q37 reinforces shallow-copy aliasing through assertions, but is a coding/design question rather than an additional output-prediction item.

---

# 6. Answer key and explanations

## Functions answers (Q1–Q20)

### A1 — Dispatch table

```python
from collections.abc import Callable


def trim(text: str) -> str:
    return text.strip()


def lower(text: str) -> str:
    return text.lower()


def upper(text: str) -> str:
    return text.upper()


TRANSFORMS: dict[str, Callable[[str], str]] = {
    "trim": trim,
    "lower": lower,
    "upper": upper,
}


def transform(text: str, operation: str) -> str:
    try:
        fn = TRANSFORMS[operation]
    except KeyError:
        raise ValueError(f"unknown operation: {operation!r}") from None
    return fn(text)
```

Tests:

```python
def test_transform_dispatch() -> None:
    assert transform(" Hi ", "trim") == "Hi"
    assert transform("Hi", "lower") == "hi"


def test_transform_unknown_operation() -> None:
    import pytest
    with pytest.raises(ValueError, match="missing"):
        transform("x", "missing")
```

The dictionary stores function objects, not their results. `trim` is a callable value; `trim(text)` is a call.

### A2 — Register versus invoke

`register(cleanup)` passes the function object for later use. `register(cleanup())` invokes it immediately and passes its return value. A minimal proof:

```python
from collections.abc import Callable


def register(callback: Callable[[], None], callbacks: list[Callable[[], None]]) -> None:
    callbacks.append(callback)


def test_register_defers_callback() -> None:
    calls: list[str] = []

    def cleanup() -> None:
        calls.append("ran")

    callbacks: list[Callable[[], None]] = []
    register(cleanup, callbacks)
    assert calls == []
    callbacks[0]()
    assert calls == ["ran"]
```

### A3 — Bound methods

`handler.__self__` is `exporter`; `handler.__func__` is the function object `Exporter.export`. `handler(rows)` binds the stored instance automatically. Explicit low-level invocation is `Exporter.export(exporter, rows)`, but ordinary code should use the bound method because it is clearer and preserves normal binding behavior.

### A4 — Lambda and `operator`

```python
from operator import itemgetter

sorted_records = sorted(records, key=itemgetter("timestamp"))
```

For nontrivial normalization, use a named function, e.g.:

```python
def normalized_email(record: dict[str, str]) -> str:
    """Return the normalized email field."""
    return normalize(record["email"])
```

Named functions are easier to document, annotate, debug, reuse, and inspect in tracebacks. `itemgetter` makes the simple field-selection intent explicit.

### A5 — Closure counter output

```text
1 2 3
```

The nested function retains a reference to the enclosing `count` cell after `make_counter` returns. `nonlocal count` allows rebinding that enclosing local name; every call uses the same cell.

### A6 — Threshold closure

```python
from collections.abc import Callable


def make_threshold(minimum: int) -> Callable[[int], bool]:
    def accepts(value: int) -> bool:
        return value >= minimum
    return accepts


def test_threshold() -> None:
    accepts = make_threshold(5)
    assert not accepts(4)
    assert accepts(5)
    assert accepts(6)
```

A callable class may be preferable if the component needs several operations, explicit public configuration, mutable state, a custom representation, or serialization as an importable type. A one-method, immutable predicate is well served by a closure.

### A7 — Late-bound loop lambdas

Output:

```text
[30, 30, 30]
```

Each lambda refers to the same loop variable `n`; the lookup occurs when the lambda is called, after the loop has finished. Two fixes:

```python
functions = [lambda value, n=n: value * n for n in range(1, 4)]
print([fn(10) for fn in functions])  # [10, 20, 30]
```

Or use a factory:

```python
def make_multiplier(n: int):
    def multiply(value: int) -> int:
        return value * n
    return multiply

functions = [make_multiplier(n) for n in range(1, 4)]
```

### A8 — Scope and `UnboundLocalError`

Because `total += amount` assigns to `total`, Python treats `total` as local throughout `add_to_total`; the read needed for `+=` occurs before that local has a value, so a call raises `UnboundLocalError`.

Explicit global mutation:

```python
total = 10

def add_to_total_global(amount: int) -> int:
    global total
    total += amount
    return total
```

Prefer explicit input/output:

```python
def add_to_total(total: int, amount: int) -> int:
    return total + amount
```

`nonlocal` targets a binding in an enclosing *function* scope, not the module scope. A nested counter factory can use `nonlocal count`; this function cannot use `nonlocal total` for a module global.

### A9 — Mutable default output

Output:

```text
['raw']
['raw', 'clean']
['ready']
```

The default list is created once when the function is defined and reused on calls that omit `tags`. Correct implementation:

```python
def append_tag(tag: str, tags: list[str] | None = None) -> list[str]:
    if tags is None:
        tags = []
    tags.append(tag)
    return tags
```

This still mutates a caller-provided list intentionally; document that contract or return a new list if mutation is not desired.

### A10 — Comprehension versus `map`/`filter`

```python
values = [3, -2, 0, 5, -1]
result = [value * value for value in values if value > 0]
# [9, 25]
```

Equivalent toolkit form:

```python
result = list(map(lambda value: value * value, filter(lambda value: value > 0, values)))
```

The comprehension states the filter and transformation in one readable expression. `reduce` is designed for folding a sequence into one accumulated value and adds no clarity here. Empty input should produce `[]`:

```python
def positive_squares(values: list[int]) -> list[int]:
    return [value * value for value in values if value > 0]

assert positive_squares([]) == []
```

### A11 — Multi-key ordering

```python
ordered = sorted(
    records,
    key=lambda row: (row["team"], -row["score"], row["player"]),
)
```

This assumes numeric scores and comparable string fields. Stable sorting preserves input order when the entire key compares equal. `reverse=True` reverses the ordering of the whole key tuple, not just the score component. An alternative is stable sorts from least-significant to most-significant key, but the tuple key is concise when directions can be expressed directly.

```python
def test_multi_key_sort_and_equal_key_stability() -> None:
    records = [
        {"team": "A", "score": 9, "player": "Mia", "sequence": 1},
        {"team": "A", "score": 9, "player": "Mia", "sequence": 2},
        {"team": "A", "score": 10, "player": "Zoe", "sequence": 3},
        {"team": "B", "score": 10, "player": "Ada", "sequence": 4},
    ]
    ordered = sorted(records, key=lambda row: (row["team"], -row["score"], row["player"]))
    assert [row["sequence"] for row in ordered] == [3, 1, 2, 4]
```

### A12 — `top_k`

The module roadmap specifies `key=None` and `reverse=False`, with results matching `sorted(items, key=key, reverse=reverse)[:k]`. `heapq.nsmallest` handles ascending order and `heapq.nlargest` handles descending order. Both preserve input order among equal keys for the same stable-order contract as `sorted`.

```python
import heapq
from collections.abc import Callable, Iterable
from typing import Any, TypeVar

T = TypeVar("T")


def top_k(
    items: Iterable[T],
    k: int,
    *,
    key: Callable[[T], Any] | None = None,
    reverse: bool = False,
) -> list[T]:
    if isinstance(k, bool) or not isinstance(k, int):
        raise TypeError("k must be an integer")
    if k < 0:
        raise ValueError("k must be non-negative")
    if k == 0:
        return []
    if reverse:
        return heapq.nlargest(k, items, key=key)
    return heapq.nsmallest(k, items, key=key)
```

Tests:

```python
import pytest


def test_top_k_matches_sorted_slice_and_preserves_ties() -> None:
    items = [("a", 2), ("b", 3), ("c", 3), ("d", 1)]
    original = items.copy()
    ascending = top_k(items, 4, key=lambda item: item[1])
    assert ascending == sorted(items, key=lambda item: item[1])[:4]
    assert ascending[-2:] == [("b", 3), ("c", 3)]
    assert top_k(items, 2, key=lambda item: item[1], reverse=True) == [
        ("b", 3), ("c", 3)
    ]
    assert items == original


def test_top_k_defaults_and_boundaries() -> None:
    assert top_k([3, 1, 2], 2) == [1, 2]
    assert top_k([], 2) == []
    assert top_k([1, 2], 0) == []
    assert top_k([1, 2], 9, reverse=True) == [2, 1]
    assert top_k(iter([3, 1, 2]), 2) == [1, 2]


def test_top_k_invalid_k() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        top_k([1], -1)
    with pytest.raises(TypeError, match="integer"):
        top_k([1], 1.5)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="integer"):
        top_k([1], True)
```

The helper uses heap selection rather than sorting the entire input in the common case. It still consumes an iterable as needed and does not mutate a caller-owned container. The `key` callable should be deterministic and side-effect-free; for a very small input, `sorted(... )[:k]` may be simpler. Benchmark realistic workloads before claiming a speedup.

### A13 — Class attribute output

```text
batch stream batch
```

`Pipeline.mode` is a class attribute. `first.mode = "stream"` creates an instance attribute that shadows the class attribute for `first`; it does not change `Pipeline.mode` or `second.mode`.

### A14 — Invalid `__init__` return

Calling `BadConfig(3)` raises `TypeError` because `__init__` must return `None`; explicitly returning `self` violates the initialization protocol. The normal class call creates/obtains the instance and then initializes it. Use a `@classmethod` alternative constructor when a factory needs to select or return an object.

### A15 — Configuration abstraction choice

- One-off fixed factor: `partial(multiply, factor=3)` is compact.
- Private one-method configured predicate: closure is sufficient.
- Stateful transformer with visible configuration and call count: callable class is justified because configuration and state have a named home.

Example:

```python
from dataclasses import dataclass

@dataclass
class Scaler:
    factor: float
    calls: int = 0

    def __call__(self, value: float) -> float:
        self.calls += 1
        return value * self.factor
```

Test:

```python
def test_scaler_tracks_calls() -> None:
    scaler = Scaler(factor=3.0)
    assert scaler(2.0) == 6.0
    assert scaler.calls == 1
```

The mutable call count means the object is stateful and not automatically thread-safe. Do not add a class solely to wrap a function without a meaningful state/configuration/API benefit.

### A16 — Injectable retry policy

One acceptable design is to inject a sleeper and avoid a clock if retry decisions depend only on attempt count:

```python
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def retry(
    operation: Callable[[], T],
    attempts: int,
    *,
    sleep: Callable[[float], None],
    delay: float = 0.0,
) -> T:
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    if delay < 0:
        raise ValueError("delay must be non-negative")
    for attempt in range(attempts):
        try:
            return operation()
        except Exception:
            if attempt == attempts - 1:
                raise
            sleep(delay)
    raise AssertionError("unreachable")
```

A production version should catch only the documented retryable exception types; catching `Exception` above keeps the small exercise focused on injection and should be narrowed for a real system.

```python
def test_retry_uses_fake_sleep() -> None:
    calls = 0
    sleeps: list[float] = []

    def operation() -> str:
        nonlocal calls
        calls += 1
        if calls < 3:
            raise OSError("temporary")
        return "ok"

    assert retry(operation, 3, sleep=sleeps.append, delay=0.25) == "ok"
    assert calls == 3
    assert sleeps == [0.25, 0.25]


def test_retry_reraises_last_failure_and_validates_attempts() -> None:
    import pytest

    def always_fails() -> str:
        raise OSError("still failing")

    with pytest.raises(OSError, match="still failing"):
        retry(always_fails, 2, sleep=lambda _: None)
    with pytest.raises(ValueError, match="at least 1"):
        retry(lambda: "unused", 0, sleep=lambda _: None)
```

A fake clock is needed if the policy uses elapsed time, deadlines, or rate limits; a sleep dependency alone is enough for this attempt-count policy.

### A17 — Function review

Defects include: mutable shared default `cache`; mutates input rows; weak/unannotated contract; assumes `email` and `id` exist and are strings; repeated `result += [row]` is unnecessarily indirect; side effect and transformation are mixed; returned records alias the inputs.

A corrected boundary-oriented version:

```python
from collections.abc import Iterable, Mapping

Row = Mapping[str, object]


def normalize_rows(rows: Iterable[Row]) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for index, row in enumerate(rows):
        email = row.get("email")
        if not isinstance(email, str):
            raise ValueError(f"row {index} must contain a string email")
        normalized = dict(row)
        normalized["email"] = email.strip().lower()
        result.append(normalized)
    return result
```

Tests:

```python
import pytest

def test_normalize_rows_does_not_mutate_input() -> None:
    source = {"id": 1, "email": " A@EXAMPLE.COM "}
    output = normalize_rows([source])
    assert output == [{"id": 1, "email": "a@example.com"}]
    assert source["email"] == " A@EXAMPLE.COM "
    assert output[0] is not source


def test_normalize_rows_rejects_missing_email() -> None:
    with pytest.raises(ValueError, match="string email"):
        normalize_rows([{"id": 1}])


def test_normalize_rows_rejects_non_string_email() -> None:
    with pytest.raises(ValueError, match="string email"):
        normalize_rows([{"id": 1, "email": None}])
```

`Any` is not needed in the final signature above and may be omitted from imports. If `id` is required by the domain, validate it explicitly rather than silently assuming it exists.

### A18 — Bound-method output

```text
False
True
```

Repeated `worker.run` access generally creates distinct bound-method objects, so identity (`is`) is false. Bound method equality compares the underlying function and instance, so two accesses to the same method on the same instance compare equal. Do not use `is` to test whether a callback is the same bound method.

### A19 — Pickling

Process pools generally need to serialize submitted callables and their arguments. Lambdas and nested functions are not normally importable by qualified module name, so standard pickle cannot reliably resolve them in another process. Prefer an importable module-level function, or a top-level callable class whose instance state is picklable. A `partial` around a module-level function can work if the function and bound arguments are picklable. Thread pools execute in the same process and do not impose the same callable-pickling requirement, though shared-state safety still matters.

### A20 — Safe refactoring sequence

A strong answer includes these steps:

1. **Characterize behavior:** add tests for representative input, empty file, malformed row, invalid business data, write failure, and exact report semantics.
2. **Record baseline:** line count, cyclomatic complexity, test count/coverage, runtime and peak memory on representative data; record tool/version and dataset size.
3. **Rename local variables and clarify branches:** run tests after each small change.
4. **Extract pure parsing and validation functions:** test them without file I/O; preserve error categories and messages where callers depend on them.
5. **Separate I/O shell:** inject file reader/writer or use explicit path boundaries; test failures with fakes or temporary files.
6. **Introduce a parameter object only if related options form a coherent concept:** keep public defaults compatible.
7. **Replace repeated conditionals with dispatch only when it simplifies extension and error handling.**
8. **Re-run tests, lint, type checks, and performance measurements after each behavior-preserving step.**
9. **Review security boundaries:** path handling, encoding, untrusted fields, and whether errors/logs expose sensitive values.
10. **Stop when responsibilities are clear and further extraction would create indirection without reducing change risk.**

Refactoring should preserve behavior unless a change is explicitly approved and tested. A lower line count alone is not proof of improvement.

## Class answers (Q21–Q40)

### B21 — Account

```python
class Account:
    def __init__(self, owner: str, opening_balance: int = 0) -> None:
        if not isinstance(owner, str):
            raise TypeError("owner must be a string")
        normalized_owner = owner.strip()
        if not normalized_owner:
            raise ValueError("owner must not be empty")
        if isinstance(opening_balance, bool) or not isinstance(opening_balance, int):
            raise TypeError("opening_balance must be an integer")
        if opening_balance < 0:
            raise ValueError("opening_balance must be non-negative")
        self.owner = normalized_owner
        self._balance = opening_balance

    @property
    def balance(self) -> int:
        return self._balance

    def deposit(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        self._balance += amount
```

Tests:

```python
import pytest

def test_account_state_is_per_instance() -> None:
    first = Account("Ada", 10)
    second = Account("Lin", 20)
    first.deposit(5)
    assert first.balance == 15
    assert second.balance == 20
    assert type(first) is Account
    assert isinstance(first, Account)


def test_account_rejects_negative_balance() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        Account("Ada", -1)


def test_account_rejects_blank_owner_and_non_integer_balance() -> None:
    with pytest.raises(ValueError, match="owner"):
        Account("   ")
    with pytest.raises(TypeError, match="integer"):
        Account("Ada", True)
```

`self` is the instance supplied to the bound method. The read-only property and `_balance` convention reduce accidental invariant-breaking, though Python underscore conventions are not security boundaries. In a production money model, integer minor units or a `Decimal`-based value object would be preferable to an unqualified integer balance.

### B22 — Encapsulated queue

```python
from collections import deque
from collections.abc import Iterable


class JobQueue:
    def __init__(self, jobs: Iterable[str] = ()) -> None:
        self._jobs: deque[str] = deque()
        for job in jobs:
            self.enqueue(job)

    @property
    def jobs(self) -> tuple[str, ...]:
        """Return an immutable snapshot of queued jobs."""
        return tuple(self._jobs)

    def enqueue(self, job: str) -> None:
        if not isinstance(job, str) or not job.strip():
            raise ValueError("job must be a non-empty string")
        self._jobs.append(job)

    def dequeue(self) -> str:
        if not self._jobs:
            raise IndexError("cannot dequeue from an empty queue")
        return self._jobs.popleft()
```

Tests:

```python
import pytest


def test_job_queue_fifo_and_snapshot_isolation() -> None:
    queue = JobQueue(["first", "second"])
    snapshot = queue.jobs
    assert snapshot == ("first", "second")
    with pytest.raises(AttributeError):
        snapshot.append("external")  # tuple has no append method
    assert queue.dequeue() == "first"
    assert queue.jobs == ("second",)


def test_job_queue_empty_and_invalid_job() -> None:
    queue = JobQueue()
    with pytest.raises(IndexError, match="empty"):
        queue.dequeue()
    with pytest.raises(ValueError, match="non-empty string"):
        queue.enqueue("")
    with pytest.raises(ValueError, match="non-empty string"):
        JobQueue(["valid", "   "])
    with pytest.raises(ValueError, match="non-empty string"):
        JobQueue(["valid", 7])  # type: ignore[list-item]
```

The invariant is that all entries are valid job identifiers and queue operations preserve FIFO order. The underscore is a convention, not a security barrier.

### B23 — Manual initialization output

Output:

```text
['b'] ['a'] False
```

`copy.copy(original)` creates a distinct shallow copy whose `items` initially refers to the same list. Then `original.__init__(["b"])` reassigns `original.items` to a new list; it does not reinitialize `cloned`. The clone retains the original list `['a']`. Manually invoking `__init__` is usually a smell because it bypasses the normal construction protocol and can leave related state inconsistent. Use a constructor/factory or explicit reset method with a documented contract.

### B24 — `super()` output

```text
Child
Base
```

`Child.__init__` runs first and delegates with `super().__init__()`. That resolves to `Base.__init__`, which prints `Base` and delegates to `object.__init__`. In single inheritance this looks like a parent call; semantically, `super()` starts lookup after the current class in the instance's MRO.

### B25 — Construction protocol

For ordinary `C(...)`, the metaclass call machinery obtains an object through `__new__`; if the result is an instance of the requested class, initialization runs via `__init__`. If `__new__` returns an unrelated object, `__init__` for the requested class is not called. `__init__` initializes an existing object and must return `None`. Override `__new__` when controlling creation of immutable built-in subclasses or a genuinely specialized allocation/factory protocol; most application classes only need a validating `__init__` and perhaps classmethod factories.

### B26 — `Config.from_dict`

```python
from collections.abc import Mapping


class Config:
    def __init__(self, environment: str, batch_size: int) -> None:
        if not isinstance(environment, str):
            raise ValueError("environment must be a string")
        environment = environment.strip()
        if not environment:
            raise ValueError("environment must not be empty")
        if isinstance(batch_size, bool) or not isinstance(batch_size, int) or batch_size <= 0:
            raise ValueError("batch_size must be a positive integer")
        self.environment = environment
        self.batch_size = batch_size

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "Config":
        try:
            environment = data["environment"]
            batch_size = data["batch_size"]
        except KeyError as exc:
            raise ValueError(f"missing config field: {exc.args[0]}") from exc
        if not isinstance(environment, str):
            raise ValueError("environment must be a string")
        if isinstance(batch_size, bool) or not isinstance(batch_size, int):
            raise ValueError("batch_size must be an integer")
        return cls(environment, batch_size)
```

The constructor is the single authority for valid state; `from_dict` handles mapping-specific extraction and boundary errors. `bool` is a subclass of `int`, so explicitly excluding it is useful when a true integer count is required.

Tests:

```python
import pytest

def test_config_factory() -> None:
    config = Config.from_dict({"environment": " prod ", "batch_size": 4})
    assert config.environment == "prod"
    assert config.batch_size == 4


def test_config_rejects_bad_batch_size() -> None:
    with pytest.raises(ValueError, match="positive integer"):
        Config("prod", 0)


def test_config_factory_missing_field() -> None:
    with pytest.raises(ValueError, match="missing config field"):
        Config.from_dict({"environment": "prod"})


def test_config_rejects_non_string_environment() -> None:
    with pytest.raises(ValueError, match="environment must be a string"):
        Config(None, 4)  # type: ignore[arg-type]
```

### B27 — `Celsius(float)`

```python
class Celsius(float):
    def __new__(cls, value: float) -> "Celsius":
        numeric = float(value)
        if numeric < -273.15:
            raise ValueError("temperature is below absolute zero")
        return super().__new__(cls, numeric)
```

`float` values are immutable; the numeric payload is created in `__new__`, before an instance exists to initialize. Tests:

```python
import pytest


def test_celsius_absolute_zero_boundary() -> None:
    assert Celsius(-273.15) == -273.15
    assert isinstance(Celsius(0), Celsius)


def test_celsius_rejects_below_absolute_zero() -> None:
    with pytest.raises(ValueError, match="absolute zero"):
        Celsius(-273.16)
```

If non-finite values are not acceptable, explicitly reject `math.isnan`/infinity too; the requirement must be defined by the domain.

### B28 — Substitutability

The subclass strengthens the precondition (rejects inputs accepted by the base) and weakens the postcondition (returns `None` instead of a `bool`). Callers typed against `Notifier` cannot safely substitute it. A reusable contract-test helper is:

```python
from typing import Protocol


class Notifier(Protocol):
    def send(self, message: str) -> bool: ...


def assert_notifier_contract(notifier: Notifier) -> None:
    result = notifier.send("ordinary valid message")
    assert isinstance(result, bool)
```

Run this helper for every concrete notifier implementation, and add tests for the documented failure/exception policy. A protocol or ABC can help express the interface, but behavioral tests verify the contract.

### B29 — Composition

A reasonable design has a `Notifier` service that receives a `Transport` protocol, a retry policy, and an urgency setting. The transport sends one message; the retry policy decides how to retry; urgency changes message metadata or scheduling policy. This avoids a subclass for every Cartesian product of features.

```python
from collections.abc import Callable
from typing import Protocol


class Transport(Protocol):
    def send(self, message: str, *, urgent: bool) -> bool: ...


class RetryPolicy(Protocol):
    def run(self, operation: Callable[[], bool]) -> bool: ...


class NotifierService:
    def __init__(
        self, transport: Transport, retry: RetryPolicy, *, urgent: bool = False
    ) -> None:
        self._transport = transport
        self._retry = retry
        self._urgent = urgent

    def send(self, message: str) -> bool:
        return self._retry.run(
            lambda: self._transport.send(message, urgent=self._urgent)
        )
```

Test the retry policy independently with a fake operation, test transport behavior independently, then test orchestration with fakes that record calls and return deterministic results. Composition adds explicit wiring and can feel verbose for a tiny fixed system; inheritance may remain suitable for a true subtype with a stable behavioral contract.

### B30 — Money and dataclass

```python
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        normalized = self.currency.strip().upper()
        if not normalized:
            raise ValueError("currency must not be empty")
        object.__setattr__(self, "currency", normalized)
```

A production version should also validate currency format and amount policy. Frozen dataclasses generate equality based on fields and a compatible hash when the fields are hashable; `Decimal` and `str` are hashable. A handwritten class is useful for specialized equality, validation, arithmetic, or compatibility requirements. Do not define a hash based on mutable fields: changing a key's hash after insertion breaks set/dict lookup assumptions.

Tests:

```python
import pytest

def test_money_value_equality() -> None:
    assert Money(Decimal("2.00"), "usd") == Money(Decimal("2.00"), "USD")


def test_money_rejects_blank_currency() -> None:
    with pytest.raises(ValueError):
        Money(Decimal("1"), "  ")
```

### B31 — Dependency injection

```python
from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    def __call__(self) -> datetime: ...


class ReportWriter(Protocol):
    def write(self, content: str) -> None: ...


class ReportService:
    def __init__(self, clock: Clock, writer: ReportWriter) -> None:
        self._clock = clock
        self._writer = writer

    def publish(self, body: str) -> None:
        timestamp = self._clock().isoformat()
        self._writer.write(f"{timestamp}\n{body}")
```

A deterministic test can use a fixed clock and fake writer:

```python
from datetime import datetime, timezone


class FakeWriter:
    def __init__(self) -> None:
        self.contents: list[str] = []

    def write(self, content: str) -> None:
        self.contents.append(content)


def test_report_service_uses_injected_dependencies() -> None:
    fixed = datetime(2025, 1, 2, tzinfo=timezone.utc)
    writer = FakeWriter()
    service = ReportService(clock=lambda: fixed, writer=writer)
    service.publish("ready")
    assert writer.contents == ["2025-01-02T00:00:00+00:00\nready"]
```

This makes time deterministic and prevents tests from needing real storage/network clients. Protocols document the collaborator shape; structural typing does not automatically validate external runtime data.

### B32 — Shared mutable class attribute output

Output:

```text
['alpha'] ['alpha']
```

Both instances mutate the same list defined on the class. Fix by assigning `self.entries = []` in `__init__`, or using a dataclass `field(default_factory=list)`:

```python
class Registry:
    def __init__(self) -> None:
        self.entries: list[str] = []

    def add(self, entry: str) -> None:
        self.entries.append(entry)


def test_registry_entries_are_per_instance() -> None:
    first = Registry()
    second = Registry()
    first.add("alpha")
    assert first.entries == ["alpha"]
    assert second.entries == []
```

Class attributes are appropriate for genuinely shared constants or registries with explicit shared-state semantics, not per-instance collections.

### B33 — Equality and hashing

Value equality means two points with equal coordinates compare equal even if they are separate objects (`p1 == p2` true, `p1 is p2` false). A useful representation is `Point(x=2, y=4)`. If objects compare equal and are hashable, their hashes must be equal. Mutable equality fields make stable hashing unsafe; use an immutable value object or leave it unhashable. `repr` should be unambiguous and useful for debugging, while avoiding secrets.

### B34 — Job state transitions

```python
from enum import Enum

class JobState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class Job:
    def __init__(self) -> None:
        self._state = JobState.PENDING

    @property
    def state(self) -> JobState:
        return self._state

    def start(self) -> None:
        if self._state is not JobState.PENDING:
            raise ValueError("only pending jobs can start")
        self._state = JobState.RUNNING

    def finish(self, *, succeeded: bool) -> None:
        if not isinstance(succeeded, bool):
            raise TypeError("succeeded must be a bool")
        if self._state is not JobState.RUNNING:
            raise ValueError("only running jobs can finish")
        self._state = JobState.SUCCEEDED if succeeded else JobState.FAILED
```

A contract may instead define duplicate `start` as idempotent; the important part is to choose and document the behavior. State must not change before validation. If transitions perform I/O, handle partial failure and retries explicitly; async cancellation can occur at await points, so design operations to leave state consistent or record an intermediate state.

Tests:

```python
import pytest


def test_job_valid_transition_sequence() -> None:
    job = Job()
    job.start()
    job.finish(succeeded=True)
    assert job.state is JobState.SUCCEEDED


def test_job_rejects_illegal_transition_without_mutation() -> None:
    job = Job()
    with pytest.raises(ValueError):
        job.finish(succeeded=True)
    assert job.state is JobState.PENDING
    job.start()
    with pytest.raises(ValueError):
        job.start()
    assert job.state is JobState.RUNNING
    with pytest.raises(TypeError, match="bool"):
        job.finish(succeeded=1)  # type: ignore[arg-type]
    assert job.state is JobState.RUNNING
```

Also cover running→failed and finishing twice. These tests demonstrate that invalid transitions are rejected before state changes.

### B35 — Constructor chaining

```python
class Account:
    def __init__(self, owner: str, opening_balance: int = 0) -> None:
        if not isinstance(owner, str):
            raise TypeError("owner must be a string")
        owner = owner.strip()
        if not owner:
            raise ValueError("owner must not be empty")
        if isinstance(opening_balance, bool) or not isinstance(opening_balance, int):
            raise TypeError("opening_balance must be an integer")
        if opening_balance < 0:
            raise ValueError("opening_balance must be non-negative")
        self.owner = owner
        self.balance = opening_balance


class SavingsAccount(Account):
    def __init__(self, owner: str, opening_balance: int, interest_rate: float) -> None:
        import math
        if isinstance(interest_rate, bool) or not isinstance(interest_rate, (int, float)):
            raise TypeError("interest_rate must be numeric")
        if not math.isfinite(interest_rate) or interest_rate < 0:
            raise ValueError("interest_rate must be finite and non-negative")
        super().__init__(owner, opening_balance)
        self.interest_rate = float(interest_rate)
```

The child validates its own parameter and delegates shared initialization to the parent. Omitting `super().__init__` leaves `owner` and `balance` absent and violates the base contract. A focused regression test is:

```python
def test_savings_account_preserves_parent_invariants() -> None:
    account = SavingsAccount(" Ada ", 100, 0.02)
    assert account.owner == "Ada"
    assert account.balance == 100
    assert account.interest_rate == 0.02


def test_savings_account_rejects_invalid_parent_state() -> None:
    import pytest
    with pytest.raises(ValueError, match="owner"):
        SavingsAccount("  ", 100, 0.02)
    with pytest.raises(ValueError, match="finite and non-negative"):
        SavingsAccount("Ada", 100, float("nan"))
```

Tests should exercise base behavior through the child instance as well as inspect expected attributes.

### B36 — Construction versus instance call output

```text
init
call
12
```

`Multiplier(3)` calls the class and initializes a new instance, printing `init`. `multiply_by_three(4)` invokes that instance's `__call__`, printing `call` and returning `12`. The two call paths are different protocols.

### B37 — Shallow-copy aliasing

The assertions `source is not clone` and `source.rows is clone.rows` are both true immediately after `copy.copy(source)`. `__init__` runs once for `source`. A shallow copy creates a separate outer object without calling `__init__`, but copies attribute references, so both `rows` attributes initially point to the same list. Appending through `clone.rows` mutates the shared list. Use `deepcopy` only when its semantics are appropriate, or provide an explicit clone/factory method that defines how nested state is copied.

### B38 — Public API evolution

Preserve the existing positional signature while adding a configuration route, for example `Processor(path, mode, retry, timeout, *, config=None)` temporarily, or add a `from_config` factory. In a future major release, move new options to keyword-only parameters and deprecate ambiguous positional forms with warnings and release notes. Use `Literal["fast", "safe"]` or an enum for finite modes, `Protocol` for collaborators, `@override` (Python 3.12 via `typing.override`) on overrides, and runtime validation at untrusted boundaries. Type hints guide tools but do not reject invalid runtime values by themselves.

### B39 — Review findings

Example prioritization:

1. **High correctness:** `items=[]` is shared across calls/instances that use the default. Use `None` or `field(default_factory=list)` and test instance independence.
2. **High correctness/isolation:** `cache = {}` is shared across all instances and stores mutable input objects. Decide whether the cache is truly shared; otherwise make it per-instance. Copy or normalize stored data if aliasing is unsafe.
3. **Medium contract clarity:** missing annotations and undocumented required keys make the API hard to use. Define a record type (`TypedDict` or dataclass), validate `data` at the boundary, and annotate client protocol.
4. **Medium cohesion:** `Manager` is vague and combines persistence, cache management, list accumulation, and status extraction. Separate responsibilities if they change independently.
5. **Potential high robustness:** `data["id"]` and `data["status"]` can raise `KeyError`; validate schema and raise a domain-specific error.
6. **Potential side effect:** `client.save` happens before later key access; if `status` is missing, the save succeeds but the method fails. Validate all required fields before side effects.
7. **API behavior:** returns raw `status` without an explicit type or documented result contract.

Do not automatically delete or rename the class based on its name alone. Use actual callers, change history, tests, and responsibilities to decide. The example is illustrative; it is not an audit of an unseen Stage 1 project.

### B40 — Capstone plan

Suggested module boundaries:

- `functional.py`: `compose`, `pipe`, `once`, closure-based `memoize`, late-binding-safe `bind_loop`, and `top_k(items, k, key=...)`.
- `callables.py`: callable `RetryPolicy`, `RateLimiter` with an injected clock, and `partial`-based adapters.
- `model.py`: `Money`, `Account` + `SavingsAccount` with constructor chaining and contract tests, and `Celsius(float)` using `__new__`.
- `config.py`: `Config.from_env` and `Config.from_dict`, with parsing at the boundary and validated state in the constructor.
- `tests/`: unit, contract, regression, boundary, property-oriented where useful, and fake-dependency tests.
- `REVIEW.md`: joint function/class review with prioritized findings, before/after code, and measured evidence.

Test categories should include: `once`/`memoize` behavior; closure-state behavior; late-binding regression; empty and boundary `top_k`; stable ties; fake-clock rate limits; retry exhaustion; invalid Money; Account invariants; subclass constructor chaining and base contract; Celsius absolute-zero boundary; malformed environment/dictionary config; and input non-mutation. Every late-binding and construction pitfall needs a failing-then-passing regression test. Configure CI with Ruff (including applicable `B023`, `E731`, `PLR`, `C901`, and `FBT` rules), strict mypy on `gapcheck`, pytest, and at least 90% branch coverage for the mini-project. These are this roadmap's acceptance criteria, not universal thresholds for every codebase.

Eight small commits might be: characterization tests; functional helpers; closure regressions; top-k tests; callable policy and `partial` adapters; fake-clock rate limiter; domain models/config; final review and CI gates. Measure complexity, parameter count, test count, branch coverage, runtime, and coupling before/after using the same tool versions and representative inputs. Review two functions and two classes from actual accessible project sources; if unavailable, explicitly label replacements as illustrative and document the evidence gap. An ADR is useful when a non-obvious architectural choice has long-term consequences, not for every small refactor.

---

## 7. Coding solutions and test-running guidance

The answer key includes executable implementations and pytest-style tests for the principal coding exercises, plus explicit test criteria for design/contract questions. Where a solution is shown as a fragment, combine it with the question's stated inputs and the relevant test snippet before running it. For a clean audit, put each solution in a module and its associated tests in `test_*.py`; avoid copying multiple classes with the same name into one namespace. Run:

```bash
python --version
python -m pytest -q
ruff check .
mypy --strict gapcheck
```

Run only tools installed in the environment. Record tool versions and actual output in your own notes. The commands are recommendations, not claims that every environment has these tools installed. Keep test fixtures deterministic: fake clocks and sleepers are preferable to real delays; temporary directories are preferable to machine-specific paths.

## 8. Scoring rubric

Suggested study scoring: score each question from 0–4 (maximum 160 points). These thresholds are learning guidance, **not official roadmap requirements**.

| Dimension | What to assess | Suggested weight |
|---|---|---:|
| Conceptual understanding | Explains semantics and trade-offs, not just terminology | 25% |
| Code correctness | Meets stated behavior, handles edge cases, uses Python semantics correctly | 35% |
| Testing quality | Covers boundaries, invalid inputs, state, regressions, and deterministic fakes | 20% |
| Design reasoning | Makes proportionate choices, preserves contracts, identifies risks | 20% |

Per-question scale:

- **0:** blank or materially incorrect.
- **1:** recognizes part of the topic but has major gaps.
- **2:** mostly correct core idea, missing important edge cases or tests.
- **3:** correct and clear, with appropriate tests or reasoning.
- **4:** robust, well-typed, testable, and justified with relevant trade-offs.

Suggested interpretation: below 60% means revisit foundations and retry; 60–79% means revisit missed lessons and implement more tests; 80–89% means ready for a focused mini-project pass; 90%+ suggests strong coverage but does not replace completing the `gapcheck` mini-project. Do not let a high aggregate score conceal a critical defect in construction, shared state, or contract behavior.

## 9. Weak-area diagnosis mapped to Lessons 01–11

| Observed weakness | Revisit | Practice next |
|---|---|---|
| Confuses function object with function result; callbacks execute too early | 01 | Q1–Q3, dispatch table and callback registration tests |
| Overuses anonymous lambdas or cannot explain their limits | 02 | Q4, replace one opaque lambda with `operator` or `def` |
| Cannot explain closure state or captured variables | 03 | Q5–Q6, inspect `__closure__` and `co_freevars` |
| Late-binding bugs, mutable defaults, or scope errors | 04 | Q7–Q9, add regression tests before fixing |
| Uses `reduce` where a comprehension is clearer; unstable/tie-unsafe sorting | 05 | Q10–Q12, add stable tie and boundary tests |
| Chooses callable classes by default or hides shared state | 06 | Q15–Q16, compare function/partial/closure/class designs |
| Functions mix I/O, mutation, validation, and formatting | 07 | Q17, Q20, characterize then extract pure functions |
| Confuses class and instance state, equality, or encapsulation | 08 | Q13, Q21–Q23, Q30–Q33 |
| Misunderstands construction or `__new__`/`__init__` | 09 | Q14, Q25–Q27, Q36–Q37 |
| Missing parent initialization or weak subtype contracts | 10 | Q24, Q28–Q29, Q35; add contract tests |
| God classes, shared state, poor dependency direction, or no refactoring evidence | 11 | Q22, Q29–Q40 and the class-review checklist |

## 10. Completion checklist aligned with the roadmap

- [ ] I can pass, return, store, dispatch, inspect, and call functions as values.
- [ ] I can use lambdas where they improve clarity and prefer named functions when documentation or debugging needs it.
- [ ] I can explain closures, free variables, cells, `nonlocal`, and late binding.
- [ ] I can identify mutable-default hazards and choose a safe default pattern.
- [ ] I can select among `map`, `filter`, `reduce`, comprehensions, `sum`/`any`/`all`, key functions, and stable sorting.
- [ ] I can choose among a plain function, `partial`, closure, and callable class based on state and API needs.
- [ ] I can review/refactor a function using tests, types, error contracts, purity, and performance evidence.
- [ ] I can explain classes, instances, `self`, class/instance attributes, equality, representation, and encapsulation conventions.
- [ ] I can explain `__new__` versus `__init__`, validate construction, and design classmethod factories.
- [ ] I can use inheritance and `super()` for constructor chaining and recognize when composition is better.
- [ ] I can review/refactor a class with attention to invariants, cohesion, coupling, collaborators, and contract tests.
- [ ] I completed the `gapcheck` mini-project with tests, relevant lint/type checks, and a review report.
- [ ] I completed the Stage 1 consolidation review using actual available project code, or explicitly recorded which examples were illustrative because source code was unavailable.

**Roadmap next step:** return to Module 1.11 if this module was completed before the advanced object-model modules; otherwise proceed to Stage 2 after completing the Stage 1 sequence.
