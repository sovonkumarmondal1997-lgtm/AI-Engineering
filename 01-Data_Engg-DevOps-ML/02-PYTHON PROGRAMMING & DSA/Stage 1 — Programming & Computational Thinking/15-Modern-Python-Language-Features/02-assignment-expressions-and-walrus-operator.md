# Assignment Expressions and the Walrus Operator (`:=`)

> **Repository version policy:** write new code for Python **3.12+**. Assignment expressions were introduced in **Python 3.8** (PEP 572), so the feature itself is available on Python 3.8 and later.
>
> **Core principle:** use `:=` when naming a value at the point where it is tested or consumed makes the code clearer. Do not use it merely to reduce line count.

## Learning objectives

By the end of this lesson, you should be able to:

1. Explain the difference between an assignment statement (`=`) and an assignment expression (`:=`).
2. Read and write walrus expressions in conditions, loops, regular-expression checks, and comprehensions.
3. Predict evaluation order, truth testing, and the value produced by a named expression.
4. Explain the binding scope of a walrus target, including the special rules for comprehensions.
5. Recognize syntax restrictions and prohibited rebinding patterns.
6. Choose between a walrus expression, a conventional assignment, and alternatives such as `iter(callable, sentinel)`.
7. Measure performance with `timeit` rather than inferring it from line count.
8. Review walrus usage for readability, side effects, debugging, compatibility, and team style.

## Prerequisites

You should already understand variables, expressions and statements, truthiness, `if`/`while`, loops, functions, comprehensions, dictionaries, exceptions, regular expressions, and basic scope rules. You do not need to know compiler internals.

## 1. The mental model

An assignment statement binds a name but is not itself an expression that can be embedded in a larger expression:

```python
def calculate() -> int:
    return 12

value = calculate()
if value > 10:
    print(value)
```

Expected output:

```text
12
```

An assignment expression binds a name **and evaluates to the assigned value**:

```python
def calculate() -> int:
    return 12

if (value := calculate()) > 10:
    print(value)
```

Expected output:

```text
12
```

Read `value := calculate()` as: “evaluate `calculate()` once, bind its result to `value`, and produce that result as the value of this expression.” The parentheses make the assignment-expression boundary explicit and are required in many contexts.

### Assignment statement versus assignment expression

| Property | Assignment statement (`=`) | Assignment expression (`:=`) |
| --- | --- | --- |
| Main purpose | Bind or update a name as a statement | Bind a name while producing a value inside an expression |
| Can be embedded in `if` condition | No | Yes, with valid syntax such as `if (n := read()):` |
| Produces a value usable by surrounding expression | No | Yes: the assigned value |
| Typical best use | Ordinary state changes and multi-step logic | Avoiding duplicated work or keeping a tested value available |
| Readability risk | Usually low | Can hide mutation or make a condition hard to scan |

The `:=` operator does not mean “assign only if the value is truthy.” The assignment always happens when the expression is evaluated. The surrounding `if`, `while`, `and`, `or`, `any`, or `all` decides what happens next.

## 2. Syntax and parentheses

The basic form is:

```python
(example := 42)
```

- The target must be a simple identifier such as `count`, `match`, or `chunk`.
- You cannot use a walrus expression to assign directly to an attribute or subscript: `obj.value := 3` and `items[0] := 3` are invalid.
- Parentheses are often necessary to make the grammar unambiguous. Even where they are optional, parentheses around a walrus expression are often the clearest style.
- A walrus expression is not a replacement for every `=`. Use ordinary assignment for normal setup, state updates, and multi-step code.

```python
number = 7
print((doubled := number * 2))
print(doubled)
```

Expected output:

```text
14
14
```

The parentheses around the whole expression are not what make it assign; `:=` does. They make the expression boundary clear and satisfy syntax rules in many contexts.

## 3. Beginner patterns

### 3.1 `if`: compute once, test once, reuse the result

Without `:=`, a function may be called twice if its result is needed for both the condition and the body:

```python
def get_status() -> str:
    print("querying")
    return "ready"

status = get_status()
if status == "ready":
    print(status.upper())
```

Expected output:

```text
querying
READY
```

A walrus expression can put the assignment at the point of use:

```python
def get_status() -> str:
    print("querying")
    return "ready"

if (status := get_status()) == "ready":
    print(status.upper())
```

Expected output is the same:

```text
querying
READY
```

**Important:** the benefit is not that a walrus magically makes the function faster. The benefit is that the value is computed once and reused, instead of accidentally calling `get_status()` once in the condition and again in the body.

### 3.2 `while`: read until the result is empty

A common file-processing loop reads a chunk, processes it if non-empty, and stops at end-of-file (`b""` for binary reads):

```python
from io import BytesIO

stream = BytesIO(b"alpha\nbeta\n")
while chunk := stream.read(5):
    print(repr(chunk))
```

Expected output:

```text
b'alpha'
b'\nbeta'
b'\n'
```

Each iteration calls `read(5)` once. The returned bytes are assigned to `chunk`; the `while` condition tests whether the bytes object is truthy. An empty `bytes` object ends the loop. The final empty result is assigned to `chunk` too, so after the loop `chunk == b""`.

A conventional version is also valid:

```python
from io import BytesIO

stream = BytesIO(b"alpha\nbeta\n")
while True:
    chunk = stream.read(5)
    if not chunk:
        break
    print(repr(chunk))
```

Choose whichever form makes termination and processing easiest for your team to review. The examples above use `BytesIO` so they run as written without a repository-specific file or `process()` function.

### 3.3 Regular expressions: keep the match object

```python
import re

text = "job=ingest id=420 state=ready"
if (match := re.search(r"id=(\d+)", text)):
    print(int(match.group(1)))
else:
    print("no id found")
```

Expected output:

```text
420
```

`re.search()` returns a match object when it finds a match and `None` otherwise. The condition tests that result; the body can then use the same match object without running the search again. A match object is truthy, but test explicitly for `is not None` if that communicates the contract better to readers.

### 3.4 Assignment happens even when the condition is false

```python
if (payload := ""):
    print("non-empty")
else:
    print(repr(payload))
```

Expected output:

```text
''
```

`payload` is bound to the empty string before its truth value is tested. The body of the `else` can still read it.

## 4. Intermediate patterns

### 4.1 Refactor a repeated expensive calculation

Suppose a score calculation is expensive and the result is needed both for filtering and output. This version calculates it twice for accepted records:

```python
def score(record: dict[str, int]) -> int:
    # Placeholder for a real, potentially expensive computation.
    return record["views"] * record["quality"]

records = [
    {"id": "a", "views": 10, "quality": 2},
    {"id": "b", "views": 3, "quality": 1},
    {"id": "c", "views": 8, "quality": 3},
]

selected = [
    {"id": record["id"], "score": score(record)}
    for record in records
    if score(record) >= 20
]
print(selected)
```

Expected output:

```text
[{'id': 'a', 'score': 20}, {'id': 'c', 'score': 24}]
```

The function is called twice for accepted records. Store the score in the filter expression instead:

```python
selected = [
    {"id": record["id"], "score": computed_score}
    for record in records
    if (computed_score := score(record)) >= 20
]
print(selected)
```

Expected output:

```text
[{'id': 'a', 'score': 20}, {'id': 'c', 'score': 24}]
```

The calculation now runs once per record. The assignment expression's target, `computed_score`, is bound in the scope containing the comprehension, not in a private comprehension-local scope. In production code, consider whether that enclosing binding is useful or surprising; a regular loop may be clearer when the calculation or filtering logic grows.

### 4.2 Comprehension scope: two different kinds of names

Python comprehensions have an implicit scope for their iteration variables. A walrus target used inside a comprehension is a special case: it binds in the **containing scope** (subject to the restrictions below).

```python
def demonstrate_scope() -> tuple[list[int], int]:
    values = [1, 2, 3, 4]
    squares = [square for item in values if (square := item * item) > 0]
    return squares, square

print(demonstrate_scope())
```

Expected output:

```text
([1, 4, 9, 16], 16)
```

Here, `item` is the comprehension iteration variable and is local to the comprehension's implicit scope. It does **not** become a local name in `demonstrate_scope`. `square` is the target of `:=`, so it is bound in `demonstrate_scope`; its final value is `16` because the last iteration assigns that value.

Conceptual scope map:

```text
demonstrate_scope() local scope
├── values
├── squares
├── square       ← walrus target binds here
└── comprehension's implicit scope
    └── item     ← iteration variable is local here
```

Scope notes:

- If the iterable is empty, the comprehension never evaluates the walrus expression. The target name may therefore remain unbound; reading it can raise `UnboundLocalError` inside a function or `NameError` at module scope, depending on the surrounding context.
- In nested comprehensions, a walrus target still binds in the containing scope, not in the innermost comprehension's implicit scope.
- Assignment expressions in a comprehension are prohibited in a class body because there is no suitable containing class scope for this binding rule.
- Assignment expressions are prohibited in a comprehension's iterable expression, such as `[x for x in (items := make_items())]`.
- A walrus target cannot rebind an iteration variable of the same comprehension. For example, `[ (item := transform(item)) for item in items ]` is a `SyntaxError`.

### 4.3 Filtering and output using one computed value

```python
words = ["stream", "map", "transformation", "ETL", "warehouse"]
long_uppercase = [upper for word in words if len(upper := word.upper()) >= 5]
print(long_uppercase)
```

Expected output:

```text
['STREAM', 'TRANSFORMATION', 'WAREHOUSE']
```

`word.upper()` is called once for each input word. The resulting string is used in the filter and then emitted as the element. The walrus target `upper` is bound in the enclosing scope; do not rely on that side effect unless you intend it. If the output expression is more complex than this example, a conventional loop can be easier to maintain.

### 4.4 `dict.get()`: preserve a lookup result

Use a walrus when you need to distinguish a missing key from a present value and reuse the lookup result:

```python
settings = {"retries": 0, "region": "ap-south-1"}
if (retries := settings.get("retries")) is not None:
    print(f"configured retries: {retries}")
```

Expected output:

```text
configured retries: 0
```

Do not write `if (retries := settings.get("retries")):` if `0`, `False`, or `""` is a valid configured value; that condition checks truthiness and would treat those values as absent. If `None` itself is a valid stored value, use a unique sentinel with `get` instead:

```python
settings = {"retries": 0, "region": "ap-south-1"}
missing = object()
if (retries := settings.get("retries", missing)) is not missing:
    print("key exists")
```

### 4.5 `any()` and `all()`: use walrus only when it adds value

A walrus can retain a result while a generator expression is evaluated:

```python
values = [3, 8, 12, 5]
if any((parsed := value * 2) > 20 for value in values):
    print("first matching value retained:", parsed)
```

Expected output:

```text
first matching value retained: 24
```

`any()` stops at the first truthy test. Here, `parsed` is updated for each value tested and retains `24`, the first value whose doubled result exceeds 20. If there were no match, `parsed` would be bound to the last visited result if at least one item were visited, but it would remain unbound if `values` were empty. That behavior is a warning sign: do not use the variable after `any()` unless the control flow guarantees that it was assigned.

For `all()`, short-circuiting works in the opposite direction: evaluation stops at the first false result. A walrus target may reflect only the values visited before that point. In this all-true example, every word is visited:

```python
words = ["alpha", "beta", "gamma"]
all_valid = all((normalized := word.strip()).isalpha() for word in words)
print(all_valid, normalized)
```

Expected output:

```text
True gamma
```

If a word fails the predicate, `all()` stops there; if the iterable is empty, the generator body never runs and `normalized` is not assigned by this expression. Prefer a simple predicate when you do not need the intermediate result:

```python
all(value > 0 for value in values)
```

### 4.6 `next()` with a default

```python
import re

records = ["skip", "id:17", "id:24"]
first_id = next((match.group(1)
                 for record in records
                 if (match := re.fullmatch(r"id:(\d+)", record))), None)
print(first_id)
```

Expected output:

```text
17
```

This combines `next()`, a generator expression, and a regex match. It is compact but has several moving parts. In application code, use a multi-line loop if the pattern is unfamiliar to the team or if error handling is needed.

### 4.7 Keyword arguments, defaults, and f-strings

Walrus expressions can appear in keyword argument values when parenthesized:

```python
def show(**kwargs: object) -> None:
    print(kwargs)

result = show(value=(number := 6))
print(number)
```

Expected output:

```text
{'value': 6}
6
```

The unparenthesized form `show(value=number := 6)` is invalid syntax. The parser needs the parentheses to separate the keyword argument value from the assignment expression.

Parenthesize assignment expressions in function defaults too, for clarity and to satisfy the grammar:

```python
seed = 0

def make_value(value=(seed := 12)) -> int:
    return value

print(make_value(), seed)
```

Expected output:

```text
12 12
```

Default expressions execute when the `def` statement executes, not each time the function is called. This example is intentionally about syntax and timing, not a recommended default-value design. In normal code, avoid mutating an outer name as a side effect of defining a function; use an ordinary assignment before the definition if the value is important.

In an f-string, parenthesize the walrus expression so the colon is not confused with the format-specifier boundary:

```python
message = f"{(count := 3)} rows loaded"
print(message, count)
```

Expected output:

```text
3 rows loaded 3
```

Although newer f-string grammar permits more expression forms, `f"{count := 3}"` is not a safe way to express a walrus: the colon belongs to f-string format-specifier syntax. Use `{(count := 3)}`.

### 4.8 Parentheses and restrictions: quick reference

| Context | Guidance |
| --- | --- |
| `if` / `while` condition | `if (value := compute()):` is clear and widely used |
| Standalone expression statement | Use `(value := compute())`; a bare `value := compute()` is invalid |
| Keyword argument value | Use `func(arg=(value := compute()))`; unparenthesized `arg=value := compute()` is invalid |
| Function default | A parenthesized walrus can parse, but side effects at function definition time are usually a poor design |
| F-string expression | Use `{(value := compute())}` to avoid confusing the `:` with a format specifier |
| Comprehension iterable expression | Prohibited: `[x for x in (items := make_items())]` |
| Comprehension class body | Prohibited for assignment-expression targets inside comprehensions |
| Target of `:=` | Must be a simple name; no attribute or subscript target |
| Rebinding iteration variable | Prohibited within the same comprehension |
| Lambda body | Use parentheses around a walrus expression, e.g. `lambda x: (result := x * 2)` |

Do not memorize parentheses as a vague rule. Learn the context-specific grammar and prefer explicit parentheses when the expression might be ambiguous to a reader.

## 5. Advanced use and design judgment

### 5.1 Lambdas

A lambda can contain a walrus expression in its body:

```python
transform = lambda value: (doubled := value * 2)
print(transform(7))
```

Expected output:

```text
14
```

`doubled` is local to the lambda call's scope; it does not become a useful name outside the lambda. In this simple case, `lambda value: value * 2` is clearer because the temporary adds no value. Do not use `:=` in a lambda merely to make it look sophisticated.

### 5.2 Nested comprehensions

A nested comprehension may assign a computed value into the containing function scope, but this is often harder to read than a loop:

```python
def flatten_positive(matrix: list[list[int]]) -> tuple[list[int], int | None]:
    flattened = [value for row in matrix for item in row
                 if (value := item * 10) > 0]
    # Deliberately unsafe: a non-empty outer list does not prove that the
    # comprehension evaluated its walrus expression (for example, [[]]).
    return flattened, value if matrix else None

print(flatten_positive([[1, -1], [2, 0]]))
```

Expected output:

```text
([10, 20], 0)
```

`value` is bound in `flatten_positive`, not in the comprehension's implicit scope. The final assignment can be `0` from a filtered-out item, so the returned `value` is not necessarily the last element of `flattened`. More importantly, `if matrix` only checks that the outer list is non-empty: calling `flatten_positive([[]])` raises `UnboundLocalError`, because the comprehension never assigns `value`. This is an intentionally unsafe example. A clearer production implementation is:

```python
def flatten_positive_clear(matrix: list[list[int]]) -> list[int]:
    flattened: list[int] = []
    for row in matrix:
        for item in row:
            value = item * 10
            if value > 0:
                flattened.append(value)
    return flattened

print(flatten_positive_clear([[1, -1], [2, 0]]))
```

Expected output:

```text
[10, 20]
```

The loop makes evaluation order and state explicit. Prefer it when nested comprehensions require commentary to explain their side effects.

### 5.3 `match` guards

A walrus expression may appear in a `match` guard when the computed value is useful in that case body:

```python
def route(message: object) -> str:
    match message:
        case str() if (normalized := message.strip().lower()):
            return f"text:{normalized}"
        case str():
            return "text:empty"
        case _:
            return "unsupported"

print(route("  READY "))
print(route("   "))
print(route(42))
```

Expected output:

```text
text:ready
text:empty
unsupported
```

A guard runs only after the pattern matches. If the guard's expression is evaluated, `normalized` is assigned before its truth value is tested. Keep in mind that this is a function-local binding, and do not use the variable in branches where the guard never ran.

### 5.4 Evaluation order, short-circuiting, and side effects

Assignment expressions execute only when evaluation reaches them:

```python
calls = 0

def probe() -> int:
    global calls
    calls += 1
    return calls

if False and (value := probe()):
    print("unreachable")
print(calls)
```

Expected output:

```text
0
```

The right side of `and` is skipped, so `probe()` is not called and `value` is not bound by this expression. Similar care is needed with `or`, conditional expressions, `any()`, `all()`, and generator expressions: short-circuiting can mean some walrus expressions never execute.

Do not hide meaningful I/O, mutation, or expensive work in a long Boolean condition. It complicates breakpoints, error localization, and stack traces. If an exception occurs inside a call used by `:=`, the traceback points to that call/expression line; a compact line can make the exact failing operation harder to isolate. Split complex expressions across lines when debugging or code review benefits from it.

### 5.5 Compare `while (item := read())` with `iter(callable, sentinel)`

The walrus loop is natural when the returned value is also needed in the body:

```python
from io import StringIO

source = StringIO("alpha\nbeta\n")
while (line := source.readline()):
    print(line.rstrip())
```

Expected output:

```text
alpha
beta
```

`iter(callable, sentinel)` repeatedly calls a zero-argument callable and stops when its result equals the sentinel. It is a useful alternative when the sentinel value is unambiguous:

```python
from io import StringIO

source = StringIO("alpha\nbeta\n")
for line in iter(source.readline, ""):
    print(line.rstrip())
```

Expected output is identical:

```text
alpha
beta
```

Comparison:

| Consideration | Walrus `while` loop | `iter(callable, sentinel)` |
| --- | --- | --- |
| Termination | Condition's truth value is false | Callable result equals sentinel using equality |
| Body access to last read | The target name is explicit | The loop variable receives each non-sentinel result |
| Sentinel handling | Any falsy result terminates in the common idiom | Only a result equal to the sentinel terminates |
| Best fit | Result is tested by truthiness, or loop logic needs explicit control | A stable sentinel precisely represents “done” |
| Common caveat | A valid falsy data item can terminate the loop | A valid data item equal to the sentinel cannot be represented as ordinary data |

For `readline()`, the empty string is the EOF sentinel, so both are idiomatic. For a custom reader where `0`, `False`, or an empty value can be legitimate data, do not use a truthiness-based walrus loop unless that behavior is intended.

### 5.6 PEP 572 design guidance and review checklist

PEP 572 introduced assignment expressions to make certain common patterns more direct, not to eliminate normal assignment statements. In code review, ask:

1. Does the walrus prevent duplicated work or make a tested value available exactly where it is needed?
2. Is the target name meaningful, and is its scope obvious?
3. Can a reader understand the condition without mentally executing several assignments?
4. Is the target guaranteed to be assigned before later use, including empty-input and short-circuit cases?
5. Does the expression hide I/O, mutation, or an exception-producing call?
6. Would a separate assignment or ordinary loop be easier to debug and maintain?
7. Is the syntax compatible with the project's minimum Python version?

Avoid multiple walrus assignments in one Boolean expression, walrus-heavy comprehensions, and assignments whose values are not reused. A few saved characters are not a maintainability win.

### 5.7 Linting and tooling

Use the repository's configured linter and formatter rather than relying on personal taste alone. Linters can detect some related problems, such as unused assigned names, overly complex conditions, and style issues, but no single universal rule can decide whether a walrus expression is clearer than a conventional assignment. Exact diagnostics depend on the enabled rule families and tool version. Inspect warnings for ambiguous or unnecessary assignments, and let Python itself reject prohibited rebinding. Check the installed tool version and the project's `pyproject.toml` instead of relying on a remembered rule code.

A useful local workflow is:

```bash
ruff check path/to/module.py
ruff format --check path/to/module.py
python -m compileall -q path/to/module.py
```

A linter does not replace tests, and formatting does not prove that the walrus target is assigned on every control-flow path.

## 6. Performance: measure instead of guessing

A walrus can avoid repeated calculation, but syntax alone does not guarantee a speedup. Function-call cost, comprehension construction, data shape, interpreter version, and the work being performed all matter. Benchmark equivalent behavior with `timeit`.

```python
from timeit import timeit

records = [{"views": i, "quality": (i % 5) + 1} for i in range(10_000)]

def score(record: dict[str, int]) -> int:
    return record["views"] * record["quality"]

def repeated() -> list[int]:
    return [score(row) for row in records if score(row) >= 20]

def cached_in_filter() -> list[int]:
    return [value for row in records if (value := score(row)) >= 20]

# Warm up and check equivalence before timing.
assert repeated() == cached_in_filter()
print("repeated:", timeit(repeated, number=100))
print("walrus:", timeit(cached_in_filter, number=100))
```

The script prints timings that vary by machine, Python build, and system load. Do not copy a specific timing into documentation as a universal result. This example isolates a real algorithmic difference: `repeated()` calls `score()` twice for rows that pass the filter, while `cached_in_filter()` calls it once per row. For trivial arithmetic, the measured difference may be small; for expensive functions, avoiding duplicate work may matter much more.

A fair benchmark should:

- produce equivalent results (assert that first);
- use representative data and enough repetitions;
- avoid printing, disk I/O, or unrelated setup inside the timed function unless that is the real workload;
- run more than once and compare distributions or repeated runs;
- be interpreted in the context of the target Python version and production workload.

## 7. Common mistakes and fixes

| Mistake | Why it is wrong or risky | Better approach |
| --- | --- | --- |
| `if result := compute() > limit:` | Due to operator precedence, `result` receives the Boolean comparison result, not the computed value | `if (result := compute()) > limit:` |
| Calling the same function in the condition and body | Repeats work and can produce inconsistent results if the function has side effects | Bind once with `:=` or use a separate assignment |
| Assuming a walrus target is comprehension-local | Comprehension walrus targets bind in the containing scope | Name it deliberately and avoid using it outside the expression unless needed |
| Assuming iteration variables leak | Comprehension iteration variables are isolated in the implicit comprehension scope | Use the value in the comprehension or assign separately beforehand |
| Using `if (value := mapping.get(key))` when `0` is valid | Truthiness conflates a valid falsy value with absence | Compare with `None` or use a unique sentinel |
| Using a target after an empty comprehension or short-circuited expression | The assignment may never execute | Initialize separately or restructure the control flow |
| Putting several assignments in one condition | Hard to read, debug, and reason about | Split the logic into named statements |
| Using walrus just to make code shorter | Fewer lines can hide scope and side effects | Prefer the clearest implementation |
| `obj.attr := value` or `items[0] := value` | The walrus target must be a simple identifier | Use a normal assignment statement |
| Rebinding a comprehension iteration variable | The language rejects it with `SyntaxError` | Use a distinct target name or a loop |

## 8. Practical use cases

Walrus expressions are often useful in:

- **Streaming and file processing:** read a chunk or line once, test for termination, then process it.
- **Parsing and validation:** keep a regex match object or parsed intermediate value.
- **Filtering data:** calculate a normalized or derived value once and use it both in the filter and output.
- **Configuration lookup:** retain a value while checking for `None` or a sentinel.
- **Control-flow diagnostics:** capture a value needed in a conditional branch, provided the name's scope and lifetime remain clear.

Prefer conventional assignment when the value is reused in many places, when the expression is complex, when error handling is needed, or when a team member must be able to place a breakpoint on the calculation independently.

## 9. Exercises

Try each exercise before reading the hints and solutions.

### Exercise 1 — Single evaluation

Refactor the following so `parse_record(line)` is called only once per line and valid parsed records are appended to `accepted`:

```python
if parse_record(line) is not None:
    accepted.append(parse_record(line))
```

### Exercise 2 — Read until empty

Write a `BytesIO` loop that reads four bytes at a time until EOF and prints each chunk with `repr()`.

### Exercise 3 — Comprehension scope

Predict the output and explain which name is local to the comprehension and which is bound in the containing function:

```python
def example():
    squares = [square for item in [2, 3] if (square := item * item)]
    return squares, square

print(example())
```

### Exercise 4 — Missing versus falsy

A configuration dictionary can contain `"timeout": 0`. Write a condition that prints `timeout configured: 0` rather than treating the value as missing.

### Exercise 5 — Pick the clearer design

Which is clearer and why?

```python
if (normalized := normalize(raw)) and normalized.startswith("prod-"):
    deploy(normalized)
```

or

```python
normalized = normalize(raw)
if normalized and normalized.startswith("prod-"):
    deploy(normalized)
```

Give an answer based on complexity, reuse, and team readability rather than line count alone.

### Exercise 6 — `any()` and short-circuiting

Explain when `candidate` is assigned in this expression and what happens if `values` is empty:

```python
found = any((candidate := value.strip()).startswith("ERR") for value in values)
```

### Exercise 7 — Compare alternatives

Write both a walrus `while` loop and an `iter(callable, sentinel)` loop to read lines from `StringIO` until EOF. State when each form is preferable.

### Exercise 8 — Invalid rebinding

Why is this invalid? Rewrite it correctly.

```python
cleaned = [(item := item.strip()) for item in raw_items]
```

### Exercise 9 — Benchmark design

Design a small `timeit` experiment to compare a repeated computation with a version that computes once. State how you will ensure both implementations return equivalent results.

### Exercise 10 — Review 10 snippets

For each snippet below, label it **keep**, **rewrite**, or **depends**, and explain why.

1. `if (match := pattern.search(text)):`
2. `if (x := get_x()) and (y := get_y()):`
3. `values = [result for item in items if (result := transform(item))]`
4. `if (count := len(records)) > limit:`
5. `while chunk := stream.read(8192):`
6. `if (value := mapping.get(key)):`
7. `message = f"{(size := len(payload))} bytes"`
8. `all((value := normalize(item)) for item in items)`
9. `if (status := get_status()) == "ready":`
10. `if (result := compute()) > threshold: consume(result)`

## 10. Hints

1. Use `is not None` if `None` is the invalid/missing signal.
2. Use a `while` condition that reads once and relies on empty bytes at EOF.
3. `item` is the iteration variable; `square` is assigned by `:=` in the containing function.
4. Compare the retrieved value with `None` if `None` means missing; otherwise use a unique sentinel.
5. Consider how many times `normalized` is used and whether the condition is still easy to scan.
6. Generator expressions short-circuit and may not assign the target for every item.
7. The callable form terminates when the callable result equals the sentinel.
8. Use a different target name or a conventional loop.
9. Benchmark the same data and assert result equality before timing.
10. Consider duplicated work, side effects, target scope, and whether the name is used again.

## 11. Worked solutions

### Solution 1

```python
if (parsed := parse_record(line)) is not None:
    accepted.append(parsed)
```

The call happens once. The explicit `is not None` check preserves valid falsy records such as `0`, `False`, or an empty string if the parser can return them.

### Solution 2

```python
from io import BytesIO

stream = BytesIO(b"abcdefghij")
while (chunk := stream.read(4)):
    print(repr(chunk))
```

Expected output:

```text
b'abcd'
b'efgh'
b'ij'
```

### Solution 3

Expected output:

```text
([4, 9], 9)
```

`item` is local to the comprehension's implicit scope. `square` is a walrus target and is bound in `example()`'s local scope. The final evaluated assignment sets it to `9`.

### Solution 4

```python
config = {"timeout": 0}
if (timeout := config.get("timeout")) is not None:
    print(f"timeout configured: {timeout}")
```

Expected output:

```text
timeout configured: 0
```

If `None` can itself be a configured value, use a unique sentinel with `dict.get()`.

### Solution 5

Both are correct. The walrus version can be reasonable if `normalized` is used only in this condition and its body, and the team finds it easy to read. The separate-assignment version is usually clearer if normalization is non-trivial, is used later, needs a breakpoint, or may raise an exception that deserves a distinct line. Choose based on the surrounding code, not the number of lines.

### Solution 6

`candidate` is assigned for each item the generator expression actually evaluates. `any()` stops on the first truthy result. If `values` is empty, the generator body never runs and `candidate` is never bound by this expression; `found` is `False`. Do not read `candidate` afterward unless assignment is guaranteed.

### Solution 7

```python
from io import StringIO

source = StringIO("first\nsecond\n")
while (line := source.readline()):
    print(line.rstrip())

source = StringIO("first\nsecond\n")
for line in iter(source.readline, ""):
    print(line.rstrip())
```

Both print `first` and `second`. The walrus form uses truthiness; the sentinel form uses equality with `""`. The sentinel form is concise when a unique end marker exists. The walrus form is flexible when the condition is more involved or the read result must be tested by truthiness.

### Solution 8

The original attempts to assign to the comprehension iteration variable `item`, which is prohibited. Use a distinct name:

```python
cleaned = [stripped for item in raw_items if (stripped := item.strip())]
```

This version filters out empty stripped strings and binds `stripped` in the containing scope. If you need to preserve empty strings, do not use the filter; use a conventional comprehension or loop instead:

```python
cleaned = [item.strip() for item in raw_items]
```

### Solution 9

Use equivalent functions and verify equality before timing:

```python
from timeit import timeit

items = list(range(20_000))

def expensive(item: int) -> int:
    return item * item

def twice() -> list[int]:
    return [expensive(item) for item in items if expensive(item) > 100]

def once() -> list[int]:
    return [result for item in items if (result := expensive(item)) > 100]

assert twice() == once()
print(timeit(twice, number=50))
print(timeit(once, number=50))
```

The values printed are machine-dependent measurements. They are not a universal claim that walrus expressions are always faster.

### Solution 10 — Suggested review

1. **Keep** when the match object is reused in the branch; it avoids repeating the search.
2. **Depends / often rewrite.** Two assignments plus short-circuit behavior make the condition harder to reason about. Split it if either call has side effects or distinct failure behavior.
3. **Depends.** Reasonable for a simple transform whose result is used for filtering and output, but the walrus target binds outside the comprehension and the one-line logic can become dense.
4. **Keep or rewrite.** It is reasonable if `count` is used again in the body; otherwise `if len(records) > limit:` is simpler.
5. **Keep** when an empty chunk reliably means EOF and the body uses `chunk`.
6. **Depends / often rewrite.** Incorrect if a valid value can be falsy. Check against `None` or a sentinel when absence is distinct from falsiness.
7. **Depends.** Parentheses make the syntax clear, but a separate `size = len(payload)` is often easier if the size is reused or the f-string is already complex.
8. **Usually rewrite.** It is subtle because `all()` short-circuits, so `value` may hold only a partial result or remain unbound on empty input.
9. **Keep** if `status` is needed in the body and `get_status()` should run once.
10. **Keep** when the result is reused and the expression is simple; split it if `compute()` is complex or debugging warrants a separate line.

## 12. Final integrated exercise — validate and route incoming records

### Scenario

A small data-ingestion utility receives lines such as `"id=42 status=ready"`. It should:

1. Read each line until EOF.
2. Parse the identifier and status once per line using a regular expression.
3. Skip malformed lines.
4. Retain the parsed match object only where that improves clarity.
5. Route `ready` records to an accepted list and all other well-formed records to a review list.
6. Avoid walrus-heavy conditions and handle empty input correctly.
7. Include tests for valid, invalid, and empty input.

### Starter implementation

Complete the TODOs. Keep the API small and make each binding obvious.

```python
import re
from io import StringIO

RECORD_RE = re.compile(r"id=(\d+)\s+status=([a-z]+)")

def route_records(source: StringIO) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    accepted: list[dict[str, str]] = []
    review: list[dict[str, str]] = []

    # TODO: read until EOF with a walrus loop
    # TODO: parse each line exactly once
    # TODO: skip malformed input
    # TODO: build a record and route by status

    return accepted, review
```

### Reference solution

```python
import re
from io import StringIO

RECORD_RE = re.compile(r"id=(\d+)\s+status=([a-z]+)")

def route_records(source: StringIO) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    accepted: list[dict[str, str]] = []
    review: list[dict[str, str]] = []

    while (line := source.readline()):
        if (match := RECORD_RE.fullmatch(line.strip())) is None:
            continue

        record = {"id": match.group(1), "status": match.group(2)}
        if record["status"] == "ready":
            accepted.append(record)
        else:
            review.append(record)

    return accepted, review


def test_route_records() -> None:
    source = StringIO(
        "id=42 status=ready\n"
        "bad line\n"
        "id=43 status=pending\n"
    )
    accepted, review = route_records(source)
    assert accepted == [{"id": "42", "status": "ready"}]
    assert review == [{"id": "43", "status": "pending"}]
    assert route_records(StringIO("")) == ([], [])
    assert route_records(StringIO("bad\n")) == ([], [])


if __name__ == "__main__":
    test_route_records()
    print("all integrated exercise tests passed")
```

Expected output:

```text
all integrated exercise tests passed
```

### Extension challenges

- Add a counter for malformed lines without using a global variable.
- Add a timestamp field and explain whether parsing it inside the comprehension or in a separate statement would be easier to review.
- Benchmark the walrus read loop against an equivalent explicit `while True` loop on a large in-memory input. Check output equality before timing.
- Add a static type checker and explain what it can and cannot prove about variables assigned only in some branches.

## 13. Final self-check

You are ready to move on when you can explain, without running the code:

- why `:=` is an expression and `=` is an assignment statement;
- why `(result := compute()) > limit` differs from `result := compute() > limit`;
- why comprehension iteration variables do not leak but walrus targets bind in the containing scope;
- why empty input and short-circuiting can leave a walrus target unbound;
- why `dict.get()` plus a truth test can misclassify `0` or `False`;
- why a `while` walrus loop and `iter(callable, sentinel)` have different termination rules;
- why performance must be measured rather than inferred from compact syntax;
- when a normal assignment or loop is the better engineering choice.

## Version and compatibility summary

- **Introduced:** Python 3.8 (PEP 572).
- **Repository target:** Python 3.12+.
- **Compatibility:** the core assignment-expression feature works on Python 3.8+, but surrounding syntax and other language features in a larger program may impose a higher minimum version. The operator itself works on Python 3.8+. Because the repository targets Python 3.12+, some examples use modern syntax beyond Python 3.8: built-in generic annotations such as `list[int]` require Python 3.9+, union annotations such as `X | None` require Python 3.10+, and the `match`-guard example requires Python 3.10+. When backporting those examples to Python 3.8, replace annotations with equivalents from `typing` (for example, `List[int]` and `Optional[X]`) and rewrite the `match` example with `if`/`elif`.
- **Design standard:** use `:=` when it removes repeated work or gives a value a clear, local name at the point of testing; prefer ordinary assignment when it improves control flow, debugging, or readability.
