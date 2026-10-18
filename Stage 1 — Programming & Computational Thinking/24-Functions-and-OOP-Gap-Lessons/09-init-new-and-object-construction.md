# `__init__`, `__new__`, and Object Construction

> **Level:** beginner → advanced reasoning  
> **Target:** Python 3.12+  
> **Prerequisites:** functions and exceptions; classes, instances, `self`, class/instance attributes; basic type hints; pytest fundamentals; dataclasses and dependency injection at an introductory level.

## Learning objectives

By the end of this lesson, you should be able to:

- Trace what a normal `SomeClass(...)` call does, in the correct order.
- Explain the distinct jobs and return-value rules of `__new__` and `__init__`.
- Validate constructor inputs so a successfully constructed domain object satisfies its invariants.
- Use `__new__` for an immutable built-in subclass when value creation requires it—and recognize why ordinary classes rarely need an override.
- Implement subclass-friendly alternative constructors with `@classmethod`.
- Keep parsing, I/O, and resource acquisition at explicit boundaries rather than hiding them in `__init__`.
- Test successful and failed construction, factories, and relevant subclass behavior.
- Recognize the boundaries of this lesson: cooperative inheritance is developed in Lesson 10; metaclasses and detailed object lifecycle mechanics belong to later modules.

## 1. The central idea: construction has two responsibilities

For most application classes, you write `__init__` and leave `__new__` alone. The instance must be created before it can be initialized.

- **`__new__` creates or returns an object.** It receives the class being constructed as `cls` and must return an object.
- **`__init__` initializes an already-created object.** It receives that object as `self`, establishes its instance state, and must return `None`.

This distinction matters most when subclassing immutable built-ins such as `float`, `int`, `str`, and `tuple`, whose value is fixed during object creation.

### A first constructor

```python
class User:
    """A user identified by a non-empty name."""

    def __init__(self, name: str) -> None:
        if not name.strip():
            raise ValueError("name must not be empty")
        self.name = name.strip()


user = User("  Mira  ")
print(user.name)
```

Expected output:

```text
Mira
```

Line-by-line:

1. `class User:` creates a class object and binds the name `User` to it.
2. `User("  Mira  ")` calls the class object.
3. The normal construction protocol obtains an instance, then calls its initializer if the returned object is an instance of `User`.
4. `__init__` validates and normalizes the name, then stores it on that instance.
5. The expression `User(...)` evaluates to the created instance—not to the return value of `__init__`.

The class is responsible for its own domain invariant: once construction succeeds, `user.name` is non-empty and trimmed. Do not rely on every caller remembering to validate the name.

## 2. Ordinary construction: what happens when a class is called?

A useful conceptual trace for an ordinary class is:

```text
User("Mira")
    │
    ▼
class-call protocol (normally type.__call__)
    │
    ▼
User.__new__(User, "Mira")       # inherited if not defined here
    │ returns an object
    ▼
Is the returned object an instance of User?
    │ yes                         │ no
    ▼                             ▼
User.__init__(instance, "Mira")   skip User.__init__
    │
    ▼
return the instance from User(...)
```

This is a conceptual description of the normal path, not a complete implementation of every possible metaclass. A custom metaclass can change class-call behavior; that advanced topic belongs to the later metaclass module.

### Observe the order directly

```python
class Trace:
    def __new__(cls, value: int) -> "Trace":
        print(f"__new__: cls={cls.__name__}, value={value}")
        instance = super().__new__(cls)
        return instance

    def __init__(self, value: int) -> None:
        print(f"__init__: self={type(self).__name__}, value={value}")
        self.value = value


item = Trace(5)
print(item.value)
```

Expected output:

```text
__new__: cls=Trace, value=5
__init__: self=Trace, value=5
5
```

`super().__new__(cls)` delegates allocation to the next implementation, normally `object.__new__` for this simple class. `__new__` is normally treated as a static method by Python's special-method machinery; its conventional signature explicitly receives `cls`. `__init__` is an instance method and receives the newly created instance as `self`.

**Design rule:** the trace is important to understand, but do not add a `__new__` override merely to observe or customize ordinary construction. It adds complexity without a benefit in most application classes.

### What `object.__new__` and `object.__init__` do

For a straightforward user-defined class with no custom `__new__`, Python normally inherits `object.__new__`, which creates a new instance. If there is no custom initializer, `object.__init__` is the inherited initializer. The built-in implementations are intentionally minimal; they do not populate your domain attributes or validate your business rules.

Call `super().__new__(cls)` in an appropriate `__new__` override rather than hard-coding a base class. This keeps the construction path compatible with subclasses in common inheritance designs. Constructor chaining and cooperative multiple inheritance are treated in Lesson 10.

## 3. `__new__` and `__init__`: different jobs and signatures

| Concern | `__new__` | `__init__` |
|---|---|---|
| Main responsibility | Create or select an object | Initialize an existing object |
| Conventional signature | `def __new__(cls, ...) -> object` | `def __init__(self, ...) -> None` |
| Receives | The class being called | The object returned by `__new__`, if eligible |
| Must return | An object | Exactly `None` |
| Common use | Immutable built-in subclasses; specialized creation | Most validation and state assignment |
| Typical application-class use | Rare | Routine |

### Why `__init__` must return `None`

The return value of `__init__` is not the constructed object. Python already has the object from `__new__`. If `__init__` returns a non-`None` value, the class call raises `TypeError`.

Deliberately broken example—do not use in application code:

```python
class Broken:
    def __init__(self) -> int:
        return 42  # TypeError when Broken() is called


Broken()
```

Typical error text is:

```text
TypeError: __init__() should return None, not 'int'
```

Exact formatting can vary by Python version, but the rule does not: `__init__` must return `None`. The correct annotation is `-> None`, and a normal initializer reaches its end without a `return` statement or uses a bare `return`.

### Important special case: `__new__` returns a different kind of object

Python calls `__init__` for the class being called only if the object returned from `__new__` is an instance of that class (including an instance of a subclass). If `__new__` returns an unrelated object, that class's `__init__` is skipped and the class call expression returns the unrelated object.

```python
class Token:
    def __new__(cls, raw: str) -> object:
        if raw == "plain":
            return {"kind": "plain"}
        return super().__new__(cls)

    def __init__(self, raw: str) -> None:
        print("Token.__init__ called")
        self.raw = raw


plain = Token("plain")
print(type(plain).__name__)
other = Token("custom")
print(type(other).__name__, other.raw)
```

Expected output:

```text
dict
Token.__init__ called
Token custom
```

The first construction returns a `dict`, so `Token.__init__` does not run. The second returns a `Token`, so initialization runs. More precisely, when `__new__` returns an instance of the requested class or one of its subclasses, the class-call machinery dispatches initialization through the returned object's actual type. If a base class's `__new__` returns a subclass instance, that subclass's `__init__` may run with the original arguments; their signatures must therefore be compatible. The diagram above assumes the ordinary case where the returned object's type is exactly the requested class.

This behavior is a reason to be cautious: a constructor that sometimes returns unrelated types surprises callers and weakens the class's contract. Prefer a clearly named factory function when you intentionally want to return different kinds of results.

## 4. Validation and invariants during construction

An **invariant** is a condition that should remain true for every valid instance. Construction is the first point at which the class can establish it. Mutating methods must preserve it later too.

### A `Money` value object

This example stores amounts as integer minor units (for example, cents) to avoid introducing binary floating-point rounding into the core representation. It is intentionally small; real financial systems may need currency-specific scales, rounding rules, and domain policies.

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Money:
    """A monetary amount in minor units for a three-letter currency code."""

    minor_units: int
    currency: str

    def __post_init__(self) -> None:
        if isinstance(self.minor_units, bool) or not isinstance(self.minor_units, int):
            raise TypeError("minor_units must be an integer, not bool")
        if not isinstance(self.currency, str):
            raise TypeError("currency must be a string")
        normalized = self.currency.upper()
        if len(normalized) != 3 or not normalized.isalpha():
            raise ValueError("currency must be a three-letter alphabetic code")
        object.__setattr__(self, "currency", normalized)
```

Example:

```python
price = Money(1299, "usd")
print(price)
print(price.minor_units, price.currency)
```

Expected output:

```text
Money(minor_units=1299, currency='USD')
1299 USD
```

Important details:

- The dataclass-generated initializer assigns the supplied fields, then invokes `__post_init__`.
- `frozen=True` blocks ordinary attribute assignment after initialization, but it is not a security boundary and does not make arbitrary nested objects deeply immutable.
- `object.__setattr__` is used in `__post_init__` to normalize the field while satisfying the frozen dataclass's generated assignment behavior.
- The invariant is checked during construction, so a successfully constructed `Money` has normalized currency and an integer minor-unit amount.
- `bool` is a subclass of `int`, so the explicit boolean rejection prevents `True` from being accepted as one minor unit.

For a hand-written mutable class, validate before publishing or storing state where possible. Avoid calling overridable methods from `__init__`: a subclass override may execute before the subclass has established its own invariants. Lesson 10 explores this inheritance hazard further.

### Avoid partial initialization

A constructor should not leave an object that appears usable but violates its contract. If validation depends only on constructor inputs, validate first and then assign. If a step can fail after resources or state have been acquired, consider an explicit factory or context manager that can clean up failures.

Poor pattern:

```python
class Job:
    def __init__(self, job_id: str, retries: int) -> None:
        self.job_id = job_id
        self.retries = retries
        if retries < 0:
            raise ValueError("retries must be non-negative")
```

Although the failed instance is not returned by the ordinary class call, assigning before validation makes the construction logic harder to reason about, especially if later code introduces callbacks or side effects. Better:

```python
class Job:
    """A job with a non-empty identifier and non-negative retry count."""

    def __init__(self, job_id: str, retries: int = 0) -> None:
        normalized_id = job_id.strip()
        if not normalized_id:
            raise ValueError("job_id must not be empty")
        if isinstance(retries, bool) or not isinstance(retries, int):
            raise TypeError("retries must be an integer")
        if retries < 0:
            raise ValueError("retries must be non-negative")

        self.job_id = normalized_id
        self.retries = retries
```

In this simplified example, no partially initialized `Job` is returned if validation fails. Avoid storing `self` in a global registry, starting a thread, or invoking external callbacks before all required invariants are established; such actions can expose a partially initialized object to other code.

## 5. When should you override `__new__`?

The most useful introductory case is subclassing an immutable built-in. For immutable objects, the value cannot be assigned after allocation in the way ordinary mutable attributes can; the value is provided to the creation operation.

### `Celsius`, a `float` subclass

```python
import math
from typing import Self


class Celsius(float):
    """A finite Celsius temperature at or above absolute zero."""

    def __new__(cls, value: float) -> Self:
        numeric_value = float(value)
        if not math.isfinite(numeric_value):
            raise ValueError("temperature must be finite")
        if numeric_value < -273.15:
            raise ValueError("temperature cannot be below absolute zero")
        return super().__new__(cls, numeric_value)


room = Celsius(21.5)
print(room, isinstance(room, float), type(room).__name__)
try:
    Celsius(-300)
except ValueError as error:
    print(type(error).__name__, error)
```

Expected output:

```text
21.5 True Celsius
ValueError temperature cannot be below absolute zero
```

`float(value)` normalizes the input to the built-in numeric representation before `float.__new__` creates the value. The result remains a `Celsius` instance, while also being a `float`. `math.isfinite` rejects NaN and both infinities; the lower-bound check then enforces the physical constraint. This small example is appropriate for learning; production temperature models may prefer a separate immutable value object with explicit units and arithmetic rules.

Other specialized uses include controlled instance caching or flyweight designs, but these add complexity around repeated initialization, subclasses, thread safety, and testing. Prefer an explicit factory, module-level shared instance, or `functools.cache` on a factory when it expresses the intent more clearly.

### Why not put ordinary validation in `__new__`?

For ordinary mutable application classes, `__init__` is the conventional place to validate arguments and initialize attributes. Overriding `__new__` merely to validate a string, set a list, or assign fields makes the code less familiar without gaining anything. Use `__new__` when the object's creation/value semantics require it, not because it is available.

## 6. Alternative constructors with `@classmethod`

An alternative constructor gives a domain object another readable creation path without making the primary initializer handle every input format.

Use:

- `Config.from_dict(...)` when the caller already has a mapping.
- `Config.from_env(...)` when reading an explicitly supplied environment mapping.
- `Config.from_string(...)` or `parse(...)` for textual formats.
- A module-level factory or `Config.load(path)` when I/O belongs in a clear loading boundary.

### A validated `Config` with `from_dict`

```python
from collections.abc import Mapping
import tomllib
from typing import Self


class Config:
    """Validated application endpoint configuration."""

    def __init__(self, host: str, port: int) -> None:
        if not isinstance(host, str):
            raise TypeError("host must be a string")
        normalized_host = host.strip()
        if not normalized_host:
            raise ValueError("host must not be empty")
        if isinstance(port, bool) or not isinstance(port, int):
            raise TypeError("port must be an integer")
        if not 1 <= port <= 65535:
            raise ValueError("port must be between 1 and 65535")
        self.host = normalized_host
        self.port = port

    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> Self:
        """Build from an explicit environment-like mapping for testability."""
        host = env.get("APP_HOST", "localhost")
        port_text = env.get("APP_PORT", "5432")
        try:
            port = int(port_text)
        except ValueError as error:
            raise ValueError("APP_PORT must be an integer") from error
        return cls(host=host, port=port)

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> Self:
        """Build a validated config from a mapping of host and port."""
        try:
            host = data["host"]
            port = data["port"]
        except KeyError as error:
            raise ValueError(f"missing required config field: {error.args[0]}") from error
        if not isinstance(host, str):
            raise TypeError("host must be a string")
        if isinstance(port, bool) or not isinstance(port, int):
            raise TypeError("port must be an integer")
        return cls(host=host, port=port)

    @classmethod
    def from_toml(cls, text: str) -> Self:
        """Parse TOML text, then construct a validated config."""
        try:
            data = tomllib.loads(text)
        except tomllib.TOMLDecodeError as error:
            raise ValueError("invalid TOML config") from error
        return cls.from_dict(data)

    def __repr__(self) -> str:
        return f"Config(host={self.host!r}, port={self.port!r})"


config = Config.from_dict({"host": "warehouse.internal", "port": 5432})
from_env = Config.from_env({"APP_HOST": "staging.internal", "APP_PORT": "6432"})
from_toml = Config.from_toml('host = "toml.internal"\nport = 443')
print(config)
print(from_env)
print(from_toml)
```

Expected output:

```text
Config(host='warehouse.internal', port=5432)
Config(host='staging.internal', port=6432)
Config(host='toml.internal', port=443)
```

`from_env` accepts a mapping rather than reading `os.environ` implicitly. Production code can pass `os.environ` at the application boundary, while tests can pass a small deterministic dictionary. Parsing and conversion errors are explicit, and the primary constructor still enforces the port range and host invariant.

The design separates responsibilities:

1. `from_dict` understands the input representation and reports missing/wrongly typed fields.
2. `__init__` enforces the domain object's invariants regardless of how it was created.
3. `return cls(...)` preserves subclass support. A hard-coded `return Config(...)` would always create `Config`, even when a subclass calls the inherited factory.
4. `Self` communicates that the factory returns an instance of the class used to call it (or a subclass), which is the intended typing contract here.

Factories should not silently bypass validation. There should be one clear invariant boundary, usually the primary constructor or a shared validation routine used by all construction paths.

### Subclass-friendly factory behavior

```python
class SecureConfig(Config):
    """Configuration that also requires TLS to be enabled."""

    def __init__(self, host: str, port: int, *, tls: bool = True) -> None:
        super().__init__(host, port)
        if not tls:
            raise ValueError("TLS must be enabled")
        self.tls = tls


secure = SecureConfig.from_dict({"host": "db.internal", "port": 5432})
print(type(secure).__name__, secure.host, secure.tls)
```

Expected output:

```text
SecureConfig db.internal True
```

The inherited `from_dict` calls `cls(host=..., port=...)`; the subclass's `tls` parameter has a default, so it can be omitted. If a subclass changes constructor requirements incompatibly, inherited factories may no longer be suitable. Document or override the factory as part of the subclass API.

### Parsing is not the same as domain initialization

Keep a clean boundary between external representations and a valid domain object:

```text
text / mapping / environment / file
              │
              ▼
       parse and validate shape
              │
              ▼
       Config(host, port)
              │
              ▼
       valid domain instance
```

Parsing can fail because data is missing, malformed, or has the wrong representation. Domain validation can fail because values violate business rules. The same rule may be checked at both boundaries when that makes errors clearer, but the object itself must never rely exclusively on external callers to enforce its invariants.

## 7. Keep I/O and unpredictable side effects out of `__init__`

An initializer should usually be quick and predictable: validate inputs, normalize values, and assign state. Avoid hidden network requests, database connections, file reads, thread starts, expensive model loading, or retry loops in `__init__`.

Why:

- Construction becomes slow and can fail for environmental reasons unrelated to object validity.
- Unit tests require network/database fakes even when testing simple domain logic.
- Creating an object unexpectedly performs work, which complicates dependency injection and resource ownership.
- Retry and cleanup behavior is difficult to make explicit when hidden inside construction.

### Inject dependencies; make operations explicit

```python
from collections.abc import Callable


class ReportService:
    """Build reports using an injected loader, without loading during construction."""

    def __init__(self, load_rows: Callable[[], list[dict[str, object]]]) -> None:
        self._load_rows = load_rows

    def build(self) -> dict[str, int]:
        rows = self._load_rows()
        return {"row_count": len(rows)}


def example_loader() -> list[dict[str, object]]:
    return [{"id": 1}, {"id": 2}]


service = ReportService(example_loader)
print("constructed")
print(service.build())
```

Expected output:

```text
constructed
{'row_count': 2}
```

The dependency is passed in rather than created inside the service. The constructor stores it; `build()` performs the operation. A `Protocol` can be used instead of `Callable` when the collaborator needs a richer interface, but the core principle is the same.

### Resource-owning objects

For a file, database connection, or network client, make ownership and lifetime explicit. Common choices include:

- A factory such as `Client.connect(...)` that performs connection setup and returns a ready object.
- A separate `.open()` or `.connect()` operation with a documented state transition.
- A context manager: `with Client(...) as client:` where entry acquires the resource and exit releases it.
- An asynchronous factory or async context manager for asynchronous resources; `__init__` itself cannot be declared `async`.

Do not open a resource in `__init__` unless the abstraction deliberately defines construction as acquisition and has a clear, reliable cleanup contract. The context-manager protocol and full lifecycle design belong to their dedicated lessons.

A small wrapper can defer acquisition until `with` begins. The injected functions make the lifecycle observable in tests; a production implementation must also define timeout, retry, and cleanup-failure policy.

```python
from collections.abc import Callable
from types import TracebackType
from typing import Self


class ConnectionScope:
    """Acquire on context entry and release on exit."""

    def __init__(
        self,
        open_connection: Callable[[], object],
        close_connection: Callable[[object], None],
    ) -> None:
        self._open_connection = open_connection
        self._close_connection = close_connection
        self._connection: object | None = None

    def __enter__(self) -> Self:
        if self._connection is not None:
            raise RuntimeError("connection is already open")
        connection = self._open_connection()
        self._connection = connection
        return self

    @property
    def connection(self) -> object:
        if self._connection is None:
            raise RuntimeError("connection is not open")
        return self._connection

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        connection = self._connection
        self._connection = None
        if connection is not None:
            self._close_connection(connection)
```

Construction only stores dependencies. `__enter__` acquires the connection, and `__exit__` clears the internal reference before attempting cleanup, so the wrapper does not continue to advertise an open connection if closing raises. Returning `None` from `__exit__` means exceptions from the `with` body are not suppressed.

## 8. Constructor parameter design and mutable defaults

Avoid mutable default values such as `items=[]`. Default objects are evaluated once when the function is defined, not separately for each call.

Incorrect:

```python
class Queue:
    def __init__(self, items: list[str] = []) -> None:
        self.items = items
```

Both `Queue()` instances may refer to the same default list. Also, callers can mutate the list passed to the constructor and thereby change the queue's contents unless aliasing is intentional.

Safer:

```python
from collections.abc import Iterable


class Queue:
    """A queue that owns its initial list of items."""

    def __init__(self, items: Iterable[str] = ()) -> None:
        self.items = list(items)
```

The immutable empty tuple is a safe default, and `list(items)` creates a new list owned by the instance. This is a **shallow** copy: if items themselves are mutable objects, those elements are still shared. Decide explicitly whether shallow copying, deep copying, or shared ownership is appropriate; deep copying is not automatically correct for clients, file handles, locks, or other resources.

For many parameters, use keyword-only arguments (`*, timeout: float = ...`) or a configuration/parameter dataclass. Avoid constructors that accept many unrelated positional values whose order is easy to mix up.

## 9. Inheritance and `super()`: preview for Lesson 10

A subclass may inherit a base initializer, override it, or add constructor requirements. If it overrides `__init__`, it must deliberately initialize the base portion when the base contract requires it.

```python
class BaseJob:
    def __init__(self, job_id: str) -> None:
        if not job_id.strip():
            raise ValueError("job_id must not be empty")
        self.job_id = job_id.strip()


class TimedJob(BaseJob):
    def __init__(self, job_id: str, timeout_seconds: float) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        super().__init__(job_id)
        self.timeout_seconds = timeout_seconds
```

`super().__init__(job_id)` delegates base initialization. It does not create a second object; the same `self` is being initialized through the inheritance chain.

Constructor order matters. Avoid calling overridable instance methods from a base `__init__`, because a subclass override can run before the subclass has initialized its own attributes. Prefer direct private helpers, validation functions, or a factory/hook that runs after construction. Full cooperative inheritance and multiple-inheritance details are Lesson 10's scope.

### `__new__` and inheritance

When overriding `__new__`, use `cls` and delegate appropriately, commonly via `super().__new__(cls, ...)` for immutable built-in subclasses. Remember that `__new__` may return a subclass instance or an unrelated object; only an instance compatible with the class call receives that class's `__init__`. Do not duplicate `__new__`/`__init__` logic across a hierarchy without a specific need.

## 10. Copying, creating, and reconstructing are different

These operations can look similar but have different semantics:

- **Creating:** `Config(host="x", port=1234)` runs the ordinary class-call construction path.
- **Alternative construction:** `Config.from_dict(mapping)` parses/validates the representation and then constructs a valid instance.
- **Copying:** `copy.copy(obj)` asks Python's copy protocol to make a shallow copy; `copy.deepcopy(obj)` attempts recursive copying according to the copy protocol.
- **Reconstruction/serialization:** loading a stored representation may call a factory or constructor, while pickle/unpickle uses its own reduction/state protocol. Do not assume deserialization calls `__init__` or automatically revalidates your domain invariants.

If an object has important invariants, explicitly validate untrusted serialized data at the boundary and reconstruct through a trusted factory. Pickle is unsafe for untrusted input and belongs to the later serialization/security material. Advanced `__reduce__`, `__setstate__`, and copy hooks are intentionally not covered here.

## 11. Copying and reconstruction do not imply initialization

For an ordinary class using Python's default copy/reduction behavior, `copy.copy(obj)` creates a shallow copy without calling `__init__` again. A custom `__copy__` method can define different behavior, so this is a rule about the default protocol—not an absolute restriction on all classes.

```python
import copy


class InitTracked:
    init_calls = 0

    def __init__(self, value: int) -> None:
        type(self).init_calls += 1
        self.value = value


original = InitTracked(7)
duplicate = copy.copy(original)
print(original is duplicate, duplicate.value, InitTracked.init_calls)
```

Expected output:

```text
False 7 1
```

The duplicate has the copied state, but the initializer counter did not increase. Therefore, do not make correctness depend on `__init__` running during copy or unpickling. Use a deliberate copy/reconstruction protocol when invariants require more than a shallow state copy. Pickle is unsafe for untrusted input; validate external representations and reconstruct trusted domain objects through an explicit factory. Detailed `__reduce__`, `__setstate__`, and custom copy hooks belong to the later data-model/serialization lessons.

## 12. Tests for construction and invariants

Construction tests should verify more than “no exception occurred.” Check the contract that callers rely on:

1. Valid input creates the expected type and normalized attributes.
2. Invalid input raises a specific exception.
3. Each alternative constructor handles missing and malformed fields.
4. Factories return the subclass when subclass support is part of the API.
5. Constructor dependencies are stored/invoked at the intended time; no hidden I/O happens during object creation.
6. Invariants still hold after public operations, not just immediately after initialization.

Save the following as `test_construction.py` next to a module containing the definitions, or use the self-contained test block below as a reference. It is designed to run as a single pytest module.

```python
# test_construction.py
import math
from dataclasses import dataclass
from collections.abc import Callable
from types import TracebackType
import tomllib
import pytest
from typing import Self


class User:
    def __init__(self, name: str) -> None:
        normalized = name.strip()
        if not normalized:
            raise ValueError("name must not be empty")
        self.name = normalized


class Config:
    def __init__(self, host: str, port: int) -> None:
        if not isinstance(host, str):
            raise TypeError("host must be a string")
        host = host.strip()
        if not host:
            raise ValueError("host must not be empty")
        if isinstance(port, bool) or not isinstance(port, int):
            raise TypeError("port must be an integer")
        if not 1 <= port <= 65535:
            raise ValueError("port must be between 1 and 65535")
        self.host = host
        self.port = port

    @classmethod
    def from_env(cls, env: dict[str, str]) -> Self:
        host = env.get("APP_HOST", "localhost")
        try:
            port = int(env.get("APP_PORT", "5432"))
        except ValueError as error:
            raise ValueError("APP_PORT must be an integer") from error
        return cls(host, port)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Self:
        try:
            host, port = data["host"], data["port"]
        except KeyError as error:
            raise ValueError(f"missing required config field: {error.args[0]}") from error
        if not isinstance(host, str):
            raise TypeError("host must be a string")
        if isinstance(port, bool) or not isinstance(port, int):
            raise TypeError("port must be an integer")
        return cls(host, port)

    @classmethod
    def from_toml(cls, text: str) -> Self:
        try:
            data = tomllib.loads(text)
        except tomllib.TOMLDecodeError as error:
            raise ValueError("invalid TOML config") from error
        return cls.from_dict(data)


@dataclass(frozen=True, slots=True)
class Money:
    minor_units: int
    currency: str

    def __post_init__(self) -> None:
        if isinstance(self.minor_units, bool) or not isinstance(self.minor_units, int):
            raise TypeError("minor_units must be an integer, not bool")
        if not isinstance(self.currency, str):
            raise TypeError("currency must be a string")
        normalized = self.currency.upper()
        if len(normalized) != 3 or not normalized.isalpha():
            raise ValueError("currency must be a three-letter alphabetic code")
        object.__setattr__(self, "currency", normalized)


class PositiveInt(int):
    def __new__(cls, value: int) -> Self:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("value must be an integer")
        if value <= 0:
            raise ValueError("value must be positive")
        return super().__new__(cls, value)


class ReportService:
    def __init__(self, load_rows: Callable[[], list[dict[str, object]]]) -> None:
        self._load_rows = load_rows

    def build(self) -> dict[str, int]:
        return {"row_count": len(self._load_rows())}


class ConnectionScope:
    def __init__(
        self,
        open_connection: Callable[[], object],
        close_connection: Callable[[object], None],
    ) -> None:
        self._open_connection = open_connection
        self._close_connection = close_connection
        self._connection: object | None = None

    def __enter__(self) -> Self:
        if self._connection is not None:
            raise RuntimeError("connection is already open")
        self._connection = self._open_connection()
        return self

    @property
    def connection(self) -> object:
        if self._connection is None:
            raise RuntimeError("connection is not open")
        return self._connection

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        connection = self._connection
        self._connection = None
        if connection is not None:
            self._close_connection(connection)


class Celsius(float):
    def __new__(cls, value: float) -> Self:
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("temperature must be finite")
        if number < -273.15:
            raise ValueError("temperature cannot be below absolute zero")
        return super().__new__(cls, number)


def test_user_normalizes_name() -> None:
    assert User(" Ana ").name == "Ana"


def test_user_rejects_blank_name() -> None:
    with pytest.raises(ValueError, match="name must not be empty"):
        User("  ")


@pytest.mark.parametrize("port", [0, 65536, -1])
def test_config_rejects_invalid_port_range(port: int) -> None:
    with pytest.raises(ValueError, match="between 1 and 65535"):
        Config("localhost", port)


@pytest.mark.parametrize("port", [True, "5432", 1.5])
def test_config_rejects_non_integer_port(port: object) -> None:
    with pytest.raises(TypeError, match="port must be an integer"):
        Config("localhost", port)  # type: ignore[arg-type]


def test_from_dict_constructs_valid_config() -> None:
    config = Config.from_dict({"host": " db.local ", "port": 5432})
    assert (config.host, config.port) == ("db.local", 5432)


def test_from_dict_reports_missing_field() -> None:
    with pytest.raises(ValueError, match="missing required config field: port"):
        Config.from_dict({"host": "db.local"})


def test_from_dict_checks_field_type() -> None:
    with pytest.raises(TypeError, match="host must be a string"):
        Config.from_dict({"host": 3, "port": 5432})


def test_direct_config_constructor_checks_host_type() -> None:
    with pytest.raises(TypeError, match="host must be a string"):
        Config(3, 5432)  # type: ignore[arg-type]


def test_from_env_uses_injected_mapping() -> None:
    config = Config.from_env({"APP_HOST": "staging", "APP_PORT": "6432"})
    assert (config.host, config.port) == ("staging", 6432)


def test_from_env_rejects_malformed_port() -> None:
    with pytest.raises(ValueError, match="APP_PORT must be an integer"):
        Config.from_env({"APP_PORT": "not-a-port"})


def test_from_toml_parses_and_preserves_subclass() -> None:
    class LocalConfig(Config):
        pass

    config = LocalConfig.from_toml('host = "db.local"\nport = 5432')
    assert type(config) is LocalConfig
    assert (config.host, config.port) == ("db.local", 5432)


def test_from_toml_rejects_malformed_text() -> None:
    with pytest.raises(ValueError, match="invalid TOML config"):
        Config.from_toml("port =")


def test_money_normalizes_currency_and_rejects_invalid_minor_units() -> None:
    assert Money(1299, "usd").currency == "USD"
    with pytest.raises(TypeError, match="minor_units must be an integer"):
        Money(True, "USD")
    with pytest.raises(ValueError, match="three-letter"):
        Money(100, "US")


def test_celsius_is_float_and_rejects_invalid_values() -> None:
    assert isinstance(Celsius(20), float)
    assert float(Celsius(20)) == 20.0
    with pytest.raises(ValueError, match="below absolute zero"):
        Celsius(-300)
    for invalid in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(ValueError, match="finite"):
            Celsius(invalid)


def test_alternative_constructor_preserves_subclass() -> None:
    class LocalConfig(Config):
        pass

    result = LocalConfig.from_dict({"host": "localhost", "port": 8000})
    assert type(result) is LocalConfig


def test_new_returning_unrelated_object_skips_init() -> None:
    class MaybeToken:
        init_calls = 0

        def __new__(cls, as_mapping: bool):
            if as_mapping:
                return {"kind": "plain"}
            return super().__new__(cls)

        def __init__(self, as_mapping: bool) -> None:
            type(self).init_calls += 1

    assert MaybeToken(True) == {"kind": "plain"}
    assert MaybeToken.init_calls == 0
    token = MaybeToken(False)
    assert isinstance(token, MaybeToken)
    assert MaybeToken.init_calls == 1


def test_non_none_init_return_raises_type_error() -> None:
    class InvalidInitializer:
        def __init__(self) -> None:
            return 1  # type: ignore[return-value]

    with pytest.raises(TypeError, match="__init__.*should return None"):
        InvalidInitializer()


def test_copy_copy_does_not_rerun_ordinary_init() -> None:
    import copy

    class InitTracked:
        init_calls = 0

        def __init__(self, value: int) -> None:
            type(self).init_calls += 1
            self.value = value

    original = InitTracked(7)
    duplicate = copy.copy(original)
    assert duplicate is not original
    assert duplicate.value == 7
    assert InitTracked.init_calls == 1


def test_report_service_loads_only_when_build_is_called() -> None:
    calls: list[str] = []

    def loader() -> list[dict[str, object]]:
        calls.append("loaded")
        return [{"id": 1}]

    service = ReportService(loader)
    assert calls == []
    assert service.build() == {"row_count": 1}
    assert calls == ["loaded"]


def test_connection_scope_acquires_on_enter_and_closes_on_exit() -> None:
    events: list[object] = []
    connection = object()

    def open_connection() -> object:
        events.append("open")
        return connection

    def close_connection(value: object) -> None:
        events.append(("close", value))

    scope = ConnectionScope(open_connection, close_connection)
    assert events == []
    with scope as entered:
        assert entered.connection is connection
        assert events == ["open"]
    assert events == ["open", ("close", connection)]
    with pytest.raises(RuntimeError, match="not open"):
        _ = scope.connection


def test_connection_scope_closes_and_propagates_body_exception() -> None:
    events: list[object] = []
    connection = object()

    def open_connection() -> object:
        events.append("open")
        return connection

    def close_connection(value: object) -> None:
        events.append(("close", value))

    with pytest.raises(RuntimeError, match="body failed"):
        with ConnectionScope(open_connection, close_connection) as scope:
            assert scope.connection is connection
            raise RuntimeError("body failed")
    assert events == ["open", ("close", connection)]


def test_positive_int_validates_in_new() -> None:
    assert PositiveInt(3) == 3
    assert isinstance(PositiveInt(3), int)
    for invalid in (0, -1):
        with pytest.raises(ValueError, match="positive"):
            PositiveInt(invalid)
    for invalid in (True, 3.5):
        with pytest.raises(TypeError, match="integer"):
            PositiveInt(invalid)  # type: ignore[arg-type]
```

Run with:

```bash
python -m pytest -q test_construction.py
```

Expected result: all tests pass. The test module is self-contained; if you move the classes into a production module, import them from that module instead of redefining them in the test file.

### What these tests do not prove

A passing constructor test suite does not prove thread safety, safe serialization, or correctness for every input. Add tests for the invariants and failure modes that matter to your domain. For a factory that reads a file or environment, inject the source mapping or loader so tests can run without machine-specific state.

## 13. Common mistakes and their corrections

| Mistake | Why it is a problem | Better approach |
|---|---|---|
| Overriding `__new__` for a normal mutable class | Unnecessary protocol complexity | Implement `__init__` |
| Returning a value from `__init__` | Class call raises `TypeError` | Annotate `-> None`; initialize in place |
| Doing network I/O in `__init__` | Hidden latency and environmental failure | Explicit factory/`connect()`/context manager |
| Mutable constructor default `items=[]` | State leaks across calls | Use `None` or an immutable default; make ownership explicit |
| Factory returns `Config(...)` instead of `cls(...)` | Breaks subclass-friendly construction | Return `cls(...)` when subclass support is intended |
| Factory bypasses validation | Multiple creation paths produce inconsistent instances | Route all paths through invariant enforcement |
| `__new__` returns an unrelated object unexpectedly | Caller gets a surprising type; initializer is skipped | Prefer a clearly named factory for alternative result types |
| Constructor calls overridable methods | Subclass code can observe incomplete state | Keep initialization local; use post-construction hooks deliberately |
| Assuming unpickling calls `__init__` | Invariants may not be re-established | Validate external data and use explicit reconstruction factories |
| Treating annotations as runtime validation | Type hints do not automatically reject invalid values | Validate at runtime where input is untrusted or contract-critical |

## 14. Exercises and solutions

Work through each exercise before reading its solution. All examples target Python 3.12+.

### Exercise 1 — Build a validated `Account`

Implement `Account(owner, balance=0)` with these rules:

- Trim and require a non-empty owner.
- Balance must be a non-negative `int`; reject `bool`.
- `deposit(amount)` requires a positive integer and preserves the invariant.
- Do not use a mutable default.

**Solution:**

```python
class Account:
    """A simple account with a non-negative integer balance in minor units."""

    def __init__(self, owner: str, balance: int = 0) -> None:
        normalized_owner = owner.strip()
        if not normalized_owner:
            raise ValueError("owner must not be empty")
        if isinstance(balance, bool) or not isinstance(balance, int):
            raise TypeError("balance must be an integer")
        if balance < 0:
            raise ValueError("balance must be non-negative")
        self.owner = normalized_owner
        self.balance = balance

    def deposit(self, amount: int) -> None:
        if isinstance(amount, bool) or not isinstance(amount, int):
            raise TypeError("amount must be an integer")
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.balance += amount
```

### Exercise 2 — Implement `Config.from_string`

Accept strings in the exact form `host:port`. Reject missing parts and non-integer ports. Reuse `Config` validation rather than duplicating its rules.

**Solution:**

```python
from typing import Self


class Config:
    def __init__(self, host: str, port: int) -> None:
        host = host.strip()
        if not host:
            raise ValueError("host must not be empty")
        if isinstance(port, bool) or not isinstance(port, int):
            raise TypeError("port must be an integer")
        if not 1 <= port <= 65535:
            raise ValueError("port must be between 1 and 65535")
        self.host = host
        self.port = port

    @classmethod
    def from_string(cls, text: str) -> Self:
        host, separator, port_text = text.partition(":")
        if not separator or not host.strip() or not port_text:
            raise ValueError("expected non-empty host:port")
        try:
            port = int(port_text)
        except ValueError as error:
            raise ValueError("port must be an integer") from error
        return cls(host, port)
```

This simple grammar does not support IPv6 literals containing colons. A production parser should define and test its accepted grammar rather than silently pretending this format covers every hostname/address form.

### Exercise 3 — Implement `PositiveInt(int)`

Implement a positive integer subtype that rejects booleans and non-integers, as well as values less than or equal to zero. Validate in `__new__`, because the integer value is fixed at creation.

**Solution:**

```python
from typing import Self


class PositiveInt(int):
    def __new__(cls, value: int) -> Self:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("value must be an integer")
        if value <= 0:
            raise ValueError("value must be positive")
        return super().__new__(cls, value)
```

### Exercise 4 — Decide whether `__new__` is needed

You need a class `Temperature` with a mutable `label` attribute and a validated numeric `value`. Should you override `__new__`?

**Solution:** Usually not. Use `__init__` to validate and assign the ordinary instance attributes. Override `__new__` when the value/identity of the object must be established during creation, as with an immutable built-in subclass—not simply because a class needs validation.

### Exercise 5 — Make construction testable

A `ReportClient` downloads metadata during `__init__`. Refactor it so construction is deterministic and the download happens only when requested.

**Solution outline:** accept a downloader callable or protocol in `__init__`, store it, and invoke it from `load_metadata()`. Test with a fake downloader that records calls and returns a fixed result. Assert construction causes zero calls and the explicit operation causes one call. Keep retry, timeout, and resource lifetime policy in the operation/factory where they can be observed and tested.

### Exercise 6 — Test the invariant after construction

Extend `Account` with `withdraw(amount)`. Write tests for a successful withdrawal, a rejected withdrawal that would overdraw the account, and a check that a failed withdrawal leaves the balance unchanged.

**Solution:** validate `amount` and check `amount <= self.balance` before subtracting. Raise a specific exception such as `ValueError("insufficient funds")` before changing state. Tests should assert both the exception and the unchanged balance after failure.

### Exercise 7 — Keep connection acquisition explicit

Review the `ConnectionScope` example in Section 7 and the two regression tests for normal exit and body-exception exit. For a production wrapper, define what happens if opening or closing fails and whether re-entry is supported.

**Solution:** `__exit__` releases the acquired connection and returns `None`, so the body exception is not suppressed. The tests verify both cleanup and propagation. A close failure will propagate and can replace an exception from the body, so systems that need to preserve both failures should define an explicit exception-chaining policy.

## 15. Self-check

Answer without looking back:

1. Why does Python need a creation step before initialization?
2. What must `__new__` return? Under what condition is the class's `__init__` called?
3. Why does returning `self` or `42` from `__init__` violate the protocol?
4. Why is `__new__` appropriate for `Celsius(float)` but usually unnecessary for `Account`?
5. Why should `Config.from_dict` usually return `cls(...)` rather than `Config(...)`?
6. Where should network access occur if constructing a service must be fast and deterministic?
7. What risk does `items=[]` create in an initializer?
8. Why does a successful ordinary constructor call not guarantee safety if the object leaks `self` before initialization completes?
9. Why should serialized input be validated even if the class has a validating `__init__`?
10. Which details of `super()` and cooperative multiple inheritance are intentionally deferred to Lesson 10?

## 16. Summary

- A normal class call follows a class-call protocol that usually invokes `__new__`, then invokes `__init__` only when the returned object is an instance of the requested class.
- `__new__` creates/selects an object and returns it; `__init__` initializes an existing object and must return `None`.
- Most application classes need `__init__`, not a custom `__new__`.
- Immutable built-in subclasses are a canonical reason to customize `__new__`.
- Constructors should establish invariants and avoid hidden I/O or unpredictable side effects.
- Alternative constructors clarify parsing and creation paths; use `cls(...)` when subclass-preserving behavior is part of the contract.
- Make mutable ownership explicit, inject dependencies, and test successful construction, invalid input, factory behavior, and invariants.
- Copying, ordinary creation, and deserialization are distinct operations; do not assume every path runs `__init__`.

## Completion checklist

- [ ] I can trace the ordinary class-call sequence without confusing `__new__` and `__init__`.
- [ ] I know that `__init__` must return `None` and can explain the resulting `TypeError` otherwise.
- [ ] I can explain the unrelated-object return special case for `__new__`.
- [ ] I can implement a validated ordinary class without overriding `__new__`.
- [ ] I can justify `__new__` for an immutable built-in subclass.
- [ ] I can write a `@classmethod` factory that calls `cls(...)` and preserves subclass behavior.
- [ ] I can separate parsing/loading from domain invariant enforcement.
- [ ] I avoid mutable defaults and hidden resource acquisition in constructors.
- [ ] I can test valid construction, invalid input, alternative constructors, and invariants.
- [ ] I understand that inheritance chaining is continued in Lesson 10 and metaclass/lifecycle internals are later topics.
