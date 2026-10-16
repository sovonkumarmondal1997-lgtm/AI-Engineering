# MRO, `super()`, and Cooperative Inheritance

> **Stage:** Stage 1 — Programming & Computational Thinking  
> **Module:** 11 — Advanced Python Data Model and Object Design  
> **Lesson:** 08 of 11  
> **Audience:** Beginner to advanced Python learner, with data-engineering applications  
> **Recommended environment:** Python 3.12+; examples use language features available in modern Python 3.

## Learning outcomes

By the end of this lesson, you should be able to:

1. Explain inheritance, method overriding, and the method resolution order (MRO).
2. Inspect an MRO with `Class.__mro__`, `Class.mro()`, and `inspect.getmro()`.
3. Use zero-argument `super()` to extend behaviour without hard-coding a parent class.
4. Explain a diamond hierarchy and the three core properties of C3 linearization.
5. Build cooperative methods and constructors that pass control through a multiple-inheritance chain exactly once.
6. Use keyword-only arguments and `**kwargs` carefully in cooperative initialization.
7. Explain the `__class__` closure cell behind zero-argument `super()` and use the two-argument forms when appropriate.
8. Diagnose skipped methods, duplicate base initialization, inconsistent MROs, and incompatible signatures.
9. Recognize when composition is safer than inheritance.
10. Apply these ideas to extensible ingestion, validation, logging, and transformation components.

---

## 1. The big picture

Inheritance lets one class reuse or specialize behaviour from another class. In single inheritance, the lookup path is usually easy to picture: Python checks the child class, then its base class, then further ancestors.

Multiple inheritance allows a class to inherit from more than one base. It can be useful for combining small, independent behaviours, but it makes the lookup path more important. Python defines a deterministic order called the **method resolution order (MRO)**.

`super()` follows that order. It does **not** simply mean “call my parent.” More precisely, it creates a proxy that continues lookup **after a specified class in the MRO of a particular object or class**.

This distinction enables cooperative inheritance: each implementation performs its part, then hands control to the next implementation in the MRO.

### A useful mental model

Imagine a request moving through a chain of processing stages:

1. A class receives the request.
2. It performs its own work.
3. It calls `super()` to hand off to the next implementation.
4. The chain eventually reaches a terminal implementation that has no more work to delegate.

Every participant must agree on the method name, the argument contract, and the fact that it should continue the chain. If one class skips the hand-off, later classes do not run. If a class calls a named parent directly, a shared ancestor can run more than once.

### Why a data engineer should care

These mechanics matter when maintaining extensible systems such as:

- ingestion components with reusable retry, metrics, and validation behaviour;
- data-quality checks composed from focused mixins;
- framework classes that use `__init_subclass__` for registration;
- test fixtures that extend setup behaviour;
- third-party libraries with mixin-based APIs.

Multiple inheritance is not automatically better than composition. Use it when the behaviours are genuinely designed to cooperate and the MRO remains understandable.

---

## 2. Prerequisites and terminology

| Term | Meaning |
|---|---|
| Class | A definition describing objects and their behaviour. |
| Instance | An object created from a class. |
| Base class | A class listed in another class's inheritance declaration. |
| Subclass | A class derived from another class. |
| Override | A subclass defines a method with the same name as an inherited method. |
| MRO | The ordered sequence Python uses to resolve methods and attributes through a class hierarchy. |
| `super()` | A proxy that continues lookup after a class in the relevant MRO. |
| Cooperative method | A method that does its part and delegates with `super()` according to a shared contract. |
| Diamond inheritance | A hierarchy in which two branches inherit from a common ancestor. |
| C3 linearization | The algorithm Python uses to calculate a consistent MRO for new-style classes. |
| Mix-in | A focused class intended to add one behaviour when combined with other classes. |

Before continuing, be comfortable with `class`, `__init__`, instance methods, `self`, inheritance syntax, and method overriding.

---

## 3. Basic level: single inheritance and MRO

### 3.1 A simple inheritance chain

```python
class Base:
    def greet(self):
        return "base"


class Child(Base):
    def greet(self):
        return "child"


print(Child().greet())
print(Child.__mro__)
```

Expected output (the class representations may include a module name):

```text
child
(<class '__main__.Child'>, <class '__main__.Base'>, <class 'object'>)
```

Python looks for `greet` on `Child` first. It finds the override there, so `Base.greet` is not automatically called.

Every ordinary Python class ultimately inherits from `object`, directly or indirectly. Therefore, the MRO usually ends with `object`.

### 3.2 Inspect the MRO

```python
import inspect


class Record:
    pass


class CsvRecord(Record):
    pass


print(CsvRecord.__mro__)
print(CsvRecord.mro())
print(inspect.getmro(CsvRecord))
```

All three expressions expose the resolution order in slightly different forms:

- `CsvRecord.__mro__` is a tuple.
- `CsvRecord.mro()` returns a list.
- `inspect.getmro(CsvRecord)` returns a tuple.

For debugging, printing the MRO is often the fastest way to answer “which implementation comes next?”

### 3.3 Extend versus replace inherited behaviour

An override can completely replace inherited behaviour:

```python
class Parser:
    def parse(self, raw):
        return {"raw": raw}


class StrictParser(Parser):
    def parse(self, raw):
        if not raw:
            raise ValueError("Input must not be empty")
        return {"value": raw.strip()}
```

Or it can extend it:

```python
class Parser:
    def parse(self, raw):
        return {"raw": raw}


class AuditedParser(Parser):
    def parse(self, raw):
        result = super().parse(raw)
        result["audited"] = True
        return result


print(AuditedParser().parse("row-17"))
# {'raw': 'row-17', 'audited': True}
```

The second implementation reuses the next implementation selected by the MRO. This reduces duplicated logic and can make a class hierarchy easier to extend.

### 3.4 Zero-argument `super()`

Inside a normal instance method, this is the common form:

`super().method_name(arguments)`

Inside a class method, the same syntax works:

`super().class_method_name(arguments)`

Zero-argument `super()` uses the class where the method was defined and the first argument (`self` or `cls`) to determine where to continue lookup.

**Important:** `super()` does not always call the class written immediately after the current class in the source code. With multiple inheritance, the next class depends on the actual instance's MRO.

### 3.5 The first rule

Use `super()` when you intend to cooperate with the class hierarchy. Avoid hard-coding a particular base implementation unless you intentionally want to bypass cooperative dispatch and understand the consequences.

---

## 4. Intermediate level: diamond inheritance

### 4.1 The diamond shape

Consider this hierarchy:

```text
        A
       / \
      B   C
       \ /
        D
```

Both `B` and `C` inherit from `A`, and `D` inherits from both `B` and `C`.

```python
class A:
    def identify(self):
        return ["A"]


class B(A):
    def identify(self):
        return ["B"] + super().identify()


class C(A):
    def identify(self):
        return ["C"] + super().identify()


class D(B, C):
    def identify(self):
        return ["D"] + super().identify()


item = D()
print(item.identify())
print([cls.__name__ for cls in D.__mro__])
```

Expected output:

```text
['D', 'B', 'C', 'A']
['D', 'B', 'C', 'A', 'object']
```

Notice that `B`'s `super()` call continues to `C`, not directly to `A`, when invoked on a `D` instance. `C` then delegates to `A`. The shared ancestor runs once.

### 4.2 Why direct parent calls are dangerous

This version is not cooperative:

```python
class A:
    def identify(self):
        return ["A"]


class B(A):
    def identify(self):
        return ["B"] + A.identify(self)


class C(A):
    def identify(self):
        return ["C"] + A.identify(self)


class D(B, C):
    def identify(self):
        return ["D"] + B.identify(self) + C.identify(self)


print(D().identify())
```

It calls branches directly, and both branches call `A.identify`. The result contains `A` twice. Direct calls such as `A.method(self)` can be appropriate in narrow, intentional cases, but they defeat the single cooperative chain.

**Rule of thumb:** In a cooperative hierarchy, each implementation calls `super().method(...)` once when it needs to continue the chain.

---

## 5. C3 linearization: how Python orders the hierarchy

Python uses the **C3 linearization** algorithm to calculate a class's MRO. You do not need to implement the algorithm in everyday code, but you should understand its constraints.

### 5.1 Three core properties

1. **Children before parents:** a class appears before its ancestors.
2. **Local precedence order:** the order of bases in a class declaration is respected. In `class D(B, C)`, `B` is ordered before `C` in `D`'s MRO.
3. **Monotonicity:** subclassing should not reverse an ordering already established by a base class's MRO.

These rules produce a deterministic, consistent order for method lookup.

### 5.2 A valid hierarchy

```python
class A:
    pass


class B(A):
    pass


class C(A):
    pass


class D(B, C):
    pass


print([cls.__name__ for cls in D.__mro__])
# ['D', 'B', 'C', 'A', 'object']
```

The order starts with `D`, keeps `B` before `C` as declared, and places their shared ancestor `A` after both branches.

### 5.3 An inconsistent hierarchy

```python
class X:
    pass


class Y:
    pass


class A(X, Y):
    pass


class B(Y, X):
    pass


# This definition raises TypeError:
# class Impossible(A, B):
#     pass
```

`A` requires `X` before `Y`, while `B` requires `Y` before `X`. A subclass of both cannot preserve both orders, so Python rejects the hierarchy.

The error is a design signal: the base ordering contains contradictory constraints. Do not try to silence it by adding arbitrary bases. Reconsider the hierarchy, separate behaviours into independent mixins, or use composition.

### 5.4 A practical way to reason about MRO

When the hierarchy is non-trivial:

1. Draw the inheritance graph.
2. Write down each class's base order.
3. Inspect each base's own MRO.
4. Check whether all declared local orders can be preserved.
5. Ask Python for the actual MRO with `Class.__mro__`.
6. Test the method call order, not just the class list.

The interpreter is the authority for the actual MRO; your hand reasoning is a way to understand it.

---

## 6. Cooperative inheritance: the contract

A hierarchy is cooperative only when participating classes follow compatible conventions.

### 6.1 Core rules

- Each class performs only its own responsibility.
- A class that should continue dispatch calls `super().method(...)` once.
- Method names and argument contracts must be compatible.
- Constructors should forward unconsumed keyword arguments.
- The chain must have a clear endpoint that handles the remaining arguments.
- Do not mix cooperative calls and direct base calls casually.
- Test the actual order, including whether each implementation runs exactly once.

A class that forgets `super()` cuts off the remainder of the chain. A class that calls it twice may run later implementations twice. Either mistake violates the contract.

### 6.2 Cooperative method chain

```python
class Stage:
    def run(self, events):
        events.append("Stage")


class ValidateMixin:
    def run(self, events):
        events.append("Validate")
        return super().run(events)


class MetricsMixin:
    def run(self, events):
        events.append("Metrics")
        return super().run(events)


class Pipeline(ValidateMixin, MetricsMixin, Stage):
    def run(self, events):
        events.append("Pipeline")
        return super().run(events)


events = []
Pipeline().run(events)
print(events)
print([cls.__name__ for cls in Pipeline.__mro__])
```

Expected output:

```text
['Pipeline', 'Validate', 'Metrics', 'Stage']
['Pipeline', 'ValidateMixin', 'MetricsMixin', 'Stage', 'object']
```

This resembles a data-processing pipeline in which the outer component, validation, metrics, and core stage each add one action. The order is intentional and inspectable.

### 6.3 What happens if a class skips `super()`?

```python
class Stage:
    def run(self, events):
        events.append("Stage")


class ValidateMixin:
    def run(self, events):
        events.append("Validate")
        # Bug: no super().run(events)


class MetricsMixin:
    def run(self, events):
        events.append("Metrics")
        return super().run(events)


class Pipeline(ValidateMixin, MetricsMixin, Stage):
    def run(self, events):
        events.append("Pipeline")
        return super().run(events)


events = []
Pipeline().run(events)
print(events)
# ['Pipeline', 'Validate']
```

`MetricsMixin` and `Stage` never run because `ValidateMixin` stopped the chain. The code may not raise an exception; it can silently omit important behaviour.

In a production pipeline, that could mean metrics or validation are not executed. This is why tests should assert the full sequence or verify observable side effects.

---

## 7. Cooperative constructors and keyword forwarding

Constructors are where cooperative inheritance most often becomes tricky because different classes need different configuration.

### 7.1 Why `**kwargs` helps

A class should consume the options it owns and forward the rest:

```python
class Root:
    def __init__(self, **kwargs):
        if kwargs:
            unexpected = ", ".join(sorted(kwargs))
            raise TypeError(f"Unexpected arguments: {unexpected}")
        super().__init__()


class SourceMixin:
    def __init__(self, *, source_name, **kwargs):
        self.source_name = source_name
        super().__init__(**kwargs)


class RetryMixin:
    def __init__(self, *, max_retries=3, **kwargs):
        if max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        self.max_retries = max_retries
        super().__init__(**kwargs)


class IngestionJob(SourceMixin, RetryMixin, Root):
    def __init__(self, *, job_name, **kwargs):
        self.job_name = job_name
        super().__init__(**kwargs)


job = IngestionJob(
    job_name="daily-orders",
    source_name="orders-api",
    max_retries=5,
)
print(job.job_name, job.source_name, job.max_retries)
```

Expected output:

```text
daily-orders orders-api 5
```

Each constructor has a clear responsibility:

- `IngestionJob` consumes `job_name`.
- `SourceMixin` consumes `source_name`.
- `RetryMixin` consumes `max_retries`.
- `Root` verifies that no unrecognized options remain and terminates the chain.

`Root` then calls `object.__init__()` with no arguments. That is why all configuration arguments must be consumed before the chain reaches `object`.

### 7.2 Why keyword-only arguments are useful

The `*` in `def __init__(self, *, source_name, **kwargs)` makes `source_name` keyword-only. This reduces ambiguity when several mixins contribute independent options.

Prefer explicit keyword-only options for configuration. `**kwargs` should be a deliberate forwarding mechanism, not a way to hide unclear APIs.

### 7.3 Common constructor failures

**Failure: a class doesn't forward the remaining options**

```python
class BrokenMixin:
    def __init__(self, *, enabled=True, **kwargs):
        self.enabled = enabled
        # Bug: remaining kwargs are dropped.
```

A later class's constructor will never run.

**Failure: a constructor passes unknown options to `object`**

If the final class forwards `{"mystery": 1}` to `object.__init__`, initialization raises `TypeError`. That is often useful: it exposes a misspelled or unconsumed argument rather than silently ignoring it.

**Failure: incompatible signatures**

If one mixin expects a positional argument while another forwards it as a keyword, the chain can fail. Agree on keyword names and forwarding conventions across the hierarchy.

### 7.4 Constructor order in a diamond

```python
class A:
    def __init__(self, **kwargs):
        print("A")
        super().__init__(**kwargs)


class B(A):
    def __init__(self, **kwargs):
        print("B")
        super().__init__(**kwargs)


class C(A):
    def __init__(self, **kwargs):
        print("C")
        super().__init__(**kwargs)


class D(B, C):
    def __init__(self, **kwargs):
        print("D")
        super().__init__(**kwargs)


D()
```

Expected output:

```text
D
B
C
A
```

`A.__init__` executes once. It delegates to `object.__init__`, which terminates the chain because there are no remaining keyword arguments.

**Important:** The `**kwargs` pattern is appropriate when all participants are designed for cooperation. For a simple hierarchy with one base, a clear explicit signature may be simpler.

---

## 8. `super()` in class methods and `__init_subclass__`

### 8.1 Class methods

`super()` can be used inside a `classmethod`; its implicit first argument is the class (`cls`):

```python
class Base:
    @classmethod
    def description(cls):
        return "base"


class Child(Base):
    @classmethod
    def description(cls):
        return "child -> " + super().description()


print(Child.description())
# child -> base
```

With multiple inheritance, the next class is determined by the MRO of the class on which the method was called.

### 8.2 `__init_subclass__`

`__init_subclass__` is a class hook called when a subclass is created. A base class can use it to validate or register subclasses without requiring every subclass to call a registration method manually.

```python
class NamedJob:
    def __init_subclass__(cls, *, job_kind, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.job_kind = job_kind


class DailyJob(NamedJob, job_kind="daily"):
    pass


print(DailyJob.job_kind)
# daily
```

The `super().__init_subclass__(**kwargs)` call allows other base classes in a cooperative hierarchy to participate in subclass initialization. This is especially important when more than one base defines the hook.

Avoid treating `__init_subclass__` as magic registration without tests. Be explicit about required class keywords and whether duplicate names or registrations are permitted.

---

## 9. Advanced: what zero-argument `super()` does

### 9.1 The short explanation

In a method defined in a class, Python provides the information needed for zero-argument `super()`:

- the class where the method was defined, captured through a compiler-created `__class__` closure cell;
- the first argument of the current method, normally `self` or `cls`.

Conceptually, `super()` uses those values to create a proxy that continues lookup after the defining class in the MRO for the relevant object or class.

This is not equivalent to `Base.method(self)`. A direct call names a specific implementation; `super()` follows the MRO.

### 9.2 Why it can fail outside a class method

This function is not defined in a class body:

```python
def helper():
    # Calling super() here without arguments raises RuntimeError,
    # because there is no method's __class__ context or first argument.
    return super()
```

A standalone helper function has no implicit `self` and no class context captured for zero-argument `super()`. If a design needs to operate on a class hierarchy, pass the required object/class explicitly and choose the appropriate form carefully.

### 9.3 Two-argument `super`

The general form is:

`super(CurrentClass, object_or_subclass)`

Examples:

```python
class Base:
    @classmethod
    def label(cls):
        return "base"


class Child(Base):
    @classmethod
    def label(cls):
        return "child -> " + super(Child, cls).label()


print(Child.label())
# child -> base
```

Inside a class method, `super()` is normally preferred because it is concise and supports cooperative inheritance. The explicit form can be useful for introspection, unusual delegation, or understanding the mechanics. It is easier to get wrong, so do not use it merely for style.

The second argument must be an instance of the specified class or a subclass of it, depending on the form used. If it is incompatible, Python raises `TypeError`.

### 9.4 `super()` is a proxy, not a parent instance

`super()` does not instantiate a base class. It creates a lookup proxy. Attribute access on the proxy searches after the specified class in the MRO associated with the given object or class.

This explains why a method can call `super().run()` and reach a sibling mixin in a diamond hierarchy.

---

## 10. Attribute lookup versus special-method lookup

For ordinary attributes, the MRO participates in locating class attributes and methods. Descriptors and instance attributes add further rules to the attribute lookup process.

Special methods used by language syntax and built-in operations are often looked up on the type rather than by ordinary instance attribute lookup. For example, setting an arbitrary `obj.__len__` attribute is not a reliable way to make `len(obj)` work. Define the special method on the class.

```python
class SizedBatch:
    def __init__(self, rows):
        self.rows = rows

    def __len__(self):
        return len(self.rows)


batch = SizedBatch([{"id": 1}, {"id": 2}])
print(len(batch))
# 2
```

For this lesson, the key point is that inheritance and MRO influence which class-level special-method implementation Python uses. Do not assume that assigning a same-named attribute to one instance changes all special-method behavior.

---

## 11. `functools.singledispatchmethod` and `super()`: awareness

`functools.singledispatchmethod` dispatches a method based on the type of its first non-`self`/`cls` argument. It is useful for type-based behavior, but it solves a different problem from MRO-based method lookup.

```python
from functools import singledispatchmethod


class Formatter:
    @singledispatchmethod
    def format_value(self, value):
        return str(value)

    @format_value.register
    def _(self, value: int):
        return f"integer:{value}"


class AuditedFormatter(Formatter):
    def format_value(self, value):
        result = super().format_value(value)
        return f"[audit] {result}"


formatter = AuditedFormatter()
print(formatter.format_value(7))
print(formatter.format_value("ready"))
```

Expected output:

```text
[audit] integer:7
[audit] ready
```

The subclass uses `super()` to reach the inherited dispatcher. The dispatcher then chooses an implementation based on the argument type. Keep these two decisions conceptually separate: MRO chooses the inherited method implementation; singledispatch chooses a registered implementation inside the dispatcher.

---

## 12. Common mistakes and how to diagnose them

| Mistake | Symptom | Better approach |
|---|---|---|
| Treating `super()` as “my direct parent” | A sibling mixin unexpectedly runs | Inspect the concrete class's MRO. |
| Calling `Parent.method(self)` in a cooperative diamond | Shared base behaviour may run twice | Use `super()` consistently across participating classes. |
| Forgetting `super()` | Later methods or constructors are skipped | Add tests that assert the full call sequence. |
| Calling `super()` more than once in one chain path | Later behavior may run more than once | Delegate once, normally at the appropriate point. |
| Incompatible constructor signatures | `TypeError` during object creation | Agree on keyword-only options and forwarding conventions. |
| Forwarding unconsumed arguments to `object` | Unexpected-keyword `TypeError` | Consume known arguments and validate leftovers at the root. |
| Contradictory base order | Class creation raises MRO `TypeError` | Redesign the hierarchy or use composition. |
| Adding multiple complex mixins without tests | Order-dependent behavior and fragile code | Keep mixins focused and test every supported combination. |
| Using multiple inheritance when one object should own another | Unclear responsibilities and tight coupling | Prefer composition when behaviors are not designed to cooperate. |

### Debugging checklist

When a method appears to run in the wrong order:

1. Print `[cls.__name__ for cls in ConcreteClass.__mro__]`.
2. Identify which class defines the method.
3. Follow each `super()` call to the next class in the concrete MRO.
4. Check for a method that does not delegate.
5. Check whether a direct base call bypasses the chain.
6. Verify constructor argument consumption and forwarding.
7. Add a regression test for the observed order.

---

## 13. Data-engineering case study: extensible ingestion job

This example combines a job class with validation and metrics mixins. It demonstrates a deliberate, testable cooperative chain without external dependencies.

```python
class JobRoot:
    def execute(self, records):
        raise NotImplementedError("Concrete job must implement execute")


class ValidationMixin:
    def execute(self, records):
        records = list(records)
        if any(record is None for record in records):
            raise ValueError("Records must not contain None")
        return super().execute(records)


class MetricsMixin:
    def execute(self, records):
        records = list(records)
        result = super().execute(records)
        return {
            "record_count": len(records),
            "result": result,
        }


class CountJob(JobRoot):
    def execute(self, records):
        return {"count": len(records)}


class IngestionJob(ValidationMixin, MetricsMixin, CountJob):
    pass


job = IngestionJob()
print(job.execute([{"id": 1}, {"id": 2}]))
```

Expected output:

```text
{'record_count': 2, 'result': {'count': 2}}
```

Read the MRO before changing the order of the mixins. `ValidationMixin` delegates to `MetricsMixin`; `MetricsMixin` delegates to `CountJob`; the concrete job returns the count. If a mixin does not delegate, the later behavior will not execute.

### Design review

This is a teaching example, not a universal recommendation to implement ETL pipelines through multiple inheritance. In a larger production system, explicit composition can make dependencies and execution order clearer:

```python
class CountJob:
    def execute(self, records):
        records = list(records)
        if any(record is None for record in records):
            raise ValueError("Records must not contain None")
        result = {"count": len(records)}
        return {
            "record_count": len(records),
            "result": result,
        }
```

The composed version is simpler if there are only a few fixed behaviors. Cooperative mixins are most appropriate when a framework or extension model intentionally supports combining independent behaviors through a shared MRO contract.

---

## 14. Composition over inheritance

Inheritance is useful when a subtype relationship and shared dispatch are meaningful. Composition is often better when a class simply needs to use another object's service.

Choose **composition** when:

- behavior order should be explicit rather than derived from an MRO;
- components need independent lifecycles or configuration;
- you want to swap validators, metrics collectors, storage clients, or retry policies at runtime;
- the hierarchy has conflicting constraints or too many mixins;
- a base class has methods unrelated to the concrete class's responsibility.

Example:

```python
class Validator:
    def validate(self, records):
        if any(record is None for record in records):
            raise ValueError("Records must not contain None")
        return records


class Metrics:
    def summarize(self, records, result):
        return {"record_count": len(records), "result": result}


class CountJob:
    def __init__(self, validator, metrics):
        self.validator = validator
        self.metrics = metrics

    def execute(self, records):
        records = list(self.validator.validate(records))
        result = {"count": len(records)}
        return self.metrics.summarize(records, result)
```

Composition makes dependencies visible in `__init__` and makes behavior order explicit. It can be easier to test by injecting a fake validator or metrics object.

---

## 15. Testing cooperative behavior

Do not validate a cooperative hierarchy only by reading the code. Assert the behavior you rely on.

### 15.1 Test the MRO and call sequence

```python
def test_pipeline_order():
    class Root:
        def run(self, events):
            events.append("Root")

    class First:
        def run(self, events):
            events.append("First")
            return super().run(events)

    class Second:
        def run(self, events):
            events.append("Second")
            return super().run(events)

    class Pipeline(First, Second, Root):
        def run(self, events):
            events.append("Pipeline")
            return super().run(events)

    events = []
    Pipeline().run(events)

    assert events == ["Pipeline", "First", "Second", "Root"]
    assert [cls.__name__ for cls in Pipeline.__mro__] == [
        "Pipeline", "First", "Second", "Root", "object"
    ]
```

### 15.2 Test the constructor contract

```python
def test_cooperative_init_consumes_options():
    class Root:
        def __init__(self, **kwargs):
            if kwargs:
                raise TypeError(f"Unexpected options: {sorted(kwargs)}")
            super().__init__()

    class NameMixin:
        def __init__(self, *, name, **kwargs):
            self.name = name
            super().__init__(**kwargs)

    class RetryMixin:
        def __init__(self, *, retries=2, **kwargs):
            self.retries = retries
            super().__init__(**kwargs)

    class Job(NameMixin, RetryMixin, Root):
        pass

    job = Job(name="orders", retries=4)
    assert job.name == "orders"
    assert job.retries == 4
```

Save these tests in a test module and run `pytest`. Tests should cover supported class combinations, invalid options, and the observable order of execution.

---

## 16. Exercises

Try to solve these before reading the solutions.

### Exercise 1 — Read a simple MRO

What is the MRO of `Child`?

```python
class Base:
    pass

class Child(Base):
    pass
```

Write the class names in order.

### Exercise 2 — Predict `super()`

What does this print, and why?

```python
class Base:
    def name(self):
        return "Base"

class Child(Base):
    def name(self):
        return "Child-" + super().name()

print(Child().name())
```

### Exercise 3 — Diamond order

For `D(B, C)`, where both `B` and `C` inherit from `A`, what order does this cooperative method follow?

```python
class A:
    def run(self, events):
        events.append("A")

class B(A):
    def run(self, events):
        events.append("B")
        super().run(events)

class C(A):
    def run(self, events):
        events.append("C")
        super().run(events)

class D(B, C):
    def run(self, events):
        events.append("D")
        super().run(events)
```

### Exercise 4 — Find the bug

Why does this hierarchy fail to execute every method?

```python
class Root:
    def run(self):
        print("root")

class First:
    def run(self):
        print("first")
        # no super()

class Pipeline(First, Root):
    def run(self):
        print("pipeline")
        super().run()
```

Change the minimum amount of code to make the chain cooperative.

### Exercise 5 — Constructor forwarding

Design `NamedMixin` and `RetryMixin` so the following assertions pass (this is an incomplete target snippet, not a standalone program):

```text
job = Job(name="daily", retries=4)
assert job.name == "daily"
assert job.retries == 4
```

Use keyword-only arguments, `**kwargs`, and a terminal root class that rejects leftover options.

### Exercise 6 — Inconsistent MRO

Why can Python not create a subclass of `A(X, Y)` and `B(Y, X)`? Explain the conflicting ordering constraints.

### Exercise 7 — Choose inheritance or composition

You need to combine validation, metrics, and a storage client. The storage client is configured independently and may be replaced at runtime. Should the storage client be a base class or a composed dependency? Explain your choice.

### Exercise 8 — Production-style test

Write a test that asserts the exact call order of three cooperative classes. Include the terminal implementation and assert that it runs exactly once.

---

## 17. Exercise solutions

### Solution 1

```text
Child -> Base -> object
```

The tuple is `(Child, Base, object)`.

### Solution 2

```text
Child-Base
```

`Child.name` runs first, then `super().name()` continues after `Child` in the MRO and finds `Base.name`.

### Solution 3

```text
D, B, C, A
```

For `D(B, C)`, the MRO is `D -> B -> C -> A -> object`. Cooperative `super()` follows that order, so `A.run` executes once.

### Solution 4

`First.run` does not call `super().run()`, so it stops the chain before `Root.run`. The minimal fix is:

```python
class First:
    def run(self):
        print("first")
        super().run()
```

This assumes `First` is used in a cooperative hierarchy whose next implementation defines `run`.

### Solution 5

One valid design:

```python
class Root:
    def __init__(self, **kwargs):
        if kwargs:
            raise TypeError(f"Unexpected options: {sorted(kwargs)}")
        super().__init__()

class NamedMixin:
    def __init__(self, *, name, **kwargs):
        self.name = name
        super().__init__(**kwargs)

class RetryMixin:
    def __init__(self, *, retries=2, **kwargs):
        if retries < 0:
            raise ValueError("retries must be non-negative")
        self.retries = retries
        super().__init__(**kwargs)

class Job(NamedMixin, RetryMixin, Root):
    pass

job = Job(name="daily", retries=4)
assert job.name == "daily"
assert job.retries == 4
```

### Solution 6

`A` establishes `X` before `Y`; `B` establishes `Y` before `X`. A subclass of both would need to preserve both orders, which is impossible. C3 linearization rejects the inconsistent hierarchy.

### Solution 7

Prefer composition for the storage client. It is independently configured and replaceable at runtime, which are strong signs that it should be an injected dependency rather than a base class. Validation or metrics might be composed too; use mixins only when their cooperative behavior and ordering are part of a deliberate extension design.

### Solution 8

For example:

```python
def test_cooperative_order():
    class Root:
        def run(self, events):
            events.append("root")

    class A:
        def run(self, events):
            events.append("a")
            return super().run(events)

    class B:
        def run(self, events):
            events.append("b")
            return super().run(events)

    class Job(A, B, Root):
        def run(self, events):
            events.append("job")
            return super().run(events)

    events = []
    Job().run(events)
    assert events == ["job", "a", "b", "root"]
    assert events.count("root") == 1
```

---

## 18. Quick reference

| Need | Use |
|---|---|
| Inspect lookup order | `Class.__mro__`, `Class.mro()`, `inspect.getmro(Class)` |
| Extend the next implementation | `super().method(...)` |
| Continue a cooperative constructor | `super().__init__(**kwargs)` |
| Support independent mixin options | Keyword-only parameters plus careful `**kwargs` forwarding |
| Diagnose skipped behavior | Find a method that omits `super()` |
| Diagnose repeated base behavior | Find direct calls such as `Base.method(self)` |
| Diagnose a class-creation failure | Inspect conflicting base order and C3 constraints |
| Avoid fragile inheritance | Use composition for independent services and runtime-swappable dependencies |

### The central rule

**`super()` means “continue after this class in the relevant MRO,” not “call my parent.”** Cooperative inheritance works only when the participating methods share a compatible contract, delegate consistently, and terminate cleanly.

---

## 19. Self-check and readiness checklist

You are ready to move on when you can do all of the following without copying a solution:

- [ ] Explain the difference between overriding a method and extending it with `super()`.
- [ ] Inspect an MRO and predict which method implementation runs next.
- [ ] Draw a diamond hierarchy and explain why a shared base runs once in a cooperative chain.
- [ ] Explain C3's local precedence order, child-before-parent rule, and monotonicity.
- [ ] Recognize an inconsistent MRO and explain the contradiction.
- [ ] Write cooperative mixins whose methods call `super()` once.
- [ ] Design constructors that consume keyword-only arguments and forward the rest.
- [ ] Use a terminal root constructor to reject unconsumed options.
- [ ] Explain why a missing `super()` call silently skips later behavior.
- [ ] Explain why direct parent calls can execute a shared ancestor more than once.
- [ ] Explain zero-argument `super()` and identify when its context is unavailable.
- [ ] Use `super()` in a class method and understand the purpose of `__init_subclass__`.
- [ ] Decide when composition is clearer than multiple inheritance.
- [ ] Write a test that asserts a cooperative call sequence.

## 20. Suggested study workflow

1. Type and run every example in a Python 3.12+ environment.
2. Predict output before running each example.
3. Change the base order in a diamond and inspect how the MRO changes.
4. Remove one `super()` call intentionally and observe which behavior disappears.
5. Replace a cooperative call with a direct parent call and look for duplicate work.
6. Run the testing examples under `pytest`.
7. Complete the exercises without looking at the solutions, then compare your reasoning.
8. Before using multiple inheritance in a real pipeline, document the intended MRO and add tests for supported combinations.

**Connection to the next lesson:** Lesson 09, *Mixins and Multiple-Inheritance Pitfalls*, builds directly on this lesson by focusing on how to design small mixins and avoid fragile inheritance hierarchies.
