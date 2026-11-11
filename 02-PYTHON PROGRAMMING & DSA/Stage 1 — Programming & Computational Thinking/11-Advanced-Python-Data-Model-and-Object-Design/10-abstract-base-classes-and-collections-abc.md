# Abstract Base Classes and `collections.abc`

> **Module 11 — Advanced Python Data Model and Object Design**  
> **Lesson 10** · Python 3.12+  
> **Focus:** behavioral contracts, abstract members, collection ABCs, virtual subclassing, and the design boundary between ABCs, protocols, and duck typing.

## 1. Learning objectives

By the end of this lesson, you should be able to:

1. Explain when an abstract base class (ABC) is useful and what it enforces.
2. Use `abc.ABC`, `@abstractmethod`, abstract properties, and abstract class/static methods correctly.
3. Separate an abstract contract from concrete template-method behavior.
4. Choose a suitable `collections.abc` base for a custom collection.
5. Implement the primitive methods required by `Mapping` and use its supplied mix-in methods.
6. Distinguish nominal inheritance, virtual subclass registration, structural runtime checks, duck typing, and `typing.Protocol`.
7. Explain exactly what `ABC.register()` does—and what it does **not** do.
8. Test abstractness, concrete behavior, collection semantics, and runtime classification.
9. Choose the least complicated interface mechanism that meets a public API's needs.

## 2. Prerequisites and scope

You should already understand classes, inheritance, overriding, properties, type annotations, `isinstance`, `issubclass`, and basic MRO / `super()` behavior from Lessons 08–09.

This lesson builds on those mechanics but has a different emphasis:

- **Lesson 08:** how Python orders method lookup.
- **Lesson 09:** how to design mixins and avoid multiple-inheritance pitfalls.
- **Lesson 10 (this lesson):** how to express behavioral contracts, reuse collection implementations, and choose between ABCs, structural typing, and ordinary duck typing.

The roadmap's central distinction is that an ABC can provide both an interface contract and reusable implementation. Registering a virtual subclass gives classification, not inherited implementation.

## 3. Mental model: contract, implementation, and recognition

Think of an ABC as a contract with optional shared behavior.

```text
                 Abstract contract
              (required operations)
                       |
           +-----------+-----------+
           |                       |
   Nominal subclass          Virtual subclass
   inherits ABC              registered with ABC
   and its methods            for recognition only
           |                       |
   must implement             receives no methods
   abstract members           from the ABC
```

There are three different questions:

1. **Can this class be instantiated?**  
   `ABCMeta` tracks abstract members. A nominal subclass that has not implemented them cannot be instantiated.

2. **Can this object be recognized as belonging to an interface?**  
   `isinstance()` and `issubclass()` can recognize nominal subclasses, registered virtual subclasses, and—where an ABC defines an applicable structural hook—some classes that provide the expected shape.

3. **Does this object actually behave correctly?**  
   Neither inheritance nor registration proves semantic correctness. Tests and a precise contract are still required.

Do not collapse these questions into one.

## 4. First principles: `ABC` and `abstractmethod`

### 4.1 Define a small contract

```python
from abc import ABC, abstractmethod


class Exporter(ABC):
    @abstractmethod
    def serialise(self, data: dict[str, object]) -> bytes:
        """Convert application data to bytes."""
        raise NotImplementedError

    def export(self, data: dict[str, object], path: str) -> None:
        """Template method shared by every exporter."""
        payload = self.serialise(data)
        with open(path, "wb") as stream:
            stream.write(payload)


class JsonLikeExporter(Exporter):
    def serialise(self, data: dict[str, object]) -> bytes:
        import json
        return json.dumps(data, sort_keys=True).encode("utf-8")
```

`Exporter` cannot be instantiated because `serialise` is abstract. `JsonLikeExporter` implements it and is concrete. Its inherited `export()` method calls the subclass implementation through normal dynamic dispatch.

A minimal demonstration:

```python
try:
    Exporter()
except TypeError as exc:
    print(type(exc).__name__)

exporter = JsonLikeExporter()
print(exporter.serialise({"count": 2}))
```

Expected output:

```text
TypeError
b'{"count": 2}'
```

The abstractness check occurs when instantiating a class, not when Python first executes the class statement. Defining an incomplete subclass is normally allowed; attempting to instantiate it raises `TypeError`.

### 4.2 Abstract methods may contain code

An abstract method can have a useful implementation. Abstractness means “subclasses must provide an implementation,” not “this method must have an empty body.” A subclass can call an abstract method's implementation through `super()` when that is part of the contract.

```python
from abc import ABC, abstractmethod


class NormalisingExporter(ABC):
    @abstractmethod
    def serialise(self, data: dict[str, object]) -> bytes:
        """Subclasses provide the concrete format; shared audit hook."""
        print("serialisation requested")


class CompactExporter(NormalisingExporter):
    def serialise(self, data: dict[str, object]) -> bytes:
        super().serialise(data)  # invokes the base implementation in this chain
        if not isinstance(data, dict):
            raise TypeError("data must be a dictionary")
        return repr(data).encode("utf-8")


print(CompactExporter().serialise({"x": 1}))
```

Expected output:

```text
serialisation requested
b"{'x': 1}"
```

An abstract method may have a body, and that body can be called with `super()` when it is designed to participate in the chain. Avoid putting a terminal `raise NotImplementedError` in a base implementation that subclasses are expected to call through `super()`.

### 4.3 Abstract properties

Use `@property` outside `@abstractmethod`. A concrete subclass must provide a concrete property implementation.

```python
from abc import ABC, abstractmethod


class DataSource(ABC):
    @property
    @abstractmethod
    def source_name(self) -> str:
        """Stable identifier for this source."""
        raise NotImplementedError

    @abstractmethod
    def fetch(self, key: str) -> bytes:
        raise NotImplementedError


class MemorySource(DataSource):
    def __init__(self, records: dict[str, bytes]) -> None:
        self._records = dict(records)

    @property
    def source_name(self) -> str:
        return "memory"

    def fetch(self, key: str) -> bytes:
        return self._records[key]
```

The abstract property contract requires a readable `source_name`; it does not require the implementation to store the value in a particular way. A computed property is valid.

### 4.4 Abstract class methods and static methods

Decorator order matters. For abstract class methods, put `@classmethod` outermost and `@abstractmethod` directly inside it. The same outermost rule applies to `@staticmethod`.

```python
from abc import ABC, abstractmethod


class Parser(ABC):
    @classmethod
    @abstractmethod
    def from_text(cls, text: str) -> "Parser":
        """Construct an appropriate parser from text."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def supports_extension(extension: str) -> bool:
        raise NotImplementedError
```

A concrete subclass must implement both members. Prefer class methods when construction should respect the subclass (`cls`). Use static methods only when the operation is logically associated with the interface but does not need the class or instance.

## 5. ABCs as public behavioral contracts

A useful ABC specifies observable behavior, not merely a list of method names.

A contract should state:

- Required operations and their input/output types.
- Return-value semantics and exception behavior.
- Invariants and side effects.
- Whether calls are idempotent, mutable, lazy, or resource-owning.
- What subclasses may override and what the base implementation guarantees.

For example, a `fetch(key)` contract should clarify whether a missing key raises `KeyError`, returns `None`, or returns a sentinel. A method signature alone cannot settle that semantic choice.

ABCs can improve:
- **API clarity:** users see the intended extension points.
- **Early feedback:** incomplete nominal subclasses cannot be instantiated.
- **Reuse:** concrete template methods can centralize invariants.
- **Testing:** a minimal fake implementation can validate shared behavior.
- **Plugin architecture:** an application can define a stable extension contract.

They do not automatically verify every semantic promise, enforce type annotations at runtime, or guarantee that a subclass is substitutable.

## 6. `collections.abc`: standard collection contracts

`collections.abc` contains ABCs for common Python behaviors. Several are designed to provide useful methods when a subclass implements a small set of primitives.

### 6.1 Common ABCs and their roles

| ABC | Core expectation / primitive operations | Common use |
|---|---|---|
| `Iterable` | `__iter__()` | Values can be iterated |
| `Iterator` | `__next__()` and iterator behavior | Stateful stream of values |
| `Sized` | `__len__()` | Object has a size |
| `Container` | `__contains__()` | Membership test is supported |
| `Collection` | Combines iterable, sized, and container behavior | General collection |
| `Sequence` | Indexed access (`__getitem__`) and `__len__` | Ordered, integer-indexed collection |
| `MutableSequence` | Sequence primitives plus mutation operations | Mutable ordered collection |
| `Mapping` | `__getitem__`, `__iter__`, `__len__` | Read-only mapping interface |
| `MutableMapping` | Mapping primitives plus `__setitem__`, `__delitem__` | Mutable mapping |
| `Set` | Membership, iteration, and length primitives | Set-like value collection |
| `Callable` | `__call__` | Callable object |
| `Hashable` | `__hash__` with valid hash/equality semantics | Usable as a dict key or set element |

These are not all interchangeable. Choose the narrowest useful contract that matches the public behavior of your object. For example, if a function only iterates through records, accept `Iterable[Record]` rather than requiring a concrete `list[Record]`.

Some ABCs, such as `Iterable`, can recognize structural support via `__subclasshook__`; `isinstance(x, Iterable)` is not a universal proof that every object can be iterated successfully in every circumstance. The iteration itself and the object's semantics still matter.

### 6.2 A `Mapping` implementation that receives mix-in methods

The roadmap emphasizes three methods for a read-only `Mapping`:

- `__getitem__(key)`
- `__iter__()`
- `__len__()`

Implement these primitives and inherit `Mapping` to receive useful behavior such as `get`, `keys`, `items`, `values`, membership, and mapping equality.

```python
from collections.abc import Iterator, Mapping
from typing import TypeVar, Generic

K = TypeVar("K")
V = TypeVar("V")


class FrozenConfig(Mapping[K, V], Generic[K, V]):
    """A read-only mapping backed by a defensive copy."""

    def __init__(self, data: Mapping[K, V]) -> None:
        self._data = dict(data)

    def __getitem__(self, key: K) -> V:
        return self._data[key]

    def __iter__(self) -> Iterator[K]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)


config: FrozenConfig[str, int] = FrozenConfig({"a": 1})
print(config.get("b", 0), "a" in config, list(config.items()))
```

Expected output:

```text
0 True [('a', 1)]
```

The class inherits `Mapping`, so the mix-in implementations are present in its MRO. The defensive `dict(data)` copy prevents later mutations to the input mapping from changing this object's backing dictionary. However, this is only a shallow copy: if values themselves are mutable, callers may still mutate those values.

A useful design point: `Mapping` is an interface and reusable implementation, not a promise that the object is deeply immutable. If the contract requires deep immutability, define and enforce that separately.

### 6.3 Mutable mappings

`MutableMapping` builds on `Mapping` and expects mutation primitives, including `__setitem__` and `__delitem__`, in addition to the read-only mapping primitives. It supplies other standard mapping operations from those primitives.

Use `MutableMapping` when callers should be able to mutate the mapping through the standard interface. Do not inherit it merely to gain a convenient method if the object does not honor mutation semantics.

### 6.4 Sequence and mutable sequence

A custom `Sequence` generally implements `__getitem__` and `__len__`. The ABC can supply mix-in behavior such as iteration, containment, index lookup, and counting. A `MutableSequence` requires additional mutation primitives and supplies higher-level mutation behavior.

Be precise about semantics:
- Integer indexing should behave like a sequence.
- Out-of-range indexes should raise `IndexError`.
- Slices should return a deliberate and documented result type.
- Mutation methods should preserve invariants.
- Complexity should be documented if it differs materially from built-in sequences.

Do not choose an ABC only because its helper methods look convenient; its behavioral contract is part of what you promise.

## 7. Nominal inheritance versus virtual subclass registration

### 7.1 Ordinary inheritance

```python
from collections.abc import Mapping


class MyMapping(Mapping[str, int]):
    def __init__(self, data: dict[str, int]) -> None:
        self._data = dict(data)

    def __getitem__(self, key: str) -> int:
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)
```

`MyMapping` is a nominal subclass. It inherits `Mapping`'s methods through its MRO and must implement abstract members before instances can be created.

### 7.2 Virtual subclass registration

`ABC.register(SomeClass)` tells the ABC machinery to recognize `SomeClass` as a virtual subclass. It does **not** modify `SomeClass.__mro__`, inject methods into `SomeClass`, or guarantee that `SomeClass` satisfies the full semantic contract.

```python
from abc import ABC, abstractmethod


class SupportsExport(ABC):
    @abstractmethod
    def export_bytes(self) -> bytes:
        raise NotImplementedError


class LegacyReport:
    def export_bytes(self) -> bytes:
        return b"legacy-report"


SupportsExport.register(LegacyReport)

report = LegacyReport()
print(isinstance(report, SupportsExport))
print(issubclass(LegacyReport, SupportsExport))
print("export_bytes" in LegacyReport.__dict__)
print(SupportsExport in LegacyReport.__mro__)
```

Expected output:

```text
True
True
True
False
```

Why? `export_bytes` is defined on `LegacyReport`, so it is in that class's own dictionary. The ABC is not in its MRO. If `LegacyReport` did not define `export_bytes`, registration would still classify it as a virtual subclass, but calling the missing method would fail with `AttributeError`.

Registration is useful when you cannot or should not change a legacy class's inheritance. Use it carefully: recognition can be broader than behavioral conformance. Tests must verify the contract.

### 7.3 `isinstance`, `issubclass`, and recognition

- `isinstance(obj, SomeABC)` asks whether the object's class is recognized as a subclass of the ABC.
- `issubclass(Concrete, SomeABC)` asks the analogous question about classes.
- Nominal inheritance, virtual registration, and ABC-specific structural hooks may affect the answer.
- These checks do not validate return types, exception semantics, or all required behavior.

`ABC.register()` is a class-level classification mechanism. It does not provide implementations and does not force an unrelated class to implement abstract methods.

### 7.4 `__subclasshook__` and structural recognition

An ABC can customize subclass recognition through `__subclasshook__`. This is an advanced tool: an overly broad hook can classify classes that merely happen to have a matching attribute name. Check the full semantics you need, and return `NotImplemented` when the hook cannot decide.

For common structural typing needs, `typing.Protocol` is often clearer than inventing a custom hook.

## 8. ABC vs duck typing vs `typing.Protocol`

| Approach | Main idea | Runtime enforcement / recognition | Best fit |
|---|---|---|---|
| Duck typing | Call the operations you need and handle their documented failures | No upfront interface check required | Small internal APIs and Pythonic flexible code |
| ABC | Explicit nominal contract; may provide shared implementations | Abstract members prevent instantiation of incomplete nominal subclasses; runtime recognition also supports registration/hooks | Framework extension points and shared behavior |
| `Protocol` | Describe a structural type shape for static type checkers | Static checking by default; `@runtime_checkable` permits limited runtime checks | Decoupled APIs and third-party types that need not inherit |
| Concrete type (`list[T]`) | Require one implementation family | `isinstance` can test concrete type, but does not establish broader substitutability | APIs that genuinely depend on concrete-list behavior |

### 8.1 Protocol example

```python
from typing import Protocol


class ByteSource(Protocol):
    def read_bytes(self, key: str) -> bytes:
        ...


class FileBackedSource:
    def read_bytes(self, key: str) -> bytes:
        return key.encode("utf-8")


def consume(source: ByteSource, key: str) -> bytes:
    return source.read_bytes(key)


print(consume(FileBackedSource(), "alpha"))
```

Expected output:

```text
b'alpha'
```

`FileBackedSource` does not need to inherit `ByteSource`; a static type checker can accept it because its shape matches. `Protocol` itself does not automatically impose runtime abstract-method enforcement.

### 8.2 `@runtime_checkable` caveat

A runtime-checkable protocol permits certain `isinstance` checks based on member presence. It does not validate signatures, annotations, return types, or semantic behavior. Treat it as a shallow runtime convenience, not a runtime type checker.

### 8.3 A practical decision table

| Ask yourself | Prefer |
|---|---|
| Do I need shared concrete implementation and incomplete subclasses must not instantiate? | ABC |
| Do I need to describe an extension point for framework plugins? | Often ABC, potentially with a registry and entry points |
| Do I only need static structural typing across unrelated classes? | `Protocol` |
| Is there no need to declare/check an interface in advance? | Duck typing |
| Do I require behavior specific to a concrete implementation? | Concrete type may be appropriate, but state the constraint explicitly |
| Do I only need to accept iterable input? | `Iterable[T]`, not `list[T]` |
| Would a second metaclass or inheritance relationship complicate the design? | Consider `Protocol` or duck typing instead |

## 9. Template methods, plugins, and metaclass considerations

### 9.1 Template method pattern

An ABC can centralize an invariant in a concrete method while delegating one step to a subclass.

```python
from abc import ABC, abstractmethod


class ReportRenderer(ABC):
    def render(self, title: str, body: str) -> str:
        """Shared template: every report uses the same framing."""
        if not title.strip():
            raise ValueError("title must not be blank")
        return f"# {title.strip()}\n\n{self.render_body(body)}"

    @abstractmethod
    def render_body(self, body: str) -> str:
        raise NotImplementedError


class PlainTextRenderer(ReportRenderer):
    def render_body(self, body: str) -> str:
        return body.strip()


print(PlainTextRenderer().render(" Summary ", " Ready "))
```

Expected output:

```text
# Summary

Ready
```

The base class owns the framing and validation; subclasses provide the format-specific operation. Avoid putting unstable infrastructure or excessive policy into an ABC's concrete methods, because every implementation then inherits those decisions.

### 9.2 Plugin interface

A practical plugin architecture often combines:
1. An ABC describing the plugin contract.
2. A registry or discovery mechanism.
3. Tests that validate every registered implementation.
4. Optional package entry points for external plugins.

The ABC is only the contract layer. It does not discover, load, sandbox, or securely validate plugins by itself.

### 9.3 `ABCMeta` and metaclass conflicts

`abc.ABC` uses `ABCMeta`, which calculates abstract-method state such as `__abstractmethods__`. If a class hierarchy also needs a different metaclass, Python can report a metaclass conflict unless a compatible combined metaclass is designed. Do not introduce custom metaclasses casually; first ask whether an ABC, a `Protocol`, or composition can meet the requirement with less complexity.

## 10. The `numbers` ABC tower

The `numbers` module defines numeric ABCs such as `Number`, `Complex`, `Real`, `Rational`, and `Integral`. They describe numeric behavior categories and can help APIs state what numeric capabilities they accept.

Do not assume every third-party numeric class is automatically registered or that inheritance alone guarantees all mathematical laws. Numeric protocols have semantic expectations—such as equality, ordering where applicable, and arithmetic behavior—that require appropriate implementations and tests.

## 11. Incorrect designs and their corrections

### Mistake A: treating registration as implementation

Incorrect assumption:

```python
from abc import ABC, abstractmethod


class Serializer(ABC):
    @abstractmethod
    def dumps(self, value: object) -> bytes:
        raise NotImplementedError


class EmptySerializer:
    pass


Serializer.register(EmptySerializer)
serializer = EmptySerializer()
# serializer.dumps({})  # AttributeError: registration added no method
```

**Correction:** either inherit from `Serializer` and implement `dumps`, or register only when classification is justified and the class independently satisfies the contract. Registration must not be used to silence missing behavior.

### Mistake B: choosing a concrete type when the API needs an interface

Overly narrow:

```python
def first_record(records: list[str]) -> str:
    return records[0]
```

If the function only needs indexing, a sequence contract may be better:

```python
from collections.abc import Sequence


def first_record(records: Sequence[str]) -> str:
    if not records:
        raise ValueError("records must not be empty")
    return records[0]
```

Do not broaden the annotation blindly. If the implementation mutates the list, it needs a mutable contract; if it only iterates, `Iterable[str]` may be enough.

### Mistake C: ABC for every interface

An ABC can be unnecessary overhead when:
- There is only one implementation and no extension point.
- The caller only needs one operation and can use duck typing.
- Structural typing through `Protocol` is enough.
- Shared behavior would create a fragile base class.

Start with the simplest mechanism that communicates the contract. Add an ABC when it earns its cost.

### Mistake D: abstractness confused with runtime validation

Annotations such as `def load(self, key: str) -> bytes` do not enforce that callers pass a `str` or that implementations return `bytes`. An ABC enforces the presence of abstract implementations for nominal subclasses; it does not provide general runtime type validation. Use explicit validation when runtime guarantees are part of the API.

### Mistake E: using `isinstance(x, list)` for a broad collection contract

If an API accepts any read-only sequence, `isinstance(x, list)` rejects tuples and custom sequences unnecessarily. Annotate with `Sequence[T]` and, if a runtime guard is truly needed, check `collections.abc.Sequence`. Remember that a runtime check only classifies the object; test the behavior you depend on.

## 12. Testing ABCs and collection implementations

Tests should cover both interface mechanics and semantics.

```python
# test_abc_collections.py
from abc import ABC, abstractmethod
from collections.abc import Mapping
import pytest


class Reader(ABC):
    @abstractmethod
    def read(self, key: str) -> bytes:
        raise NotImplementedError


class IncompleteReader(Reader):
    pass


class DictReader(Reader):
    def __init__(self, values: dict[str, bytes]) -> None:
        self._values = dict(values)

    def read(self, key: str) -> bytes:
        return self._values[key]


class TinyMapping(Mapping[str, int]):
    def __init__(self, data: dict[str, int]) -> None:
        self._data = dict(data)

    def __getitem__(self, key: str) -> int:
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)


def test_incomplete_abstract_subclass_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        IncompleteReader()


def test_concrete_reader_implements_contract() -> None:
    reader = DictReader({"alpha": b"A"})
    assert reader.read("alpha") == b"A"
    with pytest.raises(KeyError):
        reader.read("missing")


def test_mapping_mixins_and_primitives() -> None:
    mapping = TinyMapping({"a": 1, "b": 2})
    assert mapping["a"] == 1
    assert len(mapping) == 2
    assert list(mapping) == ["a", "b"]
    assert mapping.get("missing", 0) == 0
    assert "b" in mapping
    assert list(mapping.items()) == [("a", 1), ("b", 2)]


def test_mapping_is_recognised_by_abc() -> None:
    assert isinstance(TinyMapping({"x": 1}), Mapping)
```

Run with:

```bash
python -m pytest -q test_abc_collections.py
```

Expected test summary:

```text
4 passed
```

The test suite checks more than inheritance: it verifies abstract instantiation restrictions, missing-key behavior, the three `Mapping` primitives, and inherited mix-in methods.

Add tests for iteration order, empty collections, unusual keys, mutation isolation, equality, and complexity-sensitive behavior when those properties are part of your public contract.

## 13. Graduated exercises with worked solutions

### Exercise 1 — Basic ABC

Create an abstract `HealthCheck` with `check() -> bool`. Make `DatabaseHealthCheck` concrete. Prove that the abstract base cannot be instantiated.

**Solution:**

```python
from abc import ABC, abstractmethod


class HealthCheck(ABC):
    @abstractmethod
    def check(self) -> bool:
        raise NotImplementedError


class DatabaseHealthCheck(HealthCheck):
    def check(self) -> bool:
        return True


assert DatabaseHealthCheck().check() is True
try:
    HealthCheck()
except TypeError:
    print("abstract")
```

Expected output: `abstract`

### Exercise 2 — Abstract property

Create an abstract `Plugin` with a `name` property and `run(payload: bytes) -> bytes`. Implement a concrete plugin whose name is computed rather than stored.

**Solution:**

```python
from abc import ABC, abstractmethod


class Plugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def run(self, payload: bytes) -> bytes:
        raise NotImplementedError


class PrefixPlugin(Plugin):
    @property
    def name(self) -> str:
        return type(self).__name__.lower()

    def run(self, payload: bytes) -> bytes:
        return b"prefix:" + payload


plugin = PrefixPlugin()
print(plugin.name, plugin.run(b"x"))
```

Expected output:

```text
prefixplugin b'prefix:x'
```

### Exercise 3 — Choose a collection ABC

You need a custom read-only configuration object supporting key lookup, iteration over keys, length, and standard helpers like `get()` and `items()`. Which ABC should you use, and which three methods must be implemented?

**Solution:** inherit from `collections.abc.Mapping`; implement `__getitem__`, `__iter__`, and `__len__`. Add the tests that prove the mapping semantics, rather than relying only on `isinstance`.

### Exercise 4 — Virtual registration

Register a legacy class with an ABC. Demonstrate that `issubclass()` returns true but the ABC is not in the legacy class's MRO and its methods are not injected.

**Solution:**

```python
from abc import ABC


class SupportsClose(ABC):
    def close(self) -> None:
        raise NotImplementedError


class LegacyConnection:
    def close(self) -> None:
        print("closed")


SupportsClose.register(LegacyConnection)

assert issubclass(LegacyConnection, SupportsClose)
assert SupportsClose not in LegacyConnection.__mro__
LegacyConnection().close()
```

Expected output: `closed`

### Exercise 5 — Design decision

A function only calls `obj.read_bytes(key)`. Should you require an ABC, a `Protocol`, or neither?

**Worked answer:** use duck typing for a tiny internal function if the operation is self-evident and failures are naturally handled. Use `Protocol` when static type checking should describe the structural requirement without forcing inheritance. Use an ABC if the application owns an extension contract, needs abstract instantiation enforcement for nominal subclasses, or provides shared template behavior.

## 14. Roadmap self-check — answers

### 1. Which three methods make a `Mapping` complete, and which methods do you get free?

Implement `__getitem__`, `__iter__`, and `__len__`. `Mapping` supplies useful operations including `get`, `keys`, `items`, `values`, containment, and equality. Confirm the exact behavior you depend on with tests.

### 2. What is the difference between `register()` and subclassing?

Subclassing makes the ABC part of the class's inheritance/MRO, inherits its implementations, and subjects the nominal subclass to abstract-member enforcement. `ABC.register(cls)` marks an unrelated class as a virtual subclass for ABC recognition; it does not change the MRO, inject methods, or enforce abstract members on that class.

### 3. When is a `Protocol` the better choice than an ABC?

When an API needs to describe a structural shape for static type checking without requiring implementations to inherit from a shared base class. This is especially useful for third-party classes, adapters, and decoupled libraries. If runtime abstractness enforcement and shared concrete implementation are needed, an ABC may be a better fit.

## 15. Common mistakes checklist

- [ ] Making every interface an ABC when a `Protocol` or no explicit interface would do.
- [ ] Forgetting that abstract methods are checked at instantiation, not at class definition.
- [ ] Using `isinstance(value, list)` when the contract really accepts `Sequence` or another ABC.
- [ ] Assuming `register()` injects implementations or proves semantic correctness.
- [ ] Confusing runtime classification with signature or return-type validation.
- [ ] Choosing `MutableMapping` or `MutableSequence` without honoring their mutation contracts.
- [ ] Returning a narrow concrete type annotation when callers only need a broader ABC.
- [ ] Ignoring decorator order for abstract class and static methods.
- [ ] Treating a read-only `Mapping` as deeply immutable without checking its values.
- [ ] Adding an ABC/template method whose shared behavior makes subclasses more fragile.
- [ ] Forgetting metaclass compatibility when introducing `ABCMeta` into a complex hierarchy.
- [ ] Testing only `isinstance()` instead of testing required behavior and failure cases.

## 16. Final engineering checklist

Before publishing an ABC or custom collection:

- [ ] Is there a real public contract or extension point?
- [ ] Would duck typing or `Protocol` be simpler?
- [ ] Are abstract methods, properties, class methods, and static methods declared correctly?
- [ ] Are concrete template methods limited, documented, and invariant-preserving?
- [ ] Does a custom collection implement the correct primitive methods for its chosen ABC?
- [ ] Do inherited mix-in methods behave correctly for empty, normal, and edge-case inputs?
- [ ] Are `isinstance` / `issubclass` checks being used only for classification, not as a substitute for semantic tests?
- [ ] If virtual registration is used, does the registered class independently satisfy the contract?
- [ ] Are public annotations as broad as the actual requirements, but no broader than semantics permit?
- [ ] Are tests checking both successful behavior and required exceptions?
- [ ] Are runtime validation and static type checking responsibilities explicit?
- [ ] Have ABC/metaclass trade-offs and plugin lifecycle concerns been considered?

## 17. Key takeaways

1. An ABC can enforce abstract-member implementation for nominal subclasses and can also provide concrete shared behavior.
2. `collections.abc` offers established contracts and mix-in methods; implement the required primitives and test their semantics.
3. Virtual subclass registration affects recognition, not inheritance or method availability.
4. `isinstance` and `issubclass` do not prove semantic correctness.
5. Choose among ABC, `Protocol`, duck typing, and concrete types according to the contract you actually need.
