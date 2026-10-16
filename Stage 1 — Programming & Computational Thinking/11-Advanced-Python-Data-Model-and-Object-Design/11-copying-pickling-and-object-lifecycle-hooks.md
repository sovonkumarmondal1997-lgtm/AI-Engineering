# Lesson 11 — Copying, Pickling, and Object Lifecycle Hooks

**Stage:** Stage 1 — Programming & Computational Thinking  
**Module:** 11 — Advanced Python Data Model and Object Design  
**Level:** Beginner → Intermediate → Advanced  
**Target:** Python 3.12+ (Python 3.13+ notes are explicitly marked)

> **Engineering objective:** Understand object identity and lifetime, choose correct copy semantics, serialize only appropriate state, reconstruct objects safely, and manage resources without depending on unreliable destruction timing.

## Learning outcomes

By completing this lesson, you should be able to:

- Distinguish assignment, aliasing, shallow copy, deep copy, and copy-with-changes.
- Predict how nested mutable objects and cyclic graphs behave under copying.
- Implement `__copy__` and `__deepcopy__` without breaking cycles or shared references.
- Explain the roles of `__new__`, `__init__`, `__del__`, and garbage collection.
- Use `copy.replace()` (Python 3.13+) and `dataclasses.replace()` appropriately.
- Serialize and restore supported Python objects with `pickle`, including custom state handling.
- Explain `__reduce__`, `__reduce_ex__`, pickle protocols, and `copyreg` at a practical level.
- Identify why unpickling untrusted data is unsafe and select safer interchange formats.
- Prefer context managers and `weakref.finalize` over `__del__` for resource cleanup.
- Recognize class-creation hooks such as `__init_subclass__` and `__set_name__`.
- Design and test robust behavior for data-engineering objects that contain caches, locks, connections, or large data structures.

## Prerequisites and environment

You should understand classes, instance attributes, mutability, references, inheritance, exceptions, context managers, and basic unit testing. Use Python 3.12 or newer; use Python 3.13+ only for the `copy.replace()` section.

Recommended tools:

```bash
python --version
python -m venv .venv
# Activate the virtual environment, then:
python -m pip install pytest ruff
```

The examples are standard-library-first. Run them in a trusted local environment. Never test untrusted pickle payloads.

---

## 1. Object identity, references, and lifetime

### 1.1 Variables are names, not boxes

A Python variable is a name bound to an object. Assignment normally creates another reference to the same object; it does not clone the object.

```python
source = {"status": "ready", "tags": ["daily"]}
alias = source

assert alias is source
alias["status"] = "running"
assert source["status"] == "running"
```

- `is` asks whether two references point to the exact same object.
- `==` asks whether objects compare equal according to their equality implementation.
- `id(obj)` returns an identity value that is unique during that object's lifetime. Do not treat it as a persistent identifier or business key.

```python
left = [1, 2]
right = [1, 2]
assert left == right
assert left is not right
```

### 1.2 Object graph model

Objects can refer to other objects. A dictionary containing a list is a small object graph. Copying decisions concern which nodes in that graph are reused and which are recreated.

```python
record = {"metadata": {"labels": ["silver"]}}
second_reference = record

assert second_reference["metadata"] is record["metadata"]
```

This distinction matters in ETL jobs, where a transformation may unexpectedly mutate a shared configuration object, cached payload, or in-memory batch.

### 1.3 Lifecycle at a high level

For an ordinary class call such as `JobConfig(...)`, Python creates an instance through `__new__`, then initializes it through `__init__` if `__new__` returned an instance of that class. The object remains alive while references keep it reachable (with implementation-specific details around cycles and garbage collection). Finalization is not a reliable scheduling mechanism.

```python
class Trace:
    def __new__(cls, *args, **kwargs):
        print("allocate")
        return super().__new__(cls)

    def __init__(self, name):
        print("initialize", name)
        self.name = name

item = Trace("daily-ingest")
# allocate
# initialize daily-ingest
```

Do not infer that `__del__` runs immediately when a variable goes out of scope. The timing and behavior of finalization can vary, especially with reference cycles and interpreter shutdown.

---

## 2. Assignment vs shallow copy vs deep copy

### 2.1 Assignment: another reference

```python
import copy

original = {"columns": ["id", "amount"]}
assigned = original
assigned["columns"].append("currency")
assert original["columns"] == ["id", "amount", "currency"]
assert assigned is original
```

Use assignment when shared ownership is intentional. It is not a copy operation.

### 2.2 Shallow copy: new outer object, shared children

`copy.copy(obj)` makes a shallow copy. For a built-in list or dictionary, it creates a new outer container while references to nested objects are copied as references.

```python
import copy

original = {"tags": ["daily"], "attempt": 1}
shallow = copy.copy(original)

assert shallow is not original
assert shallow["tags"] is original["tags"]
shallow["attempt"] = 2
shallow["tags"].append("retry")

assert original["attempt"] == 1
assert original["tags"] == ["daily", "retry"]
```

This is useful when the outer structure should be independent but its child objects are intentionally shared or immutable. It is dangerous when nested state must be isolated.

### 2.3 Deep copy: recursively copy a graph

`copy.deepcopy(obj)` recursively copies supported objects and maintains a memo table to handle cycles and preserve repeated references within the copied graph.

```python
import copy

original = {"tags": ["daily"]}
deep = copy.deepcopy(original)
deep["tags"].append("retry")

assert original["tags"] == ["daily"]
assert deep["tags"] == ["daily", "retry"]
assert deep is not original
assert deep["tags"] is not original["tags"]
```

Deep copy is not a universal promise to duplicate every reachable resource. Classes can customize it; some objects are treated specially; external resources such as open sockets should generally not be cloned as if they were ordinary data.

### 2.4 Decision table

| Operation | New outer object? | Nested mutable objects | Typical use |
|---|---:|---|---|
| `b = a` | No | Shared | Intentional alias |
| `copy.copy(a)` | Usually yes for built-in containers | Usually shared | Copy container shell |
| `copy.deepcopy(a)` | Usually yes | Recursively copied where supported | Independent object graph |
| `dataclasses.replace(a, ...)` | Yes for a dataclass instance | Other fields are reused by reference | Copy a record with selected field changes |
| `copy.replace(a, ...)` | Yes for supported replaceable objects; Python 3.13+ | Depends on object's replacement implementation | Generic copy-with-changes protocol |

Do not choose `deepcopy` reflexively. It can be expensive, duplicate objects that should remain shared, and fail or behave unexpectedly for objects that represent external resources.

### 2.5 Common copy patterns

**Copy only the mutable field that needs isolation:**

```python
from copy import copy

class Batch:
    def __init__(self, rows, schema):
        self.rows = list(rows)
        self.schema = schema  # schema is intentionally shared/read-only

    def with_rows(self, rows):
        clone = copy(self)
        clone.rows = list(rows)
        return clone

schema = {"id": "int"}
first = Batch([{"id": 1}], schema)
second = first.with_rows([{"id": 2}])
assert second is not first
assert second.schema is first.schema
assert second.rows is not first.rows
```

Note that `list(rows)` copies the outer list only. If row dictionaries are mutable and must be isolated too, define that requirement explicitly and copy each row or use a suitable deep-copy strategy.

---

## 3. Customizing copy behavior

### 3.1 `__copy__`

Define `__copy__(self)` when the default shallow-copy behavior is not appropriate. Return a new instance with the intended shallow semantics; do not accidentally invoke the public copy function recursively on `self`.

```python
import copy

class QueryPlan:
    def __init__(self, steps, cache=None):
        self.steps = list(steps)
        self.cache = {} if cache is None else cache

    def __copy__(self):
        cls = type(self)
        clone = cls.__new__(cls)
        clone.steps = self.steps.copy()
        clone.cache = self.cache  # explicitly shared cache
        return clone

plan = QueryPlan(["scan", "filter"])
clone = copy.copy(plan)
assert clone is not plan
assert clone.steps is not plan.steps
assert clone.cache is plan.cache
```

This example chooses to copy the steps list but share the cache. That is a design decision, not a universal rule. Document it so callers know what mutations are shared.

### 3.2 `__deepcopy__(self, memo)`

A custom `__deepcopy__` must cooperate with the memo dictionary. The memo prevents infinite recursion for cycles and ensures that repeated references to one source object map to one corresponding copied object.

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

root = Node("root")
child = Node("child")
root.children.extend([child, child])  # two edges to the same node
root.children[0].children.append(root)  # cycle back to root

cloned_root = copy.deepcopy(root)
assert cloned_root is not root
assert cloned_root.children[0] is cloned_root.children[1]
assert cloned_root.children[0].children[0] is cloned_root
```

The order is essential: allocate the clone and put it in `memo` **before** recursively copying children. Otherwise a cycle can recurse indefinitely.

### 3.3 Copying immutable or shared objects

Immutable values such as integers and strings are safe to share. Some domain objects are intentionally identity-bearing (for example, a connection pool or a process-wide registry) and should not be duplicated. A custom `__deepcopy__` can return `self` for a genuinely immutable object, but do not do this for an object whose reachable state can change.

```python
import copy

class CurrencyCode:
    __slots__ = ("value",)

    def __init__(self, value):
        object.__setattr__(self, "value", value.upper())

    def __setattr__(self, name, value):
        raise AttributeError("CurrencyCode is immutable")

    def __deepcopy__(self, memo):
        return self

usd = CurrencyCode("usd")
assert copy.deepcopy(usd) is usd
```

For production code, also consider how immutability is enforced during construction, equality, and serialization. “I intend not to mutate this” is weaker than a design that prevents mutation.

### 3.4 Testing copy contracts

Write tests for identity and mutation behavior, not just equality.

```python
import copy

source = {"items": [{"value": 1}]}
shallow = copy.copy(source)
deep = copy.deepcopy(source)

assert shallow == source == deep
assert shallow is not source
assert shallow["items"] is source["items"]
assert deep["items"] is not source["items"]

deep["items"][0]["value"] = 99
assert source["items"][0]["value"] == 1
```

A useful test suite checks: outer identity, nested identity, cycle preservation, alias preservation, and any resources intentionally shared or excluded.

---

## 4. Copy with changes: `dataclasses.replace` and `copy.replace`

### 4.1 `dataclasses.replace`

`dataclasses.replace()` creates a new dataclass instance by calling its initialization path with existing field values and requested changes. It is a shallow, field-level replacement—not a recursive clone.

```python
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class RunConfig:
    dataset: str
    retries: int
    labels: list[str]

base = RunConfig("events", 3, ["raw"])
retry_config = replace(base, retries=5)

assert retry_config is not base
assert retry_config.retries == 5
assert retry_config.labels is base.labels
```

The frozen dataclass prevents field reassignment but does not make a list field immutable. If the label list must be immutable, prefer a tuple or another immutable representation.

Be aware that dataclass `init=False` fields are not simply copied as ordinary constructor arguments; consult the dataclasses contract when using custom initialization or derived state.

### 4.2 `copy.replace` — Python 3.13+

Python 3.13 introduced `copy.replace(obj, **changes)`, a generic replacement operation for supported objects, including dataclass instances, named tuples, and classes that implement `__replace__`. It is not a general replacement for `copy.copy` or `copy.deepcopy`.

```python
import copy
from collections import namedtuple

Point = namedtuple("Point", "x y")
p1 = Point(2, 3)
p2 = copy.replace(p1, x=10)

assert p1 == Point(2, 3)
assert p2 == Point(10, 3)
```

Only run this example on Python 3.13 or newer. On Python 3.12, use `dataclasses.replace` for dataclasses or the relevant type-specific replacement method.

### 4.3 Choosing a replacement strategy

- Use `copy.copy` for shallow duplication.
- Use `copy.deepcopy` when independent nested state is genuinely required and supported.
- Use `dataclasses.replace` for dataclass records with selected changed fields.
- Use `copy.replace` on Python 3.13+ when the object's replacement protocol is supported.
- Use a named constructor or factory when a replacement must enforce complex invariants or recalculate derived state.

---

## 5. `__new__` and `__init__`

### 5.1 The distinction

- `__new__(cls, ...)` creates and returns an instance. It is a static method in behavior, although it is normally written without `@staticmethod`.
- `__init__(self, ...)` initializes an already-created instance and must return `None`.
- Python calls `__init__` only when `__new__` returns an instance of the class being constructed (or a subclass).

Most classes only need `__init__`. Override `__new__` when construction itself must control the instance, especially for immutable built-in subclasses, interning/singleton designs, or specialized allocation behavior.

### 5.2 Subclassing an immutable built-in

Immutable built-in values must usually be customized in `__new__`, because the value is established during creation.

```python
class NormalizedCode(str):
    def __new__(cls, value):
        normalized = value.strip().upper()
        return super().__new__(cls, normalized)

code = NormalizedCode("  ab-12  ")
assert code == "AB-12"
assert isinstance(code, NormalizedCode)
```

This is an example where `__init__` is not the right place to normalize the underlying string value.

### 5.3 Construction pitfalls

- Do not return a non-instance from `__new__` and expect `__init__` to run.
- Do not use `__new__` as a routine substitute for a factory function.
- Singleton patterns can introduce hidden global state and complicate tests; use only when the identity requirement is real.
- If subclassing `tuple`, `int`, or `str`, follow the built-in type's construction contract and test subclass behavior carefully.

### 5.4 `__init_subclass__` and `__set_name__`

These are class-creation hooks rather than per-instance initialization hooks.

- `__init_subclass__` runs when a subclass is created and is useful for validation or registration.
- A descriptor's `__set_name__(owner, name)` is called when the descriptor is assigned in the class body, allowing it to learn its owner and attribute name.

```python
class Plugin:
    registry = {}
    plugin_name = None

    def __init_subclass__(cls, *, name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if name is not None:
            if name in Plugin.registry:
                raise ValueError(f"duplicate plugin: {name}")
            cls.plugin_name = name
            Plugin.registry[name] = cls

class CsvPlugin(Plugin, name="csv"):
    pass

assert Plugin.registry["csv"] is CsvPlugin
```

This example uses a small class registry. In production, consider import order, duplicate registration policy, thread safety, plugin discovery, and whether Python package entry points are a better extension mechanism.

---

## 6. Pickle fundamentals

### 6.1 What pickle does

`pickle` is Python's object serialization mechanism. It converts supported Python object graphs into a byte stream and reconstructs them later. It is useful for trusted Python-to-Python persistence and some internal workflows, but it is not a language-neutral interchange format and should not be treated as a stable long-term schema by default.

```python
import pickle

payload = {"job_id": 42, "status": "complete", "columns": ["id", "value"]}
blob = pickle.dumps(payload, protocol=pickle.HIGHEST_PROTOCOL)
restored = pickle.loads(blob)
assert restored == payload
```

This example uses only a built-in dictionary. For custom classes, pickle generally relies on importable class definitions and reconstruction instructions; the class code itself is not bundled as a portable application definition.

### 6.2 Pickle protocols

A pickle protocol is a versioned encoding capability. `pickle.HIGHEST_PROTOCOL` selects the highest protocol supported by the current Python runtime. This is convenient for local same-environment use, but it may not be readable by older Python versions. Choose a protocol deliberately when interoperability with older supported runtimes matters.

```python
import pickle

value = ("partition-7", 120)
blob = pickle.dumps(value, protocol=4)
assert pickle.loads(blob) == value
```

Do not assume that selecting an older protocol makes a custom class universally portable. The class must still be importable and compatible, and the object must be supported by that protocol.

### 6.3 What is commonly picklable?

Commonly supported values include built-in containers of picklable values, many standard-library types, and instances of importable user-defined classes. Module-level functions and classes can often be referenced by module and qualified name. Lambdas, nested/local classes, open file handles, sockets, locks, database connections, and many runtime-bound resources are not directly picklable in the expected way.

```python
# Place this class at module top level in a real .py module for normal use.
class TaskSpec:
    def __init__(self, name):
        self.name = name

# In a module-level script, an instance is typically picklable if the module
# can be imported by the receiving process.
```

Interactive notebooks, REPLs, and `__main__` can behave differently across processes. Test serialization in the actual deployment context, especially when using multiprocessing or distributed workers.

### 6.4 Security: never unpickle untrusted data

**Unpickling untrusted bytes can execute arbitrary code.** Treat pickle data as executable input, not merely as passive data. Do not load pickle files from users, unknown websites, untrusted object stores, or arbitrary network sources.

Safer choices depend on the use case:

- JSON for simple, language-neutral data structures.
- MessagePack for compact structured values when the ecosystem supports it.
- Protocol Buffers or another schema-based format for explicit schemas and cross-language contracts.
- A signed/authenticated envelope can help verify origin and integrity, but signing does not make unsafe pickle payloads safe if the signing key or trust boundary is compromised.

Serialization format selection should account for schema evolution, validation, size, performance, compatibility, and threat model.

---

## 7. Custom pickle state: `__getstate__` and `__setstate__`

### 7.1 Why custom state is needed

A runtime object may combine durable data with runtime-only state. A cache may contain a dictionary that is safe to serialize, alongside a `threading.Lock` that is not. Serialize the durable state and recreate the runtime-only field during restoration.

```python
import pickle
import threading

class Cache:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("lock", None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.lock = threading.Lock()

cache = Cache()
cache.data["region"] = "ap-south-1"
restored = pickle.loads(pickle.dumps(cache))
assert restored.data == cache.data
assert restored.lock is not cache.lock
```

`__getstate__` should return the state intended for serialization. `__setstate__` restores that state and recreates or reinitializes omitted runtime-only resources. This example is for illustration; the class should live in an importable module for cross-process use.

### 7.2 State design checklist

Before pickling a class, decide:

1. Which fields represent durable business state?
2. Which fields are caches that can be recomputed?
3. Which fields hold external resources or synchronization primitives?
4. Does the restored object need validation or migration?
5. Are credentials, tokens, personal data, or secrets accidentally included?
6. Can a newer/older class definition read the stored state?

Do not serialize secrets simply because they are attributes. Prefer explicit allow-listed state over dumping every field if the object contains sensitive or volatile data.

### 7.3 Slots and state

Slotted classes and classes with custom storage may require careful state handling. Do not assume that `self.__dict__` exists when using `__slots__`. Check the exact class layout and the pickle support provided by its base classes. A simple explicit state tuple or dictionary is often easier to review than relying on implicit state details.

---

## 8. `__reduce__`, `__reduce_ex__`, and `copyreg`

### 8.1 The reconstruction model

At a lower level, pickle can ask an object for a reduction recipe describing how to reconstruct it. `__reduce_ex__(protocol)` is the protocol-aware hook; `__reduce__()` is the older/general hook. A reduction can describe a callable plus arguments and optional state/iterators. The exact tuple forms are part of the pickle protocol and should be used only when the simpler state hooks are insufficient.

Prefer `__getstate__` / `__setstate__` for ordinary state customization. Reach for a custom reduction only when reconstruction genuinely requires a custom factory or a more specialized recipe.

### 8.2 Example: custom reconstruction factory

```python
import pickle

class Endpoint:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def __reduce__(self):
        return (type(self), (self.host, self.port))

endpoint = Endpoint("warehouse.internal", 5432)
restored = pickle.loads(pickle.dumps(endpoint))
assert (restored.host, restored.port) == (endpoint.host, endpoint.port)
```

This simple example returns the class and constructor arguments. It is mainly educational; ordinary classes may already support the needed behavior without overriding `__reduce__`.

### 8.3 `copyreg`

`copyreg` lets an application register reduction functions for types that it does not own or cannot modify. Registration affects the process that performs serialization and should be treated as explicit application configuration.

```python
import copyreg
import pickle

class Coordinate:
    def __init__(self, x, y):
        self.x, self.y = x, y

def rebuild_coordinate(x, y):
    return Coordinate(x, y)

def reduce_coordinate(value):
    return (rebuild_coordinate, (value.x, value.y))

copyreg.pickle(Coordinate, reduce_coordinate)
point = Coordinate(3, 4)
restored = pickle.loads(pickle.dumps(point))
assert (restored.x, restored.y) == (3, 4)
```

The reconstruction function must be available in the receiving environment. Avoid global registrations that unexpectedly change serialization behavior across unrelated parts of a large application.

### 8.4 Copy and pickle are related, not identical

The `copy` module can use reduction support for some objects, which is why poorly designed serialization hooks can also affect copying. However, shallow copying, deep copying, and serialization have different goals. Test each public operation independently and document the intended contract.

---

## 9. Lifecycle cleanup: `__del__`, context managers, and `weakref.finalize`

### 9.1 Why `__del__` is not reliable resource management

`__del__(self)` may be called when an object is about to be finalized, but its timing is not guaranteed in a portable way. Reference cycles, interpreter shutdown, resurrection, and exceptions inside finalizers make it unsuitable for reliably closing files, sockets, transactions, or database connections.

Avoid this pattern:

```python
class BadFileOwner:
    def __init__(self, path):
        self.file = open(path, "w", encoding="utf-8")

    def __del__(self):
        # Not a reliable guarantee that the file closes at a useful time.
        self.file.close()
```

The code is syntactically valid but intentionally demonstrates a design to avoid.

### 9.2 Prefer a context manager

A context manager makes the resource lifetime explicit and deterministic on normal control-flow exit, including when exceptions occur inside the block.

```python
from pathlib import Path

path = Path("example-output.txt")
with path.open("w", encoding="utf-8") as stream:
    stream.write("completed\n")

assert path.read_text(encoding="utf-8") == "completed\n"
path.unlink()
```

For custom resources, implement `__enter__` and `__exit__`, or use `contextlib` helpers. Database transactions, locks, temporary files, and network sessions should have explicit ownership and cleanup rules.

### 9.3 `weakref.finalize`

`weakref.finalize(obj, callback, *args, **kwargs)` registers a callback that can run when the target object is about to be finalized, without requiring the target class to define `__del__`. It is often easier to reason about than `__del__`, but it is still a fallback mechanism—not a substitute for explicit resource management.

```python
import tempfile
import weakref

class TempPath:
    def __init__(self):
        handle = tempfile.NamedTemporaryFile(delete=False)
        handle.close()
        self.path = handle.name
        self._finalizer = weakref.finalize(self, self._remove, self.path)

    @staticmethod
    def _remove(path):
        import os
        try:
            os.remove(path)
        except FileNotFoundError:
            pass

item = TempPath()
assert item._finalizer.alive
item._finalizer()  # Explicitly invoke cleanup now; later finalization is disabled.
assert not item._finalizer.alive
```

Important: the callback and its arguments must not accidentally keep a strong reference to the target object, or finalization may never happen. Here the callback is a static method and receives only the path string.

### 9.4 `weakref.ref` and object reachability

A weak reference allows code to refer to an object without keeping it alive. It is useful for caches and registries where entries should not by themselves prevent object collection. Not all Python objects support weak references; slotted classes generally need a `__weakref__` slot unless a base class already provides weak-reference support.

```python
import weakref

class Session:
    pass

session = Session()
reference = weakref.ref(session)
assert reference() is session

del session
assert reference() is None
```

The example assumes ordinary CPython behavior for this simple object; write portable code around reachability and weak-reference semantics, not around assumptions about exact garbage-collection timing.

### 9.5 Object resurrection and shutdown

A finalizer can, in some circumstances, arrange for an object to become reachable again (“resurrection”). This is surprising and usually a design smell. During interpreter shutdown, module globals and logging facilities may already be partially dismantled, so cleanup code that depends on them can fail. Keep finalizers minimal and idempotent; perform essential cleanup explicitly.

---

## 10. Class-creation hooks: awareness and safe usage

This lesson's main focus is instance copying, serialization, and lifecycle. The following hooks operate at class-creation time and connect to the next metaprogramming module.

| Hook | When it runs | Typical purpose |
|---|---|---|
| `__new__` | When an instance is created | Control allocation/value creation |
| `__init__` | After instance creation | Initialize instance state |
| `__init_subclass__` | When a subclass is created | Validate or register subclasses |
| `__set_name__` | When a descriptor is assigned in a class body | Learn owner and attribute name |
| `__class_getitem__` | When `SomeClass[...]` syntax is evaluated | Generic-style class subscription |
| `__instancecheck__` / `__subclasscheck__` | During relevant `isinstance` / `issubclass` checks | Customize instance/subclass checks via a metaclass |

Do not confuse these class-definition hooks with `__del__`, which concerns instance finalization. Use the smallest hook that solves the problem; metaprogramming can make APIs harder to debug if used unnecessarily.

---

## 11. Identity, interning, and implementation details

### 11.1 Identity is not value equality

Use `is` for identity comparisons, especially `x is None`. Use `==` for value equality. Never use `is` to compare strings, numbers, timestamps, or business identifiers.

```python
first = "pipeline"
second = "pipe" + "line"
# Do not depend on whether these happen to be the same interned object.
assert first == second
```

Python implementations may intern some strings or reuse some small integer objects. These are implementation optimizations, not application contracts. `id()` is not a stable ID across process runs.

### 11.2 Caches and singleton assumptions

A cache may intentionally return the same object for repeated inputs, but make that behavior explicit in the API. Do not accidentally depend on an implementation cache for correctness. Tests should assert documented identity guarantees only.

---

## 12. Data-engineering case study: copying a pipeline configuration

Imagine an ingestion pipeline has a shared schema, per-run options, a cache, and a lock. A run-specific variant should not accidentally mutate the default options, and a lock should not be duplicated or serialized as ordinary data.

```python
import copy
import threading

class PipelineConfig:
    def __init__(self, dataset, options=None):
        self.dataset = dataset
        self.options = dict(options or {})
        self.cache = {}
        self._lock = threading.Lock()

    def for_run(self, **overrides):
        clone = copy.copy(self)
        clone.options = {**self.options, **overrides}
        clone.cache = {}  # run-scoped cache, deliberately not shared
        clone._lock = threading.Lock()  # independent synchronization primitive
        return clone

    def __getstate__(self):
        return {"dataset": self.dataset, "options": self.options}

    def __setstate__(self, state):
        self.dataset = state["dataset"]
        self.options = dict(state["options"])
        self.cache = {}
        self._lock = threading.Lock()

base = PipelineConfig("events", {"batch_size": 500, "mode": "incremental"})
retry = base.for_run(batch_size=100)
assert base.options["batch_size"] == 500
assert retry.options["batch_size"] == 100
assert retry.cache is not base.cache
```

The example's design choices are deliberate:

- Per-run options are independent dictionaries.
- The cache is recreated because it is transient state.
- The lock is recreated because it is a runtime synchronization primitive.
- Pickled state contains only the durable dataset identifier and options.

In a real system, validate configuration values, avoid serializing credentials, decide whether the cache should be shared or reset, and test compatibility across the versions you actually deploy. If the configuration is intended to be a durable cross-language contract, a schema-based format may be preferable to pickle.

---

## 13. Common mistakes and production risks

| Mistake | Why it fails | Better approach |
|---|---|---|
| Treating assignment as copying | Both names point to one object | Choose aliasing or copy explicitly |
| Assuming shallow copy isolates nested state | Child objects remain shared | Test nested identity; copy selected children or deep-copy intentionally |
| Deep-copying everything | Expensive and may duplicate identity-bearing resources | Define an ownership and sharing policy |
| Omitting `memo` handling in custom `__deepcopy__` | Cycles can recurse; aliases can be broken | Register clone in `memo` before copying children |
| Pickling locks, connections, or open files directly | These are runtime resources, not portable data | Exclude them and recreate on restore |
| Unpickling untrusted bytes | May execute arbitrary code | Use a safe data format and validate input |
| Treating pickle as a durable schema | Class paths and code changes can break compatibility | Version schemas and use explicit migrations/formats |
| Relying on `__del__` for essential cleanup | Timing is uncertain | Use context managers and explicit `close()` methods |
| Finalizer captures target strongly | Target may never become collectible | Keep finalizer callbacks independent of target |
| Assuming `frozen=True` makes nested values immutable | Nested lists/dicts can still mutate | Use immutable field types or defensive copies |
| Depending on `id()` or interning | Behavior is not a persistent identity contract | Use explicit identifiers |

---

## 14. Testing strategy

### 14.1 Copy behavior tests

Test each documented invariant: equal values, distinct outer identity, nested sharing/isolation, cycle preservation, and intentional shared state.

```python
import copy

class Box:
    def __init__(self, items):
        self.items = items

box = Box([[1]])
shallow = copy.copy(box)
deep = copy.deepcopy(box)

assert shallow is not box
assert shallow.items is box.items
assert deep.items is not box.items
assert deep.items[0] is not box.items[0]
```

### 14.2 Pickle round-trip tests

A round-trip test should verify the public contract, not necessarily identity equality with the original object.

```python
import pickle

payload = {"offset": 25, "partition": "p-3"}
restored = pickle.loads(pickle.dumps(payload))
assert restored == payload
assert restored is not payload
```

For custom classes, run tests from an importable module and include the actual supported Python versions and deployment process model. Test omitted transient state, recreated locks, validation, and schema-version migrations.

### 14.3 Test resource cleanup explicitly

Do not rely on garbage collection to prove cleanup works. Invoke `close()` or context-manager exit and assert the resource is closed. For `weakref.finalize`, test that explicit invocation performs cleanup and marks the finalizer dead; do not make fragile tests that depend on an exact time when garbage collection runs.

### 14.4 Suggested pytest tests

```python
import copy
import pytest

@pytest.mark.parametrize("operation", [copy.copy, copy.deepcopy])
def test_copy_returns_distinct_outer_container(operation):
    original = {"values": [1, 2]}
    duplicate = operation(original)
    assert duplicate == original
    assert duplicate is not original
```

Extend this with assertions about nested identity appropriate to each operation. Parametrization is useful, but do not assert the same nested-object contract for shallow and deep copy.

---

## 15. Exercises

### Beginner

1. Create a list, assign it to a second name, mutate through the second name, and explain the result using `is`.
2. Create a nested dictionary and compare assignment, `copy.copy`, and `copy.deepcopy` by checking outer and inner identity.
3. Explain why `id(obj)` is not a suitable persistent database primary key.
4. Use `dataclasses.replace` to create a run configuration with a different retry count; test whether nested fields are shared.

### Intermediate

5. Implement a `__copy__` method for a `PipelineConfig` that copies run-specific options but shares an immutable schema object.
6. Implement `__deepcopy__` for a `Node` graph that contains both cycles and repeated references. Prove that the copied graph preserves both relationships.
7. Add `__getstate__` and `__setstate__` to a class containing a dictionary and `threading.Lock`; prove that data is restored and the lock is new.
8. Write a top-level class in an importable module and test a pickle round trip in a fresh Python process.
9. Replace a `__del__`-based file cleanup example with a context manager.

### Advanced

10. Design a versioned serialized state format and a migration function from version 1 to version 2. Explain why pickle alone does not solve schema evolution.
11. Compare `__reduce__` with `__getstate__` / `__setstate__`; justify the simpler option for a class of your choice.
12. Implement a `weakref.finalize` fallback for a temporary resource while preserving an explicit `close()` API. Ensure the callback does not strongly reference the owner.
13. Review a dataclass containing a mutable list and a cache. Decide which fields should be immutable, copied, recomputed, or omitted from serialized state.
14. Write a threat-model note explaining why signing a pickle is not a substitute for avoiding untrusted unpickling.

## 16. Selected solutions and reasoning

### Solution 1: assignment aliases

```python
items = ["extract"]
other_name = items
other_name.append("load")
assert items == ["extract", "load"]
assert other_name is items
```

Both names refer to one list. No new list was created.

### Solution 2: shallow vs deep copy

```python
import copy
source = {"nested": [1]}
shallow = copy.copy(source)
deep = copy.deepcopy(source)
assert shallow is not source
assert shallow["nested"] is source["nested"]
assert deep["nested"] is not source["nested"]
```

The shallow copy creates an independent outer dictionary, while deep copy also copies the nested list.

### Solution 7: exclude and recreate a lock

Use the `Cache` implementation in Section 7.1. The key invariants are that the serialized state contains the durable data only and that `__setstate__` constructs a new `threading.Lock` after restoring the dictionary.

### Solution 9: deterministic cleanup

Use a `with` statement around the file or implement `__enter__` / `__exit__` on a resource-owning class. Essential cleanup should be explicit and tested; `__del__` may be a last-resort safety net but should not be the only cleanup path.

---

## 17. Quick reference

| Need | Preferred tool | Important caveat |
|---|---|---|
| Another reference to same object | Assignment | Mutations are shared |
| New outer container | `copy.copy` | Nested references usually remain shared |
| Independent supported object graph | `copy.deepcopy` | Expensive; custom objects/resources need care |
| Change fields on a dataclass | `dataclasses.replace` | Shallow field reuse; initialization rules apply |
| Generic replacement (Python 3.13+) | `copy.replace` | Requires a supported object / `__replace__` implementation |
| Customize shallow copy | `__copy__` | Document which fields are shared |
| Customize deep copy | `__deepcopy__(memo)` | Memoize clone before recursive copying |
| Serialize trusted Python object state | `pickle` | Never unpickle untrusted input |
| Exclude/recreate transient state | `__getstate__`, `__setstate__` | Plan schema evolution and secret handling |
| Custom reconstruction recipe | `__reduce_ex__`, `__reduce__`, `copyreg` | Use only when simpler hooks are insufficient |
| Deterministic resource cleanup | Context manager / `close()` | Explicit ownership and error handling |
| Fallback cleanup callback | `weakref.finalize` | Callback must not retain target strongly |
| Create immutable subclass value | `__new__` | Follow base type construction contract |
| Validate/register subclasses | `__init_subclass__` | Class-creation hook, not instance lifecycle |

## 18. Completion checklist

- [ ] I can explain aliasing with `is` and value equality with `==`.
- [ ] I can predict the effects of shallow and deep copying on nested mutable state.
- [ ] I can implement `__deepcopy__` with cycle and alias preservation.
- [ ] I can choose between copy, deep copy, and copy-with-changes based on ownership requirements.
- [ ] I can explain when `__new__` is necessary and how it differs from `__init__`.
- [ ] I can serialize and restore a class while excluding locks or other runtime-only state.
- [ ] I understand `__reduce__` / `__reduce_ex__` and when not to use them.
- [ ] I can explain the security risk of unpickling untrusted data.
- [ ] I use context managers for essential resource cleanup and understand the limits of finalizers.
- [ ] I can explain `weakref.finalize`, `__init_subclass__`, and `__set_name__` at a practical level.
- [ ] I have tests for identity, nested state, round trips, and cleanup behavior.

## Recommended study sequence

1. Type and run Sections 1–2; predict identities before executing.
2. Implement the custom copy examples in Section 3 and deliberately remove the memo assignment to observe why cycle handling matters.
3. Run the `dataclasses.replace` example; if using Python 3.13+, run the `copy.replace` example too.
4. Run pickle examples only with trusted local data; test in an importable module.
5. Compare custom state hooks with the `__reduce__` example and write down why one is simpler for your use case.
6. Replace finalizer-only cleanup with explicit context management and add tests.
7. Complete exercises 5–14 and include the resulting code in your module mini-project.

**Module connection:** This lesson completes Module 11's data-model series. The next module, **Metaprogramming and Dynamic Python**, builds on class-creation hooks, descriptors, and runtime type behavior.
