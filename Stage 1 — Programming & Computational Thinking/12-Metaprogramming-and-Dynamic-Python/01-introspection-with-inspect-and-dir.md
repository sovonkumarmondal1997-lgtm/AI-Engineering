# Introspection with `inspect` and `dir()`

> **Stage 1 — Programming & Computational Thinking**  
> **Module 12 — Metaprogramming and Dynamic Python**  
> **Baseline:** Python 3.12+; version-sensitive notes call out Python 3.13 and 3.14.

## 1. Scope and learning objectives

Introspection means examining objects, their types, attributes, call signatures, annotations, source, and runtime state while a program is running. It is a foundation for debuggers, REPLs, documentation tools, test frameworks, plugin discovery, serializers, web frameworks, and dependency-injection (DI) containers.

This lesson teaches how to inspect objects without confusing a useful observation with a stable public contract. It covers:

- Class and object identity: `type`, `isinstance`, `issubclass`, `id`, and `callable`.
- Namespaces and attributes: `dir`, `vars`, `__dict__`, inherited attributes, `help`, docstrings, and naming metadata.
- Function/class metadata: code objects, defaults, annotations, MRO, bases, and subclasses.
- `inspect.signature`, `Parameter` kinds, `Signature.bind`, and `BoundArguments`.
- Member, predicate, source, and documentation inspection.
- Type-hint resolution, annotation evaluation changes, and forward references.
- Stack/frame inspection, static attribute lookup, descriptors, and operational risks.
- A small, explicit DI container based on signatures and type hints.

By the end, you should be able to choose the least risky introspection tool for a job, explain its limits, and test the behavior you rely on.

## 2. Prerequisites and environment setup

You should already understand functions and default arguments, classes and inheritance, descriptors/properties, type hints, exceptions, modules, and basic testing. The preceding object-model lessons are particularly relevant to method binding, the method resolution order (MRO), and descriptor lookup.

Check your interpreter:

```bash
python --version
python -c "import sys; print(sys.version)"
```

Use Python 3.12 or later for the baseline examples. Python 3.14 introduces important annotation semantics described later. The examples use only the standard library unless noted. Save examples in `.py` files and run them with `python file.py`; assertions are intended to be executable checks. Optional quality tools include `pytest`, `ruff`, and `mypy` or `pyright`.

**Working rule:** introspection of arbitrary objects is not automatically safe. An object's attribute hooks, descriptors, metaclass, or annotation expressions may execute code. Prefer static inspection where appropriate and inspect only objects you trust.

## 3. Beginner foundations

### 3.1 `type`, `isinstance`, `issubclass`, `id`, and `callable`

```python
class Animal:
    pass

class Dog(Animal):
    def bark(self) -> str:
        return "woof"

pet = Dog()
print(type(pet).__name__)              # Dog
print(isinstance(pet, Dog))            # True
print(isinstance(pet, Animal))         # True
print(issubclass(Dog, Animal))         # True
print(callable(pet))                   # False
print(callable(pet.bark))              # True
print(id(pet) == id(pet))              # True
```

- `type(x)` returns the object's actual type. For ordinary class checks, prefer `isinstance(x, SomeBase)` when subclasses should count.
- `isinstance(x, T)` supports inheritance and can also honor a class's customized instance-checking behavior. Some runtime-checkable protocols provide structural checks, but those checks do not validate full method signatures.
- `issubclass(C, B)` asks whether a class is a subclass of another class (or accepted tuple of classes). Passing a non-class where a class is required raises `TypeError`.
- `id(x)` is an identity token that is unique among simultaneously live objects. In CPython it is commonly the memory address, but code must not depend on that implementation detail. IDs can be reused after an object dies.
- `callable(x)` answers whether Python considers an object callable; it does not guarantee that calling it will succeed or return a particular type.

```python
assert type(3) is int
assert isinstance(True, int)  # bool is a subclass of int
assert not issubclass(int, str)
assert callable(lambda: None)
assert not callable(object())

try:
    issubclass(3, object)
except TypeError:
    pass
else:
    raise AssertionError("issubclass should reject a non-class first argument")
```

**Trade-off:** `type(x) is T` deliberately rejects subclasses. It is appropriate only when exact type identity is a real requirement, not as a default substitute for `isinstance`.

### 3.2 `dir`, `vars`, and `__dict__`

```python
class Parent:
    category = "parent"
    def describe(self) -> str:
        return "parent object"

class Child(Parent):
    kind = "child"
    def __init__(self, value: int) -> None:
        self.value = value

obj = Child(7)
print(vars(obj))                       # {'value': 7}
print(obj.__dict__)                    # {'value': 7}
print("describe" in dir(obj))         # True (inherited method)
print("category" in dir(obj))         # True (inherited class attribute)
print("value" in dir(obj))            # True (instance attribute)
print(Child.__dict__["kind"])         # 'child'
print(Child.__bases__)                 # (<class '__main__.Parent'>,)
```

- `dir(obj)` returns a list of names considered useful for interactive exploration. It often includes instance, class, and inherited names, and a class can customize it with `__dir__`. It is **not** a guaranteed stable API or a complete inventory of every possible dynamic attribute.
- `vars(obj)` is effectively access to `obj.__dict__` and raises `TypeError` if the object has no suitable `__dict__`. It does not return inherited attributes.
- `obj.__dict__`, when present, is the object's own attribute namespace. Classes also have a `__dict__`, generally exposed as a read-only mapping proxy. Objects with `__slots__` may lack an instance dictionary unless a slot or base class provides one.
- Class attributes are stored on classes, not copied into each instance's dictionary. Attribute lookup searches class bases according to the MRO.

```python
class Parent:
    def describe(self) -> str:
        return "parent object"

class Child(Parent):
    def __init__(self, value: int) -> None:
        self.value = value

obj = Child(7)
assert vars(obj) == {"value": 7}
assert "describe" not in vars(obj)
assert "describe" in dir(obj)

class Slotted:
    __slots__ = ("x",)
    def __init__(self) -> None:
        self.x = 1

s = Slotted()
assert s.x == 1
try:
    vars(s)
except TypeError:
    pass
else:
    raise AssertionError("slotted object has no __dict__ in this example")
```

Do not write tests that compare the entire `dir()` list. Assert only the specific name or behavior that matters.

### 3.3 `help`, docstrings, and name metadata

```python
class Report:
    """Represent a generated report."""
    def render(self, format: str = "text") -> str:
        """Render the report in the requested format."""
        return format

print(Report.__name__)                 # Report
print(Report.__module__)               # __main__ when run as a script
print(Report.__qualname__)             # Report
print(Report.__doc__)                  # Represent a generated report.
print(Report.render.__name__)          # render
print(Report.render.__qualname__)      # Report.render
```

- `__name__` is the object's short declared name for functions/classes/modules where applicable.
- `__module__` records the module name associated with the definition; generated or moved objects may need deliberate metadata handling.
- `__qualname__` gives a qualified name, including lexical nesting such as `Outer.Inner` or `factory.<locals>.Thing`. It is descriptive metadata, not a globally resolvable import path in every case.
- `__doc__` contains a docstring or `None`. `help(obj)` uses documentation and other introspection mechanisms to render help, usually through `pydoc`; it is interactive output, not a machine-stable serialization format.
- `inspect.getdoc()` can clean indentation and inherit documentation in some cases; `inspect.cleandoc()` removes common indentation from a docstring.

```python
import inspect

class Report:
    """Represent a generated report."""
    def render(self, format: str = "text") -> str:
        """Render the report in the requested format."""
        return format

raw = """
    A short description.
        An indented detail.
"""
print(inspect.cleandoc(raw))
print(inspect.getdoc(Report.render))
```

`help()` is intended primarily for interactive exploration. Run `help(Report.render)` in a REPL or script to display documentation and related metadata; avoid asserting its exact terminal formatting in automated tests.

For generated code and public libraries, write explicit docstrings and test meaningful metadata. Avoid assuming `__module__` is always `__main__` or that qualified names can be imported directly.

### 3.4 Function and class metadata

```python
def greet(name: str, punctuation: str = "!") -> str:
    """Return a greeting."""
    return f"Hello {name}{punctuation}"

print(greet.__name__)                  # greet
print(greet.__defaults__)              # ('!',)
print(greet.__annotations__)           # {'name': <class 'str'>, 'return': <class 'str'>}
print(greet.__code__.co_varnames[:greet.__code__.co_argcount])  # ('name', 'punctuation')
print(greet.__code__.co_argcount)      # 2
```

Important fields:

- `function.__defaults__`: tuple of positional parameter defaults, or `None`.
- `function.__kwdefaults__`: dictionary of keyword-only defaults, or `None`.
- `function.__annotations__`: annotation storage; its representation and evaluation timing are version-sensitive (see Section 5.3).
- `function.__code__`: a code object describing compiled function code. It is not the function's closure, globals, defaults, or complete runtime state.
- `Class.__mro__`: the linearized method resolution order used for inherited lookup.
- `Class.__bases__`: direct base classes.
- `Class.__subclasses__()`: currently live, direct subclasses known to the runtime, not all descendants and not a durable plugin registry.

```python
class Root: pass
class Left(Root): pass
class Right(Root): pass
class Leaf(Left): pass

print([c.__name__ for c in Leaf.__mro__])
# ['Leaf', 'Left', 'Root', 'object']
print([c.__name__ for c in Left.__bases__])
# ['Root']
assert Left in Root.__subclasses__()
assert Leaf not in Root.__subclasses__()  # direct subclasses only

def options(a, b=2, *, mode="safe"):
    return a, b, mode

assert options.__defaults__ == (2,)
assert options.__kwdefaults__ == {"mode": "safe"}
```

The exact order of `__subclasses__()` reflects runtime class creation and object lifetime. Use explicit registration or entry points for production plugin discovery.

## 4. Intermediate `inspect` techniques

### 4.1 `inspect.signature()` and parameter kinds

A function's call contract is often best represented by a `Signature` object rather than by manually decoding code-object fields.

```python
import inspect

def sample(pos_only, /, positional_or_keyword, *items,
           required_keyword, optional_keyword="x", **extras):
    """Show every standard parameter kind."""
    return pos_only, positional_or_keyword, items, required_keyword, optional_keyword, extras

sig = inspect.signature(sample)
for parameter in sig.parameters.values():
    print(parameter.name, parameter.kind.name, parameter.default)
```

The parameter kinds, in declaration order, are:

| Kind | Syntax | Meaning |
|---|---|---|
| `POSITIONAL_ONLY` | `x, /` | Must be passed positionally |
| `POSITIONAL_OR_KEYWORD` | `x` | Can be positional or keyword |
| `VAR_POSITIONAL` | `*args` | Collects extra positional arguments into a tuple |
| `KEYWORD_ONLY` | `*, x` | Must be passed by keyword |
| `VAR_KEYWORD` | `**kwargs` | Collects extra keyword arguments into a dict |

`Parameter.empty` marks an absent default or annotation. It is a sentinel, not the value `None`.

```python
import inspect

def sample(pos_only, /, positional_or_keyword, *items,
           required_keyword, optional_keyword="x", **extras):
    return pos_only, positional_or_keyword, items, required_keyword, optional_keyword, extras

sig = inspect.signature(sample)
params = sig.parameters
assert params["pos_only"].kind is inspect.Parameter.POSITIONAL_ONLY
assert params["items"].kind is inspect.Parameter.VAR_POSITIONAL
assert params["required_keyword"].kind is inspect.Parameter.KEYWORD_ONLY
assert params["extras"].kind is inspect.Parameter.VAR_KEYWORD
assert params["required_keyword"].default is inspect.Parameter.empty
assert params["optional_keyword"].default == "x"
```

`inspect.signature()` follows `__wrapped__` by default and may honor a callable's `__signature__`. Some built-ins and extension callables do not expose an inspectable signature; `TypeError` or `ValueError` can be raised. Do not assume every callable has a recoverable signature.

### 4.2 `Signature.bind()` and `BoundArguments`

`bind()` validates an argument set against a signature without executing the target function. It raises `TypeError` for missing required arguments, unexpected keywords, duplicate assignments, or invalid positional/keyword usage.

```python
import inspect

def create_user(name: str, active: bool = True, *, region: str) -> dict:
    return {"name": name, "active": active, "region": region}

signature = inspect.signature(create_user)
bound = signature.bind("Asha", region="ap-south-1")
print(bound.arguments)                 # {'name': 'Asha', 'region': 'ap-south-1'}
bound.apply_defaults()
print(bound.arguments)
# {'name': 'Asha', 'active': True, 'region': 'ap-south-1'}
print(bound.args)                      # ('Asha', True)
print(bound.kwargs)                    # {'region': 'ap-south-1'}
assert create_user(*bound.args, **bound.kwargs) == {
    "name": "Asha", "active": True, "region": "ap-south-1"
}
```

`BoundArguments.arguments` is an ordered mapping of supplied/bound values. Before `apply_defaults()`, omitted defaults are not necessarily present. `args` and `kwargs` provide a call-compatible representation. Binding does **not** enforce runtime types from annotations and does not run business validation.

```python
import inspect

def create_user(name: str, active: bool = True, *, region: str) -> dict:
    return {"name": name, "active": active, "region": region}

signature = inspect.signature(create_user)
for args, kwargs in [
    ((), {"region": "x"}),                 # missing name
    (("Asha",), {}),                        # missing region
    (("Asha",), {"region": "x", "oops": 1}),
    (("Asha",), {"name": "duplicate", "region": "x"}),
]:
    try:
        signature.bind(*args, **kwargs)
    except TypeError as exc:
        print(type(exc).__name__)
    else:
        raise AssertionError("invalid call unexpectedly bound")
```

### 4.3 Member discovery and predicates

```python
import inspect

class Service:
    def method(self):
        return "ok"

    @property
    def status(self):
        return "ready"

async def async_task():
    return 1

def generator():
    yield 1

assert inspect.isclass(Service)
assert inspect.isfunction(Service.method)
assert inspect.ismethod(Service().method)
assert inspect.iscoroutinefunction(async_task)
assert inspect.isgeneratorfunction(generator)

methods = inspect.getmembers(Service, inspect.isfunction)
print([name for name, _ in methods])
```

Useful predicates include `isclass`, `isfunction`, `ismethod`, `isbuiltin`, `ismodule`, `isroutine`, `isgeneratorfunction`, `isgenerator`, `iscoroutinefunction`, `iscoroutine`, `isasyncgenfunction`, `isasyncgen`, `isawaitable`, and `isdatadescriptor`.

`inspect.getmembers(obj, predicate=None)` returns sorted `(name, value)` pairs for members discoverable through normal attribute access. **It may invoke descriptors and custom attribute hooks.** For a class, retrieving members may bind descriptors differently from reading the raw class namespace. Use it with trusted objects; it is not a safe sandboxing tool.

### 4.4 Source and documentation inspection

```python
import inspect
import math

print(inspect.getdoc(math))
print(inspect.getsourcefile(inspect.signature))  # often a Python stdlib source path
```

Typical tools:

- `inspect.getsource(obj)` returns source text when available.
- `inspect.getsourcelines(obj)` returns source lines and the starting line number.
- `inspect.getsourcefile(obj)` tries to identify a Python source file.
- `inspect.getfile(obj)` identifies the defining file where supported.
- `inspect.getdoc(obj)` returns cleaned documentation or `None`.
- `inspect.cleandoc(text)` normalizes indentation.

Source retrieval can fail with `OSError` or `TypeError` when source is unavailable, for example for many built-ins, extension modules, dynamically generated functions, or interactive definitions. Source paths can be unavailable or misleading in frozen/packaged environments. Do not make production correctness depend on source being retrievable.

```python
def local_function():
    """Example function defined in this source file."""
    return 42

import inspect

try:
    source = inspect.getsource(local_function)
except (OSError, TypeError) as exc:
    print(f"Source unavailable: {exc}")
else:
    print(source)

try:
    inspect.getsource(len)  # usually unavailable for a built-in
except (OSError, TypeError):
    print("Built-in source is not available through inspect.getsource")
```

### 4.5 `typing.get_type_hints()` versus `__annotations__`

Annotations are metadata, not automatic runtime validation. Reading `__annotations__` directly may expose strings or unresolved references, may omit inherited context, and is affected by Python version and annotation semantics.

```python
from __future__ import annotations
from typing import get_type_hints

class Node:
    next: Node | None
    value: int

def transform(value: Node) -> list[Node]:
    return [value]

print(transform.__annotations__)       # with future import, commonly strings
hints = get_type_hints(transform)
print(hints)                            # resolved runtime objects
assert hints["return"] == list[Node]
assert get_type_hints(Node)["next"] == Node | None

def unresolved(value: "MissingType") -> None:
    pass

try:
    get_type_hints(unresolved)
except NameError:
    pass  # Expected: the forward reference is not defined in this module.
else:
    raise AssertionError("an unresolved annotation should not resolve silently")
```

`typing.get_type_hints(obj, globalns=None, localns=None, include_extras=False)` attempts to resolve forward references and string annotations in the appropriate namespace. It can raise exceptions if names are missing or evaluation fails. Annotation resolution can evaluate expressions; only use it on trusted definitions. `include_extras=True` preserves metadata such as `Annotated` extras.

When annotation metadata is absent, an annotation can be `None`, an empty mapping, or lack the expected key. Handle missing keys explicitly instead of assuming every parameter has a hint.

## 5. Advanced introspection

### 5.1 Static lookup with `inspect.getattr_static()`

Normal attribute lookup can execute user-defined behavior. `getattr(obj, name)` can invoke `__getattribute__`, `__getattr__`, a property getter, or another descriptor's `__get__`. `hasattr()` also performs normal lookup and suppresses `AttributeError`; it is not a side-effect-free existence check.

```python
import inspect

class Sensor:
    @property
    def reading(self):
        print("PROPERTY EXECUTED")
        return 21

sensor = Sensor()
print(getattr(sensor, "reading"))
# prints PROPERTY EXECUTED, then 21
raw = inspect.getattr_static(sensor, "reading")
print(type(raw).__name__)              # property
assert isinstance(raw, property)
```

`getattr_static(obj, name[, default])` attempts to retrieve the attribute without invoking the descriptor protocol, `__getattr__`, or `__getattribute__` in the usual way. It may return the raw descriptor rather than the value that normal access would return. It can also fail to find dynamically synthesized attributes. It is safer for inspecting many objects, but it is **not** a complete security boundary: the object may already be malicious, and other operations can execute code.

Use this pattern when examining a property or descriptor definition without calling its getter:

```python
import inspect

class Sensor:
    @property
    def reading(self):
        raise RuntimeError("getter must not run during static inspection")

sensor = Sensor()
raw = inspect.getattr_static(sensor, "reading")
assert isinstance(raw, property)
# Inspect raw.fget only if appropriate; do not call it merely to inspect it.
```

The same caution applies to `inspect.getmembers(instance)`: it uses normal attribute access. On a trusted instance, a property getter can run during enumeration:

```python
import inspect

class Observable:
    def __init__(self):
        self.calls = 0
    @property
    def value(self):
        self.calls += 1
        return 10

obj = Observable()
inspect.getmembers(obj)
assert obj.calls >= 1
```

### 5.2 Code objects and flags

```python
import inspect

CO_VARARGS = inspect.CO_VARARGS
CO_VARKEYWORDS = inspect.CO_VARKEYWORDS
CO_GENERATOR = inspect.CO_GENERATOR
CO_COROUTINE = inspect.CO_COROUTINE
CO_ASYNC_GENERATOR = inspect.CO_ASYNC_GENERATOR

def example(a, *args, **kwargs):
    return a

def gen():
    yield 1

async def coro():
    return 1

async def async_gen():
    yield 1

code = example.__code__
print(code.co_varnames)                 # local/parameter names (ordering is defined by code metadata)
print(code.co_argcount)                 # positional parameter count, including positional-only
print(code.co_kwonlyargcount)           # keyword-only parameter count
print(code.co_code)                     # bytecode bytes; version-specific
print(code.co_consts)                   # constants used by the code object
print(code.co_names)                    # names referenced by the code
print(bool(code.co_flags & CO_VARARGS))
print(bool(code.co_flags & CO_VARKEYWORDS))
assert gen.__code__.co_flags & CO_GENERATOR
assert coro.__code__.co_flags & CO_COROUTINE
assert async_gen.__code__.co_flags & CO_ASYNC_GENERATOR
```

- `co_code` contains bytecode, `co_consts` constants, `co_names` referenced names, `co_varnames` local/parameter names, and `co_flags` compilation flags.
- `inspect.CO_VARARGS`, `CO_VARKEYWORDS`, `CO_GENERATOR`, `CO_COROUTINE`, and `CO_ASYNC_GENERATOR` expose relevant flag values. Use named constants rather than unexplained numeric bit masks.
- Code objects are implementation-level metadata and are not a stable format for serialization or cross-version bytecode analysis. Bytecode changes between Python releases. Prefer `inspect.signature()` for call contracts and `dis` for supported disassembly.
- A code object's flags indicate code shape, not that a coroutine has been awaited or that a generator has been consumed.

### 5.3 Annotation evaluation and Python version differences

Annotations have evolved, and libraries that inspect them must account for the interpreter version and definition context.

- **Python 3.12 baseline:** annotations are normally evaluated when the function/class definition executes. `from __future__ import annotations` postpones storing evaluated values and commonly stores string forms instead. Forward references may need resolution later.
- **Python 3.13:** the future import remains relevant; library code should avoid assuming a single representation across modules and Python versions.
- **Python 3.14:** deferred annotation evaluation changes introduced by PEP 649 and PEP 749 alter how annotations are stored and accessed. Annotation values may be computed on demand rather than eagerly at definition time. The standard-library `annotationlib` module provides `get_annotations()` and annotation formats for requesting values, forward references, or string representations. Consult the version-matched documentation for exact behavior and accepted `format` options.

Example for Python 3.14+ (run only on a Python version that provides `annotationlib`):

```python
# Python 3.14+
import annotationlib

def parse(value: NotImportedYet) -> int:
    return 1

print(annotationlib.get_annotations(parse, format=annotationlib.Format.STRING))
```

The example deliberately leaves `NotImportedYet` undefined. In Python 3.14, requesting the string format can represent the annotation expression without resolving that name to a runtime object. For cross-version library code, feature-detect `annotationlib` and use `typing.get_type_hints()` only when actual resolved types are required and the annotations' execution context is trusted.

**Important security note:** resolving annotations can evaluate expressions. Treat annotations from untrusted plugins or dynamically imported modules as executable metadata, not inert text. Do not call `eval()` on annotation strings as a shortcut.

### 5.4 Stack and frame inspection

```python
import inspect

def report_caller() -> str:
    frame = inspect.currentframe()
    if frame is None:
        return "frame unavailable"
    caller = None
    try:
        caller = frame.f_back
        if caller is None:
            return "caller unavailable"
        return f"{caller.f_code.co_name}:{caller.f_lineno}"
    finally:
        # Frame references can retain local variables and object graphs.
        del caller
        del frame

def run():
    return report_caller()

print(run())

def inspect_local_state() -> tuple[str, bool]:
    frame = inspect.currentframe()
    if frame is None:
        return "unavailable", False
    try:
        # Read-only diagnostic use; do not depend on mutating f_locals.
        return frame.f_code.co_name, "frame" in frame.f_locals
    finally:
        del frame

print(inspect_local_state())

stack = inspect.stack(context=0)
try:
    print(stack[0].function)
finally:
    # FrameInfo objects retain frame references; release the stack promptly.
    del stack
```

`inspect.stack()` returns frame information for the current stack and is convenient for diagnostics, but collecting and formatting many frames is relatively expensive. `inspect.currentframe()` may return `None` on implementations without the relevant frame support. A frame exposes data such as `f_code`, `f_lineno`, `f_globals`, and `f_locals`.

Risks and trade-offs:

- Stack walking is slower than passing context explicitly and can make hot paths expensive.
- Frame references can retain local variables and object graphs, delaying garbage collection; release references promptly.
- `f_locals` is a view/snapshot with implementation- and execution-context nuances; do not use it as a reliable way to mutate local variables.
- Stack shape changes with wrappers, async scheduling, generators, optimization, and refactoring. Avoid using caller inspection for core business logic or authorization.
- `sys._getframe()` is explicitly implementation-specific/private (underscore-prefixed); use only when a justified, documented portability trade-off exists.
- For warnings, prefer a suitable `stacklevel` or `skip_file_prefixes` where supported by the target Python version rather than manually constructing stack messages.

For traceback-oriented diagnostics, prefer the public `traceback` module over hand-formatting frames. `traceback.extract_tb(exc.__traceback__)` yields structured traceback entries:

```python
import traceback

try:
    1 / 0
except ZeroDivisionError as exc:
    frames = traceback.extract_tb(exc.__traceback__)
    assert frames
    print(type(exc).__name__, frames[-1].name)
```

Warnings emitted by library code can set `stacklevel=2` so the warning points to the caller rather than the helper:

```python
import warnings

def deprecated_api():
    warnings.warn("deprecated_api is deprecated", DeprecationWarning, stacklevel=2)
```

### 5.5 Inherited attributes and MRO reasoning

Python's attribute lookup is governed by the object's type, descriptors, and MRO—not simply by merging dictionaries.

```python
class A:
    label = "A"
class B(A):
    label = "B"
class C(A):
    pass
class D(B, C):
    pass

print([cls.__name__ for cls in D.__mro__])
# ['D', 'B', 'C', 'A', 'object']
assert D.label == "B"
assert "label" not in D.__dict__
assert "label" in dir(D)
```

`dir()` gives names; it does not explain which class wins lookup or whether a descriptor transforms the result. For a specific inherited value, inspect the MRO and each class's namespace. Class dictionaries are mapping proxies, and descriptor precedence (data descriptors, instance dictionary, non-data descriptors/class attributes) affects ordinary instance lookup.

### 5.6 Handling partial and unsupported introspection

Introspection APIs may fail for legitimate reasons. Write defensive code around the specific failure modes instead of broadly swallowing every exception.

```python
import inspect


def describe_callable(obj) -> str:
    if not callable(obj):
        return "not callable"
    try:
        signature = inspect.signature(obj)
    except (TypeError, ValueError):
        return "callable; signature unavailable"
    return str(signature)

assert describe_callable(len).startswith("(") or "unavailable" in describe_callable(len)
assert describe_callable(object()) == "not callable"

class CallableWithBadSignature:
    __signature__ = object()  # deliberately invalid metadata for a boundary test
    def __call__(self):
        return None

assert describe_callable(CallableWithBadSignature()) == "callable; signature unavailable"
```

The exact inspectability of built-ins can differ across implementations and releases, so the example accepts either a signature or an explicit unavailable result. Do not catch `Exception` indiscriminately unless there is a carefully justified boundary; doing so can hide real bugs.

## 6. Practical engineering examples

### 6.1 A validation wrapper that binds arguments

```python
import inspect
from collections.abc import Callable
from typing import Any


def invoke_checked(fn: Callable[..., Any], /, *args: Any, **kwargs: Any) -> Any:
    """Validate argument shape before invoking a callable."""
    signature = inspect.signature(fn)
    signature.bind(*args, **kwargs)  # raises TypeError before target execution
    return fn(*args, **kwargs)


def divide(numerator: float, denominator: float = 1.0) -> float:
    if denominator == 0:
        raise ValueError("denominator must not be zero")
    return numerator / denominator

assert invoke_checked(divide, 8, denominator=2) == 4
try:
    invoke_checked(divide, numerator=8, unknown=2)
except TypeError:
    pass
else:
    raise AssertionError("unexpected keyword should be rejected")
```

Signature binding validates the *shape* of the call, not annotation types or domain constraints. The target function still owns value validation.

### 6.2 Mini dependency-injection container

A DI container maps declared dependencies to already-created instances. This example intentionally supports a small subset: required constructor/function parameters need type annotations; dependencies are registered by type; optional unregistered parameters use their defaults; unknown required dependencies fail clearly. It does not implement scopes, async providers, generic type resolution, or security isolation.

```python
from __future__ import annotations

import inspect
from typing import Any, get_type_hints


class Container:
    def __init__(self) -> None:
        self._instances: dict[object, object] = {}

    def register_instance(self, key: object, instance: object) -> None:
        self._instances[key] = instance

    def resolve(self, provider: Any) -> Any:
        signature = inspect.signature(provider)
        # For a class provider, constructor parameter annotations live on __init__,
        # while inspect.signature(class) exposes the constructor call signature.
        annotation_source = provider.__init__ if inspect.isclass(provider) else provider
        try:
            hints = get_type_hints(annotation_source)
        except (NameError, TypeError, AttributeError) as exc:
            raise ValueError(f"Cannot resolve annotations for {provider!r}") from exc

        bound_values: dict[str, object] = {}
        for name, parameter in signature.parameters.items():
            if parameter.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
                # This deliberately small container does not inject variadic args.
                continue
            if parameter.kind is inspect.Parameter.POSITIONAL_ONLY:
                raise ValueError(
                    f"Provider parameter {name!r} is positional-only; this container injects by keyword"
                )

            key = hints.get(name, parameter.annotation)
            if key is inspect.Parameter.empty:
                if parameter.default is not inspect.Parameter.empty:
                    continue
                raise ValueError(f"Parameter {name!r} has no type annotation")

            if key in self._instances:
                bound_values[name] = self._instances[key]
            elif parameter.default is not inspect.Parameter.empty:
                # Leave optional parameters to their declared defaults.
                continue
            else:
                raise LookupError(f"No dependency registered for {name!r}: {key!r}")

        bound = signature.bind(**bound_values)
        bound.apply_defaults()
        return provider(*bound.args, **bound.kwargs)


class Logger:
    def __init__(self, label: str = "app") -> None:
        self.label = label

class UserRepository:
    def __init__(self, logger: Logger) -> None:
        self.logger = logger

class UserService:
    def __init__(self, repository: UserRepository, logger: Logger) -> None:
        self.repository = repository
        self.logger = logger

container = Container()
logger = Logger("users")
repository = UserRepository(logger)
container.register_instance(Logger, logger)
container.register_instance(UserRepository, repository)
service = container.resolve(UserService)
assert service.repository is repository
assert service.logger is logger

# Negative/boundary tests: missing dependency, missing annotation, and
# positional-only parameters are rejected explicitly.
class UnregisteredDependency:
    pass

class NeedsMissingDependency:
    def __init__(self, dep: UnregisteredDependency) -> None:
        self.dep = dep

try:
    container.resolve(NeedsMissingDependency)
except LookupError:
    pass
else:
    raise AssertionError("unregistered required dependency should fail")

def untyped_required(value):
    return value

try:
    container.resolve(untyped_required)
except ValueError as exc:
    assert "no type annotation" in str(exc)
else:
    raise AssertionError("missing required annotation should fail")

def positional_only(value: int, /):
    return value

try:
    container.resolve(positional_only)
except ValueError as exc:
    assert "positional-only" in str(exc)
else:
    raise AssertionError("positional-only provider should be rejected")
```

**How it works:** `inspect.signature()` supplies parameter names and defaults; `get_type_hints()` resolves annotation objects; the registry maps a type key to an instance; `Signature.bind()` confirms the resulting keyword arguments satisfy the provider's call signature; `apply_defaults()` fills defaults before invocation.

**Limitations and production considerations:**

- `get_type_hints()` can execute annotation expressions and may fail on unresolved names. Only resolve trusted application code.
- `Optional[T]`, unions, generic aliases, `Annotated`, protocols, forward references, and qualifiers need explicit resolution policies; this example does not pretend to handle them.
- Variadic parameters are skipped; positional-only parameters are not supported by this keyword-only injection strategy and should be rejected or handled explicitly in a production version.
- A real container needs lifecycle/scope rules, cycle detection, useful dependency graphs, deterministic override behavior, tests, and clear error reporting.
- Prefer explicit constructor injection for small applications. Introspection is justified when a framework genuinely needs generic wiring, not merely to avoid writing a few lines.

### 6.3 A safe member summary for a trusted object

```python
import inspect


def summarize_trusted_object(obj: object) -> dict[str, object]:
    """Summarize common metadata; assumes obj itself is trusted."""
    cls = type(obj)
    try:
        instance_vars = vars(obj)
    except TypeError:
        instance_vars = None

    return {
        "type": f"{cls.__module__}.{cls.__qualname__}",
        "callable": callable(obj),
        "instance_namespace": instance_vars,
        "mro": tuple(base.__qualname__ for base in cls.__mro__),
        "doc": inspect.getdoc(cls),
    }
```

This helper avoids iterating through every member, but it is not safe for arbitrary hostile objects: `type(obj)`, `vars(obj)`, metadata access, and representations may still be influenced by custom behavior or objects nested in the result. Do not serialize arbitrary introspection output without controlling its contents.

## 7. Common mistakes and debugging techniques

1. **Treating `dir()` as a schema.** It is for exploration, can be customized, and does not promise a stable public interface. Use documented APIs or explicit registries for contracts.
2. **Assuming `vars(obj)` shows inherited attributes.** It usually shows only the object's own namespace. Check class dictionaries and `__mro__` for inherited definitions.
3. **Calling a property just to inspect it.** `getattr()` can execute I/O, mutate state, block, or raise. Use `inspect.getattr_static()` when raw descriptor information is what you need.
4. **Assuming `hasattr()` is side-effect-free.** It invokes normal lookup and treats `AttributeError` as absence, including an `AttributeError` raised inside a property.
5. **Assuming annotations are runtime validation.** They are metadata unless a separate validator enforces them.
6. **Reading `__annotations__` as always resolved values.** The future import and Python 3.14 semantics make that assumption brittle. Choose `get_type_hints()` or version-aware `annotationlib` based on the task.
7. **Assuming all callables have signatures or source.** Handle `TypeError`/`ValueError` from signature inspection and `OSError`/`TypeError` from source inspection.
8. **Using `__code__` to reconstruct a function call contract.** Use `inspect.signature()` for parameter semantics; code objects are lower-level and version-sensitive.
9. **Using stack inspection for application logic.** It couples behavior to call-stack shape and adds overhead. Pass explicit context where possible.
10. **Assuming `__subclasses__()` finds every plugin.** It lists direct, currently live subclasses and does not import modules that have not been loaded.

Debugging workflow:

- Start with `type(obj)` and `callable(obj)`.
- Inspect `dir(obj)` for discovery, then query one known attribute at a time.
- Use `vars(obj)` only when a namespace exists; inspect class dictionaries and MRO separately.
- Prefer `inspect.signature()` and `inspect.getdoc()` over manual metadata reconstruction.
- Catch documented introspection failures narrowly and report what is unavailable.
- Build minimal reproducible tests for descriptor side effects, inherited lookup, and version-sensitive annotations.

## 8. Security, performance, and compatibility

### Security

- Introspection is not a sandbox. A hostile object can run code through properties, descriptors, custom attribute hooks, metaclasses, or annotation evaluation.
- Avoid evaluating annotations from untrusted code. Importing a module can itself execute module-level code.
- Do not expose arbitrary `getattr(obj, user_supplied_name)` access in public APIs. Use an allow-list of explicitly supported names.
- Avoid calling `repr()` on arbitrary nested objects when logging introspection results; representations may execute custom code or disclose secrets.
- Keep introspection output out of public responses unless sanitized; it may reveal module paths, configuration, internal names, or implementation details.

### Performance

- `inspect.stack()` and repeated member enumeration can be expensive. Do not place them in tight loops without measurement.
- Cache stable metadata only when invalidation and object lifetime are understood. Classes and annotations may be modified or resolved later.
- Prefer explicit dependency wiring and registries on hot paths. Introspect at setup/startup time rather than for every request where feasible.
- Measure before optimizing; introspection overhead depends on object type, runtime, and call frequency.

### Compatibility

- The lesson's baseline is Python 3.12+. Annotation representation and evaluation are version-sensitive, especially in Python 3.14.
- `inspect` behavior for built-ins, extension callables, source paths, and frames can vary by implementation and version.
- Code objects and bytecode are not stable cross-version interchange formats.
- Use feature detection for optional APIs and test against the interpreter versions your library supports.
- Avoid depending on CPython memory addresses, private `sys._getframe()` behavior, exact `dir()` ordering, or the exact output formatting of `help()`.

## 9. Practical mini-project: Object Inspector

Build a small inspector script for a set of **trusted, locally defined objects**. The goal is to produce useful diagnostics without executing every property. The reference implementation is a reusable function rather than a full command-line parser; adding an `argparse` interface is an optional extension.

### Requirements

1. Define a sample class with a base class, an instance attribute, a class attribute, and a property that records when it runs.
2. Report the object's fully qualified type name, callable status, instance namespace when available, MRO, docstring, and signature when the object is callable.
3. List names from `dir()` but label them as exploratory names, not a public schema.
4. For selected attributes, use `inspect.getattr_static()` to identify properties without invoking their getter.
5. Handle missing `__dict__`, unavailable signatures, and unavailable source gracefully.
6. Add tests proving the inspector does not trigger the sample property.

### Reference implementation

```python
import inspect
from typing import Any


class BaseRecord:
    """Base class for inspector examples."""
    source = "demo"

class Record(BaseRecord):
    """A record with a deliberately observable property."""
    def __init__(self, value: int) -> None:
        self.value = value
        self.property_calls = 0

    @property
    def expensive(self) -> int:
        self.property_calls += 1
        return self.value * 10


def inspect_object(obj: Any) -> dict[str, Any]:
    cls = type(obj)
    try:
        namespace = dict(vars(obj))
    except TypeError:
        namespace = None

    try:
        signature = str(inspect.signature(obj)) if callable(obj) else None
    except (TypeError, ValueError):
        signature = None

    # Best-effort source inspection; call only for trusted objects.
    try:
        source = inspect.getsource(obj)
    except (OSError, TypeError):
        source = None

    return {
        "qualified_type": f"{cls.__module__}.{cls.__qualname__}",
        "callable": callable(obj),
        "namespace": namespace,
        "mro": [base.__qualname__ for base in cls.__mro__],
        "doc": inspect.getdoc(cls),
        "signature": signature,
        "source": source,
        "names_for_exploration": dir(obj),
    }


record = Record(4)
report = inspect_object(record)
assert report["namespace"]["value"] == 4
assert "BaseRecord" in report["mro"]
assert "expensive" in report["names_for_exploration"]
assert record.property_calls == 0  # no property getter was invoked
assert "source" in report  # source may be text or None
raw = inspect.getattr_static(record, "expensive")
assert isinstance(raw, property)
assert record.property_calls == 0
print(report["qualified_type"], report["mro"])

class SlotRecord:
    __slots__ = ("value",)
    def __init__(self, value: int) -> None:
        self.value = value

slot_report = inspect_object(SlotRecord(3))
assert slot_report["namespace"] is None
assert slot_report["signature"] is None

class CallableWithUnavailableSignature:
    __signature__ = object()
    def __call__(self):
        return None

callable_report = inspect_object(CallableWithUnavailableSignature())
assert callable_report["callable"] is True
assert callable_report["signature"] is None
```

### Project acceptance tests

- The inspector does not call `Record.expensive`.
- A slotted object is reported with `namespace=None`, not a crash.
- A non-callable instance reports `signature=None`.
- A callable with an unavailable signature is handled without crashing.
- Source retrieval is attempted only for trusted local objects and records an unavailable result when `OSError` or `TypeError` is raised.
- The output does not claim that `dir()` is a stable public contract.
- Tests assert selected facts rather than the entire `dir()` result.

Extension task: add a `--source` option that attempts `inspect.getsource()` only for trusted local objects and handles `OSError` and `TypeError`. Keep source output separate from the default summary because it can be large and unavailable.

## 10. Hands-on exercises

Try each exercise before reading the solutions in the next section.

1. **Namespace reasoning:** Create `Parent` and `Child`, where `Parent` defines a method and class attribute and `Child.__init__` defines an instance attribute. Predict which names appear in `vars(child)` and whether each appears in `dir(child)`.
2. **Binding:** Write a function with positional-only, positional-or-keyword, `*args`, keyword-only, and `**kwargs` parameters. Use `inspect.signature()` to verify each kind and show one valid and two invalid calls with `Signature.bind()`.
3. **Defaults:** Show the difference between `__defaults__`, `__kwdefaults__`, and defaults after `BoundArguments.apply_defaults()`.
4. **Descriptor safety:** Make a property increment a counter. Demonstrate that `getattr()` increments it and `inspect.getattr_static()` does not.
5. **Annotations:** Define a forward reference and compare `__annotations__` with `typing.get_type_hints()`. Explain what happens if the referenced name is missing.
6. **Source limits:** Attempt `inspect.getsource()` on a local function and on `len`; handle unavailable source without assuming one specific result for all implementations.
7. **MRO:** Use diamond inheritance to print `__mro__` and explain which class supplies a shadowed attribute.
8. **Frames:** Capture the caller's function name and line number, then explain why that is brittle as application logic.
9. **DI extension:** Modify the mini container to reject positional-only provider parameters with a clear error instead of silently mishandling them.
10. **Boundary case:** Create a class with `__slots__` and confirm that `vars(instance)` may raise `TypeError`.

## 11. Exercise solutions

### Solution 1 — namespaces

```python
class Parent:
    role = "base"
    def speak(self):
        return "hello"
class Child(Parent):
    def __init__(self):
        self.name = "Mira"

child = Child()
assert vars(child) == {"name": "Mira"}
assert "speak" not in vars(child)
assert "role" not in vars(child)
assert "speak" in dir(child)
assert "role" in dir(child)
assert "name" in dir(child)
```

### Solution 2 — binding

```python
import inspect

def f(a, /, b, *args, required, optional=9, **extras):
    return a, b, args, required, optional, extras

sig = inspect.signature(f)
assert sig.parameters["a"].kind is inspect.Parameter.POSITIONAL_ONLY
assert sig.parameters["args"].kind is inspect.Parameter.VAR_POSITIONAL
assert sig.parameters["required"].kind is inspect.Parameter.KEYWORD_ONLY
assert sig.parameters["extras"].kind is inspect.Parameter.VAR_KEYWORD
sig.bind(1, 2, 3, required="yes")
for args, kwargs in [((1,), {"required": "yes"}), ((1, 2), {})]:
    try:
        sig.bind(*args, **kwargs)
    except TypeError:
        pass
    else:
        raise AssertionError("expected binding failure")
```

### Solution 3 — defaults

```python
def f(a, b=2, *, mode="fast"):
    pass

assert f.__defaults__ == (2,)
assert f.__kwdefaults__ == {"mode": "fast"}
import inspect
bound = inspect.signature(f).bind(1)
assert "b" not in bound.arguments
bound.apply_defaults()
assert bound.arguments == {"a": 1, "b": 2, "mode": "fast"}
```

### Solution 4 — descriptor safety

```python
import inspect
class Counter:
    def __init__(self): self.calls = 0
    @property
    def value(self):
        self.calls += 1
        return 5

c = Counter()
assert getattr(c, "value") == 5
assert c.calls == 1
assert isinstance(inspect.getattr_static(c, "value"), property)
assert c.calls == 1
```

### Solution 5 — annotations

```python
from __future__ import annotations
from typing import get_type_hints

class Item: pass
def use(item: Item) -> list[Item]: return [item]
assert get_type_hints(use)["item"] is Item
assert get_type_hints(use)["return"] == list[Item]
```

With the future import, raw annotations are commonly strings. If a referenced name is missing from the namespaces used for resolution, `get_type_hints()` can raise `NameError`; catch it at a framework boundary and explain which annotation could not be resolved.

### Solution 6 — source

```python
import inspect

def local():
    return 1

for obj in (local, len):
    try:
        text = inspect.getsource(obj)
    except (OSError, TypeError):
        text = None
    print(obj, "source available" if text is not None else "source unavailable")
```

Whether a source string is available depends on how and where the callable was defined. The code tests the supported failure path rather than asserting that every runtime must behave identically.

### Solution 7 — MRO

```python
class A: value = "A"
class B(A): value = "B"
class C(A): value = "C"
class D(B, C): pass
assert [x.__name__ for x in D.__mro__] == ["D", "B", "C", "A", "object"]
assert D.value == "B"
```

### Solution 8 — frames

Use the `report_caller()` example in Section 5.4. Its output depends on the call site and line numbers change when code is edited; wrappers and async boundaries can change what counts as the caller. Pass explicit diagnostic context when correctness depends on it.

### Solution 9 — DI boundary

The full container in Section 6.2 already contains this guard. The following runnable check isolates the same policy:

```python
import inspect

def positional_only(value: int, /):
    return value

parameter = next(iter(inspect.signature(positional_only).parameters.values()))
name = parameter.name
try:
    if parameter.kind is inspect.Parameter.POSITIONAL_ONLY:
        raise ValueError(
            f"Provider parameter {name!r} is positional-only; this container injects by keyword"
        )
except ValueError as exc:
    assert "positional-only" in str(exc)
else:
    raise AssertionError("positional-only provider should be rejected")
```

A more complete container could build positional arguments in signature order, but it should implement and test that behavior deliberately.

### Solution 10 — slots

```python
class SlotOnly:
    __slots__ = ("x",)
    def __init__(self): self.x = 3

item = SlotOnly()
try:
    vars(item)
except TypeError:
    pass
else:
    raise AssertionError("expected no instance dictionary")
```

## 12. Interview and reasoning questions

1. Why is `isinstance(x, Base)` often preferable to `type(x) is Base`?
2. What does `id()` guarantee, and what does it not guarantee?
3. Why can `dir(x)` contain names absent from `vars(x)`?
4. Why might `vars(x)` raise `TypeError`?
5. What does `Signature.bind()` validate, and what does it leave to the target function?
6. Explain the five `inspect.Parameter` kinds and how they map to Python syntax.
7. Why is `getattr_static()` valuable when inspecting properties or descriptors? What does it not guarantee?
8. Why should frameworks avoid assuming `__annotations__` is always a dictionary of resolved classes?
9. What changed in Python 3.14 annotation handling, and why does `annotationlib` matter?
10. Why is `inspect.stack()` a poor choice for a hot request path?
11. How do `__bases__`, `__mro__`, and `__subclasses__()` differ?
12. Why can `inspect.getsource()` fail for a callable that works perfectly?
13. How would you safely inspect plugin classes without triggering arbitrary properties?
14. What are the limits of a type-hint-based dependency-injection container?
15. When should a production API avoid introspection and use explicit registration or configuration instead?

**Strong-answer standard:** explain the mechanism, one practical use case, a failure mode, and the relevant compatibility/security trade-off—not just a definition.

## 13. Final competency checklist

You are ready to move on when you can do all of the following without copying the examples blindly:

- [ ] Distinguish exact type checks from subclass-aware checks.
- [ ] Explain `id()` and `callable()` without overclaiming.
- [ ] Distinguish `dir()`, `vars()`, instance `__dict__`, class `__dict__`, and inherited attributes.
- [ ] Inspect names, docs, function defaults, annotations, code objects, MRO, bases, and direct subclasses.
- [ ] Read all five parameter kinds from a `Signature`.
- [ ] Use `Signature.bind()` and `BoundArguments.apply_defaults()` to validate call shape.
- [ ] Use relevant `inspect` predicates and handle unsupported source/signature inspection.
- [ ] Explain why `get_type_hints()` can be more useful than raw `__annotations__` and why it is not risk-free.
- [ ] Describe the Python 3.12+ baseline and Python 3.14 annotation changes accurately.
- [ ] Demonstrate the side-effect difference between `getattr()` and `getattr_static()` for a property.
- [ ] Explain code flags and why bytecode is version-sensitive.
- [ ] Use frame inspection for diagnostics only and release frame references.
- [ ] Build and test the mini object inspector and DI example, including negative cases.
- [ ] Choose explicit APIs over introspection when the latter adds fragility without meaningful value.

## Official references

Use documentation matching the interpreter version you support:

- Python built-in functions (`type`, `isinstance`, `issubclass`, `id`, `callable`, `dir`, `vars`, `getattr`, `hasattr`): https://docs.python.org/3/library/functions.html
- `inspect` module: https://docs.python.org/3/library/inspect.html
- `typing.get_type_hints`: https://docs.python.org/3/library/typing.html#typing.get_type_hints
- `annotationlib` (Python 3.14+): https://docs.python.org/3/library/annotationlib.html
- PEP 649 — Deferred Evaluation Of Annotations: https://peps.python.org/pep-0649/
- PEP 749 — Implementing PEP 649: https://peps.python.org/pep-0749/
- Python data model (attribute access, descriptors, class objects): https://docs.python.org/3/reference/datamodel.html
- `dis` module for bytecode inspection: https://docs.python.org/3/library/dis.html
- `sys._getframe`: https://docs.python.org/3/library/sys.html#sys._getframe

---

**Engineering principle:** introspection is powerful when it reduces duplication and enables generic tooling. It becomes a liability when runtime observations are treated as contracts, when inspection triggers side effects, or when version-specific details leak into application logic. Prefer the simplest explicit design that satisfies the requirement.
