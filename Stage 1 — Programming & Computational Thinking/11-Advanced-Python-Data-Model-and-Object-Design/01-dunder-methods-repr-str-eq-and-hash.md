# Lesson 01 — Dunder Methods: `__repr__`, `__str__`, `__eq__`, and `__hash__`

> **Stage:** Stage 1 — Programming & Computational Thinking  
> **Module:** 11 — Advanced Python Data Model and Object Design  
> **Target runtime:** Python 3.12+  
> **Level:** Beginner → Intermediate → Advanced  
> **Estimated time:** 4–6 hours, including implementation, tests, and exercises

## Learning outcomes

By the end of this lesson, you should be able to:

- Explain what special (dunder) methods are and how Python's data model invokes them.
- Design useful, safe developer-facing representations with `__repr__` and readable output with `__str__`.
- Implement value equality with `__eq__`, including correct behavior for unsupported operand types and subclasses.
- Explain and enforce Python's equality/hash contract; choose when a class should be hashable.
- Recognize why mutable hash keys are dangerous and why `hash()` is not a persistent identifier.
- Use `__bool__`, `__len__`, and `__format__` appropriately, as scoped by the module roadmap.
- Test these behaviors with `pytest` and diagnose common production failures.

## 1. Prerequisites and mental model

You should already understand classes, instances, attributes, `__init__`, basic inheritance, mutability, tuples, dictionaries, sets, type hints, and assertions. If any of those are unfamiliar, review the earlier Stage 1 lessons on Python core types, OOP, and testing first.

### What is a dunder method?

A **dunder** method has a double underscore at the beginning and end of its name, such as `__repr__`. It is part of Python's data model: Python calls it to give an object a standard language behavior.

```python
items = [10, 20, 30]
len(items)       # Python dispatches to the object's length protocol
repr(items)      # developer-oriented representation
str(items)       # readable string form
```

Prefer the public operation (`len(value)`, `repr(value)`, `value == other`) instead of manually calling `value.__len__()` or `value.__eq__(other)`. Special-method lookup often happens on the type rather than through ordinary instance attribute lookup, so direct calls are not a reliable substitute for using the language operation.

### Why data engineers should care

Custom classes frequently represent money, source records, pipeline configuration, schema fields, event identities, database entities, and validation results. Their representations appear in logs and test failures; equality affects deduplication and assertions; hashing affects dictionaries and sets. A broken equality/hash design can make records disappear from a set or become effectively unreachable in a dictionary.

## 2. The four core methods at a glance

| Method | Main question | Common caller | Design goal |
|---|---|---|---|
| `__repr__(self)` | “What object is this?” | `repr(x)`, REPL, containers, debugging | Useful, unambiguous developer representation |
| `__str__(self)` | “How should this read to a person?” | `str(x)`, `print(x)`, `f"{x}"` | Readable display |
| `__eq__(self, other)` | “Do these values represent the same thing?” | `x == y`, membership operations in some contexts | Consistent value equality |
| `__hash__(self)` | “Which hash bucket should this value use?” | `hash(x)`, sets, dictionary keys | Stable hash compatible with equality |

They serve different purposes. A representation is not a serialization format, equality is not identity, and a hash is not a unique ID.

## 3. Beginner level — `__repr__` and `__str__`

### 3.1 `__repr__`: developer-facing representation

`repr(x)` asks Python for a representation intended primarily for debugging and development. A good representation helps someone identify the object's meaningful state without inspecting it manually.

For simple value objects, aim for a representation that looks like a constructor call and could recreate the object when practical. This is a useful goal, not a universal guarantee: some objects depend on external resources, secrets, or state that cannot safely or accurately be reconstructed.

```python
class Money:
    """Money stored as integer minor units, such as cents."""

    def __init__(self, amount_minor: int, currency: str) -> None:
        self.amount_minor = amount_minor
        self.currency = currency

    def __repr__(self) -> str:
        return f"Money({self.amount_minor!r}, {self.currency!r})"

money = Money(1250, "EUR")
assert repr(money) == "Money(1250, 'EUR')"
```

The `!r` conversion in the f-string applies `repr()` to each field. It preserves quotes around strings and helps distinguish values such as `None`, strings, and integers.

### 3.2 `__str__`: readable, user-facing display

`str(x)` is intended to be convenient for people reading the output. `print(x)` uses `str(x)`. When a class defines `__str__`, `f"{x}"` normally uses it too.

```python
class Money:
    def __init__(self, amount_minor: int, currency: str) -> None:
        self.amount_minor = amount_minor
        self.currency = currency

    def __repr__(self) -> str:
        return f"Money({self.amount_minor!r}, {self.currency!r})"

    def __str__(self) -> str:
        amount = self.amount_minor / 100
        return f"{amount:.2f} {self.currency}"

money = Money(1250, "EUR")
assert str(money) == "12.50 EUR"
assert repr(money) == "Money(1250, 'EUR')"
```

For financial software, integer minor units or `Decimal` are generally safer than binary floating-point for representing currency. The example's division is for display only and is not a recommendation to use floats for financial calculations.

### 3.3 What if only one method exists?

If `__str__` is not defined, `str(x)` falls back to `__repr__`. For that reason, when you only implement one representation method, implement a useful `__repr__` first.

```python
class Batch:
    def __init__(self, batch_id: str, row_count: int) -> None:
        self.batch_id = batch_id
        self.row_count = row_count

    def __repr__(self) -> str:
        return f"Batch(batch_id={self.batch_id!r}, row_count={self.row_count})"

batch = Batch("daily-2026-10-16", 1250)
assert str(batch) == repr(batch)
```

### 3.4 Containers usually show contained objects with `repr`

```python
money = Money(1250, "EUR")
print(money)       # 12.50 EUR
print([money])     # [Money(1250, 'EUR')]
```

A list uses the representation of its elements, rather than each element's user-facing `str`. This makes nested structures more useful when debugging.

### 3.5 Rules for a production-quality representation

A good `__repr__` should:

1. Return a `str` (not bytes, `None`, or an arbitrary object).
2. Include enough state to distinguish important instances.
3. Avoid performing I/O, database queries, network calls, or expensive computations.
4. Avoid exposing passwords, access tokens, connection strings, personally identifying data, or other secrets.
5. Remain bounded in size when fields may contain huge payloads.
6. Handle recursive object graphs safely when recursion is possible.

Do not make a representation the canonical wire format for an API, a database record, or a long-term archive. Use explicit serialization such as JSON with a defined schema instead.

#### Recursive representations

If objects can reference themselves, naïve representations can recurse indefinitely. Python's `reprlib.recursive_repr` can protect a representation method.

```python
from reprlib import recursive_repr

class Node:
    def __init__(self, name: str) -> None:
        self.name = name
        self.parent: Node | None = None

    @recursive_repr(fillvalue="...")
    def __repr__(self) -> str:
        return f"Node(name={self.name!r}, parent={self.parent!r})"

root = Node("root")
root.parent = root
assert "..." in repr(root)
```

### 3.6 Round-tripping a representation: useful, but conditional

For simple objects whose constructor arguments fully describe their state, `repr()` can be designed to be evaluable in a context where the class name is available. Never call `eval()` on an untrusted string: evaluating untrusted Python expressions can execute arbitrary code.

```python
class Point:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"Point({self.x!r}, {self.y!r})"

original = Point(3, 4)
namespace = {"Point": Point}
rebuilt = eval(repr(original), {"__builtins__": {}}, namespace)
assert (rebuilt.x, rebuilt.y) == (original.x, original.y)
```

This tightly controlled demonstration is for learning only. In real applications, prefer an explicit safe parser or serializer. Do not use `eval()` as a general-purpose deserialization mechanism.

## 4. Beginner level — equality and identity

### 4.1 `==` is not the same as `is`

- `a == b` asks whether two objects are equal according to their equality behavior.
- `a is b` asks whether both names refer to the very same object.

```python
left = [1, 2]
right = [1, 2]
assert left == right
assert left is not right
```

A user-defined class that does not implement `__eq__` normally inherits identity-based equality from `object`. Two separately created instances with identical attributes are therefore not automatically equal.

### 4.2 Define value equality with `__eq__`

For a value object, identify the fields that define its meaning and compare those fields. Avoid comparing incidental details such as cached values, log messages, or timestamps unless they are part of the value's identity by design.

```python
class Money:
    def __init__(self, amount_minor: int, currency: str) -> None:
        self.amount_minor = amount_minor
        self.currency = currency

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return (self.amount_minor, self.currency) == (
            other.amount_minor,
            other.currency,
        )

one = Money(100, "USD")
another_one = Money(100, "USD")
different = Money(100, "EUR")
assert one == another_one
assert one != different
```

The return annotation is `bool` because supported comparisons return booleans. Returning the singleton `NotImplemented` for an unsupported type is also valid and tells Python to continue its comparison-dispatch process.

### 4.3 Why return `NotImplemented` instead of `False`?

`NotImplemented` is a special singleton recognized by Python's operator machinery. It does **not** mean “the answer is false.” It means “this method does not implement this comparison for this operand combination.” Python can then try the other operand's reflected comparison method and apply its fallback rules.

```python
class RecordId:
    def __init__(self, value: str) -> None:
        self.value = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RecordId):
            return NotImplemented
        return self.value == other.value

assert RecordId("r-1") == RecordId("r-1")
assert RecordId("r-1") != 42
```

For `==`, if both sides return `NotImplemented`, Python falls back to identity comparison. Thus `RecordId("r-1") == 42` evaluates to `False`; it does not raise merely because the types differ. Ordering comparisons can instead raise `TypeError` when no implementation supports the operands.

Do not use `NotImplementedError` here. `NotImplementedError` is an exception; `NotImplemented` is the special return value used for operator dispatch.

### 4.4 Equality design principles

A well-designed value equality relation should generally be:

- **Reflexive:** `x == x` is true for ordinary well-behaved values.
- **Symmetric:** if `x == y`, then `y == x`.
- **Transitive:** if `x == y` and `y == z`, then `x == z`.
- **Consistent:** repeated comparisons give the same result while relevant state remains unchanged.

These principles can be complicated by floating-point `NaN`, custom cross-type comparisons, mutable objects, and badly designed inheritance hierarchies. Decide what “same value” means before writing code.

## 5. Intermediate level — `__hash__` and the equality/hash contract

### 5.1 What is a hash?

`hash(x)` returns an integer hash value. Python uses hashes to organize hash-based collections such as `set` and `dict`, allowing efficient average-case lookup. Hashes can collide: different objects are allowed to have the same hash. Equality is still used to distinguish colliding keys.

A hash is **not**:

- a unique identifier;
- a cryptographic digest;
- a stable cross-process ID;
- a replacement for equality.

### 5.2 The non-negotiable contract

If two objects compare equal, they **must** have equal hashes:

\[
x == y \implies hash(x) == hash(y)
\]

The reverse implication is not required. Equal hashes do not prove that objects are equal.

A safe implementation for an immutable value object is to hash the same logical fields used by equality:

```python
class Money:
    __slots__ = ("amount_minor", "currency")

    def __init__(self, amount_minor: int, currency: str) -> None:
        self.amount_minor = amount_minor
        self.currency = currency

    def __repr__(self) -> str:
        return f"Money({self.amount_minor!r}, {self.currency!r})"

    def __str__(self) -> str:
        return f"{self.amount_minor / 100:.2f} {self.currency}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return (self.amount_minor, self.currency) == (
            other.amount_minor,
            other.currency,
        )

    def __hash__(self) -> int:
        return hash((self.amount_minor, self.currency))

first = Money(100, "USD")
second = Money(100, "USD")
assert first == second
assert hash(first) == hash(second)
assert len({first, second}) == 1
assert {first: "settled"}[second] == "settled"
```

The tuple is hashable because both fields are hashable. This implementation is safe only if the fields that participate in equality do not change while the object is used as a key. The class above does not enforce immutability; the later frozen-dataclass example demonstrates a stronger default for a simple value object.

### 5.3 Why defining `__eq__` can make a class unhashable

When a class defines `__eq__` but does not define `__hash__`, Python normally sets its `__hash__` to `None`. This is deliberate: value equality plus identity-based hashing would violate the contract, and Python cannot assume which fields should be hashed.

```python
class UnhashableMoney:
    def __init__(self, amount_minor: int) -> None:
        self.amount_minor = amount_minor

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UnhashableMoney):
            return NotImplemented
        return self.amount_minor == other.amount_minor

value = UnhashableMoney(100)
assert UnhashableMoney.__hash__ is None
# hash(value) raises TypeError: unhashable type: 'UnhashableMoney'
```

This is usually the correct default for mutable value objects. If the type should be hashable, explicitly design its equality and hash semantics. Assigning `__hash__ = object.__hash__` while defining value equality is almost always wrong because equal instances could have different identity hashes.

### 5.4 Mutable fields and dictionary/set corruption

A dictionary or set stores an object's hash when inserting it. If you later mutate a field that changes the object's hash, the object may remain in the bucket chosen by the old hash while future lookups compute a new hash. It can then appear to be missing, and removal can fail.

```python
class MutableKey:
    def __init__(self, key: int) -> None:
        self.key = key

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MutableKey):
            return NotImplemented
        return self.key == other.key

    def __hash__(self) -> int:
        return hash(self.key)

# Do not do this in production:
key = MutableKey(1)
# mapping = {key: "value"}
# key.key = 2  # changes the hash-relevant state after insertion
```

The lesson is not that Python's dictionary is broken; the key violated the hashability contract by changing its hash-relevant state. A hashable object's hash and equality behavior must remain stable while it is in a set or used as a dictionary key.

**Preferred options:**

- Use immutable value objects for keys.
- Use a stable immutable identifier as the key.
- If the object must be mutable, do not hash it; use an unhashable class or index it externally by a stable key.

### 5.5 What makes a good hash implementation?

- Hash the same logical components that equality compares.
- Use `hash((field_a, field_b, ...))` when the component values are hashable.
- Do not hash a mutable list directly; convert to a tuple only if the represented contents are themselves intended to be immutable for the key's lifetime.
- Do not hand-roll a complex hash unless there is a measured reason and a clear correctness argument.
- Do not store `hash(x)` in a database as a durable identifier.

### 5.6 Hash randomization and process boundaries

Python randomizes hashes for some built-in types, including strings, to help defend against collision-based denial-of-service attacks. Therefore, `hash("pipeline")` may differ between Python processes; `PYTHONHASHSEED` can control the seed for reproducibility or testing, but a fixed seed does not turn built-in hashes into a durable identifier. The exact integer returned by `hash()` is an implementation-level collection aid, not a persistence format.

For durable fingerprints, choose a deliberate canonical encoding and a stable digest such as `hashlib.sha256`, with clear decisions about normalization, field ordering, encoding, and versioning. A cryptographic digest has a different purpose and security profile from Python's built-in `hash()`.

## 6. `__bool__` and `__len__`: truthiness behavior

The roadmap includes truthiness because it is another data-model behavior that can surprise callers. In a Boolean context (`if value:`, `bool(value)`), Python checks `__bool__` first if it exists. If `__bool__` is absent, Python can use `__len__`; a zero length is false and a nonzero length is true. If neither is defined, instances are normally truthy.

```python
class QueueView:
    def __init__(self, items: list[str]) -> None:
        self.items = items

    def __len__(self) -> int:
        return len(self.items)

empty = QueueView([])
nonempty = QueueView(["job-1"])
assert bool(empty) is False
assert bool(nonempty) is True
```

If both are defined, `__bool__` takes precedence:

```python
class AlwaysReady:
    def __len__(self) -> int:
        return 0

    def __bool__(self) -> bool:
        return True

assert bool(AlwaysReady()) is True
```

`__bool__` must return an actual `bool`; returning an integer such as `1` is an error. `__len__` must return a non-negative integer. Do not give a collection a surprising truthiness meaning unless it is clearly documented. For example, “no records loaded” and “the operation failed” are different states and should not be conflated by an arbitrary Boolean conversion.

## 7. `__format__` and formatting specifications

`format(value, spec)` and f-strings with a format specifier such as `f"{value:>12}"` use the object's formatting protocol. If a class does not define `__format__`, the inherited behavior generally delegates an empty format spec to `str(value)` and rejects unsupported non-empty specs.

For a custom type, define a small, documented format mini-language only when it materially improves the API. Do not create an obscure formatting syntax just to avoid a normal method.

```python
class DataVolume:
    def __init__(self, bytes_count: int) -> None:
        if bytes_count < 0:
            raise ValueError("bytes_count must be non-negative")
        self.bytes_count = bytes_count

    def __repr__(self) -> str:
        return f"DataVolume({self.bytes_count})"

    def __str__(self) -> str:
        return f"{self.bytes_count} bytes"

    def __format__(self, spec: str) -> str:
        if spec == "bytes" or spec == "":
            return str(self)
        if spec == "kb":
            return f"{self.bytes_count / 1_000:.2f} kB"
        if spec == "kib":
            return f"{self.bytes_count / 1_024:.2f} KiB"
        raise ValueError(f"unsupported DataVolume format specifier: {spec!r}")

volume = DataVolume(2048)
assert format(volume) == "2048 bytes"
assert format(volume, "kib") == "2.00 KiB"
```

Here `kB` uses decimal units (1,000 bytes), while `KiB` uses binary units (1,024 bytes). The class intentionally rejects unknown specs so mistakes do not silently produce misleading output.

## 8. Advanced level — subclass equality and type policy

### 8.1 `isinstance` versus exact type checks

The roadmap asks you to understand the trade-off between `isinstance(self, SomeType)` and `type(self) is type(other)`.

- `isinstance(other, Base)` accepts instances of subclasses. This can be useful when subclasses preserve the same equality meaning.
- `type(other) is type(self)` only compares instances of the exact same runtime class. This avoids some cross-subclass asymmetry, but may make a base instance and a behaviorally compatible subclass unequal.

There is no universally correct choice. Equality should remain symmetric and transitive across the inheritance hierarchy. If a subclass adds state that changes the meaning of a value, inherited equality based only on base fields can be misleading.

```python
class EntityKey:
    def __init__(self, key: str) -> None:
        self.key = key

    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return NotImplemented
        return self.key == other.key

    def __hash__(self) -> int:
        return hash((type(self), self.key))

class CustomerKey(EntityKey):
    pass

assert EntityKey("42") == EntityKey("42")
assert EntityKey("42") != CustomerKey("42")
```

This policy deliberately treats the type as part of the value. If your domain instead treats a `CustomerKey` as interchangeable with an `EntityKey`, define and test that policy explicitly. Do not casually combine subclass-friendly equality with hashing that omits fields or type information when that would violate the equality/hash contract.

### 8.2 `NotImplemented` and subclass dispatch

For rich comparison operators, Python has a dispatch protocol: it tries the appropriate method, can give a strict subclass's reflected implementation priority in relevant cases, and can try the other operand's method when the first returns `NotImplemented`. The exact rules differ by operator category, so do not assume every operator follows an identical path.

For equality, the safe practical pattern for value types is to return `NotImplemented` when the other operand is outside the type domain you support. This leaves Python free to consult the other operand and apply the documented fallback. Returning `False` is appropriate when the comparison is supported and the values are simply unequal.

### 8.3 Floating-point `NaN`

IEEE floating-point `NaN` is not equal to itself:

```python
nan = float("nan")
assert nan != nan
```

This means naïve equality and deduplication policies involving `NaN` can surprise you. Do not rely on `x == x` as a universal test for “valid value.” Decide how missing or non-finite values should be handled in your domain: reject them, normalize them, or represent them explicitly. `NaN` behavior inside containers can have identity-related subtleties, so tests should assert the business rule you need rather than assume every container behaves like a simple repeated `==` expression.

### 8.4 Dataclasses: generated equality and hashing

For straightforward value objects, `dataclasses` can generate these methods. The defaults matter:

- `@dataclass` normally generates `__eq__` and does not make a mutable class hashable by default.
- `@dataclass(frozen=True)` with equality enabled normally generates a hash, assuming the selected fields are themselves hashable.
- `unsafe_hash=True` can force hash generation, but it is unsafe when equality-relevant state can mutate; avoid it unless you can justify the invariant.
- `field(compare=False)` excludes a field from generated equality and hash behavior associated with that equality policy.

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class ImmutableMoney:
    amount_minor: int
    currency: str
    source_note: str = field(default="", compare=False)

usd_a = ImmutableMoney(100, "USD", "imported from A")
usd_b = ImmutableMoney(100, "USD", "imported from B")
assert usd_a == usd_b
assert hash(usd_a) == hash(usd_b)
assert len({usd_a, usd_b}) == 1
```

Because `source_note` has `compare=False`, it does not distinguish values for equality. That is correct only if source provenance is intentionally not part of the value's identity. If provenance should distinguish records, remove `compare=False` or define the domain policy another way.

### 8.5 Repr safety and operational logging

Representations often end up in logs, error reports, monitoring systems, notebook outputs, and CI traces. Treat them as potentially exported data. Do not include raw credentials or sensitive payloads. A good representation can include a record ID, state, and a bounded summary while omitting secret or high-volume fields.

```python
class DatabaseConfig:
    def __init__(self, host: str, username: str, password: str) -> None:
        self.host = host
        self.username = username
        self.password = password

    def __repr__(self) -> str:
        return (
            f"DatabaseConfig(host={self.host!r}, "
            f"username={self.username!r}, password=<redacted>)"
        )

config = DatabaseConfig("db.internal", "pipeline_user", "do-not-log-this")
assert "do-not-log-this" not in repr(config)
assert "<redacted>" in repr(config)
```

In production, consider whether the username is also sensitive under your threat model. Redaction is not a substitute for controlling access to logs.

## 9. A complete production-oriented value object

The following example brings together the core ideas. It models an immutable identifier for a source record. It is deliberately small so that its invariants can be understood and tested.

```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class SourceRecordKey:
    source: str
    record_id: str

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ValueError("source must not be empty")
        if not self.record_id.strip():
            raise ValueError("record_id must not be empty")

key_a = SourceRecordKey("crm", "C-100")
key_b = SourceRecordKey("crm", "C-100")
key_c = SourceRecordKey("billing", "C-100")

assert key_a == key_b
assert hash(key_a) == hash(key_b)
assert key_a != key_c
assert len({key_a, key_b, key_c}) == 2
assert {key_a: "processed"}[key_b] == "processed"
```

The dataclass generates a useful representation, equality, and a hash because it is frozen and uses the default equality policy. `slots=True` is included as an example of a feature covered more deeply in the next lesson; it is not required for correct equality or hashing. `frozen=True` prevents ordinary field reassignment, though Python's frozen dataclasses are not a security boundary and do not recursively freeze mutable objects stored in fields. Here the fields are strings, so the key components themselves are immutable.

### When should a class be hashable?

Make a class hashable when it has a clear, stable value identity and can keep all equality/hash-relevant state stable during its lifetime as a key. Examples include immutable record keys, normalized schema identifiers, and immutable configuration value objects. Avoid hashability for mutable entities whose equality-relevant fields change over time.

## 10. Testing strategy with `pytest`

Tests should check behavior through public operations (`repr`, `str`, `==`, `hash`, set membership, dictionary lookup), not only call the dunder methods directly.

Save this as `test_value_objects.py` in a small project with the classes under test imported from your module. The test examples below assume the `Money` implementation in Section 5.2 is available as `Money`.

```python
import pytest


def test_money_representation_and_display() -> None:
    value = Money(1250, "EUR")
    assert repr(value) == "Money(1250, 'EUR')"
    assert str(value) == "12.50 EUR"


def test_money_value_equality() -> None:
    assert Money(100, "USD") == Money(100, "USD")
    assert Money(100, "USD") != Money(200, "USD")
    assert Money(100, "USD") != Money(100, "EUR")


def test_money_unsupported_type_is_safe() -> None:
    assert Money(100, "USD") != 100


def test_equal_money_values_have_equal_hashes() -> None:
    left = Money(100, "USD")
    right = Money(100, "USD")
    assert left == right
    assert hash(left) == hash(right)


def test_equal_money_values_deduplicate_in_set() -> None:
    assert len({Money(100, "USD"), Money(100, "USD")}) == 1


def test_equal_money_values_are_interchangeable_dict_keys() -> None:
    mapping = {Money(100, "USD"): "settled"}
    assert mapping[Money(100, "USD")] == "settled"


def test_repr_does_not_leak_password() -> None:
    config = DatabaseConfig("db.internal", "pipeline_user", "secret-value")
    assert "secret-value" not in repr(config)
```

Run the tests with:

```bash
python -m pytest -q
```

### Additional invariants worth testing

For any pair of supported values `a` and `b`:

- If `a == b`, assert `hash(a) == hash(b)` whenever the type is hashable.
- Check equality symmetry: `a == b` and `b == a` should agree.
- Check equality transitivity across representative values.
- Check that changing irrelevant metadata does not affect equality if that is the stated policy.
- Check that invalid values fail at construction with clear errors.
- Check that representations do not contain secrets and remain reasonably small.

Property-based testing can generate many value pairs and is especially useful for equality and hash invariants, but start with explicit unit tests that communicate the intended domain semantics.

## 11. Common mistakes and how to correct them

| Mistake | Why it is wrong | Better approach |
|---|---|---|
| Defining `__str__` but no useful `__repr__` | Debuggers and containers still need a developer representation | Implement `__repr__` first; add `__str__` when a distinct display helps |
| Returning a non-string from `__repr__` or `__str__` | Python expects a string and raises `TypeError` | Return a valid `str` on every path |
| Performing I/O inside `__repr__` | Logging can unexpectedly block or fail | Display already available state only |
| Logging secrets in `__repr__` | Logs often leave the process boundary | Redact secrets and bound output |
| Accessing `other.some_field` before checking the type | Can raise `AttributeError` during unrelated comparisons | Check the supported type and return `NotImplemented` if unsupported |
| Returning `False` for every foreign type | Prevents Python from trying the other operand's equality implementation | Return `NotImplemented` when this implementation does not support the pair |
| Defining `__eq__` but assuming the class remains hashable | Python normally sets `__hash__ = None` | Decide explicitly whether instances should be hashable |
| Hashing mutable fields | Mutating them can break dictionary/set lookup | Use immutable keys or leave mutable objects unhashable |
| Hashing a field not used by equality | Equal objects could have different hashes | Hash the same logical components as equality |
| Persisting `hash(x)` | Built-in hashes can vary between processes and are not unique | Use a stable ID or explicitly specified digest |
| Assuming `repr()` is a serialization format | It may omit state, expose secrets, or depend on code context | Use a versioned explicit serialization format |
| Assuming `NaN == NaN` | IEEE NaN compares unequal to itself | Define explicit policy for non-finite values |

## 12. Hands-on lab — deduplicating ingestion records

### Scenario

A data ingestion job receives repeated source events. You need a key that treats events from the same source with the same external ID as the same record. The key will be used in a `set` to deduplicate the batch and in a `dict` to attach processing status.

### Requirements

1. Create an immutable `EventKey` value object with `source` and `external_id` string fields.
2. Reject blank fields after trimming whitespace.
3. Give the object a useful representation that shows both fields.
4. Ensure equality compares both fields and does not claim equality with unrelated types.
5. Ensure equal keys have equal hashes.
6. Demonstrate set deduplication and dictionary lookup using a separately constructed but equal key.
7. Write `pytest` tests for the valid and invalid cases.
8. Explain why a mutable event payload should not be included in the hash if it changes during processing.

### Reference solution

```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class EventKey:
    source: str
    external_id: str

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ValueError("source must not be blank")
        if not self.external_id.strip():
            raise ValueError("external_id must not be blank")

keys = [
    EventKey("crm", "100"),
    EventKey("crm", "100"),
    EventKey("billing", "100"),
]
unique_keys = set(keys)
status_by_key = {keys[0]: "processed"}

assert len(unique_keys) == 2
assert status_by_key[EventKey("crm", "100")] == "processed"
assert "external_id='100'" in repr(keys[0])
```

### Lab test file

```python
import pytest


def test_event_key_equality_and_hash() -> None:
    first = EventKey("crm", "100")
    second = EventKey("crm", "100")
    assert first == second
    assert hash(first) == hash(second)
    assert len({first, second}) == 1


def test_event_key_source_is_part_of_identity() -> None:
    assert EventKey("crm", "100") != EventKey("billing", "100")


@pytest.mark.parametrize(
    ("source", "external_id"),
    [("", "100"), ("   ", "100"), ("crm", ""), ("crm", "   ")],
)
def test_event_key_rejects_blank_fields(source: str, external_id: str) -> None:
    with pytest.raises(ValueError):
        EventKey(source, external_id)
```

## 13. Practice questions

Try these before reading the answer key.

### Beginner

1. What is a dunder method, and why should you usually use `repr(x)` instead of calling `x.__repr__()` directly?
2. What is the difference between `str(x)` and `repr(x)`?
3. Why does `print([money])` generally show the element's `repr` rather than its `str`?
4. What is the difference between `==` and `is`?
5. If a class defines `__repr__` but not `__str__`, what does `str(instance)` do?

### Intermediate

6. Why should `__eq__` return `NotImplemented` for unsupported operand types?
7. State the equality/hash contract. Is the reverse implication required?
8. Why does defining `__eq__` without `__hash__` usually make instances unhashable?
9. Why is a mutable object with a hash based on mutable fields unsafe as a dictionary key?
10. If `__bool__` and `__len__` both exist, which controls truthiness?
11. Why should you not save Python's built-in `hash()` result as a durable ID?

### Advanced

12. What can go wrong if a base class uses `isinstance` equality while a subclass adds equality-relevant state?
13. When is `@dataclass(frozen=True)` a useful choice for a key object, and what does it not guarantee?
14. How should a `__repr__` handle credentials or very large payloads?
15. Why can `float("nan")` complicate equality-based deduplication?
16. Design a test that verifies the hash contract without asserting a particular hash integer.

## 14. Answer key

1. A dunder method is a Python data-model hook. Use the public operation because special-method dispatch is controlled by Python and may not match ordinary instance attribute lookup.
2. `str` aims for readable display; `repr` aims for useful developer inspection and ideally an unambiguous representation.
3. Built-in containers use `repr` for their elements so nested values remain diagnostically useful.
4. `==` checks equality semantics; `is` checks object identity.
5. `str(instance)` falls back to `__repr__`.
6. It tells Python this implementation does not support the operand pair, allowing the other operand's comparison method and Python's fallback behavior to run.
7. If `a == b`, then `hash(a) == hash(b)`. Equal hashes do not imply equality.
8. Python cannot infer which fields define value equality or a stable hash; defaulting to unhashable prevents a common contract violation.
9. The hash can change after insertion, while the collection placed the key using its previous hash, so later lookup/removal may fail.
10. `__bool__` takes precedence. If it is absent, Python can use `__len__`; zero means false.
11. Hashes for types such as strings are randomized across processes and are not unique or designed for persistence.
12. A base instance and subclass instance might compare equal based on base fields while the subclass's extra state makes the values semantically different, potentially breaking symmetry or transitivity if the two classes implement equality differently. Define a consistent type policy and test it.
13. It is useful when the key is a value object whose equality-relevant fields should not be reassigned. It does not recursively freeze arbitrary mutable fields and is not a security boundary.
14. Redact secrets, avoid I/O, summarize or truncate large fields, and ensure representation code is robust enough for logs and debuggers.
15. NaN is unequal to itself, so ordinary equality may not identify repeated NaN values as duplicates. Define an explicit domain policy for non-finite values.
16. For two equal instances, assert both `a == b` and `hash(a) == hash(b)`; never assert a specific numeric hash value.

## 15. Readiness checklist

You are ready to continue to Lesson 02 when you can do all of the following without copying an example:

- [ ] Explain `repr` versus `str` and implement both for a small value object.
- [ ] Write a safe `__eq__` that returns `NotImplemented` for unsupported types.
- [ ] Explain why equal values must have equal hashes, while equal hashes need not mean equal values.
- [ ] Explain why mutable hash keys are unsafe and why Python's `hash()` is not a persistent ID.
- [ ] Describe `__bool__`/`__len__` precedence and implement a small `__format__` protocol.
- [ ] Test equality, hash invariants, set deduplication, dictionary lookup, validation, and representation safety.
- [ ] Complete the EventKey lab and explain every design choice.

## 16. Further reading

Use the official Python documentation as the source of truth for exact runtime behavior:

- [Python data model — special method names](https://docs.python.org/3/reference/datamodel.html#special-method-names)
- [Python built-in functions — `repr`, `str`, `hash`, `format`, and `bool`](https://docs.python.org/3/library/functions.html)
- [Python glossary — hashable](https://docs.python.org/3/glossary.html#term-hashable)
- [Dataclasses documentation](https://docs.python.org/3/library/dataclasses.html)
- [The `reprlib` module](https://docs.python.org/3/library/reprlib.html)
- [The `pytest` documentation](https://docs.pytest.org/)

---

**Lesson summary:** `__repr__` supports debugging, `__str__` supports readable display, `__eq__` defines value equality, and `__hash__` enables hash-based collections when equality and state stability make that safe. Treat these methods as public contracts: define the semantics first, implement the methods consistently, and prove the behavior with tests.
