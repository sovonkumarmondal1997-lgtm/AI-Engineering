# Memory Allocator and Small-Object Optimizations

> **Target:** CPython 3.12–3.14. Examples use public Python APIs unless marked otherwise. Exact sizes, allocator thresholds, free-list behavior, RSS changes, and internal data structures depend on CPython release, build options, operating system, architecture, and allocator. Record `python --version` and `sys.version` when reproducing measurements. Never treat numeric outputs as cross-build contracts.

## Learning outcomes

By the end of this lesson, you should be able to:

1. Explain what `sys.getsizeof()` measures—and what it omits.
2. Distinguish identity from equality and explain integer caching, string interning, and singleton objects without relying on `is` for values.
3. Describe CPython's raw, Python-memory, and object-allocation layers, and explain how pymalloc arenas, pools, and blocks can create fragmentation.
4. Interpret list over-allocation, compact dictionaries/key sharing, Unicode representation, and relevant free-list behavior as implementation optimizations.
5. Use `tracemalloc`, `sys._debugmallocstats()` where available, `PYTHONMALLOC`, and external profilers to investigate memory.
6. Compare object-heavy Python representations with `__slots__`, `array`, NumPy, Arrow, and columnar layouts.
7. Explain immortal objects, cyclic garbage collection, large buffers, `memoryview`, native allocator interaction, and copy-on-write after `fork`.
8. Distinguish Python allocations, allocator-reserved memory, RSS, working set, page cache, and container memory limits.
9. Run a measurement-table exercise and an RSS/fragmentation experiment, state what each measurement does and does not establish, and answer all roadmap self-checks.

## Prerequisites

You should know the Python object model, references, lists/dictionaries/tuples, classes, garbage collection, basic process virtual memory, and how to run scripts. Earlier lessons on `__slots__`, profiling, and GC are useful context.

Recommended environment: CPython 3.12–3.14. If possible, compare a conventional GIL-enabled build with a free-threaded build, but do not assume both are installed. Optional tools: `psutil`, Memray, NumPy, and PyArrow. Core examples use the standard library.

## 1. Mental model: objects, allocations, and resident memory

```text
application data
  └── Python objects and references
        └── CPython object allocator / Python memory allocators
              └── system allocator and/or OS virtual-memory mappings
                    └── virtual pages resident in physical RAM (RSS)

Other contributors: native-extension allocations, thread stacks, code/shared
libraries, memory-mapped files, allocator metadata, page cache, runtime state.
```

These layers answer different questions:

- **Object size:** direct size reported for one object.
- **Live allocations:** what Python allocation tracing can attribute to currently traced allocations.
- **Allocator-reserved memory:** memory held for future reuse.
- **RSS:** pages currently resident for a process, including more than Python objects.
- **Container memory:** what the OS/cgroup accounts to the container; this can include page cache and other contributors depending on metric and cgroup version.

A drop in live Python objects need not immediately lower RSS. The allocator may keep memory for reuse; pages may remain resident; native libraries may hold allocations; fragmentation may prevent whole regions from being returned.

**Real-world example:** an API worker parses a million JSON records. The records are released after a request, but RSS stays high. That alone does not prove a leak: freed blocks may be retained by pymalloc or the system allocator. Conversely, stable RSS does not prove there is no leak. Measure object reachability, traced allocations, allocator behavior, and process memory separately.

## 2. Object headers and `sys.getsizeof()`

### 2.1 What an object contains

Conceptually, a CPython object has runtime metadata that identifies its type and supports reference management. Many dynamically allocated objects begin with a `PyObject`-like header; variable-sized objects use a variable-size header conceptually associated with `PyVarObject`. Not every runtime object is an ordinary per-instance heap allocation (for example, some runtime-global objects and types have static/runtime-managed storage). GC bookkeeping may be stored separately from the object payload; CPython’s `sys.getsizeof()` includes GC overhead for GC-tracked objects through its size-reporting mechanism. Exact struct layout, field widths, and accounting details are implementation-specific and vary by build.

An integer contains more than its mathematical digits: it carries type/reference metadata and storage for integer digits. A list stores a header and a separately allocated array of element pointers. A dictionary stores metadata plus table/entry structures. These indirections matter for large collections.

### 2.2 What `sys.getsizeof()` tells you

`sys.getsizeof(obj)` returns the object's **direct, implementation-specific size** as reported by its size mechanism. It does not recursively add the size of objects referenced by it.

```python
import sys

values = [1, 2, 3]
print(sys.getsizeof(values))
print(sum(sys.getsizeof(value) for value in values))
print(sys.getsizeof(values) + sum(sys.getsizeof(value) for value in values))
```

Numbers vary by interpreter/build. The first line is the list object plus its currently allocated pointer array; the second sums direct sizes of the integer objects; the third is a simple subtotal. It can still double-count shared objects or omit other reachable objects.

**Limitations:** this is not a portable language guarantee, not RSS, and not the amount the OS will release after deletion. Native-extension objects may own memory not included in the Python object's reported size. Allocator rounding and metadata can make reserved memory larger than the reported object size.

### 2.3 Measurement script

```python
import platform
import sys

print("implementation:", platform.python_implementation())
print("version:", sys.version.split()[0])
for label, value in [
    ("int 1", 1), ("float 1.0", 1.0), ("empty tuple", ()),
    ("3-item tuple", (1, 2, 3)), ("empty list", []),
    ("3-item list", [1, 2, 3]), ("empty dict", {}),
    ("empty string", ""), ("ASCII string", "memory"),
    ("non-ASCII string", "café"),
]:
    print(f"{label:16} {sys.getsizeof(value):>6} bytes")
```

**Expected observation:** types and populated/empty containers report different sizes. Do not hard-code counts into portable tests. Record the runtime and compare trends within the same build.

### 2.4 Memory arithmetic for collections

For a list of `N` references to distinct objects, a first-order estimate is:

\[
M \approx M_{\text{list header + pointer capacity}} + \sum_{i=1}^{N} M_{\text{element object},i}
\]

This omits allocator overhead, sharing, and other reachable objects. If every slot refers to the same integer object, do not count that object `N` times. For a dictionary mapping one million distinct strings to integer values, count the hash table/entries, every distinct key and its character storage, every distinct value object that is not shared, and allocator overhead. `sys.getsizeof(big_dict)` alone is not the dataset's size.

#### Worked first-order estimate (one measured build)

On the 64-bit CPython 3.13.5 build used for this lesson's audit, `sys.getsizeof(1)` reported 28 bytes, `sys.getsizeof(1.0)` 24 bytes, and `sys.getsizeof(list(range(1_000_000)))` 8,000,056 bytes. A comprehension-built one-million-float list (`[float(i) for i in range(1_000_000)]`) reported 8,448,728 bytes because its allocated pointer capacity differed. These values are measurements of that build, not guarantees.

- **List of one million integers:** list plus pointers is about 8,000,056 bytes. If you naïvely add 1,000,000 × 28 bytes for integer objects, the subtotal is about 36,000,056 bytes (34.3 MiB). This slightly overcounts shared cached small integers and omits allocator bookkeeping and any unrelated runtime state.
- **List of one million distinct floats:** using the measured comprehension-built list above, 8,448,728 bytes for the list plus 1,000,000 × 24 bytes for distinct float objects gives a first-order subtotal of about 32,448,728 bytes (about 30.9 MiB). This assumes one separately allocated float per element and excludes allocator overhead; another construction path may allocate a different pointer capacity.
- **One million distinct string-to-integer pairs in a dict:** use `sys.getsizeof(mapping) + sum(sys.getsizeof(k) for k in mapping) + sum(sys.getsizeof(v) for v in mapping.values())` as a direct-size subtotal, taking care not to count shared objects more than once. In the same build, a 100,000-entry `{f"key-{i}": i}` mapping reported a 3,844,864-byte shallow dictionary, average key shallow size about 49.9 bytes, and integer shallow size 28 bytes. A crude tenfold extrapolation suggests roughly 116 MB of direct-size subtotal for one million pairs, but the dictionary's capacity growth, key lengths, small-integer sharing, allocator rounding, and build differences make this only a planning estimate. Do not treat it as an RSS prediction.

The point of the arithmetic is to expose the terms that must be counted. Use the measurement exercise below to validate the actual representation and runtime you deploy.

## 3. Identity, integer caching, interning, and singletons

### 3.1 Equality is not identity

- `a == b` asks whether two objects compare equal according to their type.
- `a is b` asks whether they are the same object.
- `id(obj)` returns an identity value unique among simultaneously living objects. In CPython it is typically address-like, but Python does not promise that representation.

Use `is` when identity is intended—especially `value is None`. Use `==` for numeric and string values.

```python
left = [1, 2]
right = [1, 2]
print(left == right)  # True: equal contents
print(left is right)  # False: distinct list objects
print(None is None)   # True: singleton check
```

Output:

```text
True
False
True
```

### 3.2 Small-integer caching and constant reuse

CPython caches a range of small integers (commonly −5 through 256 in conventional builds). This is an implementation optimization, not a promise that equal integers have identical identity. The compiler may also reuse constants within a code object, so values outside the cache can sometimes appear identical.

```python
a, b = 256, 256
c, d = 257, 257
print(a is b)
print(c is d)
```

The first result is commonly `True` on CPython. The second is not portable: the compiler may reuse a constant object. Independently computed equal integers need not be identical. For example, `a = int("257"); b = int("257")` should be compared with `==`; do not rely on the identity result.

### 3.3 String interning

Interning allows an implementation to keep a canonical string object for some strings. CPython interns many identifier-like strings and offers `sys.intern()` for explicit interning.

```python
import sys
first = sys.intern("customer_status")
second = sys.intern("customer_status")
print(first is second)  # True while both refer to the interned object
```

Interning may help with repeated stable identifiers, such as schema field names. It is not a general optimization for arbitrary user input: interning many unique strings can retain memory. Behavior and lifetime details are version-sensitive. Never use identity to compare string values.

### 3.4 Singletons, empty tuple, and `id()` caveats

`None`, `True`, and `False` are singleton objects in Python semantics. The empty tuple is commonly shared by CPython, but do not generalize this into a guarantee that all equal tuples are identical.

Correct: `if result is None: ...`.

Incorrect: `if status is "ready": ...`; use `status == "ready"`.

In CPython, `id(obj)` is typically address-like. When an object dies, its address may later be reused, so IDs from objects that were not alive simultaneously do not prove they were the same object. Do not use `id()` as a persistent identifier, database key, cross-process handle, or proof of allocation behavior.

## 4. Why freed objects do not always reduce RSS

When the last reference to an ordinary CPython object disappears, reference counting often makes it reclaimable promptly. Cycles may require cyclic garbage collection. Reclaiming an object means its storage can be reused by the allocator; it does not mean the OS immediately reduces the process's resident memory.

Common reasons RSS remains high:
1. **Allocator reuse:** freed blocks remain available for future allocations.
2. **Fragmentation:** a pool/arena has some live blocks, preventing the whole region from being released.
3. **System allocator retention:** `malloc` implementations can retain freed memory in arenas/caches.
4. **Native allocations:** NumPy, compression libraries, database drivers, and other extensions may allocate outside the Python allocator.
5. **Resident pages and mappings:** pages may remain resident or mapped after application objects disappear.
6. **Still-reachable objects:** caches, globals, closures, tracebacks, cycles, or background tasks may keep data alive.

Ask separate questions: are objects reachable? Are Python allocations live? Is allocator-reserved memory high? Is RSS high? What does the container memory controller report?

## 5. CPython allocator layers

The names below are C API concepts; Python application code normally does not call them directly. Allocation domains define which API family must allocate/free a block; the concrete allocator behind a domain is build- and configuration-dependent.

| Layer | API family | Role |
|---|---|---|
| Raw memory | `PyMem_RawMalloc`, `PyMem_RawFree`, etc. | General-purpose buffers that can be allocated without an attached thread state; commonly uses the system allocator in conventional builds, but concrete defaults are build-dependent. |
| Python memory | `PyMem_Malloc`, `PyMem_Free`, etc. | General Python memory domain for buffers/internal allocations. |
| Object memory | `PyObject_Malloc`, `PyObject_Free`, etc. | Object allocation domain; conventional CPython uses pymalloc for eligible small allocations, with larger allocations routed elsewhere. |

Domains have C API contracts, but their underlying implementation and selection are build/version-sensitive. Extensions must use the matching allocation/free family rather than freeing a pointer with the wrong allocator.

### 5.1 Pymalloc: arenas, pools, blocks

For conventional GIL-enabled CPython builds, pymalloc is optimized for small allocations. A useful conceptual hierarchy:

```text
arena (large region acquired from the OS)
  └── pools (subregions managed for allocation size classes)
        └── blocks (fixed-size slots for allocations in one size class)
```

- **Block:** one allocation slot; blocks in a pool are sized for a particular allocation class.
- **Pool:** manages blocks of one size class and tracks free blocks; it may be partially full or empty.
- **Arena:** a larger region from which pools are obtained. It can be returned only when the allocator can release it as a whole under its rules.

This design makes small allocations fast but can retain memory when live blocks are scattered across pools/arenas. Exact arena/pool sizes, size classes, thresholds, and OS acquisition behavior must be checked for the target version/build. The roadmap's 1 MiB arena / 16 KiB pool figures are historical/conventional reference points, not universal promises; pool size has differed across releases/platforms, and free-threaded builds use different allocator architecture. A common rule of thumb is that conventional pymalloc handles requests up to around 512 bytes, with larger requests routed to the underlying allocator. Confirm exact details before relying on the threshold in low-level tooling.

### 5.2 Fragmentation

Internal fragmentation occurs when a block/size class reserves more space than the requested payload needs. External fragmentation occurs when free space is split across regions so the allocator cannot release a whole region or satisfy a request in the desired way.

A pool with one live block and many free blocks may not be releasable if it shares an arena with other live pools. Deleting most objects can free blocks without returning the same proportion of memory to the OS.

**Production example:** a long-running worker processes batches with millions of short-lived dictionaries. Later batches may reuse freed blocks, so throughput is fine even though RSS stays high. Under tight limits, batch size, representation, allocator choice, and worker recycling may matter more than live-object count alone.

### 5.3 `PYTHONMALLOC`

`PYTHONMALLOC` selects allocator behavior and/or enables debug hooks in CPython. Common values include `pymalloc`, `malloc`, `debug`, `pymalloc_debug`, and `malloc_debug`; CPython 3.13+ builds with mimalloc support may also accept `mimalloc` and `mimalloc_debug`. Exact accepted values depend on version/build. In a free-threaded build, mimalloc is required for the Python memory/object domains and cannot be disabled with `PYTHONMALLOC=malloc`. In a conventional GIL-enabled build, `PYTHONMALLOC=malloc` can help investigate whether pymalloc contributes to a pattern, but it changes the allocation path and may affect performance/RSS.

```bash
PYTHONMALLOC=malloc python memory_probe.py
```

Use the appropriate shell syntax on Windows. Set it before starting Python; existing allocations do not migrate. Treat this as a controlled diagnostic, not an automatic production fix.

## 6. Container-specific optimizations

### 6.1 Lists and over-allocation

A Python list is a resizable array of object references. It typically allocates spare pointer capacity so repeated `append()` operations do not require reallocation each time. This gives amortized \(O(1)\) append behavior, while a resize can occasionally cost \(O(n)\) as references are copied or storage is moved.

```python
import sys
items = []
previous_size = sys.getsizeof(items)
for number in range(100):
    items.append(number)
    current_size = sys.getsizeof(items)
    if current_size != previous_size:
        print(number + 1, current_size)
        previous_size = current_size
```

The output shows capacity-growth steps, not one line per append. Exact points and sizes are implementation details. This demonstrates over-allocation; it does not expose every internal capacity field or predict all list workloads. A list of numbers stores references to Python number objects, not packed numeric values.

### 6.2 Dictionaries, compact layout, and key sharing

Modern CPython dictionaries use compact layouts that separate index information from entries more efficiently than older implementations. Dictionaries used as instance attribute storage can share key-layout information across instances (PEP 412), reducing duplicated metadata when many instances have the same attribute names.

This is an implementation optimization, not a fixed bytes-per-entry contract. Table size depends on population, hash-table growth, key/value types, deletion history, and version. A million records represented as a million dictionaries repeats per-dictionary overhead. Columnar storage can put each field in a contiguous array, improving memory locality, vectorization, and compression.

### 6.3 Unicode representation (PEP 393)

CPython's flexible Unicode representation selects an internal character width appropriate to a string's contents (conceptually 1-, 2-, or 4-byte code units). Compact ASCII strings can be especially space-efficient. Two strings with the same number of characters therefore need not occupy the same amount of memory.

This representation is an internal CPython detail. `len(text)` counts Unicode code points, not UTF-8 bytes and not necessarily user-perceived grapheme clusters. Use `len(text.encode("utf-8"))` when UTF-8 byte length is what you need.

### 6.4 Tuple free lists and reuse

CPython has historically used free lists or specialized reuse strategies for some object types, including tuples, to reduce allocation overhead. These details have changed over releases; do not assume a particular tuple free list exists, has a particular size, or guarantees identity reuse in CPython 3.12–3.14. The reliable lesson is that object deallocation and returning memory to the OS are separate events.

## 7. Measuring memory: `tracemalloc`, allocator stats, Memray

### 7.1 `tracemalloc`

`tracemalloc` traces Python memory allocations made after tracing starts. It can compare snapshots and attribute traced allocations to Python source locations.

```python
import tracemalloc
tracemalloc.start()
before = tracemalloc.take_snapshot()
records = [{"id": i, "active": True} for i in range(20_000)]
after = tracemalloc.take_snapshot()
for stat in after.compare_to(before, "lineno")[:5]:
    print(stat)
del records
```

Output is environment-specific: it lists source locations and positive/negative allocation differences. Start tracing before the allocations of interest. Tracing has runtime and memory overhead and does not automatically account for every native allocation made directly by C extensions.

### 7.2 `sys._debugmallocstats()`

On CPython builds that expose it, `sys._debugmallocstats()` writes allocator statistics to standard error. It is a private/debugging-oriented interface: availability and output format are not stable public contracts.

```python
import sys
stats = getattr(sys, "_debugmallocstats", None)
if stats is None:
    print("This interpreter does not expose _debugmallocstats")
else:
    stats()
```

Use it on a known CPython build. Avoid parsing its text as a stable production interface.

### 7.3 Memray and native allocations

Memray can profile Python and native allocation activity. Its native stack capture can help attribute allocation paths when the environment supports the required stack collection. Install it according to its official documentation and consult the installed version's help before using a specific command. A typical workflow is:

```bash
python -m pip install memray
python -m memray run --native memory_probe.py
python -m memray stats memray-*.bin
```

Exact options vary by Memray release. Profilers add overhead; native stack traces can require platform/toolchain support. Use `tracemalloc` as a standard-library starting point and a native-aware profiler when evidence suggests allocations outside Python's traced allocator.

### 7.4 Measurement discipline

Record interpreter version/build, OS/architecture, allocator environment, tracing/profiling state, workload size and representation, and whether a measurement is direct object size, traced allocations, or RSS. Use repeated equivalent trials. Never compare numbers from different workloads/configurations as if they isolate one cause.

## 8. Object-heavy versus compact representations

### 8.1 `__slots__`

Ordinary Python instances commonly store attributes in an instance dictionary. `__slots__` declares fixed instance attributes and can avoid a per-instance `__dict__` (unless inherited or explicitly added), reducing memory for many instances.

```python
class PointWithDict:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class PointWithSlots:
    __slots__ = ("x", "y")
    def __init__(self, x, y):
        self.x = x
        self.y = y

points_a = [PointWithDict(i, i + 1) for i in range(10_000)]
points_b = [PointWithSlots(i, i + 1) for i in range(10_000)]
```

Measure the full representation, not only `sys.getsizeof(points_a[0])`: referenced integers, list capacity, and allocator effects matter. `__slots__` changes behavior: dynamic attributes may be disallowed, inheritance needs care, and weak-reference support may need a `__weakref__` slot. It is useful for large populations of small fixed-schema objects, not automatically better for every class.

### 8.2 Tuples, `array('d')`, NumPy, Arrow, and columnar layouts

- A tuple is compact as a container but stores references to Python objects.
- `array('d')` stores C double values in a contiguous buffer, avoiding a separate Python float object per element.
- NumPy arrays store homogeneous numeric data in contiguous or strided buffers and can vectorize operations.
- Arrow uses typed columnar buffers and supports efficient interchange and analytical workloads.
- A `struct`-packed `bytes` representation can be compact but requires explicit encoding/decoding and careful schema handling.

For one million double-precision values, a Python list may need one million references plus one million Python float objects if values are distinct. `array('d')` and a contiguous NumPy `float64` array need approximately `8N` bytes for the raw double payload, plus metadata/capacity/alignment. These are payload-level estimates, not RSS predictions. Construction can temporarily hold old and new representations at once. Choose based on operations, mutability, interoperability, and measurement.

## 9. Immortal objects and copy-on-write (PEP 683)

PEP 683 introduced immortal objects in CPython 3.12. Conceptually, selected objects have a reference-count state that avoids ordinary reference-count writes. This can reduce mutation and improve copy-on-write (COW) behavior in process-forking scenarios.

The roadmap mentions `None`, small integers, and interned strings as examples; the exact set and implementation details are version/build-dependent. Do not assume every interned string or every object of a type is immortal. This is not an application API for marking arbitrary objects immortal.

### Copy-on-write after `fork`

On systems using `fork`, the child initially shares memory pages with the parent. A page is copied when either process writes to it. Reference-count updates, allocator metadata changes, and ordinary mutations can dirty pages and reduce sharing. Immortal objects can reduce some refcount writes but do not eliminate all COW costs.

`gc.freeze()` can help carefully designed pre-fork servers by moving long-lived tracked objects out of normal cyclic-GC tracking before fork. The documented pattern for a process that will `fork()` without `exec()` is to disable GC early in the parent, call `gc.freeze()` immediately before `fork()`, and re-enable GC early in the child. Apply this only when the process lifecycle is understood; it is not a universal switch for eliminating COW. Follow the GC docs and test the actual worker model. Process start-method defaults vary by platform/release: in Python 3.14, `fork` is no longer the default on any platform; `forkserver` is the default on POSIX platforms that support it, while macOS and Windows use `spawn` by default. Check `multiprocessing.get_start_method()` in the deployed environment, and explicitly choose a context only when the application requires it.

## 10. Free-threaded builds and native allocator interactions

A free-threaded CPython build changes more than a lock setting. It uses allocation and reference-management strategies designed for concurrent execution; current free-threaded CPython uses mimalloc-based allocation machinery. Per-thread heaps/caches, biased or deferred reference counting, and related optimizations are implementation details explored further in the GIL/subinterpreter lesson.

Implications:
- Memory use can differ between conventional and free-threaded builds.
- Many short-lived objects may behave differently under different allocator strategies.
- Native extensions must be compatible with the selected build; their assumptions about the GIL and object lifetime matter.
- Do not infer that free-threaded execution uses less memory or that a particular allocator is available in every build.

The system allocator also matters. On Linux, glibc may retain memory in allocator arenas; `M_ARENA_MAX` and `malloc_trim()` are glibc-specific diagnostics/tuning topics. `jemalloc` and `mimalloc` may be used in specific builds or supported deployment arrangements. `LD_PRELOAD` changes process-wide allocation behavior and can cause compatibility problems; experiment only in a disposable environment and validate before any production use.

Large allocations (for example, buffers above pymalloc's small-request threshold) are generally routed to the underlying allocator, which may use `malloc`, `mmap`, or platform-specific mechanisms. The exact cutoff and path are implementation-dependent.

## 11. Cyclic GC and container tracking

CPython primarily reclaims ordinary objects through reference counting, with cyclic garbage collection for unreachable reference cycles involving GC-tracked objects. Containers that can participate in cycles need GC support; GC bookkeeping contributes overhead beyond a simple payload estimate.

Some tuples and dictionaries containing only atomic/non-container values can be untracked from cyclic GC when CPython determines they cannot participate in a cycle through those contents. Tracking decisions are internal and may change as contents change. `gc.is_tracked()` demonstrates behavior on the current interpreter but should not be used to predict exact layout.

```python
import gc
gc.collect()  # Give the collector an opportunity to untrack eligible containers.
print(gc.is_tracked([]))
print(gc.is_tracked((1, 2, 3)))
print(gc.is_tracked(([],)))
```

Representative CPython behavior often shows lists and tuples containing a list as tracked, while a tuple of atomic integers may be untracked after relevant GC processing. Exact observations can vary by version and timing. GC tracking concerns cycle detection, not whether an object is on the heap.

Why millions of small dictionaries hurt: each dictionary has table/entry overhead; keys and values are separate objects/references; dictionaries may be GC tracked; pointer-rich layouts have poorer cache locality than contiguous buffers; and GC traverses tracked containers to search for cycles. For fixed schemas consider slotted dataclasses; for homogeneous numeric data consider arrays/NumPy; for analytics consider Arrow. Measure actual operations and conversion costs.

## 12. Large buffers and zero-copy `memoryview`

`memoryview` exposes a view over an object's buffer protocol without copying the underlying bytes for ordinary compatible views. It is useful for binary parsing, network buffers, and slicing large arrays.

```python
payload = bytearray(b"abcdefgh")
view = memoryview(payload)
part = view[2:5]
print(bytes(part))
part[0] = ord("X")
print(payload)
part.release()  # Release the sliced view as well.
view.release()  # Release the parent view.
```

Output:

```text
b'cde'
bytearray(b'abXdefgh')
```

The slice is a view into the same mutable buffer, so changing it changes the original. A view can keep the exporter alive and may prevent resizing some exporters while the view exists. `bytes(part)` explicitly copies the selected bytes. Zero-copy reduces copying but does not mean zero memory use, zero synchronization concerns, or zero lifetime constraints.

`bytearray` and `io.BytesIO` may over-allocate capacity to reduce repeated reallocations. Repeated concatenation of immutable `bytes` can copy large buffers; prefer `bytearray`, `BytesIO`, or views where appropriate, but benchmark and keep ownership/lifetime rules clear.

## 13. RSS, working set, page cache, cgroups, and `MemoryError`

### 13.1 Metrics are not interchangeable

- **Virtual address space / virtual size:** ranges mapped into a process; not all pages need to be resident.
- **RSS (resident set size):** pages currently resident for the process; shared pages complicate attribution.
- **Working set:** an OS- or monitoring-tool-specific estimate of actively used/resident memory over a period.
- **Page cache:** filesystem-backed data cached in memory; cgroup accounting can include some cache even when it is not simply private process heap.
- **cgroup memory:** Linux container accounting and limits, which may include more than one process's Python heap and may include page cache/kernel memory according to cgroup version/configuration.

Check the deployed cgroup version and metric source. A container limit is not equivalent to the sum of `sys.getsizeof()` values or one process's RSS.

### 13.2 `MemoryError` and OOM kills

Python may raise `MemoryError` when an allocation fails and the runtime can report it. Under an OS/container limit, however, the kernel may kill a process before Python can raise a catchable exception. Native extensions can also fail differently.

A `MemoryError` handler is not a substitute for memory budgeting. Avoid allocating a huge fallback diagnostic inside a memory-exhaustion handler. Leave headroom for runtime overhead, request concurrency, native buffers, and transient copies.

### 13.3 `ulimit -v`

On Unix-like systems, `ulimit -v` can set a virtual-memory limit for a shell-launched process where supported. It is not a portable container memory limit and can behave poorly with runtimes that reserve large address ranges. Use it only in a controlled experiment and understand platform semantics; for containers, configure and inspect the relevant cgroup limits.

## 14. Exercise 1 — build a memory measurement table

**Goal:** compare memory behavior across representations without pretending one measurement is the whole truth.

Save as `memory_table.py`:

```python
import sys
import tracemalloc
from array import array

N = 100_000

def measure(label, factory):
    tracemalloc.start()
    before = tracemalloc.take_snapshot()
    value = factory()
    after = tracemalloc.take_snapshot()
    delta = sum(stat.size_diff for stat in after.compare_to(before, "filename"))
    print(f"{label:22} traced_delta={delta:>12,} bytes  "
          f"per_item={delta / N:8.2f} bytes")
    tracemalloc.stop()
    return value

# Distinct objects are deliberately created in these examples.
python_ints = measure("list of ints", lambda: [int(str(i)) for i in range(N)])
python_floats = measure("list of floats", lambda: [float(i) for i in range(N)])
records = measure("dict records", lambda: [
    {"id": i, "ok": True} for i in range(N)
])
packed_doubles = measure("array('d')", lambda: array("d", (float(i) for i in range(N))))

print("direct list size:", sys.getsizeof(python_ints))
print("direct first int size:", sys.getsizeof(python_ints[0]))
print("direct records list size:", sys.getsizeof(records))
print("direct first record size:", sys.getsizeof(records[0]))
print("direct array size:", sys.getsizeof(packed_doubles))
```

Run `python memory_table.py`.

**Question:** How do object count, representation, and allocator behavior affect measured memory?

**Procedure**
1. Record Python version, OS, and build.
2. Run the script more than once and keep the results.
3. Add a slotted dataclass with the same fields, a tuple-based representation, and a NumPy array if NumPy is available. For a binary/numeric payload, also compare `struct.pack`/`struct.pack_into` into a `bytes` or `bytearray` buffer; for analytical columns, optionally compare Arrow if installed. State which metadata and conversion buffers each representation includes.
4. Compare `tracemalloc` deltas, direct `getsizeof()` values, and process RSS using a suitable OS tool. They measure different things.
5. For a one-million-element or one-million-row variant, use the worked estimate above to budget memory first and run only where there is adequate headroom. Include the dictionary table, distinct key/value objects, wrapper objects, and temporary conversion copies in the estimate.

**Expected observations:** pointer-rich lists and dictionary records generally allocate substantially more traced memory than a packed numeric array for the same number of numeric values. In the audited CPython 3.13.5 environment, the original N=100,000 script reported approximate traced deltas of 3.59 MB for integers, 3.20 MB for floats, 22.39 MB for dictionary records, and 0.82 MB for `array('d')`; these are representative observations from one run, not fixed outputs. Exact ratios depend on representation, interpreter, and data. `array('d')` is comparable to a numeric column, not to dictionaries containing multiple fields. NumPy/Arrow/packed bytes may reduce per-value overhead for suitable schemas, but the result depends on metadata, alignment, ownership, conversion costs, and whether buffers are copied.

**Interpretation:** per-object headers, references, table capacity, and allocation granularity compound at scale.

**What this does not prove:** a universal bytes-per-record ratio, total RSS, or that one representation is faster for every operation. `tracemalloc` adds overhead and does not see every native allocation.

## 15. Exercise 2 — RSS and fragmentation experiment

Run this in a disposable process. Memory measurements vary widely by allocator, OS, workload, and container limit. Optionally install `psutil` with `python -m pip install psutil`; otherwise use an OS process tool.

Save as `rss_fragmentation.py`:

```python
import gc
import os
import sys
import time

try:
    import psutil
except ImportError:
    psutil = None

def rss_mib():
    if psutil is None:
        return None
    return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)

def report(label):
    value = rss_mib()
    if value is None:
        print(f"{label}: psutil not installed; use OS process metrics")
    else:
        print(f"{label}: RSS={value:.1f} MiB")

print("Python:", sys.version.split()[0])
report("start")
items = [{"key": f"item-{i}", "value": i, "flag": bool(i & 1)}
         for i in range(300_000)]
report("after allocation")
items.clear()
del items
gc.collect()
report("after clear + gc.collect")
time.sleep(1)
report("after brief wait")
```

**Question:** Does releasing a large population of objects return the same amount of RSS to the OS?

**Procedure**
1. Start the script as a fresh process and record baseline RSS.
2. Record RSS after allocation and after clearing/deleting references.
3. Repeat with a different representation or smaller chunks.
4. Repeat with `PYTHONMALLOC=malloc python rss_fragmentation.py` in a separate process if supported.
5. Record Python build, environment, workload, and container limits.

**Expected observations:** RSS rises after allocation. After references are released, Python-level live allocations decrease, but RSS may fall partially, remain high, or sometimes fall substantially. Variability is expected.

**Interpretation:** allocator reuse and fragmentation can prevent RSS from mirroring live-object counts. A packed representation or smaller chunks may reduce peak memory and allocator pressure. Worker recycling can be an operational mitigation for workloads with high transient peaks.

**What this does not prove:** that pymalloc alone caused the pattern, that there is no leak, or that `PYTHONMALLOC=malloc` is universally better. The system allocator, OS, page residency, native extensions, and workload all affect results.

## 16. Advanced diagnostics and production guidance

### Common misconceptions

| Misconception | Correction | Practical response |
|---|---|---|
| `sys.getsizeof(x)` is the total reachable memory. | It reports direct object size, not a recursive graph. | Measure references and distinct reachable objects separately. |
| `del x` returns its bytes to the OS. | Releasing a reference, deallocation/reuse, and OS release differ. | Measure reachability, traced allocations, allocator stats, and RSS separately. |
| `a is b` means values are equal. | Identity and equality are different. | Use `==` for values and `is None` for the singleton. |
| Every list element's payload is stored inline. | Lists store references; objects are separately allocated. | Use packed arrays for homogeneous numeric data where appropriate. |
| Stable RSS proves no leak. | Retention and allocator reuse can mask each other. | Track equivalent workloads over repeated cycles. |
| High RSS proves a leak. | Allocator retention and fragmentation can keep RSS high after frees. | Investigate reachability and native allocations before concluding. |
| `tracemalloc` sees all memory. | It does not account for every native allocation or total RSS. | Use a native-aware profiler when required. |
| `__slots__` is always better. | It changes instance behavior and helps mainly when per-instance savings matter. | Measure the actual population and access pattern. |
| Immortal objects make `fork` free. | They reduce selected refcount writes; many writes still trigger COW. | Benchmark actual worker startup and memory sharing. |
| `MemoryError` is guaranteed under a cgroup limit. | The kernel may OOM-kill the process first. | Budget headroom and monitor cgroup metrics. |

### Diagnostic sequence for a memory incident

1. **Record environment:** Python version/build, GIL-enabled or free-threaded, OS, container limits, allocator environment, native libraries, workload size.
2. **Confirm growth:** measure equivalent workload cycles; distinguish one-time warm-up from unbounded growth.
3. **Check reachability:** inspect caches, globals, queues, closures, tasks, tracebacks, and reference cycles.
4. **Trace Python allocations:** use `tracemalloc` snapshots started before the workload.
5. **Check allocator/process metrics:** use `_debugmallocstats()` where available and observe RSS/working-set/cgroup values.
6. **Investigate native allocations:** use Memray or an approved native profiler if Python allocation traces do not explain growth.
7. **Reduce per-record overhead:** test slots, chunking, arrays, columnar formats, and object reuse where appropriate.
8. **Mitigate safely:** bound batches/queues, add backpressure, recycle workers if needed, and test under actual container limits.
9. **Avoid unsafe assumptions:** do not blindly tune glibc, set `LD_PRELOAD`, or increase limits without evidence and operational review.

## 17. Concept map

```text
Python object graph
  ├── direct object size (`sys.getsizeof`)
  ├── references to other objects (deep size ≠ direct size)
  └── lifetime
        ├── refcount reaches zero → object can be deallocated
        └── unreachable cycle → cyclic GC may reclaim it

allocation
  ├── raw memory domain
  ├── Python memory domain
  └── object allocation domain
        └── conventional pymalloc
              ├── arenas
              ├── pools
              └── fixed-size blocks
                    └── freed blocks may be reused without lowering RSS

measurement
  ├── `tracemalloc`: traced Python allocations
  ├── `_debugmallocstats`: CPython allocator diagnostics
  ├── Memray/native profiler: Python + supported native allocation stacks
  └── RSS / working set / cgroup: process or container memory state

design choices
  ├── `__slots__` for fixed-schema instances
  ├── `array` / NumPy for homogeneous numeric values
  ├── Arrow / columnar layout for analytical data
  └── chunking / process recycling for peak-memory control
```

## 18. Self-check questions with answers

### 1. Why does `sys.getsizeof([1, 2, 3])` not equal `3 × sizeof(int)`?

**Answer:** A list's reported size covers the list object and its allocated array of references, not the integer objects' storage. Integer objects are separate allocations. The list may also have spare pointer capacity from over-allocation. Adding element sizes naïvely can double-count shared objects and still omit allocator metadata/native memory.

### 2. What are arenas, pools, and blocks, and how do they cause fragmentation?

**Answer:** In conventional pymalloc, arenas are larger memory regions divided into pools, which manage fixed-size blocks from a size class. Free blocks can be reused quickly. If some blocks remain live in a pool/arena, the allocator may be unable to return the entire region to the OS even when many other blocks are free. Exact sizes and thresholds vary by CPython version/build and are not portable constants.

### 3. Reproduce a “memory never shrinks” case and remove it by changing the data representation.

**Answer:** Run Exercise 2 in a fresh process: allocate many small dictionaries, release references, collect cycles, and record RSS before and after. RSS may not fall proportionally because freed blocks can be retained by pymalloc/system allocator and fragmentation can keep regions resident. Then change representation—for example, use `array('d')` for a homogeneous numeric column, a slotted class for fixed-schema records, or smaller chunks—and compare peak RSS and post-release behavior. Exact outcomes depend on allocator/OS. An inconclusive result is valid: one RSS experiment cannot isolate the allocator as the sole cause.

## 19. Summary

- `sys.getsizeof()` reports direct object size, not the full reachable graph, allocator overhead, or RSS.
- CPython may cache small integers and intern some strings, but ordinary value comparisons should use `==`; `is` is for identity.
- CPython `id()` is typically address-like, but IDs can be reused after object death and are not persistent identifiers.
- Object allocation, deallocation, allocator reuse, and releasing pages to the OS are separate events.
- Conventional pymalloc uses arenas, pools, and blocks for small allocations; fragmentation can keep RSS high. Exact allocator layout varies by version/build.
- Lists over-allocate, dictionaries use compact layouts and may share keys, and Unicode uses a flexible representation. These are optimizations, not portable size contracts.
- Use `tracemalloc` for traced Python allocations, allocator diagnostics where available, and native-aware tools for native allocations. Compare with RSS and cgroup metrics rather than substituting one for another.
- `__slots__`, packed arrays, NumPy, Arrow, and columnar layouts can reduce per-record overhead, but measure the actual workload.
- Immortal objects (PEP 683) can reduce selected refcount writes and help COW behavior, but do not eliminate COW costs.
- Cyclic GC, native allocator behavior, large buffers, memoryviews, process start methods, and container limits influence real memory behavior.
- The production goal is not to make RSS always fall after `del`; it is to understand the memory graph, bound peak usage, select appropriate representations, and diagnose growth with multiple independent measurements.

## References

Use documentation and source for the exact deployed version. Internal source layouts and allocator behavior can change.

1. `sys.getsizeof`, runtime APIs: https://docs.python.org/3.14/library/sys.html#sys.getsizeof
2. Python data model and object identity: https://docs.python.org/3/reference/datamodel.html
3. `gc` module: https://docs.python.org/3.14/library/gc.html
4. `tracemalloc`: https://docs.python.org/3.14/library/tracemalloc.html
5. `array` module: https://docs.python.org/3.14/library/array.html
6. `memoryview` and buffer protocol: https://docs.python.org/3.14/library/stdtypes.html#memory-views
7. `multiprocessing` start methods: https://docs.python.org/3.14/library/multiprocessing.html#contexts-and-start-methods
8. PEP 393 — Flexible String Representation: https://peps.python.org/pep-0393/
9. PEP 412 — Key-Sharing Dictionary: https://peps.python.org/pep-0412/
10. PEP 683 — Immortal Objects: https://peps.python.org/pep-0683/
11. CPython C API memory management: https://docs.python.org/3.14/c-api/memory.html
12. CPython allocator source (match the tag to your version): https://github.com/python/cpython/blob/main/Objects/obmalloc.c
13. Memray documentation: https://bloomberg.github.io/memray/
14. Linux cgroup v2 memory controller: https://docs.kernel.org/admin-guide/cgroup-v2.html
15. Python `resource` module (Unix-specific): https://docs.python.org/3.14/library/resource.html
16. Python 3.12 “What’s New”: https://docs.python.org/3/whatsnew/3.12.html
17. Python 3.13 “What’s New”: https://docs.python.org/3/whatsnew/3.13.html
18. Python 3.14 “What’s New”: https://docs.python.org/3/whatsnew/3.14.html
