# Practice Questions — Advanced Python Data Model and Object Design

**Curriculum position:** Stage 1 — Programming & Computational Thinking → Module 11 — Advanced Python Data Model and Object Design  
**Python baseline:** Python 3.12+; version-specific behavior is marked  
**Purpose:** Demonstrate that you can explain, implement, debug, test, and apply the module's object-model concepts—not merely recognize terminology.

## How to use this bank

Work through the lessons in roadmap order. Attempt the **Question Bank** without consulting the answer key; write code in a small `uv` project and run tests. For output-prediction tasks, predict first, then execute. For design tasks, state assumptions and trade-offs. Use Python 3.12+ unless a question explicitly says Python 3.13+.

The roadmap groups the module into four phases: **A — Making Objects Behave** (Lessons 1–3), **B — Operators and Attributes** (Lessons 4–6), **C — Memory and Inheritance Mechanics** (Lessons 7–9), and **D — Contracts and Lifecycle** (Lessons 10–11). The module sits in Stage 1 after foundational classes, inheritance, iterators, mutability, dataclasses/Protocols, and pytest. Its goal is to make custom objects behave predictably with Python syntax and standard-library tools.

## Assessment levels

1. **L1 — Fundamentals:** terminology and basic behavior.
2. **L2 — Conceptual understanding:** explain mechanisms and trade-offs.
3. **L3 — Code tracing:** predict outputs, dispatch, identity, exceptions, or lookup order.
4. **L4 — Implementation:** write a correct class/protocol implementation.
5. **L5 — Debugging/code review:** find defects and repair them.
6. **L6 — Testing/edge cases:** design regression tests and boundary checks.
7. **L7 — Advanced engineering:** justify design, compatibility, and performance choices.
8. **L8 — Practical integration:** combine multiple module concepts in realistic scenarios.

**Suggested scoring:** L1–L3: 1 point each; L4–L6: 2 points each; L7–L8: 3 points each. A question may award partial credit for a sound explanation even if code needs correction. Reference solutions are examples, not the only acceptable designs.

---

# Part I — Question Bank (attempt before reading Part II)

## Lesson 01 — Dunder methods, representation, equality, and hashing

### L1 — Fundamentals
**Q01.** Distinguish `repr(x)` from `str(x)`. Which should prioritize developer diagnostics, and what should a useful `repr` ideally communicate?

**Q02.** State the required equality/hash contract. What happens to an object used as a dictionary key if fields contributing to its hash change while it is stored?

### L2 — Conceptual understanding
**Q03.** Explain why a custom `__eq__` that returns `True` for values of another unrelated type should usually be avoided. When should `__eq__` return `NotImplemented` instead of `False`?

**Q04.** Explain the interactions among `__bool__`, `__len__`, and truth testing. What does Python do if a class defines neither?

### L3 — Code tracing
**Q05.** Predict the output and explain each result.
```python
class Key:
    def __init__(self, value): self.value = value
    def __eq__(self, other):
        if not isinstance(other, Key): return NotImplemented
        return self.value == other.value
    def __hash__(self): return hash(self.value)

a, b = Key("x"), Key("x")
print(a == b, a is b, len({a, b}))
```

**Q06.** What is the value of `float('nan') == float('nan')`, and why should code not assume NaN obeys ordinary reflexive equality? What testing issue can this cause?

### L4 — Implementation
**Q07.** Implement a frozen `dataclass` named `Coordinate` with integer `x` and `y` fields, value equality, and safe hash behavior. Add tests showing equivalent coordinates work as dictionary keys.

**Q08.** Implement `__format__` for a `Money`-like value object so `format(value, "c")` displays the currency code and `format(value, ".2f")` displays the amount to two decimals. Define how unsupported format specifications are handled. Explain why the public representation should not allow recursive `__repr__` calls.

### L5 — Debugging and code review
**Q09.** Review this class. Identify at least two contract defects and repair it.
```python
class UserKey:
    def __init__(self, email): self.email = email
    def __eq__(self, other): return self.email.lower() == other.email.lower()
    def __hash__(self): return hash(self.email)
```

### L6 — Testing and edge cases
**Q10.** Write test cases for a value object that cover equality reflexivity/symmetry/transitivity, equality with an unsupported type, equal objects having equal hashes, and hash stability. Explain why a test should not assert a specific numeric hash value across processes.

### L7 — Advanced engineering
**Q11.** Compare a hand-written equality/hash implementation with `@dataclass(frozen=True)` and `@dataclass(unsafe_hash=True)`. When can `unsafe_hash=True` be dangerous?

### L8 — Integration
**Q12.** Design a hashable `DatasetKey` for a cache. Its logical identity is `(source, schema_version)`; a mutable display label must not affect equality/hash. State the invariants and tests.

## Lesson 02 — Rich comparison and total ordering

### L1 — Fundamentals
**Q13.** Name the six rich-comparison methods and identify the method normally required by `sorted()` for a sequence of mutually comparable objects.

**Q14.** Explain the difference between a total order and a partial order. Give one example where two values may be incomparable or where `<` is not a useful total ordering.

### L2 — Conceptual understanding
**Q15.** What does `functools.total_ordering` generate, and why does it still need equality plus one ordering operation? Give one reason to implement all required methods directly instead.

**Q16.** Explain why `key=` is often preferable to changing a class's global comparison semantics for one report. When is `cmp_to_key` justified?

### L3 — Code tracing
**Q17.** Predict the output.
```python
from dataclasses import dataclass
@dataclass(order=True)
class Version:
    major: int
    minor: int
print(Version(1, 9) < Version(1, 10))
print(sorted([Version(2, 0), Version(1, 11)]))
```

**Q18.** Explain what this code assumes and why it may be invalid for some domains.
```python
values = [3.0, float("nan"), 1.0]
print(sorted(values))
```

### L4 — Implementation
**Q19.** Implement a `Job` ordering by `(priority, created_at)` without ordering by every field. Unsupported comparisons should return `NotImplemented`. Include a deterministic sorting example using `key=`.

### L5 — Debugging and code review
**Q20.** A class implements `__lt__` by comparing `self.score < other.score` but does not validate operand types; its comparison is non-transitive because a custom tolerance is applied. Explain the risks for `sorted`, `bisect`, and `heapq`, and suggest a repair.

### L6 — Testing and edge cases
**Q21.** Specify tests for comparison laws: irreflexivity of strict less-than, antisymmetry/consistency where applicable, transitivity, equality consistency, and unsupported operands. Explain why tests must reflect the domain's intended ordering rather than impose a total order on a partial-order domain.

### L7 — Advanced engineering
**Q22.** Describe how `bisect` and `heapq` use ordering and why changing an object's ordering fields after inserting it into a heap can break the heap invariant. Contrast `cmp_to_key` with a native `key=` function.

### L8 — Integration
**Q23.** A scheduler needs stable sorting by priority, then submission sequence, while its `Job` equality remains based on job ID. Propose an implementation and tests that keep ordering and equality contracts intentionally distinct.

## Lesson 03 — Container protocols

### L1 — Fundamentals
**Q24.** Map `len(x)`, `x[i]`, `for v in x`, `v in x`, `del x[i]`, and `reversed(x)` to the relevant special methods. Explain the legacy sequence-iteration fallback.

**Q25.** Explain the difference between `__index__` and `__int__`. Why should `__index__` represent an exact integer value?

### L2 — Conceptual understanding
**Q26.** What minimum primitives should a custom `Sequence` provide? What behaviors can be inherited from `collections.abc.Sequence`? Explain why `__length_hint__` is only a hint.

### L3 — Code tracing
**Q27.** Predict output and explain why the second expression succeeds or fails.
```python
class Items:
    def __getitem__(self, index):
        if index >= 3: raise IndexError
        return index * 10
x = Items()
print(list(x))
print(20 in x)
```

**Q28.** What does `items[1:4]` pass to `__getitem__`? Describe how a class should decide whether to support slices and tuple-based multidimensional indices such as `matrix[1, 2]`.

### L4 — Implementation
**Q29.** Implement a small `Sequence`-like `Window` backed by a tuple. Support `len`, integer indexing, slicing, and iteration; reject invalid indices clearly. Include tests for negative indices and empty slices.

**Q30.** Implement a `dict` subclass that uses `__missing__` to create a default value only when a key is accessed through `obj[key]`. Test the difference between `obj[key]` and `obj.get(key)` for a missing key.

### L5 — Debugging and code review
**Q31.** Find the bug: `__contains__` returns `self._items.index(value)`. Repair it so membership returns a Boolean and behaves correctly for missing values. Explain why returning an index is a protocol violation even when the index is truthy.

### L6 — Testing and edge cases
**Q32.** Design tests for a mutable sequence's `__setitem__` and `__delitem__`, including negative indices, out-of-range indices, slices, mutation during iteration, and empty collections. State which mutation-during-iteration behavior your API promises.

### L7 — Advanced engineering
**Q33.** Explain the pitfalls of subclassing built-in containers: inherited C-level methods may not call overridden Python methods consistently. How could composition plus `collections.abc.MutableMapping` reduce risk?

### L8 — Integration
**Q34.** Design a read-only configuration collection that supports `Mapping`, membership, iteration, length, and clear errors for missing keys. Identify the three core `Mapping` methods and tests for inherited mix-ins.

## Lesson 04 — Operator overloading and numeric protocols

### L1 — Fundamentals
**Q35.** Map `+`, reflected `+`, `+=`, unary `-`, `abs(x)`, bitwise inversion, and matrix multiplication to their special methods. Explain why `@` does not automatically mean a particular mathematical operation.

**Q36.** What does returning `NotImplemented` from an arithmetic method mean? How is it different from raising `NotImplementedError`?

### L2 — Conceptual understanding
**Q37.** Explain normal/reflected operator dispatch and why a reflected method on a suitable right-hand subclass can receive priority. When should `__iadd__` mutate in place versus return a new object?

**Q38.** Explain why `Decimal("0.1") + Decimal("0.2")` is preferable to constructing `Decimal` from binary floats for decimal accounting, and how `Fraction` differs from floating-point arithmetic.

### L3 — Code tracing
**Q39.** Predict output and object identity.
```python
class Bag:
    def __init__(self, items): self.items = list(items)
    def __iadd__(self, item):
        self.items.append(item)
        return self
b = Bag([1]); alias = b; b += 2
print(b.items, alias is b)
```

**Q40.** What happens if both `left.__add__(right)` and the applicable reflected operation return `NotImplemented`? What if `__add__` returns `None` instead?

### L4 — Implementation
**Q41.** Implement an immutable two-dimensional `Vector` supporting `+`, unary `-`, scalar multiplication from either side, and clear rejection of unsupported types. Include tests for non-mutation and reflected multiplication.

### L5 — Debugging and code review
**Q42.** Review a `Money.__add__` implementation that silently adds different currencies and mutates `self`. Identify the semantic defects and propose a safe contract, including the treatment of unsupported types.

### L6 — Testing and edge cases
**Q43.** Design tests for numeric interoperability across `int`, `float`, `Decimal`, and `Fraction`. Which mixed operations should be supported or rejected explicitly? Explain why coercing every input to `float` is not a universal solution.

### L7 — Advanced engineering
**Q44.** Discuss bitwise methods (`__and__`, `__or__`, `__xor__`, shifts), conversion methods (`__int__`, `__float__`, `__index__`), NumPy interoperability (`__array_priority__`, `__array_ufunc__` awareness), and performance costs of allocating many intermediate objects. Do not assume NumPy is installed.

### L8 — Integration
**Q45.** Design a small matrix type whose `@` operator performs matrix multiplication. Specify dimension validation, unsupported operand behavior, numerical tolerances, and tests. Explain why the implementation should document the meaning of `@`.

## Lesson 05 — Properties and computed attributes

### L1 — Fundamentals
**Q46.** Implement a property with a validating setter and a read-only derived property. Why should initialization usually assign through the public property if the setter owns validation?

**Q47.** When is a method a better API than a property? Discuss side effects, cost, and the expectation that property access feels attribute-like.

### L2 — Conceptual understanding
**Q48.** What does `functools.cached_property` cache, where does it normally store the cached value, and how is it invalidated? What constraint matters for classes using `__slots__`?

### L3 — Code tracing
**Q49.** Predict behavior.
```python
class Sample:
    @property
    def value(self): return 10
s = Sample()
s.__dict__["value"] = 99
print(s.value)
```
Explain the descriptor rule that determines the result.

### L4 — Implementation
**Q50.** Implement a `Temperature` class with Celsius validation (`>= -273.15`), a Fahrenheit computed property, and a setter for Fahrenheit that updates Celsius. Add boundary and conversion tests.

### L5 — Debugging and code review
**Q51.** Find the defect in a `cached_property` whose underlying source data can change. Propose a cache invalidation API and explain concurrency implications if multiple threads compute it at once.

### L6 — Testing and edge cases
**Q52.** Give tests for property validation, deletion behavior, inherited property overrides, invalid values, and cache invalidation. How should type hints communicate a property and setter's type?

### L7 — Advanced engineering
**Q53.** Compare `property`, `cached_property`, and a normal method for a computed field in a slotted class. Discuss Python-version differences in `cached_property` concurrency behavior and avoid assuming a property cache is automatically thread-safe.

### L8 — Integration
**Q54.** Design a validated data-transfer object with a normalized `email` property and an expensive `normalized_rows` cache. Define when the cache is cleared and what tests prove that it cannot go stale.

## Lesson 06 — Descriptors and attribute lookup

### L1 — Fundamentals
**Q55.** Distinguish data from non-data descriptors. Give examples of each and explain how ordinary instance attributes interact with them.

**Q56.** What does `__set_name__(owner, name)` enable? Why is a descriptor usually stored as a class attribute rather than created separately in every instance?

### L2 — Conceptual understanding
**Q57.** Describe the practical lookup precedence for an ordinary instance attribute access, including data descriptors, instance `__dict__`, non-data descriptors/class attributes, and `__getattr__` fallback. Explain why `__getattribute__` must be written carefully.

### L3 — Code tracing
**Q58.** Predict the output.
```python
class NonData:
    def __get__(self, obj, owner=None): return "descriptor"
class Example:
    value = NonData()
e = Example(); e.__dict__["value"] = "instance"
print(e.value, Example.value)
```

**Q59.** Why can `inspect.getattr_static(obj, name)` reveal a descriptor object without invoking its normal descriptor behavior? Give a use case.

### L4 — Implementation
**Q60.** Implement a reusable `PositiveNumber` data descriptor that uses `__set_name__`, stores values in a private instance attribute, rejects non-numbers and non-positive values, and works independently across two instances. Add tests.

### L5 — Debugging and code review
**Q61.** A descriptor stores the last assigned value in `self.value`, which is a single descriptor instance shared by every owner instance. Explain the cross-instance bug and repair it using per-instance storage. Discuss name collisions and slots.

### L6 — Testing and edge cases
**Q62.** Test descriptor class access, instance access, invalid assignment, deletion policy, inherited descriptors, and recursive access. How would you annotate the descriptor for a typed codebase?

### L7 — Advanced engineering
**Q63.** Explain how functions become bound methods, how `classmethod`/`staticmethod` differ, and how slot member descriptors affect attribute lookup. Discuss when descriptor caching helps and when it adds complexity.

### L8 — Integration
**Q64.** Design a declarative schema with `RequiredString` and `PositiveNumber` descriptors. Specify validation timing, per-instance state, error messages, inheritance behavior, and a minimal test matrix.

## Lesson 07 — Slots and memory layout

### L1 — Fundamentals
**Q65.** What does `__slots__` change? How does it affect arbitrary attributes, per-instance `__dict__`, memory use, and weak-reference support?

**Q66.** Explain why `sys.getsizeof(obj)` alone is not a fair measurement of total memory used by an instance with a dictionary and nested objects.

### L2 — Conceptual understanding
**Q67.** Explain `__slots__` interactions with inheritance. What happens when a subclass does not define slots, or when multiple bases define incompatible non-empty slots?

### L3 — Code tracing
**Q68.** What happens when the code below runs? Why?
```python
class Point:
    __slots__ = ("x", "y")
p = Point(); p.x = 1
p.label = "origin"
```

### L4 — Implementation
**Q69.** Implement a slotted immutable-ish `Point` with `x`, `y`, and weak-reference support on Python 3.12+. State whether it is actually immutable and how you would enforce immutability if required.

### L5 — Debugging and code review
**Q70.** A team reports that adding `__slots__` reduced `sys.getsizeof(instance)` but did not reduce total process memory. Design a controlled measurement with `tracemalloc`, equivalent workloads, warm-up, and enough instances. Explain why exact byte totals vary by Python build.

### L6 — Testing and edge cases
**Q71.** Plan tests for dynamic attributes, subclass behavior, weak references, pickling, descriptors, and slot-name collisions. Explain what must be tested when a subclass adds `__dict__` or `__weakref__`.

### L7 — Advanced engineering
**Q72.** Give a decision framework for choosing slots versus ordinary instances. Consider instance count, public API flexibility, inheritance, debugging, pickling, weakrefs, and whether profiling demonstrates a real bottleneck.

### L8 — Integration
**Q73.** Optimize a class representing millions of immutable event records. Compare slotted classes with frozen slotted dataclasses and discuss object count, field types, memory measurement, compatibility, and tests.

## Lesson 08 — MRO, `super()`, and cooperative inheritance

### L1 — Fundamentals
**Q74.** What is a method resolution order? How can `Class.__mro__` or `Class.mro()` help debug a method call?

**Q75.** Explain zero-argument `super()`. Why does `super()` mean “next in the MRO” rather than simply “call my parent”?

### L2 — Conceptual understanding
**Q76.** Describe the three core ideas of C3 linearization: child before parents, preserve local precedence order, and monotonicity. Why can Python reject a hierarchy?

### L3 — Code tracing
**Q77.** Predict the method call order.
```python
class A:
    def run(self): print("A")
class B(A):
    def run(self): print("B"); super().run()
class C(A):
    def run(self): print("C"); super().run()
class D(B, C):
    def run(self): print("D"); super().run()
D().run()
print([c.__name__ for c in D.__mro__])
```

### L4 — Implementation
**Q78.** Implement a cooperative constructor chain for `Record`, `TimestampMixin`, and `ValidatedMixin` using keyword-only parameters and `**kwargs`. Ensure each initializer runs once and unexpected keywords fail clearly.

### L5 — Debugging and code review
**Q79.** Diagnose a diamond hierarchy where each parent explicitly calls `Base.__init__(self)`. Explain duplicate initialization and rewrite the pattern cooperatively with `super()`.

### L6 — Testing and edge cases
**Q80.** Write tests proving each cooperative method runs exactly once, the MRO is as expected, constructor parameters reach the intended class, and unknown keywords are rejected.

### L7 — Advanced engineering
**Q81.** Explain signature compatibility requirements in cooperative inheritance. How can positional-only or keyword-only parameters help, and what are the risks of swallowing unknown values in `**kwargs`?

### L8 — Integration
**Q82.** Design a three-mixin processing pipeline where each mixin transforms a record and calls `super()`. Define order, idempotency expectations, failure propagation, and tests that verify MRO-driven execution.

## Lesson 09 — Mixins and multiple-inheritance pitfalls

### L1 — Fundamentals
**Q83.** Define a mixin and explain why it should normally provide one focused behavior rather than represent a complete standalone domain entity.

**Q84.** Why are mixins conventionally placed before a concrete base class? How do method and attribute collisions occur?

### L2 — Conceptual understanding
**Q85.** Compare composition and inheritance for adding logging, serialization, or timestamps. Identify situations where composition is safer.

### L3 — Code tracing
**Q86.** Trace which `to_dict` implementation runs in `class Service(JsonMixin, AuditMixin, BaseService)`, assuming each implementation returns its class name and calls `super().to_dict()` when available. Explain how changing the base order changes behavior.

### L4 — Implementation
**Q87.** Implement a `JsonMixin` and `ReprMixin` that cooperate with a host class. Define a safe policy for objects containing secrets or resources so the mixins do not blindly serialize every attribute.

### L5 — Debugging and code review
**Q88.** Find the design issues in a mixin that requires a positional constructor argument, stores mutable global state, overrides `save()` without calling `super()`, and assumes a particular base class. Propose a repair.

### L6 — Testing and edge cases
**Q89.** Design tests for two mixins with colliding method names, initialization order, state ownership, diamond inheritance, and the complete composed class. Why are isolated unit tests for each mixin insufficient?

### L7 — Advanced engineering
**Q90.** Give criteria for choosing a mixin, ABC, Protocol, or composition. Include behavior reuse, state, method resolution, required host attributes, and API stability.

### L8 — Integration
**Q91.** Build an auditable ETL processor from `MetricsMixin`, `LoggingMixin`, and `BaseProcessor`. Specify a cooperative call chain, redaction policy, error behavior, and tests for all combined orderings you intend to support.

## Lesson 10 — Abstract base classes and collections ABCs

### L1 — Fundamentals
**Q92.** What do `ABC` and `@abstractmethod` provide? At what point does Python prevent an incomplete abstract class from being instantiated?

**Q93.** What three methods make a minimal `Mapping` implementation complete, and which useful methods does `collections.abc.Mapping` provide?

### L2 — Conceptual understanding
**Q94.** Compare nominal ABC inheritance, virtual subclass registration with `.register()`, structural `Protocol`, and plain duck typing. What does virtual registration not do?

### L3 — Code tracing
**Q95.** Predict the results and explain why.
```python
from abc import ABC
class PluginABC(ABC): pass
class ThirdParty: pass
PluginABC.register(ThirdParty)
print(issubclass(ThirdParty, PluginABC))
print(isinstance(ThirdParty(), PluginABC))
print(PluginABC in ThirdParty.__mro__)
```

### L4 — Implementation
**Q96.** Implement a read-only `Mapping` over a private dictionary using only `__getitem__`, `__iter__`, and `__len__`. Demonstrate inherited `get`, `keys`, `items`, `values`, membership, and equality behavior.

### L5 — Debugging and code review
**Q97.** Diagnose an ABC whose abstract method is decorated in the wrong order with `@classmethod`. Correct the decorators. Explain the difference between defining an abstract method and checking abstractness at instantiation.

### L6 — Testing and edge cases
**Q98.** Design tests for an abstract base class, a concrete implementation, virtual registration, a runtime-checkable protocol, and a minimal custom `Mapping`. Include tests for what registration does not change.

### L7 — Advanced engineering
**Q99.** Explain why `@runtime_checkable Protocol` checks only a limited runtime structural shape and does not validate method signatures/types like a static checker. When should a public API use an ABC versus a Protocol?

### L8 — Integration
**Q100.** Design a pluggable data-source interface for CSV, API, and in-memory sources. State which operations are abstract, whether third-party structural implementations are accepted, how plugins are tested, and how you avoid overengineering the interface.

## Lesson 11 — Copying, pickling, and object lifecycle hooks

### L1 — Fundamentals
**Q101.** Distinguish assignment aliasing, shallow copy, deep copy, and serialization. Explain how mutable nested children behave in a shallow copy.

**Q102.** Contrast `__new__` and `__init__`. When is overriding `__new__` appropriate, especially for immutable subclasses or singleton/factory patterns?

### L2 — Conceptual understanding
**Q103.** Why must a custom `__deepcopy__(self, memo)` consult and populate `memo`? Explain cycles and preservation of shared aliases.

**Q104.** Why should `__getstate__` exclude a `threading.Lock`, open file, or live database connection from pickle state? What must `__setstate__` do?

### L3 — Code tracing
**Q105.** Predict output and explain identities.
```python
import copy
child = []
source = {"left": child, "right": child}
shallow = copy.copy(source)
deep = copy.deepcopy(source)
print(shallow is source, shallow["left"] is child)
print(deep["left"] is deep["right"], deep["left"] is child)
```

### L4 — Implementation
**Q106.** Implement a slotted node with a self-cycle and two references to the same child. Write `__deepcopy__` correctly so a deep copy preserves the cycle and shared-reference topology. Test identity relationships.

**Q107.** Implement a picklable cache object with a `threading.Lock` that is excluded from state and recreated during restoration. Include a round-trip test. State clearly that `pickle.loads` is only used for data produced by this trusted test.

### L5 — Debugging and code review
**Q108.** Review a class that closes a socket in `__del__`, pickles an open file, and calls `pickle.loads` on a network payload. Identify all substantive problems and rewrite the design using explicit resource ownership and a safe data interchange format.

### L6 — Testing and edge cases
**Q109.** Design tests for shallow/deep copies, shared aliases, cycles, slotted/frozen dataclass behavior, pickle round trips, missing/old state versions, and finalizer behavior. Which lifecycle tests should avoid asserting exact collection or shutdown timing?

### L7 — Advanced engineering
**Q110.** Explain `__reduce__`/`__reduce_ex__`, `copyreg`, pickle protocols, pickle compatibility/versioning, and why pickle is not a durable interchange format. State the security rule for untrusted pickle input and safer alternatives.

**Q111.** Explain `weakref.ref` versus `weakref.finalize`, why finalizer callbacks must not keep the target alive, and why `weakref.finalize` is not a substitute for deterministic cleanup. Discuss resurrection and interpreter shutdown.

### L8 — Integration
**Q112.** A job configuration contains nested mutable options, a shared sub-object, a lock, a live connection, and a schema version. Specify separate copy and serialization policies, state migration behavior, lifecycle/resource ownership, and a comprehensive test plan.


### Roadmap-specific checkpoints and multiple-choice questions

These short checkpoints preserve the roadmap's exact self-check emphasis and add a small multiple-choice component. They are in addition to Q01–Q112.

**Q113 (Lesson 01, L3).** Why can `{Money(1, "USD")}` raise `TypeError` if `Money` defines `__eq__` but no `__hash__`? Then explain why `Money(1, "USD") == 5` should normally return `NotImplemented` from `__eq__` rather than claim equality or raise `AttributeError`. Write a safe `__repr__` for a module-level `Money` class that can be evaluated in a trusted namespace to reconstruct an equivalent value.

**Q114 (Lesson 03, L3).** For `obj[1:3, 0]`, what exact kind of object is passed to `obj.__getitem__`? Why might `collections.UserDict` be safer than subclassing `dict` when enforcing validation in all mutation paths?

**Q115 (Lesson 04, L4).** Explain why `sum([Vector(1, 1), Vector(2, 2)])` can fail for a custom vector. Implement an appropriate `__radd__` policy that supports the initial integer zero without pretending arbitrary integers are vectors. Also state what `v += w` does if `__iadd__` is absent.

**Q116 (Lesson 06, L3).** State the four-step ordinary instance attribute lookup order taught in this module. Explain why `Order.quantity` should normally return descriptor metadata/the descriptor itself when `__get__` receives `obj is None`, rather than reading instance state.

**Q117 (Lesson 07, L7).** The roadmap asks you to measure one million ordinary and slotted instances. Design a reproducible `tracemalloc` experiment and explain two differences a normal instance usually has compared with a slots-only instance. Do not invent a universal memory ratio.

**Q118 (Lesson 08, L3).** In the diamond `D(B, C)`, predict the effect on initialization order if `B.__init__` forgets to call `super()`. The roadmap self-check claims `class X(A, B)` fails when `class A(B)`. Verify that claim, then give the base ordering that really creates a C3 conflict. What does `super()` inside `B` resolve to when invoked on a `D` instance?

**Q119 (Lesson 09, L4).** Implement a minimal `TimestampMixin` that cooperatively adds a timestamp to a host class, show the MRO, and name two cases where composition is preferable to a mixin.

**Q120 (Lesson 11, L4).** Implement a `weakref.finalize`-based fallback cleanup example without capturing the target object in the callback arguments. Explain why a context manager remains the preferred deterministic cleanup path.

**Q121 (Lesson 11, L2).** What is the role of `__init_subclass__` in class creation, and how does it differ from instance initialization? Give a short plugin-registration example or a precise pseudocode sketch.

**Q122 (Lesson 11, L2).** Explain the awareness-level purposes of `__class_getitem__`, `__instancecheck__`, and `__subclasscheck__`. State why a user-defined `isinstance`/`issubclass` policy should be documented and tested carefully.

**Q123 (Lesson 11, L2).** Compare `dataclasses.replace()` on Python 3.12 with `copy.replace()` and the `__replace__` protocol on Python 3.13+. What does “copy with changes” mean, and why is it not the same as deep-copying an object graph?

**Q124 (Lesson 11, L2).** Explain why small-integer caching, string interning, and `id()` must not be used as business identity or persistent identifiers. Distinguish object identity (`is`) from value equality (`==`).

**Q125 (Multiple choice, Lessons 1–11).** Choose the single best answer for each item.

1. If `a == b` is true, which statement must hold?
   - A. `a is b`
   - B. `hash(a) == hash(b)` whenever both are hashable
   - C. `hash(a) != hash(b)`
   - D. `repr(a) == repr(b)`
2. Which method is normally used by `sorted(values)` when no `key=` is supplied?
   - A. `__contains__`  B. `__lt__`  C. `__hash__`  D. `__index__`
3. A descriptor defines only `__get__`. Which is generally true?
   - A. It is always a data descriptor
   - B. An instance attribute can shadow it
   - C. It cannot be stored on a class
   - D. It must define `__set_name__`
4. What is the main memory-measurement limitation of `sys.getsizeof(obj)`?
   - A. It only works on integers
   - B. It includes all recursively referenced objects
   - C. It reports shallow size, not the complete object graph
   - D. It changes object identity
5. What does virtual ABC registration do?
   - A. Injects all ABC methods into the registered class
   - B. Changes the registered class's MRO
   - C. Affects `isinstance`/`issubclass` checks without method injection or MRO change
   - D. Makes every method abstract
6. Which is the safe rule for `pickle.loads`?
   - A. Safe if the payload says it was generated by Python
   - B. Safe if protocol 5 is used
   - C. Never deserialize untrusted data
   - D. Safe if the payload is compressed
7. Why does `__deepcopy__` memoize a clone before recursively copying children?
   - A. To force a shallow copy
   - B. To preserve cycles and shared references
   - C. To make the clone hashable
   - D. To invoke `__init__` twice




**Q126 (Lesson 11, L4).** Implement `__copy__` for a class that owns a mutable list and an immutable identifier. Specify which state is shared/copied, and test that the new outer object is distinct, the chosen list policy is honored, and the identifier is preserved. Explain why a custom `__copy__` should not accidentally claim deep-copy semantics.

---

# Part II — Cumulative assessment

These tasks intentionally combine multiple lessons. Work independently, document assumptions, and submit code plus tests.

## C1. Reliable value object (Lessons 1, 2, 4)

Implement `Money(amount: Decimal, currency: str)` with immutable state, value equality, safe hashing, formatting, addition of matching currencies, unsupported-operand handling, and ordering by amount only when currencies match. **Acceptance criteria:** no mutation during arithmetic; equal values hash equally; adding mismatched currencies raises a documented domain error; unsupported unrelated types follow a consistent `NotImplemented` policy; tests cover zero, negative amounts if allowed, NaN/infinity policy, and rounding/quantization policy. Explain whether cross-currency ordering is meaningful.

## C2. Native-feeling read-only collection (Lessons 3, 10)

Implement a `Mapping[str, int]` backed by private data. **Acceptance criteria:** `__getitem__`, `__iter__`, and `__len__` are correct; iteration yields keys; membership and inherited mapping helpers work; the caller cannot mutate internal state through a returned view; missing keys raise `KeyError`; tests cover empty mappings, insertion order expectations, and equality.

## C3. Validated descriptor schema (Lessons 5, 6)

Implement a class with `PositiveInt` and `NonEmptyString` descriptors. **Acceptance criteria:** validation occurs on assignment; descriptor metadata is set with `__set_name__`; values are stored per instance; two objects do not share state; invalid assignments raise clear errors; class-level access is defined; inheritance does not accidentally reuse a storage name; tests include slots or document why the host class needs a dictionary.

## C4. Memory measurement (Lesson 7)

Compare ordinary and slotted instances for at least 100,000 equivalent objects. Use `tracemalloc` snapshots and report Python version, workload, warm-up, and measurement method. **Acceptance criteria:** same fields and workload; include referenced dictionary size when using `sys.getsizeof`; distinguish shallow from total allocated memory; no hard-coded expected byte total; discuss weakref/dynamic attribute/pickling compatibility.

## C5. Cooperative pipeline (Lessons 8, 9, 10)

Implement a `BaseProcessor` and two cooperative mixins: `ValidationMixin` and `AuditMixin`. **Acceptance criteria:** each stage executes once in MRO order; all constructors cooperate with `super()`; unknown keywords fail; audit output redacts secrets; a minimal interface contract is tested; integration tests prove combined behavior rather than only isolated mixin methods.

## C6. Safe copy and persistence boundary (Lesson 11)

Implement a `JobConfig` with nested mutable state, shared references, a lock, and a runtime-only connection placeholder. Define a deep-copy policy preserving intended shared aliases while separating mutable state. Define a serialization policy that stores only portable data and recreates runtime-only fields. **Acceptance criteria:** tests verify identity graph relationships, lock independence, versioned state migration, and cleanup. Never deserialize untrusted pickle. For external data, use JSON or another schema-based format with validation.

## C7. Module capstone — `datamodel_kit`

Build a small tested package with: (a) a hashable value object, (b) a sequence or mapping implementation, (c) one validating descriptor or property, (d) a slotted record whose memory footprint is measured, (e) a cooperative mixin chain, (f) an ABC or Protocol for a plugin, and (g) a copy/persistence example. Include `pytest` tests and a short README.

**Acceptance criteria:**
- Public behavior is documented and typed.
- Equality/hash and ordering contracts are tested.
- Container protocol behavior matches Python conventions.
- Unsupported operators return `NotImplemented` where appropriate.
- Validation failures are deterministic and informative.
- Memory claims are measured and qualified, not guessed.
- MRO and mixin execution order are tested.
- ABC/Protocol choice is justified.
- Deep-copy graph relationships are tested.
- Pickle is never applied to untrusted data; resource ownership is explicit.
- All tests pass on the stated Python version; lint/type-check results are reported only if actually run.


## C8. Roadmap mini-project — `datamodel_kit`

Build the exact module-roadmap mini-project as a package in a `uv` project with `pytest`, `ruff`, and type hints. Include:

1. `Money`: immutable value object with hash, ordering, arithmetic, currency safety, and formatting.
2. `TypedField`: descriptors for validated/coerced fields with useful errors (positive, bounded, regex-matching, and enum-valued fields).
3. `FrozenRecord`: slotted, hashable record base using descriptors.
4. `OrderedCatalog`: a `MutableMapping` with a slice-aware sequence view.
5. `SerialisableMixin`: JSON round-trip plus safe `__getstate__` behavior; do not serialize runtime-only resources.
6. A benchmark script comparing dict-based, slotted, and dataclass records for 1,000,000 objects using `tracemalloc` for memory and `timeit` for speed.

**Acceptance criteria:** at least 90% branch coverage on the public API; `ruff` and a chosen type checker run clean; a README contains usage examples; `DESIGN.md` documents every implemented special method and why it exists. Record actual commands/results—do not claim tools ran unless they did. Keep JSON as the safe interchange format for external data; never unpickle untrusted bytes.

### Capstone review rubric (100 points)

| Area | Points | Full-credit evidence |
|---|---:|---|
| Data-model contracts | 15 | Correct equality/hash/order and formatting semantics |
| Protocol behavior | 15 | Correct container/numeric protocols and edge cases |
| Validation and descriptors | 10 | Per-instance state, clear errors, lookup semantics understood |
| Memory and slots | 10 | Reproducible measurement and honest interpretation |
| MRO and mixins | 15 | Cooperative chain, no duplicate calls, collision tests |
| ABC/Protocol design | 10 | Minimal, justified interface and meaningful tests |
| Copy/persistence/security | 15 | Alias/cycle preservation, state migration, safe security boundary |
| Documentation and test quality | 10 | Runnable examples, useful tests, clear assumptions |

---

# Part III — Answer key and reference guidance

> Use this section after attempting Part I. Answers describe a defensible reference approach; alternatives are valid when they preserve the stated contract and are tested.

## Lesson 01 answers

**A01.** `repr` is for debugging/developer inspection and should be unambiguous; ideally it resembles a constructor expression when practical. `str` is the friendlier user-facing representation. If `__str__` is absent, `str(x)` falls back to `__repr__`.

**A02.** If `a == b`, then `hash(a) == hash(b)` must hold. Hashes need not be unique. A key's hash/equality-relevant state must remain stable while it is in a set/dict; mutating it can make lookup fail or produce surprising membership behavior.

**A03.** Equality should model the domain's equivalence relation, not claim unrelated objects are equal by accident. Return `NotImplemented` when the type does not know how to compare to the other operand; Python can try reflected dispatch or conclude equality/ordering according to the operator. Returning `False` can suppress a meaningful comparison implemented by the other type.

**A04.** `bool(x)` calls `__bool__` if present; otherwise it uses `__len__` if present (`0` is false); otherwise instances are truthy. `__bool__` must return `bool`, and `__len__` must return a non-negative integer.

**A05.** Output: `True False 1`. The instances are distinct but equal and have equal hashes, so the set retains one logical key.

**A06.** NaN is unequal to itself: `nan == nan` is `False`. It violates ordinary reflexivity, and calculations/comparisons involving it need explicit policy. Tests should use `math.isnan` rather than equality to detect NaN.

**A07.** Reference:
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Coordinate:
    x: int
    y: int


def test_coordinate_hashing():
    a, b = Coordinate(2, 5), Coordinate(2, 5)
    assert a == b and a is not b
    assert hash(a) == hash(b)
    assert {a: "found"}[b] == "found"
```
Frozen dataclasses with hashable fields generate a compatible hash. If a field is mutable/unhashable, redesign the value object rather than forcing an unsafe hash.

**A08.** One valid design:
```python
class Money:
    def __init__(self, amount, currency):
        self.amount, self.currency = amount, currency
    def __format__(self, spec):
        if spec == "c":
            return f"{self.amount:.2f} {self.currency}"
        if spec == ".2f":
            return format(self.amount, ".2f")
        raise ValueError(f"unsupported format specifier: {spec!r}")
    def __repr__(self):
        return f"Money(amount={self.amount!r}, currency={self.currency!r})"
```
A production implementation should choose a numeric type and rounding policy explicitly. `__repr__` must not interpolate `self!r` or otherwise call itself recursively.

**A09.** Defects: comparing an unrelated object accesses `.email` and can raise `AttributeError`; hash uses original casing while equality ignores casing. Repair:
```python
class UserKey:
    def __init__(self, email): self.email = email.casefold()
    def __eq__(self, other):
        if not isinstance(other, UserKey): return NotImplemented
        return self.email == other.email
    def __hash__(self): return hash(self.email)
```
If email normalization has domain-specific rules, use the same canonicalization for equality and hashing and avoid mutating the canonical value.

**A10.** Test equal-but-distinct values, symmetry and transitivity across triples, unrelated types, `hash(a) == hash(b)` whenever `a == b`, and stable hash across the object's lifetime. Do not assert exact hash integers: hash randomization and implementation/version differences make them unsuitable persistent values.

**A11.** `dataclass(frozen=True)` is a concise way to express immutable value semantics and can generate a compatible hash when fields permit. `unsafe_hash=True` can generate a hash even though equality-relevant state may be mutable; mutation while keyed breaks dictionary/set assumptions. Prefer immutable hash-relevant fields.

**A12.** Store normalized `source` and `schema_version` as the identity fields; leave `display_label` out of `__eq__` and `__hash__` (for dataclasses, use `field(compare=False, hash=False)`). Test that changing the display label does not alter identity, and that equal keys retrieve the same cache entry. Avoid mutating identity fields after insertion.

## Lesson 02 answers

**A13.** `__lt__`, `__le__`, `__eq__`, `__ne__`, `__gt__`, `__ge__`. `sorted()` normally relies on `<` comparisons between elements; `key=` can instead transform values to comparable keys.

**A14.** A total order compares every pair consistently; a partial order can leave some pairs incomparable. Set inclusion is a partial order; NaN also defeats ordinary total-order assumptions for floating-point values.

**A15.** `total_ordering` fills in the remaining ordering methods from `__eq__` and one of `__lt__`, `__le__`, `__gt__`, `__ge__`. Implementing methods directly can improve clarity, performance, or domain-specific behavior.

**A16.** `key=` makes one operation's sort policy local and explicit. `cmp_to_key` adapts a legacy two-argument comparator when rewriting it as a key is impractical; a native key function is generally simpler and faster.

**A17.** First output: `True`. Second output is `[Version(major=1, minor=11), Version(major=2, minor=0)]` (dataclass repr formatting). Tuple-like field ordering compares `major` first and then `minor`.

**A18.** Python sorting uses comparisons but NaN compares neither less-than nor equal in ordinary ways, so a list containing NaN may not have a meaningful, portable domain order. Define an explicit key that places NaNs, rejects them, or maps them to a documented sentinel.

**A19.** Reference:
```python
from dataclasses import dataclass

@dataclass
class Job:
    priority: int
    created_at: int
    name: str
    def __lt__(self, other):
        if not isinstance(other, Job): return NotImplemented
        return (self.priority, self.created_at) < (other.priority, other.created_at)

jobs = [Job(2, 10, "b"), Job(1, 20, "c"), Job(1, 10, "a")]
ordered = sorted(jobs, key=lambda j: (j.priority, j.created_at))
```
Use `key=` if only the caller needs that ordering. If implementing `<`, consider whether equality and all other comparisons are needed by the API.

**A20.** Non-transitive comparisons violate assumptions used by sorting/search/priority structures and can produce unintuitive results. Use an exact, transitive domain rule; if tolerance is required, quantize values to explicit buckets or use a key, and validate operand type. Do not promise ordering where the domain has none.

**A21.** Test same-object comparisons, pairwise consistency, transitivity over triples, equality/order consistency, and unsupported types. For a partial order, test its actual laws (for example transitivity) without requiring every pair to be comparable.

**A22.** `bisect` locates insertion positions in an already sorted sequence based on comparisons; `heapq` maintains a heap property through comparisons. Mutating a priority field in-place can invalidate the structure without reheapifying. `cmp_to_key` wraps a comparator into objects that expose ordering; `key=` computes a sort key directly.

**A23.** Keep equality based on job ID, and sort with `(priority, sequence)` using a key. If defining class ordering, document that ordering is not the same as identity and test ties, equality of different IDs, and stable tie behavior.

## Lesson 03 answers

**A24.** `len`→`__len__`; indexing→`__getitem__`; iteration→`__iter__`; membership→`__contains__` or iteration fallback; deletion→`__delitem__`; reversed→`__reversed__` or sequence fallback using `__len__`/`__getitem__`. Legacy iteration requests integer indices starting at zero until `IndexError` when `__iter__` is absent.

**A25.** `__int__` converts to an integer, potentially truncating; `__index__` supplies an exact integer for indexing/slicing and APIs requiring an integer index. Do not use it for approximate conversion.

**A26.** For `Sequence`, implement `__getitem__` and `__len__`; iteration and other methods can often be inherited from `collections.abc.Sequence`. `__length_hint__` is an optimization hint, not a correctness guarantee.

**A27.** Output is `[0, 10, 20]` then `True`. The fallback iterates via successive indices until `IndexError`; membership searches those values.

**A28.** A slice object (`slice(1, 4, None)`) is passed to `__getitem__`. Support slicing explicitly by applying it to backing storage; tuple indices such as `(1, 2)` can represent multidimensional access if the class documents that API.

**A29.** Example:
```python
from collections.abc import Sequence

class Window(Sequence):
    def __init__(self, values): self._values = tuple(values)
    def __len__(self): return len(self._values)
    def __getitem__(self, index): return self._values[index]
    def __iter__(self): return iter(self._values)

def test_window():
    w = Window([4, 5, 6])
    assert w[-1] == 6
    assert list(w[1:]) == [5, 6]
    assert list(w[2:2]) == []
```
Tuple indexing naturally raises `TypeError` for unsupported index types and `IndexError` for out-of-range integer indices. Slicing returns a tuple here; a different API may return a `Window` if documented.

**A30.** Example:
```python
class AutoDict(dict):
    def __missing__(self, key):
        value = []
        self[key] = value
        return value

def test_missing():
    d = AutoDict()
    assert d["x"] == [] and "x" in d
    assert d.get("y") is None and "y" not in d
```
`dict.get` does not invoke `__missing__`.

**A31.** `list.index` returns an integer or raises `ValueError`; membership must return a Boolean. Correct implementation: `return value in self._items` (if this is not itself a recursive call). For an absent value, return `False` rather than raise.

**A32.** Test valid and invalid integer indices, negative indices, slices with steps, deletion, empty sequence, iteration order, and mutation policy. A robust API may specify that mutation during iteration is unsupported or that iteration uses a snapshot; avoid accidental undocumented behavior.

**A33.** Built-in subclasses may have C-level operations that bypass overridden Python-level hooks, so invariants can be broken unexpectedly. Composition keeps storage private; implementing `MutableMapping`'s required methods provides standard mix-ins without subclassing `dict` directly.

**A34.** Implement `__getitem__`, `__iter__`, and `__len__` over private storage. Do not expose mutable storage directly. Test key iteration, membership, `get`, `items`, `values`, equality, missing-key `KeyError`, and empty mapping behavior.

## Lesson 04 answers

**A35.** `+`→`__add__`; reflected addition→`__radd__`; `+=`→`__iadd__` (or fallback to normal addition/rebinding); unary `-`→`__neg__`; `abs(x)`→`__abs__`; `~x`→`__invert__`; `@`→`__matmul__`/`__rmatmul__`. The meaning of matrix multiplication is defined by the type, not by Python itself.

**A36.** `NotImplemented` tells the operator dispatcher the method does not support the operand combination. `NotImplementedError` is an exception for an intentionally unimplemented operation and does not trigger normal reflected dispatch.

**A37.** Python tries the appropriate left operation and may try the right reflected method; a right-hand subclass can receive priority in documented dispatch cases. `__iadd__` may mutate for mutable types; immutable types commonly return a new value. Preserve intuitive semantics and document identity behavior.

**A38.** Decimal arithmetic is designed for decimal values when created from strings/integers, avoiding binary-float representation artifacts. `Fraction` represents rational values exactly when its numerator/denominator inputs are exact. Mixing numeric families is not always supported; don't silently coerce without a domain policy.

**A39.** Output: `[1, 2] True`. `__iadd__` mutates the same object and returns it, so the alias sees the change.

**A40.** If both applicable operations return `NotImplemented`, Python raises `TypeError` for the operator. Returning `None` is a valid returned result, not a dispatch signal, and may silently produce a meaningless result.

**A41.** Reference:
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Vector:
    x: float
    y: float
    def __add__(self, other):
        if not isinstance(other, Vector): return NotImplemented
        return Vector(self.x + other.x, self.y + other.y)
    def __neg__(self): return Vector(-self.x, -self.y)
    def __mul__(self, scalar):
        if not isinstance(scalar, (int, float)): return NotImplemented
        return Vector(self.x * scalar, self.y * scalar)
    def __rmul__(self, scalar): return self * scalar

def test_vector():
    v = Vector(1, 2)
    assert v + Vector(3, 4) == Vector(4, 6)
    assert 3 * v == Vector(3, 6)
    assert -v == Vector(-1, -2)
    assert v == Vector(1, 2)
```
A stricter numeric type policy may exclude `bool` and may use `Decimal`/`Fraction` deliberately.

**A42.** Currency mismatch must not silently add; mutating `self` violates expected arithmetic value semantics. Validate currency and return a new value; for unsupported types return `NotImplemented`, and for same-type domain mismatch raise a documented exception such as `ValueError`.

**A43.** Test intended pairs, exactness, rounding, overflow/invalid values, and unsupported mixed families. Do not automatically coerce all inputs to `float`: it can lose decimal precision and rational exactness. Define a supported interoperability matrix and reject unsupported combinations explicitly.

**A44.** Bitwise methods correspond to bitwise operators; `__int__` and `__float__` perform conversions, while `__index__` is exact integer-index conversion. NumPy has additional dispatch protocols such as `__array_priority__` and `__array_ufunc__`; test them only in an environment with NumPy installed. Allocation-heavy operators may create many temporaries; profile before optimizing.

**A45.** Validate compatible dimensions and define shape errors clearly. Implement `__matmul__` for supported matrix operands and return `NotImplemented` otherwise. Tests should include identity matrices, rectangular compatible products, incompatible dimensions, empty dimensions if supported, and floating tolerance using `math.isclose` or an appropriate array testing helper.

## Lesson 05 answers

**A46.** Store the value in a private attribute through the setter so validation is applied consistently. A read-only property can derive a value without allowing direct public assignment.

**A47.** Use a method for operations that are expensive, have side effects, require parameters, or communicate an action. A property should generally feel like cheap attribute access even if its implementation computes a value.

**A48.** `cached_property` computes once and stores the result as an attribute on the instance, usually in `__dict__`; deleting that attribute invalidates the cache. It normally needs an instance dictionary, so a slots-only class without `__dict__` cannot use it as-is.

**A49.** Output: `10`. A property is a data descriptor and takes precedence over an instance dictionary entry of the same name.

**A50.** Reference:
```python
class Temperature:
    def __init__(self, celsius: float) -> None:
        self.celsius = celsius
    @property
    def celsius(self) -> float:
        return self._celsius
    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15: raise ValueError("below absolute zero")
        self._celsius = float(value)
    @property
    def fahrenheit(self) -> float:
        return self.celsius * 9 / 5 + 32
    @fahrenheit.setter
    def fahrenheit(self, value: float) -> None:
        self.celsius = (value - 32) * 5 / 9

def test_temperature():
    t = Temperature(0)
    assert t.fahrenheit == 32
    t.fahrenheit = 212
    assert abs(t.celsius - 100) < 1e-9
```
Also test `-273.15` accepted and lower values rejected.

**A51.** The cached result becomes stale when source data changes. Provide a setter/update method that deletes the cached attribute or computes from immutable input. Concurrent first access may compute more than once depending on Python version/implementation; synchronize explicitly if exactly-once computation matters.

**A52.** Test accepted/rejected values, boundary conditions, deletion, subclass overrides, cache hit/invalidation, and setter type annotations. Property getter and setter should express the same public value type unless there is a deliberate conversion policy.

**A53.** `property` recomputes every access; `cached_property` caches but needs suitable storage and invalidation; a method signals an operation/parameterization. Python 3.12 removed the undocumented per-property lock from `cached_property`, so code should not rely on exactly-once evaluation. Use explicit synchronization if necessary.

**A54.** Normalize `email` at assignment and ensure every source-data update invalidates `normalized_rows`. Test case normalization, invalid email policy, cache reuse, update invalidation, and independent caches across instances.

## Lesson 06 answers

**A55.** Data descriptors define `__set__` and/or `__delete__` (properties are common examples); non-data descriptors only define `__get__` (ordinary functions are classic examples). Data descriptors take precedence over instance dictionary entries; instance entries can shadow non-data descriptors.

**A56.** `__set_name__` tells a descriptor the owner class and assigned attribute name during class creation, enabling automatic private storage names and clearer diagnostics. A descriptor on the class is shared as behavior; per-instance values belong in the instance or another per-instance store.

**A57.** Simplified instance lookup: data descriptor; instance dictionary; non-data descriptor/class attribute; then `__getattr__` if normal lookup raises `AttributeError`. `__getattribute__` runs for every normal attribute access, so careless recursion or skipped descriptor logic can break nearly everything; use `object.__getattribute__` for safe delegation.

**A58.** Output: `instance descriptor`. The instance dictionary shadows a non-data descriptor on instance access, while `Example.value` invokes the descriptor with `obj=None`.

**A59.** `inspect.getattr_static` bypasses normal dynamic attribute lookup/descriptor execution, useful for introspection, documentation, debugging, and inspecting potentially side-effectful descriptors safely.

**A60.** Reference (finite positive numeric values):
```python
import math
class PositiveNumber:
    def __set_name__(self, owner, name): self.storage = f"_{name}"
    def __get__(self, obj, owner=None):
        if obj is None: return self
        return getattr(obj, self.storage)
    def __set__(self, obj, value):
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0 or (isinstance(value, float) and not math.isfinite(value)):
            raise ValueError("value must be a finite positive number")
        setattr(obj, self.storage, value)

class Product:
    price = PositiveNumber()

def test_descriptor():
    a, b = Product(), Product()
    a.price = 3
    b.price = 8
    assert (a.price, b.price) == (3, 8)
```
For slots-only hosts, reserve storage slots or use a deliberate external storage design.

**A61.** Descriptor instances are shared at class level; `self.value` therefore stores one shared value. Store under a per-instance name (for example `_<field>`) or use a weak-key map where appropriate. Avoid collisions with other descriptors and account for slots.

**A62.** Test class/instance access, valid/invalid values, deletion behavior, inherited owner/name metadata, and recursive lookup. Typing can use generics/overloads for class access versus instance access, or a descriptor library's established typing pattern.

**A63.** Functions implement descriptor binding, turning `obj.method` into a bound method with `self`. `classmethod` binds the class; `staticmethod` does not bind an instance/class. Slots use member descriptors for slot storage. Cache only when measurement shows benefit and invalidation semantics are clear.

**A64.** Use descriptors as class-level field declarations, but keep values per instance and validation deterministic. Test each descriptor alone and through the full schema, including inheritance, duplicate names, slots storage, and invalid assignment. Document whether class access returns descriptor metadata.

## Lesson 07 answers

**A65.** `__slots__` declares fixed attribute storage and usually removes the instance dictionary unless explicitly included or inherited. Arbitrary attributes fail without a dictionary. Weak references require `__weakref__` support in a suitable class layout.

**A66.** `sys.getsizeof` reports shallow size only. A dict-backed instance's dictionary and all referenced objects are separate allocations; use comparable workloads and `tracemalloc` for broader allocation measurements.

**A67.** A subclass without `__slots__` typically regains an instance dictionary. Multiple inheritance with incompatible non-empty slots can raise `TypeError`; design the layout deliberately and test supported inheritance paths.

**A68.** `p.x = 1` succeeds; `p.label = "origin"` raises `AttributeError` because no slot or instance dictionary exists for `label`.

**A69.** Example:
```python
class Point:
    __slots__ = ("x", "y", "__weakref__")
    def __init__(self, x, y): self.x, self.y = x, y
```
This is not immutable: slots restrict attribute names but do not prevent reassignment. Enforce immutability with a frozen dataclass or controlled assignment policy, and test it.

**A70.** Compare many objects under the same Python executable, identical fields/data, warm-up, and repeatable allocation phase; use `tracemalloc.start()` and snapshots or peak memory. Include the dictionary when interpreting `getsizeof`. Report methodology/version rather than asserting a universal byte count.

**A71.** Test slot assignment, dynamic-attribute rejection, subclass dictionary behavior, weakrefs, pickling round trips, and descriptors. If a subclass adds `__dict__` or `__weakref__`, verify that the intended memory/weakref constraints still hold.

**A72.** Use slots after profiling indicates many instances and memory pressure. Avoid when dynamic attributes, flexible subclassing, introspection, or third-party tooling is important. Include weakref, serialization, inheritance, and debugging trade-offs.

**A73.** A frozen slotted dataclass is a good candidate for immutable records but must be measured with realistic field values and object counts. Confirm supported Python version, serialization behavior, weakrefs, construction cost, and no reliance on undocumented memory numbers.

## Lesson 08 answers

**A74.** MRO is the ordered class sequence Python searches for methods/attributes. Inspect `Class.__mro__` or `Class.mro()` to understand which implementation a call reaches next.

**A75.** Zero-argument `super()` uses the current class and instance to find the next implementation after the current class in the MRO. In multiple inheritance, that “next” class need not be the lexical parent.

**A76.** C3 places subclasses before their parents, preserves the order specified by bases, and is monotonic (subclass ordering doesn't contradict a base's established order). Conflicting precedence constraints can make a consistent order impossible, so Python raises `TypeError` at class creation.

**A77.** Call order: `D`, `B`, `C`, `A`; MRO list: `['D', 'B', 'C', 'A', 'object']`.

**A78.** Use keyword-only parameters and consume only owned arguments, passing remaining `**kwargs` to `super().__init__(**kwargs)`. The root class should reject leftover keywords by calling `object.__init__` with them (which raises `TypeError`) or validating them explicitly. Test every field and one call per class.

**A79.** Explicitly calling `Base.__init__` from both branches initializes the shared base twice and bypasses cooperative order. Use `super()` in every participant and compatible signatures so C3 invokes each implementation once.

**A80.** Test expected MRO, a call counter/log per class, parameter propagation, exactly-once execution, and unknown keyword failure.

**A81.** Every cooperative implementation must accept/pass arguments compatible with the chain. Keyword-only parameters reduce positional ambiguity; `**kwargs` should be passed onward and unexpected keys rejected at the root, not silently ignored.

**A82.** Each mixin should transform then pass the record onward (or explicitly define the reverse order) and avoid hidden side effects. Test the expected sequence, one invocation per stage, errors, repeated processing, and MRO after class composition changes.

## Lesson 09 answers

**A83.** A mixin adds one focused, reusable behavior to another class and is usually not a complete domain object by itself. Keep it small, document host requirements, and avoid owning complex state.

**A84.** Earlier bases appear earlier in the MRO and can override later behavior. Collisions happen when mixins define the same method/attribute or assume incompatible state/initialization.

**A85.** Composition keeps dependencies explicit and avoids MRO conflicts; inheritance is reasonable when behavior is a stable “is-a” relation or cooperative behavior reuse is deliberate. Logging/serialization can often be composed as collaborators.

**A86.** `JsonMixin` is searched before `AuditMixin` and `BaseService`; if each calls `super()`, the chain continues in that MRO order. Reordering bases changes which implementation executes first. Exact output depends on each implementation's return/composition logic, which the prompt must define.

**A87.** Avoid serializing `__dict__` blindly. Provide an explicit allowlist or serializer that excludes credentials, locks, file handles, connections, and other runtime state. Use `repr` only for safe diagnostic fields and redact secrets.

**A88.** Problems include constructor coupling, global mutable state, broken cooperative chain, and an assumption about a specific host. Move state to the host or a collaborator, avoid required mixin `__init__` or make it cooperative, call `super()` as part of a documented chain, and validate required host attributes explicitly.

**A89.** Test isolated behavior and composed classes: collisions, exact MRO, initialization, state isolation, diamond paths, and error propagation. Isolated tests cannot prove interactions or call-once behavior.

**A90.** Choose a mixin for focused cooperative behavior, ABC for nominal runtime contract and shared implementation, Protocol for structural static typing, and composition for explicit collaborators/state. Justify the choice by stability and complexity.

**A91.** Use a documented chain such as `MetricsMixin, LoggingMixin, BaseProcessor`; every override calls `super()` and each concern has a clear contract. Redact secrets before logging, propagate or wrap errors deliberately, and test the full processor's execution sequence.

## Lesson 10 answers

**A92.** `ABC` provides an abstract base metaclass; `@abstractmethod` marks required methods/properties. Python prevents instantiation when the class still has abstract methods, not simply because the class definition exists.

**A93.** `Mapping` requires `__getitem__`, `__iter__`, and `__len__`. It supplies mix-ins such as `get`, `keys`, `items`, `values`, membership and mapping equality behavior.

**A94.** ABC inheritance is nominal and participates in MRO; `.register()` declares a virtual subclass for `isinstance`/`issubclass` without injecting methods or changing the MRO; Protocol is structural for static typing (runtime checking is limited); duck typing simply relies on supported operations.

**A95.** Outputs: `True`, `True`, `False`. Registration affects subclass/instance checks but does not put `PluginABC` in `ThirdParty.__mro__`.

**A96.** Reference:
```python
from collections.abc import Mapping

class ReadOnlyMap(Mapping):
    def __init__(self, data): self._data = dict(data)
    def __getitem__(self, key): return self._data[key]
    def __iter__(self): return iter(self._data)
    def __len__(self): return len(self._data)

def test_mapping():
    m = ReadOnlyMap({"a": 1})
    assert m.get("a") == 1
    assert list(m.keys()) == ["a"]
    assert list(m.items()) == [("a", 1)]
    assert "a" in m
```
For strict read-only guarantees, avoid exposing `_data` and consider whether nested values need copying/immutability.

**A97.** Correct order is typically `@classmethod` outermost and `@abstractmethod` innermost:
```python
from abc import ABC, abstractmethod
class Factory(ABC):
    @classmethod
    @abstractmethod
    def build(cls): ...
```
The abstract requirement is checked at instantiation time; a class can be defined while remaining abstract.

**A98.** Test instantiation failure for an incomplete ABC, successful concrete implementation, registered virtual subclass checks, no MRO change/method injection, Protocol structural behavior, and required Mapping mix-ins.

**A99.** Runtime-checkable protocols mostly test member presence, not static signature compatibility or type correctness. Use ABC when runtime enforcement/shared implementation is useful; Protocol when structural typing and third-party implementations are desired without inheritance coupling.

**A100.** Define only stable source operations (for example `read_batches()` and perhaps a schema capability). Use ABC if the application owns/enforces runtime plugin registration, or Protocol if structural implementations should type-check without inheriting. Test contract behavior and malformed plugins; don't add abstract methods without a real consumer need.

## Lesson 11 answers

**A101.** Assignment creates another reference. Shallow copy creates a new outer container but shares children. Deep copy recursively copies supported graph nodes and uses a memo to preserve cycles and shared aliases. Serialization encodes state for later reconstruction; it is not the same as an in-memory copy.

**A102.** `__new__` creates/returns an instance; `__init__` initializes an instance after `__new__` returns an instance of the requested class. Override `__new__` for immutable built-in subclasses, controlled singleton/factory construction, or other allocation-level needs—not for ordinary initialization.

**A103.** Check `memo[id(self)]` first; create an uninitialized clone; store it in `memo` before recursively copying children. This breaks cycles and ensures repeated references to one source node point to one copied node.

**A104.** Locks and live resources are process-local and generally unpicklable or meaningless after restore. `__getstate__` should serialize portable logical state only; `__setstate__` restores data, migrates older state if needed, and creates fresh runtime-only resources.

**A105.** Output:
```
False True
True False
```
The shallow outer dictionary differs but its child is the original. Deep copy creates a new child and preserves the fact that `left` and `right` share one child.

**A106.** Reference:
```python
import copy

class Node:
    __slots__ = ("name", "child", "peer")
    def __init__(self, name): self.name, self.child, self.peer = name, None, None
    def __deepcopy__(self, memo):
        existing = memo.get(id(self))
        if existing is not None: return existing
        clone = type(self).__new__(type(self))
        memo[id(self)] = clone
        clone.name = copy.deepcopy(self.name, memo)
        clone.child = copy.deepcopy(self.child, memo)
        clone.peer = copy.deepcopy(self.peer, memo)
        return clone

def test_graph_copy():
    root = Node("root"); shared = Node("shared")
    root.child = shared; root.peer = shared; shared.child = root
    clone = copy.deepcopy(root)
    assert clone is not root
    assert clone.child is clone.peer
    assert clone.child.child is clone
```
For slots-only classes, ensure all slot fields are initialized. Use `type(self).__new__` only if subclass construction semantics support it; custom inheritance may require a carefully defined factory.

**A107.** Reference:
```python
import pickle
import threading

class Cache:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()
    def __getstate__(self):
        return {"version": 1, "data": self.data}
    def __setstate__(self, state):
        version = state.get("version", 0)
        if version not in (0, 1): raise ValueError("unsupported state version")
        self.data = dict(state.get("data", {}))
        self.lock = threading.Lock()

def test_trusted_round_trip():
    original = Cache(); original.data["n"] = 3
    # Safe only because bytes are generated locally by this trusted test.
    restored = pickle.loads(pickle.dumps(original))
    assert restored.data == original.data
    assert restored.lock is not original.lock
```
Never call `pickle.loads` on network/user-controlled/untrusted bytes. This round-trip test is deliberately restricted to trusted bytes it just generated.

**A108.** `__del__` timing is not deterministic and can be skipped/complicated during shutdown; file/socket closure belongs to explicit ownership and context managers. Open handles should not be pickled; network payloads must not be passed to pickle. Use `with socket.create_connection(...) as sock` or explicit `close()` in `finally`, and parse external JSON/schema-validated data. A signed pickle remains unsafe if its signer or key policy is compromised and is not a general safe interchange format.

**A109.** Test alias/cycle topology and data independence; round-trip portable state; migrate older state versions; test finalizer callback behavior through explicit invocation/detachment or weak references where possible. Do not assert exact garbage-collection or interpreter-shutdown timing. Test resource cleanup deterministically with context managers.

**A110.** `__reduce__` and `__reduce_ex__` specify reconstruction instructions; `__reduce_ex__` receives a protocol version and is generally preferred by pickle when available. `copyreg` registers reduction functions for types. When a class does not provide a dedicated `__copy__`/`__deepcopy__` hook, the `copy` module can also use the pickle reduction protocol to reconstruct a copy. Pickle protocol versions and Python/class refactors affect compatibility; pickle is Python-specific and unsuitable as a durable public interchange contract. **Never unpickle untrusted data**: reconstruction can execute arbitrary code. Prefer validated JSON, MessagePack, Protocol Buffers, or another schema-based format; signatures do not make arbitrary pickle safe against all threats.

**A111.** `weakref.ref` observes an object without keeping it alive; `weakref.finalize` registers a callback when the referent is about to be finalized and keeps the finalizer alive until it runs. The callback/arguments must not strongly retain the referent. Finalizers are fallback cleanup, not deterministic close semantics; shutdown ordering is tricky and an object can be resurrected by `__del__` in edge cases. Use context managers for reliable resource release.

**A112.** Deep-copy logical configuration while preserving intended graph topology via `memo`; decide whether locks should be cloned as fresh locks or treated as runtime-only. Do not copy live connections blindly. Serialize only schema/version and portable values; restore/migrate state and recreate lock/connection lazily. Test nested mutations, aliases, cycles, independent locks, old/new versions, resource close paths, and the untrusted-pickle prohibition.


**A113.** Defining `__eq__` without a compatible `__hash__` makes instances unhashable by default, so set construction raises `TypeError`. For unrelated types, return `NotImplemented` so Python can try the other operand's comparison; avoid accessing arbitrary attributes. A constructor-style representation could be `return f"Money({self.amount!r}, {self.currency!r})"`, provided `Money` is resolvable in the evaluation namespace and those constructor arguments faithfully recreate the value. Never `eval` untrusted text.

**A114.** `__getitem__` receives a tuple `(slice(1, 3, None), 0)`. `UserDict` is a wrapper around an underlying mapping and routes its operations through a more consistently overridable Python-level interface; it can be safer for validation than assuming every built-in `dict` mutation path calls an overridden `__setitem__`.

**A115.** `sum` starts with integer `0`, so the first operation is `0 + Vector(...)`. A suitable implementation is `def __radd__(self, other): return self if type(other) is int and other == 0 else NotImplemented`, with the zero check intentionally narrow; do not accept arbitrary numeric values unless specified. Without `__iadd__`, augmented assignment falls back to the normal addition operation and rebinds the target to the result when that operation succeeds.

**A116.** The simplified precedence is: (1) data descriptor on the class, (2) instance dictionary, (3) non-data descriptor or ordinary class attribute, (4) `__getattr__` fallback if normal lookup raises `AttributeError`. On class access, `obj is None`; returning `self` exposes the descriptor/declaration metadata without pretending a particular instance's value exists.

**A117.** Create equivalent ordinary/slotted classes with the same fields, warm up construction, start `tracemalloc`, allocate a large list of (for example) 1,000,000 instances, take a snapshot or peak reading, release references, and repeat in separate runs/processes. Report Python version/build and exact measurement method. A normal instance usually has an instance `__dict__` and weak-reference support; a slots-only instance normally has neither unless requested/inherited. Actual ratios vary by build and workload.

**A118.** If `B.__init__` omits `super()`, later classes in the MRO chain—including `C` and potentially the shared base—are skipped from that call path. The roadmap self-check statement is technically incorrect as written: `class X(A, B)` is valid when `class A(B)`, because both constraints put `A` before `B` (the redundant base is accepted). The conflicting order is `class X(B, A)`, because it requires `B` before `A` while `A` itself must precede `B`, so C3 cannot construct a consistent MRO and Python raises `TypeError`. In a `D` instance, `super()` inside `B` continues after `B` in `D.__mro__`—for `D(B, C)` that is `C`, not necessarily `A`.

**A119.** Example:
```python
from datetime import datetime, timezone
class TimestampMixin:
    def __init__(self, **kwargs):
        self.created_at = datetime.now(timezone.utc)
        super().__init__(**kwargs)
class Record:
    def __init__(self, name, **kwargs):
        self.name = name
        super().__init__(**kwargs)
class Event(TimestampMixin, Record):
    pass

e = Event(name="loaded")
print([c.__name__ for c in Event.__mro__])
```
In a real chain, ensure the root rejects unknown keywords. Composition is often preferable when behavior has independent state/lifecycle, when multiple behaviors are chosen dynamically, or when mixin MRO/signature coordination becomes fragile.

**A120.** Example (illustrative fallback; `release_handle` must not retain the owner object):
```python
import weakref
class Resource:
    def __init__(self, handle):
        self._handle = handle
        self._finalizer = weakref.finalize(self, handle.close)
```
This is only safe if `handle.close` does not retain `self` and the handle's lifetime is intended to be owned by the resource. A more explicit callback such as `weakref.finalize(self, close_handle, handle)` can make the ownership contract clearer. Prefer `with Resource(...) as resource:` and an explicit `close()` because finalization timing is not deterministic.

**A121.** `__init_subclass__` runs when a subclass is created and can validate/register the class; it is not an instance constructor. Example:
```python
class Plugin:
    registry = {}
    plugin_name = None
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.plugin_name:
            if cls.plugin_name in Plugin.registry:
                raise ValueError("duplicate plugin")
            Plugin.registry[cls.plugin_name] = cls
class CsvPlugin(Plugin):
    plugin_name = "csv"
```
For production, avoid relying on registration side effects before all import/configuration concerns are understood.

**A122.** `__class_getitem__` supports class subscription syntax such as `MyClass[int]` (often for generic/type metadata). `__instancecheck__` and `__subclasscheck__` customize `isinstance`/`issubclass` behavior on suitable metaclass implementations. These hooks can make type checks surprising, so document semantics and test positive/negative cases; they are not needed for ordinary classes.

**A123.** `dataclasses.replace()` works on Python 3.12 for dataclass instances. Python 3.13 adds `copy.replace(obj, **changes)`, which uses the object's replacement protocol (including `__replace__`) for supported types. It constructs a related object with selected fields changed; it does not promise recursive copying of every nested child. Tests should verify which nested references are shared.

**A124.** `id()` is an identity token only for an object's lifetime; it can be reused later and is not a stable database key. Small-integer caching/string interning are implementation details and can make some identities appear equal unexpectedly. `is` checks object identity; `==` checks domain value equality. Use explicit stable identifiers for business identity.

**A125.** Correct answers: **1-B, 2-B, 3-B, 4-C, 5-C, 6-C, 7-B.**


**A126.** One valid shallow-copy policy is:
```python
import copy
class Batch:
    def __init__(self, batch_id, rows):
        self.batch_id = batch_id
        self.rows = rows
    def __copy__(self):
        clone = type(self).__new__(type(self))
        clone.batch_id = self.batch_id
        clone.rows = self.rows  # intentional shallow sharing
        return clone

def test_batch_copy():
    rows = [{"n": 1}]
    original = Batch("b-1", rows)
    clone = copy.copy(original)
    assert clone is not original
    assert clone.batch_id == original.batch_id
    assert clone.rows is original.rows
```
If the intended semantics require a new list but shared row objects, use `self.rows.copy()` instead and test that exact contract. Document the policy; do not describe a shallow copy as recursively independent.

## Cumulative assessment reference guidance

**C1.** Use `Decimal` and immutable fields; normalize currency codes; ensure equality/hash use the same normalized identity. Addition should return a new `Money` only for matching currencies; define quantization and non-finite amount policy. Ordering across currencies should raise or be undefined unless a conversion-rate policy is explicit. Test hash contracts and unsupported operands.

**C2.** Implement the three Mapping primitives over private copied storage. Use `Mapping` mix-ins and ensure nested mutable values do not accidentally expose mutable internals if read-only semantics are required.

**C3.** Use class-level descriptors with `__set_name__`, unique per-field storage names, per-instance state, explicit validation, and a defined class-access result. If using slots, declare storage slots or choose a compatible storage design.

**C4.** Measure equivalent object populations with `tracemalloc`; report Python build and method. `sys.getsizeof` is shallow, and exact byte totals are implementation-specific. Do not claim optimization without a repeatable measurement.

**C5.** Use keyword-only cooperative constructors and a single `super()` chain. The root consumes no unexpected keywords. Test exact execution order and redaction in the combined class.

**C6.** Define separate policies for in-memory copying and persistence. Deepcopy should preserve shared aliases/cycles while separating mutable nodes. Serialize logical state, not locks/connections; restore runtime resources fresh. Never deserialize untrusted pickle.

**C7.** Grade with the capstone rubric. Valid alternatives must satisfy all acceptance criteria and tests; a clever implementation that violates identity/hash, protocol, security, or resource contracts is not correct.


**C8.** Evaluate against the explicit six-component checklist. A strong submission includes contract tests for `Money`, validation and per-instance state tests for `TypedField`, slot/hash tests for `FrozenRecord`, mapping and slice semantics for `OrderedCatalog`, JSON round-trip and runtime-state exclusion for `SerialisableMixin`, and reproducible memory/speed benchmarks. The ≥90% branch-coverage target applies to the public API; report the coverage tool and result. `ruff` and a type checker must be run and their actual results recorded. README usage examples and `DESIGN.md` should explain the purpose and behavior of each special method. Do not use pickle for untrusted input.

---

# Part IV — Roadmap self-check traceability

The following table maps the exact lesson-roadmap self-check prompts to this bank and answer key. The roadmap's self-check questions are represented directly or by a question that asks for the same skill.

| Roadmap lesson | Roadmap self-check focus | Question IDs | Answer section |
|---|---|---|---|
| 01 | `repr` vs `str`; hashability and equality contract; frozen dataclass hash | Q01–Q04, Q07, Q09–Q12 | A01–A04, A07, A09–A12 |
| 02 | Requirement for `sorted`; `total_ordering`/equality; non-transitive comparison | Q13–Q21 | A13–A21 |
| 03 | Sequence protocol primitives; iteration fallback; built-in subclass pitfalls | Q24–Q34 | A24–A34 |
| 04 | `NotImplemented`; reflected dispatch; in-place operations and numeric interoperability | Q35–Q45 | A35–A45 |
| 05 | Setter validation; `cached_property` storage; property vs method | Q46–Q54 | A46–A54 |
| 06 | Descriptor types and lookup; `__set_name__`; bound methods/introspection | Q55–Q64 | A55–A64 |
| 07 | Slots layout; measuring memory; inheritance/weakrefs/pickling | Q65–Q73 | A65–A73 |
| 08 | MRO and `super`; C3; cooperative constructor behavior | Q74–Q82 | A74–A82 |
| 09 | Mixin contract; composition; collisions and cooperative chains | Q83–Q91 | A83–A91 |
| 10 | Mapping primitives; virtual registration vs inheritance; Protocol choice | Q92–Q100 | A92–A100 |
| 11 | `__new__` vs `__init__`; lock state restoration; replacing `__del__` | Q101–Q112 | A101–A112 |

## Additional roadmap coverage index

- `__bool__`, `__len__`, `__format__`, recursive representations, NaN: Q04, Q06, Q08, Q10.
- All six comparisons, dataclass ordering, `cmp_to_key`, `bisect`, `heapq`: Q13–Q23.
- `__setitem__`, `__delitem__`, `__missing__`, `__reversed__`, `__index__`, `__length_hint__`, slices, multidimensional indexing, iterator behavior: Q24–Q34.
- Arithmetic/unary/reflected/in-place, conversions, Decimal/Fraction, bitwise, `@`, NumPy awareness, performance: Q35–Q45.
- Property setters/deleters, inheritance, slots, dataclass and version concerns, cache invalidation: Q46–Q54.
- Data/non-data descriptors, `__getattribute__`, `__getattr__`, static inspection, bound methods, slots: Q55–Q64.
- `sys.getsizeof`, `tracemalloc`, weakrefs, dynamic attributes, pickling, inheritance: Q65–Q73.
- C3 order, cooperative constructors, signatures, diamond inheritance: Q74–Q82.
- State ownership, method collisions, fragile bases, composition trade-offs: Q83–Q91.
- Abstract properties/class methods, virtual subclass registration, ABC vs Protocol/duck typing, runtime limitations: Q92–Q100.
- Copy hooks/memo/cycles, copy-with-changes awareness, pickle hooks/reduction/protocol/security/versioning, lifecycle/finalizers, `__init_subclass__`/`__set_name__`, `__class_getitem__`, `__instancecheck__`/`__subclasscheck__`, slots/frozen dataclasses, `__replace__`, identity/interning: Q101–Q126 and C6. Exact self-check extensions: Q113–Q124; custom `__copy__`: Q126. Multiple-choice coverage: Q125.

## Python version and behavior notes

- Baseline is Python 3.12+. `copy.replace()` and the `__replace__` protocol are Python 3.13+; use `dataclasses.replace()` where appropriate on Python 3.12.
- `functools.cached_property` no longer uses its undocumented per-property lock starting in Python 3.12; do not rely on exactly-once concurrent evaluation.
- `__slots__` memory behavior, object sizes, and implementation details should be measured on the target interpreter rather than treated as language-level constants.
- Object finalization and garbage collection timing are not deterministic contracts. Prefer explicit resource ownership and context managers.
- Pickle examples are only for trusted local data. **Never unpickle untrusted input.**

---

# Part V — Learner progress checklist

Mark a box only after you can demonstrate the behavior with code, tests, or a clear explanation. Reading alone does not count as mastery.

| Lesson | L1–L2: explain | L3: trace | L4: implement | L5–L6: debug/test | L7: justify trade-offs | L8: integrate |
|---|---|---|---|---|---|---|
| 01 Representation/equality/hash | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| 02 Comparison/ordering | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| 03 Container protocols | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| 04 Operators/numeric protocols | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| 05 Properties/caching | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| 06 Descriptors/lookup | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| 07 Slots/memory | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| 08 MRO/`super()` | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| 09 Mixins/composition | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| 10 ABCs/Protocols | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| 11 Copy/pickle/lifecycle | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

## Demonstrated-ability rubric

Choose the highest level you can demonstrate consistently—not the level you feel familiar with.

| Level | Evidence | Next action |
|---|---|---|
| 0 — Not yet explainable | Cannot explain the purpose or predict basic behavior without notes. | Re-read the lesson, write a mental model in your own words, then retry L1/L2. |
| 1 — Understands, cannot implement | Can explain terms and trace examples but cannot build a working implementation independently. | Complete one small L4 task with a reference hidden; add tests. |
| 2 — Implements with guidance | Can implement with hints and can explain most lines, but misses edge cases. | Remove hints, add negative/boundary tests, and debug a deliberately broken version. |
| 3 — Independent implementation and testing | Can implement, test, and explain normal and boundary behavior without assistance. | Review protocol contracts and integration with neighboring lessons. |
| 4 — Production reasoning | Can diagnose edge cases, justify alternatives, identify compatibility/security risks, and support claims with tests or measurements. | Complete the relevant L7/L8 task and document trade-offs for review. |

## Suggested completion gate

Before considering the module complete:

- [ ] All 11 lessons have a demonstrated L1–L4 pass.
- [ ] Every lesson has at least one meaningful L5/L6 debugging or test exercise completed.
- [ ] Every roadmap self-check is answered without looking at the key, then reviewed.
- [ ] All cumulative tasks C1–C6 are implemented or reviewed against the rubric.
- [ ] Capstone C7 has tests for contracts, edge cases, and integration behavior.
- [ ] No performance claim is based only on `sys.getsizeof` or intuition.
- [ ] No pickle deserialization of untrusted data is present in code or tests.
- [ ] Test/lint/type-check outcomes are recorded truthfully for the actual environment used.

