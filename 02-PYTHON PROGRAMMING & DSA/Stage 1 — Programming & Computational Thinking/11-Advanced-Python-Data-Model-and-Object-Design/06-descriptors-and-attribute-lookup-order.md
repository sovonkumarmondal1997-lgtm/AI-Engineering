# Lesson 06 — Descriptors and Attribute Lookup Order

> **Module 11 — Advanced Python Data Model and Object Design**  
> Target runtime: Python 3.12+  
> Prerequisites: classes, instance attributes, inheritance/MRO, properties, `__slots__`, type annotations, and basic exceptions.

## Learning objectives

By the end of this lesson, you should be able to:

- Explain why descriptors are class-level objects and how `__get__`, `__set__`, `__delete__`, and `__set_name__` participate in attribute access.
- Distinguish data descriptors from non-data descriptors and explain their precedence.
- Predict ordinary instance attribute lookup, including inheritance and `__getattr__`.
- Explain how functions, `classmethod`, `staticmethod`, properties, and slot attributes use descriptor behavior.
- Build a reusable, typed field descriptor with defaults, optional coercion, validation, and actionable errors.
- Store state per instance without leaking data between instances.
- Inspect attributes without invoking their descriptors and safely customize attribute access.
- Recognize descriptor behavior in caching, typing, metaclasses, and performance-sensitive code.
- Test descriptor behavior, including class access, validation, missing values, inheritance, and independent instance state.

## 1. Mental model: an attribute can be behavior, not just stored data

An ordinary instance attribute is often a name/value entry in `obj.__dict__`:

```python
class User:
    def __init__(self, name: str) -> None:
        self.name = name

user = User("Asha")
print(user.__dict__)
print(user.name)
```

Expected output:

```text
{'name': 'Asha'}
Asha
```

But `obj.name` does not always mean “read the `name` key from the instance dictionary.” Python may find a class-level object that controls reading, assignment, or deletion. Such an object is a **descriptor**.

A descriptor is an object whose **type** defines one or more of these methods:

- `__get__(self, instance, owner=None)` — controls attribute reads.
- `__set__(self, instance, value)` — controls assignment.
- `__delete__(self, instance)` — controls deletion.
- `__set_name__(self, owner, name)` — receives the owner class and attribute name when the class is created (Python 3.6+).

A descriptor generally has to be placed on a class to participate in the normal descriptor protocol. Putting a descriptor object only in an instance dictionary does not make `obj.attr` invoke its `__get__` method.

### Why descriptors matter

Descriptors are the mechanism behind properties, bound instance methods, `classmethod`, `staticmethod`, slot attributes, and many reusable field systems in ORMs and validation libraries. A descriptor centralizes behavior that would otherwise be duplicated across many classes.

A descriptor object is normally created once when the class body is executed. Every instance of that class refers to the same descriptor object. Therefore, **the descriptor itself must not hold a single mutable value intended to represent each instance's field value**. Instance-specific values belong on each instance or in an external per-instance store.

## 2. The descriptor protocol

### 2.1 A minimal read-only descriptor

```python
from __future__ import annotations

class UppercaseView:
    def __set_name__(self, owner: type, name: str) -> None:
        self._storage_name = f"_{name}"

    def __get__(self, instance: object | None, owner: type | None = None) -> str | "UppercaseView":
        if instance is None:
            return self
        value = getattr(instance, self._storage_name)
        return str(value).upper()


class Record:
    def __init__(self, code: str) -> None:
        self._code = code

    code = UppercaseView()


record = Record("ab-12")
print(record.code)
print(Record.code is Record.__dict__["code"])
```

Expected output:

```text
AB-12
True
```

`Record.code` invokes `__get__` with `instance=None`; this lesson's descriptor returns itself for class access. `record.code` invokes it with the actual `record`.

**Important:** the exact return value for class access is a descriptor design choice. Returning the descriptor itself is common and useful, but not a universal requirement. Some descriptors intentionally return metadata or a different object.

### 2.2 Data versus non-data descriptors

Classification depends on methods defined on the descriptor's **class**:

| Kind | Protocol methods | Precedence against `instance.__dict__` | Typical examples |
|---|---|---|---|
| **Data descriptor** | Defines `__set__` and/or `__delete__` | If it also defines `__get__`, its read result takes precedence over a same-named instance entry | `property` (even without a setter), slot member descriptors |
| **Non-data descriptor** | Defines `__get__`, but neither `__set__` nor `__delete__` | Can be shadowed by an instance-dictionary entry | Python functions used as methods, `functools.cached_property` |

A descriptor with `__get__` and `__set__` is a data descriptor. A descriptor with `__get__` and `__delete__` is also a data descriptor. A descriptor with only `__set__` or only `__delete__` participates in the data-descriptor category, although a normal read may still follow the descriptor protocol's applicable behavior.

A `property` is a data descriptor even if no setter was supplied. Thus a read-only property cannot be overridden simply by writing a same-named key into an ordinary instance dictionary; assignment normally raises `AttributeError`.

**Protocol edge case:** a descriptor that defines `__set__` or `__delete__` but has no `__get__` is classified as a data descriptor, but it has no getter to invoke. On reads, an instance-dictionary entry can still supply the value in CPython's normal lookup path. The familiar “data descriptors beat the instance dictionary” rule concerns descriptors that provide a `__get__` result (as properties and slot member descriptors do).

#### Demonstrate precedence

```python
class ReadField:
    def __get__(self, instance: object | None, owner: type | None = None) -> str:
        if instance is None:
            return "class access"
        return "descriptor value"


class WriteField:
    def __get__(self, instance: object | None, owner: type | None = None) -> str:
        if instance is None:
            return "class access"
        return "descriptor value"

    def __set__(self, instance: object, value: object) -> None:
        instance.__dict__["_stored"] = value


class Example:
    non_data = ReadField()
    data = WriteField()


item = Example()
item.__dict__["non_data"] = "instance value"
item.__dict__["data"] = "direct dictionary value"
print(item.non_data)
print(item.data)
```

Expected output:

```text
instance value
descriptor value
```

The first descriptor loses to `item.__dict__`; the second wins because it is a data descriptor. The direct dictionary write in the second case intentionally bypasses the descriptor's setter and is shown only to make the lookup precedence visible. Normal assignment `item.data = value` invokes `WriteField.__set__`.

### 2.3 What the hooks receive

Conceptually, when a descriptor is found as a class attribute:

- Instance read `obj.field` calls `descriptor.__get__(obj, type(obj))`.
- Class read `Owner.field` calls `descriptor.__get__(None, Owner)` through the class lookup machinery when the descriptor applies.
- Assignment `obj.field = value` calls `descriptor.__set__(obj, value)` for a data descriptor.
- Deletion `del obj.field` calls `descriptor.__delete__(obj)` when implemented.
- During class creation, `descriptor.__set_name__(Owner, "field")` is called for descriptors present in the class namespace.

The hooks are special methods looked up on the descriptor's type; adding a `__get__` attribute to an individual descriptor instance does not normally make it a descriptor.

### 2.4 `__set_name__` and inheritance

`__set_name__` is called automatically for attributes in a newly created class namespace. It is **not automatically rerun merely because a descriptor is assigned to a class later**, nor is it automatically called again for inherited descriptors. If installing a descriptor dynamically, call its `__set_name__(Owner, name)` explicitly when appropriate.

```python
class NamedField:
    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name
        self.owner = owner


class Parent:
    identifier = NamedField()


class Child(Parent):
    pass


print(Parent.identifier.name)
print(Child.identifier.name)
print(Parent.identifier.owner.__name__)
```

Expected output:

```text
identifier
identifier
Parent
```

`Child` inherits the same descriptor object; its `__set_name__` was not called again for `Child`. If a subclass replaces the descriptor with a new one in its own class body, that new descriptor receives the subclass and its declared name.

## 3. Attribute lookup: the order that matters

For ordinary instance access `obj.attr`, the default lookup path is implemented by `object.__getattribute__`. A useful conceptual sequence is:

1. Find the first matching `attr` in `type(obj).__mro__` (the class and its bases, in MRO order).
2. If that class attribute is a **data descriptor with `__get__`**, invoke its `__get__` and return its result.
3. Otherwise, if `obj` has an instance dictionary containing `attr`, return that value.
4. Otherwise, if the class attribute exists, invoke it as a **non-data descriptor** if it has `__get__`; otherwise return the plain class attribute.
5. If normal lookup raises `AttributeError`, `__getattr__` may provide a fallback value.

This is a teaching model for the default path. Custom `__getattribute__`, metaclasses, custom descriptors, and special class lookup paths can change what happens. Also, the fallback is not simply “try `__getattr__` after any exception”: it is specifically used when attribute lookup raises `AttributeError`.

### Lookup table

| Priority | Candidate | Result |
|---:|---|---|
| 1 | Data descriptor with `__get__` found on the type/MRO | Descriptor result; it takes precedence over same-named instance data |
| 2 | `obj.__dict__[attr]`, if present | Instance value |
| 3 | Non-data descriptor found on the type/MRO | Result of `descriptor.__get__(obj, type(obj))` |
| 3 | Plain class attribute found on the type/MRO | Class attribute value |
| 4 | `obj.__getattr__(attr)`, if defined | Fallback only after normal lookup raises `AttributeError` |

A practical nuance: “find the class attribute” means normal class/MRO lookup, not merely `type(obj).__dict__`. An inherited descriptor can therefore govern an attribute on a subclass instance.

### Flow diagram

```text
obj.attr
   |
   v
object.__getattribute__(obj, "attr")
   |
   v
Find attr in type(obj).__mro__
   |
   +-- data descriptor with __get__? -- yes --> descriptor.__get__(obj, type(obj))
   |
   no
   |
   +-- attr in obj.__dict__? -- yes --> instance value
   |
   no
   |
   +-- class attribute found? -- yes --> non-data __get__ or plain class value
   |
   no / normal lookup raises AttributeError
   |
   v
__getattr__(obj, "attr"), if defined
```

### Why data descriptors win

A data descriptor has an assignment/deletion hook and is intended to control the attribute rather than act as a passive default. Giving it precedence ensures that its validation, computed behavior, or storage policy cannot be bypassed by an ordinary same-named instance attribute.

A non-data descriptor behaves more like a default behavior supplied by the class. Allowing the instance dictionary to win makes method shadowing possible:

```python
class Greeter:
    def greet(self) -> str:
        return "hello from the class"


g = Greeter()
print(g.greet())
g.greet = lambda: "hello from the instance"
print(g.greet())
print(Greeter.greet)
```

Expected output (the final line is a function representation and is implementation-specific):

```text
hello from the class
hello from the instance
<function Greeter.greet at ...>
```

The function stored on `Greeter` is a non-data descriptor. When retrieved through an instance, it normally creates a bound method; the instance assignment then shadows that class attribute.

## 4. Functions are descriptors: bound methods

A Python function stored in a class implements `__get__`. Access through an instance produces a bound method that remembers the instance in its `__self__` attribute; calling it passes that instance as the first argument.

```python
class Counter:
    def add(self, amount: int) -> int:
        return amount + 1


counter = Counter()
function_on_class = Counter.__dict__["add"]
bound_method = counter.add

print(callable(function_on_class))
print(bound_method.__self__ is counter)
print(bound_method.__func__ is function_on_class)
print(counter.add(4))
```

Expected output:

```text
True
True
True
5
```

The conceptual relationship is:

```python
bound_method = function_on_class.__get__(counter, Counter)
```

Do not normally call `__get__` manually in application code; this expression illustrates the descriptor mechanism.

## 5. `classmethod` and `staticmethod`

Both are descriptor-based wrappers, but their binding behavior differs:

- A `classmethod` binds the class (the class through which it was accessed, including a subclass) as the first argument.
- A `staticmethod` returns the wrapped callable without binding either an instance or a class.

```python
class Base:
    @classmethod
    def make(cls) -> str:
        return cls.__name__

    @staticmethod
    def combine(left: int, right: int) -> int:
        return left + right


class Child(Base):
    pass


print(Base.make())
print(Child.make())
print(Base.combine(2, 3))
print(Child.combine(4, 5))
```

Expected output:

```text
Base
Child
5
9
```

Use `classmethod` when behavior should depend on the actual class, such as an alternative constructor. Use `staticmethod` for a function logically grouped in the class namespace but requiring no implicit first argument.

For inspection, `Base.__dict__["make"]` is a `classmethod` descriptor wrapper, while `Base.make` is the bound class method. Similarly, `Base.__dict__["combine"]` is a `staticmethod` wrapper, while `Base.combine` is the underlying callable on modern Python versions.

## 6. Build a reusable validated-field descriptor

This section implements a field descriptor appropriate for configuration objects, ETL records, and simple model layers. It supports:

- Required fields or a default value.
- Optional coercion before validation.
- A validator predicate.
- A private per-instance storage name.
- Clear errors that identify the field and rejected value.
- Class access that returns the descriptor for introspection.
- Independent state for each model instance.

This is a teaching example, not a replacement for a mature validation library. Production frameworks must also consider serialization, aliases, schema generation, thread safety, inheritance policy, and richer error aggregation.

### 6.1 Incorrect: store the field value on the descriptor

```python
# INCORRECT: all instances share this descriptor object.
class BrokenField:
    def __get__(self, instance: object | None, owner: type | None = None) -> object:
        if instance is None:
            return self
        return self.value

    def __set__(self, instance: object, value: object) -> None:
        self.value = value


class BrokenRecord:
    quantity = BrokenField()


first = BrokenRecord()
second = BrokenRecord()
first.quantity = 10
second.quantity = 99
print(first.quantity, second.quantity)
```

Expected output demonstrating the bug:

```text
99 99
```

`BrokenRecord.quantity` is created once. `first.quantity = 10` and `second.quantity = 99` both mutate the same descriptor object's `value` attribute. The second write overwrites the first instance's value.

### 6.2 Correct: store values per instance

```python
from __future__ import annotations

from collections.abc import Callable
from typing import Any, Generic, TypeVar, overload

T = TypeVar("T")


class Field(Generic[T]):
    """Reusable data descriptor with coercion, validation, and per-instance storage.

    Instances must provide a mutable __dict__. Use explicit backing slots or
    another storage strategy for slots-only classes.
    """

    def __init__(
        self,
        expected_type: type[T],
        *,
        default: T | object = ...,
        default_factory: Callable[[], T] | None = None,
        coerce: Callable[[object], T] | None = None,
        validator: Callable[[T], bool] | None = None,
    ) -> None:
        if default is not ... and default_factory is not None:
            raise ValueError("provide either default or default_factory, not both")
        self.expected_type = expected_type
        self.default = default
        self.default_factory = default_factory
        self.coerce = coerce
        self.validator = validator
        self.name = "<unbound>"
        self.storage_name = "<unbound>"

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name
        self.storage_name = f"_{name}"
        # Validate/coerce a fixed default once the field name is known. A
        # default_factory is evaluated and validated separately for each object.
        if self.default is not ...:
            self.default = self._prepare(self.default)

    def _prepare(self, value: object) -> T:
        original_value = value
        if self.expected_type is int and isinstance(value, bool):
            raise TypeError(f"{self.name!r} must be int, not bool")
        if self.coerce is not None:
            try:
                value = self.coerce(value)
            except (TypeError, ValueError, OverflowError) as exc:
                raise TypeError(
                    f"{self.name!r} could not coerce {original_value!r}: {exc}"
                ) from exc
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name!r} must be {self.expected_type.__name__}; "
                f"got {type(value).__name__} ({value!r})"
            )
        typed_value = value
        if self.validator is not None and not self.validator(typed_value):
            raise ValueError(f"{self.name!r} rejected value {typed_value!r}")
        return typed_value

    @overload
    def __get__(self, instance: None, owner: type | None = None) -> Field[T]: ...

    @overload
    def __get__(self, instance: object, owner: type | None = None) -> T: ...

    def __get__(self, instance: object | None, owner: type | None = None) -> Field[T] | T:
        if instance is None:
            return self
        namespace = vars(instance)
        if self.storage_name in namespace:
            return namespace[self.storage_name]
        if self.default is not ...:
            # Fixed defaults should be immutable; use default_factory for
            # mutable per-instance defaults.
            namespace[self.storage_name] = self.default
            return namespace[self.storage_name]
        if self.default_factory is not None:
            value = self._prepare(self.default_factory())
            namespace[self.storage_name] = value
            return value
        raise AttributeError(
            f"{type(instance).__name__}.{self.name} has not been set"
        )

    def __set__(self, instance: object, value: object) -> None:
        typed_value = self._prepare(value)
        vars(instance)[self.storage_name] = typed_value

    def __delete__(self, instance: object) -> None:
        namespace = vars(instance)
        if self.storage_name not in namespace:
            raise AttributeError(f"{self.name!r} has no stored value to delete")
        del namespace[self.storage_name]

```

The descriptor is a data descriptor because it defines both `__set__` and `__delete__`. Values live under names such as `_quantity` in each individual object's `__dict__`, not in `self` (the descriptor). A slots-only instance without `__dict__` is unsupported by this particular `Field` implementation.

**Default semantics:** a fixed default is validated/coerced when `__set_name__` runs and stored on an instance the first time the field is read. Use immutable fixed defaults (numbers, strings, tuples of immutable values). For mutable defaults, use `default_factory`, which is called and validated once per instance on first access. Supplying both `default` and `default_factory` raises `ValueError`. This implementation uses `vars(instance)`, so `Field` requires an instance dictionary; a slots-only model needs a descriptor designed for a reserved backing slot or another store.

### 6.3 Use the descriptor in a model

```python
class Order:
    quantity = Field(int, default=1, coerce=int, validator=lambda value: value > 0)
    unit_price = Field(float, coerce=float, validator=lambda value: value >= 0.0)

    def __init__(self, quantity: object = 1, unit_price: object = 0.0) -> None:
        self.quantity = quantity
        self.unit_price = unit_price

    @property
    def total(self) -> float:
        return self.quantity * self.unit_price


order = Order("3", "2.50")
print(order.quantity, type(order.quantity).__name__)
print(order.unit_price, type(order.unit_price).__name__)
print(order.total)
print(Order.quantity.name)
print(order.__dict__)
```

Expected output:

```text
3 int
2.5 float
7.5
quantity
{'_quantity': 3, '_unit_price': 2.5}
```

`Order.quantity` returns the descriptor itself because `__get__` handles `instance is None`. Instance access returns the validated per-instance value. The `total` property is a computed property: it recalculates on each access, unlike a cached descriptor.

### 6.4 Missing values, invalid values, and assignment behavior

```python
class RequiredRecord:
    amount = Field(int, validator=lambda value: value >= 0)


record = RequiredRecord()
try:
    print(record.amount)
except AttributeError as exc:
    print(type(exc).__name__, str(exc))

record.amount = 12
print(record.amount)

for bad_value in (-1, "not-an-int"):
    try:
        record.amount = bad_value
    except (TypeError, ValueError) as exc:
        print(type(exc).__name__, str(exc))
```

Expected output:

```text
AttributeError RequiredRecord.amount has not been set
12
ValueError 'amount' rejected value -1
TypeError 'amount' must be int; got str ('not-an-int')
```

A failed assignment does not overwrite the previously stored value, because validation occurs before `setattr` writes the backing attribute.

### 6.5 Coercion is a policy, not a universal default

Coercion can be convenient at ingestion boundaries, but it can also hide data-quality problems. For example, `int(3.8)` truncates to `3`, and `bool("false")` is `True`. Do not use permissive coercion blindly for financial or analytical data.

For a strict quantity field, omit `coerce=int`; then `"3"` raises `TypeError`. If you need string-to-integer parsing but must reject non-integral floats, write a dedicated converter that accepts only the intended source types and formats.

### 6.6 Descriptor assignment, initialization, and bypasses

`self.quantity = value` inside `__init__` invokes the descriptor's `__set__`, so validation applies during initialization too. Avoid writing directly to the backing attribute from normal application code (`self._quantity = value`), because that bypasses the descriptor. Private naming is a convention, not an access-control boundary.

Direct writes to `obj.__dict__` can also bypass the public assignment path. In this example, a direct `_quantity` write changes the value the descriptor subsequently reads; Python does not make backing attributes secure against deliberate bypasses.

## 7. Descriptor storage strategies

### 7.1 Private instance attributes

The most common design derives a private backing name from the public field name:

```python
class PrivateStorage:
    def __set_name__(self, owner: type, name: str) -> None:
        self.public_name = name
        self.storage_name = f"_{name}"

    def __get__(self, instance: object | None, owner: type | None = None) -> object:
        if instance is None:
            return self
        try:
            return getattr(instance, self.storage_name)
        except AttributeError:
            raise AttributeError(f"{self.public_name!r} has not been set") from None

    def __set__(self, instance: object, value: object) -> None:
        setattr(instance, self.storage_name, value)


class Example:
    value = PrivateStorage()


example = Example()
example.value = 42
print(example.value)
print(example.__dict__)
```

Expected output:

```text
42
{'_value': 42}
```

This pattern is straightforward and efficient, but it requires the instance to permit the backing attribute. Objects with `__slots__` and no `__dict__` need an explicit backing slot or a different strategy.

### 7.2 `WeakKeyDictionary`

An external mapping can keep values outside the instance:

```python
from weakref import WeakKeyDictionary


class WeakMapField:
    def __init__(self) -> None:
        self._values: WeakKeyDictionary[object, object] = WeakKeyDictionary()

    def __get__(self, instance: object | None, owner: type | None = None) -> object:
        if instance is None:
            return self
        try:
            return self._values[instance]
        except KeyError:
            raise AttributeError("field has not been set") from None

    def __set__(self, instance: object, value: object) -> None:
        self._values[instance] = value


class SlottedLike:
    __slots__ = ("__weakref__",)
    value = WeakMapField()


a = SlottedLike()
b = SlottedLike()
a.value = 1
b.value = 2
print(a.value, b.value)
```

Expected output:

```text
1 2
```

`WeakKeyDictionary` keys must be weak-referenceable and usable as dictionary keys (normally hashable, with equality/hash behavior that is stable while stored). A class with slots may need `__weakref__` in `__slots__` to support weak references. If objects define value-based equality and hashes, distinct but equal objects may interact unexpectedly as keys; consider identity-based storage or explicit slots when identity isolation is essential. Weak mappings also have synchronization and lifecycle considerations in concurrent applications.

## 8. Properties, descriptors, and `__getattr__`

These mechanisms solve related but different problems:

- Use `@property` for a focused computed attribute or a controlled attribute with a small amount of logic on one class.
- Use a custom descriptor when the same field behavior must be reused across many classes or names.
- Use `__getattr__` for fallback behavior when an attribute is otherwise missing, such as a proxy or a compatibility layer. Avoid using it as a substitute for clear, explicit fields when the API is known.
- Use a method when the operation is expensive, has side effects, needs explicit parameters, or would surprise a caller who expects attribute access to be cheap.

`__getattr__` is only consulted after ordinary attribute lookup fails with `AttributeError`. It does not override an existing data descriptor or instance value.

```python
class Settings:
    mode = "safe"

    def __getattr__(self, name: str) -> str:
        if name.startswith("legacy_"):
            return f"mapped:{name.removeprefix('legacy_')}"
        raise AttributeError(f"{type(self).__name__} has no attribute {name!r}")


settings = Settings()
print(settings.mode)
print(settings.legacy_timeout)
try:
    print(settings.unknown)
except AttributeError as exc:
    print(type(exc).__name__, str(exc))
```

Expected output:

```text
safe
mapped:timeout
AttributeError Settings has no attribute 'unknown'
```

Do not catch every `AttributeError` indiscriminately inside a descriptor or `__getattr__`: an `AttributeError` may indicate a genuine bug in a nested lookup, and overly broad fallback behavior can conceal it.

## 9. `__getattribute__` versus `__getattr__`

- `__getattribute__(self, name)` runs for essentially every normal instance attribute read. It can intercept successful as well as unsuccessful lookups.
- `__getattr__(self, name)` is a fallback invoked by the standard machinery when normal lookup raises `AttributeError`.

Overriding `__getattribute__` is powerful but easy to break. To perform normal lookup from an override, call `object.__getattribute__(self, name)`. Do **not** write `self.name` inside `__getattribute__` to fetch the same or another attribute without careful reasoning: that expression calls `__getattribute__` again and can recurse indefinitely.

### Incorrect versus correct

```python
class Recursive:
    def __getattribute__(self, name: str) -> object:
        return self.name  # INCORRECT: re-enters __getattribute__ forever.


class Logged:
    def __init__(self, value: int) -> None:
        self.value = value

    def __getattribute__(self, name: str) -> object:
        # This print avoids looking up self.value, which would recurse.
        print(f"reading {name}")
        return object.__getattribute__(self, name)


logged = Logged(7)
print(logged.value)
```

Expected output:

```text
reading value
7
```

The `Recursive` class is intentionally incorrect and should not be instantiated or executed. A correct override may log, authorize, or proxy access, but should delegate ordinary lookup to `object.__getattribute__`. Accessing helper state from inside the override may need `object.__getattribute__` too.

A custom `__getattribute__` can alter the normal lookup behavior described earlier. Keep overrides narrow, document the contract, and test missing attributes and descriptor interactions.

## 10. `object.__getattribute__`, class lookup, and metaclasses

### 10.1 Instance lookup versus class lookup

For an ordinary instance, `object.__getattribute__` implements the standard instance lookup algorithm. For a class object such as `Model.field`, lookup is performed by `type.__getattribute__` (because a class is itself an instance of its metaclass).

Class attribute access has its own descriptor behavior:

- A data descriptor defined on the metaclass can take precedence over attributes in the class's own namespace.
- Otherwise, attributes in the class's MRO are considered; descriptors found there are accessed with `instance=None` and the class as owner.
- Metaclass attributes can be found through the metaclass MRO as appropriate.

This distinction explains why a metaclass can control class-level attributes without changing ordinary instances of the class.

### 10.2 A metaclass can define class-level behavior

```python
class UppercaseName(type):
    @property
    def label(cls) -> str:
        return cls.__name__.upper()


class Job(metaclass=UppercaseName):
    pass


print(Job.label)
print(Job.__name__)
```

Expected output:

```text
JOB
Job
```

Here `label` is a property on the metaclass. Since `Job` is an instance of `UppercaseName`, `Job.label` invokes the metaclass property with `Job` as the instance argument. A normal property declared in `Job` is intended for `Job` instances and should not be confused with a metaclass property for `Job.label`.

Do not assume that `object.__getattribute__(Job, "label")` is interchangeable with `type.__getattribute__(Job, "label")`; use the appropriate machinery only when implementing advanced metaclass or proxy behavior. Most application code should use ordinary attribute access.

## 11. `inspect.getattr_static`: inspect without invoking descriptors

`getattr(obj, name)` and `hasattr(obj, name)` may trigger descriptors or custom attribute access. This can have side effects, perform I/O, raise errors, or compute a value. `inspect.getattr_static(obj, name)` attempts to retrieve the raw attribute without invoking the descriptor protocol or `__getattr__`.

```python
import inspect


class Lazy:
    @property
    def payload(self) -> str:
        print("property executed")
        return "loaded"


lazy = Lazy()
raw = inspect.getattr_static(lazy, "payload")
print(type(raw).__name__)
print(isinstance(raw, property))
```

Expected output:

```text
property
True
```

There is no `property executed` line: static inspection retrieves the raw property object. `getattr_static` is useful for debuggers, documentation tools, schema inspection, and safe introspection. Its result may be a descriptor rather than the runtime value. It also has limitations: dynamic attributes and custom lookup behavior may not be represented as normal runtime access would reveal them.

## 12. Descriptors and `__slots__`

A slot declared in a class is represented by a built-in **member descriptor** stored on the class. It controls access to a fixed storage location.

```python
class Point:
    __slots__ = ("x", "y")


point = Point()
point.x = 3
point.y = 4
print(point.x + point.y)
print(type(Point.x).__name__)
print(hasattr(point, "__dict__"))
```

Expected output:

```text
7
member_descriptor
False
```

Because there is no instance dictionary, arbitrary attributes such as `point.label = "origin"` raise `AttributeError`. A descriptor that writes to `instance.__dict__` cannot work with such an object unless the class also provides `__dict__` (for example, by including `"__dict__"` in `__slots__`). Alternatives include:

1. Reserve a backing slot for each descriptor field.
2. Use an external store such as `WeakKeyDictionary`, provided instances can be weakly referenced and used as keys.
3. Avoid `__slots__` when the flexibility of instance dictionaries is more valuable than the memory savings.

When a subclass introduces slots, account for inherited slots and any inherited instance dictionary. Avoid redeclaring a slot name already present in a base class; duplicate slot names have confusing and unsupported layout implications.

## 13. Cached descriptors and `functools.cached_property`

A cached property computes a value once on first access and stores it in the instance dictionary under the property name. Subsequent reads usually find the instance dictionary value before the non-data descriptor, so the descriptor is bypassed after the first successful computation.

```python
from functools import cached_property


class Report:
    def __init__(self, rows: list[int]) -> None:
        self.rows = rows
        self.computations = 0

    @cached_property
    def total(self) -> int:
        self.computations += 1
        print("computing total")
        return sum(self.rows)


report = Report([2, 3, 5])
print(report.total)
print(report.total)
print(report.computations)
report.rows.append(7)
del report.total
print(report.total)
```

Expected output:

```text
computing total
10
10
1
computing total
17
```

`cached_property` is a **non-data descriptor**: it defines `__get__` but does not define `__set__` or `__delete__` as descriptor protocol methods. This allows the cached instance attribute to shadow it. Deleting `report.total` removes the cached value so the next access recomputes it.

Important constraints:

- `cached_property` requires an instance with a mutable `__dict__`; it does not work with a pure-slotted instance that lacks one.
- It can interfere with key-sharing dictionaries and has higher per-instance memory implications than a slot-based field.
- It is appropriate when computation is expensive enough to justify caching and the underlying inputs are stable or explicit invalidation is implemented.
- It is not automatically invalidated when dependencies such as `rows` change. Delete the cached attribute or implement a deliberate invalidation policy.
- In Python 3.12, the undocumented per-property lock used by `cached_property` in earlier versions was removed. The getter may run more than once when concurrent threads access the same uncached property. If exactly-once computation is required, implement synchronization appropriate to the object and workload.

### A small custom cache descriptor

```python
class Cached:
    """Cache the getter result in the instance dictionary."""

    def __init__(self, getter: Callable[[object], T]) -> None:
        self.getter = getter
        self.name = getter.__name__

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, instance: object | None, owner: type | None = None) -> T | "Cached":
        if instance is None:
            return self
        namespace = vars(instance)  # requires an instance __dict__
        if self.name not in namespace:
            namespace[self.name] = self.getter(instance)
        return namespace[self.name]


class Metrics:
    def __init__(self) -> None:
        self.calls = 0

    @Cached
    def answer(self) -> int:
        self.calls += 1
        return 42


metrics = Metrics()
print(metrics.answer, metrics.answer, metrics.calls)
del metrics.answer
print(metrics.answer, metrics.calls)
```

Expected output:

```text
42 42 1
42 2
```

This descriptor is non-data because it has no `__set__` or `__delete__`. After the first access, `metrics.__dict__["answer"]` shadows the descriptor. `del metrics.answer` deletes that cached instance key because the descriptor has no deletion hook. This implementation is intentionally minimal: it does not preserve every function metadata attribute, support slots-only instances, coordinate concurrent computation, or define a richer invalidation API.

## 14. Generic descriptors and typing

A generic descriptor can express different types for class access and instance access. A common typing pattern overloads `__get__`:

```python
from __future__ import annotations

from typing import Generic, TypeVar, overload

T = TypeVar("T")


class Stored(Generic[T]):
    def __init__(self) -> None:
        self._name = "<unbound>"

    def __set_name__(self, owner: type, name: str) -> None:
        self._name = f"_{name}"

    @overload
    def __get__(self, instance: None, owner: type | None = None) -> "Stored[T]": ...

    @overload
    def __get__(self, instance: object, owner: type | None = None) -> T: ...

    def __get__(self, instance: object | None, owner: type | None = None) -> "Stored[T]" | T:
        if instance is None:
            return self
        return getattr(instance, self._name)

    def __set__(self, instance: object, value: T) -> None:
        setattr(instance, self._name, value)


class Batch:
    row_count = Stored[int]()


batch = Batch()
batch.row_count = 128
print(batch.row_count)
print(isinstance(Batch.row_count, Stored))
```

Expected output:

```text
128
True
```

The overloads tell a static type checker that `Batch.row_count` is a `Stored[int]` descriptor while `batch.row_count` is an `int`. Exact inference depends on the checker and its version; validate the typing behavior with the checker used by your project. Runtime Python does not enforce generic type arguments by itself. The `Stored` example intentionally does not perform runtime validation; combine typing with validation when runtime input may be untrusted.

Use `Self` when a method's return type should follow the dynamic class, but do not confuse that use with descriptor access typing. Descriptor types often need overloads because class access and instance access return different types.

## 15. Inheritance and overriding descriptors

Attribute lookup searches the MRO, so a descriptor defined on a base class governs subclasses unless a subclass shadows it with another class attribute. Descriptor objects are shared class attributes; state must still be stored per instance.

```python
from __future__ import annotations

class NonNegative:
    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name
        self.storage_name = f"_{name}"

    def __get__(self, instance: object | None, owner: type | None = None) -> int | "NonNegative":
        if instance is None:
            return self
        return getattr(instance, self.storage_name)

    def __set__(self, instance: object, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError(f"{self.name} must be an int")
        if value < 0:
            raise ValueError(f"{self.name} must be non-negative")
        setattr(instance, self.storage_name, value)


class BaseJob:
    retries = NonNegative()


class SpecialJob(BaseJob):
    pass


class StrictJob(BaseJob):
    retries = NonNegative()


a = SpecialJob()
a.retries = 2
b = SpecialJob()
b.retries = 4
print(a.retries, b.retries)
c = StrictJob()
c.retries = 1
print(c.retries)
```

Expected output:

```text
2 4
1
```

`SpecialJob` inherits the same `retries` descriptor from `BaseJob`; the descriptor's `__set_name__` is not called again for the subclass. `StrictJob` creates a new descriptor in its own namespace, so that descriptor is bound to `StrictJob` and `retries`.

If a descriptor needs to know the class currently being accessed, the `owner` argument to `__get__` can help. However, an inherited descriptor's stored `owner` from `__set_name__` refers to the class where that descriptor was originally declared, not necessarily the runtime subclass.

## 16. Deletion behavior and read-only descriptors

A descriptor can control deletion by implementing `__delete__`. If a descriptor implements neither `__set__` nor `__delete__`, it is non-data; but a descriptor that implements `__delete__` is a data descriptor.

```python
class ManagedValue:
    def __set_name__(self, owner: type, name: str) -> None:
        self.storage_name = f"_{name}"

    def __get__(self, instance: object | None, owner: type | None = None) -> object:
        if instance is None:
            return self
        return getattr(instance, self.storage_name)

    def __set__(self, instance: object, value: object) -> None:
        setattr(instance, self.storage_name, value)

    def __delete__(self, instance: object) -> None:
        delattr(instance, self.storage_name)


class Box:
    item = ManagedValue()


box = Box()
box.item = "payload"
print(box.item)
del box.item
try:
    print(box.item)
except AttributeError as exc:
    print(type(exc).__name__)
```

Expected output:

```text
payload
AttributeError
```

This example intentionally lets a missing backing value surface as `AttributeError`. A production descriptor may instead provide a more informative missing-value message.

## 17. Performance: measure before optimizing

Attribute access is common and Python implementations optimize it aggressively. CPython's specializing interpreter (introduced in Python 3.11 and present in Python 3.12+) can specialize common operations based on observed runtime types and code paths. This means performance is contextual: a descriptor access is not guaranteed to have a fixed overhead relative to a dictionary lookup across all versions and workloads.

Practical guidance:

- Prefer readable `@property` or descriptors when their semantics improve the API.
- A custom descriptor adds Python-level calls and policy logic; do not use one for every trivial field without a reuse or correctness benefit.
- `__slots__` can reduce memory for large numbers of objects, but it changes flexibility and storage assumptions.
- `cached_property` trades memory and invalidation complexity for avoiding repeated computation.
- Benchmark representative workloads with `timeit` or a profiler before optimizing. Keep interpreter version, data size, warm-up, and workload realistic.
- For the broader profiling workflow, follow the roadmap's Module 1.19 material; do not infer performance from a single microbenchmark alone.

## 18. Common mistakes checklist

Every common mistake listed in Lesson 06 is covered below.

1. **Storing instance state on the descriptor itself.** The descriptor is shared by instances. Store each value in the instance's private backing attribute or an appropriate external mapping.
2. **Forgetting the `instance is None` branch in `__get__`.** Class access such as `Order.quantity` calls `__get__(None, Order)` for applicable descriptors. Decide and document what it returns.
3. **Overriding `__getattribute__` carelessly.** It runs for every normal instance read. Delegate to `object.__getattribute__` to avoid recursion and preserve default semantics unless intentionally replacing them.

Other high-frequency errors:

- Treating every descriptor as a data descriptor; classification depends on whether its type defines `__set__` and/or `__delete__`.
- Assuming `__set_name__` reruns for inherited descriptors or late assignment.
- Storing into the public field name inside `__set__`, causing recursion (`setattr(instance, name, value)` invokes the descriptor again).
- Catching `AttributeError` too broadly and hiding a genuine bug.
- Assuming a descriptor that uses `instance.__dict__` works on pure-slotted instances.
- Assuming cached values automatically refresh when dependencies change.
- Using permissive coercion that silently changes input data.
- Assuming annotations alone enforce runtime types.
- Assuming class-level access and instance-level access return the same type.
- Assuming a descriptor's owner recorded in `__set_name__` is the runtime subclass.

## 19. Pytest tests

Save the following as `test_descriptors.py` and run `python -m pytest -q`. These tests exercise the `Field` implementation from Section 6; in a single-file lesson, copy that implementation above these tests or import it from the module where you saved it.

```python
import pytest


def test_class_access_returns_descriptor() -> None:
    assert isinstance(Order.quantity, Field)
    assert Order.quantity.name == "quantity"


def test_instance_access_and_coercion() -> None:
    order = Order("3", "2.50")
    assert order.quantity == 3
    assert isinstance(order.quantity, int)
    assert order.unit_price == 2.5
    assert order.total == 7.5


def test_invalid_value_does_not_replace_previous_value() -> None:
    order = Order(2, 1.0)
    with pytest.raises(ValueError, match="quantity"):
        order.quantity = 0
    assert order.quantity == 2


def test_wrong_type_without_coercion() -> None:
    class Strict:
        count = Field(int)

    item = Strict()
    with pytest.raises(TypeError, match="count"):
        item.count = "5"


def test_bool_is_not_accepted_as_integer_field() -> None:
    class Strict:
        count = Field(int, coerce=int)

    with pytest.raises(TypeError, match="not bool"):
        Strict().count = True


def test_missing_required_field() -> None:
    class Required:
        value = Field(int)

    with pytest.raises(AttributeError, match="has not been set"):
        _ = Required().value


def test_default_value() -> None:
    class WithDefault:
        retries = Field(int, default=3)

    assert WithDefault().retries == 3


def test_default_is_coerced_and_validated() -> None:
    class WithDefault:
        count = Field(int, default="3", coerce=int, validator=lambda value: value > 0)

    assert WithDefault().count == 3
    with pytest.raises(ValueError, match="rejected"):
        class InvalidDefault:
            count = Field(int, default=0, validator=lambda value: value > 0)


def test_default_factory_is_per_instance() -> None:
    class WithList:
        values = Field(list, default_factory=list)

    first = WithList()
    second = WithList()
    first.values.append("first")
    assert first.values == ["first"]
    assert second.values == []


def test_independent_state_across_instances() -> None:
    first = Order(1, 2.0)
    second = Order(5, 4.0)
    first.quantity = 8
    assert first.quantity == 8
    assert second.quantity == 5


def test_delete_removes_stored_value() -> None:
    class Required:
        value = Field(int)

    item = Required()
    item.value = 10
    del item.value
    with pytest.raises(AttributeError, match="has not been set"):
        _ = item.value


def test_inherited_descriptor_state_is_per_instance() -> None:
    class Parent:
        count = Field(int, default=0)

    class Child(Parent):
        pass

    first = Child()
    second = Child()
    first.count = 9
    assert first.count == 9
    assert second.count == 0


def test_cached_property_reuses_value_and_can_be_invalidated() -> None:
    from functools import cached_property

    class Example:
        def __init__(self) -> None:
            self.calls = 0

        @cached_property
        def value(self) -> int:
            self.calls += 1
            return self.calls

    example = Example()
    assert example.value == 1
    assert example.value == 1
    assert example.calls == 1
    del example.value
    assert example.value == 2


def test_data_descriptor_precedes_instance_dictionary() -> None:
    class Data:
        def __get__(self, instance: object | None, owner: type | None = None) -> str:
            if instance is None:
                return "descriptor"
            return "descriptor"

        def __set__(self, instance: object, value: object) -> None:
            vars(instance)["_value"] = value

    class Example:
        value = Data()

    example = Example()
    example.__dict__["value"] = "instance dictionary"
    assert example.value == "descriptor"


def test_non_data_descriptor_can_be_shadowed() -> None:
    class NonData:
        def __get__(self, instance: object | None, owner: type | None = None) -> str:
            return "descriptor"

    class Example:
        value = NonData()

    example = Example()
    assert example.value == "descriptor"
    example.value = "instance"
    assert example.value == "instance"


def test_getattribute_delegates_without_recursion() -> None:
    class Logged:
        def __init__(self) -> None:
            self.value = 7

        def __getattribute__(self, name: str) -> object:
            return object.__getattribute__(self, name)

    assert Logged().value == 7


def test_computed_property_is_not_cached() -> None:
    class Example:
        def __init__(self) -> None:
            self.calls = 0

        @property
        def value(self) -> int:
            self.calls += 1
            return self.calls

    example = Example()
    assert example.value == 1
    assert example.value == 2
```

Expected test result, when the code is saved with the `Field`, `Order`, and imports defined in the same module or imported into the test module:

```text
17 passed
```

The count above is the expected result for the included tests; run the command in your environment to confirm it there. These tests do not establish thread safety or performance characteristics.

## 20. Graduated exercises

### Exercise 1 — predict lookup

Given:

```python
class Label:
    def __get__(self, instance: object | None, owner: type | None = None) -> str:
        return "descriptor"


class Item:
    label = Label()


item = Item()
item.__dict__["label"] = "instance"
```

What does `item.label` return? Explain why. Then add a `__set__` method to `Label` and explain how the lookup result changes.

### Exercise 2 — add deletion to a field

Extend `Field` with a `reset(instance)` helper that removes the stored backing value. It should not write `None` unless `None` is an allowed field value. Decide whether `del obj.field` should raise when no stored value exists, and document the choice.

### Exercise 3 — strict conversion

Implement `parse_quantity(value: object) -> int` that accepts an `int` or a string containing only decimal digits, rejects `bool`, rejects floats (including `2.0`), and rejects negative strings. Use it as the `coerce` argument. Explain why `bool` needs explicit treatment even though it is a subclass of `int`.

### Exercise 4 — a slotted model

Create a class with `__slots__ = ("_code",)` and a descriptor for public field `code` that validates non-empty strings. Make the descriptor use `_code` as storage rather than relying on `__dict__`. Test valid assignment, invalid assignment, and independent instances.

### Exercise 5 — cached derived data

Create a `cached_property` called `normalized_rows` that returns a sorted tuple of rows. Demonstrate that repeated reads reuse the cached object, and invalidate it after modifying the source data. State when this design would be inappropriate.

## 21. Worked solutions

### Solution 1

`item.label` returns `"instance"` because `Label` defines only `__get__`, making it a non-data descriptor. The instance dictionary wins. Adding `__set__` makes it a data descriptor, so normal instance-dictionary entries with the same name no longer win.

### Solution 2

The implementation in Section 6 already has `__delete__`, which removes the backing attribute and raises `AttributeError` if no stored value exists. A separate helper could call `delattr(instance, self.storage_name)` and apply the same policy. Do not call `delattr(instance, self.name)` from inside the descriptor: that would invoke the descriptor's own `__delete__` again.

### Solution 3

```python
def parse_quantity(value: object) -> int:
    if isinstance(value, bool):
        raise TypeError("bool is not a valid quantity")
    if isinstance(value, int):
        if value < 0:
            raise ValueError("quantity must be non-negative")
        return value
    if isinstance(value, str) and value.isdecimal():
        return int(value)
    raise TypeError("quantity must be a non-negative int or decimal digit string")
```

This policy accepts Unicode decimal digit characters that Python's `str.isdecimal()` recognizes. If an external data format requires ASCII digits only, use an explicit ASCII check such as `value.isascii() and value.isdigit()`. `bool` is a subclass of `int`, so it must be rejected before the general integer branch if `True`/`False` are not valid quantities.

### Solution 4

```python
from __future__ import annotations

class NonEmptyString:
    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name
        self.storage_name = f"_{name}"

    def __get__(self, instance: object | None, owner: type | None = None) -> str | "NonEmptyString":
        if instance is None:
            return self
        return getattr(instance, self.storage_name)

    def __set__(self, instance: object, value: object) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{self.name} must be a non-empty string")
        setattr(instance, self.storage_name, value)


class SlottedRecord:
    __slots__ = ("_code",)
    code = NonEmptyString()

    def __init__(self, code: str) -> None:
        self.code = code


one = SlottedRecord("A-1")
two = SlottedRecord("B-2")
assert one.code == "A-1"
assert two.code == "B-2"
try:
    one.code = ""
except ValueError:
    pass
else:
    raise AssertionError("empty code should be rejected")
assert one.code == "A-1"
```

The descriptor stores each value in the explicitly declared `_code` slot. No instance dictionary is needed.

### Solution 5

```python
from functools import cached_property


class Dataset:
    def __init__(self, rows: list[int]) -> None:
        self.rows = rows

    @cached_property
    def normalized_rows(self) -> tuple[int, ...]:
        return tuple(sorted(self.rows))


data = Dataset([3, 1, 2])
first_result = data.normalized_rows
assert first_result == (1, 2, 3)
assert data.normalized_rows is first_result

data.rows.append(0)
del data.normalized_rows
assert data.normalized_rows == (0, 1, 2, 3)
```

This is inappropriate when the source changes frequently, cache invalidation is unreliable, computation is cheap, memory is constrained, or the object lacks a mutable `__dict__`.

## 22. Self-check questions and answers

### 1. Order the four steps of attribute lookup and justify why data descriptors win over the instance dictionary.

For ordinary instance lookup: (1) a data descriptor found on the type/MRO, (2) the instance dictionary, (3) a non-data descriptor or plain class attribute found on the type/MRO, and (4) `__getattr__` if normal lookup raises `AttributeError`. Data descriptors win because they are designed to control reads/writes/deletes and must not be silently bypassed by a same-named instance entry.

### 2. Why is `quantity = Positive()` shared state a bug if you store the value on `self.value` of the descriptor?

The class creates one descriptor object for the `quantity` class attribute, shared by every `Order` instance. Storing `self.value` mutates that shared object, so one order overwrites another order's value. Store data on each order instance (for example, `_quantity`) or in a carefully designed external per-instance mapping.

### 3. What does `Order.quantity` return and why?

In the `Positive` example from the roadmap, `Order.quantity` invokes `Positive.__get__(None, Order)`. The `obj is None` branch returns `self`, so the result is the descriptor object. This class-access behavior supports introspection and is a deliberate design choice.

## 23. Final roadmap coverage checklist

- [x] Descriptor definition and class-level placement.
- [x] `__get__`, `__set__`, `__delete__`, and `__set_name__`.
- [x] Data versus non-data descriptor classification and precedence.
- [x] Functions as descriptors and bound-method creation.
- [x] Attribute lookup sequence, MRO, instance dictionary, and `__getattr__` fallback.
- [x] Why data descriptors beat instance values and non-data descriptors can be shadowed.
- [x] Per-instance storage using private backing attributes and `WeakKeyDictionary`.
- [x] `classmethod` and `staticmethod` descriptor behavior.
- [x] `inspect.getattr_static`.
- [x] `__getattribute__` versus `__getattr__`, recursion hazards, and `object.__getattribute__`.
- [x] Class lookup through `type.__getattribute__` and metaclass effects.
- [x] Reusable validated field descriptor with typing, coercion, defaults, and errors.
- [x] `__slots__` and member descriptors.
- [x] Cached descriptor pattern, `cached_property` non-data behavior, and invalidation.
- [x] Generic descriptor typing and overloaded `__get__`.
- [x] Performance and specializing interpreter at a conceptual level.
- [x] All three roadmap-listed common mistakes.
- [x] All three roadmap self-check questions answered.
- [x] Complete examples, expected outputs, tests, graduated exercises, and worked solutions.
