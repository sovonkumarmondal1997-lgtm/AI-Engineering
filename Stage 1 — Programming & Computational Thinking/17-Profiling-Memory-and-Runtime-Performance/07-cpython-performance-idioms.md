# CPython Performance Idioms

> **Stage:** 1 — Programming & Computational Thinking  
> **Module:** 1.17 — Profiling, Memory and Runtime Performance  
> **Lesson:** 07 of 09  
> **Target:** Python 3.12+; version-sensitive behavior is explicitly qualified  
> **Working rule:** correctness → clarity → algorithm → data layout → vectorization/native execution → micro-tuning.

---

## 1. Purpose and scope

This lesson is about choosing Python idioms deliberately after profiling has identified a real bottleneck. It is not a syntax survey and it is not a replacement for algorithm analysis, profiling, or the Stage 2 lessons on NumPy, Numba, pandas, Polars, and columnar processing.

The Module 1.17 roadmap places this lesson after:

1. `cProfile`, `pstats`, and flame graphs;
2. sampling profilers and production investigation;
3. `timeit` and benchmark pitfalls;
4. `tracemalloc` and memory-leak hunting;
5. Memray and allocation analysis;
6. reference cycles and GC tuning.

It precedes `ctypes`/`cffi` and C/Rust extension awareness. This sequence matters: use the evidence from the earlier lessons before deciding that a line of Python needs a micro-optimization. A shorter expression is not automatically faster, and a faster microbenchmark does not automatically make an ETL job faster.

### Prerequisites

You should already know:

- Big-O complexity and common data structures.
- Functions, iterators, generators, comprehensions, classes, and exceptions.
- Python object references, garbage collection, weak references, and `__slots__`.
- `time.perf_counter()`, repeatable microbenchmarks, and the difference between CPU time and wall-clock time.
- `cProfile`/`pstats`, sampling profiles, `tracemalloc`, and Memray at an introductory level.
- How to run tests and compare outputs on the shared `slowlog` log-analysis/ETL workload.

### Learning objectives

By the end, you should be able to:

- Choose built-ins and data structures based on semantics, clarity, asymptotic behavior, and measured cost.
- Explain the memory/performance trade-off among loops, comprehensions, generators, and copies.
- Design fair, result-equivalent benchmarks for common performance claims.
- Interpret CPython specialization and bytecode inspection without treating implementation details as universal guarantees.
- Recognize when the next step should be vectorization, native execution, process parallelism, a different runtime, or no change.
- Manage cache lifetime and invalidation risks.
- Document performance decisions in code review and test against explicit latency/throughput budgets.

---

## 2. Before optimizing: establish a baseline

Follow this order:

1. **Correctness:** write tests for outputs, edge cases, error behavior, ordering, and side effects.
2. **Clarity:** choose a readable implementation with a clear contract.
3. **Algorithm:** fix avoidable repeated work and complexity problems before changing syntax.
4. **Profile:** identify where time is actually spent using lesson 01/02 tools.
5. **Measure:** establish a representative baseline using lesson 03 principles and `pyperf` when appropriate.
6. **Change one thing:** keep the input, environment, and semantics fixed.
7. **Verify:** run correctness tests and compare the full workload, not only the edited line.
8. **Decide:** keep the change only if its benefit is repeatable and worth the readability, memory, and maintenance cost.

A 30% improvement in a helper that consumes 1% of the end-to-end runtime yields, at most, roughly a 0.3% total improvement under a simple Amdahl-style estimate. If a workload is I/O-bound, reducing a tiny Python loop may not change throughput at all.

### A performance claim has a scope

Write claims like:

> “On CPython 3.13.5, Linux x86-64, with 100,000 pre-built strings, this implementation reduced median function time by X in repeated `pyperf` runs. The full ETL job changed by Y, and peak RSS changed by Z.”

Do not write “comprehensions are always faster” or “local variables are always faster.” The measured effect depends on the interpreter/build, workload shape, input size, cache state, memory pressure, and the surrounding program.

---

## 3. Built-ins, comprehensions, and data structures

### 3.1 Prefer built-ins when they express the operation

Built-ins such as `sum`, `min`, `sorted`, `any`, and `str.join` communicate intent and often execute important loops in optimized implementation code. The best choice is still the one with the right semantics.

```python
values = [12, 4, 19, 7]

total = sum(values)
smallest = min(values)
ordered = sorted(values)
has_negative = any(value < 0 for value in values)
message = ", ".join(str(value) for value in ordered)

assert (total, smallest, ordered, has_negative) == (
    42, 4, [4, 7, 12, 19], False
)
assert message == "4, 7, 12, 19"
```

Trade-offs:

- `sum()` is suitable for numeric summation but is not a generic substitute for domain-specific aggregation (for example, floating-point accuracy may require `math.fsum`).
- `min()` and `max()` can consume iterators once; do not assume the input remains available.
- `sorted()` materializes a new list; it costs \(O(n \log n)\) time and \(O(n)\) additional references.
- `any()` and `all()` short-circuit, which can avoid work. A list comprehension used only to feed `any()` would unnecessarily materialize all results.
- `str.join()` needs to consume all the strings before it can return the final result. A generator expression avoids an explicit list in your source code, but CPython's `join()` implementation may materialize references to the yielded strings internally; do not treat `join(generator)` as a streaming, constant-memory operation. The final output string also requires memory proportional to output size.

### 3.2 Comprehension, generator, and manual loop

These forms can be semantically equivalent but have different memory and readability properties.

```python
def squares_comprehension(values):
    return [value * value for value in values]

def squares_loop(values):
    result = []
    for value in values:
        result.append(value * value)
    return result

def squares_generator(values):
    return (value * value for value in values)

sample = [1, 2, 3, 4]
assert squares_comprehension(sample) == squares_loop(sample) == [1, 4, 9, 16]
assert list(squares_generator(sample)) == [1, 4, 9, 16]
```

- **List comprehension:** concise, usually efficient for producing a list; memory grows with the result.
- **Manual loop:** useful when the body has branching, state changes, logging, or several operations. Do not rewrite a clear loop solely because a folklore benchmark says comprehensions win.
- **Generator expression:** computes values lazily and can reduce peak memory when the consumer streams through values once. It has its own generator/frame overhead and can be slower when all values are immediately consumed and the dataset is small.
- **Iterator lifetime:** a generator can hold references to its input and local variables until exhausted or released. Lazy does not mean free of retention.
- **Repeated consumption:** generators are one-shot. If the result is needed multiple times, materializing it may be simpler and faster overall.

For a streaming reduction, compare the correct memory profile:

```python
def sum_squares_list(values):
    return sum([value * value for value in values])

def sum_squares_generator(values):
    return sum(value * value for value in values)

sample = range(100)
assert sum_squares_list(sample) == sum_squares_generator(sample)
```

The generator version avoids the intermediate list. Whether this matters for a small input is a measurement question; for a very large input, peak-memory behavior may be the decisive criterion even if elapsed times are similar.

### 3.3 `map()` versus comprehensions

`map()` can be a good fit when applying an existing function, particularly a built-in implemented in C, such as `map(str, values)`. A comprehension is often clearer when the expression is more complex or includes a condition.

```python
values = range(20)
via_map = list(map(abs, range(-10, 10)))
via_comp = [abs(value) for value in range(-10, 10)]
assert via_map == via_comp
```

Do not benchmark `map()` against a comprehension that performs different work. If a comprehension calls a Python lambda but `map()` calls a C built-in, the comparison measures both iteration form and callable implementation.

### 3.4 String construction: `join()` and `+=`

When many pieces are already available, `separator.join(parts)` clearly expresses one final construction:

```python
parts = [f"event-{i}" for i in range(100)]
joined = "|".join(parts)
assert joined.count("|") == len(parts) - 1
```

Repeated immutable-string concatenation can copy accumulated content, potentially leading to quadratic work. CPython can optimize some local `str += piece` patterns under particular conditions, so “`+=` is always quadratic” is too broad. The optimization is an implementation detail and can be defeated by aliases, container storage, or different expression shapes.

Use `join()` for a collection of pieces. For incremental construction, a list of fragments plus one `join()` is often clear. For file output, write chunks to a buffered file instead of assembling a huge final string when the consumer can stream.

```python
def build_with_plus(parts):
    result = ""
    for part in parts:
        result += part
    return result

def build_with_join(parts):
    return "".join(parts)

parts = ["abc", "def", "ghi"]
assert build_with_plus(parts) == build_with_join(parts) == "abcdefghi"
```

This pair is suitable for a benchmark only if `parts` is built before timing and both functions receive the same input. Also test different piece counts and piece lengths. Tiny strings and a short list may conceal differences; modern CPython's optimization behavior can make simplistic results misleading.

### 3.5 Membership: list versus set/dict

A list scan is \(O(n)\) in the average case; a set or dictionary generally provides expected \(O(1)\) membership, subject to hashing, collisions, and key costs. But building a set costs time and memory.

```python
def list_membership(keys, probes):
    return [probe in keys for probe in probes]

def set_membership(keys, probes):
    lookup = set(keys)
    return [probe in lookup for probe in probes]

keys = list(range(100))
probes = [0, 50, 99, 101]
assert list_membership(keys, probes) == set_membership(keys, probes)
```

Decision points:

- If a lookup structure is reused for many probes, the build cost can amortize well.
- If there are only one or two probes, constructing a set may cost more than scanning the list.
- Sets require hashable keys and use additional memory.
- A dictionary is suitable when each key maps to a value; a set is suitable for membership and uniqueness.
- Preserve ordering requirements explicitly. A set is not a replacement for an ordered sequence when duplicates or positional semantics matter.

### 3.6 `dict.get`, `setdefault`, and `defaultdict`

Use these APIs to make intent clear, but understand eager evaluation and mutation.

```python
counts = {}
for category in ("auth", "search", "auth", "other", "auth"):
    counts[category] = counts.get(category, 0) + 1
assert counts == {"auth": 3, "search": 1, "other": 1}
```

`dict.get(key, default)` does not insert a missing key. The default expression is evaluated before the call:

```python
def expensive_default():
    print("computed")
    return []

mapping = {"present": [1]}
value = mapping.get("present", expensive_default())  # expensive_default still runs
```

For grouping, `setdefault` can be concise but its default expression is also evaluated every time:

```python
groups = {}
for key, value in [("a", 1), ("a", 2), ("b", 3)]:
    groups.setdefault(key, []).append(value)
assert groups == {"a": [1, 2], "b": [3]}
```

`defaultdict(list)` calls the factory only when a missing key is accessed with `[]`:

```python
from collections import defaultdict

groups = defaultdict(list)
for key, value in [("a", 1), ("a", 2), ("b", 3)]:
    groups[key].append(value)
assert dict(groups) == {"a": [1, 2], "b": [3]}
```

Trade-offs:

- `defaultdict[key]` creates a missing entry; `get()` does not invoke the factory.
- `setdefault(key, [])` creates a new list expression even when the key already exists.
- `defaultdict` may be less suitable when a missing key should be an error or when read access must not mutate the mapping.
- Benchmark the real operation, including whether the dictionary already exists and whether keys repeat.

### 3.7 `deque` for queues

A list is excellent for append-at-end and indexed access, but repeatedly removing the first element with `pop(0)` shifts remaining elements. `collections.deque` supports efficient append/pop at both ends.

```python
from collections import deque

def drain_list(items):
    queue = list(items)
    result = []
    while queue:
        result.append(queue.pop(0))
    return result

def drain_deque(items):
    queue = deque(items)
    result = []
    while queue:
        result.append(queue.popleft())
    return result

sample = range(100)
assert drain_list(sample) == drain_deque(sample)
```

This example includes queue construction and draining. It illustrates why algorithm/data structure choice can dominate micro-tuning. Do not conclude that `deque` is faster for every list workload: indexed access in the middle is not its strength, and list append/pop at the end is efficient.

### 3.8 Local variables and attribute/global lookups

A local alias can reduce repeated global or attribute lookup in some hot loops. Modern CPython specializes many operations, so the gain is not guaranteed and may be too small to matter.

```python
import math

def roots_global(values):
    return [math.sqrt(value) for value in values]

def roots_local(values):
    sqrt = math.sqrt
    return [sqrt(value) for value in values]

values = [float(i) for i in range(100)]
assert roots_global(values) == roots_local(values)
```

Benchmark the whole function. The local alias adds setup work, and the comprehension, list allocation, and `sqrt` call may dominate. Use aliases when they improve clarity or when a measured hot loop benefits; do not litter code with aliases based on unverified folklore.

---

## 4. CPython's specializing adaptive interpreter

### 4.1 What changed in Python 3.11+

CPython 3.11 introduced an adaptive specializing interpreter (PEP 659). Some bytecode instructions can specialize based on observed runtime types and values, replacing a general operation with a faster specialized form while assumptions remain valid. The interpreter can adapt when observed behavior changes.

Consequences:

- Repeated operations on stable types can become faster after warm-up.
- Highly variable types at one operation site can prevent a specialization from remaining effective or trigger deoptimization.
- Warm-up and steady-state measurements can differ.
- A bytecode listing may change with Python version and after execution; opcode names are not a language-level performance contract.
- Specialization does not remove the need for algorithm choice, data layout, or end-to-end profiling.

“Type-stable” means that hot operations repeatedly see compatible operand types and shapes; it does **not** mean Python code must add type annotations everywhere. An annotation alone generally does not enforce runtime types or guarantee specialization.

### 4.2 Use `dis` as supporting evidence

```python
import dis

def total(values):
    result = 0
    for value in values:
        result += value
    return result

dis.dis(total)
```

For CPython versions that support adaptive output, `dis.dis(total, adaptive=True, show_caches=True)` can expose specialized instructions and inline-cache state after warm-up. Check the `dis` documentation for the exact Python version; options and output vary.

Do not write tests that assert a particular opcode name. Use disassembly to form a hypothesis, then benchmark a representative workload. Bytecode does not show the cost of all C functions, memory allocation, cache misses, I/O, scheduling, or native-library work.

### 4.3 Function-call overhead and inlining

Python function calls have a cost, but the cost depends on Python version, call shape, and what the function does. CPython 3.11 reduced overhead in several call paths; that does not make calls free.

Inlining can help when a tiny helper is called millions of times in a profiled hot loop. It can also make code harder to test, duplicate logic, increase maintenance cost, and reduce clarity. Compare:

```python
def normalize(value):
    return value.strip().lower()

def normalized_values(values):
    return [normalize(value) for value in values]
```

with a carefully equivalent inlined implementation only after profiling shows the call boundary matters. Keep normalization semantics identical for Unicode, whitespace, exceptions, and `None` handling. Do not inline a helper merely because it is short.

---

## 5. Exceptions: EAFP versus LBYL

- **EAFP** (“easier to ask forgiveness than permission”) attempts an operation and handles the expected exception.
- **LBYL** (“look before you leap”) checks a condition before attempting the operation.

Choose based on semantics, race conditions, and failure frequency—not style slogans.

```python
def parse_int_eafp(text):
    try:
        return int(text)
    except ValueError:
        return None

def parse_int_lbyl(text):
    stripped = text.strip()
    if stripped and stripped.lstrip("+-").isdigit():
        return int(stripped)
    return None

for text in ("12", "-4", "bad", "", " 7 "):
    # This assertion covers only the listed sample inputs, not int()'s full grammar.
    assert parse_int_eafp(text) == (int(text) if text.strip() and text.strip().lstrip("+-").isdigit() else None)

# Demonstrate why this hand-written LBYL predicate is not generally equivalent:
assert parse_int_eafp("1_000") == 1000
assert parse_int_lbyl("1_000") is None
```

This example illustrates a crucial fairness point: the LBYL predicate must match the exact accepted input grammar before the functions can be treated as equivalent. For production numeric parsing, the `int()` parser may accept forms that a naive `isdigit()` check rejects (for example, underscores in integer literals are accepted by `int()` in supported forms). A benchmark that quietly changes accepted inputs is not a valid comparison.

For dictionary lookup, EAFP can be reasonable when missing keys are rare; LBYL (`if key in mapping`) can be reasonable when a missing key is common or the value is needed only conditionally. But `if key in mapping: value = mapping[key]` usually performs two lookups; `try: value = mapping[key] except KeyError` performs one lookup on the success path. For mutable/shared state, check-then-act can have race windows unless synchronization protects the operation.

Exception handling has low overhead on the normal path in modern CPython compared with older implementations, but raising and handling an exception is still relatively expensive. Measure realistic success/failure ratios. Never use exceptions as an unmeasured loop-control trick.

---

## 6. Caching: `cache`, `lru_cache`, and lifecycle

### 6.1 When memoization helps

`functools.cache` and `functools.lru_cache` can avoid recomputing an expensive, deterministic function for repeated hashable arguments.

```python
from functools import lru_cache

@lru_cache(maxsize=256)
def normalize_code(code: str) -> str:
    return code.strip().upper()

assert normalize_code(" ab ") == "AB"
assert normalize_code("AB") == "AB"
print(normalize_code.cache_info())
```

- `@cache` is an unbounded dictionary-backed cache (equivalent in intent to `lru_cache(maxsize=None)`).
- `@lru_cache(maxsize=N)` evicts least-recently-used entries after the bound is reached.
- Arguments must be hashable; keyword argument order can affect cache keys.
- Cache entries retain arguments and return values until eviction or `cache_clear()`.
- A function whose result depends on time, locale, current user, mutable external state, database contents, or permissions may be unsafe to cache unless those dependencies are included in the key or invalidation is explicit.
- The cache is coherent across threads, but concurrent calls for the same missing key may compute the value more than once before the first result is cached. A cache is not automatically a single-flight/stampede-prevention mechanism.

### 6.2 Cache invalidation and stampedes

A cache must define:

- **Key:** which inputs and versions determine the result?
- **Lifetime:** when does a result become stale?
- **Invalidation:** who clears it when source data changes?
- **Capacity:** what bounds memory use?
- **Concurrency:** what happens when many callers miss simultaneously?
- **Failure policy:** are exceptions cached? `lru_cache` does not cache a raised exception as a successful result.
- **Observability:** hit/miss ratio, eviction count where available, entry count, compute latency, and memory.

For expensive remote calls, use a TTL/versioned key, explicit invalidation, request coalescing/single-flight where appropriate, and bounded concurrency. External caches such as Redis introduce network latency, serialization, availability, and consistency trade-offs; they are not automatically faster than local computation.

### 6.3 Bound methods and instance retention

Decorating an instance method with an unbounded cache can keep `self` alive because the instance participates in the cache key. Use bounded caches, per-instance storage with a clear lifecycle, explicit cache clearing, or a cache design that does not retain instances unexpectedly. Add weak-reference regression tests for lifecycle-sensitive objects.

---

## 7. `__slots__` and object layout

By default, many Python instances have an instance dictionary, which allows dynamic attributes but adds memory overhead. `__slots__` can reduce per-instance overhead for classes with many instances and a fixed attribute set.

```python
class PlainPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class SlottedPoint:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y

points_a = [PlainPoint(i, i + 1) for i in range(3)]
points_b = [SlottedPoint(i, i + 1) for i in range(3)]
assert [(p.x, p.y) for p in points_a] == [(p.x, p.y) for p in points_b]
```

Trade-offs:

- `__slots__` can save memory at scale, but the savings depend on class layout, inheritance, Python version, and object count.
- It does not automatically make attribute access faster in every workload.
- Dynamic attributes are unavailable unless a `__dict__` slot is included.
- Weak references require `__weakref__` in slots when the class hierarchy otherwise does not provide it.
- Multiple inheritance and slotted base classes require careful design.
- `sys.getsizeof(instance)` is shallow and can omit separately allocated referents. Measure representative aggregate memory, not only a single object's shallow size.

Use `__slots__` for a justified object-layout need, not as a default decoration for every class.

---

## 8. Copies, iterators, views, and `memoryview`

### 8.1 Avoid unnecessary copies

Common sources of extra memory and time include:

- `list(iterator)` when the consumer can stream;
- repeated list slicing inside a loop;
- copying large dictionaries before every read;
- repeated string/bytes conversions;
- materializing intermediate collections used only once;
- retaining both source and transformed data longer than necessary.

A slice of a list creates a new list of references. A slice of a `memoryview` generally creates another view over the same buffer, not a copy of the underlying bytes. An array library may use views for some indexing operations and copies for others; verify the specific operation's contract.

### 8.2 Iterator versus materialized list

```python
def total_materialized(values):
    return sum(list(values))

def total_streamed(values):
    return sum(values)

sample = range(100)
assert total_materialized(sample) == total_streamed(sample)
```

For `range(100)`, the difference may be too small to matter. For a large input, the materialized list adds memory and allocation pressure. On the other hand, if the values must be iterated repeatedly, building a reusable list once may be cheaper than recomputing a generator.

### 8.3 `memoryview`: share a bytes-like buffer

```python
payload = bytearray(b"abcdefgh")
view = memoryview(payload)
middle = view[2:5]
assert bytes(middle) == b"cde"

middle[0] = ord("X")
assert payload == bytearray(b"abXdefgh")
```

`memoryview` supports buffer-protocol objects and can expose slices without copying the underlying data. But it adds lifetime and mutability considerations:

- The exporter must stay alive while the view is used.
- A view may prevent resizing a mutable exporter such as `bytearray` while the view exists.
- Read-only versus writable behavior depends on the exporter.
- `bytes(view)` materializes a copy.
- A view is useful only when the consumer can operate on the buffer without forcing a copy immediately afterward.

For data engineering workloads, streaming, chunking, and buffer reuse can be more valuable than saving a few Python-level lookups.

---

## 9. Sorting, top-k, and sorted lookup

### 9.1 `sorted(key=...)` versus `cmp_to_key`

Prefer a `key` function when the data can be mapped to a sortable key. Python evaluates the key function once per item for a sort.

```python
from functools import cmp_to_key

rows = [
    {"name": "b", "score": 9},
    {"name": "a", "score": 9},
    {"name": "c", "score": 4},
]

by_key = sorted(rows, key=lambda row: (row["score"], row["name"]))

def compare_rows(left, right):
    left_key = (left["score"], left["name"])
    right_key = (right["score"], right["name"])
    return (left_key > right_key) - (left_key < right_key)

by_comparator = sorted(rows, key=cmp_to_key(compare_rows))
assert by_key == by_comparator
```

A comparator may be needed for a legacy ordering contract or specialized pairwise comparison, but it can call Python code many times. A key is usually clearer and avoids repeatedly recomputing the ordering value. Confirm semantics, especially tie handling and stability.

### 9.2 `heapq.nsmallest` / `nlargest` versus full sorting

If only a small top-k is needed, a heap can avoid sorting the entire input. The trade-off depends on k relative to n and on key/comparison cost.

```python
import heapq

values = [17, 2, 44, 8, 3, 29, 1]
k = 3
assert heapq.nsmallest(k, values) == sorted(values)[:k]
assert heapq.nlargest(k, values) == sorted(values, reverse=True)[:k]
```

- Full sort: \(O(n \log n)\), materializes a sorted result.
- Top-k heap strategy: often around \(O(n \log k)\), plus output; for large k, a full sort can be competitive.
- `heapq.nsmallest(1, items)` is often equivalent in purpose to `min(items)`, and `nlargest(1, items)` to `max(items)`.
- Benchmark across multiple n and k ratios. The best strategy can change with input size and implementation constants.

### 9.3 `bisect` for sorted sequences

`bisect` finds insertion points in a sorted list in \(O(\log n)\) comparisons. Inserting into a Python list still shifts elements and is \(O(n)\), so repeated insertions may be expensive.

```python
from bisect import bisect_left, insort

values = [10, 20, 30, 40]
index = bisect_left(values, 25)
assert index == 2
insort(values, 25)
assert values == [10, 20, 25, 30, 40]
```

Use it for repeated lookups into a sequence that is already sorted or updated infrequently. For frequent updates, consider a different data structure or batch-sort after collecting data. Keep the sequence sorted at all times; binary search on unsorted data is incorrect.

---

## 10. Regex, string operations, and I/O

### 10.1 Compile repeated regular expressions

```python
import re

PATTERN = re.compile(r"^ERR-(\d+):\s*(.*)$")

def parse_compiled(line):
    match = PATTERN.match(line)
    return None if match is None else (int(match.group(1)), match.group(2))

def parse_module_cached(line):
    match = re.match(r"^ERR-(\d+):\s*(.*)$", line)
    return None if match is None else (int(match.group(1)), match.group(2))

lines = ["ERR-12: failed", "OK", "ERR-7: timeout"]
assert [parse_compiled(x) for x in lines] == [parse_module_cached(x) for x in lines]
```

The `re` module caches recent patterns, so repeated `re.match(pattern_string, ...)` is not necessarily recompiling from scratch each time. Explicit compilation communicates reuse and can avoid repeated pattern lookup/dispatch, but its gain depends on the workload and cache state. Measure before claiming a win.

### 10.2 String methods versus regex

For simple literal transformations or prefix checks, built-in string methods may be clearer and avoid regex-engine overhead. For complex patterns, regex can be the correct and maintainable tool. Do not replace a correct parser with a pile of fragile string operations for a tiny unmeasured gain.

- `startswith()` / `endswith()` for prefix/suffix checks.
- `partition()` for splitting once at a delimiter.
- `split()` for simple delimiter-based parsing.
- `translate()` for bulk character mapping/deletion.
- `bytes` operations for byte-oriented protocols where encoding semantics are explicit.

Unicode normalization, locale, escaping, and malformed-input behavior are correctness concerns, not merely performance details.

### 10.3 Buffered I/O, larger chunks, and `readinto`

Python file objects are buffered by default. Larger chunks can reduce per-call overhead when processing large inputs, but may increase memory and latency before output is emitted. The standard `csv` module already uses optimized implementation code for much of its parsing; do not replace it with a hand-written parser without evidence and equivalent quoting/newline semantics.

```python
def line_count(path):
    with open(path, "rt", encoding="utf-8", newline="") as handle:
        return sum(1 for _ in handle)

def chunk_count(path, chunk_size=1024 * 1024):
    # Count newline bytes only; this is not a general CSV record counter.
    count = 0
    with open(path, "rb") as handle:
        while chunk := handle.read(chunk_size):
            count += chunk.count(b"\n")
    return count
```

The two functions above are intentionally **not** equivalent for arbitrary CSV or text data: newline counting can differ for final lines without a newline and CSV fields containing embedded newlines. Use this only to discuss chunk I/O mechanics, not as a valid benchmark of the same parser.

For binary protocols or fixed byte layouts, `readinto(buffer)` can reuse an allocated writable buffer and avoid allocating a new bytes object for each read. Ensure the consumer handles partial reads and only processes the number of bytes actually read.

### 10.4 Chunked processing

Chunking controls peak memory and often improves throughput by bounding intermediate state. It can also increase overhead if chunks are too small or change semantics if state must cross chunk boundaries.

A fair comparison must preserve:
- output order and row counts;
- error handling and malformed-record behavior;
- boundary state (e.g., a CSV row, UTF-8 code point, or record can cross a byte-chunk boundary);
- conversion and serialization costs;
- total memory and end-to-end time, not just parser loop time.

---

## 11. Reproducible idiom experiments with `pyperf`

Install `pyperf` in the project's development environment:

```bash
python -m pip install pyperf
python -m pip show pyperf
```

Use the same interpreter, machine, input data, and dependencies for each comparison. Run on an otherwise idle system; use the tool's metadata and stability checks. Do not force CPU governor or privileged system settings on a production machine just to benchmark.

The script below benchmarks pairs of implementations on identical pre-built inputs and checks result equality before timing. It intentionally reports no pre-filled benchmark numbers. It uses `pyperf.Runner`, which runs multiple worker processes and supports saved JSON output for later comparison.

Save it as `idiom_benchmarks.py`:

```python
import heapq
import math
import re
import sys
import pyperf


# Input fixtures are prepared before timing. Output/result construction remains
# inside each benchmark when it is part of the operation being compared.
N = 20_000
INTS = list(range(N))
REVERSED = list(reversed(INTS))
STRINGS = [f"item-{i:06d}" for i in range(2_000)]
PARTS = ["abcde" for _ in range(2_000)]
PROBES = list(range(0, N, 17))
LOOKUP_SET = set(INTS)
ROWS = [{"key": i % 97, "value": i} for i in range(2_000)]
SORTED_VALUES = list(range(N))
QUEUE_INTS = list(range(2_000))  # keep the O(n^2) pop(0) demonstration bounded
PATTERN_TEXT = [f"ERR-{i}: issue {i}" for i in range(200)]
REGEX = re.compile(r"^ERR-(\d+):\s*(.*)$")


# 1. += vs join: both receive the same prebuilt fragments.
def plus_strings():
    result = ""
    for part in PARTS:
        result += part
    return result

def join_strings():
    return "".join(PARTS)


# 2. comprehension vs map with the same built-in callable.
def squares_comp():
    return [abs(value) for value in REVERSED]

def squares_map():
    return list(map(abs, REVERSED))


# 3. dict literal vs dict() constructor with equivalent mapping.
def make_dict_literal():
    return {}

def make_dict_constructor():
    return dict()

def make_nonempty_dict_literal():
    return {"a": 1, "b": 2, "c": 3}

def make_nonempty_dict_constructor():
    return dict(a=1, b=2, c=3)


# 4. EAFP vs LBYL for dictionary membership; both return the same count.
MAPPING = {str(i): i for i in range(1000)}
MAPPING_PROBES = [str(i) for i in range(0, 1200, 3)]

def dict_eafp():
    found = 0
    for key in MAPPING_PROBES:
        try:
            MAPPING[key]
        except KeyError:
            pass
        else:
            found += 1
    return found

def dict_lbyl():
    found = 0
    for key in MAPPING_PROBES:
        if key in MAPPING:
            MAPPING[key]
            found += 1
    return found


# 5. f-string vs str.format for a fixed formatting contract.
def format_fstring():
    return [f"{row['key']}:{row['value']}" for row in ROWS]

def format_format():
    return ["{}:{}".format(row["key"], row["value"]) for row in ROWS]


# 6. Global module attribute vs local alias.
def sqrt_global():
    return [math.sqrt(value) for value in INTS]

def sqrt_local():
    sqrt = math.sqrt
    return [sqrt(value) for value in INTS]


# 7. list comprehension vs generator consumed by sum.
def squares_sum_list():
    return sum([value * value for value in INTS])

def squares_sum_generator():
    return sum(value * value for value in INTS)


# 8. __slots__: compare attribute-access throughput and object construction.
class PlainPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class SlottedPoint:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y

POINTS_PLAIN = [PlainPoint(i, i + 1) for i in range(2_000)]
POINTS_SLOTTED = [SlottedPoint(i, i + 1) for i in range(2_000)]

def sum_plain_points():
    return sum(point.x + point.y for point in POINTS_PLAIN)

def sum_slotted_points():
    return sum(point.x + point.y for point in POINTS_SLOTTED)

def construct_plain_points():
    return [PlainPoint(i, i + 1) for i in range(2_000)]

def construct_slotted_points():
    return [SlottedPoint(i, i + 1) for i in range(2_000)]


# 9. full sort prefix vs heap top-k.
K = 25

def sort_top_k():
    return sorted(REVERSED)[:K]

def heap_top_k():
    return heapq.nsmallest(K, REVERSED)


# 10. compiled regex vs module-level convenience call.
def regex_compiled():
    result = []
    for text in PATTERN_TEXT:
        match = REGEX.match(text)
        result.append(None if match is None else (int(match.group(1)), match.group(2)))
    return result

def regex_convenience():
    result = []
    for text in PATTERN_TEXT:
        match = re.match(r"^ERR-(\d+):\s*(.*)$", text)
        result.append(None if match is None else (int(match.group(1)), match.group(2)))
    return result


# 11. list pop(0) vs deque.popleft includes queue creation and drain.
from collections import deque

def queue_list():
    queue = list(QUEUE_INTS)
    result = []
    while queue:
        result.append(queue.pop(0))
    return result

def queue_deque():
    queue = deque(QUEUE_INTS)
    result = []
    while queue:
        result.append(queue.popleft())
    return result


PAIRS = [
    ("strings_plus", plus_strings, join_strings),
    ("comprehension_map", squares_comp, squares_map),
    ("empty_dict_literal_constructor", make_dict_literal, make_dict_constructor),
    ("nonempty_dict_literal_constructor", make_nonempty_dict_literal, make_nonempty_dict_constructor),
    ("dict_eafp_lbyl", dict_eafp, dict_lbyl),
    ("format_fstring_format", format_fstring, format_format),
    ("sqrt_global_local", sqrt_global, sqrt_local),
    ("sum_list_generator", squares_sum_list, squares_sum_generator),
    ("slots_attribute_access", sum_plain_points, sum_slotted_points),
    ("slots_construction", construct_plain_points, construct_slotted_points),
    ("topk_sort_heap", sort_top_k, heap_top_k),
    ("regex_compiled_convenience", regex_compiled, regex_convenience),
    ("queue_list_deque", queue_list, queue_deque),
]


def main():
    # Correctness check happens before any measurements.
    for name, left, right in PAIRS:
        left_result = left()
        right_result = right()
        # Distinct point instances compare by identity unless equality is defined;
        # compare their public values for the construction-only slots pair.
        if name == "slots_construction":
            left_result = [(point.x, point.y) for point in left_result]
            right_result = [(point.x, point.y) for point in right_result]
        if left_result != right_result:
            raise AssertionError(f"result mismatch in {name}")

    print("Correctness checks passed:", len(PAIRS), "benchmark pairs")
    print("Python:", sys.version.replace("\n", " "))
    runner = pyperf.Runner()
    for name, left, right in PAIRS:
        runner.bench_func(name + "_A", left)
        runner.bench_func(name + "_B", right)


if __name__ == "__main__":
    main()
```

### Run and compare

```bash
python idiom_benchmarks.py --help
python idiom_benchmarks.py -o idioms.json
python -m pyperf check idioms.json
python -m pyperf stats idioms.json
python -m pyperf show idioms.json --metadata
```

The script writes one JSON suite containing separately named A/B benchmarks. Each `bench_func` is calibrated and sampled by pyperf, but the A and B cases still run sequentially and are not a randomized, tightly paired experiment. Inspect distributions and metadata; do not simply compare displayed means. For stronger conclusions, run a focused pair in separate before/after suites and use `pyperf compare_to`, repeat in reversed order or on a fresh process, and verify the effect persists. Keep the same machine, interpreter build, inputs, and dependency versions.

**Important:** the script's `queue_list` deliberately uses a quadratic algorithm (`pop(0)`), so it is a data-structure/complexity demonstration rather than a fair tiny-operation comparison. It uses a bounded 2,000-item fixture and includes queue construction, draining, and result construction in both variants. Increase the size only in a dedicated run if you need to examine scaling. The EAFP/LBYL pair tests dictionary hits and misses in a particular ratio; change that ratio to match production. The benchmark results are not known in advance and are not included here.

### Benchmarks to treat as hypotheses

| Comparison | Fairness requirement | Qualitative expectation, not a guaranteed result |
| --- | --- | --- |
| `+=` vs `join` | Pre-build fragments; same piece count/length; compare several sizes. | `join` is often attractive for many fragments; CPython may optimize some `+=` shapes. |
| comprehension vs `map` | Same callable and same result; separate C built-ins from Python functions. | Differences are often workload- and callable-dependent. |
| `{...}` vs `dict(...)` | Same resulting mapping and equivalent value expressions; note that literal and keyword-argument construction have different call/argument mechanics. | A literal may be cheaper for fixed keys, but this comparison measures the full syntax paths, not an isolated constructor primitive. |
| EAFP vs LBYL | Same success/miss ratio and exception semantics. | EAFP may suit mostly-successful dictionary access; frequent exceptions change cost. |
| f-string vs `format` | Same format specification, conversions, and values. | f-strings are often competitive for inline formatting, but not universal. |
| global vs local alias | Same input, return value, and setup cost. | A local alias may help in a tight loop; specialization can narrow the gap. |
| list vs generator | Same result; include list construction when it is part of the contract. | Generator often lowers peak intermediate memory; list may be faster for some bounded workloads. |
| `__slots__` | Compare aggregate object memory and realistic attribute use, not only shallow size. | Slots can save memory for many instances; access speed is not guaranteed to improve. |
| top-k heap vs sort | Same tie semantics and k/n ratios. | Heap can help when k is small relative to n; full sort may win when k is large. |
| compiled regex vs convenience call | Same pattern, flags, text, and result; account for regex module's cache. | Explicit compilation may help reuse, but the convenience API already caches patterns. |

### Why this suite is not the whole story

A microbenchmark does not measure end-to-end I/O, serialization, allocation pressure, cache misses, concurrent load, or operational memory limits unless those are included. It may also be affected by CPU frequency scaling, background processes, thermal throttling, the adaptive interpreter, PGO/LTO build flags, and free-threaded build behavior.

For memory trade-offs, run a separate process-level memory experiment or use the tools from lessons 04–05. Do not add `tracemalloc` to the timed path and then treat the result as normal production speed; instrumentation has overhead.

---

## 12. Memory-oriented idioms and realistic measurement

Performance has at least two dimensions: time and memory. An implementation that saves time but doubles peak RSS can be a regression if the ETL job runs close to its container limit.

Measure:
- total runtime and throughput;
- peak RSS or container memory;
- object/allocation behavior where relevant;
- input/output equivalence;
- memory retained after the workload;
- conversion and cleanup costs.

`sys.getsizeof()` is shallow. `tracemalloc` traces Python allocations, not every native allocation or RSS component. Memray can help when native allocation stacks matter. Use the right tool for the question rather than assuming one number describes “memory.”

### Data-layout choices

- Use `array.array` or packed bytes for homogeneous primitive values when their type/range semantics fit.
- Use NumPy/columnar libraries when bulk numeric operations can execute in native loops.
- Use `__slots__` for large numbers of fixed-shape objects when measurements show per-instance overhead matters.
- Use iterators and bounded chunks when the consumer can stream.
- Avoid converting large buffers to Python lists only to convert them back into arrays again.

Stage 2 covers NumPy vectorization, views/copies, Arrow, pandas, Polars, and streaming engines. This lesson should teach when to escalate, not duplicate their implementation tutorials.

---

## 13. Vectorization and native execution: decision points

When a Python loop dominates a profile, ask in this order:

1. Can a built-in or library operation perform the whole task?
2. Can the data be represented in a more efficient layout?
3. Can the loop be expressed as a NumPy array operation or a pandas/Polars expression?
4. Is Numba/Cython or an existing native library appropriate?
5. Only after those options, is pure-Python micro-tuning still worthwhile?

Vectorization can reduce Python-level loop overhead and improve locality, but it may allocate intermediate arrays, change dtype/overflow semantics, or use more memory. A native call can be slower if the program converts a large Python list on every call. Keep data in the optimized representation across multiple operations where possible.

Do not write C/Rust or call FFI simply because a loop is slow. Lessons 08–09 address native boundaries, packaging, and safety; Stage 2 covers numerical/data-engineering implementations.

---

## 14. Processes, serialization, shared memory, and free-threading

### 14.1 Processes

For CPU-bound pure-Python work on a conventional GIL-enabled build, processes can execute Python code in parallel across cores. But process parallelism adds:

- worker startup and lifecycle cost;
- pickling/unpickling or other data-transfer overhead;
- memory duplication and copy-on-write behavior;
- load balancing, chunk sizing, and failure/cancellation complexity;
- ordering and aggregation costs.

Benchmark the full pipeline, including input partitioning, serialization, worker work, result transfer, and combination. A speedup in the worker function may be erased by sending millions of small Python objects between processes.

Use `concurrent.futures.ProcessPoolExecutor` for a straightforward process pool; consider `multiprocessing.shared_memory` for large compatible buffers when the complexity is justified. Shared memory requires explicit ownership, synchronization, cleanup, and clear dtype/shape contracts. It is not a drop-in shared Python object graph.

### 14.2 Free-threaded CPython

An optional free-threaded CPython build became available in the Python 3.13 series. It can allow Python threads to run Python code in parallel without the traditional global interpreter lock, but it changes runtime overheads and extension compatibility constraints. It is not automatically faster for single-threaded code or every multi-threaded workload.

Benchmark on the exact build and dependency stack. Check whether native extensions support free-threaded execution and whether the workload is actually CPU-bound, thread-safe, and sufficiently coarse-grained. Record whether the GIL is enabled; do not compare a GIL build with a free-threaded build without recording the build and workload.

### 14.3 Chunk sizing

Small chunks increase scheduling and serialization overhead; large chunks can increase latency, peak memory, and straggler cost. Sweep a small range of chunk sizes using representative data, and measure throughput, tail latency, memory, and error/retry behavior. Do not pick a chunk size from one benchmark run.

---

## 15. JIT, PGO/LTO, and alternative runtimes

### 15.1 CPython JIT and build options

The roadmap calls out the experimental copy-and-patch JIT in Python 3.13+ and `PYTHON_JIT`. Availability and behavior are build- and release-specific. Treat it as an experiment, not a default production recommendation. Check the official documentation for the exact interpreter build and verify that the feature is enabled and applicable to your workload.

Profile-guided optimization (PGO) and link-time optimization (LTO) affect how CPython itself is built. A PGO/LTO-enabled interpreter can behave differently from a debug build or a custom build. Compare supported production builds under the same workload and record `sys.version`, `sys.implementation`, compiler/build information where available, and relevant environment flags.

### 15.2 PyPy and GraalPy

Alternative runtimes may speed up some long-running, pure-Python workloads through JIT compilation, but compatibility, C-extension support, startup, memory, and warm-up behavior differ. A workload dominated by NumPy or other native extensions may have a different outcome than a pure-Python loop.

Evaluate:
- dependency and extension compatibility;
- cold-start and warm steady-state performance;
- memory footprint and latency distribution;
- test coverage and production observability;
- operational packaging and deployment constraints.

Do not infer “PyPy is faster” or “CPython is faster” from one function. Benchmark the application and its dependencies.

---

## 16. Caching at multiple levels

| Cache type | Example | Strength | Main risk |
| --- | --- | --- | --- |
| In-process | Local dictionary or object memo | Very low access latency | Lifecycle, stale state, memory growth |
| Function-level | `functools.cache`, `lru_cache` | Simple for deterministic functions | Retained arguments/results, invalidation |
| Disk | `joblib.Memory`, `diskcache` | Can survive process restarts and cache expensive local results | Serialization, disk pressure, invalidation |
| External | Redis or another shared cache | Shared across workers | Network latency, availability, consistency, stampedes |

Before adding a cache, calculate the expected hit rate and cost avoided. If the underlying operation is cheap, key construction, hashing, serialization, and cache lookup can cost more than recomputation.

A cache review must answer:
- What exact inputs and source versions form the key?
- What event invalidates a value?
- Is the capacity bounded?
- What happens during a thundering herd or stampede?
- Can sensitive data be retained longer than intended?
- How will hits, misses, evictions, errors, latency, and memory be observed?
- Is the cached result safe to share if it is mutable?

For a stampede-prone key, options include per-key single-flight coordination, short-lived locks, stale-while-revalidate, jittered TTLs, or bounded concurrency. Each adds complexity and must be matched to consistency requirements.

---

## 17. Focused exercise: optimize the shared `slowlog` workload

Use the same slowlog log-analysis/ETL script used in lessons 01–06. Keep the input file and output contract fixed so the performance investigation remains comparable across the module.

### Task

1. Generate or select a representative log file with realistic line lengths, category distribution, malformed records, and enough rows to expose the bottleneck.
2. Run the correctness suite and record output rows, error counts, aggregation values, and ordering guarantees.
3. Capture a baseline end-to-end runtime and profile the program using the tools from lessons 01–02.
4. Select **one** hotspot supported by the profile. Examples might include repeated membership checks, repeated string processing, a materialized intermediate list, a queue implemented with front-removal, or repeated parsing. Do not assume any one of these is the actual bottleneck.
5. Form a hypothesis and implement a minimal change using an idiom from this lesson.
6. Add or update a regression test that proves output equivalence on valid, malformed, empty, and boundary inputs.
7. Benchmark the focused function with identical pre-built inputs using `pyperf` or the approved project benchmark harness.
8. Re-run the full workload and record total time, throughput, peak memory, and result equivalence.
9. Review the diff for readability, API semantics, and lifecycle changes.
10. Decide: keep, revert, or gather more evidence.

### Required report

```text
Workload and input version:
Python version/build, OS, CPU, dependencies:
Correctness tests and expected invariants:
Baseline end-to-end time / throughput / peak memory:
Profile evidence (function and cost):
Hypothesis:
Change and expected mechanism:
Focused benchmark setup and result distribution:
End-to-end result:
Output equivalence / error counts:
Memory and operational trade-offs:
Readability/maintenance trade-off:
Decision (keep / revert / inconclusive):
Rollback criteria:
```

A valid outcome is “no change.” If the measured benefit is smaller than noise, does not affect end-to-end time, increases memory beyond budget, or makes the code materially harder to maintain, do not keep it solely because a microbenchmark improved.

---

## 18. Common mistakes

- Optimizing a line before profiling the whole workload.
- Treating a benchmark's fastest run as the expected performance.
- Comparing different inputs or semantics.
- Comparing a comprehension with a Python lambda against `map()` with a C built-in and attributing all difference to syntax.
- Forgetting data-structure construction costs when comparing list and set membership.
- Assuming `+=` is always quadratic or always optimized.
- Using a generator when a reusable materialized result is needed.
- Using `get(key, expensive())` and assuming the default is lazy.
- Caching functions that depend on hidden mutable state.
- Adding an unbounded cache to a long-running worker.
- Assuming `__slots__` always improves speed or that `sys.getsizeof()` measures deep memory.
- Using `bisect` on unsorted input or expecting list insertion to be logarithmic.
- Assuming regex convenience calls always recompile the pattern from scratch.
- Counting newline bytes and assuming the result equals logical CSV record count.
- Ignoring process serialization and memory when evaluating parallel speedup.
- Assuming free-threaded Python, a JIT, or an alternative runtime is automatically faster.
- Treating bytecode as a language contract.
- Accepting a microbenchmark win that does not move the end-to-end objective.

---

## 19. Exercises

### Beginner

1. Rewrite a manual sum loop using `sum()`. State which input types and side effects would make the rewrite inappropriate.
2. Compare a list comprehension and generator expression for a large reduction. Measure both time and peak memory.
3. Build the same grouped dictionary with `setdefault` and `defaultdict`. Explain which API mutates on a missing-key read.
4. Compare `list.pop(0)` and `deque.popleft()` for several queue sizes. Include queue construction and result equality.
5. Compare repeated string `+=` and `join()` at several fragment counts and lengths.

### Intermediate

6. Compare global `math.sqrt` lookup with a local alias in a representative hot loop. Inspect `dis` output but base the decision on measurement.
7. Write an EAFP and an LBYL implementation with exactly the same accepted input grammar. Test success-heavy and failure-heavy data.
8. Add `lru_cache(maxsize=...)` to a pure expensive function. Measure hit rate and memory; prove that invalidation works.
9. Compare a normal class and a slotted class with many instances. Measure aggregate memory and confirm whether dynamic attributes/weakrefs are required.
10. Use `memoryview` to inspect and modify a `bytearray` slice without copying the underlying buffer. Explain the exporter lifetime and resize constraint.
11. Compare `sorted(key=...)`, `heapq.nsmallest`, and `bisect` for the operations they actually support; do not compare unrelated semantics.

### Advanced

12. Run the benchmark suite on two CPython minor versions and compare metadata, distributions, and results.
13. Test a type-stable hot loop against a type-variable version; use `dis` as supporting evidence and measure both after warm-up.
14. Compare process-pool chunk sizes while including serialization, result transfer, and aggregation.
15. Compare a pure-Python loop with an appropriate vectorized implementation in Stage 2. Include conversion costs and peak memory.
16. Design a cache stampede test with concurrent misses and propose an explicit single-flight or stale-while-revalidate policy.
17. Submit a performance code-review note for the slowlog change, including the evidence and rollback condition.

---

## 20. Self-check questions

1. Why do correctness and profiling precede micro-optimization?
2. When does a generator reduce memory, and when can a list be preferable?
3. Why is “`+=` is always quadratic” too broad for CPython?
4. Why can building a set be slower than a list scan for a small number of probes?
5. What is the difference between `dict.get`, `setdefault`, and `defaultdict` on a missing key?
6. What did CPython 3.11's specializing adaptive interpreter change, and why is specialization not a guarantee?
7. Why can `dis` help form a hypothesis but not prove a speedup?
8. When is EAFP a good choice, and what makes a benchmark comparing EAFP/LBYL unfair?
9. How can an unbounded `lru_cache` retain objects or grow memory?
10. What are the limitations of `__slots__` and `sys.getsizeof()`?
11. When is a heap preferable to sorting all input, and why does the ratio k/n matter?
12. Why might explicit regex compilation make little difference in a repeated `re.match()` benchmark?
13. What does `memoryview` avoid copying, and what lifetime/resize constraints does it introduce?
14. What costs can erase a process-parallel speedup?
15. What evidence is required before adopting a JIT, free-threaded build, PyPy, or GraalPy?
16. Why does a microbenchmark win not guarantee a measurable end-to-end improvement?
17. What information belongs in a performance code-review comment?
18. When should an optimization be reverted even if its microbenchmark is faster?

---

## 21. Performance code-review checklist

### Correctness and semantics
- [ ] Output values, ordering, errors, and side effects are preserved.
- [ ] Edge cases, malformed inputs, and empty inputs are tested.
- [ ] Iterator consumption and object lifetime are intentional.
- [ ] Cache key, invalidation, and mutable-result semantics are correct.

### Evidence
- [ ] A profile identifies the code as relevant to the objective.
- [ ] Baseline and changed versions use the same input and environment.
- [ ] The benchmark isolates the intended difference without changing semantics.
- [ ] Results include enough repetitions/distribution data to judge noise.
- [ ] The full workload is measured, not only the microbenchmark.
- [ ] Python version/build and hardware/software environment are recorded.

### Performance and resources
- [ ] Time, throughput, and peak memory are considered together.
- [ ] Data construction, conversion, serialization, and cleanup costs are included where relevant.
- [ ] Cache growth and invalidation are bounded and observable.
- [ ] Any concurrency change is safe and measured at realistic load.
- [ ] Latency percentiles and service-level objectives are checked.

### Maintainability and rollback
- [ ] The code is still readable and the benefit justifies the complexity.
- [ ] Non-obvious choices have a short comment linking to benchmark evidence.
- [ ] The change has a measurable acceptance criterion.
- [ ] A rollback path exists if performance, memory, or correctness regresses.
- [ ] Results are rechecked after Python/runtime upgrades.

---

## 22. Performance budgets and SLOs

A performance budget turns an optimization claim into a decision criterion. Define budgets at the level users experience:

- p50, p95, and p99 latency for request-oriented work;
- rows/records per second and total duration for batch work;
- peak RSS and container memory headroom;
- CPU time or cost per unit of data where useful;
- error rate, retry rate, and output correctness.

Avoid brittle CI assertions on a single absolute wall-clock time on noisy shared runners. Prefer stable dedicated runners, repeated measurements, stored baselines, relative regression tolerances justified by observed noise, and artifacts that preserve the benchmark metadata. Use functional regression tests separately from performance tests.

For a batch ETL job, an acceptance criterion might be:

> “For the fixed representative fixture, output and error counts remain identical; median end-to-end runtime does not regress by more than the agreed tolerance over repeated dedicated-runner trials; peak RSS remains below the memory budget.”

The actual threshold is a project decision and must be based on measured variability and operational requirements, not copied from this lesson.

---

## 23. References and version notes

- [Python built-in functions](https://docs.python.org/3/library/functions.html): `sum`, `min`, `sorted`, `any`, and related APIs.
- [Python data structures](https://docs.python.org/3/tutorial/datastructures.html): lists, sets, dictionaries, and idioms.
- [`functools`](https://docs.python.org/3/library/functools.html): `cache`, `lru_cache`, and related wrappers.
- [`collections`](https://docs.python.org/3/library/collections.html): `deque` and `defaultdict`.
- [`heapq`](https://docs.python.org/3/library/heapq.html) and [`bisect`](https://docs.python.org/3/library/bisect.html): top-k and sorted-sequence operations.
- [`memoryview`](https://docs.python.org/3/library/stdtypes.html#memory-views): buffer-protocol views.
- [`dis`](https://docs.python.org/3/library/dis.html): bytecode inspection and adaptive output options.
- [PEP 659 — Specializing Adaptive Interpreter](https://peps.python.org/pep-0659/): CPython 3.11 specialization background.
- [`pyperf` documentation](https://pyperf.readthedocs.io/en/stable/): benchmark design, metadata, stability checks, and result comparison.
- [What's New in Python 3.13 — experimental JIT](https://docs.python.org/3.13/whatsnew/3.13.html#an-experimental-just-in-time-jit-compiler): build flags and `PYTHON_JIT` behavior for that release.
- [PEP 703 — Making the GIL Optional](https://peps.python.org/pep-0703/): free-threaded CPython context.
- [Python performance FAQ](https://docs.python.org/3/faq/programming.html#performance): general performance guidance.

Python performance changes between minor versions and build configurations. Check the documentation for the interpreter you deploy, record the environment, and rerun benchmarks after upgrades.

---

## Final principle

Optimize the bottleneck you measured, preserve the program's contract, and evaluate the whole workload. A readable implementation with adequate performance is often the best production choice. A faster microbenchmark is evidence about one experiment—not a promise about every application.
