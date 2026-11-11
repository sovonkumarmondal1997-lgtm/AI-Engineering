# Positional-Only, Keyword-Only, and Star-Argument Design

> **Stage 1 — Programming & Computational Thinking · Module 15 — Modern Python Language Features · Lesson 03**
>
> **Repository target:** Python 3.12+. Positional-only parameter syntax (`/`) was introduced in Python 3.8. `typing.ParamSpec` and `typing.Concatenate` arrived in 3.10; `typing.Unpack` and PEP 692 support for typed `**kwargs` are available in Python 3.11+. The examples below use the Python 3.12+ repository baseline unless a compatibility note says otherwise.

## Learning objectives

By the end of this lesson, you should be able to:

- Read and design signatures with positional-only, positional-or-keyword, keyword-only, `*args`, and `**kwargs` parameters.
- Predict argument binding and diagnose common `TypeError`s.
- Use `/`, `*`, and argument unpacking to make APIs safer and easier to evolve.
- Avoid mutable-default bugs and distinguish a missing argument from an explicit `None`.
- Write wrappers that preserve useful metadata and, when possible, callable typing.
- Apply `TypedDict` + `Unpack`, overloads, `functools.partial`, and `inspect.signature` appropriately.
- Make evidence-based decisions about API compatibility, deprecation, parameter objects, and lint rules.

## Prerequisites

You should understand functions, local variables, dictionaries, type annotations, exceptions, and basic classes/dataclasses. Familiarity with decorators and static type checking (`mypy` or `pyright`) helps with the advanced sections.

## 1. Mental model: a signature is a caller-facing contract

A **parameter** is a name in a function definition. An **argument** is a value supplied by a caller. Python binds supplied arguments to parameters before the function body runs. A signature determines which calls are accepted and how values are assigned.

```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(greet("Ada"))
print(greet("Ada", "Welcome"))
print(greet(name="Ada", greeting="Welcome"))
```

Expected output:

```text
Hello, Ada!
Welcome, Ada!
Welcome, Ada!
```

`name` and `greeting` are parameters; `"Ada"` and `"Welcome"` are arguments. `greeting="Hello"` gives the parameter a default. The first call omits that argument, so Python uses the default.

## 2. The parameter kinds

Python has five useful parameter categories. The `/` and `*` markers define how callers may provide values; they are not parameters themselves.

| Kind | How declared | How caller may pass it | Typical reason |
|---|---|---|---|
| Positional-only | Before `/` | Position only | Argument name is an implementation detail; avoid keyword-name commitments |
| Positional-or-keyword | Before `*` and not before `/` | Position or keyword | Natural for stable, meaningful names |
| Variadic positional | `*args` | Extra positional arguments | A variable number of positional values |
| Keyword-only | After bare `*` or after `*args` | Keyword only | Flags, units, options, and less-common behavior |
| Variadic keyword | `**kwargs` | Extra keyword arguments | Explicit forwarding or a deliberately extensible keyword interface |

### 2.1 Positional and keyword calls

```python
def subtract(minuend, subtrahend):
    return minuend - subtrahend

print(subtract(10, 3))
print(subtract(minuend=10, subtrahend=3))
print(subtract(10, subtrahend=3))
```

All three calls return `7`. The two parameters are positional-or-keyword: each can be filled by position or by its name, but a parameter cannot be supplied twice.

```python
# subtract(10, minuend=4)  # TypeError: multiple values for argument 'minuend'
```

The exact wording of interpreter error messages can vary between Python versions; the exception category and cause are the important facts.

### 2.2 Positional-only parameters: `/` (Python 3.8+)

```python
def normalize_key(value, /, *, casefold=True):
    text = str(value).strip()
    return text.casefold() if casefold else text

print(normalize_key("  UserID "))
print(normalize_key("  UserID ", casefold=False))
```

Expected output:

```text
userid
UserID
```

`value` must be passed positionally. `casefold` must be passed by keyword if supplied. A positional-only name is not part of the public keyword-call contract, so the implementation can later rename `value` without breaking callers that use the supported positional form.

```python
# normalize_key(value="Ada")  # TypeError: value is positional-only
```

This is a design tool, not a rule that every function should use `/`. Use it when the parameter name is not intended to be a stable public keyword, such as many built-in operations and operator-like methods.

### 2.3 Keyword-only parameters: `*`

```python
def transfer(source, destination, /, *, amount, dry_run=False):
    """Describe a transfer without performing external I/O."""
    return {
        "source": source,
        "destination": destination,
        "amount": amount,
        "dry_run": dry_run,
    }

print(transfer("acct-A", "acct-B", amount=125, dry_run=True))
```

Expected output:

```text
{'source': 'acct-A', 'destination': 'acct-B', 'amount': 125, 'dry_run': True}
```

The account identifiers are positional-only; `amount` and `dry_run` are keyword-only. The call documents the unit of intent and prevents a caller from accidentally treating `125` or `True` as another positional argument.

```python
# transfer("acct-A", "acct-B", 125)  # TypeError: amount is keyword-only
```

Keyword-only parameters are especially useful for booleans, units (`timeout_seconds=...`), optional behavior, and options that may grow over time.

### 2.4 `*args` and `**kwargs`

`*args` collects extra positional arguments into a **tuple**. `**kwargs` collects extra keyword arguments into a **dict**.

```python
def inspect_call(first, *args, mode="safe", **kwargs):
    return first, args, mode, kwargs

print(inspect_call("job", 10, 20, mode="fast", trace=True))
```

Expected output:

```text
('job', (10, 20), 'fast', {'trace': True})
```

Here `first` is positional-or-keyword; `args` receives `10, 20`; `mode` is keyword-only because it follows `*args`; and `kwargs` receives remaining keyword arguments.

Prefer `*args` for a genuinely variable sequence of same-role positional values, such as `max(1, 5, 3)`. Prefer `**kwargs` when deliberately forwarding options or defining an explicitly extensible keyword interface. Do not use them merely to avoid designing a signature: overly broad `**kwargs` can hide misspellings and delay errors.

### 2.5 Legal parameter order

The common full ordering is positional-only, positional-or-keyword, `*args` (or bare `*`), keyword-only, then `**kwargs`.

```python
def example(pos_only, /, pos_or_kw, *args, keyword_only, optional=False, **kwargs):
    return pos_only, pos_or_kw, args, keyword_only, optional, kwargs

print(example("P", "Q", 1, 2, keyword_only="K", extra=9))
```

Expected output:

```text
('P', 'Q', (1, 2), 'K', False, {'extra': 9})
```

Parameter-binding table for this call:

| Signature component | Bound value | Why |
|---|---|---|
| `pos_only` | `"P"` | First positional argument before `/` |
| `pos_or_kw` | `"Q"` | Second positional argument; may alternatively be keyword |
| `args` | `(1, 2)` | Remaining positional arguments |
| `keyword_only` | `"K"` | Explicit keyword after `*args` |
| `optional` | `False` | Default used because omitted |
| `kwargs` | `{"extra": 9}` | Remaining unconsumed keyword |

These forms are invalid syntax:

```python
# def bad(a=1, b): ...        # non-default parameter follows default parameter
# def bad(**kwargs, extra): ... # **kwargs must be last
# def bad(*args, /): ...       # / cannot follow *args
```

Keep these syntax examples commented out if you paste them into a file. Python rejects them at definition/parse time, before any call can run.

## 3. Call-site unpacking: `f(*xs, **kw)`

Unpacking expands an iterable into positional arguments and a mapping into keyword arguments. The resulting call still has to obey the target function's signature.

```python
def connect(host, port, *, tls=True):
    return f"{host}:{port}, tls={tls}"

positional = ("db.internal", 5432)
options = {"tls": False}
print(connect(*positional, **options))
```

Expected output:

```text
db.internal:5432, tls=False
```

Common failures include too many positional values, missing required arguments, duplicate values, and unexpected keywords:

```python
# connect("db.internal", 5432, tls=True, debug=True)
# TypeError: unexpected keyword argument 'debug'

# connect("db.internal", 5432, True)
# TypeError: tls is keyword-only
```

If a wrapper intentionally accepts `**kwargs`, validate or forward them explicitly. A typo such as `timeuot=3` should normally fail clearly rather than be silently ignored.

A strict API naturally rejects an unknown keyword:

```python
def connect_strict(host, /, *, timeout_seconds=5):
    return host, timeout_seconds

try:
    connect_strict("db.internal", timeuot=3)
except TypeError as exc:
    print(type(exc).__name__)
```

Expected output:

```text
TypeError
```

Do not write `def connect_strict(..., **kwargs): pass` unless the function deliberately accepts or forwards that open-ended keyword namespace; otherwise misspellings may be silently accepted.

## 4. Why parameter kinds improve API design

### 4.1 Keyword-only flags, units, and optional behavior

Compare:

```python
# Hard to review: what do True, False, and 3 mean?
# export(data, True, False, 3)

# Self-documenting call:
# export(data, include_header=True, compress=False, retries=3)
```

Keyword names make code review, incident debugging, and future edits safer. Keyword-only parameters also let you add a new optional option without shifting existing positional slots.

### 4.2 Positional-only protects names from becoming API commitments

If callers can write `f(value=...)`, the name `value` is part of the public API. Renaming it may break those callers. If callers can only pass that value positionally, the implementation can rename it without breaking supported call forms.

Positional-only can also resolve a useful name collision when a function accepts `**kwargs`:

```python
def route(name, /, **metadata):
    return name, metadata

print(route("primary", name="audit", priority=2))
```

Expected output:

```text
('primary', {'name': 'audit', 'priority': 2})
```

The first `name` is the positional-only parameter. The keyword `name="audit"` is captured by `metadata`; it does not try to fill the positional-only parameter. This is legal and can be useful in APIs that forward arbitrary mapping keys, but should be explained because it may surprise readers.

## 5. Defaults: evaluated once, not per call

Default expressions are evaluated when the `def` statement executes. A mutable default is therefore shared between calls.

```python
def append_bad(item, items=[]):
    items.append(item)
    return items

print(append_bad("a"))
print(append_bad("b"))
```

Output (showing the bug):

```text
['a']
['a', 'b']
```

Use `None` when `None` itself means “no collection supplied” and is not a valid meaningful input:

```python
def append_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items

print(append_item("a"))
print(append_item("b"))
```

Expected output:

```text
['a']
['b']
```

If `None` is a meaningful value, use a dedicated sentinel object. Identity (`is`) is used to test the sentinel.

```python
_MISSING = object()

def lookup(mapping, key, default=_MISSING):
    """Return mapping[key], or default if supplied; otherwise raise KeyError."""
    try:
        return mapping[key]
    except KeyError:
        if default is _MISSING:
            raise
        return default

values = {"configured": None}
print(lookup(values, "configured"))
print(lookup(values, "absent", None))
try:
    lookup(values, "absent")
except KeyError as exc:
    print(type(exc).__name__)
```

Expected output:

```text
None
None
KeyError
```

The first `None` is the stored value. The second is an explicitly supplied default. The sentinel distinguishes both from omitting `default` entirely.

### 5.1 Validate at the boundary

Annotations do not enforce values at runtime. Validate domain constraints and produce useful errors close to the API boundary.

```python
def retry_request(url, /, *, retries=3, timeout_seconds=5.0):
    if not isinstance(retries, int) or isinstance(retries, bool) or retries < 0:
        raise ValueError("retries must be a non-negative integer")
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    return {"url": url, "retries": retries, "timeout_seconds": timeout_seconds}

print(retry_request("https://example.test", retries=2))
```

Expected output:

```text
{'url': 'https://example.test', 'retries': 2, 'timeout_seconds': 5.0}
```

`bool` is a subclass of `int`, so the explicit boolean rejection is needed if `True` should not count as one retry. In production, also consider the accepted URL scheme, timeout type/range, and any security policy relevant to the service.

## 6. Wrappers, metadata, and introspection

### 6.1 A simple forwarding wrapper

```python
from functools import wraps


def log_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_calls
def total(values, /, *, include_zero=True):
    return sum(value for value in values if include_zero or value != 0)

print(total([2, 0, 3], include_zero=False))
```

Expected output:

```text
calling total
5
```

`wrapper` accepts a broad runtime signature (`*args, **kwargs`) and forwards the actual binding to `total`. `functools.wraps` copies useful metadata and sets `__wrapped__`, which enables introspection tools to discover the wrapped callable.

**Important distinction:** `wraps` does not rewrite the wrapper's code or magically enforce the wrapped function's signature. The wrapper's actual Python code still accepts `*args, **kwargs`; `inspect.signature()` follows `__wrapped__` by default and commonly displays the original signature. Tools can request `follow_wrapped=False` to inspect the wrapper's own signature. Custom descriptors, dynamic wrappers, or `__signature__` can change what introspection reports. Do not claim that runtime binding, static typing, and introspected signatures are always identical.

```python
import inspect

print(inspect.signature(total))
print(inspect.signature(total, follow_wrapped=False))
```

Typical output:

```text
(values, /, *, include_zero=True)
(*args, **kwargs)
```

Exact annotation rendering and signature display can vary with annotations and Python version; the parameter-kind distinction is what matters.

### 6.2 Typing wrappers with `ParamSpec`

At runtime, `ParamSpec` is a typing construct; it does not validate calls. It allows static type checkers to model the parameter list of a wrapped callable.

```python
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def trace(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"trace: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@trace
def scale(value: float, factor: float = 2.0) -> float:
    return value * factor

print(scale(3, factor=4))
```

Expected output:

```text
trace: scale
12
```

This is intended for Python 3.10+ typing. Static type checkers can preserve the callable's parameter types through the decorator. Runtime `ParamSpec` annotations do not make the wrapper's implementation signature identical to `scale`.

## 7. Typing `**kwargs` precisely with `TypedDict` + `Unpack`

A plain `**kwargs: object` says little about accepted names and value types. `TypedDict` plus `Unpack` can describe the supported keyword set to static type checkers. PEP 692 support is available in Python 3.11+.

```python
from typing import NotRequired, TypedDict, Unpack

class ExportOptions(TypedDict):
    include_header: bool
    compress: bool
    retries: NotRequired[int]


def export_data(data: list[dict[str, object]], /, **options: Unpack[ExportOptions]) -> dict[str, object]:
    # TypedDict describes the expected call shape to static checkers; it does
    # not validate a runtime caller, so validate keys and values here.
    allowed = {"include_header", "compress", "retries"}
    unexpected = options.keys() - allowed
    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise TypeError(f"unexpected export option(s): {names}")
    for required in ("include_header", "compress"):
        if required not in options:
            raise TypeError(f"missing required keyword-only option: {required}")
    include_header = options["include_header"]
    compress = options["compress"]
    retries = options.get("retries", 0)
    if not isinstance(include_header, bool):
        raise TypeError("include_header must be bool")
    if not isinstance(compress, bool):
        raise TypeError("compress must be bool")
    if not isinstance(retries, int) or isinstance(retries, bool) or retries < 0:
        raise ValueError("retries must be a non-negative integer")
    return {
        "rows": len(data),
        "include_header": include_header,
        "compress": compress,
        "retries": retries,
    }

print(export_data([{"id": 1}], include_header=True, compress=False, retries=3))
```

Expected output:

```text
{'rows': 1, 'include_header': True, 'compress': False, 'retries': 3}
```

Static type checkers can flag missing required keys, unknown keys, or wrong value types. At runtime, `TypedDict` is not a validator: the function still needs runtime checks if callers or data sources are untrusted. `NotRequired[int]` means the key may be omitted; it does not mean the key's value can be `None`.

For example, the implementation above raises `TypeError` for missing required options, unexpected options, or non-boolean flags, and `ValueError` for a negative, non-integer, or boolean `retries` value. The distinction is deliberate: annotations describe the static contract; explicit checks enforce the runtime contract.

## 8. Overloads when argument choices affect return types

Use `@overload` to describe relationships between accepted arguments and return types to static type checkers. Overload declarations do not dispatch at runtime; the following ordinary implementation does. Here, the input type predicts the output type.

```python
from typing import overload

@overload
def convert_text(value: bytes) -> str: ...

@overload
def convert_text(value: str) -> bytes: ...


def convert_text(value: bytes | str) -> str | bytes:
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return value.encode("utf-8")

print(convert_text(b"hello"))
print(convert_text("hello"))
```

Expected output:

```text
hello
b'hello'
```

A static type checker can infer `str` for the bytes input and `bytes` for the string input. The overload declarations themselves are not runtime dispatch; the implementation performs the conversion and can still raise `UnicodeDecodeError` for invalid UTF-8 input. Runtime validation and error behavior must be designed independently of overloads.

## 9. API evolution and compatibility

A function signature is part of the public contract. Before changing one, search for call sites, including keyword calls, wrappers, `partial` objects, tests, and external users if the API is published.

| Change | Compatibility risk | Guidance |
|---|---|---|
| Add optional keyword-only parameter with a default | Usually low for ordinary calls | Check wrappers that reject/forward keywords and introspection-sensitive users |
| Add required parameter | Breaking for callers that omit it | Consider a default or a staged deprecation/migration |
| Rename positional-or-keyword parameter | Breaking for callers using old keyword | Preserve alias during deprecation if feasible |
| Rename positional-only parameter | Usually compatible for callers using supported positional calls | Recheck introspection, docs, reflection-based frameworks, and internal uses; Python callers cannot bind it by keyword through the ordinary signature |
| Reorder positional-or-keyword parameters | Breaking for positional callers | Avoid reordering public positional slots |
| Make an optional parameter required or tighten accepted values | Potentially breaking | Deprecate gradually and document constraints |
| Change a parameter from positional-or-keyword to keyword-only | Breaking for positional callers | Treat as a breaking change unless versioned migration says otherwise |
| Add `**kwargs` and silently ignore unknown names | Dangerous | Validate, consume intentionally, or forward to a known target |

“Adding an optional keyword-only parameter is safe” is a useful default heuristic, not a universal guarantee. It may break a wrapper that forwards to a function with a strict signature, code that introspects signatures, generated bindings, or custom call adapters.

### 9.1 Deprecating an old parameter

Use `warnings.warn` with `DeprecationWarning` and a useful `stacklevel`. In ordinary Python execution, `DeprecationWarning` is often filtered by default for application code, so tests should explicitly enable it.

```python
import warnings


def render(text, *, legacy_mode=None, mode="standard"):
    if legacy_mode is not None:
        warnings.warn(
            "legacy_mode is deprecated; use mode instead",
            DeprecationWarning,
            stacklevel=2,
        )
        mode = "legacy" if legacy_mode else mode
    return f"[{mode}] {text}"

with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always", DeprecationWarning)
    print(render("hello", legacy_mode=True))
    print(caught[0].category.__name__)
    print(str(caught[0].message))
```

Expected output:

```text
[legacy] hello
DeprecationWarning
legacy_mode is deprecated; use mode instead
```

This example is illustrative: when a legacy parameter and a new parameter can both be supplied, define and test precedence explicitly. A mature migration plan states the deprecation version, replacement, removal timeline, and warning policy. See the module's warnings/deprecations lesson for broader warning filters and policy.

## 10. `functools.partial` and binding semantics

`partial` pre-fills some arguments and returns a callable. Positional arguments are bound positionally; keyword arguments are merged with later call keywords taking precedence for the same key.

```python
from functools import partial

def send_message(recipient, message, /, *, urgent=False, channel="email"):
    return recipient, message, urgent, channel

urgent_email = partial(send_message, urgent=True)
print(urgent_email("ops", "disk alert"))
print(urgent_email("ops", "disk alert", channel="chat", urgent=False))
```

Expected output:

```text
('ops', 'disk alert', True, 'email')
('ops', 'disk alert', False, 'chat')
```

The call-time keyword overrides the keyword pre-filled by `partial`. Because `recipient` and `message` are positional-only, callers cannot accidentally supply them again by keyword. When using `partial`, reason through the resulting binding and test its public call forms; don't assume it freezes every argument permanently.

## 11. Redesign case study: `export(data, True, False, 3)`

Suppose the original function is called like this:

```python
# The old call shape is shown only for discussion; `export` is defined below.
# export(data, True, False, 3)
```

The booleans are opaque at the call site. Is `True` “include header”, “overwrite”, or “validate”? What does `3` count? The signature should express the domain and make risky options explicit.

### Step 1 — name the concepts and units

```python
def export(
    data,
    /,
    *,
    include_header=True,
    compress=False,
    retries=3,
):
    """Return export settings and row count; this demo performs no I/O."""
    if not isinstance(retries, int) or isinstance(retries, bool) or retries < 0:
        raise ValueError("retries must be a non-negative integer")
    return {
        "rows": len(data),
        "include_header": include_header,
        "compress": compress,
        "retries": retries,
    }

records = [{"id": 1}, {"id": 2}]
print(export(records, include_header=True, compress=False, retries=3))
```

Expected output:

```text
{'rows': 2, 'include_header': True, 'compress': False, 'retries': 3}
```

### Step 2 — justify the parameter kinds

- `data` is positional-only because the payload is the primary object and the API does not need to promise the public keyword name `data`.
- `include_header` and `compress` are keyword-only because booleans are easy to misread when positional.
- `retries` is keyword-only because it is an option and should not be confused with another numeric setting.
- Defaults make the common call concise while allowing the call site to document important choices.
- Validation rejects negative retries and booleans masquerading as integers. A production exporter would additionally define compression format, idempotency, failure behavior, and whether retries are actually safe.

### Step 3 — consider whether this should be a parameter object

With only three options, explicit keyword-only parameters are reasonable. If export settings grow into a coherent group, use a dataclass or other configuration object:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ExportOptions:
    include_header: bool = True
    compress: bool = False
    retries: int = 3


def export_with_options(data, /, *, options: ExportOptions = ExportOptions()):
    if options.retries < 0:
        raise ValueError("retries must be non-negative")
    return {"rows": len(data), "options": options}

print(export_with_options([1, 2], options=ExportOptions(compress=True)))
```

Expected output:

```text
{'rows': 2, 'options': ExportOptions(include_header=True, compress=True, retries=3)}
```

The default `ExportOptions()` is safe here because the dataclass is frozen and its fields are immutable values. Frozen dataclasses are shallowly immutable; if fields contain mutable objects, that alone does not make those nested objects immutable.

## 12. Too many parameters, boolean traps, and linting

A useful heuristic from the module roadmap is to pause when a function has more than about four or five parameters. This is not a language rule: some low-level APIs legitimately need more. Ask whether the parameters represent one cohesive configuration, whether a parameter object improves invariants, and whether separate functions would express distinct operations better.

Boolean-trap example:

```python
# Difficult to understand at the call site:
# write_report(report, True, False)

# Clearer:
# Illustrative call shape; `write_report` is a separate application function.
# write_report(report, include_metadata=True, overwrite=False)
```

If the flags select fundamentally different workflows, separate functions may be clearer than two booleans:

```python
# Illustrative alternatives; implement these operations in the application.
# write_report(report, overwrite=False)
# write_report_with_metadata(report, overwrite=False)
```

Do not split functions mechanically; avoid duplication and choose names that represent meaningful operations.

Relevant lint checks include:

- **Ruff `FBT` rules** (flake8-boolean-trap family) for boolean positional arguments/defaults in selected contexts.
- **Pylint `too-many-positional-arguments` / too-many-arguments** checks, depending on configured version and rules.
- **Ruff `PLR0913`** when the corresponding Pylint-derived rule set is enabled, for too many arguments.

Exact rule availability and defaults depend on tool version and configuration. Configure the rules in project settings rather than assuming every check is enabled by default. Linting is a review aid, not a substitute for API judgment.

## 13. Common mistakes

1. **Assuming annotations validate input.** They inform tools; runtime validation is separate.
2. **Using positional booleans.** The caller cannot tell what `True` means without reading the signature.
3. **Using mutable defaults.** A list/dict/set default is shared across calls unless deliberately intended.
4. **Using `**kwargs` to hide typos.** Validate known options and forward only to an intended target.
5. **Renaming a positional-or-keyword parameter casually.** Existing callers may use it by keyword.
6. **Assuming `wraps` changes runtime binding.** It preserves metadata and enables introspection; it does not rewrite wrapper code.
7. **Overusing `/`.** Positional-only is useful when names should not be public, but it reduces caller self-documentation if applied indiscriminately.
8. **Treating overloads as runtime dispatch.** The implementation must perform actual branching and validation.
9. **Changing a signature without checking wrappers.** Forwarding code and introspection may be affected even when direct calls still work.
10. **Using `partial` without checking argument precedence.** Call-time keywords can override pre-filled keywords.

## 14. Exercises

Try these before reading the solutions.

### Exercise 1 — classify the parameters

For `def f(a, b, /, c=1, *args, d, e=False, **kwargs): ...`, classify every parameter and say how each may be passed.

### Exercise 2 — diagnose the calls

```python
def schedule(task, /, *, timeout=10, retries=0):
    return task, timeout, retries
```

Which calls are valid, and why?

```python
schedule("sync")
# schedule(task="sync")  # TypeError: task is positional-only
# schedule("sync", 5)     # TypeError: timeout is keyword-only
schedule("sync", timeout=5, retries=2)
```

### Exercise 3 — repair the default

Rewrite this function so calls do not share a list by accident:

```python
def record(event, history=[]):
    history.append(event)
    return history
```

### Exercise 4 — design an API

Redesign `upload(path, True, 5000)` so the boolean and number are self-documenting. State whether the number is milliseconds or seconds and make that unit explicit.

### Exercise 5 — compatibility review

A public function is currently `def query(table, limit=100)`. Is adding `*, timeout_seconds=5.0` generally compatible? Name two cases where it might still cause problems.

### Exercise 6 — wrappers and typing

Explain the difference between (a) `functools.wraps`, (b) `inspect.signature`, and (c) `ParamSpec`. Which one changes runtime argument binding?

### Exercise 7 — parameter object or signature?

A function now has eight options related to retry policy, backoff, and jitter. Propose a design and explain when keeping keyword-only parameters might still be preferable.

## 15. Hints

- Exercise 1: `/` ends the positional-only group; `*args` captures extra positional arguments; after it, named parameters are keyword-only.
- Exercise 2: distinguish position-only `task` from keyword-only options; duplicate keyword spelling is a syntax error in a direct call.
- Exercise 3: create a fresh list when no history is supplied.
- Exercise 4: choose a unit and put it in the parameter name, e.g. `timeout_ms`.
- Exercise 5: adding an optional keyword-only parameter is usually compatible for direct callers, but inspect wrappers and signature-sensitive integrations.
- Exercise 6: metadata, introspection, and static callable typing solve different problems.
- Exercise 7: group cohesive settings into a named immutable configuration object if that improves clarity and validation.

## 16. Worked solutions

### Solution 1

- `a`, `b`: positional-only; must be passed by position.
- `c`: positional-or-keyword with default `1`.
- `args`: tuple of any extra positional arguments.
- `d`: required keyword-only parameter.
- `e`: optional keyword-only parameter with default `False`.
- `kwargs`: dict of remaining keyword arguments.

### Solution 2

- `schedule("sync")`: valid; defaults apply.
- `schedule(task="sync")`: invalid; `task` is positional-only.
- `schedule("sync", 5)`: invalid; `timeout` is keyword-only.
- `schedule("sync", timeout=5, retries=2)`: valid.
- `schedule("sync", timeout=5, timeout=6)`: invalid syntax because the keyword `timeout` is repeated in one call. To demonstrate duplicate binding at runtime, use `schedule("sync", **{"timeout": 5}, **{"timeout": 6})`; this also raises `TypeError` for multiple values for `timeout`.

### Solution 3

```python
def record(event, history=None):
    if history is None:
        history = []
    history.append(event)
    return history
```

Use a custom sentinel instead if `None` must be accepted as an actual history value.

### Solution 4

One reasonable design:

```python
def upload(path, /, *, overwrite=False, timeout_ms=5000):
    return {"path": path, "overwrite": overwrite, "timeout_ms": timeout_ms}

print(upload("report.csv", overwrite=True, timeout_ms=5000))
```

Expected output:

```text
{'path': 'report.csv', 'overwrite': True, 'timeout_ms': 5000}
```

The explicit unit prevents ambiguity. A real implementation should validate `timeout_ms` and define the meaning of overwrite.

### Solution 5

Usually compatible for direct calls such as `query("users")` and `query("users", 50)`, because the existing positional parameters are unchanged and the new option is optional and keyword-only. It can still affect a wrapper that rejects or does not forward keywords, or code that asserts an exact signature / generates bindings from it. Compatibility is contextual, not a guarantee.

### Solution 6

- `functools.wraps` copies metadata and sets `__wrapped__` so tools can identify the wrapped function.
- `inspect.signature` introspects a callable and follows `__wrapped__` by default unless asked not to.
- `ParamSpec` models a callable's parameter types for static type checking.
- None of these automatically changes the wrapper's actual code-level argument binding. A wrapper with `*args, **kwargs` binds broadly at runtime and forwards to the wrapped callable, where errors may then occur.

### Solution 7

For a cohesive group, define a `RetryPolicy` dataclass with fields such as `max_attempts`, `initial_delay_seconds`, `max_delay_seconds`, and `jitter`. Validate combinations in `__post_init__` or a factory. Keep direct keyword-only parameters if the options are few, callers commonly set only one, and a separate object would add more ceremony than value.

## 17. Final integrated exercise: design a stable export API

Implement a small `export_rows` API with the following requirements:

1. `rows` is positional-only.
2. `include_header` and `delimiter` are keyword-only.
3. `delimiter` must be a one-character string.
4. `retries` is optional, keyword-only, and a non-negative integer but not a boolean.
5. A `None` row collection is rejected with a useful `ValueError`.
6. Return a dictionary describing the export configuration; do not perform filesystem I/O.
7. Add tests for a valid call, invalid delimiter, negative retries, boolean retries, and `None` rows.

### Reference implementation

```python
def export_rows(rows, /, *, include_header=True, delimiter=",", retries=0):
    if rows is None:
        raise ValueError("rows must not be None")
    if not isinstance(delimiter, str) or len(delimiter) != 1:
        raise ValueError("delimiter must be a one-character string")
    if not isinstance(retries, int) or isinstance(retries, bool) or retries < 0:
        raise ValueError("retries must be a non-negative integer")
    return {
        "row_count": len(rows),
        "include_header": include_header,
        "delimiter": delimiter,
        "retries": retries,
    }

assert export_rows([{"id": 1}], include_header=False, delimiter="|", retries=2) == {
    "row_count": 1,
    "include_header": False,
    "delimiter": "|",
    "retries": 2,
}

for bad_call in (
    lambda: export_rows([], delimiter="||"),
    lambda: export_rows([], retries=-1),
    lambda: export_rows([], retries=True),
    lambda: export_rows(None),
):
    try:
        bad_call()
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")

print("all integrated exercise checks passed")
```

Expected output:

```text
all integrated exercise checks passed
```

### What to test beyond the happy path

- Missing required arguments and invalid positional/keyword forms raise `TypeError`.
- Validation errors identify the offending option.
- Existing positional call forms remain unchanged when evolving an API.
- Decorators preserve intended metadata and static typing.
- Runtime validation is tested separately from static type-checker diagnostics.

## 18. Version and compatibility summary

| Feature | Introduced | Compatibility note |
|---|---:|---|
| `*args`, `**kwargs`, `*` for keyword-only parameters | Long-established Python 3 syntax | Available well before modern Python; keyword-only parameters introduced in Python 3.0 |
| `/` in Python function definitions for positional-only parameters | Python 3.8 | Syntax fails to parse on Python versions before 3.8 |
| `ParamSpec` in `typing` | Python 3.10 | For older runtimes, `typing_extensions` is commonly used where supported |
| `TypedDict` + `Unpack` for typed `**kwargs` (PEP 692) | Python 3.11 typing support | Use `typing_extensions` for older target runtimes if appropriate; type-checker support also matters |
| Generic built-in syntax such as `list[str]` | Python 3.9 | This lesson's core signature examples do not require the Python 3.12 generic type-parameter syntax |

## 19. Final design checklist

Before publishing a function, ask:

- Are the most important values obvious at the call site?
- Should any parameters be positional-only to avoid making names contractual?
- Should flags, units, and optional behavior be keyword-only?
- Are defaults immutable, or is a sentinel/factory required?
- Are unexpected keywords rejected with a clear error?
- Are wrappers forwarding and typing parameters accurately?
- Are return-type overloads supported by a real runtime implementation?
- Could a cohesive parameter object improve validation and readability?
- Have signature changes been checked for positional callers, keyword callers, wrappers, `partial`, introspection, and external consumers?
- Are deprecations warned about and documented before removal?
- Do lint and type-check configurations match the repository's policy?

The goal is not the most elaborate signature. It is a contract that is explicit, testable, maintainable, and safe to evolve.
