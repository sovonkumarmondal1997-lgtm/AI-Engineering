# Lesson 10 — Abstract Base Classes and `collections.abc`

**Stage 1 — Programming & Computational Thinking**  
**Module 11 — Advanced Python Data Model and Object Design**  
**Target:** Python 3.12+  
**Level:** Beginner → Intermediate → Advanced  
**Primary goal:** Design reliable interfaces for interchangeable implementations, and use Python's standard abstract collection classes without overengineering.

---

## 1. Learning outcomes

By the end of this lesson, you should be able to:

1. Explain the difference between an interface, an abstract class, and a concrete class.
2. Define an ABC using `abc.ABC` and `@abstractmethod`, and explain why an incomplete subclass cannot be instantiated.
3. Implement abstract instance methods, properties, class methods, and static methods with correct decorator order.
4. Use concrete methods in an ABC to implement a template method and centralize invariant behavior.
5. Choose the appropriate `collections.abc` abstraction: `Iterable`, `Iterator`, `Collection`, `Sequence`, `Mapping`, `MutableMapping`, `Set`, and related ABCs.
6. Implement a mapping by writing only its core primitives and reuse methods supplied by `Mapping`.
7. Distinguish nominal inheritance, virtual subclass registration, structural checks, duck typing, and `typing.Protocol`.
8. Explain the role of `ABCMeta`, `__abstractmethods__`, `register()`, and `__subclasshook__`.
9. Select an interface for a data-engineering component such as a source, sink, serializer, or configuration store.
10. Test interface contracts, edge cases, and alternative implementations without coupling tests to implementation details.

## 2. Prerequisites and setup

You should already understand classes, inheritance, overriding, `super()`, type hints, exceptions, iterables, and unit tests. The preceding lessons in this module cover container protocols and mixins; this lesson builds on them.

Use Python 3.12 or newer and a project environment with `pytest`. The examples use only the Python standard library unless a test example explicitly mentions pytest.

Verify your interpreter:

```python
import sys
print(sys.version)
```

**Core idea:** an interface describes what an object can do. An abstract base class can define that contract and provide reusable implementation. A concrete class supplies the missing behavior needed to create usable instances.

---

## 3. The problem ABCs solve

Imagine a batch pipeline that writes records to a CSV file, an object store, or a test sink. The pipeline should call the same operation regardless of the storage backend. Without a shared contract, each implementation can invent a different method name or signature, and the pipeline discovers the mismatch only when it runs.

```python
class CsvSink:
    def write_batch(self, rows):
        print(f"CSV: writing {len(rows)} rows")

class ObjectStoreSink:
    def put_records(self, rows):
        print(f"Object store: writing {len(rows)} rows")
```

These classes perform similar jobs but do not expose the same interface. A caller must know which class it received:

```python
def publish(sink, rows):
    if isinstance(sink, CsvSink):
        sink.write_batch(rows)
    elif isinstance(sink, ObjectStoreSink):
        sink.put_records(rows)
    else:
        raise TypeError("unsupported sink")
```

This branching becomes difficult to maintain as implementations grow. An interface provides one stable contract, such as `write_batch(rows)`, so the caller can depend on behavior rather than concrete classes.

### The three terms

| Term | Meaning | Example |
|---|---|---|
| Interface/contract | The operations and behavior a caller may rely on | A sink supports `write_batch(rows)` |
| Abstract base class (ABC) | A class that can declare required methods and shared behavior | `class Sink(ABC)` |
| Concrete class | A class that can be instantiated and provides required implementations | `class CsvSink(Sink)` |

An ABC is useful when you want explicit inheritance and runtime enforcement that required abstract methods have been implemented. It is not the only way to define an interface in Python; duck typing and `Protocol` are often better choices for other situations.

---

## 4. Your first abstract base class

### 4.1 `ABC` and `@abstractmethod`

`abc.ABC` is a convenient base class that uses `ABCMeta`. Decorate a required method with `@abstractmethod`. A class with unresolved abstract methods cannot be instantiated.

```python
from abc import ABC, abstractmethod

class Exporter(ABC):
    @abstractmethod
    def serialize(self, records: list[dict[str, object]]) -> bytes:
        """Convert records into the export format."""
        raise NotImplementedError

class JsonLinesExporter(Exporter):
    import json

    def serialize(self, records: list[dict[str, object]]) -> bytes:
        import json
        text = "".join(json.dumps(row) + "\n" for row in records)
        return text.encode("utf-8")

payload = JsonLinesExporter().serialize([{"id": 1}, {"id": 2}])
assert payload == b'{"id": 1}\n{"id": 2}\n'
```

The abstract method's body is not what makes it abstract; the decorator does. Raising `NotImplementedError` is a useful defensive body, but the abstractness check is performed by the ABC machinery.

The following is an intentionally incomplete class. It is valid to define, but instantiating it raises `TypeError`:

```python
from abc import ABC, abstractmethod

class Reader(ABC):
    @abstractmethod
    def read(self) -> bytes:
        ...

class UnfinishedReader(Reader):
    pass

# Expected behavior when run separately:
# UnfinishedReader()  -> TypeError: Can't instantiate abstract class ...
```

### 4.2 What gets checked, and when?

Python normally checks abstract methods when you **instantiate** a class, not when the class statement is executed. The class can exist and be subclassed, but construction is blocked while required abstract methods remain unresolved.

```python
from abc import ABC, abstractmethod

class Transformer(ABC):
    @abstractmethod
    def transform(self, value: str) -> str:
        ...

class Uppercase(Transformer):
    def transform(self, value: str) -> str:
        return value.upper()

assert Uppercase().transform("daily") == "DAILY"
assert Transformer.__abstractmethods__ == frozenset({"transform"})
assert Uppercase.__abstractmethods__ == frozenset()
```

`__abstractmethods__` is useful for introspection and debugging, but application code should usually depend on the public contract rather than manually modifying this attribute.

### 4.3 Abstract method signatures are a design contract

Python does not automatically prove that a subclass's method has a compatible signature or correct semantics. Static type checkers can catch many signature mismatches; tests must verify behavior.

```python
from abc import ABC, abstractmethod

class BatchSink(ABC):
    @abstractmethod
    def write_batch(self, rows: list[dict[str, object]]) -> int:
        """Write rows and return the number accepted."""
        ...

class InMemorySink(BatchSink):
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def write_batch(self, rows: list[dict[str, object]]) -> int:
        self.rows.extend(rows)
        return len(rows)

sink = InMemorySink()
assert sink.write_batch([{"id": 1}]) == 1
assert sink.rows == [{"id": 1}]
```

For production interfaces, document return values, exception behavior, ordering, idempotency, retry expectations, and whether the method is synchronous or asynchronous. A method name alone is not a complete contract.

---

## 5. Abstract classes can provide concrete behavior

An ABC does not have to be a list of empty methods. It can contain fully implemented methods that rely on one or more abstract primitives. This is the **Template Method** pattern: the base class defines the stable workflow, while subclasses supply selected steps.

```python
from abc import ABC, abstractmethod

class Exporter(ABC):
    @abstractmethod
    def serialize(self, records: list[dict[str, object]]) -> bytes:
        """Serialize records into bytes."""
        ...

    def export(self, records: list[dict[str, object]], path: str) -> int:
        """Serialize and write bytes; return the byte count."""
        payload = self.serialize(records)
        with open(path, "wb") as stream:
            stream.write(payload)
        return len(payload)
```

The shared `export()` method centralizes file handling. Every concrete exporter inherits the same write path, reducing duplicated behavior and making it easier to apply consistent logging, validation, or metrics.

A test implementation can override only the primitive and still inherit the workflow:

```python
from abc import ABC, abstractmethod

class PrefixExporter(ABC):
    @abstractmethod
    def serialize(self, records: list[str]) -> bytes:
        ...

    def prepare_payload(self, records: list[str]) -> bytes:
        if not records:
            return b""
        return self.serialize(records)

class PipeExporter(PrefixExporter):
    def serialize(self, records: list[str]) -> bytes:
        return "|".join(records).encode("utf-8")

assert PipeExporter().prepare_payload(["a", "b"]) == b"a|b"
assert PipeExporter().prepare_payload([]) == b""
```

### When to use a template method

Use it when the overall workflow should remain consistent across implementations but specific steps vary. Do not force unrelated implementations into one workflow merely because they share a few method names.

---

## 6. Abstract properties, class methods, and static methods

ABCs can require more than ordinary instance methods. Decorator order matters because `@abstractmethod` must be applied to the underlying function/property descriptor.

### 6.1 Abstract property

```python
from abc import ABC, abstractmethod

class DataSource(ABC):
    @property
    @abstractmethod
    def source_name(self) -> str:
        """A stable human-readable identifier for the source."""
        ...

class ApiSource(DataSource):
    @property
    def source_name(self) -> str:
        return "orders-api"

assert ApiSource().source_name == "orders-api"
```

If the base requires both reading and writing a property, declare the relevant abstract accessors explicitly. A subclass can implement the property according to the contract.

### 6.2 Abstract class method

Put `@classmethod` outside `@abstractmethod` (outermost decorator first in source order):

```python
from abc import ABC, abstractmethod

class Connector(ABC):
    @classmethod
    @abstractmethod
    def from_config(cls, config: dict[str, str]) -> "Connector":
        """Construct the appropriate connector from configuration."""
        ...

class MemoryConnector(Connector):
    def __init__(self, namespace: str) -> None:
        self.namespace = namespace

    @classmethod
    def from_config(cls, config: dict[str, str]) -> "MemoryConnector":
        return cls(config.get("namespace", "default"))

assert MemoryConnector.from_config({"namespace": "test"}).namespace == "test"
```

### 6.3 Abstract static method

```python
from abc import ABC, abstractmethod

class Validator(ABC):
    @staticmethod
    @abstractmethod
    def supports(value: object) -> bool:
        ...

class StringValidator(Validator):
    @staticmethod
    def supports(value: object) -> bool:
        return isinstance(value, str)

assert StringValidator.supports("ok")
assert not StringValidator.supports(10)
```

### Decorator-order rule of thumb

- Instance method: `@abstractmethod` directly above `def`.
- Property: `@property` above `@abstractmethod`.
- Class method: `@classmethod` above `@abstractmethod`.
- Static method: `@staticmethod` above `@abstractmethod`.

For abstract properties with setters, follow the standard `property` accessor pattern and test the concrete implementation rather than relying on decorator intuition alone.

---

## 7. `collections.abc`: standard collection contracts

The `collections.abc` module contains ABCs describing common container and callable behaviors. Some are mostly labels for a capability; others provide useful implementations of methods based on a small number of required primitives.

Import from `collections.abc` for runtime ABCs. For type annotations, `typing` and built-in generic types may also be relevant; they serve a related but not identical purpose.

### 7.1 Important ABCs at a glance

| ABC | Informal contract | Typical required primitives for explicit subclassing |
|---|---|---|
| `Iterable` | Can produce an iterator | `__iter__` |
| `Iterator` | Produces values one at a time and is itself an iterator | `__next__` and `__iter__` returning self |
| `Sized` | Has a length | `__len__` |
| `Container` | Supports membership tests | `__contains__` |
| `Collection` | Iterable, sized, and supports containment | `__len__`, `__iter__`, `__contains__` |
| `Sequence` | Ordered, integer-indexed collection | `__getitem__`, `__len__` |
| `MutableSequence` | Mutable ordered collection | sequence primitives plus mutation methods |
| `Mapping` | Read-only mapping interface | `__getitem__`, `__iter__`, `__len__` |
| `MutableMapping` | Mutable mapping interface | mapping primitives plus `__setitem__`, `__delitem__` |
| `Set` | Mathematical set operations | `__contains__`, `__iter__`, `__len__` |
| `MutableSet` | Mutable set | set primitives plus `add`, `discard` |
| `Hashable` | Has a usable hash | `__hash__` that returns an integer |
| `Callable` | Can be called | `__call__` |
| `Reversible` | Can be iterated in reverse | `__reversed__` |
| `AsyncIterable` / `AsyncIterator` | Asynchronous iteration | `__aiter__` / `__anext__` contracts |

This table is a practical guide, not a replacement for the exact API documentation. Some ABCs provide default implementations, and ABCs may recognize classes structurally through `__subclasshook__` or virtual registration.

### 7.2 The collection capability ladder

`Collection` combines three useful capabilities:

- `Iterable`: `for item in collection` works.
- `Sized`: `len(collection)` works.
- `Container`: `item in collection` works.

`Sequence` adds ordered indexing semantics. `Mapping` describes key-based access rather than integer-position access. Choose the narrowest useful contract for the consumer, not the concrete type you happen to use today.

```python
from collections.abc import Collection, Mapping, Sequence

numbers: Sequence[int] = (10, 20, 30)
config: Mapping[str, str] = {"region": "ap-south-1"}
labels: Collection[str] = {"bronze", "silver"}

assert numbers[0] == 10
assert config["region"] == "ap-south-1"
assert "bronze" in labels
assert len(labels) == 2
```

Annotations do not convert values or enforce runtime contracts by themselves. These annotations communicate what the function expects to callers and type checkers.

---

## 8. Use `Mapping` to build a read-only configuration view

A key benefit of collection ABCs is **mix-in methods**. If a class explicitly subclasses `Mapping` and implements its core primitives, it inherits helpful operations such as `get()`, `keys()`, `items()`, `values()`, membership behavior, and mapping equality.

For `Mapping`, the central methods are:

- `__getitem__(key)` — return the value or raise `KeyError` for a missing key.
- `__iter__()` — iterate over keys.
- `__len__()` — number of keys.

### 8.1 A small `Mapping` implementation

```python
from collections.abc import Mapping, Iterator

class FrozenConfig(Mapping[str, object]):
    def __init__(self, data: Mapping[str, object]) -> None:
        self._data = dict(data)

    def __getitem__(self, key: str) -> object:
        return self._data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

config = FrozenConfig({"region": "ap-south-1", "retries": 3})
assert config["region"] == "ap-south-1"
assert config.get("timeout", 30) == 30
assert "retries" in config
assert list(config.keys()) == ["region", "retries"]
assert list(config.items()) == [("region", "ap-south-1"), ("retries", 3)]
assert config == {"region": "ap-south-1", "retries": 3}
```

The implementation copies the input dictionary, so later changes to the original input dictionary do not affect it. However, this is only a **shallow** copy: if values themselves are mutable objects, those nested objects are still shared. Also, `Mapping` does not provide mutation methods through its interface, but the class is not deeply immutable by magic. Avoid exposing `_data` as public API.

### 8.2 Contract details that matter

- A missing key should raise `KeyError`, not return `None` silently.
- `__iter__` should yield keys, not `(key, value)` pairs.
- `__len__` should be consistent with iteration.
- Iteration order follows the underlying mapping's order; built-in dictionaries preserve insertion order.
- A read-only interface does not guarantee thread safety or deep immutability.

### 8.3 Why the mix-in methods are valuable

If you manually implement every method, you create more code to test and more opportunities for inconsistency. Inheriting `Mapping` gives users a familiar mapping API while you implement only the essential behavior.

```python
from collections.abc import Mapping, Iterator

class DemoConfig(Mapping[str, object]):
    def __init__(self, data: dict[str, object]) -> None:
        self._data = dict(data)
    def __getitem__(self, key: str) -> object:
        return self._data[key]
    def __iter__(self) -> Iterator[str]:
        return iter(self._data)
    def __len__(self) -> int:
        return len(self._data)

config = DemoConfig({"mode": "batch", "workers": 4})
assert config.get("workers") == 4
assert config.get("missing") is None
assert list(config.values()) == ["batch", 4]
assert dict(config) == {"mode": "batch", "workers": 4}
```

Do not subclass an ABC merely to gain a few convenient methods if the object does not actually satisfy that abstraction's semantics. A class that behaves unlike a mapping should not claim to be a `Mapping` just because it has a dictionary internally.

---

## 9. Implementing a `MutableMapping`

`MutableMapping` extends `Mapping` with assignment and deletion. Implement `__setitem__` and `__delitem__` in addition to the read-only mapping primitives. The ABC supplies other familiar operations such as `pop`, `popitem`, `clear`, `update`, and `setdefault` using those primitives.

```python
from collections.abc import MutableMapping, Iterator

class ValidatedConfig(MutableMapping[str, str]):
    def __init__(self, data: dict[str, str] | None = None) -> None:
        self._data: dict[str, str] = {}
        if data:
            self.update(data)

    def __getitem__(self, key: str) -> str:
        return self._data[key]

    def __setitem__(self, key: str, value: str) -> None:
        if not key or key.strip() != key:
            raise ValueError("keys must be non-empty and have no outer whitespace")
        if not isinstance(value, str):
            raise TypeError("configuration values must be strings")
        self._data[key] = value

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

settings = ValidatedConfig({"environment": "prod"})
settings["region"] = "ap-south-1"
settings.update({"log_level": "INFO"})
assert settings.pop("log_level") == "INFO"
assert dict(settings) == {"environment": "prod", "region": "ap-south-1"}
```

Notice that `update()` routes through the class's mutation interface, allowing the validation to be applied consistently. This is one reason ABC mix-ins can be safer than reimplementing a collection API from scratch.

### Practical design caution

`MutableMapping` defines API behavior, not storage strategy. It does not make your implementation transactional, thread-safe, durable, or suitable for concurrent writes. Those are separate operational requirements that must be designed and tested explicitly.

---

## 10. Other collection ABCs and when to choose them

### 10.1 `Sequence` versus `list`

Accept `Sequence[T]` if the consumer needs indexing, length, and iteration but does not need mutation. This allows tuples and other sequence implementations as well as lists.

```python
from collections.abc import Sequence

def first_nonempty(values: Sequence[str]) -> str | None:
    for value in values:
        if value:
            return value
    return None

assert first_nonempty(("", "orders", "customers")) == "orders"
assert first_nonempty(["", "events"]) == "events"
```

Use `MutableSequence[T]` only when the consumer truly needs operations such as insertion, assignment, and deletion by index.

### 10.2 `Iterable` versus `Iterator`

An iterable can produce an iterator; an iterator returns the next item from itself and is usually stateful and exhausted after use. Do not annotate an input as `Iterator[T]` when any reusable iterable would work.

```python
from collections.abc import Iterable, Iterator

def count_items(values: Iterable[object]) -> int:
    return sum(1 for _ in values)

def take_two(values: Iterator[int]) -> list[int]:
    result: list[int] = []
    for _ in range(2):
        try:
            result.append(next(values))
        except StopIteration:
            break
    return result

assert count_items([1, 2, 3]) == 3
assert take_two(iter([10, 20, 30])) == [10, 20]
```

A generator object is an iterator. A list is iterable but is not itself an iterator; `iter(list_value)` produces an iterator.

### 10.3 `Callable`

Use `Callable[[InputType], ReturnType]` in annotations when a function or callable object is accepted as a dependency. For complex signatures, `Protocol` with `__call__` may communicate the contract more clearly.

### 10.4 `Hashable`

A value being hashable means it can provide a stable hash for its lifetime and can be used in hash-based collections under Python's equality/hash rules. It does not mean the object is cryptographically secure or that its hash is stable across processes.

### 10.5 `Set` and `MutableSet`

`Set` describes set-like membership and mathematical operations. `MutableSet` adds mutation operations. The implementation must preserve set semantics: uniqueness, membership consistency, and correct equality/hash behavior for elements.

### 10.6 Asynchronous iteration

`AsyncIterable` and `AsyncIterator` describe `async for` contracts. Do not confuse them with ordinary `Iterable` and `Iterator`. A network stream, asynchronous database cursor, or message consumer may expose asynchronous iteration because retrieving each next value can require awaiting I/O.

---

## 11. Nominal ABCs, duck typing, and `Protocol`

These approaches solve related but different problems. The right choice depends on whether you need runtime enforcement, inheritance-based reuse, static structural typing, or simply a flexible caller.

### 11.1 Nominal inheritance

A class explicitly inherits from an ABC:

```python
from abc import ABC, abstractmethod

class RecordReader(ABC):
    @abstractmethod
    def read_records(self) -> list[dict[str, object]]:
        ...

class MemoryReader(RecordReader):
    def read_records(self) -> list[dict[str, object]]:
        return [{"id": 1}]

reader = MemoryReader()
assert isinstance(reader, RecordReader)
```

Advantages: explicit relationship, abstract-method enforcement, shared implementations, and a clear place to document the contract. Trade-off: a third-party class that already has the right methods is not automatically a subclass.

### 11.2 Duck typing

Duck typing asks whether an object supports the operation the caller needs. It avoids requiring a particular class relationship.

```python
def read_and_count(reader: object) -> int:
    # This version deliberately uses a small runtime check at the boundary.
    method = getattr(reader, "read_records", None)
    if not callable(method):
        raise TypeError("reader must provide read_records()")
    return len(method())

class ThirdPartyReader:
    def read_records(self) -> list[dict[str, object]]:
        return [{"id": 1}, {"id": 2}]

assert read_and_count(ThirdPartyReader()) == 2
```

Duck typing is often the most Pythonic choice for small internal boundaries. However, `getattr` checks only method presence and callability; it does not prove the signature, return type, or semantics. Type hints and tests remain valuable.

### 11.3 Structural typing with `Protocol`

A `typing.Protocol` describes the members a type must provide without requiring inheritance. Static type checkers can use it to verify compatibility.

```python
from typing import Protocol

class RecordReader(Protocol):
    def read_records(self) -> list[dict[str, object]]:
        ...

class VendorReader:
    def read_records(self) -> list[dict[str, object]]:
        return [{"source": "vendor"}]

def process(reader: RecordReader) -> int:
    return len(reader.read_records())

assert process(VendorReader()) == 1
```

The class does not need to inherit from `RecordReader`. A static checker can verify the shape when configured and run against the code. The `Protocol` declaration alone does not enforce anything at runtime.

### 11.4 `@runtime_checkable` is not a full validator

A protocol can be marked `@runtime_checkable` to allow limited `isinstance` checks. These checks are primarily about member presence, not full type-signature validation or semantic correctness.

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class HasClose(Protocol):
    def close(self) -> None:
        ...

class FileLike:
    def close(self) -> None:
        self.closed = True

assert isinstance(FileLike(), HasClose)
```

Do not use runtime-checkable protocols as a substitute for validating untrusted input or checking method signatures. Runtime behavior of protocol checks has version-specific details; use them for lightweight capability checks, not comprehensive validation.

### 11.5 Decision table

| Need | Good starting choice | Why |
|---|---|---|
| Shared implementation plus required methods | ABC | Contract and reusable behavior in one place |
| Enforce implementation of abstract methods at instantiation | ABC | Python blocks instantiation of incomplete concrete subclasses |
| Accept unrelated implementations with static checking | `Protocol` | Structural compatibility without forced inheritance |
| Small local function needs one operation | Duck typing | Minimal ceremony; depend only on what is used |
| Reuse collection semantics such as `get`, `items`, `pop` | `collections.abc` ABC | Standard contract and tested mix-in methods |
| Check only a simple runtime capability | Carefully chosen `isinstance`/callable check | Lightweight boundary check, with limitations documented |

Do not make every interface an ABC. Interfaces are valuable when they clarify a stable boundary; unnecessary abstractions make small code harder to navigate.

---

## 12. Virtual subclasses with `register()`

An ABC can recognize a class as a **virtual subclass** without requiring it to inherit from the ABC. Registration affects `issubclass()` and `isinstance()` checks, but it does not add methods to the class and does not insert the ABC into the class's method resolution order.

```python
from abc import ABC, abstractmethod

class Plugin(ABC):
    @abstractmethod
    def run(self) -> str:
        ...

class LegacyPlugin:
    def run(self) -> str:
        return "legacy result"

Plugin.register(LegacyPlugin)

plugin = LegacyPlugin()
assert isinstance(plugin, Plugin)
assert issubclass(LegacyPlugin, Plugin)
assert LegacyPlugin.__mro__ == (LegacyPlugin, object)
assert plugin.run() == "legacy result"
```

The registration example is appropriate only if `LegacyPlugin` really honors the contract. The ABC does not verify that it has a compatible `run()` method before registering it. Registering an incomplete class can make `isinstance()` say yes while later calls fail.

### Virtual subclass versus ordinary subclass

| Behavior | Explicit subclass | Registered virtual subclass |
|---|---|---|
| Appears in `isinstance` / `issubclass` | Yes | Yes |
| ABC is in the class MRO | Yes | No |
| Inherits ABC concrete methods | Yes | No |
| Abstract-method instantiation enforcement applies through this ABC | Yes | No |
| Can use `super()` to reach ABC implementations | Yes, according to MRO | No, not through registration alone |

Use virtual registration when interoperability with a pre-existing type is useful and you can trust its contract. It is not a method-injection mechanism.

---

## 13. `__subclasshook__`: custom structural recognition

An ABC may customize subclass checks with `__subclasshook__`. A common pattern returns `True` when the class provides a required capability, `False` when it is definitely incompatible, or `NotImplemented` to allow normal subclass/registration checks to continue.

```python
from abc import ABC, abstractmethod

class SupportsFlush(ABC):
    @abstractmethod
    def flush(self) -> None:
        ...

    @classmethod
    def __subclasshook__(cls, candidate: type) -> object:
        if cls is SupportsFlush:
            if any("flush" in base.__dict__ for base in candidate.__mro__):
                return True
        return NotImplemented

class Buffer:
    def flush(self) -> None:
        self.flushed = True

assert issubclass(Buffer, SupportsFlush)
assert isinstance(Buffer(), SupportsFlush)
```

This is a deliberately minimal capability check. It does not guarantee that `flush` is callable, that its signature is compatible, or that it performs the expected operation. For a real ABC, document the limits of the check and avoid treating attribute presence as proof of semantic correctness.

### Important rules

- Usually guard the custom behavior with `if cls is YourABC` so it does not accidentally apply to unrelated subclasses of the ABC.
- Return `NotImplemented` when the hook has no opinion; do not use `False` as a generic “not sure” result.
- The hook is part of subclass recognition, not a replacement for a complete test suite.
- Avoid complicated introspection logic unless there is a clear interoperability need.

`collections.abc.Iterable` is a useful cautionary example: `isinstance(obj, Iterable)` does not detect every object that Python can iterate through the legacy `__getitem__` fallback. For reliable capability checks, prefer `iter(obj)` in a guarded runtime check when that is what the code actually needs.

```python
from collections.abc import Iterable

class LegacySequence:
    def __getitem__(self, index: int) -> int:
        if index >= 3:
            raise IndexError
        return index * 10

legacy = LegacySequence()
assert list(legacy) == [0, 10, 20]
assert not isinstance(legacy, Iterable)

try:
    iter(legacy)
except TypeError:
    raise AssertionError("legacy sequence protocol should be iterable")
```

The final `try` block is a successful runtime check: `iter(legacy)` returns an iterator because Python supports the legacy sequence protocol even though the object does not explicitly define `__iter__` and is not recognized by the `Iterable` ABC check.

---

## 14. The `numbers` ABC tower

The `numbers` module describes numeric categories such as `Number`, `Complex`, `Real`, `Rational`, and `Integral`. These are ABCs intended to express numeric behavior and relationships, not to replace concrete numeric types.

```python
from numbers import Number, Real, Integral
from decimal import Decimal
from fractions import Fraction

assert isinstance(5, Number)
assert isinstance(5, Integral)
assert isinstance(3.5, Real)
assert isinstance(Fraction(1, 2), Real)
assert isinstance(Decimal("1.5"), Number)
assert not isinstance(Decimal("1.5"), Real)
```

`Decimal` is a `Number`, but it is not registered as a `Real`; this distinction helps explain why numeric ABC checks do not mean every numeric type interoperates with every other numeric type. For financial and precision-sensitive workloads, choose the numeric representation deliberately and test mixed-type operations.

Use numeric ABCs when the contract is genuinely mathematical and broad numeric interoperability is intended. If a function specifically requires a concrete operation or precision model, document that requirement rather than assuming the numeric tower guarantees every operation.

---

## 15. `ABCMeta`, abstract-method bookkeeping, and metaclass conflicts

`abc.ABC` uses `ABCMeta`, a metaclass that tracks abstract methods and prevents incomplete classes from being instantiated. You rarely need to create `ABCMeta` classes directly; subclassing `ABC` is usually enough.

### 15.1 How the enforcement works conceptually

1. `@abstractmethod` marks a method or supported descriptor as abstract.
2. During class creation, ABC machinery calculates the abstract methods remaining on the class.
3. Concrete overrides resolve the corresponding abstract requirements.
4. If unresolved abstract methods remain, construction raises `TypeError`.

This is a runtime construction check. It does not prove that a method's implementation is correct, efficient, safe, or semantically compatible.

### 15.2 Metaclass conflicts

A class can have only one effective metaclass, and that metaclass must be compatible with the metaclasses of its bases. If one base requires `ABCMeta` and another uses an incompatible custom metaclass, Python may reject the class definition with a metaclass conflict.

Do not solve this by blindly writing a new metaclass. First consider whether both inheritance relationships are necessary. Composition, a `Protocol`, or a simpler ABC boundary is often easier to maintain. If both metaclasses are truly required, a deliberately combined metaclass may be possible, but it should be an advanced, tested design decision.

### 15.3 Abstract methods can have implementations

An abstract method may contain a useful implementation. A subclass can override it and call `super()` to reuse that implementation, provided the inheritance design is intentional.

```python
from abc import ABC, abstractmethod

class BaseParser(ABC):
    @abstractmethod
    def parse(self, text: str) -> list[str]:
        """Return parsed tokens."""
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        return text.split()

class UppercaseParser(BaseParser):
    def parse(self, text: str) -> list[str]:
        tokens = super().parse(text)
        return [token.upper() for token in tokens]

assert UppercaseParser().parse("orders ready") == ["ORDERS", "READY"]
```

The base implementation does not make `BaseParser` instantiable while `parse` remains abstract. It can still provide reusable behavior to concrete subclasses.

---

## 16. ABCs and plugin architecture

ABCs can make plugin boundaries explicit. For example, a data platform may support multiple source connectors. Each connector implements the same required method, while the orchestration code depends on the abstraction rather than a particular vendor.

```python
from abc import ABC, abstractmethod

class RecordSource(ABC):
    @abstractmethod
    def read_batch(self, limit: int) -> list[dict[str, object]]:
        """Read up to limit records; return an empty list at end of input."""
        ...

class InMemorySource(RecordSource):
    def __init__(self, records: list[dict[str, object]]) -> None:
        self._records = list(records)
        self._position = 0

    def read_batch(self, limit: int) -> list[dict[str, object]]:
        if limit <= 0:
            raise ValueError("limit must be positive")
        start = self._position
        stop = min(start + limit, len(self._records))
        self._position = stop
        return self._records[start:stop]

def consume(source: RecordSource, batch_size: int) -> list[dict[str, object]]:
    all_records: list[dict[str, object]] = []
    while True:
        batch = source.read_batch(batch_size)
        if not batch:
            return all_records
        all_records.extend(batch)

source = InMemorySource([{"id": 1}, {"id": 2}, {"id": 3}])
assert consume(source, 2) == [{"id": 1}, {"id": 2}, {"id": 3}]
```

### Contract questions a senior engineer asks

The signature alone is not enough. Before shipping a connector interface, decide:

- Does `read_batch(0)` return an empty list or raise `ValueError`?
- Is end-of-stream represented by an empty batch, `None`, or an exception?
- Are records mutable? Can the source reuse or mutate them after returning?
- Is the method blocking, asynchronous, or streaming?
- How are retries, pagination tokens, timeouts, and cancellation handled?
- Does a batch preserve source order? Are duplicate records allowed?
- What metrics and logs are required, and who owns them?
- Does the interface guarantee idempotency, or must the pipeline handle duplicate delivery?

Keep the interface small and stable. Add a method only when the abstraction can define its semantics across implementations.

### ABC plus registry

A basic registry can map names to concrete implementations. Validate subclasses at registration time so configuration errors fail early:

```python
from abc import ABC, abstractmethod

class Source(ABC):
    @abstractmethod
    def read_batch(self, limit: int) -> list[dict[str, object]]:
        ...

SOURCE_TYPES: dict[str, type[Source]] = {}

def register_source(name: str, source_type: type[Source]) -> None:
    if not name or name in SOURCE_TYPES:
        raise ValueError("name must be non-empty and unique")
    if not issubclass(source_type, Source):
        raise TypeError("source_type must inherit from Source")
    SOURCE_TYPES[name] = source_type

class DemoSource(Source):
    def read_batch(self, limit: int) -> list[dict[str, object]]:
        return [{"demo": True}][:limit]

register_source("demo", DemoSource)
assert SOURCE_TYPES["demo"]().read_batch(10) == [{"demo": True}]
```

This registry is an in-process example, not a complete production plugin system. Real plugin loading may require configuration validation, import boundaries, package entry points, version compatibility, access controls, and careful handling of import-time side effects. Do not dynamically load untrusted Python plugins as if the ABC made them safe.

---

## 17. ABCs in production data engineering

ABCs are most useful at boundaries where multiple implementations must be interchangeable and the contract has meaningful behavior. Examples include:

- **Sources:** files, APIs, databases, object stores, message brokers.
- **Sinks:** warehouse tables, data lake files, search indexes, test sinks.
- **Serializers:** JSON Lines, Parquet adapters, Avro adapters, domain-specific encoders.
- **Configuration views:** read-only access to runtime settings via `Mapping`.
- **Validation strategies:** a common validation operation with specialized rules.
- **Metrics or notification adapters:** a consistent method contract across providers.

### Where ABCs may be the wrong tool

- A small pure function only needs one argument and one result: use a function or callable.
- A consumer needs only one method and implementations should not inherit from your code: consider a `Protocol` or duck typing.
- Two implementations share no stable semantics beyond similar names: do not force them into one ABC.
- The interface is changing rapidly and no reliable contract exists yet: wait until repeated needs clarify the boundary.
- You want to check a runtime capability but do not need inheritance or reusable behavior: use a focused runtime check.

### Design principle

**Depend on the smallest stable contract that describes what the caller needs.** ABCs are a means to express that contract, not a goal in themselves.

---

## 18. Testing ABC-based designs

Test the interface contract with a small fake implementation and test each real implementation against the same expectations. This is often called contract testing.

### 18.1 A simple contract test

```python
from abc import ABC, abstractmethod

class Writer(ABC):
    @abstractmethod
    def write(self, value: str) -> int:
        ...

class ListWriter(Writer):
    def __init__(self) -> None:
        self.values: list[str] = []

    def write(self, value: str) -> int:
        self.values.append(value)
        return len(value)

def assert_writer_contract(writer: Writer) -> None:
    assert writer.write("abc") == 3

writer = ListWriter()
assert_writer_contract(writer)
assert writer.values == ["abc"]
```

### 18.2 Pytest-style contract tests

Save the following as a test module if you are using pytest:

```python
import pytest

@pytest.mark.parametrize("value, expected", [("a", 1), ("abc", 3), ("", 0)])
def test_list_writer_returns_character_count(value, expected):
    writer = ListWriter()
    assert writer.write(value) == expected
    assert writer.values == [value]
```

The example assumes `Writer` and `ListWriter` are defined in the same test module or imported from your package. The test validates observable behavior, not just the existence of the method.

### 18.3 What to test for a collection ABC

For a custom `Mapping`, test at least:

- existing key access and missing-key `KeyError`;
- iteration yields keys and `len()` matches the number of keys;
- `in`, `get`, `keys`, `items`, `values`, and `dict(mapping)`;
- equality with another mapping;
- whether mutation is unavailable or explicitly supported;
- empty mapping behavior;
- nested mutable-value behavior if shallow immutability matters.

For `MutableMapping`, also test `__setitem__`, `__delitem__`, `update`, `pop`, `clear`, and validation failures.

### 18.4 Test the negative case

```python
import pytest
from abc import ABC, abstractmethod

class Incomplete(ABC):
    @abstractmethod
    def execute(self) -> None:
        ...

class MissingExecute(Incomplete):
    pass

def test_abstract_class_cannot_be_instantiated():
    with pytest.raises(TypeError):
        MissingExecute()
```

A test for an abstract class is not complete if it only checks that the base class has the expected name. Test the actual enforcement and the behavior of concrete implementations.

---

## 19. Common mistakes and how to avoid them

| Mistake | Why it is a problem | Better approach |
|---|---|---|
| Treating an ABC as a guarantee of correct behavior | ABCs check abstract method implementation status, not semantics | Document the contract and test it |
| Decorating every method abstract | Removes useful shared implementation and can overconstrain subclasses | Abstract only true variation points |
| Assuming virtual registration injects methods | It only changes subclass recognition | Use explicit inheritance if shared methods are needed |
| Assuming `isinstance(x, Iterable)` detects every iterable | Legacy `__getitem__` iteration can be missed | Test `iter(x)` when that is the actual requirement |
| Using `list` in every parameter annotation | Rejects or discourages other valid collection types | Accept `Sequence`, `Iterable`, or `Mapping` when sufficient |
| Choosing `MutableMapping` for a read-only consumer | Requires unnecessary mutation semantics | Use `Mapping` |
| Assuming `Mapping` means deeply immutable | Nested values may still be mutable | Copy/freeze nested data when required and document semantics |
| Using `Protocol` but expecting runtime enforcement | Protocol is primarily for static structural typing | Use a runtime check or ABC when justified; still test behavior |
| Treating `@runtime_checkable` as full type validation | Runtime protocol checks do not validate signatures and semantics fully | Use static checking and tests |
| Registering an unverified third-party class as a virtual subclass | `isinstance` may pass while methods are absent or incorrect | Verify the contract before registration |
| Building a complex `__subclasshook__` | Presence checks can misclassify unrelated classes | Keep it small, return `NotImplemented` when uncertain |
| Using ABCs for every class relationship | Increases coupling and ceremony | Prefer the smallest stable interface, function, or composition |
| Forgetting operational semantics in a data interface | Same signature can hide different retry, ordering, or durability behavior | Specify behavior beyond method names and types |

---

## 20. Guided exercises

Work through these in order. Type and run the code yourself rather than only reading it.

### Exercise 1 — Define a serializer contract

Create `Serializer(ABC)` with abstract `serialize(record: dict[str, object]) -> bytes`. Implement `JsonSerializer` using `json.dumps`. Test a simple record and confirm that an incomplete subclass cannot be instantiated.

### Exercise 2 — Add a template method

Extend the serializer ABC with a concrete `serialize_many(records)` method that calls `serialize` for each record and returns a list of byte strings. Decide what an empty list should return and test it.

### Exercise 3 — Abstract property

Create `Source(ABC)` with abstract property `name`. Implement `LocalFileSource` and `ApiSource`. Test that both concrete sources expose a non-empty name.

### Exercise 4 — Implement a `Mapping`

Build `EnvConfig(Mapping[str, str])` around a dictionary. Implement only `__getitem__`, `__iter__`, and `__len__`. Verify `get`, `keys`, `items`, `values`, membership, and equality with a normal dictionary.

### Exercise 5 — Add mutation carefully

Change the configuration object to `MutableMapping`. Add validation that rejects blank keys and non-string values. Test `update`, `pop`, `del`, and invalid values.

### Exercise 6 — Pick an annotation

Write a function that counts records. Decide whether it needs `list[dict]`, `Sequence[dict]`, `Iterable[dict]`, or `Iterator[dict]`. Explain the choice based on how the function consumes the input.

### Exercise 7 — Compare ABC and Protocol

Define a `Protocol` for a sink and implement a class that does not inherit from it. Run a static type checker if available. Explain how this differs from an ABC and what the type checker can verify.

### Exercise 8 — Virtual subclass

Register an existing class as a virtual subclass. Demonstrate `isinstance` and `issubclass`, then print its MRO. Explain why it does not inherit the ABC's concrete methods.

### Exercise 9 — A custom subclass hook

Implement a very small ABC that recognizes classes with a named method. Include a test for a class without the method. State the limits of the check and why method presence does not prove semantic correctness.

### Exercise 10 — Data-engineering interface review

Design a `BatchSource` contract for a pipeline. Specify batch size, end-of-input behavior, exception behavior, record ordering, and retry semantics. Implement an in-memory source and a fake source for tests. Keep external I/O out of the contract test.

---

## 21. Selected exercise solutions

### Solution to Exercise 1

```python
import json
from abc import ABC, abstractmethod

class Serializer(ABC):
    @abstractmethod
    def serialize(self, record: dict[str, object]) -> bytes:
        ...

class JsonSerializer(Serializer):
    def serialize(self, record: dict[str, object]) -> bytes:
        return json.dumps(record, separators=(",", ":")).encode("utf-8")

assert JsonSerializer().serialize({"id": 1}) == b'{"id":1}'
```

### Solution to Exercise 2

```python
from abc import ABC, abstractmethod

class Serializer(ABC):
    @abstractmethod
    def serialize(self, record: dict[str, object]) -> bytes:
        ...

    def serialize_many(self, records: list[dict[str, object]]) -> list[bytes]:
        return [self.serialize(record) for record in records]
```

This method delegates each record to the concrete serializer, preserving the format-specific behavior while sharing iteration logic.

### Solution to Exercise 4

The `FrozenConfig` example in Section 8 is a complete reference implementation. Extend it with tests for missing keys and empty data rather than copying the class into multiple places in a real project.

### Solution to Exercise 6

If the function only loops over records once, `Iterable[dict[str, object]]` is usually the widest useful contract. Use `Sequence` if it also requires indexing or length; use `Iterator` only when the function specifically requires a stateful next-item iterator. Use `list` only if list-specific behavior is needed.

---

## 22. Quick reference

### ABC skeleton

```python
from abc import ABC, abstractmethod

class MyContract(ABC):
    @abstractmethod
    def required_operation(self, value: str) -> str:
        ...

    def shared_operation(self, value: str) -> str:
        return self.required_operation(value).strip()
```

### Mapping skeleton

```python
from collections.abc import Mapping, Iterator

class MyMapping(Mapping[str, int]):
    def __getitem__(self, key: str) -> int:
        raise KeyError(key)  # replace with real lookup

    def __iter__(self) -> Iterator[str]:
        return iter(())       # replace with real key iteration

    def __len__(self) -> int:
        return 0               # replace with real size
```

### Useful introspection

```python
from abc import ABC, abstractmethod
from collections.abc import Mapping, Iterator

class MyContract(ABC):
    @abstractmethod
    def required_operation(self, value: str) -> str:
        ...

class MyMapping(Mapping[str, int]):
    def __getitem__(self, key: str) -> int:
        return {"answer": 42}[key]
    def __iter__(self) -> Iterator[str]:
        return iter(("answer",))
    def __len__(self) -> int:
        return 1

print(MyContract.__abstractmethods__)
print(MyMapping.__mro__)
print(issubclass(dict, Mapping))
print(isinstance({}, Mapping))
```

### Remember these distinctions

- **Abstract subclass:** inherits ABC behavior and is subject to abstract-method enforcement.
- **Virtual subclass:** registered for `isinstance`/`issubclass`; receives no methods and no MRO relationship.
- **Duck typing:** caller tries the operation it needs; behavior matters more than inheritance.
- **Protocol:** describes structural compatibility for static type checking; runtime checks are optional and limited.
- **Collection ABC:** a standard contract, often with useful mix-in methods.

---

## 23. Readiness checklist

You are ready to move on when you can confidently check every item:

- [ ] I can explain when an ABC is more useful than duck typing or a `Protocol`.
- [ ] I can create an ABC with one abstract method and show the incomplete-instantiation error.
- [ ] I can implement abstract properties and class/static methods with correct decorator order.
- [ ] I can use a concrete template method in an ABC without duplicating workflow code.
- [ ] I know the core primitives for `Mapping` and `MutableMapping`.
- [ ] I can explain why collection ABC mix-ins reduce duplicated code.
- [ ] I can choose `Iterable`, `Iterator`, `Sequence`, `Mapping`, or `Collection` based on actual needs.
- [ ] I can explain what virtual registration does and does not do.
- [ ] I understand that `__subclasshook__` and `@runtime_checkable` checks do not prove semantic correctness.
- [ ] I can design and test a small data-engineering interface with operational behavior documented.
- [ ] I can identify when an ABC would be unnecessary abstraction.

## 24. Suggested study workflow

1. **Read Sections 3–6:** implement your first ABC, then intentionally leave a subclass incomplete and observe the `TypeError` in a separate experiment.
2. **Type Section 8 by hand:** implement `FrozenConfig` from scratch without looking at the solution. Add tests for empty mappings and missing keys.
3. **Compare Section 11's approaches:** implement the same sink boundary once with an ABC and once with a `Protocol`; write down the trade-offs.
4. **Experiment with Section 12:** register a virtual subclass and inspect its MRO. Confirm that no ABC methods were injected.
5. **Complete Exercises 1, 4, 7, and 10:** these give the highest practical return for Python API design and data-engineering boundaries.
6. **Run tests and static checks:** use `pytest`, `ruff`, and `mypy` or `pyright` if installed. Fix contract mismatches instead of silencing checks without explanation.
7. **Explain the design aloud:** describe why the chosen contract is the smallest one the caller needs, and list what the interface does *not* guarantee.

**Final principle:** use ABCs when explicit runtime contracts and shared behavior help. Use `collections.abc` when you are implementing a genuine collection. Prefer `Protocol`, duck typing, functions, or composition when they express the dependency more simply.
