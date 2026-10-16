# Rich Comparison and Total Ordering in Python

**Stage:** Stage 1 — Programming & Computational Thinking  
**Module:** 11 — Advanced Python Data Model and Object Design  
**Lesson:** 02 — Rich Comparison and Total Ordering  
**Target:** Python 3.12+  
**Learning style:** Theory → runnable examples → tests → production case study → exercises → review

> This lesson follows `roadmap-Advanced-Python-Data-Model-and-Object-Design.md`, Lesson 02. It covers the roadmap's basic, intermediate, and advanced objectives, common mistakes, and self-check questions. It assumes you can write simple classes and functions and have met `__eq__` in Lesson 01.

## Learning outcomes

By the end, you should be able to:

- Explain the six rich comparison methods: `__lt__`, `__le__`, `__eq__`, `__ne__`, `__gt__`, and `__ge__`.
- Implement ordering for a value object without accidentally accepting unrelated types.
- Explain why `sorted()` and `list.sort()` normally need only `<`, and when a `key=` function is better than class-level ordering.
- Use `functools.total_ordering`, understand what it generates, and recognize its runtime trade-off.
- Use `NotImplemented` correctly to allow Python's comparison dispatch to work.
- Use tuple comparisons, dataclass ordering, `field(compare=False)`, `operator.attrgetter`, and `operator.itemgetter`.
- Explain sorting stability, multi-key sorting, total-order laws, partial orders, NaN, and heterogeneous values.
- Apply ordering safely with `bisect` and `heapq`, with tests for invariants and edge cases.

## 1. What is rich comparison?

A comparison asks a question about two objects: are they equal, different, less than, or greater than one another? Python calls these **rich comparisons** because objects can customize the behavior of each comparison operator through special methods.

| Expression | Special method | Meaning |
|---|---|---|
| `a < b` | `a.__lt__(b)` | less than |
| `a <= b` | `a.__le__(b)` | less than or equal to |
| `a == b` | `a.__eq__(b)` | equal |
| `a != b` | `a.__ne__(b)` | not equal |
| `a > b` | `a.__gt__(b)` | greater than |
| `a >= b` | `a.__ge__(b)` | greater than or equal to |

Python's operator syntax performs dispatch; you usually write `a < b`, not `a.__lt__(b)` directly. The methods are part of the data model, like `__repr__` and `__hash__` from the previous lesson.

### Why this matters in data engineering

Ordering affects more than presentation. It can decide:

- which event is processed first in a priority queue;
- whether a record is inserted at the correct position in a sorted batch;
- which version is considered newer;
- how pagination and merge operations behave;
- whether `bisect` can find an insertion point correctly;
- whether a scheduler or retry system consistently chooses the next job.

A comparator that is inconsistent may not raise an exception. It can instead produce a misleading order, so correctness must be designed and tested.

## 2. Start with built-in comparisons

```python
print(3 < 8)          # True
print(3 <= 3)         # True
print("alpha" < "beta")  # True: lexicographic string order
print((1, 4) < (2, 0))    # True: tuple order is lexicographic
```

For sequences such as tuples, Python compares element by element. It stops at the first pair of unequal elements. If all compared elements are equal, the shorter tuple is smaller.

```python
print((2, 1, 9) < (2, 3, 0))  # True: 1 < 3 decides the result
print((2, 1) < (2, 1, 0))     # True: equal prefix, shorter tuple first
```

This behavior is useful for a value object's ordering key, for example `(major, minor, patch)` for a software version or `(priority, created_at, job_id)` for a job queue.

## 3. Basic implementation: a `Version` value object

A version is naturally ordered by major, then minor, then patch. Implement `__lt__` to compare the tuple of components.

```python
class Version:
    def __init__(self, major: int, minor: int, patch: int) -> None:
        for name, value in (("major", major), ("minor", minor), ("patch", patch)):
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        self.major = major
        self.minor = minor
        self.patch = patch

    def _key(self) -> tuple[int, int, int]:
        return (self.major, self.minor, self.patch)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self._key() < other._key()

    def __repr__(self) -> str:
        return f"Version({self.major}, {self.minor}, {self.patch})"

versions = [Version(1, 2, 0), Version(1, 0, 9), Version(2, 0, 0)]
print(sorted(versions))
# [Version(1, 0, 9), Version(1, 2, 0), Version(2, 0, 0)]
```

`sorted()` creates a new list. `list.sort()` sorts a list in place and returns `None`.

```python
versions = [Version(1, 2, 0), Version(1, 0, 9)]
ordered = sorted(versions)
assert versions[0]._key() == (1, 2, 0)  # original list is unchanged
assert ordered[0]._key() == (1, 0, 9)

versions.sort()
assert versions[0]._key() == (1, 0, 9)  # original list is now sorted
```

### Why does the type check return `NotImplemented`?

For a type it does not support, `__lt__` should generally return the singleton `NotImplemented`, rather than return `False` or raise an `AttributeError`. This tells Python that this implementation does not know how to compare the operands. Python can try the other operand's reflected comparison method, where applicable, and if no implementation can handle the pair, the operator normally raises `TypeError`.

```python
version = Version(1, 0, 0)
assert version < Version(2, 0, 0)

try:
    version < 3
except TypeError:
    print("Unsupported ordering raises TypeError")
```

Do not confuse `NotImplemented` with `NotImplementedError`. The former is a special return value used by operator dispatch; the latter is an exception that a method may raise when deliberately left unimplemented.

## 4. What does `sorted()` actually need?

For ordinary sorting, Python's sorting algorithm relies on `<` comparisons between elements. A custom class can therefore be sortable by implementing `__lt__`, even if it does not implement `<=`, `>`, or `>=`.

```python
class BuildNumber:
    def __init__(self, value: int) -> None:
        self.value = value

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, BuildNumber):
            return NotImplemented
        return self.value < other.value

builds = [BuildNumber(30), BuildNumber(10), BuildNumber(20)]
print([item.value for item in sorted(builds)])  # [10, 20, 30]
```

This does **not** mean the class has a complete ordering API. An expression such as `BuildNumber(10) <= BuildNumber(20)` can still raise `TypeError`, because `__le__` is not defined and Python does not automatically derive every rich comparison from `__lt__`.

## 5. Sort with `key=` or define class ordering?

Use `key=` when a particular operation needs a particular order. Define ordering methods when the ordering is an intrinsic, stable meaning of the value object and callers should be able to compare instances directly.

| Situation | Usually prefer | Reason |
|---|---|---|
| Sort customer records by current balance for one report | `key=` | The order belongs to this report, not necessarily to the domain object |
| Sort versions by `(major, minor, patch)` everywhere | Class ordering or a shared key function | Version order is intrinsic to the value |
| Sort log records by timestamp, then severity | `key=` | The report defines the chosen fields and tie-breakers |
| Sort a queue item by its explicit priority contract | Class ordering or a dedicated priority key | The order is part of the queue's semantics |
| Sort the same objects differently in different views | Separate `key=` functions | Avoid one global order that does not fit every use case |

Example: sorting ingestion events without defining an ordering for the event class.

```python
events = [
    {"event_id": "e-3", "timestamp": 30, "source": "api"},
    {"event_id": "e-1", "timestamp": 10, "source": "batch"},
    {"event_id": "e-2", "timestamp": 10, "source": "api"},
]
ordered = sorted(events, key=lambda event: (event["timestamp"], event["event_id"]))
assert [event["event_id"] for event in ordered] == ["e-1", "e-2", "e-3"]
```

A key function is called once per input element during a sort, and its results are compared. This is often simpler and more efficient than repeatedly deriving values inside custom comparison methods.

## 6. Intermediate: `functools.total_ordering`

Python's `functools.total_ordering` class decorator fills in the ordering methods you did not implement. You provide:

1. `__eq__`, and
2. one of `__lt__`, `__le__`, `__gt__`, or `__ge__`.

The decorator generates the remaining ordering methods. It does not create a meaningful ordering for you; the methods you supply must still express a coherent contract.

```python
from functools import total_ordering

@total_ordering
class Priority:
    _RANK = {"low": 10, "normal": 20, "high": 30, "critical": 40}

    def __init__(self, name: str) -> None:
        if name not in self._RANK:
            raise ValueError(f"Unknown priority: {name!r}")
        self.name = name

    def _key(self) -> int:
        return self._RANK[self.name]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Priority):
            return NotImplemented
        return self._key() == other._key()

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Priority):
            return NotImplemented
        return self._key() < other._key()

    def __repr__(self) -> str:
        return f"Priority({self.name!r})"

assert Priority("low") < Priority("high")
assert Priority("critical") > Priority("normal")
assert Priority("normal") <= Priority("normal")
assert Priority("low") != Priority("high")
```

### Important interaction with hashing

As covered in Lesson 01, defining `__eq__` on a normal class without explicitly preserving or defining a compatible `__hash__` generally makes instances unhashable (`__hash__` becomes `None`). `total_ordering` does not change that behavior. Do not add a hash simply to make the example hashable: first decide whether the value object should be hashable and ensure equality and hashing use the same immutable identity fields.

### Trade-offs of `total_ordering`

**Advantages**

- Less repetitive code.
- Reduces the risk of implementing six methods inconsistently.
- Good for ordinary domain objects where clarity matters more than tiny comparison overhead.

**Costs and limitations**

- Generated methods can add call overhead compared with carefully implemented explicit methods.
- Tracebacks can be less direct because a generated method calls another comparison method.
- It cannot repair inconsistent or semantically incorrect `__eq__` and ordering logic.
- For a performance-critical path, benchmark the real workload before deciding whether to replace it with explicit methods.

Prefer the simplest implementation that satisfies the contract. Do not optimize based on assumption alone.

## 7. Returning `NotImplemented` correctly

A rich comparison method has three important outcomes:

- Return `True` when the comparison is true.
- Return `False` when the method understands the comparison and it is false.
- Return `NotImplemented` when this implementation does not support comparing these operand types.

For example, `Version(1, 0, 0) < 3` is not a meaningful comparison in this class. Returning `NotImplemented` lets Python finish dispatch and produce a normal `TypeError` if the other side cannot handle it.

Avoid this incorrect implementation:

```python
class BadVersion:
    def __init__(self, major: int) -> None:
        self.major = major

    def __lt__(self, other: object) -> bool:
        # Incorrect: assumes every object has .major.
        return self.major < other.major
```

Comparing `BadVersion(1) < 3` raises `AttributeError`, leaking an implementation detail rather than reporting unsupported comparison. A robust method checks the supported type and returns `NotImplemented` for other types.

### `isinstance` or exact type?

The example above uses `isinstance(other, Version)`, which permits subclasses. That is convenient when subclasses genuinely share the same ordering semantics. But in value-object designs, cross-class equality or ordering can violate symmetry or substitutability if a subclass adds fields or changes the meaning of a value.

A stricter implementation may use `type(other) is type(self)` or `type(other) is Version`. Choose deliberately:

- Use `isinstance` when subclass instances should participate in the same ordering contract.
- Use exact type checks when the value's identity and ordering are defined only for the same concrete type.

Whichever policy you choose, test subclass interactions and keep equality and ordering consistent. A simple type check is not a substitute for a clear domain contract.

## 8. Dataclasses and ordering

For simple data models, `dataclasses` can generate comparisons for you. With `order=True`, the generated ordering methods compare instances as tuples of fields in declaration order, and only instances of the identical class are comparable under the generated comparison implementation.

```python
from dataclasses import dataclass, field

@dataclass(order=True, frozen=True)
class SemanticVersion:
    major: int
    minor: int
    patch: int
    label: str = field(default="", compare=False)

versions = [
    SemanticVersion(1, 2, 0, "release candidate"),
    SemanticVersion(1, 0, 9, "stable"),
    SemanticVersion(1, 2, 0, "stable"),
]
ordered = sorted(versions)
assert [(v.major, v.minor, v.patch) for v in ordered] == [
    (1, 0, 9), (1, 2, 0), (1, 2, 0)
]
assert versions[0] == versions[2]  # label is excluded from equality and ordering
```

`field(compare=False)` excludes the field from generated equality and ordering. That is useful for annotations or display metadata that should not affect the value's identity. It also means the field will not distinguish two instances during sorting; Python's stable sort preserves their input order when their keys compare equal.

### Dataclass design cautions

- `order=True` also requires equality generation; the dataclass decorator rejects incompatible method definitions rather than silently overriding explicitly defined ordering methods.
- Field declaration order becomes part of the public ordering contract. Reordering fields can change behavior.
- Every compared field must itself be comparable with the corresponding field in another instance.
- Do not include fields in ordering merely because they exist. Define the domain's intended order.
- `frozen=True` prevents ordinary attribute assignment but does not recursively freeze mutable objects stored inside fields.

For one-off sorting, a `key=` function can be more explicit than setting `order=True` on a general data model.

## 9. Tuple comparisons as a compact ordering key

Tuple comparison is a common, readable way to express lexicographic ordering.

```python
class DataFile:
    def __init__(self, partition_date: str, source_priority: int, path: str) -> None:
        self.partition_date = partition_date
        self.source_priority = source_priority
        self.path = path

    def _key(self) -> tuple[str, int, str]:
        return (self.partition_date, self.source_priority, self.path)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, DataFile):
            return NotImplemented
        return self._key() < other._key()

    def __repr__(self) -> str:
        return f"DataFile({self.partition_date!r}, {self.source_priority}, {self.path!r})"

files = [
    DataFile("2026-01-02", 2, "s3://bucket/b.csv"),
    DataFile("2026-01-01", 1, "s3://bucket/a.csv"),
    DataFile("2026-01-01", 1, "s3://bucket/z.csv"),
]
assert [item.path for item in sorted(files)] == [
    "s3://bucket/a.csv", "s3://bucket/z.csv", "s3://bucket/b.csv"
]
```

Tuple keys are concise, but the order of fields must match the domain rule. A tuple containing mixed, non-comparable types can still raise `TypeError` when Python reaches an incompatible position.

## 10. `operator.attrgetter`, `itemgetter`, and sorting by multiple keys

The `operator` module provides reusable key functions that can be clearer than repeated lambdas.

```python
from operator import attrgetter, itemgetter

class Run:
    def __init__(self, name: str, duration_ms: int, region: str) -> None:
        self.name = name
        self.duration_ms = duration_ms
        self.region = region

runs = [Run("job-c", 200, "ap-south"), Run("job-a", 100, "eu-west"), Run("job-b", 100, "ap-south")]
by_duration_then_name = sorted(runs, key=attrgetter("duration_ms", "name"))
assert [run.name for run in by_duration_then_name] == ["job-a", "job-b", "job-c"]

rows = [("api", 40), ("batch", 10), ("api", 20)]
assert sorted(rows, key=itemgetter(1)) == [("batch", 10), ("api", 20), ("api", 40)]
```

- `attrgetter("duration_ms", "name")` extracts multiple attributes and returns them as a tuple.
- `itemgetter(1)` extracts the second item from each row.
- `key=lambda x: (...)` is often best when transformation, normalization, or custom logic is required.

### Stable sorting

Python sorting is stable: items with equal keys keep their relative order from the input. Stability lets you perform multi-key sorting in multiple passes, sorting by the least significant key first and the most significant key last.

```python
records = [
    {"team": "A", "score": 80, "name": "Mira"},
    {"team": "B", "score": 90, "name": "Arun"},
    {"team": "A", "score": 80, "name": "Zoya"},
]
# First order ties by name, then stable sort by team and score.
records.sort(key=lambda row: row["name"])
records.sort(key=lambda row: (row["team"], row["score"]))
assert [(r["team"], r["score"], r["name"]) for r in records] == [
    ("A", 80, "Mira"), ("A", 80, "Zoya"), ("B", 90, "Arun")
]
```

For mixed sort directions, multiple stable passes can be clearer than trying to reverse every field in a composite key. Another option is to encode direction explicitly in a key, when that transformation is safe and readable.

```python
records = [
    {"team": "A", "score": 80, "name": "Mira"},
    {"team": "A", "score": 90, "name": "Zoya"},
    {"team": "A", "score": 90, "name": "Arun"},
]
records.sort(key=lambda row: row["name"])                 # ascending name
records.sort(key=lambda row: row["score"], reverse=True) # descending score; stable ties
assert [r["name"] for r in records] == ["Arun", "Zoya", "Mira"]
```

## 11. Advanced: ordering laws and invariants

A sorting implementation should represent a coherent ordering, not just return plausible answers for one list.

For a **non-strict total order** (`<=`), the usual laws are:

1. **Reflexivity:** `a <= a` is true.
2. **Antisymmetry:** if `a <= b` and `b <= a`, then `a` and `b` are equal in the ordering's sense.
3. **Transitivity:** if `a <= b` and `b <= c`, then `a <= c`.
4. **Totality:** for any `a` and `b`, at least one of `a <= b` or `b <= a` holds.

For a **strict total order** (`<`), the corresponding formulation uses irreflexivity (`not a < a`), transitivity, and comparability of distinct values. Keep the strict and non-strict formulations separate: `a < a` should be false, so strict ordering is not reflexive.

For practical class design, also test consistency between equality and ordering. If both `a <= b` and `b <= a` are true, they should normally compare equal (`a == b`) for a total value ordering. If your class intentionally models a different relation, document that rather than pretending it is a total order.

### What breaks when laws fail?

If a comparator is inconsistent, sorting and priority structures may produce results that do not match the business rule. The algorithm generally does not validate all mathematical laws for you. Some defects may not raise exceptions at all.

```python
class Cyclic:
    """Intentionally broken example: 0 < 1, 1 < 2, and 2 < 0."""
    def __init__(self, value: int) -> None:
        self.value = value % 3

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Cyclic):
            return NotImplemented
        return (self.value, other.value) in {(0, 1), (1, 2), (2, 0)}

items = [Cyclic(0), Cyclic(1), Cyclic(2)]
# This comparator violates transitivity. Do not rely on sorted(items) to
# establish a meaningful global order; it may return a list without error.
```

The lesson from this deliberately broken example is not to memorize the output of `sorted()`. The output depends on the algorithm's comparisons and input arrangement; it is not a valid ordering guarantee when the comparison contract is violated.

## 12. Floating-point values and `NaN`

IEEE floating-point `NaN` (not a number) is unusual:

```python
nan = float("nan")
assert not (nan < 1)
assert not (nan > 1)
assert not (nan == nan)
assert not (nan <= nan)
```

NaN does not behave like an ordinary number in an order. If NaN values appear in a list, a normal numeric sort key does not define a reliable business ordering for them. Decide what they mean in your domain: missing measurement, invalid data, or a special category. Then encode that decision explicitly.

```python
import math

measurements = [3.5, float("nan"), 1.2, 2.0]
# Policy: finite numeric values first in ascending order; NaN values last.
ordered = sorted(measurements, key=lambda value: (math.isnan(value), 0.0 if math.isnan(value) else value))
assert ordered[:3] == [1.2, 2.0, 3.5]
assert math.isnan(ordered[-1])
```

Do not use floating-point arithmetic for exact financial amounts. Use integer minor units (such as cents) or `decimal.Decimal` with an explicit precision and rounding policy. Even with `Decimal`, define how special values and missing data should be handled if they are allowed in your domain.

## 13. Partial orders: why sets are different

Not every comparison relation is a total order. Python sets use `<` to mean **proper subset**, not “comes before.” Two sets can be incomparable.

```python
left = {1, 2}
right = {2, 3}
assert not (left < right)
assert not (right < left)
assert left != right
```

Because neither set is a subset of the other, neither is less than the other. This is a partial order. Sorting sets does not create a meaningful canonical ordering by subset relation. If you need a display order, provide an explicit key such as `(len(value), sorted(value))` for sets whose elements are mutually sortable.

```python
sets = [{3, 1}, {1}, {2, 4, 5}]
ordered_sets = sorted(sets, key=lambda value: (len(value), tuple(sorted(value))))
assert ordered_sets == [{1}, {1, 3}, {2, 4, 5}]
```

## 14. `functools.cmp_to_key` for legacy comparators

Modern Python sorting expects a key function or rich comparisons. `functools.cmp_to_key` adapts a legacy two-argument comparator that returns a negative number, zero, or a positive number.

```python
from functools import cmp_to_key

def compare_case_insensitive(left: str, right: str) -> int:
    left_key = left.casefold()
    right_key = right.casefold()
    return (left_key > right_key) - (left_key < right_key)

names = ["zoe", "Arun", "mira"]
assert sorted(names, key=cmp_to_key(compare_case_insensitive)) == ["Arun", "mira", "zoe"]
```

Use `cmp_to_key` mainly when adapting an existing comparator or when the comparison rule cannot be expressed cleanly as a key. A normal `key=` function is generally simpler and avoids repeated pairwise comparison work to derive the key.

## 15. Heterogeneous values: make the order explicit

Python 3 does not define a general ordering between unrelated types such as `int` and `str`.

```python
try:
    sorted([10, "2"])
except TypeError:
    print("Mixed int and str values need an explicit policy")
```

Do not depend on type names or arbitrary conversions without a domain reason. Define a deterministic policy for the values you expect. For example, to put integers before strings:

```python
values = ["10", 3, "2", 1]
ordered = sorted(values, key=lambda value: (0, value) if isinstance(value, int) else (1, value))
assert ordered == [1, 3, "10", "2"]
```

This policy intentionally sorts integers numerically and strings lexicographically. It does **not** treat numeric-looking strings as numbers. If that is required, parse and validate them explicitly rather than silently coercing arbitrary data.

## 16. `bisect`: sorted insertion and lookup

`bisect` finds insertion points in a list that is already sorted under the same ordering rule. It does not sort the list for you. If the list's ordering invariant is broken, the result is not meaningful.

```python
from bisect import bisect_left, insort

scores = [10, 20, 20, 40]
position = bisect_left(scores, 20)
assert position == 1
insort(scores, 30)
assert scores == [10, 20, 20, 30, 40]
```

When using custom objects, ensure the comparison behavior used by `bisect` matches the order in which the list was built. If you sort by a key, maintain and search a parallel list of those keys or use an appropriate design for your Python version and API; do not assume a key used for sorting automatically transforms values passed to every lookup operation.

## 17. `heapq`: priority queues

`heapq` uses `<` comparisons to maintain a heap. It does not fully sort the data; it keeps the smallest item at the root so the next item can be popped efficiently. If two objects can have the same priority, include a deterministic tie-breaker to avoid comparing unsupported payload objects.

```python
import heapq

jobs = [
    (2, 100, {"job_id": "transform"}),
    (1, 200, {"job_id": "extract"}),
    (1, 100, {"job_id": "validate"}),
]
heapq.heapify(jobs)
assert [heapq.heappop(jobs)[2]["job_id"] for _ in range(3)] == [
    "validate", "extract", "transform"
]
```

Here the tuple order is `(priority, sequence_number, payload)`. If priority and sequence number tie, Python would attempt to compare the payload dictionaries, which is not an ordering you should rely on. In production, use a unique sequence number or a stable identifier as a tie-breaker. A common pattern is `(priority, counter, task)`.

## 18. Production case study: deterministic event ordering

Suppose a pipeline receives events from multiple sources. The processing contract says:

1. Earlier event timestamps come first.
2. At the same timestamp, higher source priority comes first.
3. Remaining ties are resolved by `event_id` so the order is deterministic.

A one-off `key=` function is appropriate because the ordering belongs to this pipeline operation, not necessarily to every use of an event record.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Event:
    event_id: str
    timestamp_ms: int
    source_priority: int
    payload: str


def event_order(event: Event) -> tuple[int, int, str]:
    # Negative priority means larger priority numbers come first.
    return (event.timestamp_ms, -event.source_priority, event.event_id)

batch = [
    Event("e-03", 1_000, 1, "third"),
    Event("e-02", 1_000, 5, "second"),
    Event("e-01", 900, 1, "first"),
    Event("e-04", 1_000, 5, "fourth"),
]
ordered_batch = sorted(batch, key=event_order)
assert [event.event_id for event in ordered_batch] == ["e-01", "e-02", "e-04", "e-03"]
```

### Engineering review checklist

- Is the sort rule a business requirement or merely a display preference?
- Are all key fields present and validated before sorting?
- Are ties resolved deterministically if reproducible output matters?
- Can any key contain `None`, NaN, or mixed types that are not mutually comparable?
- Does the ordering agree with equality where the domain requires it?
- Will `bisect` or `heapq` use the same comparison rule?
- Is the class's ordering intrinsic, or would `key=` keep the contract narrower?
- Are tests covering equal keys, unsupported types, boundaries, and inconsistent cases?

## 19. Common mistakes and fixes

| Mistake | Why it is a problem | Better approach |
|---|---|---|
| Implement only `__lt__` and assume `<=` works | Python does not derive all comparison methods automatically | Implement the required methods or use `@total_ordering` |
| Return `False` for every foreign type | Blocks the normal unsupported-operation dispatch path | Return `NotImplemented` when the type is unsupported |
| Compare one field in `__eq__` and unrelated fields in `__lt__` | Can make equality and ordering contradictory | Define a shared domain key and test invariants |
| Use `order=True` without considering field order | Field declaration order becomes observable behavior | Make ordering fields deliberate; exclude metadata with `compare=False` |
| Assume all comparisons form a total order | NaN and subset relations are counterexamples | Model special values and partial orders explicitly |
| Sort mixed types without a policy | Python may raise `TypeError` | Normalize or define a type-aware key |
| Use `total_ordering` on a hot path without measurement | Generated methods can add overhead | Benchmark realistic data before optimizing |
| Compare money as binary floats | Rounding behavior can violate business expectations | Use integer minor units or `Decimal` with explicit rules |
| Give a heap items equal priorities with unorderable payloads | Heap comparisons may reach the payload and fail | Add a deterministic sequence or identifier tie-breaker |
| Use `bisect` on an unsorted list | Insertion points no longer match the invariant | Keep the list sorted using the same ordering rule |

## 20. Testing comparison contracts with pytest

Create `test_ordering.py` and place the following code in it. It assumes the `Version`, `Priority`, and `Event` examples above are in an importable module named `ordering_lesson.py`. If your file has a different name, adjust the import accordingly.

```python
import pytest

from ordering_lesson import Event, Priority, Version, event_order


def test_version_sorts_lexicographically() -> None:
    values = [Version(1, 2, 0), Version(1, 0, 9), Version(2, 0, 0)]
    assert [value._key() for value in sorted(values)] == [
        (1, 0, 9), (1, 2, 0), (2, 0, 0)
    ]


def test_version_unsupported_type_raises_type_error() -> None:
    with pytest.raises(TypeError):
        _ = Version(1, 0, 0) < 3


def test_priority_total_ordering_supplies_methods() -> None:
    low = Priority("low")
    normal = Priority("normal")
    high = Priority("high")
    assert low < normal <= high
    assert high > low
    assert normal == Priority("normal")


def test_event_sort_is_deterministic() -> None:
    events = [
        Event("b", 100, 1, "payload"),
        Event("a", 100, 1, "payload"),
        Event("c", 90, 1, "payload"),
    ]
    assert [event.event_id for event in sorted(events, key=event_order)] == ["c", "a", "b"]


def test_version_rejects_negative_components() -> None:
    with pytest.raises(ValueError):
        Version(-1, 0, 0)
```

Run:

```bash
python -m pytest -q
```

### Property-style invariants

For a well-behaved total order, test relationships across representative values rather than only one expected sorted list.

```python
def assert_ordering_invariants(values: list[Version]) -> None:
    for a in values:
        assert not (a < a)  # strict ordering is irreflexive
        for b in values:
            if a < b:
                assert not (b < a)  # asymmetry of a strict order
            if not (a < b) and not (b < a):
                assert a == b  # for this total value order, ties mean equality
            for c in values:
                if a < b and b < c:
                    assert a < c  # transitivity

assert_ordering_invariants([
    Version(0, 0, 0), Version(1, 0, 0), Version(1, 2, 0), Version(2, 0, 0)
])
```

This helper is deliberately small and cubic in the number of values; use a compact representative set for unit tests. For larger test spaces, consider property-based testing and generate valid domain values. The invariants should reflect the exact ordering contract of your class.

## 21. Exercises

Attempt each exercise before reading the solution. Use Python 3.12+.

### Exercise 1 — Which method does sorting require?

Create a class that implements only `__lt__`. Show that `sorted()` works, then show that `<=` is not automatically available.

### Exercise 2 — Implement a release priority

Create an immutable or effectively immutable `Release` value object with `major`, `minor`, and `patch` integers. Implement equality and less-than comparison using a tuple key. Unsupported operand types should be handled properly. Explain whether you would use `@total_ordering` or implement every method explicitly.

### Exercise 3 — Sort records for a data quality report

Given dictionaries with `dataset`, `failed_rows`, and `checked_at`, sort by most failed rows first, then dataset name ascending, then timestamp ascending. Do not add ordering methods to `dict` or wrap every row in a custom class.

### Exercise 4 — Handle NaN

Sort `[float("nan"), 3.0, 1.0, float("nan"), 2.0]` with finite values first in ascending order and NaNs last. Explain why a plain numeric key does not define a satisfactory policy for NaN.

### Exercise 5 — Diagnose a broken comparator

A class defines `__eq__` based on `name` but `__lt__` based on `created_at`. What kinds of inconsistent behavior can result? Propose a consistent domain rule.

### Exercise 6 — Priority queue ties

Design a heap entry for tasks with `priority`, `sequence`, and a task payload that may not be comparable. Explain how your tuple layout prevents Python from comparing the payload when priorities tie.

## 22. Exercise solutions

### Solution 1

```python
class Number:
    def __init__(self, value: int) -> None:
        self.value = value

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Number):
            return NotImplemented
        return self.value < other.value

numbers = [Number(3), Number(1), Number(2)]
assert [n.value for n in sorted(numbers)] == [1, 2, 3]
try:
    Number(1) <= Number(2)
except TypeError:
    pass
else:
    raise AssertionError("<= should not be assumed to exist")
```

### Solution 2

```python
from functools import total_ordering

@total_ordering
class Release:
    def __init__(self, major: int, minor: int, patch: int) -> None:
        self._key = (major, minor, patch)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Release):
            return NotImplemented
        return self._key == other._key

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Release):
            return NotImplemented
        return self._key < other._key

assert Release(1, 2, 0) < Release(1, 10, 0)
assert Release(2, 0, 0) >= Release(1, 9, 9)
```

For a small value object, `@total_ordering` reduces boilerplate. For a very hot path or a public API requiring explicit behavior and easier tracebacks, implement the necessary methods explicitly and benchmark if performance is material. A production implementation should also validate non-negative integer components and decide whether to expose immutable fields.

### Solution 3

```python
rows = [
    {"dataset": "orders", "failed_rows": 10, "checked_at": "2026-01-02"},
    {"dataset": "customers", "failed_rows": 10, "checked_at": "2026-01-01"},
    {"dataset": "orders", "failed_rows": 5, "checked_at": "2026-01-01"},
]
ordered = sorted(rows, key=lambda row: (-row["failed_rows"], row["dataset"], row["checked_at"]))
assert [(r["failed_rows"], r["dataset"], r["checked_at"]) for r in ordered] == [
    (10, "customers", "2026-01-01"),
    (10, "orders", "2026-01-02"),
    (5, "orders", "2026-01-01"),
]
```

This assumes `failed_rows` is a validated numeric value and `checked_at` is in a consistent sortable representation. For production timestamps, use normalized timezone-aware `datetime` values or an explicitly normalized numeric timestamp.

### Solution 4

```python
import math

values = [float("nan"), 3.0, 1.0, float("nan"), 2.0]
ordered = sorted(values, key=lambda value: (math.isnan(value), 0.0 if math.isnan(value) else value))
assert ordered[:3] == [1.0, 2.0, 3.0]
assert math.isnan(ordered[3]) and math.isnan(ordered[4])
```

NaN is not equal to itself and is neither less than nor greater than ordinary numbers. The key maps values into an explicit two-part order: `(False, numeric_value)` for finite values and `(True, 0.0)` for NaN values. The second component is a placeholder for NaNs and does not define their numeric meaning.

### Solution 5

If equality says two objects are equal because their names match, but ordering distinguishes them by creation time, it is possible for `a == b` to be true while `a < b` or `b < a` is also true. That is usually a confusing contract for a value object. Choose one identity/order model: for example, both equality and ordering could use `(created_at, name)`, or equality could use a stable identifier while sorting uses `key=lambda x: x.created_at`. The second option keeps sorting policy separate from equality.

### Solution 6

```python
import heapq
from itertools import count

sequence = count()
heap: list[tuple[int, int, object]] = []
heapq.heappush(heap, (2, next(sequence), {"task": "slow"}))
heapq.heappush(heap, (1, next(sequence), {"task": "fast-a"}))
heapq.heappush(heap, (1, next(sequence), {"task": "fast-b"}))

first = heapq.heappop(heap)
assert first[2] == {"task": "fast-a"}
```

The sequence counter is unique for each inserted item. If priorities tie, Python compares the sequence values and does not need to compare the payload. In production, consider a small named dataclass or a documented tuple alias to make the heap entry's structure clear.

## 23. Self-check — answer from memory

1. Which single comparison method does `sorted()` normally require from a custom class?
2. Why does `total_ordering` need `__eq__` as well as one ordering method?
3. What should a rich comparison method return when it does not support the other operand's type?
4. Why might a class use `field(compare=False)` for a dataclass field?
5. What does stability mean for Python sorting?
6. Why is NaN problematic for ordinary numeric ordering?
7. Why are sets an example of a partial order?
8. When would `cmp_to_key` be useful instead of a regular key function?
9. What invariant must be maintained before using `bisect`?
10. Why should heap entries have a deterministic tie-breaker before the payload?

### Answer key

1. `__lt__` (less-than).
2. The generated methods need equality to distinguish equal values from strictly ordered values.
3. `NotImplemented`, allowing Python to try other supported dispatch paths and ultimately raise `TypeError` if necessary.
4. The field is metadata or otherwise should not affect generated equality and ordering.
5. Items with equal sort keys retain their relative input order.
6. NaN is not equal to itself and is neither less than nor greater than ordinary values, so a numeric key alone does not define a useful total order.
7. Two sets can be incomparable under subset ordering.
8. To adapt an existing two-argument comparison function that returns negative/zero/positive values.
9. The list must already be sorted under the same order used for insertion-point search.
10. If earlier tuple fields tie, Python compares the next field; a unique tie-breaker prevents comparison from reaching a non-orderable payload.

## 24. Completion checklist

You are ready to continue when you can do all of the following without copying the examples:

- [ ] Implement `__lt__` using a clear tuple key.
- [ ] Return `NotImplemented` for unsupported types.
- [ ] Explain the difference between a class ordering contract and a one-off `key=` function.
- [ ] Use `@total_ordering` and explain its trade-offs.
- [ ] Use `dataclass(order=True)` and `field(compare=False)` appropriately.
- [ ] Sort records with multiple keys and mixed directions.
- [ ] Explain stability, total-order laws, partial orders, and NaN handling.
- [ ] Use `bisect` only with a maintained sorted invariant.
- [ ] Use a deterministic tie-breaker in `heapq` entries.
- [ ] Test comparison laws and edge cases with pytest.

## 25. Key takeaways

- Rich comparison methods define how custom objects respond to comparison operators.
- `sorted()` and `list.sort()` normally need `<`; they do not automatically provide every other comparison operation.
- `key=` is often the clearest choice for report-specific or pipeline-specific ordering. Implement class ordering when it is truly part of the value's domain contract.
- `NotImplemented` is the correct signal for an unsupported operand type.
- `total_ordering` reduces boilerplate but does not fix an incoherent comparison design.
- Equality and ordering should agree with the domain's identity model.
- Sorting stability, explicit NaN policy, deterministic tie-breakers, and valid invariants are production correctness concerns—not just syntax details.
- `bisect` and `heapq` rely on a consistent comparison rule; neither can repair a broken ordering contract.

**Next lesson:** `03-container-protocols-getitem-len-iter-and-contains.md`.
