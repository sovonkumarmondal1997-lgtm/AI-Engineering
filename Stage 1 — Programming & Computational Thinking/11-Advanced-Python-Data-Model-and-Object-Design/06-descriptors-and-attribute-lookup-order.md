# Lesson 06 — Descriptors and Attribute Lookup Order

**Stage 1 — Programming & Computational Thinking**  
**Module 11 — Advanced Python Data Model and Object Design**  
**Target version:** Python 3.12+  
**Level:** Beginner → intermediate → advanced

> **Source alignment:** This lesson follows the `Lesson 06` requirements in `roadmap-Advanced-Python-Data-Model-and-Object-Design.md`. The core roadmap topics are descriptors and their protocol, data versus non-data descriptors, method binding, `__set_name__`, the four-step instance lookup order, per-instance descriptor storage, class/static methods, `inspect.getattr_static`, `__getattribute__` versus `__getattr__`, `type.__getattribute__` and metaclasses, reusable validated fields, slots, a caching descriptor, typed generic descriptors, performance, common mistakes, and the three roadmap self-check questions. Additional examples are labeled as practical elaborations.

---

## 1. Learning outcomes

By the end of this lesson, you should be able to:

1. Explain what a descriptor is and why descriptors must normally be stored as attributes on a class.
2. Implement `__get__`, `__set__`, `__delete__`, and `__set_name__`.
3. Distinguish data descriptors from non-data descriptors and predict which one wins during lookup.
4. Explain why functions become bound methods when accessed through instances.
5. Apply Python's attribute lookup order without guessing.
6. Store descriptor values separately for each instance instead of accidentally sharing state.
7. Understand how `property`, `classmethod`, `staticmethod`, `__slots__`, and `cached_property` relate to descriptors.
8. Use `inspect.getattr_static` to inspect an attribute without invoking descriptor behavior.
9. Explain why overriding `__getattribute__` carelessly can cause recursion.
10. Build a reusable validated-field descriptor and test its happy and failure paths.
11. Recognize the role of descriptors in data models, validation libraries, and ORM fields.

---

## 2. Why descriptors matter

Descriptors are one of Python's mechanisms for customizing attribute access. They are the machinery behind many familiar features:

- `property` controls reads, writes, and deletes of a named attribute.
- A normal function stored on a class becomes a bound method when accessed through an instance.
- `classmethod` and `staticmethod` customize method binding.
- `__slots__` uses member descriptors to manage fixed per-instance storage.
- `functools.cached_property` computes a value once and caches it on the instance.
- ORM and validation libraries can use descriptors or similar class-level field objects to validate, convert, or load values.

A descriptor is an object whose **type** defines one or more of these methods:

- `__get__(self, instance, owner=None)` — customize reading an attribute;
- `__set__(self, instance, value)` — customize assignment;
- `__delete__(self, instance)` — customize deletion;
- `__set_name__(self, owner, name)` — receive the owner class and attribute name when the class is created (Python 3.6+).

The descriptor instance is commonly placed in a class body:

```text
class Example:
    field = SomeDescriptor()
```

The descriptor object is shared as a class-level object, but the *value it manages* usually belongs to each individual `Example` instance.

---

## 3. A first descriptor

The following descriptor enforces positive numeric values:

```python
class Positive:
    def __set_name__(self, owner: type, name: str) -> None:
        self.private_name = "_" + name

    def __get__(self, instance: object, owner: type | None = None):
        if instance is None:
            return self
        return getattr(instance, self.private_name)

    def __set__(self, instance: object, value: int | float) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{self.private_name[1:]} must be numeric")
        if value <= 0:
            raise ValueError(f"{self.private_name[1:]} must be positive")
        setattr(instance, self.private_name, value)


class Order:
    quantity = Positive()
    price = Positive()

    def __init__(self, quantity: int, price: float) -> None:
        self.quantity = quantity
        self.price = price


order = Order(3, 12.5)
assert order.quantity == 3
assert order.price == 12.5

try:
    order.quantity = 0
except ValueError:
    pass
else:
    raise AssertionError("quantity=0 should be rejected")
```

### What happens?

1. Python creates the `Positive()` descriptor object for the class attribute `quantity`.
2. During class creation, Python calls `__set_name__` so the descriptor learns that it manages the attribute named `quantity`.
3. `Order.__init__` executes `self.quantity = quantity`.
4. Because `quantity` is a data descriptor on the class, Python calls `Positive.__set__`.
5. The descriptor validates the value and stores it on that specific order as `_quantity`.
6. Reading `order.quantity` invokes `Positive.__get__`, which retrieves `order._quantity`.

The same descriptor instance is used for the `quantity` field on every `Order` object. The data itself is not stored in the descriptor; it is stored on each order instance.

---

## 4. The descriptor protocol in detail

### 4.1 `__get__`

The general signature is:

```python
def __get__(self, instance, owner=None):
    ...
```

- `self` is the descriptor object.
- `instance` is the object being accessed, or `None` for class-level access.
- `owner` is the class through which access is occurring.

A common pattern is:

```python
def __get__(self, instance, owner=None):
    if instance is None:
        return self
    return read_value_for(instance)
```

Returning `self` on class access makes `Order.quantity` return the descriptor itself, which is useful for introspection and declarative APIs. A descriptor may intentionally return something else on class access, but that behavior should be designed and documented.

### 4.2 `__set__`

`__set__(self, instance, value)` intercepts assignments such as `order.quantity = 10`. In the complete `Positive` and `Order` example above, this invokes the descriptor's `__set__` method.

Use it for validation, conversion, access control, or controlled storage. If a descriptor defines `__set__`, it is a data descriptor—even if the method always raises `AttributeError`.

### 4.3 `__delete__`

`__delete__(self, instance)` intercepts a statement such as `del record.code`. For example:

```python
class DeletableField:
    def __set_name__(self, owner: type, name: str) -> None:
        self.private_name = "_" + name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return getattr(instance, self.private_name)

    def __set__(self, instance, value) -> None:
        setattr(instance, self.private_name, value)

    def __delete__(self, instance) -> None:
        delattr(instance, self.private_name)


class Record:
    code = DeletableField()

    def __init__(self, code: str) -> None:
        self.code = code


record = Record("A-17")
assert record.code == "A-17"
del record.code
assert not hasattr(record, "code")
```

A delete operation can remove the backing state, reset it, or reject deletion. Choose behavior that preserves the object's invariants.

### 4.4 `__set_name__`

Python calls `__set_name__(owner, name)` automatically for descriptors found directly in the class namespace while the class is created. It is an ideal way to avoid hard-coding the managed attribute name.

```python
class NamedField:
    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return instance.__dict__[self.name]


class Event:
    event_id = NamedField()
    source = NamedField()


assert Event.event_id.name == "event_id"
assert Event.source.name == "source"
```

**Important limitation:** assigning a descriptor to a class *after* class creation does not automatically call `__set_name__`. If you deliberately add descriptors dynamically, you must call `descriptor.__set_name__(Owner, "attribute_name")` yourself and understand the risks of modifying classes at runtime.

---

## 5. Data descriptors versus non-data descriptors

The distinction is about which protocol methods the descriptor's class defines.

| Kind | Protocol methods | Lookup behavior |
|---|---|---|
| Data descriptor | Defines `__set__` and/or `__delete__` (usually also `__get__`) | Takes priority over a same-name instance dictionary entry |
| Non-data descriptor | Defines `__get__` but not `__set__` or `__delete__` | Can be shadowed by a same-name instance dictionary entry |

A property is a data descriptor even if it has no setter. A normal function is a non-data descriptor.

### 5.1 Data descriptor wins over the instance dictionary

```python
class DataField:
    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return "from descriptor"

    def __set__(self, instance, value):
        instance.__dict__["field"] = value


class Example:
    field = DataField()


obj = Example()
obj.__dict__["field"] = "from instance dictionary"
assert obj.field == "from descriptor"
```

Even though the instance dictionary contains `"field"`, the data descriptor wins.

### 5.2 Non-data descriptor can be shadowed

```python
class NonDataField:
    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return "from descriptor"


class Example:
    field = NonDataField()


obj = Example()
assert obj.field == "from descriptor"
obj.__dict__["field"] = "from instance dictionary"
assert obj.field == "from instance dictionary"
```

The non-data descriptor loses to the instance dictionary.

This distinction explains why assigning `obj.method = something_else` can shadow an ordinary method on that one object, while assigning over a property normally invokes its setter or raises `AttributeError`.

---

## 6. Attribute lookup order for `obj.attr`

For ordinary instance attribute access, Python's `object.__getattribute__` follows a precedence model. The roadmap's four-step order is:

1. **Data descriptor on the type**, including attributes found on base classes through the method resolution order (MRO).
2. **Instance `__dict__`**, if the object has one.
3. **Non-data descriptor or plain class attribute** found on the type/MRO.
4. **`__getattr__` fallback**, if defined, when the normal lookup raises `AttributeError`.

The exact implementation has details, but this is the practical precedence model to reason with.

### 6.1 Example: all four layers

```python
class DataDescriptor:
    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return "1: data descriptor"

    def __set__(self, instance, value):
        instance.__dict__["item"] = value


class NonDataDescriptor:
    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return "3: non-data descriptor"


class Demo:
    item = DataDescriptor()
    alternate = NonDataDescriptor()
    plain = "3: plain class attribute"

    def __getattr__(self, name):
        if name == "missing":
            return "4: __getattr__ fallback"
        raise AttributeError(name)


demo = Demo()
demo.__dict__["item"] = "2: instance dictionary, but overridden"
demo.__dict__["alternate"] = "2: instance dictionary wins"
demo.__dict__["plain"] = "2: instance dictionary wins"

assert demo.item == "1: data descriptor"
assert demo.alternate == "2: instance dictionary wins"
assert demo.plain == "2: instance dictionary wins"
assert demo.missing == "4: __getattr__ fallback"
```

### 6.2 Why data descriptors win

A data descriptor usually represents a controlled attribute contract: validation, storage, computed behavior, or a managed field. Giving it priority ensures that an instance dictionary entry cannot bypass that contract through ordinary attribute lookup.

### 6.3 Why non-data descriptors lose

Non-data descriptors allow the instance to override class-provided behavior. Ordinary methods rely on this behavior, which makes instance-level customization and monkeypatching possible.

### 6.4 What if a descriptor raises `AttributeError`?

If the normal lookup path ultimately raises `AttributeError`, `__getattr__` may be called. This means a descriptor can signal that it cannot provide an attribute by raising `AttributeError`, but do not use that behavior casually: it can make an attribute appear absent and activate fallback behavior.

---

## 7. Functions are descriptors: bound methods

A function defined in a class is a descriptor. Access through an instance binds that instance to the function and produces a bound method.

```python
class Worker:
    def run(self, job_id: str) -> str:
        return f"{self.name}:{job_id}"

    def __init__(self, name: str) -> None:
        self.name = name


worker = Worker("ingest-01")
bound = worker.run
assert bound("job-7") == "ingest-01:job-7"
assert bound.__self__ is worker
assert bound.__func__ is Worker.run
```

Conceptually, `worker.run` behaves like binding the function `Worker.run` to `worker`. The instance becomes the `self` argument automatically.

By contrast, `Worker.run` accessed on the class is the function itself; no particular instance is bound. This is why a normal instance method expects its first argument to be supplied when called through the class.

---

## 8. `classmethod` and `staticmethod`

These built-in wrappers participate in descriptor behavior.

```python
class Parser:
    format_name = "json"

    @classmethod
    def describe(cls) -> str:
        return f"parser format={cls.format_name}"

    @staticmethod
    def normalize(value: str) -> str:
        return value.strip().lower()


class SpecialParser(Parser):
    format_name = "csv"


assert Parser.describe() == "parser format=json"
assert SpecialParser.describe() == "parser format=csv"
assert Parser.normalize("  ABC ") == "abc"
```

- A `classmethod` binds the class through which it is accessed as `cls`. This supports subclass-aware constructors and class-level behavior.
- A `staticmethod` does not automatically bind an instance or class. It behaves like a function stored in the class namespace.

You usually do not need to implement these descriptors yourself. Understanding the mechanism helps explain why these decorators behave differently from ordinary functions.

---

## 9. Storage strategies for descriptor values

### 9.1 Store values on the managed instance under a private name

This is the most straightforward pattern:

```python
class Field:
    def __set_name__(self, owner: type, name: str) -> None:
        self.private_name = "_" + name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return getattr(instance, self.private_name)

    def __set__(self, instance, value) -> None:
        setattr(instance, self.private_name, value)
```

The descriptor object is shared, but `_quantity` and `_price` are stored on each `Order` instance separately.

### 9.2 Do not store each instance's value on the descriptor itself

**Incorrect:**

```python
class BrokenField:
    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return self.value

    def __set__(self, instance, value):
        self.value = value


class BrokenOrder:
    quantity = BrokenField()


a = BrokenOrder()
b = BrokenOrder()
a.quantity = 2
b.quantity = 9
assert a.quantity == 9  # demonstrates the bug: both instances share descriptor.value
```

The descriptor is one class-level object, so `self.value` belongs to the descriptor and is shared by all `BrokenOrder` instances. One order overwrites the other order's value.

The assertion above intentionally demonstrates the incorrect behavior; it is not a recommended pattern.

### 9.3 `WeakKeyDictionary` as an alternate storage strategy

A descriptor can store values externally, keyed by the managed instance. A `weakref.WeakKeyDictionary` avoids keeping otherwise-unreferenced instances alive solely because they are keys.

```python
from weakref import WeakKeyDictionary


class ExternalStorageField:
    def __init__(self) -> None:
        self.values = WeakKeyDictionary()

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        try:
            return self.values[instance]
        except KeyError:
            raise AttributeError(self.name) from None

    def __set__(self, instance, value) -> None:
        self.values[instance] = value


class Job:
    state = ExternalStorageField()


first = Job()
second = Job()
first.state = "running"
second.state = "queued"
assert first.state == "running"
assert second.state == "queued"
```

This technique has constraints: instances must be weak-referenceable and usable as dictionary keys (normally hashable). Equality/hash behavior can complicate key semantics. For most simple fields, private storage on the instance is easier to understand.

---

## 10. `inspect.getattr_static`: inspect without triggering descriptors

Normal `getattr(obj, name)` and `obj.name` can execute user-defined code. This may validate, compute, load a value, or raise an exception.

`inspect.getattr_static` retrieves the raw attribute without invoking the descriptor protocol or dynamic `__getattr__` behavior.

```python
import inspect


class Sample:
    @property
    def answer(self) -> int:
        return 42


sample = Sample()
assert sample.answer == 42
raw = inspect.getattr_static(sample, "answer")
assert isinstance(raw, property)
```

This is useful for debugging, introspection tools, and frameworks that need to inspect class declarations without causing side effects. The raw result may be a descriptor object rather than the value that normal attribute access would return.

---

## 11. `__getattribute__` versus `__getattr__`

These methods have different roles:

- `__getattribute__(self, name)` is called for essentially every ordinary instance attribute lookup.
- `__getattr__(self, name)` is a fallback called when normal lookup fails with `AttributeError`.

### 11.1 A safe `__getattr__` fallback

```python
class Environment:
    def __init__(self, values: dict[str, str]) -> None:
        self._values = dict(values)

    def __getattr__(self, name: str) -> str:
        try:
            return self._values[name]
        except KeyError:
            raise AttributeError(name) from None


env = Environment({"REGION": "ap-south-1"})
assert env.REGION == "ap-south-1"
```

`__getattr__` is appropriate when missing attributes should map to another source, such as a configuration mapping. Use it sparingly because it can make typos harder to detect.

### 11.2 Why overriding `__getattribute__` is dangerous

`__getattribute__` runs for nearly every attribute access. If its implementation tries to read `self.name`, that read calls `__getattribute__` again and can recurse forever.

```python
class BrokenLookup:
    def __getattribute__(self, name: str):
        return self.name  # intentionally wrong: every lookup recurses


# Accessing BrokenLookup().anything would raise RecursionError.
```

When a custom `__getattribute__` is truly needed, delegate carefully to `object.__getattribute__`:

```python
class LoggedLookup:
    def __init__(self, value: int) -> None:
        self.value = value

    def __getattribute__(self, name: str):
        # Use the base implementation to avoid re-entering this method.
        return object.__getattribute__(self, name)


logged = LoggedLookup(7)
assert logged.value == 7
```

The example above shows the safe delegation pattern; it does not add logging. In production, prefer properties, descriptors, or `__getattr__` unless the requirement genuinely demands interception of every attribute lookup.

---

## 12. Class-level lookup: `type.__getattribute__` and metaclasses

Instance access and class access are related but not identical.

- For `obj.attr`, `object.__getattribute__` manages normal instance lookup.
- For `SomeClass.attr`, `type.__getattribute__` manages class lookup.
- The class's metaclass can customize class-level lookup because the class object is itself an instance of its metaclass.

A descriptor's `__get__` can receive `instance=None` when the descriptor is accessed through the class. In that case, the `owner` argument indicates the class through which access is taking place.

```python
class OwnerAware:
    def __get__(self, instance, owner=None):
        if instance is None:
            return f"descriptor accessed through {owner.__name__}"
        return f"instance of {owner.__name__}"


class Model:
    marker = OwnerAware()


assert Model.marker == "descriptor accessed through Model"
assert Model().marker == "instance of Model"
```

Metaclasses are useful for framework-level class creation and class-level APIs, but are more complex than ordinary descriptors. For a single instance attribute, use a regular property or descriptor instead of introducing a metaclass without a clear need.

---

## 13. Reusable validated-field descriptor

A descriptor becomes especially useful when many classes need the same field behavior. This example validates types, supports a default, and produces clear errors.

```python
class TypedField:
    def __init__(self, expected_type: type, default=None) -> None:
        self.expected_type = expected_type
        self.default = default

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name
        self.private_name = "_" + name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        try:
            return getattr(instance, self.private_name)
        except AttributeError:
            if self.default is not None:
                return self.default
            raise AttributeError(f"{self.name} has not been set") from None

    def __set__(self, instance, value) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name} must be {self.expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
        setattr(instance, self.private_name, value)


class PipelineSettings:
    name = TypedField(str)
    batch_size = TypedField(int, default=100)

    def __init__(self, name: str) -> None:
        self.name = name


settings = PipelineSettings("daily-orders")
assert settings.name == "daily-orders"
assert settings.batch_size == 100
settings.batch_size = 500
assert settings.batch_size == 500

try:
    settings.batch_size = "500"
except TypeError:
    pass
else:
    raise AssertionError("string batch_size should be rejected")
```

### Important design notes

1. The default above is returned but not written into the instance. If a caller later changes the class descriptor's `default`, an instance without a stored value can observe the new default.
2. `isinstance(True, int)` is `True` in Python. If booleans should not count as integers, add an explicit boolean check.
3. This is a teaching-quality descriptor, not a complete validation framework. Production systems may need coercion policy, required/optional distinction, default factories, error aggregation, serialization, and static typing support.
4. Never store a mutable default list or dictionary on the descriptor and return the same object for every instance. Use a `default_factory` or create per-instance values.

### A default factory for mutable defaults

```python
class ListField:
    def __init__(self, default_factory=list) -> None:
        self.default_factory = default_factory

    def __set_name__(self, owner: type, name: str) -> None:
        self.private_name = "_" + name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if not hasattr(instance, self.private_name):
            setattr(instance, self.private_name, self.default_factory())
        return getattr(instance, self.private_name)

    def __set__(self, instance, value) -> None:
        if not isinstance(value, list):
            raise TypeError("value must be a list")
        setattr(instance, self.private_name, value)


class TableSchema:
    columns = ListField()


left = TableSchema()
right = TableSchema()
left.columns.append("order_id")
assert left.columns == ["order_id"]
assert right.columns == []
```

Each instance gets its own list. The factory is called when the field is first read, so this descriptor is intentionally lazy.

---

## 14. Descriptors and `__slots__`

`__slots__` is not merely a memory optimization. Slot declarations are implemented using member descriptors that control access to fixed storage locations.

```python
class SlottedPoint:
    __slots__ = ("x", "y")

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


point = SlottedPoint(2, 5)
assert point.x == 2
assert isinstance(vars(SlottedPoint)["x"], type(SlottedPoint.x))
```

A slotted class without a `__dict__` does not allow arbitrary new instance attributes. A custom descriptor that stores data in `instance.__dict__` therefore will not work on such an instance unless the class includes `__dict__` in its slots. Alternative designs include using an available slot as storage or a carefully designed external store.

Do not assume that a descriptor's private storage name is available just because it is named `_field`. The owning class must have a compatible storage mechanism.

---

## 15. Implementing a caching descriptor

The roadmap asks you to understand a caching descriptor and why `cached_property` is a non-data descriptor. The following simplified implementation caches the first computed result in the instance dictionary.

```python
class SimpleCached:
    def __init__(self, function) -> None:
        self.function = function
        self.name = function.__name__

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        cache = instance.__dict__
        if self.name not in cache:
            cache[self.name] = self.function(instance)
        return cache[self.name]


class Report:
    def __init__(self, amounts: list[int]) -> None:
        self.amounts = list(amounts)
        self.calls = 0

    @SimpleCached
    def total(self) -> int:
        self.calls += 1
        return sum(self.amounts)


report = Report([10, 20])
assert report.total == 30
assert report.total == 30
assert report.calls == 1
```

### Why is this a non-data descriptor?

`SimpleCached` defines `__get__` but not `__set__` or `__delete__`. After the first access, `report.__dict__["total"]` contains the computed value. On later access, the instance dictionary entry wins over the non-data descriptor, so the descriptor is not called again.

### Cache invalidation

This simple implementation does not know when `amounts` changes. If the underlying data is mutated, `total` may be stale. A production implementation needs an explicit invalidation policy, immutable dependencies, or a versioned cache.

```python
report = Report([1, 2])
assert report.total == 3
report.amounts.append(7)
assert report.total == 3  # intentionally demonstrates stale cached data
report.__dict__.pop("total", None)
assert report.total == 10
```

This cache does not include thread synchronization. If concurrent first access could run expensive or side-effectful computation more than once, design explicit synchronization or avoid caching side effects.

---

## 16. Typing descriptors

Descriptors can be generic and can use overloaded `__get__` signatures to express different return types for class-level and instance-level access. This is an advanced typing topic because descriptor access has two distinct cases.

A simplified sketch:

```python
from typing import Generic, TypeVar, overload

T = TypeVar("T")


class TypedValue(Generic[T]):
    def __init__(self, initial: T) -> None:
        self.initial = initial

    @overload
    def __get__(self, instance: None, owner: type | None = None) -> "TypedValue[T]":
        ...

    @overload
    def __get__(self, instance: object, owner: type | None = None) -> T:
        ...

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return self.initial
```

This is a typing demonstration, not a complete storage descriptor: it returns the same initial value for every instance. A real implementation should store each value per instance and should be checked with the project's static type checker. Different type checkers can require slightly different overload annotations depending on the descriptor design.

---

## 17. Descriptors in data engineering and application frameworks

Descriptors are useful when the same attribute policy must be applied consistently across many fields or classes.

### 17.1 Data validation

A reusable field can enforce that `batch_size` is a positive integer or that `source_name` is a non-empty string. Centralizing validation prevents each model from implementing subtly different rules.

### 17.2 ORM fields and lazy loading

ORMs can use class-level field objects to describe columns and intercept access. An attribute read may return a value already loaded into memory, perform conversion, or trigger lazy loading. Such behavior is powerful, but hidden database I/O can make code costs unpredictable; know the framework's loading behavior and query plan.

### 17.3 Configuration models

A descriptor can normalize environment names, validate a region or retry policy, and supply a default. For complex validation requirements, use a well-established library rather than building a large custom framework without a strong reason.

### 17.4 Avoid surprising side effects

A descriptor getter can run arbitrary Python code. Do not assume `obj.field` is always a simple dictionary lookup. If reading a field performs network calls, database queries, or expensive transformations, document that behavior and consider an explicit method.

---

## 18. Performance and debugging

Attribute access is common, and descriptors add behavior to the lookup path. Python implementations such as CPython use adaptive/specializing interpreter optimizations, so do not assume a custom descriptor is slow—or fast—without measurement.

Practical rules:
- Prefer a plain attribute when no special behavior is required.
- Use properties for a small amount of behavior tied to one named attribute.
- Use a reusable descriptor when many fields need the same policy.
- Keep descriptor getters and setters simple and predictable.
- Benchmark representative workloads before optimizing attribute access.
- For large tabular data, columnar tools such as pandas or Arrow are often more appropriate than creating millions of Python objects with elaborate descriptors.
- Avoid overriding `__getattribute__` merely to log reads; it can complicate correctness and performance.

For debugging:
- use `vars(SomeClass)` to inspect the class namespace;
- use `inspect.getattr_static(obj, "name")` to avoid triggering descriptor behavior;
- inspect `obj.__dict__` when available to see stored instance state;
- remember that a descriptor's `__get__` may return a computed value, not the descriptor object itself.

---

## 19. Common mistakes and how to prevent them

### Mistake 1 — storing the value on the descriptor

**Why it fails:** one descriptor instance is shared by all instances of the owner class.

**Fix:** store data on the managed instance under a private name, or use a deliberate external per-instance store.

### Mistake 2 — forgetting `instance is None`

**Why it fails:** class access such as `Order.quantity` may attempt to read an instance field when no instance exists.

**Fix:** handle class-level access explicitly. Returning `self` is a common choice.

### Mistake 3 — confusing data and non-data descriptors

**Why it fails:** the instance dictionary can shadow a non-data descriptor but not a data descriptor under ordinary lookup.

**Fix:** identify whether the descriptor's class defines `__set__` or `__delete__`, then apply the lookup order.

### Mistake 4 — overriding `__getattribute__` and recursively accessing `self`

**Why it fails:** the new attribute access invokes `__getattribute__` again.

**Fix:** use `object.__getattribute__(self, name)` inside an override, and only override it when genuinely necessary.

### Mistake 5 — forgetting `__set_name__` on dynamically added descriptors

**Why it fails:** Python automatically calls `__set_name__` during class creation, not whenever an attribute is later assigned to the class.

**Fix:** call it deliberately if adding a descriptor dynamically, or avoid dynamic descriptor installation.

### Mistake 6 — using a shared mutable default

**Why it fails:** all instances can receive the same list or dictionary.

**Fix:** use a default factory that creates a fresh object for each instance.

### Mistake 7 — assuming slots provide a `__dict__`

**Why it fails:** a slotted class may not have an instance dictionary, and a descriptor may depend on one.

**Fix:** choose storage compatible with the class layout and test the slotted case.

---

## 20. Exercises

Attempt these before reading the solutions.

### Exercise 1 — positive integer field

Implement a descriptor `PositiveInt` that accepts integers greater than zero, rejects booleans, and stores each instance's value separately. Use it for `Task.retries`.

### Exercise 2 — lookup precedence

Create a class with:
- a data descriptor named `status`;
- a non-data descriptor named `label`;
- a plain class attribute named `kind`;
- an instance dictionary entry for each name.

Predict and then test which value each access returns.

### Exercise 3 — method binding

Create a class with a method `run`. Show the difference between `obj.run` and `Class.run`, and inspect `obj.run.__self__` and `obj.run.__func__`.

### Exercise 4 — lazy validated field

Extend `TypedField` to accept a `default_factory`. Confirm that two instances receive different list objects.

### Exercise 5 — safe introspection

Create a property whose getter increments a counter. Compare `getattr(obj, "value")` with `inspect.getattr_static(obj, "value")` and explain why only one invokes the getter.

### Exercise 6 — caching descriptor

Implement a descriptor that caches a computed total. Add an explicit `invalidate_total()` method to the owner class and test the cache before and after invalidation.

### Exercise 7 — data engineering design review

A team proposes a descriptor that runs a SQL query every time `pipeline.latest_count` is accessed. Identify the design risks and suggest a clearer API.

### Exercise 8 — debugging recursion

Explain why this override is broken, then fix it:

```python
class Broken:
    def __getattribute__(self, name):
        return self.__dict__[name]
```

---

## 21. Exercise solutions

### Solution 1

```python
class PositiveInt:
    def __set_name__(self, owner, name):
        self.private_name = "_" + name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return getattr(instance, self.private_name)

    def __set__(self, instance, value):
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{self.private_name[1:]} must be an integer")
        if value <= 0:
            raise ValueError(f"{self.private_name[1:]} must be positive")
        setattr(instance, self.private_name, value)


class Task:
    retries = PositiveInt()

    def __init__(self, retries):
        self.retries = retries


task_a = Task(1)
task_b = Task(3)
assert task_a.retries == 1
assert task_b.retries == 3
```

### Solution 2

```python
class Data:
    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return "data descriptor"

    def __set__(self, instance, value):
        instance.__dict__["status"] = value


class NonData:
    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return "non-data descriptor"


class Lookup:
    status = Data()
    label = NonData()
    kind = "class kind"


obj = Lookup()
obj.__dict__["status"] = "instance status"
obj.__dict__["label"] = "instance label"
obj.__dict__["kind"] = "instance kind"

assert obj.status == "data descriptor"
assert obj.label == "instance label"
assert obj.kind == "instance kind"
```

### Solution 3

```python
class Runner:
    def run(self, job: str) -> str:
        return f"{self.name}:{job}"

    def __init__(self, name: str) -> None:
        self.name = name


runner = Runner("worker")
assert runner.run("sync") == "worker:sync"
assert runner.run.__self__ is runner
assert runner.run.__func__ is Runner.run
assert Runner.run(runner, "sync") == "worker:sync"
```

### Solution 4

```python
class FactoryListField:
    def __init__(self, default_factory=list):
        self.default_factory = default_factory

    def __set_name__(self, owner, name):
        self.private_name = "_" + name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if not hasattr(instance, self.private_name):
            setattr(instance, self.private_name, self.default_factory())
        return getattr(instance, self.private_name)

    def __set__(self, instance, value):
        if not isinstance(value, list):
            raise TypeError("expected a list")
        setattr(instance, self.private_name, value)


class Schema:
    columns = FactoryListField()


a, b = Schema(), Schema()
a.columns.append("id")
assert a.columns == ["id"]
assert b.columns == []
assert a.columns is not b.columns
```

### Solution 5

`getattr(obj, "value")` performs normal attribute access and invokes the property's getter. `inspect.getattr_static(obj, "value")` retrieves the raw property object without invoking it. The latter is useful when inspecting declarations without triggering arbitrary code.

### Solution 6

```python
class CachedTotal:
    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if self.name not in instance.__dict__:
            instance.__dict__[self.name] = sum(instance.amounts)
        return instance.__dict__[self.name]


class Ledger:
    total = CachedTotal()

    def __init__(self, amounts):
        self.amounts = list(amounts)

    def invalidate_total(self):
        self.__dict__.pop("total", None)


ledger = Ledger([2, 3])
assert ledger.total == 5
ledger.amounts.append(4)
assert ledger.total == 5
ledger.invalidate_total()
assert ledger.total == 9
```

### Solution 7

The attribute looks cheap but may block, incur database cost, fail due to network/warehouse issues, or execute a query repeatedly in loops. Prefer an explicit method such as `pipeline.fetch_latest_count()` or `pipeline.refresh_metrics()` with clear caching, timeout, and error behavior. If the value is already loaded and in-memory, a property may be reasonable.

### Solution 8

The override uses `self.__dict__`, which itself triggers `__getattribute__`, causing recursion. Use the base implementation:

```python
class Safe:
    def __init__(self, value: int) -> None:
        self.value = value

    def __getattribute__(self, name: str):
        return object.__getattribute__(self, name)


assert Safe(4).value == 4
```

---

## 22. Roadmap self-check

Answer these three questions exactly as framed by the roadmap.

1. **Order the four steps of attribute lookup and justify why data descriptors win over the instance dictionary.**
2. **Why is `quantity = Positive()` shared state a bug if you store the value on `self.value` of the descriptor?**
3. **What does `Order.quantity` return and why?**

### Answer key

1. Data descriptor on the type/MRO → instance `__dict__` → non-data descriptor or plain class attribute → `__getattr__` fallback. Data descriptors take precedence so managed attribute behavior such as validation cannot be bypassed by placing a same-name entry in the instance dictionary.
2. `quantity = Positive()` creates one descriptor object shared by the class. If values are stored on the descriptor itself, all instances use the same storage and overwrite each other's values. Store per-instance values on the managed object or in a dedicated per-instance external store.
3. In the provided `Positive` implementation, `Order.quantity` returns the descriptor object itself because `__get__` checks whether `instance is None`. Class access passes no managed instance, and returning `self` allows inspection of the descriptor declaration.

---

## 23. Readiness checklist

Before moving to Lesson 07, make sure you can:

- [ ] Define a descriptor and explain `__get__`, `__set__`, and `__delete__`.
- [ ] Explain the difference between data and non-data descriptors.
- [ ] Use `__set_name__` to learn a field's declared name.
- [ ] Predict which value wins when class attributes, descriptors, and instance dictionary entries share a name.
- [ ] Explain how `obj.method` becomes a bound method.
- [ ] Explain how `classmethod` and `staticmethod` differ.
- [ ] Store data per instance rather than on the shared descriptor object.
- [ ] Inspect an attribute with `inspect.getattr_static`.
- [ ] Distinguish `__getattribute__` from `__getattr__` and avoid recursion.
- [ ] Explain how slots and cached properties relate to descriptors.
- [ ] Write and test a reusable validation descriptor.
- [ ] Explain when a descriptor is appropriate and when a plain attribute or property is simpler.

---

## 24. Key takeaways

1. A descriptor customizes attribute access through methods such as `__get__`, `__set__`, and `__delete__`.
2. Descriptors normally live on the class; per-instance values should not be stored on the shared descriptor object.
3. Data descriptors take precedence over the instance dictionary; non-data descriptors can be shadowed by it.
4. Functions are descriptors, which explains normal method binding.
5. `__set_name__` gives a descriptor its declared owner and attribute name at class creation.
6. `__getattr__` is a fallback; `__getattribute__` intercepts ordinary lookup and is easier to misuse.
7. Use descriptors when attribute behavior should be reusable across many fields. Keep the implementation simple, test edge cases, and measure performance before optimizing.

**Next lesson:** `07-slots-and-memory-layout.md`.
