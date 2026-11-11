# Copying, Pickling, and Object Lifecycle Hooks

> **Stage 1 · Module 11 — Advanced Python Data Model and Object Design · Lesson 11**  
> **Baseline:** Python 3.12+ (Python 3.13+ features are marked explicitly)  
> **Audience:** beginner through advanced Python engineers, with data-pipeline examples

## Why this lesson matters

A data pipeline often starts with a configuration object and then creates per-run variants, caches state, persists job specifications, and manages resources such as files or connections. Bugs appear when a “copy” still shares nested state, a deserialized object restores a stale or unsafe representation, or cleanup depends on garbage collection happening at a convenient time.

This lesson connects the object model to those engineering problems. It does **not** replace earlier lessons on identity, mutability, slots, cooperative inheritance, or context managers; it applies those concepts to copying, serialization, construction, and finalization.

## Prerequisites

You should be comfortable with:

- names, references, `is`, `==`, mutable and immutable values;
- lists, dictionaries, tuples, classes, instance attributes, and inheritance;
- exceptions, context managers (`with`), type annotations, and basic `pytest`;
- class attributes, `__slots__`, method resolution order, and the idea that special methods are generally looked up on the type.

## Learning objectives

By the end, you should be able to:

1. Distinguish assignment/aliasing, shallow copy, deep copy, and serialization.
2. Predict which identities and nested references are shared after each operation.
3. Implement `__copy__` and `__deepcopy__` without breaking cycles or shared aliases.
4. Explain the `memo` dictionary and test graph-copy invariants.
5. Pickle and restore a module-level domain class, exclude process-local state, and version restored state.
6. Explain `__reduce__` / `__reduce_ex__`, pickle compatibility limits, and why untrusted pickle bytes are unsafe.
7. Distinguish `__new__`, `__init__`, `__init_subclass__`, `__del__`, and `weakref.finalize`.
8. Choose reliable resource cleanup and reason about slots, weak references, cycles, and inheritance.
9. Apply these rules with tests rather than relying on assumptions about identity or finalizer timing.

---

## 1. Names, references, and identity

Python variables are **names bound to objects**. Assignment usually binds another name to the same object; it does not clone the object.

```python
settings = {"retries": 3, "tags": ["daily"]}
alias = settings

print(alias is settings)   # True
print(alias == settings)   # True
alias["retries"] = 5
print(settings["retries"]) # 5
```

`is` asks whether two references point to the same object. `==` asks whether values compare equal according to their equality implementation. Equal objects need not be identical.

### Reference diagram: assignment

```text
settings ─────┐
              ├────> dict {"retries": 3, "tags": [...]}
alias ────────┘
```

### Identity is not a value contract

Use `is` for identity-sensitive checks (especially `x is None`), not to compare ordinary values. CPython may reuse or intern some immutable objects, such as certain small integers and strings, as an implementation optimization. That behavior is not a portable application contract. Do not infer semantic equality or object lifetime from `id()` values.

## 2. Shallow copy versus deep copy

The `copy` module provides two different policies:

- `copy.copy(obj)` makes a **shallow copy**: a new outer object, with references to nested objects copied as references.
- `copy.deepcopy(obj)` recursively copies objects it is designed to copy, using a memo table to handle repeated references and cycles.

Neither operation means “clone every byte of the process.” Files, sockets, locks, database sessions, generators, and other resources need deliberate semantics and may reject copying or pickling.

### One nested configuration, three operations

```python
import copy

source = {
    "name": "daily-ingest",
    "options": {"retries": 3, "tags": ["raw", "validated"]},
}

assigned = source
shallow = copy.copy(source)
deep = copy.deepcopy(source)

print(assigned is source)                         # True
print(shallow is source, shallow == source)       # False True
print(shallow["options"] is source["options"])    # True
print(deep["options"] is source["options"])      # False

source["options"]["tags"].append("published")
print(shallow["options"]["tags"])                 # ['raw', 'validated', 'published']
print(deep["options"]["tags"])                    # ['raw', 'validated']
```

### Reference diagrams

Before copying:

```text
source ──> outer dict ──> options dict ──> tags list
```

After `copy.copy(source)`:

```text
source  ──> original outer dict ──┐
                                  ├──> same options dict ──> same tags list
shallow ──> new outer dict ───────┘
```

After `copy.deepcopy(source)`:

```text
source ──> original dict ──> original options ──> original tags
deep   ──> new dict      ──> copied options   ──> copied tags
```

### “Deep” is not the same as “independent in every sense”

Deep copy follows the copy protocol of each encountered object. Some types are treated as atomic or shared; custom types may define their own policy; external resources may not be copyable. A deep copy is only as correct as the semantics of the object graph and its copy hooks.

### Mutable and immutable objects

- Mutating a list or dict can be observed through every alias to that same object.
- Integers, strings, and bytes are immutable: sharing them is generally safe because their value cannot be changed in place.
- A tuple is immutable as a container, but may contain mutable objects. `("job", options_dict)` cannot have an element replaced, yet `options_dict` can still be mutated.
- A frozen dataclass prevents normal field assignment; it does **not** automatically make nested lists or dictionaries immutable.
- Copying immutable/atomic values may return the original object. Do not use identity as proof that a copy operation failed.

For a production design, ask: **which state must be independent, and which state is intentionally shared?** That is the contract to test.

## 3. A custom object graph for a pipeline

Consider a pipeline run whose two stages intentionally share the same mutable defaults object. This can represent a shared policy/cache within one in-memory graph.

```python
from dataclasses import dataclass, field

@dataclass
class Stage:
    name: str
    options: dict[str, object]

@dataclass
class PipelineConfig:
    name: str
    shared_defaults: dict[str, object]
    stages: list[Stage] = field(default_factory=list)

defaults: dict[str, object] = {"timeout": 30, "labels": ["batch"]}
pipeline = PipelineConfig(
    name="orders",
    shared_defaults=defaults,
    stages=[
        Stage("extract", {"defaults": defaults, "source": "warehouse"}),
        Stage("transform", {"defaults": defaults, "strict": True}),
    ],
)

assert pipeline.stages[0].options["defaults"] is pipeline.shared_defaults
assert pipeline.stages[1].options["defaults"] is pipeline.shared_defaults
```

Graph shape:

```text
pipeline
 ├── shared_defaults ───────────────────────┐
 └── stages list                            │
      ├── Stage("extract").options["defaults"] ─┤
      └── Stage("transform").options["defaults"]┘
```

The three edges point to **one** dictionary, not three equal dictionaries. If a copy is meant to represent a separate run, you usually want the new graph to preserve the internal sharing pattern while separating it from the original graph.

## 4. Implementing `__copy__` and `__deepcopy__`

Only implement these hooks when default behavior is wrong or your class has a clear copy contract. Prefer ordinary composition and immutable state when that avoids custom copying entirely.

### The `memo` dictionary

The `memo` argument to `__deepcopy__(self, memo)` is managed by the `copy` module. It maps identities of source objects to their already-created copies. A correct custom implementation normally:

1. checks whether `id(self)` is already in `memo`;
2. allocates an uninitialized clone;
3. stores `memo[id(self)] = clone` **before** recursively copying child references;
4. deep-copies each field with `copy.deepcopy(field, memo)` using the same memo;
5. returns the clone.

Registering the clone before descending is essential for cycles. Passing the same memo is essential for preserving shared aliases: if two fields point to one source object, they should usually point to one copied object.

### A custom, slotted `JobSpec`

This example gives `JobSpec` a deliberate copy policy and pickle state policy. It uses slots to demonstrate that custom code should not assume an instance has `__dict__`.

```python
from __future__ import annotations

import copy
from typing import Any

class JobSpec:
    __slots__ = ("name", "settings", "metadata", "__weakref__")
    STATE_VERSION = 1

    def __init__(
        self,
        name: str,
        settings: dict[str, Any],
        metadata: dict[str, Any],
    ) -> None:
        self.name = name
        self.settings = settings
        self.metadata = metadata

    def __copy__(self) -> JobSpec:
        # New outer object; nested values intentionally remain shared.
        clone = type(self).__new__(type(self))
        clone.name = self.name
        clone.settings = self.settings
        clone.metadata = self.metadata
        return clone

    def __deepcopy__(self, memo: dict[int, Any]) -> JobSpec:
        existing = memo.get(id(self))
        if existing is not None:
            return existing

        # Bypass __init__: we are reconstructing an existing object's state.
        clone = type(self).__new__(type(self))
        memo[id(self)] = clone  # must precede recursive field copies

        clone.name = copy.deepcopy(self.name, memo)
        clone.settings = copy.deepcopy(self.settings, memo)
        clone.metadata = copy.deepcopy(self.metadata, memo)
        return clone

    def __getstate__(self) -> dict[str, Any]:
        # Store durable data only. Do not serialize open resources or locks.
        return {
            "version": self.STATE_VERSION,
            "name": self.name,
            "settings": self.settings,
            "metadata": self.metadata,
        }

    def __setstate__(self, state: dict[str, Any]) -> None:
        # Example migration point for older saved state.
        version = state.get("version", 0)
        if version == 0:
            # Hypothetical older format used "options" instead of "settings".
            settings = state["options"]
            metadata = state.get("metadata", {})
        elif version == 1:
            settings = state["settings"]
            metadata = state["metadata"]
        else:
            raise ValueError(f"Unsupported JobSpec state version: {version}")

        self.name = state["name"]
        self.settings = settings
        self.metadata = metadata
```

**Inheritance boundary:** these hooks deliberately copy and serialize only the slots declared by `JobSpec`. A subclass that adds slots or changes allocation through a custom `__new__` must extend or override the relevant hooks and test its own state. The expression `type(self).__new__(type(self))` bypasses `__init__`, but it still invokes the subclass's `__new__`; it is not a universal allocator for every possible subclass.

### Test the graph semantics

```python
import copy

shared = {"tags": ["raw"]}
job = JobSpec(
    "orders",
    settings={"defaults": shared, "retries": 2},
    metadata={"defaults": shared, "owner": "data-platform"},
)

shallow = copy.copy(job)
deep = copy.deepcopy(job)

assert shallow is not job
assert shallow.settings is job.settings
assert deep.settings is not job.settings
assert deep.settings["defaults"] is deep.metadata["defaults"]
assert deep.settings["defaults"] is not shared

shared["tags"].append("changed")
assert "changed" in shallow.settings["defaults"]["tags"]
assert "changed" not in deep.settings["defaults"]["tags"]
```

`JobSpec` deliberately does not define value equality, so the default `==` is identity-based. For that reason, the meaningful assertions here are about identity and state, not `shallow == job`.

### Cycles: why memoization order matters

```python
import copy

cycle: list[object] = []
cycle.append(cycle)

cloned_cycle = copy.deepcopy(cycle)
assert cloned_cycle is not cycle
assert cloned_cycle[0] is cloned_cycle
```

The list implementation in the standard library already handles this. A custom `__deepcopy__` that recursively copies children **before** memoizing its partially built clone can recurse indefinitely on cycles.

### Shared aliases are a graph property

```python
shared_child = {"threshold": 10}
source = {"left": shared_child, "right": shared_child}
clone = copy.deepcopy(source)

assert clone["left"] is clone["right"]   # sharing preserved inside clone
assert clone["left"] is not shared_child # detached from source graph
```

Do not call `copy.deepcopy(child)` without passing `memo` inside your own hook. That starts a separate copy operation and can duplicate shared nodes or mishandle cycles across fields.

### When custom copy hooks should not copy everything

A class may intentionally share immutable collaborators, caches, or externally managed services. It may also reject copying if duplication has no valid meaning. Document that policy. Never blindly duplicate a database connection, lock, thread, open file, generator, or transaction and pretend it is independent.

## 5. Copying related APIs

### `dataclasses.replace` and `copy.replace`

`dataclasses.replace(instance, field=value)` creates a new dataclass instance with selected fields changed. It is not a recursive deep copy: unchanged fields can continue to refer to the same nested objects.

Python 3.13+ adds `copy.replace(obj, **changes)` for supported objects (including dataclasses and named tuples, and classes implementing `__replace__`). It is a *new-object-with-selected-fields-changed* operation, not a substitute for `copy.copy` or `copy.deepcopy`. On Python 3.12, use `dataclasses.replace` where appropriate.

### Slotted and frozen dataclasses

- A slotted object may not have `__dict__`; use its public attributes or explicit state rather than assuming `vars(obj)` works.
- Weak references to slotted instances require a `__weakref__` slot (or the appropriate dataclass option where supported).
- Frozen dataclasses prevent ordinary assignment but may still contain mutable nested values.
- Copy behavior depends on fields and their values; test nested state explicitly.
- Multiple inheritance with incompatible non-empty slot layouts can fail with `TypeError`. Do not use slots without considering the hierarchy and layout constraints.

## 6. Copying is not serialization

| Operation | Purpose | Result | Main concern |
|---|---|---|---|
| Assignment | Bind another name | Same object | Aliasing |
| `copy.copy` | New outer object | In-memory object | Nested references stay shared |
| `copy.deepcopy` | Recursively copy supported graph | In-memory graph | Custom policies, resources, cycles |
| `pickle.dumps` | Encode supported Python object state | `bytes` | Compatibility and code-execution risk |
| `pickle.loads` | Reconstruct object from pickle bytes | In-memory object | **Unsafe for untrusted input** |
| JSON encoding | Exchange basic data structures | Text/bytes | Requires explicit schema/type mapping |

Copying operates on an in-memory object graph. Pickling encodes reconstruction instructions and state into a byte stream. Neither is automatically a stable public storage schema.

## 7. Pickle basics and practical restoration

Pickle is Python's object serialization mechanism. The exact bytes depend on protocol and implementation details. `pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)` creates bytes; `pickle.loads(data)` reconstructs an object.

Typical constraints:

- Functions and classes are generally referenced by importable module and qualified name, not embedded as their source code. They should be defined at module scope and remain importable under the same name.
- Lambdas and local/nested classes/functions generally cannot be pickled by standard `pickle`.
- Open files, sockets, locks, database connections, generators, and live sessions are generally not suitable serialized state.
- Pickle does not promise compatibility across arbitrary code changes, Python versions, package versions, or deployments.
- `pickle` is Python-specific and is not an interoperable data-exchange format like a documented JSON schema or Protocol Buffers schema.

The `JobSpec` class above defines `__getstate__` and `__setstate__`, so it can serialize durable fields and reconstruct them without trying to pickle a process-local resource.

```python
import pickle

job = JobSpec(
    "orders",
    settings={"retries": 3, "tags": ["raw"]},
    metadata={"owner": "analytics"},
)

payload = pickle.dumps(job, protocol=pickle.HIGHEST_PROTOCOL)
restored = pickle.loads(payload)

assert isinstance(restored, JobSpec)
assert restored is not job
assert restored.name == job.name
assert restored.settings == job.settings
assert restored.settings is not job.settings
print(restored.name, restored.settings["retries"])
# orders 3
```

### State hooks and versioning

`__getstate__` returns the state to serialize. `__setstate__` restores it on an object allocated during unpickling. Do not assume `__init__` will be called when unpickling an instance. The class above includes a `version` field and a migration branch for a hypothetical version-0 state.

For durable systems:

1. Treat stored state as a schema that can evolve.
2. Add explicit version identifiers and migration tests.
3. Keep durable data separate from runtime resources.
4. Fail clearly on unknown future versions rather than silently inventing defaults.
5. Pin and test relevant code/runtime versions if pickle is used for trusted internal caches.
6. Prefer a documented, language-neutral format for long-lived data or cross-service interchange.

Versioning a pickle state dict can help with migrations, but it does **not** make pickle a stable long-term storage format. Class paths and reconstruction behavior can still change.

### Excluding a process-local lock

A lock represents synchronization state for one process, not durable business data. Exclude it from the state and create a fresh lock when restoring the object. This example is for trusted, local data only; never use pickle on attacker-controlled bytes.

```python
import pickle
from threading import Lock

class Cache:
    def __init__(self) -> None:
        self.data: dict[str, int] = {}
        self.lock = Lock()

    def __getstate__(self) -> dict[str, object]:
        return {"state_version": 1, "data": self.data}

    def __setstate__(self, state: dict[str, object]) -> None:
        if state.get("state_version", 0) != 1:
            raise ValueError("unsupported Cache state version")
        data = state.get("data")
        if not isinstance(data, dict) or any(
            not isinstance(key, str) or not isinstance(value, int)
            for key, value in data.items()
        ):
            raise ValueError("invalid Cache data state")
        self.data = data
        self.lock = Lock()

cache = Cache()
cache.data["rows"] = 12
restored_cache = pickle.loads(pickle.dumps(cache))
assert restored_cache.data == {"rows": 12}
assert restored_cache.lock is not cache.lock
```

In production code, validate state shapes and types explicitly rather than relying on a type-ignore comment. The lock is recreated, not restored from the byte stream.

### `__reduce__` and `__reduce_ex__`

Pickle can use `__reduce_ex__(protocol)` (preferred when provided) or `__reduce__()` to obtain a reconstruction recipe. A reduction is commonly a tuple such as:

```python
(callable, args, state)
```

Conceptually, pickle calls `callable(*args)` to create an object and then applies `state` (often through `__setstate__` if present). The full reduction protocol has additional supported tuple forms for list items, dictionary items, and state-setting callables; consult the Python documentation before implementing those forms.

Example: an immutable-like domain value whose constructor is the reconstruction callable. This class uses the protocol-aware `__reduce_ex__(protocol)` hook:

```python
import pickle

class RegionCode:
    def __init__(self, code: str) -> None:
        self.code = code

    def __reduce_ex__(self, protocol: int):
        # This example needs only a callable and positional arguments.
        return (type(self), (self.code,))

code = RegionCode("ap-south-1")
round_trip = pickle.loads(pickle.dumps(code))
assert round_trip.code == "ap-south-1"
```

`copyreg` offers an alternative when you need to register a reduction function for a type you do not control. In real applications, keep the class and reducer importable at module scope:

```python
import copyreg
import pickle

class RegisteredRegionCode:
    def __init__(self, code: str) -> None:
        self.code = code

def restore_region_code(code: str) -> RegisteredRegionCode:
    return RegisteredRegionCode(code)

def reduce_region_code(value: RegisteredRegionCode):
    return (restore_region_code, (value.code,))

copyreg.pickle(RegisteredRegionCode, reduce_region_code)
value = RegisteredRegionCode("eu-west-1")
restored = pickle.loads(pickle.dumps(value))
assert type(restored) is RegisteredRegionCode
assert restored.code == "eu-west-1"
```

A reduction is a reconstruction recipe, not merely a dump of attributes. A custom reduction is powerful and therefore easy to get wrong. Prefer ordinary pickle support and state hooks unless you need explicit control over reconstruction. The `copy` module may also consult reduction/pickle protocols for types without specialized copy hooks; that does not make copying equivalent to serialization.

### Security: never unpickle untrusted bytes

**Never call `pickle.loads` or `pickle.load` on data an attacker can control.** Unpickling can invoke arbitrary callables during reconstruction and can execute code. A signature or MAC can help establish authenticity only if keys and verification are handled correctly and the signed bytes are verified *before* deserialization; it does not make untrusted pickle intrinsically safe.

For untrusted input, use a constrained format such as JSON with schema validation, or a purpose-built protocol. Do not accept pickle files from uploads, public URLs, untrusted job queues, or users. Do not treat “it came from our network” as a security boundary.

## 8. Construction: `__new__` versus `__init__`

Object creation and initialization are distinct phases:

1. `type.__call__` orchestrates construction for an ordinary class.
2. `__new__(cls, ...)` creates and returns an instance (or potentially returns something else).
3. If `__new__` returns an instance of `cls` or a subclass, Python calls `__init__(instance, ...)` to initialize that already-created object.
4. If `__new__` returns an object that is not an instance of `cls`, `__init__` for `cls` is not called.

Most classes should implement `__init__` only. Override `__new__` when creation itself needs control, especially for immutable built-in subclasses, caching/factory behavior, or carefully designed singleton-like patterns.

```python
class TracedJob:
    def __new__(cls, name: str):
        print("allocate")
        return super().__new__(cls)

    def __init__(self, name: str) -> None:
        print("initialize")
        self.name = name

job = TracedJob("orders")
# allocate
# initialize
```

An immutable built-in subclass commonly validates/transforms its value in `__new__`, because the immutable value must be established during creation:

```python
class PositiveCode(int):
    def __new__(cls, value: int) -> PositiveCode:
        if value <= 0:
            raise ValueError("value must be positive")
        return super().__new__(cls, value)

assert PositiveCode(7) == 7
```

Copy and unpickle protocols may allocate an object without running the ordinary `__init__`; their job is to reconstruct state. Therefore, keep constructors focused and make state restoration establish the invariants it needs.

## 9. `__init_subclass__`: a class-creation hook

`__init_subclass__` runs when a subclass is created. It is useful for validating subclass declarations or building a registry without a metaclass. It is not called each time an instance is constructed.

```python
class JobPlugin:
    registry: dict[str, type["JobPlugin"]] = {}

    def __init_subclass__(cls, *, plugin_name: str | None = None, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if plugin_name is None:
            return
        if plugin_name in JobPlugin.registry:
            raise ValueError(f"duplicate plugin: {plugin_name}")
        JobPlugin.registry[plugin_name] = cls

class CsvJob(JobPlugin, plugin_name="csv"):
    pass

class JsonJob(JobPlugin, plugin_name="json"):
    pass

assert JobPlugin.registry["csv"] is CsvJob
```

Engineering points:

- Call `super().__init_subclass__(**kwargs)` to cooperate with other hooks in the MRO.
- Consume only the keyword arguments your class owns; pass the rest onward.
- Decide whether abstract/intermediate subclasses should register.
- Be cautious with import-time side effects and plugin registration.
- `__set_name__` is another class-creation hook, used by descriptors to learn the attribute name assigned to them.
- `__class_getitem__` supports class subscription syntax such as `MyType[int]` for generic-like APIs. `__instancecheck__` and `__subclasscheck__` can customize checks through a metaclass; they are advanced tools, not normal replacements for good interfaces.

## 10. Finalization, `__del__`, and reliable cleanup

### `__del__` is not a resource-management plan

`__del__(self)` is a finalizer that may be invoked when an object is being finalized, but its timing and conditions are not a dependable cleanup contract. Cycles, implementation details, process termination, interpreter shutdown, and exceptions in finalizers complicate behavior. During shutdown, module globals or dependencies a finalizer expects may already be cleared. Finalizers can also participate in resurrection or keep objects alive in surprising ways.

Never rely on `__del__` to guarantee that a file, socket, transaction, lock, or remote session is closed promptly. Do not write tests that assert a finalizer runs at a particular time after `del obj`. `del obj` removes a name; it does not itself guarantee immediate destruction.

### Prefer deterministic cleanup: context managers

```python
from pathlib import Path

def read_first_line(path: Path) -> str:
    with path.open("r", encoding="utf-8") as handle:
        return handle.readline()
```

The `with` statement calls the context manager's exit protocol when the block exits, including exceptional exits. For resources you own, implement or use a context manager and define who owns the resource. This is the preferred mechanism for deterministic cleanup.

### `weakref.finalize` as a fallback

`weakref.finalize(obj, callback, *args, **kwargs)` registers a callback associated with `obj` becoming unreachable. The finalizer object keeps the callback and its arguments alive, but it must not hold a strong reference back to `obj`; otherwise the target may never become unreachable. A callback that is a bound method of the target is a common mistake because the bound method retains the target.

Example pattern: the callback owns only the file handle, not the wrapper object.

```python
from pathlib import Path
import weakref
from typing import TextIO

def _close_handle(handle: TextIO) -> None:
    if not handle.closed:
        handle.close()

class ManagedTextFile:
    def __init__(self, path: Path) -> None:
        self._handle = path.open("w", encoding="utf-8")
        self._finalizer = weakref.finalize(self, _close_handle, self._handle)

    def write(self, text: str) -> None:
        self._handle.write(text)

    def close(self) -> None:
        # Calling the finalizer explicitly invokes the callback once and
        # marks it dead; later finalization will not invoke it a second time.
        self._finalizer()

    def __enter__(self) -> ManagedTextFile:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()
```

Usage:

```python
with ManagedTextFile(Path("pipeline.log")) as log:
    log.write("pipeline started\n")
```

The context manager provides deterministic cleanup. The finalizer is a safety net, not a substitute for `close()`/`with`. For critical resources, test explicit cleanup and error paths.

### Cycles and garbage collection

Reference cycles can keep objects reachable from one another even after external names disappear. Modern Python's cyclic garbage collector can collect many unreachable cycles, but collection timing is not a resource-lifetime guarantee. A finalizer may be called as part of cyclic collection, and finalization order among related objects should not be assumed. Design cleanup so it does not depend on another object being finalized first.

### `weakref.ref` versus `weakref.finalize`

- `weakref.ref(obj)` creates a weak reference that does not keep `obj` alive; calling the weak reference returns the object while it remains alive, otherwise `None`.
- `weakref.finalize(obj, callback, ...)` registers a one-shot callback associated with the target's finalization.
- Many built-in and slotted objects are not weak-referenceable by default. For a custom slotted class, include `__weakref__` in `__slots__` if weak references are needed.
- A weak-reference callback should not close over the target strongly. Avoid storing a bound method of the target as the callback.

## 11. `__del__`, ownership, and process-local state

A pipeline configuration is data; an open connection is a live resource. Separate these responsibilities.

- A durable `JobSpec` can be copied or serialized as data.
- A database connection should be created by the worker that owns it and closed by an explicit context manager or lifecycle method.
- A lock should be recreated in the receiving process rather than copied as if it were ordinary data.
- A cache may be intentionally shared within one process but omitted from persisted state.
- A finalizer can be useful as a fallback for cleanup, but should not decide transaction commit/rollback semantics.

Do not put runtime-only state into a pickle merely because it happens to be an attribute. Define a clear boundary between durable configuration and runtime execution state.

## 12. Common mistakes and corrections

| Mistake | Why it fails | Better approach |
|---|---|---|
| Treating assignment as copying | Both names refer to one object | Draw the reference graph; use an explicit copy policy |
| Shallow-copying nested config and mutating it | Nested dicts/lists remain shared | Deep-copy the graph or copy only the fields that need isolation |
| Assuming deep copy duplicates every object | Hooks and atomic/resource types can be shared or reject copying | Define and test semantics for each custom type |
| Forgetting `memo` in `__deepcopy__` | Cycles can recurse forever; aliases can split | Memoize the clone before recursing and pass the same memo to every nested `deepcopy` |
| Calling `copy.deepcopy(child)` without `memo` in a hook | Starts a separate copy traversal | Always call `copy.deepcopy(child, memo)` inside `__deepcopy__` |
| Using `vars(obj)` on a slotted object | It may have no `__dict__` | Access slots explicitly or define state hooks |
| Treating pickle as a permanent schema | Class paths and code/state layouts can change | Version state, test migrations, or use a stable data format |
| Pickling lambdas, local classes, or live handles | Standard pickle relies on importable names and supported state | Move definitions to module scope; serialize durable data only |
| Unpickling user-controlled bytes | Reconstruction can execute arbitrary code | Never unpickle untrusted data; validate a constrained format |
| Using `__del__` to close resources | Timing/order are unreliable | Use `with`, explicit `close()`, and optionally `weakref.finalize` as fallback |
| Registering a finalizer with a bound method of its target | The callback can keep the target alive | Pass a standalone callback and only the resource it needs |
| Assuming `__init__` always runs during restore/copy | Reconstruction protocols may bypass it | Validate and restore invariants in the relevant hook |
| Relying on small-int/string interning | Identity reuse is implementation-dependent | Compare values with `==`; use `is` for identity checks only |
| Confusing `replace` with deep copy | Unchanged fields may still share nested objects | Test identities of changed and unchanged fields |

## 13. Tests with `pytest`

Save the following as `test_lesson11.py` in the same directory as a module containing the `JobSpec` definition, or keep the class in the test file for a standalone exercise. The tests below are self-contained when `JobSpec` is defined above them in the same file.

```python
import copy
import pickle
import pytest

def make_job() -> JobSpec:
    shared = {"tags": ["raw"]}
    return JobSpec(
        "orders",
        settings={"defaults": shared, "retries": 2},
        metadata={"defaults": shared, "owner": "data-platform"},
    )

def test_assignment_and_shallow_copy() -> None:
    job = make_job()
    alias = job
    shallow = copy.copy(job)

    assert alias is job
    assert shallow is not job
    assert shallow.settings is job.settings
    assert shallow.settings["defaults"] is job.settings["defaults"]

def test_deepcopy_detaches_and_preserves_internal_alias() -> None:
    job = make_job()
    clone = copy.deepcopy(job)

    assert clone is not job
    assert clone.settings is not job.settings
    assert clone.settings == job.settings
    assert clone.settings["defaults"] is clone.metadata["defaults"]
    assert clone.settings["defaults"] is not job.settings["defaults"]

    job.settings["defaults"]["tags"].append("changed")
    assert "changed" not in clone.settings["defaults"]["tags"]

def test_deepcopy_handles_cycle() -> None:
    original: list[object] = []
    original.append(original)

    cloned = copy.deepcopy(original)

    assert cloned is not original
    assert cloned[0] is cloned

def test_custom_deepcopy_handles_cycle_through_a_field() -> None:
    job = JobSpec("cyclic", settings={}, metadata={})
    job.settings["owner"] = job

    clone = copy.deepcopy(job)

    assert clone is not job
    assert clone.settings["owner"] is clone

def test_pickle_round_trip_restores_state() -> None:
    job = make_job()
    restored = pickle.loads(pickle.dumps(job))

    assert isinstance(restored, JobSpec)
    assert restored is not job
    assert restored.name == job.name
    assert restored.settings == job.settings
    assert restored.settings is not job.settings
    assert restored.settings["defaults"] is restored.metadata["defaults"]

def test_legacy_state_version_migrates() -> None:
    job = JobSpec.__new__(JobSpec)
    job.__setstate__({
        "version": 0,
        "name": "orders",
        "options": {"retries": 1},
    })
    assert job.settings == {"retries": 1}
    assert job.metadata == {}

def test_unsupported_state_version_fails() -> None:
    job = JobSpec.__new__(JobSpec)
    with pytest.raises(ValueError, match="Unsupported JobSpec state version"):
        job.__setstate__({
            "version": 999,
            "name": "orders",
            "settings": {},
            "metadata": {},
        })
```

Run with:

```bash
python -m pytest -q
```

Expected test summary when run in a correctly configured Python 3.12+ environment:

```text
7 passed
```

The count is an expected summary, not a substitute for running the suite in your own supported environment. If the test file is split from the implementation, import `JobSpec` from its actual module rather than relying on a shared file namespace.

### What these tests establish

- identity versus aliasing;
- shallow-copy sharing of nested fields;
- deep-copy detachment while preserving graph-internal aliases;
- self-referential built-in cycles and cycles passing through a custom `__deepcopy__`;
- pickle round-trip state restoration;
- migration from a legacy state version and rejection of an unsupported state version.

Add tests for any project-specific policy, such as deliberately shared collaborators, omitted caches, migration from each supported state version, and resource cleanup on exceptions.

## 14. Graduated exercises with worked solutions

### Exercise 1 — Predict the references (beginner)

```python
import copy
a = {"columns": ["id", "amount"]}
b = copy.copy(a)
c = copy.deepcopy(a)
a["columns"].append("country")
```

Questions: Which list contains `"country"`? Are `a` and `b` identical? Are `a` and `b` equal after the mutation?

**Worked solution**

- `a["columns"]` and `b["columns"]` refer to the same list, so both see `"country"`.
- `a is b` is `False`: the outer dictionaries are distinct.
- `a == b` is `True` after the mutation because their nested values compare equal.
- `c["columns"]` does not contain `"country"` because its nested list was copied.

### Exercise 2 — Preserve an alias (intermediate)

Create a dict where `"left"` and `"right"` point to the same child dict. Deep-copy it and prove the clone keeps the internal alias while detaching from the original.

**Worked solution**

```python
child = {"limit": 5}
source = {"left": child, "right": child}
clone = copy.deepcopy(source)

assert clone["left"] is clone["right"]
assert clone["left"] is not child
```

The memo table records the source child’s identity after it is copied; the second edge reuses that copied child.

### Exercise 3 — Fix a broken `__deepcopy__` (advanced)

This implementation is wrong:

```python
def __deepcopy__(self, memo):
    clone = type(self).__new__(type(self))
    clone.child = copy.deepcopy(self.child)  # bug
    return clone
```

**Worked solution**

```python
def __deepcopy__(self, memo):
    existing = memo.get(id(self))
    if existing is not None:
        return existing
    clone = type(self).__new__(type(self))
    memo[id(self)] = clone
    clone.child = copy.deepcopy(self.child, memo)
    return clone
```

The fixed method uses the same memo for the full traversal and records the clone before descending, which handles both repeated references and cycles.

### Exercise 4 — Persist data, not runtime resources (advanced)

A class owns `settings`, an open file, and a lock. What should survive a pickle round trip?

**Worked solution**

Persist the durable settings and any stable logical identifiers. Omit the live file and lock from serialized state; in `__setstate__`, restore the settings and create new runtime resources only if that is the class's documented responsibility. Prefer a separate runtime wrapper/context manager so a pure configuration object does not own resources at all. Never deserialize untrusted pickle data.

### Exercise 5 — Replace nondeterministic cleanup (advanced)

A class closes a socket only in `__del__`. Rewrite its usage to make cleanup reliable.

**Worked solution**

Implement/use a context manager and close the socket in `__exit__` (or use `contextlib.closing` if the object exposes `close()`):

```python
from contextlib import closing

with closing(open_socket()) as sock:
    perform_work(sock)
```

`open_socket()` and `perform_work()` are application-specific placeholders. The key property is that the resource is closed as control leaves the `with` block, including when the body raises. A `weakref.finalize` callback may be an additional fallback, but it should not replace deterministic ownership.

## 15. Roadmap self-check — answers

1. **What is the difference between `__new__` and `__init__`, and when must you override `__new__`?**  
   `__new__` creates and returns an instance; `__init__` initializes an instance already returned by `__new__`. Override `__new__` when creation itself must be customized, especially for immutable built-in subclasses, factories, or carefully controlled instance caching. Most ordinary classes need only `__init__`.

2. **Why is `__getstate__` needed for a class holding a `threading.Lock`?**  
   A lock is process-local runtime synchronization state and is not ordinarily picklable. `__getstate__` can omit it and return only durable data; `__setstate__` restores that data and creates a fresh lock if the restored object owns one. Prefer keeping runtime resources outside serializable configuration where possible.

3. **Rewrite a `__del__`-based cleanup using `weakref.finalize` or a context manager.**  
   Prefer a context manager with explicit `close()` in `__exit__` for deterministic cleanup. If a finalizer is appropriate as a fallback, register a standalone callback and pass only the resource to close; do not use a bound method that strongly retains the target object. The `ManagedTextFile` example above demonstrates both patterns.

## 16. Final engineering checklist

Before shipping code that copies, serializes, or finalizes objects, verify:

- [ ] I know whether each operation creates an alias, a shallow copy, a deep copy, or serialized bytes.
- [ ] I have documented which nested state must be independent and which sharing is intentional.
- [ ] My tests assert identity (`is`) and value equality (`==`) separately.
- [ ] Custom `__deepcopy__` checks `memo`, registers the clone before recursion, and passes the same memo to nested copies.
- [ ] Shared references and cycles are tested explicitly.
- [ ] Copy behavior for slots, inheritance, frozen dataclasses, weak references, and resource fields is deliberate.
- [ ] Pickle state excludes live resources and contains an explicit version where persistence requires migration.
- [ ] Restoration is tested without assuming `__init__` runs.
- [ ] I understand that `__reduce__` controls reconstruction and that class/function import paths affect compatibility.
- [ ] I never unpickle data that an attacker can control.
- [ ] Resource ownership is explicit; critical cleanup uses `with` or `close()`, not `__del__`.
- [ ] Any `weakref.finalize` callback does not strongly retain the target.
- [ ] I do not depend on garbage-collection timing, finalizer ordering, object resurrection, interning, or `id()` reuse.
- [ ] I have run the tests in the supported Python versions and recorded the actual results.

## Key takeaways

1. A copy is a graph transformation; decide the intended aliasing semantics first.
2. `deepcopy`'s memo is what lets a traversal preserve shared nodes and cycles.
3. Pickle is a Python reconstruction protocol, not a safe untrusted-input format or a universal long-term schema.
4. `__new__` creates; `__init__` initializes; `__init_subclass__` runs during subclass creation.
5. Deterministic resource ownership beats destructor timing. Use context managers first and finalizers only as a fallback.
