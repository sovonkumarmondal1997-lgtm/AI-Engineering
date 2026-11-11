# Map, Filter, Reduce, and Sorting with Key Functions

> **Level:** Beginner → advanced  
> **Target:** Python 3.12+  
> **Module:** Stage 1 — Programming & Computational Thinking, Module 1.24, Lesson 05  
> **Focus:** Choosing clear, correct, memory-aware transformations and ordering operations for reliable data pipelines.

## Learning objectives

By the end of this lesson, you should be able to:

- Explain the contracts and return values of `map`, `filter`, `functools.reduce`, `sorted`, `list.sort`, `min`, and `max`.
- Predict iterator laziness, one-pass consumption, exhaustion, and the memory consequences of materialization.
- Choose among comprehensions, generator expressions, built-ins, `itertools`, explicit loops, and `reduce` based on intent.
- Design deterministic sort keys for records, missing values, mixed directions, ties, and locale-aware text.
- Use counting, grouping, top-K selection, first-match lookup, `zip(strict=True)`, and `enumerate` appropriately.
- Build a tested `top_k(items, k, *, key=None, reverse=False)` helper whose semantics match `sorted(items, key=key, reverse=reverse)[:k]`.
- Recognize floating-point, NaN, mutation, side-effect, streaming, and parallel-execution hazards.
- Test stable ordering, tie-breaking, permutation, and input preservation.

## Prerequisites and scope

You should already know basic functions and callables, lambdas, loops, list/dict/set comprehensions, generator expressions, mutability, iterators, exceptions, type hints, and `pytest`. The earlier module material on pure functions and side effects, collection operations, `functools`, generators, and performance measurement is directly relevant. Lesson 03 introduces closures and Lesson 04 covers late binding; this lesson applies those ideas to callback/key-function APIs.

This lesson stays with Python's standard library. NumPy and pandas may be faster for appropriate columnar numerical workloads, but their APIs are not taught here. Distributed map APIs are mentioned only to clarify their different execution and serialization contracts.

## 1. Transformation fundamentals

A transformation consumes input values and produces other values. A filter selects which values continue. An aggregation combines many values into a result. Sorting reorders values according to an ordering rule.

```text
source ── map(transform) ── filter(predicate) ── aggregate / materialize
  │              │                 │                       │
  └── values     └── new values     └── selected values    └── result
```

These operations are not interchangeable. A good pipeline makes the intent obvious and avoids materializing large intermediate collections without need.

### 1.1 `map`: transform each input

**Signature:** `map(function, iterable, /)` or `map(function, iterable1, iterable2, /, *iterables)` in current Python. `map` returns a lazy iterator, not a list.

```python
raw_ids = [" 101 ", " 102 ", "103 "]
parsed_ids = map(int, map(str.strip, raw_ids))
print(list(parsed_ids))
```

Expected output:

```text
[101, 102, 103]
```

The nested `map` is valid but can be harder to read than a comprehension:

```python
parsed_ids = [int(value.strip()) for value in raw_ids]
print(parsed_ids)  # [101, 102, 103]
```

Prefer `map` when an existing named function or built-in directly expresses the transformation, such as `map(int, values)`, `map(str.strip, lines)`, or `map(json.loads, json_lines)`. Prefer a comprehension when the transformation is inline or when it combines transformation and selection.

### 1.2 Multiple iterables and `operator`

With multiple iterables, `map` calls the function with one item from each iterable. Iteration stops when the shortest input is exhausted.

```python
from operator import add

left = [10, 20, 30]
right = [1, 2]
print(list(map(add, left, right)))  # [11, 22]
```

If different lengths are a data-integrity error, do not silently accept truncation. Python 3.10+ supports `zip(strict=True)` for paired iteration:

```python
left = [10, 20, 30]
right = [1, 2]
try:
    print([a + b for a, b in zip(left, right, strict=True)])
except ValueError as exc:
    print(type(exc).__name__)
```

Expected output:

```text
ValueError
```

`zip(strict=True)` detects a length mismatch when iteration reaches the point where one iterable ends before another; do not assume every input has been validated before earlier output is consumed. In a production pipeline, validate or stage results if partial processing before the exception would be harmful.

### 1.3 `filter`: keep values that pass a predicate

**Signature:** `filter(function_or_none, iterable, /)`. It returns a lazy iterator. With a predicate, values are retained when the predicate result is truthy. With `None`, it retains truthy values.

```python
measurements = [-2.0, 0.0, 1.5, 4.0, -0.1]
positive = filter(lambda value: value > 0, measurements)
print(list(positive))  # [1.5, 4.0]

raw_flags = ["", "ready", None, 0, "0", False]
print(list(filter(None, raw_flags)))  # ['ready', '0']
```

**Pitfall:** `filter(None, values)` removes all falsy values, not just `None`. It drops `0`, `False`, `""`, and other falsy objects. If only `None` is missing, write `value is not None`:

```python
values = [0, None, 2, False, ""]
print([value for value in values if value is not None])
# [0, 2, False, '']
```

A comprehension is often more readable than `filter(lambda ...)` because it keeps the condition next to the output expression.

### 1.4 `functools.reduce`: fold values into one result

**Signature:** `functools.reduce(function, iterable, /[, initial])`. The function receives an accumulator and the next item. Without `initial`, the first iterable item becomes the accumulator; with `initial`, folding begins from that value.

```python
from functools import reduce
from operator import mul

values = [2, 3, 4]
print(reduce(mul, values))       # 24
print(reduce(mul, values, 10))   # 240
```

Without an initial value, reducing an empty iterable raises `TypeError`. With an initial value, the result is that initial value:

```python
print(reduce(mul, [], 1))  # 1
```

A reduce operation can be correct but obscure. For ordinary addition use `sum`; for a product use `math.prod`; for a readable stateful transformation use a loop. `reduce` is most appropriate when the fold itself is the natural abstraction, such as composing functions or combining values with a well-defined associative operation.

```python
# Harder to read for a simple total:
total = reduce(lambda accumulator, value: accumulator + value, values, 0)

# Preferred:
total = sum(values)
```

### 1.5 Side-by-side choices

| Intent | Clear default | Alternative | Why |
|---|---|---|---|
| Transform every value | Comprehension or `map(named_function, xs)` | `map(lambda, xs)` | Named functions make intent explicit; comprehensions make inline logic visible. |
| Select values | Comprehension with `if` | `filter(predicate, xs)` | Comprehension usually reads better with an inline predicate. |
| Sum numbers | `sum(xs)` | `reduce(add, xs)` | Built-in states intent and handles empty input naturally. |
| Product | `math.prod(xs)` | `reduce(mul, xs, 1)` | `math.prod` is the direct API. |
| Test whether any pass | `any(pred(x) for x in xs)` | Manual loop | `any` short-circuits. |
| Test whether all pass | `all(pred(x) for x in xs)` | Manual loop | `all` short-circuits; empty input yields `True`. |
| Running totals | `itertools.accumulate(xs)` | Manual loop | Emits each intermediate accumulator. |
| Multi-step state update | Explicit `for` loop | `reduce` | A loop is often easier to debug and type. |

```python
from itertools import accumulate
from math import prod

values = [2, 3, 4]
print(sum(values))                         # 9
print(prod(values))                        # 24
print(list(accumulate(values)))            # [2, 5, 9]
print(any(value > 3 for value in values))  # True
print(all(value > 0 for value in values))  # True
```

`any` and `all` stop as soon as the answer is known. The generator expression avoids building a list. For an empty iterable, `any(...)` is `False` and `all(...)` is `True`—the latter means “there is no counterexample,” not “there was at least one item.”

## 2. Laziness, iterators, and memory

### 2.1 Lazy operations defer work

`map`, `filter`, generator expressions, and many `itertools` functions produce iterators. They generally do not process all values when created; work happens as values are requested.

```python
def normalize(value: str) -> str:
    print(f"normalizing {value}")
    return value.strip().lower()

source = [" A ", " B "]
result = map(normalize, source)
print("created")
print(next(result))
print(list(result))
```

Expected output:

```text
created
normalizing  A 
a
normalizing  B 
['b']
```

The first `next` consumes the first result. `list(result)` consumes only the remainder. This is a frequent source of confusing logs and partial results.

### 2.2 One pass means one pass

```python
values = map(int, ["1", "2", "3"])
print(list(values))  # [1, 2, 3]
print(list(values))  # [] — already exhausted
```

**Incorrect assumption:** a lazy iterator behaves like a reusable list. If you need two passes, either retain a materialized result or recreate the iterator from a re-iterable source.

```python
source = ["1", "2", "3"]
first_pass = map(int, source)
second_pass = map(int, source)
print(sum(first_pass), sum(second_pass))  # 6 6
```

A generator, database cursor, network stream, or file iterator may be single-pass and may own resources. Do not assume you can rewind it.

### 2.3 Streaming versus materialization

```python
from itertools import islice

# Produces only the first five qualifying values, without storing the full output.
large_source = range(10_000_000)
first_five = list(islice((x * x for x in large_source if x % 2 == 0), 5))
print(first_five)  # [0, 4, 16, 36, 64]
```

The generator pipeline holds only the state needed to produce the next value, plus the five outputs explicitly collected. By contrast, `list(map(...))` stores every result and may be expensive for a large input. Laziness does not guarantee constant memory for the whole program: the source, downstream consumer, caches, sort operation, or a `tee` buffer may retain data.

`sorted(iterable)` must consume its input and store items to order them, so it is not a streaming sort. If a full sort does not fit in memory, use a suitable external/distributed sort or change the requirement; do not expect `sorted` to stream sorted output from an arbitrary unsorted source.

### 2.4 `itertools.tee` is not a free replay button

`itertools.tee(iterator, n)` creates independent logical iterators, but values consumed by one branch may need to be buffered until other branches catch up. If one branch runs far ahead, the buffer can grow substantially.

```python
from itertools import tee

source = iter(range(4))
left, right = tee(source)
print(next(left))
print(next(left))
print(list(right))  # [0, 1, 2, 3]
```

Use `tee` only when multiple consumers genuinely need the same one-pass source and their consumption patterns are understood. For a finite, modest dataset, materializing once may be simpler and easier to reason about.

## 3. Sorting and key functions

### 3.1 `sorted`, `list.sort`, `min`, and `max`

- `sorted(iterable, *, key=None, reverse=False)` returns a **new list** and leaves the source collection's order unchanged.
- `list.sort(*, key=None, reverse=False)` sorts a list **in place** and returns `None`.
- `min(iterable, *, key=None, default=...)` and `max(iterable, *, key=None, default=...)` select an extremum; `default=` is used only if the iterable is empty. (The actual built-in signatures make `default` optional and keyword-only in this iterable form.)
- `min(a, b, *args, key=None)` and `max(a, b, *args, key=None)` also accept multiple positional values, but that form does not accept `default=`.

```python
scores = [8, 3, 10, 3]
ordered = sorted(scores)
scores.sort(reverse=True)
print(ordered)  # [3, 3, 8, 10]
print(scores)   # [10, 8, 3, 3]
print(min([], default=None))  # None
print(max([], default=0))     # 0
```

Do not write `ordered = scores.sort()`: `ordered` would be `None` because `list.sort` mutates and returns no list.

### 3.2 `key=` transforms each item into a comparison key

The key function defines the ordering criterion. Python calls the key function once per item for a single sorting operation and uses those key values to compare records. This avoids recalculating an expensive key for every pairwise comparison.

```python
words = ["pear", "Apple", "fig", "banana"]
print(sorted(words, key=len))             # ['fig', 'pear', 'Apple', 'banana']
print(sorted(words, key=str.lower))       # ['Apple', 'banana', 'fig', 'pear']
print(sorted([-7, 2, -1, 5], key=abs))    # [-1, 2, 5, -7]
```

The sort is **stable**: if two elements have equal keys, their relative input order is preserved. Stability is useful when ranking records with equal metrics and when applying multiple stable sorts.

```python
rows = [("bronze", 7), ("silver", 7), ("gold", 9)]
print(sorted(rows, key=lambda row: row[1]))
# [('bronze', 7), ('silver', 7), ('gold', 9)]
```

The two rows with score 7 remain in their original relative order. The reverse flag reverses the overall ordering but Python's sort remains stable for equal keys, including with `reverse=True`.

**Key functions should be pure and deterministic.** Avoid keys that mutate records, read changing global state, consume shared iterators, or perform side effects. Although the key is evaluated once per item during one sort, the order of those calls should not be used as an application contract.

### 3.3 Common key functions

```python
from operator import attrgetter, itemgetter

records = [
    {"name": "Mira", "score": 92},
    {"name": "Arun", "score": 92},
    {"name": "Zoe", "score": 87},
]
print(sorted(records, key=itemgetter("name")))
print(sorted(records, key=itemgetter("score", "name")))
```

`operator.itemgetter("name")` reads a mapping item; `itemgetter(1)` reads a sequence element. `operator.attrgetter("name")` reads an attribute from an object. They avoid a tiny lambda and often communicate intent well.

```python
from dataclasses import dataclass
from operator import attrgetter

@dataclass(frozen=True)
class ModelRun:
    run_id: str
    loss: float
    duration_seconds: int

runs = [
    ModelRun("run-c", 0.21, 80),
    ModelRun("run-a", 0.19, 95),
    ModelRun("run-b", 0.19, 70),
]
print([run.run_id for run in sorted(runs, key=attrgetter("loss", "duration_seconds"))])
# ['run-b', 'run-a', 'run-c']
```

Use `len`, `str.lower`, `abs`, tuples, `itemgetter`, and `attrgetter` when they make the rule clearer. Use a named key function for domain rules that need documentation, validation, or reuse.

### 3.4 Multi-key ordering

Tuple keys compare lexicographically: the first component decides unless equal, then the next component is considered. For example, sort by department ascending, then salary descending:

```python
employees = [
    {"name": "Asha", "department": "data", "salary": 120},
    {"name": "Dev", "department": "data", "salary": 150},
    {"name": "Mina", "department": "ml", "salary": 130},
]
ordered = sorted(employees, key=lambda row: (row["department"], -row["salary"]))
print([(row["name"], row["department"], row["salary"]) for row in ordered])
# [('Dev', 'data', 150), ('Asha', 'data', 120), ('Mina', 'ml', 130)]
```

Negating a numeric value reverses that numeric component, but is not a universal solution for arbitrary key types. Do not negate strings or mixed objects. A second clear approach is stable multi-pass sorting: sort by the least significant key first, then the more significant key.

```python
from operator import itemgetter

ordered = sorted(employees, key=itemgetter("salary"), reverse=True)
ordered = sorted(ordered, key=itemgetter("department"))
print([(row["name"], row["department"], row["salary"]) for row in ordered])
# [('Dev', 'data', 150), ('Asha', 'data', 120), ('Mina', 'ml', 130)]
```

The second sort is stable, so salary ordering is retained within each department. This method handles mixed directions without inventing reversed values, but performs multiple sorting passes. For many criteria, a tuple key is usually concise when directions align; stable multi-pass sorting is useful when directions differ or keys are not naturally invertible.

### 3.5 `cmp_to_key` for legacy comparators

A key function returns a value to compare. A legacy comparator returns a negative number, zero, or a positive number depending on whether the first value sorts before, equal to, or after the second. Adapt such a comparator with `functools.cmp_to_key` only when you must preserve a comparator-based API.

```python
from functools import cmp_to_key

def compare_length_then_name(left: str, right: str) -> int:
    by_length = len(left) - len(right)
    if by_length:
        return by_length
    return (left > right) - (left < right)

words = ["pear", "fig", "plum", "apple"]
print(sorted(words, key=cmp_to_key(compare_length_then_name)))
# ['fig', 'pear', 'plum', 'apple']
```

Prefer a normal `key=` when possible: it is simpler and generally avoids repeated comparator calls. Comparators must obey a consistent ordering; contradictory comparisons can produce confusing results.

### 3.6 Missing values, mixed types, NaN, and locale

**Mixed incomparable types:** Python 3 does not define a general ordering between unrelated types such as `int` and `str`.

```python
try:
    sorted([3, "2", 1])
except TypeError as exc:
    print(type(exc).__name__)  # TypeError
```

Normalize values at the boundary or define an explicit type-aware key. Do not silently stringify every value unless lexical ordering is the actual business rule (`"10"` sorts before `"2"`).

**`None` handling:** `(value is None, value)` places non-`None` values first for mutually comparable non-`None` values. The Boolean first component is `False` for real values and `True` for `None`.

```python
values = [3, None, 1, 2, None]
print(sorted(values, key=lambda value: (value is None, value if value is not None else 0)))
# [1, 2, 3, None, None]
```

The fallback `0` is never used to rank a non-`None` value against `None` because the first tuple element differs. For richer schemas, make missing-value placement explicit in a named key and test it.

**NaN:** IEEE floating-point NaN is unordered: comparisons such as `nan < 1`, `nan > 1`, and `nan == nan` are all false. Sorting raw values containing NaN therefore does not provide the intuitive numeric ranking users may expect. Normalize or separate NaNs explicitly.

```python
from math import isnan, nan

values = [3.0, nan, 1.0]
def nan_last(value: float) -> tuple[bool, float]:
    return (isnan(value), 0.0 if isnan(value) else value)

print(["nan" if isnan(x) else x for x in sorted(values, key=nan_last)])
# [1.0, 3.0, 'nan']
```

**Locale-aware text:** ordinary string sorting uses Unicode code-point order, not the current human language's collation rules. For locale-aware collation, use `locale.strxfrm` as a key after deliberately configuring the process locale. Locale configuration is process-global and environment-dependent, so it can reduce reproducibility across machines. For stable production rankings, prefer a documented normalization/collation policy and test the actual locale/runtime.

**Deterministic ordering:** a stable sort preserves prior order for equal keys, but stability alone does not guarantee repeatable results if the input order varies between runs (for example, data collected from an unordered source). Add a deterministic tie-breaker such as a unique record ID when business semantics permit it.

## 4. Intermediate patterns for data work

### 4.1 Normalize records and validate rows

```python
from collections.abc import Iterable, Mapping
from typing import Any

RawRecord = Mapping[str, Any]

def normalize_record(row: RawRecord) -> dict[str, Any]:
    return {
        "record_id": str(row["record_id"]).strip(),
        "country": str(row["country"]).strip().upper(),
        "amount": float(row["amount"]),
    }

def is_valid_record(row: Mapping[str, Any]) -> bool:
    return bool(row["record_id"]) and row["amount"] >= 0

raw_rows = [
    {"record_id": " A-1 ", "country": "in", "amount": "12.5"},
    {"record_id": "B-2", "country": "us", "amount": "0"},
    {"record_id": " C-3 ", "country": "gb", "amount": "-4"},
]
normalized = (normalize_record(row) for row in raw_rows)
valid = [row for row in normalized if is_valid_record(row)]
print(valid)
# [{'record_id': 'A-1', 'country': 'IN', 'amount': 12.5},
#  {'record_id': 'B-2', 'country': 'US', 'amount': 0.0}]
```

This generator expression delays normalization until consumed. The list comprehension materializes only valid output records. In real ingestion code, decide explicitly what happens when conversion raises `ValueError`, required keys are missing, or a record violates the schema: reject, quarantine, or fail the batch. Do not let a compact expression hide a data-quality policy.

### 4.2 Ranking model runs with tie-breakers

```python
runs = [
    {"run_id": "r-9", "validation_loss": 0.18, "started_at": "2026-01-03"},
    {"run_id": "r-2", "validation_loss": 0.16, "started_at": "2026-01-04"},
    {"run_id": "r-1", "validation_loss": 0.16, "started_at": "2026-01-02"},
]
best = min(runs, key=lambda run: (run["validation_loss"], run["started_at"], run["run_id"]))
leaderboard = sorted(runs, key=lambda run: (run["validation_loss"], run["started_at"], run["run_id"]))
print(best["run_id"])  # r-1
print([run["run_id"] for run in leaderboard])  # ['r-1', 'r-2', 'r-9']
```

Document whether a lower or higher metric is better, how ties are resolved, and whether missing or non-finite metrics are allowed. A tie-breaker is part of the ranking contract, not an implementation detail.

### 4.3 Counting, grouping, and first-match lookup

```python
from collections import Counter, defaultdict
from itertools import groupby
from operator import itemgetter

countries = ["IN", "US", "IN", "GB", "US", "IN"]
print(Counter(countries))  # Counter({'IN': 3, 'US': 2, 'GB': 1})

rows = [
    {"country": "IN", "id": 1},
    {"country": "US", "id": 2},
    {"country": "IN", "id": 3},
]
groups: dict[str, list[dict[str, object]]] = defaultdict(list)
for row in rows:
    groups[row["country"]].append(row)
print([row["id"] for row in groups["IN"]])  # [1, 3]

ordered_rows = sorted(rows, key=itemgetter("country"))
compact_groups = {
    country: list(group)
    for country, group in groupby(ordered_rows, key=itemgetter("country"))
}
print(sorted(compact_groups))  # ['IN', 'US']
```

`itertools.groupby` groups **consecutive** equal keys, not all equal keys anywhere in an arbitrary input. Sort by the same key first if you want global groups. Each group iterator shares the underlying source, so materialize each group while iterating if it must be retained.

For first-match lookup, `next` with a generator avoids materializing all matches:

```python
records = [{"id": 1, "active": False}, {"id": 2, "active": True}]
first_active = next((row for row in records if row["active"]), None)
print(first_active)  # {'id': 2, 'active': True}
```

If `None` is a valid record value, use a unique sentinel rather than `None` as the “not found” marker.

### 4.4 Top-K selection

If you need only a small number of highest or lowest values, `heapq.nsmallest`/`heapq.nlargest` can avoid fully sorting the entire input. For small `k` relative to `n`, this can reduce comparison work; for large `k`, a full sort may be competitive. Benchmark representative data rather than relying on a universal cutoff.

```python
from heapq import nlargest

scores = [12, 80, 45, 91, 73]
print(nlargest(3, scores))  # [91, 80, 73]
```

Top-K helpers need a clear tie contract. A heap-based implementation can choose a different subset among equal keys than `sorted(... )[:k]`, unless it deliberately preserves the same stable tie behavior. This lesson's `top_k` helper uses sorting to match the exact reference semantics.

### 4.5 Companion iteration tools

```python
names = ["Asha", "Dev", "Mina"]
print(list(enumerate(names, start=1)))
# [(1, 'Asha'), (2, 'Dev'), (3, 'Mina')]

prices = [10, 20, 30]
quantities = [2, 1, 4]
print([price * quantity for price, quantity in zip(prices, quantities, strict=True)])
# [20, 20, 120]
```

Useful `itertools` companions include `chain` to concatenate streams, `islice` to take a bounded prefix, `starmap` to call a function with argument tuples, `accumulate` for running reductions, and `groupby` for adjacent grouping. Each is lazy unless its contract says otherwise; understand source consumption before reusing an iterator.

## 5. Advanced correctness and performance

### 5.1 Floating-point accumulation

Floating-point addition is not mathematically associative at finite precision. Different accumulation orders can produce slightly different results.

```python
import math

values = [0.1] * 10
print(sum(values))
print(math.fsum(values))
```

`math.fsum` tracks partial sums to provide a more accurate floating-point sum for many inputs. Do not promise a particular printed decimal representation without running the target Python version; the important property is that `fsum` is designed for improved accuracy. For financial values, use a domain-appropriate representation such as `decimal.Decimal` when exact decimal arithmetic is required.

### 5.2 Key-call count and mutation hazards

```python
calls = 0
def key_with_counter(value: int) -> int:
    global calls
    calls += 1
    return value

values = [3, 1, 2]
print(sorted(values, key=key_with_counter))
print(calls)  # 3: one key call per element for this sort
```

This example is an observation, not a recommendation to build side effects into keys. A key that mutates an item can change data during ranking; a key that reads the clock or mutable global state can produce results that are difficult to reproduce. Precompute a field explicitly when it is expensive, reused, or belongs in the record's data contract.

Never mutate the list being iterated or sorted from inside a key function. Avoid using `list.sort` when another part of the program expects the original order. Use `sorted` when you need an independent ordered list, and remember that a shallow copy still refers to the same mutable record objects.

### 5.3 Comprehensions, `map`, `reduce`, and vectorization

- A list comprehension is often the clearest and efficient choice for Python-level transformation plus filtering.
- `map` with a built-in or named function can be concise and may perform well because the call path is implemented in optimized code.
- `map(lambda ...)` adds a Python function call per item and is often less readable than a comprehension; the relative speed depends on the function and workload.
- `reduce` does not automatically make code faster. It still calls a function repeatedly and can obscure the accumulator's meaning.
- Numeric array libraries can eliminate Python-level per-element overhead for suitable homogeneous numeric workloads, but only use vectorization when data shape, missing-value behavior, and semantics match the task.

**No benchmark claim is universal.** Measure with representative input sizes, data types, interpreter builds, and realistic key functions. Avoid timing tiny snippets once and treating the result as a production guarantee.

A reproducible starting point is `timeit`; run this on the same Python build and data shape that matter to your workload. It prints local measurements rather than assuming a winner:

```python
from timeit import repeat

values = list(range(100_000))
cases = {
    "comprehension": "[int(x) for x in values]",
    "map builtin": "list(map(int, values))",
    "map lambda": "list(map(lambda x: int(x), values))",
}
for label, statement in cases.items():
    seconds = min(repeat(statement, globals=globals(), number=10, repeat=5)) / 10
    print(f"{label}: {seconds:.6f} seconds per run (best of 5 repeats)")
```

This is a microbenchmark, not proof of end-to-end pipeline speed. Here `values` already contains integers, so the conversion does little work; for a real comparison, use representative strings, error rates, transformations, and output consumption. Benchmark equivalent semantics, include setup costs when they belong to the production path, and record the interpreter and machine context with the result.

### 5.4 `Executor.map` and multiprocessing map

`concurrent.futures.Executor.map` and `multiprocessing.Pool.map` are related in name to built-in `map`, but their execution and operational contracts differ. They schedule work through an executor or process pool, may introduce serialization and scheduling overhead, and are not drop-in performance wins for cheap transformations.

```python
from concurrent.futures import ThreadPoolExecutor

def normalize_id(value: str) -> int:
    return int(value.strip())

with ThreadPoolExecutor(max_workers=2) as executor:
    result = list(executor.map(normalize_id, [" 10 ", " 20 ", "30"]))
print(result)  # [10, 20, 30]
```

`Executor.map` yields results in input order, even if tasks finish in a different order. Threads are useful for suitable I/O-bound workloads; CPU-bound Python work may not speed up under the GIL. Process pools can help CPU-bound work but incur process startup, IPC, and pickling costs. Functions and arguments generally need to be picklable for process execution; top-level named functions are safer than lambdas or nested functions. Guard process-pool entry points with `if __name__ == "__main__":` in scripts on platforms that use spawn semantics.

`multiprocessing.Pool.map` has a `chunksize` parameter. `Executor.map` in Python 3.12 also supports `chunksize` for `ProcessPoolExecutor` (ignored by thread and interpreter executors); its `buffersize` parameter was added in Python 3.14, so it is **not** part of the Python 3.12 target contract. Do not copy newer API parameters into 3.12 code without checking the target version. Chunking trades scheduling overhead against load balancing and latency; benchmark on realistic tasks.

## 6. A reusable `top_k` helper

Define semantics before implementation:

- `k` must be a non-negative integer; booleans are rejected even though `bool` is a subclass of `int`.
- `k == 0` returns an empty list without consuming the iterable.
- `key=None` uses normal item ordering, matching `sorted`.
- `reverse` follows `sorted` semantics.
- The result matches `sorted(items, key=key, reverse=reverse)[:k]`, including stable ties.
- Input items and a caller-owned list's order are not mutated.

```python
from collections.abc import Callable, Iterable
from typing import TypeVar

T = TypeVar("T")
K = TypeVar("K")

def top_k(
    items: Iterable[T],
    k: int,
    *,
    key: Callable[[T], K] | None = None,
    reverse: bool = False,
) -> list[T]:
    """Return the first k items under sorted() ordering, without mutating input."""
    if isinstance(k, bool) or not isinstance(k, int):
        raise TypeError("k must be an integer, not bool")
    if k < 0:
        raise ValueError("k must be non-negative")
    if k == 0:
        return []
    return sorted(items, key=key, reverse=reverse)[:k]
```

This implementation fully sorts, with worst-case `O(n log n)` time and `O(n)` auxiliary storage; Python's adaptive sort can run in `O(n)` time on already ordered input. The slice creates the returned list as well, so peak storage remains `O(n)`. This approach is intentionally chosen for semantic simplicity. For very large streams and small `k`, a heap implementation may use less memory, but matching stable tie behavior requires careful design and dedicated tests. Do not replace this implementation with `heapq` without preserving its documented ordering contract.

## 7. Testing transformations and ordering

Save the following as `test_transform_sorting.py`. Run with `python -m pytest -q`. These tests exercise the public contract, not implementation details.

```python
from collections.abc import Callable, Iterable
from math import isnan, nan
from typing import TypeVar

import pytest

T = TypeVar("T")
K = TypeVar("K")

def top_k(
    items: Iterable[T],
    k: int,
    *,
    key: Callable[[T], K] | None = None,
    reverse: bool = False,
) -> list[T]:
    """Return the first k items under sorted() ordering, without mutating input."""
    if isinstance(k, bool) or not isinstance(k, int):
        raise TypeError("k must be an integer, not bool")
    if k < 0:
        raise ValueError("k must be non-negative")
    if k == 0:
        return []
    return sorted(items, key=key, reverse=reverse)[:k]

def test_map_and_filter_are_lazy_and_one_pass():
    calls = []
    mapped = map(lambda x: calls.append(x) or x * 2, [1, 2, 3])
    assert calls == []
    assert next(mapped) == 2
    assert calls == [1]
    assert list(mapped) == [4, 6]
    assert list(mapped) == []


def test_filter_none_removes_all_falsy_values():
    assert list(filter(None, [0, None, "", "0", False, 2])) == ["0", 2]


def test_reduce_empty_input_requires_initial_value():
    from functools import reduce
    from operator import add
    with pytest.raises(TypeError):
        reduce(add, [])
    assert reduce(add, [], 0) == 0


def test_sort_is_stable_for_equal_keys():
    rows = [("first", 5), ("second", 5), ("third", 7)]
    assert sorted(rows, key=lambda row: row[1]) == [
        ("first", 5), ("second", 5), ("third", 7)
    ]


def test_sort_reverse_is_still_stable_for_equal_keys():
    rows = [("first", 5), ("second", 5), ("third", 7)]
    assert sorted(rows, key=lambda row: row[1], reverse=True) == [
        ("third", 7), ("first", 5), ("second", 5)
    ]


def test_key_is_called_once_per_item():
    calls = []
    def key(value):
        calls.append(value)
        return value
    assert sorted([3, 1, 2], key=key) == [1, 2, 3]
    assert len(calls) == 3
    assert sorted(calls) == [1, 2, 3]


def test_tuple_key_tie_breaking_is_deterministic():
    runs = [
        {"id": "b", "loss": 0.1, "day": 2},
        {"id": "a", "loss": 0.1, "day": 1},
        {"id": "c", "loss": 0.2, "day": 1},
    ]
    ordered = sorted(runs, key=lambda row: (row["loss"], row["day"], row["id"]))
    assert [row["id"] for row in ordered] == ["a", "b", "c"]


def test_none_last_key():
    values = [3, None, 1, None, 2]
    key = lambda value: (value is None, value if value is not None else 0)
    assert sorted(values, key=key) == [1, 2, 3, None, None]


def test_nan_last_key():
    values = [3.0, nan, 1.0]
    def key(value: float):
        return (isnan(value), 0.0 if isnan(value) else value)
    ordered = sorted(values, key=key)
    assert ordered[:2] == [1.0, 3.0]
    assert isnan(ordered[2])


def test_zip_strict_detects_mismatched_lengths():
    with pytest.raises(ValueError):
        list(zip([1, 2, 3], [4, 5], strict=True))


def test_groupby_requires_adjacent_keys_or_sorting_first():
    from itertools import groupby
    values = ["IN", "US", "IN"]
    groups = [(key, list(group)) for key, group in groupby(values)]
    assert groups == [("IN", ["IN"]), ("US", ["US"]), ("IN", ["IN"])]


def test_top_k_matches_sorted_reference_and_preserves_input():
    values = [("a", 4), ("b", 4), ("c", 7), ("d", 1)]
    original = values.copy()
    assert top_k(values, 3, key=lambda row: row[1]) == sorted(
        values, key=lambda row: row[1]
    )[:3]
    assert values == original


def test_top_k_reverse_preserves_stable_ties():
    values = [("a", 4), ("b", 4), ("c", 7)]
    assert top_k(values, 3, key=lambda row: row[1], reverse=True) == [
        ("c", 7), ("a", 4), ("b", 4)
    ]


def test_top_k_preserves_stable_ties_at_the_cutoff():
    values = [("first", 2), ("second", 2), ("third", 2), ("higher", 3)]
    assert top_k(values, 2, key=lambda row: row[1]) == [
        ("first", 2), ("second", 2)
    ]
    assert top_k(values, 2, key=lambda row: row[1], reverse=True) == [
        ("higher", 3), ("first", 2)
    ]


def test_top_k_matches_reference_across_deterministic_generated_cases():
    import random

    rng = random.Random(20261018)
    for _ in range(100):
        values = [(index, rng.randrange(-3, 4)) for index in range(rng.randrange(20))]
        for reverse in (False, True):
            for k in (0, 1, len(values) // 2, len(values), len(values) + 2):
                assert top_k(values, k, key=lambda row: row[1], reverse=reverse) == sorted(
                    values, key=lambda row: row[1], reverse=reverse
                )[:k]


def test_top_k_edge_cases():
    assert top_k([3, 1], 0) == []
    assert top_k([], 4) == []
    assert top_k([3, 1], 9) == [1, 3]
    with pytest.raises(ValueError):
        top_k([1], -1)
    with pytest.raises(TypeError):
        top_k([1], True)
    with pytest.raises(TypeError):
        top_k([1], 1.5)


def test_top_k_zero_does_not_consume_generator():
    consumed = []
    def source():
        for value in range(3):
            consumed.append(value)
            yield value
    iterator = source()
    assert top_k(iterator, 0) == []
    assert consumed == []
    assert next(iterator) == 0


def test_sorted_does_not_mutate_source_list():
    source = [3, 1, 2]
    result = sorted(source)
    assert result == [1, 2, 3]
    assert source == [3, 1, 2]


def test_min_max_default_only_for_empty_iterable():
    assert min([], default=10) == 10
    assert max([3, 1], default=10) == 3


def test_zip_strict_can_raise_after_partial_consumption():
    paired = zip([1, 2, 3], [4, 5], strict=True)
    assert next(paired) == (1, 4)
    assert next(paired) == (2, 5)
    with pytest.raises(ValueError):
        next(paired)
```

### Property-oriented test ideas

For a sort helper, useful properties include:

- **Permutation:** the output contains exactly the same items as the input, including duplicates.
- **Sortedness:** adjacent output keys are non-decreasing (or non-increasing for `reverse=True`).
- **Stability:** equal-key items preserve their relative input order.
- **Input preservation:** the original list order and record contents are unchanged.
- **Reference equivalence:** `top_k(xs, k, key=key, reverse=reverse)` equals `sorted(xs, key=key, reverse=reverse)[:k]` for generated cases.
- **Boundary behavior:** `k=0`, empty input, `k > len(xs)`, ties at the cutoff, invalid `k`, and key exceptions.

If using Hypothesis, generate finite lists with duplicates and a deterministic key, then compare against `sorted` as the oracle. Keep generated values mutually comparable unless the test is specifically exercising missing or mixed-type behavior.

## 8. Exercises with solutions

### Exercise 1 — Parse and select

Given `raw = [" 12 ", "-3", "0", " 7"]`, produce positive integers only. Avoid an intermediate list of every parsed integer.

**Solution:**

```python
raw = [" 12 ", "-3", "0", " 7"]
positive = [number for text in raw if (number := int(text)) > 0]
print(positive)  # [12, 7]
```

The assignment expression keeps parsing and the condition together, but can be less readable for beginners. A simple explicit loop is often clearer and avoids the walrus operator:

```python
positive = []
for text in raw:
    number = int(text)
    if number > 0:
        positive.append(number)
```

### Exercise 2 — Sort by score descending, then name ascending

```python
players = [
    {"name": "Zed", "score": 10},
    {"name": "Ari", "score": 10},
    {"name": "Bea", "score": 12},
]
```

**Solution:**

```python
ordered = sorted(players, key=lambda player: (-player["score"], player["name"]))
print([(p["name"], p["score"]) for p in ordered])
# [('Bea', 12), ('Ari', 10), ('Zed', 10)]
```

The numeric score is negated to reverse that component while name remains ascending. For arbitrary non-numeric score objects, use stable multi-pass sorting instead.

### Exercise 3 — Running totals

Replace a reduce-based running-total attempt with a standard-library iterator.

**Solution:**

```python
from itertools import accumulate
print(list(accumulate([5, -2, 4])))  # [5, 3, 7]
```

Use `accumulate` when all intermediate results are useful; use `sum` when only the final total is needed.

### Exercise 4 — Group by country

Rows may arrive in arbitrary country order. Return a mapping from country to rows.

**Solution:**

```python
from collections import defaultdict

def group_by_country(rows):
    result = defaultdict(list)
    for row in rows:
        result[row["country"]].append(row)
    return dict(result)
```

This avoids sorting just to group. Use `itertools.groupby` when input is already ordered by the grouping key or when adjacent grouping is specifically desired.

### Exercise 5 — Design a reliable model leaderboard

Requirements: lowest `loss` wins; ties break by shortest runtime, then `run_id`; records with missing loss must appear last.

**Solution:**

```python
runs = [
    {"run_id": "r-2", "loss": 0.2, "runtime_seconds": 12},
    {"run_id": "r-1", "loss": 0.1, "runtime_seconds": 15},
    {"run_id": "r-3", "loss": None, "runtime_seconds": 8},
]

def leaderboard_key(run):
    loss = run.get("loss")
    missing = loss is None
    return (
        missing,
        0.0 if missing else loss,
        run.get("runtime_seconds", float("inf")),
        run["run_id"],
    )

leaderboard = sorted(runs, key=leaderboard_key)
```

The first key component puts missing losses after present losses. The fallback numeric value is only a placeholder for missing rows; their first component differs. Validate that non-missing loss values have the intended numeric type and that NaN is either prohibited or normalized separately. `run_id` gives deterministic tie-breaking.

### Exercise 6 — Optimize only after defining semantics

A pipeline uses `sorted(records, key=lambda row: expensive_parse(row["timestamp"]))`. Propose a safe optimization.

**Solution:**

If the parsed timestamp is reused or expensive, parse it once into a normalized field before sorting, or build `(parsed_timestamp, original_record)` pairs and sort by the parsed value. Preserve stable tie behavior and do not mutate caller-owned records unless mutation is explicitly part of the API. Benchmark the complete pipeline—including the cost of creating the decorated records—before adopting the optimization.

## 9. Common mistakes and review checklist

- Treating `map`/`filter` as lists and reusing an exhausted iterator.
- Using `filter(None, xs)` when only `None` should be removed.
- Using `reduce` for plain addition, product, concatenation, or other operations with clearer built-ins.
- Forgetting that `map` over multiple inputs stops at the shortest input.
- Assuming `zip(strict=True)` validates lengths before any paired values have been consumed.
- Assigning the result of `list.sort()` to a variable.
- Sorting records by multiple fields with a key that does not fully express tie-breaking policy.
- Assuming `groupby` collects all equal keys regardless of adjacency.
- Sorting `None`, NaN, or mixed incomparable values without a documented normalization rule.
- Depending on set iteration order or input order that is not guaranteed by the source system.
- Putting side effects, mutation, I/O, or nondeterministic state access inside a key function.
- Using a heap-based top-K implementation without testing tie semantics against the intended reference behavior.
- Claiming a micro-optimization is faster without representative measurement.
- Using process-pool lambdas or nested functions that cannot be pickled reliably.

Before merging a transformation pipeline, ask:

1. Is each operation eager or lazy, and who consumes it?
2. Can the source be consumed only once? Is a materialized result required?
3. Is the transformation's error policy explicit for invalid or missing values?
4. Is ordering stable, deterministic, and documented for ties?
5. Are sort keys pure, deterministic, and safe for every possible input type?
6. Is memory use appropriate for expected data volume?
7. Does a test compare results with a simple reference implementation?
8. Have performance claims been measured on representative workloads?

## 10. Self-check

Try answering without looking back:

1. What does `map` return in Python 3, and when does it execute the function?
2. Why can a second `list(iterator)` be empty?
3. When is `filter(None, xs)` unsafe for data cleaning?
4. What does `reduce(fn, [])` do without an initial value?
5. When should `sum`, `math.prod`, `any`, `all`, or `accumulate` replace `reduce`?
6. What is the difference between `sorted(xs)` and `xs.sort()`?
7. How does sort stability help with ties, and what does it not guarantee?
8. How would you sort score descending and name ascending?
9. Why does `groupby` often require sorting first?
10. Why is NaN handling important for numeric rankings?
11. What does `zip(strict=True)` guarantee, and when can it raise?
12. Why can `itertools.tee` consume substantial memory?
13. What is the reference contract for `top_k` in this lesson?
14. Why is a top-level named function usually safer for process pools than a lambda?

## 11. Summary

Use transformations that state intent. Prefer comprehensions for inline mapping and filtering, built-ins for familiar aggregations, `itertools` for streaming iteration patterns, and `reduce` only when a fold is genuinely the clearest abstraction. Use `key=` for sorting and extrema; rely on stability deliberately, but add deterministic tie-breakers when source order is not a contract. Make missing values, NaNs, types, memory use, iterator consumption, and parallel serialization explicit. Test the public contract against a simple reference implementation.

## Completion criteria

You are ready to move on when you can:

- [ ] Explain the return types and consumption behavior of `map`, `filter`, and `reduce`.
- [ ] Rewrite an opaque `map`/`filter`/`reduce` chain into a clearer expression or loop.
- [ ] Select appropriate eager or lazy operations for a bounded-memory pipeline.
- [ ] Implement stable, multi-key sorting with explicit missing-value and tie rules.
- [ ] Explain the limits of `groupby`, `tee`, `zip(strict=True)`, and `top_k`.
- [ ] Run the tests and add at least one regression test for a real pipeline edge case.
- [ ] Measure any performance optimization rather than assuming it is faster.
