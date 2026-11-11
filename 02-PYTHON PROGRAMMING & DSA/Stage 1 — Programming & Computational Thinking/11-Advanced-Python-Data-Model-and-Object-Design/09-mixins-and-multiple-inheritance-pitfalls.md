# Mixins and Multiple-Inheritance Pitfalls

> **Stage 1 · Module 11 — Advanced Python Data Model and Object Design**  
> **Target:** Python 3.12+  
> **Focus:** Practical mixin design, cooperative behavior, and failure prevention—not a replacement for the preceding lesson on C3/MRO mechanics.

## 1. Learning objectives

By the end of this lesson, you should be able to:

- Explain what a mixin contributes and when it is a better fit than a normal base class.
- Distinguish stateless mixins from mixins that rely on documented host attributes or state.
- Design mixins with narrow responsibilities, predictable names, and explicit contracts.
- Use cooperative `super()` calls in methods and constructors without duplicating shared-base work.
- Predict how base order affects method lookup and why mixins are usually listed before the concrete base.
- Diagnose method/attribute collisions, incompatible signatures, missing `super()` calls, fragile base classes, and initialization-order dependencies.
- Recognize diamond inheritance, metaclass conflicts, and instance-layout conflicts.
- Choose composition, delegation, a plain function, or a protocol when inheritance adds more coupling than value.
- Test the combined class, not just isolated mixin behavior, and reason about MRO-related special cases.

## 2. Prerequisites and scope

You should already understand classes, inheritance, instance attributes, `super()`, and the basics of `Class.__mro__`/C3 linearization from Lesson 08. This lesson uses those mechanics to make design decisions. It does not repeat a full C3 derivation; instead, it asks whether a proposed mixin hierarchy is understandable, cooperative, and safe to maintain.

**Key distinction:** MRO is Python's method-lookup order. A mixin is a design technique that uses multiple inheritance to add a focused capability. A valid MRO does not automatically make the design good.

## 3. Mental model: a capability that can be mixed in

A mixin is a small class intended primarily to be combined with another class. It contributes a capability—such as formatting, logging, timestamp access, or a reusable method implementation—rather than representing a complete domain entity by itself.

```text
                 ┌────────────────┐
                 │    User model  │  domain state: name, email
                 └────────┬───────┘
                          │ combined with
             ┌────────────┴────────────┐
             │                         │
      ┌──────▼──────┐          ┌───────▼──────┐
      │ ReprMixin   │          │ JsonMixin    │
      │ __repr__    │          │ to_json()    │
      └─────────────┘          └──────────────┘
```

The diagram shows capabilities, not a runtime call sequence. Actual lookup follows the combined class's MRO. A mixin should have a small, documented surface and should avoid making unrelated assumptions about the host class.

### Ordinary base class versus mixin

| Design question | Ordinary/domain base class | Mixin |
|---|---|---|
| Primary purpose | Model an “is-a” relationship or shared domain contract | Add one reusable capability to otherwise different classes |
| Instantiated alone? | Often yes | Usually not; it is primarily composed into a concrete class |
| State | May own substantial state and lifecycle | Prefer none or minimal, explicit state |
| Constructor | May define its own required initialization | Usually avoids `__init__`; if it participates, it must cooperate |
| Contract | Domain semantics and invariants | Narrow capability requirements and method-chain rules |

The suffix `Mixin` is a convention, not a language feature. `JsonMixin`, `TimestampMixin`, and `AuditMixin` signal intent to readers.

## 4. A first working example

This example uses stateless mixins. They provide methods but do not initialize state of their own.

```python
from __future__ import annotations

import json
from typing import Any


class JsonMixin:
    def to_json(self) -> str:
        """Serialize the host object's instance attributes."""
        return json.dumps(vars(self), default=str, sort_keys=True)


class ReprMixin:
    def __repr__(self) -> str:
        fields = ", ".join(
            f"{name}={value!r}" for name, value in vars(self).items()
        )
        return f"{type(self).__name__}({fields})"


class User(ReprMixin, JsonMixin):
    def __init__(self, name: str, active: bool = True) -> None:
        self.name = name
        self.active = active


user = User("Ada")
print(repr(user))
print(user.to_json())
print(User.__mro__)
```

Expected output (the JSON keys are sorted):

```text
User(name='Ada', active=True)
{"active": true, "name": "Ada"}
(<class '__main__.User'>, <class '__main__.ReprMixin'>, <class '__main__.JsonMixin'>, <class 'object'>)
```

**Contract and limits:** these mixins assume the host has a normal instance dictionary. `vars(self)` raises `TypeError` for some objects without `__dict__`, such as a class using only slots. JSON serialization of arbitrary instance attributes is not automatically a stable public data format: values may be non-serializable, sensitive, or unsuitable for API output. In production, prefer explicit serialization fields and test the supported data model.

## 5. Design boundaries for a good mixin

A mixin should answer a simple question: “What one capability does this add, and what does it require from the host?”

### Good design rules

1. **One responsibility.** `TimestampMixin` should not also open database connections or validate unrelated business rules.
2. **Small public surface.** Prefer a few focused methods over a second framework hidden in the class hierarchy.
3. **Document host requirements.** If `to_label()` reads `self.display_name`, say so and validate that assumption where possible.
4. **Prefer statelessness.** Stateless mixins are easier to combine and less sensitive to initialization order.
5. **Avoid `__init__` when possible.** If state is essential, either use a carefully designed cooperative constructor contract or use composition.
6. **Use distinctive names.** Generic attributes such as `status`, `name`, and `data` are collision risks.
7. **Cooperate consistently.** If a method is intended to continue a chain, call `super()` exactly as the contract requires.
8. **Do not swallow behavior silently.** Document whether a method wraps, extends, or intentionally replaces the next implementation.
9. **Keep ordering understandable.** List mixins before the concrete base so their methods can participate before the base implementation.
10. **Test the final composition.** The combined class's MRO and interactions are part of the behavior.

### Stateless versus state-requiring mixins

**Stateless:** computes a value from arguments or documented host attributes; no own initialization is needed. Examples include a formatting helper or a method that adds a derived display label.

**Host-dependent:** reads attributes the host promises to provide. This can be reasonable if the contract is explicit and typed. Python does not enforce that contract merely because a mixin is in the MRO.

**Stateful:** stores data or needs initialization. This is not forbidden, but it increases coupling. If it defines `__init__`, it should normally accept `**kwargs`, consume only its own named arguments, and call `super().__init__(**kwargs)`. The terminal base must accept the remaining arguments, and every class in the chain must follow the same convention.

## 6. Cooperative methods: extend the chain instead of bypassing it

A cooperative mixin uses `super()` to delegate to the next implementation in the MRO. “Next” is determined by the runtime class's MRO, not by the textual parent named in the mixin declaration.

```text
class Request(AuditMixin, RetryMixin, BaseRequest):

MRO: Request → AuditMixin → RetryMixin → BaseRequest → object

call handle()
   │
   ▼
AuditMixin.handle() ──super()──▶ RetryMixin.handle()
                                     │
                                  super()
                                     ▼
                              BaseRequest.handle()
```

Every method in a cooperative chain must agree on the contract: whether it expects a next implementation, what arguments it forwards, and what return value it preserves or transforms.

### Correct wrapping behavior

```python
class BasePipeline:
    def run(self, value: str) -> str:
        return value


class PrefixMixin:
    def run(self, value: str) -> str:
        return super().run(f"prefix:{value}")


class SuffixMixin:
    def run(self, value: str) -> str:
        return f"{super().run(value)}:suffix"


class Pipeline(PrefixMixin, SuffixMixin, BasePipeline):
    pass

print(Pipeline().run("job"))
print([cls.__name__ for cls in Pipeline.__mro__])
```

Expected output:

```text
prefix:job:suffix
['Pipeline', 'PrefixMixin', 'SuffixMixin', 'BasePipeline', 'object']
```

`PrefixMixin` delegates a transformed argument; `SuffixMixin` transforms the result from the next method. Both cooperate. The exact transformation order is determined by the MRO.

### The non-cooperative version is fragile

```python
class BadPrefixMixin:
    def run(self, value: str) -> str:
        # Bypasses any run() implementation between this class and BasePipeline.
        return BasePipeline.run(self, f"prefix:{value}")
```

This direct call may appear to work in a simple hierarchy, but it hard-codes a particular base and skips other mixins. In a diamond, explicitly calling `Parent.__init__(self)` can also initialize a shared ancestor more than once. Use `super()` for cooperative chains; call a named base explicitly only when intentionally bypassing dynamic dispatch and when the design documents that choice.

## 7. A complete cooperative mixin example

This example demonstrates multiple mixins contributing one ordered processing pipeline. All methods share a stable `process(record, *, trace)` contract. Each layer records its participation and calls `super()` once. The terminal base returns the processed value.

```python
from __future__ import annotations

from typing import Protocol, cast


class RecordProcessor(Protocol):
    def process(self, record: str, *, trace: list[str]) -> str: ...


class NormalizeMixin:
    def process(self, record: str, *, trace: list[str]) -> str:
        trace.append("normalize")
        normalized = record.strip().lower()
        return cast(RecordProcessor, super()).process(normalized, trace=trace)


class AuditMixin:
    def process(self, record: str, *, trace: list[str]) -> str:
        trace.append("audit")
        return cast(RecordProcessor, super()).process(record, trace=trace)


class EnrichMixin:
    def process(self, record: str, *, trace: list[str]) -> str:
        trace.append("enrich")
        enriched = f"{record}|source=etl"
        return cast(RecordProcessor, super()).process(enriched, trace=trace)


class TerminalProcessor:
    def process(self, record: str, *, trace: list[str]) -> str:
        trace.append("terminal")
        return record


class CustomerRecordProcessor(NormalizeMixin, AuditMixin, EnrichMixin, TerminalProcessor):
    pass


trace: list[str] = []
result = CustomerRecordProcessor().process("  CUSTOMER-42  ", trace=trace)
print(result)
print(trace)
print([cls.__name__ for cls in CustomerRecordProcessor.__mro__])
```

Expected output:

```text
customer-42|source=etl
['normalize', 'audit', 'enrich', 'terminal']
['CustomerRecordProcessor', 'NormalizeMixin', 'AuditMixin', 'EnrichMixin', 'TerminalProcessor', 'object']
```

**Why it works:** the combined class determines one linear order. Each method has the same parameters and forwards `trace` consistently. Each layer delegates once; the terminal implementation ends the chain. No mixin directly names another mixin or assumes which class follows it.

`Protocol` documents the expected public method shape for static typing; it does not implement or enforce the cooperative chain. `cast(RecordProcessor, super())` tells the type checker to treat the next-MRO proxy as providing that protocol. `cast` performs no runtime validation and does not change dispatch: the method call still resolves dynamically through the concrete class MRO. This is an explicit typing trade-off, so the combined class must be tested and every participating implementation must honor the protocol.

## 8. Constructor chaining and initialization contracts

Constructor cooperation is harder than method cooperation because each layer may need its own argument and state. A robust pattern is:

- each mixin consumes only the keyword argument it owns;
- each mixin forwards the rest with `super().__init__(**kwargs)`;
- all mixins accept `**kwargs` and use compatible signatures;
- the terminal base accepts only the remaining documented arguments and rejects unexpected ones rather than silently ignoring typos.

```python
class Root:
    def __init__(self, **kwargs: object) -> None:
        if kwargs:
            unexpected = ", ".join(sorted(kwargs))
            raise TypeError(f"unexpected constructor arguments: {unexpected}")
        super().__init__()


class TenantMixin:
    def __init__(self, *, tenant_id: str, **kwargs: object) -> None:
        self.tenant_id = tenant_id
        super().__init__(**kwargs)


class RetryMixin:
    def __init__(self, *, retries: int = 3, **kwargs: object) -> None:
        if retries < 0:
            raise ValueError("retries must be non-negative")
        self.retries = retries
        super().__init__(**kwargs)


class Job(TenantMixin, RetryMixin, Root):
    pass


job = Job(tenant_id="tenant-7", retries=2)
print(job.tenant_id, job.retries)
print([cls.__name__ for cls in Job.__mro__])
```

Expected output:

```text
tenant-7 2
['Job', 'TenantMixin', 'RetryMixin', 'Root', 'object']
```

`TenantMixin` removes `tenant_id` from the argument stream by binding it explicitly; `RetryMixin` does the same for `retries`; `Root` verifies that no unknown keywords remain. This catches misspellings such as `retry=2` instead of quietly ignoring them.

### Failure: incompatible signatures

```python
class NeedsModeMixin:
    def __init__(self, *, mode: str, **kwargs: object) -> None:
        self.mode = mode
        super().__init__(**kwargs)


class StrictBase:
    def __init__(self, *, required: str) -> None:
        self.required = required


class Broken(NeedsModeMixin, StrictBase):
    pass


try:
    Broken(mode="fast")  # `required` is never supplied.
except TypeError as error:
    print(type(error).__name__, error)
```

Expected output:

```text
TypeError StrictBase.__init__() missing 1 required keyword-only argument: 'required'
```

The chain is brittle because each layer's argument contract must be satisfied together. The right repair is not always to add `**kwargs` everywhere blindly: define a clear constructor contract, consume owned arguments, forward the remainder, and validate at the terminal boundary. For simple data classes, composition or a single explicit constructor may be clearer than a cooperative `__init__` chain.

### Initialization-order traps

Avoid calling overridable methods from a base constructor before all state required by those methods is initialized. In a cooperative hierarchy, `self.some_method()` may resolve to a mixin override that expects attributes not yet assigned. Prefer explicit, non-overridable initialization helpers or establish and document a strict initialization order. Constructor order follows the MRO, not a separate “parent-first” rule.

## 9. Base ordering, collisions, and accidental overrides

### Put behavior mixins before the concrete base

```python
class ExportMixin:
    def export(self) -> str:
        return "mixin export"


class BaseModel:
    def export(self) -> str:
        return "base export"


class GoodModel(ExportMixin, BaseModel):
    pass


class SurprisingModel(BaseModel, ExportMixin):
    pass

print(GoodModel().export())
print(SurprisingModel().export())
```

Expected output:

```text
mixin export
base export
```

For `SurprisingModel`, the base class's method is found first, so the mixin implementation is never reached through ordinary lookup. This is why `class A(Mixin, Base)` is the common ordering when the mixin should contribute or override behavior.

### Method-name collision

If two mixins define `save()`, the leftmost applicable implementation wins unless it delegates cooperatively. Python will not warn that the two methods may have incompatible meanings. Use distinct names, an explicit composition layer, or a documented cooperative wrapper chain.

### Attribute collision

Two mixins may both read or assign `self.status`, but mean different things by it. This hidden coupling can cause subtle defects even when method lookup is valid. Prefer specific names such as `retry_status` and `audit_status`, or store helper state in a clearly owned object. Do not rely on base order to resolve ambiguous state semantics.

### Silent behavior replacement

A mixin that defines `close()`, `save()`, `validate()`, or `__repr__()` can replace a method on the concrete base. Ask whether it should wrap the next method, deliberately replace it, or expose a differently named capability. Document that choice and test the composed class.

## 10. Diamond inheritance and duplicate work

A diamond occurs when two branches share a common ancestor:

```text
        Root
       /    \
      Left  Right
       \    /
        Final
```

A non-cooperative implementation may call `Root` twice. Python's MRO does not automatically make manually named base calls cooperative; `super()` is what lets each class pass control to the next class in the linearization.

```python
class Root:
    def __init__(self) -> None:
        print("Root")
        super().__init__()


class Left(Root):
    def __init__(self) -> None:
        print("Left")
        super().__init__()


class Right(Root):
    def __init__(self) -> None:
        print("Right")
        super().__init__()


class Final(Left, Right):
    def __init__(self) -> None:
        print("Final")
        super().__init__()


Final()
print([cls.__name__ for cls in Final.__mro__])
```

Expected output:

```text
Final
Left
Right
Root
['Final', 'Left', 'Right', 'Root', 'object']
```

Every constructor appears once. `Left`'s `super()` continues to `Right`, because `Right` is next after `Left` in `Final`'s MRO; it does not jump straight to `Root`.

### Failure: named parent calls duplicate the root

```python
class BadLeft(Root):
    def __init__(self) -> None:
        print("BadLeft")
        Root.__init__(self)


class BadRight(Root):
    def __init__(self) -> None:
        print("BadRight")
        Root.__init__(self)


class BadFinal(BadLeft, BadRight):
    def __init__(self) -> None:
        print("BadFinal")
        BadLeft.__init__(self)
        BadRight.__init__(self)
```

Calling `BadFinal()` prints `BadFinal`, `BadLeft`, `Root`, `BadRight`, `Root`: the shared root is initialized twice. In real code this can duplicate resource acquisition, register callbacks twice, overwrite state, or repeat side effects.

## 11. Other multiple-inheritance failure modes

### 11.1 Inconsistent hierarchy

Python rejects an inheritance graph when it cannot produce a consistent MRO. Do not try to “fix” such a graph by relying on an arbitrary lookup order. Reconsider the declared relationships or use composition. Lesson 08 explains C3 constraints; for this lesson, the design rule is to keep the graph small and semantically consistent.

### 11.2 Metaclass conflict

A class's metaclass must be compatible with the metaclasses of its bases. Combining unrelated frameworks or extension types can produce a `TypeError` about metaclass conflict. This is not the same problem as two methods having the same name. Prefer a common supported metaclass only when you understand both frameworks' requirements; otherwise use adapters or composition.

### 11.3 Instance layout conflict

Some bases contribute incompatible instance layouts, particularly when multiple bases define non-empty `__slots__` or involve certain C-implemented built-in types. Python can raise `TypeError: multiple bases have instance lay-out conflict`. Do not assume adding mixins is layout-neutral. A stateless mixin with `__slots__ = ()` can avoid introducing its own instance dictionary, but it does not magically resolve every layout conflict.

```python
class LoggingMixin:
    __slots__ = ()

    def log(self, message: str) -> None:
        print(message)
```

### 11.4 Fragile base class

A base class becomes fragile when a subclass or mixin depends on undocumented internal methods, attribute names, or call order. For example, calling `self._prepare()` in `Base.__init__` allows a mixin override to run before the host is fully initialized. Reduce this risk by narrowing extension points, documenting contracts, avoiding overridable calls during construction, and testing representative combinations.

### 11.5 Missing `super()` breaks the chain

If one class in the cooperative chain forgets `super()`, all later classes in the MRO are skipped for that method call. The MRO remains valid, but the behavior chain is incomplete. Test the full trace, not merely the final return value.

## 12. Host attributes, dataclasses, and `__slots__`

A mixin that requires `self.created_at` should state that requirement. A type-checking `Protocol` can document the expected interface, while a runtime check can validate it when needed. Neither mechanism makes an undocumented assumption safe by itself.

For stateless mixins combined with slotted classes, declaring `__slots__ = ()` avoids the mixin itself adding an instance dictionary. It does not grant the mixin permission to assign new attributes to the host. A mixin that writes `self.audit_events = []` needs that storage declared by the concrete host (or another suitable base), or it will fail for a slotted host without such a slot.

Dataclasses can use mixins for behavior, but do not assume a mixin's constructor will be called automatically by a generated dataclass `__init__`. Dataclass-generated constructors initialize dataclass fields according to dataclass rules; a non-dataclass base initializer is not automatically chained just because it appears in the MRO. If base initialization is required, implement and test an explicit initialization strategy. Avoid combining several stateful constructor mixins with a generated dataclass constructor unless the lifecycle is carefully designed.

A stateless mixin can work well with a slotted dataclass when it adds behavior without requiring undeclared storage:

```python
from dataclasses import dataclass


class UppercaseLabelMixin:
    __slots__ = ()

    def label(self) -> str:
        return self.name.upper()


@dataclass(slots=True)
class Product(UppercaseLabelMixin):
    name: str


print(Product("widget").label())
print([cls.__name__ for cls in Product.__mro__])
```

Expected output:

```text
WIDGET
['Product', 'UppercaseLabelMixin', 'object']
```

Here `name` is declared by the dataclass, while the mixin contributes only a method. The empty slots declaration prevents the mixin from introducing an instance dictionary; it does not create a `name` slot itself.


## 12.1 `__init_subclass__` and registration/validation mixins

A mixin can use `__init_subclass__` to validate or register subclasses at class-creation time. This hook itself participates in cooperative class initialization: a mixin should normally call `super().__init_subclass__(**kwargs)` so other bases can process the class too.

```python
class SlugMixin:
    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if not getattr(cls, "slug_prefix", ""):
            raise TypeError(f"{cls.__name__} must define a non-empty slug_prefix")


class Article(SlugMixin):
    slug_prefix = "article"


print(Article.slug_prefix)
```

Expected output:

```text
article
```

Do not use this hook casually as hidden global registration machinery. Make the contract discoverable, avoid mutating unrelated classes, and test class creation failures. If multiple mixins define `__init_subclass__`, each must cooperate with `super()` and accept/forward compatible keyword arguments.

## 12.2 Default methods from an interface: `collections.abc.Mapping`

`collections.abc.Mapping` illustrates a related but distinct pattern: implement a small required interface and inherit useful derived operations. It is an abstract base class/interface with mixin-like provided behavior, not merely a generic “add any feature” mixin. For example, a mapping implementation supplies `__getitem__`, `__iter__`, and `__len__`; the ABC provides other mapping operations. Read the ABC contract and test inherited behavior instead of assuming every method is supplied automatically.

```python
from collections.abc import Iterator, Mapping


class Settings(Mapping[str, str]):
    def __init__(self, values: dict[str, str]) -> None:
        self._values = dict(values)

    def __getitem__(self, key: str) -> str:
        return self._values[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)


settings = Settings({"region": "ap-south-1", "mode": "batch"})
print(settings["region"])
print(settings.get("mode"))  # supplied by Mapping's inherited behavior
print(len(settings))
```

Expected output:

```text
ap-south-1
batch
2
```

This works because the implementation satisfies the ABC's required mapping operations. Do not confuse this defined interface and its documented derived methods with arbitrary mixins that happen to provide methods.

## 13. Attribute lookup versus special-method lookup

For ordinary attributes such as `obj.label`, Python searches the instance and its class hierarchy according to the attribute access rules. Many special methods used by syntax and built-in operations—such as `len(obj)`, iteration, arithmetic, and context-manager operations—are generally looked up on the type, not by ordinary instance-attribute lookup. Assigning `obj.__len__ = ...` is not a reliable way to change `len(obj)`.

When a mixin adds a special method, test the actual operation (`len(x)`, `iter(x)`, `x + y`, `with x`, etc.), not only `getattr(x, "__len__")`. This complements the preceding data-model lessons; it is not a reason to create a mixin for every special method.

### Awareness: `singledispatchmethod` and `super()`

`functools.singledispatchmethod` dispatches based on the type of the first non-`self`/`cls` argument. When combining it with inheritance, decorators, and `super()`, test the actual dispatch path and decorator order. Do not assume a dispatched implementation or a `super()` call behaves like an ordinary un-decorated method without checking the documented API. This is an awareness topic here, not a full tutorial on generic dispatch.

## 14. Production-oriented use cases

Mixins are useful when a focused capability needs to be reused across otherwise different classes and inheritance is an intentional extension mechanism. Examples include:

- **Web frameworks:** request/response behavior and generic view capabilities are often assembled from mixins. Read the concrete class's MRO and each mixin's contract rather than inferring behavior from names alone.
- **`socketserver.ThreadingMixIn`:** the standard library provides a mixin that changes server request-handling behavior. Its documented ordering and lifecycle expectations matter; consult the Python version's standard-library documentation before overriding related methods.
- **`unittest` test cases:** reusable assertion or setup helpers can be factored into a focused mixin, provided names and setup contracts are explicit.
- **Serialization/representation:** a small helper can be useful when the serialized schema is stable and intentionally defined. Avoid dumping every attribute for public APIs.
- **Audit or metrics wrappers:** a cooperative method can record an event before/after delegating, but exceptions, return values, and exactly-once semantics must be tested.

Do not add a mixin solely to avoid writing one short helper function. The hierarchy itself becomes a dependency that future maintainers must understand.

### Real-world MRO reading exercise

Inspect a concrete standard-library server class in your Python 3.12+ interpreter:

```python
import socketserver

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True

print([cls.__name__ for cls in ThreadedTCPServer.__mro__])
```

Expected class-name order on a standard CPython installation is:

```text
['ThreadedTCPServer', 'ThreadingMixIn', 'TCPServer', 'BaseServer', 'object']
```

Read the current `socketserver` documentation before overriding `process_request`, `process_request_thread`, or shutdown behavior: the mixin is deliberately placed before `TCPServer`, and ordering affects which methods are found first. For a web-framework analogue, inspect a concrete Django generic `ListView` and trace contributions from `MultipleObjectTemplateResponseMixin` and `BaseListView`; the exact MRO and implementation details should be checked against the installed Django version rather than memorized from an unrelated release.

## 15. When composition, delegation, or a protocol is safer

Use composition when the capability is a separate collaborator with its own state, dependencies, lifecycle, or configuration. Use a plain function when the behavior is a stateless transformation that does not need access to host internals. Use a protocol when the goal is to describe a required interface without prescribing inheritance.

```python
from dataclasses import dataclass


@dataclass
class TimestampFormatter:
    format_string: str = "%Y-%m-%dT%H:%M:%S"

    def format(self, value: object) -> str:
        # A real implementation would accept datetime explicitly.
        return f"{value!s} ({self.format_string})"


class Event:
    def __init__(self, timestamp: object, formatter: TimestampFormatter) -> None:
        self.timestamp = timestamp
        self._formatter = formatter

    def formatted_timestamp(self) -> str:
        return self._formatter.format(self.timestamp)
```

Here the formatter is an explicit dependency. It can be configured, replaced, and tested independently without changing the Event class's inheritance graph.

A useful decision question is: **Does the behavior need to be part of the host's method-resolution chain, or does the host simply need to use another object?** If the latter, composition is often clearer.

## 16. Testing mixins and the combined class

Test at three levels:

1. **Focused behavior:** a tiny host proves a mixin's documented requirement and output.
2. **Composition:** the real combined class verifies method order, signatures, and return values.
3. **Failure contracts:** tests demonstrate that missing host attributes, unknown constructor arguments, and incompatible combinations fail clearly.

Do not stop after testing each mixin in isolation. Many defects only appear when methods collide or a `super()` chain crosses the concrete class and several mixins.

### Pytest test suite

Save the relevant examples in a module, for example `mixins_example.py`, then place this test file beside it. The tests below target the `Pipeline`, `CustomerRecordProcessor`, `Job`, and diamond `Final` examples from this lesson. If you keep examples in the same test module, remove the import and leave the tests unchanged.

```python
from datetime import datetime, timezone

import pytest

from mixins_example import CustomerRecordProcessor, Final, Job, Pipeline


def test_pipeline_composes_both_mixins_in_mro_order() -> None:
    assert Pipeline().run("job") == "prefix:job:suffix"
    assert [cls.__name__ for cls in Pipeline.__mro__] == [
        "Pipeline", "PrefixMixin", "SuffixMixin", "BasePipeline", "object"
    ]


def test_processor_runs_every_layer_once_in_order() -> None:
    trace: list[str] = []
    result = CustomerRecordProcessor().process("  CUSTOMER-42  ", trace=trace)
    assert result == "customer-42|source=etl"
    assert trace == ["normalize", "audit", "enrich", "terminal"]


def test_constructor_mixins_consume_their_own_keywords() -> None:
    job = Job(tenant_id="tenant-7", retries=2)
    assert job.tenant_id == "tenant-7"
    assert job.retries == 2


def test_constructor_rejects_unknown_keyword() -> None:
    with pytest.raises(TypeError, match="unexpected constructor arguments: retry"):
        Job(tenant_id="tenant-7", retry=2)  # type: ignore[call-arg]


def test_diamond_initializes_root_once(capsys) -> None:
    Final()
    assert capsys.readouterr().out.splitlines() == ["Final", "Left", "Right", "Root"]


def test_timestamp_mixin_contract_and_host_mro() -> None:
    class TimestampMixin:
        def created_at_iso(self) -> str:
            value = self.created_at
            if not isinstance(value, datetime):
                raise TypeError("created_at must be a datetime")
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError("created_at must be timezone-aware")
            return value.astimezone(timezone.utc).isoformat()

    class Event(TimestampMixin):
        def __init__(self, created_at: datetime) -> None:
            self.created_at = created_at

    event = Event(datetime(2025, 1, 1, tzinfo=timezone.utc))
    assert event.created_at_iso() == "2025-01-01T00:00:00+00:00"
    assert [cls.__name__ for cls in Event.__mro__] == ["Event", "TimestampMixin", "object"]


def test_timestamp_mixin_rejects_naive_datetime() -> None:
    class TimestampMixin:
        def created_at_iso(self) -> str:
            value = self.created_at
            if not isinstance(value, datetime):
                raise TypeError("created_at must be a datetime")
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError("created_at must be timezone-aware")
            return value.astimezone(timezone.utc).isoformat()

    class Event(TimestampMixin):
        def __init__(self, created_at: datetime) -> None:
            self.created_at = created_at

    with pytest.raises(ValueError, match="timezone-aware"):
        Event(datetime(2025, 1, 1)).created_at_iso()
```

**Test note:** `capsys` is a built-in pytest fixture. The diamond test checks observed constructor order, not just the MRO list. The timestamp tests use a minimal host to test the mixin's explicit attribute contract and its timezone failure mode. Keep the example classes in a module named `mixins_example.py` if using the import as written; put demonstration `print()` calls under `if __name__ == "__main__":` so importing that module for tests has no side effects.

## 17. Debugging checklist for a surprising mixin hierarchy

1. Print the actual MRO: `print([cls.__name__ for cls in type(obj).__mro__])`.
2. Identify the first class defining the surprising method: inspect each class in order, for example `cls.__dict__.get("method_name")`.
3. Trace each cooperative call: add temporary logging immediately before and after `super().method(...)`.
4. Compare signatures and keyword forwarding across every method in the chain.
5. Confirm each mixin's host attributes are documented and initialized before use.
6. Search for explicit calls such as `Parent.method(self, ...)` that bypass the MRO chain.
7. Check for a method that omits `super()` or calls it more than once.
8. Check class attribute/instance attribute name collisions and accidental overrides.
9. If class creation fails, distinguish inconsistent MRO, metaclass conflict, and instance-layout conflict.
10. Reproduce the issue with a minimal hierarchy and a test that asserts the complete call trace.

## 18. Exercises with worked solutions

### Exercise 1 — Why does the mixin lose?

Given `class Report(BaseReport, JsonMixin): ...`, `BaseReport` and `JsonMixin` both define `to_json()`. Which implementation is found first, and how would you fix the order if the mixin is intended to supply the behavior?

**Solution:** `BaseReport` comes before `JsonMixin` in the MRO, so its `to_json()` is found first. Prefer `class Report(JsonMixin, BaseReport)` if the mixin is intended to override or wrap the base behavior. If it should extend the base implementation, implement the mixin method cooperatively with `super()` and test the actual order.

### Exercise 2 — Write a `TimestampMixin`

Implement a mixin that formats a host-provided `created_at` value. Include a tiny host and show the MRO. Avoid pretending that every arbitrary object has a timestamp.

**Solution:**

```python
from datetime import datetime, timezone


class TimestampMixin:
    def created_at_iso(self) -> str:
        value = self.created_at  # documented host contract
        if not isinstance(value, datetime):
            raise TypeError("created_at must be a datetime")
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("created_at must be timezone-aware")
        return value.astimezone(timezone.utc).isoformat()


class Event(TimestampMixin):
    def __init__(self, created_at: datetime) -> None:
        self.created_at = created_at


item = Event(datetime(2025, 1, 1, tzinfo=timezone.utc))
print(item.created_at_iso())
print([cls.__name__ for cls in Event.__mro__])
```

Expected output:

```text
2025-01-01T00:00:00+00:00
['Event', 'TimestampMixin', 'object']
```

### Exercise 3 — Find the broken cooperative chain

A mixin's `process()` method transforms the input and returns without calling `super().process()`. What happens when another mixin follows it in the MRO?

**Solution:** the later mixin and terminal implementation are skipped. If the method is designed as a cooperative wrapper, delegate once to `super()` and transform the input/output around that call. If it is intentionally terminal, document that it stops the chain and do not present it as cooperative.

### Exercise 4 — Choose mixin or composition

A reusable formatter has configurable locale, timezone, and external dependencies. Should it be a mixin?

**Solution:** composition is usually clearer. The formatter has its own configuration and lifecycle and does not need to alter host method lookup. Inject it into the class and delegate formatting to it.

### Exercise 5 — Constructor contract

A cooperative mixin consumes `timeout`, another consumes `retries`, and the terminal base rejects unknown keywords. Describe the contract needed to avoid dropping arguments or raising a false error.

**Solution:** each mixin explicitly binds and validates its own keyword, forwards all remaining keywords through `super().__init__(**kwargs)`, and the terminal base checks that no unexpected keywords remain. All participants must use compatible keyword-based signatures and call `super()` exactly once.

## 19. Roadmap self-check answers

1. **Why is `class A(Mixin, Base)` the usual order?** Because the mixin appears earlier in the MRO, so its method can contribute behavior before the concrete base's implementation. If it delegates with `super()`, the base implementation can still run later in the chain.
2. **Write a `TimestampMixin` and a test host; show an MRO listing.** Exercise 2 supplies a timezone-aware implementation, host class, expected output, and MRO: `Event → TimestampMixin → object`.
3. **Name two situations where composition beats a mixin.** (a) The behavior has substantial independent state/configuration or a lifecycle, such as a locale-aware formatter. (b) The host only needs to call a helper/service and does not need the helper to participate in method resolution. Other valid examples include external dependencies or avoiding collisions in a large hierarchy.

## 20. Common mistakes from the roadmap

- **Mixin reads an attribute the host never defines.** Document the host contract, use clear types/protocols where useful, and test a realistic host. Avoid hidden assumptions such as `self.some_attr` with no declaration.
- **Concrete base listed before the mixin.** `class A(Base, Mixin)` often means `Base`'s method wins before the mixin is consulted. Use `class A(Mixin, Base)` when the mixin is intended to contribute the behavior, and verify the MRO.
- **Stateful mixin adds its own `__init__` without cooperation.** This can skip later initialization or duplicate work. Prefer stateless mixins; otherwise use a documented keyword-only cooperative contract or composition.

Related pitfalls covered by the lesson: explicitly calling a named parent rather than `super()`, inconsistent constructor signatures, missing `super()` calls, generic name collisions, assumptions about initialization order, and treating a valid MRO as proof of a sound design.

## 21. Final review checklist

Before merging a mixin-based design, verify:

- [ ] Each mixin has one focused responsibility and a clear name.
- [ ] Its host attributes and methods are documented; no hidden assumptions remain.
- [ ] It is stateless unless state is justified and explicitly initialized.
- [ ] Base order matches intended lookup behavior; the actual MRO has been inspected.
- [ ] Cooperative methods use `super()` consistently and have compatible signatures.
- [ ] Each constructor consumes only its own arguments, forwards the rest, and validates leftovers at the terminal boundary.
- [ ] Every intended layer runs exactly once; no method silently truncates the chain.
- [ ] Method and attribute collisions have been ruled out or intentionally documented.
- [ ] The design does not call overridable methods before required state exists.
- [ ] Diamond behavior is tested for duplicate initialization and side effects.
- [ ] Special methods are tested through the relevant built-in operation.
- [ ] Dataclass, `__slots__`, metaclass, and layout implications have been considered where applicable.
- [ ] Composition, delegation, or a protocol was considered and rejected for a clear reason.
- [ ] Tests cover the combined class, call order, result, constructor contract, and failure modes.

**Engineering principle:** multiple inheritance is a mechanism, not a goal. A mixin is successful when it adds one predictable capability with an explicit contract and makes the resulting class easier—not harder—to understand.
