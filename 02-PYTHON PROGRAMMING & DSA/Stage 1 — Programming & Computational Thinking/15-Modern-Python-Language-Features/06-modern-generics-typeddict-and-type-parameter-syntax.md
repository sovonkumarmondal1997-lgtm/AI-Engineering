# Modern Generics, `TypedDict`, and Type-Parameter Syntax

**Stage 1 · Module 1.15 — Modern Python Language Features · Lesson 06**

> **Version policy:** New examples target Python 3.12+. The version labels below identify when a feature entered the standard library or language. Some typing features were available earlier through `typing_extensions`; that does not make the syntax or import available on every older interpreter.

## Learning outcomes

By the end of this lesson, you should be able to design typed function and class APIs, describe dictionary-shaped data contracts, express generic relationships, narrow union types, inspect annotations responsibly, configure static analysis, and choose a runtime validation strategy when untrusted data crosses a boundary.

## 1. The mental model: types are contracts, not magic

Python typing has three interacting layers:

1. **Runtime values:** objects actually flowing through the program.
2. **Annotations:** metadata describing intended inputs, outputs, attributes, and relationships.
3. **Static analysis:** a type checker (for example, mypy or Pyright) interpreting the source and reporting likely contract violations before execution.

Python does **not** automatically enforce ordinary annotations. A function annotated `def add(x: int, y: int) -> int` can still be called with strings at runtime; whether that fails depends on its implementation. A type checker may reject that call, but the interpreter generally will not.

```python
# Python 3.12+
def add(x: int, y: int) -> int:
    return x + y

# A type checker should flag add("2", 3); Python itself does not
# reject the call merely because of the annotations.
```

Type checking is not a proof of program correctness. It cannot, by itself, establish that a remote service is available, that an integer is within a business limit, that a database row exists, or that a `dict` received from JSON has valid values. Static analysis is strongest when contracts are explicit and `Any` is kept at well-defined boundaries.

### Three distinct kinds of guarantees

| Mechanism | What it can establish | What it does not establish by itself |
|---|---|---|
| Annotation + static checker | Many incompatible calls, return types, and data-shape mistakes | Runtime validation of untrusted input |
| `TypedDict`, `Protocol`, generic type | Static shape or behavioral contract | Automatic runtime enforcement |
| Runtime validator (for example, explicit checks or Pydantic) | The checks actually implemented at runtime | Every property not covered by its schema/validators |

## 2. Built-in generic types and unions

### 2.1 Built-in collections

**Python 3.9 (PEP 585)** made built-in collection types directly subscriptable for annotations. Prefer these in modern code:

```python
# Python 3.12+
prices: list[float] = [1.25, 2.50]
counts: dict[str, int] = {"accepted": 12, "rejected": 2}
coordinates: tuple[float, float] = (10.0, 20.0)
records: tuple[str, ...] = ("a", "b", "c")  # any number of strings
```

`tuple[int, str]` means a two-element tuple whose first element is an `int` and second a `str`. `tuple[str, ...]` means zero or more strings. `list[int]` is invariant in the type system: a `list[Dog]` is not generally usable where `list[Animal]` is expected, because code could append a different `Animal`.

### 2.2 Choose the narrowest useful contract, not the narrowest container

Use `list[T]` if the implementation requires a mutable list and may mutate it. Use `Sequence[T]` when it only needs ordered access/iteration and should accept tuples or other sequence implementations. Use `Mapping[K, V]` when it reads key/value pairs but does not require mutation. These abstractions document what callers need to provide.

```python
from collections.abc import Mapping, Sequence

def average(values: Sequence[float]) -> float:
    if not values:
        raise ValueError("values must not be empty")
    return sum(values) / len(values)

def lookup_label(labels: Mapping[str, str], key: str) -> str | None:
    return labels.get(key)
```

`Sequence` and `Mapping` are useful contracts; they do not make an object immutable or validate its elements at runtime.

### 2.3 Union and nullable syntax

**Python 3.10 (PEP 604)** introduced `X | Y` for union annotations. `str | None` means a value may be a `str` or `None` and is the modern spelling of `Optional[str]`.

```python
# Python 3.12+
def parse_identifier(raw: str) -> int | None:
    try:
        return int(raw)
    except ValueError:
        return None
```

A union means *one of these types*, not “all of them.” Type checkers narrow a union after recognized tests such as `isinstance`, identity checks against `None`, or suitable user-defined narrowing functions.

## 3. `TypedDict`: a dictionary-shaped static contract

`TypedDict` describes expected keys and value types for a dictionary-like object. It is especially useful for JSON-like payloads and API DTOs when a dictionary is the desired runtime representation.

### 3.1 Required and optional keys

`TypedDict` entered the standard library in **Python 3.8**. `total=False` makes keys declared in that class body non-required. `Required` and `NotRequired` (standard library in **Python 3.11**, with earlier support through `typing_extensions`) let a schema mix required and optional keys precisely.

```python
from typing import NotRequired, TypedDict

class UserPayload(TypedDict):
    user_id: int
    email: str
    nickname: NotRequired[str]

class UserPatch(TypedDict, total=False):
    display_name: str
    active: bool
```

In `UserPayload`, `user_id` and `email` must be present according to the static contract; `nickname` may be omitted. In `UserPatch`, both declared keys may be omitted. `total=False` does not mean values can be `None`: presence and nullability are separate concerns. Use `str | None` if the value may explicitly be `None`.

`Required[T]` can mark an individual key as required even in a `total=False` class:

```python
from typing import Required, TypedDict

class PatchWithVersion(TypedDict, total=False):
    version: Required[int]
    comment: str
```

### 3.2 Static contract versus validation

This is a type-checker contract, not a parser. `TypedDict` does not validate an incoming dictionary at runtime and does not create a special dictionary subclass. Validate JSON, environment variables, database results, and external API responses before trusting them.

```python
from typing import TypedDict

class JobPayload(TypedDict):
    job_id: str
    attempts: int

def handle_job(job: JobPayload) -> None:
    print(job["job_id"], job["attempts"])

# A checker should flag a missing `attempts` key in a JobPayload literal.
# A raw dict decoded from JSON still needs runtime validation.
```

For `TypedDict` inheritance and mixed requiredness, keep required and optional key contracts explicit. Different checkers can have differences at the edges, so include a minimal checker test when a library relies on subtle structural assignability.

## 4. Useful typing building blocks

These constructs communicate different kinds of constraints; none is a universal runtime validator.

| Construct | Purpose | Version note |
|---|---|---|
| `Literal["open", "closed"]` | Restrict a value to specific literal values for static analysis | `Literal`: 3.8 |
| `Final` | Mark a name as not intended to be rebound | 3.8 |
| `ClassVar[T]` | Mark a class-level variable, not an instance field | 3.5+ |
| `Annotated[T, metadata]` | Attach metadata to a base type; consumers decide its meaning | 3.9 |
| `Callable[[A, B], R]` | Describe a callable's argument and return types | 3.5+ |
| `Iterator[T]` | Describe an iterator yielding `T` | 3.5+ |
| `Sequence[T]`, `Mapping[K, V]` | Describe read-oriented collection interfaces | `collections.abc` generic support in 3.9 |

```python
from typing import Annotated, ClassVar, Final, Literal

Mode = Literal["dry-run", "apply"]
DEFAULT_TIMEOUT: Final[float] = 5.0

class BatchConfig:
    supported_modes: ClassVar[tuple[Mode, ...]] = ("dry-run", "apply")
    timeout_seconds: Annotated[float, "must be positive"]

    def __init__(self, timeout_seconds: float) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.timeout_seconds = timeout_seconds
```

`Final` and `ClassVar` are primarily static declarations. `Annotated` does not enforce its metadata: a framework or application must explicitly interpret it. Here the constructor, not `Annotated`, enforces the positive timeout.

For callbacks, prefer a precise `Callable` signature over `Callable[..., Any]` where possible:

```python
from collections.abc import Callable, Iterator

def apply_each(values: Iterator[int], transform: Callable[[int], str]) -> list[str]:
    return [transform(value) for value in values]
```

Use `Iterable[T]` when any iterable is enough, `Iterator[T]` when the input must itself be an iterator, and `Sequence[T]` when indexed access or length is required. These are not interchangeable contracts.

## 5. PEP 695: modern type-parameter syntax (Python 3.12)

**PEP 695 (Python 3.12)** introduced a dedicated syntax for generic functions, classes, and aliases. It reduces global `TypeVar` boilerplate and scopes type parameters to the declaration.

### 5.1 Generic function, class, and alias

```python
from collections.abc import Callable, Sequence

def first[T](items: Sequence[T]) -> T:
    if not items:
        raise ValueError("items must not be empty")
    return items[0]

class Stack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()  # raises IndexError if empty

type Pair[T] = tuple[T, T]
type Handler[T] = Callable[[T], None]
```

The generic relationship is the key: `first([1, 2])` returns an `int`; `first(["a"])` returns a `str`. A type checker should reject a call where the sequence element type cannot satisfy the inferred `T`.

`type Pair[T] = ...` is the new **type alias statement**, not an ordinary assignment. It is valid in Python 3.12+ and not in Python 3.11 or earlier.

### 5.2 Bounds and constraints

A **bound** allows any subtype of a particular type. A **constraint** asks the type variable to resolve to one of a listed set of types. They model different contracts.

```python
from collections.abc import Hashable, Sequence

def unique[T: Hashable](items: Sequence[T]) -> set[T]:
    return set(items)

def normalize_text[S: (str, bytes)](value: S) -> S:
    # This example is illustrative only if normalization preserves S;
    # real transformations often return str for both inputs instead.
    return value.strip()  # str.strip and bytes.strip both preserve their type
```

The `T: Hashable` syntax is a bound. The `S: (str, bytes)` syntax is a constraint. With constraints, inference generally resolves to one of the listed constraint types; subclasses can be treated as the corresponding listed type rather than retaining their exact subclass type. Check the inferred type in your chosen checker when this distinction matters.

### 5.3 `ParamSpec` (`**P`) for callable signatures

A `ParamSpec` represents a callable's parameter list so a decorator can preserve the wrapped callable's call contract. The modern syntax uses `**P` in the parameter list.

```python
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")  # traditional spelling works on Python 3.10+
R = TypeVar("R")

def traced(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
```

The example uses the older `ParamSpec` declaration so it remains understandable on Python 3.10+. In Python 3.12+, the same concept can be expressed with PEP 695 syntax:

```python
from collections.abc import Callable
from functools import wraps

def traced[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
```

A type checker should preserve the wrapped function's parameter names/types and return type through this decorator. Runtime behavior is still the wrapper's actual behavior; `@wraps` helps introspection but does not enforce types.

### 5.4 `TypeVarTuple` (`*Ts`) for variadic type parameters

`TypeVarTuple` arrived in **Python 3.11**. In PEP 695 syntax, `*Ts` declares a variadic sequence of type parameters. It is useful for typing tuples and array-like structures whose type-level shape varies.

```python
# Python 3.12+
class Tensor[*Shape]:
    def __init__(self, shape: tuple[*Shape]) -> None:
        self.shape = shape

point: Tensor[int, int] = Tensor((10, 20))
```

This is a teaching example of a type-level shape; it does not validate numeric dimensions or guarantee mathematical tensor operations. `TypeVarTuple` support in particular operations varies among checkers and libraries. For pre-3.12 code, use `TypeVarTuple`/`Unpack` from `typing` where available (3.11+) or `typing_extensions` for supported older runtimes.

### 5.5 Older generic syntax

Before Python 3.12, generic functions/classes commonly used `TypeVar` and `Generic[T]`. This form remains useful when supporting older Python versions and is not obsolete.

```python
from collections.abc import Sequence
from typing import Generic, TypeVar

T = TypeVar("T")

def first_legacy(items: Sequence[T]) -> T:
    if not items:
        raise ValueError("items must not be empty")
    return items[0]

class StackLegacy(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()
```

Use PEP 695 syntax for new code whose minimum version is 3.12+. Use `TypeVar`/`Generic` when compatibility with older interpreters is a real requirement. Do not mix both styles in one declaration without a concrete reason.

## 6. `Self`, `@override`, and `@final`

- `Self` (standard library in **Python 3.11**) expresses that a method returns the current instance's concrete subtype, especially for fluent APIs.
- `@override` entered `typing` in **Python 3.12**. It tells a checker that a method is intended to override a base-class member; the checker can report a typo or incompatible signature. It does not change dispatch at runtime.
- `@final` (standard library in Python 3.8) marks a class as not intended to be subclassed or a method as not intended to be overridden. This is a static contract, not a runtime access-control mechanism.

```python
from typing import Self, final, override

class Query:
    def __init__(self) -> None:
        self._predicate: str | None = None

    def where(self, predicate: str) -> Self:
        self._predicate = predicate
        return self

class AnalyticsQuery(Query):
    @override
    def where(self, predicate: str) -> Self:
        return super().where(predicate)  # concrete return remains AnalyticsQuery

@final
class InternalToken:
    def __init__(self, value: str) -> None:
        self.value = value
```

The example omits constructor state initialization for brevity; a production class should initialize `_predicate` explicitly. A checker should reject `@override` when there is no compatible base member and should flag subclassing `InternalToken` under its configured rules. Older runtimes can use `typing_extensions` for many of these annotations/decorators.

## 7. `Protocol` versus abstract base classes

A **Protocol** describes a structural contract: an object can satisfy it by providing compatible members, without inheriting from the protocol. An **abstract base class (ABC)** provides nominal inheritance and can enforce abstract methods at instantiation time.

```python
from typing import Protocol
from abc import ABC, abstractmethod

class Reader(Protocol):
    def read(self, size: int = -1) -> bytes: ...

class BaseReader(ABC):
    @abstractmethod
    def read(self, size: int = -1) -> bytes:
        raise NotImplementedError

class MemoryReader:
    def read(self, size: int = -1) -> bytes:
        return b"payload"[:size] if size >= 0 else b"payload"

def consume(reader: Reader) -> bytes:
    return reader.read()

consume(MemoryReader())  # structurally compatible for a static checker
```

Use `Protocol` to type plugin interfaces, adapters, repositories, and third-party objects without requiring inheritance. Use an ABC when shared implementation, nominal identity, or runtime abstract-method enforcement is desired. A protocol is not automatically a runtime validator; `@runtime_checkable` only enables limited runtime structural checks, not full signature/type validation.

Generic protocols can express relationships such as a source yielding `T` or a sink accepting `T`. Variance rules still apply to the protocol's type parameters.

## 8. Variance: invariance, covariance, and contravariance

Variance describes how a generic type behaves when its type argument has a subtype relationship.

- **Invariant:** `Container[Dog]` is not a subtype of `Container[Animal]` or vice versa. Mutable `list[T]` is invariant because writing through a wider alias could break the list's promise.
- **Covariant:** if `Dog` is an `Animal`, then `Source[Dog]` can be used as a `Source[Animal]` when it only produces values of `T`.
- **Contravariant:** a consumer able to accept any `Animal` can also be used where a consumer of `Dog` is required; it accepts at least as broad a set of inputs.

```python
from collections.abc import Sequence

class Animal: ...
class Dog(Animal): ...

def inspect_animals(animals: Sequence[Animal]) -> None:
    for animal in animals:
        print(type(animal).__name__)

dogs: list[Dog] = [Dog(), Dog()]
inspect_animals(dogs)  # Sequence is covariant in its element type
# Passing list[Dog] to a parameter typed list[Animal] is not generally safe.
```

**Automatic variance inference (PEP 695, Python 3.12+)** allows type checkers to infer variance for new-style generic classes from how the parameter is used. In broad terms, a parameter used only in output positions can be covariant; input-only use can be contravariant; mutable or mixed use tends toward invariance. The exact inference model and edge cases are specified by PEP 695 and may expose checker differences. Legacy `TypeVar` declarations express variance explicitly with `covariant=True` or `contravariant=True`; ordinary `TypeVar` defaults to invariant.

A callable illustrates contravariance: a function that accepts any `Animal` can be used where a function accepting only `Dog` is needed, because it can handle every `Dog`. The reverse is unsafe. `Callable[[Animal], None]` can therefore be assignable to `Callable[[Dog], None]` under the typing rules.

Do not make a type parameter covariant merely to silence an error. Check whether the API genuinely only produces that type and cannot mutate through a wider reference.

## 9. `NewType`, `TypeAlias`, `cast`, and `TYPE_CHECKING`

- `NewType` creates a distinct static type for values that share a runtime representation. At runtime, calling a `NewType` returns the original value; it does not validate it.
- `TypeAlias` (Python 3.10) explicitly marks a traditional assignment as a type alias. In Python 3.12+, prefer the `type` statement for new parameterized aliases.
- `cast(T, value)` tells a checker to treat a value as `T`; it performs no runtime check or conversion.
- `TYPE_CHECKING` is `False` at runtime and `True` for static analyzers, enabling imports used only for annotations. In the example below, `from __future__ import annotations` postpones lookup at function definition time, so `Sequence` need not be imported at runtime. However, `get_type_hints(first_label)` can still fail unless `Sequence` is made available in the runtime namespace; future annotations do not make runtime resolution automatic.

```python
from __future__ import annotations

from typing import NewType, TYPE_CHECKING, TypeAlias, cast

UserId = NewType("UserId", int)
OrderId = NewType("OrderId", int)
JsonScalar: TypeAlias = str | int | float | bool | None

# This import is only for static analysis. The future import keeps the
# annotation from looking up Sequence while this module is imported.
if TYPE_CHECKING:
    from collections.abc import Sequence

def first_label(labels: Sequence[str]) -> str | None:
    return labels[0] if labels else None

def load_user(user_id: UserId) -> str:
    return f"user:{user_id}"

raw_id = 42
user_id = cast(UserId, raw_id)  # static assertion, not validation
load_user(UserId(raw_id))
# Expected static error (uncomment only in a checker-negative test):
# load_user(OrderId(raw_id))  # UserId and OrderId are distinct to the checker.
```

`NewType` does not prove the integer is positive or corresponds to a real user. Put domain validation at the boundary. Avoid unnecessary `cast`; prefer a check or a well-typed adapter that lets the checker infer the type.

### Accepted versus rejected calls (static-analysis example)

```python
from typing import NewType

UserId = NewType("UserId", int)
OrderId = NewType("OrderId", int)

def fetch_user(user_id: UserId) -> str:
    return f"user:{user_id}"

fetch_user(UserId(10))       # accepted
# fetch_user(OrderId(10))    # expected checker error: wrong NewType
# fetch_user(10)             # expected checker error: plain int is not UserId
```

The two negative calls are commented out so the example remains executable. To verify the expected diagnostics, place them in a dedicated negative type-checking fixture and assert the diagnostics with your pinned checker; do not infer checker behavior from runtime execution.

## 10. Type narrowing: `TypeGuard`, `TypeIs`, `assert_never`, and `assert_type`

A narrowing function gives a checker additional information after a condition succeeds.

- `TypeGuard[T]` (Python 3.10) says a true result permits narrowing to `T`. It can narrow to a target that is not a subtype of the input type (for example, `list[object]` to `list[str]`); it generally narrows only the true branch.
- `TypeIs[T]` (standard library in **Python 3.13**) requires `T` to be assignable to the input parameter type under the typing rules. Supported checkers narrow the true branch to the intersection with `T` and the false branch by excluding `T` where they can prove that. Use `typing_extensions` when supporting Python 3.12 or older; checker support and edge cases can vary by version.
- `assert_never(value)` (Python 3.11) marks a branch that should be unreachable; a checker can detect an unhandled union member.
- `assert_type(value, T)` (Python 3.11) asks a checker to verify the inferred type at that point. At runtime it returns the value; it is not a validator.

```python
from typing import assert_never, assert_type
from typing_extensions import TypeIs  # standard-library TypeIs requires Python 3.13+

def is_text(value: object) -> TypeIs[str]:
    return isinstance(value, str)

class Created: ...
class Deleted: ...
Event = Created | Deleted

def handle(event: Event) -> str:
    if isinstance(event, Created):
        return "created"
    if isinstance(event, Deleted):
        return "deleted"
    assert_never(event)

count = 3
assert_type(count, int)

raw: object = "ready"
if is_text(raw):
    # The checker narrows raw to str in this branch.
    print(raw.upper())
```

The import from `typing_extensions` is shown to keep this example runnable on Python 3.12 if that dependency is installed. On a Python 3.13+ only-standard-library example, import `TypeIs` from `typing`. If the event union gains a new member, a checker should report the final branch as no longer unreachable, subject to the checker's exhaustiveness support and configuration.

`TypeGuard` example:

```python
from typing import TypeGuard

def is_str_list(value: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(item, str) for item in value)

items: list[object] = ["a", "b"]
if is_str_list(items):
    # A checker narrows items to list[str] in this branch.
    print(",".join(items))
```

The implementation checks every item and is therefore meaningful. A dishonest `TypeGuard` can trick the checker; type guards must reflect a correct runtime predicate. Empty lists pass `all(...)`, which is correct because an empty list contains no non-strings.

## 11. `ReadOnly`, `Unpack`, and typed keyword arguments

`ReadOnly` for `TypedDict` keys arrived in **Python 3.13**. It says a key should not be mutated through that typed view; it does not make the underlying dictionary immutable at runtime. `Unpack` can expand a `TypedDict` schema into a function's keyword parameters (standard library in Python 3.11; earlier use via `typing_extensions`).

```python
from typing import NotRequired, ReadOnly, TypedDict, Unpack

class RequestOptions(TypedDict):
    request_id: ReadOnly[str]
    timeout: float
    trace_label: NotRequired[str]

def send_request(url: str, **options: Unpack[RequestOptions]) -> None:
    print(url, options["request_id"], options["timeout"])

send_request("https://example.invalid", request_id="r-1", timeout=2.0)
# A checker should reject an unknown keyword or a missing required request_id/timeout.
```

The `.invalid` top-level domain is reserved for examples; this function does not make a network request. Runtime Python accepts arbitrary keyword arguments unless the implementation checks them. The `Unpack` annotation alone does not reject an unknown keyword or validate values at runtime.

## 12. Overloads and precise public APIs

`@overload` lets a checker select a return type based on the argument signature. The overload declarations are for static analysis; a concrete implementation must still exist and behave consistently with them.

```python
from typing import overload

@overload
def decode(value: bytes) -> str: ...

@overload
def decode(value: str) -> bytes: ...

def decode(value: bytes | str) -> str | bytes:
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return value.encode("utf-8")

text_value = decode(b"hello")  # inferred str
bytes_value = decode("hello")  # inferred bytes
```

The first overload can raise `UnicodeDecodeError` for invalid UTF-8 bytes. Overloads do not remove runtime errors; document them and test them. Checkers can differ in overload resolution for complex literal, union, or generic cases, so test public APIs with the checker versions you support.

### Bounded generic repository/service design

A repository should preserve the relationship between the entity it stores and the entity it returns. A `Protocol` can describe only the operations a service needs, reducing coupling to a specific database implementation.

```python
from typing import Protocol

class HasId(Protocol):
    id: str

class Repository[T: HasId](Protocol):
    def get(self, key: str) -> T | None: ...
    def save(self, entity: T) -> None: ...

class UserRecord:
    def __init__(self, user_id: str, email: str) -> None:
        self.id = user_id
        self.email = email

def require_user[T: HasId](repository: Repository[T], user_id: str) -> T:
    entity = repository.get(user_id)
    if entity is None:
        raise LookupError(f"No entity found for id {user_id!r}")
    return entity
```

`Repository[UserRecord]` keeps `get` and `save` tied to `UserRecord` for static analysis. This contract says nothing about database transactionality, authorization, existence, or uniqueness. Those are runtime and system-level concerns. A type checker should also ensure a saved object satisfies the declared entity contract.

## 13. Runtime annotation inspection and Python 3.14

### 13.1 `get_type_hints`

`typing.get_type_hints(obj)` resolves annotations into useful runtime objects and, by default, strips `Annotated` metadata unless called with `include_extras=True`. Resolution may require the names used in annotations to exist in the correct global/local namespace. Forward references, conditional imports, and dynamically defined names can make evaluation fail.

```python
from typing import Annotated, get_type_hints

def process(amount: Annotated[int, "cents; non-negative"]) -> str:
    return str(amount)

hints = get_type_hints(process, include_extras=True)
assert "amount" in hints
```

Treat annotation evaluation as code execution in the relevant namespace: do not blindly evaluate annotations from untrusted plugins or arbitrary modules. A runtime framework that relies on annotations should document its resolution policy and test forward references, inheritance, and postponed/deferred annotations.

### 13.2 Version history for annotation evaluation

| Version | Relevant change |
|---|---|
| Python 3.9 | Built-in generic syntax such as `list[int]`; `Annotated` in `typing` |
| Python 3.10 | Union operator `X | Y`; `ParamSpec`; `TypeGuard`; `TypeAlias` |
| Python 3.11 | `Self`, `Required`/`NotRequired`, `TypeVarTuple`, `Unpack`, `assert_never`, `assert_type`, `dataclass_transform` |
| Python 3.12 | PEP 695 generic syntax and `type` aliases; `@override`; automatic variance inference for new-style generics |
| Python 3.13 | `TypeIs`, `ReadOnly` for `TypedDict` |
| Python 3.14 | Deferred annotation evaluation based on PEP 649, with supporting changes in PEP 749; `annotationlib` provides annotation formats for introspection |

`from __future__ import annotations` (available since Python 3.7) changes annotation storage/evaluation behavior to a stringized form. In Python 3.14, the default model changes to deferred evaluation (PEP 649), while the future import remains a compatibility mode with stringized annotations rather than simply becoming equivalent to the default. PEP 749 specifies supporting and compatibility details. Code should not assume `obj.__annotations__` always has the same representation across versions.

For advanced introspection on Python 3.14, the `annotationlib` module supports formats such as evaluated values, forward-reference-aware representations, and strings. Select the API and format based on whether values must be resolved. `get_type_hints` remains a high-level convenience, but it evaluates names and is not a sandbox.

```python
# Python 3.14+; guarded so the example also runs on Python 3.12/3.13.
import sys

def describe(value: int) -> str:
    return str(value)

if sys.version_info >= (3, 14):
    from annotationlib import Format, get_annotations

    as_values = get_annotations(describe, format=Format.VALUE)
    as_source_text = get_annotations(describe, format=Format.STRING)
    assert as_values["value"] is int
    assert as_source_text["value"] == "int"
```

`Format.VALUE` resolves annotations; `Format.STRING` is useful for display without resolving each annotation to its value. For unresolved forward references, `Format.FORWARDREF` can preserve unresolved names as `ForwardRef` objects. These formats are not a security boundary: annotation evaluation can execute code.

### 13.3 Framework implications

- **Dataclasses:** field discovery and annotation interpretation are affected by annotation resolution, but dataclasses do not generally validate field types on construction.
- **Pydantic:** uses annotations and its own validation machinery; behavior depends on Pydantic version, model configuration, and validators. Its runtime validation is separate from static type checking.
- **FastAPI:** inspects annotations for request/response schemas and dependency wiring. Forward references and import cycles can affect schema construction; test the framework version you deploy.
- **Custom frameworks:** avoid depending on undocumented annotation internals. Test under each supported Python version and prefer supported introspection APIs.

Do not assume every runtime consumer interprets `Annotated`, aliases, forward references, or deferred annotations identically.

## 14. `dataclass_transform` and declarative APIs

`dataclass_transform` (standard library in **Python 3.11**) tells static type checkers that a decorator, base class, or metaclass provides dataclass-like behavior. It does not generate methods by itself; the framework must implement that behavior at runtime.

```python
from typing import dataclass_transform

@dataclass_transform()
def model[T](cls: type[T]) -> type[T]:
    # A real framework would generate/attach init, repr, and other behavior.
    return cls

@model
class CustomerDTO:
    customer_id: int
    email: str
```

This minimal decorator is only a typing demonstration: it does **not** generate an `__init__` method. A checker may treat the class as dataclass-like based on the transform declaration, but constructing it with keyword arguments can fail at runtime because no initializer was generated. A production framework must ensure the static promise matches runtime behavior.

## 15. Data-contract decision table

| Option | Best fit | Runtime validation? | Main trade-off |
|---|---|---|---|
| `TypedDict` | JSON-like mappings with known keys; static API contracts | No, not by itself | Keeps `dict` representation; key presence is a static contract |
| `dataclass` | Internal records, domain objects, immutable/value-like structures | No general type validation by default | Standard library and low overhead; validation must be implemented |
| Pydantic model | Untrusted input, parsing/coercion, rich validation and errors | Yes, according to model/configuration | Dependency and runtime cost; coercion/strictness choices matter |
| Plain `dict[str, object]` | Truly dynamic key/value maps | No | Weak schema and more manual narrowing |
| `Protocol` | Structural behavior expected from collaborators | No, generally static only | Decouples implementations; runtime checks are limited if enabled |
| ABC | Nominal extension point with shared behavior or abstract methods | Abstract-method enforcement at instantiation | Requires explicit inheritance or registration patterns |

Choose the simplest contract that matches the boundary. A common architecture is: validate external JSON with a runtime schema; convert to a typed internal DTO/domain object; use protocols for service dependencies; keep static checks strict in new modules.

## 16. Practical case study: ingestion contract

Suppose an ingestion endpoint receives JSON-like records, validates them, normalizes them, and writes accepted records through a repository. Separate **shape**, **validation**, **domain behavior**, and **persistence**.

```python
from typing import NotRequired, TypedDict

class RawOrder(TypedDict):
    order_id: str
    amount_cents: int
    customer_note: NotRequired[str | None]

from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Order:
    order_id: str
    amount_cents: int
    note: str | None

def parse_order(raw: object) -> Order:
    # Validate an untrusted decoded value before treating it as a typed payload.
    if not isinstance(raw, dict):
        raise ValueError("order payload must be a JSON object")
    order_id = raw.get("order_id")
    amount = raw.get("amount_cents")
    if not isinstance(order_id, str) or not order_id:
        raise ValueError("order_id must be a non-empty string")
    # bool is a subclass of int, so explicitly reject it for numeric contracts.
    if isinstance(amount, bool) or not isinstance(amount, int) or amount < 0:
        raise ValueError("amount_cents must be a non-negative integer")
    note = raw.get("customer_note")
    if note is not None and not isinstance(note, str):
        raise ValueError("customer_note must be a string or None")
    return Order(order_id, amount, note)
```

The parser accepts `object`, checks that the decoded value is a dictionary, validates required values and optional metadata, then returns a frozen/slotted domain object. The `RawOrder` TypedDict remains useful for trusted internal call sites, but is not used to pretend the external value has already been validated. This example does not reject extra keys; add that policy explicitly if your contract requires it. Depending on requirements, use Pydantic or another runtime schema library at the edge, then map to a domain object.

### Example service contract

```python
from dataclasses import dataclass
from typing import NotRequired, Protocol, TypedDict

class RawOrder(TypedDict):
    order_id: str
    amount_cents: int
    customer_note: NotRequired[str | None]

@dataclass(frozen=True, slots=True)
class Order:
    order_id: str
    amount_cents: int
    note: str | None

class OrderRepository(Protocol):
    def save(self, order: Order) -> None: ...

def parse_order(raw: object) -> Order:
    if not isinstance(raw, dict):
        raise ValueError("order payload must be a JSON object")
    order_id = raw.get("order_id")
    amount = raw.get("amount_cents")
    note = raw.get("customer_note")
    if not isinstance(order_id, str) or not order_id:
        raise ValueError("order_id must be a non-empty string")
    if isinstance(amount, bool) or not isinstance(amount, int) or amount < 0:
        raise ValueError("amount_cents must be a non-negative integer")
    if note is not None and not isinstance(note, str):
        raise ValueError("customer_note must be a string or None")
    return Order(order_id, amount, note)

def ingest_order(payload: object, repository: OrderRepository) -> str:
    order = parse_order(payload)
    repository.save(order)
    return order.order_id
```

This function is easy to unit test with a fake repository. Its `object` input makes the runtime validation boundary explicit; `RawOrder` remains useful for already-validated internal mappings. Static typing checks the dependency's shape; tests and runtime logic establish behavior such as whether a save commits, retries safely, or is idempotent.

## 17. Type-checker workflow and packaging

### 17.1 mypy, Pyright, Pyrefly, and ty

Mypy, Pyright, Pyrefly, and ty are distinct tools. They share many typing conventions but may differ in inference, narrowing, overload resolution, plugin support, configuration, and support for newer PEPs. Do not claim that every checker produces identical results. Pin or document the checker and version used in CI; add small conformance tests for public typing APIs.

Example `mypy.ini` for a strict package (adjust for your codebase and pinned version):

```ini
[mypy]
python_version = 3.12
strict = True
warn_unused_ignores = True
show_error_codes = True
```

Example `pyrightconfig.json`:

```json
{
  "pythonVersion": "3.12",
  "typeCheckingMode": "strict",
  "reportUnknownMemberType": "error"
}
```

Configuration keys and diagnostics evolve. Validate configuration against the installed checker version rather than copying settings blindly.

### 17.2 `py.typed`, stubs, and `type: ignore`

- A distributable package that provides inline type information should include a `py.typed` marker as specified by PEP 561. Ensure the file is actually included in the built wheel.
- Use `.pyi` stub files when types cannot be expressed cleanly in implementation code or when typing third-party/native code. Keep stubs synchronized with runtime behavior.
- Prefer a narrow suppression such as `# type: ignore[arg-type]` over an unqualified ignore, where supported by the checker. Explain why it is necessary and remove it when the underlying issue is fixed.
- `cast()` and ignores suppress static uncertainty; neither changes runtime values.

### 17.3 Gradual typing for legacy code

1. Inventory entry points, high-risk transformations, and shared public APIs.
2. Add annotations at boundaries first: parsed payloads, service inputs/outputs, repository interfaces.
3. Replace `Any` and unstructured `dict` only where the real schema is understood; avoid pretending uncertain data is trusted.
4. Make new or touched modules stricter before imposing repository-wide strictness.
5. Run the checker in CI, track ignored errors, and use tests for runtime behavior that static typing cannot establish.
6. Upgrade the checker deliberately and review newly surfaced diagnostics rather than blanket-suppressing them.

## 18. Common errors and better alternatives

- **Mistake:** “The function says `int`, so runtime input must be an integer.”
  **Better:** validate untrusted inputs at the boundary; annotations are not enforcement.
- **Mistake:** use `list[T]` when the function only needs iteration.
  **Better:** choose `Iterable[T]`, `Sequence[T]`, or `Mapping[K, V]` based on operations required.
- **Mistake:** treat `TypedDict` as a validator.
  **Better:** validate external data explicitly or use a runtime schema library.
- **Mistake:** use `Any` to make errors disappear.
  **Better:** narrow `object`, define a protocol, or isolate dynamic values at an adapter.
- **Mistake:** use `cast` as a conversion.
  **Better:** call the actual constructor/converter or perform a runtime check.
- **Mistake:** annotate a decorator as `Callable[..., Any]` when it should preserve a signature.
  **Better:** use `ParamSpec` and a return type variable.
- **Mistake:** assume a checker feature is supported identically everywhere.
  **Better:** pin the tool and run a small checker-specific test suite.
- **Mistake:** rely on `__annotations__` being eagerly evaluated strings or types forever.
  **Better:** use supported introspection APIs and test across the supported Python matrix.

## 19. Exercises with hints and worked solutions

### Exercise 1 — choose a collection contract

Write a function that computes the maximum of numeric values and accepts both lists and tuples without mutating input. It should reject an empty sequence.

**Hint:** the contract needs length/iteration but not mutation.

**Solution:**

```python
from collections.abc import Sequence

def maximum(values: Sequence[float]) -> float:
    if not values:
        raise ValueError("values must not be empty")
    return max(values)
```

### Exercise 2 — describe a patch payload

Create a `TypedDict` where `id` is required, `enabled` is optional, and `description` is required but may be `None`.

**Hint:** key requiredness and value nullability are separate.

**Solution:**

```python
from typing import NotRequired, TypedDict

class FeaturePatch(TypedDict):
    id: str
    description: str | None
    enabled: NotRequired[bool]
```

### Exercise 3 — preserve a decorator's signature

Write a decorator that logs a call and returns exactly the wrapped function's result type.

**Hint:** use `Callable[P, R]` and `P.args`/`P.kwargs`.

**Solution (Python 3.12+):**

```python
from collections.abc import Callable
from functools import wraps

def logged[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
```

### Exercise 4 — static or runtime guarantee?

For each statement, classify it as primarily a static contract or a runtime guarantee:

1. A `TypedDict` has a required `order_id` key.
2. Incoming JSON contains a non-empty string `order_id`.
3. A `Protocol` declares `save(order: Order) -> None`.
4. A Pydantic model validates a field under the deployed model configuration.

**Solution:** 1 and 3 are static contracts; 2 needs runtime validation; 4 is runtime behavior implemented by the Pydantic model/configuration and should be tested.

### Exercise 5 — generic stack

Implement a generic stack using PEP 695 syntax and explain what happens when `pop()` is called on an empty stack.

**Solution:** use `class Stack[T]` with an internal `list[T]`, `push(item: T) -> None`, and `pop() -> T` returning `self._items.pop()`. Empty `pop()` raises `IndexError`; the annotation does not encode a non-empty precondition. If empty is expected, return `T | None` or provide a separate check/exception contract.

## 20. Final integrated exercise: typed ingestion boundary

Build an ingestion module that:

1. Defines a `TypedDict` payload with required `event_id`, `event_type`, and `occurred_at`, plus optional nullable metadata.
2. Uses `Literal` for supported event types.
3. Validates decoded JSON at runtime before treating it as the `TypedDict` contract.
4. Converts the payload into a frozen or slotted dataclass/domain object.
5. Exposes a generic repository `Protocol` that preserves the entity type.
6. Uses a `ParamSpec` decorator on one service method without losing the callable signature.
7. Adds at least one `@overload` where return type depends on input type.
8. Runs a static checker in CI and unit tests for invalid runtime payloads.

**Acceptance criteria:** no external value is trusted merely because of an annotation; the repository API preserves type relationships; type-checker suppressions are narrow and explained; and the README documents the minimum Python version and runtime validation boundary.

## 21. Final self-check

- [ ] I can explain the difference between static typing and runtime validation.
- [ ] I can select between `list`, `Sequence`, and `Mapping` based on required operations.
- [ ] I can describe requiredness and nullability separately in `TypedDict`.
- [ ] I can write a PEP 695 generic function, class, and alias.
- [ ] I can explain bounds, constraints, variance, `ParamSpec`, and `TypeVarTuple`.
- [ ] I know what `Self`, `@override`, `@final`, `Protocol`, `NewType`, and `cast` mean.
- [ ] I can use `TypeGuard`/`TypeIs` and exhaustive-union helpers appropriately.
- [ ] I understand `ReadOnly`, `Unpack`, overloads, and annotation inspection.
- [ ] I can explain Python 3.14's annotation-evaluation changes and test runtime consumers.
- [ ] I can configure a checker, package typing metadata, and introduce types gradually into legacy code.
