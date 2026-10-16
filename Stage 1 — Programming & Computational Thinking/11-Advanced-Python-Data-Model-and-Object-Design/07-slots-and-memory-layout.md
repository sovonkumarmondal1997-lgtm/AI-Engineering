# Lesson 07 — `__slots__` and Memory Layout

**Stage 1 — Programming & Computational Thinking**  
**Module 11 — Advanced Python Data Model and Object Design**  
**Target version:** Python 3.12+  
**Level:** Beginner → intermediate → advanced

> **Roadmap alignment:** This lesson follows Lesson 07 in `roadmap-Advanced-Python-Data-Model-and-Object-Design.md`. It covers ordinary instance dictionaries and weak-reference support; `__slots__`; memory measurement with `sys.getsizeof` and `tracemalloc`; inheritance and multiple-inheritance layout constraints; opting back into `__dict__` and `__weakref__`; slot defaults; `dataclass(slots=True)`; `cached_property`; pickling; CPython object layout, key-sharing dictionaries and inline values; slot member descriptors; when not to use slots; and compact data alternatives. Supplemental explanations are identified where helpful.

---

## 1. Learning outcomes

By the end of this lesson, you should be able to:

1. Explain how normal Python instances store attributes and why `__slots__` changes that model.
2. Declare slots and predict which assignments are allowed.
3. Measure memory responsibly, distinguishing shallow object size from total traced allocations.
4. Explain slot inheritance behavior and common layout conflicts.
5. Add `__dict__` or `__weakref__` support when a class needs it.
6. Avoid slot defaults that conflict with the slot descriptor.
7. Use `dataclass(slots=True)` and understand that it creates a new class.
8. Recognize compatibility issues with `cached_property`, weak references, and pickling.
9. Explain the broad CPython memory model without assuming implementation details are universal.
10. Decide when slots are appropriate and when arrays or columnar storage are better for data workloads.

---

## 2. The normal instance model

Consider a typical class:

```python
class Job:
    def __init__(self, job_id: str, state: str) -> None:
        self.job_id = job_id
        self.state = state


job = Job("job-42", "queued")
assert job.__dict__ == {"job_id": "job-42", "state": "queued"}
job.priority = 3
assert job.priority == 3
```

For an ordinary user-defined class, instance attributes are usually stored in an instance dictionary, accessible as `obj.__dict__`. That dictionary supports flexible, dynamic attributes: code can add new names after construction.

Depending on the class and implementation, an ordinary instance may also support weak references. Weak references allow another object to refer to an instance without keeping that instance alive solely through the reference.

The flexibility has a cost: attribute names and values need storage, and each instance's dictionary has overhead. The exact overhead depends on Python implementation and version.

---

## 3. What `__slots__` changes

`__slots__` declares a fixed set of instance attributes at class creation:

```python
class SlottedJob:
    __slots__ = ("job_id", "state")

    def __init__(self, job_id: str, state: str) -> None:
        self.job_id = job_id
        self.state = state


job = SlottedJob("job-42", "queued")
assert job.job_id == "job-42"
assert job.state == "queued"

try:
    job.priority = 3
except AttributeError:
    pass
else:
    raise AssertionError("undeclared dynamic attributes should be rejected")
```

For a class that does not inherit an instance dictionary from a base class and does not include `"__dict__"` in its slots:

- the declared attributes have fixed slot storage;
- arbitrary additional instance attributes are not allowed;
- an ordinary instance `__dict__` is not provided;
- a weak-reference slot is not provided unless `"__weakref__"` is included or inherited.

Slots do **not** make Python a statically typed language. They constrain which instance attribute names can be stored; they do not automatically validate the values assigned to those names.

### 3.1 Slots do not validate types

```python
class SlottedCounter:
    __slots__ = ("count",)

    def __init__(self, count) -> None:
        self.count = count


counter = SlottedCounter("not an integer")
assert counter.count == "not an integer"
```

If type or value validation is required, implement it separately, for example with a property or descriptor.

### 3.2 Why memory may improve

A conventional instance typically has an object header and attribute storage machinery. A slotted instance can avoid a separate per-instance dictionary and store declared attributes in fixed positions. This can reduce memory, particularly when many instances each have a small number of attributes.

The benefit is not guaranteed to be large. Modern CPython has optimizations for ordinary instance dictionaries, and object sizes depend on the Python version, class shape, allocator behavior, and measurement method. Measure your workload rather than relying on a fixed percentage.

---

## 4. First comparison: `sys.getsizeof`

The roadmap introduces a simple comparison:

```python
import sys


class PointDict:
    def __init__(self, x, y):
        self.x, self.y = x, y


class PointSlots:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x, self.y = x, y


p = PointDict(1, 2)
q = PointSlots(1, 2)

print("normal instance plus its dict:", sys.getsizeof(p) + sys.getsizeof(p.__dict__))
print("slotted instance:", sys.getsizeof(q))
```

### What does `sys.getsizeof` actually measure?

`sys.getsizeof(obj)` reports the object's **shallow** size as reported by the Python implementation. It does not recursively count every object referenced by that object.

In the first expression, the size of the instance and the size of its dictionary are added explicitly. That still does not include the integer objects referenced by the dictionary, class objects, allocator fragmentation, or every other process-level cost.

Use this comparison as an illustration, not a universal benchmark.

---

## 5. Measure allocations with `tracemalloc`

The roadmap recommends measuring a large population—up to one million instances—with `tracemalloc`. This records Python memory allocations during the traced period. A million objects can require substantial memory, so run the experiment in a controlled environment and start with a smaller number if necessary.

```python
import gc
import tracemalloc


class RowDict:
    def __init__(self, row_id: int, value: int) -> None:
        self.row_id = row_id
        self.value = value


class RowSlots:
    __slots__ = ("row_id", "value")

    def __init__(self, row_id: int, value: int) -> None:
        self.row_id = row_id
        self.value = value


def measure(factory, count: int) -> int:
    gc.collect()
    tracemalloc.start()
    before, _ = tracemalloc.get_traced_memory()
    rows = [factory(i, i * 2) for i in range(count)]
    current, peak = tracemalloc.get_traced_memory()
    delta = current - before
    # Keep rows alive until after the measurement so their allocations count.
    assert len(rows) == count
    tracemalloc.stop()
    del rows
    return delta


if __name__ == "__main__":
    count = 100_000  # Increase to 1_000_000 when resources allow.
    normal_bytes = measure(RowDict, count)
    slots_bytes = measure(RowSlots, count)
    print(f"normal: {normal_bytes:,} bytes")
    print(f"slots:  {slots_bytes:,} bytes")
    print(f"ratio (normal / slots): {normal_bytes / slots_bytes:.2f}x")
```

### How to interpret the result

- The ratio is specific to the current interpreter, class design, and test environment.
- The `value` and `row_id` integers are created by the same pattern in both versions; their allocation behavior can influence the measurement.
- `tracemalloc` traces Python memory allocations, not every native allocation in the process.
- Run several trials and compare the same Python version and workload.
- If the class has many attributes or uses other object structures, results may differ.

**Do not memorize a promised percentage of savings.** The professional habit is to measure representative data and report the environment, sample size, and methodology.

---

## 6. Inheritance and slots

Inheritance is one of the most important sources of surprises.

### 6.1 A subclass without `__slots__` can regain `__dict__`

```python
class BaseRecord:
    __slots__ = ("record_id",)

    def __init__(self, record_id: str) -> None:
        self.record_id = record_id


class FlexibleRecord(BaseRecord):
    pass


record = FlexibleRecord("r-1")
record.extra = "allowed because subclass has a dictionary"
assert record.extra.startswith("allowed")
assert hasattr(record, "__dict__")
```

If a subclass does not declare `__slots__`, it normally gains an instance dictionary even if its base class is slotted. The base class's fixed storage remains, but dynamic attributes are possible again.

To keep the subclass slotted, declare slots for its new fields.

### 6.2 Declare only new names in a subclass

```python
class BasePoint:
    __slots__ = ("x",)

    def __init__(self, x: float) -> None:
        self.x = x


class ColoredPoint(BasePoint):
    __slots__ = ("color",)

    def __init__(self, x: float, color: str) -> None:
        super().__init__(x)
        self.color = color


point = ColoredPoint(2.5, "blue")
assert point.x == 2.5
assert point.color == "blue"
assert not hasattr(point, "__dict__")
```

Do not repeat `"x"` in the subclass slots. Re-declaring a slot name already defined by a base class can hide the base slot and create confusing behavior. Declare only the additional slot names.

### 6.3 Multiple inheritance layout conflicts

Multiple inheritance can fail when more than one base contributes incompatible non-empty slot layouts.

```python
class Left:
    __slots__ = ("left_value",)


class Right:
    __slots__ = ("right_value",)


# Intentionally invalid: CPython cannot combine these independent
# non-empty instance layouts in this simple multiple-inheritance shape.
try:
    class Combined(Left, Right):
        __slots__ = ()
except TypeError:
    pass
else:
    raise AssertionError("expected a slot layout conflict")
```

This example intentionally demonstrates a class-creation error. Do not use this pattern as a design template. When a hierarchy needs multiple inheritance, consider whether only one base should own the physical layout, whether other bases can be slotless mixins, or whether composition is simpler.

---

## 7. Opt back into `__dict__` or weak references

Slots can include special names that restore capabilities.

### 7.1 Allow dynamic attributes with `"__dict__"`

```python
class PartlySlotted:
    __slots__ = ("name", "__dict__")

    def __init__(self, name: str) -> None:
        self.name = name


obj = PartlySlotted("extractor")
obj.runtime_metric = 12
assert obj.name == "extractor"
assert obj.__dict__["runtime_metric"] == 12
```

This retains a declared slot for `name` while allowing arbitrary additional attributes. It also reduces the memory advantage compared with a class that has no instance dictionary.

### 7.2 Allow weak references with `"__weakref__"`

```python
import weakref


class Weakable:
    __slots__ = ("name", "__weakref__")

    def __init__(self, name: str) -> None:
        self.name = name


obj = Weakable("worker")
reference = weakref.ref(obj)
assert reference() is obj
```

A slotted class without weak-reference support cannot normally be the target of a weak reference. Include `"__weakref__"` when that capability is required and is not inherited from a base class.

### 7.3 A weak-reference limitation

Weak references are useful for caches, observers, and registries that should not keep objects alive. But a weak-reference-based design should be tested with the actual class hierarchy and equality/hash behavior. `WeakKeyDictionary` in particular relies on keys being weak-referenceable and hashable.

---

## 8. Slot defaults and initialization

A slot name creates a descriptor in the class namespace. Defining a class attribute with the same name can conflict with the slot declaration.

**Avoid this pattern:**

```text
class BadDefaults:
    __slots__ = ("state",)
    state = "queued"  # conflicts with the slot descriptor
```

Instead, set the default in `__init__`:

```python
class Job:
    __slots__ = ("job_id", "state")

    def __init__(self, job_id: str, state: str = "queued") -> None:
        self.job_id = job_id
        self.state = state


job = Job("job-42")
assert job.state == "queued"
```

This makes the default an instance value stored in the slot, rather than a class attribute that masks the slot descriptor.

For dataclasses, use a field default as shown in the next section.

---

## 9. `dataclass(slots=True)`

Python 3.10+ supports `slots=True` in `dataclasses.dataclass`:

```python
from dataclasses import dataclass, fields


@dataclass(slots=True)
class Batch:
    batch_id: str
    row_count: int = 0


batch = Batch("batch-10", 250)
assert batch.batch_id == "batch-10"
assert batch.row_count == 250
assert not hasattr(batch, "__dict__")
assert [field.name for field in fields(batch)] == ["batch_id", "row_count"]
```

This is often a convenient way to declare compact record-like objects while retaining generated initialization, representation, equality, and other dataclass behavior.

### 9.1 Important: `dataclass(slots=True)` creates a new class

Unlike the ordinary dataclass transformation, `slots=True` returns a newly created class rather than simply modifying the original class object in place. This matters for decorators, class identity, inheritance, and hooks such as `__init_subclass__`. Test interactions with custom metaclasses and class-creation hooks rather than assuming all class-transforming patterns behave identically.

### 9.2 Mutable defaults still need care

Slots do not solve mutable-default bugs. Use a `default_factory` for lists or dictionaries:

```python
from dataclasses import dataclass, field


@dataclass(slots=True)
class TableSchema:
    columns: list[str] = field(default_factory=list)


a = TableSchema()
b = TableSchema()
a.columns.append("order_id")
assert a.columns == ["order_id"]
assert b.columns == []
```

Each instance gets its own list.

---

## 10. `__slots__` and `cached_property`

`functools.cached_property` stores its computed value in the instance dictionary under the property name. Therefore, a class needs a mutable instance `__dict__` for the standard `cached_property` to work.

```python
from functools import cached_property


class Report:
    def __init__(self, amounts: list[int]) -> None:
        self.amounts = list(amounts)
        self.calls = 0

    @cached_property
    def total(self) -> int:
        self.calls += 1
        return sum(self.amounts)


report = Report([4, 6])
assert report.total == 10
assert report.total == 10
assert report.calls == 1
```

This slotted class has no `__dict__`, so standard `cached_property` cannot cache the result:

```python
from functools import cached_property


class SlottedReport:
    __slots__ = ("amounts",)

    def __init__(self, amounts: list[int]) -> None:
        self.amounts = amounts

    @cached_property
    def total(self) -> int:
        return sum(self.amounts)


slotted = SlottedReport([4, 6])
try:
    slotted.total
except TypeError:
    pass
else:
    raise AssertionError("cached_property requires an instance __dict__ here")
```

Possible alternatives:
- include `"__dict__"` in `__slots__` if the flexibility and memory trade-off is acceptable;
- use a normal property that computes each time;
- use an explicit slot for the cached value and an appropriate sentinel;
- use a dedicated external cache if its lifecycle and concurrency behavior are well designed.

If a computed value depends on mutable input, also decide how the cache is invalidated.

---

## 11. Pickling slotted objects

Pickling serializes an object for later reconstruction. Slot-only classes have historically had more constraints than ordinary classes, but modern Python supports many common slotted-class pickling cases. The roadmap notes that pickling works in Python 3.x for protocol 2 and later in common cases; custom `__getstate__`, `__setstate__`, or `__reduce__` behavior can still require care.

Test the actual class and protocol you intend to use:

```python
import pickle


class SlottedEvent:
    __slots__ = ("event_id", "status")

    def __init__(self, event_id: str, status: str) -> None:
        self.event_id = event_id
        self.status = status


def round_trip() -> SlottedEvent:
    event = SlottedEvent("evt-1", "processed")
    restored = pickle.loads(pickle.dumps(event, protocol=pickle.HIGHEST_PROTOCOL))
    assert restored.event_id == "evt-1"
    assert restored.status == "processed"
    return restored


# Run this in a normal .py module so the class is importable by pickle.
restored_event = round_trip()
```

**Operational caution:** pickle is Python-specific and unsafe for untrusted input. Do not unpickle data from untrusted sources. For durable cross-language data interchange, use a documented format such as JSON, Avro, or Protocol Buffers when suitable.

---

## 12. Slots are descriptors

Each declared slot is represented in the class namespace by a member descriptor. That descriptor manages the fixed storage associated with the slot.

```python
class Coordinate:
    __slots__ = ("x", "y")


x_descriptor = vars(Coordinate)["x"]
assert type(x_descriptor).__name__ == "member_descriptor"
```

The precise internal type names are implementation details, but on CPython the slot entries are `member_descriptor` objects. This connects Lesson 07 directly to Lesson 06: slots are not a separate attribute-access system; they use the descriptor protocol to expose fixed storage.

---

## 13. A high-level view of CPython object layout

This section is explanatory rather than a portable binary-layout specification.

A CPython object generally has an object header that supports reference counting and type identification. Garbage-collected objects may also have garbage-collector bookkeeping. The object's instance attributes then need storage.

Broadly:

- A normal class instance has the object header plus instance attribute storage, commonly represented by a dictionary.
- A slotted instance uses fixed slot positions for the declared attributes and can avoid a per-instance dictionary.
- References stored in slots point to Python objects; slots do not automatically pack arbitrary Python integers or strings into C-style inline values.

### 13.1 Key-sharing dictionaries (PEP 412)

CPython can share dictionary *keys* across instances of the same class when their attribute layouts are compatible, while keeping values per instance. This reduces the cost of ordinary instance dictionaries compared with a simplistic model where every instance owns a completely independent copy of every key.

### 13.2 CPython 3.11+ inline values

CPython 3.11 introduced implementation changes that can keep instance values in a more compact inline arrangement for eligible instances, with dictionary materialization behavior depending on access and layout. These optimizations further narrow the memory difference in some workloads. Exact details are version-dependent and should be confirmed against the CPython version being measured.

### 13.3 What this means in practice

Do not make universal claims such as “slots always save X percent” or “slots always make attribute access faster.” Memory and speed depend on the Python version, attribute count, object lifetime, access patterns, subclass layout, and measurement method.

The engineering rule is simple: **measure before adopting slots**.

---

## 14. When slots are a good fit

Consider slots when:
- a class has a small, stable set of attributes;
- the application creates a very large number of instances;
- dynamic attributes are not part of the API;
- you have measured meaningful memory savings in the real workload;
- the class's inheritance, serialization, weak-reference, and testing needs are compatible.

Examples may include compact internal records, parsed tokens, lightweight graph nodes, or transient event objects—provided they are genuinely object-oriented workloads and not better represented in a bulk data structure.

## 15. When not to use slots

Be cautious or avoid slots when:
- consumers need dynamic attributes or monkeypatching;
- tests attach ad hoc state to instances;
- mixins and complex multiple inheritance make storage layout difficult;
- subclasses are expected to add arbitrary fields;
- a library promises broad subclassing compatibility;
- the class relies on standard `cached_property` but has no instance dictionary;
- memory savings are small or unmeasured.

Slots are a design trade-off, not a universal optimization switch.

---

## 16. Alternatives for compact or large-scale data

For data engineering, choosing the right data representation often matters more than optimizing each Python object.

| Tool or representation | Appropriate use | Important trade-off |
|---|---|---|
| `typing.NamedTuple` / `collections.namedtuple` | Small immutable record-like values | Fixed tuple-oriented structure; different mutability and extension behavior |
| `array.array` | Homogeneous primitive numeric values | Restricted type codes and narrower capabilities than a general Python list |
| `struct` | Packing/unpacking fixed binary layouts | Low-level format handling; explicit layout and byte-order choices |
| NumPy structured arrays | Typed records in contiguous numerical memory | Requires NumPy and its data model; not a general replacement for Python objects |
| `memoryview` | Zero-copy views over buffer-protocol objects | Works only with compatible buffer exporters and formats |
| pandas / Apache Arrow | Columnar analytics and tabular data processing | Columnar operations and conversion costs; best for bulk operations, not arbitrary per-row object behavior |

A million Python row objects may be the wrong representation if the actual task is columnar filtering, aggregation, joins, or vectorized numerical work. In those cases, pandas or Arrow can offer a better memory and throughput profile than any per-object slot optimization.

---

## 17. Common mistakes

1. **Expecting slots to speed up everything.** Their clearest benefit is often memory reduction; performance must be measured.
2. **Assuming `sys.getsizeof(instance)` includes all referenced objects.** It is shallow.
3. **Forgetting that a subclass without `__slots__` can regain `__dict__`.**
4. **Repeating a base-class slot name in a subclass.** Declare only new names.
5. **Assuming any multiple-inheritance combination of slotted classes is valid.** Layout conflicts can raise `TypeError`.
6. **Assigning a class-level default with the same name as a slot.** Initialize the value in `__init__` or use dataclass field defaults.
7. **Expecting `cached_property` to work without an instance dictionary.**
8. **Forgetting `"__weakref__"` when a slotted class must support weak references.**
9. **Treating implementation-specific memory measurements as language guarantees.**
10. **Optimizing millions of Python row objects when columnar storage is the better solution.**

---

## 18. Exercises

Try each exercise before reading the solutions.

### Exercise 1 — basic slots

Create a `Task` class with slots for `task_id`, `state`, and `attempts`. Confirm that declared fields work and assigning `task.debug_note` raises `AttributeError`.

### Exercise 2 — inheritance

Create a slotted base class with `id`. Make one subclass without `__slots__` and another with only a new slot called `priority`. Confirm which subclass has an instance dictionary.

### Exercise 3 — memory experiment

Use `tracemalloc` to compare 100,000 instances of a normal class and a slotted class with the same two attributes. Record Python version, sample size, and ratio. Repeat with one million instances if resources permit.

### Exercise 4 — weak references

Create a slotted class that supports weak references. Verify that `weakref.ref(instance)()` returns the same object while the strong reference exists.

### Exercise 5 — cached computation

Explain why `cached_property` fails on a slot-only class with no `__dict__`. Implement a cache using a dedicated slot and a sentinel.

### Exercise 6 — pickling

Round-trip a slotted object through `pickle.dumps` and `pickle.loads`. Verify the relevant field values after reconstruction.

### Exercise 7 — choose a representation

A pipeline processes 15 million records and performs column filters, group-by aggregations, and joins. Compare using one Python object per row with using Arrow or pandas. State which you would test first and why.

### Exercise 8 — explain the memory result

Your experiment shows that slots save much less memory on Python 3.12 than a colleague's older benchmark. Give at least three reasons this may happen without either benchmark necessarily being wrong.

---

## 19. Exercise solutions

### Solution 1

```python
class Task:
    __slots__ = ("task_id", "state", "attempts")

    def __init__(self, task_id: str, state: str, attempts: int = 0) -> None:
        self.task_id = task_id
        self.state = state
        self.attempts = attempts


task = Task("t-7", "ready")
assert task.attempts == 0
try:
    task.debug_note = "temporary"
except AttributeError:
    pass
else:
    raise AssertionError("unexpected dynamic attribute")
```

### Solution 2

```python
class Base:
    __slots__ = ("id",)


class Flexible(Base):
    pass


class Compact(Base):
    __slots__ = ("priority",)


assert hasattr(Flexible(), "__dict__")
assert not hasattr(Compact(), "__dict__")
```

### Solution 3

Use the `tracemalloc` experiment in Section 5. Report the environment and methodology, not only the ratio. Ensure the measured objects remain alive until after reading traced memory.

### Solution 4

```python
import weakref


class CacheEntry:
    __slots__ = ("key", "__weakref__")

    def __init__(self, key: str) -> None:
        self.key = key


entry = CacheEntry("customer:42")
ref = weakref.ref(entry)
assert ref() is entry
```

### Solution 5

The standard `cached_property` writes the result into the instance dictionary. A slot-only class with no dictionary has nowhere for that cached value to be stored under the property name. Use a dedicated cache slot, a property that computes on every access, or include `__dict__` if the trade-off is acceptable.

### Solution 6

Use the `SlottedEvent` example in Section 11 and assert the restored object's `event_id` and `status`.

### Solution 7

Start by testing a columnar representation such as Arrow or pandas because filtering, grouping, and joining are bulk data operations. Benchmark the actual workload, including conversion cost, memory peak, and output requirements. A row-object design may still be appropriate when each record has rich behavior, but that is not the workload described.

### Solution 8

Possible reasons include:
- newer CPython versions improved ordinary instance dictionary storage;
- the number of attributes or shape of the class differs;
- the old benchmark included instance dictionary size differently;
- object values and their allocations affect the measured totals;
- allocator, platform, and interpreter version differ;
- measurement method and object lifetime differ.

---

## 20. Roadmap self-check

1. **What two things does a normal instance carry that a slotted instance does not?**  
   In the basic comparison, the normal instance typically has an instance `__dict__` and weak-reference support, while a slot-only instance without those special slots does not. Strictly, these are capabilities provided by the class layout, not universal guarantees about every class.

2. **Why does a subclass without `__slots__` lose the benefit?**  
   Such a subclass normally gains an instance dictionary, so arbitrary attributes become possible and the object no longer has the same dictionary-free layout.

3. **Measure 1,000,000 instances with and without slots using `tracemalloc` and report the ratio.**  
   Run the experiment in Section 5 with `count = 1_000_000` on your environment. The ratio is intentionally not pre-filled because it is a measurement result, not a portable constant.

---

## 21. Readiness checklist

Before moving to Lesson 08, make sure you can:

- [ ] Explain the difference between ordinary instance dictionaries and slot storage.
- [ ] Declare slots and demonstrate the restriction on arbitrary attributes.
- [ ] Explain why `sys.getsizeof` is shallow.
- [ ] Run a repeatable `tracemalloc` comparison and report the ratio honestly.
- [ ] Explain what happens when a subclass omits `__slots__`.
- [ ] Avoid duplicate slot names in subclasses.
- [ ] Recognize multiple-inheritance layout conflicts.
- [ ] Add `__dict__` or `__weakref__` only when the capability is needed.
- [ ] Set slot defaults correctly.
- [ ] Explain `dataclass(slots=True)` and its class-creation behavior.
- [ ] Explain why `cached_property` needs an instance dictionary.
- [ ] Test pickling for the actual slotted class.
- [ ] Explain that slots are implemented through member descriptors.
- [ ] Choose between slots and columnar representations based on workload measurements.

---

## 22. Key takeaways

1. `__slots__` declares fixed instance attribute storage and can eliminate the per-instance dictionary.
2. Slots can save memory, but the amount depends on Python version, class design, and measurement method.
3. A subclass without `__slots__` normally regains a dictionary; inheritance and multiple inheritance need deliberate design.
4. `"__dict__"` and `"__weakref__"` can be included when dynamic attributes or weak references are required.
5. Avoid slot-name class defaults; initialize instance values in `__init__` or use dataclass field defaults.
6. Standard `cached_property` needs a mutable instance dictionary; verify pickling and weak-reference behavior for real classes.
7. For millions of records, compare per-object optimizations against array and columnar data structures before committing to a representation.

**Next lesson:** `08-mro-super-and-cooperative-inheritance.md`.
