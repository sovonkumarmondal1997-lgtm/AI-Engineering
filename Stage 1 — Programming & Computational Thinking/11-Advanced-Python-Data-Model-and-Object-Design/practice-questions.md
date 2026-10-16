# Practice Questions — Advanced Python Data Model and Object Design

**Stage:** 1 — Programming & Computational Thinking  
**Module:** 11 — Advanced Python Data Model and Object Design  
**Target Python:** 3.12+ (questions explicitly marked 3.13+ use newer features)  
**Suggested tools:** `pytest`, `ruff`, `mypy` or `pyright`, `tracemalloc`, `timeit`

---

## How to use this workbook

Work through the phases in order. For output-prediction questions, write down the exact output or exception **before** running the code, then explain the mechanism. For implementation questions, write tests first, include edge cases, and check the public contract rather than only the happy path.

- **Basic:** explain or implement a core mechanism.
- **Intermediate:** handle type boundaries, inheritance, and edge cases.
- **Advanced:** reason about design trade-offs, failure modes, security, and performance.

Unless a question states otherwise, assume Python 3.12+. Some questions ask for a short explanation; implementation questions should include type hints and tests where practical.

## Phase A — Making objects behave

Focus: special methods, equality and hashing, rich comparisons, containers, and iteration.

### A1. Dunder-method output prediction — Basic

**What does this print, and why?**

```python
class Job:
    def __init__(self, job_id):
        self.job_id = job_id

    def __repr__(self):
        return f"Job({self.job_id!r})"

    def __str__(self):
        return f"job {self.job_id}"

job = Job("J-17")
print(job)
print([job])
```

Explain why the direct print and list representation differ.

### A2. Equality and hash contract — Intermediate

**Find the defect and repair it.**

```python
class Customer:
    def __init__(self, customer_id):
        self.customer_id = customer_id

    def __eq__(self, other):
        if not isinstance(other, Customer):
            return False
        return self.customer_id == other.customer_id

    def __hash__(self):
        return id(self)
```

Two `Customer("C-1")` objects compare equal but may have different hashes. Explain why that violates the equality/hash contract, then implement a correct policy. State what should happen if `customer_id` can change after the object is inserted into a set.

**Corrected implementation:**

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Customer:
    customer_id: str

left, right = Customer("C-1"), Customer("C-1")
assert left == right and hash(left) == hash(right)
assert len({left, right}) == 1

try:
    left.customer_id = "C-2"
except AttributeError:
    pass
else:
    raise AssertionError("the equality/hash key must remain immutable")
```

The frozen dataclass generates equality and a compatible hash from the same field. For a mutable entity, prefer making it unhashable or using a separate immutable key rather than hashing fields that can change.

### A3. Round-trippable representation — Intermediate

Implement `__repr__` for an immutable `Coordinate(x, y)` value object so that, when `Coordinate` is available in the evaluation namespace, `eval(repr(point))` reconstructs an equal object. Add a test for negative coordinates. Explain why `eval` should not be used on representations from untrusted sources.

**Complete example:**

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Coordinate:
    x: int
    y: int

    def __repr__(self) -> str:
        return f"Coordinate({self.x!r}, {self.y!r})"

point = Coordinate(-2, 5)
rebuilt = eval(repr(point), {"Coordinate": Coordinate})
assert rebuilt == point
assert rebuilt is not point
print(repr(point))
```


### A4. Rich comparison — Intermediate

Implement a `Version(major, minor, patch)` value object with `__eq__` and `__lt__`. Unsupported operand types must return `NotImplemented`. Add tests for ordering, equality, and `Version(...) < 3`. Explain why the last expression should raise `TypeError` rather than silently inventing an ordering.

**Complete example:**

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Version:
    major: int
    minor: int
    patch: int

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

assert Version(1, 2, 0) < Version(1, 10, 0)
assert Version(2, 0, 0) == Version(2, 0, 0)
try:
    Version(1, 0, 0) < 3
except TypeError:
    pass
else:
    raise AssertionError("incompatible comparison should raise TypeError")
```


### A5. Container protocol — Basic

Implement a read-only `Batch` sequence backed by a private list. Support `len(batch)`, integer indexing, negative indexes, slicing, and iteration. A slice should return a `Batch`, not a raw list. Add tests for empty batches and out-of-range indexing.

**Complete example:**

```python
from collections.abc import Sequence, Iterator
from typing import overload

class Batch(Sequence):
    def __init__(self, items=()):
        self._items = list(items)

    def __len__(self) -> int:
        return len(self._items)

    @overload
    def __getitem__(self, index: int): ...
    @overload
    def __getitem__(self, index: slice) -> "Batch": ...
    def __getitem__(self, index):
        result = self._items[index]
        return Batch(result) if isinstance(index, slice) else result

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return NotImplemented
        return self._items == other._items

    def __repr__(self) -> str:
        return f"Batch({self._items!r})"

batch = Batch([10, 20, 30])
assert len(batch) == 3 and batch[-1] == 30
assert batch[1:] == Batch([20, 30])
assert list(batch) == [10, 20, 30]
try:
    batch[9]
except IndexError:
    pass
else:
    raise AssertionError("out-of-range indexing must raise IndexError")
assert len(Batch()) == 0
```


### A6. **What does this print, and why?** — Basic

```python
class Bag:
    def __init__(self, items):
        self.items = list(items)

    def __len__(self):
        return len(self.items)

bag = Bag([10, 20])
print(bool(bag))
bag.items.clear()
print(bool(bag))
```

Explain the truth-value fallback when `__bool__` is absent.

### A7. **What does this print, and why?** — Intermediate

```python
class LegacySequence:
    def __getitem__(self, index):
        if index == 0:
            return "alpha"
        if index == 1:
            return "beta"
        raise IndexError

print(list(LegacySequence()))
```

Name the legacy protocol used here and explain why the stopping exception matters.

### A8. **What does this print, and why?** — Intermediate

```python
class Token:
    def __eq__(self, other):
        if not isinstance(other, Token):
            return NotImplemented
        return self.value == other.value

    def __init__(self, value):
        self.value = value

print(Token("x") == 5)
```

Explain how Python handles `NotImplemented` in equality comparisons and distinguish the singleton `NotImplemented` from the exception `NotImplementedError`.

### A9. **What does this print, and why?** — Advanced

```python
from functools import total_ordering

@total_ordering
class Rank:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, Rank):
            return NotImplemented
        return self.value == other.value

    def __lt__(self, other):
        if not isinstance(other, Rank):
            return NotImplemented
        return self.value < other.value

print(Rank(2) <= Rank(2))
print(Rank(2) > Rank(3))
```

Explain which methods are generated and one reason explicit methods may be preferable in a performance-sensitive class.

### A10. **What does this print, and why?** — Advanced

```python
class Counter:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, Counter):
            return NotImplemented
        return self.value == other.value

a = Counter(1)
b = Counter(1)
print(a == b)
try:
    print({a, b})
except TypeError as exc:
    print(type(exc).__name__)
```

Explain why defining `__eq__` normally makes this class unhashable unless an appropriate `__hash__` is supplied.

### A11. Container and equality review — Advanced

A custom mapping stores normalized string keys, but its `__contains__` checks the raw input and its `__getitem__` normalizes keys. Describe a failing example, then repair the design. Explain when inheriting from `collections.UserDict` or implementing `collections.abc.Mapping` is safer than subclassing `dict`.

---

## Phase B — Operators and attributes

Focus: arithmetic protocols, reflected/in-place operators, properties, descriptors, and attribute lookup.

**Complete example — normalized mapping:**

```python
from collections import UserDict

class CaseInsensitiveDict(UserDict):
    @staticmethod
    def _normalize(key: str) -> str:
        if not isinstance(key, str):
            raise TypeError("keys must be strings")
        return key.casefold()

    def __getitem__(self, key):
        return super().__getitem__(self._normalize(key))

    def __setitem__(self, key, value):
        super().__setitem__(self._normalize(key), value)

    def __contains__(self, key):
        return super().__contains__(self._normalize(key))

cfg = CaseInsensitiveDict({"Host": "db01"})
assert cfg["HOST"] == "db01"
assert "host" in cfg
cfg["hOsT"] = "db02"
assert len(cfg) == 1 and cfg["HOST"] == "db02"
```


### B1. Implement a safe `Money` type — Intermediate

Implement an immutable `Money(amount_minor_units, currency)` type. Requirements:

1. Equality and hashing use both amount and currency.
2. Addition is allowed only for the same currency.
3. Unsupported operand types return `NotImplemented`.
4. A currency mismatch raises a clearly documented exception.
5. Add tests for equality, set membership, addition, and mismatched currencies.

Do not use binary floating-point values to store the amount.

**Complete example:**

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    amount_minor_units: int
    currency: str

    def __post_init__(self) -> None:
        if isinstance(self.amount_minor_units, bool) or not isinstance(self.amount_minor_units, int):
            raise TypeError("amount_minor_units must be an integer")
        if not self.currency or self.currency != self.currency.upper():
            raise ValueError("currency must be a non-empty uppercase code")

    def __add__(self, other: object) -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("cannot add different currencies")
        return Money(self.amount_minor_units + other.amount_minor_units, self.currency)

price = Money(1250, "USD")
assert price + Money(75, "USD") == Money(1325, "USD")
assert len({price, Money(1250, "USD")}) == 1
try:
    price + Money(1, "EUR")
except ValueError:
    pass
else:
    raise AssertionError("currency mismatch should fail")
```


### B2. Reflected and in-place operators — Intermediate

Complete this runnable example by adding `__rmul__` and `__iadd__`:

```python
class Vector2D:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __mul__(self, scalar):
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return Vector2D(self.x * scalar, self.y * scalar)

    def __add__(self, other):
        if not isinstance(other, Vector2D):
            return NotImplemented
        return Vector2D(self.x + other.x, self.y + other.y)

    def __rmul__(self, scalar):
        return self * scalar

    def __iadd__(self, other):
        if not isinstance(other, Vector2D):
            return NotImplemented
        self.x += other.x
        self.y += other.y
        return self

    def __repr__(self):
        return f"Vector2D({self.x}, {self.y})"

a = Vector2D(1, 2)
alias = a
a += Vector2D(3, 4)
print(a, alias, a is alias)
print((3 * Vector2D(2, 4)))
```

Document whether `+=` mutates the existing instance. Explain how identity and values depend on `__iadd__` implementation.

### B3. Property validation — Basic

Create a `Temperature` class with a Celsius property that rejects values below absolute zero. The constructor must validate through the same public property. Add tests for the boundary value and a rejected value.

**Complete example:**

```python
class Temperature:
    def __init__(self, celsius: float) -> None:
        self.celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15:
            raise ValueError("temperature is below absolute zero")
        self._celsius = float(value)

t = Temperature(-273.15)
assert t.celsius == -273.15
try:
    Temperature(-273.16)
except ValueError:
    pass
else:
    raise AssertionError("below absolute zero should fail")
```


### B4. Build a validating descriptor — Advanced

Implement `PositiveInt`, a data descriptor that accepts only positive integers and rejects `bool` (remember `bool` is a subclass of `int`). Store values per instance without accidentally sharing them between instances. Test missing values, invalid values, and two independent instances.

**Complete example:**

```python
class PositiveInt:
    def __set_name__(self, owner, name):
        self.storage_name = f"_{name}"
        self.public_name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        try:
            return instance.__dict__[self.storage_name]
        except KeyError:
            raise AttributeError(f"{self.public_name} has not been set") from None

    def __set__(self, instance, value):
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{self.public_name} must be an integer")
        if value <= 0:
            raise ValueError(f"{self.public_name} must be positive")
        instance.__dict__[self.storage_name] = value

class Partition:
    count = PositiveInt()

p1, p2 = Partition(), Partition()
p1.count = 3
p2.count = 7
assert (p1.count, p2.count) == (3, 7)
try:
    Partition().count
except AttributeError:
    pass
else:
    raise AssertionError("unset descriptor should raise AttributeError")
for bad in (True, 0, -1, 1.5):
    try:
        p1.count = bad
    except (TypeError, ValueError):
        pass
    else:
        raise AssertionError(f"invalid value accepted: {bad!r}")
```


### B5. Attribute lookup — Advanced

Given a class with a data descriptor named `value`, an instance attribute also named `value`, and a non-data descriptor named `method`, predict which value is returned by attribute access. Write a minimal runnable demonstration and explain the lookup order involving `__getattribute__`, data descriptors, the instance dictionary, non-data descriptors, and `__getattr__`.

**Complete example:**

```python
class DataDescriptor:
    def __get__(self, instance, owner=None):
        return "data descriptor"
    def __set__(self, instance, value):
        instance.__dict__["_value"] = value

class NonDataDescriptor:
    def __get__(self, instance, owner=None):
        return "non-data descriptor"

class Example:
    value = DataDescriptor()
    method = NonDataDescriptor()
    def __getattr__(self, name):
        if name == "missing":
            return "fallback"
        raise AttributeError(name)

obj = Example()
obj.__dict__["value"] = "instance value"
obj.__dict__["method"] = "instance method value"
assert obj.value == "data descriptor"
assert obj.method == "instance method value"
assert obj.missing == "fallback"
```


### B6. **What does this print, and why?** — Basic

```python
class Example:
    @property
    def doubled(self):
        return self._value * 2

    def __init__(self, value):
        self._value = value

item = Example(7)
print(item.doubled)
item._value = 9
print(item.doubled)
```

Explain why this property is computed on access rather than stored as a separate field.

### B7. **What does this print, and why?** — Intermediate

```python
class Descriptor:
    def __get__(self, instance, owner=None):
        return "descriptor"

class Example:
    value = Descriptor()

item = Example()
item.__dict__["value"] = "instance"
print(item.value)
```

Explain why this descriptor is a non-data descriptor and how adding `__set__` or `__delete__` changes precedence.

### B8. **What does this print, and why?** — Intermediate

```python
class Vector:
    def __init__(self, value):
        self.value = value

    def __mul__(self, other):
        if not isinstance(other, (int, float)):
            return NotImplemented
        return Vector(self.value * other)

    def __rmul__(self, other):
        return self * other

print((3 * Vector(4)).value)
```

Explain the reflected-operator dispatch that makes the expression work.

### B9. **What does this print, and why?** — Advanced

```python
class Base:
    @property
    def name(self):
        return "base"

class Child(Base):
    def __init__(self):
        self.__dict__["name"] = "instance"

print(Child().name)
```

Explain why a property with a getter and no setter is still a data descriptor and therefore takes precedence over the instance dictionary.

### B10. **What does this print, and why?** — Advanced

```python
from functools import cached_property

class Report:
    def __init__(self):
        self.calls = 0

    @cached_property
    def total(self):
        self.calls += 1
        return 42

r = Report()
print(r.total, r.total, r.calls)
```

Explain the caching behaviour and one important constraint when using `cached_property` with `__slots__`.

### B11. Operator and descriptor design review — Advanced

Review a proposed class that overloads `+` to mean “send this job to a queue” and whose property setter performs a network request. Identify the API-design risks and propose clearer alternatives. Discuss side effects, operator expectations, and testability.

---

## Phase C — Memory and inheritance mechanics

Focus: `__slots__`, memory measurement, MRO, `super()`, and mixins.

### C1. Measure slots versus instance dictionaries — Intermediate

Create two equivalent classes, one with a normal instance dictionary and one with `__slots__`. Allocate a large number of instances and compare memory using `tracemalloc`. State the Python version, allocation method, and limitations of your measurement. Do not assume `sys.getsizeof(instance)` alone captures all referenced memory.

**Complete benchmark example:**

```python
import gc
import tracemalloc

class DictRecord:
    def __init__(self, x, y):
        self.x, self.y = x, y

class SlottedRecord:
    __slots__ = ("x", "y")
    def __init__(self, x, y):
        self.x, self.y = x, y

def measure(factory, count=100_000):
    gc.collect()
    tracemalloc.start()
    objects = [factory(i, i + 1) for i in range(count)]
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return current, peak, objects

for cls in (DictRecord, SlottedRecord):
    current, peak, keep_alive = measure(cls)
    print(cls.__name__, current, peak)
    del keep_alive
```


### C2. Diamond MRO — Intermediate

Predict the MRO and constructor call order for:

```python
class Root:
    def __init__(self, **kwargs):
        print("Root")
        super().__init__(**kwargs)

class Left(Root):
    def __init__(self, **kwargs):
        print("Left")
        super().__init__(**kwargs)

class Right(Root):
    def __init__(self, **kwargs):
        print("Right")
        super().__init__(**kwargs)

class Leaf(Left, Right):
    def __init__(self, **kwargs):
        print("Leaf")
        super().__init__(**kwargs)

Leaf()
```

Explain why `Root` runs once in this cooperative chain.

### C3. Repair a non-cooperative hierarchy — Advanced

A mixin calls `Base.__init__(self)` directly, while another parent also inherits from `Base`. Refactor the hierarchy to use cooperative `super()` and compatible keyword arguments. Write a test proving the shared base is initialized exactly once.

**Complete cooperative example:**

```python
class Root:
    def __init__(self, **kwargs):
        if kwargs:
            unexpected = next(iter(kwargs))
            raise TypeError(f"unexpected argument: {unexpected}")
        self.initialized = getattr(self, "initialized", 0) + 1
        super().__init__()

class Base(Root):
    def __init__(self, *, source, **kwargs):
        self.source = source
        super().__init__(**kwargs)

class AuditMixin(Root):
    def __init__(self, *, audit=True, **kwargs):
        self.audit = audit
        super().__init__(**kwargs)

class Pipeline(AuditMixin, Base):
    def __init__(self, *, source, audit=True):
        super().__init__(source=source, audit=audit)

p = Pipeline(source="warehouse", audit=False)
assert p.source == "warehouse" and p.audit is False
assert p.initialized == 1
assert [c.__name__ for c in Pipeline.__mro__][:4] == ["Pipeline", "AuditMixin", "Base", "Root"]
```


### C4. Diagnose an inconsistent MRO — Advanced

Explain why this hierarchy cannot be created, and propose a coherent redesign:

```python
class A: pass
class B(A): pass
class C(A, B): pass
```

Your answer should use local precedence order and inheritance constraints, not only state “Python raises `TypeError`.”

**Corrected redesign example:**

```python
class A:
    pass

class B(A):
    pass

class C(B):
    pass

assert C.__mro__ == (C, B, A, object)
```

### C5. Mixin versus composition — Advanced

Design a `RetryPolicy` for a data-ingestion client. Compare (a) a `RetryMixin`, (b) a composed `RetryPolicy` object, and (c) a plain retry function. Recommend one based on independent reuse, state, host coupling, and testability.

**Complete composition example:**

```python
from dataclasses import dataclass
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")

@dataclass(frozen=True)
class RetryPolicy:
    attempts: int = 3

    def run(self, operation: Callable[[], T]) -> T:
        if self.attempts < 1:
            raise ValueError("attempts must be at least one")
        last_error = None
        for _ in range(self.attempts):
            try:
                return operation()
            except OSError as exc:
                last_error = exc
        assert last_error is not None
        raise last_error

class IngestionClient:
    def __init__(self, fetch, retry_policy=None):
        self.fetch = fetch
        self.retry_policy = retry_policy or RetryPolicy()

    def ingest(self):
        return self.retry_policy.run(self.fetch)

tries = 0
def flaky_fetch():
    global tries
    tries += 1
    if tries < 2:
        raise OSError("temporary failure")
    return ["row"]

assert IngestionClient(flaky_fetch).ingest() == ["row"]
assert tries == 2
```


### C6. **What does this print, and why?** — Basic

```python
class Base:
    def run(self):
        return "base"

class Mixin:
    def run(self):
        return "mixin"

class Service(Mixin, Base):
    pass

print(Service().run())
print([cls.__name__ for cls in Service.__mro__])
```

Explain why base order is observable behaviour.

### C7. **What does this print, and why?** — Intermediate

```python
class A:
    def action(self):
        return ["A"]

class B(A):
    def action(self):
        return ["B"] + super().action()

class C(A):
    def action(self):
        return ["C"] + super().action()

class D(B, C):
    def action(self):
        return ["D"] + super().action()

print(D().action())
```

Trace the MRO and explain why `C.action` is reached through `super()` inside `B`.

### C8. **What does this print, and why?** — Intermediate

```python
class Base:
    __slots__ = ("value",)

class Mixin:
    __slots__ = ()

class Record(Mixin, Base):
    __slots__ = ()

r = Record()
r.value = 5
print(r.value)
```

Explain why empty slots are useful for stateless mixins and how non-empty slot layouts can create multiple-inheritance conflicts.

### C9. **What does this print, and why?** — Advanced

```python
class Base:
    def __init__(self):
        print("Base")

class Mixin(Base):
    def __init__(self):
        print("Mixin")

class Child(Mixin):
    pass

Child()
```

Explain why the base initializer does not run and why `super()` should be used in cooperative constructors.

### C10. **What does this print, and why?** — Advanced

```python
class A:
    def f(self):
        return "A"

class B:
    def f(self):
        return "B"

class C(A, B):
    pass

class D(B, A):
    pass

print(C().f(), D().f())
```

Explain why both classes are valid but resolve the same method name differently.

### C11. Inheritance design review — Advanced

A team adds five mixins, each defining `__init__`, with different positional signatures and no `super()` calls. Identify at least four failure modes and propose a migration plan that uses cooperative keyword forwarding or composition. Include tests that protect the MRO contract.

---

## Phase D — Contracts and object lifecycle

Focus: ABCs, mapping contracts, copying, pickling, resource cleanup, and lifecycle hooks.

**Complete cooperative pattern to compare against the flawed design:**

```python
class Root:
    def __init__(self, **kwargs):
        if kwargs:
            raise TypeError(f"unexpected options: {sorted(kwargs)}")
        super().__init__()

class MetricsMixin:
    def __init__(self, *, metrics=True, **kwargs):
        self.metrics_enabled = metrics
        super().__init__(**kwargs)

class RetryMixin:
    def __init__(self, *, retries=3, **kwargs):
        self.retries = retries
        super().__init__(**kwargs)

class Worker(MetricsMixin, RetryMixin, Root):
    def __init__(self, *, name, metrics=True, retries=3):
        self.name = name
        super().__init__(metrics=metrics, retries=retries)

w = Worker(name="ingest", metrics=False, retries=5)
assert (w.name, w.metrics_enabled, w.retries) == ("ingest", False, 5)
assert [c.__name__ for c in Worker.__mro__][:4] == ["Worker", "MetricsMixin", "RetryMixin", "Root"]
```


### D1. Implement a `Mapping` — Intermediate

Implement a read-only `ConfigView` by subclassing `collections.abc.Mapping`. Implement only the required methods `__getitem__`, `__iter__`, and `__len__`; then demonstrate `get`, `keys`, `items`, `values`, membership, and equality. Test missing keys and empty mappings.

**Complete example:**

```python
from collections.abc import Mapping

class ConfigView(Mapping):
    def __init__(self, values=()):
        self._data = dict(values)

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

cfg = ConfigView({"host": "db01", "port": 5432})
assert cfg.get("port") == 5432
assert list(cfg.keys()) == ["host", "port"]
assert list(cfg.items()) == [("host", "db01"), ("port", 5432)]
assert list(cfg.values()) == ["db01", 5432]
assert "host" in cfg and cfg == {"host": "db01", "port": 5432}
try:
    cfg["missing"]
except KeyError:
    pass
else:
    raise AssertionError("missing key should raise KeyError")
assert len(ConfigView()) == 0
```


### D2. Make a lock-owning class picklable — Advanced

A `Cache` owns a dictionary and a `threading.Lock`. Implement `__getstate__` and `__setstate__` so the data is serialized while a fresh lock is created after unpickling. Add a round-trip test. Explain why the lock itself should not be serialized and why this does not make pickle safe for untrusted input.

**Complete example:**

```python
import pickle
import threading

class Cache:
    def __init__(self, data=None):
        self.data = dict(data or {})
        self.lock = threading.Lock()

    def __getstate__(self):
        return {"data": self.data.copy()}

    def __setstate__(self, state):
        self.data = dict(state["data"])
        self.lock = threading.Lock()

original = Cache({"rows": 12})
restored = pickle.loads(pickle.dumps(original))
assert restored.data == original.data
assert restored.lock is not original.lock
assert restored.lock.acquire(blocking=False)
restored.lock.release()
```


### D3. Replace `__del__` cleanup — Advanced

A class opens a resource and uses `__del__` to close it. Refactor it to use a context manager for deterministic cleanup. Then describe when `weakref.finalize` is appropriate and what object-reference mistakes can prevent finalization.

**Complete context-manager example:**

```python
class ManagedResource:
    def __init__(self, resource):
        self.resource = resource
        self.closed = False

    def __enter__(self):
        if self.closed:
            raise RuntimeError("resource already closed")
        return self

    def close(self):
        if not self.closed:
            self.resource.close()
            self.closed = True

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False

class FakeHandle:
    def __init__(self): self.closed = False
    def close(self): self.closed = True

handle = FakeHandle()
with ManagedResource(handle) as managed:
    assert managed.closed is False
assert handle.closed is True
assert managed.closed is True
```


### D4. Copy semantics and aliasing — Basic

**What does this print, and why?**

```python
import copy

source = {"tags": ["raw"]}
shallow = copy.copy(source)
deep = copy.deepcopy(source)
source["tags"].append("clean")
print(shallow["tags"])
print(deep["tags"])
```

Explain which objects are shared and why the deep copy remains independent in this example.

### D5. Custom deep copy with a cycle — Advanced

Implement a `Node` class with a `children` list that may contain cycles. Implement `__deepcopy__(self, memo)` correctly so cycles terminate and copied references point to the copied graph. Test both a self-cycle and two nodes that refer to one another. Explain why registering the clone in `memo` early is essential.

**Complete example:**

```python
import copy

class Node:
    def __init__(self, name):
        self.name = name
        self.children = []

    def __deepcopy__(self, memo):
        existing = memo.get(id(self))
        if existing is not None:
            return existing
        clone = type(self).__new__(type(self))
        memo[id(self)] = clone
        clone.name = copy.deepcopy(self.name, memo)
        clone.children = copy.deepcopy(self.children, memo)
        return clone

a = Node("a")
a.children.append(a)
a_copy = copy.deepcopy(a)
assert a_copy is not a
assert a_copy.children[0] is a_copy

a, b = Node("a"), Node("b")
a.children.append(b); b.children.append(a)
clone_a = copy.deepcopy(a)
clone_b = clone_a.children[0]
assert clone_b.children[0] is clone_a
assert clone_a is not a and clone_b is not b
```


### D6. **What does this print, and why?** — Basic

```python
class Sample:
    def __new__(cls, value):
        print("new")
        return super().__new__(cls)

    def __init__(self, value):
        print("init")
        self.value = value

Sample(3)
```

Explain the distinct responsibilities of `__new__` and `__init__`.

### D7. **What does this print, and why?** — Intermediate

```python
import copy

class Box:
    def __init__(self, items):
        self.items = items

original = Box([1, 2])
clone = copy.copy(original)
clone.items.append(3)
print(original.items)
print(original is clone)
print(original.items is clone.items)
```

Explain why the outer object is distinct but its nested list is shared.

### D8. **What does this print, and why?** — Intermediate

```python
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class Job:
    job_id: str
    retries: int

job1 = Job("J-1", 1)
job2 = replace(job1, retries=2)
print(job1.retries, job2.retries, job1 is job2)
```

Explain what `dataclasses.replace` returns and what `frozen=True` does—and does not—guarantee.

### D9. **What does this print, and why?** — Advanced

```python
import pickle

class Record:
    def __init__(self, value):
        self.value = value

record = Record("ok")
restored = pickle.loads(pickle.dumps(record))
print(restored.value)
print(restored is record)
```

Explain why the restored object is not the same identity and list the conditions that normally allow a user-defined class instance to be pickled.

### D10. **What does this print, and why?** — Advanced

```python
import weakref

class Resource:
    pass

events = []
resource = Resource()
finalizer = weakref.finalize(resource, events.append, "released")
print(finalizer.alive)
finalizer()
print(events, finalizer.alive)
```

Explain what calling a `weakref.finalize` object does, why callbacks should not capture the target strongly, and why deterministic context-manager cleanup is still preferable for ordinary resource management.

### D11. Serialization and lifecycle review — Advanced

A data pipeline persists Python objects with pickle in long-lived object storage and later loads payloads uploaded by external users. Identify the security, schema-evolution, portability, and resource-lifecycle risks. Propose a safer design for untrusted payloads and explain when pickle might still be acceptable inside a trusted, versioned system.

---

**Complete safer interchange example (schema-validated JSON):**

```python
import json

def encode_job(job_id: str, retries: int) -> str:
    if not job_id or retries < 0:
        raise ValueError("invalid job fields")
    return json.dumps({"schema_version": 1, "job_id": job_id, "retries": retries})

def decode_job(payload: str) -> dict:
    data = json.loads(payload)
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("unsupported payload schema")
    if not isinstance(data.get("job_id"), str) or not data["job_id"]:
        raise ValueError("invalid job_id")
    retries = data.get("retries")
    if isinstance(retries, bool) or not isinstance(retries, int) or retries < 0:
        raise ValueError("invalid retries")
    return {"job_id": data["job_id"], "retries": retries}

payload = encode_job("J-1", 2)
assert decode_job(payload) == {"job_id": "J-1", "retries": 2}
```


### D12. Reconstruction protocol and `copyreg` — Advanced

Explain the roles of `__reduce__`, `__reduce_ex__`, and `copyreg`. For a small class with a non-trivial constructor, write a minimal reduction strategy that reconstructs the object from importable callable/state data. State why you should first prefer `__getstate__`/`__setstate__` when those hooks are sufficient, and test round-trip behaviour with the supported pickle protocols.

**Complete reduction example:**

```python
import pickle

class PortRange:
    def __init__(self, start, end):
        if not (0 <= start <= end <= 65535):
            raise ValueError("invalid port range")
        self.start, self.end = start, end

    def __reduce__(self):
        return (type(self), (self.start, self.end))

original = PortRange(8000, 8010)
restored = pickle.loads(pickle.dumps(original))
assert (restored.start, restored.end) == (8000, 8010)
assert restored is not original
```


### D13. `copy.replace()` and the replacement protocol — Intermediate

On Python 3.13+, implement `__replace__(self, **changes)` for a small immutable record or use a standard class that supports `copy.replace()`. Compare it with `dataclasses.replace()`. Explain that `copy.replace()` is a shallow field replacement operation, not a deep copy, and note the version requirement. Do not execute this question on Python 3.12.

**Complete Python 3.13+ example (do not run on Python 3.12):**

```python
# Requires Python 3.13+
import copy

class JobRecord:
    def __init__(self, job_id, retries):
        self.job_id, self.retries = job_id, retries

    def __replace__(self, **changes):
        unknown = set(changes) - {"job_id", "retries"}
        if unknown:
            raise TypeError(f"unknown fields: {sorted(unknown)}")
        return type(self)(
            changes.get("job_id", self.job_id),
            changes.get("retries", self.retries),
        )

job = JobRecord("J-1", 1)
updated = copy.replace(job, retries=2)
assert updated.retries == 2 and job.retries == 1
assert updated is not job
```


### D14. Class creation and instance lifecycle hooks — Advanced

Write a descriptor that uses `__set_name__(owner, name)` to learn the attribute name assigned by the class body. Then create a base class using `__init_subclass__` to validate a required class attribute on subclasses. Explain when each hook runs and how each differs from instance construction through `__new__` and `__init__`.

**Complete example:**

```python
class NamedField:
    def __set_name__(self, owner, name):
        self.name = name
        self.storage_name = "_" + name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return getattr(instance, self.storage_name)

    def __set__(self, instance, value):
        setattr(instance, self.storage_name, value)

class PluginBase:
    plugin_name = None
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls is not PluginBase and not isinstance(cls.plugin_name, str):
            raise TypeError("subclasses must define plugin_name")

class CsvPlugin(PluginBase):
    plugin_name = "csv"
    label = NamedField()
    def __init__(self, label):
        self.label = label

p = CsvPlugin("CSV export")
assert p.label == "CSV export"
try:
    class InvalidPlugin(PluginBase):
        pass
except TypeError:
    pass
else:
    raise AssertionError("subclass validation should fail")
```


### D15. Generic classes and type checks — Advanced

Describe what `__class_getitem__` enables for an expression such as `Repository[str]`. Explain the purpose of metaclass hooks `__instancecheck__` and `__subclasscheck__`, and why they are awareness-level topics here rather than a default solution for ordinary application code. Include a short example or pseudocode and identify which hook belongs on a metaclass.

**Complete awareness example:**

```python
class Repository:
    def __class_getitem__(cls, item):
        return (cls.__name__, item)

assert Repository[str] == ("Repository", str)

class HasKeyMeta(type):
    def __instancecheck__(cls, instance):
        return hasattr(instance, "key")

    def __subclasscheck__(cls, subclass):
        return any("key" in base.__dict__ for base in subclass.__mro__)

class HasKey(metaclass=HasKeyMeta):
    pass

class Item:
    key = "id"

assert isinstance(Item(), HasKey)
assert issubclass(Item, HasKey)
```


### D16. Identity, interning, and finalization — Advanced

Explain why `is` should be used for identity (including `x is None`) rather than value comparison, why `id()` values should not be persisted, and why small-integer caching/string interning are implementation details rather than application contracts. Describe object resurrection and interpreter-shutdown ordering issues that make `__del__` unreliable.

## Phase E — Integrated engineering judgment

These questions combine concepts across the module.

### E1. Choose the right abstraction — Advanced

For each requirement, choose among an ABC, `typing.Protocol`, duck typing, a mixin, composition, or a plain function. Justify each choice:

1. Several unrelated exporters must expose `export(data)`.
2. A helper adds a small `to_dict()` method to compatible host objects.
3. A component owns a retry policy with configuration and mutable state.
4. A library should type-check against an interface without requiring inheritance.
5. A one-off transformation has no state and no polymorphic requirement.

**Complete decision-table example:**

```python
from typing import Protocol
from abc import ABC, abstractmethod

class ExporterABC(ABC):
    @abstractmethod
    def export(self, data: object) -> bytes: ...

class ExporterProtocol(Protocol):
    def export(self, data: object) -> bytes: ...

class RetryPolicy:
    def __init__(self, attempts: int):
        if attempts < 1:
            raise ValueError("attempts must be >= 1")
        self.attempts = attempts

    def run(self, operation):
        last_error = None
        for _ in range(self.attempts):
            try:
                return operation()
            except OSError as exc:
                last_error = exc
        raise last_error

def normalize_name(value: str) -> str:
    return value.strip().casefold()

assert normalize_name("  HOST ") == "host"
assert RetryPolicy(2).attempts == 2
```


### E2. Design a robust immutable `Money` — Advanced

Write a compact design specification for `Money`: equality, hash stability, ordering, arithmetic, formatting, currency mismatch behaviour, copying, and serialization. Identify which guarantees come from Python’s data model and which must be implemented by the class. Add a test matrix covering valid, invalid, and boundary cases.

**Complete reference implementation and test matrix:**

```python
from dataclasses import dataclass
from functools import total_ordering

@total_ordering
@dataclass(frozen=True)
class Money:
    minor_units: int
    currency: str

    def __post_init__(self):
        if isinstance(self.minor_units, bool) or not isinstance(self.minor_units, int):
            raise TypeError("minor_units must be int")
        if len(self.currency) != 3 or not self.currency.isalpha() or self.currency != self.currency.upper():
            raise ValueError("currency must be a three-letter uppercase code")

    def __lt__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("cannot order different currencies")
        return self.minor_units < other.minor_units

    def __add__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("cannot add different currencies")
        return Money(self.minor_units + other.minor_units, self.currency)

    def __format__(self, spec):
        amount = self.minor_units / 100
        return f"{amount:{spec}} {self.currency}" if spec else f"{amount:.2f} {self.currency}"

assert Money(100, "USD") == Money(100, "USD")
assert hash(Money(100, "USD")) == hash(Money(100, "USD"))
assert Money(100, "USD") < Money(200, "USD")
assert Money(100, "USD") + Money(25, "USD") == Money(125, "USD")
assert format(Money(125, "USD")) == "1.25 USD"
for bad in ((True, "USD"), (1.5, "USD"), (1, "usd")):
    try:
        Money(*bad)
    except (TypeError, ValueError):
        pass
    else:
        raise AssertionError(f"invalid input accepted: {bad!r}")
```


### E3. Module mini-project — Advanced capstone

Build the roadmap’s `datamodel_kit` mini-project with:

1. `Money` — immutable value object with hash, ordering, arithmetic, currency safety, and formatting.
2. `TypedField` descriptors — validated fields with useful error messages.
3. `FrozenRecord` — a slotted, hashable record base.
4. `OrderedCatalog` — a `MutableMapping` with a slice-aware sequence view.
5. `SerialisableMixin` — JSON round-trip and safe state handling.
6. A benchmark comparing dictionary-backed, slotted, and dataclass records using `tracemalloc` and `timeit`.

Acceptance criteria from the roadmap: at least 90% branch coverage on the public API, clean `ruff` and type-checker runs, a README with usage examples, and a `DESIGN.md` explaining every special method and why it exists. Record Python version and benchmark methodology; do not claim memory or speed improvements without measurements.

---

# Answer key and solution guidance

Use this section only after attempting the questions. For implementation tasks, the guidance identifies the contract and key edge cases; it is not a substitute for writing and running your own tests.

## Phase A guidance

- **A1:** First line is `job J-17`; second line is `[Job('J-17')]`. `print(obj)` uses `str(obj)` while a list represents its elements with `repr`.
- **A2:** Equal objects must have equal hashes. Hash the immutable equality key, such as `hash(self.customer_id)`. If the key can change, do not allow mutation while hashed; prefer an immutable key or make the type unhashable.
- **A3:** Return a constructor-shaped representation, e.g. `Coordinate(-2, 5)`, using `!r` for fields. Never `eval` untrusted representations.
- **A4:** Compare tuples of version components. Return `NotImplemented` for unsupported types. Python then tries the other operand’s reflected comparison where applicable and raises `TypeError` if no comparison succeeds.
- **A5:** Delegate indexing to the backing list; if the index is a `slice`, wrap the sliced list in a new `Batch`. Preserve ordinary `IndexError` semantics.
- **A6:** Prints `True`, then `False`: absent `__bool__`, truthiness uses `__len__`.
- **A7:** Prints `['alpha', 'beta']`. Python’s legacy sequence iteration requests indexes from zero until `IndexError`.
- **A8:** Prints `False`. If both equality implementations decline the comparison with `NotImplemented`, equality falls back to identity. `NotImplementedError` is an exception and is not the same object.
- **A9:** Prints `True`, then `False`. `total_ordering` supplies the missing ordering operations based on `__eq__` and one ordering method; explicit methods can reduce call overhead and clarify edge cases.
- **A10:** Prints `True`, then `TypeError`. Defining `__eq__` without a compatible `__hash__` normally makes the class unhashable.
- **A11:** Normalize keys consistently for lookup, assignment, and membership. `Mapping` mix-ins provide a coherent set of derived operations; `UserDict` can be easier to customize than a built-in `dict` subclass.

## Phase B guidance

- **B1:** Use integer minor units and a currency code. Implement equality/hash on the same immutable fields. Return `NotImplemented` for unrelated operand types; raise a documented `ValueError` (or a domain-specific exception) for currency mismatch.
- **B2:** With the supplied implementation, output is `Vector2D(4, 6) Vector2D(4, 6) True` and `Vector2D(6, 12)`. `__iadd__` mutates and returns `self`, so the alias observes the same updated instance. Without `__iadd__`, `+=` can fall back to `__add__` and rebind the variable.
- **B3:** Validate in the setter and assign through `self.celsius` in `__init__`.
- **B4:** Use a unique per-instance storage name (often a private key in `instance.__dict__`), reject `bool` explicitly, and raise a clear exception when a required field has not been set.
- **B5:** Data descriptors take precedence over the instance dictionary; then non-data descriptors/class attributes are considered, followed by `__getattr__` only if normal lookup fails.
- **B6:** Prints `14` and `18`; the getter calculates from the current `_value`.
- **B7:** Prints `instance`. A descriptor with only `__get__` is non-data; defining `__set__` or `__delete__` makes it a data descriptor.
- **B8:** Prints `12`. The right operand’s `__rmul__` handles `3 * Vector(4)` when integer multiplication cannot handle the vector.
- **B9:** Prints `base`. A property implements descriptor behaviour and takes precedence over the instance dictionary.
- **B10:** Prints `42 42 1`. `cached_property` stores the computed result in the instance dictionary; a slotted class needs a `__dict__` slot for it to work.
- **B11:** Operators should preserve reader expectations; `+` should model addition. Network activity in a property is surprising and hard to test. Prefer explicit methods such as `enqueue()` and `refresh_remote_state()`.

## Phase C guidance

- **C1:** Measure equivalent workloads in the same process and report methodology. A normal instance typically has an instance dictionary; a slotted instance can avoid it, but inheritance, weak references, allocator overhead, and measurement technique affect results.
- **C2:** MRO is `Leaf, Left, Right, Root, object`; output is `Leaf`, `Left`, `Right`, `Root`. Every implementation delegates once with `super()`.
- **C3:** Replace direct base calls with cooperative `super()` and compatible signatures. Ensure every class consumes its own keyword and forwards the rest; the root should not pass unknown keywords to `object.__init__`.
- **C4:** `C(A, B)` requests `A` before `B`, but `B` already requires `A` before `B` in its own MRO. Since `B` is a subclass of `A`, use `class C(B)` or otherwise redesign the hierarchy.
- **C5:** Prefer composition when retry behaviour has its own configuration/state and should be independently tested. A mixin is reasonable only when the host contract and inheritance relationship are clear.
- **C6:** Prints `mixin`, then the MRO names `Service`, `Mixin`, `Base`, `object`.
- **C7:** Prints `['D', 'B', 'C', 'A']`. `super()` follows the runtime instance’s MRO, not merely the class named in the source declaration.
- **C8:** Prints `5`. Empty slots prevent the mixin from adding an instance dictionary; incompatible non-empty layouts can conflict.
- **C9:** Prints `Mixin`. `Mixin.__init__` replaces the inherited initializer and does not delegate to `Base`.
- **C10:** Prints `A B`. Both MROs are valid; base order determines which `f` is found first.
- **C11:** Risks include skipped initialization, duplicate initialization, incompatible signatures, hidden state assumptions, and MRO-dependent behaviour. Refactor toward cooperative keyword forwarding or composed collaborators and add tests for call order and invariants.

## Phase D guidance

- **D1:** Implement `__getitem__`, `__iter__`, and `__len__`; test the inherited mapping views and lookup behaviour.
- **D2:** Copy state without the lock; rebuild a fresh lock in `__setstate__`. This only solves lock picklability, not pickle’s code-execution risk.
- **D3:** Prefer `with` and a context manager for deterministic cleanup. `weakref.finalize` can be a fallback; its callback and arguments must not keep the target alive.
- **D4:** Prints `['raw', 'clean']`, then `['raw']`. The shallow copy shares the nested list; the deep copy duplicates the nested graph in this case.
- **D5:** Create the clone, put `memo[id(self)] = clone` before recursively copying children, then copy the remaining state. This preserves cycles and shared references.
- **D6:** Prints `new`, then `init`. `__new__` creates/returns the instance; `__init__` initializes it if the returned object is an instance of the class.
- **D7:** Prints `[1, 2, 3]`, `False`, `True`. The shallow copy is a different `Box`, but both boxes reference the same list.
- **D8:** Prints `1 2 False`. `replace` returns a new dataclass instance. `frozen=True` prevents ordinary field reassignment but does not recursively freeze mutable objects held by fields.
- **D9:** Prints `ok`, then `False`. A typical instance can be pickled if its class is importable by module and qualified name and its state is picklable, subject to custom reduction/state hooks.
- **D10:** First prints `True`; after explicitly calling the finalizer, prints `['released'] False`. The callback should not strongly capture the target. Use a context manager when deterministic release is required.
- **D11:** Never unpickle untrusted payloads. For untrusted interchange, use a schema-validated data format such as JSON or Protocol Buffers. For trusted internal persistence, version the schema, document compatibility, restrict access, and test migrations.
- **D12:** A reduction protocol describes how to reconstruct an object. Prefer the simpler state hooks when they express the needed state; use `copyreg` for external registration when class modification is not appropriate.
- **D13:** `copy.replace()` is available in Python 3.13+ and delegates to the replacement protocol; it creates a new object with selected fields replaced, without recursively copying all nested state.
- **D14:** `__set_name__` runs when a descriptor is assigned in the class namespace during class creation; `__init_subclass__` runs when a subclass is created. Neither is an instance initializer.
- **D15:** `__class_getitem__` customizes class subscription. `__instancecheck__` and `__subclasscheck__` are normally implemented on a metaclass to customize `isinstance`/`issubclass`; use built-in mechanisms unless custom semantics are genuinely needed.
- **D16:** Identity is distinct from equality; `id()` is only meaningful during an object's lifetime and should not be persisted. Finalizer timing and interpreter shutdown are not deterministic cleanup mechanisms.

## Phase E guidance

- **E1:** ABC for an enforced nominal contract when runtime enforcement is useful; Protocol for structural static typing; duck typing for simple capability-based use; mixin for focused reusable behaviour that intentionally uses a host contract; composition for stateful independent policy; plain function for stateless transformation.
- **E2:** Define equality and hash from the same immutable identity fields; do not hash mutable state; make currency mismatch explicit; test ordering/equality consistency and serialization assumptions.
- **E3:** Treat the acceptance criteria as release gates. Keep examples executable, document trade-offs, and measure benchmarks rather than asserting expected outcomes.

---

## Final self-assessment checklist

- [ ] I can explain identity, aliasing, shallow copy, deep copy, and cyclic object graphs.
- [ ] I can implement `__copy__` and `__deepcopy__` without breaking shared references or cycles.
- [ ] I understand `__new__`, `__init__`, and when immutable subclasses require `__new__`.
- [ ] I can explain pickle reconstruction and implement state hooks for non-picklable fields.
- [ ] I can explain why unpickling untrusted data is unsafe.
- [ ] I can choose deterministic context-manager cleanup over relying on `__del__`.
- [ ] I can use `weakref.finalize` without accidentally retaining the target.
- [ ] I can distinguish Python guarantees from version-specific implementation details.
- [ ] I have completed the integrated `datamodel_kit` mini-project and its tests.

**Compact integrated reference implementation:**

```python
from collections.abc import MutableMapping
from dataclasses import dataclass
import json

@dataclass(frozen=True)
class Money:
    minor_units: int
    currency: str

    def __post_init__(self):
        if isinstance(self.minor_units, bool) or not isinstance(self.minor_units, int):
            raise TypeError("minor_units must be an integer")
        if len(self.currency) != 3 or self.currency != self.currency.upper():
            raise ValueError("currency must be a three-letter uppercase code")

    def __add__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("currency mismatch")
        return Money(self.minor_units + other.minor_units, self.currency)

class PositiveInt:
    def __set_name__(self, owner, name):
        self.storage = "_" + name
    def __get__(self, instance, owner=None):
        if instance is None: return self
        return getattr(instance, self.storage)
    def __set__(self, instance, value):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError("value must be a positive integer")
        object.__setattr__(instance, self.storage, value)

class FrozenRecord:
    __slots__ = ("record_id", "_count", "_sealed")
    count = PositiveInt()
    def __init__(self, record_id, count):
        object.__setattr__(self, "record_id", record_id)
        self.count = count
        object.__setattr__(self, "_sealed", True)
    def __setattr__(self, name, value):
        if getattr(self, "_sealed", False):
            raise AttributeError("FrozenRecord is immutable")
        object.__setattr__(self, name, value)
    def __eq__(self, other):
        if not isinstance(other, FrozenRecord): return NotImplemented
        return (self.record_id, self.count) == (other.record_id, other.count)
    def __hash__(self):
        return hash((self.record_id, self.count))

class OrderedCatalog(MutableMapping):
    def __init__(self): self._data = {}
    def __getitem__(self, key): return self._data[key]
    def __setitem__(self, key, value): self._data[key] = value
    def __delitem__(self, key): del self._data[key]
    def __iter__(self): return iter(self._data)
    def __len__(self): return len(self._data)
    def values_in_order(self): return list(self._data.values())

class SerialisableMixin:
    def to_json(self):
        return json.dumps(self.__dict__)
    @classmethod
    def from_json(cls, payload):
        obj = cls.__new__(cls)
        obj.__dict__.update(json.loads(payload))
        return obj

# Smoke tests: run with Python 3.12+
assert Money(100, "USD") + Money(50, "USD") == Money(150, "USD")
record = FrozenRecord("r-1", 2)
assert record.count == 2 and hash(record) == hash(FrozenRecord("r-1", 2))
catalog = OrderedCatalog()
catalog["job-1"] = {"status": "ready"}
assert catalog["job-1"]["status"] == "ready"
```

This is a compact teaching implementation, not a production-ready library: expand tests, clarify serialization contracts, add ordering and arithmetic rules, and verify branch coverage before treating the capstone as complete.

