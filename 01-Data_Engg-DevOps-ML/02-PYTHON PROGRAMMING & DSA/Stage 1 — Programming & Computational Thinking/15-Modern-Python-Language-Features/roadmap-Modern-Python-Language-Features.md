# Roadmap — Module 1.15: Modern Python Language Features

This is the learning roadmap for the fifteenth module of Stage 1,
**Programming & Computational Thinking**. It tells you **what** to learn
about the language features added in Python 3.8 → 3.14, **in what order**,
**how** to practise each topic, and **how to prove to yourself** that you
have learned it.

Python has changed substantially in the last few years: structural pattern
matching, assignment expressions, positional-only parameters, exception
groups, new generic syntax, deferred annotation evaluation, better error
messages, a faster interpreter, template strings, and an optional JIT and
free-threaded build. Production codebases mix several versions of
"Pythonic" style. A senior engineer reads **old and new** code fluently,
modernises it deliberately, and knows which features are safe to use for the
Python versions they must support.

> **Version policy for this repository:** write new code for **Python 3.12+**.
> Each lesson flags the version that introduced a feature so you can judge
> compatibility when supporting older versions.

---

## 1. Module outcome

By the end of this module you will be able to:

- Use `match`/`case` with literal, sequence, mapping, class, guard and OR
  patterns, and know when `if/elif` or a dispatch table is better.
- Use the walrus operator `:=` where it improves clarity and avoid it where it hurts.
- Design function signatures with positional-only (`/`), keyword-only (`*`),
  `*args`, `**kwargs` and defaults, and evolve them without breaking callers.
- Use exception chaining (`raise ... from`), `add_note`, custom hierarchies, and
  write good error messages.
- Handle concurrent failures with `ExceptionGroup` and `except*`.
- Write modern generics (`class Box[T]`, `def f[T](x: T)`, `type` aliases),
  `TypedDict`, `Required`/`NotRequired`, `Self`, `override`, `TypeIs`, `ReadOnly`.
- Use advanced `dataclass` features (`slots`, `kw_only`, `frozen`, `__post_init__`,
  `InitVar`, `field`) and explain when `attrs`/Pydantic are the better tool.
- Explain f-string internals (PEP 701), formatting specs, and 3.14 template strings.
- Emit and filter warnings, and run a deprecation cycle.
- Summarise key differences between Python 3.10 → 3.14 and plan a migration.

---

## 2. Prerequisites

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Conditionals, boolean logic | Module 1.3 (01) | `match` extends branching |
| Function parameters, defaults | Module 1.3 (03, 04) | Signature design |
| Exceptions and useful errors | Module 1.3 (07) | Chaining, groups |
| Type hints and checking | Modules 1.6 (06), 1.9 (05) | Modern generics |
| Dataclasses | Module 1.8 (03) | Advanced options |
| Decorators / metaprogramming | Modules 1.9 (02), 1.12 | Understand `@override`, `dataclass_transform` |
| Standard library toolkit | Module 1.13 | Combining features |
| Tooling (`ruff`, `mypy`/`pyright`) | Module 1.6 | Enforcing modern style (`pyupgrade` rules) |

**Tools:** `uv` with multiple Python versions (`uv python install 3.10 3.12 3.14`),
`ruff` (rules `UP`, `B`, `SIM`), `mypy` or `pyright`, `pytest`, `tox`/`nox` (preview).

---

## 3. How the module is organised

```text
Phase A — Control Flow and Signatures            (Basics)
  01 structural pattern matching
  02 assignment expressions
  03 positional-only, keyword-only, star arguments
Phase B — Errors and Types                       (Intermediate)
  04 exception chaining, notes, hierarchies
  05 exception groups and except*
  06 modern generics, TypedDict, type parameter syntax
Phase C — Data and Text                          (Intermediate)
  07 advanced dataclasses and attrs
  08 f-string internals and template strings
Phase D — Evolution and Compatibility            (Advanced)
  09 warnings and deprecations
  10 Python version differences, 3.10 → 3.14
```

Pace: about 3 weeks part-time.

---

## Lesson 01 — `01-structural-pattern-matching.md`

**Why it matters.** `match` replaces long `isinstance` / `if-elif`
chains when handling structured data: parsed commands, AST nodes, API
event payloads, JSON-like dicts, tokens. It makes intent explicit and
exhaustive.

### Basic — what to learn

- Syntax: `match subject:` + `case pattern:`; first matching case wins; `_` wildcard.
- Literal patterns (ints, strings, `None`, `True/False`) and OR patterns `1 | 2 | 3`.
- Capture patterns bind names: `case x:` captures **anything** (careful!).
- Guards: `case n if n > 0:`.

```python
def http_status(code: int) -> str:
    match code:
        case 200 | 201 | 204:
            return "success"
        case 301 | 302:
            return "redirect"
        case code if 400 <= code < 500:
            return "client error"
        case _:
            return "other"
```

### Intermediate — what to learn

- **Sequence patterns**: `[x, y]`, `[first, *rest]`, `(a, b, *_)`; do not match `str`/`bytes`.
- **Mapping patterns**: `{"type": "click", "pos": (x, y)}`; extra keys are allowed; `**rest`.
- **Class patterns**: `Point(x=0, y=0)`, positional patterns via `__match_args__`
  (dataclasses provide it automatically).
- **Value patterns** with dotted names (`Color.RED`, `config.MAX`) — bare names are captures, not comparisons.
- **AS patterns**: `case [Point() as p1, Point() as p2]:`.
- Nested patterns and combining with guards.

```python
from dataclasses import dataclass

@dataclass
class Click: x: int; y: int
@dataclass
class Key: char: str

def handle(event):
    match event:
        case Click(x=0, y=0):             return "origin click"
        case Click(x, y) if x == y:       return "diagonal"
        case Click(x, y):                 return f"click {x},{y}"
        case Key(char="q"):               return "quit"
        case {"type": "scroll", "dy": dy}: return f"scroll {dy}"
        case [cmd, *args]:                return f"{cmd} with {args}"
        case _:                           raise ValueError(event)
```

### Advanced — what to learn

- Exhaustiveness: pairing `match` with `typing.assert_never` and enums/unions so
  type checkers flag unhandled variants.
- Performance and semantics: evaluation order, side effects in guards, no fall-through,
  pattern compilation; compare with dict dispatch for flat literals.
- Matching on `Enum`, `Literal`, `TypedDict` shapes, and `Protocol`-like duck structures
  via class patterns and `__match_args__`.
- Designing ADT-style models (sum types) with dataclasses/enums and matching over them;
  the interpreter/visitor pattern using `match` (AST evaluator).
- Parsing CLI commands, tokens or config trees with sequence+mapping patterns.
- Pitfalls: capturing names that shadow existing variables, forgetting dotted names for constants,
  mutable captures, matching strings as sequences.
- When **not** to use it: simple two-branch conditions, polymorphism (use methods),
  hot loops (profile), code that must run on Python < 3.10.
- Readability review checklist; refactoring `isinstance` ladders into `match`.

### Common mistakes

- `case RED:` (a capture!) instead of `case Color.RED:`.
- Expecting `str` to match sequence patterns.
- Using `match` where a dictionary lookup would be clearer.

### Self-check

1. Why does `case RED:` always match, and how do you fix it?
2. Write an expression evaluator for `("add", a, b)`, `("neg", a)`, `("lit", n)` tuples with `match`.
3. How do you make a type checker prove your `match` over an enum is exhaustive?

---

## Lesson 02 — `02-assignment-expressions-and-walrus-operator.md`

**Why it matters.** `:=` assigns **and** returns a value inside an
expression, removing repeated computation and awkward loops. Used well it
shortens code; used badly it hides side effects.

### Basic — what to learn

- Syntax: `(name := expr)`; parentheses are usually required.
- Common uses: `while chunk := f.read(n):`, `if (m := pattern.search(s)):`,
  filtering with a computed value in comprehensions.

```python
import re
if (m := re.search(r"id=(\d+)", "x id=42 y")):
    print(int(m.group(1)))

with open("big.bin", "rb") as f:
    while chunk := f.read(65536):
        process(chunk)
```

### Intermediate — what to learn

- Scope rule: in a comprehension, the target binds in the **enclosing** scope.
- Avoiding double computation: `[y for x in data if (y := expensive(x)) > 0]`.
- Where it is **not allowed** unparenthesised: top-level statements, keyword argument
  defaults, f-string expressions without parentheses.
- Style: prefer it only when it removes duplication or a temporary variable
  without reducing clarity.
- Combining with `any()` / `all()`, regex checks, `dict.get`, and `next(...)`.

```python
results = [y for x in range(10) if (y := x * x) % 2 == 0]
print(results, y)       # y leaks to enclosing scope (last value)
```

### Advanced — what to learn

- Interactions with `match` guards, lambdas, and nested comprehensions; disallowed
  patterns (rebinding the iteration variable).
- Readability review: when a separate assignment line is clearer; team style guides
  (PEP 572 guidance; `ruff` rules).
- Performance: saves recomputation; measure with `timeit`.
- Walrus in `while True` loops vs sentinel `iter(callable, sentinel)`.
- Debugging implications: breakpoints and stack traces on one-liners.
- Compatibility: Python 3.8+.
- Refactoring exercise: take 10 snippets and decide, with reasons, whether `:=` helps.

### Common mistakes

- Overusing in conditions with multiple assignments.
- Forgetting the comprehension leak into the outer scope.
- Using it to be clever.

### Self-check

1. What scope does `y` have in `[y for x in data if (y := f(x))]`?
2. Rewrite a read-until-empty loop using `:=` and using `iter(callable, sentinel)`; compare.
3. Give one case where `:=` makes code worse.

---

## Lesson 03 — `03-positional-only-keyword-only-and-star-argument-design.md`

**Why it matters.** The signature is the contract of your API. Positional-only
and keyword-only parameters let you evolve functions without breaking
callers, prevent argument-order bugs (`transfer(a, b, 100)`), and are used
throughout the standard library.

### Basic — what to learn

- Recap `*args` (tuple) and `**kwargs` (dict); unpacking at call sites `f(*xs, **kw)`.
- **Keyword-only** after `*`: `def f(a, *, flag=False)`.
- **Positional-only** before `/` (3.8+): `def f(a, b, /, c)`.
- The full signature order: `def f(pos_only, /, pos_or_kw, *, kw_only, **kwargs)` (with `*args` replacing bare `*`).

```python
def transfer(src: str, dst: str, /, *, amount: int, dry_run: bool = False) -> None: ...

transfer("A", "B", amount=100)            # ok
# transfer("A", "B", 100)                 # TypeError: amount is keyword-only
```

### Intermediate — what to learn

- Why use keyword-only for booleans/flags/units/optional behaviour: call sites document themselves.
- Why use positional-only: names are not part of the API; allows renaming; mirrors C builtins (`len(obj, /)`).
- Default values: evaluated once; **mutable default trap**; `None` sentinel pattern;
  custom sentinels (`_MISSING = object()`) when `None` is meaningful.
- Forwarding arguments: `*args, **kwargs` wrappers and typing them (`ParamSpec`).
- `inspect.signature` to see parameter kinds; `functools.wraps` preserves them.
- Argument validation and error messages for unexpected kwargs.

```python
_MISSING = object()

def get(d: dict, key, default=_MISSING):
    try:
        return d[key]
    except KeyError:
        if default is _MISSING:
            raise
        return default
```

### Advanced — what to learn

- **API evolution rules**: adding an optional keyword-only parameter is safe;
  reordering, renaming positional-or-keyword parameters or tightening defaults is breaking;
  deprecating a parameter with warnings (links to lesson 09).
- `TypedDict` + `Unpack[...]` (PEP 692) to type `**kwargs` precisely.
- Overloads (`typing.overload`) for functions whose return type depends on arguments.
- Function design heuristics: ≤ 4–5 parameters; group related ones into a dataclass
  (parameter object); avoid boolean flag parameters that change behaviour (split functions).
- Variadic design: `*args` for homogeneous inputs, `**kwargs` forwarding only when you truly forward.
- Positional-only for dunder/operator-like functions; handling name collisions between a
  positional-only name and `**kwargs` keys.
- Call-site readability review; lint rules (`FBT` boolean trap, `PLR0913` too many arguments).
- Binding semantics with `functools.partial` and keyword-only parameters.

### Common mistakes

- Mutable default arguments.
- Boolean positional flags (`process(data, True, False)`).
- `**kwargs` swallowing typos silently.

### Self-check

1. Which parameters of `def f(a, /, b, *, c)` can be passed by keyword?
2. Why is adding a new keyword-only parameter with a default non-breaking?
3. Redesign `export(data, True, False, 3)` into a safe, self-documenting signature.

---

## Lesson 04 — `04-exception-chaining-notes-and-custom-hierarchies.md`

**Why it matters.** In production the question is rarely "did it fail?" but
"why, where, and with what context?". Chained exceptions, notes and
well-designed hierarchies make failures diagnosable and handleable by callers.

### Basic — what to learn

- Recap `try/except/else/finally`, catching specific exceptions, re-raising with `raise`.
- Implicit chaining (`__context__`) vs explicit `raise NewError(...) from err`
  (`__cause__`); suppressing with `from None` (and when that is appropriate).
- Reading chained tracebacks: "The above exception was the direct cause…" vs "During handling…".

```python
class ConfigError(Exception): ...

def load(path):
    try:
        return open(path).read()
    except FileNotFoundError as err:
        raise ConfigError(f"config file missing: {path}") from err
```

### Intermediate — what to learn

- **Custom exception hierarchies**: one base per library/package
  (`class AppError(Exception)`), specific subclasses (`ValidationError`, `NotFoundError`),
  attributes carrying structured data (field, value, code), `__str__`.
- `add_note()` (3.11+) to attach context while propagating without wrapping:
  `err.add_note(f"while processing {file}")`.
- `__traceback__`, `with_traceback`, `traceback.format_exception`, `logging.exception`.
- Don't catch `Exception` broadly; never bare `except:`; avoid `except Exception: pass`.
- `contextlib.suppress`, `try/finally` cleanup, context managers handling exceptions.
- Exception design for APIs: translating low-level errors into domain errors at boundaries.

```python
try:
    parse(line)
except ValueError as err:
    err.add_note(f"line {lineno}: {line!r}")
    raise
```

### Advanced — what to learn

- Error taxonomy: **programmer errors** (bugs: let them crash/log), **operational
  errors** (retry/handle), **validation errors** (report to the user); map each to
  exception types and HTTP/exit codes (links to Module 1.10 lesson 03).
- Exceptions as part of the public API: document `Raises:`, keep stable, deprecate carefully.
- Performance: exceptions are cheap on success path (zero-cost try in 3.11+) but costly when raised frequently — avoid for control flow in hot loops.
- Pickle/multiprocessing-safe exceptions (constructor args must round-trip).
- Retry logic: classify transient vs permanent; exponential backoff + jitter; exception
  groups for aggregated failures (lesson 05).
- Logging: log once at the boundary with full traceback; avoid log-and-raise duplication.
- `sys.excepthook`, `threading.excepthook`, `asyncio` exception handlers; top-level crash reporting.
- Error messages guidance: what happened, what was expected, how to fix; no secrets in messages.
- Testing exceptions: `pytest.raises(match=...)`, checking `__cause__` and notes.

### Common mistakes

- Losing the original cause by raising a new exception without `from`.
- Catching and returning `None` silently.
- Creating exceptions with required constructor args that break pickling.

### Self-check

1. Difference between `__cause__` and `__context__`?
2. When is `raise ... from None` justified?
3. Design an exception hierarchy for an ingestion library and show how a caller handles transient vs permanent failures.

---

## Lesson 05 — `05-exception-groups-and-except-star.md`

**Why it matters.** Concurrent code (`asyncio.TaskGroup`, threads, batch
validation) can fail in several ways at once. `ExceptionGroup` (3.11+) models
multiple unrelated failures, and `except*` handles them selectively.

### Basic — what to learn

- `ExceptionGroup("msg", [exc1, exc2, ...])`; `BaseExceptionGroup`.
- `except* TypeError:` handles the matching subset; unmatched exceptions are re-raised as a group.
- `asyncio.TaskGroup` raises an `ExceptionGroup` when children fail.

```python
try:
    raise ExceptionGroup("batch", [ValueError("a"), TypeError("b"), ValueError("c")])
except* ValueError as eg:
    print("values:", [str(e) for e in eg.exceptions])
except* TypeError as eg:
    print("types:", [str(e) for e in eg.exceptions])
```

### Intermediate — what to learn

- Group methods: `.exceptions`, `.subgroup(predicate)`, `.split(predicate)`; nested groups.
- Rules: you cannot mix `except` and `except*` in one `try`; `return`/`break`/`continue`
  are not allowed inside `except*`; handlers must not catch the group itself with plain `except` expecting a single type.
- Collecting validation errors: validate all records, raise one group with all failures
  instead of failing on the first (better UX for bulk ingestion).
- `asyncio.TaskGroup` vs `gather(return_exceptions=True)` semantics (structured concurrency).
- Adding notes to groups; formatting tracebacks of groups.
- `concurrent.futures` collecting exceptions from futures into a group.

```python
def validate_all(rows):
    errors = []
    for i, r in enumerate(rows):
        try:
            validate(r)
        except ValueError as e:
            e.add_note(f"row {i}")
            errors.append(e)
    if errors:
        raise ExceptionGroup("validation failed", errors)
```

### Advanced — what to learn

- Cancellation: `asyncio.CancelledError` is a `BaseException`; how it is handled inside groups.
- Splitting retryable vs fatal errors with `split()` and re-raising only fatal ones.
- Designing APIs that surface groups vs a single aggregated domain error; compatibility
  for callers on Python < 3.11 (`exceptiongroup` backport).
- Testing: `pytest.raises(ExceptionGroup)` and `excinfo.group_contains` (pytest 8+).
- Logging and tracing groups (flatten for structured logs).
- Interplay with context managers (`ExitStack` raising groups on multiple cleanup failures).
- Failure-mode analysis: partial success, rollback vs best-effort continuation.
- Reading `TaskGroup` source / docs to see how groups form.

### Common mistakes

- Using plain `except ValueError` and missing errors wrapped in a group.
- Trying to `return` inside `except*`.
- Swallowing part of a group unintentionally.

### Self-check

1. What happens to unmatched exceptions in a group?
2. Why can't `except` and `except*` mix in one `try`?
3. Write a bulk validator that reports all invalid rows as one group and a test that inspects the group.

---

## Lesson 06 — `06-modern-generics-typeddict-and-type-parameter-syntax.md`

**Why it matters.** Typed Python is standard in production and in AI
libraries (FastAPI, Pydantic, LangChain-style frameworks). The modern syntax
is clearer and less ceremonious than `TypeVar` boilerplate.

### Basic — what to learn

- Built-in generics: `list[int]`, `dict[str, int]`, `tuple[int, ...]`, `X | None` (3.9/3.10+).
- `TypedDict` for dictionary shapes: `class Movie(TypedDict): title: str; year: int`;
  `total=False`, `Required`/`NotRequired`.
- `Literal`, `Final`, `ClassVar`, `Annotated`, `Callable`, `Iterator`, `Sequence`, `Mapping`.

```python
from typing import TypedDict, NotRequired

class User(TypedDict):
    id: int
    email: str
    nickname: NotRequired[str]

def greet(u: User) -> str:
    return f"hi {u.get('nickname', u['email'])}"
```

### Intermediate — what to learn

- **PEP 695 syntax (3.12+)**: `def first[T](xs: Sequence[T]) -> T`, `class Stack[T]:`,
  and `type Pair[T] = tuple[T, T]` aliases; bounds `[T: Hashable]` and constraints `[T: (int, str)]`;
  `ParamSpec` (`**P`) and `TypeVarTuple` (`*Ts`) in the same syntax.
- Old style (`TypeVar("T")`, `Generic[T]`) for pre-3.12 compatibility.
- `Self` (3.11) for fluent/builder methods; `@override` (3.12) to catch signature drift;
  `@final`.
- `Protocol` with generics; `Callable[[int], str]` vs `Callable[..., Any]`.
- Variance: invariance (`list`), covariance (`Sequence`, `tuple`), contravariance; **PEP 695 infers variance automatically**.
- `NewType`, `TypeAlias`, `cast`, `TYPE_CHECKING` imports.

```python
class Stack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []
    def push(self, x: T) -> None: self._items.append(x)
    def pop(self) -> T: return self._items.pop()

type Handler[T] = Callable[[T], None]
```

### Advanced — what to learn

- `TypeIs` (3.13) / `TypeGuard` for custom narrowing; `assert_never`; `assert_type`.
- `ReadOnly` in `TypedDict` (3.13); `Unpack` for `**kwargs` typing.
- Runtime vs static: annotations are not enforced; reading them at runtime
  (`get_type_hints`), **deferred evaluation in 3.14** (PEP 649/749), `from __future__ import annotations`, and what each means for Pydantic/FastAPI/dataclasses.
- `dataclass_transform` for frameworks; `Protocol` vs ABC (Module 1.11 lesson 10).
- Overloads and `@overload` precision; generics in classes with bounded types for repository/service layers.
- Type-checker differences (mypy vs pyright vs pyrefly/ty): strictness config, `py.typed`, stubs, `# type: ignore[code]` hygiene.
- Gradual typing strategy for legacy code: start at boundaries, strict for new modules, track coverage.
- Typed config and data contracts: TypedDict vs dataclass vs Pydantic — decision table.

### Common mistakes

- Typing everything as `Any` or `dict`.
- Using `list[int]` for parameters where `Sequence[int]` is the contract.
- Assuming annotations validate data at runtime.

### Self-check

1. Rewrite a `TypeVar`/`Generic` class using PEP 695 syntax.
2. When should a parameter be `Sequence[T]` rather than `list[T]`?
3. Type a decorator that preserves the wrapped function's signature using `ParamSpec`.

---

## Lesson 07 — `07-advanced-dataclasses-and-attrs.md`

**Why it matters.** Data-holding classes are everywhere: records, configs,
DTOs, events. Dataclasses remove boilerplate, but their options and edge
cases (mutability, defaults, inheritance, slots) cause real bugs.

### Basic — what to learn

- `@dataclass` generates `__init__`, `__repr__`, `__eq__`; `field(default=..., default_factory=list)`.
- `frozen=True` (immutable + hashable with `eq=True`), `order=True`, `slots=True`, `kw_only=True`.
- Mutable defaults are rejected — use `default_factory`.

```python
from dataclasses import dataclass, field

@dataclass(frozen=True, slots=True, kw_only=True)
class Event:
    name: str
    tags: tuple[str, ...] = ()
    meta: dict = field(default_factory=dict, compare=False)
```

### Intermediate — what to learn

- `__post_init__` for validation/derived fields; `InitVar` for init-only parameters;
  `field(init=False, repr=False, compare=False, hash=...)`.
- `dataclasses.asdict`, `astuple`, `replace`, `fields`, `is_dataclass`; `KW_ONLY` sentinel.
- Inheritance: field ordering with defaults, `kw_only` to avoid "non-default after default" errors.
- `frozen` + `__post_init__` assignments via `object.__setattr__`; `slots=True` pitfalls with `cached_property`
  and `super()`.
- `match_args`, `weakref_slot`, `dataclass_transform`.
- Comparison with `NamedTuple` (immutable, tuple behaviour), `TypedDict` (plain dict at runtime), `attrs`, Pydantic.

```python
@dataclass
class Order:
    qty: int
    price: float
    total: float = field(init=False)
    def __post_init__(self):
        if self.qty <= 0:
            raise ValueError("qty must be positive")
        self.total = self.qty * self.price
```

### Advanced — what to learn

- **attrs**: validators, converters, `define`/`frozen`, `evolve`, slots by default,
  `attrs` vs dataclasses (richer features, older, cattrs for structuring).
- **Pydantic v2** vs dataclasses: runtime validation/coercion, serialisation, JSON Schema,
  performance (Rust core) — when parsing untrusted input, use Pydantic at the boundary and plain dataclasses inside (Stage 2 and Stage 7 coverage).
- Immutability strategies: deep vs shallow immutability (`frozen` with a `list` field is still mutable inside); `tuple`/`frozenset`/`MappingProxyType`.
- Hashing/equality design (Module 1.11 lesson 01) with `frozen` and `unsafe_hash`.
- Serialisation round-trips: `asdict` recursion, custom encoders, versioned schemas;
  dates/Decimals/enums; avoid pickling dataclasses for storage.
- Performance and memory: slots dataclasses for millions of records; compare to NamedTuple and columnar structures.
- Copy-on-modify patterns using `replace`; builder patterns; state transitions as new objects.
- Testing dataclasses: equality assertions, property-based generation (`hypothesis.strategies.builds`).

### Common mistakes

- `frozen=True` with mutable containers, assuming deep immutability.
- Default shared state through class-level mutable defaults.
- Using `asdict` for huge objects in hot paths.

### Self-check

1. What does `__post_init__` run after, and how do you assign a field in a frozen dataclass inside it?
2. Why does `kw_only=True` fix the "non-default argument follows default argument" error in inheritance?
3. Choose between dataclass, NamedTuple, TypedDict, attrs and Pydantic for: a config, a DB row, an API payload, an in-memory event.

---

## Lesson 08 — `08-f-string-internals-and-template-strings.md`

**Why it matters.** String formatting is in every line of logging, CLI
output, SQL building (dangerous), prompts for LLMs, and reports. Knowing
the internals prevents bugs, and **t-strings** (3.14) give a safe way to
build structured output.

### Basic — what to learn

- f-strings: `{expr}`, `{expr!r}`, `{expr:spec}`, `{x=}` debug form.
- Format spec mini-language: fill/align (`<^>`), sign, `#`, `0`, width, grouping (`,` `_`), precision,
  type (`d f e g % x b o s`).
- Dates: `f"{dt:%Y-%m-%d}"`; nested specs `f"{x:{width}.{prec}f}"`.

```python
x, w = 1234567.891, 14
print(f"{x:>{w},.2f}|{x=:.1f}|{42:#06x}|{0.256:.1%}")
```

### Intermediate — what to learn

- **PEP 701 (3.12)**: f-strings parsed by the real grammar — nested quotes
  of the same type, multi-line expressions, backslashes and comments inside expressions.
- Evaluation: expressions run at runtime in order; side effects; cost of formatting in logging
  (use `%`-style lazy args: `logger.debug("x=%s", x)`).
- `__format__` and `format(obj, spec)`; `str.format`/`format_map`; `%` formatting
  where still required (logging, bytes).
- Multi-line strings, `textwrap.dedent`, joining templates; avoiding giant f-strings.
- Debugging with `!r`, `=`; formatting floats and Decimals; locale-aware formatting (`locale`, `babel`).
- Prompt templates for LLMs: f-strings vs `string.Template` vs Jinja2; escaping braces `{{ }}`.

```python
name = "Ana"
print(f"{'nested "quotes" ok in 3.12+'} {name!r:>10}")
```

### Advanced — what to learn

- Bytecode of an f-string (`dis`): `FORMAT_VALUE` / `BUILD_STRING` (3.12-) and the changes
  in 3.13/3.14 (`CONVERT_VALUE`, `FORMAT_SIMPLE`, `FORMAT_WITH_SPEC`) — link to Module 1.19.
- **Template strings (PEP 750, Python 3.14)**: `t"Hello {name}"` produces a `Template` object
  (strings + interpolations), not a `str`; consumers can escape/transform values safely.
  Use cases: SQL with bound parameters, HTML escaping, shell-safe commands, structured logging.
- Injection prevention: why f-strings must never build SQL/HTML/shell from user data;
  how t-string-based libraries make the safe path the default.
- Logging performance and structured logging: `extra=`, JSON logs, avoiding eager formatting.
- Security: format-string attacks with `str.format` on untrusted templates (attribute traversal `{0.__class__}`).
- Internationalisation: gettext and plural forms; why f-strings and translation don't mix (use `gettext` with named placeholders).
- Testing string output: golden files / snapshot tests (link to Module 1.16 lesson 04).
- Style: ruff rules (`UP031/UP032`, `G004` logging f-string, `S608` SQL injection).

### Common mistakes

- f-strings in `logging` calls (eager formatting) and in SQL.
- Calling `str.format` on user-supplied templates.
- Misplaced `!r` and format specs on non-numeric types.

### Self-check

1. What does `f"{x=}"` print?
2. What changed in f-string parsing in 3.12 and which previously illegal code is now valid?
3. Sketch how a t-string-based `sql()` function would produce a parameterised query safely.

---

## Lesson 09 — `09-the-warnings-module-and-deprecations.md`

**Why it matters.** Libraries change. A deprecation policy lets you remove
or rename APIs without breaking users overnight. Applications and test
suites must also treat warnings as signals, not noise.

### Basic — what to learn

- `warnings.warn(message, category, stacklevel)`; categories: `UserWarning`,
  `DeprecationWarning`, `FutureWarning`, `RuntimeWarning`, `ResourceWarning`, `PendingDeprecationWarning`.
- Default visibility: `DeprecationWarning` shown only when triggered in `__main__` (and by test runners);
  `FutureWarning` for end users.
- Control: `-W` flags, `PYTHONWARNINGS`, `warnings.filterwarnings`, `simplefilter`, `catch_warnings`.

```python
import warnings

def old_func():
    warnings.warn("old_func() is deprecated; use new_func()",
                  DeprecationWarning, stacklevel=2)
    return new_func()
```

### Intermediate — what to learn

- **`stacklevel=2`** so the warning points at the caller's line, not the library internals.
- `@warnings.deprecated("…")` (3.13+) decorator and `typing_extensions.deprecated`: type checkers
  and IDEs flag deprecated usage statically.
- Testing: `pytest.warns(DeprecationWarning, match=...)`; running tests with
  `-W error` (or `filterwarnings = error` in pytest config) to fail on new warnings.
- Deprecating parameters, attributes (module `__getattr__`), classes and behaviour changes.
- Python's own `ResourceWarning` (unclosed files) and `-X dev` mode.
- Capturing warnings into logging (`logging.captureWarnings(True)`).

```python
def __getattr__(name):                # module-level, PEP 562
    if name == "OldName":
        warnings.warn("OldName was renamed to NewName", DeprecationWarning, stacklevel=2)
        return NewName
    raise AttributeError(name)
```

### Advanced — what to learn

- **Deprecation lifecycle policy**: announce (docs + warning) → grace period
  (≥ 2 minor releases or 6–12 months) → remove in a major release (links to semantic versioning in Module 1.6 and API design in Module 1.20).
- Changelog entries, migration guides and automated codemods (`libcst`, `ruff` fixes).
- Filter configuration pitfalls: filters are global state; thread-safety of `catch_warnings`;
  `once`/`default`/`module`/`always` actions and the `__warningregistry__`.
- Library vs application responsibilities: libraries emit; applications decide filters. Never silence all warnings globally.
- Dealing with warnings from dependencies; upgrade dashboards; CI jobs against the next
  Python/dependency pre-release to catch breaks early.
- Warnings as errors in CI for your own package only (`error::DeprecationWarning:yourpkg`).
- `FutureWarning` for behaviour changes (pandas-style) and how to opt in to new behaviour.
- Observability: counting deprecated-API usage in production to decide removal timing.

### Common mistakes

- Missing `stacklevel` so users cannot find their offending call.
- Using `DeprecationWarning` for end-user-visible changes (invisible by default).
- Removing APIs without a warning period.

### Self-check

1. Why might a `DeprecationWarning` be invisible to users and what category fixes that for end-user code?
2. Write a deprecated function wrapper and a test asserting the warning's category, message and location.
3. Draft a three-release deprecation timeline for renaming a parameter.

---

## Lesson 10 — `10-python-version-differences-3-10-to-3-14.md`

**Why it matters.** You will maintain code on different versions and decide
when to upgrade. Knowing what each release brought — and what it removed —
lets you modernise safely, choose minimum supported versions, and
exploit performance and tooling improvements.

### Basic — what to learn

- Python's yearly release cycle (October), five-year support window
  (security fixes), `python.org` status page; why running end-of-life Python is a risk.
- Reading "What's New" documents efficiently.
- Declaring support: `requires-python = ">=3.12"` in `pyproject.toml`; classifiers.

**Feature timeline (know at least this):**

| Version | Highlights to know |
| --- | --- |
| 3.10 | `match`/`case`; `X \| Y` in annotations; parenthesised context managers; better error messages; `zip(strict=True)` |
| 3.11 | Large speed-up (specialising interpreter, zero-cost `try`); `ExceptionGroup`/`except*`; `tomllib`; `Self`; `add_note`; `asyncio.TaskGroup`/`timeout`; fine-grained error locations |
| 3.12 | PEP 695 generics/`type` statement; PEP 701 f-strings; `@override`; per-interpreter GIL (C-API); `itertools.batched`; improved `sys.monitoring`; `distutils` removed |
| 3.13 | Experimental free-threaded build and JIT; improved REPL; `copy.replace`; `warnings.deprecated`; `TypeIs`, `ReadOnly`; defined `locals()` semantics (PEP 667); dead batteries (PEP 594) removed |
| 3.14 | Template strings (PEP 750); deferred annotation evaluation (PEP 649/749); officially supported free-threaded build; multiple interpreters in stdlib (`concurrent.interpreters`); `compression.zstd`; safe external debugger attach (PEP 768); `uuid7`; tail-call interpreter option |

(Verify details against the official "What's New" pages when you study; treat this table as an index.)

### Intermediate — what to learn

- Backward-compatibility strategy: `typing_extensions`, `exceptiongroup`, `tomli`,
  `from __future__ import annotations`, feature checks with `sys.version_info`.
- Using `uv python install` and `tox`/`nox` (Module 1.16 lesson 08) to test across versions.
- Modernising code with `ruff --select UP` (pyupgrade) automatically; reviewing diffs.
- Performance upgrades: measure the real speed-up of your workload when moving 3.10 → 3.12/3.14.
- Removed/changed behaviour to watch: `datetime.utcnow()` deprecation, `asyncio` API changes,
  removal of `distutils`, `imp`, `asynchat`; changes to `tarfile` extraction filters; `locals()` semantics;
  default multiprocessing start method change on Linux (3.14: `forkserver`).
- Reading deprecation warnings in CI and tracking them (lesson 09).

```python
import sys
if sys.version_info >= (3, 11):
    import tomllib
else:                                  # pragma: no cover
    import tomli as tomllib
```

### Advanced — what to learn

- **Upgrade playbook**: inventory (Python, deps, C-extensions, wheels availability) → add new version to CI →
  fix warnings → upgrade dependencies → run full tests under `-W error` → canary deploy → bump `requires-python`.
- Free-threaded and JIT builds: what they change, what libraries support them, benchmarking
  and thread-safety audits (preview of Module 1.19 lessons 06–07).
- C-extension/wheel ecosystem lag: checking `abi3`, `cp313t` wheels; building from source cost.
- Policy: "support the last N versions" (SPEC 0 for scientific Python: 3 years for Python, 2 years for core packages).
- Docker base image strategy and pinning (`python:3.12-slim` vs digest pins) — links to Stage 2 containers.
- Security: only supported versions get security patches; track CVEs and supply-chain (Module 1.10 lesson 07).
- Writing an internal "Python upgrade RFC" with risks, rollout, rollback.
- Experiment: run the same benchmark on 3.10, 3.12 and 3.14 and write up results.

### Common mistakes

- Pinning to EOL Python "because it works".
- Using new syntax in a package that declares older support.
- Upgrading the interpreter and dependencies simultaneously with no baseline tests.

### Self-check

1. Which features from this module require 3.12 or newer?
2. How would you test a library on 3.10–3.14 in CI and keep a compatibility shim minimal?
3. Draft a one-page upgrade plan from 3.10 to 3.13 for a service with C-extension dependencies.

---

## 4. Practice questions (`practice-questions.md`)

About **35 questions**:

| Phase | Question types |
| --- | --- |
| A | Convert `if/elif` to `match`; fix capture-vs-constant bug; walrus refactors; signature redesign |
| B | Exception chain tracing; bulk validator with groups; type a generic repository |
| C | Dataclass option puzzles; choose dataclass/attrs/Pydantic; f-string/format-spec table formatting |
| D | Deprecation workflow; compatibility shims; version-timeline matching |

Add 6 **"predict the output"** questions on `match` captures, comprehension scope with `:=`, chained tracebacks and `ExceptionGroup` splitting.

---

## 5. Module mini-project

**Build `modernize-lab`**, a tested package that demonstrates and enforces modern style:

1. A command parser using `match` over tokenised commands with exhaustive handling.
2. A typed generic `Result[T, E]` / `Repository[T]` using PEP 695 syntax, `Self`, `@override`.
3. A bulk-ingestion function that validates rows and raises an `ExceptionGroup`; a CLI that prints grouped errors with row notes.
4. A frozen, slotted, keyword-only dataclass model hierarchy with `__post_init__` validation and JSON round-trip.
5. A public function with a careful positional-only/keyword-only signature and a deprecated alias using `warnings.deprecated` (with fallback).
6. A `tox`/`nox` matrix across 3.12–3.14 and a `ruff --select UP,B,SIM,FBT` configuration.
7. `UPGRADE.md`: findings from running the code on multiple Python versions (timings, warnings).

Acceptance: type checker strict, ≥ 90 % coverage, all warnings treated as errors in CI for the package, README documenting minimum Python and the feature rationale.

---

## 6. Completion checklist

- [ ] I can write and review `match` statements, including class and mapping patterns, and avoid capture traps.
- [ ] I use `:=` only where it improves clarity.
- [ ] I design signatures with positional-only/keyword-only parameters and evolve them safely.
- [ ] I chain exceptions properly, add notes, and design hierarchies.
- [ ] I handle `ExceptionGroup` with `except*`.
- [ ] I use PEP 695 generics, `TypedDict`, `Self`, `override`, and know runtime vs static typing.
- [ ] I choose the right data-model tool and use dataclass options correctly.
- [ ] I explain f-string parsing, injection risks and t-strings.
- [ ] I run a deprecation cycle with correct `stacklevel` and tests.
- [ ] I can summarise 3.10–3.14 changes and plan a version upgrade.
- [ ] I completed the `modernize-lab` mini-project.

**Next:** Module 1.16 — Advanced Testing and Test Architecture.
