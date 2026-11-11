# Container Protocols: `__getitem__`, `__len__`, `__iter__`, and `__contains__`

> **Stage 1 — Programming & Computational Thinking**  
> **Module 11 — Advanced Python Data Model and Object Design**  
> **Lesson 03** · Python 3.12+

## 1. Why this lesson matters

Python containers feel natural because they implement protocols that connect objects to language operations. A custom dataset can support `len(dataset)`, `dataset[10]`, `for row in dataset`, and `row in dataset` without imitating a built-in class's entire implementation.

The authoritative module roadmap places this lesson after rich comparisons and before operator overloading. The project tree places it in `Stage 1 — Programming & Computational Thinking/11-Advanced-Python-Data-Model-and-Object-Design/`.

This lesson follows the Lesson 03 sequence: basic protocol methods and fallbacks; intermediate indexing, mutation, iteration, truthiness, and built-in subclassing; then advanced indexing, views, collection ABCs, and iteration contracts.

## 2. Prerequisites

You should be comfortable with:

- classes, instances, attributes, and methods;
- lists, tuples, dictionaries, slices, and `for` loops;
- exceptions and `raise`;
- iterables, iterators, and generators at an introductory level;
- type annotations and basic `pytest`.

You do not need NumPy or pandas. Their indexing behavior is useful context, but the examples below use the standard library.

## 3. Learning objectives

By the end, you should be able to:

1. Explain what `__len__`, `__getitem__`, `__iter__`, and `__contains__` promise.
2. Predict how `len(x)`, `x[i]`, `for`, and `in` dispatch to these methods.
3. Explain the legacy sequence iteration fallback and membership fallback.
4. Design sequence and mapping behavior with correct indexing, slicing, and exceptions.
5. Distinguish an iterable from an iterator and make containers repeatably iterable.
6. Implement mutation, missing-key behavior, reverse iteration, integer-like indices, truthiness, and length hints where appropriate.
7. Handle tuple-based multi-dimensional keys and `Ellipsis`.
8. Choose between materialized results, lazy views, composition, built-in subclasses, `UserDict`, and `UserList`.
9. Use `collections.abc` to describe and check collection interfaces.
10. Test boundary cases and avoid protocol violations in production code.

---

## 4. The four core container protocols

A protocol is a set of behaviors an object promises. Python often checks for behavior rather than requiring a class to inherit from a particular base class.

| Language operation | Typical special method | Contract |
|---|---|---|
| `len(x)` | `x.__len__()` | Return a non-negative integer representing the number of elements. |
| `x[key]` | `x.__getitem__(key)` | Return the item associated with the key, or raise the appropriate exception. |
| `iter(x)` / `for item in x` | `x.__iter__()` | Return an iterator. |
| `item in x` | `x.__contains__(item)` | Return a truth value indicating membership. |

These methods are not interchangeable. A class can support indexing without being a good repeatable iterable, and it can support membership without supporting indexing.

### 4.1 `__len__`: size and default truthiness

`len(x)` calls the length protocol. The result must be an integer greater than or equal to zero; a negative result raises `ValueError`, and a non-integer result raises `TypeError`.

When a class has no `__bool__`, truth testing uses `__len__` if it exists: zero means false, non-zero means true.

```python
class Batch:
    def __init__(self, rows: list[str]) -> None:
        self._rows = rows

    def __len__(self) -> int:
        return len(self._rows)


batch = Batch(["r1", "r2"])
print(len(batch))
print(bool(batch))
print(bool(Batch([])))
```

Expected output:

```text
2
True
False
```

If the class defines `__bool__`, that method controls truthiness instead of `__len__`. Keep the two consistent unless the object has a clearly documented reason not to.

**Do not use `__len__` to trigger expensive remote queries.** A size operation is generally expected to be straightforward. For streaming sources, exact length may be unknown or require consuming the stream; model that explicitly rather than pretending a stream is a fully materialized sequence.

### 4.2 `__getitem__`: indexed access

`obj[key]` passes `key` to `__getitem__`. The key can be an integer, a slice, a string, a tuple, or another object. The class defines what key shapes it accepts.

```python
class Labels:
    def __init__(self, values: list[str]) -> None:
        self._values = values

    def __getitem__(self, index: int | slice) -> str | list[str]:
        return self._values[index]


labels = Labels(["bronze", "silver", "gold", "platinum"])
print(labels[1])
print(labels[-1])
print(labels[1:3])
print(labels[::2])
```

Expected output:

```text
silver
platinum
['silver', 'gold']
['bronze', 'gold']
```

This wrapper delegates indexing to a list, so it inherits that list's integer and slice semantics. Notice, however, that slicing returns a `list`, not a `Labels` instance. That is a design choice—not an automatic property of custom containers.

### 4.3 `__iter__`: iteration

`iter(obj)` calls `obj.__iter__()` when present. It must return an iterator, which is an object implementing `__next__()` and raising `StopIteration` when exhausted.

A simple and usually effective implementation is to return an iterator over the internal collection:

```python
class Team:
    def __init__(self, names: list[str]) -> None:
        self._names = list(names)

    def __iter__(self):
        return iter(self._names)


team = Team(["Asha", "Ben"])
print(list(team))
print(list(team))  # a fresh iterator makes the container repeatable
```

Expected output:

```text
['Asha', 'Ben']
['Asha', 'Ben']
```

A generator method is also useful:

```python
def __iter__(self):
    for row in self._rows:
        yield row
```

Calling a generator function creates a new generator object each time, so repeated calls to `iter(container)` get independent iteration state.

### 4.4 `__contains__`: membership

`item in obj` uses `obj.__contains__(item)` if it exists. The result is interpreted as a truth value. If `__contains__` is absent, Python attempts membership by iterating over the object; if the object is not iterable, the legacy sequence protocol may be used.

```python
class AllowedCodes:
    def __init__(self, codes: list[str]) -> None:
        self._codes = set(codes)

    def __contains__(self, code: object) -> bool:
        return code in self._codes


allowed = AllowedCodes(["OK", "WARN"])
print("OK" in allowed)
print("MISSING" in allowed)
```

Expected output:

```text
True
False
```

The explicit implementation uses a set, giving average-case constant-time membership for ordinary hashable codes. A list-backed implementation would generally scan items linearly. If the incoming value can be unhashable, `code in self._codes` can raise `TypeError`; decide whether that is acceptable or whether your API should normalize or reject such values explicitly.

---

## 5. A complete read-only sequence: `Deck`

The roadmap uses a deck of cards to introduce the basic sequence protocol. This implementation makes the behavior explicit and demonstrates length, integer indexing, slices, iteration, and membership.

```python
from collections.abc import Iterator, Sequence
from typing import overload


class Deck(Sequence[tuple[str, str]]):
    RANKS = tuple([str(n) for n in range(2, 11)] + list("JQKA"))
    SUITS = ("spades", "diamonds", "clubs", "hearts")

    def __init__(self) -> None:
        self._cards = tuple(
            (rank, suit)
            for suit in self.SUITS
            for rank in self.RANKS
        )

    def __len__(self) -> int:
        return len(self._cards)

    @overload
    def __getitem__(self, index: int) -> tuple[str, str]: ...

    @overload
    def __getitem__(self, index: slice) -> tuple[tuple[str, str], ...]: ...

    def __getitem__(
        self, index: int | slice
    ) -> tuple[str, str] | tuple[tuple[str, str], ...]:
        return self._cards[index]

    def __iter__(self) -> Iterator[tuple[str, str]]:
        return iter(self._cards)

    def __contains__(self, card: object) -> bool:
        return card in self._cards


deck = Deck()
print(len(deck), deck[0], deck[-1])
print(deck[:3])
print(("A", "hearts") in deck)
print(("JOKER", "stars") in deck)
```

Expected output:

```text
52 ('2', 'spades') ('A', 'hearts')
(('2', 'spades'), ('3', 'spades'), ('4', 'spades'))
True
False
```

### What this implementation promises

- `__len__` returns the number of cards.
- Integer indexing follows tuple behavior: negative indices count from the end; out-of-range indices raise `IndexError`.
- Slicing returns a tuple of cards, not a mutable list.
- `__iter__` returns a fresh tuple iterator.
- `__contains__` checks the tuple directly.
- Because it subclasses `Sequence`, it is communicating and implementing a read-only sequence interface.

In a small example, explicit `__iter__` and `__contains__` are clear. For many sequence classes, however, implementing `__len__` and `__getitem__` is enough for some iteration and membership operations to work through fallback behavior. Prefer explicit methods when they improve clarity or performance.

---

## 6. Python's fallback behavior

### 6.1 Legacy sequence iteration fallback

If `__iter__` is missing, Python can iterate using the legacy sequence protocol: it repeatedly calls `obj[0]`, `obj[1]`, and so on until `__getitem__` raises `IndexError`.

```python
class LegacyNumbers:
    def __init__(self, values: list[int]) -> None:
        self._values = list(values)

    def __getitem__(self, index: int) -> int:
        return self._values[index]


numbers = LegacyNumbers([10, 20, 30])
print(list(numbers))
```

Expected output:

```text
[10, 20, 30]
```

This fallback is useful to recognize in existing code, but do not rely on it as the preferred design for a new container. An explicit `__iter__` communicates intent and may be more efficient.

**Important:** the sequence fallback terminates on `IndexError`. If a custom `__getitem__` raises `KeyError`, `ValueError`, or another exception at the end, iteration does not treat that exception as normal exhaustion.

A mapping should not accidentally behave like a sequence. For example, `mapping[0]` normally means “look up key `0`,” not “return the first value.”

### 6.2 Membership fallback when `__contains__` is absent

When `__contains__` is absent, `item in obj` searches by iteration. That means it compares the sought item against each yielded element and may consume a one-shot iterator.

```python
class LinearCodes:
    def __init__(self, codes: list[str]) -> None:
        self._codes = list(codes)

    def __iter__(self):
        return iter(self._codes)


codes = LinearCodes(["A", "B", "C"])
print("B" in codes)
print("Z" in codes)
```

Expected output:

```text
True
False
```

For a large collection, a custom `__contains__` may use an index, set, or database query. Document performance and side effects: membership should not unexpectedly consume a stream or issue an expensive query unless that is the abstraction's explicit contract.

---

## 7. Indexing, negative indices, slices, and slice objects

### 7.1 Integer indexing and boundaries

For sequence-like objects, a common contract is:

- valid non-negative indices identify elements from the beginning;
- valid negative indices identify elements from the end;
- an index outside the sequence raises `IndexError`.

If you delegate to a built-in list or tuple, these rules come for free. If you implement indexing yourself, test the boundaries carefully.

```python
values = [11, 22, 33]
print(values[0], values[-1])
try:
    values[3]
except IndexError as exc:
    print(type(exc).__name__)
```

Expected output:

```text
11 33
IndexError
```

Do not silently return `None` for an invalid sequence index. It confuses “there is no element at this position” with “the element exists and its value is `None`.”

### 7.2 What a slice passes to `__getitem__`

For `obj[start:stop:step]`, Python constructs a `slice` object and passes it as the key. For multidimensional expressions, the key may be a tuple containing integers, slices, and other values.

```python
class ShowKey:
    def __getitem__(self, key: object) -> object:
        print(type(key).__name__, repr(key))
        return key


x = ShowKey()
x[1:8:2]
x[1:3, 0]
```

Expected output:

```text
slice slice(1, 8, 2)
tuple (slice(1, 3, None), 0)
```

A `slice` has `.start`, `.stop`, and `.step` attributes. Any of these can be `None`. To apply a slice to a known sequence length, use `slice_obj.indices(length)`, which normalizes the bounds and step.

```python
s = slice(1, None, 2)
print(s.start, s.stop, s.step)
print(s.indices(8))
```

Expected output:

```text
1 None 2
(1, 8, 2)
```

### 7.3 Preserve the container type on slicing

A custom sequence often should return the same abstraction from a slice. That is not mandatory for every class, but returning an unrelated list can surprise callers and lose validation or metadata.

```python
from __future__ import annotations

from collections.abc import Sequence
from typing import overload


class SampleBatch(Sequence[int]):
    def __init__(self, values: Sequence[int]) -> None:
        self._values = tuple(values)

    def __len__(self) -> int:
        return len(self._values)

    @overload
    def __getitem__(self, index: int) -> int: ...

    @overload
    def __getitem__(self, index: slice) -> "SampleBatch": ...

    def __getitem__(self, index: int | slice) -> int | "SampleBatch":
        result = self._values[index]
        if isinstance(index, slice):
            return SampleBatch(result)
        return result

    def __iter__(self):
        return iter(self._values)


batch = SampleBatch([3, 6, 9, 12])
subset = batch[1:3]
print(type(subset).__name__, list(subset))
```

Expected output:

```text
SampleBatch [6, 9]
```

This design deliberately materializes a new immutable tuple for each slice. It is a copy, not a view. If the underlying data is huge, a view object may be a better choice.

---

## 8. Mutable containers: `__setitem__` and `__delitem__`

Mutable sequences may implement:

- `__setitem__(key, value)` for `obj[key] = value`;
- `__delitem__(key)` for `del obj[key]`.

Their accepted keys should be consistent with `__getitem__`. Built-in lists allow integer and slice assignment/deletion, but a custom type can define a narrower contract.

```python
class MutableSamples:
    def __init__(self, values: list[int]) -> None:
        self._values = list(values)

    def __len__(self) -> int:
        return len(self._values)

    def __getitem__(self, index: int | slice) -> int | list[int]:
        return self._values[index]

    def __setitem__(self, index: int | slice, value) -> None:
        self._values[index] = value

    def __delitem__(self, index: int | slice) -> None:
        del self._values[index]

    def __iter__(self):
        return iter(self._values)


samples = MutableSamples([10, 20, 30, 40])
samples[1] = 99
del samples[-1]
samples[1:2] = [21, 22]
print(list(samples))
```

Expected output:

```text
[10, 21, 22, 30]
```

The type annotations for `value` above are intentionally broad because integer assignment and slice assignment have different shapes. Production code should use overloads or a narrower API if static typing is important.

A mutable container must also define its aliasing policy: does a slice produce a copy, a view, or a new container sharing internal storage? Make that contract explicit.

---

## 9. Mapping behavior and `__missing__`

Sequences and mappings use different key conventions:

- Sequence-like integer indexing normally raises `IndexError` when out of range.
- Mapping lookup raises `KeyError` when a key is absent.
- A `dict` subclass can define `__missing__(key)` to customize lookup for absent keys accessed through `d[key]`.

`dict.__missing__` is a hook for subclasses; it is not called by `dict.get()` in the ordinary dictionary implementation.

```python
class ZeroDefaultDict(dict[str, int]):
    def __missing__(self, key: str) -> int:
        return 0


counts = ZeroDefaultDict({"valid": 3})
print(counts["valid"])
print(counts["unknown"])
print(counts.get("other"))
print("other" in counts)
```

Expected output:

```text
3
0
None
False
```

`counts["unknown"]` returns `0` because `__missing__` is called. But that does not insert the missing key. The membership test remains false, and `get()` returns its default `None`.

If you want a missing lookup to insert a value, implement that behavior deliberately or use `collections.defaultdict` where appropriate. Do not assume `__missing__` changes membership, iteration, or all lookup methods.

### 9.1 A small mapping wrapper

```python
from collections.abc import Iterator, Mapping


class Config(Mapping[str, str]):
    def __init__(self, data: dict[str, str]) -> None:
        self._data = dict(data)

    def __getitem__(self, key: str) -> str:
        return self._data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)


config = Config({"region": "ap-south-1", "mode": "batch"})
print(config["mode"])
print(list(config))
print("region" in config)
```

Expected output:

```text
batch
['region', 'mode']
True
```

For a mapping, iteration normally yields keys. This is why `"region" in config` checks keys rather than values. A `Mapping` implementation needs `__getitem__`, `__iter__`, and `__len__`; the ABC supplies useful mixin behavior.

---

## 10. Iterable versus iterator

An **iterable** can produce an iterator. An **iterator** maintains traversal state and supplies the next item through `__next__`.

The key distinction is repeatability:

- A container such as a list should usually return a fresh iterator each time.
- An iterator is normally one-shot: once exhausted, subsequent calls continue to raise `StopIteration`.

### 10.1 The incorrect `return self` pattern

This class is broken because `__iter__` returns `self`, but the object has no `__next__`:

```python
class Broken:
    def __iter__(self):
        return self


# iter(Broken()) raises TypeError: iter() returned non-iterator
```

Returning `self` is valid only if the object is itself an iterator, normally by implementing `__next__` as well. Even then, using the same stateful iterator object as a reusable container is usually a mistake because nested or repeated loops interfere with each other.

### 10.2 A separate iterator object

```python
from collections.abc import Iterator


class CountdownIterator(Iterator[int]):
    def __init__(self, start: int) -> None:
        self._current = start

    def __iter__(self) -> "CountdownIterator":
        return self

    def __next__(self) -> int:
        if self._current < 1:
            raise StopIteration
        result = self._current
        self._current -= 1
        return result


it = CountdownIterator(3)
print(next(it))
print(list(it))
print(list(it))
```

Expected output:

```text
3
[2, 1]
[]
```

This is a valid one-shot iterator. A reusable `Countdown` container should instead have `__iter__` create a new `CountdownIterator` every time.

### 10.3 Repeatable container with a fresh generator

```python
class Countdown:
    def __init__(self, start: int) -> None:
        self._start = start

    def __iter__(self):
        current = self._start
        while current >= 1:
            yield current
            current -= 1


countdown = Countdown(3)
print(list(countdown))
print(list(countdown))
```

Expected output:

```text
[3, 2, 1]
[3, 2, 1]
```

Do not implement `__iter__` by returning a single generator stored on `self` if callers expect the container to be repeatable. That generator is consumed once.

---

## 11. `__reversed__`, `__index__`, `__bool__`, and `__length_hint__`

These methods are useful in specific designs. They are not mandatory for every container.

### 11.1 `__reversed__`

`reversed(obj)` first uses the `__reversed__` method when available. Otherwise, the sequence fallback requires `__len__` and integer indexing from `0` through `len(obj) - 1`.

```python
class ReverseLabels:
    def __init__(self, labels: list[str]) -> None:
        self._labels = tuple(labels)

    def __len__(self) -> int:
        return len(self._labels)

    def __getitem__(self, index: int) -> str:
        return self._labels[index]

    def __reversed__(self):
        return reversed(self._labels)


labels = ReverseLabels(["a", "b", "c"])
print(list(reversed(labels)))
```

Expected output:

```text
['c', 'b', 'a']
```

An explicit `__reversed__` is useful when the storage has an efficient reverse traversal that differs from repeatedly indexing from the end.

### 11.2 `__index__`: integer-like objects

`__index__` tells Python that an object represents an exact integer, suitable for operations requiring an integer index. It must return an `int` (not merely a value convertible to one). It is different from `__int__`, which may represent a lossy conversion.

```python
class Index:
    def __init__(self, value: int) -> None:
        self._value = value

    def __index__(self) -> int:
        return self._value


values = ["zero", "one", "two"]
print(values[Index(2)])
print(values[:Index(2)])
```

Expected output:

```text
two
['zero', 'one']
```

Use this protocol only if your type has a clear exact-integer meaning. Do not implement it for values such as fractional measurements that would require rounding.

### 11.3 Truthiness through `__len__`

If `__bool__` is absent, a class with `__len__` is false when its length is zero and true otherwise.

```python
class ResultSet:
    def __init__(self, rows: list[str]) -> None:
        self._rows = rows

    def __len__(self) -> int:
        return len(self._rows)


print(bool(ResultSet([])))
print(bool(ResultSet(["row"])))
```

Expected output:

```text
False
True
```

If `__bool__` is implemented, Python uses it instead. Avoid surprising contradictions such as `len(x) == 0` while `bool(x)` is true unless that distinction is intentional and documented.

### 11.4 `__length_hint__`

`operator.length_hint(obj, default)` asks for an estimated length when an exact length is unavailable. It can help consumers preallocate storage, but it is only a hint and does not replace `__len__`.

```python
from operator import length_hint


class EstimatedRows:
    def __iter__(self):
        yield from ("r1", "r2", "r3")

    def __length_hint__(self) -> int:
        return 3


rows = EstimatedRows()
print(length_hint(rows, 0))
print(list(rows))
```

Expected output:

```text
3
['r1', 'r2', 'r3']
```

Length hints should be non-negative integer estimates. They should not be used as a correctness mechanism: callers must still handle more or fewer items than estimated.

---

## 12. Multi-dimensional indexing, tuple keys, and `Ellipsis`

Python does not give every custom container special multi-dimensional behavior. It passes the indexing expression as a key, and the container decides what that key means.

- `obj[1, 2]` passes `(1, 2)`.
- `obj[1:3, ::2]` passes `(slice(1, 3, None), slice(None, None, 2))`.
- `obj[..., 0]` passes `(Ellipsis, 0)`.

`Ellipsis` is the singleton object written as `...`. Array libraries use it as a compact way to represent omitted dimensions.

```python
class IndexInspector:
    def __getitem__(self, key: object) -> object:
        return key


x = IndexInspector()
print(x[1, 2])
print(x[1:3, ::2])
print(x[..., 0])
print(x[...] is Ellipsis)
```

Expected output:

```text
(1, 2)
(slice(1, 3, None), slice(None, None, 2))
(Ellipsis, 0)
True
```

### 12.1 A tiny 2D matrix with tuple indexing

This example deliberately supports a limited 2D API: `matrix[row, column]` returns a scalar, and `matrix[row_slice, column_slice]` returns a new nested list. It is an educational implementation, not a NumPy replacement.

```python
class Matrix:
    def __init__(self, rows: list[list[int]]) -> None:
        if rows and any(len(row) != len(rows[0]) for row in rows):
            raise ValueError("matrix rows must have equal length")
        self._rows = [list(row) for row in rows]

    def __getitem__(self, key):
        if not isinstance(key, tuple) or len(key) != 2:
            raise TypeError("use matrix[row, column]")
        row_key, col_key = key

        if isinstance(row_key, int) and isinstance(col_key, int):
            return self._rows[row_key][col_key]

        selected_rows = self._rows[row_key] if isinstance(row_key, slice) else [self._rows[row_key]]
        selected = [
            row[col_key] if isinstance(col_key, slice) else [row[col_key]]
            for row in selected_rows
        ]
        if isinstance(row_key, int) and isinstance(col_key, slice):
            return selected[0]
        if isinstance(row_key, slice) and isinstance(col_key, int):
            return [row[0] for row in selected]
        return selected


m = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
print(m[1, 2])
print(m[0:2, 1:3])
print(m[1, 0:2])
```

Expected output:

```text
6
[[2, 3], [5, 6]]
[4, 5]
```

This intentionally small implementation does not support `Ellipsis`, negative-dimension expansion, boolean masks, or arbitrary advanced indexing. State supported key shapes clearly; rejecting unsupported shapes is safer than accidentally returning misleading data.

---

## 13. Lazy views versus materialized lists

For large collections, returning a new list of all values can waste memory and time. A view can expose a live or read-only window over existing data. The standard library's `dict.keys()`, `dict.values()`, and `dict.items()` return dynamic view objects, not lists.

```python
data = {"a": 1, "b": 2}
keys = data.keys()
print(list(keys))
data["c"] = 3
print(list(keys))
```

Expected output:

```text
['a', 'b']
['a', 'b', 'c']
```

The view reflects later dictionary changes. By contrast, `list(data.keys())` materializes a snapshot at that moment.

A custom view should define:

- whether it reflects later changes to the backing collection;
- whether it is read-only;
- what happens if the backing collection changes during iteration;
- whether it supports `len`, membership, and repeatable iteration;
- whether slicing creates another view or a materialized result.

Do not call a result a “view” if it is actually an independent copy. Likewise, do not promise snapshot semantics if the result reads live state.

---

## 14. `collections.abc`: expressing collection interfaces

`collections.abc` provides abstract base classes (ABCs) describing common collection shapes. They are useful for documentation, runtime checks, and inherited mixin methods.

| ABC | Core idea | Common required methods |
|---|---|---|
| `Sized` | Has a size | `__len__` |
| `Iterable` | Can produce an iterator | `__iter__` |
| `Container` | Supports membership | `__contains__` |
| `Collection` | Sized, iterable, and supports membership | `__len__`, `__iter__`, `__contains__` |
| `Sequence` | Ordered integer-indexed collection | `__len__`, `__getitem__` |
| `Hashable` | Can be passed to `hash()` and used as a dictionary key or set member | `__hash__` returns an integer; equal objects must have equal hashes |

ABC requirements can include abstract methods and mixins. Check the relevant documentation when implementing a more specialized ABC. Inheritance is not the only way to satisfy a protocol: many Python operations use structural behavior. Runtime `isinstance` checks against ABCs have their own rules and should not be treated as a full static type checker.

`Hashable` is a separate concept from `Iterable` or `Iterator`: an object does not need to be hashable to be iterable, and an iterator does not promise a stable collection of values just because it can be hashed. Do not confuse a collection's iteration contract with whether it can be a dictionary key. If an object is used as a dictionary key or set member, its hash and equality behavior must remain suitable while it is stored; mutable collections are commonly unhashable.

```python
from collections.abc import Collection, Sequence


class Codes(Sequence[str]):
    def __init__(self, values: list[str]) -> None:
        self._values = tuple(values)

    def __len__(self) -> int:
        return len(self._values)

    def __getitem__(self, index: int | slice):
        return self._values[index]


codes = Codes(["A", "B"])
print(isinstance(codes, Sequence))
print(isinstance(codes, Collection))
print("B" in codes)
```

Expected output:

```text
True
True
True
```

Because `Sequence` supplies mixin implementations for operations such as iteration and membership based on its primitives, this small class supports more than the methods it explicitly defines. Still test those behaviors, and override a mixin when a more efficient or semantically appropriate implementation is available.

### 14.1 `typing` protocols versus ABCs

For static typing, `typing.Protocol` can describe a structural interface without requiring inheritance. `collections.abc` is the standard runtime collection family. This lesson's focus is the runtime behavior; static structural typing is a preview of the later ABC/typing material in the roadmap.

---

## 15. Built-in subclassing versus composition

Subclassing `list` or `dict` can be convenient, but built-in implementations have optimized operations that may not route through every overridden Python-level method. A subclass that overrides only `__setitem__` cannot assume all bulk operations, constructors, or inherited methods will invoke that override for every inserted item.

### 15.1 Why overriding only `dict.__setitem__` is fragile

```python
class ValidatedDict(dict[str, int]):
    def __setitem__(self, key: str, value: int) -> None:
        if value < 0:
            raise ValueError("value must be non-negative")
        super().__setitem__(key, value)


d = ValidatedDict()
d["a"] = 1
print(d)
d.update({"b": -2})
print(d)
```

Expected output:

```text
{'a': 1}
{'a': 1, 'b': -2}
```

The example illustrates a design hazard in CPython: `dict.update` can bypass a subclass's overridden `__setitem__`. This dispatch detail is an implementation-level behavior, not a portable validation hook to build an invariant around. Do not rely on overriding one method as a universal validation hook for a built-in subclass.

### 15.2 Prefer `UserDict` for dictionary customization

`collections.UserDict` wraps an underlying dictionary and is designed to be easier to customize consistently.

```python
from collections import UserDict


class CaseInsensitiveDict(UserDict[str, int]):
    def __setitem__(self, key: str, value: int) -> None:
        super().__setitem__(key.lower(), value)

    def __getitem__(self, key: str) -> int:
        return super().__getitem__(key.lower())

    def __contains__(self, key: object) -> bool:
        if not isinstance(key, str):
            return False
        return super().__contains__(key.lower())


d = CaseInsensitiveDict()
d.update({"Region": 1})
print(d["REGION"])
print("region" in d)
print(dict(d))
```

Expected output:

```text
1
True
{'region': 1}
```

If validation is important, test every mutation path you expose: direct assignment, `update`, initialization, deletion, and any custom bulk operation.

### 15.3 `UserList` and composition

`collections.UserList` provides a similar wrapper for list customization. For example, it can normalize inserted strings while retaining familiar list operations:

```python
from collections import UserList


class NormalizedTags(UserList[str]):
    def append(self, item: str) -> None:
        super().append(item.strip().lower())


tags = NormalizedTags(["raw"])
tags.append(" CLEAN ")
print(tags)
```

Expected output:

```text
['raw', 'clean']
```

This example customizes `append`, not every possible mutation path. If the invariant must hold for assignment, slice assignment, `extend`, `insert`, and initialization too, override and test those paths or use composition with a smaller controlled API.

Composition—storing an internal list or dictionary and exposing only deliberate methods—is often even clearer when you do not need to emulate the entire built-in API.

Choose:

- **built-in subclassing** when its semantics are truly the semantics you want and you understand inherited methods;
- **`UserDict` / `UserList`** when you need a familiar mutable interface that is easier to customize;
- **composition** when you want a narrow API, invariants, or control over mutation and aliasing.

---

## 16. Practical applications in data engineering and AI

### 16.1 Dataset wrapper

A dataset object can implement `__len__`, `__getitem__`, and `__iter__` so training or evaluation code can request samples naturally. A map-style dataset usually supports random access; a streaming dataset may be iterable without a meaningful exact length or integer indexing.

Avoid claiming both models at once without specifying how they behave. For remote data, decide whether indexing triggers I/O, whether repeated access is cached, and whether `len()` is exact.

### 16.2 Record collection

A typed collection of records can make membership mean “record is present,” “record ID exists,” or “record satisfies a predicate.” These are different semantics. For large datasets, membership by ID may be best served by an index rather than scanning every record.

### 16.3 Lazy partitions and views

A partition view can expose a slice of a larger dataset without copying all rows. Document whether it is live or a snapshot, and whether parent mutations change the view. For distributed systems, a seemingly cheap `len()` or membership test may trigger a job or network request; avoid hiding expensive operations behind simple syntax unless the abstraction clearly communicates the cost.

### 16.4 Configuration and schema objects

A mapping-like configuration object can use `__getitem__`, `__iter__`, and `__len__` while preserving validation and predictable missing-key errors. Use `KeyError` for missing mapping keys and make any defaulting behavior explicit.

---

## 17. Common mistakes and how to avoid them

1. **Returning a list from a slice when callers expect the custom type.** Decide whether slices return a copy, view, or same-type object; test it.
2. **Returning `self` from `__iter__` without implementing `__next__`.** `iter(obj)` then raises `TypeError`. A reusable container should normally return a fresh iterator.
3. **Returning the same exhausted generator every time.** Repeated loops unexpectedly see no values. Create a fresh generator in `__iter__`.
4. **Using the wrong termination exception.** Legacy sequence iteration stops on `IndexError`, not `KeyError`.
5. **Using `KeyError` for sequence boundaries or `IndexError` for missing mapping keys.** Follow the caller's expected abstraction.
6. **Assuming membership always calls `__contains__`.** It falls back to iteration when that method is absent, potentially making a test linear or consuming a one-shot iterator.
7. **Implementing `__len__` with a negative or non-integer result.** Python rejects it. Return a non-negative integer.
8. **Making truthiness surprising.** Without `__bool__`, zero length means false. If `__bool__` overrides this, document the rationale.
9. **Assuming a slice is always a list.** A slice is passed as a `slice` object; your class controls the result.
10. **Assuming `__missing__` affects `get()` or membership.** It is a `dict` subclass hook for `d[key]`; it does not automatically insert or make the key present.
11. **Subclassing `dict` and overriding only `__setitem__`.** Bulk operations such as `update` may bypass the override. Prefer `UserDict` or composition for validation.
12. **Returning a materialized list for a large live collection without considering cost.** Decide whether callers need a snapshot or a lazy view.
13. **Claiming a custom object is a sequence without coherent behavior.** Indexing, length, iteration, and exceptions should agree.
14. **Overpromising multidimensional indexing.** `obj[1, 2]` passes a tuple; your class must parse it. NumPy-specific semantics do not come for free.
15. **Using `__length_hint__` as an exact length.** It is only an estimate and cannot be relied on for correctness.

---

## 18. Debugging checklist

When a custom container behaves unexpectedly, check:

- What exact key reaches `__getitem__`? Temporarily print `type(key)` and `repr(key)`.
- Is the key an `int`, `slice`, tuple of keys, or `Ellipsis`?
- Does an out-of-range sequence index raise `IndexError`?
- Does a missing mapping key raise `KeyError`?
- Does `iter(obj)` return an object with `__next__`?
- Does each `iter(container)` call get fresh state?
- Is iteration finite, and does it terminate normally?
- If `__contains__` is absent, is membership scanning or consuming an iterator?
- Does `len(obj)` return a non-negative integer without unexpected side effects?
- Does `bool(obj)` agree with its documented emptiness semantics?
- Does slicing return the documented copy/view/container type?
- Do `update`, initialization, and other bulk methods preserve invariants?
- Have you tested empty, singleton, negative-index, out-of-range, empty-slice, and stepped-slice cases?

For a minimal debugging harness:

```python
def inspect_key(key: object) -> None:
    print("type:", type(key).__name__)
    print("repr:", repr(key))
```

---

## 19. Pytest tests for the core contracts

Save the following in `test_container_protocols.py`. The tests target the `Deck`, `SampleBatch`, `Matrix`, `Countdown`, `LegacyNumbers`, and `CaseInsensitiveDict` examples above. Put the example classes in an importable module such as `container_protocols_examples.py`, or keep the definitions in the same test file while learning.

```python
from __future__ import annotations

from collections import UserDict
from collections.abc import Collection, Container, Iterable, Sequence, Sized
from operator import length_hint
import pytest


class Deck(Sequence[tuple[str, str]]):
    RANKS = tuple([str(n) for n in range(2, 11)] + list("JQKA"))
    SUITS = ("spades", "diamonds", "clubs", "hearts")

    def __init__(self) -> None:
        self._cards = tuple((rank, suit) for suit in self.SUITS for rank in self.RANKS)

    def __len__(self) -> int:
        return len(self._cards)

    def __getitem__(self, index: int | slice):
        return self._cards[index]


class SampleBatch(Sequence[int]):
    def __init__(self, values: Sequence[int]) -> None:
        self._values = tuple(values)

    def __len__(self) -> int:
        return len(self._values)

    def __getitem__(self, index: int | slice) -> int | SampleBatch:
        result = self._values[index]
        return SampleBatch(result) if isinstance(index, slice) else result


class LegacyNumbers:
    def __init__(self, values: list[int]) -> None:
        self._values = list(values)

    def __getitem__(self, index: int) -> int:
        return self._values[index]


class Countdown:
    def __init__(self, start: int) -> None:
        self._start = start

    def __iter__(self):
        current = self._start
        while current >= 1:
            yield current
            current -= 1


class MutableSamples:
    def __init__(self, values: list[int]) -> None:
        self._values = list(values)

    def __len__(self) -> int:
        return len(self._values)

    def __getitem__(self, index: int | slice):
        return self._values[index]

    def __setitem__(self, index: int | slice, value) -> None:
        self._values[index] = value

    def __delitem__(self, index: int | slice) -> None:
        del self._values[index]

    def __iter__(self):
        return iter(self._values)


class ZeroDefaultDict(dict[str, int]):
    def __missing__(self, key: str) -> int:
        return 0


class Matrix:
    def __init__(self, rows: list[list[int]]) -> None:
        if rows and any(len(row) != len(rows[0]) for row in rows):
            raise ValueError("matrix rows must have equal length")
        self._rows = [list(row) for row in rows]

    def __getitem__(self, key):
        if not isinstance(key, tuple) or len(key) != 2:
            raise TypeError("use matrix[row, column]")
        row_key, col_key = key
        if isinstance(row_key, int) and isinstance(col_key, int):
            return self._rows[row_key][col_key]
        selected_rows = self._rows[row_key] if isinstance(row_key, slice) else [self._rows[row_key]]
        selected = [
            row[col_key] if isinstance(col_key, slice) else [row[col_key]]
            for row in selected_rows
        ]
        if isinstance(row_key, int) and isinstance(col_key, slice):
            return selected[0]
        if isinstance(row_key, slice) and isinstance(col_key, int):
            return [row[0] for row in selected]
        return selected


class CaseInsensitiveDict(UserDict[str, int]):
    def __setitem__(self, key: str, value: int) -> None:
        super().__setitem__(key.lower(), value)

    def __getitem__(self, key: str) -> int:
        return super().__getitem__(key.lower())

    def __contains__(self, key: object) -> bool:
        return isinstance(key, str) and super().__contains__(key.lower())


class SliceView(Sequence[int]):
    def __init__(self, backing: list[int], selection: slice | range) -> None:
        self._backing = backing
        self._indices = (
            range(*selection.indices(len(backing)))
            if isinstance(selection, slice)
            else selection
        )

    def __len__(self) -> int:
        return len(self._indices)

    def __getitem__(self, index: int | slice) -> int | SliceView:
        if isinstance(index, slice):
            return SliceView(self._backing, self._indices[index])
        return self._backing[self._indices[index]]

    def __iter__(self):
        for backing_index in self._indices:
            yield self._backing[backing_index]


def test_deck_size_indexing_slicing_and_membership():
    deck = Deck()
    assert len(deck) == 52
    assert deck[0] == ("2", "spades")
    assert deck[-1] == ("A", "hearts")
    assert len(deck[:3]) == 3
    assert ("A", "hearts") in deck
    assert ("JOKER", "stars") not in deck


def test_sequence_out_of_range_uses_index_error():
    with pytest.raises(IndexError):
        _ = Deck()[52]


def test_sample_batch_slice_preserves_type():
    subset = SampleBatch([3, 6, 9, 12])[1:3]
    assert isinstance(subset, SampleBatch)
    assert list(subset) == [6, 9]


def test_legacy_getitem_iteration_and_membership_fallbacks():
    values = LegacyNumbers([10, 20, 30])
    assert list(values) == [10, 20, 30]
    assert 20 in values
    assert 99 not in values


def test_container_iteration_is_repeatable_and_iterator_is_one_shot():
    countdown = Countdown(3)
    assert list(countdown) == [3, 2, 1]
    assert list(countdown) == [3, 2, 1]
    iterator = iter(countdown)
    assert next(iterator) == 3
    assert list(iterator) == [2, 1]
    assert list(iterator) == []


def test_mutation_methods_preserve_list_semantics():
    values = MutableSamples([10, 20, 30, 40])
    values[1] = 99
    del values[-1]
    values[1:2] = [21, 22]
    assert list(values) == [10, 21, 22, 30]
    with pytest.raises(IndexError):
        values[100] = 1


def test_missing_mapping_key_differs_from_get_and_membership():
    values = ZeroDefaultDict({"known": 3})
    assert values["missing"] == 0
    assert "missing" not in values
    assert values.get("other") is None
    with pytest.raises(KeyError):
        _ = {"known": 3}["missing"]


def test_matrix_tuple_indexing_and_wrong_key_shape():
    matrix = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    assert matrix[1, 2] == 6
    assert matrix[0:2, 1:3] == [[2, 3], [5, 6]]
    assert matrix[1, 0:2] == [4, 5]
    with pytest.raises(TypeError, match=r"matrix\[row, column\]"):
        _ = matrix[1]
    with pytest.raises(ValueError, match="equal length"):
        Matrix([[1, 2], [3]])


def test_case_insensitive_dict_normalizes_update():
    values = CaseInsensitiveDict()
    values.update({"Region": 1})
    assert values["REGION"] == 1
    assert "region" in values
    assert dict(values) == {"region": 1}


def test_slice_view_is_lazy_live_and_slice_preserving():
    backing = [10, 20, 30, 40]
    view = SliceView(backing, slice(1, 4))
    assert list(view) == [20, 30, 40]
    backing[1] = 99
    assert list(view) == [99, 30, 40]
    subview = view[1:]
    assert isinstance(subview, SliceView)
    assert list(subview) == [30, 40]
    backing.append(50)
    assert list(view) == [99, 30, 40]


def test_collection_abc_and_length_hint_contracts():
    deck = Deck()
    assert isinstance(deck, Sized)
    assert isinstance(deck, Iterable)
    assert isinstance(deck, Container)
    assert isinstance(deck, Collection)

    class EstimatedRows:
        def __iter__(self):
            yield from ("r1", "r2", "r3")

        def __length_hint__(self) -> int:
            return 3

    assert length_hint(EstimatedRows(), 0) == 3


def test_reverse_and_index_protocols():
    class ReverseLabels:
        def __init__(self, labels: list[str]) -> None:
            self._labels = tuple(labels)

        def __len__(self) -> int:
            return len(self._labels)

        def __getitem__(self, index: int) -> str:
            return self._labels[index]

        def __reversed__(self):
            return reversed(self._labels)

    class Index:
        def __init__(self, value: int) -> None:
            self._value = value

        def __index__(self) -> int:
            return self._value

    assert list(reversed(ReverseLabels(["a", "b", "c"]))) == ["c", "b", "a"]
    assert ["zero", "one", "two"][Index(2)] == "two"


def test_truthiness_uses_len_unless_bool_is_defined():
    class ResultSet:
        def __init__(self, rows: list[str]) -> None:
            self._rows = rows

        def __len__(self) -> int:
            return len(self._rows)

    class AlwaysTruthyEmpty:
        def __len__(self) -> int:
            return 0

        def __bool__(self) -> bool:
            return True

    assert not ResultSet([])
    assert ResultSet(["row"])
    assert bool(AlwaysTruthyEmpty()) is True


def test_length_and_iterator_protocol_reject_invalid_implementations():
    class BadLength:
        def __len__(self):
            return -1

    class BrokenIterator:
        def __iter__(self):
            return self

    with pytest.raises(ValueError):
        len(BadLength())
    with pytest.raises(TypeError, match="non-iterator"):
        iter(BrokenIterator())


def test_userdict_membership_rejects_non_string_key():
    values = CaseInsensitiveDict({"Region": 1})
    assert 1 not in values

```

### What these tests cover

- sequence length, positive/negative indexing, slices, membership, and `IndexError` boundaries;
- custom type preservation on slicing;
- legacy sequence iteration and membership fallbacks;
- repeatable containers versus one-shot iterators;
- assignment, slice assignment, deletion, and invalid mutation indices;
- `KeyError` versus `__missing__`, `get`, and membership behavior;
- tuple-based indexing, unsupported key shapes, and malformed matrix dimensions;
- normalization on `UserDict.update`;
- live view values, stable selected positions, and view-preserving slicing;
- `Sized`, `Iterable`, `Container`, and `Collection` conformance; reverse iteration, `__index__`, truthiness precedence, length hints, invalid lengths, and invalid iterators.

Run with `python -m pytest -q test_container_protocols.py`. The test block is self-contained, so it does not depend on an unpublished helper module. Extend it for any additional mutation or view semantics your own container promises.

---

## 20. Graduated exercises

### Exercise 1 — Beginner: inspect a key

Implement a class whose `__getitem__` returns the received key. Demonstrate the difference between `obj[2]`, `obj[1:5:2]`, and `obj[1:3, 0]`.

### Exercise 2 — Beginner: read-only sequence

Implement `Tags` over a tuple. Support `len(tags)`, integer indexing, negative indices, slices, and repeatable iteration. A slice must return another `Tags`.

### Exercise 3 — Intermediate: mutable sequence

Add `__setitem__` and `__delitem__` to a sequence wrapper. Test integer assignment, slice assignment, deletion, and invalid indices.

### Exercise 4 — Intermediate: mapping defaults

Implement a `dict` subclass whose `__missing__` returns an empty list. Explain why this does not automatically insert the key, and compare `d[key]`, `d.get(key)`, and `key in d`.

### Exercise 5 — Intermediate: one-shot iterator

Implement an iterator class with `__iter__` and `__next__`. Confirm that the second full traversal is empty. Then build a separate iterable container that creates a fresh iterator each time.

### Exercise 6 — Advanced: a lazy slice view

Implement a `Sequence` view that stores a backing sequence and a slice rather than copying the selected elements. Specify whether the view is live or snapshot-based and test what happens after backing data changes.

### Exercise 7 — Advanced: multidimensional keys

Extend `Matrix` to support `matrix[..., 1]`. Define the exact behavior of `Ellipsis` and reject unsupported combinations rather than silently misinterpreting them.

### Exercise 8 — Production design: validation

Compare a `dict` subclass that overrides only `__setitem__` with a `UserDict` implementation. Test initialization, assignment, `update`, and deletion. Explain which invariant each design can actually guarantee.

---

## 21. Worked solutions

### Solution 1

```python
class Inspect:
    def __getitem__(self, key):
        return key

x = Inspect()
assert x[2] == 2
assert x[1:5:2] == slice(1, 5, 2)
assert x[1:3, 0] == (slice(1, 3), 0)
```

### Solution 2

```python
from collections.abc import Sequence


class Tags(Sequence[str]):
    def __init__(self, values):
        self._values = tuple(values)

    def __len__(self):
        return len(self._values)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return Tags(self._values[index])
        return self._values[index]


tags = Tags(["raw", "clean", "feature"])
assert tags[-1] == "feature"
assert list(tags[1:]) == ["clean", "feature"]
assert isinstance(tags[:2], Tags)
assert list(tags) == list(tags)
```

`Sequence` supplies iteration and membership mixins based on the required primitives. A type checker may benefit from overloads for the two `__getitem__` return shapes.

### Solution 3

```python
class MutableTags:
    def __init__(self, values):
        self._values = list(values)

    def __len__(self):
        return len(self._values)

    def __getitem__(self, index):
        return self._values[index]

    def __setitem__(self, index, value):
        self._values[index] = value

    def __delitem__(self, index):
        del self._values[index]

    def __iter__(self):
        return iter(self._values)


tags = MutableTags(["a", "b", "c"])
tags[1] = "B"
del tags[0]
assert list(tags) == ["B", "c"]
```

This deliberately delegates to a list, so slice assignment must use an iterable of replacement values, following list semantics.

### Solution 4

```python
class MissingLists(dict[str, list[object]]):
    def __missing__(self, key: str) -> list[object]:
        return []


d = MissingLists()
assert d["new"] == []
assert "new" not in d
assert d.get("other") is None
```

The missing result is returned but not stored. If storing is desired, use `setdefault`, implement insertion intentionally, or choose `defaultdict`.

### Solution 5

The `CountdownIterator` in Section 10 is the one-shot iterator solution. The `Countdown` generator in that section is the reusable container solution: each call to `iter(countdown)` creates a new generator.

### Solution 6

This view captures the selected *positions* when it is created but reads the current values from the backing list. Updating an existing selected element is visible through the view; appending new elements does not expand the view. Slicing a view creates another view over the composed range of positions.

```python
from __future__ import annotations

from collections.abc import Sequence


class SliceView(Sequence[int]):
    def __init__(self, backing: list[int], selection: slice | range) -> None:
        self._backing = backing
        self._indices = (
            range(*selection.indices(len(backing)))
            if isinstance(selection, slice)
            else selection
        )

    def __len__(self) -> int:
        return len(self._indices)

    def __getitem__(self, index: int | slice) -> int | "SliceView":
        if isinstance(index, slice):
            return SliceView(self._backing, self._indices[index])
        return self._backing[self._indices[index]]

    def __iter__(self):
        for backing_index in self._indices:
            yield self._backing[backing_index]


backing = [10, 20, 30, 40]
view = SliceView(backing, slice(1, 4))
assert list(view) == [20, 30, 40]
backing[1] = 99
assert list(view) == [99, 30, 40]
subview = view[1:]
assert isinstance(subview, SliceView)
assert list(subview) == [30, 40]
backing.append(50)
assert list(view) == [99, 30, 40]
```

This avoids copying all selected values for a single indexed access. The view is still not immune to structural changes to the backing list: deleting or shortening the backing list can make a captured index invalid. A production API should specify whether structural mutation is prohibited, reflected, or detected.

### Solution 7

A correct solution should define `Ellipsis` placement, expand it to the appropriate number of full slices, and then reuse the matrix's indexing logic. It must reject multiple ellipses or excess dimensions if the API does not support them. There is no single required behavior for a custom class: consistency and explicit documented semantics are the requirements.

### Solution 8

`dict` subclasses can have inherited bulk operations that bypass an overridden `__setitem__`. `UserDict` routes ordinary mapping operations through its wrapped data and is generally easier to customize. In either design, tests should cover every public mutation path. For strict invariants, composition plus a deliberately small public API is often easiest to reason about.

---

## 22. Roadmap self-check answers

### 1. How does Python iterate an object that only defines `__getitem__`?

If `__iter__` is absent, Python can use the legacy sequence protocol: it requests indices `0`, `1`, `2`, and so on, and treats `IndexError` as the end of iteration. This is compatibility behavior; new container designs should usually implement `__iter__` explicitly.

### 2. What does `obj[1:3, 0]` pass to `__getitem__`?

It passes a tuple containing two entries: `slice(1, 3, None)` and integer `0`, i.e. `(slice(1, 3, None), 0)`. Python constructs the key; the object decides how to interpret it.

### 3. Why prefer `UserDict` over subclassing `dict` for validation logic?

Built-in `dict` operations such as `update` can bypass an overridden Python-level `__setitem__`, so overriding that one method is not a universal validation hook. `UserDict` wraps a dictionary and is easier to customize consistently. For strong invariants, test all mutation paths or use composition with a controlled API.

---

## 23. Final engineering checklist

Before shipping a custom container, verify:

- [ ] `__len__` returns a non-negative integer and has a clear cost.
- [ ] `__getitem__` documents accepted key types and return types.
- [ ] Sequence boundaries raise `IndexError`; missing mapping keys raise `KeyError`.
- [ ] Negative indices and slice behavior are tested.
- [ ] Slices return the documented type and have explicit copy/view semantics.
- [ ] `__iter__` returns an iterator and is repeatable when the object is a reusable container.
- [ ] `__contains__` is correct and has understood performance/side effects.
- [ ] Legacy fallback behavior is understood but not relied on unnecessarily.
- [ ] Mutation methods preserve invariants across direct and bulk operations.
- [ ] `__missing__` behavior is distinguished from `get`, membership, and insertion.
- [ ] `__reversed__`, `__index__`, truthiness, and length hints are implemented only where useful.
- [ ] Tuple keys, slices, and `Ellipsis` are either supported deliberately or rejected clearly.
- [ ] Views and materialized lists are distinguished accurately.
- [ ] ABCs describe the intended interface and mixin behavior is tested.
- [ ] Built-in subclassing limitations are understood; `UserDict`, `UserList`, or composition is considered.
- [ ] Tests include empty containers, boundaries, repeated iteration, and unsupported key shapes.

**Lesson complete when:** you can explain each protocol and fallback, implement a coherent sequence or mapping, and test the behavior callers rely on without confusing indexing, iteration, membership, and missing-key semantics.
