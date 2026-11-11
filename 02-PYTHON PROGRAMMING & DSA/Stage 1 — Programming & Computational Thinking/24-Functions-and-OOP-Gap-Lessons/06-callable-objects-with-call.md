# Callable Objects with `__call__`

**Stage 1 — Programming & Computational Thinking · Module 1.24 · Lesson 06**  
**Target version:** Python 3.12+  
**Estimated study time:** 3–4 focused sessions, including exercises and tests

## 1. Learning objectives

By the end of this lesson, you should be able to:

- Explain how defining `__call__` on a class makes its instances callable, and distinguish an instance call from construction of a class.
- Use `callable(obj)` correctly without treating it as proof that every invocation is valid.
- Build stateful and configured callables for counters, scaling, validation, transformation, retry, and rate limiting.
- Pass callable instances to `map`, `sorted(key=...)`, `Executor.submit`, callbacks, and pipeline APIs.
- Choose deliberately between a function, `functools.partial`, closure, callable class, and ordinary object with named methods.
- Design public configuration, state visibility, useful representations, documentation, and defensible equality/hash semantics.
- Inject clocks, sleepers, and ID generators so tests remain deterministic and do not rely on real waiting.
- Type callable contracts with `Callable`, `Protocol`, generic type variables, and `ParamSpec` where appropriate.
- Distinguish instance `__call__` from the metaclass construction protocol used when calling a class.
- Reason about performance, mutable state, concurrency, process boundaries, and serialization constraints.
- Test configuration, state transitions, error paths, dependency injection, and repeatability.
- Refactor procedural code into pure functions plus configuration, closures, or callable objects and justify the trade-off.

## 2. Prerequisites and roadmap placement

This lesson assumes familiarity with function definitions and parameters, scope and closures, mutability and identity, basic classes, type annotations, pytest, and higher-order functions. It follows Lessons 01–05 in this gap module and prepares for Lesson 07's function-design review. It previews construction mechanics covered directly in Lesson 09; it does not attempt to replace the lessons on descriptors, decorators, or CPython internals.

| Prerequisite | Why it matters here |
|---|---|
| Functions, parameters, return values, exceptions (Module 1.3) | A callable's signature is a contract, and its body may raise exceptions. |
| Scope, side effects, and closures (Module 1.3; Lessons 03–04 here) | Callables can retain state or depend on external resources. |
| Classes, instances, identity, and mutability (Modules 1.2 and 1.8) | `__call__` is defined on a type and invoked for an instance. |
| Typing and protocols (Module 1.9) | Public callback contracts should be expressible to type checkers. |
| Pytest and deterministic testing (Module 1.7) | Stateful behavior and time-dependent policies need repeatable tests. |
| Higher-order functions and sorting (Lesson 05 here) | Callable objects are values passed to APIs that expect behavior. |

## 3. Callability fundamentals

### 3.1 The smallest callable object: `Counter`

A callable object combines ordinary instance data with function-like syntax. Define `__call__` on the class, then call an instance with parentheses:

```python
class Counter:
    """A counter whose calls increment and return its current value."""

    def __init__(self, start: int = 0) -> None:
        self.n = start

    def __call__(self, step: int = 1) -> int:
        self.n += step
        return self.n


tick = Counter()
print(tick(), tick(), tick(5))
print(callable(tick))
print(tick.n)
```

Expected output:

```text
1 2 7
True
7
```

The instance stores state (`n`), and each invocation updates it. `tick` is the object; `tick()` invokes it. The default `step=1` applies when no argument is supplied.

### 3.2 What `obj(...)` means

At the Python language level, `obj(*args, **kwargs)` asks the object's type to perform the call operation. For a typical user-defined class whose instances implement `__call__`, the effective behavior is equivalent in spirit to:

```python
# Conceptual illustration; ordinary code should write obj(...).
result = type(obj).__call__(obj, *args, **kwargs)
```

The call machinery is a special-method operation: Python looks for the relevant special method on the type, not by treating an arbitrary `obj.__call__` instance attribute as a universal replacement. This is one reason that assigning `instance.__call__ = ...` is not a reliable way to make an otherwise non-callable instance callable. Define the method on the class (or use a class whose type already supports calls).

`__call__(self, *args, **kwargs)` is a flexible signature pattern, not a requirement that every implementation accept arbitrary arguments. A good API usually exposes the narrowest meaningful signature:

```python
class Scaler:
    """Multiply numeric input by a configured factor."""

    def __init__(self, factor: float) -> None:
        self.factor = factor

    def __call__(self, value: float) -> float:
        return value * self.factor


double = Scaler(2.0)
print(double(3.5))
print(list(map(double, [1.0, 2.0, 3.0])))
```

Expected output:

```text
7.0
[2.0, 4.0, 6.0]
```

The configuration is supplied once to `Scaler(2.0)`; each later `double(value)` supplies data.

### 3.3 Callable class versus callable instance

A **class** is normally callable because calling it constructs an instance. An **instance** is callable only if its type supports the call protocol, commonly through `__call__`.

```python
class Greeter:
    def __init__(self, greeting: str = "Hello") -> None:
        self.greeting = greeting

    def __call__(self, name: str) -> str:
        return f"{self.greeting}, {name}!"


print(callable(Greeter))            # The class can construct an instance.
print(callable(Greeter()))          # This instance can greet.
print(Greeter("Welcome")("Ada"))   # Construct, then invoke the instance.
```

Expected output:

```text
True
True
Welcome, Ada!
```

The syntax `Greeter("Welcome")` runs the class-construction protocol and returns an instance. The second pair of parentheses invokes that instance's `__call__`. In contrast, `Greeter()`, with no second call, only constructs an instance.

### 3.4 `callable(obj)` and the common `TypeError`

`callable(obj)` reports whether the object appears callable according to Python's runtime call protocol. It does **not** check whether a particular argument list matches the signature, whether validation will pass, or whether the call will succeed.

```python
class Report:
    pass

report = Report()
print(callable(report))

try:
    report()
except TypeError as exc:
    print(type(exc).__name__, str(exc))
```

Expected output:

```text
False
TypeError 'Report' object is not callable
```

A different `TypeError` can occur when an object is callable but called with the wrong arguments:

```python
class Adder:
    def __call__(self, left: int, right: int) -> int:
        return left + right

add = Adder()
assert callable(add)
assert add(2, 3) == 5
# add(2)  # TypeError: missing a required positional argument
```

Treat `callable()` as a capability check, not a substitute for a documented interface or error handling. A function can also be callable but raise an exception internally.

## 4. Beginner patterns: configuration and state

### 4.1 A configured transformation

A configured callable is useful when the policy is fixed for a batch or pipeline but the input varies per call.

```python
from collections.abc import Iterable


class Clamp:
    """Clamp numeric values to an inclusive interval."""

    def __init__(self, minimum: float, maximum: float) -> None:
        if minimum > maximum:
            raise ValueError("minimum must be <= maximum")
        self.minimum = minimum
        self.maximum = maximum

    def __call__(self, value: float) -> float:
        return min(max(value, self.minimum), self.maximum)


def transform_all(values: Iterable[float], transform: Clamp) -> list[float]:
    return [transform(value) for value in values]


clamp = Clamp(0.0, 1.0)
print(transform_all([-0.4, 0.2, 1.8], clamp))
```

Expected output:

```text
[0.0, 0.2, 1.0]
```

Validate configuration at construction time so invalid objects fail early. This example does not need mutable state: the same input produces the same output as long as the configuration remains unchanged.

### 4.2 A validator with an explicit contract

Validators should make their failure semantics clear. This validator returns a boolean; it does not silently rewrite input or raise for ordinary invalid values.

```python
class NonEmptyText:
    """Check that text contains at least one non-whitespace character."""

    def __call__(self, value: str) -> bool:
        return bool(value.strip())


is_non_empty = NonEmptyText()
for candidate in ["north", "  ", "south"]:
    print(repr(candidate), is_non_empty(candidate))
```

Expected output:

```text
'north' True
'  ' False
'south' True
```

If invalid data should produce structured diagnostics, a named method such as `validate()` returning a result object may be clearer than a bare boolean. The callable syntax is an API choice, not a requirement.

### 4.3 Expose configuration and represent objects usefully

Production callables should be inspectable. Prefer public read-only properties or documented attributes for stable configuration, and a useful `repr` for debugging. Do not include secrets, credentials, or huge payloads in representations.

```python
class Multiplier:
    """Multiply values by an immutable-by-convention factor."""

    def __init__(self, factor: float) -> None:
        self._factor = factor

    @property
    def factor(self) -> float:
        return self._factor

    def __call__(self, value: float) -> float:
        return value * self._factor

    def __repr__(self) -> str:
        return f"Multiplier(factor={self._factor!r})"


triple = Multiplier(3.0)
print(repr(triple))
print(triple.factor, triple(4.0))
```

Expected output:

```text
Multiplier(factor=3.0)
3.0 12.0
```

A property prevents callers from assigning `factor` through the public API, but `_factor` is still technically accessible in Python. This is encapsulation by convention, not a security boundary. If runtime reconfiguration is a supported feature, expose a deliberate setter or configuration method and document whether concurrent calls may observe changes.

### 4.4 Equality and hashing: do not invent semantics

Two callables are not automatically equivalent because they have the same class. If equality is useful, define what it means—for example, two immutable `Multiplier` objects with equal factors. A mutable stateful callable is usually a poor dictionary key: changing fields that participate in hashing can break lookup invariants. By default, user-defined instances normally use identity-based equality and hashing inherited from `object` unless overridden.

Use a frozen dataclass for simple immutable configuration when that fits the design:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class AffineTransform:
    scale: float
    offset: float = 0.0

    def __call__(self, value: float) -> float:
        return self.scale * value + self.offset


first = AffineTransform(2.0, 1.0)
second = AffineTransform(2.0, 1.0)
print(first(4.0))
print(first == second)
print(len({first, second}))
```

Expected output:

```text
9.0
True
1
```

A frozen dataclass generates equality and, when its fields permit it, a compatible hash. Do not make a class hashable if its equality-relevant state can mutate. Also note that `frozen=True` is shallow: a field that refers to a mutable object is not made deeply immutable.

For a class-based decorator, `functools.update_wrapper(self, fn)` can copy useful function metadata and set `__wrapped__`, allowing tools such as `inspect.signature` to follow the wrapped callable. This is appropriate only when the instance is intended to present itself as a wrapped function; it does not make the instance's call behavior or signature magically type-safe.

```python
from functools import update_wrapper
from typing import Any


class TraceCalls:
    def __init__(self, fn: Any) -> None:
        self._fn = fn
        update_wrapper(self, fn)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        print(f"calling {self.__name__}")
        return self._fn(*args, **kwargs)


@TraceCalls
def greet(name: str) -> str:
    """Return a greeting."""
    return f"Hello, {name}!"


print(greet.__name__)
print(greet("Ada"))
print(greet.__wrapped__("Lin"))
```

Expected output:

```text
greet
calling greet
Hello, Ada!
Hello, Lin!
```

Prefer `ParamSpec` and a generic result type when you need a statically precise decorator contract (Section 9.4). `update_wrapper` copies metadata; it does not preserve static typing by itself. The example uses `Any` to keep attention on runtime metadata rather than pretending to provide a type-safe generic wrapper.

## 5. Choosing the right abstraction

Callable objects are useful, but they are not automatically better than functions. Choose the simplest representation that makes state, configuration, and behavior clear.

| Need | Usually start with | Why / limitation |
|---|---|---|
| Stateless operation with no retained configuration | Plain function | Familiar, easy to test, and easy to inspect. |
| Bind a few arguments to an existing function | `functools.partial` | Avoids a wrapper; semantics can be less obvious for complex configuration. |
| Small amount of private retained state | Closure | Concise, but state is less inspectable and serialization is often awkward. |
| Several settings, meaningful state, public representation, lifecycle, or multiple related methods | Callable class | Explicit and extensible, but adds a type and object lifecycle. |
| Object has multiple operations or a domain lifecycle | Ordinary class with named methods | `transform()`, `validate()`, or `close()` can be clearer than making the object callable. |
| Different interchangeable policies | Functions or callable instances behind a common protocol | Makes strategy selection explicit. |

### 5.1 One operation, five implementations

Suppose a pipeline must multiply every value by a configured factor.

**Plain function** — best when there is no per-instance configuration:

```python
def double_value(value: float) -> float:
    return value * 2.0
```

**`partial`** — best when binding an argument to a reusable function is enough:

```python
from functools import partial


def multiply(value: float, factor: float) -> float:
    return value * factor


double_partial = partial(multiply, factor=2.0)
assert double_partial(3.0) == 6.0
```

**Closure** — compact when retained state can remain private and the function will stay local:

```python
from collections.abc import Callable


def make_multiplier(factor: float) -> Callable[[float], float]:
    def transform(value: float) -> float:
        return value * factor
    return transform


double_closure = make_multiplier(2.0)
assert double_closure(3.0) == 6.0
```

**Callable class** — useful when configuration needs a named type and inspectable state:

```python
class ConfiguredMultiplier:
    def __init__(self, factor: float) -> None:
        self.factor = factor

    def __call__(self, value: float) -> float:
        return value * self.factor


double_object = ConfiguredMultiplier(2.0)
assert double_object(3.0) == 6.0
```

**Ordinary class with a named method** — useful when the operation belongs to a larger object API:

```python
class PricingRule:
    def __init__(self, multiplier: float) -> None:
        self.multiplier = multiplier

    def apply(self, subtotal: float) -> float:
        return subtotal * self.multiplier


rule = PricingRule(2.0)
assert rule.apply(3.0) == 6.0
```

The outputs match, but the APIs communicate different intent. `partial` and a closure do not need a new class; the callable class can expose configuration and evolve with additional behavior; a named method makes the operation explicit. Do not introduce a callable class solely to avoid writing one small function.

### 5.2 Refactor procedural code: separate computation from policy

Start with a function that mixes transformation logic with parameters:

```python
def normalize_score(raw: float, scale: float, offset: float, floor: float) -> float:
    return max(floor, raw * scale + offset)
```

If the configuration is reused many times, a callable object can name that configuration and validate it once:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ScoreTransform:
    scale: float
    offset: float = 0.0
    floor: float = 0.0

    def __call__(self, raw: float) -> float:
        return max(self.floor, raw * self.scale + self.offset)


transform = ScoreTransform(scale=0.1, offset=2.0, floor=0.0)
print([transform(value) for value in [10.0, 20.0, -50.0]])
```

Expected output:

```text
[3.0, 4.0, 0.0]
```

For stronger separation, keep the mathematical operation pure and treat the object as a configured adapter:

```python
from dataclasses import dataclass


def calculate_score(raw: float, *, scale: float, offset: float, floor: float) -> float:
    return max(floor, raw * scale + offset)


@dataclass(frozen=True)
class ScorePolicy:
    scale: float
    offset: float = 0.0
    floor: float = 0.0

    def __call__(self, raw: float) -> float:
        return calculate_score(
            raw, scale=self.scale, offset=self.offset, floor=self.floor
        )
```

The pure function is easy to reuse independently; `ScorePolicy` packages a stable set of parameters into a pipeline-compatible callable. A closure can be equally valid for a small local policy. Choose based on visibility, reuse, testing, lifecycle, and serialization needs—not on fashion.

## 6. Callable objects in higher-order APIs

A higher-order API accepts behavior as a value. Callable instances work wherever the API contract accepts a compatible callable.

### 6.1 `map`, filtering, and `sorted(key=...)`

```python
class CaseFold:
    def __call__(self, text: str) -> str:
        return text.casefold()


fold = CaseFold()
words = ["pear", "Apple", "apricot"]
print(list(map(fold, words)))
print(sorted(words, key=fold))
```

Expected output:

```text
['pear', 'apple', 'apricot']
['Apple', 'apricot', 'pear']
```

`sorted` calls the key callable once per item to obtain comparison keys; it does not expect a comparator that compares two items. The returned keys determine ordering. This also means the key should generally be deterministic and side-effect-free.

### 6.2 Data pipeline stages

A small pipeline can store stages as callables and apply them in sequence:

```python
from collections.abc import Callable, Iterable
from typing import TypeVar

T = TypeVar("T")


def apply_stages(value: str, stages: Iterable[Callable[[str], str]]) -> str:
    result = value
    for stage in stages:
        result = stage(result)
    return result


class Strip:
    def __call__(self, value: str) -> str:
        return value.strip()


class Upper:
    def __call__(self, value: str) -> str:
        return value.upper()


print(apply_stages("  north  ", [Strip(), Upper()]))
```

Expected output:

```text
NORTH
```

This example deliberately uses same-type string stages so the contract remains clear to a type checker. A statically typed pipeline with heterogeneous input and output types generally needs overloads, a composition abstraction, or a carefully chosen common input/output type. Do not claim that arbitrary function composition is type-safe merely because every stage is callable.

### 6.3 Executor submission and callbacks

`Executor.submit` accepts a callable and positional/keyword arguments, then schedules the call. A callable instance is valid if it is compatible with the executor's execution and serialization requirements.

```python
from concurrent.futures import ThreadPoolExecutor


class AddOffset:
    def __init__(self, offset: int) -> None:
        self.offset = offset

    def __call__(self, value: int) -> int:
        return value + self.offset


add_ten = AddOffset(10)
with ThreadPoolExecutor(max_workers=2) as executor:
    futures = [executor.submit(add_ten, value) for value in [1, 2, 3]]
    results = [future.result() for future in futures]
print(results)
```

Expected output:

```text
[11, 12, 13]
```

The result list preserves submission order because the futures are collected in the original list order; completion order may differ. The call itself does not mutate instance state, so concurrent calls do not race over call-managed state. The `offset` attribute is still publicly mutable; do not mutate configuration concurrently, and make it read-only/private if that is part of the production contract. A callable with mutable per-call state needs a separate concurrency design.

A callback API may call the supplied object later, sometimes with arguments chosen by the framework. Match the callback's documented signature exactly. A callable that expects `event: Event` cannot safely stand in for a zero-argument callback unless an adapter binds or discards arguments intentionally. Other standard-library callback APIs accept callables too: `threading.Thread(target=obj)` invokes the target in the new thread (and can pass `args=`/`kwargs=`), while `atexit.register(obj, ...)` defers invocation until normal interpreter shutdown. `signal.signal(signum, handler)` expects the handler signature `(signum, frame)`, so a callable with a different signature is not a compatible handler. These APIs differ in timing and execution context; “callable” alone does not guarantee signature compatibility or thread safety.

### 6.4 Tool interfaces and middleware: a restrained pattern

A callable tool can package a name, description, validation policy, and execution behavior. Keep external I/O and trust boundaries explicit; `__call__` is not itself a security or schema-validation mechanism.

```python
from dataclasses import dataclass


@dataclass
class AddTool:
    name: str = "add"
    description: str = "Add two integers."

    def __call__(self, *, left: int, right: int) -> int:
        # bool is a subclass of int, so decide explicitly whether to allow it.
        if type(left) is not int or type(right) is not int:
            raise TypeError("left and right must be integers")
        return left + right


tool = AddTool()
print(tool.name, tool(left=4, right=7))
```

Expected output:

```text
add 11
```

For a real tool boundary, validate untrusted inputs, define timeouts and error mapping, and avoid executing arbitrary names or expressions. A normal class with `.run()` may be clearer when the interface has several operations, lifecycle requirements, or structured results. Middleware can also be a callable that accepts a request and returns a response, but this lesson focuses on the callable abstraction rather than a framework.

## 7. Injecting dependencies into callable behavior

Callables make useful dependencies because the consumer needs only a contract such as “call this to get the current time” or “call this to generate an ID.” Inject dependencies instead of reaching into global state; tests can provide fakes.

### 7.1 Clock and ID generator

```python
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class IngestRecord:
    record_id: UUID
    created_at: datetime
    payload: str


class RecordFactory:
    def __init__(
        self,
        *,
        clock: Callable[[], datetime],
        id_generator: Callable[[], UUID] = uuid4,
    ) -> None:
        self._clock = clock
        self._id_generator = id_generator

    def __call__(self, payload: str) -> IngestRecord:
        return IngestRecord(
            record_id=self._id_generator(),
            created_at=self._clock(),
            payload=payload,
        )


fixed_time = datetime(2026, 1, 2, tzinfo=timezone.utc)
factory = RecordFactory(clock=lambda: fixed_time, id_generator=lambda: UUID(int=1))
print(factory("batch-7"))
```

Expected output:

```text
IngestRecord(record_id=UUID('00000000-0000-0000-0000-000000000001'), created_at=datetime.datetime(2026, 1, 2, 0, 0, tzinfo=datetime.timezone.utc), payload='batch-7')
```

The lambdas are fine for local deterministic examples. If a callable instance must cross a process boundary or be persisted through pickle, prefer importable module-level functions or an importable callable class with picklable state.

## 8. Retry and rate limiting with injected time

Time-based policies are easy to make flaky when tests call `time.sleep`. Inject the clock and sleeper instead, and test with a fake clock that advances deterministically. The examples below intentionally keep policy simple; production retry systems also need budgets, cancellation, observability, and a policy for which exceptions are retryable.

### 8.1 Retry policy

This policy retries a function after selected exceptions, with a fixed delay. Both `clock` and `sleep` are injected. An optional elapsed-time budget limits whether another delay may be scheduled; it is not a hard timeout for an operation already running. The policy does not catch arbitrary exceptions by default.

```python
from collections.abc import Callable
from dataclasses import dataclass
from time import monotonic, sleep
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


@dataclass(frozen=True)
class RetryPolicy:
    attempts: int = 3
    delay_seconds: float = 0.0
    retry_on: tuple[type[Exception], ...] = (TimeoutError,)
    sleep: Callable[[float], None] = sleep
    clock: Callable[[], float] = monotonic
    max_elapsed_seconds: float | None = None

    def __post_init__(self) -> None:
        if self.attempts < 1:
            raise ValueError("attempts must be at least 1")
        if self.delay_seconds < 0:
            raise ValueError("delay_seconds must be non-negative")
        if self.max_elapsed_seconds is not None and self.max_elapsed_seconds < 0:
            raise ValueError("max_elapsed_seconds must be non-negative")

    def __call__(
        self,
        operation: Callable[P, R],
        /,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        started = self.clock()
        for attempt in range(1, self.attempts + 1):
            try:
                return operation(*args, **kwargs)
            except self.retry_on:
                if attempt == self.attempts:
                    raise
                elapsed = self.clock() - started
                if (
                    self.max_elapsed_seconds is not None
                    and elapsed + self.delay_seconds > self.max_elapsed_seconds
                ):
                    raise
                self.sleep(self.delay_seconds)
        raise AssertionError("unreachable")
```

The policy accepts an operation plus its positional and keyword arguments; `ParamSpec` keeps the callable signature relationship visible to static type checkers. The operation is invoked with the same arguments on each attempt. Avoid retrying non-idempotent writes unless the operation has an idempotency strategy; retries can duplicate side effects.

A deterministic fake clock can record sleeps and advance its current time:

```python
class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0
        self.sleeps: list[float] = []

    def __call__(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


clock = FakeClock()
policy = RetryPolicy(attempts=3, delay_seconds=0.25, sleep=clock.sleep, clock=clock)
calls = 0

def sometimes_fails() -> str:
    global calls
    calls += 1
    if calls < 3:
        raise TimeoutError("temporary failure")
    return "ok"

print(policy(sometimes_fails))
print(calls, clock.sleeps, clock.now)
```

Expected output:

```text
ok
3 [0.25, 0.25] 0.5
```

In a test module, avoid a module-level `global` counter where possible; a local mutable list or a small fake object is usually clearer. The `clock` and `sleep` dependencies are fake, so the example is deterministic. The optional budget controls whether the policy starts another retry after waiting; it does not interrupt an operation that runs too long. A hard timeout requires a separately designed cancellation or isolation strategy, which arbitrary synchronous Python calls cannot always be forcibly interrupted safely.

### 8.2 A deterministic token-bucket rate limiter

A token bucket allows bursts up to capacity and replenishes tokens over time. This implementation is intentionally single-threaded; it rejects a request when there is less than one token. Time is injected and must be monotonic.

```python
from dataclasses import dataclass, field
from collections.abc import Callable
from math import isfinite
from time import monotonic


@dataclass
class TokenBucket:
    capacity: float
    refill_per_second: float
    clock: Callable[[], float] = monotonic
    _tokens: float = field(init=False, repr=False)
    _last_time: float = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if not isfinite(self.capacity) or self.capacity < 1.0:
            raise ValueError("capacity must be finite and at least one token")
        if not isfinite(self.refill_per_second) or self.refill_per_second < 0:
            raise ValueError("refill_per_second must be finite and non-negative")
        now = self.clock()
        if not isfinite(now):
            raise ValueError("clock must return a finite timestamp")
        self._tokens = self.capacity
        self._last_time = now

    def __call__(self) -> bool:
        now = self.clock()
        if not isfinite(now):
            raise ValueError("clock must return a finite timestamp")
        if now < self._last_time:
            raise ValueError("clock must not move backwards")
        elapsed = now - self._last_time
        self._tokens = min(
            self.capacity,
            self._tokens + elapsed * self.refill_per_second,
        )
        self._last_time = now
        if self._tokens < 1.0:
            return False
        self._tokens -= 1.0
        return True
```

Example with a fake clock:

```python
class ManualClock:
    def __init__(self, start: float = 0.0) -> None:
        self.value = start

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError("seconds must be non-negative")
        self.value += seconds


clock = ManualClock()
limit = TokenBucket(capacity=2, refill_per_second=1, clock=clock)
print(limit(), limit(), limit())
clock.advance(1.0)
print(limit())
```

Expected output:

```text
True True False
True
```

For multi-threaded use, protect the entire refill-and-consume transition with a lock or use one limiter per thread. Locking only the final decrement is insufficient because reading time, refilling, and consuming form one logical state transition. For distributed rate limiting, an in-process object is not enough; use a shared atomic store or service.

## 9. Typing callable contracts

### 9.1 `Callable[[Input], Output]`

`collections.abc.Callable` (usable in annotations) and `typing.Callable` describe ordinary positional callable shapes. For example:

```python
from collections.abc import Callable


def run_batch(values: list[int], transform: Callable[[int], int]) -> list[int]:
    return [transform(value) for value in values]


class Increment:
    def __call__(self, value: int) -> int:
        return value + 1


print(run_batch([1, 2, 3], Increment()))
```

Expected output:

```text
[2, 3, 4]
```

`Callable[[int], int]` describes the call signature structurally: a callable accepting an integer and returning an integer. It does not require the implementation to be a function object. Callable instances, bound methods, and suitable `partial` objects can satisfy the contract.

### 9.2 `Protocol` for keyword-only parameters and richer contracts

Use a protocol when keyword-only parameters, overloads, or a named structural interface matter. Static type checkers can verify whether a class provides the required callable signature; Python does not enforce annotations at runtime.

```python
from typing import Protocol


class Event:
    def __init__(self, name: str) -> None:
        self.name = name


class EventHandler(Protocol):
    def __call__(self, event: Event, *, retry: bool = False) -> None: ...


class AuditHandler:
    def __init__(self) -> None:
        self.events: list[str] = []

    def __call__(self, event: Event, *, retry: bool = False) -> None:
        suffix = " (retry)" if retry else ""
        self.events.append(event.name + suffix)


def dispatch(handler: EventHandler, event: Event) -> None:
    handler(event, retry=True)


audit = AuditHandler()
dispatch(audit, Event("ingest"))
print(audit.events)
```

Expected output:

```text
['ingest (retry)']
```

The protocol captures the public contract without requiring inheritance. The default value is part of how callers may invoke the protocol, but a default value itself is not usually the central compatibility property; parameter names and kinds matter when callers use keywords.

### 9.3 Generic input/output types

Use `TypeVar` to preserve a relationship between input and output types. For a simple identity callable, `Callable[[T], T]` says the output type matches the input type.

```python
from collections.abc import Callable, Iterable
from typing import TypeVar

T = TypeVar("T")


def transform_all(values: Iterable[T], transform: Callable[[T], T]) -> list[T]:
    return [transform(value) for value in values]


class Identity:
    def __call__(self, value: T) -> T:
        return value


print(transform_all([3, 4, 5], Identity()))
```

Expected output:

```text
[3, 4, 5]
```

For transformations that change type, use separate type variables such as `Callable[[T], R] -> list[R]`. A generic class's exact syntax and inference depend on how its type parameters are declared; Python 3.12 supports the newer type-parameter syntax, while the `TypeVar` form above remains widely understood.

### 9.4 `ParamSpec` for decorators and signature-preserving wrappers

A wrapper that accepts arbitrary arguments and returns the wrapped function's result should preserve the parameter specification instead of reducing every function to `Callable[..., object]`. `ParamSpec` models the wrapped callable's parameter list; `TypeVar` models its result type.

```python
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def logged(fn: Callable[P, R]) -> Callable[P, R]:
    @wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"calling {fn.__name__}")
        return fn(*args, **kwargs)
    return wrapper


@logged
def combine(left: int, right: int, *, separator: str = ":") -> str:
    return f"{left}{separator}{right}"


print(combine(2, 5, separator="-"))
```

Expected output:

```text
calling combine
2-5
```

`ParamSpec` is especially useful for decorators and wrappers. A callable object with `__call__(*args: P.args, **kwargs: P.kwargs) -> R` can also preserve a wrapped signature, but a generic class-based decorator is more involved and should be implemented only when it buys meaningful state or lifecycle behavior. `functools.wraps` copies useful metadata and sets `__wrapped__`; it does not magically enforce runtime types.

## 10. Instance calls versus class construction

Two different call operations share the same surface syntax.

- **Calling an instance:** `worker(item)` uses the instance's type-level call behavior, often its class's `__call__` method.
- **Calling a class:** `Worker(config)` uses the metaclass's call behavior. For ordinary classes whose metaclass is `type`, the construction protocol coordinates `__new__` and `__init__` to produce an instance.

Conceptually, ordinary class construction follows `type.__call__`, which orchestrates allocation (`__new__`) and initialization (`__init__`). The exact details and customization points belong to Lesson 09 (`__init__`, `__new__`, and object construction). Do not confuse the `__call__` used by a class's metaclass with a method that makes each instance callable.

```python
class Worker:
    def __init__(self, label: str) -> None:
        self.label = label

    def __call__(self, item: str) -> str:
        return f"{self.label}: {item}"


worker = Worker("loader")   # class call: construct instance
result = worker("file.csv") # instance call: execute behavior
print(result)
```

Expected output:

```text
loader: file.csv
```

`callable(Worker)` is usually `True` even if `Worker` instances are not callable. Conversely, adding `__call__` to a class does not change the ordinary class-construction syntax. A custom metaclass can customize class calls, but that is a separate advanced design and rarely needed for routine pipeline code.

## 11. State, concurrency, and process boundaries

### 11.1 Is the callable pure or stateful?

A configured transform can be deterministic and effectively pure if it only reads immutable configuration. A counter, cache, retry tracker, or rate limiter mutates state and may return different results across calls. Document that distinction.

Questions to ask in review:

- Is state intentional, and is its lifetime clear?
- Can a caller inspect the state needed for debugging?
- Can two calls run at once on the same instance?
- Is state reset between batches or jobs?
- Is the instance shared across threads or processes?
- Is a call safe to repeat after a partial failure?

Avoid hiding essential state in surprising places. If `__call__` performs I/O, consumes a queue, increments metrics, or changes configuration, document the side effects and failure semantics.

### 11.2 Thread safety

The Global Interpreter Lock (GIL) is not a substitute for a concurrency contract. Compound state transitions can race, and free-threaded Python builds make assumptions based on interpreter-wide serialization even less reliable. If a stateful callable is shared by threads, use a lock around the complete invariant-preserving operation, use per-thread instances, or redesign it to be stateless. A lock does not make external side effects transactional.

```python
from threading import Lock


class SafeCounter:
    def __init__(self, start: int = 0) -> None:
        self._value = start
        self._lock = Lock()

    def __call__(self, step: int = 1) -> int:
        with self._lock:
            self._value += step
            return self._value

    @property
    def value(self) -> int:
        with self._lock:
            return self._value
```

A lock protects updates and reads made through this API. It does not protect code that directly mutates a public field outside the lock, which is one reason the example keeps state private. Do not hold locks while waiting on slow network or disk operations unless the design specifically requires serializing those operations.

### 11.3 Thread pools versus process pools

A `ThreadPoolExecutor` shares object references within a process; simultaneous calls may access the same instance. A `ProcessPoolExecutor` uses separate processes and generally needs submitted callables and arguments to be picklable under the selected multiprocessing start method. The worker receives serialized/copied state rather than a live shared Python object. Mutating a callable in a child process does not automatically mutate the parent's instance.

Prefer module-level functions or importable callable classes with picklable state for process work. Keep process entry points importable and guard application startup with `if __name__ == "__main__":` where required by the platform/start method. Test process behavior in a real importable module rather than relying only on notebook cells or REPL definitions.

## 12. Serialization and pickling

Pickle records references to importable functions/classes by qualified module/name and serializes object state according to its protocol. A top-level callable class instance is often picklable if:

1. Its class is importable by the receiving process under the same module path.
2. Its instance state is picklable.
3. It does not contain unpicklable resources such as open sockets, locks, generators, or certain client objects (unless custom state handling is implemented).

Lambdas and nested functions generally cannot be pickled by the standard `pickle` module because they are not importable by a stable module-level qualified name. Closures commonly capture state that standard pickle does not serialize as a standalone function. A `functools.partial` of a top-level picklable function can often be pickled if its bound arguments are picklable; this is not a blanket guarantee for all partials.

```python
import pickle
from functools import partial


def multiply(value: int, factor: int) -> int:
    return value * factor


class Multiply:
    def __init__(self, factor: int) -> None:
        self.factor = factor

    def __call__(self, value: int) -> int:
        return multiply(value, self.factor)


original = Multiply(4)
restored = pickle.loads(pickle.dumps(original))
print(restored(3))

bound = partial(multiply, factor=4)
restored_partial = pickle.loads(pickle.dumps(bound))
print(restored_partial(3))
```

Expected output, when run from a normal importable Python module:

```text
12
12
```

The class `Multiply` and function `multiply` must be defined at module scope in an importable module for robust cross-process use. The snippet may appear to work in some interactive environments but fail in notebooks, REPLs, or dynamically loaded contexts because importability differs. Do not unpickle untrusted data: pickle can execute arbitrary code during deserialization. Use a data format such as JSON for untrusted interchange, with explicit schema validation.

If the callable holds a lock, connection, or other resource, define an intentional lifecycle. Sometimes the right answer is to serialize only configuration via `__getstate__`/`__setstate__` or to reconstruct a fresh resource in the worker; sometimes the object should not be pickled at all.

## 13. Performance and benchmarking

Callable instances have a small amount of call machinery and often an ordinary Python method body; plain functions, bound methods, and callable instances can have different costs depending on Python version and workload. There is no universal performance winner. In hot loops, measure the actual pipeline with representative inputs and include allocation, I/O, data conversion, and key-function costs. Do not add a class for a speculative speed improvement.

A reproducible local microbenchmark can compare alternatives, but it is not a substitute for end-to-end profiling:

```python
from timeit import timeit


def add_one(value: int) -> int:
    return value + 1


class AddOne:
    def __call__(self, value: int) -> int:
        return value + 1


add_one_object = AddOne()
values = list(range(10_000))

function_seconds = timeit("[add_one(x) for x in values]", number=200, globals=globals())
object_seconds = timeit("[add_one_object(x) for x in values]", number=200, globals=globals())
print(f"function: {function_seconds:.4f}s")
print(f"callable object: {object_seconds:.4f}s")
```

The numbers depend on hardware, Python build/version, background load, and data shape. Run it locally several times, use a profiler for realistic workloads, and record the environment before drawing conclusions. This lesson does not assert a benchmark result.

## 14. Testing callable objects with pytest

Test behavior, configuration, state transitions, failure paths, and injected dependencies. Keep tests deterministic: do not make retry or rate-limit tests wait on real time. The following test module is self-contained and can be saved as `test_callable_objects.py`. It includes compact test-target implementations so the block runs on its own; in a production project, move the implementations into an importable module and import them in the tests instead of maintaining duplicate implementations. The test examples below cover retry behavior and token-bucket boundaries as well as basic callable state.

```python
# test_callable_objects.py
from dataclasses import dataclass, field
from typing import Callable, ParamSpec, TypeVar

import pytest

P = ParamSpec("P")
R = TypeVar("R")


class Counter:
    def __init__(self, start: int = 0) -> None:
        self.n = start

    def __call__(self, step: int = 1) -> int:
        self.n += step
        return self.n


class Scaler:
    def __init__(self, factor: float) -> None:
        self.factor = factor

    def __call__(self, value: float) -> float:
        return self.factor * value


@dataclass
class FakeClock:
    now: float = 0.0
    sleeps: list[float] = field(default_factory=list)

    def __call__(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


@dataclass(frozen=True)
class RetryPolicy:
    attempts: int
    delay_seconds: float
    sleep: Callable[[float], None]
    clock: Callable[[], float]
    max_elapsed_seconds: float | None = None
    retry_on: tuple[type[Exception], ...] = (TimeoutError,)

    def __post_init__(self) -> None:
        if self.attempts < 1:
            raise ValueError("attempts must be at least 1")
        if self.delay_seconds < 0:
            raise ValueError("delay_seconds must be non-negative")
        if self.max_elapsed_seconds is not None and self.max_elapsed_seconds < 0:
            raise ValueError("max_elapsed_seconds must be non-negative")

    def __call__(
        self,
        operation: Callable[P, R],
        /,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        started = self.clock()
        for attempt in range(1, self.attempts + 1):
            try:
                return operation(*args, **kwargs)
            except self.retry_on:
                if attempt == self.attempts:
                    raise
                elapsed = self.clock() - started
                if (
                    self.max_elapsed_seconds is not None
                    and elapsed + self.delay_seconds > self.max_elapsed_seconds
                ):
                    raise
                self.sleep(self.delay_seconds)
        raise AssertionError("unreachable")


def test_counter_state_transitions() -> None:
    counter = Counter(start=3)
    assert callable(counter)
    assert counter() == 4
    assert counter(3) == 7
    assert counter.n == 7


def test_scaler_is_repeatable_and_configuration_is_visible() -> None:
    scaler = Scaler(2.5)
    assert scaler.factor == 2.5
    assert scaler(4.0) == 10.0
    assert scaler(4.0) == 10.0


def test_non_callable_instance_raises_type_error() -> None:
    class Plain:
        pass

    item = Plain()
    assert not callable(item)
    with pytest.raises(TypeError, match="not callable"):
        item()  # type: ignore[operator]


def test_retry_uses_fake_sleep_and_retries_only_expected_error() -> None:
    clock = FakeClock()
    retry = RetryPolicy(attempts=3, delay_seconds=0.25, sleep=clock.sleep, clock=clock)
    calls = 0

    def flaky() -> str:
        nonlocal calls
        calls += 1
        if calls < 3:
            raise TimeoutError("temporary")
        return "ok"

    assert retry(flaky) == "ok"
    assert calls == 3
    assert clock.sleeps == [0.25, 0.25]
    assert clock.now == 0.5


def test_retry_passes_positional_and_keyword_arguments() -> None:
    clock = FakeClock()
    retry = RetryPolicy(attempts=2, delay_seconds=0.1, sleep=clock.sleep, clock=clock)

    def calculate(left: int, right: int, *, factor: int) -> int:
        return (left + right) * factor

    assert retry(calculate, 2, 3, factor=4) == 20
    assert clock.sleeps == []


@pytest.mark.parametrize(
    ("attempts", "delay_seconds", "message"),
    [(0, 0.1, "attempts must be at least 1"), (1, -0.1, "delay_seconds must be non-negative")],
)
def test_retry_rejects_invalid_configuration(
    attempts: int, delay_seconds: float, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        RetryPolicy(
            attempts=attempts,
            delay_seconds=delay_seconds,
            sleep=lambda _seconds: None,
            clock=lambda: 0.0,
        )


def test_retry_reraises_after_final_attempt() -> None:
    clock = FakeClock()
    retry = RetryPolicy(attempts=2, delay_seconds=0.1, sleep=clock.sleep, clock=clock)
    calls = 0

    def always_fails() -> str:
        nonlocal calls
        calls += 1
        raise TimeoutError("still down")

    with pytest.raises(TimeoutError, match="still down"):
        retry(always_fails)
    assert calls == 2
    assert clock.sleeps == [0.1]


def test_retry_does_not_swallow_unconfigured_exception() -> None:
    clock = FakeClock()
    retry = RetryPolicy(attempts=3, delay_seconds=0.1, sleep=clock.sleep, clock=clock)

    def invalid() -> str:
        raise ValueError("bad input")

    with pytest.raises(ValueError, match="bad input"):
        retry(invalid)
    assert clock.sleeps == []


def test_retry_elapsed_budget_uses_fake_clock_without_sleeping() -> None:
    clock = FakeClock()
    retry = RetryPolicy(
        attempts=3, delay_seconds=0.25, sleep=clock.sleep, clock=clock, max_elapsed_seconds=0.1
    )
    calls = 0

    def flaky() -> str:
        nonlocal calls
        calls += 1
        raise TimeoutError("temporary")

    with pytest.raises(TimeoutError, match="temporary"):
        retry(flaky)
    assert calls == 1
    assert clock.sleeps == []
    assert clock.now == 0.0


class ManualClock:
    def __init__(self, start: float = 0.0) -> None:
        self.value = start

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError("seconds must be non-negative")
        self.value += seconds


@dataclass
class TokenBucket:
    capacity: float
    refill_per_second: float
    clock: Callable[[], float]
    _tokens: float = field(init=False, repr=False)
    _last_time: float = field(init=False, repr=False)

    def __post_init__(self) -> None:
        import math

        if not math.isfinite(self.capacity) or self.capacity < 1.0:
            raise ValueError("capacity must be finite and at least one token")
        if not math.isfinite(self.refill_per_second) or self.refill_per_second < 0:
            raise ValueError("refill_per_second must be finite and non-negative")
        now = self.clock()
        if not math.isfinite(now):
            raise ValueError("clock must return a finite timestamp")
        self._tokens = self.capacity
        self._last_time = now

    def __call__(self) -> bool:
        import math

        now = self.clock()
        if not math.isfinite(now):
            raise ValueError("clock must return a finite timestamp")
        if now < self._last_time:
            raise ValueError("clock must not move backwards")
        elapsed = now - self._last_time
        self._tokens = min(
            self.capacity,
            self._tokens + elapsed * self.refill_per_second,
        )
        self._last_time = now
        if self._tokens < 1.0:
            return False
        self._tokens -= 1.0
        return True


def test_token_bucket_refills_from_injected_clock() -> None:
    clock = ManualClock()
    limit = TokenBucket(capacity=2, refill_per_second=1, clock=clock)
    assert [limit(), limit(), limit()] == [True, True, False]
    clock.advance(1.0)
    assert limit() is True


def test_token_bucket_rejects_capacity_below_one_and_non_finite_config() -> None:
    clock = ManualClock()
    with pytest.raises(ValueError, match="at least one token"):
        TokenBucket(capacity=0.5, refill_per_second=1, clock=clock)
    with pytest.raises(ValueError, match="finite"):
        TokenBucket(capacity=float("nan"), refill_per_second=1, clock=clock)
    with pytest.raises(ValueError, match="finite"):
        TokenBucket(capacity=1, refill_per_second=float("inf"), clock=clock)


def test_token_bucket_rejects_clock_moving_backwards() -> None:
    clock = ManualClock(start=5.0)
    limit = TokenBucket(capacity=1, refill_per_second=1, clock=clock)
    clock.value = 4.0  # Move the fake clock backwards to exercise the limiter contract.
    with pytest.raises(ValueError, match="must not move backwards"):
        limit()
```

Run the tests with:

```bash
python -m pytest -q test_callable_objects.py
```

Expected result for this exact test module after running it with pytest:

```text
13 passed
```

The test module uses a `FakeClock` with an injected `sleep` method. It never sleeps in real time. The `# type: ignore[operator]` comment marks the intentional runtime test of a non-callable instance; remove it if static type checking is not part of the test run. A separate static-analysis run may report deliberate type violations in negative tests, so keep runtime-negative tests isolated from strict type-checking targets when necessary.

### 14.1 Test checklist

- **Construction:** invalid configuration fails at the boundary, before pipeline processing begins.
- **Behavior:** expected output for representative and boundary inputs.
- **State:** repeated calls transition state exactly as specified.
- **Repeatability:** pure configured transformations return the same result for the same input.
- **Property-oriented checks:** for pure transforms, optionally use Hypothesis to assert invariants over generated inputs—for example, that `Clamp(0.0, 1.0)(value)` always remains in the inclusive interval `[0.0, 1.0]` for finite numeric inputs. Hypothesis is an optional development dependency, not part of the standard library.
- **Injected dependencies:** fake clock, sleeper, ID generator, or client is called as expected.
- **Failure semantics:** retryable and non-retryable errors are distinguished; final errors are propagated.
- **Concurrency:** if the class promises thread safety, test its invariant under concurrent use; a test alone does not prove all possible schedules safe.
- **Serialization:** round-trip only when it is a supported contract, and run it from an importable module.
- **Representations:** test stable public configuration in `repr` only if that representation is a documented interface; avoid brittle tests of memory addresses.

## 15. Exercises with solutions

Try each exercise before reading its solution. All examples use standard-library Python unless pytest is explicitly mentioned.

### Exercise 1 — Implement a step counter

Implement a callable `StepCounter(start=0)` where calling with `step` increments and returns the count. Reject negative steps.

**Solution:**

```python
class StepCounter:
    def __init__(self, start: int = 0) -> None:
        self.value = start

    def __call__(self, step: int = 1) -> int:
        if step < 0:
            raise ValueError("step must be non-negative")
        self.value += step
        return self.value


counter = StepCounter(2)
assert counter() == 3
assert counter(4) == 7
```

### Exercise 2 — Pick the simplest abstraction

For each case, choose a plain function, `partial`, closure, callable class, or named-method class, and explain why.

1. Convert a string to uppercase without configuration.
2. Apply a fixed tenant ID to an existing module-level `fetch_record(record_id, tenant_id)` function.
3. Count calls within one short local helper whose state never needs inspection.
4. A reusable validator has five configuration fields, structured diagnostics, and a documented representation.
5. A file exporter has `write()`, `flush()`, and `close()` operations.

**Solution:**

1. Plain function: no state or configuration is needed.
2. `functools.partial(fetch_record, tenant_id=...)` (or bind the argument according to the actual function signature): no new class is required.
3. Closure: private local state is sufficient; a class is also possible if state becomes more substantial.
4. Callable class or named-method class: choose `__call__` if it naturally fits the consumer's one-operation interface; choose `.validate()` if diagnostics and multiple operations are clearer as a named API.
5. Ordinary class with named methods: lifecycle operations are the point of the abstraction, so `__call__` would obscure the API.

### Exercise 3 — Make a validator injectable

Write a `MinimumLength` callable configured with a minimum number of characters. Whitespace counts as characters, and a non-string argument should raise `TypeError`.

**Solution:**

```python
class MinimumLength:
    def __init__(self, minimum: int) -> None:
        if minimum < 0:
            raise ValueError("minimum must be non-negative")
        self.minimum = minimum

    def __call__(self, value: str) -> bool:
        if not isinstance(value, str):
            raise TypeError("value must be str")
        return len(value) >= self.minimum


validate = MinimumLength(3)
assert validate("abc") is True
assert validate("  ") is False
```

### Exercise 4 — Add a deterministic retry policy

Implement a retry callable that accepts `operation: Callable[[], T]`, retries only `TimeoutError`, uses injected `sleep(seconds)`, and stops after a configured positive number of attempts. Test it with a fake sleeper and no real waiting.

**Solution:** The `RetryPolicy` in Section 8.1 is one complete implementation. The standalone tests in Section 14 show deterministic retry assertions; add a case where the operation succeeds on the second call, then assert one sleep and two calls. Do not assert elapsed wall-clock time; assert the exact requested delay values recorded by the fake.

### Exercise 5 — Type a handler protocol

Create a protocol for a callable that receives a string `event_id` and keyword-only `urgent: bool`, and returns a boolean. Write a function that accepts this protocol and invokes it with `urgent=True`.

**Solution:**

```python
from typing import Protocol


class Handler(Protocol):
    def __call__(self, event_id: str, *, urgent: bool = False) -> bool: ...


def handle(handler: Handler, event_id: str) -> bool:
    return handler(event_id, urgent=True)
```

Any object with a compatible `__call__` can satisfy this protocol structurally. Static type checking can validate the signature; the annotation itself does not perform runtime validation.

### Exercise 6 — Review a callable for concurrency

A `RateLimiter` stores `self.remaining` and decrements it in `__call__`. Multiple threads share the same instance. Identify the risk and propose two valid designs.

**Solution:** The decrement and any associated refill/eligibility logic form a shared state transition. Concurrent calls may observe inconsistent state or consume more capacity than intended. Either (a) guard the entire state transition with a `threading.Lock`, or (b) give each thread its own limiter if per-thread limits match the requirements. If the limit must apply across machines, use a shared service or datastore with an atomic operation; an in-process lock is insufficient.

### Exercise 7 — Pickling decision

A job queue needs to serialize a configured transform for execution in worker processes. Compare a lambda, a nested closure, a `partial` of a top-level function, and a top-level callable class.

**Solution:** Standard `pickle` generally cannot serialize lambdas and nested functions as importable functions. A `partial` of a top-level function can work when the function and bound arguments are picklable. A top-level callable class can work when its class is importable and its instance state is picklable. Test from the actual worker module and environment; never unpickle untrusted payloads.

## 16. Common mistakes and debugging guide

| Mistake | Why it fails | Better approach |
|---|---|---|
| Calling an instance that has no `__call__` | Raises `TypeError: 'X' object is not callable`. | Call its named method, or deliberately implement `__call__` on the class. |
| Confusing `Worker(config)` with `worker(item)` | One constructs an instance; the other invokes its behavior. | Name variables by role and draw the two-step flow. |
| Assuming `callable(obj)` proves valid invocation | Arguments may be wrong and the body may raise. | Specify and test the call signature and failure behavior. |
| Using a callable class for one trivial stateless function | Adds ceremony and another abstraction to maintain. | Start with a plain function or `partial`. |
| Hiding changing state behind function-like syntax | Call results become surprising and hard to reproduce. | Document state, expose safe diagnostics, and test transitions. |
| Retrying all exceptions | Can hide programming errors or repeat non-idempotent side effects. | Retry only known transient failures with a bounded policy. |
| Using real sleeps in retry/rate-limit tests | Slow, flaky tests depend on scheduler and wall-clock timing. | Inject a fake clock/sleeper and assert state changes. |
| Assuming the GIL guarantees a compound transition is safe | Multiple operations can interleave; builds and runtimes differ. | Lock the full invariant or avoid shared mutable state. |
| Assuming process workers share instance mutations | Process memory and serialization boundaries differ. | Return results explicitly or use a deliberate shared-state mechanism. |
| Assuming every callable instance is picklable | State or class/function importability may fail. | Test serialization in an importable module with realistic state. |
| Defining equality but leaving a mutable hash inconsistent | Dictionary/set invariants can be violated. | Prefer identity semantics or immutable equality-relevant state. |
| Using `Callable[..., Any]` for every callback | Loses signature information and hides interface mistakes. | Use a precise `Callable`, `Protocol`, `TypeVar`, or `ParamSpec`. |
| Treating annotations as runtime enforcement | Python normally does not validate annotated values automatically. | Validate untrusted input at runtime where required. |

## 17. Self-check

You should be able to answer these without looking back:

1. What makes `instance()` callable, and why is defining an instance attribute named `__call__` not a reliable substitute for a class-level special method?
2. Why can `callable(obj)` be `True` while `obj(wrong_argument)` still raises `TypeError`?
3. Explain the difference between `Counter()` and `Counter()()`.
4. When is `partial` simpler than a callable class? When does a callable class become justified?
5. How would you inject a clock, ID generator, or sleeper into a policy and test it without wall-clock waiting?
6. What does `Protocol` with `__call__` provide that can be awkward with a simple `Callable` alias?
7. Why is `ParamSpec` useful for decorators and wrappers?
8. What is the difference between instance invocation and class construction? Which lesson covers construction in detail?
9. What must be true for a callable instance to be picklable for process execution?
10. Why can a callable object with mutable state be unsafe to share across threads?
11. Why is a named method sometimes clearer than `__call__`?
12. What evidence would you collect before claiming one callable representation is faster?

## 18. Completion checklist

- [ ] I can explain instance `__call__`, `callable()`, and the non-callable-object `TypeError`.
- [ ] I can distinguish a class call (construction) from a callable-instance call.
- [ ] I can implement a configured, stateful callable and test its transitions.
- [ ] I can justify a function, `partial`, closure, callable class, or named-method class for a specific requirement.
- [ ] I can pass a callable instance to `map`, `sorted(key=...)`, and `Executor.submit` with the right signature.
- [ ] I can use `Callable`, `Protocol`, generics, and `ParamSpec` at the appropriate level.
- [ ] I can inject clocks and sleepers and test time-based policies deterministically.
- [ ] I can identify shared-state, thread-safety, process-boundary, and pickling risks.
- [ ] I can explain why a top-level callable class is often more portable than a lambda or nested closure for standard pickle-based workers.
- [ ] I can benchmark a hot path rather than relying on an unverified performance claim.
- [ ] I can write tests for configuration, repeatability, errors, and state transitions.
- [ ] I can explain why the callable abstraction is justified instead of overengineering a simple function.

## 19. Key takeaways

1. Defining `__call__` on a class gives its instances function-like invocation syntax; it does not eliminate the need for a clear contract.
2. A class is usually callable for construction even when its instances are not callable. Instance calls and class construction are distinct protocols.
3. Callable objects shine when behavior needs retained configuration, state, inspectability, or a reusable interface; plain functions, closures, and `partial` remain excellent choices.
4. Treat state, errors, concurrency, serialization, and side effects as part of the public design—not as implementation details hidden by parentheses.
5. Inject time and external dependencies to make policies testable. Use fake clocks and sleepers instead of real delays in unit tests.
6. Prefer precise typing contracts, deterministic tests, and measured performance over broad annotations, speculative optimization, or abstraction for its own sake.
