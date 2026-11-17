# Lesson 04 — `tracemalloc` and Memory Leak Hunting

> **Module:** Stage 1 — Programming & Computational Thinking → Module 1.17, Profiling, Memory and Runtime Performance  
> **Target:** Python 3.12+; check the documentation for the exact interpreter and platform you run.  
> **Scope:** Find and explain Python allocation growth and object retention. This lesson complements, but does not replace, Lesson 05 (`05-memray-and-allocation-analysis.md`, Memray/native allocation analysis) or Lesson 06 (`06-garbage-collector-tuning-and-reference-cycles.md`, garbage collection and reference-cycle internals).

## Why this lesson matters

A long-running ETL job can process the same-sized batch repeatedly yet consume more memory after every batch. The cause might be an application-level collection that keeps records forever, a cache without a limit, a traceback that retains a frame, a task that never finishes, or a native buffer that Python's allocation tracer cannot fully explain. A rising process RSS alone does not identify which cause is responsible.

The disciplined workflow is:

**reproduce → measure → compare → identify references → change the retention cause → verify correctness and object lifetime → measure again.**

Do not label every increase a “leak.” Temporary allocation churn, allocator high-water marks, intentional caches, and genuinely retained objects are different phenomena.

## 1. Location, prerequisites, and learning objectives

### Where this lesson fits

The Module 1.17 roadmap places this lesson in **Phase B — Where Does the Memory Go?**, after CPU profiling and sampling, and before Memray allocation analysis and garbage-collector tuning. The shared project is a deliberately inefficient log-analysis/ETL script called `slowlog`, containing a hot loop and a memory-retention defect. Use the same workload to practise controlled investigations rather than inventing a different project for each tool.

### Prerequisites

- Python containers, references, functions, exceptions, and object lifetime.
- Generators and the memory trade-off between streaming and materializing a collection.
- Reference counting and a basic understanding of cyclic garbage collection.
- `weakref`, `contextvars`, and the difference between a reference and a copy.
- Basic process memory concepts: virtual memory, resident set size (RSS), and operating-system/container memory limits.
- Test discipline: preserve outputs and edge-case behavior while fixing a suspected leak.

Relevant earlier roadmap topics include Module 1.9's generators/object model/GC lessons, Module 1.11's `__slots__` and descriptors, Module 1.13's `weakref` and `contextvars`, and Module 1.14's bytes, `memoryview`, and `mmap`.

### Learning objectives

By the end, you should be able to:

1. Explain the difference between an object's shallow size, the graph of objects it retains, traced Python allocations, and process RSS.
2. Capture and compare `tracemalloc` snapshots without confusing cumulative allocation churn with retained memory.
3. Recognize common retention patterns in collections, caches, callbacks, tracebacks, tasks, threads, context variables, and logging configuration.
4. Use `psutil`, `resource`, `gc`, weak references, and `objgraph` as complementary evidence.
5. Reproduce growth, locate a retaining reference, fix the cause, and verify object lifetime after the fix.
6. Explain why RSS may remain high after Python objects are freed, and when native allocation tools are the next step.
7. Add reliable regression tests and monitoring without depending on exact RSS values.

## 2. The memory vocabulary

### 2.1 Objects, references, and allocations

Python variables normally hold references to objects. A list does not contain a second copy of every referenced object: it stores references to those objects. A dictionary similarly stores references for keys and values, alongside its own table structure. If several structures refer to one object, that object remains alive while a strong reference to it remains.

An **allocation** is an event in which memory is obtained for an object or buffer. An allocation can be short-lived: a parser may allocate a temporary string, use it, and release the last reference immediately. A **retention problem** occurs when an object remains reachable longer than the application's intended lifetime. A **leak-like growth pattern** is sustained growth without an intentional bound or useful release condition; Python-level reachability is often the reason, but native code can also retain memory.

Do not infer retention from allocation volume alone. A workload can allocate many temporary objects while ending at a stable live-memory level.

### 2.2 Shallow size versus retained graph size

`sys.getsizeof(obj)` reports the shallow size of the object as reported by that object's type. It does not recursively add the sizes of objects referenced by the object. It may also omit memory managed outside the object's directly reported size.

```python
import sys

numbers = [10**6 + i for i in range(5)]
print(sys.getsizeof(numbers))       # shallow list size; varies by build/platform
print(sys.getsizeof(numbers[0]))    # shallow size of one referenced integer
```

The list's shallow size covers its list structure and allocated reference slots; it does not include the integer objects it points to. Exact byte counts vary with Python version, architecture, allocator, and object representation. Never copy a `getsizeof()` result from one machine as a universal constant.

A “deep size” must define how it traverses the object graph and avoids counting the same shared object multiple times. Even then, it is not the same as “memory that would be freed if this variable were deleted”: another root may reference the same object.

**Pitfall 1 — treating shallow size as total size.** Detect it when a small-looking container is blamed despite holding many large objects. Correct it by examining referenced objects and retained paths, while remembering shared references.

### 2.3 RSS, virtual memory, and traced memory

- **RSS (resident set size):** pages of a process currently resident in physical memory, as reported by the OS. It includes Python-managed memory, native allocations, interpreter/runtime structures, mapped pages, and allocator overhead; exact accounting differs by platform.
- **Virtual memory:** the process's virtual address-space mappings; it is not equivalent to physical RAM currently resident.
- **Traced current/peak memory:** allocations that `tracemalloc` has observed and that remain traced at the relevant time, and the peak traced value since tracing began or the peak was reset.
- **Object count:** a count of objects of a type or reachable from selected roots; it is not a byte count and may omit types not tracked by the selected mechanism.

`tracemalloc` is excellent for Python allocations tracked by the interpreter's tracing hooks. It is not a complete process-memory profiler. It may not account for every allocation made directly by C/C++ libraries, native allocators, memory-mapped files, or GPU runtimes. Conversely, RSS can remain high after traced objects disappear because an allocator keeps arenas/pages for reuse or because other memory remains resident.

**Diagnostic principle:** compare several signals over the same repeated workload. Do not expect RSS and traced memory to match.

## 3. Beginner: start tracing and read snapshots

### 3.1 Start tracing early

```python
import tracemalloc

tracemalloc.start( traceback_limit=10 )
```

The positional or keyword traceback limit specifies how many frames are stored for each traced allocation. More frames can help identify call paths, but tracing consumes memory and CPU. Start tracing before the workload whose allocations you want to observe. Starting after a large object graph was allocated cannot reconstruct the allocation history for objects created before tracing began.

Use a small isolated script first. Do not enable expensive tracing indiscriminately on every production request without estimating overhead and considering data sensitivity.

### 3.2 Current and peak traced memory

```python
import tracemalloc

tracemalloc.start(10)
# Run the workload here.
current_bytes, peak_bytes = tracemalloc.get_traced_memory()
print(f"current={current_bytes / 1024**2:.2f} MiB")
print(f"peak={peak_bytes / 1024**2:.2f} MiB")
```

- `current_bytes` is the amount currently traced.
- `peak_bytes` is the high-water mark of traced memory since tracing started or since the peak was reset.
- `tracemalloc.reset_peak()` resets the recorded peak to the current traced level; it does not free allocations or reset the current level.
- `tracemalloc.clear_traces()` clears tracing records, not the application's objects. Use it only when you deliberately want to discard earlier trace history.

A high peak with a low current level can indicate large temporary allocations. A rising current level across equivalent batches is evidence to investigate, not proof by itself of a leak.

### 3.3 Take snapshots and compare by source line

```python
import tracemalloc

tracemalloc.start(10)
baseline = tracemalloc.take_snapshot()

run_one_batch()

after = tracemalloc.take_snapshot()
for stat in after.compare_to(baseline, "lineno")[:10]:
    print(stat)
```

A snapshot records traced allocations that are live when the snapshot is taken. `after.compare_to(baseline, "lineno")` compares the two snapshots and returns statistics ordered by the absolute size of the differences (largest absolute differences first). A statistic commonly displays a signed difference in size and count, followed by the traceback/location for the grouping key.

For investigating retained growth, positive size/count differences at relevant lines are often useful. Negative differences can be just as informative: those lines have fewer traced allocations or bytes in the later snapshot. A line with many allocations is not automatically a leak; ask whether those allocations are still live and whether the workload should retain them.

`Snapshot.statistics("lineno")` groups live traced allocations by the line identified in their traceback. Other useful grouping keys include `"filename"` and `"traceback"`; use traceback grouping when call paths matter.

**Pitfall 2 — confusing total allocations with live allocations.** A snapshot is not a log of every allocation ever performed. It describes traced allocations still live at snapshot time. To study churn, compare repeated current/peak measurements or use an allocation profiler designed for that question.

### 3.4 Allocation tracebacks

Each traced allocation can retain a traceback up to the configured limit. A statistic such as:

```text
# Illustrative format only; values are not measured results:
842.1 KiB  12000 blocks  pipeline.py:87
```

means that the grouped live traced allocations associated with the reported source line account for about that many bytes and blocks in the later snapshot/statistic. It does **not** mean that the line allocated that amount only once, nor does it prove the allocations are unintended. The exact formatting and numbers are illustrative.

Use `stat.traceback` (a traceback object in the `tracemalloc` API) to inspect the allocation path when needed:

```python
for stat in after.statistics("traceback")[:5]:
    print(f"{stat.size / 1024:.1f} KiB across {stat.count} blocks")
    for frame in stat.traceback:
        print(f"  {frame.filename}:{frame.lineno}")
```

Interpretation sequence:

1. Find the largest meaningful positive differences.
2. Confirm the source line belongs to your workload, not just test harness or imports.
3. Inspect the traceback to identify the allocation path.
4. Ask which long-lived object or root could still reference the allocations.
5. Reproduce with a smaller controlled workload and verify the suspected reference path.
6. Apply a fix and repeat the same measurements.

### 3.5 Snapshot comparison: a controlled repeated workload

The following script demonstrates how to compare equivalent workload phases. It is runnable as a single file. Its output is deliberately not hard-coded because object sizes and trace statistics vary by interpreter and environment.

```python
# snapshot_demo.py
import tracemalloc

retained_records: list[dict[str, object]] = []

def process_batch(batch_id: int, retain: bool) -> None:
    # Build a fresh batch. Payload strings are deliberately distinct enough
    # to avoid relying on string interning as the demonstration.
    rows = [
        {"id": batch_id * 10_000 + i, "payload": f"event-{batch_id}-{i}-" + "x" * 80}
        for i in range(2_000)
    ]
    # Work with the rows as a pipeline might.
    total = sum(row["id"] for row in rows)
    if total < 0:
        raise AssertionError("unreachable")
    if retain:
        retained_records.extend(rows)
    # Otherwise, rows become unreachable when this function returns.

tracemalloc.start(10)
process_batch(0, retain=False)
baseline = tracemalloc.take_snapshot()

for batch_id in range(1, 4):
    process_batch(batch_id, retain=True)

after = tracemalloc.take_snapshot()
print("Current/peak MiB:", tuple(round(v / 1024**2, 2)
                                for v in tracemalloc.get_traced_memory()))
for stat in after.compare_to(baseline, "lineno")[:8]:
    print(stat)
```

The retained version intentionally stores each batch in a global list. Expect the later snapshot to show positive growth associated with row/dictionary/string allocation sites. Do not use an exact byte count as a test expectation.

To test the corrected variant, change the three calls to `retain=False`, rerun in a fresh process, and compare after equivalent warm-up/baseline handling. Temporary peak memory can still rise during each batch; the live traced memory after each batch should be much more stable than in the retaining version. For a more rigorous experiment, take snapshots after each batch and compare slopes rather than relying on one pair of snapshots.

**Pitfall 3 — taking snapshots at inconsistent phases.** If one snapshot is taken during a batch and another after cleanup, their difference mixes workload phase with retention. Capture snapshots at equivalent boundaries and include a warm-up phase when imports or one-time initialization are part of the program.

## 4. Intermediate: identify common retention patterns

The key question is not simply “what allocated this object?” but “what strong reference keeps it alive?”

### 4.1 Unbounded lists, dictionaries, and global registries

```python
# Defect: every processed event remains reachable forever.
EVENTS_BY_ID: dict[str, dict[str, object]] = {}

def handle_event(event: dict[str, object]) -> None:
    EVENTS_BY_ID[str(event["id"])] = event
```

This may be intentional if the dictionary is a bounded index for the full run. It becomes a leak-like defect when the intended lifetime is one batch or when there is no eviction/retention policy. Common variants include appending every parsed row to a global list, collecting all error messages indefinitely, or registering each job in a global dictionary without removing completed jobs.

Correct the ownership model: keep only the fields needed, clear per-batch structures at the boundary, persist required records to a durable store, or use an explicitly bounded cache. Avoid “fixing” memory by deleting records that are still needed for correctness.

### 4.2 Callbacks and listeners that never unregister

Event buses, signal handlers, metrics registries, and plugin systems often retain callbacks. A bound method retains its instance; a closure may retain its enclosing variables. If the registration owner outlives the listener, the listener can remain alive even when the application has dropped its own reference.

Diagnosis: inspect the registry's contents and lifecycle; verify registration and unregistration are paired; use weak references only when the callback semantics allow a listener to disappear automatically. Weak callbacks can make event delivery nondeterministic if no other strong reference owns the listener.

### 4.3 Caches and cached instance methods

`functools.lru_cache` decorates a function and stores arguments and results until eviction or cache clearing. When used on an instance method, `self` is part of the cache key. A module-level wrapper can therefore retain instances. `@functools.cache` is unbounded; `lru_cache(maxsize=...)` has a bound on entries, not bytes, and each entry can vary substantially in size.

Use bounded caches when a cache is justified, measure hit rate and retained data, and expose invalidation where needed. If a method cache should not own an instance, consider an external per-instance cache with a deliberate lifecycle or a weak-key design whose values do not themselves strongly reference the keys.

### 4.4 Exceptions and retained tracebacks

An exception's traceback references frames; frames reference local variables. Saving exceptions for later inspection can therefore retain a large request, DataFrame, or batch even after the request function has returned.

```python
import traceback

saved_errors: list[BaseException] = []

def process() -> None:
    large_payload = bytearray(2_000_000)
    raise RuntimeError("bad record")

try:
    process()
except Exception as exc:
    saved_errors.append(exc)  # The exception/traceback may retain its frame.
```

If you need a durable error log, usually store structured metadata or a rendered traceback string rather than the live exception object. If live exception objects are required, define a retention limit and understand the references they preserve. Avoid assuming that the exception's message alone is the source of memory use.

### 4.5 Closures, tasks, threads, and `contextvars`

- **Closures:** a callback may capture a large local variable even if the callback only needs one small field. Capture the minimum required data.
- **Async tasks:** tasks that are never awaited, cancelled, or removed from a registry may keep coroutines and their locals alive. Inspect task ownership and shutdown behavior; use task names and explicit lifecycle management.
- **Threads:** a live thread retains its stack and locals; queues and thread-local state may retain payloads. Ensure workers terminate and queues are drained or bounded.
- **`contextvars`:** context-local values are useful for request metadata, but large objects placed in a context can remain alive as long as the context/task is retained. Store IDs or small immutable metadata rather than whole request objects.
- **Logging handlers:** repeatedly adding handlers during reloads or per-request setup can accumulate handlers, references, and duplicate output. Configure handlers at a deliberate application lifecycle boundary and remove them when their owner shuts down.

**Pitfall 4 — treating every growing cache as a bug.** A cache may be an intentional optimization. Determine expected cardinality, hit rate, eviction policy, value size, and lifecycle before changing it. A cache with a fixed number of entries can still retain a large amount of memory if entries contain large object graphs.

### 4.6 Temporary churn versus persistent retention

Use a repeated-workload experiment:

1. Start tracing before the workload.
2. Warm up once if imports and one-time setup are not the subject.
3. Record current traced bytes and RSS at a stable boundary.
4. Process one representative batch and allow expected temporary locals to leave scope.
5. Record again after the same cleanup/idle point.
6. Repeat several times with the same input size and shape.
7. Compare snapshots and object-lifetime probes.

Typical patterns:

| Observation across equivalent batch boundaries | Possible explanation | Next check |
|---|---|---|
| Peak rises during batch, current returns near baseline | Temporary allocation churn | Optimize peak if needed; check peak against limits |
| Traced current rises by roughly a repeatable amount per batch | Python objects may be retained | Compare snapshots; inspect roots/references |
| RSS rises, traced current is stable | Native memory, allocator retention/fragmentation, mappings, or other process memory | Check RSS source, native profiler, allocator behavior |
| Traced current falls, RSS stays high | Freed memory may remain in allocator arenas/pages or other resident allocations | Observe trend over time; do not infer a leak from RSS alone |
| Object count rises but bytes do not rise much | Many small objects or counting artifacts | Identify type and reference paths |
| Growth only appears with production concurrency | Queue/task accumulation, context retention, native buffers, or different input distribution | Reproduce concurrency and realistic data shape |

These are diagnostic patterns, not unique proofs. Different causes can produce the same graph.

## 5. Process-level measurements: `psutil` and `resource`

### 5.1 RSS with psutil

Install `psutil` in the project environment if it is not already present:

```bash
uv add --dev psutil
```

Then:

```python
import os
import psutil
import tracemalloc

tracemalloc.start(10)
process = psutil.Process(os.getpid())

def report(label: str) -> None:
    current, peak = tracemalloc.get_traced_memory()
    rss = process.memory_info().rss
    print(
        f"{label}: traced={current / 1024**2:.1f} MiB, "
        f"traced_peak={peak / 1024**2:.1f} MiB, "
        f"RSS={rss / 1024**2:.1f} MiB"
    )
```

Call `report()` at equivalent workload boundaries. RSS values are observations, not portable thresholds. The sampling call itself and tracing overhead can affect the measurement. Keep tracing and non-tracing runs distinct if you need to estimate tracing overhead.

### 5.2 `resource.getrusage`

The standard-library `resource` module is available on Unix-like platforms, but not universally on Windows. Its `ru_maxrss` field is a **maximum resident set size**, and units vary by operating system (commonly KiB on Linux, bytes on macOS). It is a high-water mark, not current RSS, so it cannot show memory falling after a batch.

```python
import resource
import sys

usage = resource.getrusage(resource.RUSAGE_SELF)
print("max RSS raw value:", usage.ru_maxrss)
print("platform:", sys.platform)
# Interpret ru_maxrss units using the documentation for this OS.
```

Use `psutil.Process().memory_info().rss` for current RSS when `psutil` is available; use `resource` when its platform-specific semantics suit the question. Neither replaces `tracemalloc`.

**Pitfall 5 — comparing incompatible metrics.** Do not compare `ru_maxrss` directly to current RSS, traced current bytes, or a container memory limit without checking units and accounting scope.

## 6. Intermediate: find surviving objects and their owners

### 6.1 `gc.get_objects()` is a view, not a universal heap census

`gc.get_objects()` returns objects tracked by the cyclic garbage collector. It does not include every Python object, and objects such as many atomic values may not be GC-tracked. Use it for object types and GC-tracked graphs, not as an exact total-object or total-memory measure.

```python
import gc
from collections import Counter

counts = Counter(type(obj).__name__ for obj in gc.get_objects())
for type_name, count in counts.most_common(15):
    print(type_name, count)
```

Take comparable measurements after equivalent workload boundaries. A count increase can be meaningful, but a different set of live application objects, test harness references, or GC tracking behavior can also change counts.

### 6.2 `gc.get_referrers()` requires care

`gc.get_referrers(obj)` lists objects found by the GC machinery that refer to `obj`. The result is not a complete ownership proof: it may include temporary diagnostic structures, frames, locals, or interpreter internals. The act of inspecting an object can itself create references.

```python
import gc

def show_referrer_types(obj: object) -> None:
    referrers = gc.get_referrers(obj)
    try:
        print([type(ref).__name__ for ref in referrers])
    finally:
        # This local list goes away on return; avoid retaining it globally.
        del referrers
```

Use this as a targeted probe after you have a candidate object. Do not print or traverse arbitrary object graphs from a production process without considering sensitive data, execution impact, and cycles.

### 6.3 `objgraph`

Install:

```bash
uv add --dev objgraph
```

Useful operations include:

```python
import objgraph

objgraph.show_growth(limit=10)
# After a representative workload:
objgraph.show_growth(limit=10)
```

`show_growth()` compares type counts with its prior baseline in that process. It can suggest which types grew, but it does not by itself prove why they survived or estimate their full retained bytes.

For a known suspect, `objgraph.show_backrefs([suspect], max_depth=4, filename="backrefs.png")` can generate a graph of objects referring back to the suspect. The exact graph may be large and may contain frames or infrastructure references; begin with a small depth and a minimal reproduction. Do not infer ownership from a graph without checking the application lifecycle.

### 6.4 Reference cycles are not the same as unbounded retention

Reference counting immediately releases an object when its strong reference count reaches zero. Cyclic GC handles certain unreachable cycles that reference counting alone cannot free. However, an object inside a cycle that remains reachable from a global registry is not garbage: the registry still owns it. Calling `gc.collect()` will not fix a global dictionary that intentionally retains the object.

Use `gc.collect()` in a test only when the test is specifically checking whether an unreachable cycle is collectible. It is not a general “clear memory” command and does not force the allocator to return resident pages to the OS. GC tuning belongs to Lesson 06; here the focus is on proving reachability and retention.

## 7. A systematic leak-hunting runbook

### Step 1 — establish the symptom and its unit

Record current traced memory, traced peak, current RSS, and workload counters (records processed, batches completed, queue depth, cache entries). Check whether growth is steady per batch, tied to input size, tied to concurrency, or only a one-time warm-up.

### Step 2 — reproduce safely

Use a repeatable fixture with controlled input size and distribution. Start with hundreds or thousands of rows, not multi-gigabyte input. Preserve the production path that matters, including callbacks, caching, and exception handling, but remove unrelated I/O when it obscures the retention question.

### Step 3 — establish a stable baseline

Start `tracemalloc` before constructing the workload. Run a warm-up if imports/initialization are not under investigation. Capture a baseline snapshot after warm-up and at a stable batch boundary.

### Step 4 — repeat equivalent batches

Take snapshots after each batch at the same phase. Compare each with the baseline and, where useful, with the preceding batch. Look for repeatable positive deltas and rising type counts. A single difference may reflect one-time initialization.

### Step 5 — trace the allocation and reference path

Use line/traceback statistics to identify allocation sites. Use `gc.get_objects()` and `objgraph` to identify growing types. Inspect candidate objects and their referrers in a minimal reproduction. Ask which root owns the object: global collection, cache, callback registry, task, traceback, context, or native buffer.

### Step 6 — state a falsifiable hypothesis

Example: “Each processed record is added to `EVENTS_BY_ID`; after batch completion, those entries are still reachable from the module global. If the global insertion is removed or the registry is bounded, the per-batch positive traced-memory delta and object count should disappear while output counts remain unchanged.”

Avoid hypotheses such as “Python GC is bad” or “RSS is too high”; they do not identify a cause.

### Step 7 — fix the retention cause

Make the smallest behavior-preserving change. Do not clear all state if downstream code requires it. For caches, define an explicit capacity and invalidation policy. For tasks/threads/listeners, define who owns and closes them. For exceptions, retain summaries rather than traceback-bearing objects unless live exceptions are necessary.

### Step 8 — verify correctness and object lifetime

Run existing tests and edge cases. Where appropriate, use `weakref.ref()` to check that an object becomes collectible after the owning lifecycle ends. Take new snapshots across the same repeated workload. Confirm the expected growth trend changed, not merely one noisy RSS reading.

### Step 9 — assess residual memory and operational risk

If traced memory stabilizes but RSS remains high, investigate allocator behavior, native allocations, mappings, and container limits. If Python tracing does not explain the growth, use the dedicated native allocation tools covered in Lesson 05 (Memray) or library-specific diagnostics.

### Step 10 — document the evidence

Record the workload, Python version/build, OS/container limits, tracing settings, batch counts, traced current/peak, RSS, top snapshot deltas, fix, correctness checks, and known limitations. Keep raw numbers tied to the exact environment and avoid universal claims.

## 8. Three roadmap-aligned leak investigations

The following examples are standalone teaching experiments. Their code is provided for execution; output is not claimed as executed unless you run it. Run each in a fresh process when comparing memory behavior, because global caches and allocator history can affect observations.

### Investigation A — accumulating global dictionary

**Defect:** a module-level dictionary retains every event even though downstream processing only needs the current batch.

```python
# global_registry_demo.py
import gc
import tracemalloc
import weakref

class Event:
    def __init__(self, event_id: int, payload: bytes) -> None:
        self.event_id = event_id
        self.payload = payload

REGISTRY: dict[int, Event] = {}

def process_batch(batch_id: int, retain: bool) -> None:
    events = [
        Event(batch_id * 1_000 + i, b"x" * 1_024)
        for i in range(1_000)
    ]
    # Imagine validation and aggregation occur here.
    _ = sum(event.event_id for event in events)
    if retain:
        REGISTRY.update((event.event_id, event) for event in events)

tracemalloc.start(10)
process_batch(0, retain=False)
baseline = tracemalloc.take_snapshot()

for batch in range(1, 6):
    process_batch(batch, retain=True)
    current, peak = tracemalloc.get_traced_memory()
    print(batch, round(current / 1024**2, 2), round(peak / 1024**2, 2))

after = tracemalloc.take_snapshot()
for stat in after.compare_to(baseline, "lineno")[:8]:
    print(stat)
```

**Interpretation:** `REGISTRY` is an explicit strong-reference root. Removing the local `events` variable at function exit cannot release events still referenced by `REGISTRY`. The per-batch object count and traced current memory should rise while the registry accumulates distinct keys.

**Fix:** if the registry is not part of required behavior, remove it; if it is a current-batch index, create it inside the batch scope or clear it after all consumers finish; if it must persist, define a retention policy or move durable records to storage. Re-run correctness tests to ensure downstream consumers do not depend on the accidental global lifetime.

**Weak-reference probe:** use a single known event in a test, remove all intended strong references, and assert its weak reference is dead. Do not assert that every event is collectible if the test itself still holds a reference.

### Investigation B — `lru_cache` retains instances

**Defect:** a cached instance method includes `self` in the cache key. The wrapper can retain instances beyond their intended lifetime.

```python
# cached_method_demo.py
from functools import lru_cache
import gc
import weakref

class Parser:
    def __init__(self, name: str) -> None:
        self.name = name

    @lru_cache(maxsize=None)
    def parse_key(self, key: str) -> str:
        return f"{self.name}:{key}"

def demonstrates_retention() -> bool:
    parser = Parser("batch-1")
    ref = weakref.ref(parser)
    assert parser.parse_key("customer_id") == "batch-1:customer_id"
    del parser
    gc.collect()
    # Expected True while the cached wrapper still holds the instance.
    return ref() is not None

if __name__ == "__main__":
    print("instance retained by cache:", demonstrates_retention())
    Parser.parse_key.cache_clear()
    gc.collect()
```

The printed expectation describes the logic; execute it to verify in your interpreter. The cached method wrapper is attached to the class function, and `self` is a cache argument. The cache's strong reference to its key can keep the instance alive.

**Fix options:** remove the cache if the function is cheap; use a bounded cache if the number and size of entries must be controlled; cache immutable data independently of the instance when semantics allow; or design a per-instance cache with a deliberate lifecycle. Merely changing `maxsize=None` to a finite value bounds entry count but may still retain instances until eviction.

**Regression test:** prefer asserting lifetime behavior over exact bytes.

```python
import gc
import weakref

def test_parser_lifetime_after_cache_clear() -> None:
    parser = Parser("temporary")
    ref = weakref.ref(parser)
    parser.parse_key("id")
    del parser

    gc.collect()
    assert ref() is not None  # The known defect retains it.

    Parser.parse_key.cache_clear()
    gc.collect()
    assert ref() is None
```

This test intentionally codifies the defect so that the retention mechanism is visible. After redesigning the cache, replace it with a test that expects collection without global cache clearing. Always clear shared caches between tests to prevent order dependence.

### Investigation C — a retained traceback keeps frame locals alive

**Defect:** storing a live exception object can keep its traceback and frame locals reachable.

```python
# traceback_retention_demo.py
import gc
import weakref

SAVED_EXCEPTIONS: list[BaseException] = []

class Payload:
    def __init__(self) -> None:
        self.data = bytearray(500_000)

def fail_with_payload(probe: list[weakref.ReferenceType[Payload]]) -> None:
    payload = Payload()
    probe.append(weakref.ref(payload))
    raise RuntimeError("synthetic processing failure")

def run_defect() -> bool:
    probe: list[weakref.ReferenceType[Payload]] = []
    try:
        fail_with_payload(probe)
    except RuntimeError as exc:
        SAVED_EXCEPTIONS.append(exc)
    gc.collect()
    return probe[0]() is not None

if __name__ == "__main__":
    print("payload retained by saved exception:", run_defect())
    SAVED_EXCEPTIONS.clear()
    gc.collect()
```

The exception's traceback references the frame in `fail_with_payload`; that frame's local `payload` can remain reachable. The weak reference lets the test observe the payload without itself retaining it. The exact timing of collection depends on references and implementation details, so execute the example rather than treating an unrun output as evidence.

**Fix:** store a rendered traceback or structured error fields instead of the live exception if that meets the requirement. If live exceptions are needed, bound their retention and clear references when diagnosis is complete.

```python
import traceback

ERROR_SUMMARIES: list[str] = []

try:
    fail_with_payload([])
except RuntimeError as exc:
    ERROR_SUMMARIES.append("".join(
        traceback.format_exception(type(exc), exc, exc.__traceback__)
    ))
    # Do not append `exc` itself to a long-lived collection.
```

The rendered string can still be large, so bound the log/error store too. The fix changes what is retained; it does not eliminate the cost of retaining an unlimited number of traceback strings.

## 9. Memory-aware design patterns

### 9.1 Generators and chunking

If the next stage can consume records incrementally, avoid materializing all rows at once.

```python
import csv
from collections.abc import Iterator

def read_events(path: str) -> Iterator[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as handle:
        yield from csv.DictReader(handle)

def process_file(path: str) -> int:
    count = 0
    for event in read_events(path):
        # Validate and aggregate the current record; do not append it
        # to a global list unless the full collection is required.
        count += 1
    return count
```

Generators reduce the need to retain all parsed rows simultaneously, but they do not make the entire pipeline streaming automatically. A downstream `list(read_events(path))`, a large aggregation dictionary, or an unbounded queue can still dominate memory.

### 9.2 Bounded queues and backpressure

A producer that outpaces consumers can turn a queue into a memory sink. Use bounded queues, apply backpressure when full, and define what happens when consumers fail. Queue capacity should be chosen using the payload size distribution and memory budget, not an arbitrary universal number.

### 9.3 `__slots__`

`__slots__` can reduce per-instance overhead for classes that otherwise use an instance `__dict__`, but the benefit depends on inheritance, weak-reference needs, and the class layout. It does not fix unbounded retention. Use it only after measuring object count and memory and after checking compatibility with dynamic attributes and weak references.

### 9.4 Weak references

Weak references are appropriate for non-owning indexes, observers, or caches where it is acceptable for entries to disappear when the object has no other strong owner. They are not a substitute for lifecycle design: a weak cache can have unexpected misses, and a weak-key mapping's value must not strongly reference its key indirectly if that would defeat the purpose.

### 9.5 Bounded caches

Choose bounds by an explicit operational objective: maximum entries, approximate bytes, TTL, or workload-specific eviction. Entry-count bounds are not byte bounds. Track cache size, hit/miss rate, eviction count, and retained value types. Test invalidation and correctness under eviction.

For a time-to-live cache, `cachetools.TTLCache` provides both a maximum cache size and a per-item TTL. Install it only if the project needs this dependency:

```bash
uv add cachetools
```

Use `uv add --dev cachetools` instead if the dependency is needed only for local experiments or tests and is not imported by the application at runtime.

```python
from cachetools import TTLCache

# Default getsizeof behavior counts each entry as size 1, not its bytes.
recent_results: TTLCache[str, str] = TTLCache(maxsize=1_000, ttl=300)
recent_results["customer:42"] = "validated"

if "customer:42" in recent_results:
    print(recent_results["customer:42"])
```

With the default sizing function, `maxsize=1_000` limits the number of entries, not total retained bytes. TTL expiry is time-based, not an exact memory budget; expired entries are removed during cache operations and can also be explicitly expired with the cache's `expire()` method. Check the installed `cachetools` version's API and choose a custom `getsizeof` only if an approximate application-specific size is meaningful. Even a custom size estimate does not equal process RSS.

## 10. Advanced: deep size, object layout, and allocator behavior

### 10.1 Pympler for deep-size estimates

Install Pympler when you need an estimate of a Python object graph's size:

```bash
uv add --dev pympler
```

```python
from pympler import asizeof

example = [{"id": i, "tags": ["etl", "event"]} for i in range(100)]
print("shallow list bytes:", __import__("sys").getsizeof(example))
print("deep estimate bytes:", asizeof.asizeof(example))
```

`asizeof.asizeof()` recursively estimates the size of reachable objects according to Pympler's rules and attempts to avoid double-counting shared objects. Treat the result as a tool-specific estimate, not a guaranteed amount of RSS that will be released by deleting the root. Shared references, extension types, external buffers, and native allocations complicate any universal “deep size.”

### 10.2 Object layout and allocation arenas

A Python object has implementation-specific metadata and storage. Lists and dictionaries reserve space for references or table entries; separate referenced objects have their own overhead. Small allocations may be served from Python's allocator pools/arenas, while other memory is obtained through system allocators or native libraries.

Freeing Python objects does not guarantee that RSS immediately decreases. An allocator may keep freed blocks available for reuse, a page may still contain other live objects, memory may be fragmented, or native libraries may retain their own pools. This is not automatically a leak. Observe whether the live traced allocations and object populations stabilize over repeated equivalent workloads.

Platform-specific tools and tuning such as `malloc_trim`, `MALLOC_ARENA_MAX`, jemalloc, or mimalloc are outside the first-line fix and have portability and operational trade-offs. Do not prescribe them merely because RSS remains high.

### 10.3 Native allocations and NumPy/pandas buffers

`tracemalloc` may not account for all memory allocated directly by native code. NumPy arrays and pandas objects may own or share buffers outside the Python object header. A small view can keep a much larger base array alive because the view references its base buffer. Copying a view can sometimes release the original buffer after all other references disappear, but copying also temporarily increases memory and must be justified by measured lifetime and workload behavior.

Diagnostic path when RSS rises but traced memory does not explain it:

1. Confirm the measurement interval and input/concurrency are equivalent.
2. Check Python-level object counts and snapshots for obvious retention.
3. Inspect library-specific buffer ownership and whether views retain base arrays.
4. Check memory maps, native caches, and allocator behavior.
5. Use Memray/native allocation analysis (Lesson 05) if needed; do not expand `tracemalloc` beyond what it can observe.

## 11. Advanced: copy-on-write and fork

On Unix-like systems that support `fork`, a child initially shares many parent memory pages through copy-on-write. When either process writes to a shared page, the operating system can create a private copy for that process. Python reference-count updates and ordinary object mutation can dirty pages, so a worker may gradually lose sharing even if the logical data structures appear unchanged.

The actual effect depends on operating system, Python build/version, object graph, workload, allocator, and fork model. Python 3.12 introduced immortal-object behavior for selected objects, which can reduce some reference-count writes for those objects; it does **not** make all Python memory immutable or guarantee copy-on-write sharing. `gc.freeze()` is a specific GC technique discussed in the dedicated GC lesson; it is not a general memory deduplication switch and does not prevent arbitrary writes from dirtying pages.

Use `fork`-related optimization only after measuring worker RSS/PSS and understanding the process model. Consider `spawn` where platform/runtime constraints or safety requirements make it appropriate, while accounting for serialization and startup costs. Do not assume that numbers from Linux `fork` behavior transfer to macOS, Windows, containers, or a different Python build.

## 12. Production monitoring, budgets, and incident response

### 12.1 What to monitor

For long-running pipelines, collect a small set of signals at meaningful boundaries:

- RSS/current process memory and, where available, container/cgroup memory usage and limit.
- Traced current/peak memory in controlled diagnostics, not necessarily on every production request.
- Batch count, records processed, queue depth, active tasks/workers, cache entries, and retry/error counts.
- Memory growth slope across equivalent batches or requests.
- Restart count, OOM-kill events, and time to reach a memory budget.

A memory budget should include headroom for input-size variation, concurrency, temporary peaks, native buffers, and process/runtime overhead. A container limit is a hard operational constraint, not a safe target to consume fully.

### 12.2 Production incident decision tree

```text
Memory alert
|
+-- Is the metric current RSS, peak RSS, traced current, or container usage?
|   +-- Unknown -> clarify metric, unit, and scope first.
|
+-- Does traced current grow across equivalent batch boundaries?
|   +-- Yes -> compare snapshots; inspect allocation sites and retaining roots.
|   +-- No  -> inspect native allocations, mappings, allocator retention, and workload changes.
|
+-- Do object counts / cache entries / queue depth grow with each batch?
|   +-- Yes -> inspect registry, cache, task, callback, traceback, and queue ownership.
|   +-- No  -> inspect large buffers, native libraries, allocator behavior, and input/concurrency differences.
|
+-- After a fix, do correctness and lifetime tests pass?
    +-- No -> restore behavior; refine ownership/lifecycle fix.
    +-- Yes -> repeat equivalent workload; verify growth trend and memory budget.
```

This tree narrows the investigation; it does not replace incident-specific judgment. Avoid dumping arbitrary object graphs from a live process if the operation can block the service or expose sensitive data.

### 12.3 Memory regression tests

Prefer deterministic lifecycle probes and repeated-workload trends over exact RSS assertions.

Good candidates:
- a weak reference becomes dead after the documented owner is released;
- a cache entry count stays within its specified bound;
- a registry contains only the current batch after cleanup;
- repeated batches produce equivalent outputs and do not cause a steadily rising count of retained domain objects;
- `tracemalloc` current bytes remain within a broad, justified budget in a pinned environment.

Avoid brittle tests such as `assert rss < 50_000_000` on every OS or `assert traced_bytes == 123456`. Allocator versions, Python builds, test runners, native libraries, and OS page accounting vary. If using a byte threshold, pin the environment, include margin, compare the same measurement phase, and test trends rather than one noisy observation.

Example object-lifetime test:

```python
import gc
import weakref

class BatchRecord:
    pass

def make_record_ref() -> weakref.ReferenceType[BatchRecord]:
    record = BatchRecord()
    return weakref.ref(record)

def test_record_is_not_retained_after_owner_releases_it() -> None:
    ref = make_record_ref()
    gc.collect()  # relevant if the object graph could contain an unreachable cycle
    assert ref() is None
```

This checks object lifetime, not RSS. The explicit `gc.collect()` is not required for an acyclic object with no remaining strong references under CPython's reference counting, but can make a test that intentionally includes cycles more deterministic. Do not call it indiscriminately in production code.

A repeated-trend test can be useful but should not rely on a single exact number:

```python
import tracemalloc

def traced_after_batches(run_batch, batches: int = 5) -> list[int]:
    tracemalloc.start(10)
    try:
        run_batch()  # warm-up
        measurements = []
        for _ in range(batches):
            run_batch()
            current, _ = tracemalloc.get_traced_memory()
            measurements.append(current)
        return measurements
    finally:
        tracemalloc.stop()
```

This helper only measures current traced bytes; it does not prove a leak by itself. The caller must ensure that `run_batch` uses equivalent inputs and does not intentionally retain output between iterations. In a test, assert a trend or broad budget justified by a known workload and pinned environment, and pair it with a specific lifetime probe for the suspected owner.

## 13. Troubleshooting guide

| Symptom | Likely explanations | What to do next |
|---|---|---|
| `tracemalloc` current increases every batch | Persistent Python references, retained outputs, cache growth, traceback retention | Compare snapshots at equal boundaries; inspect registry/cache/exception roots |
| `tracemalloc` peak is high but current is stable | Large temporary lists/frames/serialization buffers | Stream or chunk; reduce simultaneous intermediates; measure peak |
| RSS rises but traced current is flat | Native allocations, allocator fragmentation, mapped files, native library caches, different workload | Check library buffers and mappings; use native allocation tooling |
| RSS does not fall after a fix | Allocator retained pages, live objects elsewhere, high-water metric used by mistake | Check current RSS vs max RSS; repeat workload; inspect object/snapshot trend |
| Snapshot shows a large positive line | Many allocations are live from that allocation path | Inspect traceback and owning references; determine whether retention is intended |
| `gc.collect()` changes little | Objects remain strongly reachable or memory is retained by allocator/native code | Find roots; do not keep forcing collections |
| Weakref test fails unexpectedly | A local, cache, closure, exception, test fixture, or referrer still owns the object | Reduce to a fresh-process reproduction and inspect reference paths |
| Memory grows only under concurrency | Queues, tasks, context variables, thread locals, buffers, or backpressure failure | Bound work in flight; measure queue depth and active tasks; reproduce concurrency |

## 14. Common mistakes

1. **Using `sys.getsizeof()` as total retained memory.** It is shallow; inspect the graph and shared references.
2. **Calling a rise in RSS a Python leak.** RSS includes native and allocator effects; correlate it with traced current, object counts, and workload metrics.
3. **Taking snapshots at different phases.** Compare after the same batch/cleanup boundary.
4. **Starting tracing too late.** Earlier allocations have no recorded traceback history.
5. **Assuming a large positive snapshot delta is automatically a bug.** Decide whether those objects should remain alive.
6. **Running `gc.collect()` as a universal fix.** It cannot free objects still strongly referenced and does not guarantee RSS release.
7. **Using `gc.get_objects()` as a complete heap inventory.** It reports GC-tracked objects, not every object or every byte.
8. **Using weak references without checking ownership semantics.** An object may disappear earlier than the application expects, or a strong reference may remain elsewhere.
9. **Retaining exception objects for logging.** Tracebacks can keep frames and large local variables alive.
10. **Treating `lru_cache(maxsize=N)` as a byte budget.** It bounds entries, not the size of each retained object graph.
11. **Asserting exact RSS in portable tests.** Prefer lifecycle assertions and broad environment-specific trends.
12. **Claiming a fix worked after one reading.** Repeat equivalent batches and verify correctness, object lifetime, and the growth slope.

## 15. Exercises

### Exercise 1 — snapshot reading
Create a list of records, take a snapshot, release it, and take another snapshot. Explain why positive and negative deltas may both appear and why the result is not a complete history of allocations.

### Exercise 2 — distinguish churn from retention
Create one workload that builds a large temporary list and discards it, and another that appends each list to a global collection. Compare current and peak traced memory after each batch. Write down which measurements support the conclusion and what remains uncertain.

### Exercise 3 — cache lifecycle
Run the cached-method example. Prove which reference keeps the instance alive. Replace the cache strategy and write a test for the intended lifetime. Include a test that prevents global cache state from leaking between tests.

### Exercise 4 — traceback retention
Save exceptions from failed rows, compare object lifetime with storing formatted summaries, and ensure the error store itself is bounded. Preserve useful diagnostics without keeping entire batch frames unnecessarily.

### Exercise 5 — native-buffer diagnosis
Using NumPy or pandas if available, create a large base array and a small view. Drop the base variable and explain why the view may still retain the underlying buffer. Compare Python-level tracing with process memory, and clearly document what each tool can and cannot prove.

### Exercise 6 — bounded pipeline
Modify a batch processor to use a generator or chunked input and a bounded queue. Preserve row counts, error counts, ordering requirements, and aggregation results. Measure peak/current memory across repeated batches; do not assert a universal byte count.

### Exercise 7 — production runbook
Write a one-page runbook for a worker whose RSS grows while processing CSV logs. Include the metric and unit, reproduction plan, snapshot schedule, decision tree, rollback/containment action, and evidence required before declaring the incident resolved.

## 16. Self-check questions

1. What does `sys.getsizeof(obj)` include, and what does it omit?
2. What exactly is represented by a `tracemalloc` snapshot?
3. How do `get_traced_memory()` current and peak differ?
4. Why can `snapshot.compare_to()` show negative as well as positive deltas?
5. Why must snapshots be taken at equivalent workload boundaries?
6. How can a cached instance method retain an otherwise unused object?
7. How can an exception traceback retain a large local variable?
8. What are the limitations of `gc.get_objects()` and `gc.get_referrers()`?
9. Why might RSS remain high after traced Python allocations decrease?
10. What evidence would suggest native allocations rather than Python-level retention?
11. How do generators and backpressure help, and what can still cause an unbounded pipeline?
12. Why is a weak-reference probe often more reliable than an exact RSS assertion?
13. What version/platform factors complicate copy-on-write measurements after `fork`?
14. What is the difference between an object being unreachable and an object being absent from RSS?
15. What evidence is required to claim that a leak fix worked?

## 17. Hands-on task: `slowlog` memory investigation

Use the shared `slowlog` log-analysis/ETL script from Module 1.17. The project is deliberately inefficient and includes a hot loop and a memory-retention defect. Do not replace the whole application; isolate and document one retention cause.

### Deliverables

1. **Reproducible workload:** generate or select representative CSV/log input. Start with a small dataset and scale only after the behavior is understood.
2. **Baseline report:** record Python version/build, OS/container limits, input rows/size, batch size, concurrency, cache/registry counts, traced current/peak, RSS, and measurement boundaries.
3. **Repeated-run experiment:** process equivalent batches several times, taking snapshots after the same cleanup boundary. Compare baseline and subsequent snapshots by line and traceback.
4. **Retention hypothesis:** identify a specific root, such as a global dictionary, unbounded cache, listener registry, task, or saved exception. Support it with a reference/lifetime probe.
5. **Behavior-preserving fix:** correct the retention lifecycle, use streaming/chunking where appropriate, or bound the structure. Do not remove data that is required by output semantics.
6. **Regression tests:** preserve output row/error/aggregation counts; add an object-lifetime or bounded-cardinality assertion; use a memory budget only if it is justified for the test environment.
7. **Verification:** rerun the exact workload and measurement procedure after the fix. Show whether traced current stabilizes and explain any RSS residual.
8. **Report:** save `PERF_REPORT.md` with the hypothesis, environment, workload, methodology, snapshots, reference evidence, fix, correctness results, limitations, and what remains unexplained.

### Acceptance criteria

- The bug is demonstrated by repeatable evidence, not just a single RSS sample.
- The retaining reference or ownership failure is identified.
- Output correctness remains unchanged, or any intentional semantic change is explicitly justified.
- A regression test covers the lifecycle or bound.
- The post-fix repeated workload shows the expected trend change.
- Any unexplained RSS or native memory is stated honestly; do not claim `tracemalloc` explains memory it does not observe.
- Memray is used only if evidence points toward native allocations or additional allocation attribution is needed. GC tuning is deferred to Lesson 06 unless cycle collectability is central to the specific diagnosis.

## 18. Reproducible memory-investigation report template

Copy this into `PERF_REPORT.md` and complete every section.

```markdown
# Memory Investigation — [workload / incident]

## 1. Summary
- Symptom:
- User/operational impact:
- Hypothesis:
- Root cause (confirmed / likely / unresolved):
- Fix:
- Verification status:

## 2. Environment
- Python version and implementation:
- Python build (debug/free-threaded/other relevant flags):
- OS, architecture, container/runtime:
- Container memory limit and observed OOM behavior:
- Dependencies/native libraries:
- Git commit/configuration:

## 3. Workload
- Input format, row count, bytes, shape/distribution:
- Batch size and number of repetitions:
- Concurrency / active tasks / queue bounds:
- Cache, registry, and handler cardinalities:
- Warm-up and cleanup procedure:

## 4. Measurement method
- `tracemalloc` start point and traceback depth:
- Snapshot boundaries:
- Metrics: traced current/peak, RSS, object counts, queue/cache counts:
- Units and collection interval:
- Instrumentation overhead/limitations:
- Reproduction command:

## 5. Baseline evidence
- Current/peak traced memory per batch:
- Current RSS per batch and metric source:
- Snapshot deltas by line/traceback:
- Growing object types:
- Candidate retaining reference path:
- Correctness outputs:

## 6. Root-cause reasoning
- Expected object lifetime:
- Actual retaining owner/root:
- Evidence that distinguishes retention from churn:
- Alternative explanations considered:

## 7. Change
- Code/configuration change:
- Why it fixes the ownership/lifecycle cause:
- Behavior and compatibility risks:
- Rollback/containment plan:

## 8. Verification
- Tests and commands run:
- Output equivalence:
- Weak-reference/lifecycle/bound assertions:
- Post-fix current/peak traced memory:
- Post-fix RSS and residual explanation:
- Repetitions and trend:
- Regression guard added:

## 9. Limitations and conclusion
- What the evidence proves:
- What it does not prove:
- Native/allocator uncertainty:
- Production monitoring follow-up:
- Decision: resolved / mitigated / needs further investigation
```

## 19. Completion checklist

- [ ] I can distinguish shallow size, retained graph size, traced memory, and RSS.
- [ ] I can start `tracemalloc`, take snapshots, compare by line/traceback, and interpret current/peak bytes.
- [ ] I can reproduce growth across equivalent workload boundaries.
- [ ] I can identify strong-reference roots in globals, caches, callbacks, exceptions, tasks, threads, and contexts.
- [ ] I can use `psutil`, `resource`, `gc`, weak references, and `objgraph` with their limitations understood.
- [ ] I can explain why RSS may remain high after Python objects are released.
- [ ] I can write lifecycle-focused leak regression tests without brittle exact-RSS assertions.
- [ ] I completed the `slowlog` investigation and wrote a reproducible `PERF_REPORT.md`.

**Next lesson:** `05-memray-and-allocation-analysis.md` — use native allocation tracing when Python-level snapshots do not explain the process-memory evidence.

## Documentation references

- Python 3.12 `tracemalloc`: https://docs.python.org/3.12/library/tracemalloc.html
- Python 3.12 `sys.getsizeof`: https://docs.python.org/3.12/library/sys.html#sys.getsizeof
- Python 3.12 `gc`: https://docs.python.org/3.12/library/gc.html
- Python 3.12 `resource` (Unix availability and `getrusage`): https://docs.python.org/3.12/library/resource.html
- Python 3.12 `weakref`: https://docs.python.org/3.12/library/weakref.html
- `cachetools.TTLCache`: https://cachetools.readthedocs.io/en/latest/
- Pympler `asizeof`: https://pympler.readthedocs.io/en/latest/library/asizeof.html
- `objgraph`: https://mg.pov.lt/objgraph/

Check the documentation version matching the interpreter and dependency installed in the environment. The external references validate API behavior; the module roadmap remains authoritative for lesson scope and sequence.

