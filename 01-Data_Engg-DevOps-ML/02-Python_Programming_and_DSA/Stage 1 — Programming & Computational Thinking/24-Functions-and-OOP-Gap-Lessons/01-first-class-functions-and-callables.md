# First-Class Functions and Callables

**Stage 1 — Programming & Computational Thinking · Module 1.24 · Lesson 01**  
**Target version:** Python 3.12+  
**Estimated study time:** 2–3 focused sessions, including exercises and tests

## 1. Learning objectives

By the end of this lesson, you should be able to:

- Explain what a function object is and how `def` creates a function and binds a name to it.
- Distinguish a function reference (`f`) from a function call (`f()`), and safely pass callbacks without invoking them prematurely.
- Assign functions to names, store them in collections, pass them as arguments, return them, and reason about identity.
- Write higher-order functions, callbacks, strategy functions, and dispatch tables.
- Inspect function metadata and signatures without treating introspection as a substitute for a stable API.
- Recognise common callable kinds, including functions, methods, built-ins, classes, callable instances, and `functools.partial` objects.
- Explain bound methods and the introductory descriptor mechanism that creates them.
- Use `Callable`, `Protocol`, `ParamSpec`, and `TypeVar` to describe callable interfaces, including keyword-aware and generic callables.
- Implement and test `compose(*fns)` and `pipe(value, *fns)` with unambiguous order.
- Apply function values to data transformations, validation strategies, registries, configuration-driven dispatch, dependency injection, and inversion of control.
- Identify callback-lifetime risks and choose between a function, closure, `partial`, or class based on requirements.

## 2. Prerequisites

Review these Stage 1 lessons if any of the following are unfamiliar:

| Prerequisite | Stage 1 location | Why it matters |
|---|---|---|
| Variables, types, identity, mutability | Module 1.2 — Python Core Language and Data Types | Function names refer to objects; multiple names can refer to one object. |
| Function parameters, return values, defaults | Module 1.3 — Control Flow, Functions, Scope and Errors, lessons 03–04 | A callback must receive arguments compatible with its signature. |
| Scope, lifetime, pure functions and side effects | Module 1.3, lessons 05–06 | Returned functions and callbacks can retain state or cause effects. |
| Collections, comprehensions and sorting | Module 1.4 — Problem Solving, Collections and Algorithmic Habits | Functions can be stored in mappings and passed as sorting keys. |
| Pytest and systematic debugging | Module 1.7 — Testing and Systematic Debugging | Higher-order behaviour should be tested at boundaries. |
| Composition, protocols and dependency boundaries | Module 1.8 — Object-Oriented Design, Data Modelling and Functional Style | Callable interfaces help separate policy from orchestration. |
| Type hints, decorators and `functools` | Module 1.9 — Advanced Production-Oriented Python Foundations | This lesson uses callable typing and `partial`, but does not teach decorators in depth. |

The project tree places this gap lesson in `24-Functions-and-OOP-Gap-Lessons/`. The roadmap recommends taking Lessons 01–07 after Module 1.9. It deliberately leaves full descriptor mechanics to Module 1.11, introspection/metaprogramming depth to Module 1.12, functional helpers to Module 1.13, and deeper CPython call-frame mechanics to Module 1.19.

## 3. Conceptual foundation

### 3.1 What is a function object?

A function is both **behaviour** (code that can be called) and an **object** that can be stored, passed around, inspected, and referenced by names. A normal Python function created by `def` has a runtime type commonly displayed as `<class 'function'>`, an identity, attributes, and a callable interface.

```python
def square(value: int) -> int:
    """Return the square of an integer."""
    return value * value

alias = square

print(type(square))          # <class 'function'>
print(callable(square))      # True
print(square(5))             # 25
print(alias is square)       # True: both names refer to the same object
print(square.__name__)       # square
```

Expected output, in order:

```text
<class 'function'>
True
25
True
square
```

The exact representation of a function printed directly (for example, `<function square at 0x...>`) includes implementation-dependent details such as a memory address. Do not hard-code that representation in tests.

### 3.2 What `def` does

When Python executes a `def` statement, it creates a function object and binds the declared name to that object in the current namespace. The body is not executed at definition time; it runs when the function is called. Default argument expressions are evaluated when the `def` statement executes, not on each call.

```python
def normalize_code(code: str) -> str:
    return code.strip().upper()

# Definition has bound the name; the body has not normalized any value yet.
result = normalize_code("  ab-12  ")
assert result == "AB-12"
```

A function name is not the function itself in a special syntactic sense; it is a name bound to an object. Rebinding a name does not mutate the function object that was previously referenced:

```python
def first() -> str:
    return "first"

saved = first

def first() -> str:
    return "replacement"

assert first() == "replacement"
assert saved() == "first"
assert saved is not first
```

### 3.3 Identity, equality, type, and behaviour

- **Identity** answers whether two references point to the same object: use `is` when identity is the question.
- **Equality** (`==`) asks whether objects are considered equal. Function objects normally compare by identity, but some callable objects may define different equality semantics.
- **Type** tells you the object's runtime class. Many distinct callable kinds are callable without having type `function`.
- **Behaviour** is observed by calling the object with valid arguments; `callable(obj)` only indicates that Python considers it callable, not that every possible call is valid or successful.

Do not compare functions by `__name__` to determine whether they are interchangeable. Two functions may have the same name but different code, globals, defaults, or captured state. Conversely, two references to the same function may be given different names.

### 3.4 `f` versus `f()` — reference versus call

This distinction is central to callbacks:

```python
def send_report() -> str:
    print("report sent")
    return "sent"

callback = send_report       # stores the function object; does not call it
result = send_report()       # calls it immediately and stores its return value

assert callable(callback)
assert result == "sent"
```

The first assignment produces no `report sent` output. The second call prints it once. A common bug is registering the result rather than the function:

```python
# Usually wrong when register expects a callback:
# register(send_report())

# Usually correct: register the function to be called later:
# register(send_report)
```

There are legitimate APIs that expect a precomputed result; always check the parameter contract. The rule is not “never use parentheses”—it is “know whether the API expects a callable or the result of calling it.”

## 4. Beginner-level lessons

### 4.1 Assign functions to variables

```python
def celsius_to_fahrenheit(celsius: float) -> float:
    return celsius * 9 / 5 + 32

convert = celsius_to_fahrenheit
print(convert(0))  # 32.0
```

Aliases are useful when an algorithm accepts a behaviour choice. They do not copy the function.

### 4.2 Store functions in lists and dictionaries

A list can hold a sequence of operations; a dictionary can map stable names to operations.

```python
def strip_text(value: str) -> str:
    return value.strip()

def uppercase_text(value: str) -> str:
    return value.upper()

def redact_text(value: str) -> str:
    return "[REDACTED]"

steps = [strip_text, uppercase_text]
text = "  customer-17  "
for step in steps:
    text = step(text)
assert text == "CUSTOMER-17"

TRANSFORMS = {
    "strip": strip_text,
    "uppercase": uppercase_text,
    "redact": redact_text,
}
assert TRANSFORMS["redact"]("secret") == "[REDACTED]"
```

Use explicit names as registry keys. Avoid relying on display names or arbitrary Python expressions in configuration; configuration should select from an allow-listed set of operations.

### 4.3 Pass a function as an argument

A function that accepts another function is a **higher-order function**. The passed function is often called a callback, strategy, predicate, key function, or transformation depending on its role.

```python
from collections.abc import Callable, Iterable
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")

def apply_to_each(fn: Callable[[T], R], values: Iterable[T]) -> list[R]:
    """Call fn once for each value and collect the results."""
    return [fn(value) for value in values]

def square(value: int) -> int:
    return value * value

assert apply_to_each(square, [1, 2, 3]) == [1, 4, 9]
```

`apply_to_each` controls iteration; `square` controls the transformation. This separation makes each part easier to test and reuse.

### 4.4 `sorted(key=...)` and callback timing

`sorted` calls the key function to derive a comparison key for each input element, then sorts by those keys. The key function receives one element and returns a value that can be ordered with the other key results.

```python
words = ["pear", "fig", "banana", "plum"]
assert sorted(words, key=len) == ["fig", "pear", "plum", "banana"]

records = [
    {"name": "Asha", "quality_score": 0.91},
    {"name": "Ravi", "quality_score": 0.84},
    {"name": "Mina", "quality_score": 0.97},
]
ranked = sorted(records, key=lambda row: row["quality_score"], reverse=True)
assert [row["name"] for row in ranked] == ["Mina", "Asha", "Ravi"]
```

Prefer a named function when the key logic is reused, has business meaning, needs a docstring, or is complex enough to obscure the call. This lesson uses a short lambda only to demonstrate the callable interface; Lesson 02 covers lambda design in depth.

### 4.5 Return a function

A function may return another function object. A function that builds and returns a configured function is commonly called a **function factory**.

```python
from collections.abc import Callable

def make_multiplier(factor: int) -> Callable[[int], int]:
    def multiply(value: int) -> int:
        return value * factor
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)
assert double(10) == 20
assert triple(10) == 30
```

The returned functions retain access to `factor`; that is a closure. Closures, free variables, cells, `nonlocal`, and late binding are the subjects of Lessons 03–04, so here the essential point is that returning a function is ordinary object-returning behaviour.

## 5. Intermediate-level lessons

### 5.1 Higher-order functions and strategies

A **strategy function** represents a policy selected by the caller. For example, the same batch processor can apply different validation policies without inheriting from a new class for every policy.

```python
from collections.abc import Callable, Iterable
from typing import TypeVar

T = TypeVar("T")

def keep_valid(
    rows: Iterable[T],
    validator: Callable[[T], bool],
) -> list[T]:
    """Return rows accepted by validator, preserving input order."""
    return [row for row in rows if validator(row)]

def has_required_fields(row: dict[str, object]) -> bool:
    return bool(row.get("customer_id")) and "amount" in row

def positive_amount(row: dict[str, object]) -> bool:
    amount = row.get("amount")
    # bool is a subclass of int, but True/False are not valid monetary amounts.
    return (
        isinstance(amount, (int, float))
        and not isinstance(amount, bool)
        and amount > 0
    )

rows = [
    {"customer_id": "c-1", "amount": 12.5},
    {"customer_id": "", "amount": 9.0},
    {"customer_id": "c-3", "amount": -1.0},
]
structurally_valid = keep_valid(rows, has_required_fields)
financially_valid = keep_valid(structurally_valid, positive_amount)
assert [row["customer_id"] for row in financially_valid] == ["c-1"]
assert not positive_amount({"customer_id": "c-4", "amount": True})
```

In production, distinguish **schema validity**, **business validity**, and **operational failure**. A validator should have a documented contract: does it return `False`, raise a domain-specific exception, or produce a structured validation result? Do not silently swallow malformed records unless the pipeline's error policy explicitly requires it.

### 5.2 Dispatch tables instead of long `if/elif` chains

A dispatch table maps a controlled command name to a handler. It is especially useful when each branch performs a distinct operation and the mapping is easy to inspect or extend.

```python
from collections.abc import Callable
from typing import TypedDict

class JobContext(TypedDict):
    job_id: str
    status: str

def handle_start(ctx: JobContext) -> JobContext:
    return {**ctx, "status": "running"}

def handle_stop(ctx: JobContext) -> JobContext:
    return {**ctx, "status": "stopped"}

HANDLERS: dict[str, Callable[[JobContext], JobContext]] = {
    "start": handle_start,
    "stop": handle_stop,
}

def dispatch(command: str, ctx: JobContext) -> JobContext:
    try:
        handler = HANDLERS[command]
    except KeyError:
        expected = ", ".join(sorted(HANDLERS))
        raise ValueError(
            f"unknown command {command!r}; expected one of: {expected}"
        ) from None
    return handler(ctx)

assert dispatch("start", {"job_id": "job-7", "status": "queued"}) == {
    "job_id": "job-7", "status": "running"
}
```

Design considerations:

- **Validate at the boundary.** Unknown commands should fail clearly; do not silently select a default handler unless that is an explicit product requirement.
- **Keep registration controlled.** A registry of trusted functions is not a reason to use `eval`, `exec`, dynamic imports, or arbitrary user-supplied names.
- **Watch shared state.** A module-level dictionary is mutable global state. It is reasonable for a fixed, read-only mapping; for tests or plugins, inject the mapping or build it in a factory.
- **Choose the right abstraction.** If handlers need different dependencies or substantial state, a callable object or service class may be clearer than forcing everything into a function.

### 5.3 Function metadata

Ordinary Python functions expose useful metadata. The following example inspects common attributes safely for learning and diagnostics:

```python
from inspect import signature

def parse_amount(text: str, *, allow_negative: bool = False) -> float:
    """Parse an amount from text, optionally permitting negative values."""
    value = float(text)
    if value < 0 and not allow_negative:
        raise ValueError("negative amount is not allowed")
    return value

print(parse_amount.__name__)        # parse_amount
print(parse_amount.__qualname__)    # parse_amount
print(parse_amount.__doc__)         # docstring text
print(parse_amount.__module__)      # __main__ when run as a script
print(parse_amount.__defaults__)    # None: no positional defaults
print(parse_amount.__kwdefaults__)  # {'allow_negative': False}
print(parse_amount.__annotations__) # annotations dictionary
print(signature(parse_amount))     # (text: str, *, allow_negative: bool = False) -> float
print(parse_amount.__code__.co_argcount)  # 1 positional-or-keyword parameter
print(parse_amount.__dict__)        # initially {}
```

Attribute meanings and caveats:

| Attribute | Meaning | Practical caution |
|---|---|---|
| `__name__` | Function's short name | Can be changed; not a stable identifier. |
| `__qualname__` | Qualified name, including nesting context | Describes lexical naming, not a globally unique registry key. |
| `__doc__` | Docstring or `None` | Keep it accurate; tools often display it. |
| `__module__` | Module name associated with the function | May be `__main__`; can be altered in dynamic setups. |
| `__defaults__` | Tuple of positional parameter defaults, or `None` | Mutable objects inside defaults are shared; do not mutate defaults casually. |
| `__kwdefaults__` | Dictionary of keyword-only defaults, or `None` | Inspection detail; avoid modifying it as normal application control flow. |
| `__annotations__` | Annotation mapping | Depending on annotation form/version, evaluation can involve forward references; do not blindly evaluate untrusted annotations. |
| `__code__` | Code object for a Python function | Not available on every callable (e.g. many built-ins); code details are not a stable public API. |
| `__dict__` | Function-specific attribute dictionary | Custom attributes can hide state and make code harder to understand; use sparingly. |

A function's metadata is useful for debugging, documentation, and tooling. Do not build core business behaviour around mutable metadata unless you are deliberately designing a framework that owns that contract. Annotations are not runtime enforcement by themselves.

Custom function attributes are possible:

```python
def enrich(record: dict[str, object]) -> dict[str, object]:
    return {**record, "enriched": True}

enrich.pipeline_stage = "enrichment"  # type: ignore[attr-defined]
assert enrich.pipeline_stage == "enrichment"  # type: ignore[attr-defined]
```

This works at runtime, but static type checkers may reject arbitrary attributes. For durable metadata, prefer a registry entry, dataclass, or explicitly typed wrapper rather than scattering ad hoc attributes across functions.

### 5.4 What counts as callable?

`callable(value)` returns `True` if the object appears callable. It does **not** prove that a particular argument list is valid or that calling it will succeed.

```python
from functools import partial

class BatchCounter:
    def __init__(self, start: int = 0) -> None:
        self.count = start

    def __call__(self, amount: int = 1) -> int:
        self.count += amount
        return self.count

def add(left: int, right: int) -> int:
    return left + right

class Record:
    pass

counter = BatchCounter()
add_five = partial(add, 5)

candidates = [add, lambda x: x, str.upper, Record, counter, add_five, 42]
print([callable(candidate) for candidate in candidates])
# [True, True, True, True, True, True, False]
assert counter(2) == 2
assert add_five(7) == 12
assert isinstance(Record(), Record)
```

Common callable categories:

- **Python functions**, including `def` and `lambda` functions.
- **Bound methods**, such as `"hello".upper`, which carry a receiver.
- **Built-in functions and methods**, such as `len` and `str.upper`.
- **Classes**, which are callable and ordinarily construct an instance (construction may run `__new__` and `__init__`). In special cases, `__new__` can return an object that is not an instance of that class, in which case that class's `__init__` is not called.
- **Callable instances**, whose class defines `__call__`.
- **`functools.partial` objects**, which call another callable with some arguments pre-filled.

The term “unbound method” is mainly historical in Python 3: `SomeClass.method` for a normal instance method is a function object, not a special unbound-method object. `instance.method` is a bound method.

### 5.5 Bound methods: `__self__` and `__func__`

Accessing a normal function through an instance creates a bound method that remembers both the instance and the underlying function:

```python
class Worker:
    def __init__(self, worker_id: str) -> None:
        self.worker_id = worker_id

    def process(self, item: str) -> str:
        return f"{self.worker_id}:{item}"

worker = Worker("worker-3")
bound = worker.process
plain_function = Worker.process

assert bound("row-9") == "worker-3:row-9"
assert bound.__self__ is worker
assert bound.__func__ is Worker.process
assert plain_function(worker, "row-9") == bound("row-9")
```

`worker.process("row-9")` supplies `worker` as the method's `self` automatically. Calling `Worker.process(worker, "row-9")` is the explicit equivalent for this ordinary method.

Repeated access to `worker.process` produces distinct bound-method objects on standard Python implementations, so identity is not a safe way to compare repeated accesses. Do not use object identity as a portable callback-registration contract:

```python
class Worker:
    def process(self, item: str) -> str:
        return item

worker = Worker()
assert worker.process is not worker.process
assert worker.process == worker.process
```

The second assertion is true for normal bound methods because equality compares the underlying function and receiver. If a callback must later be removed from a registry, understand whether the registry uses identity or equality and whether it stores the exact callback object.

### 5.6 Bound-method lifetime pitfalls

A bound method holds a strong reference to its receiver through `__self__`. A long-lived scheduler, event bus, or registry that stores `instance.handle` can therefore keep the instance alive longer than expected.

```python
import gc
import weakref

class Listener:
    def handle(self, event: str) -> None:
        print(event)

listener = Listener()
weak_listener = weakref.ref(listener)
callback = listener.handle

del listener
assert weak_listener() is not None  # callback still owns the receiver

del callback
gc.collect()
assert weak_listener() is None
```

This example makes the object unreachable after the last strong reference is released. The timing of reclamation is implementation-dependent; `gc.collect()` requests collection, and the immediate timing should not be used as a cross-implementation performance guarantee. For weak references to bound methods, `weakref.WeakMethod` exists, but a weak method reference must be resolved before calling and may already be dead. Use it only when weak listener lifetime is part of the design; ordinary strong references are often simpler and correct. Do not introduce weak references merely to hide unclear ownership.

### 5.7 `functools.partial` for argument adaptation

`partial` creates a callable that forwards a call to another callable with some positional and/or keyword arguments pre-filled. It is often clearer than writing a wrapper that only binds arguments.

```python
from functools import partial
from collections.abc import Callable

def parse_field(raw: str, *, field_name: str, allow_blank: bool = False) -> str:
    value = raw.strip()
    if not value and not allow_blank:
        raise ValueError(f"{field_name} must not be blank")
    return value

parse_customer_id: Callable[[str], str] = partial(
    parse_field, field_name="customer_id"
)
assert parse_customer_id("  c-17 ") == "c-17"
```

The callable contract exposed by a `partial` can be more nuanced than a plain `Callable[[str], str]` annotation expresses. Type checkers may infer a more precise signature from the `partial` expression; annotate at the boundary where it improves readability, and verify with the project's checker. Avoid claiming that `Callable` captures every detail of keyword-only parameters—it does not.

## 6. Advanced-level lessons

### 6.1 How a function call works — introductory model

At a conceptual level, a call such as `result = transform(record)` proceeds as follows:

1. Python evaluates the callable expression (`transform`) and the argument expressions (`record`).
2. Python verifies that the object can be called and binds supplied arguments to the callable's accepted parameters. Invalid calls raise errors such as `TypeError`.
3. For a Python function, execution enters a new call frame with local parameter bindings and execution state.
4. The function body runs until it returns, raises an exception, or otherwise transfers control.
5. A normal return value becomes the value of the call expression; an uncaught exception propagates to the caller.

This is an explanatory model, not a full description of CPython's evolving interpreter implementation. For deeper frames, bytecode and evaluation-loop detail, use Module 1.19, especially its call-stack lesson.

### 6.2 Inspect signatures and source

`inspect.signature` is useful for showing the callable's advertised parameters. `inspect.getsource` may retrieve source text when it is available (for example, from an imported Python module or a source-backed interactive environment).

```python
import inspect

def load_partition(path: str, *, retries: int = 3) -> list[str]:
    """Load one partition, retrying a bounded number of times."""
    return [path] * retries

sig = inspect.signature(load_partition)
assert str(sig) == "(path: str, *, retries: int = 3) -> list[str]"

bound = sig.bind("s3://bucket/day=2026-10-18", retries=2)
assert bound.arguments["retries"] == 2

# Works when Python source is available to inspect:
source = inspect.getsource(load_partition)
assert "def load_partition" in source
```

Important limits:

- `inspect.signature` may not be available or exact for every built-in, extension callable, dynamically generated callable, or wrapper. A callable can advertise a signature that does not fully describe runtime behaviour.
- `inspect.getsource` can raise `OSError` or `TypeError` if source is unavailable; source retrieval is environment-dependent and may not work for interactive definitions or frozen/compiled modules.
- Do not call `getsource` on arbitrary objects as part of normal production request handling. It is primarily a development and tooling facility.
- Avoid parsing a signature's string representation. Use `Signature` and `Parameter` objects if tooling genuinely needs structured signature information.

### 6.3 Why methods become bound: descriptor behaviour

Functions stored on a class participate in Python's descriptor protocol. At a high level, when a normal function is accessed through an instance, its descriptor behaviour returns a bound method that pairs the function with that instance. Access through the class returns the function without automatically supplying an instance.

```python
class Formatter:
    def label(self, value: str) -> str:
        return f"[{value}]"

formatter = Formatter()

assert formatter.label("ok") == "[ok]"
assert Formatter.label(formatter, "ok") == "[ok]"
assert formatter.label.__self__ is formatter
assert formatter.label.__func__ is Formatter.label
```

`staticmethod` changes the binding behaviour so the function is accessed without an automatically supplied instance. `classmethod` binds the class as the first argument (conventionally `cls`). Their complete mechanics belong with the advanced object model; this lesson needs only the binding intuition. See Module 1.11 Lesson 06 for descriptors and attribute lookup.

### 6.4 Callable typing: `Callable`

`collections.abc.Callable` is the runtime ABC; `typing.Callable` is also available for annotations. The familiar annotation `Callable[[A, B], R]` means “callable accepting positional arguments of types `A` and `B`, returning `R`.” It does not fully express overloads, arbitrary keyword names, or all parameter kinds.

```python
from collections.abc import Callable

def combine(left: int, right: int) -> int:
    return left + right

def run_binary(
    operation: Callable[[int, int], int],
    left: int,
    right: int,
) -> int:
    return operation(left, right)

assert run_binary(combine, 2, 3) == 5
```

`Callable[..., R]` means the parameter signature is intentionally not specified precisely, while the return type is `R`. It can be useful at loose integration boundaries, but it gives a type checker less information. `Callable[..., object]` is often safer than `Callable[..., Any]` when the result is not used dynamically; `Any` deliberately disables many checks.

### 6.5 `Protocol` with `__call__` for keyword-aware interfaces

Use a callback protocol when the interface has meaningful keyword-only parameters, overloads, or a signature that `Callable[[...], R]` cannot express clearly.

```python
from typing import Protocol

class RowValidator(Protocol):
    def __call__(
        self,
        row: dict[str, object],
        *,
        strict: bool = ...,
    ) -> bool: ...

def required_fields(
    row: dict[str, object],
    *,
    strict: bool = True,
) -> bool:
    required = {"id", "amount"}
    present = required.issubset(row)
    if strict:
        return present and bool(row.get("id"))
    return present

def validate_rows(
    rows: list[dict[str, object]],
    validator: RowValidator,
) -> list[dict[str, object]]:
    return [row for row in rows if validator(row, strict=True)]

assert validate_rows([{"id": "a", "amount": 2}], required_fields) == [
    {"id": "a", "amount": 2}
]
```

A protocol is structural: a function or object matches if its interface satisfies the protocol; it need not inherit from `RowValidator`. The ellipsis in a protocol signature's default is a typing convention, not a runtime default value to copy into an implementation.

### 6.6 `ParamSpec` and `TypeVar` for signature-preserving wrappers

`TypeVar` relates input and output types. `ParamSpec` represents a callable's parameter specification so a higher-order function can accept and return callables while preserving their parameter types. Python 3.12 also supports PEP 695 type-parameter syntax (`def identity[T](...)`); the following uses the familiar `TypeVar` spelling, which remains valid on Python 3.12+ and can be easier to compare with older code.

```python
from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def trace_call(fn: Callable[P, R]) -> Callable[P, R]:
    """Return a transparent wrapper with the same static call signature."""
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"calling {fn.__name__}")
        return fn(*args, **kwargs)
    return wrapped

def format_row(row_id: str, *, uppercase: bool = False) -> str:
    return row_id.upper() if uppercase else row_id

traced_format = trace_call(format_row)
assert traced_format("r-4", uppercase=True) == "R-4"
```

This demonstrates typing, not a full decorator lesson. Static signature preservation does not automatically copy runtime metadata such as `__name__`, annotations, or `__doc__`; standard decorator tooling often uses `functools.wraps`, covered elsewhere. Also, `ParamSpec` does not make a wrapper's runtime signature magically identical: it informs static type checkers.

A generic mapper can use type parameters to express that each input `T` becomes an output `R`:

```python
from collections.abc import Callable, Iterable
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")

def map_to_list(fn: Callable[[T], R], values: Iterable[T]) -> list[R]:
    return [fn(value) for value in values]

assert map_to_list(str, [10, 20]) == ["10", "20"]
```

On Python 3.12+, the signature can instead be written using PEP 695 syntax as `def map_to_list[T, R](fn: Callable[[T], R], values: Iterable[T]) -> list[R]: ...`. Do not mix the two declaration styles for the same type parameter in one function.

### 6.7 Composition and piping

Function composition combines transformations. Here the order is explicit:

- `compose(f, g, h)(x)` applies **right to left**: `f(g(h(x)))`.
- `pipe(x, f, g, h)` applies **left to right**: `h(g(f(x)))`.
- With no functions, both are identity operations under these definitions: `compose()(x) == x` and `pipe(x) == x`.

```python
from collections.abc import Callable
from functools import reduce
from typing import TypeVar

T = TypeVar("T")

def compose(*fns: Callable[..., object]) -> Callable[[object], object]:
    """Compose unary callables right-to-left; an empty composition is identity."""
    def composed(value: object) -> object:
        return reduce(lambda current, fn: fn(current), reversed(fns), value)
    return composed

def pipe(value: T, *fns: Callable[..., object]) -> object:
    """Apply unary callables left-to-right to value.

    Runtime contract: each stage must accept one positional argument.
    The broad callable annotation cannot statically verify that contract.
    """
    return reduce(lambda current, fn: fn(current), fns, value)

# Runtime examples: the public helpers above are deliberately simple and broad.
assert compose(lambda x: x + 1, lambda x: x * 2)(3) == 7
assert pipe(3, lambda x: x * 2, lambda x: x + 1) == 7
assert compose()(3) == 3
assert pipe(3) == 3
```

The broad `Callable[..., object]` input signatures above are intentionally imprecise: the runtime contract is that each supplied callable accepts one positional value, but the type does not prove that contract. Each function can change the value type, so a simple `Callable[[T], T]` would incorrectly require every step to preserve one type. For production code, choose one of these approaches:

1. Use a generic composition library with a carefully designed typing model if static inference across heterogeneous stages is essential.
2. Use a practical runtime helper with a documented broad boundary, then narrow or validate the result at the caller.
3. Define a domain-specific pipeline whose stage types are known, rather than pretending arbitrary heterogeneous composition is trivially expressible with one `TypeVar`.

A more useful pipeline for same-type transformations can be typed precisely:

```python
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")

def pipe_same_type(value: T, *fns: Callable[[T], T]) -> T:
    for fn in fns:
        value = fn(value)
    return value

assert pipe_same_type("  abc ", str.strip, str.upper) == "ABC"
```

For heterogeneous transformations such as `str -> int -> float`, use the broad helper with explicit validation or write the stages as ordinary named code. Never hide a real type boundary behind `Any` merely to make a composition helper look elegant.

### 6.8 Function versus callable class

Choose the simplest abstraction that fits the required state and interface.

| Need | Often a good fit | Trade-off |
|---|---|---|
| Stateless transformation or predicate | Named function | Simple and easy to test; state must be passed explicitly. |
| Small configured behaviour with captured values | Closure or `partial` | Compact; hidden captured state can be harder to inspect. |
| Reusable operation with several methods, explicit lifecycle, or substantial state | Class | More structure and surface area; clearer ownership and observability. |
| A mapping from a small, fixed set of names to handlers | Dictionary of functions | Direct dispatch; validation and registry mutation must be controlled. |
| Third-party extension points with a documented contract | Protocol or plugin interface | Flexible and testable; requires versioning and compatibility discipline. |

Do not introduce a class solely because an operation is important. Conversely, do not force a stateful subsystem with multiple behaviours into a pile of closures if a class makes dependencies and lifecycle clearer.

### 6.9 Callbacks and inversion of control

A callback is behaviour supplied to a component that decides **when** to invoke it. This is a small form of **inversion of control**: the caller provides the policy, while the framework or orchestration code controls execution timing.

```python
from collections.abc import Callable

def run_job(job_id: str, on_success: Callable[[str], None]) -> None:
    # The job runner owns the control flow and calls the callback after success.
    print(f"running {job_id}")
    on_success(job_id)

def record_success(job_id: str) -> None:
    print(f"success recorded: {job_id}")

run_job("daily-import", record_success)
```

Expected output:

```text
running daily-import
success recorded: daily-import
```

Registration and invocation are distinct operations. A registration API stores a callback for later use; an event loop, scheduler, framework, or job runner invokes it at the appropriate time. Be explicit about who owns callback lifetime, what thread/task invokes it, what exceptions are allowed to escape, and whether callbacks can be registered or removed while dispatch is in progress.

Standard-library hooks such as `atexit.register`, signal handlers, and `sys.excepthook` are examples of callback-based APIs, but they have different timing, threading, and exception constraints. Read each API's contract rather than assuming all callbacks behave alike. Observer/strategy/command patterns are explored further in Module 1.20 Lesson 04.

## 7. Annotated runnable code examples

The examples in this section are self-contained and can be copied into separate `.py` files. The main pipeline combines a transformation registry, strategy injection, validation, and deterministic dispatch without importing any third-party runtime library.

### 7.1 A small transformation registry

```python
from collections.abc import Callable, Mapping
from typing import TypeAlias

Record: TypeAlias = dict[str, object]
Transform: TypeAlias = Callable[[Record], Record]


def trim_customer_id(record: Record) -> Record:
    value = record.get("customer_id")
    if not isinstance(value, str):
        raise ValueError("customer_id must be a string")
    return {**record, "customer_id": value.strip()}


def normalize_currency(record: Record) -> Record:
    value = record.get("currency")
    if not isinstance(value, str):
        raise ValueError("currency must be a string")
    return {**record, "currency": value.upper()}


TRANSFORMS: Mapping[str, Transform] = {
    "trim_customer_id": trim_customer_id,
    "normalize_currency": normalize_currency,
}


def run_transforms(record: Record, names: list[str]) -> Record:
    current = dict(record)  # avoid mutating the caller's mapping
    for name in names:
        try:
            transform = TRANSFORMS[name]
        except KeyError:
            allowed = ", ".join(sorted(TRANSFORMS))
            raise ValueError(f"unknown transform {name!r}; allowed: {allowed}") from None
        current = transform(current)
    return current


raw = {"customer_id": "  c-17 ", "currency": "usd", "amount": 10.5}
clean = run_transforms(raw, ["trim_customer_id", "normalize_currency"])
assert clean == {"customer_id": "c-17", "currency": "USD", "amount": 10.5}
assert raw["customer_id"] == "  c-17 "  # input was not mutated
```

**Why this design works:** the registry is an allow-list; each transformation has a narrow contract; `run_transforms` controls ordering and error reporting; the input mapping is copied to make non-mutation explicit. In a larger system, define how transformations handle missing fields, type errors, logging, retries, and partial failure.

### 7.2 Configuration-driven dispatch with dependency injection

Configuration should name an operation, not contain executable Python. Dependencies are passed into the function that needs them instead of being discovered from global state.

```python
from collections.abc import Callable, Mapping
from typing import TypeAlias

Record: TypeAlias = dict[str, object]
Transform: TypeAlias = Callable[[Record], Record]


def execute_configured_step(
    record: Record,
    *,
    step_name: str,
    registry: Mapping[str, Transform],
) -> Record:
    try:
        step = registry[step_name]
    except KeyError:
        names = ", ".join(sorted(registry))
        raise ValueError(f"unknown step {step_name!r}; available: {names}") from None
    return step(record)


def add_source_tag(record: Record) -> Record:
    return {**record, "source": "daily_ingest"}


def add_loaded_flag(record: Record) -> Record:
    return {**record, "loaded": True}


registry: Mapping[str, Transform] = {
    "tag_source": add_source_tag,
    "mark_loaded": add_loaded_flag,
}

result = execute_configured_step(
    {"id": "r-1"}, step_name="tag_source", registry=registry
)
assert result == {"id": "r-1", "source": "daily_ingest"}
```

The registry is injected, so tests can pass a tiny fake mapping. This is dependency injection without a container framework. The caller chooses dependencies; the worker does not create or locate them internally. That separation improves testability and limits hidden global coupling.

Security and reliability note: if a configuration file is untrusted, validate the requested name and the input data. Never evaluate a configuration string as Python code to select a function. A registry does not itself make a transformation safe; each registered operation still needs an appropriate trust boundary.

### 7.3 `partial` as a configured callback

```python
from functools import partial


def reject_if_below(
    value: float,
    *,
    minimum: float,
    field: str,
) -> None:
    if value < minimum:
        raise ValueError(f"{field} must be at least {minimum}")

validate_amount = partial(reject_if_below, minimum=0.0, field="amount")
validate_amount(12.0)  # no exception

try:
    validate_amount(-1.0)
except ValueError as exc:
    assert str(exc) == "amount must be at least 0.0"
else:
    raise AssertionError("negative amount should have failed")
```

This is useful when a framework expects a callback with fewer arguments than the underlying function. Check that the resulting signature matches what the receiving API calls.

## 8. Practical data-engineering applications

### 8.1 Transformation pipelines

A pipeline often has a stable orchestration sequence but configurable transformation rules. Passing functions lets orchestration remain independent of individual business operations:

```python
from collections.abc import Callable, Iterable
from typing import TypeAlias

Row: TypeAlias = dict[str, object]
RowTransform: TypeAlias = Callable[[Row], Row]


def apply_pipeline(rows: Iterable[Row], steps: Iterable[RowTransform]) -> list[Row]:
    # Materialize steps once: callers may pass a one-shot generator.
    step_sequence = tuple(steps)
    output: list[Row] = []
    for row in rows:
        current = dict(row)  # shallow copy; nested mutable values remain shared
        for step in step_sequence:
            current = step(current)
        output.append(current)
    return output
```

This implementation materializes the steps as a tuple and the output as a list, then processes one row at a time. Materializing the steps once matters because `steps` may be a one-shot generator; iterating it directly inside the row loop would apply the stages only to the first row. The row copy is shallow, not a deep copy, so nested mutable values can still be shared. For large datasets, consider streaming an iterator of transformed rows instead, while documenting whether errors stop the stream and whether input records are copied. Do not confuse this small Python example with distributed execution semantics in Spark or Dask.

### 8.2 Validation strategies

Inject a validator when the same orchestration must support different policies (for example, strict ingestion versus a permissive backfill). Give validators a stable contract and test each policy independently. If a boolean result cannot explain a failure adequately, use a structured result type or raise a documented validation exception.

### 8.3 Configuration-driven selection

Keep configuration declarative, for example:

```json
{
  "steps": ["trim_customer_id", "normalize_currency"]
}
```

The application validates each string against a registry of approved functions. The configuration chooses from known capabilities; it does not define new executable code. Version registry keys when changing behaviour would break historical jobs, and log the selected step names without logging secrets or sensitive row values.

### 8.4 Dependency injection and inversion of control

If a function needs a clock, database client, object store, or metrics sink, pass the dependency in explicitly when practical. Tests can inject a fake or stub. The component that receives a callback or dependency then controls the call sequence, which is inversion of control at a small scale.

### 8.5 When to use classes instead

Functions are a strong fit for stateless transformations. Prefer a class or a callable instance when the operation needs managed mutable state, multiple related methods, explicit resource lifecycle, configuration that must be inspected, or an identity that matters to registration. Do not make all functions stateful merely to use object-oriented design, and do not hide complex lifecycle state in closures just to avoid defining a class.

## 9. Common mistakes and debugging

### 9.1 Calling too early

```python
# Bug: invokes the function immediately and registers its return value.
# event_bus.subscribe("ready", on_ready())

# Correct if subscribe expects a zero-argument callback:
# event_bus.subscribe("ready", on_ready)
```

**Debug:** inspect the registration method's annotation/docstring, print `repr(callback)` during local debugging, and assert `callable(callback)` at a boundary when that is part of the contract. `callable()` is not a substitute for checking the expected signature.

### 9.2 Putting results in a dispatch table

```python
# Bug: values are computed now; the table may contain strings/None instead of functions.
# HANDLERS = {"start": handle_start(context)}

# Correct when dispatch should call the handler later:
# HANDLERS = {"start": handle_start}
```

### 9.3 Wrong callback signature

A framework may call `callback(event)`, while the supplied function accepts no parameters. This is usually a `TypeError` at invocation time. Use a compatible function, a small adapter, or `partial` when it correctly adapts arguments. Do not catch and suppress the `TypeError` broadly; it might originate inside the callback itself.

### 9.4 Assuming every callable is a function

`isinstance(value, type(lambda: None))` tests for Python function objects, not callability in general. Use `callable(value)` when the question is whether it can be called, then validate the interface through types, documented contracts, or explicit tests.

### 9.5 Comparing callbacks by identity

Repeated access to `obj.method` may produce distinct bound-method objects. If callback deregistration relies on identity, store the exact registered object or design a stable registration token. Understand the event system's equality and lifetime rules.

### 9.6 Keeping objects alive accidentally

A stored bound method holds its instance alive. Investigate long-lived queues, schedulers, observer lists, and caches when an instance does not get collected. Use `weakref.WeakMethod` only if weak ownership is intended and dead-listener handling is explicit.

### 9.7 Assuming metadata is a contract

Names and annotations are helpful but can be changed or missing. Do not use `__name__` as a security check, assume annotations validate input at runtime, or assume every callable exposes `__code__`.

### 9.8 Confusing composition order

Write the intended order down. For `compose(f, g)`, verify `compose(f, g)(x) == f(g(x))`. For `pipe(x, f, g)`, verify `pipe(x, f, g) == g(f(x))`. A tiny test with non-commutative functions such as multiplication then addition catches many order mistakes.

## 10. Testing and type-checking considerations

### 10.1 Pytest tests for core behaviour

Save the following as `test_first_class_functions.py`. It is self-contained and tests identity, callback invocation, dispatch errors, composition order, identity behaviour for empty composition, and dependency injection.

```python
from collections.abc import Callable, Iterable, Mapping
from functools import reduce
from typing import TypeVar

import pytest

T = TypeVar("T")
R = TypeVar("R")
Row = dict[str, object]
RowTransform = Callable[[Row], Row]


def apply(fn: Callable[[T], T], value: T) -> T:
    return fn(value)


def apply_to_each(fn: Callable[[T], R], values: Iterable[T]) -> list[R]:
    return [fn(value) for value in values]


def apply_pipeline(rows: Iterable[Row], steps: Iterable[RowTransform]) -> list[Row]:
    step_sequence = tuple(steps)
    output: list[Row] = []
    for row in rows:
        current = dict(row)
        for step in step_sequence:
            current = step(current)
        output.append(current)
    return output


def compose(*fns: Callable[..., object]) -> Callable[[object], object]:
    def composed(value: object) -> object:
        return reduce(lambda current, fn: fn(current), reversed(fns), value)
    return composed


def pipe(value: T, *fns: Callable[[T], T]) -> T:
    for fn in fns:
        value = fn(value)
    return value


def dispatch(command: str, handlers: Mapping[str, Callable[[int], int]], value: int) -> int:
    try:
        handler = handlers[command]
    except KeyError:
        raise ValueError(f"unknown command {command!r}") from None
    return handler(value)


def test_function_is_a_value_and_alias_preserves_identity() -> None:
    def increment(value: int) -> int:
        return value + 1

    alias = increment
    assert alias is increment
    assert apply(alias, 3) == 4


def test_callback_is_passed_not_called_during_registration() -> None:
    calls: list[int] = []

    def callback(value: int) -> int:
        calls.append(value)
        return value * 2

    registered = callback
    assert calls == []
    assert registered(4) == 8
    assert calls == [4]


def test_apply_to_each_handles_empty_input_without_invoking_callback() -> None:
    calls: list[int] = []

    def callback(value: int) -> int:
        calls.append(value)
        return value + 1

    assert apply_to_each(callback, []) == []
    assert calls == []


def test_pipeline_reuses_generator_steps_for_every_row() -> None:
    def add_loaded_flag(row: Row) -> Row:
        return {**row, "loaded": True}

    rows: list[Row] = [{"id": "a"}, {"id": "b"}]
    steps = (step for step in [add_loaded_flag])
    assert apply_pipeline(rows, steps) == [
        {"id": "a", "loaded": True},
        {"id": "b", "loaded": True},
    ]


def test_compose_runs_right_to_left() -> None:
    fn = compose(lambda x: x + 1, lambda x: x * 2)
    assert fn(3) == 7  # (3 * 2) + 1


def test_empty_compose_is_identity() -> None:
    assert compose()("unchanged") == "unchanged"


def test_pipe_runs_left_to_right_and_empty_pipe_is_identity() -> None:
    assert pipe(3, lambda x: x * 2, lambda x: x + 1) == 7
    assert pipe("same") == "same"


def test_dispatch_returns_handler_result() -> None:
    handlers = {"double": lambda value: value * 2}
    assert dispatch("double", handlers, 5) == 10


def test_dispatch_unknown_command_has_helpful_error() -> None:
    with pytest.raises(ValueError, match="unknown command 'missing'"):
        dispatch("missing", {}, 5)


def test_callable_predicate_is_not_a_signature_check() -> None:
    fn = lambda value: value
    assert callable(fn)
    with pytest.raises(TypeError):
        fn()  # type: ignore[call-arg]
```

Run it with:

```bash
python -m pytest -q test_first_class_functions.py
```

Expected result: **10 tests pass**. The tests include an empty input (the callback is not invoked) and a one-shot generator of pipeline stages reused across multiple rows. The final test intentionally demonstrates that `callable()` does not verify that a call with zero arguments is valid.

### 10.2 What to test

For higher-order functions, test at least:

- Normal input and output behaviour.
- Empty input or no callbacks, where supported.
- Unknown registry keys and incompatible callbacks.
- Callback invocation count and ordering when order matters.
- Whether input data is mutated or preserved.
- Exceptions: which are propagated, translated, or recorded.
- Boundary cases such as empty composition, an empty pipeline, and duplicate registrations.
- Lifetime behaviour if callbacks are stored beyond the immediate call.

Use simple fake functions in unit tests. They make it easy to observe invocation, force failure, or verify ordering without bringing up a database or cloud service. Integration tests are still needed to verify real adapter contracts.

### 10.3 Type-checking guidance

- Use `Callable[[Input], Output]` for a simple unary callback and `Callable[[A, B], R]` for a two-positional-argument callback.
- Use `Protocol` with `__call__` for meaningful keyword-only arguments or a richer callable contract.
- Use `ParamSpec` to preserve parameter types in generic wrappers and `TypeVar` to relate inputs and outputs.
- Prefer `object` to `Any` when values should remain opaque; use `Any` deliberately at dynamic boundaries.
- Remember that type annotations are primarily static metadata. Python does not automatically enforce them at runtime.
- Type-check the examples with the project's selected tool (`mypy` or `pyright`) and keep the tool configuration consistent across the repository.
- A generic heterogeneous composition function is difficult to type precisely because each stage may change the type. Do not misrepresent this as `Callable[[T], T]` unless every stage truly preserves `T`.

## 11. Hands-on exercises with expected outcomes

Attempt each exercise before reading its expected outcome. Use pytest for the cases where correctness can be expressed as assertions.

### Exercise 1 — Five ways to use a function as a value

Define a function `clean_code(value: str) -> str`. Demonstrate: aliasing, storing in a list, storing in a dictionary, passing as an argument, and returning from a factory.

**Expected outcome:** every stored or passed reference is callable; `clean_code(" a ")` returns `"a"`; aliasing does not create a copy of the function.

### Exercise 2 — Dispatch table

Replace a command handler with at least five commands using a dictionary. Each handler should accept a context and return a new context. Unknown commands must raise `ValueError` listing the supported names.

**Expected outcome:** all known commands call the correct handler; the error for an unknown command is deterministic and useful; the registry stores functions, not their return values.

### Exercise 3 — Function metadata inspection

Write a function with a docstring, one positional default, one keyword-only default, and annotations. Print its `__name__`, `__qualname__`, `__doc__`, `__module__`, `__defaults__`, `__kwdefaults__`, `__annotations__`, `__code__`, and `__dict__`.

**Expected outcome:** you can explain each field and identify which attributes are implementation/tooling details rather than a stable business contract. Do not assert a memory address or assume source inspection works in every environment.

### Exercise 4 — Adapt arguments with `partial`

Write `validate_range(value, *, minimum, maximum, field)` and use `partial` to create a validator for a temperature column and a separate validator for a score column.

**Expected outcome:** each configured callable accepts the intended value argument; out-of-range values raise an informative error; tests verify lower and upper boundaries.

### Exercise 5 — Compose and pipe

Implement `compose(*fns)` and `pipe(value, *fns)`. Test both order conventions using multiplication and addition, and test no functions.

**Expected outcome:** `compose(add_one, double)(3)` returns `7`; `pipe(3, double, add_one)` also returns `7`; both empty forms return their input unchanged. State the ordering in each docstring.

### Exercise 6 — Configurable transformation pipeline

Build two or more record transformations and a registry keyed by configuration names. Apply a sequence of configured steps to a sample record.

**Expected outcome:** transformation order affects the result where appropriate; unknown names fail clearly; caller-owned input is not mutated unless mutation is an explicit contract; tests cover missing and invalid fields.

### Exercise 7 — Callable protocol

Define a `Protocol` for a validator accepting `row` and keyword-only `strict`. Implement it as a plain function and pass it to an orchestration function.

**Expected outcome:** the code runs without inheritance from the protocol; a static type checker accepts a compatible implementation and flags a mismatched signature.

### Exercise 8 — Callback lifetime

Create an instance, save its bound method, remove the ordinary instance reference, and inspect a `weakref.ref`. Then release the saved callback.

**Expected outcome:** the saved bound method keeps the instance alive; after deleting the callback and with no other strong references, the weak reference returns `None` (assuming no other reference remains).

### Exercise 9 — Strategy injection

Write a function that accepts a `Callable[[Record], bool]` and filters records. Test a strict validator and a permissive validator without changing the orchestration code.

**Expected outcome:** each policy is independently testable; the orchestrator does not need to know the implementation details of either validator.

## 12. Self-check questions and solutions

### Questions

1. What is the difference between `f` and `f()`?
2. Why does `alias = f` not copy a function?
3. Name five callable categories besides ordinary `def` functions, or including functions if you prefer.
4. Why is `callable(value)` insufficient to prove that `value("x")` will succeed?
5. What do `__self__` and `__func__` tell you about a bound method?
6. Why can a bound method stored in a scheduler keep an object alive?
7. When is a dispatch table clearer than `if/elif`, and what boundary validation should it perform?
8. What are the limitations of `Callable[[A], R]` for keyword-only callback parameters?
9. How do `ParamSpec` and `TypeVar` differ conceptually?
10. State the execution order of `compose(f, g)(x)` and `pipe(x, f, g)`.
11. Why should a configuration-driven registry use allow-listed names rather than evaluating strings as code?
12. Give one reason to choose a class or callable instance instead of a function.

### Solutions

1. `f` refers to the callable object; `f()` invokes it and evaluates to its return value (or raises an exception).
2. Assignment binds another name to the same object. `alias is f` is true unless one of the names is later rebound.
3. Examples: lambdas, bound methods, built-ins, classes, callable instances implementing `__call__`, and `functools.partial` objects.
4. `callable` only indicates that the object is callable in general. The supplied arguments may not match its signature, and the call may raise for other reasons.
5. `__self__` is the receiver instance; `__func__` is the underlying function used to create the bound method.
6. A bound method strongly references its receiver, so a long-lived callback collection may retain the instance.
7. A dispatch table is useful when each named branch maps to a handler and the mapping is easier to inspect or extend. Validate the command against the approved registry and report unknown names clearly.
8. `Callable[[A], R]` primarily describes positional argument types and a return type; it does not precisely name keyword-only parameters or model every parameter kind. Use a `Protocol` with `__call__` for a richer signature.
9. `TypeVar` relates types across positions (for example, input and output); `ParamSpec` represents a callable's parameter specification so a wrapper can preserve its argument shape for static typing.
10. `compose(f, g)(x)` is `f(g(x))` (right to left); `pipe(x, f, g)` is `g(f(x))` (left to right).
11. An allow-list constrains configuration to known operations. Evaluating strings as code creates an unnecessary code-execution risk and obscures the application's trust boundary.
12. Choose a class/callable instance when behaviour needs explicit mutable state, multiple related methods, resource lifecycle, or a durable identity/configuration object.

## 13. Summary and completion checklist

First-class functions are ordinary Python objects that can be referenced, stored, passed, returned, and invoked. Higher-order functions separate the algorithm or orchestration from the behaviour supplied by a caller. This enables callbacks, key functions, strategies, dispatch tables, function factories, argument adaptation, and transformation pipelines.

Before marking this lesson complete, verify that you can:

- [ ] Explain how `def` binds a function object to a name.
- [ ] Distinguish references from calls and avoid registering callback results accidentally.
- [ ] Store functions in collections and invoke the selected function safely.
- [ ] Write a higher-order function with a useful `Callable` annotation.
- [ ] Inspect common function metadata and explain its limitations.
- [ ] Recognise callable objects without assuming all callables are function objects.
- [ ] Explain `__self__`, `__func__`, method binding, and callback lifetime.
- [ ] Use `partial` to adapt a function's arguments.
- [ ] Explain when `Protocol`, `ParamSpec`, and `TypeVar` are appropriate.
- [ ] Implement and test composition and piping with documented order.
- [ ] Build a controlled transformation registry with helpful unknown-key errors.
- [ ] Test callback ordering, error paths, input mutation, and empty cases.
- [ ] Explain when a function is simpler than a class and when a class provides clearer state/lifecycle management.

## 14. References to relevant adjacent Stage 1 modules

Use these project-tree paths as the intended follow-up map; do not treat this lesson as a replacement for their deeper coverage.

- **Module 1.3 — `03-Control-Flow-Functions-Scope-and-Errors/`**
  - `03-functions-parameters-and-return-values.md`
  - `04-function-arguments-defaults-and-docstrings.md`
  - `05-scope-lifetime-and-global-state.md`
  - `06-pure-functions-and-side-effects.md`
  - Foundation for parameters, defaults, scope, side effects, and return behaviour.
- **Module 1.4 — `04-Problem-Solving-Collections-and-Algorithmic-Habits/`**
  - `01-search-count-filter-map-and-aggregate.md`
  - `02-grouping-deduplication-and-sorting.md`
  - Foundation for key functions, collection processing, and algorithm selection.
- **Module 1.7 — `07-Testing-and-Systematic-Debugging/`**
  - `02-pytest-assertions-fixtures-and-parametrization.md`
  - `03-arrange-act-assert-and-test-design.md`
  - `04-boundary-invalid-and-regression-tests.md`
  - `07-mocking-and-test-doubles.md`
  - Test higher-order functions, edge cases, and injected dependencies.
- **Module 1.8 — `08-Object-Oriented-Design-Data-Modelling-and-Functional-Style/`**
  - `05-protocols-interfaces-and-dependency-inversion.md`
  - `06-pure-functions-immutability-and-higher-order-functions.md`
  - `07-separating-side-effects-from-domain-logic.md`
  - `08-dependency-boundaries-and-layered-design.md`
  - Context for protocols, functional style, dependency inversion, and boundaries.
- **Module 1.9 — `09-Advanced-Production-Oriented-Python-Foundations/`**
  - `02-decorators.md`
  - `05-advanced-typing-essentials.md`
  - `09-functools-cache-and-partial.md`
  - `10-python-object-model-and-garbage-collection.md`
  - Follow-up for decorators, deeper typing, `partial`, and object lifetime.
- **Module 1.11 — `11-Advanced-Python-Data-Model-and-Object-Design/`**
  - `06-descriptors-and-attribute-lookup-order.md`
  - Full descriptor and attribute-lookup mechanics; only the method-binding intuition is introduced here.
- **Module 1.12 — `12-Metaprogramming-and-Dynamic-Python/`**
  - `01-introspection-with-inspect-and-dir.md`
  - Deeper introspection and dynamic Python; this lesson covers only practical `inspect` usage.
- **Module 1.13 — `13-Standard-Library-Toolkit/`**
  - `02-operator-and-functional-composition.md`
  - `10-weakref-contextvars-and-copy.md`
  - Functional helpers, operator utilities, and weak-reference tools.
- **Module 1.19 — `19-CPython-Internals-and-Runtime-Behaviour/`**
  - `03-frames-call-stack-and-the-evaluation-loop.md`
  - Deeper call-frame and runtime mechanics.
- **Module 1.20 — `20-Design-Patterns-and-Library-API-Design/`**
  - `04-behavioural-patterns-strategy-observer-and-command.md`
  - `05-plugin-and-registry-patterns.md`
  - Formal treatment of strategy, observer, command, and registry patterns.
- **Module 1.24 — `24-Functions-and-OOP-Gap-Lessons/`**
  - Next: `02-lambda-expressions-and-when-not-to-use-them.md`
  - Then: `03-closures-and-captured-variables.md` and `04-nonlocal-and-late-binding-pitfalls.md`
  - Later lessons deepen functional helpers, callable objects, and function-design review.

---

**Completion criterion:** you can explain the concepts without memorising syntax, implement the exercises, and use tests to demonstrate callback order, dispatch behaviour, composition order, and error handling.
