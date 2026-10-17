# Lesson 07 — Advanced Dataclasses and `attrs`

> **Version policy:** New examples target Python 3.12+. Most examples also work on later Python 3 releases. Version-specific features are labelled. Third-party examples use `attrs` 26.x and Pydantic v2 APIs; check the versions pinned by your project.

## Learning objectives

By the end of this lesson, you should be able to choose a record model deliberately, design reliable defaults and constructors, control equality and hashing, distinguish shallow from deep immutability, validate a domain object, serialize it with an explicit schema, and explain when standard-library dataclasses, `attrs`, Pydantic, `TypedDict`, or `NamedTuple` fit best.

## 1. Mental model: a data model has more than fields

A record type defines several contracts:

1. **Construction:** which values are accepted by the constructor and in what order.
2. **Representation:** how the object appears in debugging output.
3. **Equality and ordering:** which fields determine whether two objects are equivalent.
4. **Mutation policy:** whether fields, nested values, or both may change.
5. **Validation:** whether values are checked at runtime, and at which boundary.
6. **Serialization:** how values become a stable external representation.
7. **Memory and performance:** per-instance overhead, allocation, and attribute access.

`@dataclass` primarily generates boilerplate. It does **not** automatically validate annotations or create a stable wire format.

### Version guide

| Feature | Introduced | Notes |
|---|---:|---|
| `dataclasses.dataclass`, `field`, `InitVar`, `asdict`, `replace` | Python 3.7 | Standard library; `dataclasses` backport exists for older supported versions. |
| `typing.Annotated` | Python 3.9 | Metadata itself does not enforce validation. |
| `kw_only`, `KW_ONLY`, `slots`, `match_args` | Python 3.10 | `slots=True` returns a new class object; consider inheritance carefully. |
| `weakref_slot` | Python 3.11 | Requires `slots=True`. |
| `typing.dataclass_transform` | Python 3.11 | Helps static analyzers understand dataclass-like decorators; does not generate methods by itself. |
| `attrs` and Pydantic features | Third-party | Behavior depends on the installed/pinned package version, not the Python minor version alone. Pydantic v2's core validation/serialization engine (`pydantic-core`) is implemented in Rust; this does not guarantee it wins every workload benchmark. |

## 2. Beginner: a first dataclass

A dataclass normally generates `__init__`, `__repr__`, and `__eq__`. It can also generate ordering and hashing according to options. It does not generate every possible method and it does not validate values merely because fields are annotated.

```python
from dataclasses import dataclass

@dataclass
class Product:
    sku: str
    name: str
    price_cents: int

p = Product("SKU-1", "Notebook", 499)
print(p)
print(p == Product("SKU-1", "Notebook", 499))
```

Expected output:

```text
Product(sku='SKU-1', name='Notebook', price_cents=499)
True
```

`price_cents: int` is a contract for readers and static type checkers. Unless your code or a library validates it, `Product("SKU-1", "Notebook", "cheap")` can still be constructed at runtime.

### 2.1 Defaults: `default` and `default_factory`

Use `field(default=...)` for a shared immutable default, or `field(default_factory=...)` when each instance needs a newly created value.

```python
from dataclasses import dataclass, field

@dataclass
class RequestContext:
    request_id: str
    tags: tuple[str, ...] = ()
    attributes: dict[str, str] = field(default_factory=dict)

left = RequestContext("r-1")
right = RequestContext("r-2")
left.attributes["region"] = "ap-south-1"
assert right.attributes == {}
```

Do not write `attributes: dict[str, str] = {}`. Dataclasses reject common mutable defaults, and since Python 3.11 the rejection is based on unhashability rather than only a hard-coded list of mutable built-ins. A custom mutable-but-hashable object may still be accepted; that does not make it a safe shared default.

`default_factory` must be a zero-argument callable, such as `list`, `dict`, `set`, or a function you define. Do not pass `default_factory=[]`.

### 2.2 Common options

```python
from dataclasses import dataclass, field

@dataclass(frozen=True, slots=True, kw_only=True)
class Event:
    name: str
    tags: tuple[str, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict, compare=False)
```

- `frozen=True` blocks ordinary attribute assignment/deletion after initialization; it is not recursive immutability.
- `slots=True` creates slot-backed attributes and normally removes the per-instance `__dict__`, reducing memory for many instances. It may affect inheritance and introspection.
- `kw_only=True` makes fields keyword-only in the generated constructor. It can make APIs safer as field lists evolve.
- `order=True` generates ordering methods based on comparable fields in declaration order. It requires `eq=True`; ordering unrelated domain concepts may be meaningless.
- `repr=True` and `compare=True` are field defaults. Set them deliberately for secrets, large fields, and non-semantic metadata.

## 3. Equality, ordering, and hashing are domain decisions

By default, dataclass equality compares the fields marked `compare=True`, and requires the compared objects to have the same concrete type. It is not automatically a database identity comparison.

Hashing rules for the common combinations:

| Configuration | Typical generated behavior | Implication |
|---|---|---|
| `eq=True`, `frozen=False` (defaults) | `__hash__ = None` | Instances are unhashable; this avoids unsafe hash keys when equality-relevant fields can mutate. |
| `eq=True`, `frozen=True` | Generates a hash by default | Hashing succeeds only if all fields included in the hash are hashable. |
| `eq=False` | Does not generate equality or hash | Existing superclass behavior is retained. |
| `unsafe_hash=True` | Forces hash generation in cases where dataclasses normally would not | Use only if hash-relevant state cannot change while the object is a key/set member. |

`frozen=True` does not guarantee every field is hashable. A frozen object containing a `list` may be unhashable, and a frozen object containing a mutable but hashable object can still violate hash stability if that nested object changes.

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class CacheKey:
    tenant: str
    options: tuple[tuple[str, str], ...]

@dataclass
class MutableRecord:
    record_id: str
    labels: list[str] = field(default_factory=list)

assert CacheKey("t1", (("mode", "fast"),)) == CacheKey("t1", (("mode", "fast"),))
try:
    hash(MutableRecord("x"))
except TypeError:
    print("mutable record is unhashable")
```

Expected output: `mutable record is unhashable`.

Avoid `unsafe_hash=True` as a shortcut. If equality is based on a mutable field, changing that field after inserting the object into a dictionary or set can make lookups behave incorrectly.

## 4. Intermediate: validation and derived fields with `__post_init__`

The generated initializer assigns normal fields, then calls `__post_init__` if one is defined. Use it for invariants and deterministic derived values—not for complex I/O or hidden side effects. The constructor signature is generated from fields with `init=True`, respecting field defaults and keyword-only status; `InitVar` parameters appear in that signature even though they are not stored as normal fields.

```python
from dataclasses import dataclass, field
from decimal import Decimal

@dataclass(frozen=True, slots=True)
class LineItem:
    sku: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.sku, str) or not self.sku.strip():
            raise ValueError("sku must be a non-blank string")
        if isinstance(self.quantity, bool) or not isinstance(self.quantity, int) or self.quantity <= 0:
            raise ValueError("quantity must be a positive integer")
        if not isinstance(self.unit_price, Decimal) or not self.unit_price.is_finite() or self.unit_price < 0:
            raise ValueError("unit_price must be a finite non-negative Decimal")
        object.__setattr__(self, "sku", self.sku.strip())
        object.__setattr__(self, "line_total", self.unit_price * self.quantity)
```

`object.__setattr__` is a controlled initialization technique for frozen classes. It should be limited to initialization-time normalization/derived values, not used to bypass the object's immutability contract later.

For strict runtime validation, check actual runtime types when needed. The condition `quantity <= 0` alone would not reject `True`, because `bool` is a subclass of `int`; the example rejects it explicitly. A static checker may catch many such mistakes in typed callers, but cannot validate arbitrary JSON, database rows, or values arriving from untyped code.

### 4.1 `InitVar` and field flags

`InitVar[T]` is an initialization-only parameter: it is passed to `__post_init__` but is not a normal stored dataclass field. It is useful for input needed to compute stored state, such as a tax rate or a validation policy. Do not put secrets in an `InitVar` and assume they are automatically hidden from logs; callers and tracing can still observe constructor arguments.

```python
from dataclasses import InitVar, dataclass, field
from decimal import Decimal

@dataclass
class Price:
    net: Decimal
    tax_rate: InitVar[Decimal]
    gross: Decimal = field(init=False)

    def __post_init__(self, tax_rate: Decimal) -> None:
        if tax_rate < 0:
            raise ValueError("tax_rate must be non-negative")
        self.gross = self.net * (Decimal("1") + tax_rate)
```

Field options:

- `init=False`: omit the field from the generated constructor; often used for derived state.
- `repr=False`: exclude it from generated `repr` output (useful for credentials or large payloads).
- `compare=False`: exclude it from generated equality and ordering.
- `hash=False`: exclude it from generated hash calculation. If omitted, it follows `compare` by default; a field may intentionally be compared but not hashed when hashing it is expensive, but this requires care with equality/hash consistency.
- `metadata={...}`: attach a read-only metadata mapping for frameworks; dataclasses do not interpret it themselves.

A combined example shows how the flags affect the constructor, `repr`, equality, and hashing. `hash=False` with `compare=False` is redundant for the generated hash, but explicit declarations can document intent; a field with `compare=True, hash=False` is also permitted when hashing it is expensive, because equal objects must still have equal hashes (collisions are acceptable).

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class CredentialView:
    principal: str
    token: str = field(repr=False, compare=False, hash=False)
    fingerprint: str = field(init=False, repr=False, compare=False, hash=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "fingerprint", f"fp:{self.principal}")

credential = CredentialView("service-a", "do-not-log-this")
assert "do-not-log-this" not in repr(credential)
assert credential == CredentialView("service-a", "different-token")
assert credential.fingerprint == "fp:service-a"
assert len({credential, CredentialView("service-a", "another-token")}) == 1
```

Do not treat `repr=False` as a complete secret-management boundary: custom logging, serializers, debuggers, and explicit attribute access may still expose a value.

### 4.2 Inspection and transformation helpers

```python
from dataclasses import asdict, astuple, dataclass, fields, is_dataclass, replace

@dataclass
class Coordinate:
    x: float
    y: float
    label: str = "origin"

point = Coordinate(2.0, 3.0)
assert is_dataclass(point)
assert [f.name for f in fields(point)] == ["x", "y", "label"]
assert astuple(point) == (2.0, 3.0, "origin")
assert asdict(point) == {"x": 2.0, "y": 3.0, "label": "origin"}
assert replace(point, x=4.0) == Coordinate(4.0, 3.0, "origin")
```

Important behavior:

- `fields()` returns dataclass fields, excluding `ClassVar` and `InitVar` pseudo-fields.
- `asdict()` and `astuple()` recursively process dataclasses and containers and deep-copy other objects. They are not automatically a stable JSON schema or a cheap shallow view.
- `replace(obj, ...)` creates a new instance by calling the class initializer. Fields with `init=False` are not copied from the old instance; they are typically recomputed by `__post_init__`. Required `InitVar` arguments without defaults may need to be passed again.
- `is_dataclass(SomeClass)` and `is_dataclass(instance)` can both be true; if your API must distinguish class from instance, add `not isinstance(x, type)` or use an explicit check.

### 4.3 `KW_ONLY` and positional pattern matching

Python 3.10 added `KW_ONLY` as a sentinel: fields after it are keyword-only in the generated initializer. This is useful when you want earlier fields positional and later extension fields keyword-only.

```python
from dataclasses import KW_ONLY, dataclass

@dataclass
class Connection:
    host: str
    port: int
    _: KW_ONLY
    timeout_seconds: float = 3.0

assert Connection("localhost", 5432, timeout_seconds=1.5).timeout_seconds == 1.5
```

`match_args` (Python 3.10+) controls generation of `__match_args__` for positional structural pattern matching. By default it is derived from the generated initializer's non-keyword-only parameters; keyword-only fields are not included. Set `match_args=False` when positional matching should not be part of the public API. Prefer keyword patterns for public models where field order may evolve.

Use `inspect.signature()` to verify the constructor contract instead of guessing from annotations or field order:

```python
from inspect import Parameter, signature

connection_signature = signature(Connection)
assert connection_signature.parameters["host"].default is Parameter.empty
assert connection_signature.parameters["timeout_seconds"].default == 3.0
assert connection_signature.parameters["timeout_seconds"].kind is Parameter.KEYWORD_ONLY
```

`weakref_slot=True` (Python 3.11+) adds a `__weakref__` slot when using `slots=True`. It requires `slots=True` and is useful only when weak references are needed. A base class that already supports weak references may affect whether you need this option.

## 5. Inheritance and constructor ordering

Dataclasses collect fields from dataclass bases in reverse MRO order and then add subclass fields. A non-default field cannot follow a default field in the generated positional initializer—even if the fields come from different classes. This can make a subclass fail at class creation.

```python
from dataclasses import dataclass

@dataclass
class BaseConfig:
    region: str = "ap-south-1"

# This raises TypeError at class definition: required field follows a default.
# @dataclass
# class AppConfig(BaseConfig):
#     service_name: str
```

Safer options include making fields keyword-only or designing a base class whose required fields precede defaults.

```python
from dataclasses import dataclass

@dataclass(kw_only=True)
class BaseConfig:
    region: str = "ap-south-1"

@dataclass
class AppConfig(BaseConfig):
    service_name: str

config = AppConfig(service_name="orders")
assert config.region == "ap-south-1"
```

This example makes the base field keyword-only and leaves the required subclass field positional-or-keyword. If the subclass itself also uses `kw_only=True`, both become keyword-only.

### 5.1 `slots=True`, `cached_property`, and `super()` pitfalls

- `functools.cached_property` normally writes into the instance `__dict__`; a slotted class without `__dict__` cannot use it as intended. Add a `__dict__` slot deliberately if necessary, or use an explicit cached field/property strategy.
- `slots=True` causes `@dataclass` to return a new class. In certain inheritance patterns, zero-argument `super()` inside methods can fail because it refers to the original class cell. When encountering this, test the exact hierarchy and consider `super(CurrentClass, self)` or redesigning the class; do not assume every `slots=True` hierarchy is broken.
- Subclass slot generation omits slot names already present in base classes. Use `dataclasses.fields()` rather than treating `__slots__` as a complete field list.
- Slots constrain dynamic attributes and can complicate multiple inheritance, weak references, and frameworks that expect `__dict__`.

### 5.2 `dataclass_transform`

`typing.dataclass_transform` (Python 3.11+) tells static type checkers that a decorator, base class, or metaclass behaves like a dataclass constructor. It does not create `__init__`, equality, or other methods at runtime.

```python
from typing import dataclass_transform

@dataclass_transform()
def model(cls: type) -> type:
    # A real framework must implement runtime behavior separately.
    return cls
```

This is only a typing declaration. The toy decorator above does **not** generate a constructor; a framework must implement that behavior itself.

## 6. Immutability: frozen is shallow

`frozen=True` prevents ordinary rebinding of attributes, but nested mutable values remain mutable. This is true for dictionaries as well as lists; freezing the outer object does not freeze a contained mapping:

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class FrozenEnvelope:
    labels: list[str] = field(default_factory=list)

message = FrozenEnvelope()
message.labels.append("still mutable")  # allowed: the list itself is mutable
assert message.labels == ["still mutable"]

@dataclass(frozen=True)
class FrozenMetadata:
    values: dict[str, str] = field(default_factory=dict)

metadata = FrozenMetadata()
metadata.values["region"] = "ap-south-1"  # allowed: the nested dict is mutable
assert metadata.values["region"] == "ap-south-1"
```

For stronger immutability, prefer immutable field types such as `tuple`, `frozenset`, `Decimal`, and immutable value objects. For mappings, `types.MappingProxyType` provides a read-only view, but it is a *view* of its underlying mapping: if another reference mutates the original dictionary, the view reflects that mutation. Copy first if you need to prevent outside aliases from changing the data.

```python
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

@dataclass(frozen=True)
class ImmutableSettings:
    values: Mapping[str, str]

    @classmethod
    def from_mapping(cls, values: Mapping[str, str]) -> "ImmutableSettings":
        return cls(MappingProxyType(dict(values)))
```

The copy breaks the caller's dictionary alias; the proxy prevents mutation through this field. This remains shallow: nested values would need their own immutable conversion.

## 7. `attrs`: richer class modeling

`attrs` predates standard-library dataclasses and provides validators, converters, field transforms, and other features. Its APIs differ slightly; use docs for the pinned release. `attrs.define` is a modern class decorator and commonly uses slots by default (unless configured otherwise). It is not part of the Python standard library.

```python
from attrs import define, field, validators, evolve

@define(frozen=True)
class CustomerId:
    value: str = field(
        converter=str,
        validator=[validators.instance_of(str), validators.min_len(1)],
    )

original = CustomerId("C-100")
updated = evolve(original, value="C-101")
assert original.value == "C-100"
assert updated.value == "C-101"
```

Here `converter=str` coerces input before validators run; coercion is a design choice, not a guarantee of strict input validation. For example, converting arbitrary objects to strings may hide upstream mistakes. `validators.instance_of(str)` and `min_len(1)` then validate the converted value. Verify the exact validator API against the attrs version you pin.

Attrs validators can be composed, and validators may be disabled at runtime by configuration. Do not treat type annotations alone as validators. `attrs.evolve(instance, field=value)` creates a new instance; it does not mutate the original. `@define(frozen=True)` blocks normal attribute reassignment, but like a frozen dataclass it does not recursively freeze a list or dictionary stored in a field.

### When `attrs` may be preferable

- You want converters and validators integrated directly into class declarations.
- You need mature field transformation and class-construction hooks.
- You want immutable or slotted records with less custom boilerplate.
- Your team already standardizes on attrs and its ecosystem (for example `cattrs` for structuring/unstructuring).

Standard-library dataclasses are often preferable when dependencies should stay minimal or the model is simple. Neither is universally faster or safer in every workload; benchmark representative use cases.

## 8. Pydantic v2 at untrusted boundaries

Pydantic models perform runtime validation and can coerce inputs according to their configuration. This is useful for HTTP payloads, configuration, and external data. Pydantic's default coercion behavior is not the same as strict validation; use strict modes or field constraints when coercion is undesirable.

```python
from pydantic import BaseModel, ConfigDict, Field

class OrderInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sku: str = Field(min_length=1)
    quantity: int = Field(gt=0, strict=True)
    unit_price: str = Field(pattern=r"^\d+(?:\.\d{1,2})?$")

payload = {"sku": "SKU-1", "quantity": 2, "unit_price": "12.50"}
parsed = OrderInput.model_validate(payload)
print(parsed.model_dump())
print(OrderInput.model_json_schema()["title"])
```

Expected output (dictionary key order shown as emitted by this declaration):

```text
{'sku': 'SKU-1', 'quantity': 2, 'unit_price': '12.50'}
OrderInput
```

This example keeps price as a validated decimal-formatted string to avoid accidental binary-float arithmetic at the boundary. Convert to `Decimal` in the domain layer with an explicit policy. `model_validate` raises a `ValidationError` for invalid payloads; `model_dump` serializes model fields to Python data structures, and `model_json_schema` generates JSON Schema.

A common architecture is **Pydantic at the boundary, domain dataclasses inside**: validate and normalize external data once, then use simple domain objects with explicit invariants. Pydantic dataclasses are also available; choose based on whether you need BaseModel's validation/schema/serialization API.

## 9. Tool choice decision table

| Tool | Runtime shape | Runtime validation? | Best fit | Main trade-off |
|---|---|---|---|---|
| `dataclass` | Normal Python class | No, unless implemented | Internal domain records, configs, events | Low dependency cost; you own validation and serialization policy. |
| `attrs` | Normal Python class | Validators/converters when configured | Rich record modeling and validation hooks | Extra dependency and ecosystem-specific APIs. |
| Pydantic v2 `BaseModel` | Model class with validation APIs | Yes, according to model/config | Untrusted payloads, API schemas, settings | Rust-backed `pydantic-core` handles core validation/serialization; actual performance depends on schema and workload. Coercion policy and runtime cost need deliberate configuration. |
| `TypedDict` | Plain `dict` at runtime | No | Static contracts for dictionary-shaped data | No generated object behavior or runtime enforcement. |
| `NamedTuple` | Tuple subclass | No | Small immutable positional records/interoperability | Tuple semantics and positional coupling can be awkward for evolving APIs. |
| `dict` | Plain mapping | No | Dynamic/unstructured data | Weak static contract unless separately typed. |

Choose according to the boundary and invariant, not fashion. A DTO for a JSON API, an internal domain object, and a database persistence record may reasonably use different types.

## 10. Production `Order`: money, invariants, and derived totals

Use `Decimal` for decimal money values when the business contract is decimal arithmetic. Establish whether prices include tax, the rounding mode, currency, and scale explicitly; the example below keeps the model deliberately small and rounds line totals to cents using `quantize`.

```python
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")

@dataclass(frozen=True, slots=True, kw_only=True)
class OrderLine:
    sku: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.sku, str) or not self.sku.strip():
            raise ValueError("sku must be a non-blank string")
        if isinstance(self.quantity, bool) or not isinstance(self.quantity, int) or self.quantity <= 0:
            raise ValueError("quantity must be a positive integer")
        if not isinstance(self.unit_price, Decimal) or not self.unit_price.is_finite() or self.unit_price < 0:
            raise ValueError("unit_price must be a finite non-negative Decimal")
        object.__setattr__(self, "sku", self.sku.strip())
        object.__setattr__(self, "line_total", (self.unit_price * self.quantity).quantize(CENT, rounding=ROUND_HALF_UP))

@dataclass(frozen=True, slots=True, kw_only=True)
class Order:
    order_id: str
    lines: tuple[OrderLine, ...]
    currency: str = "INR"
    total: Decimal = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.order_id, str) or not self.order_id.strip():
            raise ValueError("order_id must be a non-blank string")
        if not isinstance(self.lines, tuple) or not self.lines:
            raise ValueError("lines must be a non-empty tuple of OrderLine values")
        if not all(isinstance(line, OrderLine) for line in self.lines):
            raise ValueError("every line must be an OrderLine")
        if not isinstance(self.currency, str) or not self.currency.isascii() or not self.currency.isalpha() or len(self.currency) != 3:
            raise ValueError("currency must be a three-letter ASCII code")
        object.__setattr__(self, "order_id", self.order_id.strip())
        object.__setattr__(self, "currency", self.currency.upper())
        object.__setattr__(self, "total", sum((line.line_total for line in self.lines), start=Decimal("0.00")))

line = OrderLine(sku=" SKU-7 ", quantity=3, unit_price=Decimal("19.995"))
order = Order(order_id="ORD-42", lines=(line,))
assert line.sku == "SKU-7"
assert line.line_total == Decimal("59.99")
assert order.total == Decimal("59.99")
```

This model has no untrusted-input parser. Constructing it directly validates the invariants shown in `__post_init__`, but upstream values still need parsing into the expected Python types. If currency-specific precision, tax, discounts, refunds, or multiple rounding stages matter, encode those rules explicitly and test them against business requirements.

### 10.1 Equality and identity

The generated equality compares all fields not marked `compare=False`, including the derived total. Because `total` is a deterministic function of `lines`, including it is redundant but consistent. For entities whose identity is `order_id`, you might instead choose `compare=False` for descriptive fields or implement explicit identity semantics. Do not accidentally use value equality where identity equality is required.

### 10.2 Frozen/slotted value object

`OrderLine` and `Order` are frozen and slotted. Their stored nested collection uses a tuple, and each line is itself frozen. This is substantially stronger than `frozen=True` with a list field, though Python cannot provide a universal security boundary against deliberate low-level mutation. `Decimal` is immutable, so it is suitable for this model.

## 11. Serialization: define a schema instead of serializing an object blindly

`asdict()` is useful for local transformations, but `json.dumps(asdict(order))` will not automatically serialize `Decimal`. Prefer an explicit versioned wire representation with deliberate conversions.

```python
import json
from decimal import Decimal
from enum import StrEnum

class OrderStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"

def order_to_wire(order: Order, status: OrderStatus) -> dict[str, object]:
    return {
        "schema_version": 1,
        "order_id": order.order_id,
        "currency": order.currency,
        "status": status.value,
        "lines": [
            {
                "sku": line.sku,
                "quantity": line.quantity,
                "unit_price": str(line.unit_price),
                "line_total": str(line.line_total),
            }
            for line in order.lines
        ],
        "total": str(order.total),
    }

wire = order_to_wire(order, OrderStatus.PENDING)
encoded = json.dumps(wire, sort_keys=True)
assert json.loads(encoded)["schema_version"] == 1
assert Decimal(json.loads(encoded)["total"]) == order.total
```

Notes:

- `StrEnum` was introduced in Python 3.11. For Python 3.10 and older, use `class OrderStatus(str, Enum)` or a string-valued enum pattern.
- ISO 8601 strings are a common explicit representation for dates/times, but define timezone handling and precision. Do not silently treat naive datetimes as UTC.

This small round-trip makes the conversion policy executable. It preserves a date, an aware UTC timestamp, a decimal amount, an enum value, and a schema version without relying on a generic `str()` fallback:

```python
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import StrEnum

class WireState(StrEnum):
    OPEN = "open"
    CLOSED = "closed"

original_date = date(2026, 10, 17)
original_time = datetime(2026, 10, 17, 12, 30, tzinfo=timezone.utc)
wire_record = {
    "schema_version": 1,
    "created_on": original_date.isoformat(),
    "created_at": original_time.isoformat(),
    "amount": str(Decimal("12.30")),
    "state": WireState.OPEN.value,
}
round_tripped_date = date.fromisoformat(wire_record["created_on"])
round_tripped_time = datetime.fromisoformat(wire_record["created_at"])
assert round_tripped_date == original_date
assert round_tripped_time == original_time
assert Decimal(wire_record["amount"]) == Decimal("12.30")
assert WireState(wire_record["state"]) is WireState.OPEN
assert wire_record["schema_version"] == 1
```

`datetime.fromisoformat()` preserves the encoded offset; it does not by itself normalize every timestamp to UTC. A schema must state whether offsets are preserved, normalized, or rejected. `StrEnum` requires Python 3.11+; the lesson's default Python 3.12+ target supports it.
- Encode `Decimal` as a decimal string or as integer minor units according to a documented contract; avoid binary floats for money.
- Persist enum values or stable codes, not assumptions about member names.
- Increment `schema_version` when a change is not backward-compatible; define migration and unknown-field behavior.
- A serializer should reject or intentionally handle unsupported values rather than silently calling `str()` on everything.

### Why not pickle for durable storage?

Pickle is Python-specific, can be fragile across code/schema changes, and unpickling untrusted data can execute arbitrary code. Use it only for trusted, controlled Python-to-Python workflows with a clear compatibility policy. For durable business data or cross-language APIs, prefer a documented schema such as JSON, Avro, Protobuf, or another format appropriate to the system.

## 12. Memory and performance

For large populations of small objects, `slots=True` can reduce per-instance memory by avoiding a per-instance dictionary. The actual benefit depends on inheritance, fields, object count, Python implementation, and what the fields reference. Slotted records do not make the objects referenced by fields smaller.

Benchmark realistic workloads before choosing based on performance claims. Measure object allocation, retained memory, construction throughput, and attribute access using the actual Python version and representative field distributions. Include the costs of validation and serialization if those are on the hot path.

## 13. Copy-on-modify and state transitions

For immutable models, `dataclasses.replace()` supports copy-on-modify:

```python
from dataclasses import replace

paid_order = replace(order, currency="USD")
assert order.currency == "INR"
assert paid_order.currency == "USD"
```

This example demonstrates copying, not a real currency conversion: production code must not change a currency code without converting monetary amounts. For domain transitions, expose intention-revealing methods that enforce invariants (for example, `mark_paid(payment_id=...)`) rather than allowing arbitrary field replacement everywhere.

A builder is useful when a valid object needs many incremental inputs. Keep the mutable builder separate from the immutable finished value, and validate on `build()`. Do not let a builder leak mutable aliases into the final object.

## 14. Testing strategies

Test the contract, not just the generated repr. Include valid construction, invalid boundaries, equality, hashability, derived fields, replacement behavior, serialization round-trips, and version/schema compatibility.

```python
from decimal import Decimal
import pytest


def test_order_total() -> None:
    line = OrderLine(sku="A-1", quantity=2, unit_price=Decimal("3.25"))
    order = Order(order_id="O-1", lines=(line,))
    assert order.total == Decimal("6.50")


def test_order_rejects_empty_lines() -> None:
    with pytest.raises(ValueError, match="non-empty tuple"):
        Order(order_id="O-2", lines=())


def test_frozen_line_cannot_be_reassigned() -> None:
    line = OrderLine(sku="A-1", quantity=1, unit_price=Decimal("1.00"))
    with pytest.raises((AttributeError, TypeError)):
        line.quantity = 2  # type: ignore[misc]
```

For property-based testing, Hypothesis can generate quantities, prices, and strings to check invariants across many combinations. Keep strategies constrained to valid values where testing positive properties, and generate invalid values separately to test rejection. Property-based tests complement, rather than replace, targeted examples.

For example, `hypothesis.strategies.builds` can construct valid `LineItem` instances from generated arguments. This optional test requires Hypothesis to be installed; it is not part of the standard-library runtime examples above.

```python
from decimal import Decimal
from hypothesis import given, strategies as st

valid_skus = st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-", min_size=1)
valid_prices = st.decimals(
    min_value=Decimal("0.00"),
    max_value=Decimal("1000.00"),
    places=2,
    allow_nan=False,
    allow_infinity=False,
)

@given(st.builds(LineItem, sku=valid_skus, quantity=st.integers(min_value=1, max_value=1000), unit_price=valid_prices))
def test_generated_line_items_preserve_invariants(line: LineItem) -> None:
    assert line.sku == line.sku.strip()
    assert line.quantity > 0
    assert line.line_total >= Decimal("0.00")
```

## 15. Common mistakes and repairs

| Mistake | Why it fails | Better approach |
|---|---|---|
| Mutable default `items=[]` | Shared state or rejected dataclass declaration | `field(default_factory=list)` |
| Treating annotations as runtime validation | Annotations are not automatically enforced | Validate at boundaries or in explicit constructors/models. |
| `frozen=True` with mutable nested state | Only attribute rebinding is blocked | Prefer immutable containers or copy-and-wrap nested data. |
| `unsafe_hash=True` on mutable equality fields | Hash may change after insertion into a set/dict | Use immutable keys and explicit identity semantics. |
| `asdict()` as a public schema | Deep conversion and no guaranteed wire compatibility | Write explicit serializer and schema version. |
| Using float for money | Binary floating-point rounding surprises | Use `Decimal` or integer minor units with a policy. |
| Assuming `slots=True` is transparent | Can affect weakrefs, `__dict__`, descriptors, inheritance | Test framework/inheritance integration and benchmark. |
| Blind `replace()` for business transitions | Can bypass intent and change related fields inconsistently | Use named domain transition methods. |
| Pickle as a long-term public format | Version coupling and unsafe unpickling of untrusted data | Use versioned, documented serialization. |

## 16. Exercises with hints and solutions

### Exercise 1 — independent defaults

Create a dataclass `Job` with a name and a list of warnings. Prove two instances do not share warnings.

**Hint:** use `field(default_factory=list)`.

**Solution:**

```python
from dataclasses import dataclass, field

@dataclass
class Job:
    name: str
    warnings: list[str] = field(default_factory=list)

first = Job("extract")
second = Job("load")
first.warnings.append("retry")
assert second.warnings == []
```

### Exercise 2 — derived immutable value

Make a frozen, slotted `Rectangle` that rejects non-positive dimensions and derives `area`.

**Hint:** `field(init=False)` plus `object.__setattr__` inside `__post_init__`.

**Solution:**

```python
from dataclasses import dataclass, field

@dataclass(frozen=True, slots=True)
class Rectangle:
    width: float
    height: float
    area: float = field(init=False)

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("dimensions must be positive")
        object.__setattr__(self, "area", self.width * self.height)

assert Rectangle(3, 4).area == 12
```

### Exercise 3 — choose a boundary model

An HTTP endpoint accepts JSON, needs coercion/validation, and publishes OpenAPI-compatible schema. Which model is the best starting point?

**Hint:** distinguish untrusted boundary data from internal domain state.

**Solution:** Pydantic v2 is a strong starting point because it provides runtime validation and JSON Schema generation. Convert validated data to domain dataclasses if the domain benefits from a separate representation. This is a trade-off, not a universal mandate.

## 17. Integrated mini-project: order intake and domain conversion

Implement an order-intake boundary that accepts a mapping, validates it with Pydantic v2, converts it to the immutable `Order` model, and serializes it using the versioned wire format. Requirements:

1. Reject unknown input fields.
2. Require positive integer quantity and a decimal price string with at most two fractional digits.
3. Convert price to `Decimal` without passing through `float`.
4. Keep the domain model frozen and slotted.
5. Serialize `Decimal` as strings and include `schema_version`.
6. Test valid input, invalid quantity, and a wire round-trip.

### Reference solution

```python
from decimal import Decimal
from typing import Any, Mapping
from pydantic import BaseModel, ConfigDict, Field

class OrderLinePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sku: str = Field(min_length=1)
    quantity: int = Field(gt=0, strict=True)
    unit_price: str = Field(pattern=r"^\d+(?:\.\d{1,2})?$")

class OrderPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    order_id: str = Field(min_length=1)
    lines: list[OrderLinePayload] = Field(min_length=1)
    currency: str = "INR"


def parse_order(payload: Mapping[str, Any]) -> Order:
    validated = OrderPayload.model_validate(payload)
    lines = tuple(
        OrderLine(
            sku=line.sku,
            quantity=line.quantity,
            unit_price=Decimal(line.unit_price),
        )
        for line in validated.lines
    )
    return Order(order_id=validated.order_id, lines=lines, currency=validated.currency)


payload = {
    "order_id": "O-100",
    "lines": [{"sku": "SKU-1", "quantity": 2, "unit_price": "10.25"}],
}
parsed_order = parse_order(payload)
assert parsed_order.total == Decimal("20.50")
wire_data = order_to_wire(parsed_order, OrderStatus.PENDING)
assert wire_data["schema_version"] == 1
```

This solution assumes the `Order`, `OrderLine`, `OrderStatus`, and `order_to_wire` definitions from earlier sections are in the same module. A real project should place payload schemas, domain models, serialization, and tests in separate modules with explicit dependencies. Add policies for currency codes, duplicate SKUs, quantity limits, rounding, idempotency, and schema migration as required by the business.

## 18. Final review checklist

- [ ] Mutable defaults use `default_factory` when independent per-instance state is needed.
- [ ] Equality and hashing match domain identity and mutation rules.
- [ ] Frozen models do not expose mutable aliases unintentionally.
- [ ] `__post_init__` validates and derives only deterministic local state.
- [ ] Inheritance constructor ordering is tested.
- [ ] `slots`, weak references, descriptors, and framework integration are tested where used.
- [ ] Runtime validation happens at untrusted boundaries, not by assumption from annotations.
- [ ] Serialization has explicit conversions, versioning, and migration policy.
- [ ] Tests cover invalid inputs, equality, immutability, derived fields, and round-trips.
- [ ] Performance decisions are supported by representative measurements.
