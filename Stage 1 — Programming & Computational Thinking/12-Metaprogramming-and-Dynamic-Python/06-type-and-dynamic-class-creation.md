# Type and Dynamic Class Creation

**Stage 1 — Programming & Computational Thinking · Module 1.12: Metaprogramming and Dynamic Python**  
**Target runtime:** Python 3.12+ (version notes called out inline)

## Learning outcomes

By the end of this lesson, you should be able to:

- Distinguish `type(obj)` from `type(name, bases, namespace)` and explain why classes are objects.
- Translate a simple class statement into an equivalent three-argument `type()` call.
- Describe the major steps in class creation and choose `types.new_class()` when metaclass selection or class keywords matter.
- Use `types.FunctionType`, `types.MethodType`, `types.SimpleNamespace`, and `types.MappingProxyType` appropriately.
- Choose between `namedtuple`, `typing.NamedTuple`, `dataclasses.make_dataclass`, `enum.Enum`, and a third-party factory such as Pydantic's `create_model()`.
- Build a class from a validated schema while controlling metadata, type identity, memory use, and failure modes.
- Explain the limits of pickling, static analysis, `__class__` reassignment, and monkeypatching.
- Test generated classes and decide when ordinary classes or simpler factories are better engineering.

## 1. Prerequisites and object-model foundations

You should already know functions and closures, basic decorators, class inheritance and MRO, descriptors, type hints, and pytest basics. This lesson connects those concepts rather than replacing them.

### 1.1 Two meanings of `type`

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

- `type(customer)` asks: “What is this object's class?”
- `type(Customer)` asks for the class of the class object `Customer`; ordinary classes are instances of `type`.
- `type(type) is type` is a special but intentional part of Python's object model.

The three-argument form is different: `type(name, bases, namespace)` **creates a class object**. It is not merely introspection.

```python
Product = type("Product", (), {"category": "books"})
item = Product()
print(type(item) is Product, item.category, Product.__name__)
```

Expected output:

```text
True books Product
```

### 1.2 A class is an object

A class can be assigned to a variable, passed to a function, stored in a mapping, and returned from a factory. Instances are objects created by calling classes.

```python
def instantiate(cls):
    return cls()

class Marker:
    pass

created = instantiate(Marker)
print(isinstance(created, Marker))
print(isinstance(Marker, type))
```

Expected output:

```text
True
True
```

This makes runtime class factories possible. It does not mean every application should use them: dynamic classes add indirection and often reduce readability and static-analysis support.

## 2. Basic dynamic class creation

### 2.1 `type(name, bases, namespace)`

The three arguments are:

1. `name`: the class name as a string.
2. `bases`: a tuple of base classes, such as `(object,)` or `(BaseRecord,)`.
3. `namespace`: a mapping of class attributes, methods, descriptors, and special metadata.

```python
def hello(self):
    return f"hi from {type(self).__name__}"

Dynamic = type("Dynamic", (object,), {"greet": hello, "x": 1})
instance = Dynamic()

print(instance.greet())
print(instance.x)
print(Dynamic.__mro__)
```

Expected output:

```text
hi from Dynamic
1
(<class '__main__.Dynamic'>, <class 'object'>)
```

The exact module prefix can differ when run from an importable module rather than the interactive interpreter. The important point is the MRO order: `Dynamic`, then `object`.

**Why does `hello` become a method?** A Python function stored in a class namespace participates in descriptor binding. Accessing it through an instance produces a bound method, so `self` is supplied automatically. A function stored only on an instance generally does not receive this automatic binding.

### 2.2 Attributes, inheritance, and identity

```python
class Identified:
    def describe(self):
        return f"id={self.identifier}"

DynamicIdentified = type(
    "DynamicIdentified",
    (Identified,),
    {"identifier": "R-17", "kind": "generated"},
)

obj = DynamicIdentified()
print(obj.describe())
print(obj.kind)
print(issubclass(DynamicIdentified, Identified))
print(isinstance(obj, Identified))
print(DynamicIdentified.__bases__)
```

Expected output:

```text
id=R-17
generated
True
True
(<class '__main__.Identified'>,)
```

A generated class is a distinct object with its own identity. Two classes with identical names, bases, and attributes are not automatically the same class:

```python
First = type("Record", (), {})
Second = type("Record", (), {})
print(First is Second)
print(isinstance(First(), Second))
```

Expected output:

```text
False
False
```

This identity distinction is central to caching, `isinstance`, registries, and serialization.

## 3. Class statements versus `type()`

### 3.1 Equivalent simple forms

A simple class statement:

```python
class Greeter:
    greeting = "hello"

    def greet(self, name):
        return f"{self.greeting}, {name}!"
```

Can be expressed with `type()`:

```python
def greet(self, name):
    return f"{self.greeting}, {name}!"

Greeter = type(
    "Greeter",
    (object,),
    {"greeting": "hello", "greet": greet, "__module__": __name__},
)

print(Greeter().greet("Mira"))
```

Expected output:

```text
hello, Mira!
```

This is an equivalence of the **simple class shape**, not a universal statement that every class statement can be replaced by a bare `type()` call without changing behavior. A class statement has additional semantics: compiler-created metadata, special handling of `__class__` cells and zero-argument `super()`, metaclass selection, namespace preparation, class keywords, and base resolution.

For example, methods that use zero-argument `super()` rely on a compiler-provided `__class__` closure cell. Defining a normal function elsewhere and inserting it into a class dictionary does not magically create that cell. Prefer `types.new_class()` when class-creation protocol details matter; use a normal `class` statement when it is clearest.

### 3.2 What happens during a class statement?

A useful conceptual sequence is:

1. **Evaluate decorator expressions, bases, and class keywords.** Decorator expressions are evaluated before the class is created; expressions in the base list and keyword arguments are evaluated as part of class definition. `__mro_entries__` may resolve non-class bases.
2. **Select the metaclass.** An explicit `metaclass=` is considered; otherwise Python derives a metaclass from the bases (normally `type`). Conflicting metaclasses raise `TypeError`.
3. **Prepare the namespace.** The chosen metaclass's `__prepare__`, if present, supplies the mapping in which the body executes. Otherwise a normal namespace is used.
4. **Execute the class body.** The body runs with that namespace as its local namespace. Class-body code is executed; it is not just a dictionary literal.
5. **Create the class.** The metaclass is called with the name, bases, namespace, and class keywords. The usual metaclass is `type`.
6. **Apply class decorators and bind the result.** If decorators are present, the already-evaluated decorators are applied to the newly created class, from the innermost decorator outward. The final result is bound to the class name.

This is a practical mental model, not a replacement for the language reference. Metaclasses can customize parts of the process. The following simplified observation shows the prepared namespace hook:

```python
class RecordingMeta(type):
    @classmethod
    def __prepare__(mcls, name, bases, **kwargs):
        print(f"prepare:{name}")
        return {}

    def __new__(mcls, name, bases, namespace, **kwargs):
        print(f"create:{name}")
        return super().__new__(mcls, name, bases, namespace, **kwargs)

class Sample(metaclass=RecordingMeta):
    value = 3
```

Expected output:

```text
prepare:Sample
create:Sample
```

This example previews metaclasses; Lesson 07 explores them in depth. Do not introduce a metaclass just to add one attribute or method.

### 3.3 When ordinary code is better

Use the simplest mechanism that meets the requirement:

- Ordinary class: known structure and behavior at development time.
- Function or factory returning an instance: vary data, not the type.
- Class decorator: transform or augment a known class.
- `__init_subclass__`: validate or register subclasses.
- `type()` / `types.new_class()`: the class's structure itself must be generated at runtime.
- Metaclass: class-creation protocol needs customization that simpler tools cannot express.
- `exec`: only for carefully controlled code-generation use cases; never treat untrusted text as safe Python source.

## 4. `types.new_class()` and supporting utilities

### 4.1 `types.new_class`

`types.new_class(name, bases=(), kwds=None, exec_body=None)` follows Python's class-creation protocol, including metaclass selection and `__prepare__`. It is usually preferable to manually calling a metaclass when you need class keywords or metaclass behavior.

```python
from types import new_class

class TaggedMeta(type):
    def __new__(mcls, name, bases, namespace, *, tag=None, **kwargs):
        namespace["tag"] = tag
        return super().__new__(mcls, name, bases, namespace, **kwargs)

def populate(namespace):
    namespace["value"] = 42

Generated = new_class(
    "Generated",
    (object,),
    {"metaclass": TaggedMeta, "tag": "runtime"},
    populate,
)

print(Generated.value, Generated.tag, type(Generated).__name__)
```

Expected output:

```text
42 runtime TaggedMeta
```

The `kwds` mapping contains class keywords; `metaclass` is used to select the metaclass and is not passed as an ordinary class attribute. `exec_body` receives the prepared namespace, which lets the class-creation protocol execute the body-like population step.

Use `type()` for straightforward classes with a known namespace and no special class-creation protocol. Use `types.new_class()` when metaclass selection, nontrivial bases, or class keywords matter. It is not a security sandbox.

### 4.2 `types.FunctionType`

`types.FunctionType` constructs a function object from a code object and a globals dictionary. It is a low-level tool, not a replacement for `def` in normal code. Closures, defaults, annotations, and globals must be handled deliberately.

```python
from types import FunctionType

def template(value):
    return value * 2

recreated = FunctionType(template.__code__, template.__globals__, "recreated")
print(recreated(5), recreated.__name__)
```

Expected output:

```text
10 recreated
```

This works because `template` has no closure variables and its code uses no external local state. If a function references free variables, a compatible closure is required; constructing one incorrectly can fail or behave unexpectedly. Prefer a normal function, closure, or `functools.partial` unless you have a concrete low-level need.

### 4.3 `types.MethodType`

`MethodType(function, instance)` binds a function to a specific instance. It is useful for instance-local behavior changes; it does not install the method on the class.

```python
from types import MethodType

class Worker:
    def __init__(self, name):
        self.name = name


def report(self):
    return f"worker={self.name}"

worker = Worker("Asha")
worker.report = MethodType(report, worker)
print(worker.report())
print(hasattr(Worker, "report"))
```

Expected output:

```text
worker=Asha
False
```

A different `Worker` instance does not get `report`. Classes with `__slots__` that omit `__dict__` may prohibit assigning a new instance attribute.

### 4.4 `types.SimpleNamespace`

`SimpleNamespace` is a lightweight object for attribute-style access to a small collection of values. It is not a generated class and does not validate a schema.

```python
from types import SimpleNamespace

config = SimpleNamespace(host="localhost", port=5432)
print(config.host, config.port)
print(config)
config.port = 6432
print(config)
```

Expected output:

```text
localhost 5432
namespace(host='localhost', port=5432)
namespace(host='localhost', port=6432)
```

The first print displays the two attributes; the next line is the updated namespace representation. Use a dataclass or validated model when the shape, defaults, and types are part of a public contract.

### 4.5 `types.MappingProxyType` and `cls.__dict__`

`cls.__dict__` is a read-only mapping proxy over the class namespace. You cannot assign through it, but it reflects later changes made through normal class attribute assignment. It is not a deep immutable snapshot: mutable values stored in the mapping can still be mutated.

```python
from types import MappingProxyType

class Example:
    value = 1

namespace = Example.__dict__
print(isinstance(namespace, MappingProxyType))
print(namespace["value"])
Example.value = 2
print(namespace["value"])
```

Expected output:

```text
True
1
2
```

`namespace["value"] = 3` raises `TypeError`. To add or change a class attribute, use `setattr(Example, "value", 3)` or assignment. Do not try to mutate `cls.__dict__` directly.

## 5. Standard-library and ecosystem class factories

Use a purpose-built factory when it already models the desired semantics. A general `type()` call should not be your first choice for records, enums, or validated data models.

### 5.1 `collections.namedtuple`

```python
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])
p = Point(2, 5)
print(p, p.x, p[1])
```

Expected output:

```text
Point(x=2, y=5) 2 5
```

A named tuple is immutable and tuple-compatible. It is good for small fixed records; it is not intended for mutable domain entities or complex validation.

### 5.2 `typing.NamedTuple`

```python
from typing import NamedTuple

class Coordinate(NamedTuple):
    latitude: float
    longitude: float

print(Coordinate(12.9, 77.6))
```

Expected output:

```text
Coordinate(latitude=12.9, longitude=77.6)
```

The class syntax supports annotations and editor support. `typing.NamedTuple` also has a functional form, but use the class syntax when the fields are known at authoring time.

### 5.3 `dataclasses.make_dataclass`

```python
from dataclasses import make_dataclass

Invoice = make_dataclass(
    "Invoice",
    [("id", int), ("total", float), ("paid", bool, False)],
    namespace={"label": lambda self: f"invoice-{self.id}"},
)
invoice = Invoice(1, 9.99)
print(invoice)
print(invoice.label())
```

Expected output:

```text
Invoice(id=1, total=9.99, paid=False)
invoice-1
```

`make_dataclass()` generates dataclass behavior including an initializer and representation. It is a better fit than bare `type()` when the target is a dataclass record. Field annotations are not runtime validation by themselves: `Invoice(1, "not a float")` is generally allowed unless you add validation.

### 5.4 `enum.Enum` functional API

```python
from enum import Enum

Color = Enum("Color", "RED GREEN BLUE")
print(Color.RED, Color.RED.name, Color.RED.value)
```

Expected output:

```text
Color.RED RED 1
```

The functional API is useful when the set of enum members is data-driven. The default values shown are auto-assigned integers for this string form. Do not generate enum names directly from untrusted strings without validation.

### 5.5 Pydantic's `create_model()` — awareness

Pydantic (third-party package) provides `pydantic.create_model()` for runtime models with validation and parsing semantics. It is appropriate when your application already uses Pydantic and needs a dynamic model, such as a model assembled from trusted schema metadata.

```python
# Optional dependency: pydantic (install separately)
from pydantic import create_model

RuntimeUser = create_model(
    "RuntimeUser",
    name=(str, ...),
    active=(bool, True),
)

user = RuntimeUser(name="Sam")
print(user.name, user.active)
```

Expected output with a compatible installed Pydantic version:

```text
Sam True
```

This is an optional ecosystem example, not part of the standard library and not included in the no-dependency test suite. Pydantic's API and behavior vary by major version; check the documentation for the installed version. Do not assume Pydantic or Python annotations make arbitrary schemas trustworthy.

## 6. Schema-driven class generation

Dynamic models can be useful when a trusted external schema describes records at runtime—for example, one record type per database table, message format, or JSON schema. The difficult part is not calling `type()`: it is defining and validating the schema contract.

### 6.1 Design rules before writing a factory

- Accept only the schema forms your application explicitly supports.
- Validate class names and field names as identifiers; reject keywords and duplicates.
- Map external type labels through an allowlist. Never evaluate a schema string as Python code.
- Set defaults deliberately; distinguish “required” from “optional with default `None`”.
- Decide whether generated classes should be cached and how their identity is keyed.
- Decide whether instances need dataclass behavior, runtime validation, serialization, or just attribute access.
- Do not claim static type checkers can infer arbitrary runtime fields.

### 6.2 A small validated record factory

The following implementation deliberately supports only `str`, `int`, `float`, and `bool`. It is an educational example with production-oriented guardrails, not a complete JSON Schema implementation.

```python
# dynamic_records.py
from __future__ import annotations

import keyword
import re
from threading import RLock
from types import new_class
from typing import Any

_ALLOWED_TYPES: dict[str, type] = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
}
_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_CACHE: dict[tuple[str, str, tuple[tuple[str, str], ...]], type] = {}
_LOCK = RLock()
_MAX_CACHED_CLASSES = 256
_MAX_FIELDS = 100
_MAX_IDENTIFIER_LENGTH = 64
_RESERVED_FIELD_NAMES = {"as_dict"}


def _validate_identifier(value: object, *, label: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be a string")
    if (
        len(value) > _MAX_IDENTIFIER_LENGTH
        or not _NAME_RE.fullmatch(value)
        or keyword.iskeyword(value)
    ):
        raise ValueError(f"invalid {label}: {value!r}")
    return value


def make_record_class(
    class_name: str,
    fields: dict[str, str],
    *,
    module_name: str = __name__,
) -> type:
    """Create or reuse a record class from an allowlisted field schema.

    `fields` maps field names to the strings 'str', 'int', 'float', or 'bool'.
    The input is copied into a normalized immutable cache key.
    """
    class_name = _validate_identifier(class_name, label="class name")
    if not isinstance(module_name, str):
        raise TypeError("module_name must be a string")
    module_parts = module_name.split(".")
    if not module_parts or any(
        not _NAME_RE.fullmatch(part) or keyword.iskeyword(part)
        for part in module_parts
    ):
        raise ValueError(f"invalid module name: {module_name!r}")
    if not isinstance(fields, dict):
        raise TypeError("fields must be a dict[str, str]")
    if len(fields) > _MAX_FIELDS:
        raise ValueError(f"at most {_MAX_FIELDS} fields are supported")

    normalized: list[tuple[str, str]] = []
    for field_name, type_name in fields.items():
        field_name = _validate_identifier(field_name, label="field name")
        if field_name.startswith("_") or field_name in _RESERVED_FIELD_NAMES:
            raise ValueError(f"reserved field name: {field_name!r}")
        if not isinstance(type_name, str) or type_name not in _ALLOWED_TYPES:
            raise ValueError(f"unsupported field type for {field_name!r}")
        normalized.append((field_name, type_name))

    key = (module_name, class_name, tuple(normalized))
    with _LOCK:
        existing = _CACHE.get(key)
        if existing is not None:
            return existing
        # Reject new schemas at the limit rather than evicting a class whose
        # identity may still be relied on by existing instances or callers.
        if len(_CACHE) >= _MAX_CACHED_CLASSES:
            raise RuntimeError(
                f"class cache limit ({_MAX_CACHED_CLASSES}) reached; "
                "apply an explicit schema lifecycle policy"
            )

        annotations = {
            field_name: _ALLOWED_TYPES[type_name]
            for field_name, type_name in normalized
        }

        def populate(namespace: dict[str, Any]) -> None:
            namespace["__module__"] = module_name
            namespace["__qualname__"] = class_name
            namespace["__doc__"] = f"Generated record class {class_name}."
            namespace["__annotations__"] = annotations.copy()
            namespace["__init__"] = _make_init(tuple(annotations))
            namespace["as_dict"] = _make_as_dict(tuple(annotations))

        generated = new_class(class_name, (object,), exec_body=populate)
        _CACHE[key] = generated
        return generated


def _make_init(field_names: tuple[str, ...]):
    def __init__(self, **values: Any) -> None:
        expected = set(field_names)
        supplied = set(values)
        missing = expected - supplied
        extra = supplied - expected
        if missing or extra:
            raise TypeError(
                f"missing fields={sorted(missing)!r}; extra fields={sorted(extra)!r}"
            )
        for name in field_names:
            setattr(self, name, values[name])
    return __init__


def _make_as_dict(field_names: tuple[str, ...]):
    def as_dict(self) -> dict[str, Any]:
        return {name: getattr(self, name) for name in field_names}
    return as_dict
```

Usage (put this in a separate script next to `dynamic_records.py`, or append it under an `if __name__ == "__main__":` block):

```python
from dynamic_records import make_record_class

Order = make_record_class("Order", {"order_id": "int", "status": "str"})
order = Order(order_id=12, status="shipped")

print(order.as_dict())
print(Order.__module__, Order.__qualname__, Order.__doc__)
print(Order.__mro__)
print(make_record_class("Order", {"order_id": "int", "status": "str"}) is Order)
```

Expected output:

```text
{'order_id': 12, 'status': 'shipped'}
dynamic_records Order Generated record class Order.
(<class 'dynamic_records.Order'>, <class 'object'>)
True
```

The module prefix is `dynamic_records` if the module is imported under that name. If you run all code in a notebook or another module, the module metadata differs.

**Important limitations in this example:** the factory checks field names and schema type labels, but it does not validate the values passed to `Order(...)`; annotations are descriptive metadata. It also does not publish the generated class as `dynamic_records.Order` in the module globals. Consequently, setting `__module__` and `__qualname__` here does **not** guarantee that pickling the class or instances will work. A production factory must make a deliberate publication and lifecycle decision (see Section 7).

### 6.3 Tests for the record factory

```python
# test_dynamic_records.py
import pytest
import dynamic_records
from dynamic_records import make_record_class


@pytest.fixture(autouse=True)
def isolate_factory_cache():
    # Keep each test independent of generated classes retained by other tests.
    with dynamic_records._LOCK:
        original = dynamic_records._CACHE.copy()
        dynamic_records._CACHE.clear()
    try:
        yield
    finally:
        with dynamic_records._LOCK:
            dynamic_records._CACHE.clear()
            dynamic_records._CACHE.update(original)


def test_attributes_methods_and_metadata():
    Order = make_record_class("Order", {"order_id": "int", "status": "str"})
    order = Order(order_id=12, status="shipped")
    assert order.order_id == 12
    assert order.as_dict() == {"order_id": 12, "status": "shipped"}
    assert Order.__qualname__ == "Order"
    assert Order.__module__ == "dynamic_records"
    assert Order.__doc__ == "Generated record class Order."
    assert Order.__mro__[1] is object


def test_factory_caches_identical_schema():
    first = make_record_class("CachedRecord", {"value": "int"})
    second = make_record_class("CachedRecord", {"value": "int"})
    assert first is second
    assert isinstance(first(value=1), second)


def test_different_schema_has_different_identity():
    first = make_record_class("DifferentRecord", {"value": "int"})
    second = make_record_class("DifferentRecord", {"value": "str"})
    assert first is not second
    assert not isinstance(first(value=1), second)


def test_field_order_is_part_of_the_schema_key():
    first = make_record_class("OrderedRecord", {"first": "str", "second": "int"})
    second = make_record_class("OrderedRecord", {"second": "int", "first": "str"})
    assert first is not second
    assert list(first.__annotations__) == ["first", "second"]
    assert list(second.__annotations__) == ["second", "first"]


@pytest.mark.parametrize("bad_name", ["", "not-valid", "class", "has space", "_private"])
def test_rejects_invalid_field_names(bad_name):
    with pytest.raises(ValueError):
        make_record_class("BadSchema", {bad_name: "str"})


def test_rejects_unknown_type_label():
    with pytest.raises(ValueError):
        make_record_class("BadType", {"value": "object"})


def test_rejects_field_that_would_shadow_generated_method():
    with pytest.raises(ValueError):
        make_record_class("BadCollision", {"as_dict": "str"})


def test_rejects_non_mapping_schema():
    with pytest.raises(TypeError):
        make_record_class("BadSchemaType", [("value", "int")])


def test_rejects_non_string_class_name():
    with pytest.raises(TypeError):
        make_record_class(123, {"value": "int"})


def test_rejects_invalid_class_and_module_names():
    with pytest.raises(ValueError):
        make_record_class("not a class name", {"value": "int"})
    with pytest.raises(ValueError):
        make_record_class("ValidName", {"value": "int"}, module_name="bad-module")


def test_rejects_too_many_fields(monkeypatch):
    import dynamic_records

    monkeypatch.setattr(dynamic_records, "_MAX_FIELDS", 1)
    with pytest.raises(ValueError, match="at most"):
        make_record_class("TooManyFields", {"first": "int", "second": "str"})


def test_rejects_missing_and_extra_values():
    Record = make_record_class("StrictValues", {"value": "int"})
    with pytest.raises(TypeError):
        Record()
    with pytest.raises(TypeError):
        Record(value=1, extra=2)


def test_cache_limit_rejects_new_schema_without_evicting_existing(monkeypatch):
    import dynamic_records

    Record = make_record_class("AtCapacity", {"value": "int"})
    original_limit = dynamic_records._MAX_CACHED_CLASSES
    monkeypatch.setattr(dynamic_records, "_MAX_CACHED_CLASSES", len(dynamic_records._CACHE))
    try:
        with pytest.raises(RuntimeError, match="cache limit"):
            make_record_class("BeyondCapacity", {"value": "int"})
        assert make_record_class("AtCapacity", {"value": "int"}) is Record
    finally:
        monkeypatch.setattr(dynamic_records, "_MAX_CACHED_CLASSES", original_limit)
```

The cache is process-local. This teaching implementation caps it at 256 unique schemas and rejects further new schemas rather than evicting entries. That choice bounds retained classes while preserving identity for all schemas already admitted. Eviction can be appropriate for some workloads, but if an evicted schema is requested again, a new class object may be created and old instances will not satisfy `isinstance(old_instance, new_class)`. Choose a cache policy based on whether stable identity is part of the contract. The lock protects lookup-and-create as one critical section for threads using this factory; it does not make arbitrary class behavior or generated instances generally thread-safe.

## 7. Pickling, typing, caching, and security

### 7.1 Class metadata: `__module__`, `__qualname__`, and `__doc__`

- `__module__` identifies the module where the class is intended to live.
- `__qualname__` identifies its qualified name, including lexical nesting for normal nested definitions.
- `__doc__` is the class documentation string.

Setting these attributes improves introspection, documentation, and representations. It is not enough to make an object pickleable.

### 7.2 Pickling requires an importable binding

For ordinary class instances, pickle commonly records the class by module and qualified name. During unpickling, Python must be able to import that module and resolve the class at that name. A class created inside a function usually cannot be resolved by a stable module-level qualified name. Setting `__module__ = "some_module"` alone does not create a binding there.

For a generated class intended to be pickleable:

1. Generate it from an importable module, not a transient local scope.
2. Choose a stable name and metadata.
3. Publish it at that name in the module namespace (for example, a carefully managed module-level registry whose entries are also reachable as module attributes under the names used for pickling).
4. Ensure another process can import the same module and reconstruct or load the same binding before unpickling.
5. Test round-trip serialization in a fresh interpreter/process where practical.

For example, `module.__dict__[class_name] = generated_class` may publish a name, but only do this after validating the name and resolving collision policy. A generated class name that changes on every run or depends on request-specific data is not a reliable cross-process serialization contract. If schema evolution matters, a stable serialized data format is often better than pickling dynamic class objects.

### 7.3 A runnable pickle name-resolution check

Save this as `pickle_demo.py` and import it as a module (for example, `python -c "import pickle_demo"`). It deliberately contrasts a generated class that is not published under a module-level name with one that is. The test checks Python's actual lookup behavior rather than assuming metadata alone is enough.

```python
# pickle_demo.py
import pickle
from types import new_class


def make_record_type(name: str) -> type:
    def populate(namespace: dict[str, object]) -> None:
        namespace["__module__"] = __name__
        namespace["__qualname__"] = name
        namespace["__doc__"] = f"Generated class {name}."

    return new_class(name, (), exec_body=populate)


def make_unpublished_type() -> type:
    # __qualname__ is a simple name, but no module attribute has this name.
    return make_record_type("UnpublishedRecord")


# This object has module metadata, but no matching module-level binding yet.
_deliberately_missing = make_unpublished_type()
PublishedRecord = make_record_type("PublishedRecord")
try:
    pickle.dumps(_deliberately_missing)
except pickle.PicklingError as exc:
    print(type(exc).__name__)

# Publish the exact class under the name its metadata advertises.
UnpublishedRecord = _deliberately_missing
print(pickle.loads(pickle.dumps(PublishedRecord)) is PublishedRecord)
item = PublishedRecord()
item.value = 7
restored = pickle.loads(pickle.dumps(item))
print(type(restored) is PublishedRecord, restored.value)
```

Expected output:

```text
PicklingError
True
True 7
```

The failure is caused by the missing module-level binding at the time `pickle.dumps()` resolves the class. Once restored to the module namespace, the class is resolvable. The successful round trip assumes the module has already executed and created `PublishedRecord`. For a fresh process, the module must be importable and must recreate the same binding deterministically before unpickling. Do not delete or temporarily remove module globals in production code; this controlled demonstration makes the lookup requirement observable.

A companion test can verify the round-trip behavior after importing `pickle_demo`:

```python
# test_pickle_demo.py
import pickle
import pytest
import pickle_demo


def test_unpublished_class_fails_resolution():
    candidate = pickle_demo.make_record_type("NotPublishedForPickle")
    with pytest.raises(pickle.PicklingError):
        pickle.dumps(candidate)


def test_published_class_and_instance_round_trip():
    cls = pickle_demo.PublishedRecord
    assert pickle.loads(pickle.dumps(cls)) is cls
    item = cls()
    item.value = 9
    restored = pickle.loads(pickle.dumps(item))
    assert type(restored) is cls
    assert restored.value == 9
```

### 7.4 Static type checking and IDE support

Static type checkers analyze source and declared interfaces; they do not execute arbitrary runtime factories to discover every generated attribute. A class returned by `type()` may appear as `type` or a broad type in an IDE, and member completion may be poor.

Options:

- Prefer an ordinary class, `dataclass`, or typed protocol when the structure is known at development time.
- Provide a `.pyi` stub for a stable public API generated at build time.
- Use `if TYPE_CHECKING:` declarations to expose a static approximation when the runtime import is optional or dynamic. This is a type-checking aid, not runtime construction.
- Return a common protocol or base class when callers only need a stable shared interface.
- If the schema is genuinely arbitrary at runtime, document that callers need runtime validation or mapping-style access rather than promising static member completion.

Example of a `TYPE_CHECKING` declaration:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    class GeneratedOrder:
        order_id: int
        status: str
```

This declaration is visible to type checkers but does not create a runtime class named `GeneratedOrder`. Do not write runtime code that assumes it exists.

### 7.5 Caching and class identity

Every call to `type("Row", bases, namespace)` creates a new class unless your factory explicitly returns an existing one. Even if the name and members are identical, the identities differ. Consequences include:

- `isinstance(value, NewlyGeneratedClass)` may unexpectedly be false for instances of a previous class.
- Registries and caches may accumulate duplicate logical types.
- Pickle and debugging become harder because names do not uniquely identify class objects.
- Retained classes, their methods, and references to their instances consume memory. In a long-lived worker, unbounded generation can become memory growth.

Use a cache only if two schemas are semantically equivalent and should share type identity. Build a stable immutable key from all class-shaping inputs, normalize the schema, and consider a bounded cache or explicit lifecycle. Do not key only by the class name if field definitions, bases, validators, or options can differ. The example in Section 6 keys by class name and ordered field/type pairs; production code may need to include module, bases, defaults, validators, and schema version.

`functools.cache`/`lru_cache` can help when arguments are hashable and the factory's semantics are pure. A custom cache is appropriate when normalization, locking, or eviction is required. Weak references are not a universal solution: class identity must remain stable for as long as instances and callers rely on it.

### 7.6 Security and untrusted schemas

Dynamic class creation is not automatically arbitrary code execution, but unsafe schema handling can still cause serious problems: attribute shadowing, namespace collisions, unexpected descriptors, memory exhaustion from unbounded unique schemas, expensive validation, unsafe imports, and unsafe downstream serialization.

- Do not feed untrusted text to `eval()` or `exec()` to define fields or methods.
- Map schema type names through an allowlist instead of resolving arbitrary module paths or evaluating expressions.
- Reject special names such as `__dict__`, `__class__`, and reserved internal fields unless explicitly supported.
- Bound schema size, field count, identifier length, and cache growth. The sample caps field count and identifier length and rejects new schemas once its class-cache limit is reached; production limits should reflect workload and threat model.
- Keep generated behavior fixed and trusted; generate data structure, not executable methods from user text.
- Treat external schemas as data and validate them with a parser or a purpose-built schema validator.
- If multiple tenants can submit schemas, isolate quotas and avoid a global unbounded cache keyed by tenant-controlled values.

The sample factory is intentionally narrow and must not be described as a full security boundary or complete JSON Schema validator.

### 7.7 Assigning to an instance's `__class__`

`obj.__class__ = Other` is not a general-purpose conversion operation. Python permits it only for compatible types/layouts and may reject it with `TypeError`. Differences in object layout, slots, built-in representation, or extension-type constraints commonly prevent reassignment. Even when it succeeds, it can violate invariants expected by the original and target classes.

Prefer explicit conversion, an adapter, composition, or constructing a new object. Do not use `__class__` reassignment as a routine migration technique.

```python
class Original:
    pass

class Replacement:
    pass

obj = Original()
obj.__class__ = Replacement  # Compatible ordinary instance layouts in this example.
print(type(obj) is Replacement)

class Slotted:
    __slots__ = ("value",)

try:
    obj.__class__ = Slotted
except TypeError:
    print("incompatible layout")
```

Expected output:

```text
True
incompatible layout
```

The exact low-level layout checks depend on the involved types; use this only to understand the restriction, not as a conversion pattern.

### 7.8 Monkeypatching in tests: instance versus class

- `monkeypatch.setattr(instance, "method", replacement)` changes that instance's attribute (when assignment is supported). It usually does not bind a plain function the way class-level method lookup does; use `MethodType` if you deliberately need binding.
- `monkeypatch.setattr(Class, "method", replacement)` changes the class attribute and affects lookup on instances that do not shadow it, including existing instances. pytest restores the original attribute after the test.
- Patch the name where the code under test looks it up, not necessarily where it was originally defined.

Example:

```python
# test_monkeypatching.py
class Service:
    def status(self):
        return "real"


def test_instance_patch_is_local(monkeypatch):
    first = Service()
    second = Service()
    monkeypatch.setattr(first, "status", lambda: "fake")
    assert first.status() == "fake"
    assert second.status() == "real"


def test_class_patch_affects_existing_instances(monkeypatch):
    first = Service()
    second = Service()
    monkeypatch.setattr(Service, "status", lambda self: "fake")
    assert first.status() == "fake"
    assert second.status() == "fake"
```

These are separate tests because pytest restores the class after each test. If a class uses `__slots__` without a writable `__dict__`, an instance-level patch may fail; class-level patching may still work if the class attribute is replaceable.

## 8. Practical implementation project

This project combines the lesson's concepts: a class factory, a dynamically attached method, inheritance, MRO inspection, metadata, identity caching, and tests. The validated factory in Section 6 is the recommended baseline; the following smaller running example is designed to be easy to run from one file.

Save as `dynamic_class_demo.py`:

```python
from __future__ import annotations

from types import new_class


class Named:
    def display_name(self) -> str:
        return self.name


def make_message_type(class_name: str, *, prefix: str = "message") -> type:
    if not class_name.isidentifier() or class_name.startswith("_"):
        raise ValueError("class_name must be a public Python identifier")

    def populate(namespace: dict[str, object]) -> None:
        namespace["__module__"] = __name__
        namespace["__qualname__"] = class_name
        namespace["__doc__"] = f"Dynamically generated {class_name} type."
        namespace["prefix"] = prefix

        def render(self) -> str:
            return f"{self.prefix}: {self.display_name()}"

        namespace["render"] = render

    return new_class(class_name, (Named,), exec_body=populate)


if __name__ == "__main__":
    Message = make_message_type("Message", prefix="event")
    message = Message()
    message.name = "invoice.created"

    # Add a method after class creation. It becomes available to existing instances.
    def upper_name(self) -> str:
        return self.name.upper()

    setattr(Message, "upper_name", upper_name)

    print(message.display_name())
    print(message.render())
    print(message.upper_name())
    print([base.__name__ for base in Message.__mro__])
    print(Message.__module__, Message.__qualname__)
```

Expected output:

```text
invoice.created
event: invoice.created
INVOICE.CREATED
['Message', 'Named', 'object']
__main__ Message
```

`__main__` is expected when executing this file directly. When imported as a module, `__module__` will be the importable module name. The example deliberately does not claim that the class is pickleable: the factory has not published the generated class under a stable module-level binding. Also, `name` is assigned to the instance dynamically; a production model should define fields and validate them explicitly.

### 8.1 Test the project

Save as `test_dynamic_class_demo.py` beside the demo module:

```python
import pytest
from dynamic_class_demo import Named, make_message_type


def test_attributes_methods_inheritance_and_mro():
    Message = make_message_type("TestMessage", prefix="event")
    item = Message()
    item.name = "invoice.created"

    assert item.display_name() == "invoice.created"
    assert item.render() == "event: invoice.created"
    assert Message.__bases__[0].__name__ == "Named"
    assert Message.__mro__[1].__name__ == "Named"
    assert isinstance(item, Message)
    assert isinstance(item, Named)


def test_metadata():
    Message = make_message_type("MetadataMessage")
    assert Message.__name__ == "MetadataMessage"
    assert Message.__qualname__ == "MetadataMessage"
    assert Message.__module__ == "dynamic_class_demo"
    assert "MetadataMessage" in Message.__doc__


def test_each_call_creates_distinct_class_without_cache():
    First = make_message_type("SameName")
    Second = make_message_type("SameName")
    assert First is not Second
    assert not isinstance(First(), Second)


def test_invalid_class_name():
    with pytest.raises(ValueError):
        make_message_type("not a valid name")
```

The test imports the real `Named` base class and verifies the actual inheritance contract.

Run from the directory containing the files:

```bash
python -m pytest -q
python dynamic_class_demo.py
```

### 8.2 Improve the project for production

Before shipping a factory, make explicit decisions about:

- Schema versioning and compatibility.
- Cache maximum size, eviction, locking, and metrics.
- Collision handling for names and module publication.
- Whether runtime value validation is required.
- Stable serialization format and cross-process reconstruction.
- Error messages and observability for invalid schemas.
- How static type checkers and users discover the generated interface.
- Whether a dataclass, Pydantic model, named tuple, mapping, or plain object is a better fit.

Do not cache classes solely because caching is possible. Cache when identity sharing is part of the intended contract.

## 9. Exercises with solutions

### Exercise 1 — Translate a class statement

Given a class with class attribute `kind = "sensor"` and method `label(self)` returning `self.kind`, write the equivalent `type()` call.

**Solution:**

```python
def label(self):
    return self.kind

Sensor = type("Sensor", (object,), {"kind": "sensor", "label": label})
print(Sensor().label())
```

Output:

```text
sensor
```

### Exercise 2 — Add a method after creation

Create a dynamic class `Counter` with `value = 4`. Add `double(self)` after class creation and prove an instance created before the patch can call it.

**Solution:**

```python
Counter = type("Counter", (), {"value": 4})
item = Counter()

setattr(Counter, "double", lambda self: self.value * 2)
print(item.double())
```

Output:

```text
8
```

The instance performs attribute lookup on the class, so the newly added method is visible to an existing instance unless an instance attribute shadows that name.

### Exercise 3 — Compare identity

Why can instances from two calls to a naive class factory fail `isinstance(instance, second_class)` even if both classes look the same?

**Solution:** each call creates a distinct class object. `isinstance` follows the instance's actual class and its inheritance relationships; matching names or attributes do not establish identity or subclassing.

### Exercise 4 — Validate a schema

Extend the Section 6 factory to reject duplicate field names from a list-based input schema before converting it to a dictionary. Why must this happen before the dictionary conversion?

**Solution:** a dictionary silently overwrites duplicate keys, so duplicate information is lost after conversion. Validate the ordered list first, then normalize it into a mapping. For example:

```python
def validate_field_pairs(pairs):
    seen = set()
    normalized = []
    for name, type_name in pairs:
        if name in seen:
            raise ValueError(f"duplicate field: {name}")
        seen.add(name)
        normalized.append((name, type_name))
    return normalized
```

### Exercise 5 — Explain pickle behavior

Why doesn't setting `Generated.__module__ = "my_package.models"` guarantee that pickle works?

**Solution:** pickle must import that module and resolve the class by its qualified name. The module must exist and expose the same class at that name. Assigning a string to `__module__` does not create or register that binding.

### Exercise 6 — Choose the right factory

Pick a mechanism for each case: immutable tuple-like row; annotated fixed record; enum members derived from trusted config; runtime validated API payload model in a Pydantic project; class structure based on a runtime schema with custom metaclass keywords.

**Solution:** `collections.namedtuple`; `typing.NamedTuple` or a dataclass; `enum.Enum` functional API; Pydantic `create_model()`; `types.new_class()` respectively. Reconsider a runtime class if a mapping or fixed model is enough.

## 10. Interview questions and final competency checklist

### Interview questions

1. What is the difference between `type(obj)` and `type(name, bases, namespace)`?
2. Why is `type(type) is type` true?
3. How does a function in a class namespace become a bound method?
4. Why is a class statement more than a bare call to `type()`?
5. When should you prefer `types.new_class()`?
6. What does `MappingProxyType` guarantee, and what does it not guarantee?
7. Compare `namedtuple`, `NamedTuple`, `make_dataclass`, and `Enum`'s functional API.
8. Why are generated classes difficult for static type checkers and IDEs?
9. Why doesn't `__module__` alone make a class pickleable?
10. How can repeated class generation affect memory and `isinstance()`?
11. What should a safe schema-to-class factory validate?
12. What are the risks and limitations of assigning to `obj.__class__`?
13. How does patching a class attribute differ from patching an instance attribute?
14. When is a normal class or dataclass preferable to dynamic class generation?

### Competency checklist

- [ ] I can explain both forms of `type()` without conflating introspection and construction.
- [ ] I can create a dynamic class with attributes, methods, and a base class.
- [ ] I can inspect `__bases__`, `__mro__`, `__module__`, `__qualname__`, and `__doc__`.
- [ ] I understand method binding and why functions attached to instances behave differently.
- [ ] I can describe the class-statement creation sequence and use `types.new_class()` when appropriate.
- [ ] I know when to choose standard-library factories instead of raw `type()`.
- [ ] I can validate schema names and type labels without `eval()` or `exec()`.
- [ ] I understand class identity, caching, memory retention, and `isinstance()` behavior.
- [ ] I know the importable module binding requirement for reliable pickling.
- [ ] I can describe static typing workarounds and their limits.
- [ ] I can explain `__class__` reassignment restrictions and test monkeypatch scope.
- [ ] I can justify why a simpler mechanism is sufficient—or explain why dynamic class creation is genuinely needed.

### Self-check answers

1. `type(obj)` returns an object's class; the three-argument form constructs a class object.
2. `types.new_class()` follows metaclass selection, `__prepare__`, and class keyword protocol rather than bypassing them with a hand-built namespace call.
3. A locally defined class normally has no stable importable module-level qualified name; pickle cannot resolve it from a fresh import unless the module binding is deliberately established.

## Version and compatibility notes

- Target the examples at Python 3.12+. The core forms `type(name, bases, namespace)`, `types.new_class`, `dataclasses.make_dataclass`, and the other listed factories are established APIs.
- `types.new_class()` and the exact details of class creation are specified by the Python language/runtime; when relying on advanced metaclass hooks, verify behavior against the version you deploy.
- Pydantic is third-party. Its API and validation behavior vary between major versions; the example is intentionally labeled optional.
- Python 3.13/3.14 introduce broader typing and annotation changes elsewhere in Python. This lesson does not depend on a particular new annotation-evaluation API; do not infer runtime validation from annotations in any supported version.

## Final engineering rule

Dynamic class creation is useful when the **type structure** is genuinely runtime data. If only values differ, use ordinary objects. If a record, enum, or validated model matches the requirement, prefer its dedicated factory. Generate classes deliberately, validate the schema, test identity and behavior, and make serialization and typing contracts explicit.
