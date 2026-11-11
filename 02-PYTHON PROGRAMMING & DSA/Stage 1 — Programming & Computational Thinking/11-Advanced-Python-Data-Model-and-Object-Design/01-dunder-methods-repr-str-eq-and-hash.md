# Dunder Methods: `__repr__`, `__str__`, `__eq__`, and `__hash__`

> **Stage:** 1 — Programming & Computational Thinking  
> **Module:** 11 — Advanced Python Data Model and Object Design  
> **Lesson:** 01  
> **Target runtime:** Python 3.12+  
> **Level:** Beginner → intermediate → advanced  
> **Scope:** Python special methods for representation, equality, hashability, truth-value testing, and formatting.

## 1. Scope, prerequisites, and learning objectives

This lesson follows Lesson 01 of `roadmap-Advanced-Python-Data-Model-and-Object-Design.md`. It is the first lesson in Phase A, *Making Objects Behave*. Later lessons cover rich ordering, container protocols, and operator overloading; this lesson introduces the data-model mechanisms needed to reason about those topics.

### Prerequisites

You should be comfortable with:

- Defining classes, creating instances, and using `self`.
- Instance attributes, inheritance, and `isinstance`.
- `None`, booleans, conditionals, tuples, and exceptions.
- Lists, tuples, sets, and dictionaries.
- Basic type annotations and running Python files.
- Basic pytest assertions.

If any prerequisite is unfamiliar, pause and review it before trying the advanced exercises.

### Learning objectives

By the end, you should be able to:

1. Explain how Python's data model connects language operations to special methods.
2. Design useful `repr()` and `str()` output, including output inside containers.
3. Implement equality without unsafe assumptions about the other operand's type.
4. Explain and preserve the equality/hash contract.
5. Decide whether a class should be hashable and keep hashes stable while objects are dictionary keys or set members.
6. Implement truth-value and formatting behavior deliberately.
7. Reason about `NotImplemented`, subclass equality, exact-type checks, `NaN`, hash randomization, and dataclasses.
8. Test these contracts with pytest and identify common production failure modes.

---

## 2. The mental model: Python's data model

Python objects are not just bundles of attributes. A class can participate in language operations by defining **special methods**, often called **dunder methods** because their names begin and end with double underscores.

Examples:

| Operation you write | Special-method mechanism |
|---|---|
| `repr(obj)` | `type(obj).__repr__(obj)` |
| `str(obj)` / `print(obj)` | `__str__`, with a fallback to `__repr__` |
| `a == b` | equality dispatch involving `__eq__` |
| `hash(obj)` | `type(obj).__hash__(obj)` |
| `if obj:` | `__bool__`, or `__len__` if no `__bool__` exists |
| `format(obj, spec)` / `f"{obj:spec}"` | `__format__` (including the empty spec in `f"{obj}"`) |
| `len(obj)` | `__len__` |

These are conceptual descriptions of Python's special-method dispatch, not a promise that every operation is implemented as a literal Python-level method call. In CPython, many operations use interpreter-level slots. One important practical rule is that special-method lookup generally happens on the object's **type**, not by looking for an ordinary same-named attribute on the instance.

```python
class Box:
    def __init__(self, value: int) -> None:
        self.value = value

    def __len__(self) -> int:
        return self.value

box = Box(3)
print(len(box))
# 3
```

Python's built-in `len(box)` invokes the length protocol. You almost never need to write `box.__len__()` yourself. Prefer `len(box)`: it expresses intent and uses the language protocol correctly.

### Why this matters in engineering

Libraries become composable when their objects follow familiar protocols. A data model that has reliable representations is easier to debug; a value object with correct equality behaves predictably in tests and deduplication; a hashable immutable key can be used in dictionaries and sets. The same principles apply to configuration objects, data-quality results, feature descriptors, cache keys, and model metadata.

---

## 3. Core terminology

- **Identity:** whether two references point to the same object; test with `is`.
- **Equality:** whether two objects should count as equivalent according to `==`.
- **Value object:** an object whose meaning is primarily its values, rather than its identity. Two separate `Money(500, "USD")` instances may represent the same amount.
- **Hash:** an integer returned by `hash(obj)`, used by hash tables to narrow down candidate matches.
- **Hashable:** an object whose hash remains stable during its lifetime and whose equality behavior meets Python's requirements. In practice, hashable objects can be dictionary keys and set members.
- **Mutable:** an object's observable state can change after construction.
- **Immutable:** the object's equality-relevant state cannot be changed after construction.
- **Contract:** a rule that an implementation must preserve for callers and built-in data structures to behave correctly.
- **Fallback:** behavior Python uses when a preferred protocol method is absent.
- **`NotImplemented`:** a special singleton value that tells binary-operation dispatch that this implementation does not handle the operand combination. It is not an exception and is not the same as `False`.

---

## 4. `__repr__` and `__str__`: two audiences, two jobs

### 4.1 `__repr__`: developer-facing representation

`repr(obj)` should produce a useful, unambiguous representation that helps a developer inspect the object. When practical, it should resemble a valid constructor expression that could recreate an equivalent object in the current namespace.

```python
class Point:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"Point(x={self.x!r}, y={self.y!r})"

point = Point(2, 5)
print(repr(point))
# Point(x=2, y=5)
```

Use `!r` or `repr()` for fields inside `__repr__`. That preserves useful quoting for strings and recursively uses the field's representation.

A constructor-like representation is a goal, not an unconditional requirement. It may be impractical when an object contains secrets, huge data, open file handles, external resources, or state that cannot be reconstructed. Never expose passwords, API tokens, personal data, or confidential payloads merely to make a representation detailed.

### 4.2 `__str__`: user-facing representation

`str(obj)` should be readable and suitable for user-facing output; `print(obj)` uses string conversion. An f-string always goes through `__format__` with the supplied format specifier (the empty string for `f"{obj}"`). The default `object.__format__` delegates an empty spec to `str(obj)`, but a custom `__format__` can choose different behavior.

```python
class Temperature:
    def __init__(self, celsius: float) -> None:
        self.celsius = celsius

    def __repr__(self) -> str:
        return f"Temperature(celsius={self.celsius!r})"

    def __str__(self) -> str:
        return f"{self.celsius:.1f} °C"

temperature = Temperature(21.25)
print(repr(temperature))
print(str(temperature))
print(f"Current temperature: {temperature}")
```

Expected output:

```text
Temperature(celsius=21.25)
21.2 °C
Current temperature: 21.2 °C
```

The `.1f` formatting rounds the value to one decimal place. The underlying value remains `21.25`.

### 4.3 Fallback and container behavior

If a class defines `__repr__` but not `__str__`, `str(obj)` falls back to `__repr__`. Therefore, if you implement only one representation method, implement `__repr__`.

Containers normally display their elements using `repr()`, not `str()`:

```python
class Label:
    def __repr__(self) -> str:
        return "Label(code='A7')"

    def __str__(self) -> str:
        return "A7"

label = Label()
print(label)
print([label])
print({"label": label})
```

Expected output:

```text
A7
[Label(code='A7')]
{'label': Label(code='A7')}
```

This is intentional: the container's representation should help identify the contained objects.

### 4.4 Representation safety and recursive objects

A `__repr__` should be dependable during debugging and logging. It should not normally perform network I/O, mutate the object, or raise an exception. Avoid printing entire multi-gigabyte arrays or full records in every log line.

For bounded representations, use `reprlib`:

```python
import reprlib

large = list(range(100))
print(reprlib.repr(large))
```

The exact abbreviated output can depend on `reprlib`'s configured limits, but it will abbreviate the large list rather than print every element.

For recursive structures, `reprlib.recursive_repr` prevents infinite recursion:

```python
from reprlib import recursive_repr

class Node:
    def __init__(self, name: str) -> None:
        self.name = name
        self.child: Node | None = None

    @recursive_repr()
    def __repr__(self) -> str:
        return f"Node(name={self.name!r}, child={self.child!r})"

root = Node("root")
root.child = root
print(root)
# Node(name='root', child=...)
```

The decorator uses a recursion sentinel (`...`) when the same object's representation is encountered recursively.

### 4.5 `repr()` is not serialization

A representation that looks evaluable can be convenient for local debugging:

```python
class Coordinate:
    def __init__(self, x: int, y: int) -> None:
        self.x, self.y = x, y

    def __repr__(self) -> str:
        return f"Coordinate({self.x!r}, {self.y!r})"

original = Coordinate(4, 9)
namespace = {"Coordinate": Coordinate}
restored = eval(repr(original), {"__builtins__": {}}, namespace)
assert (restored.x, restored.y) == (4, 9)
```

Expected output: no output; the assertion passes.

This example is only for a controlled demonstration. `eval()` executes expressions. Restricting built-ins is not a general security boundary, and a representation may contain names or expressions that cannot be resolved. **Never evaluate arbitrary representations from logs, users, external systems, or untrusted files.** Use an explicit serialization format such as JSON with validation, or a deliberately designed schema, when data must cross process or trust boundaries.

---

## 5. `__eq__`: value equality, identity, and type handling

### 5.1 Identity is not equality

By default, ordinary user-defined objects inherit identity-based equality from `object`: two distinct instances compare unequal unless the class defines otherwise.

```python
class Empty:
    pass

a = Empty()
b = Empty()
c = a

print(a == b)
print(a is b)
print(a == c)
print(a is c)
```

Expected output:

```text
False
False
True
True
```

`is` asks whether references identify the same object. `==` asks the objects' equality protocol. Built-in types and value-object classes often define value equality.

### 5.2 A safe equality method

A robust `__eq__` should handle unsupported operand types without blindly reading attributes that may not exist.

```python
from types import NotImplementedType
class Pixel:
    def __init__(self, red: int, green: int, blue: int) -> None:
        self.red, self.green, self.blue = red, green, blue

    def __eq__(self, other: object) -> bool | NotImplementedType:
        if not isinstance(other, Pixel):
            return NotImplemented
        return (self.red, self.green, self.blue) == (
            other.red, other.green, other.blue
        )

print(Pixel(1, 2, 3) == Pixel(1, 2, 3))
print(Pixel(1, 2, 3) == (1, 2, 3))
```

Expected output:

```text
True
False
```

Because these methods can return either a boolean or the `NotImplemented` singleton, the examples below use the explicit Python 3.12+ annotation `bool | NotImplementedType` and import `NotImplementedType` from `types`. Some codebases keep `-> bool` as a conventional shorthand for `__eq__`, but strict static checking may flag `return NotImplemented`; prefer the union annotation when your type checker supports it. `NotImplemented` remains a runtime singleton value, not a boolean result.

### 5.3 Why `NotImplemented` is not `False`

When an equality implementation returns `NotImplemented`, it declines to decide the comparison. Python can try the other operand's equality implementation. If the right operand's type is a proper subclass of the left operand's type and supplies an override, that subclass implementation can receive priority. Otherwise, Python tries the left operand and then the right operand as applicable. If neither side handles equality, it ultimately falls back to identity behavior; inequality follows corresponding fallback behavior.

Returning `False` means “I handled this comparison and the values are not equal.” That can prematurely reject an operand pair that the other object's implementation knows how to compare.

`NotImplemented` is a special return value, **not** an exception. Do not write `raise NotImplemented`; do not confuse it with `NotImplementedError`, which is an exception sometimes used in abstract or unfinished methods.

### 5.4 `isinstance` versus exact-type equality

Two common policies are:

```python
from types import NotImplementedType
class Money:
    def __init__(self, minor_units: int, currency: str) -> None:
        self.minor_units = minor_units
        self.currency = currency

    def __eq__(self, other: object) -> bool | NotImplementedType:
        if not isinstance(other, Money):
            return NotImplemented
        return (self.minor_units, self.currency) == (
            other.minor_units, other.currency
        )

print(Money(100, "USD") == 100)
# False, with no AttributeError
```

and:

```python
from types import NotImplementedType
class BasePoint:
    def __init__(self, x: int, y: int) -> None:
        self.x, self.y = x, y

    def __eq__(self, other: object) -> bool | NotImplementedType:
        if type(other) is not type(self):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

class ColoredPoint(BasePoint):
    def __init__(self, x: int, y: int, color: str) -> None:
        super().__init__(x, y)
        self.color = color

print(BasePoint(1, 2) == ColoredPoint(1, 2, "red"))
# False: exact-type policy declines the comparison
```

They encode different design choices:

- `isinstance` allows subclass instances to participate in the base class's equality logic.
- Exact-type checks restrict equality to instances of the same concrete class.

Neither policy is universally correct. The danger is allowing subclasses to add equality-relevant state while the base class ignores it. For example, if `BasePoint(x, y)` compares equal to `ColoredPoint(x, y, color)` by ignoring `color`, the classes may disagree about equality or produce surprising transitivity results. If subclasses add semantic state, define a deliberate equality policy; exact-type checks are often a safe default for independent value-object types.

For a class intended to be extended polymorphically, `isinstance` may be appropriate if all participating subclasses preserve the same equality semantics. Follow the Liskov substitution principle: subtype behavior should remain consistent with the promises callers rely on.

### 5.5 Equality laws

A well-designed value equality relation should normally satisfy:

- **Reflexivity:** `a == a` is true.
- **Symmetry:** if `a == b`, then `b == a`.
- **Transitivity:** if `a == b` and `b == c`, then `a == c`.
- **Consistency:** repeated comparisons return the same result while relevant state is unchanged.
- **Compatibility with hashing:** equal objects have equal hashes.

Floating-point `NaN` is a notable exception to ordinary reflexivity: `nan != nan`. This is a property of floating-point semantics, not a model to imitate casually in domain objects.

---

## 6. `__hash__`: hashability and the equality/hash contract

### 6.1 What a hash does

A hash table such as `dict` or `set` uses a hash to find a likely storage location, then uses equality to distinguish keys that share a hash. A hash is not a unique identifier: collisions are permitted.

The central contract is:

> If `a == b` is true, then `hash(a) == hash(b)` must be true.

The reverse is not required. Two unequal objects can have the same hash.

### 6.2 Why defining `__eq__` usually makes a class unhashable

When a class defines `__eq__` but does not explicitly define `__hash__`, Python sets `__hash__ = None` for that class. This conservative default prevents instances from accidentally remaining hashable when value equality is introduced but no compatible hash policy is supplied.

```python
from types import NotImplementedType
class Record:
    def __init__(self, key: str) -> None:
        self.key = key

    def __eq__(self, other: object) -> bool | NotImplementedType:
        if not isinstance(other, Record):
            return NotImplemented
        return self.key == other.key

record = Record("r-17")
print(Record.__hash__)
print(Record.__eq__(record, record))
# hash(record)  # TypeError: unhashable type: 'Record'
```

Expected output (the exact function representation is implementation-dependent):

```text
None
True
```

Uncommenting `hash(record)` raises `TypeError`.

### 6.3 Implementing a compatible hash

If a class is intended to be hashable, hash the same immutable values that determine equality:

```python
from dataclasses import dataclass
from types import NotImplementedType

@dataclass(frozen=True, eq=False)
class Tag:
    namespace: str
    name: str

    def __eq__(self, other: object) -> bool | NotImplementedType:
        if not isinstance(other, Tag):
            return NotImplemented
        return (self.namespace, self.name) == (other.namespace, other.name)

    def __hash__(self) -> int:
        return hash((self.namespace, self.name))

a = Tag("event", "created")
b = Tag("event", "created")
print(a == b)
print(hash(a) == hash(b))
print(len({a, b}))
```

Expected output:

```text
True
True
1
```

The example uses `@dataclass(frozen=True, eq=False)` to prevent ordinary reassignment while keeping the hand-written equality and hash methods. The tuple is hashable because both components are hashable strings. If any equality-relevant component is unhashable, such as a list, the tuple hash will fail. Frozen dataclasses are not deeply immutable if a field itself refers to mutable state, so choose immutable field types.

### 6.4 Mutable state and hash stability

A hash must remain stable while an object is stored as a dictionary key or set member. This is unsafe:

```python
from types import NotImplementedType
# INTENTIONALLY INCORRECT — do not use in production.
class MutableKey:
    def __init__(self, code: str) -> None:
        self.code = code

    def __eq__(self, other: object) -> bool | NotImplementedType:
        if not isinstance(other, MutableKey):
            return NotImplemented
        return self.code == other.code

    def __hash__(self) -> int:
        return hash(self.code)
```

If `code` changes after insertion, the object's hash may change. The table placed the object based on its old hash, so lookups and membership tests can fail unexpectedly. This can look like silent data loss.

Safer options:

1. Make equality-relevant state immutable.
2. Make the class unhashable (`__hash__ = None`) if its state is mutable.
3. Use an immutable key derived from the object, such as a tuple of stable fields.
4. Keep mutable operational state separate from immutable identity/value fields.

Do not “fix” this by hashing only a mutable object's identity if equality is value-based. Equal objects must still have equal hashes.

### 6.5 Hash randomization: never persist `hash()` values

Python salts hashes for types such as strings and bytes to mitigate certain denial-of-service attacks. As a result, hash values can differ between interpreter processes. The exact hash algorithm and values are not a persistent data format.

Do not use `hash(value)` as:

- A database primary key.
- A cross-process cache key.
- A durable event identifier.
- A checksum or cryptographic digest.
- A stable partition key across independent runs.

For stable identifiers, choose an explicit canonical representation and a suitable digest such as `hashlib.sha256`, or use a UUID/identifier strategy appropriate to the application. Canonicalization matters: equivalent data must be encoded identically before hashing. A cryptographic digest has different goals and properties from Python's in-memory `hash()`.

---

## 7. Truth-value testing: `__bool__` and `__len__`

Python decides whether an object is true in a boolean context such as `if obj`, `while obj`, `bool(obj)`, and boolean operators.

The precedence is:

1. If `__bool__` exists, use it. It must return `True` or `False`.
2. Otherwise, if `__len__` exists, zero means false and nonzero means true.
3. Otherwise, the object is true by default.

```python
class Batch:
    def __init__(self, items: list[int]) -> None:
        self.items = items

    def __len__(self) -> int:
        return len(self.items)

class ExplicitBatch(Batch):
    def __bool__(self) -> bool:
        return True  # Example only: even an empty batch is considered active.

print(bool(Batch([])))
print(bool(Batch([1])))
print(bool(ExplicitBatch([])))
```

Expected output:

```text
False
True
True
```

The third result proves that `__bool__` takes precedence over `__len__`. In production, an always-true `__bool__` should only be used if it reflects meaningful domain semantics. Avoid making an object false merely because an identifier or numeric field happens to be zero unless that is the intended contract.

`__len__` should return a non-negative integer. A negative length or an invalid return type causes errors when Python evaluates the protocol.

---

## 8. `__format__`: explicit formatting behavior

`format(value, spec)` and `f"{value:spec}"` call `value.__format__(spec)`. `object.__format__` supports an empty format specification by delegating to string conversion, but a non-empty unsupported specification normally raises `TypeError`. Built-in numbers implement rich format specifications such as alignment, width, precision, and type.

A domain object can define a small, documented format mini-language:

```python
class DataSize:
    def __init__(self, bytes_count: int) -> None:
        if bytes_count < 0:
            raise ValueError("bytes_count must be non-negative")
        self.bytes_count = bytes_count

    def __repr__(self) -> str:
        return f"DataSize({self.bytes_count})"

    def __str__(self) -> str:
        return f"{self.bytes_count} bytes"

    def __format__(self, spec: str) -> str:
        if spec == "" or spec == "human":
            return str(self)
        if spec == "commas":
            return f"{self.bytes_count:,} bytes"
        if spec == "KiB":
            return f"{self.bytes_count / 1024:.2f} KiB"
        raise ValueError(f"unsupported DataSize format specifier: {spec!r}")

size = DataSize(4096)
print(f"{size}")
print(f"{size:commas}")
print(f"{size:KiB}")
```

Expected output:

```text
4096 bytes
4,096 bytes
4.00 KiB
```

A custom mini-language should be small, predictable, and documented. This example raises `ValueError` for an unsupported custom spec; `TypeError` is also common for unsupported format operations, especially when relying on default behavior. The important design requirement is to fail clearly rather than silently misformat data.

---

## 9. Floating-point `NaN`: equality and set behavior

IEEE 754 `NaN` (“not a number”) compares unequal to itself:

```python
nan = float("nan")
print(nan == nan)
print(nan != nan)
```

Expected output:

```text
False
True
```

This has subtle implications for equality and hash collections. In Python, container membership can use identity shortcuts in addition to equality checks. Thus, the same `nan` object can be found in a set that contains it, while a separately created `NaN` value may not compare equal to it. Do not assume that `NaN` behaves like an ordinary reflexive value.

```python
nan1 = float("nan")
nan2 = float("nan")
values = {nan1}
print(nan1 in values)
print(nan2 in values)
```

Expected output on CPython 3.12+ (the exact hash-table details are implementation-dependent):

```text
True
False
```

The first succeeds because the set contains that same object; the second normally fails because the distinct NaN does not compare equal and has a different hash in CPython. Do not use this example as a cross-implementation guarantee about distinct NaN hashes. This is a useful illustration of why identity, equality, and container implementation details must not be conflated.

For data pipelines, explicitly define how missing or invalid numeric values should be treated. If domain equality needs a “missing equals missing” rule, represent missingness explicitly or normalize values before comparison rather than casually overriding global floating-point semantics.

---

## 10. Dataclasses: `eq=True` and `frozen=True`

Dataclasses generate common methods from declared fields. With `@dataclass(eq=True)` (the default), Python generates equality that compares participating fields as tuples, and the instances must have the same concrete type for the generated comparison to return true. With `frozen=True`, assignment to fields is blocked through normal attribute assignment and, when `eq=True` and `frozen=True`, dataclasses normally generate a hash based on the equality fields.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ModelVersion:
    name: str
    major: int
    minor: int

v1 = ModelVersion("encoder", 2, 1)
v2 = ModelVersion("encoder", 2, 1)
print(v1)
print(v1 == v2)
print(hash(v1) == hash(v2))
print(len({v1, v2}))
```

Expected output:

```text
ModelVersion(name='encoder', major=2, minor=1)
True
True
1
```

Important qualifications:

- `frozen=True` emulates immutability; it is not deep immutability. A frozen dataclass containing a mutable list still contains a mutable list.
- If a participating field is unhashable, the generated hash can fail when called.
- `eq=False` disables generated equality.
- A mutable dataclass with generated equality is normally unhashable by default.
- `unsafe_hash=True` asks dataclasses to generate a hash despite the usual safety default; it does not make mutable state safe.
- `field(compare=False)` excludes a field from generated equality and hash participation where applicable. Make sure that matches the domain's semantics.

Use frozen dataclasses for small, value-oriented objects when their equality and hashing behavior matches the domain. Do not rely on decorators without understanding which fields participate.

---

## 11. A cohesive value-object example: immutable `Money`

This example uses integer minor units (for example, cents) to avoid binary floating-point rounding in monetary equality. It intentionally treats currency as part of identity: `Money(100, "USD")` is not equal to `Money(100, "EUR")`.

```python
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True, slots=True)
class Money:
    """A monetary value represented by integer minor units and a currency code."""
    minor_units: int
    currency: str

    def __post_init__(self) -> None:
        if isinstance(self.minor_units, bool) or not isinstance(self.minor_units, int):
            raise TypeError("minor_units must be an int, not bool or another type")
        if len(self.currency) != 3 or not self.currency.isalpha():
            raise ValueError("currency must be a three-letter code")
        object.__setattr__(self, "currency", self.currency.upper())

    def __str__(self) -> str:
        # Assumes a two-decimal minor-unit convention for this teaching example.
        amount = Decimal(self.minor_units) / Decimal(100)
        return f"{amount:.2f} {self.currency}"

    def __format__(self, spec: str) -> str:
        if spec == "" or spec == "display":
            return str(self)
        if spec == "code":
            return f"{self.currency} {self.minor_units}"
        raise ValueError(f"unsupported Money format specifier: {spec!r}")

money = Money(1250, "eur")
same_money = Money(1250, "EUR")
different_currency = Money(1250, "USD")

print(repr(money))
print(str(money))
print(money == same_money)
print(money == different_currency)
print(len({money, same_money, different_currency}))
print(f"{money:code}")
```

Expected output:

```text
Money(minor_units=1250, currency='EUR')
12.50 EUR
True
False
2
EUR 1250
```

Why this design works:

- Dataclass-generated `__repr__`, `__eq__`, and `__hash__` use the declared fields.
- `frozen=True` prevents ordinary reassignment of fields; `slots=True` reduces per-instance storage overhead and prevents an instance dictionary by default.
- Currency normalization occurs during initialization. `object.__setattr__` is used because a frozen dataclass blocks ordinary assignment in `__post_init__`.
- The hash is derived from immutable equality fields.
- `Decimal` is used for display calculation, while the stored amount remains an integer.
- The example assumes two minor-unit digits for every currency. Real financial systems must model currency-specific scales and rounding policies explicitly; not every currency uses two decimal places.

For a hand-written implementation, the same design rules apply: validate inputs, normalize before equality/hash use, compare exactly the fields that define value, and never mutate those fields after the object becomes a key.

---

## 12. Production applications: data engineering and AI engineering

### Data engineering

- **Deduplication:** a stable value object can be compared and placed in a set when its fields define a record's logical identity.
- **Pipeline cache keys:** immutable tuples or frozen value objects can make safe in-process keys. For cross-run caches, use a canonical encoding and stable digest rather than Python's `hash()`.
- **Data-quality findings:** representations should expose useful fields such as rule name, severity, and row count without dumping an entire dataset or leaking source records.
- **Schema and configuration models:** equality helps tests detect semantic changes; explicit formatting improves logs and command-line reports.
- **Dictionary indexing:** hashability supports in-memory grouping and lookup, but only if equality/hash semantics are correct.

### AI engineering

- **Feature/configuration keys:** immutable configuration objects can safely key memoization or local caches when all equality-relevant fields are immutable.
- **Experiment metadata:** concise `repr()` output helps compare run configurations; avoid embedding credentials or large prompts in logs.
- **Evaluation results:** value equality can make tests deterministic, provided floating-point tolerances and missing values are handled intentionally.
- **Model artifact identity:** do not use `hash(model_config)` as a durable artifact ID. Use canonical serialized configuration plus a stable digest and include versioning where appropriate.
- **Tensor and array objects:** library objects may have domain-specific equality semantics (for example, elementwise comparisons). Do not assume every `==` result is a single boolean or that every object should be hashable. Follow the library's documented contract.

---

## 13. Common mistakes and corrected designs

| Mistake | Why it fails | Better approach |
|---|---|---|
| `__eq__` blindly accesses `other.value` | Comparing to an unrelated type can raise `AttributeError` | Check supported types and return `NotImplemented` |
| Return `False` for every foreign type | Prevents the other type's equality method from deciding | Return `NotImplemented` when unsupported |
| Define `__eq__` but assume instances remain hashable | Python normally sets `__hash__ = None` | Deliberately implement a compatible hash or stay unhashable |
| Hash a list directly | Lists are unhashable | Use immutable normalized data, or make the object unhashable |
| Hash mutable equality fields | Mutating a key can break set/dict lookup | Freeze state or hash an immutable key |
| Equal values produce different hashes | Hash table behavior violates the contract | Hash the same equality-relevant immutable fields |
| Use `hash()` as a persistent ID | Hashes may vary across processes and are not collision-free | Use canonical serialization and an appropriate stable identifier/digest |
| Put secrets in `__repr__` | Logs and tracebacks can leak credentials | Redact or omit sensitive fields |
| Make `__repr__` perform I/O | Logging/debugging can become slow or fail | Keep representations local, bounded, and side-effect-free |
| Treat `repr()` as safe serialization | `eval` can execute code and representations may not round-trip | Use validated, explicit serialization |
| Assume frozen means deeply immutable | Nested mutable objects can still change | Use immutable field types or defensive copies |
| Use float equality for financial values | Binary floating-point can surprise | Store integer minor units or use `Decimal` with explicit rules |
| Assume `NaN == NaN` | IEEE 754 specifies otherwise | Normalize or represent missingness explicitly |
| Add a custom `__bool__` casually | Truth tests may contradict object contents | Document domain semantics and test both empty/non-empty cases |

### Failure scenario: mutable dictionary key

Suppose an object is inserted into a dictionary, then a field used by `__hash__` changes. A later lookup may fail because the object is searched for in a bucket determined by its new hash, while it remains stored in the old bucket. Never mutate equality/hash fields of stored keys.

### Failure scenario: equality that violates symmetry

If a base class compares equal to a subclass while the subclass compares unequal to the base class, `a == b` and `b == a` may disagree. This can make deduplication, testing, and collections hard to reason about. Choose and test a coherent subclass policy rather than mixing incompatible equality definitions.

---

## 14. Testing and debugging strategies

Use tests to verify contracts, not just individual example outputs. The following checks are especially valuable:

1. **Representation:** readable output, useful field names, no secrets, no exceptions for recursive structures.
2. **Equality laws:** reflexivity for ordinary values, symmetry, transitivity, and sensible cross-type behavior.
3. **Hash contract:** equal objects have equal hashes; a set deduplicates equal values.
4. **Hashability policy:** mutable value objects intentionally raise `TypeError` from `hash()`.
5. **Stability:** fields participating in equality/hash cannot be reassigned or mutated.
6. **Truthiness:** test both empty and non-empty states and verify `__bool__` precedence when used.
7. **Formatting:** test supported specs and clear errors for unsupported specs.
8. **Process behavior:** never assert a specific string hash across processes.

### Example pytest test module

Save the `Money` implementation from Section 11 in `money.py`, then save this as `test_money.py`:

```python
import pytest

from money import Money

def test_equal_money_has_equal_hash_and_deduplicates() -> None:
    left = Money(1250, "eur")
    right = Money(1250, "EUR")

    assert left == right
    assert hash(left) == hash(right)
    assert len({left, right}) == 1

def test_currency_is_part_of_value() -> None:
    assert Money(100, "USD") != Money(100, "EUR")

def test_foreign_type_comparison_is_safe() -> None:
    assert Money(100, "USD") != 100

def test_frozen_fields_cannot_be_reassigned() -> None:
    value = Money(100, "USD")
    with pytest.raises((AttributeError, TypeError)):
        value.minor_units = 200  # type: ignore[misc]

def test_currency_validation() -> None:
    with pytest.raises(ValueError):
        Money(100, "US")

def test_minor_units_reject_bool() -> None:
    with pytest.raises(TypeError):
        Money(True, "USD")

def test_format_specs() -> None:
    value = Money(1250, "USD")
    assert str(value) == "12.50 USD"
    assert format(value, "code") == "USD 1250"

def test_unknown_format_spec_fails_clearly() -> None:
    with pytest.raises(ValueError, match="unsupported Money format"):
        format(Money(100, "USD"), "scientific")

def test_repr_is_informative_and_container_uses_repr() -> None:
    value = Money(1250, "USD")
    assert repr(value) == "Money(minor_units=1250, currency='USD')"
    assert repr([value]) == "[Money(minor_units=1250, currency='USD')]"

def test_dataclass_equality_is_same_concrete_type() -> None:
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class Base:
        value: int

    @dataclass(frozen=True)
    class Child(Base):
        extra: str = "x"

    assert Base(1) != Child(1, "x")

def test_money_is_hashable_but_frozen() -> None:
    value = Money(100, "USD")
    assert isinstance(hash(value), int)
    with pytest.raises((AttributeError, TypeError)):
        value.currency = "EUR"  # type: ignore[misc]
```

Run:

```bash
python -m pytest -q
```

Expected result: all eleven tests pass when the `Money` class from Section 11 is saved in `money.py` and pytest is installed. This expected result must be checked by running the command; do not assume a test suite passed merely because the code looks plausible.

### Additional contract tests for a hand-written class

```python
def assert_equality_laws(a: object, b: object, c: object) -> None:
    assert a == a
    assert (a == b) == (b == a)
    if a == b and b == c:
        assert a == c
```

This helper is intentionally simple. In real tests, only apply reflexivity expectations to types whose equality semantics promise it; `NaN` is an exception. Avoid calling the helper with arbitrary unrelated types if the domain does not promise cross-type equality.

Useful debugging tools:

- `repr(obj)` at a breakpoint to inspect state.
- `type(obj)` and `type(obj).__hash__` to inspect type/hash policy.
- `hash(obj)` inside a controlled test to check hashability, not to record a stable identifier.
- `obj == other` in both operand orders when testing custom equality.
- `pytest.mark.parametrize` for multiple currencies, values, and unsupported operand types.
- A minimal reproduction when collection membership behaves unexpectedly.

---

## 15. Exercises

Try each exercise before reading the answer key.

### Beginner

1. Create a `Job` class with `name` and `attempts`. Implement a constructor-like `__repr__`. What should `print([job])` display?
2. Explain the difference between `a == b` and `a is b` using two separate objects with the same fields.
3. Create a class with `__len__` returning zero. Predict `bool(instance)`, then add `__bool__` returning `True` and explain the changed result.

### Intermediate

4. Implement a `DatasetKey` value object with immutable `source` and `version` fields, value equality, and a compatible hash. Prove two equal keys deduplicate in a set.
5. Explain why a class that defines `__eq__` but not `__hash__` is normally unhashable.
6. Extend a class with `__format__` to support one documented format specifier and reject unknown ones.
7. Write a pytest test proving that a class's equality works safely against an integer.

### Advanced

8. A subclass adds `tenant_id` to a base class that compares only `name`. Explain how the chosen `isinstance` policy could violate the intended equality semantics. Propose a coherent policy.
9. Explain why using `hash(configuration)` as a persistent cache key is incorrect. Outline a safer strategy.
10. Create a recursive linked object and protect its `__repr__` using `reprlib.recursive_repr`.
11. Explain the surprising difference between `nan1 in {nan1}` and `nan2 in {nan1}` for two separately created NaNs.
12. Review a proposed `__hash__` that returns `hash(self.tags)` where `self.tags` is a list. Explain the immediate failure and a safe redesign.

---

## 16. Answer key

1. A useful implementation is `return f"Job(name={self.name!r}, attempts={self.attempts!r})"`. A list displays each element with `repr()`, so output is similar to `[Job(name='load', attempts=0)]`.
2. `==` invokes equality semantics and may compare values. `is` tests whether both names refer to the exact same object. Separate instances can be equal without being identical.
3. If `__bool__` is absent, a zero length makes the instance false. If `__bool__` returns `True`, it takes precedence and the instance is true even when `__len__` returns zero.
4. Store only immutable fields (for example, a frozen dataclass). Compare `(source, version)` and return `hash((source, version))`. Equal instances then have equal hashes; a set keeps one representative.
5. Python disables inherited object hashing when a class defines equality but does not define a matching hash. This avoids accidentally using identity hashing for objects that now compare equal by value.
6. Parse only documented specs and raise a clear exception for unknown specs. Keep the format grammar narrow; do not silently ignore unsupported formatting instructions.
7. Implement `__eq__(self, other: object)` with a type check and `return NotImplemented` for unsupported types. Assert `value != 7` and ensure no `AttributeError` is raised.
8. If the base accepts all subclasses but ignores `tenant_id`, objects from different tenants might compare equal despite being distinct domain values. Use exact-type equality for independent value types, or design a shared equality contract that includes all relevant fields across the hierarchy.
9. `hash()` can vary between processes and is not collision-free. Canonicalize the configuration (with stable field ordering and normalized values), serialize it in a documented format, and use a stable digest such as SHA-256; version the schema if its meaning can change.
10. Decorate `__repr__` with `@recursive_repr()` from `reprlib`, and build the string from fields using `!r`.
11. A set may recognize the identical object through identity shortcuts, while a distinct NaN compares unequal to the stored NaN. NaN is not reflexive under equality.
12. Lists are unhashable, so `hash(self.tags)` raises `TypeError`. If tags define value identity, normalize them into an immutable tuple at construction and prevent mutation; otherwise make the containing object unhashable.

---

## 17. Roadmap coverage checklist

Use this checklist to verify that the lesson's required syllabus has been studied.

- [ ] Dunder terminology and Python data-model dispatch.
- [ ] `__repr__`, `__str__`, their audiences, fallback, REPL and container behavior.
- [ ] Default identity equality versus value equality.
- [ ] Type checks and safe `__eq__` handling.
- [ ] `NotImplemented` as a special return value; reflected equality dispatch and identity fallback.
- [ ] `isinstance` versus exact-type equality and subclass implications.
- [ ] Equality laws: reflexivity, symmetry, transitivity, and consistency.
- [ ] `__hash__`, hashability, collisions, and the equality/hash contract.
- [ ] Why defining `__eq__` without `__hash__` normally makes instances unhashable.
- [ ] Immutable equality fields, mutable state, dictionary keys, sets, and hash stability.
- [ ] Hash randomization and why `hash()` is not a persistent identifier.
- [ ] `__bool__`, `__len__`, truth-value testing, and precedence.
- [ ] `__format__` and custom format specifications.
- [ ] Safe and bounded representations, recursive representations, and `reprlib`.
- [ ] Limits and security risks of `eval`-compatible representations.
- [ ] Dataclass behavior with `eq=True` and `frozen=True`.
- [ ] Floating-point `NaN` equality and set-membership implications.
- [ ] Common implementation mistakes, failure scenarios, pytest tests, and corrected designs.
- [ ] All three authoritative roadmap self-check questions answered below.

---

## 18. Roadmap self-assessment: the three self-check questions

### 1. Why does `{Money(1, "USD")}` raise `TypeError` if you define only `__eq__`?

Defining `__eq__` without defining a compatible `__hash__` causes Python to set the class's `__hash__` to `None`. A set requires hashable elements, so adding an instance raises `TypeError`. The correct design is either to make the object intentionally unhashable or to implement a compatible hash over immutable equality-relevant state.

### 2. What does `Money(1, "USD") == 5` return, and why is that better than `False` from `__eq__`?

For a well-designed `Money.__eq__`, comparing to an unsupported type returns `NotImplemented`. Python then gives the other operand a chance to handle the comparison. If neither side supports it, equality falls back to identity semantics, so this expression evaluates to `False` without an attribute error. This is more composable than claiming that every foreign type has been handled by returning `False` immediately.

### 3. Write a `__repr__` whose output, passed to `eval`, rebuilds the object.

For a simple class:

```python
class MoneyExample:
    def __init__(self, minor_units: int, currency: str) -> None:
        self.minor_units = minor_units
        self.currency = currency

    def __repr__(self) -> str:
        return (
            f"MoneyExample({self.minor_units!r}, "
            f"{self.currency!r})"
        )

original = MoneyExample(100, "USD")
namespace = {"MoneyExample": MoneyExample}
copy = eval(repr(original), {"__builtins__": {}}, namespace)
assert copy.minor_units == original.minor_units
assert copy.currency == original.currency
```

This works only because the class name is available in the evaluation namespace and the representation is deliberately written as a valid constructor expression. It is a controlled demonstration, not a safe serialization pattern. Never evaluate representations from untrusted sources.

---

## 19. Final engineering checklist

Before shipping a class that customizes these methods, confirm:

- [ ] `__repr__` is informative, bounded, side-effect-free, and does not expose secrets.
- [ ] `__str__` is appropriate for user-facing output; containers still have a useful `repr`.
- [ ] Representation output is not mistaken for a guaranteed serialization format.
- [ ] `__eq__` handles unsupported types without raising accidental `AttributeError`.
- [ ] The subclass equality policy is explicit and preserves symmetry/transitivity.
- [ ] Equality is consistent with the domain's definition of value.
- [ ] The class is deliberately hashable or unhashable.
- [ ] If hashable, equal objects always have equal hashes.
- [ ] Every equality/hash field is immutable for as long as the object is used as a key.
- [ ] No Python `hash()` value is persisted as a durable identifier.
- [ ] Truthiness has documented semantics and respects `__bool__` precedence.
- [ ] Custom formatting is documented and rejects unsupported specifications clearly.
- [ ] `NaN` and missing numeric values are handled intentionally.
- [ ] Dataclass-generated methods and field participation have been reviewed rather than assumed.
- [ ] Tests cover equality laws, hash compatibility, foreign types, mutation attempts, formatting, and edge cases.
- [ ] Examples and tests are run in the project's supported Python version before release.

**Lesson complete.** The next lesson in the roadmap is `02-rich-comparison-and-total-ordering.md`; do not start it until you can explain and test the contracts in this lesson.
