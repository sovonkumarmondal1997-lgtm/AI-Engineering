# Rich Comparison and Total Ordering

**Module:** Stage 1 — Programming & Computational Thinking → Module 11 — Advanced Python Data Model and Object Design  
**Target file:** `02-rich-comparison-and-total-ordering.md`  
**Python baseline:** Python 3.12+  
**Level:** Beginner → Intermediate → Advanced

## 1. Prerequisites and place in the roadmap

This lesson follows `01-dunder-methods-repr-str-eq-and-hash.md`. You should be comfortable with classes, tuples, equality, special methods, `NotImplemented`, and the equality/hash contract. It prepares you for the next lesson on container protocols and for later work with operator overloading and object design.

The project tree places this file at:

```text
Stage 1 — Programming & Computational Thinking/
└── 11-Advanced-Python-Data-Model-and-Object-Design/
    ├── 01-dunder-methods-repr-str-eq-and-hash.md
    ├── 02-rich-comparison-and-total-ordering.md  ← this lesson
    ├── 03-container-protocols-getitem-len-iter-and-contains.md
    └── roadmap-Advanced-Python-Data-Model-and-Object-Design.md
```

The module roadmap is the syllabus authority. This lesson expands its basic, intermediate, advanced, common-mistake, and self-check requirements without changing their intent.

## 2. Learning objectives

By the end, you should be able to:

1. Explain and implement `__lt__`, `__le__`, `__eq__`, `__ne__`, `__gt__`, and `__ge__`.
2. Explain how sorting, `min()`, `max()`, `bisect`, and `heapq` use comparisons.
3. Choose between a local `key=` function and a class-wide ordering contract.
4. Implement lexicographic, multi-field ordering safely with tuples and standard-library helpers.
5. Return `NotImplemented` for unsupported operand types and understand reflected dispatch.
6. Use `functools.total_ordering` and `dataclass(order=True)` deliberately, including their trade-offs.
7. Distinguish total orders from partial orders and test ordering laws.
8. Handle NaN and heterogeneous data deliberately rather than relying on accidental behavior.
9. Use `cmp_to_key` only when adapting a genuine legacy comparator is appropriate.
10. Test equality/order consistency and recognize how broken comparisons affect sorting and priority structures.

## 3. Intuition: what does “ordering” promise?

A comparison operator is a public contract. If a class says that one value is “less than” another, Python tools may rely on that claim to sort values, choose minima, maintain a heap, or locate insertion points in a sorted sequence.

Consider version numbers:

```python
(1, 9, 0) < (1, 10, 0)  # True: tuple comparison is lexicographic
```

Tuple comparison checks the first pair of unequal elements. It does **not** compare the tuples as sets, nor does it compare the lengths first. That makes tuples useful for ordering a sequence of fields in priority order.

A class should define an ordering when that order is intrinsic and unambiguous for its values. Use `key=` when the order is specific to a task, report, or caller. For example, a `Job` may have a natural priority order, but one report might sort jobs by creation time and another by owner.

## 4. The six rich comparison methods

| Method | Operator | Intended meaning |
|---|---|---|
| `__lt__(self, other)` | `a < b` | Strictly less than |
| `__le__(self, other)` | `a <= b` | Less than or equal |
| `__eq__(self, other)` | `a == b` | Equal under the class's value semantics |
| `__ne__(self, other)` | `a != b` | Not equal |
| `__gt__(self, other)` | `a > b` | Strictly greater than |
| `__ge__(self, other)` | `a >= b` | Greater than or equal |

Unlike arithmetic operators, comparison special methods are not guaranteed by the language to return `bool`; a user-defined method can return another object. Ordinary value classes should return booleans for supported comparisons. `NotImplemented` is a special dispatch signal, not a false result. In annotations, a method that explicitly returns this sentinel can use `bool | NotImplementedType` (from `types`) to describe both possibilities.

### Method-by-method reference

- **`__lt__` (`a < b`)**: strict ordering. This is the primary operation used by Python's built-in sorting machinery when no `key=` is supplied.
- **`__le__` (`a <= b`)**: non-strict ordering. Python does not infer it from `__lt__` and `__eq__` unless a helper such as `@total_ordering` generates it.
- **`__eq__` (`a == b`)**: equality according to the domain. Returning `NotImplemented` lets dispatch try the other operand and, if unresolved, equality uses its documented fallback behavior.
- **`__ne__` (`a != b`)**: inequality. If it is not explicitly supplied, `object`'s implementation delegates to `__eq__` and negates a supported result; if equality returns `NotImplemented`, that signal is preserved for dispatch. Explicit implementations should remain consistent with `__eq__`.
- **`__gt__` (`a > b`)**: greater-than. It is not simply a direct alias for `__lt__`; reflected dispatch may let the right operand's `__lt__` handle `a > b` when appropriate.
- **`__ge__` (`a >= b`)**: greater-than-or-equal. Implement it directly or generate it with a suitable helper.

Rich comparisons use reflected dispatch: for example, `a < b` can give `b.__gt__(a)` a chance if `a.__lt__(b)` returns `NotImplemented`. A strict subclass on the right may receive priority. Avoid hard-coding `False` for an operand type the method does not support, because that can prevent a meaningful reflected implementation from running.

### 4.1 Minimal `Version` implementation

This version class uses tuple comparison for ordering and equality. It accepts only other `Version` objects. The immutable tuple representation makes the ordering key stable.

```python
from __future__ import annotations

from functools import total_ordering
from types import NotImplementedType


@total_ordering
class Version:
    __slots__ = ("_parts",)

    def __init__(self, major: int, minor: int, patch: int) -> None:
        for name, value in (("major", major), ("minor", minor), ("patch", patch)):
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        object.__setattr__(self, "_parts", (major, minor, patch))

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("Version instances are immutable")

    def __eq__(self, other: object) -> bool | NotImplementedType:
        if not isinstance(other, Version):
            return NotImplemented
        return self._parts == other._parts

    def __lt__(self, other: object) -> bool | NotImplementedType:
        if not isinstance(other, Version):
            return NotImplemented
        return self._parts < other._parts

    def __repr__(self) -> str:
        return f"Version{self._parts!r}"


versions = [Version(1, 2, 0), Version(1, 0, 9), Version(2, 0, 0)]
print([v._parts for v in sorted(versions)])
print(Version(1, 0, 9) < Version(1, 2, 0))
print(Version(1, 2, 0) <= Version(1, 2, 0))
print(Version(1, 2, 0) == Version(1, 2, 0))
```

Expected output:

```text
[(1, 0, 9), (1, 2, 0), (2, 0, 0)]
True
True
True
```

`@total_ordering` generates the other ordering methods from `__eq__` and `__lt__`. Without it, this class would implement only `<` and `==` directly. This example is intentionally compact; a production value object may use `@dataclass(frozen=True, order=True)` instead, discussed below.

### 4.2 What happens if a method is absent?

Python does not automatically define every comparison in terms of `<` and `==`. If a needed comparison is unsupported, the operation may fall back to the other operand's reflected comparison method and eventually raise `TypeError` if dispatch cannot handle it. `==` and `!=` have a special identity-based fallback when neither operand supplies a result; ordering operators do not have an equivalent general fallback.

For a custom class, do not assume `a <= b` works merely because `a < b` and `a == b` work. Implement the needed methods explicitly or use `functools.total_ordering` / `dataclass(order=True)` when their semantics fit.

## 5. `NotImplemented`, operand types, and reflected dispatch

Return the singleton `NotImplemented` when the method does not know how to compare the other type. Python can then give the other operand a chance through its corresponding reflected method. If neither side supports the operation, Python raises `TypeError` for ordering.

```python
v = Version(1, 0, 0)

print(v == 3)  # False: equality ultimately falls back to identity comparison
try:
    print(v < 3)
except TypeError as exc:
    print(type(exc).__name__)
```

Expected output:

```text
False
TypeError
```

The equality result is `False` because the class returns `NotImplemented`, and neither side implements a meaningful cross-type equality; Python then applies its equality fallback. Returning `False` directly can be appropriate if the class explicitly owns the decision that values of other types are unequal, but `NotImplemented` is usually the better protocol choice for an operation that the class does not support.

### 5.1 Why `isinstance` is a design choice

The following snippet continues from the `Version` definition in Section 4.1; run the examples in order or copy that class into the same module.

The `Version` example uses `isinstance(other, Version)`, so a subclass is accepted. Whether that is correct depends on the equality contract. A subclass may add fields that change its meaning, making base/subclass comparisons asymmetric or surprising. If values must compare only when they have exactly the same concrete type, use `type(other) is type(self)` in both equality and ordering methods. Do not casually mix an exact-type check in one method with `isinstance` in another.

Python gives a strict subclass on the right a priority opportunity in rich comparison dispatch when its implementation is considered the more specific reflected operation. This is one reason to return `NotImplemented` when the current implementation cannot decide, rather than forcing a premature `False` result.

## 6. How built-in sorting and selection use comparisons

### 6.1 `sorted()` and `list.sort()`

The examples in this section continue to use `Version` from Section 4.1. For ordinary custom objects without a `key=`, Python's sorting API relies on `<` comparisons; it does not require all six rich comparison methods. `sorted(iterable)` returns a new list. `list.sort()` mutates the list in place and returns `None`.

```python
versions = [Version(1, 2, 0), Version(1, 0, 9), Version(1, 1, 0)]
ordered = sorted(versions)
print([v._parts for v in ordered])
print([v._parts for v in versions])

versions.sort()
print([v._parts for v in versions])
```

Expected output:

```text
[(1, 0, 9), (1, 1, 0), (1, 2, 0)]
[(1, 2, 0), (1, 0, 9), (1, 1, 0)]
[(1, 0, 9), (1, 1, 0), (1, 2, 0)]
```

Sorting is stable: elements with equal sort keys retain their relative input order. This is a documented property of Python's sorting API. Stability is useful when sorting records by one field after they have already been ordered by another.

### 6.2 `min()` and `max()`

`min()` and `max()` select using rich comparisons. In the CPython implementation checked for this lesson, `min()` compares candidates using `<` and `max()` using `>`; treat that operator-level detail as implementation behavior rather than a promise that every Python implementation must invoke only that method. Reflected rich-comparison dispatch may allow a class with only `__lt__` to participate in `max()` as well, but this depends on coherent dispatch and fallback behavior. Portable code should implement a coherent ordering or supply a `key=` function, which provides comparable keys and avoids requiring ordering on the original objects.

```python
items = [Version(1, 2, 0), Version(1, 0, 9), Version(2, 0, 0)]
print(min(items))
print(max(items))
```

Expected output:

```text
Version(1, 0, 9)
Version(2, 0, 0)
```

Do not infer that every pairwise relation is checked or validated. These functions assume the comparisons give a coherent answer; they are not order-law validators.

## 7. Choose `key=` or class ordering

### 7.1 Prefer `key=` for task-specific orderings

```python
from dataclasses import dataclass
from operator import attrgetter

@dataclass(frozen=True)
class Job:
    name: str
    priority: int
    created_at: int

jobs = [
    Job("batch-A", 2, 100),
    Job("urgent", 1, 120),
    Job("batch-B", 2, 90),
]

print([job.name for job in sorted(jobs, key=attrgetter("priority", "created_at"))])
```

Expected output:

```text
['urgent', 'batch-B', 'batch-A']
```

The key tuple sorts first by priority ascending and then by creation timestamp ascending. It does not make `Job` globally orderable. This is often the safer choice when there are several reasonable orderings.

### 7.2 `operator.attrgetter` and `operator.itemgetter`

```python
from operator import attrgetter, itemgetter

records = [
    {"name": "A", "score": 8},
    {"name": "B", "score": 10},
    {"name": "C", "score": 8},
]
print([r["name"] for r in sorted(records, key=itemgetter("score", "name"))])

class Row:
    def __init__(self, group: str, index: int) -> None:
        self.group = group
        self.index = index

rows = [Row("b", 1), Row("a", 2), Row("a", 1)]
print([(r.group, r.index) for r in sorted(rows, key=attrgetter("group", "index"))])
```

Expected output:

```text
['A', 'C', 'B']
[('a', 1), ('a', 2), ('b', 1)]
```

`itemgetter` retrieves mapping keys or sequence indices. `attrgetter` retrieves attributes. Both can retrieve multiple fields and return a tuple-like key. They are clear, reusable alternatives to small lambdas.

### 7.3 Mixed ascending and descending directions

A tuple key sorts all tuple components ascending. Negating a numeric field reverses that numeric field, but it is not a universal technique for strings, arbitrary objects, or values where negation is not defined.

For mixed directions, use stable multi-pass sorting from the least significant key to the most significant key:

```python
from operator import itemgetter

rows = [
    {"team": "red", "score": 8, "name": "Mira"},
    {"team": "blue", "score": 10, "name": "Ari"},
    {"team": "red", "score": 10, "name": "Noah"},
    {"team": "blue", "score": 10, "name": "Bea"},
]
rows.sort(key=itemgetter("name"))                 # tertiary: name ascending
rows.sort(key=itemgetter("score"), reverse=True)  # secondary: score descending
rows.sort(key=itemgetter("team"))                 # primary: team ascending
print([(r["team"], r["score"], r["name"]) for r in rows])
```

Expected output:

```text
[('blue', 10, 'Ari'), ('blue', 10, 'Bea'), ('red', 10, 'Noah'), ('red', 8, 'Mira')]
```

Because sorting is stable, later passes preserve the relative order established by earlier passes among ties. Apply passes in reverse priority order: least important field first, most important field last.

## 8. Multi-field ordering with tuples

Tuple comparison is lexicographic and often the most maintainable implementation for a value class:

```python
from dataclasses import dataclass
from types import NotImplementedType

@dataclass(frozen=True)
class Endpoint:
    host: str
    port: int

    def sort_key(self) -> tuple[str, int]:
        return (self.host, self.port)

    def __lt__(self, other: object) -> bool | NotImplementedType:
        if not isinstance(other, Endpoint):
            return NotImplemented
        return self.sort_key() < other.sort_key()
```

For custom equality and ordering, use the same logical fields unless the domain explicitly requires different semantics. A class where `a == b` but `a < b` or `b < a` is true is usually incoherent for sorting, binary search, and heaps.

## 9. `functools.total_ordering`

`@total_ordering` is a class decorator. Define `__eq__` and at least one of `__lt__`, `__le__`, `__gt__`, or `__ge__`; the decorator supplies the other ordering methods that are missing. It does not generate `__eq__`.

```python
from functools import total_ordering
from types import NotImplementedType

@total_ordering
class Priority:
    _RANK = {"low": 1, "medium": 2, "high": 3}

    def __init__(self, name: str) -> None:
        if name not in self._RANK:
            raise ValueError(f"unknown priority: {name}")
        self.name = name

    def _key(self) -> int:
        return self._RANK[self.name]

    def __eq__(self, other: object) -> bool | NotImplementedType:
        if not isinstance(other, Priority):
            return NotImplemented
        return self._key() == other._key()

    def __lt__(self, other: object) -> bool | NotImplementedType:
        if not isinstance(other, Priority):
            return NotImplemented
        return self._key() < other._key()

    def __repr__(self) -> str:
        return f"Priority({self.name!r})"

print(Priority("low") < Priority("high"))
print(Priority("medium") >= Priority("low"))
print(sorted([Priority("high"), Priority("low"), Priority("medium")]))
```

Expected output:

```text
True
True
[Priority('low'), Priority('medium'), Priority('high')]
```

This class is intentionally not hashable by a custom value hash. Since it defines `__eq__` and does not define `__hash__`, Python normally sets `__hash__ = None`; that avoids accidentally hashing mutable state. If instances need to be hashable, make the equality-relevant state immutable and implement a matching hash, or use an appropriate frozen dataclass.

### 9.1 Trade-offs

- **Benefit:** fewer repetitive methods and a compact implementation.
- **Cost:** generated comparisons can be slower than carefully written explicit methods, and tracebacks may pass through generated methods.
- **Requirement:** the chosen primitive comparison and equality must already be coherent. The decorator cannot repair a bad ordering model.
- **Decision:** use it for ordinary domain objects when simplicity matters. For a heavily exercised hot path, profile first; write explicit methods only when there is a measured reason or a semantic need.

## 10. `dataclass(order=True)` and `field(compare=False)`

A dataclass with `order=True` generates ordering methods based on fields in declaration order. It also generates equality when `eq=True` (the default). Dataclass ordering compares instances as tuples of their comparison-enabled fields and requires the operands to be instances of the identical class, not merely compatible subclasses.

```python
from dataclasses import dataclass, field

@dataclass(frozen=True, order=True)
class Task:
    priority: int
    sequence: int
    description: str = field(compare=False)

items = [
    Task(2, 10, "later batch"),
    Task(1, 30, "urgent"),
    Task(1, 20, "urgent earlier"),
]
print(sorted(items))
print(Task(1, 20, "first label") == Task(1, 20, "different label"))
```

Expected output:

```text
[Task(priority=1, sequence=20, description='urgent earlier'), Task(priority=1, sequence=30, description='urgent'), Task(priority=2, sequence=10, description='later batch')]
True
```

`description` is excluded from equality and ordering because `compare=False`. This means two tasks with the same priority and sequence compare equal even if their descriptions differ. Use this only when that is the intended domain contract. `frozen=True` prevents ordinary attribute reassignment and makes a generated hash possible when the dataclass settings permit it; it does not make nested mutable objects deeply immutable.

Do not use `order=True` merely because sorting is needed once. A `key=` is more explicit when the class has multiple legitimate orderings.

## 11. Comparison laws: total and partial orders

A sorting relation should behave consistently. For a non-strict order `<=`, the usual total-order properties are:

- **Reflexivity:** `a <= a`.
- **Antisymmetry:** if `a <= b` and `b <= a`, then `a == b` under the ordering's equality semantics.
- **Transitivity:** if `a <= b` and `b <= c`, then `a <= c`.
- **Totality (comparability):** for every `a` and `b`, `a <= b` or `b <= a` (or both).

For strict `<`, the corresponding expectations are irreflexivity (`not a < a`), asymmetry (if `a < b`, then not `b < a`), and transitivity. A total order additionally makes any two values comparable. The equality operator should agree with ordering: ideally `a == b` exactly when neither `a < b` nor `b < a` is true, subject to the domain's documented semantics.

### 11.1 A non-transitive comparator can mislead sorting

This deliberately broken rock-paper-scissors relation has a cycle: rock beats scissors, scissors beats paper, and paper beats rock. Here “less than” means “comes before” in a cycle, not a valid total order.

```python
from types import NotImplementedType

class Cyclic:
    _NEXT = {"rock": "scissors", "scissors": "paper", "paper": "rock"}

    def __init__(self, name: str) -> None:
        self.name = name

    def __lt__(self, other: object) -> bool | NotImplementedType:
        if not isinstance(other, Cyclic):
            return NotImplemented
        return self._NEXT[self.name] == other.name

    def __repr__(self) -> str:
        return f"Cyclic({self.name!r})"

cycle = [Cyclic("rock"), Cyclic("paper"), Cyclic("scissors")]
print([x.name for x in sorted(cycle)])
```

On the CPython 3.13.5 environment used to check this lesson, the snippet prints:

```text
['scissors', 'paper', 'rock']
```

That output is an observation for this input and runtime, not a correctness guarantee for the relation or a portable result to rely on. The important point is that sorting is not required to detect or reject the cycle. It can return a list even though no ordering can satisfy all comparisons. The result can depend on input arrangement and the implementation's comparison sequence. Do not use a broken comparator in production and do not treat a successful return as proof of valid ordering.

### 11.2 Partial orders: sets are the classic example

Set `<` means proper-subset, not “sorts before.” Some sets are incomparable:

```python
print({1} < {1, 2})
print({1} < {2})
print({1} <= {1})
```

Expected output:

```text
True
False
True
```

The sets `{1}` and `{2}` are incomparable under subset ordering. Therefore, sorting sets does not produce a meaningful general ascending order, even if `sorted()` returns a list. Use a deliberate key such as `(len(s), sorted(s))` when that is the order your application needs and the elements are mutually sortable.

## 12. Floating-point `NaN`

IEEE floating-point NaN is unordered: comparisons such as `nan < x`, `nan > x`, and `nan == nan` are false. That breaks ordinary assumptions used by sorting and equality-based lookup. Python's sorting algorithm does not validate that all values form a total order; a list containing NaNs can therefore produce results that are surprising or not meaningful as a numeric sort. Avoid claiming a universal output for mixed NaN input unless the exact input, key, and behavior are part of a tested application contract.

```python
import math

nan = float("nan")
print(nan == nan)
print(nan < 1.0)
print(nan > 1.0)

values = [3.0, nan, 1.0]
print([math.isnan(x) for x in values])
```

Expected output:

```text
False
False
False
[False, True, False]
```

For predictable numeric sorting, decide where NaNs belong and encode that policy in a key:

```python
import math


def nan_last_key(value: float) -> tuple[bool, float]:
    return (math.isnan(value), 0.0 if math.isnan(value) else value)

nan = float("nan")
values = [3.0, nan, 1.0]
print(["nan" if math.isnan(x) else x for x in sorted(values, key=nan_last_key)])
```

Expected output:

```text
[1.0, 3.0, 'nan']
```

The boolean field puts finite numbers first (`False`) and NaNs last (`True`). The numeric second field keeps the key tuple's types consistent. This policy is explicit; it is not an intrinsic universal ordering of NaN.

## 13. Heterogeneous values

Python 3 does not define a general ordering between unrelated types such as integers and strings:

```python
try:
    print(1 < "a")
except TypeError as exc:
    print(type(exc).__name__)
```

Expected output:

```text
TypeError
```

If heterogeneous values must be sorted, create a deliberate normalization key. For example, if the input is restricted to integers and strings:

```python
def mixed_key(value: int | str) -> tuple[int, int | str]:
    if isinstance(value, int) and not isinstance(value, bool):
        return (0, value)
    if isinstance(value, str):
        return (1, value.casefold())
    raise TypeError(f"unsupported value: {type(value).__name__}")

values: list[int | str] = ["Pear", 10, "apple", 2]
print(sorted(values, key=mixed_key))
```

Expected output:

```text
[2, 10, 'apple', 'Pear']
```

The first tuple element groups integers before strings; the second sorts within each group. `bool` is a subclass of `int`, so this example explicitly rejects it as an integer value. Extend the policy for any additional types rather than relying on arbitrary cross-type comparisons.

## 14. Legacy comparator functions and `cmp_to_key`

A comparator returns a negative number when `a` should come before `b`, zero when they are equivalent for sorting, and a positive number when `a` should come after `b`. Python 3 sorting APIs use key functions, not a direct `cmp=` parameter. `functools.cmp_to_key` adapts a legacy comparator into a key object.

```python
from functools import cmp_to_key


def compare_case_insensitive(a: str, b: str) -> int:
    left, right = a.casefold(), b.casefold()
    return (left > right) - (left < right)

words = ["pear", "Apple", "banana"]
print(sorted(words, key=cmp_to_key(compare_case_insensitive)))
```

Expected output:

```text
['Apple', 'banana', 'pear']
```

Prefer `key=str.casefold` for this specific case because it is simpler and avoids repeatedly expressing pairwise comparisons. `cmp_to_key` is appropriate when integrating an existing comparator, porting legacy code, or implementing a domain comparison that cannot be expressed cleanly as a normal key. The comparator still must be consistent; the adapter does not fix a non-transitive relation.

## 15. Equality and ordering must agree

A common defect is implementing equality on one field but ordering on a different field without a domain reason. Consider a `Record` that says two objects are equal by identifier but sorts by timestamp. It may be possible for `a == b` and also `a < b`, which violates the expected relationship between equality and ordering and can cause confusing results in bisect-based workflows.

Choose and document one of these designs:

1. **Same semantic fields:** equality and ordering use the same key tuple. This is the default recommendation for value objects.
2. **Different but intentional semantics:** document exactly why the concepts differ, and do not assume generic sorting/searching tools interpret equality as ordering-equivalence.
3. **No intrinsic ordering:** do not implement rich ordering; use caller-supplied `key=` functions.

For a well-behaved total order, if both `a < b` and `b < a` are false, `a` and `b` should be equivalent under ordering. For many value objects, that equivalence should match `a == b`.

## 16. `bisect` and `heapq`

Both modules depend on consistent `<` behavior, but they use it for different purposes:

- `bisect` finds an insertion point in a sequence that is already sorted according to the same ordering. It does not sort or validate the sequence for you. If the sequence was sorted under a different key/order, the insertion point may be wrong.
- `heapq` maintains a heap invariant using `<` comparisons. A heap is not a fully sorted list; it guarantees access to the smallest item according to its comparison relation, assuming that relation is coherent.

```python
from bisect import bisect_left
import heapq

numbers = [1, 3, 5, 7]
print(bisect_left(numbers, 4))

heap = [5, 1, 4]
heapq.heapify(heap)
print(heapq.heappop(heap))
```

Expected output:

```text
2
1
```

For custom objects, ensure their `<` method and any `key=`-derived order used to prepare the data are consistent. `bisect`'s key support has a specific API detail: when `key=` is supplied, it is applied to elements in the sequence, but the searched `x` is expected to already be in key form. Check the Python version's `bisect` documentation when using that argument in production.

## 17. Practical applications in data engineering and AI systems

### 17.1 Job priority queues

A scheduler may need to order jobs by priority and then by enqueue sequence. A frozen dataclass is often appropriate:

```python
from dataclasses import dataclass, field

@dataclass(order=True, frozen=True)
class QueueItem:
    priority_rank: int
    sequence: int
    payload: str = field(compare=False)
```

The payload is excluded from comparisons so arbitrary payload types do not accidentally participate in ordering. The sequence field provides deterministic tie-breaking among equal priorities. For `heapq`, lower numeric ranks are popped first; if higher priority should be served first, encode ranks accordingly or use a deliberate reverse-priority scheme.

### 17.2 Data pipeline records

Use `key=attrgetter("event_time", "partition", "offset")` to sort event records for a batch when the order is specific to that pipeline. This keeps ordering policy visible at the call site and avoids making the record class globally sortable for unrelated use cases.

### 17.3 Model evaluation results

Use a key that handles missing or invalid metrics explicitly. Do not assume NaN scores sort meaningfully. For example, place invalid scores last and then sort valid scores by a defined metric. Document tie-breaking rules so experiment reports remain reproducible.

### 17.4 Semantic versions

Compare parsed numeric components, not raw version strings: lexical string ordering can put `"1.10"` before `"1.2"`. If the domain follows a full standard such as Semantic Versioning, implement its pre-release and build-metadata rules rather than assuming a three-integer tuple is a complete implementation.

## 18. Common mistakes and failure modes

1. **Assuming sorting needs all six methods.** For ordinary `sorted()` / `list.sort()` comparisons, `<` is the key rich comparison; `key=` can bypass object ordering by comparing keys instead.
2. **Defining `__eq__` and forgetting hash behavior.** Python normally makes the class unhashable when `__eq__` is defined and `__hash__` is not. Do not add a hash unless equality-relevant state is stable.
3. **Returning `False` for every unsupported type.** This can suppress the other operand's opportunity to handle the operation. Prefer `NotImplemented` when the operation is unsupported.
4. **Mixing equality and ordering keys.** This can make equal values order differently or distinct values indistinguishable to ordering-based algorithms.
5. **Assuming tuple keys solve every mixed-direction sort.** They sort each component ascending; use stable passes or a carefully designed key for mixed directions.
6. **Assuming sets have a total order.** Set `<` means proper subset, which is a partial order; `sorted(sets)` is not generally a meaningful ascending arrangement.
7. **Ignoring NaN.** NaN is not equal to itself and is unordered; define a sorting policy explicitly.
8. **Relying on Python 2-style cross-type ordering.** In Python 3, unrelated types generally cannot be ordered; normalize values with an explicit key.
9. **Using `total_ordering` without profiling or without coherent primitives.** It improves maintainability but generated methods may add overhead and cannot repair inconsistent semantics.
10. **Using `dataclass(order=True)` by habit.** It imposes declaration-order tuple semantics and identical-class comparisons; ensure this is truly the domain's natural order.
11. **Assuming `bisect` checks sortedness.** It does not; the input must already be sorted under the same ordering policy.
12. **Assuming `heapq` produces a fully sorted list.** It maintains a heap invariant, not complete sorted order.
13. **Assuming successful `sorted()` proves the comparator is valid.** Python does not generally check reflexivity, transitivity, or totality; broken relations may return results without raising.
14. **Using `cmp_to_key` where a key is simpler.** Prefer a direct key unless adapting a real comparator is needed.
15. **Comparing money using binary floating-point values.** For monetary values, prefer `Decimal` with a defined quantization policy or integer minor units; float rounding and NaN complicate ordering.

## 19. Debugging checklist

When ordering fails or output looks suspicious:

1. Reproduce with the smallest pair of values that fails.
2. Inspect `a == b`, `a < b`, `b < a`, and (if implemented) `a <= b`, `b <= a`.
3. Check unsupported operand types and whether methods return `NotImplemented`.
4. Check that equality and ordering use compatible fields and type rules.
5. Check that values do not mutate in ways that change their comparison result while stored in a heap or while a sequence is assumed sorted.
6. Check NaN, `None`, mixed types, missing fields, and duplicate keys.
7. Verify that the list passed to `bisect` is sorted using the same policy.
8. For a comparator, test reflexivity/irreflexivity, antisymmetry/asymmetry, transitivity, and totality on representative triples.
9. For `total_ordering`, confirm `__eq__` and the one primitive ordering method are both correct before investigating generated methods.
10. For a performance concern, benchmark realistic data and profile before replacing `total_ordering` with handwritten methods.

## 20. Tests with pytest

Save the following as `test_rich_comparison.py`. It is a self-contained test module and deliberately checks laws and public behavior, not private implementation details alone.

```python
from __future__ import annotations

from dataclasses import dataclass, field
from functools import total_ordering
import math
from types import NotImplementedType

import pytest


@total_ordering
class Version:
    __slots__ = ("parts",)

    def __init__(self, major: int, minor: int, patch: int) -> None:
        parts = (major, minor, patch)
        if any(not isinstance(x, int) or isinstance(x, bool) or x < 0 for x in parts):
            raise ValueError("version parts must be non-negative integers")
        object.__setattr__(self, "parts", parts)

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("Version instances are immutable")

    def __eq__(self, other: object) -> bool | NotImplementedType:
        if not isinstance(other, Version):
            return NotImplemented
        return self.parts == other.parts

    def __lt__(self, other: object) -> bool | NotImplementedType:
        if not isinstance(other, Version):
            return NotImplemented
        return self.parts < other.parts

    def __repr__(self) -> str:
        return f"Version{self.parts!r}"


@dataclass(order=True, frozen=True)
class Task:
    priority: int
    sequence: int
    description: str = field(compare=False)


def test_version_lexicographic_order_and_sorting() -> None:
    versions = [Version(1, 2, 0), Version(1, 0, 9), Version(2, 0, 0)]
    assert [v.parts for v in sorted(versions)] == [(1, 0, 9), (1, 2, 0), (2, 0, 0)]
    assert min(versions).parts == (1, 0, 9)
    assert max(versions).parts == (2, 0, 0)


def test_total_ordering_generated_relations() -> None:
    low, same_low, high = Version(1, 0, 0), Version(1, 0, 0), Version(2, 0, 0)
    assert low == same_low
    assert low <= same_low
    assert low >= same_low
    assert low < high
    assert high > low
    assert low != high
    assert low <= high
    assert high >= low


def test_unsupported_operands() -> None:
    version = Version(1, 0, 0)
    assert (version == 5) is False
    with pytest.raises(TypeError):
        _ = version < 5


def test_invalid_version_components_are_rejected() -> None:
    with pytest.raises(ValueError):
        Version(-1, 0, 0)
    with pytest.raises(ValueError):
        Version(True, 0, 0)


def test_version_ordering_state_is_immutable() -> None:
    version = Version(1, 2, 3)
    with pytest.raises(AttributeError):
        version.parts = (9, 9, 9)


def test_dataclass_compare_false_excludes_description() -> None:
    a = Task(1, 10, "first")
    b = Task(1, 10, "different description")
    assert a == b
    assert not (a < b)
    assert not (b < a)


def test_order_laws_for_sample_values() -> None:
    values = [Version(0, 9, 9), Version(1, 0, 0), Version(1, 0, 1)]
    for a in values:
        assert not (a < a)  # strict irreflexivity
        for b in values:
            if a < b:
                assert not (b < a)  # asymmetry
            if not (a < b) and not (b < a):
                assert a == b  # this class uses the same key for equality/order
            for c in values:
                if a < b and b < c:
                    assert a < c  # transitivity


def test_nan_policy_key_puts_nan_last() -> None:
    values = [3.0, float("nan"), 1.0]
    ordered = sorted(values, key=lambda x: (math.isnan(x), 0.0 if math.isnan(x) else x))
    assert ordered[0] == 1.0
    assert ordered[1] == 3.0
    assert math.isnan(ordered[2])


def test_equal_items_are_stably_sorted_by_key() -> None:
    values = [(1, "first"), (0, "zero"), (1, "second")]
    ordered = sorted(values, key=lambda pair: pair[0])
    assert ordered == [(0, "zero"), (1, "first"), (1, "second")]


def test_list_sort_and_unsupported_relational_operators() -> None:
    values = [Version(2, 0, 0), Version(1, 0, 0)]
    result = values.sort()
    assert result is None
    assert [value.parts for value in values] == [(1, 0, 0), (2, 0, 0)]
    with pytest.raises(TypeError):
        _ = Version(1, 0, 0) >= 5
    with pytest.raises(TypeError):
        _ = Version(1, 0, 0) > 5


def test_cyclic_relation_violates_transitivity_but_sort_returns() -> None:
    class Cyclic:
        _NEXT = {"rock": "scissors", "scissors": "paper", "paper": "rock"}

        def __init__(self, name: str) -> None:
            self.name = name

        def __lt__(self, other: object) -> bool | NotImplementedType:
            if not isinstance(other, Cyclic):
                return NotImplemented
            return self._NEXT[self.name] == other.name

    rock, scissors, paper = Cyclic("rock"), Cyclic("scissors"), Cyclic("paper")
    assert rock < scissors
    assert scissors < paper
    assert not (rock < paper)
    assert len(sorted([rock, paper, scissors])) == 3
```

Run in an environment with Python 3.12+ and pytest installed:

```bash
python -m pytest -q test_rich_comparison.py
```

Expected test result when run with a compatible environment:

```text
11 passed
```

Verification note: this test module was executed in the available Python 3.13.5 environment with pytest 9.0.2 and passed all 11 tests. Python 3.12 was not available in that environment, so this is not a direct 3.12 run. A test suite cannot prove the laws for every possible object; it checks representative values and regressions. Expand generated/property-based tests when the domain has a large state space.

## 21. Graduated exercises

### Exercise 1 — Beginner: compare versions

Implement a `Version` class that stores `(major, minor, patch)`, supports equality and `<`, and sorts correctly. Unsupported ordering against an integer must raise `TypeError`.

### Exercise 2 — Beginner/intermediate: choose a key

Given records with `team`, `score`, and `name`, sort by team ascending, score descending, then name ascending. Preserve stable order when all three fields tie.

### Exercise 3 — Intermediate: `total_ordering`

Implement a `Priority` value with `low < medium < high`. Explain which methods you implement directly and which are generated. Explain why you should not hash mutable priority state by default.

### Exercise 4 — Intermediate: dataclass ordering

Create a frozen `Task` dataclass ordered by `priority` then `sequence`, while excluding `payload` from comparison. Demonstrate that two tasks with equal comparison fields compare equal despite different payloads.

### Exercise 5 — Advanced: audit a relation

Create three values `a`, `b`, and `c` and test whether `a < b`, `b < c`, and `a < c` are consistent. Explain why sorting successfully does not prove transitivity.

### Exercise 6 — Advanced: NaN policy

Write a key function that puts NaN values last and finite values in ascending order. Test a list containing at least two finite values and one NaN.

### Exercise 7 — Advanced: legacy comparator

Write a comparator that orders strings case-insensitively, adapt it with `cmp_to_key`, and explain why `key=str.casefold` is simpler for this specific task.

## 22. Worked solutions

### Solution 1 — Version

The complete `Version` implementation in Section 4.1 is the reference solution. It compares the tuple of numeric components lexicographically and returns `NotImplemented` for unsupported operand types. The `total_ordering` decorator supplies the missing relational methods.

### Solution 2 — Mixed sort directions

```python
from operator import itemgetter

records = [
    {"team": "red", "score": 8, "name": "Mira"},
    {"team": "blue", "score": 10, "name": "Ari"},
    {"team": "red", "score": 10, "name": "Noah"},
    {"team": "blue", "score": 10, "name": "Bea"},
]
records.sort(key=itemgetter("name"))
records.sort(key=itemgetter("score"), reverse=True)
records.sort(key=itemgetter("team"))
print([(r["team"], r["score"], r["name"]) for r in records])
```

Expected output:

```text
[('blue', 10, 'Ari'), ('blue', 10, 'Bea'), ('red', 10, 'Noah'), ('red', 8, 'Mira')]
```

### Solution 3 — Priority

Section 9 provides a working implementation. Implement `__eq__` and `__lt__`; `@total_ordering` generates the missing order methods. Since the sample's `name` is mutable and equality depends on its rank, a custom hash based on rank would be unsafe if the name changed after insertion into a set or dictionary. Either keep the object unhashable, or use an immutable representation and a matching hash.

### Solution 4 — Task

```python
from dataclasses import dataclass, field

@dataclass(frozen=True, order=True)
class Task:
    priority: int
    sequence: int
    payload: object = field(compare=False)

print(Task(1, 2, "a") == Task(1, 2, "b"))
```

Expected output:

```text
True
```

### Solution 5 — transitivity

For any valid strict ordering, if `a < b` and `b < c`, then `a < c` must hold. The `Cyclic` example in Section 11.1 intentionally violates this law. `sorted()` does not generally inspect every triple to verify transitivity, so the call may return without an exception even though the comparator is invalid.

### Solution 6 — NaN last

```python
import math

def nan_last_key(x: float) -> tuple[bool, float]:
    return (math.isnan(x), 0.0 if math.isnan(x) else x)

values = [float("nan"), 2.0, 1.0]
ordered = sorted(values, key=nan_last_key)
print(["nan" if math.isnan(x) else x for x in ordered])
```

Expected output:

```text
[1.0, 2.0, 'nan']
```

### Solution 7 — comparator adapter

Section 14 contains the full `compare_case_insensitive` function and its use with `cmp_to_key`. For a simple case-insensitive ordering, `sorted(words, key=str.casefold)` is clearer and uses a direct key function rather than adapting a pairwise comparator.

## 23. Roadmap self-check answers

### 1. Which single method does `sorted()` require?

For custom objects sorted without a `key=`, the sorting API relies on `<`, which dispatches to `__lt__` (with Python's rich-comparison reflected dispatch rules). If a `key=` is supplied, the sort compares the produced keys instead, so the original objects do not need to implement ordering.

### 2. Why does `total_ordering` need `__eq__` as well?

The decorator needs equality to derive the missing inclusive and reverse comparisons consistently from one primitive ordering method. It does not invent the domain's equality semantics; the class must supply `__eq__` itself.

### 3. Demonstrate a comparison that breaks transitivity and show what `sorted` does.

The `Cyclic` example in Section 11.1 defines a rock-paper-scissors cycle. It violates transitivity by design. `sorted()` may return a list without raising because it assumes comparisons form a coherent order and does not perform a general transitivity audit. The exact returned order is not a valid guarantee of a meaningful ordering and can depend on input arrangement and comparison sequence.

## 24. Final checklist

- [ ] The six rich comparison methods and their operators are understood.
- [ ] Sorting and selection behavior is understood, including the role of `<` and `key=`.
- [ ] `NotImplemented`, unsupported types, and reflected dispatch are handled deliberately.
- [ ] Equality and ordering use compatible semantics.
- [ ] Tuple keys, `attrgetter`, `itemgetter`, stable sorting, and mixed directions are understood.
- [ ] `total_ordering` and `dataclass(order=True)` are used only when their contracts fit.
- [ ] Total-order laws and partial-order limitations are understood.
- [ ] NaN and heterogeneous values have explicit policies.
- [ ] `cmp_to_key` is reserved for appropriate comparator adaptation.
- [ ] `bisect` input ordering and `heapq` comparison requirements are understood.
- [ ] The pytest examples pass in the target Python environment before being used as a project baseline.
- [ ] The comparator is not assumed valid merely because `sorted()` returns.

## 25. References

Use the documentation matching the Python version deployed by your project:

- Python Language Reference — data model, rich comparison methods: <https://docs.python.org/3/reference/datamodel.html#object.__lt__>
- Python Standard Library — `functools.total_ordering` and `cmp_to_key`: <https://docs.python.org/3/library/functools.html>
- Python Standard Library — `dataclasses`: <https://docs.python.org/3/library/dataclasses.html>
- Python Standard Library — sorting HOWTO: <https://docs.python.org/3/howto/sorting.html>
- Python Standard Library — `bisect`: <https://docs.python.org/3/library/bisect.html>
- Python Standard Library — `heapq`: <https://docs.python.org/3/library/heapq.html>
