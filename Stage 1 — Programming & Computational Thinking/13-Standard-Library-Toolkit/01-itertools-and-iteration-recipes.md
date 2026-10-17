# `itertools` and Iteration Recipes

> **Target:** Python 3.12+\
> **Stage:** 1 --- Programming & Computational Thinking\
> **Module:** 13 --- Standard Library Toolkit\
> **Lesson:** 01\
> **Focus:** Lazy iteration, streaming transformations, safe batching,
> and standard-library recipes.

## 1. Learning objectives and prerequisites

By the end of this lesson, you should be able to:

-   Explain the relationship between an iterable, iterator, generator,
    and `itertools`.
-   Select appropriate finite and infinite iterator tools and predict
    their outputs.
-   Use combinatoric tools for small parameter grids without
    accidentally creating enormous outputs.
-   Apply `groupby`, `tee`, `pairwise`, `batched`, `islice`, and strict
    `zip` safely.
-   Implement and test reusable recipes that are not built into
    `itertools`.
-   Build a bounded-memory ETL pipeline and measure Python allocations
    with `tracemalloc`.
-   Recognize exhaustion, buffering, ordering, closure, and
    materialization bugs.
-   Choose readable loops when they communicate intent better than a
    clever iterator chain.

### Prerequisites

You should know basic Python functions, loops, conditionals, lists,
tuples, dictionaries, exceptions, type hints, file iteration, and simple
tests. Module 1.9 covers iterables, iterators, generators, and generator
expressions; this lesson uses those ideas rather than re-teaching
generator internals in full. Earlier lessons also cover file handling,
validation, and testing.

## 2. Conceptual foundations

### 2.1 Iterable, iterator, and generator

An **iterable** can provide an iterator. Lists, tuples, strings,
dictionaries, files, and generator objects are common examples. An
**iterator** produces one value at a time through `next()` and raises
`StopIteration` when exhausted. A **generator** is a convenient way to
create an iterator, usually with `yield` or a generator expression.

``` python
values = [10, 20, 30]        # reusable iterable
it = iter(values)            # iterator
print(next(it))
print(next(it))
print(next(it))
try:
    next(it)
except StopIteration:
    print("exhausted")
```

Expected output:

``` text
10
20
30
exhausted
```

Calling `iter(values)` again creates a fresh list iterator. Calling
`iter(it)` returns the same iterator, already part-way through. Most
iterators are single-pass: after exhaustion, another `next()` continues
to raise `StopIteration`.

### 2.2 Laziness and pull-based evaluation

A lazy iterator computes or fetches an item only when its consumer
requests one. `itertools` supplies composable iterator building blocks.
A pipeline such as:

``` python
from itertools import islice

numbers = (n * n for n in range(1_000_000))
first_five = list(islice(numbers, 5))
print(first_five)
```

prints `[0, 1, 4, 9, 16]`. It does not build a million-element list. The
generator is consumed only as far as needed.

Laziness does **not** mean zero memory or zero work. An operation may
retain a small buffer (`pairwise`), retain many values (`tee` when
branches diverge), materialize its input (`product` pools its input
iterables), or produce an enormous number of results. A downstream
consumer can also force full materialization with `list(...)`.

### 2.3 A useful pipeline model

Think of a pipeline as a sequence of pull-based stages:

``` text
source -> parse -> filter -> transform -> batch -> sink
```

Each stage should usually yield one result at a time. The sink drives
the pipeline by requesting the next item. If a stage raises, the
consumer sees the exception unless the stage deliberately handles it.
Lazy stages can reduce peak memory, but they do not replace validation,
error policy, retries, observability, or transaction design.

### 2.4 When is `list(iterator)` safe?

`list(...)` is appropriate when the input is known to be finite and
comfortably fits memory, such as a tiny test fixture or a small, bounded
configuration grid. It is dangerous for an unbounded iterator such as
`count()` or for a large stream whose size is unknown. It also consumes
a one-shot iterator.

Prefer `next(it, default)` for one item, `islice(it, n)` for a bounded
prefix, and a `for` loop for streaming. If an operation needs all input
values internally, document that fact and bound the input.

## 3. Beginner lessons

The signatures below describe common usage; consult
`help(itertools.name)` or the Python documentation for full details.

### 3.1 Infinite iterators: `count`, `cycle`, `repeat`

#### `count(start=0, step=1)`

Produces `start`, then repeatedly adds `step`, without stopping.

``` python
from itertools import count, islice

print(list(islice(count(10, 5), 4)))
print(list(islice(count(3), 5)))
```

Output:

``` text
[10, 15, 20, 25]
[3, 4, 5, 6, 7]
```

Use it for sequence numbers, synthetic indexes, or controlled test data.
Always put a bound downstream if the consumer must terminate.
Floating-point steps can accumulate rounding error; use integers or
`decimal.Decimal` when exact decimal increments matter.

#### `cycle(iterable)`

Repeats values from an iterable forever. It saves the input values so it
can replay them, so it is not appropriate for an unbounded source.

``` python
from itertools import cycle, islice
print(list(islice(cycle(["primary", "secondary"]), 5)))
# ['primary', 'secondary', 'primary', 'secondary', 'primary']
```

An empty input produces no values. A large input may be retained in
memory for the duration of the cycle.

#### `repeat(object, times=None)`

Produces the same object repeatedly. If `times` is omitted or `None`, it
is infinite.

``` python
from itertools import repeat
print(list(repeat("retry", 3)))
print(list(repeat(None, 2)))
```

Output:

``` text
['retry', 'retry', 'retry']
[None, None]
```

It repeats the **same object reference**, not a fresh copy. Repeating a
mutable object can therefore expose shared mutation. Use a factory
function or comprehension if you need independent objects.

### 3.2 Combining and slicing streams

#### `chain(*iterables)` and `chain.from_iterable(iterable_of_iterables)`

`chain` emits all values from each input in order, without nesting them.

``` python
from itertools import chain
print(list(chain([1, 2], (3,), "ab")))
print(list(chain.from_iterable([[1, 2], [], [3, 4]])))
```

Output:

``` text
[1, 2, 3, 'a', 'b']
[1, 2, 3, 4]
```

`chain.from_iterable` is useful when the input is itself a stream of
batches or partitions. It does not recursively flatten arbitrary
nesting; it removes one iterable level only. An infinite first input
prevents later inputs from ever being reached.

#### `islice(iterable, stop)` / `islice(iterable, start, stop[, step])`

Produces a slice-like selection without building the whole source as a
list. `stop` is required in the one-argument form; negative values are
not supported. `islice` consumes the source up to the last selected
position, including skipped items.

``` python
from itertools import count, islice
print(list(islice(count(10), 4)))
print(list(islice(range(20), 3, 10, 2)))
```

Output:

``` text
[10, 11, 12, 13]
[3, 5, 7, 9]
```

For pagination over a one-shot iterator, offsets consume all skipped
values. Repeatedly requesting page 100 from the beginning can be
expensive. This small helper illustrates bounded page output; call it with
a fresh/replayable source when you need independent pages:

``` python
def page(iterable, page_number: int, page_size: int):
    if page_number < 0:
        raise ValueError("page_number must be non-negative")
    if page_size <= 0:
        raise ValueError("page_size must be positive")
    start = page_number * page_size
    return list(islice(iterable, start, start + page_size))

assert page(iter(range(10)), 1, 3) == [3, 4, 5]
```

The result retains at most `page_size` values, but reaching page `p`
requires consuming up to `p * page_size` source values. Do not call this
repeatedly on the same already-advanced iterator expecting it to restart.
For databases or APIs, prefer native cursor/offset/keyset pagination when
available.

#### `zip_longest(*iterables, fillvalue=None)`

Pairs values until the **longest** input is exhausted, filling missing
positions.

``` python
from itertools import zip_longest
print(list(zip_longest([1, 2, 3], ["a"], fillvalue="-")))
```

Output:

``` text
[(1, 'a'), (2, '-',), (3, '-')]
```

It is useful for aligning uneven streams. If one input is infinite, the
result is infinite even after all finite inputs end. Use a finite input
or bound the result.

#### `zip` and `zip(strict=True)`

Ordinary `zip` stops at the shortest input, potentially hiding data
loss:

``` python
print(list(zip([1, 2, 3], ["a", "b"])))
# [(1, 'a'), (2, 'b')]
```

In Python 3.10+, `zip(..., strict=True)` raises `ValueError` if input
lengths differ. The mismatch may be discovered only when iteration
reaches the shorter input's end, so some pairs may already have been
consumed. Use strict mode when equal lengths are an invariant, not when
truncation is intended.

### 3.3 Accumulation and selection

#### `accumulate(iterable, func=operator.add, *, initial=None)`

Yields running accumulated results. By default it computes cumulative
sums. With `initial`, the initial value is emitted first.

``` python
from itertools import accumulate
from operator import mul
print(list(accumulate([1, 2, 3, 4])))
print(list(accumulate([1, 2, 3, 4], mul)))
print(list(accumulate([1, 2, 3], initial=100)))
```

Output:

``` text
[1, 3, 6, 10]
[1, 2, 6, 24]
[100, 101, 103, 106]
```

Use for running totals, cumulative counts, or prefix products. The
function must accept two arguments. Some accumulation functions (for
example, `max`) are not invertible; this is a running fold, not a
general rolling-window aggregation.

#### `compress(data, selectors)`

Emits data values whose corresponding selector is truthy. It stops when
either input ends.

``` python
from itertools import compress
print(list(compress(["keep", "drop", "keep"], [1, 0, True])))
# ['keep', 'keep']
```

This is useful when a Boolean mask is already available. If selector and
data lengths must match, validate them or use an explicit strict-length
strategy; `compress` silently truncates.

#### `takewhile(predicate, iterable)` and `dropwhile(predicate, iterable)`

`takewhile` yields the initial run for which the predicate is true, then
stops permanently at the first false value. That failing value is
consumed and is **not** returned. `dropwhile` skips the initial run of
true values, then yields everything else, including later values that
satisfy the predicate again.

``` python
from itertools import takewhile, dropwhile
print(list(takewhile(lambda n: n < 5, [1, 3, 4, 2, 7, 1])))
print(list(dropwhile(lambda n: n < 5, [1, 3, 4, 2, 7, 1])))
```

Output:

``` text
[1, 3, 4, 2]
[7, 1]
```

These are boundary operations, not general filters. Use `filter` or a
comprehension when every item should be tested independently.

#### `filterfalse(predicate, iterable)`

Yields values for which the predicate is false. If `predicate=None`, it
yields falsey values.

``` python
from itertools import filterfalse
print(list(filterfalse(lambda n: n % 2, range(6))))
print(list(filterfalse(None, [0, 1, "", "ok", None])))
```

Output:

``` text
[0, 2, 4]
[0, '', None]
```

It is useful when expressing the rejected side of a filter. Do not
confuse a falsey value with invalid data unless that is your explicit
rule.

#### `starmap(function, iterable)`

Calls the function with each input tuple unpacked as positional
arguments.

``` python
from itertools import starmap
print(list(starmap(pow, [(2, 3), (3, 2), (4, 2)])))
# [8, 9, 16]
```

Use when records already contain argument tuples. A comprehension is
often clearer for simple transformations:
`[pow(a, b) for a, b in pairs]`.

## 4. Intermediate lessons

### 4.1 Combinatoric iterators

Combinatoric functions first consume their input iterables into finite
pools. Their outputs are lazy, but their input pools are materialized,
so do not feed them an infinite source.

-   `product(*iterables, repeat=1)`: Cartesian product; `product(A, B)`
    yields every pair. Output count is the product of input lengths.
-   `permutations(iterable, r=None)`: ordered selections without
    replacement; output count is `n! / (n-r)!`.
-   `combinations(iterable, r)`: unordered selections without
    replacement; output count is `n! / (r!(n-r)!)`.
-   `combinations_with_replacement(iterable, r)`: unordered selections
    where an input position may be selected repeatedly.

``` python
from itertools import product, permutations, combinations, combinations_with_replacement

print(list(product(["dev", "prod"], [1, 2])))
print(list(permutations("ABC", 2)))
print(list(combinations("ABC", 2)))
print(list(combinations_with_replacement("AB", 2)))
```

Output:

``` text
[('dev', 1), ('dev', 2), ('prod', 1), ('prod', 2)]
[('A', 'B'), ('A', 'C'), ('B', 'A'), ('B', 'C'), ('C', 'A'), ('C', 'B')]
[('A', 'B'), ('A', 'C'), ('B', 'C')]
[('A', 'A'), ('A', 'B'), ('B', 'B')]
```

**Production caution:** a 10-by-10-by-10 parameter grid already has
1,000 combinations; permutations grow factorially. Estimate result count
before collecting output. Use `islice` to inspect a prefix, or stream
candidates directly into evaluation.

### 4.2 `groupby`: consecutive groups, not SQL-style grouping

`groupby(iterable, key=None)` starts a new group whenever the key
changes. It does not collect every equal key from the entire stream.
Sort by the same key first when global grouping is required and sorting
is feasible.

``` python
from itertools import groupby
from operator import itemgetter

rows = [
    {"k": "a", "v": 1},
    {"k": "b", "v": 2},
    {"k": "a", "v": 3},
]
for key, group in groupby(rows, key=itemgetter("k")):
    print(key, [row["v"] for row in group])
```

Output (three consecutive groups):

``` text
a [1]
b [2]
a [3]
```

Sorted input gives the intended global groups:

``` python
for key, group in groupby(sorted(rows, key=itemgetter("k")), key=itemgetter("k")):
    print(key, [row["v"] for row in group])
```

Output:

``` text
a [1, 3]
b [2]
```

**Group lifetime:** each group is an iterator sharing the underlying
source with the outer `groupby`. Advancing the outer iterator can make
an earlier group unusable. Consume each group before advancing, or
explicitly materialize a group only if its size is bounded and needed.
Sorting generally costs `O(n log n)` time and `O(n)` memory; streaming
grouping is most attractive when input is already ordered by key.

### 4.3 `tee`: multiple consumers, hidden buffer

`tee(iterable, n=2)` creates independent-looking iterators from one
source. If one branch advances far ahead of another, values must be
buffered for the lagging branch. Buffer size can approach the distance
between consumers; it is not a free broadcast mechanism.

``` python
from itertools import tee
left, right = tee(range(5))
print(next(left), next(left))
print(list(right))  # right still sees 0 through 4
print(list(left))   # left has already consumed 0 and 1
```

Output:

``` text
0 1
[0, 1, 2, 3, 4]
[2, 3, 4]
```

Use only when branches are expected to stay reasonably close or the
source is small. For independent parallel consumers, consider an
explicit queue with backpressure, a durable stream, or rereading a
replayable source. Do not use `tee` to make an infinite stream safely
reusable without a bounded-consumption design.

### 4.4 `pairwise` (Python 3.10+) and `batched` (Python 3.12+)

`pairwise(iterable)` emits overlapping pairs: `(x0, x1)`, `(x1, x2)`,
and so on. It uses constant-size state.

`batched(iterable, n, *, strict=False)` emits tuples of up to `n`
elements. In Python 3.12, `batched` was added. The `strict` parameter
was added in Python 3.13; on Python 3.12, do not pass it.

``` python
from itertools import pairwise, batched
print(list(pairwise([1, 4, 9])))
print(list(batched(range(7), 3)))
```

Output:

``` text
[(1, 4), (4, 9)]
[(0, 1, 2), (3, 4, 5), (6,)]
```

`batched` requires a positive batch size. It consumes at most `n` items
to produce each batch, with a shorter final tuple by default. In 3.13+,
`strict=True` raises `ValueError` if the last batch is incomplete. If
supporting both 3.12 and later versions, use a version-compatible
implementation or handle the final partial batch yourself.

### 4.5 Chunking files, records, and API pages

A batch bounds the number of records held by the batching stage, but not
necessarily the whole process: a writer may buffer, a parser may retain
data, or a source client may prefetch pages.

``` python
from itertools import batched

def write_batches(records, write_batch, batch_size: int = 500) -> int:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    written = 0
    for batch in batched(records, batch_size):
        write_batch(batch)
        written += len(batch)
    return written

saved = []
count = write_batches(({"id": n} for n in range(7)), saved.append, 3)
print(count, [len(batch) for batch in saved])
```

Output:

``` text
7 [3, 3, 1]
```

Use keyset/cursor pagination for large database or API results where
possible. An `islice` offset over a generator is linear in the number of
skipped items, not random access. Be explicit about whether a final
partial batch is valid.

## 5. Advanced standard-library recipes

These recipes are small, testable helpers inspired by the Python
`itertools` documentation. They are not all built-in `itertools`
functions. Each recipe states its memory characteristics and edge cases.

``` python
from collections import deque
from itertools import chain, islice, repeat
from typing import Iterable, Iterator, TypeVar, Callable

T = TypeVar("T")
```

### 5.1 `take(n, iterable)`

Returns at most the first `n` items as a list. This recipe deliberately
materializes only a bounded prefix.

``` python
def take(n: int, iterable: Iterable[T]) -> list[T]:
    if n < 0:
        raise ValueError("n must be non-negative")
    return list(islice(iterable, n))

assert take(3, range(10)) == [0, 1, 2]
assert take(3, iter([1])) == [1]
assert take(0, range(10)) == []
```

Time `O(min(n, source length))`, result space `O(n)`. It consumes a
one-shot source.

### 5.2 `nth(iterable, n, default=None)`

Returns the item at zero-based index `n`, or `default` if it does not
exist.

``` python
def nth(iterable: Iterable[T], n: int, default=None):
    if n < 0:
        raise ValueError("n must be non-negative")
    return next(islice(iterable, n, None), default)

assert nth("abcdef", 2) == "c"
assert nth([1], 5, "missing") == "missing"
assert nth([], 0) is None
```

Time is `O(n)` because an iterator must be advanced through skipped
values; auxiliary space is `O(1)`.

### 5.3 `flatten(iterable_of_iterables)`

Flattens exactly one level. Strings are iterable too, so avoid passing
strings when you intend to flatten collections of records.

``` python
def flatten(iterables: Iterable[Iterable[T]]) -> Iterator[T]:
    return chain.from_iterable(iterables)

assert list(flatten([[1, 2], [], [3]])) == [1, 2, 3]
```

It streams one level and does not recursively flatten nested lists.

### 5.4 `unique_everseen(iterable, key=None)`

Yields the first occurrence of each key in encounter order. The set of
seen keys grows with the number of distinct keys, so memory is `O(u)`
where `u` is the number of unique keys.

``` python
def unique_everseen(iterable: Iterable[T], key: Callable[[T], object] | None = None) -> Iterator[T]:
    seen: set[object] = set()
    for item in iterable:
        marker = item if key is None else key(item)
        if marker not in seen:
            seen.add(marker)
            yield item

assert list(unique_everseen([1, 2, 1, 3, 2])) == [1, 2, 3]
assert list(unique_everseen(["A", "a", "B"], key=str.lower)) == ["A", "B"]
```

Without `key`, items must be hashable. With `key`, the returned markers
must be hashable. For unbounded streams with unbounded unique values,
this recipe cannot have constant memory.

### 5.5 `sliding_window(iterable, n)`

Produces overlapping tuples of length `n`. It uses a deque of at most
`n` items and is suitable for rolling calculations.

``` python
def sliding_window(iterable: Iterable[T], n: int) -> Iterator[tuple[T, ...]]:
    if n <= 0:
        raise ValueError("n must be positive")
    it = iter(iterable)
    window = deque(islice(it, n), maxlen=n)
    if len(window) < n:
        return
    yield tuple(window)
    for item in it:
        window.append(item)
        yield tuple(window)

assert list(sliding_window([1, 2, 3, 4], 3)) == [(1, 2, 3), (2, 3, 4)]
assert list(sliding_window([1, 2], 3)) == []
assert list(sliding_window([], 1)) == []
```

For each output, creating a tuple costs `O(n)`; the internal deque is
`O(n)`. The function returns no windows if the input is shorter than
`n`. This implementation uses a generator function, so validation occurs
when iteration begins, not necessarily at the call site.

### 5.6 `roundrobin(*iterables)`

Takes one item from each active iterator in turn, removing iterators as
they exhaust. A simple implementation is:

``` python
def roundrobin(*iterables: Iterable[T]) -> Iterator[T]:
    active = deque(iter(item) for item in iterables)
    while active:
        current = active.popleft()
        try:
            item = next(current)
        except StopIteration:
            continue
        yield item
        active.append(current)

assert list(roundrobin("ABC", [1, 2], ["x"])) == ["A", 1, "x", "B", 2, "C"]
assert list(roundrobin([], [1])) == [1]
```

This is fair only at the item level; a slow or blocking iterator can
still stall the whole loop. It retains one iterator per input.

### 5.7 `partition(predicate, iterable)`

Returns two iterators: first the items where the predicate is false,
then the items where it is true. A `tee` implementation is concise but
can buffer heavily if one side is consumed far ahead.

``` python
from itertools import filterfalse, tee

def partition(predicate: Callable[[T], bool], iterable: Iterable[T]) -> tuple[Iterator[T], Iterator[T]]:
    left, right = tee(iterable)
    return filterfalse(predicate, left), (item for item in right if predicate(item))

even_or_odd_false, even_or_odd_true = partition(lambda n: n % 2 == 0, range(6))
assert list(even_or_odd_false) == [1, 3, 5]
assert list(even_or_odd_true) == [0, 2, 4]
```

This recipe is convenient for small or similarly consumed branches. The
predicate is evaluated independently in each branch, so it may run twice
per source item; use a pure, deterministic predicate rather than one with
side effects. For large or divergent branches, prefer a single pass that
explicitly routes values into bounded sinks or stores.

### 5.8 `powerset(iterable)`

Yields all subsets in increasing subset size. The number of results is
`2**n`, so this is only suitable for small finite inputs.

``` python
from itertools import combinations

def powerset(iterable: Iterable[T]) -> Iterator[tuple[T, ...]]:
    pool = tuple(iterable)  # finite input required; materializes it
    return chain.from_iterable(combinations(pool, r) for r in range(len(pool) + 1))

assert list(powerset([1, 2])) == [(), (1,), (2,), (1, 2)]
```

The input pool uses `O(n)` memory, and each yielded subset contains up
to `n` references. Do not materialize the powerset for moderate or large
`n`.

### 5.9 Recipe tests

Keep these checks in a test module and run them with `pytest`. They
exercise boundaries as well as normal behavior.

``` python
import pytest

def test_take_and_nth():
    assert take(2, iter([4, 5, 6])) == [4, 5]
    assert nth([4, 5], 9, "x") == "x"
    with pytest.raises(ValueError):
        take(-1, [])
    with pytest.raises(ValueError):
        nth([], -1)

def test_unique_everseen():
    assert list(unique_everseen([1, 1, 2, 1])) == [1, 2]
    with pytest.raises(TypeError):
        list(unique_everseen([[1], [1]]))

def test_sliding_window():
    assert list(sliding_window([1, 2, 3], 2)) == [(1, 2), (2, 3)]
    assert list(sliding_window([1], 2)) == []
    with pytest.raises(ValueError):
        list(sliding_window([], 0))

def test_roundrobin_and_powerset():
    assert list(roundrobin([1, 2], ["a"])) == [1, "a", 2]
    assert len(list(powerset(range(4)))) == 16
```

Place recipe definitions in a module (for example
`iteration_recipes.py`) and tests in `test_iteration_recipes.py`; the
combined snippets above are for teaching and can be separated as shown.

## 6. Production-oriented streaming ETL

This example reads line-delimited JSON records, parses each record,
validates a small schema, filters unwanted events, batches accepted
records, and writes batches through an injected sink. It does not load
the whole input file or all output records into memory. It is
intentionally small enough to run locally; production systems should add
structured logging, metrics, retries, idempotency, and a sink
transaction policy appropriate to the destination.

``` python
from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Iterator
from itertools import batched
from pathlib import Path
from typing import Any

Record = dict[str, Any]

def parse_json_lines(lines: Iterable[str]) -> Iterator[Record]:
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON on line {line_number}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"line {line_number}: expected a JSON object")
        yield value

def valid_event(record: Record) -> bool:
    return (
        isinstance(record.get("event_id"), str)
        and bool(record["event_id"])
        and isinstance(record.get("event_type"), str)
        and isinstance(record.get("amount"), (int, float))
        and not isinstance(record.get("amount"), bool)
        and record["amount"] >= 0
    )

def transform(records: Iterable[Record]) -> Iterator[Record]:
    for record in records:
        if not valid_event(record):
            continue
        if record["event_type"] == "debug":
            continue
        yield {
            "event_id": record["event_id"],
            "event_type": record["event_type"],
            "amount": float(record["amount"]),
        }

def run_etl(
    input_path: Path,
    write_batch: Callable[[tuple[Record, ...]], None],
    batch_size: int = 500,
) -> int:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")

    written = 0
    # Keep the file context open for the complete lazy pipeline. This also
    # closes the file if parsing or the sink raises an exception.
    with input_path.open("r", encoding="utf-8") as source:
        parsed = parse_json_lines(source)
        accepted = transform(parsed)
        for batch in batched(accepted, batch_size):
            write_batch(batch)
            written += len(batch)
    return written
```

A minimal runnable demonstration:

``` python
from pathlib import Path
from tempfile import TemporaryDirectory
import json

with TemporaryDirectory() as tmp:
    source = Path(tmp) / "events.jsonl"
    source.write_text(
        "\n".join([
            json.dumps({"event_id": "e1", "event_type": "purchase", "amount": 12}),
            json.dumps({"event_id": "e2", "event_type": "debug", "amount": 1}),
            json.dumps({"event_id": "e3", "event_type": "refund", "amount": 4.5}),
            json.dumps({"event_id": "", "event_type": "purchase", "amount": 9}),
        ]) + "\n",
        encoding="utf-8",
    )
    sink: list[tuple[Record, ...]] = []
    count = run_etl(source, sink.append, batch_size=2)
    print(count, sink)
```

Expected output:

``` text
2 [({'event_id': 'e1', 'event_type': 'purchase', 'amount': 12.0}, {'event_id': 'e3', 'event_type': 'refund', 'amount': 4.5})]
```

The demo sink stores all output only so the result can be inspected; a
production sink would write each batch to a database, object store, or
message producer and would not retain all batches in a list. `run_etl`
keeps the input file inside a `with` block while the lazy pipeline is
consumed, so the file is closed on normal completion and when parsing or
the sink raises. The sink must still define its own transaction and
partial-failure behavior.

### 6.1 Failure policy is part of ETL design

The example fails fast on malformed JSON and skips schema-invalid
records. That policy is illustrative, not universal. Alternatives
include quarantining bad rows with line number and reason, counting
rejected records, or failing the batch. Do not silently drop malformed
records in a regulated or financially sensitive pipeline.

### 6.2 Measure memory with `tracemalloc`

`tracemalloc` tracks Python memory allocations, not total process RSS
and not every native allocation. Compare designs on the same input and
environment; avoid claiming a universal ratio.

``` python
import tracemalloc
from itertools import batched

def stream_sum(n: int) -> int:
    return sum(i for i in range(n))

def materialized_sum(n: int) -> int:
    return sum(list(range(n)))

for label, operation in [
    ("stream", stream_sum),
    ("materialized", materialized_sum),
]:
    tracemalloc.start()
    operation(200_000)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(label, "peak bytes:", peak)
```

The exact byte counts depend on Python version and environment. The
expected qualitative result is that `materialized_sum` has a much higher
peak because it builds a list of all integers, while `stream_sum`
consumes values incrementally. Use `tracemalloc` to measure, not to
infer all process memory.

## 7. Complexity, memory, and performance

  -----------------------------------------------------------------------
  Operation               Typical time behavior   Auxiliary memory /
                                                  caveat
  ----------------------- ----------------------- -----------------------
  `count`, `repeat`       O(1) per yielded item   O(1) internal state

  `cycle`                 O(1) per output after   Retains the finite
                          source traversal        source pool

  `chain`                 O(1) overhead per       Small iterator state
                          yielded item            

  `islice`                O(k) to advance through O(1), but skipped
                          k source positions      values are consumed

  `accumulate`            O(1) per item if the    O(1) state
                          combining function is   
                          O(1)                    

  `pairwise`              O(1) per item           O(1) retained values

  `batched(n)`            O(n) to fill each batch O(n) per current batch

  `groupby`               O(n) over already       Small state if groups
                          ordered input           consumed in sequence

  sort then `groupby`     O(n log n)              Usually O(n)
                                                  materialization

  `tee`                   O(1) per source item    Buffer grows with
                          plus buffering          branch lag

  `unique_everseen`       Expected O(n) total     O(number of distinct
                          with hashable keys      keys)

  `sliding_window(n)`     O(n) to create each     O(n) window state
                          tuple                   

  combinatorics           Proportional to number  Input pools
                          and size of results     materialized; output
                                                  count may explode

  `powerset`              2ⁿ subsets              Exponential output;
                                                  finite pool retained
  -----------------------------------------------------------------------

These are useful models, not guarantees for every custom iterator,
predicate, key function, or Python implementation. `itertools`
primitives are implemented in C in CPython and often have low overhead,
but a Python loop can be faster or clearer for a specific task.
Benchmark representative workloads with `timeit` or a profiler before
optimizing. Include parsing, I/O, allocations, and sink costs in
realistic benchmarks. This small benchmark compares the same result computed with
`chain` and an explicit loop; timing is environment-dependent and should
not be treated as a universal ranking:

``` python
from itertools import chain
from timeit import timeit

left = range(1_000)
right = range(1_000, 2_000)

def using_chain() -> int:
    return sum(chain(left, right))

def using_loop() -> int:
    total = 0
    for group in (left, right):
        for value in group:
            total += value
    return total

assert using_chain() == using_loop()
for label, operation in [("chain", using_chain), ("loop", using_loop)]:
    print(label, round(timeit(operation, number=1_000), 4), "seconds")
```

The assertion is the correctness check; the timings are intentionally not
specified because hardware, Python builds, and system load differ.

### 7.1 Bounded memory is a whole-pipeline property

A pipeline is not bounded-memory just because it uses generators. Check
each stage:

-   Does the source prefetch the entire result set?
-   Does a parser retain prior records?
-   Does a combinatoric operation materialize input pools?
-   Does `groupby` require a global sort?
-   Does `tee` buffer a lagging branch?
-   Does deduplication retain every key?
-   Does the sink queue grow without backpressure?
-   Does a test or debug statement call `list(...)`?

A common streaming pipeline uses memory proportional to the batch size
plus fixed parser/sink buffers. But stateful requirements such as exact
global deduplication inherently need state proportional to the number of
seen keys unless that state is externalized (for example, to a
database).

### 7.2 Standard library or `more-itertools`?

The standard library is usually sufficient for straightforward chaining,
batching, pairwise iteration, combinatorics, and simple custom recipes.
Consider `more-itertools` when a project repeatedly needs well-tested
helpers such as chunking variants, windowing, lookahead, collapsing, or
iterable inspection not directly provided by the standard library. Weigh
dependency maintenance, version policy, readability, and whether the
helper is genuinely reused. Do not add a dependency for a three-line
helper unless its correctness or breadth justifies it.

## 8. Common mistakes and debugging

### 8.1 Grouping unsorted input

**Symptom:** the same key appears in multiple groups. `groupby` groups
consecutive equal keys only. Sort by the grouping key first if global
grouping is needed and sorting is feasible, or use a
dictionary/aggregation store when the dataset fits or external state is
appropriate.

### 8.2 Reusing an exhausted iterator

``` python
it = iter([1, 2, 3])
print(sum(it))
print(list(it))  # []
```

If two passes are needed, use a reusable source (like a list or a
function that opens the file again), or deliberately buffer a bounded
dataset. Do not assume `iter(iterator)` resets it.

### 8.3 Uneven `tee` consumers

If branch A reads a million items while branch B has not moved, `tee`
must retain values for B. Avoid divergent consumption on large streams.
Use one-pass routing or a durable source instead.

### 8.4 Accidental unbounded materialization

Never do `list(count())`, `list(cycle(...))`, or `list()` on a source
whose size is unbounded or unknown. Use a finite bound such as `islice`,
or consume incrementally.

### 8.5 Late binding in closures and generator expressions

Closures capture variables, not snapshots of their values. This can
surprise code that builds callbacks in a loop:

``` python
functions = [lambda: i for i in range(3)]
print([f() for f in functions])  # [2, 2, 2]
```

Bind the current value using a default argument:

``` python
functions = [lambda i=i: i for i in range(3)]
print([f() for f in functions])  # [0, 1, 2]
```

A generator expression also runs lazily, so changes to referenced
variables before consumption can affect results. Prefer simple local
variables and clear generator lifetimes; see the dedicated closures
lesson for the full language model.

### 8.6 Edge cases to make explicit

-   **Empty inputs:** `chain()` yields nothing; `pairwise([])` yields
    nothing; `sliding_window([], n)` yields nothing for valid `n`.
-   **Invalid batch/window sizes:** reject `n <= 0` before processing.
-   **Infinite sources:** `count`, unbounded `repeat`, and `cycle` do
    not terminate; always bound the consumer if termination is required.
-   **Uneven lengths:** `zip` truncates; `zip(strict=True)` raises;
    `zip_longest` pads; `compress` truncates to the shorter input.
-   **One-shot sources:** `islice`, `take`, `nth`, and `groupby` consume
    inputs.
-   **Exceptions:** lazy pipelines often raise only when consumed, not
    when constructed.
-   **Mutable values:** `repeat(obj)` repeats the same reference.
-   **Side effects:** predicates and transforms may run later than
    expected; avoid depending on their exact timing beyond iteration
    order.

### 8.7 Readable loop versus iterator chain

This loop is often the best choice:

``` python
rows = [
    {"id": "a", "active": True, "amount": "12.5"},
    {"id": "b", "active": False, "amount": "4"},
    {"id": "c", "active": True, "amount": "-2"},
]
valid = []
for row in rows:
    if not row["active"]:
        continue
    amount = float(row["amount"])
    if amount < 0:
        continue
    valid.append((row["id"], amount))

print(valid)
# [('a', 12.5)]
```

A chain of `filter`, `map`, lambdas, `starmap`, and custom iterators
might be shorter in characters but harder to debug. Use iterator tools
when they make the transformation structure clearer, not merely to avoid
a `for` loop.

## 9. Testing strategy and runnable tests

Test both values and consumption semantics. Useful categories include:

1.  Normal input and expected ordering.
2.  Empty and one-item input.
3.  Exact batch boundaries and partial final batches.
4.  Invalid sizes and invalid records.
5.  Uneven source lengths.
6.  Infinite sources guarded by `islice`.
7.  Iterator exhaustion and group lifetime.
8.  Large synthetic streams where a list would be inappropriate.
9.  Error policy for malformed records.
10. Memory behavior measured as an experiment, not a brittle byte-exact
    unit test.

Example tests for built-ins:

``` python
import pytest
from itertools import (
    accumulate, batched, chain, compress, count, dropwhile,
    filterfalse, islice, pairwise, repeat, starmap, takewhile,
    zip_longest,
)

def test_basic_itertools():
    assert list(islice(count(10, 5), 4)) == [10, 15, 20, 25]
    assert list(chain([1, 2], (3,), "ab")) == [1, 2, 3, "a", "b"]
    assert list(accumulate([1, 2, 3, 4])) == [1, 3, 6, 10]
    assert list(compress("abcd", [1, 0, 1])) == ["a", "c"]
    assert list(takewhile(lambda x: x < 4, [1, 3, 4, 2])) == [1, 3]
    assert list(dropwhile(lambda x: x < 4, [1, 3, 4, 2])) == [4, 2]
    assert list(filterfalse(lambda x: x % 2, range(5))) == [0, 2, 4]
    assert list(starmap(pow, [(2, 3), (3, 2)])) == [8, 9]

def test_batches_and_windows():
    assert list(batched(range(7), 3)) == [(0, 1, 2), (3, 4, 5), (6,)]
    assert list(pairwise([1, 4, 9])) == [(1, 4), (4, 9)]
    assert list(zip_longest([1, 2], ["x"], fillvalue="-")) == [(1, "x"), (2, "-")]

def test_exhaustion_and_strict_zip():
    it = iter([1, 2])
    assert list(it) == [1, 2]
    assert list(it) == []
    assert list(zip([1, 2], ["a"])) == [(1, "a")]
    with pytest.raises(ValueError):
        list(zip([1, 2], ["a"], strict=True))
```

For the last test block, import `pytest`. In Python 3.12+, `batched` is
available; `pairwise` requires Python 3.10+. Keep tests deterministic
and avoid exact memory-byte assertions across machines.

## 10. Hands-on exercises

Attempt these before reading the suggested outcomes. Keep all
experiments bounded.

### Exercise 1 --- First N IDs

Given `source = (f"id-{n}" for n in count())`, return the first four IDs
without materializing the source.

**Expected behavior:** `["id-0", "id-1", "id-2", "id-3"]`.

### Exercise 2 --- Uneven columns

Combine timestamps `[100, 200, 300]` with statuses `["ok", "failed"]` so
that every timestamp is represented.

**Expected behavior:**
`[(100, "ok"), (200, "failed"), (300, "unknown")]`.

### Exercise 3 --- Consecutive status groups

Given statuses `["ok", "ok", "error", "ok"]`, group consecutive runs and
report their counts.

**Expected behavior:** `[("ok", 2), ("error", 1), ("ok", 1)]`; do not
assume the two `ok` runs are one group.

### Exercise 4 --- Batch validation

Write `chunks(records, size)` using `batched` and reject zero/negative
sizes.

**Expected behavior:** size 2 over `[1, 2, 3]` gives `[(1, 2), (3,)]`;
size 0 raises `ValueError`.

### Exercise 5 --- Unique events

Implement encounter-order deduplication by `event_id`, retaining the
first record for each ID. Consider missing IDs and unhashable keys.

**Expected behavior:** duplicate IDs yield only their first record;
define whether missing IDs are rejected or handled separately.

### Exercise 6 --- Sliding average

Use `sliding_window` to calculate averages over windows of three
measurements.

**Expected behavior:** `[1, 2, 3, 4]` yields windows `(1,2,3)` and
`(2,3,4)`, with averages `2.0` and `3.0`.

### Exercise 7 --- Bounded pipeline

Generate one million integers, filter multiples of 10, batch by 1,000,
and count processed values without storing all batches.

**Expected behavior:** 100,000 values processed in 100 batches; memory
should be bounded by current batch and pipeline state (excluding any
state added by your sink).

### Exercise 8 --- Strict alignment

Use `zip(strict=True)` to align two ID columns. Test both equal and
unequal lengths.

**Expected behavior:** equal inputs pair normally; unequal inputs raise
`ValueError` during consumption.

## 11. Mini-project: streaming event ETL

### Objective

Create a command-line-ready module that reads JSON Lines, validates
event records, removes debug events, normalizes accepted records, and
writes batches to a sink without holding the full dataset in memory.

### Requirements

-   Target Python 3.12+.
-   Use type annotations on public functions.
-   Parse each nonblank line as JSON and require an object.
-   Require a nonempty string `event_id`, a string `event_type`, and a
    nonnegative numeric `amount`; reject booleans as numeric amounts.
-   Filter out `event_type == "debug"`.
-   Normalize amount to `float`.
-   Batch using `itertools.batched`; reject batch sizes less than one.
-   Inject the writer function so the transformation can be tested
    without a database.
-   Define a deliberate malformed-row policy: fail fast or quarantine
    with a reason. Do not silently discard malformed JSON.
-   Test empty input, a partial final batch, malformed JSON, invalid
    schema, all-filtered input, and invalid batch size.
-   Ensure the sink does not retain all output batches in production.
-   Include a short note on idempotency and partial failure: if a sink
    writes batch 1 and fails on batch 2, reruns may duplicate batch 1
    unless the sink/job is designed to be idempotent.

### Suggested acceptance tests

``` python
def test_etl_filters_and_batches(tmp_path):
    source = tmp_path / "events.jsonl"
    source.write_text(
        '{"event_id":"a","event_type":"purchase","amount":2}\n'
        '{"event_id":"b","event_type":"debug","amount":1}\n'
        '{"event_id":"c","event_type":"refund","amount":3.5}\n'
        '{"event_id":"d","event_type":"purchase","amount":4}\n',
        encoding="utf-8",
    )
    batches = []
    assert run_etl(source, batches.append, batch_size=2) == 3
    assert batches == [
        (
            {"event_id": "a", "event_type": "purchase", "amount": 2.0},
            {"event_id": "c", "event_type": "refund", "amount": 3.5},
        ),
        ({"event_id": "d", "event_type": "purchase", "amount": 4.0},),
    ]

def test_etl_empty_file(tmp_path):
    source = tmp_path / "empty.jsonl"
    source.write_text("", encoding="utf-8")
    batches = []
    assert run_etl(source, batches.append, batch_size=10) == 0
    assert batches == []

def test_etl_rejects_bad_batch_size(tmp_path):
    source = tmp_path / "empty.jsonl"
    source.write_text("", encoding="utf-8")
    with pytest.raises(ValueError):
        run_etl(source, lambda batch: None, batch_size=0)

def test_etl_rejects_malformed_json(tmp_path):
    source = tmp_path / "bad.jsonl"
    source.write_text('{"event_id":\n', encoding="utf-8")
    with pytest.raises(ValueError, match="line 1"):
        run_etl(source, lambda batch: None)

def test_etl_rejects_non_object_json(tmp_path):
    source = tmp_path / "array.jsonl"
    source.write_text('[1, 2, 3]\n', encoding="utf-8")
    with pytest.raises(ValueError, match="line 1"):
        run_etl(source, lambda batch: None)

def test_etl_skips_invalid_schema(tmp_path):
    source = tmp_path / "invalid-schema.jsonl"
    source.write_text(
        '{"event_id":"x","event_type":"purchase","amount":"not-a-number"}\n',
        encoding="utf-8",
    )
    batches = []
    assert run_etl(source, batches.append) == 0
    assert batches == []

def test_etl_all_records_filtered(tmp_path):
    source = tmp_path / "debug-only.jsonl"
    source.write_text(
        '{"event_id":"x","event_type":"debug","amount":1}\n',
        encoding="utf-8",
    )
    batches = []
    assert run_etl(source, batches.append) == 0
    assert batches == []
```

Add tests for malformed JSON and wrong top-level JSON type; both should
raise `ValueError` with line context in the sample implementation. A
test sink that appends batches is suitable for small tests, but not for
production memory measurement because it deliberately stores all output.

## 12. Self-check questions with answers

### 1. Why does `groupby` need sorted input?

It does not technically require sorted input; it groups consecutive
runs. Sorting by the same key is needed when the intended result is one
group per key across the whole dataset. Sorting costs memory and time,
so an already ordered source is preferable for streaming.

### 2. Implement `sliding_window(iterable, n)` using `islice` and `deque`.

Use the `sliding_window` recipe in Section 5.5. Initialize a deque from
`islice(iterator, n)`, return no windows if fewer than `n` items exist,
yield the first tuple, then append each next item and yield the new
tuple. Reject `n <= 0`.

### 3. Which function chunks an iterable into tuples of fixed size in Python 3.12+?

`itertools.batched(iterable, n)`. The final tuple may be shorter unless
strict behavior is requested on Python 3.13+.

### 4. Which operations in this lesson can retain input values?

`cycle` retains its source pool; combinatoric tools pool their inputs;
`tee` buffers values until all branches pass them; `unique_everseen`
retains seen keys; `powerset` pools the source; `groupby` requires
careful group consumption; `list(...)` retains every collected result.
`batched` retains at most the current batch.

### 5. Why can `list(islice(count(), 10))` be safe while `list(count())` is not?

The first has a finite upper bound and collects ten items. The second
attempts to exhaust an infinite iterator and never completes.

### 6. What is the difference between `zip`, `zip_longest`, and `zip(strict=True)`?

`zip` stops at the shortest input. `zip_longest` continues until the
longest input and fills missing positions. Strict `zip` checks for
unequal lengths and raises `ValueError` rather than silently truncating.

### 7. Why can `tee` use substantial memory?

Branches share a source but must appear independent. Values consumed by
a fast branch are retained until slower branches consume them; memory
depends on branch lag.

### 8. When should you prefer a loop over `itertools`?

When the loop makes validation, branching, side effects, error handling,
or domain rules easier to read. Prefer the most maintainable
implementation, not the most compact expression.

### 9. Does using generators guarantee constant memory?

No. Any stage may buffer, sort, pool, deduplicate, or materialize. The
whole pipeline---including source client, transformation, queues, and
sink---must be bounded.

### 10. What does `tracemalloc` measure?

Python-traced memory allocations and peak traced memory. It is useful
for comparing Python allocation behavior, but it is not a complete
measurement of process RSS or every native allocation.

## 13. Mastery checklist

You are ready to move on when you can explain and demonstrate each item
without notes:

-   [ ] Distinguish iterable, iterator, and generator; explain
    exhaustion and laziness.
-   [ ] Use `count`, `cycle`, and `repeat` without accidentally creating
    nonterminating consumers.
-   [ ] Select among `chain`, `islice`, `zip_longest`, `accumulate`,
    `compress`, `takewhile`, `dropwhile`, `filterfalse`, and `starmap`.
-   [ ] Explain why `list(...)` is safe only for known, bounded input.
-   [ ] Estimate combinatorial output sizes before generating them.
-   [ ] Explain consecutive grouping and group iterator lifetime for
    `groupby`.
-   [ ] Explain `tee` buffering and when not to use it.
-   [ ] Use `pairwise` (Python 3.10+) and `batched` (Python 3.12+).
-   [ ] Distinguish `zip` truncation from strict length checking.
-   [ ] Implement and test `take`, `nth`, `flatten`, `unique_everseen`,
    `sliding_window`, `roundrobin`, `partition`, and `powerset`.
-   [ ] Build a streaming parse-filter-batch-write pipeline with
    explicit validation and failure policy.
-   [ ] Measure allocation peaks with `tracemalloc` and state its
    limitations.
-   [ ] Choose readable loops over unnecessarily complex iterator
    chains.

## 14. Concise reference table

  ----------------------------------------------------------------------
  Need                 Tool                         Important caveat
  -------------------- ---------------------------- --------------------
  Infinite integer     `count(start, step)`         Bound downstream
  sequence                                          consumption

  Repeat finite        `cycle(iterable)`            Caches finite source
  sequence                                          

  Repeat one value     `repeat(value, times)`       Same object
                                                    reference

  Concatenate streams  `chain(...)`                 One level only

  Flatten one level    `chain.from_iterable(...)`   Not recursive

  Read first N values  `islice(iterable, N)`        Consumes source

  Align uneven streams `zip_longest`                Infinite input means
                                                    infinite output

  Enforce equal        `zip(..., strict=True)`      Python 3.10+;
  lengths                                           mismatch appears
                                                    during iteration

  Running aggregate    `accumulate`                 Not a general
                                                    rolling aggregate

  Apply Boolean mask   `compress`                   Stops at shorter
                                                    input

  Initial true run     `takewhile`                  Consumes first
                                                    failing value

  Skip initial true    `dropwhile`                  Later matches are
  run                                               yielded

  Select false         `filterfalse`                Predicate semantics
  predicate                                         must be explicit

  Unpack argument      `starmap`                    Comprehension may be
  tuples                                            clearer

  Cartesian grid       `product`                    Pools inputs; output
                                                    can explode

  Ordered selections   `permutations`               Factorial growth

  Unordered selections `combinations`               Output grows
                                                    combinatorially

  Consecutive grouping `groupby`                    Sort by key for
                                                    global grouping

  Split iterator       `tee`                        Buffer grows with
  branches                                          branch lag

  Adjacent pairs       `pairwise`                   Python 3.10+

  Fixed-size batches   `batched`                    Python 3.12+; final
                                                    batch may be short

  Sliding windows      `sliding_window` recipe      O(window size) state

  Encounter-order      `unique_everseen` recipe     Retains seen keys
  deduplication                                     

  All subsets          `powerset` recipe            2ⁿ results; small
                                                    finite input only
  ----------------------------------------------------------------------

------------------------------------------------------------------------

**Engineering rule:** use lazy iteration to control data flow, but
verify the memory behavior of every stage. Bound inputs and batches,
make consumption semantics explicit, test edge cases, and favor code a
teammate can debug at 2 a.m.
