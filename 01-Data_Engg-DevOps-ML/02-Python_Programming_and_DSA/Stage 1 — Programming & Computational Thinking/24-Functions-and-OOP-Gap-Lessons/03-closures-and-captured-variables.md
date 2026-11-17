# Lesson 03 — Closures and Captured Variables

> **Stage 1 · Programming & Computational Thinking · Module 1.24**  
> **Target runtime:** Python 3.12+  
> **Level:** Beginner → Intermediate → Advanced

A closure lets a function retain access to names from an enclosing function scope after that enclosing call has returned. This is the foundation for function factories, callbacks with context, decorators, small stateful abstractions, and some memoization strategies.

The central rule for this lesson is: **a closure retains access to a variable binding (through a cell), not a frozen copy of the value that happened to be there when the function was created.**

## Learning objectives

By the end, you should be able to:

- Explain LEGB lookup and identify local, enclosing, global, and built-in names.
- Distinguish a closure, a free variable, a cell variable, a closure cell, and an ordinary local variable.
- Build function factories and independent stateful closures using `nonlocal` where reassignment is needed.
- Inspect a closure with `__closure__`, `__code__.co_freevars`, and `cell_contents` without treating those details as a stable application API.
- Choose between a closure, a plain function, `functools.partial`, and a small class.
- Explain how closures support decorators, memoization, and partial application.
- Recognize lifetime and memory-retention risks, including callbacks that keep objects alive.
- Read relevant `dis` output while understanding that bytecode details vary by Python version and implementation.
- Explain Python 3.12+ comprehension scope without confusing it with the separate late-binding issue covered in Lesson 04.
- Implement and test `once(fn)`, `memoize(fn)`, and `counter_factory()`; reason about cache invalidation, hashability, concurrency, and serialization.
- Test closures through their public behavior, state transitions, configuration, and independence.

## Prerequisites and boundaries

This lesson builds on:

- Module 1.2: names, objects, identity, mutability, and references.
- Module 1.3 lessons 01–06: function basics, parameters, scope/lifetime, and pure functions versus side effects.
- Module 1.4: collections and comprehensions.
- Module 1.7: pytest and debugging.
- Module 1.8: encapsulation, composition, classes, and dataclasses.
- Module 1.9 lessons 02 and 09: decorators and `functools`.
- Module 1.19: symbol-table/compiler and runtime-inspection context.

Use Python 3.12 or newer and `pytest`; `dis`, `inspect`, and a debugger are useful for exploration.

**Scope boundary:** this is a focused lesson about closures. Lesson 04, `04-nonlocal-and-late-binding-pitfalls.md`, treats assignment rules, `UnboundLocalError`, and loop late binding in depth. We will identify those interactions here, but not turn them into a second full lesson. Likewise, decorators, concurrency, and CPython internals are discussed only to explain closure behavior.

---

## 1. Scope foundations: the LEGB lookup path

Python resolves an ordinary name by searching these scopes in order:

```text
L — Local       current function's local namespace
E — Enclosing   relevant enclosing function scopes
G — Global       current module's global namespace
B — Built-in     names in the builtins namespace
```

A simple mental diagram:

```text
builtins (e.g. len, sum)
  ↑ searched last
module globals (e.g. DEFAULT_REGION)
  ↑
enclosing function (e.g. make_parser's prefix)
  ↑
current function locals (e.g. parse's row)
  ↑ searched first
```

The diagram is a *lookup order*, not a claim that every function has all four kinds of name. A function may have no enclosing function. Class bodies and methods have some additional rules; the ordinary LEGB mnemonic is not a complete description of class namespace behavior.

### 1.1 A tiny example

```python
DEFAULT_REGION = "ap-south-1"  # global

from collections.abc import Callable


def make_label(prefix: str) -> Callable[[str], str]:
    suffix = "daily"            # enclosing for label()

    def label(dataset: str) -> str:
        local_note = "load"      # local to label()
        return f"{prefix}:{dataset}:{suffix}:{DEFAULT_REGION}:{len(local_note)}"

    return label

build_label = make_label("bronze")
print(build_label("events"))
# bronze:events:daily:ap-south-1:4
```

In `label`, `dataset` and `local_note` are local; `prefix` and `suffix` are enclosing names; `DEFAULT_REGION` is global; `len` is built-in. `label` is returned, so its enclosing call has finished, but its enclosing bindings remain accessible.

For production annotations, prefer a concrete callable type such as `Callable[[str], str]` over the built-in `callable` function used as an annotation. A fully typed version is:

```python
from collections.abc import Callable

def make_label_typed(prefix: str) -> Callable[[str], str]:
    suffix = "daily"

    def label(dataset: str) -> str:
        return f"{prefix}:{dataset}:{suffix}"

    return label
```

### 1.2 Lookup is not the same as assignment

Reading a name that belongs to an enclosing scope is usually automatic. Rebinding it from the nested function requires an explicit declaration:

```python
from collections.abc import Callable


def make_accumulator() -> Callable[[int], int]:
    total = 0

    def add(amount: int) -> int:
        nonlocal total
        total += amount
        return total

    return add
```

`nonlocal total` says that assignment should target the nearest enclosing function binding named `total`. It does not mean “make this variable global,” and it does not create a copy. Reassignment rules are covered more fully in Lesson 04.

A mutable object can sometimes be mutated without `nonlocal`, because the *binding* is not being reassigned:

```python
from collections.abc import Callable


def make_batch() -> Callable[[str], int]:
    rows: list[str] = []

    def append_row(row: str) -> int:
        rows.append(row)  # mutates the list; does not rebind `rows`
        return len(rows)

    return append_row
```

That distinction matters: mutation still creates shared state and side effects even when `nonlocal` is unnecessary.

---

## 2. What exactly is a closure?

A **closure** is a function together with access to bindings from an enclosing lexical scope. The function can outlive the call that created it. In CPython, captured bindings are represented by *cells*, and a function's `__closure__` attribute exposes a tuple of cell objects for its free variables.

Consider the simplest factory:

```python
def make_multiplier(factor: int):
    def multiply(value: int) -> int:
        return factor * value
    return multiply

triple = make_multiplier(3)
print(triple(7))  # 21
```

The outer call returns; the local name `factor` is no longer in an active outer frame. Nevertheless, `triple(7)` can still read the binding for `factor`. The closure keeps the required binding alive.

### 2.1 Vocabulary: local, free, cell

- **Local variable:** a name local to a function, such as `value` inside `multiply`.
- **Free variable:** a name used by a function but not bound locally there, whose binding comes from an enclosing function scope. `factor` is free in `multiply`.
- **Cell variable:** from the enclosing function's perspective, a local variable that must be made available to a nested function. `factor` is a cell variable in `make_multiplier`.
- **Closure cell:** the runtime cell that holds a reference to the current object bound to a captured name. A nested function uses the cell to access that binding.
- **Closure:** the function plus its references to the cells needed for free variables. Not every nested function necessarily has free variables or a non-empty `__closure__`.

One name can be described differently depending on which function's perspective you take: `factor` is a cell variable in `make_multiplier` and a free variable in `multiply`.

### 2.2 A variable is not a copied value

A closure does not normally snapshot the current value at creation time. It retains access to a binding. Rebinding that name changes what the closure sees:

```python
def make_reader():
    status = "queued"

    def read() -> str:
        return status

    def update(new_status: str) -> None:
        nonlocal status
        status = new_status

    return read, update

read_status, update_status = make_reader()
print(read_status())       # queued
update_status("loaded")
print(read_status())       # loaded
```

The `read` and `update` functions share the same enclosing binding. They do not each hold separate copies of the string. Rebinding `status` changes the binding; the string objects themselves are immutable.

Captured objects may also be mutable:

```python
from collections.abc import Callable


def make_tags() -> Callable[[str], set[str]]:
    tags = {"source"}

    def add_tag(tag: str) -> set[str]:
        tags.add(tag)
        return set(tags)

    return add_tag

add_tag = make_tags()
print(sorted(add_tag("validated")))  # ['source', 'validated']
```

The closure retains a reference to the set object. Mutating that set is visible to later calls. This is shared mutable state, so document it and consider whether a pure function or a class would make ownership clearer.

---

## 3. Beginner examples: closures in practice

### 3.1 Independent counters

```python
from collections.abc import Callable

def counter_factory(start: int = 0) -> Callable[[], int]:
    count = start

    def next_count() -> int:
        nonlocal count
        count += 1
        return count

    return next_count

first = counter_factory()
second = counter_factory(10)
print(first(), first(), second(), first(), second())
# 1 2 11 3 12
```

Each call to `counter_factory` creates a new binding for `count`. The closures returned by separate factory calls have independent state. The counter starts by returning `start + 1`; the initial value is not returned until after the first increment.

**Why it matters:** a retry counter, local sequence, or small state machine can be expressed without defining a class when a single operation is enough.

**Limitation:** the state is hidden and the returned function exposes only one operation. If callers need `reset`, `peek`, persistence, or rich inspection, a class is usually clearer.

### 3.2 Multipliers and configurable behavior

```python
from collections.abc import Callable

def make_multiplier(factor: float) -> Callable[[float], float]:
    def multiply(value: float) -> float:
        return value * factor
    return multiply

usd_to_cents = make_multiplier(100)
print(usd_to_cents(12.5))  # 1250.0
```

This is a **function factory**: input configuration is supplied once, and the result is a function specialized for repeated use. Keep units explicit in real financial code; a `Decimal`-based conversion or a domain-specific type may be more appropriate than `float`.

### 3.3 A configurable validator

```python
from collections.abc import Callable

def make_length_validator(min_length: int, max_length: int) -> Callable[[str], str]:
    if min_length < 0 or max_length < min_length:
        raise ValueError("invalid length range")

    def validate(value: str) -> str:
        if not min_length <= len(value) <= max_length:
            raise ValueError(
                f"expected length {min_length}..{max_length}; got {len(value)}"
            )
        return value

    return validate

validate_dataset = make_length_validator(3, 24)
print(validate_dataset("events"))  # events
```

Validate configuration at factory construction time when possible. This makes invalid configuration fail early rather than during a later pipeline record.

### 3.4 A logger prefix and callback context

```python
from collections.abc import Callable

def make_log_formatter(component: str) -> Callable[[str], str]:
    def format_message(message: str) -> str:
        return f"[{component}] {message}"
    return format_message

api_log = make_log_formatter("api-ingest")
warehouse_log = make_log_formatter("warehouse-load")
print(api_log("page fetched"))
print(warehouse_log("batch committed"))
# [api-ingest] page fetched
# [warehouse-load] batch committed
```

The returned function carries the component context without requiring every call site to pass it again. For production logging, prefer the `logging` module and structured fields rather than building an entire logging framework from closures.

### 3.5 Closures as small private-state abstractions

Closures can keep implementation details out of the caller's namespace. This is a convention, not a security boundary: introspection can reveal captured state, and code that holds the returned function can use its public behavior.

A useful rule of thumb: a closure is a good fit when there is one primary operation and a small amount of stable configuration or state. Prefer a class when there are several related operations or state needs to be explicit and inspectable.

---

## 4. Inspecting a closure safely

Python function objects expose useful introspection attributes:

- `fn.__code__.co_freevars`: tuple of free-variable names in the code object.
- `fn.__closure__`: tuple of closure cells, or `None` when there are no closure cells.
- `cell.cell_contents`: the object currently referenced by a particular cell. Access can raise `ValueError` if the cell is empty.

Example:

```python
def make_offsetter(offset_value: int):
    def add(value: int) -> int:
        return value + offset_value
    return add

add_five = make_offsetter(5)
print(add_five(10))
print(add_five.__code__.co_freevars)  # ('offset_value',)
print(add_five.__closure__[0].cell_contents)  # 5
```

The order of names in `co_freevars` corresponds to the order of cells in `__closure__`; use that relationship when exploring a function. Do not assume a particular cell index without checking the corresponding name.

A more defensive inspection helper:

```python
from types import FunctionType

def show_closure(fn: FunctionType) -> dict[str, object]:
    names = fn.__code__.co_freevars
    cells = fn.__closure__ or ()
    return {
        name: cell.cell_contents
        for name, cell in zip(names, cells, strict=True)
    }

print(show_closure(add_five))  # {'offset_value': 5}
```

**Caveats:**

- These are introspection details, not a recommended way for application logic to read configuration. Test the returned function's behavior instead.
- `__closure__` may be `None`; not all functions close over anything.
- `cell_contents` exposes the current referenced object, not a historical snapshot. Mutable values can be modified, and rebinding can change what a cell exposes.
- Internal details and bytecode are implementation- and version-sensitive. Avoid tests that require exact bytecode sequences or exact closure layout unless the purpose is explicitly runtime education.
- The contents may be sensitive. Do not dump arbitrary closure contents into production logs.

---

## 5. Intermediate applications

### 5.1 Closure-based callback configuration

```python
from collections.abc import Callable, Iterable

def make_row_filter(required_status: str) -> Callable[[dict[str, str]], bool]:
    def matches(row: dict[str, str]) -> bool:
        return row.get("status") == required_status
    return matches

is_ready = make_row_filter("ready")
rows = [
    {"id": "a", "status": "ready"},
    {"id": "b", "status": "pending"},
]
ready_rows = [row for row in rows if is_ready(row)]
print([row["id"] for row in ready_rows])  # ['a']
```

A configured predicate can be passed to a filtering stage or callback API. The closure makes the configuration explicit at construction and keeps the call signature small. Avoid hiding configuration that a caller should be able to inspect or override.

### 5.2 Decorators: the closure connection

A decorator often returns a wrapper that closes over both the original function and decorator configuration. This is the relevant closure concept; decorator mechanics are covered in Module 1.9.

```python
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def add_prefix(prefix: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorate(fn: Callable[P, R]) -> Callable[P, R]:
        @wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            print(prefix)
            return fn(*args, **kwargs)
        return wrapper
    return decorate
```

The `wrapper` closes over `prefix` and `fn`. `wraps` preserves useful metadata such as `__name__` and `__doc__`; it does not remove the closure or make it automatically serializable.

### 5.3 Partial application

Partial application fixes some arguments now and leaves the rest for later. A closure can implement it, but the standard tool is usually `functools.partial`:

```python
from functools import partial

def build_partition(table: str, region: str, day: str) -> str:
    return f"{table}/{region}/{day}"

partition_for_events = partial(build_partition, "events", "ap-south-1")
print(partition_for_events("2026-10-18"))
# events/ap-south-1/2026-10-18
```

Use `partial` when the job is simply to bind positional or keyword arguments. A custom closure is useful when the behavior needs validation, transformations, or private state in addition to fixed arguments. `partial` is generally more transparent and often easier to pickle than a nested closure, provided the wrapped callable and bound arguments are themselves picklable.

### 5.4 Closure memoization

Memoization stores a result for a key and reuses it for later calls. A closure is a natural place to keep a private cache dictionary, but caching introduces semantics beyond “remember a value”: key design, invalidation, memory bounds, failures, and concurrency all matter. See Section 8 for a complete implementation and comparison with `functools.cache`.

### 5.5 Composition and currying: closures as function factories

A closure can build a function by retaining another function or a configuration value. For a simple two-function composition, the inner function calls `g` first and passes its result to `f`:

```python
from collections.abc import Callable
from typing import TypeVar

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")

def compose2(f: Callable[[B], C], g: Callable[[A], B]) -> Callable[[A], C]:
    """Return a function equivalent to f(g(value))."""
    def composed(value: A) -> C:
        return f(g(value))
    return composed

normalize = compose2(str.upper, str.strip)
print(normalize("  events  "))  # EVENTS
```

This makes the execution order explicit: `str.strip` runs before `str.upper`. A named function is often clearer when composition has side effects, multiple arguments, or error-handling policy.

Currying transforms a multi-argument operation into a sequence of one-argument calls. A small illustrative example is:

```python
from collections.abc import Callable

def add_left(left: int) -> Callable[[int], int]:
    def add_right(right: int) -> int:
        return left + right
    return add_right

add_five = add_left(5)
print(add_five(8))  # 13
```

The returned function closes over `left`. Python code does not need to be curried to use higher-order functions; if the goal is only to bind existing arguments, `functools.partial` is usually more direct.

Memoizing a factory deserves special care. Caching a factory can return the *same function object and its captured state* for repeated configuration keys, rather than a fresh independent closure each time. Only cache a factory when that reuse is intentional and the configuration is hashable; test object identity and state-sharing semantics explicitly.

---

## 6. Closure versus class: choosing the right abstraction

A closure with mutable state can be similar to an object with one method and private attributes. They are not interchangeable in every context.

| Concern | Closure | Class / callable instance |
|---|---|---|
| Small configuration plus one operation | Often concise | Can be more ceremony |
| Multiple related operations (`reset`, `peek`, `snapshot`) | Possible by returning several functions, but awkward | Usually clearer as methods |
| State visibility and documentation | State is implicit in the returned function | Fields and methods can be documented explicitly |
| Type annotations and editor support | Callable return type may hide configuration/state shape | Named class provides a clear type and API |
| Pickling / multiprocessing | Nested functions and closures are generally not picklable by standard `pickle` | Top-level class instances can be picklable if their contents are picklable |
| Testing | Test observable behavior and instance independence | Test public methods and state transitions |
| Memory ownership | Captures may retain objects invisibly | Fields still retain objects, but ownership is often easier to inspect |
| Evolution over time | Can become hard to extend as operations grow | Usually easier to extend without returning a bundle of functions |

Choose a closure for a small, cohesive behavior with limited state. Choose a class when state is central to the domain, multiple operations are needed, configuration should be inspectable, or serialization and maintainability are important. Do not use a class merely because a closure exists; do not use a closure merely to avoid writing a small class.

---

## 7. Runtime mechanics: cells, symbol tables, and `dis`

### 7.1 Compiler decisions

Before a function runs, Python compiles its code and determines how names are used. The compiler's symbol-table analysis identifies names that are local, global, free, or cell variables. If an enclosing function's local binding is referenced by a nested function, the compiler arranges for that binding to be stored in a cell accessible to both scopes.

This is why a closure is not simply “a saved copy of the outer frame.” The implementation retains the needed binding(s), not the whole active execution frame as a general-purpose snapshot.

### 7.2 Relevant bytecode instructions

Use `dis` to explore the code objects on the Python version you actually run:

```python
import dis

def make_counter_for_dis():
    count = 0
    def increment() -> int:
        nonlocal count
        count += 1
        return count
    return increment

factory_code = make_counter_for_dis.__code__
inner_fn = make_counter_for_dis()

dis.dis(make_counter_for_dis)
dis.dis(inner_fn)
print(make_counter_for_dis.__code__.co_cellvars)
print(inner_fn.__code__.co_freevars)
```

Instructions you may encounter include:

- `MAKE_CELL`: establishes a cell for a local that must be captured (version/context dependent).
- `LOAD_CLOSURE`: loads a cell for constructing a nested function's closure tuple (may appear in relevant bytecode layouts).
- `LOAD_DEREF`: reads a cell/free-variable binding.
- `STORE_DEREF`: writes to a cell binding, including a `nonlocal` rebinding.
- `LOAD_FAST` / `STORE_FAST`: common operations for ordinary fast locals.

Do not memorize an exact disassembly listing. Python 3.11+ changed bytecode substantially, and Python 3.12 inlined comprehensions under PEP 709; instruction sequences can differ by version, optimization, and function shape. The reliable learning goal is to recognize the *role* of a cell and to inspect `co_freevars`/`co_cellvars`, not to depend on a particular instruction offset.

### 7.3 Cell identity and shared state

Two nested functions returned from the same factory can share a cell for the same captured variable. Two separate factory calls normally create separate cells for their independent local bindings. For debugging only, comparing `id(cell)` can help illustrate this, but IDs are process-specific and should not become application logic.

---

## 8. Memoization: closure implementation versus `functools.cache`

### 8.1 A small `memoize(fn)` closure

The implementation below is deliberately simple and useful for learning. It caches only calls whose positional and keyword arguments are hashable. It has no invalidation or size limit and is **not designed as a thread-safe single-flight cache**: two concurrent misses may compute the same key more than once.

```python
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar, cast

P = ParamSpec("P")
R = TypeVar("R")

def memoize(fn: Callable[P, R]) -> Callable[P, R]:
    cache: dict[object, R] = {}

    @wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        key = (args, tuple(kwargs.items()))
        # Raise TypeError immediately for unhashable keys instead of silently
        # using an unsafe or ambiguous representation.
        hash(key)
        if key not in cache:
            cache[key] = fn(*args, **kwargs)
        return cast(R, cache[key])

    return wrapper
```

This example intentionally does not normalize keyword argument order. Calls such as `f(a=1, b=2)` and `f(b=2, a=1)` can occupy different cache entries even if the wrapped function treats them equivalently. A production cache must define key semantics explicitly. It also caches only successful results because an exception prevents assignment to `cache[key]`.

Example:

```python
calls = 0

@memoize
def normalize_code(code: str) -> str:
    global calls
    calls += 1
    return code.strip().upper()

print(normalize_code(" ab "))  # AB
print(normalize_code(" ab "))  # AB, reused result
print(calls)                    # 1
```

Global `calls` is used here only to make the example's effect visible; real tests should generally keep such instrumentation local to a test or use a mock.

### 8.2 Compare with `functools.cache`

```python
from functools import cache

@cache
def normalize_code_stdlib(code: str) -> str:
    return code.strip().upper()
```

`functools.cache` is an unbounded cache equivalent in behavior to `lru_cache(maxsize=None)`. It is usually the first choice for a pure function with hashable arguments when unbounded retention is acceptable. `functools.lru_cache(maxsize=...)` is a useful bounded alternative.

| Issue | Custom closure cache above | `functools.cache` |
|---|---|---|
| Hashability | Key components must be hashable; `hash(key)` raises `TypeError` otherwise | Arguments must be hashable; raises `TypeError` otherwise |
| Memory growth | Unbounded dictionary until the wrapper/cache is released | Unbounded by definition; use `lru_cache(maxsize=...)` for a bound |
| Invalidation | No public invalidation API in this example | `cache_clear()` and `cache_info()` are available on the decorated function |
| Concurrency | No synchronization; duplicate work on concurrent misses is possible | Cache data structure is thread-safe, but concurrent misses may still call the wrapped function more than once |
| Key normalization | Defined by this implementation; keyword order remains significant here | Uses standard-library cache key machinery; different keyword order may produce separate entries |
| Custom policy | Can implement custom eviction, normalization, or invalidation | Standard behavior is simpler and better understood |

Caching is correct only if the result remains valid for the lifetime of the cache entry. Avoid caching functions that depend on mutable external state, current time, authorization, database contents, or side effects unless the key and invalidation policy account for those dependencies. Never assume a cache is safe merely because it is hidden in a closure.

### 8.3 A closure memoizer with invalidation?

If callers need to clear entries, inspect hit counts, bound memory, or coordinate concurrent work, returning a function alone may hide too much. Consider `functools.lru_cache`, a small cache class, or a dedicated caching layer with explicit policy. The correct choice depends on cache lifetime, workload, and correctness requirements—not on whether closures are elegant.

---

## 9. Captured-object lifetime and memory retention

A closure keeps its referenced cells alive; a cell keeps its current referenced object alive. Therefore, a long-lived callback can retain a large object graph unintentionally.

### 9.1 The data-engineering risk

```python
def make_bad_row_parser(large_dataframe):
    # The returned function keeps the DataFrame reachable through its closure.
    def parse(row_id: int) -> dict[str, object]:
        row = large_dataframe.loc[row_id]
        return row.to_dict()
    return parse
```

If a scheduler stores `parse` for weeks, the DataFrame may remain alive even after the pipeline's main code no longer needs it. This can look like a leak, though it is ordinary reference retention rather than necessarily a garbage-collector defect.

Prefer a smaller captured configuration, a query/repository object with explicit lifecycle, or passing the required data explicitly:

```python
def parse_row(row: dict[str, object], required_columns: tuple[str, ...]) -> dict[str, object]:
    return {name: row[name] for name in required_columns}
```

Passing data explicitly may be more verbose, but makes dependencies and ownership easier to see.

### 9.2 Callbacks and bound objects

A closure that captures `self` can keep the instance alive. For example, registering a closure with a long-lived event bus can retain the object and everything reachable from it. The event bus may also retain the callback after the object is logically finished.

Mitigations include:

- Unregister callbacks during teardown or use a subscription/context-manager API.
- Capture only small immutable configuration instead of a large object.
- Where appropriate, use `weakref`/`weakref.WeakMethod` patterns, understanding that the target may disappear before the callback runs.
- Avoid global registries of callbacks without a clear ownership and cleanup policy.
- Use `tracemalloc`, object references, or heap profiling to confirm retention before changing code.

Closures do not automatically cause leaks. They make dependencies implicit, so lifecycle review is important when callbacks outlive the function that created them.

---

## 10. Comprehensions in Python 3.12+: scope and closures

Python 3 comprehension semantics prevent the iteration variable from leaking into the surrounding scope. Python 3.12 implemented comprehension inlining (PEP 709), which changes implementation details and bytecode, but **does not make the comprehension's iteration variable leak into the surrounding scope**.

A nested function created inside a comprehension can still close over the comprehension's iteration variable. That is a separate question from whether the name leaks out of the comprehension.

```python
functions = [lambda: number for number in range(3)]
print([fn() for fn in functions])  # [2, 2, 2]
```

The functions are created while iterating, but each lambda refers to the same comprehension-scope binding of `number`, which has its final value when the functions are called. This is a **late-binding** example, not evidence that the variable leaked into the module scope. Lesson 04 explains the pitfall and remedies in detail.

For contrast, the comprehension variable does not become a global/module local:

```python
squares = [number * number for number in range(3)]
# `number` is not introduced in the surrounding scope by the comprehension.
```

Default arguments can snapshot an object reference at function creation, but that is a binding-time technique with subtleties for mutable objects. Since this module's exact scope is closure mechanics, see Lesson 04 for the recommended loop-capture patterns rather than treating a workaround as the general definition of a closure.

---

## 11. Concurrency and serialization trade-offs

### 11.1 Shared mutable closure state

Closures returned from the same factory can intentionally share state. If multiple threads call a stateful closure concurrently, compound operations such as “read count, increment, store” need synchronization when correctness depends on a strict sequence. Do not rely on the GIL as an application-level correctness guarantee, especially across Python implementations and evolving runtime versions.

A lock can protect a tiny counter:

```python
from collections.abc import Callable
from threading import Lock

def thread_safe_counter(start: int = 0) -> Callable[[], int]:
    count = start
    lock = Lock()

    def next_count() -> int:
        nonlocal count
        with lock:
            count += 1
            return count

    return next_count
```

This demonstrates the closure principle only. It does not solve all coordination problems: lock contention, reentrancy, cancellation, process boundaries, and persistence require separate design. If several operations must share the same lock and state, a class may communicate the design better.

### 11.2 `once(fn)` and concurrency semantics

A basic `once(fn)` can remember the first successful result and return it on later calls. That implementation is not automatically thread-safe. If two threads make the first call simultaneously, the wrapped function may run twice unless a lock guards the check-and-call-and-store sequence. If the wrapped function fails, a common policy is to leave the wrapper uninitialized so a later call retries; document this policy because “once” can mean different things in different systems.

### 11.3 Pickling and multiprocessing

The standard `pickle` module normally serializes functions by qualified name, not by serializing arbitrary function code plus closure cells. A nested function is usually not importable by a stable module-level name, so nested closures generally cannot be pickled by standard `pickle` and may fail when passed to multiprocessing APIs that require picklable callables. Behavior also depends on the process start method and the callable/arguments.

Prefer a top-level function plus explicit arguments, `functools.partial` around a picklable top-level function, or a top-level callable class with picklable state. `partial` is not a magic guarantee: its underlying function and bound arguments must still be picklable. Avoid relying on non-standard serializers as a universal deployment fix; they may have different compatibility and security trade-offs.

---

## 12. Implement `once(fn)`, `memoize(fn)`, and `counter_factory()`

This section provides a compact reference implementation and tests. The implementations are teaching examples with explicitly stated limits, not drop-in distributed coordination primitives.

### 12.1 `once(fn)` — cache the first successful result

```python
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar, cast

P = ParamSpec("P")
R = TypeVar("R")
_MISSING = object()

def once(fn: Callable[P, R]) -> Callable[P, R]:
    result: object = _MISSING

    @wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        nonlocal result
        if result is _MISSING:
            result = fn(*args, **kwargs)
        return cast(R, result)

    return wrapper
```

Semantics: the first **successful** call determines the result. Later calls return that result and ignore their arguments. If the wrapped call raises, `result` remains `_MISSING`, so a later call retries. This is not thread-safe; concurrent first calls can invoke `fn` more than once. It is also unsuitable if each call's arguments should affect the result.

### 12.2 `memoize(fn)` — full implementation

Use the implementation from Section 8.1. It is repeated here only as a checklist of its contract:

- It keys by `(args, tuple(kwargs.items()))`.
- Every argument included in the key must be hashable.
- It caches successful results only.
- It has no cache bound or invalidation method.
- Keyword insertion order can affect cache identity.
- It may compute a miss more than once under concurrent calls.

If a learner changes the implementation, update tests to specify the new key and failure semantics.

### 12.3 `counter_factory()` — private mutable state

```python
from collections.abc import Callable

def counter_factory(start: int = 0) -> Callable[[], int]:
    count = start

    def increment() -> int:
        nonlocal count
        count += 1
        return count

    return increment
```

The returned callable has one public operation: increment and return. Each factory invocation gets independent state. It is intentionally not resettable; if reset/peek are requirements, expose a small class or return a documented set of operations.

---

## 13. Testing closures with pytest

Prefer tests that assert the behavior a caller relies on. Avoid making `__closure__` layout part of a normal unit-test contract unless the test is specifically about introspection.

Save the implementations from Sections 8.1, 12, and 14 in `closure_examples.py`. Then use the following tests in `test_closure_examples.py` (adjust imports if you organize the lesson examples differently):

```python
from functools import cache

import pytest

from closure_examples import counter_factory, memoize, once, rate_limited


def test_counter_increments_from_default_and_custom_start() -> None:
    counter = counter_factory()
    assert [counter(), counter(), counter()] == [1, 2, 3]

    other = counter_factory(10)
    assert other() == 11
    assert counter() == 4


def test_counter_instances_are_independent() -> None:
    left = counter_factory()
    right = counter_factory()
    assert left() == 1
    assert left() == 2
    assert right() == 1


def test_once_reuses_first_successful_result_and_ignores_later_args() -> None:
    calls: list[int] = []

    def compute(value: int) -> int:
        calls.append(value)
        return value * 10

    run_once = once(compute)
    assert run_once(3) == 30
    assert run_once(8) == 30
    assert calls == [3]


def test_once_retries_after_exception() -> None:
    attempts = 0

    def flaky() -> str:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise RuntimeError("temporary failure")
        return "ready"

    run_once = once(flaky)
    with pytest.raises(RuntimeError, match="temporary failure"):
        run_once()
    assert run_once() == "ready"
    assert run_once() == "ready"
    assert attempts == 2


def test_memoize_computes_a_hashable_key_once() -> None:
    calls = 0

    @memoize
    def square(number: int) -> int:
        nonlocal calls
        calls += 1
        return number * number

    assert square(4) == 16
    assert square(4) == 16
    assert calls == 1


def test_memoize_supports_keyword_arguments() -> None:
    @memoize
    def join(left: str, *, right: str) -> str:
        return left + right

    assert join("data", right="ops") == "dataops"
    assert join("data", right="ops") == "dataops"


def test_memoize_rejects_unhashable_arguments() -> None:
    @memoize
    def count_items(items: list[int]) -> int:
        return len(items)

    with pytest.raises(TypeError):
        count_items([1, 2])


def test_memoize_does_not_cache_exceptions() -> None:
    attempts = 0

    @memoize
    def sometimes(value: int) -> int:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise ValueError("not ready")
        return value

    with pytest.raises(ValueError, match="not ready"):
        sometimes(7)
    assert sometimes(7) == 7
    assert sometimes(7) == 7
    assert attempts == 2


def test_closure_configuration_is_visible_in_behavior() -> None:
    from closure_examples import make_length_validator

    validator = make_length_validator(2, 4)
    assert validator("abc") == "abc"
    with pytest.raises(ValueError):
        validator("x")


def test_functools_cache_is_an_alternative_for_hashable_inputs() -> None:
    calls = 0

    @cache
    def normalize(value: str) -> str:
        nonlocal calls
        calls += 1
        return value.strip().lower()

    assert normalize(" A ") == "a"
    assert normalize(" A ") == "a"
    assert calls == 1
    normalize.cache_clear()
    assert normalize(" A ") == "a"
    assert calls == 2


def test_length_validator_rejects_invalid_factory_configuration() -> None:
    from closure_examples import make_length_validator

    with pytest.raises(ValueError, match="invalid length range"):
        make_length_validator(-1, 4)
    with pytest.raises(ValueError, match="invalid length range"):
        make_length_validator(5, 4)


def test_rate_limiter_expires_calls_at_the_exact_window_boundary() -> None:
    now = 0.0

    def clock() -> float:
        return now

    @rate_limited(1, 10.0, clock=clock)
    def operation(value: int) -> int:
        return value

    assert operation(1) == 1
    with pytest.raises(RuntimeError, match="rate limit"):
        operation(2)
    now = 10.0
    assert operation(3) == 3


def test_rate_limiter_rejects_invalid_configuration() -> None:
    with pytest.raises(ValueError, match="must be positive"):
        rate_limited(0, 1.0)
    with pytest.raises(ValueError, match="must be positive"):
        rate_limited(1, 0.0)
```

The test file assumes `make_length_validator` from Section 3.3 is also defined in `closure_examples.py`. For a real project, keep production implementations in one importable module rather than copying code blocks into tests.

### 13.1 Test design checklist

- **Behavior:** does the returned function return the expected result or raise the documented exception?
- **Independence:** do two factory calls keep independent state?
- **Configuration:** does changing factory configuration change behavior as intended?
- **State transitions:** do repeated calls follow the documented transition sequence?
- **Failure policy:** are exceptions cached, retried, or propagated? Test the chosen policy.
- **Boundaries:** empty input, minimum/maximum values, invalid configuration, unhashable cache keys, and repeated calls.
- **Concurrency:** if thread safety is a requirement, add deliberate concurrent tests and synchronize the implementation; ordinary sequential tests do not prove thread safety.
- **Introspection:** use focused diagnostic tests for `co_freevars` and cells, not as a substitute for behavioral tests.

---

## 14. Optional rate-limiter exercise with an injectable clock

An injectable clock lets tests control time deterministically. It avoids sleeping and makes boundary behavior reproducible. This is a focused closure exercise, not a complete production rate-limiting design.

```python
import time
from collections import deque
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def rate_limited(
    calls: int,
    period: float,
    *,
    clock: Callable[[], float] = time.monotonic,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    if calls <= 0 or period <= 0:
        raise ValueError("calls and period must be positive")

    def decorate(fn: Callable[P, R]) -> Callable[P, R]:
        timestamps: deque[float] = deque()

        @wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            now = clock()
            while timestamps and now - timestamps[0] >= period:
                timestamps.popleft()
            if len(timestamps) >= calls:
                raise RuntimeError("rate limit exceeded")
            timestamps.append(now)
            return fn(*args, **kwargs)

        return wrapper

    return decorate
```

Here the closure retains `calls`, `period`, `clock`, `fn`, and the `timestamps` deque. The policy is a rolling window: timestamps at least `period` seconds old are removed before the next call. This example is not thread-safe, not distributed across workers, and does not define retry/backoff behavior. A timestamp is recorded before calling `fn`, so a failing call consumes a slot; decide explicitly whether your production policy limits attempts or successful operations. In a real service, consider whether a token bucket, a server-side limiter, or a shared store is required.

A deterministic test for the limiter:

```python
import pytest

from closure_examples import rate_limited


def test_rate_limiter_uses_injected_clock() -> None:
    now = 0.0

    def clock() -> float:
        return now

    @rate_limited(2, 10.0, clock=clock)
    def fetch_page(page: int) -> int:
        return page

    assert fetch_page(1) == 1
    assert fetch_page(2) == 2
    with pytest.raises(RuntimeError, match="rate limit"):
        fetch_page(3)

    now = 10.0
    assert fetch_page(4) == 4
```

The `clock` closure above reads `now` from the test's enclosing scope. In a test function, `now = 10.0` rebinds the same enclosing local binding read by `clock`. This is a simple example of why a closure captures a binding rather than a frozen value.

---

## 15. Common mistakes and debugging strategies

### Mistake 1: expecting a snapshot

**Symptom:** a callback reads a newer configuration value than expected.  
**Cause:** it closes over a variable binding; the binding was later changed.  
**Fix:** decide explicitly whether you want live shared state or a snapshot. Pass a value as an argument, bind configuration deliberately, or use a class with explicit state. See Lesson 04 for loop capture.

### Mistake 2: forgetting `nonlocal`

**Symptom:** `UnboundLocalError` when a nested function tries to increment an enclosing integer.  
**Cause:** assignment makes the name local unless `nonlocal` or `global` says otherwise.  
**Fix:** declare `nonlocal` for an enclosing function binding. See Lesson 04 for the full name-binding rules.

### Mistake 3: confusing a shared object with a shared binding

**Symptom:** two closures appear to affect the same list or dictionary.  
**Cause:** they share a reference to the same mutable object, or share the same cell.  
**Fix:** identify whether the issue is rebinding or mutation; choose copying, immutable data, separate factory calls, or explicit synchronization according to the intended ownership model.

### Mistake 4: over-inspecting cells in application code

**Symptom:** production behavior depends on `fn.__closure__[0]`.  
**Cause:** implementation details were mistaken for a public API.  
**Fix:** expose configuration explicitly or test behavior. Use cell inspection as a debugging aid.

### Mistake 5: hiding too much state in a closure

**Symptom:** maintainers need several helper functions to inspect, reset, or serialize one closure's state.  
**Cause:** a closure is being used as a substitute for a domain object.  
**Fix:** consider a class with named fields and methods.

### Mistake 6: assuming memoization is always safe

**Symptom:** stale data, growing memory, duplicate computation, or `TypeError` for unhashable inputs.  
**Cause:** cache lifetime and key semantics were not designed.  
**Fix:** specify key identity, invalidation, bounds, failure policy, and concurrency behavior; use `functools.cache` or `lru_cache` when their semantics fit.

### Mistake 7: assuming a closure is picklable

**Symptom:** multiprocessing fails to serialize a nested callback.  
**Cause:** standard pickle generally expects importable top-level functions and does not serialize arbitrary closure environments.  
**Fix:** use a top-level function plus arguments, `partial`, or a picklable callable class.

### A practical debugging sequence

1. Identify the exact function object being called.
2. Inspect `fn.__code__.co_freevars` and `fn.__closure__` if it is a Python function.
3. Pair each free-variable name with the corresponding cell; inspect contents only when safe.
4. Determine whether the bug is a rebinding, mutable-object mutation, shared state, lifetime, or cache-policy issue.
5. Reproduce with the smallest test that calls the returned function more than once.
6. Add a behavioral regression test; avoid hard-coding cell indices or bytecode unless testing runtime internals is the explicit goal.

---

## 16. Exercises

Try these before reading the solutions.

### Exercise A — trace LEGB

Given the code below, identify where each name is resolved and predict the output.

```python
mode = "module"

def make_reader(mode: str):
    label = "outer"
    def read(value: str) -> str:
        return f"{mode}|{label}|{value}|{len(value)}"
    return read

read = make_reader("configured")
print(read("abc"))
```

### Exercise B — prove independence

Implement `counter_factory(start=0)`. Test two counters interleaved and show that calling one does not advance the other.

### Exercise C — validator factory

Implement `make_length_validator(min_length, max_length)`. Reject invalid ranges at factory creation. Raise `ValueError` when a value is outside the inclusive range; return the original string when valid.

### Exercise D — once semantics

Implement `once(fn)` so that it caches the first successful result, ignores later arguments, and retries if the first invocation raises. Write tests for all three requirements. State whether your implementation is thread-safe.

### Exercise E — memoize policy

Implement `memoize(fn)` for hashable arguments. Test repeated calls, exceptions, and unhashable arguments. Explain why a cache with no bound can be dangerous in a long-running ingestion worker.

### Exercise F — inspect a closure

Create `make_multiplier(9)`, inspect `co_freevars`, and map each free-variable name to its cell contents. Explain why asserting `__closure__[0]` is `9` without checking the corresponding name is brittle.

### Exercise G — class or closure?

A rate limiter needs `allow()`, `reset()`, `snapshot()`, metrics, and a serializable configuration. Recommend a closure or class and justify the trade-offs.

### Exercise H — comprehension scope

Explain the difference between (a) the iteration variable leaking into the surrounding scope and (b) lambdas in a comprehension referring to the same captured binding. Link the second behavior to Lesson 04 without turning this answer into a late-binding tutorial.

### Exercise I — callback lifetime

A long-lived event dispatcher stores a callback returned by a factory. The callback closes over a large DataFrame and a service instance. List two likely retention risks and three possible mitigations.

### Exercise J — deterministic time

Implement or adapt `rate_limited` with an injectable clock. Test the exact boundary where an event becomes old enough to leave the rolling window without using `sleep()`.

---

## 17. Exercise solutions

### Solution A

Output:

```text
configured|outer|abc|3
```

Inside `read`, `mode` resolves to the `mode` parameter of `make_reader` (enclosing), `label` resolves to the local of `make_reader` (enclosing), `value` is local, and `len` is built-in. The module-level `mode` is shadowed by the parameter binding captured by this closure.

### Solution B

```python
def counter_factory(start: int = 0):
    count = start
    def increment() -> int:
        nonlocal count
        count += 1
        return count
    return increment

left = counter_factory()
right = counter_factory(20)
assert left() == 1
assert right() == 21
assert left() == 2
assert right() == 22
```

Each factory invocation creates a distinct enclosing binding and cell for `count`.

### Solution C

```python
def make_length_validator(min_length: int, max_length: int):
    if min_length < 0 or max_length < min_length:
        raise ValueError("invalid length range")
    def validate(value: str) -> str:
        if not min_length <= len(value) <= max_length:
            raise ValueError("length outside allowed range")
        return value
    return validate
```

The configuration is checked once; each call uses the captured bounds. The returned function's behavior is the best public test of the captured configuration.

### Solution D

Use the `once` implementation in Section 12.1. It caches successful results and retries after exceptions. The simple implementation is **not thread-safe** because the first-call check and wrapped invocation are not protected by a lock. If strict at-most-once invocation across threads is required, define lock and exception semantics explicitly; a lock alone also raises design questions about reentrant calls.

### Solution E

Use the implementation in Section 8.1 and the tests in Section 13. The dictionary retains both keys and results. In an unbounded stream with high-cardinality keys, the cache can grow for the entire worker lifetime. Use bounded caching, explicit invalidation, a lifecycle-scoped cache, or no cache if the memory/correctness trade-off is unfavorable.

### Solution F

```python
multiplier = make_multiplier(9)
names = multiplier.__code__.co_freevars
cells = multiplier.__closure__ or ()
print(dict(zip(names, (cell.cell_contents for cell in cells), strict=True)))
```

The name-to-cell pairing is the meaningful relationship. Cell ordering is related to the code object's free-variable ordering, but an unexplained numeric index is fragile if the function changes.

### Solution G

Prefer a class. Multiple public operations, snapshots, metrics, reset semantics, and serializable configuration make explicit named state valuable. A closure can implement the behavior, but returning several functions or adding side channels for inspection would make the API harder to maintain.

### Solution H

A comprehension's iteration name does not leak into the surrounding scope. But a nested function created inside that comprehension may close over the comprehension-local iteration binding; if the functions are called later, they can all observe that binding's final value. The first is a name-scope rule; the second is closure binding behavior and the late-binding topic of Lesson 04.

### Solution I

Risks: the dispatcher can keep the DataFrame alive through the closure; it can also keep the service instance and its object graph alive. Mitigations include unregistering the callback, capturing only small immutable configuration, passing data explicitly, using weak-reference patterns where appropriate, and measuring object retention.

### Solution J

Use an injected fake clock as in Section 14. Test at `t=0` and again at exactly `t=period`; the implementation expires entries when `now - oldest >= period`, so the boundary is inclusive for expiration. No sleep is needed.

---

## 18. Self-check questions

Answer without looking back, then review the explanations.

1. What does LEGB stand for, and which name does a closure use if a local variable shadows a global?
2. What is the difference between a free variable and a cell variable?
3. Does a closure snapshot an immutable value or retain access to a binding? What changes if the binding is rebound?
4. Why can two functions returned by one factory share state while two factory invocations remain independent?
5. What do `__closure__`, `co_freevars`, and `cell_contents` reveal? Why should tests usually avoid depending on their exact layout?
6. When is `functools.partial` a better choice than a custom closure?
7. Name two reasons to choose a class over a closure.
8. How can a callback accidentally keep a large DataFrame alive?
9. What did Python 3.12 change about comprehension implementation, and what scope behavior did it preserve?
10. Why do nested closures generally fail standard `pickle` serialization?
11. Why is a custom memoization closure not automatically safe for mutable external data or concurrent use?
12. What should tests prove about `once`, `memoize`, and `counter_factory`?

### Self-check answer key

1. Local, Enclosing, Global, Built-in. A local binding takes precedence over an enclosing or global name.
2. A free variable is used by a nested function but bound outside it; the corresponding local in the enclosing function is a cell variable when the compiler must expose it to nested code.
3. It retains access to the binding. Rebinding the name changes the object the cell refers to; mutating the captured object changes that object for all references to it.
4. Functions created in the same factory invocation can reference the same cell. Separate invocations create separate local bindings/cells.
5. They expose closure cell structure, free-variable names, and current cell contents. This is introspection, not the function's public behavioral contract; code changes and implementations may alter details.
6. When only some arguments need to be fixed and no additional logic/state is required. It is standard and often more picklable when its components are picklable.
7. Multiple related methods, explicit state inspection, clearer documentation/types, maintainability, or serialization requirements.
8. The closure retains a cell whose object reference points to the DataFrame; a long-lived callback retains that closure and therefore the DataFrame.
9. Python 3.12 inlined comprehensions for implementation efficiency under PEP 709. The iteration variable still does not leak into the surrounding scope; nested functions can still capture the comprehension's binding.
10. Standard pickle generally resolves functions by qualified module name rather than serializing arbitrary code and closure cells; nested functions are generally not importable by a stable top-level name.
11. Mutable external dependencies can make cached values stale; unbounded keys/results consume memory; concurrent misses can duplicate work, and synchronization semantics need to be designed.
12. Observable outputs/errors, independence of factory instances, configured behavior, state transitions, and the documented failure/cache policy. Add concurrency tests only if thread-safety is part of the contract.

---

## 19. Completion checklist

- [ ] I can trace a name through LEGB and explain shadowing.
- [ ] I can define a closure without confusing it with a function that merely calls another function.
- [ ] I can explain free variables, cell variables, and closure cells.
- [ ] I understand that a closure retains access to a binding rather than freezing the bound value.
- [ ] I can create independent counters and configured validators.
- [ ] I can inspect a closure for debugging and explain why introspection is not the public API.
- [ ] I can choose between closure, `partial`, and class using maintainability and lifecycle criteria.
- [ ] I can describe closure behavior in decorators and memoization without expanding those topics into separate courses.
- [ ] I can identify memory-retention risks in callbacks and captured data objects.
- [ ] I can use `dis` to explore cell-related bytecode without relying on a fixed listing.
- [ ] I can explain Python 3.12+ comprehension scope and distinguish it from late binding.
- [ ] I can state the limitations of `once`, a custom `memoize`, and a stateful closure under concurrency and pickling.
- [ ] I have run the pytest examples and can explain what each test protects.

## Summary

Closures let functions carry access to selected enclosing bindings beyond the outer call. The compiler identifies captured names; runtime cells preserve the bindings; nested functions read or rebind those cells according to normal Python scope rules. This makes closures useful for compact factories, callbacks, decorators, and private state—but the same implicit references affect mutability, lifetime, testing, concurrency, and serialization.

Use closures when their small API makes behavior clearer. Use `functools.partial` for straightforward argument binding and a class when state and operations need to be explicit. Inspect closure internals for learning and debugging, test public behavior for correctness, and treat caches and callback lifetimes as design decisions rather than incidental implementation details.

## Related lessons

- **Module 1.3, lesson 05:** scope and lifetime foundations.
- **Module 1.3, lesson 06:** pure functions and side effects.
- **Module 1.7:** pytest, debugging, and test design.
- **Module 1.9, lessons 02 and 09:** decorators and `functools`.
- **Module 1.19, lessons 01–02:** compiler/symbol-table and bytecode exploration.
- **Lesson 02 — Lambda expressions and when not to use them:** function expressions and callback choices.
- **Lesson 04 — Nonlocal and late-binding pitfalls:** detailed assignment rules, `UnboundLocalError`, and loop-capture remedies.
- **Lesson 06 — Callable objects with `__call__`:** an alternative when a stateful callable deserves a named object.
