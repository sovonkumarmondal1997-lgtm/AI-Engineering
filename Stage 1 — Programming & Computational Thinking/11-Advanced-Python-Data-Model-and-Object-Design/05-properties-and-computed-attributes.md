# Lesson 05 — Properties and Computed Attributes

**Stage 1 — Programming & Computational Thinking**  
**Module 11 — Advanced Python Data Model and Object Design**  
**Target version:** Python 3.12+  
**Level:** Beginner → intermediate → advanced  
**Primary goal:** Design attribute-style APIs that preserve invariants, expose computed state, and make caching behavior explicit and correct.

---

## 1. Learning outcomes

By the end of this lesson, you should be able to:

1. Explain why Python usually favors attribute access and `@property` over Java-style `get_x()` / `set_x()` methods.
2. Implement read-only properties, setters, and deleters.
3. validate values through the public property, including during `__init__`.
4. Distinguish stored state from computed state and identify when a method is clearer than a property.
5. Use `functools.cached_property` and explain its storage, invalidation, `__slots__`, and concurrency trade-offs.
6. Explain that `property` is a descriptor and recognize where descriptors fit into attribute lookup.
7. Avoid recursion, stale caches, hidden I/O, mutable-default mistakes, and dataclass/property initialization pitfalls.
8. Test properties through the public API, including both successful and failure paths.
9. Apply these ideas to data-engineering objects such as validated configuration, batch metadata, and report summaries.

---

## 2. Why properties matter

Imagine an API that starts with a plain attribute:

```python
class Temperature:
    def __init__(self, celsius: float) -> None:
        self.celsius = celsius
```

At first, `celsius` is just a name stored on the instance. Later, the class needs to reject impossible values, normalize input, or calculate a related value. If callers already use `temperature.celsius`, a property lets the implementation add behavior without forcing callers to switch to `temperature.get_celsius()`.

A property is therefore an **API-preserving boundary** between how callers use an attribute and how the class stores or computes it.

Properties are useful for:
- enforcing an invariant whenever a value changes;
- exposing a value derived from other state;
- presenting a read-only view;
- maintaining compatibility while internal representation evolves;
- lazily computing a value when first accessed, if that behavior is clearly documented.

A property is not automatically the right choice for every calculation. If access is expensive, performs I/O, changes state, or has important failure modes, a method often communicates intent better.

---

## 3. Basic concepts: stored, computed, and validated attributes

### 3.1 A normal instance attribute

```python
class Job:
    def __init__(self, name: str) -> None:
        self.name = name

job = Job("daily-orders")
assert job.name == "daily-orders"
job.name = "hourly-orders"
assert job.name == "hourly-orders"
```

A plain attribute is simple and often best when no additional behavior is needed. Do not add a property merely because properties are available.

### 3.2 A computed property

A computed property derives its result from other state:

```python
class Rectangle:
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    @property
    def area(self) -> float:
        return self.width * self.height

rectangle = Rectangle(3, 4)
assert rectangle.area == 12
rectangle.width = 5
assert rectangle.area == 20
```

`area` is not stored separately. It is calculated when read, so it cannot become stale merely because `width` changes. This is ideal when the calculation is cheap.

### 3.3 A validated property

A setter can enforce a rule at the point where the value enters the object:

```python
class Temperature:
    def __init__(self, celsius: float) -> None:
        self.celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("celsius must be a real numeric value")
        if value < -273.15:
            raise ValueError("temperature cannot be below absolute zero")
        self._celsius = float(value)

    @property
    def fahrenheit(self) -> float:
        return self._celsius * 9 / 5 + 32

temperature = Temperature(20)
assert temperature.fahrenheit == 68
temperature.celsius = 0
assert temperature.fahrenheit == 32
```

The public property name is `celsius`; `_celsius` is the internal storage convention. The leading underscore communicates “internal implementation detail,” not a security boundary.

**Important:** `__init__` assigns through `self.celsius`, not `self._celsius`, so construction uses the same validation rule as later updates.

---

## 4. `@property`, setters, and deleters

### 4.1 The getter

`@property` turns a method into attribute-style access:

```python
class Circle:
    def __init__(self, radius: float) -> None:
        self._radius = radius

    @property
    def radius(self) -> float:
        return self._radius
```

Callers write `circle.radius`, not `circle.radius()`. The method body executes during attribute access.

### 4.2 The setter

The setter is declared by decorating a method with the property object:

```python
class Account:
    def __init__(self, balance: int) -> None:
        self.balance = balance

    @property
    def balance(self) -> int:
        return self._balance

    @balance.setter
    def balance(self, value: int) -> None:
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError("balance must be an integer")
        if value < 0:
            raise ValueError("balance cannot be negative")
        self._balance = value

account = Account(100)
account.balance = 125
assert account.balance == 125
```

The setter protects the invariant regardless of whether the caller is `__init__`, another method, or external code.

### 4.3 The deleter

A deleter controls `del obj.attribute`:

```python
class OptionalLabel:
    def __init__(self, label: str | None) -> None:
        self.label = label

    @property
    def label(self) -> str | None:
        return self._label

    @label.setter
    def label(self, value: str | None) -> None:
        if value is not None and not isinstance(value, str):
            raise TypeError("label must be a string or None")
        self._label = value

    @label.deleter
    def label(self) -> None:
        self._label = None

item = OptionalLabel("priority")
del item.label
assert item.label is None
```

Deletion does not have to remove the backing attribute. Here, it resets the state. Choose semantics that are clear and document them. If deletion would violate an invariant, omit the deleter or raise an appropriate exception.

### 4.4 Read-only properties and `AttributeError`

A property with no setter is read-only through normal assignment:

```python
class Batch:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self._rows = list(rows)

    @property
    def row_count(self) -> int:
        return len(self._rows)

batch = Batch([{"id": 1}, {"id": 2}])
assert batch.row_count == 2

try:
    batch.row_count = 10
except AttributeError:
    pass
else:
    raise AssertionError("assignment should fail")
```

The caller cannot normally assign to `row_count`; Python raises `AttributeError`. This does not make the entire object immutable, and it does not prevent a caller from mutating `_rows` if that internal field is deliberately exposed.

---

## 5. Naming and API design: properties versus methods

Use conventional names:
- `value` — public property;
- `_value` — internal backing state;
- `value` in the setter — incoming value;
- `compute_value()` or `refresh()` — explicit action.

Python usually does not need Java-style `get_value()` and `set_value()` wrappers for ordinary attributes. A property supports a natural interface and can later add validation without changing call sites.

### Prefer a property when

- access is cheap and predictable;
- the result represents a current attribute of the object;
- the operation has no surprising external side effects;
- a read-only or validated attribute is useful.

### Prefer a method when

- computation is expensive or may block;
- the operation performs network, filesystem, database, or other I/O;
- the caller should know an action is happening;
- parameters are needed;
- the operation may change state or require explicit refresh behavior.

For example, `report.total` can be reasonable if it is a cheap in-memory calculation. `report.load_from_warehouse()` is clearer than hiding a database query inside `report.total`.

---

## 6. Validation and invariants

An **invariant** is a condition that must remain true for every valid object state. Examples:
- a temperature cannot be below absolute zero;
- a retry count cannot be negative;
- a batch identifier must be non-empty;
- a date range must have `start <= end`.

Put validation at the boundary that owns the invariant. A setter is useful when callers are allowed to update the value after construction.

```python
class RetryPolicy:
    def __init__(self, max_attempts: int) -> None:
        self.max_attempts = max_attempts

    @property
    def max_attempts(self) -> int:
        return self._max_attempts

    @max_attempts.setter
    def max_attempts(self, value: int) -> None:
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError("max_attempts must be an integer")
        if value < 1:
            raise ValueError("max_attempts must be at least 1")
        self._max_attempts = value

policy = RetryPolicy(3)
policy.max_attempts = 5
assert policy.max_attempts == 5
```

### Why not validate only in `__init__`?

Because later assignment can bypass the rule if the public attribute is unguarded. The property centralizes the rule and makes it apply consistently.

### Validation should be specific

Prefer clear exceptions:
- `TypeError` when the kind of value is inappropriate;
- `ValueError` when the value has the right general kind but is outside the allowed domain.

Do not silently coerce values unless coercion is part of the documented contract. For example, silently converting `"10"` to `10` can conceal upstream schema problems in a data pipeline.

---

## 7. Common property bugs

### 7.1 Infinite recursion in a setter

**Incorrect:**

```python
class Broken:
    @property
    def value(self) -> int:
        return self.value

    @value.setter
    def value(self, new_value: int) -> None:
        self.value = new_value
```

Both methods access the public property again, so the getter or setter calls itself recursively until Python raises `RecursionError`.

**Correct:** store in a separate backing attribute:

```python
class Correct:
    def __init__(self, value: int) -> None:
        self.value = value

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, new_value: int) -> None:
        self._value = new_value

obj = Correct(7)
assert obj.value == 7
obj.value = 8
assert obj.value == 8
```

### 7.2 Bypassing the setter during initialization

This skips validation:

```python
class UnsafeTemperature:
    def __init__(self, celsius: float) -> None:
        self._celsius = celsius  # direct write bypasses property validation
```

Use `self.celsius = celsius` when the setter is responsible for enforcing the invariant.

### 7.3 Exposing mutable internal state

A read-only property does not make the returned object read-only:

```python
class Tags:
    def __init__(self, tags: list[str]) -> None:
        self._tags = list(tags)

    @property
    def tags(self) -> list[str]:
        return self._tags

tags = Tags(["bronze"])
tags.tags.append("unvalidated")
assert tags.tags == ["bronze", "unvalidated"]
```

If callers must not mutate the internal collection, return an immutable view or copy, such as a tuple:

```python
class SafeTags:
    def __init__(self, tags: list[str]) -> None:
        self._tags = list(tags)

    @property
    def tags(self) -> tuple[str, ...]:
        return tuple(self._tags)

safe_tags = SafeTags(["bronze"])
assert safe_tags.tags == ("bronze",)
```

The tuple protects the container structure, though it would not make mutable objects inside that tuple immutable.

---

## 8. `functools.cached_property`

A normal property recomputes on every access. `functools.cached_property` computes on first access and stores the result on the instance. It is useful when a calculation is expensive, depends on stable instance state, and is read repeatedly.

```python
from functools import cached_property

class Report:
    def __init__(self, rows: list[dict[str, int]]) -> None:
        self.rows = list(rows)
        self.computation_count = 0

    @cached_property
    def total(self) -> int:
        self.computation_count += 1
        return sum(row["amount"] for row in self.rows)

report = Report([{"amount": 10}, {"amount": 20}])
assert report.total == 30
assert report.total == 30
assert report.computation_count == 1
```

The value is calculated once on first access, then the result is stored in the instance dictionary under the property name. In this example, `report.total` is later resolved from the instance dictionary rather than recomputing the descriptor.

### 8.1 The `__dict__` requirement

`cached_property` requires an instance `__dict__` that it can write into. A class using `__slots__` without a `__dict__` slot cannot use it normally.

```python
from functools import cached_property

class Slotted:
    __slots__ = ("x",)

    def __init__(self, x: int) -> None:
        self.x = x

    @cached_property
    def doubled(self) -> int:
        return self.x * 2

# Accessing Slotted(3).doubled raises TypeError because there is no instance __dict__.
```

A class can include `"__dict__"` in `__slots__`, but that allows an instance dictionary and reduces some of the memory benefit of slots. Alternatively, use a regular `@property`, a dedicated cache field, or another cache design.

### 8.2 Cache invalidation

A cached value is correct only while its dependencies remain unchanged. If the underlying rows change, `total` may become stale.

One option is to make source data immutable. Another is to invalidate the cached attribute whenever dependencies are changed:

```python
from functools import cached_property

class MutableReport:
    def __init__(self, amounts: list[int]) -> None:
        self._amounts = list(amounts)

    @property
    def amounts(self) -> tuple[int, ...]:
        return tuple(self._amounts)

    def add_amount(self, amount: int) -> None:
        self._amounts.append(amount)
        self.__dict__.pop("total", None)

    @cached_property
    def total(self) -> int:
        return sum(self._amounts)

report = MutableReport([4, 6])
assert report.total == 10
report.add_amount(5)
assert report.total == 15
```

All mutation paths must invalidate the cache. If callers can mutate a list directly, or if the cached result depends on external state that changes independently, invalidation becomes harder. Consider an explicit refresh method, immutable input, a versioned cache, or no cache.

### 8.3 Concurrency and Python 3.12+

Do not assume `cached_property` guarantees exactly-once computation under concurrent access. In Python 3.12, the undocumented per-property lock that existed in earlier versions was removed. Concurrent first access can therefore cause the getter to run more than once; the eventual stored value is one of the computed results.

If duplicate computation is harmless, this can be acceptable. If the calculation has side effects or must run exactly once, add explicit synchronization or redesign it. A property getter should generally be free of side effects.

### 8.4 Cache mutable results carefully

A cached list or dictionary is shared by every caller accessing that same instance property. If one caller mutates it, future callers see the mutation. Prefer immutable cached values or return a copy when callers should not alter the cached result.

---

## 9. `property` is a descriptor

A descriptor is an object that customizes attribute access by implementing methods such as `__get__`, `__set__`, or `__delete__`. The `property` built-in is a data descriptor.

You do not need to implement a descriptor to use properties, but understanding the relationship explains why a property can intercept reads and writes even though it is declared on the class.

```python
class Example:
    @property
    def value(self) -> int:
        return 42

assert isinstance(vars(Example)["value"], property)
assert Example().value == 42
```

Conceptually:
- the property object is stored on the class;
- accessing `instance.value` invokes the property's getter;
- assigning `instance.value = x` invokes the setter if one exists;
- without a setter, ordinary assignment raises `AttributeError`.

A property is a data descriptor even when no setter is defined, so an instance attribute with the same name does not simply override its getter through normal attribute lookup.

### 9.1 Explicit construction

The decorator form is syntax for building a property object. The explicit constructor is:

```python
property(fget=None, fset=None, fdel=None, doc=None)
```

In everyday code, prefer `@property`, `@name.setter`, and `@name.deleter` because they are easier to read. The explicit constructor is useful for understanding the model or constructing properties dynamically.

### 9.2 Properties versus `__getattr__` and custom descriptors

Use:
- `@property` for behavior tied to a specific named attribute;
- `__getattr__` when providing fallback behavior for attributes that were not found;
- a custom descriptor when reusable attribute behavior is needed across many fields or classes, such as a reusable validation field.

Custom descriptors are covered more deeply in the next lesson, **06 — Descriptors and Attribute Lookup Order**.

---

## 10. Inheritance and property overrides

A subclass can override a property getter. To extend or replace a setter while retaining the base property's behavior, use `@BaseClass.property_name.setter`.

```python
class BaseConfig:
    def __init__(self, name: str) -> None:
        self.name = name

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        value = value.strip()
        if not value:
            raise ValueError("name cannot be empty")
        self._name = value


class UppercaseConfig(BaseConfig):
    @BaseConfig.name.setter
    def name(self, value: str) -> None:
        BaseConfig.name.fset(self, value.upper())


config = UppercaseConfig("  orders  ")
assert config.name == "ORDERS"
```

This example deliberately reuses the base setter's validation and storage behavior. Another design is to override the getter only, but be careful: defining a new property in a subclass can replace the inherited property object, including its setter. Use an explicit pattern and test both reads and writes.

---

## 11. Dataclasses and properties

Dataclasses generate an initializer that assigns to fields. That is convenient, but combining a dataclass field and a property with the same name can create surprising initialization behavior.

### Safer pattern: separate storage field and public property

```python
from dataclasses import dataclass

@dataclass
class PortConfig:
    _port: int

    def __post_init__(self) -> None:
        self.port = self._port

    @property
    def port(self) -> int:
        return self._port

    @port.setter
    def port(self, value: int) -> None:
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError("port must be an integer")
        if not 1 <= value <= 65535:
            raise ValueError("port must be between 1 and 65535")
        self._port = value

config = PortConfig(5432)
assert config.port == 5432
```

This works, but note that the generated constructor parameter is `_port`, not `port`. For a public constructor argument named `port`, consider a regular class, a custom `__init__`, or a deliberate dataclass design with `InitVar`. Do not use a same-name field/property pattern without verifying how the generated initializer behaves.

### Frozen dataclasses

A frozen dataclass is useful for immutable value objects. A property can expose a derived value from frozen fields without caching it:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Dimensions:
    width: float
    height: float

    @property
    def area(self) -> float:
        return self.width * self.height

dimensions = Dimensions(3.0, 5.0)
assert dimensions.area == 15.0
```

Frozen dataclasses prevent normal field reassignment but do not recursively freeze mutable objects stored in fields. Prefer immutable field values when immutability is important.

### `NamedTuple` and frozen classes

Named tuples are immutable tuple-like records. They can expose properties for derived values, but cannot normally cache by assigning to an instance dictionary. For immutable records, ordinary computed properties are often the simplest option.

---

## 12. Typing properties

Type annotations communicate the getter's result and setter's accepted value. Keep the public API consistent with actual runtime behavior.

```python
from typing import Protocol

class HasRowCount(Protocol):
    @property
    def row_count(self) -> int:
        ...

class InMemoryBatch:
    def __init__(self, rows: list[object]) -> None:
        self._rows = list(rows)

    @property
    def row_count(self) -> int:
        return len(self._rows)

def summarize(batch: HasRowCount) -> str:
    return f"{batch.row_count} rows"

assert summarize(InMemoryBatch([1, 2, 3])) == "3 rows"
```

A protocol can specify a read-only property, allowing different implementations to satisfy the interface without inheriting from a shared base class.

`Self` from `typing` is useful in fluent APIs and methods that return the current instance, but is not usually needed for a basic property. Avoid overcomplicating types when a straightforward return annotation is sufficient.

---

## 13. Class-level properties: version caution

Do not use the `@classmethod` + `@property` combination as a portable class-level-property pattern. This combination was deprecated in Python 3.11 and removed in Python 3.13. For class-level computed attributes, use a dedicated descriptor or metaclass when the use case genuinely requires one; otherwise, a class method such as `Config.default_region()` may be clearer.

This lesson targets Python 3.12+, so code that must run on both 3.12 and 3.13 should avoid relying on the deprecated combination.

---

## 14. Lazy loading and external resources

A property can defer work, but hiding external I/O behind attribute access can surprise users:

```python
class WarehouseReport:
    @property
    def total(self) -> int:
        # Avoid this design if the body silently executes a slow database query.
        raise NotImplementedError
```

The example is intentionally incomplete: it illustrates a design warning, not a runnable implementation. Prefer an explicit method such as `load_total()` or `refresh()` when database/network access is involved. A method tells the caller that work may happen and gives a natural place for parameters, retries, timeouts, and errors.

For lazy-loaded ORM attributes, be aware that access may trigger a database query. Document that behavior and consider whether the caller can predict the cost.

---

## 15. Performance and design trade-offs

- A normal property runs its getter on each access. Keep cheap computed properties simple.
- `cached_property` stores data in the instance dictionary and can increase per-instance memory use.
- Cache invalidation creates complexity; a stale answer can be worse than a slower calculation.
- A getter with side effects makes attribute reads surprising and difficult to reason about.
- Returning a copy from a property can protect internal state but costs time and memory.
- If a property performs a database query, file read, network call, or heavy computation, consider a method with an explicit name.
- Profile real workloads before optimizing. Do not add caching just because a calculation might be expensive.

---

## 16. Production example: validated data-pipeline configuration

The following example combines validation, a computed property, and a clear API boundary:

```python
class PipelineConfig:
    def __init__(self, batch_size: int, max_retries: int) -> None:
        self.batch_size = batch_size
        self.max_retries = max_retries

    @property
    def batch_size(self) -> int:
        return self._batch_size

    @batch_size.setter
    def batch_size(self, value: int) -> None:
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError("batch_size must be an integer")
        if value < 1:
            raise ValueError("batch_size must be at least 1")
        self._batch_size = value

    @property
    def max_retries(self) -> int:
        return self._max_retries

    @max_retries.setter
    def max_retries(self, value: int) -> None:
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError("max_retries must be an integer")
        if value < 0:
            raise ValueError("max_retries cannot be negative")
        self._max_retries = value

    @property
    def max_attempts(self) -> int:
        return self.max_retries + 1

config = PipelineConfig(batch_size=500, max_retries=3)
assert config.max_attempts == 4
config.max_retries = 5
assert config.max_attempts == 6
```

The `max_attempts` property is derived from `max_retries`; it cannot become stale because it is recomputed. The setters enforce the same rules during initialization and later updates.

For production systems, consider whether configuration should be immutable after construction. An immutable configuration object can reduce accidental runtime changes and simplify concurrency reasoning.

---

## 17. Testing properties correctly

Test through the public interface. A caller should not need to know the backing attribute name.

A useful test suite includes:
- valid initialization;
- valid reassignment;
- invalid type;
- invalid domain value;
- read-only assignment;
- computed value after dependency changes;
- cache reuse and invalidation, if caching is part of the contract.

Example pytest tests:

```python
import pytest

def test_temperature_validation_and_computed_value():
    temperature = Temperature(0)
    assert temperature.fahrenheit == 32
    temperature.celsius = 100
    assert temperature.fahrenheit == 212

def test_temperature_rejects_below_absolute_zero():
    with pytest.raises(ValueError):
        Temperature(-300)

def test_temperature_rejects_wrong_type():
    with pytest.raises(TypeError):
        Temperature("warm")  # type: ignore[arg-type]

def test_read_only_property_rejects_assignment():
    batch = Batch([{"id": 1}])
    with pytest.raises(AttributeError):
        batch.row_count = 10  # type: ignore[misc]

def test_cached_total_is_computed_once():
    report = Report([{"amount": 2}, {"amount": 3}])
    assert report.total == 5
    assert report.total == 5
    assert report.computation_count == 1

def test_cached_total_is_invalidated_after_mutation():
    report = MutableReport([2, 3])
    assert report.total == 5
    report.add_amount(4)
    assert report.total == 9
```

Place these tests in a test file that imports the corresponding classes from the lesson's module. If the lesson is copied as a standalone Markdown file, first extract the relevant class definitions into a Python module or adapt the tests to the code layout in your project.

---

## 18. Exercises

Try these before reading the solutions.

### Exercise 1 — validated percentage

Create a `Percentage` class with a writable `value` property. Accept numbers from 0 through 100 and reject values outside the range. Decide how booleans should be treated.

### Exercise 2 — computed duration

Create a `JobRun` class that stores `started_at_seconds` and `finished_at_seconds`. Expose a read-only `duration_seconds` property. Validate that the finish time is not before the start time.

### Exercise 3 — cache invalidation

Extend `MutableReport` so a method can replace all amounts. Ensure `total` is correct after replacement.

### Exercise 4 — read-only collection

Create a class that stores a list of column names but exposes them as a tuple through a property. Explain why returning the internal list would weaken encapsulation.

### Exercise 5 — property or method?

For each operation, choose a property or method and explain why:
1. Return a stored job identifier.
2. Compute the number of rows in an in-memory list.
3. Query a remote warehouse for the latest row count.
4. Rebuild a materialized report.

### Exercise 6 — inheritance

Create a base `Config` with a property that strips whitespace and rejects an empty string. Create a subclass that stores the accepted name in uppercase while retaining the base validation.

### Exercise 7 — stale cache analysis

A `cached_property` sums values in `self.rows`, where `rows` is a public list. Identify two ways the cached result could become stale and propose a safer design.

### Exercise 8 — dataclass design

Create a frozen dataclass `Rectangle` with `width` and `height` and a computed `area` property. Explain why no cache is needed for this inexpensive calculation.

---

## 19. Exercise solutions

### Solution 1

```python
class Percentage:
    def __init__(self, value: int | float) -> None:
        self.value = value

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, value: int | float) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("value must be a number, not bool")
        if not 0 <= value <= 100:
            raise ValueError("value must be between 0 and 100")
        self._value = float(value)

percentage = Percentage(75)
assert percentage.value == 75.0
```

### Solution 2

```python
class JobRun:
    def __init__(self, started_at_seconds: float, finished_at_seconds: float) -> None:
        if finished_at_seconds < started_at_seconds:
            raise ValueError("finish time cannot precede start time")
        self._started = started_at_seconds
        self._finished = finished_at_seconds

    @property
    def duration_seconds(self) -> float:
        return self._finished - self._started

run = JobRun(10.0, 17.5)
assert run.duration_seconds == 7.5
```

### Solution 3

```python
from functools import cached_property

class ReplaceableReport:
    def __init__(self, amounts: list[int]) -> None:
        self._amounts = list(amounts)

    def replace_amounts(self, amounts: list[int]) -> None:
        self._amounts = list(amounts)
        self.__dict__.pop("total", None)

    @cached_property
    def total(self) -> int:
        return sum(self._amounts)

report = ReplaceableReport([1, 2])
assert report.total == 3
report.replace_amounts([10, 20])
assert report.total == 30
```

### Solution 4

```python
class Schema:
    def __init__(self, columns: list[str]) -> None:
        self._columns = list(columns)

    @property
    def columns(self) -> tuple[str, ...]:
        return tuple(self._columns)

schema = Schema(["id", "created_at"])
assert schema.columns == ("id", "created_at")
```

Returning the internal list would let callers append, remove, or replace names without going through the class's intended validation or cache invalidation.

### Solution 5

1. **Property:** a stored identifier is a simple attribute.
2. **Property:** counting an in-memory list is cheap and predictable.
3. **Method:** the remote query may block, fail, incur cost, and need timeout/retry behavior.
4. **Method:** rebuilding is an explicit action with side effects and likely nontrivial cost.

### Solution 6

```python
class Config:
    def __init__(self, name: str) -> None:
        self.name = name

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        value = value.strip()
        if not value:
            raise ValueError("name cannot be empty")
        self._name = value

class UpperConfig(Config):
    @Config.name.setter
    def name(self, value: str) -> None:
        Config.name.fset(self, value.upper())

config = UpperConfig("  analytics ")
assert config.name == "ANALYTICS"
```

### Solution 7

The cached total can become stale if a caller appends directly to `self.rows`, or if another method replaces or mutates the list without invalidating the cache. Safer designs include immutable input (such as a tuple), encapsulating all mutations behind methods that invalidate the cache, or computing the total with a normal property if the calculation is cheap enough.

### Solution 8

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Rectangle:
    width: float
    height: float

    @property
    def area(self) -> float:
        return self.width * self.height

rectangle = Rectangle(4, 6)
assert rectangle.area == 24
```

The calculation is inexpensive, and the fields are immutable under normal assignment. A cache would add complexity and memory overhead without a meaningful benefit.

---

## 20. Self-check

Answer these without looking back, then compare with the key.

1. Why should `__init__` assign through `self.celsius` rather than directly to `self._celsius`?
2. What does `cached_property` store, and where?
3. Why does `cached_property` not work normally on a slotted class without `__dict__`?
4. When is a method better than a property?
5. What error does assignment to a read-only property normally raise?
6. Why can a cached result become stale?
7. What does it mean that `property` is a data descriptor?
8. Why can a same-name dataclass field/property combination be surprising?
9. What changed for `cached_property` concurrency in Python 3.12?
10. Why is `@classmethod` + `@property` not a portable class-level-property pattern on Python 3.12+?

### Answer key

1. To route initialization through the setter and enforce the invariant consistently.
2. It computes the value once on first access and stores it in the instance dictionary under the property name.
3. It needs a writable instance dictionary to store the cached result.
4. When the operation is expensive, performs I/O, has side effects, needs parameters, or should be explicit to the caller.
5. `AttributeError`.
6. A dependency may change after the first calculation while the cached result remains stored.
7. It participates in attribute access through descriptor methods and takes precedence over a same-name instance attribute for normal lookup.
8. The generated initializer assigns fields; the property can intercept or change the expected initialization semantics.
9. The undocumented per-property lock was removed; concurrent first access may compute more than once.
10. It was deprecated in Python 3.11 and removed in Python 3.13; use a dedicated descriptor, metaclass, or clearer class method.

---

## 21. Common mistakes checklist

- [ ] Writing `self.value = value` inside the `value` setter, causing recursion.
- [ ] Bypassing the setter in `__init__` and skipping validation.
- [ ] Returning a mutable internal list while assuming a read-only property makes it immutable.
- [ ] Caching a result without identifying all of its dependencies.
- [ ] Forgetting to invalidate cached values after mutation.
- [ ] Using `cached_property` on a class with no instance dictionary.
- [ ] Assuming concurrent access guarantees exactly-once computation.
- [ ] Hiding network/database I/O in an innocent-looking property.
- [ ] Using a dataclass field and same-name property without checking generated initialization.
- [ ] Using deprecated or removed class-level-property patterns.
- [ ] Adding properties where a plain attribute would be simpler.

---

## 22. Readiness checklist

You are ready to move on when you can do all of the following without copying the examples:

- [ ] Explain when a plain attribute is preferable to a property.
- [ ] Write a property with a getter, setter, and optional deleter.
- [ ] Validate values in one place and preserve invariants during initialization and later assignment.
- [ ] Implement a read-only computed attribute.
- [ ] Explain why property setters can recurse and how backing attributes avoid that.
- [ ] Explain how `cached_property` stores results and why invalidation matters.
- [ ] Describe the `__dict__` and `__slots__` interaction.
- [ ] Explain why properties are descriptors and distinguish them from `__getattr__`.
- [ ] Choose a method over a property when work is expensive or has side effects.
- [ ] Test public property behavior for both success and failure cases.

---

## 23. Key takeaways

1. A property gives an attribute a controlled interface without changing how callers access it.
2. Put validation in the setter when the class owns the invariant, and assign through that setter during initialization.
3. A read-only property prevents normal reassignment of the attribute; it does not automatically make returned mutable objects immutable.
4. `cached_property` is a trade-off: faster repeated access at the cost of memory, invalidation complexity, and possible duplicate computation under concurrency.
5. Properties are descriptors. Reusable attribute behavior may call for a custom descriptor, covered in the next lesson.
6. Keep properties cheap and predictable. Use methods for explicit actions, expensive work, and I/O.

**Next lesson:** `06-descriptors-and-attribute-lookup-order.md`.
