# Metaclasses: Controlling Class Creation in Python

**Stage 1 — Programming & Computational Thinking · Module 1.12: Metaprogramming and Dynamic Python**  
**Target runtime:** Python 3.12+ (version notes are marked inline)

## Learning outcomes

By the end of this lesson, you should be able to:

- Explain why a class is an object and why `type` is the default metaclass.
- Trace the class-creation lifecycle, including `__prepare__`, metaclass `__new__` and `__init__`, `__set_name__`, `__init_subclass__`, and class decorators.
- Distinguish metaclass `__call__` (creating instances of a class) from instance `__new__` and `__init__`.
- Build a small metaclass that collects and validates declarative fields.
- Compare metaclasses with descriptors, `__set_name__`, `__init_subclass__`, and class decorators.
- Understand `ABCMeta`, enum metaclasses, metaclass conflicts, class-level lookup, `__instancecheck__`, and `__subclasscheck__`.
- Diagnose interactions with `__slots__`, `dataclass`, and `Generic`.
- Test metaprogramming code without leaking global state between tests.
- Decide when a metaclass is justified—and when a simpler design is better.

> **Design rule:** If a class decorator or `__init_subclass__` solves the requirement, prefer it. A metaclass is powerful precisely because it changes how classes are created; that power increases coupling, debugging cost, and surprise.

## 1. Prerequisites and the Python object model

You should already be comfortable with class definitions, inheritance and MRO, descriptors, decorators, `__init_subclass__`, `type(name, bases, namespace)`, type hints, and pytest. The earlier lessons in this module cover those prerequisites; this lesson connects them.

### 1.1 Everything is an object—including classes

```python
class Customer:
    pass

customer = Customer()
print(type(customer) is Customer)
print(type(Customer) is type)
print(type(type) is type)
```

Expected output:

```text
True
True
True
```

- `Customer` is a **class object**.
- `customer` is an instance of `Customer`.
- `type(customer)` reports the instance's class.
- `type(Customer)` reports the class of the class object: normally `type`.
- `type` is itself an instance of `type`, which makes the object model coherent rather than infinitely recursive.

The built-in `type` has two common roles:

```python
value = 42
print(type(value))

Generated = type("Generated", (), {"kind": "example"})
print(Generated().kind)
```

Expected output:

```text
<class 'int'>
example
```

The one-argument form inspects an object's type. The three-argument form creates a class from a name, base tuple, and namespace. A metaclass is the callable used to construct a class object; most ordinary classes use `type`.

### 1.2 The basic relationship

```text
instance  --type(instance)-->  class object
class     --type(class)----->  metaclass (usually `type`)
```

A class's metaclass is available as `type(MyClass)`. A metaclass usually subclasses `type`:

```python
class Meta(type):
    pass

class Model(metaclass=Meta):
    pass

print(type(Model) is Meta)
print(type(Model()) is Model)
```

Expected output:

```text
True
True
```

The metaclass is not the same thing as the class's base class. `Model` inherits instance behavior from its bases; its class object is constructed by `Meta`.

## 2. Basic metaclass mental model

### 2.1 What `class Foo(metaclass=Meta)` means

Conceptually, Python executes the class body to build a namespace and then asks the selected metaclass to create a class object. This is **not** a literal translation of every class statement into `type(name, bases, dict)`—custom metaclasses, `__prepare__`, class keywords, descriptors, and decorators add steps—but it is a useful first approximation.

```python
class Meta(type):
    def __new__(mcls, name, bases, namespace, **kwargs):
        print(f"creating {name}")
        return super().__new__(mcls, name, bases, namespace, **kwargs)

class Model(metaclass=Meta):
    pass

class User(Model):
    pass
```

Expected output:

```text
creating Model
creating User
```

The metaclass is inherited by subclasses unless Python selects a different compatible metaclass due to explicit bases or a `metaclass=` argument. `User` does not need to repeat `metaclass=Meta`.

### 2.2 The metaclass's important hooks

| Hook | Main role | Runs at |
|---|---|---|
| `Meta.__prepare__(name, bases, **kw)` | Provide the namespace used while executing the class body | Before body execution |
| `Meta.__new__(mcls, name, bases, namespace, **kw)` | Create the class object; can inspect or transform the namespace | During class creation |
| `Meta.__init__(cls, name, bases, namespace, **kw)` | Initialize/configure the already-created class object | After metaclass `__new__` returns it |
| `Meta.__call__(cls, *args, **kwargs)` | Control calls to a class, normally instance creation | When `cls(...)` is called |
| `Meta.__getattr__(cls, name)` | Provide fallback for missing attributes on the class object | Class attribute lookup fallback |

These hooks are not interchangeable. Class creation and instance creation are separate phases.

## 3. Class creation lifecycle

For a conventional class statement, a useful high-level sequence is:

1. Resolve base classes and determine a compatible metaclass.
2. Call the metaclass's `__prepare__` if it defines one; otherwise use a normal namespace mapping.
3. Execute the class body in that namespace.
4. Call the metaclass; its `__new__` begins class-object construction.
5. Inside the usual `type.__new__` path, descriptors in the namespace receive `__set_name__(owner, name)` calls, then the parent-class `__init_subclass__` hook runs.
6. After metaclass `__new__` returns the class object, metaclass `__init__` initializes/configures that object.
7. Apply class decorators, from the innermost decorator outward.

This is a conceptual sequence for normal class statements and standard `type`-based metaclasses. Custom metaclasses can alter details, and a decorator may replace the class object after creation. The order matters: for example, `__init_subclass__` normally runs **before** a `@dataclass` decorator processes the subclass.

### 3.1 Observe the lifecycle

```python
class TracingNamespace(dict):
    def __setitem__(self, key, value):
        # Compiler-generated dunder entries vary by Python version; show
        # only application declarations for stable teaching output.
        if not key.startswith("__"):
            print(f"body assigns {key}")
        super().__setitem__(key, value)

class TraceMeta(type):
    @classmethod
    def __prepare__(mcls, name, bases, **kwargs):
        print(f"prepare {name}")
        return TracingNamespace()

    def __new__(mcls, name, bases, namespace, **kwargs):
        print(f"new {name}")
        return super().__new__(mcls, name, bases, dict(namespace), **kwargs)

    def __init__(cls, name, bases, namespace, **kwargs):
        print(f"init {name}")
        super().__init__(name, bases, namespace, **kwargs)

class Base(metaclass=TraceMeta):
    marker = 1
```

Expected output:

```text
prepare Base
body assigns marker
new Base
init Base
```

The exact implementation details of the namespace entries can vary with the class body, but the standard Python class-creation protocol supports this overall hook order. The custom mapping records assignments as the class body executes.

## 4. `__new__`, `__init__`, and `__prepare__`

### 4.1 Metaclass `__new__`: create or transform the class

`Meta.__new__` receives `mcls` (the metaclass), the prospective class name, its bases, and the namespace produced by the body. It can reject a class definition with `TypeError`, add attributes, or pass a transformed namespace to `super().__new__`.

```python
class UppercaseNames(type):
    def __new__(mcls, name, bases, namespace, **kwargs):
        if not name.isidentifier():
            raise TypeError(f"invalid class name: {name!r}")
        return super().__new__(mcls, name, bases, namespace, **kwargs)

class Event(metaclass=UppercaseNames):
    pass

print(Event.__name__)
```

Expected output:

```text
Event
```

The check is illustrative, not a complete replacement for Python's parser: ordinary `class` syntax already enforces identifier syntax. Metaclass validation is more useful for constraints on class-body declarations, such as required fields or duplicate keys.

### 4.2 Metaclass `__init__`: configure the created class

The metaclass's `__init__` receives the class object returned by `__new__` as `cls`. It can attach metadata or validate the finished class. `__new__` is often the right place to alter the namespace before class construction; `__init__` is useful for post-creation setup.

```python
class Labelled(type):
    def __init__(cls, name, bases, namespace, **kwargs):
        super().__init__(name, bases, namespace, **kwargs)
        cls.label = name.lower()

class Customer(metaclass=Labelled):
    pass

print(Customer.label)
```

Expected output:

```text
customer
```

Always consider cooperative inheritance: if a metaclass method overrides a method expected to participate in a multiple-inheritance chain, call `super()` with the appropriate arguments unless the implementation deliberately terminates the chain.

### 4.3 `__prepare__`: control the class-body namespace

`__prepare__` is a class method on the metaclass. It returns the mapping in which the class body executes. Modern dictionaries preserve insertion order, so custom namespaces are not needed merely to retain order. They are useful when the namespace needs to **observe** or **reject** assignments while the body is running.

```python
class NoDuplicateNames(dict):
    def __setitem__(self, key, value):
        if key in self:
            raise TypeError(f"duplicate class-body name: {key}")
        super().__setitem__(key, value)

class StrictMeta(type):
    @classmethod
    def __prepare__(mcls, name, bases, **kwargs):
        return NoDuplicateNames()

class Example(metaclass=StrictMeta):
    first = 1
    second = 2

print([name for name in Example.__dict__ if name in {"first", "second"}])
```

Expected output:

```text
['first', 'second']
```

The sample shows the namespace concept; a duplicate assignment such as two `first = ...` statements raises `TypeError` while the body executes. A custom mapping must still support the operations that class bodies and compiler-generated assignments require. Use `__prepare__` only when you truly need to observe the class body as it executes.

### 4.4 Keep instance `__new__` and `__init__` separate

There are two levels of methods with these names:

- `Meta.__new__` / `Meta.__init__` construct and initialize **class objects**.
- `Foo.__new__` / `Foo.__init__` construct and initialize **instances of `Foo`**.

For ordinary classes, `type.__call__` coordinates instance creation by calling the class's `__new__`, then—if the returned object is an instance of the class—calling its `__init__`. Do not confuse that with the metaclass's `__new__`, which runs when the class statement creates `Foo`.

## 5. Controlling instantiation with metaclass `__call__`

When code evaluates `Widget(...)`, it calls the class object. The class object's type (its metaclass) controls this call through `Meta.__call__`. The default `type.__call__` coordinates the instance-level `__new__` and `__init__` protocol.

```python
class CallTrace(type):
    def __call__(cls, *args, **kwargs):
        print(f"calling {cls.__name__}")
        return super().__call__(*args, **kwargs)

class Job(metaclass=CallTrace):
    def __init__(self, job_id: int):
        self.job_id = job_id

job = Job(7)
print(job.job_id)
```

Expected output:

```text
calling Job
7
```

`super().__call__` is essential here because it preserves normal construction, including custom instance `__new__` and `__init__` methods. Omitting it means you must deliberately implement the construction protocol yourself, which is rarely desirable.

### 5.1 Singleton metaclass: a teaching exercise, not a default design

```python
class Singleton(type):
    _instances: dict[type, object] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in Singleton._instances:
            Singleton._instances[cls] = super().__call__(*args, **kwargs)
        return Singleton._instances[cls]

class Settings(metaclass=Singleton):
    def __init__(self, mode: str = "prod"):
        self.mode = mode

first = Settings("prod")
second = Settings("test")
print(first is second)
print(second.mode)
```

Expected output:

```text
True
prod
```

The second call does not run `__init__` again because it is intercepted by the metaclass cache. This example is intentionally minimal and has limitations:

- The first constructor arguments win; later arguments are ignored, which can surprise callers.
- The dictionary strongly retains classes and instances for the life of the process.
- It is not thread-safe: concurrent first calls may race without synchronization.
- Global state complicates tests, parallel test execution, reloads, and multiple application configurations.
- Subclasses generally receive their own cache entry because the class object is the key, but shared mutable state in the metaclass still needs careful ownership.

Prefer, in order, an ordinary module-level instance for process-wide settings, a cached factory when arguments define the identity, or dependency injection when consumers should receive an explicit dependency. A metaclass singleton is rarely the simplest production choice.

## 6. Field collection and class-definition validation

Declarative APIs often let users write fields in a class body and then collect them into schema metadata. An ORM-like field collector is a realistic metaclass use case because it needs to inspect and transform the class namespace at class-creation time.

### 6.1 A descriptor for a declared field

```python
class Field:
    def __init__(self, *, required: bool = True):
        self.required = required
        self.name: str | None = None

    def __set_name__(self, owner, name):
        self.name = name
        self.storage_name = f"_{name}"

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        try:
            return getattr(instance, self.storage_name)
        except AttributeError:
            return None

    def __set__(self, instance, value):
        if value is None and self.required:
            raise ValueError(f"{self.name} is required")
        setattr(instance, self.storage_name, value)
```

`__set_name__` is called by `type.__new__` for descriptors present in the namespace. It records the name and owner context without requiring a metaclass. If the same descriptor object is reused under multiple names or classes, it must be designed to track that safely; a single mutable `name` attribute cannot represent multiple owners simultaneously.

### 6.2 A small schema metaclass

```python
class SchemaMeta(type):
    def __new__(mcls, name, bases, namespace, **kwargs):
        inherited: dict[str, Field] = {}
        for base in bases:
            inherited.update(getattr(base, "_fields", {}))

        declared = {
            key: value
            for key, value in namespace.items()
            if isinstance(value, Field)
        }
        fields = {**inherited, **declared}

        # Validate field names before creating the class.
        invalid = [field_name for field_name in fields if field_name.startswith("_")]
        if invalid:
            raise TypeError(f"field names must be public: {invalid}")

        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        cls._fields = fields
        return cls

class Record(metaclass=SchemaMeta):
    pass

class UserRecord(Record):
    user_id = Field()
    email = Field()

print(tuple(UserRecord._fields))
```

Expected output:

```text
('user_id', 'email')
```

Stage by stage:

1. The class body binds `user_id` and `email` to `Field` descriptor objects.
2. `SchemaMeta.__new__` receives the namespace mapping.
3. It copies field metadata inherited from bases, then overlays fields declared by the new class. The ordinary dictionary insertion order makes the declared order deterministic.
4. It validates the combined field names and rejects invalid definitions before the class is returned.
5. `super().__new__` creates the class. During this operation, `Field.__set_name__` is called for each field descriptor in the class namespace.
6. The metaclass attaches `_fields` to the finished class.

This is a teaching-sized schema. Production systems must define whether overriding a field with a non-field removes an inherited field, whether multiple inheritance can define the same field, how field types and defaults work, and how class-level metadata is exposed to static type checkers. In this example, inherited fields remain in `_fields` even if a subclass shadows the descriptor with a non-`Field` attribute; that policy should be changed explicitly if unwanted.

### 6.3 Validate instance data separately from class definitions

```python
class Record(metaclass=SchemaMeta):
    def __init__(self, **values):
        unknown = set(values) - self._fields.keys()
        if unknown:
            raise TypeError(f"unknown fields: {sorted(unknown)}")
        missing = [
            name for name, field in self._fields.items()
            if field.required and name not in values
        ]
        if missing:
            raise TypeError(f"missing fields: {missing}")
        for name, value in values.items():
            setattr(self, name, value)

class User(Record):
    user_id = Field()
    email = Field()
    nickname = Field(required=False)

user = User(user_id=7, email="a@example.com")
print(user.user_id, user.email, user.nickname)
```

Expected output:

```text
7 a@example.com None
```

The metaclass validates the **class definition** and collects schema metadata. The `Record.__init__` validates **instance input**. Descriptor assignment then enforces each field's required-value rule. These are distinct responsibilities and should remain explicit.

### 6.4 Testing the field collector

Save this as `test_metaclasses.py` next to the example module (or adapt imports to your package). The following tests are complete when the schema code above is saved in a module named `schema_example.py`.

```python
import pytest
from schema_example import Field, Record, SchemaMeta


def test_collects_declared_and_inherited_fields():
    class Parent(Record):
        code = Field()

    class Child(Parent):
        label = Field()

    assert tuple(Child._fields) == ("code", "label")


def test_rejects_invalid_field_name():
    with pytest.raises(TypeError, match="field names must be public"):
        class Invalid(Record):
            _secret = Field()


def test_rejects_missing_required_field():
    class User(Record):
        email = Field()

    with pytest.raises(TypeError, match="missing fields"):
        User()


def test_rejects_unknown_field():
    class User(Record):
        email = Field()

    with pytest.raises(TypeError, match="unknown fields"):
        User(email="x@example.com", admin=True)


def test_descriptor_validation_and_instantiation():
    class User(Record):
        email = Field()

    user = User(email="x@example.com")
    assert user.email == "x@example.com"
    with pytest.raises(ValueError, match="email is required"):
        user.email = None
```

Run with `python -m pytest -q`. Tests that define classes inside test functions keep their class objects local, but any explicit global registry should still be reset or snapshotted in a fixture.

## 7. Inheritance and metaclass conflicts

### 7.1 Metaclass inheritance

A subclass normally inherits its base's metaclass. If multiple bases have different metaclasses, Python must find a metaclass that is a (non-strict) subclass of every candidate metaclass. If no such compatible metaclass exists, class creation fails with `TypeError`.

### 7.2 A realistic conflict

```python
class AuditMeta(type):
    pass

class ValidationMeta(type):
    pass

class Audited(metaclass=AuditMeta):
    pass

class Validated(metaclass=ValidationMeta):
    pass

# This definition raises TypeError because the metaclasses are unrelated.
try:
    class BrokenCombined(Audited, Validated):
        pass
except TypeError as exc:
    print(type(exc).__name__)
```

`AuditMeta` and `ValidationMeta` are unrelated subclasses of `type`. Python cannot select one that is a subclass of both, so combining the bases fails. This is a genuine design issue encountered when a framework base and an abstract base class each impose a metaclass.

Expected output for the runnable negative example:

```text
TypeError
```

A corresponding pytest assertion should define `BrokenCombined` inside `pytest.raises(TypeError)` so the conflict is verified rather than merely described.

### 7.3 Resolve the conflict with a compatible derived metaclass

```python
class CombinedMeta(AuditMeta, ValidationMeta):
    pass

class Combined(Audited, Validated, metaclass=CombinedMeta):
    pass

print(type(Combined).__name__)
print([base.__name__ for base in Combined.__mro__[:3]])
```

Expected output:

```text
CombinedMeta
['Combined', 'Audited', 'Validated']
```

The new metaclass is a subclass of both candidate metaclasses, so it satisfies the compatibility requirement. The order `AuditMeta, ValidationMeta` also determines the metaclass MRO. If both metaclasses override the same hook, implementations must be cooperative and call `super()`; otherwise one behavior may be skipped. A derived metaclass cannot magically reconcile incompatible semantics—test the combined behavior, not just whether class creation succeeds.

### 7.4 Cooperative `super()` in metaclasses

Treat metaclass hooks like cooperative methods in ordinary multiple inheritance. Consume only the keyword arguments your hook owns, and forward the rest:

```python
class TaggedMeta(type):
    def __new__(mcls, name, bases, namespace, *, tag=None, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        cls.tag = tag
        return cls

class VersionedMeta(type):
    def __new__(mcls, name, bases, namespace, *, version=1, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        cls.version = version
        return cls

class TaggedVersionedMeta(TaggedMeta, VersionedMeta):
    pass

class Event(metaclass=TaggedVersionedMeta, tag="billing", version=2):
    pass

print(Event.tag, Event.version)
```

Expected output:

```text
billing 2
```

Each implementation consumes its own keyword and passes remaining keywords through `super()`. If a hook fails to forward `**kwargs`, a later hook may never see its option. If it forwards an unrecognized keyword to `type` after no hook consumes it, the class statement should fail rather than silently ignore a typo.

## 8. Standard-library case studies

### 8.1 `ABCMeta` and abstract base classes

`abc.ABCMeta` is the metaclass behind `abc.ABC`. It tracks abstract methods and prevents instantiation while required abstract methods remain unimplemented.

```python
from abc import ABC, abstractmethod

class Reader(ABC):
    @abstractmethod
    def read(self) -> str:
        raise NotImplementedError

class TextReader(Reader):
    def read(self) -> str:
        return "data"

print(type(Reader).__name__)
print(TextReader().read())
try:
    Reader()
except TypeError as exc:
    print("abstract")
```

Expected output:

```text
ABCMeta
data
abstract
```

Use `ABC` rather than implementing your own abstract-method metaclass. `ABCMeta` also supports virtual subclass registration and the `__instancecheck__` / `__subclasscheck__` machinery. Abstract base classes express a runtime contract; `typing.Protocol` often expresses a structural typing contract without requiring inheritance.

### 8.2 Enum metaclass

In Python 3.11+, the public metaclass is `enum.EnumType` (the historical name `EnumMeta` remains an alias). Enum's metaclass processes members in the class body and prevents ordinary enum members from being reassigned.

```python
from enum import Enum, EnumType

class Status(Enum):
    NEW = "new"
    DONE = "done"

print(isinstance(type(Status), type))
print(isinstance(type(Status), EnumType))
print(Status.NEW.value)
```

Expected output:

```text
True
True
new
```

Prefer `Enum` and its supported API rather than copying its metaclass behavior. Enum creation has nuanced rules for aliases, member names, mixins, and value lookup; the standard library already handles these cases.

### 8.3 Class-level attribute lookup and `type.__getattribute__`

Class attribute lookup and instance attribute lookup are related but distinct. For `SomeClass.attr`, Python's class-object lookup is implemented by the metaclass's `__getattribute__` (normally `type.__getattribute__`). It searches metaclass data descriptors and attributes as well as the class's own MRO according to the type lookup rules. A method defined on a metaclass is therefore available on the class object, not automatically on its instances.

```python
class Meta(type):
    def describe(cls):
        return f"class:{cls.__name__}"

class Thing(metaclass=Meta):
    pass

thing = Thing()
print(Thing.describe())
print(hasattr(thing, "describe"))
print(type(Thing).__name__)
```

Expected output:

```text
class:Thing
False
Meta
```

`type.__getattribute__` is the standard class-object lookup implementation. Overriding it is advanced and can make ordinary class attributes, descriptors, and introspection behave unexpectedly. If only a missing class attribute needs fallback behavior, a metaclass `__getattr__` is usually less invasive.

### 8.4 `__instancecheck__` and `__subclasscheck__`

These hooks customize `isinstance(value, SomeClass)` and `issubclass(OtherClass, SomeClass)`. They are defined on the metaclass. Use them sparingly because they can make the meaning of these familiar checks less obvious.

```python
class HasCloseMeta(type):
    def __instancecheck__(cls, instance):
        return callable(getattr(type(instance), "close", None))

class Closable(metaclass=HasCloseMeta):
    pass

class Stream:
    def close(self):
        pass

print(isinstance(Stream(), Closable))

class HasCloseSubclassMeta(type):
    def __subclasscheck__(cls, subclass):
        return callable(getattr(subclass, "close", None))

class CloseCapable(metaclass=HasCloseSubclassMeta):
    pass

print(issubclass(Stream, CloseCapable))
```

Expected output:

```text
True
True
```

These examples are intentionally permissive and should not be treated as robust protocol implementations. `abc.ABCMeta` already implements useful subclass hooks and caching. For static typing, a `Protocol` with `@runtime_checkable` may be more appropriate, though runtime-checkable protocols check attribute presence rather than fully validating method signatures.

## 9. Interactions with `__slots__`, `dataclass`, and `Generic`

### 9.1 `__slots__`

A metaclass does not make `__slots__` irrelevant. `__slots__` is processed during class construction and affects instance layout, descriptors, and whether instances have a `__dict__`. If a metaclass rewrites `__slots__`, it must do so before `type.__new__` constructs the class. Adding a `__slots__` attribute after class creation does not retroactively change the layout.

```python
class SlotMeta(type):
    def __new__(mcls, name, bases, namespace, **kwargs):
        namespace.setdefault("__slots__", ())
        return super().__new__(mcls, name, bases, namespace, **kwargs)

class Compact(metaclass=SlotMeta):
    value = 1

item = Compact()
print(hasattr(item, "__dict__"))
```

Expected output:

```text
False
```

Do not inject empty slots blindly into a hierarchy whose design expects instance attributes. Base classes, multiple inheritance, and layout compatibility can constrain slot combinations.

### 9.2 `dataclass`

`@dataclass` is a class decorator, not generally a metaclass. It receives an already-created class and adds generated methods. This timing explains why a base class's `__init_subclass__` cannot assume that the subclass has already been processed by `@dataclass`.

```python
from dataclasses import dataclass, fields

@dataclass
class Point:
    x: int
    y: int

print([field.name for field in fields(Point)])
print(Point(2, 3))
```

Expected output:

```text
['x', 'y']
Point(x=2, y=3)
```

`@dataclass(slots=True)` may return a replacement class rather than simply mutating the original class. That can affect identity-sensitive registries and zero-argument `super()` in some situations because the method's `__class__` closure refers to the original class. Test decorator stacking, subclass hooks, and pickling when relying on class identity.

### 9.3 `typing.Generic`

Modern generic classes generally do not require application authors to write a metaclass. `typing.Generic` uses the type system's supported machinery; Python 3.7 changed generic infrastructure so that the old `GenericMeta` approach was no longer needed. Python 3.12's PEP 695 adds new syntax for type parameters, such as `class Box[T]: ...`.

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Box(Generic[T]):
    def __init__(self, value: T):
        self.value = value

print(Box[int](3).value)
```

Expected output:

```text
3
```

Do not infer a class's generic behavior from old Python 3.6-era examples that rely on `GenericMeta`. If combining a custom metaclass with framework bases, inspect `type(Base)` and test compatibility on the target Python version.

## 10. The alternatives ladder: one registry, four approaches

Suppose every handler should be discoverable by a stable name. This can be implemented in several ways. The best choice depends on whether registration should be opt-in, inherited, descriptor-driven, or inseparable from class creation.

### 10.1 Class decorator: explicit and opt-in

```python
DECORATOR_REGISTRY: dict[str, type] = {}

def register(name: str):
    def decorate(cls):
        if name in DECORATOR_REGISTRY:
            raise ValueError(f"duplicate handler: {name}")
        DECORATOR_REGISTRY[name] = cls
        return cls
    return decorate

@register("csv")
class CsvHandler:
    pass

print(DECORATOR_REGISTRY["csv"].__name__)
```

Expected output: `CsvHandler`.

Choose this when a class explicitly opts in. Registration runs after the class object has been created and before the decorated name is bound in the surrounding module.

### 10.2 `__init_subclass__`: register every subclass

```python
class HandlerBase:
    registry: dict[str, type["HandlerBase"]] = {}

    def __init_subclass__(cls, *, name: str | None = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if name is None:
            return
        if name in HandlerBase.registry:
            raise ValueError(f"duplicate handler: {name}")
        HandlerBase.registry[name] = cls

class JsonHandler(HandlerBase, name="json"):
    pass

print(HandlerBase.registry["json"].__name__)
```

Expected output: `JsonHandler`.

Choose this when all subclasses should participate and the parent can own the rule. Remember that class creation happens at import time and that a module must be imported for its class statement to run.

### 10.3 Descriptor + `__set_name__`: field registration

```python
class RegisteredField:
    def __set_name__(self, owner, name):
        fields = dict(owner.__dict__.get("fields", {}))
        fields[name] = self
        owner.fields = fields

class Table:
    fields: dict[str, RegisteredField] = {}
    key = RegisteredField()
    value = RegisteredField()

print(tuple(Table.fields))
```

Expected output: `('key', 'value')`.

Choose this when the registration unit is an attribute declared in a class body. This simple example copies the owner's directly declared `fields` mapping; in a production hierarchy, define explicitly how inherited fields are merged. A descriptor can validate values and manage storage too.

### 10.4 Metaclass: collect and enforce at class creation

```python
class RegistryMeta(type):
    registry: dict[str, type] = {}

    def __new__(mcls, name, bases, namespace, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        key = namespace.get("plugin_name")
        if key is not None:
            if key in mcls.registry:
                raise TypeError(f"duplicate plugin: {key}")
            mcls.registry[key] = cls
        return cls

class Plugin(metaclass=RegistryMeta):
    plugin_name = None

class ParquetPlugin(Plugin):
    plugin_name = "parquet"

print(RegistryMeta.registry["parquet"].__name__)
```

Expected output: `ParquetPlugin`.

Choose this only when class creation itself must be intercepted—for example, a framework must transform the class namespace, coordinate declarations across the whole class body, or reject invalid class definitions before the class is exposed. Notice the registry is updated after `super().__new__` here; a more robust implementation should validate duplicate keys before class construction or make registration transactional so a failed definition does not leave partial state. Also decide whether inherited `plugin_name` values should trigger registration: this example reads only the new class's namespace, so it registers only explicitly declared keys.

### 10.5 Comparison

| Mechanism | Best fit | Main trade-off |
|---|---|---|
| Class decorator | Explicit opt-in after class creation | Can be forgotten; order relative to other decorators matters |
| `__init_subclass__` | A base class enforces rules for subclasses | Less control over the namespace during body execution |
| Descriptor + `__set_name__` | Attribute-level metadata or validation | Registration logic is distributed across descriptors |
| Metaclass | Transform/validate the class namespace as a whole | More complex MRO, conflicts, debugging, and typing support |

The module's complexity ladder remains: plain code → decorators → class decorators → `__init_subclass__` → descriptors → metaclasses → AST/`exec`. Use the lowest rung that satisfies the requirement.

## 11. Debugging and introspection

Metaclass bugs are class-construction bugs. Inspect the class object and its metaclass before stepping through every hook.

```python
import inspect

class Meta(type):
    pass

class Base(metaclass=Meta):
    pass

class Child(Base):
    pass

print(type(Child).__name__)
print([base.__name__ for base in Child.__mro__])
print(inspect.isclass(Child))
print(inspect.isclass(type(Child)))
print(Child.__bases__[0].__name__)
```

Expected output:

```text
Meta
['Child', 'Base', 'object']
True
True
Base
```

Useful tools:

- `type(cls)` identifies the metaclass actually used.
- `cls.__mro__` shows the class's method resolution order; `type(cls).__mro__` shows the metaclass MRO.
- `cls.__dict__` shows attributes declared directly on the class (as a read-only mapping proxy); `vars(cls)` is a convenient view of that namespace.
- `inspect.getmembers` performs attribute access and can invoke descriptors; use `inspect.getattr_static` when you need to inspect an attribute without invoking normal descriptor logic.
- `inspect.signature`, `inspect.getsource`, and a debugger help trace framework behavior, but source may be unavailable for built-ins or dynamically created classes.

Avoid depending on private implementation details of a particular interpreter. The examples in this lesson use public Python object-model protocols.

## 12. Performance, imports, and test isolation

### 12.1 Import-time cost

A class statement executes during module import. A metaclass that scans annotations, merges large schemas, resolves forward references, imports plugins, or performs I/O can increase startup latency and make imports fail for reasons unrelated to using the class. Keep class creation deterministic, bounded, and free of network or filesystem side effects where possible.

### 12.2 Runtime performance

Most metaclass work happens once per class, so it may not affect every instance operation directly. However, custom `__call__`, custom attribute lookup, descriptors, and per-instance validation can affect hot paths. Measure the real workload with `timeit` or a profiler rather than assuming a metaclass is fast or slow by definition. Avoid adding custom `__getattribute__` behavior unless needed.

### 12.3 Registry and singleton test isolation

Global registries are mutable process-wide state. Tests that define classes can silently add entries and make later tests order-dependent. Prefer an injectable registry object or provide a fixture that snapshots and restores the registry:

```python
import pytest

@pytest.fixture
def isolated_registry():
    original = dict(RegistryMeta.registry)
    try:
        yield RegistryMeta.registry
    finally:
        RegistryMeta.registry.clear()
        RegistryMeta.registry.update(original)
```

Use the fixture in tests that mutate `RegistryMeta.registry`. For singleton tests, provide a test-only reset method or isolate the cache in a factory whose lifetime the test controls. Do not rely on test ordering or reload modules to clean state. In concurrent applications, also consider locks and whether process-wide singleton semantics are actually required.

## 13. Version and compatibility notes

- **Python 3.12+ target:** all core metaclass examples in this lesson use supported language features available in Python 3.12.
- **Python 3.6+:** dictionaries preserve insertion order as a language guarantee from Python 3.7 onward; custom `__prepare__` mappings are no longer needed just to preserve order.
- **Python 3.7:** `typing.Generic` no longer required the old `GenericMeta` architecture; do not copy obsolete examples uncritically.
- **Python 3.11+:** `enum.EnumType` is the public name for the enum metaclass; `EnumMeta` remains a historical alias.
- **Python 3.12:** PEP 695 adds type-parameter syntax such as `class Box[T]: ...`; this does not imply you need a custom metaclass for generic classes.
- **Python 3.13/3.14:** annotation introspection and evaluation APIs are evolving. If a metaclass or framework resolves annotations, use the APIs and compatibility guidance for the exact target version rather than assuming `__annotations__` always contains eagerly evaluated objects. This topic is covered in the module's introspection lesson.

## 14. Practical project: declarative event schema

Build a small declarative API that validates field names, collects inherited fields, instantiates records, and exposes stable schema metadata. Save as `event_schema.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FieldSpec:
    value_type: type
    required: bool = True


class SchemaMeta(type):
    def __new__(mcls, name, bases, namespace, **kwargs):
        fields: dict[str, FieldSpec] = {}
        for base in bases:
            fields.update(getattr(base, "__schema_fields__", {}))

        declared = {
            key: value
            for key, value in namespace.items()
            if isinstance(value, FieldSpec)
        }
        fields.update(declared)

        for field_name in fields:
            if not field_name.isidentifier() or field_name.startswith("_"):
                raise TypeError(f"invalid schema field: {field_name!r}")

        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        cls.__schema_fields__ = fields
        return cls


class Event(metaclass=SchemaMeta):
    event_id = FieldSpec(str)

    def __init__(self, **values: Any) -> None:
        fields = type(self).__schema_fields__
        unknown = set(values) - fields.keys()
        if unknown:
            raise TypeError(f"unknown fields: {sorted(unknown)}")

        missing = [
            key for key, spec in fields.items()
            if spec.required and key not in values
        ]
        if missing:
            raise TypeError(f"missing fields: {missing}")

        for key, value in values.items():
            spec = fields[key]
            if value is None and not spec.required:
                setattr(self, key, value)
            elif spec.value_type is int and isinstance(value, bool):
                # bool is a subclass of int, but is not a valid numeric amount.
                raise TypeError(
                    f"{key} must be int, got {type(value).__name__}"
                )
            elif not isinstance(value, spec.value_type):
                raise TypeError(
                    f"{key} must be {spec.value_type.__name__}, "
                    f"got {type(value).__name__}"
                )
            else:
                setattr(self, key, value)

        # Materialize absent optional fields as None so class-level FieldSpec
        # declarations do not leak through instance attribute lookup.
        for key, spec in fields.items():
            if not spec.required and key not in values:
                setattr(self, key, None)

    def to_dict(self) -> dict[str, Any]:
        return {
            name: getattr(self, name, None)
            for name in type(self).__schema_fields__
        }


class InvoiceCreated(Event):
    invoice_id = FieldSpec(str)
    amount_cents = FieldSpec(int)
    source = FieldSpec(str, required=False)


if __name__ == "__main__":
    event = InvoiceCreated(
        event_id="evt-1",
        invoice_id="inv-7",
        amount_cents=1250,
        source="batch",
    )
    print(tuple(InvoiceCreated.__schema_fields__))
    print(event.to_dict())
```

Run `python event_schema.py`.

Expected output:

```text
('event_id', 'invoice_id', 'amount_cents', 'source')
{'event_id': 'evt-1', 'invoice_id': 'inv-7', 'amount_cents': 1250, 'source': 'batch'}
```

### 14.1 Project tests

Save as `test_event_schema.py` beside `event_schema.py`:

```python
import pytest
from event_schema import Event, FieldSpec, InvoiceCreated


def test_inherited_schema_and_serialization():
    event = InvoiceCreated(
        event_id="evt-1", invoice_id="inv-7", amount_cents=1250
    )
    assert tuple(InvoiceCreated.__schema_fields__) == (
        "event_id", "invoice_id", "amount_cents", "source"
    )
    assert event.to_dict() == {
        "event_id": "evt-1",
        "invoice_id": "inv-7",
        "amount_cents": 1250,
        "source": None,
    }


def test_missing_required_field_fails():
    with pytest.raises(TypeError, match="missing fields"):
        InvoiceCreated(event_id="evt-1", invoice_id="inv-7")


def test_unknown_field_fails():
    with pytest.raises(TypeError, match="unknown fields"):
        InvoiceCreated(
            event_id="evt-1", invoice_id="inv-7", amount_cents=5, debug=True
        )


def test_wrong_type_fails():
    with pytest.raises(TypeError, match="amount_cents must be int"):
        InvoiceCreated(
            event_id="evt-1", invoice_id="inv-7", amount_cents="1250"
        )


def test_invalid_declared_name_fails():
    with pytest.raises(TypeError, match="invalid schema field"):
        class Invalid(Event):
            _internal = FieldSpec(str)


def test_bool_is_not_accepted_as_integer_amount():
    # bool is a subclass of int; the schema deliberately rejects it for amounts.
    with pytest.raises(TypeError, match="amount_cents must be int"):
        InvoiceCreated(
            event_id="evt-1", invoice_id="inv-7", amount_cents=True
        )
```

Run:

```bash
python -m pytest -q
```

This is a learning project, not a production schema engine. It does not resolve forward references, support unions or coercion, validate nested records, handle schema versioning, or provide static type-checker support for dynamically declared instance attributes. A production design should state these limits and may be better served by `dataclasses`, Pydantic, attrs, or an explicit schema library.

### 14.2 Negative and positive tests for metaclass conflicts

The conflict example in Section 7 is deliberately reproducible. This isolated pytest test verifies both the failure and the compatible resolution, including the combined metaclass identity:

```python
import pytest

class AuditMeta(type):
    pass

class ValidationMeta(type):
    pass

class Audited(metaclass=AuditMeta):
    pass

class Validated(metaclass=ValidationMeta):
    pass


def test_unrelated_metaclasses_conflict():
    with pytest.raises(TypeError, match="metaclass conflict"):
        class BrokenCombined(Audited, Validated):
            pass


def test_derived_metaclass_resolves_conflict():
    class CombinedMeta(AuditMeta, ValidationMeta):
        pass

    class Combined(Audited, Validated, metaclass=CombinedMeta):
        pass

    assert type(Combined) is CombinedMeta
    assert Combined.__mro__[:3] == (Combined, Audited, Validated)
```

The conflict message shown here is the standard CPython wording for this condition; if testing across Python implementations, asserting `TypeError` without matching the message is less brittle.

## 15. Exercises

Try each before reading the solutions.

1. **Metaclass basics:** write a metaclass that attaches `created_by` containing the class name. Demonstrate that a subclass inherits the metaclass.
2. **Lifecycle:** use `__prepare__` to record class-body assignments. Explain why insertion-ordered dictionaries mean you should not use it only for ordering.
3. **Class versus instance:** create a metaclass `__call__` that logs construction and still preserves a class's custom `__init__`.
4. **Field validation:** extend `SchemaMeta` to reject duplicate field declarations across bases, or document a deterministic override policy.
5. **Conflict:** create two independent metaclasses and two bases using them. Show the conflict, then create a derived metaclass that resolves it. Make both parent hooks cooperative.
6. **Alternative design:** implement the same plugin registry with a class decorator, `__init_subclass__`, a descriptor, and a metaclass. Compare readability and typing support.
7. **Singleton:** implement a module-level `settings` instance and a cached factory. Explain how each changes state lifetime and testability compared with a singleton metaclass.
8. **Debugging:** for a class with a custom metaclass, print `type(cls)`, `cls.__mro__`, `type(cls).__mro__`, and selected `inspect` results.
9. **Standard library:** demonstrate why an abstract class cannot be instantiated, then implement a concrete subclass. Compare this with `typing.Protocol`.
10. **Testing:** add a fixture that restores a global registry even when an assertion fails. Test duplicate registration and avoid depending on test order.

## 16. Exercise solutions

### Solution 1

```python
class NamedMeta(type):
    def __new__(mcls, name, bases, namespace, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        cls.created_by = name
        return cls

class Base(metaclass=NamedMeta):
    pass

class Child(Base):
    pass

print(type(Child).__name__, Child.created_by)
```

Output: `NamedMeta Child`.

### Solution 2

Use the `TracingNamespace` example in Section 3.1. A normal `dict` preserves insertion order on supported modern Python versions; a custom namespace is useful to detect or record operations during execution, not merely to sort fields after the fact.

### Solution 3

Use `CallTrace` from Section 5. The critical line is `return super().__call__(*args, **kwargs)`, which delegates to the normal instance construction protocol.

### Solution 4

A clear policy is often better than forbidding all inherited overrides. For example, allow a subclass to replace a base field only with another `FieldSpec`, and explicitly remove inherited metadata when a subclass intentionally shadows a field with a non-field. Test the exact policy with multiple inheritance and shadowing.

### Solution 5

Use `CombinedMeta(AuditMeta, ValidationMeta)` from Section 7.3. Ensure every overridden `__new__`, `__init__`, or `__call__` calls `super()` and forwards unconsumed keyword arguments. A class that merely avoids `TypeError` but skips one parent's behavior is not a correct resolution.

### Solution 6

Sections 10.1–10.4 show the four patterns. The decorator is opt-in, `__init_subclass__` is automatic for subclasses, descriptors focus on fields, and the metaclass controls the whole class namespace. The metaclass is not automatically the most maintainable choice.

### Solution 7

For a fixed process-wide configuration:

```python
class Settings:
    def __init__(self, mode="prod"):
        self.mode = mode

settings = Settings()
```

Consumers import or receive `settings`. For a factory whose arguments identify a reusable object:

```python
from functools import cache

@cache
def get_client(endpoint: str):
    return Client(endpoint)
```

Here `Client` must be defined or imported by the application. `cache` retains results until cleared and requires hashable arguments; it does not magically make the result immutable or thread-safe in every respect. Dependency injection is preferable when tests or different application instances need different settings/clients.

### Solution 8

Use Section 11. Distinguish the class MRO (`cls.__mro__`) from the metaclass MRO (`type(cls).__mro__`).

### Solution 9

Use Section 8.1 for `ABC`/`abstractmethod`. A protocol describes expected operations structurally and can be checked statically without forcing the implementation class to inherit from a common base.

### Solution 10

Use the `isolated_registry` fixture in Section 12.3. The `finally` block restores the prior mapping even if the test fails.

## 17. Interview questions and model answers

1. **What is a metaclass?** The class of a class object. It controls how class objects are created; ordinary classes normally use `type`.
2. **What is the difference between metaclass `__new__` and `__init__`?** `__new__` creates the class object and can transform the namespace before calling `type.__new__`; metaclass `__init__` configures the returned class object afterward.
3. **What does `__prepare__` do?** It supplies the mapping used to execute the class body, allowing recording or validation while assignments happen.
4. **How does metaclass `__call__` differ from instance `__init__`?** It intercepts calls to the class object and normally delegates to `type.__call__`, which coordinates instance `__new__` and `__init__`.
5. **When is `__init_subclass__` sufficient?** When the requirement is to configure or validate subclasses after their class objects are created, without needing a custom class-body namespace or whole-namespace transformation.
6. **How do metaclass conflicts arise?** Multiple bases impose incompatible metaclasses with no common derived metaclass satisfying all of them.
7. **How can a conflict be resolved?** Define a metaclass inheriting from each required metaclass in a compatible order and make overridden hooks cooperative. If semantics are incompatible, redesign the composition instead.
8. **Why do descriptors matter here?** `__set_name__` lets attributes learn their owner/name during class creation, often removing the need for a metaclass when the task is field-level validation.
9. **What do `ABCMeta` and enum metaclasses provide?** Established rules for abstract base classes and enum member construction/validation. Prefer those standard abstractions over reimplementation.
10. **Why are metaclass singletons risky?** They hide shared state, complicate constructor semantics and test isolation, may leak instances, and need synchronization if initialization can race.
11. **Does a metaclass change `__slots__` after class creation?** No. Slot layout is determined during class construction; changes after the fact do not retroactively alter instance layout.
12. **What is the main design principle?** Prefer the least powerful mechanism that clearly meets the requirement; use a metaclass only when class creation itself must be controlled.

## 18. Competency checklist

You are ready to move on when you can explain or demonstrate each item without copying the examples:

- [ ] Explain `type(obj)`, `type(MyClass)`, and `type(name, bases, namespace)`.
- [ ] Explain metaclass inheritance and the class creation lifecycle.
- [ ] Distinguish metaclass hooks from instance `__new__` and `__init__`.
- [ ] Use `__prepare__` for a concrete namespace requirement, not just ordering.
- [ ] Explain why cooperative metaclass methods call `super()`.
- [ ] Build a tested field collector with inherited metadata and validation failures.
- [ ] Explain descriptor `__set_name__` and `__init_subclass__` timing.
- [ ] Demonstrate and resolve a metaclass conflict, including cooperative behavior.
- [ ] Explain the roles of `ABCMeta`, `EnumType`, `type.__getattribute__`, `__instancecheck__`, and `__subclasscheck__`.
- [ ] Describe interactions with `__slots__`, `dataclass`, and modern `Generic` support.
- [ ] Implement the same registry with four mechanisms and justify the simplest option.
- [ ] Inspect `type(cls)`, both relevant MROs, and class attributes with `inspect` safely.
- [ ] Explain singleton alternatives, import-time costs, performance measurement, and test isolation.
- [ ] Run the practical project's tests and explain its limitations.

## 19. Common mistakes to avoid

- Choosing a metaclass when a decorator or `__init_subclass__` is enough.
- Treating metaclass `__new__` as if it were instance `__new__`.
- Overriding `__call__` but forgetting `super().__call__`, thereby bypassing normal construction.
- Overriding metaclass hooks without cooperative `super()` in multiple inheritance.
- Assuming a metaclass method is also an instance method.
- Assuming custom `__prepare__` is necessary to preserve order on modern Python.
- Mutating a registry before validating a class, then leaving partial state when creation fails.
- Assuming `__init_subclass__` sees the class after class decorators have run.
- Treating a singleton metaclass as thread-safe or easy to reset in tests.
- Making runtime annotation evaluation assumptions without checking the Python version.

## Final takeaway

A metaclass is a mechanism for controlling **class objects**, not a general-purpose replacement for ordinary object-oriented design. Use it when you must shape or validate a class as it is created, or when reading a framework that relies on that pattern. For most application features, explicit code, decorators, descriptors, or `__init_subclass__` will be easier to understand, test, type-check, and maintain.
