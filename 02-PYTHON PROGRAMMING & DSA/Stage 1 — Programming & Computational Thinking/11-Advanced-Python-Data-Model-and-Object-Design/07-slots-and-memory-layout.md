# Lesson 07 — Slots and Memory Layout

> **Module 11 — Advanced Python Data Model and Object Design**  
> **Target:** Python 3.12+ (CPython implementation details are labelled explicitly)  
> **Primary use case:** deciding whether `__slots__` is justified for large populations of small objects.

## Learning objectives

After this lesson, you should be able to:

- Explain the conventional instance dictionary model and what `__slots__` changes.
- Declare, initialize, read, and assign slot attributes correctly.
- Distinguish shallow object size from the retained memory of an object graph.
- Compare ordinary and slotted instances using `sys.getsizeof` and `tracemalloc` without inventing universal savings.
- Explain dynamic-attribute restrictions, the `__dict__` and `__weakref__` opt-ins, and slot member descriptors.
- Predict how slots interact with inheritance, unslotted bases, duplicate names, and multiple inheritance.
- Recognize implications for `cached_property`, properties, pickling, weak references, and dataclasses.
- Decide when ordinary classes, slotted classes, `dataclass(slots=True)`, `NamedTuple`, arrays, or columnar storage fit the workload.
- Avoid common slot mistakes and answer the roadmap self-check questions.

## Prerequisites

You should know classes and instances, `__init__`, instance and class attributes, inheritance, properties and descriptors, exceptions, and basic profiling. You do not need to know CPython C internals; those details are introduced only to explain why measurement varies.

## 1. Mental model: an instance is not just its fields

Consider a typical class:

```python
class Event:
    def __init__(self, event_id: int, kind: str) -> None:
        self.event_id = event_id
        self.kind = kind


event = Event(101, "created")
print(event.event_id, event.kind)
print(event.__dict__)
```

Expected output:

```text
101 created
{'event_id': 101, 'kind': 'created'}
```

For a typical user-defined class with no slots, each instance can carry an instance dictionary, accessible through `obj.__dict__`. That dictionary maps attribute names to values. The values themselves are references to Python objects; the dictionary does not inline the integer or string payloads.

The usual mental model is:

```text
Event class
  ├── methods and class attributes
  └── instance layout policy
          |
          v
event instance
  ├── object/runtime bookkeeping
  ├── instance dictionary ──> "event_id" ──> integer object
  │                         └─ "kind" ─────> string object
  └── possibly weak-reference support
```

This diagram is conceptual, not a byte-accurate CPython memory map. Exact layout depends on Python implementation, version, class shape, and allocator behavior.

### Why instance dictionaries are useful

They support flexible object shapes:

```python
class Event:
    def __init__(self, event_id: int, kind: str) -> None:
        self.event_id = event_id
        self.kind = kind


event = Event(101, "created")
event.source = "api"
event.debug_note = "replayed"
print(event.__dict__)
```

Expected output:

```text
{'event_id': 101, 'kind': 'created', 'source': 'api', 'debug_note': 'replayed'}
```

Dynamic attributes are convenient for debugging, monkeypatching, plugin systems, and evolving object models. The cost is that an instance dictionary has overhead beyond the object itself. For millions of objects with only a few stable fields, that overhead may become material.

## 2. What `__slots__` changes

Declaring `__slots__` tells Python to create descriptors for named attributes and reserve storage for them in the instance layout. For a class that has no instance dictionary through itself or its bases, this prevents arbitrary new instance attributes and usually avoids a per-instance dictionary.

```python
class EventSlot:
    __slots__ = ("event_id", "kind")

    def __init__(self, event_id: int, kind: str) -> None:
        self.event_id = event_id
        self.kind = kind


event = EventSlot(101, "created")
print(event.event_id, event.kind)
print(hasattr(event, "__dict__"))
```

Expected output:

```text
101 created
False
```

The slot names must be declared in `__slots__` before instances are created. A string is accepted as one slot name—even when it contains multiple characters; Python does not split it into one slot per character. A tuple is clearer and makes the intended collection of names explicit.

```python
class OneSlot:
    __slots__ = ("value",)  # The trailing comma makes this a one-item tuple.
```

### Attribute restrictions

```python
class Point:
    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


point = Point(2.0, 4.0)
try:
    point.label = "origin"
except AttributeError as exc:
    print(type(exc).__name__)
```

Expected output:

```text
AttributeError
```

This restriction is not a security boundary. Code can still mutate declared slots, and class-level behavior can be changed where Python permits it. Slots are a storage/layout choice, not access control.

## 3. The descriptor mechanics behind slots

A slot name is represented on the class by a built-in member descriptor. That descriptor maps normal attribute syntax such as `point.x` to the instance's reserved slot storage.

```python
class Coordinate:
    __slots__ = ("x",)

coordinate = Coordinate()
coordinate.x = 7

print(coordinate.x)
print(type(Coordinate.x).__name__)
print(Coordinate.x)
```

Expected output:

```text
7
member_descriptor
<member 'x' of 'Coordinate' objects>
```

The last line is a representative CPython display of the member descriptor; descriptor representations are implementation-specific. The important invariant is that `Coordinate.x` is a descriptor, while `coordinate.x` is the value stored in that instance's slot.

This connects slots to the descriptor protocol covered in Lesson 06: attribute reads and writes are mediated by a class-level descriptor. A slot descriptor is not the same as a normal entry in `coordinate.__dict__`.

Uninitialized slots raise `AttributeError` on read:

```python
class Pair:
    __slots__ = ("left", "right")

pair = Pair()
try:
    print(pair.left)
except AttributeError as exc:
    print(type(exc).__name__)
```

Expected output:

```text
AttributeError
```

## 4. Memory measurement: know what you are measuring

There is no universal statement such as “slots save exactly N bytes per instance.” The result depends on interpreter version, number of fields, whether dictionaries are key-shared, object graph shape, allocator behavior, and the way the experiment is run.

Use two tools for different questions:

- `sys.getsizeof(obj)` reports the shallow size attributed to that object by the current implementation. It does **not** recursively count referenced values or the full object graph.
- `tracemalloc` records Python memory allocations made after tracing starts. It can compare aggregate allocation deltas for a controlled experiment, but it is not a complete measurement of process RSS or every native allocation.

### 4.1 Shallow size: ordinary versus slotted

```python
import sys


class PointDict:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


class PointSlots:
    __slots__ = ("x", "y")

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


ordinary = PointDict(1, 2)
slotted = PointSlots(1, 2)

print("ordinary instance:", sys.getsizeof(ordinary))
print("ordinary dictionary:", sys.getsizeof(ordinary.__dict__))
print("slotted instance:", sys.getsizeof(slotted))
```

Expected behavior: the program prints three integer sizes for the current interpreter. Do not copy numbers from another machine into documentation as universal constants. The ordinary instance's dictionary size is reported separately, while the slotted object's shallow size includes its slot storage as accounted for by that implementation. The integer values `1` and `2` are separate referenced objects and are not recursively included by these calls.

The sum `sys.getsizeof(ordinary) + sys.getsizeof(ordinary.__dict__)` is a useful limited comparison for this small example, but still is not the total memory of the graph. It omits the sizes of referenced field values and any other objects the instance refers to.

### 4.2 Why dictionary sharing complicates comparisons

CPython has used key-sharing dictionaries for instances of many classes (PEP 412), allowing instances of the same class to share dictionary key metadata. CPython 3.11 also introduced inline values for many instance dictionaries, changing how instance attribute values are stored. These optimizations reduce the overhead of ordinary objects compared with simplistic “a full independent hash table per instance” mental models.

These are CPython implementation details, not guarantees for every Python implementation. They also mean `sys.getsizeof(obj.__dict__)` can vary with access patterns and runtime version. Measure on the interpreter and workload you actually deploy.

### 4.3 Aggregate experiment with `tracemalloc`

The following script measures allocations after tracing starts and reports observed values instead of embedding a fabricated benchmark result. It uses the same number of objects and the same payload values in each run. The integer key objects are created before tracing and reused in both comparisons; the literal status string is also shared. The measured delta therefore emphasizes the row instances, their per-instance storage, and the retained list, rather than a complete independently allocated payload graph.

```python
import gc
import tracemalloc


class RowDict:
    def __init__(self, key: int, status: str) -> None:
        self.key = key
        self.status = status


class RowSlots:
    __slots__ = ("key", "status")

    def __init__(self, key: int, status: str) -> None:
        self.key = key
        self.status = status


def measure_allocated_bytes(factory, keys: list[int]) -> int:
    """Measure retained rows and their list, reusing pre-created key objects."""
    gc.collect()
    tracemalloc.start()
    before, _ = tracemalloc.get_traced_memory()
    rows = [factory(key, "ok") for key in keys]
    current, _ = tracemalloc.get_traced_memory()
    delta = current - before
    # Keep rows alive until after the measurement; release them before stopping.
    assert len(rows) == len(keys)
    del rows
    tracemalloc.stop()
    return delta


if __name__ == "__main__":
    count = 100_000  # Increase to 1_000_000 when time and memory permit.
    keys = list(range(count))  # Created before tracing in both comparisons.
    dict_bytes = measure_allocated_bytes(RowDict, keys)
    slots_bytes = measure_allocated_bytes(RowSlots, keys)

    print(f"count: {count:,}")
    print(f"ordinary traced delta: {dict_bytes:,} bytes")
    print(f"slotted traced delta:  {slots_bytes:,} bytes")
    if slots_bytes:
        print(f"observed ratio (ordinary / slotted): {dict_bytes / slots_bytes:.3f}x")
```

Expected behavior: the script prints the measured byte deltas and a ratio for the current runtime. The exact numbers and ratio are environment-dependent; no fixed result is promised here.

**Methodology notes:**

1. Run both classes in the same interpreter build, with the same count and construction pattern.
2. Start tracing before the objects are created and retain the list until after reading the current traced allocation.
3. Collect garbage before each run; avoid measuring unrelated work in the same process.
4. Repeat runs, compare medians, and report the Python implementation/version, OS, count, field count, and whether payload objects are included.
5. For the roadmap's one-million-instance check, set `count = 1_000_000` only when sufficient memory is available. Do not assume the experiment is safe on every development machine.
6. This measurement captures traced Python allocations, not complete process resident memory. For process-level memory use, use an OS-aware measurement tool as a separate experiment.
7. This particular benchmark intentionally creates `"ok"` and integer values through repeated references/construction patterns that may be optimized or shared by the runtime. It is primarily a comparison of instance representation overhead, not a realistic end-to-end event pipeline.

### 4.4 A fairer object-graph experiment

If the production question is “how much memory does a million complete event records retain?”, include the payload graph deliberately and identically for both designs. For example, create distinct strings or nested values in both cases, retain all objects, and measure the whole construction interval. State whether payloads are shared or unique. Never compare one case with pre-created payloads against another case that allocates payloads inside the measured interval.

`tracemalloc` is a diagnostic, not a perfect census. It traces Python memory allocations; native buffers in third-party extensions and total process overhead may need additional tools. Use it to answer a clearly defined comparison question, not as a synonym for RSS.

## 5. Opting back into an instance dictionary or weak references

Slots remove features only if neither the class nor its bases provides them. You can opt back in:

```python
class FlexibleSlots:
    __slots__ = ("value", "__dict__")

    def __init__(self, value: int) -> None:
        self.value = value


item = FlexibleSlots(3)
item.extra = "allowed"
print(item.value, item.extra)
print(item.__dict__)
```

Expected output:

```text
3 allowed
{'extra': 'allowed'}
```

The declared `value` slot remains slot-backed; arbitrary attributes such as `extra` are held in the dictionary. Adding `__dict__` reduces the benefit of slots and should be justified by the required dynamic behavior.

Weak references are separate:

```python
import weakref


class Weakable:
    __slots__ = ("value", "__weakref__")

    def __init__(self, value: int) -> None:
        self.value = value


obj = Weakable(8)
reference = weakref.ref(obj)
print(reference() is obj)
```

Expected output:

```text
True
```

Without `__weakref__`, a pure-slotted instance generally cannot be the target of a weak reference unless a base class already supplies weak-reference support. Weak references are used by weak mappings, caches, observer registries, and lifecycle-aware infrastructure.

## 6. Inheritance: slots are a class-hierarchy decision

### 6.1 A subclass without `__slots__` gets a dictionary

```python
class SlottedBase:
    __slots__ = ("base_value",)

    def __init__(self, base_value: int) -> None:
        self.base_value = base_value


class UnslottedChild(SlottedBase):
    pass


child = UnslottedChild(10)
child.extra = "works"
print(child.base_value, child.extra)
print(hasattr(child, "__dict__"))
```

Expected output:

```text
10 works
True
```

A subclass that omits `__slots__` receives the normal instance dictionary even when its base is slotted. The inherited `base_value` remains slot-backed, but new attributes can be stored in the subclass dictionary. To keep the subclass dictionary-free, explicitly declare empty slots:

```python
class SlottedBase:
    __slots__ = ("base_value",)

    def __init__(self, base_value: int) -> None:
        self.base_value = base_value


class SlottedChild(SlottedBase):
    __slots__ = ()
```

An empty tuple means the subclass adds no new slots and does not introduce an instance dictionary of its own. The base's slots remain available.

### 6.2 Declare only new names

```python
class BaseRecord:
    __slots__ = ("record_id",)


class GoodRecord(BaseRecord):
    __slots__ = ("status",)


record = GoodRecord()
record.record_id = 12
record.status = "ready"
print(record.record_id, record.status)
```

Expected output:

```text
12 ready
```

Avoid repeating `record_id` in the subclass's `__slots__`. Redeclaring an inherited slot name can shadow the base descriptor and lead to confusing behavior; the Python documentation warns that the meaning of duplicate slot names is undefined. Declare only genuinely new slot names.

### 6.3 Unslotted bases and mixins

If a base class has an instance dictionary, a subclass cannot remove that inherited dictionary merely by declaring slots. The instance still supports dynamic attributes because the base layout allows them.

```python
class DynamicMixin:
    pass


class SlottedButDynamic(DynamicMixin):
    __slots__ = ("value",)


instance = SlottedButDynamic()
instance.value = 1
instance.extra = 2
print(instance.value, instance.extra)
print(hasattr(instance, "__dict__"))
```

Expected output:

```text
1 2
True
```

This is why slots require hierarchy-wide design awareness. A mixin intended to cooperate with slotted classes can use `__slots__ = ()` if it does not need per-instance storage.

### 6.4 Multiple inheritance and layout conflicts

Python can combine multiple bases when their instance layouts are compatible. However, **multiple inheritance from two unrelated bases that both define non-empty slot layouts commonly raises `TypeError` due to layout conflicts**.

```python
class Left:
    __slots__ = ("left",)


class Right:
    __slots__ = ("right",)


try:
    class Combined(Left, Right):
        __slots__ = ()
except TypeError as exc:
    print(type(exc).__name__)
```

Expected output:

```text
TypeError
```

Do not treat every combination of slot-bearing bases as invalid: compatibility depends on the actual base layouts. The safe design rule is to avoid multiple independent non-empty slotted layouts unless the hierarchy has been deliberately designed and tested. Prefer one storage-bearing base plus stateless mixins (often `__slots__ = ()`) when appropriate.

## 7. Slot name collisions and class-level defaults

This is incorrect:

```python
class Incorrect:
    __slots__ = ("status",)
    status = "new"  # Incorrect: conflicts with the slot descriptor.
```

A slot is represented by a descriptor at the class level, so a class attribute with the same name would overwrite/conflict with that descriptor. Define defaults in `__init__` instead:

```python
class Job:
    __slots__ = ("status",)

    def __init__(self, status: str = "new") -> None:
        self.status = status


print(Job().status)
print(Job("done").status)
```

Expected output:

```text
new
done
```

For immutable defaults, constructor defaults are straightforward. For mutable per-instance defaults, create a fresh object inside `__init__` or use a `default_factory` in a dataclass; do not share a mutable class-level object by accident.

## 8. Slots, properties, and cached properties

### 8.1 Properties can use a slot as backing storage

```python
class Celsius:
    __slots__ = ("_value",)

    def __init__(self, value: float) -> None:
        self.value = value

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, new_value: float) -> None:
        if new_value < -273.15:
            raise ValueError("temperature is below absolute zero")
        self._value = new_value


temperature = Celsius(20.0)
print(temperature.value)
try:
    temperature.value = -300.0
except ValueError as exc:
    print(type(exc).__name__)
```

Expected output:

```text
20.0
ValueError
```

The property is a descriptor; `_value` is the declared slot. The class must not declare a slot named `value` while also defining a property named `value`, because those class attributes would conflict.

### 8.2 `cached_property` requires a mutable instance dictionary

`functools.cached_property` writes its computed value into the instance dictionary under the property's name. It therefore does not work on a pure-slotted instance that has no `__dict__`.

```python
from functools import cached_property


class SlottedReport:
    __slots__ = ("rows",)

    def __init__(self, rows: tuple[int, ...]) -> None:
        self.rows = rows

    @cached_property
    def total(self) -> int:
        return sum(self.rows)


report = SlottedReport((1, 2, 3))
try:
    print(report.total)
except TypeError as exc:
    print(type(exc).__name__)
```

Expected output on CPython 3.12+:

```text
TypeError
```

If caching is required, alternatives include adding `"__dict__"` to the slots, storing a dedicated cache slot with a sentinel and explicit invalidation, or using a custom descriptor with an external store. Adding a dictionary partly defeats the memory objective; a dedicated cache slot is more explicit but needs careful invalidation semantics.

## 9. Pickling and object protocols

Slotted classes can be pickled in Python 3.x when the class and its state are supported by the pickle protocol; the roadmap specifies protocol 2+ for the relevant built-in slot support. Actual success still depends on the object's state, the class being importable by pickle, custom `__getstate__`/`__setstate__` logic, and any inherited dictionary or slots. Do not generalize this to every object graph or every custom class.

```python
import pickle


class SlottedPoint:
    __slots__ = ("x", "y")

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


point = SlottedPoint(3, 4)
restored = pickle.loads(pickle.dumps(point, protocol=pickle.HIGHEST_PROTOCOL))
print(restored.x, restored.y)
```

Expected output:

```text
3 4
```

Test pickling with the actual Python versions, protocols, and data your application supports. Classes with custom `__new__`, custom state methods, extension-backed values, or complex inheritance may need explicit state handling. Do not use pickle with untrusted input.

Other protocols are affected indirectly by storage layout. For example, serializers that assume `obj.__dict__` exists will fail on pure-slotted objects. Prefer documented serialization methods or explicit field enumeration rather than assuming every object has a dictionary.

## 10. Dataclasses and compact record alternatives

### 10.1 `dataclass(slots=True)`

Python 3.10+ supports `slots=True` in `dataclasses.dataclass`. It creates and returns a new class with slots, rather than merely toggling a flag on the original class. This detail matters for decorators, class identity, inheritance, and code that captures the original class object.

```python
from dataclasses import dataclass


@dataclass(slots=True)
class EventRecord:
    event_id: int
    kind: str


event = EventRecord(7, "updated")
print(event)
print(hasattr(event, "__dict__"))
```

Expected output:

```text
EventRecord(event_id=7, kind='updated')
False
```

`dataclass(slots=True)` is often a convenient choice for stable data-transfer objects. Check the Python version and inheritance rules in the deployment target. Dataclass slot generation omits slots already present in base classes in modern Python; do not rely on `__slots__` as the source of dataclass field metadata—use `dataclasses.fields()`.

### 10.2 Empty-slot mixins with slotted dataclasses

A mixin that does not store per-instance data can declare `__slots__ = ()` so it does not add an instance dictionary:

```python
class ReprMixin:
    __slots__ = ()

    def label(self) -> str:
        return type(self).__name__


from dataclasses import dataclass


@dataclass(slots=True)
class BatchRecord(ReprMixin):
    batch_id: int


record = BatchRecord(42)
print(record.label(), record.batch_id, hasattr(record, "__dict__"))
```

Expected output:

```text
BatchRecord 42 False
```

A mixin with no slots of its own can otherwise introduce a dictionary depending on its class definition and hierarchy. Test the complete MRO, not only the leaf class.

### 10.3 Alternatives for large data

Slots are not always the best representation for millions of records:

| Representation | Best fit | Trade-offs |
|---|---|---|
| Ordinary class | Flexible application objects, dynamic fields, monkeypatching | Instance dictionaries add overhead; shape is flexible |
| Slotted class | Stable small objects with known fields | No arbitrary attributes unless opted in; inheritance constraints |
| `dataclass(slots=True)` | Typed record-like domain/DTO objects | Same slot constraints; class transformation/inheritance details |
| `NamedTuple` / `typing.NamedTuple` | Immutable tuple-like records with named fields | Tuple semantics and immutability; not a drop-in mutable object |
| `array` / `struct` / `memoryview` | Compact homogeneous numeric or binary layouts | Lower-level layout and conversion complexity |
| NumPy structured arrays | Large numerical datasets with structured records | Adds dependency and dtype/layout considerations |
| pandas / Arrow / columnar storage | Analytical workloads and column-oriented processing | Different access model; conversion and memory behavior depend on data types |

For data engineering workloads, millions of Python row objects may be the wrong abstraction. Columnar formats and vectorized operations can outperform row-oriented object collections in both memory and throughput. Choose the representation that fits the workload, not just the smallest individual object.

## 11. Trade-offs and engineering decision criteria

Use slots when all of the following are true:

- The class has a stable, known set of attributes.
- There are enough live instances for per-instance overhead to matter.
- A representative measurement shows a useful reduction for the deployed interpreter and data.
- The team can accept the effects on dynamic attributes, inheritance, weak references, serialization, and tooling.

Prefer ordinary classes when you need:

- Dynamic attributes or ad hoc instrumentation.
- Flexible mixins and multiple inheritance.
- Tests that intentionally monkeypatch instance attributes.
- Libraries that expect `__dict__` or use `cached_property`.
- A simple object population where memory is not a measured bottleneck.

Slots may improve attribute access in some cases, but do not expect them to speed up everything. Attribute performance depends on the interpreter and workload; memory reduction is the primary reason to consider them. Benchmark real end-to-end work rather than relying on a microbenchmark alone.

## 12. Common mistakes

All three common mistakes listed in the authoritative Lesson 07 roadmap are covered here:

1. **Expecting `__slots__` to speed up everything.** Slots mainly target memory overhead; any speed change is workload- and version-dependent.
2. **Declaring slots in every level of a hierarchy and duplicating names.** Declare only new names in subclasses. Duplicate inherited names can shadow descriptors and have undefined/unsupported consequences.
3. **Using slots and then trying `obj.new_attr = 1` in tests.** That assignment correctly raises `AttributeError` when no instance dictionary is available. Add a dictionary only if dynamic attributes are part of the design.

Additional mistakes to avoid:

- Treating `sys.getsizeof(obj)` as the complete object graph size.
- Comparing measurements taken with different object counts or payload allocation patterns.
- Claiming a fixed memory saving without recording the Python implementation and version.
- Forgetting that an unslotted base or subclass can reintroduce `__dict__`.
- Assuming `__slots__` automatically provides weak-reference support.
- Declaring a class attribute with the same name as a slot.
- Assuming `cached_property` works without `__dict__`.
- Assuming pickle works for every custom slotted class without testing its state protocol.
- Using a slotted design in a mixin-heavy hierarchy without checking layout compatibility.
- Believing slots enforce privacy or prevent deliberate mutation of declared fields.

## 13. Pytest tests

Save the examples below in `test_slots_and_memory_layout.py` and run `python -m pytest -q`. The tests check semantics, not fixed byte savings; tests must not assert machine-specific `sys.getsizeof` values.

```python
import pickle
import weakref
from dataclasses import dataclass

import pytest


class Plain:
    def __init__(self, value: int) -> None:
        self.value = value


class Slotted:
    __slots__ = ("value",)

    def __init__(self, value: int) -> None:
        self.value = value


def test_plain_instances_have_dict() -> None:
    item = Plain(1)
    assert item.__dict__ == {"value": 1}


def test_pure_slotted_instance_has_no_dict() -> None:
    item = Slotted(1)
    assert not hasattr(item, "__dict__")


def test_dynamic_attribute_is_rejected() -> None:
    item = Slotted(1)
    with pytest.raises(AttributeError):
        item.extra = 2


def test_slots_store_independent_values() -> None:
    first = Slotted(10)
    second = Slotted(20)
    first.value = 99
    assert first.value == 99
    assert second.value == 20


def test_slot_descriptor_is_a_member_descriptor() -> None:
    assert type(Slotted.value).__name__ == "member_descriptor"


def test_unslotted_subclass_reintroduces_dict() -> None:
    class Child(Slotted):
        pass

    child = Child(1)
    child.extra = "allowed"
    assert child.extra == "allowed"
    assert hasattr(child, "__dict__")


def test_empty_slots_keep_subclass_dictionary_free() -> None:
    class Child(Slotted):
        __slots__ = ()

    child = Child(1)
    assert not hasattr(child, "__dict__")
    with pytest.raises(AttributeError):
        child.extra = "not allowed"


def test_weakref_requires_support() -> None:
    class Weakable:
        __slots__ = ("value", "__weakref__")

        def __init__(self, value: int) -> None:
            self.value = value

    item = Weakable(1)
    assert weakref.ref(item)() is item


def test_slotted_object_round_trips_through_pickle() -> None:
    item = Slotted(7)
    restored = pickle.loads(pickle.dumps(item, protocol=pickle.HIGHEST_PROTOCOL))
    assert restored.value == 7


def test_slotted_dataclass() -> None:
    @dataclass(slots=True)
    class Record:
        key: int

    record = Record(3)
    assert record.key == 3
    assert not hasattr(record, "__dict__")


def test_slot_class_attribute_collision_is_rejected() -> None:
    with pytest.raises(ValueError):
        class Invalid:
            __slots__ = ("status",)
            status = "new"
```

Expected test outcome on a compatible Python 3.12+ environment is that all tests pass. Run the suite in the target interpreter; the test intentionally avoids asserting specific memory sizes or ratios because those vary by environment.

## 14. Graduated exercises

### Exercise 1 — predict the result

Explain which assignments work and which raise `AttributeError`:

```python
class Packet:
    __slots__ = ("sequence",)

packet = Packet()
packet.sequence = 10
packet.topic = "events"
```

### Exercise 2 — preserve slots through inheritance

Create `BaseEvent` with a `timestamp` slot and `Event` with a `name` slot. Confirm that `Event` instances have no `__dict__`, and demonstrate that both attributes work.

### Exercise 3 — support weak references

Modify a slotted class so a `weakref.ref(instance)` succeeds. Explain the role of `__weakref__`.

### Exercise 4 — measure a workload

Adapt Section 4's script to one million instances. Record the Python implementation/version, object count, number of fields, measured traced deltas, and observed ratio. Run several times and report a median. Do not reuse a result from another machine.

### Exercise 5 — choose a representation

For each workload, justify ordinary classes, slotted classes, `dataclass(slots=True)`, `NamedTuple`, or columnar storage:

- 100 long-lived service objects that need dynamic debugging fields.
- 2 million immutable event records consumed by a batch analytics job.
- A domain entity with validated properties and several inheritance-based plugins.
- Millions of numeric values used for vectorized aggregation.

## 15. Worked solutions

### Solution 1

`packet.sequence = 10` works because `sequence` is declared as a slot. `packet.topic = "events"` raises `AttributeError` because the class has no instance dictionary and `topic` is not a declared slot.

### Solution 2

```python
class BaseEvent:
    __slots__ = ("timestamp",)

    def __init__(self, timestamp: int) -> None:
        self.timestamp = timestamp


class Event(BaseEvent):
    __slots__ = ("name",)

    def __init__(self, timestamp: int, name: str) -> None:
        super().__init__(timestamp)
        self.name = name


event = Event(1_700_000_000, "ingested")
assert event.timestamp == 1_700_000_000
assert event.name == "ingested"
assert not hasattr(event, "__dict__")
```

The subclass declares only its new field, `name`. Neither class introduces a dictionary.

### Solution 3

```python
import weakref


class WeakEvent:
    __slots__ = ("event_id", "__weakref__")

    def __init__(self, event_id: int) -> None:
        self.event_id = event_id


event = WeakEvent(5)
assert weakref.ref(event)() is event
```

The `__weakref__` slot provides storage needed for weak-reference support when no base class already provides it.

### Solution 4

Set `count = 1_000_000` in the measurement script and run it on a machine with sufficient memory. Record actual output and environment. The correct answer is the measured ratio from those runs, not a universal expected ratio. Include whether strings and integer payloads are shared or allocated inside the measured region.

### Solution 5

- **100 dynamic service objects:** ordinary classes are likely simplest; the population is small and dynamic debugging attributes are useful.
- **2 million immutable event records:** benchmark slotted dataclasses or `NamedTuple`; if processing is primarily analytical, consider a columnar representation instead of millions of Python objects.
- **Validated domain entity with plugin inheritance:** ordinary classes may be preferable if dynamic behavior and multiple inheritance dominate; slots are viable only after auditing the full hierarchy and tooling.
- **Millions of numeric values for vectorized aggregation:** arrays or NumPy/Arrow/pandas columnar storage are often a better fit than individual Python objects.

These are initial design hypotheses, not substitutes for measurement.

## 16. Roadmap self-check — questions and answers

### 1. What two things does a normal instance carry that a slotted instance does not?

In the roadmap's conventional mental model, a normal instance has an instance `__dict__` and weak-reference support (`__weakref__`) that a pure-slotted instance does not have by default. Actual inherited layout matters: a base class may supply either capability.

### 2. Why does a subclass without `__slots__` lose the benefit?

A subclass that omits `__slots__` gets a normal instance dictionary for its own dynamic attributes. It still inherits the base's slot descriptors, but arbitrary attributes can be stored in the new dictionary. Declare `__slots__ = ()` when the subclass adds no storage and should remain dictionary-free.

### 3. Measure 1,000,000 instances with and without slots using `tracemalloc` and report the ratio.

Run the Section 4 script with `count = 1_000_000`, repeat it under controlled conditions, and calculate:

\[
\text{observed ratio} =
\frac{\text{ordinary traced allocation delta}}
{\text{slotted traced allocation delta}}
\]

Record the actual values from your runtime. The ratio is not supplied as a fixed number because the roadmap requires measurement and the result depends on Python version, object shape, allocator/runtime behavior, and measurement methodology.

## 17. Final engineering checklist

- [ ] I can explain the ordinary instance dictionary model and how slots reserve named storage.
- [ ] I know that slots are class-level member descriptors and instance reads return stored values.
- [ ] I understand the `AttributeError` behavior for undeclared attributes.
- [ ] I know how `__dict__` and `__weakref__` can be opted back in.
- [ ] I understand slot behavior through slotted and unslotted inheritance.
- [ ] I avoid duplicate inherited slot names and test multiple-inheritance layout compatibility.
- [ ] I understand why class-level defaults cannot reuse slot names.
- [ ] I know why `cached_property` needs a mutable instance dictionary.
- [ ] I test pickling and serializers against actual object state and target protocols.
- [ ] I know how `dataclass(slots=True)` affects class creation and inherited fields.
- [ ] I can explain why `sys.getsizeof` is shallow and why `tracemalloc` is not process RSS.
- [ ] I have measured representative workloads on the target Python version instead of assuming fixed savings.
- [ ] I considered `NamedTuple`, arrays, `memoryview`, NumPy structured arrays, pandas, or Arrow for large data.
- [ ] I have covered all three roadmap common mistakes and answered all three self-check questions.
