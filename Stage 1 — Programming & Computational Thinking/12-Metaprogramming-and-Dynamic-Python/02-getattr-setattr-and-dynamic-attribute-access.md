# Dynamic Attribute Access in Python

> **Roadmap location:** Stage 1 — Programming & Computational Thinking → `12-Metaprogramming-and-Dynamic-Python/` → `02-getattr-setattr-and-dynamic-attribute-access.md`  
> **Compatibility baseline:** Python 3.12+  
> **Scope:** Dynamic attribute lookup, assignment, deletion, safe dispatch, configuration wrappers, proxies, lazy access, typing, and production risks.

## Learning objectives

By the end, you should be able to explain normal attribute lookup, use `getattr()`, `setattr()`, `hasattr()`, and `delattr()`, implement `__getattr__`, `__setattr__`, `__delattr__`, `__dir__`, and (only when necessary) `__getattribute__`, prevent recursion, design allow-listed dispatch, build a read-only nested configuration view, understand proxies and special-method lookup, implement module-level lazy imports, and test interactions with initialization, copying, and pickling.

## Prerequisites and setup

You should understand classes, inheritance, properties/descriptors, exceptions, dictionaries, functions, and basic type hints. Save each complete example in a `.py` file and run it with `python example.py`. Check the version with `python --version`.

**Important boundary:** Python attribute access is programmable behavior, not a passive dictionary read. A property, descriptor, `__getattribute__`, `__getattr__`, or `__setattr__` can execute arbitrary code. Examples involving untrusted objects are not sandboxing techniques.

# 1. Beginner: normal dynamic access

## 1.1 `getattr`, `setattr`, `hasattr`, and `delattr`

These built-ins let code access an attribute when its name is held in a string.

```python
class Job:
    def __init__(self) -> None:
        self.status = "queued"

    def handle_created(self, event_id: str) -> str:
        return f"created:{event_id}"

job = Job()
name = "status"

print(getattr(job, name))             # queued
setattr(job, "status", "running")
print(job.status)                     # running
print(hasattr(job, "status"))         # True
delattr(job, "status")
print(hasattr(job, "status"))         # False
print(getattr(job, "missing", "N/A")) # N/A
```

- `getattr(obj, name)` performs ordinary attribute lookup; without a default it raises `AttributeError` when lookup reports the attribute missing.
- `getattr(obj, name, default)` returns `default` when lookup raises `AttributeError`. This can also hide an `AttributeError` raised inside custom lookup logic; it does not prove the attribute is conceptually absent.
- `setattr(obj, name, value)` performs ordinary assignment semantics, including descriptors and a custom `__setattr__`.
- `delattr(obj, name)` performs ordinary deletion semantics, including descriptors and custom `__delattr__`.
- `hasattr(obj, name)` performs attribute lookup and returns `False` if that lookup raises `AttributeError`. It may execute code and can conceal a real bug inside a property.

Use these APIs for controlled names from configuration, protocol adapters, and dispatch. If the attribute name is fixed in source, ordinary syntax (`obj.status`) is simpler and easier for static tools.

### Why `hasattr()` can mislead

```python
class Broken:
    @property
    def value(self) -> int:
        raise AttributeError("bug inside getter")

b = Broken()
print(hasattr(b, "value"))  # False: the getter's AttributeError is also suppressed
assert getattr(b, "value", "fallback") == "fallback"  # same masking applies to getattr's default

class BrokenDifferently:
    @property
    def value(self) -> int:
        raise RuntimeError("operational failure")

try:
    hasattr(BrokenDifferently(), "value")
except RuntimeError:
    print("non-AttributeError propagates")
else:
    raise AssertionError("hasattr must not suppress RuntimeError")
```

The property exists, but its getter failed with `AttributeError`; `hasattr` cannot distinguish this from a genuinely missing attribute. A `ValueError`, `RuntimeError`, or other non-`AttributeError` raised during lookup is **not** suppressed and propagates to the caller. If this distinction matters, inspect the class definition or redesign the property to raise a more appropriate exception for operational failure. Do not use `hasattr()` as a side-effect-free probe.

### Boundary tests

```python
class Sample:
    value = 3

s = Sample()
assert getattr(s, "value") == 3
assert hasattr(s, "value")
setattr(s, "extra", 8)
assert vars(s) == {"extra": 8}
delattr(s, "extra")
assert not hasattr(s, "extra")

try:
    getattr(s, "missing")
except AttributeError:
    pass
else:
    raise AssertionError("missing lookup should fail")

try:
    delattr(s, "missing")
except AttributeError:
    pass
else:
    raise AssertionError("deleting a missing attribute should fail")
```

## 1.2 How Python finds an attribute

For ordinary instances, lookup involves the object's type, descriptors, the instance namespace (if present), and the class's method resolution order (MRO). A simplified rule for normal instance lookup is:

1. A data descriptor on the class (for example, a `property` with a setter) takes precedence.
2. Otherwise, an instance attribute can take precedence over a non-data descriptor or ordinary class attribute.
3. A non-data descriptor such as a normal function can bind to a method.
4. If ordinary lookup fails, `__getattr__(self, name)` may provide a fallback.

This is a conceptual summary, not a complete substitute for the data model specification: custom `__getattribute__`, metaclasses, and descriptor details affect exact behavior.

```python
class Example:
    label = "class value"

    @property
    def guarded(self) -> str:
        return "property value"

e = Example()
e.label = "instance value"
print(e.label)      # instance value
print(e.guarded)    # property value
print(type(e).__mro__[0].__name__)  # Example
```

## 1.3 Dynamic method dispatch

Dynamic dispatch chooses a handler based on a string. A naive implementation builds an attribute name and calls it:

```python
class Handler:
    def handle_created(self, event_id: str) -> str:
        return f"created {event_id}"

    def handle_deleted(self, event_id: str) -> str:
        return f"deleted {event_id}"

    def dispatch(self, kind: str, event_id: str) -> str:
        method = getattr(self, f"handle_{kind}", None)
        if method is None or not callable(method):
            raise ValueError(f"unsupported event: {kind!r}")
        return method(event_id)

handler = Handler()
print(handler.dispatch("created", "evt-7"))  # created evt-7
```

This is better than blindly calling any name, but still uses string-to-attribute resolution. A safer explicit dispatch table is shown in Section 3.2. Never assume that a user-controlled string is safe merely because it is used as an attribute name.

# 2. Intermediate: customize attribute behavior

## 2.1 `__getattr__`: fallback only

Python calls `__getattr__(self, name)` only after normal lookup fails with `AttributeError`. It is suitable for computed fallback attributes, compatibility aliases, lazy values, and dictionary-backed views.

```python
class Fallback:
    def __init__(self) -> None:
        self.present = 10

    def __getattr__(self, name: str) -> str:
        print(f"fallback:{name}")
        if name == "label":
            return "generated"
        raise AttributeError(f"{type(self).__name__!s} has no attribute {name!r}")

x = Fallback()
print(x.present)  # 10; __getattr__ is not called
print(x.label)    # fallback:label, then generated
try:
    x.unknown
except AttributeError as exc:
    print(type(exc).__name__)  # AttributeError
```

**Why it exists:** it adds behavior for names not otherwise supplied without replacing the entire lookup mechanism.

**Use it when:** a small, documented set of missing names maps to a backing store or lazy provider.

**Prefer a simpler alternative when:** a normal property, explicit method, or mapping lookup communicates the interface more clearly.

**Common failure:** returning a value for every unknown name makes typos appear valid, breaks `hasattr`, can confuse `copy`/`pickle` and debuggers, and may make introspection misleading. Unknown names should normally raise `AttributeError`.

## 2.2 `__setattr__` and `__delattr__`

`__setattr__(self, name, value)` is called for every ordinary assignment such as `obj.x = 1`. `__delattr__(self, name)` is called for ordinary deletion. Inside either method, assigning/deleting through the same syntax can call the override again and recurse.

```python
class Tracked:
    def __init__(self, value: int) -> None:
        # Calls this class's __setattr__ during initialization.
        self.value = value

    def __setattr__(self, name: str, value: object) -> None:
        print(f"setting {name}")
        if name == "value" and not isinstance(value, int):
            raise TypeError("value must be int")
        object.__setattr__(self, name, value)

    def __delattr__(self, name: str) -> None:
        if name == "value":
            raise AttributeError("value cannot be deleted")
        object.__delattr__(self, name)

t = Tracked(4)       # setting value
print(t.value)       # 4
try:
    t.value = "bad"
except TypeError as exc:
    print(type(exc).__name__)  # TypeError
try:
    del t.value
except AttributeError as exc:
    print(type(exc).__name__)  # AttributeError
```

`object.__setattr__(self, name, value)` delegates to the base implementation and avoids re-entering this class's override. `super().__setattr__` is appropriate in cooperative multiple inheritance when each class in the MRO participates correctly. `object.__setattr__` is a direct escape hatch for a class deliberately implementing its own storage semantics. Neither is a universal solution for every custom descriptor or immutable object.

### Recursion failure (do not run as an unguarded example)

```python
class Broken:
    def __setattr__(self, name: str, value: object) -> None:
        self.name = value  # calls Broken.__setattr__ again: recursion
```

The safe pattern is `object.__setattr__(self, name, value)` or a separate backing store accessed without recursively invoking the same override. Similarly, `del self.name` inside `__delattr__` recursively calls `__delattr__`.

### Initialization order

`__init__` uses normal assignment, so an override is active while initialization runs. If an override depends on `_ready` or `_data`, initialize that state first using `object.__setattr__`, or ensure the override explicitly handles the pre-initialized state.

```python
class SafeInit:
    def __init__(self, value: int) -> None:
        object.__setattr__(self, "_ready", False)
        object.__setattr__(self, "_value", value)
        object.__setattr__(self, "_ready", True)

    def __setattr__(self, name: str, value: object) -> None:
        if not object.__getattribute__(self, "_ready"):
            object.__setattr__(self, name, value)
            return
        if name == "value":
            object.__setattr__(self, "_value", value)
            return
        raise AttributeError(f"cannot set {name!r}")

    @property
    def value(self) -> int:
        return object.__getattribute__(self, "_value")

obj = SafeInit(12)
obj.value = 13
assert obj.value == 13
try:
    obj.other = 1
except AttributeError:
    pass
else:
    raise AssertionError("unknown assignment should be rejected")
```

In real classes, avoid overriding assignment unless validation, immutability, or storage abstraction genuinely requires it. Dataclasses, properties, and explicit setter methods are often easier to maintain.

### Write-once attributes

A write-once field accepts its initial value but rejects later reassignment. The implementation below uses a private backing field and `object.__getattribute__` to check whether it already exists. This example intentionally supports only the `token` field; a property or a small explicit setter is often clearer in production.

```python
class WriteOnce:
    def __init__(self, token: str) -> None:
        object.__setattr__(self, "_token", token)

    @property
    def token(self) -> str:
        return object.__getattribute__(self, "_token")

    def __setattr__(self, name: str, value: object) -> None:
        if name != "token":
            raise AttributeError(f"cannot assign {name!r}")
        try:
            object.__getattribute__(self, "_token")
        except AttributeError:
            object.__setattr__(self, "_token", value)
            return
        raise AttributeError("token is write-once")

item = WriteOnce("initial")
assert item.token == "initial"
try:
    item.token = "replacement"
except AttributeError:
    pass
else:
    raise AssertionError("write-once field was reassigned")
```

The `__init__` assignment is performed through `object.__setattr__` deliberately, so construction does not depend on the public reassignment path. If a write-once field must also survive deserialization or support copying, define and test those lifecycle rules explicitly.

## 2.3 `__dir__` and discoverability

`dir(obj)` asks for a list of useful names and may use `obj.__dir__()`. A custom `__dir__` helps interactive autocomplete discover dynamic attributes; it does not create those attributes or make them a stable public API.

```python
class DynamicRecord:
    _fields = {"name": "Asha", "region": "ap-south-1"}

    def __getattr__(self, name: str) -> object:
        try:
            return self._fields[name]
        except KeyError:
            raise AttributeError(name) from None

    def __dir__(self) -> list[str]:
        return sorted(set(super().__dir__()) | set(self._fields))

record = DynamicRecord()
assert record.name == "Asha"
assert "region" in dir(record)
assert "missing" not in dir(record)
```

Keep `__dir__` cheap and deterministic. Do not make it perform network requests, load secrets, or enumerate sensitive internal names.

## 2.4 Attribute-style configuration: trade-offs and collisions

Attribute-style configuration (`cfg.database.host`) can be convenient for trusted, schema-like data. A naive wrapper can collide with its own methods: if a key is named `items`, `keys`, or `_data`, ordinary class attributes may win before `__getattr__` runs. Keep mapping access available for all keys and document that attribute access is a convenience, not a complete mapping replacement.

The following wrapper is **read-only at its public interface**, recursively wraps nested mappings, returns immutable sequences for list-like values, and rejects attribute assignment/deletion. It defensively copies the input mapping into private storage. As always in Python, this is not a security boundary against hostile code running in the same process.

```python
from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value

class ConfigView:
    __slots__ = ("__data",)

    def __init__(self, data: Mapping[str, Any]) -> None:
        object.__setattr__(self, "_ConfigView__data", _freeze(dict(data)))

    def __getattr__(self, name: str) -> Any:
        data = object.__getattribute__(self, "_ConfigView__data")
        try:
            value = data[name]
        except KeyError:
            raise AttributeError(name) from None
        return ConfigView(value) if isinstance(value, Mapping) else value

    def __getitem__(self, key: str) -> Any:
        data = object.__getattribute__(self, "_ConfigView__data")
        value = data[key]
        return ConfigView(value) if isinstance(value, Mapping) else value

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("configuration is read-only")

    def __delattr__(self, name: str) -> None:
        raise AttributeError("configuration is read-only")

    def __dir__(self) -> list[str]:
        data = object.__getattribute__(self, "_ConfigView__data")
        return sorted(set(super().__dir__()) | {k for k in data if isinstance(k, str) and k.isidentifier()})

raw = {
    "database": {"host": "db.internal", "port": 5432},
    "__getitem__": "this key collides with a real wrapper method",
    "features": ["search", "export"],
}
cfg = ConfigView(raw)
raw["database"]["host"] = "changed after wrapping"
print(cfg.database.host)       # db.internal: nested input was copied/frozen
print(cfg["__getitem__"])      # this key collides with a real wrapper method
assert callable(cfg.__getitem__)  # normal class lookup wins for attribute syntax
print(cfg.features)            # ('search', 'export')
assert "database" in dir(cfg)
try:
    cfg.database.host = "changed"
except AttributeError:
    pass
else:
    raise AssertionError("nested configuration should be read-only")
try:
    cfg.missing
except AttributeError:
    pass
else:
    raise AssertionError("unknown configuration key should fail")
try:
    cfg.database = {}
except AttributeError:
    print("read-only")         # read-only
```

**Limitations:**

- `cfg.items` refers to a class method if the wrapper defines `items`; use `cfg["items"]` to access colliding keys. This implementation intentionally does not define dictionary methods such as `items()`, but names can still collide with methods added later or inherited attributes.
- The wrapper recursively freezes mappings and common built-in containers, but arbitrary custom mutable objects stored as values remain references. For truly immutable configuration, validate and convert values to an explicitly supported set of scalar/container types.
- `MappingProxyType` prevents mutation through that view, but does not by itself freeze objects nested inside it; `_freeze` handles common containers recursively.
- This implementation intentionally does **not** promise generic copy/pickle support: `copy.copy(cfg)` can fail because the public setter rejects reconstruction, `copy.deepcopy(cfg)` encounters `mappingproxy`, and pickling is unsupported. If serialization is required, define an explicit conversion to a supported plain-data representation and test that contract rather than assuming the wrapper is serializable.
- Attribute access is limited to keys that do not collide with normal attributes. Bracket access is unambiguous.
- This is not protection against hostile Python code: name-mangled fields can still be reached deliberately, and Python does not enforce private attributes as a security boundary.

For most production configuration, a typed dataclass, Pydantic model, or ordinary mapping is preferable when schema validation, IDE support, serialization, and clear errors matter more than dotted access.

## 2.5 Explicit dispatch tables

For event handling, an allow-list dispatch table is usually safer and easier to audit than constructing arbitrary attribute names.

```python
from collections.abc import Callable

class EventDispatcher:
    def __init__(self) -> None:
        self._handlers: dict[str, Callable[[str], str]] = {
            "created": self.handle_created,
            "deleted": self.handle_deleted,
        }

    def handle_created(self, event_id: str) -> str:
        return f"created:{event_id}"

    def handle_deleted(self, event_id: str) -> str:
        return f"deleted:{event_id}"

    def dispatch(self, event_name: str, event_id: str) -> str:
        if not isinstance(event_name, str):
            raise TypeError("event_name must be a string")
        try:
            handler = self._handlers[event_name]
        except KeyError:
            raise ValueError(f"unsupported event: {event_name!r}") from None
        return handler(event_id)

dispatcher = EventDispatcher()
assert dispatcher.dispatch("created", "42") == "created:42"
try:
    dispatcher.dispatch("__class__", "42")
except ValueError:
    print("rejected")  # rejected
```

The registry itself should not be writable by untrusted callers. If events are extensible, expose a controlled registration method that validates names, callables, and ownership. The dispatch table makes the allowed operation set explicit.

# 3. Advanced: intercept lookup and build reliable abstractions

## 3.1 `__getattribute__` versus `__getattr__`

`__getattribute__(self, name)` runs for essentially every ordinary instance attribute access. It must delegate carefully; calling `self.other` inside it normally starts the override again. `object.__getattribute__(self, name)` performs the standard lookup path without recursively re-entering the override for that same lookup. If it raises `AttributeError`, Python may then call `__getattr__`.

```python
class Trace:
    def __getattribute__(self, name: str) -> object:
        print(f"lookup:{name}")
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            print(f"missing:{name}")
            raise

    def __getattr__(self, name: str) -> str:
        print(f"fallback:{name}")
        if name == "dynamic":
            return "from fallback"
        raise AttributeError(name)

    def __init__(self) -> None:
        self.value = 7

x = Trace()
print(x.value)
# lookup:value
# 7
print(x.dynamic)
# lookup:dynamic
# missing:dynamic
# fallback:dynamic
# from fallback
```

Do not read `self._internal` inside `__getattribute__` to reach internal state; that triggers the override again. Use `object.__getattribute__(self, "_internal")`. Avoid this hook unless you need cross-cutting behavior such as transparent proxies or auditing; properties and `__getattr__` are simpler for most use cases.

### Why “return `None` for everything” is dangerous

```python
class Dangerous:
    def __getattr__(self, name: str) -> None:
        return None

d = Dangerous()
print(d.typo)             # None, instead of an AttributeError
print(hasattr(d, "typo")) # True
```

This silently turns misspellings into valid-looking values and breaks feature detection, error reporting, autocomplete, and tools that rely on missing attributes raising `AttributeError`. Prefer raising `AttributeError` for unsupported names.

## 3.2 Proxies and special-method lookup

A proxy can delegate ordinary attributes with `__getattr__`, but Python's implicit special operations often look up methods on the object's **type**, not through ordinary instance fallback. Therefore `__getattr__` alone does not make `len(proxy)` or `proxy + other` work.

```python
class Target:
    def __init__(self, values: list[int]) -> None:
        self.values = values

    def __len__(self) -> int:
        return len(self.values)

class IncompleteProxy:
    def __init__(self, target: Target) -> None:
        self._target = target

    def __getattr__(self, name: str) -> object:
        return getattr(self._target, name)

target = Target([1, 2, 3])
proxy = IncompleteProxy(target)
print(proxy.values)  # [1, 2, 3]
try:
    len(proxy)
except TypeError:
    print("len not forwarded")  # len not forwarded
```

Forward the special methods that your proxy promises to support:

```python
class SequenceProxy:
    def __init__(self, target: list[int]) -> None:
        self._target = target

    def __getattr__(self, name: str) -> object:
        return getattr(self._target, name)

    def __len__(self) -> int:
        return len(self._target)

    def __iter__(self):
        return iter(self._target)

p = SequenceProxy([2, 4, 6])
assert len(p) == 3
assert list(p) == [2, 4, 6]
```

A general transparent proxy is difficult: operators, context managers, async protocols, hashing, equality, pickling, and introspection may all need explicit forwarding. Define the exact protocol you support instead of claiming universal transparency.

## 3.3 Lazy attributes and module-level `__getattr__` (PEP 562)

A module can define module-level `__getattr__(name)` to supply attributes missing from its global namespace. This is useful for lazy imports and deprecation shims. It applies to attribute access on the module object; it does not intercept every global-name lookup performed inside the module itself.

A minimal module file `lazy_api.py`:

```python
"""Small example of a lazily exposed name."""
def __getattr__(name: str):
    if name == "heavy_tool":
        from pathlib import Path
        value = Path
        globals()[name] = value  # cache after first lookup
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

def __dir__():
    return sorted(set(globals()) | {"heavy_tool"})
```

Usage in another file:

```python
import lazy_api
assert "heavy_tool" in dir(lazy_api)
assert lazy_api.heavy_tool.__name__ == "Path"
try:
    lazy_api.not_a_real_name
except AttributeError:
    print("missing")  # missing
```

PEP 562 is available in Python 3.7+, so it is available under the Python 3.12+ baseline. Module-level `__getattr__` does not override names already present in the module dictionary. Cache lazily loaded names only when doing so is consistent with the API and import semantics. Lazy imports can defer latency and errors until first use, so document that trade-off.

## 3.4 `copy`, `pickle`, and object lifecycle

Copying, pickling, debuggers, and serializers may probe attributes such as `__getstate__`, `__setstate__`, `__deepcopy__`, or reduction hooks. A broad `__getattr__` that returns fabricated values can confuse these mechanisms. Correct missing-name behavior is to raise `AttributeError`; custom serialization should be explicit and tested.

A particularly common recursion bug occurs when `__getattr__` tries to reach backing state through ordinary lookup before that state exists:

```python
class BrokenStore:
    def __getattr__(self, name: str) -> object:
        # If _data is absent, evaluating self._data invokes __getattr__ again.
        return self._data[name]
```

Do not execute this intentionally broken class: `obj.missing` can recurse until `RecursionError`. Initialize backing state before any hook depends on it, and use `object.__getattribute__(self, "_data")` inside lookup hooks when direct access to the already-initialized storage is required. For genuinely missing user-facing names, raise `AttributeError` rather than fabricating values. This also lets copy/pickle machinery correctly detect that a protocol hook is absent.

```python
import copy
import pickle

class Settings:
    def __init__(self, mode: str) -> None:
        self.mode = mode

    def __getattr__(self, name: str) -> object:
        if name == "legacy_mode":
            return self.mode
        raise AttributeError(name)

original = Settings("safe")
clone = copy.copy(original)
restored = pickle.loads(pickle.dumps(original))
assert clone.mode == "safe"
assert restored.mode == "safe"
assert original.legacy_mode == "safe"
```

Pickling typically requires importable classes and pickle-compatible state. It must not be used to load untrusted data: unpickling can execute code. Objects containing locks, sockets, open files, or runtime-only resources may need custom state handling or may not be pickleable. Do not assume every proxy or dynamic wrapper will copy or pickle correctly without dedicated tests.

## 3.5 Typing dynamic attributes

Dynamic attribute APIs are difficult for static type checkers because a name resolved at runtime may not be visible to them.

- **`Protocol`:** describe the attributes callers are guaranteed to use.
- **`TYPE_CHECKING`:** provide imports or declarations for type checkers without executing them at runtime.
- **Stub files (`.pyi`):** publish a static interface for a dynamic library.
- **`Literal`:** constrain a finite set of accepted dynamic names.
- **Explicit methods or mappings:** often provide the best editor support and clearest contracts.

```python
from typing import Literal, Protocol

class HasStatus(Protocol):
    status: str

EventName = Literal["created", "deleted"]

def display_status(item: HasStatus) -> str:
    return item.status

def dispatch_name(name: EventName) -> str:
    return name.upper()

assert dispatch_name("created") == "CREATED"
# A type checker should reject dispatch_name("updated"),
# although Python itself does not enforce Literal at runtime.
```

`Protocol` is a static structural contract, not a runtime guarantee unless an appropriate runtime-checkable protocol is used—and runtime protocol checks do not validate all type details. `Literal` is also a static constraint; validate untrusted input at runtime.

### `TYPE_CHECKING` and stub files

`typing.TYPE_CHECKING` is `False` at runtime and treated as `True` by static type checkers. It can guard imports used only for annotations, while a local runtime import keeps an optional dependency lazy. With postponed annotations, a quoted annotation also avoids evaluating the imported type at function-definition time:

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from expensive_client import Client

def connect() -> Client:
    from expensive_client import Client
    return Client()
```

This pattern assumes `expensive_client.Client` is installed when `connect()` is called. `TYPE_CHECKING` does not install the dependency or make the runtime import safe; it only prevents the type-checking-only import from running at module import time. Because `Client` is not bound in the runtime module namespace, tools such as `typing.get_type_hints(connect)` may need an explicit namespace or a runtime-visible type import to resolve the annotation. Do not assume a type-checking-only import is available to runtime introspection.

For a library with dynamic runtime behavior, a `.pyi` stub can declare the stable public surface for editors and type checkers. For example, a `config_api.pyi` file could contain:

```python
class DatabaseSettings:
    host: str
    port: int

class Config:
    database: DatabaseSettings
    features: tuple[str, ...]
    def __getitem__(self, key: str) -> object: ...
```

A stub should describe the supported contract, not every implementation detail. Explicitly listing finite names gives better checking than a blanket `__getattr__(name: str) -> Any`, which effectively permits typos. Keep the runtime implementation and stub synchronized, and validate actual runtime inputs separately.

## 3.6 User-controlled names and security

Do not let a caller choose arbitrary attributes on sensitive objects. An attacker may discover internals, trigger properties, reach methods, or cause unexpected state changes. Avoid exposing `getattr(secret_object, user_input)` or `setattr(config, user_input, value)` as a generic public API.

Use allow-lists and explicit validation:

```python
class PublicProfile:
    def __init__(self) -> None:
        self.display_name = "Asha"
        self._api_token = "never expose this"

    def public_value(self, name: str) -> str:
        allowed = {"display_name"}
        if name not in allowed:
            raise ValueError("field is not public")
        value = getattr(self, name)
        if not isinstance(value, str):
            raise TypeError("unexpected field type")
        return value

profile = PublicProfile()
assert profile.public_value("display_name") == "Asha"
try:
    profile.public_value("_api_token")
except ValueError:
    print("blocked")  # blocked
```

An allow-list is stronger than trying to block names beginning with underscores. It defines exactly what the caller is allowed to request. Still, if attributes have side effects, keep the allow-listed getters simple and controlled. Python objects are not security sandboxes; isolate genuinely untrusted code in a separate process with operating-system controls.

# 4. Production engineering guidance

## 4.1 Common failure modes

| Failure | Why it happens | Better approach |
|---|---|---|
| Infinite recursion in `__setattr__` | Assignment inside the override calls it again | Use `object.__setattr__` or a deliberate backing store |
| `hasattr()` hides a property bug | It suppresses `AttributeError` from lookup | Avoid probing side-effectful properties; inspect known definitions or redesign errors |
| Unknown names return `None` | Typos become valid-looking values | Raise `AttributeError` |
| Configuration key collides with a method | Normal class lookup wins before `__getattr__` | Use `cfg[key]` for collisions; prefer mapping/schema models |
| Proxy fails under `len()` | Implicit special methods are looked up on the type | Explicitly implement each supported protocol method |
| Dynamic dispatch exposes internals | User input becomes an unrestricted attribute name | Use an allow-list dispatch table |
| Lazy access hides import errors | Work is deferred until first access | Document latency/failure behavior and test first access |
| Pickling breaks | Dynamic hooks or non-pickleable state interfere | Test copy/pickle explicitly; define state behavior if necessary |
| Static type checking loses names | Names exist only at runtime | Protocols, stubs, `Literal`, explicit APIs |

## 4.2 Performance

- Ordinary attribute access is optimized heavily by Python. In CPython, adaptive/specializing bytecode can optimize common attribute access patterns; custom `__getattribute__` can inhibit or reduce those optimizations and adds work to every access. Exact effects depend on the interpreter and workload.
- `__getattr__` adds work only on failed normal lookups, but repeated missing-name checks can still be costly.
- Dynamic dispatch table lookup is typically straightforward and easier to audit than repeated string-built attribute resolution.
- Avoid doing I/O, imports, schema scans, or logging with expensive representations inside lookup hooks.
- Benchmark representative workloads before optimizing. Do not use fragile lookup tricks to save negligible time.

## 4.3 Compatibility and design boundaries

- Examples target Python 3.12+. PEP 562 module-level `__getattr__` and `__dir__` are supported well before that baseline.
- Attribute lookup semantics are part of Python's data model, but behavior involving descriptors, custom metaclasses, special methods, and extension types can be subtle.
- Private names such as `_internal` and name-mangled names are conventions, not access control.
- Type annotations and static typing do not automatically validate runtime input.
- `copy`/`pickle` behavior depends on the object's state and protocol support; test the concrete object and interpreter versions you support.
- Never treat introspection or dynamic attribute access as isolation from hostile Python code.

# 5. Practical mini-project: safe event router

Build an event router that dispatches only registered events, rejects non-string and unknown names, and does not expose arbitrary object methods.

```python
from collections.abc import Callable
from typing import Final

Handler = Callable[[dict[str, object]], str]

class EventRouter:
    _ALLOWED: Final[frozenset[str]] = frozenset({"created", "deleted"})

    def __init__(self) -> None:
        self._handlers: dict[str, Handler] = {
            "created": self._created,
            "deleted": self._deleted,
        }

    @staticmethod
    def _created(payload: dict[str, object]) -> str:
        return f"created:{payload.get('id', 'unknown')}"

    @staticmethod
    def _deleted(payload: dict[str, object]) -> str:
        return f"deleted:{payload.get('id', 'unknown')}"

    def dispatch(self, name: str, payload: dict[str, object]) -> str:
        if not isinstance(name, str):
            raise TypeError("event name must be str")
        if name not in self._ALLOWED:
            raise ValueError(f"unsupported event: {name!r}")
        handler = self._handlers[name]
        return handler(payload)

router = EventRouter()
assert router.dispatch("created", {"id": 9}) == "created:9"
assert router.dispatch("deleted", {"id": 9}) == "deleted:9"
for bad_name in ("__class__", "_created", "updated"):
    try:
        router.dispatch(bad_name, {"id": 9})
    except ValueError:
        pass
    else:
        raise AssertionError(f"{bad_name!r} should be rejected")
try:
    router.dispatch(7, {})
except TypeError:
    pass
else:
    raise AssertionError("non-string name should be rejected")
print("router tests passed")
```

**Design review:** The allow-list is the policy; the dictionary is the implementation. In a larger system, validate payload schema, control who can register handlers, decide how handler exceptions propagate, and use structured logging. Do not expose a generic `getattr` endpoint as a substitute for an event API.

# 6. Exercises

Attempt each exercise before reading the solutions.

1. Write a class whose property raises `AttributeError`. Show why `hasattr()` returns `False`, and explain why that does not prove the property is absent.
2. Implement `__setattr__` to validate that `port` is an integer from 1 to 65535. Avoid recursion and test invalid values.
3. Implement `__getattr__` for a finite set of aliases. Confirm unknown aliases raise `AttributeError`.
4. Explain why a proxy with `__getattr__` may support `proxy.name` but fail under `len(proxy)`. Add `__len__`.
5. Modify the configuration wrapper test so that a key named `database` is available by attribute, while keys colliding with methods remain accessible by bracket lookup.
6. Explain why returning `None` from `__getattr__` is dangerous. Write a negative test that verifies unknown names fail.
7. Extend the event router with an `archived` event without allowing arbitrary handler names.
8. Test `copy.copy` and pickle round-tripping for a dynamic wrapper. State any assumptions about picklability.
9. Add a `Protocol` for an object with a `status` attribute and use it in a typed function.
10. Explain why an allow-list is better than merely rejecting names beginning with `_`.

# 7. Exercise solutions

## Solution 1: `hasattr`

```python
class BrokenProperty:
    @property
    def value(self) -> int:
        raise AttributeError("getter bug")

obj = BrokenProperty()
assert not hasattr(obj, "value")
try:
    obj.value
except AttributeError as exc:
    assert "getter bug" in str(exc)
```

`hasattr` suppresses `AttributeError` from the entire lookup path, including the property getter. The property exists, but its getter fails.

## Solution 2: validated assignment

```python
class Server:
    def __init__(self, port: int) -> None:
        object.__setattr__(self, "port", port)

    def __setattr__(self, name: str, value: object) -> None:
        if name == "port":
            if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= 65535:
                raise ValueError("port must be an integer from 1 to 65535")
        object.__setattr__(self, name, value)

server = Server(8080)
server.port = 443
assert server.port == 443
for bad in (0, 65536, "80", True):
    try:
        server.port = bad
    except ValueError:
        pass
    else:
        raise AssertionError(f"invalid port accepted: {bad!r}")
```

`bool` is a subclass of `int`, so the explicit exclusion prevents `True` from being accepted as port 1.

## Solution 3: finite fallback

```python
class Aliases:
    _values = {"old_name": "new value"}

    def __getattr__(self, name: str) -> str:
        try:
            return self._values[name]
        except KeyError:
            raise AttributeError(name) from None

a = Aliases()
assert a.old_name == "new value"
try:
    a.typo
except AttributeError:
    pass
else:
    raise AssertionError("unknown alias should fail")
```

## Solution 4: special methods

`len(obj)` uses the type's special-method protocol, not a general search through `obj.__getattr__`. Implement `__len__` on the proxy class and delegate to the target explicitly.

## Solution 5: configuration collisions

Use `cfg["items"]` for a key that could collide with a wrapper method. Dotted access is a convenience only for non-colliding identifiers. A mapping or schema model is the better interface when every key must be represented unambiguously.

## Solution 6: missing names

```python
class Strict:
    def __getattr__(self, name: str) -> object:
        raise AttributeError(name)

strict = Strict()
assert not hasattr(strict, "missing")
try:
    strict.missing
except AttributeError:
    pass
else:
    raise AssertionError("missing attribute did not fail")
```

## Solution 7: safe extension

Add `"archived": self._archived` to the explicit registry and implement `_archived`; add `"archived"` to the allowed set. Test both the new valid name and an unrelated invalid name. Do not derive the callable from arbitrary user input.

## Solution 8: copying and pickle

Use the runnable `Settings` example in Section 3.4. Pickle only trusted data and importable classes. If a class stores unpickleable resources, define and test explicit state handling or avoid pickling that object.

## Solution 9: `Protocol`

```python
from typing import Protocol

class HasStatus(Protocol):
    status: str

def status_text(value: HasStatus) -> str:
    return value.status
```

Static type checkers can accept unrelated classes that satisfy the protocol structurally. Runtime behavior still depends on the actual object.

## Solution 10: allow-list

Rejecting underscore-prefixed names only blocks one naming convention. Public or inherited methods can still be dangerous to expose. An allow-list declares exactly which fields the caller may request.

# 8. Interview and reasoning questions

1. Why does `hasattr()` execute code, and which bug does it sometimes conceal?
2. What is the difference between `__getattr__` and `__getattribute__`?
3. Why must `__setattr__` avoid `self.name = value` for its own storage path?
4. When should `object.__setattr__` be used instead of `super().__setattr__`?
5. Why does `__getattr__` returning `None` for every name break useful Python behavior?
6. Why is `__dir__` about discoverability rather than a public schema?
7. Why can a dictionary-backed attribute wrapper have key collisions?
8. Why do implicit special methods such as `__len__` require explicit proxy support?
9. What does PEP 562 enable for modules, and what does it not intercept?
10. How can custom attribute hooks interfere with copy/pickle?
11. Why is an allow-list safer than a deny-list for user-controlled names?
12. Which typing tools can describe dynamic APIs, and what do they not enforce at runtime?
13. What performance costs can custom `__getattribute__` introduce?
14. When should a dispatch table be preferred to string-built `getattr`?
15. Why is a dynamic wrapper not a security boundary in Python?

A strong answer explains the lookup mechanism, an appropriate use case, one failure mode, and a safer alternative.

# 9. Final competency checklist

- [ ] Use `getattr`, `setattr`, `hasattr`, and `delattr` with correct exception expectations.
- [ ] Explain why `hasattr` may conceal an `AttributeError` raised by a property.
- [ ] Explain ordinary lookup, descriptors, and MRO at a practical level.
- [ ] Implement `__getattr__` that returns only known fallbacks and raises `AttributeError` otherwise.
- [ ] Implement `__setattr__`/`__delattr__` without recursion and handle initialization order.
- [ ] Explain and test a write-once attribute policy.
- [ ] Use `object.__getattribute__` carefully inside `__getattribute__`.
- [ ] Use `__dir__` to expose dynamic names without claiming they are a stable schema.
- [ ] Explain configuration key collisions and use bracket access when needed.
- [ ] Build a dispatcher with an explicit allow-list.
- [ ] Explain why `__getattr__` alone does not proxy special methods.
- [ ] Describe module-level `__getattr__` under PEP 562.
- [ ] Test copy/pickle behavior for the concrete class.
- [ ] Use Protocols, stubs, `TYPE_CHECKING`, and `Literal` appropriately.
- [ ] Validate user-controlled names and avoid exposing internals.
- [ ] Explain the performance and maintenance costs of dynamic lookup hooks.

# Official references

- Python built-in functions (`getattr`, `setattr`, `hasattr`, `delattr`, `dir`): https://docs.python.org/3/library/functions.html
- Python data model — customizing attribute access: https://docs.python.org/3/reference/datamodel.html#customizing-attribute-access
- Python data model — special method lookup: https://docs.python.org/3/reference/datamodel.html#special-method-lookup
- PEP 562 — Module `__getattr__` and `__dir__`: https://peps.python.org/pep-0562/
- `copy` module: https://docs.python.org/3/library/copy.html
- `pickle` module and security warning: https://docs.python.org/3/library/pickle.html
- `typing` module: https://docs.python.org/3/library/typing.html
- `typing.Protocol`: https://docs.python.org/3/library/typing.html#typing.Protocol
- `typing.Literal`: https://docs.python.org/3/library/typing.html#typing.Literal

---

**Engineering principle:** dynamic attribute access is useful when it provides a small, explicit abstraction. It becomes fragile when unknown names silently succeed, arbitrary strings select internal behavior, or lookup hooks hide side effects. Prefer explicit interfaces unless dynamic behavior materially improves the design.
