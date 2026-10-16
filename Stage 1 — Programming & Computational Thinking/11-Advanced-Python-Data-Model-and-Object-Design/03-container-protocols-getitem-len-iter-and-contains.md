# Python Container Protocols: `__getitem__`, `__len__`, `__iter__`, and `__contains__`

**Stage:** Stage 1 — Programming & Computational Thinking  
**Module:** 11 — Advanced Python Data Model and Object Design  
**Lesson:** 03 — Container Protocols  
**Target:** Python 3.12+  
**Learning path:** Mental models → protocol mechanics → runnable examples → tests → data-engineering case study → exercises → self-check

> This lesson follows Lesson 03 in `roadmap-Advanced-Python-Data-Model-and-Object-Design.md`. It covers the specified basic, intermediate, and advanced topics: sequence-protocol fallbacks, slicing, mutable-container hooks, mapping behavior, iteration/reversal, `__index__`, truthiness, built-in subclassing versus composition, multidimensional indexing, lazy views, typing protocols, `__length_hint__`, and correct exception contracts.

## Learning outcomes

By the end, you should be able to:

- Explain the difference between a container, an iterable, an iterator, a sequence, and a mapping.
- Implement `__len__`, `__getitem__`, `__iter__`, and `__contains__` so built-in Python operations work naturally.
- Explain Python's legacy iteration fallback through integer `__getitem__` calls and its `IndexError` stopping rule.
- Implement slicing, negative indices, explicit membership, reversal, and optional mutation methods with clear contracts.
- Explain how `__bool__` uses `__len__` when `__bool__` is absent, and how `__index__` differs from `__int__`.
- Choose composition, `collections.UserDict`, or `collections.UserList` instead of assuming a built-in subclass will intercept every operation.
- Understand tuple-based multidimensional indexing, `Ellipsis`, lazy views, and the limits of `__length_hint__`.
- Test protocol behavior, complexity, boundary conditions, and repeatability in production-oriented code.

## 1. Why container protocols matter

Python's built-in operations do not need to know the implementation details of your class. They ask objects to follow a protocol: a set of behaviors expressed through special methods. When a class implements the appropriate methods, it can work with `len()`, indexing, slicing, `for` loops, `in`, `reversed()`, and many standard-library tools.

This is one reason libraries such as NumPy, pandas, `pathlib`, ORM result collections, and configuration wrappers can feel familiar even when their internals are very different. The goal is not to make every class act like a list. The goal is to provide the operations that accurately represent the abstraction.

### The four core methods

| Python operation | Main protocol method | Typical contract |
|---|---|---|
| `len(obj)` | `obj.__len__()` | Return a non-negative integer size. |
| `obj[key]` | `obj.__getitem__(key)` | Retrieve the item described by a key or index. |
| `for item in obj` / `iter(obj)` | `obj.__iter__()` | Return an iterator that yields items. |
| `item in obj` | `obj.__contains__(item)` when present | Return whether the item is a member. |

These methods are connected but not interchangeable. For example, implementing `__getitem__` does not automatically make random access efficient, and implementing `__len__` does not mean the object should support indexing.

## 2. Container, iterable, iterator, sequence, and mapping

These words describe related but different ideas.

- **Container:** an object that can answer membership questions, usually through `in`.
- **Iterable:** an object from which an iterator can be obtained with `iter(obj)`.
- **Iterator:** an object that produces the next item when `next(iterator)` is called. It normally implements both `__iter__` (returning itself) and `__next__`.
- **Sequence:** an ordered collection with integer indexing, usually a defined length, and sequence-style slicing semantics. Lists, tuples, strings, and ranges are examples.
- **Mapping:** a collection that associates keys with values, such as a dictionary. Mapping keys are not necessarily integer positions.

A list is a sequence, container, and iterable. A generator is an iterable and iterator, but it is not a reusable sequence and does not generally support `len()` or indexing. A custom object may support some protocols but not others; that is often the correct design.

```python
values = [10, 20, 30]
iterator = iter(values)

print(len(values))       # 3
print(values[1])         # 20
print(20 in values)      # True
print(iter(values) is values)  # False: a list returns a separate iterator
print(next(iterator))    # 10
print(next(iterator))    # 20
```

A useful design question is: *What operations should callers reasonably expect this object to support?* Do not add indexing or a length merely because a list has them.

## 3. `__len__`: size and truthiness

`__len__` supports `len(obj)`. It should return an integer greater than or equal to zero. In ordinary Python code, return a real integer, not a float, string, or a negative number.

```python
class Batch:
    def __init__(self, records: list[dict[str, object]]) -> None:
        self._records = list(records)

    def __len__(self) -> int:
        return len(self._records)

batch = Batch([{"id": 1}, {"id": 2}])
print(len(batch))  # 2
```

### Truthiness fallback

If an object defines `__bool__`, Python uses it for truth-value testing. If it does not define `__bool__` but does define `__len__`, Python treats the object as false when its length is zero and true otherwise.

```python
class QueueSnapshot:
    def __init__(self, items: list[str]) -> None:
        self._items = list(items)

    def __len__(self) -> int:
        return len(self._items)

empty = QueueSnapshot([])
nonempty = QueueSnapshot(["job-17"])
print(bool(empty))     # False
print(bool(nonempty))  # True
```

This fallback is convenient when “empty” naturally means “false.” If the domain's truth value has a different meaning, define `__bool__` deliberately. A size method should describe size, not encode business rules.

### Production cautions

- Computing `len(obj)` should normally be cheap and predictable. Do not scan a huge remote data source every time `len()` is called unless that cost is explicit in the API.
- Do not return a negative length. It violates the protocol and raises an exception when `len()` is evaluated.
- If size is unknown or expensive, consider not implementing `__len__`; do not fabricate a value.

## 4. `__getitem__`: indexing and key lookup

`obj[key]` passes `key` to `__getitem__`. For a sequence, the key is typically an integer or a `slice`. For a mapping, it may be a string, tuple, UUID, or another hashable key. The protocol itself does not force every class to use integer indices.

```python
class FieldMap:
    def __init__(self, values: dict[str, object]) -> None:
        self._values = dict(values)

    def __getitem__(self, key: str) -> object:
        return self._values[key]

fields = FieldMap({"source": "orders", "rows": 125})
print(fields["source"])  # orders
print(fields["rows"])    # 125
```

### Sequence-style index handling

A sequence usually supports:

- zero-based indices (`items[0]`);
- negative indices (`items[-1]` means the last item);
- `IndexError` when an integer index is outside the valid range;
- slices (`items[start:stop:step]`).

A wrapper around a list can delegate these details to the underlying list.

```python
class RecordBatch:
    def __init__(self, records: list[str]) -> None:
        self._records = list(records)

    def __len__(self) -> int:
        return len(self._records)

    def __getitem__(self, index: int | slice) -> str | list[str]:
        return self._records[index]

batch = RecordBatch(["r-100", "r-101", "r-102", "r-103"])
print(batch[0])      # r-100
print(batch[-1])     # r-103
print(batch[1:3])    # ['r-101', 'r-102']
```

This implementation deliberately returns a `list` for a slice. That is acceptable if the class documents that contract, but it may be surprising when callers expect a slice to preserve the custom type. The next section shows how to preserve the type.

### Exceptions are part of the API

For sequence-like objects, an out-of-range integer index should normally raise `IndexError`. For mapping-like objects, an unknown key should normally raise `KeyError`. Avoid returning `None` for a missing item unless `None` is explicitly the documented result; otherwise, callers cannot distinguish “missing” from “present with value `None`.”

## 5. Slicing: `slice` objects and preserving the container type

For `obj[1:8:2]`, Python passes a `slice` object to `__getitem__`. A slice contains `start`, `stop`, and `step`; any of these may be `None`. Python's built-in sequences handle normalization, negative indices, and invalid ranges.

```python
window = slice(1, 8, 2)
print(window.start, window.stop, window.step)  # 1 8 2
print(list(range(10))[window])                # [1, 3, 5, 7]
```

A custom sequence can use the underlying list's slice behavior, then wrap the result in a new instance of its own type.

```python
from __future__ import annotations

class RecordBatch:
    def __init__(self, records: list[str]) -> None:
        self._records = list(records)

    def __len__(self) -> int:
        return len(self._records)

    def __getitem__(self, index: int | slice) -> str | "RecordBatch":
        result = self._records[index]
        if isinstance(index, slice):
            return RecordBatch(result)
        return result

    def __iter__(self):
        return iter(self._records)

batch = RecordBatch(["a", "b", "c", "d", "e"])
window = batch[1:4]
print(type(window).__name__)  # RecordBatch
print(list(window))           # ['b', 'c', 'd']
print(list(batch[::-1]))      # ['e', 'd', 'c', 'b', 'a']
```

### Slicing design decisions

There is no universal rule that all custom slices must return the same type. Decide based on the abstraction:

- A list-like wrapper often returns the same wrapper type.
- A view may return a lightweight object that references the original data.
- A query API may return a query expression rather than materialized records.
- A mapping may not support slicing at all.

Document whether a slice is a copy or a view, whether it is mutable, and whether changes to the original are visible in the slice.

## 6. `__iter__`: make the object iterable

`__iter__` should return an iterator. A simple and reliable implementation for a wrapper is to return an iterator over the internal collection.

```python
class DatasetNames:
    def __init__(self, names: list[str]) -> None:
        self._names = list(names)

    def __iter__(self):
        return iter(self._names)

names = DatasetNames(["customers", "orders", "payments"])
for name in names:
    print(name)
```

### Iterable versus iterator: why `return self` is often wrong

A reusable container should normally return a **fresh iterator** each time `iter(container)` is called. Returning `self` is appropriate when the object itself is an iterator and implements `__next__`; it is usually wrong for a reusable collection.

```python
class BadBatch:
    def __init__(self, items: list[int]) -> None:
        self._items = items
        self._position = 0

    def __iter__(self):
        return self  # Bug: this object has no __next__, and iteration state is shared.

# iter(BadBatch([1, 2])) fails because the returned object is not an iterator.
```

The corrected container delegates iteration to its internal list:

```python
class GoodBatch:
    def __init__(self, items: list[int]) -> None:
        self._items = list(items)

    def __iter__(self):
        return iter(self._items)

batch = GoodBatch([1, 2, 3])
print(list(batch))  # [1, 2, 3]
print(list(batch))  # [1, 2, 3] — a second pass works
```

A generator function is another good option: calling it creates a fresh generator iterator each time.

```python
class PositiveIds:
    def __init__(self, ids: list[int]) -> None:
        self._ids = list(ids)

    def __iter__(self):
        for value in self._ids:
            if value > 0:
                yield value
```

The important contract is not whether you use `iter(...)` or `yield`; it is that `iter(container)` returns a valid iterator and repeated iteration behaves as documented.

## 7. The legacy sequence-iteration fallback

Python supports a legacy iteration protocol for compatibility: if an object has no usable `__iter__` but does provide integer-based `__getitem__`, iteration can request indices `0`, `1`, `2`, and so on until `__getitem__` raises `IndexError`.

The roadmap's deck example demonstrates this. Here is a smaller version:

```python
class LegacySequence:
    def __init__(self, values: list[str]) -> None:
        self._values = list(values)

    def __getitem__(self, index: int) -> str:
        return self._values[index]

legacy = LegacySequence(["north", "south", "west"])
print(list(legacy))  # ['north', 'south', 'west']
```

The list raises `IndexError` after the last element, and that exception signals the end of iteration in this fallback. This is a compatibility behavior, not a reason to omit `__iter__` from a new class. Implement `__iter__` explicitly because it communicates intent and lets you choose a suitable iteration strategy.

**Important:** do not catch `IndexError` broadly inside a sequence's `__getitem__` and return a placeholder for out-of-range integer indices. Doing so can break termination of legacy iteration. For normal sequence semantics, let an invalid integer index raise `IndexError`.

## 8. `__contains__`: membership with `in`

The expression `item in obj` checks membership. Python calls `obj.__contains__(item)` if the type provides it. If it does not, Python falls back to iteration; for legacy sequence-like objects, that can in turn use indexed access.

```python
class AllowedRegions:
    def __init__(self, regions: list[str]) -> None:
        self._regions = tuple(regions)

    def __iter__(self):
        return iter(self._regions)

allowed = AllowedRegions(["ap-south-1", "eu-west-1"])
print("ap-south-1" in allowed)  # True, via iteration fallback
print("us-east-1" in allowed)  # False
```

For a small container, iteration fallback may be sufficient. For a large container, an explicit `__contains__` can use an index or set and avoid a full scan.

```python
class RegionRegistry:
    def __init__(self, regions: list[str]) -> None:
        self._regions = tuple(regions)
        self._lookup = frozenset(regions)

    def __iter__(self):
        return iter(self._regions)

    def __contains__(self, region: object) -> bool:
        return region in self._lookup

registry = RegionRegistry(["ap-south-1", "eu-west-1"])
print("eu-west-1" in registry)  # True
print("us-east-1" in registry)  # False
```

The explicit set lookup is expected O(1) average-case membership, while scanning a list is O(n). The trade-off is extra memory and the requirement that the lookup elements be hashable. Do not create a set blindly if duplicates, ordering, unhashable values, or memory costs matter to the abstraction.

### Special-method lookup note

Implicit special-method operations such as `len(obj)` and `item in obj` look for the relevant method on the object's type, not by consulting an arbitrary same-named attribute attached to one instance. Define the protocol method on the class (or its base class) rather than trying to patch it onto one instance.

## 9. Deck example: several protocols working together

This follows the roadmap's beginner example. Because the class defines `__len__` and `__getitem__`, it supports length, indexing, slicing, and legacy iteration. Membership works through iteration because `__contains__` is not defined.

```python
class Deck:
    RANKS = [str(number) for number in range(2, 11)] + list("JQKA")
    SUITS = ["spades", "diamonds", "clubs", "hearts"]

    def __init__(self) -> None:
        self._cards = [(rank, suit) for suit in self.SUITS for rank in self.RANKS]

    def __len__(self) -> int:
        return len(self._cards)

    def __getitem__(self, position: int | slice):
        return self._cards[position]

deck = Deck()
print(len(deck))                       # 52
print(deck[0])                         # ('2', 'spades')
print(deck[-1])                        # ('A', 'hearts')
print(deck[:3])                        # first three cards
print(("A", "hearts") in deck)        # True via iteration fallback
```

For this class, `in` scans the cards until it finds a match or reaches the end. A custom `__contains__` is not necessary for correctness, but could be useful if membership becomes a hot path and a suitable lookup structure is worth its memory cost.

## 10. Mutable containers: `__setitem__` and `__delitem__`

The roadmap asks you to recognize these related methods:

- `obj[key] = value` calls `__setitem__(key, value)`.
- `del obj[key]` calls `__delitem__(key)`.

They are appropriate only when the object is intended to be mutable. A read-only collection should not implement mutation methods merely to resemble a list.

```python
class MutableRecordBatch:
    def __init__(self, records: list[str]) -> None:
        self._records = list(records)

    def __len__(self) -> int:
        return len(self._records)

    def __getitem__(self, index: int | slice):
        return self._records[index]

    def __setitem__(self, index: int, value: str) -> None:
        self._records[index] = value

    def __delitem__(self, index: int) -> None:
        del self._records[index]

batch = MutableRecordBatch(["a", "b", "c"])
batch[1] = "B"
del batch[0]
print(batch[0], len(batch))  # B 2
```

For a mutable sequence, think through slice assignment, deletion, and invariant preservation. If a mutation must update several internal structures, perform the update atomically enough that an exception cannot leave them inconsistent.

## 11. `__missing__` for dictionary subclasses

`dict` subclasses can define `__missing__(key)` to customize what happens when `d[key]` is used for a missing key. It is not a general hook for every dictionary lookup operation: methods such as `get()` do not invoke `__missing__` in the same way as subscription.

```python
class ZeroDefaultDict(dict[str, int]):
    def __missing__(self, key: str) -> int:
        return 0

counts = ZeroDefaultDict()
print(counts["missing-key"])  # 0
print(counts)                  # {} — __missing__ did not insert the key
```

This example returns a default but does not store it. If you want the missing key to be inserted, do so explicitly and document the side effect, or use a standard-library type such as `collections.defaultdict` when its semantics fit.

## 12. `__reversed__`: reverse iteration

`reversed(obj)` first looks for a suitable `__reversed__`. If it is absent, Python can use the sequence protocol when the object supports `__len__` and integer `__getitem__`.

```python
class EventBatch:
    def __init__(self, events: list[str]) -> None:
        self._events = list(events)

    def __len__(self) -> int:
        return len(self._events)

    def __getitem__(self, index: int | slice):
        return self._events[index]

    def __reversed__(self):
        # Delegate to the underlying list's reverse iterator.
        return reversed(self._events)

events = EventBatch(["created", "validated", "loaded"])
print(list(reversed(events)))  # ['loaded', 'validated', 'created']
```

Implement `__reversed__` when it provides a clearer or more efficient reverse traversal than repeated indexing. For streaming or one-shot sources, reverse traversal may be impossible without buffering; do not pretend otherwise.

## 13. `__index__`: integer-like objects for indexing

`__index__` is for objects that represent an exact integer and need to be accepted where Python requires an integer index, such as list indexing or `range()` arguments. It is not a substitute for `__int__`: `int(x)` can represent a conversion or truncation, while `__index__` promises an exact integer value.

```python
class BatchPosition:
    def __init__(self, value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("position must be an integer")
        self._value = value

    def __index__(self) -> int:
        return self._value

records = ["row-0", "row-1", "row-2"]
position = BatchPosition(1)
print(records[position])  # row-1
print(list(range(BatchPosition(3))))  # [0, 1, 2]
```

Use `__index__` only if the type genuinely represents an integer. Avoid silently rounding or truncating a decimal value into an index.

## 14. Truthiness: `__bool__` versus `__len__`

The default truth-value behavior is:

1. If `__bool__` exists, use its boolean result.
2. Otherwise, if `__len__` exists, zero length means false and nonzero length means true.
3. Otherwise, the object is normally true.

Do not implement `__bool__` to perform expensive I/O, run a database query, or evaluate a complex business policy as an incidental side effect of `if obj:`. Callers expect truth-value testing to be simple and unsurprising.

## 15. Built-in subclassing versus composition

Subclassing `list` or `dict` can be useful, but it is not a guarantee that every built-in operation will route through your Python-level overrides. Some built-in methods and C-level implementations may operate directly on the underlying built-in storage. For example, a `dict` subclass that overrides only `__setitem__` should not assume `dict.update(...)` will call that override for each inserted item.

A fragile example:

```python
class FragileLowercaseDict(dict[str, int]):
    def __setitem__(self, key: str, value: int) -> None:
        super().__setitem__(key.lower(), value)

fragile = FragileLowercaseDict()
fragile["REGION"] = 1
# Some inherited bulk operations can bypass the intended normalization hook.
```

For custom mapping behavior, `collections.UserDict` often gives a more predictable delegation model. This is the approach called out by the roadmap:

```python
from collections import UserDict

class CaseInsensitiveDict(UserDict[str, object]):
    def __setitem__(self, key: str, value: object) -> None:
        super().__setitem__(key.lower(), value)

    def __getitem__(self, key: str) -> object:
        return super().__getitem__(key.lower())

config = CaseInsensitiveDict({"region": "ap-south-1"})
config["ENV"] = "production"
print(config["REGION"])  # ap-south-1
print(config["env"])     # production
```

This sample assumes string keys. A production version should validate keys explicitly if non-string keys must be rejected, and should decide whether `in`, `get`, deletion, and bulk update normalize keys consistently. The lesson is that a mapping's whole public API must preserve its invariant—not only one assignment method.

`collections.UserList` provides a similar wrapper pattern for list-like behavior. Composition is also a strong default: keep a built-in list or dict as an internal field and implement only the interface your abstraction needs.

### Choosing an approach

| Approach | Use when | Watch out for |
|---|---|---|
| Compose around `list`/`dict` | You need a focused domain abstraction and control over exposed operations. | Decide which list/dict features to forward. |
| Subclass `list`/`dict` | You need genuine substitutability and understand inherited behavior. | Built-in operations may not call your overridden hooks consistently. |
| `UserList` / `UserDict` | You want wrapper behavior with delegated operations that are easier to customize. | Still define and test the complete desired semantics. |

## 16. Multidimensional indexing: tuples and `Ellipsis`

When Python evaluates `obj[1, 2]`, it passes a **tuple** `(1, 2)` to `__getitem__`. For `obj[1:3, ::2]`, it passes a tuple containing two slice objects. This convention is used by array libraries and is useful for custom grid, tensor, or table abstractions.

```python
class Grid:
    def __init__(self, rows: list[list[int]]) -> None:
        self._rows = [list(row) for row in rows]

    def __getitem__(self, key):
        if isinstance(key, tuple):
            row_key, column_key = key
            if isinstance(row_key, int) and isinstance(column_key, int):
                return self._rows[row_key][column_key]
            raise NotImplementedError("this teaching Grid supports integer pairs only")
        return self._rows[key]

grid = Grid([[1, 2, 3], [4, 5, 6]])
print(grid[1, 2])  # 6
print(grid[0])     # [1, 2, 3]
```

A full multidimensional container must define what combinations of integers, slices, and `Ellipsis` mean, including bounds and result shape. Do not claim NumPy-compatible semantics unless you actually implement them.

The literal `...` is the singleton `Ellipsis` object. Array libraries commonly use it as a placeholder for one or more unspecified dimensions. Your class can support it if that is part of the API, but Python does not automatically expand `Ellipsis` for a custom class.

```python
key = (..., slice(None, None, 2))
print(key[0] is Ellipsis)  # True
print(key[1])             # slice(None, None, 2)
```

## 17. Lazy views versus materialized lists

A view exposes data through an interface without necessarily copying every item into a new list. Views are valuable when data is large because materializing a million-item list consumes additional memory and may add latency. Dictionary views such as `mapping.keys()` are standard examples: they reflect the mapping's current keys rather than returning a new list each time.

```python
config = {"region": "ap-south-1"}
keys_view = config.keys()
config["environment"] = "production"
print(list(keys_view))  # ['region', 'environment']
```

When designing a custom view, document:

- whether it is live or snapshot-based;
- whether it holds a reference to the source;
- what happens if the source changes during iteration;
- whether indexing or `len()` is supported;
- whether iteration is repeatable;
- whether it can keep a large source object alive longer than expected.

A lazy view is not automatically better. It can complicate consistency, lifetime, and concurrent modification semantics. Choose based on scale and user expectations.

## 18. `__length_hint__`: an optimization hint, not a promise

`__length_hint__` may provide an estimate of how many items an iterator is likely to produce. Some consumers can use the estimate to preallocate storage. It is optional, and the result is only a hint: correctness must never depend on it being exact.

```python
class CountingIterator:
    def __init__(self, stop: int) -> None:
        self._next_value = 0
        self._stop = stop

    def __iter__(self):
        return self

    def __next__(self) -> int:
        if self._next_value >= self._stop:
            raise StopIteration
        value = self._next_value
        self._next_value += 1
        return value

    def __length_hint__(self) -> int:
        return max(0, self._stop - self._next_value)

iterator = CountingIterator(3)
print(next(iterator))
print(iterator.__length_hint__())  # 2
print(list(iterator))              # [1, 2]
```

Most application code does not need to implement this. Profile first, and ensure the estimate is non-negative and safe. The iterator must still terminate correctly through `StopIteration`; the hint does not replace the iterator protocol.

## 19. Typing and abstract collection interfaces

The roadmap previews collection types from `collections.abc` and typing concepts that will be studied more directly in Lesson 10. These interfaces help communicate which behavior a class promises.

Common shapes include:

- `Sized`: supports `len(obj)`;
- `Iterable[T]`: can be iterated to produce values of type `T`;
- `Container[T]`: supports membership testing;
- `Collection[T]`: combines sized, iterable, and container behavior;
- `Sequence[T]`: an ordered, indexable collection with sequence semantics.

Use `collections.abc` for runtime abstract base classes and `typing` annotations where appropriate. A type annotation is documentation for tools and readers; it does not by itself enforce runtime behavior.

```python
from collections.abc import Collection, Sequence


def count_items(items: Collection[str]) -> int:
    return len(items)


def first_item(items: Sequence[str]) -> str:
    if not items:
        raise ValueError("items must not be empty")
    return items[0]

print(count_items({"orders", "payments"}))
print(first_item(("orders", "payments")))
```

A `Collection[T]` promises membership, iteration, and length, but not necessarily integer indexing. A `Sequence[T]` communicates the stronger ordered/indexable contract. Annotate the weakest interface that satisfies your function's needs; this improves reuse and avoids imposing unnecessary constraints.

## 20. Complexity is part of the practical contract

The protocol tells callers what operation is available; it does not guarantee how fast that operation is. State or document complexity where it matters.

| Operation | Typical list-backed behavior | Typical set/dict-backed behavior |
|---|---|---|
| `len(obj)` | O(1) for a normal list | O(1) for a normal set/dict |
| integer indexing | O(1) for a list | Not a standard set/dict operation |
| scan-based membership | O(n) | — |
| hash-based membership | — | O(1) average case, subject to hashing and collisions |
| iteration | O(n) to visit all items | O(n) to visit all items |
| slicing a list | O(k) to copy k selected items | Not generally applicable |

These are typical costs, not universal laws for every custom class. A wrapper around a remote API could make indexing O(network latency), and a lazy object could defer work until iteration. Make those costs visible instead of making expensive behavior look like a cheap list operation.

## 21. Data-engineering case study: a read-only batch of validated records

A useful domain object can expose sequence behavior while keeping its internal storage private. This makes it convenient for transformation code and tests without exposing mutation that could invalidate validation guarantees.

```python
from __future__ import annotations

from collections.abc import Iterator
from typing import TypedDict


class OrderRecord(TypedDict):
    order_id: str
    amount_cents: int


class ValidatedOrderBatch:
    """Read-only, in-memory batch of already validated order records."""

    def __init__(self, records: list[OrderRecord]) -> None:
        copied = [dict(record) for record in records]
        for position, record in enumerate(copied):
            if not isinstance(record.get("order_id"), str) or not record["order_id"]:
                raise ValueError(f"record {position}: order_id must be a non-empty string")
            amount = record.get("amount_cents")
            if isinstance(amount, bool) or not isinstance(amount, int) or amount < 0:
                raise ValueError(f"record {position}: amount_cents must be a non-negative integer")
        self._records: tuple[OrderRecord, ...] = tuple(copied)  # type: ignore[assignment]
        self._ids = frozenset(record["order_id"] for record in self._records)

    def __len__(self) -> int:
        return len(self._records)

    def __getitem__(self, index: int | slice) -> OrderRecord | "ValidatedOrderBatch":
        if isinstance(index, slice):
            return ValidatedOrderBatch(list(self._records[index]))
        return dict(self._records[index])  # do not expose the stored dictionary itself

    def __iter__(self) -> Iterator[OrderRecord]:
        for record in self._records:
            yield dict(record)

    def __contains__(self, order_id: object) -> bool:
        return order_id in self._ids

orders = ValidatedOrderBatch([
    {"order_id": "o-100", "amount_cents": 2500},
    {"order_id": "o-101", "amount_cents": 0},
])

print(len(orders))                 # 2
print(orders[0])                   # {'order_id': 'o-100', 'amount_cents': 2500}
print([row["order_id"] for row in orders])
print("o-101" in orders)            # True: indexed membership
print("o-999" in orders)            # False
print([row["order_id"] for row in orders[:1]])
```

### Design notes

- The batch validates input at construction, then stores a tuple to prevent changes to the outer collection.
- It returns copied dictionaries so callers cannot mutate the internal record dictionaries through indexing or iteration.
- `__contains__` is intentionally defined as membership of an **order ID**, not membership of an entire record. That contract is domain-specific and must be documented; a different design might choose record membership instead.
- Membership uses a `frozenset` for fast lookup, which consumes additional memory.
- A production implementation should use a precise `TypedDict`/immutable record model, and carefully type the defensive copies. This example emphasizes protocol behavior rather than prescribing one canonical data model.

The important lesson: a natural Python interface should preserve domain invariants. Implementing a protocol is not merely adding magic methods; it is defining a reliable public contract.

## 22. Testing container protocols

Test behavior through the public operations callers will use. Include empty collections, boundaries, negative indices, slices, repeated iteration, membership, and exception contracts.

```python
from __future__ import annotations

# Save as test_container_protocols.py and run: pytest -q
import pytest


class RecordBatch:
    def __init__(self, records: list[str]) -> None:
        self._records = list(records)

    def __len__(self) -> int:
        return len(self._records)

    def __getitem__(self, index: int | slice) -> str | "RecordBatch":
        result = self._records[index]
        if isinstance(index, slice):
            return RecordBatch(result)
        return result

    def __iter__(self):
        return iter(self._records)

    def __contains__(self, value: object) -> bool:
        return value in self._records


def test_len_and_truthiness() -> None:
    assert len(RecordBatch([])) == 0
    assert not RecordBatch([])
    assert bool(RecordBatch(["x"]))


def test_indexing_and_slicing() -> None:
    batch = RecordBatch(["a", "b", "c", "d"])
    assert batch[0] == "a"
    assert batch[-1] == "d"
    assert list(batch[1:3]) == ["b", "c"]
    assert list(batch[::-1]) == ["d", "c", "b", "a"]
    with pytest.raises(IndexError):
        _ = batch[99]


def test_iterates_repeatedly() -> None:
    batch = RecordBatch(["a", "b"])
    assert list(batch) == ["a", "b"]
    assert list(batch) == ["a", "b"]


def test_membership() -> None:
    batch = RecordBatch(["a", "b"])
    assert "b" in batch
    assert "missing" not in batch
```

### Additional test ideas

- A slice preserves the intended type and does not unexpectedly alias mutable state.
- An empty collection has the expected truthiness.
- A one-shot iterator is not accidentally presented as a reusable container.
- Membership semantics match the documentation (IDs, keys, records, or values).
- Unknown mapping keys raise `KeyError`; out-of-range sequence indices raise `IndexError`.
- A large collection's membership operation has an acceptable complexity profile.
- Mutating operations preserve all internal indexes and validation rules.

## 23. Common mistakes and how to avoid them

| Mistake | Why it is a problem | Better approach |
|---|---|---|
| Returning a list from every custom slice without considering the API | Callers may expect the custom abstraction to be preserved. | Return the custom type or document why the result is a list/view. |
| Defining `__iter__` as `return self` without implementing `__next__` | The result is not a valid iterator. | Return `iter(self._items)` or yield items from a generator. |
| Returning `self` from a reusable container's `__iter__` | Iteration state may be shared and later loops may start partway through. | Return a fresh iterator for each call. |
| Returning `None` for an invalid sequence index | It hides out-of-range errors and can break legacy iteration termination. | Raise `IndexError` for invalid integer indices. |
| Assuming `in` is always fast | Iteration fallback can scan every item. | Add a suitable index/set when profiling and semantics justify it. |
| Subclassing `dict` and overriding only `__setitem__` | Inherited bulk operations may bypass the intended invariant hook. | Use composition or `UserDict`; test all mutation paths. |
| Making a view's copy/live behavior unclear | Callers cannot reason about mutation and consistency. | Document whether the result is a snapshot or live view. |
| Using `__len__` for expensive remote counts | `len(obj)` appears cheap but triggers costly work. | Cache a known size, expose a separate explicit method, or omit `__len__`. |
| Implementing `__index__` with rounding | Indexing requires an exact integer interpretation. | Use `__index__` only for exact integer-like values. |
| Treating `__length_hint__` as exact | A hint is not a correctness guarantee. | Keep iteration correct regardless of the estimate. |

## 24. Practice exercises

Try each exercise before reading the solution.

### Exercise 1 — Protocol mapping

For each expression, identify the primary protocol method involved: `len(batch)`, `batch[2]`, `for row in batch`, `row in batch`, `del batch[1]`.

### Exercise 2 — Implement a read-only sequence

Implement `StringBatch` that stores strings and supports `len()`, integer indexing, negative indexing, slicing that returns `StringBatch`, and repeatable iteration. Invalid integer indices must raise `IndexError`.

### Exercise 3 — Improve membership

A class stores 500,000 unique string IDs in a list. Explain the expected cost of `id in collection` using iteration fallback, and implement an additional index to improve average membership speed. State the memory trade-off.

### Exercise 4 — Legacy fallback

Implement a class that only defines `__getitem__` over a list. Demonstrate that `list(obj)` works. Then explain why a new class should usually still implement `__iter__` explicitly.

### Exercise 5 — Mapping invariants

A case-insensitive mapping lowercases keys in `__setitem__` but inherits `update`, `get`, and membership behavior. Identify at least three operations that must be tested or normalized to make the public behavior consistent. Would you choose `dict` subclassing, `UserDict`, or composition?

### Exercise 6 — Multidimensional indexing

Write a class whose `__getitem__` prints `repr(key)`. Show the values of `key` for `obj[1, 2]`, `obj[1:3, ::2]`, and `obj[..., 0]`. Explain why the first two are tuples.

### Exercise 7 — Review a flawed iterator

Why is the following implementation incomplete? Fix it.

```python
class NumberSource:
    def __init__(self, values: list[int]) -> None:
        self.values = values

    def __iter__(self):
        return self
```

### Exercise 8 — Design review

You are building a `RemoteQueryResults` class backed by an API. The API can stream rows but does not know the total count without a separate expensive request. Which protocols would you implement? Explain why you might avoid `__len__` and integer `__getitem__`.

## 25. Exercise solutions

### Solution 1

- `len(batch)` → `__len__`.
- `batch[2]` → `__getitem__`.
- `for row in batch` → `__iter__` when available; otherwise Python may use the legacy integer-`__getitem__` fallback.
- `row in batch` → `__contains__` when available; otherwise iteration fallback.
- `del batch[1]` → `__delitem__`.

### Solution 2

```python
from __future__ import annotations

class StringBatch:
    def __init__(self, values: list[str]) -> None:
        self._values = list(values)

    def __len__(self) -> int:
        return len(self._values)

    def __getitem__(self, index: int | slice) -> str | "StringBatch":
        result = self._values[index]
        if isinstance(index, slice):
            return StringBatch(result)
        return result

    def __iter__(self):
        return iter(self._values)
```

The underlying list provides negative indexing, slice normalization, and `IndexError` for invalid integer indices.

### Solution 3

A list-backed membership fallback is O(n) in the worst case because Python may examine every ID. Store a `set` or `frozenset` alongside the ordered list to get O(1) average-case membership. The trade-off is additional memory and the need for hashable IDs. Keep the list if order/duplicates matter and the set only as an index.

### Solution 4

```python
class LegacyValues:
    def __init__(self, values: list[str]) -> None:
        self._values = list(values)

    def __getitem__(self, index: int) -> str:
        return self._values[index]

print(list(LegacyValues(["a", "b"])))  # ['a', 'b']
```

It works because indexing starts at zero and eventually raises `IndexError`. Explicit `__iter__` makes the intent clear and lets the implementation choose an iterator independent of integer indexing.

### Solution 5

Test and define semantics for assignment, `update`, `get`, `in`, deletion, construction from another mapping, and possibly `setdefault`/`pop`. A `UserDict` wrapper or composition is usually easier to reason about than assuming every built-in `dict` operation will route through an overridden `__setitem__`. Normalize all relevant keys at the public API boundary.

### Solution 6

```python
class ShowKey:
    def __getitem__(self, key):
        print(repr(key))
        return key

obj = ShowKey()
obj[1, 2]       # (1, 2)
obj[1:3, ::2]   # (slice(1, 3, None), slice(None, None, 2))
obj[..., 0]     # (Ellipsis, 0)
```

The comma in subscription syntax packages multiple index components into a tuple; slices are `slice` objects and `...` is `Ellipsis`.

### Solution 7

It returns `self` but does not implement `__next__`, so it is not an iterator. A reusable container should return a new iterator:

```python
class NumberSource:
    def __init__(self, values: list[int]) -> None:
        self._values = list(values)

    def __iter__(self):
        return iter(self._values)
```

If the object itself is intended to be a one-shot iterator, it must implement `__next__` and manage its own iteration state.

### Solution 8

Implement `__iter__` for streaming. Avoid `__len__` if the only way to know the total count is an expensive remote call and that cost would surprise callers. Avoid integer `__getitem__` if the API cannot efficiently retrieve an arbitrary position; sequence syntax would imply random-access behavior the backend does not provide. Expose explicit methods such as `fetch_page()` or `count_remote()` for operations with network costs.

## 26. Self-check

Answer without looking at the solutions.

1. How does Python iterate an object that only defines integer-based `__getitem__`?
2. What does `obj[1:3, 0]` pass to `__getitem__`?
3. Why might `UserDict` be preferable to subclassing `dict` for validation and key normalization?
4. When does Python use `__len__` for truthiness?
5. Why should a reusable container usually return a fresh iterator rather than `self`?
6. What exception should a sequence normally raise for an out-of-range integer index? What exception is conventional for a missing mapping key?
7. What is the complexity difference between scanning a list for membership and using a set index?
8. What is the difference between `__index__` and `__int__`?
9. Why is `__length_hint__` not a correctness guarantee?
10. What should a custom class define before claiming support for multidimensional indexing and `Ellipsis`?

### Answer key

1. Python may call `__getitem__(0)`, `__getitem__(1)`, and so on until `IndexError` signals the end.
2. A tuple `(slice(1, 3, None), 0)`.
3. Wrapper-based delegation makes custom mapping behavior easier to centralize; built-in operations on a `dict` subclass may bypass overridden Python hooks.
4. When `__bool__` is absent and `__len__` exists; zero length is false, nonzero length is true.
5. A fresh iterator supports independent/repeated passes without sharing iteration position.
6. `IndexError` for sequence index out of range; `KeyError` for a missing mapping key.
7. List scan is O(n) worst case; set membership is O(1) average case, with extra memory and hashability requirements.
8. `__index__` represents an exact integer for index contexts; `__int__` provides integer conversion and may have different semantics.
9. It is only an estimate used as an optimization hint; iteration must remain correct if the hint is absent or imperfect.
10. The class must define the meaning of tuple indices, slices, dimension combinations, and `Ellipsis`, including result and error semantics.

## 27. Readiness checklist

You are ready to move on when you can:

- [ ] Explain the difference between a container, iterable, iterator, sequence, and mapping.
- [ ] Implement and test `__len__`, `__getitem__`, `__iter__`, and `__contains__`.
- [ ] Explain both iteration and membership fallbacks.
- [ ] Handle slicing, negative indexing, and sequence/mapping exceptions correctly.
- [ ] Explain `__setitem__`, `__delitem__`, `__missing__`, `__reversed__`, `__index__`, `__bool__`, and `__length_hint__` at a practical level.
- [ ] Choose intentionally between composition, built-in subclassing, `UserDict`, and `UserList`.
- [ ] Explain when views are useful and document their mutation semantics.
- [ ] Design tests that cover empty inputs, boundaries, repeatability, and complexity-sensitive membership.
- [ ] Explain why a remote/streaming result source may not be a sequence.

## Key takeaways

1. Python protocols make custom objects cooperate with built-in syntax; implement only the behaviors your abstraction can support honestly.
2. `__getitem__` supports indexing or key lookup, and slices arrive as `slice` objects. The return type of a slice is a design decision that should be documented.
3. A reusable container should usually return a fresh iterator. The legacy `__getitem__` fallback exists, but new code should generally implement `__iter__` explicitly.
4. `in` uses `__contains__` when available and otherwise falls back to iteration. A suitable index can improve performance, but has memory and semantic trade-offs.
5. `__len__` also affects default truthiness when `__bool__` is absent; do not make it expensive or misleading.
6. Mapping and sequence protocols have different error conventions: `KeyError` for missing keys and `IndexError` for out-of-range sequence indices.
7. A correct container API is about semantic consistency, predictable cost, and preserving invariants—not merely adding special methods.
