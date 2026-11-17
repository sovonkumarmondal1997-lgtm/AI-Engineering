# Lesson 05 — Properties and Computed Attributes

**Stage:** 1 — Programming & Computational Thinking  
**Module:** 11 — Advanced Python Data Model and Object Design  
**Baseline:** Python 3.12+ (version-specific behavior is called out)  
**Audience:** Learners progressing from Python fundamentals toward production Data Engineering and AI Engineering

## Scope and why this matters

A property lets a class expose an attribute-like API while controlling how a value is read, validated, computed, cached, or deleted. It allows a simple public attribute to gain validation or computation later without forcing callers to change `obj.value` into `obj.get_value()`. In data and AI systems, properties commonly expose validated configuration, derived measurements, metadata, and already-loaded state. They should not disguise slow I/O or surprising side effects.

This lesson follows the Basic → Intermediate → Advanced progression in the module roadmap. It introduces properties and computed attributes, setter/deleter behavior, private-by-convention backing fields, `cached_property`, inheritance, dataclasses and tuple-like records, descriptor mechanics, typing, performance, testing, common mistakes, and the roadmap self-check.

## Learning objectives

By the end, you should be able to:

1. Distinguish stored attributes, computed properties, and cached properties.
2. Use `@property`, `@name.setter`, and `@name.deleter` correctly.
3. Validate values through a public property, including during initialization.
4. Explain read-only property assignment and deletion errors.
5. Use `functools.cached_property`, invalidate its cache, and understand its storage and concurrency limitations.
6. Use properties with dataclasses, named tuples, frozen classes, inheritance, `Self`, and `Protocol`.
7. Explain why `property` is a data descriptor and when custom descriptors or `__getattr__` are more suitable.
8. Decide when an attribute-like property is appropriate and when a method communicates cost or side effects better.
9. Test both successful property access and failure paths through the public API.

## Prerequisite check

You should know classes, instance attributes, `__init__`, exceptions, decorators at a basic level, and type annotations. If decorators are new, read `@property` as a tool that transforms a getter function into a descriptor stored on the class; the following examples make this concrete.

---

## 1. Attributes: stored versus computed

A normal instance attribute stores a value in the instance, commonly in `obj.__dict__`:

```python
class User:
    def __init__(self, name: str) -> None:
        self.name = name

user = User("Asha")
print(user.name)
print(user.__dict__)
```

Expected output:

```text
Asha
{'name': 'Asha'}
```

A **computed attribute** derives a value from other state instead of storing a separate copy. A method can do this, but a property exposes it with attribute syntax:

```python
class Rectangle:
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    @property
    def area(self) -> float:
        return self.width * self.height

rectangle = Rectangle(3, 4)
print(rectangle.area)
rectangle.width = 5
print(rectangle.area)
```

Expected output:

```text
12
20
```

`area` is recalculated on each access. It is not stored in `rectangle.__dict__`; changing `width` changes the next result automatically.

### Why `@property` instead of `get_x()` and `set_x()`?

Python generally favors direct attribute syntax for ordinary state: `account.balance`, `temperature.celsius`. A property can later add validation or computation while preserving that syntax. Explicit methods remain appropriate when an operation is a command, has meaningful cost, needs arguments, or has side effects.

Use a property when reading it is unsurprising, quick, and attribute-like. Do not create a property solely to imitate a getter/setter convention when a plain attribute is sufficient.

## 2. `@property`, setters, and deleters

The `property` built-in can be constructed explicitly as `property(fget, fset, fdel, doc)`, but decorator syntax is usually more readable. The decorated getter function becomes the property descriptor on the class. The explicit form is useful when inspecting or assembling descriptors programmatically:

```python
def get_code(self) -> str:
    return self._code

def set_code(self, value: str) -> None:
    if not value.strip():
        raise ValueError("code cannot be empty")
    self._code = value.strip()

class Record:
    code = property(get_code, set_code, doc="Validated record code")

record = Record()
record.code = "  A-17  "
print(record.code, Record.code.__doc__)
```

Expected output:

```text
A-17 Validated record code
```

```python
class Account:
    def __init__(self, balance: float) -> None:
        self._balance = balance

    @property
    def balance(self) -> float:
        """The current account balance."""
        return self._balance

    @balance.setter
    def balance(self, value: float) -> None:
        if value < 0:
            raise ValueError("balance cannot be negative")
        self._balance = value

    @balance.deleter
    def balance(self) -> None:
        del self._balance

account = Account(100.0)
print(account.balance)
account.balance = 125.0
print(account.balance)
del account.balance
print(hasattr(account, "_balance"))
```

Expected output:

```text
100.0
125.0
False
```

The setter and deleter decorators refer to the same property name. Each returns an updated property descriptor; they do not create unrelated functions exposed as public attributes.

### Read-only properties and `AttributeError`

If a property has no setter, assigning to it raises `AttributeError`. A property without a deleter similarly rejects `del obj.property`. The error is raised by the descriptor protocol, even if the object has a writable `__dict__`.

```python
class Circle:
    def __init__(self, radius: float) -> None:
        self.radius = radius

    @property
    def diameter(self) -> float:
        return self.radius * 2

circle = Circle(2)
print(circle.diameter)
try:
    circle.diameter = 10
except AttributeError as exc:
    print(type(exc).__name__)
```

Expected output:

```text
4
AttributeError
```

A property is read-only through that public property interface; this does not make the whole object immutable. For example, `circle.radius` remains assignable unless you validate or otherwise restrict it.

## 3. Private-by-convention backing fields

A common pattern is `_value` for internal storage and `value` for the public property. A leading underscore is a convention: it signals “internal use” but does not enforce access control. Avoid using the same name for the property and backing field, which would recurse or collide.

```python
class Product:
    def __init__(self, sku: str) -> None:
        self._sku = sku

    @property
    def sku(self) -> str:
        return self._sku
```

The public API is `product.sku`; implementation details remain in `_sku`. Python does not have Java-style private instance fields by default. Name mangling with a double leading underscore serves a different purpose and is not a security boundary.

## 4. Complete validated `Temperature` example

Initialization should assign through `self.celsius`, not directly to `self._celsius`, so the same validation runs during construction and later updates. The example rejects booleans, non-numeric inputs, infinities, NaN, and temperatures below absolute zero. The annotation communicates intended use; runtime validation enforces it.

```python
from math import isfinite

class Temperature:
    """Temperature stored in Celsius with a validated public interface."""

    def __init__(self, celsius: float) -> None:
        self.celsius = celsius  # deliberately invokes the setter

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("celsius must be a real int or float, not bool")
        numeric_value = float(value)
        if not isfinite(numeric_value):
            raise ValueError("celsius must be finite")
        if numeric_value < -273.15:
            raise ValueError("below absolute zero")
        self._celsius = numeric_value

    @property
    def fahrenheit(self) -> float:
        """Return the Fahrenheit equivalent; calculated on every access."""
        return self._celsius * 9 / 5 + 32

    @property
    def kelvin(self) -> float:
        """Return the Kelvin equivalent; calculated on every access."""
        return self._celsius + 273.15

sample = Temperature(0)
print(sample.celsius)
print(sample.fahrenheit)
print(sample.kelvin)
sample.celsius = 100
print(sample.fahrenheit)
for invalid in (-300, float("nan"), True, "20"):
    try:
        sample.celsius = invalid  # type: ignore[assignment]
    except (TypeError, ValueError) as exc:
        print(type(exc).__name__)
```

Expected output:

```text
0.0
32.0
273.15
212.0
ValueError
ValueError
TypeError
TypeError
```

`fahrenheit` and `kelvin` are computed properties: they reflect the current Celsius value without needing invalidation logic. The setter writes to `_celsius`, not `self.celsius`, which avoids infinite recursion. The `type: ignore` comment is only for static type checkers in the deliberately invalid test loop; runtime validation is still exercised.

### Validation design notes

- Choose exceptions deliberately: `TypeError` for an input of the wrong kind, `ValueError` for a supported kind with an unacceptable value.
- Do not silently clamp invalid data unless clamping is part of the documented domain contract.
- If the domain accepts `Decimal` or other numeric types, expand the type policy intentionally; converting everything to `float` can lose precision.
- Validate at the public boundary. Do not rely on every caller to remember a separate validation method.

## 5. `cached_property`: compute once per instance

A normal property runs its getter each time. `functools.cached_property` computes on first access, stores the result under the same name in that instance's `__dict__`, and subsequent lookups read that stored value instead of invoking the descriptor again. This is a per-instance cache, not a global cache and not a shared mutable default.

```python
from functools import cached_property

class Report:
    def __init__(self, rows: list[dict[str, float]]) -> None:
        self.rows = rows
        self.computations = 0

    @cached_property
    def total(self) -> float:
        self.computations += 1
        return sum(row["amount"] for row in self.rows)

first = Report([{"amount": 10.0}, {"amount": 2.5}])
second = Report([{"amount": 7.0}])
print(first.total, first.computations)
print(first.total, first.computations)
print(second.total, second.computations)
print(first.__dict__["total"])
```

Expected output:

```text
12.5 1
12.5 1
7.0 1
12.5
```

The two instances have independent cached values. The first `first.total` lookup executes the getter and writes `first.__dict__["total"]`; the second lookup does not execute it again.

### Cache invalidation

A cached value becomes stale when its dependencies change. There are two common strategies:

1. Delete the cached attribute: `del obj.total`. The next access recomputes it.
2. Encapsulate dependency changes and invalidate the cache automatically in a setter or mutation method.

```python
from functools import cached_property

class Cart:
    def __init__(self, prices: list[float]) -> None:
        self._prices = list(prices)

    @property
    def prices(self) -> tuple[float, ...]:
        return tuple(self._prices)

    @prices.setter
    def prices(self, values: list[float]) -> None:
        if any(price < 0 for price in values):
            raise ValueError("prices must be non-negative")
        self._prices = list(values)
        self.__dict__.pop("total", None)  # invalidates, if cached

    @cached_property
    def total(self) -> float:
        return sum(self._prices)

cart = Cart([2.0, 3.0])
print(cart.total)
cart.prices = [10.0, 1.5]
print(cart.total)
```

Expected output:

```text
5.0
11.5
```

This setter copies the incoming list and exposes a tuple, so callers cannot mutate the internal list through the returned property. If instead the class exposed a mutable list directly, `cart.prices.append(...)` could change dependencies without invoking a setter; the cached total would remain stale. Prefer immutable views, controlled mutation methods that invalidate the cache, or a normal computed property when recomputation is cheap.

`del cart.total` also invalidates the cached value. Deleting it does not call a `cached_property`-specific deleter; it removes the instance entry, allowing the descriptor to compute again.

### `__dict__`, `__slots__`, and thread safety

- `cached_property` requires a writable instance `__dict__` because it stores the computed value there.
- A class using `__slots__` without a `__dict__` slot cannot use `cached_property`; access raises `TypeError` because it cannot cache the result. A class can explicitly include `"__dict__"` in `__slots__`, if the memory trade-off is acceptable.
- A normal `@property` does not itself require an instance dictionary; it can compute from slots.
- **Python 3.12 change:** before 3.12, `cached_property` used an undocumented lock to prevent concurrent first computations for the same property descriptor. That lock was removed in Python 3.12. Concurrent first access can therefore execute the getter more than once, potentially on different threads, before one value wins in the instance dictionary. Make the computation idempotent/thread-safe or provide your own synchronization if duplicate execution is unsafe. Do not depend on the old lock.

For work that must happen exactly once (for example, a non-idempotent external action), `cached_property` is the wrong synchronization primitive.

## 6. Properties with dataclasses, named tuples, and frozen classes

### Dataclasses: avoid a field/property name collision

A common trap is declaring a dataclass field and a property with the same name. The class-level property object can become the apparent default value for the generated initializer, causing surprising behavior. Keep backing storage and public property names distinct, and be explicit about initialization.

```python
from dataclasses import dataclass

@dataclass(init=False)
class UserProfile:
    _email: str

    def __init__(self, email: str) -> None:
        self.email = email  # validation runs through the setter

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        normalized = value.strip().lower()
        if "@" not in normalized:
            raise ValueError("email must contain @")
        self._email = normalized

profile = UserProfile("  USER@EXAMPLE.COM ")
print(profile.email)
print(profile)
```

Expected output:

```text
user@example.com
UserProfile(_email='user@example.com')
```

The dataclass still provides a generated `repr` based on `_email`; `init=False` tells it not to generate an initializer that bypasses the public property. The custom initializer deliberately assigns through `self.email`.

### `NamedTuple` / named tuple

`typing.NamedTuple` is designed around declared tuple fields. Avoid trying to replace a field with a property of the same name. For a tuple-compatible record that needs a computed property, subclass `collections.namedtuple` and add a differently named property:

```python
from collections import namedtuple

_PointBase = namedtuple("Point", ["x", "y"])

class Point(_PointBase):
    __slots__ = ()

    @property
    def magnitude_squared(self) -> int:
        return self.x * self.x + self.y * self.y

point = Point(3, 4)
print(point.x, point.y, point.magnitude_squared)
```

Expected output:

```text
3 4 25
```

The tuple's fields are immutable; the additional property computes from them without storing state. The same principle applies to `typing.NamedTuple`: add new computed names, and do not collide with tuple field names. Here is the `typing.NamedTuple` form explicitly:

```python
from typing import NamedTuple

class TypedPoint(NamedTuple):
    x: int
    y: int

    @property
    def magnitude_squared(self) -> int:
        return self.x * self.x + self.y * self.y

print(TypedPoint(5, 12).magnitude_squared)
```

Expected output: `169`.

### Frozen dataclasses

A frozen dataclass prevents ordinary assignment to its fields after initialization. It can still expose computed read-only properties:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Measurement:
    value: float
    unit: str

    @property
    def display(self) -> str:
        return f"{self.value:g} {self.unit}"

measurement = Measurement(12.5, "ms")
print(measurement.display)
try:
    measurement.value = 13.0
except (AttributeError, TypeError) as exc:
    print(type(exc).__name__)
```

Expected output on supported Python versions:

```text
12.5 ms
FrozenInstanceError
```

`dataclasses.FrozenInstanceError` is a subclass of `AttributeError`, so the broad exception handler catches it. Frozen is a programming contract implemented by generated methods, not a security boundary; avoid using `object.__setattr__` to bypass it outside specialized construction code.

## 7. Inheritance and property overrides

A subclass can override only the getter, or it can add a setter using the base property's descriptor. When extending a base property with a setter, use `@BaseClass.property_name.setter`; this creates a new property in the subclass with the base getter retained and the new setter attached.

```python
class BaseConfig:
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name

class UppercaseConfig(BaseConfig):
    @property
    def name(self) -> str:
        return super().name.upper()

class MutableConfig(BaseConfig):
    @BaseConfig.name.setter
    def name(self, value: str) -> None:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("name cannot be empty")
        self._name = cleaned

print(UppercaseConfig("alpha").name)
mutable = MutableConfig("alpha")
mutable.name = "  beta  "
print(mutable.name)
```

Expected output:

```text
ALPHA
beta
```

`UppercaseConfig` intentionally overrides the getter behavior. `MutableConfig` inherits `BaseConfig.name`'s getter and adds a setter. Note that `MutableConfig.__init__` inherits the base initializer, which assigns `_name` directly; if constructor inputs also require validation, validate in the base initializer or route construction through a validated property consistently.

## 8. Properties are data descriptors

A descriptor is an object whose type implements one or more of `__get__`, `__set__`, or `__delete__`. `property` is a built-in data descriptor (implemented in C in CPython). Descriptor lookup explains why a property can intercept `obj.x` even when `obj.__dict__` exists.

A simplified instance attribute lookup model is:

1. A data descriptor on the class takes precedence.
2. Otherwise, an instance dictionary entry can provide the value.
3. A non-data descriptor or ordinary class attribute may then provide it.
4. If normal lookup fails, `__getattr__` may be called.

This is a teaching model; Python's full lookup behavior includes class MRO and special cases. The next lesson examines descriptor and lookup order in depth.

```python
class Example:
    def __init__(self) -> None:
        self._value = 3
        self.__dict__["value"] = 999  # deliberately creates a conflicting entry

    @property
    def value(self) -> int:
        return self._value

print(Example().value)
```

Expected output:

```text
3
```

The property is a data descriptor, so it takes precedence over the `value` entry in the instance dictionary. Do not create conflicting entries like this in normal application code; it illustrates lookup mechanics only.

### Properties versus `__getattr__` versus custom descriptors

- **`@property`:** best for one class's named attribute with a getter and optional setter/deleter.
- **`__getattr__(self, name)`:** runs only after normal lookup fails. Useful for dynamic fallback behavior, proxy objects, or delegating unknown names; it is not the default tool for a single ordinary field.
- **Custom descriptor:** best when the same reusable behavior is needed across many attributes or classes, such as reusable validation, ORM fields, or managed values. Descriptors are stored on the class and receive the instance in `__get__`/`__set__`.

A property is itself a descriptor, so these are related tools rather than unrelated mechanisms. A small `__getattr__` example shows the key difference: it runs only when an attribute is otherwise missing.

```python
class SettingsProxy:
    def __init__(self, values: dict[str, str]) -> None:
        self._values = values

    @property
    def environment(self) -> str:
        return self._values.get("ENV", "development")

    def __getattr__(self, name: str) -> str:
        try:
            return self._values[name]
        except KeyError:
            raise AttributeError(name) from None

settings = SettingsProxy({"REGION": "ap-south-1"})
print(settings.environment)
print(settings.REGION)
try:
    print(settings.MISSING)
except AttributeError as exc:
    print(type(exc).__name__)
```

Expected output:

```text
development
ap-south-1
AttributeError
```

Do not implement a generic fallback like this when a small, stable public interface would be clearer. `__getattr__` should raise `AttributeError` for unknown names so introspection and normal Python attribute semantics continue to work.

## 9. Expensive properties, lazy loading, and API design

A property should normally feel like reading state. A property that opens a network connection, performs a database query, downloads a model, or scans a large dataset can surprise callers because `obj.value` hides the cost.

Reasonable property uses:

- cheap arithmetic derived from in-memory state;
- validation-backed state access;
- cached metadata that is already local and whose freshness rules are clear;
- a lazy parse or calculation when the API documents the one-time cost.

Prefer a method such as `load_records()`, `fetch_remote_schema()`, or `recompute_index()` when the action performs I/O, can fail due to external conditions, has side effects, or needs parameters. In ORM/configuration systems, lazy properties can be useful, but document when the value loads, how errors surface, how stale data is refreshed, and whether concurrent access is safe.

A normal property recomputes every time. A `cached_property` stores a result and can become stale. Neither is universally better: choose based on computation cost, dependency mutability, memory, freshness, and concurrency requirements.

## 10. Typing properties with `Self` and `Protocol`

`typing.Self` (Python 3.11+) expresses that a method returns the same concrete type as the instance; it is useful for fluent methods and factories, but is not needed for every property. A `Protocol` can specify the shape of an object by declaring a property. A protocol property without a setter describes read-only access for structural typing.

```python
from typing import Protocol, Self

class HasArea(Protocol):
    @property
    def area(self) -> float: ...

class ScaledValue:
    def __init__(self, value: float) -> None:
        self.value = value

    @property
    def doubled(self) -> float:
        return self.value * 2

    def scale(self, factor: float) -> Self:
        return type(self)(self.value * factor)

def describe_area(shape: HasArea) -> str:
    return f"area={shape.area:.1f}"

class Square:
    def __init__(self, side: float) -> None:
        self.side = side

    @property
    def area(self) -> float:
        return self.side * self.side

print(ScaledValue(3).doubled)
print(ScaledValue(3).scale(2).value)
print(describe_area(Square(4)))
```

Expected output:

```text
6
6
area=16.0
```

`Square` need not inherit from `HasArea`; it structurally satisfies the protocol because it provides a compatible read-only `area` property. `Self` is a static typing construct, not a runtime validation system. `Self` is available in `typing` from Python 3.11; for earlier Python versions, `typing_extensions.Self` is a common backport.

## 11. Class-level properties and Python version history

The combination of `@classmethod` above `@property` worked in Python 3.9 and 3.10. It was deprecated in Python 3.11 and removed in Python 3.13. Therefore, on the Python 3.12+ baseline, do not introduce this pattern as a new API: it emits a deprecation warning in 3.12 and no longer works as intended in 3.13.

For a class-level computed value, alternatives include:

- a class method such as `@classmethod def default_name(cls) -> str`, if call syntax is acceptable;
- a custom descriptor when `SomeClass.attribute` must return a computed class-level value;
- a metaclass property when the value genuinely belongs to class objects and metaclass behavior is justified.

Example of a custom descriptor that returns a value based on the class accessed:

```python
class ClassLabel:
    def __get__(self, instance: object, owner: type | None = None) -> str:
        target = owner if owner is not None else type(instance)
        return target.__name__.lower()

class DataJob:
    label = ClassLabel()

print(DataJob.label)
print(DataJob().label)
```

Expected output:

```text
datajob
datajob
```

The descriptor is a non-data descriptor because it defines `__get__` only. The example is intentionally simple; add `__set__` or `__delete__` only if the intended contract needs them. A metaclass property is another option, but it should be introduced only when the class-level semantics warrant the additional complexity.

## 12. Common mistakes and safer alternatives

### Mistake 1: recursive setter

Incorrect:

```python
@value.setter
def value(self, value: int) -> None:
    self.value = value  # recursively calls this setter
```

Correct: store into a distinct backing field such as `self._value = value` after validation.

### Mistake 2: bypassing validation in `__init__`

Assigning `self._celsius = value` directly in the initializer skips the public setter. Use `self.celsius = value` when constructor and later assignments must follow the same rules.

### Mistake 3: stale `cached_property`

If a cached value depends on mutable state, every supported mutation path must invalidate it. If you cannot reliably manage invalidation, use a regular property or immutable dependencies.

### Mistake 4: assuming cached mutable defaults are shared correctly

`cached_property` stores a separate result per instance, but if its getter returns a module-level list or a shared mutable object, the instances may still share that returned object. Construct mutable values per instance; never use a cached property as a disguised shared mutable default.

### Mistake 5: hidden network calls

A property that performs remote I/O makes ordinary attribute access slow and failure-prone. Prefer a clearly named method or explicitly document the lazy-loading behavior.

### Mistake 6: dataclass field and property share a name

Use `_field` for backing storage and a distinct public property name. Decide whether the generated initializer is appropriate; use `init=False` and a custom initializer when it must validate through the property.

### Mistake 7: expecting a property to make the object immutable

A read-only property only blocks assignment through that property name. Other mutable fields may still change. Use a frozen dataclass or another deliberate immutability design when the whole value object should be immutable.

## 13. Testing properties with pytest

Tests should use the public API, not only inspect private storage. Include successful reads, successful writes, invalid writes, computed values, read-only behavior, and cache invalidation. The following test module is self-contained; save it as `test_properties_lesson.py` and run `python -m pytest -q test_properties_lesson.py` after installing pytest.

```python
from functools import cached_property
from math import isfinite
import pytest

class Temperature:
    def __init__(self, celsius: float) -> None:
        self.celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("celsius must be an int or float, not bool")
        value = float(value)
        if not isfinite(value):
            raise ValueError("celsius must be finite")
        if value < -273.15:
            raise ValueError("below absolute zero")
        self._celsius = value

    @property
    def fahrenheit(self) -> float:
        return self._celsius * 9 / 5 + 32

class Report:
    def __init__(self, rows: list[dict[str, float]]) -> None:
        self.rows = rows
        self.calls = 0

    @cached_property
    def total(self) -> float:
        self.calls += 1
        return sum(row["amount"] for row in self.rows)

class SlotsWithoutDict:
    __slots__ = ("value",)

    @cached_property
    def doubled(self) -> int:
        return self.value * 2

class BaseConfig:
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name

class UppercaseConfig(BaseConfig):
    @property
    def name(self) -> str:
        return super().name.upper()

class MutableConfig(BaseConfig):
    @BaseConfig.name.setter
    def name(self, value: str) -> None:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("name cannot be empty")
        self._name = cleaned

def test_temperature_reads_and_computation() -> None:
    temperature = Temperature(0)
    assert temperature.celsius == 0.0
    assert temperature.fahrenheit == 32.0

def test_temperature_setter_updates_computed_property() -> None:
    temperature = Temperature(0)
    temperature.celsius = 100
    assert temperature.fahrenheit == 212.0

def test_temperature_rejects_below_absolute_zero() -> None:
    with pytest.raises(ValueError, match="below absolute zero"):
        Temperature(-300)

def test_temperature_rejects_nonfinite_values() -> None:
    with pytest.raises(ValueError, match="finite"):
        Temperature(float("nan"))

def test_failed_setter_does_not_replace_previous_value() -> None:
    temperature = Temperature(20)
    with pytest.raises(ValueError):
        temperature.celsius = -500
    assert temperature.celsius == 20.0

def test_temperature_rejects_wrong_types_and_bool() -> None:
    for value in (True, "10"):
        with pytest.raises(TypeError):
            Temperature(value)  # type: ignore[arg-type]

def test_read_only_property_rejects_assignment() -> None:
    temperature = Temperature(10)
    with pytest.raises(AttributeError):
        temperature.fahrenheit = 50  # type: ignore[misc]

def test_cached_property_computes_once_per_instance() -> None:
    report = Report([{"amount": 2.0}, {"amount": 3.0}])
    assert report.total == 5.0
    assert report.total == 5.0
    assert report.calls == 1

def test_cached_property_can_be_invalidated() -> None:
    report = Report([{"amount": 2.0}])
    assert report.total == 2.0
    report.rows.append({"amount": 8.0})
    del report.total
    assert report.total == 10.0
    assert report.calls == 2

def test_cached_property_requires_instance_dict() -> None:
    instance = SlotsWithoutDict()
    instance.value = 4
    with pytest.raises(TypeError):
        _ = instance.doubled

def test_property_getter_can_be_overridden() -> None:
    assert UppercaseConfig("alpha").name == "ALPHA"

def test_subclass_can_extend_base_property_with_validating_setter() -> None:
    config = MutableConfig("alpha")
    config.name = "  beta  "
    assert config.name == "beta"
    with pytest.raises(ValueError, match="name cannot be empty"):
        config.name = "   "
    assert config.name == "beta"
```

Expected test result on a compatible environment:

```text
12 passed
```

The final line is an expected result, not a claim that your machine has run the tests. Run the command to verify in your environment. A local execution record for this generated lesson is maintained separately in the private verification report, not in this learning file.

## 14. Graduated exercises

Attempt each exercise before reading its solution. Each solution is independently runnable.

### Exercise 1 — a validated `Person.age`

Create a class with a public `age` property. Accept non-negative integers, reject booleans and other types with `TypeError`, and reject negative values with `ValueError`. Ensure constructor validation uses the setter.

**Solution:**

```python
class Person:
    def __init__(self, age: int) -> None:
        self.age = age

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("age must be an integer")
        if value < 0:
            raise ValueError("age cannot be negative")
        self._age = value

person = Person(21)
print(person.age)
```

Output: `21`.

### Exercise 2 — cached report total

Implement a cached total for a report, then show that changing source rows does not change the cached value until the cache is invalidated.

**Solution:**

```python
from functools import cached_property

class Report:
    def __init__(self, rows: list[float]) -> None:
        self.rows = list(rows)

    @cached_property
    def total(self) -> float:
        return sum(self.rows)

report = Report([1.0, 2.0])
print(report.total)
report.rows.append(5.0)
print(report.total)  # stale cache by design
del report.total
print(report.total)  # recomputed after invalidation
```

Expected output:

```text
3.0
3.0
8.0
```

The cache is intentionally stale after mutating `rows`; `del report.total` invalidates it, so the next access returns `8.0`. In production, prefer encapsulating mutation and invalidation rather than asking callers to remember it.

### Exercise 3 — override a getter and extend a setter

Use a base `name` property, a subclass that displays the name in uppercase, and a different subclass that adds a validating setter while retaining the base getter. Refer to Section 7 and add tests for empty input.

### Exercise 4 — choose property or method

For each case, choose a property or method and explain why: (a) rectangle area from in-memory dimensions, (b) downloading a remote schema, (c) a cached count of local rows, (d) refreshing a remote token. Prefer properties for (a); (b) and (d) should normally be methods; (c) depends on cost, freshness, and whether cache invalidation is reliable.

## 15. Roadmap self-check — answers

1. **Why must `__init__` assign through the property rather than `_celsius`?** So constructor input follows the same validation and normalization rules as subsequent assignments. Directly writing `_celsius` bypasses the setter and can create invalid instances.
2. **What does `cached_property` store and where?** It computes the getter's result on first access and stores it as an entry under the property name in the instance's writable `__dict__`. Later accesses use that entry until it is deleted or otherwise changed.
3. **When is a method better than a property?** When access performs I/O, has side effects, is expensive or failure-prone, needs parameters, or represents an explicit action such as refreshing, fetching, or recomputing. Attribute syntax should not conceal a surprising operation.

## 16. Final engineering checklist

- [ ] Public attribute names and private-by-convention backing fields are distinct.
- [ ] Setter validation uses deliberate `TypeError` and `ValueError` semantics.
- [ ] `__init__` routes values through the public property when validation is required.
- [ ] Read-only properties reject assignment and deletion as intended.
- [ ] Computed properties remain correct when dependencies change.
- [ ] Cached properties have documented dependencies, invalidation, memory, and concurrency behavior.
- [ ] `cached_property` is used only when instances have a writable `__dict__` (or an explicit `__dict__` slot).
- [ ] No code depends on the pre-3.12 `cached_property` lock.
- [ ] Dataclass fields do not collide with property names; frozen semantics are understood.
- [ ] Inheritance preserves the intended getter and setter behavior, and both are covered by tests.
- [ ] A property is chosen over a method only when attribute syntax communicates cost and side effects honestly.
- [ ] Tests cover valid access, writes, invalid values, computed results, read-only behavior, cache invalidation, getter overriding, and inherited-property setter extension.
- [ ] Python 3.11+ `Self` usage and the Python 3.13 class-level-property compatibility change are understood.

## Summary

Properties preserve an attribute-style API while adding validation, computation, or controlled mutation. Use a distinct backing field and avoid recursive setters. Use `cached_property` only when caching is worth the memory and freshness complexity; invalidate it whenever dependencies change, and remember that Python 3.12 removed its former per-property lock. Keep properties predictable, test public behavior, and use methods when an operation is expensive or has side effects.
