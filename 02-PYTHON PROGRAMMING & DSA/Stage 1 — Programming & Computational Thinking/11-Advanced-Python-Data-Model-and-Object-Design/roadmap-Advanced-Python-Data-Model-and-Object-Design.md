# Roadmap — Module 1.11: Advanced Python Data Model and Object Design

This is the learning roadmap for the eleventh module of Stage 1,
**Programming & Computational Thinking**. It tells you **what** to learn
about the Python data model, **in what order**, **how** to practise each
topic, and **how to prove to yourself** that you have learned it.

Every Python object — a list, a `Decimal`, a pandas `DataFrame`, a
PyTorch `Tensor`, a Pydantic model — behaves the way it does because of
**special methods** ("dunder methods") the class defines. Libraries you will
use for the rest of this repository (NumPy, pandas, SQLAlchemy, Pydantic,
PyTorch, FastAPI) are built from exactly the mechanisms in this module:
operator overloading, descriptors, properties, `__slots__`, the method
resolution order, abstract base classes and pickling. A senior engineer
reads library source, debugs surprising attribute behaviour, and designs
classes that feel native to Python. This module is where that skill is built.

Modules 1.8 (OOP design) and 1.24 (gap lessons: classes, `__init__`, `super()`
basics) taught **how to design with classes**. This module teaches **how Python
itself implements classes**, and how to make your own classes plug into the
language.

> Target version: **Python 3.12+**. Where 3.13 or 3.14 changes behaviour
> (for example `copy.replace`, deferred annotations), the lesson says so.

---

## 1. Module outcome

By the end of this module you will be able to:

- Implement `__repr__`, `__str__`, `__eq__`, `__hash__`, `__bool__` and
  `__format__` correctly, and explain the **eq/hash contract**.
- Make a class sortable with `functools.total_ordering` or explicit rich
  comparisons, and return `NotImplemented` properly.
- Build classes that behave like sequences, mappings and iterables using
  `__len__`, `__getitem__`, `__iter__`, `__contains__`, `__reversed__`.
- Overload arithmetic and comparison operators, including reflected and
  in-place variants, without breaking type expectations.
- Use `@property`, setters, `functools.cached_property`, and explain why
  properties are built on descriptors.
- Write data and non-data descriptors, and predict the **attribute lookup
  order** (`__getattribute__`, data descriptors, instance dict, non-data
  descriptors, `__getattr__`).
- Use `__slots__` and measure the memory difference and its trade-offs.
- Read an MRO, use `super()` correctly in cooperative multiple inheritance,
  and explain C3 linearisation.
- Design mixins and recognise multiple-inheritance traps.
- Define abstract base classes with `abc`, use `collections.abc` mix-in
  methods, and register virtual subclasses.
- Control copying (`__copy__`, `__deepcopy__`), pickling (`__reduce__`,
  `__getstate__`, `__setstate__`) and object lifecycle (`__new__`,
  `__init_subclass__`, `__del__`, `weakref.finalize`).

---

## 2. Prerequisites

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Classes, instance vs class attributes | Module 1.8 (04) | The data model extends these |
| Inheritance and polymorphism | Module 1.8 (02) | MRO and `super()` build on it |
| `__init__`, `__new__`, basic `super()` | Module 1.24 (09, 10) | Construction is revisited at depth |
| Iterators and generators | Module 1.9 (01) | Container protocols use them |
| Python object model and garbage collection | Module 1.9 (10) | `__slots__`, weakrefs and finalizers |
| Mutability, aliasing | Module 1.2 (10) | Copy semantics |
| Dataclasses and Protocols | Module 1.8 (03, 05) | Compare with hand-written dunder methods |
| pytest and parametrization | Module 1.7 | Every exercise has tests |

**Tools needed:** Python 3.12+ in a `uv` project, `pytest`, `ruff`,
`mypy` or `pyright`, and `sys.getsizeof` / `tracemalloc` for the memory
exercises.

---

## 3. How the module is organised

```text
Phase A — Making Objects Behave            (Basics)
  01 dunder methods: repr, str, eq, hash
  02 rich comparison and total ordering
  03 container protocols
Phase B — Operators and Attributes         (Intermediate)
  04 operator overloading and numeric protocols
  05 properties and computed attributes
  06 descriptors and attribute lookup order
Phase C — Memory and Inheritance Mechanics (Advanced)
  07 __slots__ and memory layout
  08 MRO, super() and cooperative inheritance
  09 mixins and multiple-inheritance pitfalls
Phase D — Contracts and Lifecycle          (Advanced)
  10 abstract base classes and collections.abc
  11 copying, pickling and object lifecycle hooks
```

Suggested pace: one lesson per study session, plus a consolidation session at
the end of each phase. Total: about 3–4 weeks part-time.

For every lesson use the same loop: **read → type every example → break it on
purpose → write tests → answer the self-check questions**.

---

## Lesson 01 — `01-dunder-methods-repr-str-eq-and-hash.md`

**Why it matters.** Printing, logging, debugging, set membership, dictionary
keys and test assertions all depend on these five methods. A wrong
`__eq__`/`__hash__` pair causes silent data loss in sets and dict keys.

### Basic — what to learn

- What a "dunder" (double-underscore) method is, and that you almost never
  call it directly: `len(x)` calls `type(x).__len__(x)`.
- `__repr__`: unambiguous, developer-facing, ideally `eval`-able look.
  `__str__`: readable, user-facing. `print` and `f"{x}"` use `__str__`;
  the REPL, `repr()`, and containers' display use `__repr__`.
- If only one is defined, define `__repr__` — `__str__` falls back to it.
- `__eq__` compares values; default compares identity (`is`).
- `__bool__` and `__len__` and how truthiness is decided.

```python
class Money:
    def __init__(self, amount: int, currency: str) -> None:
        self.amount = amount          # minor units, e.g. cents
        self.currency = currency

    def __repr__(self) -> str:
        return f"Money({self.amount!r}, {self.currency!r})"

    def __str__(self) -> str:
        return f"{self.amount / 100:.2f} {self.currency}"

print(Money(1250, "EUR"))        # 12.50 EUR
print([Money(1250, "EUR")])      # [Money(1250, 'EUR')]  <- containers use repr
```

### Intermediate — what to learn

- Writing `__eq__` correctly: check type, return `NotImplemented` (not
  `False`) for foreign types so Python can try the reflected operation.
- **The eq/hash contract:** objects that compare equal must have equal
  hashes. Defining `__eq__` without `__hash__` sets `__hash__` to `None`
  (the class becomes unhashable).
- Hash only **immutable** fields; mutating a hashed field after insertion
  into a set/dict corrupts lookups.
- `__format__` and format specs: `f"{price:>10.2f}"`, custom spec mini-languages.
- `__bool__` vs `__len__` precedence.

```python
class Money:
    __slots__ = ("amount", "currency")

    def __init__(self, amount: int, currency: str) -> None:
        self.amount, self.currency = amount, currency

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return (self.amount, self.currency) == (other.amount, other.currency)

    def __hash__(self) -> int:
        return hash((self.amount, self.currency))

assert {Money(1, "USD"), Money(1, "USD")} == {Money(1, "USD")}
assert Money(1, "USD") != 1          # falls back to identity, no exception
```

### Advanced — what to learn

- Why `NotImplemented` matters: `a == b` tries `a.__eq__(b)`, then
  `b.__eq__(a)`, then identity. Returning `False` too early blocks subclass
  and third-party equality.
- Subclass equality: `isinstance` vs `type(self) is type(other)`; the
  Liskov trade-off and symmetry/transitivity of equality.
- Hash stability across processes: string hashes are randomised
  (`PYTHONHASHSEED`), so never persist `hash()` values.
- `__repr__` design for debuggability: include identifying fields, avoid
  huge output, handle recursion with `reprlib` / `reprlib.recursive_repr`.
- `dataclass(eq=True, frozen=True)` generates `__eq__` and `__hash__` — know
  exactly what it generates so you can reason about it.
- Float and NaN: `nan != nan`, and what that means for `__eq__` and set membership.

### Common mistakes

- `__eq__` that raises `AttributeError` for other types.
- Defining `__eq__` and forgetting `__hash__`, or hashing mutable lists.
- A `__repr__` that raises (it breaks debuggers and logs).
- Using `__str__` for data that must round-trip.

### Self-check

1. Why does `{Money(1,"USD")}` raise `TypeError` if you define only `__eq__`?
2. What does `Money(1,"USD") == 5` return, and why is that better than `False` from `__eq__`?
3. Write a `__repr__` whose output, passed to `eval`, rebuilds the object.

---

## Lesson 02 — `02-rich-comparison-and-total-ordering.md`

**Why it matters.** Sorting, `min`/`max`, `bisect`, `heapq` and sorted
containers all rely on ordering methods. Version numbers, priorities,
money, semantic versions and timestamps need correct, consistent ordering.

### Basic — what to learn

- The six rich comparison methods: `__lt__`, `__le__`, `__eq__`, `__ne__`,
  `__gt__`, `__ge__`.
- `sorted()` and `list.sort()` only need `__lt__`.
- Sorting with `key=` versus defining ordering on the class itself — prefer
  `key=` for one-off sorting, class ordering when ordering is intrinsic.

```python
class Version:
    def __init__(self, major: int, minor: int, patch: int) -> None:
        self.parts = (major, minor, patch)

    def __lt__(self, other: "Version") -> bool:
        return self.parts < other.parts

print(sorted([Version(1, 2, 0), Version(1, 0, 9)])[0].parts)   # (1, 0, 9)
```

### Intermediate — what to learn

- `functools.total_ordering`: define `__eq__` plus one of `<`, `<=`, `>`, `>=`
  and the decorator fills in the rest; know its **performance cost** and that
  the generated methods are slower than hand-written ones.
- Returning `NotImplemented` for unsupported types so that `Version(1,0,0) < 3`
  raises a clean `TypeError`.
- `dataclass(order=True)` compares fields as a tuple in declaration order;
  `field(compare=False)` excludes a field.
- Using `tuple` comparison as a shortcut: `(self.a, self.b) < (other.a, other.b)`.
- `operator.attrgetter`, `operator.itemgetter` and `key=` for multi-key sorting;
  stable sorting and sorting by multiple keys with different directions.

```python
from functools import total_ordering

@total_ordering
class Priority:
    _ORDER = {"low": 0, "medium": 1, "high": 2}
    def __init__(self, name: str) -> None:
        self.name = name
    def _rank(self) -> int:
        return self._ORDER[self.name]
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Priority):
            return NotImplemented
        return self._rank() == other._rank()
    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Priority):
            return NotImplemented
        return self._rank() < other._rank()
    def __hash__(self) -> int:       # defining __eq__ removes the default hash
        return hash(self._rank())
```

### Advanced — what to learn

- **Total order laws:** reflexive, antisymmetric, transitive, total. A
  comparison that violates them makes `sort` and `heapq` return garbage
  without raising.
- Floating-point and `NaN` in comparisons; why sorting lists with `NaN` is
  undefined; how to handle with a key function.
- Partial orders (sets use `<` as subset) and why `sorted` on sets of sets is wrong.
- `functools.cmp_to_key` for legacy comparators and when a comparator is
  genuinely needed.
- Consistency between ordering and equality: `a <= b and b <= a` should imply `a == b`.
- Ordering heterogeneous types: Python 3 refuses (`1 < "a"`); design a
  deliberate sort key rather than relying on cross-type ordering.
- Interaction with `bisect` and `heapq`: both require a consistent `__lt__`.

### Common mistakes

- Mixing `__eq__` with a different notion than `__lt__`.
- Comparing floats built from money.
- Using `total_ordering` on a hot path without profiling.

### Self-check

1. Which single method does `sorted()` require?
2. Why does `total_ordering` need `__eq__` as well?
3. Demonstrate a comparison that breaks transitivity and show what `sorted` does.

---

## Lesson 03 — `03-container-protocols-getitem-len-iter-and-contains.md`

**Why it matters.** NumPy arrays, pandas Series, `pathlib.Path`, ORM result
sets and config objects all feel native because they implement the container
protocols. This lesson is the recipe.

### Basic — what to learn

- `__len__` → `len(x)`; `__getitem__` → `x[i]`; `__iter__` → `for ... in x`;
  `__contains__` → `item in x`.
- The fallback: if `__iter__` is missing but `__getitem__` accepts integers
  from 0, Python can iterate using the **legacy sequence protocol**.
- `__contains__` fallback: uses iteration if not defined.

```python
class Deck:
    RANKS = [str(n) for n in range(2, 11)] + list("JQKA")
    SUITS = ["spades", "diamonds", "clubs", "hearts"]
    def __init__(self) -> None:
        self._cards = [(r, s) for s in self.SUITS for r in self.RANKS]
    def __len__(self) -> int:
        return len(self._cards)
    def __getitem__(self, position):
        return self._cards[position]

d = Deck()
print(len(d), d[0], d[-1], d[:3])       # slicing works for free
print(("A", "hearts") in d)             # True via iteration fallback
```

### Intermediate — what to learn

- Slice objects: `__getitem__` receives a `slice(start, stop, step)`;
  return the same container type from a slice.
- `__setitem__`, `__delitem__` and mutable containers; `__missing__` for
  `dict` subclasses.
- `__reversed__` and `__iter__` vs returning a separate iterator class.
- `__index__` so your integer-like object can index lists.
- `__bool__` default via `__len__`.
- Subclassing built-ins (`list`, `dict`) versus composition; why overridden
  methods on `dict` subclasses are **not** called by C-level code (for
  example `dict.update`), and why `collections.UserDict` / `UserList`
  exist.

```python
from collections import UserDict

class CaseInsensitiveDict(UserDict):
    def __setitem__(self, key, value):
        super().__setitem__(key.lower(), value)
    def __getitem__(self, key):
        return super().__getitem__(key.lower())
```

### Advanced — what to learn

- Multi-dimensional indexing: `x[1, 2]` passes a **tuple**; `x[1:3, ::2]`
  passes a tuple of slices; this is how NumPy and pandas work.
- Ellipsis `...` in indexing.
- Lazy views vs copies: return a view object (like `dict.keys()`), not a
  list, for large containers.
- Reversibility, sized and hashable iteration contracts; how `typing`
  protocols (`Sized`, `Iterable`, `Container`, `Collection`, `Sequence`)
  describe these shapes — preview of Lesson 10.
- Iterator vs iterable: implement `__iter__` returning a fresh generator so
  the container can be iterated many times.
- `__length_hint__` for pre-sizing.
- Exceptions: `IndexError` for sequences, `KeyError` for mappings — `for`
  loops over the legacy protocol stop on `IndexError`.

### Common mistakes

- Returning a `list` from a slice of a custom type.
- Making `__iter__` return `self` without a `__next__`.
- Subclassing `dict` and overriding only `__setitem__`.

### Self-check

1. How does Python iterate an object that only defines `__getitem__`?
2. What does `obj[1:3, 0]` pass to `__getitem__`?
3. Why prefer `UserDict` over subclassing `dict` for validation logic?

---

## Lesson 04 — `04-operator-overloading-and-numeric-protocols.md`

**Why it matters.** `Vector + Vector`, `Money * 3`, `Path / "file"`,
`DataFrame & mask`, `Tensor @ Tensor` — operator overloading is the reason
scientific Python reads like maths. Misused, it produces unreadable and
surprising code, so this lesson also teaches restraint.

### Basic — what to learn

- Binary operators map to methods: `+` → `__add__`, `-` → `__sub__`,
  `*` → `__mul__`, `/` → `__truediv__`, `//` → `__floordiv__`,
  `%` → `__mod__`, `**` → `__pow__`, `@` → `__matmul__`.
- Unary: `__neg__`, `__pos__`, `__abs__`, `__invert__`.
- Return a **new** object; do not mutate operands for `+`.

```python
class Vector:
    def __init__(self, x: float, y: float) -> None:
        self.x, self.y = x, y
    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)
    def __mul__(self, scalar: float) -> "Vector":
        return Vector(self.x * scalar, self.y * scalar)
    def __abs__(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5
    def __repr__(self) -> str:
        return f"Vector({self.x!r}, {self.y!r})"
```

### Intermediate — what to learn

- **Reflected operators** (`__radd__`, `__rmul__`): why `3 * Vector(1, 2)`
  fails without `__rmul__`.
- **In-place operators** (`__iadd__`): mutate and return `self`; fall back
  to `__add__` if absent. Contrast `list +=` (in-place, aliasing!) with
  `tuple +=` (rebinding).
- Returning `NotImplemented` for unsupported operand types, so Python tries
  the other operand's reflected method, and finally raises `TypeError`.
- Conversion methods: `__int__`, `__float__`, `__complex__`, `__round__`,
  `__index__`, `__bool__`.
- Bitwise operators `&`, `|`, `^`, `<<`, `>>` and their use for sets/flags
  (`enum.Flag`).
- `__matmul__` for matrix multiplication; why `@` exists.

```python
    def __rmul__(self, scalar: float) -> "Vector":
        return self * scalar

    def __iadd__(self, other: "Vector") -> "Vector":
        self.x += other.x
        self.y += other.y
        return self
```

### Advanced — what to learn

- Operand dispatch order, including the rule that a **subclass's reflected
  method gets priority** over the left operand's method.
- Numeric tower and `numbers.Number`, `numbers.Real`; supporting `Fraction`,
  `Decimal` and `int` interoperably; why `Decimal + float` raises.
- `__divmod__`, `__pow__` with the three-argument modular form.
- Fluent DSL operators (`Path / "x"`, `|` for pipelines, `>>` for composition)
  and the design test: *is the operator meaning obvious to a reader?*
- `__array_ufunc__` / `__array__` (awareness): how NumPy coordinates with
  custom objects.
- Immutability for value objects: operators on frozen dataclasses.
- Performance: operator overloads create many temporaries; discuss in-place
  variants and vectorisation instead of per-element Python objects.

### Common mistakes

- Mutating `self` inside `__add__`.
- Forgetting reflected methods and then being surprised by `sum()`
  (which starts from `0 + obj` → needs `__radd__`).
- Overloading `+` for a non-addition meaning.

### Self-check

1. Why does `sum([Vector(1,1), Vector(2,2)])` fail by default and how do you fix it?
2. What happens if `__add__` returns `NotImplemented`?
3. Which method does `v += w` call when `__iadd__` is absent?

---

## Lesson 05 — `05-properties-and-computed-attributes.md`

**Why it matters.** Properties let you start with a simple public attribute
and later add validation, caching or computation **without changing the
API**. That is the Pythonic replacement for Java-style getters/setters.

### Basic — what to learn

- `@property` for read-only computed attributes.
- `@x.setter` and `@x.deleter`.
- Naming conventions: `_value` for storage, `value` for the public property.
- Why not to write `get_x()`/`set_x()` in Python.

```python
class Temperature:
    def __init__(self, celsius: float) -> None:
        self.celsius = celsius                  # goes through the setter

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15:
            raise ValueError("below absolute zero")
        self._celsius = value

    @property
    def fahrenheit(self) -> float:              # computed, read-only
        return self._celsius * 9 / 5 + 32
```

### Intermediate — what to learn

- Validation in setters, including in `__init__` (assign through the
  property, not directly to `_celsius`).
- Read-only attributes and the `AttributeError` behaviour.
- `functools.cached_property`: compute once per instance; requires an
  instance `__dict__` (so it does not work with `__slots__` unless a
  `__dict__` slot exists); thread-safety history and the 3.12 change.
- Invalidating caches when dependencies change.
- Properties on dataclasses (`field` + `@property` pitfalls), and on
  `NamedTuple`/frozen classes.
- Properties and inheritance: overriding only the getter, using
  `@Base.prop.setter` to extend.

```python
from functools import cached_property

class Report:
    def __init__(self, rows: list[dict]) -> None:
        self.rows = rows

    @cached_property
    def total(self) -> float:
        print("computing…")
        return sum(r["amount"] for r in self.rows)
```

### Advanced — what to learn

- A property is a **data descriptor** implemented in C; understand
  `property(fget, fset, fdel, doc)` as the explicit form.
- Properties vs `__getattr__` vs descriptors: when each is right.
- Expensive properties: a property that looks like an attribute but does
  I/O violates reader expectations — document or use a method.
- Lazy loading patterns and their trade-offs (ORMs, config objects).
- Typing properties: `Self`, `Protocol` with property members, read-only
  protocol members.
- Class-level properties (the `classmethod`+`property` combination was
  deprecated in 3.11 and removed in 3.13) — use a descriptor or metaclass
  instead.
- Testing properties: validate both the happy and failure paths via the
  public attribute.

### Common mistakes

- Infinite recursion by setting `self.value = v` inside the `value` setter.
- Mutable defaults cached via `cached_property` shared across instances by mistake.
- Property performing network calls.

### Self-check

1. Why must `__init__` assign through the property rather than `_celsius`?
2. What does `cached_property` store and where?
3. When is a method better than a property?

---

## Lesson 06 — `06-descriptors-and-attribute-lookup-order.md`

**Why it matters.** Descriptors are the engine behind properties, methods,
`classmethod`, `staticmethod`, `__slots__`, and the field definitions of ORMs
(Django, SQLAlchemy) and validation libraries. If you understand
descriptors you understand how attribute access really works.

### Basic — what to learn

- A descriptor is an object whose class defines `__get__`, `__set__`,
  or `__delete__`, stored as a **class attribute**.
- Non-data descriptor: only `__get__` (functions are the classic example).
  Data descriptor: `__set__` and/or `__delete__` as well.
- Functions are descriptors: that is how `obj.method` becomes a **bound method**.

```python
class Positive:
    def __set_name__(self, owner, name):
        self.private = "_" + name
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self                   # accessed on the class
        return getattr(obj, self.private)
    def __set__(self, obj, value):
        if value <= 0:
            raise ValueError(f"{self.private[1:]} must be positive")
        setattr(obj, self.private, value)

class Order:
    quantity = Positive()
    price = Positive()
    def __init__(self, quantity, price):
        self.quantity, self.price = quantity, price
```

### Intermediate — what to learn

- `__set_name__` (3.6+) to learn the attribute name automatically.
- **Attribute lookup order** for `obj.attr` (`object.__getattribute__`):
  1. data descriptor on the type (including parents via MRO),
  2. instance `__dict__`,
  3. non-data descriptor or plain class attribute on the type,
  4. `__getattr__` fallback if defined (only when 1–3 raise `AttributeError`).
- Why a data descriptor wins over the instance dict and a non-data
  descriptor loses to it (this is why you can shadow a method on an instance).
- Storing per-instance data: in the instance `__dict__` under another name
  (as above), or a `WeakKeyDictionary` keyed by instance.
- Descriptors and `classmethod`/`staticmethod`: what `__get__` returns for each.
- Reading `inspect.getattr_static` to see attributes without triggering descriptors.

### Advanced — what to learn

- `__getattribute__` vs `__getattr__`: overriding the former is dangerous
  (infinite recursion; use `object.__getattribute__`).
- `type.__getattribute__` for **class** attribute lookup and how metaclasses change it.
- Writing a reusable validated-field system (typed descriptor with
  coercion, defaults, and error messages) — the shape of Pydantic v1 / ORM
  fields.
- Descriptors and `__slots__`: slots are implemented as member descriptors.
- Caching descriptor (`cached_property` reimplemented), and why it is a non-data descriptor.
- Descriptors in type checking: `Generic` descriptors with overloaded `__get__` for typed attributes.
- Performance: attribute lookup cost and the specialising interpreter (links to Module 1.19).

### Common mistakes

- Storing instance state on the descriptor itself (shared across all instances).
- Forgetting the `obj is None` branch, breaking class access (`Order.quantity`).
- Overriding `__getattribute__` carelessly.

### Self-check

1. Order the four steps of attribute lookup and justify why data descriptors win over the instance dict.
2. Why is `quantity = Positive()` shared state a bug if you store the value on `self.value` of the descriptor?
3. What does `Order.quantity` return and why?

---

## Lesson 07 — `07-slots-and-memory-layout.md`

**Why it matters.** Creating millions of small objects (rows, events,
tokens, nodes) is a classic memory hot spot. `__slots__` removes the
per-instance `__dict__` and can cut memory sharply — and also changes
inheritance and pickling behaviour you must know about.

### Basic — what to learn

- Default: each instance has a `__dict__` (a hash table) and a `__weakref__`.
- `__slots__ = ("x", "y")` replaces the dict with fixed storage slots.
- Effects: less memory, slightly faster attribute access, **no arbitrary new
  attributes** (`AttributeError`).

```python
import sys

class PointDict:
    def __init__(self, x, y): self.x, self.y = x, y

class PointSlots:
    __slots__ = ("x", "y")
    def __init__(self, x, y): self.x, self.y = x, y

p, q = PointDict(1, 2), PointSlots(1, 2)
print(sys.getsizeof(p) + sys.getsizeof(p.__dict__), sys.getsizeof(q))
```

### Intermediate — what to learn

- Measuring properly: `sys.getsizeof` is shallow; use `tracemalloc` on
  1,000,000 instances to measure real totals.
- Slots and inheritance: a subclass that does not declare `__slots__` gets a
  `__dict__` again; only declare **new** names in subclasses; multiple
  inheritance with non-empty slots on more than one base raises `TypeError`
  (layout conflict).
- Opt back in: include `"__dict__"` or `"__weakref__"` in `__slots__`.
- Slots with class-level defaults: a class attribute with the same name as a
  slot conflicts; set defaults in `__init__` or use `dataclass(slots=True)`.
- `dataclass(slots=True)` (3.10+) and what it rewrites (it creates a *new* class).
- Interaction with `cached_property` (needs `__dict__`) and pickling (works in 3.x for protocol 2+).

### Advanced — what to learn

- How CPython lays out an instance: object header, GC header, slot pointers;
  key-sharing dictionaries (PEP 412) and why plain classes are already
  smaller than you expect, and in 3.11+ **inline values** reduce the gap further.
- Therefore: **measure before adopting `__slots__`** — the saving depends on
  version and attribute count.
- When not to use slots: classes needing dynamic attributes, monkeypatching in
  tests, mixins, multiple inheritance.
- Alternatives for compact records: `NamedTuple`, `array`/`struct`, NumPy
  structured arrays, `memoryview`, columnar storage (pandas/Arrow) — row
  objects are rarely the right shape for millions of records.
- Slots as descriptors: `type(obj).x` is a `member_descriptor`.
- Weak references to slotted objects need `__weakref__` in slots.

### Common mistakes

- Expecting `__slots__` to speed up everything (it mainly saves memory).
- Declaring slots in every level of a hierarchy and duplicating names.
- Using `__slots__` and then trying `obj.new_attr = 1` in tests.

### Self-check

1. What two things does a normal instance carry that a slotted instance does not?
2. Why does a subclass without `__slots__` lose the benefit?
3. Measure 1,000,000 instances with and without slots using `tracemalloc` and report the ratio.

---

## Lesson 08 — `08-mro-super-and-cooperative-inheritance.md`

**Why it matters.** `super()` does **not** mean "my parent". It means "the
next class in the MRO". This distinction is the difference between working
and broken multiple inheritance, Django mixins, `unittest` cooperative
`setUp`, and every framework with plugin hierarchies.

### Basic — what to learn

- Every class has an ordered `__mro__`; inspect with `Class.__mro__` and
  `Class.mro()`.
- Single inheritance: MRO is the chain up to `object`.
- Zero-argument `super()` inside methods; calling `super().__init__(...)`.
- Method overriding, extending vs replacing parent behaviour.

```python
class Base:
    def greet(self): return "base"
class Child(Base):
    def greet(self): return "child+" + super().greet()
print(Child().greet())     # child+base
print(Child.__mro__)       # (Child, Base, object)
```

### Intermediate — what to learn

- Diamond inheritance and **C3 linearisation**: the rules (children before
  parents, preserve local precedence order, monotonicity) and why some
  hierarchies are rejected with `TypeError: Cannot create a consistent
  method resolution order`.
- Cooperative `super()`: every class in the chain calls `super().method(...)`
  once, so each implementation runs exactly once.
- Cooperative `__init__`: use keyword arguments and `**kwargs` pass-through so
  parents with different signatures compose.
- `super()` in classmethods and `__init_subclass__`.
- Debugging: printing the MRO, `inspect.getmro`.

```python
class A:
    def __init__(self, **kw): print("A"); super().__init__(**kw)
class B(A):
    def __init__(self, **kw): print("B"); super().__init__(**kw)
class C(A):
    def __init__(self, **kw): print("C"); super().__init__(**kw)
class D(B, C):
    def __init__(self, **kw): print("D"); super().__init__(**kw)
D()    # D B C A   — A runs once
```

### Advanced — what to learn

- How zero-argument `super()` works: the compiler-created `__class__` cell and
  the first argument; why it fails in functions defined outside a class.
- The two-argument forms `super(Class, obj)` and `super(Class, Class)`.
- Designing for cooperation: the base of the hierarchy must terminate the
  chain (consumes remaining `**kwargs`, calls `object.__init__()` with none).
- Pitfalls: signature mismatches, mixed positional arguments, calling
  `Parent.__init__(self)` directly in diamonds (runs the shared base twice).
- Fixing an unlinearisable hierarchy; composition over inheritance as the
  common refactor.
- Method resolution for attributes vs for special methods (looked up on the type).
- `functools.singledispatchmethod` and `super()` interplay (awareness).

### Common mistakes

- Using `Parent.method(self)` instead of `super()`.
- Different `__init__` signatures along the MRO.
- Assuming `super()` always refers to the declared base.

### Self-check

1. Predict the print order for the `D(B, C)` example when `B` forgets to call `super().__init__`.
2. Why does `class X(A, B)` fail if `class A(B)`? Write the C3 reasoning.
3. What does `super()` resolve to inside `B` when called on a `D` instance?

---

## Lesson 09 — `09-mixins-and-multiple-inheritance-pitfalls.md`

**Why it matters.** Mixins are the controlled, sensible use of multiple
inheritance: small classes that add one behaviour. Django, DRF, Flask
extensions, `socketserver` and `unittest` all use them. Knowing the
rules keeps you from the "diamond of doom".

### Basic — what to learn

- What a mixin is: a class meant to be **combined**, not instantiated alone;
  provides focused behaviour (`JSONMixin`, `ReprMixin`, `TimestampMixin`).
- Naming convention (`...Mixin`) and ordering (mixins first, base last).

```python
import json

class JsonMixin:
    def to_json(self) -> str:
        return json.dumps(self.__dict__, default=str)

class ReprMixin:
    def __repr__(self) -> str:
        args = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"{type(self).__name__}({args})"

class User(ReprMixin, JsonMixin):
    def __init__(self, name): self.name = name
```

### Intermediate — what to learn

- Rules for good mixins: no state of their own (or minimal), no `__init__`
  requirements, cooperative `super()`, document required host attributes.
- Ordering effects: left-most mixin overrides right-most; MRO decides.
- Mixin vs composition vs protocol: *"Does the behaviour need the host's
  internals?"* If not, prefer composition or a plain function.
- Mixin that provides default methods from a few required ones —
  `collections.abc.Mapping` is the model.
- Combining with dataclasses and `__slots__` (empty `__slots__ = ()` in mixins to stay compatible).
- Testing a mixin in isolation with a tiny host class.

### Advanced — what to learn

- **Pitfalls:** name collisions between mixins; hidden coupling through shared
  attribute names; `__init__` conflicts; the fragile base class problem;
  metaclass conflicts when bases have different metaclasses.
- Layout conflicts (`TypeError: multiple bases have instance lay-out conflict`)
  from non-empty slots or C-implemented builtins.
- Diamond problem with state and how cooperative design avoids duplicate initialisation.
- `__init_subclass__` hooks inside mixins to register or validate subclasses.
- Real-world reading exercise: trace `MRO` of a Django `ListView`
  (`MultipleObjectTemplateResponseMixin`, `BaseListView`) or
  `socketserver.ThreadingMixIn`; summarise what each layer contributes.
- Refactoring a deep hierarchy into strategy objects or protocols.

### Common mistakes

- Mixins that need `self.some_attr` that the host never defines.
- Putting the mixin after the concrete base (`class A(Base, Mixin)`), so the base overrides it.
- Stateful mixins with their own `__init__`.

### Self-check

1. Why is `class A(Mixin, Base)` the usual order?
2. Write a `TimestampMixin` and a test host class; show an MRO listing.
3. Name two situations where composition beats a mixin.

---

## Lesson 10 — `10-abstract-base-classes-and-collections-abc.md`

**Why it matters.** ABCs let you define an interface **and** enforce it at
instantiation time. `collections.abc` gives you ready-made protocols
(`Sequence`, `Mapping`, `MutableMapping`, `Iterable`, …) that fill in dozens of methods
from a handful of required ones.

### Basic — what to learn

- `abc.ABC`, `@abstractmethod`; a class with unimplemented abstract methods
  cannot be instantiated (`TypeError`).
- Abstract properties, abstract class/static methods (stack decorators
  correctly: `@classmethod` outermost, `@abstractmethod` innermost).
- Concrete methods on abstract classes (template method pattern).

```python
from abc import ABC, abstractmethod

class Exporter(ABC):
    @abstractmethod
    def serialise(self, data: dict) -> bytes: ...

    def export(self, data: dict, path: str) -> None:       # template method
        with open(path, "wb") as f:
            f.write(self.serialise(data))

class JsonExporter(Exporter):
    def serialise(self, data): return repr(data).encode()
```

### Intermediate — what to learn

- `collections.abc`: `Iterable`, `Iterator`, `Sized`, `Container`,
  `Collection`, `Sequence`, `MutableSequence`, `Mapping`, `MutableMapping`,
  `Set`, `Callable`, `Hashable`.
- **Mix-in methods:** subclass `Mapping` and implement `__getitem__`,
  `__iter__`, `__len__` to get `get`, `keys`, `items`, `values`, `__contains__`, `__eq__` free.
- `isinstance(x, Iterable)` checks via `__subclasshook__` (structural for
  one-trick-pony ABCs).
- `isinstance` vs duck typing vs `typing.Protocol`: nominal ABC vs structural
  protocol; use `@runtime_checkable` carefully (checks presence only).
- `numbers` ABC tower.

```python
from collections.abc import Mapping

class FrozenConfig(Mapping):
    def __init__(self, data): self._d = dict(data)
    def __getitem__(self, k): return self._d[k]
    def __iter__(self): return iter(self._d)
    def __len__(self): return len(self._d)

c = FrozenConfig({"a": 1})
print(c.get("b", 0), "a" in c, list(c.items()))
```

### Advanced — what to learn

- `ABC.register(cls)` for **virtual subclasses**; `__subclasshook__` for
  custom structural checks; the cost of ABC `isinstance` (cache, `ABCMeta`).
- `abc.ABCMeta` is a metaclass: it computes `__abstractmethods__`; so ABC
  adds a metaclass to your hierarchy (conflicts with other metaclasses).
- Abstract methods can have implementations callable through `super()`.
- Designing a plugin interface: ABC + registry + entry points (links to Modules 1.12, 1.18, 1.20).
- Typing: `Sequence[T]` vs `list[T]` in annotations — accept the widest
  ABC you need, return concrete types.
- Choosing between ABC, Protocol and plain duck typing, with a decision table.
- Testing ABCs: a minimal concrete subclass in the test suite.

### Common mistakes

- Making every interface an ABC when a `Protocol` or nothing would do.
- Forgetting that abstract methods are checked at **instantiation**, not definition.
- `isinstance(x, list)` where `isinstance(x, Sequence)` was meant.

### Self-check

1. Which three methods make a `Mapping` complete, and which methods do you get free?
2. What is the difference between `register()` and subclassing?
3. When is a `Protocol` the better choice than an ABC?

---

## Lesson 11 — `11-copying-pickling-and-object-lifecycle-hooks.md`

**Why it matters.** Copying, serialising and cleaning up objects are where
subtle bugs hide: shared mutable state after a "copy", unsafe pickles,
resources that never close, and finalizers that run at the wrong time.

### Basic — what to learn

- Assignment aliases; `copy.copy` (shallow) vs `copy.deepcopy` (recursive).
- Shallow copy shares nested mutable objects; deep copy copies the graph and
  handles cycles with a memo.
- The object lifecycle: `__new__` (creates) → `__init__` (initialises) →
  use → destruction (`__del__` / garbage collection).

```python
import copy
a = {"tags": ["x"]}
b = copy.copy(a)
c = copy.deepcopy(a)
a["tags"].append("y")
print(b["tags"], c["tags"])       # ['x', 'y']  ['x']
```

### Intermediate — what to learn

- Customising copy: `__copy__`, `__deepcopy__(self, memo)`, using `memo` to
  preserve shared references and cycles.
- `copy.replace()` (3.13+) and `dataclasses.replace` for "copy with changes".
- `__new__` for immutable subclasses (`int`, `str`, `tuple`), singletons,
  and factories; `__init__` then runs only if `__new__` returns an instance of the class.
- Pickle basics: `pickle.dumps/loads`, protocols, what is picklable
  (module-level functions and classes, not lambdas or local classes).
- `__getstate__` / `__setstate__` to exclude unpicklable fields (locks,
  open files, connections) and rebuild them.
- `__del__` basics: not guaranteed timing, avoid for resource management —
  use context managers (Module 1.9 lesson 03).

```python
import pickle, threading

class Cache:
    def __init__(self): self.data = {}; self.lock = threading.Lock()
    def __getstate__(self):
        state = self.__dict__.copy(); del state["lock"]; return state
    def __setstate__(self, state):
        self.__dict__.update(state); self.lock = threading.Lock()

clone = pickle.loads(pickle.dumps(Cache()))
```

### Advanced — what to learn

- `__reduce__` / `__reduce_ex__` and `copyreg`: how pickle reconstructs objects;
  how `copy` reuses the same protocol.
- **Security:** unpickling untrusted data executes arbitrary code. Alternatives:
  JSON, `msgpack`, Protocol Buffers, signed payloads (preview of Module 1.22).
- Versioning pickles; compatibility across class refactors; why pickles are not
  a storage format.
- `weakref.finalize` and `weakref.ref` callbacks as safer cleanup than `__del__`;
  interpreter-shutdown ordering issues; resurrected objects.
- `__init_subclass__` and `__set_name__` as class-creation lifecycle hooks
  (full coverage in Module 1.12).
- `__class_getitem__` for `MyClass[int]`; `__instancecheck__` / `__subclasscheck__` (awareness).
- Copy semantics of slotted and frozen dataclasses; `__replace__` protocol (3.13).
- Object identity and interning: `id`, `is`, small-int cache, string interning,
  and why you never rely on them.

### Common mistakes

- `copy.copy` on nested data and then mutating "the copy".
- Using `__del__` to close files or sockets.
- Pickling untrusted input.
- Pickling lambdas, nested functions or open handles.

### Self-check

1. What is the difference between `__new__` and `__init__`, and when must you override `__new__`?
2. Why is `__getstate__` needed for a class holding a `threading.Lock`?
3. Rewrite a `__del__`-based cleanup using `weakref.finalize` or a context manager.

---

## 4. Practice questions (`practice-questions.md`)

Organise the file by phase. Suggested mix: **~35 questions**.

| Phase | Question types |
| --- | --- |
| A | Predict output; fix `__eq__`/`__hash__` pair; write a `__repr__` that round-trips |
| B | Implement `Vector`/`Money`; add reflected and in-place operators; trace attribute lookup; build a validating descriptor |
| C | Measure slots vs dict with `tracemalloc`; predict a diamond MRO; unlinearisable hierarchy fix |
| D | Implement a `Mapping` from three methods; make a class picklable with a lock; replace `__del__` with a finalizer |

Add 5 **"what does this print and why?"** questions per phase that exercise
the lookup order, MRO, and copy semantics.

---

## 5. Module mini-project

**Build `datamodel_kit`**, a small tested library (in a `uv` project with
`pytest`, `ruff`, type hints) containing:

1. `Money` — immutable value object with hash, ordering, arithmetic, currency
   safety, formatting.
2. `TypedField` descriptors — validated, coerced fields with error messages
   (positive, bounded, regex-matching, enum-valued).
3. `FrozenRecord` — a slotted, hashable record base class using the descriptors.
4. `OrderedCatalog` — a `MutableMapping` + slice-aware sequence view.
5. `SerialisableMixin` — JSON round-trip and safe `__getstate__`.
6. A benchmark script comparing dict-based, slotted and dataclass records for
   1,000,000 objects (memory via `tracemalloc`, speed via `timeit`).

Acceptance criteria: ≥ 90 % branch coverage on the public API, `ruff` and
type checker clean, a README with usage examples, and a `DESIGN.md` that
documents every special method you implemented and why.

---

## 6. Completion checklist

- [ ] I can explain the eq/hash contract and why mutable hashed fields are dangerous.
- [ ] I can implement a total ordering and prove it satisfies the order laws.
- [ ] I can make a class behave as a sequence and a mapping, including slicing.
- [ ] I can overload operators with reflected and in-place variants and return `NotImplemented` correctly.
- [ ] I can explain a property as a descriptor and write my own descriptor.
- [ ] I can recite the attribute lookup order and use it to debug.
- [ ] I can measure — not assume — the benefit of `__slots__`.
- [ ] I can compute an MRO by hand and write a cooperative `super()` chain.
- [ ] I can design, test and critique a mixin, and say when to avoid one.
- [ ] I can choose between an ABC, a Protocol and duck typing.
- [ ] I can customise copy and pickle behaviour and explain the pickle security risk.
- [ ] I completed the mini-project and its tests.

**Next:** Module 1.12 — Metaprogramming and Dynamic Python, which builds on
descriptors, `__init_subclass__` and `type` to create classes programmatically.
