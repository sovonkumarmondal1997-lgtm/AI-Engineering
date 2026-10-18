# Garbage-Collector Tuning and Reference Cycles

> **Module:** Stage 1 — Programming & Computational Thinking  
> **Lesson:** 06 of 09 in Module 1.17, *Profiling, Memory and Runtime Performance*  
> **Target:** Python 3.12+; version-specific behavior is called out where it matters  
> **Core rule:** measure first, change one variable, verify correctness and operational impact, and keep a rollback path.

---

## 1. Why this lesson exists

A Python process can release most objects promptly and still retain memory because a group of objects refers to one another. It can also experience latency spikes when the cyclic collector scans a large object graph. These are different problems:

- **Object lifetime:** when does an object become unreachable, and what keeps it alive?
- **Cycle reclamation:** can the runtime find unreachable objects whose references keep one another alive?
- **Memory footprint:** how much memory is retained by live objects, allocator arenas, native buffers, and fragmentation?
- **Latency:** when does collection run, how much work does it perform, and does that work land on a request or batch critical path?

The aim is not to make garbage collection run as rarely as possible. The aim is to understand the lifetime graph, remove accidental retention, and tune the collector only when measurements show that its work is a material part of the problem.

This lesson follows the Module 1.17 roadmap: CPU profiling and benchmarking (lessons 01–03), memory tracing (04), allocation analysis (05), cyclic GC and reference cycles (this lesson), then CPython performance idioms (07) and native-code integration (08–09). It uses the shared, deliberately inefficient **slowlog** log-analysis/ETL workload as a practical investigation context. It does not replace the earlier object-model and garbage-collection material or turn into a general allocation-profiler tutorial.

## 2. Prerequisites

You should already be comfortable with:

- Python variables, names, objects, containers, classes, attributes, and mutability.
- Big-O reasoning and choosing appropriate data structures.
- Generators and the difference between streaming and materialising a workload.
- `__slots__`, descriptors, `weakref`, and context managers.
- Exceptions, tracebacks, iterators, and basic `asyncio` concepts.
- `time.perf_counter()`, repeated benchmarks, and the rule to measure before optimizing.
- `tracemalloc` snapshots and process RSS from lessons 04–05.

### Learning objectives

After this lesson, you should be able to:

1. Distinguish CPython reference counting from its cyclic garbage collector.
2. Construct a reference cycle, prove that it is unreachable, and observe its collection without depending on destructor timing.
3. Use the public `gc` and `weakref` APIs without assuming a particular collection schedule.
4. Explain generations, thresholds, finalization, traceback retention, and the limits of `gc.garbage`.
5. Measure collection frequency and duration with `gc.callbacks`, `gc.get_stats()`, and a controlled experiment.
6. Evaluate threshold changes, explicit collection, `gc.freeze()`, and collector disabling against latency, throughput, memory, and correctness.
7. Recognize copy-on-write, free-threaded, immortal-object, and C-extension considerations that make runtime behavior version/build dependent.

---

## 3. The two mechanisms: reference counting and cyclic GC

### 3.1 Reference counting: prompt disposal when the count reaches zero

In ordinary GIL-enabled CPython builds, most objects participate in reference counting. References can be held by:

- local variables and evaluation-stack values;
- attributes and container elements;
- module globals, closures, and function defaults;
- other Python objects;
- C-extension fields and C variables that own a reference.

When a reference is acquired or released, CPython updates the relevant ownership accounting. When an object's effective reference count reaches zero, CPython can deallocate it immediately. Deallocation may release references to other objects, causing a cascade.

```python
class Probe:
    def __del__(self):
        print("finalizer called")

item = Probe()
alias = item                 # another strong reference
del item                     # alias still keeps the object alive
print("still reachable")
del alias                    # in ordinary CPython, finalization normally occurs now
```

This example demonstrates common CPython behavior, not a language-wide promise that `__del__` runs at an exact point. Avoid correctness logic that depends on immediate finalization, and do not use `__del__` as a substitute for explicit resource management.

`sys.getrefcount(obj)` can be useful for demonstrations, but it returns a count that includes a temporary reference used by the call and is not a reliable production leak detector. Do not build tests around exact reference-count numbers. Free-threaded CPython builds can use reference-counting strategies that make a raw count less directly interpretable and can defer some deallocation.

### 3.2 Why a reference cycle survives reference counting

Consider two objects:

```text
local variable ──► A ──► B
                   ▲     │
                   └─────┘
```

After the local variable is removed, `A` and `B` still point at each other. Their internal references keep their reference counts nonzero even though no live root can reach either object. Reference counting alone cannot prove that the group is unreachable.

CPython's **cyclic garbage collector** supplements reference counting. It examines tracked container objects, determines which references are internal to a candidate group, and identifies groups that are not reachable from live roots. It can then clear the cycle so the objects can be reclaimed.

Important distinctions:

- Reference counting is the primary lifetime mechanism in CPython; it handles most short-lived objects without a cyclic-GC scan.
- The cyclic collector is additional machinery for unreachable cycles and, in some free-threaded implementation details, delayed reference-count cases.
- A reachable cycle is **not** garbage. If a global registry still points to one node, that node and everything reachable from it must remain alive.
- Not every Python object is tracked by cyclic GC. Simple atomic objects such as many integers and strings do not need graph traversal. `gc.is_tracked()` is an inspection aid, not a stable application-level contract.
- A high RSS value does not prove a cycle exists. Allocator arenas, native allocations, large buffers, and fragmentation can keep RSS high after Python objects are released.

### 3.3 Runnable two-object cycle and weak-reference proof

The following example uses a weak reference so the observer does not itself keep the target alive. It deliberately avoids `__del__`, so the demonstration is about reachability and collection rather than finalizer ordering.

```python
import gc
import weakref


class Node:
    def __init__(self, name):
        self.name = name
        self.peer = None


def make_unreachable_cycle():
    left = Node("left")
    right = Node("right")
    left.peer = right
    right.peer = left
    observer = weakref.ref(left)
    return observer  # local strong references to both nodes leave scope


# Disable only automatic collection for this short demonstration so the
# pre-collection observation is deterministic. Explicit gc.collect() still works.
was_enabled = gc.isenabled()
gc.disable()
try:
    observer = make_unreachable_cycle()
    print("before explicit collection:", observer() is not None)
finally:
    if was_enabled:
        gc.enable()

collected = gc.collect()
print("gc.collect() reported:", collected)
print("after explicit collection:", observer() is None)
```

The temporary disable makes the before/after observation deterministic for this isolated CPython demonstration; it is not a production tuning recommendation. If automatic GC was already disabled, the example preserves that state. The explicit full collection should reclaim the unreachable cycle, and the weak reference should then return `None`. The exact `collected` integer can vary with Python version and surrounding process activity; test the semantic condition (`observer() is None`), not a magic count.

Notes:

- The local `observer` is weak: it does not increment the target's strong reference count.
- Calling `observer()` temporarily returns a strong reference if the target is still alive. Avoid holding that result while trying to prove collection.
- Other runtimes may schedule collection differently. `gc.collect()` is the deliberate request for a collection, but exact object-finalization timing should not be treated as portable.
- Do not use `id()` as a lifetime proof. IDs may be reused after an object is destroyed.

### 3.4 A reachable cycle is not a leak

```python
import gc

registry = {}

class Node:
    def __init__(self, name):
        self.name = name
        self.peer = None

a, b = Node("a"), Node("b")
a.peer, b.peer = b, a
registry["root"] = a

gc.collect()
assert registry["root"].peer.peer is registry["root"]
# The cycle is reachable from registry; collection must not reclaim it.

del registry["root"]
del a, b
gc.collect()
```

The first graph is intentionally live. The second is unreachable and can be reclaimed. A leak investigation should look for the **root path** retaining objects, not simply search for cycles.

---

## 4. The `gc` module: inspect before changing anything

The `gc` module exposes the cyclic collector's controls and diagnostics.

| API | What it tells you / does | Caveat |
| --- | --- | --- |
| `gc.collect()` | Requests a collection; with no argument, requests a full collection. Returns the number of objects collected plus objects found uncollectable by the collector. | Calling it while a collection is already in progress has undefined effects. Do not call it recursively from a GC callback. |
| `gc.get_count()` | Returns a three-item tuple of collector counters. | These are implementation counters, not live-object counts or a memory measurement. |
| `gc.get_threshold()` | Returns the current collection thresholds. | Defaults and the interpretation of individual entries vary by version/build. Read the current runtime. |
| `gc.set_threshold(...)` | Changes automatic collection thresholds. | Treat as a process-wide runtime policy change within that interpreter; restore the old values during experiments. |
| `gc.enable()` / `gc.disable()` / `gc.isenabled()` | Enables/disables automatic cyclic collection. | Disabling the cyclic collector does not turn off reference counting, but unreachable cycles can accumulate. |
| `gc.get_stats()` | Returns per-generation dictionaries of collection counts and outcomes. | Shape and generation semantics are version-dependent; take before/after deltas. |
| `gc.callbacks` | Lets code observe collection start and stop. | Callbacks execute on the collection path; keep them tiny, defensive, and non-blocking. |
| `gc.garbage` | Holds certain objects found uncollectable under relevant debug settings / legacy conditions. | It is not a list of all live cycles or all leaks. |
| `gc.get_referrers(obj)` | Returns objects that directly refer to `obj`. | The returned list and debugger locals create references; results can include temporary/internal objects. Use only for diagnosis. |
| `gc.set_debug(flags)` | Enables diagnostic output/retention behavior. | Debug flags can produce large output and retain objects; always restore previous flags. |
| `gc.freeze()` / `gc.unfreeze()` | Moves currently tracked objects into a permanent generation that ordinary collections do not revisit. | Primarily useful for specific lifecycle patterns such as pre-fork workers; it does not fix leaks. |

Basic inspection:

```python
import gc
import sys

print("implementation:", sys.implementation.name)
print("version:", sys.version)
print("GC enabled:", gc.isenabled())
print("counts:", gc.get_count())
print("thresholds:", gc.get_threshold())
print("stats:", gc.get_stats())
print("tracked list:", gc.is_tracked([]))
print("tracked tuple:", gc.is_tracked((object(),)))
```

Do not copy a threshold tuple from a blog post and assume it applies. Log the interpreter version, build type, operating system, allocator, and actual thresholds with every performance report.

### 4.1 Interpreting `get_count()` and `get_stats()`

`gc.get_count()` is a snapshot of collector bookkeeping counters. It is not “the number of objects in each generation,” nor is it the number of bytes allocated. It can be useful for observing whether allocation pressure is approaching a trigger, but its meaning depends on the collector implementation.

`gc.get_stats()` returns dictionaries that include counters such as `collections`, `collected`, and `uncollectable`. These are cumulative since interpreter startup. Compare snapshots around a bounded workload:

```python
import gc

def run_workload():
    # Representative placeholder: replace with the bounded workload under study.
    transient = [{"value": i} for i in range(10_000)]
    return len(transient)


before = gc.get_stats()
run_workload()
after = gc.get_stats()

for index, (old, new) in enumerate(zip(before, after)):
    print(
        index,
        "collections:", new.get("collections", 0) - old.get("collections", 0),
        "collected:", new.get("collected", 0) - old.get("collected", 0),
        "uncollectable:", new.get("uncollectable", 0) - old.get("uncollectable", 0),
    )
```

Use `zip()` rather than assuming the same generation structure on every Python version. In current mainstream GIL-enabled CPython, the returned shape commonly has three entries, but the generation model has changed in recent releases and free-threaded builds use a different collector design.

---

## 5. Generational collection and version-aware behavior

### 5.1 The rationale

The generational hypothesis says that many objects die young. CPython's reference counting already disposes of most acyclic short-lived objects as soon as their references disappear. Cyclic GC therefore concentrates on tracked containers and cycle candidates.

In the traditional GIL-enabled CPython collector, tracked objects are divided into generations. New tracked objects enter a young generation; survivors can be promoted to older generations. A young collection is relatively frequent and examines less long-lived state; older-generation work is less frequent but can be more expensive. This can reduce average work compared with scanning the entire tracked heap on every collection.

Do not oversimplify this as “all objects are checked every N allocations.” The implementation tracks allocation/deallocation pressure and applies generation-specific rules. Full-generation collection has additional behavior, including clearing some built-in free lists where possible.

### 5.2 Thresholds are not universal constants

Older CPython documentation commonly described a default threshold tuple of `(700, 10, 10)`. That tuple is historical context, **not a portable promise**. The module roadmap explicitly warns that GC internals have changed across recent releases.

Use this pattern at runtime:

```python
import gc
import platform
import sys

print(platform.python_implementation(), sys.version)
print("thresholds:", gc.get_threshold())
print("stats:", gc.get_stats())
```

Version awareness that matters for this lesson:

- **Python 3.12:** CPython introduced immortal-object machinery through PEP 683. Immortal objects avoid ordinary reference-count updates for selected objects, which can help reduce writes to shared memory pages in fork-based processes. Do not assume every object is immortal.
- **Python 3.13+:** CPython provides an optional free-threaded build. Its reference-counting and cyclic-GC implementation differ from the default GIL-enabled build. The free-threaded collector is non-generational in current CPython implementation documentation and may use process-memory growth as an additional trigger condition. Never infer behavior from a GIL-enabled build's counters alone.
- **Python 3.14.0–3.14.4 versus 3.14.5+:** the initial 3.14 releases shipped an incremental collector with changed generation/threshold semantics; Python 3.14.5 reverted to the prior generational collector behavior. In the initial 3.14 implementation, `threshold2` was ignored and generation 1 represented an incremental collection; the maintenance-release behavior changed again. Read the documentation for the exact patch release and build rather than assuming all Python 3.14 versions behave alike.
- **Python 3.15:** the documented `gc.callbacks` stop-phase info adds `duration` and `candidates`; earlier versions do not guarantee those keys. The callback example below measures duration with `time.perf_counter()` for compatibility and uses `.get()` for optional fields. Treat the documentation for the exact deployed release as authoritative.

The practical rule is simple: collect runtime facts, read the matching version's `gc` documentation and release notes, and rerun the benchmark after every interpreter upgrade.

### 5.3 Inspecting tracking is not a memory census

`gc.is_tracked(obj)` answers whether the object is currently tracked by the cyclic collector. It does not report whether the object is alive, leaked, or large. Some containers can become untracked when their contents are known not to contain GC-relevant references; exact optimization rules are implementation details.

```python
import gc

values = (1, 2, 3)
mixed = (1, object())

print(gc.is_tracked(values))
print(gc.is_tracked(mixed))
```

Treat the output as an observation of the current runtime, not a cross-version test expectation.

---

## 6. Finalization, weak references, and reliable cleanup

### 6.1 `__del__` and PEP 442

`__del__` is a finalizer, not a deterministic cleanup API. It can be invoked when an object is being finalized, but:

- the timing depends on implementation and reachability;
- finalizer order among objects in a cycle is not a safe coordination mechanism;
- a finalizer can resurrect an object by storing `self` in a live global/container;
- exceptions raised by `__del__` are reported as unraisable rather than propagated normally;
- interpreter shutdown can leave module globals or external resources in unexpected states;
- custom C-extension deallocation/finalization code has additional requirements.

[PEP 442](https://peps.python.org/pep-0442/) (implemented in Python 3.4) made cyclic garbage containing objects with `__del__` methods safely finalizable in ordinary supported cases. The old blanket rule “objects with `__del__` can never be collected in cycles” is obsolete. PEP 442 does **not** make finalizer ordering a resource-management contract, nor does it fix incorrect C-extension lifecycle code.

### 6.2 Prefer context managers for resources

Files, locks, sockets, transactions, and similar resources should have explicit lifetime boundaries.

```python
with open("events.log", "rt", encoding="utf-8") as handle:
    for line in handle:
        process(line)
# The file is closed when the block exits, including exceptional exits.
```

For your own resource-owning class, implement `__enter__`/`__exit__` (or use `contextlib`) and make `close()` idempotent if that is part of the API. Do not wait for cyclic GC to close a file descriptor or release a lock.

### 6.3 `weakref.finalize`

`weakref.finalize(obj, callback, *args, **kwargs)` registers a callback to run when `obj` is no longer strongly reachable, while the finalizer registry retains the finalizer object. It is often easier to use correctly than `__del__`, but it is still a fallback tied to object lifetime, not a replacement for a `with` statement.

```python
import weakref

class Session:
    pass

def notify_closed(label):
    print("session became unreachable:", label)

session = Session()
finalizer = weakref.finalize(session, notify_closed, "batch-17")
assert finalizer.alive
del session
# On CPython this usually runs promptly if nothing else references Session.
# The callback should not need the target object itself.
```

Important trap: do not pass `session` itself, a bound method that strongly retains `session`, or another object graph that leads back to `session` as a finalizer argument. That would keep the target alive and prevent the callback from firing. The finalizer callback should be small, idempotent, and safe during shutdown.

### 6.4 Breaking cycles by design

Prefer correcting ownership relationships over increasing GC frequency.

**Use a weak back-reference** when a child needs to refer to a parent without extending the parent's lifetime:

```python
import weakref

class Parent:
    def __init__(self):
        self.children = []

class Child:
    def __init__(self, parent):
        self._parent_ref = weakref.ref(parent)

    @property
    def parent(self):
        return self._parent_ref()

parent = Parent()
child = Child(parent)
parent.children.append(child)
assert child.parent is parent
```

This is valid only for weak-referenceable objects; many built-in types cannot be weak-referenced, and a slotted class may need a `__weakref__` slot. A weak reference can become dead at any time after the referent becomes unreachable, so callers must handle `None`.

Other design options:

- **Explicit detach/close:** unregister listeners, remove children from registries, and clear callbacks at the end of a task.
- **One-way ownership:** store the strong owner-to-child edge, but make the reverse edge weak or derive it when possible.
- **Bounded registries/caches:** weak references are not a substitute for size limits or TTLs when entries must be retained for business reasons.
- **Avoid storing exception objects and frames unnecessarily:** exception tracebacks can retain entire request or batch frames.

Do not break a cycle merely to silence a collector if the relationship is semantically required and externally reachable.

---

## 7. Diagnosing cycles and retention

### 7.1 `gc.get_referrers()`: find direct references, carefully

```python
import gc

target = []
owner = {"payload": target}
referrers = gc.get_referrers(target)
print([type(ref).__name__ for ref in referrers])
```

The result includes objects that directly refer to `target`; it does not automatically explain the full path to a GC root. The diagnostic list itself and the current frame can add references. Inspect only a bounded result, avoid dumping sensitive payloads, and release the diagnostic structures afterward. `gc.get_referrers()` only sees references visible to the collector and is not a complete native-memory debugger.

A useful investigation proceeds in this order:

1. Reproduce retention with a bounded loop.
2. Record live-object counts or weak-reference probes for the suspect type.
3. Run `gc.collect()` at a controlled checkpoint to separate “waiting for cyclic collection” from “still reachable.”
4. Inspect a few direct referrers and follow the path to a root such as a module global, registry, task, closure, cache, or traceback.
5. Fix the ownership/root path; repeat the same workload and test the lifetime invariant.

### 7.2 `gc.set_debug()` and `gc.garbage`

The collector's debug flags can help identify unreachable objects and legacy uncollectable objects. Save and restore the current flag state:

```python
import gc

old_flags = gc.get_debug()
try:
    gc.set_debug(old_flags | gc.DEBUG_SAVEALL)
    # Run a small, isolated reproducer and then inspect gc.garbage.
    gc.collect()
    print("saved objects:", len(gc.garbage))
finally:
    gc.set_debug(old_flags)
    gc.garbage.clear()
```

`DEBUG_SAVEALL` intentionally saves unreachable objects in `gc.garbage` instead of freeing them. This changes the experiment by retaining objects, so do not enable it in a long-running production service or interpret the resulting memory footprint as normal. `gc.DEBUG_LEAK` combines debugging modes including `DEBUG_SAVEALL`; it is useful in an isolated diagnostic process but can intentionally retain large object graphs.

`gc.garbage` is **not** a general list of all cycles. With modern CPython and PEP 442, many cycles with Python-level finalizers are collectible. The list is mainly relevant to objects that cannot be safely collected under particular legacy or extension-type conditions and to explicit debug modes that save all unreachable objects.

### 7.3 Exception and traceback retention

An exception traceback references frames; frames reference local variables; locals may reference a large batch, request, dataframe, or object graph. Saving an exception for later can therefore retain far more memory than the exception message suggests.

```python
saved_errors = []

def parse_one(record):
    try:
        return int(record["count"])
    except (KeyError, TypeError, ValueError) as exc:
        # Storing the exception object can retain its traceback and frames.
        saved_errors.append(exc)
        return None
```

Safer alternatives depend on the use case:

- Store a serializable summary: exception type, message, record identifier, and a formatted traceback string.
- If the actual exception must be stored, understand and intentionally manage its traceback (for example, `exc.__traceback__ = None` when losing the traceback is acceptable).
- Avoid keeping frame objects, tracebacks, or exception objects in long-lived queues/caches.
- Python deletes the `except ... as exc` target at the end of the handler to reduce accidental cycles; assigning the exception to another long-lived container defeats that safeguard.

A formatted traceback string preserves diagnostic text without retaining live frame objects. Do not remove tracebacks before they have been logged or captured when they are needed for debugging.

---

## 8. Measure collection activity

### 8.1 `gc.callbacks`

A callback receives a phase (`"start"` or `"stop"`) and an info dictionary. On stop, the dictionary commonly includes `generation`, `collected`, and `uncollectable`. Keep callback work minimal: no logging network calls, expensive formatting, `gc.collect()`, or allocation-heavy analysis inside the callback.

```python
import gc
import time

_active = {}
events = []

def run_workload():
    # Create unreachable cycles so automatic collections can be observed.
    for _ in range(10_000):
        left = []
        right = []
        left.append(right)
        right.append(left)

def observe_gc(phase, info):
    generation = info.get("generation", -1)
    if phase == "start":
        _active[generation] = time.perf_counter()
    elif phase == "stop":
        started = _active.pop(generation, None)
        if started is not None:
            events.append({
                "generation": generation,
                "seconds": time.perf_counter() - started,
                "collected": info.get("collected", 0),
                "uncollectable": info.get("uncollectable", 0),
            })

gc.callbacks.append(observe_gc)
try:
    run_workload()
finally:
    gc.callbacks.remove(observe_gc)

print(events[:10])
```

This is an illustrative diagnostic. For a production metrics exporter, avoid an unbounded `events` list: aggregate counts and durations into bounded counters/histograms or a small ring buffer. Account for reentrancy and runtime differences; callbacks must not become the bottleneck being measured.

### 8.2 What to measure together

No single GC metric is sufficient. Capture:

- **GC:** collection count by generation (where applicable), duration, collected objects, uncollectable objects, current thresholds, enabled state.
- **Latency:** request/job p50, p95, p99, maximum, and event-loop scheduling delay if applicable.
- **Throughput:** rows/events/requests per second and total batch duration.
- **Memory:** process RSS, container memory, and `tracemalloc` deltas where useful. Remember that traced Python allocations are not equivalent to RSS or native allocation totals.
- **Correctness:** output row counts, checksums, error counts, and resource-cleanup invariants.
- **Environment:** Python version and build (GIL or free-threaded), OS/kernel, allocator, worker model, input shape, concurrency, and warm/cold state.

`time.perf_counter()` is appropriate for elapsed durations. Use `time.process_time()` only when CPU time is the question. Do not infer a pause from total job time alone; correlate callback durations with request/job latency and compare with an unprofiled baseline.

---

## 9. A controlled experiment: thresholds, collection work, and memory trade-offs

This experiment creates a fixed workload of short-lived two-node cycles, measures automatic GC events and elapsed time, and compares the runtime's current thresholds with a deliberately higher first threshold. It then performs a full collection **outside** the timed interval so the cleanup cost is visible separately.

It does **not** promise that higher thresholds are faster. It tests a hypothesis: if frequent automatic cycle collections are a material cost for this workload, a higher first threshold may reduce the number of collections during the measured interval, while potentially increasing retained memory and shifting work to the final collection.

Save as `gc_threshold_experiment.py` and run it in a fresh process with the same Python executable used by the application.

```python
import gc
import statistics
import time


class Node:
    def __init__(self):
        self.peer = None


def make_cycles(pair_count: int) -> None:
    # The function's local list disappears on return. The node pairs remain
    # reachable only from one another and are candidates for cyclic GC.
    nodes = []
    for _ in range(pair_count):
        left = Node()
        right = Node()
        left.peer = right
        right.peer = left
        nodes.append(left)
        nodes.append(right)


def one_trial(thresholds: tuple[int, int, int], pair_count: int) -> dict:
    gc.collect()
    old_enabled = gc.isenabled()
    old_thresholds = gc.get_threshold()
    timings = []
    active = {}
    counts = {}
    durations = []

    def callback(phase, info):
        generation = info.get("generation", -1)
        if phase == "start":
            active[generation] = time.perf_counter()
        elif phase == "stop":
            started = active.pop(generation, None)
            if started is not None:
                durations.append((generation, time.perf_counter() - started))
                counts[generation] = counts.get(generation, 0) + 1

    before_stats = gc.get_stats()
    try:
        gc.enable()
        gc.set_threshold(*thresholds)
        gc.callbacks.append(callback)

        start = time.perf_counter()
        make_cycles(pair_count)
        workload_seconds = time.perf_counter() - start

        # Capture workload collection statistics before the explicit cleanup.
        # This keeps the manual full collection out of the "automatic" callback
        # counts and durations reported below.
        after_stats = gc.get_stats()
        timings.append(workload_seconds)
    finally:
        if callback in gc.callbacks:
            gc.callbacks.remove(callback)
        gc.set_threshold(*old_thresholds)
        if not old_enabled:
            gc.disable()

    # Run the explicit cleanup after removing the callback, so its time and
    # collected-object count are separate from automatic collection metrics.
    cleanup_start = time.perf_counter()
    leftover_collected = gc.collect()
    cleanup_seconds = time.perf_counter() - cleanup_start

    deltas = []
    for old, new in zip(before_stats, after_stats):
        deltas.append({
            "collections": new.get("collections", 0) - old.get("collections", 0),
            "collected": new.get("collected", 0) - old.get("collected", 0),
            "uncollectable": new.get("uncollectable", 0) - old.get("uncollectable", 0),
        })

    return {
        "thresholds": thresholds,
        "workload_seconds": timings[0],
        "cleanup_seconds": cleanup_seconds,
        "automatic_gc_events": counts,
        "automatic_gc_duration_seconds": round(sum(d for _, d in durations), 6),
        "stats_deltas": deltas,
        "leftover_collected_by_explicit_full_gc": leftover_collected,
    }


def main():
    original = gc.get_threshold()
    pair_count = 10_000
    candidates = [
        original,
        (max(original[0] * 5, original[0] + 1), original[1], original[2]),
    ]

    for thresholds in candidates:
        # Repeat each condition; use a fresh process for stronger isolation.
        results = [one_trial(thresholds, pair_count) for _ in range(3)]
        print("\ncondition:", thresholds)
        print("workload seconds:", [round(r["workload_seconds"], 6) for r in results])
        print("median workload seconds:",
              round(statistics.median(r["workload_seconds"] for r in results), 6))
        print("cleanup seconds:", [round(r["cleanup_seconds"], 6) for r in results])
        print("automatic GC event counts:", [r["automatic_gc_events"] for r in results])
        print("automatic GC duration:", [r["automatic_gc_duration_seconds"] for r in results])
        print("stats deltas:", [r["stats_deltas"] for r in results])
        print("final explicit collection:", [
            r["leftover_collected_by_explicit_full_gc"] for r in results
        ])


if __name__ == "__main__":
    main()
```

### Experimental controls and interpretation

The experiment keeps the cycle-construction workload constant and records workload time separately from final cleanup. Automatic callback counts/durations and `gc.get_stats()` deltas are captured before the explicit full collection; the final cleanup is reported separately. Still, it is a teaching experiment, not a production-grade benchmark:

- It measures a synthetic graph made of Python instances and attributes, not your real slowlog application's allocation mix.
- The two conditions run in one process, so allocator state and caches can carry over. For stronger evidence, launch a fresh subprocess per condition, alternate order, and run more trials.
- The callback itself adds overhead. Keep it identical across conditions and perform a separate uninstrumented end-to-end measurement.
- The raised threshold can change the timing and amount of work performed during the workload; it may reduce automatic collections but increase peak memory and explicit cleanup cost.
- `gc.get_stats()` counters are cumulative and generation semantics differ across versions/builds. Use deltas and record the exact interpreter.
- A full collection at the end is outside the workload timer. Report it separately; do not omit it from total batch cost if the real job must perform that cleanup before exit.
- Use process RSS and, if needed, `tracemalloc` or Memray from lesson 05 to understand memory behavior. Do not assume `gc.get_stats()` measures bytes.

**A valid conclusion** might be: “In this environment, the higher threshold reduced automatic collection count during this synthetic workload, but final cleanup and memory rose; end-to-end results did not justify the change.” A valid conclusion could also be that there is no meaningful difference. Only the measurements decide.

### A production-grade before/after protocol

1. Form a hypothesis from observed evidence, such as p99 pauses coinciding with expensive oldest-generation collections.
2. Capture baseline throughput, latency percentiles, peak RSS/container memory, GC event count/duration, and correctness checks over representative input.
3. Change one setting in a canary or isolated worker; keep code, workload, concurrency, and instrumentation fixed.
4. Run repeated trials and include warm-up. Compare medians and distributions, not just the best run.
5. Validate the same output, errors, resource cleanup, and memory limits.
6. Roll back if the improvement is not repeatable, memory headroom shrinks unacceptably, tail latency moves elsewhere, or correctness/cleanup changes.

---

## 10. Tuning techniques: mechanism, use case, risk, measurement, rollback

### 10.1 Raise collection thresholds

- **Mechanism:** automatic collection is triggered less frequently according to the runtime's threshold policy.
- **Use case:** measurements show excessive collection frequency in a bounded workload and adequate memory headroom exists.
- **Risk:** unreachable cycles can accumulate longer; collection cost can be shifted to a later pause; behavior varies by version/build.
- **Measure:** automatic collection count and duration, p50/p95/p99 latency, total elapsed time, peak RSS/cgroup memory, and final cleanup cost.
- **Rollback:** restore the exact tuple returned by `gc.get_threshold()` if the gain is noisy, memory rises beyond budget, tail latency worsens, or the workload changes.

Change only the threshold values you have a hypothesis for. Do not set enormous values because a synthetic microbenchmark happened to improve.

### 10.2 Explicit `gc.collect()` at a safe point

- **Mechanism:** requests a collection now instead of waiting for the automatic trigger.
- **Use case:** batch processing has a known phase boundary after a large temporary graph is dropped, and collection at that boundary is less disruptive than an arbitrary request-time pause.
- **Risk:** full collection can be expensive; the objects may still be reachable; collection may not lower RSS; concurrent/recursive collection is not a safe strategy.
- **Measure:** duration of the call, objects collected, RSS before/after, and end-to-end time including the call.
- **Rollback:** remove or narrow the explicit collection if it adds latency without reducing retained objects or improving a measured memory/latency objective.

A full collection should not be inserted after every request or loop iteration by default. It often converts amortized work into repeated pauses.

### 10.3 Disable automatic cyclic GC only in a tightly bounded experiment

- **Mechanism:** `gc.disable()` disables automatic cyclic collection. Reference counting continues to dispose of acyclic objects, but unreachable cycles can remain until collection is re-enabled and run.
- **Use case:** only a short, isolated batch phase whose object graph has been tested to produce no unreachable cycles (or where cycle accumulation is strictly bounded), with an explicit cleanup plan and enough memory headroom.
- **Risk:** an overlooked cycle can retain a large graph; an exception can leave the collector disabled; process-wide policy affects unrelated code in the same interpreter. It is not a recommended default for services.
- **Measure:** use a `try/finally` guard, record enabled state, cycle probes, RSS, elapsed time, and explicit collection cost. Test failure paths as well as success paths.
- **Rollback:** re-enable GC immediately if the assumption about cycles is violated, memory grows unexpectedly, the workload becomes long-lived, or any third-party component relies on normal automatic collection.

If a carefully controlled experiment is justified, restore the prior state:

```python
import gc

was_enabled = gc.isenabled()
try:
    gc.disable()
    run_bounded_batch_with_verified_no_unreachable_cycles()
finally:
    if was_enabled:
        gc.enable()
gc.collect()  # deliberate cleanup checkpoint, if justified by the experiment
```

The example illustrates state restoration, not a blanket recommendation to disable GC. Do not run it in a shared server request handler or library function without an explicit application-level design.

### 10.4 `gc.freeze()` before `fork`

- **Mechanism:** `gc.freeze()` moves currently tracked objects into a permanent generation that ordinary collections do not revisit. This can reduce GC metadata writes and copy-on-write page dirtiness for long-lived objects in pre-fork worker models.
- **Use case:** a process builds a stable object graph during initialization, then forks workers that should share those pages read-mostly. A common sequence is: collect, freeze, fork; in children, unfreeze only if the lifecycle requires it.
- **Risk:** objects frozen accidentally after workload-specific state accumulates may remain retained for the process lifetime; it does not make mutable pages read-only and does not prevent all copy-on-write writes. It is not useful in every process model (for example, `spawn` does not share the parent's heap in the same way).
- **Measure:** compare worker RSS/PSS and aggregate memory, page-fault/COW behavior where observable, startup time, and correctness across worker lifecycles.
- **Rollback:** remove the freeze sequence if shared-memory benefit is absent, retained memory grows, or workers need ordinary collection of the frozen graph. Test with the deployed Python version and process start method.

The ordering matters: `gc.collect()` then `gc.freeze()` is the commonly documented pre-fork pattern. Freeze only stable long-lived state, not a process that is already holding request-specific data.

### 10.5 Change object relationships instead of tuning

- **Mechanism:** weak back-references, explicit detach/close, bounded caches, and one-way ownership reduce accidental retention or cycles.
- **Use case:** the investigation found a real ownership cycle, registry leak, listener leak, or traceback root.
- **Risk:** weak references can disappear sooner than callers expect; explicit cleanup may be skipped on error paths if not protected by context managers; removing a strong reference can change semantics.
- **Measure:** weakref lifetime assertions, bounded object counts after collection, `tracemalloc` snapshots, RSS trend, and functional tests.
- **Rollback:** revert if the ownership contract breaks or legitimate objects are reclaimed early; redesign the relationship rather than making the reference weak blindly.

This is often the most durable fix because it addresses the cause rather than changing when the collector runs.

---

## 11. Copy-on-write, reference-count writes, and worker processes

### 11.1 Why forked workers can lose sharing

On Unix-like systems, `fork()` initially allows parent and child to share physical memory pages through copy-on-write (COW). When either process writes to a shared page, the OS may copy that page. Python reference-count changes can write to object headers even when application code only appears to read objects. Traversing or mutating objects, allocator metadata, and runtime activity can also dirty pages.

Consequences:

- A large preloaded Python object graph may have a high aggregate worker memory cost after workers touch many pages.
- Parent RSS alone does not show how much physical memory is shared. Where available, proportional set size (PSS) and private/shared page metrics can be more informative.
- `gc.freeze()` can reduce some GC-related COW writes for stable tracked objects, but it is not a universal COW solution.
- Compare `fork` with `spawn` only in context: `spawn` avoids sharing the parent's Python heap but incurs startup/serialization costs and has different portability/safety properties.
- Do not claim that immortal objects eliminate all reference-count writes or that freezing guarantees shared pages remain shared.

### 11.2 Immortal objects (Python 3.12+)

PEP 683 introduced immortal objects to CPython, allowing selected objects to avoid ordinary reference-count updates. This can reduce refcount writes and improve fork/COW behavior for those objects. It is an implementation optimization, not a user-facing way to immortalize arbitrary application instances. Do not use private refcount bits or undocumented APIs to diagnose lifetime.

### 11.3 Free-threaded CPython

The optional free-threaded CPython build introduced in the 3.13 series changes the assumptions behind reference counting and cyclic GC. Depending on object type and build, CPython uses biased, deferred, or per-thread reference-counting strategies; some objects may be reclaimed at a later safe point or GC run rather than at the exact point a simplified refcount model predicts. Current free-threaded GC implementation documentation describes a non-generational collector, unlike the traditional generational GIL-enabled build.

Operational implications:

- Log `sys.version`, `sys.implementation`, and the build's GIL/free-threading status where supported by the runtime.
- Do not assert that an object's finalizer must run immediately after a `del`.
- Do not write tests that expect exact `gc.get_count()` tuples or generation scheduling.
- Benchmark on the actual build. Free-threaded performance, allocation rates, synchronization, and GC pauses can differ materially from a GIL-enabled build.

---

## 12. Lowering GC pressure with better data layouts

A cycle-heavy graph often signals a data-model issue; a large object count may signal a layout issue. If each record is a Python object containing several Python objects, per-element overhead can dominate the payload.

Consider these alternatives when they fit the semantics:

- **Tuples of immutable/atomic values:** compact and simple, though still one Python tuple plus references for each record. Some tuples can become untracked if their contents do not need GC tracking; do not rely on the exact tracking optimization.
- **`array.array` or `memoryview`:** useful for homogeneous numeric/binary data with fewer Python objects per value.
- **NumPy arrays / columnar libraries:** represent large homogeneous columns in contiguous native buffers, reducing Python-object overhead. These belong to later Stage 2 material and should be adopted based on workload and dependency constraints.
- **Packed `bytes`/`struct`:** appropriate for fixed-width binary records, with trade-offs in readability and access cost.
- **`__slots__`:** can reduce per-instance dictionary overhead for suitable classes, but does not eliminate the object itself or automatically make it untracked. Include `__weakref__` in slots if weak references are needed.
- **Streaming and bounded batches:** keep fewer records live at once and avoid retaining the entire ETL input plus intermediates.

Measure peak RSS, allocations, throughput, and conversion cost. A compact representation can be slower if the program repeatedly converts it back to Python objects.

---

## 13. C-extension cleanup and uncollectable objects

A Python-level object graph is only as visible as the extension types' GC integration permits. A C extension type that owns references to other Python objects and participates in cycles generally must implement the correct GC protocol (including traversal and clearing hooks) and advertise GC support where required. Incorrect extension lifecycle code can cause leaks, premature release, crashes, or cycles the collector cannot safely clear.

When `gc.garbage` or `DEBUG_UNCOLLECTABLE` output points toward an extension type:

1. Reduce the case to a minimal reproducer.
2. Identify the exact extension and Python build/version.
3. Check whether the type owns Python references and whether its traversal/clear/deallocation contract is correct.
4. Run the extension's tests under debug builds and relevant memory diagnostics where feasible.
5. Upgrade or patch the extension; do not “solve” a broken ownership contract by globally disabling GC.

`gc.DEBUG_LEAK` can be useful in a short-lived test process because it includes `DEBUG_SAVEALL`, which intentionally retains unreachable objects. Restore debug flags and clear `gc.garbage` after the test. For native allocations not visible in Python's object graph, use the appropriate native-memory tooling; GC counters alone cannot identify them.

---

## 14. GC and asynchronous latency

A synchronous collection runs on the thread executing the collector. If that thread is an event-loop thread, a sufficiently expensive collection can delay unrelated tasks. The symptoms can look like network jitter, an inexplicable event-loop stall, or a tail-latency spike even when average CPU utilization appears moderate.

A disciplined investigation:

1. Measure event-loop lag and request/job p95/p99 latency.
2. Instrument `gc.callbacks` to correlate collection start/stop times with latency outliers.
3. Check whether a large number of tracked containers or a high-cost generation correlates with the pauses.
4. Profile the workload and inspect object retention before tuning.
5. If justified, reduce object churn/graph complexity or move batch-heavy work out of the request/event-loop critical path.
6. Consider a carefully tested collection at an explicit safe phase boundary only if it improves total and tail latency.
7. Re-run under realistic concurrency; a benchmark without other tasks cannot prove that event-loop latency improved.

Do not call `gc.collect()` from a GC callback. Do not assume moving collection to a background thread is safe or straightforward: object graph access and interpreter-specific GC synchronization constraints matter. Keep correctness and runtime contracts ahead of attempts to hide pauses.

---

## 15. Production observability and runbook

Export bounded metrics with low-cardinality labels:

- `python_gc_collections_total{generation=...}` where the runtime provides meaningful generation labels;
- `python_gc_collected_objects_total{generation=...}`;
- `python_gc_uncollectable_objects_total{generation=...}`;
- `python_gc_collection_duration_seconds` as a histogram;
- process RSS and container memory usage/limit;
- event-loop lag, request/job latency percentiles, throughput, and batch size;
- interpreter version/build and configured thresholds as deployment metadata.

Metric labels must not contain request IDs, filenames, user IDs, or other unbounded/sensitive values. Prefer counters/histograms over emitting one log record for every collection. Since callback data and generation semantics differ by runtime, make the exporter version-aware and test it on each supported interpreter.

### Incident runbook: “memory grows or p99 spikes”

1. **Confirm scope:** one process, all workers, one release, or one input class?
2. **Capture runtime:** Python patch version, GIL/free-threaded build, OS, process model, thresholds, GC enabled state.
3. **Capture baseline:** RSS/PSS where available, container limit, p50/p95/p99, throughput, GC stats.
4. **Correlate:** do collection durations line up with latency spikes? Does RSS rise after each batch?
5. **Separate causes:** run `tracemalloc` snapshots for Python allocations; use Memray/native tooling if RSS and traced allocations diverge.
6. **Find roots:** use weakref probes, bounded `gc.get_referrers()` inspection, and cycle visualisation in an isolated reproducer.
7. **Fix first:** remove unwanted roots/cycles, bound caches, release tracebacks, reduce graph size or stream data.
8. **Tune only with a hypothesis:** change one threshold or lifecycle policy in a canary.
9. **Verify:** compare distributions and memory headroom, run correctness tests, test failure paths.
10. **Rollback:** restore prior thresholds/debug flags and remove experimental callbacks if benefit is not repeatable.

---

## 16. Practical task: add a cycle-retention investigation to `slowlog`

Use the shared slowlog ETL script from earlier lessons. Do not rewrite its parsing algorithm as part of this task; isolate object lifetime and collection behavior.

### Scenario

Add a small in-memory `RunContext` that holds a list of `Record` objects, while each record holds a reference back to its context. The context and records form a cycle. The workload processes multiple batches, and the question is whether completed contexts are reclaimed or retained by a registry, error object, or callback.

### Requirements

1. Create a reproducible workload with a configurable number of records/batches.
2. Add a weak-reference probe for each completed context (or a bounded sample); do not let the probe itself retain the object.
3. Compare three designs:
   - strong back-reference (intentional cycle);
   - weak back-reference;
   - explicit `close()`/detach at the end of a batch.
4. Measure:
   - throughput and total duration;
   - automatic collection counts/durations;
   - RSS and, if useful, `tracemalloc` snapshot differences;
   - how many weak references are dead after a deliberate `gc.collect()` checkpoint;
   - output row/error counts to prove semantics stayed the same.
5. Add a regression test asserting that completed contexts become unreachable after cleanup. Assert behavior, not exact GC counts or elapsed time.
6. Run with the deployed Python version and record its actual thresholds/build. If comparing a free-threaded build, run it as a separate environment.
7. Only if measurements justify it, test a higher threshold. Record both workload time and cleanup time, plus peak memory.
8. Write a report with hypothesis, environment, baseline, change, result distribution, correctness checks, risks, rollback criteria, and unresolved questions.

### Acceptance criteria

- The test proves object lifetime with weak references and a deliberate collection checkpoint.
- The test distinguishes a reachable registry leak from an unreachable cycle.
- No production code globally disables cyclic GC.
- Any threshold or freeze change has a documented mechanism, measured result, memory budget, and rollback path.
- The report explicitly says “no material improvement” when the evidence is inconclusive.

---

## 17. Common mistakes

- **Confusing reference counting with cyclic GC.** Most acyclic objects are released by reference counting; cyclic GC handles unreachable tracked cycles and related implementation cases.
- **Assuming `del x` destroys the object.** It removes a name/reference; other references may remain.
- **Treating a cycle as automatically a leak.** A reachable cycle is live by definition.
- **Treating `gc.garbage` as a list of all cycles.** It is not.
- **Trusting `__del__` for deterministic resource cleanup.** Use context managers and explicit close protocols.
- **Holding a weakref target while testing it.** A temporary strong reference can invalidate the observation.
- **Using exact reference counts as assertions.** Counts vary with temporary references, implementation, and build.
- **Assuming `(700, 10, 10)` applies everywhere.** Query the running interpreter and read matching documentation.
- **Assuming `gc.get_stats()` measures memory.** It reports collection outcomes, not bytes or RSS.
- **Calling `gc.collect()` in a hot loop or callback.** This can add repeated pauses and complicate collector state.
- **Enabling `DEBUG_SAVEALL` in production.** It intentionally retains unreachable objects.
- **Raising thresholds without a memory budget.** Fewer collections can mean more retained cycles and larger eventual pauses.
- **Using `gc.freeze()` as a generic leak fix.** It can keep tracked objects out of ordinary collections; use only for a measured lifecycle/COW goal.
- **Assuming a freed object makes RSS fall.** Allocators may retain arenas and native libraries manage their own memory.
- **Ignoring extension types and tracebacks.** They can be the source of retention even when Python code looks clean.
- **Benchmarking only the timed loop.** Include final collection, memory peak, and full job cost in operational conclusions.

---

## 18. Exercises

### Beginner

1. Draw the object-reference graph before and after `del left` in the two-node example.
2. Modify the cycle example so a global list keeps one node alive. Explain why `gc.collect()` cannot reclaim the graph.
3. Use a weak reference to show that an observer does not keep an object alive.
4. Print `gc.get_count()`, `gc.get_threshold()`, and `gc.get_stats()` before and after creating many short-lived containers. Explain what each does and does not measure.

### Intermediate

5. Write a parent/child relationship using a weak back-reference. Test the case where the parent has already been reclaimed.
6. Write a class with `weakref.finalize`; ensure the callback does not retain the target. Explain why a context manager is still preferable for closing a file.
7. Store exception summaries rather than exception objects in a long-lived error queue. Use a weakref probe or object-count experiment to compare retention.
8. Use `gc.DEBUG_SAVEALL` in a disposable process and explain why objects appear in `gc.garbage`. Restore the debug flags and clear the list.
9. Add a GC callback that records duration without logging on the collection path. Remove the callback reliably even when the workload raises.

### Advanced

10. Run the threshold experiment with several graph sizes and report workload time, cleanup time, collection count, and peak RSS. Do not select only the fastest run.
11. Investigate a p99 latency spike in an async workload. Correlate event-loop lag with GC callback events and compare with an uninstrumented run.
12. Design a pre-fork preload experiment comparing `gc.freeze()` with no freeze. Measure PSS/worker memory where available; explain why the result may differ under `spawn`.
13. Explain how an incorrect C-extension `tp_traverse`/clear/deallocation implementation can affect cycle collection. Identify the evidence you would need before blaming the extension.
14. Compare a Python-object-per-record representation with a packed or columnar representation. Include conversion cost, peak memory, throughput, and the semantic cost of changing representation.

---

## 19. Self-check questions

1. Why can `A → B → A` survive after all external strong references are removed?
2. What is the difference between an unreachable cycle and a reachable cycle?
3. Why should a test assert that a weak reference is dead after a controlled collection rather than assert that `gc.collect()` returns exactly two?
4. What does `gc.get_count()` measure, and why is it not a live-object count?
5. Why are historical GC thresholds not universal across Python versions/builds?
6. What did PEP 442 change about Python-level finalizers in cycles, and what does it not guarantee?
7. How can an exception traceback retain a large batch after the handler has finished?
8. Why can `DEBUG_SAVEALL` make a memory investigation perturb the thing being measured?
9. What evidence would justify raising `threshold0`? What memory and tail-latency risks must be monitored?
10. Why might explicit collection improve one latency objective but worsen total batch time?
11. What is `gc.freeze()` intended to help in a pre-fork application, and why is it not a general leak fix?
12. Why can refcount writes reduce copy-on-write sharing after `fork()`?
13. How do free-threaded CPython builds change assumptions about generations and immediate object reclamation?
14. What metrics would you export to distinguish a GC pause from native allocation growth or allocator retention?
15. If RSS stays high after a weakref becomes dead, what are three plausible explanations other than a live Python cycle?

---

## 20. Investigation report template

Use this template for the slowlog task or a production incident.

```text
Title:
Date / owner:
Python version, implementation, build (GIL/free-threaded):
OS/kernel / allocator / worker model:
Input size and shape:
Hypothesis:

Baseline
- Throughput:
- Total duration:
- p50 / p95 / p99 latency:
- Peak RSS / container memory:
- GC enabled / thresholds:
- GC collection count and duration:
- Correctness checks:

Intervention (one variable at a time)
- Code or setting changed:
- Mechanism:
- Why the evidence supports trying it:
- Rollback criteria:

After
- Throughput:
- Total duration (including cleanup):
- p50 / p95 / p99 latency:
- Peak RSS / container memory:
- GC count / duration / collected / uncollectable:
- Weakref/object-lifetime result:
- Output equivalence / error counts:
- Repeats and variability:

Decision
- Keep / revert / inconclusive:
- Evidence:
- Risks and remaining memory headroom:
- Version/build caveats:
- Follow-up owner and date:
```

## 21. References and version checks

Prefer the documentation matching the exact deployed interpreter.

- [`gc` — Garbage Collector interface](https://docs.python.org/3/library/gc.html): API, current threshold semantics, generation changes, and free-threaded notes.
- [`weakref`](https://docs.python.org/3/library/weakref.html): weak references and `weakref.finalize`.
- [PEP 442 — Safe object finalization](https://peps.python.org/pep-0442/): finalization of cycles.
- [PEP 683 — Immortal Objects](https://peps.python.org/pep-0683/): immortal-object design introduced in CPython 3.12.
- [PEP 703 — Making the GIL optional](https://peps.python.org/pep-0703/): free-threaded reference counting and GC design.
- [CPython internal garbage collector design](https://github.com/python/cpython/blob/main/InternalDocs/garbage_collector.md): implementation details; `main` may differ from released versions.

Before applying a production change, verify the `gc` and `weakref` documentation for the exact patch release, record the actual runtime thresholds, and rerun the controlled experiment. A performance claim is valid only for the measured workload, build, and platform.

---

## Final engineering principle

**Fix unwanted retention first; tune collection second.** Reference counting, cyclic GC, allocators, native buffers, and operating-system memory accounting answer different questions. A reliable investigation measures each layer that could explain the symptom, changes one variable at a time, preserves correctness, and keeps an explicit rollback path.
