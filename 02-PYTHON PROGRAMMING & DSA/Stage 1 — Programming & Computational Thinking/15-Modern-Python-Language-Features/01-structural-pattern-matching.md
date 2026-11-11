# Structural Pattern Matching in Python

> **Repository policy:** New examples target **Python 3.12+**. Structural pattern matching itself was introduced in **Python 3.10** (PEP 634). The lesson's core `match`/`case` examples therefore require Python 3.10 or newer; examples using `typing.assert_never` require Python 3.11+ for the standard-library helper. No example requires Python 3.12-only syntax unless explicitly stated.
>
> **Lesson path:** `Stage 1 — Programming & Computational Thinking/15-Modern-Python-Language-Features/01-structural-pattern-matching.md`

## 1. Learning objectives and prerequisites

By the end of this lesson, you should be able to:

- Explain what structural pattern matching does and when it is clearer than `if/elif`.
- Read and write `match`/`case` statements using literal, wildcard, capture, OR, AS, sequence, mapping, and class patterns.
- Recognize the crucial difference between a **capture pattern** (`case name:`) and a **value pattern** (`case module.CONSTANT:`).
- Use guards without hiding side effects, and explain first-match/no-fall-through behavior.
- Match dataclasses, enums, `Literal`-based values, `TypedDict`-shaped dictionaries, nested configuration, commands, tokens, and event payloads.
- Design a tagged set of domain variants and use `typing.assert_never` with a static type checker to check exhaustiveness.
- Distinguish matching a shape from validating untrusted data.
- Test matching code, refactor an `isinstance` ladder safely, and select a suitable alternative when `match` is not the best design.

### Prerequisites

You should already know basic variables, strings, lists, tuples, dictionaries, conditionals, functions, exceptions, type hints, and simple classes. Dataclasses and enums are useful but will be introduced briefly where needed.

### Version compatibility

| Capability | Minimum version | Notes |
|---|---:|---|
| `match` / `case` and structural pattern matching | Python 3.10 | Not parseable by Python 3.9 or earlier |
| `X \| Y` union type syntax | Python 3.10 | Used in annotations in this lesson |
| `typing.assert_never` | Python 3.11 | A type-checking helper; runtime function also raises if reached |
| `dataclass(slots=True)` | Python 3.10 | Not needed for matching itself |
| PEP 695 type-parameter syntax such as `def f[T]` | Python 3.12 | Not used in core examples |

For a codebase supporting Python below 3.10, you cannot place `match` syntax in a module that must be parsed by that interpreter. Keep compatible code in a separate module or use `if/elif`, dispatch tables, or polymorphism. A runtime `if sys.version_info` cannot rescue syntax that the old interpreter cannot parse.

---

## 2. Conceptual explanation and mental model

Structural pattern matching is a control-flow statement that compares a subject against a series of patterns. Patterns can test literal values, object types, sequence structure, mapping keys, and nested combinations. They can also bind parts of a matching structure to local names.

It was added by Python 3.10. It is not simply a switch statement: the patterns can describe the *shape* of data, not just a single constant.

### Why it exists

Real programs often branch on structured inputs:

- an API event such as `{"type": "click", "x": 12, "y": 7}`;
- a command such as `["copy", "source.csv", "archive.csv"]`;
- a token or abstract syntax tree (AST) node;
- a domain event represented by a dataclass;
- a tagged result that can be success, retryable failure, or permanent failure.

A long `if/elif` ladder can handle these cases, but it often mixes type checks, nested lookups, and value comparisons. `match` can put the structure being recognized directly in the branch.

### Mental model

Read:

```python
def classify(subject: object) -> str:
    match subject:
        case 0:
            return "zero"
        case 1:
            return "one"
        case _:
            return "other"

print(classify(1))
print(classify("one"))
```

Expected output:

```text
one
other
```

Read this example as:

1. Evaluate `subject` once to obtain the object to inspect.
2. Try cases from top to bottom.
3. For each case, attempt to match the pattern. A successful pattern may bind names.
4. If the pattern succeeds and there is a guard, evaluate the guard. A false guard means this case is not selected.
5. Execute the body of the first case whose pattern and guard both succeed.
6. Continue after the entire `match` statement. There is **no fall-through** to later cases.

`_` is the wildcard pattern: it matches any subject and does not bind a name. It is commonly used as a final fallback, but it is not required syntactically.

Matching does not mutate the subject by itself. However, attribute access, equality comparisons, mapping operations, and guard expressions can run user-defined code or have side effects. Avoid depending on an incidental evaluation order beyond the language's specified matching behavior.

---

## 3. Syntax and terminology

### 3.1 The basic form

```python
def describe(value: object) -> str:
    match value:
        case 0:
            return "zero"
        case 1:
            return "one"
        case _:
            return "something else"

print(describe(1))
print(describe(9))
```

Expected output:

```text
one
something else
```

- `match value:` introduces the statement and its subject.
- Each `case` starts a pattern and a suite.
- `case 0:` is a literal pattern.
- `case _:` matches anything not handled earlier.

The subject expression is evaluated once. If it is a function call, that call is not repeated for every case.

### 3.2 Literal patterns, `None`, booleans, and OR patterns

Literal patterns compare against supported literals. Common examples include numbers, strings, bytes, `None`, and booleans.

```python
def classify(value: object) -> str:
    match value:
        case None:
            return "missing"
        case True:
            return "true boolean"
        case False:
            return "false boolean"
        case 0:
            return "numeric zero"
        case "ready":
            return "ready text"
        case _:
            return "other"

for item in (None, True, False, 0, "ready", 3):
    print(repr(item), "->", classify(item))
```

Expected output:

```text
None -> missing
True -> true boolean
False -> false boolean
0 -> numeric zero
'ready' -> ready text
3 -> other
```

**Order matters for booleans and numbers.** In Python, `bool` is a subclass of `int`, and `True == 1` is true. The language defines the `True` and `False` literal patterns using identity, while numeric literal patterns use equality. Put explicit boolean cases before numeric cases when the distinction matters.

An OR pattern uses `|` to accept one of several alternatives:

```python
def status_group(code: int) -> str:
    match code:
        case 200 | 201 | 204:
            return "success"
        case 301 | 302:
            return "redirect"
        case code if 400 <= code < 500:
            return "client error"
        case _:
            return "other"

print(status_group(204))
print(status_group(302))
print(status_group(404))
print(status_group(503))
```

Expected output:

```text
success
redirect
client error
other
```

Every alternative in an OR pattern must bind the same set of names. For example, `case (("point", x) | ("value", x)):` is valid because both alternatives bind `x`; alternatives binding different names are rejected.

### 3.3 Capture patterns: the most important trap

A bare name is normally a **capture pattern**, not a reference to an existing variable.

```python
def demonstrate(subject: object) -> str:
    match subject:
        case candidate:
            return f"captured {candidate!r}"

print(demonstrate(42))
print(demonstrate("anything"))
```

Expected output:

```text
captured 42
captured 'anything'
```

`case candidate:` matches any subject and binds that subject to `candidate`. It makes later cases unreachable, so do not use a bare capture as though it were a constant comparison.

This is usually wrong:

```python
# WRONG: RED is a capture name, not a comparison to an existing RED.
# match color:
#     case RED:
#         print("red")
```

Use a dotted value pattern:

```python
from enum import Enum

class Color(Enum):
    RED = "red"
    BLUE = "blue"

def color_name(color: Color) -> str:
    match color:
        case Color.RED:
            return "red"
        case Color.BLUE:
            return "blue"
        case _:
            return "unknown"

print(color_name(Color.RED))
```

Expected output:

```text
red
```

The general rule is: **bare identifier = capture; dotted name = value pattern**. `_` is the special wildcard and does not capture.

### 3.4 Guards

A guard is an ordinary boolean expression introduced by `if` after a pattern:

```python
def sign(value: object) -> str:
    match value:
        case int() as n if n > 0:
            return "positive integer"
        case int() as n if n < 0:
            return "negative integer"
        case int():
            return "zero integer"
        case _:
            return "not an integer"

print(sign(8))
print(sign(-2))
print(sign(0))
print(sign("8"))
```

Expected output:

```text
positive integer
negative integer
zero integer
not an integer
```

The pattern must succeed before its guard runs. A false guard allows later cases to be considered. A guard can use captured names, but it should generally be a simple, side-effect-free predicate. A guard that sends a network request, changes global state, or consumes an iterator makes control flow harder to reason about.

`int()` is a class pattern, and it also matches `bool` because `bool` subclasses `int`. If booleans must be excluded, test them explicitly or use a stricter validation rule.

### 3.5 Compare with `if/elif`

The same status logic can be written without `match`:

```python
def status_group_if(code: int) -> str:
    if code in (200, 201, 204):
        return "success"
    elif code in (301, 302):
        return "redirect"
    elif 400 <= code < 500:
        return "client error"
    else:
        return "other"
```

Both versions are reasonable. `match` becomes more valuable when branches inspect nested shapes, object types, and extracted values. For a handful of simple boolean conditions, `if/elif` is often more direct.

---

## 4. Trace pattern selection and variable binding

Consider:

```python
def describe_pair(value: object) -> str:
    match value:
        case [first, second] if first == second:
            return f"equal: {first}"
        case [first, second]:
            return f"different: {first}, {second}"
        case [first, *rest]:
            return f"first={first}; remaining={rest}"
        case _:
            return "not a supported sequence shape"

print(describe_pair([4, 4]))
print(describe_pair([4, 9]))
print(describe_pair([4, 9, 12]))
print(describe_pair("hi"))
```

Expected output:

```text
equal: 4
different: 4, 9
first=4; remaining=[9, 12]
not a supported sequence shape
```

Trace the third input, `[4, 9, 12]`:

1. The first pattern requires exactly two sequence elements, so it fails.
2. The second pattern also requires exactly two elements, so it fails.
3. `[first, *rest]` requires at least one element. It binds `first = 4` and `rest = [9, 12]`.
4. The third body runs; later cases are not evaluated.

Sequence-pattern captures are local names. The starred name captures the remaining elements as a list. Use `_` for a part you do not need, as in `[first, *_]`.

**Important:** names bound during a failed pattern should not be relied on. The language deliberately leaves some partial binding details unspecified for failed matches. Bind and use captures only in a case body after the complete pattern succeeds.

---

## 5. Intermediate patterns

### 5.1 Sequence patterns

Sequence patterns describe a sequence's length and elements:

```python
def parse_record(row: object) -> str:
    match row:
        case [name, score]:
            return f"{name}: {score}"
        case [name, score, *extras]:
            return f"{name}: {score} (extras={extras})"
        case _:
            return "invalid row shape"

print(parse_record(["Mira", 91]))
print(parse_record(["Dev", 88, "late", "reviewed"]))
print(parse_record(["too-short"]))
```

Expected output:

```text
Mira: 91
Dev: 88 (extras=['late', 'reviewed'])
invalid row shape
```

A starred capture can appear only once in a sequence pattern. It can capture zero or more elements. `*rest` binds a list; `*_` ignores those elements.

Strings, bytes, and bytearray objects **do not match sequence patterns**, even though they are iterable. If you want to inspect a string, use string operations or a literal pattern. If a command arrives as a string, split it explicitly before matching its tokens.

Other common sequence patterns:

```python
match (10, 20, 30):
    case (x, y, z):
        print(x, y, z)
    case _:
        print("no match")

match [1, 2, 3, 4]:
    case [first, *middle, last]:
        print(first, middle, last)
```

Expected output:

```text
10 20 30
1 [2, 3] 4
```

Parentheses and square brackets both express sequence structure; they do not require the subject to have exactly the same bracket style. Sequence patterns support sequence types recognized by Python's pattern-matching rules, not arbitrary iterables.

### 5.2 Mapping patterns

Mapping patterns check for required keys and recursively match their values:

```python
def event_summary(event: object) -> str:
    match event:
        case {"type": "click", "pos": (x, y)}:
            return f"click at ({x}, {y})"
        case {"type": "scroll", "dy": delta}:
            return f"scroll by {delta}"
        case _:
            return "unknown event"

print(event_summary({"type": "click", "pos": (5, 8), "user": "u-17"}))
print(event_summary({"type": "scroll", "dy": -3}))
print(event_summary({"type": "click", "pos": [5, 8]}))
```

Expected output:

```text
click at (5, 8)
scroll by -3
click at (5, 8)
```

The first mapping has an extra `"user"` key and still matches. Mapping patterns require the specified keys but allow extra keys by default. A nested tuple pattern `(x, y)` matches a two-element sequence, so the list `[5, 8]` is also accepted for `pos`.

Use `**rest` to capture extra mapping entries:

```python
payload = {"kind": "metric", "value": 12.5, "source": "batch-7"}

match payload:
    case {"kind": "metric", "value": value, **rest}:
        print(value)
        print(rest)
    case _:
        print("not a metric")
```

Expected output:

```text
12.5
{'source': 'batch-7'}
```

`**rest` must be a name (not `_`) and may occur only once at the end of a mapping pattern. It captures the remaining key-value pairs in a new dictionary. It does not mean “no extra keys”; if you need to reject extras, explicitly compare the key set or validate the schema separately.

### 5.3 Class patterns and dataclasses

A class pattern checks whether an object is an instance of the named class (or compatible subclass) and then matches selected attributes.

```python
from dataclasses import dataclass

@dataclass
class Click:
    x: int
    y: int

@dataclass
class Key:
    char: str

def handle_event(event: object) -> str:
    match event:
        case Click(x=0, y=0):
            return "origin click"
        case Click(x, y) if x == y:
            return "diagonal click"
        case Click(x, y):
            return f"click at {x},{y}"
        case Key(char="q"):
            return "quit"
        case {"type": "scroll", "dy": dy}:
            return f"scroll {dy}"
        case [command, *args]:
            return f"{command} with {args}"
        case _:
            raise ValueError(f"unsupported event: {event!r}")

print(handle_event(Click(0, 0)))
print(handle_event(Click(3, 3)))
print(handle_event(Click(3, 5)))
print(handle_event(Key("q")))
print(handle_event({"type": "scroll", "dy": -2}))
print(handle_event(["copy", "a.csv", "b.csv"]))
```

Expected output:

```text
origin click
diagonal click
click at 3,5
quit
scroll -2
copy with ['a.csv', 'b.csv']
```

The dataclass generates `__match_args__` by default from eligible fields, so `Click(x, y)` is positional matching for `x` and `y`. Keyword matching (`Click(x=0, y=0)`) is usually easier to maintain when classes have many fields. Class patterns do not validate field annotations: `Click("left", None)` can still be constructed unless your own validation prevents it.

A class can control positional matching with `__match_args__`:

```python
class Coordinate:
    __match_args__ = ("latitude", "longitude")

    def __init__(self, latitude: float, longitude: float) -> None:
        self.latitude = latitude
        self.longitude = longitude

point = Coordinate(12.9, 77.6)

match point:
    case Coordinate(lat, lon):
        print(lat, lon)
```

Expected output:

```text
12.9 77.6
```

`__match_args__` maps positional subpatterns to attribute names. Keyword patterns name attributes directly and do not depend on the tuple's ordering. A malformed or inconsistent `__match_args__` can make positional matching raise errors, so avoid changing it casually in a public API.

### 5.4 Value patterns, constants, and enums

Use dotted names for constants:

```python
from enum import Enum

class EventKind(Enum):
    CREATED = "created"
    DELETED = "deleted"

def action_for(kind: EventKind) -> str:
    match kind:
        case EventKind.CREATED:
            return "insert"
        case EventKind.DELETED:
            return "remove"
        case _:
            return "unknown"

print(action_for(EventKind.CREATED))
print(action_for(EventKind.DELETED))
```

Expected output:

```text
insert
remove
```

A value pattern such as `EventKind.CREATED` compares against the named value. A bare name such as `CREATED` captures the subject instead. A dotted name is not the only possible value pattern, but using a module/class-qualified constant is the clearest convention and avoids accidental captures.

### 5.5 AS patterns, nesting, and guards together

An AS pattern both matches a nested pattern and binds the matched object:

```python
@dataclass
class Point:
    x: int
    y: int

points = [Point(0, 0), Point(4, 4)]

match points:
    case [Point(x=0, y=0) as origin, Point(x=a, y=b) as other] if a == b:
        print(f"origin={origin}; other={other}")
    case _:
        print("not the expected pair")
```

Expected output:

```text
origin=Point(x=0, y=0); other=Point(x=4, y=4)
```

- The outer pattern requires a two-element sequence.
- The first element must be a `Point` at the origin and is also bound to `origin`.
- The second must be a `Point`; its attributes are bound to `a` and `b`, and the object is bound to `other`.
- The guard then checks `a == b`.

Use AS patterns when both the full object and some of its fields are useful. Avoid over-nesting patterns until the branch becomes difficult to scan; a helper function may be clearer.

### 5.6 Pattern-combination rules to remember

- OR patterns use `|`, and all alternatives must bind the same names.
- AS patterns use `pattern as name`; the name binds the whole matched object.
- A guard follows a complete pattern: `case pattern if condition:`.
- A sequence pattern can have at most one starred subpattern.
- A mapping pattern can have at most one `**rest`, and it must be last.
- Literal and value patterns test values; capture patterns bind names.
- A capture pattern such as `case item:` is irrefutable by itself. It cannot be followed by another case in the same `match` because no later case could be reached.
- `_` is the wildcard and binds nothing.
- Parentheses can group patterns and may be necessary to make combinations unambiguous.

---

## 6. Advanced engineering patterns

### 6.1 Exhaustiveness with enums and `typing.assert_never`

A final wildcard case is a runtime fallback, but it does not prove to a type checker that all domain variants have been handled. For a closed set of variants, use a union of types and `assert_never` after the cases.

```python
from dataclasses import dataclass
from typing import assert_never

@dataclass(frozen=True)
class Created:
    record_id: str

@dataclass(frozen=True)
class Deleted:
    record_id: str
    reason: str

@dataclass(frozen=True)
class RetryRequested:
    record_id: str
    attempt: int

DomainEvent = Created | Deleted | RetryRequested

def describe_domain_event(event: DomainEvent) -> str:
    match event:
        case Created(record_id=record_id):
            return f"created {record_id}"
        case Deleted(record_id=record_id, reason=reason):
            return f"deleted {record_id}: {reason}"
        case RetryRequested(record_id=record_id, attempt=attempt):
            return f"retry {record_id}, attempt {attempt}"
    assert_never(event)

print(describe_domain_event(Created("r-1")))
print(describe_domain_event(Deleted("r-2", "duplicate")))
print(describe_domain_event(RetryRequested("r-3", 2)))
```

Expected output:

```text
created r-1
deleted r-2: duplicate
retry r-3, attempt 2
```

When a static checker understands the declared union, it can narrow `event` after the `match`; if a new union variant is added and omitted, it should report that `event` is not `Never` at the `assert_never` call. `typing.assert_never` is in Python 3.11+. Check the behavior of your chosen mypy or pyright version and strictness settings; tools differ in diagnostics and may not prove every dynamic scenario.

A corresponding enum example is:

```python
from enum import Enum
from typing import assert_never

class JobState(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    FINISHED = "finished"

def describe_state(state: JobState) -> str:
    match state:
        case JobState.QUEUED:
            return "waiting"
        case JobState.RUNNING:
            return "in progress"
        case JobState.FINISHED:
            return "complete"
    assert_never(state)

print(describe_state(JobState.RUNNING))
```

Expected output:

```text
in progress
```

With a compatible checker and appropriate configuration, adding a new enum member without a corresponding branch can make the final `assert_never(state)` fail static analysis. Exact diagnostics vary by checker and settings; this is not a guarantee that every tool proves enum exhaustiveness by default.

Do not replace the final assertion with `case _:` if you want the checker to detect newly added variants—the wildcard can hide the omission. If runtime input can contain unexpected values, validate it at the boundary and decide explicitly how to handle the invalid case.

### 6.2 `Literal` and `TypedDict`: matching is not validation

`Literal` and `TypedDict` describe intended shapes to static type checkers. They do not enforce those shapes on data at runtime.

```python
from typing import Literal, TypedDict

class ClickPayload(TypedDict):
    type: Literal["click"]
    x: int
    y: int

class ErrorPayload(TypedDict):
    type: Literal["error"]
    message: str

Payload = ClickPayload | ErrorPayload

def summarize_payload(payload: Payload) -> str:
    match payload:
        case {"type": "click", "x": x, "y": y} if (
            isinstance(x, int) and not isinstance(x, bool)
            and isinstance(y, int) and not isinstance(y, bool)
        ):
            return f"click ({x}, {y})"
        case {"type": "error", "message": message} if isinstance(message, str):
            return f"error: {message}"
        case _:
            return "invalid or unsupported payload"

print(summarize_payload({"type": "click", "x": 2, "y": 9}))
print(summarize_payload({"type": "error", "message": "offline"}))
print(summarize_payload({"type": "click", "x": "2", "y": 9}))
print(summarize_payload({"type": "click", "x": True, "y": 9}))
```

Expected output:

```text
click (2, 9)
error: offline
invalid or unsupported payload
invalid or unsupported payload
```

The mapping pattern checks for keys and nested values; the guards check basic runtime types. The `TypedDict` annotation helps static analysis, but it does not parse JSON or reject malformed dictionaries at runtime. For untrusted input, validate explicitly (or use a dedicated boundary-validation library) before domain logic. Also decide whether extra keys are allowed; mapping patterns allow them by default.

### 6.3 Dataclasses and sum-type-style domain models

A **sum type** means a value can be one of a known set of alternatives. Python commonly models this with a union of dataclasses. Each variant has a distinct class, so the `match` branches are explicit and type checkers can narrow fields.

```python
from dataclasses import dataclass
from typing import assert_never

@dataclass(frozen=True, slots=True)
class Add:
    left: int
    right: int

@dataclass(frozen=True, slots=True)
class Negate:
    value: int

@dataclass(frozen=True, slots=True)
class Literal:
    value: int

Expression = Add | Negate | Literal

def evaluate(expr: Expression) -> int:
    match expr:
        case Add(left=a, right=b):
            return a + b
        case Negate(value=n):
            return -n
        case Literal(value=n):
            return n
    assert_never(expr)

print(evaluate(Add(2, 3)))
print(evaluate(Negate(4)))
print(evaluate(Literal(11)))
```

Expected output:

```text
5
-4
11
```

`frozen=True` prevents ordinary attribute reassignment and `slots=True` reduces per-instance storage overhead in many cases; neither option makes the model a security boundary or deeply immutable if fields contain mutable objects. `assert_never` makes missing variants visible to supported static checkers.

### 6.4 AST/interpreter-style evaluator

Pattern matching is especially readable when each syntax node represents a different form of expression. This small evaluator uses tuple nodes for teaching purposes.

```python
from typing import TypeAlias

Expr: TypeAlias = int | tuple[object, ...]

def eval_expr(expr: Expr) -> int:
    match expr:
        case int() as value if not isinstance(value, bool):
            return value
        case ("lit", int() as value) if not isinstance(value, bool):
            return value
        case ("neg", operand):
            return -eval_expr(operand)  # recursive evaluation
        case ("add", left, right):
            return eval_expr(left) + eval_expr(right)
        case _:
            raise ValueError(f"invalid expression: {expr!r}")

print(eval_expr(("add", ("lit", 4), ("neg", 2))))
print(eval_expr(7))
```

Expected output:

```text
2
7
```

This example is intentionally compact; for a production interpreter, define a recursive static type for each AST variant, validate parsed input, constrain recursion/depth, and report errors with source locations. The annotation above is permissive because recursive tuple aliases and dynamic input are simplified for teaching. Do not assume matching alone makes an arbitrary tuple a valid AST.

### 6.5 CLI command parsing

A sequence pattern can match token lists, but it should not be applied directly to a command string. Tokenization and validation are separate steps.

```python
def parse_command(tokens: list[str]) -> tuple[str, tuple[str, ...]]:
    match tokens:
        case ["copy", source, destination]:
            return ("copy", (source, destination))
        case ["delete", path]:
            return ("delete", (path,))
        case ["help"]:
            return ("help", ())
        case []:
            raise ValueError("empty command")
        case [unknown, *_]:
            raise ValueError(f"unknown or malformed command: {unknown!r}")

for tokens in (
    ["copy", "in.csv", "out.csv"],
    ["delete", "tmp.csv"],
    ["help"],
):
    print(parse_command(tokens))
```

Expected output:

```text
('copy', ('in.csv', 'out.csv'))
('delete', ('tmp.csv',))
('help', ())
```

A real CLI should use `argparse` for conventional argument parsing, quoting, help, and error reporting. Pattern matching is useful after arguments have been tokenized into a known representation.

### 6.6 Configuration trees and structured events

Nested mapping patterns can express required configuration shape:

```python
def choose_batch_size(config: object) -> int:
    match config:
        case {"pipeline": {"batch_size": int() as size}} if (
            not isinstance(size, bool) and 1 <= size <= 10_000
        ):
            return size
        case _:
            raise ValueError("pipeline.batch_size must be an integer from 1 to 10000")

print(choose_batch_size({"pipeline": {"batch_size": 500}, "owner": "analytics"}))
```

Expected output:

```text
500
```

Because `bool` is a subclass of `int`, `{"batch_size": True}` would satisfy `int()` and the numeric range guard. If booleans are invalid, add `and not isinstance(size, bool)` to the guard. Also consider whether the configuration loader should reject unknown keys; the mapping pattern shown does not.

For event processing, matching makes a useful *routing* layer, but it does not replace schema validation, authorization, idempotency, retry policy, or observability.

### 6.7 Tokens and nested data

A lexer may emit tokens such as `("NUMBER", 12)` or `("OP", "+")`. Sequence patterns can route token shapes, but check token types before using their payloads:

```python
def token_description(token: object) -> str:
    match token:
        case ("NUMBER", int() as number) if not isinstance(number, bool):
            return f"number {number}"
        case ("IDENT", str() as name):
            return f"identifier {name}"
        case ("OP", "+" | "-" | "*" | "/"):
            return "arithmetic operator"
        case _:
            return f"invalid token: {token!r}"

print(token_description(("NUMBER", 12)))
print(token_description(("IDENT", "total")))
print(token_description(("OP", "+")))
print(token_description(("NUMBER", "12")))
```

Expected output:

```text
number 12
identifier total
arithmetic operator
invalid token: ('NUMBER', '12')
```

---

## 7. Pattern evaluation semantics and pitfalls

### 7.1 First match, guards, and no fall-through

Only the first case whose pattern and guard succeed executes. There is no implicit fall-through, so no `break` is needed. If the body completes, execution continues after `match`.

```python
def route(value: object) -> str:
    match value:
        case int() as n if n > 10:
            return "large"
        case int():
            return "integer"
        case _:
            return "other"

print(route(12))
print(route(4))
print(route("12"))
```

Expected output:

```text
large
integer
other
```

If the first pattern matches but its guard is false, Python tries later cases. Keep guards predictable and free from side effects where possible.

### 7.2 Subject and pattern evaluation

- The subject expression is evaluated once.
- Cases are considered in source order.
- Patterns may access attributes or compare values. Objects can customize behavior through properties, equality methods, mapping/sequence protocols, and metaclasses.
- Do not depend on incidental ordering of every sub-operation in a complex pattern. The language specification leaves some ordering details intentionally flexible.
- Avoid property getters that mutate state or perform expensive I/O when used in class patterns.
- A guard executes only after its pattern succeeds. A false guard does not roll back arbitrary side effects caused by that guard.
- Do not use captures from a failed pattern. Partial bindings after failure are not a reliable contract.

### 7.3 Matching does not validate untrusted data

A mapping pattern such as `{"type": "click", "x": x}` says the mapping has at least those keys and that their values match their subpatterns. It does not prove that:

- every field has the intended type;
- no unexpected keys exist;
- values are within allowed ranges;
- the caller is authorized;
- the data is safe to use in SQL, shell commands, paths, or logs.

Use validation at trust boundaries. Pattern matching can then make domain branching clear after the data has been validated.

### 7.4 Common mistakes

| Mistake | Why it fails | Better approach |
|---|---|---|
| `case RED:` to compare with a constant | It captures the subject in `RED` | Use `case Color.RED:` or another dotted constant |
| Capture case before specific cases | It matches everything and shadows later cases | Put specific patterns first |
| Expecting `"abc"` to match `[a, b, c]` | Strings and bytes are excluded from sequence patterns | Use string operations or tokenize first |
| Assuming exact dictionary keys | Mapping patterns allow extra keys | Compare keys or validate separately if exactness matters |
| Treating `TypedDict` as runtime validation | Annotations do not enforce shape at runtime | Validate incoming data explicitly |
| Treating `int()` as “integer but not bool” | `bool` is a subclass of `int` | Exclude booleans explicitly |
| Overusing positional class patterns | Field order may change or be unclear | Prefer keyword patterns for public/domain models |
| Writing complex side-effecting guards | Control flow becomes hard to reason about | Keep guards pure; calculate first if needed |
| Assuming `case _` proves exhaustiveness | It accepts future variants without a type-checker warning | Use a typed union and `assert_never` where appropriate |
| Assuming `match` is faster | Speed depends on workload and interpreter | Benchmark representative code |
| Using `match` for a two-branch condition | Adds ceremony without structural benefit | Use `if/else` |
| Matching raw external payloads and trusting captures | Pattern shape is not complete validation | Validate at the boundary, then match |

---

## 8. Refactor an `isinstance` ladder without changing behavior

Suppose a handler supports three object types and rejects all others:

```python
from dataclasses import dataclass

@dataclass
class CreatedRecord:
    record_id: str

@dataclass
class DeletedRecord:
    record_id: str

def old_handler(event: object) -> str:
    if isinstance(event, CreatedRecord):
        return f"created:{event.record_id}"
    elif isinstance(event, DeletedRecord):
        return f"deleted:{event.record_id}"
    else:
        raise TypeError(f"unsupported event: {event!r}")
```

A behavior-preserving `match` version is:

```python
def new_handler(event: object) -> str:
    match event:
        case CreatedRecord(record_id=record_id):
            return f"created:{record_id}"
        case DeletedRecord(record_id=record_id):
            return f"deleted:{record_id}"
        case _:
            raise TypeError(f"unsupported event: {event!r}")
```

Before merging a refactor, preserve all observable behavior:

1. Same supported input types, including subclass behavior.
2. Same branch precedence if types overlap through inheritance.
3. Same return values and side effects.
4. Same exception class and meaningful message for unsupported inputs.
5. Same treatment of `None`, malformed objects, and missing attributes.
6. Tests covering every branch and the fallback.

Class patterns also use instance checks, but they additionally access attributes. A class pattern may fail to match if a requested attribute is absent; property access can raise or have side effects. Therefore, do not assume every refactor is equivalent merely because the happy path looks similar. Characterization tests are valuable for legacy behavior.

A class pattern is not a general “has these attributes” structural duck-typing test: it checks the subject against the named class (including subclasses), then matches attributes. A `Protocol` annotation alone does not change that runtime rule. If your design intentionally accepts unrelated objects by shape, use explicit attribute validation or a suitable runtime-checkable protocol where its limits are understood.

---

## 9. Testing strategy and edge cases

Test both successful patterns and negative cases. Include exact boundary values, wrong types, extra keys, missing keys, empty sequences, strings/bytes, and unexpected classes. `pytest` is optional; the following tests use the standard library and can be run with Python 3.12+.

```python
import unittest
from dataclasses import dataclass

@dataclass
class ClickEvent:
    x: int
    y: int

def classify_event(value: object) -> str:
    match value:
        case ClickEvent(x=0, y=0):
            return "origin"
        case ClickEvent(x=x, y=y) if (
            isinstance(x, int) and not isinstance(x, bool)
            and isinstance(y, int) and not isinstance(y, bool)
        ):
            return "click"
        case {"type": "scroll", "dy": int() as dy} if not isinstance(dy, bool):
            return "scroll"
        case _:
            return "invalid"

class TestClassifyEvent(unittest.TestCase):
    def test_origin(self):
        self.assertEqual(classify_event(ClickEvent(0, 0)), "origin")

    def test_other_click(self):
        self.assertEqual(classify_event(ClickEvent(2, 3)), "click")

    def test_scroll(self):
        self.assertEqual(classify_event({"type": "scroll", "dy": -1}), "scroll")

    def test_missing_key(self):
        self.assertEqual(classify_event({"type": "scroll"}), "invalid")

    def test_wrong_type(self):
        self.assertEqual(classify_event({"type": "scroll", "dy": "down"}), "invalid")

    def test_bool_is_not_accepted_as_integer_delta(self):
        self.assertEqual(classify_event({"type": "scroll", "dy": True}), "invalid")

    def test_string_is_not_a_sequence_pattern_here(self):
        self.assertEqual(classify_event("scroll"), "invalid")

    def test_unrelated_object(self):
        self.assertEqual(classify_event(object()), "invalid")

if __name__ == "__main__":
    unittest.main()
```

Expected test result when run as a script:

```text
........
----------------------------------------------------------------------
Ran 8 tests in ...
OK
```

The exact elapsed time is environment-dependent; the output above illustrates the expected test summary, not a measured runtime.

A test suite should also cover malformed serialized input before it reaches this function. For example, `json.loads()` can return a list, string, number, or `None` as well as a dictionary. Do not annotate untrusted decoded data as a valid `TypedDict` without checking it.

### Optional pytest form

```python
import pytest

@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (ClickEvent(0, 0), "origin"),
        (ClickEvent(1, 2), "click"),
        ({"type": "scroll", "dy": 3}, "scroll"),
        ({"type": "scroll"}, "invalid"),
        ({"type": "scroll", "dy": True}, "invalid"),
        ("scroll", "invalid"),
    ],
)
def test_classify_event(value, expected):
    assert classify_event(value) == expected
```

---

## 10. Performance: measure, do not assume

`match` is primarily a clarity and correctness tool, not a promise of faster execution. Do not assume patterns are precompiled into a faster dispatch table or that pattern matching has a universal performance advantage. A flat dictionary lookup may be simpler and fast for a stable mapping from a small set of hashable keys to handlers. A complex structural pattern may perform type checks, key lookups, attribute access, and guards. The result depends on data distribution, Python version, and surrounding work.

Use `timeit` or a profiler on representative inputs before optimizing. Keep the benchmark honest: identical behavior, same inputs, warm-up/repetition as appropriate, and no unrelated I/O in one version but not the other.

Example benchmark scaffold (run locally; no timings are claimed here):

```python
from timeit import timeit

def via_match(code: int) -> str:
    match code:
        case 200 | 201 | 204:
            return "success"
        case 301 | 302:
            return "redirect"
        case _:
            return "other"

TABLE = {
    200: "success",
    201: "success",
    204: "success",
    301: "redirect",
    302: "redirect",
}

def via_dict(code: int) -> str:
    return TABLE.get(code, "other")

samples = [200, 302, 404, 204, 503] * 100

print("match:", timeit(lambda: [via_match(x) for x in samples], number=1_000))
print("dict: ", timeit(lambda: [via_dict(x) for x in samples], number=1_000))
```

This is a starting point, not proof that one approach is universally faster. For real systems, profile the application first. In a hot loop, small dispatch differences may be irrelevant compared with parsing, allocation, database calls, or network latency.

---

## 11. Choosing the right design

| Situation | Usually consider | Why |
|---|---|---|
| Two simple boolean branches | `if/else` | Less ceremony |
| Several numeric ranges or unrelated predicates | `if/elif` | Conditions read naturally |
| Flat finite mapping from key to function/value | Dictionary dispatch | Data-driven, easy to extend |
| Many variants with distinct behavior owned by each object | Polymorphic methods | Behavior stays with the type |
| Nested sequences/mappings or a tagged set of domain variants | `match` | Structure and extracted fields are visible |
| CLI argument parsing with conventional help/errors | `argparse` | Handles tokenization and standard CLI semantics |
| Untrusted JSON/API input | Explicit validation, then `match` | Matching alone does not enforce a schema |
| Must support Python 3.9 or older | `if/elif`, mapping, or polymorphism | Old interpreters cannot parse `match` syntax |
| Performance-critical dispatch | Benchmark alternatives | Do not infer speed from syntax |

### Dictionary dispatch example

```python
def create_report() -> str:
    return "report"

def create_export() -> str:
    return "export"

HANDLERS = {
    "report": create_report,
    "export": create_export,
}

def dispatch(command: str) -> str:
    try:
        handler = HANDLERS[command]
    except KeyError:
        raise ValueError(f"unknown command: {command!r}") from None
    return handler()

print(dispatch("report"))
```

Expected output:

```text
report
```

Use a dispatch table when the operation is simply “look up this key and call its handler.” Use `match` when selection depends on a shape, nested values, or a combination of type and structure. These approaches can also be combined: match a structured command, then use a table for a flat sub-dispatch.

---

## 12. Hands-on exercises

Try each exercise before reading its solution. Use Python 3.12+ for all examples.

### Exercise 1 — status classifier

Write `status_group(code)` that returns `"success"` for 200/201/204, `"redirect"` for 301/302, `"client error"` for 400–499, and `"other"` otherwise.

**Hint:** Use OR patterns for the fixed values and a guard for the range.

<details>
<summary>Solution</summary>

```python
def status_group(code: int) -> str:
    match code:
        case 200 | 201 | 204:
            return "success"
        case 301 | 302:
            return "redirect"
        case n if 400 <= n < 500:
            return "client error"
        case _:
            return "other"
```

Note that the annotation does not enforce the input type at runtime. If arbitrary values can reach this function, add explicit validation.
</details>

### Exercise 2 — parse a row

Accept a two-element row `[name, score]` and return `"name=..., score=..."`. If the row has a third or later field, report the extras. Reject other shapes.

**Hint:** Put the exact-length case before the starred case.

<details>
<summary>Solution</summary>

```python
def describe_row(row: object) -> str:
    match row:
        case [name, score]:
            return f"name={name}, score={score}"
        case [name, score, *extras]:
            return f"name={name}, score={score}, extras={extras}"
        case _:
            return "invalid row"
```
</details>

### Exercise 3 — find the capture bug

Explain the bug and correct this attempted function:

```python
def is_ready(value: str) -> bool:
    READY = "ready"
    match value:
        case READY:
            return True
        case _:
            return False
```

**Hint:** A bare identifier in a pattern captures the subject. Because that capture is irrefutable, the following case is unreachable and Python rejects this code with a `SyntaxError`; it does not run and always return `True`. Use a literal or dotted constant.

<details>
<summary>Solution</summary>

```python
READY = "ready"

def is_ready(value: str) -> bool:
    match value:
        case "ready":
            return True
        case _:
            return False
```

Alternatively, define a constants namespace and use a dotted value pattern. A local or global bare name does not become a constant pattern.
</details>

### Exercise 4 — event payload

Write a function that accepts `{"type": "metric", "name": str, "value": int-or-float}` and returns a summary. Reject booleans as numeric values and reject missing/wrongly typed fields.

**Hint:** Mapping patterns allow extra keys. Remember that `bool` is a subclass of `int`.

<details>
<summary>Solution</summary>

```python
def metric_summary(payload: object) -> str:
    match payload:
        case {"type": "metric", "name": str() as name, "value": (int() | float()) as value} if not isinstance(value, bool):
            return f"{name}={value}"
        case _:
            raise ValueError(f"invalid metric payload: {payload!r}")
```

The pattern checks the required keys and value types. If the contract disallows extra keys, validate the key set explicitly.
</details>

### Exercise 5 — exhaustiveness

Create two dataclass variants, `Started(job_id)` and `Finished(job_id, count)`. Write a function that handles both and calls `assert_never` for an unhandled variant.

**Hint:** Annotate the parameter as `Started | Finished`; use Python 3.11+ for `typing.assert_never`.

<details>
<summary>Solution</summary>

```python
from dataclasses import dataclass
from typing import assert_never

@dataclass(frozen=True)
class Started:
    job_id: str

@dataclass(frozen=True)
class Finished:
    job_id: str
    count: int

JobEvent = Started | Finished

def describe_job_event(event: JobEvent) -> str:
    match event:
        case Started(job_id=job_id):
            return f"started {job_id}"
        case Finished(job_id=job_id, count=count):
            return f"finished {job_id}: {count}"
    assert_never(event)
```

Run a static checker in strict mode and verify how it reports an added, unhandled union variant. Runtime tests alone do not establish static exhaustiveness.
</details>

### Exercise 6 — design choice

For each task, choose `match`, `if/elif`, a dictionary, or polymorphism and justify your choice:

1. Convert a fixed set of string command names to handler functions.
2. Evaluate nested arithmetic AST nodes.
3. Check whether a number is in a range.
4. Give each domain object its own `render()` behavior.

**Hint:** Choose the simplest design that exposes the decision clearly.

<details>
<summary>Suggested solution</summary>

1. Dictionary dispatch is often clearest for a flat key-to-handler map.
2. `match` works well for a closed set of AST variants and recursive evaluation.
3. `if/elif` is usually clearest for a simple numeric range.
4. Polymorphism keeps behavior with each object when the type owns the behavior.
</details>

---

## 13. Integrated mini-project: event router for a data pipeline

### Goal

Build a small event router that accepts structured internal events and returns deterministic action descriptions. It demonstrates class patterns, mapping patterns, guards, input checks, and a clear error path.

### Requirements

- Accept typed dataclass events for `RecordCreated` and `RecordRejected`.
- Accept a mapping payload for a `"heartbeat"` event.
- Reject malformed values instead of silently treating them as valid.
- Keep routing logic separate from external I/O.
- Test supported cases, malformed data, and boundary values.

### Implementation

Save as `event_router.py`:

```python
from dataclasses import dataclass
from typing import assert_never


@dataclass(frozen=True, slots=True)
class RecordCreated:
    record_id: str
    row_count: int


@dataclass(frozen=True, slots=True)
class RecordRejected:
    record_id: str
    reason: str


DomainEvent = RecordCreated | RecordRejected


def route_domain_event(event: DomainEvent) -> str:
    """Return a routing decision for an internal domain event."""
    match event:
        case RecordCreated(record_id=record_id, row_count=count):
            if isinstance(count, bool) or not isinstance(count, int) or count < 0:
                raise ValueError("row_count must be a non-negative integer")
            return f"publish:{record_id}:{count}"
        case RecordRejected(record_id=record_id, reason=reason):
            if not reason.strip():
                raise ValueError("rejection reason must not be blank")
            return f"quarantine:{record_id}:{reason}"
    assert_never(event)


def route_external_payload(payload: object) -> str:
    """Inspect an external mapping only after checking its required fields."""
    match payload:
        case {"type": "heartbeat", "service": str() as service, "lag_seconds": lag} if (
            isinstance(lag, (int, float))
            and not isinstance(lag, bool)
            and 0 <= lag <= 86_400
        ):
            return f"heartbeat:{service}:lag={lag}"
        case _:
            raise ValueError(f"invalid external event payload: {payload!r}")


def route(event: object) -> str:
    """Route either a typed internal event or an external heartbeat payload."""
    match event:
        case RecordCreated() as domain_event:
            return route_domain_event(domain_event)
        case RecordRejected() as domain_event:
            return route_domain_event(domain_event)
        case dict():
            return route_external_payload(event)
        case _:
            raise TypeError(f"unsupported event type: {type(event).__name__}")


if __name__ == "__main__":
    print(route(RecordCreated("batch-42", 120)))
    print(route(RecordRejected("batch-43", "schema mismatch")))
    print(route({"type": "heartbeat", "service": "ingest", "lag_seconds": 3.5}))
```

Expected output:

```text
publish:batch-42:120
quarantine:batch-43:schema mismatch
heartbeat:ingest:lag=3.5
```

### Implementation notes

- `RecordCreated` and `RecordRejected` model a closed set of internal domain variants. Their dataclass annotations are not runtime validation, so constructors or boundary code should enforce invariants.
- `route_domain_event` uses `assert_never` after matching the union. A static checker can flag newly added variants that are not handled.
- `route_external_payload` treats the payload as `object`, checks the mapping shape, and validates the numeric range. It rejects `bool`, despite `bool` being an `int` subclass.
- The heartbeat pattern permits extra keys. Add exact-key validation if the external contract requires it.
- The router returns strings rather than performing I/O. Production code can interpret the routing decision in a separate layer, which makes tests deterministic.

### Tests

Save as `test_event_router.py` in the same directory:

```python
import unittest

from event_router import (
    RecordCreated,
    RecordRejected,
    route,
)


class TestEventRouter(unittest.TestCase):
    def test_created(self):
        self.assertEqual(route(RecordCreated("b-1", 0)), "publish:b-1:0")

    def test_rejected(self):
        self.assertEqual(
            route(RecordRejected("b-2", "bad schema")),
            "quarantine:b-2:bad schema",
        )

    def test_negative_row_count_rejected(self):
        with self.assertRaises(ValueError):
            route(RecordCreated("b-bad", -1))

    def test_boolean_row_count_rejected(self):
        with self.assertRaises(ValueError):
            route(RecordCreated("b-bad", True))

    def test_blank_rejection_reason_rejected(self):
        with self.assertRaises(ValueError):
            route(RecordRejected("b-bad", "   "))

    def test_heartbeat(self):
        self.assertEqual(
            route({"type": "heartbeat", "service": "ingest", "lag_seconds": 2}),
            "heartbeat:ingest:lag=2",
        )

    def test_heartbeat_boundary(self):
        self.assertEqual(
            route({"type": "heartbeat", "service": "ingest", "lag_seconds": 86400}),
            "heartbeat:ingest:lag=86400",
        )

    def test_negative_lag_rejected(self):
        with self.assertRaises(ValueError):
            route({"type": "heartbeat", "service": "ingest", "lag_seconds": -1})

    def test_bool_lag_rejected(self):
        with self.assertRaises(ValueError):
            route({"type": "heartbeat", "service": "ingest", "lag_seconds": True})

    def test_missing_field_rejected(self):
        with self.assertRaises(ValueError):
            route({"type": "heartbeat", "service": "ingest"})

    def test_unknown_event_rejected(self):
        with self.assertRaises(TypeError):
            route("heartbeat")


if __name__ == "__main__":
    unittest.main()
```

Run:

```bash
python -m unittest -v
```

Expected result: all eight tests pass. This is the expected behavior from inspection; do not report tests as executed unless you actually run them in the target environment.

### Extension tasks

1. Add a `RecordRetried` dataclass and update the union, router, and tests. Confirm your type checker flags an omitted case before you implement it.
2. Decide whether heartbeat payloads may contain extra keys. Implement and test your chosen policy.
3. Add a schema version to external events and route unsupported versions to a clear validation error.
4. Benchmark only if routing is shown by profiling to be a meaningful cost.

---

## 14. Production use cases

Structural pattern matching is useful in data engineering and backend systems when the input has recognizable structure:

- **Ingestion event routing:** distinguish created, rejected, retried, and completed records.
- **Log and telemetry processing:** classify structured event payloads by `"type"` and extract fields.
- **Configuration interpretation:** inspect nested configuration after schema validation.
- **Token processing and interpreters:** route syntax nodes and token shapes.
- **CLI commands:** route already-tokenized arguments; use `argparse` for the parser itself.
- **API response handling:** branch on a tagged result, provided the response has been validated.
- **State machines:** handle explicit state/event combinations. For large or extensible state machines, a dedicated transition table may be easier to maintain.
- **Data quality rules:** match known record variants, then apply explicit field-level checks.

Production guardrails:

1. Validate untrusted data before domain processing.
2. Keep patterns readable; extract helpers for deep or repeated logic.
3. Prefer keyword class patterns for long-lived domain models.
4. Keep guards pure and cheap.
5. Use explicit error cases for unknown or malformed variants.
6. Use static typing and `assert_never` for closed unions where supported.
7. Add tests for every branch and the fallback.
8. Measure performance in the real workload rather than relying on syntax-based assumptions.

---

## 15. Readability and code-review checklist

Before approving a `match` statement, ask:

- [ ] Is `match` clearer than the equivalent `if/elif` or dispatch table?
- [ ] Are specific patterns placed before broad patterns?
- [ ] Is every bare identifier intentionally a capture?
- [ ] Are constants written as literals or dotted names?
- [ ] Do all OR alternatives bind the same names?
- [ ] Are sequence and mapping shapes understood correctly?
- [ ] Are extra mapping keys intentionally allowed or explicitly rejected?
- [ ] Are booleans distinguished from integers when necessary?
- [ ] Are guards side-effect-free and easy to understand?
- [ ] Is malformed or unsupported input handled intentionally?
- [ ] Is runtime validation separate from static annotations?
- [ ] Would a type checker detect newly added variants where exhaustiveness matters?
- [ ] Are version requirements compatible with the project's minimum Python?
- [ ] Are tests covering normal, boundary, malformed, and unmatched inputs?
- [ ] Has performance been measured if this code is on a demonstrated hot path?

---

## 16. Summary and mastery checklist

Structural pattern matching lets Python branch on values and structure using `match` and `case`. Literal patterns recognize known values; capture patterns bind names; guards add predicates; sequence, mapping, and class patterns describe nested data; OR and AS patterns combine or retain matches. The first successful case runs, and there is no fall-through.

The biggest correctness trap is confusing a bare capture (`case RED:`) with a constant comparison (`case Color.RED:`). The biggest production trap is confusing a successful shape match with validation of untrusted input. Matching is not automatically exhaustive, either: typed unions plus `assert_never` and a capable static checker can help detect missing variants.

Before moving on, make sure you can:

- [ ] Explain why structural pattern matching was introduced and when to use it.
- [ ] Explain subject evaluation, first-match behavior, wildcard `_`, and no fall-through.
- [ ] Write literal, `None`, boolean, OR, capture, and guarded patterns.
- [ ] Explain why `case x:` matches nearly anything and why `case Color.RED:` is different.
- [ ] Match sequences, starred captures, mappings, nested mappings, and class instances.
- [ ] Explain why strings/bytes do not match sequence patterns.
- [ ] Use `**rest`, AS patterns, dataclasses, enums, and `__match_args__`.
- [ ] Match `Literal`/`TypedDict`-shaped data while keeping runtime validation explicit.
- [ ] Use a typed union and `assert_never` for static exhaustiveness checks.
- [ ] Refactor an `isinstance` ladder without changing behavior.
- [ ] Test unmatched inputs, malformed data, boundaries, and type traps.
- [ ] Choose rationally between `match`, `if/elif`, dictionary dispatch, and polymorphism.
- [ ] Explain that `match` requires Python 3.10+ and new repository code targets Python 3.12+.

**Self-check questions**

1. Why does `case RED:` capture instead of compare, and how do you write the comparison?
2. Why can a mapping pattern match a dictionary that has extra keys?
3. Why is `isinstance(value, int)` not enough if booleans are invalid?
4. What does `assert_never` contribute that `case _:` does not?
5. When would a dispatch dictionary or polymorphic method be more maintainable than `match`?
