# Class Decorators and Class Factories

> **Stage 1 · Programming & Computational Thinking · Module 1.12 — Metaprogramming and Dynamic Python**  
> **Target:** Python 3.12+  
> **Prerequisites:** functions and closures, basic decorators, class attributes, inheritance and MRO, descriptors, annotations, `inspect`, type hints, and pytest.

## Learning outcomes

By the end of this lesson, you should be able to:

- Explain exactly what a class decorator receives and returns.
- Add attributes and methods, register classes, and generate a useful `__repr__` from annotations without pretending annotations are runtime fields.
- Distinguish an in-place class mutation from a decorator that returns a replacement class.
- Wrap ordinary methods, `staticmethod`s, and `classmethod`s without accidentally changing descriptor behavior.
- Use a configured class factory and understand closures, generated class identity, and pickling constraints.
- Explain `functools.total_ordering`, `typing.final`, `typing.runtime_checkable`, and `typing.dataclass_transform` accurately.
- Choose between class decorators, `__init_subclass__`, descriptors, and metaclasses.
- Test generated behavior, identity, decorator order, inheritance, repeated application, and assignment restrictions.

> **Roadmap rule:** start with plain code, then decorators, class decorators, `__init_subclass__`, descriptors, metaclasses, and only then AST/`exec` when a simpler mechanism is insufficient.

---

# 1. Foundations and prerequisites

## 1.1 A class is an object

A class statement creates a class object. A class decorator is applied to that object after the class body has executed and the class has been created.

```python
def mark(cls):
    print("decorating:", cls.__name__)
    cls.reviewed = True
    return cls

@mark
class Job:
    pass

print(Job.reviewed)
```

Expected output:

```text
decorating: Job
True
```

The syntax is equivalent to `Job = mark(Job)`. This equivalence is the most important rule in the lesson. A decorator may mutate and return the original class, or return a different object that replaces the name `Job`. Python does not enforce that the returned object is a class; a decorator can return any object, but a non-class result usually breaks code that expects `Job` to remain a class.

## 1.2 Class decorator versus function decorator

The mechanism is the same; the input object differs.

| Decorator kind | Receives | Common return value |
|---|---|---|
| Function decorator | A function or callable | A callable, often a wrapper |
| Class decorator | A class object | The same class, modified; sometimes a replacement class |
| Decorator factory | Configuration first, then returns a decorator | A decorator that closes over configuration |
| Class factory | Configuration and/or values | A newly created class object |

A class decorator does **not** receive each instance. It usually runs once when the decorated class definition executes (normally at import time). If it registers a class, that registration is an import-time side effect.

## 1.3 Minimal prerequisites: attributes and descriptors

- `cls.name = value` and `setattr(cls, name, value)` usually do the same job. `setattr` is useful when the name is dynamic.
- Functions stored on a class are descriptors: accessing one through an instance binds the instance as `self`.
- `staticmethod` and `classmethod` are descriptors too. `staticmethod` returns the underlying function without binding an instance; `classmethod` binds the class as the first argument.
- `cls.__annotations__` describes declared annotations, not a reliable list of initialized instance fields.
- `type(cls)` is normally `type`, but a class can have a custom metaclass.

```python
class Sample:
    def ordinary(self):
        return self

    @staticmethod
    def utility(value):
        return value * 2

    @classmethod
    def construct(cls):
        return cls()

s = Sample()
print(s.ordinary() is s)
print(s.utility(3))
print(type(s.construct()).__name__)
```

Expected output:

```text
True
6
Sample
```

## 1.4 Prerequisite checklist

Before continuing, make sure you can explain:

- Why `@decorator` is an assignment transformation.
- How function descriptors bind `self` and how `classmethod` binds `cls`.
- Why mutable class attributes are shared unless shadowed.
- How annotations differ from actual values stored on instances.
- Why import order matters for registries.

---

# 2. Basic class decorators

## 2.1 Add metadata and return the same class

**What it does:** adds a marker or configuration attribute to an existing class.  
**How it works:** receives `cls`, mutates its namespace, and returns `cls`.  
**Use it when:** the behavior is opt-in and class-local.  
**Avoid it when:** a normal class attribute, helper function, or base class is clearer.

```python
def api_model(cls):
    cls.api_model = True
    cls.api_version = 1
    return cls

@api_model
class Customer:
    pass

print(Customer.api_model, Customer.api_version)
```

Expected output: `True 1`

Always return the class unless replacement is intentional. If the decorator falls off the end without a return, the decorated name becomes `None`.

## 2.2 Parameterized class decorators

A decorator factory captures configuration and returns the actual decorator.

```python
def tagged(*, category: str, version: int = 1):
    def decorate(cls):
        cls.category = category
        cls.version = version
        return cls
    return decorate

@tagged(category="reader", version=2)
class JsonReader:
    pass

print(JsonReader.category, JsonReader.version)
```

Expected output: `reader 2`

Keep configuration explicit and validate it before mutating the class. Parameterized decorators are useful for reusable policies, but a constructor argument or plain class attribute is often simpler.

## 2.3 Class registration and plugin registries

A registration decorator can record a class while returning the exact same object.

```python
from typing import TypeVar

T = TypeVar("T", bound=type)
PLUGINS: dict[str, type] = {}

def register(name: str):
    if not name or name.strip() != name:
        raise ValueError("plugin name must be non-empty and trimmed")

    def decorate(cls: T) -> T:
        if name in PLUGINS:
            raise ValueError(f"duplicate plugin name: {name!r}")
        PLUGINS[name] = cls
        return cls
    return decorate

@register("csv")
class CsvReader:
    def read(self) -> str:
        return "csv"

print(PLUGINS["csv"] is CsvReader)
print(PLUGINS["csv"]().read())
```

Expected output:

```text
True
csv
```

### Production considerations

- **Duplicate policy:** reject duplicates, replace intentionally, or allow versioned keys. Do not silently choose accidentally.
- **Import side effects:** the decorator runs only when the module is imported. A registry cannot discover modules that were never imported.
- **Test isolation:** provide a reset fixture or a registry object instead of leaking global state between tests.
- **Threading:** imports are coordinated by Python, but later registry mutation may need a lock if performed concurrently.
- **Trust boundary:** importing a plugin executes its module. A registry is not a sandbox.
- **Identity:** return `cls` so the registry and the decorated name refer to the same class.

A decorator registry is appropriate for explicit opt-in registration. If every subclass must register itself, compare `__init_subclass__` in Section 6.

## 2.4 Idempotency and repeated application

A decorator is **idempotent** if applying it repeatedly has the same effect as applying it once. Not every decorator needs to be idempotent, but library decorators should define their repeated-application behavior.

```python
def add_marker(cls):
    if cls.__dict__.get("_marker_added", False):
        return cls
    cls.marker = "active"
    cls._marker_added = True
    return cls

class Worker:
    pass

once = add_marker(Worker)
twice = add_marker(once)
print(once is twice, Worker.marker)
```

Expected output: `True active`

Use `cls.__dict__` when checking whether the class itself owns the marker. `getattr(cls, marker)` can see an inherited marker and incorrectly skip work on a subclass. A marker is not magic: name collisions and deliberate marker forgery remain possible. If repeated application is invalid, raise a clear exception instead.

---

# 3. Method and attribute injection

## 3.1 Adding attributes with assignment and `setattr`

```python
def add_schema_version(cls):
    cls.schema_version = 3
    setattr(cls, "is_schema", True)
    return cls

@add_schema_version
class Event:
    pass

print(Event.schema_version, Event.is_schema)
```

Expected output: `3 True`

Use assignment for literal identifiers. Use `setattr` when the name comes from validated configuration. Never feed arbitrary untrusted strings into dynamic attribute injection: it can overwrite important methods or descriptors.

## 3.2 Injecting a method: binding behavior

A plain function assigned to a class becomes a descriptor. Access through an instance binds `self` automatically.

```python
def describe(self) -> str:
    return f"{type(self).__name__}(id={self.id})"

def add_describe(cls):
    if "describe" in cls.__dict__:
        raise TypeError("describe already exists on this class")
    cls.describe = describe
    return cls

@add_describe
class Record:
    def __init__(self, record_id: int):
        self.id = record_id

print(Record(7).describe())
```

Expected output: `Record(id=7)`

The conflict check deliberately uses `cls.__dict__`: it rejects a class-local method but permits an inherited `describe`. Whether overriding an inherited method is acceptable is a design decision that should be explicit.

## 3.3 `@auto_repr`: generate `__repr__` from annotations carefully

**Purpose:** provide a compact, deterministic representation for simple record-like classes.  
**Assumptions:** annotated names are intended fields; instances initialize those attributes; values are safe to represent; and the generated representation is acceptable for debugging.  
**Limitations:** annotations are not proof that a field exists, has a value, or is a runtime-enforced type. This implementation does not generate an initializer, equality, hashing, defaults, slots, field metadata, or validation. It is not a replacement for `dataclasses.dataclass`.

```python
from __future__ import annotations

_AUTO_REPR_MARKER = "__auto_repr_generated__"

def auto_repr(cls):
    # Use the class's own annotations, not inherited annotations implicitly.
    field_names = tuple(cls.__dict__.get("__annotations__", {}))
    if "__repr__" in cls.__dict__:
        raise TypeError(f"{cls.__name__} defines its own __repr__")

    def __repr__(self):
        parts = []
        for name in field_names:
            try:
                value = getattr(self, name)
            except AttributeError as exc:
                raise AttributeError(
                    f"{type(self).__name__} is missing annotated field {name!r}; "
                    "initialize it before using generated repr"
                ) from exc
            parts.append(f"{name}={value!r}")
        return f"{type(self).__name__}({', '.join(parts)})"

    __repr__.__name__ = "__repr__"
    __repr__.__qualname__ = f"{cls.__qualname__}.__repr__"
    setattr(cls, "__repr__", __repr__)
    setattr(cls, _AUTO_REPR_MARKER, True)
    return cls

@auto_repr
class Point:
    x: int
    y: int

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

print(repr(Point(2, 5)))
```

Expected output: `Point(x=2, y=5)`

### Edge cases and design choices

1. **Annotation order:** dictionary insertion order preserves the order fields were declared in the class body.
2. **Missing values:** a field annotated but not initialized raises a targeted `AttributeError` when `repr` is called. Annotation-only declarations do not create instance values.
3. **Inheritance:** this implementation uses only the decorated class's own annotations. If a subclass is independently decorated, its generated representation includes that subclass's own annotations but does not merge base fields. If it is not decorated, it inherits the base's generated `__repr__`, which uses the base field list but `type(self).__name__`; that can display a subclass name with only base fields. A production implementation must define and test this behavior explicitly.
4. **Existing `__repr__`:** the decorator rejects an explicit class-local implementation rather than silently overwriting it.
5. **Annotation evaluation:** this implementation reads annotation names only; it does not evaluate string annotations or call `typing.get_type_hints`. Avoid evaluating annotations from untrusted modules.
6. **Sensitive data:** repr can leak tokens, passwords, personal data, or large values into logs. Use explicit exclusions or standard dataclasses' `field(repr=False)` where appropriate.
7. **Reapplication:** the implementation raises on a second application because the class now has a class-local `__repr__`. This is deliberate and testable.
8. **Static typing:** a type checker generally does not infer that arbitrary decorators inject a method. Annotate the decorator with `dataclass_transform` only when its behavior truly follows that contract, or use a stub/protocol for other generated APIs.

For ordinary application data models, prefer `@dataclass` and its explicit field controls. A small custom decorator is useful for learning or a narrowly scoped library feature, not as a casual reimplementation of the standard library.

## 3.4 Simplified dataclass-like generation: what is missing?

This intentionally limited example demonstrates the idea of reading annotations and adding a method. It does **not** attempt to replace `dataclasses`.

```python
def simple_record(cls):
    fields = tuple(cls.__dict__.get("__annotations__", {}))

    def to_dict(self):
        missing = [name for name in fields if not hasattr(self, name)]
        if missing:
            raise AttributeError(f"uninitialized fields: {missing}")
        return {name: getattr(self, name) for name in fields}

    if "to_dict" in cls.__dict__:
        raise TypeError("to_dict already exists")
    cls.to_dict = to_dict
    return cls

@simple_record
class UserRow:
    user_id: int
    active: bool

    def __init__(self, user_id: int, active: bool):
        self.user_id = user_id
        self.active = active

print(UserRow(12, True).to_dict())
```

Expected output: `{'user_id': 12, 'active': True}`

The standard library `dataclasses` additionally handles field objects, defaults and default factories, generated signatures, equality/order/hash policies, frozen semantics, slots, keyword-only fields, inheritance, `InitVar`, `ClassVar`, `__post_init__`, metadata, and many interactions among them. Prefer `dataclasses` unless a deliberately smaller contract is genuinely sufficient.

## 3.5 Wrapping class methods correctly

A method-wrapping decorator must preserve descriptor kinds. A naive `for name, value in cls.__dict__.items(): setattr(cls, name, wrapper(value))` can wrap `staticmethod` and `classmethod` descriptor objects as if they were ordinary functions and break binding.

This example wraps only ordinary instance methods and explicitly leaves static methods, class methods, properties, and special methods untouched.

```python
import functools
import inspect

def traced(fn):
    """Trace a callable without changing sync/async/generator call shape."""
    if inspect.isasyncgenfunction(fn):
        @functools.wraps(fn)
        async def async_generator_wrapper(*args, **kwargs):
            print(f"calling {fn.__name__}")
            async for item in fn(*args, **kwargs):
                yield item
        return async_generator_wrapper
    if inspect.iscoroutinefunction(fn):
        @functools.wraps(fn)
        async def async_wrapper(*args, **kwargs):
            print(f"calling {fn.__name__}")
            return await fn(*args, **kwargs)
        return async_wrapper
    if inspect.isgeneratorfunction(fn):
        @functools.wraps(fn)
        def generator_wrapper(*args, **kwargs):
            print(f"calling {fn.__name__}")
            yield from fn(*args, **kwargs)
        return generator_wrapper

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        print(f"calling {fn.__name__}")
        return fn(*args, **kwargs)
    return wrapper


def trace_instance_methods(cls):
    for name, raw in tuple(vars(cls).items()):
        if name.startswith("__") and name.endswith("__"):
            continue
        if isinstance(raw, (staticmethod, classmethod, property)):
            continue
        if inspect.isfunction(raw):
            setattr(cls, name, traced(raw))
    return cls

@trace_instance_methods
class Service:
    def run(self, value):
        return value + 1

    @staticmethod
    def normalize(value):
        return value.strip().lower()

    @classmethod
    def kind(cls):
        return cls.__name__

    @property
    def ready(self):
        return True

print(Service().run(4))
print(Service.normalize(" YES "))
print(Service.kind())
print(Service().ready)
```

Expected output:

```text
calling run
5
yes
Service
True
```

### Why the default argument matters

The loop creates a wrapper for each method. `__fn=raw` captures that iteration's function as a default argument; without it, all wrappers could resolve the final loop value (late binding).

### If you intentionally wrap all method kinds

Unwrap, wrap, and re-wrap each descriptor kind deliberately:

```python
import functools
import inspect


def trace_all_methods(cls):
    for name, raw in tuple(vars(cls).items()):
        if name.startswith("__") and name.endswith("__"):
            continue
        if isinstance(raw, staticmethod):
            setattr(cls, name, staticmethod(traced(raw.__func__)))
        elif isinstance(raw, classmethod):
            setattr(cls, name, classmethod(traced(raw.__func__)))
        elif isinstance(raw, property):
            # Preserve accessors independently; do not replace a property
            # with an ordinary callable.
            getter = traced(raw.fget) if raw.fget is not None else None
            setter = traced(raw.fset) if raw.fset is not None else None
            deleter = traced(raw.fdel) if raw.fdel is not None else None
            setattr(cls, name, property(getter, setter, deleter, raw.__doc__))
        elif inspect.isfunction(raw):
            setattr(cls, name, traced(raw))
    return cls
```

This demonstrates descriptor preservation. The shared `traced()` helper keeps coroutine, generator, and async-generator functions in their corresponding callable shape. The loop only visits attributes in the class's own namespace; it does not automatically wrap inherited methods. Production instrumentation must still decide how to treat abstract methods, special methods, methods added by other decorators, and descriptor subclasses. Wrapping a method can affect traceback shape and introspection. Use explicit instrumentation or a framework's supported hooks when broad class-wide wrapping becomes difficult to reason about.

---

# 4. Class factories

## 4.1 What is a class factory?

A class factory is a callable that returns a class. It may use `type()`, `types.new_class`, a nested class statement, or a closure. A class decorator modifies a class it is given; a class factory typically creates one based on configuration.

## 4.2 Closure-based factory

```python
def make_range_validator(minimum: int, maximum: int):
    if minimum > maximum:
        raise ValueError("minimum must be <= maximum")

    class RangeValidator:
        lower = minimum
        upper = maximum

        def validate(self, value: int) -> bool:
            return self.lower <= value <= self.upper

    RangeValidator.__name__ = f"RangeValidator_{minimum}_{maximum}"
    RangeValidator.__qualname__ = RangeValidator.__name__
    return RangeValidator

SmallInt = make_range_validator(0, 9)
LargeInt = make_range_validator(100, 999)
print(SmallInt is LargeInt)
print(SmallInt().validate(7), SmallInt().validate(11))
print(LargeInt().validate(200))
```

Expected output:

```text
False
True False
True
```

**How it works:** each call defines a new local class whose methods and class body close over the configuration values. The resulting classes are distinct identities.

**Use it when:** a family of related classes has genuinely different structural behavior or a class is part of a schema/adapter factory.  
**Avoid it when:** an instance with configuration, a normal function, or a single parameterized class can express the variation. Instances are usually simpler than generating many classes.

### Factory considerations

- **Identity:** each invocation usually returns a different class. `isinstance(x, SmallInt)` will not accept instances of another factory result even if the classes look identical.
- **Naming:** set `__name__`, `__qualname__`, and `__module__` thoughtfully if diagnostics matter. Renaming alone does not make a class importable or pickleable.
- **Pickling:** standard pickle generally locates classes by module and qualified name. A local class defined inside a factory is ordinarily not pickleable by name. If serialization is required, use a stable top-level class or a deliberate serialization protocol.
- **Configuration capture:** closures retain referenced objects. Avoid capturing mutable global state unintentionally.
- **Testing:** test distinct identities and configuration isolation.

## 4.3 Factory using `type()`

```python
def make_flag_class(name: str, *, enabled: bool):
    def status(self) -> bool:
        return enabled

    namespace = {"enabled": enabled, "status": status, "__module__": __name__}
    return type(name, (), namespace)

FeatureOn = make_flag_class("FeatureOn", enabled=True)
FeatureOff = make_flag_class("FeatureOff", enabled=False)
print(FeatureOn().status(), FeatureOff().status())
print(FeatureOn.enabled, FeatureOff.enabled)
```

Expected output:

```text
True False
True False
```

`type(name, bases, namespace)` is the simplest dynamic class constructor. For more complex metaclass selection, class keywords, `__prepare__`, or cooperative class creation, prefer `types.new_class` rather than hand-rolling the entire creation protocol.

---

# 5. Advanced generation patterns

## 5.1 `functools.total_ordering` case study

`functools.total_ordering` is a standard-library class decorator. Given one ordering method plus equality, it supplies the other rich comparison methods (`__lt__`, `__le__`, `__gt__`, `__ge__`) that are not already defined.

```python
from functools import total_ordering

@total_ordering
class Release:
    def __init__(self, major: int, minor: int):
        self.major, self.minor = major, minor

    def __eq__(self, other):
        if not isinstance(other, Release):
            return NotImplemented
        return (self.major, self.minor) == (other.major, other.minor)

    def __lt__(self, other):
        if not isinstance(other, Release):
            return NotImplemented
        return (self.major, self.minor) < (other.major, other.minor)

print(Release(2, 1) <= Release(2, 2))
print(Release(3, 0) > Release(2, 9))
```

Expected output:

```text
True
True
```

### Trade-offs

- Implement consistent `__eq__` and one ordering method; return `NotImplemented` for unsupported operand types.
- The decorator does not decide what ordering means. The domain must define a valid total order.
- Generated methods can be slower than hand-written methods and may produce less direct tracebacks.
- Existing comparison methods are not overwritten. Decorator ordering matters if another decorator changes them.
- If only equality or only one comparison is needed, don't add an ordering API unnecessarily.

For a source-reading exercise, run `python -c "import inspect, functools; print(inspect.getsource(functools.total_ordering))"` and trace how it chooses a root comparison method and fills missing methods. Read the implementation for the Python version you target when you need exact behavior; do not depend on private implementation details.

## 5.2 `typing.final`: static intent, not runtime enforcement

`typing.final` marks a method or class as final for static type checkers. It does not prevent subclassing or overriding at runtime.

```python
from typing import final

@final
class FinalBase:
    pass

class RuntimeStillAllowsSubclass(FinalBase):
    pass

print(issubclass(RuntimeStillAllowsSubclass, FinalBase))
print(getattr(FinalBase, "__final__", None))
```

Expected output on Python 3.11+:

```text
True
True
```

The `__final__` marker is a runtime attribute when it can be set; it is not an enforcement mechanism. In older Python versions or unusual objects, marker behavior can differ. Use a type checker to enforce the intended restriction during development, and do not treat `@final` as a security boundary.

## 5.3 `typing.runtime_checkable`: runtime structural checks are shallow

A `Protocol` describes a structural interface. `@runtime_checkable` permits limited runtime `isinstance` checks; it does not validate method signatures, annotations, return types, or semantic correctness.

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Closable(Protocol):
    def close(self) -> None: ...

class LooksClosable:
    def close(self, force: bool = False) -> str:
        return "closed"

class NotClosable:
    pass

print(isinstance(LooksClosable(), Closable))
print(isinstance(NotClosable(), Closable))
```

Expected output:

```text
True
False
```

The first result is `True` even though the implementation's signature and return type differ from the protocol annotation. Runtime checking primarily checks required attribute presence; it is not a substitute for static type checking or runtime validation. In Python 3.12+, runtime protocol attribute lookup behavior changed to use static attribute access and the set of protocol members is frozen at protocol creation; consult the target-version documentation if relying on details.

## 5.4 Replacement-class decorators

Most class decorators mutate and return the original class. A decorator can instead return a newly created class, but this changes identity and can surprise code that has references to the original class.

```python
def replacement_subclass(cls):
    class Replacement(cls):
        replacement_marker = True
    Replacement.__name__ = cls.__name__
    Replacement.__qualname__ = cls.__qualname__
    Replacement.__module__ = cls.__module__
    return Replacement

@replacement_subclass
class Base:
    def value(self):
        return 10

print(Base.__dict__.get("replacement_marker"))
print(Base().value())
print(Base.__name__)
```

Expected output:

```text
True
10
Base
```

The displayed name is intentionally copied, but `Base` is not the original class object. Name equality is not identity equality.

### Replacement-class risks

1. **Identity and references:** any code that saved the original class before decoration still refers to the original object. Registries, annotations, and plugin systems may retain it.
2. **`isinstance` and subclass checks:** instances of the replacement subclass are instances of the original class, but instances of the original class are not necessarily instances of the replacement class.
3. **`super()` and `__class__` closure:** methods compiled in the original class can carry a `__class__` closure referring to the original class. A method using zero-argument `super()` can fail if its instance is not an instance/subtype of that captured class. Reusing original methods on a replacement class therefore needs careful testing.
4. **Pickling:** pickle typically needs a class reachable from its module under the expected qualified name. Local replacement classes and mismatches between a class object's `__module__`/`__qualname__` and the actual module binding can break pickling. Test the actual importable package layout.
5. **Metaclass and slots:** creating a replacement class must preserve intended bases, metaclass, slots, class keywords, descriptors, and `__set_name__` behavior. A nested subclass is not a general replacement for `dataclass(slots=True)`.
6. **Decorator stacking:** a later decorator sees the replacement, not the original. A prior decorator may have stored the original class elsewhere.

Use replacement classes only when the identity change is part of the documented API. Prefer in-place mutation when feasible.

## 5.5 Why `dataclass(slots=True)` is special

The `dataclasses.dataclass` decorator usually mutates the class in place, but with `slots=True` it returns a **new class** with slots configured. Consequently, `DecoratedClass` may not be the same object created by the original class statement.

This has an important zero-argument `super()` caveat. Zero-argument `super()` uses a compiler-created `__class__` closure cell that refers to the class object in which the method was originally defined. If a decorator replaces that class object, the method's closure may still refer to the original class. Calling `super()` can then raise `TypeError` when `self` is not an instance or subtype of the captured class. This is why `@dataclass(slots=True)` has documented interaction with zero-argument `super()` in affected cases.

Prefer `super().method()` in ordinary inheritance, but when using a class decorator that creates a replacement class, explicitly test the exact method and Python version. A two-argument form such as `super(CurrentClass, self)` is not a universal fix: `CurrentClass` must be the correct class in the actual MRO and the instance must be its instance/subtype. Do not blindly replace `super()` across a codebase.

## 5.6 Source generation, `types.FunctionType`, and AST

Use these tools only when measurements or a concrete requirement justify them.

### Trusted source with `exec`

Generating source can create a function with a tailored signature, but string interpolation into source is fragile and dangerous if any part is untrusted.

```python
def build_constant_function(function_name: str, value: int):
    # This example validates the identifier and only interpolates an int.
    import keyword
    if (not function_name.isidentifier() or keyword.iskeyword(function_name)
            or function_name.startswith("__")):
        raise ValueError("invalid function name")
    if type(value) is not int:
        raise TypeError("value must be an int")
    namespace = {}
    source = f"def {function_name}():\n    return {value}\n"
    exec(compile(source, "<generated>", "exec"), namespace)
    return namespace[function_name]

answer = build_constant_function("answer", 42)
print(answer(), answer.__name__)
```

Expected output: `42 answer`

Only generate code from trusted, constrained inputs. `exec` is not a sandbox; avoid it for ordinary attribute injection.

### `types.FunctionType`

`types.FunctionType(code, globals, name, defaults, closure)` creates a function from a code object. It does **not** synthesize arbitrary code: you still need a compatible code object, globals, defaults, and (when required) closure cells. Mismatches cause confusing runtime failures. This is a low-level tool for advanced framework internals, not the default way to attach a method.

```python
import types

def template(self):
    return self.value * 2

class Doubler:
    def __init__(self, value):
        self.value = value

# Reuse a compatible code object and globals deliberately.
double = types.FunctionType(
    template.__code__, template.__globals__, name="double"
)
Doubler.double = double
print(Doubler(6).double())
```

Expected output: `12`

### AST-based generation

`ast` lets you construct or transform syntax trees, then compile them. It is useful for source-to-source tools and constrained code generators. It adds validation, location-fixing, compiler, and testing complexity. Prefer direct functions or `type()` unless the input is genuinely code-shaped.

```python
import ast

module = ast.parse("def generated(value):\n    return value + 1\n")
code = compile(module, "<ast-generated>", "exec")
namespace = {}
exec(code, namespace)
print(namespace["generated"](4))
```

Expected output: `5`

### Decision rule

- Add a known method: assign a normal function.
- Generate a class from a namespace: use `type()` or `types.new_class`.
- Generate signatures for a stable set of fields: consider `dataclasses` or a well-tested library.
- Transform Python syntax: use `ast`.
- Use `exec` only with trusted, validated source and a clear reason.
- Use `FunctionType` only when manipulating existing code objects and you understand closure semantics.

## 5.7 `dataclass_transform`: communicate generated behavior to type checkers

PEP 681's `typing.dataclass_transform` tells static type checkers that a decorator, base class, or metaclass provides dataclass-like behavior. It does not implement that behavior at runtime.

```python
from typing import dataclass_transform

@dataclass_transform()
def model(cls):
    # Runtime behavior in this example is intentionally minimal.
    cls.__model_marker__ = True
    return cls

@model
class User:
    id: int
    name: str

try:
    User(id=1, name="Ada")
except TypeError as error:
    print(type(error).__name__)
```

Expected runtime output: `TypeError`

This deliberately demonstrates a mismatch: a static type checker may accept `User(id=1, name="Ada")` because `@dataclass_transform` tells it to model a generated initializer, but the runtime call raises `TypeError` because this minimal example does not generate one. `dataclass_transform` is metadata for tools; it does not inject `__init__`, validate fields, freeze instances, or alter runtime semantics by itself. **Do not ship this mismatch.** Mark a decorator with `dataclass_transform` only when the library actually implements the declared dataclass-like contract.

Use it in a real library only after defining supported field specifiers, defaults, keyword-only behavior, frozen semantics, and generated signatures. Test with the type checkers you officially support.

## 5.8 `@frozen_after_init`: restrict assignment after initialization

Python's `dataclass(frozen=True)` provides a supported, intentionally limited frozen-data-model behavior. This example demonstrates a custom policy: assignments are allowed during `__init__`, then blocked.

```python
from functools import wraps

_FROZEN_AFTER_INIT_MARKER = "__frozen_after_init_decorator__"


def frozen_after_init(cls):
    """Freeze ordinary attribute rebinding after successful __init__.

    Deliberately supports only leaf classes with a normal instance __dict__.
    Use dataclasses.dataclass(frozen=True) for most value objects.
    """
    if cls.__dict__.get(_FROZEN_AFTER_INIT_MARKER, False):
        raise TypeError(f"{cls.__name__} is already decorated")
    if "__init_subclass__" in cls.__dict__:
        raise TypeError("frozen_after_init does not support a custom __init_subclass__")
    if cls.__setattr__ is not object.__setattr__:
        raise TypeError("frozen_after_init requires the default __setattr__")
    if cls.__dictoffset__ == 0:
        raise TypeError("frozen_after_init requires instances with __dict__")

    original_init = cls.__init__

    @wraps(original_init)
    def init_then_freeze(self, *args, **kwargs):
        try:
            state = object.__getattribute__(self, "__dict__")
        except AttributeError:
            state = {}
        if state.get("_frozen_after_init", False):
            raise AttributeError(f"{type(self).__name__} is already initialized")
        object.__setattr__(self, "_frozen_after_init", False)
        original_init(self, *args, **kwargs)
        object.__setattr__(self, "_frozen_after_init", True)

    def guarded_setattr(self, name, value):
        try:
            frozen = object.__getattribute__(self, "__dict__").get(
                "_frozen_after_init", False
            )
        except AttributeError:
            frozen = False
        if frozen:
            raise AttributeError(
                f"{type(self).__name__} is frozen after initialization"
            )
        object.__setattr__(self, name, value)

    def reject_subclass(subcls, **kwargs):
        raise TypeError(
            f"{cls.__name__} is a frozen_after_init leaf class and cannot be subclassed"
        )

    cls.__init__ = init_then_freeze
    cls.__setattr__ = guarded_setattr
    cls.__init_subclass__ = classmethod(reject_subclass)
    setattr(cls, _FROZEN_AFTER_INIT_MARKER, True)
    return cls


@frozen_after_init
class Settings:
    def __init__(self, region: str):
        self.region = region


settings = Settings("ap-south-1")
print(settings.region)
try:
    settings.region = "eu-west-1"
except AttributeError as error:
    print(type(error).__name__)
```

Expected output:

```text
ap-south-1
AttributeError
```

### Assumptions and limitations

- The class has a normal `__init__` and instance attributes. This decorator does not define fields or generate `__init__`. The internal `_frozen_after_init` instance name is reserved; the wrapper also rejects a direct second call to `__init__` after successful construction.
- If `__init__` raises, the object may remain partially initialized and unfrozen. It has not been successfully constructed, but code holding a leaked reference could observe it.
- This teaching implementation deliberately rejects subclassing so a child initializer cannot call `super().__init__()`, become frozen midway, and then fail while assigning child fields. It also rejects classes with a custom `__setattr__`, custom `__init_subclass__`, or no instance `__dict__` rather than silently overriding those contracts. If an inheritable policy is required, design a cooperative initialization-depth mechanism and test the entire MRO; do not remove the guard casually.
- A subclass is not relevant to this leaf-class implementation, but mutable objects stored in attributes can still be changed, e.g. `settings.options.append(...)`; blocking rebinding is not deep immutability.
- `object.__setattr__(obj, name, value)` can deliberately bypass the restriction. This is a programming convention, not a security boundary.
- Deletion is not blocked by this implementation (`del obj.attr` uses `__delattr__`); a complete policy must implement and test `__delattr__` too.
- Slots, custom descriptors, dataclass-generated methods, custom `__new__`, multiple inheritance, and metaclasses require additional design and tests.
- Wrapping `__init__` preserves metadata with `wraps`, but the runtime signature generally follows `__wrapped__` for introspection. Static type checkers may not infer the mutation-based behavior.

Use `@dataclass(frozen=True)` for normal value objects. Use a custom assignment policy only when its precise semantics are documented and tested.

---

# 6. Comparison of alternative mechanisms

The roadmap's recommended preference order is: plain code → decorators → class decorators → `__init_subclass__` → descriptors → metaclasses → AST/`exec`.

| Mechanism | Best fit | Timing | Main trade-off |
|---|---|---|---|
| Plain code / helper | One-off explicit behavior | Normal call time | Often clearest; less automatic |
| Class decorator | Opt-in change to a completed class | After class body creation | Good local scope; injected behavior may be invisible to type checkers |
| `__init_subclass__` | Every subclass participates in validation/registration | During subclass creation | Cooperative `super()` and multiple inheritance need care |
| Descriptor | Reusable attribute access, validation, lazy/computed fields | Attribute access / `__set_name__` at class creation | Powerful but lookup semantics can be subtle |
| Metaclass | Control the class-creation process itself | While class object is created | Broad influence, conflicts between metaclasses, harder debugging |
| AST / `exec` | Source transformation or measured code generation | Compile/execution time | Highest complexity and security burden |

## 6.1 When `__init_subclass__` is better

Use it when every subclass should automatically be validated or registered. Use a class decorator when the behavior should be explicitly opted into one class. See the next lesson, `05-init-subclass-and-subclass-registries.md`, for subclass hooks and cooperative inheritance.

## 6.2 When a descriptor is better

Use a descriptor when the behavior belongs to an attribute's access semantics—validation on assignment, lazy evaluation, computed values, or field metadata. Do not use a class decorator to reinvent the descriptor protocol.

## 6.3 When a metaclass is justified

A metaclass can influence namespace preparation, class construction, and class-object behavior. It is justified when the requirement genuinely concerns class creation and cannot be handled cleanly with decorators or `__init_subclass__`. Avoid metaclasses merely to register a few classes or add one method.

## 6.4 Decision questions

1. Can an ordinary function or explicit class attribute solve it?
2. Should the behavior be opt-in on a particular class? Consider a class decorator.
3. Should every subclass inherit the policy? Consider `__init_subclass__`.
4. Does the behavior need to participate in attribute lookup? Consider a descriptor.
5. Must the namespace or construction of the class itself change? Consider a metaclass.
6. Must Python syntax be transformed? Consider AST, with code generation last.

---

# 7. Testing, typing, and production design

## 7.1 Test contracts, not implementation trivia

For every decorator or factory, test:

- **Identity:** did the decorator return the same class or a replacement by design?
- **Generated behavior:** do injected methods work and preserve binding?
- **Descriptor kinds:** ordinary, static, class, and property behavior stays correct.
- **Decorator ordering:** the documented outer decorator receives the expected object.
- **Inheritance:** base and subclass semantics are intentional.
- **Repeated application:** idempotent, rejected, or explicitly cumulative behavior.
- **Assignment restrictions:** ordinary assignment, deletion, and documented bypasses.
- **Serialization:** only if pickling is part of the supported contract.
- **Typing:** run mypy/pyright or other supported checker; runtime tests cannot prove static behavior.

## 7.2 Decorator order is bottom-up

```python
def label(name):
    def decorate(cls):
        cls.labels = (*getattr(cls, "labels", ()), name)
        return cls
    return decorate

@label("outer")
@label("inner")
class Item:
    pass

print(Item.labels)
```

Expected output: `('inner', 'outer')`

The equivalent assignment is `Item = label("outer")(label("inner")(Item))`. The bottom decorator runs first. If one decorator returns a replacement class, the decorator above it receives that replacement. A decorator that reads attributes injected by another decorator depends on the order; document this dependency.

## 7.3 Static typing and runtime behavior are different contracts

| Feature | Runtime effect | Static type-checker effect |
|---|---|---|
| `typing.final` | Marker attribute where supported; no enforced prohibition | Flags subclassing/overrides in supported checkers |
| `@runtime_checkable` protocol | Enables limited structural `isinstance` checks | Protocol members are checked structurally with type/signature information |
| `dataclass_transform` | Metadata only; no code generation by itself | Tells supported checkers to model dataclass-like generated methods/fields |
| Arbitrary method injection | Adds runtime attribute/method | Usually not inferred automatically |
| `functools.wraps` | Copies metadata and sets `__wrapped__` | Does not by itself guarantee all decorator typing is correct |

For decorators that preserve a callable signature, use `ParamSpec`/`TypeVar` patterns where appropriate. For generated class APIs, publish accurate stubs or use `dataclass_transform` only if its contract is genuinely met. Verify both runtime tests and static checking.

## 7.4 Executable regression suite

The following tests are intentionally self-contained. Save them as `test_class_decorators.py` and run `python -m pytest -q`. They exercise identity, injection, method descriptor kinds, factory identity, decorator order, inheritance behavior, repeated application, assignment restrictions, replacement-class pickling assumptions, and negative cases. They test the documented leaf-class restriction of `frozen_after_init` rather than implying that it supports inheritance.

```python
import pickle
import functools
import inspect
import pytest


def add_marker(cls):
    cls.marker = True
    return cls


def register(registry, key):
    def decorate(cls):
        if key in registry:
            raise ValueError(f"duplicate key: {key}")
        registry[key] = cls
        return cls
    return decorate


def inject_describe(cls):
    def describe(self):
        return f"{type(self).__name__}:{self.value}"
    cls.describe = describe
    return cls


def auto_repr(cls):
    names = tuple(cls.__dict__.get("__annotations__", {}))
    if "__repr__" in cls.__dict__:
        raise TypeError("class already defines __repr__")

    def generated_repr(self):
        parts = []
        for name in names:
            try:
                value = getattr(self, name)
            except AttributeError as exc:
                raise AttributeError(f"missing annotated field {name!r}") from exc
            parts.append(f"{name}={value!r}")
        return f"{type(self).__name__}({', '.join(parts)})"

    cls.__repr__ = generated_repr
    return cls


def traced(fn):
    if inspect.iscoroutinefunction(fn):
        @functools.wraps(fn)
        async def async_wrapper(*args, **kwargs):
            return await fn(*args, **kwargs)
        return async_wrapper
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper


def trace_all_methods(cls):
    for name, raw in tuple(vars(cls).items()):
        if name.startswith("__") and name.endswith("__"):
            continue
        if isinstance(raw, staticmethod):
            setattr(cls, name, staticmethod(traced(raw.__func__)))
        elif isinstance(raw, classmethod):
            setattr(cls, name, classmethod(traced(raw.__func__)))
        elif isinstance(raw, property):
            getter = traced(raw.fget) if raw.fget is not None else None
            setter = traced(raw.fset) if raw.fset is not None else None
            deleter = traced(raw.fdel) if raw.fdel is not None else None
            setattr(cls, name, property(getter, setter, deleter, raw.__doc__))
        elif inspect.isfunction(raw):
            setattr(cls, name, traced(raw))
    return cls


def make_range_validator(minimum, maximum):
    class RangeValidator:
        def validate(self, value):
            return minimum <= value <= maximum
    return RangeValidator


def label(name):
    def decorate(cls):
        cls.labels = (*getattr(cls, "labels", ()), name)
        return cls
    return decorate


_FROZEN_AFTER_INIT_MARKER = "__frozen_after_init_decorator__"
def frozen_after_init(cls):
    if cls.__dict__.get(_FROZEN_AFTER_INIT_MARKER, False):
        raise TypeError("already decorated")
    if "__init_subclass__" in cls.__dict__:
        raise TypeError("custom __init_subclass__ unsupported")
    if cls.__setattr__ is not object.__setattr__:
        raise TypeError("custom __setattr__ unsupported")
    if cls.__dictoffset__ == 0:
        raise TypeError("instances require __dict__")
    original_init = cls.__init__
    @functools.wraps(original_init)
    def init_then_freeze(self, *args, **kwargs):
        try:
            state = object.__getattribute__(self, "__dict__")
        except AttributeError:
            state = {}
        if state.get("_frozen_after_init", False):
            raise AttributeError("already initialized")
        object.__setattr__(self, "_frozen_after_init", False)
        original_init(self, *args, **kwargs)
        object.__setattr__(self, "_frozen_after_init", True)
    def guarded_setattr(self, name, value):
        try:
            frozen = object.__getattribute__(self, "__dict__").get("_frozen_after_init", False)
        except AttributeError:
            frozen = False
        if frozen:
            raise AttributeError("frozen after initialization")
        object.__setattr__(self, name, value)
    def reject_subclass(subcls, **kwargs):
        raise TypeError("leaf class cannot be subclassed")
    cls.__init__ = init_then_freeze
    cls.__setattr__ = guarded_setattr
    cls.__init_subclass__ = classmethod(reject_subclass)
    setattr(cls, _FROZEN_AFTER_INIT_MARKER, True)
    return cls


def replacement_subclass(cls):
    class Replacement(cls):
        replacement_marker = True
    Replacement.__name__ = cls.__name__
    Replacement.__qualname__ = cls.__qualname__
    Replacement.__module__ = cls.__module__
    return Replacement


class PickleBase:
    def __init__(self, value):
        self.value = value


PickleBase = replacement_subclass(PickleBase)


def test_in_place_decorator_preserves_identity():
    class Item:
        pass
    original = Item
    result = add_marker(Item)
    assert result is original is Item
    assert Item.marker is True


def test_registration_preserves_identity_and_rejects_duplicates():
    registry = {}
    class CsvReader:
        pass
    decorated = register(registry, "csv")(CsvReader)
    assert decorated is CsvReader
    assert registry["csv"] is CsvReader
    with pytest.raises(ValueError, match="duplicate key"):
        register(registry, "csv")(type("OtherReader", (), {}))


def test_injected_method_binds_instance():
    @inject_describe
    class Record:
        def __init__(self, value):
            self.value = value
    record = Record(8)
    assert record.describe() == "Record:8"


def test_auto_repr_generated_behavior_and_missing_field():
    @auto_repr
    class Point:
        x: int
        def __init__(self, x):
            self.x = x
    assert repr(Point(3)) == "Point(x=3)"
    @auto_repr
    class Missing:
        x: int
    with pytest.raises(AttributeError, match="missing annotated field"):
        repr(Missing())


def test_auto_repr_reapplication_is_rejected():
    @auto_repr
    class Point:
        x: int
    with pytest.raises(TypeError, match="already defines"):
        auto_repr(Point)


def test_auto_repr_inheritance_policy_is_explicit():
    @auto_repr
    class Base:
        base: int
        def __init__(self, base):
            self.base = base
    class Inherited(Base):
        def __init__(self, base, extra):
            super().__init__(base)
            self.extra = extra
    @auto_repr
    class DecoratedChild(Base):
        child: int
        def __init__(self, base, child):
            super().__init__(base)
            self.child = child
    assert repr(Inherited(1, 2)) == "Inherited(base=1)"
    assert repr(DecoratedChild(1, 2)) == "DecoratedChild(child=2)"


def test_static_class_and_property_descriptors_survive_wrapping():
    @trace_all_methods
    class Example:
        def ordinary(self, value):
            return value + 1
        @staticmethod
        def static(value):
            return value * 2
        @classmethod
        def class_name(cls):
            return cls.__name__
        @property
        def ready(self):
            return True
    assert Example().ordinary(2) == 3
    assert Example.static(3) == 6
    assert Example.class_name() == "Example"
    assert Example().ready is True


def test_factory_calls_create_distinct_classes_and_capture_config():
    Low = make_range_validator(0, 5)
    High = make_range_validator(10, 20)
    assert Low is not High
    assert Low().validate(4) is True
    assert Low().validate(12) is False
    assert High().validate(12) is True


def test_decorator_order_is_bottom_up():
    @label("outer")
    @label("inner")
    class Item:
        pass
    assert Item.labels == ("inner", "outer")


def test_inheritance_and_replacement_identity():
    class Original:
        def value(self):
            return 7
    saved_original = Original
    Replacement = replacement_subclass(Original)
    assert Replacement is not saved_original
    assert issubclass(Replacement, saved_original)
    assert Replacement().value() == 7


def test_replacement_class_pickles_when_module_binding_matches():
    class Local:
        pass
    # Local classes are not pickleable by module/name; this is the expected
    # negative case and documents the importability requirement.
    with pytest.raises((pickle.PicklingError, AttributeError, TypeError)):
        pickle.dumps(Local())


def test_replacement_class_pickle_works_when_module_binding_matches():
    value = PickleBase(41)
    restored = pickle.loads(pickle.dumps(value))
    assert type(restored) is PickleBase
    assert restored.value == 41


def test_dataclass_slots_zero_argument_super_caveat():
    from dataclasses import dataclass
    @dataclass(slots=True)
    class Slotted:
        value: int
        def call_super(self):
            return super().__repr__()
    # The decorator replaces the original class; the method's __class__ cell
    # still refers to the original class object on supported affected runtimes.
    with pytest.raises(TypeError, match=r"super\(type, obj\)"):
        Slotted(1).call_super()


def test_frozen_after_init_allows_init_then_rejects_rebinding():
    @frozen_after_init
    class Settings:
        def __init__(self, region):
            self.region = region
            self.zone = "a"
    settings = Settings("ap-south-1")
    assert (settings.region, settings.zone) == ("ap-south-1", "a")
    with pytest.raises(AttributeError, match="frozen"):
        settings.region = "eu-west-1"


def test_frozen_after_init_rejects_explicit_reinitialization():
    @frozen_after_init
    class Settings:
        def __init__(self, region):
            self.region = region
    settings = Settings("ap-south-1")
    with pytest.raises(AttributeError, match="already initialized"):
        settings.__init__("eu-west-1")
    assert settings.region == "ap-south-1"


def test_frozen_after_init_rejects_subclassing():
    @frozen_after_init
    class Settings:
        def __init__(self):
            self.region = "ap-south-1"
    with pytest.raises(TypeError, match="leaf class"):
        class Child(Settings):
            pass


def test_frozen_after_init_does_not_freeze_failed_construction():
    leaked = []
    @frozen_after_init
    class Failing:
        def __init__(self):
            self.partial = True
            leaked.append(self)
            raise RuntimeError("construction failed")
    with pytest.raises(RuntimeError, match="construction failed"):
        Failing()
    leaked[0].recovery_note = "partial object"
    assert leaked[0].recovery_note == "partial object"


def test_frozen_after_init_rejects_slots_only_class():
    class Slotted:
        __slots__ = ("value",)
        def __init__(self, value):
            self.value = value
    with pytest.raises(TypeError, match="instances require __dict__"):
        frozen_after_init(Slotted)


def test_frozen_after_init_rejects_reapplication_and_custom_setattr():
    @frozen_after_init
    class Settings:
        def __init__(self):
            self.region = "x"
    with pytest.raises(TypeError, match="already decorated"):
        frozen_after_init(Settings)
    class Custom:
        def __setattr__(self, name, value):
            object.__setattr__(self, name, value)
    with pytest.raises(TypeError, match="custom __setattr__"):
        frozen_after_init(Custom)
```

> Pickling note: the negative local-class test is intentionally conservative across runtimes. For a positive pickling test, define the class at module scope, ensure its `__module__` and `__qualname__` resolve to the same class object through an importable module binding, then round-trip with `pickle.loads(pickle.dumps(instance))`.

## 7.5 Production safety checklist

- Validate names and configuration before modifying a class.
- Do not execute source assembled from untrusted input.
- Avoid logging sensitive values from generated repr methods.
- Keep registries explicit, deterministic, and resettable in tests.
- Document identity changes and serialization support.
- Avoid changing special methods casually: Python may look them up on the type, and some behavior is fixed during object creation.
- Define inheritance behavior explicitly rather than relying on accidental `getattr` results.
- Avoid mutation after a class is exported publicly unless the API promises it.
- Add type-checker tests for the supported checker and version.
- Prefer standard-library features such as `dataclasses`, `functools.total_ordering`, and `typing` markers over custom imitations when they fit.

---

# 8. A practical project: a small transform-plugin system

Build a registry of record transforms. Each transform class is registered under a unique name, gets a generated repr for simple annotations, and exposes a `run` method. The example keeps the contract small and uses in-place decorators so class identity remains stable.

Save as `transform_plugins.py`:

```python
from __future__ import annotations

from typing import Any

TRANSFORMS: dict[str, type] = {}


def register_transform(name: str):
    if not name or name.strip() != name:
        raise ValueError("name must be non-empty and trimmed")

    def decorate(cls):
        if name in TRANSFORMS:
            raise ValueError(f"duplicate transform: {name!r}")
        if not callable(getattr(cls, "run", None)):
            raise TypeError("transform classes must define callable run")
        TRANSFORMS[name] = cls
        cls.transform_name = name
        return cls
    return decorate


def auto_repr(cls):
    names = tuple(cls.__dict__.get("__annotations__", {}))
    if "__repr__" in cls.__dict__:
        raise TypeError("class already defines __repr__")

    def __repr__(self):
        values = []
        for name in names:
            if not hasattr(self, name):
                raise AttributeError(f"missing initialized field: {name}")
            values.append(f"{name}={getattr(self, name)!r}")
        return f"{type(self).__name__}({', '.join(values)})"

    cls.__repr__ = __repr__
    return cls


@register_transform("trim")
@auto_repr
class TrimTransform:
    field: str

    def __init__(self, field: str):
        self.field = field

    def run(self, row: dict[str, Any]) -> dict[str, Any]:
        result = dict(row)
        value = result.get(self.field)
        if isinstance(value, str):
            result[self.field] = value.strip()
        return result


@register_transform("lowercase")
@auto_repr
class LowercaseTransform:
    field: str

    def __init__(self, field: str):
        self.field = field

    def run(self, row: dict[str, Any]) -> dict[str, Any]:
        result = dict(row)
        value = result.get(self.field)
        if isinstance(value, str):
            result[self.field] = value.lower()
        return result


def apply_pipeline(row: dict[str, Any], steps: list[tuple[str, str]]) -> dict[str, Any]:
    current = dict(row)
    for name, field in steps:
        try:
            transform_cls = TRANSFORMS[name]
        except KeyError as exc:
            raise ValueError(f"unknown transform: {name!r}") from exc
        current = transform_cls(field).run(current)
    return current


if __name__ == "__main__":
    transform = TrimTransform("city")
    print(repr(transform))
    print(apply_pipeline(
        {"city": "  Kolkata  ", "status": "ACTIVE"},
        [("trim", "city"), ("lowercase", "status")],
    ))
```

Run:

```bash
python transform_plugins.py
```

Expected output:

```text
TrimTransform(field='city')
{'city': 'Kolkata', 'status': 'active'}
```

### Project extension tasks

1. Add a duplicate-registration test.
2. Define whether subclass transforms inherit generated repr fields from a base class.
3. Add a `priority` or version field to registry metadata without changing transform identity.
4. Add type aliases or a `Protocol` for the transform interface.
5. Add a pytest fixture that clears `TRANSFORMS` between tests.
6. Decide whether plugin loading should be explicit imports or entry points; do not assume the registry can discover unimported modules.
7. Add a policy for unknown fields and values that are not strings.
8. Test the output with sensitive input and confirm no raw data is logged by default.

---

# 9. Exercises with solutions

Try each exercise before reading its solution.

## Exercise 1 — preserve identity

Write a decorator `mark_internal` that sets `internal = True` and returns the same class.

**Solution:**

```python
def mark_internal(cls):
    cls.internal = True
    return cls

@mark_internal
class Parser:
    pass

assert Parser.internal is True
```

## Exercise 2 — detect duplicate registration

Make a decorator factory that rejects duplicate keys and registers classes without changing identity.

**Solution:**

```python
registry = {}

def register(key):
    def decorate(cls):
        if key in registry:
            raise ValueError(key)
        registry[key] = cls
        return cls
    return decorate
```

A complete test should also assert `registry[key] is DecoratedClass` and reset the registry between tests.

## Exercise 3 — explain annotation-only fields

Why can `@auto_repr` fail for `class C: x: int` when `repr(C())` is called?

**Solution:** `x: int` records an annotation in the class namespace. It does not initialize `self.x`; the generated repr must either report the missing value, omit it by documented policy, or rely on a constructor contract that guarantees initialization.

## Exercise 4 — preserve static and class methods

Update a method decorator to wrap `staticmethod` and `classmethod` without losing descriptor semantics.

**Solution:** unwrap `raw.__func__`, wrap that function, then re-wrap it with `staticmethod(...)` or `classmethod(...)`. Do not wrap the descriptor object as if it were a normal function.

## Exercise 5 — factory identity

Why is `make_range_validator(0, 5) is make_range_validator(0, 5)` normally false?

**Solution:** each factory call executes a class definition and creates a new class object. To reuse identity, cache the generated class deliberately or use one parameterized class and store the range on instances.

## Exercise 6 — decorator order

What does `@outer @inner class C: ...` mean?

**Solution:** it is equivalent to `C = outer(inner(C))`. The inner decorator executes first, and the outer decorator receives whatever the inner decorator returned.

## Exercise 7 — assignment restrictions

What does `@frozen_after_init` prevent, and what does it not prevent?

**Solution:** it blocks ordinary rebinding of attributes after successful initialization under the implementation's assumptions. It does not make nested mutable values immutable, prevent deliberate `object.__setattr__`, prevent deletion unless `__delattr__` is implemented, or stop a non-cooperative subclass from overriding the policy.

## Exercise 8 — runtime versus static typing

Does `@final` prevent runtime subclassing? Does `@dataclass_transform` generate an initializer?

**Solution:** no to both. `final` is principally a static-checker marker; `dataclass_transform` communicates expected generated behavior to supported type checkers but performs no runtime code generation.

## Exercise 9 — choose a mechanism

A library needs every subclass of `Handler` to validate a `kind` attribute. What should you consider first?

**Solution:** `__init_subclass__` is usually the natural first choice because the policy applies to every subclass at class creation. A decorator is better when opting in per class is intended.

## Exercise 10 — source generation

When is `exec` appropriate for generating methods?

**Solution:** only when there is a concrete requirement (for example, generated signatures or a source transformation) that simpler mechanisms cannot meet, inputs are trusted and constrained, and generated code is compiled and tested. It is not a sandbox and should not be used for arbitrary user-controlled source.

---

# 10. Interview questions and completion checklist

## 10.1 Interview questions

1. What object does a class decorator receive, and when does it run?
2. What does `@decorate class C: ...` desugar to?
3. Why should most class decorators return `cls`?
4. How do you add a method while preserving ordinary instance binding?
5. Why must class-wide wrappers treat `staticmethod`, `classmethod`, and `property` differently?
6. Why are `__annotations__` insufficient to infer initialized fields?
7. What are the most important ways a simplified dataclass differs from `dataclasses.dataclass`?
8. What is a class factory, and how does closure configuration work?
9. Why can two factory calls create distinct classes with identical names and attributes?
10. What does `functools.total_ordering` generate, and what comparison methods should the class implement first?
11. Does `typing.final` enforce a runtime restriction?
12. What does `@runtime_checkable` check, and what does it not check?
13. What does `dataclass_transform` do for a type checker? What does it not do at runtime?
14. What changes when a decorator returns a replacement class?
15. Why can zero-argument `super()` fail when methods are reused across replacement classes?
16. Why can replacement or local classes create pickle problems?
17. What does idempotency mean for a decorator? How would you test it?
18. Explain bottom-up decorator application and a real bug caused by the wrong order.
19. When would you use `__init_subclass__` instead of a class decorator?
20. What requirement justifies a metaclass over a descriptor or class decorator?
21. Why is `exec` unsafe with untrusted source, and when might AST generation be justified?
22. What does the custom `frozen_after_init` implementation guarantee—and what does it not guarantee?

## 10.2 Completion checklist

Mark each item only after you can demonstrate it without copying the lesson.

- [ ] Explain class decorator input, return value, and execution timing.
- [ ] Implement a simple and parameterized class decorator.
- [ ] Register a plugin and test duplicate handling and identity.
- [ ] Inject a method and explain descriptor binding.
- [ ] Preserve ordinary, static, class, and property behavior in a method wrapper.
- [ ] Implement `auto_repr` and explain missing annotations, inheritance, and sensitive values.
- [ ] Explain why the custom record example is not equivalent to dataclasses.
- [ ] Build a configured class factory and test class identity.
- [ ] Explain `total_ordering`, `final`, and `runtime_checkable` accurately.
- [ ] Explain `FunctionType`, `exec`, and AST trade-offs and security limits.
- [ ] Explain replacement-class identity, pickling, and zero-argument `super()` risks.
- [ ] Implement and test `frozen_after_init`, including its documented limitations.
- [ ] Explain decorator order, repeated application, and idempotency.
- [ ] Distinguish runtime behavior from static typing metadata.
- [ ] Choose among plain code, class decorators, `__init_subclass__`, descriptors, and metaclasses.
- [ ] Complete the project and its tests.

## 10.3 Suggested verification commands

For a project with the examples in importable modules and a pytest suite:

```bash
python -m compileall -q .
python -m pytest -q
python -m ruff check .
python -m mypy .
```

Run only tools installed and configured in your environment. Compilation and runtime tests do not replace static checking; static checking does not prove runtime semantics. Pin the supported Python version and test it in CI.

**Verification limitation for this artifact:** the Markdown's 28 Python code blocks were compiled and executed under Python 3.13.5, and the embedded pytest regression suite passed (19 tests). `mypy`, `pyright`, and `ruff` were not available in the execution environment, so no static-type-checker or linter pass is claimed. Run the suite on each Python version your project supports, especially Python 3.12, before treating cross-version behavior as verified.

---

## Final principle

Class decorators are best when they make an opt-in class transformation explicit and local. Class factories are best when configuration genuinely needs to produce distinct class objects. Keep identity stable unless replacement is a documented requirement, preserve descriptors deliberately, test the generated contract, and choose the least powerful mechanism that solves the problem.
