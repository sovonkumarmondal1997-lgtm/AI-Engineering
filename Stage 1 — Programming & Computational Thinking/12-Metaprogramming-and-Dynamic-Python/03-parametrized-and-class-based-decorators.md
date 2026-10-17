# Parameterized and Class-Based Decorators

> **Roadmap location:** Stage 1 — Programming & Computational Thinking → `12-Metaprogramming-and-Dynamic-Python/03-parametrized-and-class-based-decorators.md`
>
> **Compatibility baseline:** Python 3.12+. The examples use standard-library features available in Python 3.12 unless a version note says otherwise.
>
> **Scope boundary:** This lesson builds on ordinary function decorators introduced earlier. It covers parameterized and class-based decorators, method binding, async/generator behavior, typing, and production concerns. Class decorators and class factories belong to Lesson 04; `__init_subclass__`, metaclasses, and AST/code generation are later lessons.

## Learning outcomes

By the end, you should be able to:

- Explain how Python applies a decorator and why `@retry(times=3)` has three nested call layers.
- Build function decorators and decorator factories without losing return values, exceptions, or metadata.
- Preserve introspection metadata with `functools.wraps`, understand `__wrapped__`, and distinguish an apparent signature from actual argument validation.
- Implement callable-instance decorators with `__init__`, `__call__`, and `functools.update_wrapper`.
- Make class-based decorators work on instance methods using descriptor binding.
- Explain stacking order and the differences between wrapping and registration-only decorators.
- Decorate synchronous functions, coroutines, and generator functions without accidentally changing their execution model.
- Type decorators with `ParamSpec`, `TypeVar`, and `Concatenate`.
- Identify state, concurrency, retry-safety, logging, caching, and signature-modification trade-offs.
- Test behavior and metadata instead of judging a decorator by its appearance.

## 1. Prerequisites and mental model

### 1.1 What is a decorator?

A decorator is a callable that receives an object—usually a function—and returns an object that replaces it at the decorated name. The returned object is often a wrapper that adds behavior before or after calling the original function.

```python
def announce(fn):
    def wrapper(*args, **kwargs):
        print("calling")
        result = fn(*args, **kwargs)
        print("finished")
        return result
    return wrapper

def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b

add = announce(add)  # same transformation as @announce above add's definition
print(add(2, 3))
```

Output:

```text
calling
finished
5
```

The `@announce` syntax is syntactic convenience for rebinding the function name to the decorator's return value. Decoration normally occurs when the `def` statement executes, typically during module import—not every time the decorated function is called.

A decorator does not have to return a function, but a replacement must support the operations callers expect. Returning `None`, for example, would bind the name to `None` and make later calls fail.

### 1.2 The three-level structure of `@retry(times=3)`

```python
@retry(times=3)
def fetch_record(record_id: str) -> dict[str, str]:
    ...
```

Conceptually, Python evaluates this as:

```python
decorator_factory_result = retry(times=3)  # layer 1: configuration
decorated_function = decorator_factory_result(fetch_record)  # layer 2: decoration
fetch_record = decorated_function  # layer 3: rebinding; calls later enter its wrapper
```

The three layers have different responsibilities:

1. **Factory `retry(times=3)`** receives configuration and returns a decorator. It runs at decoration time.
2. **Decorator `decorator(fn)`** receives the original function and returns a replacement. It also runs at decoration time.
3. **Wrapper `wrapper(*args, **kwargs)`** receives each call's arguments and runs at call time.

The factory's closure retains `times` (and other configuration) for future calls. The wrapper's closure retains `fn`. These are separate captured values; they are not magic global variables.

### 1.3 Closures and captured state

A closure is a function together with access to variables from its enclosing lexical scope. Captured values remain available while the inner function is reachable.

```python
def make_multiplier(factor: int):
    def multiply(value: int) -> int:
        return factor * value
    return multiply

triple = make_multiplier(3)
print(triple(7))  # 21
```

A decorator factory uses the same mechanism to retain options. Be deliberate about whether state belongs to the factory, the decorated function, each invocation, or a shared decorator object. Those choices affect re-entrancy and thread safety.

### 1.4 What should a decorator preserve?

Unless the contract explicitly says otherwise, a wrapper should preserve:

- the original return value;
- exceptions (same exception type and traceback propagation; do not silently suppress them);
- positional and keyword argument forwarding;
- function metadata used by debugging, documentation, test frameworks, and web frameworks;
- the execution model: sync stays sync, coroutine stays coroutine, generator stays generator.

Decorators can intentionally alter these semantics, but such changes must be documented and tested.

## 2. Basic function decorators

### 2.1 A simple `timed` decorator

```python
from collections.abc import Callable
from functools import wraps
from time import perf_counter
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def timed(fn: Callable[P, R]) -> Callable[P, R]:
    @wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        started = perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            elapsed = perf_counter() - started
            print(f"{fn.__qualname__} took {elapsed:.6f}s")
    return wrapper
```

`perf_counter()` is a monotonic high-resolution clock suitable for elapsed durations. `finally` ensures timing is emitted even if the wrapped function raises. The wrapper returns the exact result when the call succeeds and does not catch or replace exceptions.

The `print` is for a minimal demonstration. Production observability should normally use an injected logger/metrics interface and avoid writing sensitive arguments or return values.

### 2.2 Decorators must return results and propagate failures

A common defect is forgetting `return fn(*args, **kwargs)`. The decorated function then returns `None` even if the original returned a value. Another defect is catching `Exception` only to log and continue, which can turn a failure into a misleading success.

```python
def safe_wrapper(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper
```

This wrapper adds no behavior; it illustrates the correct forwarding baseline. A useful decorator should add a clearly defined policy beyond this baseline.

### 2.3 When a function wrapper is the right tool

Use a function-based wrapper when behavior is naturally expressed around a call: timing, validation, retries, authorization checks, tracing, or metrics. Python functions already implement the descriptor protocol, so a wrapper function assigned to a class binds as a method automatically. A class-based decorator is not automatically better just because it can hold state.

## 3. Parameterized decorators

### 3.1 A bounded retry decorator

A retry policy must define its semantics precisely. In this lesson, `times` means **total calls to the wrapped function**, including the first call. Thus `times=3` allows at most three calls and at most two sleeps. Only the explicitly listed exception types are retried. The default is deliberately narrow (`TimeoutError`), rather than retrying every `Exception`. When the last attempt fails, the final exception propagates unchanged. Invalid configuration is rejected when the decorator is created.

```python
from collections.abc import Callable
import math
from functools import wraps
from time import sleep
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def retry(
    times: int = 3,
    *,
    delay: float = 0.1,
    retry_on: tuple[type[Exception], ...] = (TimeoutError,),
    backoff: float = 1.0,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Retry a synchronous function with bounded attempts.

    `times` counts total invocations, not retries after the first call.
    `delay` is the initial wait before a retry; each later wait is multiplied
    by `backoff`. Only exceptions matching `retry_on` trigger a retry.
    """
    if isinstance(times, bool) or not isinstance(times, int) or times < 1:
        raise ValueError("times must be an integer >= 1")
    if isinstance(delay, bool) or not isinstance(delay, (int, float)) or not math.isfinite(delay) or delay < 0:
        raise ValueError("delay must be a finite number >= 0")
    if isinstance(backoff, bool) or not isinstance(backoff, (int, float)) or not math.isfinite(backoff) or backoff < 1:
        raise ValueError("backoff must be a finite number >= 1")
    if not isinstance(retry_on, tuple) or not retry_on:
        raise ValueError("retry_on must be a non-empty tuple of exception classes")
    if any(not isinstance(exc, type) or not issubclass(exc, Exception) for exc in retry_on):
        raise TypeError("retry_on entries must be Exception subclasses")

    def decorate(fn: Callable[P, R]) -> Callable[P, R]:
        @wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            wait = delay
            for attempt_number in range(1, times + 1):
                try:
                    return fn(*args, **kwargs)
                except retry_on:
                    if attempt_number == times:
                        raise
                    if wait:
                        sleep(wait)
                    wait *= backoff
            raise AssertionError("unreachable")
        return wrapper
    return decorate
```

Example:

```python
@retry(times=3, delay=0.05, backoff=2, retry_on=(TimeoutError,))
def read_from_service() -> str:
    ...
```

If calls fail with `TimeoutError`, waits are 0.05 seconds and then 0.10 seconds before attempts two and three. If the first call succeeds, there is no sleep. If a non-listed exception occurs, it propagates immediately. If all three calls raise `TimeoutError`, the third exception propagates.

**Production safety:** Retrying is safe only when repeating the operation is safe or the remote system provides an idempotency mechanism. A timeout may occur after a payment, write, or message publish has already committed; retrying can duplicate side effects. Prefer narrow retry exception classes, exponential backoff, jitter, an overall deadline, and server-supported idempotency keys for distributed operations. This small decorator does not implement jitter, cancellation, deadlines, or distributed coordination.

The implementation is synchronous. It uses `time.sleep`, so it must not be used directly to retry an `async def` function; see Section 7.

### 3.2 An optional-argument decorator

A decorator can support both forms:

```python
@trace
def one(): ...

@trace(label="database")
def two(): ...
```

One common pattern uses `fn=None` to distinguish the bare form from the configured form:

```python
from functools import wraps
from typing import Any, Callable, cast

def trace(fn: Callable[..., Any] | None = None, *, label: str = "call"):
    def decorate(target: Callable[..., Any]):
        @wraps(target)
        def wrapper(*args: Any, **kwargs: Any):
            print(f"{label}: {target.__qualname__}")
            return target(*args, **kwargs)
        return wrapper

    if fn is None:
        return decorate
    return decorate(fn)
```

`@trace` passes the function as `fn`; `@trace(label="database")` first calls `trace` with no function and receives `decorate`. This example uses `Any` to keep the optional form approachable; more advanced overloads can improve static typing when both forms are part of a public library API.

Avoid ambiguous signatures that interpret a function argument as configuration accidentally. Keyword-only configuration options are often easier to reason about.

### 3.3 Factory, decorator, and wrapper: compare the objects

| Layer | Example | When it runs | Receives |
|---|---|---|---|
| Factory | `retry(times=3)` | Decoration setup | Configuration |
| Decorator | `decorate(fn)` | Function definition executes | Original function |
| Wrapper | `wrapper(*args, **kwargs)` | Each function call | Call arguments |

Keeping these roles distinct prevents mistakes such as validating call-specific values at import time or trying to access a function before the decorator receives it.

## 4. Metadata and signature preservation

### 4.1 `functools.wraps` and `__wrapped__`

A wrapper is a new function object. Without help, its `__name__`, docstring, annotations, and other metadata describe the wrapper, not the original function. `functools.wraps(fn)` is a convenience decorator built on `functools.update_wrapper`; it copies standard metadata and sets `__wrapped__` to the wrapped callable.

```python
from functools import wraps
from inspect import signature

def logged(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        print(f"calling {fn.__name__}")
        return fn(*args, **kwargs)
    return wrapper

@logged
def divide(numerator: float, denominator: float = 1.0) -> float:
    """Divide numerator by denominator."""
    return numerator / denominator

print(divide.__name__)                    # divide
print(divide.__doc__)                     # Divide numerator by denominator.
print(signature(divide))                  # (numerator: float, denominator: float = 1.0) -> float
print(divide.__wrapped__(8, 2))            # 4.0 (calls the original directly)
```

`inspect.signature()` follows `__wrapped__` by default, so it usually displays the original signature even though the wrapper's actual code accepts `*args, **kwargs`. This is an introspection convention, not a rewrite of the wrapper's bytecode or runtime argument binder. `divide(8)` is accepted by the wrapper and then by the original function; `divide(8, unexpected=True)` enters the wrapper and fails when the original function receives the unexpected keyword.

`__wrapped__` is useful for introspection, testing, and tools that need to unwrap a chain. It is not a security boundary: callers can deliberately invoke it, and framework behavior varies. Do not use it to bypass authorization or validation.

### 4.2 The apparent signature versus actual calling behavior

```python
from inspect import signature

def accepts_anything(fn):
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper

def greeting(name: str, *, excited: bool = False) -> str:
    return f"Hello, {name}{'!' if excited else '.'}"

wrapped = accepts_anything(greeting)
print(signature(wrapped))  # (*args, **kwargs), because wraps was not used
```

Using `@wraps(greeting)` makes introspection show `(name: str, *, excited: bool = False) -> str`. It does **not** make the wrapper's Python-level signature itself explicit. Runtime argument validation still occurs when the wrapper calls `greeting`. This distinction matters for documentation generators, dependency injection, CLI frameworks, web frameworks, and static type checkers.

### 4.3 `functools.update_wrapper` for callable objects

```python
from functools import update_wrapper

class CallCounter:
    def __init__(self, fn):
        self.fn = fn
        self.calls = 0
        update_wrapper(self, fn)

    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.fn(*args, **kwargs)
```

`update_wrapper(self, fn)` copies metadata onto `self` and sets `self.__wrapped__`. It does not automatically create a Python function with the original signature, nor does it solve descriptor binding for methods. A callable instance's `inspect.signature` behavior depends on its metadata and call interface; test the framework-facing behavior you promise.

## 5. Class-based decorators

### 5.1 `__init__` receives the function; `__call__` handles invocations

```python
from functools import update_wrapper
from typing import Any

class CountCalls:
    """Count calls to one decorated callable.

    The counter is shared by all calls to this decorator instance.
    """
    def __init__(self, fn):
        update_wrapper(self, fn)
        # Assign internal state after metadata copying so a same-named custom
        # attribute on fn cannot overwrite the decorator's state.
        self.fn = fn
        self.calls = 0

    def __call__(self, *args: Any, **kwargs: Any):
        self.calls += 1
        return self.fn(*args, **kwargs)
```

Usage:

```python
@CountCalls
def square(n: int) -> int:
    return n * n

assert square(3) == 9
assert square(4) == 16
assert square.calls == 2
```

The class is instantiated at decoration time, with the original function as `fn`. Later, `square(3)` invokes the decorator object's `__call__`. The state belongs to this decorator instance, so each separately decorated function normally gets its own counter.

### 5.2 Trade-offs of callable instances

**Advantages**
- State and configuration have an explicit home.
- The implementation can be organized into methods.
- Instances can expose controls such as `reset()` or statistics.

**Costs and hazards**
- A shared instance is mutable state. Concurrent calls can race on compound operations, and recursive calls can interact with state.
- A callable object used as a method decorator must implement the descriptor behavior needed for binding.
- Introspection and static typing may be less straightforward than with a function wrapper.
- Storing the original function on the instance can create reference cycles in more elaborate designs; Python's cyclic garbage collector usually handles ordinary cycles, but resource cleanup should not rely on collection timing.

A simple integer increment is not a universal cross-interpreter or free-threaded atomicity guarantee. If accurate concurrent counts matter, protect updates with a lock or use a concurrency-safe metrics backend. If calls can re-enter and the state represents “currently running,” use a per-call or context-local design rather than a single boolean.

### 5.3 A lock-protected counter

```python
from functools import update_wrapper
from threading import Lock
from typing import Any

class LockedCountCalls:
    def __init__(self, fn):
        update_wrapper(self, fn)
        self.fn = fn
        self.calls = 0
        self._lock = Lock()

    def __call__(self, *args: Any, **kwargs: Any):
        with self._lock:
            self.calls += 1
        # Do not hold the lock while executing arbitrary user code.
        return self.fn(*args, **kwargs)
```

The lock protects the counter increment, not the wrapped function. This is deliberate: holding a decorator lock while calling arbitrary code can serialize unrelated calls or deadlock if the wrapped function re-enters the decorated callable. The count means “number of calls that entered the wrapper,” including calls that later raise.

## 6. Methods, descriptors, and decorator stacking

### 6.1 Why function wrappers bind methods automatically

Functions stored on a class implement the descriptor protocol. When a function is accessed through an instance, its descriptor creates a bound method that supplies the instance as the first argument. A function-based wrapper is still a function, so this binding normally continues to work:

```python
from functools import wraps

def announce_call(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper

class Greeter:
    @announce_call
    def greet(self, name: str) -> str:
        return f"Hello, {name}"

assert Greeter().greet("Ada") == "Hello, Ada"
```

### 6.2 Class-based method decorators need descriptor binding

A callable instance does not automatically behave like a function descriptor. If it is assigned to a class attribute, `instance.method` returns that callable object without automatically inserting `instance`. Implement `__get__` to bind the instance when needed:

```python
from functools import partial, update_wrapper
from types import MethodType
from typing import Any

class CountMethodCalls:
    def __init__(self, fn):
        self.fn = fn
        self.calls = 0
        update_wrapper(self, fn)

    def __call__(self, *args: Any, **kwargs: Any):
        self.calls += 1
        return self.fn(*args, **kwargs)

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return partial(self.__call__, instance)
```

Usage:

```python
class Calculator:
    @CountMethodCalls
    def add(self, left: int, right: int) -> int:
        return left + right

calc = Calculator()
decorator_object = Calculator.add
assert calc.add(2, 5) == 7
assert calc.add(1, 1) == 2
assert decorator_object.calls == 2
```

`partial(self.__call__, instance)` produces a callable that supplies the instance as the first argument to `__call__`, which then forwards it to the original unbound function. `functools.partial` itself is not a descriptor that binds arbitrary class attributes like a Python function does; here it is returned by the decorator's `__get__` after binding has been decided.

An equivalent approach can use `MethodType`, but be careful about which callable is being bound. The core requirement is to pass the instance exactly once. Test class access (`Calculator.add`), instance access (`calc.add`), inheritance, and introspection separately if these are public APIs.

**Important limitation:** This minimal descriptor decorator is designed for ordinary instance methods. It does not automatically preserve `staticmethod` or `classmethod` semantics if decorator order is changed. For example, `@CountMethodCalls` outside `@classmethod` receives a `classmethod` descriptor rather than a plain function. Decorator ordering matters; build and test explicit support for these descriptors if required. Do not claim universal compatibility.

### 6.3 Stacking decorators: bottom-up application

```python
@outer
@inner
def task():
    ...
```

is equivalent to:

```python
task = outer(inner(task))
```

The closest decorator to `def` is applied first; calls then enter the outer wrapper first. For example:

```python
def label(name):
    def decorate(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            print(f"{name}:before")
            try:
                return fn(*args, **kwargs)
            finally:
                print(f"{name}:after")
        return wrapper
    return decorate

@label("outer")
@label("inner")
def work():
    print("work")

work()
```

Output:

```text
outer:before
inner:before
work
inner:after
outer:after
```

Stack order is part of the program's behavior. Swapping authorization, caching, logging, and retry decorators can change whether denied calls are logged, whether cache hits are retried, and how many times metrics are recorded. Write down the intended policy and test the order.

### 6.4 Registration-only decorators versus wrapping decorators

A registration decorator records a function somewhere and returns the original function unchanged:

```python
ROUTES = {}

def route(path: str):
    def decorate(fn):
        if path in ROUTES:
            raise ValueError(f"duplicate route: {path}")
        ROUTES[path] = fn
        return fn  # registration only; do not replace function
    return decorate

@route("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

A wrapping decorator returns a replacement callable. Registration-only decorators are useful when registration is the only required behavior and preserving identity matters. Wrapping decorators are appropriate when every call needs additional behavior. A registration-only decorator still has an import-time side effect; import order, duplicate registration, and test isolation must be considered.

## 7. Async-aware and advanced decorators

### 7.1 A synchronous wrapper does not await a coroutine

Calling an `async def` function returns a coroutine object. A normal wrapper that calls it and returns the result returns that coroutine object; it does not await it. Timing only the wrapper's call measures coroutine creation, not the asynchronous work.

A decorator can inspect the target and create an async wrapper for coroutine functions:

```python
import inspect
from functools import wraps
from time import perf_counter
from typing import Any, Callable

def timed_auto(fn: Callable[..., Any]):
    if inspect.iscoroutinefunction(fn):
        @wraps(fn)
        async def async_wrapper(*args, **kwargs):
            started = perf_counter()
            try:
                return await fn(*args, **kwargs)
            finally:
                elapsed = perf_counter() - started
                print(f"{fn.__qualname__} took {elapsed:.6f}s")
        return async_wrapper

    @wraps(fn)
    def sync_wrapper(*args, **kwargs):
        started = perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            elapsed = perf_counter() - started
            print(f"{fn.__qualname__} took {elapsed:.6f}s")
    return sync_wrapper
```

The async branch measures the awaited operation, including time spent suspended awaiting I/O. It propagates exceptions and cancellation because it does not suppress them. `inspect.iscoroutinefunction` identifies ordinary coroutine functions and many wrapped cases, but cannot infer every callable that returns an awaitable. Decorators should document whether they support coroutine functions only or arbitrary awaitable-returning callables.

### 7.2 Async retry with explicit cancellation policy

For async code, use `asyncio.sleep` rather than blocking `time.sleep`. Cancellation should normally propagate immediately; `asyncio.CancelledError` is not a normal transient error to retry. This example retries only configured ordinary exceptions and does not catch cancellation:

```python
import asyncio
import math
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def async_retry(
    attempts: int = 3,
    *,
    delay: float = 0.1,
    retry_on: tuple[type[Exception], ...] = (TimeoutError,),
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    if isinstance(attempts, bool) or not isinstance(attempts, int) or attempts < 1:
        raise ValueError("attempts must be an integer >= 1")
    if isinstance(delay, bool) or not isinstance(delay, (int, float)) or not math.isfinite(delay) or delay < 0:
        raise ValueError("delay must be a finite number >= 0")
    if not isinstance(retry_on, tuple) or not retry_on or any(
        not isinstance(exc, type) or not issubclass(exc, Exception)
        for exc in retry_on
    ):
        raise ValueError("retry_on must contain Exception subclasses")

    def decorate(fn: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @wraps(fn)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for attempt_number in range(1, attempts + 1):
                try:
                    return await fn(*args, **kwargs)
                except retry_on:
                    if attempt_number == attempts:
                        raise
                    if delay:
                        await asyncio.sleep(delay * attempt_number)
            raise AssertionError("unreachable")
        return wrapper
    return decorate
```

This uses a linear delay (`delay * attempt_number`) and total attempts semantics. It is a separate async decorator rather than trying to make one wrapper guess how to await arbitrary return values. Cancellation and task deadlines should be handled by the caller's structured concurrency policy. Do not retry a non-idempotent coroutine without idempotency protection.

### 7.3 Generator functions and generator-based context managers

A generator function's call returns a generator object; its body begins when the generator is iterated. A generic wrapper that returns `fn(...)` preserves the generator object, but timing that wrapper measures only generator creation. To time iteration, the wrapper must itself implement generator behavior and define how it handles exceptions, `send`, `throw`, and `close`; this is more complex than timing a normal function.

For resource management, prefer `contextlib.contextmanager` for synchronous generators and `contextlib.asynccontextmanager` for asynchronous generators. These utilities have specific protocols for entry, exit, exception injection, and cleanup. Do not decorate a generator function with a decorator that assumes its result is the final materialized value.

Example of a context-manager factory:

```python
from contextlib import contextmanager
from time import perf_counter

@contextmanager
def timed_block(label: str):
    started = perf_counter()
    try:
        yield
    finally:
        print(f"{label} took {perf_counter() - started:.6f}s")

with timed_block("load"):
    total = sum(range(1000))
```

This is a context manager, not a function decorator. It is often the clearer abstraction when the desired boundary is a block of statements rather than a single function call.

For a **synchronous generator function**, a wrapper can time iteration by itself being a generator and delegating with `yield from`:

```python
import inspect
from functools import wraps
from time import perf_counter
from typing import Any, Callable


def timed_generator(fn: Callable[..., Any]) -> Callable[..., Any]:
    if not inspect.isgeneratorfunction(fn):
        raise TypeError("timed_generator requires a generator function")

    @wraps(fn)
    def wrapper(*args: Any, **kwargs: Any):
        started = perf_counter()
        try:
            yield from fn(*args, **kwargs)
        finally:
            print(f"{fn.__qualname__} iteration took {perf_counter() - started:.6f}s")
    return wrapper
```

Because `yield from` delegates iteration, values and generator protocol operations such as `send`, `throw`, and `close` are forwarded according to generator delegation semantics. The timer starts when iteration begins, not when the generator object is created. This example is synchronous and does not handle async generators; for those, write an async-generator wrapper with `async for` and explicitly decide how to preserve `aclose`/cancellation behavior.

### 7.4 Coroutine functions versus awaitable-returning callables

`inspect.iscoroutinefunction(fn)` asks about the callable's definition/wrapping metadata; it does not prove every call result is awaitable. A synchronous function may return a custom awaitable, and a callable object may implement `__call__` with async behavior. If an API must support all awaitables, specify that contract and inspect/await the result carefully; doing so can change a synchronous function's return semantics. Prefer separate sync and async decorator APIs when the distinction is important.

## 8. Typing and production concerns

### 8.1 `ParamSpec` and `TypeVar`

`ParamSpec` captures the parameter types of a callable, and `TypeVar` captures its return type. This lets a function decorator express “same parameters and same return type” instead of degrading to `Callable[..., Any]`.

```python
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def identity_decorator(fn: Callable[P, R]) -> Callable[P, R]:
    @wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return fn(*args, **kwargs)
    return wrapper
```

This annotation is a static typing contract. Runtime Python does not enforce it. A type checker may still have limitations around dynamically generated callable objects, descriptor decorators, overloads, and signature-changing wrappers.

### 8.2 `Concatenate` for injecting an argument

`Concatenate` models a decorator that adds or removes a leading parameter from a callable's type. For example, a decorator can inject a `RequestContext` so the caller supplies the remaining parameters:

```python
from collections.abc import Callable
from functools import wraps
from typing import Concatenate, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

class RequestContext:
    def __init__(self, request_id: str) -> None:
        self.request_id = request_id

def with_context(
    fn: Callable[Concatenate[RequestContext, P], R],
) -> Callable[P, R]:
    @wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        context = RequestContext("request-123")
        return fn(context, *args, **kwargs)
    return wrapper

@with_context
def process(context: RequestContext, item_id: int) -> str:
    return f"{context.request_id}:{item_id}"

assert process(7) == "request-123:7"
```

The example uses a fixed context for teaching only; a production implementation should obtain context from a request boundary or dependency-injection mechanism. `@wraps` still copies the original function metadata, so `inspect.signature(process)` may show the injected parameter even though callers do not provide it. If the public introspection signature must reflect the changed API, set a carefully constructed `__signature__` and test it; typing and runtime introspection are separate systems.

### 8.3 Typing class-based decorators

Callable objects can be typed with `Protocol` or an explicit `__call__`, but preserving an arbitrary callable's exact parameter list in a generic class decorator is more difficult than for a function wrapper. A basic, honest contract is:

```python
from collections.abc import Callable
from functools import update_wrapper
from typing import Generic, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

class Counted(Generic[P, R]):
    def __init__(self, fn: Callable[P, R]) -> None:
        self.fn = fn
        self.calls = 0
        update_wrapper(self, fn)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        self.calls += 1
        return self.fn(*args, **kwargs)
```

The generic annotations communicate the intended call contract to compatible type checkers. Descriptor binding for methods introduces additional complexity because `__get__` has a different return type for class and instance access. For public library APIs, verify the chosen design with the project's actual type checker and Python version. Avoid promising type precision that has not been checked.

### 8.4 Signature modification with `__signature__`

`functools.wraps` preserves metadata and usually makes `inspect.signature` follow `__wrapped__`; it does not change the wrapper's actual argument binder. Frameworks sometimes need a custom public signature for dependency injection or CLI generation.

```python
from functools import wraps
from inspect import Parameter, Signature, signature

def expose_only_name(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    wrapper.__signature__ = Signature([
        Parameter("name", kind=Parameter.POSITIONAL_OR_KEYWORD)
    ])
    return wrapper

@expose_only_name
def internal(name: str, secret: str = "hidden") -> str:
    return f"{name}:{secret}"

print(signature(internal))  # (name)
print(internal("Ada"))      # Ada:hidden
```

The custom signature is a metadata contract for introspection consumers. It does not enforce that callers pass only `name`; the wrapper still accepts arbitrary arguments and forwards them. Here `internal("Ada", "x")` still succeeds. If a framework relies on the signature for validation, ensure the wrapper itself enforces the same contract. `__signature__` is an introspection convention used by tools, not a universal runtime validation mechanism.

### 8.5 Stateful decorators: re-entrancy and thread safety

Before adding state, answer:

- Is the state per decorated function, per instance, per call, per thread, or per async task?
- Can the wrapped function call itself recursively?
- Can concurrent threads/tasks invoke the same wrapper?
- What does a counter or cache mean when calls overlap?
- Is state cleared on exceptions and cancellation?
- Is a lock required, and what exactly does it protect?

A single mutable flag such as `self.in_progress = True` is usually wrong for recursive or concurrent calls. A lock around the entire wrapped function may serialize all callers and can deadlock on re-entry if it is not re-entrant. Prefer minimal critical sections, local variables for per-call state, and `contextvars` when state must follow an asynchronous task. `threading.local()` is thread-local, not task-local.

### 8.6 Cache design and invalidation

`functools.cache` and `functools.lru_cache` are often better than a home-grown cache. Their keys are based on call arguments; arguments must be hashable. A cache does not automatically understand mutation of external state, authorization changes, database updates, or time-sensitive results. Decide whether cache entries expire, how they are invalidated, how errors are treated, and whether callers may mutate returned objects.

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def normalize_code(code: str) -> str:
    return code.strip().upper()
```

This pure transformation is a reasonable cache candidate. Caching a function that reads a changing database without an invalidation strategy is not. Since cache keys must be hashable, calling an `@lru_cache`-decorated function with a list or dictionary argument raises `TypeError`; normalize mutable inputs to an immutable key (for example, a tuple of validated values) or do not cache that API. Decorator stacking also matters: `@lru_cache` outside a retry wrapper can cache a successful result; placing retry outside a cache may repeatedly call a cache that immediately re-raises a cached exception only if the selected cache implementation caches exceptions (the standard `lru_cache` does not cache raised exceptions).

### 8.7 Observability with structured logging

For production timing, use a logger rather than `print`, and log stable metadata rather than secrets:

```python
import logging
from functools import wraps
from time import perf_counter
from typing import Callable, Any

logger = logging.getLogger(__name__)

def observe(fn: Callable[..., Any]):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        started = perf_counter()
        try:
            result = fn(*args, **kwargs)
        except Exception:
            logger.exception(
                "operation_failed",
                extra={"operation": fn.__qualname__},
            )
            raise
        else:
            logger.info(
                "operation_succeeded",
                extra={
                    "operation": fn.__qualname__,
                    "duration_seconds": perf_counter() - started,
                },
            )
            return result
    return wrapper
```

The logger's `extra` values populate record attributes; the formatter/handler determines the final structured representation. `logger.exception` includes exception information and should be used inside an exception handler. This synchronous example does not measure async execution correctly; combine the same logging policy with an `async def` wrapper for coroutine functions. Avoid logging raw arguments, credentials, tokens, personal data, or large payloads. For distributed tracing, use the organization's tracing library and propagate context rather than inventing a local trace protocol.

### 8.8 Generator, async, and context-manager compatibility checklist

| Target | What calling it returns | Wrapper must do | Common mistake |
|---|---|---|---|
| Normal `def` | Result | Call and return result | Forget `return` |
| `async def` | Coroutine | `await` inside an async wrapper to measure execution | Time coroutine creation only |
| Generator `def` | Generator object | Preserve or explicitly wrap iteration protocol | Measure only generator creation |
| Async generator `async def` with `yield` | Async generator object | Preserve async iteration semantics | Treat it as an ordinary coroutine |
| Context manager | Object implementing enter/exit | Use context-manager protocol or `contextlib` | Expect function-call wrapper to manage a block |

An async generator is not a coroutine function in the same semantic sense as an `async def` without `yield`. Test `inspect.isasyncgenfunction` where that distinction matters. Do not assume one generic decorator can transparently preserve all four execution models.

### 8.9 When explicit composition is better

Prefer explicit composition when it makes policy visible and easy to test:

```python
def load_customer(customer_id: str) -> dict:
    ...

def service(customer_id: str) -> dict:
    result = load_customer(customer_id)
    validate_customer(result)
    audit_access(customer_id)
    return result
```

A decorator is useful for a cross-cutting, consistently applied policy. Explicit calls are often clearer when the order is domain-specific, behavior varies by call site, or the wrapper hides meaningful control flow. Avoid decorator stacks that make a function's real behavior impossible to understand from its definition and nearby code.

## 9. Practical implementation project: reliable operation wrappers

Build a small module named `operation_decorators.py` with:
1. `retry` for synchronous functions using total-attempt semantics and a narrow exception allow-list.
2. `async_retry` for coroutine functions using `asyncio.sleep` and propagating cancellation.
3. `timed` or `observe` for synchronous functions, plus an async-aware equivalent.
4. `CountCalls` as a class-based decorator and `CountMethodCalls` with explicit descriptor binding.
5. A registration-only decorator for a small command/handler registry.
6. Tests for success, failure, metadata, signatures, methods, async calls, and invalid configuration.

Suggested design constraints:
- Keep sleep and clock dependencies injectable in a larger production implementation so tests need not wait.
- Retry only operations that are safe to repeat or protected by an idempotency key.
- Do not log raw secrets or full argument payloads.
- Specify the state scope and concurrency guarantee of each decorator.
- Use `ParamSpec` and `TypeVar` for function wrappers; document limitations for callable objects and changed signatures.
- Avoid turning the module into a generic “magic” framework. Each decorator should have one purpose.

### 9.1 Complete reference implementation

For an end-to-end runnable baseline, save the following block as `operation_decorators.py`. It consolidates the core patterns from this lesson into one importable module. The simpler examples above explain individual concepts; this module is the implementation used by the regression tests below.

```python
from __future__ import annotations

import asyncio
import inspect
import logging
import math
from collections.abc import Awaitable, Callable
from functools import wraps, update_wrapper
from time import perf_counter, sleep
from typing import Any, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")
logger = logging.getLogger(__name__)
ROUTES: dict[str, Callable[..., Any]] = {}


def retry(
    times: int = 3,
    *,
    delay: float = 0.1,
    retry_on: tuple[type[Exception], ...] = (TimeoutError,),
    backoff: float = 1.0,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    if isinstance(times, bool) or not isinstance(times, int) or times < 1:
        raise ValueError("times must be an integer >= 1")
    if isinstance(delay, bool) or not isinstance(delay, (int, float)) or not math.isfinite(delay) or delay < 0:
        raise ValueError("delay must be a finite number >= 0")
    if isinstance(backoff, bool) or not isinstance(backoff, (int, float)) or not math.isfinite(backoff) or backoff < 1:
        raise ValueError("backoff must be a finite number >= 1")
    if not isinstance(retry_on, tuple) or not retry_on:
        raise ValueError("retry_on must be a non-empty tuple of exception classes")
    if any(not isinstance(exc, type) or not issubclass(exc, Exception) for exc in retry_on):
        raise TypeError("retry_on entries must be Exception subclasses")

    def decorate(fn: Callable[P, R]) -> Callable[P, R]:
        @wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            wait = delay
            for attempt_number in range(1, times + 1):
                try:
                    return fn(*args, **kwargs)
                except retry_on:
                    if attempt_number == times:
                        raise
                    if wait:
                        sleep(wait)
                    wait *= backoff
            raise AssertionError("unreachable")
        return wrapper
    return decorate


def async_retry(
    attempts: int = 3,
    *,
    delay: float = 0.1,
    retry_on: tuple[type[Exception], ...] = (TimeoutError,),
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    if isinstance(attempts, bool) or not isinstance(attempts, int) or attempts < 1:
        raise ValueError("attempts must be an integer >= 1")
    if isinstance(delay, bool) or not isinstance(delay, (int, float)) or not math.isfinite(delay) or delay < 0:
        raise ValueError("delay must be a finite number >= 0")
    if not isinstance(retry_on, tuple) or not retry_on or any(
        not isinstance(exc, type) or not issubclass(exc, Exception) for exc in retry_on
    ):
        raise ValueError("retry_on must contain Exception subclasses")

    def decorate(fn: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @wraps(fn)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for attempt_number in range(1, attempts + 1):
                try:
                    return await fn(*args, **kwargs)
                except retry_on:
                    if attempt_number == attempts:
                        raise
                    if delay:
                        await asyncio.sleep(delay * attempt_number)
            raise AssertionError("unreachable")
        return wrapper
    return decorate


def timed_auto(fn: Callable[..., Any]) -> Callable[..., Any]:
    if inspect.isasyncgenfunction(fn):
        raise TypeError("timed_auto does not support async-generator functions")
    if inspect.iscoroutinefunction(fn):
        @wraps(fn)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            started = perf_counter()
            try:
                return await fn(*args, **kwargs)
            finally:
                logger.info("operation_timed", extra={
                    "operation": fn.__qualname__,
                    "duration_seconds": perf_counter() - started,
                })
        return async_wrapper

    @wraps(fn)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        started = perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            logger.info("operation_timed", extra={
                "operation": fn.__qualname__,
                "duration_seconds": perf_counter() - started,
            })
    return sync_wrapper


def timed_generator(fn: Callable[..., Any]) -> Callable[..., Any]:
    if not inspect.isgeneratorfunction(fn):
        raise TypeError("timed_generator requires a generator function")

    @wraps(fn)
    def wrapper(*args: Any, **kwargs: Any):
        started = perf_counter()
        try:
            yield from fn(*args, **kwargs)
        finally:
            logger.info("generator_timed", extra={
                "operation": fn.__qualname__,
                "duration_seconds": perf_counter() - started,
            })
    return wrapper


def logged(fn: Callable[P, R]) -> Callable[P, R]:
    @wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        logger.debug("operation_called", extra={"operation": fn.__qualname__})
        return fn(*args, **kwargs)
    return wrapper


def trace(fn: Callable[..., Any] | None = None, *, label: str = "call"):
    def decorate(target: Callable[..., Any]):
        @wraps(target)
        def wrapper(*args: Any, **kwargs: Any):
            logger.debug("decorator_trace", extra={
                "label": label,
                "operation": target.__qualname__,
            })
            return target(*args, **kwargs)
        return wrapper
    return decorate if fn is None else decorate(fn)


class CountCalls:
    def __init__(self, fn: Callable[P, R]) -> None:
        update_wrapper(self, fn)
        self.fn = fn
        self.calls = 0

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        self.calls += 1
        return self.fn(*args, **kwargs)


class CountMethodCalls:
    def __init__(self, fn: Callable[..., Any]) -> None:
        update_wrapper(self, fn)
        self.fn = fn
        self.calls = 0

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.calls += 1
        return self.fn(*args, **kwargs)

    def __get__(self, instance: object | None, owner: type | None = None):
        if instance is None:
            return self
        from functools import partial
        return partial(self.__call__, instance)


def route(path: str):
    def decorate(fn: Callable[P, R]) -> Callable[P, R]:
        if path in ROUTES:
            raise ValueError(f"duplicate route: {path}")
        ROUTES[path] = fn
        return fn
    return decorate
```

This reference module intentionally does not claim support for every callable shape: `CountMethodCalls` is for ordinary instance methods, `timed_auto` rejects async generators rather than silently mismeasuring them, and retry wrappers are not safe for arbitrary side-effecting operations. For production code, consider injecting a sleeper/clock to make time behavior deterministic in tests.

## 10. Exercises, tests, interview questions, and competency checklist

### 10.1 Exercises

1. Implement `@retry(times=4, retry_on=(TimeoutError,))`. Prove that it invokes the target at most four times and re-raises the fourth exception.
2. Reject `times=0`, `times=-1`, `times=True`, and non-integer values. Explain why `bool` needs special handling despite being an `int` subclass.
3. Write an optional-argument `@trace` that supports both `@trace` and `@trace(label="sql")`.
4. Remove `@wraps` from a decorator and observe the difference in `__name__`, `__doc__`, `__wrapped__`, and `inspect.signature`.
5. Implement `CountCalls` and test that two decorated functions maintain independent counters.
6. Decorate an instance method with a class-based decorator. Test class access, instance access, and a subclass.
7. Stack logging and retry decorators in both orders. Count log messages and function invocations; explain the difference.
8. Write an async retry test using a coroutine that fails twice and succeeds on the third call. Verify that cancellation is not retried.
9. Wrap a generator function and demonstrate why timing the call alone does not time iteration. Propose a generator-aware alternative.
10. Add a cache to a pure function, then demonstrate why mutable external state requires invalidation.
11. Define an injected-context decorator with `Concatenate`. Explain the difference between its type signature and `inspect.signature`.
12. Replace a decorator stack with explicit composition and compare readability and testability.

### 10.2 Runnable regression tests

The following regression suite uses only the Python standard library. Save the complete reference implementation above as `operation_decorators.py`, save this block as `test_decorators.py` in the same directory, and run `python test_decorators.py`. It uses assertions rather than requiring `pytest`.

```python
import asyncio
import inspect
from unittest.mock import patch

from operation_decorators import (
    ROUTES, CountCalls, CountMethodCalls, async_retry, logged, retry, route,
    timed_auto, timed_generator, trace,
)


def test_retry_success_and_exhaustion():
    calls = 0

    @retry(times=3, delay=0, retry_on=(TimeoutError,))
    def eventually():
        nonlocal calls
        calls += 1
        if calls < 3:
            raise TimeoutError("temporary")
        return "ok"

    assert eventually() == "ok"
    assert calls == 3

    calls = 0
    final_error = TimeoutError("last failure")

    @retry(times=2, delay=0, retry_on=(TimeoutError,))
    def always_fails():
        nonlocal calls
        calls += 1
        raise final_error

    try:
        always_fails()
    except TimeoutError as exc:
        assert exc is final_error
        assert str(exc) == "last failure"
    else:
        raise AssertionError("expected TimeoutError")
    assert calls == 2

    calls = 0

    @retry(times=1, delay=0, retry_on=(TimeoutError,))
    def one_attempt():
        nonlocal calls
        calls += 1
        raise TimeoutError("single attempt")

    try:
        one_attempt()
    except TimeoutError as exc:
        assert str(exc) == "single attempt"
    else:
        raise AssertionError("expected TimeoutError")
    assert calls == 1


def test_retry_delay_schedule():
    calls = 0

    @retry(times=3, delay=0.1, backoff=2, retry_on=(TimeoutError,))
    def succeeds_on_third_call():
        nonlocal calls
        calls += 1
        if calls < 3:
            raise TimeoutError("temporary")
        return "ok"

    with patch("operation_decorators.sleep") as mocked_sleep:
        assert succeeds_on_third_call() == "ok"
    assert calls == 3
    assert [call.args[0] for call in mocked_sleep.call_args_list] == [0.1, 0.2]


def test_retry_does_not_retry_unlisted_exception():
    calls = 0

    @retry(times=5, delay=0, retry_on=(TimeoutError,))
    def fail_fast():
        nonlocal calls
        calls += 1
        raise ValueError("not retryable")

    try:
        fail_fast()
    except ValueError as exc:
        assert str(exc) == "not retryable"
    else:
        raise AssertionError("expected ValueError")
    assert calls == 1


def test_retry_invalid_configuration():
    for invalid in (0, -1, True, 1.5, "3"):
        try:
            retry(times=invalid)
        except ValueError:
            pass
        else:
            raise AssertionError(f"times={invalid!r} should fail")

    for invalid_delay in (-0.1, True, float("nan"), float("inf"), "0.1"):
        try:
            retry(delay=invalid_delay)
        except ValueError:
            pass
        else:
            raise AssertionError(f"delay={invalid_delay!r} should fail")

    for invalid_backoff in (0.5, True, float("nan"), float("inf"), "2"):
        try:
            retry(backoff=invalid_backoff)
        except ValueError:
            pass
        else:
            raise AssertionError(f"backoff={invalid_backoff!r} should fail")

    for options in ({"retry_on": ()}, {"retry_on": (str,)}):
        try:
            retry(**options)
        except (ValueError, TypeError):
            pass
        else:
            raise AssertionError(f"invalid retry_on={options!r} should fail")


def test_metadata_and_signature():
    @logged
    def greet(name: str, punctuation: str = "!") -> str:
        """Greet someone."""
        return f"Hello, {name}{punctuation}"

    assert greet("Ada") == "Hello, Ada!"
    assert greet.__name__ == "greet"
    assert greet.__doc__ == "Greet someone."
    assert greet.__wrapped__("Lin", "?") == "Hello, Lin?"
    assert str(inspect.signature(greet)) == "(name: str, punctuation: str = '!') -> str"


def test_positional_only_and_keyword_only_contract():
    @logged
    def combine(left, /, right=2, *, scale):
        return (left + right) * scale

    assert combine(3, scale=4) == 20
    try:
        combine(left=3, scale=4)
    except TypeError:
        pass
    else:
        raise AssertionError("positional-only argument accepted as keyword")


def test_optional_decorator_forms():
    @trace
    def one(value):
        return value + 1

    @trace(label="db")
    def two(value):
        return value * 2

    assert one(2) == 3
    assert two(3) == 6


def test_class_decorator_state_and_methods():
    @CountCalls
    def cube(n):
        return n ** 3

    cube.__wrapped__.calls = 900  # custom function metadata must not replace counter state
    assert cube.calls == 0
    assert cube(2) == 8
    assert cube(3) == 27
    assert cube.calls == 2

    class Service:
        @CountMethodCalls
        def combine(self, left, right):
            return left + right

    service = Service()
    assert service.combine(2, 4) == 6
    assert service.combine(3, 5) == 8
    assert Service.combine.calls == 2


def test_timed_generator_preserves_iteration():
    @timed_generator
    def values():
        yield 1
        yield 2
        yield 3

    generator = values()
    assert inspect.isgenerator(generator)
    assert list(generator) == [1, 2, 3]

    try:
        timed_generator(lambda: iter((1, 2)))
    except TypeError:
        pass
    else:
        raise AssertionError("timed_generator must reject non-generator functions")


def test_registration_only():
    ROUTES.clear()

    @route("/ready")
    def ready():
        return True

    assert ready() is True
    assert ROUTES["/ready"] is ready


async def test_async_retry_and_timing():
    calls = 0

    @async_retry(attempts=3, delay=0, retry_on=(TimeoutError,))
    async def eventually():
        nonlocal calls
        calls += 1
        if calls < 3:
            raise TimeoutError("temporary")
        return "async-ok"

    assert await eventually() == "async-ok"
    assert calls == 3
    assert inspect.iscoroutinefunction(eventually)

    @timed_auto
    async def answer():
        await asyncio.sleep(0)
        return 42

    assert await answer() == 42

    cancellation_calls = 0

    @async_retry(attempts=4, delay=0, retry_on=(Exception,))
    async def blocked():
        nonlocal cancellation_calls
        cancellation_calls += 1
        await asyncio.Event().wait()

    task = asyncio.create_task(blocked())
    await asyncio.sleep(0)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    else:
        raise AssertionError("cancellation must propagate")
    assert cancellation_calls == 1


def run_tests():
    test_retry_success_and_exhaustion()
    test_retry_delay_schedule()
    test_retry_does_not_retry_unlisted_exception()
    test_retry_invalid_configuration()
    test_metadata_and_signature()
    test_positional_only_and_keyword_only_contract()
    test_optional_decorator_forms()
    test_class_decorator_state_and_methods()
    test_timed_generator_preserves_iteration()
    test_registration_only()
    asyncio.run(test_async_retry_and_timing())
    print("All decorator regression tests passed.")


if __name__ == "__main__":
    run_tests()
```

**Test-suite note:** The test module imports the consolidated implementation above. The tests intentionally do not assert timing durations because wall-clock measurements are noisy; test observable behavior and inject a fake clock/sleeper for deterministic timing/retry tests in a larger implementation.

### 10.3 Additional negative and boundary cases

Add these tests in a real project:

- `retry(times=1)` invokes the function once and never sleeps.
- A successful first call produces no retry delay.
- `delay=0` does not call the sleep function; negative delay and `backoff < 1` are rejected.
- `retry_on=()` and non-exception classes are rejected.
- The final exception object and its traceback are not replaced by a generic exception.
- A wrapped function's positional-only, keyword-only, default, and unexpected-keyword behavior is preserved.
- Exceptions raised by the target are propagated through `timed` and `observe`.
- `CountCalls` counts failed calls too, and two decorator instances do not share counters.
- Method descriptor behavior is correct for instance access and documented limitations for `classmethod` and `staticmethod`.
- Async cancellation propagates immediately and is not retried.
- A generator-aware wrapper preserves iteration, `close`, and exception semantics if the API claims to support them.
- Concurrent counter tests check the exact guarantee made by the implementation.
- A custom `__signature__` agrees with runtime validation rather than misleading framework consumers.

### 10.4 Interview questions with concise answers

1. **What is the difference between a decorator and a decorator factory?** A decorator receives the target; a factory receives configuration and returns a decorator.
2. **What does `@retry(times=3)` expand to?** Evaluate `retry(times=3)`, apply the returned decorator to the function, and bind the name to the result.
3. **Why use `functools.wraps`?** It copies standard metadata and sets `__wrapped__`, improving introspection and framework compatibility; it does not rewrite runtime argument binding.
4. **What does `__wrapped__` do?** It exposes the wrapped callable for tools and explicit unwrapping; it is not a security boundary.
5. **Why does a class-based decorator need `__get__` for methods?** Callable instances do not automatically receive function-descriptor method binding.
6. **Why can retry be dangerous?** A timed-out operation may have committed side effects; repeated calls can duplicate them unless the operation is idempotent or guarded by an idempotency key.
7. **How should an async retry wait?** Use `await asyncio.sleep(...)`, and allow cancellation to propagate.
8. **Why can a generic timing decorator mismeasure a generator?** Calling a generator function creates a generator; execution occurs during iteration.
9. **What is the difference between `ParamSpec` and `TypeVar`?** `ParamSpec` captures parameter types; `TypeVar` captures a type such as the return value.
10. **What does `Concatenate` express?** A callable whose leading parameter(s) are added or removed by a decorator's interface.
11. **Does setting `__signature__` validate calls?** No. It changes introspection metadata; the wrapper must enforce the same contract.
12. **When is composition preferable?** When control flow or ordering is domain-specific and explicit calls are easier to understand than a hidden wrapper stack.
13. **Is a stateful decorator thread-safe by default?** No. State scope and synchronization guarantees must be designed and documented.
14. **What is a registration-only decorator?** It records the target and returns that same target instead of wrapping it.
15. **Does `@wraps` make an async wrapper async?** No. The wrapper's own definition determines whether it is a coroutine function.

### 10.5 Competency checklist

- [ ] I can explain decoration-time evaluation versus call-time execution.
- [ ] I can draw the three layers of a parameterized decorator and identify each layer's inputs.
- [ ] I use `wraps` or `update_wrapper` and can explain `__wrapped__`.
- [ ] I understand that introspection signatures and runtime argument binding are different.
- [ ] I can implement a bounded retry policy with clear exception, delay, and failure semantics.
- [ ] I can explain why retrying non-idempotent operations is dangerous.
- [ ] I can implement a callable-instance decorator and state where its mutable state lives.
- [ ] I can explain descriptor binding and test class-based decorators on instance methods.
- [ ] I can reason about decorator stacking order and registration-only decorators.
- [ ] I can keep sync, coroutine, generator, and async-generator behavior distinct.
- [ ] I can use `ParamSpec`, `TypeVar`, and `Concatenate` for appropriate callable contracts.
- [ ] I can discuss re-entrancy, thread safety, cache invalidation, logging, and signature modification.
- [ ] I can justify when explicit composition is clearer than a decorator.

## Summary

Decorators are ordinary callable transformations with important consequences for API behavior. Prefer the simplest function wrapper that preserves the target's contract. Use a factory when configuration is needed, a callable instance when per-decorator state is useful, and a descriptor when a callable object must bind as a method. Preserve metadata, type the callable relationship, and test exceptions, signatures, methods, and async behavior. Treat retries, caching, and logging as production policies—not just syntax—and make their state, safety, and observability guarantees explicit.

## Further reading

- Python language reference, function definitions and decorators: https://docs.python.org/3/reference/compound_stmts.html#function-definitions
- `functools.wraps`, `update_wrapper`, `partial`, `cache`, and `lru_cache`: https://docs.python.org/3/library/functools.html
- `inspect.signature`, `unwrap`, `iscoroutinefunction`, and generator inspection: https://docs.python.org/3/library/inspect.html
- `typing.ParamSpec`, `Concatenate`, and `TypeVar`: https://docs.python.org/3/library/typing.html
- `contextlib.contextmanager` and `asynccontextmanager`: https://docs.python.org/3/library/contextlib.html
- `asyncio` task cancellation and sleep: https://docs.python.org/3/library/asyncio-task.html
