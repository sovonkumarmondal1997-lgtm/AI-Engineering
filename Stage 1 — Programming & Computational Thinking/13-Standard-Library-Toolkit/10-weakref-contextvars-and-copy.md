# Weak References, Context Variables, and Copy Semantics

**Target runtime:** Python 3.12+; version-specific notes identify APIs added in Python 3.13 and 3.14.  
**Module:** Stage 1 — Programming & Computational Thinking → Module 13 — Standard Library Toolkit → Phase D — Config, Network and Runtime Utilities.  
**Scope:** Object lifetime, ownership, execution-local context, and copying. This lesson is not a complete garbage-collection, memory-profiling, or asynchronous-programming course.

## Learning objectives

By the end of this lesson, you can:

- Explain object identity, strong references, reachability, aliasing, and why a name is not the object itself.
- Predict the difference between shallow and deep copies, including nested mutable values, shared references, and cycles.
- Use `copy.copy()` and `copy.deepcopy()` deliberately, and implement `__copy__` / `__deepcopy__` when an object needs custom semantics.
- Use `weakref.ref`, `WeakValueDictionary`, `WeakKeyDictionary`, `WeakSet`, `WeakMethod`, and `weakref.finalize` where their lifetime semantics fit.
- Design caches and observer registries without unintentionally retaining objects.
- Use `ContextVar.get()`, `set()`, and token-based `reset()` to scope request/task state safely.
- Explain context behavior across synchronous calls, `asyncio` tasks, threads, and executors, including explicit propagation.
- Test object collection and context isolation without assuming a universal garbage-collection schedule.
- Diagnose likely retention with weak-reference probes and `tracemalloc`, while distinguishing evidence from proof of a leak.

## Roadmap placement and prerequisites

The Module 13 roadmap puts this lesson after `08-tomllib-and-configparser.md` and `09-urllib-sockets-and-http-server-basics.md`, before the module README and practice questions. The module's Phase D focuses on configuration, networking, and runtime utilities. This lesson joins three related but distinct tools: `weakref` for non-owning references, `contextvars` for execution-local state, and `copy` for object-graph duplication.

Relevant prerequisites from the wider Stage 1 tree:

- **Mutability, identity, and aliasing** from the fundamentals/object-model lessons (including Module 1.2 and Module 1.11 topics): a shallow copy creates a new outer object but can preserve references to nested objects.
- **Functions, decorators, bound methods, and closures** from the functional-programming and metaprogramming modules: callbacks can keep their receiver or captured variables alive.
- **Exceptions, `try`/`finally`, context managers, and testing with pytest**: context tokens must be reset reliably, and lifecycle claims need focused tests.
- **Iterators, generators, and `asyncio` task concepts** from the iteration/concurrency material: tasks can interleave on one thread, so thread-local state is not necessarily task-local state.
- **Threads and executor concepts** from concurrency and runtime material: context propagation is an explicit boundary, not a universal side effect of starting work.

If object identity (`is`), mutable containers, or `try/finally` are unfamiliar, review those first. The lesson uses small runnable examples rather than repeating the full object model or teaching all of `asyncio`.

## 1. Foundations: identity, references, and lifetime

### 1.1 Names refer to objects

A Python variable is a name bound to an object. Multiple names can refer to the same object. `id()` returns an identity value that is unique among simultaneously live objects; its numeric representation is implementation-dependent and should not be treated as a permanent object identifier.

```python
first = {"rows": []}
second = first

assert first is second
second["rows"].append("row-1")
assert first["rows"] == ["row-1"]
```

**What it is:** `first` and `second` are two references (names) to one dictionary.  
**Why it matters:** mutating through either name affects the same object.  
**When to use this knowledge:** whenever you pass mutable state between functions, cache values, keep callbacks, or make copies.  
**Trade-off:** sharing avoids copying cost but creates shared ownership and mutation coupling.

### 1.2 Strong references, reachability, and collection

An ordinary reference is strong: while an object is strongly reachable through live references and object relationships, Python must keep it available. A list, dictionary, closure, bound method, cache, task, or callback registry can all hold strong references.

Garbage collection is not the same as “the object disappears as soon as one variable is deleted.” `del name` removes a binding; it does not delete an object that other references still reach. In CPython, reference counting often releases unreachable acyclic objects promptly, while cyclic garbage collection handles unreachable reference cycles. Other Python implementations may have different collection timing. Application correctness must not depend on immediate collection.

```python
class Payload:
    pass

payload = Payload()
owner = {"current": payload}  # owner strongly retains the payload

del payload
assert owner["current"] is not None
```

The example's final assertion is intentionally about the still-referenced object, not about a guaranteed collection time. The name `del_name` is just an ordinary string and has no relationship to object lifetime.

### 1.3 Strong references can cause retention

A retention problem occurs when an object stays reachable longer than intended. It may be a real leak (unbounded growth), an accidental long-lived cache entry, or simply an intentional but expensive ownership relationship.

```python
class Worker:
    def __init__(self, name: str) -> None:
        self.name = name

workers_by_name: dict[str, Worker] = {}
workers_by_name["daily-import"] = Worker("daily-import")
```

This dictionary strongly owns every `Worker` it contains until an entry is removed or the dictionary itself becomes unreachable. If keys are never evicted, values can accumulate. A weak container can help only when the desired policy is “index this object while someone else owns it”; it is not a replacement for a deliberate cache eviction policy when the cache itself is supposed to own cached values.

## 2. Beginner: shallow copy and deep copy

### 2.1 Shallow copy

`copy.copy(obj)` makes a shallow copy. For common containers, it creates a new outer container but retains references to contained objects. The copy and original are distinct outer objects; nested mutable values may still be shared.

### 2.2 Deep copy

`copy.deepcopy(obj)` recursively copies supported members to create a separate object graph where practical. It tracks objects already visited in a `memo` mapping, so it can preserve repeated-reference relationships and terminate on cycles. It is not a universal “clone every reachable thing” operation: custom classes can control copying, and external resources such as sockets, files, locks, database connections, and live tasks generally should not be duplicated as if they were plain data.

```python
from copy import copy, deepcopy

original = {
    "name": "batch-17",
    "options": {"retries": 3},
    "tags": ["daily", "priority"],
}
shallow = copy(original)
deep = deepcopy(original)

assert shallow is not original
assert shallow["options"] is original["options"]
assert shallow["tags"] is original["tags"]
assert deep is not original
assert deep["options"] is not original["options"]
assert deep["tags"] is not original["tags"]

shallow["tags"].append("shared")
assert "shared" in original["tags"]

deep["tags"].append("independent")
assert "independent" not in original["tags"]
```

| Operation | New outer object? | Nested mutable objects | Typical use |
|---|---:|---|---|
| Assignment (`alias = original`) | No | Shared | Deliberate aliasing / shared ownership |
| `copy.copy(original)` | Usually yes for copyable containers | Usually shared | Independent top-level container with shared members |
| `copy.deepcopy(original)` | Usually yes for supported graph nodes | Recursively copied, respecting memo/custom hooks | Isolated in-memory data structures when duplication is meaningful |

Do not infer copy semantics from a class name. A class may be immutable, define custom copy hooks, return itself from a copy operation, or reject copying. Verify the documented behavior of the type.

### 2.3 Aliasing, shared references, and cycles

Shallow copying can be surprising when two keys point to the same nested object. Deepcopy's memo generally preserves that sharing *inside the copied graph* rather than creating an unrelated duplicate for every path.

```python
from copy import deepcopy

shared = []
original = {"left": shared, "right": shared}
cloned = deepcopy(original)

assert cloned is not original
assert cloned["left"] is cloned["right"]
assert cloned["left"] is not shared
```

Cycles are legal in Python object graphs. `deepcopy()` supports ordinary container cycles because it records objects in its memo as it traverses them.

```python
from copy import deepcopy

node: dict[str, object] = {"label": "root"}
node["self"] = node
cloned = deepcopy(node)
assert cloned is not node
assert cloned["self"] is cloned
```

### 2.4 Copying is an ownership decision

Before copying, ask:

1. Which parts must be independently mutable?
2. Which immutable or expensive values can safely be shared?
3. Does the object contain external resources or identity-sensitive collaborators?
4. Would an immutable data model, a new constructor, or a targeted copy be clearer than a generic deep copy?
5. What is the cost in CPU and memory for the graph's size?

For production data pipelines, prefer explicit constructors or targeted copying when only a few fields must change. Deep-copying a large record graph on every batch can multiply memory pressure and latency. For configuration data, immutable nested structures can reduce accidental mutation without repeated deep copies.

## 3. Beginner: weak references

### 3.1 What a weak reference does

A weak reference observes an object without keeping it alive. `weakref.ref(obj)` returns a weak-reference object; calling it returns the live referent or `None` if the referent has been collected.

```python
import gc
import weakref

class Payload:
    pass

payload = Payload()
probe = weakref.ref(payload)
assert probe() is payload

del payload
gc.collect()  # Useful in a focused test; not a universal timing guarantee.
assert probe() is None
```

**What it is:** a non-owning reference.  
**Why it matters:** caches, registries, and observers sometimes need to track an object without extending its lifetime.  
**When to use it:** when the object has an independent owner and the registry should not become its owner.  
**Trade-offs:** a weak reference can become dead at any point when no strong owner remains; every dereference must handle `None`. Weak references do not automatically solve unbounded keys, unbounded metadata, or incorrect ownership design.

A weak reference is not a way to keep an object available “just in case.” If an operation needs the object to remain alive, take a strong local reference for the duration of that operation:

```python
obj = probe()
if obj is not None:
    use(obj)  # `obj` is now a strong local reference during this scope
```

Avoid calling `probe()` twice in a condition and then assuming the second result cannot be `None`; retrieve it once and hold the result strongly.

### 3.2 Weak-reference eligibility

Not every object supports weak references. Typical examples:

- Instances of ordinary user-defined classes usually support weak references.
- Many built-in containers and scalar objects, including `list`, `dict`, and `int`, do not support weak references directly.
- Some built-in types do support weak references. On the target CPython runtime, `set`, `frozenset`, Python functions, and class objects are examples; `list`, `dict`, and `int` are not. This is not an exhaustive cross-implementation list—check the concrete type and supported Python version.
- `WeakKeyDictionary` keys and `WeakSet` members must be both weak-referenceable and hashable. `WeakValueDictionary` values must be weak-referenceable; its keys are held strongly and must be hashable.
- A class using `__slots__` needs a `__weakref__` slot to support weak references, unless an appropriate base class already provides it.
- `@dataclass(slots=True, weakref_slot=True)` supports this conveniently on Python 3.11+.

```python
import weakref
from dataclasses import dataclass

@dataclass(slots=True, weakref_slot=True)
class Record:
    key: str

record = Record("r-1")
record_ref = weakref.ref(record)
assert record_ref() is record
```

The `weakref_slot` option is available from Python 3.11; the module target is Python 3.12+, so it is available here. A `TypeError` from `weakref.ref(obj)` means the object is not weak-referenceable under its current type/layout.

### 3.3 Weak containers

- `weakref.WeakValueDictionary`: keys are held strongly, values weakly. Appropriate when an external owner controls the values' lifetime and the dictionary is just a lookup index.
- `weakref.WeakKeyDictionary`: keys are weakly held; values are strongly held. Appropriate for metadata keyed by object identity/lifetime, but be alert to value-to-key reference cycles that can defeat the expected lifetime behavior.
- `weakref.WeakSet`: stores weak references to its members, useful for membership registries that should not own those members.

A weak container does not promise that an entry will persist in the absence of another strong reference. This is the intended behavior, not data loss from a bug.

## 4. Intermediate implementation: a weak-value object cache

This cache stores expensive objects only while another component has a strong reference to them. A lookup may miss because the object was collected; callers that need a durable result must retain it strongly or use an owning cache with an explicit size/TTL policy.

```python
from __future__ import annotations

import weakref

class CompiledPlan:
    def __init__(self, plan_id: str, steps: tuple[str, ...]) -> None:
        self.plan_id = plan_id
        self.steps = steps

class PlanIndex:
    """Non-owning index: live plans are owned by their callers."""
    def __init__(self) -> None:
        self._plans: weakref.WeakValueDictionary[str, CompiledPlan] = (
            weakref.WeakValueDictionary()
        )

    def publish(self, plan: CompiledPlan) -> None:
        self._plans[plan.plan_id] = plan

    def get(self, plan_id: str) -> CompiledPlan | None:
        return self._plans.get(plan_id)

index = PlanIndex()
plan = CompiledPlan("daily", ("read", "validate", "write"))
index.publish(plan)
assert index.get("daily") is plan

del plan
# After collection, this non-owning index no longer promises the value exists.
```

**Design rule:** weak-value caches are suitable for re-creatable, non-authoritative objects whose lifetime is owned elsewhere. They are not suitable as the only storage for results that must remain available. For a durable cache, use explicit bounds, eviction, TTL, invalidation, or a library designed for that purpose.

### 4.1 Strong cache versus weak cache

```python
strong_cache: dict[str, CompiledPlan] = {}
weak_cache: weakref.WeakValueDictionary[str, CompiledPlan] = weakref.WeakValueDictionary()

plan = CompiledPlan("daily", ("read",))
strong_cache["daily"] = plan  # cache itself keeps the plan alive
weak_cache["daily"] = plan   # weak cache does not own the plan
```

A `functools.lru_cache` retains cached arguments and return values strongly until eviction or `cache_clear()`. This is often correct and efficient for pure functions with bounded input cardinality. It can be a retention hazard if arguments/results are large or unbounded, or if a cached method includes `self` in the cache key. Do not replace `lru_cache` with weak references automatically: choose based on the intended ownership, hit rate, invalidation, and memory budget.

## 5. Intermediate implementation: weak observer and callback registries

### 5.1 Why bound methods can retain instances

Evaluating `subscriber.on_event` creates a bound-method object that refers to both the function and its receiver (`subscriber`). A long-lived registry holding that bound method strongly can keep the subscriber alive. `weakref.WeakMethod` provides a weak reference to a bound method, because the temporary bound-method object itself is not a stable long-lived target for `weakref.ref`.

```python
from __future__ import annotations

import weakref
from collections.abc import Callable
from typing import Any, TypeAlias

Callback: TypeAlias = Callable[[str], Any]
RegistryEntry: TypeAlias = weakref.WeakMethod[Any] | Callback

class WeakObserverRegistry:
    """Single-threaded registry: bound methods are weak; other callables are strong."""
    def __init__(self) -> None:
        self._callbacks: list[RegistryEntry] = []

    def subscribe(self, callback: Callback) -> None:
        # A bound method has both __self__ and __func__. WeakMethod avoids
        # retaining its receiver. Functions/callable objects are retained
        # strongly by policy; their closures may therefore retain captured state.
        if getattr(callback, "__self__", None) is not None and getattr(callback, "__func__", None) is not None:
            entry: RegistryEntry = weakref.WeakMethod(callback)
        else:
            entry = callback
        self._callbacks.append(entry)

    def publish(self, event: str) -> None:
        # Build a snapshot and prune dead methods before calling user code.
        # This avoids overwriting subscriptions made re-entrantly by a callback.
        live_entries: list[RegistryEntry] = []
        callbacks: list[Callback] = []
        for entry in self._callbacks:
            if isinstance(entry, weakref.WeakMethod):
                callback = entry()
                if callback is None:
                    continue
                live_entries.append(entry)
                callbacks.append(callback)  # strong for this publication only
            else:
                live_entries.append(entry)
                callbacks.append(entry)
        self._callbacks = live_entries
        # Policy: the first callback exception stops publication and propagates.
        for callback in callbacks:
            callback(event)

class Subscriber:
    def __init__(self) -> None:
        self.events: list[str] = []

    def on_event(self, event: str) -> None:
        self.events.append(event)

registry = WeakObserverRegistry()
subscriber = Subscriber()
registry.subscribe(subscriber.on_event)
registry.publish("loaded")
assert subscriber.events == ["loaded"]
function_events: list[str] = []
def record_event(event: str) -> None:
    function_events.append(event)
registry.subscribe(record_event)  # plain functions are retained strongly
registry.publish("finished")
assert function_events == ["finished"]
```

This implementation assumes calls and subscription mutation occur on one thread. Bound methods are weakly held; plain functions and other callables are held strongly, so their closures or callable instances can still retain captured state. The registry takes a callback snapshot before invocation, prunes dead methods, and lets the first callback exception stop publication and propagate. It does not implement unsubscribe or deduplication. For concurrent use, synchronize registry mutation/snapshot creation and invoke user callbacks outside the lock; verify behavior on the interpreter build deployed. WeakMethod requires a compatible bound method and weak-referenceable receiver.

### 5.2 Weak references do not automatically break every cycle

A weak reference only removes one ownership edge. If another strong path reaches the object, it stays alive. For example, a `WeakKeyDictionary` can still retain a key unexpectedly if the strongly held value points back to that key. Model the full object graph, not just the container type.

## 6. Intermediate: callbacks, finalizers, and cleanup

### 6.1 Weak-reference callbacks

`weakref.ref(obj, callback)` can register a callback that runs when the referent is about to be finalized. The callback receives the weak-reference object, not the referent (which is no longer available through that reference). Keep callbacks short, and do not close over or otherwise strongly retain the target. Callback order relative to other finalization activity is not a resource-management contract, and exceptions are reported as unraisable rather than propagated to the code that dropped the last reference.

```python
import gc
import weakref

class SessionState:
    pass

events: list[str] = []
state = SessionState()
probe = weakref.ref(state, lambda dead_ref: events.append("state collected"))
del state
gc.collect()
assert probe() is None
assert events == ["state collected"]
```

The callback captures `events`, not `state`; capturing the target (directly or through a bound method/closure) can keep it alive and prevent the callback from running. Use this callback for lightweight notification, not for mandatory or deterministic cleanup.

### 6.2 `weakref.finalize`

`weakref.finalize(obj, callback, *args, **kwargs)` registers a callback to run at most once when `obj` is about to be finalized, or at interpreter exit by default if still alive. It is generally safer than writing `__del__` for simple fallback cleanup, but it is not a deterministic resource-management substitute for `with` or explicit `close()`.

Critical rule: the finalizer callback's arguments and closure must not strongly retain `obj`, or the target may never become unreachable. Pass an independent resource handle or cleanup state rather than a bound method that retains the target.

```python
import tempfile
import weakref
from pathlib import Path

class TempArtifact:
    def __init__(self) -> None:
        handle = tempfile.NamedTemporaryFile(delete=False)
        self.path = Path(handle.name)
        handle.close()
        # Pass only the path, not `self` or a bound method retaining `self`.
        self._finalizer = weakref.finalize(self, self.path.unlink, missing_ok=True)

artifact = TempArtifact()
path = artifact.path
assert path.exists()
del artifact
# Collection/finalizer timing is not portable; test with a weakref probe and
# gc.collect() where appropriate. Prefer an explicit context manager in real code.
```

For production cleanup, prefer deterministic ownership:

```python
from pathlib import Path

class ManagedFile:
    def __init__(self, path: Path) -> None:
        self.path = path

    def close(self) -> None:
        self.path.unlink(missing_ok=True)

    def __enter__(self) -> "ManagedFile":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
```

This example is illustrative; a real resource wrapper should make `close()` idempotent and define whether it owns the file. The finalizer should be a safety net, not the primary contract.

### 6.3 `weakref.finalize` versus `__del__`

| Concern | `weakref.finalize` | `__del__` |
|---|---|---|
| Registration | Separate callback object | Special method on the instance's class |
| Common cycle hazard | Callback/arguments retaining target | Finalizer logic and object cycles can complicate collection |
| Timing | Not deterministic; also has interpreter-exit behavior | Not deterministic; interpreter shutdown can leave globals partially torn down |
| Exceptions | Callback exceptions are reported as unraisable | Destructor exceptions are also unraisable |
| Best role | Fallback cleanup with independent callback state | Rarely needed; avoid for ordinary resource management |

Do not rely on either for timely closing of files, sockets, transactions, locks, or database connections. Use context managers and explicit close methods. At interpreter shutdown, module globals may be cleared and thread state may be unavailable; callbacks should be minimal and robust.

### 6.4 `weakref.proxy`

`weakref.proxy(obj)` creates a proxy that forwards operations without keeping `obj` alive. It raises `ReferenceError` after the referent dies. It can be useful in narrowly controlled APIs, but it obscures the point where an object may disappear; an explicit `weakref.ref` with a `None` check is often easier to reason about.

## 7. Advanced: reference cycles and cyclic garbage collection

A reference cycle exists when objects refer to one another, directly or indirectly. A simple cycle is not necessarily a leak: Python's cyclic garbage collector can reclaim unreachable cycles containing ordinary tracked Python objects. Cycles can still retain memory when a live root reaches them, when a finalizer/extension behavior complicates collection, or when application code unintentionally keeps a root alive.

```python
import gc
import weakref

class Node:
    def __init__(self) -> None:
        self.other: Node | None = None

left = Node()
right = Node()
left.other = right
right.other = left
probe = weakref.ref(left)
del left, right
gc.collect()
assert probe() is None
```

`gc.collect()` requests a collection pass and is useful in tests. It does **not** prove that every kind of external resource has been released, nor should production code call it routinely as a substitute for fixing ownership. Garbage-collection behavior can vary by Python implementation, runtime configuration, and object type. Test semantic outcomes (such as a weakref becoming dead) instead of asserting a specific number of milliseconds until collection.

## 8. Copying custom objects and the `memo` contract

### 8.1 Implementing `__copy__`

The copy protocol can be customized. `__copy__(self)` returns a shallow copy. Preserve invariants, decide whether identity-sensitive fields should be shared, and do not accidentally duplicate external resources.

### 8.2 Implementing `__deepcopy__(self, memo)`

The `memo` dictionary is managed by the `copy` module. A custom `__deepcopy__` should:

1. Check `memo` for an existing clone when appropriate.
2. Allocate a clone before recursively copying fields if cycles are possible.
3. Store `memo[id(self)] = clone` before recursing into fields.
4. Use `copy.deepcopy(child, memo)` with the **same memo** for recursive children.
5. Explicitly share or recreate identity-sensitive state by design; do not blindly copy locks, sockets, files, sessions, or database handles.

```python
from __future__ import annotations

from copy import copy, deepcopy
from typing import Any

class PipelineNode:
    def __init__(self, name: str, children: list[PipelineNode] | None = None) -> None:
        self.name = name
        self.children = [] if children is None else children

    def __copy__(self) -> PipelineNode:
        clone = type(self).__new__(type(self))
        clone.__dict__.update(self.__dict__)
        return clone

    def __deepcopy__(self, memo: dict[int, Any]) -> PipelineNode:
        existing = memo.get(id(self))
        if existing is not None:
            return existing
        clone = type(self).__new__(type(self))
        memo[id(self)] = clone  # register before recursing to support cycles
        clone.name = deepcopy(self.name, memo)
        clone.children = deepcopy(self.children, memo)
        return clone

root = PipelineNode("root")
child = PipelineNode("child")
root.children.append(child)
root.children.append(root)  # a cycle
cloned = deepcopy(root)
assert cloned is not root
assert cloned.children[0] is not child
assert cloned.children[1] is cloned
```

The example is a deliberately small class with a `__dict__`. A slotted class, a class with descriptors, or a class with invariants may require a different implementation. If no special semantics are needed, rely on the built-in protocol rather than writing custom hooks.

### 8.3 External resources and identity

Deep-copying a data object is not equivalent to cloning a live resource. Consider a job object containing a database connection, a file descriptor, a lock, a logger, or a shared service client. Two independent copies may be meaningless or unsafe. A better design often copies only declarative configuration and injects shared resources into the new job, or provides an explicit `clone_for_run()` method that documents what is copied and what is shared.

Python 3.13 added `copy.replace(obj, **changes)`, which creates a same-type object with selected fields replaced for supported types (including named tuples, dataclasses, and classes implementing `__replace__`). It is a shallow field replacement, not a deep copy. Use it only when Python 3.13+ is the target; this lesson's baseline Python 3.12 examples do not require it.

## 9. Context variables: request-local and task-local state

### 9.1 Why mutable globals are a problem

A module global such as `current_request_id = ...` is shared by all code that imports that module. If concurrent requests overwrite it, logs and traces can be attributed to the wrong request. A lock around the global can serialize access, but does not make one global value represent multiple overlapping logical requests. Passing an explicit context object through every call is often the clearest option; `ContextVar` is useful when cross-cutting state (request IDs, trace IDs, locale, transaction context) must be available through a call chain without changing every signature.

`threading.local()` separates values by OS thread, but multiple `asyncio` tasks can interleave on the same thread. `ContextVar` is integrated with Python's execution context and supports task-local values.

### 9.2 `ContextVar`, `get`, `set`, and token reset

Create a `ContextVar` at module scope. Use `set(value)` to set the value in the current context; it returns a token representing the prior state. Reset that token in `finally` so nested calls restore the previous value instead of leaving a stale value behind.

```python
from contextvars import ContextVar

request_id: ContextVar[str | None] = ContextVar("request_id", default=None)

def handle_request(identifier: str) -> None:
    token = request_id.set(identifier)
    try:
        process_request()
    finally:
        request_id.reset(token)

def process_request() -> None:
    print(f"request={request_id.get()}")
```

The `try/finally` is essential. A token must be reset in the context in which it was created; reset tokens in the wrong context raise an error. Tokens are single-use for reset. Do not save tokens globally or reset an old token after unrelated work.

A `ContextVar` stores a reference to its value; it does not deep-copy values. Avoid using a shared mutable dictionary/list as the value unless shared mutation is intentional. Prefer immutable IDs, frozen context records, or a new value per request/task.

### 9.3 Logging filter pattern

```python
import logging
from contextvars import ContextVar

request_id: ContextVar[str] = ContextVar("request_id", default="-")

class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id.get()
        return True

logger = logging.getLogger("ingest")
handler = logging.StreamHandler()
handler.addFilter(RequestIdFilter())
handler.setFormatter(logging.Formatter("%(asctime)s %(request_id)s %(levelname)s %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Around each request:
# token = request_id.set("run-2026-10-17")
# try:
#     logger.info("batch started")
# finally:
#     request_id.reset(token)
```

For a real application, configure logging handlers once, avoid adding duplicate handlers on module reload, and ensure all records processed by the formatter have the custom attribute (for example, attach the filter at the handler/logger level consistently).

## 10. Context propagation across sync calls, tasks, threads, and executors

### 10.1 Synchronous calls and nested scopes

Context flows through ordinary synchronous calls made inside the current context. Token reset restores the value that existed before the scope, which is why nested request/span scopes can compose correctly.

### 10.2 `asyncio` tasks

When an `asyncio.Task` is created, it captures a context for that task (by default, a copy of the current context). Concurrent tasks can therefore hold different values even when they execute on the same OS thread. A task's context is not a mutable global shared with every other task.

```python
import asyncio
from contextvars import ContextVar

request_id: ContextVar[str] = ContextVar("request_id", default="-")

async def read_after_yield() -> str:
    await asyncio.sleep(0)
    return request_id.get()

async def demo() -> list[str]:
    async def one(identifier: str) -> str:
        token = request_id.set(identifier)
        try:
            return await read_after_yield()
        finally:
            request_id.reset(token)

    return await asyncio.gather(one("req-A"), one("req-B"))

assert asyncio.run(demo()) == ["req-A", "req-B"]
```

### 10.3 `copy_context()` and controlled propagation

`contextvars.copy_context()` returns a shallow copy of the current `Context`. `Context.run(callable, *args)` executes a synchronous callable in that context. The copied context contains references to values; it does not deep-copy them. Do not concurrently enter the same `Context` object from multiple threads; make separate copies when independent execution contexts are needed.

```python
from contextvars import ContextVar, copy_context
from concurrent.futures import ThreadPoolExecutor

trace_id: ContextVar[str] = ContextVar("trace_id", default="-")

def worker() -> str:
    return trace_id.get()

with ThreadPoolExecutor(max_workers=1) as pool:
    token = trace_id.set("trace-42")
    try:
        context = copy_context()
        future = pool.submit(context.run, worker)
        assert future.result() == "trace-42"
    finally:
        trace_id.reset(token)
```

Create a fresh `copy_context()` for each independently submitted job. A `Context` cannot be entered concurrently, and reusing one context across tasks may raise `RuntimeError` or cause unwanted state coupling.

### 10.4 Threads, `asyncio.to_thread`, and executor differences

Context is **not automatically propagated to arbitrary new threads or all executor work**. In supported modern Python, `asyncio.to_thread()` propagates the current context to the worker thread. By contrast, `loop.run_in_executor()` and `ThreadPoolExecutor.submit()` should not be assumed to propagate it; use `copy_context().run` explicitly when propagation is required.

```python
import asyncio
from contextvars import ContextVar

job_id: ContextVar[str] = ContextVar("job_id", default="-")

def blocking_operation() -> str:
    return job_id.get()

async def main() -> None:
    token = job_id.set("job-7")
    try:
        result = await asyncio.to_thread(blocking_operation)
        assert result == "job-7"
    finally:
        job_id.reset(token)

asyncio.run(main())
```

Be precise about the boundary: `to_thread()` propagates context from the calling async context for that call. It does not turn a `ContextVar` into a universal cross-process context carrier. Processes, remote workers, queues, and external services need explicit serialization/headers/metadata.

### 10.5 Version notes: free-threaded builds and Python 3.14

- Python 3.13 introduced experimental free-threaded CPython builds (often described as no-GIL builds). Python 3.14 continues this area; availability and performance depend on build and extension compatibility. Do not infer that arbitrary application code or third-party extensions are automatically thread-safe.
- Free-threaded execution makes explicit synchronization and ownership discipline more important. Weak containers and compound operations should not be treated as an application-level transaction. Use locks or other synchronization when a registry is mutated concurrently; validate behavior on the exact interpreter build deployed.
- Python 3.14 adds the `context` parameter to `threading.Thread`, allowing explicit thread-context behavior. Its default can depend on the interpreter build/configuration; pass an explicit context policy when correctness requires one. For propagation, pass a copied context's `run` callable or use the supported thread API intentionally. Do not make a blanket guarantee about context inheritance across all Python versions/builds.
- Python 3.14 also provides `concurrent.futures.InterpreterPoolExecutor`. Its workers execute in separate interpreters; do not expect an in-process `ContextVar` value or `Context` object to act as shared cross-interpreter state. Pass the needed request/trace metadata explicitly through supported, serializable task arguments.
- The target roadmap baseline is Python 3.12+. Treat 3.13+ and 3.14 APIs as optional/version-gated enhancements, not requirements for the core examples.

## 11. Memory-retention diagnosis and testing

### 11.1 A practical investigation sequence

1. **Define the suspected owner:** cache, global registry, task, closure, logger handler, or callback list.
2. **Use a weakref probe:** keep a `weakref.ref(obj)` and drop the expected strong references in a small test.
3. **Force a collection only for test diagnosis:** `gc.collect()` can make unreachable cycles easier to test, but it does not model production timing.
4. **Compare allocations with `tracemalloc`:** start tracing before the workload, take snapshots, compare by filename/traceback, and reproduce the same workload. A snapshot reports traced Python allocations, not every native allocation or all process RSS.
5. **Inspect growth and roots:** repeat the same operation, observe whether live objects or allocation sites grow, and inspect application ownership paths. One high memory reading or one surviving object does not prove a leak.
6. **Test cleanup semantics:** explicitly close resources, cancel/await tasks, unsubscribe observers, clear bounded caches, and restore context in `finally`.

### 11.2 Weakref-based tests

A good lifecycle test holds only a weak reference to the target after the operation under test. If the test itself retains the object through a local, fixture, traceback, callback, or closure, collection will not occur. In CPython, local-variable lifetimes and frame retention can make interactive experiments misleading; isolate creation in a helper function when necessary.

### 11.3 `tracemalloc` snapshot sketch

```python
import tracemalloc

tracemalloc.start()
before = tracemalloc.take_snapshot()

# Run a repeatable workload here.

later = tracemalloc.take_snapshot()
for stat in later.compare_to(before, "lineno")[:10]:
    print(stat)
```

Take snapshots at comparable workload boundaries and interpret the output. `tracemalloc` tracks many Python allocations but not every native allocation made by extensions or the total resident set size. Use OS/process metrics when investigating total memory.

## 12. Common mistakes and corrections

| Mistake | Why it fails | Better approach |
|---|---|---|
| Expecting `copy.copy()` to isolate nested lists/dicts | It copies only the outer structure for common containers | Use targeted copies or `deepcopy()` if full graph duplication is intended |
| Calling `deepcopy()` on a live service/client/resource graph | May be unsupported, costly, or semantically invalid | Copy declarative state; inject or deliberately share resources |
| Assuming every object supports `weakref.ref()` | Built-ins and slotted classes may not support weak refs | Check eligibility; add `__weakref__` / `weakref_slot=True` where appropriate |
| Treating a weak-value cache as durable storage | Values can disappear when other owners release them | Use an owning bounded cache or persistent store when availability matters |
| Storing `subscriber.on_event` strongly in a long-lived registry | The bound method retains `subscriber` | Use `WeakMethod` if the registry should not own the subscriber |
| Assuming weak containers always eliminate cycles | Other strong paths or values pointing back to keys can retain objects | Analyze the complete object graph and roots |
| Using finalizers to close critical resources promptly | Collection and shutdown timing are nondeterministic | Use context managers and explicit cleanup; finalizers only as fallback |
| Resetting a context token outside its originating context | Token is context-specific and single-use | Reset in `finally` around the same logical scope |
| Putting a mutable dict in a `ContextVar` and mutating it across tasks | Context copies still reference the same mutable value | Use immutable values or create per-task state |
| Assuming all thread/executor work inherits context | Propagation depends on API and version | Use `asyncio.to_thread()` or explicitly submit `copy_context().run` |
| Decorating a method with unbounded `lru_cache` without considering `self` | The cache key can retain each instance | Bound/clear the cache or use an appropriate per-instance design |
| Calling `gc.collect()` in production to “fix” growth | It does not remove reachable objects or fix ownership | Find the retaining root and apply an explicit lifecycle policy |

## 13. Tested examples: focused pytest suite

Save the following as `test_weakref_contextvars_copy.py` and run `python -m pytest -q test_weakref_contextvars_copy.py`. It uses only the standard library plus pytest. The tests use `gc.collect()` as a diagnostic aid and test observable semantics rather than a fixed collection delay.

```python
from __future__ import annotations

import asyncio
import gc
import weakref
from concurrent.futures import ThreadPoolExecutor
from contextvars import ContextVar, copy_context
from copy import copy, deepcopy
from functools import lru_cache

import pytest


class Box:
    def __init__(self, value: object) -> None:
        self.value = value


def make_weak_probe() -> tuple[Box, weakref.ReferenceType[Box]]:
    obj = Box([])
    return obj, weakref.ref(obj)


def test_shallow_and_deep_copy_nested_mutable_values() -> None:
    original = {"nested": {"values": [1]}}
    shallow = copy(original)
    deep = deepcopy(original)

    assert shallow is not original
    assert shallow["nested"] is original["nested"]
    assert deep["nested"] is not original["nested"]

    shallow["nested"]["values"].append(2)
    assert original["nested"]["values"] == [1, 2]
    deep["nested"]["values"].append(3)
    assert original["nested"]["values"] == [1, 2]


def test_deepcopy_preserves_shared_references_and_cycles() -> None:
    shared: list[object] = []
    original: list[object] = [shared, shared]
    original.append(original)

    cloned = deepcopy(original)
    assert cloned is not original
    assert cloned[0] is cloned[1]
    assert cloned[0] is not shared
    assert cloned[2] is cloned


def test_weak_reference_target_can_be_collected() -> None:
    obj, probe = make_weak_probe()
    assert probe() is obj
    del obj
    gc.collect()
    assert probe() is None


def test_weak_value_dictionary_does_not_own_value() -> None:
    cache: weakref.WeakValueDictionary[str, Box] = weakref.WeakValueDictionary()
    obj = Box("cached")
    probe = weakref.ref(obj)
    cache["key"] = obj
    assert cache["key"] is obj

    del obj
    gc.collect()
    assert probe() is None
    assert "key" not in cache


def test_weak_method_registry_does_not_own_subscriber() -> None:
    class Subscriber:
        def on_event(self, event: str) -> None:
            pass

    callbacks: list[weakref.WeakMethod] = []
    subscriber = Subscriber()
    probe = weakref.ref(subscriber)
    callbacks.append(weakref.WeakMethod(subscriber.on_event))

    del subscriber
    gc.collect()
    assert probe() is None
    assert callbacks[0]() is None


def test_lru_cache_on_instance_method_can_retain_self() -> None:
    class Service:
        @lru_cache(maxsize=None)
        def calculate(self, value: int) -> int:
            return value * 2

    service = Service()
    probe = weakref.ref(service)
    assert service.calculate(3) == 6
    del service
    gc.collect()
    # The class-level lru_cache wrapper holds `self` in its cache key.
    assert probe() is not None
    Service.calculate.cache_clear()
    gc.collect()
    assert probe() is None


def test_observer_registry_supports_plain_functions_and_weak_methods() -> None:
    class Subscriber:
        def __init__(self) -> None:
            self.events: list[str] = []

        def on_event(self, event: str) -> None:
            self.events.append(event)

    # Keep this test self-contained instead of importing an example from a Markdown fence.
    class Registry:
        def __init__(self) -> None:
            self.callbacks: list[object] = []

        def subscribe(self, callback: object) -> None:
            if getattr(callback, "__self__", None) is not None and getattr(callback, "__func__", None) is not None:
                self.callbacks.append(weakref.WeakMethod(callback))
            else:
                self.callbacks.append(callback)

        def publish(self, event: str) -> None:
            callbacks = []
            live = []
            for entry in self.callbacks:
                if isinstance(entry, weakref.WeakMethod):
                    callback = entry()
                    if callback is not None:
                        live.append(entry)
                        callbacks.append(callback)
                else:
                    live.append(entry)
                    callbacks.append(entry)
            self.callbacks = live
            for callback in callbacks:
                callback(event)

    registry = Registry()
    subscriber = Subscriber()
    probe = weakref.ref(subscriber)
    registry.subscribe(subscriber.on_event)
    function_events: list[str] = []
    registry.subscribe(lambda event: function_events.append(event))
    registry.publish("first")
    assert subscriber.events == ["first"]
    assert function_events == ["first"]
    del subscriber
    gc.collect()
    assert probe() is None
    registry.publish("second")
    assert function_events == ["first", "second"]


def test_context_token_reset_restores_previous_value() -> None:
    variable: ContextVar[str] = ContextVar("test_variable", default="default")
    outer = variable.set("outer")
    try:
        inner = variable.set("inner")
        assert variable.get() == "inner"
        variable.reset(inner)
        assert variable.get() == "outer"
    finally:
        variable.reset(outer)
    assert variable.get() == "default"


def test_async_tasks_have_isolated_context_values() -> None:
    variable: ContextVar[str] = ContextVar("async_variable", default="-")

    async def read_after_yield() -> str:
        await asyncio.sleep(0)
        return variable.get()

    async def task(value: str) -> str:
        token = variable.set(value)
        try:
            return await read_after_yield()
        finally:
            variable.reset(token)

    async def main() -> list[str]:
        return await asyncio.gather(task("A"), task("B"))

    assert asyncio.run(main()) == ["A", "B"]
    assert variable.get() == "-"


def test_copy_context_explicitly_propagates_to_executor() -> None:
    variable: ContextVar[str] = ContextVar("executor_variable", default="-")
    token = variable.set("job-9")
    try:
        context = copy_context()
        with ThreadPoolExecutor(max_workers=1) as pool:
            result = pool.submit(context.run, variable.get).result()
        assert result == "job-9"
    finally:
        variable.reset(token)


def test_asyncio_to_thread_propagates_context() -> None:
    variable: ContextVar[str] = ContextVar("to_thread_variable", default="-")

    async def main() -> str:
        token = variable.set("job-12")
        try:
            return await asyncio.to_thread(variable.get)
        finally:
            variable.reset(token)

    assert asyncio.run(main()) == "job-12"
    assert variable.get() == "-"


def test_context_value_is_not_deep_copied() -> None:
    variable: ContextVar[list[str]] = ContextVar("mutable_context", default=[])
    value = ["shared"]
    token = variable.set(value)
    try:
        context = copy_context()
        assert context.run(variable.get) is value
    finally:
        variable.reset(token)


def test_unsupported_builtin_weakref_raises_type_error() -> None:
    with pytest.raises(TypeError):
        weakref.ref([])
```

**Expected result:** 13 tests pass on the target runtime. The weak-reference tests rely on dropping strong references and then asking the collector to process unreachable objects; they do not claim that all Python implementations collect every object immediately or identically.

## 14. Hands-on exercises

1. **Aliasing audit:** write a nested dictionary with two keys referencing the same list. Compare assignment, `copy.copy`, and `copy.deepcopy`; state which identities are shared.
2. **Weak cache:** extend `PlanIndex` with a `__len__` method and write a test showing the value disappears when the caller drops its strong reference. Ensure the test does not retain the value in an assertion local.
3. **Observer registry:** support `unsubscribe()` and dead-reference cleanup. Define how duplicate subscriptions and callback exceptions should behave.
4. **Context scope:** write a decorator or context manager that sets a `ContextVar`, invokes a function, and resets the token even if the function raises. Test nesting and exceptions.
5. **Executor propagation:** compare `ThreadPoolExecutor.submit(worker)` with `submit(copy_context().run, worker)` while a variable is set. Avoid assuming the unwrapped call inherited the context; assert the explicitly propagated case.
6. **Copy protocol:** add a non-copyable resource-like field to a custom class. Decide whether deep copy should share it, reconstruct it, omit it, or raise a clear exception, and document the policy.
7. **Retention diagnosis:** create a deliberately strong callback registry, demonstrate that a subscriber stays alive, then replace it with `WeakMethod` and show the target can be collected.
8. **Memory observations:** take `tracemalloc` snapshots around a repeatable allocation workload. Explain why a positive diff is not by itself proof of a leak.

## 15. Mini-project: request-aware weak observer hub

Build a small event hub for a data-ingestion process. It should:

- Store bound-method subscribers weakly using `weakref.WeakMethod` so the hub does not own subscriber lifetimes.
- Attach a `ContextVar` request/run ID to each publication and ensure it is reset in `finally`.
- Offer `subscribe`, `publish`, and dead-subscriber cleanup; specify whether callback exceptions stop publication or are collected/reported.
- Keep the event payload immutable or clearly document ownership; do not use a shared mutable context value as implicit per-request state.
- Include pytest tests for subscriber collection, nested context restoration, async task isolation, and explicit executor propagation.
- Include a short design note describing why a weak registry is appropriate and when a strong registry would be better.

**Acceptance criteria:** all tests pass; no test relies on a sleep-based collection race; `gc.collect()` is used only as a test aid; token reset occurs in `finally`; executor propagation is explicit; no finalizer is used for required cleanup; the module documents its thread-safety policy.

## 16. Self-check with explained answers

### 1. Why does a shallow copy still share nested lists?

Because a shallow copy creates a new outer container while copying references to its members. The nested list is the same object, so mutations through either path are visible to both structures. Use a deep copy or a targeted copy if nested independence is required.

### 2. Why can a weak-value cache lose an entry even though the key still exists?

The key is held strongly, but the value is held weakly. When no other strong reference keeps the value alive, the object can be collected and the weak dictionary removes the entry. This is suitable only when the cache is an index, not the authoritative owner of the value.

### 3. Why is a strong `lru_cache` sometimes safer than a weak cache, and sometimes a retention risk?

It reliably keeps computed values available until eviction/clearing, which is useful for memoization. The same strong retention can grow memory when the key space is unbounded, and a cached instance method may retain `self` through its cache key. Bound the cache or choose another ownership design when appropriate.

### 4. Why use `WeakMethod` instead of `weakref.ref(instance.method)`?

A bound method object is temporary and contains a reference to its receiver. `WeakMethod` is designed to reconstruct a bound method while its instance and underlying function remain alive, without a long-lived strong reference to the instance.

### 5. Why is `weakref.finalize` not a replacement for a context manager?

Finalizer execution timing is nondeterministic and shutdown state may be partially dismantled. Context managers define a deterministic lexical cleanup boundary, including on exceptions. Finalizers are fallback cleanup, not the primary lifecycle contract.

### 6. Why must `__deepcopy__` store a clone in `memo` before copying children?

A child can refer back to the parent, directly or indirectly. Registering the clone first lets recursive copying find the existing clone and preserve cycles and repeated references instead of recursing forever or creating inconsistent duplicates.

### 7. Why reset a `ContextVar` token instead of setting a default value?

Reset restores the exact previous state, including an outer nested scope's value and whether the variable was previously unset. Setting a guessed default can destroy that surrounding context. Tokens are specific to the context and must be reset in the same logical context.

### 8. Do `asyncio` tasks and arbitrary threads receive context in the same way?

No. Tasks capture execution context when created, while arbitrary new threads and executor work should not be assumed to inherit it. `asyncio.to_thread()` propagates the current context; for other executor APIs, explicitly submit `copy_context().run` when propagation is needed.

### 9. Does `gc.collect()` prove that a production memory leak is fixed?

No. It requests collection of unreachable objects but cannot collect objects that remain reachable from a live root. It also says little about native allocations or total process RSS. Use weakref probes, repeated workloads, allocation snapshots, and ownership-path inspection together.

### 10. Should a database connection be deep-copied along with a job object?

Usually not. A connection is a live external resource with identity and lifecycle semantics, not plain data. Copy the job's declarative configuration and inject or deliberately share the connection, or provide an explicit clone method with a documented resource policy.

## 17. Final reference checklist

- [ ] I can explain identity, strong references, reachability, aliasing, and why `del` only removes a binding.
- [ ] I can predict when `copy.copy()` shares nested mutable objects and when `deepcopy()` is appropriate.
- [ ] I understand that deep copy preserves cycles/repeated references through `memo` and can be customized.
- [ ] I avoid generic copying of files, sockets, locks, connections, tasks, and other identity-sensitive resources.
- [ ] I can test weak-reference eligibility and use `weakref.ref` without assuming the referent stays alive.
- [ ] I can choose between weak-value caches, weak-key metadata, weak sets, and strong bounded caches based on ownership semantics.
- [ ] I understand strong retention from dictionaries, callback registries, bound methods, and `lru_cache`.
- [ ] I can use `WeakMethod` for non-owning bound-method subscriptions.
- [ ] I use `weakref.finalize` only as fallback cleanup and prefer explicit resource lifecycle management.
- [ ] I set and reset `ContextVar` values with tokens in `try/finally`.
- [ ] I understand that context values are references, not deep-copied values.
- [ ] I can explain task-local context and explicitly propagate context to executor work when needed.
- [ ] I treat free-threaded builds and version-specific thread-context behavior as runtime-specific, not as blanket thread-safety guarantees.
- [ ] I use `gc.collect()` and `tracemalloc` as diagnostic tools, not proof by themselves.
- [ ] I have completed the exercises and mini-project with tests for lifetime, copy semantics, and context isolation.

**Next:** Module 13 README and practice questions; then Module 14 — Bytes, Binary Data and Advanced Text Processing.
