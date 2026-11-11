# `__init_subclass__()` and Subclass Registries

> **Stage 1 · Module 12 — Metaprogramming and Dynamic Python**  
> **Baseline:** Python 3.12+  
> **Goal:** build class-definition hooks and plugin registries that are explicit, cooperative, testable, and safe to extend.

## Learning outcomes

By the end, you should be able to explain when `__init_subclass__()` runs, validate a subclass at definition time, register it by an explicit identifier, cooperate with other mixins, use `__set_name__()` in descriptors, test and reset registry state, discover installed plugins through entry points, and identify the few cases where a metaclass is the better tool.

The module roadmap's guiding principle applies here: **plain code → decorators → class decorators → `__init_subclass__()` → descriptors → metaclasses → AST/`exec`**. Use the least powerful mechanism that meets the requirement.

---

# 1. Prerequisites and class-creation fundamentals

## 1.1 Classes are objects created by a class statement

A `class` statement creates a class object and binds it to a name. The class body executes once while the class is being created; methods are function objects placed in the class namespace. Later, instances are created by calling the class.

```python
class Sensor:
    kind = "temperature"

    def read(self) -> float:
        return 21.5

sensor = Sensor()
print(type(sensor).__name__)
print(Sensor.kind)
print(sensor.read())
```

Expected output:

```text
Sensor
temperature
21.5
```

## 1.2 The class-creation sequence (simplified)

For a typical `class Child(Parent, option=value): ...` statement, Python evaluates bases and class keywords, selects a metaclass, prepares and executes the class namespace, and the metaclass creates the class object. During normal `type.__new__` processing, descriptors in the new namespace receive `__set_name__(owner, name)` before the parent hook `__init_subclass__()` runs. Class decorators are then applied to the resulting class object. Metaclass customizations can affect details, so this is the normal class-statement path rather than a promise about every custom metaclass.

- Descriptors defined in the class body receive `__set_name__()` during class creation, before `__init_subclass__()`.
- `Parent.__init_subclass__` is invoked as part of creating the subclass.
- A decorator such as `@dataclass` is applied **after** the class object has been created and its `__init_subclass__()` hooks have run.

Do not rely on hooks seeing transformations that a later decorator has not performed yet.

## 1.3 What is `__init_subclass__()`?

`__init_subclass__` is a hook on a parent class. Python calls it when a new subclass is created. The hook receives the new subclass as `cls`; it is not an instance initializer and it does not run for each instance.

Use it for class-definition-time validation, registration, or interpreting class keywords. It avoids a metaclass for many common framework tasks.

---

# 2. Basic `__init_subclass__()` behavior

## 2.1 The parent receives the child through `cls`

```python
class Base:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        print(f"created subclass: {cls.__name__}")

class CsvReader(Base):
    pass

class JsonReader(Base):
    pass
```

Expected output:

```text
created subclass: CsvReader
created subclass: JsonReader
```

`cls` is `CsvReader` and then `JsonReader`. The hook is commonly written with `cls` as the first argument, just like a class method, but it is a special hook and does not need an explicit `@classmethod` decorator.

## 2.2 Class-definition keyword arguments

A subclass statement can pass keywords to base-class hooks:

```python
class Reader:
    def __init_subclass__(cls, *, format: str, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.format = format

class CsvReader(Reader, format="csv"):
    pass

print(CsvReader.format)
```

Expected output:

```text
csv
```

The `format=` keyword is consumed by `Reader.__init_subclass__`. The `**kwargs` path is still important: another base or metaclass may have a keyword to consume. Calling `super().__init_subclass__(**kwargs)` lets the next implementation in the method resolution order process remaining keywords. At the end of the chain, `object.__init_subclass__` rejects unconsumed keywords, which is useful because typos do not silently pass.

### What if a keyword is optional?

```python
class Reader:
    def __init_subclass__(cls, *, format: str | None = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if format is not None:
            cls.format = format

class GenericReader(Reader):
    pass

class CsvReader(Reader, format="csv"):
    pass

print(hasattr(GenericReader, "format"), CsvReader.format)
```

Expected output:

```text
False csv
```

Use optional class keywords when intermediate classes are legitimate and do not yet declare a concrete configuration.

## 2.3 When it is appropriate—and when it is overkill

Appropriate: automatic registration, class-level validation, processing class keywords, enforcing naming conventions, and small declarative APIs.

Overkill: one or two subclasses with no shared behavior. A normal explicit registration call or ordinary constructor often makes intent clearer.

---

# 3. Subclass validation

## 3.1 Validate the class object, not just its instances

A class hook is a good place to reject an invalid subclass early, at import/class-definition time, instead of allowing a later runtime failure.

```python
class Task:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not callable(getattr(cls, "run", None)):
            raise TypeError(f"{cls.__name__} must define a callable run()")

class GoodTask(Task):
    def run(self) -> str:
        return "done"

print(GoodTask().run())

try:
    class BrokenTask(Task):
        pass
except TypeError as exc:
    print(type(exc).__name__, exc)
```

Expected output:

```text
done
TypeError BrokenTask must define a callable run()
```

### Inherited attributes complicate validation

`getattr(cls, "run", None)` accepts an inherited implementation. That is often correct: a mixin or parent may provide the implementation. If the contract specifically requires an override in the subclass body, inspect `cls.__dict__` instead. Be deliberate about which contract you intend to enforce.

Do not treat `__annotations__` as proof that a value exists. An annotation such as `name: str` is metadata; it does not create `name` as a class attribute or instance field.

## 3.2 Abstract base classes and legitimate intermediate classes

A base can support reusable intermediate classes by separating abstractness from concrete validation. `abc.ABC` and `@abstractmethod` express an abstract contract, while `__init_subclass__` can enforce extra metadata. The hook should not reject an intentionally abstract intermediate class merely because it is not ready to be instantiated.

```python
from abc import ABC, abstractmethod

class Exporter(ABC):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Validate only concrete classes. Abstract methods inherited or
        # declared on this class remain listed in __abstractmethods__ once
        # ABCMeta finishes class creation, so don't rely on that attribute
        # inside this hook for the just-created class.
        if not cls.__dict__.get("__abstract__", False):
            if "media_type" not in cls.__dict__:
                raise TypeError(f"{cls.__name__} must declare media_type")

    @abstractmethod
    def export(self, rows: list[dict[str, object]]) -> bytes:
        raise NotImplementedError

class JsonExporterBase(Exporter):
    __abstract__ = True
    # It intentionally leaves export() abstract, so ABCMeta also prevents
    # direct instantiation of this intermediate class.

class JsonExporter(JsonExporterBase):
    media_type = "application/json"

    def export(self, rows: list[dict[str, object]]) -> bytes:
        return repr(rows).encode()

print(JsonExporter.media_type)

try:
    class BrokenExporter(JsonExporterBase):
        def export(self, rows: list[dict[str, object]]) -> bytes:
            return b"broken"
except TypeError as exc:
    print(type(exc).__name__, exc)
```

Expected output:

```text
application/json
TypeError BrokenExporter must declare media_type
```

**Important design note:** `__abstract__` here is a small explicit framework convention, not a built-in Python marker. A concrete class can still be abstract because it has unresolved abstract methods; Python's `ABCMeta` prevents instantiation. For robust frameworks, prefer explicit class keywords such as `abstract=True`, or validate required metadata only when a concrete registration keyword is supplied. Avoid fragile timing assumptions about when `ABCMeta` finalizes `__abstractmethods__`.

## 3.3 Meaningful exceptions

Raise `TypeError` when the class definition violates the framework contract. Include the subclass name and the missing/invalid requirement. Fail early, but avoid invoking arbitrary descriptors unnecessarily during validation if classes may be untrusted; `getattr()` can execute descriptor code. `inspect.getattr_static()` can be useful for passive inspection, though it returns the descriptor itself rather than its bound value.

---

# 4. Registry implementation

## 4.1 A minimal explicit-name registry

A registry maps stable identifiers to class objects. The identifier should be part of the plugin contract; do not rely on display names unless that is an intentional policy.

```python
class Reader:
    registry: dict[str, type["Reader"]] = {}

    def __init_subclass__(cls, *, name: str | None = None, **kwargs):
        super().__init_subclass__(**kwargs)
        # A base or explicitly abstract intermediate class can omit a name.
        if name is None:
            if cls.__dict__.get("__abstract_plugin__", False):
                return
            raise TypeError(f"{cls.__name__} must declare name=...")
        if not isinstance(name, str) or not name or name.strip() != name:
            raise TypeError(
                f"{cls.__name__} has an invalid plugin name; expected a non-empty, trimmed string"
            )
        if name in Reader.registry:
            existing = Reader.registry[name]
            raise TypeError(
                f"duplicate reader name {name!r}: {existing.__module__}.{existing.__qualname__}"
            )
        Reader.registry[name] = cls
        cls.plugin_name = name

    def read(self, text: str) -> list[str]:
        raise NotImplementedError

class CsvReader(Reader, name="csv"):
    def read(self, text: str) -> list[str]:
        return text.splitlines()

print(Reader.registry["csv"] is CsvReader)
print(Reader.registry["csv"]( ).read("a\nb"))
```

Expected output:

```text
True
['a', 'b']
```

The `name` argument is required for ordinary concrete plugins. An abstract/intermediate class can opt out using a clear framework convention. In production, a separate base class or an explicit `abstract=True` class keyword is often safer than a magic class attribute; the complete project below uses explicit keyword arguments to make the contract visible.

## 4.2 Three common key strategies

| Key | Example | Strength | Risk |
|---|---|---|---|
| Explicit identifier | `name="parquet"` | Stable public contract | Requires naming policy and collision checks |
| Class name | `CsvReader.__name__` | Easy, no extra declaration | Renames break configuration; collisions across modules |
| Attribute-derived key | `cls.format` or descriptor metadata | Convenient for declarative schemas | Attribute may be inherited, missing, or assigned later |

Use explicit identifiers for public plugin APIs. A module-qualified class name can be useful for diagnostics, but is usually a poor user-facing configuration key.

## 4.3 Duplicate names, namespaces, and replacement policy

Do not silently overwrite a prior registration. Choose one documented policy:

1. Reject duplicates (safest default).
2. Permit replacement only through an explicit override flag.
3. Namespace identifiers, for example `"warehouse.parquet"` or `(namespace, name)`.

If versions coexist, include a version in the key or store metadata alongside the class. Do not confuse plugin API version with package version. Normalize identifiers only if the contract explicitly defines normalization; silently lowercasing names can merge identifiers that users intended to keep distinct.

## 4.4 Lookup failures

Prefer a deliberate lookup API that raises a clear error instead of exposing accidental `KeyError` behavior:

```python
class ReaderRegistry:
    def __init__(self) -> None:
        self._items: dict[str, type] = {}

    def register(self, name: str, plugin: type) -> None:
        if not isinstance(name, str) or not name or name.strip() != name:
            raise ValueError("plugin name must be a non-empty string without surrounding whitespace")
        if not isinstance(plugin, type):
            raise TypeError("plugin must be a class")
        if name in self._items:
            raise ValueError(f"plugin {name!r} already registered")
        self._items[name] = plugin

    def get(self, name: str) -> type:
        try:
            return self._items[name]
        except KeyError:
            raise LookupError(f"no plugin registered as {name!r}") from None
```

Use `LookupError` or a domain-specific subclass for missing plugins; use `TypeError` for an invalid class definition. Keep these failure categories distinct.

---

# 5. Descriptors and `__set_name__()`

## 5.1 What `__set_name__()` does

When a descriptor instance is assigned in a class body, Python calls its `__set_name__(owner, name)` method after the class object is created. The descriptor can record which class owns it and what attribute name it was assigned to.

```python
class Field:
    def __set_name__(self, owner: type, name: str) -> None:
        self.owner = owner
        self.name = name
        self.storage_name = f"_{name}"

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return getattr(instance, self.storage_name, None)

    def __set__(self, instance, value) -> None:
        setattr(instance, self.storage_name, value)

class Record:
    identifier = Field()

record = Record()
record.identifier = 42
print(Record.identifier.name, Record.identifier.owner.__name__, record.identifier)
```

Expected output:

```text
identifier Record 42
```

This descriptor is intentionally small: it stores values on instances under a private name and returns `None` before a value is assigned. Production descriptors should specify validation, defaults, deletion behavior, and storage semantics.

## 5.2 Adding a descriptor after class creation

`__set_name__()` is automatically called for descriptors placed in the class namespace during creation. If you later do `Record.extra = Field()`, Python does **not** automatically call `__set_name__()` for you. If late injection is intentional, call it explicitly:

```python
field = Field()
Record.extra = field
field.__set_name__(Record, "extra")
```

Usually it is simpler and clearer to declare descriptors in the class body. Also note that a descriptor reused across multiple owner classes must decide whether it can safely store multiple owner/name pairs; one `owner` attribute is not sufficient for a descriptor instance shared across classes.

---

# 6. Inheritance and plugin discovery

## 6.1 Cooperative multiple inheritance

`__init_subclass__()` participates in the method resolution order (MRO). Each mixin should consume only the keywords it owns and pass the rest to `super()`. Every participating implementation must follow this protocol.

```python
class Named:
    def __init_subclass__(cls, *, name: str, **kwargs):
        cls.name = name
        super().__init_subclass__(**kwargs)

class Versioned:
    def __init_subclass__(cls, *, version: int = 1, **kwargs):
        cls.version = version
        super().__init_subclass__(**kwargs)

class PluginBase:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.initialized_by_base = True

class JsonPlugin(Named, Versioned, PluginBase, name="json", version=2):
    pass

print(JsonPlugin.name, JsonPlugin.version, JsonPlugin.initialized_by_base)
```

Expected output:

```text
json 2 True
```

A non-cooperative mixin that fails to call `super()` can stop the chain. A mixin that accepts `**kwargs` but does not consume or forward it can hide a typo. Prefer keyword-only options so configuration does not depend on positional argument order.

## 6.2 `__subclasses__()` is not a plugin loader

`Base.__subclasses__()` returns **direct, currently live subclasses** of `Base`; it does not recursively return all descendants. A recursive walk can collect descendants:

```python
def descendants(base: type) -> list[type]:
    found: list[type] = []
    seen: set[type] = set()
    stack = list(base.__subclasses__())
    while stack:
        child = stack.pop()
        if child in seen:
            continue
        seen.add(child)
        found.append(child)
        stack.extend(child.__subclasses__())
    return found
```

Even a recursive walk only finds classes that have already been created and remain alive. It does not import modules, discover plugins that have never been imported, or define a stable ordering. Multiple inheritance does not make a class appear as a direct child of every base in a predictable registry contract; `__subclasses__()` follows actual inheritance relationships and returns direct subclass relationships for that base.

## 6.3 Weak references and dynamically created classes

`__subclasses__()` tracks live subclass objects using weak-reference semantics in CPython. If a dynamically created class has no strong references, it may be garbage-collected and disappear from a later `__subclasses__()` result. A normal registry dictionary strongly references each registered class, which keeps it alive. A `weakref.WeakValueDictionary` can avoid that retention, but entries may disappear when no other strong reference exists. Weak registries are not automatically better: plugins intended to remain available need stable ownership.

## 6.4 Import-time registration and the hidden-import problem

A subclass is registered only when its class statement executes, and that statement executes only if its module is imported. Importing `plugin_base` does not automatically import every module in a `plugins/` directory. This is the hidden-import problem.

For a small application, explicit imports are often the simplest answer:

```python
# application startup
import myapp.plugins.csv_reader
import myapp.plugins.json_reader
```

For installed third-party plugins, use package entry points rather than trying to import every package on the machine.

## 6.5 Lazy discovery with `importlib.metadata.entry_points()`

Entry points let installed distributions advertise plugin objects. They are packaging metadata, not magic auto-import: your application must query the relevant group and load the selected entry point. Loading imports the referenced object and can execute its module code, so only load plugins from trusted distributions.

```python
from importlib.metadata import entry_points

# Package metadata may advertise, for example:
# [project.entry-points."myapp.readers"]
# csv = "my_csv_plugin:CsvReader"

def discover_reader_entry_points():
    eps = entry_points(group="myapp.readers")  # Python 3.12+
    for ep in eps:
        yield ep.name, ep

# Explicit loading point:
# for name, entry_point in discover_reader_entry_points():
#     plugin_class = entry_point.load()  # imports code; may raise ImportError
#     registry.register(name, plugin_class)
```

A production loader should validate the loaded object, handle import failures, detect duplicate names, and make loading policy explicit. Discovery and loading should be separate phases if you want to inspect metadata before importing code.

---

# 7. Advanced registry design

## 7.1 `abc.ABC`, `typing.Protocol`, and `dataclass`

- **`abc.ABC` / `@abstractmethod`:** runtime-enforced abstractness. A class with unresolved abstract methods cannot be instantiated. This is appropriate when runtime contract enforcement matters.
- **`typing.Protocol`:** primarily a structural typing contract for static checkers. A protocol can describe the methods a plugin must provide without requiring inheritance. `@runtime_checkable` enables limited runtime `isinstance()` checks for protocol members; it does not validate signatures or full type compatibility.
- **`@dataclass`:** a class decorator that processes annotations and adds methods after the class body has run. Therefore `__init_subclass__()` sees the subclass before the `@dataclass` transformation. If registration needs dataclass-generated fields or `__init__`, register after dataclass processing with a class decorator, or design the hook to use only class-body metadata.

```python
from dataclasses import dataclass

class DataModelBase:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.hook_saw_dataclass_fields = "__dataclass_fields__" in cls.__dict__

@dataclass
class Event(DataModelBase):
    event_id: int

print(Event.hook_saw_dataclass_fields)
print("__dataclass_fields__" in Event.__dict__)
print(Event(7))
```

Expected output:

```text
False
True
Event(event_id=7)
```

Do not infer runtime conformance from a type annotation or `Protocol` declaration alone. Type checkers and runtime enforce different parts of the contract.

## 7.2 Thread safety

A dictionary is not a complete concurrency policy. If plugin registration can occur concurrently, protect check-and-insert as one operation with a `threading.Lock`; otherwise two threads could both observe a free key before either inserts. Prefer to complete registration during single-threaded startup and then expose a read-only view. Do not execute arbitrary plugin imports while holding a registry lock: imports can trigger nested registration and deadlocks. Load first, then validate and register under a short lock.

## 7.3 A small registry with explicit policy

```python
from threading import RLock

class Registry:
    def __init__(self) -> None:
        self._items: dict[str, type] = {}
        self._lock = RLock()

    def register(self, name: str, plugin: type) -> None:
        if not isinstance(name, str) or not name or name.strip() != name:
            raise ValueError("name must be a non-empty string without surrounding whitespace")
        if not isinstance(plugin, type):
            raise TypeError("plugin must be a class")
        with self._lock:
            if name in self._items:
                raise ValueError(f"duplicate plugin name {name!r}")
            self._items[name] = plugin

    def get(self, name: str) -> type:
        with self._lock:
            try:
                return self._items[name]
            except KeyError:
                raise LookupError(f"unknown plugin {name!r}") from None

    def snapshot(self) -> dict[str, type]:
        with self._lock:
            return self._items.copy()
```

This implementation validates the key and class shape, rejects duplicates, uses a lock around mutations/lookups, and returns a copy for snapshots. A simple dict is sufficient for single-threaded startup; do not add locking unless the lifecycle requires it.

## 7.4 When is a metaclass justified?

| Requirement | First choice | Consider a metaclass when… |
|---|---|---|
| Register/validate each subclass | `__init_subclass__()` | The policy must apply at the class-creation machinery level across complex inheritance |
| Add behavior to one selected class | Class decorator | You need control before/while the namespace becomes a class object |
| Reusable field behavior | Descriptor + `__set_name__()` | You need to control the namespace or coordinate descriptors globally |
| Customize class-body namespace (`__prepare__`) | Metaclass | You need an ordered/special mapping or duplicate-definition tracking while the body executes |
| Customize class object calls (`__call__`) | Metaclass | You deliberately need to alter construction of class instances for every class using that metaclass |
| Build classes from data | `type()` / `types.new_class()` | A metaclass participates in class creation and must control it consistently |

Metaclasses are powerful but increase the complexity of inheritance and metaclass compatibility. `__call__()` on a metaclass affects calling instances of the class object (i.e. instance construction), not ordinary method calls on instances. Use a metaclass only when a class hook, decorator, or descriptor cannot express the requirement clearly.

---

# 8. Testing and production concerns

## 8.1 Isolate global registry state

Tests that create plugin classes mutate registries at import/class-definition time. If test cases share a global registry, one test can affect another. Prefer an injectable registry instance for testability. If the production API uses a global dictionary, snapshot and restore it in a fixture/finally block.

```python
# pytest fixture example
import pytest

@pytest.fixture
def isolated_registry():
    old = Reader.registry.copy()
    Reader.registry.clear()
    try:
        yield Reader.registry
    finally:
        Reader.registry.clear()
        Reader.registry.update(old)
```

This fixture assumes `Reader.registry` is a mutable dictionary. It restores the previous contents even if the test fails. It does not undo import side effects outside that dictionary.

## 8.2 What to test

- Successful registration maps the explicit key to the exact class object.
- Missing and duplicate names fail at class definition time with a useful exception.
- Invalid classes fail before they are used.
- Unknown lookup produces a clear lookup error.
- Cooperative mixins both receive their own keywords and continue through `super()`.
- Abstract intermediate classes are permitted by the chosen convention; concrete classes satisfy the contract.
- Repeated test execution does not leak registry entries.
- Plugin discovery distinguishes metadata enumeration from importing/loading the plugin.

## 8.3 Operational concerns

Document the entry-point group name, identifier rules, conflict policy, expected interface, and compatibility/version policy. Keep plugin loading at a visible startup boundary. Log the plugin identifier and distribution when loading fails, but avoid exposing secrets or dumping arbitrary configuration. Decide whether one bad plugin aborts startup or is isolated and reported. Do not silently skip a required plugin.

---

# 9. Complete plugin-registry project

This project is intentionally small enough to run locally. It uses explicit class-definition keywords, an injectable registry, contract validation, duplicate rejection, and a cooperating hook. Save the code as `plugin_registry_demo.py`.

## 9.1 Implementation

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from threading import RLock
from typing import ClassVar


class PluginRegistry:
    """Thread-safe registry with explicit duplicate rejection."""

    def __init__(self) -> None:
        self._classes: dict[str, type[Plugin]] = {}
        self._lock = RLock()

    def register(self, name: str, plugin: type[Plugin]) -> None:
        if not isinstance(name, str) or not name or name.strip() != name:
            raise ValueError("plugin name must be a non-empty string without surrounding whitespace")
        if not isinstance(plugin, type) or not issubclass(plugin, Plugin):
            raise TypeError("registered object must be a Plugin subclass")
        with self._lock:
            if name in self._classes:
                raise ValueError(f"duplicate plugin name {name!r}")
            self._classes[name] = plugin

    def get(self, name: str) -> type[Plugin]:
        with self._lock:
            try:
                return self._classes[name]
            except KeyError:
                raise LookupError(f"unknown plugin {name!r}") from None

    def snapshot(self) -> dict[str, type[Plugin]]:
        with self._lock:
            return self._classes.copy()


class Plugin(ABC):
    registry: ClassVar[PluginRegistry] = PluginRegistry()
    plugin_name: ClassVar[str]

    def __init_subclass__(cls, *, name: str | None = None,
                          abstract: bool = False, **kwargs) -> None:
        # Cooperate with ABC and any other mixins in the MRO.
        super().__init_subclass__(**kwargs)
        if abstract:
            cls.__abstract_plugin__ = True
            return
        if name is None:
            raise TypeError(f"{cls.__name__} must declare name=... or abstract=True")
        # Validate the contract before registering the class.
        run_method = getattr(cls, "run", None)
        if not callable(run_method) or getattr(run_method, "__isabstractmethod__", False):
            raise TypeError(f"{cls.__name__} must implement callable run()")
        Plugin.registry.register(name, cls)
        cls.plugin_name = name

    @abstractmethod
    def run(self, payload: str) -> str:
        """Process one payload."""


class TextPluginBase(Plugin, abstract=True):
    """Legitimate intermediate class: shares behavior but is not registered."""

    def normalize(self, payload: str) -> str:
        return payload.strip()


class UppercasePlugin(TextPluginBase, name="uppercase"):
    def run(self, payload: str) -> str:
        return self.normalize(payload).upper()


class ReversePlugin(TextPluginBase, name="reverse"):
    def run(self, payload: str) -> str:
        return self.normalize(payload)[::-1]


def main() -> None:
    cls = Plugin.registry.get("uppercase")
    print(cls is UppercasePlugin)
    print(cls().run(" hello "))
    print(Plugin.registry.get("reverse")().run("abc"))
    print(sorted(Plugin.registry.snapshot()))


if __name__ == "__main__":
    main()
```

Expected output:

```text
True
HELLO
cba
['reverse', 'uppercase']
```

### Design notes

- The registry is an instance, which makes isolated registries possible in tests; the base class owns one default instance for the demonstration.
- `name=` is explicit and stable. Duplicate names are rejected, not overwritten.
- `abstract=True` is a framework convention for intentionally unregistered intermediate classes. The class is also abstract by virtue of inheriting the unresolved `run()` method, so Python's ABC machinery prevents direct instantiation.
- The hook calls `super().__init_subclass__()` to cooperate with `ABC`/`ABCMeta` and other bases.
- The hook validates `run` by attribute lookup. If descriptor execution is a concern, use static inspection and a more explicit contract.
- The `abstract=True` keyword is this example framework's opt-out convention. It is intentionally explicit because `__init_subclass__()` runs before `ABCMeta` has finalized the new class's `__abstractmethods__`; do not assume that attribute is already authoritative inside the hook. This project checks the declared `run()` contract directly and uses the explicit marker for intermediate classes.
- Registration happens during the class statement. Merely importing this base module does not import unrelated plugin modules.

## 9.2 Tests

Save as `test_plugin_registry_demo.py` next to the implementation. Run with `python -m pytest -q` (install pytest first if needed).

```python
import pytest

from plugin_registry_demo import Plugin, PluginRegistry, TextPluginBase, UppercasePlugin


@pytest.fixture
def clean_registry():
    registry = PluginRegistry()
    old = Plugin.registry
    Plugin.registry = registry
    try:
        yield registry
    finally:
        Plugin.registry = old
        assert Plugin.registry is old


def test_successful_registration_and_behavior(clean_registry):
    # Existing classes were registered into the original default registry at
    # module import. Register explicitly in this isolated registry for the test.
    clean_registry.register("uppercase", UppercasePlugin)
    assert clean_registry.get("uppercase") is UppercasePlugin
    assert clean_registry.get("uppercase")().run(" hi ") == "HI"


def test_missing_name_rejected():
    with pytest.raises(TypeError, match="must declare name"):
        class MissingName(TextPluginBase):
            def run(self, payload: str) -> str:
                return payload


def test_duplicate_name_rejected(clean_registry):
    clean_registry.register("uppercase", UppercasePlugin)
    with pytest.raises(ValueError, match="duplicate plugin name"):
        clean_registry.register("uppercase", UppercasePlugin)

    # Also verify the automatic class-definition path rejects a duplicate.
    with pytest.raises(ValueError, match="duplicate plugin name"):
        class DuplicateUppercase(TextPluginBase, name="uppercase"):
            def run(self, payload: str) -> str:
                return payload


def test_subclass_is_automatically_registered(clean_registry):
    class LocalPlugin(TextPluginBase, name="local-test"):
        def run(self, payload: str) -> str:
            return payload.upper()

    assert clean_registry.get("local-test") is LocalPlugin
    assert clean_registry.get("local-test")().run("ok") == "OK"


def test_invalid_contract_rejected():
    with pytest.raises(TypeError, match="must implement callable run"):
        class InvalidPlugin(Plugin, name="invalid-contract"):
            pass


def test_invalid_class_definition_identifier_rejected():
    with pytest.raises(ValueError, match="plugin name must be"):
        class EmptyNamePlugin(TextPluginBase, name=""):
            def run(self, payload: str) -> str:
                return payload


def test_lookup_failure(clean_registry):
    with pytest.raises(LookupError, match="unknown plugin"):
        clean_registry.get("missing")


def test_abstract_intermediate_class_is_not_registered():
    assert getattr(TextPluginBase, "__abstract_plugin__", False) is True
    assert "TextPluginBase" not in Plugin.registry.snapshot()
    with pytest.raises(TypeError):
        TextPluginBase()


def test_cooperating_mixins_receive_their_keywords():
    class RegionMixin:
        def __init_subclass__(cls, *, region: str, **kwargs):
            cls.region = region
            super().__init_subclass__(**kwargs)

    class VersionMixin:
        def __init_subclass__(cls, *, version: int, **kwargs):
            cls.version = version
            super().__init_subclass__(**kwargs)

    class Local(RegionMixin, VersionMixin, region="eu", version=3):
        pass

    assert (Local.region, Local.version) == ("eu", 3)


def test_registry_snapshot_is_independent(clean_registry):
    clean_registry.register("uppercase", UppercasePlugin)
    snapshot = clean_registry.snapshot()
    snapshot.clear()
    assert clean_registry.get("uppercase") is UppercasePlugin


def test_invalid_registry_identifiers_are_rejected(clean_registry):
    for invalid in ("", " padded ", None, 42):
        with pytest.raises(ValueError, match="plugin name must be"):
            clean_registry.register(invalid, UppercasePlugin)


def test_non_class_registration_is_rejected(clean_registry):
    with pytest.raises(TypeError, match="must be a Plugin subclass"):
        clean_registry.register("not-a-class", object())


def test_registry_reference_can_be_restored():
    original = Plugin.registry
    replacement = PluginRegistry()
    Plugin.registry = replacement
    try:
        assert Plugin.registry is replacement
    finally:
        Plugin.registry = original
    assert Plugin.registry is original
```

### Test-design caution

The classes declared at module import time have already registered in the original `Plugin.registry`. Replacing `Plugin.registry` later does not retroactively move those classes. Tests above explicitly register the class into the isolated registry where needed; the auto-registration test defines a new class while the fixture's registry is active. The fixture restores the original registry object in `finally`, including when a test fails. Avoid reusing hard-coded keys across tests unless the fixture resets the exact registry instance.

---

# 10. Exercises, solutions, interview questions, and completion checklist

## 10.1 Exercises

1. **Basic hook:** Write a base class that stores `cls.created_by_hook = True` on each subclass.
2. **Keyword contract:** Create `Codec(Base, media_type="application/example")`; reject missing or empty `media_type` for concrete subclasses.
3. **Registry:** Implement `register(name, cls)` with duplicate rejection and a `get(name)` method that raises a domain-specific lookup error.
4. **Mixin cooperation:** Create two mixins that consume `region=` and `version=` and verify both settings survive when a class inherits from both.
5. **Descriptor:** Implement a descriptor that remembers its owner/name and rejects assignment of non-positive integers.
6. **Subclass discovery:** Write a recursive `__subclasses__()` walk and explain why it cannot discover modules that were never imported.
7. **Entry points:** Enumerate an entry-point group and explain when the referenced code executes.
8. **Testing:** Add a fixture that snapshots and restores a global registry even when an assertion fails.

## 10.2 Solutions

### Solution 1

```python
class Base:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.created_by_hook = True

class Child(Base):
    pass

print(Child.created_by_hook)
```

Output: `True`.

### Solution 2

```python
class Codec:
    def __init_subclass__(cls, *, media_type: str | None = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if media_type is None or not media_type.strip():
            if not cls.__dict__.get("__abstract_codec__", False):
                raise TypeError(f"{cls.__name__} needs media_type")
        else:
            cls.media_type = media_type
```

An explicit abstract marker lets intermediate classes omit the value. A dedicated `abstract=True` class keyword is more visible in a larger framework.

### Solution 3

```python
class PluginNotFound(LookupError):
    pass

class Registry:
    def __init__(self):
        self._items = {}

    def register(self, name, cls):
        if name in self._items:
            raise ValueError(f"duplicate name: {name}")
        self._items[name] = cls

    def get(self, name):
        try:
            return self._items[name]
        except KeyError:
            raise PluginNotFound(name) from None
```

For production, validate the identifier and plugin class before insertion, and define whether registration is allowed after startup.

### Solution 4

The `Named` and `Versioned` mixins in section 6.1 are the solution. Each consumes its own keyword and forwards remaining keywords through `super()`.

### Solution 5

```python
class PositiveInt:
    def __set_name__(self, owner, name):
        self.storage = "_" + name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return getattr(instance, self.storage, None)

    def __set__(self, instance, value):
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ValueError("value must be a positive integer")
        setattr(instance, self.storage, value)

class Batch:
    size = PositiveInt()

batch = Batch()
batch.size = 3
print(batch.size)
```

Output: `3`. `bool` is a subclass of `int`, so the explicit boolean rejection avoids accepting `True` as a size.

### Solution 6

Use the `descendants(base)` implementation in section 6.2. It walks only classes already created and still live; imports or entry-point loading are separate discovery steps.

### Solution 7

Use `entry_points(group="myapp.readers")` as shown in section 6.5. Enumeration reads installed distribution metadata; `entry_point.load()` imports and resolves the target object and may execute code.

### Solution 8

Use the `try/finally` snapshot-and-restore fixture in section 8.1. A fixture should restore state even if the test raises an exception.

## 10.3 Interview questions

1. When does `__init_subclass__()` run, and what does `cls` refer to?
2. Why should implementations usually call `super().__init_subclass__(**kwargs)`?
3. How are class-definition keyword arguments consumed across multiple bases?
4. What is the difference between `__init_subclass__()` and a class decorator?
5. What does `__set_name__()` provide to a descriptor, and when is it called?
6. Why does `Base.__subclasses__()` not discover every descendant or unimported plugin?
7. How can a registry accidentally keep dynamically created classes alive?
8. What is the hidden-import problem with import-time registration?
9. What are package entry points, and what happens when `.load()` is called?
10. How do `ABC` and `Protocol` differ in runtime enforcement?
11. Why can `__init_subclass__()` run before `@dataclass` processes the subclass?
12. When might `__prepare__()` or metaclass `__call__()` justify a metaclass?
13. What policy should a registry use for duplicate names and API versions?
14. How should a registry be tested without cross-test pollution?

## 10.4 Completion checklist

- [ ] I can describe the subclass creation hook and explain the role of `cls`.
- [ ] I can consume class keywords and forward the rest cooperatively.
- [ ] I can reject invalid subclasses with clear `TypeError` messages.
- [ ] I can register by explicit key and reject duplicate names.
- [ ] I understand descriptors and `__set_name__()` timing.
- [ ] I can explain direct versus recursive `__subclasses__()` behavior.
- [ ] I understand why import-time registration requires importing the plugin module.
- [ ] I can distinguish `ABC` runtime checks from `Protocol` static typing.
- [ ] I can isolate registry state in tests.
- [ ] I can explain when entry points and metaclasses are appropriate.
- [ ] I have run the project and its tests in a Python 3.12+ environment.

---

## Key takeaways

- `__init_subclass__()` is a class-definition hook, not an instance hook.
- `cls` is the newly created subclass; class keywords make configuration explicit.
- Cooperative inheritance requires consuming owned keywords and forwarding the rest with `super()`.
- Registries need an explicit identity policy, duplicate handling, lookup errors, and test isolation.
- `__set_name__()` connects descriptors to their class-body attribute name.
- `__subclasses__()` reports already-created live class relationships; it is not package discovery.
- Entry points make installed plugin discovery explicit, but loading still imports executable code.
- Use metaclasses only when control over class creation itself is required.
